"""Testes do protocolo 60, parte A (script 36): equivalência no preenchimento (H1) por TOST.

- A conta do TOST é conferida em casos SINTÉTICOS construídos em memória (rotulados "sintético" aqui; nada vai para
  `output/`).
- As saídas `output/rdd_bolsa/EQ_*` são conferidas contra as estimativas gravadas pelos blocos (`N_estimativas.csv`,
  `NA_estimativas.csv`), recalculando o TOST e o Holm com código próprio.
- O doc 57j tem de ser igual ao que o script gera a partir de `output/`.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "rdd_bolsa"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "36_equivalencia_H1.py"
DOC = ROOT / "docs" / "06_execucao" / "57j_resultados_equivalencia_H1.md"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


EQ = _mod("eq36_teste", SCRIPT)
Z95 = stats.norm.ppf(0.95)


class TestTOSTSintetico(unittest.TestCase):
    """Casos sintéticos em memória: a conta do TOST contra a definição."""

    def test_sintetico_equivalencia(self):
        # sintético: τ̂ = 0,01, EP = 0,02, m = 0,10 -> IC 90% [−0,0229; +0,0429] dentro de ±0,10
        r = EQ.tost(0.01, 0.02, 0.10)
        self.assertAlmostEqual(r["ic90_inf"], 0.01 - Z95 * 0.02, places=12)
        self.assertAlmostEqual(r["ic90_sup"], 0.01 + Z95 * 0.02, places=12)
        self.assertAlmostEqual(r["p_aumento"], stats.norm.cdf((0.01 - 0.10) / 0.02), places=14)
        self.assertAlmostEqual(r["p_queda"], stats.norm.sf((0.01 + 0.10) / 0.02), places=14)
        self.assertEqual(r["p_tost"], max(r["p_aumento"], r["p_queda"]))
        self.assertLess(r["p_tost"], 0.05)
        self.assertAlmostEqual(r["margem_minima"], 0.01 + Z95 * 0.02, places=12)
        self.assertEqual(EQ.classificar(r["p_aumento"] < 0.05, r["p_queda"] < 0.05), "EQUIVALENTE")

    def test_sintetico_so_aumento_e_inconclusivo(self):
        # sintético: estimativa negativa grande -> só o teste do aumento rejeita
        r = EQ.tost(-0.08, 0.03, 0.10)
        self.assertLess(r["p_aumento"], 0.05)
        self.assertGreater(r["p_queda"], 0.05)
        self.assertEqual(EQ.classificar(r["p_aumento"] < 0.05, r["p_queda"] < 0.05), "SO_AUMENTO")
        # sintético: EP grande -> nenhum rejeita
        r = EQ.tost(0.0, 0.2, 0.10)
        self.assertGreater(r["p_aumento"], 0.05)
        self.assertGreater(r["p_queda"], 0.05)
        self.assertAlmostEqual(r["p_aumento"], r["p_queda"], places=14)  # simetria em τ̂ = 0
        self.assertEqual(EQ.classificar(False, False), "INCONCLUSIVO")
        self.assertEqual(EQ.classificar(False, True), "SO_QUEDA")

    def test_sintetico_dualidade_ic90(self):
        # sintético: cada teste rejeita a 5% sse a ponta do IC 90% fica dentro da margem
        rng = np.random.default_rng(20261026)
        for _ in range(500):
            tau, ep, m, b = rng.normal(0, 0.1), rng.uniform(0.005, 0.1), rng.uniform(0.01, 0.2), rng.uniform(0, 0.05)
            r = EQ.tost(tau, ep, m, b)
            if abs(r["ic90_sup"] - m) > 1e-9:
                self.assertEqual(r["p_aumento"] < 0.05, r["ic90_sup"] < m)
            if abs(r["ic90_inf"] + m) > 1e-9:
                self.assertEqual(r["p_queda"] < 0.05, r["ic90_inf"] > -m)
            self.assertAlmostEqual(r["margem_minima"], max(abs(r["ic90_inf"]), abs(r["ic90_sup"])), places=12)
            # na margem mínima, o TOST fica exatamente no limiar de 5%
            if r["margem_minima"] > 0:
                r2 = EQ.tost(tau, ep, r["margem_minima"], b)
                self.assertAlmostEqual(r2["p_tost"], 0.05, places=9)

    def test_sintetico_vies_honesto(self):
        # sintético: com viés máximo B, o teste é o do pior caso; B = 0 reproduz o convencional
        r0 = EQ.tost(0.02, 0.03, 0.10, 0.0)
        rb = EQ.tost(0.02, 0.03, 0.10, 0.04)
        self.assertAlmostEqual(rb["p_aumento"], stats.norm.cdf((0.02 - 0.10 + 0.04) / 0.03), places=14)
        self.assertAlmostEqual(rb["p_queda"], stats.norm.cdf((-0.10 - 0.02 + 0.04) / 0.03), places=14)
        self.assertGreater(rb["p_aumento"], r0["p_aumento"])
        self.assertGreater(rb["p_queda"], r0["p_queda"])
        self.assertAlmostEqual(rb["ic90_sup"] - r0["ic90_sup"], 0.04, places=12)
        # sintético: viés maior que a margem -> nenhum teste pode rejeitar a 5%, qualquer EP
        rg = EQ.tost(0.0, 1e-6, 0.10, 0.2)
        self.assertGreater(rg["p_aumento"], 0.5)
        self.assertGreater(rg["p_queda"], 0.5)

    def test_sintetico_cobertura_monte_carlo(self):
        # sintético: no limite da nula (salto = +m, sem viés), o teste do aumento rejeita ~5% das vezes
        rng = np.random.default_rng(7)
        ep, m = 0.04, 0.10
        taus = m + ep * rng.standard_normal(20000)
        rej = np.mean([EQ.tost(t, ep, m)["p_aumento"] < 0.05 for t in taus])
        self.assertAlmostEqual(rej, 0.05, delta=0.006)

    def test_entradas_invalidas(self):
        for args in ((0.0, 0.0, 0.1), (0.0, 0.1, 0.0), (float("nan"), 0.1, 0.1), (0.0, 0.1, 0.1, -1.0)):
            with self.assertRaises(ValueError):
                EQ.tost(*args)

    def test_conferencia_doc57_para_quando_diverge(self):
        # sintético: um doc 57 com um número trocado faz a conferência falhar (sem gravar nada)
        texto = (ROOT / "docs" / "06_execucao" / "57_sintese_perguntas_reformuladas.md").read_text(encoding="utf-8")
        ref = EQ.ler_doc57(texto)
        na = pd.read_csv(OUT / "NA_estimativas.csv", dtype={"ciclo": str, "corte": str})
        n = pd.read_csv(OUT / "N_estimativas.csv", dtype={"ciclo": str, "corte": str})
        sel = EQ.selecionar(na, n)
        EQ.conferir(sel, ref)  # o real passa
        ruim = {k: dict(v) for k, v in ref.items()}
        ruim["A3-emp-123"]["tau"] += 0.2
        with self.assertRaises(EQ.FalhaValidacao):
            EQ.conferir(sel, ruim)
        sem_media = n.copy()
        m = ((sem_media["outcome_id"] == "N1") & (sem_media["especificacao"] == "S-a")
             & (sem_media["variante"] == "principal") & (sem_media["populacao"] == "V1+V2+V3")
             & (sem_media["corte"] == "empilhado"))
        sem_media.loc[m, "media_abaixo"] = np.nan
        with self.assertRaises(EQ.FalhaValidacao):
            EQ.selecionar(na, sem_media)


def _existe(*nomes):
    return all((OUT / n).exists() for n in nomes)


@unittest.skipUnless(_existe("EQ_estimativas.csv", "EQ_resumo.json"), "saídas do EQ ainda não geradas")
class TestSaidasEQ(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.est = pd.read_csv(OUT / "EQ_estimativas.csv", dtype={"ciclo": str, "corte": str})
        cls.res = json.loads((OUT / "EQ_resumo.json").read_text(encoding="utf-8"))
        cls.na = pd.read_csv(OUT / "NA_estimativas.csv", dtype={"ciclo": str, "corte": str})
        cls.n = pd.read_csv(OUT / "N_estimativas.csv", dtype={"ciclo": str, "corte": str})
        cls.conv = cls.est[cls.est["tipo_ic"] == "convencional_CR1"].set_index("id_linha")

    def test_rotulos_estatuto_e_colunas(self):
        self.assertEqual(set(self.est["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(self.est["estatuto"]), {"PROTOCOLO_60_POS_RESULTADO"})
        self.assertEqual(self.res["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.res["estatuto"], "PROTOCOLO_60_POS_RESULTADO")
        self.assertEqual(list(self.est.columns), EQ.COLUNAS)

    def test_linhas_do_protocolo(self):
        self.assertEqual(list(self.conv.index), [x[0] for x in EQ.LINHAS])
        papeis = self.conv["papel"].value_counts().to_dict()
        self.assertEqual(papeis, {"primaria": 2, "secundaria": 7})
        self.assertEqual(sorted(self.conv[self.conv["papel"] == "primaria"].index), ["A3-emp-123", "N1-emp-123"])
        # IC honesto só onde o bloco o gravou: N1 (4 variantes × 3 linhas); A3 não tem
        hon = self.est[self.est["tipo_ic"] != "convencional_CR1"]
        self.assertEqual(set(hon["outcome"]), {"N1"})
        self.assertEqual(len(hon), 12)
        self.assertTrue(self.na[(self.na["outcome_id"] == "A3_PREENCHIDA") & (self.na["variante"] == "principal")]
                        ["ic_honesto_inf"].isna().all())

    def test_numeros_contra_os_blocos(self):
        for idl, r in self.conv.iterrows():
            if r["outcome"] == "A3":
                o = self.na[(self.na["outcome_id"] == "A3_PREENCHIDA") & (self.na["especificacao"] == "A3")
                            & (self.na["variante"] == "principal") & (self.na["populacao"] == r["populacao"])
                            & (self.na["ciclo"] == r["ciclo"]) & (self.na["corte"] == r["corte"])]
            else:
                o = self.n[(self.n["outcome_id"] == "N1") & (self.n["familia"] == "N") & (self.n["especificacao"] == "S-a")
                           & (self.n["variante"] == "principal") & (self.n["populacao"] == r["populacao"])
                           & (self.n["ciclo"] == r["ciclo"]) & (self.n["corte"] == r["corte"])]
            self.assertEqual(len(o), 1, idl)
            o = o.iloc[0]
            for c in ("tau", "ep", "media_abaixo", "ic95_inf", "ic95_sup"):
                self.assertAlmostEqual(r[c], o[c], delta=1e-9 * max(1, abs(o[c])), msg=f"{idl}.{c}")

    def test_margens(self):
        for idl, r in self.conv.iterrows():
            esperado = 0.10 if r["outcome"] == "A3" else 0.25 * r["media_abaixo"]
            self.assertAlmostEqual(r["margem"], esperado, places=9, msg=idl)

    def test_tost_recalculado(self):
        for _, r in self.est.iterrows():
            b = r["vies_max"]
            pa = stats.norm.cdf((r["tau"] - r["margem"] + b) / r["ep"])
            pq = stats.norm.cdf((-r["margem"] - r["tau"] + b) / r["ep"])
            self.assertAlmostEqual(r["p_aumento"], pa, delta=1e-9)
            self.assertAlmostEqual(r["p_queda"], pq, delta=1e-9)
            self.assertAlmostEqual(r["p_tost"], max(pa, pq), delta=1e-9)
            tol = 1e-9 * max(1.0, abs(r["ic90_inf"]), abs(r["ic90_sup"]))  # CSV com 10 algarismos significativos
            self.assertAlmostEqual(r["ic90_inf"], r["tau"] - b - Z95 * r["ep"], delta=tol)
            self.assertAlmostEqual(r["ic90_sup"], r["tau"] + b + Z95 * r["ep"], delta=tol)
            self.assertAlmostEqual(r["margem_minima"], abs(r["tau"]) + b + Z95 * r["ep"], delta=tol)
        self.assertTrue((self.conv["vies_max"] == 0).all())

    def test_holm_so_nas_primarias(self):
        prim = self.est[self.est["entra_holm"]]
        self.assertEqual(sorted(prim["id_linha"]), ["A3-emp-123", "N1-emp-123"])
        self.assertTrue((prim["tipo_ic"] == "convencional_CR1").all())
        for c in ("aumento", "queda", "tost"):
            p = prim[f"p_{c}"].to_numpy()
            o = np.argsort(p)
            adj = np.empty(2)
            adj[o[0]] = min(1, 2 * p[o[0]])
            adj[o[1]] = min(1, max(adj[o[0]], p[o[1]]))
            np.testing.assert_allclose(prim[f"p_holm_{c}"].to_numpy(), adj, atol=1e-12)
        self.assertTrue(self.est.loc[~self.est["entra_holm"], ["p_holm_aumento", "p_holm_queda", "p_holm_tost"]]
                        .isna().all().all())

    def test_decisoes_e_leitura(self):
        for _, r in self.est.iterrows():
            pa = r["p_holm_aumento"] if r["entra_holm"] else r["p_aumento"]
            pq = r["p_holm_queda"] if r["entra_holm"] else r["p_queda"]
            self.assertEqual(bool(r["rejeita_aumento"]), pa < 0.05)
            self.assertEqual(bool(r["rejeita_queda"]), pq < 0.05)
            self.assertEqual(bool(r["equivalente"]), bool(r["rejeita_aumento"] and r["rejeita_queda"]))
            self.assertEqual(r["leitura_codigo"], EQ.classificar(bool(r["rejeita_aumento"]), bool(r["rejeita_queda"])))
            if r["entra_holm"]:
                self.assertEqual(bool(r["equivalente"]), r["p_holm_tost"] < 0.05)
            # equivalência só se os dois testes rejeitam; e então o IC 90% cabe na margem
            if r["equivalente"]:
                self.assertTrue(-r["margem"] < r["ic90_inf"] and r["ic90_sup"] < r["margem"])

    def test_resultados_das_primarias_no_resumo(self):
        for idl, d in self.res["primarias"].items():
            r = self.conv.loc[idl]
            for k in ("tau", "ep", "ic90_inf", "ic90_sup", "p_aumento", "p_queda", "p_holm_tost", "margem_minima"):
                self.assertAlmostEqual(d[k], r[k], delta=1e-9, msg=f"{idl}.{k}")
            self.assertEqual(d["leitura_codigo"], r["leitura_codigo"])

    def test_hashes(self):
        import hashlib

        def h(p):
            return hashlib.sha256(p.read_bytes()).hexdigest()

        for e in self.res["entradas"]:
            self.assertEqual(h(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        for k, v in self.res["saidas"].items():
            self.assertEqual(h(ROOT / k), v, k)
        for f in self.res["figuras"]:
            self.assertEqual(h(ROOT / f["arquivo"]), f["sha256"], f["arquivo"])
        self.assertEqual(self.res["protocolo"]["sha256_texto_congelado"], EQ.SHA_PROTOCOLO_CONGELADO)
        self.assertIn("60_protocolo_equivalencia_e_oferta_local.md", self.res["protocolo"]["texto"])
        papeis = {e["caminho"] for e in self.res["entradas"]}
        self.assertTrue({"output/rdd_bolsa/NA_estimativas.csv", "output/rdd_bolsa/N_estimativas.csv"} <= papeis)

    def test_conferencia_doc57_registrada(self):
        itens = self.res["conferencia"]["doc57"]
        self.assertTrue(all(i["confere"] for i in itens))
        self.assertEqual({i["linha"] for i in itens}, set(EQ.CHAVES_57.values()) | {"N1-emp-123"})


class TestIntegridadeScript(unittest.TestCase):
    def test_nao_le_ivs_errado_nem_cnes_nem_data(self):
        txt = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", txt)
        self.assertNotIn('"data"', txt)
        self.assertIsNone(re.search(r"20260(9|[1-9]\d)|2027\d\d", txt))
        self.assertNotIn("a09_", txt)

    def test_nao_regrava_saidas_anteriores(self):
        txt = SCRIPT.read_text(encoding="utf-8")
        for nome in ("NA_estimativas", "N_estimativas"):
            self.assertNotRegex(txt, rf"{nome}\.csv\"?\)?\.to_csv|to_csv\([^)]*{nome}")


@unittest.skipUnless(DOC.exists() and _existe("EQ_estimativas.csv", "EQ_resumo.json"), "doc 57j ainda não gerado")
class TestDoc57j(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texto = DOC.read_text(encoding="utf-8")

    def test_doc_igual_ao_gerado(self):
        est, res = EQ.ler_saidas()
        self.assertEqual(self.texto, EQ.gerar_doc(est, res), "doc 57j diferente do gerado: rode o script 36 "
                                                             "com --atualizar-doc")

    def test_secoes_e_marcadores(self):
        for s in ("## 1. O que se testa", "## 2. Tabela", "## 3. Leitura em linguagem simples", "## 4. Figura",
                  "**Como ler.**", "## 5. Limites"):
            self.assertIn(s, self.texto)
        for nome in ("primarias", "secundarias", "honesto", "leitura", "conferencia", "proveniencia"):
            self.assertIn(f"<!-- EQ:{nome}:inicio -->", self.texto)
            self.assertIn(f"<!-- EQ:{nome}:fim -->", self.texto)
        for limite in ("Pacote do corte", "Aproximação local linear", "Pós-resultado"):
            self.assertIn(limite, self.texto)
        self.assertIn("EQ_figuras/EQ_tost_ic90.png", self.texto)

    def test_linguagem(self):
        leitura = re.search(r"<!-- EQ:leitura:inicio -->(.*?)<!-- EQ:leitura:fim -->", self.texto, re.S).group(1)
        self.assertNotRegex(leitura.lower(), r"a bolsa não funciona|a bolsa funciona\b|não tem efeito")
        self.assertNotIn("efeito da bolsa", leitura.lower())
        est = pd.read_csv(OUT / "EQ_estimativas.csv")
        if not est["equivalente"].any():
            self.assertNotRegex(leitura, r"os dois testes rejeitam")
        if (est["leitura_codigo"] == "SO_AUMENTO").any():
            self.assertIn("não houve aumento de", leitura)

    def test_numeros_das_primarias_no_doc(self):
        est = pd.read_csv(OUT / "EQ_estimativas.csv").set_index("id_linha")
        a3 = est[(est.index == "A3-emp-123") & (est["tipo_ic"] == "convencional_CR1")].iloc[0]
        self.assertIn(f"[{EQ._n(100 * a3['ic90_inf'], 1)}; {EQ._n(100 * a3['ic90_sup'], 1)}]", self.texto)
        n1 = est[(est.index == "N1-emp-123") & (est["tipo_ic"] == "convencional_CR1")].iloc[0]
        self.assertIn(f"[{EQ._n(n1['ic90_inf'], 2)}; {EQ._n(n1['ic90_sup'], 2)}]", self.texto)


if __name__ == "__main__":
    unittest.main()
