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
        self.assertEqual(
            self.ponte["versao_ponte"],
            "3.1_normativa_nota59_sgtes_ms_corrigida",
        )
        self.assertEqual(
            self.ponte["cursos_confirmatorios_sem_sobreposicao"],
            [1, 12, 24],
        )

    def test_ponte_reproduz_todos_os_cbos_do_anexo_i(self) -> None:
        esperados = {
            1: ["225151"], 2: ["225225", "225220"], 3: ["225290"],
            4: ["225290", "225280"], 5: ["225280", "225220"],
            6: ["225250", "225290"], 7: ["225310", "225280"],
            8: ["225250"], 9: ["225120"], 10: ["225310"],
            11: ["225310"], 12: ["225121"], 13: ["225320"],
            14: ["225320", "225255", "225250"], 15: ["225275"],
            16: ["225325"], 17: ["225133"], 18: ["225120"],
            19: ["225285"], 20: ["225280"], 21: ["225255"],
            22: ["225270"], 23: ["225270"], 24: ["225150"],
        }
        observados = {
            item["cod_curso"]: item["cbos_elegiveis"]
            for item in self.ponte["catalogo_cursos"]
        }
        self.assertEqual(observados, esperados)

    def test_sobreposicoes_sao_derivadas_dos_cbos(self) -> None:
        catalogo = self.ponte["catalogo_cursos"]
        for item in catalogo:
            concorrentes_esperados = sorted({
                outro["cod_curso"]
                for outro in catalogo
                if outro["cod_curso"] != item["cod_curso"]
                and set(item["cbos_elegiveis"]) & set(outro["cbos_elegiveis"])
            })
            self.assertEqual(item["cursos_concorrentes"], concorrentes_esperados)
            self.assertEqual(item["sobreposicao"], bool(concorrentes_esperados))

    def test_amostra_confirmatoria_restringe_cursos_univocos_com_suporte(self) -> None:
        cursos = set(
            self.coorte.loc[self.coorte["amostra_confirmatoria_geral"], "cod_curso"]
        )
        self.assertEqual(cursos, {1, 12, 24})

    def test_manifesto_integrity(self) -> None:
        self.assertIn("coorte_c3_congelada.parquet", self.manifesto["arquivos_gerados_hashes"])
        self.assertIsNotNone(self.manifesto["arquivos_gerados_hashes"]["coorte_c3_congelada.parquet"])
        self.assertEqual(self.manifesto["totais_amostrais"]["imediata_pura"], 451)
        self.assertEqual(self.manifesto["totais_amostrais"]["nao_priorizada_pura"], 3241)
        municipios = self.coorte.loc[
            self.coorte["muni_tem_imediata_e_controle"], "ibge"
        ].nunique()
        self.assertEqual(
            self.manifesto["totais_amostrais"]["municipios_com_ambos_bracos_distintos"],
            municipios,
        )
        self.assertGreater(municipios, 2)

if __name__ == "__main__":
    unittest.main()
