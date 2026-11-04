"""Deck da banca 2 revisto depois da banca de 04/11/2026 (pedidos dos professores; doc 12 da banca 2).

Parte do deck que o grupo apresentou em 04/11/2026
(`docs/07_apresentacoes/banca2/apresentada/deck_grupo_banca2_0411.pptx`, template Insper) e aplica as mudanças
registradas em `docs/07_apresentacoes/banca2/12_revisao_pos_banca_0411.md`:

- hipótese explicada num slide próprio (a frase vigente do doc 07, com exemplo);
- construção das variáveis e da base de estimação (formato longo);
- metodologia com a especificação vigente (VL-1: efeito fixo do par de UFs, sem "origem" como peso testado), a
  justificativa contra a literatura e o exemplo de estimação com os coeficientes;
- o que o software mantém fixo (candidato e par de UFs; município não);
- deck mais curto: saem a descritiva "perto do corte", o slide "incentivo limitado" (origem ×11), os gráficos da
  motivação e os cartões de KPI; a regra do IVS e a antiga H3 vão para o apêndice;
- navbar com as seções que existem; "origem" vira "local de trabalho anterior"; typos e números corrigidos.

Nada é estimado aqui. Todo número vem de `output/` (registro `numeros_banca2.json`, `VL_estimativas.csv`,
`VL_resumo.json`); as contas de leitura (5β, e^5β, km) são refeitas e conferidas contra as linhas gravadas. A figura de
robustez é a do pipeline (`gerar_figuras_banca2.figura_robustez_escolha`), só com nomes de linha mais claros.

Uso:
    python3 scripts/apresentacao/gerar_deck_banca2_pos_banca.py [--deck-grupo CAMINHO] [--sem-pdf]

Saídas em `output/apresentacao_banca2/`: `deck_banca2_pos_banca.pptx` (e `.pdf`), `final_robustez_escolha.png` e
`manifesto_deck_banca2_pos_banca.json`.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import pandas as pd
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

RAIZ = Path(__file__).resolve().parents[2]
SAIDA = RAIZ / "output" / "apresentacao_banca2"
DECK_GRUPO = RAIZ / "docs" / "07_apresentacoes" / "banca2" / "apresentada" / "deck_grupo_banca2_0411.pptx"
SHA_GRUPO = "c63bb043387d0d2cf45d62758672cdb5487786e283e825c6f6a8cd8a536ae7f2"
NUMEROS = SAIDA / "numeros_banca2.json"
VL_EST = RAIZ / "output" / "rdd_bolsa" / "VL_estimativas.csv"
VL_RES = RAIZ / "output" / "rdd_bolsa" / "VL_resumo.json"
FIG_ROB = SAIDA / "final_robustez_escolha.png"
DECK = SAIDA / "deck_banca2_pos_banca.pptx"
PDF = SAIDA / "deck_banca2_pos_banca.pdf"
MANIFESTO = SAIDA / "manifesto_deck_banca2_pos_banca.json"
DOC12 = "docs/07_apresentacoes/banca2/12_revisao_pos_banca_0411.md"

# Paleta e fonte do deck do grupo (lidas do XML dos slides 3, 8, 13 e 14).
VERDE = RGBColor(0x11, 0x47, 0x19)
VERDE2 = RGBColor(0x1E, 0x42, 0x27)
ACENTO = RGBColor(0x05, 0x64, 0x29)
TINTA = RGBColor(0xEE, 0xF3, 0xED)
TINTA2 = RGBColor(0xE8, 0xF0, 0xE7)
LINHA = RGBColor(0xDD, 0xE3, 0xDE)
TEXTO = RGBColor(0x1A, 0x1A, 0x1A)
CINZA = RGBColor(0x5E, 0x66, 0x60)
MUDO = RGBColor(0x8C, 0x8C, 0x8C)
CLARO = RGBColor(0xA8, 0xC8, 0xA3)
BRANCO = RGBColor(0xFF, 0xFF, 0xFF)
FONTE = "Montserrat"
MAT = "Cambria Math"

SECOES = ("Motivação", "Hipótese", "Dados", "Análise Descritiva", "Metodologia", "Identificação", "Resultados",
          "Robustez", "Discussão")


# ---------------------------------------------------------------------------
# Números
# ---------------------------------------------------------------------------

def br(x: float, d: int) -> str:
    s = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" if x < 0 and float(f"{abs(x):.{d}f}") != 0 else "") + s


class Numeros:
    def __init__(self) -> None:
        self.reg = json.loads(NUMEROS.read_text(encoding="utf-8"))["numeros"]
        self.usados: set[str] = set()
        d = pd.read_csv(VL_EST)
        if set(d["natureza_dos_dados"]) != {"EMPIRICO"}:
            raise SystemExit("ERRO: VL_estimativas.csv com linha não EMPIRICO")
        self.vl1 = d[d["chave_modelo"] == "VL1_emp"]
        ident = json.loads(VL_RES.read_text(encoding="utf-8"))["identificacao"]["VL1_emp"]["identificacao"]
        self.ident = ident

    def __call__(self, cod: str) -> str:
        self.usados.add(cod)
        return self.reg[cod]["valor"]

    def coef(self, termo: str) -> pd.Series:
        r = self.vl1[(self.vl1["tipo_linha"] == "coeficiente") & (self.vl1["termo"] == termo)]
        if len(r) != 1:
            raise SystemExit(f"ERRO: coeficiente {termo} do VL-1 ausente ou repetido")
        return r.iloc[0]

    def conferir(self) -> dict:
        """Refaz as contas de leitura do slide de resultados e confere com as linhas gravadas e o registro."""
        b = self.coef("bolsa_mil")["estimativa"]
        dist = self.coef("distancia_100km")["estimativa"]
        cinco = 5 * b
        rc = math.exp(cinco)
        km = cinco / -dist * 100
        if br(rc, 2) != self("VL1_EMP_RC"):
            raise SystemExit("ERRO: e^(5β) não reproduz VL1_EMP_RC")
        if br(km, 0) != self("VL1_EMP_K5"):
            raise SystemExit("ERRO: 5β ÷ |δ| × 100 não reproduz VL1_EMP_K5")
        lin = self.vl1.iloc[0]
        if int(lin["n_candidatos"]) != int(self.ident["candidatos_no_modelo"]):
            raise SystemExit("ERRO: candidatos do VL-1 divergem entre VL_estimativas.csv e VL_resumo.json")
        if int(lin["n_efeitos_fixos"]) != int(self.ident["colunas_de_efeito_fixo"]):
            raise SystemExit("ERRO: dummies do par divergem entre VL_estimativas.csv e VL_resumo.json")
        return {"beta": b, "cinco_beta": cinco, "rc": rc, "dist": dist, "km": km,
                "n_cand": int(lin["n_candidatos"]), "n_lin": int(lin["n_linhas_candidato_celula"]),
                "n_conj": int(lin["n_conjuntos"]), "n_ef": int(lin["n_efeitos_fixos"]),
                "pares_var": int(self.ident["pares_com_variacao_de_bolsa"]),
                "cand_var": int(self.ident["candidatos_com_variacao_de_bolsa_em_algum_par"])}


# ---------------------------------------------------------------------------
# Ajudantes de pptx
# ---------------------------------------------------------------------------

def _fonte(font, size=None, bold=None, color=None, italic=None, nome=FONTE):
    if size is not None:
        font.size = Pt(size)
    if bold is not None:
        font.bold = bold
    if italic is not None:
        font.italic = italic
    if color is not None:
        font.color.rgb = color
    if nome:
        font.name = nome
        rpr = font._rPr
        for tag in ("a:ea", "a:cs"):
            el = rpr.find(qn(tag))
            if el is None:
                el = etree.SubElement(rpr, qn(tag))
            el.set("typeface", nome)


def escrever(tf, paras, size=14, color=TEXTO, bold=False, align=PP_ALIGN.LEFT, espaco=0, nome=FONTE):
    """paras: lista de parágrafos; cada um é str ou lista de (texto, opções)."""
    tf.word_wrap = True
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if espaco:
            p.space_after = Pt(espaco)
        corridas = [(para, {})] if isinstance(para, str) else para
        for txt, o in corridas:
            r = p.add_run()
            r.text = txt
            _fonte(r.font, o.get("size", size), o.get("bold", bold), o.get("color", color), o.get("italic"),
                   o.get("nome", nome))
            if o.get("sub"):
                r._r.get_or_add_rPr().set("baseline", "-25000")
            if o.get("sup"):
                r._r.get_or_add_rPr().set("baseline", "30000")


def caixa(sl, x, y, w, h, paras, size=14, color=TEXTO, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
          fill=None, line=None, forma=MSO_SHAPE.RECTANGLE, margem=0.0, espaco=0, nome=None, fonte=FONTE):
    if fill is None and line is None:
        sh = sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    else:
        sh = sl.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
        sh.shadow.inherit = False
        if fill is None:
            sh.fill.background()
        else:
            sh.fill.solid()
            sh.fill.fore_color.rgb = fill
        if line is None:
            sh.line.fill.background()
        else:
            sh.line.color.rgb = line
            sh.line.width = Pt(1)
        if forma == MSO_SHAPE.ROUNDED_RECTANGLE:
            sh.adjustments[0] = 0.08
    if nome:
        sh.name = nome
    tf = sh.text_frame
    m = Inches(margem)
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = m
    tf.vertical_anchor = anchor
    tf.auto_size = None
    if paras:
        escrever(tf, paras, size, color, bold, align, espaco, fonte)
    return sh


def retangulo(sl, x, y, w, h, fill, forma=MSO_SHAPE.RECTANGLE, line=None, nome=None):
    return caixa(sl, x, y, w, h, None, fill=fill, line=line, forma=forma, nome=nome)


def _borda(cell, lado, cor=None, w=Pt(1)):
    tcPr = cell._tc.get_or_add_tcPr()
    tag = {"L": "a:lnL", "R": "a:lnR", "T": "a:lnT", "B": "a:lnB"}[lado]
    for el in tcPr.findall(qn(tag)):
        tcPr.remove(el)
    ln = etree.Element(qn(tag), w=str(int(w) if cor is not None else 0))
    if cor is None:
        etree.SubElement(ln, qn("a:noFill"))
    else:
        sf = etree.SubElement(ln, qn("a:solidFill"))
        etree.SubElement(sf, qn("a:srgbClr"), val=str(cor))
    ordem = ["a:lnL", "a:lnR", "a:lnT", "a:lnB"]
    pos = 0
    for t in ordem[:ordem.index(tag)]:
        pos += len(tcPr.findall(qn(t)))
    tcPr.insert(pos, ln)


def tabela(sl, x, y, larguras, linhas, size=12, alt=0.45, cab=True, destaque=(), nome=None, cores_col=None,
           negrito_col=(0,), alt_cab=None):
    """Tabela nativa no estilo do deck: cabeçalho verde-escuro, linhas brancas com fio cinza, destaque em tinta."""
    n, m = len(linhas), len(larguras)
    gf = sl.shapes.add_table(n, m, Inches(x), Inches(y), Inches(sum(larguras)), Inches(alt * n))
    if nome:
        gf.name = nome
    t = gf.table
    tblPr = t._tbl.tblPr
    for a in ("firstRow", "bandRow"):
        tblPr.set(a, "0")
    sid = tblPr.find(qn("a:tableStyleId"))
    if sid is not None:
        tblPr.remove(sid)
    for j, w in enumerate(larguras):
        t.columns[j].width = Inches(w)
    for i, lin in enumerate(linhas):
        t.rows[i].height = Inches(alt_cab if (cab and i == 0 and alt_cab) else alt)
        for j, val in enumerate(lin):
            c = t.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.08)
            c.margin_top = c.margin_bottom = Inches(0.03)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            eh_cab = cab and i == 0
            c.fill.solid()
            c.fill.fore_color.rgb = VERDE if eh_cab else (TINTA if i in destaque else BRANCO)
            cor = BRANCO if eh_cab else (cores_col[j] if cores_col else TEXTO)
            tf = c.text_frame
            tf.paragraphs[0].text = ""
            escrever(tf, [val],
                     size=size if not eh_cab else size - 1, color=cor,
                     bold=eh_cab or (j in negrito_col) or (i in destaque))
            for lado in "LRT":
                _borda(c, lado, None)
            _borda(c, "B", LINHA if not eh_cab else None)
    return gf


def titulo(sl, texto, size=None):
    for sh in sl.placeholders:
        if sh.placeholder_format.type is not None and "TITLE" in str(sh.placeholder_format.type):
            p = sh.text_frame.paragraphs[0]
            rs = p.runs
            rs[0].text = texto
            if size:
                rs[0].font.size = Pt(size)
            for r in rs[1:]:
                p._p.remove(r._r)
            for extra in sh.text_frame.paragraphs[1:]:
                sh.text_frame._txBody.remove(extra._p)
            return sh
    raise SystemExit("ERRO: slide sem título")


def achar(sl, prefixo: str):
    for sh in sl.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip().startswith(prefixo):
            return sh
    return None


def trocar(sh, textos: list[str]):
    """Troca o texto parágrafo a parágrafo, mantendo a formatação da última corrida de cada parágrafo."""
    ps = sh.text_frame.paragraphs
    if len(textos) > len(ps):
        raise SystemExit(f"ERRO: {sh.name} tem {len(ps)} parágrafos; pedidos {len(textos)}")
    for p, txt in zip(ps, textos):
        if txt is None:
            continue
        rs = p.runs
        rs[-1].text = txt
        for r in rs[:-1]:
            p._p.remove(r._r)
    for p in ps[len(textos):]:
        sh.text_frame._txBody.remove(p._p)


def trocar_ultima(sh, txt: str, par: int = 0):
    """Troca só a última corrida de um parágrafo (preserva rótulos como 'Implica →')."""
    sh.text_frame.paragraphs[par].runs[-1].text = txt


def por_id(sl, *ids):
    out = {sh.shape_id: sh for sh in sl.shapes}
    return [out[i] for i in ids]


def remover(sl, shapes):
    for sh in shapes:
        sh._element.getparent().remove(sh._element)


def limpar_rels(sl):
    """Larga as relações de imagem e gráfico que nenhuma forma do slide usa mais."""
    xml = etree.tostring(sl._element).decode()
    for rid, rel in list(sl.part.rels.items()):
        if rel.reltype.endswith(("/image", "/chart")) and f'"{rid}"' not in xml:
            sl.part.drop_rel(rid)


def navbar(sl, atual: str | None):
    nav = achar(sl, "Motivação")
    if nav is None:
        raise SystemExit("ERRO: slide sem navbar")
    p = nav.text_frame.paragraphs[0]
    modelo = copy.deepcopy(p.runs[0]._r)
    for r in list(p.runs):
        p._p.remove(r._r)
    end = p._p.find(qn("a:endParaRPr"))
    for k, sec in enumerate(SECOES):
        txt = sec + ("" if k == len(SECOES) - 1 else "  |  ")
        partes = [(sec, sec == atual), (txt[len(sec):], False)]
        for t, bold in partes:
            if not t:
                continue
            r = copy.deepcopy(modelo)
            r.find(qn("a:t")).text = t
            rpr = r.find(qn("a:rPr"))
            for sf in rpr.findall(qn("a:solidFill")):
                rpr.remove(sf)
            if bold:
                rpr.set("b", "1")
                sf = etree.Element(qn("a:solidFill"))
                etree.SubElement(sf, qn("a:srgbClr"), val="114719")
                rpr.insert(0, sf)
            else:
                rpr.attrib.pop("b", None)
            if end is not None:
                end.addprevious(r)
            else:
                p._p.append(r)
    nav.width = Inches(12.2)


def _num_texto(sh, rotulo: str):
    """Número de página como texto fixo (troca campo 'slidenum' por corrida, para o apêndice poder ser A1, A2)."""
    p = sh.text_frame.paragraphs[0]
    for fld in p._p.findall(qn("a:fld")):
        r = etree.Element(qn("a:r"))
        rpr = fld.find(qn("a:rPr"))
        if rpr is not None:
            r.append(copy.deepcopy(rpr))
        etree.SubElement(r, qn("a:t")).text = rotulo
        fld.addprevious(r)
        p._p.remove(fld)
    if p.runs:
        p.runs[-1].text = rotulo
        for r in p.runs[:-1]:
            p._p.remove(r._r)
    else:
        p.add_run().text = rotulo


def numero(sl, rotulo: str):
    for sh in sl.shapes:
        if sh.is_placeholder and "SLIDE_NUMBER" in str(sh.placeholder_format.type):
            _num_texto(sh, rotulo)
            return
        if sh.name.startswith("Slide Number") or (sh.has_text_frame and sh.text_frame.text.strip().isdigit()
                                                   and sh.top is not None and sh.top > Inches(6.9)):
            _num_texto(sh, rotulo)
            return


def fontes(sl, texto: str):
    sh = achar(sl, "Fontes")
    if sh is None:
        raise SystemExit("ERRO: slide sem linha de fontes")
    trocar(sh, ["Fontes: " + texto])


def rodape(sl, texto: str):
    """Linha de fontes no estilo do deck, para slides do grupo que não a tinham."""
    caixa(sl, 0.2, 7.0, 12.4, 0.22, ["Fontes: " + texto], size=8, color=MUDO, anchor=MSO_ANCHOR.MIDDLE)


def notas(sl, texto: str):
    ns = sl.notes_slide
    if ns.notes_text_frame is None:  # página de notas sem o corpo: copia o corpo de uma página de notas do deck
        modelo = next(s.notes_slide.notes_placeholder for s in sl.part.package.presentation_part.presentation.slides
                      if s.has_notes_slide and s.notes_slide.notes_placeholder is not None)
        ns.shapes._spTree.append(copy.deepcopy(modelo._element))
    ns.notes_text_frame.text = texto


def nova_lamina(prs, modelo):
    """Slide novo com o layout e o cromo (título, fontes, número, navbar) do slide-modelo, sem o conteúdo."""
    sl = prs.slides.add_slide(modelo.slide_layout)
    for sh in list(sl.shapes):
        sh._element.getparent().remove(sh._element)
    for sh in modelo.shapes:
        t = sh.text_frame.text if sh.has_text_frame else ""
        if (sh.is_placeholder or t.startswith("Fontes") or t.startswith("Motivação")):
            sl.shapes._spTree.append(copy.deepcopy(sh._element))
    return sl


def cabecalho(sl, x, y, w, texto, sub=None):
    caixa(sl, x, y, w, 0.32, [texto], size=15, bold=True, color=TEXTO)
    if sub:
        caixa(sl, x, y + 0.33, w, 0.28, [sub], size=11, color=CINZA)


def chip(sl, x, y, w, texto, fill=CLARO, cor=VERDE):
    caixa(sl, x, y, w, 0.3, [texto], size=9.5, bold=True, color=cor, fill=fill, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE, forma=MSO_SHAPE.ROUNDED_RECTANGLE)


def cautela(sl, texto, y=6.5, h=0.42):
    caixa(sl, 0.25, y, 12.85, h, [[("Cautela: ", {"bold": True, "color": VERDE}), (texto, {})]], size=12,
          color=TEXTO, fill=TINTA, anchor=MSO_ANCHOR.MIDDLE, margem=0.15)


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

def s_motivacao(sl, N):
    titulo(sl, "A bolsa do PMM-E é maior onde o município é mais vulnerável")
    remover(sl, por_id(sl, 47, 45, 46, 10, 11, 12, 15, 16, 17))
    for sh in sl.shapes:  # typo do grupo no título da notícia do MS
        for sub in getattr(sh, "shapes", []):
            if sub.has_text_frame:
                for p in sub.text_frame.paragraphs:
                    for r in p.runs:
                        r.text = r.text.replace("medicos", "médicos")
    cabecalho(sl, 0.35, 3.85, 7.9, "I. A regra: a bolsa mensal cresce com o IVS do município da vaga",
              "IVS = Índice de Vulnerabilidade Social (Ipea, Censo 2010)")
    faixas = (("IVS até 0,300", "R$ 10 mil", TINTA, VERDE), ("IVS de 0,300 a 0,400", "R$ 15 mil", CLARO, VERDE),
              ("IVS acima de 0,400", "R$ 20 mil", VERDE, BRANCO))
    for k, (rot, val, fill, cor) in enumerate(faixas):
        x = 0.35 + k * 2.65
        caixa(sl, x, 4.65, 2.45, 1.55, [[(rot, {"size": 12})], [(val, {"size": 26, "bold": True})],
                                        [("por mês", {"size": 11})]], color=cor, fill=fill, anchor=MSO_ANCHOR.MIDDLE,
              align=PP_ALIGN.CENTER, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    caixa(sl, 0.35, 6.3, 7.9, 0.4, ["O município não escolhe a bolsa: ela sai da regra."], size=12, color=CINZA)
    caixa(sl, 8.65, 3.85, 4.35, 2.85,
          [[("PERGUNTA", {"size": 11, "bold": True, "color": CLARO})],
           [("Quando o médico escolhe entre as vagas do PMM-E, a bolsa maior faz uma vaga ser a sua 1ª opção?",
             {"size": 17, "bold": True})]], color=BRANCO, fill=VERDE, anchor=MSO_ANCHOR.MIDDLE, margem=0.25,
          espaco=6, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    fontes(sl, "Ministério da Saúde (gov.br), notas de 10/09/2025 e 27/08/2026; O Secretário do Povo e ClickPiauí, "
               "27/08/2026; editais do PMM-E (SGTES/MS), faixas da bolsa; Ipea, IVS 2010.")
    navbar(sl, "Motivação")
    limpar_rels(sl)
    notas(sl, "Roteiro (40 s). O Mais Médicos Especialistas paga uma bolsa mensal ao especialista, e o valor depende "
              "da vulnerabilidade do município da vaga: até IVS 0,300, R$ 10 mil; de 0,300 a 0,400, R$ 15 mil; acima, "
              "R$ 20 mil. O município não escolhe: é a regra do edital. Nossa pergunta: quando o médico escolhe entre "
              "as vagas, a bolsa maior faz uma vaga ser a sua 1ª opção?\n\nDetalhe: o IVS é o IVS 2010 oficial do "
              "Ipea; ele reproduz a faixa de todos os municípios dos ciclos 1 e 2 (apêndice A1). Nos mesmos cortes "
              "mudam outras regras federais: o contraste é o pacote do corte, não a bolsa sozinha nem a participação "
              "no PMM-E.")


def s_hipotese(sl, N):
    titulo(sl, "Hipótese: na mesma UF, a bolsa maior atrai a 1ª opção")
    caixa(sl, 0.25, 0.95, 12.85, 1.3,
          [[("HIPÓTESE", {"size": 11, "bold": True, "color": CLARO})],
           [("Entre duas vagas do mesmo curso e da mesma UF, a que paga R$ 5 mil a mais por mês tem mais chance de "
             "ser a 1ª opção do médico.", {"size": 19, "bold": True})]],
          color=BRANCO, fill=VERDE, anchor=MSO_ANCHOR.MIDDLE, margem=0.25, espaco=4,
          forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    cabecalho(sl, 0.25, 2.45, 12.8, "I. Exemplo: o que a hipótese compara", "ilustrativo")
    caixa(sl, 0.25, 3.15, 3.2, 1.75, [[("Um candidato", {"bold": True, "size": 15})],
                                      [("cardiologista que trabalhava em Minas Gerais", {"size": 12})]],
          fill=TINTA, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER, margem=0.15,
          forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    for k, (rot, bolsa, fill, cor) in enumerate((("Vaga A · MG", "R$ 10 mil/mês", BRANCO, TEXTO),
                                                 ("Vaga B · MG", "R$ 15 mil/mês", CLARO, VERDE))):
        y = 3.15 + k * 0.95
        caixa(sl, 3.95, y, 3.3, 0.8, [[(rot + "   ", {"bold": True}), (bolsa, {"bold": True, "color": cor})]],
              size=14, fill=fill, line=LINHA, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER,
              forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    caixa(sl, 3.45, 3.15, 0.5, 1.75, ["→"], size=26, color=VERDE, bold=True, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE)
    caixa(sl, 7.25, 3.15, 0.5, 1.75, ["→"], size=26, color=VERDE, bold=True, align=PP_ALIGN.CENTER,
          anchor=MSO_ANCHOR.MIDDLE)
    caixa(sl, 7.75, 3.15, 5.35, 1.75,
          [[("Hipótese: ", {"bold": True, "color": VERDE}), ("P(B ser a 1ª opção) > P(A ser a 1ª opção)", {"bold": True})],
           [("mesmo curso, mesma UF e o resto igual: distância, porte, IVS em curva contínua", {"size": 12,
                                                                                               "color": CINZA})]],
          size=15, fill=TINTA, anchor=MSO_ANCHOR.MIDDLE, margem=0.2, espaco=4, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    cards = (("Contraste", "vagas diferentes, para o mesmo médico, num mesmo momento"),
             ("Medida", "razão de chances da 1ª opção por +R$ 5 mil: hipótese > 1"),
             ("Não é", "que mais médicos cheguem ao município: só a escolha de quem se inscreveu"))
    for k, (rot, txt) in enumerate(cards):
        x = 0.25 + k * 4.35
        caixa(sl, x, 5.1, 4.15, 1.2, [[(rot, {"bold": True, "color": VERDE, "size": 13})], [(txt, {"size": 12})]],
              fill=BRANCO, line=LINHA, margem=0.15, espaco=3, anchor=MSO_ANCHOR.MIDDLE,
              forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    cautela(sl, "formulada depois de ver os dados: o resultado é exploratório. A bolsa muda junto com outras regras "
                "no mesmo corte de IVS (pacote).", y=6.42)
    fontes(sl, f"doc 07 da banca 2 (decisão do autor de 28/10/2026); adendo 52e; doc 57x; auditoria 48. {DOC12}.")
    navbar(sl, "Hipótese")
    notas(sl, "Roteiro (50 s). A hipótese é sobre escolha, não sobre o município ao longo do tempo. Pegue um "
              "candidato e duas vagas do curso dele, na mesma UF, parecidas em tudo — mas uma paga R$ 5 mil a mais "
              "por mês porque o município está do outro lado de um corte de IVS. A hipótese: a vaga de bolsa maior "
              "tem mais chance de ser a 1ª opção dele. Medimos isso como razão de chances; a hipótese é que ela seja "
              "maior que 1. Não dizemos nada sobre mais médicos chegando ao município: só sobre a vaga que quem se "
              "inscreveu marcou em 1º lugar. E um aviso honesto: formulamos a hipótese depois de ver os dados.\n\n"
              "Por que a versão anterior confundia: 'um aumento na remuneração eleva a probabilidade' sugeria uma "
              "bolsa que sobe no tempo e um efeito no município; não há aumento no tempo — a variação é entre vagas, "
              "pela regra do IVS — e a comparação é só entre vagas da mesma UF. O contraste é o pacote do corte "
              "(auditoria 18), não a participação no PMM-E. Exemplo ilustrativo: não são dados reais.")


def s_dados(sl, N, c):
    titulo(sl, "Base: uma linha por candidato × vaga possível")
    cabecalho(sl, 0.25, 0.85, 7.0, "I. Variáveis: como cada uma é construída")
    linhas = [["Variável", "Construção", "Fonte"],
              ["1ª opção (y)", "1 na vaga marcada em 1º lugar; 0 nas outras vagas do curso e ciclo",
               "Editais PMM-E (SGTES/MS)"],
              ["Bolsa", "R$ 10, 15 ou 20 mil/mês pela faixa do IVS do município da vaga", "Quadros de vagas; Ipea"],
              ["Local de trabalho anterior", "município do vínculo médico no CNES antes da inscrição (não é a "
                                             "residência)", "CNES/DATASUS"],
              ["Distância", "km entre os centros do município anterior e do município da vaga", "IBGE"],
              ["Par de UFs", "UF de trabalho anterior × UF da vaga", "IBGE"],
              ["Controles", "curva do IVS; mesma região de saúde; mesmo município; porte; capital; vaga imediata",
               "Ipea; TabNet; IBGE; quadros"]]
    tabela(sl, 0.25, 1.25, [1.75, 3.65, 1.6], linhas, size=11, alt=0.63, alt_cab=0.45)
    cabecalho(sl, 7.55, 0.85, 5.5, "II. Formato longo", "linhas ilustrativas, não dados reais")
    longa = [["Candidato", "Vaga", "y", "Bolsa", "km", "Par"],
             ["A (MG)", "v1 · MG", "0", "10", "120", "MG→MG"],
             ["A (MG)", "v2 · MG", "1", "15", "340", "MG→MG"],
             ["A (MG)", "v3 · SP", "0", "10", "510", "MG→SP"],
             ["A (MG)", "v4 · BA", "0", "20", "980", "MG→BA"],
             ["B (BA)", "v1 · MG", "0", "10", "1.100", "BA→MG"]]
    tabela(sl, 7.55, 1.6, [1.05, 1.0, 0.45, 0.75, 0.75, 1.5], longa, size=11, alt=0.45, destaque=(2,),
           negrito_col=())
    caixa(sl, 7.55, 4.4, 5.5, 0.75, ["Cada candidato vê todas as vagas do seu curso e ciclo; y = 1 numa só."],
          size=11, color=CINZA)
    retangulo(sl, 0.25, 5.6, 12.85, 1.1, VERDE, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    kpis = ((N("AM_TOT_R1"), "candidatos com 1ª opção (ciclos 1–3)"),
            (N("AM_TOT_ORI"), "com local de trabalho anterior no CNES"),
            (br(c["n_cand"], 0), "no modelo principal"),
            (br(c["n_lin"], 0), f"linhas candidato × vaga (≈ {br(c['n_lin'] / c['n_cand'], 0)} por candidato)"))
    for k, (v, rot) in enumerate(kpis):
        x = 0.45 + k * 3.2
        caixa(sl, x, 5.65, 2.7, 1.0, [[(v, {"size": 22, "bold": True})], [(rot, {"size": 10.5})]], color=BRANCO,
              anchor=MSO_ANCHOR.MIDDLE)
        if k < 2:
            caixa(sl, x + 2.75, 5.65, 0.4, 1.0, ["→"], size=18, color=CLARO, bold=True, anchor=MSO_ANCHOR.MIDDLE)
    fontes(sl, "editais e quadros de vagas do PMM-E (SGTES/MS), ciclos 1–3; CNES/DATASUS (portão G1); Ipea, IVS 2010; "
               "IBGE; TabNet. P1_resumo.json; VL_estimativas.csv (VL-1).")
    navbar(sl, "Dados")
    notas(sl, "Roteiro (55 s). A base de estimação tem uma linha para cada par candidato × vaga que ele podia "
              "escolher: todas as vagas do seu curso e ciclo no quadro da 1ª chamada. A variável dependente vale 1 "
              "na vaga que ele marcou em 1º lugar e 0 nas demais. A bolsa vem da faixa do IVS do município da vaga. O "
              "local de trabalho anterior é o município onde o médico tinha vínculo no CNES antes de se inscrever — "
              "não é onde mora. Dele saem a distância até cada vaga e o par de UFs: UF de trabalho anterior × UF da "
              f"vaga. No modelo principal ficam {br(c['n_cand'], 0)} candidatos e {br(c['n_lin'], 0)} linhas, cerca "
              f"de {br(c['n_lin'] / c['n_cand'], 0)} vagas por candidato.\n\n"
              f"Funil (P1_resumo.json): {N('AM_TOT_R1')} candidatos com 1ª opção numa vaga do quadro; "
              f"{N('AM_TOT_LIG')} ligados ao CNES (CPF e nome); {N('AM_TOT_ORI')} com município de vínculo anterior; "
              f"{N('M1_N')} no modelo base, depois de tirar quem tem a vaga ou a origem sem região de saúde na tabela "
              f"oficial; {br(c['n_cand'], 0)} no VL-1, depois de tirar os pares de UF que ninguém escolheu (a dummy "
              f"deles iria a menos infinito). {br(c['n_conj'], 0)} conjuntos de escolha (curso × ciclo). A tabela da "
              "direita é ilustrativa. Dados pessoais só em memória ou em cache fora do Git.")


def s_descritiva(sl, N):
    titulo(sl, f"{N('ESC_UF')}% escolhem uma vaga na UF onde já trabalhavam")
    manter = {2, 21, 22, 23, 28, 29, 4, 30}
    remover(sl, [sh for sh in sl.shapes if sh.shape_id not in manter])
    h21, h22, graf, cav = por_id(sl, 21, 22, 23, 28)
    h21.left, h21.top, h21.width = Inches(0.25), Inches(0.9), Inches(7.6)
    trocar(h21, ["I. Onde fica a 1ª opção, em relação ao local de trabalho anterior"])
    h22.left, h22.top, h22.width = Inches(0.25), Inches(1.24), Inches(7.6)
    trocar(h22, [f"% dos {N('ESC_N')} candidatos com 1ª opção e local de trabalho anterior identificado"])
    graf.left, graf.top, graf.width, graf.height = Inches(0.25), Inches(1.6), Inches(7.6), Inches(4.65)
    for k, (v, rot) in enumerate(((f"{N('ESC_DIST_P50')} km", "é a distância mediana até a 1ª opção"),
                                  ("3 em 4", f"escolhem uma vaga a até {N('ESC_DIST_P75')} km"))):
        y = 1.0 + k * 1.55
        caixa(sl, 8.3, y, 4.8, 1.35, [[(v, {"size": 30, "bold": True, "color": VERDE})], [(rot, {"size": 13})]],
              fill=TINTA, margem=0.2, anchor=MSO_ANCHOR.MIDDLE, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    caixa(sl, 8.3, 4.15, 4.8, 2.1,
          [[("POR ISSO", {"size": 11, "bold": True, "color": CLARO})],
           [("O modelo compara só vagas da mesma UF: a UF entra como pareamento, não como resultado.",
             {"size": 16, "bold": True})]], color=BRANCO, fill=VERDE, margem=0.25, espaco=4,
          anchor=MSO_ANCHOR.MIDDLE, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    cav.top, cav.width = Inches(6.45), Inches(12.8)
    trocar(cav, ["Descritivo: mostra onde escolhem, não por quê. Local de trabalho anterior = vínculo no CNES, não a "
                 "residência."])
    fontes(sl, "listas de classificação dos editais do PMM-E (SGTES/MS), ciclos 1–3; CNES/DATASUS (portão G1); malha "
               "municipal do IBGE. G1_distancias_opcoes.parquet.")
    navbar(sl, "Análise Descritiva")
    limpar_rels(sl)
    notas(sl, f"Roteiro (35 s). Antes do modelo, os dados crus. Dos {N('ESC_N')} candidatos, {N('ESC_UF')}% põem a "
              f"1ª opção na UF onde já trabalhavam, {N('ESC_REG')}% na mesma região de saúde e {N('ESC_MUN')}% no "
              f"próprio município; a distância mediana é {N('ESC_DIST_P50')} km. Isso é descritivo e não é o nosso "
              "resultado: é o motivo do desenho. Como quase todos escolhem dentro da própria UF, comparar uma vaga "
              "do Amazonas com uma de São Paulo misturaria a bolsa com a UF; por isso o modelo só compara vagas da "
              "mesma UF.\n\nO local de trabalho anterior é o município do vínculo médico no CNES antes da inscrição, "
              "não a residência. Saíram deste slide (pedido da banca, enxugar): os cartões repetidos, o histograma "
              "das distâncias e o slide 'perto do corte', que criava expectativa de RDD.")


def _eq(p, partes, size=20):
    for txt, sub in partes:
        r = p.add_run()
        r.text = txt
        _fonte(r.font, size, False, TEXTO, True, MAT)
        if sub:
            r._r.get_or_add_rPr().set("baseline", "-25000")


def s_modelo(sl, N, c):
    titulo(sl, "Modelo: logit condicional da 1ª opção")
    cabecalho(sl, 0.25, 0.85, 8.6, "I. Especificação (McFadden, 1974)")
    caixa_eq = retangulo(sl, 0.25, 1.25, 8.65, 1.85, TINTA, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    tb = sl.shapes.add_textbox(Inches(0.4), Inches(1.32), Inches(8.35), Inches(1.7))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    _eq(p, [("U", False), ("iv", True), (" = β·bolsa", False), ("v", True), (" + f(IVS", False), ("v", True),
            (") + δ·dist", False), ("iv", True), (" + α", False), ("UF(i),UF(v)", True), (" + θ·X", False),
            ("iv", True), (" + ε", False), ("iv", True)], 19)
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(6)
    _eq(p, [("P(i escolhe v) = exp(U", False), ("iv", True), (") ⁄ Σ", False), ("k ∈ vagas de i", True),
            (" exp(U", False), ("ik", True), (")", False)], 17)
    p = tf.add_paragraph()
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(6)
    r = p.add_run()
    r.text = "i: candidato · v: vaga do seu curso e ciclo · X: região de saúde, município, porte, capital, vaga imediata"
    _fonte(r.font, 10.5, False, CINZA)
    caixa(sl, 9.15, 1.25, 3.95, 1.85,
          [[("O QUE SE ESTIMA", {"size": 10.5, "bold": True, "color": CLARO})],
           [("e", {"size": 17, "bold": True}), ("5β", {"size": 17, "bold": True, "sup": True}),
            (": quanto +R$ 5 mil multiplicam a chance de a vaga ser a 1ª opção", {"size": 14, "bold": True})],
           [("máxima verossimilhança; erro-padrão agrupado por curso × ciclo", {"size": 10.5, "color": CLARO})]],
          color=BRANCO, fill=VERDE, margem=0.18, espaco=4, anchor=MSO_ANCHOR.MIDDLE,
          forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    cabecalho(sl, 0.25, 3.3, 12.8, "II. O papel de cada termo")
    termos = (("β · bolsa", "TESTADO", "salta nos cortes de IVS (R$ 10 → 15 → 20 mil)", VERDE, BRANCO),
              ("α · par de UFs", "PAREAMENTO", "efeito fixo: só compara vagas da mesma UF, vistas por médicos da "
                                               "mesma UF", CLARO, VERDE),
              ("f(IVS)", "CONTROLE", "curva contínua do IVS, sem salto: no corte, só a bolsa salta", LINHA, CINZA),
              ("δ · distância, θ · X", "CONTROLE", "atributos da vaga e da distância; não interpretados", LINHA,
               CINZA))
    for k, (nome, tipo, txt, fchip, cchip) in enumerate(termos):
        x = 0.25 + k * 3.25
        retangulo(sl, x, 3.7, 3.1, 1.7, BRANCO, forma=MSO_SHAPE.ROUNDED_RECTANGLE, line=LINHA)
        caixa(sl, x + 0.15, 3.8, 2.8, 0.4, [nome], size=15, bold=True, color=TEXTO, fonte=MAT)
        chip(sl, x + 0.15, 4.22, 1.45, tipo, fill=fchip, cor=cchip)
        caixa(sl, x + 0.15, 4.62, 2.8, 0.95, [txt], size=11.5, color=TEXTO)
    caixa(sl, 0.25, 5.6, 12.85, 0.95,
          [[("Por que “condicional”: ", {"bold": True, "color": VERDE}),
            ("a probabilidade é calculada dentro das vagas de cada candidato. O que é do médico (idade, nota, "
             "especialidade) é igual em todas as vagas dele e se cancela: cada médico é comparado consigo mesmo.", {})]],
          size=13, fill=TINTA, margem=0.18, anchor=MSO_ANCHOR.MIDDLE, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    fontes(sl, "McFadden (1974); protocolo 52; adendos 52c e 52e; docs 57a e 57x; scripts/rdd_bolsa/25_escolha_dap.py "
               "e 50_escolha_localizacao_par.py.")
    navbar(sl, "Metodologia")
    notas(sl, "Roteiro (50 s). O médico escolhe uma entre as vagas do seu curso: é uma escolha discreta. No logit "
              "condicional, cada vaga tem uma atratividade U; a probabilidade de ser a 1ª opção é e elevado a U "
              "dividido pela soma sobre as vagas daquele candidato. O termo testado é β, o peso da bolsa: e elevado "
              "a 5β diz quanto R$ 5 mil a mais multiplicam a chance. α é o efeito fixo do par de UFs: faz a "
              "comparação só entre vagas da mesma UF. O IVS entra como curva contínua, sem salto: no corte, só a "
              "bolsa salta. Distância e atributos da vaga são controles.\n\nDetalhe (VL-1, adendo 52e): bolsa linear "
              "por R$ 1 mil; spline do IVS com dobras em 0,300 e 0,400; distância por 100 km; mesma região de saúde "
              "e mesmo município do local de trabalho anterior; porte (log da população 2022), capital, estrato, "
              "vaga imediata; efeito fixo do par (UF de trabalho anterior, UF da vaga). Estimação por máxima "
              "verossimilhança (Newton–Raphson próprio, conferido contra o ConditionalLogit do statsmodels no doc "
              f"42). Erro-padrão agrupado por conjunto de escolha (curso × ciclo; {br(c['n_conj'], 0)} grupos), Holm "
              "nas três principais do adendo e score bootstrap de Rademacher para poucos grupos.")


def s_por_que(sl, N):
    titulo(sl, "Por que logit condicional, e não só uma RDD por vaga")
    cabecalho(sl, 0.25, 0.85, 7.9, "I. A literatura de escolha de local usa a família logit")
    linhas = [["Estudo", "Contexto e método", "Por que precisam disso"],
              ["Bobba et al. (2026), NBER", "professores no Peru: adicional salarial por regra num corte + "
                                             "modelo de escolha de vagas", "escolhe na sua vez; pode recusar todas"],
              ["Costa, Nunes e Sanches (2024), REStat", "médicos no Brasil: logit de coeficientes aleatórios + "
                                                         "instrumento", "salário de mercado é endógeno"],
              ["Nós (PMM-E)", "logit condicional + efeito fixo do par de UFs",
               "bolsa por regra; opções listadas na inscrição"]]
    tabela(sl, 0.25, 1.3, [2.2, 3.2, 2.5], linhas, size=12, alt=1.05, destaque=(3,), alt_cab=0.5)
    caixa(sl, 0.25, 5.0, 7.9, 0.9,
          [[("Referência forte: ", {"bold": True, "color": VERDE}),
            ("Bobba et al. têm o desenho mais parecido — salário por regra num corte — e também combinam a RDD por "
             "vaga com um modelo de escolha.", {})]], size=12.5, fill=TINTA, margem=0.15, anchor=MSO_ANCHOR.MIDDLE,
          forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    cabecalho(sl, 8.5, 0.85, 4.6, "II. Por que não algo mais simples?")
    alt = (("RDD por vaga", "compara vagas dos dois lados do corte, uma observação por vaga. Feita: IC contém zero.",
            BRANCO, TEXTO),
           ("Logit condicional", "compara, para o mesmo médico, ≈ 107 vagas com bolsas diferentes: usa a variação "
                                 "dentro do candidato.", VERDE, BRANCO),
           ("Poisson com efeito fixo", "dá o mesmo β (Guimarães, Figueiredo e Woodward, 2003): o logit condicional "
                                       "já é o simples da família.", BRANCO, TEXTO))
    for k, (rot, txt, fill, cor) in enumerate(alt):
        caixa(sl, 8.5, 1.3 + k * 1.62, 4.6, 1.47, [[(rot, {"bold": True, "size": 14})], [(txt, {"size": 11.5})]],
              color=cor, fill=fill, line=LINHA, margem=0.18, espaco=3, anchor=MSO_ANCHOR.MIDDLE,
              forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    cautela(sl, "trocar o estimador depois de ver o resultado seria escolha pós-resultado; alternativas entram só "
                "como robustez rotulada.", y=6.4)
    fontes(sl, "Bobba et al., NBER WP 29068 (rev. 2026); Costa, Nunes e Sanches (2024), REStat; Guimarães, "
               "Figueiredo e Woodward (2003), REStat; doc 03_literatura_empirica/20; doc 44 (F1.1); doc 11 da banca 2.")
    navbar(sl, "Metodologia")
    notas(sl, "Roteiro (45 s). Por que esse modelo? A literatura de escolha de local de trabalho usa a família "
              "logit. A referência mais próxima é Bobba et al., com professores no Peru: o salário também muda por "
              "regra num corte, e eles combinam a RDD por vaga com um modelo de escolha. Costa, Nunes e Sanches, com "
              "médicos no Brasil, precisam de logit com coeficientes aleatórios e instrumento porque o salário de "
              "mercado é endógeno; no PMM-E a bolsa vem de regra, e o candidato lista as opções na inscrição, então o "
              "logit condicional basta. A alternativa mais simples, a RDD por vaga, foi feita: compara vagas e usa "
              "uma observação por vaga, e o IC contém zero. O logit usa muito mais informação: o mesmo médico "
              "vendo cerca de 107 vagas com bolsas diferentes.\n\nDetalhe: RDD por célula, F1.1 (doc 44): +0,063 "
              "[−0,511; +0,636]. Bobba et al. usam logit multinomial com cardápio personalizado (escolhem na vez "
              "deles, com opção de não aceitar). MQO com efeito fixo do candidato faria a mesma comparação, mas cada "
              "vaga tem probabilidade perto de 1% e o modelo linear sai de [0, 1]; não está no protocolo. A Poisson "
              "das contagens com efeito fixo de cada grupo com o mesmo cardápio e a mesma origem dá exatamente o β "
              "do logit condicional (Guimarães et al., 2003). Logit misto (M8) e aninhado por região (M9) estão no "
              "protocolo 52 como sensibilidade do modelo base; não foram refeitos com o par de UFs.")


def s_identificacao(sl, N, c):
    titulo(sl, "Identificação: o que fica fixo e o que supomos")
    cabecalho(sl, 0.25, 0.85, 7.6, "I. O que o software mantém fixo no cálculo")
    linhas = [["Item", "Como entra na estimação", "Fixo?"],
              ["Candidato", "verossimilhança dentro das vagas de cada um: o que é dele se cancela", "Sim"],
              ["Par de UFs", f"{c['n_ef']} dummies: UF de trabalho anterior × UF da vaga", "Sim"],
              ["Município / vaga", "não entra: a bolsa é a mesma no município inteiro e seria absorvida", "Não"],
              ["Distância, região, porte", f"controles na utilidade (distância: {br(c['dist'], 3)} por 100 km)",
               "Controlado"]]
    tabela(sl, 0.25, 1.25, [1.95, 4.35, 1.3], linhas, size=12, alt=0.9, alt_cab=0.5)
    caixa(sl, 0.25, 5.5, 7.6, 0.8,
          [[("O β aprende só com ", {}), ("vagas do mesmo par de UFs com bolsas diferentes", {"bold": True}),
            (f": {br(c['pares_var'], 0)} pares, {br(c['cand_var'], 0)} candidatos.", {})]], size=12.5, fill=TINTA,
          margem=0.15, anchor=MSO_ANCHOR.MIDDLE, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    cabecalho(sl, 8.2, 0.85, 4.9, "II. Premissas e aderência")
    prem = (("Bolsa por regra", f"o IVS reproduz a faixa de {N('R_C1_REPR')}/{N('R_C1_MUN')} municípios (ciclo 1) e "
                                f"{N('R_C2_REPR')}/{N('R_C2_MUN')} (ciclo 2)", "atende"),
            ("Só a bolsa muda no corte?", "não: outras regras federais mudam junto; medimos esse pacote",
             "pacote"),
            ("Conjunto de escolha", "supomos que o médico viu todas as vagas do seu curso", "suposto"))
    for k, (rot, txt, selo) in enumerate(prem):
        y = 1.25 + k * 1.42
        caixa(sl, 8.2, y, 4.9, 1.3, [[(rot, {"bold": True, "size": 14})], [(txt, {"size": 11.5})]], fill=BRANCO,
              line=LINHA, margem=0.18, espaco=3, anchor=MSO_ANCHOR.MIDDLE, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
        chip(sl, 11.75, y + 0.12, 1.2, selo.upper(), fill=CLARO if selo == "atende" else LINHA,
             cor=VERDE if selo == "atende" else CINZA)
    cautela(sl, "a especificação com o par de UFs foi escolhida depois de ver o modelo base: é exploratória.", y=6.45)
    fontes(sl, "portao_r1_ivs_oficial.json; auditorias 16, 18 e 48; adendo 52e; VL_resumo.json; "
               "scripts/rdd_bolsa/25_escolha_dap.py (_estat) e 50_escolha_localizacao_par.py (matriz_vl).")
    navbar(sl, "Identificação")
    notas(sl, "Roteiro (50 s). O que o software de fato mantém fixo? Primeiro, o candidato: o logit condicional "
              "calcula a probabilidade dentro das vagas de cada um, então tudo o que é do médico se cancela — é o "
              "efeito fixo de indivíduo. Segundo, o par de UFs: uma dummy para cada combinação de UF de trabalho "
              "anterior e UF da vaga. Terceiro, e importante: não há efeito fixo de município nem de vaga, porque a "
              "bolsa é a mesma no município inteiro; um efeito fixo de município absorveria a bolsa. A distância e a "
              "região entram como controles, não como pareamento. As premissas: a bolsa segue a regra do IVS sem "
              "exceção; no corte mudam outras regras, então medimos o pacote; e supomos que o médico viu todas as "
              "vagas do seu curso.\n\nConferência no código: scripts/rdd_bolsa/25_escolha_dap.py, função _estat — a "
              "soma do denominador é feita por candidato (np.add.reduceat nos inícios de cada grupo), então "
              "constantes do candidato saem da verossimilhança; colunas sem variação dentro de nenhum candidato são "
              "retiradas. scripts/rdd_bolsa/50_escolha_localizacao_par.py: uma coluna 0/1 por par, base no par da "
              f"própria UF ({c['n_ef']} colunas); mesma_uf e macrorregiões saem porque o par as absorve; pares que "
              "ninguém escolheu saem do modelo. Pares sem variação de bolsa ficam e só ajudam os controles. IIA: no "
              "modelo base, o logit aninhado por região de saúde a rejeita em parte e o peso da bolsa fica perto do "
              "mesmo valor (docs 57a e 57v); não foi refeito com o par de UFs.")


def s_resultados(sl, N, c):
    titulo(sl, f"Na mesma UF, +R$ 5 mil multiplicam a chance por {N('VL1_EMP_RC')}")
    cabecalho(sl, 0.25, 0.85, 6.9, "I. Coeficientes estimados (log-chance), ciclos 1–3")

    def lin(rot, termo):
        r = N.coef(termo)
        return [rot, br(r["estimativa"], 3), f"[{br(r['ic95_inf'], 3)}; {br(r['ic95_sup'], 3)}]"]
    linhas = [["Termo", "Coef.", "IC 95%"], lin("Bolsa (por R$ 1 mil/mês)", "bolsa_mil"),
              lin("Distância (por 100 km)", "distancia_100km"), lin("Mesma região de saúde", "mesma_regiao_saude"),
              lin("Mesmo município", "mesmo_municipio"), lin("log(população 2022)", "log_populacao_2022"),
              lin("Capital", "capital")]
    tabela(sl, 0.25, 1.25, [3.1, 1.3, 2.5], linhas, size=12.5, alt=0.55, destaque=(1,),
           cores_col=[TEXTO, TEXTO, CINZA])
    caixa(sl, 0.25, 5.2, 6.9, 0.95,
          [f"Também na equação: curva do IVS, estrato, vaga imediata e {c['n_ef']} dummies do par. Controles: não "
           f"interpretados. {br(c['n_cand'], 0)} candidatos; EP agrupado por curso × ciclo ({c['n_conj']} grupos)."],
          size=10.5, color=CINZA)
    cabecalho(sl, 7.5, 0.85, 5.6, "II. Da estimativa à leitura")
    passos = ((f"5 × {br(c['beta'], 3)} = {br(c['cinco_beta'], 3)}", "log-chance de +R$ 5 mil por mês"),
              ([("e", {}), (br(c['cinco_beta'], 3), {"sup": True}), (f" = {N('VL1_EMP_RC')}", {})],
               f"a vaga com +R$ 5 mil tem {N('VL1_EMP_RC')} vez a chance de ser a 1ª opção (IC 95%: "
               f"{N('VL1_EMP_RCI')} a {N('VL1_EMP_RCS')}; p de Holm {N('VL1_EMP_HOLM')})"),
              (f"{br(c['cinco_beta'], 3)} ÷ {br(-c['dist'], 3)} × 100 km = {N('VL1_EMP_K5')} km",
               f"+R$ 5 mil pesam como uma vaga {N('VL1_EMP_K5')} km mais perto"))
    for k, (conta, leitura) in enumerate(passos):
        y = 1.25 + k * 1.2
        destaque = k == 1
        partes = conta if isinstance(conta, list) else [(conta, {})]
        estilo = {"bold": True, "size": 17 if destaque else 15, "nome": MAT}
        caixa(sl, 7.5, y, 5.6, 1.08, [[(t, {**estilo, **o}) for t, o in partes], [(leitura, {"size": 11.5})]],
              color=BRANCO if destaque else TEXTO, fill=VERDE if destaque else TINTA, margem=0.18, espaco=2,
              anchor=MSO_ANCHOR.MIDDLE, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    caixa(sl, 7.5, 4.9, 5.6, 0.85,
          [[("Só o ciclo 2: ", {"bold": True, "color": VERDE}),
            (f"×{N('VL1_C2_RC')} [{N('VL1_C2_RCI')}; {N('VL1_C2_RCS')}], = {N('VL1_C2_K5')} km", {"bold": True})]],
          size=14, fill=BRANCO, line=LINHA, margem=0.18, anchor=MSO_ANCHOR.MIDDLE, forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    cautela(sl, f"especificação escolhida após ver os dados. A pré-registrada, sem o par de UFs: ×{N('VLB_EMP_RC')} "
                f"[{N('VLB_EMP_RCI')}; {N('VLB_EMP_RCS')}], IC que contém 1.", y=6.3, h=0.5)
    fontes(sl, "VL_estimativas.csv (VL-1, adendo 52e; doc 57x; auditoria 48); VC_estimativas.csv (P1a, adendo 52c).")
    navbar(sl, "Resultados")
    notas(sl, "Roteiro (55 s). Este é o resultado principal, e a tabela mostra a estimação de fato. O coeficiente da "
              f"bolsa é {br(c['beta'], 3)} por mil reais, em log-chance. Para um degrau de R$ 5 mil, multiplicamos "
              f"por 5: {br(c['cinco_beta'], 3)}. Exponenciando, {N('VL1_EMP_RC')}: entre duas vagas da mesma UF, "
              f"a de bolsa R$ 5 mil maior tem {N('VL1_EMP_RC')} vez a chance de ser a 1ª opção, com intervalo de "
              f"{N('VL1_EMP_RCI')} a {N('VL1_EMP_RCS')}. Para ter uma régua: a distância pesa {br(c['dist'], 3)} por "
              f"100 km; dividindo, R$ 5 mil valem uma vaga {N('VL1_EMP_K5')} km mais perto. No ciclo 2 sozinho, "
              f"{N('VL1_C2_RC')}. Ressalva na tela: a especificação foi escolhida depois de ver os dados, e a "
              f"pré-registrada, sem o par de UFs, tem intervalo que contém 1.\n\nDetalhe: razão de chances = razão "
              "entre as probabilidades de escolher duas vagas iguais em tudo menos a bolsa; como cada vaga tem "
              f"probabilidade pequena (≈ {br(c['n_lin'] / c['n_cand'], 0)} vagas por candidato), é perto da razão de "
              f"probabilidades. IC dos km: [{N('VL1_EMP_K5I')}; {N('VL1_EMP_K5S')}] (método delta). p de Holm na "
              "família das três principais do adendo 52e. Pré-registrada (P1a, M1 sem o par): p "
              f"{N('VC_B_HOLM')} (família de um teste). Os coeficientes dos controles descrevem quais vagas os "
              "candidatos escolhem; não são efeitos causais e não são interpretados. Pacote do corte; condicional a "
              "se candidatar.")


def s_robustez(sl, N, c, fig_rob):
    remover(sl, por_id(sl, 4, 60, 61, 62, 63, 64, 65, 80, 81, 82, 83, 84, 85))
    todos = ("VL1_EMP_RC", "VLLOG_EMP_RC", "VL3_EMP_RC", "VK1_300_RC", "VK1_400_RC")
    brutos = sorted((N.reg[k]["valor_bruto"], N(k)) for k in todos)
    faixa = (brutos[0][1], brutos[-1][1])
    pic = sl.shapes.add_picture(str(fig_rob), Inches(0.2), Inches(0.85), height=Inches(4.25))
    pic.name = "Figura robustez"
    conteudo = (("MANTÉM", "Distância em log, região de saúde e cada degrau separado; bootstrap para poucos grupos: "
                           f"p {N('VL1_EMP_PSR')}.", CLARO, VERDE),
                ("POR CICLO", "Forte só no ciclo 2; nos ciclos 1 e 3, o IC contém 1.", LINHA, CINZA),
                ("IVS A ±0,05", "Só vagas perto do corte: menos dados, IC contém 1 (inconclusivo).", LINHA, CINZA))
    for k, (rot, txt, fchip, cchip) in enumerate(conteudo):
        y = 0.95 + k * 1.45
        caixa(sl, 9.5, y, 3.6, 1.32, [[(txt, {})]], size=12, fill=TINTA, margem=0.18, anchor=MSO_ANCHOR.BOTTOM,
              forma=MSO_SHAPE.ROUNDED_RECTANGLE)
        chip(sl, 9.68, y + 0.14, 1.45, rot, fill=fchip, cor=cchip)
    caixa(sl, 0.25, 5.35, 12.85, 1.1,
          [[("Leitura: ", {"bold": True, "color": CLARO}),
            (f"com todos os dados e sempre na mesma UF, o efeito fica entre ×{faixa[0]} e ×{faixa[1]} "
             "em toda variante. Onde a informação é menor — perto do corte e nos ciclos 1 e 3 —, o IC contém 1.",
             {})]], size=14, color=BRANCO, fill=VERDE, margem=0.22, anchor=MSO_ANCHOR.MIDDLE,
          forma=MSO_SHAPE.ROUNDED_RECTANGLE)
    titulo(sl, "Robustez: sempre comparando vagas da mesma UF")
    fontes(sl, "VL_estimativas.csv (adendo 52e; auditoria 48); VG_estimativas.csv e VK_estimativas.csv (adendos 52g e "
               "52h; auditoria pendente); final_robustez_escolha.png (scripts/apresentacao/gerar_figuras_banca2.py).")
    navbar(sl, "Robustez")
    limpar_rels(sl)
    notas(sl, "Roteiro (45 s). Todas as variantes comparam vagas da mesma UF. Medindo a distância em log, usando a "
              "região de saúde no lugar da UF de trabalho anterior, ou estimando cada degrau separado — R$ 10 para "
              f"15 mil e 15 para 20 mil —, o efeito fica entre {faixa[0]} e {faixa[1]}. Com poucos "
              f"grupos, o bootstrap dá p {N('VL1_EMP_PSR')}. Só com vagas de IVS a até 0,05 de um corte, há menos "
              "dados e o intervalo contém 1: inconclusivo, não 'efeito menor'. Ciclo a ciclo, o efeito é forte só no "
              "ciclo 2; nos ciclos 1 e 3, o intervalo contém 1. Por que o ciclo 2, não sabemos.\n\n"
              f"Números: principal {N('VL1_EMP_RC')} [{N('VL1_EMP_RCI')}; {N('VL1_EMP_RCS')}]; distância em log "
              f"{N('VLLOG_EMP_RC')} [{N('VLLOG_EMP_RCI')}; {N('VLLOG_EMP_RCS')}]; região de saúde × UF da vaga (VL-3) "
              f"{N('VL3_EMP_RC')} [{N('VL3_EMP_RCI')}; {N('VL3_EMP_RCS')}]; IVS a ±0,05 (VL-2) {N('VL2_EMP_RC')} "
              f"[{N('VL2_EMP_RCI')}; {N('VL2_EMP_RCS')}], p de Holm {N('VL2_EMP_HOLM')}; idem com região "
              f"{N('VL3P_EMP_RC')} [{N('VL3P_EMP_RCI')}; {N('VL3P_EMP_RCS')}]; degrau 0,300 {N('VK1_300_RC')} "
              f"[{N('VK1_300_RCI')}; {N('VK1_300_RCS')}]; degrau 0,400 {N('VK1_400_RC')} [{N('VK1_400_RCI')}; "
              f"{N('VK1_400_RCS')}]; razão entre os degraus {N('VK1_D_RC')}, p {N('VK1_D_P')}. Por ciclo: ciclo 1 "
              f"{N('VG1_RC')} [{N('VG1_RCI')}; {N('VG1_RCS')}]; ciclo 2 {N('VL1_C2_RC')} [{N('VL1_C2_RCI')}; "
              f"{N('VL1_C2_RCS')}]; ciclo 3 {N('VG3_RC')} [{N('VG3_RCI')}; {N('VG3_RCS')}]. Score bootstrap de "
              f"Rademacher: p {N('VL1_EMP_PSR')} (ciclos 1–3) e {N('VL1_C2_PSR')} (ciclo 2). Adendos 52g e 52h: "
              "auditoria pendente. Tudo pós-resultado, condicional a se candidatar; pacote do corte. Os nomes das "
              "linhas da figura foram trocados a pedido da banca (o 'perto do corte' virou 'IVS a ±0,05 de um "
              "corte'); as estimativas são as mesmas do deck anterior.")


def s_conclusao(sl, N, c):
    titulo(sl, "Conclusão: a bolsa maior aumenta a 1ª opção? Sim")
    g = {sh.name: sh for sh in sl.shapes}
    trocar(g["Número Resposta"], [f"×{N('VL1_EMP_RC')}", "+R$ 5 mil, vagas da mesma UF"])
    trocar(g["Texto Resposta"], ["Sim, a vaga com bolsa maior é mais escolhida",
                                 f"Entre vagas da mesma UF, R$ 5 mil a mais multiplicam por {N('VL1_EMP_RC')} a chance "
                                 f"de a vaga ser a 1ª opção (IC 95%: {N('VL1_EMP_RCI')} a {N('VL1_EMP_RCS')})."])
    trocar(g["Número Força"], [f"×{N('VL1_C2_RC')}", "2º ciclo, vagas da mesma UF"])
    trocar(g["Texto Força"], ["O efeito é forte só no 2º ciclo",
                              f"No 2º ciclo, IC 95% de {N('VL1_C2_RCI')} a {N('VL1_C2_RCS')}. Nos ciclos 1 e 3, "
                              f"×{N('VG1_RC')} e ×{N('VG3_RC')}, com IC que contém 1."])
    trocar(g["Número Teoria"], [f"{N('VL1_EMP_K5')} km", "é o que R$ 5 mil compensam"])
    trocar(g["Texto Teoria"], ["A bolsa compensa parte do custo do lugar",
                               f"Os dados sugerem: R$ 5 mil a mais pesam o mesmo que uma vaga {N('VL1_EMP_K5')} km "
                               f"mais perto (IC 95%: {N('VL1_EMP_K5I')} a {N('VL1_EMP_K5S')} km)."])
    pol = g["Text 21"]
    trocar_ultima(pol, "a bolsa maior reordena a escolha entre vagas da mesma UF; não mostramos que leve mais "
                       "médicos ao município.")
    rodape(sl, "VL_estimativas.csv (VL-1, adendo 52e; auditoria 48); VG_estimativas.csv (adendo 52g; auditoria "
               "pendente); modelo da banca 1; auditoria 50.")
    navbar(sl, "Discussão")
    notas(sl, f"Roteiro (35 s). Voltando à pergunta: sim. Entre vagas da mesma UF, R$ 5 mil a mais multiplicam por "
              f"{N('VL1_EMP_RC')} a chance de a vaga ser a 1ª opção, e o efeito é forte só no ciclo 2. Pela teoria "
              "da banca 1, o médico aceita a vaga se a bolsa compensa o custo do lugar; os dados sugerem que R$ 5 mil "
              f"compensam parte desse custo, o equivalente a uma vaga {N('VL1_EMP_K5')} km mais perto. Para a "
              "política: a bolsa reordena a escolha entre vagas da mesma UF; isso não mostra mais médicos chegando "
              "ao município.\n\nA leitura pela teoria é interpretação, não teste (auditoria 50). Saiu do deck a "
              "comparação origem × toda a bolsa (×11 contra ×1,57): ela compara a UF de trabalho anterior com outras "
              "UFs, fora da hipótese de 28/10/2026, e vinha do modelo base, não do VL-1. Contraste: pacote do corte, "
              "não participação no PMM-E. Condicional a se candidatar.")


def s_limitacoes(sl, N):
    g = {sh.name: sh for sh in sl.shapes}
    trocar(g["Título 1"], ["Escolhida depois de ver os dados"])
    trocar(g["Problema 1"], ["A comparação só entre vagas da mesma UF (×" + N("VL1_EMP_RC") + ") foi escolhida "
                             "depois de vermos os dados."])
    trocar(g["Título 2"], ["Sem o par de UFs, o IC contém 1"])
    trocar(g["Problema 2"], [f"Na especificação pré-registrada, que compara vagas de todas as UFs: ×{N('VLB_EMP_RC')} "
                             f"(IC 95%: {N('VLB_EMP_RCI')} a {N('VLB_EMP_RCS')})."])
    trocar_ultima(g["Implicação 2"], "Não dá para descartar efeito nulo nessa versão.")
    trocar(g["Problema 5"], [f"No 2º ciclo, ×{N('VL1_C2_RC')}; no 1º (×{N('VG1_RC')}) e no 3º (×{N('VG3_RC')}), o IC "
                             "contém 1."])
    trocar(g["Título 6"], ["Local de trabalho anterior vem do CNES"])
    trocar(g["Problema 6"], ["É onde o médico tinha vínculo antes da inscrição, não onde mora; só define o par de UFs "
                             "fixado."])
    trocar_ultima(g["Implicação 6"], "É pareamento, não resultado nem causa.")
    for nome, alt in (("Ícone 1", "Escolhida depois de ver os dados"), ("Ícone 2", "Sem o par de UFs, o IC contém 1"),
                      ("Ícone 6", "Local de trabalho anterior vem do CNES")):
        g[nome]._element.xpath("./*[1]/p:cNvPr")[0].set("descr", alt)
    rodape(sl, "VL_estimativas.csv (VL-1 e M1, adendo 52e); VG_estimativas.csv (adendo 52g); auditorias 18 e 48; "
               "portão G1.")
    navbar(sl, "Discussão")
    notas(sl, "Roteiro (45 s). Seis limitações e o que cada uma implica. A especificação é pós-resultado: o "
              "resultado é exploratório e pede dados novos. Sem o par de UFs, como no pré-registrado, o intervalo "
              "contém 1. Só vemos a inscrição: a vaga marcada, não quem foi trabalhar no município. O corte muda um "
              "pacote de regras: medimos o pacote, não os R$ 5 mil sozinhos. O efeito é forte só no ciclo 2: não dá "
              "para generalizar. E o local de trabalho anterior vem do CNES, não é a residência. Obrigado.\n\n"
              f"Pré-registrada (P1a, M1 sem o par): ×{N('VLB_EMP_RC')} [{N('VLB_EMP_RCI')}; {N('VLB_EMP_RCS')}], "
              f"p {N('VC_B_HOLM')} (família de um teste). Por ciclo (adendo 52g, auditoria pendente): ciclo 1 "
              f"{N('VG1_RC')} [{N('VG1_RCI')}; {N('VG1_RCS')}], ciclo 3 {N('VG3_RC')} [{N('VG3_RCI')}; "
              f"{N('VG3_RCS')}]. Correção em relação ao deck de 04/11: os '+7% e 0%' dos ciclos 1 e 3 eram do modelo "
              "base, não do VL-1. Se perguntarem pela origem: no modelo base, sem o par, o teste origem × toda a bolsa "
              f"(D_UF) dá {N('VC_DUF_EST')} [{N('VC_DUF_INF')}; {N('VC_DUF_SUP')}] em log-chance (doc 57p); não é "
              "interpretado aqui.")


def s_qa(sl):
    remover(sl, [sh for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.startswith("Click to edit")])


def s_apendice_regra(sl, N):
    titulo(sl, "Apêndice A1: a bolsa segue exatamente o IVS")
    t2 = achar(sl, "I. Bolsa")
    trocar(t2, ["Bolsa anunciada e IVS 2010 oficial, ciclo 1"])
    trocar_ultima(achar(sl, "A regra é exata"), f"o IVS reproduz a faixa de {N('R_C1_REPR')} de {N('R_C1_MUN')} "
                                                f"municípios no ciclo 1 e de {N('R_C2_REPR')} de {N('R_C2_MUN')} no "
                                                "ciclo 2. O município não escolhe a bolsa.")
    navbar(sl, None)
    numero(sl, "A1")
    notas(sl, "Apêndice, para perguntas sobre a regra. Cada ponto é um município com vaga no quadro da 1ª chamada do "
              "ciclo 1; até 0,300, R$ 10 mil; até 0,400, R$ 15 mil; acima, R$ 20 mil. No ciclo 3, 747 de 748: o que "
              "falta foi criado depois de 2010. Saiu do corpo do deck a pedido da banca: o gráfico criava expectativa "
              "de uma RDD, e o desenho é um modelo de escolha; a regra está no slide de motivação.")


def s_apendice_h3(sl):
    titulo(sl, "Apêndice A2: metade de quem entra já estava no município")
    trocar(achar(sl, "Antiga H3"), ["Descritivo, fora da hipótese"])
    # sai o 3º cartão (ligava o fato ao "×11" da origem) e a cautela repetida; os dois cartões restantes alargam
    remover(sl, por_id(sl, 82, 83, 84, 85, 86, 87, 88))
    d = Inches(2.1)
    for sh in por_id(sl, 72, 75, 76):
        sh.width = sh.width + d
    for sh in por_id(sl, 77, 78, 79, 80, 81):
        sh.left = sh.left + d
    for sh in por_id(sl, 77, 80, 81):
        sh.width = sh.width + d
    navbar(sl, None)
    numero(sl, "A2")
    limpar_rels(sl)
    notas(sl, "Apêndice (antiga H3, fora do corpo por decisão do autor de 27/10/2026). As horas cadastradas do médico "
              "do PMM-E sobem +6,6 h/sem [+5,4; +7,8] depois da entrada, e 51,0% [48,4; 53,7] já tinham vínculo no "
              "município do posto. Descritivo: o mesmo médico antes e depois, sem grupo de comparação; não é efeito "
              "da bolsa nem da participação no PMM-E. Horas cadastradas não são presença. Saiu o cartão que ligava "
              "isso ao '×11' da origem, que não está mais no deck.")


# ---------------------------------------------------------------------------

def _zip_deterministico(p: Path) -> None:
    """Regrava o pacote com data fixa nas entradas, para o mesmo insumo dar o mesmo arquivo."""
    import zipfile
    with zipfile.ZipFile(p) as z:
        itens = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    with zipfile.ZipFile(p, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dados in itens:
            info = zipfile.ZipInfo(nome, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, dados)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def figura_robustez(N) -> dict:
    spec = importlib.util.spec_from_file_location("gfb2", RAIZ / "scripts" / "apresentacao" / "gerar_figuras_banca2.py")
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    rot = ("Principal: vagas da mesma UF", "Distância em log, não em km", "Região de saúde × UF da vaga",
           "Só IVS a ±0,05 de um corte", "Idem, com região de saúde", "Só o degrau R$ 10 → 15 mil",
           "Só o degrau R$ 15 → 20 mil")
    ler = ["todas comparam vagas da mesma UF. Verde: IC 95% exclui 1; cinza: contém 1 (inconclusivo).",
           "±0,05: só municípios com IVS a até 0,05 de um corte (menos vagas, IC mais largo)."]
    return g.figura_robustez_escolha(N.reg, FIG_ROB, rotulos=rot, como_ler=ler)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--deck-grupo", type=Path, default=DECK_GRUPO)
    ap.add_argument("--sem-pdf", action="store_true")
    args = ap.parse_args()
    if sha256(args.deck_grupo) != SHA_GRUPO:
        raise SystemExit("ERRO: o deck do grupo não é o apresentado em 04/11/2026 (hash diferente)")
    N = Numeros()
    c = N.conferir()
    reg_fig = figura_robustez(N)

    prs = Presentation(str(args.deck_grupo))
    sl = list(prs.slides)
    if len(sl) != 15:
        raise SystemExit("ERRO: o deck do grupo deveria ter 15 slides")
    capa, motiv, dados_ant, regra, descr, perto, metod, ident, result, incent, h3, robus, concl, limit, qa = sl
    modelo = ident
    novos = {k: nova_lamina(prs, modelo) for k in ("hip", "dados", "modelo", "porque", "ident", "result")}

    s_motivacao(motiv, N)
    s_hipotese(novos["hip"], N)
    s_dados(novos["dados"], N, c)
    s_descritiva(descr, N)
    s_modelo(novos["modelo"], N, c)
    s_por_que(novos["porque"], N)
    s_identificacao(novos["ident"], N, c)
    s_resultados(novos["result"], N, c)
    s_robustez(robus, N, c, FIG_ROB)
    s_conclusao(concl, N, c)
    s_limitacoes(limit, N)
    s_qa(qa)
    s_apendice_regra(regra, N)
    s_apendice_h3(h3)

    ordem = [capa, motiv, novos["hip"], novos["dados"], descr, novos["modelo"], novos["porque"], novos["ident"],
             novos["result"], robus, concl, limit, qa, regra, h3]
    sai = [dados_ant, perto, metod, ident, result, incent]
    for k, s in enumerate(ordem[1:13], start=2):
        numero(s, str(k))

    lst = prs.slides._sldIdLst
    por_parte = {}
    for sid in list(lst):
        por_parte[id(prs.part.related_part(sid.get(qn("r:id"))))] = sid
    for s in sai:
        sid = por_parte[id(s.part)]
        prs.part.drop_rel(sid.get(qn("r:id")))
        lst.remove(sid)
    for s in ordem:
        sid = por_parte[id(s.part)]
        lst.remove(sid)
        lst.append(sid)

    SAIDA.mkdir(parents=True, exist_ok=True)
    prs.save(str(DECK))
    _zip_deterministico(DECK)
    com_pdf = False
    if not args.sem_pdf:
        spec = importlib.util.spec_from_file_location("gdb2", RAIZ / "scripts" / "apresentacao" / "gerar_deck_banca2.py")
        gd = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gd)
        com_pdf = gd.converter_pdf(DECK, PDF)
    titulos = []
    for s in Presentation(str(DECK)).slides:
        t = next((sh.text_frame.text for sh in s.shapes if sh.is_placeholder and sh.has_text_frame
                  and "TITLE" in str(sh.placeholder_format.type)), "")
        titulos.append(t)
    man = {
        "natureza_dos_dados": "EMPIRICO",
        "script": "scripts/apresentacao/gerar_deck_banca2_pos_banca.py",
        "pedido": "autor, 04/11/2026: corrigir o deck apresentado e ajustar o que os professores pediram na banca 2 "
                  f"(registro em {DOC12})",
        "regra": "nada estimado; números lidos de output/ (numeros_banca2.json, VL_estimativas.csv, VL_resumo.json); "
                 "contas de leitura conferidas contra VL1_EMP_RC e VL1_EMP_K5; figura de robustez do pipeline",
        "entradas": [{"caminho": str(p.relative_to(RAIZ)), "sha256": sha256(p)}
                     for p in (args.deck_grupo, NUMEROS, VL_EST, VL_RES)],
        "contas_de_leitura": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in c.items()},
        "codigos_usados": sorted(N.usados),
        "figura_robustez": {"arquivo": str(FIG_ROB.relative_to(RAIZ)), "sha256": sha256(FIG_ROB),
                            "textos": reg_fig["textos"]},
        "slides": [{"n": k + 1, "titulo": t} for k, t in enumerate(titulos)],
        "deck": {"arquivo": str(DECK.relative_to(RAIZ)), "sha256": sha256(DECK)},
        "pdf": ({"arquivo": str(PDF.relative_to(RAIZ)), "sha256": sha256(PDF)} if com_pdf else None),
    }
    MANIFESTO.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("gerado:", DECK.relative_to(RAIZ), "e", PDF.relative_to(RAIZ) if com_pdf else "(sem PDF)")
    for k, t in enumerate(titulos, 1):
        print(f"  {k:2d}. {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
