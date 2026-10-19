"""Relatório curto de validação metodológica da RDD da bolsa do PMM-E, para os professores (HTML e PDF).

Público: professores de economia que vão validar o desenho e os resultados obtidos até agora com os
outcomes atuais (RDD do adicional de R$ 5 mil da bolsa nos cortes 0,300 e 0,400 do IVS 2010 oficial do
Ipea). Cerca de 12 a 15 páginas A4, só o essencial: pergunta e estimando, dados e regra, validade, resultado
com o outcome original (E3 e E5), rodada multi-outcome (E6, E7, E9), síntese com Holm (E8), poder e
descartes (X6), achados exploratórios (X1 a X3) e perguntas para a banca.

Regras de integridade (as mesmas do projeto)
--------------------------------------------
- Nenhuma estimação nova. Todo número de tabela e de texto é lido de `output/` (CSV e JSON) na geração e
  formatado aqui; nenhum número de resultado é digitado neste arquivo. A única conta feita aqui é de
  exibição: o ajuste local linear do gráfico RD (o mesmo do E3, conferido contra `E3_estimativas.csv` e
  contra `E3_conferencia_sinal.json`; o script para se divergirem) e contagens de linhas das saídas.
- Figuras: PNG gravados por scripts versionados (incorporados sem alteração, byte a byte) ou desenhados aqui
  a partir de `output/` com as funções de `scripts/rdd_bolsa/09_gerar_relatorio_pdf.py` (gráfico RD e
  histograma de densidade).
- Não lê nada de `data/`. O arquivo de IVS antigo que estava em `data/` não é o IVS do município
  (auditoria 16): nenhum número dele entra no relatório, e o texto só registra, sem números, que ele foi
  descartado.
- Saída determinística: sem data de geração nem commit no HTML (a data do relatório é a do resumo da
  síntese E8). O teste regenera o HTML na memória e compara com o arquivo gravado.
- Convenção do sinal: salto = valor estimado no corte do lado com bolsa maior (IVS acima do corte) menos o
  do lado com bolsa menor. O próprio corte pertence ao lado inferior (T = 1[s > c]).

Saídas
------
- output/apresentacao_validacao/relatorio_validacao_rdd_bolsa.html  (autocontido)
- output/apresentacao_validacao/relatorio_validacao_rdd_bolsa.pdf   (A4 retrato, Chromium headless)

Uso: `python scripts/apresentacao/gerar_relatorio_validacao_professores.py` (a partir da raiz).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ESTE_SCRIPT = Path(__file__).resolve()
SCRIPT_09 = ROOT / "scripts" / "rdd_bolsa" / "09_gerar_relatorio_pdf.py"
OUT = ROOT / "output" / "rdd_bolsa"
AQ = ROOT / "output" / "aquisicao"
SAIDA_DIR = ROOT / "output" / "apresentacao_validacao"
OUT_HTML = SAIDA_DIR / "relatorio_validacao_rdd_bolsa.html"
OUT_PDF = SAIDA_DIR / "relatorio_validacao_rdd_bolsa.pdf"

# ---- entradas (todas em output/) -------------------------------------------------------------------
R1_OFICIAL = OUT / "portao_r1_ivs_oficial.json"
MATRIZ = OUT / "matriz_municipio_escore_administrativo.csv"
ESCORE = OUT / "escore_completo_ivs2010_oficial.csv"
IVS_OFICIAL = AQ / "a08_ivs_2010_oficial_municipio.csv"
A08_MANIFESTO = AQ / "a08_manifesto_ivs_2010_oficial.json"
A10_DIAG = AQ / "a10_diagnostico_cortes_normas.json"
PROTOCOLO = OUT / "protocolo_escore_administrativo.json"
PROT40 = OUT / "protocolo_E6_multioutcome.json"
E3_STATUS = OUT / "E3_status.json"
E3_EST = OUT / "E3_estimativas.csv"
E3_DIAG = OUT / "E3_diagnosticos.csv"
E3_CONF = OUT / "E3_conferencia_sinal.json"
E4_PROP = OUT / "E4_proporcao_municipio.csv"
E5_ESPEC = OUT / "E5_especificacoes.csv"
E5_RES = OUT / "E5_resumo.json"
E6_EST = OUT / "E6_estimativas.csv"
E6_DIAG = OUT / "E6_diagnosticos.csv"
E7_EST = OUT / "E7_estimativas.csv"
E8_RES = OUT / "E8_resumo.json"
E8_TAB = OUT / "E8_tabela_sintese.csv"
E9_ROB = OUT / "E9_robustez_pos_auditoria.csv"
X1_RES = OUT / "X1_ligacao_resumo.json"
X2_DESC = OUT / "X2_descritivo.csv"
X2_EST = OUT / "X2_estimativas.csv"
X3_EST = OUT / "X3_estimativas.csv"
X6_EST = OUT / "X6_poder_descartes.csv"
X6_RES = OUT / "X6_resumo.json"

FIG_REGRA = ROOT / "output" / "apresentacao_banca2" / "regra_bolsa_ivs_oficial.png"
SCRIPT_REGRA = ROOT / "scripts" / "apresentacao" / "gerar_figuras_banca2.py"
E6_FIG = OUT / "E6_figuras"
E7_FIG = OUT / "E7_figuras"
E9_FIG = OUT / "E9_figuras"
X6_FIG = OUT / "X6_figuras"
FIG_E6_P1 = E6_FIG / "E6_indice_P1_agrupado.png"
FIGS_E6_F13 = [E6_FIG / f"E6_F1_3_V{k}.png" for k in (2, 3)]  # o ciclo 1 é o gráfico RD da seção 4
FIG_E7_NIVEL = E7_FIG / "E7_nivel_F3_1_U.png"
FIG_E7_DIRD = E7_FIG / "E7_dird_F3_1_U.png"
FIG_E7_EVENTO = E7_FIG / "E7_evento_F3_1_U.png"
FIG_E9 = E9_FIG / "E9_utilidade_ivs.png"
FIG_X6 = X6_FIG / "X6_descartes.png"
PROD_E6 = ROOT / "scripts" / "rdd_bolsa" / "13_estimar_E6_funil.py"
PROD_E7 = ROOT / "scripts" / "rdd_bolsa" / "14_estimar_E7_dird_cnes.py"
PROD_E9 = ROOT / "scripts" / "rdd_bolsa" / "16_estimar_E9_escolha.py"
PROD_X6 = ROOT / "scripts" / "rdd_bolsa" / "20_poder_descartes.py"

# Arquivos lidos para os números e para as tabelas (o teste usa esta lista para rastrear os números).
FONTES_NUMEROS = [R1_OFICIAL, MATRIZ, A08_MANIFESTO, A10_DIAG, PROT40, E3_STATUS, E3_EST, E3_DIAG, E3_CONF, E5_ESPEC,
                  E5_RES, E6_EST, E6_DIAG, E7_EST, E8_RES, E8_TAB, E9_ROB, X1_RES, X2_DESC, X2_EST, X3_EST,
                  X6_EST, X6_RES]
FIGURAS_PIPELINE = {FIG_REGRA: SCRIPT_REGRA, FIG_E6_P1: PROD_E6, **{f: PROD_E6 for f in FIGS_E6_F13},
                    FIG_E7_NIVEL: PROD_E7, FIG_E7_DIRD: PROD_E7, FIG_E7_EVENTO: PROD_E7, FIG_E9: PROD_E9,
                    FIG_X6: PROD_X6}
ENTRADAS_HASH = [R1_OFICIAL, MATRIZ, ESCORE, IVS_OFICIAL, E4_PROP, PROTOCOLO, PROT40, E3_STATUS, E3_EST, E3_DIAG,
                 E3_CONF, E5_ESPEC, E5_RES, E6_EST, E6_DIAG, E7_EST, E8_RES, E8_TAB, E9_ROB, X1_RES, X2_DESC,
                 X2_EST, X3_EST, X6_EST, X6_RES, A10_DIAG, A08_MANIFESTO]

TITULO = "RDD da bolsa do PMM-E: relatório de validação"
OUTCOME_FRAC = "fracao_celulas_ch1_com_confirmacao_ou_homologacao"
OUTCOME_D = "D_k_especialista_ativo_do_ciclo"
ALFA_REF_PP = 0.10  # referência de preenchimento do protocolo 40 (+10 p.p.), só para rotular; o valor vem do JSON


# ---------------------------------------------------------------------------
# Módulo do relatório de 46 páginas (funções de formatação e de figura)
# ---------------------------------------------------------------------------


def importar_09():
    """Importa o gerador do relatório completo (nome começa com dígito) sem gravar bytecode."""
    spec = importlib.util.spec_from_file_location("relatorio_rdd_bolsa_09", SCRIPT_09)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


R = importar_09()
br, br_int, br_p, pp, ic_pp, sinal, br_mil, data_br, esc = (R.br, R.br_int, R.br_p, R.pp, R.ic_pp, R.sinal, R.br_mil,
                                                           R.data_br, R.esc)


def rel(p: Path) -> str:
    return R.rel(p)


def ler_json(p: Path):
    if not p.exists():
        raise SystemExit(f"Entrada ausente: {rel(p)}")
    return json.loads(p.read_text(encoding="utf-8"))


def ler_csv(p: Path, **kw) -> pd.DataFrame:
    if not p.exists():
        raise SystemExit(f"Entrada ausente: {rel(p)}")
    return pd.read_csv(p, **kw)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------


def tipo_unidade(u: str) -> str:
    u = str(u)
    if u.startswith("fracao"):
        return "pp"
    if u.startswith("desvios"):
        return "dp"
    if u.startswith("razão") or u.startswith("razao"):
        return "rc"
    if u.startswith("pontos"):
        return "pt"
    if u.startswith("horas"):
        return "h"
    return "n"


ROTULO_UNIDADE = {"pp": "p.p.", "dp": "DP", "rc": "razão", "pt": "pontos", "h": "horas", "n": "contagem"}


def fmt_est(u: str, x) -> str:
    t = tipo_unidade(u)
    if t == "pp":
        return pp(x, 1)
    if t == "dp":
        return sinal(x, 2)
    if t == "rc":
        return br(x, 2)
    if t == "pt":
        return sinal(x, 2)
    if t == "h":
        return sinal(x, 1)
    return sinal(x, 3)


def fmt_ic(u: str, lo, hi) -> str:
    return f"[{fmt_est(u, lo)}; {fmt_est(u, hi)}]"


def n_lados(a, b) -> str:
    return f"{br_int(a)} / {br_int(b)}"


def corte_txt(c) -> str:
    try:
        return br(float(c), 3)
    except (TypeError, ValueError):
        return str(c)


def nome_cov(v: str) -> str:
    base = {"ivs_infra_2010": "IVS infraestrutura", "ivs_ch_2010": "IVS capital humano", "ivs_rt_2010": "IVS renda e trabalho",
            "log_populacao_2010": "log população 2010", "rdpc_2010": "renda per capita 2010",
            "estrato_capital": "estrato capital", "estrato_interior_proximo_polo": "estrato interior próximo de polo",
            "estrato_interior_remoto": "estrato interior remoto", "estrato_metropolitano": "estrato metropolitano"}
    return base.get(v, v.replace("_", " "))


# ---------------------------------------------------------------------------
# Carga dos dados e conferências (sem data/)
# ---------------------------------------------------------------------------


def carregar() -> dict:
    faltam = [rel(p) for p in FONTES_NUMEROS + [ESCORE, IVS_OFICIAL, E4_PROP, PROTOCOLO] + list(FIGURAS_PIPELINE)
              if not p.exists()]
    if faltam:
        raise SystemExit("Entradas ausentes: " + ", ".join(faltam))
    r1 = ler_json(R1_OFICIAL)
    st = ler_json(E3_STATUS)
    if r1.get("decisao_r1") != "APROVADO_SHARP":
        raise SystemExit(f"R1 não aprovado: {r1.get('decisao_r1')}")
    if st.get("status") != "CONCLUIDO":
        raise SystemExit(f"E3 não concluído: {st.get('status')}")
    cortes = sorted(float(c) for c in st["cortes"])
    c_mil = [int(round(c * 1000)) for c in cortes]
    mat = ler_csv(MATRIZ, dtype={"co_ibge": str})
    valores = mat.groupby("faixa_anunciada")["valor_anunciado_brl"].agg(lambda s: sorted(set(s)))
    if any(len(v) != 1 for v in valores) or len(valores) != 3:
        raise SystemExit("A bolsa não é função única da faixa na matriz")
    valor_faixa = {f: float(v[0]) for f, v in valores.items()}
    faixas = sorted(valor_faixa, key=valor_faixa.get)
    of = ler_csv(IVS_OFICIAL, dtype={"co_ibge": str})
    of["s_mil"] = R.milesimos(of["ivs"])
    esc_ = ler_csv(ESCORE, dtype={"co_ibge": str})
    esc_["s_mil"] = R.milesimos(esc_["ivs_admin"])
    j = of[["co_ibge", "s_mil"]].merge(esc_[["co_ibge", "s_mil"]], on="co_ibge", how="outer", suffixes=("_of", "_esc"))
    if len(j) != len(of) or not np.array_equal(j["s_mil_of"].to_numpy(), j["s_mil_esc"].to_numpy()):
        raise SystemExit("O escore completo do E3 não é o IVS 2010 oficial (a08)")
    base = mat[["quadro", "co_ibge", "faixa_anunciada", "valor_anunciado_brl"]].merge(
        of[["co_ibge", "ivs", "s_mil"]], on="co_ibge", how="left")
    est = ler_csv(E3_EST)
    diag = ler_csv(E3_DIAG)
    conf = ler_json(E3_CONF)
    if conf.get("status") != "CONFERIDO":
        raise SystemExit(f"Conferência do sinal com status {conf.get('status')}")
    sha_reg = ((conf.get("entradas") or {}).get(rel(E3_EST)) or {}).get("sha256")
    if sha_reg != sha256(E3_EST):
        raise SystemExit("E3_conferencia_sinal.json não corresponde ao E3_estimativas.csv atual (rode 09b)")
    ctx = {"r1": r1, "st": st, "prot": ler_json(PROTOCOLO), "prot40": ler_json(PROT40), "cortes": cortes,
           "c_mil": c_mil, "valor_faixa": valor_faixa, "faixas": faixas, "base": base, "est": est, "diag": diag,
           "conf": conf, "h_principal": float(st["janelas"]["principal"]),
           "h_sens": [float(h) for h in st["janelas"]["sensibilidade"]]}
    # populações P1 e P2 só com o IVS oficial e, em P1, a fração preenchida do E4 (nada de data/)
    prop = ler_csv(E4_PROP, dtype={"co_ibge": str})
    pops = {}
    for nome in ("P1", "P2"):
        g = R.populacao(base, nome)[["co_ibge", "s_mil", "ivs", "faixa_anunciada", "valor_anunciado_brl"]].copy()
        if g["s_mil"].isna().any():
            raise SystemExit(f"Município de {nome} sem IVS oficial")
        if nome == "P1":
            if set(prop["co_ibge"]) != set(g["co_ibge"]):
                raise SystemExit("E4_proporcao_municipio.csv não cobre exatamente os municípios de P1")
            g = g.merge(prop[["co_ibge", "y1"]].rename(columns={"y1": OUTCOME_FRAC}), on="co_ibge", how="left")
        pops[nome] = g.reset_index(drop=True)
    ctx["pops"] = pops
    ctx["e5"] = ler_csv(E5_ESPEC, dtype={"corte": str})
    ctx["e5res"] = ler_json(E5_RES)
    ctx["e6"] = ler_csv(E6_EST, dtype={"corte": str, "ciclo": str})
    ctx["e6d"] = ler_csv(E6_DIAG, dtype={"corte": str})
    ctx["e7"] = ler_csv(E7_EST, dtype={"corte": str})
    ctx["e8"] = ler_json(E8_RES)
    ctx["e8t"] = ler_csv(E8_TAB, dtype={"ciclo": str, "corte": str})
    ctx["e9rob"] = ler_csv(E9_ROB, dtype={"ciclo": str})
    ctx["a10"] = ler_json(A10_DIAG)
    ctx["a08"] = ler_json(A08_MANIFESTO)
    ctx["x1"] = ler_json(X1_RES)
    ctx["x6"] = ler_csv(X6_EST, dtype={"corte": str, "ciclo": str})
    ctx["x6r"] = ler_json(X6_RES)
    return ctx


def dados_graficos(ctx) -> None:
    """Painéis do gráfico RD (só F1.3 no ciclo 1) e da densidade, conferidos contra o E3, como no relatório longo."""
    R.COMBOS_RD = [("P1", OUTCOME_FRAC)]  # o gráfico da seção 4 é o do outcome original (preenchimento, ciclo 1)
    ctx["paineis_rd"] = R.dados_rd(ctx)
    ctx["densidade"] = [d for d in R.dados_densidade(ctx) if d["pop"] == "P1"]


# ---------------------------------------------------------------------------
# Blocos de HTML
# ---------------------------------------------------------------------------


def fonte(arquivos: list[Path], produtor: Path | None, desenho: bool, extra: str = "") -> str:
    lista = "; ".join(f"<code>{esc(rel(a))}</code>" for a in arquivos)
    prod = ""
    if produtor is not None:
        prod = (f" Figura gravada por <code>{esc(rel(produtor))}</code> e incorporada sem alteração."
                if not desenho else f" Gráfico desenhado por <code>{esc(rel(produtor))}</code>.")
    ex = f" {extra}" if extra else ""
    return f'<div class="fonte">Fonte: {lista}.{prod}{ex}</div>'


def fig_png(titulo: str, arquivos: list[Path], sub: str = "", nota: str = "", classe: str = "") -> str:
    imgs = "".join(R.img_png(p, classe) for p in arquivos)
    prod = FIGURAS_PIPELINE[arquivos[0]]
    return R.figura(titulo, imgs, fonte(arquivos, prod, False), sub=sub, nota=nota)


def fig_svg(titulo: str, svg: str, arquivos: list[Path], sub: str = "", nota: str = "", chave: str | None = None) -> str:
    return R.figura(titulo, svg, fonte(arquivos, ESTE_SCRIPT, True,
                                       extra="Cálculo de exibição conferido contra o E3 na geração."),
                    sub=sub, nota=nota, chave=chave)


def caixa(titulo: str, corpo: str, classe: str = "") -> str:
    return f'<div class="caixa {classe}"><p class="caixa-tit">{titulo}</p>{corpo}</div>'


def lista(itens: list[str], classe: str = "") -> str:
    cl = f' class="{classe}"' if classe else ""
    return f"<ul{cl}>" + "".join(f"<li>{i}</li>" for i in itens) + "</ul>"


def tab(cabecalho, linhas, titulo, legenda="", rodape="", classe="compacta", inteiro=None) -> str:
    return R.tabela(cabecalho, linhas, classe=classe, titulo=titulo, legenda=legenda, rodape=rodape, inteiro=inteiro)


def linha_est(est: pd.DataFrame, **f) -> pd.Series:
    d = est
    for k, v in f.items():
        d = d[d[k] == v]
    if len(d) != 1:
        raise SystemExit(f"Esperada 1 linha para {f}, achei {len(d)}")
    return d.iloc[0]


def grade_texto(ctx) -> tuple[str, str, str, str]:
    vf, fx = ctx["valor_faixa"], ctx["faixas"]
    g = [br_mil(vf[f]) for f in fx]
    passo = br_mil(vf[fx[1]] - vf[fx[0]])
    return g[0], g[1], g[2], passo


def ref_evento(ctx) -> str:
    """Competência (AAAAMM) de referência do estudo de evento, lida do texto do protocolo 40."""
    import re
    m = re.search(r"relativo a (\d{6})", ctx["prot40"]["familias"]["F3"]["janelas"]["evento"])
    if not m:
        raise SystemExit("Referência do estudo de evento não encontrada no protocolo 40")
    return m.group(1)


def poder_txt(ctx) -> str:
    """Poder do efeito mínimo detectável (em %), lido dos parâmetros do X6."""
    return br(100 * ctx["x6r"]["parametros"]["poder"], 0)


def alfa_txt(ctx) -> str:
    """Nível dos testes (em %), lido dos parâmetros do X6."""
    return br(100 * ctx["x6r"]["parametros"]["alfa"], 0)


def ref_pp(ctx) -> str:
    """Referência de preenchimento do protocolo (em p.p., sem sinal), lida da síntese E8."""
    return br(100 * ctx["e8"]["descarte"]["referencias"]["preenchimento_pp"], 0)


# ---------------------------------------------------------------------------
# Seções
# ---------------------------------------------------------------------------


def secao_cabecalho(ctx) -> str:
    e8 = ctx["e8"]
    data = data_br(e8["data_execucao"])
    return (
        '<header class="cab">'
        '<div class="kicker">Relatório para validação metodológica</div>'
        "<h1>RDD do adicional de bolsa do PMM-E: desenho, diagnósticos e resultados até agora</h1>"
        f'<p class="lead">Estado em {esc(data)}, com os outcomes atuais. Documento de trabalho para os professores '
        "validarem o desenho e a leitura dos resultados. Não é decisão sobre a hipótese econômica.</p>"
        "</header>"
    )


def secao_resumo(ctx) -> str:
    e8, e3 = ctx["e8"], ctx["est"]
    g0, g1, g2, passo = grade_texto(ctx)
    p = ctx["r1"]["populacoes"]
    h = e8["holm"]
    a1 = linha_est(e3, populacao="P1", outcome=OUTCOME_FRAC, corte=0.3, especificacao="principal")
    a2 = linha_est(e3, populacao="P1", outcome=OUTCOME_FRAC, corte=0.4, especificacao="principal")
    e5 = ctx["e5"]
    m1 = linha_est(e5, outcome="Y1", especificacao="S0", corte="0.3")
    m2 = linha_est(e5, outcome="Y1", especificacao="S0", corte="0.4")
    c2 = e8["e9"]["principal"]["2"]
    emp = e8["e9"]["principal"]["empilhado"]
    f13 = next(d for d in e8["descarte"]["preenchimento"] if d["outcome_id"] == "F1.3" and d["populacao"] == "V1+V2+V3")
    itens = [
        f"<strong>Pergunta.</strong> No corte do IVS 2010 oficial, onde a bolsa anunciada sobe {passo} "
        f"({g0} para {g1} em {br(ctx['cortes'][0])}; {g1} para {g2} em {br(ctx['cortes'][1])}), o lado de bolsa maior "
        "tem mais preenchimento, presença e oferta de especialistas? O contraste é o incentivo marginal anunciado, "
        "dentro de um pacote de regras que mudam nos mesmos cortes. Não é o efeito de participar do PMM-E.",
        f"<strong>Regra e validade.</strong> A regra é sharp: o IVS oficial reproduz a faixa anunciada em "
        f"{br_int(p['P1']['regra_reproduz'])} de {br_int(p['P1']['municipios'])} municípios do ciclo 1 e em "
        f"{br_int(p['P2']['regra_reproduz'])} de {br_int(p['P2']['municipios'])} do ciclo 2. Não há salto de densidade "
        "nos cortes; o balanço de covariáveis tem poucos desequilíbrios, o maior no corte "
        f"{br(ctx['cortes'][1])} do ciclo 1 (seção 3).",
        f"<strong>Outcome original (E3, ciclo 1, fração de células preenchidas na 1ª chamada).</strong> Salto de "
        f"{pp(a1['tau'])} p.p. {ic_pp(a1['ic95_inf'], a1['ic95_sup'])} em {br(ctx['cortes'][0])} e de {pp(a2['tau'])} p.p. "
        f"{ic_pp(a2['ic95_inf'], a2['ic95_sup'])} em {br(ctx['cortes'][1])}. Nada é distinguível de zero, e o efeito mínimo "
        f"detectável ({poder_txt(ctx)}% de poder) é de cerca de{br(100 * m1['mde_80'], 1)} e {br(100 * m2['mde_80'], 1)} p.p.: "
        "resultado inconclusivo, não prova de ineficácia.",
        f"<strong>Rodada multi-outcome (protocolo 40, congelado antes de abrir os outcomes).</strong> Nenhuma das duas "
        f"primárias rejeita zero depois do Holm: índice de atração-presença P1 ({fmt_est(h['P1']['unidade'], h['P1']['tau'])} "
        f"DP, p ajustado {br(h['P1']['p_holm'], 3)}) e oferta de especialistas no CNES por DiRD P2 "
        f"(p ajustado {br(h['P2']['p_holm'], 3)}).",
        f"<strong>Único sinal que resiste a vários testes.</strong> Na escolha da 1ª opção pelos candidatos (E9, "
        f"secundário e exploratório), a razão de chances por {passo} é {br(c2['rc_5mil'], 2)} no ciclo 2 "
        f"[{br(c2['rc_5mil_ic95'][0], 2)}; {br(c2['rc_5mil_ic95'][1], 2)}], mas o empilhado dos três ciclos "
        f"({br(emp['rc_5mil'], 2)}) é frágil. É realocação entre "
        "células, não expansão do total de candidatos.",
        f"<strong>O que os ICs descartam.</strong> Com ciclos e cortes empilhados, o IC convencional do preenchimento "
        f"na 1ª chamada vai até {pp(f13['ic95_sup'])} p.p., abaixo da referência de +{br(100 * e8['descarte']['referencias']['preenchimento_pp'], 0)} p.p. "
        "do protocolo. Isso vale só sob a aproximação local linear e para o pacote do corte; o IC honesto não descarta nada.",
    ]
    return ('<section class="resumo"><h2>Em uma página</h2>' + lista(itens, "resumo-lista")
            + caixa("O que pedimos aos professores",
                    "<p>Validar (i) o estimando e o que o contraste identifica; (ii) o desenho e os diagnósticos de "
                    "validade; (iii) a leitura dos resultados, todos nulos ou inconclusivos exceto o sinal frágil da "
                    "escolha. As perguntas abertas estão na seção 8.</p>"
                    "<p class=\"nota\">Rótulos: <em>pré-especificado</em> = protocolo congelado antes de abrir os "
                    "outcomes (E3, E6, E7, e as duas primárias); <em>exploratório</em> = decidido depois de ver "
                    "resultados (E5, E9 pós-auditoria, X1 a X6). Uma análise de produção (SIA/SIH/TISS) está em "
                    "andamento e não entra aqui.</p>") + "</section>")


def secao_estimando(ctx) -> str:
    g0, g1, g2, passo = grade_texto(ctx)
    cortes = ctx["cortes"]
    cadeia = ("implementação → força de trabalho → capacidade → acesso → saúde → custos e bem-estar → equidade e "
              "spillovers")
    tabela_contr = tab(
        [("Contraste", "txt"), ("Onde", "txt"), ("O que identifica", "txt"), ("O que não identifica", "txt")],
        [["RDD em nível", "E3, E6",
          "pacote do corte: a bolsa anunciada mais as outras regras federais que mudam nos mesmos cortes",
          "a bolsa pura; participar do PMM-E; o Agora Tem Especialistas"],
         ["DiRD (diferença em descontinuidades)", "E7, CNES",
          "bolsa mais a variação, entre pré e pós, das descontinuidades das outras políticas",
          "a bolsa pura: só tira a parte das outras regras que é constante no tempo"],
         ["Logit condicional da 1ª opção", "E9",
          "o degrau da bolsa na escolha entre células do mesmo curso e ciclo (realocação, condicional a candidatar-se)",
          "efeito sobre o total de candidatos, o preenchimento ou a oferta local"]],
        "O que cada contraste identifica", inteiro=True)
    return (
        '<section><h2>1. Pergunta, estimando e o que o contraste identifica</h2>'
        f"<p>A hipótese levada à banca 1 é que a bolsa maior atrai e fixa mais especialistas. Na forma local: no corte "
        f"do IVS 2010 oficial do município, onde a bolsa anunciada sobe {passo}, o lado de cima tem mais preenchimento "
        "das vagas, mais presença de especialistas e mais oferta cadastrada? A grade do edital é "
        f"{g0} (IVS até {br(cortes[0])}), {g1} (de {br(cortes[0])} a {br(cortes[1])}) e {g2} (acima de {br(cortes[1])}).</p>"
        '<p class="formula">τ(c) = lim<sub>s↓c</sub> E[Y | IVS = s] − lim<sub>s↑c</sub> E[Y | IVS = s], '
        f"c ∈ {{{br(cortes[0])}; {br(cortes[1])}}}</p>"
        "<p><strong>Convenção do sinal.</strong> Salto = valor estimado no corte do lado com bolsa maior (IVS acima do "
        "corte) menos o do lado com bolsa menor. O próprio corte pertence ao lado de baixo (tratamento = 1 se IVS &gt; c). "
        f"Salto positivo significa mais do outcome onde a bolsa é {passo} maior. Em cada gráfico e tabela o sinal é "
        "esse; ele foi conferido no código e nos dados (seção 4).</p>"
        "<p><strong>Estimando.</strong> O efeito candidato é o incentivo marginal anunciado de "
        f"{passo}, localmente, para municípios com IVS perto do corte. Em nível, nesses cortes mudam também outras regras "
        "federais (teto de vagas do PMMB em coparticipação, estrato do financiamento da APS por porte, teto de emendas e "
        f"parcelas de custeio da MAC e, em {br(cortes[1])}, a ajuda de custo do PMMB; auditoria 18). Por isso o contraste é "
        "um pacote, e a tabela abaixo diz o que cada análise identifica.</p>"
        + tabela_contr
        + f"<p><strong>Cadeia de análise.</strong> {cadeia}. Os outcomes atuais cobrem só os primeiros elos: "
        "seleção e implementação (F0), atração (F1) e escolha (E9), presença (F2), oferta cadastrada no CNES (F3) e "
        "seleção de quem chega (F4). Acesso, saúde e custos ainda não entram. Vínculo cadastrado, produção, acesso e "
        "saúde não são sinônimos, e presença no retrato de outubro não é retenção individual.</p>"
        "</section>")


def tabela_r1(ctx) -> str:
    p = ctx["r1"]["populacoes"]
    nome = {"P1": "Ciclo 1 (1ª chamada)", "P2": "Ciclo 2 (1ª e 2ª chamadas)", "ciclo_3_congelado": "Ciclo 3 (1ª chamada)"}
    linhas = []
    for k in ("P1", "P2", "ciclo_3_congelado"):
        d = p[k]
        linhas.append([nome[k], br_int(d["municipios"]), br_int(d["com_ivs_oficial"]), br_int(d["regra_reproduz"])])
    return tab([("Quadro de vagas", "txt"), ("Municípios", "num"), ("Com IVS oficial", "num"),
                ("Faixa anunciada reproduzida", "num")], linhas, "Portão R1: o IVS oficial reproduz a faixa anunciada",
               rodape=fonte([R1_OFICIAL], None, False), inteiro=True, classe="compacta estreita")


def secao_dados(ctx) -> str:
    r1 = ctx["r1"]
    a10 = ctx["a10"]
    a08 = ctx["a08"]
    iguais = r1["escore_administrativo_e_ivs_2010_oficial"]
    g0, g1, g2, passo = grade_texto(ctx)
    prot = ctx["prot40"]
    janelas = prot["familias"]["F3"]["janelas"]
    linhas = [
        ["Running variable", "IVS 2010 oficial do Ipea (Atlas da Vulnerabilidade Social, base completa, Censo 2010, "
                             f"linha Total); {br_int(a08['saida']['municipios'])} municípios",
         "município (co_ibge, 6 dígitos)"],
        ["Regra da bolsa", "quadros de vagas publicados pelo MS por ciclo e chamada (faixa e valor por município)",
         "município"],
        ["Funil do ciclo (F0, F1, F2, F4)", "quadros de vagas e resultados das chamadas, reconstruídos às cegas "
                                            "(doc 41a): células CNES–curso por município", "célula e município"],
        ["Presença (D, F2)", "Relação Nominal de ativos do PMM-E (retrato de 09/10/2026 no E3)", "município"],
        ["Oferta no CNES (F3)", "vínculos nas CBO-alvo por 10 mil hab. (Censo 2022); pré "
                                f"{esc(janelas['pre_principal'])}, pós {esc(janelas['pos'])} (competências AAAAMM)",
         "município × mês"],
        ["Escolha (E9)", "1ª opção dos candidatos entre células do mesmo curso e ciclo", "candidato × célula"],
    ]
    t_r1 = tabela_r1(ctx)  # numerada antes da tabela de dados, na ordem em que aparecem
    tabela_dados = tab([("Elemento", "txt"), ("Fonte e cobertura", "txt"), ("Unidade e chave", "txt")], linhas,
                       "Dados usados (arquivos e hashes no apêndice)", inteiro=True)
    figura_regra = fig_png(f"A bolsa anunciada é função do IVS 2010 oficial: degraus em {br(ctx['cortes'][0])} e "
                           f"{br(ctx['cortes'][1])}", [FIG_REGRA],
                           sub="Cada ponto é um município do quadro de vagas, no valor exato da bolsa; a cor repete o IVS do "
                               "eixo horizontal.")
    falha = caixa(
        "Registro de um failure mode: o arquivo de IVS antigo",
        "<p>Até 14/10/2026 o projeto usou como \"IVS 2010\" um arquivo local em <code>data/</code> que não é o IVS do "
        "município: é, em cada município, a última linha de subgrupo com IVS preenchido da mesma base do Ipea (mulheres, "
        "em recortes de cor e domicílio). A auditoria 16 documentou isso. <strong>Nenhum número calculado com esse "
        "arquivo entra neste relatório, nem como resultado nem como comparação.</strong> Tudo o que depende do IVS foi "
        "reestimado com a base oficial (auditoria 19), e o arquivo antigo só sobrevive como registro de erro, separado.</p>",
        "aviso")
    return (
        '<section><h2>2. Dados e running variable</h2>'
        f"<p>A running variable é o <strong>IVS 2010 oficial do Ipea</strong>. Ele coincide com o escore administrativo do "
        f"Ministério da Saúde (valores iguais até a 3ª casa em {esc(iguais['valores_iguais_3_casas'])} municípios com escore "
        f"administrativo) e reproduz as faixas da bolsa com cortes em {br(ctx['cortes'][0])} e {br(ctx['cortes'][1])}. "
        "A regra é, portanto, <em>sharp</em>: a faixa anunciada é função determinística do IVS, sem municípios do lado "
        "errado. O IVS foi construído com dados do Censo 2010, uma década antes do programa, o que torna a manipulação "
        f"do escore pelos municípios implausível. Há {br_int(a10['totais']['sobre_os_cortes_da_bolsa'])} municípios com IVS "
        "exatamente igual a um dos cortes; todos ficam no lado de baixo, como na regra do MS.</p>"
        + t_r1 + figura_regra + tabela_dados + falha + "</section>")


def tabela_densidade(ctx) -> str:
    d = ctx["e6d"]
    d = d[(d["diagnostico"] == "densidade_poisson_mass_points") & np.isclose(d["h"], ctx["h_principal"])]
    nome = {"U": "Todos os municípios (U)", "V1": "Ciclo 1 (V1)", "V2": "Ciclo 2 (V2)", "V3": "Ciclo 3 (V3)"}
    linhas = []
    contem = []
    for pop in ("U", "V1", "V2", "V3"):
        for c in ("0.300", "0.400"):
            r = d[(d["populacao"] == pop) & (d["corte"].astype(str).str.ljust(5, "0") == c)]
            if len(r) != 1:
                raise SystemExit(f"E6_diagnosticos sem densidade única para {pop}/{c}")
            r = r.iloc[0]
            contem.append(r["rho_ic95_inf"] <= 1 <= r["rho_ic95_sup"])
            linhas.append([nome[pop], br(float(c), 3), n_lados(r["n_abaixo"], r["n_acima"]), br(r["rho"], 2),
                           f"[{br(r['rho_ic95_inf'], 2)}; {br(r['rho_ic95_sup'], 2)}]", br_p(r["p_valor"])])
    ctx["dens_contem"] = (int(sum(contem)), len(contem))
    return tab([("População", "txt"), ("Corte", "num"), ("n abaixo / acima", "num"), ("Razão de densidades", "num"),
                ("IC 95%", "num"), ("p", "num")], linhas,
               "Densidade do IVS nos cortes (razão acima/abaixo; 1 = sem salto)",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> Ajuste Poisson log-linear das contagens por '
                       f"valor de IVS (h = {br(ctx['h_principal'], 3)}), um por lado. Razão 1 = sem descontinuidade na "
                       "densidade. Diagnóstico sem hipótese de efeito: o desejável é não haver salto.</p>",
               rodape=fonte([E6_DIAG], None, False))


def tabela_balanco(ctx) -> str:
    d = ctx["e6d"]
    d = d[(d["diagnostico"] == "balanco_covariavel_pre") & np.isclose(d["h"], ctx["h_principal"]) & d["p_valor"].notna()]
    linhas = []
    for pop in ("U", "V1", "V2", "V3"):
        for c in ("0.300", "0.400"):
            g = d[(d["populacao"] == pop) & (d["corte"].astype(str).str.ljust(5, "0") == c)]
            sig = g[g["p_valor"] < 0.05]
            quais = "; ".join(f"{nome_cov(r.variavel)} ({sinal(r.tau, 3)}; p = {br(r.p_valor, 3)})"
                              for r in sig.itertuples()) or "—"
            linhas.append([pop, br(float(c), 3), br_int(len(g)), br_int(len(sig)), quais])
    return tab([("Pop.", "txt"), ("Corte", "num"), ("Testadas", "num"), ("p < 0,05", "num"),
                ("Quais (salto; p)", "txt")], linhas,
               "Balanço de covariáveis pré-programa nos cortes (h = " + br(ctx["h_principal"], 3) + ")",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> Salto de cada covariável fixada antes do '
                       "programa, pela mesma RDD local linear. O próprio IVS fica de fora (é a running variable). Parte dos "
                       "p &lt; 0,05 é esperada por acaso, e os subíndices do IVS não são testes independentes.</p>",
               rodape=fonte([E6_DIAG], None, False))


def tabela_placebos(ctx) -> str:
    r = ctx["e9rob"]
    r = r[r["analise"] == "placebo_cortes"]
    linhas = []
    for ciclo in ("1", "2", "3", "empilhado"):
        g = r[r["ciclo"] == ciclo]
        v = {row.estatistica: row.valor for row in g.itertuples()}
        linhas.append([ciclo if ciclo != "empilhado" else "empilhado", br_int(v["n_placebos"]), br(v["t_real"], 2),
                       br(100 * v["fracao_abs_t_placebo_maior_que_1_96"], 1) + "%",
                       br_int(v["n_abs_t_placebo_maior_ou_igual_ao_real"]), br(v["p_posto"], 3)])
    return tab([("Ciclo", "txt"), ("Cortes falsos", "num"), ("t da bolsa", "num"), ("Placebos com |t| > 1,96", "num"),
               ("Placebos com |t| ≥ t real", "num"), ("p por posto", "num")], linhas,
               "Placebo de cortes no E9 (logit condicional da escolha; exploratório, pós-auditoria)",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> Repete-se o degrau do E9 em cortes falsos de '
                       f"IVS fora das vizinhanças dos cortes verdadeiros. Se o |t| dos falsos passa de 1,96 bem mais que {alfa_txt(ctx)}% das "
                       "vezes, o EP com cluster por conjunto subestima a incerteza. O p por posto compara o t real com os "
                       "falsos.</p>", rodape=fonte([E9_ROB], None, False))


def tabela_e7_placebos(ctx) -> str:
    e7 = ctx["e7"]
    linhas = []
    rot = {"F3.1": "F3.1 vínculos nas CBO-alvo (principal)", "F3.P1": "F3.P1 placebo: generalistas",
           "F3.P2": "F3.P2 placebo: especialistas fora das CBO-alvo"}
    for oid in ("F3.1", "F3.P1", "F3.P2"):
        for c in ("0.300", "0.400", "empilhado"):
            r = linha_est(e7, outcome_id=oid, populacao="U", corte=c, especificacao="principal")
            linhas.append([rot[oid], corte_txt(c) if c != "empilhado" else "empilhado", fmt_est("n", r["tau"]),
                           fmt_ic("n", r["ic95_inf"], r["ic95_sup"]), br_p(r["p_valor"])])
    pre = linha_est(e7, outcome_id="F3.1", populacao="U", corte="0.300", especificacao="nivel_pre")
    linhas.append(["F3.1 em nível no pré (pré-existente)", corte_txt("0.300"), fmt_est("n", pre["tau"]),
                   fmt_ic("n", pre["ic95_inf"], pre["ic95_sup"]), br_p(pre["p_valor"])])
    return tab([("Outcome (DiRD em U)", "txt"), ("Corte", "num"), ("Salto", "num"), ("IC 95%", "num"), ("p", "num")],
               linhas, "E7: DiRD no CNES, placebos de outcome e descontinuidade pré-existente",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> Unidade: vínculos por 10 mil hab. (Censo 2022). '
                       "Salto da DiRD = salto de (média do pós − média do pré), lado com bolsa maior − lado com bolsa menor. "
                       "Os placebos (generalistas; especialistas fora das CBO-alvo) não deveriam responder à bolsa. A última "
                       "linha é o salto do <em>nível</em> no pré, antes das regras da bolsa.</p>",
               rodape=fonte([E7_EST], None, False))


def secao_validade(ctx) -> str:
    fig_dens = fig_svg(
        f"Histograma do IVS em torno de cada corte, ciclo 1 (V1), com a contagem esperada sem salto", R.fig_densidade(
            ctx, ctx["densidade"]), [E3_DIAG, ESCORE],
        sub="Barras = municípios por faixa do IVS (largura de " + br(R.BIN_DENS_MIL / 1000, 3) + "); linha = ajuste log-linear do E3 (um por lado).")
    td = tabela_densidade(ctx)
    n_ok, n_tot = ctx["dens_contem"]
    q = ctx["a10"]
    sel = ctx["e8"]["selecao_v1_0400"]
    return (
        '<section><h2>3. Validade: densidade, balanço, placebos e cointervenções</h2>'
        "<h3>3.1 Manipulação do IVS: densidade nos cortes</h3>"
        f"<p>Em {n_ok} de {n_tot} combinações de população e corte o IC 95% da razão de densidades contém 1. Nenhum corte "
        "tem excesso ou falta de municípios de um lado, como se espera de um escore construído com o Censo 2010.</p>"
        + fig_dens + td
        + "<h3>3.2 Balanço de covariáveis</h3>" + tabela_balanco(ctx)
        + "<p>Os desequilíbrios são poucos. Há alguns isolados em U e em V2 no corte "
          f"{br(ctx['cortes'][0])}; o maior grupo está no ciclo 1 em {br(ctx['cortes'][1])} (V1), no sentido de "
          "municípios menos metropolitanos acima do corte. Nesse mesmo "
          f"recorte a razão de densidades é {br(sel['densidade_V1_0400']['razao'], 2)} "
          f"[{br(sel['densidade_V1_0400']['ic95'][0], 2)}; {br(sel['densidade_V1_0400']['ic95'][1], 2)}] e as vagas "
          "imediatas por 10 mil hab. do ciclo 1 caem do lado de bolsa maior "
          f"({fmt_est('n', sel['vagas_imediatas_c1_0400']['tau'])} "
          f"{fmt_ic('n', sel['vagas_imediatas_c1_0400']['ic95_inf'], sel['vagas_imediatas_c1_0400']['ic95_sup'])}, em U; "
          f"p = {br(sel['vagas_imediatas_c1_0400']['p_valor'], 3)}, q BKY = {br(sel['vagas_imediatas_c1_0400']['q_bky'], 3)}). "
          "Isso torna V1 em " + br(ctx["cortes"][1]) + " suspeito de seleção: as linhas desse recorte não são lidas como "
          "contraste limpo.</p>"
        + "<h3>3.3 Placebos</h3>" + tabela_placebos(ctx)
        + "<p>O placebo de cortes só existe no E9. Para a RDD em nível (E3 e E6) o protocolo não tem placebo de corte; é "
          "uma das perguntas da seção 8. Nos outcomes do CNES os placebos de outcome estão na tabela da seção 5.</p>"
        + "<h3>3.4 Cointervenções nos mesmos cortes</h3>"
        + lista([
            "<strong>Portaria do teto de vagas do PMMB em coparticipação (752/2023):</strong> o teto de novas vagas sobe "
            f"em {br(ctx['cortes'][0])} e em {br(ctx['cortes'][1])}. Mexe em generalistas (eSF), só indiretamente em "
            "especialistas.",
            "<strong>Cofinanciamento da APS (3.493/2024, IED):</strong> o valor por equipe muda em "
            f"{br(ctx['cortes'][0])} e em {br(ctx['cortes'][1])}, conforme o porte.",
            "<strong>Teto de emendas e parcelas de custeio da MAC:</strong> acréscimo para municípios com \"IVS maior que "
            "0,3\", que cobre componentes do Agora Tem Especialistas. É a mais próxima da atenção especializada.",
            f"<strong>Ajuda de custo do PMMB em {br(ctx['cortes'][1])}</strong> (fora da Amazônia Legal e da faixa de "
            "fronteira).",
        ]) + "<p>Fonte: auditoria 18 (texto dos atos citado em <code>output/aquisicao/a10_manifesto_normas_ivs.json</code>; "
             f"{br_int(q['totais']['fontes_no_manifesto'])} fontes). Consequências: (i) a RDD em nível mede um pacote; (ii) a "
             "DiRD remove só a parte constante no tempo dessas regras; (iii) as heterogeneidades por porte e por Amazônia "
             "Legal (S3 e S4 do protocolo) são suplementares e de baixa potência.</p>"
        + "</section>")


def fig_rd(ctx) -> str:
    svg = R.fig_rd_local(ctx, ctx["paineis_rd"], [("P1", OUTCOME_FRAC)])
    return fig_svg("RDD tradicional: fração de células preenchidas na 1ª chamada do ciclo 1 (E3, outcome original)", svg,
                   [E3_EST, E3_CONF, E4_PROP, ESCORE],
                   sub=f"Médias por faixa de {br(R.BIN_RD_MIL / 1000, 3)} de IVS (área do ponto proporcional ao número de municípios), reta local "
                       "linear de cada lado e IC 95% pontual (HC1). Salto = reta da direita − reta da esquerda no corte.",
                   chave="rd_e3")


def tabela_e3(ctx) -> str:
    est = ctx["est"]
    h = ctx["h_principal"]
    hs = sorted(ctx["h_sens"])
    linhas = []
    nome_out = {OUTCOME_FRAC: "fração de células preenchidas na 1ª chamada",
                OUTCOME_D: "especialista do ciclo ativo (presença)"}
    nome_pop = {"P1": "Ciclo 1", "P2": "Ciclo 2 (replicação)"}
    for pop, out in (("P1", OUTCOME_FRAC), ("P1", OUTCOME_D), ("P2", OUTCOME_D)):
        for c in ctx["cortes"]:
            r = linha_est(est, populacao=pop, outcome=out, corte=c, h=h)
            sens = []
            for hh in hs:
                s = linha_est(est, populacao=pop, outcome=out, corte=c, h=hh)
                sens.append(pp(s["tau"]) + f" (p = {br(s['p_valor'], 2)})")
            linhas.append([nome_pop[pop], nome_out[out], br(c, 3), n_lados(r["n_abaixo"], r["n_acima"]), pp(r["tau"]),
                           ic_pp(r["ic95_inf"], r["ic95_sup"]), br_p(r["p_valor"]), *sens])
    cab = [("População", "txt"), ("Outcome", "txt"), ("Corte", "num"), ("n abaixo / acima", "num"), ("Salto (p.p.)", "num"),
           ("IC 95%", "num"), ("p", "num")] + [(f"Salto, h = {br(hh, 3)}", "num") for hh in hs]
    return tab(cab, linhas, f"E3: RDD sharp local linear (h = {br(h, 3)}), pré-especificada",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> Salto = lado com bolsa maior − lado com bolsa '
                       "menor, em pontos percentuais; local linear, kernel triangular, EP HC1 por município. Contraste: "
                       "<strong>incentivo marginal anunciado, dentro do pacote do corte</strong>; não é participar do PMM-E. "
                       "As janelas alternativas são sensibilidade.</p>", rodape=fonte([E3_EST], None, False), classe="compacta")


def texto_decomposicao(ctx) -> str:
    conf = ctx["conf"]
    c = next(r for r in conf["por_especificacao"] if r["populacao"] == "P1" and r["outcome"] == OUTCOME_FRAC
             and math.isclose(r["corte"], 0.3) and math.isclose(r["h"], ctx["h_principal"]))
    ind = c["independente"]
    g0, g1, _, _ = grade_texto(ctx)
    return (f"No corte {br(ctx['cortes'][0])}, a média bruta do lado de {g0} é {br(100 * ind['lado_bolsa_menor']['media_bruta'], 1)}% e a "
            f"do lado de {g1} é {br(100 * ind['lado_bolsa_maior']['media_bruta'], 1)}%, mas a reta local linear do lado de "
            f"{g0} chega ao corte em {br(100 * ind['lado_bolsa_menor']['valor_da_reta_no_corte'], 1)}% e a do lado de {g1} "
            f"parte de {br(100 * ind['lado_bolsa_maior']['valor_da_reta_no_corte'], 1)}%. O preenchimento sobe com o IVS "
            "dentro da janela, e esse gradiente explica a diferença bruta; o salto compara as duas retas no corte. A "
            f"diferença bruta de {pp(ind['diferenca_medias_brutas'])} p.p. se decompõe em "
            f"{pp(ind['decomposicao']['salto'])} de salto, {pp(ind['decomposicao']['inclinacao_dentro_da_janela'])} de "
            f"inclinação e {pp(ind['decomposicao']['residuo'])} de resíduo (a decomposição fecha em "
            f"{br(100 * ind['decomposicao']['soma'], 1)}).")


def tabela_precisao(ctx) -> str:
    e5 = ctx["e5"]
    e6 = ctx["e6"]
    linhas = []
    for c, cs in ((0.3, "0.3"), (0.4, "0.4")):
        s0 = linha_est(e5, outcome="Y1", especificacao="S0", corte=cs)
        hon = linha_est(e6, outcome_id="F1.3", populacao="V1", corte=f"{c:.3f}", especificacao="principal")
        linhas.append([br(c, 3), pp(s0["tau"]), ic_pp(s0["ic95_inf"], s0["ic95_sup"]),
                       "[" + pp(hon["ic_honesto_inf"], 0) + "; " + pp(hon["ic_honesto_sup"], 0) + "]",
                       br(100 * s0["mde_80"], 1), pp(s0["lim_sup_unilateral_95"])])
    return tab([("Corte", "num"), ("Salto (p.p.)", "num"), ("IC 95% convencional", "num"),
                ("IC 95% honesto (M do protocolo), p.p.", "num"),
                (f"Efeito mínimo detectável, {poder_txt(ctx)}% (p.p.)", "num"),
                (f"Limite superior unilateral {alfa_txt(ctx)}% (p.p.)", "num")], linhas,
               "Precisão do outcome original (fração preenchida, ciclo 1)",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> O IC honesto (Armstrong e Kolesár) usa o M '
                       "da regra de bolso do protocolo e inclui o viés de aproximação; aqui ele cobre bem mais que o "
                       "intervalo possível de uma fração, ou seja, não informa. O efeito mínimo detectável é "
                       f"{br(ctx['x6r']['parametros']['fator_mde'], 1)} × EP ({br(100 * ctx['x6r']['parametros']['poder'], 0)}% "
                       f"de poder, bicaudal a {br(100 * ctx['x6r']['parametros']['alfa'], 0)}%). O limite unilateral é "
                       "exploratório (E5).</p>",
               rodape=fonte([E5_ESPEC, E6_EST], None, False), inteiro=True)


def tabela_e5(ctx) -> str:
    e5 = ctx["e5"]
    y = e5[e5["outcome"] == "Y1"]
    rot = {"S0": "S0 principal (protocolo)", "A": "A local constante (viesada: ignora inclinações)",
           "B": "B cortes empilhados", "C1": "C1 + estrato, região e log pop.", "C2": "C2 = C1 + IDHM",
           "D": "D local randomization", "E0": "E0 município, peso × nº de células", "E1": "E1 célula, EP por município",
           "E2": "E2 = E1 + efeitos fixos de curso"}
    linhas = []
    mostrar = ("S0", "B", "C1", "D", "E1")  # amostra; as demais estão em E5_especificacoes.csv
    y = y[y["especificacao"].isin(mostrar)].copy()
    y["_o"] = y["especificacao"].map({k: i for i, k in enumerate(mostrar)})
    y = y.sort_values(["_o", "corte"], kind="stable")
    for r in y.itertuples():
        corte = "empilhado" if "+" in str(r.corte) else br(float(r.corte), 3)
        linhas.append([rot.get(r.especificacao, r.especificacao), corte, n_lados(r.n_abaixo, r.n_acima), pp(r.tau),
                       ic_pp(r.ic95_inf, r.ic95_sup), br_p(r.p_valor), pp(r.lim_sup_unilateral_95)])
    return tab([("Especificação", "txt"), ("Corte", "num"), ("n abaixo / acima", "num"), ("Salto (p.p.)", "num"),
                ("IC 95%", "num"), ("p", "num"), (f"Lim. sup. unilateral {alfa_txt(ctx)}%", "num")], linhas,
               "E5 (exploratório, pós-resultado): amostra das outras especificações do outcome original",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> <strong>EXPLORATÓRIO, escrito depois de ler '
                       "o E3.</strong> O principal "
                       "continua sendo o do protocolo. As especificações só verificam se a leitura depende da forma "
                       "funcional, das covariáveis ou da unidade.</p>", rodape=fonte([E5_ESPEC], None, False))


def secao_e3(ctx) -> str:
    est = ctx["est"]
    mn = min(est["p_valor"])
    e5 = ctx["e5"]
    y = e5[(e5["outcome"] == "Y1") & (e5["especificacao"] != "S0")]
    return (
        '<section><h2>4. Resultado com o outcome original (E3 e E5)</h2>'
        "<p>O outcome da hipótese da banca 1 é o preenchimento: a fração de células CNES–curso do município com "
        "confirmação ou homologação na 1ª chamada do ciclo 1. A presença de especialista ativo (retrato de outubro) é "
        "o segundo outcome do E3, e o ciclo 2 é a replicação. A estimação seguiu o protocolo congelado (local linear "
        f"triangular, h = {br(ctx['h_principal'], 3)}).</p>"
        + fig_rd(ctx) + tabela_e3(ctx)
        + f"<p><strong>Leitura.</strong> Nenhum salto é distinguível de zero; o menor p entre as linhas do E3 é {br(mn, 3)}. "
          "Os ICs são largos: o outcome é ruidoso, há poucas dezenas de municípios por lado e a reta local linear multiplica "
          "o erro-padrão em relação à diferença de médias. A leitura é \"sem evidência de efeito, com baixa precisão\", e não "
          "\"a bolsa não funciona\".</p>"
        + "<p><strong>Sobre o sinal.</strong> " + texto_decomposicao(ctx) + "</p>"
        + tabela_precisao(ctx) + tabela_e5(ctx)
        + f"<p>Nas {br_int(len(y))} linhas alternativas do preenchimento (outras especificações e cortes, todas em "
          f"<code>E5_especificacoes.csv</code>; a tabela mostra uma amostra) nenhuma é distinguível de zero (menor p: "
          f"{br(y['p_valor'].min(), 3)}). O E5 não troca o principal; só mostra que a leitura não depende da forma de "
          "estimar.</p></section>")


def tabela_p1(ctx) -> str:
    e6 = ctx["e6"]
    d = e6[(e6["outcome_id"] == "P1") & (e6["especificacao"] == "principal")]
    ordem = [("V1+V2+V3", "empilhado"), ("V1+V2+V3", "0.300"), ("V1+V2+V3", "0.400"), ("V1", "empilhado"),
             ("V2", "empilhado"), ("V3", "empilhado")]
    linhas = []
    for pop, c in ordem:
        r = linha_est(d, populacao=pop, corte=c)
        linhas.append([pop, c if c == "empilhado" else br(float(c), 3), n_lados(r["n_abaixo"], r["n_acima"]),
                       sinal(r["tau"], 2), f"[{sinal(r['ic95_inf'], 2)}; {sinal(r['ic95_sup'], 2)}]",
                       f"[{sinal(r['ic_honesto_inf'], 0)}; {sinal(r['ic_honesto_sup'], 0)}]", br_p(r["p_valor"])])
    return tab([("População", "txt"), ("Corte", "num"), ("n abaixo / acima", "num"), ("Salto (DP)", "num"),
                ("IC 95% (CR1)", "num"), ("IC honesto (DP)", "num"), ("p", "num")], linhas,
               "E6, primária P1: índice de atração-presença (pré-especificado)",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> Índice de Kling, Liebman e Katz de F1.1 '
                       "(candidatos de 1ª opção por célula), F1.2 (fração de células com candidato), F1.3 (fração "
                       "preenchida na 1ª chamada) e F2.1 (especialistas ativos por célula), em desvios-padrão do lado de "
                       "baixo. Salto = lado com bolsa maior − lado com bolsa menor. Contraste: <strong>RDD em nível = pacote "
                       "do corte</strong>. Empilhado = salto comum aos cortes e ciclos (efeito fixo de ciclo, cluster por "
                       "município).</p>", rodape=fonte([E6_EST], None, False))


def secao_multi(ctx) -> str:
    e8 = ctx["e8"]
    e7s = e8["e7"]
    seq = e7s["f31_U_0300"]["maior_sequencia_p_menor_005"]
    pre = e7s["f31_U_0300"]
    v1 = e7s["v1_0300"]
    fam = e8["familias"]
    g0, g1, g2, passo = grade_texto(ctx)
    c2 = e8["e9"]["ciclo2"]
    pe = e8["e9"]["principal"]
    emp = e8["e9"]["empilhado"]
    ro = ctx["e9rob"]
    cc = ro[(ro["analise"] == "cv3_cluster_conjunto") & (ro["ciclo"] == "2")].iloc[0]
    cub2 = c2["spline_cubico"]
    linhas_e9 = []
    for ciclo in ("1", "2", "3", "empilhado"):
        d = pe[ciclo]
        linhas_e9.append([ciclo, br(d["rc_5mil"], 2), f"[{br(d['rc_5mil_ic95'][0], 2)}; {br(d['rc_5mil_ic95'][1], 2)}]",
                          f"{sinal(d['dprob_pp'], 2)} {ic_pp(d['dprob_pp_ic95'][0] / 100, d['dprob_pp_ic95'][1] / 100, 2)}",
                          br(d["prob_base_pp"], 2), br_p(d["p"])])
    def mk_e9() -> str:
        return tab([("Ciclo", "txt"), ("Razão de chances por +" + passo, "num"), ("IC 95%", "num"),
                ("Δ prob. média (p.p.)", "num"), ("Prob. base (p.p.)", "num"), ("p", "num")], linhas_e9,
               "E9: escolha da 1ª opção (logit condicional; secundário e exploratório)",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> Razão de chances de a célula ser a 1ª opção do '
                       f"candidato por +{passo} na bolsa dela, com o IVS em spline contínuo e os degraus da bolsa em "
                       f"{br(ctx['cortes'][0])} e {br(ctx['cortes'][1])}. Cluster por conjunto de células. Mede "
                       "<strong>realocação entre células do mesmo curso</strong>, condicional a candidatar-se; o que uma "
                       "célula ganha as outras do curso perdem. Não é efeito sobre o total de candidatos.</p>",
               rodape=fonte([E8_RES], None, False))
    return (
        '<section><h2>5. Rodada multi-outcome (E6, E7 e E9)</h2>'
        f"<p>Em {data_br(ctx['prot40']['autorizacao_autor']['data'])} o autor autorizou a rodada multi-outcome, sob o "
        "protocolo 40, congelado antes de abrir os "
        "outcomes novos: funil do candidato nos ciclos 1 a 3 (E6), oferta no CNES por DiRD (E7) e escolha dos candidatos "
        "(E9). O protocolo fixou duas hipóteses primárias, com Holm: P1 (E6) e P2 (E7). O resto é secundário, com q de "
        "BKY por família. Parte do ciclo 1 já tinha sido vista antes do congelamento (seção 8).</p>"
        "<h3>5.1 E6: o funil do candidato (RDD em nível)</h3>"
        + tabela_p1(ctx)
        + fig_png("Índice P1 com ciclos e cortes agrupados (visual)", [FIG_E6_P1], classe="w50",
                  sub="Médias em faixas do IVS, reta local linear com h = " + br(ctx["h_principal"], 3) +
                      " e IC 95% pontual; reta comum em r = IVS − corte, só para visualização.")
        + fig_png("Fração de células preenchidas na 1ª chamada no ciclo 2 (F1.3; replicação do E3)",
                  [FIGS_E6_F13[0]], classe="w80", sub="O ciclo 1 é o da " + R.NUM.ref("rd_e3", "figura da seção 4")
                  + ". Médias em faixas do IVS, reta local linear (h = " + br(ctx["h_principal"], 3)
                  + ") e IC 95% pontual; salto = lado de bolsa maior − lado de bolsa menor.")
        + fig_png("Fração de células preenchidas na 1ª chamada no ciclo 3 (F1.3)", [FIGS_E6_F13[1]], classe="w80",
                  sub="Mesma construção. O ciclo 3 entra só com outcomes do funil (quadro de vagas e chamadas).")
        + f"<p>Nenhum dos quatro componentes do índice rejeita zero na linha empilhada (tabela da seção 6); "
          f"{br_int(fam['F1']['resumo_testes']['salto_negativo'])} das "
          f"{br_int(fam['F1']['resumo_testes']['linhas_principais_no_bky'])} linhas principais de F1 e "
          f"{br_int(fam['F2']['resumo_testes']['salto_negativo'])} das "
          f"{br_int(fam['F2']['resumo_testes']['linhas_principais_no_bky'])} de F2 têm salto "
          "negativo. O índice empilhado tem salto negativo com IC que contém zero. O IC honesto não informa (cobre dezenas "
          "de desvios-padrão).</p>"
        + "<h3>5.2 E7: oferta no CNES por DiRD</h3>"
        + fig_png("E7, F3.1 em nível: o pacote do corte, nas janelas pré extra, pré e pós", [FIG_E7_NIVEL], classe="w64",
                  sub="Vínculos nas CBO-alvo por 10 mil hab. (Censo 2022), municípios de U, h = " +
                      br(ctx["h_principal"], 3) + "; seis painéis (pré extra, pré e pós por corte).")
        + fig_png("E7, F3.1 por DiRD: delta de vínculos (média do pós − média do pré)", [FIG_E7_DIRD],
                  sub="Contraste: bolsa mais a variação das descontinuidades das outras políticas.")
        + fig_png("E7, F3.1: estudo de evento da DiRD", [FIG_E7_EVENTO], classe="w88",
                  sub=f"Salto de cada mês relativo à referência (competência {esc(ref_evento(ctx))}). As linhas vermelhas "
                      "tracejadas marcam atos que mudam no tempo (auditoria 18).")
        + tabela_e7_placebos(ctx)
        + f"<p><strong>Leitura.</strong> A DiRD não detecta mudança na oferta cadastrada de especialistas nas CBO-alvo, nem "
          f"nos placebos. Em {br(ctx['cortes'][0])} há uma sequência de {br_int(seq['n_meses'])} meses seguidos com p &lt; 0,05, de "
          f"{esc(seq['inicio'])} a {esc(seq['fim'])}, logo no início do pós, que depois se desfaz "
          f"({br_int(pre['meses_pos_depois_da_sequencia_p_menor_005'])} dos {br_int(pre['meses_pos_depois_da_sequencia'])} "
          "meses seguintes têm p &lt; 0,05). Ela não vira efeito: há descontinuidade pré-existente no nível em "
          f"{br(ctx['cortes'][0])} (última linha da tabela), a referência do estudo de evento está num vale, e as outras políticas "
          "variam no tempo (a DiRD só remove a parte constante). Em V1 no corte "
          f"{br(ctx['cortes'][0])}, {br_int(v1['meses_pre_extra_e_entre_p_menor_005'])} de {br_int(v1['meses_pre_extra_e_entre'])} meses "
          "do pré extra e do trecho até o pré principal têm p &lt; 0,05: há pré-tendência, e a DiRD nesse recorte não é "
          "crível.</p>"
        + "<h3>5.3 E9: escolha revelada dos candidatos (exploratório)</h3>"
        + mk_e9()
        + fig_png("E9: utilidade estimada da célula contra o IVS", [FIG_E9], classe="w80",
                  sub="Logit condicional da 1ª opção, conjunto principal; demais atributos fixos. A diferença entre as "
                      "curvas azul (principal), laranja (spline quadrático) e verde (degrau por corte) é a sensibilidade "
                      "à forma funcional.")
        + f"<p><strong>Leitura.</strong> No ciclo 2 a bolsa desloca a 1ª opção para células de bolsa maior, e o sinal "
          f"sobrevive à inferência com poucos clusters (p do CV3 {br_p(cc['p'])}; score bootstrap, {br_p(c2['p_score_rademacher'])} "
          f"e {br_p(c2['p_score_webb'])}) e a cortes placebo (p por posto {br(c2['placebo']['p_posto'], 3)}). A ressalva é o "
          f"spline cúbico na amostra toda, cujo IC inclui zero ([{sinal(cub2['ic95_inf'], 3)}; {sinal(cub2['ic95_sup'], 3)}] "
          "no coeficiente por R$ mil). Nos ciclos 1 e 3 o IC inclui zero. O empilhado é frágil: a significância vem do "
          f"ciclo 2 (os ciclos 1 e 3 juntos têm p = {br(emp['ciclos_1_e_3']['p'], 3)}); o Q de Cochran rejeita coeficiente "
          f"comum (p = {br(emp['cochran_Q']['p'], 3)}); {br(100 * emp['placebo']['fracao_abs_t_maior_1_96'], 1)}% dos "
          f"placebos passam de |t| = 1,96, e o p por posto do empilhado é {br(emp['placebo']['p_posto'], 3)}.</p>"
        + "</section>")


def tabela_holm(ctx) -> str:
    h = ctx["e8"]["holm"]
    linhas = []
    for k, nome in (("P1", "P1: índice de atração-presença (E6, ciclos e cortes empilhados)"),
                    ("P2", "P2: vínculos nas CBO-alvo por 10 mil hab., DiRD (E7, cortes empilhados)")):
        d = h[k]
        linhas.append([nome, esc(d["contraste"]), fmt_est(d["unidade"], d["tau"]),
                       fmt_ic(d["unidade"], d["ic95_inf"], d["ic95_sup"]), br(d["p_valor"], 3), br(d["p_holm"], 3),
                       "sim" if d["rejeita_holm_5pct"] else "não"])
    return tab([("Primária", "txt"), ("Contraste", "txt"), ("Salto", "num"), ("IC 95%", "num"), ("p", "num"),
                ("p Holm", "num"), (f"Rejeita a {alfa_txt(ctx)}%?", "txt")], linhas,
               "Testes primários com Holm (pré-especificados)",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> Holm sobre as duas primárias, ao nível de '
                       f"{alfa_txt(ctx)}%. P1 em desvios-padrão; P2 em vínculos por 10 mil hab.</p>", rodape=fonte([E8_RES], None, False), inteiro=True)


def tabela_sintese(ctx) -> str:
    t = ctx["e8t"]
    contr = {"pacote no corte (RDD em nível)": "N", "DiRD: bolsa + variação das co-políticas": "D",
             "degrau da bolsa na escolha entre células": "E"}
    linhas = []
    for r in t.itertuples():
        q = "—" if pd.isna(r.q_bky) else br(r.q_bky, 3)
        h = "—" if pd.isna(r.p_holm) else br(r.p_holm, 3)
        ciclo = "" if pd.isna(r.ciclo) else str(r.ciclo)
        if ciclo.startswith("pós"):
            ciclo = "pós"
        pop = esc(r.populacao)
        un = ROTULO_UNIDADE[tipo_unidade(r.unidade)]
        est = fmt_est(r.unidade, r.estimativa) + (f" {un}" if un in ("p.p.", "DP") else "")
        linhas.append([esc(r.outcome), f"{pop} · {esc(ciclo)}" if ciclo else pop, contr.get(r.contraste, "?"), est,
                       fmt_ic(r.unidade, r.ic95_inf, r.ic95_sup), br_p(r.p_valor), q, h])
    pos = ctx["prot40"]["familias"]["F3"]["janelas"]["pos"]
    return tab([("Outcome", "txt"), ("Pop. · ciclo", "txt"), ("Contr.", "txt"), ("Estimativa", "num"),
                ("IC 95%", "num"), ("p", "num"), ("q BKY", "num"), ("p Holm", "num")], linhas,
               "Síntese por elo da cadeia (E8): linhas principais, cortes empilhados",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> Contraste: <strong>N</strong> = RDD em nível '
                       "(pacote do corte); <strong>D</strong> = DiRD (bolsa mais variação das co-políticas); "
                       f"<strong>E</strong> = degrau da bolsa na escolha (E9; razão de chances por +{grade_texto(ctx)[3]}, "
                       "exploratório). "
                       "Salto = lado com bolsa maior − lado com bolsa menor, na unidade do outcome (p.p., DP, contagem por "
                       "célula ou por 10 mil hab., horas semanais ou pontos da pontuação). Ordem da cadeia: implementação e "
                       f"seleção, atração, escolha, presença, oferta no CNES, seleção de quem chega. \"pós\" = competências "
                       f"{esc(pos)} (AAAAMM). O q BKY é o da família do protocolo (E9 não tem).</p>",
               rodape=fonte([E8_TAB], None, False), inteiro=False, classe="compacta sintese")


def tabela_descartes(ctx) -> str:
    x = ctx["x6"]
    linhas = []
    ref = ctx["e8"]["descarte"]["referencias"]["preenchimento_pp"]
    for oid, pops in (("F1.3", ("V1", "V2", "V3", "V1+V2+V3")), ("F1.4", ("V1", "V2", "V1+V2"))):
        for pop in pops:
            r = x[(x["outcome_id"] == oid) & (x["populacao"] == pop) & (x["corte"] == "empilhado")
                  & (x["especificacao"] == "principal") & (x["etapa_origem"] == "E6")]
            if len(r) != 1:
                raise SystemExit(f"X6 sem linha única para {oid}/{pop}")
            r = r.iloc[0]
            linhas.append([oid, pop, pp(r["tau"]), ic_pp(r["ic95_inf"], r["ic95_sup"]), br(100 * r["mde80"], 1),
                           "sim" if bool(r["ic95_exclui_ref_protocolo"]) else "não",
                           "sim" if bool(r["ic_honesto_exclui_ref_protocolo"]) else "não"])
    return tab([("Outcome", "txt"), ("População", "txt"), ("Salto (p.p.)", "num"), ("IC 95% convencional", "num"),
                (f"Efeito mín. detectável {poder_txt(ctx)}% (p.p.)", "num"), (f"IC exclui +{br(100 * ref, 0)} p.p.?", "num"),
                ("IC honesto exclui?", "num")], linhas, "Poder e descartes do preenchimento (X6, cortes empilhados)",
               legenda='<p class="legenda-salto"><strong>Como ler.</strong> \"Descartar\" = o limite superior do IC 95% fica '
                       "abaixo da referência do protocolo (+" + br(100 * ref, 0) + " p.p. de preenchimento). Vale só com o IC "
                       "convencional, sob linearidade local e para o pacote do corte. Linhas de ciclo isolado mostram que o "
                       "ganho de precisão veio de empilhar.</p>", rodape=fonte([X6_EST], None, False))


def secao_sintese(ctx) -> str:
    e8 = ctx["e8"]
    fam = e8["familias"]
    conj = {k: fam[k]["resumo_testes"] for k in fam}
    q_menor = min(v["menor_q"] for v in conj.values())
    n_q = sum(v["q_menor_005"] for v in conj.values())
    n_p = sum(v["p_menor_005"] for v in conj.values())
    n_lin = sum(v["linhas_principais_no_bky"] for v in conj.values())
    cont = ctx["x6r"]["contagens"]
    nomes = {"f0_2_vagas_imediatas_por_10k_c1": "vagas imediatas do ciclo 1 por 10 mil hab.",
             "f2_2_ativos_pmme_por_10k_c2": "especialistas ativos do ciclo 2 por 10 mil hab.",
             "f4_2_pontuacao_media_cand_1a_opcao": "nota média dos candidatos de 1ª opção"}
    isolados = sorted({o for v in conj.values() for o in v["outcomes_com_p_menor_005"]})
    isol_txt = ", ".join(nomes.get(o, o) for o in isolados)
    return (
        '<section><h2>6. Síntese com Holm, poder e descartes</h2>'
        + tabela_holm(ctx) + tabela_sintese(ctx)
        + f"<p><strong>Leitura.</strong> Nenhuma primária rejeita zero depois do Holm. Em {br_int(n_lin)} linhas principais "
          f"das famílias F0 a F4, {br_int(n_p)} têm p &lt; 0,05 e {br_int(n_q)} têm q BKY &lt; 0,05 (menor q: {br(q_menor, 3)}). "
          f"Os p &lt; 0,05 isolados ({esc(isol_txt)}) têm q alto e são da ordem do esperado por acaso numa família com "
          "dezenas de testes. O BKY supõe dependência positiva entre linhas, o que não foi verificado.</p>"
        + tabela_descartes(ctx)
        + fig_png("X6: o que cada IC descarta (exploratório, sem estimação nova)", [FIG_X6],
                  sub="(a) RDD em nível e DiRD, cortes empilhados, em escala relativa à média de base; (b) E9, elasticidade "
                      "implícita da escolha. Referências do protocolo e da literatura (doc 20) marcadas.")
        + f"<p>Das {br_int(cont['com_referencia_do_protocolo'])} linhas com referência do protocolo, "
          f"{br_int(cont['ic95_exclui_ref_protocolo'])} têm IC 95% que exclui a referência e "
          f"{br_int(cont['mde80_abaixo_ref_protocolo'])} têm efeito mínimo detectável abaixo dela; com o IC honesto, "
          f"{br_int(cont['ic_honesto_exclui_ref_protocolo'])} a excluem. O poder é baixo em quase todas as linhas: um nulo "
          "aqui não é uma estimativa precisa de zero.</p></section>")


def secao_exploratoria(ctx) -> str:
    x1 = ctx["x1"]["mesmo_municipio_por_mes_de_referencia"]["literal_doc45"]
    tl = ctx["x1"]["taxas_ligacao"]["literal_doc45"]
    linhas1 = []
    for c in ("1", "2"):
        d = x1[c]
        linhas1.append([c, br_int(tl[c]["registros"]), pct_(tl[c]["taxa"]), br_int(d["n_ligados"]),
                        f"{pct_(d['minimo'])} a {pct_(d['maximo'])}", pct_(d["persistencia"]["fracao"])])
    t1 = tab([("Ciclo", "txt"), ("Registros PMM-E", "num"), ("Ligados ao CNES", "num"), ("n ligados", "num"),
              ("Já com vínculo médico no mesmo município antes do início (faixa entre meses de referência)", "num"),
              ("Dos que tinham, já estavam em 202406", "num")], linhas1,
             "X1 (descritivo, exploratório): origem dos especialistas do PMM-E no CNES", inteiro=True,
             rodape=fonte([X1_RES], None, False))
    d2 = ctx["x2d"]
    linhas2 = []
    for c in ("1", "2"):
        r = d2[(d2["ciclo"].astype(str) == c) & (d2["faixa"] == "TOTAL") & (d2["subgrupo"] == "todos")
               & d2["regra_ligacao"].str.startswith("ampla")]
        if len(r) != 1:
            raise SystemExit(f"X2_descritivo sem linha única do ciclo {c}")
        r = r.iloc[0]
        linhas2.append([c, br_int(r["n_alocados"]), pct_(r["taxa_ligacao"]), pct_(r["permanencia_set"])])
    t2 = tab([("Ciclo", "txt"), ("Alocados na 1ª chamada", "num"), ("Ligados a ativo no município", "num"),
              ("Permanência entre os determinados", "num")], linhas2,
             "X2 (descritivo, exploratório): permanência dos alocados no município no retrato de 11/09/2026",
             inteiro=True, rodape=fonte([X2_DESC], None, False), classe="compacta estreita")
    x2 = ctx["x2e"]
    x2 = x2[x2["regra_ligacao"].str.startswith("ampla")]  # regra de ligação principal (a estreita é sensibilidade)
    x2p = x2[x2["p_valor"].notna()]
    lee = x2[x2["lee_ic95_inf"].notna()]
    lee_zero = int(((lee["lee_ic95_inf"] <= 0) & (lee["lee_ic95_sup"] >= 0)).sum())
    x3 = ctx["x3e"]
    x3p = x3[x3["p_valor"].notna()]
    return (
        '<section><h2>7. Principais achados exploratórios (X1 a X3)</h2>'
        '<p class="alerta-exp"><strong>EXPLORATÓRIO e pós-resultado.</strong> Rodada pedida pelo autor depois da síntese '
        "(protocolo 45, congelado antes de abrir os outcomes novos). Nada aqui é teste confirmatório nem muda o Holm das "
        "primárias. Servem para orientar a revisão da hipótese.</p>"
        + t1
        + "<p><strong>X1 (origem).</strong> Uma parte grande dos especialistas do PMM-E já tinha vínculo médico no município "
          "do posto antes de começar (coluna da faixa de meses de referência), e a maioria desses já estava lá em 202406, "
          "bem antes do programa. Para esses médicos o PMM-E registra no CNES quem já estava ali, e não um médico novo. É "
          "compatível com a leitura de substituição e realocação, mas não a prova: vínculo prévio não diz se a carga "
          "horária ou a especialidade mudaram. Vínculo no CNES também não é presença nem trabalho efetivo.</p>"
        + t2
        + f"<p><strong>X2 (permanência) e RDD condicional.</strong> Nos cortes, com a regra de ligação principal, a RDD da "
          f"permanência tem {br_int(len(x2p))} estimativas com p; {br_int(int((x2p['p_valor'] < 0.05).sum()))} têm "
          f"p &lt; 0,05, o menor q BKY é {br(x2p['q_bky'].min(), 3)} e {br_int(lee_zero)} de {br_int(len(lee))} ICs dos "
          "limites de Lee contêm zero. É permanência no município no retrato, não retenção individual.</p>"
        + f"<p><strong>X3 (dinâmica mensal dos ativos).</strong> A listagem mensal é incompleta (ausência não é zero). "
          f"Das {br_int(len(x3p))} estimativas com p (incluindo sensibilidades), {br_int(int((x3p['p_valor'] < 0.05).sum()))} "
          f"têm p &lt; 0,05, todas com q BKY de {br(x3p['q_bky'].min(), 3)}, e o sinal depende de como se tratam os meses de "
          "listagem incompleta. Não há leitura causal.</p></section>")


def pct_(x) -> str:
    return br(100 * float(x), 1) + "%"


def secao_limites(ctx) -> str:
    e8 = ctx["e8"]
    sel = e8["selecao_v1_0400"]
    peso = sel["peso_c1_400_no_P1"]
    expo = ctx["prot40"]["exposicao_previa_a_outcomes"]
    g0, g1, g2, passo = grade_texto(ctx)
    lim = [
        "<strong>Pacote, não bolsa.</strong> Nenhum resultado em nível isola a bolsa, e a DiRD só remove a parte constante "
        "das co-políticas (seção 3.4).",
        "<strong>Potência.</strong> Por corte e ciclo, poucas dezenas de municípios com vaga de cada lado; só o "
        "empilhamento estreitou o IC. O IC honesto não descarta nada.",
        f"<strong>Seleção em V<sub>k</sub>.</strong> Os outcomes por célula só existem onde houve vaga. O ciclo 1 em "
        f"{br(ctx['cortes'][1])} é suspeito (seção 3.2); seu peso no P1 empilhado é {br(100 * peso, 1)}%.",
        "<strong>Presença é retrato.</strong> Vínculo no CNES não é médico do PMM-E nem retenção individual.",
        f"<strong>Exposição prévia.</strong> O protocolo foi congelado depois de exposições parciais, listadas no próprio "
        f"protocolo ({br_int(len(expo))} itens, como o E3 do ciclo 1 e uma contagem agregada de inventário).",
        "<strong>Ciclo 3.</strong> Entra só com outcomes do funil; nenhuma competência do CNES a partir de 202609 é lida "
        "(plano de pré-análise do ciclo 3 intacto), e o ciclo 3 prospectivo de força de trabalho segue congelado até a "
        "maturidade.",
        "<strong>Muitos testes.</strong> O BKY supõe dependência positiva entre linhas; isso não foi verificado.",
    ]
    perg = [
        f"<strong>Estimando.</strong> Faz sentido reportar o contraste como \"incentivo marginal de {passo} dentro de um pacote\"? "
        "Alguma delas (nível, DiRD, escolha) é preferível como manchete?",
        f"<strong>Janela.</strong> O protocolo fixou h = {br(ctx['h_principal'], 3)}, com {br(ctx['h_sens'][0], 3)} e "
        f"{br(ctx['h_sens'][1], 3)} como sensibilidade e IC honesto como ressalva. É defensável sem seleção ótima da janela?",
        "<strong>DiRD como resposta às cointervenções.</strong> Ela tira só o que é constante no tempo. Com atos que mudam no "
        f"tempo e uma descontinuidade pré-existente em {br(ctx['cortes'][0])}, há um desenho melhor com os dados "
        "disponíveis?",
        "<strong>Empilhamento de cortes e ciclos.</strong> Um salto comum para cortes com bolsas e co-políticas diferentes "
        "(e municípios que se repetem entre ciclos) é um estimando interpretável? Como pesar cada grupo?",
        f"<strong>Leitura dos nulos com poder baixo.</strong> Vale destacar que o IC convencional empilhado exclui +{ref_pp(ctx)} "
        "p.p. quando o IC honesto não exclui nada? Qual é a manchete honesta?",
        "<strong>Placebos de corte.</strong> Só o E9 tem. Para a RDD em nível, vale rodar cortes falsos antes de qualquer outra "
        "coisa?",
        "<strong>E9.</strong> A razão de chances do ciclo 2 e a fragilidade do empilhado (placebos acima do nominal, spline "
        "cúbico, heterogeneidade entre ciclos) justificam o rótulo de exploratório? O que mais seria exigido?",
        "<strong>Hipótese pendente.</strong> Manter H1 e relatar o nulo, ou adotar uma das propostas da síntese: (A) realocação "
        "entre vagas sem expansão líquida detectável, (B) elasticidade local da escolha à remuneração relativa aos fatores "
        "não pecuniários, (C) \"quanto e em que margem\" em vez de \"funciona?\". Qual é mais defensável?",
    ]
    return (
        '<section><h2>8. Limitações e perguntas para os professores validarem</h2><h3>Limitações</h3>' + lista(lim)
        + "<h3>Perguntas</h3><ol class=\"leitura\">" + "".join(f"<li>{p}</li>" for p in perg) + "</ol>"
        + caixa("O que podemos e não podemos afirmar",
                "<div class=\"duas\"><div><p class=\"caixa-sub\">Podemos</p>" + lista([
                    "Sob o protocolo, nenhuma primária rejeita zero depois do Holm.",
                    f"Com cortes e ciclos empilhados, IC convencional e linearidade local, saltos de preenchimento de "
                    f"+{ref_pp(ctx)} p.p. ou mais ficam fora do intervalo.",
                    "No ciclo 2, a bolsa desloca a 1ª opção dos candidatos para células de bolsa maior.",
                    "A DiRD no CNES não detecta mudança de oferta das CBO-alvo.",
                ]) + "</div><div><p class=\"caixa-sub\">Não podemos</p>" + lista([
                    "Dizer que a bolsa não funciona ou que o efeito é zero.",
                    "Estender o descarte ao IC honesto, a um ciclo isolado ou à bolsa sem as co-políticas.",
                    "Dizer que o deslocamento na escolha aumenta candidatos, preenchimento ou oferta local.",
                    "Atribuir o resultado à participação no PMM-E, ao Agora Tem Especialistas ou ao IVS.",
                ]) + "</div></div>")
        + "</section>")


def secao_proveniencia(ctx) -> str:
    def item(p: Path) -> str:
        return f"<li><code>{esc(rel(p).replace('output/', ''))}</code> <span class=\"hash\">{sha256(p)[:12]}</span></li>"

    return (
        "<section><h2>Apêndice. Proveniência</h2>"
        "<p class=\"nota\">Cada número do relatório vem de um destes arquivos de <code>output/</code>, lido pelo "
        f"<code>{esc(rel(ESTE_SCRIPT))}</code> na geração (nome relativo a <code>output/</code> e início do SHA-256). "
        "As figuras PNG são as gravadas pelos scripts do pipeline, incorporadas sem alteração. Nada é lido de "
        "<code>data/</code>.</p>"
        '<p class="apend-tit">Entradas lidas</p><ul class="hashes">' + "".join(item(p) for p in ENTRADAS_HASH) + "</ul>"
        '<p class="apend-tit">Figuras do pipeline incorporadas</p><ul class="hashes">'
        + "".join(item(p) for p in FIGURAS_PIPELINE) + "</ul></section>")


# ---------------------------------------------------------------------------
# Montagem
# ---------------------------------------------------------------------------

CSS_EXTRA = """
@page { margin: 13mm 14mm 15mm 14mm; }
main { max-width: 182mm; }
body { font-size: 9.2pt; line-height: 1.4; }
h1 { font-size: 19pt; margin: 3mm 0 3mm; }
h2 { font-size: 13pt; break-after: avoid; }
h3 { break-after: avoid; }
.cab { margin-bottom: 4mm; }
.lead { font-size: 10pt; margin-bottom: 4pt; }
.caixa { border-left: 3px solid var(--s1); background: var(--wash); padding: 6pt 10pt 3pt; margin: 6pt 0 8pt; font-size: 8.8pt;
  break-inside: avoid; }
