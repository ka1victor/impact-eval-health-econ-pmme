"""Slides para os professores: nº de vagas preenchidas como variável de efeito (família N, protocolo 48).

Apresentação 16:9 simples, um gráfico por slide, título = conclusão, 2 a 4 bullets curtos e o "Como ler" numa linha
no rodapé. Ordem: abertura; regra IVS × bolsa; porte e oferta por corte (diagnóstico descritivo, fora do protocolo 48) e o
cuidado com o controle pela oferta (S-c); atração (E6); taxa de preenchimento (E6); N1 sem e com controle; forest N1–N4
por corte; robustez e placebo do ciclo 2; conclusão.

Todas as figuras RD têm um painel por corte (0,300 e 0,400): dentro de cada corte, os ciclos entram juntos, com
intercepto e inclinação por ciclo (como no protocolo). A linha de cortes empilhados é secundária e só aparece nos
forest plots.

Não estima nada novo e não lê `data/`: toda cifra vem de `output/rdd_bolsa/N_estimativas.csv`, `NA_estimativas.csv`,
`E6_estimativas.csv` e `N_resumo.json`. Os gráficos de médias por faixa redesenham, só para visualização, a mesma
especificação já estimada (local linear, kernel triangular, h do protocolo, ciclos juntos), com as funções do
`scripts/rdd_bolsa/23_estimar_contagem_vagas.py`, a partir de `output/rdd_bolsa/outcomes/`; para cada variável que já
tem estimativa nos CSV, o script aborta se a reta desenhada não reproduzir salto, IC e p do CSV (1e-6). Só o diagnóstico
de população 2022 não tem linha nos CSV: é descritivo e rotulado fora do protocolo 48. O HTML não leva data nem commit
(saída determinística).

Saídas:
- output/apresentacao_validacao/slides_contagem_vagas.html  (uma <section> por slide; setas navegam)
- output/apresentacao_validacao/slides_contagem_vagas.pdf   (16:9, Chromium headless)
- output/apresentacao_validacao/slides_contagem_vagas_figuras/*.png e *.svg
"""

from __future__ import annotations

import base64
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PASTA = ROOT / "output" / "apresentacao_validacao"
PASTA_FIG = PASTA / "slides_contagem_vagas_figuras"
ORIGEM = PASTA / "relatorio_validacao_rdd_bolsa.html"
SAIDA_HTML = PASTA / "slides_contagem_vagas.html"
SAIDA_PDF = PASTA / "slides_contagem_vagas.pdf"
N_EST = ROOT / "output" / "rdd_bolsa" / "N_estimativas.csv"
NA_EST = ROOT / "output" / "rdd_bolsa" / "NA_estimativas.csv"
E6_EST = ROOT / "output" / "rdd_bolsa" / "E6_estimativas.csv"
N_RES = ROOT / "output" / "rdd_bolsa" / "N_resumo.json"
SCRIPT_N = ROOT / "scripts" / "rdd_bolsa" / "23_estimar_contagem_vagas.py"

AZUL, LARANJA, CINZA, TINTA2 = "#2a78d6", "#e8693a", "#898781", "#52514e"
TOL = 1e-6


def _carregar(nome: str, caminho: Path):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        sys.modules[nome] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


FIG = _carregar("figuras_professores_base", ROOT / "scripts" / "apresentacao" / "gerar_figuras_validacao_professores.py")
_fmt, _num = FIG._fmt, FIG._num


def _p(x: float) -> str:
    return "< 0,001" if x < 0.001 else _num(x, 3)


def _ic(inf: float, sup: float, casas: int = 2) -> str:
    return f"[{_fmt(inf, casas)}; {_fmt(sup, casas)}]"


def _cs(x) -> str:
    return f"{float(x):.3f}".replace(".", ",")


def _pct(x: float) -> str:
    return _fmt(100 * x, 0) + " %"


def _pp(x: float) -> str:
    return _fmt(100 * x, 1) + " p.p."


def _exclui(r) -> bool:
    return not (r["ic95_inf"] <= 0 <= r["ic95_sup"])


def _ctxt(c: str) -> str:
    return "cortes empilhados" if c == "empilhado" else f"corte {_cs(float(c))}"


# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------

def _unica(df: pd.DataFrame, **cond) -> pd.Series:
    m = pd.Series(True, index=df.index)
    for k, v in cond.items():
        m &= df[k].astype(str) == str(v)
    d = df[m]
    if len(d) != 1:
        raise SystemExit(f"linha ausente ou duplicada: {cond}")
    return d.iloc[0]


ROTULOS = {"N1": "N1 · vagas preenchidas na 1ª chamada",
           "N2": "N2 · células com alocado na 1ª chamada",
           "N3": "N3 · células com alocado até a 2ª chamada",
           "N4": "N4 · especialistas ativos do ciclo"}
POP_MAX = {"N1": "V1+V2+V3", "N2": "V1+V2+V3", "N3": "V1+V2", "N4": "V1+V2"}


def _dados() -> dict:
    kw = dict(dtype={"corte": str, "ciclo": str})
    n, na, e6 = pd.read_csv(N_EST, **kw), pd.read_csv(NA_EST, **kw), pd.read_csv(E6_EST, **kw)
    res = json.loads(N_RES.read_text(encoding="utf-8"))
    princ = n[(n["variante"] == "principal") & (n["especificacao"] == "S-a")]
    h = float(princ["h"].iloc[0])
    cortes = sorted({c for c in princ["corte"].astype(str) if re.fullmatch(r"\d\.\d+", c)})
    ciclos = sorted({c for c in princ["populacao"].str.extract(r"^V(\d)$")[0].dropna()})
    # R$ de cada corte, lidos do texto do contraste do N_resumo ("0,300: R$ 10 mil -> 15 mil; ...")
    reais = {m[0].replace(",", "."): (m[1], m[2]) for m in re.findall(r"(\d,\d{3}): R\$ (\d+) mil -> (\d+) mil",
                                                                       res["contraste"])}
    return dict(n=n, na=na, e6=e6, res=res, h=h, cortes=cortes, ciclos=ciclos, reais=reais)


def _linha_n(d: dict, oid: str, esp: str, corte: str, **extra) -> pd.Series:
    return _unica(d["n"], outcome_id=oid, especificacao=esp, variante=extra.pop("variante", "principal"),
                  populacao=extra.pop("populacao", POP_MAX.get(oid, "V1+V2+V3")), corte=corte, **extra)


def _linha_e6(d: dict, outcome: str, corte: str) -> pd.Series:
    return _unica(d["e6"], outcome=outcome, especificacao="principal", populacao="V1+V2+V3", corte=corte)


# ---------------------------------------------------------------------------
# Refit para visualização (funções do script 23), conferido contra os CSV
# ---------------------------------------------------------------------------

def _modulo_n():
    return _carregar("estimar_contagem_vagas_n23", SCRIPT_N)


def _carregar_v(N23) -> dict:
    rv = N23.E6.ler_running_variable()
    pops, _ = N23.E6.chaves_populacoes(rv)
    V, _u, _info = N23.carregar(rv, pops)
    return V


