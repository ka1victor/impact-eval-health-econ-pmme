"""Testes do adendo 48g (script 47): heterogeneidade do salto pelo porte em que o estrato do IED muda (PO-1 a PO-5).

- Esquema, `natureza_dos_dados = EMPIRICO` e estatuto `ADENDO_48G_POS_RESULTADO` em todas as saídas `PO_*`.
- G lido do a10: a regra refeita do JSON é a gravada e bate com o texto do adendo (portes 2 e 3 em 0,300; 1, 2 e 4 em
  0,400); o script não digita os portes.
- Portão: HI-1, HI-2 e OC-A1 em 0,300 reproduzidos (<= 1e-8), conferidos de novo contra `HI_` e `OC_`.
- Holm (4) e BKY (6) recalculados; IC e p recalculados do EP; τ₀ + τ₁ = soma; contagens e status coerentes.
- ΔB5 refeito com dados reais: com retas próprias por grupo, τ₀ e τ₀ + τ₁ são os saltos locais lineares de cada grupo.
- Integridade: IVS oficial, nenhum CNES >= 202609, nada escrito em `data/`, `HI_`, `OC_`, `CL_`, `PM_` não regravados.
- Leitura do §4 refeita das saídas; doc 57u: blocos iguais aos gerados, decisões antes dos resultados, linguagem.
- Casos SINTÉTICOS em memória (rotulados "sintético"; nada é gravado): recuperação exata de τ₀ e τ₁ sem ruído e
  identidade com os saltos por grupo.
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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "rdd_bolsa"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "47_heterogeneidade_porte_ied.py"
DOC = ROOT / "docs" / "06_execucao" / "57u_resultados_heterogeneidade_porte.md"
ADENDO = ROOT / "docs" / "06_execucao" / "48g_adendo_heterogeneidade_porte_ied.md"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


PO = _mod("po47_teste", SCRIPT)
EST, CO, RES = PO.ler_saidas()
T1 = EST[EST["termo"] == "tau1_diferenca"]


class TestEsquemaENatureza(unittest.TestCase):
    def test_colunas(self):
        self.assertEqual(list(EST.columns), PO.COLUNAS)
        self.assertEqual(list(CO.columns), PO.COLUNAS_CONT)

    def test_natureza_e_estatuto(self):
        for df in (EST, CO):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"ADENDO_48G_POS_RESULTADO"})
        self.assertEqual(RES["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(RES["estatuto"], "ADENDO_48G_POS_RESULTADO")

    def test_linhas_do_adendo(self):
        self.assertEqual(len(EST), 5 * 2 * 3)
        self.assertFalse(EST["id_linha"].duplicated().any())
        self.assertEqual(sorted(T1["id_po"].value_counts().items()), [("PO-1", 4), ("PO-2", 4), ("PO-3", 2)])
        self.assertEqual(set(EST.loc[EST["termo"] != "tau1_diferenca", "id_po"]), {"PO-4"})
        self.assertEqual(set(T1.loc[T1["id_po"] == "PO-3", "outcome"]), {"B5"})
        # Contagens: 5 outcomes × 2 cortes × 2 grupos × 2 lados; balanço: 2 populações × 2 cortes × 4.
        self.assertEqual(int((CO["tipo"] == "amostra").sum()), 40)
        self.assertEqual(int((CO["tipo"] == "balanco").sum()), 16)

    def test_figura_com_como_ler(self):
        f = RES["figura"]
        self.assertTrue((ROOT / f["arquivo"]).exists())
        self.assertEqual(PO.sha256(ROOT / f["arquivo"]), f["sha256"])
        self.assertTrue(f["como_ler"].startswith("Como ler"))


class TestRegraG(unittest.TestCase):
    def test_regra_refeita_igual_a_gravada(self):
        r = json.loads(json.dumps(PO._nan_none(PO.regra_g())))
        self.assertEqual(r, RES["regra_g"])

    def test_bate_com_o_texto_do_adendo(self):
        # Conferência no teste (o script lê do JSON do a10): adendo §1 e auditoria 18, §2.5.
        c = RES["regra_g"]["cortes"]
        self.assertEqual(c["0.300"]["portes_G1"], [2, 3])
        self.assertEqual(c["0.300"]["portes_G0"], [1, 4])
        self.assertEqual(c["0.400"]["portes_G1"], [1, 2, 4])
        self.assertEqual(c["0.400"]["portes_G0"], [3])
        txt = ADENDO.read_text(encoding="utf-8")
        self.assertIn("em **0,300**: muda nos portes **2 e 3**", txt)
        self.assertIn("em **0,400**: muda nos portes **1, 2 e 4**", txt)
        for _, r in EST.iterrows():
            self.assertEqual(r["portes_G1"], ";".join(str(p) for p in c[r["corte"]]["portes_G1"]))

    def test_script_nao_digita_os_portes(self):
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotRegex(src, r"\{\s*2\s*,\s*3\s*\}|\[\s*2\s*,\s*3\s*\]|\{\s*1\s*,\s*2\s*,\s*4\s*\}|\[\s*1\s*,\s*2\s*,\s*4\s*\]")
        self.assertIn("estrato_ied_por_codigo_ivs_e_porte", src)

    def test_estrato_do_csv_igual_a_regra(self):
        a10 = PO.ler_a10(PO.regra_g())
        self.assertEqual(len(a10), 5570)
        self.assertTrue(RES["portao"]["g_lido_do_a10"]["estrato_do_csv_igual_a_regra"])
        for v in RES["portao"]["g_lido_do_a10"]["codigo_do_anexo_vi_na_janela"].values():
            self.assertEqual(v["divergentes"], 0)
            self.assertGreater(v["conferidos"], 0)


class TestPortao(unittest.TestCase):
    def test_aprovado_e_contra_as_saidas_de_base(self):
        p = RES["portao"]
        self.assertTrue(p["aprovado"])
        self.assertLessEqual(p["max_abs_dif"], 1e-8)
        self.assertEqual(len(p["linhas"]), 6)
        hi = pd.read_csv(OUT / "HI_estimativas.csv", dtype={"corte": str})
        oc = pd.read_csv(OUT / "OC_estimativas.csv", dtype={"corte": str, "outcome_id": str})
        for x in p["linhas"]:
            if x["linha"].startswith("HI"):
                oid = x["linha"].split()[0]
                ref = hi[(hi["linha"] == oid) & (hi["outcome"] == oid) & (hi["variante"] == "principal")
                         & (hi["corte"] == "0.300")].iloc[0]
            else:
                ref = oc[(oc["parte"] == "A") & (oc["outcome_id"] == "B1") & (oc["populacao"] == "V")
                         & (oc["especificacao"] == "principal") & (oc["corte"] == "0.300")].iloc[0]
            self.assertAlmostEqual(float(ref["tau"]), x["tau"], delta=1e-8)
            self.assertAlmostEqual(float(ref["ep"]), x["ep"], delta=1e-8)


class TestInferenciaGravada(unittest.TestCase):
    def test_ic_e_p_do_ep(self):
        from math import erfc, sqrt
        for _, r in EST[EST["status"] == "EXECUTADO"].iterrows():
            self.assertAlmostEqual(r["ic95_inf"], r["tau"] - 1.959963984540054 * r["ep"], delta=1e-10)
            self.assertAlmostEqual(r["ic95_sup"], r["tau"] + 1.959963984540054 * r["ep"], delta=1e-10)
            self.assertAlmostEqual(r["p_valor"], erfc(abs(r["tau"] / r["ep"]) / sqrt(2)), delta=1e-10)

    def test_soma_dos_termos(self):
        for (oid, ct), g in EST.groupby(["outcome", "corte"]):
            t = g.set_index("termo")["tau"]
            self.assertAlmostEqual(t["tau0_mais_tau1_muda"], t["tau0_nao_muda"] + t["tau1_diferenca"], delta=1e-10)
            ep = g.set_index("termo")["ep"]
            # EP da soma entre |ep0 - ep1| e ep0 + ep1 (covariância limitada).
            self.assertLessEqual(ep["tau0_mais_tau1_muda"], ep["tau0_nao_muda"] + ep["tau1_diferenca"] + 1e-12)
            self.assertGreaterEqual(ep["tau0_mais_tau1_muda"], abs(ep["tau0_nao_muda"] - ep["tau1_diferenca"]) - 1e-12)

    def test_holm_e_bky_recalculados(self):
        L = PO.L
        for fam, n, col, fn in (("holm", 4, "p_holm", L.holm), ("bky", 6, "q_bky", L.qvalores_bky)):
            m = T1[T1["familia"] == fam]
            self.assertEqual(len(m), n)
            p = m["p_valor"].to_numpy(float)
            aj = np.asarray(fn(np.where(np.isfinite(p), p, 1.0)))
            np.testing.assert_allclose(m[col].to_numpy(float), aj, atol=1e-12)
        self.assertTrue(EST.loc[EST["termo"] != "tau1_diferenca", "familia"].eq("").all())
        self.assertTrue(EST.loc[EST["termo"] != "tau1_diferenca", ["p_holm", "q_bky"]].isna().all().all())
        self.assertEqual(set(T1.loc[T1["id_po"] == "PO-1", "outcome"]), {"HI-1", "HI-2"})

    def test_contagens_e_status(self):
        am = CO[CO["tipo"] == "amostra"]
        for _, r in EST.iterrows():
            s = am[(am["populacao"] == r["outcome"]) & (am["corte"] == r["corte"])]
            for g in (0, 1):
                for lado in ("abaixo", "acima"):
                    n = int(s[(s["G"] == g) & (s["lado"] == lado)]["n_municipios"].iloc[0])
                    self.assertEqual(n, int(r[f"n_mun_G{g}_{lado}"]))
            menor = min(int(r[f"n_mun_G{g}_{l}"]) for g in (0, 1) for l in ("abaixo", "acima"))
            if menor < 10:
                self.assertEqual(r["status"], "SEM_ESTIMATIVA_MENOS_DE_10")
            else:
                self.assertIn(r["status"], ("EXECUTADO", "SEM_ESTIMATIVA"))
        # Contagens da HI-1 e HI-2 somam as do 48b (sem porte faltante).
        hi = pd.read_csv(OUT / "HI_estimativas.csv", dtype={"corte": str})
        for oid in ("HI-1", "HI-2"):
            for ct in ("0.300", "0.400"):
                ref = hi[(hi["linha"] == oid) & (hi["outcome"] == oid) & (hi["variante"] == "principal")
                         & (hi["corte"] == ct)].iloc[0]
                s = am[(am["populacao"] == oid) & (am["corte"] == ct)]
                self.assertEqual(int(s["fora_sem_porte"].max()), 0)
                self.assertEqual(int(s[s["lado"] == "abaixo"]["n_municipios"].sum()), int(ref["n_abaixo"]))
                self.assertEqual(int(s[s["lado"] == "acima"]["n_municipios"].sum()), int(ref["n_acima"]))
                r = EST[(EST["outcome"] == oid) & (EST["corte"] == ct)].iloc[0]
                self.assertEqual(int(r["n_obs"]), int(ref["n_obs"]))

    def test_balanco_fracoes(self):
        b = CO[CO["tipo"] == "balanco"]
        for _, r in b.iterrows():
            self.assertAlmostEqual(sum(r[f"frac_{rg}"] for rg in PO.REGIOES), 1.0, delta=1e-12)
            self.assertTrue(0 <= r["frac_capital"] <= 1)


class TestRecalculoReal(unittest.TestCase):
    """ΔB5 (dados reais, construtores do 43): com retas próprias por grupo e salto T + T × G, τ₀ é o salto local linear
    só nos portes G = 0 e τ₀ + τ₁ só nos portes G = 1."""

    @classmethod
    def setUpClass(cls):
        cls.oc = PO.carregar_oc()
        cls.regra = PO.regra_g()
        cls.porte = PO.ler_a10(cls.regra)["porte_codigo"]

    def test_competencias(self):
        self.assertLess(self.oc["maior_competencia"], "202609")
        self.assertEqual(RES["parametros"]["maior_competencia_cnes_lida"], self.oc["maior_competencia"])

    def test_b5_por_grupo(self):
        L = PO.L
        for c in PO.CORTES:
            f = self.oc["frames"]["B5"]
            g = PO.g_de(f["co_ibge"].map(self.porte), self.regra, c).to_numpy(float)
            for gv, termo in ((0, "tau0_nao_muda"), (1, "tau0_mais_tau1_muda")):
                m = g == gv
                r = L.rd_local_linear(f["s_mil"].to_numpy(float)[m], f["y"].to_numpy(float)[m], c, 50)
                ref = EST[(EST["outcome"] == "B5") & (EST["corte"] == PO.ROT_CORTE[c]) & (EST["termo"] == termo)]
                self.assertAlmostEqual(r["tau"], float(ref["tau"].iloc[0]), delta=1e-9)


class TestIntegridade(unittest.TestCase):
    def setUp(self):
        self.src = SCRIPT.read_text(encoding="utf-8")

    def test_ivs_oficial_e_dados(self):
        self.assertNotIn("ivs_ipea_2010_municipios", self.src)
        for x in RES["entradas"]:
            self.assertNotIn("ivs_ipea_2010_municipios", x["arquivo"])
        self.assertIn("output/aquisicao/a08_ivs_2010_oficial_municipio.csv", [x["arquivo"] for x in RES["entradas"]])
        for v in RES["saidas"].values():
            self.assertTrue(v.startswith("output/") or v.startswith("docs/"), v)
        self.assertNotRegex(self.src, r"\"data\"[^\n]*(write|to_csv|to_parquet)")
        self.assertNotIn("ROOT / \"data\"", self.src)

    def test_sem_competencia_202609(self):
        self.assertEqual(PO.LIMITE_CNES, "202609")
        self.assertLess(RES["parametros"]["maior_competencia_cnes_lida"], "202609")

    def test_nao_regrava_saidas_de_outros(self):
        for pref in ("HI_", "OC_", "CL_", "PM_"):
            self.assertNotRegex(self.src, rf"to_csv\([^)]*{pref}|\"{pref}[^\"]*\"\)?\.write")
        self.assertEqual(RES["integridade"]["saidas_nao_regravadas"], ["HI_*", "OC_*", "CL_*", "PM_*"])
        for nome in ("NOME_EST", "NOME_CONT", "NOME_RESUMO"):
            self.assertTrue(getattr(PO, nome).startswith("PO_"))

    def test_adendo_congelado(self):
        self.assertEqual(PO.sha256(ADENDO), PO.SHA_ADENDO)
        self.assertEqual(RES["adendo"]["sha256"], PO.SHA_ADENDO)

    def test_entradas_com_hash_atual(self):
        for x in RES["entradas"]:
            self.assertEqual(PO.sha256(ROOT / x["arquivo"]), x["sha256"], x["arquivo"])


class TestLeitura(unittest.TestCase):
    def test_leitura_refeita(self):
        self.assertEqual(json.loads(json.dumps(PO._nan_none(PO.leituras(EST, CO)))), RES["leitura"])

    def test_regra_po1(self):
        prim = T1[T1["id_po"] == "PO-1"]
        todas = all(r["ic95_inf"] <= 0 <= r["ic95_sup"] for _, r in prim.iterrows())
        if todas:
            self.assertEqual(RES["leitura"]["po1"]["codigo"], "TAU1_TODOS_CONTEM_ZERO")
        if (prim["p_holm"] < 0.05).any():
            self.assertIn(RES["leitura"]["po1"]["codigo"], ("TAU1_REJEITA_HOLM_CONCENTRADO",
                                                            "TAU1_REJEITA_HOLM_SEM_CONCENTRACAO"))


class TestSintetico(unittest.TestCase):
    """SINTÉTICO, só em memória (nada é gravado)."""

    def _amostra(self, s, y, g, corte=300):
        d = pd.DataFrame({"s_mil": s, "co_ibge": [f"{i:06d}" for i in range(len(s))], "y": y})
        return PO.T23.montar_amostra([(d, corte, "V")], empilhada=False), g.astype(float)

    def test_sintetico_recupera_tau0_e_tau1_sem_ruido(self):
        s = np.concatenate([np.arange(252, 349), np.arange(252, 349)]).astype(float)
        g = np.repeat([0, 1], 97)
        t = (s > 300).astype(float)
        y = 1.0 + 0.02 * (s - 300) + 0.5 * g + 0.01 * g * (s - 300) + 2.0 * t + 3.0 * t * g
        a, G = self._amostra(s, y, g)
        r = PO.ajustar_po(a, "B5", G)
        tt = PO.termos(r)
        self.assertTrue(tt["ok"])
        self.assertAlmostEqual(tt["tau0_nao_muda"]["tau"], 2.0, places=8)
        self.assertAlmostEqual(tt["tau1_diferenca"]["tau"], 3.0, places=8)
        self.assertAlmostEqual(tt["tau0_mais_tau1_muda"]["tau"], 5.0, places=8)

    def test_sintetico_identidade_com_saltos_por_grupo(self):
        rng = np.random.default_rng(20261026)
        s = rng.integers(251, 350, 400).astype(float)
        g = rng.integers(0, 2, 400)
        y = rng.normal(size=400) + (s > 300) * (1 + g)
        a, G = self._amostra(s, y, g)
        tt = PO.termos(PO.ajustar_po(a, "B5", G))
        for gv, termo in ((0, "tau0_nao_muda"), (1, "tau0_mais_tau1_muda")):
            r = PO.L.rd_local_linear(s[g == gv], y[g == gv], 300, 50)
            self.assertAlmostEqual(r["tau"], tt[termo]["tau"], delta=1e-10)

    def test_sintetico_sem_divisao_igual_a_local_linear(self):
        rng = np.random.default_rng(7)
        s = rng.integers(251, 350, 300).astype(float)
        y = rng.normal(size=300) + (s > 300)
        a, _ = self._amostra(s, y, np.zeros(300))
        r = PO.ajustar_po(a, "B5", None)
        r0 = PO.L.rd_local_linear(s, y, 300, 50)
        self.assertAlmostEqual(r["tau"], r0["tau"], delta=1e-10)
        self.assertAlmostEqual(r["ep"], r0["ep"], delta=1e-10)

    def test_sintetico_grupo_constante_fica_sem_estimativa(self):
        rng = np.random.default_rng(3)
        s = rng.integers(251, 350, 200).astype(float)
        a, G = self._amostra(s, rng.normal(size=200), np.ones(200))
        tt = PO.termos(PO.ajustar_po(a, "B5", G))
        self.assertFalse(tt["ok"])


class TestDoc(unittest.TestCase):
    def setUp(self):
        self.txt = DOC.read_text(encoding="utf-8")

    def test_blocos_iguais_aos_gerados(self):
        blocos = PO.gerar_blocos(EST, CO, RES)
        achados = {m.group("nome"): m.group("corpo") for m in PO.MARCA.finditer(self.txt)}
        self.assertEqual(set(achados), set(blocos))
        for nome, corpo in blocos.items():
            self.assertEqual(achados[nome].rstrip(), corpo.rstrip(), nome)

    def test_cabecalho_e_decisoes_antes(self):
        self.assertIn("ADENDO_48G_POS_RESULTADO", self.txt)
        self.assertIn("**Auditoria:** [auditoria 45]", self.txt)
        i_dec = self.txt.index("## 0. Decisões de implementação")
        i_res = self.txt.index("<!-- PO:resposta_curta:inicio -->")
        self.assertLess(i_dec, i_res)

    def test_sem_numero_de_resultado_fora_dos_blocos(self):
        fora = PO.MARCA.sub("", self.txt)
        permitidos = {"0,050", "0,300", "0,400", "0,05", "1e−8"}
        for n in re.findall(r"[−+-]?\d+,\d+|\d+e[−-]\d+", fora):
            self.assertIn(n.lstrip("+−-"), permitidos, n)

    def test_linguagem(self):
        baixo = self.txt.lower()
        for proibida in ("a bolsa reduz", "a bolsa aumenta", "o ied causa", "efeito causal do ied foi"):
            self.assertNotIn(proibida, baixo)
        self.assertIn("pacote do corte", self.txt)
        self.assertIn("descritiv", self.txt)


if __name__ == "__main__":
    unittest.main()
