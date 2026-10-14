"""Monta o relatorio de resultados da RDD da bolsa do PMM-E (HTML e PDF).

O relatorio e material de trabalho para o grupo ler os resultados e, depois,
montar slides. Nao estima nada novo: le exclusivamente arquivos de `output/`
(e o IVS 2010 observado em `data/`, para a comparacao com o escore
administrativo) e os apresenta em tabelas e graficos SVG gerados aqui, sem
bibliotecas de grafico (apenas numpy, pandas e a biblioteca padrao).

Entradas
--------
- output/rdd_bolsa/portao_r1_escore_administrativo.json  (portao R1)
- output/rdd_bolsa/matriz_municipio_escore_administrativo.csv  (R1, municipio x quadro)
- output/rdd_bolsa/protocolo_escore_administrativo.json  (protocolo congelado)
- data/ivs_ipea_2010_municipios.csv  (IVS 2010 publico, observado)
- output/rdd_bolsa/E1_densidade_{estimativas,contagens}.csv, E1_densidade_resumo.json
- output/rdd_bolsa/E2_limites.csv, E2_limites_resumo.json
- output/rdd_bolsa/E3_status.json

Os arquivos de E1, E2 e E3 podem ainda nao existir; nesse caso a secao
correspondente sai marcada como pendente e o relatorio e gerado do mesmo jeito.

Saidas
------
- output/rdd_bolsa/relatorio_resultados_rdd_bolsa.html  (autocontido)
- output/rdd_bolsa/relatorio_resultados_rdd_bolsa.pdf  (A4 retrato, via Chromium headless)

Linguagem: E1 e E2 sao exploratorios (E1 condicional a premissa A1; E2 limites
parciais). Nada aqui e efeito causal estabelecido. O contraste e o incentivo
marginal anunciado de R$ 5 mil, nao participacao no PMM-E.
"""

from __future__ import annotations

import datetime as dt
import glob
import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ESTE_SCRIPT = Path(__file__).resolve()
OUT_DIR = ROOT / "output" / "rdd_bolsa"

R1_JSON = OUT_DIR / "portao_r1_escore_administrativo.json"
MATRIZ = OUT_DIR / "matriz_municipio_escore_administrativo.csv"
PROTOCOLO = OUT_DIR / "protocolo_escore_administrativo.json"
IVS_2010 = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
E1_EST = OUT_DIR / "E1_densidade_estimativas.csv"
E1_CONT = OUT_DIR / "E1_densidade_contagens.csv"
E1_RES = OUT_DIR / "E1_densidade_resumo.json"
E2_LIM = OUT_DIR / "E2_limites.csv"
E2_RES = OUT_DIR / "E2_limites_resumo.json"
E3_STATUS = OUT_DIR / "E3_status.json"

OUT_HTML = OUT_DIR / "relatorio_resultados_rdd_bolsa.html"
OUT_PDF = OUT_DIR / "relatorio_resultados_rdd_bolsa.pdf"

TITULO = "RDD da bolsa do PMM-E — resultados"

# Parametros de exibicao (nao sao dados): quadro e bins do grafico de
# "primeiro estagio" e semente do deslocamento vertical do grafico da regra.
QUADRO_PRIMEIRO_ESTAGIO = "c1_ch1"
BIN_PRIMEIRO_ESTAGIO_MILESIMOS = 20  # 0,020
N_BINS_POR_LADO = 3  # 0,340 a 0,460 em torno de 0,400
BIN_CONTAGENS_MILESIMOS = 5  # 0,005
SEMENTE_JITTER = 20261014

# Paleta (dataviz, instancia de referencia, modo claro). Categorica validada
# com scripts/validate_palette.js: azul/laranja passam todas as checagens em
# --pairs all (CVD dE 24,7; visao normal dE 33,6; contraste >= 3:1).
COR = {
    "ink": "#0b0b0b",
    "ink2": "#52514e",
    "muted": "#898781",
    "grid": "#e1e0d9",
    "axis": "#c3c2b7",
    "wash": "#f3f2ee",
    "surface": "#ffffff",
    "s1": "#2a78d6",
    "s2": "#eb6834",
}
FONTE_SANS = 'Inter, "Liberation Sans", "DejaVu Sans", system-ui, sans-serif'


# ---------------------------------------------------------------------------
# Utilitarios de leitura e formatacao
# ---------------------------------------------------------------------------


def rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def ler_json(p: Path):
    if not p.exists():
        return None
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def ler_csv(p: Path, **kw) -> pd.DataFrame | None:
    if not p.exists():
        return None
    return pd.read_csv(p, **kw)


def sha256(p: Path) -> str | None:
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def finito(x) -> bool:
    try:
        return x is not None and math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def br(x, nd: int = 3) -> str:
    """Numero no formato brasileiro (virgula decimal, ponto de milhar)."""
    if not finito(x):
        return "—"
    x = float(x)
    if abs(x) < 0.5 * 10 ** (-nd):
        x = 0.0  # evita "-0,0" vindo de ponto flutuante
    s = f"{x:,.{nd}f}"
    s = s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    if s.startswith("-"):
        s = "−" + s[1:]
    return s


def br_int(x) -> str:
    if not finito(x):
        return "—"
    return f"{int(round(float(x))):,}".replace(",", ".")


def br_pct(x, nd: int = 1) -> str:
    return "—" if not finito(x) else br(x, nd) + "%"


def br_p(p) -> str:
    if not finito(p):
        return "—"
    return "< 0,001" if float(p) < 0.001 else br(p, 3)


def br_mil(v: float) -> str:
    return f"R$ {br(v / 1000, 0)} mil" if float(v) % 1000 == 0 else f"R$ {br(v, 0)}"


def br_frac2(v: float) -> str:
    """Rotulo de potencia de 2 para eixo log: 1/4, 1/2, 1, 2, 4."""
    if v >= 1:
        return br(v, 0)
    return f"1/{int(round(1 / v))}"


def milesimos(s) -> np.ndarray:
    return np.rint(np.asarray(s, dtype=float) * 1000).astype("int64")


def faixa_pelo_valor(m: int, c_inf_m: int, c_sup_m: int, faixas: list[str]) -> str:
    """faixas = [baixa, media, alta] em ordem crescente de valor da bolsa."""
    if m <= c_inf_m:
        return faixas[0]
    if m <= c_sup_m:
        return faixas[1]
    return faixas[2]


def nome_quadro(q: str) -> str:
    m = re.fullmatch(r"c(\d+)_ch(\d+)", str(q))
    return f"Ciclo {m.group(1)}, chamada {m.group(2)}" if m else str(q)


def strip_ascii(s: str) -> str:
    import unicodedata

    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def git_info() -> tuple[str, bool]:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "indisponível", False
    try:
        sujo = bool(
            subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=no"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        sujo = False
    return commit, sujo


_CACHE_PRODUTOR: dict[str, str | None] = {}


def script_produtor(arquivo: Path, resumo: dict | None = None) -> str | None:
    """Script que grava `arquivo`.

    Usa o campo `script` do resumo JSON quando existe; senao procura, entre os
    scripts de `scripts/rdd_bolsa/`, a constante de saida (OUT_*, SAIDA_*,
    NOME_*) cujo valor e exatamente o nome do arquivo. Um script que apenas le
    o arquivo nao conta como produtor.
    """
    if isinstance(resumo, dict) and isinstance(resumo.get("script"), str):
        return resumo["script"]
    chave = arquivo.name
    if chave in _CACHE_PRODUTOR:
        return _CACHE_PRODUTOR[chave]
    padrao = re.compile(
        r"^\s*(OUT\w*|SAIDA\w*|NOME_\w*)\s*=.*[\"']" + re.escape(arquivo.name) + r"[\"']", re.M
    )
    achado = None
    for s in sorted((ROOT / "scripts" / "rdd_bolsa").glob("*.py")):
        if s.resolve() == ESTE_SCRIPT:
            continue
        if padrao.search(s.read_text(encoding="utf-8", errors="ignore")):
            achado = rel(s)
            break
    _CACHE_PRODUTOR[chave] = achado
    return achado


def commit_do_arquivo(p: Path) -> str | None:
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%h", "--", rel(p)], cwd=ROOT, capture_output=True,
                           text=True, check=True)
        return r.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def origem_html(p: Path, resumo: dict | None = None) -> str:
    """Descricao curta da origem de um arquivo de output/ para a linha de fonte."""
    prod = script_produtor(p, resumo)
    if prod:
        return f"gerado por <code>{esc(prod)}</code>"
    c = commit_do_arquivo(p)
    return f"documento versionado sem script produtor (commit {esc(c)})" if c else "origem não declarada"


def fonte_html(*arquivos: Path, extra: str = "") -> str:
    partes = []
    for a in arquivos:
        s = f"<code>{esc(rel(a))}</code>"
        s += f" ({origem_html(a)})" if a.parent == OUT_DIR else " (dado observado)"
        partes.append(s)
    txt = "; ".join(partes)
    if extra:
        txt += f". {extra}"
    return f'<div class="fonte">Fonte: {txt}. Gráfico desenhado por <code>{esc(rel(ESTE_SCRIPT))}</code>.</div>'


# ---------------------------------------------------------------------------
# Primitivas SVG
# ---------------------------------------------------------------------------


class Linear:
    def __init__(self, d0: float, d1: float, r0: float, r1: float):
        self.d0, self.d1, self.r0, self.r1 = d0, d1, r0, r1

    def __call__(self, v: float) -> float:
        return self.r0 + (v - self.d0) / (self.d1 - self.d0) * (self.r1 - self.r0)


def nice_ticks(lo: float, hi: float, n: int = 5, inteiro: bool = False) -> list[float]:
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / max(n, 1)
    mag = 10 ** math.floor(math.log10(raw))
    if inteiro:
        mag = max(mag, 1)
    step = mag
    for mult in ((1, 2, 5, 10) if inteiro else (1, 2, 2.5, 5, 10)):
        step = mult * mag
        if span / step <= n:
            break
    start = math.ceil(lo / step - 1e-9) * step
    out = []
    v = start
    while v <= hi + step * 1e-9:
        out.append(round(v, 10))
        v += step
    return out


def f2(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def t_svg(x, y, s, size=10.5, anchor="start", cor=None, peso=None, extra="") -> str:
    attrs = f'x="{f2(x)}" y="{f2(y)}" font-size="{size}" text-anchor="{anchor}" fill="{cor or COR["ink2"]}"'
    if peso:
        attrs += f' font-weight="{peso}"'
    return f"<text {attrs} {extra}>{esc(s)}</text>"


def l_svg(x1, y1, x2, y2, cor=None, w=1.0, extra="") -> str:
    return (
        f'<line x1="{f2(x1)}" y1="{f2(y1)}" x2="{f2(x2)}" y2="{f2(y2)}" '
        f'stroke="{cor or COR["grid"]}" stroke-width="{w}" {extra}/>'
    )


def svg_abrir(w: int, h: int, rotulo: str, estilo: str = "") -> str:
    st = f' style="{estilo}"' if estilo else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="{esc(rotulo)}"{st}>'
    )


def barra_arredondada(x, y_topo, w, y_base, r=2.0, cor=None, titulo="") -> str:
    """Barra vertical com cantos arredondados so no topo (base quadrada)."""
    h = y_base - y_topo
    if h <= 0:
        return ""
    r = min(r, w / 2, h)
    d = (
        f"M{f2(x)},{f2(y_base)} L{f2(x)},{f2(y_topo + r)} Q{f2(x)},{f2(y_topo)} {f2(x + r)},{f2(y_topo)} "
        f"L{f2(x + w - r)},{f2(y_topo)} Q{f2(x + w)},{f2(y_topo)} {f2(x + w)},{f2(y_topo + r)} "
        f"L{f2(x + w)},{f2(y_base)} Z"
    )
    tt = f"<title>{esc(titulo)}</title>" if titulo else ""
    return f'<path d="{d}" fill="{cor or COR["s1"]}">{tt}</path>'


def legenda_svg(itens: list[tuple[str, str, str]], x: float, y: float, size=10.5, vertical=False) -> str:
    """itens = [(tipo, cor, rotulo)], tipo em {'ponto','barra','linha','anel'}."""
    out = []
    cx = x
    for tipo, cor, rot in itens:
        if vertical and out:
            cx = x
            y += size * 1.5
        if tipo == "ponto":
            out.append(f'<circle cx="{f2(cx + 5)}" cy="{f2(y - 3.5)}" r="4.5" fill="{cor}"/>')
        elif tipo == "anel":
            out.append(
                f'<circle cx="{f2(cx + 5)}" cy="{f2(y - 3.5)}" r="3.8" fill="{cor}" '
                f'stroke="{COR["surface"]}" stroke-width="1.5"/>'
            )
        elif tipo == "barra":
            out.append(f'<rect x="{f2(cx)}" y="{f2(y - 7.5)}" width="14" height="8" rx="4" fill="{cor}"/>')
        elif tipo == "linha":
            out.append(l_svg(cx, y - 3.5, cx + 14, y - 3.5, cor=cor, w=2))
        out.append(t_svg(cx + 19, y, rot, size=size, cor=COR["ink2"]))
        cx += 19 + len(rot) * size * 0.56 + 18
    return "".join(out)


