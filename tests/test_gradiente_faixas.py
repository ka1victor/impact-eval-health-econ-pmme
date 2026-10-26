"""Testes do protocolo 62 (script 39): por que o preenchimento sobe com o IVS dentro das faixas da bolsa (descritivo).

- O doc 57m tem de ser idêntico ao que o script gera a partir de `output/`.
- Os números de `output/rdd_bolsa/GF_*` são conferidos contra uma reestimação independente (statsmodels, a partir de
  `outcomes_V_celula.parquet` e do IVS oficial do a08) e recalculados onde a conta é simples (fração da subida, regra
  da metade, BKY, IC e p, leitura pré-registrada, médias por faixa de IVS).
- O modelo e a conta do G-b são conferidos em casos SINTÉTICOS construídos em memória (rotulados "sintético"; nada vai
  para `output/`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "rdd_bolsa"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "39_gradiente_faixas.py"
DOC = ROOT / "docs" / "06_execucao" / "57m_gradiente_faixas.md"
PROTOCOLO = ROOT / "docs" / "06_execucao" / "62_protocolo_gradiente_dentro_das_faixas.md"
A08 = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
CELULAS = OUT / "outcomes" / "outcomes_V_celula.parquet"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


GF = _mod("gf39_teste", SCRIPT)
EST, RESUMO = GF.ler_saidas()
INCL = EST[EST["tipo_linha"] == "inclinacao"]
EXEC = INCL[INCL["status"] == "EXECUTADO"]


def _celulas_independentes() -> pd.DataFrame:
    """Base do A3 refeita sem o script: células do quadro com o IVS oficial do município (a08)."""
    c = pd.read_parquet(CELULAS, columns=["ciclo", "co_ibge", "n_alocados_ch1"])
    a = pd.read_csv(A08, dtype={"co_ibge": str}, usecols=["co_ibge", "ivs"])
    c["co_ibge"] = c["co_ibge"].astype(str).str.zfill(6)
    a["co_ibge"] = a["co_ibge"].str.zfill(6)
    c = c.merge(a, on="co_ibge", how="inner", validate="many_to_one")
    c = c[c["ivs"].notna()].copy()
    c["s_mil"] = np.round(c["ivs"] * 1000)
    c["preenchida"] = (c["n_alocados_ch1"] >= 1).astype(float)
    return c


class TestSaidas(unittest.TestCase):
    def test_rotulos_e_estatuto(self):
        self.assertEqual(set(EST["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(EST["estatuto"]), {"DESCRITIVO_62_POS_RESULTADO"})
        self.assertEqual(RESUMO["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(RESUMO["estatuto"], "DESCRITIVO_62_POS_RESULTADO")
        self.assertFalse(EST["id_linha"].duplicated().any())

    def test_hashes_do_protocolo_das_entradas_e_saidas(self):
        self.assertEqual(RESUMO["protocolo"]["sha256"], GF.sha256(PROTOCOLO))
        for e in RESUMO["entradas"]:
            self.assertEqual(e["sha256"], GF.sha256(ROOT / e["caminho"]), e["caminho"])
        self.assertEqual(RESUMO["saidas"]["GF_estimativas.csv"]["sha256"], GF.sha256(OUT / "GF_estimativas.csv"))
        nomes = set()
        for f in RESUMO["saidas"]["figuras"]:
            self.assertEqual(f["sha256"], GF.sha256(ROOT / f["arquivo"]))
            self.assertTrue(f["como_ler"])
            nomes.add(Path(f["arquivo"]).name)
        self.assertEqual(nomes, {"GF_medias_por_ivs.png", "GF_inclinacao_fatores.png",
                                 "GF_inclinacao_fatores_janela.png"})
        self.assertEqual(set(p.name for p in (OUT / "GF_figuras").glob("*.png")), nomes)

    def test_sem_identificador_pessoal(self):
        cols = {c.lower() for c in EST.columns}
        self.assertFalse(cols & {"id_candidato", "cpf", "cpf_masc", "nome", "co_profissional_sus"})
        for arq in ("GF_estimativas.csv", "GF_resumo.json"):
            texto = (OUT / arq).read_text(encoding="utf-8")
            self.assertNotRegex(texto, r"c[123]_\d{5}", arq)   # formato do id_candidato das tabelas de escolha

    def test_lista_fechada_relatada(self):
        self.assertEqual([e["id"] for e in RESUMO["explicacoes"]], ["G-a", "G-b", "G-c", "G-d", "G-e", "G-f"])
        for e in ("G-a", "G-b", "G-c", "G-d", "G-e", "TODOS"):
            for fx in ("R$10mil", "R$15mil", "R$20mil"):
                self.assertTrue(((INCL["explicacao"] == e) & (INCL["faixa"] == fx)).any(), (e, fx))
        gf = EST[EST["explicacao"] == "G-f"]
        self.assertEqual(len(gf), 1)
        self.assertEqual(gf["status"].iloc[0], "SEM_FATOR_TESTAVEL")

    def test_gf_aponta_a_pesquisa_documental(self):
        achados = sorted(p for p in (ROOT / "docs" / "auditorias").glob("35_*") if p.is_file())
        arquivos = RESUMO["G-f"]["arquivos"]
        if arquivos:
            for a in arquivos:
                self.assertEqual(a["sha256"], GF.sha256(ROOT / a["caminho"]))
        else:
            self.assertIn("docs/auditorias/35_*", RESUMO["G-f"]["situacao"])
        # Se a pesquisa documental chegou depois da execução, o script tem de ser rodado de novo para apontá-la.
        self.assertEqual([GF.rotulo(p) for p in achados], [a["caminho"] for a in arquivos],
                         "docs/auditorias/35_* mudou: rode 39_gradiente_faixas.py de novo")

    def test_ancoras_da_auditoria_18(self):
        aud = (ROOT / "docs" / "auditorias" / "18_politicas_nos_mesmos_cortes_ivs.md").read_text(encoding="utf-8")
        for r in RESUMO["regras_gf_auditoria_18"]:
            self.assertIn(r["ancora"], aud)

    def test_script_integridade(self):
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", src)
        self.assertNotIn('ROOT / "data"', src)
        cnes = [e for e in RESUMO["entradas"] if "cnes_nacional" in e["caminho"]]
        self.assertEqual([e["data_referencia"] for e in cnes], ["202406-202506"])
        self.assertTrue(all(e["data_referencia"] < "202609" for e in cnes))


class TestNumerosContraOutput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cel = _celulas_independentes()

    def test_contagens_por_faixa(self):
        s = self.cel["s_mil"]
        esperado = {"R$10mil": int((s <= 300).sum()), "R$15mil": int(((s > 300) & (s <= 400)).sum()),
                    "R$20mil": int((s > 400).sum())}
        self.assertEqual(RESUMO["info_dados"]["celulas_por_faixa"], esperado)

    def test_inclinacao_original_reestimada_com_statsmodels(self):
        import statsmodels.formula.api as smf
        for fx in GF.FAIXAS:
            for jan in GF.JANELAS:
                r = INCL[(INCL["faixa"] == fx["faixa"]) & (INCL["janela"] == jan) & (INCL["explicacao"] == "ORIGINAL")]
                self.assertEqual(len(r), 1)
                r = r.iloc[0]
                m = GF.mascara(self.cel, fx, jan)
                if not m.any():
                    self.assertEqual(r["status"], "NAO_SE_APLICA")
                    continue
                d = self.cel[m].copy()
                d["x"] = d["s_mil"] / 100.0
                fit = smf.ols("preenchida ~ x + C(ciclo)", data=d).fit(cov_type="cluster",
                                                                     cov_kwds={"groups": d["co_ibge"]})
                self.assertEqual(int(r["n_obs"]), len(d))
                self.assertAlmostEqual(float(r["inclinacao"]), fit.params["x"], places=10)
                self.assertAlmostEqual(float(r["ep"]), fit.bse["x"], places=8)
                self.assertAlmostEqual(float(r["media_preenchida"]), d["preenchida"].mean(), places=12)

    def test_medias_por_faixa_de_ivs(self):
        b = EST[EST["tipo_linha"] == "media_bin"]
        for fx in GF.FAIXAS:
            d = self.cel[GF.mascara(self.cel, fx, "faixa_inteira")]
            k = np.ceil(d["s_mil"] / 10).astype(int)
            g = d.groupby(k)["preenchida"].agg(["mean", "size"])
            bf = b[b["faixa"] == fx["faixa"]].sort_values("bin_ivs_sup")
            np.testing.assert_allclose(bf["bin_ivs_sup"].to_numpy(dtype=float), g.index.to_numpy() / 100, atol=1e-12)
            np.testing.assert_allclose(bf["media_preenchida"].to_numpy(dtype=float), g["mean"].to_numpy(), atol=1e-12)
            self.assertEqual(int(bf["n_celulas_bin"].sum()), len(d))

    def test_original_na_mesma_amostra_sem_ausentes_e_a_original(self):
        orig = INCL[INCL["explicacao"] == "ORIGINAL"].set_index(["faixa", "janela"])["inclinacao"]
        for _, r in EXEC[EXEC["explicacao"] != "ORIGINAL"].iterrows():
            self.assertAlmostEqual(float(r["inclinacao_original"]), float(orig[(r["faixa"], r["janela"])]), places=12)
            if int(r["n_fora"]) == 0:
                self.assertAlmostEqual(float(r["inclinacao_original_mesma_amostra"]), float(r["inclinacao_original"]),
                                       places=12)
            else:
                self.assertTrue(r["motivo_fora"])

    def test_fracao_e_regra_da_metade(self):
        fx = EXEC[EXEC["explicacao"] != "ORIGINAL"]
        self.assertGreater(len(fx), 0)
        for _, r in fx.iterrows():
            base = float(r["inclinacao_original_mesma_amostra"])
            if base <= 0:
                self.assertTrue(pd.isna(r["fracao_da_subida_levada"]))
                self.assertEqual(r["reduz_metade"], "nao_se_aplica")
                continue
            f = 1 - float(r["inclinacao"]) / base
            self.assertAlmostEqual(float(r["fracao_da_subida_levada"]), f, places=12)
            self.assertEqual(r["reduz_metade"], "sim" if f >= 0.5 else "nao")

    def test_bky_entre_as_inclinacoes(self):
        m = (EST["tipo_linha"] == "inclinacao") & EST["p_valor"].notna()
        q = GF.L.qvalores_bky(EST.loc[m, "p_valor"].to_numpy(dtype=float))
        np.testing.assert_allclose(EST.loc[m, "q_bky"].to_numpy(dtype=float), q, atol=1e-12)
        self.assertTrue(EST.loc[EST["tipo_linha"] != "inclinacao", "q_bky"].isna().all())

    def test_ic_e_p_pela_normal(self):
        from scipy import stats
        s = EST[EST["tipo_linha"].isin(["inclinacao", "balanco"]) & (EST["status"] == "EXECUTADO")]
        z = stats.norm.ppf(0.975)
        np.testing.assert_allclose(s["ic95_inf"], s["inclinacao"] - z * s["ep"], atol=1e-9)
        np.testing.assert_allclose(s["ic95_sup"], s["inclinacao"] + z * s["ep"], atol=1e-9)
        np.testing.assert_allclose(s["p_valor"], 2 * stats.norm.sf(np.abs(s["inclinacao"] / s["ep"])), atol=1e-9)

    def test_leitura_preregistrada_refeita(self):
        for fx in GF.FAIXAS:
            for jan in GF.JANELAS:
                lr = RESUMO["leitura"][f"{fx['faixa']}|{jan}"]
                sub = INCL[(INCL["faixa"] == fx["faixa"]) & (INCL["janela"] == jan)]
                o = sub[sub["explicacao"] == "ORIGINAL"].iloc[0]
                if o["status"] != "EXECUTADO":
                    self.assertEqual(lr["leitura"], "NAO_SE_APLICA")
                    continue
                if float(o["inclinacao"]) <= 0:
                    self.assertEqual(lr["leitura"], "SEM_SUBIDA")
                    continue
                red = sorted(set(sub[sub["explicacao"].str.startswith("G-") & (sub["reduz_metade"] == "sim")]
                                 ["explicacao"]))
                self.assertEqual(lr["fatores_que_reduzem_metade"], red)
                self.assertEqual(lr["leitura"], "FATOR_DESCREVE_A_SUBIDA" if red
                                 else "SUBIDA_NAO_SE_EXPLICA_COM_OS_DADOS")


class TestDoc(unittest.TestCase):
    def test_doc_igual_ao_gerado(self):
        self.assertEqual(DOC.read_text(encoding="utf-8"), GF.gerar_doc(EST, RESUMO))

    def test_secoes_e_linguagem(self):
        t = DOC.read_text(encoding="utf-8")
        for s in ("## 1. Resposta curta", "## 3. G-a", "## 4. G-b", "## 5. G-c", "## 6. G-d", "## 7. G-e",
                  "## 8. G-f", "## 9. Quanto da subida", "## 10. Leitura pré-registrada", "## 11. Figuras",
                  "## 12. Limites", "**Como ler:**", "Descritivo e pós-resultado", "anda junto"):
            self.assertIn(s, t)
        baixo = t.lower()
        self.assertNotRegex(baixo, r"\bcaus(a|am|ou|aram|ar|ando)\b")   # "causal" (em "não é causal") é permitido
        for proibida in ("a bolsa reduziu", "efeito da bolsa sobre", "provoca"):
            self.assertNotIn(proibida, baixo)
        self.assertEqual(t.count(":inicio -->"), t.count(":fim -->"))
        self.assertGreaterEqual(t.count(":inicio -->"), 20)
        for f in RESUMO["saidas"]["figuras"]:
            self.assertIn(f["como_ler"], t)
            self.assertIn(f["arquivo"], t)


class TestSintetico(unittest.TestCase):
    """Casos sintéticos em memória (rotulados "sintético"); nada vai para output/."""

    @staticmethod
    def _sintetico(semente: int = 3) -> pd.DataFrame:
        # sintético: 200 municípios, IVS de 0,100 a 0,300; a região B tem IVS mais alto e preenche mais; dentro de
        # cada região o preenchimento não depende do IVS.
        rng = np.random.default_rng(semente)
        linhas = []
        for i in range(200):
            reg = "B" if i >= 100 else "A"
            s = rng.integers(200, 301) if reg == "B" else rng.integers(100, 201)
            for k in (1, 2):
                for _ in range(4):
                    p = 0.6 if reg == "B" else 0.2
                    linhas.append({"co_ibge": f"9{i:05d}", "ciclo": k, "s_mil": float(s), "macro": reg,
                                   "preenchida": float(rng.random() < p)})
        return pd.DataFrame(linhas)

    def test_sintetico_efeito_fixo_leva_a_subida(self):
        d = self._sintetico()
        r0 = GF.ajustar(d)
        r1 = GF.ajustar(d, fe=("macro",))
        self.assertGreater(r0["inclinacao"], 0.1)
        self.assertLess(abs(r1["inclinacao"]), 0.08)
        self.assertGreaterEqual(GF.fracao_levada(r1["inclinacao"], r0["inclinacao"]), 0.5)
        self.assertTrue(np.isnan(GF.fracao_levada(0.1, -0.2)))

    def test_sintetico_ajustar_igual_a_mqo_com_cr1(self):
        d = self._sintetico(5)
        r = GF.ajustar(d, fe=("macro",))
        X = np.column_stack([np.ones(len(d)), d["s_mil"] / 100, (d["ciclo"] == 2).astype(float),
                             (d["macro"] == "B").astype(float)])
        y = d["preenchida"].to_numpy()
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        e = y - X @ beta
        _, g = np.unique(d["co_ibge"], return_inverse=True)
        S = np.zeros((g.max() + 1, X.shape[1]))
        np.add.at(S, g, X * e[:, None])
        B = np.linalg.inv(X.T @ X)
        G, n, k = g.max() + 1, len(y), X.shape[1]
        V = B @ (S.T @ S) @ B * (G / (G - 1)) * ((n - 1) / (n - k))
        self.assertAlmostEqual(r["inclinacao"], beta[1], places=10)
        self.assertAlmostEqual(r["ep"], float(np.sqrt(V[1, 1])), places=10)
        self.assertEqual(r["n_municipios"], 200)

    def test_sintetico_janela_e_faixa(self):
        d = pd.DataFrame({"s_mil": [250.0, 251.0, 300.0, 301.0, 350.0, 351.0, 400.0, 401.0]})
        f10, f15, f20 = GF.FAIXAS
        self.assertEqual(d["s_mil"][GF.mascara(d, f10, "faixa_inteira")].tolist(), [250.0, 251.0, 300.0])
        self.assertEqual(d["s_mil"][GF.mascara(d, f10, "janela_0050_corte_superior")].tolist(), [251.0, 300.0])
        self.assertEqual(d["s_mil"][GF.mascara(d, f15, "janela_0050_corte_superior")].tolist(), [351.0, 400.0])
        self.assertFalse(GF.mascara(d, f20, "janela_0050_corte_superior").any())
        self.assertEqual(GF.faixa_de(d["s_mil"]).tolist(), ["R$10mil"] * 3 + ["R$15mil"] * 4 + ["R$20mil"])

    def test_sintetico_contagem_do_gb(self):
        # sintético: 3 candidatos do curso 1 no ciclo 1 (dois da UF 11, um sem CIR), 2 células na UF 11
        o = pd.DataFrame({"ciclo": [1, 1, 1], "cod_curso": [1, 1, 1], "id_candidato": ["a", "b", "c"],
                          "uf_o": ["11", "11", "22"], "cir_o": ["R1", np.nan, "R9"]})
        q = pd.DataFrame({"ciclo": [1, 1, 1], "cod_curso": [1, 1, 1], "vic": [2.0, 3.0, 1.0],
                          "uf": ["11", "11", "33"], "cir": ["R1", "R2", np.nan]})
        cel = pd.DataFrame({"ciclo": [1, 1, 1], "cod_curso": [1, 1, 1], "uf": ["11", "11", "33"],
                            "cir": ["R1", "R2", np.nan]})
        r = GF.contar_por_perto(o, q, cel)
        np.testing.assert_allclose(r["cand_uf_por_vaga"], [2 / 5, 2 / 5, 0.0])
        np.testing.assert_allclose(r["cand_cir_por_vaga"].to_numpy()[:2], [1 / 2, 0.0])
        self.assertTrue(np.isnan(r["cand_cir_por_vaga"].iloc[2]))


if __name__ == "__main__":
    unittest.main()
