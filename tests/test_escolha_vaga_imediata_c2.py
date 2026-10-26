"""Testes do adendo 52c: `scripts/rdd_bolsa/42_escolha_vaga_imediata_c2.py`.

Partes:

1. `TestPortaoSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados `SINTETICO_TESTE` e nunca
   gravados. Montam ajustes e CSV coerentes e conferem que o portão passa com os números iguais e falha com 2e−8 de
   diferença (E9, P1 e D_UF).
2. `TestPortaoReal`: a versão antiga gravada em `VC_estimativas.csv` bate, linha a linha, com `E9_estimativas.csv`,
   `E9_efeitos_marginais.csv`, `P1_estimativas.csv` e `P1h_magnitudes.csv` (≤ 1e−8), e o resumo registra o portão
   aprovado.
3. `TestNumeros`: rótulos e hashes; razão de chances, D_UF, EP, IC, p unilateral e Holm recalculados das linhas e da
   covariância gravada no resumo; mesma amostra nas duas versões; ciclos 1 e 3 idênticos; a correção conferida contra
   a leitura independente da auditoria 36 (`a36_celulas.csv`); nada imputado; sem identificador pessoal; E9, P1 e P1h
   não regravados; script sem o arquivo de IVS errado.
4. `TestDoc57p`: o doc 57p é igual ao gerado das saídas e tem as seções e a linguagem pedidas.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "42_escolha_vaga_imediata_c2.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("escolha_vaga_imediata_c2_42", SCRIPT)
M = importlib.util.module_from_spec(_spec)
sys.modules["escolha_vaga_imediata_c2_42"] = M
_spec.loader.exec_module(M)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
CSV = OUT / "VC_estimativas.csv"
RESUMO = OUT / "VC_resumo.json"
FIG = OUT / "VC_figuras" / "VC_antigo_corrigido.png"
DOC = ROOT / "docs" / "06_execucao" / "57p_escolha_vaga_imediata_c2.md"
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


# ---------------------------------------------------------------------------
# 1. Sintético (só em memória)
# ---------------------------------------------------------------------------

TERMOS_E9 = [B, "ivs_inclinacao", "tem_vaga_imediata", "log_vagas_imediatas_mais_1"]
TERMOS_P1 = [B, "ivs_inclinacao", "tem_vaga_imediata", "log_vagas_imediatas_mais_1", "distancia_100km", "mesma_uf",
             "mesma_regiao_saude", "mesmo_municipio"]


def _V(rng, k: int, escala: float) -> np.ndarray:
    A = rng.normal(0, 0.03 * escala, (k, k))
    return A @ A.T + np.diag(np.full(k, 1e-4))


def res_sintetico(semente: int = 7) -> dict:
    """SINTÉTICO: um ajuste por modelo do adendo, no formato devolvido por `estimar_versao`."""
    rng = np.random.default_rng(semente)
    res = {"natureza_dos_dados": NATUREZA_SINTETICA}
    for chave, bloco, _, _ in M.MODELOS:
        termos = TERMOS_E9 if bloco == "E9" else TERMOS_P1
        k = len(termos)
        r = {"ok": True, "termos": termos, "theta": rng.normal(0, 0.5, k), "V_conj": _V(rng, k, 1.0),
             "V_mle": _V(rng, k, 0.5), "V_cand": _V(rng, k, 0.6), "G_conj": 20, "G_cand": 900, "n_candidatos": 900,
             "n_grupos": 900, "n_linhas": 50000, "n_conjuntos": 20}
        if bloco == "E9":
            r["_efeitos"] = [{"quantidade": q, "estimativa": rng.normal(), "ic95_inf": rng.normal(),
                              "ic95_sup": rng.normal()} for q in ("razao_chances_por_5mil", "log_razao_chances_por_5mil",
                                                                  "variacao_prob_media_pp")]
        res[chave] = r
    return res


def csvs_sinteticos(res: dict) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """SINTÉTICO: o que os scripts 16, 25 e 25c teriam gravado para `res`."""
    e9, efe, p1, p1h = [], [], [], []
    for chave, bloco, modelo, ciclo in M.MODELOS:
        r = res[chave]
        ep = {n: np.sqrt(np.diag(r[V])) for n, V in (("c", "V_conj"), ("m", "V_mle"), ("k", "V_cand"))}
        for i, t in enumerate(r["termos"]):
            linha = {"natureza_dos_dados": NATUREZA_SINTETICA, "ciclo": ciclo, "termo": t, "coef": r["theta"][i],
                     "ep_cluster_conjunto": ep["c"][i], "ep_mle": ep["m"][i], "ep_cluster_candidato": ep["k"][i]}
            if bloco == "E9":
                e9.append({**linha, "modelo": M.MOD_E9, "conjunto": "principal", "especificacao": M.ESPEC_E9})
            else:
                p1.append({**linha, "modelo": modelo, "tipo_linha": "coeficiente"})
        if bloco == "E9":
            for q in r["_efeitos"]:
                efe.append({"natureza_dos_dados": NATUREZA_SINTETICA, "ciclo": ciclo, "modelo": M.MOD_E9,
                            "conjunto": "principal", "especificacao": M.ESPEC_E9, "termo": B, **q})
        else:
            d = M.d_uf(chave, r)
            p1h.append({"natureza_dos_dados": NATUREZA_SINTETICA, "id_linha": "P1h-1" if chave == "M1" else "P1h-3",
                        "modelo": modelo, "ciclo": ciclo, **{k: d[k] for k in (
                            "estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf",
                            "ic95_sup", "p_unilateral")}})
    W, pw = M.wald_ciclos(res)
    p1.append({"natureza_dos_dados": NATUREZA_SINTETICA, "modelo": "M5", "ciclo": "1,2,3",
               "tipo_linha": "wald_igualdade_ciclos", "termo": "wald", "estatistica_wald": W, "p": pw})
    return pd.DataFrame(e9), pd.DataFrame(efe), pd.DataFrame(p1), pd.DataFrame(p1h)


class TestPortaoSintetico(unittest.TestCase):
    """Tudo aqui é sintético, gerado em memória e rotulado SINTETICO_TESTE."""

    def setUp(self) -> None:
        self.res = res_sintetico()
        self.assertEqual(self.res["natureza_dos_dados"], NATUREZA_SINTETICA)
        self.e9, self.efe, self.p1, self.p1h = csvs_sinteticos(self.res)

    def test_passa_com_numeros_iguais(self) -> None:
        p = M.portao(self.res, self.e9, self.efe, self.p1, self.p1h)
        self.assertEqual(p["status"], "PASSOU", p)
        self.assertEqual(len(p["linhas"]), 2 + 4 + 1 + 4)

    def test_falha_com_coeficiente_do_E9_diferente(self) -> None:
        e9 = self.e9.copy()
        e9.loc[(e9["ciclo"] == "2") & (e9["termo"] == "tem_vaga_imediata"), "coef"] += 2e-8
        self.assertEqual(M.portao(self.res, e9, self.efe, self.p1, self.p1h)["status"], "FALHA_REPRODUCAO_E9_2")

    def test_falha_com_razao_de_chances_diferente(self) -> None:
        efe = self.efe.copy()
        efe.loc[(efe["ciclo"] == M.EMPILHADO) & (efe["quantidade"] == "razao_chances_por_5mil"), "ic95_sup"] += 2e-8
        self.assertEqual(M.portao(self.res, self.e9, efe, self.p1, self.p1h)["status"], "FALHA_REPRODUCAO_E9_emp")

    def test_falha_com_ep_do_M5_diferente(self) -> None:
        p1 = self.p1.copy()
        p1.loc[(p1["modelo"] == "M5") & (p1["ciclo"] == "2") & (p1["termo"] == B), "ep_cluster_conjunto"] += 2e-8
        self.assertEqual(M.portao(self.res, self.e9, self.efe, p1, self.p1h)["status"], "FALHA_REPRODUCAO_M5_2")

    def test_falha_com_d_uf_diferente(self) -> None:
        p1h = self.p1h.copy()
        p1h.loc[p1h["id_linha"] == "P1h-1", "estimativa"] += 2e-8
        self.assertEqual(M.portao(self.res, self.e9, self.efe, self.p1, p1h)["status"], "FALHA_REPRODUCAO_D_UF_M1")

    def test_falha_com_termos_em_outra_ordem(self) -> None:
        p1 = self.p1.copy()
        m = (p1["modelo"] == "M1") & (p1["tipo_linha"] == "coeficiente")
        p1.loc[m] = p1.loc[m].iloc[::-1].to_numpy()
        self.assertEqual(M.portao(self.res, self.e9, self.efe, p1, self.p1h)["status"], "FALHA_REPRODUCAO_M1")

    def test_d_uf_e_combinacao_explicita(self) -> None:
        r = self.res["M1"]
        d = M.d_uf("M1", r)
        iu, ib = r["termos"].index("mesma_uf"), r["termos"].index(B)
        V = r["V_conj"]
        self.assertAlmostEqual(d["estimativa"], r["theta"][iu] - 10 * r["theta"][ib], places=14)
        self.assertAlmostEqual(d["ep_cluster_conjunto"], math.sqrt(V[iu, iu] + 100 * V[ib, ib] - 20 * V[iu, ib]),
                               places=14)

    def test_correcao_nao_imputa(self) -> None:
        """SINTÉTICO: célula do conjunto sem linha no quadro de 13/02 faz parar; troca só o ciclo 2."""
        conj = pd.DataFrame({"ciclo": [1, 2, 2], "co_cnes_7d": ["0000001", "0000002", "0000003"],
                             "cod_curso": [1, 1, 2], "co_ibge": ["100000"] * 3, "faixa_anunciada": ["FAIXA 3"] * 3,
                             "vagas_imediatas": [3, 2, 0], "tem_vaga_imediata": [1, 1, 0],
                             "log_vagas_imediatas_mais_1": np.log([4.0, 3.0, 1.0])})
        q = pd.DataFrame({"co_cnes_7d": ["0000002", "0000003"], "cod_curso": [1, 2], "co_ibge": ["100000"] * 2,
                          "faixa_anunciada": ["FAIXA 3"] * 2, "vagas_imediatas": [0.0, 1.0]})
        c, diag = M.corrigir(conj, q)
        self.assertEqual(c["tem_vaga_imediata"].tolist(), [1, 0, 1])
        self.assertAlmostEqual(c["log_vagas_imediatas_mais_1"].iloc[0], math.log(4.0))
        self.assertAlmostEqual(c["log_vagas_imediatas_mais_1"].iloc[2], math.log(2.0))
        self.assertEqual(diag["celulas_de_reserva_em_13fev_com_imediata_em_19mar"], 1)
        self.assertEqual(diag["celulas_com_imediata_em_13fev_e_reserva_em_19mar"], 1)
        with self.assertRaises(M.FalhaValidacao):
            M.corrigir(conj, q.iloc[:1])
        q2 = q.copy()
        q2.loc[1, "vagas_imediatas"] = np.nan
        with self.assertRaises(M.FalhaValidacao):
            M.corrigir(conj, q2)


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
        self.assertEqual(len(p["linhas"]), 11)
        for linha in p["linhas"]:
            self.assertTrue(linha["passou"], linha)
            self.assertTrue(linha["mesmos_termos_na_mesma_ordem"], linha)
            for k, v in linha.items():
                if k.startswith("dif_max_"):
                    self.assertLessEqual(v, TOL, (linha["linha"], k))

    def test_E9_antigo_igual_ao_gravado(self) -> None:
        e9 = ler_csv(OUT / "E9_estimativas.csv")
        efe = ler_csv(OUT / "E9_efeitos_marginais.csv")
        for chave, ciclo in (("E9_2", "2"), ("E9_emp", M.EMPILHADO)):
            g = e9[(e9["ciclo"] == ciclo) & (e9["modelo"] == M.MOD_E9) & (e9["conjunto"] == "principal") &
                   (e9["especificacao"] == M.ESPEC_E9)].set_index("termo")
            a = self.ant[(self.ant["chave_modelo"] == chave) & (self.ant["tipo_linha"] == "coeficiente")].set_index("termo")
            self.assertEqual(list(a.index), list(g.index))
            for col_a, col_g in (("estimativa", "coef"), ("ep_cluster_conjunto", "ep_cluster_conjunto"),
                                 ("ep_mle", "ep_mle"), ("ep_cluster_candidato", "ep_cluster_candidato"),
                                 ("ic95_inf", "ic95_inf"), ("ic95_sup", "ic95_sup"), ("p", "p")):
                self.assertLessEqual(float(np.max(np.abs(a[col_a] - g[col_g]))), TOL, (chave, col_a))
            f = efe[(efe["ciclo"] == ciclo) & (efe["modelo"] == M.MOD_E9) & (efe["conjunto"] == "principal") &
                    (efe["especificacao"] == M.ESPEC_E9) & (efe["termo"] == B)].set_index("quantidade")
            for q in ("razao_chances_por_5mil", "variacao_prob_media_pp"):
                o = self.ant[(self.ant["chave_modelo"] == chave) & (self.ant["tipo_linha"] == q)].iloc[0]
                for col in ("estimativa", "ic95_inf", "ic95_sup"):
                    self.assertLessEqual(abs(o[col] - f.loc[q, col]), TOL, (chave, q, col))

    def test_P1_antigo_igual_ao_gravado(self) -> None:
        p1 = ler_csv(OUT / "P1_estimativas.csv")
        for chave, _, modelo, ciclo in M.MODELOS[2:]:
            g = p1[(p1["modelo"] == modelo) & (p1["ciclo"] == ciclo) & (p1["tipo_linha"] == "coeficiente")].set_index("termo")
            a = self.ant[(self.ant["chave_modelo"] == chave) & (self.ant["tipo_linha"] == "coeficiente")].set_index("termo")
            self.assertEqual(list(a.index), list(g.index))
            for col_a, col_g in (("estimativa", "coef"), ("ep_cluster_conjunto", "ep_cluster_conjunto"),
                                 ("ep_mle", "ep_mle"), ("ep_cluster_candidato", "ep_cluster_candidato"),
                                 ("ic95_inf", "ic95_inf"), ("ic95_sup", "ic95_sup"), ("p", "p"),
                                 ("p_t_g_menos_1", "p_t_g_menos_1")):
                self.assertLessEqual(float(np.max(np.abs(a[col_a] - g[col_g]))), TOL, (chave, col_a))
        h = p1[p1["modelo"] == "M1"].set_index("termo").loc[B]
        a = self.ant[(self.ant["chave_modelo"] == "M1") & (self.ant["termo"] == B) &
                     (self.ant["tipo_linha"] == "coeficiente")].iloc[0]
        self.assertLessEqual(abs(a["p_holm"] - h["p_holm"]), TOL)
        w = p1[p1["tipo_linha"] == "wald_igualdade_ciclos"].iloc[0]
        wa = self.ant[self.ant["tipo_linha"] == "wald_igualdade_ciclos"].iloc[0]
        self.assertLessEqual(abs(wa["estatistica_wald"] - w["estatistica_wald"]), TOL)
        self.assertLessEqual(abs(wa["p"] - w["p"]), TOL)

    def test_D_UF_antigo_igual_ao_gravado(self) -> None:
        p1h = ler_csv(OUT / "P1h_magnitudes.csv")
        for chave, id_linha, modelo, ciclo in (("M1", "P1h-1", "M1", M.EMPILHADO), ("M5_1", "P1h-3", "M5", "1"),
                                               ("M5_2", "P1h-3", "M5", "2"), ("M5_3", "P1h-3", "M5", "3")):
            g = p1h[(p1h["id_linha"] == id_linha) & (p1h["modelo"] == modelo) & (p1h["ciclo"] == ciclo)].iloc[0]
            a = self.ant[(self.ant["chave_modelo"] == chave) & (self.ant["tipo_linha"] == "D_UF")].iloc[0]
            for col in ("estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf", "ic95_sup",
                        "li95_unilateral", "p_unilateral"):
                self.assertLessEqual(abs(a[col] - g[col]), TOL, (chave, col))
            if chave == "M1":
                self.assertLessEqual(abs(a["p_holm"] - g["p_holm"]), TOL)


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
        self.assertTrue((self.est["estatuto"] == "ADENDO_52C_CORRECAO_COVARIAVEL").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "ADENDO_52C_CORRECAO_COVARIAVEL")
        self.assertEqual(set(self.est["versao"]), set(M.VERSOES))
        self.assertEqual(self.resumo["adendo"]["sha256"], sha256(M.ADENDO_MD))
        for caminho, h in self.resumo["saidas"].items():
            self.assertEqual(sha256(ROOT / caminho), h, caminho)
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])

    def test_E9_P1_P1h_nao_regravados(self) -> None:
        """Os alvos do portão têm o mesmo hash que tinham quando o script os leu."""
        ent = {e["caminho"]: e["sha256"] for e in self.resumo["entradas"]}
        for nome in ("E9_estimativas.csv", "E9_efeitos_marginais.csv", "P1_estimativas.csv", "P1h_magnitudes.csv"):
            self.assertIn(f"output/rdd_bolsa/{nome}", ent)
        texto = SCRIPT.read_text(encoding="utf-8")
        for alvo in ("E9.OUT_ESTIMATIVAS.write", "OUT_EST.write", "P1H.OUT_CSV.write", "to_csv(E9_", "to_csv(P1_",
                     "to_csv(P1H_"):
            self.assertNotIn(alvo, texto)

    def test_razao_de_chances_recalculada(self) -> None:
        for v in M.VERSOES:
            for chave, *_ in M.MODELOS:
                c = self._um(v, chave, "coeficiente", B)
                o = self._um(v, chave, "razao_chances_por_5mil")
                self.assertAlmostEqual(o["estimativa"], math.exp(5 * c["estimativa"]), delta=1e-8)
                self.assertAlmostEqual(o["ic95_inf"], math.exp(5 * c["ic95_inf"]), delta=1e-8)
                self.assertAlmostEqual(o["ic95_sup"], math.exp(5 * c["ic95_sup"]), delta=1e-8)
                self.assertAlmostEqual(o["p"], c["p"], delta=1e-12)

    def test_coeficientes_ic_e_p(self) -> None:
        c = self.est[self.est["tipo_linha"] == "coeficiente"]
        z = stats.norm.ppf(0.975)
        np.testing.assert_allclose(c["ic95_inf"], c["estimativa"] - z * c["ep_cluster_conjunto"], atol=1e-8)
        np.testing.assert_allclose(c["ic95_sup"], c["estimativa"] + z * c["ep_cluster_conjunto"], atol=1e-8)
        np.testing.assert_allclose(c["p"], 2 * stats.norm.sf(np.abs(c["estimativa"] / c["ep_cluster_conjunto"])),
                                   atol=1e-8)

    def test_d_uf_da_covariancia_gravada(self) -> None:
        z, zu = stats.norm.ppf(0.975), stats.norm.ppf(0.95)
        for v in M.VERSOES:
            for chave in ("M1", "M5_1", "M5_2", "M5_3"):
                cv = self.resumo["covariancias"][v][chave]
                ib, iu = cv["termos"].index(B), cv["termos"].index("mesma_uf")
                th, V = np.array(cv["theta"]), np.array(cv["V_cluster_conjunto"])
                est = th[iu] - 10 * th[ib]
                ep = math.sqrt(V[iu, iu] + 100 * V[ib, ib] - 20 * V[iu, ib])
                d = self._um(v, chave, "D_UF")
                self.assertAlmostEqual(d["estimativa"], est, delta=1e-8)
                self.assertAlmostEqual(d["ep_cluster_conjunto"], ep, delta=1e-8)
                self.assertAlmostEqual(d["ic95_inf"], est - z * ep, delta=1e-8)
                self.assertAlmostEqual(d["li95_unilateral"], est - zu * ep, delta=1e-8)
                self.assertAlmostEqual(d["p_unilateral"], stats.norm.sf(est / ep), delta=1e-12)
                cb = self._um(v, chave, "coeficiente", B)
                cu = self._um(v, chave, "coeficiente", "mesma_uf")
                self.assertAlmostEqual(math.sqrt(V[ib, ib]), cb["ep_cluster_conjunto"], delta=1e-8)
                self.assertAlmostEqual(math.sqrt(V[iu, iu]), cu["ep_cluster_conjunto"], delta=1e-8)

    def test_holm_como_nos_protocolos(self) -> None:
        h = self.est[self.est["entra_holm"]]
        self.assertEqual(len(h), 4)  # P1a e P1h-1, nas duas versões
        for v in M.VERSOES:
            p1a = self._um(v, "M1", "coeficiente", B)
            self.assertTrue(bool(p1a["entra_holm"]))
            self.assertAlmostEqual(p1a["p_holm"], p1a["p"], delta=1e-15)
            self.assertEqual(M._verdadeiro(p1a["rejeita_h0_5pct"]), p1a["p_holm"] < 0.05)
            d = self._um(v, "M1", "D_UF")
            self.assertAlmostEqual(d["p_holm"], d["p_unilateral"], delta=1e-15)
            self.assertEqual(M._verdadeiro(d["rejeita_h0_5pct"]), d["p_holm"] < 0.05)
            for chave in ("E9_2", "E9_emp", "M5_1", "M5_2", "M5_3"):
                self.assertFalse(bool(self._um(v, chave, "coeficiente", B)["entra_holm"]))

    def test_leitura_refeita(self) -> None:
        lei = M.leitura(self.est)
        self.assertEqual(lei, self.resumo["leitura"])

    def test_mesma_amostra_e_ciclos_1_e_3_identicos(self) -> None:
        a = self.est[self.est["versao"] == M.ANTIGA].reset_index(drop=True)
        c = self.est[self.est["versao"] == M.CORRIGIDA].reset_index(drop=True)
        self.assertEqual(len(a), len(c))
        for col in ("chave_modelo", "tipo_linha", "termo", "n_candidatos", "n_alternativas_ou_linhas", "n_conjuntos"):
            self.assertTrue((a[col].fillna(-1) == c[col].fillna(-1)).all(), col)
        for chave in ("M5_1", "M5_3"):
            m = a["chave_modelo"] == chave
            np.testing.assert_array_equal(a.loc[m, "estimativa"].to_numpy(), c.loc[m, "estimativa"].to_numpy())
        for chave in ("E9_2", "E9_emp", "M1", "M5_2"):
            ta = self._um(M.ANTIGA, chave, "coeficiente", "tem_vaga_imediata")
            tc = self._um(M.CORRIGIDA, chave, "coeficiente", "tem_vaga_imediata")
            self.assertNotEqual(ta["estimativa"], tc["estimativa"], chave)
        n = {r.chave_modelo: r.n_candidatos for r in a[a["tipo_linha"] == "coeficiente"].itertuples()}
        self.assertEqual(n["E9_2"], 2140)
        self.assertEqual(n["E9_emp"], 5714)
        self.assertEqual(n["M1"], 5421)
        self.assertEqual(n["M5_2"], 2032)

    def test_correcao_contra_auditoria_36(self) -> None:
        """Contagens da correção refeitas da leitura independente da auditoria 36."""
        a = pd.read_csv(A36)
        a = a[a["ciclo"] == 2]
        cv = self.resumo["correcao"]
        self.assertEqual(cv["celulas_ciclo2_no_conjunto"], len(a))
        self.assertEqual(cv["celulas_sem_linha_no_quadro_1302"], 0)
        self.assertEqual(cv["celulas_sem_numero_de_vagas_imediatas_no_quadro_1302"], 0)
        self.assertEqual(cv["imputadas"], 0)
        self.assertEqual(cv["celulas_com_vaga_imediata_13fev"], int((a["vagas_imediatas_13fev"] > 0).sum()))
        self.assertEqual(cv["celulas_com_vaga_imediata_19mar"], int((a["vagas_imediatas_pipe_versao"] > 0).sum()))
        self.assertEqual(cv["vagas_imediatas_total_13fev"], float(a["vagas_imediatas_13fev"].sum()))
        self.assertEqual(cv["vagas_imediatas_total_19mar"], float(a["vagas_imediatas_pipe_versao"].sum()))
        conc = float(((a["vagas_imediatas_13fev"] > 0) == (a["vagas_imediatas_pipe_versao"] > 0)).mean())
        self.assertAlmostEqual(cv["concordancia_tem_vaga_imediata"], conc, places=12)
        self.assertEqual(cv["celulas_de_reserva_em_13fev_com_imediata_em_19mar"],
                         int(((a["vagas_imediatas_13fev"] == 0) & (a["vagas_imediatas_pipe_versao"] > 0)).sum()))
        self.assertEqual(self.resumo["conferencia_a36"]["celulas_com_vagas_imediatas_diferentes"], 0)
        self.assertEqual(self.resumo["correcao"]["datas"]["retificado_servicos"], "13/02/2026")

    def test_integridade(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", texto)
        for col in self.est.columns:
            self.assertNotRegex(col.lower(), r"cpf|nome|crm|id_candidato")
        corpo = CSV.read_text(encoding="utf-8").lower()
        for padrao in ("cpf", "c1_0", "c2_0", "c3_0"):
            self.assertNotIn(padrao, corpo)
        res_txt = RESUMO.read_text(encoding="utf-8")
        self.assertNotIn("id_candidato\":", res_txt)

    def test_figura_com_como_ler(self) -> None:
        self.assertTrue(FIG.exists())
        self.assertEqual(self.resumo["figura"]["sha256"], sha256(FIG))
        self.assertIn("Como ler", DOC.read_text(encoding="utf-8"))
        self.assertTrue(self.resumo["figura"]["como_ler"])


# ---------------------------------------------------------------------------
# 4. Doc 57p
# ---------------------------------------------------------------------------

class TestDoc57p(unittest.TestCase):
    def test_doc_igual_ao_gerado(self) -> None:
        gerado = M.gerar_doc(M.ler_est(), M.ler_resumo())
        self.assertEqual(DOC.read_text(encoding="utf-8"), gerado)

    def test_secoes_marcadores_e_linguagem(self) -> None:
        t = DOC.read_text(encoding="utf-8")
        for s in ("## 1. Resposta curta", "## 4. Tabelas", "## 5. Figura", "## 7. Limites"):
            self.assertIn(s, t)
        for nome in ("resposta", "portao", "correcao", "bolsa", "duf", "covariaveis", "figura", "desvios"):
            self.assertEqual(t.count(f"<!-- VC:{nome}:inicio -->"), 1, nome)
            self.assertEqual(t.count(f"<!-- VC:{nome}:fim -->"), 1, nome)
        self.assertIn("H2 (bolsa × origem)", t)
        self.assertIn("Sinal do ciclo 2", t)
        self.assertIn("pacote do corte", t)
        self.assertIn("não é efeito da participação no PMM-E", t.replace("\n", " ").replace("Não é", "não é"))
        self.assertNotIn("a bolsa funciona", t.lower())


if __name__ == "__main__":
    unittest.main()
