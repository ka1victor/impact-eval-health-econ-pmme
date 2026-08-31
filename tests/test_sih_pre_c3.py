"""Testes locais das regras corretivas do painel SIH pré-tratamento."""

from __future__ import annotations

import importlib.util
import json
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

    def test_janela_e_sigtap_sao_estritamente_pre_t0(self) -> None:
        self.assertEqual(len(MODULE.COMPETENCIAS), 25)
        self.assertEqual(set(MODULE.SIGTAP_FILES), set(MODULE.COMPETENCIAS))
        self.assertLess(max(MODULE.COMPETENCIAS), MODULE.T0_PROVISORIO)

    def test_continuidade_e_procedimento_fora_nao_contam_cirurgia(self) -> None:
        base = {
            "UF_ZI": "52",
            "ANO_CMPT": "2025",
            "MES_CMPT": "01",
            "CNES": "123",
            "MUNIC_RES": "520870",
            "MUNIC_MOV": "520870",
            "CAR_INT": "01",
            "DT_INTER": "20250101",
            "DT_SAIDA": "20250102",
            "DIAS_PERM": "1",
            "MORTE": "0",
            "VAL_TOT": "10.00",
        }
        df = pd.DataFrame([
            {**base, "PROC_REA": "0401010001", "IDENT": "1"},
            {**base, "PROC_REA": "0401010001", "IDENT": "5"},
            {**base, "PROC_REA": "0401019999", "IDENT": "1"},
            {**base, "PROC_REA": "0301010001", "IDENT": "1"},
        ])
        out = MODULE._normalise_sih(
            df, "202501", frozenset({"0401010001"})
        )
        self.assertEqual(int(out["is_cirurgica_inicial"].sum()), 1)
        self.assertEqual(int(out["is_cirurgica_eletiva"].sum()), 1)
        self.assertFalse(bool(out.loc[1, "is_cirurgica_inicial"]))
        self.assertFalse(bool(out.loc[2, "is_cirurgica_inicial"]))
        self.assertFalse(bool(out.loc[3, "is_cirurgica_inicial"]))

    def test_contagens_municipais_congeladas_reconciliam(self) -> None:
        cohort = pd.read_parquet(
            ROOT / "output" / "avaliacao_ciclo3" / "coorte_c3_congelada.parquet"
        )
        anesthesia = cohort[cohort["cod_curso"].eq(1)].copy()
        meta = MODULE.construir_meta_municipal(anesthesia)
        counts = meta["classificacao_braco"].value_counts().to_dict()
        self.assertEqual(counts["imediata_pura"], 77)
        self.assertEqual(counts["nao_priorizada_pura"], 247)
        self.assertEqual(counts["excluida_reserva_mista"], 132)
        overlap = meta[
            meta["bracos_anestesia_no_municipio"].eq(
                "imediata_pura|reserva_pura"
            )
        ]
        self.assertEqual(len(overlap), 1)
        self.assertFalse(bool(overlap.iloc[0]["amostra_anestesia_total"]))

    def test_tentativa_integral_falha_fechado_em_duas_ausencias_oficiais(self) -> None:
        output = ROOT / "output" / "avaliacao_ciclo3"
        files = pd.read_csv(
            output / "manifesto_arquivos_sih_pre.csv",
            dtype={"uf": str, "competencia": str},
        )
        self.assertEqual(len(files), 675)
        self.assertFalse(files[["uf", "competencia"]].duplicated().any())
        self.assertEqual(int(files["status"].eq("SUCCESS").sum()), 673)
        errors = set(files.loc[~files["status"].eq("SUCCESS"), "arquivo"])
        self.assertEqual(errors, {"RDAC2606.dbc", "RDRR2606.dbc"})

        sigtap = pd.read_csv(
            output / "manifesto_sigtap_pre.csv", dtype={"competencia": str}
        )
        self.assertEqual(len(sigtap), 25)
        self.assertTrue(sigtap["status"].eq("SUCCESS").all())
        dictionary = pd.read_csv(
            output / "dicionario_procedimentos_anestesia.csv",
            dtype={"competencia": str, "co_procedimento": str},
            usecols=["competencia", "co_procedimento"],
        )
        self.assertEqual(len(dictionary), 42358)
        self.assertTrue(dictionary["co_procedimento"].str.startswith("04").all())

        blocked = json.loads((output / "manifesto_sih_pre.json").read_text(encoding="utf-8"))
        self.assertEqual(
            blocked["status_portao_c3_03"],
            "BLOQUEADO_FONTE_OFICIAL_INCOMPLETA",
        )
        self.assertEqual(blocked["c3_03"], "BLOQUEADO")
        self.assertIsNone(blocked["armazenamento_temporario"]["pico_bytes"])

    def test_c3_03_nao_foi_executado(self) -> None:
        output = ROOT / "output" / "avaliacao_ciclo3"
        forbidden = [
            output / "diagnosticos_pre.csv",
            output / "potencia_pre.json",
            output / "decisao_torneio_pre.json",
            output / "registro_pre_analise.json",
            ROOT / "docs" / "13_plano_pre_analise_ciclo3.md",
        ]
        self.assertFalse(any(path.exists() for path in forbidden))


if __name__ == "__main__":
    unittest.main()
