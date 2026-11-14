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
# Deck do grupo de 14/11/2026: o mesmo de 11/11 com a data dos sumários trocada (11/11/2026 → 14/11/2026)
ENT = ROOT / "docs/07_apresentacoes/banca_final/grupo/deck_grupo_banca_final_1411.pptx"
SHA_ENT = "f051366bbcb76ea5767f9390d2bfa9c6f7fcbd323fc65c4a96da895902d64843"
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
    ("N", "estimacao", "Metodologia"), ("N", "identificacao", "Identificação"),
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
    # a bolsa não é piso: é o valor fixado pela faixa (errata da banca 1)
    (n, "define o piso da bolsa", "define o valor da bolsa") for n in (4, 5, 6)
] + [
    # descritiva: título com a mensagem, sem repetir o cartão "3 em 4" (revisão de 14/11); "candidatos", não "médicos"
    (17, "Os médicos escolhem vagas perto de onde já trabalham", "Os candidatos escolhem perto de onde trabalham"),
    # pergunta alinhada ao que testamos (escolha da 1ª opção, efeito da bolsa isolado); decisão do autor de 11/11
    (9, "Um aumento na remuneração\xa0do PMM-E eleva a probabilidade de preenchimento das vagas em municípios mais "
        "vulneráveis?", "Uma bolsa maior aumenta a chance de uma vaga\nser a 1ª opção do médico?"),
] + [
    # revisão de 14/11 -------------------------------------------------------------------------------------------
    # manchete do gov.br: acento
    (n, "permanência de medicos", "permanência de médicos") for n in (7, 9)
] + [
    # sumários: "Hips de Identificação" era abreviação de rascunho
    (n, "Hips de Identificação", "Modelo e identificação") for n in (2, 8, 10, 13, 15, 18, 23)
] + [
    # "origem" vira "local de trabalho anterior" (pedido da banca de 04/11, doc 12 da banca 2, §1.2)
    (16, "Origem do médico", "Local de trabalho anterior"),
    (16, "Com origem identificada", "Com local anterior e região"),
    # o modelo principal (VL-1) tem 5.417 candidatos; 5.421 é o modelo base (funil no slide 18)
    (16, "5.421", "5.417"),
    (16, "candidatos com 1ª opção e município de origem identificado nos três ciclos.",
     "candidatos no modelo principal, nos três ciclos (o funil está no slide seguinte)."),
    (17, "candidatos com 1ª opção e município de origem identificado",
     "candidatos com 1ª opção e local de trabalho anterior identificado"),
    (17, "é a distância mediana entre a origem e a 1ª opção", "é a distância mediana entre o local anterior e a 1ª opção"),
    (17, "I. Candidatos escolhem 1ª opção\xa0no local de\xa0origem", "I. A 1ª opção fica perto do local anterior"),
    (17, "A origem é o vínculo médico anterior no CNES, não a residência.",
     "O local anterior é o vínculo médico no CNES antes da inscrição, não a residência."),
    # anexo: decisões do autor de 11/11 (doc 02, §1, itens 3 e 19): sem altruísmo (α fica só para o par de UFs) e a
    # política decide a escolha, não o preenchimento
    (32, "; o altruísmo do médico (α) compensa em parte.", "."),
    (32, ") por (B)", ") pela bolsa (B)"),  # o "E(w|B)" vem em runs separados
    (32, "Preços e custo do local continuam contra e é a soma das três variáveis que determina se a vaga é preenchida.",
     "Preços e custo do local continuam contra, e é o saldo das três variáveis que decide qual vaga o médico escolhe."),
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
        "rc_vl2_inf": float(rc.loc["VL2_emp", "ic95_inf"]), "rc_vl2_sup": float(rc.loc["VL2_emp", "ic95_sup"]),
        # inferência do VL-1 (slide de estimação)
        "g_conj": int(c.loc["bolsa_mil", "n_conjuntos"]), "ep_cl": float(c.loc["bolsa_mil", "ep_cluster_conjunto"]),
        "ep_mle": float(c.loc["bolsa_mil", "ep_mle"]), "p_score": float(rc.loc["VL1_emp", "p_score_rademacher"]),
        "x_dist_m1": math.exp(float(d[(d.chave_modelo == "M1_emp") & (d.tipo_linha == "coeficiente") &
                                      (d.termo == "distancia_100km")].estimativa.iloc[0])),
        "alt_desenho": idt["alternativas_no_desenho"], "alt_ret": idt["alternativas_retiradas"],
        "col_ef": idt["colunas_de_efeito_fixo"],
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
    if n["alt_desenho"] - n["alt_ret"] != n["n_lin"]:
        raise SystemExit("ERRO: alternativas do desenho menos as retiradas não dão as linhas do VL-1")
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
            # caixa estreita do grupo: "11" quebrava em duas linhas no PowerPoint; alarga para a esquerda, sem quebra
            if sh.width < Inches(0.6):
                sh.left, sh.width = sh.left - (Inches(0.6) - sh.width), Inches(0.6)
                for p_ in sh.text_frame.paragraphs:
                    p_.alignment = PP_ALIGN.RIGHT
            sh.text_frame.word_wrap = False
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
    caixa(sl, 2.2, 0.92, 3.1, 0.86, [[("IVS do município", 15, True, VERDE)], [("Ipea, 2010", 11, False, CINZA)]],
          fill=CLARO, line=BORDA)
    seta(sl, 5.32, 1.35, 5.72, 1.35)
    caixa(sl, 5.75, 0.92, 7.33, 0.86, [], fill=CLARO, line=BORDA, nome="Faixas")
    texto(sl, 5.92, 0.97, 1.85, 0.76, [[("Bolsa mensal", 15, True, VERDE)]])
    for k, (faixa, valor) in enumerate((("IVS até 0,300", "R$ 10 mil"), ("0,301 a 0,400", "R$ 15 mil"),
                                        ("acima de 0,400", "R$ 20 mil"))):
        caixa(sl, 7.85 + k * 1.75, 1.04, 1.62, 0.62, [[(faixa, 10, False, TEXTO)], [(valor, 13, True, VERDE)]],
              fill=BRANCO, line=BORDA, align=PP_ALIGN.CENTER, margem=0.04)
    # 2. Escolha do médico: primeiro o que reduz, depois o que eleva
    rotulo(2.05, 2, "ESCOLHA DO MÉDICO")
    cart = (("reduz", "REDUZ O VALOR", "Custo de viver ali", "deslocamento, distância de casa",
             "Redding & Rossi-Hansberg (2017)", False),
            ("reduz", "REDUZ O VALOR", "Custo de trabalhar ali", "esforço: falta equipe e equipamento",
             "Choné & Ma (2011)", False),
            ("eleva", "ELEVA O VALOR", "Remuneração", "bolsa maior", "Moehling et al. (2020)", True))
    for k, (tp, rot, tit, corpo, ref, escuro) in enumerate(cart):
        x = 2.2 + k * 3.69
        fill, cor_t, cor_c = (VERDE, BRANCO, BRANCO) if escuro else (CLARO, VERDE, TEXTO)
        caixa(sl, x, 2.0, 3.5, 1.5, [], fill=fill, line=None if escuro else BORDA, nome=f"Fator {tit}")
        pill(sl, x + 0.15, 2.1, 1.45, rot, tp)
        texto(sl, x + 0.15, 2.42, 3.2, 0.32, [[(tit, 15, True, cor_t)]])
        texto(sl, x + 0.15, 2.76, 3.2, 0.4, [[(corpo, 12.5, False, cor_c)]], anchor=MSO_ANCHOR.TOP)
        texto(sl, x + 0.15, 3.18, 3.2, 0.24, [[(ref, 9, True, "B9E4B1" if escuro else VERDE2)]])
        if k < 2:
            seta(sl, x + 1.75, 3.52, x + 1.75, 3.82, cor=MEDIO)
        else:
            seta(sl, x + 0.9, 3.52, 8.75, 3.84, cor=VERDE)
    # valor (não observado) → 1ª opção (observada)
    caixa(sl, 2.2, 3.85, 6.9, 0.62, [], fill=CLARO, line=VERDE, nome="Valor da vaga")
    texto(sl, 2.35, 3.88, 4.9, 0.56, [[("Valor da vaga para o médico", 15, True, VERDE)]])
    pill(sl, 7.5, 4.03, 1.45, "NÃO OBSERVADO", "naoobs")
    seta(sl, 9.12, 4.16, 9.5, 4.16)
    caixa(sl, 9.53, 3.85, 3.55, 0.62, [], fill=CLARO, line=VERDE, nome="1a opção")
    texto(sl, 9.68, 3.88, 2.2, 0.56, [[("1ª opção", 15, True, VERDE)]])
    pill(sl, 11.78, 4.03, 1.18, "OBSERVADA", "obs")
    caixa(sl, 2.2, 4.57, 10.88, 0.5,
          [[("O que estimamos: ", 13, True, "B9E4B1"), ("o peso da bolsa na escolha.   ", 13, False, BRANCO),
            (f"+R$ 5 mil → chance ×{v(n['rc'])} ≈ {round(n['km'])} km mais perto", 13, True, BRANCO)]],
          fill=VERDE, nome="Métrica")
    # 3. Da vaga à saúde
    rotulo(5.25, 3, "DA VAGA À SAÚDE", apagado=ap)
    elos = ("Quantos médicos a escolhem", "Vaga ocupada", "Capacidade", "Produção e acesso", "Saúde")
    for k, tit in enumerate(elos):
        x = 2.2 + k * 2.22
        caixa(sl, x, 5.22, 2.0, 0.84, [[(tit, 13, True, APAGADO if ap else VERDE)]],
              fill=FUNDO_AP if ap else CLARO, line=None if ap else BORDA, nome=f"Elo {tit}")
        if k < 4:
            seta(sl, x + 2.01, 5.64, x + 2.21, 5.64, cor=APAGADO if ap else VERDE, larg=1.5)
    texto(sl, 2.2, 6.15, 10.88, 0.3, [[("Etapa 3: fora do que estimamos.", 11.5, True, APAGADO if ap else CINZA)]])
    fontes(sl, "Fontes: Moehling et al. (2020); Choné & Ma (2011); Redding & Rossi-Hansberg (2017); Burdett, Shi & "
               "Wright (2001); edital SGTES/MS nº 3/2025; Ipea, IVS 2010. Estimativa: VL-1, ciclos 1–3.")
    notas(sl, ("Cadeia causal, etapa por etapa. " + ("Primeiro a regra e a escolha do médico: o que reduz o valor da "
               "vaga (deslocamento, esforço) e o que o eleva (a bolsa). " if ap else "Agora a etapa 3: da vaga escolhida "
               "à saúde (quantos médicos a escolhem, vaga ocupada, vínculos e horas, consultas e exames, espera e "
               "internações); não é estimada aqui: o trabalho testa só o elo bolsa → valor → 1ª opção. ") +
               "O valor da vaga é a utilidade: a soma do que eleva e do que reduz; não aparece nos dados. O que aparece "
               "é a 1ª opção; o logit condicional lê nas escolhas quanto a bolsa pesa no valor. "
               f"Métrica: e^(5β) = {v(n['rc'])}; {round(n['km'])} km = 5β ÷ |γ| × 100. Termos usados no deck: vaga = "
               "estabelecimento × curso; cardápio = vagas que o médico podia escolher; 1ª opção = a vaga listada em 1º; "
               "chance = probabilidade de a vaga ser a 1ª opção. Origem: docs/07_apresentacoes/banca_final/"
               "01_diagrama_teoria_mudanca.md; VL_estimativas.csv (VL-1)."))
    return sl


def s_hipotese(M, prs, n):
    ex = n["ex"]
    a, b = ex["vaga_a"], ex["vaga_b"]
    sl = M.novo(prs, "Maior remuneração, maior chance de ser escolhida")
    caixa(sl, 0.25, 0.92, 12.83, 1.45,
          [[("HIPÓTESE", 11, True, "B9E4B1")],
           [("A vaga que paga mais tem mais chance de ser a 1ª opção do médico.", 26, True, BRANCO)],
           [("entre vagas do mesmo curso, na mesma UF, iguais no resto", 13, False, "DDEBDD")]],
          fill=VERDE, nome="Hipótese", margem=0.3)
    subtitulo(sl, 0.25, 2.65, 12.8, f"Exemplo real: um médico de {ex['candidato']['uf_de_trabalho_anterior']}, "
                                    f"ciclo {ex['candidato']['ciclo']}, diante de duas vagas do seu curso")
    for k, (vg, destaque) in enumerate(((a, False), (b, True))):
        y = 3.2 + k * 1.0
        caixa(sl, 0.25, y, 6.0, 0.88,
              [[(vg["municipio"], 16, True, BRANCO if destaque else TEXTO),
                (f"   R$ {int(vg['bolsa_mil'])} mil/mês", 16, True, BRANCO if destaque else VERDE)],
               [(f"IVS {v(vg['ivs'], 3)}  ·  {round(vg['km'])} km de onde trabalhava", 11.5, False,
                 "DDEBDD" if destaque else CINZA)]],
              fill=MEDIO if destaque else CLARO, line=None if destaque else BORDA, nome=f"Vaga {k + 1}")
    seta(sl, 6.35, 4.14, 6.85, 4.14, larg=2.5)
    caixa(sl, 6.95, 3.2, 6.13, 1.88,
          [[("Hipótese no exemplo", 12, True, VERDE2)],
           [("chance(", 16, True, TEXTO), (b["municipio"].split(" (")[0], 16, True, VERDE),
            (") > chance(", 16, True, TEXTO), (a["municipio"].split(" (")[0], 16, True, TEXTO), (")", 16, True, TEXTO)],
           [("Só a bolsa muda; o resto é quase igual.", 12.5, False, TEXTO)]],
          fill=CLARO, line=BORDA, nome="Hipótese no exemplo")
    caixa(sl, 0.25, 5.45, 12.83, 0.8,
          [[("O que não dizemos: ", 14, True, VERDE),
            ("que mais médicos chegam ao município. Olhamos a escolha de quem se inscreveu.", 14, False, TEXTO)]],
          fill=BRANCO, line=BORDA, nome="O que não dizemos", margem=0.3)
    fontes(sl, "Fontes: editais e quadros de vagas do PMM-E (SGTES/MS), ciclo 2; Ipea, IVS 2010; IBGE. Exemplo: "
               "output/apresentacao_banca_final/exemplo_logit_real.json (par escolhido por regra fixa).")
    notas(sl, (f"Frase central simples; o exemplo é real e volta no slide do método. O médico é de "
               f"{ex['candidato']['curso'].title().replace(' Do ', ' do ')}. As duas vagas ficam dos dois lados do corte "
               f"de 0,400 e quase iguais no resto (porte: {mil(round(a['populacao_2022'] / 1000) * 1000)} e "
               f"{mil(round(b['populacao_2022'] / 1000) * 1000)} hab.): só a bolsa muda. Comparamos vagas diferentes, "
               "para o mesmo médico, no mesmo momento. Origem: exemplo_logit_real.json (regra de escolha do par no "
               "próprio arquivo)."))
    return sl


def s_linhas(M, prs, n):
    ex = n["ex"]
    sl = M.novo(prs, "Cada candidato vira uma linha por vaga do cardápio")
    subtitulo(sl, 0.25, 0.85, 7.3, "I. O mesmo médico do exemplo",
              f"{ex['candidato']['vagas_no_cardapio']} linhas: uma por vaga do seu curso e ciclo (o cardápio)")
    vagas = [(ex["vaga_escolhida"], 1), (ex["vaga_b"], 0), (ex["vaga_a"], 0)]
    tab = sl.shapes.add_table(5, 5, Inches(0.25), Inches(1.6), Inches(7.3), Inches(3.5)).table
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
            r.font.size = Pt(11 if i == 0 else 13)
            r.font.bold = i == 0 or (i == 1 and j == 4)
            r.font.italic = i == 4 and j == 1
            r.font.name = "Montserrat"
            r.font.color.rgb = RGBColor.from_string(BRANCO if i == 0 else (CINZA if i == 4 else TEXTO))
            c.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT if j < 2 else PP_ALIGN.CENTER
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
    subtitulo(sl, 7.9, 0.85, 5.2, "II. A base do modelo principal")
    for k, (num, rot) in enumerate(((mil(n["n_lin"]), "linhas candidato × vaga"),
                                    (mil(n["n_cand"]), "candidatos"))):
        caixa(sl, 7.9 + k * 2.65, 1.3, 2.5, 1.05, [[(num, 22, True, VERDE)], [(rot, 11, False, TEXTO)]],
              fill=CLARO, line=BORDA)
    texto(sl, 7.9, 2.42, 5.18, 0.34,
          [[(f"≈ {round(n['lin_media'])} vagas por candidato", 12, True, TEXTO)]])
    funil = ((mil(n["r1"]), "com 1ª opção (ciclos 1–3)"),
             (mil(n["com_cnes"]), "com local de trabalho anterior (CNES)"),
             (mil(n["m1_cand"]), "com região de saúde"),
             (mil(n["n_cand"]), "no modelo principal"))
    for k, (num, rot) in enumerate(funil):
        y = 2.88 + k * 0.48
        caixa(sl, 7.9, y, 1.05, 0.4, [[(num, 13, True, BRANCO)]], fill=VERDE if k == 3 else MEDIO,
              align=PP_ALIGN.CENTER, margem=0.02)
        texto(sl, 9.05, y, 4.03, 0.4, [[(rot, 11, k == 3, TEXTO)]])
    texto(sl, 7.9, 4.82, 5.18, 0.4,
          [[(f"Linhas: {mil(n['alt_desenho'])} → {mil(n['n_lin'])} linhas (saem pares de UFs sem nenhuma 1ª opção).",
             9.5, False, CINZA)]], anchor=MSO_ANCHOR.TOP)
    caixa(sl, 0.25, 5.45, 12.83, 1.0,
          [[("MEDIDA:  ", 13, True, "B9E4B1"),
            ("quantas vezes a chance de ser a 1ª opção se multiplica com +R$ 5 mil. Hipótese: maior que 1.", 15, True,
             BRANCO)]],
          fill=VERDE, nome="Medida", margem=0.3)
    fontes(sl, "Fontes: editais e quadros de vagas do PMM-E (SGTES/MS), ciclos 1–3; CNES/DATASUS; Ipea; IBGE. "
               "P1_resumo.json; VL_resumo.json; exemplo_logit_real.json.")
    notas(sl, (f"Cada linha diz o que o médico podia escolher e se escolheu; atributos da vaga (bolsa, IVS, porte) e do "
               f"par médico–vaga (distância, mesma região) entram como colunas. ≈ {round(n['lin_media'])} vagas por "
               f"candidato (mediana {round(n['lin_med'])}; de {n['lin_min']} a {n['lin_max']}). De {mil(n['r1'])} "
               f"candidatos com 1ª opção, {mil(n['com_cnes'])} têm local de trabalho anterior no CNES (o ponto de "
               f"partida da distância; sem ele não há distância nem 'mesma região'); {mil(n['m1_cand'])} têm região de "
               f"saúde na tabela oficial; no modelo principal, que fixa o par de UFs, saem as vagas de pares de UFs que "
               f"nenhum médico daquela UF escolheu (não informam o peso da bolsa: {mil(n['alt_desenho'])} → "
               f"{mil(n['n_lin'])} linhas) e {n['ret_uma']} candidatos que ficaram com uma só vaga: "
               f"{mil(n['n_cand'])} candidatos. A medida é a razão de chances da 1ª opção por +R$ 5 mil, contra uma "
               "vaga igual no resto."))
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
          [[("i: candidato  ·  v: vaga  ·  V: valor da vaga", 10.5, False, CINZA)]], align=PP_ALIGN.CENTER)
    # O que se estima
    caixa(sl, 9.0, 0.9, 4.08, 2.55,
          [[("O QUE SE ESTIMA", 10.5, True, "B9E4B1")],
           [("Os pesos (β, γ, …) que melhor explicam as 1ªs opções observadas.", 16, True, BRANCO)]],
          fill=VERDE, anchor=MSO_ANCHOR.MIDDLE, nome="O que se estima", margem=0.25, esp=6)
    # II. O que cada termo faz
    texto(sl, 0.25, 3.62, 8.55, 0.32, [[("II. O que cada termo faz", 15, True, TEXTO)]])
    termos = (("β · bolsa", "testado", "TESTADO", "o que testamos"),
              ("γ · distância", "controle", "CONTROLE", "distância do local de trabalho anterior"),
              ("f(IVS)", "controle", "CONTROLE", "IVS sem salto: no corte, só a bolsa salta"),
              ("α · par de UFs", "pareamento", "FIXO", "compara vagas dentro da mesma UF"),
              ("θ · X", "controle", "CONTROLE", "região, município, porte, capital, vaga imediata"))
    for k, (t, tp, rot, leitura) in enumerate(termos):
        y = 4.05 + k * 0.52
        texto(sl, 0.35, y, 1.6, 0.46, [eq(t, 15)])
        pill(sl, 1.95, y + 0.1, 1.2, rot, tp)
        texto(sl, 3.3, y, 5.5, 0.46, [[(leitura, 12.5, False, TEXTO)]])
        if k < 4:
            linha(sl, 0.35, y + 0.5, 8.75, y + 0.5, cor=BORDA, larg=0.75)
    # Por que este modelo
    caixa(sl, 9.0, 3.62, 4.08, 3.0, [], fill=CLARO, line=BORDA, nome="Por que este modelo")
    texto(sl, 9.2, 3.72, 3.75, 0.3, [[("POR QUE ESTE MODELO", 10.5, True, VERDE2)]])
    texto(sl, 9.2, 4.05, 3.72, 1.0,
          [[("Cada médico escolhe ", 12, False, TEXTO), ("uma", 12, True, TEXTO),
            (f" entre ≈ {round(n['lin_media'])} vagas; o que é dele se cancela.", 12, False, TEXTO)]],
          anchor=MSO_ANCHOR.TOP)
    refs = (("McFadden (1974)", "o método"),
            ("Bobba et al. (2026)", "bônus que salta em cortes"),
            ("Costa, Nunes & Sanches (2024)", "médicos no Brasil"))
    texto(sl, 9.2, 5.1, 3.72, 1.4, [[(a, 10.5, True, VERDE), (f": {b}", 10.5, False, TEXTO)] for a, b in refs],
          anchor=MSO_ANCHOR.TOP, esp=3)
    fontes(sl, "Fontes: McFadden (1974); Bobba et al. (NBER WP 29068, rev. 2026); docs/03_literatura_empirica/19 e 20; "
               "protocolo 52 e adendo 52e (VL-1).")
    notas(sl, ("Correção da banca 2: antes mostrávamos a utilidade com o erro (U = … + ε) e a probabilidade sobre U. O "
               "que estimamos é a probabilidade de escolha do logit condicional: P = exp(V)/Σ exp(V), com V a parte "
               "observável do valor; o erro de cada vaga (Gumbel) é o que gera essa fórmula. Os pesos saem por máxima "
               "verossimilhança. O nível do valor não é identificado (só diferenças entre vagas, e numa escala "
               "normalizada); por isso cada coeficiente se lê pela razão de chances entre duas vagas: P(A) ÷ P(B) = "
               "exp[β·(bolsa_A − bolsa_B) + γ·(dist_A − dist_B) + …], em que o cardápio se cancela. β: +R$ 5 mil "
               "multiplicam a chance por e^(5β). Por que este modelo: o que é do médico (nota, idade, perfil) é igual "
               "em todas as vagas e se cancela. Mais referências: Scott et al. (2013) e Kolstad (2011), experimentos de "
               "escolha com médicos; McFadden recebeu o Nobel de 2000."))
    return sl


