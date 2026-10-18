"""Testes do E4 (proporção de células preenchidas): saídas reais e estimador sintético.

Duas partes:

1. Conferência das saídas reais versionadas do 08a: a proporção preenchida
   reconstruída dos brutos é 393/1.295 (Y1) e 461/1.295 (Y2), em 368
   municípios, sem nenhuma divergência célula a célula contra a fonte canônica
   (`output/rdd_bolsa/E4_validacao_reconstrucao.json` e
   `output/rdd_bolsa/E4_proporcao_municipio.csv`).
2. Estimadores de `scripts/rdd_bolsa/08_estimar_E4_proporcao.py` com DADOS
   SINTÉTICOS (municípios, escores, posições e outcomes gerados em memória com
   semente fixa; nada é observação empírica e nada é gravado): E4a recupera
   saltos conhecidos; a média extrema do E4b é o ótimo de força bruta; os
   limites do E4b contêm o valor verdadeiro de um mundo sintético; os limites
   de Lee aparam o lado certo.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "08_estimar_E4_proporcao.py"
_bytecode = sys.dont_write_bytecode  # o script desliga a gravação de bytecode ao importar o E1
SPEC = importlib.util.spec_from_file_location("e4_proporcao", SCRIPT)
E4 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E4)
sys.dont_write_bytecode = _bytecode

VALIDACAO = ROOT / "output" / "rdd_bolsa" / "E4_validacao_reconstrucao.json"
PROPORCAO = ROOT / "output" / "rdd_bolsa" / "E4_proporcao_municipio.csv"
RESUMO = ROOT / "output" / "rdd_bolsa" / "E4_resumo.json"

SEMENTE = 20261018
TOL = 1e-12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


class TestReconstrucaoReal(unittest.TestCase):
    """Saídas empíricas versionadas do 08a."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.val = json.loads(VALIDACAO.read_text(encoding="utf-8"))
        cls.mun = pd.read_csv(PROPORCAO, dtype={"co_ibge": str})

    def test_totais_393_e_461_de_1295(self) -> None:
        t = self.val["totais"]
        self.assertEqual((t["y1_canonica"], t["y2_canonica"], t["celulas"], t["municipios"]), (393, 461, 1295, 368))
        self.assertEqual((t["y1_reconstruida"], t["y2_reconstruida"]), (393, 461))
        self.assertEqual((t["celulas_reconstruidas"], t["municipios_reconstruidos"]), (1295, 368))
        self.assertTrue(t["confere_esperado"])
        self.assertTrue(self.val["reconstrucao_completa"])
        self.assertEqual(self.val["pendencias"], [])

    def test_nenhuma_divergencia_celula_a_celula(self) -> None:
        v = self.val["validacao_celula_a_celula"]
        for chave in ("celulas_divergentes_y1", "celulas_divergentes_y2", "celulas_divergentes_contagens",
                      "celulas_divergentes_atributos"):
            self.assertEqual(v[chave], 0, chave)
        self.assertEqual(v["divergencias"], [])
        self.assertEqual(v["celulas_em_ambas"], 1295)
        self.assertEqual(v["celulas_batidas_y1_y2_contagens_e_atributos"], 1295)

    def test_csv_por_municipio(self) -> None:
        m = self.mun
        self.assertEqual(list(m.columns), ["co_ibge", "faixa_anunciada", "n_celulas", "n_celulas_y1",
                                           "n_celulas_y2", "y1", "y2"])  # sem nome nem CPF
        self.assertFalse(self.val["dados_pessoais_gravados"])
        self.assertEqual(len(m), 368)
        self.assertTrue(m["co_ibge"].is_unique)
        self.assertEqual((m["n_celulas"].sum(), m["n_celulas_y1"].sum(), m["n_celulas_y2"].sum()), (1295, 393, 461))
        self.assertTrue(((m["n_celulas_y1"] <= m["n_celulas_y2"]) & (m["n_celulas_y2"] <= m["n_celulas"])).all())
        self.assertTrue(np.allclose(m["y1"], m["n_celulas_y1"] / m["n_celulas"], rtol=0, atol=1e-9))
        self.assertTrue(np.allclose(m["y2"], m["n_celulas_y2"] / m["n_celulas"], rtol=0, atol=1e-9))
        self.assertEqual(sha256(PROPORCAO), self.val["saida_municipio"]["sha256"])

    def test_e4_leu_o_insumo_conferido(self) -> None:
        resumo = json.loads(RESUMO.read_text(encoding="utf-8"))
        conf = resumo["populacao"]["outcomes_conferencia"]
        self.assertTrue(conf["confere_com_fonte_canonica"])
        self.assertEqual((conf["celulas"], conf["celulas_y1"], conf["celulas_y2"]), (1295, 393, 461))


