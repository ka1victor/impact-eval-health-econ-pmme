"""Monta o relatorio de resultados da RDD da bolsa do PMM-E (HTML e PDF).

O relatorio e a base que o grupo usa para montar os slides. Nao estima nada
novo: le os resultados gravados em `output/` (e dados observados em `data/`,
so para as comparacoes e o grafico RD) e os apresenta em tabelas e graficos
SVG desenhados aqui, sem bibliotecas de grafico (apenas numpy, pandas e a
biblioteca padrao).

Historia que o relatorio conta
------------------------------
1. A regra: a bolsa anunciada e funcao do IVS 2010 oficial do municipio (Ipea),
   que e o proprio escore administrativo do MS, com cortes 0,300 e 0,400
   (+R$ 5 mil em cada). O arquivo `data/ivs_ipea_2010_municipios.csv`, usado ate
   14/10/2026 como "IVS 2010", vem da mesma base oficial do Ipea, mas da linha
   errada: em cada municipio, a ultima linha de subgrupo com IVS preenchido
   (mulheres negras urbanas em 78% dos municipios; outros recortes de mulheres
   no resto, segundo `identificacao_arquivo_local_ivs.json`), nao o IVS do
   municipio. O rotulo do arquivo local e montado a partir desse JSON.
2. E3, a RDD sharp com o escore completo, e a analise principal.
3. E1, E2 e E4, feitos quando o escore era parcial, sao exploratorios e ficam
   como historico, superados pelo E3.

Calculos feitos aqui (so para exibicao)
---------------------------------------
- reproducao da faixa anunciada pelo IVS oficial e pelo arquivo local, por
  quadro, conferida contra `portao_r1_ivs_oficial.json`, e o cruzamento
  variavel x grade (grade aplicada 0,300/0,400 contra a grade do FAQ do
  edital, com os cortes registrados em `a01b_reconstrucao_regra_faixa.json`);
- "primeiro estagio" em bins de 0,020 no quadro c1_ch1;
- grafico RD de P1: medias do outcome em bins de 0,010 e retas locais lineares
  da especificacao principal. D_1 e lido da relacao nominal (so `co_ibge` e
  `ciclo`) com as funcoes do script do E3; a fracao preenchida vem de
  `E4_proporcao_municipio.csv`. O salto de cada reta e conferido contra
  `E3_estimativas.csv`; se divergir, o script para sem gerar o relatorio;
- efeito minimo detectavel aproximado = 2,8 x EP da especificacao principal.

Entradas: lista ENTRADAS (todas com SHA-256 no apendice do relatorio).

Saidas
------
- output/rdd_bolsa/relatorio_resultados_rdd_bolsa.html  (autocontido)
- output/rdd_bolsa/relatorio_resultados_rdd_bolsa.pdf  (A4 retrato, via Chromium headless)

Linguagem: o E3 da a estimativa local do efeito do anuncio de +R$ 5 mil sob as
premissas da RDD; nao identifica participacao no PMM-E. E1, E2 e E4 sao
exploratorios. O relatorio nao diz que "a bolsa nao funciona": diz que nao
detectamos efeito e que os intervalos nao excluem efeitos grandes.
"""

from __future__ import annotations

import datetime as dt
import glob
import hashlib
import html
import importlib.util
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
AQ_DIR = ROOT / "output" / "aquisicao"

# Regra e escore
R1_OFICIAL = OUT_DIR / "portao_r1_ivs_oficial.json"
R1_ADMIN = OUT_DIR / "portao_r1_escore_administrativo.json"  # R1 com escore parcial: datas dos quadros
MATRIZ = OUT_DIR / "matriz_municipio_escore_administrativo.csv"
ESCORE = OUT_DIR / "escore_completo_ivs2010_oficial.csv"
IVS_OFICIAL = AQ_DIR / "a08_ivs_2010_oficial_municipio.csv"
MANIF_OFICIAL = AQ_DIR / "a08_manifesto_ivs_2010_oficial.json"
ESCORE_ADMIN = AQ_DIR / "a07_ivs_administrativo_municipio.csv"
CATEGORIA = AQ_DIR / "a07_categoria_ivs_pmmb_municipio.csv"
IVS_LOCAL = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
IDENT_LOCAL = OUT_DIR / "identificacao_arquivo_local_ivs.json"  # de que recorte do Ipea vem o arquivo local
A01B = OUT_DIR / "a01b_reconstrucao_regra_faixa.json"
A01 = OUT_DIR / "a01_primeiro_estagio_publico.json"
REGRA_ANTIGA = OUT_DIR / "portao_regra_ivs.json"
# Protocolos
PROTOCOLO = OUT_DIR / "protocolo_escore_administrativo.json"
ADENDO_E4 = OUT_DIR / "protocolo_E4_adendo_proporcao.json"
# E3
E3_STATUS = OUT_DIR / "E3_status.json"
E3_EST = OUT_DIR / "E3_estimativas.csv"
E3_DIAG = OUT_DIR / "E3_diagnosticos.csv"
E3_SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py"
ATIVOS_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
E4_PROP = OUT_DIR / "E4_proporcao_municipio.csv"
# Historico (escore parcial)
E1_EST = OUT_DIR / "E1_densidade_estimativas.csv"
E1_RES = OUT_DIR / "E1_densidade_resumo.json"
E2_LIM = OUT_DIR / "E2_limites.csv"
E2_RES = OUT_DIR / "E2_limites_resumo.json"
E4_EST = OUT_DIR / "E4_estimativas.csv"
E4_RES = OUT_DIR / "E4_resumo.json"

ENTRADAS = [
    R1_OFICIAL, R1_ADMIN, MATRIZ, ESCORE, IVS_OFICIAL, MANIF_OFICIAL, ESCORE_ADMIN, CATEGORIA, IVS_LOCAL,
    IDENT_LOCAL, A01B, PROTOCOLO, ADENDO_E4, E3_STATUS, E3_EST, E3_DIAG, E4_PROP, ATIVOS_ZIP, E3_SCRIPT,
    E1_EST, E1_RES, E2_LIM, E2_RES, E4_EST, E4_RES,
]
OBRIGATORIAS = [R1_OFICIAL, MATRIZ, ESCORE, IVS_OFICIAL, IVS_LOCAL, IDENT_LOCAL, PROTOCOLO, E3_STATUS, E3_EST,
                E3_DIAG, E4_PROP, ATIVOS_ZIP, E3_SCRIPT]

OUT_HTML = OUT_DIR / "relatorio_resultados_rdd_bolsa.html"
OUT_PDF = OUT_DIR / "relatorio_resultados_rdd_bolsa.pdf"

TITULO = "RDD da bolsa do PMM-E — resultados"

# Populacoes em termos de quadros da matriz (mesma definicao do
# 04b_validar_ivs_oficial_escore_administrativo.py; conferida contra o R1).
QUADROS_POP = {"P1": ["c1_ch1"], "P2": ["c2_ch1", "c2_ch2"], "ciclo_3_congelado": ["c3_ch1"]}

# Parametros de exibicao (nao sao dados).
QUADRO_PRIMEIRO_ESTAGIO = "c1_ch1"
BIN_PE_MIL = 20  # bins de 0,020 no "primeiro estagio"
N_BINS_PE = 3  # bins por lado
BIN_RD_MIL = 10  # bins de 0,010 no grafico RD
ALCANCE_RD_MIL = 80  # +-0,080 em torno de cada corte
SEMENTE_JITTER = 20261014  # deslocamento vertical do grafico da regra
ALFA = 0.05
# Efeito minimo detectavel com 80% de poder e teste bicaudal a 5%:
# (z_0,975 + z_0,80) x EP ~ (1,96 + 0,84) x EP.
MDE_FATOR = 2.8
TOL_TAU = 1e-7  # tolerancia da conferencia do salto do grafico RD contra o E3

OUTCOME_D = "D_k_especialista_ativo_do_ciclo"
OUTCOME_FRAC = "fracao_celulas_ch1_com_confirmacao_ou_homologacao"
COVARIAVEL_RUNNING = "ivs_2010"  # no balanco do E3, e o proprio IVS oficial (a running variable)
ROTULO_COV = {
    "ivs_infra_2010": ("IVS: infraestrutura urbana (subíndice)", 3),
    "ivs_ch_2010": ("IVS: capital humano (subíndice)", 3),
    "ivs_rt_2010": ("IVS: renda e trabalho (subíndice)", 3),
    "log_populacao_2010": ("log da população (2010)", 2),
    "rdpc_2010": ("renda per capita (2010, R$)", 0),
    "estrato_capital": ("estrato: capital", 2),
    "estrato_interior_proximo_polo": ("estrato: interior próximo de polo", 2),
    "estrato_interior_remoto": ("estrato: interior remoto", 2),
    "estrato_metropolitano": ("estrato: metropolitano", 2),
}
# Arquivos de output/ que citam o arquivo local apenas para registrar que ele
# foi substituido (nao o usam como fonte); ficam fora da varredura de revisao.
CITAM_SEM_USAR = {R1_OFICIAL, MANIF_OFICIAL, E3_STATUS, IDENT_LOCAL}

# Paleta (dataviz, instancia de referencia, modo claro). Categorica validada
# com scripts/validate_palette.js --pairs all contra a superficie #ffffff:
# azul/laranja passam todas as checagens (CVD dE 24,7; visao normal 33,6;
# contraste >= 3:1). "muted" e o cinza de de-enfase.
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
        return Path(p).resolve().relative_to(ROOT).as_posix()
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
    """x ja em pontos percentuais (0 a 100)."""
    return "—" if not finito(x) else br(x, nd) + "%"


def pct(x, nd: int = 1) -> str:
    """Proporcao (0 a 1) como percentual."""
    return "—" if not finito(x) else br(100 * float(x), nd) + "%"


def pp(x, nd: int = 1) -> str:
    """Proporcao (0 a 1) em pontos percentuais com sinal: +11,5 / −12,8 / 0,0."""
    if not finito(x):
        return "—"
    s = br(100 * float(x), nd)
    return s if s.startswith("−") or s.strip("0,") == "" else "+" + s


def ic_pp(lo, hi, nd: int = 1) -> str:
    return f"[{pp(lo, nd)}; {pp(hi, nd)}]"


def sinal(x, nd: int) -> str:
    s = br(x, nd)
    return s if s.startswith("−") or s.strip("0,.") == "" else "+" + s


def br_p(p) -> str:
    if not finito(p):
        return "—"
    return "< 0,001" if float(p) < 0.001 else br(p, 3)


def br_mil(v: float) -> str:
    return f"R$ {br(v / 1000, 0)} mil" if float(v) % 1000 == 0 else f"R$ {br(v, 0)}"


def data_br(s) -> str:
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", str(s or ""))
    return f"{m.group(3)}/{m.group(2)}/{m.group(1)}" if m else (str(s) if s else "—")


def milesimos(s) -> np.ndarray:
    """Escore em milesimos (float; NaN preservado)."""
    return np.rint(np.asarray(s, dtype=float) * 1000)


def faixa_pelo_valor(m: float, c_mil: list[int], faixas: list[str]) -> str | None:
    """faixas = [baixa, media, alta] em ordem crescente de valor; o corte fica no lado inferior."""
    if not finito(m):
        return None
    if m <= c_mil[0]:
        return faixas[0]
    if m <= c_mil[1]:
        return faixas[1]
    return faixas[2]