def s_passos(M, prs, n):
    ex = n["ex"]
    a, b, c = ex["vaga_a"], ex["vaga_b"], ex["conta"]
    sl = M.novo(prs, "Método passo a passo: da escolha à razão de chances")
    passos = (("1", "Cardápio", f"uma linha por vaga possível (≈ {round(n['lin_media'])})"),
              ("2", "Escolha", "y = 1 na vaga listada em 1º"),
              ("3", "Valor", "V = pesos × atributos"),
              ("4", "Chance", "exp(V) ÷ soma do cardápio"),
              ("5", "Pesos", "os que melhor explicam as escolhas reais"),
              ("6", "Métrica", "chance(A) ÷ chance(B)"))
    w, gap = 1.95, 0.226
    for k, (num, tit, corpo) in enumerate(passos):
        x = 0.25 + k * (w + gap)
        final = k == 5
        caixa(sl, x, 0.92, w, 1.4, [], fill=VERDE if final else CLARO, line=None if final else BORDA,
              nome=f"Passo {num}")
        caixa(sl, x + 0.12, 1.02, 0.4, 0.4, [[(num, 13, True, VERDE if final else BRANCO)]],
              fill=BRANCO if final else VERDE, forma=MSO_SHAPE.OVAL, align=PP_ALIGN.CENTER, margem=0)
        texto(sl, x + 0.6, 1.02, w - 0.66, 0.4, [[(tit, 14, True, BRANCO if final else VERDE)]])
        texto(sl, x + 0.12, 1.5, w - 0.22, 0.8, [[(corpo, 12, False, BRANCO if final else TEXTO)]],
              anchor=MSO_ANCHOR.TOP)
        if k < 5:
            seta(sl, x + w + 0.01, 1.62, x + w + gap - 0.01, 1.62, larg=1.75)
    caixa(sl, 0.25, 2.42, 12.83, 0.34,
          [[("1–2: a base   ·   3–5: a estimação (máxima verossimilhança)   ·   6: a métrica", 11.5, True, VERDE2)]],
          forma=MSO_SHAPE.RECTANGLE, align=PP_ALIGN.CENTER)
    # Exemplo real
    subtitulo(sl, 0.25, 3.0, 12.8, f"Exemplo real: o médico de {ex['candidato']['uf_de_trabalho_anterior']} do slide "
                                   "de hipótese")
    for k, vg in enumerate((a, b)):
        y = 3.6 + k * 1.15
        caixa(sl, 0.25, y, 3.9, 1.0,
              [[(vg["municipio"], 14, True, TEXTO)],
               [(f"R$ {int(vg['bolsa_mil'])} mil  ·  {round(vg['km'])} km", 11, False, CINZA)]],
              fill=CLARO, line=BORDA, nome=f"Vaga ex {k}")
        caixa(sl, 4.25, y, 1.55, 1.0, [[("chance", 10, False, CINZA)], [(f"{v(100 * vg['chance_modelo'])}%", 20, True,
                                                                            VERDE)]],
              fill=BRANCO, line=VERDE, align=PP_ALIGN.CENTER, margem=0.04, nome=f"Chance ex {k}")
    seta(sl, 5.9, 4.68, 6.3, 4.68, larg=2.5)
    rz = c["razao_por_termo"]
    caixa(sl, 6.4, 3.6, 4.0, 2.15, [], fill=VERDE, nome="Razão do exemplo")
    texto(sl, 6.6, 3.68, 3.7, 0.3, [[("PASSO 6: A RAZÃO", 10.5, True, "B9E4B1")]])
    texto(sl, 6.6, 3.98, 3.7, 0.5,
          [[(f"{v(100 * b['chance_modelo'])}% ÷ {v(100 * a['chance_modelo'])}% = {v(c['razao_total'])}", 20, True,
             BRANCO)]])
    fat = ((f"×{v(rz['bolsa_mil'])}", "a bolsa: +R$ 5 mil"),
           (f"×{v(rz['distancia_100km'])}", f"a distância: {round(b['km'] - a['km'])} km a mais"),
           (f"×{v(rz['ivs'] * rz['log_populacao_2022'] * rz['outros'])}", "o resto"))
    for k, (x_, rot) in enumerate(fat):
        texto(sl, 6.6, 4.55 + k * 0.4, 3.7, 0.38,
              [[(x_, 15, True, "B9E4B1" if k == 0 else BRANCO), (f"  {rot}", 12, False, BRANCO)]])
    caixa(sl, 10.55, 3.6, 2.53, 2.15,
          [[("Só as duas na mesa:", 11, True, VERDE2)],
           [(f"{round(100 * c['chance_b_entre_as_duas'])}% contra {100 - round(100 * c['chance_b_entre_as_duas'])}%",
             19, True, TEXTO)]],
          fill=CLARO, line=BORDA, nome="Entre as duas")
    fontes(sl, f"Fontes: VL-1 (ciclos 1–3) reestimado em scripts/apresentacao/gerar_exemplo_logit_real.py, igual a "
               f"VL_estimativas.csv; β = {v(n['b'], 3)} por R$ 1 mil; γ = {v(n['dist'], 3)} por 100 km. Par escolhido por "
               f"regra fixa (exemplo_logit_real.json).")
    notas(sl, (f"Passo a passo da estimação e da métrica, com um caso real ({ex['candidato']['vagas_no_cardapio']} vagas "
               f"no cardápio; IVS {v(a['ivs'], 3)} e {v(b['ivs'], 3)}). As chances são as do modelo estimado (efeitos "
               "fixos incluídos); na razão entre as duas vagas o efeito fixo do par de UFs é o mesmo e se cancela, como "
               f"o denominador. ×{v(rz['bolsa_mil'])} = e^(5 × β). A razão do exemplo ({v(c['razao_total'])}) não é "
               f"exatamente {v(n['rc'])} porque as vagas diferem um pouco em distância, IVS e porte. Por que razão, e "
               "não diferença: com centenas de vagas cada chance é pequena; a razão não depende do tamanho do cardápio. "
               "Estamos estimando utilidade? Estimamos os pesos da parte observável do valor, numa escala normalizada; "
               "o nível do valor não é identificado. A métrica final é a razão de chances."))
    return sl


