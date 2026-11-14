"""Roteiro de fala da banca final em Word, a partir do doc 05 (fonte de verdade em Markdown).

Entrada (só leitura): `docs/07_apresentacoes/banca_final/05_roteiro_fala.md`.
Saída: `output/apresentacao_banca_final/roteiro_fala_banca_final.docx`.

O Markdown do doc 05 usa só: título (#), seções (##), blocos de citação (>), linhas de slide em negrito
(**N. Título** (tempo)), listas (- …, com continuação recuada) e parágrafos. Negrito (**…**), código (`…`) e links
([texto](alvo)) viram texto simples com o negrito mantido. Nada é estimado aqui.

Uso:
    python scripts/apresentacao/gerar_roteiro_docx.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/07_apresentacoes/banca_final/05_roteiro_fala.md"
SAIDA = ROOT / "output/apresentacao_banca_final/roteiro_fala_banca_final.docx"
VERDE, CINZA, TEXTO = RGBColor(0x11, 0x47, 0x19), RGBColor(0x5E, 0x66, 0x60), RGBColor(0x1A, 0x1A, 0x1A)
FONTE = "Calibri"


def limpar(t: str) -> str:
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)  # links: só o texto
    t = t.replace("`", "").replace("<br>", "")
    return t


def runs(p, t: str, tam: float, cor=TEXTO, negrito_base: bool = False) -> None:
    """Escreve `t` no parágrafo, com **negrito**."""
    for k, parte in enumerate(limpar(t).split("**")):
        if not parte:
            continue
        r = p.add_run(parte)
        r.font.size = Pt(tam)
        r.font.name = FONTE
        r.font.bold = negrito_base or k % 2 == 1
        r.font.color.rgb = cor


def espaco(p, antes: float, depois: float) -> None:
    p.paragraph_format.space_before = Pt(antes)
    p.paragraph_format.space_after = Pt(depois)


def blocos(md: str) -> list[tuple[str, str]]:
    """Junta linhas de continuação: devolve (tipo, texto)."""
    out: list[tuple[str, str]] = []
    for linha in md.splitlines():
        if not linha.strip():
            out.append(("vazio", ""))
            continue
        if linha.startswith("# "):
            out.append(("titulo", linha[2:].strip()))
        elif linha.startswith("## "):
            out.append(("secao", linha[3:].strip()))
        elif linha.startswith(">"):
            t = linha.lstrip(">").strip()
            if out and out[-1][0] == "cit" and not out[-1][1].endswith("<br>"):
                out[-1] = ("cit", out[-1][1] + " " + t)
            else:
                out.append(("cit", t))
        elif linha.startswith("- "):
            out.append(("item", linha[2:].strip()))
        elif linha.startswith("  ") and out and out[-1][0] == "item":
            out[-1] = ("item", out[-1][1] + " " + linha.strip())
        elif out and out[-1][0] == "par":
            out[-1] = ("par", out[-1][1] + " " + linha.strip())
        else:
            out.append(("par", linha.strip()))
    return [b for b in out if b[0] != "vazio"]


def main() -> int:
    d = Document()
    sec = d.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    for m in ("left_margin", "right_margin"):
        setattr(sec, m, Cm(2.2))
    sec.top_margin = sec.bottom_margin = Cm(2)
    estilo = d.styles["Normal"]
    estilo.font.name = FONTE
    estilo.element.rPr.rFonts.set(qn("w:eastAsia"), FONTE)
    estilo.font.size = Pt(11)

    for tipo, t in blocos(DOC.read_text(encoding="utf-8")):
        if tipo == "titulo":
            p = d.add_paragraph()
            runs(p, re.sub(r"^\d+\.\s*", "", t), 20, VERDE, True)
            espaco(p, 0, 10)
        elif tipo == "cit":
            p = d.add_paragraph()
            runs(p, t.replace("<br>", ""), 9.5, CINZA)
            espaco(p, 0, 4)
        elif tipo == "secao":
            p = d.add_paragraph()
            runs(p, t, 14, VERDE, True)
            espaco(p, 14, 4)
            p.paragraph_format.keep_with_next = True
            pb = p._p.get_or_add_pPr()
            borda = pb.makeelement(qn("w:pBdr"), {})
            baixo = borda.makeelement(qn("w:bottom"), {qn("w:val"): "single", qn("w:sz"): "6", qn("w:space"): "1",
                                                       qn("w:color"): "B9E4B1"})
            borda.append(baixo)
            pb.append(borda)
        elif tipo == "par" and t.startswith("**"):
            # linha de slide: **N. Título** (tempo) …
            m = re.match(r"\*\*(.+?)\*\*(.*)", t)
            p = d.add_paragraph()
            runs(p, m.group(1), 11.5, TEXTO, True)
            runs(p, m.group(2), 10.5, CINZA)
            espaco(p, 8, 2)
            p.paragraph_format.keep_with_next = True
        elif tipo == "item":
            p = d.add_paragraph(style="List Bullet")
            runs(p, t, 11)
            espaco(p, 0, 2)
        else:
            p = d.add_paragraph()
            runs(p, t, 11)
            espaco(p, 4, 4)
    rod = sec.footer.paragraphs[0]
    rod.alignment = WD_ALIGN_PARAGRAPH.CENTER
    runs(rod, "Roteiro de fala, banca final do PMM-E (Grupo 2). Gerado do doc 05.", 8, CINZA)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(SAIDA))
    print(SAIDA.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
