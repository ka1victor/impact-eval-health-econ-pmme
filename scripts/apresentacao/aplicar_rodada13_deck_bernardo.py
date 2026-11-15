"""Aplica a rodada 13 de comentários do autor (15/11/2026) sobre o deck do Bernardo, mantendo a formatação e a
estrutura dele.

Entrada (só leitura): `docs/07_apresentacoes/banca_final/grupo/deck_grupo_banca_final_1511_bernardo.pptx`, o
`Banca Final.pptx` que o Bernardo mandou ao grupo em 15/11 (40 slides: a versão conciliada de 14/11 com slides de foco,
em que um retângulo branco semitransparente apaga parte do slide, anexos reordenados e um anexo 7 novo).

O que muda (só conteúdo dos slides que a rodada 13 pediu; o resto do deck fica byte a byte igual):
- 20, descritiva: a explicação "quem / distância / onde" fica sem título, embaixo dos gráficos; os títulos dos
  gráficos são os do Bernardo;
- 22, vagas A, B e C; 23 e 24, modelo; 25, passo a passo; 28, resultado; 29, robustez; 30, limitações: o miolo do
  slide é redesenhado com as funções do gerador do nosso deck (`gerar_deck_banca_final_grupo.py`), que já têm as
  mudanças da rodada 13. Ficam o título, o rodapé de seções, o número da página e os retângulos de foco do Bernardo
  (postos de novo por cima).

Números: os mesmos do gerador (lidos de `output/`). Saídas em `output/apresentacao_banca_final/`:
`deck_banca_final_bernardo_r13.pptx` (e `.pdf`) e `manifesto_deck_banca_final_bernardo_r13.json`.

Uso:
    python scripts/apresentacao/aplicar_rodada13_deck_bernardo.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches

ROOT = Path(__file__).resolve().parents[2]
ENT = ROOT / "docs/07_apresentacoes/banca_final/grupo/deck_grupo_banca_final_1511_bernardo.pptx"
SHA_ENT = "9bb32765eabeda33692f406ca0fb444af58310d074fc2a5bfaf7eb777f8fb4cb"
OUT = ROOT / "output/apresentacao_banca_final"
ARQ = "deck_banca_final_bernardo_r13"


def carregar_gerador():
    caminho = ROOT / "scripts/apresentacao/gerar_deck_banca_final_grupo.py"
    spec = importlib.util.spec_from_file_location("gerar_deck_banca_final_grupo", caminho)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


G = carregar_gerador()

# slide do Bernardo (base 1) → (início do título esperado, função do gerador que redesenha o miolo)
REDESENHO = {
    22: ("Cada médico escolhe a vaga", G.s_intuicao),
    23: ("Modelo: logit condicional", G.s_modelo),
    24: ("Modelo: logit condicional", G.s_modelo),
    25: ("Método passo a passo", G.s_passos),
    28: ("Ficar perto de onde trabalha", G.s_resultados_colega),
    29: ("Robustez:", G.s_robustez),
    30: ("Limitações", G.s_limitacoes),
}
DESCRITIVA = 20


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def titulo(slide) -> str:
    for sh in slide.shapes:
        if sh.is_placeholder and "TITLE" in str(sh.placeholder_format.type):
            return " ".join(sh.text_frame.text.split())
    return ""


def eh_foco(sh) -> bool:
    """Retângulo de foco do Bernardo: forma sem texto com preenchimento semitransparente."""
    xml = etree.tostring(sh._element).decode()
    return '<a:alpha val="' in xml and not (sh.has_text_frame and sh.text_frame.text.strip())


def fica(sh) -> bool:
    if sh.is_placeholder:
        return True
    if sh.has_text_frame and sh.text_frame.text.strip().startswith("Motivação") and "|" in sh.text_frame.text:
        return True  # rodapé de seções
    if sh.has_text_frame and sh.text_frame.text.strip().isdigit() and sh.top > Inches(6.8):
        return True  # número da página
    return eh_foco(sh)


class Reuso:
    """Faz o papel do `Modelo` do gerador: em vez de criar um slide, devolve o do Bernardo sem o miolo."""

    def __init__(self, slide):
        self.slide = slide

    def novo(self, prs, titulo_novo):
        for sh in list(self.slide.shapes):
            if not fica(sh):
                sh._element.getparent().remove(sh._element)
        return self.slide


def focos_por_cima(slide) -> int:
    arvore = slide.shapes._spTree
    focos = [sh._element for sh in slide.shapes if eh_foco(sh)]
    for el in focos:
        arvore.remove(el)
        arvore.append(el)
    return len(focos)


def refazer_descritiva(slide, n) -> None:
    sh = {x.name: x for x in slide.shapes}
    esperadas = {"Text 18", "Text 19", "Chart 0", "Text 20", "Text 21", "Image 0", "Text 22", "Como montamos"}
    if not esperadas <= set(sh):
        raise SystemExit(f"ERRO: descritiva sem as formas esperadas: {sorted(esperadas - set(sh))}")
    # tira a caixa antiga (com o título "COMO MONTAMOS"), que fica no alto do slide
    topo = Inches(0.85)
    for x in list(slide.shapes):
        if (not x.is_placeholder and x.top is not None and topo <= x.top < Inches(2.45) and
                x.name not in ("Text 18", "Text 19", "Text 20", "Text 21")):
            x._element.getparent().remove(x._element)
    sobe = Inches(1.6)
    for nome in ("Text 18", "Text 19", "Chart 0", "Text 20", "Text 21", "Image 0", "Text 22"):
        sh[nome].top = sh[nome].top - sobe
    e = n["esc"]
    G.caixa(slide, 0.25, 5.3, 12.83, 1.15, [], fill=G.CLARO, line=G.BORDA, nome="Como montamos")
    passos = (("Quem", f"{e['n']} candidatos com 1ª opção nos ciclos 1–3 e local de trabalho anterior conhecido"),
              ("Distância", "do município onde trabalhava (vínculo no CNES antes da inscrição) ao da vaga posta em 1º"),
              ("Onde", "se essa vaga fica na mesma UF, na mesma região de saúde ou no mesmo município"))
    for k, (rot, t) in enumerate(passos):
        x = 0.5 + k * 4.2
        G.caixa(slide, x, 5.5, 0.4, 0.4, [[(str(k + 1), 12, True, G.BRANCO)]], fill=G.VERDE, forma=MSO_SHAPE.OVAL,
                align=PP_ALIGN.CENTER, margem=0)
        G.texto(slide, x + 0.5, 5.44, 3.55, 1.0, [[(rot + ": ", 13, True, G.VERDE), (t, 12.5, False, G.TEXTO)]],
                anchor=MSO_ANCHOR.TOP)


def main() -> int:
    if sha256(ENT) != SHA_ENT:
        raise SystemExit("ERRO: o deck do Bernardo mudou (hash diferente)")
    prs = Presentation(str(ENT))
    if len(prs.slides) != 40:
        raise SystemExit("ERRO: esperava 40 slides no deck do Bernardo")
    n = G.numeros()
    feitas = []
    s = prs.slides[DESCRITIVA - 1]
    if not titulo(s).startswith("Candidatos escolhem perto"):
        raise SystemExit(f"ERRO: slide {DESCRITIVA} não é a descritiva: {titulo(s)!r}")
    refazer_descritiva(s, n)
    feitas.append(f"{DESCRITIVA}: descritiva com a explicação embaixo dos gráficos, sem título")
    for num, (inicio, funcao) in REDESENHO.items():
        s = prs.slides[num - 1]
        t = titulo(s)
        if not t.startswith(inicio):
            raise SystemExit(f"ERRO: slide {num} deveria começar com {inicio!r}; é {t!r}")
        funcao(Reuso(s), prs, n)
        k = focos_por_cima(s)
        feitas.append(f"{num}: {t} (miolo redesenhado; {k} retângulo(s) de foco mantido(s))")
    OUT.mkdir(parents=True, exist_ok=True)
    pptx = OUT / f"{ARQ}.pptx"
    prs.save(str(pptx))
    pdf = OUT / f"{ARQ}.pdf"
    ok_pdf = G.converter_pdf(pptx, pdf)
    man = {"etapa": ARQ, "natureza_dos_dados": "EMPIRICO",
           "script": str(Path(__file__).resolve().relative_to(ROOT)),
           "entradas": {str(p.relative_to(ROOT)): sha256(p) for p in (ENT, G.F_VL, G.F_VLR, G.F_VG, G.F_EX, G.F_NB2,
                                                                    G.FIG_SEIS, G.FIG_ROB)},
           "alteracoes": feitas, "slides": [{"posicao": i, "titulo": titulo(x)} for i, x in enumerate(prs.slides, 1)],
           "saidas": {str(pptx.relative_to(ROOT)): sha256(pptx),
                      **({str(pdf.relative_to(ROOT)): "gerado (PDF não é determinístico)"} if ok_pdf else {})}}
    (OUT / f"manifesto_{ARQ}.json").write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n".join(feitas))
    print(f"{len(prs.slides)} slides; PDF {'ok' if ok_pdf else 'FALHOU'}")
    return 0 if ok_pdf else 1


if __name__ == "__main__":
    sys.exit(main())
