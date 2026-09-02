"""Invariantes do portão A2 — tipologia territorial."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "output" / "tema_trabalho" / "manifesto_tipologia_territorial.json"
MATRIX = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
SUPORTE = ROOT / "output" / "tema_trabalho" / "suporte_estratos_territoriais.csv"


class TipologiaTerritorialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.matrix = pd.read_parquet(MATRIX)
        cls.suporte = pd.read_csv(SUPORTE)

    def test_gate_approved_four_strata(self) -> None:
        self.assertEqual(self.gate["portao"], "APROVADO_4_ESTRATOS")
        self.assertTrue(self.gate["criterios"]["cobertura_populacao_A1"])
        self.assertTrue(self.gate["criterios"]["nenhum_NAO_CLASSIFICADO_em_A1"])
        self.assertFalse(self.gate["decisao"]["consultou_outcomes"])
        self.assertIn("capital", self.gate["decisao"]["estrutura_minima"])
        self.assertIn("interior_remoto", self.gate["decisao"]["estrutura_minima"])

    def test_coverage_integral_A1(self) -> None:
        self.assertEqual(self.gate["populacao"]["universo_A1_municipios"], 540)
        self.assertEqual(self.gate["populacao"]["municipios_A1_classificados_4_estratos"], 540)
        a1 = self.matrix[self.matrix["in_populacao_A1"]]
        self.assertEqual(len(a1), 540)
        self.assertEqual((a1["estrato"] == "NAO_CLASSIFICADO").sum(), 0)
        # sem inferir remoticidade apenas por ser não capital — metropolitano e próximo devem existir
        estratos_a1 = set(a1["estrato"].unique())
        self.assertIn("metropolitano", estratos_a1)
        self.assertIn("interior_proximo_polo", estratos_a1)
        self.assertIn("interior_remoto", estratos_a1)
        self.assertIn("capital", estratos_a1)

    def test_strata_counts_match_manifest(self) -> None:
        # A1 distribution congelada
        counts = self.matrix[self.matrix["in_populacao_A1"]]["estrato"].value_counts().to_dict()
        self.assertEqual(counts.get("capital"), 25)
        self.assertEqual(counts.get("metropolitano"), 104)
        self.assertEqual(counts.get("interior_proximo_polo"), 235)
        self.assertEqual(counts.get("interior_remoto"), 176)

    def test_no_outcome_columns_consulted(self) -> None:
        lowered = [c.lower() for c in self.matrix.columns]
        forbidden = ["confirmacao", "homologacao", "outcome", "alocacao", "candidat"]
        for frag in forbidden:
            self.assertFalse(any(frag in c for c in lowered), f"coluna proibida com '{frag}' encontrada")

    def test_ivs_canonical_and_missing_rule(self) -> None:
        # 5 novos municípios pós-2010 sem IVS — única falta nacional
        self.assertEqual(self.matrix["flag_ivs_missing"].sum(), 5)
        novos = set(self.gate["populacao"]["municipios_novos_pos2010_sem_IVS"])
        self.assertEqual(novos, {"1504752", "4212650", "4220000", "4314548", "5006275"})
        # nenhum A1 com NAO_CLASSIFICADO
        self.assertEqual(len(self.gate["populacao"]["nao_classificados_em_A1"]), 0)

    def test_continuous_measures_preserved(self) -> None:
        # População e IVS presentes para A1 (exceto 5 novos que não estão em A1)
        a1 = self.matrix[self.matrix["in_populacao_A1"]]
        self.assertEqual(a1["ivs_2010"].notna().sum(), 540)
        self.assertEqual(a1["populacao_2010"].notna().sum(), 540)
        # Estoque pré-oferta disponível para os municípios do quadro Ch1 (368)
        self.assertEqual(int(a1["estoque_especialistas_pre_12m_media"].notna().sum()), 368)

    def test_suporte_totals_and_no_outcome(self) -> None:
        total = self.suporte[self.suporte["estrato"] == "total"].iloc[0]
        self.assertEqual(int(total["n_municipios_populacao_A1"]), 540)
        self.assertEqual(int(total["n_celulas_quadro_ch1"]), 1295)
        self.assertEqual(int(total["vagas_imediatas_publicadas"]), 678)
        self.assertEqual(int(total["vagas_reserva_publicadas"]), 1145)
        # suporte não contém colunas de outcome
        cols = [c.lower() for c in self.suporte.columns]
        self.assertFalse(any("confirm" in c for c in cols))
        self.assertFalse(any("homolog" in c for c in cols))

    def test_matrix_key_uniqueness_and_privacy(self) -> None:
        self.assertEqual(self.matrix.duplicated(subset=["co_ibge_6d"]).sum(), 0)
        self.assertEqual(len(self.matrix), 5570)
        lowered = [c.lower() for c in self.matrix.columns]
        self.assertFalse(any("cpf" in c for c in lowered))
        self.assertFalse(any("candidato" in c for c in lowered))


if __name__ == "__main__":
    unittest.main()
