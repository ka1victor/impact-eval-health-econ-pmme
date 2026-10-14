"""Fail-closed do controlador do plano causal do RDD da bolsa.

Cada cenario roda o controlador numa copia descartavel, com so os artefatos que
ele le, e nunca no repositorio. Revisao S1b de 14/10/2026: um registro R3 vazio,
sem autorizacao ou desvinculado de R1/R2 nao pode contar como congelado, e
resultado R4 com qualquer nome `resultados_*` ou `r4_*` tem de ser detectado.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path("scripts") / "rdd_bolsa" / "02_controlar_execucao_plano_causal.py"
ENTRADAS = (
    SCRIPT,
    Path("output/rdd_bolsa/portao_regra_ivs.json"),
    Path("output/rdd_bolsa/a01c_regra_ivs_administrativo.json"),
    Path("output/rdd_bolsa/r2_portao.json"),
    Path("output/rdd_bolsa/a01_primeiro_estagio_publico.json"),
    Path("output/rdd_bolsa/triagem_resposta_administrativa.json"),
    Path("output/rdd_bolsa/matriz_municipio_ivs_administrativo.csv"),
    Path("output/rdd_bolsa/r2_testes_continuidade.csv"),
    Path("output/tema_trabalho/A7_cutoff_selecao_resumo.json"),
    Path("docs/pedidos_dados/solicitacao_focal_rdd_bolsa.md"),
    Path("docs/pedidos_dados/vagas_e_regra_ivs.md"),
    Path("docs/pedidos_dados/eventos_e_ponte_cnes.md"),
    Path("docs/pedidos_dados/cutoff_selecao_causal.md"),
)
VINCULOS = (
    "output/rdd_bolsa/matriz_municipio_ivs_administrativo.csv",
    "output/rdd_bolsa/r2_testes_continuidade.csv",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TestControladorFailClosed(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._tmp.name)
        for rel in ENTRADAS:
            destino = self.raiz / rel
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, destino)
        self.r3 = self.raiz / "output" / "rdd_bolsa" / "registro_pre_analise.json"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def rodar(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.raiz / SCRIPT)], cwd=self.raiz, capture_output=True, text=True
        )

    def status(self) -> str:
        caminho = self.raiz / "output" / "rdd_bolsa" / "status_execucao_plano_causal.json"
        return json.loads(caminho.read_text(encoding="utf-8"))["status_geral"]

    def registro_valido(self) -> dict:
        return {
            "autorizacao_autor": {"data": "2026-10-14", "autorizado_por": "autor (teste sintético)"},
            "decisoes": {"0": "running variable: IVS administrativo"},
            "cortes": ["0.300", "0.400"],
            "hashes_entradas": {rel: sha256(self.raiz / rel) for rel in VINCULOS},
            "conhecimento_previo": ["comparações por faixa de A4"],
        }

    def gravar_r3(self, conteudo: dict | str) -> None:
        texto = conteudo if isinstance(conteudo, str) else json.dumps(conteudo)
        self.r3.write_text(texto, encoding="utf-8")

    def test_estado_atual_aguarda_r3(self) -> None:
        processo = self.rodar()
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertEqual(self.status(), "R1_R2_EXECUTADOS_AGUARDANDO_R3")

    def test_registro_valido_libera_r4(self) -> None:
        self.gravar_r3(self.registro_valido())
        processo = self.rodar()
        self.assertEqual(processo.returncode, 0, processo.stderr)
        self.assertEqual(self.status(), "R3_CONGELADO_R4_AUTORIZAVEL")

    def test_cortes_numericos_valem_como_os_textuais(self) -> None:
        registro = self.registro_valido()
        registro["cortes"] = [0.3, 0.4]
        self.gravar_r3(registro)
        processo = self.rodar()
        self.assertEqual(processo.returncode, 0, processo.stderr)

    def test_registro_vazio_nao_congela(self) -> None:
        self.gravar_r3("")
        processo = self.rodar()
        self.assertNotEqual(processo.returncode, 0)
        self.assertIn("registro R3 inválido", processo.stderr)

    def test_registro_sem_autorizacao_nao_congela(self) -> None:
        registro = self.registro_valido()
        registro["autorizacao_autor"] = {"data": "2026-10-14"}
        self.gravar_r3(registro)
        self.assertNotEqual(self.rodar().returncode, 0)

    def test_registro_desvinculado_de_r1_r2_nao_congela(self) -> None:
        registro = self.registro_valido()
        registro["hashes_entradas"][VINCULOS[0]] = "0" * 64
        self.gravar_r3(registro)
        processo = self.rodar()
        self.assertNotEqual(processo.returncode, 0)
        self.assertIn("hash ausente ou divergente", processo.stderr)

    def test_corte_fora_dos_viaveis_nao_congela(self) -> None:
        registro = self.registro_valido()
        registro["cortes"] = ["0.300", "0.500"]
        self.gravar_r3(registro)
        self.assertNotEqual(self.rodar().returncode, 0)

    def test_resultado_r4_com_qualquer_nome_sem_r3_falha(self) -> None:
        for nome in ("resultados_rdd_atracao.csv", "resultados_outro_nome.json", "r4_estimativas.csv"):
            with self.subTest(nome=nome):
                arquivo = self.raiz / "output" / "rdd_bolsa" / nome
                arquivo.write_text("x", encoding="utf-8")
                processo = self.rodar()
                arquivo.unlink()
                self.assertNotEqual(processo.returncode, 0)
                self.assertIn("resultados R4 sem protocolo R3", processo.stderr)


if __name__ == "__main__":
    unittest.main()
