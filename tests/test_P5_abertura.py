"""Testes do P5 (protocolo 55): `scripts/rdd_bolsa/29_determinantes_abertura.py`.

Três partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados como sintéticos e nunca
   gravados em `output/` nem em `data/`. Conferem o logit e o Poisson (Newton-Raphson) contra o statsmodels
   (coeficientes, EP CR1 por cluster e HC1, pseudo-R²), os efeitos marginais médios e o EP pelo método delta
   contra o `get_margeff` do statsmodels, a regra de separação, a contribuição de bloco e a regra "município
   ausente do resultado da adesão = pedido ausente, nunca zero".
2. `TestSaidasReais`: esquema e rótulos de `output/rdd_bolsa/P5_*`, ausências com nota, grade do T5.2, BKY só
   nas linhas do T5.2 do protocolo, janelas do CNES e do SIA, hashes, figuras e um recálculo independente (com
   o statsmodels) do logit do E2 e do Poisson do T5.3.
3. `TestDoc57e`: blocos do doc 57e iguais aos gerados das saídas, prosa sem número de resultado e linguagem
   descritiva.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "29_determinantes_abertura.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("determinantes_abertura_29", SCRIPT)
P5 = importlib.util.module_from_spec(_spec)
sys.modules["determinantes_abertura_29"] = P5
_spec.loader.exec_module(P5)
sys.dont_write_bytecode = _bytecode
L = P5.L

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "P5_estimativas.csv"
RESUMO = OUT / "P5_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "57e_resultados_P5_abertura.md"

NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui; nunca gravados


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def celulas_sinteticas(semente: int = 11, n: int = 4000) -> pd.DataFrame:
    """SINTÉTICO: células com cluster (município), uma contínua, uma binária, uma categórica e um efeito fixo."""
    rng = np.random.default_rng(semente)
    mun = rng.integers(0, 300, n)
    x = rng.normal(0, 1, n) + 0.3 * (mun % 7) / 7
    b = (rng.random(n) < 0.4).astype(float)
    cat = rng.choice(["A", "B", "C"], n, p=[0.5, 0.3, 0.2])
    curso = rng.choice([f"curso{i:02d}" for i in range(1, 6)], n)
    eta = -0.3 + 0.8 * x - 0.6 * b + np.where(cat == "B", 0.5, np.where(cat == "C", -0.4, 0.0)) \
        + np.array([0.0, 0.2, -0.3, 0.4, 0.1])[np.array([int(c[-2:]) - 1 for c in curso])] \
        + rng.normal(0, 0.3, 300)[mun]
    y = (rng.random(n) < 1 / (1 + np.exp(-eta))).astype(float)
    cont = rng.poisson(np.exp(0.2 + 0.5 * x - 0.4 * b)).astype(float)
    return pd.DataFrame({"co_ibge": [f"9{m:05d}" for m in mun], "x": x, "b": b, "cat": cat, "curso": curso, "y": y,
                         "cont": cont, "natureza_dos_dados": NATUREZA_SINTETICA})


COVS_SINT = [P5._c("x", "municipio", "continua", "x sintético"),
             P5._c("b", "estabelecimento", "binaria", "b sintético"),
             P5._c("cat", "estabelecimento", "categorica", "cat sintético", "A")]


class TestSintetico(unittest.TestCase):
    """Estimadores em dados sintéticos (nada é gravado)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.d = celulas_sinteticas()

    def test_dados_rotulados_como_sinteticos(self) -> None:
        self.assertTrue((self.d["natureza_dos_dados"] == NATUREZA_SINTETICA).all())

    def test_logit_e_cluster_iguais_ao_statsmodels(self) -> None:
        import statsmodels.api as sm
        r = P5.ajustar_glm(self.d, "y", COVS_SINT, "curso", "logit")
        self.assertTrue(r["fit"]["convergiu"])
        m = sm.Logit(r["y"], r["X"]).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(r["d"]["co_ibge"])[0]})
        np.testing.assert_allclose(r["fit"]["beta"], m.params, rtol=1e-7, atol=1e-9)
        np.testing.assert_allclose(np.sqrt(np.diag(r["V"])), m.bse, rtol=1e-6)
        self.assertAlmostEqual(r["pseudo_r2"], m.prsquared, places=10)
        # A inclinação da contínua recupera o valor usado na geração (com folga de amostra).
        j = r["nomes"].index("x")
        self.assertLess(abs(r["fit"]["beta"][j] - 0.8), 0.15)

    def test_efeitos_marginais_iguais_ao_get_margeff(self) -> None:
        import statsmodels.api as sm
        covs = COVS_SINT[:2]   # contínua e uma dummy isolada (sem irmãos de fator), como no statsmodels
        r = P5.ajustar_glm(self.d, "y", covs, None, "logit")
        m = sm.Logit(r["y"], r["X"]).fit(disp=0, cov_type="cluster", cov_kwds={"groups": pd.factorize(r["d"]["co_ibge"])[0]})
        me = m.get_margeff(at="overall", method="dydx", dummy=True)
        for j, nome in enumerate(r["nomes"][1:], start=1):
            ame, ep = P5.ame_logit(r["X"], r["fit"]["beta"], r["V"], j, r["meta"][j], r["nomes"], r["meta"])
            self.assertAlmostEqual(ame, me.margeff[j - 1], places=8, msg=nome)
            self.assertAlmostEqual(ep, me.margeff_se[j - 1], places=6, msg=nome)

    def test_efeito_marginal_de_nivel_zera_os_irmaos(self) -> None:
        r = P5.ajustar_glm(self.d, "y", COVS_SINT, None, "logit")
        j = r["nomes"].index("cat=B")
        ame, _ = P5.ame_logit(r["X"], r["fit"]["beta"], r["V"], j, r["meta"][j], r["nomes"], r["meta"])
        X1, X0 = r["X"].copy(), r["X"].copy()
        for nome in ("cat=B", "cat=C"):
            X1[:, r["nomes"].index(nome)] = 0.0
            X0[:, r["nomes"].index(nome)] = 0.0
        X1[:, j] = 1.0
        esperado = np.mean(1 / (1 + np.exp(-X1 @ r["fit"]["beta"])) - 1 / (1 + np.exp(-X0 @ r["fit"]["beta"])))
        self.assertAlmostEqual(ame, float(esperado), places=12)

    def test_poisson_hc1_igual_ao_statsmodels(self) -> None:
        import statsmodels.api as sm
        d = self.d.assign(co_ibge=[f"u{i}" for i in range(len(self.d))])   # um município por linha: CR1 = HC1
        r = P5.ajustar_glm(d, "cont", COVS_SINT[:2], None, "poisson")
        # HC1 = HC0 x n/(n-k) (o "HC1" do GLM do statsmodels não aplica o fator; por isso o HC0 escalado).
        m = sm.GLM(r["y"], r["X"], family=sm.families.Poisson()).fit(cov_type="HC0")
        n, k = r["X"].shape
        np.testing.assert_allclose(r["fit"]["beta"], m.params, rtol=1e-7, atol=1e-9)
        np.testing.assert_allclose(np.sqrt(np.diag(r["V"])), m.bse * np.sqrt(n / (n - k)), rtol=1e-6)
        self.assertAlmostEqual(r["pseudo_r2"], 1 - m.deviance / m.null_deviance, places=10)

    def test_separacao_remove_nivel_constante_e_conta(self) -> None:
        d = self.d.copy()
        d.loc[d["curso"] == "curso05", "y"] = 1.0
        r = P5.ajustar_glm(d, "y", COVS_SINT, "curso", "logit")
        self.assertEqual([(s["variavel"], s["nivel"]) for s in r["separacao"]], [("curso", "curso05")])
        self.assertEqual(len(r["y"]), int((d["curso"] != "curso05").sum()))
        self.assertTrue(r["fit"]["convergiu"])

    def test_covariavel_ausente_sai_e_e_contada_sem_virar_zero(self) -> None:
        d = self.d.copy()
        d.loc[d.index[:50], "x"] = np.nan
        r = P5.ajustar_glm(d, "y", COVS_SINT, None, "logit")
        self.assertEqual(r["descartadas_covariavel"]["x"], 50)
        self.assertEqual(len(r["y"]), len(d) - 50)

    def test_contribuicao_de_bloco_e_queda_do_pseudo_r2(self) -> None:
        r = P5.ajustar_glm(self.d, "y", COVS_SINT, "curso", "logit")
        idx = [i for i, m in enumerate(r["meta"]) if m["bloco"] != "estabelecimento"]
        f = P5.irls(r["X"][:, idx], r["y"], "logit")
        self.assertAlmostEqual(r["blocos"]["estabelecimento"]["pseudo_r2_sem_bloco"],
                               P5.pseudo_r2("logit", r["X"][:, idx], r["y"], f), places=12)
        self.assertGreater(r["pseudo_r2"], r["blocos"]["estabelecimento"]["pseudo_r2_sem_bloco"])

    def test_municipio_ausente_da_adesao_fica_ausente_nunca_zero(self) -> None:
        card = pd.DataFrame({"co_cnes_7d": ["0000001", "0000002", "0000003", "0000004"], "cod_curso": [1, 2, 1, 2],
                             "co_ibge": ["900001", "900001", "900002", "900002"], "vagas_cardapio": [2.0, 1.0, 3.0, 1.0],
                             "tipo": ["05 HOSPITAL GERAL"] * 4, "gestao": ["MUNICIPAL"] * 4, "natureza": ["PUBLICO"] * 4})
        # Só o município 900001 consta; a célula 2 dele não foi pedida; a 1 foi pedida e priorizada.
        ad = pd.DataFrame({"co_cnes_7d": ["0000001"], "cod_curso": [1], "co_ibge": ["900001"], "priorizadas": [2.0],
                           "priorizadas_imediatas": [2.0], "priorizadas_cr": [0.0], "nao_priorizadas": [0.0]})
        mun = pd.DataFrame({"s_mil": [300.0, 350.0]}, index=pd.Index(["900001", "900002"], name="co_ibge"))
        vc = pd.DataFrame({1: [1.0, 2.0], 2: [0.5, 0.0]}, index=mun.index)
        cel, info = P5.montar_celulas(card, ad, mun, vc, vc, {1: ["225151"], 2: ["225225"]})
        self.assertEqual(cel["pedida"].tolist()[:2], [1.0, 0.0])
        self.assertTrue(cel["pedida"].iloc[2:].isna().all())
        self.assertTrue(cel["priorizada_cardapio"].iloc[2:].isna().all())
        self.assertEqual(cel["priorizada"].iloc[0], 1.0)
        self.assertTrue(cel["priorizada"].iloc[1:].isna().all())
        self.assertEqual(info["municipios_que_constam"], 1)

    def test_bky_so_nas_linhas_do_t52_do_protocolo(self) -> None:
        est = pd.DataFrame([P5.nova_linha(especificacao=e, no_protocolo=np_, p_valor=p)
                            for e, np_, p in (("T5.2a", True, 0.01), ("T5.2b", True, 0.04), ("T5.2a", False, 0.001),
                                              ("T5.1c", True, 0.001), ("T5.3", True, 0.002))])
        est = P5.aplicar_bky(est)
        self.assertEqual(est["entra_bky"].tolist(), [True, True, False, False, False])
        np.testing.assert_allclose(est.loc[:1, "q_bky"], L.qvalores_bky(np.array([0.01, 0.04])))
        self.assertTrue(est.loc[2:, "q_bky"].isna().all())

    def test_fonte_sem_ivs_errado_e_sem_preencher_zero(self) -> None:
        fonte = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", fonte)
        self.assertNotIn("fillna(0", fonte)
        self.assertIn('("competencia", "<=", COMP_PRE[1])', fonte)
        self.assertIn('("competencia_processamento", "in", meses)', fonte)


class TestSaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(EST, dtype={"corte": str, "ciclo": str})
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_esquema_e_rotulos(self) -> None:
        self.assertEqual(list(self.est.columns), P5.COLUNAS)
        self.assertTrue((self.est["natureza_dos_dados"] == "EMPIRICO").all())
        self.assertTrue((self.est["estatuto"] == "PROTOCOLO_55_DESCRITIVO").all())
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(self.resumo["estatuto"], "PROTOCOLO_55_DESCRITIVO")
        self.assertTrue(set(self.est["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA", "NAO_EXECUTADO"})
        fora = self.est[~self.est["no_protocolo"].astype(bool)]
        self.assertTrue((fora["rotulo"].fillna("").str.len() > 0).all())

    def test_nan_sempre_com_nota(self) -> None:
        nucleo = ["estimativa", "ep", "ic95_inf", "ic95_sup", "p_valor"]
        ruins = self.est[self.est[nucleo].isna().any(axis=1) & (self.est["nota"].fillna("") == "")]
        self.assertEqual(len(ruins), 0)

    def test_todas_as_especificacoes_relatadas(self) -> None:
        self.assertEqual(set(self.est["especificacao"]), {"T5.1a", "T5.1b", "T5.1c", "T5.2a", "T5.2b", "T5.3"})
        t52 = self.est[self.est["especificacao"].isin(["T5.2a", "T5.2b"])]
        # célula: 3 outcomes; município: 4; x 2 especificações x 3 cortes (0,300, 0,400, empilhado).
        self.assertEqual(len(t52), (3 + 4) * 2 * 3)
        self.assertEqual(set(t52["corte"]), {"0.300", "0.400", "empilhado"})
        self.assertTrue((t52["h"] == 0.05).all())
        t53 = self.est[(self.est["especificacao"] == "T5.3") & (self.est["tipo_termo"] == "modelo")]
        self.assertEqual(sorted(t53["outcome"]), ["n_celulas_c1", "n_celulas_c2", "vagas_c1", "vagas_c2"])
        for etapa, var in (("E1", "principal"), ("E2", "principal"), ("E1", "presenca_municipio")):
            sub = self.est[(self.est["especificacao"] == "T5.1c") & (self.est["etapa"] == etapa)
                           & (self.est["variante"] == var)]
            self.assertIn("ivs", set(sub["termo"]))
            self.assertTrue({"municipio", "capacidade_pre", "producao_pre", "escassez_regional", "ivs"}
                            <= set(sub.loc[sub["tipo_termo"] == "bloco", "bloco"]))

    def test_efeito_por_dp_e_contribuicao_coerentes(self) -> None:
        c = self.est[(self.est["especificacao"] == "T5.1c") & (self.est["tipo_termo"] == "continua")]
        np.testing.assert_allclose(c["estimativa_por_dp"], c["estimativa"] * c["dp_termo"], rtol=1e-10)
        b = self.est[self.est["tipo_termo"] == "bloco"]
        np.testing.assert_allclose(b["contribuicao_bloco"], b["pseudo_r2"] - b["pseudo_r2_sem_bloco"], atol=1e-12)
        t53 = self.est[(self.est["especificacao"] == "T5.3") & (self.est["tipo_termo"] == "continua")]
        np.testing.assert_allclose(t53["estimativa_por_dp"], np.exp(t53["coef"] * t53["dp_termo"]), rtol=1e-10)

    def test_bky_so_no_t52_do_protocolo(self) -> None:
        m = self.est["entra_bky"].astype(bool)
        self.assertTrue(self.est.loc[m, "especificacao"].isin(["T5.2a", "T5.2b"]).all())
        self.assertTrue(self.est.loc[m, "no_protocolo"].astype(bool).all())
        self.assertTrue(self.est.loc[~m, "q_bky"].isna().all())
        np.testing.assert_allclose(self.est.loc[m, "q_bky"], L.qvalores_bky(self.est.loc[m, "p_valor"].to_numpy()))

    def test_ausencias_e_populacoes(self) -> None:
        c = self.resumo["contagens"]["celulas"]
        g3 = pd.read_parquet(OUT / "outcomes" / "outcomes_G3_municipio.parquet")
        self.assertEqual(c["municipios_que_constam"], int(g3["f0_3a_consta_do_resultado_final_adesao"].sum()))
        self.assertEqual(c["municipios_cardapio"], len(g3))
        e1 = self.resumo["modelos"]["T5.1a|E1|principal"]
        self.assertEqual(e1["n_entrada"], c["celulas_em_municipios_que_constam"])
        e2 = self.resumo["modelos"]["T5.1b|E2|principal"]
        self.assertEqual(e2["n_entrada"], c["celulas_pedidas"])
        # Cursos fora da ponte: vínculos do curso ausentes (não zero) e contados na amostra principal.
        self.assertGreaterEqual(e1["descartadas_por_covariavel_ausente"]["vinc_curso_10k"], 1)
        self.assertEqual(set(c["cursos_fora_da_ponte"]) & set(range(1, 17)), set())
        t52 = self.est[(self.est["especificacao"] == "T5.2a") & (self.est["outcome"] == "E1_pedida")
                       & (self.est["corte"] == "empilhado")].iloc[0]
        self.assertLessEqual(int(t52["n_obs"]), c["celulas_em_municipios_que_constam"])

    def test_janelas_do_cnes_e_do_sia(self) -> None:
        for chave in ("cnes_pre", "sia_pre"):
            comps = self.resumo[chave]["competencias"]
            self.assertEqual((comps[0], comps[-1], len(comps)), ("202406", "202506", 13), chave)
            self.assertTrue(all(c < "202609" for c in comps))

    def test_hashes_das_entradas_e_saidas(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
            self.assertNotIn("ivs_ipea_2010_municipios", e["caminho"])
        self.assertEqual(sha256(EST), self.resumo["saidas"]["P5_estimativas.csv"]["sha256"])
        self.assertEqual(self.resumo["protocolo"]["sha256"], sha256(ROOT / self.resumo["protocolo"]["arquivo"]))

    def test_figuras_existem_e_titulos_batem_com_o_csv(self) -> None:
        figs = self.resumo["saidas"]["figuras"]
        self.assertEqual({Path(f["arquivo"]).name for f in figs}, set(P5.DESCRICAO_FIGURAS))
        for f in figs:
            caminho = ROOT / f["arquivo"]
            self.assertTrue(caminho.exists() and caminho.stat().st_size > 10_000, f["arquivo"])
            self.assertEqual(caminho.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(sha256(caminho), f["sha256"])
            for p in f.get("paineis", []):
                s = self.est[(self.est["especificacao"] == p["especificacao"])
                             & (self.est["unidade_analise"] == p["unidade_analise"])
                             & (self.est["outcome"] == p["outcome"]) & (self.est["corte"] == p["corte"])]
                self.assertEqual(len(s), 1, p)
                for k_csv, k_fig in (("estimativa", "tau"), ("ic95_inf", "ic95_inf"), ("ic95_sup", "ic95_sup"),
                                     ("p_valor", "p_valor")):
                    self.assertAlmostEqual(float(s.iloc[0][k_csv]), p[k_fig], places=12)

    def test_como_ler_nas_figuras(self) -> None:
        for nome in ("COMO_LER_AME", "COMO_LER_BLOCOS", "COMO_LER_T52_MUN", "COMO_LER_T52_CEL", "COMO_LER_T53"):
            texto = getattr(P5, nome)
            self.assertTrue(texto.startswith("COMO LER."), nome)
            self.assertIn("EMPIRICO", texto)
        self.assertIn("descritivo", P5.COMO_LER_AME)
        self.assertIn("pacote do corte", P5.COMO_LER_T52_MUN)


class TestRecalculoIndependente(unittest.TestCase):
    """Recalcula com o statsmodels o logit do E2 e o Poisson do T5.3 (ciclo 1, células) a partir das bases do script."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(EST, dtype={"corte": str, "ciclo": str})
        cls.dados = P5.carregar()

    def test_logit_e2_igual_ao_statsmodels(self) -> None:
        import statsmodels.api as sm
        cel = self.dados["cel"]
        base = cel[cel["priorizada"].notna()].dropna(subset=[c["col"] for c in P5.COVS_CELULA])
        r = P5.ajustar_glm(base, "priorizada", P5.COVS_CELULA, "curso", "logit")
        m = sm.Logit(r["y"], r["X"]).fit(disp=0, cov_type="cluster",
                                         cov_kwds={"groups": pd.factorize(r["d"]["co_ibge"])[0]})
        csv = self.est[(self.est["especificacao"] == "T5.1b") & (self.est["variante"] == "principal")
                       & ~self.est["tipo_termo"].isin(["modelo"])].set_index("termo")
        for j, nome in enumerate(r["nomes"]):
            if nome == "const" or nome.startswith("ef["):
                continue
            self.assertAlmostEqual(float(csv.at[nome, "coef"]), float(m.params[j]), places=7, msg=nome)
            self.assertAlmostEqual(float(csv.at[nome, "ep_coef"]), float(m.bse[j]), places=6, msg=nome)
        self.assertEqual(int(csv["n_obs"].iloc[0]), len(r["y"]))

    def test_poisson_t53_igual_ao_statsmodels(self) -> None:
        import statsmodels.api as sm
        u = self.dados["u"].dropna(subset=[c["col"] for c in P5.COVS_MUN])
        X, nomes, _ = P5.desenho(u, P5.COVS_MUN, None)
        m = sm.GLM(u["n_celulas_c1"].to_numpy(float), X, family=sm.families.Poisson()).fit(cov_type="HC0")
        fator = np.sqrt(len(u) / (len(u) - X.shape[1]))   # HC1 = HC0 x n/(n-k)
        csv = self.est[(self.est["especificacao"] == "T5.3") & (self.est["outcome"] == "n_celulas_c1")
                       & self.est["tipo_termo"].isin(["continua", "binaria", "nivel"])].set_index("termo")
        for j, nome in enumerate(nomes[1:], start=1):
            self.assertAlmostEqual(float(csv.at[nome, "coef"]), float(m.params[j]), places=6, msg=nome)
            self.assertAlmostEqual(float(csv.at[nome, "ep_coef"]), float(m.bse[j]) * fator, places=5, msg=nome)

    def test_rdd_celula_igual_a_rdd_lib_direta(self) -> None:
        cel = self.dados["cel"]
        d = cel[cel["pedida"].notna() & cel["s_mil"].notna()]
        partes = [d.assign(c=c, g=str(c)) for c in P5.CORTES]
        a = pd.concat(partes, ignore_index=True)
        r = L.rd_empilhado(a["s_mil"].to_numpy(float), a["pedida"].to_numpy(float), a["c"].to_numpy(float),
                           grupo=a["g"].to_numpy(), h_mil=50, cluster=a["co_ibge"].to_numpy(),
                           efeitos_fixos=a["curso"].to_numpy())
        s = self.est[(self.est["especificacao"] == "T5.2a") & (self.est["outcome"] == "E1_pedida")
                     & (self.est["corte"] == "empilhado")].iloc[0]
        self.assertAlmostEqual(float(s["estimativa"]), r["tau"], places=12)
        self.assertAlmostEqual(float(s["ep"]), r["ep"], places=12)


class TestDoc57e(unittest.TestCase):
    def test_blocos_iguais_aos_gerados(self) -> None:
        est, resumo = P5.ler_saidas()
        geradas = P5.gerar_tabelas_doc(est, resumo)
        no_doc = P5.tabelas_no_doc(DOC.read_text(encoding="utf-8"))
        self.assertEqual(set(no_doc), set(geradas))
        for nome, corpo in no_doc.items():
            self.assertEqual(corpo, geradas[nome], nome)

    def test_prosa_sem_numero_de_resultado(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        texto = P5.MARCA.sub("", texto)
        texto = re.sub(r"`[^`]*`", "", texto)
        texto = re.sub(r"\]\([^)]*\)", "]", texto)
        texto = re.sub(r"(?m)^#+ .*$", "", texto)
        texto = re.sub(r"§+\s?\d+", "", texto)
        texto = re.sub(r"\b(?:docs?|protocolo|seção|auditoria)\s+\d+", "", texto)
        texto = re.sub(r"\b[A-Za-z_]+\d+[a-z]?\b", "", texto)
        texto = re.sub(r"\d{2}/\d{2}/\d{4}", "", texto)
        texto = re.sub(r"\d+ª", "", texto)
        decimais = set(re.findall(r"(?<![\w.,])[−+-]?\d+[,.]\d+", texto))
        self.assertEqual(decimais - {"0,050", "0,300", "0,400"}, set())
        sem_dec = re.sub(r"(?<![\w.,])[−+-]?\d+[,.]\d+", "", texto)
        inteiros = set(re.findall(r"(?<![\w.,])[−+-]?\d+(?![\w.,]\d)", sem_dec))
        self.assertEqual(inteiros - {"1", "2", "3"}, set())

    def test_linguagem_descritiva(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        leitura = P5.tabelas_no_doc(texto)["leitura"]
        self.assertIn("associad", leitura)
        self.assertIn("critério oficial de priorização não é publicado", leitura)
        self.assertIn("pacote do corte", leitura)
        # A regra do protocolo citada como proibição ('nunca "o Ministério escolhe por causa de"') não conta.
        sem_regra = texto.replace('nunca "o Ministério escolhe por causa de"', "")
        for proibida in ("por causa de", "causa o", "causou", "o Ministério escolhe porque", "efeito causal"):
            self.assertNotIn(proibida, sem_regra)
        self.assertIn("descritiv", texto)


if __name__ == "__main__":
    unittest.main()
