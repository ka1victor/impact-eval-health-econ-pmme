"""Invariantes A8 — corte de escore estrito e efeito local condicional."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "tema_trabalho"
PROTOCOL = OUT / "A8_protocolo_cutoff_escore.json"
SUPPORT = OUT / "A8_tabela_01_suporte_escore_estrito.csv"
ESTIMATES = OUT / "A8_tabela_02_estimativas_escore_estrito.csv"
PLACEBOS = OUT / "A8_tabela_03_placebos_escore_estrito.csv"
SENSITIVITY = OUT / "A8_tabela_04_sensibilidade_gap.csv"
LEAVE_ONE_OUT = OUT / "A8_tabela_05_leave_one_out.csv"
SUMMARY = OUT / "A8_estimativas_cutoff_escore.json"
REPORT = OUT / "A8_relatorio_cutoff_escore.md"
FIGURE = OUT / "A8_figura_01_efeitos_cutoff_escore.png"


class CutoffEscoreEstritoA8Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
        cls.support = pd.read_csv(SUPPORT)
        cls.estimates = pd.read_csv(ESTIMATES)
        cls.placebos = pd.read_csv(PLACEBOS)
        cls.sensitivity = pd.read_csv(SENSITIVITY)
        cls.leave_one_out = pd.read_csv(LEAVE_ONE_OUT)
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.report = REPORT.read_text(encoding="utf-8")

    def test_entregaveis_existem(self) -> None:
        for path in [
            PROTOCOL,
            SUPPORT,
            ESTIMATES,
            PLACEBOS,
            SENSITIVITY,
            LEAVE_ONE_OUT,
            SUMMARY,
            REPORT,
            FIGURE,
        ]:
            self.assertTrue(path.exists(), f"missing {path}")
            self.assertGreater(path.stat().st_size, 200)

    def test_suporte_estrito_reproduzido(self) -> None:
        expected = {
            "2025_C1_CH1": (123, 30, 48, 20, 3),
            "2025_C1_CH2": (53, 6, 28, 10, 2),
            "2026_C2_CH2": (50, 11, 26, 8, 4),
        }
        for cycle, values in expected.items():
            row = self.support[self.support["ciclo_chamada"].eq(cycle)]
            self.assertEqual(len(row), 1)
            observed = tuple(
                int(row.iloc[0][column])
                for column in [
                    "pares_cutoff_ampla_concorrencia",
                    "pares_gap_1_ac",
                    "pares_empate_excluidos",
                    "placebos_abaixo_gap_1_ac",
                    "placebos_acima_gap_1_ac",
                ]
            )
            self.assertEqual(observed, values)
            self.assertEqual(int(row.iloc[0]["violacoes_gap_1"]), 0)

    def test_resultado_principal_2025(self) -> None:
        main = self.estimates[
            self.estimates["ciclo_chamada"].eq("2025_C1_CH1_E_CH2")
            & self.estimates["amostra"].eq("gap_1_ac")
        ]
        expected = {
            "homologacao_mesma_celula": (36, 0.6388888889, 0.4740657432, 2.384185791015625e-07),
            "ativo_mesma_celula_snapshot": (36, 0.3333333333, 0.1352150858, 0.004180908203125),
        }
        for outcome, (n_pairs, difference, ci_low, p_value) in expected.items():
            row = main[main["desfecho"].eq(outcome)]
            self.assertEqual(len(row), 1)
            self.assertEqual(int(row.iloc[0]["n_pares"]), n_pairs)
            self.assertAlmostEqual(float(row.iloc[0]["diferenca"]), difference, places=8)
            self.assertAlmostEqual(float(row.iloc[0]["ic95_convencional_inferior"]), ci_low, places=8)
            self.assertAlmostEqual(float(row.iloc[0]["p_exato_pareado_bicaudal"]), p_value, places=12)
            self.assertEqual(
                row.iloc[0]["classificacao_inferencial"],
                "EFEITO_LOCAL_CONDICIONAL_A_RANDOMIZACAO_LOCAL",
            )

    def test_placebo_abaixo_e_nulo(self) -> None:
        below = self.placebos[self.placebos["amostra"].eq("placebo_abaixo_gap_1_ac")]
        expected = {
            "homologacao_mesma_celula": -1 / 30,
            "ativo_mesma_celula_snapshot": 0.0,
        }
        for outcome, difference in expected.items():
            row = below[below["desfecho"].eq(outcome)]
            self.assertEqual(len(row), 1)
            self.assertEqual(int(row.iloc[0]["n_pares"]), 30)
            self.assertAlmostEqual(float(row.iloc[0]["diferenca"]), difference, places=10)
            self.assertEqual(float(row.iloc[0]["p_exato_pareado_bicaudal"]), 1.0)

    def test_replicacao_2026_e_direcional_mas_imprecisa(self) -> None:
        row = self.estimates[
            self.estimates["ciclo_chamada"].eq("2026_C2_CH2")
            & self.estimates["desfecho"].eq("ativo_mesma_celula_snapshot")
        ]
        self.assertEqual(len(row), 1)
        self.assertEqual(int(row.iloc[0]["n_pares"]), 11)
        self.assertAlmostEqual(float(row.iloc[0]["diferenca"]), 4 / 11, places=10)
        self.assertEqual(float(row.iloc[0]["p_exato_pareado_bicaudal"]), 0.125)
        self.assertEqual(row.iloc[0]["classificacao_inferencial"], "REPLICACAO_DIRECIONAL_IMPRECISA")

    def test_sensibilidades_e_leave_one_out_nao_invertem_sinal(self) -> None:
        valid = self.sensitivity[
            ~self.sensitivity["amostra"].eq("empate_descritivo_nao_causal")
        ]
        self.assertTrue((valid["diferenca"] > 0).all())
        self.assertEqual(set(valid["n_pares"]), {36, 74, 100})
        self.assertTrue((self.leave_one_out["diferenca"] > 0).all())
        self.assertEqual(len(self.leave_one_out), 46)
        self.assertAlmostEqual(float(self.leave_one_out["diferenca"].min()), 0.2727272727, places=8)
        self.assertAlmostEqual(float(self.leave_one_out["diferenca"].max()), 0.7096774194, places=8)

    def test_protocolo_e_linguagem_causal_sao_delimitados(self) -> None:
        self.assertFalse(self.protocol["pre_registro"])
        self.assertTrue(self.protocol["outcomes_previamente_observados"])
        self.assertIn("retrospectiva", self.protocol["nota"].lower())
        self.assertEqual(self.summary["status"], "EFEITO_LOCAL_CAUSAL_CONDICIONAL")
        self.assertEqual(self.summary["grau_de_rigor"], "MODERADO")
        prohibited = self.summary["interpretacao_proibida"].lower()
        self.assertIn("bolsa", prohibited)
        self.assertIn("ivs", prohibited)
        self.assertIn("candidatar", prohibited)
        report = self.report.lower()
        self.assertIn("causalidade condicional", report)
        self.assertIn("nao identifica", report)

    def test_artefatos_nao_persistem_identificadores(self) -> None:
        forbidden_columns = {
            "nome",
            "name",
            "cpf",
            "candidate",
            "candidato",
            "hash_candidato",
            "cell_internal",
            "high_name_internal",
            "low_name_internal",
        }
        for frame in [
            self.support,
            self.estimates,
            self.placebos,
            self.sensitivity,
            self.leave_one_out,
        ]:
            columns = {str(column).lower() for column in frame.columns}
            self.assertTrue(forbidden_columns.isdisjoint(columns))
        self.assertIn("somente em memoria", self.summary["privacidade"].lower())


if __name__ == "__main__":
    unittest.main()
