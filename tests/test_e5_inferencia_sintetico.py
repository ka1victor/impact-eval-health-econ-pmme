"""Teste do E5 (inferência alternativa da RDD da bolsa) com DADOS SINTÉTICOS.

Todos os municípios, escores, covariáveis, células e outcomes deste módulo são
SINTÉTICOS: gerados em memória com semente fixa, com códigos IBGE fictícios
(prefixo 9, inexistente no IBGE) e efeitos conhecidos por construção. Nada
aqui é observação empírica. O que é gravado vai para diretórios temporários; o
próprio `executar` recusa gravar dados não empíricos em `output/` ou `data/`.

O teste verifica: (1) cada estimador recupera um salto conhecido e o EP
agrupado está calibrado; (2) o principal (S0) é idêntico ao estimador do E3;
(3) o p de Fisher é aproximadamente uniforme sob o nulo e o IC por inversão
cobre o efeito constante; (4) as fórmulas de limite unilateral e de
equivalência (TOST); (5) a regra de seleção da janela de local randomization;
(6) o pipeline grava a seleção da janela antes de ler outcomes, relata todas
as especificações e rotula as saídas.
"""

from __future__ import annotations

import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "11_inferencia_alternativa.py"
SPEC = importlib.util.spec_from_file_location("e5_inferencia_alternativa", SCRIPT)
E5 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E5)

SEMENTE = 20261018
NATUREZA = "SINTETICO_TESTE"


def escore_sintetico(n: int, rng: np.random.Generator) -> np.ndarray:
    """Escore SINTÉTICO uniforme em milésimos."""
    return rng.integers(150, 651, size=n)