class TestE4aSintetico(unittest.TestCase):
    def test_constante_local_recupera_diferenca_de_medias(self) -> None:
        s = np.arange(251, 351).repeat(2)
        y = 0.2 + 0.15 * (s > 300)
        r = E4.e4a(s, y, np.ones(len(s)), 300, 50, linear=False)
        self.assertAlmostEqual(r["estimativa"], 0.15, places=12)
        self.assertEqual((r["n_inf"], r["n_sup"]), (100, 100))

    def test_local_linear_recupera_salto_com_tendencia(self) -> None:
        s = np.arange(220, 381)
        x = (s - 300) / 1000
        y = 0.2 + 1.0 * x + 0.15 * (s > 300) - 0.5 * x * (s > 300)
        r = E4.e4a(s, y, np.ones(len(s)), 300, 50, linear=True)
        self.assertAlmostEqual(r["estimativa"], 0.15, places=10)
        self.assertLess(r["ep"], 1e-8)

    def test_ponderacao_por_celulas(self) -> None:
        s = np.array([290, 295, 300, 305, 310, 320])
        y = np.array([0.0, 1.0, 0.5, 1.0, 0.0, 0.5])
        peso = np.array([1.0, 3.0, 2.0, 1.0, 1.0, 2.0])
        r = E4.e4a(s, y, peso, 300, 50, linear=False)
        esperado = np.average(y[3:], weights=peso[3:]) - np.average(y[:3], weights=peso[:3])
        self.assertAlmostEqual(r["estimativa"], esperado, places=12)

    def test_suporte_insuficiente_nao_estima(self) -> None:
        r = E4.e4a(np.array([300, 300, 301]), np.array([0.0, 1.0, 1.0]), np.ones(3), 300, 50, linear=True)
        self.assertTrue(math.isnan(r["estimativa"]))
        self.assertIn("nao estimado", r["nota"])


class TestE4bSintetico(unittest.TestCase):
    def test_media_extrema_e_o_otimo_de_forca_bruta(self) -> None:
        rng = np.random.default_rng(SEMENTE)
        for _ in range(300):
            n_fix, n_poss = int(rng.integers(0, 4)), int(rng.integers(0, 8))
            y_fix, y_poss = rng.integers(0, 5, n_fix) / 4, rng.integers(0, 5, n_poss) / 4
            w_fix, w_poss = rng.integers(1, 6, n_fix).astype(float), rng.integers(1, 6, n_poss).astype(float)
            medias = []
            for k in range(n_poss + 1):
                for sub in itertools.combinations(range(n_poss), k):
                    idx = list(sub)
                    den = w_fix.sum() + w_poss[idx].sum()
                    if den > 0:
                        medias.append(((w_fix * y_fix).sum() + (w_poss[idx] * y_poss[idx]).sum()) / den)
            minimo, _ = E4.media_extrema(y_fix, w_fix, y_poss, w_poss, maximizar=False)
            maximo, _ = E4.media_extrema(y_fix, w_fix, y_poss, w_poss, maximizar=True)
            if not medias:
                self.assertTrue(math.isnan(minimo) and math.isnan(maximo))
                continue
            self.assertAlmostEqual(minimo, min(medias), places=12)
            self.assertAlmostEqual(maximo, max(medias), places=12)

    def _mundo(self, rng: np.random.Generator, n_com: int, n_sem: int) -> tuple[pd.DataFrame, np.ndarray]:
        """P1 SINTÉTICA: S = 1 com escore; S = 0 com posição verdadeira só dentro da faixa."""
        s = rng.integers(150, 651, size=n_com + n_sem)
        faixa = [next(f for f, (a, b) in E4.INTERVALO_FAIXA_MIL.items() if a <= v <= b) for v in s]
        n_cel = rng.integers(1, 9, size=n_com + n_sem)
        n_y1 = rng.binomial(n_cel, 0.35)
        p = pd.DataFrame({
            "S": np.r_[np.ones(n_com, dtype=int), np.zeros(n_sem, dtype=int)],
            "s_mil": np.r_[s[:n_com].astype(float), np.full(n_sem, np.nan)],
            "faixa_anunciada": faixa,
            "n_celulas": n_cel,
            "y1": n_y1 / n_cel,
        })
        p["faixa_lo"] = p["faixa_anunciada"].map(lambda f: E4.INTERVALO_FAIXA_MIL[f][0])
        p["faixa_hi"] = p["faixa_anunciada"].map(lambda f: E4.INTERVALO_FAIXA_MIL[f][1])
        return p, s

    def test_limites_contem_a_diferenca_verdadeira(self) -> None:
        rng = np.random.default_rng(SEMENTE + 1)
        testados = 0
        for _ in range(120):
            p, verdade = self._mundo(rng, int(rng.integers(20, 100)), int(rng.integers(0, 60)))
            sem = p[p["S"] == 0]
            conj = E4.conjuntos_possiveis(sem, "pior_caso")[:2]
            for c in E4.CORTES_MIL:
                for h in E4.JANELAS_MIL:
                    inf = (verdade > c - h) & (verdade <= c)
                    sup = (verdade > c) & (verdade <= c + h)
                    if not inf.any() or not sup.any():
                        continue
                    for ponderacao in E4.PONDERACOES:
                        w = np.ones(len(p)) if ponderacao == "simples" else p["n_celulas"].to_numpy(float)
                        y = p["y1"].to_numpy()
                        dif = np.average(y[sup], weights=w[sup]) - np.average(y[inf], weights=w[inf])
                        r = E4.e4b(p, conj, "Y1", ponderacao, c, h)
                        self.assertLessEqual(r["limite_inf"], dif + TOL)
                        self.assertGreaterEqual(r["limite_sup"], dif - TOL)
                        self.assertLessEqual(r["media_inf_min"], r["media_inf_max"] + TOL)
                        self.assertLessEqual(r["media_sup_min"], r["media_sup_max"] + TOL)
                        testados += 1
        self.assertGreater(testados, 500)

    def test_sem_municipio_sem_escore_colapsa_na_diferenca_de_medias(self) -> None:
        rng = np.random.default_rng(SEMENTE + 2)
        p, s = self._mundo(rng, 300, 0)
        vazio = np.array([], dtype=int)
        r = E4.e4b(p, (vazio, vazio), "Y1", "simples", 300, 50)
        y = p["y1"].to_numpy()
        dif = y[(s > 300) & (s <= 350)].mean() - y[(s > 250) & (s <= 300)].mean()
        self.assertAlmostEqual(r["limite_inf"], dif, places=12)
        self.assertAlmostEqual(r["limite_sup"], dif, places=12)


