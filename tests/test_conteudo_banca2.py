"""Testes do conteúdo canônico da banca 2 (`docs/07_apresentacoes/banca2/`) e do gerador de figuras.

Quatro partes:

1. `TestFormatacaoSintetica`: o formatador e as funções de escala do gerador
   (`scripts/apresentacao/gerar_figuras_banca2.py`) com valores SINTÉTICOS
   fixados em memória. Nada é gravado em `output/` nem em `data/`.
2. `TestNumerosContraFontes`: cada código de `numeros_banca2.json` é relido do
   arquivo-fonte pelo seletor declarado e formatado aqui, de forma independente
   do gerador; o valor tem de bater com o JSON e com o bloco gerado do doc 03.
   Os alvos vêm dos arquivos de `output/`; nenhum número é digitado.
3. `TestSlides` e `TestOutrosDocs`: todo número de cada slide do doc 02 é o valor
   de um código listado na linha `**Números:**` do slide ou um parâmetro do
   protocolo; README, roteiro e doc 03 só têm números registrados ou
   parâmetros.
4. `TestFiguras` e `TestIntegridade`: toda figura citada existe e foi produzida
   por script do pipeline (hash do manifesto, ou listada no resumo da etapa);
   todo número desenhado nas figuras novas é registrado ou parâmetro; o
   gerador não lê o arquivo de IVS errado.
5. `TestDeck`: o deck derivado (`gerar_deck_banca2.py`) traz os títulos e o
   texto do doc 02, só números registrados, as correções do plano (§2) e
   hashes atuais; se `PMME_DECK_GRUPO` apontar para o deck do grupo, confere
   o determinismo refazendo o deck numa pasta temporária.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import re
import sys
import tempfile
import unittest
import zipfile
from html import unescape
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apresentacao" / "gerar_figuras_banca2.py"
SCRIPT_DECK = ROOT / "scripts" / "apresentacao" / "gerar_deck_banca2.py"
SAIDA = ROOT / "output" / "apresentacao_banca2"
NUMEROS = SAIDA / "numeros_banca2.json"
MANIFESTO = SAIDA / "manifesto_figuras.json"
DOCS = ROOT / "docs" / "07_apresentacoes" / "banca2"
DOC01, DOC02, DOC03, README = (DOCS / "01_roteiro_narrativo.md", DOCS / "02_conteudo_slides.md",
                               DOCS / "03_proveniencia_figuras_e_numeros.md", DOCS / "README.md")
ARQUIVO_ERRADO = "data/ivs_ipea_2010_municipios.csv"  # só citado: nenhum teste nem gerador o lê
TEM_SAIDAS = NUMEROS.exists() and MANIFESTO.exists()
DECK, MANIF_DECK = SAIDA / "deck_banca2.pptx", SAIDA / "manifesto_deck_banca2.json"  # um arquivo só
TEM_DECK = DECK.exists() and MANIF_DECK.exists()

_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("gerar_figuras_banca2", SCRIPT)
G = importlib.util.module_from_spec(_spec)
sys.modules["gerar_figuras_banca2"] = G
_spec.loader.exec_module(G)
_spec_d = importlib.util.spec_from_file_location("gerar_deck_banca2", SCRIPT_DECK)
_D = importlib.util.module_from_spec(_spec_d)
sys.modules["gerar_deck_banca2"] = _D
_spec_d.loader.exec_module(_D)
sys.dont_write_bytecode = _bytecode

MENOS = "−"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Formatador independente (não usa o do gerador)
# --------------------------------------------------------------------------

def _br(x: float, nd: int) -> str:
    inteiro, _, frac = f"{abs(x):.{nd}f}".partition(".")
    grupos = []
    while len(inteiro) > 3:
        grupos.insert(0, inteiro[-3:])
        inteiro = inteiro[:-3]
    grupos.insert(0, inteiro)
    return ".".join(grupos) + ("," + frac if nd else "")


def formatar(valor, formato: str) -> str:
    if formato == "txt":
        return str(valor)
    if formato == "fracao":
        a, b = str(valor).split("/")
        return f"{_br(int(a), 0)}/{_br(int(b), 0)}"
    x = float(valor)
    if formato == "int":
        assert x == int(x), valor
        return _br(x, 0)
    if formato == "p3":
        return "< 0,001" if x < 0.001 else _br(x, 3)
    tipo, nd, sinal = re.fullmatch(r"(d|pp|pct)(\d)(s?)", formato).groups()
    nd = int(nd)
    if tipo in ("pp", "pct"):
        x *= 100
    corpo = _br(x, nd)
    eh_zero = set(corpo) <= set("0.,")
    if sinal:
        return ("+" if x >= 0 or eh_zero else MENOS) + corpo
    return corpo if x >= 0 or eh_zero else MENOS + corpo


# --------------------------------------------------------------------------
# Tokens numéricos e limpeza de texto
# --------------------------------------------------------------------------

NUM = re.compile(r"(?<![\w.,/])[−+-]?(?:\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?!\w)")
PERMITIDOS = {"0,300", "0,400", "0,3", "0,4", "0,301", "0,050", "0,030", "0,080", "0,05", "1,96", "0,001",
              "1", "2", "3", "5", "10", "15", "20", "+10", "+25", "25", "95", "90", "80"}
MAX_SLIDE = 60  # números de slide (deck do grupo, até 36; deck proposto, até 53) nos quadros do doc 02


def limpar(texto: str) -> str:
    t = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    t = re.sub(r"(?m)^\*\*Números:\*\*.*?(?=\n\n|\Z)", "", t, flags=re.S)  # linha de códigos
    t = re.sub(r"```.*?```", "", t, flags=re.S)
    t = re.sub(r"`[^`]*`", "", t)                                           # caminhos e códigos
    t = re.sub(r"\]\([^)]*\)", "]", t)                                      # links e imagens
    t = re.sub(r"\[\d{2}(?:[,\s][^\]]*)?\]", "[]", t)                         # [01, §3]: referência a doc
    t = t.replace("SHA-256", "")
    t = re.sub(r"(?m)^#+\s+\d+\.", "", t)                                   # número de seção no título
    t = re.sub(r"(?m)^\s*\d+\.\s", "", t)                                   # listas numeradas
    t = re.sub(r"\b\d{2}/\d{2}/\d{4}\b", "", t)                             # datas
    t = re.sub(r"\b\d{4}-\d{2}\b", "", t)                                   # competências
    t = re.sub(r"\b20\d{4}\b", "", t)                                       # competência AAAAMM
    t = re.sub(r"\b\d+(?:\.\d+)?/\d{4}\b", "", t)                           # atos normativos
    t = re.sub(r"§+\s?\d+(?:[.,–-]\d+)*", "", t)                            # seções
    t = re.sub(r"\b\d+(?:\.\d+){2,}\b", "", t)                              # itens de edital
    t = re.sub(r"\b(?:docs?|seção|auditorias?|pedido|protocolos?|tarefa|slides?|banca|errata)\s+\d+[a-z]?"
               r"(?:\s*(?:,|e|a|–|-)\s*\d+[a-z]?)*", "", t, flags=re.I)
    return t


def tokens(texto: str) -> set[str]:
    return set(NUM.findall(texto))


def ano(tok: str) -> bool:
    return tok.isdigit() and 2000 <= int(tok) <= 2030


def blocos_do_doc03() -> dict[str, str]:
    t = DOC03.read_text(encoding="utf-8")
    ini, fim = t.index(G.MARCA_INI) + len(G.MARCA_INI), t.index(G.MARCA_FIM)
    linhas = {}
    for ln in t[ini:fim].strip().splitlines()[2:]:
        cel = [c.strip() for c in re.split(r"(?<!\\)\|", ln)[1:-1]]
        linhas[cel[0].strip("`")] = cel[1]
    return linhas


def slides() -> list[dict]:
    t = DOC02.read_text(encoding="utf-8")
    corpo = t[t.index("<!-- deck:inicio -->"):t.index("<!-- apendice:fim -->")]
    partes = re.split(r"(?m)^(?=#{1,2} )", corpo)
    out = []
    for p in partes:
        if not re.match(r"## ", p):  # `#` marca a seção do deck do grupo, não é slide
            continue
        titulo = p.splitlines()[0]
        m = re.search(r"(?m)^\*\*Números:\*\*(.*?)(?=\n\n|\Z)", p, flags=re.S)
        codigos = re.findall(r"`([A-Z0-9_]+)`", m.group(1)) if m else None
        out.append({"titulo": titulo, "texto": p, "codigos": codigos})
    return out


def todos_valores(numeros: dict) -> set[str]:
    vals = set()
    for b in ("numeros", "failure_mode", "texto_citado"):
        for e in numeros[b].values():
            vals |= tokens(e["valor"])
    return vals


# --------------------------------------------------------------------------
# 1. Sintético
# --------------------------------------------------------------------------

class TestFormatacaoSintetica(unittest.TestCase):
    """Formatador e escalas do gerador com valores sintéticos fixados aqui (não são resultados)."""

    CASOS_SINTETICOS = [(-0.0726, "pp1s"), (0.0338, "pp1s"), (-0.12832, "d2s"), (0.0834, "d3s"),
                        (0.85107, "d2"), (0.00099, "p3"), (0.4257, "p3"), (5714.0, "int"), (0.3333, "pct0s"),
                        (0.784, "pct0"), (0.123, "pct1"), (-2.04, "d1s"), (-0.0004, "pp1s"), ("404/404", "fracao"),
                        ("5565/5565", "fracao")]

    def test_igual_ao_formatador_independente(self) -> None:
        for v, f in self.CASOS_SINTETICOS:
            self.assertEqual(G.fmt(v, f), formatar(v, f), (v, f))

    def test_casos_conhecidos(self) -> None:
        self.assertEqual(G.fmt(-0.0726, "pp1s"), MENOS + "7,3")
        self.assertEqual(G.fmt(0.0338, "pp1s"), "+3,4")
        self.assertEqual(G.fmt(0.00099, "p3"), "< 0,001")
        self.assertEqual(G.fmt(5714.0, "int"), "5.714")
        self.assertEqual(G.fmt("5565/5565", "fracao"), "5.565/5.565")
        self.assertEqual(G.fmt(-0.0004, "pp1s"), "+0,0")  # zero arredondado não leva sinal negativo

    def test_escala_simetrica(self) -> None:
        lo, hi = G.limites_simetricos(-3.0, 1.0, 0.0, log=False, folga=1.0)
        self.assertAlmostEqual(lo, -3.0)
        self.assertAlmostEqual(hi, 3.0)
        lo, hi = G.limites_simetricos(0.5, 4.0, 1.0, log=True, folga=1.0)
        self.assertAlmostEqual(math.log(lo), -math.log(4.0))
        self.assertAlmostEqual(math.log(hi), math.log(4.0))

    def test_exclui_nulo(self) -> None:
        self.assertTrue(G.exclui_nulo(-0.5, -0.9, -0.1, 0.0))
        self.assertFalse(G.exclui_nulo(-0.5, -0.9, 0.1, 0.0))
        self.assertTrue(G.exclui_nulo(1.9, 1.4, 2.5, 1.0))
        self.assertFalse(G.exclui_nulo(1.1, 0.9, 1.4, 1.0))

    def test_tokens_sinteticos(self) -> None:
        txt = "−0,13 DP [−0,44; +0,19], 4.362 de 5.565 (78%), F1.3, V1+V2, 1ª chamada, 2025-10"
        self.assertEqual(tokens(limpar(txt)), {MENOS + "0,13", MENOS + "0,44", "+0,19", "4.362", "5.565", "78"})


# --------------------------------------------------------------------------
# 2. Números contra as fontes
# --------------------------------------------------------------------------

def _transf(v, transf: list) -> float:
    x = float(v)
    for op in transf:
        x = x * float(op[1]) if op[0] == "mul" else (x + float(op[1]) if op[0] == "add" else math.exp(x))
    return x


def _resolver_independente(sel: dict, brutos: dict, calculados: dict):
    v = _resolver_bruto(sel, brutos, calculados)
    return _transf(v, sel["transf"]) if "transf" in sel else v


def _resolver_bruto(sel: dict, brutos: dict, calculados: dict):
    if "descritiva" in sel:
        return calculados["descritivas"][sel["descritiva"]]
    if "json" in sel:
        obj = json.loads((ROOT / sel["json"]).read_text(encoding="utf-8"))
        for k in sel["caminho"]:
            obj = obj[k]
        return obj
    if "json_lista" in sel:
        obj = json.loads((ROOT / sel["json_lista"]).read_text(encoding="utf-8"))
        for k in sel["caminho"]:
            obj = obj[k]
        ach = [r for r in obj if all(str(r.get(k)) == v for k, v in sel["filtro"].items())]
        assert len(ach) == 1, sel
        v = ach[0][sel["campo"]]
        return v[sel["indice"]] if "indice" in sel else v
    if "csv" in sel:
        d = pd.read_csv(ROOT / sel["csv"], dtype=str, keep_default_na=False)
        for k, v in sel["filtro"].items():
            d = d[d[k] == v]
        assert len(d) == 1, sel
        return d[sel["coluna"]].iloc[0] if sel.get("texto_csv") else float(d[sel["coluna"]].iloc[0])
    if "texto" in sel:
        p = ROOT / sel["texto"]
        txt = (json.dumps(json.loads(p.read_text(encoding="utf-8")), ensure_ascii=False) if p.suffix == ".json"
               else p.read_text(encoding="utf-8"))
        ach = set(re.findall(sel["regex"], txt))
        assert len(ach) == 1, (sel, ach)
        return ach.pop()
    if "razao" in sel:
        a, b = sel["razao"]
        return float(brutos[a]) / float(brutos[b])
    if "calculado" in sel:
        return calculados[sel["calculado"]]
    raise AssertionError(sel)


def _descritivas_independentes() -> dict[str, float]:
    """Recontagem independente das descritivas por ciclo (quadro de células e cobertura das fontes)."""
    d = pd.read_parquet(ROOT / "output/rdd_bolsa/outcomes/outcomes_V_celula.parquet")
    c0, c1 = G.CORTES
    out: dict[str, float] = {}
    for c in (1, 2, 3):
        g = d[d["ciclo"] == c]
        faixa = g["ivs_2010_oficial"].map(lambda v: None if pd.isna(v) else
                                          ("F3" if v <= c0 + 1e-9 else ("F2" if v <= c1 + 1e-9 else "F1")))
        out.update({f"C{c}_MUN": g["co_ibge"].nunique(), f"C{c}_CEL": len(g),
                    f"C{c}_VI": g["vagas_imediatas"].sum(), f"C{c}_CR": g["vagas_cr"].sum(),
                    f"C{c}_CAND1": g["n_cand_1a_opcao"].sum(), f"C{c}_PRE1": g["f1_3_preenchida_ch1"].sum(),
                    f"C{c}_PRE1_PCT": g["f1_3_preenchida_ch1"].sum() / len(g),
                    f"C{c}_SEM_IVS": g.loc[faixa.isna(), "co_ibge"].nunique()})
        if g["f1_4_preenchida_ate_ch2"].notna().all():
            out[f"C{c}_PRE2"] = g["f1_4_preenchida_ate_ch2"].sum()
            out[f"C{c}_PRE2_PCT"] = g["f1_4_preenchida_ate_ch2"].sum() / len(g)
        for k in ("F1", "F2", "F3"):
            out[f"C{c}_{k}"] = g.loc[faixa == k, "co_ibge"].nunique()
    out["IVS_MUN"] = pd.read_csv(ROOT / "output/aquisicao/a08_ivs_2010_oficial_municipio.csv")["ivs"].notna().sum()
    out["POP_MUN"] = len(pd.read_csv(ROOT / "output/aquisicao/populacao_censo2022_municipios.csv", dtype=str))
    return {k: float(v) for k, v in out.items()}


def _lado_errado(coluna_ivs: str, arquivo: str, chave: str) -> int:
    """Recontagem independente: municípios do quadro c1_ch1 cuja faixa anunciada não é a dos cortes."""
    m = pd.read_csv(ROOT / "output/rdd_bolsa/matriz_municipio_escore_administrativo.csv", dtype={"co_ibge": str})
    m = m[m["quadro"] == "c1_ch1"].drop_duplicates("co_ibge")[["co_ibge", "faixa_anunciada"]]
    s = pd.read_csv(ROOT / arquivo, dtype={chave: str})[[chave, coluna_ivs]].rename(columns={chave: "co_ibge"})
    d = m.merge(s, on="co_ibge")
    c0, c1 = G.CORTES
    regra = d[coluna_ivs].map(lambda v: "FAIXA 3" if v <= c0 + 1e-9 else ("FAIXA 2" if v <= c1 + 1e-9 else "FAIXA 1"))
    return int((regra != d["faixa_anunciada"]).sum())


@unittest.skipUnless(TEM_SAIDAS, "saídas da banca 2 ausentes")
class TestNumerosContraFontes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.numeros = json.loads(NUMEROS.read_text(encoding="utf-8"))
        cls.manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))

    def test_naturezas_e_blocos_separados(self) -> None:
        self.assertEqual(self.numeros["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual({e["natureza"] for e in self.numeros["numeros"].values()}, {"EMPIRICO"})
        self.assertEqual({e["natureza"] for e in self.numeros["failure_mode"].values()}, {"FAILURE_MODE"})
        self.assertLessEqual({e["natureza"] for e in self.numeros["texto_citado"].values()},
                             {"TEXTO_NORMATIVO", "CITACAO_LITERATURA", "REGISTRO_DOCUMENTAL"})

    def test_cada_codigo_relido_da_fonte(self) -> None:
        calculados = {"lado_errado_oficial": _lado_errado("ivs", "output/aquisicao/a08_ivs_2010_oficial_municipio.csv",
                                                          "co_ibge"),
                      "descritivas": _descritivas_independentes()}
        for bloco in ("numeros", "failure_mode", "texto_citado"):
            brutos: dict = {}
            for cod, e in self.numeros[bloco].items():
                bruto = _resolver_independente(e["seletor"], brutos, calculados)
                brutos[cod] = bruto
                self.assertEqual(formatar(bruto, e["formato"]), e["valor"], cod)

    def test_regra_sem_excecao_com_ivs_oficial(self) -> None:
        self.assertEqual(self.numeros["numeros"]["R_LADO_ERRADO_OFICIAL"]["valor"], "0")
        self.assertEqual(self.numeros["numeros"]["R_C1_MUN"]["valor"], self.numeros["numeros"]["R_C1_REPR"]["valor"])
        self.assertEqual(self.numeros["numeros"]["R_C2_MUN"]["valor"], self.numeros["numeros"]["R_C2_REPR"]["valor"])

    def test_bloco_do_doc03_igual_ao_json(self) -> None:
        no_doc = blocos_do_doc03()
        todos = {c: e for b in ("numeros", "failure_mode", "texto_citado") for c, e in self.numeros[b].items()}
        self.assertEqual(set(no_doc), set(todos))
        for c, e in todos.items():
            self.assertEqual(no_doc[c], e["valor"], c)
        texto = DOC03.read_text(encoding="utf-8")
        ini, fim = texto.index(G.MARCA_INI) + len(G.MARCA_INI), texto.index(G.MARCA_FIM)
        self.assertEqual(texto[ini:fim].strip(), G.bloco_doc(self.numeros).strip())

    def test_manifesto_com_hashes_atuais(self) -> None:
        self.assertEqual(self.manifesto["natureza_dos_dados"], "EMPIRICO")
        for e in self.manifesto["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], f"entrada mudou: {e['caminho']}")
            for campo in ("papel", "data_referencia", "cobertura", "unidade", "chaves"):
                self.assertIn(campo, e)
        self.assertEqual(sha256(NUMEROS), self.manifesto["numeros"]["sha256"])
        for f in self.manifesto["figuras"]:
            self.assertEqual(sha256(ROOT / f["arquivo"]), f["sha256"], f["arquivo"])

    def test_figuras_da_cadeia_batem_com_a_tabela(self) -> None:
        tab = pd.read_csv(ROOT / "output/rdd_bolsa/E8_tabela_sintese.csv", dtype=str, keep_default_na=False)
        self.assertEqual(len(self.manifesto["cadeia_sintese_completa"]), len(tab))
        for r in self.manifesto["cadeia_sintese_completa"]:
            linha = tab[(tab["outcome"] == r["outcome"]) & (tab["populacao"] == r["populacao"])
                        & (tab["ciclo"] == r["ciclo"])]
            self.assertEqual(len(linha), 1)
            est = float(linha["estimativa"].iloc[0])
            self.assertIn(formatar(est, "d2" if linha["unidade"].iloc[0] == "razão de chances" else
                                   ("pp1s" if linha["unidade"].iloc[0].startswith("fracao") else
                                    "d2s" if linha["unidade"].iloc[0].startswith("desvios") else
                                    "d1s" if linha["unidade"].iloc[0].startswith("horas") else "d3s")),
                          r["texto"])

    def test_descarte_bate_com_o_resumo(self) -> None:
        res = json.loads((ROOT / "output/rdd_bolsa/E8_resumo.json").read_text(encoding="utf-8"))
        ref = res["descarte"]["referencias"]["preenchimento_pp"]
        linhas = res["descarte"]["ancora_E3_ciclo1"] + res["descarte"]["preenchimento"]
        reg = self.manifesto["descarte_preenchimento"]
        self.assertEqual(len(reg), len(linhas))
        for r in linhas:
            txt = f"{formatar(r['tau'], 'pp1s')} [{formatar(r['ic95_inf'], 'pp1s')}; {formatar(r['ic95_sup'], 'pp1s')}]"
            achado = [x for x in reg if x["texto"] == txt]
            self.assertEqual(len(achado), 1, txt)
            self.assertEqual(achado[0]["descarta_referencia"], r["ic95_sup"] < ref)
        self.assertTrue(all(not r["ic_honesto_exclui_referencia"] for r in res["descarte"]["preenchimento"]))


# --------------------------------------------------------------------------
# 3. Slides e outros documentos
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS and DOC02.exists(), "saídas ou doc 02 ausentes")
class TestSlides(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.numeros = json.loads(NUMEROS.read_text(encoding="utf-8"))
        cls.todos = {c: e for b in ("numeros", "failure_mode", "texto_citado") for c, e in cls.numeros[b].items()}
        cls.slides = slides()

    def test_contagem(self) -> None:
        t = DOC02.read_text(encoding="utf-8")
        deck = t[t.index("<!-- deck:inicio -->"):t.index("<!-- deck:fim -->")]
        self.assertEqual(len(re.findall(r"(?m)^## ", deck)), 18)
        apend = t[t.index("<!-- apendice:inicio -->"):t.index("<!-- apendice:fim -->")]
        self.assertEqual(len(re.findall(r"(?m)^## ", apend)), 11)
        self.assertTrue(all(h.startswith("## Apêndice:") for h in re.findall(r"(?m)^## .*$", apend)))

    def test_secoes_na_ordem_da_banca(self) -> None:
        t = DOC02.read_text(encoding="utf-8")
        deck = t[t.index("<!-- deck:inicio -->"):t.index("<!-- deck:fim -->")]
        self.assertEqual(re.findall(r"(?m)^# (.+)$", deck), ["Prévios do grupo", "Hipótese", "Base de Dados", "Metodologia",
                                                             "Resultados", "Robustez e discussão"])
        # a regra sharp é evidência de identificação: fica na Metodologia
        met = deck[deck.index("# Metodologia"):deck.index("# Resultados")]
        self.assertIn("## A bolsa é função exata do IVS: a regra é sharp", met)

    def test_h1_por_corte_sem_empilhado_no_corpo(self) -> None:
        """Decisão do autor (26/10/2026): na H1, só os cortes separados no corpo; o empilhado, no apêndice, rotulado."""
        t = DOC02.read_text(encoding="utf-8")
        corpo = t[t.index("<!-- deck:inicio -->"):t.index("<!-- deck:fim -->")]
        for cod in ("A3_EMP_", "N1_SA_", "N1_SB_", "N1_MEDIA", "N1_H030", "N1_H080", "N1_DONUT_", "N1_UNICO_", "N1_HON_"):
            self.assertNotIn(f"`{cod}", corpo, cod)
        self.assertNotIn("cortes empilhados", corpo)
        for s in self.slides:
            if s["titulo"].startswith(("## Apêndice: N1 a N4", "## Apêndice: A3")):
                for linha in s["texto"].splitlines():
                    if linha.startswith("|") and "empilhado" in linha:
                        self.assertIn("só referência", linha)
        h1 = next(s for s in self.slides if s["titulo"].startswith("## H1"))
        for c in ("EQ_A3_300_I90I", "EQ_N1_300_I90I", "ND_TX300", "ND_VIC400", "N1_300_HON_INF"):
            self.assertIn(c, h1["codigos"])
        man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        linhas = [ln["linha"] for ln in man["figuras_novas"]["h1_preenchimento.png"]["linhas"]]
        self.assertTrue(linhas and all(("0,300" in x or "0,400" in x) for x in linhas), linhas)
        cad = [ln["linha"] for ln in man["figuras_novas"]["cadeia_resumo_doc57.png"]["linhas"]]
        self.assertFalse(any(("(A3)" in x or "(N1)" in x) and "0,300" not in x and "0,400" not in x for x in cad))

    def test_especificacoes_por_estimador(self) -> None:
        """Pedido do autor (26/10/2026): cada estimador tem a sua especificação explicada na metodologia."""
        campos = {"Outcome", "Amostra", "Equação em palavras", "Erro-padrão", "Leitura", "Cuidado", "Sensibilidades"}
        fichas = [s for s in self.slides if s["titulo"].startswith("## Especificação")]
        self.assertEqual(len(fichas), 4)
        for f in fichas:
            linhas = [ln.split("|")[1].strip() for ln in f["texto"].splitlines() if ln.startswith("| ") and "---" not in ln]
            achados = " ".join(linhas)
            for c in ("Equação em palavras", "Erro-padrão" if "TOST" not in f["titulo"] else "Testes", "Leitura",
                      "Cuidado" if "H4" not in f["titulo"] else "Pré", "Sensibilidades"):
                self.assertIn(c, achados, (f["titulo"], c))
        self.assertIn("## Apêndice: especificações formais de cada estimador", DOC02.read_text(encoding="utf-8"))
        self.assertIn('<!-- reservado: slide "Por que o preenchimento cai em 0,300"', DOC02.read_text(encoding="utf-8"))

    def test_h2_por_ciclo_e_h3_explica_causalidade(self) -> None:
        h2 = next(s for s in self.slides if s["titulo"].startswith("## H2"))
        corpo = h2["texto"].split("> **Notas do apresentador.**")[0]
        num = json.loads(NUMEROS.read_text(encoding="utf-8"))["numeros"]
        self.assertNotIn(num["M1_RC"]["valor"] + " [", corpo)
        self.assertNotIn(num["E9_C2_RC"]["valor"] + " [", corpo)
        man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        self.assertEqual([ln["codigos"][0] for ln in man["figuras_novas"]["h2_escolha.png"]["linhas"]],
                         ["M5_C1_RC", "M5_C2_RC", "M5_C3_RC"])
        h3 = next(s for s in self.slides if s["titulo"].startswith("## H3"))
        self.assertIn("**Como foi medido.**", h3["texto"])
        self.assertIn("**É causal?**", h3["texto"])

    def test_cronologia_dos_ciclos(self) -> None:
        s = next(x for x in self.slides if x["titulo"].startswith("## O PMM-E já teve três chamamentos"))
        linhas = [[c.strip() for c in re.split(r"(?<!\\)\|", ln)[1:-1]] for ln in s["texto"].splitlines()
                  if ln.startswith("|") and not re.fullmatch(r"[|\-: ]+", ln)]
        d = pd.read_csv(SAIDA / "cronologia_ciclos.csv", dtype=str, keep_default_na=False).drop(columns="natureza_dos_dados")
        self.assertEqual(linhas, [list(d.columns)] + d.values.tolist())

    def test_controle_por_corte_identidade_exata(self) -> None:
        """Slide de antes e depois do controle: total = via oferta + com controle, em cada corte, lido do registro."""
        num = json.loads(NUMEROS.read_text(encoding="utf-8"))["numeros"]
        for c in ("300", "400"):
            tot, via, sa = (float(num[f"N1_{c}_{k}"]["valor_bruto"]) for k in ("DTOT", "VIA", "DSA"))
            self.assertAlmostEqual(tot, via + sa, places=9)
            self.assertAlmostEqual(sa, float(num[f"N1_{c}_TAU"]["valor_bruto"]), places=9)
        s = next(x for x in self.slides if x["titulo"].startswith("## O controle muda a leitura"))
        t = DOC02.read_text(encoding="utf-8")
        self.assertLess(t.index(s["titulo"]), t.index('<!-- reservado: slide "Por que o preenchimento cai em 0,300"'))
        self.assertGreater(t.index(s["titulo"]), t.index("## H1:"))

    def test_corpo_sintetizado(self) -> None:
        """Na parte empírica (antes do apêndice): no máximo 3 marcadores (por coluna) e uma frase de cautela."""
        for sl in _D.ler_slides():
            if sl["apendice"]:
                continue
            grupos = [c["itens"] for c in sl["colunas"]] or [sl["marcadores"]]
            for itens in grupos:
                self.assertLessEqual(len(itens), 3, sl["titulo"])
            self.assertTrue(sl["cautela"], sl["titulo"])
        disc = [sl for sl in _D.ler_slides() if sl["titulo"].startswith("Discussão")]
        self.assertEqual(len(disc), 1)
        self.assertEqual(len(disc[0]["colunas"]), 2)

    def test_ordem_e_classificacao_do_doc02(self) -> None:
        """Marcadores de slide do grupo, tabela de classificação e mapa do deck dizem a mesma coisa."""
        classif = _D.ler_classificacao()
        self.assertEqual(sorted(classif), list(range(1, 37)))
        removidos = {n for n, c in classif.items() if c["destino"] == "removido"}
        self.assertEqual(removidos, {25, 27, 29, 32, 33})  # marcadores "X" e EXEMPLO de outro trabalho
        ordem = _D.ler_ordem()
        grupo = [n for t, n, *_ in ordem if t == "grupo"]
        self.assertEqual(sorted(grupo), sorted(set(range(1, 37)) - removidos))
        self.assertEqual(grupo[:23], list(range(1, 24)))  # prévios do grupo na ordem do grupo
        for k, item in enumerate(ordem, 1):
            if item[0] == "grupo":
                self.assertEqual(classif[item[1]]["posicao"], k, item)

    def test_titulo_curto_e_cautela_em_todo_slide(self) -> None:
        for s in self.slides:
            self.assertLessEqual(len(s["titulo"][3:]), 62, s["titulo"])
            self.assertRegex(s["texto"], r"(?m)^> \*\*(?!Notas do apresentador)", f"sem frase de cautela: {s['titulo']}")

    def test_figura_com_caminho_exato_nos_resultados(self) -> None:
        com_figura = [s["titulo"] for s in self.slides if re.search(r"!\[[^\]]*\]\(", s["texto"])]
        for chave in ("regra é sharp", "H1:", "H2:", "H4:", "Na cadeia"):
            self.assertTrue(any(chave in t for t in com_figura), chave)

    def test_h3_com_o_p1h_auditado(self) -> None:
        """A H3 sai do P1h auditado: título fiel à leitura pré-registrada, figura do P1h e cautelas obrigatórias."""
        h3 = next(s for s in self.slides if s["titulo"].startswith("## H3"))
        self.assertNotIn("PENDENTE", h3["texto"])
        self.assertIn("no modelo de escolha", h3["titulo"])
        self.assertIn("output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png", h3["texto"])
        for c in ("H3_DUF", "H3_DUF_INF", "H3_DUF_SUP", "H3_DUF_P", "H3_K10", "H3_K10_INF", "H3_K10_SUP",
                  *[f"H3_S_{k}" for k, *_ in G.SENS_H3]):
            self.assertIn(c, h3["codigos"])
            self.assertTrue(self.todos[c]["arquivo"].startswith("output/rdd_bolsa/P1h_"), c)
        corrido = " ".join(re.sub(r"(?m)^>\s?", "", h3["texto"]).split())
        for frase in ("preferência revelada condicional ao modelo", "não efeito da geografia", "pacote do corte",
                      "Escolha de quem se candidatou, entre vagas abertas", "mesma UF, outra região de saúde",
                      "o IC contém zero", "não traz mais candidatos"):
            self.assertIn(frase, corrido, frase)
        # o limite unilateral do km só aparece ao lado do teste bilateral do P1a, que não rejeita
        k5p, m1p = self.todos["H3_K5_P"]["valor"], self.todos["M1_P"]["valor"]
        self.assertIn(f"p de {k5p} do km: é unilateral e descritivo", corrido)
        self.assertIn(f"bilateral do P1a, com p {m1p}, que não rejeita", corrido)
        self.assertGreaterEqual(float(self.todos["M1_P"]["valor_bruto"]), 0.05)

    def test_tabelas_do_doc_iguais_aos_csv(self) -> None:
        for titulo, csv in (("oito bases oficiais", "tabela_fontes.csv"), ("Os três ciclos", "tabela_descritiva_ciclos.csv")):
            s = next(x for x in self.slides if titulo in x["titulo"])
            linhas = [[c.strip() for c in re.split(r"(?<!\\)\|", ln)[1:-1]] for ln in s["texto"].splitlines()
                      if ln.startswith("|") and not re.fullmatch(r"[|\-: ]+", ln)]
            d = pd.read_csv(SAIDA / csv, dtype=str, keep_default_na=False).drop(columns="natureza_dos_dados")
            self.assertEqual(linhas, [list(d.columns)] + d.values.tolist(), csv)

    def test_todo_slide_tem_linha_de_numeros(self) -> None:
        for s in self.slides:
            self.assertIsNotNone(s["codigos"], f"slide sem linha **Números:** — {s['titulo']}")

    def test_codigos_existem_e_aparecem(self) -> None:
        for s in self.slides:
            sem_linha = re.sub(r"(?m)^\*\*Números:\*\*.*?(?=\n\n|\Z)", "", s["texto"], flags=re.S)
            for c in s["codigos"]:
                self.assertIn(c, self.todos, f"código desconhecido {c} em {s['titulo']}")
                self.assertIn(self.todos[c]["valor"], sem_linha, f"{c} listado e ausente em {s['titulo']}")

    def test_todo_numero_do_slide_e_registrado_ou_parametro(self) -> None:
        sobra = {}
        for s in self.slides:
            permitidos = set(PERMITIDOS)
            for c in s["codigos"]:
                permitidos |= tokens(self.todos[c]["valor"])
            achados = {x for x in tokens(limpar(s["texto"])) if not ano(x)}
            if achados - permitidos:
                sobra[s["titulo"]] = sorted(achados - permitidos)
        self.assertEqual(sobra, {}, "números sem código, por slide")

    def test_preambulo_so_tem_parametros(self) -> None:
        t = DOC02.read_text(encoding="utf-8")
        pre = t[:t.index("<!-- deck:inicio -->")]
        achados = {x for x in tokens(limpar(pre)) if not ano(x)}
        livres = {x for x in achados if x.isdigit() and int(x) <= MAX_SLIDE}  # números de slide no mapa
        self.assertEqual(achados - livres - PERMITIDOS - todos_valores(self.numeros), set())

    def test_frases_e_distincoes_obrigatorias(self) -> None:
        corrido = " ".join(re.sub(r"(?m)^>\s?", "", DOC02.read_text(encoding="utf-8")).split())
        for frase in (
            "IC que contém zero não é efeito zero",
            "é ausência de efeito detectável",
            "Inconclusivo não quer dizer que a bolsa não funciona",
            "Não é a participação no PMM-E",
            "nem o Agora Tem Especialistas",
            "Associação sob tendências paralelas",
            "Escolha não é expansão",
            "Vínculo não é presença",
            "pacote do corte",
            "Sem margem extensiva",
            "θ é preferência revelada condicional ao modelo, não efeito da geografia",
            "(estabelecimento × curso) com alguma confirmação ou homologação",
            "SGTES",
        ):
            self.assertIn(frase, corrido)


@unittest.skipUnless(TEM_SAIDAS, "saídas da banca 2 ausentes")
class TestOutrosDocs(unittest.TestCase):
    def test_readme_roteiro_e_doc03_sem_numero_solto(self) -> None:
        numeros = json.loads(NUMEROS.read_text(encoding="utf-8"))
        validos = PERMITIDOS | todos_valores(numeros)
        for doc in (README, DOC01, DOC03):
            t = doc.read_text(encoding="utf-8")
            if doc == DOC03:
                t = t[:t.index(G.MARCA_INI)] + t[t.index(G.MARCA_FIM):]
            achados = {x for x in tokens(limpar(t)) if not ano(x)}
            livres = {x for x in achados if x.lstrip("+").isdigit() and int(x.lstrip("+")) <= MAX_SLIDE}
            self.assertEqual(achados - livres - validos, set(), doc.name)

    def test_readme_declara_estado_e_decisoes(self) -> None:
        t = README.read_text(encoding="utf-8")
        self.assertNotIn("PENDENTE", t)
        self.assertIn("auditoria 31", t)
        self.assertIn("57_sintese_perguntas_reformuladas.md", t)
        self.assertIn("04_plano_entrega_empirica.md", t)
        self.assertIn("metodologia **econométrica**", t)
        # organização do deck: escopo do autor registrado; EXEMPLO de outro trabalho fora do deck
        self.assertIn("reutilizar tudo o que der", t)
        self.assertIn("EXEMPLO", t)
        self.assertIn("modelo de outro trabalho", DOC02.read_text(encoding="utf-8"))

    def test_indice_da_secao(self) -> None:
        t = (ROOT / "docs" / "07_apresentacoes" / "README.md").read_text(encoding="utf-8")
        self.assertIn("(banca2/)", t)

    def test_registro_de_mudancas(self) -> None:
        t = (ROOT / "docs" / "00_registro_mudancas.md").read_text(encoding="utf-8")
        self.assertIn("07_apresentacoes/banca2/", t)


# --------------------------------------------------------------------------
# 4. Figuras e integridade
# --------------------------------------------------------------------------

RESUMO_DA_ETAPA = {"E6_figuras": "output/rdd_bolsa/E6_resumo.json",
                   "E7_figuras": "output/rdd_bolsa/E7_resumo.json",
                   "E9_figuras": "output/rdd_bolsa/E9_resumo.json",
                   "P1h_figuras": "output/rdd_bolsa/P1h_resumo.json"}
SCRIPT_DA_ETAPA = {"E6_figuras": "scripts/rdd_bolsa/13_estimar_E6_funil.py",
                   "E7_figuras": "scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py",
                   "E9_figuras": "scripts/rdd_bolsa/16_estimar_E9_escolha.py",
                   "P1h_figuras": "scripts/rdd_bolsa/25c_magnitudes_P1h.py"}


@unittest.skipUnless(TEM_SAIDAS, "saídas da banca 2 ausentes")
class TestFiguras(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        cls.do_manifesto = {f["arquivo"]: f for f in cls.manifesto["figuras"]}
        cls.citadas = set()
        for doc in (DOC02, DOC03, README):
            cls.citadas |= set(re.findall(r"output/[\w/.\-]+\.(?:png|svg)", doc.read_text(encoding="utf-8")))

    def test_ha_figuras_citadas(self) -> None:
        self.assertGreaterEqual(len(self.citadas), 10)

    def test_toda_figura_existe_e_vem_do_pipeline(self) -> None:
        for f in self.citadas:
            p = ROOT / f
            self.assertTrue(p.exists(), f)
            if f.startswith("output/apresentacao_banca2/"):
                self.assertIn(f, self.do_manifesto, f)
                self.assertEqual(sha256(p), self.do_manifesto[f]["sha256"], f)
                continue
            pasta = Path(f).parent.name
            self.assertIn(pasta, RESUMO_DA_ETAPA, f"figura fora do pipeline conhecido: {f}")
            resumo = json.loads((ROOT / RESUMO_DA_ETAPA[pasta]).read_text(encoding="utf-8"))
            self.assertIn(f, json.dumps(resumo, ensure_ascii=False), f"{f} não listada em {RESUMO_DA_ETAPA[pasta]}")
            self.assertEqual(resumo.get("natureza_dos_dados"), "EMPIRICO")
            script = (ROOT / SCRIPT_DA_ETAPA[pasta]).read_text(encoding="utf-8")
            self.assertIn(pasta, script)
            saidas = resumo.get("saidas")
            if isinstance(saidas, dict) and re.fullmatch(r"[0-9a-f]{64}", str(saidas.get(f, ""))):
                self.assertEqual(sha256(p), saidas[f], f)

    def test_slides_citam_figuras_por_caminho_exato(self) -> None:
        for s in slides():
            for img in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", s["texto"]):
                self.assertTrue((DOC02.parent / img).resolve().exists(), img)
                self.assertIn("/output/", (DOC02.parent / img).resolve().as_posix())


@unittest.skipUnless(TEM_SAIDAS, "saídas da banca 2 ausentes")
class TestIntegridade(unittest.TestCase):
    def test_arquivo_errado_nao_e_lido(self) -> None:
        man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        for f in man["figuras"]:
            self.assertNotIn(ARQUIVO_ERRADO, f["fontes"], f["arquivo"])
            self.assertEqual(f["natureza"] == "FAILURE_MODE", "/failure_mode/" in f["arquivo"], f["arquivo"])
        self.assertFalse(any(e["caminho"].startswith("data/") for e in man["entradas"]))
        for script in (SCRIPT, SCRIPT_DECK):
            self.assertNotIn("ivs_ipea_2010_municipios", script.read_text(encoding="utf-8"), script.name)

    def test_nada_gravado_em_data(self) -> None:
        man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        for f in man["figuras"]:
            self.assertTrue(f["arquivo"].startswith("output/apresentacao_banca2/"))
        for script in (SCRIPT, SCRIPT_DECK):
            self.assertNotIn('"data/', script.read_text(encoding="utf-8"), script.name)

    def test_h3_lida_do_p1h_auditado(self) -> None:
        """A H3 é lida das saídas do P1h, sem recálculo: nenhum código H3_ vem de outro arquivo, a figura e o CSV têm o
        hash gravado no resumo do P1h, e o gerador não importa nem roda o script 25c."""
        numeros = json.loads(NUMEROS.read_text(encoding="utf-8"))["numeros"]
        h3 = {c: e for c, e in numeros.items() if c.startswith("H3_")}
        self.assertGreaterEqual(len(h3), 20)
        for c, e in h3.items():
            self.assertIn(e["arquivo"], ("output/rdd_bolsa/P1h_magnitudes.csv", "output/rdd_bolsa/P1h_resumo.json"), c)
        res = json.loads((ROOT / "output/rdd_bolsa/P1h_resumo.json").read_text(encoding="utf-8"))
        self.assertEqual(res["natureza_dos_dados"], "EMPIRICO")
        for rel in ("output/rdd_bolsa/P1h_magnitudes.csv", "output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png"):
            self.assertEqual(sha256(ROOT / rel), res["saidas"][rel], rel)
        texto = SCRIPT.read_text(encoding="utf-8") + SCRIPT_DECK.read_text(encoding="utf-8")
        self.assertNotIn("25c_", texto)

    def test_h3_numeros_do_slide(self) -> None:
        """Releitura independente do CSV do P1h: D_UF, IC do km com zero, sensibilidades todas positivas e com q < 0,05,
        e a faixa da robustez vai do menor ao maior D_UF das sensibilidades."""
        d = pd.read_csv(ROOT / "output/rdd_bolsa/P1h_magnitudes.csv", dtype=str, keep_default_na=False)
        num = json.loads(NUMEROS.read_text(encoding="utf-8"))["numeros"]
        p1 = d[d["id_linha"] == "P1h-1"].iloc[0]
        self.assertEqual(num["H3_DUF"]["valor"], formatar(float(p1["estimativa"]), "d2"))
        self.assertEqual(p1["rejeita_h0_5pct"], "True")
        self.assertLess(float(p1["p_holm"]), 0.05)
        k10 = d[d["id_linha"] == "P1h-2b"].iloc[0]
        self.assertLess(float(k10["ic95_inf"]), 0.0)
        self.assertGreater(float(k10["ic95_sup"]), 0.0)
        sens = d[d["id_linha"] == "P1h-3"]
        self.assertEqual(len(sens), len(G.SENS_H3))
        self.assertTrue((sens["estimativa"].astype(float) > 0).all())
        self.assertTrue((sens["q_bky"].astype(float) < 0.05).all())
        est = {(r["modelo"], r["ciclo"]): float(r["estimativa"]) for _, r in sens.iterrows()}
        self.assertEqual(min(est, key=est.get), ("M2", "empilhado"))
        self.assertEqual(max(est, key=est.get), ("M5", "3"))
        rob = next(s for s in slides() if s["titulo"].startswith("## Apêndice: robustez"))
        self.assertIn(f"de {num['H3_S_M2']['valor']} a {num['H3_S_M5C3']['valor']}", rob["texto"])

    def test_regra_desenhada_pela_funcao_do_relatorio(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("var_pontos_cor", texto)
        galeria = (ROOT / "scripts/rdd_bolsa/10_galeria_figura_regra.py").read_text(encoding="utf-8")
        self.assertIn("R.fig_regra_pontos", galeria)


# --------------------------------------------------------------------------
# 5. Figuras novas e deck
# --------------------------------------------------------------------------

@unittest.skipUnless(TEM_SAIDAS, "saídas da banca 2 ausentes")
class TestFigurasNovas(unittest.TestCase):
    """Todo número desenhado nas figuras novas é o valor de um código do registro ou um parâmetro."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.manifesto = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        cls.numeros = json.loads(NUMEROS.read_text(encoding="utf-8"))

    def test_figuras_novas_registradas(self) -> None:
        novas = self.manifesto["figuras_novas"]
        for nome in ("h1_preenchimento.png", "h1_controle.png", "h2_escolha.png", "h4_horas_medico.png",
                     "cadeia_resumo_doc57.png",
                     "tabela_descritiva_ciclos.png", "tabela_fontes.png"):
            self.assertIn(nome, novas)
            self.assertIn(f"output/apresentacao_banca2/{nome}", {f["arquivo"] for f in self.manifesto["figuras"]})

    def test_como_ler_nas_figuras_de_hipotese(self) -> None:
        for nome in ("h1_preenchimento.png", "h2_escolha.png", "h4_horas_medico.png"):
            self.assertIn("Como ler", self.manifesto["figuras_novas"][nome]["textos"], nome)

    def test_numeros_desenhados_sao_registrados(self) -> None:
        validos = PERMITIDOS | todos_valores(self.numeros)
        for nome, reg in self.manifesto["figuras_novas"].items():
            achados = set()
            for t in reg["textos"]:
                achados |= {x for x in tokens(limpar(t)) if not ano(x)}
            self.assertEqual(achados - validos, set(), nome)

    def test_forca_da_evidencia_por_regra(self) -> None:
        """Recalcula a categoria de cada linha da cadeia pela regra declarada, com os valores do registro."""
        todos = {c: e for b in ("numeros", "failure_mode", "texto_citado") for c, e in self.numeros[b].items()}
        linhas = self.manifesto["figuras_novas"]["cadeia_resumo_doc57.png"]["linhas"]
        self.assertEqual(len(linhas), len(G.LINHAS_CADEIA_57))
        for ln, defin in zip(linhas, G.LINHAS_CADEIA_57):
            tipo, cod = defin[-1][:2]
            nulo = defin[6]
            if tipo == "holm":
                pos = len(defin[-1]) == 3 and str(todos[defin[-1][2]]["valor_bruto"]).endswith("POS_RESULTADO")
                esperado = ("inconclusivo" if float(todos[cod]["valor_bruto"]) >= 0.05
                            else "rejeita zero, pós-resultado" if pos else "rejeita zero (Holm)")
            elif tipo == "ic":
                inf, sup = (float(todos[c]["valor_bruto"]) for c in ln["codigos"][1:])
                esperado = "inconclusivo" if inf <= nulo <= sup else "IC exclui o nulo"
            elif tipo == "tost":
                esperado = {"SO_AUMENTO": "sem aumento ≥ margem", "SO_QUEDA": "sem queda ≥ margem",
                            "EQUIVALENTE": "equivalente na margem",
                            "INCONCLUSIVO": "inconclusivo"}[str(todos[cod]["valor_bruto"])]
            elif tipo == "pre":
                p = float(todos[cod]["valor_bruto"])
                esperado = "ATT sob tendências paralelas" if p >= 0.05 else "ATT com pré falhando"
            else:
                self.assertTrue(str(todos[cod]["valor_bruto"]).startswith("EXPLORATORIO"))
                esperado = "exploratório"
            self.assertEqual(ln["forca"], esperado, ln["linha"])
            self.assertIn(ln["forca"], self.manifesto["figuras_novas"]["cadeia_resumo_doc57.png"]["textos"])

    def test_universos_de_candidatos_encaixados(self) -> None:
        n = {c: float(e["valor_bruto"]) for c, e in self.numeros["numeros"].items()
             if c.startswith("D_C") or c == "M1_N"}
        for c in (1, 2, 3):
            self.assertLessEqual(n[f"D_C{c}_LIG"], n[f"D_C{c}_CANDG1"])
            self.assertLessEqual(n[f"D_C{c}_CAND1"], n[f"D_C{c}_CANDG1"])
            self.assertLessEqual(n[f"D_C{c}_P1"], min(n[f"D_C{c}_LIG"], n[f"D_C{c}_CAND1"]))
        self.assertEqual(sum(n[f"D_C{c}_P1"] for c in (1, 2, 3)), n["M1_N"])

    def test_linhas_das_figuras_batem_com_o_registro(self) -> None:
        todos = {c: e for b in ("numeros", "failure_mode", "texto_citado") for c, e in self.numeros[b].items()}
        for nome, reg in self.manifesto["figuras_novas"].items():
            for ln in reg.get("linhas", []):
                est, inf, sup = (todos[c]["valor"] for c in ln["codigos"])
                self.assertIn(f"{est}", ln["texto"], nome)
                self.assertIn(f"[{inf}; {sup}]", ln["texto"], nome)
                bruto = [float(todos[c]["valor_bruto"]) for c in ln["codigos"]]
                nulo = 1.0 if ("razão" in ln.get("painel", "").lower() or ln["linha"].startswith("Peso da bolsa")) else 0.0
                self.assertEqual(ln["exclui_nulo"], bruto[1] > nulo or bruto[2] < nulo, (nome, ln["linha"]))