def _png_hab_para_mil(V: dict) -> dict:
    return {k: d.assign(pop_mil=d["populacao_2022"].astype(float) / 1000.0) for k, d in V.items()}


def _refit(N23, V: dict, corte_mil: int, col: str, ctl: str | None = None) -> dict:
    ks = sorted(V)
    a = N23.montar_amostra([(V[k], corte_mil, f"c{k}") for k in ks], empilhada=True)
    y = a.col(col)
    r = N23.ajustar(a, y, N23.H, v=a.col(ctl) if ctl else None)
    cur, y_p, _ = N23.curva_empilhada(r, a)
    x = N23.L.normalizar_s_mil(a.s) - a.c
    dentro = np.isfinite(y_p)
    return dict(r=r, cur=cur, x=np.where(dentro, x, np.nan), y=y_p, dentro=dentro)


def _confere(fit: dict, row: pd.Series, nome: str) -> None:
    for k in ("tau", "ic95_inf", "ic95_sup", "p_valor"):
        if abs(float(fit["r"][k]) - float(row[k])) > TOL:
            raise SystemExit(f"a reta desenhada não reproduz o CSV em {nome}: {k} {fit['r'][k]} != {row[k]}")


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------

def _svg_ticks(a: float, b: float) -> tuple[list[float], int]:
    bruto = (b - a) / 6
    mag = 10 ** math.floor(math.log10(bruto))
    passo = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= bruto)
    k0, k1 = math.ceil(a / passo - 1e-9), math.floor(b / passo + 1e-9)
    casas = max(0, -math.floor(math.log10(passo) + 1e-9))
    if passo < 1 and abs(passo * 10 ** casas - round(passo * 10 ** casas)) > 1e-9:
        casas += 1
    return [k * passo for k in range(k0, k1 + 1)], casas


def _svg_esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;")


def _svg_rot(t: float, casas: int) -> str:
    lab = f"{abs(t):.{casas}f}".replace(".", ",")
    return ("−" if t < 0 and float(lab.replace(",", ".")) != 0 else "") + lab


def _svg_forest(grupos: list[dict], eixo: str, legenda: list[tuple[str, str, bool]], rotulo_aria: str) -> str:
    """Forest plot com eixo comum. grupos = [{titulo, linhas:[{rot, est, lo, hi, cor, oco, val}]}]."""
    W, L, R, TOPO, LH, GH = 800, 300, 545, 34, 21, 24
    todas = [r for g in grupos for r in g["linhas"]]
    a, b = min(min(r["lo"] for r in todas), 0.0), max(max(r["hi"] for r in todas), 0.0)
    pad = 0.06 * (b - a)
    a, b = a - pad, b + pad

    def X(v: float) -> float:
        return L + (v - a) / (b - a) * (R - L)

    y = TOPO + 6
    corpo, y0 = [], y
    for g in grupos:
        if g.get("titulo"):
            corpo.append(f'<text x="0" y="{y + 14}" class="gt">{_svg_esc(g["titulo"])}</text>')
            y += GH
        for r in g["linhas"]:
            cy = y + LH / 2
            corpo.append(f'<text x="{L - 10}" y="{cy + 4}" class="rl" text-anchor="end">{_svg_esc(r["rot"])}</text>')
            corpo.append(f'<line x1="{X(r["lo"]):.1f}" y1="{cy}" x2="{X(r["hi"]):.1f}" y2="{cy}" stroke="{r["cor"]}" '
                         f'stroke-width="2.4" stroke-linecap="round"/>')
            fill = "#ffffff" if r["oco"] else r["cor"]
            corpo.append(f'<circle cx="{X(r["est"]):.1f}" cy="{cy}" r="5" fill="{fill}" stroke="{r["cor"]}" '
                         f'stroke-width="2"/>')
            corpo.append(f'<text x="{R + 14}" y="{cy + 4}" class="val">{_svg_esc(r["val"])}</text>')
            y += LH
        y += 6
    y1 = y
    ticks, casas = _svg_ticks(a, b)
    grade, eixo_svg = [], []
    for t in ticks:
        grade.append(f'<line x1="{X(t):.1f}" y1="{y0}" x2="{X(t):.1f}" y2="{y1}" stroke="#e1e0d9" stroke-width="1"/>')
        eixo_svg.append(f'<text x="{X(t):.1f}" y="{y1 + 16}" class="tick" text-anchor="middle">{_svg_rot(t, casas)}</text>')
    zero = (f'<line x1="{X(0.0):.1f}" y1="{y0 - 2}" x2="{X(0.0):.1f}" y2="{y1}" stroke="#52514e" '
            f'stroke-width="1.4" stroke-dasharray="4 3"/>')
    leg, lx = [], 0
    for cor, nome, oco in legenda:
        fill = "#ffffff" if oco else cor
        leg.append(f'<circle cx="{lx + 6}" cy="12" r="5" fill="{fill}" stroke="{cor}" stroke-width="2"/>'
                   f'<text x="{lx + 16}" y="16" class="leg">{_svg_esc(nome)}</text>')
        lx += 16 + 6.0 * len(nome) + 20
    H = y1 + 44
    estilo = ('<style>text{font-family:Inter,"Liberation Sans",sans-serif;fill:#0b0b0b}.rl{font-size:11.5px}'
              '.gt{font-size:12px;font-weight:650}.val{font-size:11px;fill:#52514e}.tick{font-size:10.5px;fill:#52514e}'
              '.leg{font-size:11px;fill:#52514e}.eixo{font-size:11px;fill:#52514e}</style>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" role="img" aria-label="{_svg_esc(rotulo_aria)}">'
            f'{estilo}{"".join(grade)}{zero}{"".join(leg)}{"".join(corpo)}{"".join(eixo_svg)}'
            f'<text x="{(L + R) / 2:.0f}" y="{y1 + 34}" class="eixo" text-anchor="middle">{_svg_esc(eixo)}</text></svg>')