class TestEstimadoresSinteticos(unittest.TestCase):
    def test_s0_igual_ao_estimador_do_e3(self) -> None:
        rng = np.random.default_rng(SEMENTE)
        s = escore_sintetico(3_000, rng)
        y = (rng.random(len(s)) < 0.3 + 0.4 * (s / 1000 - 0.15)).astype(float)
        for corte in (300, 400):
            a = E5.rd_local(s, y, corte)
            b = E5.E3.rdd_local_linear(s, y, corte, 50)
            self.assertAlmostEqual(a["tau"], b["tau"], places=12)
            self.assertAlmostEqual(a["ep"], b["ep"], places=12)
            self.assertEqual((a["n_abaixo"], a["n_acima"]), (b["n_abaixo"], b["n_acima"]))

    def test_local_constante_recupera_salto_sem_inclinacao(self) -> None:
        rng = np.random.default_rng(SEMENTE + 1)
        s = escore_sintetico(20_000, rng)
        y = 0.3 + 0.2 * (s > 300) + rng.normal(0, 0.3, len(s))
        r = E5.rd_local(s, y, 300, grau=0)
        self.assertLess(abs(r["tau"] - 0.2), 4 * r["ep"])

    def test_cortes_empilhados_recuperam_salto_comum_com_menor_ep(self) -> None:
        rng = np.random.default_rng(SEMENTE + 2)
        s = escore_sintetico(20_000, rng)
        x = s / 1000
        y = 0.2 + 1.5 * x - 2.0 * x * (s > 350) + 0.15 * (s > 300) + 0.15 * (s > 400) + rng.normal(0, 0.3, len(s))
        separados = [E5.rd_local(s, y, c) for c in (300, 400)]
        cortes = np.concatenate([np.full(len(s), 300), np.full(len(s), 400)])
        r = E5.rd_empilhado(np.concatenate([s, s]), np.concatenate([y, y]), cortes, cortes.astype(str))
        self.assertLess(abs(r["tau"] - 0.15), 4 * r["ep"])
        self.assertLess(r["ep"], min(sep["ep"] for sep in separados))

    def test_covariavel_preditiva_reduz_ep_sem_mudar_o_salto(self) -> None:
        rng = np.random.default_rng(SEMENTE + 3)
        s = escore_sintetico(10_000, rng)
        x = (s - 300) / 1000
        z = rng.normal(0, 1, len(s))
        y = 1 + 2 * x + 0.2 * (s > 300) + 1.0 * z + rng.normal(0, 0.2, len(s))
        sem = E5.rd_local(s, y, 300)
        com = E5.rd_local(s, y, 300, Z=z[:, None], nomes_z=["z_sintetica"])
        self.assertLess(abs(com["tau"] - 0.2), 4 * com["ep"])
        self.assertLess(com["ep"], 0.5 * sem["ep"])

    def test_covariavel_constante_ou_colinear_e_descartada(self) -> None:
        rng = np.random.default_rng(SEMENTE + 4)
        s = escore_sintetico(2_000, rng)
        z = rng.normal(0, 1, len(s))
        y = 0.5 + 0.1 * (s > 300) + z + rng.normal(0, 0.5, len(s))
        Z = np.column_stack([z, np.ones(len(s)), 2 * z])
        r = E5.rd_local(s, y, 300, Z=Z, nomes_z=["z", "constante", "z_dobro"])
        ref = E5.rd_local(s, y, 300, Z=z[:, None], nomes_z=["z"])
        self.assertEqual(r["covariaveis_descartadas"], "constante;z_dobro")
        self.assertAlmostEqual(r["tau"], ref["tau"], places=10)

    def test_celula_e_municipio_ponderado_por_celulas_tem_o_mesmo_ponto(self) -> None:
        rng = np.random.default_rng(SEMENTE + 5)
        n = 1_500
        s = escore_sintetico(n, rng)
        ncel = rng.integers(1, 7, size=n)
        ids = np.array([f"9{i:05d}" for i in range(n)])
        cel_ids = np.repeat(ids, ncel)
        cel_s = np.repeat(s, ncel)
        p = np.clip(0.3 + 0.2 * (cel_s > 300), 0, 1)
        cel_y = (rng.random(len(cel_s)) < p).astype(float)
        frac = pd.Series(cel_y).groupby(cel_ids).mean().reindex(ids).to_numpy()
        e0 = E5.rd_local(s, frac, 300, peso=ncel.astype(float))
        e1 = E5.rd_local(cel_s, cel_y, 300, cluster=cel_ids)
        self.assertAlmostEqual(e0["tau"], e1["tau"], places=10)
        self.assertEqual(e1["n_abaixo"], e0["n_abaixo"])
        self.assertGreater(e1["n_obs"], e1["n_abaixo"] + e1["n_acima"])

    def test_ep_agrupado_calibrado_em_monte_carlo(self) -> None:
        rng = np.random.default_rng(SEMENTE + 6)
        taus, eps = [], []
        for _ in range(200):
            n = 800
            s = rng.integers(250, 351, size=n)
            ncel = rng.integers(1, 6, size=n)
            efeito_mun = rng.normal(0, 0.15, n)  # correlação SINTÉTICA dentro do município
            cel_s = np.repeat(s, ncel)
            cel_ids = np.repeat(np.arange(n), ncel)
            p = np.clip(0.3 + 0.1 * (cel_s > 300) + np.repeat(efeito_mun, ncel), 0, 1)
            cel_y = (rng.random(len(cel_s)) < p).astype(float)
            r = E5.rd_local(cel_s, cel_y, 300, cluster=cel_ids)
            taus.append(r["tau"])
            eps.append(r["ep"])
        razao = np.mean(eps) / np.std(taus, ddof=1)
        self.assertGreater(razao, 0.85)
        self.assertLess(razao, 1.2)
        self.assertLess(abs(np.mean(taus) - 0.1), 3 * np.std(taus) / math.sqrt(len(taus)))

    def test_ciclos_empilhados_recuperam_salto_comum(self) -> None:
        rng = np.random.default_rng(SEMENTE + 7)
        partes = []
        for ciclo, (a, b) in ((1, (0.3, 1.0)), (2, (0.5, -0.5))):
            s = escore_sintetico(15_000, rng)
            x = (s - 300) / 1000
            y = (rng.random(len(s)) < np.clip(a + b * x + 0.12 * (s > 300), 0, 1)).astype(float)
            partes.append(pd.DataFrame({"s": s, "y": y, "g": f"ciclo{ciclo}", "id": [f"{ciclo}-{i}" for i in range(len(s))]}))
        d = pd.concat(partes, ignore_index=True)
        r = E5.rd_empilhado(d["s"], d["y"], np.full(len(d), 300), d["g"], cluster=d["id"], ids_municipio=d["id"])
        self.assertLess(abs(r["tau"] - 0.12), 4 * r["ep"])
        self.assertIsNotNone(r["n_clusters"])

    def test_decomposicao_reproduz_fatores_teoricos_em_desenho_uniforme(self) -> None:
        rng = np.random.default_rng(SEMENTE + 8)
        s = rng.integers(251, 350, size=200_000)
        y = 0.3 + 1.2 * (s - 300) / 1000 + rng.normal(0, 0.35, len(s))
        linhas, lados, resumo = E5.decompor_ic(s, y, np.ones(len(s)), 300)
        self.assertAlmostEqual(resumo["fator_kernel_constante"], math.sqrt(4 / 3), delta=0.03)
        self.assertAlmostEqual(resumo["fator_inclinacoes_uniforme"], 2.0, delta=0.06)
        self.assertAlmostEqual(resumo["fator_total"], math.sqrt(4.8), delta=0.08)
        ident = resumo["identidade"]
        self.assertAlmostEqual(ident["soma"], resumo["media_ponderada_acima_menos_abaixo"], places=10)
        self.assertEqual([l["componente"] for l in linhas],
                         ["DM_simples", "LC_triangular", "LL_uniforme", "LL_triangular_principal"])
        self.assertEqual([l["lado"] for l in lados], ["abaixo", "acima"])


