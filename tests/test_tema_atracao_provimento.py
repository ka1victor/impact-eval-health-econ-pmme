"""Invariantes da auditoria do tema atração e provimento fora das capitais."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "output" / "tema_trabalho" / "diagnostico_atracao_provimento_interior.json"


class TemaAtracaoProvimentoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_territorial_support_is_frozen(self) -> None:
        territory = self.report["oferta_e_resultados_publicos"]["por_territorio"]
        self.assertEqual(territory["total"]["municipios_oferta"], 368)
        self.assertEqual(territory["fora_capital"]["municipios_oferta"], 350)
        self.assertEqual(territory["fora_capital"]["vagas_imediatas"], 593)
        self.assertEqual(territory["capital"]["municipios_vaga_imediata"], 14)

    def test_public_funnel_requires_reconciliation(self) -> None:
        funnel = self.report["oferta_e_resultados_publicos"]
        self.assertEqual(funnel["alocacoes_confirmadas_publicadas"], 468)
        self.assertEqual(funnel["celulas_alocacao_sem_chave_da_oferta_original"], 0)
        self.assertEqual(
            funnel["por_modalidade_original"]["RESERVA"]["alocacoes_confirmadas"],
            211,
        )
        self.assertEqual(funnel["celulas_alocacao_acima_da_capacidade_publicada"], 10)
        self.assertEqual(funnel["homologacoes_publicadas"], 316)
        self.assertEqual(funnel["homologacoes_em_chave_da_oferta_original"], 296)

    def test_cnes_is_aggregate_not_individual_retention(self) -> None:
        cnes = self.report["painel_cnes"]
        self.assertEqual(cnes["competencia_inicial"], "202406")
        self.assertEqual(cnes["competencia_final"], "202607")
        self.assertEqual(cnes["por_territorio"]["fora_capital"]["competencias"], 26)
        self.assertEqual(
            cnes["por_territorio"]["fora_capital"]["celulas_municipio_curso"],
            1122,
        )
        self.assertFalse(cnes["retencao_individual_identificada"])

    def test_language_gate(self) -> None:
        verdict = self.report["veredito"]
        self.assertTrue(verdict["tema_faz_sentido"])
        self.assertIn("persistência da oferta", verdict["formulacao_defensavel"])
        self.assertIn("retenção individual", verdict["formulacao_nao_defensavel_hoje"])


if __name__ == "__main__":
    unittest.main()
