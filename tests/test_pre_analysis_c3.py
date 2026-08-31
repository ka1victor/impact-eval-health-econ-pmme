"""Invariantes do torneio pré-tratamento e registro C3-03."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "avaliacao_ciclo3"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class PreAnalysisC3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.muni = pd.read_parquet(OUT / "cnes_pre" / "painel_forca_trabalho_pre.parquet")
        cls.cnes = pd.read_parquet(OUT / "cnes_pre" / "painel_forca_trabalho_cnes_pre.parquet")
        cls.diagnostics = pd.read_csv(OUT / "diagnosticos_pre.csv")
        cls.decision = load_json(OUT / "decisao_torneio_pre.json")
        cls.registry = load_json(OUT / "registro_pre_analise.json")

    def test_no_post_t0_and_balanced_panels(self) -> None:
        for panel, key in [(self.muni, "ibge"), (self.cnes, "cnes")]:
            self.assertLess(panel["competencia"].max(), "202609")
            self.assertEqual(panel["competencia"].nunique(), 26)
            self.assertFalse(panel.duplicated([key, "cod_curso", "competencia"]).any())
            sizes = panel.groupby([key, "cod_curso"]).size()
            self.assertTrue(sizes.eq(26).all())

    def test_exact_frozen_anesthesiology_arms(self) -> None:
        expected = {"cnes_ofertante": (119, 305), "municipio": (77, 247)}
        for level, counts in expected.items():
            row = self.diagnostics.loc[
                self.diagnostics["modulo"].eq("anestesiologia")
                & self.diagnostics["nivel"].eq(level)
            ].iloc[0]
            self.assertEqual((int(row["n_tratados"]), int(row["n_controles"])), counts)

    def test_course_cbo_mapping(self) -> None:
        observed = self.muni.drop_duplicates("cod_curso").set_index("cod_curso")["cbo"].astype(str).to_dict()
        self.assertEqual(observed, {1: "225151", 2: "225225", 12: "225121", 24: "225150"})

    def test_longitudinal_censoring_is_explicit(self) -> None:
        for panel in [self.muni, self.cnes]:
            self.assertTrue(panel.loc[panel["indice_mes"].lt(6), "n_entradas_apos_6m_ausencia"].isna().all())
            self.assertTrue(panel.loc[panel["indice_mes"].gt(22), "n_saidas_confirmadas_3m"].isna().all())
            self.assertTrue(panel.loc[panel["indice_mes"].gt(19), "n_entrantes_presentes_6m"].isna().all())
            self.assertTrue((panel["vinculo_070102_generico_distintos"] <= panel["especialistas_distintos"]).all())

    def test_decisions_and_gates(self) -> None:
        anesthesia = [
            x for x in self.decision["modulos_forca_trabalho"]
            if x["modulo"] == "anestesiologia"
        ]
        self.assertEqual({x["decisao"] for x in anesthesia}, {"associacao_ajustada"})
        self.assertEqual(
            self.decision["modulo_clinico_sih"]["status_operacional"],
            "BLOQUEADO_TEMPORARIAMENTE_FONTE_INCOMPLETA",
        )
        self.assertFalse(self.decision["modulo_clinico_sih"]["efeito_estimado"])
        self.assertEqual(
            self.decision["primeiro_estagio_pmme"]["status"],
            "NAO_MENSURAVEL_NOS_PARQUETS_MENSAIS_ATUAIS",
        )
        self.assertFalse(self.registry["leitura_pos_t0"])
        self.assertFalse(self.registry["efeitos_pos_tratamento_estimados"])

    def test_registry_hashes(self) -> None:
        for relative, expected in self.registry["hashes_artefatos_congelados"].items():
            path = ROOT / relative
            self.assertTrue(path.exists(), relative)
            self.assertEqual(sha256(path), expected, relative)

    def test_independent_estimator_audit(self) -> None:
        path = ROOT / "scripts" / "avaliacao_ciclo3" / "03_auditar_pre_e_potencia.py"
        spec = importlib.util.spec_from_file_location("c3_pre", path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        audit = module.audit_estimators()
        self.assertEqual(audit["status"], "APROVADA")
        self.assertLess(audit["diferenca_absoluta"], 1e-10)
        self.assertTrue(audit["bootstrap_deterministico"])


if __name__ == "__main__":
    unittest.main()
