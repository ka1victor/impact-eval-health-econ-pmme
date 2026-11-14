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
F_NB2 = ROOT / "output/apresentacao_banca2/numeros_banca2.json"  # ESC_*: descritiva da escolha
F_EX = OUT / "exemplo_logit_real.json"
FIG_COEF, FIG_ROB = OUT / "figuras/coeficientes_vl1.png", OUT / "figuras/robustez_vl1.png"
FIG_SEIS = OUT / "figuras/coeficientes_vl1_seis.png"  # slide de resultado do colega (versão conciliada)
DOC = "docs/07_apresentacoes/banca_final/03_deck_banca_final_grupo.md"

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
SECOES = ("Motivação", "Pergunta", "Literatura", "Hipótese", "Base de Dados", "Análise Descritiva", "Metodologia",
          "Identificação", "Resultados", "Robustez", "Discussão")
VERDE, VERDE2, MEDIO, CLARO, BORDA = "114719", "056429", "2E7D46", "EEF3ED", "D5E2D8"
TEXTO, CINZA, BRANCO, APAGADO, FUNDO_AP = "1A1A1A", "5E6660", "FFFFFF", "B9C1BB", "F5F7F5"
# destaque (14/11): o que o trabalho estima e observa, e o que muda no exemplo
ACENTO, ACENTO_CLARO, ACENTO_ESCURO = "D99A2B", "FFF2D6", "8A5A00"
PILL = {"reduz": ("F5B5B0", "7A1C17"), "eleva": ("B9E4B1", VERDE), "testado": (MEDIO, BRANCO),
        "pareamento": ("B9E4B1", VERDE), "controle": ("DDE3DE", "39413B"), "suposto": ("DDE3DE", "39413B"),
        "parte": ("F6DDB0", "6B4A0B"), "nao": ("F5B5B0", "7A1C17"), "obs": ("B9E4B1", VERDE),
        "naoobs": ("DDE3DE", "39413B"), "estima": ("FFD98A", "8A5A00")}

# Ideias do deck de um colega (slide das vagas A, B e C; anexos 3 e 4; o slide de resultado). A nossa versão, sem
# elas, foi para o colega conciliar (pedido do autor de 14/11); com --com-colega sai a versão conciliada, em
# deck_banca_final_grupo_conciliado.pptx.
COM_IDEIAS_COLEGA = False
IDEIAS_COLEGA = {"intuicao", "formal", "alternativas"}

