"""Testes da verificação de ambiente exigida antes de gravar artefato.

A verificação existe porque a suíte passa mesmo sob ambiente divergente, o que
já mascarou uma troca silenciosa de versão de numpy. Estes testes garantem que
a divergência é detectada e que o modo estrito realmente interrompe.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from utils import ambiente  # noqa: E402


class VerificacaoAmbienteTest(unittest.TestCase):
    def test_requirements_fixa_os_pacotes_criticos(self):
        """Os pacotes que mudam resultado numérico devem estar fixados com ==."""
        fixadas = ambiente._versoes_fixadas()
        for pacote in ambiente.PACOTES_CRITICOS:
            self.assertIn(
                pacote,
                fixadas,
                f"{pacote} altera resultado gravado e precisa de versão fixa",
            )

    def test_minimo_de_python_e_coerente_com_requirements(self):
        """numpy 2.5.x exige Python 3.12; o mínimo declarado não pode ser menor."""
        self.assertGreaterEqual(ambiente.PYTHON_MINIMO, (3, 12))

    def test_divergencias_devolve_lista_de_strings(self):
        problemas = ambiente.divergencias()
        self.assertIsInstance(problemas, list)
        for p in problemas:
            self.assertIsInstance(p, str)
            self.assertTrue(p.strip(), "divergência não pode ser string vazia")

    def test_estrito_interrompe_quando_ha_divergencia(self):
        """Com divergência, o modo estrito levanta SystemExit; sem, não levanta."""
        originais = ambiente.divergencias

        ambiente.divergencias = lambda: ["divergência sintética de teste"]
        try:
            with self.assertRaises(SystemExit):
                ambiente.verificar_ambiente(estrito=True)
            # Sem estrito, apenas devolve a lista.
            self.assertEqual(
                ambiente.verificar_ambiente(estrito=False),
                ["divergência sintética de teste"],
            )
        finally:
            ambiente.divergencias = originais

    def test_sem_divergencia_nao_interrompe(self):
        originais = ambiente.divergencias
        ambiente.divergencias = lambda: []
        try:
            self.assertEqual(ambiente.verificar_ambiente(estrito=True), [])
        finally:
            ambiente.divergencias = originais

    def test_pontos_de_entrada_chamam_a_verificacao(self):
        """run_all grava artefato e deve ser estrito; run_tests só avisa."""
        run_all = (ROOT / "run_all.py").read_text(encoding="utf-8")
        run_tests = (ROOT / "run_tests.py").read_text(encoding="utf-8")
        self.assertIn("verificar_ambiente(estrito=True)", run_all)
        self.assertIn("verificar_ambiente(estrito=False)", run_tests)


if __name__ == "__main__":
    unittest.main()
