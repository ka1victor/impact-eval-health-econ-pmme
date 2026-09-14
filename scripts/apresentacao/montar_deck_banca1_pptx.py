# -*- coding: utf-8 -*-
"""Monta o deck .pptx da banca 1 sobre o template desenhado pelo autor.

Entrada  : docs/07_apresentacoes/banca1/deck_pptx/base_modelo_economico.pptx
Conteudo : docs/07_apresentacoes/banca1/02_conteudo_slides.md (fonte de verdade)
Saida    : output/apresentacao_banca1/deck_banca1_modelo_economico.pptx

O template traz a identidade visual, os slides de sumario, os tres slides de
equacao da literatura e dois gabaritos de modelo preenchidos com "X". Este
script preserva o desenho e substitui o conteudo, seguindo a estrutura pedida
pelo autor em 14/09/2026:

  Motivacao   problema em figuras, politica enxuta na oferta, efeito em serie
              temporal por faixa como prenuncio da pergunta
  Pergunta    mantida como esta no template
  Teoria      uma primitiva por slide, com um segundo slide de custo laboral
  Modelo      juncao das tres, remuneracao alem da bolsa, e o IVS no custo
  Hipotese    um slide, com derivacao e enunciado
  Viabilidade dados disponiveis e onde procurar variacao exogena

As figuras vem de output/ e sao produzidas por script versionado; nenhuma
figura e desenhada fora do pipeline. As equacoes novas sao renderizadas em
LaTeX para PNG porque o OMML nativo do template nao e verificavel neste
ambiente: so o que este script escreve pode ser conferido no render.
"""

from __future__ import annotations

import copy
import hashlib
import json
import zipfile
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TARGET_MODE as RTM
from pptx.opc.package import _Relationship
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

RAIZ = Path(__file__).resolve().parents[2]
BASE = RAIZ / "docs" / "07_apresentacoes" / "banca1" / "deck_pptx" / "base_modelo_economico.pptx"
SAIDA_DIR = RAIZ / "output" / "apresentacao_banca1"
SAIDA = SAIDA_DIR / "deck_banca1_modelo_economico.pptx"
EQ_DIR = SAIDA_DIR / "equacoes"
FIGURAS = SAIDA_DIR

# Paleta lida do proprio template (ppt/slides/*.xml).
VERDE_ESCURO = RGBColor(0x11, 0x47, 0x19)
VERDE_NOITE = RGBColor(0x18, 0x40, 0x1E)
VERDE = RGBColor(0x05, 0x64, 0x29)
VERDE_MEDIO = RGBColor(0x80, 0xB2, 0x81)
VERDE_CLARO = RGBColor(0xBF, 0xD5, 0xC6)
FUNDO_VERDE = RGBColor(0xEF, 0xF4, 0xF0)
FUNDO_CINZA = RGBColor(0xF2, 0xF2, 0xF2)
TINTA = RGBColor(0x3A, 0x3A, 0x3A)
CINZA = RGBColor(0x7F, 0x7F, 0x7F)
BRANCO = RGBColor(0xFF, 0xFF, 0xFF)

FONTE = "Montserrat"

# Cor das equacoes em LaTeX, igual a VERDE_ESCURO.
EQ_COR = "#114719"

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


# --------------------------------------------------------------------------
# equacoes em LaTeX
# --------------------------------------------------------------------------

_EQ_CACHE: dict[str, Path] = {}


def equacao(nome: str, latex: str, *, pt: int = 18, cor: str = EQ_COR) -> Path:
    """Renderiza `latex` em PNG transparente e devolve o caminho.

    Usa LaTeX de verdade (nao o mathtext) porque o conteudo precisa de
    \\underbrace, \\operatorname e ambientes de alinhamento.
    """
    destino = EQ_DIR / f"{nome}.png"
    _EQ_CACHE[nome] = destino
    import matplotlib

    matplotlib.use("Agg")
    matplotlib.rcParams["text.usetex"] = True
    matplotlib.rcParams["text.latex.preamble"] = (
        r"\usepackage{amsmath}\usepackage{amssymb}\usepackage[T1]{fontenc}"
    )
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, latex, fontsize=pt, color=cor)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=400, transparent=True, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return destino


# --------------------------------------------------------------------------
# manipulacao de slides
# --------------------------------------------------------------------------


def por_nome(slide, nome: str):
    """Devolve a primeira forma cujo nome e `nome`, ou None."""
    for shape in slide.shapes:
        if shape.name == nome:
            return shape
    return None


def apagar(slide, *nomes: str) -> None:
    for nome in nomes:
        shape = por_nome(slide, nome)
        while shape is not None:
            shape._element.getparent().remove(shape._element)
            shape = por_nome(slide, nome)


def limpar(slide, manter: set[str]) -> None:
    """Remove todas as formas cujo nome nao esteja em `manter`."""
    for shape in list(slide.shapes):
        if shape.name not in manter:
            shape._element.getparent().remove(shape._element)


def duplicar(prs, indice: int):
    """Copia o slide `indice` para o fim da apresentacao, com suas relacoes."""
    origem = prs.slides[indice]
    destino = prs.slides.add_slide(origem.slide_layout)
    for shape in list(destino.shapes):
        shape._element.getparent().remove(shape._element)
    # Copia os filhos crus da arvore de formas, e nao `slide.shapes`: o
    # equacionamento OMML do template mora dentro de mc:AlternateContent, que a
    # iteracao de alto nivel do python-pptx nao enxerga e perderia na copia.
    origem_tree = origem.shapes._spTree
    destino_tree = destino.shapes._spTree
    for filho in origem_tree:
        marca = etree.QName(filho).localname
        if marca in ("nvGrpSpPr", "grpSpPr"):
            continue
        destino_tree.append(copy.deepcopy(filho))
    for rid, rel in origem.part.rels.items():
        if rel.reltype.endswith("slideLayout"):
            continue
        if rid in destino.part.rels:
            continue
        # Escreve direto no dicionario de relacoes: a API publica sorteia um rId
        # novo, e o XML copiado ja referencia o rId da origem.
        destino.part.rels._rels[rid] = _Relationship(
            destino.part.rels._base_uri,
            rid,
            rel.reltype,
            target_mode=RTM.EXTERNAL if rel.is_external else RTM.INTERNAL,
            target=rel.target_ref if rel.is_external else rel.target_part,
        )
    return destino


def apagar_equacoes(slide, *nomes: str) -> int:
    """Remove blocos mc:AlternateContent, que e onde o template guarda o OMML.

    Sem `nomes`, remove todos. Com `nomes`, remove so os blocos cuja forma tem
    aquele nome - o que permite apagar as equacoes-marcador "X" do gabarito sem
    perder a equacao principal do slide. `slide.shapes` nao enxerga esses
    blocos, entao remover por nome de forma nao alcancaria nenhum deles.
    """
    tree = slide.shapes._spTree
    removidos = 0
    for filho in list(tree):
        if etree.QName(filho).localname != "AlternateContent":
            continue
        if nomes:
            bruto = etree.tostring(filho, encoding="unicode")
            if not any(f'name="{nome}"' in bruto for nome in nomes):
                continue
        tree.remove(filho)
        removidos += 1
    return removidos


