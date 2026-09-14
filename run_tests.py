"""Executa toda a suíte de testes automatizados do PMM-E ponta a ponta."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parent
TESTS_DIR = ROOT / "tests"
sys.path.insert(0, str(ROOT / "scripts"))

from utils.ambiente import verificar_ambiente  # noqa: E402


def main() -> int:
    print("=" * 70)
    print("   SUÍTE DE TESTES AUTOMATIZADOS — PMM-E (LEI Nº 15.233/2025)")
    print("=" * 70)

    # A suite so le artefato, entao ambiente divergente e aviso, nao bloqueio.
    # O aviso existe porque a suite passa sob o ambiente errado, o que ja
    # mascarou uma divergencia de versao nesta sessao.
    verificar_ambiente(estrito=False)

    print(f"Diretório de testes: {TESTS_DIR.relative_to(ROOT)}\n")

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(TESTS_DIR), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print(f"   SUCESSO: Todos os {result.testsRun} testes foram aprovados!")
        print("=" * 70)
        return 0
    else:
        print(
            f"   FALHA: {len(result.failures)} falha(s) e {len(result.errors)} erro(s) em {result.testsRun} testes."
        )
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