def s_estimacao(M, prs, n):
    """Como chegamos ao ×1,47: de onde vem a variação, o que fica fixo, a estimação e a incerteza (pedido de 14/11)."""
    sl = M.novo(prs, "Estimação: de onde vem o β e quão preciso ele é")
    topo, alto = 0.9, 4.55

    def cartao(x, w, rotulo):
        caixa(sl, x, topo, w, alto, [], fill=BRANCO, line=BORDA, nome=f"Cartão {rotulo}")
        texto(sl, x + 0.2, topo + 0.12, w - 0.3, 0.3, [[(rotulo, 11.5, True, VERDE2)]])

    # I. De onde vem a variação da bolsa
    x1, w1 = 0.25, 4.15
    cartao(x1, w1, "I. DE ONDE VEM O β")
    itens = (("1", "A bolsa **salta** nos cortes 0,300 e 0,400."),
             ("2", "O IVS entra **sem salto**: no corte, só a bolsa muda."),
             ("3", f"Comparação **dentro da mesma UF**: {n['pares_var']} pares, {mil(n['cand_var'])} candidatos."))
    for k, (num, t) in enumerate(itens):
        y = topo + 0.62 + k * 1.25
        caixa(sl, x1 + 0.2, y + 0.02, 0.4, 0.4, [[(num, 13, True, BRANCO)]], fill=VERDE, forma=MSO_SHAPE.OVAL,
              align=PP_ALIGN.CENTER, margem=0)
        texto(sl, x1 + 0.75, y, w1 - 0.9, 1.1, [negrito(t, 13.5, TEXTO)], anchor=MSO_ANCHOR.TOP)

    # II. O que o modelo mantém fixo
    x2, w2 = 4.55, 4.15
    cartao(x2, w2, "II. O QUE FICA FIXO")
    fixos = (("Candidato", "se cancela na conta", "FIXO", "pareamento"),
             ("UF de trabalho × UF da vaga", f"{n['col_ef']} colunas 0/1", "FIXO", "pareamento"),
             ("Município ou vaga", "apagaria a bolsa", "NÃO", "nao"),
             ("Distância, região, porte", "colunas do V", "CONTROLE", "controle"))
    for k, (tit, sub, rot, tp) in enumerate(fixos):
        y = topo + 0.62 + k * 0.95
        texto(sl, x2 + 0.2, y, 2.6, 0.85, [[(tit, 12.5, True, TEXTO)], [(sub, 10.5, False, CINZA)]],
              anchor=MSO_ANCHOR.TOP)
        pill(sl, x2 + w2 - 1.27, y + 0.05, 1.1, rot, tp, h=0.3, tam=9)
        if k < 3:
            linha(sl, x2 + 0.2, y + 0.86, x2 + w2 - 0.17, y + 0.86, cor=BORDA, larg=0.75)

    # III. Estimação e incerteza
    x3, w3 = 8.85, 4.23
    cartao(x3, w3, "III. QUÃO PRECISO")
    linhas_ = (("Máxima verossimilhança", "código próprio, conferido"),
               ("Erro-padrão agrupado", f"por curso × ciclo ({n['g_conj']} grupos)"),
               ("Poucos grupos: score bootstrap", f"p = {v(n['p_score'], 3)}"),
               ("Três testes: correção de Holm", f"p = {v(n['p_holm'], 3)}"))
    for k, (a, b) in enumerate(linhas_):
        y = topo + 0.62 + k * 0.95
        texto(sl, x3 + 0.2, y, w3 - 0.35, 0.85, [[(a, 12.5, True, VERDE)], [(b, 12.5, False, TEXTO)]],
              anchor=MSO_ANCHOR.TOP)

    caixa(sl, 0.25, 5.65, 12.83, 0.95,
          [[("É exploratório: ", 14, True, BRANCO),
            (f"fixar a UF foi decidido depois de ver o modelo base, que dá ×{v(n['rc_m1'])} "
             f"(IC {v(n['rc_m1_inf'])} a {v(n['rc_m1_sup'])}).", 14, False, BRANCO)]],
          fill=VERDE, nome="Por que a UF", margem=0.3)
    fontes(sl, "Fontes: VL_estimativas.csv e VL_resumo.json (VL-1, VL-2 e M1; adendo 52e; doc 57x; auditoria 48); "
               "portao_r1_ivs_oficial.json; scripts/rdd_bolsa/25_escolha_dap.py e 50_escolha_localizacao_par.py.")
    notas(sl, (f"Pedido de 14/11: explicar como o logit foi feito, além da equação. (I) A bolsa é função em degraus do "
               f"IVS (a regra reproduz {n['r1_c1']}/{n['n_c1']} e {n['r1_c2']}/{n['n_c2']} municípios) e o IVS entra "
               "como spline linear contínuo com nós nos cortes (reta com dobras, sem salto); por isso o β vem dos "
               "saltos, como na nota 13 de Bobba et al. Só perto do corte (VL-2, ±0,05): "
               f"×{v(n['rc_vl2'])} (IC {v(n['rc_vl2_inf'])} a {v(n['rc_vl2_sup'])}), mesma direção, inconclusivo. "
               "(II) O que fica fixo responde à pergunta da banca de 04/11: o candidato se cancela no denominador; o "
               f"par UF de trabalho × UF da vaga entra como {n['col_ef']} colunas 0/1 (salário de mercado, conselho "
               "regional, família na UF); não há fixo de município, porque a bolsa é constante no município. (III) "
               "Newton–Raphson no script 25; antes de estimar, o código reproduz as estimativas gravadas (diferença ≤ "
               f"1e−8). EP sanduíche CR1 por conjunto de escolha (curso × ciclo): EP do β {v(n['ep_cl'], 3)}, o dobro do "
               f"ingênuo ({v(n['ep_mle'], 3)}). Score bootstrap de Kline–Santos (2012), Rademacher. Holm entre VL-1 "
               "ciclos 1–3, VL-1 ciclo 2 e VL-2. Faixa: dentro da UF a distância pesa mais "
               f"(×{v(n['x_dist'])} contra ×{v(n['x_dist_m1'])} por 100 km) e a bolsa também (×{v(n['rc'])}); a "
               "diferença de log RC entre VL-1 e M1 tem IC que exclui 0 (doc 57x); a especificação com o par veio "
               "depois do M1 (adendo 52e, pós-resultado)."))
    return sl


