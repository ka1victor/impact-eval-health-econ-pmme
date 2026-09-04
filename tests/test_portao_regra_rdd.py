"""Invariantes do portão R1 e do controlador do novo plano causal."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "output" / "rdd_bolsa" / "portao_regra_ivs.json"
MATRIX = ROOT / "output" / "rdd_bolsa" / "matriz_municipio_regra_ivs.csv"
STATUS = ROOT / "output" / "rdd_bolsa" / "status_execucao_plano_causal.json"
AUDIT = ROOT / "docs" / "auditorias" / "07_portao_rdd_bolsa.md"
EXECUTION = ROOT / "docs" / "06_execucao" / "33_status_execucao_plano_causal.md"


class PortaoRegraRddTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = json.loads(GATE.read_text(encoding="utf-8"))
        cls.matrix = pd.read_csv(MATRIX, dtype={"co_ibge_6d": "string"})
        cls.status = json.loads(STATUS.read_text(encoding="utf-8"))

    def test_matriz_tem_uma_linha_por_municipio(self) -> None:
        self.assertEqual(len(self.matrix), 368)
        self.assertEqual(self.matrix["co_ibge_6d"].nunique(), 368)
        self.assertFalse(self.matrix["co_ibge_6d"].isna().any())

    def test_reproducao_publica_falha_em_177_municipios(self) -> None:
        diagnostic = self.gate["diagnostico_publico"]
        self.assertEqual(diagnostic["n_reproduzidos"], 191)
        self.assertEqual(diagnostic["n_divergentes"], 177)
        self.assertEqual(int((~self.matrix["reproduz_faixa"]).sum()), 177)

    def test_score_publico_nao_e_promovido_a_administrativo(self) -> None:
        self.assertFalse(self.matrix["score_administrativo_comprovado"].any())
        self.assertEqual(
            set(self.matrix["fonte_running_variable"]),
            {"IVS_IPEA_2010_PUBLICO_CANDIDATO"},
        )
        self.assertFalse(
            self.gate["requisitos_r1"][
                "regra_reproduz_100_pct_ou_excecoes_previas"
            ]
        )

    def test_r1_reprovado_bloqueia_r2_a_r5(self) -> None:
        self.assertEqual(
            self.gate["decisao_r1"], "REPROVADO_PENDENTE_DE_RECONSTRUCAO"
        )
        self.assertFalse(self.gate["outcomes_abertos"])
        self.assertTrue(
            all(
                state == "BLOQUEADO_POR_R1"
                for state in self.gate["bloqueios_resultantes"].values()
            )
        )

    def test_controlador_mantem_execucao_fail_closed(self) -> None:
        self.assertEqual(
            self.status["status_geral"],
            "PARCIAL_EXECUTADO_AGUARDANDO_DADOS_ADMINISTRATIVOS",
        )
        self.assertFalse(self.status["estimacao_rdd_atracao_autorizada"])
        self.assertTrue(self.status["fail_closed_verificado"])
        self.assertEqual(self.status["artefatos_proibidos_encontrados"], [])

    def test_pacote_esta_pronto_mas_nao_foi_enviado(self) -> None:
        request = self.status["pacote_solicitacao"]
        self.assertEqual(request["status"], "PRONTO_NAO_ENVIADO")
        self.assertIsNone(request["canal_submissao"])
        self.assertIsNone(request["protocolo"])
        self.assertEqual(len(request["arquivos_sha256"]), 4)

    def test_alternativa_a7_continua_preliminar(self) -> None:
        a7 = self.status["alternativa_a7"]
        self.assertEqual(a7["pares_adjacentes"], 423)
        self.assertIn("NAO_CAUSAL", a7["status"])

    def test_documentacao_nao_promove_linguagem_causal(self) -> None:
        audit = AUDIT.read_text(encoding="utf-8")
        execution = EXECUTION.read_text(encoding="utf-8")
        self.assertIn("nenhum outcome", audit.lower())
        self.assertIn("nenhum efeito RDD", execution)
        self.assertIn("nenhum pedido foi enviado", execution.lower())


if __name__ == "__main__":
    unittest.main()