class TestPermutacaoSintetica(unittest.TestCase):
    def test_matriz_de_permutacao_deterministica_e_com_n1_fixo(self) -> None:
        a = E5.matriz_permutacao(12, 5, 300, (SEMENTE, 1, 300, 4))
        b = E5.matriz_permutacao(12, 5, 300, (SEMENTE, 1, 300, 4))
        c = E5.matriz_permutacao(12, 5, 300, (SEMENTE, 2, 300, 4))
        self.assertTrue(np.array_equal(a, b))
        self.assertFalse(np.array_equal(a, c))
        self.assertTrue((a.sum(axis=1) == 5).all())

    def test_p_de_fisher_aproximadamente_uniforme_sob_o_nulo(self) -> None:
        rng = np.random.default_rng(SEMENTE + 9)
        ps = []
        t = np.array([False] * 15 + [True] * 15)
        for i in range(500):
            y = rng.normal(0, 1, 30)  # nulo exato SINTÉTICO: o lado não muda y
            P = E5.matriz_permutacao(30, 15, 499, (SEMENTE, 9, i, 0))
            ps.append(E5.p_fisher_dif_medias(y, t, P))
        ps = np.sort(np.array(ps))
        ks = np.max(np.abs(ps - (np.arange(1, len(ps) + 1) / len(ps))))
        self.assertLess(ks, 0.08)
        self.assertGreater(np.mean(ps <= 0.05), 0.02)
        self.assertLess(np.mean(ps <= 0.05), 0.09)
        self.assertGreater(np.mean(ps <= 0.5), 0.43)
        self.assertLess(np.mean(ps <= 0.5), 0.57)

    def test_ic_por_inversao_cobre_o_efeito_constante(self) -> None:
        rng = np.random.default_rng(SEMENTE + 10)
        t = np.array([False] * 20 + [True] * 20)
        cobre = []
        for i in range(120):
            # Efeito constante SINTÉTICO de +0,3; escala compatível com a grade [-1, +1]
            # fixada para outcomes em [0, 1].
            y = rng.normal(0, 0.25, 40) + 0.3 * t
            P = E5.matriz_permutacao(40, 20, 999, (SEMENTE, 10, i, 0))
            r = E5.inferencia_lr(y, t, P)
            self.assertFalse(r["ic_toca_borda_da_grade"])
            cobre.append(r["ic95_inf"] <= 0.3 <= r["ic95_sup"])
            self.assertLessEqual(r["ic95_inf"], r["tau"] + 0.001)
            self.assertGreaterEqual(r["ic95_sup"], r["tau"] - 0.001)
            self.assertGreaterEqual(r["lim_sup_unilateral_95"], r["tau"] - 0.001)
            self.assertLessEqual(r["lim_sup_unilateral_95"], r["ic95_sup"] + 0.001)
            self.assertGreaterEqual(r["lim_inf_unilateral_95"], r["ic95_inf"] - 0.001)
        self.assertGreater(np.mean(cobre), 0.88)

    def test_efeito_grande_e_detectado(self) -> None:
        rng = np.random.default_rng(SEMENTE + 11)
        t = np.array([False] * 25 + [True] * 25)
        y = rng.normal(0, 0.1, 50) + 1.0 * t
        P = E5.matriz_permutacao(50, 25, 999, (SEMENTE, 11, 0, 0))
        r = E5.inferencia_lr(y, t, P)
        self.assertAlmostEqual(r["p_valor"], 1 / 1000)
        self.assertGreater(r["ic95_inf"], 0.8)