def caixa_pendente(titulo: str, arquivos: list[Path], detalhe: str = "") -> str:
    lista = "".join(
        f"<li><code>{esc(rel(a))}</code> — {'presente' if a.exists() else 'ausente'}</li>" for a in arquivos
    )
    det = f"<p>{detalhe}</p>" if detalhe else ""
    return (
        f'<div class="pendente"><p class="pend-tit"><span class="pill pill-pend">pendente</span> {esc(titulo)}</p>'
        f"<ul>{lista}</ul>{det}</div>"
    )


def tabela(cabecalho: list[tuple[str, str]], linhas: list[list[str]], classe: str = "", titulo: str = "",
           rodape: str = "") -> str:
    """cabecalho = [(rotulo, 'num'|'txt')]; linhas ja formatadas (HTML).

    Com `titulo`, devolve titulo + tabela + rodape num bloco; blocos curtos nao
    se partem entre paginas.
    """
    th = "".join(f'<th class="{c}">{r}</th>' for r, c in cabecalho)
    trs = []
    for ln in linhas:
        tds = "".join(f'<td class="{cabecalho[i][1]}">{v}</td>' for i, v in enumerate(ln))
        trs.append(f"<tr>{tds}</tr>")
    tab = f'<table class="{classe}"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'
    if not titulo and not rodape:
        return tab
    tt = titulo_tabela(titulo) if titulo else ""
    inteiro = " inteiro" if len(linhas) <= 16 else ""
    return f'<div class="bloco-tab{inteiro}">{tt}{tab}{rodape}</div>'


def notas_rodape(notas: list[str]) -> tuple[dict[str, str], str]:
    """Mapeia notas distintas em letras; devolve (nota -> letra, HTML da legenda)."""
    unicas = list(dict.fromkeys(n for n in notas if n))
    letras = {n: chr(ord("a") + i) for i, n in enumerate(unicas)}
    leg = "".join(f"<li><sup>{letras[n]}</sup> {esc(n)}</li>" for n in unicas)
    return letras, (f'<ul class="notas">{leg}</ul>' if leg else "")


def render_generico(obj, nivel: int = 0) -> str:
    """Renderiza JSON arbitrario como lista de definicoes legivel."""
    if isinstance(obj, dict):
        if not obj:
            return '<span class="muted">{}</span>'
        if nivel > 3:
            return f"<code>{esc(json.dumps(obj, ensure_ascii=False)[:400])}</code>"
        itens = "".join(
            f"<dt>{esc(str(k).replace('_', ' '))}</dt><dd>{render_generico(v, nivel + 1)}</dd>" for k, v in obj.items()
        )
        return f'<dl class="kv">{itens}</dl>'
    if isinstance(obj, list):
        if not obj:
            return '<span class="muted">nenhum</span>'
        if all(not isinstance(x, (dict, list)) for x in obj):
            curtos = [render_generico(x, nivel + 1) for x in obj]
            if len(obj) <= 6 and sum(len(str(x)) for x in obj) <= 60:
                return "; ".join(curtos)
            lis = "".join(f"<li>{render_generico(x, nivel + 1)}</li>" for x in obj[:20])
            mais = f'<li class="muted">… mais {len(obj) - 20}</li>' if len(obj) > 20 else ""
            return f"<ul>{lis}{mais}</ul>"
        if nivel >= 2:
            return f'<span class="muted">{len(obj)} itens (ver arquivo)</span>'
        lis = "".join(f"<li>{render_generico(x, nivel + 1)}</li>" for x in obj[:12])
        mais = f'<li class="muted">… mais {len(obj) - 12} (ver arquivo)</li>' if len(obj) > 12 else ""
        return f"<ol>{lis}{mais}</ol>"
    if isinstance(obj, bool):
        return "sim" if obj else "não"
    if obj is None:
        return "—"
    if isinstance(obj, float):
        return esc(f"{obj:.4g}".replace(".", ","))
    s = str(obj)
    if re.fullmatch(r"(scripts|output|data|docs)/[\w./\-]+", s) or s.startswith("python"):
        return f"<code>{esc(s)}</code>"
    return esc(s)


class Numerador:
    def __init__(self):
        self.fig = 0
        self.tab = 0

    def figura(self) -> int:
        self.fig += 1
        return self.fig

    def tabela(self) -> int:
        self.tab += 1
        return self.tab


NUM = Numerador()


def figura(titulo: str, svg: str, fonte: str, sub: str = "", nota: str = "") -> str:
    n = NUM.figura()
    s = f'<div class="fig-sub">{sub}</div>' if sub else ""
    nt = f'<div class="fig-nota">{nota}</div>' if nota else ""
    return (
        f'<figure class="fig"><div class="fig-titulo"><span class="fig-num">Figura {n}.</span> {titulo}</div>'
        f"{s}{svg}{nt}{fonte}</figure>"
    )


def titulo_tabela(txt: str) -> str:
    return f'<div class="tab-titulo"><span class="fig-num">Tabela {NUM.tabela()}.</span> {txt}</div>'


# ---------------------------------------------------------------------------
# Dados da regra (R1)
# ---------------------------------------------------------------------------


def carregar_regra():
    r1 = ler_json(R1_JSON)
    mat = ler_csv(MATRIZ)
    ivs = ler_csv(IVS_2010)
    if r1 is None or mat is None:
        raise SystemExit(f"Entradas do R1 ausentes: {rel(R1_JSON)} / {rel(MATRIZ)}")
    mat["tem_escore"] = mat["tem_escore"].astype(str).str.lower().eq("true")
    cortes = r1["running_variable"]["cutoffs"]
    c_inf = float(cortes["inferior"]["valor"])
    c_sup = float(cortes["superior"]["valor"])
    # Faixas em ordem crescente de valor anunciado, lidas da matriz.
    valores = mat.groupby("faixa_anunciada")["valor_anunciado_brl"].agg(lambda s: sorted(set(s)))
    if any(len(v) != 1 for v in valores):
        raise SystemExit("Mais de um valor anunciado por faixa na matriz; regra nao e funcao da faixa.")
    valor_faixa = {f: float(v[0]) for f, v in valores.items()}
    faixas = sorted(valor_faixa, key=valor_faixa.get)  # [baixa, media, alta]
    if len(faixas) != 3:
        raise SystemExit(f"Esperadas 3 faixas na matriz; encontradas {faixas}")
    if ivs is not None:
        ivs = ivs[["cod_ibge6", "ivs_2010"]].rename(columns={"cod_ibge6": "co_ibge"})
    return r1, mat, ivs, c_inf, c_sup, faixas, valor_faixa


# ---------------------------------------------------------------------------
# Figuras da secao 2
# ---------------------------------------------------------------------------


def fig_regra_degraus(mat, c_inf, c_sup, faixas, valor_faixa) -> tuple[str, int]:
    d = (
        mat[mat["tem_escore"]]
        .sort_values(["co_ibge", "quadro"])
        .drop_duplicates("co_ibge")
        .reset_index(drop=True)
    )
    n = len(d)
    W, H = 680, 270
    ml, mr, mt, mb = 74, 24, 26, 44
    s = d["ivs_admin"].to_numpy(float)
    v = d["valor_anunciado_brl"].to_numpy(float)
    x0 = math.floor(s.min() / 0.05) * 0.05
    x1 = math.ceil(s.max() / 0.05) * 0.05
    vals = [valor_faixa[f] for f in faixas]
    passo = vals[1] - vals[0]
    X = Linear(x0, x1, ml, W - mr)
    Y = Linear(vals[0] - passo * 0.55, vals[-1] + passo * 0.55, H - mb, mt)
    rng = np.random.default_rng(SEMENTE_JITTER)
    jit = rng.uniform(-1, 1, n) * passo * 0.28

    o = [svg_abrir(W, H, "Valor anunciado da bolsa contra o escore administrativo")]
    for vv in vals:
        o.append(l_svg(ml, Y(vv), W - mr, Y(vv), COR["grid"]))
        o.append(t_svg(ml - 8, Y(vv) + 3.5, br_mil(vv), anchor="end"))
    for tx in nice_ticks(x0, x1, 7):
        o.append(l_svg(X(tx), H - mb, X(tx), H - mb + 4, COR["axis"]))
        o.append(t_svg(X(tx), H - mb + 16, br(tx, 2), anchor="middle"))
    o.append(l_svg(ml, H - mb, W - mr, H - mb, COR["axis"]))
    o.append(t_svg((ml + W - mr) / 2, H - 6, "Escore administrativo de IVS (MS)", anchor="middle", cor=COR["ink2"]))
    # Cortes
    for c in (c_inf, c_sup):
        o.append(l_svg(X(c), mt - 4, X(c), H - mb, COR["axis"]))
        o.append(t_svg(X(c), mt - 9, br(c, 3), anchor="middle", cor=COR["ink"], peso=600))
    # Regra (degraus)
    pts = [
        (x0, vals[0]),
        (c_inf, vals[0]),
        (c_inf, vals[1]),
        (c_sup, vals[1]),
        (c_sup, vals[2]),
        (x1, vals[2]),
    ]
    path = " ".join(f"{'M' if i == 0 else 'L'}{f2(X(a))},{f2(Y(b))}" for i, (a, b) in enumerate(pts))
    o.append(f'<path d="{path}" fill="none" stroke="{COR["ink2"]}" stroke-width="2" stroke-linejoin="round"/>')
    # Pontos
    for i in range(n):
        tt = f"{d.at[i, 'co_ibge']}: escore {br(s[i])}, {d.at[i, 'faixa_anunciada']} ({br_mil(v[i])})"
        o.append(
            f'<circle cx="{f2(X(s[i]))}" cy="{f2(Y(v[i] + jit[i]))}" r="3" fill="{COR["s1"]}" '
            f'fill-opacity="0.55" stroke="{COR["surface"]}" stroke-width="0.6"><title>{esc(tt)}</title></circle>'
        )
    # Rotulos dos degraus
    for c, (va, vb) in ((c_inf, (vals[0], vals[1])), (c_sup, (vals[1], vals[2]))):
        o.append(t_svg(X(c) + 6, Y((va + vb) / 2) + 4, f"+{br_mil(vb - va)}", cor=COR["ink"], peso=600))
    # Rotulo de cada faixa onde a linha de grade esta livre de pontos: a mais
    # alta a esquerda, as outras duas a direita.
    for i, f in enumerate(faixas):
        if i == len(faixas) - 1:
            o.append(t_svg(ml + 4, Y(valor_faixa[f]) - 5, f.title(), size=10, cor=COR["muted"]))
        else:
            o.append(t_svg(W - mr, Y(valor_faixa[f]) - 5, f.title(), anchor="end", size=10, cor=COR["muted"]))
    o.append("</svg>")
    return "".join(o), n


