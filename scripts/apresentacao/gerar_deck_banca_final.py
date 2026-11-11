"""Deck da banca final: a parte da banca 1 (motivação e teoria), ajustada pelo feedback da banca 2 de 04/11/2026,
seguida do deck da banca 2 revisto depois dessa banca e do apêndice de teoria.

Conteúdo canônico: docs/07_apresentacoes/banca_final/02_deck_banca_final.md. O deck é derivado; divergência entre
ele e o doc é erro do deck.

Entradas (só leitura, todas em output/):
- output/apresentacao_banca_final/deck_proposta_reorganizada.pptx — deck do grupo da banca 1 reorganizado, com o
  diagrama da teoria da mudança (scripts/apresentacao/gerar_diagrama_banca_final.py);
- output/apresentacao_banca2/deck_banca2_pos_banca.pptx — a banca 2 revista depois da banca de 04/11/2026
  (scripts/apresentacao/gerar_deck_banca2_pos_banca.py; doc 12 da banca 2);
- output/apresentacao_banca1/especialistas_por_uf_extremos.png e vagas_ciclo1_por_regiao.png — figuras do pipeline
  da banca 1 (gerar_figuras_banca1.py), no lugar dos gráficos do grupo sem fonte reproduzível (P6, P7).

O feedback de 04/11 (doc 12 da banca 2, §1.2) vale também para a parte da banca 1: menos slides (saem os sumários),
navegação só com as seções que existem e igual em todos os slides, "origem" fora da tela, título da capa pela
pergunta. Nada é estimado; nada é lido de data/. Cada troca de texto confere o texto antigo antes de trocar.

    python3 scripts/apresentacao/gerar_deck_banca_final.py            # .pptx, .pdf e manifesto
    python3 scripts/apresentacao/gerar_deck_banca_final.py --sem-pdf
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[2]
# Deck atual do grupo (09/11/2026), guardado sem alteração; é a base do design
ENT_GRUPO = ROOT / "docs/07_apresentacoes/banca_final/grupo/deck_grupo_banca_final_0911.pptx"
SHA_GRUPO = "b5ed0d74807526e6288d7f15837c71c76f9be236116cef151430857baf15ce42"
N_GRUPO = 35
# Deck do grupo reorganizado de 26/10, só para o slide do diagrama da teoria da mudança (gerar_diagrama_banca_final.py)
ENT_DIAG = ROOT / "output/apresentacao_banca_final/deck_proposta_reorganizada.pptx"
N_DIAG_SLIDE = 16
ENT_PB = ROOT / "output/apresentacao_banca2/deck_banca2_pos_banca.pptx"
FIG_UF = ROOT / "output/apresentacao_banca1/especialistas_por_uf_extremos.png"
FIG_VAGAS = ROOT / "output/apresentacao_banca1/vagas_ciclo1_por_regiao.png"
SAIDA = ROOT / "output/apresentacao_banca_final"
ARQ_DECK = "deck_banca_final.pptx"
ARQ_PDF = "deck_banca_final.pdf"
ARQ_MANIF = "manifesto_deck_banca_final.json"
DOC = "docs/07_apresentacoes/banca_final/02_deck_banca_final.md"

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
QN_EMBED = "{%s}embed" % NS["r"]
QN_RID = "{%s}id" % NS["r"]

# --------------------------------------------------------------------------------------------------------------
# Ordem do deck final. ("G", n) = slide n do deck do grupo reorganizado (banca 1); ("PB", n) = slide n do deck
# pós-banca da banca 2. A seção é a marcada na navegação do rodapé (None: nenhuma, como na capa e no apêndice).
# --------------------------------------------------------------------------------------------------------------
SECOES = ("Motivação", "Literatura", "Hipótese", "Dados", "Análise Descritiva", "Metodologia", "Identificação",
          "Resultados", "Robustez", "Discussão")
ORDEM = [
    ("G", 1, None),                  # capa, com o título da pergunta
    ("G", 3, "Motivação"),           # escassez de especialistas (figuras do pipeline)
    ("PB", 2, "Motivação"),          # a bolsa por faixa de IVS e a pergunta
    ("D", N_DIAG_SLIDE, "Literatura"),  # diagrama A: teoria da mudança
    ("PB", 3, "Hipótese"),
    ("PB", 4, "Dados"),
    ("PB", 5, "Análise Descritiva"),
    ("M", 1, "Metodologia"),         # novo: o método passo a passo
    ("M", 2, "Metodologia"),         # novo: exemplo com três vagas e os pesos do VL-1
    ("PB", 6, "Metodologia"),
    ("PB", 7, "Metodologia"),
    ("PB", 8, "Identificação"),
    ("PB", 9, "Resultados"),
    ("PB", 10, "Robustez"),
    ("PB", 11, "Discussão"),
    ("PB", 12, "Discussão"),
    ("G", 31, None),                 # Q&A
    ("G", 32, None),                 # divisor Apêndice
    ("PB", 14, None),                # A1: a bolsa segue exatamente o IVS
    ("G", 16, None),                 # três elementos da teoria
    ("G", 17, None),                 # escolha locacional maximiza a utilidade
    ("G", 19, None),                 # renda real líquida
    ("G", 20, None),                 # custo geográfico e laboral
    ("G", 18, None),                 # da escolha individual ao agregado
    ("G", 35, None),                 # o IVS
]
SUMARIO = "sumário do grupo: sai pelo pedido 'menos slides' (doc 12 da banca 2, §1.2); a navegação do rodapé fica"
# Slides do deck do grupo que saem, com o motivo (vão para o manifesto e para o doc 02)
FORA_G = {
    2: SUMARIO, 12: SUMARIO, 15: SUMARIO, 22: SUMARIO, 24: SUMARIO, 26: SUMARIO, 28: SUMARIO,
    4: "oculto; figura de UF do grupo sem fonte reproduzível (P6)",
    5: "animação parcial do slide 7",
    6: "animação parcial do slide 7",
    7: "IVS e bolsa: a regra em três faixas está no slide pós-banca 2 e o IVS em detalhe no apêndice; tinha o "
       "'piso' e a grade do FAQ (errata E10)",
    8: "oculto; versão antiga do mapa do IVS",
    9: "crescimento por faixa que não se reproduz (P12) e distribuição regional com diferença sem origem (P13)",
    10: "oculto; rodapé antigo",
    11: "oculto; 'indícios de efetividade' (antes/depois sem comparação; errata E6, P12)",
    13: "pergunta antiga (preenchimento) sobre fundo com números que não se reproduzem; a pergunta está no "
        "slide pós-banca 2",
    14: "oculto; tabela de inclinações que não se reproduz (P8)",
    21: "oculto; versão anterior do slide 18",
    23: "hipótese na redação que a banca de 04/11 apontou como errada (bolsa que 'aumenta' e efeito no "
        "município), sobreposta às derivadas; a hipótese vigente está no slide pós-banca 3",
    25: "dados: o slide pós-banca 4 traz a mesma base com a construção das variáveis e o funil até o modelo "
        "principal (5.417); o do grupo tem números sobrepostos e o 5.421 do modelo base",
    27: "marcador 'X' do grupo", 29: "EXEMPLO de outro trabalho (limitações)", 30: "EXEMPLO de outro trabalho",
    33: "viabilidade empírica da banca 1, substituída pela banca 2 (erratas E4 e E5)",
    34: "viabilidade empírica da banca 1, substituída pela banca 2 (erratas E4 e E5)",
}
ORIGENS = {"G": "deck do grupo", "D": "diagrama (deck reorganizado)", "PB": "banca 2 pós-banca",
           "M": "novo, método passo a passo"}
FORA_PB = {
    1: "capa da banca 2: a capa é a do grupo, com o mesmo título novo",
    13: "Q&A da banca 2: o Q&A é o do grupo",
}

# --------------------------------------------------------------------------------------------------------------
# Textos novos (os mesmos do doc 02; o teste confere)
# --------------------------------------------------------------------------------------------------------------
TITULO_CAPA = ("A bolsa maior atrai a 1ª opção?", "Um modelo de escolha para o", "Programa Mais Médicos Especialistas")
SUB2_UF = "Especialistas por 100 mil habitantes, as duas maiores e as duas menores UFs – dez/2024"
SUB_VAGAS = "II. O ciclo 1 do PMM-E abriu vagas nas cinco regiões"
SUB2_VAGAS = "Células estabelecimento × curso e vagas imediatas, ciclo 1, 1ª chamada"
FONTES_ESCASSEZ = ("Fontes: Medicina S/A; Amado Mundo; Agência Câmara; Scheffer et al., Demografia Médica no Brasil "
                   "2025 (FMUSP/AMB), só as UFs com valor citado; quadro de vagas do Edital SGTES/MS nº 3/2025.")
A4_DIAGRAMA = "Moradia, deslocamento, amenidades e distância de casa."
CTEXT_UTILIDADE = ("A política mexe em apenas uma variável: eleva E(w|B) pela bolsa (B). Preços e custo do local "
                   "continuam contra, e é a soma das três variáveis que decide qual vaga o médico escolhe.")
ROTULO_CADEIA = "CADEIA DO MODELO"
ADICOES = "Adições ao modelo do slide anterior:"

# ---- Slides novos do método (pedido do autor, 09/11/2026: a banca não entendeu o método e nunca tinha ouvido falar) --
VL_EST = ROOT / "output/rdd_bolsa/VL_estimativas.csv"
TITULO_M1 = "Método passo a passo: logit condicional"
SUB_M1 = ("I. Como o modelo lê cada escolha", "McFadden (1974), Nobel de 2000; o mesmo modelo de Bobba et al. (2026)")
PASSOS_M1 = (
    ("Cardápio", "todas as vagas do curso no ciclo (≈ {cardapio})"),
    ("Escolha", "1ª opção = 1; as outras = 0"),
    ("Pontuação", "β·bolsa + δ·distância + par de UFs"),
    ("Chance", "e^pontuação ÷ soma do cardápio"),
)
SUB2_M1 = ("II. O que sai", "os pesos que melhor explicam as escolhas observadas")
CAIXA_M1 = ("PESO DA BOLSA", "β = {b}", "por R$ 1 mil/mês")
CONDICIONAL_M1 = ("Condicional:", "só compara vagas do mesmo médico")
FONTES_M1 = ("Fontes: McFadden (1974); Bobba et al. (NBER WP 29068, rev. jan. 2026); "
             "output/rdd_bolsa/VL_estimativas.csv (VL-1, adendo 52e): {cand} candidatos, {linhas} linhas.")
TITULO_M2 = "Exemplo: um candidato, três vagas"
SUB_M2 = ("I. Mesmo curso, mesma UF (MG)", "ilustrativo: vagas inventadas, pesos estimados no VL-1")
VAGAS_M2 = (("A", 10, 50), ("B", 15, 50), ("C", 15, 125))  # ilustrativo: bolsa (R$ mil/mês) e distância (km)
SUB2_M2 = ("II. O que o exemplo mostra", "B e C pagam R$ 5 mil a mais que A")
CAIXAS_M2 = (("B CONTRA A", "×{rc}", "mesma distância: é o resultado"),
             ("C CONTRA A", "{km} km", "a distância come os R$ 5 mil"))
FONTES_M2 = "Fontes: output/rdd_bolsa/VL_estimativas.csv (VL-1, ciclos 1–3, adendo 52e; doc 57x; auditoria 48)."
NOTAS_M = {
    1: ("Este é o slide que a banca pediu: o método em quatro passos, sem equação. (1) Cada candidato tem um "
        "cardápio: as vagas abertas do seu curso no ciclo, umas cem em média. (2) Na base, ele aparece uma vez para "
        "cada vaga do cardápio; a vaga que marcou como 1ª opção vale 1. (3) Cada vaga ganha uma pontuação, que soma "
        "o peso da bolsa, o peso da distância, o par de UFs e os controles; a chance de uma vaga ser a escolhida é a "
        "pontuação exponenciada dividida pela soma do cardápio. (4) O computador procura os pesos que tornam as "
        "escolhas que de fato aconteceram as mais prováveis. É o modelo de escolha discreta de McFadden, o mesmo "
        "usado em demanda de transporte e em escolha de escola; o caso mais parecido com o nosso é o de Bobba et "
        "al., professores escolhendo vagas no Peru. Como a comparação é sempre entre vagas do mesmo cardápio, para o "
        "mesmo médico, o que é do médico se cancela: é isso que o \"condicional\" quer dizer."),
    2: ("Um exemplo com números. Um candidato de MG vê três vagas do mesmo curso. A paga R$ 10 mil e fica a 50 km; "
        "B paga R$ 15 mil e fica a 50 km; C paga R$ 15 mil, mas fica a 125 km. Com os pesos que estimamos, a "
        "pontuação de B é maior que a de A, e a chance de B ser a 1ª opção fica 1,47 vez a de A: é exatamente o "
        "×1,47 do resultado. C paga o mesmo que B, mas está 75 km mais longe, e a distância come o ganho da bolsa: "
        "C volta à chance de A. Daí vem a frase \"R$ 5 mil valem cerca de 75 km\". As vagas são inventadas; os pesos, "
        "não."),
}
NOTAS = {
    3: ("A escassez de especialistas é desigual entre as UFs: na Demografia Médica 2025, de 453 por 100 mil no DF a "
        "68 no MA (só as UFs com valor citado na fonte). O ciclo 1 do PMM-E abriu 1.295 células estabelecimento × "
        "curso em 368 municípios das cinco regiões, com 678 vagas imediatas. Os gráficos do grupo com as 16 UFs e "
        "com o deslocamento por região saíram: não têm fonte primária reproduzível (pendências P6 e P7 da banca 1)."),
    16: ("A teoria em uma figura. 1: a regra. O IVS 2010 oficial define a faixa da bolsa, com cortes em 0,300 e "
         "0,400. 2: a escolha do médico. A bolsa eleva o salário esperado; o custo de viver ali e o custo de "
         "trabalhar ali puxam contra; o saldo é o valor da vaga. 3: da vaga à saúde. Quanto maior o valor, maior a "
         "parcela de médicos que escolhe a vaga. A nossa hipótese testa só esse elo, a escolha (a 1ª opção na "
         "inscrição); preenchimento, capacidade, acesso e saúde são a cadeia do programa, não testada aqui. As "
         "equações estão no apêndice."),
}


# --------------------------------------------------------------------------------------------------------------
def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def formas(shapes):
    for sh in shapes:
        if sh.shape_type == 6:
            yield from formas(sh.shapes)
        else:
            yield sh


def por_texto(slide, texto: str, inicio: bool = False):
    """A única forma cujo texto (espaços normalizados) é `texto` (ou começa com ele)."""
    achadas = []
    for sh in formas(slide.shapes):
        if not sh.has_text_frame:
            continue
        t = " ".join(sh.text_frame.text.split())
        if (t.startswith(texto) if inicio else t == " ".join(texto.split())):
            achadas.append(sh)
    if len(achadas) != 1:
        raise SystemExit(f"ERRO: esperava 1 forma com o texto {texto!r}; achei {len(achadas)}")
    return achadas[0]


def por_nome(slide, nome: str):
    achadas = [sh for sh in formas(slide.shapes) if sh.name == nome]
    if len(achadas) != 1:
        raise SystemExit(f"ERRO: esperava 1 forma chamada {nome!r}; achei {len(achadas)}")
    return achadas[0]


def trocar_paragrafo(sh, novo: str, par: int = 0, antigo: str | None = None) -> None:
    """Troca o texto do parágrafo `par`, mantendo a formatação do primeiro run; confere o texto antigo."""
    p = sh.text_frame.paragraphs[par]
    if antigo is not None and " ".join(p.text.split()) != " ".join(antigo.split()):
        raise SystemExit(f"ERRO: texto antigo não confere em {sh.name!r}: {p.text!r}")
    runs = p.runs
    if not runs:
        raise SystemExit(f"ERRO: parágrafo sem run em {sh.name!r}")
    runs[0].text = novo
    for r in runs[1:]:
        r._r.getparent().remove(r._r)
    for br in p._p.findall("a:br", NS):
        p._p.remove(br)


def trocar_forma(sh, novo: str, antigo: str) -> None:
    """Troca todo o texto da forma por um parágrafo só (formatação do primeiro run)."""
    if " ".join(sh.text_frame.text.split()) != " ".join(antigo.split()):
        raise SystemExit(f"ERRO: texto antigo não confere em {sh.name!r}: {sh.text_frame.text!r}")
    for p in sh.text_frame.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    trocar_paragrafo(sh, novo, 0)


def remover(sh) -> None:
    sh._element.getparent().remove(sh._element)


def rodape(slide, secao: str | None) -> None:
    """Refaz a navegação do rodapé com as seções do deck final, a corrente em negrito verde."""
    alvo = [sh for sh in formas(slide.shapes) if sh.has_text_frame and "|" in sh.text_frame.text
            and sh.text_frame.text.startswith(("Motivação", "Hipótese"))]
    alvo += [sh for sh in formas(slide.shapes) if sh.has_text_frame and sh.text_frame.text.startswith("Motivação  I ")]
    if not alvo:
        return
    if len(alvo) != 1:
        raise SystemExit(f"ERRO: mais de um rodapé de navegação: {[s.name for s in alvo]}")
    sh = alvo[0]
    sh.left, sh.width = Inches(0.22), Inches(12.2)
    p = sh.text_frame.paragraphs[0]._p
    modelo = p.find("a:r/a:rPr", NS)
    for r in p.findall("a:r", NS):
        p.remove(r)
    end = p.find("a:endParaRPr", NS)

    def run(texto: str, destaque: bool):
        r = etree.Element("{%s}r" % NS["a"])
        rpr = copy.deepcopy(modelo)
        rpr.attrib.pop("b", None)
        rpr.set("sz", "1000")
        for f in rpr.findall("a:solidFill", NS):
            rpr.remove(f)
        if destaque:
            rpr.set("b", "1")
            sf = etree.Element("{%s}solidFill" % NS["a"])
            etree.SubElement(sf, "{%s}srgbClr" % NS["a"]).set("val", "114719")
            rpr.insert(0, sf)
        r.append(rpr)
        etree.SubElement(r, "{%s}t" % NS["a"]).text = texto
        if end is not None:
            end.addprevious(r)
        else:
            p.append(r)

    for k, s in enumerate(SECOES):
        run(s, s == secao)
        if k < len(SECOES) - 1:
            run("  |  ", False)


def numerar(slide, n: int) -> None:
    """Número digitado à mão no canto inferior direito: passa a ser a posição no deck final."""
    for sh in formas(slide.shapes):
        if (sh.has_text_frame and sh.text_frame.text.strip().isdigit() and sh.left is not None
                and sh.left > Inches(12) and sh.top > Inches(6.8)):
            trocar_paragrafo(sh, str(n), 0)


def notas(slide, texto: str) -> None:
    slide.notes_slide.notes_text_frame.text = texto


# --------------------------------------------------------------------------------------------------------------
def adaptar_grupo(prs) -> list[str]:
    s = prs.slides
    feitas = []

    # Capa: o título vira a pergunta (doc 12 da banca 2, §1.3)
    capa = por_texto(s[0], "Remuneração como incentivo limitado:", inicio=True)
    antigos = ("Remuneração como incentivo limitado:", "um modelo de escolha racional para o",
               "Programa Mais Médicos Especialistas")
    for k, (velho, novo) in enumerate(zip(antigos, TITULO_CAPA)):
        trocar_paragrafo(capa, novo, k, antigo=velho)
    feitas.append("capa: título pela pergunta, como no deck pós-banca")

    # Slide 3: gráficos do grupo sem fonte reproduzível (P6, P7) -> figuras do pipeline da banca 1
    sl = s[2]
    from PIL import Image
    for nome, fig in (("Chart 14", FIG_UF), ("Chart 11", FIG_VAGAS)):
        ch = por_nome(sl, nome)
        x, y, h = ch.left, ch.top, ch.height
        remover(ch)
        w_px, h_px = Image.open(fig).size
        sl.shapes.add_picture(str(fig), x, y, height=h, width=int(h * w_px / h_px))
    trocar_paragrafo(por_texto(sl, "Médicos especialistas por 100 mil habitantes, por UF – 2024"), SUB2_UF)
    trocar_paragrafo(por_texto(sl, "II. Serviços especializados exigem longos deslocamentos"), SUB_VAGAS)
    trocar_paragrafo(por_texto(sl, "Deslocamento médio da população para serviços de alta complexidade"), SUB2_VAGAS)
    f = por_texto(sl, "Fontes: Medicina S/A", inicio=True)
    trocar_forma(f, FONTES_ESCASSEZ, f.text_frame.text)
    notas(sl, NOTAS[3])
    feitas.append("slide 3: figuras do pipeline (UFs com valor citado; vagas do ciclo 1 por região)")

    # Slide 28: a soma das três variáveis decide a escolha, não o preenchimento
    c = por_nome(s[16], "cText")
    trocar_forma(c, CTEXT_UTILIDADE, c.text_frame.text)
    feitas.append("slide 17: 'decide qual vaga o médico escolhe'")

    # Slide 29: a cadeia até o preenchimento é do modelo, não a hipótese testada
    trocar_paragrafo(por_nome(s[17], "hyplab"), ROTULO_CADEIA, 0, antigo="HIPÓTESE")
    feitas.append("slide 18: rótulo 'CADEIA DO MODELO' no lugar de 'HIPÓTESE'")

    # Slide 20: a referência "slide 11" era a numeração da banca 1; no deck final, a equação vem no slide anterior
    c = por_nome(s[19], "cText")
    r0 = c.text_frame.paragraphs[0].runs[0]
    if r0.text.strip() != "Adições ao modelo do slide 11:":
        raise SystemExit(f"ERRO: texto antigo não confere no slide 20: {r0.text!r}")
    r0.text = ADICOES + "  "
    feitas.append("slide 20: 'Adições ao modelo do slide anterior' (a numeração mudou)")

    # Slide 35: grafia (errata E8)
    t = por_texto(s[34], "Vulnerabilidade social: fragilidades", inicio=True)
    achou = False
    for p in t.text_frame.paragraphs:
        for r in p.runs:
            if "trasnporte" in r.text:
                r.text = r.text.replace("trasnporte", "transporte")
                achou = True
    if not achou:
        raise SystemExit("ERRO: 'trasnporte' não encontrado no slide 35")
    feitas.append("slide 35: 'transporte' (errata E8)")
    return feitas


def _renomear_grafico(part, sufixo: str, vistos: set) -> None:
    """Dá nomes únicos às partes do gráfico copiado (e às que ele usa), para não colidir no pacote de destino."""
    if id(part) in vistos:
        return
    vistos.add(id(part))
    nome = str(part.partname)
    pasta, arq = nome.rsplit("/", 1)
    part.partname = PackURI(f"{pasta}/final_{sufixo}_{arq}")
    for rel in part.rels.values():
        if not rel.is_external:
            _renomear_grafico(rel.target_part, sufixo, vistos)


def _estilo_do_layout(sp, layout) -> None:
    """Placeholder copiado: leva junto a posição e o estilo do layout de origem (o layout de destino é outro)."""
    ph = sp.find(".//p:nvPr/p:ph", NS)
    if ph is None:
        return
    idx, tipo = ph.get("idx"), ph.get("type")
    fonte = None
    for lp in layout.placeholders:
        lph = lp._element.find(".//p:nvPr/p:ph", NS)
        if (idx is not None and lph.get("idx") == idx) or (tipo is not None and lph.get("type") == tipo):
            fonte = lp._element
            break
    if fonte is None:
        return
    sppr, sppr_l = sp.find("p:spPr", NS), fonte.find("p:spPr", NS)
    if sppr is not None and sppr.find("a:xfrm", NS) is None and sppr_l.find("a:xfrm", NS) is not None:
        sppr.insert(0, copy.deepcopy(sppr_l.find("a:xfrm", NS)))
    tx, tx_l = sp.find("p:txBody", NS), fonte.find("p:txBody", NS)
    if tx is not None and tx_l is not None:
        ls, ls_l = tx.find("a:lstStyle", NS), tx_l.find("a:lstStyle", NS)
        if ls is not None and len(ls) == 0 and ls_l is not None:
            tx.replace(ls, copy.deepcopy(ls_l))


def copiar_slide(origem, destino_prs, layout, sufixo: str):
    novo = destino_prs.slides.add_slide(layout)
    for sh in list(novo.shapes):
        remover(sh)
    arvore = novo.shapes._spTree
    vistos: set = set()
    for el in origem.shapes._spTree:
        if el.tag.endswith(("}nvGrpSpPr", "}grpSpPr", "}extLst")):
            continue
        el2 = copy.deepcopy(el)
        for no in el2.iter():
            for att, val in list(no.attrib.items()):
                if not att.startswith("{%s}" % NS["r"]):
                    continue
                if att == QN_EMBED and no.tag == "{%s}blip" % NS["a"]:
                    img = origem.part.related_part(val)
                    _, rid = novo.part.get_or_add_image_part(io.BytesIO(img.blob))
                    no.set(att, rid)
                elif att == QN_RID and no.tag == "{%s}chart" % NS["c"]:
                    graf = origem.part.related_part(val)
                    _renomear_grafico(graf, sufixo, vistos)
                    no.set(att, novo.part.relate_to(graf, RT.CHART))
                else:
                    raise SystemExit(f"ERRO: relação não tratada ao copiar slide: {no.tag} {att}")
        if el2.tag == "{%s}sp" % NS["p"]:
            _estilo_do_layout(el2, origem.slide_layout)
        arvore.append(el2)
    if origem.has_notes_slide:
        notas(novo, origem.notes_slide.notes_text_frame.text)
    return novo


# --------------------------------------------------------------------------------------------------------------
# Slides novos do método passo a passo
# --------------------------------------------------------------------------------------------------------------
VERDE, TEXTO, CLARO, BORDA, CINZA, BRANCO = "114719", "1A1A1A", "EEF3ED", "DDE3DE", "5E6660", "FFFFFF"


def _virgula(x: float, casas: int) -> str:
    return f"{x:.{casas}f}".replace(".", ",")


def pesos_vl1() -> dict:
    """Pesos do VL-1 (ciclos 1–3) lidos de output/; as contas do exemplo saem daqui."""
    import math
    import pandas as pd
    d = pd.read_csv(VL_EST)
    coef = d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "coeficiente")].set_index("termo")
    b, dist = float(coef.loc["bolsa_mil", "estimativa"]), float(coef.loc["distancia_100km", "estimativa"])
    n_cand = int(coef.loc["bolsa_mil", "n_candidatos"])
    n_lin = int(coef.loc["bolsa_mil", "n_linhas_candidato_celula"])
    rc = math.exp(5 * b)
    km = 5 * b / -dist * 100
    pont = [b * bolsa + dist * km_v / 100 for _, bolsa, km_v in VAGAS_M2]
    ex = [math.exp(u) for u in pont]
    prob = [e / sum(ex) for e in ex]
    rc_vl = d[(d.chave_modelo == "VL1_emp") & (d.tipo_linha == "razao_chances_por_5mil")]["estimativa"].iloc[0]
    if abs(rc - rc_vl) > 1e-6:
        raise SystemExit(f"ERRO: e^(5β) = {rc} não reproduz a razão de chances gravada ({rc_vl})")
    return {"b": b, "dist": dist, "rc": rc, "km": km, "pont": pont, "prob": prob, "n_cand": n_cand,
            "n_lin": n_lin, "cardapio": round(n_lin / n_cand)}


def _caixa(sl, x, y, w, h, paragrafos, fill=None, line=None, anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT,
           forma=MSO_SHAPE.ROUNDED_RECTANGLE, nome="Caixa"):
    """paragrafos: lista de listas de (texto, tamanho, negrito, cor)."""
    sh = sl.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name = nome
    if forma == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = 0.06
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
    for lado in ("margin_left", "margin_right"):
        setattr(tf, lado, Inches(0.14))
    for lado in ("margin_top", "margin_bottom"):
        setattr(tf, lado, Inches(0.06))
    for k, par in enumerate(paragrafos):
        p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
        p.alignment = align
        for texto, tam, negrito, cor in par:
            r = p.add_run()
            r.text = texto
            r.font.size = Pt(tam)
            r.font.bold = negrito
            r.font.name = "Montserrat"
            r.font.color.rgb = RGBColor.from_string(cor)
    return sh


def _slide_base(prs, layout, titulo: str, modelo_rodape):
    sl = prs.slides.add_slide(layout)
    for sh in list(sl.shapes):
        if not (sh.is_placeholder and "TITLE" in str(sh.placeholder_format.type)):
            remover(sh)
    if sl.shapes.title is None:
        raise SystemExit("ERRO: o layout do grupo não tem título")
    sl.shapes.title.text = titulo
    sl.shapes._spTree.append(copy.deepcopy(modelo_rodape._element))
    _caixa(sl, 12.55, 7.06, 0.7, 0.36, [[("0", 14, True, "BFBFBF")]], forma=MSO_SHAPE.RECTANGLE,
           align=PP_ALIGN.RIGHT, nome="Número da página")
    return sl


def _fontes(sl, texto: str) -> None:
    _caixa(sl, 0.2, 6.92, 12.3, 0.28, [[(texto, 8, False, CINZA)]], forma=MSO_SHAPE.RECTANGLE, nome="Fontes")


def _cabecalho(sl, x, y, w, titulo: str, sub: str) -> None:
    """Cabeçalho no estilo do grupo: "I. Título" em negrito e subtítulo cinza pequeno."""
    _caixa(sl, x, y, w, 0.34, [[(titulo, 15, True, TEXTO)]], forma=MSO_SHAPE.RECTANGLE, nome="Cabeçalho")
    _caixa(sl, x, y + 0.34, w, 0.28, [[(sub, 9, False, CINZA)]], forma=MSO_SHAPE.RECTANGLE, nome="Subtítulo")


def _linha(sl, x, y, w, h, rotulo: str, texto: str, num: int) -> None:
    """Linha no estilo do grupo: barra verde à esquerda, rótulo em negrito, texto curto."""
    barra = sl.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y + 0.12), Inches(0.07), Inches(h - 0.24))
    barra.fill.solid()
    barra.fill.fore_color.rgb = RGBColor.from_string(VERDE)
    barra.line.fill.background()
    barra.name = "Barra"
    _caixa(sl, x + 0.18, y, 2.3, h, [[(f"{num}  ", 16, True, "A8C8A3"), (rotulo, 16, True, TEXTO)]],
           forma=MSO_SHAPE.RECTANGLE, nome=f"Passo {num}")
    _caixa(sl, x + 2.5, y, w - 2.5, h, [[(texto, 15, False, TEXTO)]], forma=MSO_SHAPE.RECTANGLE,
           nome=f"Passo {num} texto")
    sep = sl.shapes.add_connector(1, Inches(x), Inches(y + h), Inches(x + w), Inches(y + h))
    sep.line.color.rgb = RGBColor.from_string(BORDA)
    sep.name = "Separador"


def _numero(sl, x, y, w, h, rotulo: str, grande: str, texto: str, nome: str, fill=VERDE) -> None:
    """Caixa escura com número grande, como a "Amostra do modelo" do grupo."""
    _caixa(sl, x, y, w, h, [[(rotulo, 11, True, "A8C8A3")], [(grande, 36, True, BRANCO)], [(texto, 13, False, BRANCO)]],
           fill=fill, forma=MSO_SHAPE.RECTANGLE, nome=nome)


def slides_metodo(prs, layout, modelo_rodape) -> list:
    v = pesos_vl1()
    car = str(v["cardapio"])
    # ---- 1: o método em quatro passos
    s1 = _slide_base(prs, layout, TITULO_M1, modelo_rodape)
    _cabecalho(s1, 0.3, 0.95, 7.4, *SUB_M1)
    for k, (rot, txt) in enumerate(PASSOS_M1):
        _linha(s1, 0.3, 1.75 + k * 1.05, 7.4, 1.05, rot, txt.format(cardapio=car), k + 1)
    _cabecalho(s1, 8.25, 0.95, 4.8, *SUB2_M1)
    r, g, tx = CAIXA_M1
    _numero(s1, 8.25, 1.75, 4.8, 2.3, r, g.format(b=_virgula(v["b"], 3)), tx, "Peso da bolsa")
    c1, c2 = CONDICIONAL_M1
    _caixa(s1, 8.25, 4.25, 4.8, 1.7, [[(c1 + " ", 15, True, VERDE), (c2, 15, False, TEXTO)]],
           fill=CLARO, forma=MSO_SHAPE.RECTANGLE, nome="Condicional")
    _fontes(s1, FONTES_M1.format(cand=f"{v['n_cand']:,}".replace(",", "."), linhas=f"{v['n_lin']:,}".replace(",", ".")))
    notas(s1, NOTAS_M[1])
    # ---- 2: exemplo com três vagas
    s2 = _slide_base(prs, layout, TITULO_M2, modelo_rodape)
    _cabecalho(s2, 0.3, 0.95, 7.4, *SUB_M2)
    tab = s2.shapes.add_table(len(VAGAS_M2) + 1, 4, Inches(0.3), Inches(1.75), Inches(7.4), Inches(3.4)).table
    cab = ("Vaga", "Bolsa", "Distância", "Chance de ser a 1ª opção")
    for j, wj in enumerate((1.1, 1.7, 1.7, 2.9)):
        tab.columns[j].width = Inches(wj)
    corpo = [[n, f"R$ {bolsa} mil", f"{km} km", _virgula(100 * pr, 1) + "%"]
             for (n, bolsa, km), pr in zip(VAGAS_M2, v["prob"])]
    for i_, linha in enumerate([cab] + corpo):
        for j, txt in enumerate(linha):
            c = tab.cell(i_, j)
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor.from_string(VERDE if i_ == 0 else (CLARO if i_ % 2 else BRANCO))
            c.text = txt
            rr = c.text_frame.paragraphs[0].runs[0]
            rr.font.size = Pt(14 if i_ == 0 else 20)
            rr.font.bold = i_ == 0 or j in (0, 3)
            rr.font.name = "Montserrat"
            rr.font.color.rgb = RGBColor.from_string(BRANCO if i_ == 0 else (VERDE if j == 3 else TEXTO))
            c.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
    _cabecalho(s2, 8.25, 0.95, 4.8, *SUB2_M2)
    rc, km = _virgula(v["rc"], 2), str(round(v["km"]))
    for k, (rot, grande, txt) in enumerate(CAIXAS_M2):
        _numero(s2, 8.25, 1.75 + k * 1.8, 4.8, 1.62, rot, grande.format(rc=rc, km=km), txt, rot.title())
    _fontes(s2, FONTES_M2)
    notas(s2, NOTAS_M[2])
    return [s1, s2], v

def construir(saida: Path) -> dict:
    if sha256(ENT_GRUPO) != SHA_GRUPO:
        raise SystemExit("ERRO: o deck do grupo não é o guardado em 09/11/2026 (SHA-256 diferente)")
    prs = Presentation(str(ENT_GRUPO))
    pb = Presentation(str(ENT_PB))
    diag = Presentation(str(ENT_DIAG))
    if len(prs.slides) != N_GRUPO or len(pb.slides) != 14:
        raise SystemExit(f"ERRO: esperava {N_GRUPO} slides no deck do grupo e 14 no pós-banca; "
                         f"vieram {len(prs.slides)} e {len(pb.slides)}")
    usados_g = {n for o, n, _ in ORDEM if o == "G"}
    usados_pb = {n for o, n, _ in ORDEM if o == "PB"}
    if usados_g | set(FORA_G) != set(range(1, N_GRUPO + 1)) or usados_g & set(FORA_G):
        raise SystemExit(f"ERRO: ORDEM e FORA_G precisam cobrir os {N_GRUPO} slides do grupo, sem repetição")
    if usados_pb | set(FORA_PB) != set(range(1, 15)) or usados_pb & set(FORA_PB):
        raise SystemExit("ERRO: ORDEM e FORA_PB precisam cobrir os 14 slides do pós-banca, sem repetição")
    feitas = adaptar_grupo(prs)
    # Diagrama da teoria da mudança: "origem" sai da tela (doc 12, §1.2); a nota diz qual elo a hipótese testa
    sd = diag.slides[N_DIAG_SLIDE - 1]
    trocar_paragrafo(por_nome(sd, "A_no_A4"), A4_DIAGRAMA, 2,
                     antigo="Moradia, deslocamento, amenidades e distância da origem.")
    notas(sd, NOTAS[16])
    feitas.append("diagrama da teoria: 'distância de casa' no lugar de 'distância da origem'")
    layout = prs.slides[2].slide_layout
    if layout.name != "1_Title Slide" or sd.slide_layout.name != "1_Title Slide":
        raise SystemExit(f"ERRO: layout inesperado {layout.name!r}")
    ids_grupo = list(prs.slides._sldIdLst)
    ids_novos = {}
    copiar_slide(sd, prs, layout, "diag")
    ids_novos[("D", N_DIAG_SLIDE)] = prs.slides._sldIdLst[-1]
    for n in sorted(usados_pb):
        copiar_slide(pb.slides[n - 1], prs, layout, f"pb{n}")
        ids_novos[("PB", n)] = prs.slides._sldIdLst[-1]
    modelo_rodape = next(sh for sh in prs.slides[2].shapes if sh.has_text_frame
                         and sh.text_frame.text.startswith("Motivação") and "|" in sh.text_frame.text)
    novos_m, pesos = slides_metodo(prs, layout, modelo_rodape)
    for k in range(len(novos_m)):
        ids_novos[("M", k + 1)] = prs.slides._sldIdLst[len(prs.slides._sldIdLst) - len(novos_m) + k]
    feitas.append("slides novos do método passo a passo (4 passos; exemplo com três vagas e os pesos do VL-1)")
    lista = prs.slides._sldIdLst
    for el in list(lista):
        lista.remove(el)
    for o, n, _ in ORDEM:
        lista.append(ids_grupo[n - 1] if o == "G" else ids_novos[(o, n)])
    for n in FORA_G:
        prs.part.drop_rel(ids_grupo[n - 1].get(QN_RID))
    ordem_saida = []
    for pos, (o, n, secao) in enumerate(ORDEM, start=1):
        sl = prs.slides[pos - 1]
        sl._element.attrib.pop("show", None)
        rodape(sl, secao)
        numerar(sl, pos)
        titulo = next((" ".join(sh.text_frame.text.split()) for sh in formas(sl.shapes)
                       if sh.has_text_frame and sh.is_placeholder
                       and "TITLE" in str(sh.placeholder_format.type)), "")
        ordem_saida.append({"posicao": pos, "origem": f"{ORIGENS[o]} {n}",
                            "secao": secao, "titulo": titulo})
    saida.mkdir(parents=True, exist_ok=True)
    prs.save(str(saida / ARQ_DECK))
    return {"ordem": ordem_saida, "adaptacoes": feitas,
            "exemplo_metodo": {"peso_bolsa_por_mil": pesos["b"], "peso_distancia_por_100km": pesos["dist"],
                               "e_5beta": pesos["rc"], "km_equivalentes": pesos["km"],
                               "chances_ilustrativas_A_B_C": pesos["prob"],
                               "natureza": "ILUSTRATIVO: vagas inventadas; pesos estimados (VL-1)"}}


def converter_pdf(pptx: Path, pdf: Path) -> bool:
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, str(pptx)],
                           capture_output=True, text=True, timeout=600)
        gerado = Path(tmp) / (pptx.stem + ".pdf")
        if r.returncode != 0 or not gerado.exists():
            print("aviso: PDF não gerado:", r.stderr[-500:], file=sys.stderr)
            return False
        pdf.write_bytes(gerado.read_bytes())
    return True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sem-pdf", action="store_true")
    a = ap.parse_args(argv)
    resumo = construir(SAIDA)
    com_pdf = not a.sem_pdf and converter_pdf(SAIDA / ARQ_DECK, SAIDA / ARQ_PDF)
    entradas = [{"caminho": p.relative_to(ROOT).as_posix(), "sha256": sha256(p)}
                for p in (ENT_GRUPO, ENT_DIAG, ENT_PB, FIG_UF, FIG_VAGAS)]
    saidas = [{"caminho": (SAIDA / n).relative_to(ROOT).as_posix(), "sha256": sha256(SAIDA / n)}
              for n in (ARQ_DECK, ARQ_PDF) if (SAIDA / n).exists() and (n != ARQ_PDF or com_pdf)]
    man = {
        "script": "scripts/apresentacao/gerar_deck_banca_final.py",
        "conteudo_canonico": DOC,
        "natureza_dos_dados": "EMPIRICO",
        "observacao": "slides da banca 2 com números de output/; parte da banca 1 é teoria; nada estimado aqui",
        "regra": "lê só de output/; slides da banca 2 pós-banca copiados sem mudar texto; slides do grupo com as "
                 "trocas listadas em 'adaptacoes', cada uma conferida contra o texto antigo",
        "nota_pdf": "o PDF é renderizado pelo LibreOffice e não é byte a byte determinístico",
        "entradas": entradas,
        "saidas": saidas,
        "slides_do_grupo_fora": {str(k): v for k, v in sorted(FORA_G.items())},
        "slides_do_pos_banca_fora": {str(k): v for k, v in sorted(FORA_PB.items())},
        **resumo,
    }
    (SAIDA / ARQ_MANIF).write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for s in saidas:
        print(s["caminho"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
