"""Testes do adendo 52d: `scripts/rdd_bolsa/48_sensibilidades_ciclo2_quadro_1302.py`.

Partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória, rotulados `SINTETICO_TESTE` e nunca gravados. Conferem a
   comparação do portão (passa com números iguais, falha com 2e−8, relativa acima de 1, NaN só com NaN), a regra do
   conjunto "só células com vaga imediata", a marca da 1ª opção refeita sem imputar, os critérios de sinal e de
   significância e a regra do VD-1 (§3 do adendo).
2. `TestPortaoReal`: a versão antiga gravada em `VD_estimativas.csv` bate, linha a linha, com `E9_estimativas.csv`,
   `E9_efeitos_marginais.csv`, `P1_estimativas.csv`, `P1_dap.csv` e `P1h_magnitudes.csv`, e o resumo registra o
   portão aprovado.
3. `TestNumeros`: rótulos e hashes; razão de chances, IC, p, D_UF, km e BKY recalculados das linhas e da covariância
   gravada; mesma amostra nas duas versões; M1 e M5 iguais aos do `VC_estimativas.csv`; correção conferida contra a
   leitura da auditoria 36; leitura e mudanças refeitas; inventário conferido nos termos; integridade.
4. `TestDoc57v`: o doc 57v é igual ao gerado, tem os marcadores e nenhum número de resultado fora dos blocos.
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
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "48_sensibilidades_ciclo2_quadro_1302.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("sensibilidades_ciclo2_quadro_1302_48", SCRIPT)
M = importlib.util.module_from_spec(_spec)
sys.modules["sensibilidades_ciclo2_quadro_1302_48"] = M
_spec.loader.exec_module(M)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
CSV = OUT / "VD_estimativas.csv"
RESUMO = OUT / "VD_resumo.json"
FIG = OUT / "VD_figuras" / "VD_antigo_corrigido.png"
DOC = ROOT / "docs" / "06_execucao" / "57v_sensibilidades_ciclo2_quadro_1302.md"
A36 = ROOT / "output" / "auditoria_H1" / "a36_celulas.csv"
NATUREZA_SINTETICA = "SINTETICO_TESTE"
TOL = 1e-8
B = M.B


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def ler_csv(p: Path) -> pd.DataFrame:
    return pd.read_csv(p, dtype={"ciclo": str})


def dif_rel(a, b) -> float:
    """Escrita no teste, sem a função do script: absoluta até 1, relativa acima; NaN só com NaN."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    assert (np.isnan(a) == np.isnan(b)).all(), "NaN em só um dos lados"
    ok = ~np.isnan(a)
    return float(np.max(np.abs(a[ok] - b[ok]) / np.maximum(1.0, np.abs(b[ok])))) if ok.any() else 0.0


# ---------------------------------------------------------------------------
# 1. Sintético (só em memória)
# ---------------------------------------------------------------------------

