"""Testes do cache do a08: o zip de 201 MB do Ipea não é baixado de novo.

Usa um zip SINTÉTICO de poucos bytes (uma "planilha" fictícia, de conteúdo
inventado), servido por URL `file://` num diretório temporário: nada vai à
rede e nada é gravado em `data/` ou `output/`. O teste do zip real preservado
pula se ele faltar, porque o zip fica fora do Git.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aquisicao" / "a08_adquirir_ivs_2010_oficial.py"
SPEC = importlib.util.spec_from_file_location("ivs_oficial_a08", SCRIPT)
A08 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A08)

MANIFESTO = ROOT / "output" / "aquisicao" / "a08_manifesto_ivs_2010_oficial.json"
CONTEUDO = b"planilha SINTETICA de teste; nao e a base do Ipea\n" * 200


def zip_sintetico(pasta: Path) -> tuple[Path, str, str]:
    """Zip SINTÉTICO com uma planilha fictícia; devolve o caminho e os SHA-256 do zip e da planilha."""
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / "base_sintetica.zip"
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr("planilha_sintetica.xlsx", CONTEUDO)
    return caminho, A08.sha256(caminho), hashlib.sha256(CONTEUDO).hexdigest()


def rede_proibida(*_args, **_kwargs):
    raise AssertionError("o zip preservado foi baixado de novo")


class TestCacheDoZip(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.origem, self.sha_zip, self.sha_planilha = zip_sintetico(self.dir / "origem")
        self.destino = self.dir / "cache" / "base_sintetica.zip"
        self.destino.parent.mkdir()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_zip_preservado_com_hash_certo_nao_e_baixado(self) -> None:
        self.destino.write_bytes(self.origem.read_bytes())
        with mock.patch("urllib.request.urlopen", side_effect=rede_proibida):
            status, h = A08.obter_zip(self.destino, self.origem.as_uri(), self.sha_zip)
        self.assertEqual((status, h), ("ja_preservado", self.sha_zip))

    def test_download_so_ganha_o_nome_final_conferido(self) -> None:
        status, h = A08.obter_zip(self.destino, self.origem.as_uri(), self.sha_zip)
        self.assertEqual((status, h), ("baixado_agora", self.sha_zip))
        self.assertEqual(self.destino.read_bytes(), self.origem.read_bytes())
        self.assertEqual(sorted(p.name for p in self.destino.parent.iterdir()), [self.destino.name])
        with mock.patch("urllib.request.urlopen", side_effect=rede_proibida):
            self.assertEqual(A08.obter_zip(self.destino, self.origem.as_uri(), self.sha_zip)[0], "ja_preservado")

    def test_download_com_hash_errado_nao_deixa_arquivo(self) -> None:
        with self.assertRaises(ValueError):
            A08.obter_zip(self.destino, self.origem.as_uri(), "0" * 64)
        self.assertEqual(list(self.destino.parent.iterdir()), [])

    def test_zip_preservado_com_hash_errado_para_sem_tocar_no_arquivo(self) -> None:
        self.destino.write_bytes(b"zip SINTETICO corrompido")
        with mock.patch("urllib.request.urlopen", side_effect=rede_proibida):
            with self.assertRaisesRegex(ValueError, "Apague-o"):
                A08.obter_zip(self.destino, self.origem.as_uri(), self.sha_zip)
        self.assertEqual(self.destino.read_bytes(), b"zip SINTETICO corrompido")


class TestCacheDaPlanilha(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.zip, _, self.sha_planilha = zip_sintetico(Path(self.tmp.name))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_extrai_reaproveita_e_refaz_a_planilha(self) -> None:
        destino, h = A08.extrair_planilha(self.zip, self.sha_planilha)
        self.assertEqual((destino, h), (self.zip.parent / "planilha_sintetica.xlsx", self.sha_planilha))
        self.assertEqual(destino.read_bytes(), CONTEUDO)
        # Planilha já extraída e conferida: não extrai de novo.
        with mock.patch.object(zipfile.ZipFile, "extract", side_effect=AssertionError("extraiu de novo")):
            self.assertEqual(A08.extrair_planilha(self.zip, self.sha_planilha), (destino, self.sha_planilha))
        # Extração interrompida (arquivo truncado): refeita a partir do zip.
        destino.write_bytes(CONTEUDO[:100])
        self.assertEqual(A08.extrair_planilha(self.zip, self.sha_planilha), (destino, self.sha_planilha))
        self.assertEqual(destino.read_bytes(), CONTEUDO)
        self.assertEqual(sorted(p.name for p in self.zip.parent.iterdir()),
                         sorted([self.zip.name, destino.name]))  # sem diretório temporário sobrando

    def test_planilha_com_hash_errado_falha(self) -> None:
        with self.assertRaises(ValueError):
            A08.extrair_planilha(self.zip, "0" * 64)


class TestZipReal(unittest.TestCase):
    def test_constantes_do_script_iguais_ao_manifesto(self) -> None:
        fonte = json.loads(MANIFESTO.read_text(encoding="utf-8"))["fonte"]
        self.assertEqual(fonte["sha256_zip"], A08.SHA256_ESPERADO)
        self.assertEqual(fonte["sha256_xlsx"], A08.SHA256_XLSX_ESPERADO)
        self.assertFalse(fonte["no_git"])
        self.assertEqual(fonte["caminho_zip"], str(A08.ZIP.relative_to(ROOT)))

    @unittest.skipUnless(A08.ZIP.exists(), "zip do Ipea fora do Git; rode scripts/aquisicao/a08_*")
    def test_zip_preservado_e_o_registrado(self) -> None:
        self.assertEqual(A08.sha256(A08.ZIP), A08.SHA256_ESPERADO)


if __name__ == "__main__":
    unittest.main()
