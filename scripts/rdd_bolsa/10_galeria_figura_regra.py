"""Galeria de formas para a figura "bolsa anunciada contra o IVS" (ciclo 1).

Gera variantes sem deslocamento aleatório. Cada variante aparece duas vezes:
com o IVS 2010 oficial (a variável que define a bolsa) e com o arquivo local
`data/ivs_ipea_2010_municipios.csv`, que traz linhas de subgrupo. Na versão do
arquivo local, os municípios cuja faixa a regra erraria aparecem em destaque.
Serve para o autor escolher a forma da figura. Não abre outcome.

Em 18/10/2026 o autor escolheu a variante A. A galeria passou a trazer também a
"A colorida" (cor do ponto = IVS do eixo, verde -> amarelo -> vermelho; contorno
preto nos municípios do lado errado do corte), desenhada pela mesma função que
o relatório usa (`fig_regra_pontos` de `09_gerar_relatorio_pdf.py`). As
variantes anteriores ficam como registro da escolha.

Saídas: `output/rdd_bolsa/galeria_figura_regra.html` e `.pdf`.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("rel09", ROOT / "scripts" / "rdd_bolsa" / "09_gerar_relatorio_pdf.py")
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)

MATRIZ = ROOT / "output" / "rdd_bolsa" / "matriz_municipio_escore_administrativo.csv"
OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
LOCAL = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
OUT_HTML = ROOT / "output" / "rdd_bolsa" / "galeria_figura_regra.html"
OUT_PDF = ROOT / "output" / "rdd_bolsa" / "galeria_figura_regra.pdf"

CORTES = (0.300, 0.400)
FAIXAS = ["FAIXA 3", "FAIXA 2", "FAIXA 1"]  # ordem crescente de bolsa
VALOR = {"FAIXA 3": 10_000, "FAIXA 2": 15_000, "FAIXA 1": 20_000}
X0, X1 = 0.10, 0.75
W = 680
COR, Linear, br, br_mil, f2 = R.COR, R.Linear, R.br, R.br_mil, R.f2
t_svg, l_svg, esc = R.t_svg, R.l_svg, R.esc


def faixa_regra(s: float) -> str:
    return "FAIXA 3" if s <= CORTES[0] + 1e-9 else ("FAIXA 2" if s <= CORTES[1] + 1e-9 else "FAIXA 1")


def dados() -> pd.DataFrame:
    m = pd.read_csv(MATRIZ, dtype={"co_ibge": str})
    d = m[m["quadro"] == "c1_ch1"].drop_duplicates("co_ibge")[["co_ibge", "faixa_anunciada"]]
    of = pd.read_csv(OFICIAL, dtype={"co_ibge": str})[["co_ibge", "nome_municipio_uf", "ivs"]]
    lo = pd.read_csv(LOCAL, dtype={"cod_ibge6": str})[["cod_ibge6", "ivs_2010"]].rename(
        columns={"cod_ibge6": "co_ibge", "ivs_2010": "ivs_local"})
    d = d.merge(of, on="co_ibge").merge(lo, on="co_ibge")
    d["nivel"] = d["faixa_anunciada"].map({f: i for i, f in enumerate(FAIXAS)})
    return d.reset_index(drop=True)


def moldura(H: int, mt: int, mb: int, ml: int, mr: int, eixo_x: str, Y, rotulo_nivel: bool = True) -> list[str]:
    X = Linear(X0, X1, ml, W - mr)
    o = []
    for tx in R.nice_ticks(X0, X1, 7):
        o.append(l_svg(X(tx), H - mb, X(tx), H - mb + 4, COR["axis"]))
        o.append(t_svg(X(tx), H - mb + 16, br(tx, 2), anchor="middle"))
    o.append(l_svg(ml, H - mb, W - mr, H - mb, COR["axis"]))
    o.append(t_svg((ml + W - mr) / 2, H - 6, eixo_x, anchor="middle"))
    for c in CORTES:
        o.append(l_svg(X(c), mt - 4, X(c), H - mb, COR["ink2"], w=1.2, extra='stroke-dasharray="4 3"'))
        o.append(t_svg(X(c), mt - 9, br(c, 3), anchor="middle", cor=COR["ink"], peso=600))
    if rotulo_nivel:
        for i, f in enumerate(FAIXAS):
            o.append(t_svg(ml - 8, Y(i) + 3.5, br_mil(VALOR[f]), anchor="end", cor=COR["ink"]))
    return o


def cor_ponto(errado: bool) -> str:
    return COR["s2"] if errado else COR["s1"]


def var_pontos(s, nivel, errado, eixo_x) -> str:
    """V1: pontos exatamente no valor da bolsa, sem deslocamento; a sobreposição aparece pela opacidade."""
    H, mt, mb, ml, mr = 210, 26, 44, 74, 24
    Y = Linear(-0.6, 2.6, H - mb, mt)
    X = Linear(X0, X1, ml, W - mr)
    o = [R.svg_abrir(W, H, "variante pontos sobre o degrau")]
    o += moldura(H, mt, mb, ml, mr, eixo_x, Y)
    pts = [(X0, 0), (CORTES[0], 0), (CORTES[0], 1), (CORTES[1], 1), (CORTES[1], 2), (X1, 2)]
    o.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{f2(X(a))},{f2(Y(b))}" for i, (a, b) in enumerate(pts))
             + f'" fill="none" stroke="{COR["axis"]}" stroke-width="1.5"/>')
    for k in np.argsort(errado, kind="stable"):
        o.append(f'<circle cx="{f2(X(s[k]))}" cy="{f2(Y(nivel[k]))}" r="3.4" fill="{cor_ponto(errado[k])}" '
                 f'fill-opacity="0.35"/>')
    o.append("</svg>")
    return "".join(o)


def _empilhar(s, nivel, largura):
    """Posição de empilhamento de cada ponto dentro de (nível, bin)."""
    bins = np.floor((np.asarray(s) - X0) / largura + 1e-9).astype(int)
    ordem = np.lexsort((np.asarray(s), bins, nivel))
    pos = np.zeros(len(s), int)
    vistos: dict = {}
    for k in ordem:
        chave = (int(nivel[k]), int(bins[k]))
        pos[k] = vistos.get(chave, 0)
        vistos[chave] = pos[k] + 1
    return bins, pos, max(vistos.values())


def var_empilhado(s, nivel, errado, eixo_x) -> str:
    """V2: dot plot. Cada município é um ponto; pontos do mesmo bin de 0,005 se empilham sobre a linha da faixa."""
    largura = 0.005
    bins, pos, pmax = _empilhar(s, nivel, largura)
    passo_px = 5.2
    faixa_px = max(60, pmax * passo_px + 14)
    mt, mb, ml, mr = 26, 44, 74, 24
    H = int(mt + mb + 3 * faixa_px)
    base = {i: H - mb - i * faixa_px - 6 for i in range(3)}
    X = Linear(X0, X1, ml, W - mr)
    o = [R.svg_abrir(W, H, "variante pontos empilhados")]
    o += moldura(H, mt, mb, ml, mr, eixo_x, lambda i: base[i] - 2)
    for i in range(3):
        o.append(l_svg(ml, base[i] + 3, W - mr, base[i] + 3, COR["grid"]))
    for k in range(len(s)):
        cx = X(X0 + (bins[k] + 0.5) * largura)
        cy = base[int(nivel[k])] - pos[k] * passo_px
        o.append(f'<circle cx="{f2(cx)}" cy="{f2(cy)}" r="2.3" fill="{cor_ponto(errado[k])}"/>')
    o.append("</svg>")
    return "".join(o)


def var_histograma(s, nivel, errado, eixo_x) -> str:
    """V3: um histograma por faixa (bins de 0,01), empilhando os municípios na posição errada em destaque."""
    largura = 0.01
    nb = int(round((X1 - X0) / largura))
    cont = np.zeros((3, nb, 2), int)
    b = np.clip(np.floor((np.asarray(s) - X0) / largura + 1e-9).astype(int), 0, nb - 1)
    for k in range(len(s)):
        cont[int(nivel[k]), b[k], int(errado[k])] += 1
    cmax = int(cont.sum(axis=2).max())
    faixa_px = 72
    mt, mb, ml, mr = 26, 44, 74, 24
    H = mt + mb + 3 * faixa_px
    base = {i: H - mb - i * faixa_px - 4 for i in range(3)}
    X = Linear(X0, X1, ml, W - mr)
    esc_h = (faixa_px - 14) / max(cmax, 1)
    o = [R.svg_abrir(W, H, "variante histogramas por faixa")]
    o += moldura(H, mt, mb, ml, mr, eixo_x, lambda i: base[i] - 8)
    for i in range(3):
        o.append(l_svg(ml, base[i], W - mr, base[i], COR["grid"]))
        for j in range(nb):
            y = base[i]
            for e in (0, 1):
                n = cont[i, j, e]
                if n:
                    h = n * esc_h
                    o.append(f'<rect x="{f2(X(X0 + j * largura) + 0.6)}" y="{f2(y - h)}" '
                             f'width="{f2(X(X0 + largura) - X(X0) - 1.2)}" height="{f2(h)}" fill="{cor_ponto(e)}"/>')
                    y -= h
    o.append(t_svg(W - mr, mt + 4, f"altura máx. = {cmax} municípios", anchor="end", size=9.5, cor=COR["muted"]))
    o.append("</svg>")
    return "".join(o)


def var_barras(s, nivel, errado, eixo_x) -> str:
    """V4: código de barras. Uma fileira por faixa; cada município é um traço vertical na posição do IVS."""
    faixa_px = 34
    mt, mb, ml, mr = 26, 44, 74, 24
    H = mt + mb + 3 * faixa_px + 10
    centro = {i: H - mb - 10 - i * faixa_px - faixa_px / 2 for i in range(3)}
    X = Linear(X0, X1, ml, W - mr)
    o = [R.svg_abrir(W, H, "variante código de barras")]
    o += moldura(H, mt, mb, ml, mr, eixo_x, lambda i: centro[i])
    for k in np.argsort(errado, kind="stable"):
        cy = centro[int(nivel[k])]
        o.append(l_svg(X(s[k]), cy - 11, X(s[k]), cy + 11, cor_ponto(errado[k]), w=1.3,
                       extra='stroke-opacity="0.55"'))
    o.append("</svg>")
    return "".join(o)


def var_pontos_cor(s, nivel, errado, eixo_x) -> str:
    """A colorida (escolhida pelo autor): a mesma funcao da figura do relatorio, cor = IVS do eixo."""
    errado = np.asarray(errado, bool)
    return R.fig_regra_pontos(
        s, [FAIXAS[int(i)] for i in nivel], errado, eixo_x, list(CORTES), FAIXAS, VALOR, X0, X1,
        destacar=bool(errado.any()),
        rotulo_errado=f"contorno preto: faixa do lado errado do corte ({int(errado.sum())} municípios)")


VARIANTES = [
    ("A", "Pontos sobre o degrau, sem deslocamento",
     "Cada município é um ponto no valor exato da bolsa. Onde há muitos municípios, a cor fica mais forte.",
     var_pontos),
    ("A colorida", "Pontos sobre o degrau, coloridos pelo IVS (escolhida em 18/10/2026)",
     "A variante A com a cor de cada ponto dada pelo IVS do eixo horizontal, numa escala contínua verde → amarelo "
     "→ vermelho (vermelho = IVS maior). Os municípios do lado errado do corte ganham contorno preto, porque o "
     "laranja colidiria com a escala. É a forma usada no relatório.",
     var_pontos_cor),
    ("B", "Pontos empilhados (dot plot)",
     "Cada município é um ponto. Municípios com IVS no mesmo intervalo de 0,005 se empilham para cima, então "
     "a altura mostra quantos há ali, sem nenhuma aleatoriedade.",
     var_empilhado),
    ("C", "Histograma por faixa",
     "Para cada valor de bolsa, a distribuição do IVS dos municípios que o recebem (barras de 0,01).",
     var_histograma),
    ("D", "Código de barras por faixa",
     "Uma fileira por valor de bolsa; cada município é um traço vertical na posição do seu IVS.",
     var_barras),
]


def montar() -> str:
    d = dados()
    s_of = d["ivs"].to_numpy(float)
    s_lo = d["ivs_local"].to_numpy(float)
    nivel = d["nivel"].to_numpy(int)
    err_of = np.array([faixa_regra(v) != f for v, f in zip(s_of, d["faixa_anunciada"])])
    err_lo = np.array([faixa_regra(v) != f for v, f in zip(s_lo, d["faixa_anunciada"])])
    n = len(d)
    leg = (f'<p class="leg"><span class="sw" style="background:{COR["s1"]}"></span> faixa coerente com a regra '
           f'(cortes 0,300 e 0,400) &nbsp; <span class="sw" style="background:{COR["s2"]}"></span> '
           "faixa que a regra não explica: o ponto está do lado errado do corte</p>")
    blocos = []
    for cod, tit, desc, fn in VARIANTES:
        blocos.append(
            f'<section class="var"><h2>Variante {cod} — {esc(tit)}</h2><p class="desc">{esc(desc)}</p>'
            f"<h3>Com o IVS 2010 oficial (o que define a bolsa) — {int(err_of.sum())} de {n} fora da regra</h3>"
            + fn(s_of, nivel, err_of, "IVS 2010 oficial do município (Ipea)")
            + f"<h3>Com o arquivo antigo do repositório (linha de subgrupo) — {int(err_lo.sum())} de {n} "
              "fora da regra</h3>"
            + fn(s_lo, nivel, err_lo, "IVS do arquivo antigo (data/ivs_ipea_2010_municipios.csv)")
            + "</section>")
    css = """
    @page { size: A4; margin: 14mm 13mm; }
    body { font-family: %s; color: #0b0b0b; background: #fff; margin: 0; }
    h1 { font-size: 20px; margin: 0 0 6px; } h2 { font-size: 15px; margin: 0 0 4px; }
    h3 { font-size: 12px; font-weight: 600; color: #52514e; margin: 10px 0 2px; }
    p { font-size: 11.5px; line-height: 1.45; margin: 4px 0; } .desc { color: #52514e; }
    .var { break-inside: avoid; page-break-inside: avoid; margin: 16px 0 10px; }
    .var + .var { break-before: page; }
    svg { width: 100%%; height: auto; display: block; }
    .leg { font-size: 11px; color: #52514e; }
    .sw { display: inline-block; width: 10px; height: 10px; border-radius: 5px; vertical-align: -1px; }
    .fonte { font-size: 9.5px; color: #898781; margin-top: 10px; }
    """ % R.FONTE_SANS
    commit, _ = R.git_info()
    return (
        '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><title>Galeria — figura da regra</title>'
        f"<style>{css}</style></head><body>"
        "<h1>Bolsa anunciada contra o IVS: formas possíveis</h1>"
        f"<p>Ciclo 1, chamada 1: {n} municípios do quadro de vagas. Nenhuma variante usa deslocamento aleatório. "
        "Em cada uma, o painel de cima usa o IVS 2010 oficial e o de baixo usa o arquivo antigo do repositório, "
        "com os mesmos municípios e a mesma bolsa anunciada: muda só a posição no eixo do IVS. Escolha do autor "
        "(18/10/2026): variante A, na versão colorida que vem logo depois dela.</p>"
        + leg + "".join(blocos)
        + f'<p class="fonte">Fontes: {esc(R.rel(MATRIZ))}; {esc(R.rel(OFICIAL))}; {esc(R.rel(LOCAL))}. '
          f"Gerado por scripts/rdd_bolsa/10_galeria_figura_regra.py, commit {commit}, "
          f"{dt.date.today().strftime('%d/%m/%Y')}.</p></body></html>"
    )


def main() -> int:
    OUT_HTML.write_text(montar(), encoding="utf-8")
    ok = R.gerar_pdf(OUT_HTML, OUT_PDF)
    print(f"HTML: {R.rel(OUT_HTML)}; PDF: {R.rel(OUT_PDF) if ok else 'falhou'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