def reordenar(prs, ordem: list[int]) -> None:
    """Reordena os slides. `ordem` traz os indices originais na ordem final."""
    lst = prs.slides._sldIdLst
    ids = list(lst)
    for elem in ids:
        lst.remove(elem)
    for i in ordem:
        lst.append(ids[i])


# --------------------------------------------------------------------------
# desenho
# --------------------------------------------------------------------------


def _aplicar(run, props: dict) -> None:
    fonte = run.font
    fonte.name = props.get("fonte", FONTE)
    fonte.size = Pt(props.get("sz", 11))
    fonte.bold = props.get("b", False)
    fonte.italic = props.get("i", False)
    fonte.color.rgb = props.get("cor", TINTA)


def _sem_marcador(paragrafo) -> None:
    ppr = paragrafo._p.get_or_add_pPr()
    ppr.append(etree.SubElement(ppr, f"{{{A}}}buNone"))


def _marcador(paragrafo, char: str, cor: RGBColor) -> None:
    ppr = paragrafo._p.get_or_add_pPr()
    ppr.set("indent", "-171450")
    ppr.set("marL", "171450")
    cor_el = etree.SubElement(ppr, f"{{{A}}}buClr")
    srgb = etree.SubElement(cor_el, f"{{{A}}}srgbClr")
    srgb.set("val", str(cor))
    tam = etree.SubElement(ppr, f"{{{A}}}buSzPct")
    tam.set("val", "90000")
    fonte = etree.SubElement(ppr, f"{{{A}}}buFont")
    fonte.set("typeface", "Arial")
    bu = etree.SubElement(ppr, f"{{{A}}}buChar")
    bu.set("char", char)


def caixa(slide, l, t, w, h, linhas, *, fundo=None, borda=None, borda_pt=1.0,
          anchor=MSO_ANCHOR.TOP, margem=0.06, nome=None, autoajuste=False):
    """Cria um retangulo com texto. `linhas` e uma lista de paragrafos.

    Cada paragrafo e um dict: `t` (texto simples) ou `runs` (lista de tuplas
    (texto, props)), mais `align`, `antes`, `depois`, `entrelinhas`, `bullet`.
    """
    shape = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    if nome:
        shape.name = nome
    if fundo is not None:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fundo
    else:
        shape.fill.background()
    if borda is not None:
        shape.line.color.rgb = borda
        shape.line.width = Pt(borda_pt)
    else:
        shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(margem)
    tf.margin_right = Inches(margem)
    tf.margin_top = Inches(margem * 0.7)
    tf.margin_bottom = Inches(margem * 0.7)
    if autoajuste:
        from pptx.enum.text import MSO_AUTO_SIZE

        tf.auto_size = MSO_AUTO_SIZE.NONE
    for i, linha in enumerate(linhas):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = linha.get("align", PP_ALIGN.LEFT)
        if "antes" in linha:
            p.space_before = Pt(linha["antes"])
        if "depois" in linha:
            p.space_after = Pt(linha["depois"])
        if "entrelinhas" in linha:
            p.line_spacing = linha["entrelinhas"]
        if linha.get("bullet"):
            _marcador(p, linha["bullet"], linha.get("bullet_cor", VERDE_MEDIO))
        else:
            _sem_marcador(p)
        runs = linha.get("runs")
        if runs is None:
            runs = [(linha.get("t", ""), linha)]
        for texto, props in runs:
            if texto == "":
                continue
            run = p.add_run()
            run.text = texto
            _aplicar(run, props)
    return shape


def faixa(slide, l, t, w, h, texto, *, fundo=VERDE_ESCURO, cor=BRANCO, sz=11,
          b=True, align=PP_ALIGN.LEFT, nome=None):
    """Barra de titulo de bloco, no estilo dos cabecalhos do template."""
    return caixa(
        slide, l, t, w, h,
        [{"t": texto, "sz": sz, "b": b, "cor": cor, "align": align}],
        fundo=fundo, anchor=MSO_ANCHOR.MIDDLE, nome=nome, margem=0.08,
    )


def rotulo(slide, l, t, w, texto, *, sz=10, cor=VERDE, b=True, align=PP_ALIGN.LEFT):
    """Rotulo de secao em versalete, como 'O QUE CADA TERMO SIGNIFICA'."""
    return caixa(
        slide, l, t, w, 0.24,
        [{"t": texto.upper(), "sz": sz, "b": b, "cor": cor, "align": align,
          "entrelinhas": 1.0}],
        margem=0.0,
    )


def regua(slide, l, t, w, *, cor=VERDE_MEDIO, pt=1.25):
    """Linha horizontal fina, usada sob os rotulos de secao."""
    from pptx.enum.shapes import MSO_CONNECTOR

    linha = slide.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(l), Inches(t), Inches(l + w), Inches(t)
    )
    linha.line.color.rgb = cor
    linha.line.width = Pt(pt)
    return linha


def figura(slide, caminho: Path, l, t, *, w=None, h=None):
    if not Path(caminho).exists():
        raise FileNotFoundError(caminho)
    kwargs = {}
    if w is not None:
        kwargs["width"] = Inches(w)
    if h is not None:
        kwargs["height"] = Inches(h)
    return slide.shapes.add_picture(str(caminho), Inches(l), Inches(t), **kwargs)


def eq_figura(slide, nome, latex, l, t, *, w=None, pt=18, cor=EQ_COR, centro=None):
    """Insere uma equacao renderizada. `centro` centraliza horizontalmente em x."""
    caminho = equacao(nome, latex, pt=pt, cor=cor)
    pic = figura(slide, caminho, l, t, w=w)
    if centro is not None:
        pic.left = Inches(centro) - pic.width // 2
    return pic


def definir_texto(shape, texto: str, *, sz=None, cor=None, b=None):
    """Troca o texto de uma forma do gabarito preservando a formatação do
    primeiro run, e apagando os demais runs e parágrafos.

    Trocar apenas `runs[0].text` deixaria o resto do texto antigo no slide.
    """
    tf = shape.text_frame
    for extra in list(tf.paragraphs)[1:]:
        extra._p.getparent().remove(extra._p)
    paragrafo = tf.paragraphs[0]
    runs = list(paragrafo.runs)
    if not runs:
        run = paragrafo.add_run()
    else:
        run = runs[0]
        for sobra in runs[1:]:
            sobra._r.getparent().remove(sobra._r)
    run.text = texto
    if sz is not None:
        run.font.size = Pt(sz)
    if cor is not None:
        run.font.color.rgb = cor
    if b is not None:
        run.font.bold = b
    return run


def titulo(slide, texto: str) -> None:
    shape = por_nome(slide, "Title 2")
    if shape is None:
        for candidato in slide.shapes:
            if candidato.name.startswith("Title"):
                shape = candidato
                break
    definir_texto(shape, texto)


def fonte_rodape(slide, texto: str, *, t=7.02, sz=7, l=0.14, w=12.9):
    return caixa(
        slide, l, t, w, 0.24,
        [{"t": texto, "sz": sz, "cor": CINZA, "i": True, "entrelinhas": 1.0}],
        margem=0.0,
    )


def remover(prs, indice: int) -> None:
    """Retira o slide da apresentacao e solta sua relacao."""
    lst = prs.slides._sldIdLst
    elem = list(lst)[indice]
    prs.part.drop_rel(elem.get(f"{{{R}}}id"))
    lst.remove(elem)