class TestSintetico(unittest.TestCase):
    """Tudo aqui é sintético, gerado em memória e rotulado SINTETICO_TESTE."""

    def setUp(self) -> None:
        rng = np.random.default_rng(52)
        self.g = pd.DataFrame({"natureza_dos_dados": NATUREZA_SINTETICA, "modelo": "Mx", "ciclo": "empilhado",
                               "tipo_linha": "coeficiente", "termo": [f"t{i}" for i in range(6)],
                               "coef": rng.normal(0, 0.3, 6), "ep_cluster_conjunto": rng.uniform(0.01, 0.1, 6),
                               "q_bky": [np.nan] * 5 + [0.04]})
        self.g.loc[5, "coef"] = 812.3456789  # valor grande: comparação relativa

    def test_passa_com_numeros_iguais(self) -> None:
        ok, difs, n = M.comparar(self.g.copy(), self.g, ["modelo", "ciclo", "tipo_linha", "termo"],
                                 ["coef", "ep_cluster_conjunto", "q_bky"])
        self.assertTrue(ok)
        self.assertEqual(n, 6)
        self.assertEqual(max(difs.values()), 0.0)

    def test_falha_com_2e_8_abaixo_de_1(self) -> None:
        n = self.g.copy()
        n.loc[0, "coef"] += 2e-8
        _, difs, _ = M.comparar(n, self.g, ["modelo", "ciclo", "tipo_linha", "termo"], ["coef"])
        self.assertGreater(difs["coef"], TOL)

    def test_relativa_acima_de_1(self) -> None:
        n = self.g.copy()
        n.loc[5, "coef"] += 5e-7          # relativa ≈ 6e−10: passa
        _, difs, _ = M.comparar(n, self.g, ["modelo", "ciclo", "tipo_linha", "termo"], ["coef"])
        self.assertLessEqual(difs["coef"], TOL)
        n.loc[5, "coef"] += 1e-4          # relativa ≈ 1e−7: falha
        _, difs, _ = M.comparar(n, self.g, ["modelo", "ciclo", "tipo_linha", "termo"], ["coef"])
        self.assertGreater(difs["coef"], TOL)

    def test_nan_so_casa_com_nan(self) -> None:
        n = self.g.copy()
        n.loc[0, "q_bky"] = 0.5
        _, difs, _ = M.comparar(n, self.g, ["modelo", "ciclo", "tipo_linha", "termo"], ["q_bky"])
        self.assertEqual(difs["q_bky"], float("inf"))

    def test_linha_sem_par_falha(self) -> None:
        n = self.g.copy()
        n.loc[0, "termo"] = "outro"
        ok, _, _ = M.comparar(n, self.g, ["modelo", "ciclo", "tipo_linha", "termo"], ["coef"])
        self.assertFalse(ok)

    def test_regra_do_conjunto_e_conferencia(self) -> None:
        conj = pd.DataFrame({"ciclo": [2, 2, 2, 1], "co_cnes_7d": ["0000001", "0000002", "0000003", "0000004"],
                             "cod_curso": [1, 1, 2, 1], "id_conjunto_escolha": ["c2_curso01", "c2_curso01", "c2_curso02",
                                                                                "c1_curso01"],
                             "co_ibge": ["100000"] * 4, "faixa_anunciada": ["FAIXA 3"] * 4, "macrorregiao": ["SUL"] * 4,
                             "estrato_territorial": ["capital"] * 4, "vagas_imediatas": [2.0, 0.0, 1.0, 3.0],
                             "tem_vaga_imediata": [1, 0, 1, 1], "log_vagas_imediatas_mais_1": np.log([3.0, 1.0, 2.0, 4.0]),
                             "bolsa_mil": [10.0] * 4, "s_mil": [250.0] * 4, "populacao_2022": [1e4] * 4})
        s = M.sensibilidade_pela_regra(conj)
        self.assertEqual(len(s), 3)
        self.assertTrue((s["tem_vaga_imediata"] == 1).all())
        self.assertEqual(M.conferir_sensibilidade_gravada(s.iloc[::-1], s)["celulas"], 3)
        with self.assertRaises(M.FalhaValidacao):
            M.conferir_sensibilidade_gravada(s.iloc[:2], s)
        s2 = s.copy()
        s2.loc[0, "log_vagas_imediatas_mais_1"] += 1e-3
        with self.assertRaises(M.FalhaValidacao):
            M.conferir_sensibilidade_gravada(s2, s)

    def test_marca_refeita_so_no_ciclo_2_sem_imputar(self) -> None:
        cand = pd.DataFrame({"ciclo": [2, 2, 1], "co_cnes_7d": ["0000001", "0000002", "0000001"], "cod_curso": [1, 1, 1],
                             "opcao_rank": [1, 1, 1], "celula_no_quadro": [1, 1, 1],
                             "celula_com_vaga_imediata": [1.0, 1.0, 1.0]})
        q1903 = pd.DataFrame({"co_cnes_7d": ["0000001", "0000002"], "cod_curso": [1, 1], "vagas_imediatas": [2.0, 1.0]})
        q1302 = pd.DataFrame({"co_cnes_7d": ["0000001", "0000002"], "cod_curso": [1, 1], "vagas_imediatas": [2.0, 0.0]})
        c, diag = M.corrigir_candidatos(cand, q1302, q1903)
        self.assertEqual(c["celula_com_vaga_imediata"].tolist(), [1.0, 0.0, 1.0])
        self.assertEqual(diag["primeiras_opcoes_com_vaga_imediata_13fev"], 1)
        with self.assertRaises(M.FalhaValidacao):     # célula sem linha no quadro de 13/02: para
            M.corrigir_candidatos(cand, q1302.iloc[:1], q1903)
        cand2 = cand.copy()
        cand2.loc[1, "celula_com_vaga_imediata"] = 0.0
        with self.assertRaises(M.FalhaValidacao):     # marca gravada que não bate com 19/03: para
            M.corrigir_candidatos(cand2, q1302, q1903)

    def test_regra_vd1(self) -> None:
        a = pd.Series({"estimativa": 1.9, "ic95_inf": 1.4, "ic95_sup": 2.6})
        self.assertEqual(M.regra_vd1(a, pd.Series({"estimativa": 1.6, "ic95_inf": 1.1, "ic95_sup": 2.3})), "MANTEM")
        self.assertEqual(M.regra_vd1(a, pd.Series({"estimativa": 1.3, "ic95_inf": 0.9, "ic95_sup": 1.9})),
                         "DEPENDIA_DO_QUADRO_POS_RESULTADO")
        self.assertEqual(M.regra_vd1(a, pd.Series({"estimativa": 0.6, "ic95_inf": 0.4, "ic95_sup": 0.8})),
                         "SINAL_OPOSTO")

    def test_criterios(self) -> None:
        base = {"entra_bky": False, "q_bky": np.nan, "chave_modelo": "M2", "p_mle": np.nan, "p": 0.2}
        r = pd.Series({**base, "tipo_linha": "razao_chances_por_5mil", "estimativa": 1.5, "ic95_inf": 1.1,
                       "ic95_sup": 2.0})
        self.assertEqual(M.criterio(r), ("IC 95% exclui 1", True))
        r = pd.Series({**base, "tipo_linha": "coeficiente", "estimativa": 0.1, "ic95_inf": -0.1, "ic95_sup": 0.3})
        self.assertEqual(M.criterio(r), ("IC 95% exclui 0", False))
        r = pd.Series({**base, "entra_bky": True, "q_bky": 0.03, "tipo_linha": "interacao", "estimativa": 0.1,
                       "ic95_inf": -0.1, "ic95_sup": 0.3})
        self.assertEqual(M.criterio(r), ("q BKY < 0,05", True))
        r = pd.Series({**base, "chave_modelo": "M6_curso", "p_mle": 0.01, "tipo_linha": "interacao", "estimativa": 0.1,
                       "ic95_inf": -0.1, "ic95_sup": 0.3})
        self.assertEqual(M.criterio(r), ("p MV < 0,05", True))
        self.assertEqual(M._sinal(0.8, 1.0), -1)
        self.assertEqual(M._sinal(1.2, 1.0), 1)
        self.assertEqual(M._sinal(-0.2), -1)


