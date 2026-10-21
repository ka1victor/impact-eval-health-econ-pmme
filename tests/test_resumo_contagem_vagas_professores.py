"""Resumo da contagem de vagas para os professores (`scripts/apresentacao/gerar_resumo_contagem_vagas_professores.py`).

Confere, sobre o HTML e o PDF gravados em `output/apresentacao_validacao/`:
- o HTML gravado é idêntico ao regenerado a partir de `output/` (determinismo e resumo em dia);
- todo número do texto visível vem de `N_estimativas.csv`, `NA_estimativas.csv` ou `N_resumo.json` (formatado), ou é
  identificador (N1, A4, S-a, ciclo, "1ª chamada", IVS 2010, protocolo 48);
- números-chave da tabela e da robustez batem com as saídas;
- o código não digita número de resultado (varredura por AST) e a geração não abre nada de `data/`;
- a figura é a PNG do pipeline, byte a byte; o PDF é A4, tem de 1 a 3 páginas e não tem caracteres quebrados.

Nenhum dado sintético: o teste só lê `output/`.
"""

from __future__ import annotations

import ast
import base64
import builtins
import importlib.util
import io
import json
import math
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apresentacao" / "gerar_resumo_contagem_vagas_professores.py"
HTML = ROOT / "output" / "apresentacao_validacao" / "resumo_contagem_vagas.html"
PDF = ROOT / "output" / "apresentacao_validacao" / "resumo_contagem_vagas.pdf"


def _importar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        sys.modules[nome] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


G = _importar("resumo_contagem_vagas_teste", SCRIPT)

PT = re.compile(r"(?<![\w.,/])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?![\w/]|[.,]\d)")
# identificadores e constantes que não são resultado
IDENT = [r"\b[NA]\d\b", r"\bS-[a-z]\b", r"\d+ª", r"IVS 2010", r"protocolo \d+", r"R\$ \d+ mil", r"\b10 mil\b",
         r"\bciclos? \d\b", r"\b\d a \d\b"]
CONSTANTES = {"0", "1", "2", "3", "95", "0.001"}


def _canon(tok: str) -> str:
    return tok.replace(".", "").replace(",", ".")


def _formatos(x: float, out: set[str]) -> None:
    if not math.isfinite(x):
        return
    for nd in range(6):
        out.add(f"{abs(x):.{nd}f}")
    out.add(repr(abs(x)))


def _tokens(s: str, out: set[str]) -> None:
    for m in PT.finditer(s):
        c = _canon(m.group(1))
        out.add(c)
        try:
            _formatos(float(c), out)
        except ValueError:
            pass


def _walk(obj, out: set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            _tokens(str(k), out)
            _walk(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, out)
    elif isinstance(obj, bool) or obj is None:
        return
    elif isinstance(obj, (int, float)):
        _formatos(float(obj), out)
    else:
        _tokens(str(obj), out)


def valores_das_fontes() -> set[str]:
    out: set[str] = set()
    for csv in (G.N_EST, G.NA_EST):
        df = pd.read_csv(csv)
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]):
                for v in df[c].dropna().unique():
                    _formatos(float(v), out)
            else:
                for v in df[c].dropna().astype(str).unique():
                    _tokens(v, out)
    _walk(json.loads(G.N_RES.read_text(encoding="utf-8")), out)
    return out