def s_identificacao(M, prs, n):
    sl = M.novo(prs, "Identificação: as premissas do logit condicional")
    cab = (("Premissa", 0.25, 4.1), ("Como atendemos", 4.45, 6.6), ("Situação", 11.15, 1.93))
    for t, x, w in cab:
        texto(sl, x, 0.92, w, 0.3, [[(t, 11.5, True, VERDE2)]])
    linha(sl, 0.25, 1.25, 13.08, 1.25, cor=VERDE, larg=1.5)
    linhas_ = (
        ("Escolha sincera", "Supomos que cada um pôs em 1º a vaga que prefere. Não dá para testar.", "SUPOSTO",
         "suposto"),
        ("Cardápio conhecido", "O edital publica todas as vagas; supomos que o médico viu todas.", "SUPOSTO",
         "suposto"),
        ("Bolsa sem relação com o que não medimos",
         f"A bolsa segue a regra do IVS ({n['r1_c1']}/{n['n_c1']}; {n['r1_c2']}/{n['n_c2']} municípios). Mas no corte "
         "mudam outras regras: é um pacote.", "EM PARTE", "parte"),
        ("Alternativas independentes",
         f"Não vale (logit aninhado rodado no modelo base, sem o par de UFs: λ = {v(n['lambda'])}), mas o peso da "
         f"bolsa quase não muda ({v(n['b_m9'], 3)} contra {v(n['b_m1'], 3)}).", "NÃO VALE; β ESTÁVEL", "nao"),
    )
    for k, (tit, como, rot, tp) in enumerate(linhas_):
        y = 1.42 + k * 1.3
        texto(sl, 0.25, y, 4.0, 1.15, [[(tit, 16, True, TEXTO)]])
        texto(sl, 4.45, y, 6.5, 1.15, [[(como, 13, False, TEXTO)]])
        pill(sl, 11.15, y + 0.4, 1.93, rot, tp, h=0.36, tam=9.5)
        linha(sl, 0.25, y + 1.2, 13.08, y + 1.2, cor=BORDA, larg=0.75)
    fontes(sl, "Fontes: portao_r1_ivs_oficial.json; P1_estimativas.csv (M1 e M9, ciclos 1–3); VL_resumo.json (VL-1); "
               "docs/auditorias/18 (políticas nos mesmos cortes).")
    notas(sl, ("Só as premissas do logit condicional e como atendemos (ou não) a cada uma. Escolha sincera: ninguém "
               "deixa de pôr em 1º a vaga preferida por medo de não passar na nota (premissa do autor, 11/11/2026). "
               "Bolsa sem relação com o que não medimos: curva do IVS e par de UFs no modelo; outras políticas "
               "federais usam os mesmos cortes (auditoria 18). A independência das alternativas (IIA) não vale por "
               "inteiro: o aninhado por região de saúde rejeita λ = 1 (vagas da mesma região se substituem mais); o "
               "peso da bolsa no aninhado fica perto do logit condicional (modelo base M1, sem o par de UFs). O logit "
               f"misto (M8) mostra que o peso varia entre candidatos: o β é uma média. O β vem de {n['pares_var']} pares "
               f"de UFs e {mil(n['cand_var'])} candidatos com variação de bolsa (slide anterior)."))
    return sl


