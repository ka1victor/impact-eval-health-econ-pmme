"""Testes do E9 (escolha revelada dos candidatos, `scripts/rdd_bolsa/16_estimar_E9_escolha.py`).

Duas partes:
1. `TestE9Sintetico*`: dados SINTÉTICOS, gerados em memória com semente fixa,
   nunca gravados. Células, IVS, atributos e escolhas são fictícios, com
   coeficientes conhecidos por construção. Verificam que o estimador recupera
   o coeficiente da bolsa com os controles de spline, que a verossimilhança é a
   mesma do `ConditionalLogit` do statsmodels (condicional e explodido), que o
   spline é contínuo nos nós e que o efeito sobre a probabilidade bate com o
   recálculo direto.
2. `TestE9SaidasEmpiricas`: invariantes das saídas EMPÍRICAS gravadas em
   `output/rdd_bolsa/`: todas as especificações presentes, nenhum NaN sem
   nota, contagens iguais às do dicionário da tarefa B, hashes das entradas e
   do protocolo, tabelas do doc 42 iguais às regeneradas a partir dos CSVs.
   Os alvos vêm de arquivos de `output/`, nunca digitados.
"""

from __future__ import annotations

import importlib.util
import json
import math
import re
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "16_estimar_E9_escolha.py"
SPEC = importlib.util.spec_from_file_location("e9_escolha", SCRIPT)
E9 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E9)

SEMENTE = 20261018
DOC = ROOT / "docs" / "06_execucao" / "42_resultados_E9_escolha.md"
MARCA_INI = "<!-- E9_TABELAS_INICIO -->"
MARCA_FIM = "<!-- E9_TABELAS_FIM -->"


# --------------------------------------------------------------------------
# Gerador sintético (só em memória)
# --------------------------------------------------------------------------

def dgp_sintetico(rng: np.random.Generator, n_conj: int = 24, n_cel: int = 70, n_cand: int = 9000,
                  beta: float = 0.10, degraus: tuple[float, float] | None = None, com_2a: bool = False):
    """Conjunto e escolhas SINTÉTICOS no formato das tabelas da tarefa B (só em memória).

    Utilidade: beta·bolsa (ou degraus) + spline linear contínuo + atributos, com choque Gumbel.
    """
    linhas = []
    for c in range(n_conj):
        for j in range(n_cel):
            s = float(rng.integers(100, 701))
            vagas = float(rng.integers(0, 4))
            linhas.append({"ciclo": 9, "id_conjunto_escolha": f"sint_c{c:02d}", "cod_curso": c,
                           "co_cnes_7d": f"S{c:02d}{j:04d}", "s_mil": s,
                           "bolsa_mil": 20.0 if s > 400 else (15.0 if s > 300 else 10.0),
                           "faixa_anunciada": "FAIXA 1" if s > 400 else ("FAIXA 2" if s > 300 else "FAIXA 3"),
                           "tem_vaga_imediata": int(vagas > 0), "vagas_imediatas": vagas,
                           "log_vagas_imediatas_mais_1": math.log(vagas + 1.0),
                           "populacao_2022": float(np.exp(rng.normal(10.5, 1.2))),
                           "macrorregiao": rng.choice(["NORTE", "SUDESTE", "SUL"]),
                           "estrato_territorial": rng.choice(["capital", "interior_remoto"])})
    conj = pd.DataFrame(linhas)
    sp = E9.base_spline(conj["s_mil"].to_numpy(), 1)
    v = (-0.30 * sp["ivs_inclinacao"] + 0.20 * sp["ivs_mudanca_inclinacao_0300"]
         - 0.25 * sp["ivs_mudanca_inclinacao_0400"]).to_numpy()
    if degraus is None:
        v = v + beta * conj["bolsa_mil"].to_numpy()
    else:
        v = v + degraus[0] * (conj["bolsa_mil"] >= 15) + degraus[1] * (conj["bolsa_mil"] >= 20)
    v = v + 0.5 * conj["tem_vaga_imediata"] + 0.3 * conj["log_vagas_imediatas_mais_1"] \
        + 0.2 * np.log(conj["populacao_2022"]) - 0.4 * (conj["macrorregiao"] == "NORTE") \
        - 0.3 * (conj["estrato_territorial"] == "interior_remoto")
    v = np.asarray(v, dtype=float)
    cand = []
    grupos = conj.groupby("id_conjunto_escolha").indices
    nomes = sorted(grupos)
    for i in range(n_cand):
        g = nomes[i % len(nomes)]
        idx = grupos[g]
        u = v[idx] + rng.gumbel(size=len(idx))
        ordem = idx[np.argsort(-u)]
        for posto in ((1, 2) if com_2a else (1,)):
            r = conj.iloc[ordem[posto - 1]]
            cand.append({"ciclo": 9, "id_candidato": f"sint_{i:05d}", "cod_curso": r.cod_curso,
                         "opcao_rank": posto, "id_conjunto_escolha": g, "co_cnes_7d": r.co_cnes_7d,
                         "celula_com_vaga_imediata": float(r.tem_vaga_imediata)})
    return conj, pd.DataFrame(cand)


