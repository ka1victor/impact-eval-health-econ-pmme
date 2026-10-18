"""Testes do E2 (limites parciais com escore ausente) com DADOS SINTÉTICOS.

Municípios, escores, posições verdadeiras e D_k deste módulo são SINTÉTICOS:
gerados em memória com semente fixa. Nada aqui é observação empírica e nada é
gravado. A última classe só lê as saídas reais versionadas do E2.

Propriedades verificadas em `scripts/rdd_bolsa/06_estimar_E2_limites.py`:
(1) ordenação: p_min <= p_max em cada lado e delta_min <= delta_max; (2) sem
município sem escore, os limites colapsam na diferença ingênua; (3) os extremos
exatos ficam dentro dos marginais e coincidem com eles quando nenhum município
pode cruzar as duas janelas; (4) validade: o Delta verdadeiro de um mundo
sintético fica dentro dos limites; (5) mais informação (conjuntos possíveis
menores) dá limites aninhados; (6) as mesmas propriedades nas saídas reais.
"""

from __future__ import annotations

import importlib.util
import json
import math
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "06_estimar_E2_limites.py"
SPEC = importlib.util.spec_from_file_location("e2_limites", SCRIPT)
E2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E2)

SEMENTE = 20261018
TOL = 1e-12


def faixa_de(s: int) -> str:
    return E2.faixa_por_escore_mil(int(s))


def mundo_sintetico(rng: np.random.Generator, n_com: int, n_sem: int) -> dict:
    """Mundo SINTÉTICO: com escore (s, D) e sem escore (D = 0, posição verdadeira).

    O conjunto possível de quem não tem escore é o intervalo da faixa anunciada,
    que contém a posição verdadeira, como no cenário `pior_caso`.
    """
    s = rng.integers(150, 651, size=n_com)
    d = (rng.random(n_com) < 0.6).astype(int)
    verdade = rng.integers(150, 651, size=n_sem)
    lo = np.array([E2.INTERVALO_FAIXA_MIL[faixa_de(v)][0] for v in verdade], dtype=int)
    hi = np.array([E2.INTERVALO_FAIXA_MIL[faixa_de(v)][1] for v in verdade], dtype=int)
    return {"s": s, "d": d, "verdade": verdade, "lo": lo, "hi": hi}


def delta_verdadeiro(m: dict, c: int, h: int) -> float:
    """Delta com todas as posições conhecidas; quem não tem escore tem D = 0."""
    s = np.concatenate([m["s"], m["verdade"]])
    d = np.concatenate([m["d"], np.zeros(len(m["verdade"]), dtype=int)])
    inf = (s > c - h) & (s <= c)
    sup = (s > c) & (s <= c + h)
    if not inf.any() or not sup.any():
        return math.nan
    return d[sup].mean() - d[inf].mean()


class TestLimitesMarginais(unittest.TestCase):
    def test_ordenacao_e_formulas(self) -> None:
        for k in range(1, 6):
            for nd in range(0, k + 1):
                for n_poss in range(0, 4):
                    p_min, p_max = E2.limites_marginais(nd, k, n_poss)
                    self.assertLessEqual(p_min, p_max)
                    self.assertAlmostEqual(p_min, nd / (k + n_poss))
                    self.assertAlmostEqual(p_max, nd / k)
                    if n_poss == 0:
                        self.assertEqual(p_min, p_max)

    def test_janela_que_pode_ficar_vazia(self) -> None:
        self.assertEqual(E2.limites_marginais(0, 0, 3), (0.0, 0.0))
        p_min, p_max = E2.limites_marginais(0, 0, 0)
        self.assertTrue(math.isnan(p_min) and math.isnan(p_max))


