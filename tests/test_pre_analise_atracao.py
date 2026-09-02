"""Invariantes da pré-análise A3 — núcleo associativo."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
REGISTRO = ROOT / "output" / "tema_trabalho" / "registro_pre_analise_atracao.json"
POTENCIA = ROOT / "output" / "tema_trabalho" / "potencia_atracao.json"
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"


class PreAnaliseAtracaoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registro = json.loads(REGISTRO.read_text(encoding="utf-8"))
        cls.potencia = json.loads(POTENCIA.read_text(encoding="utf-8"))

    def test_outcome_conforme_A1(self) -> None:
        out = self.registro["outcome_primario"]
        self.assertEqual(out["nome"], "alguma_confirmacao_ou_homologacao_na_celula")
        self.assertIn("taxa de preenchimento por vaga", out["outcomes_bloqueados"])
        self.assertEqual(out["tipo"], "binário por célula")
        self.assertFalse(self.registro["efeitos_estimados"])

    def test_unidade_e_cluster(self) -> None:
        self.assertIn("célula CNES", self.registro["populacao"]["unidade_analitica"])
        self.assertEqual(self.registro["populacao"]["primaria"][:4], "1295")
        self.assertIn("município", self.registro["inferencia"]["unidade_cluster"])
        self.assertIn("cluster", self.registro["inferencia"]["metodo"].lower())

    def test_covariadas_pre_oferta_e_ivs_canonico(self) -> None:
        cov = self.registro["covariadas_exclusivamente_pre_oferta"]
        permitidas = " ".join(cov["permitidas"])
        self.assertIn("ivs_2010", permitidas)
        proibidas = " ".join(cov["proibidas"])
        self.assertIn("CNES pós", proibidas)
        # IVS canônico — não substituir por IDHM sem justificativa está no texto
        self.assertTrue(any("IVS" in p for p in cov["proibidas"]) or "IDHM" in proibidas)

    def test_modelos_e_efeitos_fixos(self) -> None:
        esp = self.registro["especificacao"]
        self.assertTrue(any("LPM" in m for m in esp["modelos_candidatos_primarios"]))
        self.assertTrue(any("Logit" in m for m in esp["modelos_candidatos_primarios"]))
        self.assertIn("curso", esp["efeitos_fixos"])
        self.assertIn("UF", esp["efeitos_fixos"])

    def test_potencia_global_e_por_estrato(self) -> None:
        self.assertAlmostEqual(self.potencia["alfa_bilateral"], 0.05)
        self.assertAlmostEqual(self.potencia["poder_alvo"], 0.80)
        # Global MDE ~3-4pp bem abaixo de 10pp relevante
        self.assertLess(self.potencia["mde_global"]["mde_80_pp_p30"], 0.05)
        # Próximo é o estrato mais potenciado (maior n)
        self.assertLess(
            self.potencia["por_estrato"]["interior_proximo_polo"]["mde_80_pp_p30"],
            self.potencia["por_estrato"]["capital"]["mde_80_pp_p30"],
        )

    def test_linguagem_maxima(self) -> None:
        ling = self.registro["linguagem_maxima"]
        texto = ling["proibido"]
        self.assertIn("preenchimento por vaga", texto)
        self.assertIn("individual", texto)

    def test_hashes_presentes(self) -> None:
        self.assertIn("output/aquisicao/quadro_vagas_tratamento.parquet", self.registro["hashes_entradas"])
        self.assertGreater(len(self.registro["hashes_entradas"]), 3)

    def test_quadro_consistencia(self) -> None:
        q = pd.read_parquet(QUADRO)
        self.assertEqual(len(q), 1295)
        self.assertEqual(q["qt_vagas_imediatas"].sum(), 678)


if __name__ == "__main__":
    unittest.main()