def s_resultados(M, prs, n):
    sl = M.novo(prs, f"Resultados: +R$ 5 mil multiplicam a chance por {v(n['rc'])}")
    subtitulo(sl, 0.25, 0.85, 7.9, "I. O que cada termo faz com a chance de uma vaga",
              "ponto = estimativa  ·  barra = IC 95%")
    sl.shapes.add_picture(str(FIG_COEF), Inches(0.2), Inches(1.5), width=Inches(7.95))
    cards = ((f"×{v(n['rc'])}", "+R$ 5 mil, na mesma UF", f"IC 95%: {v(n['rc_inf'])} a {v(n['rc_sup'])}", True),
             (f"{round(n['km'])} km", "o mesmo peso que +R$ 5 mil", "", False),
             (f"×{v(n['rc_c2'])}", "só no ciclo 2", "ciclos 1 e 3: o IC contém 1", False))
    for k, (num, rot, sub, escuro) in enumerate(cards):
        y = 0.9 + k * 1.92
        pars = [[(num, 36, True, BRANCO if escuro else VERDE)], [(rot, 15, True, BRANCO if escuro else TEXTO)]]
        if sub:
            pars.append([(sub, 12, False, "DDEBDD" if escuro else CINZA)])
        caixa(sl, 8.45, y, 4.63, 1.75, pars, fill=VERDE if escuro else CLARO, line=None if escuro else BORDA,
              nome=f"Cartão {k}", margem=0.25)
    fontes(sl, "Fontes: output/rdd_bolsa/VL_estimativas.csv (VL-1, adendo 52e; doc 57x; auditoria 48); VG_estimativas.csv "
               "(ciclos 1 e 3, adendo 52g); figura de scripts/apresentacao/gerar_figuras_banca_final.py.")
    notas(sl, (f"Leitura: cada × é e^coeficiente. Bolsa: β = {v(n['b'], 3)} por R$ 1 mil; 5β = {v(n['b5'], 3)}; "
               f"e^{v(n['b5'], 3)} = {v(n['rc'])}; p de Holm {v(n['p_holm'], 3)}. Km equivalentes: 5β ÷ |γ| × 100 = "
               f"{v(n['b5'], 3)} ÷ {v(-n['dist'], 3)} × 100 = {round(n['km'])} km. Ciclo 2: IC {v(n['rc_c2_inf'])} a "
               f"{v(n['rc_c2_sup'])}; ciclos 1 e 3: ×{v(n['rc_c1'])} e ×{v(n['rc_c3'])}. Distância, mesma região e "
               "mesmo município são controles, mas ajudam a ler o tamanho da bolsa: estar na mesma região de saúde "
               "pesa mais que toda a bolsa extra."))
    return sl