class TestEquivalenciaSintetica(unittest.TestCase):
    def test_formulas_normais(self) -> None:
        r = E5.equivalencia_normal(0.0, 0.02)
        self.assertLess(r["p_tost_010"], 1e-6)
        r = E5.equivalencia_normal(0.0, 0.2)
        self.assertGreater(r["p_tost_020"], 0.1)
        r = E5.equivalencia_normal(0.15, 0.1)
        self.assertAlmostEqual(r["p_unilateral_tau_ge_015"], 0.5, places=12)
        self.assertAlmostEqual(r["lim_sup_unilateral_95"], 0.15 + 1.6448536269514722 * 0.1, places=12)
        self.assertAlmostEqual(r["mde_80"], 0.28, places=12)

    def test_tost_equivale_a_ic90_dentro_da_margem(self) -> None:
        for tau, ep in ((0.02, 0.04), (-0.05, 0.03), (0.0, 0.07), (0.08, 0.02), (-0.12, 0.05)):
            r = E5.equivalencia_normal(tau, ep)
            for d, tag in ((0.10, "010"), (0.15, "015"), (0.20, "020")):
                dentro = (tau - 1.6448536269514722 * ep > -d) and (tau + 1.6448536269514722 * ep < d)
                self.assertEqual(r[f"p_tost_{tag}"] < 0.05, dentro, (tau, ep, d))

    def test_equivalencia_por_permutacao(self) -> None:
        rng = np.random.default_rng(SEMENTE + 12)
        t = np.array([False] * 100 + [True] * 100)
        y = rng.normal(0, 0.05, 200)  # efeito nulo SINTÉTICO, pouco ruído
        P = E5.matriz_permutacao(200, 100, 999, (SEMENTE, 12, 0, 0))
        r = E5.inferencia_lr(y, t, P)
        self.assertLess(r["p_tost_010"], 0.01)
        self.assertLess(r["p_unilateral_tau_ge_010"], 0.01)
        t = np.array([False] * 4 + [True] * 4)
        y = rng.normal(0, 1.0, 8)
        P = E5.matriz_permutacao(8, 4, 999, (SEMENTE, 12, 1, 0))
        r = E5.inferencia_lr(y, t, P)
        self.assertGreater(r["p_tost_010"], 0.05)


def pop_cov_sintetica(s_mil: np.ndarray, log_pop: np.ndarray) -> pd.DataFrame:
    """População SINTÉTICA para a seleção de janela (covariáveis sem outcome)."""
    n = len(s_mil)
    return pd.DataFrame({
        "co_ibge": [f"9{i:05d}" for i in range(n)],
        "s_mil": s_mil,
        "log_populacao_2010": log_pop,
        "idhm_2010": np.full(n, 0.7),
        "estrato": ["interior_remoto"] * n,
        "regiao": ["S"] * n,
    })