def _svg_placebo(pontos: list[dict], reais: list[dict], eixo_x: str, eixo_y: str, rotulo_aria: str) -> str:
    W, H, L, R, T, B = 760, 330, 62, 740, 18, 52
    todos = pontos + reais
    xa, xb = min(p["x"] for p in todos), max(p["x"] for p in todos)
    ya, yb = min(min(p["lo"] for p in todos), 0.0), max(max(p["hi"] for p in todos), 0.0)
    pad = 0.05 * (yb - ya)
    ya, yb = ya - pad, yb + pad
    px = 0.03 * (xb - xa)

    def X(v: float) -> float:
        return L + (v - xa + px) / (xb - xa + 2 * px) * (R - L)

    def Y(v: float) -> float:
        return T + (yb - v) / (yb - ya) * (H - T - B)

    g = []
    yt, cy = _svg_ticks(ya, yb)
    for t in yt:
        g.append(f'<line x1="{L}" y1="{Y(t):.1f}" x2="{R}" y2="{Y(t):.1f}" stroke="#e1e0d9"/>'
                 f'<text x="{L - 8}" y="{Y(t) + 4:.1f}" class="tick" text-anchor="end">{_svg_rot(t, cy)}</text>')
    xt, cx = _svg_ticks(xa, xb)
    for t in xt:
        g.append(f'<text x="{X(t):.1f}" y="{H - B + 16}" class="tick" text-anchor="middle">{f"{t:.{cx}f}".replace(".", ",")}</text>')
    g.append(f'<line x1="{L}" y1="{Y(0.0):.1f}" x2="{R}" y2="{Y(0.0):.1f}" stroke="#52514e" stroke-width="1.4" '
             f'stroke-dasharray="4 3"/>')
    for p in pontos:
        g.append(f'<line x1="{X(p["x"]):.1f}" y1="{Y(p["lo"]):.1f}" x2="{X(p["x"]):.1f}" y2="{Y(p["hi"]):.1f}" '
                 f'stroke="{CINZA}" stroke-width="2" stroke-linecap="round"/>'
                 f'<circle cx="{X(p["x"]):.1f}" cy="{Y(p["est"]):.1f}" r="3.8" fill="{CINZA}"/>')
    for p in reais:
        g.append(f'<line x1="{X(p["x"]):.1f}" y1="{T}" x2="{X(p["x"]):.1f}" y2="{H - B}" stroke="{LARANJA}" '
                 f'stroke-width="1.2" stroke-dasharray="2 3"/>'
                 f'<line x1="{X(p["x"]):.1f}" y1="{Y(p["lo"]):.1f}" x2="{X(p["x"]):.1f}" y2="{Y(p["hi"]):.1f}" '
                 f'stroke="{LARANJA}" stroke-width="2.8" stroke-linecap="round"/>'
                 f'<circle cx="{X(p["x"]):.1f}" cy="{Y(p["est"]):.1f}" r="5.5" fill="{LARANJA}"/>')
    estilo = ('<style>text{font-family:Inter,"Liberation Sans",sans-serif;fill:#0b0b0b}.tick{font-size:10.5px;fill:#52514e}'
              '.eixo{font-size:11px;fill:#52514e}</style>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{_svg_esc(rotulo_aria)}">'
            f'{estilo}{"".join(g)}<text x="{(L + R) / 2:.0f}" y="{H - 12}" class="eixo" text-anchor="middle">'
            f'{_svg_esc(eixo_x)}</text><text x="14" y="{(T + H - B) / 2:.0f}" class="eixo" text-anchor="middle" '
            f'transform="rotate(-90 14 {(T + H - B) / 2:.0f})">{_svg_esc(eixo_y)}</text></svg>')