class TestLeeSintetico(unittest.TestCase):
    def test_sem_selecao_diferencial_e_a_diferenca_de_medias(self) -> None:
        r = E4.lee(np.array([0.0, 1.0]), np.array([0.5, 1.0]), 1.0)
        self.assertEqual((r["limite_inf"], r["limite_sup"], r["lado_aparado"]), (0.25, 0.25, "nenhum"))

    def test_rho_maior_que_1_apara_o_lado_superior(self) -> None:
        r = E4.lee(np.array([0.5]), np.array([0.0, 0.0, 1.0, 1.0]), 2.0)
        self.assertEqual(r["lado_aparado"], "superior")
        self.assertAlmostEqual(r["fracao_aparada"], 0.5)
        self.assertAlmostEqual(r["limite_inf"], -0.5)
        self.assertAlmostEqual(r["limite_sup"], 0.5)

    def test_rho_menor_que_1_apara_o_lado_inferior(self) -> None:
        r = E4.lee(np.array([0.0, 0.0, 1.0, 1.0]), np.array([0.5]), 0.5)
        self.assertEqual(r["lado_aparado"], "inferior")
        self.assertAlmostEqual(r["limite_inf"], -0.5)
        self.assertAlmostEqual(r["limite_sup"], 0.5)

    def test_media_aparada_com_peso_fracionario(self) -> None:
        y = np.array([1.0, 0.0])
        self.assertAlmostEqual(E4.media_aparada(y, 0.75, manter_baixos=True), 1 / 3)
        self.assertAlmostEqual(E4.media_aparada(y, 0.75, manter_baixos=False), 2 / 3)
        self.assertAlmostEqual(E4.media_aparada(y, 1.0, manter_baixos=True), 0.5)

    def test_limites_ordenados_e_contem_a_diferenca_sem_aparo(self) -> None:
        rng = np.random.default_rng(SEMENTE + 3)
        for _ in range(300):
            y_inf = rng.integers(0, 5, size=int(rng.integers(1, 30))) / 4
            y_sup = rng.integers(0, 5, size=int(rng.integers(1, 30))) / 4
            rho = float(np.exp(rng.normal(0, 0.4)))
            r = E4.lee(y_inf, y_sup, rho)
            self.assertLessEqual(r["limite_inf"], r["limite_sup"] + TOL)
            self.assertLessEqual(r["limite_inf"], y_sup.mean() - y_inf.mean() + TOL)
            self.assertGreaterEqual(r["limite_sup"], y_sup.mean() - y_inf.mean() - TOL)

    def test_rho_s_e_o_estimador_principal_do_e1(self) -> None:
        rng = np.random.default_rng(SEMENTE + 4)
        s = rng.integers(200, 501, size=600)
        r = E4.rho_s(s, 300)
        cont = pd.Series(s).value_counts().sort_index()
        e1 = E4.E1.ajustar_poisson(cont, 300, 50, linear=True, excluir_corte=False)
        self.assertEqual(r["rho"], e1["rho"])
        self.assertEqual((r["n_esq"], r["n_dir"]), (e1["n_esq"], e1["n_dir"]))


if __name__ == "__main__":
    unittest.main()