class TestSelecaoJanelaSintetica(unittest.TestCase):
    def test_para_antes_do_primeiro_desequilibrio(self) -> None:
        s = np.repeat(np.arange(281, 321), 6)
        x = s - 300
        # SINTÉTICO: balanço perfeito até |x| <= 8 milésimos; salto forte fora disso.
        log_pop = 10.0 + 5.0 * ((x > 8)).astype(float)
        sel = E5.selecionar_janela(pop_cov_sintetica(s, log_pop), "P1", n_perm=999)
        escolhida = sel[sel["selecionada"]]
        self.assertEqual(len(escolhida), 1)  # 0,400 sem municípios: nenhuma janela
        self.assertAlmostEqual(escolhida.iloc[0]["w"], 0.008)
        self.assertAlmostEqual(escolhida.iloc[0]["corte"], 0.3)
        linha9 = sel[(sel["corte"] == 0.3) & (np.isclose(sel["w"], 0.009))].iloc[0]
        self.assertFalse(linha9["passa"])
        self.assertTrue((~sel[sel["corte"] == 0.4]["viavel"]).all())

    def test_janela_inviavel_nao_reprova(self) -> None:
        s = np.concatenate([np.repeat(np.arange(296, 301), 1)[:1], np.repeat(np.arange(281, 296), 4),
                            np.repeat(np.arange(305, 321), 4)])
        sel = E5.selecionar_janela(pop_cov_sintetica(s, np.full(len(s), 10.0)), "P1", n_perm=499)
        c300 = sel[sel["corte"] == 0.3]
        self.assertFalse(c300.iloc[0]["viavel"])
        self.assertTrue(c300["todas_ate_aqui_passam"].all())
        self.assertAlmostEqual(c300[c300["selecionada"]].iloc[0]["w"], 0.020)

    def test_menor_janela_reprovada_nao_deixa_janela(self) -> None:
        s = np.repeat(np.arange(281, 321), 6)
        log_pop = 10.0 + 5.0 * (s > 300) + np.random.default_rng(SEMENTE + 13).normal(0, 0.01, len(s))
        sel = E5.selecionar_janela(pop_cov_sintetica(s, log_pop), "P1", n_perm=999)
        self.assertFalse(sel["selecionada"].any())


