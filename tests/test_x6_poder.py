"""Testes do X6 (`scripts/rdd_bolsa/20_poder_descartes.py`): poder, MDE, TOST e descartes.

Três partes:

1. `TestFormulasSintetico`: MDE, TOST, base empilhada e posição da referência
   com números SINTÉTICOS fixados em memória (não são resultados; nada é gravado
   em `output/` nem em `data/`).
2. `TestX6SaidasReais`: `output/rdd_bolsa/X6_*` contra os CSV do E6, E7 e E9 e o
   resumo do E8. Os alvos são lidos desses arquivos e recalculados aqui, sem
   digitar número; os trechos da literatura são procurados no doc 20.
3. `TestDoc46X6`: os blocos da seção X6 do doc 46 são idênticos aos gerados das
   saídas do X6, e a prosa fora deles só tem parâmetros.
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
from statistics import NormalDist

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "20_poder_descartes.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("x6_poder_20", SCRIPT)
X6 = importlib.util.module_from_spec(_spec)
sys.modules["x6_poder_20"] = X6
_spec.loader.exec_module(X6)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
CSV = OUT / "X6_poder_descartes.csv"
RESUMO = OUT / "X6_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "46_resultados_exploratorios_pos_sintese.md"
TEM_SAIDAS = CSV.exists() and RESUMO.exists()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# 1. Fórmulas com números sintéticos
# --------------------------------------------------------------------------

class TestFormulasSintetico(unittest.TestCase):
    """MDE, TOST e bases com valores sintéticos fixados aqui (não são resultados)."""

    EPS_SINTETICOS = (0.01, 0.054, 0.3, 2.0)
    TAUS_SINTETICOS = (-0.2, -0.01, 0.0, 0.05, 0.4)

    def test_mde_e_2_8_ep_e_tem_cerca_de_80_de_poder(self) -> None:
        for ep in self.EPS_SINTETICOS:
            self.assertAlmostEqual(X6.mde(ep), 2.8 * ep, places=12)
            # 2,8 ≈ z_0,975 + z_0,80: poder bicaudal a 5% contra o MDE fica em 80% (± arredondamento do 2,8)
            self.assertAlmostEqual(X6.poder_bicaudal(X6.mde(ep), ep), 0.80, delta=0.002)
        nd = NormalDist()
        self.assertAlmostEqual(nd.inv_cdf(0.975) + nd.inv_cdf(0.80), 2.8, delta=0.002)

    def test_delta_tost_e_o_menor_delta_com_ic90_dentro(self) -> None:
        z90 = NormalDist().inv_cdf(0.95)
        for tau in self.TAUS_SINTETICOS:
            for ep in self.EPS_SINTETICOS:
                d = X6.delta_tost(tau, ep)
                self.assertAlmostEqual(d, abs(tau) + z90 * ep, places=12)
                a, b = X6.ic90(tau, ep)
                self.assertTrue(-d - 1e-12 <= a and b <= d + 1e-12)
                # no δ mínimo, o p do TOST é exatamente 5%; acima, menor; abaixo, maior
                self.assertAlmostEqual(X6.p_tost(tau, ep, d), 0.05, places=9)
                self.assertLess(X6.p_tost(tau, ep, d * 1.01 + 1e-9), 0.05)
                self.assertGreater(X6.p_tost(tau, ep, d * 0.99), 0.05)

    def test_base_empilhada_ponderada(self) -> None:
        pesos = {"300": 0.25, "400": 0.75}
        self.assertAlmostEqual(X6.base_empilhada(pesos, {"300": 2.0, "400": 6.0}), 5.0, places=12)
        self.assertTrue(math.isnan(X6.base_empilhada(pesos, {"300": 2.0})))
        with self.assertRaises(X6.FalhaFechada):
            X6.base_empilhada({"300": 0.5, "400": 0.6}, {"300": 1.0, "400": 1.0})

    def test_arco_de_ponto_medio_sintetico(self) -> None:
        """Elasticidade-arco de ponto médio com bolsas e probabilidades sintéticas."""
        b0, b1, p0, p1 = 10.0, 15.0, 0.02, 0.03          # sintéticos
        r = p1 / p0 - 1
        arco = ((p1 - p0) / ((p0 + p1) / 2)) / ((b1 - b0) / ((b0 + b1) / 2))
        self.assertAlmostEqual((r / (1 + r / 2)) / ((b1 - b0) / ((b0 + b1) / 2)), arco, places=12)
        self.assertAlmostEqual(arco, 1.0, places=12)       # +50% em P e B: arco = 1 por construção
        self.assertAlmostEqual(r / ((b1 - b0) / b0), 1.0, places=12)

    def test_posicao_da_referencia(self) -> None:
        self.assertEqual(X6.posicao(-0.2, 0.05, 0.10, 0.10), "IC_ABAIXO_DA_REFERENCIA")
        self.assertEqual(X6.posicao(0.8, 2.9, 0.4, 0.7), "IC_ACIMA_DA_REFERENCIA")
        self.assertEqual(X6.posicao(-0.2, 0.5, 0.4, 0.7), "IC_CONTEM_REFERENCIA")
        self.assertEqual(X6.posicao(float("nan"), 0.5, 0.4, 0.7), "NAO_AVALIAVEL")

    def test_linha_sintetica_relativa_e_referencia(self) -> None:
        meta = {"natureza_dos_dados": "sintetico_teste"}
        ref = {"nome": "ref (protocolo 40, §7)", "valor": 0.10, "escala": "fracao (absoluta)", "coluna": "abs"}
        r = X6.linha(meta, -0.05, 0.02, (-0.05 - X6.Z95 * 0.02, -0.05 + X6.Z95 * 0.02), 0.01, (-1.2, 1.1), 0.4,
                     "sintetica", "base", ref, [], "abs", True)
        self.assertAlmostEqual(r["mde80_rel"], 2.8 * 0.02 / 0.4, places=12)
        self.assertAlmostEqual(r["ic95_sup_rel"], (-0.05 + X6.Z95 * 0.02) / 0.4, places=12)
        self.assertTrue(r["ic95_exclui_ref_protocolo"])
        self.assertTrue(r["mde80_abaixo_ref_protocolo"])
        self.assertTrue(r["ic_honesto_cobre_todo_salto_possivel"])
        self.assertFalse(r["ic_honesto_informativo"])
        # escala log (Poisson): relativo = exp(.) - 1
        r = X6.linha(meta, 0.1, 0.3, (0.1 - X6.Z95 * 0.3, 0.1 + X6.Z95 * 0.3), 0.7, (float("nan"),) * 2,
                     float("nan"), "log", "log", None, [], "rel", False)
        self.assertAlmostEqual(r["mde80_rel"], math.exp(2.8 * 0.3) - 1, places=12)
        self.assertIsNone(r["ic_honesto_informativo"])


# --------------------------------------------------------------------------
# 2. Saídas reais
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS, "saidas do X6 ausentes")
class TestX6SaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tab = pd.read_csv(CSV, dtype={"ciclo": str, "corte": str})
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        cls.e6 = pd.read_csv(OUT / "E6_estimativas.csv", dtype={"ciclo": str, "corte": str})
        cls.e7 = pd.read_csv(OUT / "E7_estimativas.csv", dtype={"corte": str})
        cls.e9 = pd.read_csv(OUT / "E9_estimativas.csv", dtype={"ciclo": str})
        cls.efm = pd.read_csv(OUT / "E9_efeitos_marginais.csv", dtype={"ciclo": str})
        cls.e8 = json.loads((OUT / "E8_resumo.json").read_text(encoding="utf-8"))

    def test_adicionais_ao_doc45_rotulados(self) -> None:
        self.assertTrue(self.tab["especificacao_adicional_doc45"].str.startswith("ESPECIFICACAO_ADICIONAL").all())
        for c in ("delta_tost", "ic90_inf", "ic_honesto_informativo"):
            self.assertTrue(self.tab["especificacao_adicional_doc45"].str.contains(c).all(), c)
        el = self.tab[self.tab["quantidade"].astype(str).str.startswith("elasticidade_")]
        self.assertEqual(len(el), 4 * 2 * 2)  # 4 ciclos x 2 cortes x 2 versões (estrutura)
        self.assertTrue(el["especificacao_adicional_doc45"].str.contains("linha inteira").all())
        self.assertEqual(self.resumo["adicionais_ao_doc45"]["rotulo"], "ESPECIFICACAO_ADICIONAL")

    def test_rotulos(self) -> None:
        self.assertEqual(set(self.tab["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(self.tab["estatuto"]), {"EXPLORATORIO_POS_SINTESE"})
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "EXPLORATORIO_POS_SINTESE")

    def test_hashes_das_entradas_e_saidas(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(e["sha256"], sha256(ROOT / e["caminho"]), e["caminho"])
            for k in ("fonte", "data_referencia", "cobertura", "unidade", "chaves", "filtros"):
                self.assertTrue(e[k], f"{e['caminho']}: {k}")
        for s in self.resumo["saidas"].values():
            self.assertEqual(s["sha256"], sha256(ROOT / s["caminho"]))

    def test_cobertura_das_linhas(self) -> None:
        e6 = self.e6
        n6 = int(((e6["especificacao"] == "principal") & e6["familia"].isin(["P1", "F0", "F1", "F2", "F4"])).sum()
                 + ((e6["especificacao"] == "poisson_local") & (e6["outcome_id"] == "F1.1")).sum())
        n7 = int(((self.e7["especificacao"] == "principal")
                  & self.e7["outcome_id"].isin(["F3.1", "F3.2", "F3.3", "F3.P1", "F3.P2"])).sum())
        cont = self.tab["etapa_origem"].value_counts()
        self.assertEqual(int(cont["E6"]), n6)
        self.assertEqual(int(cont["E7"]), n7)
        self.assertEqual(int(cont["E9"]), 4 * 9)  # 4 ciclos x 9 quantidades (estrutura, não resultado)
        self.assertEqual(self.resumo["contagens"]["linhas"], len(self.tab))

    def test_copia_e_formulas_e6_e7(self) -> None:
        z90 = NormalDist().inv_cdf(0.95)
        for et, fonte, chave in (("E6", self.e6, ["outcome", "populacao", "ciclo", "corte", "especificacao"]),
                                 ("E7", self.e7, ["outcome", "populacao", "corte", "especificacao"])):
            t = self.tab[self.tab["etapa_origem"] == et]
            fonte = fonte[fonte["especificacao"].isin(["principal", "poisson_local"])]
            m = t.merge(fonte, on=chave, suffixes=("", "_src"), validate="one_to_one")
            self.assertEqual(len(m), len(t))
            for c in ("tau", "ep", "ic95_inf", "ic95_sup", "ic_honesto_inf", "ic_honesto_sup"):
                np.testing.assert_allclose(m[c], m[f"{c}_src"], rtol=1e-12, atol=1e-12, equal_nan=True, err_msg=c)
            np.testing.assert_allclose(m["mde80"], 2.8 * m["ep"], rtol=1e-12)
            np.testing.assert_allclose(m["delta_tost"], m["tau"].abs() + z90 * m["ep"], rtol=1e-12)

    def test_bases_relativas(self) -> None:
        t = self.tab
        # E6, linha por grupo: base = media_bruta_abaixo da própria linha
        g = t[(t["etapa_origem"] == "E6") & (t["corte"] != "empilhado") & ~t["ciclo"].str.contains(r"\+")
              & (t["especificacao"] == "principal") & (t["familia"] != "P1")]
        m = g.merge(self.e6, on=["outcome", "populacao", "ciclo", "corte", "especificacao"], suffixes=("", "_s"))
        np.testing.assert_allclose(m["base_relativa"], m["media_bruta_abaixo"], rtol=1e-12)
        # E6, F1.3 empilhado em ciclos e cortes: recalculado aqui a partir dos pesos e das linhas V1..V3
        r = t[(t["outcome_id"] == "F1.3") & (t["populacao"] == "V1+V2+V3") & (t["corte"] == "empilhado")].iloc[0]
        src = self.e6[(self.e6["outcome_id"] == "F1.3") & (self.e6["populacao"] == "V1+V2+V3")
                      & (self.e6["corte"] == "empilhado") & (self.e6["especificacao"] == "principal")].iloc[0]
        base = 0.0
        for gk, w in json.loads(src["pesos_grupos"]).items():
            k, c = gk[1], "0." + gk.split("_")[1]
            mb = self.e6[(self.e6["outcome_id"] == "F1.3") & (self.e6["populacao"] == f"V{k}")
                         & (self.e6["corte"] == c) & (self.e6["especificacao"] == "principal")]["media_bruta_abaixo"]
            base += w * float(mb.iloc[0])
        self.assertAlmostEqual(r["base_relativa"], base, places=12)
        self.assertAlmostEqual(r["ic95_sup_rel"], r["ic95_sup"] / base, places=12)
        # E7, F3.1 em U por corte: base = nivel_pre
        for c in ("0.300", "0.400"):
            r = t[(t["etapa_origem"] == "E7") & (t["outcome_id"] == "F3.1") & (t["populacao"] == "U")
                  & (t["corte"] == c)].iloc[0]
            pre = self.e7[(self.e7["outcome_id"] == "F3.1") & (self.e7["populacao"] == "U") & (self.e7["corte"] == c)
                          & (self.e7["especificacao"] == "nivel_pre")]["media_bruta_abaixo"].iloc[0]
            self.assertAlmostEqual(r["base_relativa"], float(pre), places=12)
        self.assertEqual(self.resumo["contagens"]["bases_indisponiveis"],
                         int(t["base_relativa_tipo"].astype(str).str.startswith("INDISPONIVEL").sum()))

    def test_e9(self) -> None:
        t = self.tab[self.tab["etapa_origem"] == "E9"]
        b = self.e9[(self.e9["modelo"] == "logit_condicional_1a_opcao") & (self.e9["conjunto"] == "principal")
                    & (self.e9["termo"] == "bolsa_mil") & (self.e9["especificacao"] == "spline_linear__bolsa_linear")]
        q = self.efm[(self.efm["modelo"] == "logit_condicional_1a_opcao") & (self.efm["conjunto"] == "principal")
                     & (self.efm["termo"] == "bolsa_mil") & (self.efm["especificacao"] == "spline_linear__bolsa_linear")]
        for cic in ("1", "2", "3", "empilhado"):
            src = b[b["ciclo"] == cic].iloc[0]
            r = t[(t["ciclo"] == cic) & (t["quantidade"] == "coef_por_mil")].iloc[0]
            self.assertAlmostEqual(r["tau"], src["coef"], places=12)
            self.assertAlmostEqual(r["mde80"], 2.8 * src["ep_cluster_conjunto"], places=12)
            lo = q[(q["ciclo"] == cic) & (q["quantidade"] == "log_razao_chances_por_5mil")].iloc[0]
            rc = t[(t["ciclo"] == cic) & (t["quantidade"] == "razao_chances_por_5mil")].iloc[0]
            self.assertAlmostEqual(rc["mde80"], math.exp(2.8 * lo["ep_cluster_conjunto"]), places=12)
            dp = q[(q["ciclo"] == cic) & (q["quantidade"] == "variacao_prob_media_pp")].iloc[0]
            vs = q[(q["ciclo"] == cic) & (q["quantidade"] == "variacao_media_sobre_prob_media")].iloc[0]
            r = t[(t["ciclo"] == cic) & (t["quantidade"] == "variacao_prob_media_pp")].iloc[0]
            self.assertAlmostEqual(r["tau"], dp["estimativa"], places=12)
            self.assertAlmostEqual(r["tau_rel"], vs["estimativa"], places=9)  # Δ prob. / prob. base = coluna do E9
            vr = q[(q["ciclo"] == cic) & (q["quantidade"] == "variacao_relativa_media")].iloc[0]
            for c in ("0.300", "0.400"):
                d = self.e8["degrau_relativo_bolsa"][c]
                b0, b1 = float(d["de_mil"]), float(d["para_mil"])
                r = t[(t["ciclo"] == cic) & (t["quantidade"] == f"elasticidade_base_bolsa_menor_degrau_{c}")].iloc[0]
                self.assertAlmostEqual(r["tau"], vr["estimativa"] / ((b1 - b0) / b0), places=12)
                self.assertAlmostEqual(r["ic95_sup"], vr["ic95_sup"] / ((b1 - b0) / b0), places=12)
                # arco de ponto médio, recalculado aqui: (ΔP / P_médio) / (ΔB / B_médio)
                q_ = vr["estimativa"]
                arco = (q_ / (1 + q_ / 2)) / ((b1 - b0) / ((b0 + b1) / 2))
                r = t[(t["ciclo"] == cic) & (t["quantidade"] == f"elasticidade_arco_ponto_medio_degrau_{c}")].iloc[0]
                self.assertAlmostEqual(r["tau"], arco, places=12)
                self.assertTrue(r["ic95_inf"] < r["tau"] < r["ic95_sup"])
                self.assertIn("linha inteira", r["especificacao_adicional_doc45"])

    def test_referencias_do_protocolo(self) -> None:
        t = self.tab
        r = t[t["ref_protocolo"].astype(str).str.contains(r"\(protocolo 40", regex=True)]
        self.assertEqual(set(r["outcome_id"]), {"F1.1", "F1.3", "F1.4"})
        fill = r[r["outcome_id"] != "F1.1"]
        self.assertTrue(((fill["ic95_sup"] < fill["ref_protocolo_valor"]) == fill["ic95_exclui_ref_protocolo"]).all())
        self.assertTrue(((fill["mde80"] < fill["ref_protocolo_valor"]) == fill["mde80_abaixo_ref_protocolo"]).all())
        cand = r[r["outcome_id"] == "F1.1"]
        self.assertTrue(((cand["ic95_sup_rel"] < cand["ref_protocolo_valor"])
                         == cand["ic95_exclui_ref_protocolo"]).all())
        c = self.resumo["contagens"]
        self.assertEqual(c["com_referencia_do_protocolo"], len(r))
        self.assertEqual(c["ic95_exclui_ref_protocolo"], int(r["ic95_exclui_ref_protocolo"].sum()))
        self.assertEqual(c["mde80_abaixo_ref_protocolo"], int(r["mde80_abaixo_ref_protocolo"].sum()))

    def test_literatura_copiada_da_fonte(self) -> None:
        texto = (ROOT / "docs" / "03_literatura_empirica"
                 / "20_evidencia_empirica_hipotese_remuneracao_preenchimento.md").read_text(encoding="utf-8")
        for x in self.resumo["literatura"]:
            self.assertIn(x["trecho"], texto)
            m = re.search(x["regex"], x["trecho"])
            brutos = [float(g.replace(",", ".")) for g in m.groups()]
            self.assertEqual(brutos, x["valores_no_trecho"])
            self.assertAlmostEqual(x["valor_inf"], min(brutos) * x["fator_escala"], places=12)
            self.assertAlmostEqual(x["valor_sup"], max(brutos) * x["fator_escala"], places=12)


# --------------------------------------------------------------------------
# 3. Doc 46, seção X6
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS and DOC.exists(), "saidas do X6 ou doc 46 ausentes")
class TestDoc46X6(unittest.TestCase):
    def test_blocos_iguais_aos_gerados(self) -> None:
        resumo, tab = X6.ler_saidas()
        gerados = X6.blocos_doc(resumo, tab)
        no_doc = X6.blocos_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertEqual(set(no_doc), set(gerados))
        for k, v in gerados.items():
            self.assertEqual(no_doc[k], v, f"bloco {k} da secao X6 difere das saidas")

    def test_secao_igual_ao_modelo(self) -> None:
        sec = X6.secao_x6(DOC.read_text(encoding="utf-8"))
        self.assertEqual(X6.MARCA.sub(lambda m: m.group(1) + m.group(4), sec).rstrip("\n"),
                         X6.MARCA.sub(lambda m: m.group(1) + m.group(4), X6.SECAO_X6).rstrip("\n"))

    def test_prosa_sem_numero_de_resultado(self) -> None:
        texto = X6.MARCA.sub("", X6.secao_x6(DOC.read_text(encoding="utf-8")))
        texto = re.sub(r"`[^`]*`", "", texto).replace("SHA-256", "")
        texto = re.sub(r"\]\([^)]*\)", "]", texto)
        texto = re.sub(r"(?m)^#+ .*$", "", texto)
        texto = re.sub(r"§+\s?\d+", "", texto)
        texto = re.sub(r"\b\d{2}/\d{2}/\d{4}\b", "", texto)
        texto = re.sub(r"\b(?:docs?|protocolo|seção)\s+\d+\b", "", texto)
        texto = re.sub(r"\b[A-Za-z_]+\d+(?:\.\d+)?\b", "", texto)            # F1.3, E9, X6, P2
        texto = re.sub(r"\d+ª", "", texto)
        texto = re.sub(r"[A-Z]\d+[–-][A-Z]\d+", "", texto)
        decimais = set(re.findall(r"(?<![\w.,])[−+-]?\d+[,.]\d+", texto))
        self.assertEqual(decimais - {"2,8"}, set())                       # fator do MDE
        texto = re.sub(r"(?<![\w.,])[−+-]?\d+[,.]\d+", "", texto)
        inteiros = set(re.findall(r"(?<![\w.,])[−+-]?\d+(?![\w.,]\d)", texto))
        permitidos = {"80", "5", "95", "90", "100", "+10", "+25"}          # poder, alfa, IC, ±100% da base, referências
        anos = {x for x in inteiros if x.isdigit() and 2000 <= int(x) <= 2030}
        self.assertEqual(inteiros - permitidos - anos, set())

    def test_contraste_dito(self) -> None:
        corrido = " ".join(X6.secao_x6(DOC.read_text(encoding="utf-8")).split())
        self.assertIn("Nenhum é efeito da participação no PMM-E nem do Agora Tem Especialistas", corrido)
        self.assertIn("EXPLORATORIO_POS_SINTESE", corrido)


if __name__ == "__main__":
    unittest.main()