def fig_ivs2010_vs_admin(mat, ivs, c_inf, c_sup, faixas):
    d = mat[mat["tem_escore"]].sort_values(["co_ibge", "quadro"]).drop_duplicates("co_ibge")
    d = d.merge(ivs, on="co_ibge", how="inner").reset_index(drop=True)
    ci, cs = int(round(c_inf * 1000)), int(round(c_sup * 1000))
    d["faixa_ivs2010"] = [faixa_pelo_valor(m, ci, cs, faixas) for m in milesimos(d["ivs_2010"])]
    d["concorda"] = d["faixa_ivs2010"].eq(d["faixa_anunciada"])
    n, n_conc = len(d), int(d["concorda"].sum())
    W, H = 470, 486
    ml, mr, mt, mb = 56, 18, 52, 46
    allv = np.concatenate([d["ivs_2010"].to_numpy(float), d["ivs_admin"].to_numpy(float)])
    lo = math.floor(allv.min() / 0.05) * 0.05
    hi = math.ceil(allv.max() / 0.05) * 0.05
    X = Linear(lo, hi, ml, W - mr)
    Y = Linear(lo, hi, H - mb, mt)
    o = [svg_abrir(W, H, "IVS 2010 contra escore administrativo", estilo="max-width:100mm;margin:0 auto")]
    for t in nice_ticks(lo, hi, 6):
        o.append(l_svg(X(t), mt, X(t), H - mb, COR["grid"]))
        o.append(l_svg(ml, Y(t), W - mr, Y(t), COR["grid"]))
        o.append(t_svg(X(t), H - mb + 15, br(t, 1), anchor="middle"))
        o.append(t_svg(ml - 6, Y(t) + 3.5, br(t, 1), anchor="end"))
    o.append(l_svg(ml, H - mb, W - mr, H - mb, COR["axis"]))
    o.append(l_svg(ml, mt, ml, H - mb, COR["axis"]))
    for c in (c_inf, c_sup):
        o.append(l_svg(X(c), mt, X(c), H - mb, COR["ink2"], 0.9))
        o.append(l_svg(ml, Y(c), W - mr, Y(c), COR["ink2"], 0.9))
    o.append(l_svg(X(lo), Y(lo), X(hi), Y(hi), COR["muted"], 1))
    o.append(t_svg(X(hi) - 4, Y(hi) + 12, "45°", anchor="end", size=9.5, cor=COR["muted"]))
    o.append(t_svg((ml + W - mr) / 2, H - 8, "IVS 2010 (Ipea, público)", anchor="middle"))
    o.append(
        t_svg(14, (mt + H - mb) / 2, "Escore administrativo (MS)", anchor="middle",
              extra=f'transform="rotate(-90 14 {f2((mt + H - mb) / 2)})"')
    )
    for flag, cor in ((True, COR["s1"]), (False, COR["s2"])):
        sub = d[d["concorda"] == flag]
        for _, r in sub.iterrows():
            tt = (f"{r['co_ibge']}: IVS 2010 {br(r['ivs_2010'])} ({r['faixa_ivs2010']}); "
                  f"escore {br(r['ivs_admin'])} ({r['faixa_anunciada']})")
            o.append(
                f'<circle cx="{f2(X(r["ivs_2010"]))}" cy="{f2(Y(r["ivs_admin"]))}" r="3.2" fill="{cor}" '
                f'fill-opacity="0.75" stroke="{COR["surface"]}" stroke-width="0.8"><title>{esc(tt)}</title></circle>'
            )
    o.append(
        legenda_svg(
            [
                ("ponto", COR["s1"], f"mesma faixa pelos dois ({br_int(n_conc)})"),
                ("ponto", COR["s2"], f"faixa diferente pelo IVS 2010 ({br_int(n - n_conc)})"),
            ],
            ml,
            14,
            size=10,
            vertical=True,
        )
    )
    o.append("</svg>")
    return "".join(o), n, n_conc


def dados_primeiro_estagio(mat, ivs, c_sup, faixa_topo):
    d = mat[mat["quadro"] == QUADRO_PRIMEIRO_ESTAGIO].drop_duplicates("co_ibge")
    if ivs is not None:
        d = d.merge(ivs, on="co_ibge", how="left")
    else:
        d = d.assign(ivs_2010=np.nan)
    topo = d["faixa_anunciada"].eq(faixa_topo).to_numpy()
    cs = int(round(c_sup * 1000))
    b = BIN_PRIMEIRO_ESTAGIO_MILESIMOS
    bordas = [cs + k * b for k in range(-N_BINS_POR_LADO, N_BINS_POR_LADO + 1)]
    linhas = []
    for var in ("ivs_admin", "ivs_2010"):
        vv = d[var].to_numpy(float)
        ok = np.isfinite(vv)
        m = np.where(ok, np.rint(np.where(ok, vv, 0) * 1000), -1).astype(int)
        for lo, hi in zip(bordas[:-1], bordas[1:]):
            sel = ok & (m > lo) & (m <= hi)
            nn = int(sel.sum())
            k = int((sel & topo).sum())
            linhas.append(
                {"var": var, "lo": lo / 1000, "hi": hi / 1000, "n": nn, "k": k, "pct": 100 * k / nn if nn else np.nan}
            )
    n_admin = int(np.isfinite(d["ivs_admin"].to_numpy(float)).sum())
    n_ivs = int(np.isfinite(d["ivs_2010"].to_numpy(float)).sum())
    return pd.DataFrame(linhas), len(d), n_admin, n_ivs


def fig_primeiro_estagio(pe: pd.DataFrame, c_sup: float, faixa_topo: str) -> str:
    W, H = 680, 250
    ml, mr, mt, mb = 56, 24, 34, 44
    lo, hi = pe["lo"].min(), pe["hi"].max()
    X = Linear(lo, hi, ml, W - mr)
    Y = Linear(0, 100, H - mb, mt)
    o = [svg_abrir(W, H, f"Percentual em {faixa_topo} por bin")]
    for t in (0, 25, 50, 75, 100):
        o.append(l_svg(ml, Y(t), W - mr, Y(t), COR["grid"]))
        o.append(t_svg(ml - 8, Y(t) + 3.5, f"{t}%", anchor="end"))
    bordas = sorted(set(pe["lo"]).union(pe["hi"]))
    for t in bordas:
        o.append(l_svg(X(t), H - mb, X(t), H - mb + 4, COR["axis"]))
        o.append(t_svg(X(t), H - mb + 16, br(t, 2), anchor="middle"))
    o.append(l_svg(ml, H - mb, W - mr, H - mb, COR["axis"]))
    o.append(l_svg(X(c_sup), mt - 6, X(c_sup), H - mb, COR["ink2"], 1))
    o.append(t_svg(X(c_sup), mt - 10, f"corte {br(c_sup, 3)}", anchor="middle", cor=COR["ink"], peso=600))
    o.append(t_svg((ml + W - mr) / 2, H - 6, "Bin da variável de corte (largura 0,020; o corte fica no bin à esquerda)",
                   anchor="middle"))
    series = [("ivs_admin", COR["s1"], "Escore administrativo"), ("ivs_2010", COR["s2"], "IVS 2010")]
    for var, cor, nome in series:
        sub = pe[pe["var"] == var]
        for lado in (sub[sub["hi"] <= c_sup + 1e-9], sub[sub["lo"] >= c_sup - 1e-9]):
            pts = [(X((r.lo + r.hi) / 2), Y(r.pct)) for r in lado.itertuples() if finito(r.pct)]
            if len(pts) > 1:
                dd = " ".join(f"{'M' if i == 0 else 'L'}{f2(a)},{f2(b)}" for i, (a, b) in enumerate(pts))
                o.append(f'<path d="{dd}" fill="none" stroke="{cor}" stroke-width="2" stroke-linejoin="round" '
                         f'stroke-linecap="round"/>')
        for r in sub.itertuples():
            if not finito(r.pct):
                continue
            tt = f"{nome}, ({br(r.lo)}; {br(r.hi)}]: {r.k}/{r.n} = {br_pct(r.pct)}"
            o.append(f'<circle cx="{f2(X((r.lo + r.hi) / 2))}" cy="{f2(Y(r.pct))}" r="4.5" fill="{cor}" '
                     f'stroke="{COR["surface"]}" stroke-width="2"><title>{esc(tt)}</title></circle>')
    o.append(legenda_svg([("ponto", c, nm) for _, c, nm in series], ml, 14, size=10.5))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Figuras de E1 e E2
# ---------------------------------------------------------------------------


def fig_e1_contagens(cont: pd.DataFrame, cortes: list[float], placebos: list[float], h_principal: float | None):
    cont = cont.copy()
    cont["m"] = milesimos(cont["s"])
    b = BIN_CONTAGENS_MILESIMOS
    ciclos = sorted(cont["ciclo"].unique(), key=lambda x: str(x))
    paineis = []
    ymax = 1
    for c in ciclos:
        sub = cont[cont["ciclo"] == c]
        presentes = set(sub["m"].tolist())
        k = np.ceil(sub["m"].to_numpy() / b).astype(int)
        g = sub.assign(k=k).groupby("k")["n_D"].sum()
        # so bins cobertos integralmente pelos mass points do arquivo
        bins = [(int(kk), int(vv)) for kk, vv in g.items()
                if all(mm in presentes for mm in range(kk * b - b + 1, kk * b + 1))]
        paineis.append((c, bins, int(sub["n_D"].sum())))
        if bins:
            ymax = max(ymax, max(v for _, v in bins))
    todos_k = [k for _, bins, _ in paineis for k, _ in bins]
    if not todos_k:
        return None
    x0 = (min(todos_k) - 1) * b / 1000
    x1 = max(todos_k) * b / 1000
    W = 680
    ml, mr = 46, 16
    PH = 150  # altura do painel (area de plotagem)
    topo_jan = 40  # faixa para colchetes das janelas
    gap = 34
    cab = 34  # titulo do painel + linha de rotulos dos cortes
    H = topo_jan + len(paineis) * (PH + gap + cab) + 14
    X = Linear(x0, x1, ml, W - mr)
    yt = nice_ticks(0, ymax * 1.08, 5, inteiro=True)
    ytop = max(yt[-1], ymax * 1.08)
    o = [svg_abrir(W, H, "Contagens de municipios com D_k = 1 por bin do escore")]
    # Colchetes das janelas principais (acima de tudo)
    if h_principal:
        # Colchete sob o rotulo, um por corte; janelas adjacentes ficam lado a
        # lado com um pequeno respiro entre elas.
        for c in cortes:
            a, z = X(c - h_principal) + 2, X(c + h_principal) - 2
            yy = 26
            o.append(l_svg(a, yy, z, yy, COR["ink2"], 1))
            o.append(l_svg(a, yy, a, yy + 5, COR["ink2"], 1))
            o.append(l_svg(z, yy, z, yy + 5, COR["ink2"], 1))
            o.append(t_svg((a + z) / 2, yy - 5, f"janela principal do corte {br(c, 3)} (h = {br(h_principal, 3)})",
                           size=9.5, anchor="middle"))
    y_cursor = topo_jan
    for c, bins, total in paineis:
        y_tit = y_cursor + 12
        rot = f"Ciclo {c}" if str(c).isdigit() else str(c)
        o.append(t_svg(ml, y_tit, f"{rot}: municípios com D = 1 por bin de 0,005 ({br_int(total)} no intervalo)",
                       cor=COR["ink"], peso=600, size=10.5))
        y_rot = y_tit + 16  # linha de rotulos dos cortes, acima da area de plotagem
        top = y_tit + cab - 8
        base = top + PH
        Y = Linear(0, ytop, base, top)
        for t in yt:
            o.append(l_svg(ml, Y(t), W - mr, Y(t), COR["grid"]))
            o.append(t_svg(ml - 6, Y(t) + 3.5, br_int(t), anchor="end", size=9.5))
        for pc in placebos:
            if x0 <= pc <= x1:
                o.append(l_svg(X(pc), y_rot + 3, X(pc), base, COR["axis"], 1))
                o.append(t_svg(X(pc), y_rot, f"placebo {br(pc, 3)}", size=8.5, cor=COR["muted"], anchor="middle"))
        bw = (X(x0 + b / 1000) - X(x0))
        for k, v in bins:
            lo_b = (k - 1) * b / 1000
            tt = f"({br(lo_b)}; {br(k * b / 1000)}]: {v}"
            o.append(barra_arredondada(X(lo_b) + 1, Y(v), bw - 2, base, r=2, cor=COR["s1"], titulo=tt))
        for cc in cortes:
            o.append(l_svg(X(cc), y_rot + 3, X(cc), base, COR["ink"], 1.2))
            o.append(t_svg(X(cc), y_rot, f"corte {br(cc, 3)}", anchor="middle", size=9.5, cor=COR["ink"], peso=600))
        o.append(l_svg(ml, base, W - mr, base, COR["axis"]))
        for t in nice_ticks(x0, x1, 8):
            o.append(l_svg(X(t), base, X(t), base + 4, COR["axis"]))
            o.append(t_svg(X(t), base + 15, br(t, 2), anchor="middle", size=9.5))
        y_cursor = base + gap
    o.append(t_svg((ml + W - mr) / 2, H - 6, "Escore administrativo de IVS (bins (a; b], o corte fica no bin à esquerda)",
                   anchor="middle"))
    o.append("</svg>")
    return "".join(o)


def rotulo_papel(p: str) -> str:
    low = strip_ascii(str(p).lower())
    mapa = [
        ("princip", "Principal"),
        ("exat", "Complemento exato"),
        ("sensib", "Sensibilidade"),
        ("placebo", "Placebos (cortes sem mudança de bolsa)"),
        ("replic", "Replicação"),
    ]
    for k, v in mapa:
        if k in low:
            return v
    return str(p)


ORDEM_PAPEL = ["princip", "replic", "exat", "sensib", "placebo"]


