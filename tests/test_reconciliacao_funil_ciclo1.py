"""Invariantes do portão A1 de atração administrativa."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "output" / "tema_trabalho" / "portao_denominador.json"
MATRIX = ROOT / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"


class ReconciliacaoFunilCiclo1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.matrix = pd.read_parquet(MATRIX)

    def test_gate_approves_cell_not_vacancy(self) -> None:
        self.assertEqual(self.gate["portao"], "APROVADO_CELULA")
        self.assertFalse(self.gate["decisao"]["denominador_por_vaga"])
        self.assertTrue(self.gate["decisao"]["denominador_por_celula"])
        self.assertIn(
            "taxa de preenchimento por vaga",
            self.gate["decisao"]["outcomes_bloqueados"],
        )

    def test_allocation_versions_are_not_summed(self) -> None:
        comparison = self.gate["chamada_1"]["versoes_alocacao"]["comparacao"]
        self.assertEqual(comparison["registros_versao_anterior"], 1671)
        self.assertEqual(comparison["registros_versao_canonica"], 1671)
        self.assertEqual(comparison["chaves_adicionadas"], 0)
        self.assertEqual(comparison["chaves_removidas"], 0)
        self.assertEqual(comparison["registros_com_conteudo_alterado"], 3)
        self.assertEqual(comparison["registros_com_marcacao_em_coluna_adicional"], 1)

    def test_first_call_funnel_and_capacity(self) -> None:
        call = self.gate["chamada_1"]
        self.assertEqual(call["quadro_original"]["celulas"], 1295)
        self.assertEqual(call["quadro_original"]["vagas_imediatas"], 678)
        self.assertEqual(call["quadro_original"]["vagas_reserva"], 1145)
        self.assertEqual(call["confirmacoes"], 468)
        self.assertEqual(call["propostas_realocacao"], 59)
        self.assertEqual(call["homologacoes"], 316)
        self.assertEqual(call["homologacoes_fora_do_quadro_original"], 20)
        self.assertEqual(call["celulas_homologacao_fora_do_quadro_original"], 18)
        self.assertEqual(call["celulas_confirmacao_acima_vagas_imediatas"], 10)
        self.assertEqual(call["celulas_confirmacao_acima_capacidade_total_publicada"], 15)
        self.assertEqual(call["confirmacoes_excedentes_capacidade_total_publicada"], 20)
        self.assertEqual(sum(call["trilha_homologacao"].values()), 316)

    def test_second_call_is_not_simple_cumulative_list(self) -> None:
        call = self.gate["chamada_2"]
        self.assertEqual(call["quadro_cadastro_reserva"]["celulas"], 1762)
        self.assertEqual(
            call["quadro_cadastro_reserva"]["vagas_reserva_publicadas"], 2896
        )
        self.assertFalse(
            call["quadro_cadastro_reserva"]["vagas_imediatas_numericas_publicadas"]
        )
        self.assertEqual(call["publicacao_preliminar"]["registros"], 98)
        self.assertEqual(call["publicacao_preliminar"]["classificados"], 33)
        self.assertEqual(call["classificacao_final"]["alocados"], 374)
        homolog = call["segunda_lista_homologados"]
        self.assertEqual(homolog["registros"], 581)
        self.assertEqual(homolog["reaparecem_da_primeira_lista"], 299)
        self.assertEqual(homolog["novos_na_segunda_lista"], 282)
        self.assertEqual(homolog["homologados_ch1_ausentes_na_segunda_lista"], 17)
        self.assertEqual(homolog["total_distinto_observado_nas_duas_listas"], 598)
        self.assertEqual(sum(homolog["trilha_novos"].values()), 581)

    def test_matrix_key_counts_and_privacy(self) -> None:
        key = ["ciclo", "chamada", "versao_quadro", "co_cnes_7d", "cod_curso"]
        self.assertEqual(len(self.matrix), 3323)
        self.assertEqual(self.matrix.duplicated(key).sum(), 0)
        self.assertEqual(self.matrix["registro_fora_do_quadro_publicado"].sum(), 266)
        lowered = [column.lower() for column in self.matrix.columns]
        self.assertFalse(any("cpf" in column for column in lowered))
        self.assertFalse(any("candidato" in column for column in lowered))
        self.assertFalse(any("person" in column for column in lowered))

    def test_event_totals_are_preserved(self) -> None:
        call1 = self.matrix[self.matrix["chamada"] == 1]
        call2 = self.matrix[self.matrix["chamada"] == 2]
        self.assertEqual(call1["n_confirmacoes_ch1"].sum(), 468)
        self.assertEqual(call1["n_homologacoes_ch1"].sum(), 316)
        self.assertEqual(call2["n_classificados_preliminares_ch2"].sum(), 33)
        self.assertEqual(call2["n_alocados_finais_ch2"].sum(), 374)
        self.assertEqual(call2["n_homologacoes_lista_ch2"].sum(), 581)
        self.assertEqual(call2["n_homologacoes_novas_ch2"].sum(), 282)


if __name__ == "__main__":
    unittest.main()
