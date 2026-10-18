"""Testes do E1 (razão de densidades laterais) com DADOS SINTÉTICOS.

Escores e contagens deste módulo são SINTÉTICOS: gerados em memória com
semente fixa, com saltos conhecidos por construção. Nada aqui é observação
empírica e nada é gravado.

Verifica, em `scripts/rdd_bolsa/05_estimar_E1_densidade.py`: (1) o Poisson
log-linear em mass points não acusa salto em densidade uniforme e detecta
massa plantada logo acima do corte; (2) recupera os parâmetros exatos quando as
contagens seguem o modelo sem ruído; (3) o corte pertence ao lado inferior;
(4) não estima quando o MLE não existe; (5) binomial exata, Clopper-Pearson e
Holm em valores conhecidos; (6) concorda com a densidade do E3, que implementa
o mesmo estimador por outro caminho.
"""

from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "05_estimar_E1_densidade.py"
SPEC = importlib.util.spec_from_file_location("e1_densidade", SCRIPT)
E1 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E1)

SCRIPT_E3 = ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py"
SPEC_E3 = importlib.util.spec_from_file_location("e3_rdd_completa_para_e1", SCRIPT_E3)
E3 = importlib.util.module_from_spec(SPEC_E3)
SPEC_E3.loader.exec_module(E3)

SEMENTE = 20261018


def contagens(s_mil) -> pd.Series:
    """Contagem SINTÉTICA de municípios por mass point de 0,001 (milésimos)."""
    return pd.Series(np.asarray(s_mil)).value_counts().sort_index()


class TestDensidadeSintetica(unittest.TestCase):
    def test_densidade_uniforme_nao_acusa_salto(self) -> None:
        rng = np.random.default_rng(SEMENTE)
        cont = contagens(rng.integers(150, 651, size=20_000))
        for corte in (300, 400):
            r = E1.ajustar_poisson(cont, corte, 50, linear=True, excluir_corte=False)
            self.assertTrue(r["estimado"], r["nota"])
            self.assertLessEqual(r["ic_inf"], 1.0, corte)
            self.assertGreaterEqual(r["ic_sup"], 1.0, corte)

    def test_densidade_uniforme_no_teste_exato(self) -> None:
        # Na escala das populações reais (P2 tem 454 municípios); ver test_binomial_no_tamanho_das_populacoes.
        rng = np.random.default_rng(SEMENTE + 4)
        cont = contagens(rng.integers(150, 651, size=3_000))
        for corte in (300, 400):
            ex = E1.teste_exato(cont, corte, 20)
            self.assertTrue(ex["estimado"])
            self.assertLessEqual(ex["ic_inf"], 1.0, corte)
            self.assertGreaterEqual(ex["ic_sup"], 1.0, corte)
            self.assertGreater(ex["p_valor"], 0.05, corte)

    def test_salto_plantado_e_detectado(self) -> None:
        rng = np.random.default_rng(SEMENTE + 1)
        base = rng.integers(150, 651, size=20_000)
        extra = rng.integers(301, 351, size=2_000)  # massa SINTÉTICA logo acima de 0,300
        cont = contagens(np.concatenate([base, extra]))
        r = E1.ajustar_poisson(cont, 300, 50, linear=True, excluir_corte=False)
        self.assertGreater(r["rho"], 1.3)
        self.assertLess(r["p_valor"], 0.001)
        self.assertGreater(r["ic_inf"], 1.0)
        # Em 0,400, longe da massa plantada, nada muda.
        r400 = E1.ajustar_poisson(cont, 400, 50, linear=True, excluir_corte=False)
        self.assertLessEqual(r400["ic_inf"], 1.0)
        self.assertGreaterEqual(r400["ic_sup"], 1.0)

    def test_salto_plantado_no_teste_exato(self) -> None:
        rng = np.random.default_rng(SEMENTE + 5)
        base = rng.integers(150, 651, size=3_000)
        extra = rng.integers(301, 321, size=150)  # massa SINTÉTICA na janela de 0,020 acima do corte
        ex = E1.teste_exato(contagens(np.concatenate([base, extra])), 300, 20)
        self.assertGreater(ex["rho"], 1.5)
        self.assertGreater(ex["ic_inf"], 1.0)
        self.assertLess(ex["p_valor"], 0.001)

    def test_recupera_parametros_sem_ruido(self) -> None:
        a, b, tau, d = math.log(40.0), 3.0, math.log(1.5), -2.0
        s = np.arange(251, 351)
        x = (s - 300) / 1000.0
        t = (s > 300).astype(float)
        cont = pd.Series(np.exp(a + b * x + tau * t + d * t * x), index=s)  # contagem esperada exata
        r = E1.ajustar_poisson(cont, 300, 50, linear=True, excluir_corte=False)
        self.assertTrue(r["estimado"], r["nota"])
        self.assertAlmostEqual(r["tau"], tau, places=8)
        self.assertAlmostEqual(r["rho"], 1.5, places=8)
        for nome, valor in zip(["a", "b", "tau", "d"], [a, b, tau, d]):
            self.assertAlmostEqual(r["coeficientes"][nome], valor, places=6, msg=nome)

    def test_corte_pertence_ao_lado_inferior(self) -> None:
        cont = pd.Series({300: 5, 301: 7})
        r = E1.ajustar_poisson(cont, 300, 50, linear=False, excluir_corte=False)
        self.assertEqual((r["n_esq"], r["n_dir"]), (5, 7))
        self.assertEqual((r["mass_points_esq"], r["mass_points_dir"]), (50, 50))
        self.assertAlmostEqual(r["rho"], 7 / 5, places=8)  # constante local: razão das contagens
        sem_corte = E1.ajustar_poisson(cont, 300, 50, linear=False, excluir_corte=True)
        self.assertEqual(sem_corte["mass_points_esq"], 49)
        self.assertFalse(sem_corte["estimado"])  # sem o mass point 0,300, o lado inferior fica vazio
        ex = E1.teste_exato(cont, 300, 20)
        self.assertEqual((ex["n_esq"], ex["n_dir"]), (5, 7))

    def test_mle_inexistente_nao_estima(self) -> None:
        vazio = E1.ajustar_poisson(pd.Series({320: 4, 330: 2}), 300, 50, linear=True, excluir_corte=False)
        self.assertFalse(vazio["estimado"])
        self.assertIn("contagem zero", vazio["nota"])
        # Contagens só no mass point extremo do lado: a inclinação do lado não tem MLE finito.
        extremo = E1.ajustar_poisson(pd.Series({251: 6, 310: 3, 320: 4}), 300, 50, linear=True,
                                     excluir_corte=False)
        self.assertFalse(extremo["estimado"])
        self.assertIn("inclinacao sem MLE finito", extremo["nota"])
        self.assertFalse(E1.teste_exato(pd.Series(dtype=float), 300, 20)["estimado"])

    def test_concorda_com_a_densidade_do_e3(self) -> None:
        rng = np.random.default_rng(SEMENTE + 2)
        s = np.concatenate([rng.integers(200, 501, size=3_000), rng.integers(301, 331, size=150)])
        for corte in (300, 400):
            e1 = E1.ajustar_poisson(contagens(s), corte, 50, linear=True, excluir_corte=False)
            e3 = E3.densidade_poisson(s, corte, 50)
            self.assertAlmostEqual(e1["tau"], e3["tau"], places=7)
            self.assertAlmostEqual(e1["ep_tau_hc0"], e3["ep"], places=7)
            self.assertEqual((e1["n_esq"], e1["n_dir"]), (e3["n_abaixo"], e3["n_acima"]))


