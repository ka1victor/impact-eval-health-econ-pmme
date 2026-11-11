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
                   "continuam contra, e é o saldo das três variáveis que decide qual vaga o médico escolhe.")
ROTULO_CADEIA = "CADEIA DO MODELO"
ADICOES = "Adições ao modelo do slide anterior:"
A_NOTA_DIAGRAMA = ("Diagrama teórico. Testamos o elo da remuneração: a bolsa eleva o valor da vaga e muda a 1ª opção; "
                   "o resto da cadeia não é estimado.")
PREMISSA_LISTA = "supomos que viu todas as vagas do curso e listou sem estratégia"
NOTA_LISTA = ("Lista sincera (decisão do autor de 11/11/2026; premissa no slide de Identificação): a 1ª opção só é a vaga "
              "preferida se o médico listou as vagas pela preferência, sem estratégia (por exemplo, pôr em 1º onde acha "
              "que passa). Se houver estratégia, o ×1,47 mistura preferência e chance de ser alocado.")

# ---- Slides novos do método (pedido do autor, 09/11/2026: a banca não entendeu o método e nunca tinha ouvido falar) --
VL_EST = ROOT / "output/rdd_bolsa/VL_estimativas.csv"
TITULO_M1 = "Método passo a passo: como medimos o peso da bolsa"
FAIXA_M1 = ("Logit condicional (McFadden, 1974; Nobel de Economia de 2000): o modelo padrão para quem escolhe uma "
            "opção entre várias. É o que Bobba et al. usam para professores escolhendo vagas no Peru.")
PASSOS_M1 = (
    ("1", "O cardápio", "Cada candidato vê todas as vagas abertas do seu curso no ciclo: ≈ {cardapio} vagas, em média."),
    ("2", "A escolha", "Na base, uma linha por candidato × vaga. A vaga que ele marcou como 1ª opção vale 1; as outras, 0."),
    ("3", "A pontuação", "Cada vaga ganha uma pontuação: peso × bolsa + peso × distância + par de UFs + controles. "
                         "Chance de ser a escolhida = e^pontuação ÷ soma do cardápio."),
    ("4", "Os pesos", "O computador escolhe os pesos que deixam as 1ªs opções observadas o mais prováveis possível "
                      "(máxima verossimilhança). O peso da bolsa é o β."),
)
RODAPE_M1 = ("Por que \"condicional\": a conta compara vagas do mesmo cardápio, para o mesmo médico. O que é do médico "
             "(nota, idade, perfil) é igual em todas as vagas e se cancela.")
CAUTELA_M1 = "Mede a vaga marcada na inscrição, não a ida ao município."
FONTES_M1 = ("Fontes: McFadden (1974); Bobba et al. (NBER WP 29068, rev. jan. 2026), seção 4.1; "
             "output/rdd_bolsa/VL_estimativas.csv (VL-1, adendo 52e): {cand} candidatos, {linhas} linhas.")
TITULO_M2 = "Exemplo: um candidato, três vagas do mesmo curso em MG"
VAGAS_M2 = (("A", 10, 50), ("B", 15, 50), ("C", 15, 125))  # ilustrativo: bolsa (R$ mil/mês) e distância (km)
NOTA_M2 = ("Ilustrativo: três vagas inventadas, iguais no resto; pontuação só com a bolsa e a distância, com os pesos "
           "estimados no VL-1 ({b} por R$ 1 mil; {d} por 100 km). Na base real, cada candidato tem ≈ {cardapio} vagas.")
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
    (17, "eqleg", None, 0, 3, ": Local escolhido por r  ·  ", ": 1ª opção de r  ·  "),
    (17, "eqleg", None, 0, 6, ": ofertas disponíveis a r  ·  ", ": cardápio de r  ·  "),
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
     "Aumenta com equipe e equipamentos ruins", "Equipe ruim, longe de casa"),
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
    (20, "pill0", None, 0, 0, "CUSTO GEOGRÁFICO (", "GEOGRÁFICO ("),
    (20, "pill1", None, 0, 0, "CUSTO LABORAL (CHONÉ & MA, 2011)", "LABORAL (CHONÉ & MA, 2011)"),
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
    (19, "TextBox 1", "renda_real_liquida.png", "eq",
     r"$\mathbf{arg\,max}_{\mathbfit{m}\in \mathbfit{I}}\ \sum_{\mathbfit{t}}\ \mathbfit{\delta}^{\mathbfit{t}}\left["
     r"\frac{\mathbb{E}(\mathbfit{w}_{\mathbfit{mt(s)}})}{\mathbfit{p}_{\mathbfit{mt}}} - \mathbfit{c}_{\mathbfit{mt(s)}}\right]$"),
    (19, "Retângulo: Cantos Arredondados 38", "gera_m.png", "caixa",
     (r"Gera $\mathit{m}^{*}$:", ("a localidade que maximiza a renda real líquida", "esperada ao longo da carreira"))),
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


