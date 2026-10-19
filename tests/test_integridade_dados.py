"""Integridade: nada simulado em `data/` ou `output/` passando por observação.

Regra do `CLAUDE.md`: dados simulados, parâmetros assumidos e testes sintéticos
ficam rotulados e separados dos resultados empíricos. Dado sintético existe só
em memória, dentro de `tests/`. Estes testes varrem o que está gravado.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
PASTAS_DE_DADOS = [ROOT / "data", ROOT / "output"]
NOME_SUSPEITO = re.compile(r"sintetic|synthetic|simulad|simulated|fake|mock|dummy|placeholder", re.IGNORECASE)
# Saídas gravadas por estimadores que rotulam a natureza dos dados (07, 09b, 11 e os novos E6+).
CHAVE = "natureza_dos_dados"


def _arquivos(sufixos: tuple[str, ...]) -> list[Path]:
    return sorted(p for pasta in PASTAS_DE_DADOS for p in pasta.rglob("*")
                  if p.is_file() and p.suffix.lower() in sufixos)


def _valores_da_chave(obj) -> list:
    if isinstance(obj, dict):
        achados = [v for k, v in obj.items() if k == CHAVE]
        return achados + [x for v in obj.values() for x in _valores_da_chave(v)]
    if isinstance(obj, list):
        return [x for v in obj for x in _valores_da_chave(v)]
    return []


class TestNadaSimuladoGravado(unittest.TestCase):
    def test_nenhum_arquivo_de_dados_com_nome_de_simulado(self) -> None:
        suspeitos = [str(p.relative_to(ROOT)) for pasta in PASTAS_DE_DADOS for p in pasta.rglob("*")
                     if p.is_file() and NOME_SUSPEITO.search(p.name)]
        self.assertEqual(suspeitos, [], "arquivo com nome de dado simulado em data/ ou output/")

    def test_csv_e_parquet_rotulados_sao_empiricos(self) -> None:
        for caminho in _arquivos((".csv", ".parquet")):
            if caminho.suffix == ".csv":
                with caminho.open(encoding="utf-8", errors="replace") as f:
                    if CHAVE not in f.readline():
                        continue
                valores = pd.read_csv(caminho, usecols=[CHAVE])[CHAVE]
            else:
                # Só a coluna, lida pelo pyarrow como dicionário, e só os valores distintos: o painel SIA tem
                # ~64 milhões de linhas e pd.read_parquet da coluna inteira estourava a memória (auditoria 21).
                # Mesma semântica: arquivo sem a coluna (ou ilegível) é pulado; nulos não contam.
                try:
                    if CHAVE not in pq.read_schema(caminho).names:
                        continue
                    try:
                        coluna = pq.read_table(caminho, columns=[CHAVE], read_dictionary=[CHAVE]).column(CHAVE)
                    except (pa.ArrowException, ValueError, TypeError):  # tipo que não aceita dicionário
                        coluna = pq.read_table(caminho, columns=[CHAVE]).column(CHAVE)
                    distintos = pc.unique(coluna)
                    if pa.types.is_dictionary(distintos.type):
                        distintos = distintos.dictionary_decode()
                except (KeyError, ValueError, Exception):  # sem a coluna ou ilegível
                    continue
                valores = pd.Series(distintos.to_pylist(), dtype=object)
            rotulos = set(valores.dropna().astype(str).str.upper())
            self.assertTrue(rotulos <= {"EMPIRICO"}, f"{caminho.relative_to(ROOT)}: {sorted(rotulos)}")

    def test_json_rotulados_sao_empiricos(self) -> None:
        for caminho in _arquivos((".json",)):
            try:
                obj = json.loads(caminho.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            rotulos = {str(v).upper() for v in _valores_da_chave(obj) if not isinstance(v, (dict, list))}
            self.assertTrue(rotulos <= {"EMPIRICO"}, f"{caminho.relative_to(ROOT)}: {sorted(rotulos)}")


if __name__ == "__main__":
    unittest.main()
