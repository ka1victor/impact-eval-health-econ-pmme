"""Testes funcionais da triagem de respostas administrativas da RDD."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "03_triagem_resposta_administrativa.py"


def write_csv(path: Path, row: dict[str, str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row))
        writer.writeheader()
        writer.writerow(row)


class TriagemAdminRddTest(unittest.TestCase):
    def run_triage(self, input_dir: Path, output: Path) -> dict:
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input-dir",
                str(input_dir),
                "--output",
                str(output),
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads(output.read_text(encoding="utf-8"))

    def test_ausencia_nao_vira_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            report = self.run_triage(base / "nao_existe", base / "report.json")
        self.assertEqual(report["status"], "AGUARDANDO_RECEBIMENTO")
        self.assertFalse(report["ausencia_interpretada_como_zero"])
        self.assertFalse(report["estimacao_liberada"])

    def test_identificador_pessoal_interrompe_triagem(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            input_dir = base / "input"
            input_dir.mkdir()
            write_csv(
                input_dir / "vagas_mestre.csv",
                {
                    "id_vaga_pseudo": "V1",
                    "ciclo": "1",
                    "chamada_origem": "1",
                    "cnes": "0000001",
                    "ibge_municipio": "000001",
                    "curso": "CURSO",
                    "modalidade_inicial": "IMEDIATA",
                    "data_criacao": "2025-07-24",
                    "cpf": "NAO_DEVERIA_EXISTIR",
                },
            )
            report = self.run_triage(input_dir, base / "report.json")
        self.assertEqual(
            report["status"], "INTERROMPIDO_DADO_PESSOAL_NAO_SOLICITADO"
        )
        self.assertFalse(report["estimacao_liberada"])
        self.assertIn("vagas_mestre.csv", report["identificadores_pessoais_nao_solicitados"])

    def test_nucleo_r1_completo_libera_apenas_reexecucao_do_portao(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            input_dir = base / "input"
            input_dir.mkdir()
            write_csv(
                input_dir / "vagas_mestre.csv",
                {
                    "id_vaga_pseudo": "V1",
                    "ciclo": "1",
                    "chamada_origem": "1",
                    "cnes": "0000001",
                    "ibge_municipio": "000001",
                    "curso": "CURSO",
                    "modalidade_inicial": "IMEDIATA",
                    "data_criacao": "2025-07-24",
                },
            )
            write_csv(
                input_dir / "vagas_versoes.csv",
                {
                    "id_vaga_pseudo": "V1",
                    "id_versao": "1",
                    "versao_vigencia_inicio": "2025-07-24T00:00:00-03:00",
                    "versao_vigencia_fim": "",
                    "ciclo": "1",
                    "chamada": "1",
                    "cnes": "0000001",
                    "ibge_municipio": "000001",
                    "curso": "CURSO",
                    "modalidade": "IMEDIATA",
                    "status_vaga": "PUBLICADA",
                    "fonte_ato": "ATO",
                },
            )
            write_csv(
                input_dir / "regra_ivs_vaga.csv",
                {
                    "id_vaga_pseudo": "V1",
                    "vigencia_inicio": "2025-07-24",
                    "vigencia_fim": "",
                    "escore_ivs_aplicado": "0.401",
                    "vintagem": "IVS 2010",
                    "precisao": "3",
                    "regra_arredondamento": "NAO HOUVE",
                    "cutoff": "0.400/0.401",
                    "categoria": "ALTA",
                    "faixa": "FAIXA 2",
                    "valor_anunciado": "15000",
                    "excecao_motivo": "NA",
                    "fonte_regra": "MEMORIA",
                },
            )
            (input_dir / "manifesto.json").write_text("{}", encoding="utf-8")
            write_csv(
                input_dir / "dicionario.csv",
                {"campo": "id_vaga_pseudo", "definicao": "chave"},
            )
            report = self.run_triage(input_dir, base / "report.json")
        self.assertEqual(
            report["status"],
            "TRIAGEM_ESTRUTURAL_APROVADA_R1_DEVE_SER_REEXECUTADO",
        )
        self.assertTrue(report["r1_pronto_para_reexecucao"])
        self.assertFalse(report["estimacao_liberada"])


if __name__ == "__main__":
    unittest.main()