def _texto_slides(pptx: Path) -> list[tuple[str, str, str]]:
    """(parte, título, texto) de cada slide, na ordem da apresentação; o texto junta os parágrafos."""
    with zipfile.ZipFile(pptx) as z:
        pres = z.read("ppt/presentation.xml").decode("utf-8")
        rels = z.read("ppt/_rels/presentation.xml.rels").decode("utf-8")
        alvo = dict(re.findall(r'<Relationship Id="(rId\d+)"[^>]*Target="([^"]*)"', rels))
        out = []
        for rid in re.findall(r'<p:sldId id="\d+" r:id="(rId\d+)"/>', pres):
            parte = "ppt/" + alvo[rid]
            xml = z.read(parte).decode("utf-8")
            m = re.search(r'<p:ph type="title"[^>]*/>.*?</p:sp>', xml, flags=re.S)
            titulo = "".join(re.findall(r"<a:t>([^<]*)</a:t>", m.group(0))) if m else ""
            paras = ["".join(re.findall(r"<a:t>([^<]*)</a:t>", p)) for p in re.findall(r"<a:p>(.*?)</a:p>", xml, flags=re.S)]
            texto = "\n".join(p for p in paras if p.strip())
            out.append((parte, unescape(titulo), unescape(texto)))
    return out


