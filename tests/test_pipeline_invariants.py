"""Testes de integridade substantiva do pipeline agregado."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
EVAL = OUT / "avaliacao_impacto"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class PipelineInvariantsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.panel = pd.read_parquet(EVAL / "dados" / "painel_municipio_curso_mes.parquet")
        cls.audit = load_json(OUT / "aquisicao" / "auditoria_painel_final.json")
        cls.gate = load_json(EVAL / "relatorios" / "01_relatorio_portao_relevancia.json")

    def test_panel_is_balanced_and_unique(self) -> None:
        self.assertEqual(self.panel["competencia"].nunique(), 26)
        self.assertFalse(
            self.panel.duplicated(["co_ibge_6d", "cod_curso", "competencia"]).any()
        )
        sizes = self.panel.groupby(["co_ibge_6d", "cod_curso"]).size()
        self.assertTrue((sizes == 26).all())

    def test_outcomes_are_cnes_only_and_not_imputed_fte(self) -> None:
        forbidden = {
            "fte_total_ist",
            "horas_totais_ist",
            "id_pmm_e",
            "nome_profissional",
            "crm",
        }
        self.assertTrue(forbidden.isdisjoint(self.panel.columns))
        self.assertTrue(self.audit["checks"]["nenhuma_lista_nominal_incorporada"])

    def test_longitudinal_edges_are_censored(self) -> None:
        early = self.panel[self.panel["competencia"] < "202412"]
        late = self.panel[self.panel["competencia"] > "202604"]
        self.assertTrue(early["n_entradas_6m"].isna().all())
        self.assertTrue(late["n_saidas_confirmadas_3m"].isna().all())

    def test_longitudinal_identifier_diagnostic_covers_all_adjacent_pairs(self) -> None:
        diagnostic = self.audit["diagnostico_identificador_longitudinal"]
        self.assertEqual(len(diagnostic["pares_adjacentes"]), 25)
        self.assertGreater(diagnostic["min_sobrevivencia_sobre_mes_anterior_pct"], 0)

    def test_bridge_is_explicitly_operational_not_official_crosswalk(self) -> None:
        bridge = load_json(OUT / "aquisicao" / "ponte_curso_cbo_oficial.json")
        self.assertEqual(
            bridge["status_substantivo"],
            "OPERACIONAL_NAO_PUBLICADA_COMO_CROSSWALK_OFICIAL",
        )
        self.assertGreater(len(bridge["cursos_sobrepostos"]), 0)

    def test_relevance_gate_uses_analysis_sample(self) -> None:
        first_stage = self.gate["resultados_ajustados"]["tem_alocado_muni_ddd"]
        expected = "APROVADO" if first_stage["beta"] > 0 and first_stage["p_valor"] < 0.10 else "NAO_APROVADO"
        self.assertEqual(self.gate["status_portao"], expected)
        self.assertIn("mesmo grão município-curso", self.gate["criterio_decisao"])

    def test_note_respects_failed_gate(self) -> None:
        note = (EVAL / "relatorios" / "03_nota_tecnica_avaliacao_impacto_pmme.md").read_text(
            encoding="utf-8"
        )
        if self.gate["status_portao"] != "APROVADO":
            self.assertIn("Status: **COMPARAÇÃO AJUSTADA**", note)
            self.assertIn("não sustenta uma afirmação causal", note)

    def test_absorption_converged_in_all_reported_models(self) -> None:
        ddd = load_json(EVAL / "modelos" / "resultados_ddd_estatica.json")
        for result in ddd:
            diagnostics = result["diagnosticos_numericos"]
            self.assertTrue(diagnostics["convergiu"])
            self.assertLess(diagnostics["max_media_grupo_residual"], 1e-7)

    def test_local_links_in_current_documentation_exist(self) -> None:
        documents = [
            ROOT / "README.md",
            ROOT / "docs" / "06_execucao" / "05_roadmap_execucao.md",
            ROOT / "docs" / "auditorias" / "04_auditoria_pipeline_agregado.md",
            ROOT / "prompts" / "README.md",
        ]
        missing: list[str] = []
        for document in documents:
            text = document.read_text(encoding="utf-8")
            for raw in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                target = raw.strip().strip("<>").split("#", 1)[0]
                if not target or re.match(r"^[a-z]+://", target):
                    continue
                resolved = (document.parent / target).resolve()
                if not resolved.exists():
                    missing.append(f"{document.relative_to(ROOT)} -> {target}")
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
