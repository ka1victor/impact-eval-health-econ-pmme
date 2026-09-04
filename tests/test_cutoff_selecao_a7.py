"""Invariantes A7 — corte de seleção candidato e trava de causalidade."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "tema_trabalho"
SUPPORT = OUT / "A7_tabela_01_suporte_cutoffs.csv"
RESULTS = OUT / "A7_tabela_02_descontinuidades_preliminares.csv"
SUMMARY = OUT / "A7_cutoff_selecao_resumo.json"
REPORT = OUT / "A7_relatorio_cutoff_selecao.md"


class CutoffSelecaoA7Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.support = pd.read_csv(SUPPORT)
        cls.results = pd.read_csv(RESULTS)
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_entregaveis_existem(self) -> None:
        for path in [SUPPORT, RESULTS, SUMMARY, REPORT]:
            self.assertTrue(path.exists(), f"missing {path}")
            self.assertGreater(path.stat().st_size, 200)

    def test_suporte_reproduzido(self) -> None:
        expected = {
            "2025_C1_CH1": 136,
            "2025_C1_CH2": 57,
            "2026_C2_CH2": 56,
            "2026_C3_CH1": 174,
        }
        observed = dict(zip(self.support["ciclo_chamada"], self.support["pares_adjacentes"], strict=True))
        self.assertEqual(observed, expected)
        self.assertEqual(int(self.support["pares_adjacentes"].sum()), 423)
        self.assertEqual(int(self.support["pares_mesmo_escore_publicado"].sum()), 184)

    def test_descontinuidades_2025(self) -> None:
        main = self.results[self.results["amostra"].eq("todos_pares_adjacentes")]
        expected = {
            ("2025_C1_CH1", "homologated"): 0.4632352941,
            ("2025_C1_CH1", "active_snapshot"): 0.2720588235,
            ("2025_C1_CH2", "homologated"): 0.7719298246,
            ("2025_C1_CH2", "active_snapshot"): 0.5614035088,
        }
        for key, value in expected.items():
            row = main[(main["ciclo_chamada"] == key[0]) & (main["desfecho"] == key[1])]
            self.assertEqual(len(row), 1)
            self.assertAlmostEqual(float(row.iloc[0]["diferenca"]), value, places=8)
            self.assertGreater(float(row.iloc[0]["ic95_inferior"]), 0)

    def test_mesmo_escore_nao_promovido_a_causal(self) -> None:
        same = self.results[self.results["amostra"].eq("mesmo_escore_publicado")]
        self.assertEqual(int(same[same["ciclo_chamada"].eq("2025_C1_CH1_E_CH2")]["n_pares"].max()), 81)
        self.assertTrue((same["classificacao_inferencial"] == "DESCONTINUIDADE_PRELIMINAR_NAO_CAUSAL").all())
        low = self.report.lower()
        self.assertIn("mesma uf", low)
        self.assertIn("idade", low)
        self.assertIn("ainda não é causal", low)

    def test_status_e_estimando_corretos(self) -> None:
        self.assertEqual(
            self.summary["status"],
            "DESENHO_PROMISSOR_MAS_NAO_CAUSAL_COM_DADOS_PUBLICOS",
        )
        self.assertIn("ITT local", self.summary["estimando_causal_condicional"])
        self.assertIn("primeira opção", self.summary["pergunta_recomendada"])
        self.assertEqual(self.summary["linkage"]["data_snapshot"], "2026-08-12")

    def test_artefatos_nao_persistem_pii(self) -> None:
        forbidden_columns = {"nome", "name", "cpf", "candidate", "candidato", "hash_candidato"}
        for frame in [self.support, self.results]:
            self.assertTrue(forbidden_columns.isdisjoint({str(column).lower() for column in frame.columns}))
        privacy = self.summary["privacidade"].lower()
        self.assertIn("nenhum nome", privacy)
        self.assertIn("nenhum", privacy)


if __name__ == "__main__":
    unittest.main()
