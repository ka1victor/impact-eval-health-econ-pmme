"""Invariantes do diagnóstico salário–IVS e provimento duradouro.

O diagnóstico é saída do script retirado `scripts/rdd_bolsa/00_*`, que usava
`data/ivs_ipea_2010_municipios.csv` como IVS 2010. A parte de running variable é
registro de failure mode (auditorias 16 e 19): o estado vigente da regra é o do
portão R1 com o IVS 2010 oficial.
"""

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

    def test_bloqueio_da_rdd_e_failure_mode_e_r1_oficial_e_o_vigente(self) -> None:
        # O "bloqueio" deste diagnóstico veio do arquivo de IVS errado.
        self.assertIn("data/ivs_ipea_2010_municipios.csv", self.report["fontes"])
        running = self.report["running_variable"]
        self.assertEqual(running["portao_rdd"], "BLOQUEADO_R1_REGRA_E_ESCORE_NAO_RECONSTRUIDOS")
        # O script que o gera está fora do pipeline.
        import importlib.util
        spec = importlib.util.spec_from_file_location("run_all_viab", ROOT / "run_all.py")
        ra = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ra)
        self.assertNotIn(ROOT / "scripts" / "rdd_bolsa" / "00_diagnosticar_viabilidade_salario_ivs.py", ra.STEPS)
        # Estado vigente: R1 com o IVS 2010 oficial reproduz a regra em toda a população P1.
        r1 = json.loads((ROOT / "output" / "rdd_bolsa" / "portao_r1_ivs_oficial.json").read_text(encoding="utf-8"))
        self.assertEqual(r1["decisao_r1"], "APROVADO_SHARP")
        p1 = r1["populacoes"]["P1"]
        self.assertEqual(p1["regra_reproduz"], p1["municipios"])
        # Nenhum diagnóstico vigente repete o número de divergência do arquivo errado.
        vigente = json.loads((ROOT / "output" / "tema_trabalho" / "diagnostico_atracao_provimento_interior.json")
                             .read_text(encoding="utf-8"))
        rdd = next(m for m in vigente["decisao_por_modulo"] if m["modulo"] == "rdd_bolsa")
        self.assertNotIn(str(running["municipios_faixa_divergente"]) + " de", rdd["evidencia"])
        self.assertIn(f"{p1['municipios']} de {p1['municipios']}", rdd["evidencia"])

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