def ordem_papel(p: str) -> int:
    low = strip_ascii(str(p).lower())
    for i, k in enumerate(ORDEM_PAPEL):
        if k in low:
            return i
    return len(ORDEM_PAPEL)


def espec_legivel(s: str) -> str:
    t = str(s)
    # Sufixo hNNN = janela em milesimos (h050 -> h = 0,050).
    t = re.sub(r"h(\d{3})(?!\d)", lambda m: f"h = 0,{m.group(1)}", t)
    t = t.replace("_sem_mass_point_do_corte", ", sem o mass point do corte")
    t = t.replace("_", " ")
    t = re.sub(r"\bpoisson\b", "Poisson", t)
    t = t.replace(" h = ", ", h = ")
    return t


def fmt_corte(c) -> str:
    return br(float(c), 3) if finito(c) else str(c)


def fig_e1_forest(est: pd.DataFrame) -> str | None:
    d = est.copy()
    for col in ("rho", "ic_inf", "ic_sup"):
        d[col] = pd.to_numeric(d[col], errors="coerce")
    d = d[(d["rho"] > 0) & np.isfinite(d["rho"])]
    if d.empty:
        return None
    d["_ord"] = d["papel"].map(ordem_papel)
    d["_i"] = range(len(d))
    d = d.sort_values(["ciclo", "_ord", "_i"])
    los = d["ic_inf"].where(d["ic_inf"] > 0).dropna()
    his = d["ic_sup"].where(np.isfinite(d["ic_sup"])).dropna()
    lo_e = math.floor(math.log2(max(min(los.min() if len(los) else 0.5, d["rho"].min()), 1 / 16)))
    hi_e = math.ceil(math.log2(min(max(his.max() if len(his) else 2, d["rho"].max()), 16)))
    lo_e, hi_e = min(lo_e, -1), max(hi_e, 1)
    W = 680
    lab_w, val_w = 318, 104
    pl, pr = lab_w + 8, W - val_w
    X = Linear(lo_e, hi_e, pl, pr)
    lx = lambda v: X(math.log2(v))  # noqa: E731
    RH, GH = 15, 22
    linhas = []
    y = 26
    for ciclo, gc in d.groupby("ciclo", sort=False):
        for papel, gp in gc.groupby("papel", sort=False):
            linhas.append(("grupo", y, f"Ciclo {ciclo} · {rotulo_papel(papel)}", None))
            y += GH - 6
            for r in gp.itertuples():
                linhas.append(("linha", y, r, None))
                y += RH
            y += 6
    H = int(y + 34)
    o = [svg_abrir(W, H, "Razao de densidades com IC 95%")]
    top, base = 18, y - 2
    for e in range(lo_e, hi_e + 1):
        v = 2.0 ** e
        o.append(l_svg(lx(v), top, lx(v), base, COR["grid"]))
        o.append(t_svg(lx(v), base + 14, br_frac2(v), anchor="middle", size=9.5))
    o.append(l_svg(lx(1), top, lx(1), base, COR["ink2"], 1))
    o.append(l_svg(pl, base, pr, base, COR["axis"]))
    o.append(t_svg((pl + pr) / 2, base + 30, "ρ (escala log; 1 = sem diferença entre os lados do corte)",
                   anchor="middle", size=10))
    o.append(t_svg(W - 4, 12, "ρ [IC 95%]", anchor="end", size=9.5, cor=COR["muted"]))
    o.append(t_svg(4, 12, "Especificação", size=9.5, cor=COR["muted"]))
    for tipo, yy, r, _ in linhas:
        if tipo == "grupo":
            o.append(t_svg(4, yy + 4, r, size=10.5, cor=COR["ink"], peso=600))
            continue
        destaque = ordem_papel(r.papel) <= 1
        cor = COR["s1"] if destaque else COR["ink2"]
        rot = f"c = {fmt_corte(r.corte)} · {espec_legivel(r.especificacao).replace(', sem o ', ', sem ')}"
        maxc = int((lab_w - 14) / (9.5 * 0.5))
        rot_c = rot if len(rot) <= maxc else rot[: maxc - 1] + "…"
        o.append(t_svg(14, yy + 3.5, rot_c, size=9.5, cor=COR["ink2"]))
        if finito(r.ic_inf) and finito(r.ic_sup) and r.ic_inf > 0:
            a = lx(max(r.ic_inf, 2.0 ** lo_e))
            z = lx(min(r.ic_sup, 2.0 ** hi_e))
            o.append(l_svg(a, yy, z, yy, cor, 2, extra='stroke-linecap="round"'))
            if r.ic_inf < 2.0 ** lo_e:
                o.append(t_svg(a - 2, yy + 3.5, "◂", anchor="end", size=9, cor=cor))
            if r.ic_sup > 2.0 ** hi_e:
                o.append(t_svg(z + 2, yy + 3.5, "▸", size=9, cor=cor))
        tt = (f"ciclo {r.ciclo}, c = {fmt_corte(r.corte)}, {r.especificacao}: ρ = {br(r.rho, 2)} "
              f"[{br(r.ic_inf, 2)}; {br(r.ic_sup, 2)}], p = {br_p(r.p_valor)}")
        o.append(f'<circle cx="{f2(lx(min(max(r.rho, 2.0 ** lo_e), 2.0 ** hi_e)))}" cy="{f2(yy)}" r="4" fill="{cor}" '
                 f'stroke="{COR["surface"]}" stroke-width="2"><title>{esc(tt)}</title></circle>')
        o.append(t_svg(W - 4, yy + 3.5, f"{br(r.rho, 2)} [{br(r.ic_inf, 2)}; {br(r.ic_sup, 2)}]", anchor="end",
                       size=9.5, extra='font-variant-numeric="tabular-nums"'))
    o.append("</svg>")
    return "".join(o)


def fig_e2_intervalos(lim: pd.DataFrame, h_principal: float | None) -> str | None:
    d = lim.copy()
    for col in ("delta_min", "delta_max", "delta_ingenuo_viesado"):
        if col in d:
            d[col] = pd.to_numeric(d[col], errors="coerce")
    d = d[np.isfinite(d["delta_min"]) & np.isfinite(d["delta_max"])]
    if d.empty:
        return None
    cenarios = list(dict.fromkeys(d["cenario"].astype(str)))
    paleta = [COR["s1"], COR["s2"]]
    cor_cen = {c: paleta[i] if i < len(paleta) else COR["ink2"] for i, c in enumerate(cenarios)}
    vals = np.concatenate([d["delta_min"], d["delta_max"]])
    if "delta_ingenuo_viesado" in d:
        vals = np.concatenate([vals, d["delta_ingenuo_viesado"].dropna()])
    lo = min(math.floor(vals.min() / 0.2) * 0.2, 0)
    hi = max(math.ceil(vals.max() / 0.2) * 0.2, 0)
    W = 680
    lab_w = 210
    pl, pr = lab_w + 10, W - 18
    X = Linear(lo, hi, pl, pr)
    RH, GH = 15, 22
    y = 44
    linhas = []
    for (ciclo, corte), g in d.groupby(["ciclo", "corte"], sort=False):
        linhas.append(("grupo", y, f"Ciclo {ciclo} · corte {fmt_corte(corte)}"))
        y += GH - 6
        for r in g.itertuples():
            linhas.append(("linha", y, r))
            y += RH
        y += 6
    base = y - 2
    H = int(base + 36)
    o = [svg_abrir(W, H, "Limites de Delta por especificacao")]
    for t in nice_ticks(lo, hi, 8):
        o.append(l_svg(X(t), 32, X(t), base, COR["grid"]))
        o.append(t_svg(X(t), base + 14, br(t, 1), anchor="middle", size=9.5))
    o.append(l_svg(X(0), 32, X(0), base, COR["ink"], 1.2))
    o.append(l_svg(pl, base, pr, base, COR["axis"]))
    o.append(t_svg((pl + pr) / 2, base + 30, "Δ = P(D = 1 | acima do corte) − P(D = 1 | abaixo), limites exatos",
                   anchor="middle", size=10))
    itens = [("barra", cor_cen[c], c.replace("_", " ")) for c in cenarios]
    if "delta_ingenuo_viesado" in d:
        itens.append(("anel", COR["ink"], "ingênuo, só municípios com escore (viesado)"))
    o.append(legenda_svg(itens, 4, 14, size=10))
    for tipo, yy, r in linhas:
        if tipo == "grupo":
            o.append(t_svg(4, yy + 4, r, size=10.5, cor=COR["ink"], peso=600))
            continue
        hh = float(r.h) if finito(r.h) else None
        princ = h_principal is not None and hh is not None and abs(hh - h_principal) < 1e-9
        rot = f"h = {br(hh, 3)} · {str(r.cenario).replace('_', ' ')}" + (" (principal)" if princ else "")
        o.append(t_svg(14, yy + 3.5, rot, size=10, cor=COR["ink" if princ else "ink2"], peso=600 if princ else None))
        a, z = X(r.delta_min), X(r.delta_max)
        cor = cor_cen.get(str(r.cenario), COR["ink2"])
        tt = f"[{br(r.delta_min)}; {br(r.delta_max)}]"
        o.append(f'<rect x="{f2(a)}" y="{f2(yy - 4)}" width="{f2(max(z - a, 1))}" height="8" rx="4" fill="{cor}">'
                 f"<title>{esc(tt)}</title></rect>")
        v = getattr(r, "delta_ingenuo_viesado", None)
        if finito(v):
            o.append(f'<circle cx="{f2(X(v))}" cy="{f2(yy)}" r="3.6" fill="{COR["ink"]}" stroke="{COR["surface"]}" '
                     f'stroke-width="1.6"><title>ingênuo: {esc(br(v))}</title></circle>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Secoes
# ---------------------------------------------------------------------------


def secao_capa(commit, sujo, agora, prot, status_itens) -> str:
    meta = [
        ("Gerado em", agora.strftime("%d/%m/%Y %H:%M")),
        ("Commit", f"<code>{esc(commit)}</code>" + (" (árvore de trabalho com alterações não commitadas)" if sujo else "")),
        ("Script", f"<code>{esc(rel(ESTE_SCRIPT))}</code>"),
    ]
    if prot:
        meta.append(("Protocolo congelado em", esc(prot.get("data_congelamento", "—"))
                     + f" (<code>{esc(rel(PROTOCOLO))}</code>)"))
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in meta)
    st = "".join(
        f'<tr><td>{nome}</td><td><span class="pill {"pill-ok" if ok else "pill-pend"}">{esc(rot)}</span></td>'
        f"<td>{det}</td></tr>"
        for nome, ok, rot, det in status_itens
    )
    sumario = "".join(
        f"<li>{s}</li>"
        for s in [
            "A regra reconstruída",
            "Por que a falta de escore impede a RDD direta",
            "E1 — razão de densidades",
            "E2 — limites parciais",
            "E3 — RDD completa (status)",
            "Leitura e limites",
            "Apêndice — proveniência das entradas",
        ]
    )
    return f"""
<section class="capa">
  <div class="kicker">Programa Mais Médicos Especialistas · adicional de bolsa por faixa de IVS</div>
  <h1>{esc(TITULO)}</h1>
  <p class="lead">Relatório de trabalho para o grupo: regra reconstruída, estimações exploratórias E1 e E2 e
  status de E3. Todos os números e gráficos são lidos de <code>output/</code> por script versionado.</p>
  <dl class="meta">{dl}</dl>
  <div class="aviso"><strong>Aviso.</strong> E1 e E2 são <strong>exploratórios</strong>: E1 depende da premissa
  A1 (não testável com dados públicos) e E2 entrega apenas limites parciais. <strong>E3 aguarda o escore
  completo</strong> para todos os municípios da população. Nada neste relatório é efeito causal estabelecido;
  o contraste é o incentivo marginal anunciado de R$ 5 mil, não a participação no PMM-E.</div>
  <h3>Situação das entradas</h3>
  <table class="status"><thead><tr><th>Etapa</th><th>Status</th><th>Detalhe</th></tr></thead><tbody>{st}</tbody></table>
  <h3>Conteúdo</h3>
  <ol class="sumario">{sumario}</ol>
</section>
"""


