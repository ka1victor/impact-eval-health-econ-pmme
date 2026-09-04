"""Executa toda a suíte de testes automatizados do PMM-E ponta a ponta."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parent
TESTS_DIR = ROOT / "tests"


def main() -> int:
    print("=" * 70)
    print("   SUÍTE DE TESTES AUTOMATIZADOS — PMM-E (LEI Nº 15.233/2025)")
    print("=" * 70)
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