# ("G", n): slide n do deck do grupo (ordem de apresentação); ("N", nome): slide novo. Seção do rodapé.
ORDEM = [
    ("G", 1, None), ("G", 2, None), ("G", 3, "Motivação"), ("G", 4, "Motivação"), ("G", 5, "Motivação"),
    ("G", 6, "Motivação"), ("G", 7, "Motivação"), ("G", 8, None), ("G", 9, None), ("G", 10, None),
    ("N", "cadeia1", "Literatura"), ("N", "cadeia2", "Literatura"),
    ("G", 13, None), ("N", "hipotese", "Hipótese"),
    ("G", 15, None), ("G", 16, "Base de Dados"), ("N", "linhas", "Base de Dados"),
    ("G", 17, "Análise Descritiva"),
    ("G", 18, None), ("N", "intuicao", "Metodologia"), ("N", "modelo", "Metodologia"), ("N", "passos", "Metodologia"),
    ("N", "identificacao", "Identificação"),
    ("G", 23, None), ("N", "resultados", "Resultados"), ("N", "robustez", "Robustez"),
    ("N", "limitacoes", "Discussão"), ("N", "conclusao", "Discussão"),
    # anexos (rodada 10, 14/11): Literatura e Estimação saem do corpo para encurtar a fala
    ("G", 31, None), ("G", 11, None), ("G", 32, None), ("G", 33, None), ("N", "estimacao", None),
    ("N", "formal", None), ("N", "alternativas", None),
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
    (17, "Os médicos escolhem vagas perto de onde já trabalham", "Candidatos escolhem perto de onde trabalham"),
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
    (17, "A origem é o vínculo médico anterior no CNES, não a residência.",
     "O local anterior é o vínculo médico no CNES antes da inscrição, não a residência."),
    # anexo: decisões do autor de 11/11 (doc 02, §1, itens 3 e 19): sem altruísmo (α fica só para o par de UFs) e a
    # política decide a escolha, não o preenchimento
    (32, "; o altruísmo do médico (α) compensa em parte.", "."),
    (32, ") por (B)", ") pela bolsa (B)"),  # o "E(w|B)" vem em runs separados
] + [
    # títulos sem artigo no começo (pedido do autor de 14/11)
    (3, "A escassez de especialistas já é tratada como urgência sanitária",
     "Escassez de especialistas já é tratada como urgência sanitária", "exato"),
    (11, "O modelo combina dois elementos da teoria", "Anexo 1: modelo combina dois elementos da teoria", "exato"),
    (32, "Anexo 1: Literatura Teórica - Equação", "Anexo 2: literatura teórica, a equação", "exato"),
    (16, "Os dados ligam os editais do PMM-E ao CNES", "Dados ligam os editais do PMM-E ao CNES", "exato"),
    (33, "A bolsa segue exatamente o IVS do município", "Anexo 3: bolsa segue exatamente o IVS do município", "exato"),
] + [(n, "A vulnerabilidade social define o valor da bolsa do PMM-E",
      "Vulnerabilidade social define o valor da bolsa do PMM-E", "exato") for n in (4, 5, 6)] + [
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
    nb2 = json.loads(F_NB2.read_text(encoding="utf-8"))["numeros"]
    esc = {k: str(nb2[c]["valor"]) for k, c in (("uf", "ESC_UF"), ("mun", "ESC_MUN"), ("p50", "ESC_DIST_P50"),
                                                ("p75", "ESC_DIST_P75"), ("n", "ESC_N"))}
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
        "ex": ex, "esc": esc,
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
    """Equação em runs de Montserrat, sem itálico (a pedido do autor: o itálico fino ficava ilegível):
    _{...} subscrito, ^{...} sobrescrito, `...` igual ao resto."""
    runs, pos = [], 0
    for m in re.finditer(r"_\{([^}]*)\}|\^\{([^}]*)\}|`([^`]*)`", texto_eq):
        if m.start() > pos:
            runs.append((texto_eq[pos:m.start()], tam, False, cor, "Montserrat", False, 0))
        if m.group(1) is not None:
            runs.append((m.group(1), tam, False, cor, "Montserrat", False, -25000))
        elif m.group(2) is not None:
            runs.append((m.group(2), tam, False, cor, "Montserrat", False, 30000))
        else:
            runs.append((m.group(3), tam, False, cor, "Montserrat", False, 0))
        pos = m.end()
    if pos < len(texto_eq):
        runs.append((texto_eq[pos:], tam, False, cor, "Montserrat", False, 0))
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


def alinhar_titulo(slide) -> None:
    """Título na faixa verde centrado na vertical, sem margem de cima (nos slides do grupo vinha colado no topo)."""
    for sh in slide.shapes:
        if (sh.has_text_frame and sh.top is not None and sh.top < Inches(0.05) and sh.left < Inches(0.3)
                and Inches(0.6) < sh.height < Inches(0.8)):
            tf = sh.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf.margin_top = tf.margin_bottom = 0


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
FONTE_PUBLICA = ("Fontes: editais e quadros de vagas do PMM-E (SGTES/MS), ciclos 1–3; CNES/DATASUS; Ipea, IVS 2010; IBGE. "
                 "Elaboração própria.")
CRM_EX = "CRM 123456/MG"  # ilustrativo: a base não guarda identificação do médico


TITULO_CADEIA = "Cadeia causal: da bolsa aos desfechos na saúde"


def s_cadeia(M, prs, n, etapa: int):
    """Cadeia causal. Em âmbar, o que o trabalho estima (o peso da remuneração) e observa (a 1ª opção)."""
    sl = M.novo(prs, TITULO_CADEIA)
    ap = etapa < 3

    def rotulo(y, num, t, apagado=False, sub=None):
        cor = APAGADO if apagado else VERDE
        caixa(sl, 0.25, y, 0.44, 0.44, [[(str(num), 15, True, BRANCO)]], fill=cor, forma=MSO_SHAPE.OVAL,
              align=PP_ALIGN.CENTER, margem=0, nome=f"Etapa {num}")
        pars = [[(t, 11.5, True, cor)]] + ([[(sub, 10, False, cor if apagado else CINZA)]] if sub else [])
        texto(sl, 0.25, y + 0.5, 1.85, 0.7, pars, anchor=MSO_ANCHOR.TOP)

    # 1. Regra
    rotulo(0.92, 1, "REGRA")
    caixa(sl, 2.2, 0.9, 3.1, 0.8, [[("IVS do município", 15, True, VERDE)], [("Ipea, 2010", 11, False, CINZA)]],
          fill=CLARO, line=BORDA)
    seta(sl, 5.32, 1.3, 5.72, 1.3)
    caixa(sl, 5.75, 0.9, 7.33, 0.8, [], fill=CLARO, line=BORDA, nome="Faixas")
    texto(sl, 5.92, 0.94, 1.85, 0.72, [[("Bolsa mensal", 15, True, VERDE)]])
    for k, (faixa, valor) in enumerate((("IVS até 0,300", "R$ 10 mil"), ("0,301 a 0,400", "R$ 15 mil"),
                                        ("acima de 0,400", "R$ 20 mil"))):
        caixa(sl, 7.85 + k * 1.75, 0.99, 1.62, 0.62, [[(faixa, 10, False, TEXTO)], [(valor, 13, True, VERDE)]],
              fill=BRANCO, line=BORDA, align=PP_ALIGN.CENTER, margem=0.04)
    # 2. Escolha do médico: a remuneração (o que estimamos) primeiro, depois o que reduz o valor
    rotulo(1.98, 2, "ESCOLHA DO MÉDICO")
    cart = (("estima", "ELEVA O VALOR", "Remuneração", "bolsa maior", "Moehling et al. (2020)"),
            ("reduz", "REDUZ O VALOR", "Custo de viver ali", "deslocamento, distância de casa",
             "Redding & Rossi-Hansberg (2017)"),
            ("reduz", "REDUZ O VALOR", "Custo de trabalhar ali", "falta equipe e equipamento",
             "Choné & Ma (2011)"))
    for k, (tp, rot, tit, corpo, ref) in enumerate(cart):
        x = 2.2 + k * 3.69
        dest = tp == "estima"
        caixa(sl, x, 1.95, 3.5, 1.62, [], fill=ACENTO_CLARO if dest else CLARO, line=ACENTO if dest else BORDA,
              nome=f"Fator {tit}")
        pill(sl, x + 0.15, 2.05, 1.45, rot, "estima" if dest else "reduz")
        texto(sl, x + 0.15, 2.4, 3.2, 0.36, [[(tit, 17, True, ACENTO_ESCURO if dest else VERDE)]])
        texto(sl, x + 0.15, 2.8, 3.2, 0.4, [[(corpo, 13.5, False, TEXTO)]], anchor=MSO_ANCHOR.TOP)
        texto(sl, x + 0.15, 3.24, 3.2, 0.26, [[(ref, 9.5, True, ACENTO_ESCURO if dest else VERDE2)]])
        if k < 2:
            seta(sl, x + 1.75, 3.59, x + 1.75, 3.86, cor=ACENTO if dest else MEDIO)
        else:
            seta(sl, x + 0.9, 3.59, 8.75, 3.88, cor=MEDIO)
    # valor (não observado) → 1ª opção (observada)
    caixa(sl, 2.2, 3.9, 6.9, 0.7, [], fill=CLARO, line=VERDE, nome="Valor da vaga")
    texto(sl, 2.38, 3.92, 4.9, 0.66, [[("Valor da vaga para o médico", 16, True, VERDE)]])
    pill(sl, 7.48, 4.09, 1.47, "NÃO OBSERVADO", "naoobs", h=0.32)
    seta(sl, 9.12, 4.25, 9.5, 4.25, cor=ACENTO)
    caixa(sl, 9.53, 3.9, 3.55, 0.7, [], fill=ACENTO_CLARO, line=ACENTO, nome="1a opção")
    texto(sl, 9.7, 3.92, 2.0, 0.66, [[("1ª opção", 16, True, ACENTO_ESCURO)]])
    pill(sl, 11.72, 4.09, 1.24, "OBSERVADA", "estima", h=0.32)
    # o que estimamos: a faixa mais importante do slide
    caixa(sl, 2.2, 4.78, 10.88, 0.95,
          [[("O que estimamos: ", 17, True, "FFD98A"),
            ("o peso da remuneração na chance de a vaga ser a 1ª opção", 17, True, BRANCO)],
           [("chance = probabilidade de o médico pôr a vaga em 1º lugar", 12.5, False, "DDEBDD")]],
          fill=VERDE, nome="Métrica", margem=0.25)
    # 3. Da vaga à saúde
    rotulo(5.86, 3, "DA VAGA À SAÚDE", apagado=ap, sub="fora do que estimamos")
    # rodada 9 (14/11): uma explicação curta em cada bloco
    elos = (("Quantos médicos a escolhem", "candidatos de 1ª opção por vaga"),
            ("Vaga ocupada", "médico homologado e em atividade"),
            ("Capacidade", "vínculos e horas do especialista no CNES"),
            ("Produção e acesso", "consultas, exames e cirurgias feitos"),
            ("Saúde", "menos espera e internações evitáveis"))
    for k, (tit, ex_) in enumerate(elos):
        x = 2.2 + k * 2.22
        caixa(sl, x, 5.84, 2.0, 1.0, [[(tit, 12, True, APAGADO if ap else VERDE)],
                                      [(ex_, 10, False, APAGADO if ap else CINZA)]],
              fill=FUNDO_AP if ap else CLARO, line=None if ap else BORDA, nome=f"Elo {tit}", margem=0.1, esp=2)
        if k < 4:
            seta(sl, x + 2.01, 6.34, x + 2.21, 6.34, cor=APAGADO if ap else VERDE, larg=1.5)
    fontes(sl, "Fontes: Moehling et al. (2020); Choné & Ma (2011); Redding & Rossi-Hansberg (2017); Burdett, Shi & "
               "Wright (2001); edital SGTES/MS nº 3/2025; Ipea, IVS 2010.")
    notas(sl, ("Cadeia causal, etapa por etapa. Em âmbar, o que o trabalho estima (o peso da remuneração) e o que "
               "observa (a 1ª opção). " + ("Primeiro a regra e a escolha do médico: o que eleva o valor da vaga (a "
               "bolsa) e o que o reduz (deslocamento, esforço). " if ap else "Agora a etapa 3: da vaga escolhida à "
               "saúde (quantos médicos a escolhem, vaga ocupada, vínculos e horas, consultas e exames, espera e "
               "internações); não é estimada aqui: o trabalho testa só o elo bolsa → valor → 1ª opção. ") +
               "O valor da vaga é a utilidade: a soma do que eleva e do que reduz; não aparece nos dados. O que aparece "
               "é a 1ª opção; o modelo lê nas escolhas quanto a bolsa pesa no valor. O resultado só aparece depois, no "
               "slide de resultados. Origem do diagrama: docs/07_apresentacoes/banca_final/"
               "01_diagrama_teoria_mudanca.md."))
    return sl


def s_hipotese(M, prs, n):
    """Hipótese com o exemplo real: em cinza o que é quase igual (IVS, distância), em âmbar o que muda (a bolsa)."""
    ex = n["ex"]
    a, b = ex["vaga_a"], ex["vaga_b"]
    sl = M.novo(prs, "Maior remuneração, maior chance de ser escolhida")
    caixa(sl, 0.25, 0.9, 12.83, 1.25,
          [[("HIPÓTESE", 11, True, "B9E4B1")],
           [("A vaga que paga mais tem mais chance de ser a 1ª opção do médico", 22, True, BRANCO)],
           [("entre vagas do mesmo curso, na mesma UF, iguais no resto", 13, False, "DDEBDD")]],
          fill=VERDE, nome="Hipótese", margem=0.3)
    subtitulo(sl, 0.25, 2.35, 12.8, f"Exemplo real: um médico de {ex['candidato']['uf_de_trabalho_anterior']}, "
                                    f"ciclo {ex['candidato']['ciclo']}, diante de duas vagas do seu curso")
    # tabela-desenho: linhas = vagas; colunas = IVS (quase igual), distância (quase igual), bolsa (muda)
    x0, wn, wc = 0.25, 2.9, 2.05
    cols = (("IVS", "igual"), ("Distância", "igual"), ("Bolsa", "muda"))
    for j, (c, tp) in enumerate(cols):
        x = x0 + wn + j * (wc + 0.12)
        texto(sl, x, 2.85, wc, 0.32, [[(c, 13, True, ACENTO_ESCURO if tp == "muda" else CINZA)]],
              align=PP_ALIGN.CENTER)
    for i, vg in enumerate((a, b)):
        y = 3.22 + i * 1.0
        caixa(sl, x0, y, wn - 0.12, 0.88, [[(vg["municipio"], 16, True, TEXTO)]], fill=CLARO, line=BORDA,
              nome=f"Vaga {i + 1}")
        vals = (v(vg["ivs"], 3), f"{round(vg['km'])} km", f"R$ {int(vg['bolsa_mil'])} mil")
        for j, ((_, tp), val) in enumerate(zip(cols, vals)):
            x = x0 + wn + j * (wc + 0.12)
            muda = tp == "muda"
            caixa(sl, x, y, wc, 0.88, [[(val, 22 if muda else 17, True, ACENTO_ESCURO if muda else CINZA)]],
                  fill=ACENTO_CLARO if muda else BRANCO, line=ACENTO if muda else BORDA, align=PP_ALIGN.CENTER,
                  margem=0.04, nome=f"Valor {i}{j}")
    # o que se lê: quase igual × muda
    yl = 5.17
    for j, (_, tp) in enumerate(cols):
        x = x0 + wn + j * (wc + 0.12)
        txt, cor = (("+ R$ 5 mil", ACENTO_ESCURO) if tp == "muda" else ("≈ igual", CINZA))
        texto(sl, x, yl, wc, 0.32, [[(txt, 13, True, cor)]], align=PP_ALIGN.CENTER)
    # hipótese no exemplo
    xh = x0 + wn + 3 * (wc + 0.12) + 0.15
    seta(sl, xh - 0.1, 4.17, xh + 0.25, 4.17, cor=ACENTO, larg=2.5)
    caixa(sl, xh + 0.32, 3.22, 13.08 - xh - 0.32, 1.88,
          [[("Hipótese no exemplo", 12, True, ACENTO_ESCURO)],
           [("chance (", 15, True, TEXTO), (b["municipio"].split(" (")[0], 15, True, ACENTO_ESCURO), (")", 15, True,
                                                                                                    TEXTO)],
           [(">  chance (", 15, True, TEXTO), (a["municipio"].split(" (")[0], 15, True, TEXTO), (")", 15, True, TEXTO)]],
          fill=ACENTO_CLARO, line=ACENTO, nome="Hipótese no exemplo", margem=0.18)
    caixa(sl, 0.25, 5.75, 12.83, 0.72,
          [[("Observação: ", 14, True, VERDE),
            ("medimos a escolha de quem se inscreveu, não a chegada de médicos ao município.", 14, False, TEXTO)]],
          fill=BRANCO, line=BORDA, nome="Observação", margem=0.3)
    fontes(sl, "Fontes: editais e quadros de vagas do PMM-E (SGTES/MS), ciclo 2; CNES/DATASUS; Ipea, IVS 2010; IBGE. "
               "Elaboração própria.")
    notas(sl, (f"Frase central simples; o exemplo é real e volta no slide do método. O médico é de "
               f"{ex['candidato']['curso'].title().replace(' Do ', ' do ')}. Em cinza o que é quase igual (IVS e "
               "distância); em âmbar o que muda (a bolsa). As duas vagas ficam dos dois lados do corte de 0,400 "
               f"(porte: {mil(round(a['populacao_2022'] / 1000) * 1000)} e "
               f"{mil(round(b['populacao_2022'] / 1000) * 1000)} hab.). O par foi escolhido por regra fixa, sem olhar "
               "a escolha (scripts/apresentacao/gerar_exemplo_logit_real.py; exemplo_logit_real.json)."))
    return sl


def s_linhas(M, prs, n):
    ex = n["ex"]
    nv = ex["candidato"]["vagas_no_cardapio"]
    crm = CRM_EX.replace("MG", ex["candidato"]["uf_de_trabalho_anterior"])
    sl = M.novo(prs, "Cada candidato vira uma linha por vaga possível")
    subtitulo(sl, 0.25, 0.85, 7.9, "I. Um candidato, todas as vagas que ele podia escolher",
              f"{nv} vagas do seu curso e ciclo; y = 1 só na que ele pôs em 1º")
    vagas = [(ex["vaga_escolhida"], 1), (ex["vaga_b"], 0), (ex["vaga_a"], 0)]
    tab = sl.shapes.add_table(5, 5, Inches(0.25), Inches(1.6), Inches(7.9), Inches(3.3)).table
    cab = ("Candidato", "Vaga", "Bolsa", "Distância", "1ª opção (y)")
    for j, w in enumerate((1.9, 2.55, 1.2, 1.2, 1.05)):
        tab.columns[j].width = Inches(w)
    corpo = [[crm, vg["municipio"], f"R$ {int(vg['bolsa_mil'])} mil", f"{round(vg['km'])} km", str(y)]
             for vg, y in vagas]
    corpo.append([crm, f"… mais {nv - 3} vagas não escolhidas por ele", "", "", "0"])
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
            r.font.bold = i == 0 or j == 0 or (i == 1 and j == 4)
            r.font.italic = i == 4 and j == 1
            r.font.name = "Montserrat"
            r.font.color.rgb = RGBColor.from_string(BRANCO if i == 0 else (CINZA if (i == 4 and j == 1) else TEXTO))
            c.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT if j < 2 else PP_ALIGN.CENTER
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
    tab.cell(4, 1).merge(tab.cell(4, 3))
    texto(sl, 0.25, 5.0, 7.9, 0.3, [[("CRM ilustrativo: a base não guarda a identidade do médico.", 9.5, False,
                                      CINZA)]])
    # II. A base inteira: candidatos × vagas = linhas
    subtitulo(sl, 8.5, 0.85, 4.6, "II. A base inteira")
    blocos = ((mil(n["n_cand"]), "candidatos", CLARO, VERDE, TEXTO),
              (f"≈ {round(n['lin_media'])}", "vagas por candidato", CLARO, VERDE, TEXTO),
              (mil(n["n_lin"]), "linhas", VERDE, BRANCO, BRANCO))
    for k, (num, rot, fill, cn, cr) in enumerate(blocos):
        y = 1.4 + k * 1.25
        caixa(sl, 8.5, y, 4.58, 0.95, [[(num, 24, True, cn), (f"   {rot}", 14, False, cr)]], fill=fill,
              line=None if fill == VERDE else BORDA, nome=f"Base {k}", margem=0.3)
        if k < 2:
            texto(sl, 10.55, y + 0.95, 0.5, 0.3, [[("×" if k == 0 else "=", 15, True, VERDE)]], align=PP_ALIGN.CENTER)
    caixa(sl, 0.25, 5.5, 12.83, 0.95,
          [[("Assim, para cada candidato temos ", 15, False, BRANCO), ("todas as vagas que ele podia escolher", 15, True,
                                                                        BRANCO),
            (" e ", 15, False, BRANCO), ("qual ele escolheu", 15, True, BRANCO), (".", 15, False, BRANCO)]],
          fill=VERDE, nome="Ideia", margem=0.3, align=PP_ALIGN.CENTER)
    fontes(sl, FONTE_PUBLICA)
    notas(sl, (f"Mesmo candidato em todas as linhas (CRM ilustrativo; a base não guarda nome, CPF nem CRM). "
               f"Atributos da vaga (bolsa, IVS, porte) e do par médico–vaga (distância, mesma região) entram como "
               f"colunas. ≈ {round(n['lin_media'])} vagas por candidato (mediana {round(n['lin_med'])}; de "
               f"{n['lin_min']} a {n['lin_max']}). Funil: {mil(n['r1'])} candidatos com 1ª opção → {mil(n['com_cnes'])} "
               f"com local de trabalho anterior no CNES (o ponto de partida da distância) → {mil(n['m1_cand'])} com "
               f"região de saúde → {mil(n['n_cand'])} no modelo principal ({n['ret_uma']} ficaram com uma só vaga). "
               f"Linhas: {mil(n['alt_desenho'])} → {mil(n['n_lin'])} linhas, porque saem as vagas de pares de UFs que "
               "nenhum médico daquela UF escolheu (não informam o peso da bolsa). Transição: o próximo slide mostra, "
               "de forma descritiva, onde ficam as 1ªs opções em relação a onde o médico já trabalhava."))
    return sl


def s_modelo(M, prs, n):
    sl = M.novo(prs, "Modelo: logit condicional da 1ª opção")
    caixa(sl, 0.25, 0.9, 8.55, 3.05, [], fill=BRANCO, line=BORDA, nome="Cartão das equações")
    # ① a chance
    texto(sl, 0.45, 0.97, 8.2, 0.3, [[("①  Chance de a vaga v ser a 1ª opção do candidato i", 12, True, VERDE2)]])
    texto(sl, 0.45, 1.45, 2.75, 0.45, [eq("P(i escolhe v) =", 18)], align=PP_ALIGN.RIGHT)
    texto(sl, 3.3, 1.22, 5.3, 0.4, [eq("exp(β·x_{iv})", 18)], align=PP_ALIGN.CENTER)
    linha(sl, 3.45, 1.67, 8.45, 1.67, larg=1.25)
    texto(sl, 3.3, 1.71, 5.3, 0.42, [eq("soma de exp(β·x_{ik}) em todas as vagas k de i", 15)], align=PP_ALIGN.CENTER)
    linha(sl, 0.45, 2.2, 8.6, 2.2, cor=BORDA, larg=1.0)
    # ② o valor
    texto(sl, 0.45, 2.25, 8.2, 0.3, [[("②  Utilidade da vaga v para o candidato i", 12, True, VERDE2)]])
    texto(sl, 0.45, 2.55, 8.2, 0.42,
          [eq("U_{iv} = β_{1}·bolsa_{v} + β_{2}·dist_{iv} + β_{3}·IVS_{v} + β_{4}·X_{iv} + α_{UF(i),UF(v)} + ε_{iv}",
              14.5)], align=PP_ALIGN.CENTER)
    texto(sl, 0.45, 2.95, 8.2, 0.28, [eq("β·x_{iv}: tudo menos o ε, a parte de U que observamos  ·  ε_{iv}: a que não "
                                         "observamos", 10.5, CINZA)], align=PP_ALIGN.CENTER)
    # a ligação, abaixo de ②, em destaque
    caixa(sl, 0.35, 3.3, 8.35, 0.56,
          [[("Ligação: ", 13, True, ACENTO_ESCURO),
            ("vemos só qual vaga tem o maior U (a 1ª opção). Supondo ε de valor extremo, a chance disso é ①, "
             "que depende só da parte observada de ②.", 12, False, ACENTO_ESCURO)]],
          fill=ACENTO_CLARO, line=ACENTO, nome="Ligação", margem=0.15)
    # O que cada termo faz (foco no regressor)
    texto(sl, 0.25, 4.05, 8.55, 0.32, [[("O que cada termo faz", 14, True, TEXTO)]])
    termos = (("bolsa", "β_{1}", "testado", "TESTADO", "o que testamos"),
              ("distância", "β_{2}", "controle", "CONTROLE", "do local de trabalho anterior até a vaga"),
              ("IVS", "β_{3}", "controle", "CONTROLE", "vulnerabilidade do município, sem salto no corte"),
              ("X", "β_{4}", "controle", "CONTROLE", "região, município, porte, capital, vaga imediata"),
              ("par de UFs", "α", "pareamento", "FIXO", "254 efeitos fixos, um por par: compara vagas na mesma UF"))
    for k, (reg, par, tp, rot, leitura) in enumerate(termos):
        y = 4.42 + k * 0.46
        texto(sl, 0.35, y, 1.75, 0.42, [[(reg, 14, True, TEXTO), ("  ", 10, False, TEXTO)] + eq(par, 12, CINZA)])
        pill(sl, 2.15, y + 0.08, 1.15, rot, tp)
        texto(sl, 3.45, y, 5.35, 0.42, [[(leitura, 12.5, False, TEXTO)]])
        if k < 4:
            linha(sl, 0.35, y + 0.44, 8.75, y + 0.44, cor=BORDA, larg=0.75)
    # O que se estima (pequeno)
    caixa(sl, 9.0, 0.9, 4.08, 0.95,
          [[("O QUE SE ESTIMA: ", 10.5, True, "B9E4B1"),
            ("os pesos β₁ a β₄ e os efeitos fixos α que melhor explicam as 1ªs opções", 12, True, BRANCO)]],
          fill=VERDE, nome="O que se estima", margem=0.2)
    # Por que este modelo (grande): o método e a lógica; depois, onde a família é usada
    # pedido de 14/11 (rodada 7): o quadro inteiro explica o modelo, com letra maior; só o exemplo de saúde
    caixa(sl, 9.0, 2.0, 4.08, 4.7,
          [[("POR QUE ESTE MODELO", 11, True, VERDE2)],
           # rodada 11 (14/11): texto do autor; sai a frase da regra
           [("Logit condicional", 14, True, VERDE),
            (" de McFadden (1974), que lhe rendeu o Nobel de Economia de 2000.", 13, False, TEXTO)],
           [("Cada médico escolhe uma vaga entre várias. O modelo compara as vagas do ", 13, False, TEXTO),
            ("mesmo", 13, True, TEXTO),
            (" médico: o que é dele (nota, idade) é igual em todas e sai da conta.", 13, False, TEXTO)],
           [("Referência de uso em economia da saúde: ", 13, True, VERDE),
            ("Costa, Nunes e Sanches (2024) usam um modelo da mesma família para estudar onde os médicos escolhem "
             "trabalhar no Brasil.", 13, False, TEXTO)]],
          fill=CLARO, line=BORDA, anchor=MSO_ANCHOR.MIDDLE, nome="Por que este modelo", margem=0.25, esp=9)
    fontes(sl, "Fontes: McFadden (1974); Costa, Nunes e Sanches (2024), The Review of Economics and Statistics. "
               "Elaboração própria.")
    notas(sl, ("Duas equações. ② é a utilidade da vaga: U = β·x + ε, com o erro no fim; β·x (bolsa, distância, IVS, "
               "controles e o efeito fixo do par) é a parte observável; ε é o que não observamos. ① é a chance de cada "
               "vaga ser a 1ª opção. A ligação: se cada ε segue uma distribuição de valor extremo (Gumbel), a chance de "
               "a vaga ter o maior U é exatamente exp(β·x) ÷ soma de exp(β·x) nas vagas do candidato; a chance não se "
               "escreve sobre U inteiro, porque o ε não é observado. α são 254 parâmetros, um efeito fixo por par UF de "
               "trabalho × UF da vaga (por isso α, a letra usual para efeito fixo, e não um β₅ único). Os pesos saem por máxima verossimilhança. O nível do valor não é identificado (só "
               "diferenças entre vagas, numa escala normalizada); por isso cada coeficiente se lê pela razão de "
               "chances entre duas vagas: P(A) ÷ P(B) = exp[β₁·(bolsa_A − bolsa_B) + …]. β₃·IVS: na estimação, o IVS "
               "entra como reta com dobras nos cortes 0,300 e 0,400 (spline linear contínuo, sem salto), para que só a "
               "bolsa salte no corte. α é o efeito fixo do par UF de trabalho × UF da vaga. Literatura: Bobba et al. "
               "usam logit multinomial com cardápio personalizado (o professor escolhe na sua vez e pode recusar); "
               "Costa, Nunes & Sanches usam logit de coeficientes aleatórios com instrumento (o salário de mercado é "
               "endógeno). No PMM-E a bolsa é fixada por regra com corte e a lista é feita na inscrição: o logit "
               "condicional, o mais simples da família, basta (doc 11 da banca 2). McFadden recebeu o Nobel de 2000 "
               "pela teoria e pelos métodos de escolha discreta. Ligação com o y: o que observamos é y = 1 na vaga "
               "posta em 1º, isto é, a de maior U."))
    return sl


def s_passos(M, prs, n):
    ex = n["ex"]
    a, b, c = ex["vaga_a"], ex["vaga_b"], ex["conta"]
    sl = M.novo(prs, "Método passo a passo: da escolha à razão de chances")
    grupos = {"base": ("DCEFD9", VERDE, TEXTO, BORDA), "est": (MEDIO, BRANCO, BRANCO, None),
              "met": (VERDE, BRANCO, BRANCO, None)}
    passos = (("1", "Vagas", "uma linha por vaga possível", "base"),
              ("2", "Escolha", "y = 1 na vaga posta em 1º", "base"),
              ("3", "Utilidade", "U = pesos × características + ε", "est"),
              ("4", "Chance", "exp(U sem ε) da vaga ÷ a soma disso em todas as vagas dele", "est"),
              ("5", "Pesos", "os que melhor explicam as escolhas", "est"),
              ("6", "Métrica", "chance da vaga que paga mais ÷ chance da outra", "met"))
    # rodada 9 (14/11): denominador explícito nos passos 4 e 6; exemplo mais abaixo
    w, gap = 1.95, 0.226
    for k, (num, tit, corpo, g) in enumerate(passos):
        x = 0.25 + k * (w + gap)
        fill, ct, cc, ln = grupos[g]
        caixa(sl, x, 0.88, w, 1.62, [], fill=fill, line=ln, nome=f"Passo {num}")
        caixa(sl, x + 0.1, 0.96, 0.4, 0.4, [[(num, 13, True, fill if g != "base" else BRANCO)]],
              fill=BRANCO if g != "base" else VERDE, forma=MSO_SHAPE.OVAL, align=PP_ALIGN.CENTER, margem=0)
        texto(sl, x + 0.57, 0.96, w - 0.62, 0.4, [[(tit, 16, True, ct)]])
        texto(sl, x + 0.1, 1.42, w - 0.18, 1.05, [[(corpo, 13, False, cc)]], anchor=MSO_ANCHOR.TOP)
        if k < 5:
            seta(sl, x + w + 0.01, 1.69, x + w + gap - 0.01, 1.69, larg=1.75)
    for k, (g, rot) in enumerate((("base", "1–2: a base de dados"), ("est", "3–5: a estimação"),
                                  ("met", "6: a métrica"))):
        fill, ct, _, ln = grupos[g]
        caixa(sl, 2.3 + k * 3.0, 2.62, 2.75, 0.34, [[(rot, 11.5, True, ct)]], fill=fill, line=ln,
              align=PP_ALIGN.CENTER, margem=0.05, nome=f"Legenda {g}")
    # Exemplo real
    subtitulo(sl, 0.25, 3.2, 12.8, f"Exemplo real: o médico de {ex['candidato']['uf_de_trabalho_anterior']} do slide "
                                   "de hipótese")
    y0, h = 3.7, 1.3
    for k, vg in enumerate((a, b)):
        y = y0 + k * (h + 0.15)
        caixa(sl, 0.25, y, 3.8, h,
              [[(vg["municipio"], 17, True, TEXTO)],
               [(f"R$ {int(vg['bolsa_mil'])} mil  ·  {round(vg['km'])} km", 13.5, False, CINZA)]],
              fill=CLARO, line=BORDA, nome=f"Vaga ex {k}", margem=0.25)
        caixa(sl, 4.15, y, 1.95, h, [[("chance (passo 4)", 10.5, False, CINZA)],
                                     [(f"{v(100 * vg['chance_modelo'])}%", 27, True, MEDIO)]],
              fill=BRANCO, line=MEDIO, align=PP_ALIGN.CENTER, margem=0.04, nome=f"Chance ex {k}")
    alto = 2 * h + 0.15
    seta(sl, 6.2, y0 + alto / 2, 6.6, y0 + alto / 2, larg=2.5)
    rz = c["razao_por_termo"]
    caixa(sl, 6.7, y0, 4.05, alto, [], fill=VERDE, nome="Razão do exemplo")
    texto(sl, 6.9, y0 + 0.1, 3.75, 0.3, [[("PASSO 6: A RAZÃO", 11, True, "B9E4B1")]])
    texto(sl, 6.9, y0 + 0.4, 3.75, 0.5,
          [[(f"{v(100 * b['chance_modelo'])}% ÷ {v(100 * a['chance_modelo'])}% = {v(c['razao_total'])}", 23, True,
             BRANCO)]])
    texto(sl, 6.9, y0 + 0.9, 3.75, 0.32,
          [[(f"{b['municipio'].split(' (')[0]} (paga mais) ÷ {a['municipio'].split(' (')[0]}", 11.5, False,
             "DDEBDD")]])
    fat = ((f"×{v(rz['bolsa_mil'])}", "a bolsa: +R$ 5 mil"),
           (f"×{v(rz['distancia_100km'])}", f"a distância: {round(b['km'] - a['km'])} km a mais"),
           (f"×{v(rz['ivs'] * rz['log_populacao_2022'] * rz['outros'])}", "o resto"))
    for k, (x_, rot) in enumerate(fat):
        texto(sl, 6.9, y0 + 1.3 + k * 0.42, 3.75, 0.42,
              [[(x_, 17, True, "B9E4B1" if k == 0 else BRANCO), (f"  {rot}", 13, False, BRANCO)]])
    caixa(sl, 10.9, y0, 2.18, alto,
          [[("Se fossem as únicas duas vagas:", 12, True, VERDE2)],
           [(f"{round(100 * c['chance_b_entre_as_duas'])}%", 26, True, TEXTO)],
           [("contra", 12, False, CINZA)],
           [(f"{100 - round(100 * c['chance_b_entre_as_duas'])}%", 26, True, TEXTO)]],
          fill=CLARO, line=BORDA, nome="Entre as duas", align=PP_ALIGN.CENTER)
    fontes(sl, FONTE_PUBLICA)
    notas(sl, (f"Passo a passo da estimação e da métrica, com um caso real ({ex['candidato']['vagas_no_cardapio']} vagas "
               f"possíveis; IVS {v(a['ivs'], 3)} e {v(b['ivs'], 3)}). Cores: base de dados, estimação, métrica. As "
               "chances são as do modelo estimado (efeitos fixos incluídos); na razão entre as duas vagas o efeito fixo "
               f"do par de UFs é o mesmo e se cancela, como o denominador. ×{v(rz['bolsa_mil'])} = e^(5 × β₁), com β₁ = "
               f"{v(n['b'], 3)} por R$ 1 mil; β₂ = {v(n['dist'], 3)} por 100 km. A razão do exemplo "
               f"({v(c['razao_total'])}) não é exatamente {v(n['rc'])} porque as vagas diferem um pouco em distância, "
               "IVS e porte. Por que razão, e não diferença: com centenas de vagas cada chance é pequena; a razão não "
               "depende de quantas vagas o candidato tem. Exemplo reestimado em scripts/apresentacao/"
               "gerar_exemplo_logit_real.py, igual ao VL-1 gravado."))
    return sl


def s_estimacao(M, prs, n):
    """De onde vem o β e o que comparamos; a incerteza fica nas notas e no slide de resultados (pedido de 14/11)."""
    sl = M.novo(prs, "Anexo 4: estimação, de onde vem o β")
    topo, alto = 0.9, 4.0

    def cartao(x, w, rotulo):
        caixa(sl, x, topo, w, alto, [], fill=BRANCO, line=BORDA, nome=f"Cartão {rotulo}")
        texto(sl, x + 0.25, topo + 0.15, w - 0.4, 0.32, [[(rotulo, 12.5, True, VERDE2)]])

    x1, w1 = 0.25, 6.3
    cartao(x1, w1, "I. DE ONDE VEM A VARIAÇÃO DA BOLSA")
    itens = (("1", "A bolsa é **fixada por regra**: R$ 10, 15 ou 20 mil, pela faixa de IVS do município."),
             ("2", "O **IVS também está no modelo**: o β não mistura bolsa com vulnerabilidade."),
             ("3", f"Comparamos **vagas da mesma UF** com bolsas diferentes: {n['pares_var']} pares de UFs, "
                   f"{mil(n['cand_var'])} candidatos."))
    for k, (num, t) in enumerate(itens):
        y = topo + 0.7 + k * 1.05
        caixa(sl, x1 + 0.25, y + 0.02, 0.44, 0.44, [[(num, 14, True, BRANCO)]], fill=VERDE, forma=MSO_SHAPE.OVAL,
              align=PP_ALIGN.CENTER, margem=0)
        texto(sl, x1 + 0.85, y, w1 - 1.05, 0.95, [negrito(t, 15, TEXTO)], anchor=MSO_ANCHOR.TOP)

    x2, w2 = 6.78, 6.3
    cartao(x2, w2, "II. O QUE COMPARAMOS")
    comp = (("✓", "Vagas do mesmo candidato", "o que é dele (nota, idade) se cancela", MEDIO),
            ("✓", "Vagas da mesma UF", "o que é da UF (salário local, família) se cancela", MEDIO),
            ("✗", "Não dentro do município", "a bolsa é igual no município inteiro", "7A1C17"))
    for k, (sim, tit, sub, cor) in enumerate(comp):
        y = topo + 0.7 + k * 1.05
        texto(sl, x2 + 0.25, y, 0.45, 0.45, [[(sim, 22, True, cor)]])
        texto(sl, x2 + 0.85, y, w2 - 1.05, 0.95, [[(tit, 15, True, TEXTO)], [(sub, 12.5, False, CINZA)]],
              anchor=MSO_ANCHOR.TOP)

    # 14/11, 3ª rodada: a ressalva "exploratório" saiu daqui e foi para Limitações (pedido do autor); no lugar, a
    # síntese do slide e a ponte para o seguinte
    caixa(sl, 0.25, 5.1, 12.83, 1.45,
          [[("Em resumo: ", 16, True, "B9E4B1"),
            ("o β mede quanto a chance de uma vaga muda com a bolsa, comparando vagas do mesmo candidato, na mesma "
             "UF, com o IVS controlado.", 16, False, BRANCO)]],
          fill=VERDE, nome="Em resumo", margem=0.3, esp=6)
    fontes(sl, FONTE_PUBLICA)
    notas(sl, (f"(I) A bolsa é função em degraus do IVS (a regra reproduz {n['r1_c1']}/{n['n_c1']} e "
               f"{n['r1_c2']}/{n['n_c2']} municípios) e o IVS entra como spline linear contínuo com nós nos cortes (reta "
               "com dobras, sem salto); por isso o β vem dos saltos, como na nota 13 de Bobba et al. Só perto do corte "
               f"(±0,05): ×{v(n['rc_vl2'])} (IC {v(n['rc_vl2_inf'])} a {v(n['rc_vl2_sup'])}), mesma direção, "
               "inconclusivo. (II) Em termos técnicos: o candidato entra como efeito fixo implícito (se cancela no "
               f"denominador); o par UF de trabalho × UF da vaga entra como {n['col_ef']} colunas 0/1; não há efeito "
               "fixo de município, porque a bolsa é constante no município e seria absorvida. A ressalva de que fixar "
               "a UF foi decidido depois de ver o modelo base está em Limitações. Incerteza (se perguntarem): máxima "
               "verossimilhança por "
               "Newton–Raphson em código próprio conferido; erro-padrão agrupado por curso × ciclo "
               f"({n['g_conj']} grupos; EP do β {v(n['ep_cl'], 3)}, o dobro do ingênuo {v(n['ep_mle'], 3)}); score "
               f"bootstrap de Kline e Santos (2012): p = {v(n['p_score'], 3)}; Holm entre as três principais: "
               f"p = {v(n['p_holm'], 3)}."))
    return sl


def s_identificacao(M, prs, n):
    sl = M.novo(prs, "Identificação: as premissas do logit condicional")
    linhas_ = (
        ("Escolha sincera", "o médico lista a vaga que prefere", "SUPOSIÇÃO", "suposto",
         "Ninguém deixa de pôr em 1º a vaga preferida por achar que não passaria na nota."),
        ("Conjunto de escolha conhecido", "o médico vê todas as vagas", "SUPOSIÇÃO", "suposto",
         "Ele considerou todas as vagas do seu curso e ciclo; o edital publica a lista inteira."),
        ("Exogeneidade da bolsa", "a bolsa não depende do que não medimos", "VALE EM PARTE", "parte",
         "A bolsa segue a regra do IVS, e o IVS está no modelo. Mas outras regras federais mudam nos mesmos cortes: "
         "medimos o efeito do conjunto."),
        ("Independência de alternativas (IIA)", "vagas parecidas não se substituem a mais", "TESTADA", "obs",
         "Vagas da mesma região concorrem mais entre si. Num logit aninhado, testado no modelo base, o peso da bolsa "
         "quase não muda."),
    )
    for k, (tit, sub, rot, tp, expl) in enumerate(linhas_):
        x, y = 0.25 + (k % 2) * 6.53, 0.95 + (k // 2) * 2.92
        caixa(sl, x, y, 6.3, 2.72, [], fill=CLARO, line=BORDA, nome=f"Premissa {k + 1}")
        caixa(sl, x + 0.25, y + 0.22, 0.46, 0.46, [[(str(k + 1), 15, True, BRANCO)]], fill=VERDE,
              forma=MSO_SHAPE.OVAL, align=PP_ALIGN.CENTER, margem=0)
        texto(sl, x + 0.85, y + 0.18, 3.55, 0.56, [[(tit, 16, True, TEXTO)]])
        pill(sl, x + 4.45, y + 0.27, 1.65, rot, tp, h=0.36, tam=10)
        texto(sl, x + 0.85, y + 0.78, 5.25, 0.32, [[(sub, 12.5, True, VERDE2)]])
        linha(sl, x + 0.25, y + 1.18, x + 6.05, y + 1.18, cor=BORDA, larg=0.75)
        texto(sl, x + 0.25, y + 1.3, 5.8, 1.3, [[(expl, 14, False, TEXTO)]], anchor=MSO_ANCHOR.TOP)
    fontes(sl, "Fontes: Ipea, IVS 2010; editais e quadros de vagas do PMM-E (SGTES/MS), ciclos 1–3; CNES/DATASUS. "
               "Elaboração própria.")
    notas(sl, (f"Premissas do logit condicional. Escolha sincera: não dá para testar com estes dados (premissa do autor, "
               f"11/11/2026). Bolsa sem relação com o que não medimos: a regra do IVS reproduz {n['r1_c1']}/{n['n_c1']} e "
               f"{n['r1_c2']}/{n['n_c2']} municípios; IVS e par de UFs no modelo; outras políticas federais usam os "
               "mesmos cortes (auditoria 18). Vagas próximas como substitutas (a premissa de alternativas "
               "independentes, IIA): no logit aninhado por região de saúde, rodado no modelo base sem o par de UFs, "
               f"λ = {v(n['lambda'])} (λ = 1 seria o logit condicional; rejeita-se λ = 1); o peso da bolsa fica "
               f"{v(n['b_m9'], 3)} contra {v(n['b_m1'], 3)}. Se perguntarem: a IIA não vale por inteiro, mas o β quase "
               "não muda. O logit misto (M8) mostra que o peso varia entre candidatos: o β é uma média."))
    return sl


def s_resultados(M, prs, n):
    sl = M.novo(prs, f"Resultados: +R$ 5 mil multiplicam a chance por {v(n['rc'])}")
    cards = ((f"×{v(n['rc'])}", "+R$ 5 mil de bolsa, na mesma UF", f"IC 95%: {v(n['rc_inf'])} a {v(n['rc_sup'])}",
              True),
             (f"≈ {round(n['km'])} km", "mais perto valem o mesmo que +R$ 5 mil", "na escolha do médico", False),
             (f"×{v(n['rc_c2'])}", "só no ciclo 2", "nos ciclos 1 e 3, o IC inclui 1", False))
    for k, (num, rot, sub, escuro) in enumerate(cards):
        x = 0.25 + k * 4.31
        caixa(sl, x, 0.9, 4.15, 1.6,
              [[(num, 34, True, BRANCO if escuro else VERDE)], [(rot, 14, True, BRANCO if escuro else TEXTO)],
               [(sub, 11.5, False, "DDEBDD" if escuro else CINZA)]],
              fill=VERDE if escuro else CLARO, line=None if escuro else BORDA, nome=f"Cartão {k}", margem=0.25)
    subtitulo(sl, 0.25, 2.68, 8.4, "Para comparar: o que mais pesa na escolha da vaga")
    sl.shapes.add_picture(str(FIG_COEF), Inches(0.25), Inches(3.05), width=Inches(7.9))
    caixa(sl, 8.4, 2.7, 4.68, 3.95,
          [[("LEITURA", 11, True, "B9E4B1")],
           [("A bolsa pesa, mas a proximidade pesa mais.", 18, True, BRANCO)],
           [(f"Na mesma região de saúde de onde já trabalhava, a chance é ×{v(n['x_reg'])}; cada 100 km a mais a "
             f"multiplicam por {v(n['x_dist'])}.", 13.5, False, "DDEBDD")],
           [("Por isso falamos em incentivo limitado.", 13.5, True, BRANCO)]],
          fill=VERDE, nome="Leitura", margem=0.3, esp=8)
    fontes(sl, FONTE_PUBLICA)
    notas(sl, (f"Cada × é e^coeficiente. Bolsa: β₁ = {v(n['b'], 3)} por R$ 1 mil; 5β₁ = {v(n['b5'], 3)}; "
               f"e^{v(n['b5'], 3)} = {v(n['rc'])}; p de Holm {v(n['p_holm'], 3)}; score bootstrap p = "
               f"{v(n['p_score'], 3)}. Km equivalentes: 5β₁ ÷ |β₂| × 100 = {v(n['b5'], 3)} ÷ {v(-n['dist'], 3)} × 100 "
               f"= {round(n['km'])} km. Ciclo 2: IC {v(n['rc_c2_inf'])} a {v(n['rc_c2_sup'])}; ciclos 1 e 3: "
               f"×{v(n['rc_c1'])} e ×{v(n['rc_c3'])}. Mesma região e mesmo município são controles, mas dão a escala: "
               "estar na mesma região de saúde pesa mais que toda a bolsa extra."))
    return sl


def s_resultados_colega(M, prs, n):
    """Slide de resultado do deck do colega (14/11, rodada 8): seis fatores, as três contas e a leitura."""
    sl = M.novo(prs, "Ficar perto de onde trabalha pesa mais que a bolsa")
    subtitulo(sl, 0.25, 0.9, 7.7, "Quanto cada fator multiplica a chance da vaga",
              "Acima de 1: a vaga atrai mais. Abaixo: atrai menos. Barra = intervalo de 95%.")
    sl.shapes.add_picture(str(FIG_SEIS), Inches(0.15), Inches(1.6), width=Inches(7.75))
    subtitulo(sl, 8.2, 0.9, 4.9, f"O {v(n['b'], 3)} do modelo vira ×{v(n['rc'])} e {round(n['km'])} km",
              "três contas, da estimativa à leitura")
    contas = (("Por R$ 5 mil: ", f"5 × {v(n['b'], 3)} = {v(n['b5'], 3)}",
               "o modelo dá o peso por R$ 1 mil; a bolsa sobe de 5 em 5 mil"),
              ("Em chance: ", f"exp({v(n['b5'], 3)}) = ×{v(n['rc'])}",
               f"a vaga com +R$ 5 mil tem {round(100 * (n['rc'] - 1))}% mais chance (IC {v(n['rc_inf'])} a "
               f"{v(n['rc_sup'])})"),
              ("Em distância: ", f"{v(n['b5'], 3)} ÷ {v(-n['dist'], 3)} × 100 = {round(n['km'])} km",
               f"a distância pesa {v(n['dist'], 3)} por 100 km"))
    for k, (rot, conta, sub) in enumerate(contas):
        y = 1.6 + k * 1.37
        caixa(sl, 8.2, y, 4.88, 1.22, [], fill=CLARO, nome=f"Conta {k + 1}")
        caixa(sl, 8.4, y + 0.36, 0.5, 0.5, [[(str(k + 1), 15, True, BRANCO)]], fill=VERDE, forma=MSO_SHAPE.OVAL,
              align=PP_ALIGN.CENTER, margem=0)
        texto(sl, 9.05, y + 0.12, 3.95, 1.0, [[(rot, 12.5, True, VERDE), (conta, 13, True, TEXTO)],
                                             [(sub, 11, False, CINZA)]], esp=3)
    x_reg = v(n["x_reg"])
    caixa(sl, 0.25, 5.85, 12.83, 0.8,
          [[("Leitura: ", 15, True, "B9E4B1"),
            (f"a bolsa conta (×{v(n['rc'])}), mas estar na mesma região de saúde de onde já trabalha pesa mais "
             f"(×{x_reg}).", 15, False, BRANCO)]],
          fill=VERDE, nome="Leitura", margem=0.35)
    fontes(sl, FONTE_PUBLICA)
    notas(sl, (f"Cada × é e^coeficiente do modelo principal (VL-1, ciclos 1–3). Bolsa: β₁ = {v(n['b'], 3)} por R$ 1 "
               f"mil; 5β₁ = {v(n['b5'], 3)}; e^{v(n['b5'], 3)} = {v(n['rc'])}; p de Holm {v(n['p_holm'], 3)}; score "
               f"bootstrap p = {v(n['p_score'], 3)}. Km equivalentes: 5β₁ ÷ |β₂| × 100 = {round(n['km'])} km. "
               "Mesma região de saúde e mesmo município são controles (relação com o local de trabalho anterior), mas "
               "dão a escala: estar perto pesa mais que a bolsa extra. População em dobro: e^(β·ln 2). Capital: o "
               f"intervalo inclui 1. Ciclo 2 sozinho: ×{v(n['rc_c2'])} (slide de robustez)."))
    return sl


def s_robustez(M, prs, n):
    sl = M.novo(prs, "Robustez: ×1,47 se mantém com mais dados".replace("1,47", v(n["rc"])))
    sl.shapes.add_picture(str(FIG_ROB), Inches(0.15), Inches(0.88), width=Inches(8.25))
    lo, hi = min(n["rc"], n["rc_log"], n["rc_vl3"]), max(n["rc"], n["rc_log"], n["rc_vl3"])
    blocos = (("OUTRAS MEDIDAS", f"Com todos os dados, de ×{v(lo)} a ×{v(hi)}: o resultado se mantém.", VERDE, BRANCO,
               "B9E4B1"),
              ("SÓ PARTE DOS DADOS", f"Perto do corte e nos ciclos 1 e 3, o IC inclui 1: inconclusivo, não contrário. O "
                                     f"ciclo 2 é o mais forte (×{v(n['rc_c2'])}).", CLARO, TEXTO, VERDE2))
    y = 1.1
    for k, (tit, corpo, fill, cor, cor_t) in enumerate(blocos):
        h = 2.1
        caixa(sl, 8.55, y, 4.53, h, [[(tit, 12, True, cor_t)], [(corpo, 15, k == 0, cor)]],
              fill=fill, line=None if fill == VERDE else BORDA, nome=f"Robustez {k}", margem=0.25, esp=4)
        y += h + 0.15
    texto(sl, 8.55, y + 0.05, 4.53, 0.35, [[("Verde: ", 12, True, MEDIO), ("IC exclui 1.   ", 12, False, TEXTO),
                                            ("Cinza: ", 12, True, CINZA), ("IC inclui 1.", 12, False, TEXTO)]])
    fontes(sl, FONTE_PUBLICA)
    notas(sl, (f"Grupos na ordem da leitura: principal; outras medidas com todos os dados (distância em log; região "
               f"anterior × UF da vaga); só parte dos dados (perto do corte; cada ciclo). Por que o × e não o "
               f"coeficiente: é o mesmo número, ln({v(n['rc'])}) = "
               f"{v(n['b5'], 3)} = 5 × β₁; o × diz quantas vezes a chance muda; o teste (IC exclui 1) é o mesmo do β "
               "(IC exclui 0)."))
    return sl




def s_conclusao(M, prs, n):
    """Conclusão com a discussão (antigo slide 'metade de quem ocupa a vaga', fundido aqui a pedido de 14/11)."""
    sl = M.novo(prs, "Conclusão: bolsa pesa na escolha, mas pouco")
    caixa(sl, 0.25, 0.9, 12.83, 1.3,
          [[("RESPOSTA", 11, True, "B9E4B1")],
           [(f"Sim: na mesma UF, +R$ 5 mil multiplicam por {v(n['rc'])} a chance de a vaga ser a 1ª opção", 20, True,
             BRANCO)],
           [(f"≈ {round(n['km'])} km mais perto  ·  forte só no ciclo 2 (×{v(n['rc_c2'])})", 14, False, "DDEBDD")]],
          fill=VERDE, nome="Resposta", margem=0.3)
    # quem ocupa a vaga (descritivo)
    kpis = ((f"{round(n['origem'])}%", "de quem ocupa a vaga já tinha vínculo no município",
             f"IC 95%: {round(n['origem_lo'])}% a {round(n['origem_hi'])}%"),
            (f"+{v(n['horas'], 1)} h/sem", "no CNES depois da entrada, num programa de 20 h",
             f"IC 95%: +{v(n['horas_lo'], 1)} a +{v(n['horas_hi'], 1)}"))
    texto(sl, 0.25, 2.35, 4.2, 0.3, [[("QUEM OCUPA A VAGA (DESCRITIVO)", 10.5, True, VERDE2)]])
    for k, (num, rot, ic) in enumerate(kpis):
        caixa(sl, 0.25, 2.7 + k * 1.42, 4.2, 1.3, [[(num, 28, True, VERDE)], [(rot, 12, True, TEXTO)],
                                                   [(ic, 10, False, CINZA)]],
              fill=CLARO, line=BORDA, nome=f"KPI {k}", margem=0.22)
    # rodada 8 (14/11): termos-chave em negrito
    blocos = (("✓  Dá para afirmar", (f"A **bolsa maior é preferida** (×{v(n['rc'])})",
                                      f"O **peso é moderado**: R$ 5 mil ≈ {round(n['km'])} km",
                                      "**Metade** de quem ocupa a vaga **já estava no município**")),
              ("✗  Não dá para afirmar", ("Que leva **mais médicos ao município**",
                                          "Que o efeito é **só da bolsa**",
                                          "Que vale em **todo ciclo**")))
    for k, (tit, itens) in enumerate(blocos):
        x = 4.6 + k * 4.3
        caixa(sl, x, 2.7, 4.18, 2.72, [[(tit, 16, True, VERDE if k == 0 else "7A1C17")]] +
              [[("•  ", 13.5, False, TEXTO)] + negrito(it, 13.5, TEXTO) for it in itens],
              fill=CLARO if k == 0 else BRANCO, line=BORDA, anchor=MSO_ANCHOR.MIDDLE, nome=tit, margem=0.25, esp=8)
    # rodada 8: "Para a política" maior, na largura toda
    caixa(sl, 0.25, 5.62, 12.83, 1.1,
          [[("Para a política: ", 17, True, "B9E4B1"),
            ("pagar mais muda a escolha entre vagas próximas.", 17, False, BRANCO)],
           [("Não mostramos que atraia médicos de longe.", 17, False, BRANCO)]],
          fill=VERDE, nome="Política", margem=0.4, esp=2)
    fontes(sl, FONTE_PUBLICA)
    notas(sl, ("Conclusão e discussão num slide (pedido de 14/11): a resposta, quem ocupa a vaga, dá / não dá para "
               "afirmar e a leitura para a política. Quem ocupa a vaga: números do P4 (trajetória no CNES), "
               "descritivos: compara o mesmo médico antes e depois, sem grupo de comparação; horas cadastradas no CNES "
               "não são horas trabalhadas. Em metade dos casos, o programa passa a pagar quem já estava lá; o cadastro "
               "sobe menos que as 20 h da bolsa. Não dá para afirmar: que a bolsa leva mais médicos ao município "
               "(vemos a escolha, não a chegada); que é só o dinheiro (no corte do IVS muda um pacote de regras); que "
               "o efeito vale em todo ciclo (só o ciclo 2 é forte)."))
    return sl


def s_limitacoes(M, prs, n):
    sl = M.novo(prs, "Limitações")
    caixas = (("O que o resultado não mede",
               (("Escolha, não alocação", "medimos a 1ª opção, não a chegada ao município"),
                ("Tratamento composto", "outras regras mudam no mesmo corte de IVS"),
                ("Origem pelo CNES", "local de trabalho anterior, não residência"))),
              ("Quão forte é o resultado",
               (("Especificação escolhida após os dados",
                 "resultado exploratório; confirmar exige dados novos"),
                ("Heterogeneidade entre ciclos", "significativo só no ciclo 2: validade externa limitada"),
                ("Escolha sincera", "premissa não testável com estes dados"))))
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
    fontes(sl, FONTE_PUBLICA)
    notas(sl, ("Seis limitações em duas caixas. Escolha, não alocação: vemos a 1ª opção na inscrição, não a chegada "
               "ao município. Tratamento composto: no corte de IVS outras regras mudam junto com a bolsa; o efeito do "
               "dinheiro não sai isolado. Origem pelo CNES: é onde o médico trabalhava, não onde mora. Especificação "
               "escolhida após os dados: comparar só vagas da mesma UF (o efeito fixo do par de UFs) foi decidido "
               f"depois de ver os primeiros resultados. Por isso o ×{v(n['rc'])} é exploratório. Exploratório não quer dizer 'não causal': o desenho (salto da bolsa no "
               "corte, dentro da mesma UF) é o mesmo; quer dizer que não foi o teste planejado (adendo 52e, "
               "pós-resultado). Para virar confirmatório, seria preciso repetir o teste em dados novos, por exemplo o "
               "ciclo 3 quando estiver maduro. Dizer isso antes da banca perguntar. Heterogeneidade: ciclo 1 "
               f"×{v(n['rc_c1'])} e ciclo 3 ×{v(n['rc_c3'])}, com IC que contém 1. A "
               "escolha sincera é premissa e não dá para testar com estes dados."))
    return sl


# --------------------------------------------------------------------------------------------------------------
# Ideias do deck v4.1 de um colega do grupo (14/11, 3ª rodada): intuição com três vagas inventadas, o modelo formal
# com y e U, e por que não outro método. As chances das vagas A, B e C são calculadas com os pesos do VL-1.
# --------------------------------------------------------------------------------------------------------------
def abc(n) -> list[dict]:
    """Três vagas ilustrativas: A (R$ 10 mil, 50 km), B (+R$ 5 mil) e C (como B, mas os km equivalentes mais longe)."""
    km_c = 50 + round(n["km"])
    vagas = [("A", 10, 50), ("B", 15, 50), ("C", 15, km_c)]
    out = []
    for nome, bolsa, km in vagas:
        V = n["b"] * (bolsa - 10) + n["dist"] * (km - 50) / 100
        out.append({"nome": nome, "bolsa": bolsa, "km": km, "V": V})
    soma = sum(math.exp(x["V"]) for x in out)
    for x in out:
        x["P"] = math.exp(x["V"]) / soma
    if abs(out[1]["P"] / out[0]["P"] - n["rc"]) > 1e-9 or abs(out[2]["P"] - out[0]["P"]) > 0.005:
        raise SystemExit("ERRO: o exemplo A, B, C não reproduz a razão de chances e a equivalência em km")
    return out


def s_intuicao(M, prs, n):
    """Versão enxuta (pedido de 14/11, rodada 8): a estrutura do slide do colega, com menos texto."""
    vs = abc(n)
    sl = M.novo(prs, "Cada médico escolhe a vaga que mais vale a pena")
    caixa(sl, 0.25, 0.88, 12.83, 0.62,
          [[("Não vemos o que o médico pensa, só a vaga que ele pôs em 1º lugar.", 17, True, VERDE)]],
          fill=CLARO, nome="Faixa", margem=0.3)
    topo, alto, w, gap = 1.75, 3.2, 4.0, 0.415
    titulos = ("Cada médico tem uma lista de vagas", "Cada vaga tem prós e contras", "O modelo dá a chance de cada vaga")
    for k, tit in enumerate(titulos):
        x = 0.25 + k * (w + gap)
        caixa(sl, x, topo, w, alto, [], fill=CLARO, line=BORDA, nome=f"Etapa {k + 1}")
        caixa(sl, x + 0.2, topo + 0.2, 0.5, 0.5, [[(str(k + 1), 16, True, BRANCO)]], fill=VERDE,
              forma=MSO_SHAPE.OVAL, align=PP_ALIGN.CENTER, margem=0)
        texto(sl, x + 0.85, topo + 0.17, w - 1.0, 0.56, [[(tit, 15.5, True, TEXTO)]])
        if k < 2:
            seta(sl, x + w + 0.06, topo + alto / 2, x + w + gap - 0.06, topo + alto / 2, larg=2.5)
    # 1: as três vagas, uma linha cada
    for j, vg in enumerate(vs):
        caixa(sl, 0.45, topo + 0.95 + j * 0.72, w - 0.4, 0.6,
              [[(f"Vaga {vg['nome']}    ", 15, True, TEXTO), (f"R$ {vg['bolsa']} mil", 15, True, ACENTO_ESCURO),
                (f"   {vg['km']} km", 14, False, CINZA)]],
              fill=BRANCO, line=BORDA, nome=f"Vaga {vg['nome']}", margem=0.2)
    # 2: a favor e contra
    x = 0.25 + (w + gap)
    for j, (rot, t, fill, cor) in enumerate((("A favor: ", "bolsa maior, perto", "DCEFD9", VERDE),
                                              ("Contra: ", "longe, sem estrutura", "F8E0DD", "7A1C17"),
                                              ("Não vemos: ", "família, gosto pelo lugar", BRANCO, CINZA))):
        caixa(sl, x + 0.2, topo + 0.95 + j * 0.72, w - 0.4, 0.6, [[(rot, 14, True, cor), (t, 14, False, TEXTO)]],
              fill=fill, line=BORDA if fill == BRANCO else None, nome=f"Peso {j}", margem=0.2)
    # 3: chances, calculadas com os pesos estimados
    x = 0.25 + 2 * (w + gap)
    pmax = max(vg["P"] for vg in vs)
    for j, vg in enumerate(vs):
        y = topo + 1.0 + j * 0.55
        texto(sl, x + 0.25, y, 0.35, 0.4, [[(vg["nome"], 15, True, TEXTO)]])
        larg = 2.3 * vg["P"] / pmax
        caixa(sl, x + 0.6, y + 0.06, larg, 0.3, [], fill=VERDE if vg["nome"] == "B" else APAGADO,
              forma=MSO_SHAPE.RECTANGLE, nome=f"Barra {vg['nome']}")
        texto(sl, x + 0.68 + larg, y, 0.8, 0.4, [[(f"{v(100 * vg['P'], 0)}%", 15, True,
                                                   VERDE if vg["nome"] == "B" else CINZA)]])
    texto(sl, x + 0.25, topo + 2.7, w - 0.45, 0.4, [[("B paga mais e fica perto.", 14, True, TEXTO)]])
    caixa(sl, 0.25, 5.2, 12.83, 1.35,
          [[("Nossa pergunta: quanto a bolsa pesa? ", 17, True, BRANCO),
            ("Se vagas iguais, com bolsas diferentes, fossem escolhidas meio a meio, a bolsa não pesaria nada.", 16,
             False, BRANCO)]],
          fill=VERDE, nome="Pergunta do método", margem=0.4)
    fontes(sl, "Fontes: McFadden (1974); Train (2009), Discrete Choice Methods with Simulation. Vagas A, B e C "
               "ilustrativas; chances calculadas com os pesos estimados do modelo principal. Elaboração própria.")
    notas(sl, ("Fala (≈ 1 min). Não temos como perguntar a cada médico o que ele pensa; temos a lista de vagas que ele "
               "podia escolher e a vaga que pôs em 1º lugar. Cada vaga tem prós (bolsa maior, ficar perto de onde já "
               "trabalha) e contras (longe, município sem estrutura), e coisas que não vemos, como família e gosto pelo "
               "lugar; por isso o modelo dá a chance de cada vaga, não uma certeza. No exemplo, B ganha de A porque "
               f"paga R$ 5 mil a mais (chance ×{v(n['rc'])}); C paga como B, mas fica {vs[2]['km'] - 50} km mais "
               f"longe, e isso anula a bolsa extra: A e C ficam com {v(100 * vs[0]['P'], 1)}% e B com "
               f"{v(100 * vs[1]['P'], 1)}%. As vagas são inventadas; os pesos são os estimados (β₁ = {v(n['b'], 3)} por "
               f"R$ 1 mil, β₂ = {v(n['dist'], 3)} por 100 km). A pergunta: se a bolsa não pesasse, vagas iguais com "
               "bolsas diferentes seriam escolhidas meio a meio. Próximo slide: a forma do modelo."))
    return sl


def s_formal(M, prs, n):
    vs = abc(n)
    sl = M.novo(prs, "Anexo 5: o modelo formal, do valor à escolha")
    cards = (("1 · UTILIDADE (NÃO OBSERVADA)", "U_{iv} = β·x_{iv} + ε_{iv}",
              "β·x: bolsa, distância, IVS, X e par de UFs, com os pesos. ε: o que não vemos (família, gosto)."),
             ("2 · ESCOLHA OBSERVADA (0 OU 1)", "y_{iv} = 1  se  U_{iv} > U_{ik}",
              "para toda outra vaga k do candidato: y = 1 na vaga posta em 1º; 0 nas demais."),
             ("3 · CHANCE", ("P(y_{iv} = 1) =", "exp(β·x_{iv}) ÷ soma de exp(β·x_{ik})"),
              "Vale se ε é de valor extremo. Os pesos saem por máxima verossimilhança."),
             ("4 · RAZÃO DE CHANCES", ("P(B) ÷ P(A) = exp(5β_{1})", f"= exp(5 × {v(n['b'], 3)}) = {v(n['rc'])}"),
              "B paga +R$ 5 mil, o resto igual: o que é do médico e o denominador se cancelam."))
    w, gap = 3.0, 0.277
    for k, (rot, f, expl) in enumerate(cards):
        x = 0.25 + k * (w + gap)
        ult = k == 3
        caixa(sl, x, 0.9, w, 2.2, [], fill=VERDE if ult else BRANCO, line=None if ult else BORDA, nome=f"Formal {k + 1}")
        texto(sl, x + 0.2, 0.98, w - 0.35, 0.3, [[(rot, 10.5, True, "B9E4B1" if ult else VERDE2)]])
        fs = f if isinstance(f, tuple) else (f,)
        texto(sl, x + 0.15, 1.32, w - 0.3, 0.75, [eq(x_, 13.5 if len(fs) > 1 else 15, BRANCO if ult else TEXTO)
                                                   for x_ in fs], align=PP_ALIGN.CENTER)
        texto(sl, x + 0.2, 2.12, w - 0.38, 0.92, [[(expl, 11, False, "DDEBDD" if ult else TEXTO)]],
              anchor=MSO_ANCHOR.TOP)
        if k < 3:
            seta(sl, x + w + 0.03, 2.0, x + w + gap - 0.03, 2.0, larg=2.0)
    # tabela A, B, C
    subtitulo(sl, 0.25, 3.28, 7.9, "Exemplo: as vagas A, B e C, com os pesos estimados")
    cols = (("Vaga", 0.7), ("Bolsa", 1.1), ("Distância", 1.1), ("β·x (sem ε)", 1.1), ("P(y = 1)", 1.05), ("y", 0.5),
            ("Razão vs. A", 2.2))
    y0, h = 3.7, 0.42
    x = 0.25
    for nome, cw in cols:
        caixa(sl, x, y0, cw, h, [[(nome, 11.5, True, BRANCO)]], fill=VERDE, forma=MSO_SHAPE.RECTANGLE,
              align=PP_ALIGN.CENTER, margem=0.03)
        x += cw
    for j, vg in enumerate(vs):
        destaque = vg["nome"] == "B"
        razao = "1,00 (base)" if j == 0 else f"{v(100 * vg['P'], 1)} ÷ {v(100 * vs[0]['P'], 1)} = {v(vg['P'] / vs[0]['P'])}"
        vals = (vg["nome"], f"R$ {vg['bolsa']} mil", f"{vg['km']} km", v(vg["V"] + 0.0 if round(vg["V"], 2) else 0.0),
                f"{v(100 * vg['P'], 1)}%",
                "1" if destaque else "0", razao)
        x = 0.25
        for (nome, cw), val in zip(cols, vals):
            caixa(sl, x, y0 + (j + 1) * h, cw, h, [[(val, 12, destaque, TEXTO)]],
                  fill="DCEFD9" if destaque else (CLARO if j % 2 == 0 else BRANCO), line=BORDA,
                  forma=MSO_SHAPE.RECTANGLE, align=PP_ALIGN.CENTER, margem=0.03)
            x += cw
    texto(sl, 0.25, y0 + 4 * h + 0.1, 7.75, 0.85,
          [[("Ilustrativo: ", 10.5, True, CINZA),
            (f"vagas inventadas. Só as diferenças de β·x importam, por isso β·x(A) = 0. B: +R$ 5 mil somam "
             f"5 × {v(n['b'], 3)} ≈ {v(vs[1]['V'])}. C: os {vs[2]['km'] - 50} km a mais tiram o mesmo. Com ≈ 107 vagas "
             "por candidato, cada chance fica perto de 1%, mas a razão entre duas vagas é a mesma.", 10.5, False, CINZA)]],
          anchor=MSO_ANCHOR.TOP)
    caixa(sl, 8.45, 3.3, 4.63, 3.35,
          [[("y é o resultado.", 20, True, BRANCO)], [("U é o mecanismo.", 20, True, BRANCO)],
           [("Como no logit binário: ", 12.5, True, "B9E4B1"),
            ("há um valor que não vemos, e y = 1 quando ele passa de um limiar. Aqui o limiar é o maior U entre as "
             "outras vagas.", 12.5, False, BRANCO)],
           [("β não tem unidade própria ", 12.5, True, "B9E4B1"),
            (f"(a escala vem de ε): por isso lemos comparações, ×{v(n['rc'])} na chance ou {round(n['km'])} km.",
             12.5, False, BRANCO)]],
          fill=VERDE, nome="y e U", margem=0.3, esp=6)
    fontes(sl, "Fontes: McFadden (1974); Train (2009), Discrete Choice Methods with Simulation. Pesos do modelo "
               "principal (ciclos 1–3). Elaboração própria.")
    notas(sl, ("Use se a banca pedir a forma do modelo. Não observamos quanto cada vaga vale para o médico (U); "
               "observamos só qual ele pôs em 1º lugar (y). O modelo supõe que ele lista em 1º a vaga de maior U, com "
               "uma parte que medimos (β·x: bolsa, distância, IVS, controles, par de UFs) e uma que não medimos (ε). Se "
               "ε é i.i.d. de valor extremo (Gumbel), a chance de a vaga v ter o maior U é exp(β·x_v) ÷ soma de exp(β·x_k) "
               "nas vagas do candidato. Os pesos saem por máxima verossimilhança (Newton–Raphson): os que tornam as 1ªs "
               "opções observadas as mais prováveis. A razão de chances entre duas vagas do mesmo candidato é "
               "exp(β·x_B − β·x_A): o denominador e tudo o que é do médico se cancelam. No exemplo, A, B e C são "
               "inventadas e os pesos são os estimados."))
    return sl


def s_alternativas(M, prs, n):
    sl = M.novo(prs, "Anexo 6: por que este modelo e não outro")
    caixa(sl, 0.25, 0.88, 12.83, 0.5,
          [[("Havia outros jeitos de medir o peso da bolsa. Em cada linha: o que o método faz e por que não é o "
             "principal.", 14, True, VERDE)]], fill=CLARO, nome="Faixa", margem=0.25)
    linhas_ = (
        ("Comparar vagas dos dois lados do corte", "RDD por vaga",
         "Conta quantos médicos puseram em 1º as vagas logo abaixo e logo acima do corte de IVS.",
         "Feita: o intervalo contém zero. Compara vagas entre si e perde que o mesmo médico viu bolsas diferentes."),
        ("Regressão linear de 0 ou 1", "MQO com efeito fixo do médico",
         "Para cada vaga de cada médico: 1 se foi a 1ª opção, 0 se não; uma reta explica isso pela bolsa.",
         "Cada vaga tem ≈ 1% de chance: a reta pode prever chances negativas ou acima de 100%."),
        ("Contar escolhas por vaga", "Poisson das contagens",
         "Conta quantos médicos de cada grupo escolheram cada vaga e explica essas contagens.",
         "Dá exatamente o mesmo β do nosso modelo (Guimarães, Figueiredo e Woodward, 2003): outro caminho, mesma conta."),
        ("Versões mais ricas do nosso modelo", "logit misto ou aninhado",
         "Deixam o gosto variar entre médicos ou agrupam vagas parecidas.",
         "Servem quando o salário é de mercado (Costa, Nunes e Sanches) ou dá para recusar tudo (Bobba et al.). Aqui a "
         "bolsa vem de regra: ficaram como teste extra, no modelo base."),
        ("O nosso: comparar as vagas de cada médico", "logit condicional (McFadden, 1974)",
         "Para cada médico, compara as vagas que ele podia escolher e estima o peso de cada característica.",
         "Por que sim: é o modelo padrão para escolher uma entre várias opções e usa toda a informação de cada "
         "médico. Com a bolsa vinda de regra, a versão simples basta."),
    )
    for k, (tit, sub, faz, nao) in enumerate(linhas_):
        nosso = k == 4
        y = 1.52 + k * 1.03 + (0.1 if nosso else 0)
        cor, cor2 = (BRANCO, "DDEBDD") if nosso else (TEXTO, CINZA)
        caixa(sl, 0.25, y, 12.83, 0.93, [], fill=VERDE if nosso else CLARO, line=None if nosso else BORDA,
              nome=f"Alternativa {k + 1}")
        texto(sl, 0.45, y + 0.08, 3.75, 0.8, [[(tit, 13.5, True, cor)], [(sub, 10.5, False, cor2)]])
        texto(sl, 4.35, y + 0.08, 4.1, 0.8, [[("O que faz: ", 11.5, True, cor), (faz, 11.5, False, cor)]])
        linha(sl, 8.6, y + 0.12, 8.6, y + 0.81, cor="B9E4B1" if nosso else APAGADO, larg=1.5)
        texto(sl, 8.75, y + 0.08, 4.15, 0.8,
              [[("Por que sim: " if nosso else "Por que não: ", 11.5, True, cor),
                (nao.removeprefix("Por que sim: "), 11.5, False, cor)]])
    fontes(sl, "Fontes: McFadden (1974); Guimarães, Figueiredo e Woodward (2003), REStat 85(1); Bobba et al. (2026), "
               "NBER WP 29068; Costa, Nunes e Sanches (2024), REStat. Elaboração própria.")
    notas(sl, ("Use se a banca perguntar por que não outro método (doc 11 da banca 2). A RDD por vaga, com o número de "
               "candidatos de 1ª opção como resultado, foi feita (F1.1 e a ponte P1g) e o intervalo contém zero: só usa "
               "a variação entre vagas e perde que o mesmo candidato viu vagas com bolsas diferentes. O MQO com efeito "
               "fixo do candidato faz a mesma comparação, mas a chance de cada vaga é perto de 1% e o modelo prevê "
               "probabilidades fora de [0, 1]; não está no protocolo. A Poisson das contagens, com efeito fixo de cada "
               "grupo de candidatos com as mesmas vagas e o mesmo local anterior, dá exatamente o β do logit "
               "condicional (Guimarães, Figueiredo e Woodward, 2003). O logit misto (M8) e o aninhado por região de "
               f"saúde (M9) entraram como sensibilidade no modelo base, sem o par de UFs: no aninhado, λ = "
               f"{v(n['lambda'])} e o peso da bolsa fica {v(n['b_m9'], 3)} contra {v(n['b_m1'], 3)}. Pelas regras do "
               "projeto não se troca o estimador depois de ver o resultado; outra versão entraria só como robustez "
               "rotulada."))
    return sl


NOVOS = {"cadeia1": lambda M, p, n: s_cadeia(M, p, n, 2), "cadeia2": lambda M, p, n: s_cadeia(M, p, n, 3),
         "hipotese": s_hipotese, "linhas": s_linhas, "intuicao": s_intuicao, "modelo": s_modelo, "passos": s_passos,
         "estimacao": s_estimacao, "identificacao": s_identificacao,
         "resultados": lambda M, p, n: (s_resultados_colega if COM_IDEIAS_COLEGA else s_resultados)(M, p, n),
         "robustez": s_robustez, "conclusao": s_conclusao, "limitacoes": s_limitacoes, "formal": s_formal,
         "alternativas": s_alternativas}



# --------------------------------------------------------------------------------------------------------------
# Montagem
# --------------------------------------------------------------------------------------------------------------
def refazer_descritiva(prs, n) -> list[str]:
    """Slide 17 do grupo (descritiva), pedido de 14/11: o histograma da distância primeiro, depois onde fica a 1ª
    opção; cartões em números, na ordem dos gráficos; títulos descritivos; nada sobre o modelo. Números de
    output/apresentacao_banca2/numeros_banca2.json (ESC_*)."""
    s = prs.slides[16]
    sh = {x.name: x for x in s.shapes}
    esp = {"Text 21", "Text 3", "Text 5", "Text 7", "Text 9", "Text 11", "Text 13", "Text 15", "Text 17", "Text 18", "Text 19",
           "Text 20", "Chart 0", "Image 0", "Text 22"}
    if not esp <= set(sh):
        raise SystemExit(f"ERRO: descritiva do grupo sem as formas esperadas: {sorted(esp - set(sh))}")
    e = n["esc"]

    def trocar(nome, novo):
        tf = sh[nome].text_frame
        p0 = tf.paragraphs[0]
        for p_ in tf.paragraphs[1:]:
            p_._p.getparent().remove(p_._p)
        runs = p0.runs
        runs[0].text = novo
        for r in runs[1:]:
            r._r.getparent().remove(r._r)

    novos = {"Text 3": "50%", "Text 5": f"escolhem uma vaga a até {e['p50']} km de onde trabalhavam",
             "Text 7": "75%", "Text 9": f"escolhem uma vaga a até {e['p75']} km",
             "Text 11": f"{e['uf']}%", "Text 13": "escolhem uma vaga na UF onde trabalhavam",
             "Text 15": f"{e['mun']}%", "Text 17": "escolhem uma vaga no próprio município",
             "Text 20": "I. A que distância fica a 1ª opção",
             "Text 18": "II. Onde fica a 1ª opção",
             "Text 19": "% de candidatos com a 1ª opção na mesma UF, região ou município"}
    for nome, novo in novos.items():
        trocar(nome, novo)
    # rodada 7 (14/11): os cartões repetiam os gráficos; no lugar, como a análise foi montada
    for nome in ("Shape 2", "Text 3", "Shape 4", "Text 5", "Shape 6", "Text 7", "Shape 8", "Text 9", "Shape 10",
                 "Text 11", "Shape 12", "Text 13", "Shape 14", "Text 15", "Shape 16", "Text 17"):
        remover(sh[nome])
    caixa(s, 0.25, 0.92, 12.83, 1.45, [], fill=CLARO, line=BORDA, nome="Como montamos")
    texto(s, 0.5, 0.98, 6.0, 0.3, [[("COMO MONTAMOS ESTA ANÁLISE", 10.5, True, VERDE2)]])
    passos_ = (("Quem", f"{e['n']} candidatos com 1ª opção nos ciclos 1–3 e local de trabalho anterior conhecido"),
               ("Distância", "do município onde trabalhava (vínculo no CNES antes da inscrição) ao da vaga posta em 1º"),
               ("Onde", "se essa vaga fica na mesma UF, na mesma região de saúde ou no mesmo município"))
    for k, (rot, t) in enumerate(passos_):
        x = 0.5 + k * 4.2
        caixa(s, x, 1.38, 0.4, 0.4, [[(str(k + 1), 12, True, BRANCO)]], fill=VERDE, forma=MSO_SHAPE.OVAL,
              align=PP_ALIGN.CENTER, margem=0)
        texto(s, x + 0.5, 1.32, 3.55, 0.98, [[(rot + ": ", 13, True, VERDE), (t, 12.5, False, TEXTO)]],
              anchor=MSO_ANCHOR.TOP)
    # troca de lado: o histograma (direita) vem para a esquerda, as barras vão para a direita
    desloc = sh["Text 20"].left - sh["Text 18"].left
    for nome in ("Text 18", "Text 19", "Chart 0"):
        sh[nome].left = sh[nome].left + desloc
    for nome in ("Text 20", "Text 21", "Image 0", "Text 22"):
        sh[nome].left = sh[nome].left - desloc
    return ["slide 17 do grupo: cartões trocados por 'como montamos esta análise'; histograma primeiro; títulos "
            "descritivos"]


def corrigir(prs) -> list[str]:
    """Troca por parágrafo (os runs do grupo vêm picados): junta o texto no 1º run, mantendo a formatação dele."""
    feitas = []
    for num, antigo, novo, *modo in CORRECOES:
        exato = bool(modo) and modo[0] == "exato"  # só o parágrafo inteiro igual a `antigo`
        achou = 0
        for sh in formas(prs.slides[num - 1].shapes):
            if not sh.has_text_frame:
                continue
            for par in sh.text_frame.paragraphs:
                runs = par.runs
                inteiro = "".join(r.text for r in runs)
                if antigo not in inteiro or (exato and inteiro.strip() != antigo):
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
    # rodada 8 (14/11): o plano original sai da apresentação inteira, também das notas do anexo da regra do IVS
    s = prs.slides[32]
    tf = s.notes_slide.notes_text_frame if s.has_notes_slide else None
    if tf is not None and "Pós-resultado:" in tf.text:
        t = tf.text
        i0 = t.index("Pós-resultado:")
        i1 = t.index("Tudo é condicional", i0)
        tf.text = t[:i0] + t[i1:]
        tiradas.append("slide 33 do grupo: frase sobre o plano pré-registrado retirada das notas")
    return tiradas


def construir() -> dict:
    if sha256(ENT) != SHA_ENT:
        raise SystemExit("ERRO: o deck do grupo de 14/11 mudou (hash diferente)")
    prs = Presentation(str(ENT))
    if len(prs.slides) != N_ENT:
        raise SystemExit(f"ERRO: esperava {N_ENT} slides no deck do grupo")
    n = numeros()
    feitas = corrigir(prs) + corrigir_anexo(prs) + tirar_anotacoes(prs) + refazer_descritiva(prs, n)
    grupo = list(prs.slides)
    M = Modelo(prs)
    ordem = [x for x in ORDEM if COM_IDEIAS_COLEGA or not (x[0] == "N" and x[1] in IDEIAS_COLEGA)]
    novos = {nome: f(M, prs, n) for nome, f in NOVOS.items() if COM_IDEIAS_COLEGA or nome not in IDEIAS_COLEGA}
    usados = {k for t, k, _ in ordem if t == "G"}
    if usados | set(FORA) != set(range(1, N_ENT + 1)) or usados & set(FORA):
        raise SystemExit("ERRO: cada slide do grupo tem de estar na ORDEM ou em FORA")
    lista = prs.slides._sldIdLst
    ids = {id(s): el for s, el in zip(prs.slides, list(lista))}
    sequencia = []
    for t, k, secao in ordem:
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
        alinhar_titulo(s)
        if t == "G" and s._element.get("show") == "0":
            raise SystemExit(f"ERRO: slide oculto mantido ({k})")
        tits = [sh for sh in s.shapes if sh.is_placeholder and "TITLE" in str(sh.placeholder_format.type)]
        titulo = tits[0].text_frame.text if tits else ""
        manifesto.append({"posicao": pos, "origem": "grupo 14/11" if t == "G" else "novo", "slide_origem": k,
                          "secao": secao, "titulo": " ".join(titulo.split())})
    OUT.mkdir(parents=True, exist_ok=True)
    pptx = OUT / f"{arquivo()}.pptx"
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


def arquivo() -> str:
    """A nossa versão (a que foi para o colega) e a conciliada, com as ideias dele, saem em arquivos separados."""
    return ARQ + ("_conciliado" if COM_IDEIAS_COLEGA else "")


def main(argv=None) -> int:
    global COM_IDEIAS_COLEGA
    COM_IDEIAS_COLEGA = "--com-colega" in (sys.argv[1:] if argv is None else argv)
    res = construir()
    pdf = OUT / f"{arquivo()}.pdf"
    ok_pdf = converter_pdf(res["pptx"], pdf)
    entradas = [ENT, F_VL, F_VLR, F_VG, F_P1R, F_P1E, F_S57, F_R1, F_NB2, F_EX, FIG_COEF, FIG_ROB] + (
        [FIG_SEIS] if COM_IDEIAS_COLEGA else [])
    man = {"etapa": "deck_banca_final_grupo", "natureza_dos_dados": "EMPIRICO",
           "script": str(Path(__file__).resolve().relative_to(ROOT)), "doc_conteudo": DOC,
           "entradas": {str(p.relative_to(ROOT)): sha256(p) for p in entradas},
           "slides": res["manifesto"], "fora_do_deck": {str(k): v_ for k, v_ in FORA.items()},
           "correcoes_e_retiradas": res["feitas"],
           "saidas": {str(res["pptx"].relative_to(ROOT)): sha256(res["pptx"]),
                      **({str(pdf.relative_to(ROOT)): "gerado (PDF não é determinístico)"} if ok_pdf else {})}}
    (OUT / f"manifesto_{arquivo()}.json").write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(res['manifesto'])} slides; PDF {'ok' if ok_pdf else 'FALHOU'}")
    return 0 if ok_pdf else 1


if __name__ == "__main__":
    sys.exit(main())