class TestExtremosExatos(unittest.TestCase):
    def test_sem_municipio_sem_escore_e_identificacao_pontual(self) -> None:
        rng = np.random.default_rng(SEMENTE)
        s = rng.integers(150, 651, size=400)
        d = (rng.random(400) < 0.5).astype(int)
        vazio = np.array([], dtype=int)
        for c in E2.CORTES_MIL:
            for h in E2.JANELAS_MIL:
                r = E2.limites_janela(s, d, vazio, vazio, c, h)
                self.assertEqual(r["delta_min"], r["delta_max"])
                self.assertAlmostEqual(r["delta_min"], r["delta_ingenuo_viesado"], places=12)

    def test_exatos_dentro_dos_marginais(self) -> None:
        rng = np.random.default_rng(SEMENTE + 1)
        for _ in range(400):
            k_l, k_u = rng.integers(0, 6, size=2)
            nd_l, nd_u = rng.integers(0, k_l + 1), rng.integers(0, k_u + 1)
            n_a, n_b, n_c = rng.integers(0, 4, size=3)
            n_c_fora = rng.integers(0, n_c + 1)
            dmin, dmax = E2.extremos_exatos(nd_l, k_l, nd_u, k_u, n_a, n_b, n_c, n_c_fora)
            if math.isnan(dmin):
                continue
            p_inf_min, p_inf_max = E2.limites_marginais(nd_l, k_l, n_a + n_c)
            p_sup_min, p_sup_max = E2.limites_marginais(nd_u, k_u, n_b + n_c)
            self.assertLessEqual(dmin, dmax + TOL)
            self.assertGreaterEqual(dmin, p_sup_min - p_inf_max - TOL)
            self.assertLessEqual(dmax, p_sup_max - p_inf_min + TOL)
            if n_c == 0 and k_l > 0 and k_u > 0:
                self.assertAlmostEqual(dmin, p_sup_min - p_inf_max, places=12)
                self.assertAlmostEqual(dmax, p_sup_max - p_inf_min, places=12)

    def test_exclusividade_restringe_quando_a_janela_pode_esvaziar(self) -> None:
        # Um único município sem escore cruza as duas janelas e é o único candidato ao lado
        # inferior: se for para o superior, o inferior fica vazio. Só "inferior" é admissível.
        dmin, dmax = E2.extremos_exatos(nd_l=0, k_l=0, nd_u=1, k_u=1, n_a=0, n_b=0, n_c=1, n_c_fora=0)
        self.assertEqual((dmin, dmax), (1.0, 1.0))
        p_inf = E2.limites_marginais(0, 0, 1)
        p_sup = E2.limites_marginais(1, 1, 1)
        self.assertEqual(p_sup[0] - p_inf[1], 0.5)  # o marginal deixaria delta_min = 0,5