class TestE9SinteticoRecuperacao(unittest.TestCase):
    """Dados sintéticos: o logit condicional com spline recupera a bolsa conhecida."""

    @classmethod
    def setUpClass(cls) -> None:
        rng = np.random.default_rng(SEMENTE)
        cls.beta = 0.10
        cls.conj, cls.cand = dgp_sintetico(rng, beta=cls.beta, com_2a=True)
        cls.macros = sorted(cls.conj["macrorregiao"].unique())
        cls.estratos = sorted(cls.conj["estrato_territorial"].unique())

    def _estimar(self, modelo: str, espec: str) -> dict:
        r = E9.estimar(self.conj, self.cand, modelo, "principal", espec, self.macros, self.estratos)
        self.assertTrue(r["ok"], r.get("nota"))
        return r

    def test_recupera_bolsa_linear_condicional(self) -> None:
        r = self._estimar(E9.MODELO_COND, "spline_linear__bolsa_linear")
        k = r["termos"].index("bolsa_mil")
        ep = math.sqrt(r["V_mle"][k, k])
        self.assertLess(abs(r["theta"][k] - self.beta), 3 * ep)
        self.assertLess(ep, 0.04)

    def test_recupera_bolsa_linear_explodido_e_mais_preciso(self) -> None:
        rc = self._estimar(E9.MODELO_COND, "spline_linear__bolsa_linear")
        re_ = self._estimar(E9.MODELO_EXPL, "spline_linear__bolsa_linear")
        k = re_["termos"].index("bolsa_mil")
        ep = math.sqrt(re_["V_mle"][k, k])
        self.assertLess(abs(re_["theta"][k] - self.beta), 3 * ep)
        self.assertLess(ep, math.sqrt(rc["V_mle"][k, k]))

    def test_variante_quadratica_tambem_recupera(self) -> None:
        r = self._estimar(E9.MODELO_COND, "spline_quadratico__bolsa_linear")
        k = r["termos"].index("bolsa_mil")
        self.assertLess(abs(r["theta"][k] - self.beta), 3 * math.sqrt(r["V_mle"][k, k]))

    def test_degraus_iguais_quando_dgp_tem_degraus_iguais(self) -> None:
        r = self._estimar(E9.MODELO_COND, "spline_linear__degraus_por_corte")
        linhas = pd.DataFrame(E9.linhas_estimativas("sint", r)).set_index("termo")
        for t in ("degrau_0300", "degrau_0400"):
            self.assertLess(abs(linhas.loc[t, "coef"] - 5 * self.beta), 3 * linhas.loc[t, "ep_mle"])
        self.assertIn("teste_igualdade_degraus_0300_menos_0400", linhas.index)

    def test_efeito_marginal_tem_sinal_e_ordem_de_grandeza(self) -> None:
        r = self._estimar(E9.MODELO_COND, "spline_linear__bolsa_linear")
        ef = pd.DataFrame(E9.linhas_efeitos("sint", r)).set_index("quantidade")
        rc = ef.loc["razao_chances_por_5mil"]
        self.assertTrue(rc["ic95_inf"] < math.exp(5 * self.beta) < rc["ic95_sup"])
        self.assertGreater(ef.loc["variacao_prob_media_pp", "estimativa"], 0)
        self.assertTrue(np.isfinite(ef.loc["variacao_prob_media_pp", "ep_cluster_conjunto"]))