class TestInferenciaExata(unittest.TestCase):
    def test_binomial_bicaudal(self) -> None:
        self.assertAlmostEqual(E1.binom_teste_bicaudal(10, 10), 2 / 1024, places=15)
        self.assertAlmostEqual(E1.binom_teste_bicaudal(0, 10), 2 / 1024, places=15)
        self.assertAlmostEqual(E1.binom_teste_bicaudal(5, 10), 1.0, places=12)
        # P(X <= 2) + P(X >= 8) com X ~ Bin(10, 1/2) = 2 * 56 / 1024
        self.assertAlmostEqual(E1.binom_teste_bicaudal(8, 10), 112 / 1024, places=12)

    def test_binomial_no_tamanho_das_populacoes(self) -> None:
        # binom_pmf usa math.comb em ponto flutuante e estoura acima de n ~ 1.030. As janelas
        # reais têm no máximo os 454 municípios de P2; n = 1.000 cobre essa escala com folga.
        self.assertAlmostEqual(E1.binom_teste_bicaudal(500, 1000), 1.0, places=9)
        self.assertLess(E1.binom_teste_bicaudal(600, 1000), 1e-9)

    def test_clopper_pearson(self) -> None:
        inf, sup = E1.clopper_pearson(5, 10)
        self.assertAlmostEqual(inf, 0.187086, places=5)
        self.assertAlmostEqual(sup, 0.812914, places=5)
        inf0, sup0 = E1.clopper_pearson(0, 10)
        self.assertEqual(inf0, 0.0)
        self.assertAlmostEqual(sup0, 1 - 0.025 ** (1 / 10), places=8)
        self.assertEqual(E1.clopper_pearson(10, 10)[1], 1.0)

    def test_holm(self) -> None:
        self.assertEqual(E1.holm([0.01, 0.04]), [0.02, 0.04])
        self.assertEqual(E1.holm([0.04, 0.01]), [0.04, 0.02])
        self.assertEqual(E1.holm([0.03, 0.02]), [0.04, 0.04])  # monotonia
        self.assertEqual(E1.holm([0.6, 0.7]), [1.0, 1.0])  # teto em 1

    def test_quantil_normal(self) -> None:
        self.assertAlmostEqual(E1.Z975, 1.959963984540054, places=9)
        self.assertAlmostEqual(2 * E1.phi_sup(E1.Z975), 0.05, places=12)


if __name__ == "__main__":
    unittest.main()
