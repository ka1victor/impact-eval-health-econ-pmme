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
   o arquivo errado só aparece como failure mode, separado e rotulado.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apresentacao" / "gerar_figuras_banca2.py"
SAIDA = ROOT / "output" / "apresentacao_banca2"
NUMEROS = SAIDA / "numeros_banca2.json"
MANIFESTO = SAIDA / "manifesto_figuras.json"
DOCS = ROOT / "docs" / "07_apresentacoes" / "banca2"
DOC01, DOC02, DOC03, README = (DOCS / "01_roteiro_narrativo.md", DOCS / "02_conteudo_slides.md",
                               DOCS / "03_proveniencia_figuras_e_numeros.md", DOCS / "README.md")
ARQUIVO_ERRADO = "data/ivs_ipea_2010_municipios.csv"
TEM_SAIDAS = NUMEROS.exists() and MANIFESTO.exists()

_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("gerar_figuras_banca2", SCRIPT)
G = importlib.util.module_from_spec(_spec)
sys.modules["gerar_figuras_banca2"] = G
_spec.loader.exec_module(G)
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
PERMITIDOS = {"0,300", "0,400", "0,3", "0,4", "0,050", "0,030", "0,080", "0,05", "1,96", "0,001",
              "1", "2", "3", "5", "10", "15", "20", "+10", "+25", "95", "80"}


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
    t = re.sub(r"\b(?:docs?|seção|auditorias?|pedido|protocolo|tarefa|slides?|banca|errata)\s+\d+[a-z]?"
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
        if not re.match(r"#{1,2} ", p):
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

def _resolver_independente(sel: dict, brutos: dict, calculados: dict):
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
        return float(d[sel["coluna"]].iloc[0])
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
                             {"TEXTO_NORMATIVO", "CITACAO_LITERATURA"})

    def test_cada_codigo_relido_da_fonte(self) -> None:
        calculados = {"lado_errado_oficial": _lado_errado("ivs", "output/aquisicao/a08_ivs_2010_oficial_municipio.csv",
                                                          "co_ibge"),
                      # failure mode: única leitura do arquivo errado neste teste
                      "lado_errado_arquivo_errado": _lado_errado("ivs_2010", ARQUIVO_ERRADO, "cod_ibge6")}
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
        self.assertEqual(len(re.findall(r"(?m)^#{1,2} ", deck)), 21)
        apend = t[t.index("<!-- apendice:inicio -->"):t.index("<!-- apendice:fim -->")]
        self.assertEqual(len(re.findall(r"(?m)^## ", apend)), 7)

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
        livres = {x for x in achados if x.isdigit() and int(x) <= 21}  # números de slide no mapa
        self.assertEqual(achados - livres - PERMITIDOS - todos_valores(self.numeros), set())

    def test_frases_e_distincoes_obrigatorias(self) -> None:
        corrido = " ".join(re.sub(r"(?m)^>\s?", "", DOC02.read_text(encoding="utf-8")).split())
        for frase in (
            "IC que contém zero não é efeito zero",
            "É ausência de efeito detectável, não prova de ineficácia.",
            "não a participação no PMM-E nem o Agora Tem Especialistas",
            "O IC honesto com o M do protocolo não descarta nada.",
            "O empilhado é frágil",
            "O ciclo 2 é robusto",
            "Escolha não é expansão",
            "Vínculo no CNES não é médico do PMM-E",
            "pacote do corte",
            "DiRD",
            "Proposta, não decisão.",
        ):
            self.assertIn(frase, corrido)
        self.assertIn("RASCUNHO", DOC02.read_text(encoding="utf-8"))


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
            livres = {x for x in achados if x.lstrip("+").isdigit() and int(x.lstrip("+")) <= 21}
            self.assertEqual(achados - livres - validos, set(), doc.name)

    def test_readme_declara_rascunho_e_decisoes(self) -> None:
        t = README.read_text(encoding="utf-8")
        self.assertIn("RASCUNHO", t)
        self.assertIn("44_sintese_rdd_bolsa_multioutcome.md", t)
        self.assertIn("mensagem principal", t)

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
                   "E9_figuras": "output/rdd_bolsa/E9_resumo.json"}
SCRIPT_DA_ETAPA = {"E6_figuras": "scripts/rdd_bolsa/13_estimar_E6_funil.py",
                   "E7_figuras": "scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py",
                   "E9_figuras": "scripts/rdd_bolsa/16_estimar_E9_escolha.py"}


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
    def test_arquivo_errado_so_como_failure_mode(self) -> None:
        man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        for f in man["figuras"]:
            usa_errado = ARQUIVO_ERRADO in f["fontes"]
            self.assertEqual(usa_errado, f["natureza"] == "FAILURE_MODE", f["arquivo"])
            self.assertEqual(usa_errado, "/failure_mode/" in f["arquivo"], f["arquivo"])
        for e in man["entradas"]:
            if e["caminho"] == ARQUIVO_ERRADO:
                self.assertIn("FAILURE MODE", e["papel"])

    def test_nada_gravado_em_data(self) -> None:
        man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        for f in man["figuras"]:
            self.assertTrue(f["arquivo"].startswith("output/apresentacao_banca2/"))
        self.assertNotIn('"data/', re.sub(r"IVS_ARQUIVO_ERRADO = .*", "", SCRIPT.read_text(encoding="utf-8")))

    def test_regra_desenhada_pela_funcao_do_relatorio(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("var_pontos_cor", texto)
        galeria = (ROOT / "scripts/rdd_bolsa/10_galeria_figura_regra.py").read_text(encoding="utf-8")
        self.assertIn("R.fig_regra_pontos", galeria)


if __name__ == "__main__":
    unittest.main()