def secao_regra(r1, mat, ivs, c_inf, c_sup, faixas, valor_faixa) -> str:
    o = ['<section class="quebra"><h2>1. A regra reconstruída</h2>']
    rv = r1["running_variable"]
    lado = rv.get("lado_do_corte_observado", {})
    o.append(
        f"<p>A faixa da bolsa anunciada em cada quadro de vagas é função do escore administrativo de IVS "
        f"publicado pelo Ministério da Saúde. Há dois cortes: <strong>{br(c_inf)}</strong> "
        f"({esc(rv['cutoffs']['inferior'].get('salto', ''))}) e <strong>{br(c_sup)}</strong> "
        f"({esc(rv['cutoffs']['superior'].get('salto', ''))}). O próprio corte pertence ao lado inferior.</p>"
        f'<p class="nota">Variável registrada no R1: {esc(rv.get("nome", ""))}. Safra: {esc(rv.get("safra", ""))}. '
        f'Precisão: {esc(rv.get("precisao", ""))}.</p>'
    )
    # Tabela por quadro, recomputada da matriz e conferida contra o JSON do R1.
    ci, cs = int(round(c_inf * 1000)), int(round(c_sup * 1000))
    linhas, divergencias = [], []
    for q, g in mat.groupby("quadro", sort=False):
        n = g["co_ibge"].nunique()
        cat = g[g["faixa_pela_categoria"].notna()]
        n_cat, rep_cat = len(cat), int(cat["faixa_pela_categoria"].eq(cat["faixa_anunciada"]).sum())
        e = g[g["tem_escore"]]
        n_esc = len(e)
        rep_esc = int(e["faixa_pelo_escore"].eq(e["faixa_anunciada"]).sum())
        recalc = sum(
            faixa_pelo_valor(m, ci, cs, faixas) == f for m, f in zip(milesimos(e["ivs_admin"]), e["faixa_anunciada"])
        )
        if recalc != rep_esc:
            divergencias.append(f"{q}: regra recalculada aqui reproduz {recalc}, matriz registra {rep_esc}")
        jq = r1.get("quadros", {}).get(q, {})
        if jq:
            if jq.get("municipios") != n or jq.get("regra_pelo_escore", {}).get("reproduzidos") != rep_esc:
                divergencias.append(f"{q}: matriz difere do JSON do R1")
        linhas.append([
            esc(nome_quadro(q)) + f' <span class="muted">({esc(q)})</span>',
            esc(jq.get("referencia", "—")),
            br_int(n),
            f"{br_int(rep_cat)} / {br_int(n_cat)}",
            f"{br_int(rep_esc)} / {br_int(n_esc)}",
            br_pct(100 * n_esc / n if n else np.nan),
        ])
    o.append(tabela(
        [("Quadro", "txt nowrap"), ("Referência", "txt"), ("Municípios", "num"),
         ("Reproduzidos pela categoria", "num"), ("Reproduzidos pelo escore", "num"), ("Cobertura do escore", "num")],
        linhas,
        titulo="Reprodução da faixa anunciada, por quadro de vagas",
    ))
    nota_div = (
        '<p class="alerta">Divergência na conferência: ' + "; ".join(esc(x) for x in divergencias) + "</p>"
        if divergencias
        else f"<p class=\"nota\">Conferência: a faixa recalculada por este script a partir do escore e dos cortes "
        f"({br(c_inf)}; {br(c_sup)}) coincide com a faixa anunciada em todos os municípios com escore, "
        f"e as contagens da matriz coincidem com <code>{esc(rel(R1_JSON))}</code>.</p>"
    )
    o.append(nota_div)
    o.append(f'<div class="fonte">Fonte: <code>{esc(rel(MATRIZ))}</code> ({origem_html(MATRIZ)}); referência dos '
             f"quadros em <code>{esc(rel(R1_JSON))}</code> ({origem_html(R1_JSON)}). Cobertura = municípios com "
             "escore ÷ municípios do quadro.</div>")
    if lado:
        o.append(tabela(
            [("Limite", "txt"), ("Escore", "num")],
            [[esc(k.replace("_", " ")), br(v)] for k, v in lado.items() if finito(v)],
            classe="estreita",
            titulo="Lado do corte observado nos dados",
        ))
        if lado.get("nota"):
            o.append(f'<p class="nota">{esc(lado["nota"])}</p>')

    svg, n = fig_regra_degraus(mat, c_inf, c_sup, faixas, valor_faixa)
    o.append(figura(
        "Valor mensal anunciado da bolsa contra o escore administrativo",
        svg,
        fonte_html(MATRIZ, extra="Um ponto por município com escore em algum dos quatro quadros"),
        sub=f"{br_int(n)} municípios com escore observado; linha = regra de dois cortes. Deslocamento vertical "
            "aleatório (semente fixa) apenas para separar pontos sobrepostos.",
    ))

    if ivs is not None:
        svg2, n2, nc2 = fig_ivs2010_vs_admin(mat, ivs, c_inf, c_sup, faixas)
        cmp_ = r1.get("comparacao_ivs_2010_publico", {})
        sub2 = (f"{br_int(n2)} municípios com escore e IVS 2010; {br_pct(100 * nc2 / n2)} cairiam na mesma faixa "
                f"pelo IVS 2010. Linhas escuras: cortes {br(c_inf)} e {br(c_sup)} nos dois eixos; diagonal: 45°.")
        nota2 = ""
        if cmp_:
            nota2 = (f"Comparação registrada no R1 (404 municípios da relação nominal): correlação "
                     f"{br(cmp_.get('correlacao'), 3)}; diferença escore − IVS 2010 média {br(cmp_.get('diferenca_media'), 4)}, "
                     f"desvio-padrão {br(cmp_.get('diferenca_dp'), 4)}, de {br(cmp_.get('diferenca_min'))} a "
                     f"{br(cmp_.get('diferenca_max'))}. Leitura do R1: {esc(cmp_.get('leitura', ''))}.")
        o.append(figura(
            "IVS 2010 público contra o escore administrativo",
            svg2,
            fonte_html(MATRIZ, IVS_2010),
            sub=sub2,
            nota=nota2,
        ))

        faixa_topo = faixas[-1]
        pe, n_q, n_adm, n_ivs = dados_primeiro_estagio(mat, ivs, c_sup, faixa_topo)
        svg3 = fig_primeiro_estagio(pe, c_sup, faixa_topo)
        o.append(figura(
            f"“Primeiro estágio”: % de municípios na {faixa_topo.title()} por bin, em torno do corte {br(c_sup)}",
            svg3,
            fonte_html(MATRIZ, IVS_2010, extra=f"Quadro {QUADRO_PRIMEIRO_ESTAGIO}"),
            sub=(f"{nome_quadro(QUADRO_PRIMEIRO_ESTAGIO)}: {br_int(n_q)} municípios. Escore administrativo: "
                 f"{br_int(n_adm)} com escore (cobertura selecionada pelo desfecho). IVS 2010: {br_int(n_ivs)} "
                 "com IVS 2010. Pelo escore o salto é de 0 a 100%; pelo IVS 2010 é parcial."),
        ))
        tl = []
        for (lo, hi), g in pe.groupby(["lo", "hi"]):
            a = g[g["var"] == "ivs_admin"].iloc[0]
            b_ = g[g["var"] == "ivs_2010"].iloc[0]
            tl.append([f"({br(lo)}; {br(hi)}]", f"{br_int(a.k)} / {br_int(a.n)}", br_pct(a.pct),
                       f"{br_int(b_.k)} / {br_int(b_.n)}", br_pct(b_.pct)])
        o.append(tabela(
            [("Bin", "txt"), ("Escore adm.: n", "num"), ("Escore adm.: %", "num"),
             ("IVS 2010: n", "num"), ("IVS 2010: %", "num")],
            tl,
            titulo=f"Primeiro estágio em números (municípios na {faixa_topo.title()} / municípios no bin)",
            rodape=f'<div class="fonte">Fonte: <code>{esc(rel(MATRIZ))}</code>; <code>{esc(rel(IVS_2010))}</code>. '
                   "Mesmos dados da figura anterior.</div>",
        ))
    else:
        o.append(caixa_pendente("IVS 2010 ausente: gráficos de comparação não gerados", [IVS_2010]))
    o.append("</section>")
    return "".join(o)


def secao_cobertura(r1, mat, faixas) -> str:
    o = ["<section><h2>2. Por que a falta de escore impede a RDD direta</h2>"]
    bl = r1.get("bloqueio", {})
    o.append(
        "<p>O escore contínuo só é publicado para municípios que aparecem na Relação Nominal de especialistas "
        "ativos, isto é, municípios que <em>já têm</em> especialista do programa. A presença de especialista é o "
        "próprio desfecho. Restringir a RDD aos municípios com escore condiciona a amostra no desfecho: abaixo e "
        "acima do corte, os municípios observados são selecionados de forma diferente, e a comparação deixa de "
        "identificar o salto. A categoria administrativa (que reproduz a faixa em 100% dos casos) existe para "
        "todos, mas é discreta e não serve de variável de corte.</p>"
    )
    linhas = []
    for q, g in mat.groupby("quadro", sort=False):
        cel = [esc(nome_quadro(q))]
        for f in reversed(faixas):
            gf = g[g["faixa_anunciada"] == f]
            n, k = len(gf), int(gf["tem_escore"].sum())
            cel.append(f"{br_int(k)} / {br_int(n)} ({br_pct(100 * k / n if n else np.nan)})")
        n, k = len(g), int(g["tem_escore"].sum())
        cel.append(f"{br_int(k)} / {br_int(n)} ({br_pct(100 * k / n if n else np.nan)})")
        linhas.append(cel)
    o.append(tabela(
        [("Quadro", "txt")] + [(f.title(), "num") for f in reversed(faixas)] + [("Total", "num")], linhas,
        titulo="Municípios com escore / municípios do quadro, por faixa anunciada",
        rodape=f'<div class="fonte">Fonte: <code>{esc(rel(MATRIZ))}</code> ({origem_html(MATRIZ)}). O ciclo 3 aparece '
               "só na reconstrução da regra; está fora das estimações (prospectivo e congelado).</div>",
    ))
    if bl:
        o.append(f'<p><strong>Bloqueio registrado no R1.</strong> {esc(bl.get("motivo", ""))}. '
                 f'<strong>O que destrava:</strong> {esc(bl.get("o_que_destrava", ""))}.</p>')
    o.append("<p>Por isso o protocolo congelado substitui a RDD direta por duas leituras exploratórias que usam "
             "só o que é observável: E1 (razão de densidades, sob a premissa A1) e E2 (limites parciais sem "
             "premissa sobre a localização dos municípios sem escore). A RDD completa (E3) fica condicionada à "
             "obtenção do escore para todos os municípios.</p></section>")
    return "".join(o)