@unittest.skipUnless(TEM_SAIDAS and TEM_DECK, "deck da banca 2 ausente")
class TestDeck(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.numeros = json.loads(NUMEROS.read_text(encoding="utf-8"))
        cls.manifesto = json.loads(MANIF_DECK.read_text(encoding="utf-8"))
        cls.deck_ = _texto_slides(DECK)
        pos_novos = [o["posicao"] for o in cls.manifesto["ordem_do_deck_proposto"] if o["origem"] == "novo"]
        cls.novos = [cls.deck_[k - 1] for k in pos_novos]
        cls.deck = _texto_slides(DECK)
        cls.doc = slides()

    def test_slides_novos_com_titulos_do_doc02(self) -> None:
        self.assertEqual([t for _, t, _ in self.novos], [s["titulo"][3:].strip() for s in self.doc])

    def test_texto_do_doc_no_deck(self) -> None:
        import importlib
        D = importlib.import_module("gerar_deck_banca2")
        for sl, (_, titulo, texto) in zip(D.ler_slides(), self.novos):
            corrido = " ".join(texto.replace("\u00a0", " ").replace(".", "").split())
            for item in sl["marcadores"] + [x for x in (sl["cautela"], sl["explica"]) if x]:
                self.assertIn(" ".join(D.texto_puro(item).replace("**", "").replace(".", "").split()), corrido, titulo)
            for linha in sl["tabela"]:
                for cel in linha:
                    self.assertIn(" ".join(D.texto_puro(cel).replace(".", "").split()), corrido, titulo)

    def test_numeros_do_deck_sao_registrados(self) -> None:
        validos = PERMITIDOS | todos_valores(self.numeros)
        for _, titulo, texto in self.novos:
            achados = {x for x in tokens(limpar(texto.replace("\u00a0", " "))) if not ano(x)}
            self.assertEqual(achados - validos, set(), titulo)

    def test_h3_no_deck(self) -> None:
        h3 = next(t for _, ti, t in self.novos if ti.startswith("H3"))
        self.assertNotIn("PENDENTE", h3)
        v = self.numeros["numeros"]
        self.assertIn(f"{v['H3_DUF']['valor']} [{v['H3_DUF_INF']['valor']}; {v['H3_DUF_SUP']['valor']}]",
                      h3.replace("\u00a0", " "))
        fig = [e for e in self.manifesto["ordem_do_deck_proposto"] if e.get("titulo", "").startswith("H3")]
        self.assertEqual([e["figura"] for e in fig], ["output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png"])

    def test_deck_proposto_ordem_e_correcoes(self) -> None:
        titulos = [t for _, t, _ in self.deck]
        self.assertEqual(len(self.deck), 36 - 5 + len(self.doc))
        self.assertNotIn("X", titulos)
        tudo = "\n".join(t for _, _, t in self.deck)
        for proibido in ("SGETS", "177 dos 368", "O IVS é o piso", "indícios de efetividade", "renumeração",
                         "Vulnerabilidade: Muito alta", "x Especialidade"):
            self.assertNotIn(proibido, tudo, proibido)
        v = {c: e["valor"] for c, e in self.numeros["numeros"].items()}
        alvo = f"{v['D_C1_PRE1_PCT']}% na 1ª chamada · {v['D_C1_PRE2_PCT']}% somando a 2ª"
        self.assertEqual(sum(alvo in t for _, _, t in self.deck), 2)
        self.assertEqual(sum(t == "O IVS 2010 define a bolsa do PMM-E por regra" for t in titulos), 4)
        self.assertIn(f"{v['R_C1_REPR']} de {v['R_C1_MUN']} municípios do ciclo 1", tudo.replace("\u00a0", " "))
        # os slides novos entram depois do slide de hipótese; o apêndice vem depois do divisor
        i = titulos.index("Da condição de aceitação, sai nossa hipótese econômica")
        self.assertEqual(i, 22)
        self.assertEqual(titulos[i + 1], self.doc[0]["titulo"][3:].strip())
        divisor = next(k for k, (_, ti, tx) in enumerate(self.deck) if not ti and "Apêndice" in tx)
        self.assertLess(divisor, titulos.index(next(s["titulo"][3:].strip() for s in self.doc
                                                    if s["titulo"].startswith("## Apêndice"))))
        self.assertTrue(all(t.startswith("Apêndice:") for t in titulos[divisor + 1:]))

    def test_mapa_do_doc02_igual_ao_deck(self) -> None:
        t = DOC02.read_text(encoding="utf-8")
        sec = t[t.index("## Mapa do deck proposto"):t.index("## Classificação dos slides do deck do grupo")]
        mapa = [[c.strip() for c in ln.split("|")[1:3]] for ln in sec.splitlines()
                if re.match(r"\| \d+ \|", ln)]
        manif = [[str(o["posicao"]), "novo" if o["origem"] == "novo" else f"grupo {o['origem'].split()[1]}"]
                 for o in self.manifesto["ordem_do_deck_proposto"]]
        self.assertEqual(mapa, manif)
        self.assertEqual(len(manif), len(self.deck))

    def test_um_arquivo_so(self) -> None:
        self.assertEqual(DECK.name, "deck_banca2.pptx")
        for velho in ("deck_banca2_proposta.pptx", "slides_empiricos_banca2.pptx"):
            self.assertFalse((SAIDA / velho).exists(), velho)
        self.assertEqual([e["caminho"] for e in self.manifesto["saidas"]], ["output/apresentacao_banca2/deck_banca2.pptx"])

    def test_resultados_abrem_pela_cadeia(self) -> None:
        titulos = [t for _, t, _ in self.novos if not t.startswith("O controle muda")]
        i = titulos.index("Na cadeia, só a escolha e o registro do médico se movem")
        self.assertEqual([t[:3] for t in titulos[i + 1:i + 5]], ["H1:", "H2:", "H3:", "H4:"])
        self.assertTrue(titulos[i + 5].startswith("Robustez"))

    def test_letra_minima_e_explica_no_corpo(self) -> None:
        """Nos slides novos do corpo: nada abaixo de 12 pt, salvo a linha de fontes; tabelas com 14 pt ou mais; o
        bloco "O que isso quer dizer" nos slides de hipótese, metodologia, resultados e robustez."""
        doc = {sl["titulo"]: sl for sl in _D.ler_slides()}
        with zipfile.ZipFile(DECK) as z:
            for parte, titulo, texto in self.novos:
                sl = doc[titulo]
                if sl["apendice"]:
                    continue
                x = z.read(parte).decode("utf-8")
                # fora da regra: a linha de fontes e a navegação do rodapé, que é do template do deck
                sem_fontes = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="\d+" name="(?:Fontes|Navegação do rodapé)".*?</p:sp>',
                                    "", x, flags=re.S)
                tamanhos = [int(v) for v in re.findall(r'<a:rPr[^>]* sz="(\d+)"', sem_fontes)]
                self.assertTrue(tamanhos, titulo)
                self.assertGreaterEqual(min(tamanhos), 1200, titulo)
                for tab in re.findall(r"<a:tbl>.*?</a:tbl>", x, flags=re.S):
                    self.assertGreaterEqual(min(int(v) for v in re.findall(r' sz="(\d+)"', tab)), 1400, titulo)
                if not titulo.startswith(("Os três ciclos", "Discussão", "Especificação", "H3:")):
                    self.assertTrue(sl["explica"], f"sem 'O que isso quer dizer': {titulo}")
                    self.assertIn("O que isso quer dizer", texto, titulo)

    def test_exemplos_fora_e_visibilidade_do_grupo(self) -> None:
        """Os EXEMPLO de outro trabalho saem; os slides do grupo ficam com a visibilidade que o grupo deu a eles."""
        self.assertFalse(any("Wine" in tx or tx.startswith("EXEMPLO") for _, _, tx in self.deck))
        ocultos = []
        with zipfile.ZipFile(DECK) as z:
            for k, (parte, _, _) in enumerate(self.deck, 1):
                if 'show="0"' in z.read(parte).decode("utf-8")[:800]:
                    ocultos.append(k)
        self.assertEqual(ocultos, [4, 8, 10, 11, 14, 19, 20, 21])  # os ocultos do grupo, nas mesmas posições

    def test_numero_de_pagina_e_campo(self) -> None:
        """Nos slides do grupo, o número digitado à mão no canto virou o campo do número do slide, com a posição nova."""
        with zipfile.ZipFile(DECK) as z:
            for k, (parte, _, _) in enumerate(self.deck, 1):
                x = z.read(parte).decode("utf-8")
                for sp in re.findall(r"<p:sp>.*?</p:sp>", x, flags=re.S):
                    if 'name="Text Placeholder 1"' not in sp:
                        continue
                    xy = re.search(r'<a:off x="(\d+)" y="(\d+)"/>', sp)
                    if not xy or int(xy.group(1)) < 11_000_000 or int(xy.group(2)) < 6_000_000:
                        continue
                    texto = "".join(re.findall(r"<a:t>([^<]*)</a:t>", sp)).strip()
                    if re.fullmatch(r"\d{1,2}", texto):
                        self.assertIn('type="slidenum"', sp, (k, parte))
                        self.assertEqual(texto, str(k), (k, parte))
        tudo = "\n".join(tx for _, _, tx in self.deck)
        self.assertIn("Adições ao modelo do slide 19", tudo)

    def test_manifesto_do_deck(self) -> None:
        for e in self.manifesto["saidas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        for e in self.manifesto["entradas"]:
            if e["caminho"].startswith(("docs/", "output/")):
                self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
        with zipfile.ZipFile(DECK) as z:
            for e in self.manifesto["entradas"]:
                if e.get("no_pacote"):
                    self.assertEqual(hashlib.sha256(z.read(e["no_pacote"])).hexdigest(), e["sha256"], e["caminho"])
                    self.assertTrue(e["caminho"].startswith("output/"))

    @unittest.skipUnless(os.environ.get("PMME_DECK_GRUPO") and Path(os.environ.get("PMME_DECK_GRUPO", "")).exists(),
                         "PMME_DECK_GRUPO não aponta para o deck do grupo")
    def test_deterministico(self) -> None:
        import importlib
        D = importlib.import_module("gerar_deck_banca2")
        with tempfile.TemporaryDirectory() as tmp:
            D.construir(Path(os.environ["PMME_DECK_GRUPO"]), Path(tmp))
            for n in (D.ARQ_DECK,):
                self.assertEqual(sha256(Path(tmp) / n), sha256(SAIDA / n), n)


if __name__ == "__main__":
    unittest.main()