def s_robustez(M, prs, n):
    sl = M.novo(prs, "Robustez: o ×1,47 se mantém com mais dados".replace("1,47", v(n["rc"])))
    sl.shapes.add_picture(str(FIG_ROB), Inches(0.15), Inches(0.92), width=Inches(8.1))
    lo, hi = min(n["rc"], n["rc_log"], n["rc_vl3"]), max(n["rc"], n["rc_log"], n["rc_vl3"])
    caixa(sl, 8.4, 0.95, 4.68, 2.9,
          [[("CONCLUSÃO", 11, True, "B9E4B1")],
           [(f"Sempre na mesma UF, com todos os dados: de ×{v(lo)} a ×{v(hi)}.", 17, True, BRANCO)],
           [("Com menos dados (perto do corte; ciclos 1 e 3), o IC contém 1: inconclusivo, não contrário.", 13, False,
             "DDEBDD")]],
          fill=VERDE, nome="Conclusão robustez", margem=0.25, esp=6)
    caixa(sl, 8.4, 4.05, 4.68, 1.0,
          [[("Verde: ", 13, True, MEDIO), ("IC exclui 1.   ", 13, False, TEXTO),
            ("Cinza: ", 13, True, CINZA), ("IC contém 1.", 13, False, TEXTO)]],
          fill=CLARO, line=BORDA, nome="Como ler", margem=0.25)
    fontes(sl, "Fontes: output/rdd_bolsa/VL_estimativas.csv (VL-1 a VL-3; adendo 52e); VG_estimativas.csv (por ciclo; "
               "adendo 52g); figura de scripts/apresentacao/gerar_figuras_banca_final.py.")
    notas(sl, (f"Anotação do grupo: evidenciar a conclusão e como chegamos a ela. O pré-registrado compara vagas de "
               f"todas as UFs. Por que o × e não o coeficiente: é o mesmo número, ln({v(n['rc'])}) = {v(n['b5'], 3)} = "
               "5 × β; o β sozinho está numa escala sem unidade, o × diz quantas vezes a chance muda; o teste (IC "
               "exclui 1) é o mesmo do β (IC exclui 0)."))
    return sl