def secao_e1(prot) -> str:
    o = ['<section class="quebra"><h2>3. E1 — razão de densidades</h2>']
    est, cont, res = ler_csv(E1_EST, dtype={"corte": str, "h": str}), ler_csv(E1_CONT), ler_json(E1_RES)
    p1 = (prot or {}).get("E1_densidade", {})
    o.append(
        "<p><strong>Ideia.</strong> Entre os municípios da população, só os que têm especialista do ciclo "
        "(D<sub>k</sub> = 1) aparecem com escore. Logo, a contagem de municípios com D<sub>k</sub> = 1 em cada "
        "mass point do escore é proporcional a P(D<sub>k</sub> = 1 | s) × densidade de s. Se a densidade do "
        "escore entre <em>todos</em> os municípios da população for contínua no corte (premissa A1), a razão das "
        "densidades laterais entre os municípios com D<sub>k</sub> = 1 é igual à razão das probabilidades "
        "ρ = P(D = 1 | c<sup>+</sup>) / P(D = 1 | c<sup>−</sup>).</p>"
    )
    if p1:
        o.append('<dl class="kv protocolo">'
                 f'<dt>Estimando</dt><dd>{esc(p1.get("estimando", ""))}</dd>'
                 f'<dt>Premissa A1</dt><dd>{esc(p1.get("premissa_A1", ""))}</dd>'
                 f'<dt>Estimador principal</dt><dd>{esc(p1.get("estimador_principal", ""))}</dd>'
                 f'<dt>Multiplicidade</dt><dd>{esc(p1.get("multiplicidade", ""))}</dd>'
                 f'<dt>Complemento exato</dt><dd>{esc(p1.get("complemento_exato", ""))}</dd>'
                 "</dl>"
                 f'<p class="nota">Texto do protocolo congelado (<code>{esc(rel(PROTOCOLO))}</code>).</p>')
    o.append(
        "<p><strong>O que A1 exige e por que pode falhar.</strong> A1 diz que, sem a bolsa, não haveria mais "
        "(ou menos) municípios da população logo acima do corte do que logo abaixo. Ela falha se o escore tiver "
        "sido manipulado para cruzar o corte ou se a seleção dos municípios para o quadro de vagas dependeu do "
        "lado do corte. Com o escore só para os cobertos, A1 não é testável com dados públicos; ρ ≠ 1 pode vir "
        "tanto de diferença em P(D = 1) quanto de descontinuidade na densidade.</p>"
    )
    if est is None:
        o.append(caixa_pendente("E1 ainda não produzido", [E1_EST, E1_CONT, E1_RES]))
        o.append("</section>")
        return "".join(o)

    for col in ("rho", "ic_inf", "ic_sup", "p_valor", "p_holm", "n_esq", "n_dir"):
        if col in est:
            est[col] = pd.to_numeric(est[col], errors="coerce")
    est["_ord"] = est["papel"].map(ordem_papel)
    est["_i"] = range(len(est))
    est_ord = est.sort_values(["ciclo", "_ord", "_i"])

    # Populacoes (do resumo)
    if res and isinstance(res.get("populacoes"), dict):
        lp = []
        for k, v in res["populacoes"].items():
            if not isinstance(v, dict):
                continue
            lp.append([esc(k), esc(", ".join(v.get("quadros", []))), br_int(v.get("municipios")),
                       br_int(v.get("municipios_com_escore")), br_int(v.get("municipios_D1")),
                       br_int(v.get("municipios_com_ciclo_k_fora_de_P_k"))])
        if lp:
            o.append(tabela(
                [("População", "txt"), ("Quadros", "txt"), ("Municípios", "num"), ("Com escore", "num"),
                 ("Com D = 1", "num"), ("D = 1 fora da população", "num")], lp,
                titulo="Populações de E1",
                rodape=f'<div class="fonte">Fonte: <code>{esc(rel(E1_RES))}</code> ({origem_html(E1_RES, res)}). '
                       "“Com D = 1” = municípios com especialista ativo do ciclo k na relação nominal de 09/10/2026; "
                       "“fora da população” não entram em E1.</div>",
            ))

    # Leitura automatica das linhas principais
    princ = est_ord[est_ord["_ord"] == 0]
    if not princ.empty:
        itens = []
        for r in princ.itertuples():
            inclui = finito(r.ic_inf) and finito(r.ic_sup) and r.ic_inf <= 1 <= r.ic_sup
            itens.append(
                f"<li>Ciclo {esc(r.ciclo)}, corte {fmt_corte(r.corte)}: ρ = <strong>{br(r.rho, 2)}</strong> "
                f"(IC 95% {br(r.ic_inf, 2)} a {br(r.ic_sup, 2)}; p = {br_p(r.p_valor)}; p de Holm = {br_p(r.p_holm)}); "
                f"{br_int(r.n_esq)} municípios com D = 1 abaixo e {br_int(r.n_dir)} acima. "
                f"O intervalo {'inclui' if inclui else 'exclui'} 1.</li>"
            )
        n_tot = int((np.isfinite(est["ic_inf"]) & np.isfinite(est["ic_sup"])).sum())
        n_exc = int(((est["ic_inf"] > 1) | (est["ic_sup"] < 1)).sum())
        o.append("<h3>Resultado principal (ciclo 1)</h3><ul class=\"leitura\">" + "".join(itens) + "</ul>")
        o.append(f"<p>Em {br_int(n_tot)} especificações com intervalo, {br_int(n_exc)} excluem ρ = 1. "
                 "Leitura: exploratória e condicional a A1; um intervalo que inclui 1 não demonstra ausência de "
                 "diferença, apenas que a amostra não distingue ρ de 1 com essa precisão.</p>")

    forest = fig_e1_forest(est)
    if forest:
        o.append(figura("Razão de densidades ρ por especificação, com IC 95%", forest,
                        fonte_html(E1_EST, extra="Em azul, as estimativas principal e de replicação; em cinza, as demais"),
                        sub="Todas as especificações do protocolo, relatadas independentemente do resultado."))

    if cont is not None:
        cortes = sorted({float(c) for c in est.loc[est["_ord"] <= 1, "corte"]})
        placebos = sorted({float(c) for c in est.loc[est["papel"].astype(str).str.contains("placebo"), "corte"]})
        hp = est.loc[est["_ord"] == 0, "h"]
        h_principal = float(hp.iloc[0]) if len(hp) else None
        svg = fig_e1_contagens(cont, cortes, placebos, h_principal)
        if svg:
            o.append(figura("Contagens de municípios com D = 1 por bin do escore, ciclos 1 e 2", svg,
                            fonte_html(E1_CONT, extra="Mass points de 0,001 somados em bins de 0,005"),
                            sub="Linhas escuras: cortes reais. Linhas claras: cortes placebo. Colchetes no topo: "
                                "janelas do estimador principal."))
    else:
        o.append(caixa_pendente("Contagens por mass point ausentes", [E1_CONT]))

    # Tabelas por papel; notas longas viram notas de rodape com letra.
    cab = [("Ciclo", "num"), ("Corte", "num"), ("Especificação", "txt"), ("h", "num"), ("n esq.", "num"),
           ("n dir.", "num"), ("ρ", "num"), ("IC 95%", "num"), ("p", "num"), ("p Holm", "num"), ("Nota", "txt")]
    o.append("<h3>Todas as especificações</h3>")
    for papel, g in est_ord.groupby("papel", sort=False):
        notas = [str(r.nota) if isinstance(r.nota, str) else "" for r in g.itertuples()]
        letras, leg = notas_rodape(notas)
        linhas = []
        for r, nota in zip(g.itertuples(), notas):
            espec = re.sub(r",? ?h = 0,\d{3}", "", espec_legivel(r.especificacao)).strip(" ,")
            linhas.append([esc(r.ciclo), fmt_corte(r.corte), esc(espec),
                           fmt_corte(r.h), br_int(r.n_esq), br_int(r.n_dir), br(r.rho, 3),
                           f"{br(r.ic_inf, 3)} – {br(r.ic_sup, 3)}", br_p(r.p_valor), br_p(r.p_holm),
                           f"<sup>{letras[nota]}</sup>" if nota else ""])
        o.append(tabela(cab, linhas, classe="compacta", titulo=f"E1 — {rotulo_papel(papel).lower()}", rodape=leg))
    o.append(f'<div class="fonte">Fonte: <code>{esc(rel(E1_EST))}</code> ({origem_html(E1_EST, res)}). '
             "n esq. / n dir. = municípios com D = 1 na janela abaixo (c − h; c] / acima (c; c + h]. p de Holm só nos "
             "dois cortes principais do ciclo 1.</div>")

    if res:
        meta = {k: res[k] for k in ("status", "data_execucao") if k in res}
        if isinstance(res.get("metodo"), dict):
            for k in ("unidade", "janela", "existencia_mle", "exato", "papel"):
                if k in res["metodo"]:
                    meta[f"método: {k}"] = res["metodo"][k]
        o.append('<div class="bloco-tab"><h3>Registro do resumo de E1</h3>' + render_generico(meta)
                 + f'<div class="fonte">Fonte: <code>{esc(rel(E1_RES))}</code> ({origem_html(E1_RES, res)}). '
                 "Estimando, premissa, contraste e linguagem estão na seção 6.</div></div>")
    o.append("</section>")
    return "".join(o)


def secao_e2(prot) -> str:
    o = ['<section class="quebra"><h2>4. E2 — limites parciais</h2>']
    lim, res = ler_csv(E2_LIM, dtype={"corte": str}), ler_json(E2_RES)
    p2 = (prot or {}).get("E2_limites", {})
    o.append(
        "<p><strong>Ideia.</strong> Em vez de supor A1, E2 pergunta: dado que os municípios sem escore têm "
        "D = 0 e estão em algum ponto do intervalo da sua faixa anunciada, quais são os valores mínimo e máximo "
        "possíveis para a diferença de proporções Δ entre as janelas logo acima e logo abaixo do corte? Se o "
        "intervalo [Δ<sub>mín</sub>; Δ<sub>máx</sub>] inclui zero, os dados não identificam nem o sinal.</p>"
    )
    if p2:
        o.append('<dl class="kv protocolo">'
                 f'<dt>Estimando</dt><dd>{esc(p2.get("estimando", ""))}</dd>'
                 f'<dt>Cenário pior caso</dt><dd>{esc(p2.get("cenario_pior_caso", ""))}</dd>'
                 f'<dt>Cenário informado</dt><dd>{esc(p2.get("cenario_informado", ""))}</dd>'
                 f'<dt>Método</dt><dd>{esc(p2.get("metodo", ""))}</dd>'
                 f'<dt>Janelas</dt><dd>{esc("; ".join(p2.get("janelas", [])))}</dd>'
                 "</dl>"
                 f'<p class="nota">Texto do protocolo congelado (<code>{esc(rel(PROTOCOLO))}</code>).</p>')
    if lim is None:
        o.append(caixa_pendente("E2 ainda não produzido", [E2_LIM, E2_RES]))
        o.append("</section>")
        return "".join(o)
    for col in lim.columns:
        if col not in ("cenario", "corte"):
            lim[col] = pd.to_numeric(lim[col], errors="coerce")
    h_principal = None
    for j in p2.get("janelas", []):
        m = re.search(r"h\s*=\s*([0-9]+[.,][0-9]+)\s*\(principal\)", j)
        if m:
            h_principal = float(m.group(1).replace(",", "."))

    # Leitura automatica
    ok = lim[np.isfinite(lim["delta_min"]) & np.isfinite(lim["delta_max"])]
    excl = ok[(ok["delta_min"] > 0) | (ok["delta_max"] < 0)]
    itens = []
    if h_principal is not None:
        pr = ok[np.isclose(ok["h"], h_principal)]
        for r in pr.itertuples():
            inclui = r.delta_min <= 0 <= r.delta_max
            itens.append(f"<li>Ciclo {esc(int(r.ciclo) if finito(r.ciclo) else r.ciclo)}, corte {fmt_corte(r.corte)}, "
                         f"{esc(str(r.cenario).replace('_', ' '))}: Δ entre <strong>{br(r.delta_min)}</strong> e "
                         f"<strong>{br(r.delta_max)}</strong> ({'inclui' if inclui else 'exclui'} zero).</li>")
    o.append(f"<h3>Resultado na janela principal (h = {br(h_principal, 3) if h_principal else '—'})</h3>"
             f'<ul class="leitura">{"".join(itens)}</ul>')
    txt = f"<p>Dos {br_int(len(ok))} intervalos, {br_int(len(ok) - len(excl))} incluem zero."
    if len(excl):
        desc = "; ".join(
            f"ciclo {int(r.ciclo)}, corte {fmt_corte(r.corte)}, h = {br(r.h, 3)}, {str(r.cenario).replace('_', ' ')} "
            f"[{br(r.delta_min)}; {br(r.delta_max)}]"
            for r in excl.itertuples()
        )
        so_fora_principal = h_principal is not None and not np.isclose(excl["h"], h_principal).any()
        so_informado = excl["cenario"].astype(str).str.contains("inform").all()
        txt += f" Excluem zero: {esc(desc)}."
        razoes = []
        if so_fora_principal:
            razoes.append(f"estão fora da janela principal (h = {br(h_principal, 3)})")
        if so_informado:
            razoes.append("dependem da premissa do cenário informado")
        if razoes:
            um = len(excl) == 1
            razoes = [r.replace("estão", "está").replace("dependem", "depende") if um else r for r in razoes]
            txt += ((" Esse caso " if um else " Esses casos ") + " e ".join(razoes)
                    + ("; fica relatado, mas não substitui" if um else "; ficam relatados, mas não substituem")
                    + " a especificação principal fixada no protocolo.")
    txt += (" Os limites são de identificação na amostra observada e não incorporam incerteza amostral. "
            "A estimativa ingênua usa só municípios com escore e é viesada pela seleção; serve apenas de referência.</p>")
    o.append(txt)

    svg = fig_e2_intervalos(lim, h_principal)
    if svg:
        o.append(figura("Limites de Δ por ciclo, corte, janela e cenário", svg,
                        fonte_html(E2_LIM, extra="Barra = [Δ mín; Δ máx]; ponto = estimativa ingênua (viesada)"),
                        sub="Linha vertical escura em Δ = 0. Barra que cruza o zero: sinal não identificado."))
    # Tabelas: (a) contagens por janela; (b) proporcoes e limites. Colunas
    # desconhecidas vao para (b) com o nome original.
    tem = set(lim.columns)
    chave = [("Ciclo", "num"), ("Corte", "num"), ("h", "num"), ("Cenário", "txt")]

    def chave_linha(r):
        return [esc(int(r["ciclo"]) if finito(r["ciclo"]) else r["ciclo"]), fmt_corte(r["corte"]), br(r["h"], 3),
                esc(str(r["cenario"]).replace("_", " "))]

    pares = [("n_conhecidos_inf", "n_conhecidos_sup", "Com escore"),
             ("nD_inf", "nD_sup", "Com D = 1"),
             ("n_sem_escore_certos_inf", "n_sem_escore_certos_sup", "Sem escore, certamente na janela"),
             ("n_sem_escore_possiveis_inf", "n_sem_escore_possiveis_sup", "Sem escore, possivelmente na janela")]
    intervalos = [("p_inf_min", "p_inf_max", "P(D = 1) abaixo"),
                  ("p_sup_min", "p_sup_max", "P(D = 1) acima"),
                  ("delta_min", "delta_max", "Δ")]
    usados = {"ciclo", "corte", "h", "cenario"}
    pares = [p for p in pares if p[0] in tem and p[1] in tem]
    intervalos = [p for p in intervalos if p[0] in tem and p[1] in tem]
    for a, b, _ in pares + intervalos:
        usados |= {a, b}
    if "delta_ingenuo_viesado" in tem:
        usados.add("delta_ingenuo_viesado")
    resto = [c for c in lim.columns if c not in usados]
    fonte_e2 = (f'<div class="fonte">Fonte: <code>{esc(rel(E2_LIM))}</code> ({origem_html(E2_LIM, res)}). '
                "“abaixo / acima” = janelas (c − h; c] / (c; c + h].</div>")
    if pares:
        cab_a = chave + [(f"{nm}<br><span class=\"muted\">abaixo / acima</span>", "num") for _, _, nm in pares]
        linhas_a = [chave_linha(r) + [f"{br_int(r[a])} / {br_int(r[b])}" for a, b, _ in pares]
                    for _, r in lim.iterrows()]
        o.append(tabela(cab_a, linhas_a, classe="compacta", titulo="E2 — municípios por janela", rodape=fonte_e2))
    cab_b = chave + [(f"{nm}<br><span class=\"muted\">[mín; máx]</span>", "num") for _, _, nm in intervalos]
    if "delta_ingenuo_viesado" in tem:
        cab_b.append(("Δ ingênuo<br><span class=\"muted\">(viesado)</span>", "num"))
    cab_b += [(esc(c.replace("_", " ")), "num") for c in resto]
    linhas_b = []
    for _, r in lim.iterrows():
        ln = chave_linha(r) + [f"{br(r[a])}; {br(r[b])}" for a, b, _ in intervalos]
        if "delta_ingenuo_viesado" in tem:
            ln.append(br(r["delta_ingenuo_viesado"]))
        ln += [br(r[c]) if finito(r[c]) else esc(r[c]) for c in resto]
        linhas_b.append(ln)
    o.append(tabela(cab_b, linhas_b, classe="compacta", titulo="E2 — proporções e limites de Δ", rodape=fonte_e2))

    if res:
        if isinstance(res.get("populacoes"), dict):
            lp = []
            for k, v in res["populacoes"].items():
                if not isinstance(v, dict):
                    continue
                for f, vf in (v.get("por_faixa_anunciada") or {}).items():
                    lp.append([esc(v.get("rotulo", k)), esc(f.title()), br_int(vf.get("municipios")),
                               br_int(vf.get("com_escore")), br_int(vf.get("com_D_igual_1"))])
            if lp:
                o.append(tabela(
                    [("População", "txt"), ("Faixa anunciada", "txt"), ("Municípios", "num"), ("Com escore", "num"),
                     ("Com D = 1", "num")], lp, classe="estreita",
                    titulo="Populações de E2 por faixa anunciada",
                    rodape=f'<div class="fonte">Fonte: <code>{esc(rel(E2_RES))}</code> ({origem_html(E2_RES, res)}).</div>',
                ))
        meta = {k: res[k] for k in ("status", "data_execucao", "referencia_viesada") if k in res}
        if isinstance(res.get("cenarios"), dict):
            # A definicao de cada cenario ja esta no quadro do protocolo; aqui
            # ficam so os parametros numericos do cenario informado.
            meta["cenário informado"] = {k: v for k, v in res["cenarios"].items()
                                         if k in ("dmin", "dmax", "dmin_dmax_base")}
        if isinstance(res.get("metodo_extremos"), dict):
            meta["método dos extremos"] = {k: v for k, v in res["metodo_extremos"].items()
                                           if k in ("exato", "exclusividade_restringe_algum_extremo")}
        o.append('<div class="bloco-tab inteiro"><h3>Registro do resumo de E2</h3>' + render_generico(meta)
                 + f'<div class="fonte">Fonte: <code>{esc(rel(E2_RES))}</code> ({origem_html(E2_RES, res)}). '
                 "Linguagem e regra de relato estão na seção 6.</div></div>")
    o.append("</section>")
    return "".join(o)