def _png_rd(N23, paineis: list[dict], ylabel: str, caminho: Path) -> None:
    """Dois painéis (um por corte): médias por faixa de 0,010, retas por lado, IC 95% da reta e seta do salto."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    sup = N23.SUPERFICIE
    fig, eixos = plt.subplots(1, len(paineis), figsize=(10.8, 4.9), facecolor=sup)
    fig.subplots_adjust(left=0.08, right=0.985, top=0.86, bottom=0.2, wspace=0.22)
    for ax, p in zip(np.atleast_1d(eixos), paineis):
        ax.set_facecolor(sup)
        ok = np.isfinite(p["x"]) & np.isfinite(p["y"])
        fx = N23._faixas(p["x"][ok])
        for f in np.unique(fx):
            m = fx == f
            ax.scatter(np.mean(p["x"][ok][m]) / 1000, np.mean(p["y"][ok][m]), s=N23._area(int(m.sum())),
                       color=N23.COR_DENTRO, edgecolor=sup, linewidth=1.2, zorder=3, alpha=0.95)
        cur = p["cur"]
        for lado in ("abaixo", "acima"):
            gx, pr, lo, hi = cur[lado]
            ax.fill_between(gx / 1000, lo, hi, color=N23.COR_BANDA, alpha=0.16, linewidth=0, zorder=1)
            ax.plot(gx / 1000, pr, color=N23.COR_RETA, linewidth=2, zorder=2)
        y0, y1 = cur["abaixo"][1][-1], cur["acima"][1][0]
        ax.axvline(0, color=N23.TINTA_2, linewidth=1, linestyle="--", zorder=0)
        ax.annotate("", xy=(0, y1), xytext=(0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=N23.COR_SALTO, linewidth=2.4, mutation_scale=13), zorder=4)
        ax.set_title(p["titulo"], fontsize=11, color=N23.TINTA)
        ax.set_xlabel("distância ao corte (IVS − corte); 0 = o corte", fontsize=10.5, color=N23.TINTA_2)
        ax.grid(alpha=0.25, linewidth=0.6)
        ax.tick_params(colors=N23.TINTA_2, labelsize=10)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(N23._fmt_eixo_x))
        ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
    np.atleast_1d(eixos)[0].set_ylabel(ylabel, fontsize=10.5, color=N23.TINTA_2)
    handles = [Line2D([], [], marker="o", linestyle="", color=N23.COR_DENTRO, markersize=8,
                      label="média dos municípios na faixa"),
               Line2D([], [], color=N23.COR_RETA, linewidth=2, label="reta ajustada (cada lado)"),
               Patch(color=N23.COR_BANDA, alpha=0.16, label="IC 95%"),
               Line2D([], [], color=N23.COR_SALTO, linewidth=2.4, label="salto no corte")]
    fig.legend(handles=handles, loc="lower center", ncol=4, fontsize=10.5, frameon=False, bbox_to_anchor=(0.5, 0.0))
    PASTA_FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=150, facecolor=sup, metadata={"Software": None})
    plt.close(fig)


def _img(png: Path, alt: str) -> str:
    b64 = base64.b64encode(png.read_bytes()).decode("ascii")
    return f'<figure class="fig"><img src="data:image/png;base64,{b64}" alt="{alt}"></figure>'


def _svg_fig(svg: str, nome: str) -> str:
    PASTA_FIG.mkdir(parents=True, exist_ok=True)
    (PASTA_FIG / f"{nome}.svg").write_text(svg + "\n", encoding="utf-8")
    return f'<figure class="fig">{svg}</figure>'


# ---------------------------------------------------------------------------
# Figuras RD por corte (cada uma com dois painéis)
# ---------------------------------------------------------------------------

def _titulo(d: dict, c: str, valor: str, ic: str, p: str) -> str:
    de, para = d["reais"][c]
    return f"corte {_cs(float(c))} (bolsa de R\\$ {de} mil para R\\$ {para} mil)\nsalto = {valor}  {ic},  p = {p}"


def _figura_rd(N23, V: dict, d: dict, nome: str, ylabel: str, col: str, ctl: str | None, linhas: dict | None,
               unidade: str = "") -> tuple[str, dict]:
    """PNG de dois painéis; `linhas[c]` = linha do CSV (ou None: usa a reta desenhada, descritivo). Devolve (html, saltos)."""
    paineis, saltos = [], {}
    frac = unidade == "pp"
    for c in d["cortes"]:
        fit = _refit(N23, V, int(round(float(c) * 1000)), col, ctl)
        row = linhas[c] if linhas else None
        if row is not None:
            _confere(fit, row, f"{nome} {c}")
        else:
            row = pd.Series({k: fit["r"][k] for k in ("tau", "ic95_inf", "ic95_sup", "p_valor")})
        saltos[c] = row
        if frac:
            valor = _pp(row["tau"])
            ic = f"[IC 95%: {_fmt(100 * row['ic95_inf'], 1)}; {_fmt(100 * row['ic95_sup'], 1)}]"
        else:
            valor = _fmt(row["tau"], 2) + (f" {unidade}" if unidade else "")
            ic = f"[IC 95%: {_fmt(row['ic95_inf'], 2)}; {_fmt(row['ic95_sup'], 2)}]"
        paineis.append(dict(x=fit["x"], y=fit["y"], cur=fit["cur"],
                            titulo=_titulo(d, c, valor, ic, _num(row["p_valor"], 3))))
    png = PASTA_FIG / f"{nome}.png"
    _png_rd(N23, paineis, ylabel, png)
    return _img(png, nome), saltos


# ---------------------------------------------------------------------------
# Forest plots
# ---------------------------------------------------------------------------

def _fig_oferta(d: dict) -> str:
    n = d["n"]
    vic = n[(n["outcome_id"] == "VIC") & (n["especificacao"] == "S-c") & (n["variante"] == "principal")]
    nomes = [("V1", "Ciclo 1"), ("V2", "Ciclo 2"), ("V3", "Ciclo 3"), ("V1+V2+V3", "Ciclos 1 a 3 juntos")]
    grupos = []
    for pop, nome in nomes:
        linhas = []
        for corte in (*d["cortes"], "empilhado"):
            r = _unica(vic, populacao=pop, corte=corte)
            sig = r["p_valor"] < 0.05
            rot = _ctxt(corte) + (" (secundário)" if corte == "empilhado" else "")
            linhas.append(dict(rot=rot, est=r["tau"], lo=r["ic95_inf"], hi=r["ic95_sup"], cor=LARANJA if sig else AZUL,
                               oco=not sig, val=f"{_fmt(r['tau'], 1)} {_ic(r['ic95_inf'], r['ic95_sup'], 1)}  p = {_num(r['p_valor'], 3)}"))
        grupos.append(dict(titulo=nome, linhas=linhas))
    leg = [(AZUL, "IC 95% inclui zero", True), (LARANJA, "IC 95% exclui zero", False)]
    return _svg_forest(grupos, "salto nas vagas oferecidas (imediatas + cadastro reserva), em vagas por município", leg,
                       "Salto das vagas oferecidas em cada corte e ciclo")


def _fig_n1_a_n4(d: dict) -> list[str]:
    svgs = []
    for oid, rot in ROTULOS.items():
        grupos = [dict(titulo=rot, linhas=[])]
        for corte in (*d["cortes"], "empilhado"):
            sec = corte == "empilhado"
            linhas = []
            for esp, nome, cor in (("S-a", "com controle", AZUL), ("S-b", "sem controle", LARANJA)):
                r = _linha_n(d, oid, esp, corte)
                holm = sec and pd.notna(r["p_holm"])
                val = f"{_fmt(r['tau'], 2)} {_ic(r['ic95_inf'], r['ic95_sup'])}  " + (
                    f"Holm p = {_num(r['p_holm'], 3)}" if holm else f"p = {_p(r['p_valor'])}")
                linhas.append(dict(rot=nome, est=r["tau"], lo=r["ic95_inf"], hi=r["ic95_sup"], cor=CINZA if sec else cor,
                                   oco=not _exclui(r), val=val))
            grupos.append(dict(titulo=_ctxt(corte) + (" (secundário: junta dois cortes)" if sec else ""), linhas=linhas))
        leg = [(AZUL, "com controle (S-a)", False), (LARANJA, "sem controle (S-b)", False),
               (CINZA, "empilhado (secundário)", False), (TINTA2, "vazio = IC inclui zero", True)] if oid == "N1" else []
        unidade = {"N1": "vagas", "N2": "células", "N3": "células", "N4": "especialistas"}[oid]
        svgs.append(_svg_forest(grupos, f"salto no corte, em {unidade} por município", leg,
                                f"Salto de {oid} por corte, com e sem controle"))
    return svgs


def _rel(r) -> tuple[float, float, float]:
    m = r["media_abaixo"]
    return r["tau"] / m, r["ic95_inf"] / m, r["ic95_sup"] / m


def _fig_robustez(d: dict, parte: int) -> tuple[str, bool]:
    n, na = d["n"], d["na"]

    def n_(esp, var, c, pop="V1+V2+V3"):
        return _unica(n, outcome_id="N1", especificacao=esp, variante=var, populacao=pop, corte=c)

    def a4(var, c):
        return _unica(na, outcome_id="N1", especificacao="A4", variante=var, populacao="V1+V2+V3", ciclo="1+2+3", corte=c)

    def aa(oid, esp, pop, c):
        return _unica(na, outcome_id=oid, especificacao=esp, variante="principal", populacao=pop, ciclo="1+2+3", corte=c)

    h30 = n_("S-a", "h=0.030", d["cortes"][0])["h"]
    h80 = n_("S-a", "h=0.080", d["cortes"][0])["h"]
    spec = [
        ("Especificação do protocolo", [("com controle", lambda c: n_("S-a", "principal", c)),
                                        ("sem controle", lambda c: n_("S-b", "principal", c))]),
        ("Como entra o controle", [("coef. único (fora do protocolo)", lambda c: n_("S-a", "controle_coeficiente_unico", c)),
                                   ("só vagas imediatas", lambda c: n_("S-a", "controle_forma_alternativa", c))]),
        ("Janela (com controle)", [(f"janela {_cs(h30)}", lambda c: n_("S-a", "h=0.030", c)),
                                   (f"janela {_cs(h80)}", lambda c: n_("S-a", "h=0.080", c))]),
        ("Covariáveis pré-determinadas (sem controle de vagas)", [
            ("sem covariáveis", lambda c: a4("sem_covariaveis_mesma_amostra", c)),
            ("com covariáveis", lambda c: a4("com_covariaveis", c))]),
        ("Outras medidas (sem controle de vagas)", [
            ("por 10 mil habitantes (A1)", lambda c: aa("A1_PREENCH_10K", "A1", "U", c)),
            ("fração de células (A3)", lambda c: aa("A3_PREENCHIDA", "A3", "V1+V2+V3 (celulas)", c))]),
    ]
    for ci in d["ciclos"]:
        spec.append((f"Ciclo {ci} isolado (com controle)", [("", lambda c, ci=ci: n_("S-a", "principal", c, pop=f"V{ci}"))]))
    spec = (spec[:3], spec[3:])[parte]
    grupos, todas_neg = [], True
    cores = dict(zip(d["cortes"], (AZUL, LARANJA)))
    for titulo, itens in spec:
        linhas = []
        for rot, getter in itens:
            for c in d["cortes"]:
                r = getter(c)
                est, lo, hi = _rel(r)
                todas_neg &= not (r["ic95_inf"] > 0)
                linhas.append(dict(rot=(f"{rot} · " if rot else "") + _ctxt(c), est=100 * est, lo=100 * lo, hi=100 * hi,
                                   cor=cores[c], oco=not _exclui(r), val=f"{_pct(est)} {_ic(100 * lo, 100 * hi, 0)}"))
        grupos.append(dict(titulo=titulo, linhas=linhas))
    leg = [(cores[c], _ctxt(c), False) for c in d["cortes"]] + [(TINTA2, "vazio = IC 95% inclui zero", True)]
    return _svg_forest(grupos, "salto em % da média do lado de bolsa menor (salto ÷ média abaixo)", leg,
                       "Robustez do salto de N1 por corte, em % da média abaixo do corte"), bool(todas_neg)


def _fig_placebo(d: dict) -> str:
    n = d["n"]
    base = n[(n["outcome_id"] == "N1") & (n["populacao"] == "V2")]
    gr = base[(base["especificacao"] == "S-i") & (base["variante"] == "grade_E9 (S-a)")]
    pontos = [dict(x=float(r["corte_placebo"]), est=r["tau"], lo=r["ic95_inf"], hi=r["ic95_sup"]) for _, r in gr.iterrows()]
    reais = []
    for c in d["cortes"]:
        r = _unica(base, especificacao="S-a", variante="principal", corte=c)
        reais.append(dict(x=float(c), est=r["tau"], lo=r["ic95_inf"], hi=r["ic95_sup"]))
    return _svg_placebo(pontos, reais, "corte (IVS 2010 oficial); cinza = cortes falsos, laranja = cortes reais",
                        "salto de N1 com controle (vagas), ciclo 2", "Salto em cortes falsos e reais, ciclo 2")


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

def _linhas_saltos(linhas: dict, fmt_valor, fmt_ic) -> list[str]:
    return [f"Corte {_cs(float(c))}: {fmt_valor(r['tau'])} {fmt_ic(r['ic95_inf'], r['ic95_sup'])}, p = {_num(r['p_valor'], 3)}"
            for c, r in linhas.items()]


def _quais_excluem(linhas: dict) -> list[str]:
    return [_cs(float(c)) for c, r in linhas.items() if _exclui(r)]


def _fig_regra(d: dict, V: dict) -> str:
    """Bolsa anunciada × IVS 2010 oficial, desenhada aqui a partir de output/rdd_bolsa/outcomes/ (sem texto embutido)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    cs = [float(c) for c in d["cortes"]]
    niveis = [int(d["reais"][d["cortes"][0]][0])] + [int(d["reais"][c][1]) for c in d["cortes"]]
    vm = pd.concat([v[["co_ibge", "ciclo", "faixa_anunciada", "ivs_2010_oficial"]] for v in V.values()], ignore_index=True)
    vm = vm[vm["ivs_2010_oficial"].notna()].drop_duplicates(["co_ibge"])
    x = vm["ivs_2010_oficial"].to_numpy(dtype=float)
    y = np.array([niveis[sum(v > c for c in cs)] for v in x], dtype=float)
    for _, g in pd.DataFrame({"f": vm["faixa_anunciada"].to_numpy(), "y": y}).groupby("f"):
        if g["y"].nunique() != 1:
            raise SystemExit("a faixa anunciada não reproduz a regra por IVS (regra não é sharp)")
    sup = "#fcfcfb"
    fig, ax = plt.subplots(figsize=(10.8, 4.9), facecolor=sup)
    ax.set_facecolor(sup)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.9, bottom=0.14)
    rng = np.random.default_rng(len(x))
    ax.scatter(x, y + rng.uniform(-0.45, 0.45, len(y)), s=10, color=AZUL, alpha=0.45, linewidth=0, zorder=2)
    for i, c in enumerate(cs):
        ax.axvline(c, color=TINTA2, linestyle="--", linewidth=1.2, zorder=1)
        ax.annotate(f"+R$ {niveis[i + 1] - niveis[i]} mil", xy=(c, niveis[i + 1] - 1.2), xytext=(8, 0), textcoords="offset points",
                    color=LARANJA, fontsize=12, fontweight="bold", va="center")
        ax.text(c, niveis[-1] + 2.4, _cs(c), ha="center", fontsize=11, color=TINTA2)
    ax.set_yticks(niveis)
    ax.set_yticklabels([f"R$ {v} mil" for v in niveis], fontsize=11)
    ax.set_ylim(niveis[0] - 3, niveis[-1] + 4)
    ax.set_xlabel("IVS 2010 oficial do município", fontsize=11, color=TINTA2)
    ax.set_ylabel("bolsa anunciada por mês", fontsize=11, color=TINTA2)
    ax.set_title("Cada ponto é um município do quadro de vagas", fontsize=12, loc="left")
    ax.grid(alpha=0.25, linewidth=0.6)
    ax.tick_params(colors=TINTA2, labelsize=10)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    PASTA_FIG.mkdir(parents=True, exist_ok=True)
    caminho = PASTA_FIG / "regra_bolsa_ivs.png"
    fig.savefig(caminho, dpi=150, facecolor=sup, metadata={"Software": None})
    plt.close(fig)
    return _img(caminho, "regra_bolsa_ivs")


