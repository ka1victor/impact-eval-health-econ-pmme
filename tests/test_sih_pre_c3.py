"""Testes locais das regras corretivas do painel SIH pré-tratamento."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "avaliacao_ciclo3" / "02_adquirir_sih_pre.py"
SPEC = importlib.util.spec_from_file_location("sih_pre_c3", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class SihPreCiclo3Test(unittest.TestCase):
    def test_fluxos_de_residencia_exigem_as_27_ufs(self) -> None:
        self.assertEqual(len(MODULE.UFS_BRASIL), 27)
        self.assertEqual(len(set(MODULE.UFS_BRASIL)), 27)
        self.assertIn("AC", MODULE.UFS_BRASIL)
        self.assertIn("DF", MODULE.UFS_BRASIL)
        self.assertIn("RR", MODULE.UFS_BRASIL)

    def test_exposicao_municipal_nao_escolhe_primeira_linha(self) -> None:
        df = pd.DataFrame([
            {"ibge": "000001", "uf": "AA", "classificacao_braco": "imediata_pura", "cointervencao_cirurgica_muni": False},
            {"ibge": "000001", "uf": "AA", "classificacao_braco": "reserva_pura", "cointervencao_cirurgica_muni": False},
            {"ibge": "000002", "uf": "BB", "classificacao_braco": "nao_priorizada_pura", "cointervencao_cirurgica_muni": False},
            {"ibge": "000003", "uf": "CC", "classificacao_braco": "nao_priorizada_pura", "cointervencao_cirurgica_muni": True},
            {"ibge": "000003", "uf": "CC", "classificacao_braco": "imediata_pura", "cointervencao_cirurgica_muni": True},
        ])
        meta = MODULE.construir_meta_municipal(df).set_index("ibge")

        self.assertEqual(meta.loc["000001", "classificacao_braco"], "excluida_reserva_mista")
        self.assertFalse(bool(meta.loc["000001", "amostra_anestesia_total"]))
        self.assertEqual(meta.loc["000002", "classificacao_braco"], "nao_priorizada_pura")
        self.assertEqual(meta.loc["000003", "classificacao_braco"], "imediata_pura")
        self.assertFalse(bool(meta.loc["000003", "amostra_anestesia_isolada"]))


if __name__ == "__main__":
    unittest.main()