def nome_quadro(q: str) -> str:
    m = re.fullmatch(r"c(\d+)_ch(\d+)", str(q))
    return f"Ciclo {m.group(1)}, chamada {m.group(2)}" if m else str(q)


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

    Usa o campo `script` do resumo JSON quando existe; senao procura, nos
    scripts de `scripts/rdd_bolsa/` e `scripts/aquisicao/`, uma constante de
    saida (OUT_*, SAIDA_*, NOME_*) com o nome do arquivo ou uma escrita direta
    (`to_csv(OUT / "nome")`, `(OUT / "nome").write_text`). Um script que apenas
    le o arquivo nao conta como produtor.
    """
    if isinstance(resumo, dict) and isinstance(resumo.get("script"), str):
        return resumo["script"]
    chave = rel(arquivo)
    if chave in _CACHE_PRODUTOR:
        return _CACHE_PRODUTOR[chave]
    nome = re.escape(arquivo.name)
    padroes = [
        re.compile(r"^\s*(OUT\w*|SAIDA\w*|NOME_\w*)\s*=.*[\"']" + nome + r"[\"']", re.M),
        re.compile(r"(to_csv|to_parquet|to_json)\(\s*OUT\w*\s*/\s*[\"']" + nome + r"[\"']"),
        re.compile(r"\(\s*OUT\w*\s*/\s*[\"']" + nome + r"[\"']\s*\)\s*\.\s*write_(text|bytes)"),
    ]
    achado = None
    for pasta in (ROOT / "scripts" / "rdd_bolsa", ROOT / "scripts" / "aquisicao"):
        for s in sorted(pasta.glob("*.py")):
            if s.resolve() == ESTE_SCRIPT:
                continue
            txt = s.read_text(encoding="utf-8", errors="ignore")
            if any(p.search(txt) for p in padroes):
                achado = rel(s)
                break
        if achado:
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


def eh_saida(p: Path) -> bool:
    try:
        Path(p).resolve().relative_to(ROOT / "output")
        return True
    except ValueError:
        return False


def origem_html(p: Path, resumo: dict | None = None) -> str:
    """Descricao curta da origem de um arquivo para a linha de fonte."""
    if p.suffix == ".py":
        return "código versionado, importado"
    if not eh_saida(p):
        return "dado observado"
    prod = script_produtor(p, resumo)
    if prod:
        return f"gerado por <code>{esc(prod)}</code>"
    c = commit_do_arquivo(p)
    return f"documento versionado sem script produtor (commit {esc(c)})" if c else "origem não declarada"


def fonte_html(*arquivos: Path, extra: str = "", grafico: bool = True) -> str:
    partes = [f"<code>{esc(rel(a))}</code> ({origem_html(a)})" for a in arquivos]
    txt = "; ".join(partes)
    if extra:
        txt += f". {extra}"
    fim = f" Gráfico desenhado por <code>{esc(rel(ESTE_SCRIPT))}</code>." if grafico else ""
    return f'<div class="fonte">Fonte: {txt}.{fim}</div>'


# ---------------------------------------------------------------------------
# Primitivas SVG e HTML
# ---------------------------------------------------------------------------


class Linear:
    def __init__(self, d0: float, d1: float, r0: float, r1: float):
        self.d0, self.d1, self.r0, self.r1 = d0, d1, r0, r1

    def __call__(self, v: float) -> float:
        return self.r0 + (v - self.d0) / (self.d1 - self.d0) * (self.r1 - self.r0)


def nice_ticks(lo: float, hi: float, n: int = 5) -> list[float]:
    span = hi - lo
    if span <= 0:
        return [lo]
    raw = span / max(n, 1)
    mag = 10 ** math.floor(math.log10(raw))
    step = mag
    for mult in (1, 2, 2.5, 5, 10):
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


def ponto(x, y, cor, r=4.0, titulo="", opacidade=None, anel=2.0) -> str:
    op = f' fill-opacity="{opacidade}"' if opacidade is not None else ""
    tt = f"<title>{esc(titulo)}</title>" if titulo else ""
    return (f'<circle cx="{f2(x)}" cy="{f2(y)}" r="{r}" fill="{cor}"{op} stroke="{COR["surface"]}" '
            f'stroke-width="{anel}">{tt}</circle>')


def svg_abrir(w: int, h: int, rotulo: str, estilo: str = "") -> str:
    st = f' style="{estilo}"' if estilo else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" '
        f'aria-label="{esc(rotulo)}"{st}>'
    )


def legenda_svg(itens: list[tuple[str, str, str]], x: float, y: float, size=10.5) -> str:
    """itens = [(tipo, cor, rotulo)], tipo em {'ponto','linha'}."""
    out = []
    cx = x
    for tipo, cor, rot in itens:
        if tipo == "ponto":
            out.append(f'<circle cx="{f2(cx + 5)}" cy="{f2(y - 3.5)}" r="4.5" fill="{cor}"/>')
        elif tipo == "linha":
            out.append(l_svg(cx, y - 3.5, cx + 14, y - 3.5, cor=cor, w=2))
        out.append(t_svg(cx + 19, y, rot, size=size, cor=COR["ink2"]))
        cx += 19 + len(rot) * size * 0.53 + 18
    return "".join(out)


def caixa_ausente(titulo: str, arquivos: list[Path]) -> str:
    lista = "".join(
        f"<li><code>{esc(rel(a))}</code> — {'presente' if a.exists() else 'ausente'}</li>" for a in arquivos
    )
    return (f'<div class="pendente"><p class="pend-tit"><span class="pill pill-pend">ausente</span> '
            f"{esc(titulo)}</p><ul>{lista}</ul></div>")


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


def titulo_tabela(txt: str) -> str:
    return f'<div class="tab-titulo"><span class="fig-num">Tabela {NUM.tabela()}.</span> {txt}</div>'


def tabela(cabecalho: list[tuple[str, str]], linhas: list[list[str]], classe: str = "", titulo: str = "",
           rodape: str = "", inteiro: bool | None = None) -> str:
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
    if inteiro is None:
        inteiro = len(linhas) <= 18
    return f'<div class="bloco-tab{" inteiro" if inteiro else ""}">{tt}{tab}{rodape}</div>'


def figura(titulo: str, svg: str, fonte: str, sub: str = "", nota: str = "") -> str:
    n = NUM.figura()
    s = f'<div class="fig-sub">{sub}</div>' if sub else ""
    nt = f'<div class="fig-nota">{nota}</div>' if nota else ""
    return (
        f'<figure class="fig"><div class="fig-titulo"><span class="fig-num">Figura {n}.</span> {titulo}</div>'
        f"{s}{svg}{nt}{fonte}</figure>"
    )


def dl_kv(itens: list[tuple[str, str]], classe: str = "kv") -> str:
    return f'<dl class="{classe}">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in itens) + "</dl>"


# ---------------------------------------------------------------------------
# Carga e conferencias
# ---------------------------------------------------------------------------


def importar_e3():
    """Importa o script do E3 (nome comeca com digito) sem gravar bytecode."""
    spec = importlib.util.spec_from_file_location("e3_rdd_completa", E3_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


def carregar() -> dict:
    faltam = [rel(p) for p in OBRIGATORIAS if not p.exists()]
    if faltam:
        raise SystemExit("Entradas obrigatorias ausentes: " + ", ".join(faltam))
    r1 = ler_json(R1_OFICIAL)
    st = ler_json(E3_STATUS)
    prot = ler_json(PROTOCOLO)
    if r1.get("decisao_r1") != "APROVADO_SHARP":
        raise SystemExit(f"R1 com o IVS oficial nao aprovado: {r1.get('decisao_r1')}")
    if st.get("status") != "CONCLUIDO":
        raise SystemExit(f"E3 nao concluido ({st.get('status')}); o relatorio exige a RDD completa.")

    cortes = sorted(float(c) for c in st["cortes"])
    cortes_prot = sorted(float(c) for c in prot["running_variable"]["cortes"])
    if len(cortes) != 2 or cortes != cortes_prot:
        raise SystemExit(f"Cortes do E3 {cortes} divergem do protocolo {cortes_prot}")
    c_mil = [int(round(c * 1000)) for c in cortes]

    mat = pd.read_csv(MATRIZ, dtype={"co_ibge": str})
    valores = mat.groupby("faixa_anunciada")["valor_anunciado_brl"].agg(lambda s: sorted(set(s)))
    if any(len(v) != 1 for v in valores):
        raise SystemExit("Mais de um valor anunciado por faixa na matriz; a bolsa nao e funcao da faixa.")
    valor_faixa = {f: float(v[0]) for f, v in valores.items()}
    faixas = sorted(valor_faixa, key=valor_faixa.get)  # [baixa, media, alta]
    if len(faixas) != 3:
        raise SystemExit(f"Esperadas 3 faixas; encontradas {faixas}")

    of = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str})
    of["s_mil"] = milesimos(of["ivs"])
    esc_ = pd.read_csv(ESCORE, dtype={"co_ibge": str})
    esc_["s_mil"] = milesimos(esc_["ivs_admin"])
    j = of[["co_ibge", "s_mil"]].merge(esc_[["co_ibge", "s_mil"]], on="co_ibge", how="outer",
                                       suffixes=("_of", "_esc"))
    if len(j) != len(of) or not np.array_equal(j["s_mil_of"].to_numpy(), j["s_mil_esc"].to_numpy()):
        raise SystemExit("O escore completo do E3 nao e o IVS 2010 oficial do a08.")

    loc = pd.read_csv(IVS_LOCAL, dtype={"cod_ibge6": str})
    loc = loc.rename(columns={"cod_ibge6": "co_ibge", "ivs_2010": "ivs_local"})[["co_ibge", "ivs_local"]]
    loc["s_mil_local"] = milesimos(loc["ivs_local"])

    base = (mat[["quadro", "co_ibge", "faixa_anunciada", "valor_anunciado_brl"]]
            .merge(of[["co_ibge", "ivs", "s_mil"]], on="co_ibge", how="left")
            .merge(loc, on="co_ibge", how="left"))
    base["faixa_oficial"] = [faixa_pelo_valor(m, c_mil, faixas) for m in base["s_mil"]]
    base["faixa_local"] = [faixa_pelo_valor(m, c_mil, faixas) for m in base["s_mil_local"]]

    est = pd.read_csv(E3_EST)
    diag = pd.read_csv(E3_DIAG)
    ident = ler_json(IDENT_LOCAL)
    return {
        "r1": r1, "r1_adm": ler_json(R1_ADMIN) or {}, "st": st, "prot": prot, "adendo": ler_json(ADENDO_E4) or {},
        "a01b": ler_json(A01B) or {}, "manif": ler_json(MANIF_OFICIAL) or {},
        "ident": ident or {}, "rl": recorte_local(ident),
        "cortes": cortes, "c_mil": c_mil, "faixas": faixas, "valor_faixa": valor_faixa,
        "mat": mat, "of": of, "loc": loc, "base": base, "est": est, "diag": diag,
        "h_principal": float(st["janelas"]["principal"]),
        "h_sens": [float(h) for h in st["janelas"]["sensibilidade"]],
    }


def populacao(base: pd.DataFrame, nome: str) -> pd.DataFrame:
    return base[base["quadro"].isin(QUADROS_POP[nome])].drop_duplicates("co_ibge").reset_index(drop=True)


def conferir_populacoes(ctx) -> list[str]:
    """Contagens da matriz x IVS oficial contra o R1 oficial e o status do E3."""
    base, r1, st = ctx["base"], ctx["r1"], ctx["st"]
    diverg = []
    for nome in QUADROS_POP:
        g = populacao(base, nome)
        com = g[g["s_mil"].notna()]
        rep = int((com["faixa_oficial"] == com["faixa_anunciada"]).sum())
        jr = (r1.get("populacoes") or {}).get(nome, {})
        meu = (len(g), len(com), rep)
        dele = (jr.get("municipios"), jr.get("com_ivs_oficial"), jr.get("regra_reproduz"))
        if meu != dele:
            diverg.append(f"{nome}: matriz x IVS oficial dá {meu}, R1 registra {dele}")
        cob = (st.get("cobertura_do_escore") or {}).get(nome)
        if cob and (cob.get("municipios"), cob.get("com_escore")) != (len(g), len(com)):
            diverg.append(f"{nome}: E3 registra {cob.get('municipios')}/{cob.get('com_escore')}")
    return diverg


def data_relacao_nominal(prot) -> str:
    m = re.search(r"\d{2}/\d{2}/\d{4}", str((prot.get("outcome") or {}).get("D_k", "")))
    return m.group(0) if m else "data da relação nominal"


def frase_recorte(rec: dict) -> str | None:
    """'mulheres negras urbanas' a partir de {'cor': 'Negro', 'sexo': 'Mulher', 'situacao': 'Urbano'}."""
    cor, sexo, sit = (str(rec.get(k, "")) for k in ("cor", "sexo", "situacao"))
    fem = sexo != "Homem"  # "mulheres" e "pessoas" pedem concordancia feminina
    sujeito = {"Mulher": "mulheres", "Homem": "homens"}.get(sexo, "pessoas" if sexo.startswith("Total") else None)
    adj_cor = {"Negro": "negras" if fem else "negros", "Branco": "brancas" if fem else "brancos"}.get(
        cor, "" if cor.startswith("Total") else None)
    adj_sit = {"Urbano": "urbanas" if fem else "urbanos", "Rural": "rurais"}.get(
        sit, "" if sit.startswith("Total") else None)
    if sujeito is None or adj_cor is None or adj_sit is None:
        return None
    return " ".join(x for x in (sujeito, adj_cor, adj_sit) if x)


FRASE_LINHA = {
    "Negro / Mulher / Urbano": "mulheres negras urbanas",
    "Negro / Mulher / Total Situação de Domicílio": "mulheres negras",
    "Total Cor / Mulher / Urbano": "mulheres urbanas",
    "Total Cor / Mulher / Total Situação de Domicílio": "mulheres",
    "Total Cor / Total Sexo / Total Situação de Domicílio": "o município (linha total)",
}


def recorte_local(ident: dict | None) -> dict:
    """Rotulos e numeros do arquivo local, lidos de identificacao_arquivo_local_ivs.json."""
    mec = (ident or {}).get("mecanismo") or {}
    esc_ = mec.get("linha_escolhida_por_municipio") or {}
    if not mec.get("reproduz_o_arquivo_inteiro") or not esc_:
        return {"ok": False, "curto": "arquivo local (recorte não identificado)",
                "longo": "arquivo local (recorte da base do Ipea não identificado)", "eixo": "Arquivo local"}
    n_mun = int((mec.get("conferencia_por_coluna") or {}).get("municipios") or sum(esc_.values()))
    principal, n_princ = max(esc_.items(), key=lambda kv: kv[1])
    frase = FRASE_LINHA.get(principal, principal)
    share = 100 * n_princ / n_mun
    nmu = (ident or {}).get("linha_negro_mulher_urbano") or {}
    pop = (ident or {}).get("populacao") or {}
    dist = "; ".join(f"{FRASE_LINHA.get(k, k)}: {br_int(v)}" for k, v in
                     sorted(esc_.items(), key=lambda kv: -kv[1]))
    return {
        "ok": True,
        "frase": frase,
        "recorte": principal,
        "total": "Total Cor / Total Sexo / Total Situação de Domicílio",
        "n_mun": n_mun, "n_princ": n_princ, "share": share, "dist": dist,
        "n_vazio": nmu.get("municipios_com_ivs_vazio_nessa_linha"), "n_sem": nmu.get("municipios_sem_a_linha"),
        "mecanismo": mec.get("descricao", ""),
        "curto": f"arquivo local (linha de subgrupo; {br(share, 0)}% {frase})",
        "longo": (f"arquivo local = última linha preenchida de cada município na base do Ipea ({frase} em "
                  f"{br_int(n_princ)} municípios; outros recortes de mulheres no resto)"),
        "eixo": f"Arquivo local: IVS 2010 de subgrupo ({br(share, 0)}% {frase})",
        "soma_pop": pop.get("soma_arquivo_local"), "pop_br": pop.get("censo_2010_brasil"),
        "pop_total_ok": pop.get("linha_total_igual_ao_censo"),
    }


def br_milhoes(v) -> str:
    return "—" if not finito(v) else f"{br(float(v) / 1e6, 1)} milhões"


def maiuscula(s: str) -> str:
    """Primeira letra maiuscula sem mexer no resto (str.capitalize rebaixaria siglas)."""
    return s[:1].upper() + s[1:]


# ---------------------------------------------------------------------------
# Rotulos do E3
# ---------------------------------------------------------------------------


def rotulo_pop(ctx, nome: str, curto: bool = False) -> str:
    spec = (ctx["st"].get("populacoes") or {}).get(nome, {})
    ciclo = spec.get("ciclo_do_outcome", "?")
    papel = {"principal": "principal", "replicacao": "replicação"}.get(spec.get("papel"), spec.get("papel", ""))
    return f"Ciclo {ciclo}" if curto else f"Ciclo {ciclo} ({nome}, {papel})"


def rotulo_outcome(ctx, outcome: str, curto: bool = False) -> str:
    if outcome == OUTCOME_FRAC:
        return "preenchimento" if curto else "fração de células CNES–curso preenchidas na 1ª chamada"
    if outcome == OUTCOME_D:
        return "presença" if curto else f"especialista do ciclo ativo em {data_relacao_nominal(ctx['prot'])}"
    return outcome.replace("_", " ")


ORDEM_GRUPOS = [("P1", OUTCOME_FRAC), ("P1", OUTCOME_D), ("P2", OUTCOME_D)]


def ordenar_est(est: pd.DataFrame, h_principal: float) -> pd.DataFrame:
    d = est.copy()
    ordem = {k: i for i, k in enumerate(ORDEM_GRUPOS)}
    d["_g"] = [ordem.get((p, o), len(ordem)) for p, o in zip(d["populacao"], d["outcome"])]
    d["_h"] = [0 if math.isclose(h, h_principal) else 1 for h in d["h"]]
    return d.sort_values(["_g", "corte", "_h", "h"], kind="stable").reset_index(drop=True)


def principais(ctx) -> pd.DataFrame:
    d = ordenar_est(ctx["est"], ctx["h_principal"])
    return d[d["especificacao"] == "principal"].reset_index(drop=True)


# ---------------------------------------------------------------------------
# Grafico RD de P1 (calculado aqui; conferido contra o E3)
# ---------------------------------------------------------------------------


def ajuste_local_linear(s_mil: np.ndarray, y: np.ndarray, c_mil: int, h_mil: int) -> np.ndarray:
    """Mesmo MQP do E3: y = a + b x + tau T + d T x, pesos max(0, 1 - |x|/h)."""
    x = s_mil - c_mil
    w = np.clip(1.0 - np.abs(x) / h_mil, 0.0, None)
    usa = (x > -h_mil) & (x <= h_mil) & (w > 0) & np.isfinite(y)
    xs = x[usa] / 1000.0
    t = (x[usa] > 0).astype(float)
    X = np.column_stack([np.ones_like(xs), xs, t, t * xs])
    W = w[usa]
    return np.linalg.solve(X.T @ (X * W[:, None]), X.T @ (W * y[usa]))


def dados_rd_p1(ctx) -> list[dict]:
    e3 = importar_e3()
    p1 = populacao(ctx["base"], "P1")
    if p1["s_mil"].isna().any():
        raise SystemExit("Municipio de P1 sem IVS oficial")
    k = int(((ctx["st"].get("populacoes") or {}).get("P1") or {}).get("ciclo_do_outcome", 1))
    ativos = e3.ler_ativos(ATIVOS_ZIP)
    d_k = e3.construir_d_k(p1["co_ibge"], ativos, k)
    prop = pd.read_csv(E4_PROP, dtype={"co_ibge": str})
    if set(prop["co_ibge"]) != set(p1["co_ibge"]):
        raise SystemExit("E4_proporcao_municipio.csv nao cobre exatamente os municipios de P1")
    d = p1[["co_ibge", "s_mil"]].copy()
    d["D"] = d["co_ibge"].map(d_k).astype(float)
    d = d.merge(prop[["co_ibge", "y1"]], on="co_ibge", how="left")
    s = d["s_mil"].to_numpy(float)
    h_mil = int(round(ctx["h_principal"] * 1000))
    est = ctx["est"]
    paineis = []
    for outcome, col in ((OUTCOME_FRAC, "y1"), (OUTCOME_D, "D")):
        y = d[col].to_numpy(float)
        for c, c_m in zip(ctx["cortes"], ctx["c_mil"]):
            beta = ajuste_local_linear(s, y, c_m, h_mil)
            linha = est[(est["populacao"] == "P1") & (est["outcome"] == outcome)
                        & np.isclose(est["corte"], c) & np.isclose(est["h"], ctx["h_principal"])]
            if len(linha) != 1:
                raise SystemExit(f"E3_estimativas sem linha unica para P1/{outcome}/{c}")
            r = linha.iloc[0]
            if abs(beta[2] - r["tau"]) > TOL_TAU:
                raise SystemExit(f"Salto do grafico RD ({beta[2]:.10f}) difere do E3 ({r['tau']:.10f}) "
                                 f"em P1/{outcome}/{c}")
            bins = []
            for lado in (-1, 1):
                for kk in range(1, ALCANCE_RD_MIL // BIN_RD_MIL + 1):
                    if lado < 0:
                        lo, hi = c_m - BIN_RD_MIL * kk, c_m - BIN_RD_MIL * (kk - 1)
                    else:
                        lo, hi = c_m + BIN_RD_MIL * (kk - 1), c_m + BIN_RD_MIL * kk
                    sel = (s > lo) & (s <= hi)
                    n = int(sel.sum())
                    bins.append({"lo": lo, "hi": hi, "n": n, "media": float(y[sel].mean()) if n else np.nan,
                                 "dentro": lo >= c_m - h_mil and hi <= c_m + h_mil})
            bins.sort(key=lambda b: b["lo"])
            paineis.append({"outcome": outcome, "corte": c, "c_mil": c_m, "h_mil": h_mil, "beta": beta,
                            "tau": float(r["tau"]), "ic_inf": float(r["ic95_inf"]), "ic_sup": float(r["ic95_sup"]),
                            "p": float(r["p_valor"]), "n_abaixo": int(r["n_abaixo"]), "n_acima": int(r["n_acima"]),
                            "bins": bins})
    return paineis


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------


def fig_regra_degraus(d: pd.DataFrame, cortes, faixas, valor_faixa) -> str:
    """d: um municipio por linha, com ivs (oficial) e valor_anunciado_brl."""
    d = d.sort_values("co_ibge").reset_index(drop=True)
    n = len(d)
    W, H = 680, 270
    ml, mr, mt, mb = 74, 24, 26, 44
    s = d["ivs"].to_numpy(float)
    v = d["valor_anunciado_brl"].to_numpy(float)
    x0 = math.floor(s.min() / 0.05) * 0.05
    x1 = math.ceil(s.max() / 0.05) * 0.05
    vals = [valor_faixa[f] for f in faixas]
    passo = vals[1] - vals[0]
    X = Linear(x0, x1, ml, W - mr)
    Y = Linear(vals[0] - passo * 0.55, vals[-1] + passo * 0.55, H - mb, mt)
    rng = np.random.default_rng(SEMENTE_JITTER)
    jit = rng.uniform(-1, 1, n) * passo * 0.28

    o = [svg_abrir(W, H, "Valor anunciado da bolsa contra o IVS 2010 oficial")]
    for vv in vals:
        o.append(l_svg(ml, Y(vv), W - mr, Y(vv), COR["grid"]))
        o.append(t_svg(ml - 8, Y(vv) + 3.5, br_mil(vv), anchor="end"))
    for tx in nice_ticks(x0, x1, 7):
        o.append(l_svg(X(tx), H - mb, X(tx), H - mb + 4, COR["axis"]))
        o.append(t_svg(X(tx), H - mb + 16, br(tx, 2), anchor="middle"))
    o.append(l_svg(ml, H - mb, W - mr, H - mb, COR["axis"]))
    o.append(t_svg((ml + W - mr) / 2, H - 6, "IVS 2010 oficial do Ipea (= escore administrativo do MS)",
                   anchor="middle"))
    for c in cortes:
        o.append(l_svg(X(c), mt - 4, X(c), H - mb, COR["axis"]))
        o.append(t_svg(X(c), mt - 9, br(c, 3), anchor="middle", cor=COR["ink"], peso=600))
    pts = [(x0, vals[0]), (cortes[0], vals[0]), (cortes[0], vals[1]), (cortes[1], vals[1]),
           (cortes[1], vals[2]), (x1, vals[2])]
    path = " ".join(f"{'M' if i == 0 else 'L'}{f2(X(a))},{f2(Y(b))}" for i, (a, b) in enumerate(pts))
    o.append(f'<path d="{path}" fill="none" stroke="{COR["ink2"]}" stroke-width="2" stroke-linejoin="round"/>')
    for i in range(n):
        tt = f"{d.at[i, 'co_ibge']}: IVS {br(s[i])}, {d.at[i, 'faixa_anunciada']} ({br_mil(v[i])})"
        o.append(ponto(X(s[i]), Y(v[i] + jit[i]), COR["s1"], r=2.6, titulo=tt, opacidade=0.5, anel=0.5))
    for c, (va, vb) in ((cortes[0], (vals[0], vals[1])), (cortes[1], (vals[1], vals[2]))):
        o.append(t_svg(X(c) + 6, Y((va + vb) / 2) + 4, f"+{br_mil(vb - va)}", cor=COR["ink"], peso=600))
    for i, f in enumerate(faixas):
        if i == len(faixas) - 1:
            o.append(t_svg(ml + 4, Y(valor_faixa[f]) - 5, f.title(), size=10, cor=COR["muted"]))
        else:
            o.append(t_svg(W - mr, Y(valor_faixa[f]) - 5, f.title(), anchor="end", size=10, cor=COR["muted"]))
    o.append("</svg>")
    return "".join(o)


def fig_local_vs_oficial(d: pd.DataFrame, cortes, rl: dict) -> str:
    """d: P1, com ivs (oficial), ivs_local e concorda (mesma faixa pelos dois)."""
    n, n_conc = len(d), int(d["concorda"].sum())
    W, H = 470, 486
    ml, mr, mt, mb = 56, 18, 52, 46
    allv = np.concatenate([d["ivs"].to_numpy(float), d["ivs_local"].to_numpy(float)])
    lo = math.floor(allv.min() / 0.05) * 0.05
    hi = math.ceil(allv.max() / 0.05) * 0.05
    X = Linear(lo, hi, ml, W - mr)
    Y = Linear(lo, hi, H - mb, mt)
    o = [svg_abrir(W, H, "Arquivo local contra o IVS 2010 oficial do município",
                   estilo="max-width:100mm;margin:0 auto")]
    for t in nice_ticks(lo, hi, 6):
        o.append(l_svg(X(t), mt, X(t), H - mb, COR["grid"]))
        o.append(l_svg(ml, Y(t), W - mr, Y(t), COR["grid"]))
        o.append(t_svg(X(t), H - mb + 15, br(t, 1), anchor="middle"))
        o.append(t_svg(ml - 6, Y(t) + 3.5, br(t, 1), anchor="end"))
    o.append(l_svg(ml, H - mb, W - mr, H - mb, COR["axis"]))
    o.append(l_svg(ml, mt, ml, H - mb, COR["axis"]))
    for c in cortes:
        o.append(l_svg(X(c), mt, X(c), H - mb, COR["ink2"], 0.9))
        o.append(l_svg(ml, Y(c), W - mr, Y(c), COR["ink2"], 0.9))
    o.append(l_svg(X(lo), Y(lo), X(hi), Y(hi), COR["muted"], 1))
    o.append(t_svg(X(hi) - 4, Y(hi) + 12, "45°", anchor="end", size=9.5, cor=COR["muted"]))
    o.append(t_svg((ml + W - mr) / 2, H - 8, "IVS 2010 oficial do município (= escore administrativo)",
                   anchor="middle"))
    o.append(t_svg(14, (mt + H - mb) / 2, rl["eixo"], anchor="middle",
                   extra=f'transform="rotate(-90 14 {f2((mt + H - mb) / 2)})"'))
    for flag, cor in ((True, COR["s1"]), (False, COR["s2"])):
        for r in d[d["concorda"] == flag].itertuples():
            tt = (f"{r.co_ibge}: IVS oficial {br(r.ivs)} ({r.faixa_oficial}); "
                  f"arquivo local {br(r.ivs_local)} ({r.faixa_local})")
            o.append(ponto(X(r.ivs), Y(r.ivs_local), cor, r=3.2, titulo=tt, opacidade=0.8, anel=0.8))
    o.append(legenda_svg([("ponto", COR["s1"], f"mesma faixa pelos dois ({br_int(n_conc)})")], ml, 16, size=10))
    o.append(legenda_svg([("ponto", COR["s2"], f"faixa diferente pelo arquivo local ({br_int(n - n_conc)})")],
                         ml, 32, size=10))
    o.append("</svg>")
    return "".join(o)


def dados_primeiro_estagio(ctx) -> tuple[pd.DataFrame, int]:
    d = ctx["base"][ctx["base"]["quadro"] == QUADRO_PRIMEIRO_ESTAGIO].drop_duplicates("co_ibge")
    vals = [ctx["valor_faixa"][f] for f in ctx["faixas"]]
    linhas = []
    for i, c_m in enumerate(ctx["c_mil"]):
        tratado = d["valor_anunciado_brl"].to_numpy(float) >= vals[i + 1]
        bordas = [c_m + k * BIN_PE_MIL for k in range(-N_BINS_PE, N_BINS_PE + 1)]
        for var, col in (("oficial", "s_mil"), ("local", "s_mil_local")):
            m = d[col].to_numpy(float)
            ok = np.isfinite(m)
            for lo, hi in zip(bordas[:-1], bordas[1:]):
                sel = ok & (m > lo) & (m <= hi)
                nn, kk = int(sel.sum()), int((sel & tratado).sum())
                linhas.append({"corte_mil": c_m, "valor_min": vals[i + 1], "var": var, "lo": lo / 1000,
                               "hi": hi / 1000, "n": nn, "k": kk, "pct": 100 * kk / nn if nn else np.nan})
    return pd.DataFrame(linhas), len(d)


def fig_primeiro_estagio(pe: pd.DataFrame, cortes, rot_local: str) -> str:
    W, H = 680, 270
    ml, mr, gap = 44, 10, 46
    pw = (W - ml - mr - gap) / 2
    mt, mb = 58, 44
    Y = Linear(0, 100, H - mb, mt)
    series = [("oficial", COR["s1"], "IVS 2010 oficial do município"), ("local", COR["s2"], rot_local)]
    o = [svg_abrir(W, H, "Primeiro estágio: percentual com a bolsa maior por bin, nos dois cortes")]
    o.append(legenda_svg([("ponto", cor, nm) for _, cor, nm in series], ml, 14, size=10.5))
    for i, c in enumerate(cortes):
        sub = pe[np.isclose(pe["corte_mil"], c * 1000)]
        left = ml + i * (pw + gap)
        right = left + pw
        lo, hi = sub["lo"].min(), sub["hi"].max()
        X = Linear(lo, hi, left, right)
        o.append(t_svg(left, mt - 24, f"Corte {br(c)}: % com bolsa ≥ {br_mil(sub['valor_min'].iloc[0])}",
                       cor=COR["ink"], peso=600, size=10.5))
        for t in (0, 25, 50, 75, 100):
            o.append(l_svg(left, Y(t), right, Y(t), COR["grid"]))
            o.append(t_svg(left - 6, Y(t) + 3.5, f"{t}%", anchor="end", size=9.5))
        for t in sorted(set(sub["lo"]).union(sub["hi"])):
            o.append(l_svg(X(t), H - mb, X(t), H - mb + 4, COR["axis"]))
            o.append(t_svg(X(t), H - mb + 15, br(t, 2), anchor="middle", size=9.5))
        o.append(l_svg(left, H - mb, right, H - mb, COR["axis"]))
        o.append(l_svg(X(c), mt - 6, X(c), H - mb, COR["ink2"], 1))
        o.append(t_svg(X(c), mt - 9, "corte", anchor="middle", size=9, cor=COR["ink2"]))
        for var, cor, nome in series:
            sv = sub[sub["var"] == var]
            for lado in (sv[sv["hi"] <= c + 1e-9], sv[sv["lo"] >= c - 1e-9]):
                pts = [(X((r.lo + r.hi) / 2), Y(r.pct)) for r in lado.itertuples() if finito(r.pct)]
                if len(pts) > 1:
                    dd = " ".join(f"{'M' if j == 0 else 'L'}{f2(a)},{f2(b)}" for j, (a, b) in enumerate(pts))
                    o.append(f'<path d="{dd}" fill="none" stroke="{cor}" stroke-width="2" stroke-linejoin="round" '
                             f'stroke-linecap="round"/>')
            for r in sv.itertuples():
                if finito(r.pct):
                    tt = f"{nome}, ({br(r.lo)}; {br(r.hi)}]: {r.k}/{r.n} = {br_pct(r.pct)}"
                    o.append(ponto(X((r.lo + r.hi) / 2), Y(r.pct), cor, r=4.5, titulo=tt))
    o.append(t_svg((ml + W - mr) / 2, H - 6, "Bin da variável (largura 0,020; o corte fica no bin à esquerda)",
                   anchor="middle", size=10))
    o.append("</svg>")
    return "".join(o)


def fig_rd_p1(ctx, paineis: list[dict]) -> str:
    W = 680
    ml, mr, gapx = 46, 12, 44
    pw = (W - ml - mr - gapx) / 2
    ph = 150
    top0 = 30
    row_h = 36 + ph + 22 + 18
    H = int(top0 + 2 * row_h + 4)
    ymin, ymax = 0.0, 1.0
    for p in paineis:  # o dominio cobre as retas, se sairem de [0, 1]
        a, b, tau, dd = p["beta"]
        hh = p["h_mil"] / 1000
        ymin = min(ymin, a - b * hh, a, a + tau, a + tau + (b + dd) * hh)
        ymax = max(ymax, a - b * hh, a, a + tau, a + tau + (b + dd) * hh)
    ymin, ymax = math.floor(ymin * 4) / 4, math.ceil(ymax * 4) / 4
    o = [svg_abrir(W, H, "Gráfico RD de P1: média do outcome por bin do IVS e retas locais lineares")]
    o.append(legenda_svg([("ponto", COR["s1"], "média no bin (dentro da janela principal)"),
                          ("ponto", COR["muted"], "média no bin (fora da janela)"),
                          ("linha", COR["s1"], f"reta local linear (h = {br(ctx['h_principal'], 3)})")],
                         ml, 14, size=10))
    linhas_outcome = [OUTCOME_FRAC, OUTCOME_D]
    for ri, outcome in enumerate(linhas_outcome):
        top = top0 + ri * row_h
        o.append(t_svg(ml - 40, top + 13, maiuscula(rotulo_outcome(ctx, outcome)) + " (ciclo 1)",
                       cor=COR["ink"], peso=650, size=10.5))
        for ci, p in enumerate([q for q in paineis if q["outcome"] == outcome]):
            left = ml + ci * (pw + gapx)
            right = left + pw
            ptop = top + 36
            base = ptop + ph
            c, c_m, h_mil = p["corte"], p["c_mil"], p["h_mil"]
            hh = h_mil / 1000
            X = Linear(c - ALCANCE_RD_MIL / 1000, c + ALCANCE_RD_MIL / 1000, left, right)
            Y = Linear(ymin, ymax, base, ptop)
            o.append(t_svg(left, top + 29, f"corte {br(c)} · salto {pp(p['tau'])} p.p. "
                                           f"{ic_pp(p['ic_inf'], p['ic_sup'])}",
                           size=9.8, cor=COR["ink2"]))
            o.append(f'<rect x="{f2(X(c - hh))}" y="{f2(ptop)}" width="{f2(X(c + hh) - X(c - hh))}" '
                     f'height="{f2(ph)}" fill="{COR["wash"]}"/>')
            for t in np.arange(ymin, ymax + 1e-9, 0.25):
                o.append(l_svg(left, Y(t), right, Y(t), COR["grid"]))
                o.append(t_svg(left - 6, Y(t) + 3.5, f"{int(round(t * 100))}%", anchor="end", size=9))
            for k in range(-2, 3):
                t = c + k * 0.04
                o.append(l_svg(X(t), base, X(t), base + 4, COR["axis"]))
                o.append(t_svg(X(t), base + 15, br(t, 2), anchor="middle", size=9.5))
            o.append(l_svg(left, base, right, base, COR["axis"]))
            o.append(l_svg(X(c), ptop, X(c), base, COR["ink2"], 1))
            a, b, tau, dd = p["beta"]
            o.append(l_svg(X(c - hh), Y(a - b * hh), X(c), Y(a), COR["s1"], 2, extra='stroke-linecap="round"'))
            o.append(l_svg(X(c), Y(a + tau), X(c + hh), Y(a + tau + (b + dd) * hh), COR["s1"], 2,
                           extra='stroke-linecap="round"'))
            for b_ in p["bins"]:
                if not b_["n"]:
                    continue
                cor = COR["s1"] if b_["dentro"] else COR["muted"]
                xm = (b_["lo"] + b_["hi"]) / 2000
                tt = (f"({br(b_['lo'] / 1000)}; {br(b_['hi'] / 1000)}]: n = {b_['n']}, "
                      f"média = {pct(b_['media'])}")
                o.append(ponto(X(xm), Y(b_["media"]), cor, r=4, titulo=tt))
            # salto estimado no corte
            o.append(l_svg(X(c), Y(a), X(c), Y(a + tau), COR["ink"], 1.6))
            for yy in (Y(a), Y(a + tau)):
                o.append(l_svg(X(c) - 3.5, yy, X(c) + 3.5, yy, COR["ink"], 1.6))
    o.append("</svg>")
    return "".join(o)


def fig_forest_e3(ctx) -> str:
    d = ordenar_est(ctx["est"], ctx["h_principal"])
    lims = np.concatenate([d["ic95_inf"].to_numpy(float), d["ic95_sup"].to_numpy(float)]) * 100
    m = max(20.0, math.ceil(np.nanmax(np.abs(lims)) / 20) * 20)
    W = 680
    lab_w, val_w = 214, 132
    pl, pr = lab_w + 10, W - val_w
    X = Linear(-m, m, pl, pr)
    RH, GH = 15, 22
    linhas = []
    y = 30
    for (pop, outcome), g in d.groupby(["populacao", "outcome"], sort=False):
        linhas.append(("grupo", y, f"{rotulo_pop(ctx, pop)} · {rotulo_outcome(ctx, outcome, curto=True)}"))
        y += GH - 6
        for r in g.itertuples():
            linhas.append(("linha", y, r))
            y += RH
        y += 6
    base = y - 2
    H = int(base + 36)
    o = [svg_abrir(W, H, "Saltos estimados com IC 95%, todas as especificações do E3")]
    top = 22
    for t in np.arange(-m, m + 1e-9, 20):
        o.append(l_svg(X(t), top, X(t), base, COR["grid"]))
        o.append(t_svg(X(t), base + 14, sinal(t, 0), anchor="middle", size=9.5))
    o.append(l_svg(X(0), top, X(0), base, COR["ink"], 1.2))
    o.append(l_svg(pl, base, pr, base, COR["axis"]))
    o.append(t_svg((pl + pr) / 2, base + 30, "Salto no corte (pontos percentuais); 0 = sem diferença",
                   anchor="middle", size=10))
    o.append(t_svg(W - 4, 12, "salto [IC 95%], p.p.", anchor="end", size=9.5, cor=COR["muted"]))
    o.append(t_svg(4, 12, "Especificação", size=9.5, cor=COR["muted"]))
    for tipo, yy, r in linhas:
        if tipo == "grupo":
            o.append(t_svg(4, yy + 4, r, size=10.5, cor=COR["ink"], peso=600))
            continue
        princ = r.especificacao == "principal"
        cor = COR["s1"] if princ else COR["ink2"]
        rot = f"c = {br(r.corte)} · h = {br(r.h)}" + (" (principal)" if princ else "")
        o.append(t_svg(14, yy + 3.5, rot, size=9.5, cor=COR["ink"] if princ else COR["ink2"],
                       peso=600 if princ else None))
        a, z = X(max(r.ic95_inf * 100, -m)), X(min(r.ic95_sup * 100, m))
        o.append(l_svg(a, yy, z, yy, cor, 2, extra='stroke-linecap="round"'))
        tt = (f"{r.populacao}, {r.outcome}, c = {br(r.corte)}, h = {br(r.h)}: {pp(r.tau)} p.p. "
              f"{ic_pp(r.ic95_inf, r.ic95_sup)}, p = {br_p(r.p_valor)}")
        o.append(ponto(X(r.tau * 100), yy, cor, r=4, titulo=tt))
        o.append(t_svg(W - 4, yy + 3.5, f"{pp(r.tau)} {ic_pp(r.ic95_inf, r.ic95_sup)}", anchor="end", size=9.5,
                       extra='font-variant-numeric="tabular-nums"'))
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Numeros derivados para o texto
# ---------------------------------------------------------------------------


def numeros_regra(ctx) -> dict:
    base, c_mil, faixas = ctx["base"], ctx["c_mil"], ctx["faixas"]
    p1 = populacao(base, "P1")
    p1_loc = p1[p1["s_mil_local"].notna()]
    adm = ler_csv(ESCORE_ADMIN, dtype={"co_ibge": str})
    adm_iguais = adm_n = None
    if adm is not None:
        j = adm.assign(s_adm=milesimos(adm["ivs_admin"])).merge(ctx["of"][["co_ibge", "s_mil"]], on="co_ibge",
                                                                  how="left")
        adm_n, adm_iguais = len(j), int((j["s_adm"] == j["s_mil"]).sum())
    jl = ctx["of"][["co_ibge", "ivs", "s_mil"]].merge(ctx["loc"], on="co_ibge", how="inner")
    return {
        "p1_n": len(p1),
        "p1_rep_local": int((p1_loc["faixa_local"] == p1_loc["faixa_anunciada"]).sum()),
        "p1_n_local": len(p1_loc),
        "adm_n": adm_n, "adm_iguais": adm_iguais,
        "loc_n": len(jl),
        "loc_corr": float(jl[["ivs", "ivs_local"]].corr().iloc[0, 1]),
        "loc_iguais": int((jl["s_mil"] == jl["s_mil_local"]).sum()),
        "loc_faixa_dif": int(sum(faixa_pelo_valor(a, c_mil, faixas) != faixa_pelo_valor(b, c_mil, faixas)
                                 for a, b in zip(jl["s_mil"], jl["s_mil_local"]))),
    }


def cruzamento_grade(ctx) -> dict | None:
    """Ciclo 1: faixa reproduzida por variavel (arquivo local, IVS oficial) x grade (FAQ do edital, aplicada).

    "acima" = a faixa anunciada paga mais do que a grade manda; "abaixo" = paga menos.
    """
    tax = (ctx["a01b"].get("regra_de_limiar") or {}).get("taxonomia_atlas") or {}
    cortes_faq = tax.get("cortes") or []
    if len(cortes_faq) != 2:
        return None
    c_faq = [int(round(float(c) * 1000)) for c in cortes_faq]
    d = ctx["base"][ctx["base"]["quadro"] == QUADRO_PRIMEIRO_ESTAGIO].drop_duplicates("co_ibge")
    ordem = {f: i for i, f in enumerate(ctx["faixas"])}  # ordem crescente de valor
    an = d["faixa_anunciada"].map(ordem).to_numpy()
    res = {"c_faq": c_faq, "n": len(d)}
    for var, col in (("local", "s_mil_local"), ("oficial", "s_mil")):
        for grade, cm in (("faq", c_faq), ("aplicada", ctx["c_mil"])):
            g = [faixa_pelo_valor(m, cm, ctx["faixas"]) for m in d[col]]
            ok = np.array([x is not None for x in g])
            gg = np.array([ordem.get(x, -1) for x in g])
            res[(var, grade)] = {"n": int(ok.sum()), "rep": int(((an == gg) & ok).sum()),
                                 "acima": int(((an > gg) & ok).sum()), "abaixo": int(((an < gg) & ok).sum())}
    # conferencia contra o diagnostico antigo (arquivo local + grade do FAQ)
    piso = (ctx["a01b"].get("ivs_e_piso_e_nunca_teto") or {}).get("municipios_acima_da_categoria_do_edital")
    res["confere_a01b"] = (res[("local", "faq")]["rep"] == tax.get("acertos")
                           and res[("local", "faq")]["acima"] == piso)
    return res


def categorias_ivs(ctx) -> tuple[pd.DataFrame | None, dict]:
    cat = ler_csv(CATEGORIA, dtype={"co_ibge": str})
    if cat is None:
        return None, {}
    j = cat.dropna(subset=["categoria_ivs_admin"]).merge(ctx["of"][["co_ibge", "ivs", "s_mil"]], on="co_ibge",
                                                         how="inner")
    g = (j.groupby("categoria_ivs_admin")
         .agg(n=("co_ibge", "size"), s_min=("s_mil", "min"), s_max=("s_mil", "max"))
         .sort_values("s_min").reset_index())
    sep = all(g["s_max"].iloc[i] < g["s_min"].iloc[i + 1] for i in range(len(g) - 1))
    fronteiras = [(int(g["s_max"].iloc[i]), int(g["s_min"].iloc[i + 1])) for i in range(len(g) - 1)]
    nos_cortes = all(any(a == c and b == c + 1 for a, b in fronteiras) for c in ctx["c_mil"])
    return g, {"separadas": sep, "nos_cortes": nos_cortes, "n": int(g["n"].sum()), "fronteiras": fronteiras}


def balanco_principal(ctx) -> pd.DataFrame:
    d = ctx["diag"]
    b = d[(d["diagnostico"] == "balanco_covariavel_pre") & np.isclose(d["h"], ctx["h_principal"])]
    return b[b["variavel"] != COVARIAVEL_RUNNING].copy()


def numeros_e3(ctx) -> dict:
    est, diag = ctx["est"], ctx["diag"]
    pr = principais(ctx)
    larg = (pr["ic95_sup"] - pr["ic95_inf"]) * 100
    mde = MDE_FATOR * pr["ep"] * 100
    dens = diag[diag["diagnostico"] == "densidade_poisson_mass_points"]
    dens_p = dens[np.isclose(dens["h"], ctx["h_principal"])]
    bal = balanco_principal(ctx)
    sig = bal[bal["p_valor"] < ALFA]
    return {
        "pr": pr,
        "n_espec": len(est),
        "n_sig": int((est["p_valor"] < ALFA).sum()),
        "p_min": float(est["p_valor"].min()),
        "larg_min": float(larg.min()), "larg_max": float(larg.max()),
        "mde_min": float(mde.min()), "mde_max": float(mde.max()),
        "dens": dens, "dens_p": dens_p,
        "dens_todos_contem_1": bool(((dens["rho_ic95_inf"] <= 1) & (dens["rho_ic95_sup"] >= 1)).all()),
        "rho_min": float(dens_p["rho"].min()), "rho_max": float(dens_p["rho"].max()),
        "bal": bal, "bal_sig": sig, "bal_n": len(bal),
    }


def rotulo_cov(v: str) -> str:
    return ROTULO_COV.get(v, (v.replace("_", " "), 3))[0]


def nd_cov(v: str) -> int:
    return ROTULO_COV.get(v, (v, 3))[1]


# ---------------------------------------------------------------------------
# Secoes
# ---------------------------------------------------------------------------


def secao_capa(ctx) -> str:
    commit, sujo, agora = ctx["commit"], ctx["sujo"], ctx["agora"]
    prot, adendo, st, r1 = ctx["prot"], ctx["adendo"], ctx["st"], ctx["r1"]
    meta = [
        ("Gerado em", agora.strftime("%d/%m/%Y %H:%M")),
        ("Commit", f"<code>{esc(commit)}</code>" + (" (árvore de trabalho com alterações não commitadas)" if sujo else "")),
        ("Script", f"<code>{esc(rel(ESTE_SCRIPT))}</code>"),
        ("Protocolo congelado em", f"{data_br(prot.get('data_congelamento'))} (<code>{esc(rel(PROTOCOLO))}</code>)"),
    ]
    if adendo:
        meta.append(("Adendo E4 congelado em",
                     f"{data_br(adendo.get('data_congelamento'))} (<code>{esc(rel(ADENDO_E4))}</code>)"))
    dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in meta)
    eq = r1.get("escore_administrativo_e_ivs_2010_oficial") or {}
    itens = [
        ("Regra (R1 com o IVS 2010 oficial)", "pill-ok", str(r1.get("decisao_r1", "—")).replace("_", " "),
         f"escore administrativo = IVS 2010 oficial ({esc(eq.get('valores_iguais_3_casas', '—'))} valores; "
         f"{esc(eq.get('categorias_iguais', '—'))} categorias)"),
        ("E3 — RDD sharp com escore completo", "pill-ok", str(st.get("status", "—")).replace("_", " "),
         "análise principal"),
        ("E4 — limites para a proporção preenchida", "pill-hist", "histórico",
         "exploratório, com escore parcial; superado pelo E3" if E4_EST.exists() else "ausente"),
        ("E1 e E2 — densidade e limites para a presença", "pill-hist", "histórico",
         "exploratórios, com escore parcial; superados pelo E3" if (E1_EST.exists() and E2_LIM.exists())
         else "ausente"),
    ]
    stt = "".join(f'<tr><td>{a}</td><td><span class="pill {b}">{esc(c)}</span></td><td>{d}</td></tr>'
                  for a, b, c, d in itens)
    sumario = "".join(f"<li>{s}</li>" for s in [
        "Resumo em 1 página",
        "1. A regra: IVS 2010 oficial, cortes 0,300 e 0,400",
        "2. RDD sharp com o escore completo (E3)",
        "3. Antes do escore completo: E1, E2 e E4 (exploratórios)",
        "4. Leitura e limites",
        "Apêndice A — dados do gráfico RD",
        "Apêndice B — proveniência das entradas",
    ])
    return f"""
