"""Slides da contagem de vagas para os professores (`scripts/apresentacao/gerar_slides_contagem_vagas_professores.py`).

Confere, sobre o HTML e o PDF gravados em `output/apresentacao_validacao/`:
- o HTML gravado é idêntico ao regenerado a partir de `output/` (determinismo, sem data nem commit);
- todo número do texto visível e das anotações dos gráficos vem de `N_estimativas.csv`, `NA_estimativas.csv`,
  `E6_estimativas.csv` ou `N_resumo.json` (formatado), ou é identificador (N1, S-a, ciclo, IVS 2010, protocolo 48), ou é
  a reta desenhada da população 2022 (diagnóstico descritivo, único sem linha nos CSV; o teste a recalcula);
- o código não digita número de resultado (varredura por AST) e a geração não abre nada de `data/`;
- toda figura dos slides vem da pasta de figuras do próprio script, byte a byte, e nenhuma é a PNG de `N_figuras/` ou
  `NA_figuras/` (essas têm texto embutido);
- um gráfico por slide, no máximo quatro bullets curtos, "Como ler" no rodapé sem jargão e um só slide de notas técnicas;
- o PDF é 16:9, com uma página por slide, e não tem caracteres quebrados.

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
SCRIPT = ROOT / "scripts" / "apresentacao" / "gerar_slides_contagem_vagas_professores.py"
HTML = ROOT / "output" / "apresentacao_validacao" / "slides_contagem_vagas.html"
PDF = ROOT / "output" / "apresentacao_validacao" / "slides_contagem_vagas.pdf"
PASTA_FIG = ROOT / "output" / "apresentacao_validacao" / "slides_contagem_vagas_figuras"


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


G = _importar("slides_contagem_vagas_teste", SCRIPT)

PT = re.compile(r"(?<![\w.,/])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?![\w/]|[.,]\d)")
IDENT = [r"\b[NA]\d\b", r"\bS-[a-z]\b", r"\d+ª", r"IVS 2010", r"protocolo \d+", r"R\$ \d+ mil", r"\b10 mil\b",
         r"\bciclos? \d\b", r"\b\d a \d\b", r"população (?:de )?2022", r"\bV\d\b", r"\bN\d e N\d\b",
         r"#[0-9a-fA-F]{6}", r"\bh=0\.\d+"]
CONSTANTES = {"0", "1", "2", "3", "95", "0.001"}
JARGAO = ("kernel", "gamma", "CR1", "resíduo", "triangular", "EP ", "Holm")


def _canon(tok: str) -> str:
    return tok.replace(".", "").replace(",", ".")


def _formatos(x: float, out: set[str]) -> None:
    if not math.isfinite(x):
        return
    for v in (abs(x), abs(100 * x)):
        for nd in range(6):
            out.add(f"{v:.{nd}f}")
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
    for csv in (G.N_EST, G.NA_EST, G.E6_EST, G.ND_EST):
        df = pd.read_csv(csv)
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]):
                for v in df[c].dropna().unique():
                    _formatos(float(v), out)
            else:
                for v in df[c].dropna().astype(str).unique():
                    _tokens(v, out)
        for c in ("pop_media", "pop_mediana"):  # população média e mediana das faixas, em mil habitantes
            if c in df:
                for v in df[c].dropna().unique():
                    _formatos(float(v) / 1000, out)
        if "media_abaixo" in df:  # salto e IC em % da média abaixo (forest de robustez)
            for c in ("tau", "ic95_inf", "ic95_sup"):
                for v in (df[c] / df["media_abaixo"]).replace([math.inf, -math.inf], math.nan).dropna().unique():
                    _formatos(float(v), out)
    _walk(json.loads(G.N_RES.read_text(encoding="utf-8")), out)
    _walk(json.loads(G.ND_RES.read_text(encoding="utf-8")), out)
    # AD2: parte do salto da taxa (corte inferior) que vem do ciclo 2, em %
    ad = pd.read_csv(G.ND_EST, dtype={"corte": str, "ciclo": str})
    ad = ad[(ad["adendo"] == "AD2") & (ad["diagnostico"] == "AD2_A3") & (ad["outcome"] == "TAXA_VIC") & (ad["corte"] == "0.300")]
    tot = ad[ad["tipo_linha"] == "identidade"]["tau"].iloc[0]
    c2 = ad[ad["variante"] == "grupo_c2"]["contribuicao"].iloc[0]
    _formatos(c2 / tot, out)
    return out


def valores_populacao(d: dict) -> set[str]:
    """Reta desenhada da população 2022 (diagnóstico descritivo): recalculada com as funções do script 23."""
    out: set[str] = set()
    N23 = G._modulo_n()
    V = G._png_hab_para_mil(G._carregar_v(N23))
    for c in d["cortes"]:
        r = G._refit(N23, V, int(round(float(c) * 1000)), "pop_mil")["r"]
        for k in ("tau", "ic95_inf", "ic95_sup", "p_valor"):
            _formatos(float(r[k]), out)
    return out


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


def _slides(doc: str) -> list[str]:
    return re.findall(r'<section class="slide[^"]*">.*?</section>', doc, re.S)


def _texto(html: str) -> str:
    t = re.sub(r"<svg.*?</svg>", " ", html, flags=re.S)
    t = re.sub(r"<(code|style|script)>.*?</\1>", " ", t, flags=re.S)
    t = re.sub(r"<img[^>]*>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", t)


class TestSlidesContagemVagas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert HTML.exists(), f"rode {SCRIPT.name} antes dos testes"
        cls.doc = HTML.read_text(encoding="utf-8")
        with _GuardaData() as guarda:
            cls.regerado = G.montar_html()
        cls.abertos = guarda.abertos
        cls.slides = _slides(cls.doc)
        cls.d = G._dados()

    def test_html_gravado_igual_ao_regenerado(self):
        self.assertEqual(self.doc, self.regerado, "HTML desatualizado: rode o gerador de novo")

    def test_html_sem_data_nem_commit(self):
        self.assertIsNone(re.search(r"\b\d{2}/\d{2}/\d{4}\b|\b[0-9a-f]{40}\b", _texto(self.doc)))

    def test_geracao_nao_le_data(self):
        pasta_data = str((ROOT / "data").resolve()) + "/"
        self.assertEqual([a for a in self.abertos if a.startswith(pasta_data)], [])
        self.assertTrue(any("/output/" in a for a in self.abertos))
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", src)
        self.assertNotIn('ROOT / "data"', src)

    def test_todo_numero_do_texto_vem_de_output(self):
        fontes = valores_das_fontes() | valores_populacao(self.d) | CONSTANTES
        t = _texto(self.doc)
        # anotações dos gráficos SVG (coluna de valores)
        t += " " + " ".join(re.findall(r'class="val">([^<]*)<', self.doc))
        for p in IDENT:
            t = re.sub(p, " ", t)
        fora = sorted({_canon(m.group(1)) for m in PT.finditer(t)} - fontes)
        self.assertEqual(fora, [], f"números do texto sem fonte em output/: {fora}")

    def test_codigo_nao_digita_numeros_de_resultado(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        doc = ast.get_docstring(tree, clean=False)
        # CSS e JS são estilo/navegação; as funções de desenho (_svg_*, _png_*, figura da regra, refit) têm só geometria
        exentas = ("_svg_", "_png_", "_fig_regra", "_figura_rd", "_refit", "_confere", "_titulo", "_mil")
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in ("CSS_SLIDES", "JS_NAV")
                                                 for t in n.targets):
                n.value = ast.Constant(value="")
        permitidos_txt = {"0", "1", "2", "3", "95", "0300", "0400", "0.001"}
        fora, nums = [], []
        docstrings = {id(f.body[0].value) for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.body
                      and isinstance(f.body[0], ast.Expr) and isinstance(f.body[0].value, ast.Constant)}

        class V(ast.NodeVisitor):
            def visit_FunctionDef(self, n):
                if n.name.startswith(exentas):
                    return
                self.generic_visit(n)

            def visit_Constant(self, n):
                if isinstance(n.value, str) and n.value != doc and id(n) not in docstrings:
                    t = n.value
                    for p in IDENT + [r"\b(?:utf-8|SHA-256)\b", r"\bv\d\b", r"\bf2\b", r"\bdocs/06_execucao/49\b", r"\bdoc 49\b"]:
                        t = re.sub(p, " ", t)
                    for m in PT.finditer(t):
                        if _canon(m.group(1)) not in permitidos_txt:
                            fora.append(f"linha {n.lineno}: {m.group(1)} em {n.value[:50]!r}")
                elif isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
                    if n.value not in {0, 1, 2, 3, 100, 0.05, 0.001, 1e-6, 0.5, 0.1}:
                        nums.append(f"linha {n.lineno}: {n.value}")

        V().visit(tree)
        self.assertEqual(fora, [], f"números digitados em texto: {fora}")
        self.assertEqual(nums, [], f"literais numéricos suspeitos: {nums}")

    def test_figuras_vem_da_pasta_do_script_e_nao_de_n_figuras(self):
        imgs = re.findall(r'<img src="data:image/png;base64,([A-Za-z0-9+/=]+)"', self.doc)
        self.assertGreaterEqual(len(imgs), 7)
        daqui = {f.read_bytes() for f in PASTA_FIG.glob("*.png")}
        # o diagnóstico ND (doc 49b) grava figuras sem texto embutido; elas podem ser reutilizadas diretamente
        daqui |= {f.read_bytes() for f in G.ND_FIG.glob("*.png")}
        alheias = {f.read_bytes() for pasta in ("N_figuras", "NA_figuras", "E6_figuras")
                   for f in (ROOT / "output" / "rdd_bolsa" / pasta).glob("*.png")}
        for b64 in imgs:
            b = base64.b64decode(b64)
            self.assertIn(b, daqui)
            self.assertNotIn(b, alheias)
        svgs = re.findall(r"<svg.*?</svg>", self.doc, re.S)
        gravados = {f.read_text(encoding="utf-8").rstrip("\n") for f in PASTA_FIG.glob("*.svg")}
        self.assertGreaterEqual(len(svgs), 8)
        for sv in svgs:
            self.assertIn(sv, gravados)
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("N_figuras", src)
        self.assertNotIn("NA_figuras", src)
        self.assertNotIn("relatorio_validacao_rdd_bolsa", src.replace('ORIGEM = PASTA / "relatorio_validacao_rdd_bolsa.html"', ""))

    def test_figuras_rd_tem_dois_paineis_por_corte(self):
        for nome in ("porte_vagas_imediatas", "porte_populacao", "atracao_candidatos", "taxa_preenchimento",
                     "n1_sem_controle", "n1_com_controle"):
            self.assertTrue((PASTA_FIG / f"{nome}.png").exists(), nome)
        for c in self.d["cortes"]:
            self.assertEqual(self.doc.count("corte " + G._cs(float(c)) + " (bolsa de"), 0)  # títulos estão na PNG, não no HTML
        self.assertEqual(sorted(self.d["cortes"]), ["0.300", "0.400"])

    def test_slides_enxutos_e_sem_jargao(self):
        self.assertGreaterEqual(len(self.slides), 12)
        notas = [s for s in self.slides if 'class="slide notas"' in s]
        self.assertEqual(len(notas), 1, "um só slide de notas técnicas")
        self.assertTrue(self.slides[-1].startswith('<section class="slide notas"'))
        capas = [s for s in self.slides if "capa" in s.split(">")[0]]
        self.assertLessEqual(len(capas), 1)
        for s in self.slides:
            n_graf = len(re.findall(r'<img src=|<svg', s))
            lis = re.findall(r"<li>(.*?)</li>", s, re.S)
            if "figbox" in s:
                self.assertGreaterEqual(n_graf, 1)
                self.assertLessEqual(len(lis), 4, s[:120])
                palavras = sum(len(re.sub(r"<[^>]+>", "", li).split()) for li in lis)
                self.assertLessEqual(palavras, 45, f"{palavras} palavras: {s[:120]}")
                self.assertIn("<b>Como ler:</b>", s)
                como = re.search(r'<span class="cl">(.*?)</span>', s, re.S).group(1)
                for j in JARGAO:
                    self.assertNotIn(j, como)
            titulo = re.search(r'<h2 class="titulo">(.*?)</h2>|<h1>(.*?)</h1>', s, re.S)
            self.assertIsNotNone(titulo)
        # fora das notas técnicas e do slide de conclusão, nenhum jargão nos bullets das figuras
        for s in self.slides:
            if "figbox" in s:
                for li in re.findall(r"<li>(.*?)</li>", s, re.S):
                    for j in ("kernel", "gamma", "CR1", "resíduo"):
                        self.assertNotIn(j, li)

    def test_conclusoes_condizem_com_as_saidas(self):
        d = self.d
        cs = d["cortes"]
        for o in G.ROTULOS:
            self.assertGreaterEqual(G._linha_n(d, o, "S-a", "empilhado")["p_holm"], 0.05)
        txt = _texto(self.doc)
        self.assertIn("pacote do corte", txt)
        self.assertIn("Falta de evidência não é prova de efeito nulo", txt)
        self.assertIn("diagnóstico descritivo, fora do protocolo 48", self.doc)
        # títulos que afirmam algo precisam de dados que os sustentem
        atr = {c: G._linha_e6(d, "f1_1_cand_1a_opcao_por_celula", c) for c in cs}
        if "A atração não muda em nenhum dos dois cortes" in txt:
            self.assertTrue(all(not G._exclui(r) for r in atr.values()))
        taxa = {c: G._linha_e6(d, "f1_3_fracao_celulas_preenchidas_ch1", c) for c in cs}
        if "A taxa de preenchimento não aumenta do lado de bolsa maior" in txt:
            self.assertTrue(all(r["tau"] < 0 and not G._exclui(r) for r in taxa.values()))
        if "A oferta de vagas imediatas é menor à direita nos dois cortes, mas os intervalos são largos" in txt:
            for c in cs:
                r = G._unica(d["n"], outcome_id="VI", especificacao="S-c", variante="principal",
                             populacao="V1+V2+V3", corte=c)
                self.assertLess(r["tau"], 0)
                self.assertFalse(G._exclui(r))
        sem = {c: G._linha_n(d, "N1", "S-b", c) for c in cs}
        if "Sem controle, as vagas preenchidas não aumentam, e nenhum IC exclui zero" in txt:
            self.assertTrue(all(r["tau"] < 0 and not G._exclui(r) for r in sem.values()))
        if "o sinal negativo se concentra no corte" in txt:
            todas = [G._linha_n(d, o, e, c) for o in G.ROTULOS for e in ("S-a", "S-b") for c in cs]
            self.assertFalse(any(r["ic95_inf"] > 0 for r in todas))
            self.assertEqual({c for o in G.ROTULOS for e in ("S-a", "S-b") for c in cs
                              if G._exclui(G._linha_n(d, o, e, c))}, {cs[0]})

    def test_slides_do_diagnostico_nd_vem_do_nd_e_nao_atribuem_0300_ao_porte(self):
        ndf = pd.read_csv(G.ND_EST, dtype={"corte": str, "ciclo": str})
        c1, c2 = self.d["cortes"]
        ndres = json.loads(G.ND_RES.read_text(encoding="utf-8"))
        # as três figuras do ND estão nos slides, byte a byte, e o "Como ler" é o do ND
        for nome in ("ND_faixas_populacao.png", "ND_taxa_janelas.png", "ND_adendo_ciclos.png", "ND_adendo_cr_taxas.png",
                     "ND_faixas_vagas.png"):
            b64 = base64.b64encode((G.ND_FIG / nome).read_bytes()).decode("ascii")
            self.assertIn(b64, self.doc, nome)
            como = next(f["como_ler"] for f in ndres["saidas"]["figuras"] if f["arquivo"].endswith(nome))
            self.assertIn(como, self.doc)
        nd_slides = [s for s in self.slides if "ND_estimativas.csv" in s]
        self.assertEqual(len(nd_slides), 5)
        # ficam depois do N1 com controle e antes do forest
        pos = [self.slides.index(s) for s in nd_slides]
        n1_com = next(i for i, s in enumerate(self.slides) if "Com controle, " in s and "figbox" in s)
        self.assertEqual(pos, [n1_com + k for k in (1, 2, 3, 4, 5)])
        # o texto condiz com o ND: em c2 o controle quase tira a queda e a taxa não salta; em c1 o porte não salta
        def l(c, o, esp):
            return G._unica(ndf, amostra="POR_CORTE", diagnostico="D1", tipo_linha="estimativa", corte=c, outcome=o,
                            especificacao=esp, variante="principal")
        txt = _texto(self.doc)
        if "a queda acompanha a oferta e o porte" in txt:
            self.assertLess(abs(l(c2, "N1", "controle_protocolo_48")["tau"]), abs(l(c2, "N1", "sem_controle")["tau"]) / 2)
            self.assertFalse(G._exclui(l(c2, "TAXA_VIC", "taxa_ponderada")))
        if "a queda vem da taxa por vaga oferecida" in txt:
            self.assertFalse(G._exclui(l(c1, "log_pop", "sem_controle")))
            self.assertTrue(G._exclui(l(c1, "TAXA_VIC", "taxa_ponderada")))
        # adendo AD2: ciclo 2 responde por cerca de metade do salto em c1, com mais reserva e nenhuma vaga só de reserva preenchida
        def ad(**k):
            return G._unica(ndf, adendo="AD2", **k)
        tot = ad(diagnostico="AD2_A3", tipo_linha="identidade", corte=c1, outcome="TAXA_VIC", variante="soma_das_contribuicoes")
        c2g = ad(diagnostico="AD2_A3", tipo_linha="contribuicao", corte=c1, outcome="TAXA_VIC", variante="grupo_c2")
        cr2 = ad(diagnostico="AD2_A3", tipo_linha="estimativa", corte=c1, populacao="V2", outcome="FRAC_CR")
        so_cr = ndres["adendo_2026_10_21"]["taxa_separada_por_tipo_de_vaga"]["celulas_por_tipo"]["ciclo 2 / so_cr"]["alocados"]
        if "metade da queda vem do ciclo 2" in txt:
            self.assertLess(abs(c2g["contribuicao"] / tot["tau"] - 0.5), 0.1)
            self.assertTrue(G._exclui(cr2))
            self.assertEqual(so_cr, 0)
            self.assertIn("concentrada no ciclo 2 e ligada às vagas de reserva (diagnóstico)", txt)
        if "A fração de vagas de reserva sobe em" in txt:
            self.assertTrue(G._exclui(ad(diagnostico="AD2_A1", tipo_linha="estimativa", corte=c1, outcome="FRAC_CR")))
            self.assertFalse(G._exclui(ad(diagnostico="AD2_A1", tipo_linha="estimativa", corte=c2, outcome="FRAC_CR")))
        # nenhum slide fora do ND atribui a queda em c1 ao porte
        for s in self.slides:
            if s not in nd_slides:
                self.assertNotIn("puxa a contagem para baixo", s)
        # conclusão e notas técnicas
        self.assertIn("Empilhar os cortes junta dois padrões diferentes; por isso tudo aqui é por corte.", txt)
        self.assertIn("não muda o Holm", self.slides[-1])
        self.assertIn("fora do protocolo 48", self.slides[-1])

    def test_forest_mostra_cortes_separados_e_empilhado_secundario(self):
        self.assertIn("secundário", self.doc)
        for c in self.d["cortes"]:
            self.assertIn(f"corte {G._cs(float(c))}", self.doc)

    def test_pdf_16x9_uma_pagina_por_slide_sem_caracteres_quebrados(self):
        self.assertTrue(PDF.exists())
        if not shutil.which("pdfinfo"):
            self.skipTest("pdfinfo ausente")
        info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
        pag = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
        self.assertEqual(pag, len(self.slides))
        m = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", info)
        self.assertAlmostEqual(float(m.group(1)) / float(m.group(2)), 16 / 9, places=2)
        if shutil.which("pdftotext"):
            txt = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True, text=True).stdout
            self.assertNotIn("�", txt)
            self.assertIn("Nº de vagas preenchidas como variável de efeito", re.sub(r"\s+", " ", txt))


if __name__ == "__main__":
    unittest.main()