.caixa.aviso { border-left-color: var(--warn); background: var(--warn-bg); }
.caixa-tit { font-weight: 650; margin: 0 0 3pt; }
.caixa-sub { font-weight: 650; margin: 0 0 2pt; }
.duas { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; }
.formula { text-align: center; font-size: 10pt; margin: 6pt 0; }
.alerta-exp { border-left: 3px solid var(--warn); background: var(--warn-bg); padding: 5pt 9pt; font-size: 8.8pt; }
section { margin-bottom: 10pt; }
figure { margin: 6pt 0 8pt; }
figure img.w50 { width: 50%; }
figure img.w64 { width: 64%; }
figure img.w80 { width: 80%; }
figure img.w88 { width: 88%; }
figure img { margin-bottom: 2pt; }
table.compacta { font-size: 7.6pt; }
table.compacta td, table.compacta th { padding: 1.8pt 3.5pt; }
table.sintese { font-size: 7.2pt; }
table.sintese td:first-child { width: 58mm; }
table.sintese td:nth-child(2) { white-space: nowrap; }
.apend-tit { font-weight: 650; margin: 6pt 0 2pt; font-size: 8.4pt; }
ul.hashes { columns: 2; column-gap: 8mm; list-style: none; padding-left: 0; margin: 0 0 4pt; font-size: 6.6pt; }
ul.hashes li { margin-bottom: 1pt; break-inside: avoid; }
ul.hashes code { font-size: 6.4pt; overflow-wrap: anywhere; }
.hash { color: var(--muted); font-family: "DejaVu Sans Mono", monospace; }
ul.resumo-lista li { font-size: 8.8pt; margin-bottom: 3.5pt; }
"""


def montar_html(ctx) -> str:
    R.NUM.fig = 0
    R.NUM.tab = 0
    R.NUM.refs.clear()
    ctx["x2d"] = ler_csv(X2_DESC)
    ctx["x2e"] = ler_csv(X2_EST)
    ctx["x3e"] = ler_csv(X3_EST)
    dados_graficos(ctx)
    corpo = [secao_cabecalho(ctx), secao_resumo(ctx), secao_estimando(ctx), secao_dados(ctx), secao_validade(ctx),
             secao_e3(ctx), secao_multi(ctx), secao_sintese(ctx), secao_exploratoria(ctx), secao_limites(ctx),
             secao_proveniencia(ctx)]
    data = data_br(ctx["e8"]["data_execucao"])
    rodape = f"{TITULO} · estado em {data}".replace('"', "'")
    css = (R.CSS.replace("__RODAPE__", rodape).replace("__FONTE__", R.FONTE_SANS) + CSS_EXTRA)
    return (
        '<!DOCTYPE html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{esc(TITULO)}</title><style>{css}</style></head>"
        f"<body><main>{''.join(corpo)}</main></body></html>\n")


def gerar_html() -> str:
    return montar_html(carregar())


def main() -> int:
    SAIDA_DIR.mkdir(parents=True, exist_ok=True)
    doc = gerar_html()
    OUT_HTML.write_text(doc, encoding="utf-8")
    print(f"HTML: {rel(OUT_HTML)} ({OUT_HTML.stat().st_size / 1024:.0f} KiB)")
    if not R.gerar_pdf(OUT_HTML, OUT_PDF):
        return 1
    n = R.contar_paginas(OUT_PDF)
    print(f"PDF:  {rel(OUT_PDF)} ({OUT_PDF.stat().st_size / 1024:.0f} KiB, {n if n else '?'} páginas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