class TestE9SinteticoDegrausDiferentes(unittest.TestCase):
    """Dados sintéticos com degraus diferentes: o teste de igualdade rejeita."""

    def test_rejeita_igualdade(self) -> None:
        rng = np.random.default_rng(SEMENTE + 1)
        conj, cand = dgp_sintetico(rng, n_cand=12000, degraus=(0.0, 1.0))
        r = E9.estimar(conj, cand, E9.MODELO_COND, "principal", "spline_linear__degraus_por_corte",
                       sorted(conj["macrorregiao"].unique()), sorted(conj["estrato_territorial"].unique()))
        teste = [x for x in E9.linhas_estimativas("sint", r) if x["termo"].startswith("teste_igualdade")][0]
        self.assertLess(teste["p"], 0.01)
        self.assertLess(teste["coef"], 0)


def _long(X: np.ndarray, conj: np.ndarray, esc: np.ndarray, exc: np.ndarray) -> pd.DataFrame:
    rows = []
    for g, (c, e) in enumerate(zip(esc, exc)):
        for j in np.flatnonzero(conj == conj[c]):
            if j == e:
                continue
            rows.append((g, int(j == c), *X[j]))
    return pd.DataFrame(rows, columns=["g", "y"] + [f"x{k}" for k in range(X.shape[1])])


class TestE9SinteticoEquivalenciaStatsmodels(unittest.TestCase):
    """Dados sintéticos pequenos: mesma verossimilhança, coeficientes e EP de MV do ConditionalLogit."""

    @classmethod
    def setUpClass(cls) -> None:
        from statsmodels.discrete.conditional_models import ConditionalLogit

        cls.CL = ConditionalLogit
        rng = np.random.default_rng(SEMENTE + 2)
        cls.conj = np.repeat(np.arange(4), [5, 8, 4, 6])
        cls.X = rng.normal(size=(len(cls.conj), 3))
        theta = np.array([0.8, -0.5, 0.3])
        esc, exc = [], []
        for g in range(400):
            idx = np.flatnonzero(cls.conj == g % 4)
            o = idx[np.argsort(-(cls.X[idx] @ theta + rng.gumbel(size=len(idx))))]
            esc += [o[0], o[1]]
            exc += [-1, o[0]]
        cls.esc, cls.exc = np.array(esc), np.array(exc)

    def _comparar(self, esc: np.ndarray, exc: np.ndarray) -> None:
        fit = E9.ajustar_logit(self.X, self.conj, esc, exc)
        self.assertTrue(fit["convergiu"])
        L = _long(self.X, self.conj, esc, exc)
        cols = [c for c in L.columns if c.startswith("x")]
        m = self.CL(L["y"], L[cols], groups=L["g"]).fit(method="bfgs", maxiter=5000, gtol=1e-12, disp=0)
        # Mesma função: a verossimilhança do statsmodels avaliada no nosso ótimo é a nossa.
        self.assertAlmostEqual(fit["ll"], float(m.model.loglike(fit["theta"])), places=8)
        self.assertGreaterEqual(fit["ll"], m.llf - 1e-8)
        np.testing.assert_allclose(fit["theta"], m.params.to_numpy(), rtol=1e-4, atol=1e-5)
        ep_sm = np.sqrt(np.diag(np.linalg.inv(-m.model.hessian(fit["theta"]))))
        np.testing.assert_allclose(np.sqrt(np.diag(np.linalg.inv(fit["info"]))), ep_sm, rtol=1e-6)
        np.testing.assert_allclose(fit["scores"].sum(axis=0), m.model.score(fit["theta"]), atol=1e-8)

    def test_condicional(self) -> None:
        so1 = self.exc < 0
        self._comparar(self.esc[so1], self.exc[so1])

    def test_explodido(self) -> None:
        self._comparar(self.esc, self.exc)

    def test_cluster_por_grupo_unitario_e_sanduiche_robusto(self) -> None:
        fit = E9.ajustar_logit(self.X, self.conj, self.esc, self.exc)
        inv = np.linalg.inv(fit["info"])
        V, G = E9.covariancia_cluster(inv, fit["scores"], np.arange(len(self.esc)))
        s = fit["scores"]
        np.testing.assert_allclose(V, G / (G - 1) * inv @ (s.T @ s) @ inv, rtol=1e-12)


