"""Relatório de validação para os professores (`scripts/apresentacao/gerar_relatorio_validacao_professores.py`).

Confere, sobre o HTML e o PDF gravados em `output/apresentacao_validacao/`:
- o HTML gravado é idêntico ao regenerado a partir de `output/` (determinismo e relatório em dia);
- todo número do texto vem de um arquivo de `output/` lido pelo gerador (CSV ou JSON), formatado, ou é uma contagem
  que o teste recalcula sozinho dos mesmos arquivos, ou é um identificador (data, portaria, seção, figura, tabela);
- a geração não abre nenhum arquivo de `data/` (guarda em tempo de execução) e o texto não cita o arquivo de IVS
  antigo com número algum;
- as figuras PNG são as gravadas pelo pipeline, byte a byte, e os gráficos desenhados aqui reproduzem o E3;
- convenção do sinal, rótulos (exploratório, pré-especificado), a nota "em andamento" da produção e a ordem das
  seções;
- o PDF existe, tem entre 10 e 16 páginas A4 e não tem caracteres quebrados.

Os únicos dados sintéticos são os valores da classe `TestFormatacaoSintetica`, que testam só a formatação e nunca
tocam `output/`.
"""

from __future__ import annotations

import base64
import builtins
import html
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
SCRIPT = ROOT / "scripts" / "apresentacao" / "gerar_relatorio_validacao_professores.py"
SAIDA = ROOT / "output" / "apresentacao_validacao"
HTML = SAIDA / "relatorio_validacao_rdd_bolsa.html"
PDF = SAIDA / "relatorio_validacao_rdd_bolsa.pdf"


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


G = _importar("relatorio_validacao_professores_teste", SCRIPT)


class _GuardaData:
    """Registra todo arquivo aberto durante a geração, para provar que nada de `data/` é lido."""

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


# ---------------------------------------------------------------------------
# Números: tokens do HTML e valores das fontes
# ---------------------------------------------------------------------------

PT = re.compile(r"(?<![\w.,/])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?![\w/]|[.,]\d)")
EN = re.compile(r"(?<![\w])(\d+\.\d+(?:[eE][-+]?\d+)?)")

# Constantes de método e de exibição que não são resultado: nível do teste (5% e 95%), valor crítico normal, limiares
# de exibição de p, e o 1 (referência da razão de densidades e da razão de chances).
CONSTANTES = {"1", "5", "95", "1.96", "0.05", "0.001"}


def _canon(tok: str) -> str:
    return tok.replace(".", "").replace(",", ".")


def _formatos(x: float, out: set[str]) -> None:
    if not math.isfinite(x):
        return
    for v in (abs(x), abs(100 * x)):
        for nd in range(5):
            out.add(f"{v:.{nd}f}")
    out.add(repr(abs(x)))


