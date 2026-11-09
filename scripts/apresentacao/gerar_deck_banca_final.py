"""Deck da banca final: a parte da banca 1 (motivação, pergunta, literatura, hipótese), adaptada às mudanças da
banca 2, seguida dos 11 slides da banca 2 e do apêndice de teoria.

Conteúdo canônico: docs/07_apresentacoes/banca_final/02_deck_banca_final.md. O deck é derivado; divergência entre
ele e o doc é erro do deck.

Entradas (só leitura, todas em output/):
- output/apresentacao_banca_final/deck_proposta_reorganizada.pptx — deck do grupo reorganizado, com o diagrama da
  teoria da mudança (gerado por scripts/apresentacao/gerar_diagrama_banca_final.py);
- output/apresentacao_banca2/deck_banca2_curto.pptx — os 11 slides da banca 2 (gerados por gerar_deck_banca2.py);
- output/apresentacao_banca1/especialistas_por_uf_extremos.png e vagas_ciclo1_por_regiao.png — figuras do pipeline
  da banca 1 (gerar_figuras_banca1.py), no lugar dos gráficos do grupo sem fonte reproduzível (P6, P7).

Nada é estimado; nada é lido de data/. Cada troca de texto confere que o texto antigo está lá antes de trocar; se
não estiver, o script para.

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
from pptx.util import Emu, Inches

ROOT = Path(__file__).resolve().parents[2]
ENT_GRUPO = ROOT / "output/apresentacao_banca_final/deck_proposta_reorganizada.pptx"
ENT_B2 = ROOT / "output/apresentacao_banca2/deck_banca2_curto.pptx"
FIG_UF = ROOT / "output/apresentacao_banca1/especialistas_por_uf_extremos.png"
FIG_VAGAS = ROOT / "output/apresentacao_banca1/vagas_ciclo1_por_regiao.png"
SAIDA = ROOT / "output/apresentacao_banca_final"
ARQ_DECK = "deck_banca_final.pptx"
ARQ_PDF = "deck_banca_final.pdf"
ARQ_MANIF = "manifesto_deck_banca_final.json"
DOC = "docs/07_apresentacoes/banca_final/02_deck_banca_final.md"

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
QN_EMBED = "{%s}embed" % NS["r"]

# --------------------------------------------------------------------------------------------------------------
# Ordem do deck final. ("G", n) = slide n do deck do grupo reorganizado; ("B2", n) = slide n do deck curto da
# banca 2. A seção é a do rodapé de navegação (None: sem seção marcada, como no apêndice da banca 2).
# --------------------------------------------------------------------------------------------------------------
SECOES = ("Motivação", "Pergunta", "Literatura", "Hipótese", "Base de Dados", "Metodologia", "Resultados")
ORDEM = [
    ("G", 1, None),            # capa
    ("G", 2, "Motivação"),     # sumário
    ("G", 3, "Motivação"),     # escassez de especialistas (figuras do pipeline)
    ("G", 7, "Motivação"),     # IVS e bolsa (faixas corrigidas)
    ("G", 12, "Pergunta"),     # sumário
    ("G", 13, "Pergunta"),     # a pergunta (nova)
    ("G", 15, "Literatura"),   # sumário
    ("G", 16, "Literatura"),   # diagrama A: teoria da mudança
    ("G", 17, "Hipótese"),     # sumário
    ("B2", 1, "Hipótese"),     # pergunta e hipótese (banca 2)
    ("G", 18, "Hipótese"),     # diagrama B, com a hipótese nova
    ("G", 19, "Base de Dados"),
    ("B2", 2, "Base de Dados"),
    ("B2", 3, "Base de Dados"),
    ("B2", 4, "Base de Dados"),
    ("B2", 5, "Base de Dados"),
    ("G", 21, "Metodologia"),
    ("B2", 6, "Metodologia"),
    ("B2", 7, "Metodologia"),
    ("G", 23, "Resultados"),
    ("B2", 8, "Resultados"),
    ("B2", 9, "Resultados"),
    ("B2", 10, "Resultados"),
    ("B2", 11, "Resultados"),
    ("G", 25, None),           # Q&A
    ("G", 26, None),           # divisor Apêndice
    ("G", 27, None),           # três elementos da teoria
    ("G", 28, None),           # escolha locacional maximiza a utilidade
    ("G", 30, None),           # renda real líquida
    ("G", 31, None),           # custo geográfico e laboral
    ("G", 29, None),           # da escolha individual ao agregado
    ("G", 38, None),           # o IVS
]
# Sumários do grupo: a seção que cada um destaca (conferido no render; não muda nada neles)
SUMARIOS = {2: "Motivação", 12: "Pergunta", 15: "Literatura", 17: "Hipótese", 19: "Base de Dados",
            21: "Metodologia", 23: "Resultados"}
# Slides do grupo que saem, com o motivo (vão para o manifesto e para o doc 02)
FORA = {
    4: "oculto; figura de UF do grupo sem fonte reproduzível (P6)",
    5: "animação parcial do slide 7",
    6: "animação parcial do slide 7",
    8: "oculto; versão antiga do mapa do IVS",
    9: "crescimento por faixa que não se reproduz (P12) e distribuição regional com diferença sem origem (P13)",
    10: "oculto; rodapé antigo",
    11: "oculto; 'indícios de efetividade' (antes/depois sem comparação; errata E6, P12)",
    14: "oculto; tabela de inclinações que não se reproduz (P8)",
    20: "marcador 'X' do grupo, substituído pelos slides da banca 2",
    22: "marcador 'X' do grupo, substituído pelos slides da banca 2",
    24: "marcador 'X' do grupo, substituído pelos slides da banca 2",
    32: "oculto; versão anterior do slide 29",
    33: "hipótese antiga (preenchimento) sobreposta às derivadas",
    34: "EXEMPLO de outro trabalho",
    35: "EXEMPLO de outro trabalho",
    36: "viabilidade empírica da banca 1, substituída pelos dados da banca 2 (erratas E4 e E5)",
    37: "viabilidade empírica da banca 1, substituída pelos dados da banca 2 (erratas E4 e E5)",
}

# --------------------------------------------------------------------------------------------------------------
# Textos novos (os mesmos do doc 02; o teste confere)
# --------------------------------------------------------------------------------------------------------------
PERGUNTA = "Uma bolsa maior do PMM-E muda a vaga que o especialista escolhe como 1ª opção?"
HIPOTESE = ("Comparando vagas da mesma UF, a de bolsa maior tem mais chance de ser a 1ª opção do especialista "
            "(formulada após ver os dados).")
ROTULO_HIPOTESE = "HIPÓTESE: BOLSA → 1ª OPÇÃO"
TITULO_IVS = "A vulnerabilidade social define a faixa da bolsa do PMM-E"
SUB_IVS = "III. O IVS define a faixa da bolsa do PMM-E"
SUB2_IVS = "Bolsa-formação mensal por faixa do IVS 2010 oficial (Ipea)"
FAIXAS_IVS = {"Vulnerabilidade: Muito alta": "IVS acima de 0,400: alta e muito alta",
              "Vulnerabilidade: Alta": "IVS de 0,301 a 0,400: média",
              "Vulnerabilidade: Média, baixa e buito baixa": "IVS até 0,300: baixa e muito baixa"}
NOTA_IVS = ("Instrumento da política. A bolsa de R$ 10 mil, R$ 15 mil ou R$ 20 mil é fixada por regra sobre o "
            "IVS 2010 do município, com cortes em 0,300 e 0,400.")
FONTES_IVS = "Fontes: Ipea, Atlas da Vulnerabilidade Social (IVS 2010); quadros de vagas SGTES/MS; auditoria 16."
SUB2_UF = "Especialistas por 100 mil habitantes, as duas maiores e as duas menores UFs – dez/2024"
SUB_VAGAS = "II. O ciclo 1 do PMM-E abriu vagas nas cinco regiões"
SUB2_VAGAS = "Células estabelecimento × curso e vagas imediatas, ciclo 1, 1ª chamada"
FONTES_ESCASSEZ = ("Fontes: Medicina S/A; Amado Mundo; Agência Câmara; Scheffer et al., Demografia Médica no Brasil "
                   "2025 (FMUSP/AMB), só as UFs com valor citado; quadro de vagas do Edital SGTES/MS nº 3/2025.")
CTEXT_UTILIDADE = ("A política mexe em apenas uma variável: eleva E(w|B) pela bolsa (B). Preços e custo do local "
                   "continuam contra, e é a soma das três variáveis que decide qual vaga o médico escolhe.")
ROTULO_CADEIA = "CADEIA DO MODELO"
NOTAS = {
    3: ("A escassez de especialistas é desigual entre as UFs: na Demografia Médica 2025, de 453 por 100 mil no DF a "
        "68 no MA (só as UFs com valor citado na fonte). O ciclo 1 do PMM-E abriu 1.295 células estabelecimento × "
        "curso em 368 municípios das cinco regiões, com 678 vagas imediatas. Os gráficos do grupo com as 16 UFs e "
        "com o deslocamento por região saíram: não têm fonte primária reproduzível (pendências P6 e P7 da banca 1)."),
    7: ("O IVS do Ipea vai de 0 a 1 e resume infraestrutura urbana, capital humano e renda e trabalho. A bolsa do "
        "PMM-E sai do IVS 2010 oficial por regra: até 0,300, R$ 10 mil; de 0,301 a 0,400, R$ 15 mil; acima de "
        "0,400, R$ 20 mil. A regra reproduz a faixa de todos os municípios dos ciclos 1 e 2. Na banca 1 dissemos "
        "que o IVS era só um piso; isso vinha de um arquivo de IVS errado (errata E10, auditoria 16) e não vale."),
    13: ("A pergunta da banca 1 era se mais remuneração atrai especialistas para municípios mais vulneráveis. Com "
         "os dados que temos, medimos a margem que a bolsa pode mover diretamente: a vaga que o especialista que "
         "se candidatou marca como 1ª opção. Não medimos a ida ao município nem o preenchimento."),
    18: ("A cadeia é a mesma da teoria. A hipótese agora fica só no passo 2, a escolha: comparando vagas da mesma "
         "UF, a de bolsa maior tem mais chance de ser a 1ª opção. Foi formulada depois de ver os dados. Os passos "
         "seguintes (preenchimento, capacidade, acesso, saúde) não são testados aqui. Três pontos limitam a "
         "leitura: A, outras políticas mudam nos mesmos cortes de IVS (medimos um pacote); B, a vaga abre antes "
         "da escolha, e por isso contar vagas preenchidas mistura abrir com atrair; C, substituição."),
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
    """A única forma cujo texto (sem quebras e espaços nas pontas) é `texto` (ou começa com ele)."""
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
    ps = sh.text_frame.paragraphs
    for p in ps[1:]:
        p._p.getparent().remove(p._p)
    trocar_paragrafo(sh, novo, 0)


def remover(sh) -> None:
    sh._element.getparent().remove(sh._element)


def rodape(slide, secao: str | None) -> None:
    """Refaz a navegação do rodapé com as sete seções do deck do grupo, a corrente em negrito verde."""
    alvo = [sh for sh in formas(slide.shapes) if sh.has_text_frame and sh.text_frame.text.startswith("Motivação")
            and ("|" in sh.text_frame.text or " I " in sh.text_frame.text)]
    alvo += [sh for sh in formas(slide.shapes) if sh.has_text_frame and sh.text_frame.text.startswith("Hipótese  |")]
    if not alvo:
        return
    if len(alvo) != 1:
        raise SystemExit(f"ERRO: mais de um rodapé de navegação: {[s.name for s in alvo]}")
    p = alvo[0].text_frame.paragraphs[0]._p
    modelo = p.find("a:r/a:rPr", NS)
    for r in p.findall("a:r", NS):
        p.remove(r)
    end = p.find("a:endParaRPr", NS)

    def run(texto: str, destaque: bool):
        r = etree.SubElement(p, "{%s}r" % NS["a"])
        rpr = copy.deepcopy(modelo)
        for k in ("b",):
            rpr.attrib.pop(k, None)
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

    for k, s in enumerate(SECOES):
        run(s, s == secao)
        if k < len(SECOES) - 1:
            run("  |  ", False)


def numerar(slide, n: int) -> None:
    """Número digitado à mão pelo grupo no canto inferior direito: passa a ser a posição no deck final."""
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

    # Slide 3: gráficos do grupo sem fonte reproduzível (P6, P7) -> figuras do pipeline da banca 1
    sl = s[2]
    for nome in ("Chart 14", "Chart 11"):
        ch = por_nome(sl, nome)
        x, y, h = ch.left, ch.top, ch.height
        remover(ch)
        fig = FIG_UF if nome == "Chart 14" else FIG_VAGAS
        from PIL import Image
        w_px, h_px = Image.open(fig).size
        sl.shapes.add_picture(str(fig), x, y, height=h, width=int(h * w_px / h_px))
    trocar_paragrafo(por_texto(sl, "Médicos especialistas por 100 mil habitantes, por UF – 2024"), SUB2_UF)
    trocar_paragrafo(por_texto(sl, "II. Serviços especializados exigem longos deslocamentos"), SUB_VAGAS)
    trocar_paragrafo(por_texto(sl, "Deslocamento médio da população para serviços de alta complexidade"), SUB2_VAGAS)
    trocar_forma(por_texto(sl, "Fontes: Medicina S/A", inicio=True), FONTES_ESCASSEZ,
                 por_texto(sl, "Fontes: Medicina S/A", inicio=True).text_frame.text)
    notas(sl, NOTAS[3])
    feitas.append("slide 3: figuras do pipeline (UFs com valor citado; vagas do ciclo 1 por região)")

    # Slide 7: IVS e bolsa — "piso" e grade do FAQ saem; faixas pela regra aplicada (errata E10, auditoria 16)
    sl = s[6]
    trocar_paragrafo(por_texto(sl, "A vulnerabilidade social define o piso da bolsa do PMM-E"), TITULO_IVS)
    trocar_paragrafo(por_texto(sl, "III. O IVS define a renumeração do PMM-E"), SUB_IVS)
    trocar_paragrafo(por_texto(sl, "Bolsa-formação mensal por categoria do Índice de Vulnerabilidade Social"),
                     SUB2_IVS)
    for antigo, novo in FAIXAS_IVS.items():
        trocar_forma(por_texto(sl, antigo), novo, antigo)
    nota = por_texto(sl, "Instrumento da política.", inicio=True)
    trocar_forma(nota, NOTA_IVS, nota.text_frame.text)
    fontes = por_texto(sl, "Fontes: Ipea", inicio=True)
    trocar_forma(fontes, FONTES_IVS, fontes.text_frame.text)
    notas(sl, NOTAS[7])
    feitas.append("slide 7: faixas da bolsa pela regra aplicada (até 0,300; 0,301–0,400; acima de 0,400)")

    # Slide 13: a pergunta nova; o fundo (cópia do slide 9, com números que não se reproduzem) sai
    sl = s[12]
    for sh in list(sl.shapes):
        if sh.name not in ("Retângulo 4", "Group 12"):
            remover(sh)
    perg = por_texto(sl, "Um aumento na remuneração do PMM-E", inicio=True)
    trocar_forma(perg, PERGUNTA, perg.text_frame.text)
    notas(sl, NOTAS[13])
    feitas.append("slide 13: pergunta nova, sem o fundo com números não reproduzíveis")

    # Slide 18 (diagrama B): hipótese nova; colchete só sob a escolha
    sl = s[17]
    b = por_nome(sl, "B_hipotese")
    trocar_paragrafo(b, HIPOTESE, 1, antigo="Municípios com maior remuneração oferecida pelo PMM-E têm maior "
                                            "probabilidade de preenchimento de vagas.")
    col = por_nome(sl, "B_colchete_hipotese")
    no3 = por_nome(sl, "B_no_B3")
    col.left, col.width = no3.left, no3.width
    rot = por_nome(sl, "B_rotulo_hipotese")
    trocar_paragrafo(rot, ROTULO_HIPOTESE, 0, antigo="HIPÓTESE: BOLSA → PREENCHIMENTO")
    centro = no3.left + no3.width // 2
    rot.width = Inches(2.6)
    rot.left = centro - rot.width // 2
    notas(sl, NOTAS[18])
    feitas.append("slide 18: hipótese da escolha (1ª opção), colchete só no passo 2")

    # Slide 28: a soma das três variáveis decide a escolha, não o preenchimento
    sl = s[27]
    c = por_nome(sl, "cText")
    trocar_forma(c, CTEXT_UTILIDADE, c.text_frame.text)
    feitas.append("slide 28: 'decide qual vaga o médico escolhe'")

    # Slide 29: a cadeia até o preenchimento é do modelo, não a hipótese testada
    sl = s[28]
    trocar_paragrafo(por_nome(sl, "hyplab"), ROTULO_CADEIA, 0, antigo="HIPÓTESE")
    feitas.append("slide 29: rótulo 'CADEIA DO MODELO' no lugar de 'HIPÓTESE'")

    # Slide 38: grafia (errata E8)
    sl = s[37]
    t = por_texto(sl, "Vulnerabilidade social: fragilidades", inicio=True)
    achou = False
    for p in t.text_frame.paragraphs:
        for r in p.runs:
            if "trasnporte" in r.text:
                r.text = r.text.replace("trasnporte", "transporte")
                achou = True
    if not achou:
        raise SystemExit("ERRO: 'trasnporte' não encontrado no slide 38")
    feitas.append("slide 38: 'transporte' (errata E8)")
    return feitas


def copiar_slide(origem, destino_prs, layout):
    novo = destino_prs.slides.add_slide(layout)
    for sh in list(novo.shapes):
        remover(sh)
    arvore = novo.shapes._spTree
    for el in origem.shapes._spTree:
        if el.tag.endswith("}nvGrpSpPr") or el.tag.endswith("}grpSpPr") or el.tag.endswith("}extLst"):
            continue
        el2 = copy.deepcopy(el)
        for blip in el2.iter("{%s}blip" % NS["a"]):
            rid = blip.get(QN_EMBED)
            if rid:
                img = origem.part.related_part(rid)
                _, novo_rid = novo.part.get_or_add_image_part(io.BytesIO(img.blob))
                blip.set(QN_EMBED, novo_rid)
        arvore.append(el2)
    if origem.has_notes_slide:
        notas(novo, origem.notes_slide.notes_text_frame.text)
    return novo


def construir(saida: Path) -> dict:
    prs = Presentation(str(ENT_GRUPO))
    b2 = Presentation(str(ENT_B2))
    if len(prs.slides) != 38 or len(b2.slides) != 11:
        raise SystemExit(f"ERRO: esperava 38 slides no deck do grupo e 11 no da banca 2; "
                         f"vieram {len(prs.slides)} e {len(b2.slides)}")
    usados = {n for o, n, _ in ORDEM if o == "G"}
    if usados | set(FORA) != set(range(1, 39)) or usados & set(FORA):
        raise SystemExit("ERRO: ORDEM e FORA precisam cobrir os 38 slides do grupo, sem repetição")
    feitas = adaptar_grupo(prs)
    layout = prs.slides[2].slide_layout
    if layout.name != "1_Title Slide":
        raise SystemExit(f"ERRO: layout inesperado {layout.name!r}")
    ids_grupo = list(prs.slides._sldIdLst)
    copias = {n: copiar_slide(b2.slides[n - 1], prs, layout) for n in range(1, 12)}
    ids_b2 = {n: prs.slides._sldIdLst[38 + n - 1] for n in range(1, 12)}
    lista = prs.slides._sldIdLst
    for el in list(lista):
        lista.remove(el)
    ordem_saida = []
    for pos, (o, n, secao) in enumerate(ORDEM, start=1):
        el = ids_grupo[n - 1] if o == "G" else ids_b2[n]
        lista.append(el)
        el.attrib.pop("show", None)
    for n in FORA:
        rid = ids_grupo[n - 1].get("{%s}id" % NS["r"])
        prs.part.drop_rel(rid)
    for pos, (o, n, secao) in enumerate(ORDEM, start=1):
        sl = prs.slides[pos - 1]
        if sl._element.get("show") == "0":
            sl._element.attrib.pop("show")
        rodape(sl, secao)
        numerar(sl, pos)
        titulo = next((" ".join(sh.text_frame.text.split()) for sh in formas(sl.shapes)
                       if sh.has_text_frame and sh.is_placeholder and sh.placeholder_format.type is not None
                       and "TITLE" in str(sh.placeholder_format.type)), "")
        if o == "G" and n in SUMARIOS:
            titulo = f"Sumário ({SUMARIOS[n]})"
        ordem_saida.append({"posicao": pos, "origem": f"{'grupo' if o == 'G' else 'banca 2'} {n}",
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
                for p in (ENT_GRUPO, ENT_B2, FIG_UF, FIG_VAGAS)]
    saidas = [{"caminho": (SAIDA / n).relative_to(ROOT).as_posix(), "sha256": sha256(SAIDA / n)}
              for n in (ARQ_DECK, ARQ_PDF) if (SAIDA / n).exists() and (n != ARQ_PDF or com_pdf)]
    man = {
        "script": "scripts/apresentacao/gerar_deck_banca_final.py",
        "conteudo_canonico": DOC,
        "natureza_dos_dados": "EMPIRICO (slides da banca 2) e teoria (parte da banca 1); nada estimado aqui",
        "regra": "lê só de output/; slides da banca 2 copiados sem mudar texto; slides do grupo com as trocas "
                 "listadas em 'adaptacoes', cada uma conferida contra o texto antigo",
        "nota_pdf": "o PDF é renderizado pelo LibreOffice e não é byte a byte determinístico",
        "entradas": entradas,
        "saidas": saidas,
        "slides_do_grupo_fora": {str(k): v for k, v in sorted(FORA.items())},
        **resumo,
    }
    (SAIDA / ARQ_MANIF).write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for s in saidas:
        print(s["caminho"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
