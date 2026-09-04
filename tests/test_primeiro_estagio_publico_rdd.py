"""Invariantes do primeiro estágio público candidato do RDD de bolsa."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "output" / "rdd_bolsa" / "a01_primeiro_estagio_publico.json"


class PrimeiroEstagioPublicoRddTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_unidade_e_universo_sao_municipais(self) -> None:
        self.assertEqual(self.report["n_municipios"], 368)
        self.assertIn("municipio", self.report["unidade"])

    def test_ivspublico_nao_tem_primeiro_estagio_estavel(self) -> None:
        self.assertEqual(
            self.report["portao_fuzzy_com_ivs_publico"],
            "REPROVADO_SEM_SALTO_ESTAVEL",
        )
        self.assertFalse(
            self.report["resumo_cutoffs"]["0.4"]["salto_estavel_em_todas_as_janelas"]
        )
        self.assertFalse(
            self.report["resumo_cutoffs"]["0.5"]["salto_estavel_em_todas_as_janelas"]
        )

    def test_faixa_perto_de_0500_nao_muda_valor(self) -> None:
        linhas = {
            (row["corte_taxonomia"], row["bandwidth"]): row
            for row in self.report["estimativas"]
        }
        for janela in (0.01, 0.02, 0.03, 0.05):
            row = linhas[(0.5, janela)]
            self.assertAlmostEqual(row["media_abaixo_mil_brl"], 20.0)
            self.assertAlmostEqual(row["media_acima_mil_brl"], 20.0)
            self.assertEqual(row["salto_local_linear_mil_brl"], 0.0)
            self.assertEqual(row["erro_padrao_hc1_mil_brl"], 0.0)
            self.assertIsNone(row["p_valor"])

    def test_resultado_e_diagnostico_nao_autorizativo(self) -> None:
        self.assertEqual(self.report["status"], "DIAGNOSTICO_NAO_AUTORIZATIVO")
        self.assertIn("não suficiente", self.report["interpretacao"])


if __name__ == "__main__":
    unittest.main()