# --------------------------------------------------------------------------
# 1. Motivação
# --------------------------------------------------------------------------

FONTE_PROBLEMA = (
    "Fontes: Scheffer, M. (coord.). Demografia Médica no Brasil 2025 (FMUSP/AMB), dez/2024; "
    "IBGE, Regiões de Influência das Cidades — REGIC 2018; Portaria GM/MS nº 7.061/2025, que "
    "reconheceu situação de urgência em saúde pública na atenção especializada, por 24 meses. "
    "O painel da esquerda traz apenas as quatro unidades da federação que a fonte reporta; "
    "o da direita mede o custo do paciente, não o do médico."
)


def slide_problema(slide) -> None:
    """Mantém os dois gráficos e as manchetes; acrescenta o rastreio da fonte."""
    titulo(slide, "A escassez de especialistas não é de número, é de lugar")

    # Os dois gráficos nativos do template saem. O de especialistas por UF
    # trazia catorze barras interpoladas e duas que contradiziam a fonte do
    # projeto (São Paulo em 414 e Pará em 145, contra 244 e 70 conferidos).
    # Entram figuras de arquivo versionado, com fonte declarada.
    apagar(slide, "Chart 14", "Chart 11")
    figura(slide, FIGURAS / "especialistas_extremos_uf.png", 0.10, 1.44, w=5.98)
    # Esta figura é mais alta que a da esquerda: casa-se pela altura, para não
    # invadir a manchete logo abaixo, e centra-se no painel.
    deslocamento = figura(
        slide, RAIZ / "docs" / "07_apresentacoes" / "banca1" / "figuras"
        / "deslocamento_por_regiao.png", 6.80, 1.46, h=2.32)
    deslocamento.left = Inches(9.79) - deslocamento.width // 2

    definir_texto(por_nome(slide, "Text Placeholder 4"),
                  "Especialistas por 100 mil habitantes, por UF — 2024")
    definir_texto(por_nome(slide, "Text Placeholder 10"),
                  "Deslocamento médio da população para serviços de alta "
                  "complexidade (km)")

    # A manchete de baixo sobe para abrir espaço à linha de fontes.
    por_nome(slide, "Imagem 17").top = Inches(5.76)
    fonte_rodape(slide, FONTE_PROBLEMA)