# ---------------------------------------------------------------------------
# 2. Portão real
# ---------------------------------------------------------------------------

class TestPortaoReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = ler_csv(CSV)
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        cls.ant = cls.est[cls.est["versao"] == M.ANTIGA]

    def test_resumo_registra_portao_aprovado(self) -> None:
        p = self.resumo["portao"]
        self.assertEqual(p["status"], "PASSOU")
        self.assertEqual(p["tolerancia"], TOL)
        self.assertEqual(len(p["linhas"]), 2 + 13 + 4 + 9)
        for linha in p["linhas"]:
            self.assertTrue(linha["passou"], linha)
            self.assertTrue(linha["todas_casadas"], linha)
            self.assertGreater(linha["linhas_reestimadas"], 0)
            for k, v in linha.items():
                if k.startswith("dif_max_"):
                    self.assertLessEqual(v, TOL, (linha["linha"], k))

    def test_E9_antigo_igual_ao_gravado(self) -> None:
        e9, efe = ler_csv(OUT / "E9_estimativas.csv"), ler_csv(OUT / "E9_efeitos_marginais.csv")
        for chave, ciclo in (("E9s_2", "2"), ("E9s_emp", M.EMPILHADO)):
            g = e9[(e9["ciclo"] == ciclo) & (e9["modelo"] == M.MOD_E9) & (e9["conjunto"] == "sensibilidade") &
                   (e9["especificacao"] == M.ESPEC_E9)].set_index("termo")
            a = self.ant[(self.ant["chave_modelo"] == chave) & (self.ant["tipo_linha"] == "coeficiente")].set_index("termo")
            self.assertEqual(list(a.index), list(g.index))
            for ca, cg in (("estimativa", "coef"), ("ep_cluster_conjunto", "ep_cluster_conjunto"), ("ep_mle", "ep_mle"),
                           ("ep_cluster_candidato", "ep_cluster_candidato"), ("ic95_inf", "ic95_inf"),
                           ("ic95_sup", "ic95_sup"), ("p", "p"), ("n_candidatos", "n_candidatos")):
                self.assertLessEqual(dif_rel(a[ca], g[cg]), TOL, (chave, ca))
            self.assertNotIn("tem_vaga_imediata", a.index)  # constante no conjunto e omitida, como no doc 42
            f = efe[(efe["ciclo"] == ciclo) & (efe["modelo"] == M.MOD_E9) & (efe["conjunto"] == "sensibilidade") &
                    (efe["especificacao"] == M.ESPEC_E9) & (efe["termo"] == B)].set_index("quantidade")
            for q in ("razao_chances_por_5mil", "variacao_prob_media_pp"):
                o = self.ant[(self.ant["chave_modelo"] == chave) & (self.ant["tipo_linha"] == q)].iloc[0]
                for col in ("estimativa", "ic95_inf", "ic95_sup"):
                    self.assertLessEqual(dif_rel([o[col]], [f.loc[q, col]]), TOL, (chave, q, col))

    def test_P1_antigo_igual_ao_gravado(self) -> None:
        p1 = ler_csv(OUT / "P1_estimativas.csv")
        a = self.ant[self.ant["bloco"] == "P1"]
        a = a[a["tipo_linha"] != "razao_chances_por_5mil"]
        for modelo in ("M1", "M2", "M4", "M5", "M6_nota", "M6_municipio", "M6_curso", "M7", "M8", "M9"):
            sa = a[a["modelo"] == modelo]
            sg = p1[p1["modelo"] == modelo]
            self.assertEqual(len(sa), len(sg), modelo)
            m = sa.merge(sg, on=["modelo", "ciclo", "tipo_linha", "termo"], suffixes=("", "_g"), validate="one_to_one")
            self.assertEqual(len(m), len(sg), modelo)
            for ca, cg in (("estimativa", "coef"), ("ep_cluster_conjunto", "ep_cluster_conjunto_g"),
                           ("ep_mle", "ep_mle_g"), ("ic95_inf", "ic95_inf_g"), ("ic95_sup", "ic95_sup_g"), ("p", "p_g"),
                           ("p_mle", "p_mle_g"), ("estatistica_wald", "estatistica_wald_g"), ("q_bky", "q_bky_g")):
                self.assertLessEqual(dif_rel(m[ca], m[cg]), TOL, (modelo, ca))

    def test_DAP_e_P1h_antigos_iguais_aos_gravados(self) -> None:
        dap = ler_csv(OUT / "P1_dap.csv")
        a = self.ant[self.ant["tipo_linha"] == "dap"]
        for r in a.itertuples(index=False):
            g = dap[(dap["modelo"] == r.modelo) & (dap["ciclo"] == r.ciclo) & (dap["atributo"] == r.termo)].iloc[0]
            for ca, cg in (("estimativa", "dap"), ("ic95_inf", "ic95_delta_inf"), ("ic95_sup", "ic95_delta_sup"),
                           ("ic95_boot_inf", "ic95_boot_inf"), ("ic95_boot_sup", "ic95_boot_sup")):
                self.assertLessEqual(dif_rel([getattr(r, ca)], [g[cg]]), TOL, (r.chave_modelo, r.termo, ca))
        self.assertEqual(len(a), 16)
        h = ler_csv(OUT / "P1h_magnitudes.csv")
        a = self.ant[self.ant["bloco"] == "P1h"]
        self.assertEqual(len(a), 9)
        for r in a.itertuples(index=False):
            g = h[(h["modelo"] == r.modelo) & (h["ciclo"] == r.ciclo) & (h["componente"] == r.termo)].iloc[0]
            for c in ("estimativa", "ep_cluster_conjunto", "ic95_inf", "ic95_sup", "li95_unilateral", "p_unilateral",
                      "ic95_fieller_inf", "ic95_fieller_sup", "q_bky"):
                self.assertLessEqual(dif_rel([getattr(r, c)], [g[c]]), TOL, (r.chave_modelo, r.termo, c))


