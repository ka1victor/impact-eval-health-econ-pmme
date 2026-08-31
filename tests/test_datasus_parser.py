"""Testes unitários para o módulo datasus_dbc.py."""

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.utils.datasus_dbc import get_short_path_name, compute_sha256

class DatasusDbcTest(unittest.TestCase):
    def test_short_path_conversion(self):
        cur_path = str(ROOT)
        short_p = get_short_path_name(cur_path)
        self.assertTrue(os.path.exists(short_p))
        if sys.platform == "win32" and " " in cur_path:
            self.assertNotIn(" ", short_p)

    def test_sha256_computation(self):
        readme = ROOT / "README.md"
        sha = compute_sha256(str(readme))
        self.assertIsInstance(sha, str)
        self.assertEqual(len(sha), 64)

if __name__ == "__main__":
    unittest.main()