<section class="capa">
  <div class="kicker">Programa Mais Médicos Especialistas · adicional de bolsa por faixa de IVS</div>
  <h1>{esc(TITULO)}</h1>
  <p class="lead">A bolsa anunciada é atribuída pelo IVS 2010 oficial do Ipea, com dois cortes. Este relatório
  reconstrói a regra, apresenta a RDD sharp com o escore completo (E3) e resume as análises exploratórias
  anteriores. É a base para montar os slides: todo número e gráfico é lido de <code>output/</code> por script
  versionado.</p>
  <dl class="meta">{dl}</dl>
  <div class="aviso"><strong>Como ler.</strong> O E3 dá uma <strong>estimativa local do efeito do anúncio de
  +R$ 5 mil</strong> por mês, sob as premissas da RDD, para municípios do quadro de vagas com IVS perto dos
  cortes. Não identifica a participação no PMM-E nem o efeito total do Agora Tem Especialistas, e pode medir um
  pacote se outra política mudar nos mesmos cortes. E1, E2 e E4 foram feitos quando só havia escore para parte
  dos municípios: são exploratórios e ficam como histórico.</div>
  <h3>Situação das entradas</h3>
  <table class="status"><thead><tr><th>Etapa</th><th>Situação</th><th>Detalhe</th></tr></thead>
  <tbody>{stt}</tbody></table>
  <h3>Conteúdo</h3>
  <ol class="sumario">{sumario}</ol>
