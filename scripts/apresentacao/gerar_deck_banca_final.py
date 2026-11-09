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
from pptx.util import Inches

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
ORIGENS = {"G": "deck do grupo", "D": "diagrama (deck reorganizado)", "PB": "banca 2 pós-banca"}
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
    return {"ordem": ordem_saida, "adaptacoes": feitas}


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