# ---------------------------------------------------------------------------
# 3. Números contra output/
# ---------------------------------------------------------------------------

class TestNumeros(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = ler_csv(CSV)
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def _um(self, versao: str, chave: str, tipo: str, termo: str | None = None) -> pd.Series:
        return M._sel(self.est, versao, chave, tipo, termo)

    def test_rotulos_e_hashes(self) -> None:
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "ADENDO_52D_POS_RESULTADO").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "ADENDO_52D_POS_RESULTADO")
        self.assertEqual(set(self.est["versao"]), set(M.VERSOES))
        self.assertEqual(self.resumo["adendo"]["sha256"], sha256(M.ADENDO_MD))
        for caminho, h in self.resumo["saidas"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        self.assertEqual(set(self.est["id_vd"]), {"VD-1", "VD-2", "VD-3", "VD-4", "apoio"})

    def test_saidas_antigas_nao_regravadas(self) -> None:
        ent = {e["caminho"]: e["sha256"] for e in self.resumo["entradas"]}
        for nome in ("E9_estimativas.csv", "E9_efeitos_marginais.csv", "P1_estimativas.csv", "P1_dap.csv",
                     "P1h_magnitudes.csv", "VC_estimativas.csv"):
            self.assertIn(f"output/rdd_bolsa/{nome}", ent)
        texto = SCRIPT.read_text(encoding="utf-8")
        for alvo in ("to_csv(E9_", "to_csv(P1_", "to_csv(P1H_", "to_csv(VC_", "E9_EST.write", "P1_EST.write",
                     "P1_DAP.write", "P1H_CSV.write", "VC_CSV.write", "VC.OUT_RESUMO"):
            self.assertNotIn(alvo, texto)

    def test_razao_de_chances_recalculada(self) -> None:
        for v in M.VERSOES:
            for chave in ("E9s_2", "E9s_emp") + M.VD3_BETA:
                t = M.TERMO_RC.get(chave, B)
                c = self._um(v, chave, "coeficiente", t)
                o = self._um(v, chave, "razao_chances_por_5mil")
                if pd.isna(c["estimativa"]):
                    self.assertTrue(pd.isna(o["estimativa"]))
                    continue
                self.assertAlmostEqual(o["estimativa"], math.exp(5 * c["estimativa"]), delta=1e-8)
                self.assertAlmostEqual(o["ic95_inf"], math.exp(5 * c["ic95_inf"]), delta=1e-8)
                self.assertAlmostEqual(o["ic95_sup"], math.exp(5 * c["ic95_sup"]), delta=1e-8)
                self.assertAlmostEqual(o["p"], c["p"], delta=1e-12)

    def test_coeficientes_ic_e_p(self) -> None:
        c = self.est[(self.est["tipo_linha"] == "coeficiente") & self.est["ic95_inf"].notna()]
        z = stats.norm.ppf(0.975)
        np.testing.assert_allclose(c["ic95_inf"], c["estimativa"] - z * c["ep_cluster_conjunto"], atol=1e-8)
        np.testing.assert_allclose(c["ic95_sup"], c["estimativa"] + z * c["ep_cluster_conjunto"], atol=1e-8)
        cp = c[c["p"].notna()]
        np.testing.assert_allclose(cp["p"], 2 * stats.norm.sf(np.abs(cp["estimativa"] / cp["ep_cluster_conjunto"])),
                                   atol=1e-8)

    def test_d_uf_e_km_da_covariancia_gravada(self) -> None:
        z, zu = stats.norm.ppf(0.975), stats.norm.ppf(0.95)
        for v in M.VERSOES:
            for chave in ("M2", "M4", "M7", "M5_2"):
                cv = self.resumo["covariancias"][v][chave]
                ib, iu = cv["termos"].index(B), cv["termos"].index("mesma_uf")
                th, V = np.array(cv["theta"]), np.array(cv["V_cluster_conjunto"])
                est = th[iu] - 10 * th[ib]
                ep = math.sqrt(V[iu, iu] + 100 * V[ib, ib] - 20 * V[iu, ib])
                d = self._um(v, chave, "D_UF")
                self.assertAlmostEqual(d["estimativa"], est, delta=1e-8)
                self.assertAlmostEqual(d["ep_cluster_conjunto"], ep, delta=1e-8)
                self.assertAlmostEqual(d["li95_unilateral"], est - zu * ep, delta=1e-8)
                self.assertAlmostEqual(d["p_unilateral"], stats.norm.sf(est / ep), delta=1e-12)
            cv = self.resumo["covariancias"][v]["M1"]
            ib, ig = cv["termos"].index(B), cv["termos"].index("distancia_100km")
            th, V = np.array(cv["theta"]), np.array(cv["V_cluster_conjunto"])
            for termo, passo in (("K5", 5.0), ("K10", 10.0)):
                k = 100 * passo * th[ib] / (-th[ig])
                g = np.zeros(len(th))
                g[ib], g[ig] = 100 * passo / (-th[ig]), 100 * passo * th[ib] / th[ig] ** 2
                ep = math.sqrt(g @ V @ g)
                r = self._um(v, "M1", "km_equivalentes", termo)
                self.assertLessEqual(dif_rel([r["estimativa"]], [k]), 1e-8)
                self.assertLessEqual(dif_rel([r["ic95_inf"]], [k - z * ep]), 1e-8)

    def test_dap_da_covariancia_gravada(self) -> None:
        for v in M.VERSOES:
            for chave in ("M1", "M4", "M7", "M5_2"):
                cv = self.resumo["covariancias"][v][chave]
                ib, ig, iu = (cv["termos"].index(t) for t in (B, "distancia_100km", "mesma_uf"))
                th = np.array(cv["theta"])
                d = self._um(v, chave, "dap", "distancia_100km_a_menos")
                self.assertLessEqual(dif_rel([d["estimativa"]], [-th[ig] / th[ib]]), 1e-8)
                d = self._um(v, chave, "dap", "mesma_uf")
                self.assertLessEqual(dif_rel([d["estimativa"]], [th[iu] / th[ib]]), 1e-8)

    def test_bky_refeito_por_familia(self) -> None:
        for v in M.VERSOES:
            for fam, col in ((M.FAMILIA_P1, "p"), (M.FAMILIA_P1H3, "p_unilateral")):
                f = self.est[(self.est["versao"] == v) & (self.est["familia_bky"] == fam) & self.est[col].notna()]
                self.assertEqual(len(f), 12 if fam == M.FAMILIA_P1 else 6, (v, fam))
                np.testing.assert_allclose(f["q_bky"].to_numpy(), M.L.qvalores_bky(f[col].to_numpy()), atol=1e-12)
        e9 = self.est[self.est["bloco"] == "E9"]
        self.assertFalse(e9["entra_bky"].any())
        self.assertTrue(e9["q_bky"].isna().all())

    def test_mesma_amostra_e_ciclos_sem_mudanca(self) -> None:
        a = self.est[(self.est["versao"] == M.ANTIGA) & (self.est["bloco"] != "E9")].reset_index(drop=True)
        c = self.est[(self.est["versao"] == M.CORRIGIDA) & (self.est["bloco"] != "E9")].reset_index(drop=True)
        self.assertEqual(len(a), len(c))
        for col in ("chave_modelo", "tipo_linha", "termo", "n_candidatos", "n_conjuntos"):
            self.assertTrue((a[col].fillna(-1).astype(str) == c[col].fillna(-1).astype(str)).all(), col)
        for chave in ("M5_1", "M5_3"):
            m = (a["chave_modelo"] == chave) & (a["tipo_linha"] == "coeficiente")
            np.testing.assert_array_equal(a.loc[m, "estimativa"].to_numpy(), c.loc[m, "estimativa"].to_numpy())
        for chave in ("M2", "M4", "M7", "M6_nota"):
            ta = self.est[(self.est["versao"] == M.ANTIGA) & (self.est["chave_modelo"] == chave) &
                          (self.est["termo"] == "tem_vaga_imediata")]["estimativa"].iloc[0]
            tc = self.est[(self.est["versao"] == M.CORRIGIDA) & (self.est["chave_modelo"] == chave) &
                          (self.est["termo"] == "tem_vaga_imediata")]["estimativa"].iloc[0]
            self.assertNotEqual(ta, tc, chave)
        n = {(r.versao, r.chave_modelo): r.n_candidatos
             for r in self.est[(self.est["tipo_linha"] == "coeficiente") & (self.est["termo"] == B)].itertuples()}
        self.assertEqual(n[(M.ANTIGA, "E9s_2")], 1798)
        cc = self.resumo["conferencias"]["marca_dos_candidatos"]
        self.assertEqual(n[(M.CORRIGIDA, "E9s_2")], cc["primeiras_opcoes_com_vaga_imediata_13fev"])
        self.assertEqual(n[(M.ANTIGA, "M2")], 5421)

    def test_m1_e_m5_iguais_ao_vc(self) -> None:
        vc = ler_csv(OUT / "VC_estimativas.csv")
        for v in M.VERSOES:
            for chave in ("M1", "M5_2"):
                a = self.est[(self.est["versao"] == v) & (self.est["chave_modelo"] == chave) &
                             (self.est["tipo_linha"] == "coeficiente")]
                g = vc[(vc["versao"] == v) & (vc["chave_modelo"] == chave) & (vc["tipo_linha"] == "coeficiente")]
                self.assertEqual(list(a["termo"]), list(g["termo"]))
                self.assertLessEqual(dif_rel(a["estimativa"], g["estimativa"]), TOL)
                self.assertLessEqual(dif_rel(a["ep_cluster_conjunto"], g["ep_cluster_conjunto"]), TOL)

    def test_correcao_contra_auditoria_36(self) -> None:
        a = pd.read_csv(A36)
        a = a[a["ciclo"] == 2]
        s = self.resumo["correcao"]["sensibilidade_ciclo2"]
        self.assertEqual(s["celulas_13fev"], int((a["vagas_imediatas_13fev"] > 0).sum()))
        self.assertEqual(s["celulas_19mar"], int((a["vagas_imediatas_pipe_versao"] > 0).sum()))
        self.assertEqual(s["vagas_imediatas_13fev"], float(a["vagas_imediatas_13fev"].sum()))
        self.assertEqual(s["celulas_em_ambas"], s["celulas_13fev"])
        cc = self.resumo["conferencias"]["marca_dos_candidatos"]
        self.assertEqual(cc["imputadas"], 0)
        self.assertEqual(cc["marca_gravada_igual_ao_quadro_19mar"], cc["linhas_ciclo2"])
        self.assertEqual(self.resumo["conferencias"]["quadro_1302_contra_a36"]["celulas_com_vagas_imediatas_diferentes"], 0)

    def test_leitura_e_mudancas_refeitas(self) -> None:
        self.assertEqual(M.P1._nan_none(M.mudancas(self.est)), self.resumo["mudancas"])
        self.assertEqual(M.P1._nan_none(M.leitura(self.est)), self.resumo["leitura"])
        a = self._um(M.ANTIGA, "E9s_2", "razao_chances_por_5mil")
        c = self._um(M.CORRIGIDA, "E9s_2", "razao_chances_por_5mil")
        self.assertEqual(self.resumo["leitura"]["VD1"]["regra"], M.regra_vd1(a, c))

    def test_inventario_nos_termos(self) -> None:
        for chave in M.VD3:
            for v in M.VERSOES:
                termos = set(self.est[(self.est["versao"] == v) & (self.est["chave_modelo"] == chave)]["termo"])
                self.assertTrue({"tem_vaga_imediata", "log_vagas_imediatas_mais_1"} <= termos, (chave, v))
        for v in M.VERSOES:
            termos = set(self.est[(self.est["versao"] == v) & (self.est["chave_modelo"] == "E9s_2")]["termo"])
            self.assertIn("log_vagas_imediatas_mais_1", termos)
        dap = self.est[self.est["tipo_linha"] == "dap"]
        self.assertEqual(sorted(set(dap["chave_modelo"])), sorted(M.DAP_VD4))

    def test_integridade(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", texto)
        self.assertNotIn("data/ivs", texto)
        for col in self.est.columns:
            self.assertNotRegex(col.lower(), r"cpf|nome|crm|id_candidato")
        corpo = CSV.read_text(encoding="utf-8").lower()
        for padrao in ("cpf", "c1_0", "c2_0", "c3_0"):
            self.assertNotIn(padrao, corpo)
        self.assertNotIn("id_candidato\":", RESUMO.read_text(encoding="utf-8"))

    def test_figura_com_como_ler(self) -> None:
        self.assertTrue(FIG.exists())
        self.assertEqual(self.resumo["figura"]["sha256"], sha256(FIG))
        self.assertTrue(self.resumo["figura"]["como_ler"])
        self.assertIn("Como ler", DOC.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 4. Doc 57v
# ---------------------------------------------------------------------------

BLOCOS = ("resposta", "portao", "inventario", "correcao", "e9", "p1", "m6", "bky", "dap", "p1h", "mudancas", "figura",
          "decisoes")


class TestDoc57v(unittest.TestCase):
    def test_doc_igual_ao_gerado(self) -> None:
        self.assertEqual(DOC.read_text(encoding="utf-8"), M.gerar_doc(M.ler_est(), M.ler_resumo()))

    def test_marcadores_e_secoes(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        for nome in BLOCOS:
            self.assertEqual(t.count(f"<!-- VD:{nome}:inicio -->"), 1, nome)
            self.assertEqual(t.count(f"<!-- VD:{nome}:fim -->"), 1, nome)
        for s in ("## 1. Resposta curta", "## 2. Portão", "## 3. O que usa o tipo de vaga", "## 7. Decisões de "
                  "implementação", "## 8. Limites", "ADENDO_52D_POS_RESULTADO", "**Auditoria:** pendente"):
            self.assertIn(s, t)
        self.assertLess(t.index("<!-- VD:decisoes:inicio -->"), t.index("## 8. Limites"))

    def test_nenhum_numero_de_resultado_fora_dos_blocos(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        fora = re.sub(r"<!-- VD:(\w+):inicio -->.*?<!-- VD:\1:fim -->", "", t, flags=re.S)
        fora = "\n".join(x for x in fora.splitlines() if not x.startswith("#"))  # números de seção
        self.assertEqual(re.findall(r"\d+,\d+", fora), [])
        self.assertEqual(re.findall(r"\d+\.\d+", fora), [])

    def test_linguagem(self) -> None:
        t = " ".join(DOC.read_text(encoding="utf-8").split())
        self.assertIn("preferência revelada, não efeito causal", t)
        self.assertIn("pacote do corte", t)
        self.assertIn("Não é efeito da participação no PMM-E", t)
        self.assertIn("Em linguagem simples", t)
        self.assertNotIn("a bolsa funciona", t.lower())

    def test_decisoes_iguais_as_do_pre_registro(self) -> None:
        """O bloco de decisões do doc é o texto das constantes do script (commitado antes das estimativas)."""
        t = DOC.read_text(encoding="utf-8")
        ini = t.index("<!-- VD:decisoes:inicio -->") + len("<!-- VD:decisoes:inicio -->\n")
        fim = t.index("\n<!-- VD:decisoes:fim -->")
        self.assertEqual(t[ini:fim], M.texto_decisoes())
        self.assertEqual(len(M.DECISOES), 10)
        self.assertTrue(all(d["data"] == "2026-10-26" for d in M.DECISOES))


if __name__ == "__main__":
    unittest.main()