</section>
"""


def lista_covs_sig(sig: pd.DataFrame) -> str:
    return "; ".join(f"{esc(rotulo_cov(r.variavel))} ({sinal(r.tau, nd_cov(r.variavel))}; p = {br_p(r.p_valor)})"
                     for r in sig.itertuples())


def tabela_principais(ctx, nums, compacta: bool = False, titulo: str = "") -> str:
    pr = nums["pr"]
    linhas = []
    for r in pr.itertuples():
        lin = [f"{esc(rotulo_pop(ctx, r.populacao, curto=True))} · {esc(rotulo_outcome(ctx, r.outcome, True))}",
               br(r.corte), f"{br_int(r.n_abaixo)} / {br_int(r.n_acima)}"]
        if not compacta:
            lin.append(f"{pct(r.media_bruta_abaixo)} → {pct(r.media_bruta_acima)}")
        lin += [f"<strong>{pp(r.tau)}</strong>", ic_pp(r.ic95_inf, r.ic95_sup), br_p(r.p_valor),
                br(MDE_FATOR * r.ep * 100, 0)]
        linhas.append(lin)
    cab = [("População · outcome", "txt"), ("Corte", "num"), ("n abaixo / acima", "num")]
    if not compacta:
        cab.append(("Média bruta<br><span class=\"muted\">abaixo → acima</span>", "num"))
    cab += [("Salto (p.p.)", "num"), ("IC 95% (p.p.)", "num"), ("p", "num"),
            ("MDE (p.p.)<br><span class=\"muted\">2,8 × EP</span>", "num")]
    rod = (f'<div class="fonte">Fonte: <code>{esc(rel(E3_EST))}</code> ({origem_html(E3_EST)}). Local linear, '
           f"kernel triangular, h = {br(ctx['h_principal'], 3)}, EP HC1 por município. MDE = efeito mínimo "
           "detectável aproximado (80% de poder, 5% bicaudal), calculado aqui como 2,8 × EP.</div>")
    return tabela(cab, linhas, classe="compacta" if compacta else "", titulo=titulo, rodape=rod)


def secao_resumo(ctx) -> str:
    r1, a01b, st = ctx["r1"], ctx["a01b"], ctx["st"]
    nr, ne = ctx["n_regra"], ctx["n_e3"]
    vf, fx, cortes = ctx["valor_faixa"], ctx["faixas"], ctx["cortes"]
    eq = r1.get("escore_administrativo_e_ivs_2010_oficial") or {}
    pops = r1.get("populacoes") or {}
    pe = st.get("primeiro_estagio") or {}

    def rep(p):
        v = pops.get(p, {})
        return f"{br_int(v.get('regra_reproduz'))}/{br_int(v.get('municipios'))}"

    a = (f"<li><strong>A bolsa é atribuída pelo IVS 2010 oficial do Ipea, com cortes {br(cortes[0])} e "
         f"{br(cortes[1])}.</strong> Até {br(cortes[0])}: {br_mil(vf[fx[0]])}; de {br(cortes[0] + 0.001)} a "
         f"{br(cortes[1])}: {br_mil(vf[fx[1]])}; acima de {br(cortes[1])}: {br_mil(vf[fx[2]])}. São "
         f"+{br_mil(vf[fx[1]] - vf[fx[0]])} em cada corte, e o próprio corte fica no lado de baixo. O escore "
         f"administrativo do MS <em>é</em> o IVS 2010 oficial ({esc(eq.get('valores_iguais_3_casas', '—'))} valores "
         f"iguais a 3 casas; {esc(eq.get('categorias_iguais', '—'))} categorias). A regra reproduz a faixa "
         f"anunciada em {rep('P1')} municípios do ciclo 1 e {rep('P2')} do ciclo 2: primeiro estágio "
         f"{'sharp' if all((pe.get(p) or {}).get('sharp') for p in ('P1', 'P2')) else 'não sharp'}, de 0% a 100% "
         "em cada corte.</li>")

    loc = r1.get("arquivo_local_ivs_2010") or {}
    rl, cz = ctx["rl"], ctx["cruz"]
    piso = (a01b.get("ivs_e_piso_e_nunca_teto") or {}).get("municipios_acima_da_categoria_do_edital")
    mp = (a01b.get("regra_de_limiar") or {}).get("melhor_possivel") or {}
    quem = (f"é, em cada município, a última linha de subgrupo com IVS preenchido da mesma base — "
            f"<strong>{esc(rl['frase'])}</strong> em {br_int(rl['n_princ'])} de {br_int(rl['n_mun'])} municípios "
            f"({br(rl['share'], 1)}%), outros recortes de mulheres no resto —, e não o IVS do município (a regra "
            f"reproduz as 7 colunas do arquivo em {br_int(rl['n_mun'])}/{br_int(rl['n_mun'])} municípios)"
            if rl["ok"] else "não reproduz o IVS do município")
    pop = (f"; sua população ({br_milhoes(rl['soma_pop'])} no total) é a desses subgrupos" if rl["ok"] else "")
    grade = ""
    if cz:
        lf, of_ = cz[("local", "faq")], cz[("oficial", "faq")]
        grade = (f" O “IVS é piso” ({br_int(piso)} municípios “acima da categoria”, {br_int(lf['abaixo'])} abaixo) vinha "
                 f"sobretudo da grade do FAQ do edital (cortes {br(cz['c_faq'][0] / 1000)} e {br(cz['c_faq'][1] / 1000)}), "
                 f"que dá o mesmo padrão com o IVS oficial ({br_int(of_['acima'])} acima, {br_int(of_['abaixo'])} "
                 "abaixo).")
    b = (f"<li><strong>O “IVS 2010” usado até aqui era a linha errada da base do Ipea.</strong> O arquivo local "
         f"(<code>{esc(loc.get('arquivo', rel(IVS_LOCAL)))}</code>) {quem}: contra o IVS do município, a correlação é "
         f"{br(loc.get('correlacao_com_oficial'), 3)} e só {br_pct(loc.get('pct_iguais_3_casas'))} dos valores "
         f"coincidem{pop}. Com ele, nenhum par de cortes reproduzia mais que "
         f"{br_pct(100 * mp.get('acertos', np.nan) / mp.get('n', np.nan))} das faixas "
         f"({br_int(mp.get('acertos'))}/{br_int(mp.get('n'))}): era a “falsa” impossibilidade da RDD.{grade} Com o "
         f"IVS oficial e a grade aplicada: {rep('P1')} no ciclo 1.</li>")

    pr = ne["pr"]

    def tau_de(pop, outcome):
        g = pr[(pr["populacao"] == pop) & (pr["outcome"] == outcome)].sort_values("corte")
        return " e ".join(f"{pp(r.tau)} p.p. em {br(r.corte)}" for r in g.itertuples())

    c = (f"<li><strong>RDD sharp com o escore completo (E3): nenhum salto distinguível de zero.</strong> Na "
         f"especificação principal (local linear, h = {br(ctx['h_principal'], 3)}), "
         f"{'nenhuma' if not (pr['p_valor'] < ALFA).any() else 'nem todas'} das {len(pr)} estimativas tem p &lt; "
         f"0,05: proporção de células preenchidas na 1ª chamada do ciclo 1, {tau_de('P1', OUTCOME_FRAC)}; "
         f"presença de especialista do ciclo 1, {tau_de('P1', OUTCOME_D)}; replicação no ciclo 2, "
         f"{tau_de('P2', OUTCOME_D)}. Os IC 95% têm de {br(ne['larg_min'], 0)} a {br(ne['larg_max'], 0)} p.p. de "
         f"largura e o efeito mínimo detectável (2,8 × EP) vai de {br(ne['mde_min'], 0)} a {br(ne['mde_max'], 0)} "
         f"p.p. Nas {ne['n_espec']} especificações, com as janelas de sensibilidade, o menor p é "
         f"{br_p(ne['p_min'])}. <strong>Leitura: inconclusivo.</strong> Não detectamos efeito; com poder baixo, os "
         "intervalos não excluem efeitos grandes em nenhuma direção.</li>")

    sig = ne["bal_sig"]
    focos = sig.groupby(["populacao", "corte"]).size().sort_values(ascending=False)
    foco_txt, resto_txt = "", ""
    if len(focos):
        (fp, fc) = focos.index[0]
        sf = sig[(sig["populacao"] == fp) & np.isclose(sig["corte"], fc)]
        foco_txt = (f" {br_int(len(sf))} deles no corte {br(fc)} do {rotulo_pop(ctx, fp, curto=True).lower()}: "
                    f"{lista_covs_sig(sf)}.")
        outros = sig.drop(sf.index)
        if len(outros):
            resto_txt = " Fora desse corte: " + "; ".join(
                f"{lista_covs_sig(g)} no corte {br(k[1])} do {rotulo_pop(ctx, k[0], curto=True).lower()}"
                for k, g in outros.groupby(["populacao", "corte"])) + "."
        foco_txt += resto_txt + f" Cautela com o corte {br(fc)} do {rotulo_pop(ctx, fp, curto=True).lower()}."
    d = (f"<li><strong>Diagnósticos.</strong> A densidade do IVS entre os municípios do quadro não salta nos cortes: "
         f"ρ de {br(ne['rho_min'], 2)} a {br(ne['rho_max'], 2)} na janela principal, e "
         f"{'todos' if ne['dens_todos_contem_1'] else 'nem todos'} os {len(ne['dens'])} IC 95% contêm 1. No balanço "
         f"de covariáveis pré-programa (h = {br(ctx['h_principal'], 3)}), {br_int(len(sig))} de {br_int(ne['bal_n'])} "
         f"testes têm p &lt; 0,05 (seriam {br(ALFA * ne['bal_n'], 1)} por acaso).{foco_txt}</li>")

    dizer = (
        '<div class="dizer"><strong>Como dizer nos slides.</strong><ul>'
        "<li>“Estimativa local do efeito do anúncio de +R$ 5 mil, sob as premissas da RDD, para municípios do "
        "quadro com IVS perto dos cortes.”</li>"
        "<li>“Não detectamos efeito; os intervalos não excluem efeitos grandes em nenhuma direção.”</li>"
        "<li>Evitar: “a bolsa não funciona”, “efeito nulo”, “a bolsa não atrai”. Não é o efeito de participar do "
        "PMM-E nem do Agora Tem Especialistas.</li></ul></div>"
    )
    return ('<section class="resumo"><h2>Resumo em 1 página</h2>'
            f'<ul class="resumo-lista">{a}{b}{c}{d}</ul>'
            + tabela_principais(ctx, ne, compacta=True, titulo="Estimativas principais do E3")
            + dizer + "</section>")


def secao_regra(ctx) -> str:
    r1, r1_adm, nr = ctx["r1"], ctx["r1_adm"], ctx["n_regra"]
    base, cortes, c_mil, faixas, vf = ctx["base"], ctx["cortes"], ctx["c_mil"], ctx["faixas"], ctx["valor_faixa"]
    manif = ctx["manif"]
    rl = ctx["rl"]
    o = ['<section class="quebra"><h2>1. A regra: IVS 2010 oficial, cortes 0,300 e 0,400</h2>']
    fonte_m = manif.get("fonte") or {}
    o.append(
        f"<p>A faixa da bolsa anunciada em cada quadro de vagas é função do <strong>IVS 2010 oficial do município"
        f"</strong> ({esc(fonte_m.get('orgao', 'Ipea'))}; {esc(fonte_m.get('descricao', 'base completa da Plataforma IVS'))}; "
        f"recorte: {esc(manif.get('recorte', '—'))}; {br_int((manif.get('saida') or {}).get('municipios'))} "
        f"municípios). Esse IVS é o próprio escore administrativo publicado pelo MS. Há dois cortes: "
        f"<strong>{br(cortes[0])}</strong> ({fx_txt(faixas, 0)}, +{br_mil(vf[faixas[1]] - vf[faixas[0]])}) e "
        f"<strong>{br(cortes[1])}</strong> ({fx_txt(faixas, 1)}, +{br_mil(vf[faixas[2]] - vf[faixas[1]])}). O próprio "
        "corte pertence ao lado inferior.</p>")

    # Tabela: o escore administrativo, o IVS do municipio e o arquivo local
    eq = r1.get("escore_administrativo_e_ivs_2010_oficial") or {}
    loc = r1.get("arquivo_local_ivs_2010") or {}
    g_cat, info_cat = ctx["categorias"]
    lin = [
        ["Escore <code>ivs</code> da relação nominal do PMM-E (MS) igual ao IVS oficial do município, a 3 casas",
         esc(eq.get("valores_iguais_3_casas", "—")),
         f"{br_int(nr['adm_iguais'])}/{br_int(nr['adm_n'])}" if nr["adm_n"] else "—"],
        ["Categoria de IVS do consolidado PMMB (MS) igual à classe do IVS oficial do município",
         esc(eq.get("categorias_iguais", "—")),
         ("classes sem sobreposição no IVS oficial" if info_cat.get("separadas") else "classes sobrepostas")
         if g_cat is not None else "—"],
    ]
    if rl["ok"]:
        lin += [
            ["Arquivo local reproduzido pela regra “última linha com IVS preenchido de cada município” "
             "(7 colunas)", f"{br_int(rl['n_mun'])}/{br_int(rl['n_mun'])} municípios", "—"],
            [f"Municípios em que a linha escolhida é <em>{esc(rl['recorte'])}</em>",
             f"{br_int(rl['n_princ'])}/{br_int(rl['n_mun'])} ({br(rl['share'], 1)}%)", "—"],
        ]
    lin += [
        [f"Arquivo local igual ao IVS do município (linha <em>{esc(rl.get('total', 'Total'))}</em>), a 3 casas",
         br_pct(loc.get("pct_iguais_3_casas")),
         f"{br_pct(100 * nr['loc_iguais'] / nr['loc_n'])} ({br_int(nr['loc_iguais'])}/{br_int(nr['loc_n'])})"],
        ["Arquivo local: correlação com o IVS do município", br(loc.get("correlacao_com_oficial"), 3),
         br(nr["loc_corr"], 3)],
        ["Arquivo local: municípios em outra faixa pelos cortes da bolsa", "—",
         f"{br_int(nr['loc_faixa_dif'])}/{br_int(nr['loc_n'])} ({br_pct(100 * nr['loc_faixa_dif'] / nr['loc_n'])})"],
    ]
    o.append(tabela(
        [("Comparação", "txt"), ("Registrado (R1 e identificação)", "num"), ("Conferido aqui", "num")], lin,
        titulo=("O escore administrativo é o IVS 2010 do município; o arquivo local é uma linha de subgrupo"
                if rl["ok"] else "O escore administrativo é o IVS 2010 do município; o arquivo local não é"),
        rodape=fonte_html(R1_OFICIAL, IDENT_LOCAL, ESCORE_ADMIN, CATEGORIA, IVS_OFICIAL, IVS_LOCAL, grafico=False,
                          extra=("“Conferido aqui” recalcula a partir dos arquivos; as linhas por recorte exigem a base "
                                 "completa do Ipea e ficam como registradas pela identificação")),
    ))
    if rl["ok"]:
        o.append(
            "<p><strong>O que é o arquivo local.</strong> Não é um arquivo inventado nem de outra fonte: é a base "
            "oficial do Ipea, mas a linha errada de cada município. A base traz uma linha por combinação de cor, sexo e "
            f"situação de domicílio, e o IVS do município é a linha <em>{esc(rl['total'])}</em>. O arquivo é "
            f"reproduzido exatamente — nas 7 colunas e nos {br_int(rl['n_mun'])} municípios — pela regra: "
            f"{esc(rl['mecanismo'])}. A última linha da planilha é <em>{esc(rl['recorte'])}</em>; quando ela vem "
            f"vazia na base ({br_int(rl['n_vazio'])} municípios) ou não existe ({br_int(rl['n_sem'])}), a regra recua "
            f"para a linha anterior preenchida. Resultado: {esc(rl['dist'])}. "
            f"É também por isso que a população do arquivo é baixa: a coluna soma {br_milhoes(rl['soma_pop'])}, "
            f"contra {br_milhoes(rl['pop_br'])} no Censo 2010"
            + (", que é exatamente a soma da linha total da base" if rl.get("pop_total_ok") else "")
            + f". Neste relatório ele aparece como “{esc(rl['longo'])}”.</p>")

    cz = ctx["cruz"]
    if cz:
        def cel(k):
            v = cz[k]
            return (f"<strong>{br_int(v['rep'])}</strong>/{br_int(v['n'])} "
                    f"<span class=\"muted\">({br_int(v['acima'])} acima; {br_int(v['abaixo'])} abaixo)</span>")
        cab_faq = f"Grade do FAQ do edital<br><span class=\"muted\">cortes {br(cz['c_faq'][0] / 1000)} e {br(cz['c_faq'][1] / 1000)}</span>"
        cab_apl = f"Grade aplicada<br><span class=\"muted\">cortes {br(cortes[0])} e {br(cortes[1])}</span>"
        o.append(tabela(
            [("Variável", "txt"), (cab_faq, "num"), (cab_apl, "num")],
            [[esc(maiuscula(rl["curto"])), cel(("local", "faq")), cel(("local", "aplicada"))],
             ["IVS 2010 oficial do município", cel(("oficial", "faq")), cel(("oficial", "aplicada"))]],
            titulo=f"Dois erros no diagnóstico antigo: faixas reproduzidas no {nome_quadro(QUADRO_PRIMEIRO_ESTAGIO).lower()}",
            rodape=(f'<p class="nota">“acima” = a faixa anunciada paga mais do que a grade manda; “abaixo” = paga menos. '
                    "O diagnóstico antigo usava a linha de cima com a grade do FAQ"
                    + (" (os números coincidem com <code>" + esc(rel(A01B)) + "</code>)" if cz["confere_a01b"] else
                       " (<span class=\"alerta\">não coincide com " + esc(rel(A01B)) + "</span>)")
                    + ". A grade errada, sozinha, produz o padrão “IVS é piso” (só erros para cima). O arquivo local, "
                      "sozinho, erra nos dois sentidos e esconde a regra. Só o IVS oficial com a grade aplicada reproduz "
                      "todas as faixas.</p>"
                    + fonte_html(MATRIZ, IVS_OFICIAL, IVS_LOCAL, A01B, grafico=False,
                                 extra="Cortes da grade do FAQ lidos do diagnóstico antigo")),
        ))

    # Tabela: reproducao por quadro
    refs = r1_adm.get("quadros") or {}
    linhas = []
    for q, g in base.groupby("quadro", sort=False):
        g = g.drop_duplicates("co_ibge")
        com = g[g["s_mil"].notna()]
        coml = g[g["s_mil_local"].notna()]
        rep_of = int((com["faixa_oficial"] == com["faixa_anunciada"]).sum())
        rep_lo = int((coml["faixa_local"] == coml["faixa_anunciada"]).sum())
        linhas.append([
            esc(nome_quadro(q)) + f' <span class="muted">({esc(q)})</span>',
            esc((refs.get(q) or {}).get("referencia", "—")),
            br_int(len(g)), br_int(len(com)),
            f"<strong>{br_int(rep_of)}</strong> ({br_pct(100 * rep_of / len(com) if len(com) else np.nan)})",
            f"{br_int(rep_lo)} ({br_pct(100 * rep_lo / len(coml) if len(coml) else np.nan)})",
        ])
    diverg = ctx["divergencias_pop"]
    conf = ("<span class=\"alerta\">Divergência: " + "; ".join(esc(x) for x in diverg) + "</span>") if diverg else (
        f"Conferência: as contagens por população (P1 = c1_ch1; P2 = c2_ch1 ∪ c2_ch2; ciclo 3 = c3_ch1) coincidem "
        f"com <code>{esc(rel(R1_OFICIAL))}</code> e com a cobertura registrada em <code>{esc(rel(E3_STATUS))}</code>.")
    sem = (r1.get("populacoes") or {}).get("ciclo_3_congelado", {}).get("sem_ivs_oficial") or []
    o.append(tabela(
        [("Quadro", "txt nowrap"), ("Referência", "txt"), ("Municípios", "num"), ("Com IVS oficial", "num"),
         ("Reproduzidos pelo IVS oficial", "num"),
         (f"Reproduzidos pelo arquivo local<br><span class=\"muted\">IVS de subgrupo, sobretudo {esc(rl.get('frase', '?'))}; mesmos "
          "cortes</span>", "num")],
        linhas,
        titulo="Reprodução da faixa anunciada, por quadro de vagas",
        rodape=f'<p class="nota">{conf} Município sem IVS 2010: {", ".join(f"<code>{esc(x)}</code>" for x in sem) or "nenhum"}'
               " (ciclo 3, criado depois de 2010). O ciclo 3 entra só na reconstrução da regra; está fora das "
               "estimações (prospectivo e congelado).</p>"
               + fonte_html(MATRIZ, IVS_OFICIAL, IVS_LOCAL, R1_ADMIN, grafico=False,
                            extra="Referência dos quadros registrada no R1 com escore parcial"),
    ))

    # Tabela: categoria administrativa x IVS oficial
    g, info = ctx["categorias"]
    if g is not None:
        lc = [[esc(str(r.categoria_ivs_admin).capitalize()), br_int(r.n), br(r.s_min / 1000),
               br(r.s_max / 1000)] for r in g.itertuples()]
        nota_cat = (f"As {len(g)} categorias não se sobrepõem no IVS oficial e mudam exatamente em "
                    + ", ".join(f"{br(a / 1000)}/{br(b / 1000)}" for a, b in info["fronteiras"])
                    + (f". Os dois cortes da bolsa ({br(cortes[0])} e {br(cortes[1])}) são fronteiras de categoria: "
                       "qualquer benefício que dependa da categoria de IVS muda nos mesmos pontos (ver seção 4, "
                       "“pacote”)." if info["nos_cortes"] else "."))
        o.append(tabela(
            [("Categoria de IVS (MS)", "txt"), ("Municípios", "num"), ("IVS oficial mín.", "num"),
             ("IVS oficial máx.", "num")], lc, classe="estreita",
            titulo="Categoria de IVS do MS contra o IVS 2010 oficial",
            rodape=f'<p class="nota">{nota_cat}</p>' + fonte_html(CATEGORIA, IVS_OFICIAL, grafico=False),
        ))

    # Lado do corte observado (todos os quadros)
    todos = base.drop_duplicates("co_ibge")
    todos = todos[todos["s_mil"].notna()]
    lados = []
    for f in faixas:
        sf = todos[todos["faixa_anunciada"] == f]["s_mil"]
        lados.append([esc(f.title()), br_int(len(sf)), br(sf.min() / 1000), br(sf.max() / 1000)])
    no_corte = []
    for c_m in c_mil:
        g_c = todos[todos["s_mil"] == c_m]
        cont = g_c["faixa_anunciada"].value_counts().sort_index()
        if not len(g_c):
            no_corte.append(f"nenhum município com IVS exatamente {br(c_m / 1000)}")
        elif len(cont) == 1:
            no_corte.append(f"os {br_int(len(g_c))} municípios com IVS exatamente {br(c_m / 1000)} estão na "
                            f"{esc(cont.index[0].title())}")
        else:
            no_corte.append(f"municípios com IVS exatamente {br(c_m / 1000)}: "
                            + ", ".join(f"{br_int(v)} na {esc(k.title())}" for k, v in cont.items()))
    o.append(tabela(
        [("Faixa anunciada", "txt"), ("Municípios", "num"), ("IVS oficial mín.", "num"), ("IVS oficial máx.", "num")],
        lados, classe="estreita", titulo="Lado do corte observado nos quatro quadros",
        rodape=f'<p class="nota">{maiuscula("; ".join(no_corte))}. Leitura: o corte pertence ao lado inferior.</p>'
               + fonte_html(MATRIZ, IVS_OFICIAL, grafico=False),
    ))

    # Figura: degraus
    d_all = todos.sort_values("co_ibge")
    fora = int((d_all["faixa_oficial"] != d_all["faixa_anunciada"]).sum())
    o.append(figura(
        "Valor mensal anunciado da bolsa contra o IVS 2010 oficial do município",
        fig_regra_degraus(d_all, cortes, faixas, vf),
        fonte_html(MATRIZ, IVS_OFICIAL, extra="Um ponto por município com IVS oficial em algum dos quatro quadros"),
        sub=f"{br_int(len(d_all))} municípios dos quatro quadros (ciclos 1 a 3); {br_int(fora)} fora da regra. Linha = "
            "regra de dois cortes. Deslocamento vertical aleatório (semente fixa) só para separar pontos sobrepostos.",
    ))

    # Figura: arquivo local x oficial (P1)
    p1 = populacao(base, "P1")
    p1 = p1[p1["s_mil_local"].notna()].copy()
    p1["concorda"] = p1["faixa_local"] == p1["faixa_oficial"]
    corr_p1 = float(p1[["ivs", "ivs_local"]].corr().iloc[0, 1])
    o.append(figura(
        f"{esc(maiuscula(rl['curto']))} contra o IVS 2010 oficial do município, ciclo 1",
        fig_local_vs_oficial(p1, cortes, rl),
        fonte_html(MATRIZ, IVS_OFICIAL, IVS_LOCAL),
        sub=(f"{br_int(len(p1))} municípios do quadro {esc(QUADRO_PRIMEIRO_ESTAGIO)} (P1). Correlação {br(corr_p1, 3)} "
             f"nesses municípios; {br_int(int((~p1['concorda']).sum()))} cairiam em outra faixa pelo arquivo local. "
             f"Na base inteira ({br_int(nr['loc_n'])} municípios): correlação {br(loc.get('correlacao_com_oficial'), 3)} "
             f"e {br_pct(loc.get('pct_iguais_3_casas'))} de valores iguais (R1). Os dois são o mesmo índice do Ipea "
             "para populações diferentes: o município inteiro e um subgrupo dele. Linhas escuras: cortes nos dois eixos; "
             "diagonal: 45°."),
    ))

    # Figura e tabela: primeiro estagio
    pe, n_q = dados_primeiro_estagio(ctx)
    o.append(figura(
        "Primeiro estágio: % de municípios com a bolsa maior, por bin, nos dois cortes",
        fig_primeiro_estagio(pe, cortes, rl["curto"]),
        fonte_html(MATRIZ, IVS_OFICIAL, IVS_LOCAL, extra=f"Quadro {QUADRO_PRIMEIRO_ESTAGIO}"),
        sub=(f"{nome_quadro(QUADRO_PRIMEIRO_ESTAGIO)}: {br_int(n_q)} municípios, todos com IVS oficial e com valor no "
             "arquivo local. Pelo IVS oficial do município, o salto é de 0% a 100% nos dois cortes; pelo arquivo local "
             f"(IVS de subgrupo, sobretudo {esc(rl.get('frase', '?'))}), é gradual — por isso a regra parecia não existir."),
    ))
    tl = []
    for (c_m, lo, hi), g in pe.groupby(["corte_mil", "lo", "hi"], sort=True):
        a_ = g[g["var"] == "oficial"].iloc[0]
        b_ = g[g["var"] == "local"].iloc[0]
        tl.append([br(c_m / 1000), f"({br(lo)}; {br(hi)}]", f"{br_int(a_.k)} / {br_int(a_.n)}", br_pct(a_.pct),
                   f"{br_int(b_.k)} / {br_int(b_.n)}", br_pct(b_.pct)])
    o.append(tabela(
        [("Corte", "num"), ("Bin", "txt"), ("IVS oficial: n", "num"), ("IVS oficial: %", "num"),
         ("Arquivo local: n", "num"), ("Arquivo local: %", "num")],
        tl, classe="compacta",
        titulo="Primeiro estágio em números (municípios com a bolsa maior / municípios no bin)",
        rodape=fonte_html(MATRIZ, IVS_OFICIAL, IVS_LOCAL, grafico=False,
                          extra=(f"Mesmos dados da figura anterior; arquivo local = IVS de subgrupo, sobretudo {esc(rl.get('frase', '?'))}; "
                                 "bolsa maior = acima do valor do lado de baixo do corte")),
    ))
    o.append("</section>")
    return "".join(o)


def fx_txt(faixas, i) -> str:
    return f"{faixas[i].title()} → {faixas[i + 1].title()}"


def secao_e3(ctx) -> str:
    st, prot, ne = ctx["st"], ctx["prot"], ctx["n_e3"]
    p3 = prot.get("E3_rdd_completa") or {}
    o = ['<section class="quebra"><h2>2. RDD sharp com o escore completo (E3)</h2>']
    cob = st.get("cobertura_do_escore") or {}
    pops = "".join(
        f"<li><strong>{esc(rotulo_pop(ctx, k))}</strong>: {br_int(v.get('municipios'))} municípios, "
        f"{br_pct(v.get('pct'))} com escore. {esc((prot.get('populacoes') or {}).get(k, ''))}</li>"
        for k, v in cob.items())
    out = "".join(f"<li>{esc(x)}</li>" for x in (p3.get("outcomes") or []))
    o.append(dl_kv([
        ("Populações", f"<ul>{pops}</ul>"),
        ("Outcomes (protocolo)", f"<ul>{out}</ul><span class=\"muted\">D<sub>k</sub>: "
                                 f"{esc((prot.get('outcome') or {}).get('D_k', ''))}</span>"),
        ("Estimador", esc(p3.get("estimador", ""))),
        ("Lado do corte", esc(st.get("lado_do_corte", ""))),
        ("Contraste", esc(st.get("contraste", ""))),
        ("Regra de relato", esc(st.get("regra_de_relato", ""))),
    ], classe="kv protocolo"))
    o.append(f'<p class="nota">Do protocolo congelado (<code>{esc(rel(PROTOCOLO))}</code>) e do status do E3 '
             f"(<code>{esc(rel(E3_STATUS))}</code>). O escore usado é <code>{esc((st.get('escore') or {}).get('arquivo', ''))}"
             "</code>, o IVS 2010 oficial completo.</p>")

    o.append("<h3>Resultado principal</h3>")
    o.append(tabela_principais(ctx, ne, titulo="E3 — estimativas principais"))
    o.append(
        f"<p>Nenhuma das {len(ne['pr'])} estimativas principais é distinguível de zero, e o menor p entre as "
        f"{ne['n_espec']} especificações é {br_p(ne['p_min'])}. Os intervalos de 95% têm de "
        f"{br(ne['larg_min'], 0)} a {br(ne['larg_max'], 0)} p.p. de largura: são compatíveis com nenhum efeito e "
        "também com efeitos grandes, positivos ou negativos. A diferença das médias brutas mistura o salto com a "
        "inclinação do outcome no IVS dentro da janela; o local linear separa as duas coisas, e por isso médias "
        "brutas maiores do lado de cima convivem com saltos negativos.</p>")

    paineis = ctx["paineis_rd"]
    o.append(figura(
        "Gráfico RD do ciclo 1 (P1): média do outcome por bin de 0,010 do IVS, com as retas locais lineares",
        fig_rd_p1(ctx, paineis),
        fonte_html(ESCORE, E4_PROP, ATIVOS_ZIP, E3_EST,
                   extra=(f"D<sub>1</sub> lido só nas colunas <code>co_ibge</code> e <code>ciclo</code>, com as funções "
                          f"de <code>{esc(rel(E3_SCRIPT))}</code>; o salto de cada reta foi conferido contra "
                          f"<code>{esc(rel(E3_EST))}</code>")),
        sub=(f"Faixa clara: janela principal (±{br(ctx['h_principal'], 3)}), a única usada nas retas. Pontos cinza: "
             f"bins até ±{br(ALCANCE_RD_MIL / 1000, 3)}, fora da janela, só para contexto. Traço preto no corte: salto "
             "estimado. Bins (a; b], o corte fica no bin à esquerda; contagens por bin no Apêndice A."),
    ))
    o.append(figura(
        "Saltos estimados com IC 95%, todas as especificações do E3",
        fig_forest_e3(ctx),
        fonte_html(E3_EST, extra="Em azul, a janela principal; em cinza, as janelas de sensibilidade"),
        sub=f"{ne['n_espec']} especificações do protocolo, relatadas independentemente do resultado.",
    ))

    d = ordenar_est(ctx["est"], ctx["h_principal"])
    linhas = [[esc(rotulo_pop(ctx, r.populacao, curto=True)), esc(rotulo_outcome(ctx, r.outcome, curto=True)),
               br(r.corte), br(r.h) + (" *" if r.especificacao == "principal" else ""),
               f"{br_int(r.n_abaixo)} / {br_int(r.n_acima)}",
               f"{pct(r.media_bruta_abaixo)} → {pct(r.media_bruta_acima)}",
               pp(r.tau), ic_pp(r.ic95_inf, r.ic95_sup), br(r.ep * 100, 1), br_p(r.p_valor)]
              for r in d.itertuples()]
    o.append(tabela(
        [("Ciclo", "txt"), ("Outcome", "txt"), ("Corte", "num"), ("h", "num"), ("n abaixo / acima", "num"),
         ("Média bruta abaixo → acima", "num"), ("Salto (p.p.)", "num"), ("IC 95% (p.p.)", "num"),
         ("EP (p.p.)", "num"), ("p", "num")],
        linhas, classe="compacta", titulo="E3 — todas as especificações", inteiro=True,
        rodape=fonte_html(E3_EST, grafico=False, extra="* janela principal. n = municípios com peso positivo no "
                                                        "kernel triangular"),
    ))

    o.append("<h3>Diagnósticos sem outcome</h3>")
    o.append(f"<p>{esc(' / '.join(p3.get('diagnosticos_sem_outcome', [])))}. Foram gravados antes da leitura dos "
             f"outcomes (<code>{esc(rel(E3_DIAG))}</code>).</p>")
    dens = ne["dens"].copy()
    dens["_ord"] = [0 if math.isclose(h, ctx["h_principal"]) else 1 for h in dens["h"]]
    dens = dens.sort_values(["populacao", "corte", "_ord", "h"], kind="stable")
    ld = [[esc(rotulo_pop(ctx, r.populacao, curto=True)), br(r.corte),
           br(r.h) + (" *" if math.isclose(r.h, ctx["h_principal"]) else ""),
           f"{br_int(r.n_abaixo)} / {br_int(r.n_acima)}", br(r.rho, 2),
           f"[{br(r.rho_ic95_inf, 2)}; {br(r.rho_ic95_sup, 2)}]", br_p(r.p_valor)] for r in dens.itertuples()]
    o.append(tabela(
        [("Ciclo", "txt"), ("Corte", "num"), ("h", "num"), ("Municípios abaixo / acima", "num"),
         ("ρ", "num"), ("IC 95%", "num"), ("p", "num")], ld, classe="compacta",
        titulo="Densidade do IVS entre todos os municípios da população, no corte",
        rodape=(f'<p class="nota">ρ = razão das densidades laterais (acima / abaixo), Poisson log-linear em mass '
                f"points de 0,001; ρ = 1 é ausência de salto. {'Todos os intervalos contêm 1' if ne['dens_todos_contem_1'] else 'Há intervalos que excluem 1'}: "
                "não há sinal de manipulação do IVS nem de que o corte tenha mudado quais municípios entraram no quadro. "
                "* janela principal.</p>" + fonte_html(E3_DIAG, grafico=False)),
    ))

    bal = ne["bal"]
    chaves = sorted({(p, c) for p, c in zip(bal["populacao"], bal["corte"])})
    variaveis = [v for v in ROTULO_COV if v in set(bal["variavel"])] + sorted(set(bal["variavel"]) - set(ROTULO_COV))
    lb = []
    for v in variaveis:
        lin = [esc(rotulo_cov(v))]
        for p, c in chaves:
            r = bal[(bal["variavel"] == v) & (bal["populacao"] == p) & np.isclose(bal["corte"], c)]
            if len(r) != 1 or not finito(r["tau"].iloc[0]):
                lin.append("—")
                continue
            r = r.iloc[0]
            txt = f"{sinal(r['tau'], nd_cov(v))} <span class=\"muted\">({br_p(r['p_valor'])})</span>"
            lin.append(f'<span class="sig">{txt} ‡</span>' if r["p_valor"] < ALFA else txt)
        lb.append(lin)
    d_all = ctx["diag"]
    sens = d_all[(d_all["diagnostico"] == "balanco_covariavel_pre") & (d_all["variavel"] != COVARIAVEL_RUNNING)
                 & ~np.isclose(d_all["h"], ctx["h_principal"]) & (d_all["p_valor"] < ALFA)]
    sens_txt = "; ".join(
        f"{rotulo_pop(ctx, p, curto=True).lower()}, corte {br(c)}, h = {br(h)}: "
        + ", ".join(rotulo_cov(v) for v in g["variavel"])
        for (p, c, h), g in sens.groupby(["populacao", "corte", "h"]))
    run = d_all[(d_all["diagnostico"] == "balanco_covariavel_pre") & (d_all["variavel"] == COVARIAVEL_RUNNING)]
    o.append(tabela(
        [("Covariável pré", "txt")] + [(f"{esc(rotulo_pop(ctx, p, curto=True))} · {br(c)}", "num") for p, c in chaves],
        lb, classe="compacta",
        titulo=f"Balanço de covariáveis pré-programa: salto no corte (p), h = {br(ctx['h_principal'], 3)}",
        rodape=(f'<p class="nota">‡ p &lt; 0,05. {br_int(len(ne["bal_sig"]))} de {br_int(ne["bal_n"])} testes '
                f"(seriam {br(ALFA * ne['bal_n'], 1)} por acaso). Mesmo estimador do E3 (local linear, kernel triangular, "
                f"HC1). Nas janelas de sensibilidade, p &lt; 0,05 em: {esc(sens_txt) or 'nenhum'}. "
                f"<strong>Nota:</strong> a linha <code>{COVARIAVEL_RUNNING}</code> do arquivo de diagnósticos foi omitida: "
                "ela é o próprio IVS oficial, a running variable. Seu “salto” é zero por construção (|salto| máximo "
                f"{br(run['tau'].abs().max(), 0) if len(run) else '—'}; registrado como {run['tau'].abs().max():.0e}) "
                "e o p-valor é ruído numérico.</p>"
                + fonte_html(E3_DIAG, grafico=False,
                             extra="Covariáveis da base oficial do Ipea (a08) e da tipologia territorial, registradas em "
                                   f"<code>{esc(rel(E3_STATUS))}</code>")),
    ))
    o.append(f"<p>{ctx['nota_suporte']}</p>")
    o.append("</section>")
    return "".join(o)


def nota_suporte(ctx) -> str:
    """Explica (e confere) a diferenca entre o suporte e o n das estimativas."""
    d, est, base = ctx["diag"], ctx["est"], ctx["base"]
    sup = d[d["diagnostico"] == "suporte"]
    casos, ok = [], True
    for r in sup.itertuples():
        e = est[(est["populacao"] == r.populacao) & np.isclose(est["corte"], r.corte) & np.isclose(est["h"], r.h)]
        if e.empty:
            continue
        n_est = int(e["n_acima"].iloc[0])
        if n_est == r.n_acima and int(e["n_abaixo"].iloc[0]) == r.n_abaixo:
            continue
        pop = populacao(base, r.populacao)
        na_borda = int((pop["s_mil"] == round((r.corte + r.h) * 1000)).sum())
        ok &= (r.n_acima - n_est == na_borda) and int(e["n_abaixo"].iloc[0]) == r.n_abaixo
        casos.append(f"{rotulo_pop(ctx, r.populacao, curto=True).lower()}, corte {br(r.corte)}, h = {br(r.h)}: "
                     f"{br_int(r.n_acima)} acima no suporte, {br_int(n_est)} na estimativa")
    if not casos:
        return "O suporte por janela coincide com o n das estimativas."
    expl = ("A diferença é exatamente o número de municípios com IVS igual a c + h, que recebem peso zero no kernel "
            "triangular e não entram na estimativa (conferido aqui)." if ok else
            "<span class=\"alerta\">A diferença não se explica só pelos municípios em c + h; conferir.</span>")
    return (f"<span class=\"nota\">Suporte × n das estimativas: {esc('; '.join(casos))}. {expl}</span>")


def secao_antes(ctx) -> str:
    o = ['<section class="quebra"><h2>3. Antes do escore completo: E1, E2 e E4 (exploratórios)</h2>']
    o.append(
        "<p>Até se descobrir que o escore administrativo é o IVS 2010 oficial, o escore só estava publicado para os "
        "municípios com especialista ativo — a cobertura dependia do próprio outcome. O protocolo previu então três "
        "leituras exploratórias: <strong>E1</strong>, razão de densidades dos municípios com especialista, sob a "
        "premissa A1 (não testável na época); <strong>E2</strong>, limites para a diferença de presença sem supor "
        "onde estavam os municípios sem escore; <strong>E4</strong> (adendo), limites e Lee para a proporção "
        "preenchida. <strong>Todos ficam superados pelo E3</strong>, que observa o escore de todos os municípios. "
        f"Os cenários “informados” de E2 e E4 usaram como banda o {esc(ctx['rl']['longo'])} e ficam sem valor.</p>")
    e1 = ler_csv(E1_EST)
    e2 = ler_csv(E2_LIM)
    e4 = ler_csv(E4_EST)
    if e1 is None or e2 is None or e4 is None:
        o.append(caixa_ausente("Saídas exploratórias ausentes", [E1_EST, E2_LIM, E4_EST]))
    hp = ctx["h_principal"]
    pr = principais(ctx)
    ciclo_de = {k: int(v.get("ciclo_do_outcome")) for k, v in (ctx["st"].get("populacoes") or {}).items()}
    linhas = []
    for pop, outcome in ORDEM_GRUPOS[1:] + ORDEM_GRUPOS[:1]:
        for c in ctx["cortes"]:
            k = ciclo_de.get(pop)
            v_e1 = v_e2 = v_e4b = v_e4c = "—"
            if outcome == OUTCOME_D and e1 is not None:
                r = e1[(e1["ciclo"] == k) & np.isclose(e1["corte"], c) & e1["papel"].isin(["principal", "replicacao"])]
                if len(r):
                    r = r.iloc[0]
                    v_e1 = f"{br(r.rho, 2)} [{br(r.ic_inf, 2)}; {br(r.ic_sup, 2)}]"
            if outcome == OUTCOME_D and e2 is not None:
                r = e2[(e2["ciclo"] == k) & np.isclose(e2["corte"], c) & np.isclose(e2["h"], hp)
                       & (e2["cenario"] == "pior_caso")]
                if len(r):
                    r = r.iloc[0]
                    v_e2 = f"{pp(r.delta_min)} a {pp(r.delta_max)}"
            if outcome == OUTCOME_FRAC and e4 is not None:
                r = e4[(e4["componente"] == "E4b") & (e4["outcome"] == "Y1") & np.isclose(e4["corte"], c)
                       & np.isclose(e4["h"], hp) & (e4["cenario_ou_espec"] == "pior_caso")
                       & (e4["ponderacao"] == "simples")]
                if len(r):
                    r = r.iloc[0]
                    v_e4b = f"{pp(r.limite_inf)} a {pp(r.limite_sup)}"
                r = e4[(e4["componente"] == "E4c") & (e4["outcome"] == "Y1") & np.isclose(e4["corte"], c)
                       & (e4["cenario_ou_espec"] == "lee_constante_local")]
                if len(r):
                    r = r.iloc[0]
                    v_e4c = (f"{pp(r.limite_inf)} a {pp(r.limite_sup)}<br><span class=\"muted\">IC "
                             f"{pp(r.ic_inf)} a {pp(r.ic_sup)}</span>")
            r3 = pr[(pr["populacao"] == pop) & (pr["outcome"] == outcome) & np.isclose(pr["corte"], c)]
            v_e3 = f"{pp(r3['tau'].iloc[0])} {ic_pp(r3['ic95_inf'].iloc[0], r3['ic95_sup'].iloc[0])}" if len(r3) else "—"
            linhas.append([f"{esc(rotulo_pop(ctx, pop, curto=True))} · {esc(rotulo_outcome(ctx, outcome, True))}",
                           br(c), v_e1, v_e2, v_e4b, v_e4c, f"<strong>{v_e3}</strong>"])
    o.append(tabela(
        [("Ciclo · outcome", "txt"), ("Corte", "num"), ("E1: ρ [IC 95%]", "num"),
         ("E2: limites de Δ<br><span class=\"muted\">pior caso, p.p.</span>", "num"),
         ("E4b: limites<br><span class=\"muted\">pior caso, p.p.</span>", "num"),
         ("E4c: Lee<br><span class=\"muted\">limites e IC, p.p.</span>", "num"),
         ("E3: salto [IC 95%]<br><span class=\"muted\">p.p.</span>", "num")],
        linhas, classe="compacta",
        titulo=f"Exploratórios com escore parcial (h = {br(hp, 3)}) e a estimativa do E3 que os substitui",
        rodape=fonte_html(E1_EST, E2_LIM, E4_EST, E3_EST, grafico=False),
    ))
    # leitura automatica
    itens = []
    if e1 is not None:
        r = e1[e1["papel"].isin(["principal", "replicacao"])]
        cont = int(((r["ic_inf"] <= 1) & (r["ic_sup"] >= 1)).sum())
        itens.append(f"E1: {cont} de {len(r)} razões principais/replicação têm IC contendo 1 (premissa A1).")
    if e2 is not None:
        r = e2[np.isclose(e2["h"], hp) & (e2["cenario"] == "pior_caso")]
        cont = int(((r["delta_min"] <= 0) & (r["delta_max"] >= 0)).sum())
        itens.append(f"E2: {cont} de {len(r)} intervalos de pior caso na janela principal contêm zero.")
    if e4 is not None:
        r = e4[(e4["componente"] == "E4b") & (e4["outcome"] == "Y1") & np.isclose(e4["h"], hp)
               & (e4["cenario_ou_espec"] == "pior_caso") & (e4["ponderacao"] == "simples")]
        cont = int(((r["limite_inf"] <= 0) & (r["limite_sup"] >= 0)).sum())
        itens.append(f"E4b: {cont} de {len(r)} intervalos de pior caso (Y1, média simples) contêm zero.")
        lee = e4[(e4["componente"] == "E4c") & (e4["cenario_ou_espec"] == "lee_constante_local")]
        excl = lee[(lee["limite_inf"] > 0) | (lee["limite_sup"] < 0)]
        ic_ok = int(((lee["ic_inf"] <= 0) & (lee["ic_sup"] >= 0)).sum())
        txt = f"E4c (Lee, sob monotonicidade e A1): {ic_ok} de {len(lee)} IC contêm zero"
        if len(excl):
            txt += ("; os limites de identificação em si excluem zero em "
                    + ", ".join(f"{br(r.corte)} ({pp(r.limite_inf)} a {pp(r.limite_sup)} p.p.)" for r in excl.itertuples())
                    + ", mas a incerteza amostral cobre o zero")
        itens.append(txt + ".")
        naive = e4[(e4["componente"] == "E4a") & (e4["outcome"] == "Y1") & (e4["ponderacao"] == "simples")
                   & (e4["cenario_ou_espec"] == "local_linear_triangular")]
        if len(naive):
            itens.append("E4a (ingênuo, só municípios com escore; viesado por seleção, apenas referência): "
                         + "; ".join(f"{pp(r.estimativa)} {ic_pp(r.ic_inf, r.ic_sup)} p.p. em {br(r.corte)}"
                                     for r in naive.itertuples()) + ".")
    o.append('<ul class="leitura">' + "".join(f"<li>{esc(x)}</li>" for x in itens) + "</ul>")
    o.append(
        "<p class=\"nota\">Os objetos não são os mesmos: E1 estima uma razão de probabilidades; E2 e E4b, a diferença "
        "bruta de proporções entre as janelas; E4c, o efeito entre municípios que teriam especialista com ou sem a "
        "bolsa maior; o E3, o salto local linear no corte. A última coluna é a estimativa que substitui as "
        "anteriores, não uma comparação termo a termo. Nenhum dos exploratórios contradiz o E3.</p>")
    st1, st2, st4 = (ler_json(E1_RES) or {}), (ler_json(E2_RES) or {}), (ler_json(E4_RES) or {})
    o.append(f'<div class="fonte">Situação registrada: E1 <code>{esc(st1.get("status", "—"))}</code>; E2 '
             f'<code>{esc(st2.get("status", "—"))}</code>; E4 <code>{esc(st4.get("status", "—"))}</code> '
             f"(<code>{esc(rel(E1_RES))}</code>, <code>{esc(rel(E2_RES))}</code>, <code>{esc(rel(E4_RES))}</code>).</div>")
    o.append("</section>")
    return "".join(o)


def varrer_citacoes_local() -> list[str]:
    """JSONs de output/ que registram o arquivo local como fonte (exceto os que so documentam a troca)."""
    alvo = rel(IVS_LOCAL)
    achados = []
    for p in sorted((ROOT / "output").rglob("*.json")):
        if p in CITAM_SEM_USAR:
            continue
        try:
            if alvo in p.read_text(encoding="utf-8", errors="ignore"):
                achados.append(rel(p))
        except OSError:
            continue
    return achados


def secao_leitura(ctx) -> str:
    prot, adendo, st, ne, r1 = ctx["prot"], ctx["adendo"], ctx["st"], ctx["n_e3"], ctx["r1"]
    o = ['<section class="quebra"><h2>4. Leitura e limites</h2>']
    g, info = ctx["categorias"]
    pacote = ("A categoria de IVS do MS, usada no PMMB, muda exatamente nos dois cortes da bolsa (Tabela 3): qualquer "
              "benefício que dependa dessa categoria — por exemplo, a ajuda de custo do PMMB por categoria de IVS — muda "
              "junto, e o contraste passa a ser um <strong>pacote</strong>. Esses benefícios não foram mapeados."
              if info.get("nos_cortes") else
              "Se outra política usar os mesmos cortes de IVS — por exemplo, a ajuda de custo do PMMB por categoria —, "
              "o contraste é um <strong>pacote</strong>.")
    pr = ne["pr"]
    mde_txt = "; ".join(
        f"{rotulo_pop(ctx, p, curto=True).lower()} · {rotulo_outcome(ctx, oc, True)}: "
        + " e ".join(f"{br(MDE_FATOR * r.ep * 100, 0)} p.p. em {br(r.corte)}" for r in gg.itertuples())
        for (p, oc), gg in pr.groupby(["populacao", "outcome"], sort=False))
    n_lado = pr[["n_abaixo", "n_acima"]].to_numpy()
    aut = prot.get("autorizacao_autor") or {}
    expo = "".join(f"<li>{esc(x)}</li>" for x in prot.get("exposicao_previa_a_outcomes", []))
    expo4 = "".join(f"<li>{esc(x)}</li>" for x in adendo.get("exposicao_previa_a_outcomes", []))
    cov = st.get("covariaveis_pre") or {}
    cov_txt = "; ".join(f"<code>{esc(k)}</code>" for k in cov)
    auditoria = re.search(r"docs/[\w/.\-]+\.md", str((r1.get("arquivo_local_ivs_2010") or {}).get("leitura", "")))
    rever = [
        ("Gradiente de IVS no A4 e covariáveis de IVS, IDHM e população do arquivo local",
         [ROOT / "output" / "tema_trabalho" / "A4_figura_02_gradiente_ivs.png",
          ROOT / "output" / "tema_trabalho" / "A4_tabela_03d_ivs_spline.csv"]),
        ("R1 antigo: “a regra não se reproduz pelo IVS”, “177 acima do piso”, “IVS é piso”", [REGRA_ANTIGA, A01B]),
        ("Primeiro estágio público: salto instável em 0,400 e nulo em 0,500 (artefatos do arquivo local)", [A01]),
        ("Cenário “informado” de E2 e E4, que usou o arquivo local como banda", [E2_RES, E4_RES]),
        ("Comparação “IVS 2010 público × escore” do R1 com escore parcial", [R1_ADMIN]),
    ]
    rever_html = "".join(
        f"<li>{esc(t)}: " + ", ".join(f"<code>{esc(rel(p))}</code>" + ("" if p.exists() else " (ausente)") for p in ps)
        + "</li>" for t, ps in rever)
    varredura = varrer_citacoes_local()
    blocos = [
        ("Estimando e contraste",
         f"Salto em E[Y | IVS] no corte, entre os municípios do quadro de vagas: <strong>estimativa local do efeito do "
         f"anúncio de +{br_mil(ctx['valor_faixa'][ctx['faixas'][1]] - ctx['valor_faixa'][ctx['faixas'][0]])} por "
         "mês</strong>, sob as premissas da RDD. Vale para municípios do quadro com IVS perto dos cortes, não para o "
         "país nem para municípios longe dos cortes. Não identifica a participação no PMM-E nem o efeito total do Agora "
         f"Tem Especialistas. {pacote} <span class=\"muted\">Status do E3:</span> “{esc(st.get('contraste', ''))}”."),
        ("População e outcomes",
         "<ul>" + "".join(f"<li><strong>{esc(k)}</strong>: {esc(v)}</li>" for k, v in (prot.get("populacoes") or {}).items())
         + f"<li><strong>Presença (D<sub>k</sub>)</strong>: {esc((prot.get('outcome') or {}).get('D_k', ''))}. "
           f"Leitura: {esc((prot.get('outcome') or {}).get('leitura', ''))}.</li>"
         + f"<li><strong>Preenchimento</strong>: {esc((adendo.get('outcomes') or {}).get('Y1_principal', ''))}.</li></ul>"
           "Presença cadastrada no programa não é retenção individual, produção ou acesso."),
        ("Premissas e diagnósticos",
         "A RDD supõe que, sem a diferença de bolsa, os outcomes variariam de forma contínua no IVS ao passar pelo corte. "
         "Manipulação é implausível: o IVS 2010 é calculado com dados de 2010, anteriores ao programa "
         f"(recorte do a08: {esc(ctx['manif'].get('recorte', '—'))}). A densidade não salta (seção 2). O balanço tem "
         f"{br_int(len(ne['bal_sig']))} desequilíbrios com p &lt; 0,05 em {br_int(ne['bal_n'])} testes; o corte com "
         "mais desequilíbrios pede cautela e, se usado como resultado, controle por covariáveis como sensibilidade."),
        ("Poder",
         f"Cerca de {br_int(n_lado.min())} a {br_int(n_lado.max())} municípios por lado na janela principal. Efeito "
         f"mínimo detectável aproximado (2,8 × EP): {esc(mde_txt)}. A RDD só teria detectado efeitos dessa ordem; "
         "efeitos moderados ficam fora do alcance, mesmo juntando ciclos."),
        ("Protocolo e exposição prévia",
         f"Protocolo congelado em {data_br(prot.get('data_congelamento'))}, pré-registro: "
         f"{'sim' if prot.get('pre_registro') else 'não'}. Exposição prévia a outcomes registrada:<ul>{expo}</ul>"
         f"Adendo E4 congelado em {data_br(adendo.get('data_congelamento'))} (pré-registro: "
         f"{'sim' if adendo.get('pre_registro') else 'não'}); hipótese: “{esc(adendo.get('hipotese', ''))}”. "
         f"Exposição prévia:<ul>{expo4}</ul>"
         "Desvios em relação ao texto do protocolo, todos sem olhar outcome: (i) a running variable fixada era o escore "
         f"administrativo de <code>{esc((prot.get('running_variable') or {}).get('fonte', ''))}</code>; o E3 usou o IVS "
         "2010 oficial completo, idêntico ao escore onde ele é publicado — a mesma variável, com a cobertura completa "
         "que o protocolo exigia para o E3; (ii) as covariáveis de balanço vêm da base oficial e da tipologia "
         f"({cov_txt}), não do arquivo local; (iii) a justificativa da autorização do autor "
         f"(“{esc(aut.get('justificativa', ''))}”) se apoiava no arquivo local."),
        ("Multiplicidade",
         f"{ne['n_espec']} especificações de outcome e {br_int(ne['bal_n'])} testes de balanço na janela principal. "
         f"O protocolo do E3 não fixa correção; como nenhum outcome tem p &lt; 0,05 (menor p = {br_p(ne['p_min'])}), "
         "uma correção não mudaria a leitura."),
        ("Análises antigas a rever",
         "O arquivo local entrou em análises anteriores do projeto, que precisam ser revistas antes de serem citadas:"
         f"<ul>{rever_html}</ul>"
         + (f"Detalhes em <code>{esc(auditoria.group(0))}</code>. " if auditoria else "")
         + f"Varredura automática: {br_int(len(varredura))} arquivos JSON em <code>output/</code> registram "
           f"<code>{esc(rel(IVS_LOCAL))}</code> como fonte: "
         + ", ".join(f"<code>{esc(p)}</code>" for p in varredura) + "."),
        ("Ciclo 3",
         "Prospectivo e congelado. O quadro do ciclo 3 só aparece na reconstrução da regra; nenhum outcome do ciclo 3 "
         "foi lido."),
    ]
    o.append('<dl class="leitura-dl">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in blocos) + "</dl>")
    o.append(fonte_html(PROTOCOLO, ADENDO_E4, E3_STATUS, E3_EST, E3_DIAG, CATEGORIA, MANIF_OFICIAL, R1_OFICIAL,
                        grafico=False))
    o.append("</section>")
    return "".join(o)


def secao_apendice_rd(ctx) -> str:
    paineis = ctx["paineis_rd"]
    por_corte = {}
    for p in paineis:
        por_corte.setdefault(p["corte"], {})[p["outcome"]] = p
    cortes = sorted(por_corte)
    n_bins = len(next(iter(por_corte.values()))[OUTCOME_FRAC]["bins"])
    linhas = []
    for i in range(n_bins):
        b0 = por_corte[cortes[0]][OUTCOME_FRAC]["bins"][i]
        c_rel = (b0["lo"] - por_corte[cortes[0]][OUTCOME_FRAC]["c_mil"], b0["hi"] - por_corte[cortes[0]][OUTCOME_FRAC]["c_mil"])
        lin = [f"(c {'−' if c_rel[0] < 0 else '+'} {br(abs(c_rel[0]) / 1000)}; c {'−' if c_rel[1] < 0 else '+'} "
               f"{br(abs(c_rel[1]) / 1000)}]"]
        for c in cortes:
            bf = por_corte[c][OUTCOME_FRAC]["bins"][i]
            bd = por_corte[c][OUTCOME_D]["bins"][i]
            marca = "" if bf["dentro"] else ' <span class="muted">°</span>'
            lin += [f"({br(bf['lo'] / 1000)}; {br(bf['hi'] / 1000)}]{marca}", br_int(bf["n"]), pct(bf["media"]),
                    pct(bd["media"])]
        linhas.append(lin)
    cab = [("Bin relativo ao corte", "txt nowrap")]
    for c in cortes:
        cab += [(f"Corte {br(c)}: bin", "txt nowrap"), ("n", "num"), ("Preench.", "num"), ("Presença", "num")]
    return (
        '<section class="quebra"><h2>Apêndice A — dados do gráfico RD</h2>'
        "<p>Médias por bin do gráfico RD do ciclo 1 (Figura 4). Preench. = fração de células preenchidas na 1ª chamada; "
        f"Presença = especialista do ciclo 1 ativo em {esc(data_relacao_nominal(ctx['prot']))}. Cada município conta uma "
        "vez por bin; as médias são simples entre municípios.</p>"
        + tabela(cab, linhas, classe="compacta", titulo="Médias do outcome por bin de 0,010 do IVS oficial, ciclo 1",
                 inteiro=True,
                 rodape=('<p class="nota">° bin fora da janela principal (não entra nas retas). '
                         "As estimativas não usam estes bins: o local linear usa os municípios individualmente.</p>"
                         + fonte_html(ESCORE, E4_PROP, ATIVOS_ZIP, grafico=False)))
        + "</section>"
    )


def secao_proveniencia() -> str:
    resumos = {E1_EST: ler_json(E1_RES), E1_RES: ler_json(E1_RES), E2_LIM: ler_json(E2_RES), E2_RES: ler_json(E2_RES),
               E4_EST: ler_json(E4_RES), E4_RES: ler_json(E4_RES)}
    linhas = []
    for p in ENTRADAS:
        h = sha256(p)
        r = resumos.get(p)
        prod = origem_html(p, r if isinstance(r, dict) else None) if p.exists() else "—"
        nlin = "—"
        if p.exists() and p.suffix == ".csv":
            with p.open(encoding="utf-8", errors="ignore") as f:
                nlin = br_int(sum(1 for _ in f) - 1)
        linhas.append([f"<code>{esc(rel(p))}</code>",
                       '<span class="pill pill-ok">presente</span>' if h else '<span class="pill pill-pend">ausente</span>',
                       nlin, f"<code>{h[:12]}</code>" if h else "—", prod])
    return (
        '<section class="quebra"><h2>Apêndice B — proveniência das entradas</h2>'
        "<p>Cada número e gráfico deste relatório é lido dos arquivos abaixo no momento da geração. SHA-256 truncado em "
        "12 caracteres; o hash completo pode ser recalculado com <code>sha256sum</code>. Linhas = registros de dados "
        "(sem cabeçalho).</p>"
        + tabela([("Arquivo", "txt"), ("Status", "txt"), ("Linhas", "num"), ("SHA-256", "txt nowrap"),
                  ("Origem", "txt")], linhas, classe="compacta proven", inteiro=False)
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
@media screen { main { padding: 12mm 16px; } }
h1 { font-size: 24pt; font-weight: 650; line-height: 1.15; margin: 4mm 0 4mm; letter-spacing: -0.01em; }
h2 { font-size: 14pt; font-weight: 650; margin: 0 0 6pt; padding-bottom: 4pt; border-bottom: 1px solid var(--axis); }
h3 { font-size: 10.5pt; font-weight: 650; margin: 12pt 0 4pt; break-after: avoid; }
section { margin-bottom: 14pt; }
section.quebra { break-before: page; }
p { margin: 0 0 6pt; }
ul, ol { margin: 0 0 6pt; padding-left: 16pt; }
li { margin-bottom: 2pt; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 7.6pt; color: var(--ink2); overflow-wrap: anywhere; }
.bloco-tab { margin: 4pt 0 6pt; }
.bloco-tab.inteiro { break-inside: avoid; }
.nowrap { white-space: nowrap; }
table.proven td:first-child { width: 62mm; }
table.proven code { font-size: 6.8pt; }
.muted { color: var(--muted); }
.nota { font-size: 8.4pt; color: var(--ink2); }
.alerta { font-size: 8.8pt; color: #a02020; border-left: 3px solid #d03b3b; padding-left: 6pt; }
.sig { font-weight: 700; color: var(--ink); }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt; margin: 2pt 0 4pt; font-variant-numeric: tabular-nums; }
table.compacta { font-size: 7.6pt; }
table.estreita { width: auto; min-width: 55%; }
th { text-align: left; font-weight: 600; color: var(--ink2); border-bottom: 1px solid var(--axis); padding: 3pt 4pt;
  vertical-align: bottom; line-height: 1.2; }
td { border-bottom: 1px solid var(--grid); padding: 2.4pt 4pt; vertical-align: top; }
th.num, td.num { text-align: right; }
td.num { white-space: nowrap; }
tr { break-inside: avoid; }
thead { display: table-header-group; }
.tab-titulo, .fig-titulo { font-weight: 600; font-size: 9.4pt; margin: 10pt 0 2pt; break-after: avoid; }
.fig-num { color: var(--ink2); }
.fig-sub { color: var(--ink2); font-size: 8.4pt; margin-bottom: 4pt; }
.fig-nota { color: var(--ink2); font-size: 8pt; margin-top: 4pt; }
figure { margin: 8pt 0 12pt; break-inside: avoid; }
figure svg { display: block; width: 100%; height: auto; }
.fonte { font-size: 7.4pt; color: var(--muted); border-top: 1px solid var(--grid); padding-top: 3pt; margin: 3pt 0 10pt; }
.fonte code { font-size: 7pt; color: var(--muted); }
.capa { min-height: 250mm; display: flex; flex-direction: column; break-after: page; }
.kicker { font-size: 9pt; color: var(--ink2); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 24mm; }
.lead { font-size: 11pt; color: var(--ink2); max-width: 160mm; }
dl.meta { display: grid; grid-template-columns: 42mm 1fr; gap: 3pt 8pt; margin: 7mm 0; font-size: 9.4pt; }
dl.meta dt { color: var(--muted); }
dl.meta dd { margin: 0; }
.aviso { border-left: 3px solid var(--warn); background: var(--warn-bg); padding: 8pt 10pt; margin: 2mm 0 6mm; font-size: 9.6pt; }
table.status td:first-child { font-weight: 600; }
.sumario li { margin-bottom: 1pt; }
.pill { display: inline-block; font-size: 7.4pt; font-weight: 600; padding: 1pt 6pt; border-radius: 8pt;
  text-transform: uppercase; letter-spacing: 0.03em; white-space: nowrap; }
.pill-ok { background: #e3f1e3; color: #006300; }
.pill-pend { background: #fbecd2; color: #7a4d00; }
.pill-hist { background: #ecebe6; color: #52514e; }
.pendente { border: 1px solid var(--axis); background: var(--wash); padding: 8pt 10pt; border-radius: 4px; margin: 6pt 0 10pt; }
.pend-tit { font-weight: 600; }
section.resumo h2 { margin-bottom: 8pt; }
ul.resumo-lista { padding-left: 13pt; margin-bottom: 8pt; }
ul.resumo-lista li { margin-bottom: 6pt; line-height: 1.42; }
.dizer { border-left: 3px solid var(--s1); background: var(--wash); padding: 6pt 10pt 4pt; margin: 8pt 0 0; font-size: 9pt; break-inside: avoid; }
.dizer ul { margin: 3pt 0 2pt; }
dl.kv { display: grid; grid-template-columns: 34mm 1fr; gap: 3pt 8pt; margin: 4pt 0 6pt; font-size: 8.6pt; }
dl.kv dt { color: var(--ink2); font-weight: 600; }
dl.kv dd { margin: 0; }
dl.kv ul { margin: 0; padding-left: 12pt; }
dl.protocolo { background: var(--wash); padding: 6pt 8pt; border-radius: 4px; }
ul.leitura li { margin-bottom: 3pt; }
dl.leitura-dl dt { font-weight: 650; margin-top: 8pt; break-after: avoid; }
dl.leitura-dl dd { margin: 2pt 0 0; }
dl.leitura-dl dd ul { margin: 2pt 0 4pt; }
"""


def montar_html(commit, sujo, agora) -> str:
    ctx = carregar()
    ctx.update({"commit": commit, "sujo": sujo, "agora": agora})
    ctx["divergencias_pop"] = conferir_populacoes(ctx)
    ctx["n_regra"] = numeros_regra(ctx)
    ctx["cruz"] = cruzamento_grade(ctx)
    ctx["categorias"] = categorias_ivs(ctx)
    ctx["n_e3"] = numeros_e3(ctx)
    ctx["paineis_rd"] = dados_rd_p1(ctx)
    ctx["nota_suporte"] = nota_suporte(ctx)
    corpo = [
        secao_capa(ctx),
        secao_resumo(ctx),
        secao_regra(ctx),
        secao_e3(ctx),
        secao_antes(ctx),
        secao_leitura(ctx),
        secao_apendice_rd(ctx),
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
    ausentes = [rel(p) for p in ENTRADAS if not p.exists()]
    if ausentes:
        print("Entradas ausentes (secoes marcadas): " + ", ".join(ausentes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
