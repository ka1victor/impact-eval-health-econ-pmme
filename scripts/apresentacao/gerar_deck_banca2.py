"""Monta o deck da banca 2 a partir do deck do grupo e do conteúdo canônico (`docs/07_apresentacoes/banca2/02`).

Entrada (só leitura): o deck do grupo (`.pptx`, fora do repositório), cujo caminho vem de `--deck` ou da variável
de ambiente `PMME_DECK_GRUPO`; o doc 02 da banca 2; as figuras e `numeros_banca2.json` de
`output/apresentacao_banca2/`, gravados por `scripts/apresentacao/gerar_figuras_banca2.py`.

Saídas, em `output/apresentacao_banca2/`:

* `deck_banca2.pptx`: o entregável, um arquivo só com tudo: os slides prévios do grupo reutilizados como estão, só com as correções, e a parte
  empírica organizada, cortada e sintetizada (pedido do autor de 26/10/2026): hipóteses → base → metodologia →
  resultados → robustez e discussão; depois do divisor "Apêndice", o que é importante mas não central, por seção;
* `manifesto_deck_banca2.json`: entradas e saídas com SHA-256, ordem dos slides, classificação de cada slide do
  deck do grupo e correções aplicadas.

A ordem do deck inteiro vem do doc 02: cada cabeçalho `##` é um slide novo, e cada marcador
`<!-- grupo: N -->` (ou `<!-- grupo: N | título -->`, que troca o título) põe ali o slide N do deck do grupo. A
tabela de classificação do doc 02 diz o destino de cada um dos 36 slides do grupo (corpo, apêndice ou removido);
o script para se ela e os marcadores divergirem. Os slides do grupo ficam com a visibilidade que o grupo deu a
eles, e o número de página digitado à mão vira o campo de número do slide.

O texto de cada slide novo vem do doc 02 (título, marcadores, tabelas, frase de cautela, fontes e notas do
apresentador); o deck é derivado e divergência é erro do deck. Os números das correções vêm de
`numeros_banca2.json`. As figuras entram como imagem; as tabelas, como tabela nativa. Nada é estimado aqui e
nada é lido de `data/`.

Determinístico: XML montado por funções puras, zip com data fixa (a do gerador da banca final) e ordem estável.

Modo padrão, o deck curto (decisão do autor de 26/10/2026: "só as versões curtas são usadas"; a estrutura
obrigatória está no doc 06; no máximo cerca de 30 palavras visíveis por slide). O deck completo só é regerado com
`--completo` e fica como registro, sem atualização. Pedido original do curto: "só do 14 em diante, e MUITO menor,
focado nas discussões que tivemos aqui, sem colocar um monte de texto, sem colocar o diagrama causal da teoria no
meio". O modo curto lê
`docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md` e grava `deck_banca2_curto.pptx`, o PDF dele (pelo
LibreOffice, se houver) e `manifesto_deck_banca2_curto.json`. Usa o deck do grupo só como template (mestre,
layout; o rodapé passa a listar as oito seções da estrutura obrigatória): nenhum slide do grupo, nenhuma
divisória, nenhum diagrama e nenhum apêndice. Cada slide tem título-afirmação, a figura (ou a tabela) grande e
poucas linhas curtas; o resto vai para as notas. O script para se as seções fugirem da estrutura obrigatória, se
um slide passar de 30 palavras visíveis (fora título, figura e fontes), se uma linha não couber ou se um slide
passar do limite de linhas.

Uso:

    PMME_DECK_GRUPO="<caminho do deck do grupo>" python3 scripts/apresentacao/gerar_deck_banca2.py        # curto
    PMME_DECK_GRUPO="<caminho do deck do grupo>" python3 scripts/apresentacao/gerar_deck_banca2.py --completo  # registro
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SAIDA = ROOT / "output" / "apresentacao_banca2"
DOC02 = ROOT / "docs" / "07_apresentacoes" / "banca2" / "02_conteudo_slides.md"
NUMEROS = SAIDA / "numeros_banca2.json"
ARQ_DECK = "deck_banca2.pptx"
ARQ_MANIFESTO = "manifesto_deck_banca2.json"
# deck curto (pedido do autor de 26/10/2026): só a parte empírica, figura grande e no máximo duas linhas curtas
DOC_CURTO = ROOT / "docs" / "07_apresentacoes" / "banca2" / "04_conteudo_deck_curto.md"
ARQ_CURTO = "deck_banca2_curto.pptx"
ARQ_CURTO_PDF = "deck_banca2_curto.pdf"
ARQ_MANIF_CURTO = "manifesto_deck_banca2_curto.json"

_spec = importlib.util.spec_from_file_location("gerar_diagrama_banca_final",
                                               ROOT / "scripts" / "apresentacao" / "gerar_diagrama_banca_final.py")
BF = importlib.util.module_from_spec(_spec)
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec.loader.exec_module(BF)
sys.dont_write_bytecode = _bytecode

Slide, xml_slide, xml_notas, Pacote = BF.Slide, BF.xml_slide, BF.xml_notas, BF.Pacote
pol, run, para = BF.pol, BF.Slide.run, BF.Slide.para
VERDE_ESCURO, VERDE, CLARO, CLARO2, LINHA = BF.VERDE_ESCURO, BF.VERDE, BF.CLARO, BF.CLARO2, BF.LINHA
TEXTO, MUDO, BRANCO, FONTE = BF.TEXTO, BF.MUDO, BF.BRANCO, BF.FONTE

# Títulos esperados no deck do grupo (conferência de que é o deck certo)
TITULOS_ESPERADOS = {23: "Da condição de aceitação, sai nossa hipótese econômica",
                     34: "O desafio é separar o efeito da bolsa do efeito da vulnerabilidade",
                     35: "O desafio é separar o efeito da bolsa do efeito da vulnerabilidade",
                     25: "X", 27: "X", 29: "X"}
N_GRUPO = 36
DESTINOS = ("corpo", "apêndice", "removido")

# Área útil do slide (polegadas); o slide é 13,333 × 7,5
X0, X1, Y0 = 0.32, 13.0, 0.88
Y_FONTES = 6.76


# --------------------------------------------------------------------------------------------------
# Leitura do doc 02
# --------------------------------------------------------------------------------------------------

def _inline(txt: str) -> list[tuple[str, bool, bool]]:
    """Markdown em linha -> [(texto, negrito, itálico)]. Trata **, *, `código` e [texto](link)."""
    txt = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", txt).replace("\\|", "|")
    saida: list[tuple[str, bool, bool]] = []
    for parte in re.split(r"(\*\*.+?\*\*)", txt):
        if not parte:
            continue
        if parte.startswith("**") and parte.endswith("**"):
            saida.append((parte[2:-2].replace("`", ""), True, False))
            continue
        for p2 in re.split(r"(?<!\*)(\*[^*\s][^*]*\*)(?!\*)", parte):
            if not p2:
                continue
            if p2.startswith("*") and p2.endswith("*") and len(p2) > 2:
                saida.append((p2[1:-1].replace("`", ""), False, True))
            else:
                saida.append((p2.replace("`", ""), False, False))
    return saida


def texto_puro(txt: str) -> str:
    return "".join(t for t, _, _ in _inline(txt))


def _celulas(linha: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", linha.strip())[1:-1]]


def ler_slides(doc: Path = DOC02) -> list[dict]:
    """Os slides novos do doc 02, na ordem, com seção, layout e blocos."""
    t = doc.read_text(encoding="utf-8")
    corpo = t[t.index("<!-- deck:inicio -->"):t.index("<!-- apendice:fim -->")]
    linhas = corpo.splitlines()
    slides: list[dict] = []
    secao = None
    atual: dict | None = None
    i = 0
    while i < len(linhas):
        ln = linhas[i]
        if ln.startswith("# "):
            secao = ln[2:].strip()
            atual = None
        elif ln.startswith("## "):
            atual = dict(secao=secao, titulo=ln[3:].strip(), rastreio="", layout="", imagem=None, alt="",
                         tabela=[], marcadores=[], paragrafos=[], codigo=[], cadeia="", cautela="", fontes="",
                         notas="", colunas=[], explica="", blocos=[], apendice=secao == "Apêndice", selo="",
                         max_linhas=None)
            slides.append(atual)
        elif atual is not None and ln.startswith("### "):
            atual["colunas"].append({"titulo": ln[4:].strip(), "itens": []})
        elif atual is not None:
            if re.fullmatch(r"`[^`]+`", ln.strip()) and not atual["rastreio"]:
                atual["rastreio"] = ln.strip().strip("`")
            elif m := re.match(r"<!-- selo: (.+?) -->", ln.strip()):
                atual["selo"] = m.group(1).strip()
            elif m := re.match(r"<!-- linhas: (\d+) -->", ln.strip()):
                atual["max_linhas"] = int(m.group(1))
            elif m := re.match(r"<!-- layout: (\w+)(?: ([\d.]+))? -->", ln.strip()):
                atual["layout"] = m.group(1)
                atual["largura_fig"] = float(m.group(2)) if m.group(2) else None
            elif m := re.match(r"!\[([^\]]*)\]\(([^)]+)\)", ln.strip()):
                atual["alt"], atual["imagem"] = m.group(1), (doc.parent / m.group(2)).resolve()
            elif ln.startswith("```"):
                i += 1
                while not linhas[i].startswith("```"):
                    atual["codigo"].append(linhas[i])
                    i += 1
            elif ln.startswith("|"):
                cel = _celulas(ln)
                if not all(re.fullmatch(r":?-+:?", c) for c in cel):
                    atual["tabela"].append(cel)
            elif ln.startswith("- "):
                item = ln[2:]
                while i + 1 < len(linhas) and linhas[i + 1].startswith("  ") and linhas[i + 1].strip():
                    i += 1
                    item += " " + linhas[i].strip()
                atual["marcadores"].append(item)
                if atual["colunas"]:
                    atual["colunas"][-1]["itens"].append(item)
            elif ln.strip():
                bloco = [ln]
                while i + 1 < len(linhas) and linhas[i + 1].strip() and not linhas[i + 1].startswith(("#", "|", "- ")):
                    i += 1
                    bloco.append(linhas[i])
                texto = " ".join(b.strip() for b in bloco)
                if texto.startswith("> [!NOTE]") or texto.startswith("**Números:**") or texto == "---":
                    pass
                elif texto.startswith("> **Notas do apresentador.**"):
                    atual["notas"] = re.sub(r"\s*>\s*", " ", texto[1:]).replace("**Notas do apresentador.**", "").strip()
                elif texto.startswith("> "):
                    atual["cautela"] = re.sub(r"\s*>\s*", " ", texto[1:]).strip()
                elif texto.startswith("**Fontes:**"):
                    atual["fontes"] = texto
                elif texto.startswith("**O que isso quer dizer.**"):
                    atual["explica"] = texto.replace("**O que isso quer dizer.**", "").strip()
                elif m := re.match(r"\*\*(Como foi medido\.|É causal\?)\*\* (.*)", texto):
                    atual["blocos"].append((m.group(1).rstrip("."), m.group(2).split(" ‖ ")))
                elif texto.startswith("**Cadeia:**"):
                    atual["cadeia"] = texto.replace("**Cadeia:**", "").strip()
                elif not texto.startswith("<!--"):
                    atual["paragrafos"].append(texto)
        i += 1
    return slides


MARCA_GRUPO = re.compile(r"<!-- grupo: (\d+)(?: \| (.+?))? -->")


def ler_ordem(doc: Path = DOC02) -> list[tuple]:
    """Ordem do deck inteiro: ("grupo", N, título novo ou None) para cada marcador e ("novo", k) para o k-ésimo `##`."""
    t = doc.read_text(encoding="utf-8")
    corpo = t[t.index("<!-- deck:inicio -->"):t.index("<!-- apendice:fim -->")]
    ordem, k = [], 0
    for ln in corpo.splitlines():
        if m := MARCA_GRUPO.fullmatch(ln.strip()):
            ordem.append(("grupo", int(m.group(1)), m.group(2)))
        elif ln.startswith("## "):
            ordem.append(("novo", k))
            k += 1
    return ordem


def ler_classificacao(doc: Path = DOC02) -> dict[int, dict]:
    """Tabela de classificação dos slides do deck do grupo: nº → destino, nº no deck proposto e motivo."""
    t = doc.read_text(encoding="utf-8")
    sec = t[t.index("## Classificação dos slides do deck do grupo"):t.index("<!-- deck:inicio -->")]
    out = {}
    for ln in sec.splitlines():
        if not ln.startswith("| "):
            continue
        cel = _celulas(ln)
        if not cel[0].isdigit():
            continue
        destino = texto_puro(cel[2]).strip()
        if destino not in DESTINOS:
            raise SystemExit(f"ERRO: destino {destino!r} do slide {cel[0]} do grupo fora de {DESTINOS}")
        out[int(cel[0])] = {"titulo_grupo": texto_puro(cel[1]), "destino": destino,
                            "posicao": int(cel[3]) if cel[3].isdigit() else None, "motivo": texto_puro(cel[4])}
    return out


# --------------------------------------------------------------------------------------------------
# Peças de slide
# --------------------------------------------------------------------------------------------------

def runs_md(txt: str, sz: float, cor: str = TEXTO, negrito: bool = False, cor_neg: str | None = None) -> list[str]:
    out = []
    txt = txt.replace("R$ ", "R$ ")  # "R$" não se separa do valor na quebra de linha
    txt = re.sub(r"(\d) mil\b", "\\1\u00a0mil", txt)  # nem o valor do "mil"
    for t, b, it in _inline(txt):
        out.append(run(t, sz, cor_neg if (b and cor_neg) else cor, b=b or negrito, i=it))
    return out


def linhas_necessarias(txt: str, sz: float, largura: float, fator: float = 0.56) -> int:
    palavras, n, atual = txt.split(), 1, 0.0
    esp = fator * sz / 72
    for p in palavras:
        w = (len(p) + 1) * esp
        if atual + w > largura and atual > 0:
            n += 1
            atual = w
        else:
            atual += w
    return n


SZ_CORPO, SZ_TAB_CORPO, SZ_TAB_APENDICE = 16.0, 14.0, 10.0  # pt mínimos: corpo, tabela no corpo, tabela no apêndice
LINHA_PT = 1.3 / 72  # altura de uma linha de texto, em polegadas por ponto


def altura_texto(txt: str, sz: float, w: float) -> float:
    """Altura de um parágrafo; a largura média do caractere da Montserrat é estimada com folga (0,54 em; medida no texto destes slides: 0,50 no regular e 0,53 no negrito)."""
    return linhas_necessarias(texto_puro(txt), sz, w, fator=0.54) * sz * LINHA_PT


def caixa_cautela(s: Slide, txt: str) -> float:
    """Frase de cautela embaixo, logo acima da linha de fontes; a altura acompanha o texto. Devolve o topo."""
    sz, w = SZ_CORPO, X1 - X0
    h = altura_texto(txt.replace("**", ""), sz, w - 0.4) + 0.2
    y = Y_FONTES - 0.06 - h
    s.forma("Cautela", X0, y, w, h, adj=12000, fill=CLARO2, anchor="ctr", ins=(0.18, 0.04, 0.18, 0.04),
            paras=[para(runs_md(txt.replace("**", ""), sz, VERDE_ESCURO, negrito=True), "l")])
    return y


def altura_explica(txt: str, w: float, sz: float = SZ_CORPO) -> float:
    return 0.16 + sz * LINHA_PT + 0.06 + altura_texto(txt, sz, w - 0.36) + 0.14


def altura_bloco(partes: list[str], w: float, sz: float = SZ_CORPO) -> float:
    return 0.16 + sz * LINHA_PT + 0.06 + sum(altura_texto(p, sz, w - 0.36) + 0.06 for p in partes) + 0.12


def caixa_bloco(s: Slide, titulo: str, partes: list[str], x: float, y: float, w: float, h: float,
                sz: float = SZ_CORPO) -> None:
    """Bloco com título e parágrafos curtos (por exemplo, "Como foi medido" e "É causal?")."""
    s.forma(titulo, x, y, w, h, adj=6000, fill="F4F8F5", line=VERDE, line_w=1.25, anchor="t",
            ins=(0.18, 0.12, 0.18, 0.08),
            paras=[para([run(titulo, sz, VERDE, b=True)], depois=4)]
            + [para(runs_md(pt, sz, TEXTO, cor_neg=VERDE_ESCURO), linha=102, depois=4) for pt in partes])


def caixa_explica(s: Slide, txt: str, x: float, y: float, w: float, h: float, sz: float = SZ_CORPO) -> None:
    """Bloco "O que isso quer dizer": a leitura em linguagem simples do que o número significa para a pergunta."""
    s.forma("O que isso quer dizer", x, y, w, h, adj=6000, fill="F4F8F5", line=VERDE, line_w=1.25, anchor="t",
            ins=(0.18, 0.12, 0.18, 0.08),
            paras=[para([run("O que isso quer dizer", sz, VERDE, b=True)], depois=4),
                   para(runs_md(txt, sz, TEXTO, cor_neg=VERDE_ESCURO), linha=104)])


COR_SELO = "B3261E"  # vermelho do selo PRELIMINAR
H_SELO = 0.62


def caixa_selo(s: Slide, txt: str, x: float, y: float, w: float, h: float = H_SELO, sz: float = 20.0) -> None:
    """Selo bem visível (por exemplo, "PRELIMINAR: diagnóstico em auditoria"): faixa vermelha, letra branca."""
    s.forma("Selo", x, y, w, h, adj=18000, fill=COR_SELO, anchor="ctr", ins=(0.15, 0.03, 0.15, 0.03),
            paras=[para([run(txt, sz, BRANCO, b=True)], "ctr")])


def linha_fontes(s: Slide, txt: str) -> None:
    corpo = texto_puro(txt.replace("**Fontes:**", "").strip())
    s.texto("Fontes", X0, Y_FONTES, X1 - X0, 0.3,
            [para([run("Fontes: ", 8, MUDO, b=True), run(corpo, 8, MUDO)], linha=95)], anchor="b")


def imagem(s: Slide, rid: str, x: float, y: float, w: float, h: float, alt: str) -> None:
    i = s._id("Figura")
    s.partes.append(
        f'<p:pic><p:nvPicPr><p:cNvPr id="{i}" name="Figura" descr="{escape(alt, {chr(34): "&quot;"})}"/>'
        '<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
        f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
        f'<p:spPr><a:xfrm><a:off x="{pol(x)}" y="{pol(y)}"/><a:ext cx="{pol(w)}" cy="{pol(h)}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:ln w="6350"><a:solidFill><a:srgbClr val="DDE7DF"/>'
        '</a:solidFill></a:ln></p:spPr></p:pic>')


def encaixar(caminho: Path, w_max: float, h_max: float) -> tuple[float, float]:
    with Image.open(caminho) as im:
        a = im.size[0] / im.size[1]
    w = min(w_max, h_max * a)
    return w, w / a


def larguras_colunas(tab: list[list[str]], total: float, sz: float = 12.0) -> list[float]:
    """Largura proporcional ao texto, com mínimo para a palavra mais longa da coluna não quebrar."""
    n = len(tab[0])
    pesos, minimos = [], []
    for j in range(n):
        comp = [len(texto_puro(r[j])) for r in tab]
        pesos.append(min(max(max(comp) * 0.55 + sum(comp) / len(comp) * 0.45, 6), 70) ** 0.85)
        palavra = max(len(w) for r in tab for w in texto_puro(r[j]).split() or [""])
        minimos.append(palavra * 0.62 * sz / 72 + 0.22)
    larg = [total * p / sum(pesos) for p in pesos]
    for _ in range(5):
        falta = [j for j in range(n) if larg[j] < minimos[j]]
        if not falta:
            break
        extra = sum(minimos[j] - larg[j] for j in falta)
        livres = [j for j in range(n) if j not in falta]
        base = sum(larg[j] for j in livres)
        for j in falta:
            larg[j] = minimos[j]
        for j in livres:
            larg[j] -= extra * larg[j] / base
    return larg


def altura_tabela(tab: list[list[str]], larg: list[float], sz: float) -> tuple[float, list[float]]:
    alturas = []
    for r in tab:
        nl = max(linhas_necessarias(texto_puro(c), sz, w - 0.16) for c, w in zip(r, larg))
        alturas.append(nl * sz * 1.22 / 72 + 0.14)
    return sum(alturas), alturas


def tabela(s: Slide, tab: list[list[str]], x: float, y: float, w: float, h_max: float, sz_max: float = 18.0,
           sz_min: float = SZ_TAB_CORPO, preencher: bool = True, onde: str = "") -> float:
    """Tabela nativa no estilo do deck: a maior letra (até sz_max) que cabe em h_max; com `preencher`, as linhas
    crescem até ocupar h_max. Para se nem com sz_min a tabela cabe. Devolve a altura usada."""
    sz = sz_max
    while True:
        larg = larguras_colunas(tab, w, sz)
        h, alturas = altura_tabela(tab, larg, sz)
        if h <= h_max or sz <= sz_min:
            break
        sz -= 0.5
    if h > h_max + 0.02:
        raise SystemExit(f"ERRO: tabela de {onde!r} não cabe ({h:.2f} > {h_max:.2f} pol.) com letra {sz} pt")
    if preencher and h < h_max:
        alturas = [a * h_max / h for a in alturas]
    i = s._id("Tabela")
    grid = "".join(f'<a:gridCol w="{pol(c)}"/>' for c in larg)
    borda = ''.join(f'<a:{lado} w="6350"><a:solidFill><a:srgbClr val="{LINHA}"/></a:solidFill></a:{lado}>'
                    for lado in ("lnL", "lnR", "lnT", "lnB"))
    linhas_xml = []
    for k, (r, hr) in enumerate(zip(tab, alturas)):
        cab = k == 0
        fundo = VERDE_ESCURO if cab else (CLARO if k % 2 else BRANCO)
        cels = []
        for j, c in enumerate(r):
            cor = BRANCO if cab else TEXTO
            rr = runs_md(c, sz, cor, negrito=cab or j == 0, cor_neg=None if cab else VERDE_ESCURO)
            cels.append(f'<a:tc><a:txBody><a:bodyPr/><a:lstStyle/>{para(rr, "l", linha=100)}</a:txBody>'
                        f'<a:tcPr marL="{pol(0.08)}" marR="{pol(0.08)}" marT="{pol(0.04)}" marB="{pol(0.04)}" anchor="ctr">'
                        f'{borda}<a:solidFill><a:srgbClr val="{fundo}"/></a:solidFill></a:tcPr></a:tc>')
        linhas_xml.append(f'<a:tr h="{pol(hr)}">{"".join(cels)}</a:tr>')
    h_total = sum(alturas)
    s.partes.append(
        f'<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="{i}" name="Tabela"/><p:cNvGraphicFramePr>'
        '<a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/></p:nvGraphicFramePr>'
        f'<p:xfrm><a:off x="{pol(x)}" y="{pol(y)}"/><a:ext cx="{pol(w)}" cy="{pol(h_total)}"/></p:xfrm>'
        '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table"><a:tbl>'
        f'<a:tblPr firstRow="1" bandRow="1"/><a:tblGrid>{grid}</a:tblGrid>{"".join(linhas_xml)}</a:tbl>'
        '</a:graphicData></a:graphic></p:graphicFrame>')
    return h_total


def marcadores(s: Slide, itens: list[str], x: float, y: float, w: float, h: float, sz: float = SZ_CORPO,
               nome: str = "Marcadores", depois: int = 900) -> None:
    paras = []
    for it in itens:
        rr = runs_md(it, sz, TEXTO, cor_neg=VERDE_ESCURO)
        paras.append(f'<a:p><a:pPr marL="{pol(0.24)}" indent="-{pol(0.24)}" algn="l"><a:lnSpc><a:spcPct val="104000"/>'
                     f'</a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="{depois}"/></a:spcAft>'
                     f'<a:buClr><a:srgbClr val="{VERDE}"/></a:buClr><a:buFont typeface="Arial"/><a:buChar char="•"/>'
                     f'</a:pPr>{"".join(rr)}</a:p>')
    s.forma(nome, x, y, w, h, geom="rect", paras=paras, anchor="t", ins=(0, 0, 0, 0), txbox=True)


def altura_marcadores(itens: list[str], sz: float, w: float, depois: int = 900) -> float:
    """Altura dos marcadores, com um terço de linha de folga por item (o negrito do início é mais largo)."""
    return sum((altura_texto(it, sz, w - 0.26) + 0.3 * sz * LINHA_PT) * 1.04 + depois / 100 / 72 for it in itens)


# Equações: _x vira subscrito e ^x sobrescrito
def runs_equacao(txt: str, sz: float, cor: str = TEXTO) -> list[str]:
    out = []
    pos = 0
    for m in re.finditer(r"([_^])([A-Za-zÀ-ÿ0-9±×]+)", txt):
        if m.start() > pos:
            out.append(run(txt[pos:m.start()], sz, cor))
        r = run(m.group(2), sz * 0.95, cor)
        r = r.replace('dirty="0"', f'baseline="{-25000 if m.group(1) == "_" else 30000}" dirty="0"')
        out.append(r)
        pos = m.end()
    if pos < len(txt):
        out.append(run(txt[pos:], sz, cor))
    return out


# --------------------------------------------------------------------------------------------------
# Layouts
# --------------------------------------------------------------------------------------------------

def _nav(sl: dict) -> str:
    return {"Hipótese": "Hipótese", "Base de Dados": "Base de Dados", "Análise exploratória": "Base de Dados",
            "Metodologia": "Metodologia"}.get(sl["secao"], "Resultados")


def painel(s: Slide, sl: dict, x: float, y: float, w: float, y_fim: float, com_explica: bool = True,
           sz_tab_min: float = SZ_TAB_CORPO) -> None:
    """Coluna lateral: tabela (se houver), marcadores e o bloco "O que isso quer dizer", ocupando a altura toda.
    O espaço que sobra vai para a tabela (linhas mais altas) ou é dividido entre os blocos."""
    h_marc = altura_marcadores(sl["marcadores"], SZ_CORPO, w) if sl["marcadores"] else 0.0
    h_exp = altura_explica(sl["explica"], w) if (com_explica and sl["explica"]) else 0.0
    gap = 0.2
    if sl["tabela"]:
        h_tab = y_fim - y - h_marc - h_exp - gap * (bool(h_marc) + bool(h_exp))
        h_tab = tabela(s, sl["tabela"], x, y, w, h_tab, sz_max=16, sz_min=sz_tab_min, onde=sl["titulo"])
        y += h_tab + gap
    if sl["marcadores"]:
        marcadores(s, sl["marcadores"], x + 0.05, y, w - 0.05, h_marc)
        y += h_marc + gap
    if h_exp:
        if y_fim - y < h_exp - 0.05:
            raise SystemExit(f"ERRO: o painel de {sl['titulo']!r} não cabe ({y + h_exp - y_fim:.2f} pol. a mais)")
        caixa_explica(s, sl["explica"], x, y, w, y_fim - y)  # o bloco vai até o fim da área


def montar(sl: dict, rid_img: str | None) -> str:
    s = Slide()
    lay = sl["layout"]
    ap = sl["apendice"]
    sz_tab_min = SZ_TAB_APENDICE if ap else SZ_TAB_CORPO
    y_caut = caixa_cautela(s, sl["cautela"]) if sl["cautela"] else Y_FONTES - 0.1
    y_fim = y_caut - 0.14
    W = X1 - X0
    if lay == "tabela":
        h_exp = altura_explica(sl["explica"], W) if sl["explica"] else 0.0
        h_marc = altura_marcadores(sl["marcadores"], SZ_CORPO, W) if sl["marcadores"] else 0.0
        h_tab = y_fim - Y0 - h_exp - h_marc - 0.2 * (bool(h_exp) + bool(h_marc))
        h = tabela(s, sl["tabela"], X0, Y0, W, h_tab, sz_min=sz_tab_min, onde=sl["titulo"])
        y = Y0 + h + 0.2
        if sl["marcadores"]:
            marcadores(s, sl["marcadores"], X0 + 0.05, y, W - 0.05, h_marc)
            y += h_marc + 0.2
        if h_exp:
            caixa_explica(s, sl["explica"], X0, y_fim - h_exp, W, h_exp)
    elif lay == "tabela_lateral":
        w_tab = 8.5
        tabela(s, sl["tabela"], X0, Y0, w_tab, y_fim - Y0, sz_min=sz_tab_min, onde=sl["titulo"])
        sem_tab = dict(sl, tabela=[])
        painel(s, sem_tab, X0 + w_tab + 0.3, Y0, W - w_tab - 0.3, y_fim)
    elif lay == "figura_painel":
        w_fig_max = sl.get("largura_fig") or 8.6
        h_selo = (H_SELO + 0.2) if sl["selo"] else 0.0
        w, h = encaixar(sl["imagem"], w_fig_max, y_fim - Y0 - h_selo)
        imagem(s, rid_img, X0, Y0, w, h, sl["alt"])
        if sl["selo"]:
            caixa_selo(s, sl["selo"], X0, Y0 + h + 0.2, w)
        x_p = X0 + w + 0.3
        sobra = y_fim - (Y0 + h + h_selo) - 0.2
        explica_embaixo = bool(sl["explica"]) and sobra >= altura_explica(sl["explica"], w)
        if explica_embaixo:
            y_e = Y0 + h + h_selo + 0.2
            caixa_explica(s, sl["explica"], X0, y_e, w, y_fim - y_e)
        painel(s, sl, x_p, Y0, X1 - x_p, y_fim, com_explica=not explica_embaixo, sz_tab_min=sz_tab_min)
    elif lay == "figura_larga":
        # figura na largura toda, em cima; embaixo, os marcadores e o bloco "O que isso quer dizer"
        h_exp = altura_explica(sl["explica"], W) if sl["explica"] else 0.0
        h_marc = altura_marcadores(sl["marcadores"], SZ_CORPO, W) if sl["marcadores"] else 0.0
        w, h = encaixar(sl["imagem"], W, y_fim - Y0 - h_exp - h_marc - 0.2 * (bool(h_exp) + bool(h_marc)))
        imagem(s, rid_img, X0 + (W - w) / 2, Y0, w, h, sl["alt"])
        y = Y0 + h + 0.15
        if sl["marcadores"]:
            marcadores(s, sl["marcadores"], X0 + 0.05, y, W - 0.05, h_marc)
            y += h_marc + 0.1
        if h_exp:
            caixa_explica(s, sl["explica"], X0, y, W, max(h_exp, y_fim - y))
    elif lay == "figura_blocos":
        # figura e marcadores à esquerda; à direita, os blocos ("Como foi medido", "É causal?") até o fim da área
        w_fig = sl.get("largura_fig") or 6.4
        w, h = encaixar(sl["imagem"], w_fig, y_fim - Y0)
        imagem(s, rid_img, X0, Y0, w, h, sl["alt"])
        if sl["marcadores"]:
            y_m = Y0 + h + 0.15
            h_m = altura_marcadores(sl["marcadores"], SZ_CORPO, w)
            if y_m + h_m > y_fim + 0.05:
                raise SystemExit(f"ERRO: marcadores de {sl['titulo']!r} não cabem sob a figura")
            marcadores(s, sl["marcadores"], X0 + 0.05, y_m, w - 0.05, y_fim - y_m)
        x_b = X0 + w + 0.3
        w_b = X1 - x_b
        alturas = [altura_bloco(pt, w_b) for _, pt in sl["blocos"]]
        gap = 0.15
        sobra = y_fim - Y0 - sum(alturas) - gap * (len(alturas) - 1)
        if sobra < -0.05:
            raise SystemExit(f"ERRO: os blocos de {sl['titulo']!r} não cabem ({-sobra:.2f} pol. a mais)")
        y = Y0
        for (tit, pt), hb in zip(sl["blocos"], alturas):
            hb += sobra / len(alturas)
            caixa_bloco(s, tit, pt, x_b, y, w_b, hb)
            y += hb + gap
    elif lay == "cadeia":
        y_tab = montar_cadeia(s, sl)
        h_exp = altura_explica(sl["explica"], W) if sl["explica"] else 0.0
        tabela(s, sl["tabela"], X0, y_tab, W, y_fim - y_tab - h_exp - 0.2 * bool(h_exp), sz_min=sz_tab_min,
               onde=sl["titulo"])
        if h_exp:
            caixa_explica(s, sl["explica"], X0, y_fim - h_exp, W, h_exp)
    elif lay == "equacoes":
        montar_equacoes(s, sl, y_fim)
    elif lay == "cartoes":
        montar_cartoes(s, sl, y_fim)
    elif lay == "duas_colunas":
        montar_duas_colunas(s, sl, y_fim)
    else:
        raise SystemExit(f"ERRO: layout desconhecido {lay!r} em {sl['titulo']!r}")
    if sl["selo"] and lay != "figura_painel":
        raise SystemExit(f"ERRO: selo só no layout figura_painel ({sl['titulo']!r})")
    if sl["fontes"]:
        linha_fontes(s, sl["fontes"])
    return xml_slide(sl["titulo"], _nav(sl), s.partes)


def montar_cadeia(s: Slide, sl: dict) -> float:
    """Diagrama da cadeia com as hipóteses sobre as setas. Devolve onde a tabela começa."""
    nos = []
    for parte in sl["cadeia"].split(" → "):
        parte = parte.strip()
        k_par = parte.rindex(" (")
        nos.append((parte[:k_par].strip(), parte[k_par + 2:-1].strip()))
    n = len(nos)
    w_no, gap = 2.18, 0.45
    total = n * w_no + (n - 1) * gap
    x = X0 + (X1 - X0 - total) / 2
    y_no, h_no = Y0 + 0.4, 0.86
    xs = []
    for k, (sim, desc) in enumerate(nos):
        ultimo = k == n - 1
        s.forma(f"Nó {k + 1}", x, y_no, w_no, h_no, adj=14000, fill=CLARO2 if ultimo else VERDE_ESCURO, anchor="ctr",
                ins=(0.06, 0.04, 0.06, 0.04),
                paras=[para([run(sim, 20, VERDE_ESCURO if ultimo else BRANCO, b=True)], "ctr"),
                       para([run(desc, 12, TEXTO if ultimo else "DDEFE0")], "ctr")])
        xs.append(x)
        if k:
            s.seta(f"Seta {k}", x - gap + 0.05, y_no + h_no / 2, x - 0.05, y_no + h_no / 2, cor=VERDE, larg=2.5)
        x += w_no + gap

    def colchete(nome, a, b, y, txt, cor):
        xa, xb = xs[a] + 0.05, xs[b] + w_no - 0.05
        s.forma(nome, xa, y, xb - xa, 0.32, adj=50000, fill=cor, anchor="ctr", ins=(0.04, 0, 0.04, 0),
                paras=[para([run(txt, 12, BRANCO, b=True)], "ctr")])
    colchete("H1", 0, 3, Y0, "H1 · preenchimento: B → Pr(Y = 1)", VERDE)
    colchete("H2", 0, 2, y_no + h_no + 0.08, "H2 · escolha: B → V → π", "3E7C4F")
    s.forma("H3", xs[1] + 0.2, y_no - 0.17, w_no - 0.4, 0.3, adj=50000, fill="C23B33", anchor="ctr",
            ins=(0.02, 0, 0.02, 0), paras=[para([run("H3 · central", 12, BRANCO, b=True)], "ctr")])
    colchete("H4", 3, 4, y_no + h_no + 0.08, "H4 · capacidade líquida", "6B6B6B")
    return y_no + h_no + 0.5


def montar_equacoes(s: Slide, sl: dict, y_fim: float) -> None:
    linhas = [ln for ln in sl["codigo"] if ln.strip()]
    h_cx = 0.6 + 0.62 * len(linhas)
    s.forma("Caixa das equações", X0, Y0, X1 - X0, h_cx, adj=6000, fill=CLARO, line=LINHA, anchor="ctr")
    for k, ln in enumerate(linhas):
        rot, eq = ln.split(":", 1)
        y = Y0 + 0.3 + 0.62 * k
        s.texto(f"Rótulo {k + 1}", X0 + 0.25, y, 2.7, 0.5, [para([run(rot.strip(), 14, VERDE_ESCURO, b=True)])],
                anchor="ctr")
        largura = X1 - X0 - 3.2
        # a maior letra (até 19 pt, nunca abaixo de 14) em que a linha cabe na largura
        sz_eq = max(14.0, min(19.0, largura * 72 / (0.5 * len(re.sub(r"[_^]", "", eq.strip())))))
        s.texto(f"Equação {k + 1}", X0 + 3.05, y, largura, 0.5,
                [para(runs_equacao(eq.strip(), sz_eq, TEXTO))], anchor="ctr")
    y2 = Y0 + h_cx + 0.3
    marcadores(s, sl["marcadores"], X0, y2, X1 - X0, y_fim - y2, sz=SZ_CORPO)


def montar_cartoes(s: Slide, sl: dict, y_fim: float) -> None:
    itens = sl["marcadores"]
    cols, gap = (3 if len(itens) == 3 else 2), 0.3
    rows = math.ceil(len(itens) / cols)
    w = (X1 - X0 - gap * (cols - 1)) / cols
    h = (y_fim - Y0 - gap * (rows - 1)) / rows
    for k, it in enumerate(itens):
        m = re.match(r"\*\*(.+?)\*\*\s*(.*)", it)
        lead, corpo = (m.group(1), m.group(2)) if m else ("", it)
        x = X0 + (k % cols) * (w + gap)
        y = Y0 + (k // cols) * (h + gap)
        s.forma(f"Cartão {k + 1}", x, y, w, h, adj=5000, fill=CLARO, line=LINHA, anchor="t",
                ins=(0.24, 0.2, 0.24, 0.12),
                paras=[para([run(lead if lead.endswith("al.") else lead.rstrip("."), 20, VERDE_ESCURO, b=True)],
                            depois=10),
                       para(runs_md(corpo, 18, TEXTO, cor_neg=VERDE_ESCURO), linha=112)])


def montar_duas_colunas(s: Slide, sl: dict, y_fim: float) -> None:
    """Duas colunas (### no doc 02), cada uma com um cabeçalho e seus marcadores, num cartão claro; o bloco
    "O que isso quer dizer", se houver, ocupa a largura toda embaixo."""
    cols = sl["colunas"]
    if len(cols) != 2:
        raise SystemExit(f"ERRO: layout duas_colunas pede 2 colunas em {sl['titulo']!r}; achou {len(cols)}")
    gap = 0.35
    w = (X1 - X0 - gap) / 2
    h_exp = altura_explica(sl["explica"], X1 - X0) if sl["explica"] else 0.0
    h = y_fim - Y0 - h_exp - 0.2 * bool(h_exp)
    for k, col in enumerate(cols):
        x = X0 + k * (w + gap)
        s.forma(f"Coluna {k + 1}", x, Y0, w, h, adj=4000, fill=CLARO, line=LINHA, anchor="t")
        s.texto(f"Cabeçalho {k + 1}", x + 0.25, Y0 + 0.16, w - 0.5, 0.5,
                [para([run(col["titulo"], 20, VERDE_ESCURO, b=True)])], anchor="t")
        marcadores(s, col["itens"], x + 0.25, Y0 + 0.78, w - 0.5, h - 0.9, sz=17, nome=f"Marcadores {k + 1}",
                   depois=1400)
    if h_exp:
        caixa_explica(s, sl["explica"], X0, y_fim - h_exp, X1 - X0, h_exp)


def notas_do_slide(sl: dict) -> str:
    partes = [texto_puro(sl["notas"])] if sl["notas"] else []
    if sl["cautela"]:
        partes.append("Cautela: " + texto_puro(sl["cautela"]))
    return " ".join(partes) or sl["titulo"]


# --------------------------------------------------------------------------------------------------
# Correções no deck do grupo (plano da banca 2, §2)
# --------------------------------------------------------------------------------------------------

def _norm(t: str) -> str:
    return re.sub(r"\s+", "", t.replace("\xa0", " "))


def _span(xml: str, id_: str) -> tuple[int, int]:
    """Início e fim do elemento (sp, grpSp, graphicFrame, pic, cxnSp) cujo cNvPr tem o id dado."""
    k = xml.index(f'<p:cNvPr id="{id_}"')
    tags = ("p:sp", "p:grpSp", "p:graphicFrame", "p:pic", "p:cxnSp")
    ini, tag = max((max(xml.rfind(f"<{t}>", 0, k), xml.rfind(f"<{t} ", 0, k)), t) for t in tags)
    prof = 0
    for m in re.finditer(rf"<(/?){tag}(?=[ >/])[^>]*?(/?)>", xml[ini:]):
        if m.group(1):
            prof -= 1
        elif not m.group(2):
            prof += 1
        if prof == 0:
            return ini, ini + m.end()
    raise SystemExit(f"ERRO: elemento {id_} sem fechamento")


def remover(xml: str, id_: str) -> str:
    a, b = _span(xml, id_)
    return xml[:a] + xml[b:]


def trocar_paragrafo(xml: str, antigo: str, novo: list[tuple[str, bool]] | None, escopo: str | None = None,
                     sz: float | None = None) -> str:
    """Troca o parágrafo cujo texto é `antigo` (ignorando espaços). `novo=None` apaga o parágrafo."""
    a, b = _span(xml, escopo) if escopo else (0, len(xml))
    trecho = xml[a:b]
    achados = [m for m in re.finditer(r"<a:p>(.*?)</a:p>", trecho, flags=re.S)
               if _norm("".join(re.findall(r"<a:t>([^<]*)</a:t>", m.group(1)))) == _norm(escape(antigo))]
    if len(achados) != 1:
        raise SystemExit(f"ERRO: parágrafo {antigo!r} achado {len(achados)} vezes")
    m = achados[0]
    if novo is None:
        return xml[:a] + trecho[:m.start()] + trecho[m.end():] + xml[a + len(trecho):]
    corpo = m.group(1)
    ppr = re.match(r"\s*(<a:pPr[^>]*/>|<a:pPr[^>]*>.*?</a:pPr>)", corpo, flags=re.S)
    rpr = re.search(r"<a:rPr[^>]*/>|<a:rPr[^>]*>.*?</a:rPr>", corpo, flags=re.S)
    rpr_txt = rpr.group(0) if rpr else '<a:rPr lang="pt-BR"/>'
    runs = []
    for txt, neg in novo:
        r = re.sub(r' b="[01]"', "", rpr_txt)
        if sz is not None:
            r = re.sub(r' sz="\d+"', "", r)
        extra = f' b="{1 if neg else 0}"' + (f' sz="{int(sz * 100)}"' if sz is not None else "")
        r = re.sub(r"<a:rPr", "<a:rPr" + extra, r, count=1)
        if r.endswith("/>") and "</a:rPr>" not in r:
            pass
        runs.append(f"<a:r>{r}<a:t>{escape(txt)}</a:t></a:r>")
    novo_p = f"<a:p>{ppr.group(1) if ppr else ''}{''.join(runs)}</a:p>"
    return xml[:a] + trecho[:m.start()] + novo_p + trecho[m.end():] + xml[a + len(trecho):]


def trocar_texto_runs(xml: str, antigo: str, novo: str) -> tuple[str, int]:
    n = len(re.findall(rf"<a:t>[^<]*{re.escape(antigo)}[^<]*</a:t>", xml))
    return re.sub(rf"(<a:t>[^<]*){re.escape(antigo)}([^<]*</a:t>)", rf"\g<1>{novo}\g<2>", xml), n


def ajustar_xfrm(xml: str, id_: str, x: float | None = None, w: float | None = None) -> str:
    a, b = _span(xml, id_)
    trecho = xml[a:b]
    m = re.search(r'<a:off x="(\d+)" y="(\d+)"/><a:ext cx="(\d+)" cy="(\d+)"/>', trecho)
    nx = pol(x) if x is not None else int(m.group(1))
    nw = pol(w) if w is not None else int(m.group(3))
    trecho = trecho[:m.start()] + f'<a:off x="{nx}" y="{m.group(2)}"/><a:ext cx="{nw}" cy="{m.group(4)}"/>' + trecho[m.end():]
    return xml[:a] + trecho + xml[b:]


def caixa_nota_xml(id_: int, x: float, y: float, w: float, h: float, titulo: str, texto: str) -> str:
    s = Slide()
    s.prox = id_ - 1
    s.forma("Nota da correção", x, y, w, h, adj=6000, fill=CLARO2, line=LINHA, anchor="ctr",
            ins=(0.15, 0.08, 0.15, 0.08),
            paras=[para([run(titulo, 12, VERDE_ESCURO, b=True)], depois=4), para([run(texto, 10.5, TEXTO)], linha=104)])
    return s.partes[0]


def _inserir_antes_do_fim(xml: str, peca: str) -> str:
    k = xml.rindex("</p:spTree>")
    return xml[:k] + peca + xml[k:]


GRADE = "até 0,300 → R$\u00a010 mil; 0,301 a 0,400 → R$\u00a015 mil; acima de 0,400 → R$\u00a020 mil"
TITULO_REGRA = "O IVS 2010 define a bolsa do PMM-E por regra"
NOTAS_REGRA = ("O que é o IVS: índice de vulnerabilidade social, de 0 a 1, com três dimensões (infraestrutura urbana, "
               "capital humano, renda e trabalho). Como entra no PMM-E: a bolsa é fixada por regra sobre o IVS 2010 "
               f"oficial: {GRADE}. A grade do FAQ do edital é outra e não foi a aplicada (auditoria 16).")
NOTA_RETIRADO_T = "II. Crescimento por faixa: gráfico retirado desta versão"
NOTA_RETIRADO = ("O gráfico não sai de output/ por script e agrupava os municípios pela grade do FAQ, não pela "
                 "aplicada. Antes × depois sem comparação não é efeito: o teste com comparação está em Resultados.")


def corrigir(pk, nome_slide: dict[int, str], notas_de: dict[int, str], num: dict) -> list[dict]:
    """Aplica as correções do plano (§2) nos slides do deck do grupo. Devolve o registro das correções."""
    v = lambda c: num[c]["valor"]  # noqa: E731
    reg: list[dict] = []

    def gravar(pos: int, xml: str, o_que: str) -> None:
        pk.gravar(nome_slide[pos], xml)
        reg.append({"slide": pos, "correcao": o_que})

    nota_regra = (f"Regra aplicada: {GRADE}. Reproduz a faixa publicada em {v('R_C1_REPR')} de {v('R_C1_MUN')} "
                  "municípios do ciclo 1; a grade do FAQ não é a aplicada.")
    for pos in (5, 6, 7):
        x = pk.texto(nome_slide[pos])
        x = trocar_paragrafo(x, "A vulnerabilidade social define o piso da bolsa do PMM-E", [(TITULO_REGRA, True)])
        x = trocar_paragrafo(x, "III. O IVS define a renumeração do PMM-E", [("III. O IVS define a remuneração do PMM-E", True)])
        x = trocar_paragrafo(x, "Bolsa-formação mensal por categoria do Índice de Vulnerabilidade Social",
                             [("Bolsa-formação mensal pelo IVS 2010 oficial, cortes em 0,300 e 0,400", False)])
        x = trocar_paragrafo(x, "Vulnerabilidade: Muito alta", [("IVS acima de 0,400", True)])
        x = trocar_paragrafo(x, "Vulnerabilidade: Alta", [("IVS de 0,301 a 0,400", True)])
        x = trocar_paragrafo(x, "Vulnerabilidade: Média,", [("IVS até 0,300", True)])
        x = trocar_paragrafo(x, "baixa e buito baixa", None)
        x = trocar_paragrafo(x, "Instrumento da política. A bolsa de R$ 10.000,00, R$ 15.000,00 ou R$ 20.000,00 é "
                             "fixada, por regra, sobre a categoria de IVS do município.", [(nota_regra, False)], sz=11)
        x = trocar_paragrafo(x, "Fontes: Ipea, Atlas da Vulnerabilidade Social; Edital SGTES/MS nº 3/2025 (item 11.1.4); "
                             "ciclo 1 do PMM-E.", [("Fontes: Ipea, Plataforma IVS; Edital SGTES/MS nº 3/2025; grade "
                                                   "aplicada: auditoria 16; ciclo 1 do PMM-E.", False)])
        gravar(pos, x, "grade da bolsa aplicada; título sem 'piso'; 'remuneração'")
        pk.gravar(notas_de[pos], xml_notas(NOTAS_REGRA))
    # slide 8 (oculto)
    x = pk.texto(nome_slide[8])
    x = trocar_paragrafo(x, "A vulnerabilidade social define o piso da bolsa do PMM-E", [(TITULO_REGRA, True)])
    x = trocar_paragrafo(x, "II. O IVS define o piso da bolsa e organiza o custo do lugar",
                         [("II. O IVS define a bolsa por regra; contínuo, ele controla o custo do lugar", True)])
    x = trocar_paragrafo(x, "Muito alta", [("acima de 0,400", True)], escopo="87")
    x = trocar_paragrafo(x, "Alta", [("0,301 a 0,400", True)], escopo="95")
    x = trocar_paragrafo(x, "Até média", [("até 0,300", True)], escopo="104")
    x = trocar_paragrafo(x, "Bolsa-formação mensal por categoria de IVS 2010",
                         [("Bolsa-formação mensal pelo IVS 2010 oficial", False)])
    x = trocar_paragrafo(x, "Instrumento da política. A bolsa de R$ 10, 15 ou 20 mil é fixada por regra sobre a "
                         "categoria de IVS do município.", [("Instrumento da política: a bolsa de R$ 10, 15 ou 20 mil é "
                                                             "fixada por regra sobre o IVS 2010 oficial.", False)])
    x = trocar_paragrafo(x, "O IVS é o piso, não o critério: em 177 dos 368 municípios do ciclo 1, a faixa publicada "
                         "está acima da categoria de IVS; em nenhum, abaixo.", [(nota_regra, False)])
    gravar(8, x, "frase do 'IVS como piso' (artefato do arquivo errado) retirada; grade aplicada")
    pk.gravar(notas_de[8], xml_notas(NOTAS_REGRA))
    # slide 10 (oculto): categorias do gráfico
    reg.append({"slide": 10, "correcao": "categorias do gráfico pela grade aplicada"})
    # slides 9 e 13: gráfico de crescimento por faixa retirado
    for pos in (9, 13):
        x = pk.texto(nome_slide[pos])
        for id_ in ("25", "27", "29"):
            x = remover(x, id_)
        caixa = caixa_nota_xml(4900, 6.81, 4.0, 6.12, 2.25, NOTA_RETIRADO_T, NOTA_RETIRADO)
        if pos == 13:  # a faixa da pergunta (retângulo 11 e grupo 13) continua por cima da caixa
            a, _ = _span(x, "11")
            x = x[:a] + caixa + x[a:]
        else:
            x = _inserir_antes_do_fim(x, caixa)
        gravar(pos, x, "gráfico de crescimento por faixa (sem proveniência; grade do FAQ) retirado")
    # slides 11 e 14 (ocultos): rebaixados para descritivo
    for pos, retirar, ant_t, ant_s in (
            (11, ["8"], "O programa é importante, e há indícios de efetividade",
             "I. Após o PMEE, o crescimento de especialistas aumentou mais onde o piso da bolsa era maior"),
            (14, ["17", "13"], "Presença de especialistas cresceu em todos os níveis sociais",
             "I. Após o PMEE, o estoque de especialistas cresce mais nas três faixas")):
        x = pk.texto(nome_slide[pos])
        x = trocar_paragrafo(x, ant_t, [("Descritivo: antes × depois por faixa, sem comparação", True)])
        x = trocar_paragrafo(x, ant_s, [("I. Gráfico retirado: faixa pela grade do FAQ e sem proveniência em output/",
                                         True)])
        for id_ in retirar:
            x = remover(x, id_)
        x = _inserir_antes_do_fim(x, caixa_nota_xml(4900, 0.3, 1.45, 7.0, 1.6, "Por que saiu",
                                                    NOTA_RETIRADO.replace("O gráfico", "O gráfico desta página")))
        gravar(pos, x, "'indícios de efetividade' rebaixado para descritivo; gráfico retirado")
    # slides 34 e 35: células, não vagas; SGTES; curso
    alvo = [(f"{v('D_C1_PRE1_PCT')}% na 1ª chamada · {v('D_C1_PRE2_PCT')}% somando a 2ª", True)]
    for pos, antigo_prop, antigo_pct in (
            (34, "Permite calcular a proporção de vagas preenchidas em cada combinação, que, no geral, é:", "35,6%"),
            (35, "Permite calcular a proporção de vagas preenchidas em cada combinação", "30%")):
        x = pk.texto(nome_slide[pos])
        x, n1 = trocar_texto_runs(x, "SGETS", "SGTES")
        x, n2 = trocar_texto_runs(x, "Especialidade", "curso")
        x = trocar_paragrafo(x, antigo_prop, [("Permite calcular a proporção de células (estabelecimento × curso) com "
                                               "alguma confirmação ou homologação:", False)])
        x = trocar_paragrafo(x, antigo_pct, alvo, sz=16)
        x = ajustar_xfrm(x, "13", x=0.1, w=6.18)
        if pos == 34:
            x = trocar_paragrafo(x, "Faixa 1: R$20 mil; Faixa 2: R$15 mil; Faixa 3: R$10 mil mensais",
                                 [(f"Faixa pela regra do IVS 2010: {GRADE}", False)])
            x = trocar_paragrafo(x, "Utilizamos a faixa publicada em cada vaga, observada no quadro de vagas",
                                 [(f"Faixa publicada = regra: {v('R_C1_REPR')} de {v('R_C1_MUN')} municípios do ciclo 1",
                                   False)])
        else:
            x = trocar_paragrafo(x, "Custo territorial agregado", [("IVS: running variable", True)])
            x = trocar_paragrafo(x, "Dados do Atlas Vunerabilidade Social (IVS) nos Municípios Brasileiros (Ipea, 2015), "
                                 "construídos com base no censo de 2010",
                                 [("IVS 2010 oficial do Ipea (Plataforma IVS, Censo 2010)", True)])
            x = trocar_paragrafo(x, "Disponibiliza o IVS e seus três subíndices para os 5.565 municípios",
                                 [(f"IVS e três subíndices para {v('D_IVS_MUN')} municípios", False)])
            x = trocar_paragrafo(x, "Usaremos como proxy para agregar distância da família, aluguel, mercado privado e "
                                 "esforço clínico", [("É a running variable: entra contínuo (spline) e controla o custo "
                                                      "do lugar", False)])
            x = trocar_paragrafo(x, "Permite aproximar as desvantagens não monetárias do local",
                                 [("Só a bolsa (com as regras do mesmo corte) salta em 0,300 e 0,400", True)])
        gravar(pos, x, f"células, não vagas ({v('D_C1_PRE1_PCT')}% e {v('D_C1_PRE2_PCT')}%); SGTES ({n1}); curso ({n2})"
               + ("; IVS como running variable" if pos == 35 else "; grade aplicada"))
    # slide 31: notas com conversa colada (repetia a contagem do arquivo errado)
    pk.gravar(notas_de[31], xml_notas("Divisor do apêndice."))
    reg.append({"slide": 31, "correcao": "notas trocadas por uma linha neutra"})
    return reg


def corrigir_grafico_slide10(pk, nome_slide: dict[int, str]) -> None:
    rels = pk.texto(BF._rels_de(nome_slide[10]))
    graficos = [BF._alvo(nome_slide[10], t) for t in re.findall(r'Target="([^"]*charts/chart\d+\.xml)"', rels)]
    trocas = {"Faixa 3 (Vulnerabilidade baixa)": "Faixa 3 (IVS até 0,300)",
              "Faixa 2 (Vulnerabilidade intermediária)": "Faixa 2 (IVS de 0,301 a 0,400)",
              "Faixa 1 (Vulnerabilidade alta)": "Faixa 1 (IVS acima de 0,400)"}
    feitos = 0
    for g in graficos:
        x = pk.texto(g)
        for a, b in trocas.items():
            rotulo, resto = a.split(" (", 1)
            x, n = re.subn(re.escape(rotulo) + r"\s+\(" + re.escape(resto), b, x)
            feitos += min(n, 1)
        pk.gravar(g, x)
    if feitos != 3:
        raise SystemExit(f"ERRO: categorias do gráfico do slide 10 trocadas {feitos} vezes, esperado 3")


# --------------------------------------------------------------------------------------------------
# Empacotamento
# --------------------------------------------------------------------------------------------------

REL_SLIDE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
REL_IMG = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"


# Referências a outro slide, digitadas no texto de um slide do grupo: (texto, slide do grupo a que se refere)
REFERENCIAS_A_SLIDE = {20: [("slide 11", 19)]}  # o 19 do grupo trazia o número 11 digitado
NOME_NUMERO = "Text Placeholder 1"
CANTO_NUMERO = (11_000_000, 6_000_000)  # EMU: a caixa do número fica no canto inferior direito
LARGURA_NUMERO = 500_000  # EMU: largura mínima para dois dígitos não quebrarem
GUID_SLIDENUM = "{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}"


def retitular(xml: str, novo: str) -> str:
    """Troca o texto do título (placeholder de título) por `novo`, com a formatação do primeiro trecho."""
    k = xml.find('<p:ph type="title"')
    if k < 0:
        raise SystemExit("ERRO: slide sem placeholder de título")
    id_ = re.search(r'<p:cNvPr id="(\d+)"', xml[xml.rindex('<p:cNvPr id="', 0, k):]).group(1)
    a, b = _span(xml, id_)
    trecho = xml[a:b]
    paras = [p for p in re.finditer(r"<a:p>(.*?)</a:p>", trecho, flags=re.S) if re.search(r"<a:t>[^<]+</a:t>", p.group(1))]
    if not paras:
        raise SystemExit("ERRO: título vazio")
    corpo = paras[0].group(1)
    ppr = re.match(r"\s*(<a:pPr[^>]*/>|<a:pPr[^>]*>.*?</a:pPr>)", corpo, flags=re.S)
    rpr = re.search(r"<a:rPr[^>]*/>|<a:rPr[^>]*>.*?</a:rPr>", corpo, flags=re.S)
    novo_p = f"<a:p>{ppr.group(1) if ppr else ''}<a:r>{rpr.group(0) if rpr else ''}<a:t>{escape(novo)}</a:t></a:r></a:p>"
    out, ult = [], 0
    for k, p in enumerate(paras):
        out.append(trecho[ult:p.start()] + (novo_p if k == 0 else ""))
        ult = p.end()
    trecho = "".join(out) + trecho[ult:]
    return xml[:a] + trecho + xml[b:]


def numerar(xml: str, pos: int) -> tuple[str, int]:
    """O número de página digitado à mão (caixa só com dígitos, no canto inferior direito) vira o campo do número do
    slide; a caixa ganha largura para dois dígitos, mantendo a borda direita. Números dentro do conteúdo ficam."""
    n = 0
    for sp in re.findall(r"<p:sp>.*?</p:sp>", xml, flags=re.S):
        nome = re.search(r'<p:cNvPr id="\d+" name="([^"]*)"', sp).group(1)
        texto = "".join(re.findall(r"<a:t>([^<]*)</a:t>", sp)).strip()
        pos_xfrm = re.search(r'<a:off x="(\d+)" y="(\d+)"/><a:ext cx="(\d+)" cy="(\d+)"/>', sp)
        if (nome != NOME_NUMERO or not re.fullmatch(r"\d{1,2}", texto) or "<a:fld" in sp or not pos_xfrm
                or int(pos_xfrm.group(1)) < CANTO_NUMERO[0] or int(pos_xfrm.group(2)) < CANTO_NUMERO[1]):
            continue
        novo, k = re.subn(r"<a:r>(<a:rPr[^>]*/>|<a:rPr[^>]*>.*?</a:rPr>)?<a:t>\d{1,2}</a:t></a:r>",
                          lambda m: f'<a:fld id="{GUID_SLIDENUM}" type="slidenum">{m.group(1) or ""}<a:t>{pos}</a:t></a:fld>',
                          sp, count=1, flags=re.S)
        if k != 1:
            raise SystemExit("ERRO: número de página em mais de um trecho")
        x0, y0, cx, cy = (int(g) for g in pos_xfrm.groups())
        if cx < LARGURA_NUMERO:
            novo = novo.replace(pos_xfrm.group(0), f'<a:off x="{x0 + cx - LARGURA_NUMERO}" y="{y0}"/>'
                                                   f'<a:ext cx="{LARGURA_NUMERO}" cy="{cy}"/>', 1)
        xml = xml.replace(sp, novo, 1)
        n += 1
    return xml, n


# --------------------------------------------------------------------------------------------------
# Deck curto
# --------------------------------------------------------------------------------------------------

SZ_LINHA_CURTA = 18.0       # pt das linhas curtas sob a figura
SZ_LADO = 16.0              # pt das linhas na coluna ao lado da figura
SZ_ITEM_TEXTO = 24.0        # pt dos itens dos slides só de texto (hipóteses, conclusão)
SZ_ITEM_MULTI = 20.0        # pt dos itens que pedem mais de uma linha (antes e depois de um resultado)
MAX_LINHAS_ITEM = 3         # linhas por item nesses slides
H_LINHA_CURTA = 0.46        # pol.
MAX_LINHAS_FIGURA = 2       # linhas curtas por slide de figura ou tabela, contando a cautela
MAX_LINHAS_TEXTO = 4        # itens por slide só de texto, contando a cautela
MAX_TITULO_CURTO = 58       # caracteres: o título não pode encostar no logotipo do template
FRACAO_MIN_FIGURA = 0.72    # com as linhas embaixo, a figura tem de ocupar ao menos esta fração da largura
W_COLUNA_MIN = 3.4          # pol.: coluna de texto ao lado da figura
LAYOUTS_CURTOS = ("curto_figura", "curto_tabela", "curto_texto", "curto_ficha", "curto_capa", "curto_hipotese",
                  "curto_espec")
# Estrutura obrigatória da versão final (doc 06, decisão do autor de 26/10/2026): as seções do doc 04, nesta ordem
SECOES_CURTO = ("Hipótese", "Dados", "Análise descritiva", "Metodologia", "Identificação", "Resultados", "Robustez",
                "Discussão")
MAX_PALAVRAS = 30           # palavras visíveis por slide, fora o título, a figura e a linha de fontes (doc 06, §2)
MAX_LINHAS_ESPEC = 4        # linhas curtas por slide de especificação: equação, outcome, amostra ou comparação, cuidado
CINZA_FUNDO, CINZA_LINHA, CINZA_TEXTO, CINZA_ROTULO = "F2F2F0", "C9C9C4", "8A8A85", "A3A39E"
PLANO_B = "plano B"          # marca das hipóteses secundárias (H2 e H3): rótulo e título em cinza
COR_TITULO_PLANO_B = "C4CCC6"  # título cinza-claro sobre a faixa verde do template


def linhas_curtas(sl: dict) -> list[tuple[str, bool]]:
    """As linhas de texto do slide curto, na ordem: (texto, é_cautela)."""
    return [(m, False) for m in sl["marcadores"]] + ([(sl["cautela"], True)] if sl["cautela"] else [])


def limite_linhas(sl: dict) -> int:
    """No máximo duas linhas, contando a cautela (quatro nos slides só de texto e nas especificações); o doc 04 pode
    pedir outro limite num slide com `<!-- linhas: N -->`."""
    if sl["max_linhas"]:
        return sl["max_linhas"]
    if sl["layout"] == "curto_espec":
        return MAX_LINHAS_ESPEC
    return MAX_LINHAS_TEXTO if sl["layout"] in ("curto_texto", "curto_capa", "curto_hipotese") else MAX_LINHAS_FIGURA


def palavras(txt: str) -> int:
    """Palavras visíveis de um texto: tokens com letra ou algarismo (setas, "·", "=", "×" e "+" soltos não contam)."""
    return sum(1 for w in texto_puro(txt).replace("**", "").split() if re.search(r"[0-9A-Za-zÀ-ÿ]", w))


def palavras_visiveis(sl: dict) -> int:
    """Palavras na tela, fora o título, a figura e a linha de fontes: linhas, cautela, selo e células da tabela."""
    n = sum(palavras(t) for t, _ in linhas_curtas(sl)) + (palavras(sl["selo"]) if sl["selo"] else 0)
    return n + sum(palavras(c) for linha in sl["tabela"] for c in linha)


def conferir_estrutura(slides: list[dict]) -> None:
    """As seções do doc 04 são as da estrutura obrigatória (doc 06), nesta ordem, cada uma uma vez."""
    vistas: list[str] = []
    for sl in slides:
        if not vistas or vistas[-1] != sl["secao"]:
            vistas.append(sl["secao"])
    if tuple(vistas) != SECOES_CURTO:
        raise SystemExit(f"ERRO: seções do deck curto fora da estrutura obrigatória (doc 06): {vistas}")


def cabe_numa_linha(txt: str) -> bool:
    return linhas_necessarias(texto_puro(txt), SZ_LINHA_CURTA, X1 - X0 - 0.5, fator=0.54) <= 1


def conferir_curto(sl: dict) -> None:
    """Para se o slide fugir do formato curto: layout, número de linhas, linha que quebra, blocos longos, título."""
    lay = sl["layout"]
    if lay not in LAYOUTS_CURTOS:
        raise SystemExit(f"ERRO: layout {lay!r} fora do deck curto em {sl['titulo']!r}")
    if len(sl["titulo"]) > MAX_TITULO_CURTO:
        raise SystemExit(f"ERRO: título com {len(sl['titulo'])} caracteres (máximo {MAX_TITULO_CURTO}): {sl['titulo']!r}")
    if sl["explica"] or sl["blocos"] or sl["paragrafos"] or sl["colunas"] or sl["cadeia"] or sl["codigo"]:
        raise SystemExit(f"ERRO: o deck curto não leva blocos de texto ({sl['titulo']!r})")
    if palavras_visiveis(sl) > MAX_PALAVRAS:
        raise SystemExit(f"ERRO: {palavras_visiveis(sl)} palavras visíveis em {sl['titulo']!r}; o teto é {MAX_PALAVRAS}")
    if lay == "curto_ficha":  # ficha de especificação (pedido do autor): só a tabela, sem limite de linhas
        if not sl["tabela"] or sl["marcadores"] or sl["imagem"] is not None:
            raise SystemExit(f"ERRO: a ficha {sl['titulo']!r} leva só a tabela (e, se houver, a cautela)")
        return
    if lay == "curto_espec" and (not sl["marcadores"] or re.match(r"\*\*", sl["marcadores"][0])
                                 or not all(re.match(r"\*\*", m) for m in sl["marcadores"][1:])):
        raise SystemExit(f"ERRO: a especificação {sl['titulo']!r} abre com a equação (sem rótulo) e segue com linhas "
                         "rotuladas")
    if lay == "curto_hipotese" and sum("central" in m.split("**")[1] for m in sl["marcadores"]) != 1:
        raise SystemExit(f"ERRO: o slide de hipóteses {sl['titulo']!r} tem de ter uma, e só uma, hipótese central")
    n = len(linhas_curtas(sl))
    if n > limite_linhas(sl):
        raise SystemExit(f"ERRO: {n} linhas em {sl['titulo']!r}; o limite é {limite_linhas(sl)}")
    if lay == "curto_figura" and sl["imagem"] is None:
        raise SystemExit(f"ERRO: slide de figura sem figura: {sl['titulo']!r}")
    if lay == "curto_tabela" and not sl["tabela"]:
        raise SystemExit(f"ERRO: slide de tabela sem tabela: {sl['titulo']!r}")
    if lay == "curto_tabela":
        for txt, _ in linhas_curtas(sl):
            if not cabe_numa_linha(txt):
                raise SystemExit(f"ERRO: a linha {texto_puro(txt)!r} de {sl['titulo']!r} não cabe numa linha só")


def _linha_curta(s: Slide, txt: str, cautela: bool, y: float, h: float = H_LINHA_CURTA) -> None:
    if cautela:
        s.forma("Cautela", X0, y, X1 - X0, h, adj=12000, fill=CLARO2, anchor="ctr",
                ins=(0.18, 0.02, 0.18, 0.02),
                paras=[para(runs_md(txt.replace("**", ""), SZ_LINHA_CURTA, VERDE_ESCURO, negrito=True), "l",
                            linha=100)])
    else:
        s.forma("Linha", X0, y, X1 - X0, h, geom="rect", anchor="ctr", ins=(0.18, 0.02, 0.18, 0.02),
                paras=[para(runs_md(txt, SZ_LINHA_CURTA, TEXTO, cor_neg=VERDE_ESCURO), "l", linha=100)])


H_LINHA_DUPLA = 0.8         # pol.: linha curta que quebra em duas, sob uma figura larga


def _altura_linha_baixo(txt: str) -> float | None:
    """Altura da linha sob a figura: uma ou duas linhas de texto; None se pedir mais de duas."""
    n = linhas_necessarias(texto_puro(txt).replace("**", ""), SZ_LINHA_CURTA, X1 - X0 - 0.5, fator=0.54)
    return H_LINHA_CURTA if n == 1 else (H_LINHA_DUPLA if n == 2 else None)


def _altura_item_lado(txt: str, w: float) -> float:
    return altura_texto(txt.replace("**", ""), SZ_LADO, w - 0.4) * 1.06 + 0.26


def plano_curto_figura(sl: dict) -> dict:
    """Decide onde vão as linhas do slide de figura. Embaixo, cada uma numa linha só, se a figura ainda ocupar a
    largura; senão (figura alta, ou linha que não cabe numa linha só), numa coluna ao lado da figura, para não
    deixar faixas vazias dos lados (pedido do autor: nenhum espaço vazio grande). O selo, se houver, fica sob a
    figura. Para se nada couber."""
    W = X1 - X0
    linhas = linhas_curtas(sl)
    with Image.open(sl["imagem"]) as im:
        a = im.size[0] / im.size[1]
    h_selo = (H_SELO + 0.18) if sl["selo"] else 0.0
    n = len(linhas)
    alturas = [_altura_linha_baixo(t) for t, _ in linhas]
    if None not in alturas:
        # embaixo: a figura larga ocupa a largura e as linhas (até duas de texto cada) ficam sob ela
        y_lin = Y_FONTES - 0.08 - sum(alturas) - max(n - 1, 0) * 0.06
        h_area = y_lin - 0.14 - Y0 - h_selo
        w_baixo = min(W, h_area * a)
        if w_baixo >= FRACAO_MIN_FIGURA * W:
            return dict(modo="baixo", y_lin=y_lin, w=w_baixo, h=w_baixo / a, alturas=alturas)
    # ao lado: os itens numa coluna à direita; a cautela (e o selo) sob a figura, na largura dela
    h_tot = Y_FONTES - 0.1 - Y0
    itens = [t for t, c in linhas if not c]
    caut = next((t for t, c in linhas if c), "")
    w_fig = W - W_COLUNA_MIN - 0.3
    while w_fig > 4.0:
        h_caut = (_altura_item_lado(caut, w_fig) + 0.18) if caut else 0.0
        w_f = min(w_fig, (h_tot - h_selo - h_caut) * a)
        w_col = W - w_f - 0.3
        h_txt = sum(_altura_item_lado(t, w_col) for t in itens) + 0.18 * max(len(itens) - 1, 0)
        if h_txt <= h_tot:
            return dict(modo="lado", w=w_f, h=w_f / a, w_col=w_col, h_txt=h_txt, h_tot=h_tot, h_selo=h_selo,
                        h_caut=h_caut, caut=caut, itens=itens)
        w_fig -= 0.1
    raise SystemExit(f"ERRO: as linhas de {sl['titulo']!r} não cabem ao lado da figura")


def montar_curto(sl: dict, rid_img: str | None) -> str:
    conferir_curto(sl)
    s = Slide()
    W = X1 - X0
    linhas = linhas_curtas(sl)
    lay = sl["layout"]
    if lay == "curto_texto":
        itens = [t for t, c in linhas if not c]
        caut = [t for t, c in linhas if c]
        y_fim = Y_FONTES - 0.1
        if caut:
            y_c = y_fim - H_LINHA_CURTA
            _linha_curta(s, caut[0], True, y_c)
            y_fim = y_c - 0.25
        gap = 0.22
        partes = []
        for it in itens:
            m = re.match(r"\*\*(.+?)\*\*\s*(.*)", it)
            partes.append((m.group(1), m.group(2)) if m else ("", it))
        rotulos = [r for r, _ in partes if r]

        def larg_rotulo(sz: float) -> float:
            return max([len(r) * 0.6 * sz / 72 + 0.5 for r in rotulos] + [1.2]) if rotulos else 0.0

        sz = SZ_ITEM_TEXTO
        w_rot = larg_rotulo(sz)
        n_lin = [linhas_necessarias(texto_puro(c), sz, W - w_rot - 0.65, fator=0.54) for _, c in partes]
        if max(n_lin) > 1:
            # antes/depois de um resultado (pedido do autor): até 3 linhas por item, em letra menor
            sz = SZ_ITEM_MULTI
            w_rot = larg_rotulo(sz)
            n_lin = [linhas_necessarias(texto_puro(c), sz, W - w_rot - 0.65, fator=0.54) for _, c in partes]
            if max(n_lin) > MAX_LINHAS_ITEM:
                raise SystemExit(f"ERRO: item de {sl['titulo']!r} com mais de {MAX_LINHAS_ITEM} linhas")
        alturas = [max(1.05, k * sz * 1.3 / 72 + 0.34) for k in n_lin]
        disp = y_fim - Y0 - 0.1 - gap * (len(itens) - 1)
        if sum(alturas) > disp + 1e-6:
            raise SystemExit(f"ERRO: os itens de {sl['titulo']!r} não cabem ({sum(alturas) - disp:.2f} pol. a mais)")
        extra = min(0.45, (disp - sum(alturas)) / len(itens))
        y = Y0 + 0.1
        for (rotulo, corpo), h_item in zip(partes, alturas):
            h_item += extra
            w_r = w_rot if rotulo else 0.0
            b_ = PLANO_B in rotulo  # plano B (decisão do autor de 26/10/2026): em cinza, visivelmente secundário
            if rotulo:
                s.forma("Rótulo plano B" if b_ else "Rótulo", X0, y, w_r, h_item, adj=10000,
                        fill=CINZA_ROTULO if b_ else VERDE_ESCURO, anchor="ctr",
                        paras=[para([run(rotulo, sz, BRANCO, b=True)], "ctr")])
            s.forma("Item plano B" if b_ else "Item", X0 + w_r + 0.15, y, W - w_r - 0.15, h_item, adj=6000,
                    fill=CINZA_FUNDO if b_ else "F4F8F5", line=CINZA_LINHA if b_ else VERDE,
                    line_w=1.0, anchor="ctr", ins=(0.25, 0.04, 0.25, 0.04),
                    paras=[para(runs_md(corpo, sz, CINZA_TEXTO if b_ else TEXTO,
                                        cor_neg=CINZA_TEXTO if b_ else VERDE_ESCURO), "l", linha=102)])
            y += h_item + gap
    elif lay == "curto_capa":
        # capa curta e frase de destaque (pedidos do autor): uma linha grande no meio do slide e, se houver, a cautela
        if len(itens := [t for t, c in linhas if not c]) != 1:
            raise SystemExit(f"ERRO: a frase {sl['titulo']!r} leva uma linha só")
        y_fim = Y_FONTES - 0.1
        if sl["cautela"]:
            y_c = y_fim - H_LINHA_CURTA
            _linha_curta(s, sl["cautela"], True, y_c)
            y_fim = y_c - 0.3
        h = 2.6
        y = Y0 + (y_fim - Y0 - h) / 2
        s.forma("Frase", X0 + 0.4, y, W - 0.8, h, adj=8000, fill=VERDE_ESCURO, anchor="ctr",
                ins=(0.45, 0.1, 0.45, 0.1), paras=[para(runs_md(itens[0], 30, BRANCO, cor_neg="DDEFE0"), "ctr")])
    elif lay == "curto_hipotese":
        # hipóteses (doc 06): a central em destaque, em cima e maior; as de plano B em cinza, visivelmente secundárias
        itens = [t for t, c in linhas if not c]
        caut = [t for t, c in linhas if c]
        y_fim = Y_FONTES - 0.1
        if caut:
            y_c = y_fim - H_LINHA_CURTA
            _linha_curta(s, caut[0], True, y_c)
            y_fim = y_c - 0.25
        partes = [re.match(r"\*\*(.+?)\*\*\s*(.*)", it).groups() for it in itens]
        central = [p for p in partes if "central" in p[0]]
        planos = [p for p in partes if "central" not in p[0]]
        gap, w_rot = 0.25, 2.9
        h_c = (y_fim - Y0 - gap * len(planos)) * 0.5
        h_b = (y_fim - Y0 - h_c - gap * len(planos)) / max(len(planos), 1)
        y = Y0
        for (rot, corpo), h_i, eh_central in [(central[0], h_c, True)] + [(p, h_b, False) for p in planos]:
            sz = 28 if eh_central else 20
            s.forma("Rótulo central" if eh_central else "Rótulo plano B", X0, y, w_rot, h_i, adj=10000,
                    fill=VERDE_ESCURO if eh_central else CINZA_ROTULO, anchor="ctr",
                    paras=[para([run(rot, sz, BRANCO, b=True)], "ctr")])
            s.forma("Hipótese central" if eh_central else "Hipótese plano B", X0 + w_rot + 0.15, y,
                    W - w_rot - 0.15, h_i, adj=6000, fill="F4F8F5" if eh_central else CINZA_FUNDO,
                    line=VERDE if eh_central else CINZA_LINHA, line_w=2.0 if eh_central else 1.0, anchor="ctr",
                    ins=(0.3, 0.04, 0.3, 0.04),
                    paras=[para(runs_md(corpo, sz, TEXTO if eh_central else CINZA_TEXTO,
                                        cor_neg=VERDE_ESCURO if eh_central else CINZA_TEXTO, negrito=eh_central),
                                "l", linha=102)])
            y += h_i + gap
    elif lay == "curto_espec":
        # especificação (pedido do autor: "texto demais"): a equação em palavras numa linha grande, no centro, e
        # embaixo as linhas curtas rotuladas (outcome, amostra ou comparação, cuidado); o resto vai para as notas
        eq, rotuladas = linhas[0][0], [re.match(r"\*\*(.+?)\*\*\s*(.*)", t_).groups() for t_, _ in linhas[1:]]
        y_fim = Y_FONTES - 0.1
        h_eq = 1.75
        s.forma("Equação em palavras", X0, Y0 + 0.05, W, h_eq, adj=8000, fill=VERDE_ESCURO, anchor="ctr",
                ins=(0.4, 0.08, 0.4, 0.08), paras=[para(runs_md(eq, 28, BRANCO, cor_neg="DDEFE0"), "ctr")])
        gap, w_rot, sz = 0.2, 2.4, 20.0
        y = Y0 + 0.05 + h_eq + 0.3
        h_i = (y_fim - y - gap * (len(rotuladas) - 1)) / len(rotuladas)
        for rot, corpo in rotuladas:
            s.forma("Rótulo", X0, y, w_rot, h_i, adj=10000, fill=VERDE_ESCURO, anchor="ctr",
                    paras=[para([run(rot, sz, BRANCO, b=True)], "ctr")])
            s.forma("Item", X0 + w_rot + 0.15, y, W - w_rot - 0.15, h_i, adj=6000, fill="F4F8F5", line=VERDE,
                    line_w=1.0, anchor="ctr", ins=(0.25, 0.04, 0.25, 0.04),
                    paras=[para(runs_md(corpo, sz, TEXTO, cor_neg=VERDE_ESCURO), "l", linha=102)])
            y += h_i + gap
    elif lay == "curto_ficha":
        y_fim = Y_FONTES - 0.1
        if sl["cautela"]:
            y_c = y_fim - H_LINHA_CURTA
            _linha_curta(s, sl["cautela"], True, y_c)
            y_fim = y_c - 0.14
        tabela(s, sl["tabela"], X0, Y0 + 0.02, W, y_fim - Y0 - 0.02, sz_max=18, sz_min=SZ_TAB_CORPO,
               onde=sl["titulo"])
    elif lay == "curto_figura":
        p = plano_curto_figura(sl)
        if p["modo"] == "baixo":
            y_l = p["y_lin"]
            for (txt, caut), h_l in zip(linhas, p["alturas"]):
                _linha_curta(s, txt, caut, y_l, h_l)
                y_l += h_l + 0.06
            y_fim = p["y_lin"] - 0.14
            h_bloco = p["h"] + ((H_SELO + 0.18) if sl["selo"] else 0.0)
            y_img = Y0 + (y_fim - Y0 - h_bloco) / 2
            x_img = X0 + (W - p["w"]) / 2
            imagem(s, rid_img, x_img, y_img, p["w"], p["h"], sl["alt"])
            if sl["selo"]:
                caixa_selo(s, sl["selo"], x_img, y_img + p["h"] + 0.18, p["w"])
        else:
            h_bloco = p["h"] + p["h_selo"] + p["h_caut"]
            y_img = Y0 + max(0.0, (p["h_tot"] - h_bloco) / 2)
            imagem(s, rid_img, X0, y_img, p["w"], p["h"], sl["alt"])
            y_b = y_img + p["h"] + 0.18
            if sl["selo"]:
                caixa_selo(s, sl["selo"], X0, y_b, p["w"])
                y_b += H_SELO + 0.18
            if p["caut"]:
                s.forma("Cautela", X0, y_b, p["w"], p["h_caut"] - 0.18, adj=8000, fill=CLARO2, anchor="ctr",
                        ins=(0.2, 0.06, 0.2, 0.06),
                        paras=[para(runs_md(p["caut"].replace("**", ""), SZ_LADO, VERDE_ESCURO, negrito=True), "l",
                                    linha=100)])
            x_c, w_c = X0 + p["w"] + 0.3, p["w_col"]
            folga = (p["h_tot"] - p["h_txt"]) / max(len(p["itens"]), 1)
            y = Y0
            for txt in p["itens"]:
                h_it = _altura_item_lado(txt, w_c) + min(folga, 0.6)
                s.forma("Linha", x_c, y, w_c, h_it, adj=6000, fill="F4F8F5", line=VERDE, line_w=1.0,
                        anchor="ctr", ins=(0.2, 0.06, 0.2, 0.06),
                        paras=[para(runs_md(txt, SZ_LADO, TEXTO, cor_neg=VERDE_ESCURO), "l", linha=100)])
                y += h_it + 0.18
    else:
        n = len(linhas)
        y_lin = Y_FONTES - 0.08 - n * H_LINHA_CURTA - max(n - 1, 0) * 0.06
        for k, (txt, caut) in enumerate(linhas):
            _linha_curta(s, txt, caut, y_lin + k * (H_LINHA_CURTA + 0.06))
        y_fim = y_lin - 0.14
        # poucas palavras (pedido do autor): letra grande e a tabela ocupando a área, sem faixa vazia embaixo
        tabela(s, sl["tabela"], X0, Y0 + 0.05, W, y_fim - Y0 - 0.05, sz_max=24, sz_min=SZ_TAB_CORPO,
               onde=sl["titulo"])
    if sl["fontes"]:
        linha_fontes(s, sl["fontes"])
    return xml_slide_curto(sl["titulo"], sl["secao"], s.partes)


def xml_slide_curto(titulo: str, secao: str, partes: list[str]) -> str:
    """O slide do template, com a navegação do rodapé trocada pelas oito seções da estrutura obrigatória (doc 06) e
    a seção do slide em negrito."""
    x = xml_slide(titulo, "", partes)
    if PLANO_B in titulo:  # plano B: o título fica cinza, visivelmente secundário (decisão do autor de 26/10/2026)
        k = x.index('name="Título"')
        x = x[:k] + x[k:].replace('<a:srgbClr val="FFFFFF"/>', f'<a:srgbClr val="{COR_TITULO_PLANO_B}"/>', 1)
    m = re.search(r'(<p:sp><p:nvSpPr><p:cNvPr id="4" name="Navegação do rodapé"/>.*?<a:p>)(.*?)(</a:p>)', x, flags=re.S)
    runs = []
    for k, sec in enumerate(SECOES_CURTO):
        sep = "  |  " if k < len(SECOES_CURTO) - 1 else ""
        if sec == secao:
            runs.append(f'<a:r><a:rPr lang="pt-BR" sz="1000" b="1" dirty="0"><a:solidFill><a:srgbClr val="114719"/>'
                        f'</a:solidFill><a:latin typeface="{FONTE}"/></a:rPr><a:t>{escape(sec)}</a:t></a:r>'
                        f'<a:r><a:rPr lang="pt-BR" sz="1000" dirty="0"><a:latin typeface="{FONTE}"/></a:rPr>'
                        f'<a:t xml:space="preserve">{sep}</a:t></a:r>')
        else:
            runs.append(f'<a:r><a:rPr lang="pt-BR" sz="1000" dirty="0"><a:latin typeface="{FONTE}"/></a:rPr>'
                        f'<a:t xml:space="preserve">{escape(sec)}{sep}</a:t></a:r>')
    return x[:m.start(2)] + "".join(runs) + x[m.end(2):]


def construir_curto(deck: Path, saida: Path) -> dict:
    """Deck curto: o deck do grupo entra só como template (mestre, layout, rodapé); os slides vêm do doc 04."""
    slides_doc = ler_slides(DOC_CURTO)
    if any(sl["apendice"] for sl in slides_doc):
        raise SystemExit("ERRO: o deck curto não tem apêndice")
    conferir_estrutura(slides_doc)
    for sl in slides_doc:
        conferir_curto(sl)
    pk = Pacote(deck)
    pres = pk.texto("ppt/presentation.xml")
    rels = pk.texto("ppt/_rels/presentation.xml.rels")
    ct = pk.texto("[Content_Types].xml")
    entradas = re.findall(r'<p:sldId id="(\d+)" r:id="(rId\d+)"/>', re.search(r"<p:sldIdLst>(.*?)</p:sldIdLst>", pres,
                                                                              flags=re.S).group(1))
    if len(entradas) != N_GRUPO:
        raise SystemExit(f"ERRO: o deck do grupo tinha 36 slides; este tem {len(entradas)}")
    rid_alvo = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship Id="(rId\d+)"[^>]*Target="([^"]*)"', rels)}
    if 'Extension="png"' not in ct:
        ct = ct.replace("</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')
    n_slide = max(int(re.search(r"slide(\d+)\.xml", n).group(1)) for n in pk.partes if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
    n_notas = max(int(re.search(r"notesSlide(\d+)\.xml", n).group(1)) for n in pk.partes if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n))
    prox_rid = max(int(r[3:]) for r in rid_alvo) + 1
    prox_id = max(int(i) for i, _ in entradas) + 1
    layout = "slideLayout14.xml"
    if 'name="1_Title Slide"' not in pk.texto("ppt/slideLayouts/" + layout):
        raise SystemExit("ERRO: layout 1_Title Slide não está em slideLayout14.xml")
    # tira os slides do grupo da apresentação (o pacote é podado depois pelo que fica alcançável)
    rels = re.sub(r'<Relationship Id="rId\d+" Type="[^"]*/relationships/slide" Target="slides/[^"]*"/>', "", rels)
    itens, midias, lista = [], {}, []
    for k, sl in enumerate(slides_doc):
        ns, nn, rid = n_slide + 1 + k, n_notas + 1 + k, f"rId{prox_rid + k}"
        rels_slide = [f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/{layout}"/>',
                      f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{nn}.xml"/>']
        rid_img = None
        if sl["imagem"] is not None:
            if not sl["imagem"].exists() or "/output/" not in sl["imagem"].as_posix():
                raise SystemExit(f"ERRO: figura fora de output/ ou ausente: {sl['imagem']}")
            rel_out = sl["imagem"].relative_to(ROOT).as_posix()
            if rel_out not in midias:
                midias[rel_out] = f"ppt/media/curto_{len(midias) + 1:02d}_{sl['imagem'].stem}.png"
                pk.gravar(midias[rel_out], sl["imagem"].read_bytes())
            rid_img = "rId3"
            rels_slide.append(f'<Relationship Id="rId3" Type="{REL_IMG}" Target="../media/{Path(midias[rel_out]).name}"/>')
        pk.gravar(f"ppt/slides/slide{ns}.xml", montar_curto(sl, rid_img))
        pk.gravar(f"ppt/slides/_rels/slide{ns}.xml.rels",
                  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  + "".join(rels_slide) + "</Relationships>")
        pk.gravar(f"ppt/notesSlides/notesSlide{nn}.xml", xml_notas(notas_do_slide(sl)))
        pk.gravar(f"ppt/notesSlides/_rels/notesSlide{nn}.xml.rels",
                  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/>'
                  f'<Relationship Id="rId2" Type="{REL_SLIDE}" Target="../slides/slide{ns}.xml"/>'
                  '</Relationships>')
        rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="{REL_SLIDE}" Target="slides/slide{ns}.xml"/></Relationships>')
        ct = ct.replace("</Types>",
                        f'<Override PartName="/ppt/slides/slide{ns}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
                        f'<Override PartName="/ppt/notesSlides/notesSlide{nn}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>')
        itens.append((str(prox_id + k), rid))
        lista.append(dict(posicao=k + 1, titulo=sl["titulo"], secao=sl["secao"], layout=sl["layout"],
                          linhas=[texto_puro(t) for t, _ in linhas_curtas(sl)], palavras=palavras_visiveis(sl),
                          figura=sl["imagem"].relative_to(ROOT).as_posix() if sl["imagem"] else None))
    nova = "<p:sldIdLst>" + "".join(f'<p:sldId id="{i}" r:id="{r}"/>' for i, r in itens) + "</p:sldIdLst>"
    pres = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", lambda _m: nova, pres, count=1, flags=re.S)
    # seções do PowerPoint do grupo apontariam para slides que saíram: a lista de seções sai junto
    pres = re.sub(r"<p:ext uri=\"\{521415D9-36F7-43E2-AB2F-B90AF26B5E84\}\">.*?</p:ext>", "", pres, flags=re.S)
    pk.gravar("ppt/presentation.xml", pres)
    pk.gravar("ppt/_rels/presentation.xml.rels", rels)
    pk.gravar("[Content_Types].xml", ct)
    manter = BF.alcancaveis(pk)
    ct_p = re.sub(r'<Override PartName="/([^"]+)"[^>]*/>',
                  lambda m: m.group(0) if m.group(1) in manter or m.group(1) not in pk.partes else "", ct)
    pk.gravar("[Content_Types].xml", ct_p)
    saida.mkdir(parents=True, exist_ok=True)
    pk.salvar(saida / ARQ_CURTO, manter=manter | {"[Content_Types].xml"})
    return dict(ordem=lista, midias=midias)


def converter_pdf(pptx: Path, destino: Path) -> bool:
    """PDF do deck pelo LibreOffice (perfil temporário). Devolve False se o LibreOffice não estiver disponível."""
    import shutil
    import subprocess
    import tempfile
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if not exe:
        print("aviso: LibreOffice ausente; PDF do deck curto não gerado", file=sys.stderr)
        return False
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ, SAL_USE_VCLPLUGIN="svp")
        r = subprocess.run([exe, f"-env:UserInstallation=file://{tmp}/perfil", "--headless", "--convert-to", "pdf",
                            "--outdir", tmp, str(pptx)], env=env, capture_output=True, timeout=600)
        gerado = Path(tmp) / (pptx.stem + ".pdf")
        if r.returncode != 0 or not gerado.exists():
            print("aviso: o LibreOffice não converteu o deck curto: " + r.stderr.decode("utf-8", "replace")[-300:],
                  file=sys.stderr)
            return False
        destino.write_bytes(gerado.read_bytes())
    return True


def escrever_manifesto_curto(deck: Path, saida: Path, resumo: dict, com_pdf: bool) -> None:
    man = {
        "natureza_dos_dados": "EMPIRICO",
        "script": "scripts/apresentacao/gerar_deck_banca2.py (modo padrão: deck curto)",
        "pedido": "autor, 26/10/2026: só a parte empírica, muito menor, sem o diagrama causal da teoria; estrutura "
                  "obrigatória da versão final (doc 06); no máximo cerca de 30 palavras por slide",
        "regra": "nada estimado; nada lido de data/; texto lido do doc 04; figuras de output/ como imagem; seções na "
                 f"ordem {' → '.join(SECOES_CURTO)}; no máximo {MAX_PALAVRAS} palavras visíveis por slide, fora o "
                 "título, a figura e a linha de fontes; sem slides do grupo, sem divisórias, sem diagrama, sem apêndice",
        "numeracao_das_hipoteses": "a partir de 26/10/2026: H1 preenchimento; H2 bolsa × origem (antes H3); H3 "
                                   "oferta (antes H4)",
        "conteudo_canonico": "docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md",
        "entradas": [
            {"caminho": "deck do grupo (fora do repositório; não é alterado)", "nome": deck.name,
             "sha256": sha256_arq(deck), "papel": "só template: mestre, layout e rodapé"},
            {"caminho": "docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md", "sha256": sha256_arq(DOC_CURTO),
             "papel": "texto dos slides e notas"},
            {"caminho": "output/apresentacao_banca2/numeros_banca2.json", "sha256": sha256_arq(NUMEROS),
             "papel": "registro dos números citados (conferido pelo teste)"},
        ] + [{"caminho": f, "sha256": sha256_arq(ROOT / f), "papel": "figura", "no_pacote": m}
             for f, m in sorted(resumo["midias"].items())],
        "saidas": [{"caminho": f"output/apresentacao_banca2/{n}", "sha256": sha256_arq(saida / n),
                    "bytes": (saida / n).stat().st_size}
                   for n in ((ARQ_CURTO, ARQ_CURTO_PDF) if com_pdf else (ARQ_CURTO,))],
        "nota_pdf": "o PDF é renderizado pelo LibreOffice e não é byte a byte determinístico; o .pptx é",
        "ordem": resumo["ordem"],
    }
    (saida / ARQ_MANIF_CURTO).write_text(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                         encoding="utf-8")


def sha256_arq(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def construir(deck: Path, saida: Path) -> dict:
    num = {c: e for b in ("numeros", "failure_mode", "texto_citado")
           for c, e in json.loads(NUMEROS.read_text(encoding="utf-8"))[b].items()}
    slides_doc = ler_slides()
    pk = Pacote(deck)
    pres = pk.texto("ppt/presentation.xml")
    rels = pk.texto("ppt/_rels/presentation.xml.rels")
    ct = pk.texto("[Content_Types].xml")
    entradas = re.findall(r'<p:sldId id="(\d+)" r:id="(rId\d+)"/>', re.search(r"<p:sldIdLst>(.*?)</p:sldIdLst>", pres,
                                                                              flags=re.S).group(1))
    rid_alvo = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship Id="(rId\d+)"[^>]*Target="([^"]*)"', rels)}
    orig = [(i, r, "ppt/" + rid_alvo[r]) for i, r in entradas]
    if len(orig) != 36:
        raise SystemExit(f"ERRO: o deck do grupo tinha 36 slides; este tem {len(orig)}")
    nome_slide = {k + 1: n for k, (_, _, n) in enumerate(orig)}
    for pos, esperado in TITULOS_ESPERADOS.items():
        achado = BF.titulo_do_slide(pk.texto(nome_slide[pos]))
        if achado.strip() != esperado:
            raise SystemExit(f"ERRO: slide {pos}: esperado {esperado!r}, achado {achado!r}")
    notas_de = {}
    for pos, n in nome_slide.items():
        m = re.search(r'Target="\.\./notesSlides/(notesSlide\d+\.xml)"', pk.texto(BF._rels_de(n)))
        if m:
            notas_de[pos] = "ppt/notesSlides/" + m.group(1)

    correcoes = corrigir(pk, nome_slide, notas_de, num)
    corrigir_grafico_slide10(pk, nome_slide)
    if 'Extension="png"' not in ct:
        ct = ct.replace("<Types ", '<Types ', 1).replace("</Types>", '<Default Extension="png" ContentType="image/png"/></Types>')

    n_slide = max(int(re.search(r"slide(\d+)\.xml", n).group(1)) for n in pk.partes if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
    n_notas = max(int(re.search(r"notesSlide(\d+)\.xml", n).group(1)) for n in pk.partes if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", n))
    prox_rid = max(int(r[3:]) for r in rid_alvo) + 1
    prox_id = max(int(i) for i, _ in entradas) + 1
    layout = "slideLayout14.xml"
    if 'name="1_Title Slide"' not in pk.texto("ppt/slideLayouts/" + layout):
        raise SystemExit("ERRO: layout 1_Title Slide não está em slideLayout14.xml")
    novos = []
    midias: dict[str, str] = {}
    for k, sl in enumerate(slides_doc):
        ns, nn, rid = n_slide + 1 + k, n_notas + 1 + k, f"rId{prox_rid + k}"
        rels_slide = [f'<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/{layout}"/>',
                      f'<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{nn}.xml"/>']
        rid_img = None
        if sl["imagem"] is not None:
            if not sl["imagem"].exists() or "/output/" not in sl["imagem"].as_posix():
                raise SystemExit(f"ERRO: figura fora de output/ ou ausente: {sl['imagem']}")
            rel_out = sl["imagem"].relative_to(ROOT).as_posix()
            if rel_out not in midias:
                midias[rel_out] = f"ppt/media/banca2_{len(midias) + 1:02d}_{sl['imagem'].stem}.png"
                pk.gravar(midias[rel_out], sl["imagem"].read_bytes())
            rid_img = "rId3"
            rels_slide.append(f'<Relationship Id="rId3" Type="{REL_IMG}" Target="../media/{Path(midias[rel_out]).name}"/>')
        pk.gravar(f"ppt/slides/slide{ns}.xml", montar(sl, rid_img))
        pk.gravar(f"ppt/slides/_rels/slide{ns}.xml.rels",
                  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  + "".join(rels_slide) + "</Relationships>")
        pk.gravar(f"ppt/notesSlides/notesSlide{nn}.xml", xml_notas(notas_do_slide(sl)))
        pk.gravar(f"ppt/notesSlides/_rels/notesSlide{nn}.xml.rels",
                  '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/>'
                  f'<Relationship Id="rId2" Type="{REL_SLIDE}" Target="../slides/slide{ns}.xml"/>'
                  '</Relationships>')
        rels = rels.replace("</Relationships>", f'<Relationship Id="{rid}" Type="{REL_SLIDE}" Target="slides/slide{ns}.xml"/></Relationships>')
        ct = ct.replace("</Types>",
                        f'<Override PartName="/ppt/slides/slide{ns}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
                        f'<Override PartName="/ppt/notesSlides/notesSlide{nn}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/></Types>')
        novos.append(dict(sl=sl, id=str(prox_id + k), rid=rid, parte=f"ppt/slides/slide{ns}.xml"))

    # ordem do deck proposto: a do doc 02, conferida contra a tabela de classificação
    classif = ler_classificacao()
    if sorted(classif) != list(range(1, N_GRUPO + 1)):
        raise SystemExit("ERRO: a classificação do doc 02 não cobre os 36 slides do deck do grupo, um por linha")
    ordem_doc = ler_ordem()
    if [k for t, k, *_ in ordem_doc if t == "novo"] != list(range(len(novos))):
        raise SystemExit("ERRO: a ordem do doc 02 não bate com os slides novos")
    usados = [n for t, n, *_ in ordem_doc if t == "grupo"]
    if len(usados) != len(set(usados)):
        raise SystemExit("ERRO: slide do grupo repetido na ordem do doc 02")
    for n, c in classif.items():
        if (n in usados) != (c["destino"] != "removido"):
            raise SystemExit(f"ERRO: slide {n} do grupo: destino {c['destino']!r} diverge dos marcadores do doc 02")
    ordem: list[tuple[str, str, str]] = []  # (id, rid, rótulo)
    pos_novo: dict[int, int] = {}
    for k, item in enumerate(ordem_doc, 1):
        if item[0] == "novo":
            nv = novos[item[1]]
            ordem.append((nv["id"], nv["rid"], "novo"))
        else:
            n = item[1]
            pos_novo[n] = k
            ordem.append((orig[n - 1][0], orig[n - 1][1], f"slide {n} do deck do grupo"))
            esperada = classif[n]["posicao"]
            if esperada != k:
                raise SystemExit(f"ERRO: slide {n} do grupo vai para a posição {k}; o doc 02 diz {esperada}")
    for item in ordem_doc:
        if item[0] == "grupo":
            n, titulo_novo = item[1], item[2]
            x = pk.texto(nome_slide[n])
            feito = []  # a visibilidade é a do deck do grupo (oculto continua oculto)
            if titulo_novo:
                x = retitular(x, titulo_novo)
                feito.append(f"título: {titulo_novo}")
            x, n_num = numerar(x, pos_novo[n])
            if n_num:
                feito.append(f"número de página digitado → campo do número do slide ({pos_novo[n]})")
            for antigo, alvo_grupo in REFERENCIAS_A_SLIDE.get(n, []):
                x, nr = trocar_texto_runs(x, antigo, f"slide {pos_novo[alvo_grupo]}")
                if nr != 1:
                    raise SystemExit(f"ERRO: referência {antigo!r} achada {nr} vezes no slide {n} do grupo")
                feito.append(f"'{antigo}' → 'slide {pos_novo[alvo_grupo]}'")
            pk.gravar(nome_slide[n], x)
            if feito:
                correcoes.append({"slide": n, "correcao": "; ".join(feito)})
    if len([o for o in ordem if o[2] == "novo"]) != len(novos):
        raise SystemExit("ERRO: algum slide novo ficou fora da ordem")

    def com_lista(itens: list[tuple[str, str]], pres_txt: str) -> str:
        nova = "<p:sldIdLst>" + "".join(f'<p:sldId id="{i}" r:id="{r}"/>' for i, r in itens) + "</p:sldIdLst>"
        return re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", lambda _m: nova, pres_txt, count=1, flags=re.S)

    def podar(pres_txt: str, rels_txt: str, manter_rids: set[str], destino: Path) -> None:
        rels_p = re.sub(r'<Relationship Id="(rId\d+)" Type="[^"]*/relationships/slide" Target="slides/[^"]*"/>',
                        lambda m: m.group(0) if m.group(1) in manter_rids else "", rels_txt)
        pk.gravar("ppt/presentation.xml", pres_txt)
        pk.gravar("ppt/_rels/presentation.xml.rels", rels_p)
        pk.gravar("[Content_Types].xml", ct)
        manter = BF.alcancaveis(pk)
        ct_p = re.sub(r'<Override PartName="/([^"]+)"[^>]*/>',
                      lambda m: m.group(0) if m.group(1) in manter or m.group(1) not in pk.partes else "", ct)
        pk.gravar("[Content_Types].xml", ct_p)
        pk.salvar(destino, manter=manter | {"[Content_Types].xml"})

    saida.mkdir(parents=True, exist_ok=True)
    # (a) deck proposto: na ordem do doc 02, só com os slides do grupo que ficam
    podar(com_lista([(i, r) for i, r, _ in ordem], pres), rels, {r for _, r, _ in ordem}, saida / ARQ_DECK)

    titulos = {}
    for nv in novos:
        titulos[nv["id"]] = nv["sl"]["titulo"]
    lista = []
    for k, (i, r, rot) in enumerate(ordem, 1):
        if rot == "novo":
            nv = next(n for n in novos if n["id"] == i)
            lista.append(dict(posicao=k, origem="novo", titulo=nv["sl"]["titulo"], secao=nv["sl"]["secao"],
                              layout=nv["sl"]["layout"],
                              figura=nv["sl"]["imagem"].relative_to(ROOT).as_posix() if nv["sl"]["imagem"] else None))
        else:
            pos = int(rot.split()[1])
            lista.append(dict(posicao=k, origem=rot, destino=classif[pos]["destino"],
                              titulo=BF.titulo_do_slide(pk.texto(nome_slide[pos])).strip() or "(sem título)"))
    classificacao = [dict(slide_do_grupo=n, **classif[n]) for n in sorted(classif)]
    return dict(ordem=lista, correcoes=correcoes, midias=midias, classificacao=classificacao)


def escrever_manifesto(deck: Path, saida: Path, resumo: dict) -> None:
    man = {
        "natureza_dos_dados": "EMPIRICO",
        "script": "scripts/apresentacao/gerar_deck_banca2.py",
        "regra": "nada estimado; nada lido de data/; texto dos slides novos lido do doc 02; números das correções lidos "
                 "de output/apresentacao_banca2/numeros_banca2.json; figuras de output/ como imagem",
        "conteudo_canonico": "docs/07_apresentacoes/banca2/02_conteudo_slides.md",
        "entradas": [
            {"caminho": "deck do grupo (fora do repositório; não é alterado)", "nome": deck.name, "sha256": sha256_arq(deck),
             "bytes": deck.stat().st_size, "papel": "template e deck de partida (36 slides)", "data_referencia": "2026-10-26"},
            {"caminho": "docs/07_apresentacoes/banca2/02_conteudo_slides.md", "sha256": sha256_arq(DOC02),
             "papel": "texto dos slides novos e quadro de correções"},
            {"caminho": "output/apresentacao_banca2/numeros_banca2.json", "sha256": sha256_arq(NUMEROS),
             "papel": "números das correções"},
        ] + [{"caminho": f, "sha256": sha256_arq(ROOT / f), "papel": "figura", "no_pacote": m}
             for f, m in sorted(resumo["midias"].items())],
        "saidas": [{"caminho": f"output/apresentacao_banca2/{n}", "sha256": sha256_arq(saida / n),
                    "bytes": (saida / n).stat().st_size} for n in (ARQ_DECK,)],
        "correcoes": resumo["correcoes"],
        "classificacao_deck_do_grupo": resumo["classificacao"],
        "ordem_do_deck_proposto": resumo["ordem"],
    }
    (saida / ARQ_MANIFESTO).write_text(json.dumps(man, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                       encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck", type=Path, default=os.environ.get("PMME_DECK_GRUPO"),
                    help="deck do grupo (.pptx); só leitura. Padrão: variável de ambiente PMME_DECK_GRUPO")
    ap.add_argument("--curto", action="store_true",
                    help="gera o deck curto (doc 04); é o padrão desde 26/10/2026 e fica só por compatibilidade")
    ap.add_argument("--completo", action="store_true",
                    help="regera o deck completo (doc 02), que desde 26/10/2026 é só registro e não é mais usado")
    ap.add_argument("--sem-pdf", action="store_true", help="não converte o deck curto em PDF")
    a = ap.parse_args(argv)
    if not a.deck:
        ap.error("informe --deck ou a variável de ambiente PMME_DECK_GRUPO")
    if a.curto and a.completo:
        ap.error("--curto e --completo são excludentes")
    deck = Path(a.deck)
    if not a.completo:
        resumo = construir_curto(deck, SAIDA)
        com_pdf = not a.sem_pdf and converter_pdf(SAIDA / ARQ_CURTO, SAIDA / ARQ_CURTO_PDF)
        escrever_manifesto_curto(deck, SAIDA, resumo, com_pdf)
        for n in (ARQ_CURTO, ARQ_CURTO_PDF, ARQ_MANIF_CURTO):
            if (SAIDA / n).exists():
                print(SAIDA.relative_to(ROOT) / n, (SAIDA / n).stat().st_size)
        return 0
    resumo = construir(deck, SAIDA)
    escrever_manifesto(deck, SAIDA, resumo)
    for n in (ARQ_DECK, ARQ_MANIFESTO):
        print(SAIDA.relative_to(ROOT) / n, (SAIDA / n).stat().st_size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