def _tokens_texto(s: str, out: set[str]) -> None:
    for m in EN.finditer(s):
        try:
            _formatos(float(m.group(1)), out)
        except ValueError:
            pass
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
            _tokens_texto(str(k), out)
            _walk(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _walk(v, out)
    elif isinstance(obj, bool) or obj is None:
        return
    elif isinstance(obj, (int, float)):
        _formatos(float(obj), out)
    else:
        _tokens_texto(str(obj), out)


def valores_das_fontes() -> set[str]:
    out: set[str] = set()
    for p in G.FONTES_NUMEROS:
        if p.suffix == ".json":
            _walk(json.loads(p.read_text(encoding="utf-8")), out)
        elif p.suffix == ".csv":
            df = pd.read_csv(p, dtype=str, keep_default_na=False)
            for col in df.columns:
                _tokens_texto(str(col), out)
                for v in pd.unique(df[col]):
                    try:
                        _formatos(float(v), out)
                    except ValueError:
                        _tokens_texto(str(v), out)
                        continue
                    _tokens_texto(str(v), out)
    return out


def contagens_derivadas() -> set[str]:
    """Contagens que o relatório faz sobre as saídas (e não estão como valor nelas), recalculadas aqui."""
    out: set[str] = set()

    def add(*ns):
        for n in ns:
            out.add(str(int(n)))

    e5 = pd.read_csv(G.E5_ESPEC, dtype={"corte": str})
    y = e5[(e5["outcome"] == "Y1") & (e5["especificacao"] != "S0")]
    add(len(y))
    d = pd.read_csv(G.E6_DIAG, dtype={"corte": str})
    b = d[(d["diagnostico"] == "balanco_covariavel_pre") & (abs(d["h"] - 0.05) < 1e-9) & d["p_valor"].notna()]
    for _, g in b.groupby(["populacao", "corte"]):
        add(len(g), (g["p_valor"] < 0.05).sum())
    r = d[(d["diagnostico"] == "densidade_poisson_mass_points") & (abs(d["h"] - 0.05) < 1e-9)]
    ok = ((r["rho_ic95_inf"] <= 1) & (r["rho_ic95_sup"] >= 1)).sum()
    add(ok, len(r))
    e8 = json.loads(G.E8_RES.read_text(encoding="utf-8"))
    fam = [v["resumo_testes"] for v in e8["familias"].values()]
    add(sum(f["linhas_principais_no_bky"] for f in fam), sum(f["p_menor_005"] for f in fam),
        sum(f["q_menor_005"] for f in fam))
    prot = json.loads(G.PROT40.read_text(encoding="utf-8"))
    add(len(prot["exposicao_previa_a_outcomes"]))
    x2 = pd.read_csv(G.X2_EST)
    x2 = x2[x2["regra_ligacao"].str.startswith("ampla")]
    x2p = x2[x2["p_valor"].notna()]
    lee = x2[x2["lee_ic95_inf"].notna()]
    add(len(x2p), (x2p["p_valor"] < 0.05).sum(), len(lee), ((lee["lee_ic95_inf"] <= 0) & (lee["lee_ic95_sup"] >= 0)).sum())
    x3 = pd.read_csv(G.X3_EST)
    x3p = x3[x3["p_valor"].notna()]
    add(len(x3p), (x3p["p_valor"] < 0.05).sum())
    return out


def texto_visivel(doc: str) -> str:
    """Texto do HTML sem estilo, gráficos SVG, imagens, trechos de código e hashes."""
    t = re.sub(r"<style.*?</style>", " ", doc, flags=re.S)
    t = re.sub(r"<svg.*?</svg>", " ", t, flags=re.S)
    t = re.sub(r"<img[^>]*>", " ", t)
    t = re.sub(r"<code>.*?</code>", " ", t, flags=re.S)
    t = re.sub(r'<span class="hash">.*?</span>', " ", t, flags=re.S)
    t = re.sub(r"<title>.*?</title>", " ", t, flags=re.S)
    t = re.sub(r"(<h[23]>)\d+(?:\.\d+)?\.? ", r"\1", t)  # numeração dos títulos de seção
    t = re.sub(r"<[^>]+>", " ", t)
    return html.unescape(t)


# Identificadores que não são resultados: datas, número de ato (portaria), seção, figura, tabela, documento, protocolo,
# auditoria, ciclo, competência AAAAMM, códigos de outcome e anos.
IDENT = [
    r"\d{2}/\d{2}/\d{4}",
    r"\d{1,3}(?:\.\d{3})?/\d{4}",
    r"(?:Figura|Tabela)\s+\d+",
    r"(?:seção|seções|protocolo|auditoria|doc|Ciclo|ciclo|ciclos|Ciclos)\s+\d+(?:\.\d+)?[a-z]?(?:\s+(?:a|e)\s+\d+)*",
    r"\b[A-Z]\d+(?:\.[A-Z]?\d+)*\b",
    r"\b(?:19|20)\d{2}\b",
    r"\b\d{6}\b",
    r"\b[nN]º\s*\d+",
    r"\d+(?:\.\d+)? mil hab",
    r"(?<=\d)ª",
    r"\b\d+ª",
]


def tokens_do_texto(doc: str) -> list[str]:
    t = texto_visivel(doc)
    for p in IDENT:
        t = re.sub(p, " ", t)
    # o texto usa o formato brasileiro (vírgula decimal, ponto de milhar); número em formato inglês seria erro
    assert not re.search(r"(?<![\w.])\d+\.\d+(?![\d.]|\d{3})\b(?!\.\d)", re.sub(r"\d{1,3}(?:\.\d{3})+", " ", t)), \
        "número em formato inglês no texto"
    return [_canon(m.group(1)) for m in PT.finditer(t)]


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


class TestRelatorioValidacao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert HTML.exists(), f"rode {G.rel(SCRIPT)} antes dos testes"
        cls.doc = HTML.read_text(encoding="utf-8")
        with _GuardaData() as guarda:
            cls.regerado = G.gerar_html()
        cls.abertos = guarda.abertos

    def test_html_gravado_igual_ao_regenerado(self):
        self.assertEqual(self.doc, self.regerado, "HTML desatualizado: rode o gerador de novo")

    def test_geracao_nao_le_data(self):
        pasta_data = str((ROOT / "data").resolve())
        lidos = [a for a in self.abertos if a.startswith(pasta_data)]
        self.assertEqual(lidos, [], f"a geração abriu arquivos de data/: {lidos}")
        self.assertTrue(any("/output/" in a for a in self.abertos))

    def test_script_nao_cita_o_arquivo_de_ivs_antigo_nem_data(self):
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea_2010_municipios", src)
        self.assertNotIn('ROOT / "data"', src)
        self.assertNotIn("ivs_ipea_2010_municipios", self.doc)

    def test_script_nao_digita_numeros_de_resultado(self):
        """Varre o código: nenhum número de resultado é digitado em texto nem passado como literal aos formatadores."""
        import ast

        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        doc = ast.get_docstring(tree, clean=False)
        # literais permitidos: nível e valor crítico dos testes, 1 (referência de razões), números das chaves de seleção
        # de linhas ("0.300", "1", "2", "3") e o 0,3 do trecho citado do ato ("IVS maior que 0,3")
        permitidos = {"0", "1", "2", "3", "6", "95", "0.05", "1.96", "0300", "0400", "0.3"}
        pre = [r"(?<=<h2>)\d+\.\s", r"(?<=<h3>)\d\.\d\s", r"\b(?:utf-8|SHA-256)\b", r"\d+ dígitos", r"\b\d+ª"] + [
            p for p in IDENT if p not in (r"(?<=\d)ª", r"\b\d+ª")]
        fora: list[str] = []

        class V(ast.NodeVisitor):
            def visit_Constant(self, n):
                if isinstance(n.value, str) and n.value != doc and not n.value.lstrip().startswith("@page"):
                    t = n.value
                    for p in pre:
                        t = re.sub(p, " ", t)
                    for m in PT.finditer(t):
                        if _canon(m.group(1)) not in permitidos:
                            fora.append(f"linha {n.lineno}: {m.group(1)} em {n.value[:60]!r}")

        # o CSS é código de estilo, não texto do relatório
        css_nodes = [n for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CSS_EXTRA" for t in n.targets)]
        for n in css_nodes:
            n.value = ast.Constant(value="")
        V().visit(tree)
        self.assertEqual(fora, [], f"números digitados em texto: {fora}")
        # literais numéricos passados como 1º argumento aos formatadores
        tree2 = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        formatadores = {"br", "br_int", "pp", "sinal", "br_p", "br_mil", "pct_", "fmt_est", "corte_txt"}
        ruins = []
        for n in ast.walk(tree2):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in formatadores and n.args:
                a = n.args[0]
                if isinstance(a, ast.Constant) and isinstance(a.value, (int, float)):
                    ruins.append(f"linha {n.lineno}: {n.func.id}({a.value})")
        self.assertEqual(ruins, [], f"número literal passado a formatador: {ruins}")

    def test_todo_numero_do_texto_vem_de_output(self):
        fontes = valores_das_fontes() | contagens_derivadas() | CONSTANTES
        fora = sorted({t for t in tokens_do_texto(self.doc) if t not in fontes})
        self.assertEqual(fora, [], f"números do texto sem fonte em output/: {fora}")

    def test_numeros_chave_batem_com_as_saidas(self):
        e8 = json.loads(G.E8_RES.read_text(encoding="utf-8"))
        txt = texto_visivel(self.doc)
        h = e8["holm"]
        esperados = [G.br(h["P1"]["p_holm"], 3), G.br(h["P1"]["p_valor"], 3), G.br(h["P2"]["p_valor"], 3),
                     G.sinal(h["P1"]["tau"], 2), G.sinal(h["P2"]["tau"], 3)]
        c2 = e8["e9"]["principal"]["2"]
        esperados += [G.br(c2["rc_5mil"], 2), G.br(c2["rc_5mil_ic95"][0], 2), G.br(c2["rc_5mil_ic95"][1], 2)]
        e3 = pd.read_csv(G.E3_EST)
        for c in (0.3, 0.4):
            r = e3[(e3["populacao"] == "P1") & (e3["outcome"] == G.OUTCOME_FRAC) & (abs(e3["corte"] - c) < 1e-9)
                   & (e3["especificacao"] == "principal")].iloc[0]
            esperados += [G.pp(r["tau"]), G.pp(r["ic95_inf"]), G.pp(r["ic95_sup"]), G.br_p(r["p_valor"])]
        for e in esperados:
            self.assertIn(e, txt, f"número esperado ausente do texto: {e}")

    def test_p1_p2_holm_nao_rejeitam_e_o_texto_diz(self):
        e8 = json.loads(G.E8_RES.read_text(encoding="utf-8"))
        self.assertFalse(e8["holm"]["alguma_rejeitada"])
        txt = texto_visivel(self.doc)
        self.assertIn("Nenhuma primária rejeita zero depois do Holm", txt)
        self.assertIn("inconclusivo", txt)
        self.assertIn("não prova de ineficácia", txt)

    def test_figuras_sao_as_do_pipeline_byte_a_byte(self):
        imgs = re.findall(r'<img[^>]*src="data:image/png;base64,([^"]+)"', self.doc)
        self.assertEqual(len(imgs), len(G.FIGURAS_PIPELINE))
        arquivos = {p.read_bytes(): p for p in G.FIGURAS_PIPELINE}
        for b in imgs:
            self.assertIn(base64.b64decode(b), arquivos)
        for fig, prod in G.FIGURAS_PIPELINE.items():
            self.assertTrue(fig.exists() and prod.exists(), f"{fig} / {prod}")
            self.assertTrue(str(fig.resolve()).startswith(str((ROOT / "output").resolve())))

    def test_figuras_pedidas_estao_no_relatorio(self):
        for nome in ("regra_bolsa_ivs_oficial.png", "E6_indice_P1_agrupado.png", "E7_nivel_F3_1_U.png",
                     "E7_dird_F3_1_U.png", "E7_evento_F3_1_U.png", "E9_utilidade_ivs.png", "X6_descartes.png"):
            self.assertIn(nome, self.doc)
        self.assertEqual(self.doc.count("<svg"), 2, "esperados 2 gráficos desenhados aqui: RD e densidade")
        self.assertIn("RDD tradicional", self.doc)

    def test_grafico_rd_reproduz_o_e3(self):
        ctx = G.carregar()
        G.dados_graficos(ctx)
        for p in ctx["paineis_rd"]:
            r = ctx["est"][(ctx["est"]["populacao"] == p["pop"]) & (ctx["est"]["outcome"] == p["outcome"])
                           & (abs(ctx["est"]["corte"] - p["corte"]) < 1e-9)
                           & (abs(ctx["est"]["h"] - ctx["h_principal"]) < 1e-9)].iloc[0]
            self.assertAlmostEqual(p["tau"], r["tau"], places=9)
            self.assertAlmostEqual(p["beta"][2], r["tau"], places=6)
            self.assertGreater(p["bolsa_maior"], p["bolsa_menor"])

    def test_convencao_do_sinal_e_rotulos(self):
        txt = texto_visivel(self.doc)
        self.assertRegex(txt, r"Salto = valor estimado no corte do lado com bolsa maior")
        self.assertIn("menos o do lado com bolsa menor", txt)
        self.assertIn("pré-especificado", txt)
        self.assertIn("EXPLORATÓRIO", txt)
        self.assertIn("pacote", txt)
        self.assertIn("Não é o efeito de participar do PMM-E", txt)
        self.assertIn("Uma análise de produção (SIA/SIH/TISS) está em andamento", txt)
        for proibido in ("protocolo 47", "47_"):
            self.assertNotIn(proibido, txt)

    def test_failure_mode_so_como_registro(self):
        txt = texto_visivel(self.doc)
        self.assertIn("Nenhum número calculado com esse arquivo entra neste relatório", txt)
        i = txt.index("Registro de um failure mode")
        caixa = txt[i:txt.index("separado.", i)]
        caixa = re.sub(r"\d{2}/\d{2}/\d{4}", "", caixa)  # a data do último dia de uso
        caixa = re.sub(r'"IVS 2010"', "", caixa)  # o rótulo antigo do arquivo
        dig = re.findall(r"\d+", caixa)
        self.assertLessEqual(set(dig), {"16", "19"}, "a caixa do failure mode só pode citar as auditorias 16 e 19")

    def test_ordem_das_secoes(self):
        hs = re.findall(r"<h2>(.*?)</h2>", self.doc)
        pref = ["Em uma página", "1. ", "2. ", "3. ", "4. ", "5. ", "6. ", "7. ", "8. ", "Apêndice"]
        self.assertEqual(len(hs), len(pref), hs)
        for h, p in zip(hs, pref):
            self.assertTrue(h.startswith(p), (h, p))
        # exploratórios vêm depois da síntese; as primárias antes das secundárias
        self.assertLess(self.doc.index("5. Rodada multi-outcome"), self.doc.index("6. Síntese"))
        self.assertLess(self.doc.index("6. Síntese"), self.doc.index("7. Principais achados exploratórios"))

    def test_numeracao_de_tabelas_e_figuras_em_ordem(self):
        tabs = [int(n) for n in re.findall(r'<span class="fig-num">Tabela (\d+)\.</span>', self.doc)]
        figs = [int(n) for n in re.findall(r'<span class="fig-num">Figura (\d+)\.</span>', self.doc)]
        self.assertEqual(tabs, list(range(1, len(tabs) + 1)))
        self.assertEqual(figs, list(range(1, len(figs) + 1)))

    def test_nulos_nao_sao_chamados_de_efeito_zero(self):
        txt = texto_visivel(self.doc)
        self.assertIn("Dizer que a bolsa não funciona ou que o efeito é zero", txt)
        self.assertNotRegex(txt, r"(?i)a bolsa funciona")
        self.assertNotRegex(txt, r"(?i)\bprovou\b")

    def test_toda_tabela_de_resultado_tem_como_ler(self):
        tabelas = len(re.findall(r'<div class="tab-titulo">', self.doc))
        como = len(re.findall(r"<strong>Como ler\.</strong>", self.doc))
        # só as tabelas puramente descritivas de dados e de proveniência dispensam a caixa
        self.assertGreaterEqual(como, tabelas - 5)

    def test_pdf_existe_com_10_a_16_paginas_sem_caracteres_quebrados(self):
        self.assertTrue(PDF.exists())
        if not shutil.which("pdfinfo"):
            self.skipTest("pdfinfo ausente")
        info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
        n = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
        self.assertTrue(10 <= n <= 16, f"{n} páginas")
        self.assertIn("A4", info)
        if shutil.which("pdftotext"):
            txt = subprocess.run(["pdftotext", str(PDF), "-"], capture_output=True, text=True).stdout
            self.assertNotIn("�", txt)
            self.assertIn("RDD do adicional de bolsa do PMM-E", txt)

    def test_apendice_lista_hash_de_toda_entrada(self):
        for p in G.ENTRADAS_HASH + list(G.FIGURAS_PIPELINE):
            self.assertTrue(p.exists(), p)
            self.assertIn(G.sha256(p)[:12], self.doc)


class TestFormatacaoSintetica(unittest.TestCase):
    """Valores sintéticos (nunca gravados em output/): só a formatação e o sinal."""

    def test_formatacao_por_unidade(self):
        self.assertEqual(G.fmt_est("fracao (x100 = p.p.)", 0.05), "+5,0")
        self.assertEqual(G.fmt_est("fracao (x100 = p.p.)", -0.0728), "−7,3")
        self.assertEqual(G.fmt_est("razão de chances", 1.945), "1,95")
        self.assertEqual(G.fmt_est("desvios-padrao (indice)", -0.128), "−0,13")
        self.assertEqual(G.fmt_est("contagem por celula oferecida", 0.0627), "+0,063")
        self.assertEqual(G.fmt_ic("fracao (x100 = p.p.)", -0.1, 0.02), "[−10,0; +2,0]")

    def test_tipo_unidade(self):
        self.assertEqual(G.tipo_unidade("fracao (x100 = p.p.)"), "pp")
        self.assertEqual(G.tipo_unidade("horas SUS semanais"), "h")
        self.assertEqual(G.tipo_unidade("pontos da pontuacao do ciclo"), "pt")
        self.assertEqual(G.tipo_unidade("vinculos por 10 mil hab."), "n")


if __name__ == "__main__":
    unittest.main()