def _slide(titulo: str, figura: str = "", bullets: list[str] | None = None, como_ler: str = "", fonte: str = "",
           classe: str = "", diag: bool = False) -> str:
    """Um slide 16:9: título = conclusão, figura à esquerda, bullets à direita, 'Como ler' no rodapé."""
    lis = "".join(f"<li>{b}</li>" for b in (bullets or []))
    rot = '<span class="diag">diagnóstico descritivo, fora do protocolo 48</span>' if diag else ""
    corpo = (f'<div class="corpo"><div class="figbox">{figura}</div><div class="coltxt">{rot}<ul class="bullets">{lis}</ul></div></div>'
             if figura else f'<div class="corpo texto"><ul class="bullets">{lis}</ul></div>')
    rod = ""
    if como_ler or fonte:
        rod = (f'<div class="rodape"><span class="cl">{("<b>Como ler:</b> " + como_ler) if como_ler else ""}</span>'
               f'<span class="fo">{fonte}</span></div>')
    return f'<section class="slide {classe}"><h2 class="titulo">{titulo}</h2>{corpo}{rod}</section>'


CSS_SLIDES = """
@page { size: 338.667mm 190.5mm; margin: 0; }
:root { --s1: #2a78d6; }
html, body { margin: 0; padding: 0; }
body { font-family: Inter, "Liberation Sans", "DejaVu Sans", system-ui, sans-serif; color: #0b0b0b; background: #e9e8e3;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.slide { width: 338.667mm; height: 190.4mm; box-sizing: border-box; padding: 9mm 14mm 6mm; background: #fff;
  display: flex; flex-direction: column; overflow: hidden; break-after: page; page-break-after: always; }
.slide:last-child { break-after: auto; page-break-after: auto; }
@media screen { .slide { margin: 10px auto; box-shadow: 0 1px 6px rgba(0,0,0,.18); max-width: 100%; }
  body { scroll-snap-type: y proximity; } .slide { scroll-snap-align: start; } }
h2.titulo { font-size: 23pt; font-weight: 650; line-height: 1.15; margin: 0 0 4mm; letter-spacing: -0.01em;
  min-height: 20mm; border-left: 2.2mm solid var(--s1); padding-left: 4mm; }
.corpo { flex: 1; min-height: 0; display: grid; grid-template-columns: minmax(0, 1fr) 86mm; gap: 9mm; align-items: center; }
.corpo.texto { grid-template-columns: minmax(0, 1fr); align-items: start; }
.figbox { min-height: 0; height: 128mm; display: flex; flex-direction: column; align-items: center;
  justify-content: center; gap: 2mm; overflow: hidden; }
.figbox figure { margin: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; } .figbox img { max-width: 100%; max-height: 126mm; width: auto; height: auto; display: block; }
.figbox svg { width: 100%; height: 100%; display: block; }
.dois { display: flex; flex-direction: column; gap: 2mm; align-items: center; min-height: 0; }
.dois { width: 100%; height: 100%; display: flex; flex-direction: column; gap: 2mm; }
.dois figure { height: auto; flex: 1 1 0; min-height: 0; } .dois svg { width: 100%; height: 100%; }
.coltxt { min-width: 0; }
.bullets { list-style: none; margin: 0; padding: 0; font-size: 15pt; line-height: 1.32; }
.bullets li { margin: 0 0 4.5mm; padding-left: 5mm; position: relative; }
.bullets li::before { content: ""; position: absolute; left: 0; top: 0.55em; width: 2.2mm; height: 2.2mm; border-radius: 50%;
  background: var(--s1); }
.texto .bullets { font-size: 19pt; columns: 1; }
.notas .bullets { font-size: 14pt; }
.rodape { display: flex; gap: 8mm; justify-content: space-between; border-top: 1px solid #e1e0d9; margin-top: 3mm; padding-top: 2mm;
  font-size: 8.4pt; line-height: 1.3; color: #52514e; }
.rodape .fo { color: #898781; text-align: right; white-space: nowrap; }
.rodape code { font-family: "DejaVu Sans Mono", monospace; font-size: 7.4pt; }
.capa { justify-content: center; }
.capa h1 { font-size: 38pt; line-height: 1.1; margin: 0 0 6mm; font-weight: 650; }
.capa .sub { font-size: 16pt; color: #52514e; margin: 0 0 12mm; }
.dois-col { display: grid; grid-template-columns: 1fr 1fr; gap: 12mm; }
.dois-col h3 { font-size: 13pt; text-transform: uppercase; letter-spacing: .06em; color: var(--s1); margin: 0 0 4mm; }
.dois-col .bullets { font-size: 16pt; }
.diag { display: inline-block; font-size: 9pt; text-transform: uppercase; letter-spacing: .06em; color: #8a5d00;
  background: #fbf5e6; border-radius: 3px; padding: 1mm 2.5mm; margin-bottom: 3mm; }
"""