def slides_metodo(prs, layout, modelo_rodape) -> list:
    v = pesos_vl1()
    car = str(v["cardapio"])
    # ---- 1: o método em quatro passos
    s1 = _slide_base(prs, layout, TITULO_M1, modelo_rodape)
    _caixa(s1, 0.25, 0.9, 12.83, 0.78, [[(FAIXA_M1, 14, False, BRANCO)]], fill=VERDE, nome="Faixa McFadden")
    larg, x0, gap = 2.95, 0.25, 0.343
    for k, (num, tit, corpo) in enumerate(PASSOS_M1):
        x = x0 + k * (larg + gap)
        _caixa(s1, x, 1.88, larg, 3.12,
               [[(num, 30, True, VERDE)], [(tit, 17, True, VERDE)], [("", 6, False, TEXTO)],
                [(corpo.format(cardapio=car), 13, False, TEXTO)]],
               fill=CLARO, line=BORDA, anchor=MSO_ANCHOR.TOP, nome=f"Passo {num}")
        if k < len(PASSOS_M1) - 1:
            _caixa(s1, x + larg - 0.02, 3.2, gap + 0.04, 0.5, [[("→", 22, True, VERDE)]],
                   forma=MSO_SHAPE.RECTANGLE, align=PP_ALIGN.CENTER, nome="Seta")
    i = RODAPE_M1.index(":") + 1
    _caixa(s1, 0.25, 5.18, 12.83, 0.78, [[(RODAPE_M1[:i] + " ", 14, True, VERDE), (RODAPE_M1[i:].strip(), 14, False, TEXTO)]],
           fill=CLARO, line=BORDA, nome="Condicional")
    _caixa(s1, 0.25, 6.1, 12.83, 0.5, [[("Cautela: ", 13, True, VERDE), (CAUTELA_M1, 13, False, TEXTO)]],
           fill=CLARO, nome="Cautela")
    _fontes(s1, FONTES_M1.format(cand=f"{v['n_cand']:,}".replace(",", "."), linhas=f"{v['n_lin']:,}".replace(",", ".")))
    notas(s1, NOTAS_M[1])
    # ---- 2: exemplo com três vagas
    s2 = _slide_base(prs, layout, TITULO_M2, modelo_rodape)
    linhas, cols = len(VAGAS_M2) + 1, 5
    tab = s2.shapes.add_table(linhas, cols, Inches(0.25), Inches(0.95), Inches(7.6), Inches(2.7)).table
    cab = ("Vaga", "Bolsa", "Distância", "Pontuação", "Chance de ser a 1ª opção")
    larguras = (0.9, 1.35, 1.35, 1.5, 2.5)
    for j, wj in enumerate(larguras):
        tab.columns[j].width = Inches(wj)
    corpo = [[n, f"R$ {bolsa} mil", f"{km} km", _virgula(u, 2), _virgula(100 * pr, 1) + "%"]
             for (n, bolsa, km), u, pr in zip(VAGAS_M2, v["pont"], v["prob"])]
    for i_, linha in enumerate([cab] + corpo):
        for j, txt in enumerate(linha):
            c = tab.cell(i_, j)
            c.fill.solid()
            c.fill.fore_color.rgb = RGBColor.from_string(VERDE if i_ == 0 else (CLARO if i_ % 2 else BRANCO))
            c.text = txt
            r = c.text_frame.paragraphs[0].runs[0]
            r.font.size = Pt(13 if i_ == 0 else 16)
            r.font.bold = i_ == 0 or j == 4
            r.font.name = "Montserrat"
            r.font.color.rgb = RGBColor.from_string(BRANCO if i_ == 0 else TEXTO)
            c.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
    _caixa(s2, 0.25, 3.75, 7.6, 0.9,
           [[(NOTA_M2.format(b=_virgula(v["b"], 3), d=_virgula(v["dist"], 3), cardapio=car), 10, False, CINZA)]],
           forma=MSO_SHAPE.RECTANGLE, anchor=MSO_ANCHOR.TOP, nome="Nota ilustrativo")
    pa, pb_, pc = (100 * x for x in v["prob"])
    rc, km = _virgula(v["rc"], 2), str(round(v["km"]))
    _caixa(s2, 8.1, 0.95, 4.98, 1.75,
           [[("B CONTRA A", 11, True, "A8C8A3")],
            [(f"{_virgula(pb_, 1)}% ÷ {_virgula(pa, 1)}% = {rc}", 22, True, BRANCO)],
            [(f"R$ 5 mil a mais, o resto igual: é o ×{rc} do resultado.", 12, False, BRANCO)]],
           fill=VERDE, nome="B contra A")
    _caixa(s2, 8.1, 2.88, 4.98, 1.77,
           [[("C CONTRA A", 11, True, "A8C8A3")],
            [(f"{_virgula(pc, 1)}% ≈ {_virgula(pa, 1)}%", 22, True, BRANCO)],
            [(f"R$ 5 mil a mais, mas {km} km mais longe: a distância come o ganho. "
              f"Daí \"R$ 5 mil valem cerca de {km} km\".", 12, False, BRANCO)]],
           fill=VERDE, nome="C contra A")
    _caixa(s2, 0.25, 4.85, 12.83, 1.05,
           [[("Como se lê o β: ", 14, True, VERDE),
             (f"o peso da bolsa é {_virgula(v['b'], 3)} por R$ 1 mil; para R$ 5 mil, e^(5 × {_virgula(v['b'], 3)}) = {rc}. "
              f"Entre duas vagas do mesmo cardápio, a de bolsa R$ 5 mil maior tem {rc} vez a chance da outra de ser a "
              f"1ª opção.", 14, False, TEXTO)]],
           fill=CLARO, line=BORDA, nome="Leitura do beta")
    _caixa(s2, 0.25, 6.05, 12.83, 0.5, [[("Cautela: ", 13, True, VERDE),
                                          ("exemplo ilustrativo: as vagas são inventadas; os pesos são os estimados.",
                                           13, False, TEXTO)]], fill=CLARO, nome="Cautela")
    _fontes(s2, FONTES_M2)
    notas(s2, NOTAS_M[2])
    return [s1, s2], v