class TestPipelineSintetico(unittest.TestCase):
    """Pipeline completo com dados SINTÉTICOS: Y1 salta +0,25 em 0,300 e nada em 0,400."""

    @classmethod
    def setUpClass(cls) -> None:
        rng = np.random.default_rng(SEMENTE + 20)
        n1, n2_novos, sobrepostos = 3_000, 2_000, 1_000
        cod1 = [f"{900000 + i:06d}" for i in range(n1)]
        cod2 = cod1[:sobrepostos] + [f"{950000 + i:06d}" for i in range(n2_novos)]
        todos = sorted(set(cod1) | set(cod2))
        s_mil = dict(zip(todos, rng.integers(150, 651, size=len(todos)).tolist()))
        escore = pd.DataFrame({"co_ibge": todos, "s_mil": [s_mil[c] for c in todos]})
        escore["ivs_admin"] = escore["s_mil"] / 1000
        faixa = {c: E5.E3.faixa_por_mil(v) for c, v in s_mil.items()}
        pops = {"P1": pd.DataFrame({"co_ibge": cod1, "faixa_anunciada": [faixa[c] for c in cod1]}),
                "P2": pd.DataFrame({"co_ibge": cod2, "faixa_anunciada": [faixa[c] for c in cod2]})}
        base = pd.DataFrame({
            "co_ibge": todos,
            "log_populacao_2010": rng.normal(10, 1, len(todos)),
            "idhm_2010": 0.85 - 0.5 * escore["ivs_admin"].to_numpy() + rng.normal(0, 0.03, len(todos)),
            "estrato": rng.choice(["capital", "metropolitano", "interior_proximo_polo", "interior_remoto"], len(todos)),
            "regiao": rng.choice(["N", "NE", "SE", "S", "CO"], len(todos)),
        })
        cov = E5.preparar_covariaveis(base)
        # Células e outcomes SINTÉTICOS.
        ncel = rng.integers(1, 7, size=n1)
        cel_mun = np.repeat(cod1, ncel)
        cel_s = np.array([s_mil[c] for c in cel_mun])
        p = np.clip(0.25 + 0.5 * (cel_s / 1000 - 0.15) + 0.25 * (cel_s > 300), 0, 1)
        celulas = pd.DataFrame({"co_ibge": cel_mun, "co_cnes_7d": [f"{i:07d}" for i in range(len(cel_mun))],
                                "cod_curso": rng.integers(1, 17, size=len(cel_mun)),
                                "y": (rng.random(len(cel_mun)) < p).astype(float)})
        agg = celulas.groupby("co_ibge")["y"].agg(["mean", "size"]).reindex(cod1)
        y1 = pd.DataFrame({"co_ibge": cod1, "y": agg["mean"].to_numpy(), "n_celulas": agg["size"].to_numpy()})

        def presenca(cods, salto):
            sv = np.array([s_mil[c] for c in cods])
            pr = np.clip(0.4 + 0.3 * (sv / 1000 - 0.15) + salto * (sv > 300), 0, 1)
            return pd.Series((rng.random(len(cods)) < pr).astype(float), index=pd.Index(cods, name="co_ibge"))

        d1, d2 = presenca(cod1, 0.20), presenca(cod2, 0.20)
        cls.tmp = tempfile.TemporaryDirectory()
        saida = Path(cls.tmp.name)
        cls.saida = saida
        cls.estado_ao_ler = []

        def leitor(m1, m2):
            cls.estado_ao_ler.append({
                "selecao_existe": (saida / E5.NOME_LR_SELECAO).exists(),
                "especificacoes_existe": (saida / E5.NOME_ESPEC).exists(),
            })
            return {"Y1": y1, "celulas": celulas, "D1": d1.loc[list(m1)], "D2": d2.loc[list(m2)],
                    "fontes": {"SINTETICO": {"sha256": "nao se aplica"}}, "verificacoes": {}}

        # Referência do S0 calculada pelo estimador do E3 (como o E3_estimativas.csv real).
        ref = []
        for oc, serie, cods in (("Y1", y1.set_index("co_ibge")["y"], cod1), ("D1", d1, cod1), ("D2", d2, cod2)):
            sv = np.array([s_mil[c] for c in cods])
            for corte in (300, 400):
                r = E5.E3.rdd_local_linear(sv, serie.loc[cods].to_numpy(), corte, 50)
                ref.append({"outcome_e5": oc, "corte": corte / 1000, "tau": r["tau"], "ep": r["ep"],
                            "n_abaixo": r["n_abaixo"], "n_acima": r["n_acima"]})
        cls.args = (escore, pops, cov, leitor)
        cls.status = E5.executar(escore, pops, cov, leitor, saida_dir=saida, natureza=NATUREZA,
                                 referencia_e3=pd.DataFrame(ref), n_perm=199)
        cls.ref = pd.DataFrame(ref)
        cls.espec = pd.read_csv(saida / E5.NOME_ESPEC)
        cls.sens = pd.read_csv(saida / E5.NOME_LR_SENS)
        cls.selecao = pd.read_csv(saida / E5.NOME_LR_SELECAO)
        cls.decomp = pd.read_csv(saida / E5.NOME_DECOMP)
        cls.lados = pd.read_csv(saida / E5.NOME_LADOS)
        cls.resumo = json.loads((saida / E5.NOME_RESUMO).read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_selecao_gravada_antes_dos_outcomes(self) -> None:
        # A primeira leitura é a da execução de setUpClass.
        self.assertEqual(self.estado_ao_ler[0], {"selecao_existe": True, "especificacoes_existe": False})
        self.assertTrue(self.resumo["selecao_janela_lr"]["gravada_antes_de_ler_outcomes"])

    def test_todas_as_especificacoes_relatadas(self) -> None:
        contagem = self.espec["especificacao"].value_counts().to_dict()
        esperado = {"S0": 6, "A": 6, "B": 3, "C1": 6, "C2": 6, "D": 6, "E0": 2, "E1": 2, "E2": 2, "F1": 2, "F2": 1}
        self.assertEqual(contagem, esperado)
        self.assertEqual(sorted(contagem), sorted(e["id"] for e in E5.ESPECIFICACOES))
        for col in ("lim_sup_unilateral_95", "p_unilateral_tau_ge_010", "p_tost_015", "p_tost_020", "mde_80"):
            self.assertIn(col, self.espec.columns)

    def test_saidas_rotuladas_como_sinteticas_e_exploratorias(self) -> None:
        for df in (self.espec, self.sens, self.selecao, self.decomp, self.lados):
            self.assertEqual(set(df["natureza_dos_dados"]), {NATUREZA})
        rot = self.espec.set_index("especificacao")["rotulo"]
        self.assertEqual(set(rot.loc["S0"]), {E5.ROTULO_S0})
        self.assertEqual(set(rot.drop("S0")), {E5.ROTULO})
        self.assertEqual(self.resumo["rotulo"], E5.ROTULO)
        self.assertEqual(self.resumo["natureza_dos_dados"], NATUREZA)

    def test_s0_conferido_contra_a_referencia(self) -> None:
        self.assertEqual(self.resumo["verificacoes"]["s0_reproduz_e3"]["linhas"], 6)
        self.assertLess(self.resumo["verificacoes"]["s0_reproduz_e3"]["max_abs_dif_tau_ep"], 1e-12)

    def test_referencia_divergente_interrompe(self) -> None:
        ref = self.ref.copy()
        ref.loc[0, "tau"] += 0.01
        escore, pops, cov, leitor = self.args
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                E5.executar(escore, pops, cov, leitor, saida_dir=Path(tmp), natureza=NATUREZA,
                            referencia_e3=ref, n_perm=19)

    def test_recupera_salto_sintetico_de_y1(self) -> None:
        e = self.espec[self.espec["outcome"] == "Y1"]
        for sid in ("S0", "C1", "C2", "E0", "E1", "E2"):
            r300 = e[(e["especificacao"] == sid) & (e["corte"].astype(str) == "0.3")].iloc[0]
            r400 = e[(e["especificacao"] == sid) & (e["corte"].astype(str) == "0.4")].iloc[0]
            self.assertLess(abs(r300["tau"] - 0.25), 4 * r300["ep"], sid)
            self.assertLess(abs(r400["tau"]), 4 * r400["ep"], sid)

    def test_e0_e_e1_tem_o_mesmo_ponto(self) -> None:
        e = self.espec
        for corte in ("0.3", "0.4"):
            a = e[(e["especificacao"] == "E0") & (e["corte"].astype(str) == corte)].iloc[0]["tau"]
            b = e[(e["especificacao"] == "E1") & (e["corte"].astype(str) == corte)].iloc[0]["tau"]
            self.assertAlmostEqual(a, b, places=10)

    def test_presenca_empilhada_recupera_salto(self) -> None:
        f1 = self.espec[(self.espec["especificacao"] == "F1") & (self.espec["corte"].astype(str) == "0.3")].iloc[0]
        self.assertLess(abs(f1["tau"] - 0.20), 4 * f1["ep"])
        self.assertGreater(f1["n_obs"], f1["n_abaixo"] + f1["n_acima"])  # municípios em P1 e P2

    def test_local_randomization_relata_todas_as_janelas_viaveis(self) -> None:
        viaveis = self.selecao[self.selecao["viavel"]]
        esperado = sum(len(viaveis[viaveis["populacao"] == p]) * k for p, k in (("P1", 2), ("P2", 1)))
        self.assertEqual(len(self.sens), esperado)
        d = self.espec[self.espec["especificacao"] == "D"]
        for _, linha in d.iterrows():
            sel = self.selecao[(self.selecao["populacao"] == linha["populacao"])
                               & np.isclose(self.selecao["corte"], float(linha["corte"]))
                               & self.selecao["selecionada"]]
            if len(sel):
                s = self.sens[(self.sens["outcome"] == linha["outcome"]) & np.isclose(self.sens["corte"], float(linha["corte"]))
                              & self.sens["selecionada"]]
                self.assertEqual(len(s), 1)
                self.assertAlmostEqual(s.iloc[0]["tau"], linha["tau"], places=12)
            else:
                self.assertTrue(np.isnan(linha["tau"]))

    def test_b_sem_municipio_em_duas_janelas(self) -> None:
        b = self.espec[self.espec["especificacao"] == "B"]
        self.assertTrue((b["municipios_em_duas_janelas"] == 0).all())
        self.assertTrue(b["inferencia"].str.contains("HC1").all())

    def test_cenarios_rotulados(self) -> None:
        for c in self.resumo["cenarios_ilustrativos_rotulados"]:
            self.assertTrue(c["rotulo"].startswith("CENARIO_ILUSTRATIVO"))

    def test_sintetico_nao_grava_em_output_nem_data(self) -> None:
        escore, pops, cov, leitor = self.args
        for destino in (ROOT / "output" / "rdd_bolsa", ROOT / "data"):
            with self.assertRaises(ValueError):
                E5.executar(escore, pops, cov, leitor, saida_dir=destino, natureza=NATUREZA, n_perm=19)


if __name__ == "__main__":
    unittest.main()
