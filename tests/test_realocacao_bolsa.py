"""Testes da realocação (protocolo 58): `scripts/rdd_bolsa/32_realocacao_bolsa.py`.

Quatro partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados "sintético"
   (`natureza_dos_dados = SINTETICO_TESTE`) e nunca gravados em `output/` nem em `data/`. Um mercado simulado em
   que candidatos escolhem, por logit, entre as células do seu curso na sua região de saúde, com peso conhecido
   da bolsa: a célula com concorrentes de bolsa maior perde candidatos (deslocamento conhecido). O estimador do
   script tem de recuperar o sinal negativo; sem peso da bolsa, não pode achar efeito.
2. `TestSaidas`: esquema e rótulos de `output/rdd_bolsa/R_*`, grade completa de especificações, Holm só nas duas
   primárias da principal, MDE e escalas recalculados, leitura pré-registrada refeita, hashes e figuras, sem
   identificador de candidato.
3. `TestRecalculoIndependente`: refaz a exposição de algumas células com laço próprio e a regressão principal
   com o statsmodels (efeitos fixos por dummies do pandas, cluster por CIR) e compara com o CSV gravado.
4. `TestDoc57g`: doc 57g igual ao gerado das saídas, "Como ler" no doc, linguagem e limites.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "32_realocacao_bolsa.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("realocacao_bolsa_32", SCRIPT)
R = importlib.util.module_from_spec(_spec)
sys.modules["realocacao_bolsa_32"] = R
_spec.loader.exec_module(R)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "R_estimativas.csv"
VAR = OUT / "R_variacao_exposicao.csv"
RESUMO = OUT / "R_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "57g_resultados_realocacao.md"
PROTOCOLO = ROOT / "docs" / "06_execucao" / "58_protocolo_realocacao_bolsa.md"

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados sintéticos; nunca gravados


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# 1. Sintético
# ---------------------------------------------------------------------------

def mercado_sintetico(peso_bolsa: float, semente: int = 58, n_cir: int = 260) -> pd.DataFrame:
    """SINTÉTICO: células em regiões de saúde; candidatos escolhem por logit dentro de (CIR, curso).

    Cada município tem um IVS uniforme em [0,15; 0,55] e a bolsa sai da regra de dois cortes (R$ 10/15/20 mil).
    Utilidade da célula = peso_bolsa × bolsa (R$ mil) + 0,8 × IVS + Gumbel. Com peso_bolsa > 0, uma célula cujas
    concorrentes têm bolsa maior recebe menos candidatos: o deslocamento é conhecido e negativo.
    """
    rng = np.random.default_rng(semente)
    linhas = []
    for g in range(n_cir):
        n_mun = int(rng.integers(2, 6))
        ivs_mun = rng.uniform(0.15, 0.55, n_mun)
        for curso in (1, 2):
            n_cel = int(rng.integers(2, 7))
            mun = rng.integers(0, n_mun, n_cel)
            for j in range(n_cel):
                s = float(np.round(ivs_mun[mun[j]] * 1000))
                faixa = "FAIXA 1" if s > 400 else "FAIXA 2" if s > 300 else "FAIXA 3"
                linhas.append({"ciclo": 1, "cod_curso": curso, "co_cnes_7d": f"S{g:04d}{curso}{j:02d}",
                               "co_ibge": f"9{g:03d}{mun[j]:02d}", "cir": f"C{g:04d}", "uf": "99",
                               "lon": -50.0 + g * 0.01, "lat": -10.0, "s_mil": s, "faixa_anunciada": faixa,
                               "bolsa": {"FAIXA 1": 20.0, "FAIXA 2": 15.0, "FAIXA 3": 10.0}[faixa]})
    d = pd.DataFrame(linhas)
    d["cand1"] = 0.0
    for _, idx in d.groupby(["cir", "cod_curso"]).groups.items():
        sub = d.loc[idx]
        n_cand = rng.poisson(1.5 * len(sub))
        u = peso_bolsa * sub["bolsa"].to_numpy() + 0.8 * sub["s_mil"].to_numpy() / 1000.0
        escolha = np.argmax(u[None, :] + rng.gumbel(size=(n_cand, len(sub))), axis=1)
        d.loc[idx, "cand1"] = np.bincount(escolha, minlength=len(sub)).astype(float)
    d["preenchida"] = (d["cand1"] >= 1).astype(float)
    d["fe_curso_ciclo"] = "c1_curso" + d["cod_curso"].astype(str).str.zfill(2)
    d["cov_ok"] = True
    d["natureza_dos_dados"] = NATUREZA_SINTETICA
    return d.sort_values(["ciclo", "cod_curso", "co_cnes_7d"]).reset_index(drop=True)


def estimar_sintetico(d: pd.DataFrame, oid: str) -> dict:
    esp = dict(next(e for e in R.ESPECS if e["id"] == "PRINCIPAL"), covs=False)
    ex = R.exposicoes(d, "cir", "mesmo_curso")
    a, _ = R.amostra_especificacao(d, ex, esp)
    col = {"R_P1": "preenchida", "R_P2": "cand1"}[oid]
    return R.ajustar(a, a[col].to_numpy(dtype=float), esp)


class TestSintetico(unittest.TestCase):
    """Mercado simulado (sintético, só em memória)."""

    def test_dados_rotulados_como_sinteticos(self) -> None:
        d = mercado_sintetico(0.25)
        self.assertTrue((d["natureza_dos_dados"] == NATUREZA_SINTETICA).all())

    def test_recupera_deslocamento_conhecido(self) -> None:
        d = mercado_sintetico(0.25)
        r = estimar_sintetico(d, "R_P2")
        self.assertLess(r["coef"], 0.0)
        self.assertLess(r["p"], 0.01)
        r1 = estimar_sintetico(d, "R_P1")
        self.assertLess(r1["coef"], 0.0)

    def test_sem_peso_da_bolsa_nao_acha_efeito(self) -> None:
        d = mercado_sintetico(0.0, semente=59)
        r = estimar_sintetico(d, "R_P2")
        self.assertLess(abs(r["coef"] / r["ep"]), 3.0)

    def test_exposicao_contra_laco_direto(self) -> None:
        d = mercado_sintetico(0.25, n_cir=20)
        ex = R.exposicoes(d, "cir", "mesmo_curso")
        for i in range(0, len(d), 7):
            m = (d["cir"] == d.at[i, "cir"]) & (d["cod_curso"] == d.at[i, "cod_curso"]) & (d.index != i)
            if m.sum() == 0:
                self.assertTrue(np.isnan(ex.at[i, "E"]))
                continue
            self.assertAlmostEqual(ex.at[i, "E"], d.loc[m, "bolsa"].mean() - d.at[i, "bolsa"], places=12)
            self.assertAlmostEqual(ex.at[i, "frac_maior"], (d.loc[m, "bolsa"] > d.at[i, "bolsa"]).mean(), places=12)
            self.assertEqual(ex.at[i, "n_conc"], m.sum())


# ---------------------------------------------------------------------------
# 2. Saídas gravadas
# ---------------------------------------------------------------------------

class TestSaidas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = R.ler_est()
        cls.var = R.ler_var()
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_esquema_e_rotulos(self) -> None:
        for c in ("especificacao", "outcome_id", "coef", "ep", "ic95_inf", "ic95_sup", "p", "p_holm", "mde_por_5mil",
                  "n_celulas", "n_clusters", "estatuto", "natureza_dos_dados"):
            self.assertIn(c, self.est.columns)
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "EXPLORATORIO_REALOCACAO").all())
        self.assertTrue((self.var["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "EXPLORATORIO_REALOCACAO")

    def test_grade_completa(self) -> None:
        esperado = {(e["id"], o["id"]) for e in R.ESPECS for o in R.OUTCOMES}
        self.assertEqual(set(zip(self.est["especificacao"], self.est["outcome_id"])), esperado)
        self.assertEqual(len(self.est), len(esperado))

    def test_nao_executado_sempre_com_motivo(self) -> None:
        falta = self.est[self.est["status"] != "EXECUTADO"]
        self.assertTrue((falta["nota"].str.len() > 0).all())
        exe = self.est[self.est["status"] == "EXECUTADO"]
        self.assertFalse(exe[["coef", "ep", "p", "n_celulas"]].isna().any().any())

    def test_holm_so_nas_primarias_da_principal(self) -> None:
        com = self.est[self.est["p_holm"].notna()]
        self.assertEqual(set(com["especificacao"]), {"PRINCIPAL"})
        self.assertEqual(set(com["outcome_id"]), {"R_P1", "R_P2"})
        p = com.sort_values("p")["p"].to_numpy()
        holm = np.minimum(1, np.maximum.accumulate(p * np.array([2, 1])))
        np.testing.assert_allclose(com.sort_values("p")["p_holm"].to_numpy(), holm, rtol=1e-8)

    def test_escalas_mde_e_ic(self) -> None:
        e = self.est[self.est["status"] == "EXECUTADO"]
        np.testing.assert_allclose(e["mde_por_unidade"], 2.8015852 * e["ep"], rtol=1e-6)
        np.testing.assert_allclose(e["ic95_sup"] - e["ic95_inf"], 2 * 1.959963985 * e["ep"], rtol=1e-6)
        rs = e[e["exposicao"] != "frac"]
        np.testing.assert_allclose(rs["coef_por_5mil"], 5 * rs["coef"], rtol=1e-8)
        np.testing.assert_allclose(rs["mde_por_5mil"], 5 * rs["mde_por_unidade"], rtol=1e-8)
        self.assertTrue(e.loc[e["exposicao"] == "frac", "mde_por_5mil"].isna().all())
        z = (e["coef"] / e["ep"]).abs()
        from scipy import stats
        np.testing.assert_allclose(e["p"], 2 * stats.norm.sf(z), rtol=1e-6)

    def test_amostras_consistentes(self) -> None:
        a = self.resumo["amostra"]
        self.assertEqual(sum(a["n_total"].values()), 5135)
        p = a["por_especificacao"]["PRINCIPAL"]
        fora = sum(sum(v.values()) for v in a["exclusoes_universo"].values()) + \
            sum(sum(v.values()) for v in p["fora"].values())
        self.assertEqual(p["n_celulas"] + fora, 5135)
        for e in R.ESPECS:
            n = self.est[(self.est["especificacao"] == e["id"]) & (self.est["status"] == "EXECUTADO")]["n_celulas"]
            self.assertTrue((n == a["por_especificacao"][e["id"]]["n_celulas"]).all(), e["id"])
        self.assertEqual(int(self.var.loc[self.var["especificacao"] == "PRINCIPAL", "n_celulas"].iloc[0]),
                         p["n_celulas"])

    def test_leitura_pre_registrada_refeita(self) -> None:
        for oid in R.PRIMARIAS:
            c = R.classificar(self.est, oid)
            self.assertEqual(c["classe"], self.resumo["leitura"][oid]["classe"])
            p = self.est[(self.est["especificacao"] == "PRINCIPAL") & (self.est["outcome_id"] == oid)].iloc[0]
            limiar = R.LIMIAR_MDE_5MIL[oid]
            if p["ic95_inf"] <= 0 <= p["ic95_sup"]:
                self.assertIn(c["classe"], {"POUCA_COMPETICAO", "INCONCLUSIVO"})
                self.assertEqual(c["classe"] == "POUCA_COMPETICAO", p["mde_por_5mil"] <= limiar)

    def test_hashes_e_figuras(self) -> None:
        for caminho, h in self.resumo["hashes_saidas"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)
        for f in self.resumo["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists())
            self.assertTrue(f["como_ler"])
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
            self.assertNotIn("ivs_ipea_2010_municipios", e["caminho"])

    def test_sem_identificador_de_candidato(self) -> None:
        proibidos = re.compile(r"id_candidato|cpf|nome_candidato|no_candidato", re.IGNORECASE)
        for p in (EST, VAR):
            self.assertFalse(any(proibidos.search(c) for c in pd.read_csv(p, nrows=0).columns), p.name)
        self.assertIsNone(proibidos.search(RESUMO.read_text(encoding="utf-8")))

    def test_integridade_do_script(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)
        self.assertNotIn("escolhas_candidatos", fonte)
        self.assertNotRegex(fonte, r"to_csv\([^)]*data/|to_parquet\([^)]*data/")
        self.assertIn('NATUREZA = "EMPIRICO"', fonte)


# ---------------------------------------------------------------------------
# 3. Recálculo independente
# ---------------------------------------------------------------------------

class TestRecalculoIndependente(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dados = R.carregar()
        cls.univ = cls.dados["univ"]
        cls.ex = R.exposicoes(cls.univ, "cir", "mesmo_curso")
        cls.est = R.ler_est()

    def test_exposicao_por_laco_proprio(self) -> None:
        u = self.univ
        for i in range(0, len(u), 97):
            m = (u["cir"] == u.at[i, "cir"]) & (u["cod_curso"] == u.at[i, "cod_curso"]) & \
                (u["ciclo"] == u.at[i, "ciclo"]) & (u.index != i)
            if m.sum() == 0:
                self.assertTrue(np.isnan(self.ex.at[i, "E"]))
                continue
            self.assertAlmostEqual(self.ex.at[i, "E"], u.loc[m, "bolsa"].mean() - u.at[i, "bolsa"], places=12)
            ivs = u.loc[m, "s_mil"].to_numpy() / 1000.0
            self.assertAlmostEqual(self.ex.at[i, "conc_ivs_inclinacao"], np.mean((ivs - 0.3) * 10), places=10)
            self.assertAlmostEqual(self.ex.at[i, "conc_ivs_mudanca_inclinacao_0400"],
                                   np.mean(np.maximum(ivs - 0.4, 0) * 10), places=10)

    def test_principal_com_statsmodels(self) -> None:
        import statsmodels.api as sm
        d = pd.concat([self.univ, self.ex], axis=1)
        d = d[(d["n_conc"].fillna(0) > 0) & d["cov_ok"]].copy()
        s = d["s_mil"] / 1000.0
        X = pd.DataFrame({
            "E": d["bolsa_media_conc"] - d["bolsa"],
            "f2": (d["faixa_anunciada"] == "FAIXA 2").astype(float),
            "f1": (d["faixa_anunciada"] == "FAIXA 1").astype(float),
            "u": (s - 0.3) * 10, "a": np.maximum(s - 0.3, 0) * 10, "b": np.maximum(s - 0.4, 0) * 10,
            "cu": d["conc_ivs_inclinacao"], "ca": d["conc_ivs_mudanca_inclinacao_0300"],
            "cb": d["conc_ivs_mudanca_inclinacao_0400"], "ln": np.log1p(d["n_conc"]),
            "lp": d["log_pop22"], "ea": d["estoque_alvo_pre"], "eg": d["estoque_gen_pre"]}, index=d.index)
        fe = pd.get_dummies(d["fe_curso_ciclo"], drop_first=True, dtype=float)
        X = sm.add_constant(pd.concat([X, fe], axis=1))
        grupos = pd.factorize(d["cir"].astype(str))[0]
        for oid, col in (("R_P1", "preenchida"), ("R_P2", "cand1")):
            fit = sm.OLS(d[col].astype(float), X).fit(cov_type="cluster", cov_kwds={"groups": grupos})
            g = self.est[(self.est["especificacao"] == "PRINCIPAL") & (self.est["outcome_id"] == oid)].iloc[0]
            self.assertEqual(int(fit.nobs), int(g["n_celulas"]))
            self.assertAlmostEqual(fit.params["E"], g["coef"], places=8)
            self.assertAlmostEqual(fit.bse["E"] / g["ep"], 1.0, places=6)


# ---------------------------------------------------------------------------
# 4. Doc 57g
# ---------------------------------------------------------------------------

class TestDoc57g(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_doc_igual_ao_gerado(self) -> None:
        self.assertEqual(self.doc, R.gerar_doc(R.ler_est(), R.ler_var(), self.resumo))

    def test_como_ler_no_doc(self) -> None:
        for f in self.resumo["figuras"]:
            self.assertIn(f["como_ler"], self.doc)

    def test_linguagem_e_limites(self) -> None:
        for t in ("EXPLORATORIO_REALOCACAO", "pacote do corte", "condicional às vagas abertas",
                  "não a participação no PMM-E", "Vagas abertas endógenas", "Conjunto de escolha"):
            self.assertIn(t, self.doc)
        leitura = self.doc.split("<!-- R:leitura:inicio -->")[1].split("<!-- R:leitura:fim -->")[0]
        for oid in R.PRIMARIAS:
            self.assertIn(self.resumo["leitura"][oid]["leitura"], leitura)
        self.assertNotRegex(leitura.lower(), r"\bcausou\b|\bprova\b|\bcomprova\b")

    def test_numeros_da_leitura_saem_do_csv(self) -> None:
        est = R.ler_est()
        for oid in R.PRIMARIAS:
            r = est[(est["especificacao"] == "PRINCIPAL") & (est["outcome_id"] == oid)].iloc[0].to_dict()
            self.assertIn(R._efeito5(r), self.doc)
            self.assertIn(f"p de Holm = {R._p(r['p_holm'])}", self.doc)

    def test_protocolo_existe_e_declara_estatuto(self) -> None:
        texto = PROTOCOLO.read_text(encoding="utf-8")
        self.assertIn("EXPLORATORIO_REALOCACAO", texto)
        for visto in ("E9", "P1", "A3"):
            self.assertIn(visto, texto)


if __name__ == "__main__":
    unittest.main()