def slide_politica(slide) -> None:
    """A política pelo que a pergunta usa: a oferta de vagas e a regra da bolsa."""
    titulo(slide, "A bolsa do PMM-E é fixada por regra territorial")
    # O gráfico de distribuição dos especialistas passa ao slide de efeito.
    apagar(slide, "Chart 12", "Text Placeholder 7", "Text Placeholder 8",
           "Text Placeholder 5", "Text Placeholder 6", "Imagem 9", "Imagem 10")

    # coluna da esquerda: o desenho do programa
    rotulo(slide, 0.14, 0.80, 6.2, "O que o programa é")
    regua(slide, 0.14, 1.04, 6.2)
    caixa(
        slide, 0.10, 1.10, 6.3, 1.68,
        [
            {"runs": [("Bolsa-formação mensal", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                      (" do Ministério da Saúde. Não é emprego nem concurso: não há vínculo.",
                       {"sz": 10.5})],
             "bullet": "•", "depois": 5, "entrelinhas": 0.95},
            {"runs": [("Aprimoramento em serviço de 12 meses", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                      (", 20 horas semanais em estabelecimento do SUS, com supervisão de "
                       "instituição formadora.", {"sz": 10.5})],
             "bullet": "•", "depois": 5, "entrelinhas": 0.95},
            {"runs": [("16 cursos de especialidade", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                      (", concentrados no câncer e no diagnóstico que o SUS mais espera.",
                       {"sz": 10.5})],
             "bullet": "•", "depois": 5, "entrelinhas": 0.95},
            {"runs": [("O serviço não pode substituir", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                      (" profissional já contratado: a vaga é acréscimo, não troca.", {"sz": 10.5})],
             "bullet": "•", "entrelinhas": 0.95},
        ],
    )

    rotulo(slide, 0.14, 2.92, 6.2, "Como a vaga chega ao médico")
    regua(slide, 0.14, 3.16, 6.2)
    passos = [
        ("1", "Estado ou município indica serviço e especialidade; a comissão bipartite prioriza."),
        ("2", "O Ministério publica o quadro de vagas: município, estabelecimento, curso e "
              "faixa de bolsa."),
        ("3", "O médico escolhe até dois locais, em ordem de preferência, e é classificado "
              "por titulação e tempo de formação."),
    ]
    topo = 3.28
    for numero, texto in passos:
        caixa(slide, 0.14, topo, 0.34, 0.34,
              [{"t": numero, "sz": 11, "b": True, "cor": BRANCO, "align": PP_ALIGN.CENTER}],
              fundo=VERDE_ESCURO, anchor=MSO_ANCHOR.MIDDLE, margem=0.0)
        caixa(slide, 0.54, topo - 0.05, 5.9, 0.62,
              [{"t": texto, "sz": 10.5, "entrelinhas": 0.95}], margem=0.04)
        topo += 0.68

    # coluna da direita: a regra do valor
    rotulo(slide, 6.90, 0.80, 6.2, "O que determina o valor da bolsa")
    regua(slide, 6.90, 1.04, 6.2)
    caixa(
        slide, 6.86, 1.10, 6.3, 0.96,
        [
            {"runs": [("A faixa vem do IVS do município", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                      (" — índice do Ipea que resume, de 0 a 1, infraestrutura urbana, "
                       "capital humano, e renda e trabalho.", {"sz": 10.5})],
             "depois": 4, "entrelinhas": 0.95},
            {"t": "O edital de 2025 agrupa as cinco categorias do índice em três faixas de valor.",
             "sz": 10.5, "entrelinhas": 0.95},
        ], margem=0.04,
    )
    # Mesmo conteúdo do gráfico nativo, mas lido do pipeline.
    apagar(slide, "Chart 17")
    figura(slide, FIGURAS / "bolsa_por_faixa.png", 6.98, 2.18, w=6.00)

    caixa(
        slide, 6.90, 5.30, 6.15, 0.72,
        [{"runs": [("No ciclo 1:  ", {"sz": 10, "cor": CINZA}),
                   ("102", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                   (" municípios na Faixa 1,  ", {"sz": 10}),
                   ("107", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                   (" na Faixa 2,  ", {"sz": 10}),
                   ("159", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                   (" na Faixa 3.", {"sz": 10})],
          "align": PP_ALIGN.CENTER, "entrelinhas": 0.95}],
        fundo=FUNDO_VERDE, anchor=MSO_ANCHOR.MIDDLE, margem=0.06,
    )

    caixa(
        slide, 0.14, 6.20, 12.9, 0.68,
        [{"runs": [("O valor não depende da especialidade, da carga horária nem do que o médico "
                    "produz. ", {"sz": 11.5, "b": True, "cor": VERDE_ESCURO}),
                   ("Depende de onde fica o município — e é essa regra, e só ela, que o "
                    "trabalho estuda.", {"sz": 11.5, "cor": TINTA})],
          "entrelinhas": 0.95}],
        fundo=FUNDO_VERDE, borda=VERDE_MEDIO, borda_pt=1.25,
        anchor=MSO_ANCHOR.MIDDLE, margem=0.12,
    )

    fonte_rodape(
        slide,
        "Fontes: Lei nº 15.233/2025, art. 22-D; Portaria GM/MS nº 7.177/2025; Edital SGTES/MS "
        "nº 3/2025 (DOU 24/07/2025), itens 1, 3–5, 10 e 11; quadro de vagas do ciclo 1, chamada 1 "
        "— 1.295 vagas estabelecimento–curso em 460 estabelecimentos e 368 municípios.",
    )


def slide_efeito(slide) -> None:
    """A série por faixa, o que ela pode significar, e o prenúncio da pergunta."""
    titulo(slide, "A presença de especialistas cresceu nas três faixas")
    apagar_equacoes(slide)
    limpar(slide, {"Title 2", "Text Placeholder 1"})

    figura(slide, FIGURAS / "oferta_antes_depois_por_faixa.png", 0.10, 1.22, w=8.72)

    blocos = [
        ("O que o gráfico mostra", [
            "As três faixas sobem a partir da publicação da oferta. A Faixa 1, de R$ 20 mil, "
            "vai de 17,4 a 22,0 especialistas por 100 mil habitantes.",
            "A distância entre a Faixa 1 e as outras duas aumenta depois da homologação.",
        ]),
        ("O que isso pode significar", [
            "Que a bolsa maior atraiu profissionais para onde ela é maior.",
            "Ou que as três faixas seguem uma tendência comum — do programa, do mercado ou do "
            "próprio cadastro — e o degrau apenas a acompanha.",
            "Não há município fora do programa para comparar: todos os 368 receberam vaga.",
        ]),
    ]
    topo = 1.00
    for cabecalho, itens in blocos:
        rotulo(slide, 9.02, topo, 4.05, cabecalho)
        regua(slide, 9.02, topo + 0.24, 4.05)
        linhas = [{"t": item, "sz": 10, "bullet": "•", "depois": 5, "entrelinhas": 0.95}
                  for item in itens]
        altura = 0.30 + 0.46 * len(itens) + 0.22 * sum(len(i) > 110 for i in itens)
        caixa(slide, 8.98, topo + 0.30, 4.15, altura, linhas)
        topo += 0.36 + altura

    rotulo(slide, 9.02, topo, 4.05, "O que queremos entender", cor=VERDE_ESCURO)
    regua(slide, 9.02, topo + 0.24, 4.05, cor=VERDE_ESCURO)
    caixa(
        slide, 8.98, topo + 0.32, 4.15, 1.18,
        [{"runs": [("Quanto desse crescimento é o ", {"sz": 10.5}),
                   ("preço", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                   (" que a política pôs sobre a vulnerabilidade — e quanto é o ", {"sz": 10.5}),
                   ("lugar", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                   (" que esse preço deveria compensar.", {"sz": 10.5})],
          "entrelinhas": 0.95}],
        fundo=FUNDO_VERDE, borda=VERDE_MEDIO, borda_pt=1.25,
        anchor=MSO_ANCHOR.MIDDLE, margem=0.10,
    )

    fonte_rodape(
        slide,
        "Leitura descritiva: sem município fora do programa, a figura não identifica efeito. "
        "Especialistas nos CBOs dos cursos com correspondência unívoca curso–CBO, CNES mensal "
        "jun/2024 a jul/2026; população do Censo 2022 (IBGE); faixa pela bolsa publicada na vaga.",
    )


# --------------------------------------------------------------------------
# 3. Literatura teórica — segundo slide de custo laboral
# --------------------------------------------------------------------------


def slide_equipe_e_capital(slide) -> None:
    """Equipe e capital no custo laboral: a curva em U e os dois canais."""
    apagar_equacoes(slide)
    titulo(slide, "Equipe e capital entram duas vezes no custo de atender")
    definir_texto(por_nome(slide, "kicker"),
                  "CHONÉ & MA (2011), §2.3;  REINHARDT (1972, 1975)")
    apagar(slide, "col1", "col2")

    eq_figura(
        slide, "derivadas_lk",
        r"$\dfrac{\partial C}{\partial K}<0"
        r"\qquad\text{e}\qquad"
        r"\dfrac{\partial B}{\partial K}>0"
        r"\qquad\Longrightarrow\qquad"
        r"\dfrac{\partial c^{\mathrm{laboral}}}{\partial K}<0$",
        0, 1.42, w=7.3, centro=6.67, pt=20,
    )

    definir_texto(por_nome(slide, "h1"), "A CURVA EM U DO CUSTO LÍQUIDO")
    regra1 = por_nome(slide, "rule1")
    regra1.left, regra1.top, regra1.width = Inches(0.56), Inches(2.94), Inches(6.40)
    figura(slide, FIGURAS / "custo_laboral_deck.png", 0.52, 3.02, w=6.20)
    caixa(
        slide, 0.56, 5.62, 6.40, 0.32,
        [{"t": "O custo marginal c′(q) = C′ − αB′ tem sinal incerto; c″ ≫ 0 não tem. Daí o U.",
          "sz": 9.5, "cor": CINZA, "i": True, "entrelinhas": 0.95}],
        margem=0.0,
    )

    definir_texto(por_nome(slide, "h2"), "OS DOIS CANAIS DE EQUIPE E CAPITAL")
    canais = [
        ("CANAL 1 · JÁ ESTÁ EM CHONÉ & MA",
         [("Com equipe de apoio e capital instalado, o mesmo volume de atendimentos ",
           {"sz": 10.5}),
          ("cansa menos", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
          (": leitos, equipamento e pessoal reduzem o esforço de produzir q.", {"sz": 10.5})]),
        ("CANAL 2 · EXTENSÃO DESTE PROJETO",
         [("Sem medicamento, insumo cirúrgico ou maquinário em funcionamento, o atendimento ",
           {"sz": 10.5}),
          ("perde resolutividade", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
          (" — e com ela cai o benefício ao paciente, que é o que move o médico altruísta. "
           "O canal vem da função de produção médica de Reinhardt.", {"sz": 10.5})]),
    ]
    topo = 2.98
    for cabecalho, corpo in canais:
        faixa(slide, 7.08, topo, 5.76, 0.30, cabecalho, sz=9.5)
        caixa(slide, 7.08, topo + 0.32, 5.76, 1.08,
              [{"runs": corpo, "entrelinhas": 0.95}],
              fundo=FUNDO_VERDE, margem=0.10)
        topo += 1.44

    definir_texto(
        por_nome(slide, "cText"),
        "Onde chegamos:  a estrutura do município entra na decisão por dois canais, não "
        "um — e nada disso aparece no valor anunciado da bolsa.",
    )


# --------------------------------------------------------------------------
# 4. Modelo microeconômico
# --------------------------------------------------------------------------

DECOMPOSICAO = (
    r"$c_{im}="
    r"\underbrace{\phi(\mathrm{dist}_{im})-\gamma A_m+\theta_i^{\mathrm{rural}}}"
    r"_{\text{Redding \& Rossi-Hansberg}}"
    r"+\underbrace{C(q;L_m,K_m)-\alpha_i B(q;L_m,K_m)}"
    r"_{\text{Chon\'e \& Ma, com a extens\~ao em }B}$"
)


def _bloco_direita(slide, itens, topos=(4.18, 5.14, 6.13)) -> None:
    """Preenche os três cabeçalhos verdes do gabarito com título e corpo."""
    for (nome, cabecalho, corpo), topo in zip(itens, topos):
        alvo = por_nome(slide, nome)
        definir_texto(alvo, cabecalho, sz=9.5)
        caixa(slide, 7.05, topo + 0.40, 4.66, 0.54,
              [{"t": corpo, "sz": 9.5, "entrelinhas": 0.95, "align": PP_ALIGN.CENTER}],
              anchor=MSO_ANCHOR.TOP, margem=0.08)


def slide_juncao(slide) -> None:
    """A equação do modelo, com o custo aberto pelas outras duas tradições."""
    titulo(slide, "Como juntamos os três")
    apagar_equacoes(slide, "TextBox 26", "TextBox 27")  # marcadores "X" do gabarito
    apagar(slide, "Rectangle 24", "Rectangle 25", "Equals 28", "TextBox 29",
           "TextBox 30", "TextBox 32", "Rectangle 12", "Rectangle 11",
           "Rectangle 34", "Rectangle 35", "Rectangle 36", "TextBox 37",
           "TextBox 38", "Conector reto 19")

    legendas = [
        ("TextBox 21", 1.85, "a escolha é de carreira"),
        ("TextBox 20", 1.85, "a bolsa, deflacionada"),
        ("TextBox 19", 1.85, "o custo de estar ali"),
        ("TextBox 22", 2.45, "m = 0 é ficar fora do programa"),
    ]
    for nome, largura, texto in legendas:
        alvo = por_nome(slide, nome)
        alvo.width = Inches(largura)
        alvo.text_frame.word_wrap = True
        definir_texto(alvo, texto, sz=9.5, cor=VERDE_ESCURO, b=True)
        alvo.text_frame.paragraphs[0].line_spacing = 0.95

    eq_figura(slide, "decomposicao_custo", DECOMPOSICAO, 0, 3.14, w=10.6, centro=6.35, pt=17)

    fontes = [
        ("MOEHLING ET AL. (2020)",
         "o arg max intertemporal, o deflator p e a existência de um custo c"),
        ("REDDING & ROSSI-HANSBERG (2017)",
         "distância, amenidades e custo de moradia, dentro de c"),
        ("CHONÉ & MA (2011), COM REINHARDT",
         "esforço, altruísmo e o papel de equipe e capital, dentro de c"),
    ]
    for x, (cabecalho, corpo) in zip((0.56, 4.84, 9.12), fontes):
        faixa(slide, x, 4.34, 4.05, 0.34, cabecalho, sz=9.5, align=PP_ALIGN.CENTER)
        caixa(slide, x, 4.68, 4.05, 1.06,
              [{"t": corpo, "sz": 10, "align": PP_ALIGN.CENTER, "entrelinhas": 0.95}],
              fundo=FUNDO_VERDE, anchor=MSO_ANCHOR.MIDDLE, margem=0.10)

    caixa(
        slide, 0.56, 5.94, 12.22, 1.00,
        [
            {"runs": [("A decisão.", {"sz": 11, "b": True, "cor": VERDE_ESCURO}),
                      ("  A alternativa m = 0 é ficar fora do programa. A vaga em m é aceita "
                       "quando V(i,m) ≥ V(i,0) e m é a melhor entre as disponíveis; ε(i,m) "
                       "recolhe os gostos que não observamos.", {"sz": 11})],
             "depois": 4, "entrelinhas": 0.95},
            {"runs": [("O que nenhuma das três tem.", {"sz": 11, "b": True, "cor": VERDE_ESCURO}),
                      ("  Nenhuma trata de um componente da remuneração fixado por ", {"sz": 11}),
                      ("regra pública sobre um índice territorial", {"sz": 11, "b": True}),
                      (". É isso, e só isso, que a adaptação ao PMM-E acrescenta.", {"sz": 11})],
             "entrelinhas": 0.95},
        ],
        fundo=FUNDO_VERDE, borda=VERDE_MEDIO, borda_pt=1.25,
        anchor=MSO_ANCHOR.MIDDLE, margem=0.14,
    )

    fonte_rodape(slide, "Fonte: docs/02_teoria/modelo_micro.md, §2.4 e §3.")


def slide_remuneracao(slide) -> None:
    """A remuneração do município vai além da bolsa do PMM-E."""
    titulo(slide, "A remuneração do município vai além da bolsa")
    apagar(slide, "Connector: Elbow 13", "Connector: Elbow 14", "Connector: Elbow 15",
           "Connector: Elbow 16", "TextBox 19", "TextBox 20", "TextBox 21", "TextBox 22",
           "Rectangle 24", "Rectangle 25", "Equals 28", "TextBox 29", "TextBox 30",
           "TextBox 32", "Rectangle 12")
    apagar_equacoes(slide)

    # Neste gabarito a caixa da equação tem fundo verde-escuro: a equação vai em branco.
    eq_figura(
        slide, "remuneracao_total",
        r"$\mathbb{E}\!\left(w_{imt}\mid B_m\right)="
        r"\underbrace{B_m}_{\text{fixada por regra p\'ublica}}"
        r"+\underbrace{w^{\mathrm{priv}}_m}_{\text{mercado local}}$",
        0, 1.22, w=5.6, centro=6.30, pt=18, cor="#FFFFFF",
    )

    # O gabarito deixa o conteúdo na metade de baixo; aqui ele sobe.
    for nome, topo in (("Rectangle 11", 2.82), ("Rectangle 34", 2.78),
                       ("Rectangle 35", 3.74), ("Rectangle 36", 4.73),
                       ("TextBox 38", 2.30)):
        por_nome(slide, nome).top = Inches(topo)
    linha_direita = [f for f in slide.shapes if f.name == "Conector reto 19"][-1]
    linha_direita.top = Inches(2.60)

    alvo = por_nome(slide, "TextBox 37")
    alvo.left, alvo.top, alvo.width = Inches(1.49), Inches(2.30), Inches(4.32)
    definir_texto(alvo, "O mesmo valor, dois lugares")
    linha_esquerda = [f for f in slide.shapes if f.name == "Conector reto 19"][0]
    linha_esquerda.left, linha_esquerda.top = Inches(1.49), Inches(2.60)
    linha_esquerda.width = Inches(4.32)

    lugares = [
        ("CAPITAL OU REGIÃO METROPOLITANA",
         [("Consultório, planos de saúde e hospitais privados sustentam a especialidade "
           "fora das 20 horas do programa: ", {"sz": 10.5}),
          ("w = B + w", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
          ("priv", {"sz": 7, "b": True, "cor": VERDE_ESCURO}),
          (", com a segunda parcela alta.", {"sz": 10.5})]),
        ("INTERIOR ISOLADO",
         [("Não há demanda privada que sustente a especialidade: ", {"sz": 10.5}),
          ("w → B", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
          (". A bolsa é toda a remuneração — e é exatamente ali que a política mais "
           "aposta nela.", {"sz": 10.5})]),
    ]
    topo = 2.78
    for cabecalho, corpo in lugares:
        faixa(slide, 1.49, topo, 4.32, 0.32, cabecalho, sz=9.5)
        caixa(slide, 1.49, topo + 0.34, 4.32, 1.10,
              [{"runs": corpo, "entrelinhas": 0.95}],
              fundo=FUNDO_VERDE, margem=0.10)
        topo += 1.56

    definir_texto(por_nome(slide, "TextBox 38"), "   Desdobramentos")
    _bloco_direita(slide, [
        ("Rectangle 34", "BOLSA MAIOR PODE SER RENDA MENOR",
         "R$ 20 mil sem complemento contra R$ 10 mil mais o consultório da capital"),
        ("Rectangle 35", "A REGRA NÃO OBSERVA O MERCADO LOCAL",
         "a bolsa responde ao IVS, e o IVS não mede demanda privada"),
        ("Rectangle 36", "O DEFLATOR ATUA NO SENTIDO OPOSTO",
         "custo de vida menor no interior valoriza a mesma bolsa em termos reais"),
    ], topos=(2.78, 3.74, 4.73))

    caixa(
        slide, 1.49, 5.96, 10.22, 0.92,
        [{"runs": [("Onde chegamos.", {"sz": 11, "b": True, "cor": VERDE_ESCURO}),
                   ("  A bolsa é a única parcela da remuneração que a regra controla — e, "
                    "onde o mercado privado não sustenta a especialidade, é também a única "
                    "que existe. É ali que a política aposta, e é ali que o custo de estar "
                    "é maior.", {"sz": 11})],
          "entrelinhas": 0.95}],
        fundo=FUNDO_VERDE, borda=VERDE_MEDIO, borda_pt=1.25,
        anchor=MSO_ANCHOR.MIDDLE, margem=0.14,
    )


def slide_ivs(slide) -> None:
    """Como o IVS entra no custo geográfico e no custo laboral."""
    titulo(slide, "O IVS organiza o custo, com um sinal e uma dúvida")
    apagar_equacoes(slide)
    limpar(slide, {"Title 2", "Text Placeholder 1", "Rectangle 17"})
    caixa_eq = por_nome(slide, "Rectangle 17")
    caixa_eq.left, caixa_eq.top = Inches(2.30), Inches(0.86)
    caixa_eq.width, caixa_eq.height = Inches(7.90), Inches(0.74)
    eq_figura(slide, "custo_por_ivs",
              r"$c_{im}=c_0(IVS_m)+\eta_i$", 0, 1.00, w=2.5, centro=6.25, pt=18)

    caixa(
        slide, 0.56, 1.74, 12.22, 0.34,
        [{"t": "Distância da família, aluguel e esforço clínico não são observados. "
               "O IVS é. E cada dimensão do índice corresponde a um bloco do custo.",
          "sz": 11, "align": PP_ALIGN.CENTER, "entrelinhas": 0.95}],
        margem=0.0,
    )

    colunas = [
        (0.56, "CUSTO GEOGRÁFICO  ·  SINAL CONHECIDO", VERDE_ESCURO, [
            ("Infraestrutura urbana",
             "saneamento, coleta de lixo, tempo de deslocamento — é a amenidade Aₘ de "
             "Redding & Rossi-Hansberg. Índice maior, amenidade pior."),
            ("Renda e trabalho",
             "pobreza, desemprego, informalidade — sem renda local não há mercado privado "
             "que sustente a especialidade, e w tende a B."),
        ], "Nas duas dimensões o sentido é o mesmo: IVS maior, custo maior."),
        (6.86, "CUSTO LABORAL  ·  SINAL AMBÍGUO", VERDE, [
            ("Capital humano",
             "mortalidade infantil, analfabetismo, mães adolescentes. Carência sanitária "
             "eleva a gravidade do caso — e com ela o benefício de atender, B′(q) ↑, o que "
             "reduz o custo para um médico altruísta."),
            ("A mesma dimensão, em sentido contrário",
             "carência também sinaliza escassez de equipe L e de capital K, o que eleva "
             "o cansaço C(q)."),
        ], "Os dois efeitos se opõem: o sinal de ∂c laboral/∂IVS é questão empírica."),
    ]
    for x, cabecalho, cor, itens, fecho in colunas:
        faixa(slide, x, 2.16, 5.92, 0.36, cabecalho, fundo=cor, sz=10)
        topo = 2.60
        for rotulo_item, corpo in itens:
            caixa(slide, x, topo, 5.92, 1.10,
                  [{"t": rotulo_item, "sz": 10, "b": True, "cor": VERDE_ESCURO,
                    "depois": 3, "entrelinhas": 0.95},
                   {"t": corpo, "sz": 10, "entrelinhas": 0.95}],
                  fundo=FUNDO_VERDE, margem=0.10)
            topo += 1.22
        caixa(slide, x, topo, 5.92, 0.44,
              [{"t": fecho, "sz": 10, "b": True, "cor": cor, "entrelinhas": 0.95}],
              margem=0.02)

    caixa(
        slide, 0.56, 5.94, 12.22, 0.92,
        [
            {"runs": [("O que não é ambíguo.", {"sz": 11.5, "b": True, "cor": VERDE_ESCURO}),
                      ("  O sinal de ∂c laboral/∂K: mais equipe e mais capital reduzem o custo "
                       "de atender pelos dois canais do slide anterior. O que não sabemos é "
                       "quanto do IVS é falta de K.", {"sz": 11.5})],
             "depois": 4, "entrelinhas": 0.95},
            {"runs": [("É por isso que o objeto do trabalho é o ", {"sz": 11.5}),
                      ("degrau da bolsa entre faixas", {"sz": 11.5, "b": True, "cor": VERDE_ESCURO}),
                      (", e não a inclinação do índice.", {"sz": 11.5})],
             "entrelinhas": 0.95},
        ],
        fundo=FUNDO_VERDE, borda=VERDE_MEDIO, borda_pt=1.25,
        anchor=MSO_ANCHOR.MIDDLE, margem=0.14,
    )


# --------------------------------------------------------------------------
# 5. Hipótese
# --------------------------------------------------------------------------


def slide_hipotese(slide) -> None:
    """Um slide: a derivação e o enunciado."""
    titulo(slide, "Da condição de aceitação sai uma hipótese")
    apagar_equacoes(slide)
    limpar(slide, {"Title 2", "Text Placeholder 1"})

    rotulo(slide, 0.56, 0.84, 6.10, "A derivação")
    regua(slide, 0.56, 1.08, 6.10)

    passos = [
        ("Passo 1 · a condição de aceitação",
         "O médico i aceita a vaga em m quando o que ela vale supera sua melhor "
         "alternativa v̄ᵢ:",
         "condicao_aceitacao",
         r"$\dfrac{B_m+w^{\mathrm{priv}}_m}{p_m}-c_0(IVS_m)\;\geq\;\bar{v}_i$",
         3.0),
        ("Passo 2 · do médico à vaga",
         "A vaga é preenchida se existir ao menos um candidato para quem a desigualdade "
         "vale. Tudo o que aumenta o lado esquerdo aumenta essa probabilidade.",
         None, None, None),
        ("Passo 3 · a derivada que o trabalho testa",
         "",
         "derivada_hipotese",
         r"$\dfrac{\partial\Pr(\text{preenchimento}_m)}"
         r"{\partial\left(B_m/p_m\right)}\;>\;0$",
         3.2),
    ]
    topo = 1.20
    for cabecalho, corpo, nome_eq, latex, largura in passos:
        caixa(slide, 0.52, topo, 6.10, 0.28,
              [{"t": cabecalho, "sz": 10.5, "b": True, "cor": VERDE_ESCURO,
                "entrelinhas": 0.95}], margem=0.04)
        topo += 0.30
        if corpo:
            caixa(slide, 0.52, topo, 6.10, 0.62,
                  [{"t": corpo, "sz": 10.5, "entrelinhas": 0.95}], margem=0.04)
            topo += 0.34 if nome_eq else 0.66
        if nome_eq:
            pic = eq_figura(slide, nome_eq, latex, 0, topo + 0.10, w=largura, centro=3.60, pt=17)
            topo += Emu(pic.height).inches + 0.34

    caixa(
        slide, 0.52, topo + 0.10, 6.10, 1.10,
        [{"runs": [("O custo é obstáculo, não hipótese.", {"sz": 10, "b": True, "cor": VERDE_ESCURO}),
                   ("  Ele não entra como segunda hipótese porque não varia livremente: a regra "
                    "do edital o amarra à bolsa, e os dois sobem juntos. É o que torna a "
                    "hipótese difícil de testar, não uma segunda afirmação a testar.",
                    {"sz": 10})],
          "entrelinhas": 0.95}],
        fundo=FUNDO_CINZA, anchor=MSO_ANCHOR.MIDDLE, margem=0.12,
    )

    faixa(slide, 7.00, 1.20, 5.78, 0.52, "HIPÓTESE ECONÔMICA", sz=14,
          align=PP_ALIGN.CENTER)
    caixa(
        slide, 7.00, 1.72, 5.78, 1.70,
        [{"runs": [("Ceteris paribus", {"sz": 17, "b": True, "i": True, "cor": VERDE_ESCURO}),
                   (", municípios com maior remuneração do PMM-E conseguem atrair mais "
                    "especialistas.", {"sz": 17, "b": True, "cor": VERDE_ESCURO})],
          "entrelinhas": 1.05}],
        fundo=FUNDO_VERDE, borda=VERDE_MEDIO, borda_pt=1.5,
        anchor=MSO_ANCHOR.MIDDLE, margem=0.20,
    )

    rotulo(slide, 7.00, 3.82, 5.78, "O que isso exige na fronteira entre duas faixas")
    regua(slide, 7.00, 4.06, 5.78)
    caixa(
        slide, 6.96, 4.16, 5.86, 0.60,
        [{"t": "Do lado mais vulnerável, o preenchimento exige que o degrau monetário "
               "supere o degrau de custo:", "sz": 10.5, "entrelinhas": 0.95}],
        margem=0.04,
    )
    eq_figura(slide, "degrau_fronteira",
              r"$\dfrac{\Delta B_m}{p_m}>\Delta c_0,"
              r"\qquad \Delta B_m=\mathrm{R\$}\,5.000$",
              0, 4.86, w=4.0, centro=9.89, pt=17)
    caixa(
        slide, 6.96, 5.86, 5.86, 1.06,
        [{"t": "A pergunta da apresentação é se essa desigualdade vale — e o que vem a "
               "seguir é se conseguimos respondê-la com o que existe publicado.",
          "sz": 10.5, "entrelinhas": 0.95}],
        fundo=FUNDO_VERDE, anchor=MSO_ANCHOR.MIDDLE, margem=0.12,
    )


# --------------------------------------------------------------------------
# 6. Viabilidade empírica
# --------------------------------------------------------------------------


def slide_viabilidade(slide) -> None:
    """O que observamos, o que não, e onde procurar variação exógena."""
    titulo(slide, "Temos as peças; falta a variação exógena")
    apagar_equacoes(slide)
    limpar(slide, {"Title 2", "Text Placeholder 1"})

    rotulo(slide, 0.56, 0.84, 6.10, "O que conseguimos medir")
    regua(slide, 0.56, 1.08, 6.10)
    pecas = [
        ("sim", "Preenchimento da vaga",
         "quadro de vagas e resultados do ciclo 1: 1.295 vagas em 368 municípios"),
        ("sim", "Bolsa Bₘ", "o valor anunciado na vaga: R$ 10, 15 ou 20 mil — edital"),
        ("sim", "Custo cₘ",
         "IVS e suas três dimensões (Ipea); capital, metropolitano, interior conectado "
         "ou remoto (REGIC 2018 e RMs 2022); especialistas e estrutura preexistentes "
         "(CNES mensal, jun/2024 a jul/2026)"),
        ("parte", "Custo de vida pₘ", "diferenças entre estados — IBGE"),
        ("nao", "Mercado privado w priv", "não observado"),
        ("nao", "Distância da família", "não observado"),
    ]
    marca = {"sim": ("●", VERDE_ESCURO), "parte": ("◐", VERDE_MEDIO), "nao": ("○", CINZA)}
    topo = 1.18
    for estado, peca, fonte in pecas:
        simbolo, cor = marca[estado]
        altura = 0.72 if len(fonte) > 90 else 0.40
        caixa(slide, 0.52, topo, 0.28, altura,
              [{"t": simbolo, "sz": 11, "cor": cor, "align": PP_ALIGN.CENTER}], margem=0.0)
        caixa(slide, 0.82, topo, 5.84, altura,
              [{"runs": [(peca + " — ", {"sz": 10, "b": True, "cor": VERDE_ESCURO}),
                         (fonte, {"sz": 10, "cor": TINTA if estado != "nao" else CINZA})],
                "entrelinhas": 0.95}], margem=0.02)
        topo += altura + 0.06

    caixa(
        slide, 0.52, topo + 0.06, 6.14, 0.78,
        [{"t": "As duas peças não observadas entram no modelo como parte do custo que o IVS "
               "e a tipologia territorial resumem. Para o essencial, os dados existem.",
          "sz": 10, "entrelinhas": 0.95}],
        fundo=FUNDO_VERDE, anchor=MSO_ANCHOR.MIDDLE, margem=0.12,
    )

    rotulo(slide, 7.00, 0.84, 5.80, "Onde procurar variação exógena")
    regua(slide, 7.00, 1.08, 5.80)
    caixa(
        slide, 6.96, 1.18, 5.88, 0.86,
        [{"runs": [("O edital corta o IVS em categorias, e a categoria fixa a bolsa "
                    "(cláusula 11.1.4). Os cortes de ", {"sz": 10.5}),
                   ("0,400", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                   (" e ", {"sz": 10.5}),
                   ("0,500", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                   (" são o lugar natural de uma regressão descontínua: comparar municípios "
                    "logo acima e logo abaixo.", {"sz": 10.5})],
          "entrelinhas": 0.95}],
        margem=0.04,
    )

    achados = [
        ("Há suporte comum",
         "37 municípios com IVS ≤ 0,400 estão na Faixa 1 e 94 na Faixa 2; os intervalos "
         "das três faixas se sobrepõem. Não falta variação."),
        ("Mas não há descontinuidade onde os cortes estão",
         "em torno de 0,500 os dois lados são 100% Faixa 1 em qualquer janela até ±0,050; "
         "em torno de 0,400 o maior IVS da Faixa 3 é 0,372. O tratamento é localmente "
         "constante nos dois cortes."),
        ("E a variação que sobra não é exógena",
         "dos 83 municípios fora da melhor regra de limiar possível, os 41 promovidos têm "
         "mediana de população de 7.933 contra 32.179 dos 42 rebaixados. Parear por IVS "
         "confunde bolsa com posição territorial."),
    ]
    topo = 2.16
    for i, (cabecalho, corpo) in enumerate(achados, start=1):
        altura = 0.94 if len(corpo) > 130 else 0.74
        caixa(slide, 6.96, topo, 0.30, altura,
              [{"t": str(i), "sz": 10.5, "b": True, "cor": VERDE_ESCURO}], margem=0.02)
        caixa(slide, 7.26, topo, 5.58, altura,
              [{"runs": [(cabecalho + " — ", {"sz": 10, "b": True, "cor": VERDE_ESCURO}),
                         (corpo, {"sz": 10})], "entrelinhas": 0.95}], margem=0.02)
        topo += altura + 0.10

    caixa(
        slide, 6.96, topo + 0.04, 5.88, 1.36,
        [
            {"runs": [("O que destrava.", {"sz": 10.5, "b": True, "cor": VERDE_ESCURO}),
                      ("  A cláusula 11.1.3 manda seguir critérios de localização definidos "
                       "no Anexo IV, que o edital não reproduz. O dado tem a forma das duas "
                       "cláusulas: em 177 dos 368 municípios a faixa publicada está acima da "
                       "categoria de IVS, e em nenhum abaixo. O IVS é o piso da bolsa, "
                       "não o seu critério.", {"sz": 10.5})],
             "entrelinhas": 0.95},
        ],
        fundo=FUNDO_VERDE, borda=VERDE_MEDIO, borda_pt=1.25,
        anchor=MSO_ANCHOR.MIDDLE, margem=0.12,
    )

    fonte_rodape(
        slide,
        "Diagnóstico de reconstrução da regra, sem abertura de desfecho: "
        "output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json. Edital SGTES/MS nº 3/2025, "
        "itens 11.1.3 e 11.1.4; Ipea, Atlas da Vulnerabilidade Social (2015).",
    )


# --------------------------------------------------------------------------
# montagem
# --------------------------------------------------------------------------

# Índices, no arquivo base, dos slides de sumário que abrem cada seção.
DIVISORIAS = (1, 5, 7, 12, 15, 17)

# Erros de digitação do template, corrigidos nos seis sumários.
CORRECOES = {"porposto": "proposto", "Téorica": "Teórica"}


def corrigir_sumarios(prs) -> int:
    trocas = 0
    for indice in DIVISORIAS:
        for shape in prs.slides[indice].shapes:
            if not shape.has_text_frame:
                continue
            for paragrafo in shape.text_frame.paragraphs:
                for run in paragrafo.runs:
                    texto = run.text
                    for errado, certo in CORRECOES.items():
                        if errado in texto:
                            texto = texto.replace(errado, certo)
                            trocas += 1
                    if texto.strip() == "Modelo":
                        texto = texto.replace("Modelo", "Modelo Teórico")
                        trocas += 1
                    run.text = texto
    return trocas


# Ordem final: índices do arquivo base, já sem o slide vazio do fim e com os
# dois slides novos (19: equipe e capital; 20: o IVS no custo).
ORDEM_FINAL = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 19, 12, 13, 14, 20, 15, 16, 17, 18]

ROTEIRO = [
    "Capa", "Sumário · Motivação", "O problema", "A política", "O efeito",
    "Sumário · Pergunta", "A pergunta",
    "Sumário · Literatura", "As três primitivas", "Moehling et al. (2020)",
    "Redding & Rossi-Hansberg (2017)", "Choné & Ma (2011)", "Equipe e capital",
    "Sumário · Modelo", "Como juntamos os três", "A remuneração além da bolsa",
    "O IVS no custo",
    "Sumário · Hipótese", "A hipótese",
    "Sumário · Viabilidade", "Viabilidade empírica",
]


def normalizar_zip(caminho: Path) -> None:
    """Regrava o .pptx com data fixa em cada entrada.

    O python-pptx carimba a hora corrente em cada arquivo do pacote, o que faria
    duas execuções iguais produzirem hashes diferentes. O conteúdo já é idêntico;
    só os metadados do zip mudavam.
    """
    origem = zipfile.ZipFile(caminho)
    temporario = caminho.with_suffix(".pptx.tmp")
    with zipfile.ZipFile(temporario, "w", zipfile.ZIP_DEFLATED) as saida:
        for info in origem.infolist():
            dados = origem.read(info.filename)
            fixo = zipfile.ZipInfo(info.filename, date_time=(1980, 1, 1, 0, 0, 0))
            fixo.compress_type = info.compress_type
            fixo.external_attr = info.external_attr
            saida.writestr(fixo, dados)
    origem.close()
    temporario.replace(caminho)


def hash_arquivo(caminho: Path) -> str:
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


def main() -> None:
    prs = Presentation(str(BASE))
    remover(prs, 19)  # slide vazio ao fim do template
    novo_equipe = duplicar(prs, 11)  # gabarito de equação
    novo_ivs = duplicar(prs, 13)  # gabarito de modelo
    trocas = corrigir_sumarios(prs)

    slide_problema(prs.slides[2])
    slide_politica(prs.slides[3])
    slide_efeito(prs.slides[4])
    slide_equipe_e_capital(novo_equipe)
    slide_juncao(prs.slides[13])
    slide_remuneracao(prs.slides[14])
    slide_ivs(novo_ivs)
    slide_hipotese(prs.slides[16])
    slide_viabilidade(prs.slides[18])

    reordenar(prs, ORDEM_FINAL)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(SAIDA))
    normalizar_zip(SAIDA)

    manifesto = {
        "gerado_por": "scripts/apresentacao/montar_deck_banca1_pptx.py",
        "base": {
            "caminho": str(BASE.relative_to(RAIZ)),
            "sha256": hash_arquivo(BASE),
        },
        "saida": {
            "caminho": str(SAIDA.relative_to(RAIZ)),
            "sha256": hash_arquivo(SAIDA),
            "slides": len(ROTEIRO),
        },
        "correcoes_de_digitacao_nos_sumarios": trocas,
        "roteiro": {str(i): nome for i, nome in enumerate(ROTEIRO, start=1)},
        "figuras": {
            nome: hash_arquivo(FIGURAS / nome)
            for nome in ("especialistas_extremos_uf.png", "bolsa_por_faixa.png",
                         "oferta_antes_depois_por_faixa.png", "custo_laboral_deck.png")
        },
        "equacoes": {
            nome: hash_arquivo(caminho) for nome, caminho in sorted(_EQ_CACHE.items())
        },
        "figuras_de_docs": {
            "deslocamento_por_regiao.png": hash_arquivo(
                RAIZ / "docs" / "07_apresentacoes" / "banca1" / "figuras"
                / "deslocamento_por_regiao.png"
            )
        },
        "escopo": (
            "Banca 1: termina na viabilidade empírica e não apresenta resultado de "
            "estimação. As leituras das figuras de oferta são descritivas."
        ),
    }
    (SAIDA_DIR / "manifesto_deck_banca1.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf8"
    )
    print(f"deck gravado em {SAIDA} ({len(ROTEIRO)} slides)")
    print(f"correções de digitação nos sumários: {trocas}")


if __name__ == "__main__":
    main()
