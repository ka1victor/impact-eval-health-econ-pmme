"""Validação da biblioteca de sensibilidade de Rambachan–Roth (protocolo 59, parte A).

Todos os casos são SINTÉTICOS, construídos em memória e conferidos contra soluções que se fazem à mão; nada aqui
é dado observado e nada é gravado em `output/`.
"""

from __future__ import annotations

import importlib.util
import math
import sys
import unittest
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]


def _lib():
    nome = "honestdid_lib_teste"
    if nome in sys.modules:
        return sys.modules[nome]
    spec = importlib.util.spec_from_file_location(nome, ROOT / "scripts" / "rdd_bolsa" / "honestdid_lib.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


H = _lib()
Z = stats.norm.ppf(0.975)


class TestMatrizes(unittest.TestCase):
    def test_diferencas_com_referencia(self):
        # SINTÉTICO: pré e = −3, −2; pós e = 0, 1; δ = (a, b, c, d)
        F = H.primeiras_diferencas(2, 2)
        d = np.array([1.0, 2.0, 5.0, 9.0])
        # sequência aumentada: 1, 2, 0, 5, 9
        np.testing.assert_allclose(F @ d, [1.0, -2.0, 5.0, 4.0])
        S = H.segundas_diferencas(2, 2)
        np.testing.assert_allclose(S @ d, [-3.0, 7.0, -1.0])


class TestConjuntoIdentificado(unittest.TestCase):
    def test_rm_um_pre_um_pos(self):
        # SINTÉTICO: Δ^RM com um pré e um pós: θ ∈ β_pós ± M̄ |β_pré|
        for bpre, bpos, mbar in ((0.4, 2.0, 1.0), (-0.3, 1.0, 0.5), (0.0, 1.0, 2.0)):
            lo, hi = H.conjunto_identificado_rm([bpre, bpos], 1, 1, [1.0], mbar)
            self.assertAlmostEqual(lo, bpos - mbar * abs(bpre), places=8)
            self.assertAlmostEqual(hi, bpos + mbar * abs(bpre), places=8)

    def test_rm_dois_pos_media(self):
        # SINTÉTICO: um pré (β_pré = 1), dois pós, M̄ = 1: δ_0 ∈ [−1, 1], δ_1 − δ_0 ∈ [−1, 1];
        # média de δ_pós ∈ [−1,5; 1,5]
        lo, hi = H.conjunto_identificado_rm([1.0, 3.0, 3.0], 1, 2, [0.5, 0.5], 1.0)
        self.assertAlmostEqual(lo, 1.5, places=8)
        self.assertAlmostEqual(hi, 4.5, places=8)

    def test_sd_extrapola_reta(self):
        # SINTÉTICO: Δ^SD com M = 0 extrapola a reta pelo pré e pela referência: δ_0 = −β_{−2}
        lo, hi = H.conjunto_identificado_sd([0.5, 2.0], 1, 1, [1.0], 0.0)
        self.assertAlmostEqual(lo, 2.5, places=8)
        self.assertAlmostEqual(hi, 2.5, places=8)
        lo, hi = H.conjunto_identificado_sd([0.5, 2.0], 1, 1, [1.0], 0.3)
        self.assertAlmostEqual(lo, 2.2, places=8)
        self.assertAlmostEqual(hi, 2.8, places=8)

    def test_sd_vazio_quando_pre_viola(self):
        # SINTÉTICO: pré curvo (segunda diferença 2) com M = 0,5 < 2: conjunto vazio
        self.assertIsNone(H.conjunto_identificado_sd([1.0, 0.0, 0.0], 2, 1, [1.0], 0.5))


class TestFLCI(unittest.TestCase):
    def test_m_zero_um_pre_um_pos(self):
        # SINTÉTICO: v = (1, 1); IC = β_pré + β_pós ± 1,96 σ_v
        Sig = np.array([[0.04, 0.01], [0.01, 0.09]])
        r = H.flci_sd([0.5, 2.0], Sig, 1, 1, [1.0], 0.0)
        sd = math.sqrt(0.04 + 0.09 + 0.02)
        np.testing.assert_allclose(r.v, [1.0, 1.0], atol=1e-8)
        self.assertAlmostEqual(r.centro, 2.5, places=8)
        self.assertAlmostEqual(r.meio, Z * sd, places=6)

    def test_m_positivo_um_pre_um_pos(self):
        # SINTÉTICO: viés máximo = M (w = 1); meio = σ cv(M/σ)
        Sig = np.diag([0.04, 0.09])
        M = 0.2
        r = H.flci_sd([0.5, 2.0], Sig, 1, 1, [1.0], M)
        sd = math.sqrt(0.13)
        self.assertAlmostEqual(r.vies_max, M, places=8)
        self.assertAlmostEqual(r.meio, sd * H.cv_viesado(M / sd), places=6)

    def test_cv_viesado(self):
        self.assertAlmostEqual(H.cv_viesado(0.0), Z, places=8)
        # b grande: c ≈ b + 1,645
        self.assertAlmostEqual(H.cv_viesado(10.0), 10.0 + stats.norm.ppf(0.95), places=5)

    def test_meio_cresce_com_m(self):
        rng = np.random.default_rng(1)
        Araw = rng.normal(size=(6, 6))
        Sig = Araw @ Araw.T / 60 + np.eye(6) * 0.01
        beta = np.array([0.1, -0.05, 0.02, 1.0, 1.2, 1.1])
        l = np.ones(3) / 3
        meios = [H.flci_sd(beta, Sig, 3, 3, l, M).meio for M in (0.0, 0.02, 0.05, 0.1)]
        self.assertTrue(all(b >= a - 1e-8 for a, b in zip(meios, meios[1:])))

    def test_v_ortogonal_a_reta(self):
        # SINTÉTICO: o estimador do FLCI não pode ter viés sob tendência linear exata (M = 0 em Δ^SD)
        Sig = np.eye(5) * 0.01
        r = H.flci_sd(np.zeros(5), Sig, 3, 2, [0.5, 0.5], 0.1)
        e = np.array([-4, -3, -2, 0, 1], dtype=float) + 1.0   # reta que passa por zero em e = −1
        # viés de v′β̂ para l′τ quando δ = reta: v′δ
        self.assertAlmostEqual(float(r.v @ e), 0.0, places=7)
        np.testing.assert_allclose(r.v[3:], [0.5, 0.5], atol=1e-8)


class TestTesteCondicional(unittest.TestCase):
    def test_uma_desigualdade_igual_ao_z_unilateral(self):
        # SINTÉTICO: H0: E[Y] ≤ 0, sem nuisance; p = 1 − Φ(Y/σ)
        for y in (-1.0, 0.3, 1.7, 2.5):
            t = H.teste_condicional(np.array([y]), np.zeros((1, 0)), np.array([[1.0]]))
            self.assertAlmostEqual(t["p"], 1 - stats.norm.cdf(y), places=8)

    def test_igualdade_igual_ao_bilateral(self):
        # SINTÉTICO: duas desigualdades opostas (= igualdade): p = 2(1 − Φ(|y|))
        for y in (0.4, -1.2, 2.2):
            Y = np.array([y, -y])
            Sy = np.array([[1.0, -1.0], [-1.0, 1.0]])
            t = H.teste_condicional(Y, np.zeros((2, 0)), Sy)
            self.assertAlmostEqual(t["p"], 2 * (1 - stats.norm.cdf(abs(y))), places=6)

    def test_ic_rm_mbar_zero_igual_ao_ic_usual(self):
        # SINTÉTICO: M̄ = 0, um pré longe do zero: IC = β_pós ± 1,96 σ
        Sig = np.diag([0.01, 0.04])
        r = H.ic_rm([0.8, 1.0], Sig, 1, 1, [1.0], 0.0)
        self.assertAlmostEqual(r["ic_inf"], 1.0 - Z * 0.2, places=3)
        self.assertAlmostEqual(r["ic_sup"], 1.0 + Z * 0.2, places=3)

    def test_ic_rm_contem_conjunto_identificado_e_cresce(self):
        rng = np.random.default_rng(3)
        Araw = rng.normal(size=(5, 5))
        Sig = Araw @ Araw.T / 50 + np.eye(5) * 0.02
        beta = np.array([0.2, -0.1, 0.15, 1.0, 1.3])
        l = np.array([0.5, 0.5])
        larg = []
        for mbar in (0.0, 0.5, 1.0):
            r = H.ic_rm(beta, Sig, 3, 2, l, mbar)
            idset = H.conjunto_identificado_rm(beta, 3, 2, l, mbar)
            self.assertLessEqual(r["ic_inf"], idset[0] + 1e-6)
            self.assertGreaterEqual(r["ic_sup"], idset[1] - 1e-6)
            larg.append(r["ic_sup"] - r["ic_inf"])
        self.assertTrue(larg[0] <= larg[1] + 1e-6 <= larg[2] + 2e-6)

    def test_cobertura_monte_carlo(self):
        # SINTÉTICO: δ verdadeiro em Δ^RM(1) (pré com tendência, pós continua com variação igual), θ = 1;
        # cobertura do IC de Δ^RM(1) ≥ 0,93 em 400 réplicas
        rng = np.random.default_rng(20261025)
        T_pre, T_post = 2, 2
        delta = np.array([-0.2, -0.1, 0.1, 0.2])     # variações consecutivas de 0,1 no pré e no pós
        tau = np.array([1.0, 1.0])
        beta0 = delta + np.concatenate([np.zeros(T_pre), tau])
        Sig = np.eye(4) * 0.05 ** 2
        l = np.array([0.5, 0.5])
        cobre = 0
        n = 400
        for _ in range(n):
            b = rng.multivariate_normal(beta0, Sig)
            r = H.ic_rm(b, Sig, T_pre, T_post, l, 1.0, n_grade=21, iter_bissecao=8)
            cobre += int(r["ic_inf"] <= 1.0 <= r["ic_sup"])
        self.assertGreaterEqual(cobre / n, 0.93)

    def test_cobertura_monte_carlo_flci(self):
        # SINTÉTICO: δ com segunda diferença 0,02 em todo ponto (curva), M = 0,02; cobertura ≥ 0,93
        rng = np.random.default_rng(7)
        T_pre, T_post = 3, 2
        es = np.array([-4, -3, -2, 0, 1], dtype=float)
        delta = 0.01 * ((es + 1) ** 2)                   # segunda diferença 0,02; zero em e = −1
        tau = np.array([0.5, 0.5])
        beta0 = delta + np.concatenate([np.zeros(T_pre), tau])
        Sig = np.eye(5) * 0.05 ** 2
        l = np.array([0.5, 0.5])
        cobre, n = 0, 400
        for _ in range(n):
            b = rng.multivariate_normal(beta0, Sig)
            lo, hi = H.flci_sd(b, Sig, T_pre, T_post, l, 0.02).ic
            cobre += int(lo <= 0.5 <= hi)
        self.assertGreaterEqual(cobre / n, 0.93)


class TestHibrido(unittest.TestCase):
    def test_hibrido_corrige_patologia_do_condicional(self):
        # SINTÉTICO: M̄ = 0, um pré a 5 EP de zero, um pós. O condicional puro aceita θ̄ a quase 5 EP (o vértice
        # vizinho trunca a distribuição); o híbrido de ARP volta a ≈ β_pós ± 1,96 σ (nível (α − κ)/(1 − κ)).
        b = np.array([0.5, 1.0])
        S = np.eye(2) * 0.01
        rc = H.ic_rm(b, S, 1, 1, [1.0], 0.0, metodo="condicional")
        rh = H.ic_rm(b, S, 1, 1, [1.0], 0.0, metodo="hibrido", n_sim=400)
        self.assertGreater(rc["ic_sup"] - rc["ic_inf"], 2 * 2 * Z * 0.1)
        z_h = stats.norm.ppf(1 - (0.05 - 0.005) / (1 - 0.005) / 2)
        self.assertAlmostEqual(rh["ic_inf"], 1.0 - z_h * 0.1, delta=0.01)
        self.assertAlmostEqual(rh["ic_sup"], 1.0 + z_h * 0.1, delta=0.01)

    def test_valor_critico_lf_uma_desigualdade(self):
        # SINTÉTICO: uma desigualdade, sem nuisance: η̃ = ξ/σ ~ N(0, 1); quantil 0,995 ≈ 2,576
        c = H.valor_critico_lf(np.zeros((1, 0)), np.array([[4.0]]), 0.005, 20000, 1)
        self.assertAlmostEqual(c, stats.norm.ppf(0.995), delta=0.08)

    def test_cobertura_monte_carlo_hibrido(self):
        # SINTÉTICO: mesmo desenho do teste do condicional; cobertura ≥ 0,93 em 200 réplicas
        rng = np.random.default_rng(99)
        delta = np.array([-0.2, -0.1, 0.1, 0.2])
        beta0 = delta + np.array([0.0, 0.0, 1.0, 1.0])
        Sig = np.eye(4) * 0.05 ** 2
        l = np.array([0.5, 0.5])
        cobre, n = 0, 200
        for _ in range(n):
            b = rng.multivariate_normal(beta0, Sig)
            r = H.ic_rm(b, Sig, 2, 2, l, 1.0, n_grade=21, iter_bissecao=8, metodo="hibrido", n_sim=200)
            cobre += int(r["ic_inf"] <= 1.0 <= r["ic_sup"])
        self.assertGreaterEqual(cobre / n, 0.93)


class TestRuptura(unittest.TestCase):
    def test_ruptura_rm_um_pre_um_pos(self):
        # SINTÉTICO: β_pós = 1, β_pré = 0,25, σ pequenos: ruptura do conjunto identificado em M̄ = 4;
        # com ruído, a ruptura do IC fica abaixo de 4
        Sig = np.diag([1e-4, 1e-4])
        f = lambda m: (lambda r: (r["ic_inf"], r["ic_sup"]))(H.ic_rm([0.25, 1.0], Sig, 1, 1, [1.0], m))
        r = H.ruptura(f, 6.0, 0.02)
        self.assertLess(r["ruptura"], 4.0)
        self.assertGreater(r["ruptura"], 3.5)

    def test_ruptura_zero_quando_ic_inclui_zero(self):
        Sig = np.diag([0.01, 1.0])
        f = lambda m: (lambda r: (r["ic_inf"], r["ic_sup"]))(H.ic_rm([0.1, 0.5], Sig, 1, 1, [1.0], m))
        self.assertEqual(H.ruptura(f, 2.0, 0.05)["ruptura"], 0.0)


if __name__ == "__main__":
    unittest.main()