def s_metade(M, prs, n):
    sl = M.novo(prs, "Metade de quem ocupa a vaga já trabalhava ali")
    kpis = ((f"{round(n['origem'])}%", "já tinham vínculo no município antes de entrar",
             f"IC 95%: {round(n['origem_lo'])}% a {round(n['origem_hi'])}%"),
            (f"+{v(n['horas'], 1)} h/sem", "a mais no CNES, num programa de 20 h",
             f"IC 95%: +{v(n['horas_lo'], 1)} a +{v(n['horas_hi'], 1)}"))
    for k, (num, rot, ic) in enumerate(kpis):
        caixa(sl, 0.25, 0.95 + k * 2.55, 5.6, 2.35,
              [[(num, 42, True, VERDE)], [(rot, 15, True, TEXTO)], [(ic, 11, False, CINZA)]],
              fill=CLARO, line=BORDA, nome=f"KPI {k}", margem=0.3)
    subtitulo(sl, 6.2, 0.95, 6.9, "O que isso significa")
    pontos = (("Nem toda vaga ocupada é um médico novo", "metade já estava lá"),
              ("O ganho aparece mais em horas", "parte das 20 h substitui horas que já fazia"),
              ("Combina com a escolha da vaga", f"na mesma região de saúde, a chance é ×{v(n['x_reg'], 1)}"))
    for k, (tit, corpo) in enumerate(pontos):
        y = 1.45 + k * 1.3
        caixa(sl, 6.2, y, 0.09, 1.0, [], fill=VERDE, forma=MSO_SHAPE.RECTANGLE, nome="Barra")
        texto(sl, 6.45, y, 6.6, 1.0, [[(tit, 15, True, TEXTO)], [(corpo, 13, False, TEXTO)]])
    caixa(sl, 6.2, 5.55, 6.88, 0.75,
          [[("Descritivo: ", 12, True, CINZA), ("mesmo médico antes e depois, sem grupo de comparação.", 12, False,
                                               CINZA)]],
          fill=BRANCO, line=BORDA, nome="Descritivo")
    fontes(sl, "Fontes: CNES/DATASUS; quadros de vagas e homologações do PMM-E (SGTES/MS). output/rdd_bolsa/"
               "S57_resumo.json (P4: vínculo anterior e horas totais, ciclos 1 e 2); VL_estimativas.csv.")
    notas(sl, ("Pedido de 11/11: mostrar na discussão que boa parte dos médicos já estava no município. São números do "
               "P4 (trajetória no CNES), descritivos: compara o mesmo médico antes e depois, sem grupo de comparação; "
               "horas cadastradas no CNES não são horas trabalhadas. Em metade dos casos, o programa passa a pagar "
               "quem já estava lá; o cadastro sobe menos que as 20 h da bolsa. A ligação com a escolha: a mesma "
               "região de saúde multiplica a chance por ~3 no VL-1."))
    return sl


def s_conclusao(M, prs, n):
    sl = M.novo(prs, "Conclusão: a bolsa pesa na escolha, mas pouco")
    caixa(sl, 0.25, 0.92, 12.83, 1.5,
          [[("RESPOSTA", 11, True, "B9E4B1")],
           [(f"Sim: na mesma UF, +R$ 5 mil multiplicam a chance por {v(n['rc'])}", 22, True, BRANCO)],
           [(f"≈ {round(n['km'])} km mais perto  ·  forte só no ciclo 2 (×{v(n['rc_c2'])})", 15, False, "DDEBDD")]],
          fill=VERDE, nome="Resposta", margem=0.3)
    blocos = (("✓  Dá para afirmar", (f"A bolsa maior é preferida (×{v(n['rc'])})",
                                      f"O peso é moderado: R$ 5 mil ≈ {round(n['km'])} km",
                                      "O médico escolhe perto de onde já trabalha")),
              ("✗  Não dá para afirmar", ("Que leva mais médicos ao município",
                                          "Que é só o dinheiro (é um pacote)",
                                          "Que vale em todo ciclo")))
    for k, (tit, itens) in enumerate(blocos):
        x = 0.25 + k * 6.5
        caixa(sl, x, 2.62, 6.33, 2.75, [[(tit, 18, True, VERDE if k == 0 else "7A1C17")]] +
              [[("•  " + it, 16, False, TEXTO)] for it in itens],
              fill=CLARO if k == 0 else BRANCO, line=BORDA, anchor=MSO_ANCHOR.MIDDLE, nome=tit, margem=0.3, esp=10)
    caixa(sl, 0.25, 5.57, 12.83, 0.95,
          [[("Para a política: ", 15, True, "B9E4B1"),
            ("pagar mais muda a escolha entre vagas próximas; não mostramos que atraia médicos de longe.", 15, False,
             BRANCO)]],
          fill=VERDE, nome="Política", margem=0.3)
    fontes(sl, "Fontes: VL_estimativas.csv (VL-1, adendo 52e); VG_estimativas.csv (adendo 52g); S57_resumo.json (P4).")
    notas(sl, ("Conclusão e 'incentivo limitado' fundidos: uma resposta, dois blocos (dá / não dá para afirmar) e a "
               "leitura para a política. Não dá para afirmar: que a bolsa leva mais médicos ao município (vemos a "
               "escolha, não a chegada); que é só o dinheiro (no corte do IVS muda um pacote de regras); que o efeito "
               "vale em todo ciclo (só o ciclo 2 é forte). Metade de quem ocupa a vaga já estava no município."))
    return sl


