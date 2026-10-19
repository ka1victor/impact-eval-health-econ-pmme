"""Testes da biblioteca de estimação da RDD da bolsa (`scripts/rdd_bolsa/rdd_lib.py`) com DADOS SINTÉTICOS.

Todos os escores, outcomes, painéis e p-valores deste módulo são SINTÉTICOS:
gerados em memória com semente fixa e efeitos conhecidos por construção.
Nada aqui é observação empírica, nada é lido de `data/` ou de `output/` e
nada é gravado.

O teste verifica: (1) identidade com o E3 (07) e o E5 (11); (2) recuperação de
saltos conhecidos (local linear, empilhado, Poisson local, DiRD); (3) o IC
honesto: cv(0) = 1,96, colapso no HC1 com M = 0, regra de bolso exata numa
quártica, cobertura em simulação; (4) identidade DiRD em delta = DiRD em
painel; (5) índice KLK e de Anderson; (6) Holm e BKY contra exemplos feitos à
mão; (7) limites de Lee cobrem o efeito verdadeiro; (8) permutação de Fisher
igual à do E5; (9) determinismo.
"""

from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _importar(caminho: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


L = _importar(ROOT / "scripts" / "rdd_bolsa" / "rdd_lib.py", "rdd_lib_teste")
E3 = _importar(ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py", "e3_para_rdd_lib")
E5 = _importar(ROOT / "scripts" / "rdd_bolsa" / "11_inferencia_alternativa.py", "e5_para_rdd_lib")

SEMENTE = 20261018


def escore_sintetico(n: int, rng: np.random.Generator) -> np.ndarray:
    """Escore SINTÉTICO uniforme em milésimos inteiros (0,150 a 0,650)."""
    return rng.integers(150, 651, size=n)


def _iguais(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    return a == b


class TestIdentidadeComScriptsAnteriores(unittest.TestCase):
    """Sintético: identidade com o E3 (07) e o E5 (11)."""

    def test_local_linear_igual_ao_e3_bit_a_bit(self) -> None:
        for semente in range(3):
            rng = np.random.default_rng(SEMENTE + semente)
            s = escore_sintetico(3_000, rng)
            y = (rng.random(len(s)) < 0.3 + 0.4 * (s / 1000 - 0.15)).astype(float)
            for corte in (300, 400):
                for h in (30, 50, 80):
                    b = E3.rdd_local_linear(s, y, corte, h)
                    for entrada in (s, s.astype(float), s / 1000 * 1000):
                        a = L.rd_local_linear(entrada, y, corte, h)
                        for k in b:
                            self.assertTrue(_iguais(a[k], b[k]), f"{k}: {a[k]} != {b[k]} (corte {corte}, h {h})")

    def test_igual_ao_e5_com_covariaveis_peso_e_cluster(self) -> None:
        rng = np.random.default_rng(SEMENTE + 10)
        s = escore_sintetico(4_000, rng)
        z = rng.normal(size=(len(s), 2))
        peso = rng.integers(1, 6, len(s)).astype(float)
        cl = rng.integers(0, 800, len(s))
        y = 0.5 + (s / 1000) + 0.1 * (s > 300) + z @ np.array([0.3, -0.2]) + rng.normal(0, 0.3, len(s))
        casos = [
            dict(), dict(grau=0), dict(kernel="uniforme"),
            dict(Z=z, nomes_z=["z1", "z2"]), dict(peso=peso), dict(cluster=cl),
        ]
        for kw in casos:
            a = L.rd_local_linear(s, y, 300, 50, **kw)
            b = E5.rd_local(s, y, 300, 50, **kw)
            self.assertAlmostEqual(a["tau"], b["tau"], places=12, msg=str(kw.keys()))
            self.assertAlmostEqual(a["ep"], b["ep"], places=12, msg=str(kw.keys()))
            self.assertEqual((a["n_abaixo"], a["n_acima"]), (b["n_abaixo"], b["n_acima"]))

    def test_empilhado_igual_ao_e5(self) -> None:
        rng = np.random.default_rng(SEMENTE + 11)
        s = escore_sintetico(3_000, rng)
        y = rng.normal(size=len(s)) + 0.2 * (s > 300) + 0.2 * (s > 400)
        cortes = np.repeat([300, 400], len(s))
        ss, yy, ids = np.tile(s, 2), np.tile(y, 2), np.tile(np.arange(len(s)), 2)
        a = L.rd_empilhado(ss, yy, cortes, cluster=ids)
        b = E5.rd_empilhado(ss, yy, cortes, cortes.astype(str), cluster=ids, ids_municipio=ids)
        self.assertAlmostEqual(a["tau"], b["tau"], places=12)
        self.assertAlmostEqual(a["ep"], b["ep"], places=12)
        self.assertEqual((a["n_abaixo"], a["n_acima"], a["n_clusters"]), (b["n_abaixo"], b["n_acima"], b["n_clusters"]))

    def test_permutacao_igual_a_do_e5(self) -> None:
        rng = np.random.default_rng(SEMENTE + 12)
        y = rng.normal(size=60)
        t = np.zeros(60, dtype=bool)
        t[rng.choice(60, 25, replace=False)] = True
        sem = (SEMENTE, 1, 300, 10)
        np.testing.assert_array_equal(L.matriz_permutacao(60, 25, 500, sem), E5.matriz_permutacao(60, 25, 500, sem))
        p5 = E5.p_fisher_dif_medias(y, t, E5.matriz_permutacao(60, 25, 2_000, sem))
        # Blocos pequenos forçam a geração em pedaços: o fluxo aleatório tem de ser o mesmo.
        for bloco in (5_000_000, 600):
            r = L.fisher_dif_medias(y, t, n_perm=2_000, semente=sem, bloco_max=bloco)
            self.assertEqual(r["p_valor"], p5)


class TestLocalLinearEEmpilhado(unittest.TestCase):
    """Sintético: local linear e empilhado recuperam saltos conhecidos."""

    def test_recupera_salto_com_sinal_acima_menos_abaixo(self) -> None:
        rng = np.random.default_rng(SEMENTE + 20)
        s = escore_sintetico(30_000, rng)
        x = s / 1000
        for salto in (0.25, -0.25):
            y = 1 + 2 * x + salto * (s > 300) + rng.normal(0, 0.3, len(s))
            r = L.rd_local_linear(s, y, 300)
            self.assertLess(abs(r["tau"] - salto), 4 * r["ep"])
            self.assertEqual(np.sign(r["tau"]), np.sign(salto))

    def test_corte_pertence_ao_lado_inferior(self) -> None:
        s = np.array([296, 297, 298, 299, 300, 301, 302, 303, 304])
        y = (s > 300).astype(float)
        r = L.rd_local_linear(s, y, 300, 10)
        self.assertAlmostEqual(r["tau"], 1.0, places=12)
        self.assertEqual((r["n_abaixo"], r["n_acima"]), (5, 4))

    def test_covariavel_reduz_ep_sem_mudar_salto(self) -> None:
        rng = np.random.default_rng(SEMENTE + 21)
        s = escore_sintetico(10_000, rng)
        z = rng.normal(size=len(s))
        y = 1 + 2 * (s - 300) / 1000 + 0.2 * (s > 300) + z + rng.normal(0, 0.2, len(s))
        sem = L.rd_local_linear(s, y, 300)
        com = L.rd_local_linear(s, y, 300, Z=z, nomes_z=["z"])
        self.assertLess(com["ep"], 0.5 * sem["ep"])
        self.assertLess(abs(com["tau"] - 0.2), 4 * com["ep"])

    def test_empilhado_com_duplicatas_cluster_e_efeito_fixo_de_ciclo(self) -> None:
        rng = np.random.default_rng(SEMENTE + 22)
        n = 6_000
        s = escore_sintetico(n, rng)
        mun = np.arange(n)
        linhas = []
        for ciclo in (1, 2):
            efeito_ciclo = 0.3 * (ciclo == 2)
            for corte in (300, 400):
                y = (0.5 + efeito_ciclo + 1.2 * (s - corte) / 1000 + 0.15 * (s > corte)
                     + rng.normal(0, 0.3, n))
                linhas.append(pd.DataFrame({"s": s, "y": y, "corte": corte, "ciclo": ciclo, "mun": mun}))
        p = pd.concat(linhas, ignore_index=True)
        # Janela larga (h = 0,120): o mesmo município cai nas duas janelas.
        r = L.rd_empilhado(p["s"], p["y"], p["corte"], h_mil=120, cluster=p["mun"], efeitos_fixos=p["ciclo"])
        self.assertTrue(math.isfinite(r["ep"]))
        self.assertLess(abs(r["tau"] - 0.15), 4 * r["ep"])
        self.assertAlmostEqual(sum(r["pesos_grupos"].values()), 1.0, places=10)
        self.assertLess(r["n_abaixo"] + r["n_acima"], r["n_obs"])
        self.assertEqual(r["n_clusters"], int(p.loc[np.abs(p["s"] - p["corte"]) < 120, "mun"].nunique()))
        g = p["corte"].astype(str) + "_c" + p["ciclo"].astype(str)
        r2 = L.rd_empilhado(p["s"], p["y"], p["corte"], grupo=g, h_mil=120, cluster=p["mun"])
        self.assertLess(abs(r2["tau"] - 0.15), 4 * r2["ep"])
        self.assertEqual(len(r2["pesos_grupos"]), 4)
        aviso = L.rd_empilhado(p["s"], p["y"], p["corte"], h_mil=120, ids_unidade=p["mun"])
        self.assertIn("sem cluster", aviso["nota"])

    def test_suporte_insuficiente_devolve_nan_com_nota(self) -> None:
        r = L.rd_local_linear([299, 299, 301, 301], [0.0, 1.0, 0.0, 1.0], 300, 50)
        self.assertTrue(math.isnan(r["tau"]))
        self.assertIn("suporte insuficiente", r["nota"])
        g = L.rd_local_linear([299, 300, 301, 302], [0.0, 1.0, 0.0, 1.0], 300, 50)
        self.assertTrue(math.isnan(g["tau"]) and math.isnan(g["ep"]))
        self.assertIn("graus de liberdade", g["nota"])

    def test_rotulo_ou_escore_ausente_levanta_erro(self) -> None:
        rng = np.random.default_rng(SEMENTE + 23)
        s = escore_sintetico(500, rng)
        y = rng.normal(size=len(s))
        for ausente in (None, np.nan, pd.NA):
            cl = np.arange(len(s)).astype(object)
            cl[3] = ausente
            with self.assertRaises(ValueError):
                L.rd_local_linear(s, y, 300, cluster=cl)
            with self.assertRaises(ValueError):
                L.rd_empilhado(s, y, 300, cluster=cl)
            with self.assertRaises(ValueError):
                L.rd_poisson_local(s, np.abs(np.round(y)), 300, cluster=cl)
            with self.assertRaises(ValueError):
                L.rd_dird_painel(s, y, np.zeros(len(s)), 300, cl)
        with self.assertRaises(ValueError):
            L.rd_empilhado(s, y, 300, efeitos_fixos=pd.Series([1.0] * (len(s) - 1) + [np.nan]))
        s_nan = s.astype(float)
        s_nan[0] = np.nan
        with self.assertRaises(ValueError):
            L.rd_local_linear(s_nan, y, 300)

    def test_descartes_contados_e_na_nota(self) -> None:
        rng = np.random.default_rng(SEMENTE + 24)
        s = escore_sintetico(3_000, rng)
        y = s / 1000 + 0.1 * (s > 300) + rng.normal(0, 0.3, len(s))
        janela = np.flatnonzero(np.abs(s - 300) < 50)
        fora = np.flatnonzero(np.abs(s - 300) >= 50)
        z = rng.normal(size=len(s))
        z[janela[:4]] = np.nan
        z[fora[:9]] = np.nan
        peso = np.ones(len(s))
        peso[janela[4:7]] = np.nan
        peso[janela[7:9]] = 0.0
        yy = y.copy()
        yy[janela[9:11]] = np.nan
        r = L.rd_local_linear(s, yy, 300, Z=z, nomes_z=["z"], peso=peso)
        self.assertEqual((r["n_descartadas_y_ausente"], r["n_descartadas_covariavel_ausente"],
                          r["n_descartadas_peso_ausente"], r["n_peso_zero"]), (2, 4, 3, 2))
        self.assertIn("4 linhas na janela descartadas por covariavel ausente", r["nota"])
        self.assertIn("3 linhas na janela descartadas por peso ausente", r["nota"])
        self.assertIn("2 linhas na janela descartadas por y ausente", r["nota"])
        self.assertEqual(r["n_obs"], len(janela) - 11)
        self.assertTrue(math.isfinite(r["tau"]))
        limpo = L.rd_local_linear(s, y, 300)
        self.assertEqual((limpo["n_descartadas_y_ausente"], limpo["nota"]), (0, ""))
        e = L.rd_empilhado(s, yy, 300, Z=z)
        self.assertEqual((e["n_descartadas_y_ausente"], e["n_descartadas_covariavel_ausente"]), (2, 4))
        self.assertIn("descartadas", e["nota"])
        po = L.rd_poisson_local(s, np.where(np.isfinite(yy), np.abs(np.round(yy * 3)), np.nan), 300,
                                offset=np.where(np.isfinite(z), 0.0, np.nan))
        self.assertEqual((po["n_descartadas_y_ausente"], po["n_descartadas_offset_ausente"]), (2, 4))
        neg = np.ones(len(s))
        neg[0] = -1.0
        with self.assertRaises(ValueError):
            L.rd_local_linear(s, y, 300, peso=neg)


class TestHonesto(unittest.TestCase):
    """Sintético: IC com viés limitado (Armstrong e Kolesár)."""

    def test_valor_critico(self) -> None:
        self.assertAlmostEqual(L.cv_honesto(0.0), 1.959963984540054, places=10)
        self.assertAlmostEqual(L.cv_honesto(0.0, alfa=0.10), 1.6448536269514722, places=10)
        self.assertAlmostEqual(L.cv_honesto(8.0), 8.0 + 1.6448536269514722, places=6)
        self.assertGreater(L.cv_honesto(1.0), L.cv_honesto(0.5))
        self.assertAlmostEqual(L.p_honesto(1.959963984540054, 1.0, 0.0), 0.05, places=10)
        t = 0.7
        self.assertAlmostEqual(L.p_honesto(L.cv_honesto(t), 1.0, t), 0.05, places=9)

    def test_m_zero_e_ehw_reproduz_hc1(self) -> None:
        rng = np.random.default_rng(SEMENTE + 30)
        s = escore_sintetico(3_000, rng)
        y = s / 1000 + 0.1 * (s > 300) + rng.normal(0, 0.3, len(s))
        hc1 = L.rd_local_linear(s, y, 300)
        r = L.rd_honesto(s, y, 300, M=0.0, variancia="ehw")
        self.assertAlmostEqual(r["ep"], hc1["ep"], places=12)
        self.assertAlmostEqual(r["ic95_inf"], hc1["ic95_inf"], places=10)
        self.assertAlmostEqual(r["ic95_sup"], hc1["ic95_sup"], places=10)
        cl = rng.integers(0, 500, len(s))
        cr1 = L.rd_local_linear(s, y, 300, cluster=cl)
        rc = L.rd_honesto(s, y, 300, M=0.0, cluster=cl)
        self.assertEqual(rc["variancia"], "cluster")
        self.assertAlmostEqual(rc["ep"], cr1["ep"], places=12)
        with self.assertRaises(ValueError):
            L.rd_honesto(s, y, 300, M=1.0, cluster=cl, variancia="nn")

    def test_regra_de_bolso_exata_em_quartica(self) -> None:
        s = np.arange(150, 501)
        r = (s - 300) / 1000
        y = np.where(s <= 300, 1 + 2 * r + 30 * r ** 2 + 100 * r ** 3 + 500 * r ** 4, 2 - r + 10 * r ** 2)
        m = L.m_regra_de_bolso(s, y, 300, cortes_vizinhos=())
        # Abaixo: f'' = 60 + 600 r + 6000 r^2 em [-0,150; 0]: máximo 105 em r = -0,150.
        self.assertAlmostEqual(m["M_abaixo"], 105.0, places=5)
        self.assertAlmostEqual(m["M_acima"], 20.0, places=5)
        self.assertAlmostEqual(m["M"], 105.0, places=5)
        # O suporte restringe a quártica: em [-0,060; 0] o máximo é 60 (em r = 0).
        self.assertAlmostEqual(L.m_regra_de_bolso(s, y, 300, suporte_mil=(240, 500))["M_abaixo"], 60.0, places=4)

    def test_variancia_vizinhos_com_empates(self) -> None:
        x = np.array([0.0, 0.0, 1.0, 2.0, 3.0])
        y = np.array([1.0, 3.0, 2.0, 5.0, 4.0])
        sig = L.variancia_vizinhos(x, y, J=1)
        # x = 0: vizinho único (o empate); x = 1: três a distância 1 (os dois x = 0 e o x = 2; empates entram).
        self.assertAlmostEqual(sig[0], 0.5 * (1 - 3) ** 2)
        self.assertAlmostEqual(sig[2], (3 / 4) * (2 - np.mean([1, 3, 5])) ** 2)

    def test_cobertura_em_simulacao(self) -> None:
        """Curvatura forte só acima do corte: o IC HC1 subcobre; o honesto (M verdadeiro) cobre."""
        rng = np.random.default_rng(SEMENTE + 31)
        M, salto, n_sim = 600.0, 0.2, 300
        cob_hon = cob_hc1 = 0
        for _ in range(n_sim):
            s = escore_sintetico(1_500, rng)
            r = (s - 300) / 1000
            y = 1 + 2 * r + salto * (s > 300) + (M / 2) * r ** 2 * (s > 300) + rng.normal(0, 0.3, len(s))
            hon = L.rd_honesto(s, y, 300, M=M)
            cob_hon += hon["ic95_inf"] <= salto <= hon["ic95_sup"]
            cob_hc1 += hon["tau"] - Z * hon["ep_convencional"] <= salto <= hon["tau"] + Z * hon["ep_convencional"]
        self.assertGreaterEqual(cob_hon / n_sim, 0.93)
        self.assertLess(cob_hc1, cob_hon)

    def test_h_otimo_e_relato(self) -> None:
        rng = np.random.default_rng(SEMENTE + 32)
        s = escore_sintetico(4_000, rng)
        r = (s - 300) / 1000
        y = 1 + 2 * r + 20 * r ** 2 + 0.1 * (s > 300) + rng.normal(0, 0.3, len(s))
        out = L.rd_honesto_h_otimo(s, y, 300, M=40.0)
        self.assertLessEqual(out["h_otimo"]["semi_amplitude"], out["h_fixo"]["semi_amplitude"] + 1e-12)
        self.assertEqual(out["h_fixo"]["h_mil"], 50)
        self.assertEqual(out["h_otimo"]["semi_amplitude"], out["grade"]["semi_amplitude"].min())
        tab = L.rd_honesto_relato(s, y, 300, suporte_mil=(150, 400), grade_h_mil=(30, 50, 80, 120))
        self.assertEqual(len(tab), 6)
        self.assertEqual(sorted(tab["fator_M"].unique().tolist()), [0.5, 1.0, 2.0])
        fixo = tab[tab["especificacao"] == "h_fixo"].sort_values("fator_M")
        self.assertTrue((np.diff(fixo["semi_amplitude"].to_numpy()) > 0).all())
        # h ótimo sai rotulado como especificação adicional ao protocolo.
        self.assertEqual(out["h_otimo"]["rotulo"], L.ROTULO_H_OTIMO)
        self.assertIn("ADICIONAL", out["h_otimo"]["rotulo"])
        self.assertEqual(out["h_fixo"]["rotulo"], "h fixo do protocolo")
        self.assertEqual(tab["no_protocolo"].tolist(), [True, False] * 3)
        self.assertTrue(tab["nota"].str.contains(r"suporte \[150; 400\]").all())

    def test_suporte_explicito_da_regra_de_bolso(self) -> None:
        rng = np.random.default_rng(SEMENTE + 34)
        s = escore_sintetico(3_000, rng)
        y = s / 1000 + 0.1 * (s > 300) + rng.normal(0, 0.3, len(s))
        for f in (lambda: L.m_regra_de_bolso(s, y, 300), lambda: L.rd_honesto(s, y, 300),
                  lambda: L.rd_honesto_h_otimo(s, y, 300), lambda: L.rd_honesto_relato(s, y, 300),
                  lambda: L.m_regra_de_bolso(s, y, 300, suporte_mil=(150, 350), cortes_vizinhos=(300, 400))):
            with self.assertRaises(ValueError):
                f()
        self.assertEqual(L.suporte_regra_de_bolso(300, cortes_vizinhos=(300, 400)), (-math.inf, 350.0))
        self.assertEqual(L.suporte_regra_de_bolso(400, cortes_vizinhos=(300, 400)), (350.0, math.inf))
        self.assertEqual(L.suporte_regra_de_bolso(300, cortes_vizinhos=()), (-math.inf, math.inf))
        r = L.rd_honesto(s, y, 300, cortes_vizinhos=(300, 400))
        self.assertEqual(r["suporte_M_mil"], (-math.inf, 350.0))
        self.assertIn("suporte [-inf; 350]", r["nota"])
        m = L.m_regra_de_bolso(s, y, 300, suporte_mil=(None, 350))
        self.assertEqual(r["M"], m["M"])
        self.assertLessEqual(m["n_acima"], int(((s > 300) & (s <= 350)).sum()))
        # Com M informado, nenhum suporte é exigido e a nota diz a origem.
        self.assertIn("M informado pelo chamador", L.rd_honesto(s, y, 300, M=5.0)["nota"])
        # O peso da regra de bolso só entra se for passado a ela.
        pw = L.m_regra_de_bolso(s, y, 300, cortes_vizinhos=(300, 400), peso=rng.integers(1, 5, len(s)))
        self.assertTrue(pw["ponderada"])
        self.assertFalse(m["ponderada"])

    def test_empilhado_honesto(self) -> None:
        rng = np.random.default_rng(SEMENTE + 33)
        n = 4_000
        s = escore_sintetico(n, rng)
        y = s / 1000 + 0.1 * (s > 300) + 0.1 * (s > 400) + rng.normal(0, 0.3, n)
        cortes, ss, yy, ids = np.repeat([300, 400], n), np.tile(s, 2), np.tile(y, 2), np.tile(np.arange(n), 2)
        base = L.rd_empilhado(ss, yy, cortes, h_mil=120, cluster=ids)
        r0 = L.rd_empilhado_honesto(ss, yy, cortes, h_mil=120, cluster=ids, M=0.0)
        self.assertAlmostEqual(r0["ep"], base["ep"], places=12)
        self.assertAlmostEqual(r0["ic95_inf"], base["ic95_inf"], places=10)
        sup = (np.abs(ss - cortes) <= 100)
        with self.assertRaises(ValueError):
            L.rd_empilhado_honesto(ss[sup], yy[sup], cortes[sup], h_mil=50, cluster=ids[sup])
        r = L.rd_empilhado_honesto(ss[sup], yy[sup], cortes[sup], h_mil=50, cluster=ids[sup],
                                   cortes_vizinhos=(300, 400))
        self.assertEqual(set(r["M_por_grupo"]), {"300", "400"})
        self.assertEqual(r["suporte_M_por_grupo"], {"300": (-math.inf, 350.0), "400": (350.0, math.inf)})
        self.assertIn("grupo 300: M pela regra de bolso: quartica por lado no suporte [-inf; 350]", r["nota"])
        rd = L.rd_empilhado_honesto(ss[sup], yy[sup], cortes[sup], h_mil=50, cluster=ids[sup],
                                    suporte_mil={"300": (200, 350), "400": (350, 500)})
        self.assertEqual(rd["suporte_M_por_grupo"], {"300": (200.0, 350.0), "400": (350.0, 500.0)})
        self.assertEqual(rd["M_por_grupo"], r["M_por_grupo"])
        self.assertGreater(r["semi_amplitude"], Z * r["ep"])
        self.assertLessEqual(r["ic95_inf"], r["tau"])
        nn = L.rd_empilhado_honesto(np.concatenate([s[s <= 350], s[s > 350]]),
                                    np.concatenate([y[s <= 350], y[s > 350]]),
                                    np.where(np.concatenate([s[s <= 350], s[s > 350]]) <= 350, 300, 400), M=10.0)
        self.assertEqual(nn["variancia"], "nn")
        self.assertTrue(math.isfinite(nn["ep"]))


Z = 1.959963984540054


class TestPoissonLocal(unittest.TestCase):
    """Sintético: Poisson local com kernel."""

    def test_recupera_efeito_em_log_com_offset(self) -> None:
        rng = np.random.default_rng(SEMENTE + 40)
        s = escore_sintetico(20_000, rng)
        x = (s - 300) / 1000
        celulas = rng.integers(1, 6, len(s))
        mu = celulas * np.exp(0.2 + 1.5 * x + 0.3 * (s > 300))
        y = rng.poisson(mu)
        r = L.rd_poisson_local(s, y, 300, offset=np.log(celulas))
        self.assertTrue(r["convergiu"])
        self.assertLess(abs(r["tau"] - 0.3), 4 * r["ep"])
        self.assertAlmostEqual(r["efeito_relativo"], math.expm1(r["tau"]))

    def test_ponto_igual_ao_glm_do_statsmodels(self) -> None:
        import statsmodels.api as sm

        rng = np.random.default_rng(SEMENTE + 41)
        s = escore_sintetico(3_000, rng)
        off = np.log(rng.integers(1, 4, len(s)))
        y = rng.poisson(np.exp(off + 0.1 + 0.2 * (s > 400)))
        r = L.rd_poisson_local(s, y, 400, offset=off)
        xm = s - 400
        w = np.clip(1 - np.abs(xm) / 50, 0, None)
        u = w > 0
        x = xm[u] / 1000
        t = (xm[u] > 0).astype(float)
        X = np.column_stack([np.ones(u.sum()), x, t, t * x])
        glm = sm.GLM(y[u], X, family=sm.families.Poisson(), offset=off[u], var_weights=w[u]).fit(tol=1e-12)
        self.assertAlmostEqual(r["tau"], glm.params[2], places=7)

    def test_ep_sanduiche_igual_ao_glm_do_statsmodels(self) -> None:
        import warnings

        import statsmodels.api as sm

        rng = np.random.default_rng(SEMENTE + 43)
        s = escore_sintetico(3_000, rng)
        off = np.log(rng.integers(1, 4, len(s)))
        cl = rng.integers(0, 300, len(s))
        y = rng.poisson(np.exp(off + 0.1 + 0.2 * (s > 400)))
        xm = s - 400
        w = np.clip(1 - np.abs(xm) / 50, 0, None)
        u = w > 0
        x = xm[u] / 1000
        t = (xm[u] > 0).astype(float)
        X = np.column_stack([np.ones(u.sum()), x, t, t * x])

        def glm(**kw):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return sm.GLM(y[u], X, family=sm.families.Poisson(), offset=off[u],
                              var_weights=w[u]).fit(tol=1e-13, **kw)

        hc0 = glm(cov_type="HC0").bse[2]
        self.assertAlmostEqual(L.rd_poisson_local(s, y, 400, offset=off, pequena_amostra=False)["ep"], hc0, places=10)
        # O "HC1" do GLM do statsmodels não aplica n/(n-k); aqui HC1 = HC0 x raiz(n/(n-4)).
        n = int(u.sum())
        self.assertAlmostEqual(L.rd_poisson_local(s, y, 400, offset=off)["ep"], hc0 * math.sqrt(n / (n - 4)), places=10)
        cr1 = glm(cov_type="cluster", cov_kwds={"groups": cl[u]}).bse[2]
        self.assertAlmostEqual(L.rd_poisson_local(s, y, 400, offset=off, cluster=cl)["ep"], cr1, places=10)

    def test_separacao_graus_de_liberdade_e_convergencia(self) -> None:
        s = np.repeat(np.arange(260, 341), 5)
        y = np.where(s == 300, 2, 0) + np.where(s > 300, 1, 0)
        r = L.rd_poisson_local(s, y, 300)
        self.assertTrue(math.isnan(r["tau"]) and math.isnan(r["ep"]))
        self.assertIn("separacao (abaixo)", r["nota"])
        g = L.rd_poisson_local([299, 300, 301, 302], [1, 2, 3, 4], 300, h_mil=10)
        self.assertTrue(math.isnan(g["tau"]))
        self.assertIn("graus de liberdade", g["nota"])
        rng = np.random.default_rng(SEMENTE + 44)
        s2 = escore_sintetico(3_000, rng)
        y2 = rng.poisson(np.exp(1 + 0.3 * (s2 > 300)))
        curto = L.rd_poisson_local(s2, y2, 300, max_iter=1)
        self.assertFalse(curto["convergiu"])
        self.assertTrue(math.isnan(curto["tau"]))
        self.assertIn("nao convergiu", curto["nota"])
        ok = L.rd_poisson_local(s2, y2, 300)
        self.assertTrue(ok["convergiu"] and math.isfinite(ok["tau"]))

    def test_lado_sem_eventos(self) -> None:
        rng = np.random.default_rng(SEMENTE + 42)
        s = escore_sintetico(2_000, rng)
        y = np.where(s > 300, rng.poisson(2.0, len(s)), 0)
        r = L.rd_poisson_local(s, y, 300)
        self.assertTrue(math.isnan(r["tau"]))
        self.assertIn("sem eventos", r["nota"])
        r0 = L.rd_poisson_local(s, np.zeros(len(s)), 300)
        self.assertIn("abaixo, acima", r0["nota"])


def _painel_sintetico(rng: np.random.Generator, n: int, n_pre: int, n_pos: int,
                      salto_fixo: float, efeito: float) -> pd.DataFrame:
    """Painel SINTÉTICO: descontinuidade fixa (confundidor) em todos os períodos + efeito no pós."""
    s = escore_sintetico(n, rng)
    a = rng.normal(0, 0.5, n)
    linhas = []
    for k in range(n_pre + n_pos):
        pos = k >= n_pre
        y = (a + 1.5 * (s - 300) / 1000 + 0.05 * k + salto_fixo * (s > 300) + efeito * pos * (s > 300)
             + rng.normal(0, 0.2, n))
        linhas.append(pd.DataFrame({"unidade": np.arange(n), "periodo": k, "s": s, "y": y, "pos": float(pos)}))
    return pd.concat(linhas, ignore_index=True)


class TestDiRD(unittest.TestCase):
    """Sintético: diferença em descontinuidades e estudo de evento."""

    def test_delta_igual_ao_painel(self) -> None:
        rng = np.random.default_rng(SEMENTE + 50)
        p = _painel_sintetico(rng, 3_000, 4, 6, salto_fixo=0.5, efeito=0.3)
        d = L.diferenca_pos_pre(p, col_unidade="unidade", col_periodo="periodo", col_y="y",
                                periodos_pre=range(4), periodos_pos=range(4, 10))
        s_u = p.drop_duplicates("unidade").set_index("unidade").loc[d["unidade"], "s"].to_numpy()
        for pequena in (False, True):
            a = L.rd_dird_delta(s_u, d["y_pos"], d["y_pre"], 300, pequena_amostra=pequena)
            b = L.rd_dird_painel(p["s"], p["y"], p["pos"], 300, p["unidade"], pequena_amostra=pequena)
            self.assertAlmostEqual(a["tau"], b["tau"], places=10)
            if not pequena:
                self.assertAlmostEqual(a["ep"], b["ep"], places=10)
        self.assertEqual((a["n_abaixo"], a["n_acima"]), (b["n_abaixo"], b["n_acima"]))
        self.assertLess(abs(a["tau"] - 0.3), 4 * a["ep"])
        nivel = L.rd_local_linear(s_u, d["y_pos"], 300)
        self.assertLess(abs(nivel["tau"] - 0.8), 4 * nivel["ep"])
        self.assertLess(abs(b["tau_pre"] - 0.5), 0.1)

    def test_delta_exige_painel_completo(self) -> None:
        rng = np.random.default_rng(SEMENTE + 51)
        p = _painel_sintetico(rng, 50, 2, 2, 0.0, 0.0)
        p = p[~((p["unidade"] == 0) & (p["periodo"] == 1))]
        d = L.diferenca_pos_pre(p, col_unidade="unidade", col_periodo="periodo", col_y="y",
                                periodos_pre=[0, 1], periodos_pos=[2, 3])
        self.assertTrue(math.isnan(d.loc[d["unidade"] == 0, "delta"].iloc[0]))
        self.assertEqual(int(d["delta"].isna().sum()), 1)
        self.assertEqual(d.attrs["n_unidades_incompletas_pre"], 1)
        self.assertEqual(d.attrs["n_unidades_incompletas_pos"], 0)
        self.assertIn("painel desbalanceado: 1 unidades", d.attrs["nota"])
        self.assertFalse(bool(d.loc[d["unidade"] == 0, "completo_pre"].iloc[0]))
        livre = L.diferenca_pos_pre(p, col_unidade="unidade", col_periodo="periodo", col_y="y",
                                    periodos_pre=[0, 1], periodos_pos=[2, 3], exigir_completo=False)
        self.assertEqual(int(livre["delta"].isna().sum()), 0)
        self.assertIn("medias com os periodos presentes", livre.attrs["nota"])
        completo = L.diferenca_pos_pre(_painel_sintetico(rng, 20, 2, 2, 0.0, 0.0), col_unidade="unidade",
                                       col_periodo="periodo", col_y="y", periodos_pre=[0, 1], periodos_pos=[2, 3])
        self.assertEqual(completo.attrs["nota"], "")

    def test_painel_desbalanceado_nao_e_silencioso(self) -> None:
        rng = np.random.default_rng(SEMENTE + 53)
        p = _painel_sintetico(rng, 2_000, 3, 3, 0.5, 0.3)
        b = L.rd_dird_painel(p["s"], p["y"], p["pos"], 300, p["unidade"])
        self.assertTrue(b["painel_balanceado"])
        self.assertEqual(b["nota"], "")
        na_janela = p.loc[np.abs(p["s"] - 300) < 50, "unidade"].unique()
        sem_pos = na_janela[:7]
        sem_um_pre = na_janela[7:12]
        q = p[~(p["unidade"].isin(sem_pos) & (p["pos"] == 1))]
        q = q[~(q["unidade"].isin(sem_um_pre) & (q["periodo"] == 0))]
        r = L.rd_dird_painel(q["s"], q["y"], q["pos"], 300, q["unidade"])
        self.assertFalse(r["painel_balanceado"])
        self.assertEqual((r["n_unidades_sem_pre"], r["n_unidades_sem_pos"]), (0, 7))
        self.assertIn("painel desbalanceado na janela: 0 unidades sem pre, 7 sem pos", r["nota"])
        self.assertTrue(math.isfinite(r["tau"]))

    def test_estudo_de_evento(self) -> None:
        rng = np.random.default_rng(SEMENTE + 52)
        p = _painel_sintetico(rng, 6_000, 4, 3, salto_fixo=0.5, efeito=0.3)
        es = L.rd_estudo_evento(p, col_unidade="unidade", col_periodo="periodo", col_y="y", col_s="s",
                                corte_mil=300, periodo_ref=3)
        self.assertEqual(es["periodo"].tolist(), list(range(7)))
        ref = es[es["referencia"]]
        self.assertEqual(ref["periodo"].tolist(), [3])
        self.assertTrue(ref["tau"].isna().all())
        for _, linha in es[~es["referencia"]].iterrows():
            alvo = 0.3 if linha["periodo"] >= 4 else 0.0
            self.assertLess(abs(linha["tau"] - alvo), 4.5 * linha["ep"])


class TestIndice(unittest.TestCase):
    """Sintético: índices de Kling-Liebman-Katz e de Anderson."""

    def _dados(self, rng):
        n = 2_000
        s = escore_sintetico(n, rng)
        ciclo = rng.integers(1, 3, n)
        a = rng.normal(10, 2, n) + 5 * ciclo
        b = rng.normal(0.5, 0.1, n)
        desist = rng.normal(3, 1, n)
        return pd.DataFrame({"s": s, "ciclo": ciclo, "a": a, "b": b, "desist": desist})

    def test_klk_padroniza_pela_referencia_e_alinha_sinal(self) -> None:
        rng = np.random.default_rng(SEMENTE + 60)
        df = self._dados(rng)
        ref = L.mascara_referencia(df["s"], 300, 50)
        out, par = L.indice_klk(df, ["a", "b", "desist"], referencia=ref, sinais={"desist": -1}, grupo=df["ciclo"])
        for ciclo in (1, 2):
            m = ref & (df["ciclo"] == ciclo).to_numpy()
            for c in ("z_a", "z_b", "z_desist"):
                self.assertAlmostEqual(out.loc[m, c].mean(), 0.0, places=10)
                self.assertAlmostEqual(out.loc[m, c].std(ddof=1), 1.0, places=10)
        self.assertLess(np.corrcoef(out["z_desist"], df["desist"])[0, 1], -0.99)
        np.testing.assert_allclose(out["indice"], out[["z_a", "z_b", "z_desist"]].mean(axis=1), rtol=0, atol=1e-12)
        self.assertEqual(len(par), 6)

    def test_klk_media_dos_componentes_presentes(self) -> None:
        df = pd.DataFrame({"a": [0.0, 2.0, 1.0, 4.0], "b": [1.0, 3.0, np.nan, 5.0]})
        ref = np.array([True, True, False, False])
        out, _ = L.indice_klk(df, ["a", "b"], referencia=ref)
        # Referência: a ~ média 1, dp sqrt(2); b ~ média 2, dp sqrt(2).
        self.assertAlmostEqual(out["indice"].iloc[2], 0.0)
        self.assertAlmostEqual(out["indice"].iloc[3], (3 / math.sqrt(2) + 3 / math.sqrt(2)) / 2)
        self.assertEqual(out["n_componentes"].tolist(), [2, 2, 1, 2])

    def test_anderson_com_dois_componentes_igual_klk(self) -> None:
        rng = np.random.default_rng(SEMENTE + 61)
        u = rng.normal(size=500)
        df = pd.DataFrame({"a": u + rng.normal(size=500), "b": u + rng.normal(size=500)})
        ref = np.zeros(500, dtype=bool)
        ref[:250] = True
        klk, _ = L.indice_klk(df, ["a", "b"], referencia=ref)
        and_, par = L.indice_klk(df, ["a", "b"], referencia=ref, metodo="anderson")
        np.testing.assert_allclose(and_["indice"], klk["indice"], atol=1e-12)
        self.assertAlmostEqual(par["peso_anderson"].iloc[0], par["peso_anderson"].iloc[1], places=12)

    def test_anderson_pesa_menos_componentes_redundantes(self) -> None:
        rng = np.random.default_rng(SEMENTE + 62)
        u = rng.normal(size=2_000)
        df = pd.DataFrame({"a": u + 0.1 * rng.normal(size=2_000), "b": u + 0.1 * rng.normal(size=2_000),
                           "c": rng.normal(size=2_000)})
        _, par = L.indice_klk(df, ["a", "b", "c"], referencia=np.ones(2_000, dtype=bool), metodo="anderson")
        p = par.set_index("componente")["peso_anderson"]
        self.assertGreater(p["c"], 1.5 * p["a"])
        self.assertGreater(p["c"], 1.5 * p["b"])


class TestTestesMultiplos(unittest.TestCase):
    """Sintético: Holm e BKY em p-valores digitados (exemplos feitos à mão)."""

    def test_holm_exemplo_a_mao(self) -> None:
        # Ordenados: 0,005 (x4 = 0,02), 0,01 (x3 = 0,03), 0,03 (x2 = 0,06), 0,04 (x1 = 0,04 -> 0,06).
        np.testing.assert_allclose(L.holm([0.01, 0.04, 0.03, 0.005]), [0.03, 0.06, 0.06, 0.02])
        out = L.holm([0.2, np.nan, 0.6])
        self.assertTrue(math.isnan(out[1]))
        np.testing.assert_allclose(out[[0, 2]], [0.4, 0.6])
        np.testing.assert_allclose(L.holm([0.5, 0.7]), [1.0, 1.0])

    def test_bky_exemplo_a_mao(self) -> None:
        # Feito à mão pelo algoritmo de Anderson (2008), m = 4:
        # p = 0,001: q = 0,005 (q1 = 0,004975 >= 4 x 0,001; com q = 0,004 nada é rejeitado);
        # p = 0,010: q = 0,016 (R1 = 1, q2 = 4/3 q1 = 0,020997, 0,01 <= q2 x 2/4);
        # p = 0,020: q = 0,021 (R1 = 2, q2 = 2 q1 = 0,041136, 0,02 <= q2 x 3/4);
        # p = 0,500: q = 0,143 (R1 = 3, q2 = 4 q1 = 0,500437 >= 0,5).
        np.testing.assert_allclose(L.qvalores_bky([0.02, 0.5, 0.001, 0.01]), [0.021, 0.143, 0.005, 0.016])
        q = L.qvalores_bky([0.9, np.nan, 0.95])
        self.assertTrue(math.isnan(q[1]))
        self.assertEqual(q[0], 1.0)

    def test_bky_decisoes_iguais_ao_statsmodels_e_monotonas(self) -> None:
        """Rejeitar se q <= alfa equivale ao BKY de dois estágios do statsmodels (maxiter=1)."""
        from statsmodels.stats.multitest import fdrcorrection_twostage

        rng = np.random.default_rng(SEMENTE + 70)
        for _ in range(100):
            p = np.concatenate([rng.uniform(0, 0.02, rng.integers(1, 8)), rng.uniform(0, 1, rng.integers(1, 20))])
            q = L.qvalores_bky(p)
            for alfa in (0.01, 0.05, 0.10, 0.20):
                rej = fdrcorrection_twostage(p, alpha=alfa, method="bky", maxiter=1)[0]
                np.testing.assert_array_equal(rej, q <= alfa)
            o = np.argsort(p, kind="stable")
            self.assertTrue((np.diff(q[o]) >= 0).all())
            self.assertTrue(((q > 0) & (q <= 1)).all())
        # Uma única hipótese: q = menor q da grade com q/(1+q) >= p (0,04 -> 0,042; maior que p).
        self.assertAlmostEqual(L.qvalores_bky([0.04])[0], 0.042)


class TestLee(unittest.TestCase):
    """Sintético: limites de Lee no corte."""

    def test_limites_cobrem_o_efeito_dos_sempre_selecionados(self) -> None:
        rng = np.random.default_rng(SEMENTE + 80)
        n = 60_000
        s = escore_sintetico(n, rng)
        t = s > 300
        u = rng.random(n)
        sel = np.where(t, u < 0.8, u < 0.6).astype(float)
        eps = 0.8 * (u - 0.5) * 3 + rng.normal(0, 0.6, n)
        y = 1 + 0.5 * (s - 300) / 1000 + 0.2 * t + eps
        y = np.where(sel == 1, y, np.nan)
        r = L.limites_lee_rd(s, y, sel, 300)
        self.assertEqual(r["lado_aparado"], "acima")
        self.assertAlmostEqual(r["q_aparo"], 0.25, delta=0.06)
        self.assertLess(r["tau_inf"], 0.2)
        self.assertGreater(r["tau_sup"], 0.2)
        self.assertLess(r["tau_sup"] - r["tau_inf"], 2.0)
        self.assertLessEqual(r["ic95_inf"], r["tau_inf"])
        self.assertGreaterEqual(r["ic95_sup"], r["tau_sup"])

    def test_sem_selecao_diferencial_os_limites_colapsam(self) -> None:
        rng = np.random.default_rng(SEMENTE + 81)
        s = escore_sintetico(5_000, rng)
        y = s / 1000 + 0.1 * (s > 300) + rng.normal(0, 0.3, len(s))
        r = L.limites_lee_rd(s, y, np.ones(len(s)), 300)
        self.assertAlmostEqual(r["q_aparo"], 0.0, places=12)
        self.assertAlmostEqual(r["tau_inf"], r["tau_sup"], places=12)
        self.assertAlmostEqual(r["tau_inf"], L.rd_local_linear(s, y, 300)["tau"], places=12)

    def test_selecionado_sem_y_invalida_os_limites(self) -> None:
        rng = np.random.default_rng(SEMENTE + 82)
        s = escore_sintetico(5_000, rng)
        sel = (rng.random(len(s)) < 0.7).astype(float)
        y = np.where(sel == 1, s / 1000 + rng.normal(0, 0.3, len(s)), np.nan)
        janela_sel = np.flatnonzero((np.abs(s - 300) < 50) & (sel == 1))
        y_ruim = y.copy()
        y_ruim[janela_sel[:3]] = np.nan
        r = L.limites_lee_rd(s, y_ruim, sel, 300)
        self.assertTrue(math.isnan(r["tau_inf"]) and math.isnan(r["tau_sup"]))
        self.assertEqual(r["n_selecionados_sem_y"], 3)
        self.assertIn("3 selecionados sem y", r["nota"])
        sel_ruim = sel.copy()
        sel_ruim[np.flatnonzero(np.abs(s - 300) < 50)[0]] = np.nan
        r2 = L.limites_lee_rd(s, y, sel_ruim, 300)
        self.assertTrue(math.isnan(r2["tau_inf"]))
        self.assertEqual(r2["n_selecao_ausente"], 1)
        # Fora da janela, y ausente em selecionado não entra em nada e não invalida.
        fora = np.flatnonzero((np.abs(s - 300) >= 50) & (sel == 1))
        y_fora = y.copy()
        y_fora[fora[:5]] = np.nan
        self.assertTrue(math.isfinite(L.limites_lee_rd(s, y_fora, sel, 300)["tau_inf"]))

    def test_aparo_fracionario_retira_exatamente_q(self) -> None:
        y = np.array([5.0, 1.0, 3.0, 2.0])
        w = np.array([1.0, 1.0, 1.0, 1.0])
        m = L._multiplicador_aparo(y, w, 0.375, de_cima=True)
        np.testing.assert_allclose(m, [0.0, 1.0, 0.5, 1.0])
        self.assertAlmostEqual(float(np.sum(w * (1 - m))), 0.375 * 4)

    def test_aparo_proporcional_nos_empates(self) -> None:
        # Sintético (auditoria 22): três empates no topo; q tira 1,5 unidades de peso -> cada um perde a metade,
        # sem depender da ordem das linhas; sem empate na fronteira, igual ao padrão "ordem".
        y = np.array([1.0, 0.0, 1.0, 0.5, 1.0, 0.0])
        w = np.ones(6)
        m = L._multiplicador_aparo(y, w, 0.25, de_cima=True, empates="proporcional")
        np.testing.assert_allclose(m, [0.5, 1.0, 0.5, 1.0, 0.5, 1.0])
        perm = np.array([5, 3, 1, 0, 4, 2])
        np.testing.assert_allclose(L._multiplicador_aparo(y[perm], w[perm], 0.25, True, "proporcional"), m[perm])
        self.assertAlmostEqual(float(np.sum(w * (1 - m))), 0.25 * 6)
        m0 = L._multiplicador_aparo(y, w, 0.25, de_cima=True)
        np.testing.assert_allclose(m0, [0.0, 1.0, 0.5, 1.0, 1.0, 1.0])   # padrão: apara pela ordem das linhas
        y2 = np.array([5.0, 1.0, 3.0, 2.0])
        np.testing.assert_allclose(L._multiplicador_aparo(y2, np.ones(4), 0.375, True, "proporcional"),
                                   L._multiplicador_aparo(y2, np.ones(4), 0.375, True))
        with self.assertRaises(ValueError):
            L._multiplicador_aparo(y, w, 0.25, True, "aleatorio")


class TestLocalRandomizationEDeterminismo(unittest.TestCase):
    """Sintético: Fisher e determinismo."""

    def test_fisher_detecta_efeito_grande_e_nao_rejeita_nulo(self) -> None:
        rng = np.random.default_rng(SEMENTE + 90)
        s = rng.integers(290, 311, 200)
        y0 = rng.normal(size=200)
        forte = L.rl_janela(s, y0 + 2.0 * (s > 300), 300, 10, n_perm=999)
        self.assertAlmostEqual(forte["p_valor"], 1 / 1000)
        self.assertGreater(forte["tau"], 1.5)
        nulo = L.rl_janela(s, y0, 300, 10, n_perm=999)
        self.assertGreater(nulo["p_valor"], 0.01)
        self.assertEqual(nulo["semente"], [SEMENTE, 300, 10])

    def test_resultados_deterministicos(self) -> None:
        rng = np.random.default_rng(SEMENTE + 91)
        s = escore_sintetico(2_000, rng)
        y = rng.normal(size=len(s)) + 0.1 * (s > 300)
        for f in (lambda: L.rd_local_linear(s, y, 300), lambda: L.rd_honesto(s, y, 300, cortes_vizinhos=(300, 400)),
                  lambda: L.rl_janela(s, y, 300, 10, n_perm=500),
                  lambda: L.rd_poisson_local(s, np.abs(np.round(y * 3)), 300)):
            a, b = f(), f()
            for k in a:
                self.assertTrue(_iguais(a[k], b[k]) or isinstance(a[k], dict), k)


if __name__ == "__main__":
    unittest.main()
