"""Gera o diagrama causal (teoria da mudança) da banca final em formas nativas do PowerPoint.

Entrada: o deck do grupo (`.pptx`, fora do repositório; é só lido). Saída, em
`output/apresentacao_banca_final/`:

* `slides_diagrama_teoria_mudanca.pptx`: só os 2 slides novos, no template do deck;
* `deck_proposta_reorganizada.pptx`: o deck inteiro com o diagrama na seção de
  teoria e os slides de equações movidos para depois do slide "Apêndice";
* `manifesto_diagrama.json`: entradas e saídas com SHA-256, ordem dos slides e
  verificações.

Natureza: conteúdo teórico. O diagrama não traz número de resultado; os únicos
números são a regra da bolsa (cortes do IVS e valores em R$), as datas das
referências e a numeração dos passos. Nada é estimado aqui e nada é lido de
`data/`.

Fonte de verdade do conteúdo: `docs/07_apresentacoes/banca_final/01_diagrama_teoria_mudanca.md`.
O texto de cada caixa vive nas constantes `NOS_A`, `NOS_B` e `AVISOS_B` abaixo; o
bloco gerado do doc 01 é regravado a partir delas com `--atualizar-doc`, e
`tests/test_diagrama_banca_final.py` confere o pptx contra as constantes e o doc.

Uso:

    python3 scripts/apresentacao/gerar_diagrama_banca_final.py --deck "<caminho do deck do grupo>"
    python3 scripts/apresentacao/gerar_diagrama_banca_final.py --atualizar-doc   # só o bloco do doc 01

Determinístico: XML montado por funções puras, zip com data fixa e ordem estável.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
SAIDA = ROOT / "output" / "apresentacao_banca_final"
DOC01 = ROOT / "docs" / "07_apresentacoes" / "banca_final" / "01_diagrama_teoria_mudanca.md"
ARQ_SLIDES = "slides_diagrama_teoria_mudanca.pptx"
ARQ_DECK = "deck_proposta_reorganizada.pptx"
ARQ_MANIFESTO = "manifesto_diagrama.json"
MARCA_INI = "<!-- banca_final:caixas:inicio -->"
MARCA_FIM = "<!-- banca_final:caixas:fim -->"
DATA_REFERENCIA_DECK = "2026-10-26"
DATA_ZIP = (2026, 10, 26, 0, 0, 0)

# --------------------------------------------------------------------------------------------------
# Conteúdo (fonte de verdade para o pptx; o doc 01 reproduz estas linhas no bloco gerado)
# --------------------------------------------------------------------------------------------------

TITULO_A = "Da regra da bolsa à saúde: teoria da mudança"
TITULO_B = "A hipótese e onde a identificação é fraca"
NAV_A = "Literatura"
NAV_B = "Hipótese"
RODAPE_A = "Diagrama teórico: as setas dizem o que o modelo prevê, não o que foi estimado."

# id, papel, pílula, título, texto, fonte, onde as equações estão no apêndice
NOS_A = [
    dict(id="A1", papel="regra", pilula="", titulo="IVS 2010 oficial",
         texto="Vulnerabilidade social do município.",
         fonte="IPEA, ATLAS IVS",
         apendice="— (regra; sem equação)"),
    dict(id="A2", papel="regra", pilula="", titulo="Faixa da bolsa",
         texto="Cortes do IVS em 0,300 e 0,400.",
         fonte="",
         apendice="— (regra; sem equação)"),
    dict(id="A3", papel="forca_a_favor", pilula="ELEVA O VALOR", titulo="A bolsa eleva o salário esperado",
         texto="E(w | B) sobe com a faixa. Rende mais onde a vida é barata.",
         fonte="MOEHLING et al. (2020)",
         apendice="A escolha locacional maximiza a utilidade; A escolha locacional maximiza a renda real líquida"),
    dict(id="A4", papel="forca_contra", pilula="REDUZ O VALOR", titulo="Custo de viver ali (geográfico)",
         texto="Moradia, deslocamento, amenidades e distância da origem.",
         fonte="REDDING & ROSSI-HANSBERG (2017)",
         apendice="Literatura divide o custo em dois tipos: geográfico e laboral"),
    dict(id="A5", papel="forca_contra", pilula="REDUZ O VALOR", titulo="Custo de trabalhar ali (laboral)",
         texto="Equipe, capital, esforço e altruísmo do médico.",
         fonte="CHONÉ & MA (2011)",
         apendice="Literatura divide o custo em dois tipos: geográfico e laboral"),
    dict(id="A6", papel="valor", pilula="", titulo="Valor da vaga para o médico",
         texto="Valor presente da renda real menos o custo do lugar.",
         fonte="MOEHLING et al. (2020)",
         apendice="A escolha locacional maximiza a utilidade; Da condição de aceitação, sai nossa hipótese econômica"),
    dict(id="A7", papel="agregacao", pilula="", titulo="Parcela de médicos que a escolhe (π)",
         texto="Médicos diferem em curso, vínculos e preferências.",
         fonte="BURDETT, SHI & WRIGHT (2001)",
         apendice="Da escolha individual ao preenchimento agregado"),
    dict(id="A8", papel="agregacao", pilula="", titulo="Vaga preenchida",
         texto="Chance de a vaga receber ao menos um médico.",
         fonte="BURDETT, SHI & WRIGHT (2001)",
         apendice="Da escolha individual ao preenchimento agregado"),
    dict(id="A9", papel="politica", pilula="", titulo="Capacidade",
         texto="Vínculos e horas de especialistas.",
         fonte="", apendice="— (elo da política; sem equação do modelo)"),
    dict(id="A10", papel="politica", pilula="", titulo="Produção e acesso",
         texto="Consultas, exames e cirurgias.",
         fonte="", apendice="— (elo da política; sem equação do modelo)"),
    dict(id="A11", papel="politica", pilula="", titulo="Saúde",
         texto="Espera e internações dos moradores.",
         fonte="", apendice="— (elo da política; sem equação do modelo)"),
]
ROTULOS_A = [  # rótulos de faixa à esquerda e de grupo embaixo
    dict(id="R1", texto="REGRA", numero="1"),
    dict(id="R2", texto="ESCOLHA DO MÉDICO", numero="2"),
    dict(id="R3", texto="DA VAGA À SAÚDE", numero="3"),
]
FAIXAS_A = [("até 0,300", "R$ 10 mil"), ("0,301 a 0,400", "R$ 15 mil"), ("acima de 0,400", "R$ 20 mil")]
GRUPOS_A = [
    dict(id="G1", texto="AGREGAÇÃO · BURDETT, SHI & WRIGHT (2001)"),
    dict(id="G2", texto="ELOS DA POLÍTICA: DO PROVIMENTO À SAÚDE"),
]
SETAS_A = [
    ("A1", "A2", "o IVS decide a faixa", "regra aplicada (auditoria 16)"),
    ("A2", "A3", "a faixa soma R$ à remuneração esperada", "Moehling et al. (2020)"),
    ("A3", "A6", "mais renda real eleva o valor da vaga", "Moehling et al. (2020)"),
    ("A4", "A6", "custo de viver ali reduz o valor da vaga", "Redding & Rossi-Hansberg (2017)"),
    ("A5", "A6", "custo de trabalhar ali reduz o valor da vaga", "Choné & Ma (2011)"),
    ("A6", "A7", "quanto maior o valor, maior a parcela de médicos que escolhe a vaga",
     "Moehling et al. (2020); Burdett, Shi & Wright (2001)"),
    ("A7", "A8", "quanto maior a parcela, maior a chance de a vaga ser preenchida", "Burdett, Shi & Wright (2001)"),
    ("A8", "A9", "vaga preenchida vira médico no serviço (provimento)", "teoria da mudança do programa (doc 51, §1)"),
    ("A9", "A10", "mais capacidade permite mais produção e acesso", "teoria da mudança do programa (doc 51, §1)"),
    ("A10", "A11", "mais acesso, melhor a saúde dos moradores", "teoria da mudança do programa (doc 51, §1)"),
]

BANNER_B_ROTULO = "HIPÓTESE"
BANNER_B_TEXTO = ("Municípios com maior remuneração oferecida pelo PMM-E têm maior probabilidade "
                  "de preenchimento de vagas.")
PILULA_B = "A BOLSA AGE AQUI"
ROTULO_HIPOTESE_B = "HIPÓTESE: BOLSA → PREENCHIMENTO"
NOS_B = [
    dict(id="B1", passo="0", titulo="Regra", texto="IVS 2010 define a faixa da bolsa.", aviso="A", destaque=False),
    dict(id="B2", passo="1", titulo="Abertura de vagas", texto="Gestor propõe, SGTES decide.", aviso="B", destaque=False),
    dict(id="B3", passo="2", titulo="Escolha do médico", texto="Valor da vaga define quem a escolhe.",
         aviso="", destaque=True),
    dict(id="B4", passo="3", titulo="Vaga preenchida", texto="Ao menos um médico a escolhe.", aviso="", destaque=False),
    dict(id="B5", passo="4", titulo="Capacidade", texto="Vínculos e horas de especialistas.", aviso="C", destaque=False),
    dict(id="B6", passo="5", titulo="Produção e acesso", texto="Consultas, exames e cirurgias.", aviso="", destaque=False),
    dict(id="B7", passo="6", titulo="Saúde", texto="Espera e internações dos moradores.", aviso="", destaque=False),
]
CABECALHO_AVISOS_B = "ONDE A LEITURA É FRÁGIL"
AVISOS_B = [
    dict(id="A", no="B1", titulo="Outras políticas nos mesmos cortes",
         texto="Em 0,300 e 0,400 mudam também outras regras federais. O salto mede um pacote, não só a bolsa.",
         fonte="auditoria 18"),
    dict(id="B", no="B2", titulo="A vaga abre antes da escolha",
         texto="O gestor propõe e a SGTES prioriza, sem fórmula publicada. Contar vagas preenchidas mistura abrir com atrair.",
         fonte="doc 51, §1"),
    dict(id="C", no="B5", titulo="Substituição",
         texto="Parte dos médicos já estava no município. Chegada pode ser troca de vínculo, não oferta nova.",
         fonte="doc 51, §1 (passo 4)"),
]
RODAPE_B_LEAD = "O que o corte identifica: "
RODAPE_B_TEXTO = ("o incentivo marginal de R$ 5 mil, dentro de um pacote de regras. "
                  "Não é participação no PMM-E nem o efeito do Agora Tem Especialistas.")

NOTAS_A = ("Ler de cima para baixo. 1: a regra. O IVS 2010 oficial define a faixa da bolsa, com cortes em 0,300 e 0,400. "
           "2: a escolha do médico. A bolsa eleva o salário esperado; o custo de viver ali e o custo de trabalhar ali "
           "puxam contra. O saldo é o valor da vaga. 3: do valor à saúde. Quanto maior o valor, maior a parcela de "
           "médicos que escolhe a vaga e maior a chance de preencher. Só depois vêm capacidade, produção e acesso, e saúde. "
           "Este é o diagrama da teoria: as equações estão no apêndice.")
NOTAS_B = ("A hipótese é o elo da escolha: bolsa maior, vaga que vale mais, mais médicos a preferem, mais chance de preencher. "
           "A bolsa só age no passo 2. Três pontos limitam a leitura: A, outras políticas nos mesmos cortes de IVS "
           "(o salto mede um pacote); B, a abertura da vaga acontece antes da escolha e não tem fórmula publicada; "
           "C, substituição, porque parte dos médicos já estava no município. O contraste identifica o incentivo marginal "
           "de R$ 5 mil, não a participação no PMM-E.")

# Ordem do deck do grupo (posições 1-based do deck original). Os títulos conferem que são os slides certos.
TITULOS_ESPERADOS = {
    15: "Sumário", 16: "O modelo combina três elementos da teoria",
    17: "A escolha locacional maximiza a utilidade", 18: "Da escolha individual ao preenchimento agregado",
    19: "A escolha locacional maximiza a renda real líquida",
    20: "Literatura divide o custo em dois tipos: geográfico e laboral",
    21: "Da escolha individual ao preenchimento agregado",
    22: "Sumário", 23: "Da condição de aceitação, sai nossa hipótese econômica", 31: "Apêndice",
}
POS_EQUACOES = [16, 17, 18, 19, 20, 21, 23]
POS_MOSTRAR = [19, 20]  # estavam ocultos no deck do grupo; no apêndice passam a aparecer
NOVOS_NA_ORDEM = (
    list(range(1, 16)) + ["A"] + [22] + ["B"] + list(range(24, 32)) + POS_EQUACOES + list(range(32, 37))
)

# --------------------------------------------------------------------------------------------------
# Paleta e geometria (cores do deck do grupo)
# --------------------------------------------------------------------------------------------------

EMU = 914400
VERDE_ESCURO, VERDE, CLARO, CLARO2, LINHA = "114719", "056429", "F3F7F3", "E7F1EA", "C9DED1"
TEXTO, MUDO, BRANCO = "3A3A3A", "6B6B6B", "FFFFFF"
PILULA_VERDE, PILULA_ROSA, VERMELHO = "A4F09A", "FE8884", "C23B33"
FONTE = "Montserrat"


def pol(v: float) -> int:
    return int(round(v * EMU))


class Slide:
    """Acumula formas nativas (sp e cxnSp) com ids sequenciais e determinísticos."""

    def __init__(self) -> None:
        self.partes: list[str] = []
        self.prox = 100
        self.ids: dict[str, int] = {}

    def _id(self, nome: str) -> int:
        self.prox += 1
        self.ids[nome] = self.prox
        return self.prox

    # texto -------------------------------------------------------------------------------------
    @staticmethod
    def run(txt: str, sz: float, cor: str = TEXTO, b: bool = False, i: bool = False, spc: int = 0) -> str:
        attrs = f'lang="pt-BR" sz="{int(sz * 100)}"' + (' b="1"' if b else ' b="0"') + (' i="1"' if i else "")
        if spc:
            attrs += f' spc="{spc}"'
        return (f'<a:r><a:rPr {attrs} dirty="0"><a:solidFill><a:srgbClr val="{cor}"/></a:solidFill>'
                f'<a:latin typeface="{FONTE}"/></a:rPr><a:t>{escape(txt)}</a:t></a:r>')

    @staticmethod
    def para(runs: list[str], algn: str = "l", depois: float = 0, linha: int = 100) -> str:
        return (f'<a:p><a:pPr marL="0" indent="0" algn="{algn}"><a:lnSpc><a:spcPct val="{linha * 1000}"/></a:lnSpc>'
                f'<a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="{int(depois * 100)}"/></a:spcAft>'
                f'<a:buNone/></a:pPr>{"".join(runs)}</a:p>')

    # formas ------------------------------------------------------------------------------------
    def forma(self, nome: str, x: float, y: float, w: float, h: float, *, geom: str = "roundRect", adj: int = 8000,
              fill: str | None = None, line: str | None = None, line_w: float = 1.0, paras: list[str] | None = None,
              anchor: str = "ctr", ins: tuple[float, float, float, float] = (0.08, 0.05, 0.08, 0.05),
              txbox: bool = False, dash: str = "") -> int:
        i = self._id(nome)
        av = f'<a:avLst><a:gd name="adj" fmla="val {adj}"/></a:avLst>' if geom == "roundRect" else "<a:avLst/>"
        fill_x = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
        if line:
            d = f'<a:prstDash val="{dash}"/>' if dash else ""
            line_x = f'<a:ln w="{int(line_w * 12700)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill>{d}</a:ln>'
        else:
            line_x = "<a:ln><a:noFill/></a:ln>"
        corpo = "".join(paras) if paras else '<a:p><a:endParaRPr lang="pt-BR"/></a:p>'
        l, t, r, b = (pol(v) for v in ins)
        tb = ' txBox="1"' if txbox else ""
        self.partes.append(
            f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="{escape(nome)}"/><p:cNvSpPr{tb}/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{pol(x)}" y="{pol(y)}"/><a:ext cx="{pol(w)}" cy="{pol(h)}"/></a:xfrm>'
            f'<a:prstGeom prst="{geom}">{av}</a:prstGeom>{fill_x}{line_x}</p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="{l}" tIns="{t}" rIns="{r}" bIns="{b}" rtlCol="0" anchor="{anchor}">'
            f'<a:noAutofit/></a:bodyPr><a:lstStyle/>{corpo}</p:txBody></p:sp>')
        return i

    def texto(self, nome: str, x: float, y: float, w: float, h: float, paras: list[str], anchor: str = "t") -> int:
        return self.forma(nome, x, y, w, h, geom="rect", paras=paras, anchor=anchor, ins=(0, 0, 0, 0), txbox=True)

    def seta(self, nome: str, x1: float, y1: float, x2: float, y2: float, cor: str = VERDE, larg: float = 2.0,
             de: tuple[int, int] | None = None, para: tuple[int, int] | None = None, ponta: bool = True,
             dash: str = "") -> int:
        i = self._id(nome)
        flip = (' flipH="1"' if x2 < x1 else "") + (' flipV="1"' if y2 < y1 else "")
        cx = ""
        if de:
            cx += f'<a:stCxn id="{de[0]}" idx="{de[1]}"/>'
        if para:
            cx += f'<a:endCxn id="{para[0]}" idx="{para[1]}"/>'
        d = f'<a:prstDash val="{dash}"/>' if dash else ""
        fim = '<a:tailEnd type="triangle" w="med" len="med"/>' if ponta else ""
        self.partes.append(
            f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{i}" name="{escape(nome)}"/><p:cNvCxnSpPr>{cx}</p:cNvCxnSpPr><p:nvPr/></p:nvCxnSpPr>'
            f'<p:spPr><a:xfrm{flip}><a:off x="{pol(min(x1, x2))}" y="{pol(min(y1, y2))}"/>'
            f'<a:ext cx="{pol(abs(x2 - x1))}" cy="{pol(abs(y2 - y1))}"/></a:xfrm>'
            f'<a:prstGeom prst="straightConnector1"><a:avLst/></a:prstGeom>'
            f'<a:ln w="{int(larg * 12700)}"><a:solidFill><a:srgbClr val="{cor}"/></a:solidFill>{d}{fim}</a:ln></p:spPr></p:cxnSp>')
        return i

    def circulo(self, nome: str, cx: float, cy: float, d: float, txt: str, fill: str, cor: str = BRANCO, sz: float = 11) -> int:
        return self.forma(nome, cx - d / 2, cy - d / 2, d, d, geom="ellipse", fill=fill, ins=(0, 0, 0, 0),
                          paras=[self.para([self.run(txt, sz, cor, b=True)], "ctr")])

    def pilula(self, nome: str, x: float, y: float, w: float, h: float, txt: str, fill: str, cor: str, sz: float = 9.5) -> int:
        return self.forma(nome, x, y, w, h, adj=26000, fill=fill, ins=(0.05, 0, 0.05, 0),
                          paras=[self.para([self.run(txt, sz, cor, b=True, spc=60)], "ctr")])


def xml_slide(titulo: str, nav: str, corpo: list[str]) -> str:
    """Slide no layout `1_Title Slide` do deck: título, número da página, navegação do rodapé e o corpo."""
    ns = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
          'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
    run_t = (f'<a:r><a:rPr lang="pt-BR" sz="2400" b="1" dirty="0"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
             f'<a:latin typeface="{FONTE}"/></a:rPr><a:t>{escape(titulo)}</a:t></a:r>')
    titulo_sp = ('<p:sp><p:nvSpPr><p:cNvPr id="2" name="Título"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
                 '<p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr><a:normAutofit/></a:bodyPr><a:lstStyle/>'
                 '<a:p><a:pPr marL="0" indent="0" algn="l"><a:lnSpc><a:spcPct val="104000"/></a:lnSpc><a:spcAft><a:spcPts val="0"/></a:spcAft>'
                 f'<a:buNone/></a:pPr>{run_t}</a:p></p:txBody></p:sp>')
    num_sp = ('<p:sp><p:nvSpPr><p:cNvPr id="3" name="Número da página"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
              '<p:nvPr><p:ph type="body" sz="quarter" idx="18"/></p:nvPr></p:nvSpPr><p:spPr><a:xfrm><a:off x="11706744" y="6457042"/>'
              '<a:ext cx="492080" cy="400640"/></a:xfrm></p:spPr><p:txBody><a:bodyPr anchor="ctr"><a:normAutofit/></a:bodyPr><a:lstStyle/>'
              '<a:p><a:pPr algn="ctr"/><a:fld id="{B1A5E0C2-5F3A-4C7E-9D11-7A2E6C0F4B01}" type="slidenum">'
              f'<a:rPr lang="pt-BR" sz="1400" b="1"><a:solidFill><a:srgbClr val="BFBFBF"/></a:solidFill><a:latin typeface="{FONTE}"/></a:rPr>'
              '<a:t>‹#›</a:t></a:fld><a:endParaRPr lang="pt-BR" sz="1400" b="1"><a:solidFill><a:srgbClr val="BFBFBF"/></a:solidFill></a:endParaRPr></a:p></p:txBody></p:sp>')
    secoes = ["Motivação", "Pergunta", "Literatura", "Hipótese", "Base de Dados", "Metodologia", "Resultados"]
    runs = []
    for k, s in enumerate(secoes):
        sep = "  |  " if k < len(secoes) - 1 else ""
        if s == nav:
            runs.append(f'<a:r><a:rPr lang="pt-BR" sz="1000" b="1" dirty="0"><a:solidFill><a:srgbClr val="114719"/></a:solidFill>'
                        f'<a:latin typeface="{FONTE}"/></a:rPr><a:t>{s}</a:t></a:r>'
                        f'<a:r><a:rPr lang="pt-BR" sz="1000" dirty="0"><a:latin typeface="{FONTE}"/></a:rPr><a:t>{sep}</a:t></a:r>')
        else:
            runs.append(f'<a:r><a:rPr lang="pt-BR" sz="1000" dirty="0"><a:latin typeface="{FONTE}"/></a:rPr><a:t>{s}{sep}</a:t></a:r>')
    nav_sp = ('<p:sp><p:nvSpPr><p:cNvPr id="4" name="Navegação do rodapé"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
              '<p:spPr><a:xfrm><a:off x="196860" y="6639248"/><a:ext cx="9223026" cy="246221"/></a:xfrm>'
              '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr><p:txBody><a:bodyPr wrap="square" rtlCol="0">'
              f'<a:spAutoFit/></a:bodyPr><a:lstStyle/><a:p>{"".join(runs)}</a:p></p:txBody></p:sp>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<p:sld {ns}><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            f'{titulo_sp}{num_sp}{nav_sp}{"".join(corpo)}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')


# --------------------------------------------------------------------------------------------------
# Slide A: a cadeia da regra à saúde
# --------------------------------------------------------------------------------------------------

def _no(lista: list[dict], id_: str) -> dict:
    return next(n for n in lista if n["id"] == id_)


def montar_slide_a() -> str:
    s = Slide()
    r, run, par = Slide, Slide.run, Slide.para
    X0, W_CARD, GAP = 2.0, 3.5, 0.2
    # --- rótulos de faixa, à esquerda
    y_regra, h_regra = 0.88, 1.04
    y_f, h_f = 2.30, 1.62
    y_hub, h_hub = 4.30, 0.66
    y_ch, h_ch = 5.32, 1.30
    centros = {"R1": y_regra + h_regra / 2, "R2": (y_f + y_hub + h_hub) / 2, "R3": y_ch + h_ch / 2}
    for rot in ROTULOS_A:
        cy = centros[rot["id"]]
        s.circulo(f"A_numero_{rot['id']}", 0.5, cy - 0.34, 0.34, rot["numero"], VERDE_ESCURO, sz=12)
        s.texto(f"A_rotulo_{rot['id']}", 0.28, cy - 0.12, 1.55, 0.5,
                [par([run(rot["texto"], 11, VERDE, b=True, spc=60)], "l")])
    # --- regra: IVS -> faixa
    a1, a2 = _no(NOS_A, "A1"), _no(NOS_A, "A2")
    cx_w = X0 + W_CARD + GAP + W_CARD / 2
    w_faixa = 5.1
    x_faixa = cx_w - w_faixa / 2
    id_a1 = s.forma("A_no_IVS", X0, y_regra, 2.4, h_regra, fill=CLARO, anchor="ctr", ins=(0.14, 0.05, 0.1, 0.05),
                    paras=[par([run(a1["titulo"], 13, VERDE_ESCURO, b=True)], depois=2),
                           par([run(a1["fonte"], 9, VERDE, b=True, spc=40)], depois=2),
                           par([run(a1["texto"], 11, TEXTO)])])
    id_a2 = s.forma("A_no_faixa", x_faixa, y_regra, w_faixa, h_regra, fill=CLARO, anchor="t", ins=(0.14, 0.07, 0.1, 0.05),
                    paras=[par([run(a2["titulo"], 13, VERDE_ESCURO, b=True), run("  ·  " + a2["texto"], 10.5, MUDO)])])
    cw = (w_faixa - 0.28 - 2 * 0.12) / 3
    for k, (faixa, valor) in enumerate(FAIXAS_A):
        s.forma(f"A_faixa_{k + 1}", x_faixa + 0.14 + k * (cw + 0.12), y_regra + 0.46, cw, 0.5, adj=14000, fill=BRANCO, line=LINHA,
                ins=(0.03, 0.02, 0.03, 0.02),
                paras=[par([run(faixa, 10.5, TEXTO)], "ctr"), par([run(valor, 11.5, VERDE_ESCURO, b=True)], "ctr")])
    s.seta("A_seta_IVS_faixa", X0 + 2.4, y_regra + h_regra / 2, x_faixa, y_regra + h_regra / 2, de=(id_a1, 3), para=(id_a2, 1))
    # --- forças: custo geográfico | bolsa | custo laboral
    pos = {"A4": X0, "A3": X0 + W_CARD + GAP, "A5": X0 + 2 * (W_CARD + GAP)}
    ids_f = {}
    for nid, x in pos.items():
        n = _no(NOS_A, nid)
        a_favor = n["papel"] == "forca_a_favor"
        fill = VERDE if a_favor else CLARO
        c_tit, c_txt, c_fonte = (BRANCO, BRANCO, PILULA_VERDE) if a_favor else (VERDE_ESCURO, TEXTO, VERDE)
        ids_f[nid] = s.forma(f"A_no_{nid}", x, y_f, W_CARD, h_f, fill=fill, anchor="t", ins=(0.16, 0.5, 0.14, 0.05),
                             paras=[par([run(n["titulo"], 13, c_tit, b=True)], depois=3),
                                    par([run(n["fonte"], 9, c_fonte, b=True, spc=40)], depois=3),
                                    par([run(n["texto"], 11, c_txt)])])
        s.pilula(f"A_pilula_{nid}", x + 0.16, y_f + 0.14, 1.45, 0.24, n["pilula"],
                 PILULA_VERDE if a_favor else PILULA_ROSA, VERDE if a_favor else TEXTO)
    s.seta("A_seta_faixa_bolsa", cx_w, y_regra + h_regra, cx_w, y_f, de=(id_a2, 2), para=(ids_f["A3"], 0))
    # --- hub: valor da vaga
    a6 = _no(NOS_A, "A6")
    id_hub = s.forma("A_no_A6", X0, y_hub, 3 * W_CARD + 2 * GAP, h_hub, fill=VERDE_ESCURO, anchor="ctr", ins=(0.2, 0.04, 0.2, 0.04),
                     paras=[par([run(a6["titulo"], 14, BRANCO, b=True), run("   ·   " + a6["texto"], 12, BRANCO)], "ctr", depois=0),
                            par([run(a6["fonte"], 9, PILULA_VERDE, b=True, spc=40)], "ctr")])
    for nid in ("A4", "A3", "A5"):
        x = pos[nid] + W_CARD / 2
        cor = VERDE if nid == "A3" else VERMELHO
        s.seta(f"A_seta_{nid}_A6", x, y_f + h_f, x, y_hub, cor=cor, larg=2.25, de=(ids_f[nid], 2), para=None)
    # --- cadeia: agregação e elos da política
    larg = [2.3, 2.3, 1.85, 1.85, 1.85]
    g_n = 0.22
    xs = [X0 + sum(larg[:k]) + k * g_n for k in range(5)]
    ids_c = {}
    cadeia = ["A7", "A8", "A9", "A10", "A11"]
    for k, nid in enumerate(cadeia):
        n = _no(NOS_A, nid)
        agreg = n["papel"] == "agregacao"
        ids_c[nid] = s.forma(f"A_no_{nid}", xs[k], y_ch, larg[k], h_ch, fill=CLARO2 if agreg else CLARO,
                             line=None if agreg else LINHA, anchor="t", ins=(0.14, 0.12, 0.1, 0.05),
                             paras=[par([run(n["titulo"], 12.5, VERDE_ESCURO, b=True)], depois=4),
                                    par([run(n["texto"], 10.5, TEXTO)])])
    s.seta("A_seta_A6_A7", xs[0] + larg[0] / 2, y_hub + h_hub, xs[0] + larg[0] / 2, y_ch, larg=2.25, de=None, para=(ids_c["A7"], 0))
    for k in range(4):
        a, b = cadeia[k], cadeia[k + 1]
        s.seta(f"A_seta_{a}_{b}", xs[k] + larg[k], y_ch + h_ch / 2, xs[k + 1], y_ch + h_ch / 2, de=(ids_c[a], 3), para=(ids_c[b], 1))
    # grupos, embaixo
    y_g = y_ch + h_ch + 0.1
    for gid, (k0, k1) in zip(("G1", "G2"), ((0, 1), (2, 4))):
        g = _no(GRUPOS_A, gid)
        x0, x1 = xs[k0], xs[k1] + larg[k1]
        s.seta(f"A_colchete_{gid}", x0, y_g, x1, y_g, cor=LINHA, larg=1.5, ponta=False)
        s.texto(f"A_grupo_{gid}", x0, y_g + 0.07, x1 - x0, 0.24, [par([run(g["texto"], 9, VERDE, b=True, spc=40)], "l")])
    s.texto("A_nota", X0, 6.98, 10.9, 0.22, [par([run(RODAPE_A, 9.5, MUDO, i=True)], "l")])
    return xml_slide(TITULO_A, NAV_A, s.partes)


# --------------------------------------------------------------------------------------------------
# Slide B: a hipótese e os pontos fracos
# --------------------------------------------------------------------------------------------------

def montar_slide_b() -> str:
    s = Slide()
    run, par = Slide.run, Slide.para
    # faixa da hipótese
    s.forma("B_hipotese", 0.25, 0.88, 12.83, 0.86, fill=VERDE_ESCURO, anchor="ctr", ins=(0.2, 0.05, 0.2, 0.05),
            paras=[par([run(BANNER_B_ROTULO, 9.5, PILULA_VERDE, b=True, spc=80)], depois=2),
                   par([run(BANNER_B_TEXTO, 15, BRANCO)])])
    # espinha: 7 passos
    w, g = 1.56, 0.30
    y_n, h_n = 2.42, 1.62
    xs = [0.25 + k * (w + g) for k in range(len(NOS_B))]
    ids = {}
    for k, n in enumerate(NOS_B):
        dest = n["destaque"]
        fill = VERDE if dest else CLARO
        ids[n["id"]] = s.forma(f"B_no_{n['id']}", xs[k], y_n, w, h_n, fill=fill, line=None if dest else LINHA, anchor="t",
                               ins=(0.12, 0.5, 0.1, 0.05),
                               paras=[par([run(n["titulo"], 12, BRANCO if dest else VERDE_ESCURO, b=True)], depois=3),
                                      par([run(n["texto"], 10.5, BRANCO if dest else TEXTO)])])
        s.circulo(f"B_passo_{n['id']}", xs[k] + 0.3, y_n + 0.27, 0.3, n["passo"], PILULA_VERDE if dest else VERDE_ESCURO,
                  cor=VERDE if dest else BRANCO, sz=10.5)
    for k in range(len(NOS_B) - 1):
        a, b = NOS_B[k]["id"], NOS_B[k + 1]["id"]
        s.seta(f"B_seta_{a}_{b}", xs[k] + w, y_n + h_n / 2, xs[k + 1], y_n + h_n / 2, de=(ids[a], 3), para=(ids[b], 1))
    # onde a bolsa age
    k2 = [n["id"] for n in NOS_B].index(next(n["id"] for n in NOS_B if n["destaque"]))
    cx2 = xs[k2] + w / 2
    s.pilula("B_pilula_bolsa", cx2 - 0.95, y_n - 0.4, 1.9, 0.28, PILULA_B, PILULA_VERDE, VERDE, sz=10)
    s.seta("B_seta_pilula", cx2, y_n - 0.12, cx2, y_n, cor=VERDE, larg=2.0, ponta=True)
    # marcadores de aviso nos nós
    for av in AVISOS_B:
        k = [n["id"] for n in NOS_B].index(av["no"])
        s.circulo(f"B_marca_{av['id']}", xs[k] + w - 0.02, y_n + 0.02, 0.32, av["id"], VERMELHO, sz=11)
    # cartões de aviso
    x_br0, x_br1 = xs[k2], xs[k2 + 1] + w
    s.seta("B_colchete_hipotese", x_br0, y_n + h_n + 0.1, x_br1, y_n + h_n + 0.1, cor=VERDE, larg=1.5, ponta=False)
    s.texto("B_rotulo_hipotese", x_br0, y_n + h_n + 0.16, x_br1 - x_br0, 0.22,
            [par([run(ROTULO_HIPOTESE_B, 9.5, VERDE, b=True, spc=40)], "ctr")])
    s.texto("B_cab_avisos", 0.25, 4.62, 8.0, 0.24, [par([run(CABECALHO_AVISOS_B, 11, VERDE, b=True, spc=80)])])
    wc, gc = 4.1, 0.265
    for k, av in enumerate(AVISOS_B):
        x = 0.25 + k * (wc + gc)
        s.forma(f"B_aviso_{av['id']}", x, 4.95, wc, 1.45, fill=CLARO, anchor="t", ins=(0.62, 0.14, 0.16, 0.05),
                paras=[par([run(av["titulo"], 13.5, VERDE_ESCURO, b=True)], depois=5),
                       par([run(av["texto"], 11.5, TEXTO)])])
        s.circulo(f"B_aviso_marca_{av['id']}", x + 0.33, 4.95 + 0.32, 0.34, av["id"], VERMELHO, sz=12)
    # o que o corte identifica
    s.forma("B_identifica", 0.25, 6.52, 12.83, 0.6, fill=CLARO2, anchor="ctr", ins=(0.2, 0.03, 0.2, 0.03),
            paras=[par([run(RODAPE_B_LEAD, 11.5, VERDE_ESCURO, b=True), run(RODAPE_B_TEXTO, 11.5, TEXTO)])])
    return xml_slide(TITULO_B, NAV_B, s.partes)


def xml_notas(texto: str) -> str:
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:cSld><p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/>'
            '<a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Slide Image Placeholder 1"/><p:cNvSpPr><a:spLocks noGrp="1" noRot="1" noChangeAspect="1"/></p:cNvSpPr>'
            '<p:nvPr><p:ph type="sldImg"/></p:nvPr></p:nvSpPr><p:spPr/></p:sp>'
            '<p:sp><p:nvSpPr><p:cNvPr id="3" name="Notes Placeholder 2"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>'
            f'<a:p><a:r><a:rPr lang="pt-BR" dirty="0"/><a:t>{escape(texto)}</a:t></a:r></a:p></p:txBody></p:sp>'
            '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>')


# --------------------------------------------------------------------------------------------------
# Textos do diagrama (para os testes e para o bloco do doc 01)
# --------------------------------------------------------------------------------------------------

def textos_do_diagrama() -> list[str]:
    """Todo texto exibido pelas duas formas do diagrama, uma string por parágrafo, na ordem do XML."""
    achados: list[str] = []
    for xml in (montar_slide_a(), montar_slide_b()):
        for p in re.findall(r"<a:p>(.*?)</a:p>", xml, flags=re.S):
            t = "".join(re.findall(r"<a:t>([^<]*)</a:t>", p))
            if t.strip():
                achados.append(t.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))
    return achados


def _c(txt: str) -> str:
    """Escapa a barra vertical dentro de célula de tabela markdown."""
    return txt.replace("|", "\\|")


def bloco_doc() -> str:
    linhas = [MARCA_INI,
              "<!-- Bloco gerado por scripts/apresentacao/gerar_diagrama_banca_final.py --atualizar-doc. Não editar à mão. -->",
              "",
              "#### Slide A — " + TITULO_A, "",
              "| Caixa | Papel | Pílula | Título exibido | Texto exibido | Fonte exibida na caixa | Equações no apêndice (título do slide) |",
              "|:---:|---|---|---|---|---|---|"]
    for n in NOS_A:
        linhas.append(f"| {n['id']} | {n['papel']} | {n['pilula'] or '—'} | {_c(n['titulo'])} | {_c(n['texto'])} | {n['fonte'] or '—'} | {n['apendice']} |")
    linhas += ["", "Chips da faixa (dentro de A2): " + "; ".join(f"{a} → {b}" for a, b in FAIXAS_A) + ".", "",
               "Rótulos de faixa: " + "; ".join(f"{r['numero']} {r['texto']}" for r in ROTULOS_A) + ". "
               "Rótulos de grupo: " + "; ".join(g["texto"] for g in GRUPOS_A) + ".", "",
               "| Seta | O que ela diz | Literatura |", "|:---:|---|---|"]
    for de, para, diz, lit in SETAS_A:
        linhas.append(f"| {de} → {para} | {diz} | {lit} |")
    linhas += ["", "#### Slide B — " + TITULO_B, "",
               f"Faixa da hipótese ({BANNER_B_ROTULO}): {BANNER_B_TEXTO}", "",
               "| Passo | Caixa | Título exibido | Texto exibido | Aviso |", "|:---:|:---:|---|---|:---:|"]
    for n in NOS_B:
        linhas.append(f"| {n['passo']} | {n['id']} | {n['titulo']}{' (destaque: ' + PILULA_B + ')' if n['destaque'] else ''} | {n['texto']} | {n['aviso'] or '—'} |")
    linhas += ["", f"Colchete sob os passos 2 e 3: {ROTULO_HIPOTESE_B}. Etiqueta sobre o passo 2: {PILULA_B}.", "",
               f"Cabeçalho dos avisos: {CABECALHO_AVISOS_B}.", "",
               "| Aviso | Caixa marcada | Título exibido | Texto exibido | Base |", "|:---:|:---:|---|---|---|"]
    for av in AVISOS_B:
        linhas.append(f"| {av['id']} | {av['no']} | {av['titulo']} | {av['texto']} | {av['fonte']} |")
    linhas += ["", f"Faixa final: {RODAPE_B_LEAD}{RODAPE_B_TEXTO}", "", f"Nota do slide A: {RODAPE_A}", "",
               MARCA_FIM]
    return "\n".join(linhas)


def atualizar_doc() -> None:
    txt = DOC01.read_text(encoding="utf-8")
    i, j = txt.index(MARCA_INI), txt.index(MARCA_FIM) + len(MARCA_FIM)
    DOC01.write_text(txt[:i] + bloco_doc() + txt[j:], encoding="utf-8")


# --------------------------------------------------------------------------------------------------
# Empacotamento do pptx
# --------------------------------------------------------------------------------------------------

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_arq(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


class Pacote:
    """Zip do deck em memória: partes por nome, ordem preservada, escrita com data fixa."""

    def __init__(self, caminho: Path) -> None:
        with zipfile.ZipFile(caminho) as z:
            self.ordem = [i.filename for i in z.infolist()]
            self.partes = {n: z.read(n) for n in self.ordem}

    def texto(self, nome: str) -> str:
        return self.partes[nome].decode("utf-8")

    def gravar(self, nome: str, txt: str | bytes) -> None:
        if nome not in self.partes:
            self.ordem.append(nome)
        self.partes[nome] = txt.encode("utf-8") if isinstance(txt, str) else txt

    def salvar(self, caminho: Path, manter: set[str] | None = None) -> None:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as z:
            for n in self.ordem:
                if manter is not None and n not in manter:
                    continue
                zi = zipfile.ZipInfo(n, DATA_ZIP)
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = 0o644 << 16
                z.writestr(zi, self.partes[n])


def _alvo(origem: str, alvo: str) -> str:
    """Resolve o Target de uma relação para o nome da parte (sem barra inicial)."""
    if alvo.startswith("/"):
        return alvo.lstrip("/")
    base = origem.rsplit("/", 1)[0] if "/" in origem else ""
    partes = (base.split("/") if base else []) + alvo.split("/")
    saida: list[str] = []
    for p in partes:
        if p == "..":
            saida.pop()
        elif p and p != ".":
            saida.append(p)
    return "/".join(saida)


def _rels_de(nome: str) -> str:
    d, _, f = nome.rpartition("/")
    return (d + "/" if d else "") + "_rels/" + f + ".rels"


def alcancaveis(pk: Pacote) -> set[str]:
    visto: set[str] = {"[Content_Types].xml"}
    fila = ["_rels/.rels"]
    while fila:
        rels = fila.pop()
        if rels in visto or rels not in pk.partes:
            continue
        visto.add(rels)
        origem = "" if rels == "_rels/.rels" else rels.replace("/_rels/", "/", 1)[:-5]
        for m in re.finditer(r"<Relationship\b([^>]*)/?>", pk.texto(rels)):
            a = m.group(1)
            if 'TargetMode="External"' in a:
                continue
            alvo = _alvo(origem, re.search(r'Target="([^"]*)"', a).group(1))
            if alvo in pk.partes and alvo not in visto:
                visto.add(alvo)
                fila.append(_rels_de(alvo))
    return visto


def titulo_do_slide(xml: str) -> str:
    m = re.search(r'<p:ph type="title"[^>]*/>.*?</p:sp>', xml, flags=re.S)
    if m:
        return "".join(re.findall(r"<a:t>([^<]*)</a:t>", m.group(0)))
    return "Sumário" if "Sumário" in xml else ("Apêndice" if "Apêndice" in xml else "")


def construir(deck: Path, saida: Path) -> dict:
    pk = Pacote(deck)
    pres = pk.texto("ppt/presentation.xml")
    rels = pk.texto("ppt/_rels/presentation.xml.rels")
    ct = pk.texto("[Content_Types].xml")
    lista = re.search(r"<p:sldIdLst>(.*?)</p:sldIdLst>", pres, flags=re.S)
    entradas = re.findall(r'<p:sldId id="(\d+)" r:id="(rId\d+)"/>', lista.group(1))
    rid_alvo = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship Id="(rId\d+)"[^>]*Target="([^"]*)"', rels)}
    orig = [(i, r, "ppt/" + rid_alvo[r]) for i, r in entradas]
    assert len(orig) == 36, f"o deck do grupo tinha 36 slides; este tem {len(orig)}"
    for pos, esperado in TITULOS_ESPERADOS.items():
        achado = titulo_do_slide(pk.texto(orig[pos - 1][2]))
        assert achado == esperado, f"slide {pos}: esperado {esperado!r}, achado {achado!r}"

    # slides novos
    n_slide = max(int(re.search(r"slide(\d+)\.xml", n).group(1)) for n in pk.partes if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
    n_notas = max(int(re.search(r"notesSlide(\d+)\.xml", n).group(1)) for n in pk.partes if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n))
    prox_rid = max(int(r[3:]) for r in rid_alvo) + 1
    prox_id = max(int(i) for i, _ in entradas) + 1
    layout = "slideLayout14.xml"
    assert 'name="1_Title Slide"' in pk.texto("ppt/slideLayouts/" + layout)
    novos: dict[str, tuple[int, str]] = {}
    for k, (chave, xml, notas) in enumerate((("A", montar_slide_a(), NOTAS_A), ("B", montar_slide_b(), NOTAS_B))):
        ns, nn, rid = n_slide + 1 + k, n_notas + 1 + k, f"rId{prox_rid + k}"
        pk.gravar(f"ppt/slides/slide{ns}.xml", xml)
        pk.gravar(f"ppt/slides/_rels/slide{ns}.xml.rels",
                  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/{layout}"/>'
                  f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{nn}.xml"/>'
                  '</Relationships>')
        pk.gravar(f"ppt/notesSlides/notesSlide{nn}.xml", xml_notas(notas))
        pk.gravar(f"ppt/notesSlides/_rels/notesSlide{nn}.xml.rels",
                  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/>'
                  f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/slide{ns}.xml"/>'
                  '</Relationships>')
        rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{ns}.xml"/></Relationships>')
        ct = ct.replace("</Types>",
                        f'<Override PartName="/ppt/slides/slide{ns}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
                        f'<Override PartName="/ppt/notesSlides/notesSlide{nn}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>')
        novos[chave] = (prox_id + k, rid)

    def sld(item) -> str:
        i, r = novos[item] if isinstance(item, str) else orig[item - 1][:2]
        return f'<p:sldId id="{i}" r:id="{r}"/>'

    # slides do apêndice que estavam ocultos passam a aparecer
    for pos in POS_MOSTRAR:
        nome = orig[pos - 1][2]
        pk.gravar(nome, pk.texto(nome).replace(' show="0"', "", 1))

    def com_lista(itens: list, rels_txt: str) -> tuple[str, str]:
        nova = "<p:sldIdLst>" + "".join(sld(i) for i in itens) + "</p:sldIdLst>"
        return re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", lambda _m: nova, pres, count=1, flags=re.S), rels_txt

    # (b) deck reorganizado
    pres_b, _ = com_lista(NOVOS_NA_ORDEM, rels)
    pk.gravar("ppt/presentation.xml", pres_b)
    pk.gravar("ppt/_rels/presentation.xml.rels", rels)
    pk.gravar("[Content_Types].xml", ct)
    saida.mkdir(parents=True, exist_ok=True)
    pk.salvar(saida / ARQ_DECK)

    # (a) só os dois slides novos: tira as relações dos demais e poda o que ficou sem referência
    manter_rids = {novos["A"][1], novos["B"][1]}
    rels_a = re.sub(r'<Relationship Id="(rId\d+)" Type="[^"]*/relationships/slide" Target="slides/[^"]*"/>',
                    lambda m: m.group(0) if m.group(1) in manter_rids else "", rels)
    pres_a, _ = com_lista(["A", "B"], rels_a)
    pk.gravar("ppt/presentation.xml", pres_a)
    pk.gravar("ppt/_rels/presentation.xml.rels", rels_a)
    manter = alcancaveis(pk)
    ct_a = re.sub(r'<Override PartName="/([^"]+)"[^>]*/>',
                  lambda m: m.group(0) if m.group(1) in manter or m.group(1) not in pk.partes else "", ct)
    pk.gravar("[Content_Types].xml", ct_a)
    pk.salvar(saida / ARQ_SLIDES, manter=manter)

    titulos = {i + 1: titulo_do_slide(pk.texto(nome)) for i, (_, _, nome) in enumerate(orig)}
    ordem = []
    for novo, item in enumerate(NOVOS_NA_ORDEM, 1):
        if isinstance(item, str):
            ordem.append(dict(posicao_nova=novo, origem="novo", titulo=TITULO_A if item == "A" else TITULO_B))
        else:
            ordem.append(dict(posicao_nova=novo, origem=f"slide {item} do deck do grupo",
                              titulo=titulos[item] or "(sem título)",
                              apendice=item in POS_EQUACOES))
    return dict(ordem=ordem)


def escrever_manifesto(deck: Path, saida: Path, resumo: dict) -> None:
    man = {
        "natureza": "conteúdo teórico (teoria da mudança); nenhum número de resultado",
        "script": "scripts/apresentacao/gerar_diagrama_banca_final.py",
        "regra": "nada estimado; nada lido de data/; só a regra da bolsa (cortes do IVS e valores) e citações aparecem como número",
        "conteudo_canonico": "docs/07_apresentacoes/banca_final/01_diagrama_teoria_mudanca.md",
        "entradas": [{
            "caminho": "deck do grupo (fora do repositório; não é alterado)",
            "nome": deck.name,
            "sha256": sha256_arq(deck),
            "bytes": deck.stat().st_size,
            "papel": "template e deck de partida (36 slides)",
            "data_referencia": DATA_REFERENCIA_DECK,
        }],
        "saidas": [{"caminho": f"output/apresentacao_banca_final/{n}", "sha256": sha256_arq(saida / n),
                    "bytes": (saida / n).stat().st_size} for n in (ARQ_SLIDES, ARQ_DECK)],
        "slides_novos": [{"id": "A", "titulo": TITULO_A, "layout": "1_Title Slide", "formas": "nativas (sp e cxnSp), sem imagem"},
                         {"id": "B", "titulo": TITULO_B, "layout": "1_Title Slide", "formas": "nativas (sp e cxnSp), sem imagem"}],
        "slides_oculto_no_deck_do_grupo_e_exibidos_no_apendice": POS_MOSTRAR,
        "ordem_do_deck_proposto": resumo["ordem"],
    }
    (saida / ARQ_MANIFESTO).write_text(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", type=Path, help="deck do grupo (.pptx); só leitura")
    ap.add_argument("--atualizar-doc", action="store_true", help="regrava o bloco gerado do doc 01")
    a = ap.parse_args(argv)
    if a.atualizar_doc:
        atualizar_doc()
        print(f"bloco regravado em {DOC01.relative_to(ROOT)}")
    if a.deck:
        resumo = construir(a.deck, SAIDA)
        escrever_manifesto(a.deck, SAIDA, resumo)
        for n in (ARQ_SLIDES, ARQ_DECK, ARQ_MANIFESTO):
            print(SAIDA.relative_to(ROOT) / n, (SAIDA / n).stat().st_size)
    elif not a.atualizar_doc:
        ap.error("informe --deck e/ou --atualizar-doc")
    return 0


if __name__ == "__main__":
    sys.exit(main())
