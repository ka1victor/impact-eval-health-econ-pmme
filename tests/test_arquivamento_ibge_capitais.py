"""Arquivamento da fonte bruta do IBGE (capitais, UF e região) do adendo 48c (a19; auditoria 42, A1).

Confere, sem rede:
1. os sete brutos arquivados em `data/raw/aquisicao/ibge_capitais_uf/` existem e têm o SHA-256 do manifesto do 41
   (`output/aquisicao/manifesto_ibge_capitais_uf_regiao.json`) e do manifesto de arquivamento do a19;
2. o manifesto de arquivamento tem fonte, URL (as mesmas do 41), data de acesso, cobertura, unidade, chaves e hash;
3. `output/aquisicao/ibge_capitais_uf_regiao.csv` se reconstrói byte a byte do bruto arquivado, com a rede bloqueada;
4. o modo `--verificar` não grava nada, e o `--baixar`, com o download trocado pela leitura dos próprios brutos
   arquivados (dado observado, sem rede), só escreve no diretório do bruto e em `output/aquisicao/`, redirecionados
   para uma pasta temporária fora do repositório.

Pula de forma explícita se o bruto não estiver arquivado. Não usa dado sintético.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "aquisicao" / "a19_arquivar_ibge_capitais_uf.py"
SPEC = importlib.util.spec_from_file_location("arquivar_ibge_capitais_a19", SCRIPT)
A19 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(A19)

RAW = ROOT / "data" / "raw" / "aquisicao" / "ibge_capitais_uf"
OUT = ROOT / "output" / "aquisicao"
MAN_41 = OUT / "manifesto_ibge_capitais_uf_regiao.json"
MAN_ARQ = OUT / "a19_manifesto_arquivamento_ibge_capitais_uf.json"
REF_CSV = OUT / "ibge_capitais_uf_regiao.csv"
IGNORAR = {".git", "__pycache__", ".pytest_cache", ".claude"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rede_proibida(*_a, **_k):
    raise AssertionError("acesso à rede no modo sem rede")


def retrato(raiz: Path) -> dict[str, tuple[int, int]]:
    """(tamanho, mtime_ns) de cada arquivo do repositório, fora de .git e caches."""
    r = {}
    for d, subdirs, arquivos in os.walk(raiz):
        subdirs[:] = [s for s in subdirs if s not in IGNORAR]
        for a in arquivos:
            p = Path(d) / a
            st = p.stat()
            r[p.relative_to(raiz).as_posix()] = (st.st_size, st.st_mtime_ns)
    return r


def _itens() -> list[dict]:
    return A19.brutos_esperados(json.loads(MAN_41.read_text(encoding="utf-8")))


class _Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        faltam = [it["nome"] for it in _itens() if not (RAW / it["nome"]).exists()]
        if faltam or not MAN_ARQ.exists():
            raise unittest.SkipTest(
                "bruto do IBGE não arquivado em data/raw/aquisicao/ibge_capitais_uf/ "
                f"(faltam {faltam or 'o manifesto do a19'}); rode o a19 com --baixar")


class TestBrutosArquivados(_Base):
    def test_sete_brutos_com_hash_do_manifesto_do_41(self):
        itens = _itens()
        self.assertEqual(len(itens), 7)  # ZIP de Localidades 2022 + SIDRA n2 + SIDRA n3 nas 5 regiões
        for it in itens:
            p = RAW / it["nome"]
            self.assertTrue(p.is_file(), p)
            self.assertEqual(sha(p), it["sha256_esperado"], f"SHA-256 de {p.name} difere do manifesto do 41")

    def test_diretorio_so_tem_os_brutos_do_manifesto(self):
        arquivados = sorted(p.name for p in RAW.iterdir())
        man = json.loads(MAN_ARQ.read_text(encoding="utf-8"))
        self.assertEqual(arquivados, sorted(Path(a["arquivo"]).name for a in man["arquivos"]))
        self.assertFalse([n for n in arquivados if n.endswith(".part")], "download parcial no arquivo")

    def test_manifesto_de_arquivamento(self):
        man = json.loads(MAN_ARQ.read_text(encoding="utf-8"))
        m41 = json.loads(MAN_41.read_text(encoding="utf-8"))
        self.assertEqual(man["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(man["situacao"], "HASH_CONFERE")
        self.assertEqual(man["manifesto_original"]["sha256"], sha(MAN_41))
        self.assertEqual(man["diretorio_bruto"], "data/raw/aquisicao/ibge_capitais_uf")
        urls_41 = {m41["fontes"]["capitais"]["url"], m41["fontes"]["regioes"]["regioes"]["url"],
                   *(x["url"] for x in m41["fontes"]["regioes"]["ufs_por_regiao"])}
        self.assertEqual({a["url"] for a in man["arquivos"]}, urls_41, "URLs diferentes das do manifesto do 41")
        for a in man["arquivos"]:
            for campo in ("fonte", "url", "data_acesso_utc", "data_referencia", "cobertura", "unidade", "chaves",
                          "sha256", "bytes"):
                self.assertTrue(a.get(campo), f"{a['nome_canonico']}: campo {campo} vazio")
            self.assertTrue(a["confere_com_manifesto_41"])
            self.assertEqual(a["sha256"], a["sha256_manifesto_41"])
            p = ROOT / a["arquivo"]
            self.assertEqual(p.parent, RAW)
            self.assertEqual(sha(p), a["sha256"])
            self.assertEqual(p.stat().st_size, a["bytes"])
        rec = man["reconstrucao_sem_rede"]
        self.assertTrue(rec["identico"])
        self.assertEqual(rec["sha256_reconstruido"], m41["saida"]["sha256"])
        self.assertEqual(rec["sha256_dbf"], m41["fontes"]["capitais"]["sha256_dbf"])


class TestReconstrucaoSemRede(_Base):
    def test_csv_se_reconstroi_igual_sem_rede(self):
        with mock.patch("urllib.request.urlopen", side_effect=rede_proibida), \
             mock.patch.object(socket, "create_connection", side_effect=rede_proibida):
            res = A19.verificar()
        self.assertTrue(res["identico"])
        self.assertEqual(res["sha256_reconstruido"], sha(REF_CSV))
        itens = _itens()
        lidos = A19.ler_brutos_arquivados(itens)
        tabela = A19.montar_referencia(*A19._bytes_para_montar(itens, lidos))
        self.assertEqual(A19.csv_bytes(tabela), REF_CSV.read_bytes())
        self.assertEqual(len(tabela), 27)
        self.assertEqual(tabela["capital_co_ibge_6d"].nunique(), 27)
        self.assertEqual(A19.comparar_conteudo(tabela, tabela), [])

    def test_verificar_nao_grava_nada(self):
        antes = retrato(ROOT)
        with mock.patch("urllib.request.urlopen", side_effect=rede_proibida):
            self.assertEqual(A19.main(["--verificar"]), 0)
        self.assertEqual(retrato(ROOT), antes)


class TestOndeEscreve(_Base):
    def test_caminhos_de_escrita_declarados(self):
        self.assertEqual(A19.RAW, RAW)
        self.assertEqual(A19.OUT, OUT)
        self.assertEqual(A19.MANIFESTO_ARQ.parent, OUT)

    def test_baixar_so_escreve_no_bruto_e_em_output_aquisicao(self):
        """O --baixar, redirecionado para uma pasta temporária, só cria arquivos nos dois diretórios permitidos."""
        brutos = {it["url"]: (RAW / it["nome"]).read_bytes() for it in _itens()}
        cab = {"Last-Modified": "Wed, 19 Nov 2025 19:15:24 GMT"}
        antes = retrato(ROOT)
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp)
            raw_t, out_t = t / "data/raw/aquisicao/ibge_capitais_uf", t / "output/aquisicao"
            with mock.patch.object(A19, "RAW", raw_t), mock.patch.object(A19, "OUT", out_t), \
                 mock.patch.object(A19, "MANIFESTO_ARQ", out_t / A19.MANIFESTO_ARQ.name), \
                 mock.patch.object(A19, "_baixar", side_effect=lambda url, timeout=0: (brutos[url], cab)), \
                 mock.patch("urllib.request.urlopen", side_effect=rede_proibida):
                saida = A19.arquivar()
            criados = [p for p in t.rglob("*") if p.is_file()]
            fora = [p for p in criados if raw_t not in p.parents and out_t not in p.parents]
            self.assertEqual(fora, [], "arquivo escrito fora dos dois diretórios permitidos")
            self.assertEqual(len([p for p in criados if raw_t in p.parents]), 7)
            self.assertEqual([p for p in criados if out_t in p.parents], [out_t / A19.MANIFESTO_ARQ.name])
            self.assertEqual(saida["situacao"], "HASH_CONFERE")
            self.assertTrue(saida["reconstrucao_sem_rede"]["identico"])
        self.assertEqual(retrato(ROOT), antes, "o --baixar redirecionado alterou o repositório")

    def test_bruto_existente_nunca_e_substituido(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "x.json"
            p.write_bytes(b"[]")
            with self.assertRaises(A19.FalhaValidacao):
                A19._gravar_novo(p, b"[1]")
            self.assertEqual(p.read_bytes(), b"[]")

    def test_nome_datado_para_hash_divergente(self):
        self.assertEqual(A19.nome_datado("Localidades_Brasil_shp.zip", "2026-10-26"),
                         "Localidades_Brasil_shp_baixado_20261026.zip")


if __name__ == "__main__":
    unittest.main()