class TestValidadeSintetica(unittest.TestCase):
    def test_delta_verdadeiro_dentro_dos_limites(self) -> None:
        rng = np.random.default_rng(SEMENTE + 2)
        testados = 0
        for _ in range(150):
            m = mundo_sintetico(rng, n_com=int(rng.integers(20, 120)), n_sem=int(rng.integers(0, 80)))
            for c in E2.CORTES_MIL:
                for h in E2.JANELAS_MIL:
                    verdade = delta_verdadeiro(m, c, h)
                    if math.isnan(verdade):
                        continue
                    r = E2.limites_janela(m["s"], m["d"], m["lo"], m["hi"], c, h)
                    self.assertLessEqual(r["p_inf_min"], r["p_inf_max"] + TOL)
                    self.assertLessEqual(r["p_sup_min"], r["p_sup_max"] + TOL)
                    self.assertLessEqual(r["delta_min"], verdade + TOL)
                    self.assertGreaterEqual(r["delta_max"], verdade - TOL)
                    # A faixa contém o conjunto possível: ninguém cruza as duas janelas do mesmo corte.
                    self.assertEqual(r["n_sem_escore_cruzam_ambas_janelas"], 0)
                    self.assertFalse(r["exclusividade_restringe_extremos"])
                    testados += 1
        self.assertGreater(testados, 500)

    def test_mais_informacao_da_limites_aninhados(self) -> None:
        rng = np.random.default_rng(SEMENTE + 3)
        for _ in range(150):
            m = mundo_sintetico(rng, n_com=int(rng.integers(20, 120)), n_sem=int(rng.integers(1, 80)))
            # Conjunto informado SINTÉTICO: faixa intersectada com uma vizinhança da posição verdadeira.
            lo_i = np.maximum(m["lo"], m["verdade"] - rng.integers(0, 60, size=len(m["verdade"])))
            hi_i = np.minimum(m["hi"], m["verdade"] + rng.integers(0, 60, size=len(m["verdade"])))
            for c in E2.CORTES_MIL:
                for h in E2.JANELAS_MIL:
                    largo = E2.limites_janela(m["s"], m["d"], m["lo"], m["hi"], c, h)
                    estreito = E2.limites_janela(m["s"], m["d"], lo_i, hi_i, c, h)
                    if math.isnan(largo["delta_min"]) or math.isnan(estreito["delta_min"]):
                        continue
                    self.assertGreaterEqual(estreito["delta_min"], largo["delta_min"] - TOL)
                    self.assertLessEqual(estreito["delta_max"], largo["delta_max"] + TOL)
                    verdade = delta_verdadeiro(m, c, h)
                    if not math.isnan(verdade):
                        self.assertLessEqual(estreito["delta_min"], verdade + TOL)
                        self.assertGreaterEqual(estreito["delta_max"], verdade - TOL)

    def test_conjunto_informado_dentro_da_faixa(self) -> None:
        sem = pd.DataFrame({  # municípios SINTÉTICOS sem escore
            "faixa_lo": [0, 301, 401, 301],
            "faixa_hi": [300, 400, 1000, 400],
            "ivs10_mil": [280, 350, 600, 100],  # o último contradiz a faixa: [-14, 289] fora de [301, 400]
        })
        lo_p, hi_p, vazios_p = E2.conjuntos_possiveis(sem, "pior_caso", -114, 189)
        lo_i, hi_i, vazios_i = E2.conjuntos_possiveis(sem, "informado", -114, 189)
        self.assertEqual((lo_p.tolist(), hi_p.tolist(), vazios_p), ([0, 301, 401, 301], [300, 400, 1000, 400], 0))
        self.assertTrue(((lo_i >= lo_p) & (hi_i <= hi_p) & (lo_i <= hi_i)).all())
        self.assertEqual((lo_i.tolist(), hi_i.tolist()), ([166, 301, 486, 301], [300, 400, 789, 400]))
        self.assertEqual(vazios_i, 1)  # intersecção vazia volta à faixa inteira


class TestSaidasReaisE2(unittest.TestCase):
    """Saídas empíricas versionadas (arredondadas a 6 casas)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tab = pd.read_csv(ROOT / "output" / "rdd_bolsa" / "E2_limites.csv")
        cls.resumo = json.loads((ROOT / "output" / "rdd_bolsa" / "E2_limites_resumo.json").read_text(encoding="utf-8"))

    def test_ordenacao_dos_limites(self) -> None:
        t = self.tab
        eps = 2e-6
        self.assertEqual(len(t), 2 * 2 * 3 * 2)  # ciclos x cortes x janelas x cenários
        self.assertTrue((t["p_inf_min"] <= t["p_inf_max"] + eps).all())
        self.assertTrue((t["p_sup_min"] <= t["p_sup_max"] + eps).all())
        self.assertTrue((t["delta_min"] <= t["delta_max"] + eps).all())
        self.assertTrue((t["delta_min"] >= t["p_sup_min"] - t["p_inf_max"] - eps).all())
        self.assertTrue((t["delta_max"] <= t["p_sup_max"] - t["p_inf_min"] + eps).all())

    def test_informado_aninhado_no_pior_caso(self) -> None:
        chave = ["ciclo", "corte", "h"]
        pior = self.tab[self.tab["cenario"] == "pior_caso"].set_index(chave)
        inf = self.tab[self.tab["cenario"] == "informado"].set_index(chave)
        self.assertEqual(len(pior), 12)
        self.assertTrue((inf["delta_min"] >= pior.loc[inf.index, "delta_min"] - 2e-6).all())
        self.assertTrue((inf["delta_max"] <= pior.loc[inf.index, "delta_max"] + 2e-6).all())

    def test_exclusividade_nunca_restringe_nos_dados(self) -> None:
        met = self.resumo["metodo_extremos"]
        self.assertFalse(met["exclusividade_restringe_algum_extremo"])
        self.assertTrue(all(d["n_sem_escore_cruzam_ambas_janelas"] == 0 for d in met["detalhe_por_especificacao"]))


if __name__ == "__main__":
    unittest.main()
