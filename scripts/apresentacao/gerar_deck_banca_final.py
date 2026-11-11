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
    ("PB", 2, "Motivação"),          # a bolsa por faixa de IVS e a pergunta
    ("D", N_DIAG_SLIDE, "Literatura"),  # diagrama A: teoria da mudança
    ("PB", 3, "Hipótese"),
    ("PB", 4, "Dados"),
    ("PB", 5, "Análise Descritiva"),
    ("M", 1, "Metodologia"),         # novo: o método passo a passo
    ("M", 2, "Metodologia"),         # novo: exemplo com três vagas e os pesos do VL-1
    ("PB", 8, "Identificação"),
    ("PB", 9, "Resultados"),
    ("PB", 10, "Robustez"),
    ("PB", 11, "Discussão"),
    ("PB", 12, "Discussão"),
    ("G", 31, None),                 # Q&A
    ("G", 32, None),                 # divisor Apêndice
    ("PB", 14, None),                # A1: a bolsa segue exatamente o IVS
    ("PB", 6, None),                 # equação do modelo (sai do corpo: o passo a passo e o exemplo explicam)
    ("PB", 7, None),                 # Bobba et al. (reserva para pergunta da banca)
    ("G", 16, None),                 # três elementos da teoria
    ("G", 17, None),                 # escolha locacional maximiza a utilidade
    ("G", 20, None),                 # custo geográfico e laboral
    ("G", 18, None),                 # da escolha individual ao agregado
    ("G", 35, None),                 # o IVS
]
SUMARIO = "sumário do grupo: sai pelo pedido 'menos slides' (doc 12 da banca 2, §1.2); a navegação do rodapé fica"
# Slides do deck do grupo que saem, com o motivo (vão para o manifesto e para o doc 02)
FORA_G = {
    3: "escassez de especialistas: a motivação fica no slide da bolsa (notícias, regra e pergunta); pedido do autor de "
       "11/11/2026, 'slides demais'",
    19: "renda real líquida: repete o slide da utilidade (mesma equação); pedido do autor de 11/11/2026",
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
SUB2_UF = "Especialistas por 100 mil hab., as duas maiores e as duas menores UFs, dez/2024"
SUB_VAGAS = "II. O ciclo 1 do PMM-E abriu vagas nas cinco regiões"
SUB2_VAGAS = "Células estabelecimento × curso e vagas imediatas, ciclo 1, 1ª chamada"
FONTES_ESCASSEZ = ("Fontes: Medicina S/A; Amado Mundo; Agência Câmara; Scheffer et al., Demografia Médica no Brasil "
                   "2025 (FMUSP/AMB), só as UFs com valor citado; quadro de vagas do Edital SGTES/MS nº 3/2025.")
A4_DIAGRAMA = "Moradia, deslocamento, amenidades e distância de casa."
CTEXT_UTILIDADE = ("A política mexe em apenas uma variável: eleva E(w|B) pela bolsa (B). Preços e custo do local "
                   "continuam contra, e é o saldo das três variáveis que decide qual vaga o médico escolhe.")
ROTULO_CADEIA = "CADEIA DO MODELO"
ADICOES = "Adições ao modelo do slide anterior:"
A_NOTA_DIAGRAMA = "Diagrama teórico: testamos só o elo da remuneração (bolsa → valor da vaga → 1ª opção)."
PREMISSA_LISTA = "supomos que viu todas as vagas do curso e listou sem estratégia"
NOTA_LISTA = ("Lista sincera (decisão do autor de 11/11/2026; premissa no slide de Identificação): a 1ª opção só é a vaga "
              "preferida se o médico listou as vagas pela preferência, sem estratégia (por exemplo, pôr em 1º onde acha "
              "que passa). Se houver estratégia, o ×1,47 mistura preferência e chance de ser alocado.")

# ---- Slides novos do método (pedido do autor, 09/11/2026: a banca não entendeu o método e nunca tinha ouvido falar) --
VL_EST = ROOT / "output/rdd_bolsa/VL_estimativas.csv"
TITULO_M1 = "Método passo a passo: logit condicional"
SUB_M1 = ("I. Como o modelo lê cada escolha", "McFadden (1974), Nobel de 2000; o mesmo modelo de Bobba et al. (2026)")
PASSOS_M1 = (
    ("Cardápio", "todas as vagas do curso no ciclo (≈ {cardapio})"),
    ("Escolha", "1ª opção = 1; as outras = 0"),
    ("Pontuação", "β·bolsa + γ·distância + par de UFs"),
    ("Chance", "e^pontuação ÷ soma do cardápio"),
)
SUB2_M1 = ("II. O que sai", "os pesos que melhor explicam as escolhas observadas")
CAIXA_M1 = ("PESO DA BOLSA", "β = {b}", "por R$ 1 mil/mês")
CONDICIONAL_M1 = ("Condicional:", "só compara vagas do mesmo médico")
FONTES_M1 = ("Fontes: McFadden (1974); Bobba et al. (NBER WP 29068, rev. jan. 2026); "
             "output/rdd_bolsa/VL_estimativas.csv (VL-1, adendo 52e): {cand} candidatos, {linhas} linhas.")
TITULO_M2 = "Exemplo: um candidato, três vagas"
SUB_M2 = ("I. Mesmo curso, mesma UF (MG)", "ilustrativo: vagas inventadas, pesos estimados")
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
            if sh.width < Inches(0.5):
                direita = sh.left + sh.width
                sh.width = Inches(0.5)
                sh.left = direita - sh.width


def notas(slide, texto: str) -> None:
    slide.notes_slide.notes_text_frame.text = texto


# --------------------------------------------------------------------------------------------------------------

# --------------------------------------------------------------------------------------------------------------
# Correções do modelo teórico (revisão de 11/11/2026 contra docs/02_teoria/modelo_micro.md; doc 02, §3.1)
# --------------------------------------------------------------------------------------------------------------
QN_MT = "{http://schemas.openxmlformats.org/officeDocument/2006/math}t"

# (slide do grupo, nome da forma, texto inteiro da forma, parágrafo, run, texto antigo do run, texto novo do run)
TROCAS_TEORIA = (
    (16, "txt219", None, 0, 2,
     "composto pela desutilidade do atendimento (equipe e do capital instalado) e pela desutilidade da vida no local "
     "(amenidades, segurança e distância da família)",
     "composto pela desutilidade do atendimento (equipe e capital instalado) e pela desutilidade da vida no local "
     "(amenidades, segurança e distância de casa)"),
    (17, "eqlab", None, 0, 0, "MOEHLING et al. (2020), EQ. 1, P. 184", "ADAPTADO DE MOEHLING et al. (2020), EQ. 1, P. 184"),
    (17, "eqleg", None, 0, 3, ": Local escolhido por r  ·  ", ": vaga escolhida por r (a 1ª opção)  ·  "),
    (17, "eqleg", None, 0, 6, ": ofertas disponíveis a r  ·  ", ": ofertas disponíveis a r (o cardápio)  ·  "),
    (17, "dvar0", "Salário : E(wmt)", 0, 3, ")", " | B)"),
    (17, "deqbox0", "Segurança, deslocamento etc Nível de amenidades da cidade", 0, 0, "Segurança, deslocamento ",
     "Moradia e custo de vida"),
    (17, "deqbox0", "Moradia e custo de vidaetc Nível de amenidades da cidade", 0, 1, "etc", ""),
    (17, "deqbox0", "Moradia e custo de vida Nível de amenidades da cidade", 1, 0, "Nível de amenidades da cidade",
     "Nível de preços da cidade"),
    (17, "dvar0", "Custo laboral : crmt(s)", 0, 0, "Custo laboral : ", "Custo não pecuniário : "),
    (17, "deqbox0", "Esforço para atender Aumenta com equipe e equipamentos ruins", 0, 0, "Esforço para atender",
     "Esforço e vida no local"),
    (17, "deqbox0", "Esforço e vida no local Aumenta com equipe e equipamentos ruins", 1, 0,
     "Aumenta com equipe e equipamentos ruins", "Equipe ruim, poucas amenidades, longe de casa"),
    (17, "dtxt0", "Custo não monetário de exercer ali; o altruísmo do médico (α) compensa em parte.", 0, 0,
     "Custo não monetário de exercer ali; o altruísmo do médico (α) compensa em parte.",
     "Custo não monetário de viver e exercer ali."),
    (17, "dsrc0", "CHONÉ & MA (2011)", 0, 0, "CHONÉ & MA (2011)", "CHONÉ & MA (2011) · R&RH (2017)"),
    (18, "rd1", None, 0, 0, "Especialidade, vínculos e preferências variam: π", "Curso, vínculos e preferências variam: π"),
    (18, "rd0", None, 0, 5, ".", ": na inscrição, a 1ª opção."),
    (19, "chip0_0", "i: localidades candidatas", 0, 0, "i", "m"),
    (19, "chip0_0", "𝔼 (wit(s)): salário esperado em i, no ano t, na especialidade s", 0, 2, "it", "mt"),
    (19, "chip0_0", "𝔼 (wmt(s)): salário esperado em i, no ano t, na especialidade s", 0, 6,
     "salário esperado em i, no ano t, na especialidade s", "salário esperado em m, no ano t, na especialidade s"),
    (19, "chip0_0", "Pit: nível de preços da localidade (deflator)", 0, 0, "P", "p"),
    (19, "chip0_0", "pit: nível de preços da localidade (deflator)", 0, 1, "it", "mt"),
    (19, "chip0_0", "cit(s): custo não pecuniário de viver ali", 0, 1, "it", "mt"),
    (19, "chip0_0", "cmt(s): custo não pecuniário de viver ali", 0, 5, "custo não pecuniário de viver ali",
     "custo não pecuniário de viver e trabalhar ali"),
    (19, "col2", None, 0, 0,
     "O médico ganha com o salário esperado na localidade, ajustado pelo custo de vida. Perde com o custo não "
     "pecuniário de exercer a profissão naquele local",
     "O médico ganha com o salário esperado na localidade, ajustado pelo custo de vida. Perde com o custo não "
     "pecuniário de viver e exercer a profissão naquele local"),
    (19, "col2", None, 0, 3, "A escolha recai sobre aquela que oferece o maior valor presente da renda real líquida",
     "A escolha recai sobre aquela que oferece o maior valor presente da renda real líquida."),
    (20, "pill0", None, 0, 1, "REDDING & ROSSI, 2017)", "REDDING & ROSSI-HANSBERG, 2017)"),
    (20, "impact0", None, 0, 2, "it", "mt"),
    (20, "impact0", None, 0, 4, " o deflator da localidade",
     " o deflator (moradia) e a parte geográfica de c (amenidades, distância)"),
    (20, "impact1", None, 0, 2, "it", "mt"),
    (20, "impact1", None, 0, 4, "o custo não pecuniário de exercer ali", "a parte laboral de c: o custo de exercer ali"),
    (20, "chip1_1", None, 0, 0, "Q ", "q "),
    # decisão do autor (11/11/2026): o altruísmo não aparece mais como equação
    (20, "chip1_3", None, 0, 0, "B(q) ", "L, K "),
    (20, "chip1_3", None, 0, 2, " benefício ao paciente", " equipe e capital"),
    (20, "frase1", None, 0, 11, "esforço cai quando há mais equipe (L) e capital (K), ",
     "esforço cai quando há mais equipe (L) e capital (K). "),
    (20, "frase1", None, 0, 12, "e valoriza o benefício ao paciente na medida do seu altruísmo (α). ", ""),
    # decisão do autor (11/11/2026): testamos o elo da remuneração
    (18, "note", None, 1, 3, " comum entre médicos; é simplificação teórica, não equação estimada.",
     " comum entre médicos; é simplificação teórica. Testamos só o elo da remuneração: B ↑ → V ↑ → π ↑ (a 1ª opção)."),
)
# Equações em OMML: (slide do grupo, nome da forma, sequência antiga de m:t, sequência nova)
TROCAS_OMML = (
    (19, "TextBox 1",
     ["𝐦𝐚𝐱", "𝒊", "∈", "𝑰", "𝒕", "𝜹", "𝒕", "𝔼", "𝒘", "𝒊𝒕", "𝒔", "𝒑", "𝒊𝒕", "−\xa0", "𝒄", "𝒊𝒕", "𝒔"],
     ["𝐚𝐫𝐠\xa0𝐦𝐚𝐱", "𝒎", "∈", "𝑰", "𝒕", "𝜹", "𝒕", "𝔼", "𝒘", "𝒎𝒕", "𝒔", "𝒑", "𝒎𝒕", "−\xa0", "𝒄", "𝒎𝒕", "𝒔"]),
    (19, "Retângulo: Cantos Arredondados 38", ["𝒊", "∗"], ["𝒎", "∗"]),
    (20, "TextBox 4",
     ["𝒖", "𝒏𝒊𝒐", "=", "𝒁", "𝒏𝒊𝒐", "𝑩", "𝒏", "𝑾", "𝒊", "𝒌", "𝒏𝒊", "𝑸", "𝒏", "𝟏", "−", "𝜷"],
     ["𝒖", "𝒏𝒊𝒐", "=", "𝒛", "𝒏𝒊𝒐", "𝑩", "𝒏", "𝒘", "𝒊", "𝜿", "𝒏𝒊", "𝑸", "𝒏", "𝟏", "−", "𝜷"]),
    (20, "TextBox 2",
     ["𝑼", "=", "𝑹", "−", "𝑪", "𝒒", ";", "𝑳", ",", "𝑲", "+", "𝜶", "𝑩", "(", "𝒒", ")"],
     ["𝑼", "=", "𝑹", "−", "𝑪", "𝒒", ";", "𝑳", ",", "𝑲", "", "", "", "", "", ""]),
)


def _forma_unica(slide, nome: str, texto: str | None):
    achadas = [sh for sh in formas(slide.shapes) if sh.name == nome and sh.has_text_frame
               and (texto is None or " ".join(sh.text_frame.text.split()) == " ".join(texto.split()))]
    if len(achadas) != 1:
        raise SystemExit(f"ERRO: esperava 1 forma {nome!r} com o texto {texto!r}; achei {len(achadas)}")
    return achadas[0]


def _formas_xml(slide, nome: str):
    """Formas pelo nome no XML (inclui as que estão dentro de mc:AlternateContent, que o python-pptx não vê)."""
    return [sp for sp in slide._element.iter("{%s}sp" % NS["p"])
            if sp.find(".//p:cNvPr", NS) is not None and sp.find(".//p:cNvPr", NS).get("name") == nome]


def adaptar_teoria(prs) -> list[str]:
    feitas = []
    for n, nome, texto, par, run, antigo, novo in TROCAS_TEORIA:
        sh = _forma_unica(prs.slides[n - 1], nome, texto)
        r = sh.text_frame.paragraphs[par].runs[run]
        if r.text != antigo:
            raise SystemExit(f"ERRO: slide {n}, {nome}: run {par}.{run} é {r.text!r}, esperava {antigo!r}")
        r.text = novo
    feitas.append(f"modelo teórico: {len(TROCAS_TEORIA)} trocas de texto (p é o custo de vida; c tem parte "
                  "geográfica e laboral; Rossi-Hansberg; 'curso'; a 1ª opção como o argmax do cardápio)")
    for n, nome, antigo, novo in TROCAS_OMML:
        sps = _formas_xml(prs.slides[n - 1], nome)
        alvo = [sp for sp in sps if [t.text for t in sp.iter(QN_MT)] == antigo]
        if len(alvo) != 1:
            raise SystemExit(f"ERRO: slide {n}, equação {nome!r}: esperava 1 com {antigo}; achei {len(alvo)}")
        for t_el, txt in zip(list(alvo[0].iter(QN_MT)), novo):
            t_el.text = txt
    feitas.append("equações: arg max e m (localidade) no slide da renda real líquida; z, w e κ em Redding & "
                  "Rossi-Hansberg, como no modelo_micro")
    return feitas



# Imagens de reserva das equações (mc:Fallback). O PowerPoint mostra o OMML corrigido; o LibreOffice (e o PDF)
# mostra a imagem de reserva, que vinha com a equação antiga. As novas são desenhadas aqui e gravadas em output/.
DIR_EQ = SAIDA / "equacoes"
FALLBACKS = (
    # (slide do grupo, nome da forma, arquivo, tipo, conteúdo)
    (20, "TextBox 2", "chone_ma.png", "eq",
     r"$\mathbfit{U} = \mathbfit{R} - \mathbfit{C}(\mathbfit{q};\,\mathbfit{L},\mathbfit{K})$"),
    (20, "TextBox 4", "redding_rossi_hansberg.png", "eq",
     r"$\mathbfit{u}_{\mathbfit{nio}} = \frac{\mathbfit{z}_{\mathbfit{nio}}\,\mathbfit{B}_{\mathbfit{n}}\,\mathbfit{w}_{\mathbfit{i}}}"
     r"{\mathbfit{\kappa}_{\mathbfit{ni}}\,\mathbfit{Q}_{\mathbfit{n}}^{\mathbf{1}-\mathbfit{\beta}}}$"),
)


def desenhar_fallback(arquivo: str, tipo: str, conteudo, cx: int, cy: int) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    matplotlib.rcParams.update({"mathtext.fontset": "stix", "font.family": "DejaVu Sans", "svg.hashsalt": "pmme",
                                "pdf.fonttype": 42})
    dpi = 200
    w_in, h_in = cx / 914400, cy / 914400
    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    if tipo == "eq":
        txt = ax.text(0.5, 0.5, conteudo, ha="center", va="center", fontsize=h_in * 72 * 0.36, color="black")
        # ajusta o tamanho para a equação ocupar a caixa (como a imagem original), sem distorcer
        fig.canvas.draw()
        caixa = txt.get_window_extent(renderer=fig.canvas.get_renderer())
        fator = min(0.94 * w_in * dpi / caixa.width, 0.82 * h_in * dpi / caixa.height)
        txt.set_fontsize(txt.get_fontsize() * fator)
    else:
        raio = 0.1 * h_in  # cantos arredondados como os do grupo, em polegadas
        ax.set_xlim(0, w_in)
        ax.set_ylim(0, h_in)
        ax.add_patch(FancyBboxPatch((0.02, 0.02), w_in - 0.04, h_in - 0.04,
                                    boxstyle=f"round,pad=0,rounding_size={raio}", facecolor="#056429",
                                    edgecolor="none"))
        rot, linhas = conteudo
        tam = h_in * 72 * 0.2
        ax.text(w_in / 2, h_in * 0.64, rot + " " + linhas[0], ha="center", va="center", fontsize=tam, color="white")
        ax.text(w_in / 2, h_in * 0.32, linhas[1], ha="center", va="center", fontsize=tam, color="white")
    DIR_EQ.mkdir(parents=True, exist_ok=True)
    destino = DIR_EQ / arquivo
    fig.savefig(destino, dpi=dpi, transparent=True, metadata={"Software": None})
    plt.close(fig)
    return destino


def trocar_fallbacks(prs) -> list[str]:
    feitas = []
    for n, nome, arquivo, tipo, conteudo in FALLBACKS:
        slide = prs.slides[n - 1]
        fb = [f for f in slide._element.iter("{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback")
              if f.find(".//p:cNvPr", NS) is not None and f.find(".//p:cNvPr", NS).get("name") == nome]
        if len(fb) != 1:
            raise SystemExit(f"ERRO: slide {n}: esperava 1 imagem de reserva para {nome!r}; achei {len(fb)}")
        blip = fb[0].find(".//a:blip", NS)
        ext = fb[0].find(".//a:xfrm/a:ext", NS)
        img = desenhar_fallback(arquivo, tipo, conteudo, int(ext.get("cx")), int(ext.get("cy")))
        _, rid = slide.part.get_or_add_image_part(str(img))
        blip.set(QN_EMBED, rid)
        feitas.append(f"slide {n}: imagem de reserva de {nome!r} redesenhada ({img.relative_to(ROOT).as_posix()})")
    return feitas


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


# --------------------------------------------------------------------------------------------------------------
# Enxugamento do texto (pedido do autor de 11/11/2026: "texto demais"; mensagem de cada slide no doc 02, §0.2).
# (título do slide, nome da forma, trecho de um run, texto novo). Texto novo None apaga o parágrafo do trecho.
# Cada trecho tem de estar em exatamente um run da forma; as cautelas obrigatórias ficam.
# --------------------------------------------------------------------------------------------------------------
T_ESC = "A escassez de especialistas já é tratada como urgência sanitária"
T_BOL = "A bolsa do PMM-E é maior onde o município é mais vulnerável"
T_DIA = "Da regra da bolsa à saúde: teoria da mudança"
T_HIP = "Hipótese: na mesma UF, a bolsa maior atrai a 1ª opção"
T_BAS = "Base: uma linha por candidato × vaga possível"
T_DES = "79% escolhem uma vaga na UF onde já trabalhavam"
T_MOD = "Modelo: logit condicional da 1ª opção"
T_BOB = "Por que este modelo: o desenho de Bobba et al. (2026)"
T_IDE = "Identificação: o que fica fixo e o que supomos"
T_RES = "Na mesma UF, +R$ 5 mil multiplicam a chance por 1,47"
T_ROB = "Robustez: sempre comparando vagas da mesma UF"
T_CON = "Conclusão: a bolsa maior aumenta a 1ª opção? Sim"
T_LIM = "Limitações e o que cada uma implica"
TROCAS_ENXUGAR = (
    (T_BOL, "Manchete", "Do total de profissionais, 72% serão destinados", None),
    (T_BOL, "Manchete", "1.480 especialistas do PMM-E em atividade hoje", None),
    (T_BOL, "TextBox 44", "I. A regra: a bolsa mensal cresce com o IVS do município da vaga", "I. A regra da bolsa"),
    (T_BOL, "TextBox 45", "IVS = Índice de Vulnerabilidade Social (Ipea, Censo 2010)",
     "pelo IVS 2010 (Ipea) do município da vaga"),
    (T_BOL, "TextBox 49", "O município não escolhe a bolsa: ela sai da regra.", "Regra do edital: o município não escolhe."),
    (T_BOL, "Rounded Rectangle 50",
     "Quando o médico escolhe entre as vagas do PMM-E, a bolsa maior faz uma vaga ser a sua 1ª opção?",
     "A bolsa maior faz a vaga ser a 1ª opção do médico?"),
    (T_DIA, "A_no_IVS", "Vulnerabilidade social do município.", None),
    (T_DIA, "A_no_faixa", "  ·  Cortes do IVS em 0,300 e 0,400.", ""),
    (T_DIA, "A_no_A3", "E(w | B) sobe com a faixa. Rende mais onde a vida é barata.", None),
    (T_DIA, "A_no_A4", "Moradia, deslocamento, amenidades e distância de casa.", None),
    (T_DIA, "A_no_A5", "Equipe, capital, esforço e altruísmo do médico.", None),
    (T_DIA, "A_no_A6", "   ·   Valor presente da renda real menos o custo do lugar.", ""),
    (T_DIA, "A_no_A7", "Médicos diferem em curso, vínculos e preferências.", None),
    (T_DIA, "A_no_A8", "Chance de a vaga receber ao menos um médico.", None),
    (T_DIA, "A_no_A9", "Vínculos e horas de especialistas.", None),
    (T_DIA, "A_no_A10", "Consultas, exames e cirurgias.", None),
    (T_DIA, "A_no_A11", "Espera e internações dos moradores.", None),
    (T_DIA, "A_grupo_G2", "ELOS DA POLÍTICA: DO PROVIMENTO À SAÚDE", "CADEIA DO PROGRAMA: NÃO ESTIMADA AQUI"),
    (T_HIP, "Rounded Rectangle 54", "vagas diferentes, para o mesmo médico, num mesmo momento",
     "duas vagas, o mesmo médico"),
    (T_HIP, "Rounded Rectangle 55", "razão de chances da 1ª opção por +R$ 5 mil: hipótese > 1", "razão de chances > 1"),
    (T_HIP, "Rounded Rectangle 56", "que mais médicos cheguem ao município: só a escolha de quem se inscreveu",
     "a ida ao município: só a vaga marcada"),
    (T_HIP, "Rectangle 57", "formulada depois de ver os dados: o resultado é exploratório. A bolsa muda junto com outras "
     "regras no mesmo corte de IVS (pacote).", "formulada depois de ver os dados (exploratória); no corte muda um pacote."),
    (T_BAS, "TextBox 45", "I. Variáveis: como cada uma é construída", "I. Variáveis"),
    (T_BAS, "Table 46", "1 na vaga marcada em 1º lugar; 0 nas outras vagas do curso e ciclo", "1 na 1ª opção; 0 nas outras"),
    (T_BAS, "Table 46", "Editais PMM-E (SGTES/MS)", "Editais PMM-E"),
    (T_BAS, "Table 46", "R$ 10, 15 ou 20 mil/mês pela faixa do IVS do município da vaga", "faixa do IVS da vaga"),
    (T_BAS, "Table 46", "município do vínculo médico no CNES antes da inscrição (não é a residência)",
     "vínculo no CNES antes da inscrição, não a residência"),
    (T_BAS, "Table 46", "km entre os centros do município anterior e do município da vaga", "km até a vaga"),
    (T_BAS, "Table 46", "curva do IVS; mesma região de saúde; mesmo município; porte; capital; vaga imediata",
     "IVS contínuo, região, porte, capital"),
    (T_BAS, "Table 46", "Ipea; TabNet; IBGE; quadros", "Ipea; IBGE"),
    (T_BAS, "TextBox 57", "linhas candidato × vaga (≈ 107 por candidato)", "linhas (≈ 107 vagas por candidato)"),
    (T_DES, "Text 18", "I. Onde fica a 1ª opção, em relação ao local de trabalho anterior", "I. Onde fica a 1ª opção"),
    (T_DES, "Text 19", "% dos 5.425 candidatos com 1ª opção e local de trabalho anterior identificado",
     "% dos 5.425 candidatos, em relação ao local de trabalho anterior"),
    (T_DES, "Text 23", "Descritivo: mostra onde escolhem, não por quê. Local de trabalho anterior = vínculo no CNES, "
     "não a residência.", "Descritivo: onde escolhem, não por quê."),
    (T_DES, "Rounded Rectangle 30", "é a distância mediana até a 1ª opção", "distância mediana"),
    (T_DES, "Rounded Rectangle 31", "escolhem uma vaga a até 189 km", "a até 189 km"),
    (T_DES, "Rounded Rectangle 32", "O modelo compara só vagas da mesma UF: a UF entra como pareamento, não como resultado.",
     "O modelo compara só vagas da mesma UF."),
    (T_MOD, "TextBox 47", "i: candidato · v: vaga do seu curso e ciclo · X: mesma região de saúde", None),
    (T_MOD, "Rounded Rectangle 48", ": quanto +R$ 5 mil multiplicam a chance de a vaga ser a 1ª opção",
     ": efeito de +R$ 5 mil na chance da 1ª opção"),
    (T_MOD, "Rounded Rectangle 48", "máxima verossimilhança; erro-padrão agrupado por curso × ciclo", None),
    (T_MOD, "TextBox 53", "salta nos cortes de IVS (R$ 10 → 15 → 20 mil)", "salta nos cortes de IVS"),
    (T_MOD, "TextBox 57", "efeito fixo: só compara vagas da mesma UF, vistas por médicos da mesma UF",
     "só compara vagas da mesma UF"),
    (T_MOD, "TextBox 61", "curva contínua do IVS, sem salto: no corte, só a bolsa salta", "contínua: no corte, só a bolsa salta"),
    (T_MOD, "TextBox 65", "atributos da vaga e da distância; não interpretados", "não interpretados"),
    (T_MOD, "Rounded Rectangle 66", "a probabilidade é calculada dentro das vagas de cada candidato. O que é do médico "
     "(idade, nota, especialidade) é igual em todas as vagas dele e se cancela: cada médico é comparado consigo mesmo.",
     "cada médico é comparado consigo mesmo; o que é dele se cancela."),
    (T_BOB, "Table 46", "bônus salarial que salta em cortes de população e tempo de viagem (+13%)",
     "bônus que salta em cortes (+13%)"),
    (T_BOB, "Table 46", "bolsa que salta nos cortes de IVS (+R$ 5 mil)", "bolsa que salta nos cortes de IVS"),
    (T_BOB, "Table 46", "professor escolhe na sua vez, entre as vagas que restam; pode sair do setor",
     "escolhe na sua vez; pode sair do setor"),
    (T_BOB, "Table 46", "médico lista as opções na inscrição; usamos a 1ª", "lista na inscrição; usamos a 1ª"),
    (T_BOB, "Table 46", "logit multinomial com cardápio personalizado e coeficientes aleatórios",
     "logit com coeficientes aleatórios"),
    (T_BOB, "Table 46", "logit condicional com o cardápio do curso e ciclo", "logit condicional"),
    (T_BOB, "Table 46", "só os saltos nos cortes, com polinômios da população e do tempo de viagem",
     "saltos nos cortes; variável do corte contínua"),
    (T_BOB, "Table 46", "só os saltos nos cortes, com curva contínua do IVS", "saltos nos cortes; IVS contínuo"),
    (T_BOB, "Table 46", "efeito fixo de província; distância até a casa do professor", "província fixa; distância até a casa"),
    (T_BOB, "Table 46", "efeito fixo do par de UFs; distância até o trabalho anterior",
     "par de UFs fixo; distância até o trabalho anterior"),
    (T_BOB, "Rounded Rectangle 48", "Por que não só uma RDD por vaga?", "RDD por vaga?"),
    (T_BOB, "Rounded Rectangle 48", "Compara vagas, uma observação por vaga; foi feita e o IC contém zero. O logit vê o "
     "mesmo médico diante de ≈ 107 vagas.", "Feita: IC contém zero."),
    (T_BOB, "Rounded Rectangle 49", "Por que não coeficientes aleatórios?", "Coeficientes aleatórios?"),
    (T_BOB, "Rounded Rectangle 49", "Eles observam a saída do setor e dois concursos por professor; nós, não. No modelo "
     "base, o logit misto dá peso da bolsa parecido: fica como sensibilidade.",
     "Sem saída do setor nos dados; logit misto dá peso parecido (sensibilidade)."),
    (T_BOB, "Rectangle 50", "trocar o estimador depois de ver o resultado seria escolha pós-resultado; alternativas "
     "entram só como robustez rotulada.", "alternativas só como robustez rotulada."),
    (T_IDE, "TextBox 45", "I. O que o software mantém fixo no cálculo", "I. O que fica fixo"),
    (T_IDE, "Table 46", "verossimilhança dentro das vagas de cada um: o que é dele se cancela", "o que é do médico se cancela"),
    (T_IDE, "Table 46", "254 dummies: UF de trabalho anterior × UF da vaga", "254 dummies (UF anterior × UF da vaga)"),
    (T_IDE, "Table 46", "não entra: a bolsa é a mesma no município inteiro e seria absorvida", "absorveria a bolsa"),
    (T_IDE, "Table 46", "controles na utilidade (distância: −0,514 por 100 km)", "controles"),
    (T_IDE, "TextBox 48", "II. Premissas e aderência", "II. Premissas"),
    (T_IDE, "Rounded Rectangle 49", "o IVS reproduz a faixa de 368/368 municípios (ciclo 1) e 454/454 (ciclo 2)",
     "368/368 e 454/454 municípios"),
    (T_IDE, "Rounded Rectangle 51", "não: outras regras federais mudam junto; medimos esse pacote", "não: medimos o pacote"),
    (T_IDE, "Rectangle 55", "a especificação com o par de UFs foi escolhida depois de ver o modelo base: é exploratória.",
     "par de UFs escolhido depois de ver os dados: exploratório."),
    (T_RES, "TextBox 47", "Também na equação: curva do IVS, estrato, vaga imediata e 254 dummies do par. Controles: não "
     "interpretados. 5.417 candidatos; EP agrupado por curso × ciclo (55 grupos).",
     "5.417 candidatos; EP agrupado por curso × ciclo."),
    (T_RES, "Rounded Rectangle 49", "log-chance de +R$ 5 mil por mês", "log-chance de +R$ 5 mil"),
    (T_RES, "Rounded Rectangle 50", "entre duas vagas iguais exceto a bolsa, a de +R$ 5 mil tem 1,47 vez a probabilidade de "
     "ser a 1ª opção (IC 95%: 1,15 a 1,89; p de Holm 0,005)", "IC 95%: 1,15 a 1,89; p de Holm 0,005"),
    (T_RES, "Rounded Rectangle 51", "+R$ 5 mil pesam como uma vaga 75 km mais perto", "= uma vaga 75 km mais perto"),
    (T_RES, "Rectangle 53", "especificação escolhida após ver os dados. A pré-registrada, sem o par de UFs: ×1,25 "
     "[0,98; 1,61], IC que contém 1.", "exploratório. Sem o par de UFs (pré-registrada): ×1,25 [0,98; 1,61], IC contém 1."),
    (T_ROB, "Rounded Rectangle 26", "Distância em log, região anterior e cada degrau separado; bootstrap para poucos "
     "grupos: p 0,011.", "Variantes: mesmo efeito. Bootstrap: p 0,011."),
    (T_ROB, "Rounded Rectangle 30", "Só vagas perto do corte: menos dados, IC contém 1 (inconclusivo).",
     "Perto do corte: IC contém 1 (inconclusivo)."),
    (T_ROB, "Rounded Rectangle 32", "com todos os dados e sempre na mesma UF, o efeito fica entre ×1,41 e ×1,52 em toda "
     "variante. Onde a informação é menor — perto do corte e nos ciclos 1 e 3 —, o IC contém 1.",
     "com todos os dados, ×1,41 a ×1,52. Com menos dados, o IC contém 1."),
    (T_CON, "Texto Resposta", "Entre vagas da mesma UF, R$ 5 mil a mais multiplicam por 1,47 a chance de a vaga ser a 1ª "
     "opção (IC 95%: 1,15 a 1,89).", "IC 95%: 1,15 a 1,89; exploratório."),
    (T_CON, "Número Força", "2º ciclo, vagas da mesma UF", "2º ciclo"),
    (T_CON, "Texto Força", "No 2º ciclo, IC 95% de 1,30 a 2,78. Nos ciclos 1 e 3, ×1,15 e ×1,25, com IC que contém 1.",
     "Ciclos 1 e 3: IC contém 1."),
    (T_CON, "Texto Teoria", "Os dados sugerem: R$ 5 mil a mais pesam o mesmo que uma vaga 75 km mais perto (IC 95%: 28 "
     "a 122 km).", "Os dados sugerem (IC 95%: 28 a 122 km)."),
    (T_CON, "Text 21", "a bolsa maior reordena a escolha entre vagas da mesma UF; não mostramos que leve mais médicos ao "
     "município.", "reordena a 1ª opção na inscrição; não mostra mais médicos no município."),
    (T_LIM, "Problema 1", "A comparação só entre vagas da mesma UF (×1,47) foi escolhida depois de vermos os dados.",
     "Par de UFs escolhido depois de ver os dados."),
    (T_LIM, "Implicação 1", "É exploratório: sugere o efeito, não o confirma.", "Exploratório: sugere, não confirma."),
    (T_LIM, "Problema 2", "Na especificação pré-registrada, que compara vagas de todas as UFs: ×1,25 (IC 95%: 0,98 a 1,61).",
     "Pré-registrada: ×1,25 (IC 95%: 0,98 a 1,61)."),
    (T_LIM, "Implicação 2", "Não dá para descartar efeito nulo nessa versão.", "Efeito nulo não descartado."),
    (T_LIM, "Problema 3", "Observamos a vaga que o médico pôs em 1º lugar, não se ele foi trabalhar no município.",
     "Vemos a vaga marcada, não a ida ao município."),
    (T_LIM, "Implicação 3", "Escolher não é ir: não mostra mais médicos chegando.", "Escolher não é ir."),
    (T_LIM, "Problema 4", "Quando o município passa do corte de IVS, outras regras federais mudam junto com a bolsa.",
     "Outras regras federais mudam no mesmo corte."),
    (T_LIM, "Implicação 4", "Medimos o pacote: o efeito do dinheiro não sai isolado.", "O dinheiro não sai isolado."),
    (T_LIM, "Problema 5", "No 2º ciclo, ×1,90; no 1º (×1,15) e no 3º (×1,25), o IC contém 1.", "Ciclos 1 e 3: IC contém 1."),
    (T_LIM, "Implicação 5", "Não dá para generalizar para outros ciclos.", "Não generaliza para outros ciclos."),
    (T_LIM, "Problema 6", "É onde o médico tinha vínculo antes da inscrição, não onde mora; só define o par de UFs fixado.",
     "Vínculo antes da inscrição, não a residência."),
    (T_LIM, "Implicação 6", "É pareamento, não resultado nem causa.", "É pareamento, não resultado."),
)
# Grupos que saem inteiros (título do slide, texto de uma forma do grupo): números em destaque que repetem as manchetes
REMOVER_GRUPOS = ((T_BOL, "+86"), (T_BOL, "6"))


def _runs_da_forma(sh):
    if sh.has_table:
        for row in sh.table.rows:
            for cell in row.cells:
                for par in cell.text_frame.paragraphs:
                    for r in par.runs:
                        yield par, r, cell.text_frame
    elif sh.has_text_frame:
        for par in sh.text_frame.paragraphs:
            for r in par.runs:
                yield par, r, sh.text_frame


def enxugar(prs) -> list[str]:
    for titulo, nome, trecho, novo in TROCAS_ENXUGAR:
        sl = slide_por_titulo(prs, titulo)
        achados = [(par, r, tf) for sh in formas(sl.shapes) if sh.name == nome for par, r, tf in _runs_da_forma(sh)
                   if trecho in r.text]
        if not achados:  # trecho quebrado em vários runs: procura no parágrafo inteiro
            pars = {id(par): (par, par.runs[0], tf) for sh in formas(sl.shapes) if sh.name == nome
                    for par, _, tf in _runs_da_forma(sh) if trecho in par.text}
            achados = list(pars.values())
            inteiro = True
        else:
            inteiro = False
        if len(achados) != 1:
            raise SystemExit(f"ERRO: {titulo!r}, {nome!r}: o trecho {trecho!r} está em {len(achados)} lugares")
        par, r, tf = achados[0]
        if novo is None:
            if len(tf.paragraphs) > 1:
                par._p.getparent().remove(par._p)
            else:
                for rr in par.runs:
                    rr.text = ""
        elif inteiro:
            texto = par.text.replace(trecho, novo)
            for rr in par.runs[1:]:
                rr._r.getparent().remove(rr._r)
            r.text = texto
        else:
            r.text = r.text.replace(trecho, novo)
    for titulo, texto in REMOVER_GRUPOS:
        sl = slide_por_titulo(prs, titulo)
        grupos = [g for g in sl.shapes if g.shape_type == 6
                  and any(x.has_text_frame and x.text_frame.text.strip() == texto for x in formas(g.shapes))]
        if len(grupos) != 1:
            raise SystemExit(f"ERRO: {titulo!r}: esperava 1 grupo com {texto!r}; achei {len(grupos)}")
        remover(grupos[0])
    return [f"enxugamento: {len(TROCAS_ENXUGAR)} trocas de texto e {len(REMOVER_GRUPOS)} grupos removidos "
            "(doc 02, §0.2)"]



# --------------------------------------------------------------------------------------------------------------
# Redesenho (pedido do autor de 11/11/2026: "ainda tem slides demais e conteúdo demais por slide")
# (título do slide, nome da forma) que saem; o resto sobe ou se alarga em redesenhar()
# --------------------------------------------------------------------------------------------------------------
REMOVER_FORMAS = (
    # hipótese: o exemplo das vagas A e B repete o slide do exemplo do método
    (T_HIP, "TextBox 46"), (T_HIP, "TextBox 47"), (T_HIP, "Rounded Rectangle 48"), (T_HIP, "Rounded Rectangle 49"),
    (T_HIP, "Rounded Rectangle 50"), (T_HIP, "TextBox 51"), (T_HIP, "TextBox 52"), (T_HIP, "Rounded Rectangle 53"),
    # base: o formato longo repete os passos 1 e 2 do método
    (T_BAS, "TextBox 47"), (T_BAS, "TextBox 48"), (T_BAS, "Table 49"), (T_BAS, "TextBox 50"),
    # resultado: o ciclo 2 já está na robustez, na conclusão e nas limitações
    (T_RES, "Rounded Rectangle 52"),
)
# resultado: linhas de controle (não interpretadas) que saem da tabela de coeficientes
LINHAS_CONTROLE = ("Mesma região de saúde", "Mesmo município", "log(população 2022)", "Capital")


def redesenhar(prs) -> list[str]:
    for titulo, nome in REMOVER_FORMAS:
        remover(por_nome(slide_por_titulo(prs, titulo), nome))
    # hipótese: a frase em destaque maior, os três cartões e a cautela sobem
    sl = slide_por_titulo(prs, T_HIP)
    caixa = por_nome(sl, "Rounded Rectangle 45")
    caixa.height = Inches(1.75)
    for nome in ("Rounded Rectangle 54", "Rounded Rectangle 55", "Rounded Rectangle 56"):
        sh = por_nome(sl, nome)
        sh.top, sh.height = Inches(3.0), Inches(1.6)
    por_nome(sl, "Rectangle 57").top = Inches(4.85)
    # base: a tabela de variáveis ocupa a largura toda
    sl = slide_por_titulo(prs, T_BAS)
    tab = por_nome(sl, "Table 46")
    fator = Inches(12.85) / tab.width
    for col in tab.table.columns:
        col.width = int(col.width * fator)
    tab.width = Inches(12.85)
    # resultado: só a bolsa e a distância na tabela; a nota sobe
    sl = slide_por_titulo(prs, T_RES)
    tab = por_nome(sl, "Table 46")
    tbl = tab.table._tbl
    for tr in list(tbl.tr_lst):
        primeira = "".join(t_.text or "" for t_ in tr.iter("{%s}t" % NS["a"]))
        if any(primeira.startswith(x) for x in LINHAS_CONTROLE):
            tbl.remove(tr)
    if len(tbl.tr_lst) != 3:
        raise SystemExit(f"ERRO: a tabela do resultado devia ficar com 3 linhas; ficou com {len(tbl.tr_lst)}")
    for tr in tbl.tr_lst:
        tr.h = Inches(0.8)
    tab.height = Inches(2.4)
    por_nome(sl, "TextBox 47").top = Inches(3.8)
    return [f"redesenho: {len(REMOVER_FORMAS)} formas fora (exemplo da hipótese, formato longo da base, ciclo 2 do "
            f"resultado) e {len(LINHAS_CONTROLE)} linhas de controle fora da tabela do resultado"]


def slide_por_titulo(prs, titulo: str):
    achados = [s for s in prs.slides if any(x.has_text_frame and " ".join(x.text_frame.text.split()) == titulo
                                            for x in s.shapes)]
    if len(achados) != 1:
        raise SystemExit(f"ERRO: esperava 1 slide com o título {titulo!r}; achei {len(achados)}")
    return achados[0]


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
    feitas = adaptar_grupo(prs) + adaptar_teoria(prs) + trocar_fallbacks(prs)
    # Diagrama da teoria da mudança: "origem" sai da tela (doc 12, §1.2); a nota diz qual elo a hipótese testa
    sd = diag.slides[N_DIAG_SLIDE - 1]
    trocar_paragrafo(por_nome(sd, "A_no_A4"), A4_DIAGRAMA, 2,
                     antigo="Moradia, deslocamento, amenidades e distância da origem.")
    notas(sd, NOTAS[16])
    trocar_paragrafo(por_nome(sd, "A_nota"), A_NOTA_DIAGRAMA, 0,
                     antigo="Diagrama teórico: as setas dizem o que o modelo prevê, não o que foi estimado.")
    feitas.append("diagrama da teoria: a nota diz qual elo é testado (o da remuneração)")
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
    # δ é o desconto nas equações da teoria; no modelo empírico, a distância passa a ser γ (como no doc 11)
    for nome in ("TextBox 47", "TextBox 63"):
        modelo = [s for s in prs.slides if any(x.has_text_frame and x.text_frame.text.strip()
                                                == "Modelo: logit condicional da 1ª opção" for x in s.shapes)]
        if len(modelo) != 1:
            raise SystemExit("ERRO: slide do modelo não encontrado")
        sh = por_nome(modelo[0], nome)
        trocados = 0
        for par in sh.text_frame.paragraphs:
            for r in par.runs:
                if "δ" in r.text:
                    r.text = r.text.replace("δ", "γ")
                    trocados += 1
        if trocados != 1:
            raise SystemExit(f"ERRO: esperava 1 'δ' em {nome} do slide do modelo; achei {trocados}")
    feitas.append("slide do modelo: γ para a distância (δ é o desconto da teoria)")
    # decisão do autor (11/11/2026): a lista sincera entra como premissa (a grade de limitações está cheia)
    ident = slide_por_titulo(prs, "Identificação: o que fica fixo e o que supomos")
    trocar_paragrafo(por_nome(ident, "Rounded Rectangle 53"), PREMISSA_LISTA, 1,
                     antigo="supomos que o médico viu todas as vagas do seu curso")
    lim = slide_por_titulo(prs, "Limitações e o que cada uma implica")
    notas(lim, lim.notes_slide.notes_text_frame.text.rstrip() + "\n\n" + NOTA_LISTA)
    feitas.append("identificação: 'listou sem estratégia' na premissa do conjunto de escolha; nota nas limitações")
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
    feitas += enxugar(prs)
    feitas += redesenhar(prs)
    # notas do divisor "Apêndice": tinham uma resposta de chat colada, vinda do deck do grupo
    notas(prs.slides[ORDEM.index(("G", 32, None))], "")
    feitas.append("notas do divisor 'Apêndice' limpas (resposta de chat colada no deck do grupo)")
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
    saidas += [{"caminho": (DIR_EQ / f[2]).relative_to(ROOT).as_posix(), "sha256": sha256(DIR_EQ / f[2])}
               for f in FALLBACKS]
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