def secao_e3(prot) -> str:
    o = ["<section><h2>5. E3 — RDD completa (status)</h2>"]
    st = ler_json(E3_STATUS)
    p3 = (prot or {}).get("E3_rdd_completa", {})
    if st is None:
        o.append(caixa_pendente("E3_status.json ainda não produzido", [E3_STATUS]))
    elif not isinstance(st, dict):
        o.append(render_generico(st))
    else:
        st = dict(st)
        status = st.pop("status", None)
        if status:
            pill = "pill-ok" if strip_ascii(str(status).lower()).startswith(("conclu", "estimad", "ok")) else "pill-pend"
            o.append(f'<p><span class="pill {pill}">{esc(str(status).replace("_", " "))}</span></p>')
        # Campos principais, na ordem de leitura.
        principais = [("motivo", "Motivo"), ("o_que_destrava", "O que destrava"), ("como_rodar", "Como rodar")]
        dl = []
        for k, rot in principais:
            if k in st:
                v = st.pop(k)
                vv = f'<pre class="cmd">{esc(v)}</pre>' if k == "como_rodar" else render_generico(v)
                dl.append(f"<dt>{rot}</dt><dd>{vv}</dd>")
        cond = (st.get("protocolo") or {}).get("condicao") if isinstance(st.get("protocolo"), dict) else None
        if cond:
            dl.append(f"<dt>Condição do protocolo</dt><dd>{esc(cond)}</dd>")
        for k, rot in (("outcomes_abertos", "Desfechos abertos"), ("outcomes_lidos", "Desfechos lidos")):
            if k in st:
                dl.append(f"<dt>{rot}</dt><dd>{render_generico(st.pop(k))}</dd>")
        if dl:
            o.append('<dl class="kv destaque">' + "".join(dl) + "</dl>")
        cob = st.pop("cobertura_do_escore", None)
        if isinstance(cob, dict):
            faixas_cob = sorted({f for v in cob.values() if isinstance(v, dict)
                                 for f in (v.get("por_faixa_anunciada") or {})})
            linhas = []
            for k, v in cob.items():
                if not isinstance(v, dict):
                    continue
                pf = v.get("por_faixa_anunciada") or {}
                linhas.append(
                    [esc(k), esc(v.get("papel", "")), br_int(v.get("municipios")), br_int(v.get("com_escore")),
                     br_pct(v.get("pct"))]
                    + [br_pct((pf.get(f) or {}).get("pct")) for f in faixas_cob]
                    + ["sim" if v.get("completa") else "não"]
                )
            o.append(tabela(
                [("População", "txt"), ("Papel", "txt"), ("Municípios", "num"), ("Com escore", "num"),
                 ("Cobertura", "num")] + [(f"Cobertura {esc(f.title())}", "num") for f in faixas_cob]
                + [("Completa", "txt")],
                linhas, titulo="Cobertura do escore exigida por E3",
            ))
        ctx = {}
        for k in ("cortes", "lado_do_corte", "janelas", "contraste", "etapa", "natureza_dos_dados",
                  "saidas_anteriores_removidas"):
            if k in st:
                ctx[k] = st.pop(k)
        for k in ("protocolo", "escore", "populacoes"):
            st.pop(k, None)  # proveniencia (hashes): registrada no proprio arquivo
        ctx.update(st)
        if ctx:
            o.append("<h3>Parâmetros registrados</h3>" + render_generico(ctx))
        o.append(f'<div class="fonte">Fonte: <code>{esc(rel(E3_STATUS))}</code> ({origem_html(E3_STATUS)}). Hashes do '
                 "protocolo, do escore e dos quadros estão registrados no próprio arquivo.</div>")
    if p3:
        o.append('<div class="bloco-tab inteiro"><h3>O que o protocolo prevê para E3</h3>' + render_generico(p3)
                 + f'<p class="nota">Do protocolo congelado (<code>{esc(rel(PROTOCOLO))}</code>).</p></div>')
    o.append("</section>")
    return "".join(o)