JS_NAV = """<script>
document.addEventListener('keydown', function (e) {
  var s = Array.prototype.slice.call(document.querySelectorAll('section.slide'));
  var y = window.scrollY + 40, i = 0;
  s.forEach(function (el, k) { if (el.offsetTop <= y) i = k; });
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') { i = Math.min(i + 1, s.length - 1); }
  else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { i = Math.max(i - 1, 0); } else { return; }
  e.preventDefault(); s[i].scrollIntoView({behavior: 'smooth', block: 'start'});
});
</script>"""

FONTE_PNG = "Gráfico: <code>gerar_slides_contagem_vagas_professores.py</code> · números de <code>{}</code>"


def montar_html() -> str:
    d = _dados()
    res = d["res"]
    N23 = _modulo_n()
    V = _png_hab_para_mil(_carregar_v(N23))
    degrau = re.search(r"R\$ \d+ mil", res["contraste"]).group(0)
    cs = d["cortes"]
    cortes = " e ".join(_cs(c) for c in cs)
    ciclos = f"{d['ciclos'][0]} a {d['ciclos'][-1]}"
    h = _cs(d["h"])
    ctl = res["controle"]["principal_coluna"]
    r_sc = res["veredito_S_c"]
    LER_RD = ("cada ponto é a média dos municípios numa faixa de IVS. À direita do corte a bolsa é maior; a seta mostra a "
              "diferença entre as duas retas no corte.")
    u1 = lambda v: _fmt(v, 2)  # noqa: E731
    ic2 = lambda a, b: _ic(a, b)  # noqa: E731

    # --- Refits e saltos por corte (conferidos contra os CSV)
    vi = {c: _unica(d["n"], outcome_id="VI", especificacao="S-c", variante="principal", populacao="V1+V2+V3", corte=c)
          for c in cs}
    fig_vi, s_vi = _figura_rd(N23, V, d, "porte_vagas_imediatas", "vagas imediatas oferecidas (nº por município)",
                              "vagas_imediatas", None, vi, unidade="vagas")
    fig_pop, s_pop = _figura_rd(N23, V, d, "porte_populacao", "população de 2022 (mil habitantes)", "pop_mil", None, None,
                                unidade="mil hab.")
    atr = {c: _linha_e6(d, "f1_1_cand_1a_opcao_por_celula", c) for c in cs}
    fig_atr, s_atr = _figura_rd(N23, V, d, "atracao_candidatos", "candidatos de 1ª opção por célula (média por município)",
                                "f1_1_cand_1a_opcao_por_celula", None, atr, unidade="candidatos")
    taxa = {c: _linha_e6(d, "f1_3_fracao_celulas_preenchidas_ch1", c) for c in cs}
    fig_taxa, s_taxa = _figura_rd(N23, V, d, "taxa_preenchimento", "fração das células preenchidas na 1ª chamada",
                                  "f1_3_fracao_celulas_preenchidas_ch1", None, taxa, unidade="pp")
    n1b = {c: _linha_n(d, "N1", "S-b", c) for c in cs}
    n1a = {c: _linha_n(d, "N1", "S-a", c) for c in cs}
    fig_sem, _ = _figura_rd(N23, V, d, "n1_sem_controle", "vagas preenchidas na 1ª chamada (nº por município)",
                            "n_alocados_ch1", None, n1b, unidade="vagas")
    fig_com, _ = _figura_rd(N23, V, d, "n1_com_controle", "vagas preenchidas, ajustadas às vagas oferecidas\n(nº por município)",
                            "n_alocados_ch1", ctl, n1a, unidade="vagas")

    sl = []
    # 1. Abertura
    sl.append('<section class="slide capa"><h1>Nº de vagas preenchidas como variável de efeito</h1>'
              '<p class="sub">RDD do adicional da bolsa do PMM-E · família N (protocolo 48) · para os professores</p>'
              '<ul class="bullets" style="font-size:18pt">'
              '<li>O efeito passa da <b>fração</b> de vagas preenchidas para o <b>número</b> de vagas preenchidas na 1ª chamada.</li>'
              f'<li>Contraste = <b>pacote do corte</b> ({cortes}); não é o degrau de {degrau} isolado nem a participação no PMM-E.</li>'
              f'<li>Cada corte é estimado separadamente, juntando os ciclos {ciclos}.</li></ul></section>')

    # 2. Regra
    sl.append(_slide(f"A bolsa sobe em degrau exatamente nos cortes de IVS {cortes}", _fig_regra(d, V),
                     [f"Degrau de {degrau} por mês em cada corte.", "Municípios logo abaixo e logo acima são parecidos.",
                      "Mudam também outras regras federais: o contraste é o pacote do corte."],
                     "cada ponto é um município; a bolsa anunciada pula nos dois cortes de IVS.",
                     FONTE_PNG.format("outcomes_V_municipio.parquet e N_resumo.json")))

    # 3. Porte: oferta
    vi_neg = all(r["tau"] < 0 for r in s_vi.values())
    sl.append(_slide("Do lado de bolsa maior, a oferta de vagas é menor nos dois cortes" if vi_neg
                     else "A oferta de vagas difere entre os lados do corte",
                     fig_vi,
                     ["Contagem = vagas oferecidas × taxa de preenchimento.", *_linhas_saltos(s_vi, u1, ic2),
                      "Menos vagas à direita puxa a contagem para baixo." if vi_neg else "A oferta não tem o mesmo sinal nos dois cortes."],
                     LER_RD, FONTE_PNG.format("N_estimativas.csv (S-c, VI)"), diag=True))
    # 4. Porte: população
    pop_neg = all(r["tau"] < 0 for r in s_pop.values())
    pop_zero = all(not _exclui(r) for r in s_pop.values())
    cov = {c: _unica(d["na"], outcome_id="COV_log_pop22", especificacao="A4", populacao="V1+V2+V3", ciclo="1+2+3", corte=c)
           for c in cs}
    cov_zero = all(not _exclui(r) for r in cov.values())
    sl.append(_slide(("A população também é menor à direita, mas com muita incerteza" if pop_neg and pop_zero
                      else "A população difere entre os lados do corte"),
                     fig_pop,
                     [*_linhas_saltos(s_pop, lambda v: _fmt(v, 1) + " mil", lambda a, b: _ic(a, b, 1)),
                      "Em log, " + ("sem salto distinguível de zero nos dois cortes." if cov_zero else "há salto em algum corte.")],
                     LER_RD, FONTE_PNG.format("a reta desenhada; log: NA_estimativas.csv"), diag=True))
    # 5. Controle pela oferta
    sl.append(_slide(f"A oferta salta em {r_sc['n_p_menor_005']} de {r_sc['n_linhas']} comparações: controlar por ela exige cuidado",
                     _svg_fig(_fig_oferta(d), "oferta_no_corte_S-c"),
                     [f"Salta em {r_sc['quais']}.", "Com controle: preenchimento para a mesma oferta.",
                      "Sem controle: efeito total (oferecer e preencher).", "Mostramos as duas leituras."],
                     "cada linha é a diferença na oferta de vagas entre os dois lados do corte, com seu intervalo; laranja = o intervalo não inclui zero.",
                     FONTE_PNG.format("N_estimativas.csv (S-c)")))

    # 6. Atração
    ex = _quais_excluem(s_atr)
    sl.append(_slide("A atração não muda em nenhum dos dois cortes" if not ex else
                     f"A atração muda só no corte {', '.join(ex)}",
                     fig_atr, [*_linhas_saltos(s_atr, u1, ic2),
                               "Os ICs incluem zero." if not ex else "Os demais ICs incluem zero.",
                               "Falta de evidência, não prova de efeito nulo."],
                     LER_RD, FONTE_PNG.format("E6_estimativas.csv")))
    # 7. Taxa
    ex = _quais_excluem(s_taxa)
    neg = all(r["tau"] < 0 for r in s_taxa.values())
    sl.append(_slide("A taxa de preenchimento não aumenta do lado de bolsa maior" if neg and not ex else
                     "A taxa de preenchimento difere entre os lados do corte",
                     fig_taxa,
                     [*_linhas_saltos(s_taxa, _pp, lambda a, b: f"[{_fmt(100 * a, 1)}; {_fmt(100 * b, 1)}]"),
                      "Nenhum IC exclui zero." if not ex else f"O IC exclui zero em {', '.join(ex)}.",
                      "Fração de células com alocado: não depende da oferta."],
                     LER_RD, FONTE_PNG.format("E6_estimativas.csv")))

    # 8. N1 sem e com controle
    ex_b, ex_a = _quais_excluem(n1b), _quais_excluem(n1a)
    negb = all(r["tau"] < 0 for r in n1b.values())
    sl.append(_slide(("Sem controle, as vagas preenchidas não aumentam" + (", e nenhum IC exclui zero" if not ex_b else
                      f"; o IC exclui zero só em {', '.join(ex_b)}")) if negb else "Sem controle, o sinal muda entre os cortes",
                     fig_sem, [*_linhas_saltos(n1b, u1, ic2), "Efeito total da faixa, inclui a resposta da oferta.",
                               "Pacote do corte."],
                     LER_RD, FONTE_PNG.format("N_estimativas.csv (S-b)")))
    nega = all(r["tau"] < 0 for r in n1a.values())
    sl.append(_slide(("Com controle, o salto negativo se concentra no corte " + ", ".join(ex_a) if ex_a and nega else
                      "Com controle, nenhum IC exclui zero" if not ex_a else "Com controle, o sinal muda entre os cortes"),
                     fig_com, [*_linhas_saltos(n1a, u1, ic2), "Preenchimento dado a oferta; condicional a ela.",
                               "Sem correção para comparações múltiplas por corte."],
                     LER_RD + " O eixo vertical compara municípios com a mesma oferta de vagas.", FONTE_PNG.format("N_estimativas.csv (S-a)")))

    # 9. Forest N1–N4
    fs = [_svg_fig(sv, f"coeficientes_{o.lower()}") for sv, o in zip(_fig_n1_a_n4(d), ROTULOS)]
    todas = [_linha_n(d, o, e, c) for o in ROTULOS for e in ("S-a", "S-b") for c in cs]
    ex_cuts = {c for o in ROTULOS for e in ("S-a", "S-b") for c in cs if _exclui(_linha_n(d, o, e, c))}
    emp_a = [_linha_n(d, o, "S-a", "empilhado") for o in ROTULOS]
    holm_ok = all(r["p_holm"] >= 0.05 for r in emp_a)
    if not any(r["ic95_inf"] > 0 for r in todas) and ex_cuts == {cs[0]}:
        tit = f"Nenhum resultado indica aumento; o sinal negativo se concentra no corte {_cs(float(cs[0]))}"
    elif not any(r["ic95_inf"] > 0 for r in todas) and not ex_cuts:
        tit = "Nenhum resultado indica aumento e nenhum IC por corte exclui zero"
    else:
        tit = "Nenhum resultado indica aumento; alguns ICs por corte excluem zero"
    bl9 = ["Marcador cheio: o intervalo não inclui zero.",
           "Cinza (empilhado) é secundário: junta dois cortes.",
           "Holm, só no empilhado com controle: " + ("nenhuma das quatro rejeita zero." if holm_ok else "alguma rejeita zero.")]
    cl9 = "cada linha é a diferença estimada entre os dois lados do corte (barra = intervalo); à esquerda do zero, menos vagas do lado de bolsa maior."
    sl.append(_slide(tit, f'<div class="dois">{fs[0]}{fs[1]}</div>', bl9, cl9, FONTE_PNG.format("N_estimativas.csv"),
                     classe="f2"))
    sl.append(_slide("N3 e N4 seguem o mesmo padrão", f'<div class="dois">{fs[2]}{fs[3]}</div>',
                     ["N3 e N4 só existem nos ciclos 1 e 2.", "Saltos negativos ou próximos de zero.",
                      "Nenhum IC fica acima de zero." if not any(r["ic95_inf"] > 0 for r in todas) else "Há IC acima de zero."], cl9, FONTE_PNG.format("N_estimativas.csv"), classe="f2"))

    # 10. Robustez
    sens = next(x for x in res["sensibilidade_coeficiente_unico_auditoria_20"]["linhas"] if x["outcome_id"] == "N1")
    svg_a, neg_a = _fig_robustez(d, 0)
    svg_b, neg_b = _fig_robustez(d, 1)
    sl.append(_slide("Nenhuma variação do controle ou da janela produz aumento distinguível de zero" if neg_a else
                     "Algumas variações do controle ou da janela têm IC acima de zero",
                     _svg_fig(svg_a, "robustez_n1_controle_janela"),
                     [f"Um só coeficiente do controle: {_fmt(sens['tau_coef_unico'], 2)} vaga, Holm p = {_num(sens['p_holm_coef_unico'], 3)}.",
                      f"Wald rejeita coeficientes iguais (p {_p(sens['wald_igualdade_p'])}); protocolo usa um por ciclo × corte.",
                      "Leitura: negativo, frágil."],
                     "cada linha refaz a análise de N1 de outro jeito; a diferença vem em % do valor médio do lado de bolsa menor.",
                     FONTE_PNG.format("N_estimativas.csv, N_resumo.json")))
    sl.append(_slide("Com covariáveis, por habitante ou por ciclo, tampouco aparece aumento distinguível de zero" if neg_b else
                     "Algumas variações têm IC acima de zero",
                     _svg_fig(svg_b, "robustez_n1_covariaveis_medidas_ciclos"),
                     ["Covariáveis: log da população e estoques do CNES pré-programa.",
                      "O padrão por corte se repete.", "O corte " + _cs(float(cs[0])) + " concentra os saltos negativos."],
                     "cada linha refaz a análise de N1 de outro jeito; a diferença vem em % do valor médio do lado de bolsa menor.",
                     FONTE_PNG.format("N_estimativas.csv, NA_estimativas.csv")))
    # 11. Placebo
    pl = next(x for x in res["placebos_grade"] if x["outcome_id"] == "N1" and x["ciclo"] == "2"
              and x["especificacao"] == "S-a" and x["corte"] == "0.300")
    seg = _unica(d["n"][(d["n"]["outcome_id"] == "N1") & (d["n"]["populacao"] == "V2")], especificacao="S-i",
                 variante="media_do_segmento_entre_0,300_e_0,400 (S-b)")
    sl.append(_slide("No ciclo 2, um corte falso também mostra salto: cautela com a reta local" if _exclui(seg) else
                     "No ciclo 2, os cortes falsos não mostram salto isolado",
                     _svg_fig(_fig_placebo(d), "placebo_ciclo2"),
                     [f"Corte {_cs(float(pl['corte']))}: t = {_fmt(pl['t_real'], 2)}, p por posto = {_num(pl['p_posto'], 3)} ({pl['n_placebos']} cortes falsos).",
                      f"Corte falso entre os dois reais: {_fmt(seg['tau'], 2)} {_ic(seg['ic95_inf'], seg['ic95_sup'])}.",
                      "Põe em dúvida a reta local do ciclo 2."],
                     "cinza = diferença num corte falso, onde a bolsa não muda; laranja = os cortes reais.",
                     FONTE_PNG.format("N_estimativas.csv, N_resumo.json")))

    # 12. Conclusão
    sl.append('<section class="slide"><h2 class="titulo">Contar vagas não faz aparecer efeito positivo, e a contagem acompanha o porte</h2>'
              '<div class="corpo texto"><div class="dois-col"><div><h3>Pode-se afirmar</h3><ul class="bullets">'
              f'<li>Sem aumento em nenhum dos dois cortes ({degrau}, pacote do corte).</li>'
              '<li>Sinais negativos, concentrados no corte inferior; sem Holm no empilhado.</li>'
              '<li>Contagem = oferta × taxa; atração e taxa sem salto distinguível de zero.</li></ul></div>'
              '<div><h3>Não se pode afirmar</h3><ul class="bullets">'
              '<li>Que a bolsa reduz o preenchimento (pacote, porte, placebo).</li>'
              '<li>Que o salto com controle é causal por vaga.</li>'
              '<li>Nada sobre PMM-E, Agora Tem Especialistas ou retenção.</li>'
              '<li>Falta de evidência não é prova de efeito nulo.</li></ul></div></div></div></section>')

    sl.append(_slide("Notas técnicas", "", [
        f"RDD local linear, kernel triangular, janela h = {h} de IVS (IVS 2010 oficial do Ipea), cortes {cortes}, um corte por vez.",
        f"Ciclos {ciclos} juntos em cada corte, com intercepto e inclinação por ciclo; erro-padrão por município (CR1); salto = lado de bolsa maior menos lado de bolsa menor.",
        "Com controle: vagas oferecidas (imediatas + cadastro reserva) entram linearmente, um coeficiente por ciclo e corte; sem controle é o efeito total.",
        "Pontos: médias por faixa estreita de IVS, só municípios dentro da janela; faixa clara = IC 95% da reta. A reta desenhada reproduz o salto, o IC e o p dos CSV; o script aborta se não reproduzir.",
        "Holm só na linha de cortes empilhados com controle (N1 a N4). Diagnóstico de porte (vagas imediatas e população 2022): descritivo, fora do protocolo 48.",
    ], "", "protocolo 48 e docs/06_execucao/49", classe="notas"))
    return ('<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>Contagem de vagas preenchidas: slides</title><style>{CSS_SLIDES}</style></head><body>'
            + "".join(sl) + JS_NAV + '</body></html>\n')


def main() -> None:
    SAIDA_HTML.write_text(montar_html(), encoding="utf-8")
    FIG._imprimir_pdf(SAIDA_HTML, SAIDA_PDF)
    print(f"gravado: {SAIDA_HTML.relative_to(ROOT)} e {SAIDA_PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