def texto_visivel(doc: str) -> str:
    t = re.sub(r"<style>.*?</style>", " ", doc, flags=re.S)
    t = re.sub(r"<code>.*?</code>", " ", t, flags=re.S)
    t = re.sub(r"<img[^>]*>", " ", t)
    t = re.sub(r"<title>.*?</title>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("&ldquo;", "“").replace("&rdquo;", "”")
    return re.sub(r"\s+", " ", t)


class _GuardaData:
    def __init__(self):
        self.abertos: list[str] = []

    def __enter__(self):
        self._open, self._io_open = builtins.open, io.open
        guarda = self

        def aberto(f, *a, **k):
            if isinstance(f, (str, Path)):
                guarda.abertos.append(str(Path(f).resolve()))
            return guarda._open(f, *a, **k)

        builtins.open = aberto
        io.open = aberto
        return self

    def __exit__(self, *exc):
        builtins.open, io.open = self._open, self._io_open


class TestResumoContagemVagas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert HTML.exists(), f"rode {SCRIPT.name} antes dos testes"
        cls.doc = HTML.read_text(encoding="utf-8")
        with _GuardaData() as guarda:
            cls.regerado = G.montar_html()
        cls.abertos = guarda.abertos
        cls.txt = texto_visivel(cls.doc)

    def test_html_gravado_igual_ao_regenerado(self):
        self.assertEqual(self.doc, self.regerado, "HTML desatualizado: rode o gerador de novo")

    def test_html_sem_data_nem_commit(self):
        self.assertIsNone(re.search(r"\b\d{2}/\d{2}/\d{4}\b|\b[0-9a-f]{40}\b", self.txt))

    def test_geracao_nao_le_data(self):
        pasta_data = str((ROOT / "data").resolve()) + "/"
        self.assertEqual([a for a in self.abertos if a.startswith(pasta_data)], [])
        self.assertTrue(any("/output/" in a for a in self.abertos))
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", src)
        self.assertNotIn('ROOT / "data"', src)

    def test_todo_numero_do_texto_vem_de_output(self):
        t = self.txt
        for p in IDENT:
            t = re.sub(p, " ", t)
        fontes = valores_das_fontes() | CONSTANTES
        fora = sorted({_canon(m.group(1)) for m in PT.finditer(t)} - fontes)
        self.assertEqual(fora, [], f"números do texto sem fonte em output/: {fora}")

    def test_codigo_nao_digita_numeros_de_resultado(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        doc = ast.get_docstring(tree, clean=False)
        for n in ast.walk(tree):  # o CSS é estilo, não texto
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CSS_EXTRA" for t in n.targets):
                n.value = ast.Constant(value="")
        permitidos_txt = {"0", "1", "2", "3", "95", "0300", "0400", "0.001"}  # 0,001: limiar de exibição do p
        fora, nums = [], []
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value != doc:
                t = n.value
                for p in IDENT + [r"\b(?:utf-8|SHA-256)\b", r"<h2>\d\.", r"\bv\d\b"]:
                    t = re.sub(p, " ", t)
                for m in PT.finditer(t):
                    if _canon(m.group(1)) not in permitidos_txt:
                        fora.append(f"linha {n.lineno}: {m.group(1)} em {n.value[:50]!r}")
            elif isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
                if n.value not in {0, 1, 2, 3, 0.05, 0.001}:
                    nums.append(f"linha {n.lineno}: {n.value}")
        self.assertEqual(fora, [], f"números digitados em texto: {fora}")
        self.assertEqual(nums, [], f"literais numéricos suspeitos: {nums}")

    def test_numeros_chave_batem_com_as_saidas(self):
        n = pd.read_csv(G.N_EST)
        res = json.loads(G.N_RES.read_text(encoding="utf-8"))
        esperados = []
        for oid, esp in [("N1", "S-a"), ("N1", "S-b"), ("N2", "S-a"), ("N3", "S-b"), ("N4", "S-a")]:
            r = n[(n["outcome_id"] == oid) & (n["especificacao"] == esp) & (n["variante"] == "principal")
                  & (n["corte"].astype(str) == "empilhado") & (n["populacao"].str.contains(r"\+"))]
            r = r.assign(k=r["populacao"].str.count(r"\+"))
            r = r[r["k"] == r["k"].max()].iloc[0]
            esperados += [G._fmt(r["tau"], 2), G._fmt(r["ic95_inf"], 2), G._fmt(r["ic95_sup"], 2),
                          G._p(r["p_valor"]), G._num(r["media_abaixo"]), G._num(r["mde"])]
            if esp == "S-a":
                esperados.append(G._num(r["p_holm"], 3))
        sens = next(x for x in res["sensibilidade_coeficiente_unico_auditoria_20"]["linhas"] if x["outcome_id"] == "N1")
        esperados += [G._fmt(sens["tau_coef_unico"], 2), G._num(sens["p_holm_coef_unico"], 3)]
        na = pd.read_csv(G.NA_EST)
        a1 = na[(na["outcome_id"] == "A1_PREENCH_10K") & (na["especificacao"] == "A1") & (na["variante"] == "principal")
                & (na["ciclo"] == "1+2+3") & (na["corte"].astype(str) == "empilhado")].iloc[0]
        esperados += [G._fmt(a1["tau"], 3), G._num(a1["p_valor"], 3)]
        a4 = na[(na["outcome_id"] == "N1") & (na["variante"] == "com_covariaveis") & (na["ciclo"] == "1+2+3")
                & (na["corte"].astype(str) == "empilhado")].iloc[0]
        esperados += [G._fmt(a4["tau"], 2), G._num(a4["p_valor"], 3)]
        for e in esperados:
            self.assertIn(e, self.txt, f"número esperado ausente: {e}")

    def test_conclusoes_condizem_com_as_saidas(self):
        d = G._dados()
        for o in G.ROTULOS:
            self.assertLess(d["linhas"][(o, "S-a")]["tau"], 0)
            self.assertLess(d["linhas"][(o, "S-b")]["tau"], 0)
            self.assertGreaterEqual(d["linhas"][(o, "S-a")]["p_holm"], 0.05)
        self.assertIn("nenhuma rejeita zero", self.txt)
        self.assertIn("pacote do corte", self.txt)
        self.assertIn("Não é o degrau isolado nem a participação no PMM-E", self.txt)
        self.assertIn("Falta de evidência não é prova de efeito nulo", self.txt)
        self.assertEqual(sorted(d["cortes"]), [0.3, 0.4])

    def test_figura_e_a_do_pipeline_byte_a_byte(self):
        b64 = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", self.doc).group(1)
        self.assertEqual(base64.b64decode(b64), G.FIGURA.read_bytes())

    def test_secoes_em_ordem_e_como_ler(self):
        titulos = re.findall(r"<h2>(\d)\.", self.doc)
        self.assertEqual(titulos, ["1", "2", "3", "4", "5", "6"])
        self.assertIn("<b>Como ler.</b>", self.doc)

    def test_pdf_a4_ate_3_paginas_sem_caracteres_quebrados(self):
        self.assertTrue(PDF.exists())
        if not shutil.which("pdfinfo"):
            self.skipTest("pdfinfo ausente")
        info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
        pag = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
        self.assertTrue(1 <= pag <= 3, f"{pag} páginas")
        self.assertIn("A4", info)
        if shutil.which("pdftotext"):
            txt = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True, text=True).stdout
            self.assertNotIn("�", txt)
            self.assertIn("Nº de vagas preenchidas como variável de efeito", txt)


if __name__ == "__main__":
    unittest.main()
