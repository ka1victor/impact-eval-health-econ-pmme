"""Deck da banca final sobre a versão do grupo de 11/11/2026 (pedido do autor de 11/11/2026, noite).

Parte de `docs/07_apresentacoes/banca_final/grupo/deck_grupo_banca_final_1111.pptx` (33 slides, 1 oculto) e:
- mantém motivação, pergunta, sumários, base de dados, análise descritiva, Q&A e anexos do grupo, com três correções
  (faixas da bolsa pelo IVS efetivo, erros de digitação e a cláusula 11.1.4 nas fontes);
- troca literatura (cadeia causal em dois slides), hipótese, modelo, método, identificação, resultados, robustez,
  discussão, conclusão e limitações por slides novos, no estilo do grupo;
- acrescenta um slide de dados (linhas candidato × vaga) e tira os rascunhos do grupo (slide em branco, duplicata,
  slide oculto e caixas de comentário).

Conteúdo canônico: `docs/07_apresentacoes/banca_final/03_deck_banca_final_grupo.md`. Números lidos de `output/`:
VL_estimativas.csv, VL_resumo.json, VG_estimativas.csv, P1_resumo.json, P1_estimativas.csv, S57_resumo.json,
portao_r1_ivs_oficial.json, exemplo_logit_real.json e as figuras de `gerar_figuras_banca_final.py`.

Uso
---
    python3 scripts/apresentacao/gerar_exemplo_logit_real.py      # exemplo real (≈ 30 s)
    python3 scripts/apresentacao/gerar_figuras_banca_final.py     # figuras
    python3 scripts/apresentacao/gerar_deck_banca_final_grupo.py  # .pptx, .pdf e manifesto
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pandas as pd
from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
ENT = ROOT / "docs/07_apresentacoes/banca_final/grupo/deck_grupo_banca_final_1111.pptx"
SHA_ENT = "4f645142053adb33cbac43173b291cff2af94ac86bcd1a161b1bed53e9044cd5"
N_ENT = 33
OUT = ROOT / "output/apresentacao_banca_final"
ARQ = "deck_banca_final_grupo"
RD = ROOT / "output/rdd_bolsa"
F_VL, F_VLR, F_VG = RD / "VL_estimativas.csv", RD / "VL_resumo.json", RD / "VG_estimativas.csv"
F_P1R, F_P1E, F_S57 = RD / "P1_resumo.json", RD / "P1_estimativas.csv", RD / "S57_resumo.json"
F_R1 = RD / "portao_r1_ivs_oficial.json"
F_EX = OUT / "exemplo_logit_real.json"
FIG_COEF, FIG_ROB = OUT / "figuras/coeficientes_vl1.png", OUT / "figuras/robustez_vl1.png"
DOC = "docs/07_apresentacoes/banca_final/03_deck_banca_final_grupo.md"

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
SECOES = ("Motivação", "Pergunta", "Literatura", "Hipótese", "Base de Dados", "Análise Descritiva", "Metodologia",
          "Identificação", "Resultados", "Robustez", "Discussão")
VERDE, VERDE2, MEDIO, CLARO, BORDA = "114719", "056429", "2E7D46", "EEF3ED", "D5E2D8"
TEXTO, CINZA, BRANCO, APAGADO, FUNDO_AP = "1A1A1A", "5E6660", "FFFFFF", "B9C1BB", "F5F7F5"
PILL = {"reduz": ("F5B5B0", "7A1C17"), "eleva": ("B9E4B1", VERDE), "testado": (MEDIO, BRANCO),
        "pareamento": ("B9E4B1", VERDE), "controle": ("DDE3DE", "39413B"), "suposto": ("DDE3DE", "39413B"),
        "parte": ("F6DDB0", "6B4A0B"), "nao": ("F5B5B0", "7A1C17"), "obs": ("B9E4B1", VERDE),
        "naoobs": ("DDE3DE", "39413B")}

# ("G", n): slide n do deck do grupo (ordem de apresentação); ("N", nome): slide novo. Seção do rodapé.
ORDEM = [
    ("G", 1, None), ("G", 2, None), ("G", 3, "Motivação"), ("G", 4, "Motivação"), ("G", 5, "Motivação"),
    ("G", 6, "Motivação"), ("G", 7, "Motivação"), ("G", 8, None), ("G", 9, None), ("G", 10, None),
    ("G", 11, "Literatura"), ("N", "cadeia1", "Literatura"), ("N", "cadeia2", "Literatura"),
    ("G", 13, None), ("N", "hipotese", "Hipótese"),
    ("G", 15, None), ("G", 16, "Base de Dados"), ("N", "linhas", "Base de Dados"),
    ("G", 17, "Análise Descritiva"),
    ("G", 18, None), ("N", "modelo", "Metodologia"), ("N", "passos", "Metodologia"),
    ("N", "identificacao", "Identificação"),
    ("G", 23, None), ("N", "resultados", "Resultados"), ("N", "robustez", "Robustez"),
    ("N", "metade", "Discussão"), ("N", "conclusao", "Discussão"), ("N", "limitacoes", "Discussão"),
    ("G", 31, None), ("G", 32, None), ("G", 33, None),
]
FORA = {
    12: "rascunho em branco do grupo (só o título)",
    14: "hipótese em sobreposição: trocada pelo slide novo de hipótese (pedido de 11/11)",
    19: "modelo com a equação da utilidade: trocado pelo logit condicional (erro corrigido, pedido de 11/11)",
    20: "duplicata do 19 com marcas de edição",
    21: "slide oculto do grupo ('As premissas aplicadas ao nosso caso'), rascunho da identificação",
    22: "identificação: trocada pela versão só com as premissas do logit condicional",
    24: "resultado com cautela e anotação do grupo: trocado pelo slide de resultados com gráfico",
    25: "'incentivo limitado': fundido na conclusão (pedido: menos blocos)",
    26: "tabela de coeficientes: trocada por gráfico (pedido de 11/11)",
    27: "'metade de quem chega': refeito na discussão (anotação do grupo: estética)",
    28: "robustez: refeita com a conclusão explícita (anotação do grupo) e a leitura do ×",
    29: "conclusão: refeita com menos blocos",
    30: "limitações: refeitas em duas caixas",
}
# Anotações do grupo sobre os slides (caixas de comentário), retiradas dos slides mantidos
ANOTACOES = ("Esse tá ruim", "Estética ruim", "Evidenciarqal", "Escolha das palavras")

# Correções nos slides mantidos do grupo, por parágrafo: (slide, texto antigo, texto novo). As faixas passam a ser
# as do IVS efetivo (cortes em 0,300 e 0,400; portão R1), porque a legenda do mapa no mesmo slide chama 0,301–0,400 de
# "média"; o item 11.1.4 do edital é a grade do FAQ, que não é a aplicada (errata E10).
_FAIXAS = (
    (" (item 11.1.4)", ""),
    ("renumeração", "remuneração"),
    ("por categoria do Índice de Vulnerabilidade Social", "pela faixa do IVS 2010 do município"),
    ("Vulnerabilidade: Muito alta", "IVS acima de 0,400"),
    ("Vulnerabilidade: Alta", "IVS de 0,301 a 0,400"),
    ("Vulnerabilidade: Média, ", "IVS até 0,300"),
    ("baixa e buito baixa", ""),
    ("sobre a categoria de IVS do município.", "pelo IVS 2010 do município: cortes em 0,300 e 0,400."),
)
CORRECOES = [(n, a, b) for n in (4, 5, 6) for a, b in _FAIXAS] + [
    (17, "Os médicos escolhem vagas perto de onde já trabalham", "3 em 4 escolhem uma vaga a até 189 km"),
]


# --------------------------------------------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------------------------------------------
def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def v(x: float, casas: int = 2) -> str:
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "−")


def mil(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def formas(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            yield from formas(sh.shapes)
        else:
            yield sh


def remover(sh) -> None:
    sh._element.getparent().remove(sh._element)


def numeros() -> dict:
    """Todo número dos slides novos sai daqui, lido de output/."""
    d = pd.read_csv(F_VL)
    c = d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "coeficiente")].set_index("termo")
    rc = d[(d.tipo_linha == "razao_chances_por_5mil")].set_index("chave_modelo")
    b, dist = float(c.loc["bolsa_mil", "estimativa"]), float(c.loc["distancia_100km", "estimativa"])
    km = d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha.astype(str).str.contains("km"))]
    vg = pd.read_csv(F_VG)
    rcg = vg[vg.tipo_linha == "razao_chances_por_5mil"].set_index("chave_modelo")
    vlr = json.loads(F_VLR.read_text(encoding="utf-8"))
    idt = vlr["identificacao"]["VL1_emp"]["identificacao"]
    p1 = json.loads(F_P1R.read_text(encoding="utf-8"))["amostra"]
    r1 = sum(p1["r1_por_ciclo"].values())
    sem_origem = sum(sum(x.values()) for k, x in p1["exclusoes"].items() if k.startswith("sem município de origem"))
    p1e = pd.read_csv(F_P1E)
    sel = lambda m, t: p1e[(p1e.modelo == m) & (p1e.ciclo == "empilhado") & (p1e.termo == t) &
                           (p1e.tipo_linha == "coeficiente")].iloc[0]
    s57 = json.loads(F_S57.read_text(encoding="utf-8"))["v"]
    r1g = json.loads(F_R1.read_text(encoding="utf-8"))["populacoes"]
    ex = json.loads(F_EX.read_text(encoding="utf-8"))
    n = {
        "b": b, "dist": dist, "b5": 5 * b,
        "rc": float(rc.loc["VL1_emp", "estimativa"]), "rc_inf": float(rc.loc["VL1_emp", "ic95_inf"]),
        "rc_sup": float(rc.loc["VL1_emp", "ic95_sup"]), "p_holm": float(rc.loc["VL1_emp", "p_holm"]),
        "rc_c2": float(rc.loc["VL1_c2", "estimativa"]), "rc_c2_inf": float(rc.loc["VL1_c2", "ic95_inf"]),
        "rc_c2_sup": float(rc.loc["VL1_c2", "ic95_sup"]),
        "rc_c1": float(rcg.loc["VG1", "estimativa"]), "rc_c3": float(rcg.loc["VG3", "estimativa"]),
        "rc_m1": float(rc.loc["M1_emp", "estimativa"]), "rc_m1_inf": float(rc.loc["M1_emp", "ic95_inf"]),
        "rc_m1_sup": float(rc.loc["M1_emp", "ic95_sup"]),
        "rc_log": float(rc.loc["VL1log_emp", "estimativa"]), "rc_vl3": float(rc.loc["VL3_VL1_emp", "estimativa"]),
        "rc_vl2": float(rc.loc["VL2_emp", "estimativa"]),
        "km": 5 * b / -dist * 100, "km_c2": float(vlr["leitura"]["VL4"]["VL1_c2"]["km"]),
        "x_dist": math.exp(dist), "x_reg": math.exp(float(c.loc["mesma_regiao_saude", "estimativa"])),
        "x_mun": math.exp(float(c.loc["mesmo_municipio", "estimativa"])),
        "n_cand": int(c.loc["bolsa_mil", "n_candidatos"]), "n_lin": int(c.loc["bolsa_mil", "n_linhas_candidato_celula"]),
        "pares_var": idt["pares_com_variacao_de_bolsa"], "cand_var": idt["candidatos_com_variacao_de_bolsa_em_algum_par"],
        "ret_uma": idt["candidatos_retirados_uma_so_alternativa"],
        "r1": r1, "com_cnes": r1 - sem_origem, "m1_cand": vlr["identificacao"]["VL1_emp"]["identificacao"]
        ["candidatos_no_desenho"],
        "b_m1": float(sel("M1", "bolsa_mil").coef), "b_m9": float(sel("M9", "bolsa_mil").coef),
        "lambda": float(sel("M9", "lambda").coef),
        "r1_c1": r1g["P1"]["regra_reproduz"], "n_c1": r1g["P1"]["municipios"],
        "r1_c2": r1g["P2"]["regra_reproduz"], "n_c2": r1g["P2"]["municipios"],
        "origem": s57["p4_origem"]["v"], "origem_lo": s57["p4_origem_lo"]["v"], "origem_hi": s57["p4_origem_hi"]["v"],
        "horas": s57["p4_ht_att"]["v"], "horas_lo": s57["p4_ht_lo"]["v"], "horas_hi": s57["p4_ht_hi"]["v"],
        "ex": ex,
    }
    if abs(math.exp(5 * b) - n["rc"]) > 1e-6:
        raise SystemExit("ERRO: e^(5β) não reproduz a razão de chances gravada")
    if n["m1_cand"] != 5421 or n["n_cand"] != 5417:
        raise SystemExit("ERRO: tamanhos de amostra diferentes dos documentados")
    if not km.empty and abs(float(km.iloc[0].estimativa) - n["km"]) > 1e-6:
        raise SystemExit("ERRO: km equivalentes diferentes do gravado")
    if abs(ex["conta"]["beta_bolsa_por_mil"] - b) > 1e-10:
        raise SystemExit("ERRO: o exemplo real não usa o β gravado")
    linhas = ex["linhas"]
    n["lin_media"], n["lin_med"] = linhas["linhas_por_candidato"]["media"], linhas["linhas_por_candidato"]["mediana"]
    n["lin_min"], n["lin_max"] = linhas["linhas_por_candidato"]["minimo"], linhas["linhas_por_candidato"]["maximo"]
    if linhas["linhas_modelo"] != n["n_lin"]:
        raise SystemExit("ERRO: linhas do exemplo diferentes das do VL-1")
    return n


# --------------------------------------------------------------------------------------------------------------
# Primitivas de desenho (estilo do grupo: Montserrat, verde-escuro, cartões claros)
# --------------------------------------------------------------------------------------------------------------
def caixa(sl, x, y, w, h, pars, fill=None, line=None, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT,
          forma=MSO_SHAPE.ROUNDED_RECTANGLE, nome="Caixa", margem=0.14, esp=None):
    """pars: lista de parágrafos; cada um, lista de (texto, tamanho, negrito, cor[, fonte, itálico, baseline])."""
    sh = sl.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name = nome
    if forma == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = 0.08 if min(w, h) > 0.6 else 0.25
    if fill:
        sh.fill.solid()
        sh.fill.fore_color.rgb = RGBColor.from_string(fill)
    else:
        sh.fill.background()
    if line:
        sh.line.color.rgb = RGBColor.from_string(line)
        sh.line.width = Pt(1)
    else:
        sh.line.fill.background()
    sh.shadow.inherit = False
    tf = sh.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(margem)
    tf.margin_top = tf.margin_bottom = Inches(0.05)
    for k, par in enumerate(pars):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.alignment = align
        if esp:
            p.space_after = Pt(esp)
        for item in par:
            texto, tam, neg, cor = item[:4]
            fonte = item[4] if len(item) > 4 and item[4] else "Montserrat"
            ital = item[5] if len(item) > 5 else False
            base = item[6] if len(item) > 6 else 0
            r = p.add_run()
            r.text = texto
            r.font.size = Pt(tam)
            r.font.bold = neg
            r.font.italic = ital
            r.font.name = fonte
            r.font.color.rgb = RGBColor.from_string(cor)
            if base:
                r._r.get_or_add_rPr().set("baseline", str(base))
    return sh


def texto(sl, x, y, w, h, pars, **kw):
    kw.setdefault("forma", MSO_SHAPE.RECTANGLE)
    kw.setdefault("margem", 0.0)
    return caixa(sl, x, y, w, h, pars, **kw)


def pill(sl, x, y, w, rotulo, tipo, h=0.26, tam=9):
    f, c = PILL[tipo]
    return caixa(sl, x, y, w, h, [[(rotulo, tam, True, c)]], fill=f, align=PP_ALIGN.CENTER, margem=0.04,
                 nome=f"Etiqueta {rotulo}")


def seta(sl, x1, y1, x2, y2, cor=VERDE, larg=2.0):
    ln = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = RGBColor.from_string(cor)
    ln.line.width = Pt(larg)
    lnx = ln.line._get_or_add_ln()
    tail = etree.SubElement(lnx, "{%s}tailEnd" % NS["a"])
    tail.set("type", "triangle")
    tail.set("w", "med")
    tail.set("len", "med")
    return ln


def linha(sl, x1, y1, x2, y2, cor=TEXTO, larg=1.0):
    ln = sl.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = RGBColor.from_string(cor)
    ln.line.width = Pt(larg)
    return ln


def subtitulo(sl, x, y, w, titulo, sub=None):
    texto(sl, x, y, w, 0.32, [[(titulo, 15, True, TEXTO)]])
    if sub:
        texto(sl, x, y + 0.31, w, 0.28, [[(sub, 11.5, False, "333333")]], anchor=MSO_ANCHOR.TOP)


def fontes(sl, t: str) -> None:
    texto(sl, 0.2, 6.97, 12.3, 0.24, [[(t, 8, False, CINZA)]], nome="Fontes")


def eq(texto_eq: str, tam: float, cor: str = TEXTO) -> list:
    """Equação em runs de Cambria Math, como o grupo: _{...} subscrito, ^{...} sobrescrito, `...` sem itálico."""
    runs, pos = [], 0
    for m in re.finditer(r"_\{([^}]*)\}|\^\{([^}]*)\}|`([^`]*)`", texto_eq):
        if m.start() > pos:
            runs.append((texto_eq[pos:m.start()], tam, False, cor, "Cambria Math", True, 0))
        if m.group(1) is not None:
            runs.append((m.group(1), tam, False, cor, "Cambria Math", True, -25000))
        elif m.group(2) is not None:
            runs.append((m.group(2), tam, False, cor, "Cambria Math", True, 30000))
        else:
            runs.append((m.group(3), tam, False, cor, "Cambria Math", False, 0))
        pos = m.end()
    if pos < len(texto_eq):
        runs.append((texto_eq[pos:], tam, False, cor, "Cambria Math", True, 0))
    return runs


def negrito(t: str, tam: float, cor: str, cor_neg: str | None = None) -> list:
    """'**x**' em negrito dentro do texto."""
    out = []
    for k, parte in enumerate(t.split("**")):
        if parte:
            out.append((parte, tam, k % 2 == 1, cor_neg if (k % 2 == 1 and cor_neg) else cor))
    return out


# --------------------------------------------------------------------------------------------------------------
# Esqueleto de slide novo (layout, título, número e rodapé copiados do slide 16 do grupo)
# --------------------------------------------------------------------------------------------------------------
class Modelo:
    def __init__(self, prs):
        s16 = prs.slides[15]
        self.layout = s16.slide_layout
        self.rodape = next(sh for sh in s16.shapes if sh.name == "CaixaDeTexto 4")
        self.numero = next(sh for sh in s16.shapes if sh.name == "Slide Number Placeholder 0")
        self.titulo = next(sh for sh in s16.shapes if sh.name == "Text 1")

    def novo(self, prs, titulo: str):
        sl = prs.slides.add_slide(self.layout)
        for sh in list(sl.shapes):
            remover(sh)
        el = copy.deepcopy(self.titulo._element)
        sl.shapes._spTree.append(el)
        el.findall(".//a:t", NS)[0].text = titulo
        sl.shapes._spTree.append(copy.deepcopy(self.rodape._element))
        sl.shapes._spTree.append(copy.deepcopy(self.numero._element))
        return sl


def rodape(slide, secao: str | None) -> None:
    alvo = [sh for sh in formas(slide.shapes) if sh.has_text_frame
            and sh.text_frame.text.replace(" ", " ").strip().startswith("Motivação") and "|" in sh.text_frame.text]
    if not alvo:
        return
    if len(alvo) != 1:
        raise SystemExit(f"ERRO: mais de um rodapé de navegação: {[s.name for s in alvo]}")
    sh = alvo[0]
    sh.width = Inches(12.2)
    p = sh.text_frame.paragraphs[0]._p
    for ex in sh.text_frame.paragraphs[1:]:
        ex._p.getparent().remove(ex._p)
    modelo = copy.deepcopy(p.find("a:r/a:rPr", NS))
    for r in p.findall("a:r", NS) + p.findall("a:br", NS):
        p.remove(r)

    def run(t: str, destaque: bool):
        r = etree.SubElement(p, "{%s}r" % NS["a"])
        rpr = copy.deepcopy(modelo)
        rpr.attrib.pop("b", None)
        rpr.set("sz", "1000")
        for f in rpr.findall("a:solidFill", NS):
            rpr.remove(f)
        if destaque:
            rpr.set("b", "1")
            sf = etree.Element("{%s}solidFill" % NS["a"])
            etree.SubElement(sf, "{%s}srgbClr" % NS["a"]).set("val", VERDE)
            rpr.insert(0, sf)
        r.append(rpr)
        etree.SubElement(r, "{%s}t" % NS["a"]).text = t
        end = p.find("a:endParaRPr", NS)
        if end is not None:
            end.addprevious(r)

    for k, s in enumerate(SECOES):
        run(s, s == secao)
        if k < len(SECOES) - 1:
            run("  |  ", False)


def numerar(slide, n: int) -> None:
    for sh in formas(slide.shapes):
        if not sh.has_text_frame or sh.left is None or sh.top is None:
            continue
        if sh.text_frame.text.strip().isdigit() and sh.left > Inches(11.3) and sh.top > Inches(6.8):
            for t in sh._element.iter("{%s}t" % NS["a"]):
                if t.text and t.text.strip().isdigit():
                    t.text = str(n)


def notas(slide, t: str) -> None:
    ns = slide.notes_slide
    tf = ns.notes_text_frame
    if tf is None:  # o notes master do grupo não tem corpo: cria o placeholder de corpo na página de notas
        corpo = parse_xml(
            f'<p:sp xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><p:nvSpPr><p:cNvPr id="90" name="Notas"/>'
            '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="685800" y="4400550"/><a:ext cx="5486400" cy="3600450"/></a:xfrm></p:spPr>'
            '<p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')
        ns.shapes._spTree.append(corpo)
        tf = ns.notes_text_frame
    tf.text = t


# --------------------------------------------------------------------------------------------------------------
# Slides novos
# --------------------------------------------------------------------------------------------------------------
TITULO_CADEIA = "Cadeia causal: da bolsa aos desfechos na saúde"


def s_cadeia(M, prs, n, etapa: int):
    sl = M.novo(prs, TITULO_CADEIA)
    ap = etapa < 3

    def rotulo(y, num, t, apagado=False):
        cor = APAGADO if apagado else VERDE
        caixa(sl, 0.25, y, 0.42, 0.42, [[(str(num), 15, True, BRANCO)]], fill=cor, forma=MSO_SHAPE.OVAL,
              align=PP_ALIGN.CENTER, margem=0, nome=f"Etapa {num}")
        texto(sl, 0.25, y + 0.47, 1.85, 0.55, [[(t, 11, True, cor)]], anchor=MSO_ANCHOR.TOP)

    # 1. Regra
    rotulo(0.95, 1, "REGRA")
    caixa(sl, 2.2, 0.92, 3.1, 0.86, [[("IVS do município", 14, True, VERDE)],
                                     [("vulnerabilidade social (Ipea, 2010)", 11, False, TEXTO)]],
          fill=CLARO, line=BORDA)
    seta(sl, 5.32, 1.35, 5.72, 1.35)
    caixa(sl, 5.75, 0.92, 7.33, 0.86, [], fill=CLARO, line=BORDA, nome="Faixas")
    texto(sl, 5.92, 0.97, 1.85, 0.76, [[("Bolsa mensal", 14, True, VERDE)], [("fixada por regra", 11, False, TEXTO)]])
    for k, (faixa, valor) in enumerate((("IVS até 0,300", "R$ 10 mil"), ("0,301 a 0,400", "R$ 15 mil"),
                                        ("acima de 0,400", "R$ 20 mil"))):
        caixa(sl, 7.85 + k * 1.75, 1.04, 1.62, 0.62, [[(faixa, 10, False, TEXTO)], [(valor, 13, True, VERDE)]],
              fill=BRANCO, line=BORDA, align=PP_ALIGN.CENTER, margem=0.04)
    # 2. Escolha do médico: primeiro o que reduz, depois o que eleva
    rotulo(2.05, 2, "ESCOLHA DO MÉDICO")
    cart = (("reduz", "REDUZ O VALOR", "Custo de viver ali", "**Deslocamento**, moradia e distância de casa",
             "Redding & Rossi-Hansberg (2017)", False),
            ("reduz", "REDUZ O VALOR", "Custo de trabalhar ali", "**Esforço**: equipe e equipamentos que faltam",
             "Choné & Ma (2011)", False),
            ("eleva", "ELEVA O VALOR", "Remuneração", "**Bolsa** maior: salário esperado maior",
             "Moehling et al. (2020)", True))
    for k, (tp, rot, tit, corpo, ref, escuro) in enumerate(cart):
        x = 2.2 + k * 3.69
        fill, cor_t, cor_c = (VERDE, BRANCO, BRANCO) if escuro else (CLARO, VERDE, TEXTO)
        caixa(sl, x, 2.0, 3.5, 1.5, [], fill=fill, line=None if escuro else BORDA, nome=f"Fator {tit}")
        pill(sl, x + 0.15, 2.1, 1.45, rot, tp)
        texto(sl, x + 0.15, 2.42, 3.2, 0.3, [[(tit, 14, True, cor_t)]])
        texto(sl, x + 0.15, 2.72, 3.2, 0.48, [negrito(corpo, 12, cor_c)], anchor=MSO_ANCHOR.TOP)
        texto(sl, x + 0.15, 3.18, 3.2, 0.24, [[(ref, 9, True, "B9E4B1" if escuro else VERDE2)]])
        if k < 2:
            seta(sl, x + 1.75, 3.52, x + 1.75, 3.82, cor=MEDIO)
        else:
            seta(sl, x + 0.9, 3.52, 8.75, 3.84, cor=VERDE)
    # valor (não observado) → 1ª opção (observada)
    caixa(sl, 2.2, 3.85, 6.9, 0.62, [], fill=CLARO, line=VERDE, nome="Valor da vaga")
    texto(sl, 2.35, 3.88, 4.2, 0.56, [[("Valor da vaga para o médico", 14, True, VERDE)],
                                     [("a utilidade: soma do que eleva e do que reduz", 10.5, False, TEXTO)]])
    pill(sl, 7.5, 4.03, 1.45, "NÃO OBSERVADO", "naoobs")
    seta(sl, 9.12, 4.16, 9.5, 4.16)
    caixa(sl, 9.53, 3.85, 3.55, 0.62, [], fill=CLARO, line=VERDE, nome="1a opção")
    texto(sl, 9.68, 3.88, 2.2, 0.56, [[("1ª opção", 14, True, VERDE)],
                                     [("a vaga listada em 1º", 10.5, False, TEXTO)]])
    pill(sl, 11.78, 4.03, 1.18, "OBSERVADA", "obs")
    caixa(sl, 2.2, 4.57, 10.88, 0.5,
          [[("O que estimamos: ", 12.5, True, "B9E4B1"),
            ("o peso da bolsa no valor da vaga, lido nas escolhas.  ", 12.5, False, BRANCO),
            (f"+R$ 5 mil = chance ×{v(n['rc'])}  ≈  {round(n['km'])} km mais perto", 12.5, True, BRANCO)]],
          fill=VERDE, nome="Métrica")
    # 3. Da vaga à saúde
    rotulo(5.25, 3, "DA VAGA À SAÚDE", apagado=ap)
    elos = (("Quantos médicos a escolhem", ""), ("Vaga preenchida", "ao menos um médico"),
            ("Capacidade", "vínculos e horas"), ("Produção e acesso", "consultas, exames, cirurgias"),
            ("Saúde", "espera e internações"))
    for k, (tit, sub) in enumerate(elos):
        x = 2.2 + k * 2.22
        cor_t, cor_s = (APAGADO, APAGADO) if ap else (VERDE, TEXTO)
        caixa(sl, x, 5.22, 2.0, 0.84, [[(tit, 12, True, cor_t)]] + ([[(sub, 10, False, cor_s)]] if sub else []),
              fill=FUNDO_AP if ap else CLARO, line=None if ap else BORDA, nome=f"Elo {tit}")
        if k < 4:
            seta(sl, x + 2.01, 5.64, x + 2.21, 5.64, cor=APAGADO if ap else VERDE, larg=1.5)
    texto(sl, 2.2, 6.1, 10.88, 0.26,
          [[("Fora do que estimamos: ", 10.5, True, APAGADO if ap else CINZA),
            ("o trabalho testa só o elo bolsa → valor → 1ª opção.", 10.5, False, APAGADO if ap else CINZA)]])
    texto(sl, 0.25, 6.45, 12.83, 0.42,
          [[("Termos: ", 10, True, VERDE),
            ("vaga", 10, True, TEXTO), (" = estabelecimento × curso  ·  ", 10, False, TEXTO),
            ("cardápio", 10, True, TEXTO), (" = vagas que o médico podia escolher  ·  ", 10, False, TEXTO),
            ("1ª opção", 10, True, TEXTO), (" = a vaga listada em 1º  ·  ", 10, False, TEXTO),
            ("chance", 10, True, TEXTO), (" = probabilidade de a vaga ser a 1ª opção", 10, False, TEXTO)]],
          fill=None)
    fontes(sl, "Fontes: Moehling et al. (2020); Choné & Ma (2011); Redding & Rossi-Hansberg (2017); Burdett, Shi & "
               "Wright (2001); edital SGTES/MS nº 3/2025; Ipea, IVS 2010. Estimativa: VL-1, ciclos 1–3.")
    notas(sl, ("Cadeia causal, etapa por etapa. " + ("Primeiro a regra e a escolha do médico: o que reduz o valor da "
               "vaga (deslocamento, esforço) e o que o eleva (a bolsa). " if ap else "Agora a etapa 3: da vaga escolhida "
               "à saúde; não é estimada aqui. ") + "O valor da vaga é a utilidade: não aparece nos dados. O que "
               "aparece é a 1ª opção; o logit condicional lê nas escolhas quanto a bolsa pesa no valor. "
               f"Métrica: e^(5β) = {v(n['rc'])}; {round(n['km'])} km = 5β ÷ |γ| × 100. Origem: "
               "docs/07_apresentacoes/banca_final/01_diagrama_teoria_mudanca.md; VL_estimativas.csv (VL-1)."))
    return sl


def s_hipotese(M, prs, n):
    ex = n["ex"]
    a, b = ex["vaga_a"], ex["vaga_b"]
    sl = M.novo(prs, "Maior remuneração, maior chance de ser escolhida")
    caixa(sl, 0.25, 0.92, 12.83, 1.45,
          [[("HIPÓTESE", 11, True, "B9E4B1")],
           [("A vaga que paga mais tem mais chance de ser a 1ª opção do médico.", 26, True, BRANCO)],
           [("comparando vagas do mesmo curso, na mesma UF, iguais no resto", 13, False, "DDEBDD")]],
          fill=VERDE, nome="Hipótese", margem=0.3)
    subtitulo(sl, 0.25, 2.6, 12.8, "Exemplo real: o que a hipótese compara",
              f"Um médico de {ex['candidato']['curso'].title().replace(' Do ', ' do ')} que trabalhava em "
              f"{ex['candidato']['uf_de_trabalho_anterior']} (ciclo {ex['candidato']['ciclo']}), diante de duas das "
              f"vagas do seu curso")
    for k, (vg, destaque) in enumerate(((a, False), (b, True))):
        y = 3.32 + k * 0.92
        caixa(sl, 0.25, y, 6.0, 0.8,
              [[(vg["municipio"], 15, True, BRANCO if destaque else TEXTO),
                (f"   R$ {int(vg['bolsa_mil'])} mil/mês", 15, True, BRANCO if destaque else VERDE)],
               [(f"IVS {v(vg['ivs'], 3)}  ·  {round(vg['km'])} km de onde trabalhava  ·  "
                 f"{mil(round(vg['populacao_2022'] / 1000) * 1000)} hab.", 11, False, "DDEBDD" if destaque else CINZA)]],
              fill=MEDIO if destaque else CLARO, line=None if destaque else BORDA, nome=f"Vaga {k + 1}")
    seta(sl, 6.35, 4.12, 6.85, 4.12, larg=2.5)
    caixa(sl, 6.95, 3.32, 6.13, 1.72,
          [[("Hipótese no exemplo", 12, True, VERDE2)],
           [("chance(", 18, True, TEXTO), (b["municipio"].split(" (")[0], 18, True, VERDE),
            (")  >  chance(", 18, True, TEXTO), (a["municipio"].split(" (")[0], 18, True, TEXTO), (")", 18, True, TEXTO)],
           [("IVS, distância e porte quase iguais: só a bolsa muda.", 12, False, TEXTO)]],
          fill=CLARO, line=BORDA, nome="Hipótese no exemplo")
    for k, (tit, corpo) in enumerate((("O que comparamos", "vagas diferentes, para o mesmo médico, no mesmo momento"),
                                      ("O que não dizemos", "que mais médicos chegam ao município: olhamos a escolha "
                                                            "de quem se inscreveu"))):
        caixa(sl, 0.25 + k * 6.5, 5.35, 6.33, 1.0, [[(tit, 14, True, VERDE)], [(corpo, 12.5, False, TEXTO)]],
              fill=BRANCO, line=BORDA, nome=tit)
    fontes(sl, "Fontes: editais e quadros de vagas do PMM-E (SGTES/MS), ciclo 2; Ipea, IVS 2010; IBGE. Exemplo: "
               "output/apresentacao_banca_final/exemplo_logit_real.json (par escolhido por regra fixa).")
    notas(sl, "Frase central simples; o exemplo é real e volta no slide do método. As duas vagas ficam dos dois lados "
              "do corte de 0,400 e quase iguais no resto: só a bolsa muda. A medida passou para o slide de dados. "
              "Origem: exemplo_logit_real.json (regra de escolha do par no próprio arquivo).")
    return sl


def s_linhas(M, prs, n):
    ex = n["ex"]
    sl = M.novo(prs, "Cada candidato vira uma linha por vaga que podia escolher")
    subtitulo(sl, 0.25, 0.85, 7.3, "I. Formato longo: o mesmo médico do exemplo",
              f"{ex['candidato']['vagas_no_cardapio']} linhas, uma por vaga do seu cardápio; y = 1 na vaga listada em 1º")
    vagas = [(ex["vaga_escolhida"], 1), (ex["vaga_b"], 0), (ex["vaga_a"], 0)]
    tab = sl.shapes.add_table(5, 5, Inches(0.25), Inches(1.6), Inches(7.3), Inches(2.6)).table
    cab = ("Candidato", "Vaga", "Bolsa", "Distância", "1ª opção (y)")
    for j, w in enumerate((1.45, 2.55, 1.15, 1.15, 1.0)):
        tab.columns[j].width = Inches(w)
    corpo = [[f"médico ({ex['candidato']['uf_de_trabalho_anterior']})", vg["municipio"], f"R$ {int(vg['bolsa_mil'])} mil",
              f"{round(vg['km'])} km", str(y)] for vg, y in vagas]
    corpo.append(["", f"… mais {ex['candidato']['vagas_no_cardapio'] - 3} vagas", "", "", "0"])
    for i, lin in enumerate([cab] + corpo):
        for j, t in enumerate(lin):
            c = tab.cell(i, j)
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor.from_string(VERDE if i == 0 else (CLARO if i == 1 else BRANCO))
            c.text = t
            r = c.text_frame.paragraphs[0].runs[0] if c.text_frame.paragraphs[0].runs else None
            if r is None:
                continue
            r.font.size = Pt(11 if i == 0 else 12)
            r.font.bold = i == 0 or (i == 1 and j == 4)
            r.font.italic = i == 4 and j == 1
            r.font.name = "Montserrat"
            r.font.color.rgb = RGBColor.from_string(BRANCO if i == 0 else (CINZA if i == 4 else TEXTO))
            c.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT if j < 2 else PP_ALIGN.CENTER
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
    texto(sl, 0.25, 4.3, 7.3, 0.5,
          [[("Cada linha diz o que o médico ", 11.5, False, TEXTO), ("podia", 11.5, True, TEXTO),
            (" escolher e se escolheu. Atributos da vaga (bolsa, IVS, porte) e do par médico–vaga (distância, mesma "
             "região) entram como colunas.", 11.5, False, TEXTO)]], anchor=MSO_ANCHOR.TOP)
    subtitulo(sl, 7.9, 0.85, 5.2, "II. A base do modelo principal")
    for k, (num, rot) in enumerate(((mil(n["n_lin"]), "linhas candidato × vaga"),
                                    (mil(n["n_cand"]), "candidatos"))):
        caixa(sl, 7.9 + k * 2.65, 1.3, 2.5, 1.05, [[(num, 22, True, VERDE)], [(rot, 11, False, TEXTO)]],
              fill=CLARO, line=BORDA)
    texto(sl, 7.9, 2.42, 5.18, 0.34,
          [[(f"≈ {round(n['lin_media'])} vagas por candidato", 12, True, TEXTO),
            (f"  (mediana {round(n['lin_med'])}; de {n['lin_min']} a {n['lin_max']})", 11, False, CINZA)]])
    funil = ((mil(n["r1"]), "com 1ª opção nos editais (ciclos 1–3)"),
             (mil(n["com_cnes"]), "com local de trabalho anterior achado no CNES"),
             (mil(n["m1_cand"]), "com região de saúde do local anterior e da vaga"),
             (mil(n["n_cand"]), f"no modelo principal ({n['ret_uma']} ficaram com uma só vaga possível)"))
    for k, (num, rot) in enumerate(funil):
        y = 2.88 + k * 0.48
        caixa(sl, 7.9, y, 1.05, 0.4, [[(num, 13, True, BRANCO)]], fill=VERDE if k == 3 else MEDIO,
              align=PP_ALIGN.CENTER, margem=0.02)
        texto(sl, 9.05, y, 4.03, 0.4, [[(rot, 10.5, k == 3, TEXTO)]])
    texto(sl, 7.9, 4.83, 5.18, 0.45,
          [[("CNES: ", 10, True, CINZA), ("o local de trabalho anterior dá o ponto de partida da distância; quem não "
                                         "tinha vínculo médico no CNES fica fora.", 10, False, CINZA)]],
          anchor=MSO_ANCHOR.TOP)
    caixa(sl, 0.25, 5.45, 12.83, 1.1,
          [[("MEDIDA", 11, True, "B9E4B1")],
           [("Razão de chances da 1ª opção por +R$ 5 mil: ", 15, True, BRANCO),
            ("quantas vezes a chance de uma vaga ser a 1ª opção se multiplica quando ela paga R$ 5 mil a mais, "
             "contra uma vaga igual no resto. Hipótese: maior que 1.", 13, False, BRANCO)]],
          fill=VERDE, nome="Medida", margem=0.25)
    fontes(sl, "Fontes: editais e quadros de vagas do PMM-E (SGTES/MS), ciclos 1–3; CNES/DATASUS; Ipea; IBGE. "
               "P1_resumo.json; VL_resumo.json; exemplo_logit_real.json.")
    notas(sl, (f"De {mil(n['r1'])} candidatos com 1ª opção, {mil(n['com_cnes'])} têm local de trabalho anterior no CNES "
               f"(sem ele não há distância nem 'mesma região'); {mil(n['m1_cand'])} têm região de saúde na tabela "
               f"oficial; no modelo principal, que fixa o par de UFs, saem as vagas de UFs que nenhum médico da mesma "
               f"origem escolheu (não informam o peso da bolsa) e {n['ret_uma']} candidatos que ficaram com uma só "
               f"vaga: {mil(n['n_cand'])} candidatos e {mil(n['n_lin'])} linhas. A medida (antes no slide de hipótese) "
               "fica aqui, porque é construída desta base."))
    return sl


def s_modelo(M, prs, n):
    sl = M.novo(prs, "Modelo: logit condicional da 1ª opção")
    # I. A equação
    caixa(sl, 0.25, 0.9, 8.55, 2.55, [], fill=BRANCO, line=BORDA, nome="Cartão da equação")
    texto(sl, 0.45, 0.98, 6.0, 0.28, [[("I. LOGIT CONDICIONAL (McFADDEN, 1974)", 11, True, VERDE2)]])
    texto(sl, 0.45, 1.53, 2.65, 0.5, [eq("P(i escolhe v) =", 22)], align=PP_ALIGN.RIGHT)
    texto(sl, 3.2, 1.25, 5.4, 0.45, [eq("exp(V_{iv})", 22)], align=PP_ALIGN.CENTER)
    linha(sl, 3.35, 1.78, 8.45, 1.78, larg=1.25)
    texto(sl, 3.2, 1.84, 5.4, 0.5, [eq("Σ_{k ∈ cardápio de i} exp(V_{ik})", 22)], align=PP_ALIGN.CENTER)
    texto(sl, 0.45, 2.48, 8.15, 0.42,
          [eq("V_{iv} = β·bolsa_{v} + γ·dist_{iv} + f(IVS_{v}) + α_{UF(i),UF(v)} + θ·X_{iv}", 17)],
          align=PP_ALIGN.CENTER)
    texto(sl, 0.45, 2.98, 8.15, 0.36,
          [[("i: candidato  ·  v: vaga do seu curso e ciclo  ·  V: valor da vaga (a parte que os dados explicam)",
             10, False, CINZA)]], align=PP_ALIGN.CENTER)
    # O que se estima
    caixa(sl, 9.0, 0.9, 4.08, 2.55,
          [[("O QUE SE ESTIMA", 10.5, True, "B9E4B1")],
           [("Os pesos (β, γ, …) que tornam as 1ªs opções observadas as mais prováveis.", 14, True, BRANCO)],
           [("Não vemos o valor V; vemos a escolha. Os pesos saem das escolhas.", 11.5, False, "DDEBDD")]],
          fill=VERDE, anchor=MSO_ANCHOR.MIDDLE, nome="O que se estima", margem=0.22, esp=4)
    # II. Como ler cada coeficiente
    texto(sl, 0.25, 3.6, 8.55, 0.32, [[("II. Como ler cada coeficiente", 15, True, TEXTO)]])
    caixa(sl, 0.25, 3.95, 8.55, 0.5,
          [eq("P(A) ÷ P(B) = exp[ β·(bolsa_{A} − bolsa_{B}) + γ·(dist_{A} − dist_{B}) + … ]", 15)
           + [("   o cardápio se cancela", 10.5, True, VERDE2)]],
          fill=CLARO, align=PP_ALIGN.CENTER, nome="Razão")
    termos = (("β · bolsa", "testado", "TESTADO", f"+R$ 1 mil multiplica a chance relativa da vaga por e^β; "
                                                  f"+R$ 5 mil, por e^(5β)"),
              ("γ · distância", "controle", "CONTROLE", "quanto cada 100 km a mais de onde trabalhava multiplica a chance"),
              ("f(IVS)", "controle", "CONTROLE", "curva contínua do IVS: a bolsa salta no corte; a vulnerabilidade, não"),
              ("α · par de UFs", "pareamento", "PAREAMENTO", "compara só vagas da mesma UF, vistas por médicos da mesma UF"),
              ("θ · X", "controle", "CONTROLE", "mesma região de saúde, mesmo município, porte, capital, vaga imediata"))
    for k, (t, tp, rot, leitura) in enumerate(termos):
        y = 4.55 + k * 0.47
        texto(sl, 0.35, y, 1.6, 0.42, [eq(t, 14)])
        pill(sl, 1.95, y + 0.08, 1.2, rot, tp)
        texto(sl, 3.3, y, 5.5, 0.42, [[(leitura, 11, False, TEXTO)]])
        if k < 4:
            linha(sl, 0.35, y + 0.45, 8.75, y + 0.45, cor=BORDA, larg=0.75)
    # Anexo: por que este modelo
    caixa(sl, 9.0, 3.6, 4.08, 3.25, [], fill=CLARO, line=BORDA, nome="Por que este modelo")
    texto(sl, 9.18, 3.68, 3.75, 0.3, [[("POR QUE ESTE MODELO", 10.5, True, VERDE2)]])
    texto(sl, 9.18, 3.98, 3.75, 1.15,
          [[("Cada médico escolhe ", 10.5, False, TEXTO), ("uma", 10.5, True, TEXTO),
            (f" entre ≈ {round(n['lin_media'])} vagas. O modelo trata a escolha como uma disputa entre as vagas do "
             "seu cardápio: o que é do médico (nota, idade, perfil) é igual em todas e se cancela.", 10.5, False, TEXTO)]],
          anchor=MSO_ANCHOR.TOP)
    refs = (("McFadden (1974)", "o método; Nobel de Economia de 2000"),
            ("Bobba et al. (2026, NBER)", "professores no Peru escolhem vagas com bônus que salta em cortes"),
            ("Costa, Nunes & Sanches (2024, REStat)", "escolha de local por médicos no Brasil"),
            ("Holmes (2005, Labour Econ)", "logit da escolha de local de médicos nos EUA"),
            ("Scott et al. (2013); Kolstad (2011)", "experimentos de escolha com médicos"))
    texto(sl, 9.18, 4.98, 3.75, 1.8, [[(a, 10, True, VERDE), (f": {b}", 10, False, TEXTO)] for a, b in refs],
          anchor=MSO_ANCHOR.TOP, esp=2)
    fontes(sl, "Fontes: McFadden (1974); Bobba et al. (NBER WP 29068, rev. 2026); docs/03_literatura_empirica/19 e 20; "
               "protocolo 52 e adendo 52e (VL-1).")
    notas(sl, ("Correção da banca 2: antes mostrávamos a utilidade com o erro (U = … + ε) e a probabilidade sobre U. O "
               "que estimamos é a probabilidade de escolha do logit condicional: P = exp(V)/Σ exp(V), com V a parte "
               "observável do valor; o erro de cada vaga (Gumbel) é o que gera essa fórmula. Os pesos saem por máxima "
               "verossimilhança. O nível do valor não é identificado (só diferenças entre vagas, e numa escala "
               "normalizada); por isso cada coeficiente se lê pela razão de chances entre duas vagas. 'Por que este "
               "modelo' entra aqui como anexo pequeno, pedido de 11/11."))
    return sl


def s_passos(M, prs, n):
    ex = n["ex"]
    a, b, c = ex["vaga_a"], ex["vaga_b"], ex["conta"]
    sl = M.novo(prs, "Método passo a passo: da escolha à razão de chances")
    passos = (("1", "Cardápio", f"uma linha por vaga que o médico podia escolher (≈ {round(n['lin_media'])})"),
              ("2", "Escolha", "y = 1 na vaga listada em 1º; 0 nas outras"),
              ("3", "Valor", "cada vaga ganha um valor V = pesos × atributos"),
              ("4", "Chance", "chance da vaga = exp(V) ÷ soma do cardápio"),
              ("5", "Pesos", "o computador acha os pesos que tornam as 1ªs opções reais as mais prováveis"),
              ("6", "Métrica", "chance(A) ÷ chance(B): o cardápio se cancela"))
    w, gap = 1.95, 0.226
    for k, (num, tit, corpo) in enumerate(passos):
        x = 0.25 + k * (w + gap)
        final = k == 5
        caixa(sl, x, 0.92, w, 1.55, [], fill=VERDE if final else CLARO, line=None if final else BORDA,
              nome=f"Passo {num}")
        caixa(sl, x + 0.12, 1.02, 0.4, 0.4, [[(num, 13, True, VERDE if final else BRANCO)]],
              fill=BRANCO if final else VERDE, forma=MSO_SHAPE.OVAL, align=PP_ALIGN.CENTER, margem=0)
        texto(sl, x + 0.6, 1.02, w - 0.66, 0.4, [[(tit, 14, True, BRANCO if final else VERDE)]])
        texto(sl, x + 0.12, 1.5, w - 0.22, 0.95, [[(corpo, 11, False, BRANCO if final else TEXTO)]],
              anchor=MSO_ANCHOR.TOP)
        if k < 5:
            seta(sl, x + w + 0.01, 1.7, x + w + gap - 0.01, 1.7, larg=1.75)
    caixa(sl, 0.25, 2.6, 12.83, 0.34,
          [[("Passos 1–2: a base.   Passos 3–5: a estimação (máxima verossimilhança).   Passo 6: a métrica.", 11, True,
             VERDE2)]], forma=MSO_SHAPE.RECTANGLE, align=PP_ALIGN.CENTER)
    # Exemplo real
    subtitulo(sl, 0.25, 3.2, 12.8, "Exemplo real, com os pesos estimados",
              f"O médico de {ex['candidato']['uf_de_trabalho_anterior']} do slide de hipótese: "
              f"{ex['candidato']['vagas_no_cardapio']} vagas no cardápio; o modelo dá uma chance a cada uma")
    for k, (vg, cor) in enumerate(((a, CLARO), (b, CLARO))):
        y = 3.92 + k * 1.08
        caixa(sl, 0.25, y, 3.9, 0.95,
              [[(vg["municipio"], 13, True, TEXTO)],
               [(f"R$ {int(vg['bolsa_mil'])} mil  ·  IVS {v(vg['ivs'], 3)}  ·  {round(vg['km'])} km", 10.5, False, CINZA)]],
              fill=cor, line=BORDA, nome=f"Vaga ex {k}")
        caixa(sl, 4.25, y, 1.55, 0.95, [[("chance", 9.5, False, CINZA)], [(f"{v(100 * vg['chance_modelo'])}%", 20, True,
                                                                              VERDE)]],
              fill=BRANCO, line=VERDE, align=PP_ALIGN.CENTER, margem=0.04, nome=f"Chance ex {k}")
    texto(sl, 0.25, 6.1, 5.55, 0.3, [[("passo 4: exp(V) ÷ soma das 222 vagas".replace(
        "222", str(ex["candidato"]["vagas_no_cardapio"])), 10, True, VERDE2)]], align=PP_ALIGN.CENTER)
    seta(sl, 5.9, 4.95, 6.3, 4.95, larg=2.5)
    rz = c["razao_por_termo"]
    caixa(sl, 6.4, 3.92, 3.75, 2.48, [], fill=VERDE, nome="Razão do exemplo")
    texto(sl, 6.55, 3.98, 3.5, 0.3, [[("PASSO 6: A RAZÃO", 10, True, "B9E4B1")]])
    texto(sl, 6.55, 4.28, 3.5, 0.5,
          [[(f"{v(100 * b['chance_modelo'])}% ÷ {v(100 * a['chance_modelo'])}% = {v(c['razao_total'])}", 20, True,
             BRANCO)]])
    fat = ((f"×{v(rz['bolsa_mil'])}", "bolsa: +R$ 5 mil = e^(5 × β)"),
           (f"×{v(rz['distancia_100km'])}", f"distância: {round(b['km'] - a['km'])} km a mais"),
           (f"×{v(rz['ivs'] * rz['log_populacao_2022'] * rz['outros'])}", "IVS, porte e o resto: quase iguais"))
    for k, (x_, rot) in enumerate(fat):
        texto(sl, 6.55, 4.85 + k * 0.48, 3.5, 0.44,
              [[(x_, 15, True, "B9E4B1" if k == 0 else BRANCO), (f"  {rot}", 10.5, False, BRANCO)]])
    caixa(sl, 10.3, 3.92, 2.78, 1.15,
          [[("Só as duas na mesa:", 10.5, True, VERDE2)],
           [(f"{round(100 * c['chance_b_entre_as_duas'])}% contra {100 - round(100 * c['chance_b_entre_as_duas'])}%",
             17, True, TEXTO)]],
          fill=CLARO, line=BORDA, nome="Entre as duas")
    caixa(sl, 10.3, 5.17, 2.78, 1.23,
          [[("Por que razão, e não diferença?", 10.5, True, VERDE2)],
           [("Com centenas de vagas, cada chance é pequena; a razão não depende do tamanho do cardápio.", 10, False,
             TEXTO)]],
          fill=CLARO, line=BORDA, anchor=MSO_ANCHOR.TOP, nome="Por que razão")
    fontes(sl, f"Fontes: VL-1 (ciclos 1–3) reestimado em scripts/apresentacao/gerar_exemplo_logit_real.py, igual a "
               f"VL_estimativas.csv; β = {v(n['b'], 3)} por R$ 1 mil; γ = {v(n['dist'], 3)} por 100 km. Par escolhido por "
               f"regra fixa (exemplo_logit_real.json).")
    notas(sl, ("Passo a passo da estimação e da métrica, com um caso real. As chances são as do modelo estimado (efeitos "
               "fixos incluídos); na razão entre as duas vagas o efeito fixo do par de UFs é o mesmo e se cancela, "
               f"como o denominador. A razão do exemplo ({v(c['razao_total'])}) não é exatamente {v(n['rc'])} porque "
               "as vagas diferem um pouco em distância, IVS e porte; a parte da bolsa é exatamente e^(5β). "
               "Estamos estimando utilidade? Estimamos os pesos da parte observável do valor, numa escala "
               "normalizada; o nível do valor não é identificado. A métrica final é a razão de chances."))
    return sl


def s_identificacao(M, prs, n):
    sl = M.novo(prs, "Identificação: as premissas do logit condicional")
    cab = (("Premissa", 0.25, 4.1), ("Como atendemos", 4.45, 6.6), ("Situação", 11.15, 1.93))
    for t, x, w in cab:
        texto(sl, x, 0.92, w, 0.3, [[(t, 11, True, VERDE2)]])
    linha(sl, 0.25, 1.25, 13.08, 1.25, cor=VERDE, larg=1.5)
    linhas_ = (
        ("Escolha sincera", "a 1ª opção é a vaga que o médico prefere",
         "Supomos que ninguém deixa de pôr em 1º a vaga preferida por medo de não passar na nota; não dá para testar com estes dados.",
         "SUPOSTO", "suposto"),
        ("Cardápio conhecido", "o médico vê todas as vagas do seu curso e ciclo",
         "O edital publica a lista inteira; supomos que cada um considerou todas.", "SUPOSTO", "suposto"),
        ("Bolsa sem relação com o que não medimos", "nada escondido da vaga anda junto com a bolsa",
         f"A bolsa segue a regra do IVS ({n['r1_c1']}/{n['n_c1']} e {n['r1_c2']}/{n['n_c2']} municípios); curva do IVS "
         "e par de UFs no modelo. Mas no corte mudam outras regras junto: medimos um pacote.", "EM PARTE", "parte"),
        ("Alternativas independentes", "a razão entre duas vagas não depende das outras",
         f"Não vale por inteiro: vagas da mesma região se substituem mais (logit aninhado: λ = {v(n['lambda'])}). "
         f"Mas o peso da bolsa quase não muda ({v(n['b_m9'], 3)} contra {v(n['b_m1'], 3)}, modelo base).",
         "NÃO VALE; β ESTÁVEL", "nao"),
    )
    for k, (tit, sub, como, rot, tp) in enumerate(linhas_):
        y = 1.35 + k * 1.12
        texto(sl, 0.25, y, 4.0, 1.0, [[(tit, 14, True, TEXTO)], [(sub, 11, False, CINZA)]])
        texto(sl, 4.45, y, 6.5, 1.0, [[(como, 11.5, False, TEXTO)]])
        pill(sl, 11.15, y + 0.33, 1.93, rot, tp, h=0.34, tam=9.5)
        linha(sl, 0.25, y + 1.05, 13.08, y + 1.05, cor=BORDA, larg=0.75)
    caixa(sl, 0.25, 5.95, 12.83, 0.72,
          [[("De onde vem o β: ", 13, True, BRANCO),
            (f"só de vagas da mesma UF, com bolsas diferentes, vistas por médicos que trabalhavam na mesma UF — "
             f"{n['pares_var']} pares de UFs, {mil(n['cand_var'])} candidatos.", 13, False, BRANCO)]],
          fill=VERDE, nome="De onde vem")
    fontes(sl, "Fontes: portao_r1_ivs_oficial.json; P1_estimativas.csv (M1 e M9, ciclos 1–3); VL_resumo.json (VL-1); "
               "docs/auditorias/18 (políticas nos mesmos cortes).")
    notas(sl, ("Só as premissas do logit condicional e como atendemos (ou não) a cada uma. A escolha sincera é premissa "
               "do autor (11/11/2026). A independência das alternativas (IIA) não vale por inteiro: o aninhado por "
               "região de saúde rejeita λ = 1; o peso da bolsa no aninhado fica perto do logit condicional (modelo "
               "base M1, sem o par de UFs). O logit misto (M8) mostra que o peso varia entre candidatos: o β é uma média."))
    return sl


def s_resultados(M, prs, n):
    sl = M.novo(prs, f"Resultados: +R$ 5 mil multiplicam a chance por {v(n['rc'])}")
    subtitulo(sl, 0.25, 0.85, 7.9, "I. O que cada coeficiente faz com a chance de uma vaga",
              "contra outra igual no resto; ponto = estimativa, barra = IC 95%; VL-1, ciclos 1–3")
    sl.shapes.add_picture(str(FIG_COEF), Inches(0.2), Inches(1.55), width=Inches(7.95))
    texto(sl, 0.25, 5.8, 7.9, 0.75,
          [[("Leitura: ", 11, True, VERDE2),
            (f"coeficiente → ×: e^coef. A bolsa: β = {v(n['b'], 3)} por R$ 1 mil; 5β = {v(n['b5'], 3)}; "
             f"e^{v(n['b5'], 3)} = {v(n['rc'])}. Os outros coeficientes são controles: dizem o que mais pesa.",
             11, False, TEXTO)]], anchor=MSO_ANCHOR.TOP)
    cards = ((f"×{v(n['rc'])}", "+R$ 5 mil, vagas da mesma UF",
              f"IC 95%: {v(n['rc_inf'])} a {v(n['rc_sup'])}; p de Holm {v(n['p_holm'], 3)}", True),
             (f"{round(n['km'])} km", "o mesmo peso de +R$ 5 mil",
              f"5β ÷ |γ| × 100 = {v(n['b5'], 3)} ÷ {v(-n['dist'], 3)} × 100", False),
             (f"×{v(n['rc_c2'])}", "só no ciclo 2",
              f"IC 95%: {v(n['rc_c2_inf'])} a {v(n['rc_c2_sup'])}; nos ciclos 1 e 3, o IC contém 1", False))
    for k, (num, rot, sub, escuro) in enumerate(cards):
        y = 0.9 + k * 1.92
        caixa(sl, 8.45, y, 4.63, 1.75,
              [[(num, 34, True, BRANCO if escuro else VERDE)], [(rot, 13, True, BRANCO if escuro else TEXTO)],
               [(sub, 10.5, False, "DDEBDD" if escuro else CINZA)]],
              fill=VERDE if escuro else CLARO, line=None if escuro else BORDA, nome=f"Cartão {k}", margem=0.25)
    fontes(sl, "Fontes: output/rdd_bolsa/VL_estimativas.csv (VL-1, adendo 52e; doc 57x; auditoria 48); VG_estimativas.csv "
               "(ciclos 1 e 3, adendo 52g); figura de scripts/apresentacao/gerar_figuras_banca_final.py.")
    notas(sl, ("Primeiro o que cada coeficiente significa (pela razão de chances entre duas vagas), depois os números. "
               "Gráfico no lugar da tabela. Distância, mesma região e mesmo município são controles, mas ajudam a "
               "ler o tamanho da bolsa: estar na mesma região de saúde pesa mais que toda a bolsa extra."))
    return sl


def s_robustez(M, prs, n):
    sl = M.novo(prs, "Robustez: o ×1,47 se mantém nas variantes com mais dados".replace("1,47", v(n["rc"])))
    sl.shapes.add_picture(str(FIG_ROB), Inches(0.15), Inches(0.95), width=Inches(8.0))
    lo, hi = min(n["rc"], n["rc_log"], n["rc_vl3"]), max(n["rc"], n["rc_log"], n["rc_vl3"])
    caixa(sl, 8.4, 0.95, 4.68, 2.3,
          [[("CONCLUSÃO", 10.5, True, "B9E4B1")],
           [(f"Com todos os dados e sempre na mesma UF, o efeito fica entre ×{v(lo)} e ×{v(hi)}.", 14, True, BRANCO)],
           [("Onde há menos informação (perto do corte; ciclos 1 e 3), o IC contém 1: inconclusivo, não contrário.",
             11.5, False, "DDEBDD")]],
          fill=VERDE, nome="Conclusão robustez", margem=0.22, esp=4)
    caixa(sl, 8.4, 3.4, 4.68, 1.3,
          [[("Por que o “×” e não o coeficiente?", 12, True, VERDE2)],
           [(f"É o mesmo número: ln({v(n['rc'])}) = {v(n['b5'], 3)} = 5 × β. O β sozinho está numa escala sem "
             "unidade; o × diz quantas vezes a chance muda.", 11, False, TEXTO)]],
          fill=CLARO, line=BORDA, anchor=MSO_ANCHOR.TOP, nome="Por que x")
    caixa(sl, 8.4, 4.85, 4.68, 1.0,
          [[("Como ler", 12, True, VERDE2)],
           [("verde: IC 95% exclui 1; cinza: contém 1. O pré-registrado compara vagas de todas as UFs.", 11, False,
             TEXTO)]],
          fill=CLARO, line=BORDA, anchor=MSO_ANCHOR.TOP, nome="Como ler")
    fontes(sl, "Fontes: output/rdd_bolsa/VL_estimativas.csv (VL-1 a VL-3; adendo 52e); VG_estimativas.csv (por ciclo; "
               "adendo 52g); figura de scripts/apresentacao/gerar_figuras_banca_final.py.")
    notas(sl, ("Anotação do grupo: evidenciar a conclusão e como chegamos a ela. Conclusão no cartão escuro. O × é "
               "e^(5β): mesma informação do coeficiente, na escala de chance; o teste (IC exclui 1) é o mesmo do β "
               "(IC exclui 0)."))
    return sl


def s_metade(M, prs, n):
    sl = M.novo(prs, "Metade de quem ocupa a vaga já trabalhava no município")
    kpis = ((f"{round(n['origem'])}%", "já tinham vínculo no município do posto antes de entrar",
             f"IC 95%: {round(n['origem_lo'])}% a {round(n['origem_hi'])}%"),
            (f"+{v(n['horas'], 1)} h/sem", "a mais de horas cadastradas no CNES depois da entrada, num programa de 20 h",
             f"IC 95%: +{v(n['horas_lo'], 1)} a +{v(n['horas_hi'], 1)}"))
    for k, (num, rot, ic) in enumerate(kpis):
        caixa(sl, 0.25, 0.95 + k * 2.55, 5.6, 2.35,
              [[(num, 40, True, VERDE)], [(rot, 14, True, TEXTO)], [(ic, 11, False, CINZA)]],
              fill=CLARO, line=BORDA, nome=f"KPI {k}", margem=0.3)
    subtitulo(sl, 6.2, 0.95, 6.9, "O que isso significa")
    pontos = (("Nem toda vaga ocupada é um médico novo chegando",
               "Em metade dos casos, o programa passa a pagar quem já estava lá."),
              ("O ganho aparece mais em horas do que em médicos",
               "O cadastro sobe menos que as 20 h da bolsa: parte delas substitui horas que o médico já fazia."),
              ("Combina com a escolha da vaga",
               f"O médico escolhe perto de onde já trabalha: na mesma região de saúde, a chance é ×{v(n['x_reg'], 1)}."))
    for k, (tit, corpo) in enumerate(pontos):
        y = 1.42 + k * 1.33
        caixa(sl, 6.2, y, 0.09, 1.1, [], fill=VERDE, forma=MSO_SHAPE.RECTANGLE, nome="Barra")
        texto(sl, 6.45, y, 6.6, 1.1, [[(tit, 14, True, TEXTO)], [(corpo, 12, False, TEXTO)]])
    caixa(sl, 6.2, 5.55, 6.88, 0.9,
          [[("Descritivo: ", 11, True, CINZA),
            ("compara o mesmo médico antes e depois, sem grupo de comparação; horas cadastradas no CNES não são "
             "horas trabalhadas.", 11, False, CINZA)]],
          fill=BRANCO, line=BORDA, nome="Descritivo")
    fontes(sl, "Fontes: CNES/DATASUS; quadros de vagas e homologações do PMM-E (SGTES/MS). output/rdd_bolsa/"
               "S57_resumo.json (P4: vínculo anterior e horas totais, ciclos 1 e 2); VL_estimativas.csv.")
    notas(sl, ("Pedido de 11/11: mostrar na discussão que boa parte dos médicos já estava no município. São números do "
               "P4 (trajetória no CNES), descritivos. A ligação com a escolha: a mesma região de saúde multiplica a "
               "chance por ~3 no VL-1."))
    return sl


def s_conclusao(M, prs, n):
    sl = M.novo(prs, "Conclusão: a bolsa pesa na escolha, mas pouco")
    caixa(sl, 0.25, 0.92, 12.83, 1.5,
          [[("RESPOSTA", 11, True, "B9E4B1")],
           [(f"Sim: na mesma UF, +R$ 5 mil multiplicam por {v(n['rc'])} a chance de a vaga ser a 1ª opção", 20,
             True, BRANCO)],
           [(f"— o mesmo que estar {round(n['km'])} km mais perto. O efeito é forte só no ciclo 2 (×{v(n['rc_c2'])}).",
             15, False, "DDEBDD")]],
          fill=VERDE, nome="Resposta", margem=0.3)
    blocos = (("✓  Dá para afirmar", (f"Na mesma UF, a bolsa maior é preferida (×{v(n['rc'])}).",
                                      f"O peso é moderado: R$ 5 mil valem cerca de {round(n['km'])} km.",
                                      "O médico escolhe perto de onde já trabalha; metade já estava no município.")),
              ("✗  Não dá para afirmar", ("Que a bolsa leva mais médicos ao município: vemos a escolha, não a chegada.",
                                          "Que é só o dinheiro: no corte do IVS muda um pacote de regras.",
                                          "Que o efeito vale em todo ciclo: só o ciclo 2 é forte.")))
    for k, (tit, itens) in enumerate(blocos):
        x = 0.25 + k * 6.5
        caixa(sl, x, 2.62, 6.33, 2.85, [[(tit, 17, True, VERDE if k == 0 else "7A1C17")]] +
              [[("•  " + it, 14, False, TEXTO)] for it in itens],
              fill=CLARO if k == 0 else BRANCO, line=BORDA, anchor=MSO_ANCHOR.TOP, nome=tit, margem=0.25, esp=8)
    caixa(sl, 0.25, 5.67, 12.83, 0.85,
          [[("Para a política: ", 14, True, "B9E4B1"),
            ("pagar mais reordena a escolha entre vagas próximas; não mostramos que tire o médico da sua região.", 14,
             False, BRANCO)]],
          fill=VERDE, nome="Política", margem=0.3)
    fontes(sl, "Fontes: VL_estimativas.csv (VL-1, adendo 52e); VG_estimativas.csv (adendo 52g); S57_resumo.json (P4).")
    notas(sl, "Conclusão e 'incentivo limitado' fundidos: uma resposta, dois blocos (dá / não dá para afirmar) e a "
              "leitura para a política.")
    return sl


def s_limitacoes(M, prs, n):
    sl = M.novo(prs, "Limitações")
    caixas = (("O que o resultado não mostra",
               (("Escolher não é ir", "vemos a 1ª opção na inscrição, não a chegada ao município.",
                 "não mostra mais médicos chegando"),
                ("Pacote, não só dinheiro", "no corte de IVS outras regras mudam junto com a bolsa.",
                 "o efeito do dinheiro não sai isolado"),
                ("Local anterior pelo CNES", "é onde o médico trabalhava, não onde mora.",
                 "explica a escolha, não a causa"))),
              ("Quão firme é o resultado",
               (("Comparação pós-resultado", "fixar a UF foi decidido depois de ver os dados.",
                 "é exploratório: sugere, não confirma"),
                ("Sem fixar a UF", f"no plano pré-registrado, ×{v(n['rc_m1'])} (IC {v(n['rc_m1_inf'])} a "
                                   f"{v(n['rc_m1_sup'])}).", "não descarta efeito nulo"),
                ("Só o ciclo 2 é forte", f"ciclo 1 ×{v(n['rc_c1'])} e ciclo 3 ×{v(n['rc_c3'])}, com IC que contém 1.",
                 "não dá para generalizar para outros ciclos"))))
    for k, (tit, itens) in enumerate(caixas):
        x = 0.25 + k * 6.5
        pars = [[(tit, 19, True, VERDE)]]
        for t, d, imp in itens:
            pars.append([(t + ": ", 15, True, TEXTO), (d, 15, False, TEXTO)])
            pars.append([("→ " + imp, 13, True, MEDIO)])
        caixa(sl, x, 0.95, 6.33, 5.6, pars, fill=CLARO, line=BORDA, anchor=MSO_ANCHOR.MIDDLE, nome=tit, margem=0.35,
              esp=9)
    fontes(sl, "Fontes: VL_estimativas.csv (VL-1 e M1); VG_estimativas.csv (adendo 52g); auditorias 18 e 48; portão G1.")
    notas(sl, "Seis limitações do grupo agrupadas em duas caixas, sem repetição: o que o resultado não mostra e quão "
              "firme ele é.")
    return sl


NOVOS = {"cadeia1": lambda M, p, n: s_cadeia(M, p, n, 2), "cadeia2": lambda M, p, n: s_cadeia(M, p, n, 3),
         "hipotese": s_hipotese, "linhas": s_linhas, "modelo": s_modelo, "passos": s_passos,
         "identificacao": s_identificacao, "resultados": s_resultados, "robustez": s_robustez, "metade": s_metade,
         "conclusao": s_conclusao, "limitacoes": s_limitacoes}


# --------------------------------------------------------------------------------------------------------------
# Montagem
# --------------------------------------------------------------------------------------------------------------
def corrigir(prs) -> list[str]:
    """Troca por parágrafo (os runs do grupo vêm picados): junta o texto no 1º run, mantendo a formatação dele."""
    feitas = []
    for num, antigo, novo in CORRECOES:
        achou = 0
        for sh in formas(prs.slides[num - 1].shapes):
            if not sh.has_text_frame:
                continue
            for par in sh.text_frame.paragraphs:
                runs = par.runs
                inteiro = "".join(r.text for r in runs)
                if antigo not in inteiro:
                    continue
                runs[0].text = inteiro.replace(antigo, novo)
                for r in runs[1:]:
                    r._r.getparent().remove(r._r)
                for br in par._p.findall("a:br", NS):
                    par._p.remove(br)
                if not runs[0].text.strip() and len(sh.text_frame.paragraphs) > 1:
                    par._p.getparent().remove(par._p)
                achou += 1
        if achou != 1:
            raise SystemExit(f"ERRO: esperava 1 {antigo!r} no slide {num} do grupo; achei {achou}")
        feitas.append(f"slide {num} do grupo: {antigo.strip()!r} → {novo!r}")
    return feitas


def tirar_anotacoes(prs) -> list[str]:
    tiradas = []
    for i, s in enumerate(prs.slides, 1):
        for sh in list(formas(s.shapes)):
            if sh.has_text_frame and sh.text_frame.text.strip().startswith(ANOTACOES):
                tiradas.append(f"slide {i} do grupo: {sh.text_frame.text.strip()[:60]!r}")
                remover(sh)
    return tiradas


def construir() -> dict:
    if sha256(ENT) != SHA_ENT:
        raise SystemExit("ERRO: o deck do grupo de 11/11 mudou (hash diferente)")
    prs = Presentation(str(ENT))
    if len(prs.slides) != N_ENT:
        raise SystemExit(f"ERRO: esperava {N_ENT} slides no deck do grupo")
    n = numeros()
    feitas = corrigir(prs) + tirar_anotacoes(prs)
    grupo = list(prs.slides)
    M = Modelo(prs)
    novos = {nome: f(M, prs, n) for nome, f in NOVOS.items()}
    usados = {k for t, k, _ in ORDEM if t == "G"}
    if usados | set(FORA) != set(range(1, N_ENT + 1)) or usados & set(FORA):
        raise SystemExit("ERRO: cada slide do grupo tem de estar na ORDEM ou em FORA")
    lista = prs.slides._sldIdLst
    ids = {id(s): el for s, el in zip(prs.slides, list(lista))}
    sequencia = []
    for t, k, secao in ORDEM:
        s = grupo[k - 1] if t == "G" else novos[k]
        sequencia.append((s, ids[id(s)], t, k, secao))
    for el in list(lista):
        lista.remove(el)
    for s, el, *_ in sequencia:
        lista.append(el)
    # slides fora: tira a relação do pacote
    for k in FORA:
        s = grupo[k - 1]
        for rid, rel in list(prs.part.rels.items()):
            if rel.target_part is s.part:
                prs.part.drop_rel(rid)
    manifesto = []
    for pos, (s, _, t, k, secao) in enumerate(sequencia, 1):
        rodape(s, secao)
        numerar(s, pos)
        if t == "G" and s._element.get("show") == "0":
            raise SystemExit(f"ERRO: slide oculto mantido ({k})")
        tits = [sh for sh in s.shapes if sh.is_placeholder and "TITLE" in str(sh.placeholder_format.type)]
        titulo = tits[0].text_frame.text if tits else ""
        manifesto.append({"posicao": pos, "origem": "grupo 11/11" if t == "G" else "novo", "slide_origem": k,
                          "secao": secao, "titulo": " ".join(titulo.split())})
    OUT.mkdir(parents=True, exist_ok=True)
    pptx = OUT / f"{ARQ}.pptx"
    prs.save(str(pptx))
    return {"n": n, "feitas": feitas, "manifesto": manifesto, "pptx": pptx}


def converter_pdf(pptx: Path, pdf: Path) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, str(pptx)],
                           capture_output=True, text=True, timeout=600)
        gerado = Path(tmp) / (pptx.stem + ".pdf")
        if r.returncode != 0 or not gerado.exists():
            return False
        shutil.copy(gerado, pdf)
    return True


def main(argv=None) -> int:
    res = construir()
    pdf = OUT / f"{ARQ}.pdf"
    ok_pdf = converter_pdf(res["pptx"], pdf)
    entradas = [ENT, F_VL, F_VLR, F_VG, F_P1R, F_P1E, F_S57, F_R1, F_EX, FIG_COEF, FIG_ROB]
    man = {"etapa": "deck_banca_final_grupo", "natureza_dos_dados": "EMPIRICO",
           "script": str(Path(__file__).resolve().relative_to(ROOT)), "doc_conteudo": DOC,
           "entradas": {str(p.relative_to(ROOT)): sha256(p) for p in entradas},
           "slides": res["manifesto"], "fora_do_deck": {str(k): v_ for k, v_ in FORA.items()},
           "correcoes_e_retiradas": res["feitas"],
           "saidas": {str(res["pptx"].relative_to(ROOT)): sha256(res["pptx"]),
                      **({str(pdf.relative_to(ROOT)): "gerado (PDF não é determinístico)"} if ok_pdf else {})}}
    (OUT / f"manifesto_{ARQ}.json").write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(res['manifesto'])} slides; PDF {'ok' if ok_pdf else 'FALHOU'}")
    return 0 if ok_pdf else 1


if __name__ == "__main__":
    sys.exit(main())