def secao_leitura(prot, r1) -> str:
    o = ['<section class="quebra"><h2>6. Leitura e limites</h2>']
    if not prot:
        o.append(caixa_pendente("Protocolo ausente", [PROTOCOLO]))
        o.append("</section>")
        return "".join(o)
    ling = prot.get("linguagem", {})
    cortes_r1 = ((r1 or {}).get("running_variable") or {}).get("cutoffs") or {}
    saltos = "; ".join(
        f"{br(v.get('valor'))}: {esc(v.get('salto', ''))}" for v in cortes_r1.values() if isinstance(v, dict)
    )
    pop = prot.get("populacoes", {})
    out = prot.get("outcome", {})
    rv = prot.get("running_variable", {})
    aut = prot.get("autorizacao_autor", {})
    blocos = [
        ("Estimando / contraste",
         "Diferença de <strong>+R$ 5 mil anunciados</strong> por mês em cada corte"
         + (f" ({saltos})" if saltos else "")
         + ". Pode ser um <strong>pacote</strong> se outra regra mudar no mesmo corte. Não identifica participação "
         f"no PMM-E nem o efeito total do Agora Tem Especialistas. <span class=\"muted\">Protocolo:</span> "
         f"“{esc(ling.get('contraste', ''))}”."),
        ("População", "<ul>" + "".join(f"<li><strong>{esc(k)}</strong>: {esc(v)}</li>" for k, v in pop.items()) + "</ul>"),
        ("Desfecho",
         f"{esc(out.get('D_k', ''))}<br><span class=\"muted\">Leitura:</span> {esc(out.get('leitura', ''))}<br>"
         f"<span class=\"muted\">Propriedade:</span> {esc(out.get('propriedade', ''))}"),
        ("Variável de corte",
         f"{esc(rv.get('fonte', ''))}; lado: {esc(rv.get('lado', ''))}. Troca autorizada pelo autor em "
         f"{esc(aut.get('data', '—'))}: {esc(aut.get('troca_running_variable', ''))} — "
         f"{esc(aut.get('justificativa', ''))}. Escopo autorizado: {esc(aut.get('escopo_autorizado', ''))}."),
        ("Premissas",
         "<ul>"
         f"<li><strong>E1, A1:</strong> {esc(prot.get('E1_densidade', {}).get('premissa_A1', ''))}</li>"
         f"<li><strong>E2, cenário informado:</strong> {esc(prot.get('E2_limites', {}).get('cenario_informado', ''))}</li>"
         f"<li><strong>E3:</strong> {esc(prot.get('E3_rdd_completa', {}).get('condicao', ''))}</li>"
         "</ul>"),
        ("Pré-registro e exposição prévia a desfechos",
         f"Pré-registro: {'sim' if prot.get('pre_registro') else 'não'}; protocolo congelado em "
         f"{esc(prot.get('data_congelamento', '—'))}, antes da estimação. Exposição prévia registrada:"
         "<ul>" + "".join(f"<li>{esc(x)}</li>" for x in prot.get("exposicao_previa_a_outcomes", [])) + "</ul>"),
        ("Linguagem",
         f"{esc(ling.get('E1_E2', ''))}. Resultados de E1 e E2 são descritivos/exploratórios: usar “compatível "
         "com”, “associado a”, “os dados não distinguem”; não usar “efeito”, “causou” ou “aumentou”."),
        ("Regra de relato", esc(prot.get("regra_de_relato", ""))),
    ]
    o.append('<dl class="leitura-dl">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in blocos) + "</dl>")
    bl = r1.get("bloqueios_resultantes") if r1 else None
    if bl:
        o.append("<p><strong>Portões seguintes (registro do R1):</strong> "
                 + "; ".join(f"{esc(k.upper())}: {esc(v)}" for k, v in bl.items()) + ".</p>")
    o.append(f'<div class="fonte">Fonte: <code>{esc(rel(PROTOCOLO))}</code>; <code>{esc(rel(R1_JSON))}</code>.</div>')
    o.append("</section>")
    return "".join(o)


def secao_proveniencia() -> str:
    entradas = [R1_JSON, MATRIZ, PROTOCOLO, IVS_2010, E1_EST, E1_CONT, E1_RES, E2_LIM, E2_RES, E3_STATUS]
    resumos = {E1_EST: ler_json(E1_RES), E1_CONT: ler_json(E1_RES), E1_RES: ler_json(E1_RES),
               E2_LIM: ler_json(E2_RES), E2_RES: ler_json(E2_RES), E3_STATUS: ler_json(E3_STATUS)}
    linhas = []
    for p in entradas:
        h = sha256(p)
        if p.parent == OUT_DIR:
            r = resumos.get(p)
            prod = origem_html(p, r if isinstance(r, dict) else None) if p.exists() else "—"
        else:
            prod = "dado observado (<code>data/</code>)"
        nlin = "—"
        if p.exists() and p.suffix == ".csv":
            with p.open(encoding="utf-8") as f:
                nlin = br_int(sum(1 for _ in f) - 1)
        linhas.append([f"<code>{esc(rel(p))}</code>",
                       '<span class="pill pill-ok">presente</span>' if h else '<span class="pill pill-pend">ausente</span>',
                       nlin, f"<code>{h[:12]}</code>" if h else "—", prod])
    return (
        '<section><h2>Apêndice — proveniência das entradas</h2>'
        "<p>Cada número e gráfico deste relatório é lido dos arquivos abaixo no momento da geração. "
        "SHA-256 truncado em 12 caracteres; o hash completo pode ser recalculado com <code>sha256sum</code>. "
        "Linhas = registros de dados (sem cabeçalho).</p>"
        + tabela([("Arquivo", "txt"), ("Status", "txt"), ("Linhas", "num"), ("SHA-256", "txt nowrap"),
                  ("Origem", "txt")], linhas, classe="compacta proven")
        + f"<p class=\"nota\">Relatório gerado por <code>{esc(rel(ESTE_SCRIPT))}</code>; gráficos em SVG desenhados "
          "pelo próprio script, sem biblioteca de gráficos; PDF impresso pelo Chromium headless a partir do HTML.</p>"
        + "</section>"
    )


# ---------------------------------------------------------------------------
# Montagem
# ---------------------------------------------------------------------------


CSS = """
@page { size: A4 portrait; margin: 16mm 15mm 17mm 15mm;
  @bottom-left { content: "__RODAPE__"; font-family: Inter, "Liberation Sans", sans-serif; font-size: 7.5pt; color: #898781; }
  @bottom-right { content: "p. " counter(page) " de " counter(pages); font-family: Inter, "Liberation Sans", sans-serif; font-size: 7.5pt; color: #898781; }
}
@page :first { @bottom-left { content: none; } @bottom-right { content: none; } }
:root { color-scheme: light; --ink:#0b0b0b; --ink2:#52514e; --muted:#898781; --grid:#e1e0d9; --axis:#c3c2b7;
  --wash:#f3f2ee; --s1:#2a78d6; --warn:#c98500; --warn-bg:#fbf5e6; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; background: #fff; }
body { font-family: __FONTE__; font-size: 9.4pt; line-height: 1.45; color: var(--ink); background: #fff; margin: 0; }
main { max-width: 180mm; margin: 0 auto; }
@media screen { main { padding: 12mm 0; } }
h1 { font-size: 24pt; font-weight: 650; line-height: 1.15; margin: 4mm 0 4mm; letter-spacing: -0.01em; }
h2 { font-size: 14pt; font-weight: 650; margin: 0 0 6pt; padding-bottom: 4pt; border-bottom: 1px solid var(--axis); }
h3 { font-size: 10.5pt; font-weight: 650; margin: 12pt 0 4pt; break-after: avoid; }
section { margin-bottom: 14pt; }
section.quebra { break-before: page; }
p { margin: 0 0 6pt; }
ul, ol { margin: 0 0 6pt; padding-left: 16pt; }
li { margin-bottom: 2pt; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 7.6pt; color: var(--ink2); overflow-wrap: anywhere; }
pre.cmd { font-family: "DejaVu Sans Mono", monospace; font-size: 7.6pt; background: var(--wash); padding: 4pt 6pt;
  border-radius: 3px; margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; }
.bloco-tab { margin: 4pt 0 6pt; }
.bloco-tab.inteiro { break-inside: avoid; }
.nowrap { white-space: nowrap; }
ul.notas { list-style: none; padding-left: 0; margin: 0 0 6pt; font-size: 7.2pt; color: var(--ink2); }
ul.notas li { margin: 0; }
table.proven td:first-child { width: 58mm; }
table.proven code { font-size: 6.8pt; }
.muted { color: var(--muted); }
.nota { font-size: 8.4pt; color: var(--ink2); }
.alerta { font-size: 8.8pt; color: #a02020; border-left: 3px solid #d03b3b; padding-left: 6pt; }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt; margin: 2pt 0 4pt; font-variant-numeric: tabular-nums; }
table.compacta { font-size: 7.6pt; }
table.estreita { width: auto; min-width: 50%; }
th { text-align: left; font-weight: 600; color: var(--ink2); border-bottom: 1px solid var(--axis); padding: 3pt 4pt;
  vertical-align: bottom; line-height: 1.2; }
td { border-bottom: 1px solid var(--grid); padding: 2.4pt 4pt; vertical-align: top; }
th.num, td.num { text-align: right; }
td.num { white-space: nowrap; }
tr { break-inside: avoid; }
thead { display: table-header-group; }
.nota-cel { color: var(--muted); font-size: 7pt; line-height: 1.25; display: inline-block; }
td.nota { max-width: 52mm; }
.tab-titulo, .fig-titulo { font-weight: 600; font-size: 9.4pt; margin: 10pt 0 2pt; break-after: avoid; }
.fig-num { color: var(--ink2); }
.fig-sub { color: var(--ink2); font-size: 8.4pt; margin-bottom: 4pt; }
.fig-nota { color: var(--ink2); font-size: 8pt; margin-top: 4pt; }
figure { margin: 8pt 0 12pt; break-inside: avoid; }
figure svg { display: block; width: 100%; height: auto; }
.fonte { font-size: 7.4pt; color: var(--muted); border-top: 1px solid var(--grid); padding-top: 3pt; margin: 3pt 0 10pt; }
.fonte code { font-size: 7pt; color: var(--muted); }
.capa { min-height: 250mm; display: flex; flex-direction: column; break-after: page; }
.kicker { font-size: 9pt; color: var(--ink2); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 30mm; }
.lead { font-size: 11pt; color: var(--ink2); max-width: 150mm; }
dl.meta { display: grid; grid-template-columns: 42mm 1fr; gap: 3pt 8pt; margin: 8mm 0; font-size: 9.4pt; }
dl.meta dt { color: var(--muted); }
dl.meta dd { margin: 0; }
.aviso { border-left: 3px solid var(--warn); background: var(--warn-bg); padding: 8pt 10pt; margin: 2mm 0 6mm; font-size: 9.6pt; }
table.status td:first-child { font-weight: 600; white-space: nowrap; }
.sumario li { margin-bottom: 1pt; }
.pill { display: inline-block; font-size: 7.4pt; font-weight: 600; padding: 1pt 6pt; border-radius: 8pt;
  text-transform: uppercase; letter-spacing: 0.03em; white-space: nowrap; }
.pill-ok { background: #e3f1e3; color: #006300; }
.pill-pend { background: #fbecd2; color: #7a4d00; }
.pendente { border: 1px solid var(--axis); background: var(--wash); padding: 8pt 10pt; border-radius: 4px; margin: 6pt 0 10pt; }
.pend-tit { font-weight: 600; }
.destaque { border-left: 3px solid var(--s1); padding: 4pt 0 4pt 10pt; margin: 6pt 0; }
dl.kv { display: grid; grid-template-columns: 38mm 1fr; gap: 2pt 8pt; margin: 4pt 0 6pt; font-size: 8.6pt; }
dl.kv dt { color: var(--ink2); font-weight: 600; }
dl.kv dd { margin: 0; }
dl.kv dl.kv { grid-template-columns: 30mm 1fr; font-size: 8.2pt; }
dl.protocolo { background: var(--wash); padding: 6pt 8pt; border-radius: 4px; }
ul.leitura li { margin-bottom: 3pt; }
dl.leitura-dl dt { font-weight: 650; margin-top: 8pt; break-after: avoid; }
dl.leitura-dl dd { break-inside: avoid; }
dl.leitura-dl dd { margin: 2pt 0 0; }
"""


def montar_html(commit, sujo, agora) -> str:
    r1, mat, ivs, c_inf, c_sup, faixas, valor_faixa = carregar_regra()
    prot = ler_json(PROTOCOLO)
    e3 = ler_json(E3_STATUS)
    status_itens = [
        ("Regra (R1)", True, "presente", f"<code>{esc(rel(R1_JSON))}</code>; decisão: {esc(r1.get('decisao_r1', '—'))}"),
        ("E1", E1_EST.exists(), "disponível" if E1_EST.exists() else "pendente",
         ("exploratório, condicional a A1" if E1_EST.exists() else f"<code>{esc(rel(E1_EST))}</code> ausente")),
        ("E2", E2_LIM.exists(), "disponível" if E2_LIM.exists() else "pendente",
         ("exploratório, limites parciais" if E2_LIM.exists() else f"<code>{esc(rel(E2_LIM))}</code> ausente")),
        ("E3", False,
         (str(e3.get("status", "status registrado")).replace("_", " ") if isinstance(e3, dict) else "pendente"),
         ("aguardando escore completo" if e3 is None else f"<code>{esc(rel(E3_STATUS))}</code>")),
    ]
    corpo = [
        secao_capa(commit, sujo, agora, prot, status_itens),
        secao_regra(r1, mat, ivs, c_inf, c_sup, faixas, valor_faixa),
        secao_cobertura(r1, mat, faixas),
        secao_e1(prot),
        secao_e2(prot),
        secao_e3(prot),
        secao_leitura(prot, r1),
        secao_proveniencia(),
    ]
    rodape = f"{TITULO} · commit {commit} · gerado em {agora.strftime('%d/%m/%Y')}".replace('"', "'")
    css = CSS.replace("__RODAPE__", rodape).replace("__FONTE__", FONTE_SANS)
    return (
        '<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>RDD da bolsa — resultados</title><style>{css}</style></head>"
        f"<body><main>{''.join(corpo)}</main></body></html>\n"
    )


def localizar_chrome() -> str | None:
    cands = []
    if os.environ.get("CHROME_BIN"):
        cands.append(os.environ["CHROME_BIN"])
    cands.append("/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    cands += sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"), reverse=True)
    for nome in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        w = shutil.which(nome)
        if w:
            cands.append(w)
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def contar_paginas(pdf: Path) -> int | None:
    if shutil.which("pdfinfo"):
        r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
        m = re.search(r"^Pages:\s+(\d+)", r.stdout, re.M)
        if m:
            return int(m.group(1))
    dados = pdf.read_bytes()
    n = len(re.findall(rb"/Type\s*/Page(?!s)", dados))
    return n or None


def gerar_pdf(html_path: Path, pdf_path: Path) -> bool:
    chrome = localizar_chrome()
    if not chrome:
        print("AVISO: Chromium nao encontrado; PDF nao gerado (defina CHROME_BIN).", file=sys.stderr)
        return False
    if pdf_path.exists():
        pdf_path.unlink()
    with tempfile.TemporaryDirectory(prefix="relatorio_rdd_") as perfil:
        cmd = [
            chrome,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            f"--user-data-dir={perfil}",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        print(f"ERRO: Chromium nao gerou o PDF (codigo {r.returncode}).\n{r.stderr[-2000:]}", file=sys.stderr)
        return False
    return True


def main() -> int:
    commit, sujo = git_info()
    agora = dt.datetime.now()
    doc = montar_html(commit, sujo, agora)
    OUT_HTML.write_text(doc, encoding="utf-8")
    print(f"HTML: {rel(OUT_HTML)} ({OUT_HTML.stat().st_size / 1024:.0f} KiB)")
    ok = gerar_pdf(OUT_HTML, OUT_PDF)
    if not ok:
        return 1
    n = contar_paginas(OUT_PDF)
    print(f"PDF:  {rel(OUT_PDF)} ({OUT_PDF.stat().st_size / 1024:.0f} KiB, {n if n else '?'} paginas)")
    pend = [rel(p) for p in (E1_EST, E1_CONT, E1_RES, E2_LIM, E2_RES, E3_STATUS) if not p.exists()]
    if pend:
        print("Pendentes (secoes marcadas como pendente): " + ", ".join(pend))
    return 0


if __name__ == "__main__":
    sys.exit(main())
