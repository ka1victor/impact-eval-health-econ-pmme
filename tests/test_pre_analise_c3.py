"""Testes de integridade do Plano de Pré-Análise e diagnósticos do Ciclo 3."""

import os
import sys
import json
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "output" / "avaliacao_ciclo3"
DOCS_DIR = ROOT / "docs"

class PreAnaliseC3Test(unittest.TestCase):
    def test_arquivos_obrigatorios_existem(self):
        f_diag = OUT_DIR / "diagnosticos_pre.csv"
        f_pot = OUT_DIR / "potencia_pre.json"
        f_dec = OUT_DIR / "decisao_torneio_pre.json"
        f_reg = OUT_DIR / "registro_pre_analise.json"
        f_plan = DOCS_DIR / "13_plano_pre_analise_ciclo3.md"
        
        self.assertTrue(f_diag.exists(), "diagnosticos_pre.csv não encontrado")
        self.assertTrue(f_pot.exists(), "potencia_pre.json não encontrado")
        self.assertTrue(f_dec.exists(), "decisao_torneio_pre.json não encontrado")
        self.assertTrue(f_reg.exists(), "registro_pre_analise.json não encontrado")
        self.assertTrue(f_plan.exists(), "13_plano_pre_analise_ciclo3.md não encontrado")

    def test_registro_pre_analise_schema_e_hashes(self):
        f_reg = OUT_DIR / "registro_pre_analise.json"
        with open(f_reg, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.assertEqual(data["protocolo_id"], "PMM-E-C3-PROSPECTIVE-2026")
        self.assertEqual(data["status_registro"], "CONGELADO_PRE_TRATAMENTO")
        self.assertEqual(data["t0"], "2026-09")
        
        hashes = data["hashes_insumos_congelados"]
        self.assertIn("coorte_c3_congelada.parquet", hashes)
        self.assertIn("painel_sih_cnes_pre.parquet", hashes)
        self.assertIn("ponte_curso_cbo_c3_nota59.json", hashes)
        
        for k, sha in hashes.items():
            self.assertIsInstance(sha, str)
            self.assertEqual(len(sha), 64)

    def test_diagnosticos_pre_validade(self):
        f_diag = OUT_DIR / "diagnosticos_pre.csv"
        df = pd.read_csv(f_diag)
        self.assertGreaterEqual(len(df), 3)
        self.assertIn("Cirurgias Eletivas CNES (SIH)", df["modulo"].values)
        
        # Validar que cirurgias eletivas no CNES não rejeitou paralelismo pré
        row_cnes = df[df["modulo"] == "Cirurgias Eletivas CNES (SIH)"].iloc[0]
        self.assertGreater(row_cnes["placebo_pval"], 0.05)
        self.assertEqual(row_cnes["status_pre_tendencia"], "COMPATIVEL")

    def test_paineis_sih_dimensoes(self):
        f_cnes = OUT_DIR / "sih_pre" / "painel_sih_cnes_pre.parquet"
        f_muni = OUT_DIR / "sih_pre" / "painel_sih_muni_pre.parquet"
        
        df_c = pd.read_parquet(f_cnes)
        df_m = pd.read_parquet(f_muni)
        
        self.assertGreater(len(df_c), 10000)
        self.assertGreater(len(df_m), 8000)
        self.assertIn("n_cirurgias_eletivas_cnes", df_c.columns)
        self.assertIn("n_cirurgias_eletivas_ocorrencia", df_m.columns)

if __name__ == "__main__":
    unittest.main()