class TestE9SinteticoSplineEEfeito(unittest.TestCase):
    """Dados sintéticos: spline sem salto nos nós e efeito sobre a probabilidade."""

    def test_spline_continuo_nos_nos(self) -> None:
        for grau in (1, 2):
            for c in E9.CORTES_MIL:
                a = E9.base_spline(np.array([c - 1e-9]), grau).to_numpy()
                b = E9.base_spline(np.array([c + 1e-9]), grau).to_numpy()
                self.assertLess(np.max(np.abs(a - b)), 1e-8)

    def test_bolsa_nao_esta_no_espaco_do_spline(self) -> None:
        s = np.arange(100, 701, dtype=float)
        bolsa = np.where(s > 400, 20.0, np.where(s > 300, 15.0, 10.0))
        for grau in (1, 2):
            B = E9.base_spline(s, grau).to_numpy()
            B = np.column_stack([np.ones(len(s)), B])
            coef, *_ = np.linalg.lstsq(B, bolsa, rcond=None)
            self.assertGreater(np.abs(bolsa - B @ coef).max(), 0.5)

    def test_efeito_probabilidade_igual_ao_recalculo(self) -> None:
        rng = np.random.default_rng(SEMENTE + 3)
        conj = np.repeat(np.arange(3), [4, 6, 5])
        X = rng.normal(size=(len(conj), 2))
        theta = np.array([0.4, -0.7])
        esc = np.array([0, 1, 5, 6, 7, 12, 13, 10])  # candidatos por conjunto: 2, 4, 2
        dv = 0.6
        ef = E9.efeito_probabilidade(theta, X, conj, esc, dv)
        difs, ps = [], []
        for c in esc:
            idx = np.flatnonzero(conj == conj[c])
            v = X[idx] @ theta
            p = np.exp(v) / np.exp(v).sum()
            for k in range(len(idx)):
                v1 = v.copy()
                v1[k] += dv
                difs.append(np.exp(v1[k]) / np.exp(v1).sum() - p[k])
                ps.append(p[k])
        self.assertAlmostEqual(ef["variacao_prob_media"], float(np.mean(difs)), places=12)
        self.assertAlmostEqual(ef["prob_media_base"], float(np.mean(ps)), places=12)

    def test_faixa_pela_regra_corte_no_lado_inferior(self) -> None:
        r = E9.faixa_pela_regra(np.array([299.0, 300.0, 301.0, 400.0, 401.0]))
        self.assertEqual(list(r), ["FAIXA 3", "FAIXA 3", "FAIXA 2", "FAIXA 2", "FAIXA 1"])


# --------------------------------------------------------------------------
# Saídas empíricas
# --------------------------------------------------------------------------

