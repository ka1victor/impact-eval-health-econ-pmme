"""Invariantes do diagnóstico salário–IVS e provimento duradouro."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "output" / "rdd_bolsa" / "diagnostico_viabilidade_salario_ivs.json"


class ViabilidadeSalarioIvsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_offer_counts_are_frozen(self) -> None:
        offer = self.report["oferta_e_bolsa"]
        self.assertEqual(offer["celulas_cnes_curso"], 1295)
        self.assertEqual(offer["municipios"], 368)
        self.assertEqual(offer["cursos"], 16)
        self.assertEqual(offer["vagas_publicadas"], 1823)
        self.assertEqual(offer["vagas_imediatas_publicadas"], 678)
        self.assertEqual(offer["vagas_reserva_publicadas"], 1145)

    def test_rdd_remains_blocked(self) -> None:
        running = self.report["running_variable"]
        self.assertEqual(running["municipios_faixa_reproduzida"], 191)
        self.assertEqual(running["municipios_faixa_divergente"], 177)
        self.assertEqual(
            running["portao_rdd"],
            "BLOQUEADO_R1_REGRA_E_ESCORE_NAO_RECONSTRUIDOS",
        )

    def test_support_is_municipal_and_not_authorization(self) -> None:
        support = self.report["running_variable"]["suporte_preliminar_nao_autorizativo"]
        lookup = {(row["cutoff"], row["janela"]): row for row in support}
        self.assertEqual(lookup[(0.4, 0.01)]["total"], 20)
        self.assertEqual(lookup[(0.5, 0.01)]["total"], 10)

    def test_cnes_scope_and_maturity(self) -> None:
        cnes = self.report["cnes"]
        self.assertEqual(cnes["competencias"], 26)
        self.assertEqual(cnes["competencia_inicial"], "202406")
        self.assertEqual(cnes["competencia_final"], "202607")
        self.assertEqual(
            cnes["presenca_12m_coorte_entrantes_ate_202601"],
            "AGUARDA_CNES_202701",
        )

    def test_language_gates(self) -> None:
        modules = self.report["decisao_por_modulo"]
        self.assertEqual(
            modules["efeito_causal_do_ivs"], "NAO_E_ESTIMANDO_DEFENSAVEL"
        )
        self.assertEqual(
            modules["retencao_individual_6m_12m"],
            "BLOQUEADA_SEM_ID_VAGA_E_ID_PROFISSIONAL_ESTAVEIS",
        )
        self.assertFalse(self.report["veredito"]["avaliacao_causal_rdd_garantida"])


if __name__ == "__main__":
    unittest.main()