def s_limitacoes(M, prs, n):
    sl = M.novo(prs, "Limitações")
    caixas = (("O que o resultado não mostra",
               (("Escolher não é ir", "não mostra mais médicos chegando"),
                ("Pacote, não só dinheiro", "outras regras mudam no mesmo corte"),
                ("Local anterior pelo CNES", "é onde trabalhava, não onde mora"))),
              ("Quão firme é o resultado",
               (("Fixar a UF veio depois dos dados", "exploratório: sugere, não confirma"),
                (f"Sem fixar a UF: ×{v(n['rc_m1'])}", "IC contém 1: não descarta efeito nulo"),
                ("Só o ciclo 2 é forte", "não generaliza para outros ciclos"))))
    for k, (tit, itens) in enumerate(caixas):
        x = 0.25 + k * 6.5
        pars = [[(tit, 21, True, VERDE)]]
        for t, imp in itens:
            pars.append([(t, 17, True, TEXTO)])
            pars.append([("→ " + imp, 14.5, False, MEDIO)])
        cx = caixa(sl, x, 0.95, 6.33, 5.6, pars, fill=CLARO, line=BORDA, anchor=MSO_ANCHOR.MIDDLE, nome=tit,
                   margem=0.45)
        for j, par in enumerate(cx.text_frame.paragraphs):  # item colado à sua consequência; espaço entre itens
            par.space_after = Pt(16 if j == 0 else (2 if j % 2 == 1 else 20))
    fontes(sl, "Fontes: VL_estimativas.csv (VL-1 e M1); VG_estimativas.csv (adendo 52g); auditorias 18 e 48; portão G1.")
    notas(sl, ("Seis limitações em duas caixas. Escolher não é ir: vemos a 1ª opção na inscrição, não a chegada ao "
               "município. Pacote: no corte de IVS outras regras mudam junto com a bolsa; o efeito do dinheiro não sai "
               "isolado. Local anterior pelo CNES: é onde o médico trabalhava, não onde mora; explica a escolha, não a "
               f"causa. Sem fixar a UF, no plano pré-registrado: ×{v(n['rc_m1'])} (IC {v(n['rc_m1_inf'])} a "
               f"{v(n['rc_m1_sup'])}). Ciclo 1 ×{v(n['rc_c1'])} e ciclo 3 ×{v(n['rc_c3'])}, com IC que contém 1. A "
               "escolha sincera é premissa (slide de identificação)."))
    return sl


NOVOS = {"cadeia1": lambda M, p, n: s_cadeia(M, p, n, 2), "cadeia2": lambda M, p, n: s_cadeia(M, p, n, 3),
         "hipotese": s_hipotese, "linhas": s_linhas, "modelo": s_modelo, "passos": s_passos, "estimacao": s_estimacao,
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
                dentro = [r for r in runs if antigo in r.text]
                if len(dentro) == 1 and "\n" not in novo:  # cabe num run só: troca ali e mantém a formatação dos outros
                    dentro[0].text = dentro[0].text.replace(antigo, novo)
                    achou += 1
                    continue
                runs[0].text = inteiro.replace(antigo, novo)
                for r in runs[1:]:
                    r._r.getparent().remove(r._r)
                for br in par._p.findall("a:br", NS):
                    par._p.remove(br)
                if "\n" in runs[0].text:  # quebra de linha pedida: <a:br/> e um segundo run com a mesma formatação
                    t1, t2 = runs[0].text.split("\n", 1)
                    runs[0].text = t1
                    br = etree.Element("{%s}br" % NS["a"])
                    rpr = runs[0]._r.find("a:rPr", NS)
                    if rpr is not None:
                        br.append(copy.deepcopy(rpr))
                    r2 = copy.deepcopy(runs[0]._r)
                    r2.find("a:t", NS).text = t2
                    runs[0]._r.addnext(br)
                    br.addnext(r2)
                if not runs[0].text.strip() and len(sh.text_frame.paragraphs) > 1:
                    par._p.getparent().remove(par._p)
                achou += 1
        if achou != 1:
            raise SystemExit(f"ERRO: esperava 1 {antigo!r} no slide {num} do grupo; achei {achou}")
        feitas.append(f"slide {num} do grupo: {antigo.strip()!r} → {novo!r}")
    return feitas


QN_MT = "{http://schemas.openxmlformats.org/officeDocument/2006/math}t"
DIR_EQ = OUT / "equacoes"


def corrigir_anexo(prs) -> list[str]:
    """Slide 32 do grupo: a soma corre em t (δ^t), não em i. Troca o índice no OMML e redesenha a imagem de reserva."""
    s = prs.slides[31]
    ts = [t for t in s._element.iter(QN_MT) if t.text == "𝑖"]
    if len(ts) != 1:
        raise SystemExit(f"ERRO: anexo: esperava 1 índice 𝑖 na equação; achei {len(ts)}")
    ts[0].text = "𝑡"
    fb = [f for f in s._element.iter("{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback")
          if f.find(".//a:blip", NS) is not None]
    if len(fb) != 1:
        raise SystemExit("ERRO: anexo: esperava 1 imagem de reserva da equação")
    ext = fb[0].find(".//a:xfrm/a:ext", NS)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    matplotlib.rcParams.update({"mathtext.fontset": "stix"})
    w, h, dpi = int(ext.get("cx")) / 914400, int(ext.get("cy")) / 914400, 200
    fig = plt.figure(figsize=(w, h), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    txt = ax.text(0.5, 0.5, r"$\sum_{t=0}^{T}\delta^{t}\left[\frac{E(w_{mt}^{(s)})}{p_{mt}} - c_{mt}^{(s)}\right]$",
                  ha="center", va="center", fontsize=20)
    fig.canvas.draw()
    bb = txt.get_window_extent(renderer=fig.canvas.get_renderer())
    txt.set_fontsize(20 * min(0.94 * w * dpi / bb.width, 0.9 * h * dpi / bb.height))
    DIR_EQ.mkdir(parents=True, exist_ok=True)
    img = DIR_EQ / "anexo_moehling_indice_t.png"
    fig.savefig(img, dpi=dpi, transparent=True, metadata={"Software": None})
    plt.close(fig)
    _, rid = s.part.get_or_add_image_part(str(img))
    fb[0].find(".//a:blip", NS).set("{%s}embed" % NS["r"], rid)
    return ["slide 32 do grupo: índice da soma i → t (OMML e imagem de reserva)"]


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
        raise SystemExit("ERRO: o deck do grupo de 14/11 mudou (hash diferente)")
    prs = Presentation(str(ENT))
    if len(prs.slides) != N_ENT:
        raise SystemExit(f"ERRO: esperava {N_ENT} slides no deck do grupo")
    n = numeros()
    feitas = corrigir(prs) + corrigir_anexo(prs) + tirar_anotacoes(prs)
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
        manifesto.append({"posicao": pos, "origem": "grupo 14/11" if t == "G" else "novo", "slide_origem": k,
                          "secao": secao, "titulo": " ".join(titulo.split())})
    OUT.mkdir(parents=True, exist_ok=True)
    pptx = OUT / f"{ARQ}.pptx"
    prs.save(str(pptx))
    return {"n": n, "feitas": feitas, "manifesto": manifesto, "pptx": pptx}


def converter_pdf(pptx: Path, pdf: Path) -> bool:
    """LibreOffice (soffice); sem ele, no Windows, o PowerPoint instalado (COM)."""
    with tempfile.TemporaryDirectory() as tmp:
        gerado = Path(tmp) / (pptx.stem + ".pdf")
        try:
            r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, str(pptx)],
                               capture_output=True, text=True, timeout=600)
        except FileNotFoundError:
            if sys.platform != "win32":
                return False
            ps = ("$pp = New-Object -ComObject PowerPoint.Application; "
                  f"$d = $pp.Presentations.Open('{pptx.resolve()}', $true, $false, $false); "
                  f"$d.SaveAs('{gerado}', 32); $d.Close(); $pp.Quit()")
            r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True,
                               timeout=600)
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