class TestE9SaidasEmpiricas(unittest.TestCase):
    """Invariantes das saídas EMPÍRICAS do E9 gravadas em output/rdd_bolsa/."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(E9.OUT_ESTIMATIVAS, dtype={"ciclo": str})
        cls.efe = pd.read_csv(E9.OUT_EFEITOS, dtype={"ciclo": str})
        cls.resumo = json.loads(E9.OUT_RESUMO.read_text(encoding="utf-8"))
        cls.dic = json.loads(E9.DICIONARIO.read_text(encoding="utf-8"))

    def test_natureza_empirica(self) -> None:
        self.assertEqual(set(self.est["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(self.efe["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")

    def test_todas_as_especificacoes_presentes(self) -> None:
        for ciclo in E9.CICLOS:
            for modelo, conjunto in E9.COMBINACOES:
                for espec, (_, forma) in E9.ESPECIFICACOES.items():
                    sel = self.est[(self.est.ciclo == ciclo) & (self.est.modelo == modelo) &
                                   (self.est.conjunto == conjunto) & (self.est.especificacao == espec)]
                    termos = set(sel["termo"])
                    esperados = {"bolsa_mil"} if forma == "linear" else {
                        "degrau_0300", "degrau_0400", "teste_igualdade_degraus_0300_menos_0400"}
                    self.assertTrue(esperados <= termos, (ciclo, modelo, conjunto, espec))
                    self.assertTrue(set(E9.base_spline(np.array([350.0]), E9.ESPECIFICACOES[espec][0]).columns) <= termos)
                    self.assertTrue(sel["convergiu"].all())
                    self.assertTrue((sel["no_protocolo"] == True).all())  # noqa: E712
        self.assertEqual(self.resumo["n_modelos"], len(E9.CICLOS) * len(E9.COMBINACOES) * len(E9.ESPECIFICACOES))
        self.assertEqual(self.resumo["n_modelos_ok"], self.resumo["n_modelos"])

    def test_nenhum_nan_sem_nota(self) -> None:
        cols = ["coef", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "p"]
        sem = self.est[self.est[cols].isna().any(axis=1) & self.est["nota"].isna()]
        self.assertEqual(len(sem), 0)
        sem = self.efe[self.efe["estimativa"].isna() & self.efe["nota"].isna()]
        self.assertEqual(len(sem), 0)
        nan_ep = self.efe[self.efe["ep_cluster_conjunto"].isna()]
        self.assertTrue((nan_ep["quantidade"] == "prob_media_base_pp").all())
        self.assertTrue(nan_ep["nota"].notna().all())

    def test_contagens_iguais_ao_dicionario(self) -> None:
        casamento = self.dic["casamento_entre_arquivos"]["escolhas_E9_celula_escolhida_contra_quadro"]
        retiradas = pd.DataFrame(self.resumo["alternativas_retiradas"]["principal"])
        base = self.est[(self.est.modelo == E9.MODELO_COND) & (self.est.conjunto == "principal") &
                        (self.est.especificacao == "spline_linear__bolsa_linear") & (self.est.termo == "bolsa_mil")]
        base = base.set_index("ciclo")
        sens = self.est[(self.est.modelo == E9.MODELO_COND) & (self.est.conjunto == "sensibilidade") &
                        (self.est.especificacao == "spline_linear__bolsa_linear") & (self.est.termo == "bolsa_mil")]
        sens = sens.set_index("ciclo")
        tot_c = tot_a = tot_s = 0
        for k in (1, 2, 3):
            d = casamento[f"ciclo_{k}"]
            n_ret = int((retiradas["ciclo"] == k).sum()) if len(retiradas) else 0
            self.assertEqual(base.loc[str(k), "n_candidatos"], d["linhas_1a_opcao"])
            self.assertEqual(base.loc[str(k), "n_alternativas"], d["celulas_no_conjunto_principal"] - n_ret)
            self.assertEqual(sens.loc[str(k), "n_candidatos"], d["linhas_1a_opcao_no_conjunto_sensibilidade_vaga_imediata"])
            tot_c += d["linhas_1a_opcao"]
            tot_a += d["celulas_no_conjunto_principal"] - n_ret
            tot_s += d["linhas_1a_opcao_no_conjunto_sensibilidade_vaga_imediata"]
        self.assertEqual(base.loc["empilhado", "n_candidatos"], tot_c)
        self.assertEqual(base.loc["empilhado", "n_alternativas"], tot_a)
        self.assertEqual(sens.loc["empilhado", "n_candidatos"], tot_s)
        expl = self.resumo["convergencia"]
        for k in (1, 2, 3):
            dg = expl[f"{k}|{E9.MODELO_EXPL}|principal|spline_linear__bolsa_linear"]["diag_grupos"]
            d = casamento[f"ciclo_{k}"]
            sem_1a = dg["candidatos_sem_linha_de_1a_opcao_excluidos"]
            self.assertEqual(dg["grupos_posto_2"], d["linhas_2a_opcao_no_conjunto_principal"] - sem_1a)

    def test_nenhuma_alternativa_retirada_foi_escolhida(self) -> None:
        for lado in ("principal", "sensibilidade"):
            for r in self.resumo["alternativas_retiradas"][lado]:
                self.assertEqual(r["linhas_de_escolha_nessa_celula"], 0)

    def test_hashes_de_entrada_e_protocolo(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(E9.sha256_arquivo(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        prot = self.resumo["protocolo"]
        self.assertEqual(prot["sha256_texto_canonico"], prot["sha256_texto_canonico_congelado"])
        for caminho, sha in self.resumo["saidas"].items():
            self.assertEqual(E9.sha256_arquivo(ROOT / caminho), sha, caminho)
        lidos = {e["caminho"] for e in self.resumo["entradas"]}
        self.assertNotIn("data/ivs_ipea_2010_municipios.csv", lidos)
        self.assertNotIn("ivs_ipea_2010_municipios", SCRIPT.read_text(encoding="utf-8"))

    def test_conferencias(self) -> None:
        c = self.resumo["conferencias"]
        self.assertEqual(c["faixa_impressa_igual_regra_ivs_principal"]["discordantes"], 0)
        self.assertEqual(c["faixa_impressa_igual_regra_ivs_sensibilidade"]["discordantes"], 0)
        self.assertLess(max(c["spline_continuo_salto_maximo_nos_nos"].values()), 1e-6)
        self.assertTrue(c["bolsa_contra_faixa"]["bolsa_igual_faixa3_mais_5_d300_mais_5_d400"])
        mapa = self.resumo["mapa_faixa_bolsa"]["mapa_faixa_para_bolsa_mil"]
        self.assertLess(mapa["FAIXA 3"], mapa["FAIXA 2"])
        self.assertLess(mapa["FAIXA 2"], mapa["FAIXA 1"])
        self.assertEqual(mapa["FAIXA 2"] - mapa["FAIXA 3"], E9.PASSO_BOLSA_MIL)
        self.assertEqual(mapa["FAIXA 1"] - mapa["FAIXA 2"], E9.PASSO_BOLSA_MIL)

    def test_razao_de_chances_coerente_com_coeficiente(self) -> None:
        m = self.efe[(self.efe.termo == "bolsa_mil") & (self.efe.quantidade == "razao_chances_por_5mil")]
        for r in m.itertuples():
            b = self.est[(self.est.ciclo == r.ciclo) & (self.est.modelo == r.modelo) & (self.est.conjunto == r.conjunto)
                         & (self.est.especificacao == r.especificacao) & (self.est.termo == "bolsa_mil")]["coef"].iloc[0]
            self.assertAlmostEqual(r.estimativa, math.exp(5 * b), places=8)

    def test_tabelas_regeneradas_dos_csv(self) -> None:
        diag = self.resumo["diagnosticos_por_ciclo"]
        coli = self.resumo["colinearidade_principal"]
        texto = E9.tabelas_relato(self.est, self.efe, diag, coli)
        self.assertEqual(texto, E9.OUT_TABELAS.read_text(encoding="utf-8"))

    def test_doc_42_tem_as_tabelas_do_script(self) -> None:
        doc = DOC.read_text(encoding="utf-8")
        ini, fim = doc.index(MARCA_INI) + len(MARCA_INI), doc.index(MARCA_FIM)
        self.assertEqual(doc[ini:fim].strip("\n") + "\n", E9.OUT_TABELAS.read_text(encoding="utf-8"))

    def test_doc_42_sem_numero_digitado_fora_das_tabelas(self) -> None:
        """Fora do bloco gerado, decimais só podem ser parâmetros do protocolo ou números do bloco."""
        doc = DOC.read_text(encoding="utf-8")
        ini, fim = doc.index(MARCA_INI), doc.index(MARCA_FIM)
        fora = doc[:ini] + doc[fim:]
        bloco = doc[ini:fim]
        permitidos = {"0,300", "0,400", "0,3", "0,4", "0,1", "0,050"}
        no_bloco = set(re.findall(r"−?\d+,\d+", bloco))
        for n in re.findall(r"−?\d+,\d+", fora):
            self.assertTrue(n in permitidos or n in no_bloco, f"número fora das tabelas geradas: {n}")

    def test_doc_42_afirmacoes_qualitativas(self) -> None:
        """As frases do doc 42 sobre sinal e significância são conferidas aqui contra o CSV."""
        e = self.est[(self.est.modelo == E9.MODELO_COND) & (self.est.conjunto == "principal") &
                     (self.est.especificacao == "spline_linear__bolsa_linear") & (self.est.termo == "bolsa_mil")]
        e = e.set_index("ciclo")
        # "positivo e com IC 95% acima de zero no ciclo 2 e no empilhado"
        for c in ("2", "empilhado"):
            self.assertGreater(e.loc[c, "ic95_inf"], 0)
        # "nos ciclos 1 e 3 o IC 95% inclui zero"
        for c in ("1", "3"):
            self.assertLess(e.loc[c, "ic95_inf"], 0)
            self.assertGreater(e.loc[c, "ic95_sup"], 0)
        # "o EP de cluster por conjunto é maior que o de MV e o de cluster por candidato em todos os ciclos"
        self.assertTrue((e["ep_cluster_conjunto"] > e["ep_mle"]).all())
        self.assertTrue((e["ep_cluster_conjunto"] > e["ep_cluster_candidato"]).all())
        # "o coeficiente é positivo em todas as especificações de bolsa linear do empilhado"
        emp = self.est[(self.est.ciclo == "empilhado") & (self.est.termo == "bolsa_mil")]
        self.assertTrue((emp["ic95_inf"] > 0).all())
        # "com spline linear, a igualdade dos degraus é rejeitada no ciclo 3 e no empilhado; com spline quadrático,
        # não é rejeitada em nenhum ciclo nem conjunto"
        t = self.est[self.est.termo == "teste_igualdade_degraus_0300_menos_0400"]
        lin = t[(t.especificacao == "spline_linear__degraus_por_corte") & (t.modelo == E9.MODELO_COND) &
                (t.conjunto == "principal")].set_index("ciclo")
        for c in ("3", "empilhado"):
            self.assertLess(lin.loc[c, "p"], 0.05)
        quad = t[t.especificacao == "spline_quadratico__degraus_por_corte"]
        self.assertTrue((quad["p"] > 0.05).all())
        # "o degrau em 0,300 sai menor que o de 0,400" (spline linear, ciclo 3 e empilhado, todos os modelos)
        lin_todos = t[t.especificacao == "spline_linear__degraus_por_corte"]
        for c in ("3", "empilhado"):
            sel = lin_todos[lin_todos.ciclo == c]
            self.assertEqual(len(sel), len(E9.COMBINACOES))
            self.assertTrue((sel["p"] < 0.05).all())
            self.assertTrue((sel["coef"] < 0).all())
        # "com spline linear, nos ciclos 1 e 2 a igualdade não é rejeitada" (implícito na leitura)
        self.assertTrue((lin_todos[lin_todos.ciclo.isin(["1", "2"])]["p"] > 0.05).all())
        # "ciclo 3: no principal com spline linear fica perto de zero; com quadrático ou só vaga imediata, maior"
        b = self.est[(self.est.ciclo == "3") & (self.est.modelo == E9.MODELO_COND) & (self.est.termo == "bolsa_mil")]
        b = b.set_index(["conjunto", "especificacao"])["coef"]
        base3 = b[("principal", "spline_linear__bolsa_linear")]
        self.assertGreater(b[("principal", "spline_quadratico__bolsa_linear")], base3)
        self.assertGreater(b[("sensibilidade", "spline_linear__bolsa_linear")], base3)
        self.assertGreater(b[("sensibilidade", "spline_quadratico__bolsa_linear")], base3)
        self.assertLess(e.loc["3", "coef"], min(e.loc["1", "coef"], e.loc["2", "coef"]))


if __name__ == "__main__":
    unittest.main()
