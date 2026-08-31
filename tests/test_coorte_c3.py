"""Testes unitários e invariantes da coorte congelada do Ciclo 3 (Prompt C3-01)."""

from __future__ import annotations
import json
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_C3 = ROOT / "output" / "avaliacao_ciclo3"

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

class CoorteCiclo3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.coorte = pd.read_parquet(OUT_C3 / "coorte_c3_congelada.parquet")
        cls.suporte = pd.read_csv(OUT_C3 / "suporte_c3.csv")
        cls.ponte = load_json(OUT_C3 / "ponte_curso_cbo_c3_nota59.json")
        cls.manifesto = load_json(OUT_C3 / "manifesto_coorte_c3.json")
        cls.assinatura = load_json(OUT_C3 / "auditoria_assinatura_pmme_cnes.json")

    def test_total_cells_and_arm_partition(self) -> None:
        self.assertEqual(len(self.coorte), 5534)
        bracos = self.coorte["classificacao_braco"].value_counts().to_dict()
        self.assertEqual(bracos.get("imediata_pura", 0), 451)
        self.assertEqual(bracos.get("reserva_pura", 0), 1595)
        self.assertEqual(bracos.get("nao_priorizada_pura", 0), 3241)
        self.assertEqual(bracos.get("mista", 0), 247)
        self.assertEqual(bracos.get("inconsistente", 0), 0)

    def test_keys_formatting(self) -> None:
        # CNES: 7 chars
        self.assertTrue(self.coorte["cnes"].str.len().eq(7).all())
        # IBGE: 6 chars
        self.assertTrue(self.coorte["ibge"].str.len().eq(6).all())
        # Cursos 1 to 24
        self.assertEqual(self.coorte["cod_curso"].min(), 1)
        self.assertEqual(self.coorte["cod_curso"].max(), 24)

    def test_anesthesiology_support(self) -> None:
        anes = self.coorte[self.coorte["cod_curso"] == 1]
        self.assertEqual((anes["classificacao_braco"] == "imediata_pura").sum(), 119)
        self.assertEqual((anes["classificacao_braco"] == "nao_priorizada_pura").sum(), 305)
        self.assertEqual((anes["classificacao_braco"] == "reserva_pura").sum(), 188)
        self.assertEqual((anes["classificacao_braco"] == "mista").sum(), 0)

    def test_ponte_nota59_coverage(self) -> None:
        self.assertEqual(len(self.ponte["catalogo_cursos"]), 24)
        self.assertEqual(self.ponte["versao_ponte"], "3.0_normativa_nota59_sgtes_ms")
        cursos_confirmatorios = self.ponte["cursos_confirmatorios_sem_sobreposicao"]
        self.assertIn(1, cursos_confirmatorios)
        self.assertIn(2, cursos_confirmatorios)
        self.assertIn(12, cursos_confirmatorios)
        self.assertIn(13, cursos_confirmatorios)
        self.assertIn(14, cursos_confirmatorios)

    def test_manifesto_integrity(self) -> None:
        self.assertIn("coorte_c3_congelada.parquet", self.manifesto["arquivos_gerados_hashes"])
        self.assertIsNotNone(self.manifesto["arquivos_gerados_hashes"]["coorte_c3_congelada.parquet"])
        self.assertEqual(self.manifesto["totais_amostrais"]["imediata_pura"], 451)
        self.assertEqual(self.manifesto["totais_amostrais"]["nao_priorizada_pura"], 3241)

if __name__ == "__main__":
    unittest.main()