def slide_por_titulo(prs, titulo: str):
    achados = [s for s in prs.slides if any(x.has_text_frame and " ".join(x.text_frame.text.split()) == titulo
                                            for x in s.shapes)]
    if len(achados) != 1:
        raise SystemExit(f"ERRO: esperava 1 slide com o título {titulo!r}; achei {len(achados)}")
    return achados[0]


# Correções factuais da revisão de 11/11/2026, aplicadas por forma: (forma, antigo, novo)
CORRECOES = (
    # a faixa do meio começa em 0,301 (0,300 fica em R$ 10 mil), como no diagrama da teoria
    ("Rounded Rectangle 47", "IVS de 0,300 a 0,400", "IVS de 0,301 a 0,400"),
    # o item 11.1.4 do edital é a cláusula da grade do FAQ, que não é a aplicada (errata E10)
    ("Text 34", " (item 11.1.4)", ""),
)


def aplicar_correcoes(prs) -> list[str]:
    feitas = []
    for nome, antigo, novo in CORRECOES:
        achou = 0
        for s in prs.slides:
            for sh in formas(s.shapes):
                if sh.name != nome or not sh.has_text_frame or antigo not in sh.text_frame.text:
                    continue
                for par in sh.text_frame.paragraphs:
                    for r in par.runs:
                        if antigo in r.text:
                            r.text = r.text.replace(antigo, novo)
                            achou += 1
        if achou != 1:
            raise SystemExit(f"ERRO: esperava 1 {antigo!r} em {nome}; achei {achou}")
        feitas.append(f"revisão de 11/11/2026: {antigo.strip()!r} → {novo.strip()!r}" if novo
                      else f"revisão de 11/11/2026: sai {antigo.strip()!r}")
    return feitas


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
    feitas += aplicar_correcoes(prs)
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
