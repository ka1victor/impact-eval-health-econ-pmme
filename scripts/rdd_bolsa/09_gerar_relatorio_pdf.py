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
3. E5, a inferencia alternativa, e EXPLORATORIA e pos-resultado: a secao so le
   `output/rdd_bolsa/E5_*` (gravados por `11_inferencia_alternativa.py`) e nao
   recalcula nada; nenhuma especificacao do E5 substitui o principal.
4. E1, E2 e E4, feitos quando o escore era parcial, sao exploratorios e ficam
   como historico, superados pelo E3.

Calculos feitos aqui (so para exibicao)
---------------------------------------
- reproducao da faixa anunciada pelo IVS oficial e pelo arquivo local, por
  quadro, conferida contra `portao_r1_ivs_oficial.json`, e o cruzamento
  variavel x grade (grade aplicada 0,300/0,400 contra a grade do FAQ do
  edital, com os cortes registrados em `a01b_reconstrucao_regra_faixa.json`);
- figura da regra (variante A da galeria, escolhida pelo autor em 18/10/2026):
  cada municipio no valor exato da bolsa, colorido pelo IVS do eixo (verde ->
  amarelo -> vermelho); na versao do arquivo antigo, contorno preto nos
  municipios do lado errado do corte;
- graficos RD tradicionais (P1: preenchimento e presenca; P2: presenca):
  medias do outcome em bins de 0,010 (tamanho do ponto proporcional ao numero
  de municipios), retas locais lineares da especificacao principal e IC 95%
  pontual da reta (HC1). D_k e lido da relacao nominal (so `co_ibge` e
  `ciclo`) com as funcoes do script do E3; a fracao preenchida vem de
  `E4_proporcao_municipio.csv`. O salto e o EP de cada reta sao conferidos
  contra `E3_estimativas.csv`, e os valores das retas no corte contra
  `E3_conferencia_sinal.json`; se divergirem, o script para sem gerar o
  relatorio;
- visao global (descritiva): medias em bins de 0,020 em todo o suporte do IVS e
  polinomio de grau 2 em cada faixa de bolsa (MQO nos municipios);
- histograma do IVS em bins de 0,005 em torno de cada corte, com a contagem
  esperada pelo ajuste Poisson log-linear do E3 (razao conferida contra
  `E3_diagnosticos.csv`);
- balanco de covariaveis em desvios-padrao: salto e IC de `E3_diagnosticos.csv`
  divididos pelo desvio-padrao da covariavel na populacao (covariaveis lidas
  com a funcao do E3);
- efeito minimo detectavel aproximado = 2,8 x EP da especificacao principal.

A conferencia do sinal do salto (bolsa maior menos bolsa menor) e feita por
`09b_conferir_sinal.py`, que deve rodar antes deste script; o relatorio le
`E3_conferencia_sinal.json` e para se ele faltar, estiver desatualizado em
relacao a `E3_estimativas.csv` ou registrar divergencia.

Entradas: lista ENTRADAS (todas com SHA-256 no apendice do relatorio).

Saidas
------
- output/rdd_bolsa/relatorio_resultados_rdd_bolsa.html  (autocontido)
- output/rdd_bolsa/relatorio_resultados_rdd_bolsa.pdf  (A4 retrato, via Chromium headless)

Parte II (rodada multi-outcome, protocolo 40)
---------------------------------------------
Seções 6 a 12 e o resumo da rodada: protocolo 40 (lido de `protocolo_E6_multioutcome.json`), políticas nos
mesmos cortes (tabelas da auditoria 18 copiadas na geração e datas do resumo do E7), E6, E9 e E7 (lidos de
`output/rdd_bolsa/E6_*`, `E9_*` e `E7_*`), A4 corrigido (`output/tema_trabalho/failure_mode_ivs_*`, coluna
"antes" rotulada FAILURE_MODE) e a síntese E8 (`E8_resumo.json`; sem ele, a seção diz "pendente"). Nada é
estimado aqui: tabelas e frases saem das saídas na geração (as frases de leitura do E7 vêm da própria função
`gerar_leitura` do script do E7), e as figuras são os PNG gravados pelos scripts do E6, E7 e E9, incorporados
sem alteração. Antes de cada tabela há uma caixa "Como ler" (salto = lado com bolsa maior menos lado com bolsa
menor; RDD em nível = pacote do corte; DiRD = bolsa + variação das outras descontinuidades).

Linguagem: o E3 da a estimativa local do efeito do anuncio de +R$ 5 mil sob as
premissas da RDD; nao identifica participacao no PMM-E. E1, E2 e E4 sao
exploratorios. O relatorio nao diz que "a bolsa nao funciona": diz que nao
detectamos efeito e que os intervalos nao excluem efeitos grandes.
"""

from __future__ import annotations

import base64
import datetime as dt
import glob
import hashlib
import html
import importlib.util
import itertools
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
CONF_SINAL = OUT_DIR / "E3_conferencia_sinal.json"  # gerado por 09b_conferir_sinal.py
TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"  # estrato (balanco)
# E5: inferencia alternativa, EXPLORATORIA e pos-resultado (11_inferencia_alternativa.py). A secao 3 do
# relatorio le so estes arquivos; nada do E5 e recalculado aqui.
E5_ESPEC = OUT_DIR / "E5_especificacoes.csv"
E5_DECOMP = OUT_DIR / "E5_decomposicao_ic.csv"
E5_LADOS = OUT_DIR / "E5_decomposicao_lados.csv"
E5_LR_SENS = OUT_DIR / "E5_lr_sensibilidade_janelas.csv"
E5_RESUMO = OUT_DIR / "E5_resumo.json"
E5_ARQS = [E5_ESPEC, E5_DECOMP, E5_LADOS, E5_LR_SENS, E5_RESUMO]
# Historico (escore parcial)
E1_EST = OUT_DIR / "E1_densidade_estimativas.csv"
E1_RES = OUT_DIR / "E1_densidade_resumo.json"
E2_LIM = OUT_DIR / "E2_limites.csv"
E2_RES = OUT_DIR / "E2_limites_resumo.json"
E4_EST = OUT_DIR / "E4_estimativas.csv"
E4_RES = OUT_DIR / "E4_resumo.json"
# Parte II: rodada multi-outcome (protocolo 40). O relatório só lê estas saídas; nada é estimado aqui.
PROT40_JSON = OUT_DIR / "protocolo_E6_multioutcome.json"
PROT40_MD = ROOT / "docs" / "06_execucao" / "40_protocolo_multioutcome_rdd_bolsa.md"
AUD18_MD = ROOT / "docs" / "auditorias" / "18_politicas_nos_mesmos_cortes_ivs.md"
A10_DIAG = AQ_DIR / "a10_diagnostico_cortes_normas.json"
E6_EST = OUT_DIR / "E6_estimativas.csv"
E6_DIAG = OUT_DIR / "E6_diagnosticos.csv"
E6_RES = OUT_DIR / "E6_resumo.json"
E6_FIG = OUT_DIR / "E6_figuras"
E6_SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "13_estimar_E6_funil.py"
E7_EST = OUT_DIR / "E7_estimativas.csv"
E7_EV = OUT_DIR / "E7_estudo_evento.csv"
E7_RES = OUT_DIR / "E7_resumo.json"
E7_FIG = OUT_DIR / "E7_figuras"
E7_SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "14_estimar_E7_dird_cnes.py"
E9_EST = OUT_DIR / "E9_estimativas.csv"
E9_EFE = OUT_DIR / "E9_efeitos_marginais.csv"
E9_ROB = OUT_DIR / "E9_robustez_pos_auditoria.csv"
E9_RES = OUT_DIR / "E9_resumo.json"
E9_FIG = OUT_DIR / "E9_figuras"
E9_SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "16_estimar_E9_escolha.py"
FM_CSV = ROOT / "output" / "tema_trabalho" / "failure_mode_ivs_antes_depois.csv"
FM_RES = ROOT / "output" / "tema_trabalho" / "failure_mode_ivs_resumo.json"
FM_SCRIPT = ROOT / "scripts" / "tema_trabalho" / "12_registrar_failure_mode_ivs.py"
E8_RES = OUT_DIR / "E8_resumo.json"  # gravado pela tarefa E8 (síntese); ausente = seção "pendente"
# Figuras do pipeline incorporadas na parte II (PNG gravados pelos scripts do E6, E7 e E9).
FIGURAS_MO = {
    E6_SCRIPT: [E6_FIG / "E6_indice_P1_agrupado.png", *(E6_FIG / f"E6_indice_P1_V{k}.png" for k in (1, 2, 3)),
                E6_FIG / "E6_F0_1_U_c1.png", *(E6_FIG / f"E6_F1_3_V{k}.png" for k in (1, 2, 3))],
    E7_SCRIPT: [E7_FIG / "E7_dird_F3_1_U.png", E7_FIG / "E7_nivel_F3_1_U.png", E7_FIG / "E7_evento_F3_1_U.png",
                E7_FIG / "E7_evento_F3_P1_U.png", E7_FIG / "E7_evento_F3_1_V1.png"],
    E9_SCRIPT: [E9_FIG / "E9_utilidade_ivs.png"],
}
# Arquivos lidos pelas seções da parte II (o teste de rastreabilidade dos números usa esta lista).
FONTES_RODADA_MO = [PROT40_JSON, PROT40_MD, AUD18_MD, A10_DIAG, E6_EST, E6_DIAG, E6_RES, E7_EST, E7_EV, E7_RES,
                    E9_EST, E9_EFE, E9_ROB, E9_RES, FM_CSV, FM_RES, E8_RES]

ENTRADAS = [
    R1_OFICIAL, R1_ADMIN, MATRIZ, ESCORE, IVS_OFICIAL, MANIF_OFICIAL, ESCORE_ADMIN, CATEGORIA, IVS_LOCAL,
    IDENT_LOCAL, A01B, PROTOCOLO, ADENDO_E4, E3_STATUS, E3_EST, E3_DIAG, E4_PROP, ATIVOS_ZIP, E3_SCRIPT,
    CONF_SINAL, TIPOLOGIA, *E5_ARQS, E1_EST, E1_RES, E2_LIM, E2_RES, E4_EST, E4_RES,
    *FONTES_RODADA_MO, E7_SCRIPT, *(f for figs in FIGURAS_MO.values() for f in figs),
]
OBRIGATORIAS = [R1_OFICIAL, MATRIZ, ESCORE, IVS_OFICIAL, IVS_LOCAL, IDENT_LOCAL, PROTOCOLO, E3_STATUS, E3_EST,
                E3_DIAG, E4_PROP, ATIVOS_ZIP, E3_SCRIPT, CONF_SINAL]

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
BIN_GLOBAL_MIL = 20  # bins de 0,020 na visao global (0,300 e 0,400 sao bordas de bin)
GRAU_GLOBAL = 2  # polinomio descritivo em cada faixa, na visao global
BIN_DENS_MIL = 5  # histograma do IVS em bins de 0,005
SEMENTE_JITTER = 20261014  # deslocamento vertical do grafico da regra
ALFA = 0.05
Z_975 = 1.959963984540054
TOL_RHO = 1e-6  # conferencia da razao de densidades refeita aqui contra o E3
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

# Escala de cor do IVS na figura da regra (pedido do autor, 18/10/2026): verde -> amarelo -> vermelho
# conforme o IVS aumenta. As ancoras sao os centros das classes de vulnerabilidade do Atlas do Ipea
# (muito baixa < 0,200; baixa; media 0,300-0,400; alta; muito alta > 0,500); fora de [0,150; 0,550] a cor
# satura. Interpolacao linear em sRGB, a mesma do gradiente SVG da legenda. A cor repete o eixo
# horizontal (nao carrega informacao nova), por isso a escala verde-vermelho nao prejudica leitores com
# daltonismo: a posicao no eixo continua sendo a leitura.
ESCALA_IVS = [(0.150, "#1a9641"), (0.250, "#86bf3c"), (0.350, "#e3ad00"), (0.450, "#f07c1f"), (0.550, "#d7191c")]
CONTORNO_ERRADO = "#0b0b0b"  # municipios do lado errado do corte (arquivo antigo): contorno preto

# Combinacoes populacao x outcome dos graficos RD, na ordem do relatorio.
COMBOS_RD = [("P1", OUTCOME_FRAC), ("P1", OUTCOME_D), ("P2", OUTCOME_D)]

# E5: rotulo obrigatorio e rotulos curtos de apresentacao das especificacoes (os numeros vem do CSV).
AVISO_E5 = "EXPLORATÓRIO, pós-resultado; o principal continua sendo o do protocolo"
ESPEC_E5 = {
    "S0": "S0 principal (protocolo)",
    "A": "A local constante",
    "B": "B cortes empilhados",
    "C1": "C1 + estrato, região, log pop.",
    "C2": "C2 = C1 + IDHM",
    "D": "D local randomization",
    "E0": "E0 município, peso × n.º de células",
    "E1": "E1 célula, EP por município",
    "E2": "E2 = E1 + efeitos fixos de curso",
    "F1": "F1 ciclos empilhados",
    "F2": "F2 ciclos e cortes empilhados",
}
VIES_A = "viesada: ignora as inclinações"
ORDEM_E5 = ["S0", "A", "B", "C1", "C2", "D", "E0", "E1", "E2", "F1", "F2"]
OUTCOME_E5 = {"Y1": "Y1 preenchimento, ciclo 1", "D1": "D1 presença, ciclo 1", "D2": "D2 presença, ciclo 2",
              "D1+D2": "D1 + D2 presença, ciclos 1 e 2"}
MARGENS_E5 = (10, 15, 20)  # p.p.: margens de E5_especificacoes.csv (p unilateral e TOST)


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
    scripts de `scripts/rdd_bolsa/`, `scripts/aquisicao/` e `scripts/tema_trabalho/`, uma constante de
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
    for pasta in (ROOT / "scripts" / "rdd_bolsa", ROOT / "scripts" / "aquisicao", ROOT / "scripts" / "tema_trabalho"):
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


def largura_texto(s: str, size: float) -> float:
    """Largura aproximada de um texto na fonte sans do relatorio (para posicionar legendas)."""
    return len(s) * size * 0.53


def legenda_svg(itens: list[tuple[str, str, str]], x: float, y: float, size=10.5) -> str:
    """itens = [(tipo, cor, rotulo)], tipo em {'ponto','linha','faixa','anel','barra','area','tracejada','vazio'}."""
    out = []
    cx = x
    for tipo, cor, rot in itens:
        if tipo == "ponto":
            out.append(f'<circle cx="{f2(cx + 5)}" cy="{f2(y - 3.5)}" r="4.5" fill="{cor}"/>')
        elif tipo == "linha":
            out.append(l_svg(cx, y - 3.5, cx + 14, y - 3.5, cor=cor, w=2))
        elif tipo == "faixa":
            out.append(f'<rect x="{f2(cx)}" y="{f2(y - 8.5)}" width="14" height="10" fill="{cor}" '
                       f'fill-opacity="0.16"/>' + l_svg(cx, y - 3.5, cx + 14, y - 3.5, cor=cor, w=2))
        elif tipo == "barra":
            out.append(f'<rect x="{f2(cx + 1)}" y="{f2(y - 9)}" width="10" height="11" fill="{cor}" '
                       f'fill-opacity="0.8"/>')
        elif tipo == "area":
            out.append(f'<rect x="{f2(cx)}" y="{f2(y - 9)}" width="14" height="11" fill="{cor}" '
                       f'stroke="{COR["axis"]}" stroke-width="0.6"/>')
        elif tipo == "anel":
            out.append(f'<circle cx="{f2(cx + 5)}" cy="{f2(y - 3.5)}" r="4.2" fill="{COR["surface"]}" '
                       f'stroke="{cor}" stroke-width="1.4"/>')
        elif tipo == "tracejada":
            out.append(l_svg(cx + 7, y - 10, cx + 7, y + 2, cor=cor, w=1.2, extra='stroke-dasharray="3 2.5"'))
        elif tipo == "vazio":
            out.append(l_svg(cx - 2, y - 3.5, cx + 12, y - 3.5, cor=cor, w=2, extra='stroke-dasharray="3 2"')
                       + f'<circle cx="{f2(cx + 5)}" cy="{f2(y - 3.5)}" r="3.8" fill="{COR["surface"]}" '
                         f'stroke="{cor}" stroke-width="1.6"/>')
        out.append(t_svg(cx + 19, y, rot, size=size, cor=COR["ink2"]))
        cx += 19 + largura_texto(rot, size) + 18
    return "".join(out)


def raio_n(n: int, k: float = 1.45, minimo: float = 1.8) -> float:
    """Raio de um ponto com area proporcional a n (bins dos graficos RD)."""
    return max(minimo, k * math.sqrt(max(n, 0)))


def legenda_tamanho(x: float, y: float, ns=(4, 10, 16), size=9.5, k: float = 1.45, cor=None) -> str:
    """Legenda de tamanho: circulos com area proporcional ao numero de municipios no bin."""
    o = [t_svg(x, y, "tamanho do ponto ∝ municípios no bin:", size=size, cor=COR["ink2"])]
    cx = x + largura_texto("tamanho do ponto ∝ municípios no bin:", size) + 10
    for n in ns:
        r = raio_n(n, k)
        o.append(f'<circle cx="{f2(cx + r)}" cy="{f2(y - 3.5)}" r="{f2(r)}" fill="none" '
                 f'stroke="{cor or COR["ink2"]}" stroke-width="1"/>')
        o.append(t_svg(cx + 2 * r + 4, y, str(n), size=size, cor=COR["ink2"]))
        cx += 2 * r + 4 + largura_texto(str(n), size) + 12
    return "".join(o)


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
        self.refs: dict[str, str] = {}

    def figura(self, chave: str | None = None) -> int:
        self.fig += 1
        if chave:
            self.refs[chave] = f"Figura {self.fig}"
        return self.fig

    def tabela(self, chave: str | None = None) -> int:
        self.tab += 1
        if chave:
            self.refs[chave] = f"Tabela {self.tab}"
        return self.tab

    def ref(self, chave: str, alternativa: str = "acima") -> str:
        """Rotulo ('Tabela 2', 'Figura 3') de um elemento ja numerado; so referencias para tras."""
        return self.refs.get(chave, alternativa)

    def proxima(self, tipo: str, salto: int = 1) -> str:
        """Rotulo do `salto`-esimo proximo elemento do tipo ('fig' ou 'tab'): referencia para a frente, valida
        quando nenhum outro elemento desse tipo e criado antes dele."""
        return f"Figura {self.fig + salto}" if tipo == "fig" else f"Tabela {self.tab + salto}"


NUM = Numerador()


def titulo_tabela(txt: str, chave: str | None = None) -> str:
    return f'<div class="tab-titulo"><span class="fig-num">Tabela {NUM.tabela(chave)}.</span> {txt}</div>'


def tabela(cabecalho: list[tuple[str, str]], linhas: list[list[str]], classe: str = "", titulo: str = "",
           rodape: str = "", inteiro: bool | None = None, legenda: str = "", grupos=None,
           chave: str | None = None) -> str:
    """cabecalho = [(rotulo, 'num'|'txt')]; linhas ja formatadas (HTML).

    Com `titulo`, devolve titulo + legenda + tabela + rodape num bloco; blocos
    curtos nao se partem entre paginas. `legenda` (HTML) vem logo abaixo do
    titulo, antes da tabela. `grupos` = [(rotulo, n_colunas)] acrescenta uma
    linha de cabecalho agrupando colunas (rotulo vazio = coluna sem grupo).
    """
    th = "".join(f'<th class="{c}">{r}</th>' for r, c in cabecalho)
    topo = ""
    if grupos:
        topo = "<tr>" + "".join(
            f'<th class="grupo" colspan="{n}">{r}</th>' if r else f'<th class="grupo vazio" colspan="{n}"></th>'
            for r, n in grupos) + "</tr>"
    trs = []
    for ln in linhas:
        tds = "".join(f'<td class="{cabecalho[i][1]}">{v}</td>' for i, v in enumerate(ln))
        trs.append(f"<tr>{tds}</tr>")
    tab = (f'<table class="{classe}"><thead>{topo}<tr>{th}</tr></thead>'
           f'<tbody>{"".join(trs)}</tbody></table>')
    if not titulo and not rodape and not legenda:
        return tab
    tt = titulo_tabela(titulo, chave) if titulo else ""
    if inteiro is None:
        inteiro = len(linhas) <= 18
    return f'<div class="bloco-tab{" inteiro" if inteiro else ""}">{tt}{legenda}{tab}{rodape}</div>'


def figura(titulo: str, svg: str, fonte: str, sub: str = "", nota: str = "", chave: str | None = None,
           legenda: str = "") -> str:
    """`legenda` (HTML, ex.: "como ler") vem logo abaixo do titulo, antes do subtitulo e do grafico."""
    n = NUM.figura(chave)
    s = f'<div class="fig-sub">{sub}</div>' if sub else ""
    nt = f'<div class="fig-nota">{nota}</div>' if nota else ""
    return (
        f'<figure class="fig"><div class="fig-titulo"><span class="fig-num">Figura {n}.</span> {titulo}</div>'
        f"{legenda}{s}{svg}{nt}{fonte}</figure>"
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

    # Conferencia do sinal (09b): tem de estar em dia com o E3 e sem divergencia.
    conf = ler_json(CONF_SINAL)
    if conf.get("status") != "CONFERIDO":
        raise SystemExit(f"Conferencia do sinal com status {conf.get('status')}: ver {rel(CONF_SINAL)}")
    sha_reg = ((conf.get("entradas") or {}).get(rel(E3_EST)) or {}).get("sha256")
    if sha_reg != sha256(E3_EST):
        raise SystemExit(f"{rel(CONF_SINAL)} nao corresponde ao {rel(E3_EST)} atual; rode "
                         "scripts/rdd_bolsa/09b_conferir_sinal.py antes do relatorio")
    return {
        "r1": r1, "r1_adm": ler_json(R1_ADMIN) or {}, "st": st, "prot": prot, "adendo": ler_json(ADENDO_E4) or {},
        "a01b": ler_json(A01B) or {}, "manif": ler_json(MANIF_OFICIAL) or {},
        "ident": ident or {}, "rl": recorte_local(ident),
        "cortes": cortes, "c_mil": c_mil, "faixas": faixas, "valor_faixa": valor_faixa,
        "mat": mat, "of": of, "loc": loc, "base": base, "est": est, "diag": diag, "conf": conf,
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
# Graficos RD, densidade e balanco (calculados aqui; conferidos contra o E3)
# ---------------------------------------------------------------------------


def ajuste_local_linear(s_mil: np.ndarray, y: np.ndarray, c_mil: int, h_mil: int) -> tuple[np.ndarray, np.ndarray]:
    """Mesmo MQP do E3: y = a + b x + tau T + d T x, pesos max(0, 1 - |x|/h). Devolve beta e a matriz HC1."""
    x = s_mil - c_mil
    w = np.clip(1.0 - np.abs(x) / h_mil, 0.0, None)
    usa = (x > -h_mil) & (x <= h_mil) & (w > 0) & np.isfinite(y)
    xs = x[usa] / 1000.0
    t = (x[usa] > 0).astype(float)
    X = np.column_stack([np.ones_like(xs), xs, t, t * xs])
    W = w[usa]
    pao = np.linalg.inv(X.T @ (X * W[:, None]))
    beta = pao @ (X.T @ (W * y[usa]))
    sc = X * (W * (y[usa] - X @ beta))[:, None]
    n, k = X.shape
    return beta, pao @ (sc.T @ sc) @ pao * (n / (n - k))


def reta_e_banda(beta: np.ndarray, V: np.ndarray, lado: int, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Valor da reta local em x (unidades de IVS, x = s - c) e meia-largura do IC 95% pontual (HC1)."""
    t = 1.0 if lado > 0 else 0.0
    G = np.column_stack([np.ones_like(x), x, np.full_like(x, t), t * x])
    se = np.sqrt(np.clip(np.einsum("ij,jk,ik->i", G, V, G), 0.0, None))
    return G @ beta, Z_975 * se


def medias_por_bin(s_mil: np.ndarray, y: np.ndarray, bordas_mil) -> list[dict]:
    """Media simples de y por bin (lo, hi] do escore em milesimos: o corte cai no bin de baixo, como T = 1[s > c]."""
    out = []
    for lo, hi in zip(bordas_mil[:-1], bordas_mil[1:]):
        sel = (s_mil > lo) & (s_mil <= hi) & np.isfinite(y)
        n = int(sel.sum())
        out.append({"lo": int(lo), "hi": int(hi), "n": n, "media": float(y[sel].mean()) if n else np.nan})
    return out


def dados_populacoes(ctx) -> dict[str, pd.DataFrame]:
    """P1 e P2 com IVS oficial e outcomes: D_k da relacao nominal (leitor do E3) e fracao preenchida do E4."""
    e3 = ctx["e3"]
    ativos = e3.ler_ativos(ATIVOS_ZIP)
    prop = pd.read_csv(E4_PROP, dtype={"co_ibge": str})
    out = {}
    for nome in ("P1", "P2"):
        g = populacao(ctx["base"], nome)[["co_ibge", "s_mil", "ivs", "faixa_anunciada", "valor_anunciado_brl"]].copy()
        if g["s_mil"].isna().any():
            raise SystemExit(f"Municipio de {nome} sem IVS oficial")
        k = int(((ctx["st"].get("populacoes") or {}).get(nome) or {}).get("ciclo_do_outcome"))
        g[OUTCOME_D] = g["co_ibge"].map(e3.construir_d_k(g["co_ibge"], ativos, k)).astype(float)
        if nome == "P1":
            if set(prop["co_ibge"]) != set(g["co_ibge"]):
                raise SystemExit("E4_proporcao_municipio.csv nao cobre exatamente os municipios de P1")
            g = g.merge(prop[["co_ibge", "y1"]].rename(columns={"y1": OUTCOME_FRAC}), on="co_ibge", how="left")
        out[nome] = g.reset_index(drop=True)
    return out


def linha_e3(ctx, pop: str, outcome: str, corte: float) -> pd.Series:
    est = ctx["est"]
    r = est[(est["populacao"] == pop) & (est["outcome"] == outcome) & np.isclose(est["corte"], corte)
            & np.isclose(est["h"], ctx["h_principal"])]
    if len(r) != 1:
        raise SystemExit(f"E3_estimativas sem linha unica para {pop}/{outcome}/{corte}")
    return r.iloc[0]


def conf_espec(ctx, pop: str, outcome: str, corte: float) -> dict:
    """Especificacao principal registrada em E3_conferencia_sinal.json."""
    for r in ctx["conf"].get("por_especificacao") or []:
        if (r["populacao"] == pop and r["outcome"] == outcome and math.isclose(r["corte"], corte)
                and math.isclose(r["h"], ctx["h_principal"])):
            return r
    raise SystemExit(f"{rel(CONF_SINAL)} sem a especificacao {pop}/{outcome}/{corte}")


def dados_rd(ctx) -> list[dict]:
    """Paineis RD locais (populacao x outcome x corte), conferidos contra o E3 e contra a conferencia do sinal."""
    h_mil = int(round(ctx["h_principal"] * 1000))
    vals = [ctx["valor_faixa"][f] for f in ctx["faixas"]]
    paineis = []
    for pop, outcome in COMBOS_RD:
        g = ctx["pops"][pop]
        s = g["s_mil"].to_numpy(float)
        y = g[outcome].to_numpy(float)
        for i, (c, c_m) in enumerate(zip(ctx["cortes"], ctx["c_mil"])):
            beta, V = ajuste_local_linear(s, y, c_m, h_mil)
            r = linha_e3(ctx, pop, outcome, c)
            ep = math.sqrt(V[2, 2])
            if abs(beta[2] - r["tau"]) > TOL_TAU or abs(ep - r["ep"]) > TOL_TAU:
                raise SystemExit(f"Reta do grafico RD (salto {beta[2]:.10f}, EP {ep:.10f}) difere do E3 "
                                 f"({r['tau']:.10f}, {r['ep']:.10f}) em {pop}/{outcome}/{c}")
            ind = conf_espec(ctx, pop, outcome, c)["independente"]
            lim0 = ind["lado_bolsa_menor"]["valor_da_reta_no_corte"]
            lim1 = ind["lado_bolsa_maior"]["valor_da_reta_no_corte"]
            if abs(lim0 - beta[0]) > TOL_TAU or abs(lim1 - (beta[0] + beta[2])) > TOL_TAU:
                raise SystemExit(f"Valores das retas no corte divergem de {rel(CONF_SINAL)} em {pop}/{outcome}/{c}")
            bins = medias_por_bin(s, y, list(range(c_m - ALCANCE_RD_MIL, c_m + ALCANCE_RD_MIL + 1, BIN_RD_MIL)))
            for b in bins:
                b["dentro"] = b["lo"] >= c_m - h_mil and b["hi"] <= c_m + h_mil
            paineis.append({"pop": pop, "outcome": outcome, "corte": c, "c_mil": c_m, "h_mil": h_mil,
                            "beta": beta, "V": V, "tau": float(r["tau"]), "ic_inf": float(r["ic95_inf"]),
                            "ic_sup": float(r["ic95_sup"]), "p": float(r["p_valor"]),
                            "n_abaixo": int(r["n_abaixo"]), "n_acima": int(r["n_acima"]),
                            "bolsa_menor": vals[i], "bolsa_maior": vals[i + 1], "bins": bins})
    return paineis


def dados_global(ctx) -> list[dict]:
    """Visao global (descritiva): medias em bins de 0,020 e polinomio de grau 2 em cada faixa de bolsa (MQO)."""
    if any(c % BIN_GLOBAL_MIL for c in ctx["c_mil"]):
        raise SystemExit("Os cortes precisam ser bordas dos bins da visao global")
    vals = [ctx["valor_faixa"][f] for f in ctx["faixas"]]
    limites = [-math.inf] + list(ctx["c_mil"]) + [math.inf]
    out = []
    for pop, outcome in COMBOS_RD:
        g = ctx["pops"][pop]
        s = g["s_mil"].to_numpy(float)
        y = g[outcome].to_numpy(float)
        lo = int(math.floor(s.min() / BIN_GLOBAL_MIL) * BIN_GLOBAL_MIL)
        hi = int(math.ceil(s.max() / BIN_GLOBAL_MIL) * BIN_GLOBAL_MIL)
        segmentos = []
        for j in range(len(limites) - 1):
            sel = (s > limites[j]) & (s <= limites[j + 1]) & np.isfinite(y)
            if sel.sum() <= GRAU_GLOBAL + 1:
                continue
            centro = float(np.mean(s[sel]))
            xs = (s[sel] - centro) / 1000.0
            X = np.column_stack([xs ** k for k in range(GRAU_GLOBAL + 1)])
            coef = np.linalg.lstsq(X, y[sel], rcond=None)[0]
            segmentos.append({"j": j, "s_min": float(s[sel].min()), "s_max": float(s[sel].max()), "centro": centro,
                              "coef": coef, "n": int(sel.sum()), "bolsa": vals[j]})
        out.append({"pop": pop, "outcome": outcome, "n": int(np.isfinite(y).sum()),
                    "bins": medias_por_bin(s, y, list(range(lo, hi + 1, BIN_GLOBAL_MIL))), "segmentos": segmentos})
    return out


def poisson_mass_points(s_mil: np.ndarray, c_mil: int, h_mil: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Ajuste de densidade do E3: contagem por mass point de 0,001 em (c - h, c + h], log-linear de cada lado."""
    grade = np.arange(c_mil - h_mil + 1, c_mil + h_mil + 1)
    valores, contagens = np.unique(np.asarray(s_mil).astype(int), return_counts=True)
    mapa = dict(zip(valores.tolist(), contagens.tolist()))
    y = np.array([mapa.get(v, 0) for v in grade], dtype=float)
    x = (grade - c_mil) / 1000.0
    t = (grade > c_mil).astype(float)
    X = np.column_stack([np.ones_like(x), x, t, t * x])
    beta = np.linalg.lstsq(X, np.log(y + 0.5), rcond=None)[0]
    for _ in range(200):
        mu = np.exp(X @ beta)
        novo = np.linalg.solve(X.T @ (X * mu[:, None]), X.T @ (mu * (X @ beta + (y - mu) / mu)))
        convergiu = np.max(np.abs(novo - beta)) < 1e-10
        beta = novo
        if convergiu:
            break
    else:
        raise SystemExit("Ajuste de densidade nao convergiu")
    return grade, np.exp(X @ beta), beta


def dados_densidade(ctx) -> list[dict]:
    """Histograma do IVS (bins de 0,005) em torno de cada corte e contagem esperada pelo ajuste do E3."""
    diag = ctx["diag"]
    h_mil = int(round(ctx["h_principal"] * 1000))
    vals = [ctx["valor_faixa"][f] for f in ctx["faixas"]]
    out = []
    for pop in ("P1", "P2"):
        s = ctx["pops"][pop]["s_mil"].to_numpy(float)
        for i, (c, c_m) in enumerate(zip(ctx["cortes"], ctx["c_mil"])):
            r = diag[(diag["diagnostico"] == "densidade_poisson_mass_points") & (diag["populacao"] == pop)
                     & np.isclose(diag["corte"], c) & np.isclose(diag["h"], ctx["h_principal"])]
            if len(r) != 1:
                raise SystemExit(f"E3_diagnosticos sem densidade unica para {pop}/{c}")
            r = r.iloc[0]
            grade, mu, beta = poisson_mass_points(s, c_m, h_mil)
            if abs(math.exp(beta[2]) - r["rho"]) > TOL_RHO:
                raise SystemExit(f"Razao de densidades refeita ({math.exp(beta[2]):.8f}) difere do E3 "
                                 f"({r['rho']:.8f}) em {pop}/{c}")
            hist = []
            for lo in range(c_m - ALCANCE_RD_MIL, c_m + ALCANCE_RD_MIL, BIN_DENS_MIL):
                hi = lo + BIN_DENS_MIL
                no_bin = (grade > lo) & (grade <= hi)
                hist.append({"lo": lo, "hi": hi, "n": int(((s > lo) & (s <= hi)).sum()),
                             "esperado": float(mu[no_bin].sum()) if no_bin.sum() == BIN_DENS_MIL else np.nan,
                             "dentro": lo >= c_m - h_mil and hi <= c_m + h_mil})
            out.append({"pop": pop, "corte": c, "c_mil": c_m, "h_mil": h_mil, "rho": float(r["rho"]),
                        "ic_inf": float(r["rho_ic95_inf"]), "ic_sup": float(r["rho_ic95_sup"]),
                        "p": float(r["p_valor"]), "bolsa_menor": vals[i], "bolsa_maior": vals[i + 1], "hist": hist})
    return out


def dados_balanco(ctx) -> tuple[pd.DataFrame | None, str]:
    """Saltos de balanco do E3 (janela principal) em desvios-padrao da covariavel na populacao."""
    try:
        cov, notas = ctx["e3"].carregar_covariaveis(ROOT)
    except Exception as erro:  # noqa: BLE001 - a figura e opcional; a tabela continua
        return None, f"{type(erro).__name__}: {erro}"
    bal = balanco_principal(ctx)
    linhas = []
    for (pop, corte, var), g in bal.groupby(["populacao", "corte", "variavel"], sort=False):
        if var not in cov.columns:
            continue
        m = ctx["pops"][pop][["co_ibge"]].merge(cov[["co_ibge", var]], on="co_ibge", how="left")[var]
        dp = float(pd.to_numeric(m, errors="coerce").std(ddof=1))
        if not (finito(dp) and dp > 0):
            continue
        r = g.iloc[0]
        linhas.append({"populacao": pop, "corte": float(corte), "variavel": var, "dp": dp,
                       "tau_dp": r["tau"] / dp, "ic_inf_dp": r["ic95_inf"] / dp, "ic_sup_dp": r["ic95_sup"] / dp,
                       "p_valor": r["p_valor"]})
    nao_lidas = [k for k, v in notas.items() if isinstance(v, dict) and v.get("status") == "nao_lido"]
    return pd.DataFrame(linhas), ("; ".join(nao_lidas) if nao_lidas else "")


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


_UID = itertools.count(1)  # ids unicos de gradientes e recortes (varios SVG no mesmo HTML)


def _hex_rgb(h: str) -> tuple[int, int, int]:
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def cor_ivs(v: float) -> str:
    """Cor da escala verde -> amarelo -> vermelho para um IVS (interpolacao sRGB entre as ancoras)."""
    pts = ESCALA_IVS
    if not finito(v) or v <= pts[0][0]:
        return pts[0][1]
    for (a, ca), (b, cb) in zip(pts[:-1], pts[1:]):
        if v <= b:
            t = (v - a) / (b - a)
            return "#" + "".join(f"{round(p + (q - p) * t):02x}" for p, q in zip(_hex_rgb(ca), _hex_rgb(cb)))
    return pts[-1][1]


def legenda_cor_ivs(x: float, y: float, largura: float, lo: float, hi: float, size=9.5) -> str:
    """Legenda da escala de cor: barra em gradiente (mesma interpolacao de cor_ivs) com marcas de 0,1."""
    uid = f"gradIVS{next(_UID)}"
    paradas = [(0.0, cor_ivs(lo))] + [((v - lo) / (hi - lo), c) for v, c in ESCALA_IVS if lo < v < hi]
    paradas.append((1.0, cor_ivs(hi)))
    st = "".join(f'<stop offset="{f2(100 * o)}%" stop-color="{c}"/>' for o, c in paradas)
    rot = "Cor = IVS do eixo horizontal:"
    x_menor = x + largura_texto(rot, size) + 10
    bx = x_menor + largura_texto("menor", size - 1) + 6
    B = Linear(lo, hi, bx, bx + largura)
    o = [f'<defs><linearGradient id="{uid}" x1="0" x2="1" y1="0" y2="0">{st}</linearGradient></defs>',
         t_svg(x, y, rot, size=size, cor=COR["ink2"]),
         t_svg(x_menor, y - 1, "menor", size=size - 1, cor=COR["muted"]),
         f'<rect x="{f2(bx)}" y="{f2(y - 9)}" width="{f2(largura)}" height="8" rx="1.5" fill="url(#{uid})"/>',
         t_svg(bx + largura + 6, y - 1, "maior", size=size - 1, cor=COR["muted"])]
    for t in nice_ticks(lo, hi, 7):
        if lo - 1e-9 <= t <= hi + 1e-9:
            o.append(l_svg(B(t), y - 1, B(t), y + 2, COR["muted"]))
            o.append(t_svg(B(t), y + 11, br(t, 1), anchor="middle", size=size - 1, cor=COR["muted"]))
    return "".join(o)


def fig_regra_pontos(s, faixa_anunciada, errado, eixo_x: str, cortes, faixas, valor_faixa, x0: float, x1: float,
                     ids=None, destacar: bool = False, rotulo_errado: str = "") -> str:
    """Variante A da galeria, colorida pelo IVS: um ponto por municipio no valor exato da bolsa, sem deslocamento.

    A cor repete o IVS do eixo horizontal (verde -> amarelo -> vermelho). Onde ha muitos municipios, os
    pontos semitransparentes se sobrepoem e a cor fica mais forte. Com `destacar`, os municipios cuja faixa
    anunciada nao e a que os cortes dariam ganham contorno preto e ficam por cima dos demais.
    """
    s = np.asarray(s, float)
    errado = np.asarray(errado, bool)
    faixa_anunciada = list(faixa_anunciada)
    ids = None if ids is None else list(ids)
    nivel = np.array([faixas.index(f) for f in faixa_anunciada])
    vals = [valor_faixa[f] for f in faixas]
    W, H = 680, 262
    ml, mr, mt, mb = 74, 24, 66, 44
    X = Linear(x0, x1, ml, W - mr)
    Y = Linear(-0.55, 2.55, H - mb, mt)
    o = [svg_abrir(W, H, "Valor anunciado da bolsa contra o IVS: um ponto por município, colorido pelo IVS")]
    o.append(legenda_cor_ivs(ml, 15, 210, x0, x1))
    if destacar:
        o.append(legenda_svg([("anel", CONTORNO_ERRADO, rotulo_errado)], ml, 44, size=9.5))
    for tx in nice_ticks(x0, x1, 7):
        o.append(l_svg(X(tx), H - mb, X(tx), H - mb + 4, COR["axis"]))
        o.append(t_svg(X(tx), H - mb + 16, br(tx, 2), anchor="middle"))
    o.append(l_svg(ml, H - mb, W - mr, H - mb, COR["axis"]))
    o.append(t_svg((ml + W - mr) / 2, H - 6, eixo_x, anchor="middle"))
    for i, v in enumerate(vals):
        o.append(t_svg(ml - 8, Y(i) + 3.5, br_mil(v), anchor="end", cor=COR["ink"]))
    for c in cortes:
        o.append(l_svg(X(c), mt - 4, X(c), H - mb, COR["ink2"], w=1.2, extra='stroke-dasharray="4 3"'))
        o.append(t_svg(X(c), mt - 9, br(c, 3), anchor="middle", cor=COR["ink"], peso=600))
    degrau = [(x0, 0), (cortes[0], 0), (cortes[0], 1), (cortes[1], 1), (cortes[1], 2), (x1, 2)]
    o.append('<path d="' + " ".join(f"{'M' if i == 0 else 'L'}{f2(X(a))},{f2(Y(b))}" for i, (a, b) in enumerate(degrau))
             + f'" fill="none" stroke="{COR["axis"]}" stroke-width="1.5"/>')
    for i, c in enumerate(cortes):
        o.append(t_svg(X(c) + 6, Y(i + 0.5) + 4, f"+{br_mil(vals[i + 1] - vals[i])}", cor=COR["ink"], peso=600,
                       size=10))
    ordem = np.argsort(errado if destacar else np.zeros(len(s)), kind="stable")
    for k in ordem:
        cor = cor_ivs(s[k])
        rotulo = "" if ids is None else f"{ids[k]}: "
        tt = f"<title>{esc(rotulo)}IVS {br(s[k])}; {esc(faixa_anunciada[k])} ({br_mil(vals[nivel[k]])})</title>"
        if destacar and errado[k]:
            o.append(f'<circle cx="{f2(X(s[k]))}" cy="{f2(Y(nivel[k]))}" r="3.9" fill="{cor}" fill-opacity="0.95" '
                     f'stroke="{CONTORNO_ERRADO}" stroke-width="1.4">{tt}</circle>')
        else:
            o.append(f'<circle cx="{f2(X(s[k]))}" cy="{f2(Y(nivel[k]))}" r="3.6" fill="{cor}" '
                     f'fill-opacity="0.6">{tt}</circle>')
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


def rotulo_combo(ctx, pop: str, outcome: str) -> str:
    return f"{rotulo_pop(ctx, pop, curto=True)} · {rotulo_outcome(ctx, outcome)}"


def dominio_y(paineis: list[dict]) -> tuple[float, float]:
    """[0, 1], estendido se preciso para conter as retas (as bandas de IC sao recortadas no painel)."""
    ymin, ymax = 0.0, 1.0
    for p in paineis:
        a, b, tau, dd = p["beta"]
        hh = p["h_mil"] / 1000
        for v in (a - b * hh, a, a + tau, a + tau + (b + dd) * hh):
            ymin, ymax = min(ymin, v), max(ymax, v)
    return math.floor(ymin * 4) / 4, math.ceil(ymax * 4) / 4


def texto_halo(x, y, s, size=9.0, anchor="start", cor=None, peso=None) -> str:
    """Texto com halo da cor da superficie, legivel sobre pontos e linhas."""
    return t_svg(x, y, s, size=size, anchor=anchor, cor=cor, peso=peso,
                 extra=f'stroke="{COR["surface"]}" stroke-width="3" paint-order="stroke" stroke-linejoin="round"')


def eixo_corte(o: list, X, c: float, base: float, bolsa_menor: float, bolsa_maior: float, passo: float = 0.04) -> None:
    """Marcas do eixo x em torno do corte e, abaixo, a bolsa anunciada de cada lado."""
    for k in range(-2, 3):
        t = c + k * passo
        o.append(l_svg(X(t), base, X(t), base + 4, COR["axis"]))
        o.append(t_svg(X(t), base + 15, br(t, 3 if k == 0 else 2), anchor="middle", size=9.5,
                       cor=COR["ink"] if k == 0 else None, peso=600 if k == 0 else None))
    o.append(t_svg(X(c) - 5, base + 29, f"← IVS ≤ {br(c)}: {br_mil(bolsa_menor)}", anchor="end", size=9,
                   cor=COR["ink2"]))
    o.append(t_svg(X(c) + 5, base + 29, f"IVS > {br(c)}: {br_mil(bolsa_maior)} →", size=9, cor=COR["ink2"]))


def fig_rd_local(ctx, paineis: list[dict], combos) -> str:
    """Grafico RD tradicional: uma linha por populacao x outcome e um painel por corte.

    Medias por bin de 0,010 (area do ponto proporcional ao numero de municipios), retas locais lineares
    da especificacao principal com IC 95% pontual (HC1), corte, bolsa de cada lado e salto anotado.
    """
    paineis = [p for p in paineis if (p["pop"], p["outcome"]) in combos]
    W = 680
    ml, mr, gapx = 46, 12, 40
    pw = (W - ml - mr - gapx) / 2
    ph = 150
    leg_h = 46
    rot_h = 22 if len(combos) > 1 else 0
    cab_h = 32
    eixo_h = 36
    row_h = rot_h + cab_h + ph + eixo_h + 10
    H = int(leg_h + len(combos) * row_h)
    ymin, ymax = dominio_y(paineis)
    o = [svg_abrir(W, H, "Gráfico RD: médias por bin do IVS, retas locais lineares e IC 95% em cada corte")]
    o.append(legenda_svg([("ponto", COR["s1"], "média no bin de 0,010 (dentro da janela)"),
                          ("ponto", COR["muted"], "média no bin (fora da janela)"),
                          ("faixa", COR["s1"], f"reta local linear e IC 95% (h = {br(ctx['h_principal'], 3)})")],
                         6, 14, size=9.5))
    o.append(legenda_tamanho(6, 34))
    o.append(t_svg(330, 34, "traço preto no corte: salto = reta da direita − reta da esquerda", size=9.5,
                   cor=COR["ink2"]))
    for ri, (pop, outcome) in enumerate(combos):
        top = leg_h + ri * row_h
        if rot_h:
            o.append(t_svg(6, top + 14, maiuscula(rotulo_combo(ctx, pop, outcome)), cor=COR["ink"], peso=650,
                           size=10.5))
        for ci, p in enumerate([q for q in paineis if (q["pop"], q["outcome"]) == (pop, outcome)]):
            left = ml + ci * (pw + gapx)
            right = left + pw
            ctop = top + rot_h
            ptop = ctop + cab_h
            base = ptop + ph
            c, hh = p["corte"], p["h_mil"] / 1000
            X = Linear(c - ALCANCE_RD_MIL / 1000, c + ALCANCE_RD_MIL / 1000, left, right)
            Y = Linear(ymin, ymax, base, ptop)
            o.append(t_svg(left, ctop + 11, f"Corte {br(c)}: bolsa {br_mil(p['bolsa_menor'])} → "
                                            f"{br_mil(p['bolsa_maior'])}", cor=COR["ink"], peso=600, size=10))
            o.append(t_svg(left, ctop + 25, f"salto {pp(p['tau'])} p.p. · IC 95% {ic_pp(p['ic_inf'], p['ic_sup'])}"
                                            f" · p = {br_p(p['p'])}", size=9.3, cor=COR["ink2"]))
            o.append(f'<rect x="{f2(X(c - hh))}" y="{f2(ptop)}" width="{f2(X(c + hh) - X(c - hh))}" '
                     f'height="{f2(ph)}" fill="{COR["wash"]}"/>')
            for t in np.arange(ymin, ymax + 1e-9, 0.25):
                o.append(l_svg(left, Y(t), right, Y(t), COR["grid"]))
                o.append(t_svg(left - 6, Y(t) + 3.5, f"{int(round(t * 100))}%", anchor="end", size=9))
            o.append(l_svg(left, base, right, base, COR["axis"]))
            eixo_corte(o, X, c, base, p["bolsa_menor"], p["bolsa_maior"])
            clip = f"clipRD{next(_UID)}"
            o.append(f'<clipPath id="{clip}"><rect x="{f2(left)}" y="{f2(ptop)}" width="{f2(pw)}" '
                     f'height="{f2(ph)}"/></clipPath>')
            for lado in (-1, 1):
                xs = np.linspace(-hh, 0.0, 41) if lado < 0 else np.linspace(0.0, hh, 41)
                yh, meia = reta_e_banda(p["beta"], p["V"], lado, xs)
                contorno = ([(X(c + a), Y(b + m)) for a, b, m in zip(xs, yh, meia)]
                            + [(X(c + a), Y(b - m)) for a, b, m in zip(xs[::-1], yh[::-1], meia[::-1])])
                d = "M" + " L".join(f"{f2(a)},{f2(b)}" for a, b in contorno) + " Z"
                o.append(f'<path d="{d}" fill="{COR["s1"]}" fill-opacity="0.14" clip-path="url(#{clip})"/>')
                o.append(f'<path d="M{f2(X(c + xs[0]))},{f2(Y(yh[0]))} L{f2(X(c + xs[-1]))},{f2(Y(yh[-1]))}" '
                         f'stroke="{COR["s1"]}" stroke-width="2" stroke-linecap="round" fill="none" '
                         f'clip-path="url(#{clip})"/>')
            o.append(l_svg(X(c), ptop, X(c), base, COR["ink2"], 1))
            for b_ in p["bins"]:
                if not b_["n"]:
                    continue
                cor = COR["s1"] if b_["dentro"] else COR["muted"]
                xm = (b_["lo"] + b_["hi"]) / 2000
                tt = f"({br(b_['lo'] / 1000)}; {br(b_['hi'] / 1000)}]: n = {b_['n']}, média = {pct(b_['media'])}"
                o.append(ponto(X(xm), Y(b_["media"]), cor, r=f2(raio_n(b_["n"])), titulo=tt, opacidade=0.85,
                               anel=1.2))
            a, tau = p["beta"][0], p["beta"][2]
            o.append(l_svg(X(c), Y(a), X(c), Y(a + tau), COR["ink"], 1.8))
            for yy in (Y(a), Y(a + tau)):
                o.append(l_svg(X(c) - 4, yy, X(c) + 4, yy, COR["ink"], 1.8))
            o.append(texto_halo(X(c) - 7, Y(a) + 3.5, pct(a), anchor="end", cor=COR["ink"], peso=600))
            o.append(texto_halo(X(c) + 7, Y(a + tau) + 3.5, pct(a + tau), cor=COR["ink"], peso=600))
    o.append("</svg>")
    return "".join(o)


def fig_rd_global(ctx, globais: list[dict], combos) -> str:
    """Visao global (descritiva): medias por bin de 0,020 em todo o suporte do IVS, cortes, janelas da RDD e
    polinomio de grau 2 ajustado por MQO aos municipios de cada faixa de bolsa."""
    gl = [g for g in globais if (g["pop"], g["outcome"]) in combos]
    W = 680
    ml, mr = 46, 12
    ph = 118
    leg_h = 26
    rot_h = 22
    eixo_h = 36
    row_h = rot_h + ph + eixo_h + 8
    H = int(leg_h + len(gl) * row_h + 14)
    bordas = [b["lo"] for g in gl for b in g["bins"]] + [b["hi"] for g in gl for b in g["bins"]]
    x0, x1 = math.floor(min(bordas) / 50) * 0.05, math.ceil(max(bordas) / 50) * 0.05
    X = Linear(x0, x1, ml, W - mr)
    h = ctx["h_principal"]
    cortes = ctx["cortes"]
    o = [svg_abrir(W, H, "Visão global: médias por bin em todo o suporte do IVS e ajuste descritivo em cada faixa")]
    o.append(legenda_svg([("ponto", COR["s1"], "média no bin de 0,020 (área ∝ municípios)"),
                          ("linha", COR["ink2"], f"polinômio de grau {GRAU_GLOBAL} em cada faixa (descritivo)"),
                          ("area", COR["wash"], f"janelas da RDD (±{br(h, 3)})")], 6, 14, size=9.5))
    for ri, g in enumerate(gl):
        top = leg_h + ri * row_h
        ptop = top + rot_h
        base = ptop + ph
        Y = Linear(0.0, 1.0, base, ptop)
        o.append(t_svg(6, top + 14, f"{maiuscula(rotulo_combo(ctx, g['pop'], g['outcome']))} · "
                                    f"{br_int(g['n'])} municípios", cor=COR["ink"], peso=650, size=10.5))
        for c in cortes:
            o.append(f'<rect x="{f2(X(c - h))}" y="{f2(ptop)}" width="{f2(X(c + h) - X(c - h))}" '
                     f'height="{f2(ph)}" fill="{COR["wash"]}"/>')
        for t in (0, 0.25, 0.5, 0.75, 1.0):
            o.append(l_svg(ml, Y(t), W - mr, Y(t), COR["grid"]))
            o.append(t_svg(ml - 6, Y(t) + 3.5, f"{int(round(t * 100))}%", anchor="end", size=9))
        o.append(l_svg(ml, base, W - mr, base, COR["axis"]))
        for t in nice_ticks(x0, x1, 8):
            o.append(l_svg(X(t), base, X(t), base + 4, COR["axis"]))
            o.append(t_svg(X(t), base + 15, br(t, 2), anchor="middle", size=9.5))
        limites = [x0] + list(cortes) + [x1]
        for sg in g["segmentos"]:
            j = sg["j"]
            o.append(t_svg((X(limites[j]) + X(limites[j + 1])) / 2, base + 29, f"bolsa {br_mil(sg['bolsa'])}",
                           anchor="middle", size=9, cor=COR["ink2"]))
        for c in cortes:
            o.append(l_svg(X(c), ptop, X(c), base, COR["ink2"], 1))
        clip = f"clipGL{next(_UID)}"
        o.append(f'<clipPath id="{clip}"><rect x="{f2(ml)}" y="{f2(ptop)}" width="{f2(W - mr - ml)}" '
                 f'height="{f2(ph)}"/></clipPath>')
        for sg in g["segmentos"]:
            ss = np.linspace(sg["s_min"], sg["s_max"], 50)
            xs = (ss - sg["centro"]) / 1000.0
            yy = sum(cf * xs ** k for k, cf in enumerate(sg["coef"]))
            d = " ".join(f"{'M' if i == 0 else 'L'}{f2(X(a / 1000))},{f2(Y(b))}" for i, (a, b) in enumerate(zip(ss, yy)))
            o.append(f'<path d="{d}" fill="none" stroke="{COR["ink2"]}" stroke-width="2" stroke-linecap="round" '
                     f'clip-path="url(#{clip})"/>')
        for b_ in g["bins"]:
            if not b_["n"]:
                continue
            xm = (b_["lo"] + b_["hi"]) / 2000
            tt = f"({br(b_['lo'] / 1000)}; {br(b_['hi'] / 1000)}]: n = {b_['n']}, média = {pct(b_['media'])}"
            o.append(ponto(X(xm), Y(b_["media"]), COR["s1"], r=f2(raio_n(b_["n"], k=1.2)), titulo=tt,
                           opacidade=0.8, anel=1.2))
    o.append(t_svg((ml + W - mr) / 2, H - 4, "IVS 2010 oficial do município", anchor="middle", size=10))
    o.append("</svg>")
    return "".join(o)


def fig_densidade(ctx, dens: list[dict]) -> str:
    """Histograma do IVS (bins de 0,005) em torno de cada corte, com a contagem esperada pelo ajuste do E3."""
    W = 680
    ml, mr, gapx = 40, 12, 40
    pw = (W - ml - mr - gapx) / 2
    ph = 100
    leg_h = 26
    rot_h = 22
    cab_h = 32
    eixo_h = 36
    row_h = rot_h + cab_h + ph + eixo_h + 8
    pops = [p for p in ("P1", "P2") if any(d["pop"] == p for d in dens)]
    H = int(leg_h + len(pops) * row_h)
    o = [svg_abrir(W, H, "Histograma do IVS em torno de cada corte, com a contagem esperada pelo ajuste do E3")]
    o.append(legenda_svg([("barra", COR["s1"], "municípios por bin de 0,005 (dentro da janela)"),
                          ("barra", COR["muted"], "fora da janela"),
                          ("linha", COR["ink"], "contagem esperada pelo ajuste log-linear do E3")], 6, 14, size=9.5))
    for ri, pop in enumerate(pops):
        top = leg_h + ri * row_h
        dd = [d for d in dens if d["pop"] == pop]
        o.append(t_svg(6, top + 14, f"{rotulo_pop(ctx, pop, curto=True)}: {br_int(len(ctx['pops'][pop]))} municípios "
                                    "do quadro", cor=COR["ink"], peso=650, size=10.5))
        ymax = max(max(b["n"] for b in d["hist"]) for d in dd)
        ymax = max(ymax, max(b["esperado"] for d in dd for b in d["hist"] if finito(b["esperado"])))
        ticks = [t for t in nice_ticks(0, ymax, 4)]
        ytop = max(ticks[-1], ymax)
        for ci, d in enumerate(dd):
            left = ml + ci * (pw + gapx)
            right = left + pw
            ctop = top + rot_h
            ptop = ctop + cab_h
            base = ptop + ph
            c = d["corte"]
            X = Linear(c - ALCANCE_RD_MIL / 1000, c + ALCANCE_RD_MIL / 1000, left, right)
            Y = Linear(0, ytop, base, ptop)
            o.append(t_svg(left, ctop + 11, f"Corte {br(c)}: bolsa {br_mil(d['bolsa_menor'])} → "
                                            f"{br_mil(d['bolsa_maior'])}", cor=COR["ink"], peso=600, size=10))
            o.append(t_svg(left, ctop + 25, f"razão de densidades ρ = {br(d['rho'], 2)} · IC 95% [{br(d['ic_inf'], 2)}; "
                                            f"{br(d['ic_sup'], 2)}] · p = {br_p(d['p'])}", size=9.3, cor=COR["ink2"]))
            for t in ticks:
                o.append(l_svg(left, Y(t), right, Y(t), COR["grid"]))
                o.append(t_svg(left - 6, Y(t) + 3.5, br_int(t), anchor="end", size=9))
            for b in d["hist"]:
                if not b["n"]:
                    continue
                x_a, x_b = X(b["lo"] / 1000) + 1, X(b["hi"] / 1000) - 1
                cor, op = (COR["s1"], 0.8) if b["dentro"] else (COR["muted"], 0.55)
                o.append(f'<rect x="{f2(x_a)}" y="{f2(Y(b["n"]))}" width="{f2(x_b - x_a)}" '
                         f'height="{f2(base - Y(b["n"]))}" fill="{cor}" fill-opacity="{op}">'
                         f'<title>({br(b["lo"] / 1000)}; {br(b["hi"] / 1000)}]: {b["n"]} municípios</title></rect>')
            for lado in (-1, 1):
                pts = [((b["lo"] + b["hi"]) / 2000, b["esperado"]) for b in d["hist"]
                       if b["dentro"] and finito(b["esperado"])
                       and ((b["hi"] <= d["c_mil"]) if lado < 0 else (b["lo"] >= d["c_mil"]))]
                if len(pts) > 1:
                    dd_ = " ".join(f"{'M' if i == 0 else 'L'}{f2(X(a))},{f2(Y(v))}" for i, (a, v) in enumerate(pts))
                    o.append(f'<path d="{dd_}" fill="none" stroke="{COR["ink"]}" stroke-width="2" '
                             'stroke-linecap="round" stroke-linejoin="round"/>')
            o.append(l_svg(left, base, right, base, COR["axis"]))
            o.append(l_svg(X(c), ptop, X(c), base, COR["ink2"], 1))
            eixo_corte(o, X, c, base, d["bolsa_menor"], d["bolsa_maior"])
    o.append("</svg>")
    return "".join(o)


def fig_balanco(ctx, bal: pd.DataFrame) -> str:
    """Balanco de covariaveis pre-programa: salto no corte +- IC 95%, em desvios-padrao, por corte e ciclo."""
    variaveis = [v for v in ROTULO_COV if v in set(bal["variavel"])] + sorted(set(bal["variavel"]) - set(ROTULO_COV))
    pops = [p for p in ("P1", "P2") if p in set(bal["populacao"])]
    cortes = ctx["cortes"]
    W = 680
    lab_w, gapx, mr = 208, 26, 14
    pw = (W - lab_w - gapx - mr) / 2
    RH = 15
    leg_h = 26
    rot_h = 22
    cab_h = 16
    eixo_h = 22
    bloco_h = rot_h + cab_h + len(variaveis) * RH + eixo_h + 8
    H = int(leg_h + len(pops) * bloco_h + 14)
    m = max(1.0, math.ceil(2 * float(np.nanmax(np.abs(bal[["ic_inf_dp", "ic_sup_dp"]].to_numpy())))) / 2)
    passo = 0.5 if m <= 1.5 else 1.0
    o = [svg_abrir(W, H, "Balanço de covariáveis pré-programa: salto no corte em desvios-padrão, com IC 95%")]
    o.append(legenda_svg([("ponto", COR["s1"], "salto e IC 95% (o IC contém zero)"),
                          ("ponto", COR["s2"], "p < 0,05")], 6, 14, size=9.5))
    for bi, pop in enumerate(pops):
        top = leg_h + bi * bloco_h
        o.append(t_svg(6, top + 14, f"{rotulo_pop(ctx, pop, curto=True)}: {br_int(len(ctx['pops'][pop]))} municípios "
                                    "do quadro", cor=COR["ink"], peso=650, size=10.5))
        ctop = top + rot_h
        ptop = ctop + cab_h
        base = ptop + len(variaveis) * RH
        for vi, v in enumerate(variaveis):
            yy = ptop + (vi + 0.5) * RH
            o.append(t_svg(lab_w - 10, yy + 3.5, rotulo_cov(v), anchor="end", size=9.3, cor=COR["ink2"]))
        for ci, c in enumerate(cortes):
            left = lab_w + ci * (pw + gapx)
            right = left + pw
            X = Linear(-m, m, left, right)
            o.append(t_svg((left + right) / 2, ctop + 11, f"Corte {br(c)}", anchor="middle", cor=COR["ink"], peso=600,
                           size=10))
            t = -m
            while t <= m + 1e-9:
                o.append(l_svg(X(t), ptop, X(t), base, COR["grid"]))
                o.append(t_svg(X(t), base + 14, sinal(t, 1), anchor="middle", size=9))
                t += passo
            o.append(l_svg(X(0), ptop, X(0), base, COR["ink"], 1.2))
            o.append(l_svg(left, base, right, base, COR["axis"]))
            for vi, v in enumerate(variaveis):
                yy = ptop + (vi + 0.5) * RH
                r = bal[(bal["populacao"] == pop) & np.isclose(bal["corte"], c) & (bal["variavel"] == v)]
                if len(r) != 1:
                    continue
                r = r.iloc[0]
                cor = COR["s2"] if r["p_valor"] < ALFA else COR["s1"]
                a, z = X(max(r["ic_inf_dp"], -m)), X(min(r["ic_sup_dp"], m))
                o.append(l_svg(a, yy, z, yy, cor, 2, extra='stroke-linecap="round"'))
                tt = (f"{rotulo_cov(v)}, {rotulo_pop(ctx, pop, curto=True)}, corte {br(c)}: {sinal(r['tau_dp'], 2)} DP "
                      f"[{sinal(r['ic_inf_dp'], 2)}; {sinal(r['ic_sup_dp'], 2)}], p = {br_p(r['p_valor'])}")
                o.append(ponto(X(r["tau_dp"]), yy, cor, r=3.6, titulo=tt, anel=1.2))
    o.append(t_svg(lab_w + (W - lab_w - mr) / 2, H - 4, "salto no corte ÷ desvio-padrão da covariável na população "
                                                       "do ciclo (0 = sem diferença)", anchor="middle", size=9.5))
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
    """Balanco na janela principal, sem a running variable (o IVS oficial nao entra no teste de balanco)."""
    d = ctx["diag"]
    b = d[(d["diagnostico"] == "balanco_covariavel_pre") & np.isclose(d["h"], ctx["h_principal"])]
    return b[b["variavel"] != COVARIAVEL_RUNNING].copy()


SUBINDICES_IVS = ["ivs_infra_2010", "ivs_ch_2010", "ivs_rt_2010"]  # componentes do IVS (media simples)


def nota_running_balanco(ctx) -> str:
    """Ressalva do balanco: o IVS e a running variable; os subindices sao componentes dele."""
    d = ctx["diag"]
    b = d[(d["diagnostico"] == "balanco_covariavel_pre") & d["variavel"].isin(SUBINDICES_IVS)]
    chaves = ["populacao", "corte", "h"]
    soma = b.groupby(chaves)["tau"].sum()
    completo = len(soma) and bool((b.groupby(chaves)["variavel"].nunique() == len(SUBINDICES_IVS)).all())
    extra = (" Por isso os saltos dos três subíndices somam quase zero em cada corte e janela (no máximo "
             f"{br(soma.abs().max(), 4)} em valor absoluto): não são três testes independentes." if completo else "")
    return ("O IVS 2010 oficial é a própria running variable e não entra no teste de balanço; os subíndices "
            "(infraestrutura urbana, capital humano, renda e trabalho) são componentes do IVS, cuja média é contínua "
            "no corte por construção — leia o balanço deles com essa ressalva." + extra)


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
        ("Conferência do sinal do salto", "pill-ok", str(ctx["conf"].get("status", "—")).replace("_", " "),
         "salto = lado da bolsa maior menos lado da bolsa menor (<code>09b_conferir_sinal.py</code>)"),
        (("Inferência alternativa (E5)", "pill-hist", "exploratório", "pós-resultado; não substitui o E3")
         if ctx.get("e5") else
         ("Inferência alternativa (E5)", "pill-pend", "ausente", "saídas <code>output/rdd_bolsa/E5_*</code> ausentes")),
        ("E4 — limites para a proporção preenchida", "pill-hist", "histórico",
         "exploratório, com escore parcial; superado pelo E3" if E4_EST.exists() else "ausente"),
        ("E1 e E2 — densidade e limites para a presença", "pill-hist", "histórico",
         "exploratórios, com escore parcial; superados pelo E3" if (E1_EST.exists() and E2_LIM.exists())
         else "ausente"),
    ]
    mo = ctx.get("mo") or {}

    def st_mo(nome, chave, ok_txt, detalhe):
        tem = chave in mo and mo[chave]
        return (nome, "pill-ok" if tem else "pill-pend", ok_txt if tem else "ausente", detalhe if tem else "saídas ausentes")

    itens += [
        st_mo("E6 — funil (P1 e famílias F0, F1, F2, F4)", "e6", "executado", "protocolo 40; P1 é hipótese primária"),
        st_mo("E9 — escolha revelada dos candidatos", "e9", "executado", "secundário e exploratório (§12)"),
        st_mo("E7 — DiRD no CNES (P2 e família F3)", "e7", "executado", "protocolo 40; P2 é hipótese primária"),
        st_mo("A4 reestimado com a base oficial", "fm", "executado", "antes = failure mode (auditoria 19)"),
        ("Síntese da rodada (E8)", "pill-ok" if mo.get("e8") else "pill-pend", "lida" if mo.get("e8") else "pendente",
         "<code>output/rdd_bolsa/E8_resumo.json</code>" + ("" if mo.get("e8") else " ainda não gravado")),
    ]
    stt = "".join(f'<tr><td>{a}</td><td><span class="pill {b}">{esc(c)}</span></td><td>{d}</td></tr>'
                  for a, b, c, d in itens)
    sumario = "".join(f"<li>{s}</li>" for s in [
        "Resumo em 1 página (E3)",
        "Resumo da rodada multi-outcome (hipóteses primárias primeiro)",
        "<strong>Parte I — RDD da bolsa com o escore completo</strong>",
        "1. A regra: IVS 2010 oficial, cortes 0,300 e 0,400",
        "2. RDD sharp com o escore completo (E3)",
        "3. Inferência alternativa (E5; exploratória, pós-resultado)",
        "4. Antes do escore completo: E1, E2 e E4 (exploratórios)",
        "5. Leitura e limites",
        "<strong>Parte II — rodada multi-outcome (protocolo 40)</strong>",
        "6. Protocolo 40: famílias, métodos, primárias e adendos",
        "7. Políticas nos mesmos cortes de IVS (auditoria 18)",
        "8. E6 — funil: atração, presença e seleção",
        "9. E9 — escolha revelada dos candidatos",
        "10. E7 — DiRD no CNES (oferta líquida)",
        "11. A4 reestimado com a base oficial (auditoria 19)",
        "12. Síntese (E8)",
        "Apêndice A — dados dos gráficos RD",
        "Apêndice B — proveniência das entradas",
    ])
    return f"""
<section class="capa">
  <div class="kicker">Programa Mais Médicos Especialistas · adicional de bolsa por faixa de IVS</div>
  <h1>{esc(TITULO)}</h1>
  <p class="lead">A bolsa anunciada é atribuída pelo IVS 2010 oficial do Ipea, com dois cortes. Este relatório
  reconstrói a regra, apresenta a RDD sharp com o escore completo (E3) e resume as análises exploratórias
  anteriores (parte I). A parte II traz a rodada multi-outcome do protocolo 40: funil (E6), escolha dos
  candidatos (E9), DiRD no CNES (E7), políticas nos mesmos cortes e o A4 corrigido. É a base para montar os
  slides: todo número e gráfico é lido de <code>output/</code> por script versionado.</p>
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


def legenda_salto(ctx, outcome: str) -> str:
    """Frase "como ler o salto", antes de cada tabela de resultados (pedido do autor, 18/10/2026)."""
    vf, fx = ctx["valor_faixa"], ctx["faixas"]
    passo = br_mil(vf[fx[1]] - vf[fx[0]])
    por_corte = "; ".join(f"em {br(c)}: lado de {br_mil(vf[fx[i + 1]])} menos lado de {br_mil(vf[fx[i]])}"
                          for i, c in enumerate(ctx["cortes"]))
    mais = {OUTCOME_FRAC: "mais preenchimento", OUTCOME_D: "mais presença de especialista"}.get(outcome, "mais outcome")
    return (f'<p class="legenda-salto"><strong>Como ler.</strong> Salto = valor no corte do lado com bolsa {passo} '
            f"maior (IVS acima do corte) menos valor do lado com bolsa menor ({por_corte}). Positivo = bolsa maior "
            f"associada a {mais}.</p>")


def termo(x: float, nd: int = 1) -> str:
    """Parcela de uma soma em p.p.: '+ 26,5' ou '− 0,7'."""
    s = pp(x, nd)
    return ("− " + s[1:]) if s.startswith("−") else ("+ " + s.lstrip("+"))


def decomposicao_txt(ind: dict, rotulos: bool = True) -> str:
    dec = ind["decomposicao"]
    r = (" (salto)", " (inclinação)", " (resíduo)") if rotulos else ("", "", "")
    return (f"{pp(ind['diferenca_medias_brutas'])} = {pp(dec['salto'])}{r[0]} "
            f"{termo(dec['inclinacao_dentro_da_janela'])}{r[1]} {termo(dec['residuo'])}{r[2]}")


def nota_sinal(ctx, pares, compacta: bool = False) -> str:
    """Nota curta: por que o salto local linear pode ter sinal diferente da diferenca de medias brutas."""
    itens, ex = [], None
    multi = len({p for p, _ in pares}) > 1
    for pop, outcome in pares:
        for c in ctx["cortes"]:
            cs = conf_espec(ctx, pop, outcome, c)
            ind = cs["independente"]
            rot = (f"{rotulo_pop(ctx, pop, curto=True).lower()}, " if multi else "") + br(c)
            itens.append(f"{rot}: {decomposicao_txt(ind, rotulos=not compacta)}")
            if ex is None and cs["sinal_salto_difere_da_diferenca_bruta"]:
                ex = (cs, ind)
    if ex:
        cs, ind = ex
        L0, L1 = ind["lado_bolsa_menor"], ind["lado_bolsa_maior"]
        exemplo = (f" Em {br(cs['corte'])}, a reta do lado de {br_mil(cs['bolsa_lado_menor'])} sobe "
                   f"{br(100 * L0['inclinacao_por_0_010_de_ivs'], 1)} p.p. a cada 0,010 de IVS e chega ao corte em "
                   f"{pct(L0['valor_da_reta_no_corte'])}; a do lado de {br_mil(cs['bolsa_lado_maior'])} começa em "
                   f"{pct(L1['valor_da_reta_no_corte'])}.")
        meio = (f" (IVS médio {br(L0['ivs_medio'])} abaixo e {br(L1['ivs_medio'])} acima de {br(cs['corte'])})")
    else:
        exemplo, meio = "", ""
    if compacta:
        oc = rotulo_outcome(ctx, pares[0][1], curto=True)
        oc = ("a " if oc.endswith("a") else "o ") + oc
        return (f'<p class="nota"><strong>Média bruta não é salto:</strong> as médias são tomadas em toda a janela de '
                f"±{br(ctx['h_principal'], 3)}, e {esc(oc)} sobe com o IVS dentro dela; o salto compara as retas no "
                f"próprio corte. Diferença bruta = salto + inclinação + resíduo (p.p.): {'; '.join(itens)}.</p>")
    return (f'<p class="nota"><strong>Por que o salto pode ter sinal diferente da diferença de médias brutas.</strong> '
            f"A média bruta de cada lado é tomada em toda a janela de ±{br(ctx['h_principal'], 3)}, cujo meio fica "
            f"longe do corte{meio}. Se o outcome muda com o IVS dentro da janela, as médias dos dois lados diferem "
            "mesmo sem salto nenhum. O salto compara as duas retas no próprio corte." + exemplo
            + f" Decomposição exata, em p.p. (diferença bruta = salto + inclinação dentro da janela + resíduo): "
              f"{'; '.join(itens)}.</p>")


def tabela_resultados(ctx, pares, titulo: str, compacta: bool = False, chave: str | None = None) -> str:
    """Resultados da janela principal com legenda antes, medias brutas, retas no corte e nota sobre o sinal.

    pares = [(populacao, outcome)], todos com o mesmo outcome (a legenda fala do outcome).
    """
    pr = principais(ctx)
    multi = len({p for p, _ in pares}) > 1
    linhas = []
    for pop, outcome in pares:
        g = pr[(pr["populacao"] == pop) & (pr["outcome"] == outcome)].sort_values("corte")
        for r in g.itertuples():
            cs = conf_espec(ctx, pop, outcome, r.corte)
            ind = cs["independente"]
            L0, L1 = ind["lado_bolsa_menor"], ind["lado_bolsa_maior"]
            lin = [esc(rotulo_pop(ctx, pop, curto=True))] if multi else []
            lin += [f"{br(r.corte)}<br><span class=\"muted\">{br_mil(cs['bolsa_lado_menor'])} → "
                    f"{br_mil(cs['bolsa_lado_maior'])}</span>",
                    f"{br_int(r.n_abaixo)} / {br_int(r.n_acima)}",
                    f"{pct(r.media_bruta_abaixo)} → {pct(r.media_bruta_acima)}",
                    pp(ind["diferenca_medias_brutas"]),
                    f"{pct(L0['valor_da_reta_no_corte'])} → {pct(L1['valor_da_reta_no_corte'])}",
                    f"<strong>{pp(r.tau)}</strong>", ic_pp(r.ic95_inf, r.ic95_sup), br_p(r.p_valor)]
            if not compacta:
                lin.append(br(MDE_FATOR * r.ep * 100, 0))
            linhas.append(lin)
    mu = '<span class="muted">'
    cab = [("Ciclo", "txt")] if multi else []
    cab += [(f"Corte<br>{mu}bolsa menor → maior</span>", "txt nowrap"),
            (f"Municípios<br>{mu}menor / maior</span>", "num"),
            (f"Média bruta na janela<br>{mu}menor → maior</span>", "num"),
            (f"Diferença bruta<br>{mu}p.p.</span>", "num"),
            (f"Retas no corte<br>{mu}menor → maior</span>", "num"),
            (f"<strong>Salto</strong><br>{mu}maior − menor, p.p.</span>", "num"),
            (f"IC 95%<br>{mu}p.p.</span>", "num"), ("p", "num")]
    if not compacta:
        cab.append((f"MDE (p.p.)<br>{mu}2,8 × EP</span>", "num"))
    outcome = pares[0][1]
    if compacta:
        rod = (nota_sinal(ctx, pares, compacta)
               + f'<div class="fonte">Fonte: <code>{esc(rel(E3_EST))}</code>; retas no corte e decomposição: '
                 f"<code>{esc(rel(CONF_SINAL))}</code>. Local linear, kernel triangular, "
                 f"h = {br(ctx['h_principal'], 3)}, EP HC1; detalhes na seção 2.</div>")
    else:
        rod = (nota_sinal(ctx, pares, compacta)
               + f'<div class="fonte">Fonte: <code>{esc(rel(E3_EST))}</code> ({origem_html(E3_EST)}); retas no corte e '
                 f"decomposição: <code>{esc(rel(CONF_SINAL))}</code> ({origem_html(CONF_SINAL)}). Local linear, "
                 f"kernel triangular, h = {br(ctx['h_principal'], 3)}, EP HC1 por município. Municípios = n com peso "
                 "positivo de cada lado. MDE = efeito mínimo detectável aproximado (80% de poder, 5% bicaudal), "
                 "calculado aqui como 2,8 × EP.</div>")
    return tabela(cab, linhas, classe="compacta resultados", titulo=titulo, rodape=rod,
                  legenda=legenda_salto(ctx, outcome), chave=chave)


def cientifico(x: float) -> str:
    """Numero pequeno em notacao cientifica com sobrescrito: 2,0 × 10⁻¹¹."""
    if not finito(x) or x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    sobre = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return f"{br(x / 10 ** e, 1)} × 10{str(e).translate(sobre)}"


def tabela_conferencia_sinal(ctx) -> str:
    """Resumo de E3_conferencia_sinal.json: o salto e bolsa maior menos bolsa menor."""
    conf = ctx["conf"]
    cf = {c["id"]: c for c in conf.get("conferencias") or []}
    d0 = (cf.get("C0_insumos") or {}).get("detalhe") or {}
    regra = (cf.get("C1_regra_e_lado") or {}).get("detalhe") or []
    trechos = ((cf.get("C2_convencao_no_codigo") or {}).get("detalhe") or {}).get("trechos") or {}

    def ok(chave):
        return ('<span class="pill pill-ok">ok</span>' if (cf.get(chave) or {}).get("ok")
                else '<span class="pill pill-pend">divergência</span>')

    janela = "; ".join(
        f"{rotulo_pop(ctx, r['populacao'], curto=True).lower()}, {br(r['corte'])}: "
        f"{br_int(r['janela_principal']['n_lado_menor'])} com {br_mil(r['bolsa_lado_menor_ivs_ate_o_corte'])} e "
        f"{br_int(r['janela_principal']['n_lado_maior'])} com {br_mil(r['bolsa_lado_maior_ivs_acima_do_corte'])}"
        for r in regra)
    vfe = d0.get("valor_por_faixa_edital") or {}
    edital = ", ".join(f"{esc(f.title())} {br_mil(v)}" for f, v in sorted(vfe.items(), key=lambda kv: kv[1]))
    linhas_cod = ", ".join(f"<code>{esc(v.get('texto', ''))}</code> (linha {esc(v.get('linha'))})"
                           for k, v in trechos.items() if k in ("tratamento", "salto"))
    c3 = (cf.get("C3_reestimacao_independente") or {}).get("detalhe") or {}
    c4 = (cf.get("C4_tratamento_lido_do_quadro") or {}).get("detalhe") or {}
    c5 = (cf.get("C5_erro_padrao") or {}).get("detalhe") or {}
    linhas = [
        ["Quadro de vagas × lado do corte",
         "Todo município com IVS acima do corte oferece a bolsa maior e todo município com IVS até o corte, a menor, "
         f"nos ciclos 1 e 2 (população inteira). Na janela principal: {esc(janela)}. Valores do edital (cláusula "
         f"11.1.4) iguais aos da matriz: {edital}.", ok("C1_regra_e_lado")],
        ["Convenção no código do E3",
         f"{linhas_cod} em <code>{esc(rel(E3_SCRIPT))}</code>: T = 1[s &gt; c] e salto = coeficiente de T, isto é, "
         "limite pela direita (bolsa maior) menos limite pela esquerda (bolsa menor).", ok("C2_convencao_no_codigo")],
        ["Reestimação independente",
         f"Duas retas ponderadas separadas, por fórmula fechada: intercepto do lado da bolsa maior menos intercepto do "
         f"lado da bolsa menor reproduz o salto do E3 nas {br_int(c3.get('especificacoes'))} especificações (maior "
         f"diferença {cientifico(c3.get('max_abs_diferenca'))}).", ok("C3_reestimacao_independente")],
        ["Bolsa do quadro no lugar de T",
         "Com (bolsa anunciada − bolsa do lado menor) / R$ 5 mil no lugar de T, o coeficiente é o mesmo (maior "
         f"diferença {cientifico(c4.get('max_abs_diferenca'))}): o salto é por +R$ 5 mil de bolsa.",
         ok("C4_tratamento_lido_do_quadro")],
        ["Erro-padrão", f"HC1 recalculado igual ao do E3 (maior diferença {cientifico(c5.get('max_abs_diferenca'))}).",
         ok("C5_erro_padrao")],
        ["Médias brutas × salto",
         "Médias brutas iguais às do E3; a diferença de médias brutas se decompõe exatamente em salto + inclinação "
         f"dentro da janela + resíduo (nota da {NUM.ref('tab_principal', 'tabela do resultado principal')}).",
         ok("C6_medias_brutas_e_salto")],
    ]
    rod = (f'<p class="nota">Resposta registrada: “{esc(conf.get("resposta", ""))}”</p>'
           + fonte_html(CONF_SINAL, grafico=False,
                        extra=f"Status <code>{esc(conf.get('status', '—'))}</code>; executado em "
                              f"{data_br(conf.get('data_execucao'))}"))
    return tabela([("Conferência", "txt nowrap"), ("O que foi verificado", "txt"), ("Resultado", "txt")], linhas,
                  classe="compacta", titulo="Conferência do sinal: o salto é bolsa maior menos bolsa menor",
                  rodape=rod, chave="tab_sinal")


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

    fr = pr[(pr["populacao"] == "P1") & (pr["outcome"] == OUTCOME_FRAC)]
    hipotese = (f"A hipótese é <em>maior bolsa, maior preenchimento</em>. Na proporção de células preenchidas na 1ª "
                f"chamada do ciclo 1, o salto (bolsa maior menos bolsa menor) é de {tau_de('P1', OUTCOME_FRAC)} "
                f"(local linear, h = {br(ctx['h_principal'], 3)}; efeito mínimo detectável de cerca de "
                f"{br(MDE_FATOR * fr['ep'].min() * 100, 0)} p.p.; sinal conferido na seção 2).")
    c = (f"<li><strong>Secundário:</strong> a presença de especialista do ciclo no município também não salta: "
         f"{tau_de('P1', OUTCOME_D)} no ciclo 1; {tau_de('P2', OUTCOME_D)} no ciclo 2.</li>")

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
         f"de covariáveis pré-programa (h = {br(ctx['h_principal'], 3)}; sem o próprio IVS, que é a running variable; "
         "os subíndices são componentes dele e pedem leitura com ressalva), "
         f"{br_int(len(sig))} de {br_int(ne['bal_n'])} testes têm p &lt; 0,05 (seriam {br(ALFA * ne['bal_n'], 1)} "
         f"por acaso).{foco_txt}</li>")

    dizer = (
        '<div class="dizer"><strong>Como dizer nos slides.</strong><ul>'
        "<li>“Estimativa local do efeito do anúncio de +R$ 5 mil, sob as premissas da RDD, para municípios do "
        "quadro com IVS perto dos cortes”; a conclusão acima, como está.</li>"
        "<li>Evitar: “a bolsa não funciona”, “efeito nulo”, “a bolsa não atrai”. Não é o efeito de participar do "
        "PMM-E nem do Agora Tem Especialistas.</li></ul></div>"
    )
    return ('<section class="resumo"><h2>Resumo em 1 página</h2>'
            f'<div class="conclusao"><strong>Conclusão.</strong> {hipotese} '
            f"<strong>{esc(frase_conclusao(ctx))}</strong> {esc(frase_e5_resumo(ctx))}</div>"
            f'<ul class="resumo-lista">{a}{b}{c}{d}</ul>'
            + tabela_resultados(ctx, [("P1", OUTCOME_FRAC)], compacta=True,
                                titulo="A hipótese: proporção de células preenchidas, ciclo 1")
            + dizer + "</section>")


def frase_conclusao(ctx) -> str:
    """Enquadramento da conclusao pedido pelo autor (18/10/2026), com os numeros lidos do E3."""
    fr = principais(ctx)
    fr = fr[(fr["populacao"] == "P1") & (fr["outcome"] == OUTCOME_FRAC)].sort_values("corte")
    vf, fx = ctx["valor_faixa"], ctx["faixas"]
    passo = br_mil(vf[fx[1]] - vf[fx[0]])
    if (fr["ic95_inf"] > 0).any() or (fr["ic95_sup"] < 0).any():
        return (f"Atenção: algum IC 95% do preenchimento exclui zero; o enquadramento “sem evidência” não se aplica "
                f"(ver {rel(E3_EST)}).")
    lim = [f"{pp(r.ic95_sup, 0)} p.p. no corte {br(r.corte)}" if i == 0 else f"{pp(r.ic95_sup, 0)} p.p. no {br(r.corte)}"
           for i, r in enumerate(fr.itertuples())]
    return (f"Não encontramos evidência estatística de que +{passo} aumente o preenchimento perto dos cortes. Os dados "
            f"também não permitem descartar efeitos grandes: até cerca de {' e '.join(lim)} (limites superiores do "
            "IC 95%). O resultado é inconclusivo, e não evidência de que a bolsa não funciona.")


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
        chave="tab_escore",
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

    # Figuras: bolsa contra o IVS, um ponto por municipio (ciclo 1)
    p1 = populacao(base, "P1")
    p1 = p1[p1["s_mil"].notna() & p1["s_mil_local"].notna()].copy()
    err_of = (p1["faixa_oficial"] != p1["faixa_anunciada"]).to_numpy()
    err_lo = (p1["faixa_local"] != p1["faixa_anunciada"]).to_numpy()
    tudo = np.concatenate([p1["ivs"].to_numpy(float), p1["ivs_local"].to_numpy(float)])
    x0, x1 = math.floor(tudo.min() / 0.05) * 0.05, math.ceil(tudo.max() / 0.05) * 0.05
    o.append(figura(
        "Valor mensal anunciado da bolsa contra o IVS 2010 oficial do município, ciclo 1",
        fig_regra_pontos(p1["ivs"], p1["faixa_anunciada"], err_of, "IVS 2010 oficial do município (Ipea)",
                         cortes, faixas, vf, x0, x1, ids=p1["co_ibge"]),
        fonte_html(MATRIZ, IVS_OFICIAL, extra=f"Quadro {QUADRO_PRIMEIRO_ESTAGIO}"),
        sub=(f"{br_int(len(p1))} municípios do quadro da 1ª chamada do ciclo 1; {br_int(int(err_of.sum()))} fora da "
             "regra. Cada ponto é um município, na altura exata da bolsa que ele oferece, sem deslocamento; onde há "
             "muitos municípios, os pontos se sobrepõem e a cor fica mais forte. A cor repete o IVS do eixo "
             "horizontal (verde = menor, vermelho = maior). Forma escolhida pelo autor: variante A de "
             "<code>output/rdd_bolsa/galeria_figura_regra.pdf</code>."),
        chave="fig_regra",
    ))
    o.append(figura(
        "A mesma figura com o arquivo antigo do repositório no lugar do IVS oficial",
        fig_regra_pontos(p1["ivs_local"], p1["faixa_anunciada"], err_lo,
                         "IVS do arquivo antigo (data/ivs_ipea_2010_municipios.csv)", cortes, faixas, vf, x0, x1,
                         ids=p1["co_ibge"], destacar=True,
                         rotulo_errado=f"contorno preto: faixa do lado errado do corte pelo arquivo antigo "
                                       f"({br_int(int(err_lo.sum()))} municípios)"),
        fonte_html(MATRIZ, IVS_LOCAL, extra=f"Quadro {QUADRO_PRIMEIRO_ESTAGIO}"),
        sub=(f"Mesmos {br_int(len(p1))} municípios e mesma bolsa: muda só a posição no eixo (e a cor, que segue o "
             f"eixo). Com o arquivo antigo, {br_int(int(err_lo.sum()))} municípios ficam do lado errado de um corte "
             "(contorno preto) e as faixas se sobrepõem. Era isso que fazia a regra parecer inexistente."),
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

    pr = ne["pr"]
    fr = pr[(pr["populacao"] == "P1") & (pr["outcome"] == OUTCOME_FRAC)]
    h_txt = br(ctx["h_principal"], 3)
    o.append("<h3>A hipótese: proporção de células preenchidas (ciclo 1)</h3>")
    o.append(
        "<p>A hipótese da banca é <em>maior remuneração, maior preenchimento</em>. A forma operacional é a proporção "
        "de células estabelecimento–curso do município com alguém confirmado ou homologado na 1ª chamada do ciclo 1. "
        "No corte, a bolsa anunciada sobe R$ 5 mil e o IVS, que mede o custo do lugar, varia continuamente.</p>")
    o.append(tabela_resultados(ctx, [("P1", OUTCOME_FRAC)], chave="tab_principal",
                               titulo="Resultado principal: proporção de células preenchidas, ciclo 1"))

    paineis = ctx["paineis_rd"]
    fonte_rd = fonte_html(ESCORE, E4_PROP, ATIVOS_ZIP, E3_EST, CONF_SINAL,
                          extra=(f"Salto e EP de cada reta conferidos contra <code>{esc(rel(E3_EST))}</code>; valores "
                                 f"das retas no corte, contra <code>{esc(rel(CONF_SINAL))}</code>; médias por bin no "
                                 "Apêndice A"))
    sub_rd = (f"Pontos: média dos municípios por intervalo de 0,010 do IVS (área proporcional ao número de "
              f"municípios); em cinza, fora da janela de ±{h_txt}, só como contexto. Retas locais lineares com IC 95% "
              "pontual (HC1). No corte, o traço preto liga as duas retas e os números são o valor de cada uma ali: "
              "salto = direita (bolsa maior) menos esquerda (bolsa menor).")
    o.append(figura("Gráfico RD: proporção de células preenchidas na 1ª chamada do ciclo 1, em torno dos dois cortes",
                    fig_rd_local(ctx, paineis, [("P1", OUTCOME_FRAC)]), fonte_rd, sub=sub_rd, chave="fig_rd_frac"))

    o.append(
        "<p>" + maiuscula("; ".join(f"em {br(r.corte)}, {pp(r.tau)} p.p. (IC 95% {ic_pp(r.ic95_inf, r.ic95_sup)}; "
                          f"p = {br_p(r.p_valor)})" for r in fr.itertuples()))
        + f". Nenhum dos dois saltos é distinguível de zero. <strong>{esc(frase_conclusao(ctx))}</strong></p>")
    opostos: dict[bool, list[str]] = {}
    for r in fr.itertuples():
        cs = conf_espec(ctx, "P1", OUTCOME_FRAC, r.corte)
        if cs["sinal_salto_difere_da_diferenca_bruta"]:
            opostos.setdefault(cs["independente"]["diferenca_medias_brutas"] > 0, []).append(br(r.corte))
    if opostos:
        casos = "; ".join(
            f"em {' e '.join(cs_)}, a média bruta do lado de cima é {'maior' if cima else 'menor'}, mas o salto é "
            f"{'negativo' if cima else 'positivo'}" for cima, cs_ in opostos.items())
        o.append(
            f"<p>{maiuscula(casos)}. A nota da {NUM.ref('tab_principal')} e a {NUM.ref('fig_rd_frac')} mostram de onde "
            "vem a diferença: as médias brutas ficam no meio de cada lado da janela, e o salto compara as duas retas no "
            f"próprio corte. A {NUM.proxima('tab')} confere, no código e nos dados, que o salto é mesmo o lado da bolsa "
            "maior menos o da menor.</p>")
    fonte_gl = fonte_html(ESCORE, E4_PROP, ATIVOS_ZIP,
                          extra="Polinômios ajustados aqui, só para descrição; não entram em nenhuma estimativa")
    sub_gl = (f"Descritivo. Cada ponto é a média dos municípios num intervalo de 0,020 do IVS (área proporcional ao "
              f"número de municípios); 0,300 e 0,400 são bordas de bin. As curvas são polinômios de grau {GRAU_GLOBAL} "
              "ajustados por MQO aos municípios de cada faixa de bolsa, de um corte ao outro: servem para ver o padrão "
              f"em todo o suporte e não são a estimativa da RDD. Faixas claras: janelas de ±{h_txt} do E3.")
    o.append(tabela_conferencia_sinal(ctx))
    o.append(figura("Visão global: proporção de células preenchidas em todo o suporte do IVS, ciclo 1",
                    fig_rd_global(ctx, ctx["globais"], [("P1", OUTCOME_FRAC)]), fonte_gl, sub=sub_gl,
                    chave="fig_gl_frac"))

    o.append("<h3>Resultado secundário: presença de especialista</h3>")
    o.append(
        "<p>A presença mede outra coisa: se o município tem especialista do ciclo ativo na relação nominal de "
        f"{esc(data_relacao_nominal(prot))}, isto é, se a atração se manteve meses depois. É o único outcome "
        "disponível para o ciclo 2, porque o funil de confirmações e homologações por célula só foi reconciliado e "
        "auditado para o ciclo 1. Por isso o ciclo 2 entra como replicação desse outcome secundário, e não da "
        "hipótese.</p>")
    o.append(tabela_resultados(ctx, [("P1", OUTCOME_D), ("P2", OUTCOME_D)], chave="tab_secundario",
                               titulo="Resultado secundário: presença de especialista, ciclos 1 e 2"))
    o.append(figura("Gráfico RD: presença de especialista do ciclo no município, ciclos 1 e 2",
                    fig_rd_local(ctx, paineis, [("P1", OUTCOME_D), ("P2", OUTCOME_D)]), fonte_rd, sub=sub_rd,
                    chave="fig_rd_pres"))
    o.append(figura("Visão global: presença de especialista em todo o suporte do IVS, ciclos 1 e 2",
                    fig_rd_global(ctx, ctx["globais"], [("P1", OUTCOME_D), ("P2", OUTCOME_D)]), fonte_gl,
                    sub=sub_gl))
    o.append(
        f'<p class="nota">O protocolo também previu duas janelas de sensibilidade (h = 0,030 e 0,080). Elas não '
        f"mudam a leitura (menor p entre as {ne['n_espec']} estimações: {br_p(ne['p_min'])}) e estão em "
        f"<code>{esc(rel(E3_EST))}</code>. Especificações alternativas, exploratórias e pós-resultado, estão na "
        "seção 3.</p>")

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
        legenda=('<p class="legenda-salto"><strong>Como ler.</strong> ρ = densidade de municípios no corte do lado com '
                 "bolsa R$ 5 mil maior (IVS acima do corte) dividida pela do lado com bolsa menor. ρ = 1: sem salto; "
                 "ρ &gt; 1: mais municípios logo acima do corte.</p>"),
        rodape=(f'<p class="nota">ρ = razão das densidades laterais (acima / abaixo), Poisson log-linear em mass '
                f"points de 0,001; ρ = 1 é ausência de salto. {'Todos os intervalos contêm 1' if ne['dens_todos_contem_1'] else 'Há intervalos que excluem 1'}: "
                "não há sinal de manipulação do IVS nem de que o corte tenha mudado quais municípios entraram no quadro. "
                "* janela principal.</p>" + fonte_html(E3_DIAG, grafico=False)),
    ))
    o.append(figura(
        "Densidade do IVS em torno de cada corte: municípios por intervalo de 0,005",
        fig_densidade(ctx, ctx["densidade"]),
        fonte_html(ESCORE, MATRIZ, E3_DIAG, extra=("Contagem esperada refeita aqui com o ajuste do E3; razão de "
                                                   f"densidades conferida contra <code>{esc(rel(E3_DIAG))}</code>")),
        sub=(f"Barras: municípios do quadro por intervalo de 0,005 do IVS (o corte cai no bin de baixo); azul dentro da "
             f"janela de ±{h_txt}, cinza fora. Linhas: contagem esperada por bin no ajuste log-linear do E3, feito em "
             "mass points de 0,001 de cada lado do corte; ρ é a razão entre as duas linhas no corte. Sem outcome."),
        chave="fig_densidade"))

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
        legenda=('<p class="legenda-salto"><strong>Como ler.</strong> Salto = valor da covariável no corte do lado com '
                 "bolsa R$ 5 mil maior (IVS acima do corte) menos valor do lado com bolsa menor, na unidade da "
                 "covariável. Como as covariáveis são anteriores ao programa, o esperado é zero.</p>"),
        rodape=(f'<p class="nota">‡ p &lt; 0,05. {br_int(len(ne["bal_sig"]))} de {br_int(ne["bal_n"])} testes '
                f"(seriam {br(ALFA * ne['bal_n'], 1)} por acaso). Mesmo estimador do E3 (local linear, kernel triangular, "
                f"HC1). Nas janelas de sensibilidade, p &lt; 0,05 em: {esc(sens_txt) or 'nenhum'}. "
                f"<strong>Nota:</strong> {nota_running_balanco(ctx)} A linha <code>{COVARIAVEL_RUNNING}</code> do "
                "arquivo de diagnósticos foi omitida desta tabela e da figura: seu “salto” é zero por construção "
                f"(|salto| máximo registrado: {cientifico(run['tau'].abs().max()) if len(run) else '—'})"
                + (", e o E3 a registra sem teste (EP, IC e p vazios)." if len(run) and run["p_valor"].isna().all()
                   else ", e os p-valores dela são ruído numérico, não desequilíbrio.") + "</p>"
                + fonte_html(E3_DIAG, grafico=False,
                             extra="Covariáveis da base oficial do Ipea (a08) e da tipologia territorial, registradas em "
                                   f"<code>{esc(rel(E3_STATUS))}</code>")),
    ))
    bal_dp, falha_bal = ctx["balanco_dp"]
    if bal_dp is not None and len(bal_dp):
        n_sig = int((bal_dp["p_valor"] < ALFA).sum())
        o.append(figura(
            "Balanço de covariáveis pré-programa: salto no corte em desvios-padrão, com IC 95%",
            fig_balanco(ctx, bal_dp),
            fonte_html(E3_DIAG, IVS_OFICIAL, TIPOLOGIA,
                       extra=("Desvios-padrão calculados aqui, entre todos os municípios de cada população, com as "
                              "covariáveis lidas pela função do E3")),
            sub=(f"Para cada covariável, o salto no corte (lado da bolsa maior menos lado da bolsa menor; mesmo estimador "
                 f"do E3, h = {h_txt}) dividido pelo desvio-padrão da covariável na população do ciclo, com IC 95%. "
                 f"Laranja: p &lt; 0,05 ({br_int(n_sig)} de {br_int(len(bal_dp))}; seriam "
                 f"{br(ALFA * len(bal_dp), 1)} por acaso). Os números estão na tabela acima. "
                 + esc(nota_running_balanco(ctx))
                 + (f" Covariáveis não lidas: {esc(falha_bal)}." if falha_bal else "")),
            chave="fig_balanco"))
    else:
        o.append(caixa_ausente(f"Figura de balanço não gerada ({falha_bal or 'sem covariáveis'})", [IVS_OFICIAL, TIPOLOGIA]))
    o.append(f"<p>{ctx['nota_suporte']}</p>")
    o.append("</section>")
    return "".join(o)


# ---------------------------------------------------------------------------
# Secao 3: inferencia alternativa (E5), EXPLORATORIA e pos-resultado. So le output/rdd_bolsa/E5_*.
# ---------------------------------------------------------------------------


def carregar_e5(ctx) -> dict | None:
    """Le as saidas do E5 (nada e recalculado) e confere que o S0 do E5 e o E3 atual."""
    if not all(p.exists() for p in E5_ARQS):
        return None
    esp = pd.read_csv(E5_ESPEC, dtype={"corte": str})
    esp["corte_num"] = pd.to_numeric(esp["corte"], errors="coerce")
    for col in [c for c in esp.columns if c.startswith(("descarta_", "equivalencia_"))]:
        esp[col] = esp[col].astype(str).str.lower().eq("true")
    res = ler_json(E5_RESUMO) or {}
    mapa = {"Y1": OUTCOME_FRAC, "D1": OUTCOME_D, "D2": OUTCOME_D}
    diverg = []
    for r in esp[esp["especificacao"] == "S0"].itertuples():
        if r.outcome in mapa and finito(r.corte_num):
            e = linha_e3(ctx, r.populacao, mapa[r.outcome], float(r.corte_num))
            if abs(r.tau - e["tau"]) > TOL_TAU or abs(r.ep - e["ep"]) > TOL_TAU:
                diverg.append(f"{r.outcome} em {br(r.corte_num)}")
    return {"esp": esp, "dec": pd.read_csv(E5_DECOMP), "lados": pd.read_csv(E5_LADOS),
            "lr": pd.read_csv(E5_LR_SENS), "res": res, "diverg": diverg}


def ordem_e5(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["_o"] = [ORDEM_E5.index(e) if e in ORDEM_E5 else len(ORDEM_E5) for e in d["especificacao"]]
    d["_c"] = d["corte_num"].fillna(9.0)
    return d.sort_values(["_o", "_c"], kind="stable")


def corte_e5(r) -> str:
    """'0,300'; '0,300 (±0,020)' na local randomization; '0,300 + 0,400' com cortes empilhados."""
    if not finito(r.corte_num):
        return " + ".join(br(float(c.strip().replace(",", "."))) for c in str(r.corte).split("+"))
    txt = br(float(r.corte_num))
    m = re.match(r"\+-\s*([\d.]+)", str(r.janela or ""))
    if r.especificacao == "D" and m:
        txt += f" (±{br(float(m.group(1)))})"
    return txt


def n_e5(r) -> str:
    n = f"{br_int(r.n_abaixo)} / {br_int(r.n_acima)}"
    if str(r.unidade).startswith("celula") and finito(r.n_obs):
        n += f' <span class="muted">({br_int(r.n_obs)} células)</span>'
    elif str(r.outcome) == "D1+D2" and finito(r.n_obs):
        n += f' <span class="muted">({br_int(r.n_obs)} linhas)</span>'
    return n


def rotulo_e5(codigo: str, vies: bool = True) -> str:
    rot = esc(ESPEC_E5.get(codigo, codigo))
    if codigo == "S0":
        return f"<strong>{rot}</strong>"
    if codigo == "A" and vies:
        return f'{rot} <span class="muted">({VIES_A})</span>'
    return rot


def selo_e5() -> str:
    return ' <span class="pill pill-hist">exploratório</span>'


def margem(d: int) -> str:
    return f"{d:03d}"


def y1_e5(e5) -> pd.DataFrame:
    return e5["esp"][e5["esp"]["outcome"] == "Y1"]


def s0_e5(e5, corte: float) -> pd.Series:
    y = y1_e5(e5)
    return y[(y["especificacao"] == "S0") & np.isclose(y["corte_num"], corte)].iloc[0]


def tabela_decomposicao_e5(ctx, e5) -> str:
    dec, lados = e5["dec"], e5["lados"]
    js = {round(float(d["corte"]), 3): d for d in (e5["res"].get("decomposicao_ic_y1") or [])}
    cortes = sorted(float(c) for c in dec["corte"].unique())

    def comp(c, nome):
        return dec[np.isclose(dec["corte"], c) & (dec["componente"] == nome)].iloc[0]

    def lado(c, nome):
        return lados[np.isclose(lados["corte"], c) & (lados["lado"] == nome)].iloc[0]

    def dp(c):
        d = js.get(round(c, 3))
        return br(d["dp_y_combinado"], 3) if d else "—"

    ll, lc, dm = "LL_triangular_principal", "LC_triangular", "DM_simples"
    linhas = [
        ["Municípios abaixo / acima"] + [f"{br_int(comp(c, dm).n_abaixo)} / {br_int(comp(c, dm).n_acima)}" for c in cortes],
        ["n efetivo com o kernel triangular (abaixo / acima)"]
        + [f"{br_int(lado(c, 'abaixo').n_efetivo_kish_triangular)} / {br_int(lado(c, 'acima').n_efetivo_kish_triangular)}"
           for c in cortes],
        ["Desvio-padrão de Y1 (combinado)"] + [dp(c) for c in cortes],
        ["Municípios com uma única célula (abaixo / acima)"]
        + [f"{pct(lado(c, 'abaixo').share_municipios_1_celula, 0)} / {pct(lado(c, 'acima').share_municipios_1_celula, 0)}"
           for c in cortes],
        ["(1) EP da diferença de médias simples"] + [br(comp(c, dm).ep, 3) for c in cortes],
        ["(2) × kernel triangular (local constante)"]
        + [f"× {br(comp(c, lc).razao_ep_vs_dm_simples, 2)} → {br(comp(c, lc).ep, 3)}" for c in cortes],
        ["(3) × inclinações (local linear)"]
        + [f"× {br(comp(c, ll).ep / comp(c, lc).ep, 2)} → <strong>{br(comp(c, ll).ep, 3)}</strong>" for c in cortes],
        ["Fator total (3) ÷ (1)"] + [f"<strong>× {br(comp(c, ll).razao_ep_vs_dm_simples, 2)}</strong>" for c in cortes],
        ["Referência teórica, desenho uniforme"] + [f"× {br(comp(c, ll).razao_teorica_desenho_uniforme, 2)}"
                                                    for c in cortes],
        ["MDE do principal (2,8 × EP)"] + [f"<strong>{br(100 * comp(c, ll).mde_80, 1)} p.p.</strong>" for c in cortes],
    ]
    return tabela(
        [("Preenchimento (Y1), janela h = 0,050, mesma amostra do principal", "txt")]
        + [(f"Corte {br(c)}", "num") for c in cortes], linhas, classe="compacta",
        titulo="Por que o IC é largo: decomposição do erro-padrão do salto" + selo_e5(), chave="tab_e5_decomp",
        rodape=('<p class="nota">EP = erro-padrão (HC1, por município), em proporção. Cada linha multiplica a anterior: '
                "(1) diferença de médias simples na janela; (2) com os pesos do kernel triangular, sem inclinação "
                "(local constante); (3) com as inclinações de cada lado (local linear, o principal). A referência "
                "teórica é o fator esperado se os municípios fossem uniformes na janela, com variância constante.</p>"
                + fonte_html(E5_DECOMP, E5_LADOS, E5_RESUMO, grafico=False)))


def itens_largura_e5(ctx, e5) -> str:
    """Os tres fatores que multiplicam o EP (doc 39, secao 1), com os numeros lidos do E5."""
    dec, lados = e5["dec"], e5["lados"]
    y = y1_e5(e5)
    c0 = ctx["cortes"][0]
    ll = dec[dec["componente"] == "LL_triangular_principal"]
    lc = dec[dec["componente"] == "LC_triangular"]
    dm = dec[dec["componente"] == "DM_simples"]
    e1 = y[(y["especificacao"] == "E1") & np.isclose(y["corte_num"], c0)]
    cel = (f" ({br_int(e1['n_obs'].iloc[0])} células em {br_int(e1['n_clusters'].iloc[0])} municípios na janela de "
           f"{br(c0)}, {br(e1['n_obs'].iloc[0] / e1['n_clusters'].iloc[0], 1)} por município)" if len(e1) else "")
    sh = lados["share_municipios_1_celula"]
    nef = lados["n_efetivo_kish_triangular"] / lados["n"]
    fat_incl = (ll.set_index("corte")["ep"] / lc.set_index("corte")["ep"])
    dm0 = dm[np.isclose(dm["corte"], c0)].iloc[0]
    ll0 = ll[np.isclose(ll["corte"], c0)].iloc[0]
    n_lado = (dm0["n_abaixo"] + dm0["n_acima"]) / 2
    dp0 = next((d["dp_y_combinado"] for d in (e5["res"].get("decomposicao_ic_y1") or [])
                if math.isclose(float(d["corte"]), c0)), np.nan)
    return (
        '<ol class="leitura">'
        f"<li><strong>Ruído do outcome e n pequeno.</strong> Y1 é uma fração de poucas células{cel}. Entre "
        f"{pct(sh.min(), 0)} e {pct(sh.max(), 0)} dos municípios de cada lado têm uma única célula, e para eles Y1 só "
        f"pode ser 0 ou 1. Com desvio-padrão de {br(dp0, 2)} e cerca de {br_int(n_lado)} municípios por lado, até uma "
        f"diferença de médias simples teria EP de {br(dm0['ep'], 3)}, isto é, IC de ±{br(100 * Z_975 * dm0['ep'], 0)} "
        "p.p.</li>"
        f"<li><strong>Kernel triangular.</strong> Dá menos peso aos municípios longe do corte: o n efetivo cai para "
        f"{pct(nef.min(), 0)} a {pct(nef.max(), 0)} do n, o que multiplica o EP por {br(lc['razao_ep_vs_dm_simples'].min(), 2)}"
        f" a {br(lc['razao_ep_vs_dm_simples'].max(), 2)}.</li>"
        f"<li><strong>Extrapolação até o corte.</strong> O local linear estima o valor de cada reta exatamente na borda "
        f"dos dados, onde a inclinação estimada pesa mais. É o fator dominante: × {br(fat_incl.min(), 1)} a "
        f"× {br(fat_incl.max(), 1)}. Em {br(c0)} o fator total ({br(ll0['razao_ep_vs_dm_simples'], 2)}) supera a "
        f"referência ({br(ll0['razao_teorica_desenho_uniforme'], 2)}), que supõe municípios uniformes na janela e "
        "variância constante.</li></ol>")


def tabela_estimadores_e5(ctx, e5) -> str:
    dec = e5["dec"]
    cortes = sorted(float(c) for c in dec["corte"].unique())
    nomes = [("DM_simples", "Diferença de médias simples"), ("LC_triangular", "Local constante triangular (= A)"),
             ("LL_uniforme", "Local linear, kernel uniforme"),
             ("LL_triangular_principal", "<strong>Local linear triangular (= principal)</strong>")]
    linhas = []
    for comp, rot in nomes:
        lin = [rot]
        for c in cortes:
            r = dec[np.isclose(dec["corte"], c) & (dec["componente"] == comp)]
            if len(r) != 1:
                lin.append("—")
                continue
            r = r.iloc[0]
            lin.append(f"{pp(r.tau)} {ic_pp(r.ic95_inf, r.ic95_sup)} <span class=\"muted\">p = {br_p(r.p_valor)}</span>")
        linhas.append(lin)
    dm0 = dec[np.isclose(dec["corte"], cortes[0]) & (dec["componente"] == "DM_simples")].iloc[0]
    return tabela(
        [("Estimador (mesma amostra)", "txt")] + [(f"Corte {br(c)}: salto (p.p.) [IC 95%]", "num") for c in cortes],
        linhas, classe="compacta", titulo="Quatro estimadores do salto na mesma amostra" + selo_e5(),
        legenda=legenda_salto(ctx, OUTCOME_FRAC),
        rodape=(f'<p class="nota">A diferença de médias simples em {br(cortes[0])} ({pp(dm0["tau"])} p.p.) é a '
                "comparação bruta das médias. Não estima o salto, porque ignora o gradiente de Y1 no IVS dentro da "
                f"janela (nota da {NUM.ref('tab_principal')}).</p>" + fonte_html(E5_DECOMP, grafico=False)))


def fig_forest_e5(ctx, e5) -> str:
    """Forest plot das especificacoes do preenchimento (Y1): um painel por corte e um para os cortes empilhados."""
    y = y1_e5(e5)
    cortes = ctx["cortes"]
    vf, fx = ctx["valor_faixa"], ctx["faixas"]
    por_corte = {c: ordem_e5(y[np.isclose(y["corte_num"], c)]) for c in cortes}
    emp = ordem_e5(y[y["corte_num"].isna()])
    codigos = [e for e in ORDEM_E5 if any(e in set(d["especificacao"]) for d in por_corte.values())]
    vals = np.concatenate([y["ic95_inf"].to_numpy(float), y["ic95_sup"].to_numpy(float)]) * 100
    lo = math.floor(np.nanmin(vals) / 10) * 10
    hi = max(30, math.ceil(np.nanmax(vals) / 10) * 10)
    W = 680
    lab_w, gapx, mr = 206, 22, 12
    pw = (W - lab_w - gapx - mr) / 2
    RH = 21
    leg_h = 26
    cab_h = 30
    top = leg_h + cab_h
    base = top + len(codigos) * RH
    emp_top = base + 46
    emp_base = emp_top + 22 + max(len(emp), 1) * RH
    H = int(emp_base + 46)
    o = [svg_abrir(W, H, "Forest plot das especificações exploratórias do preenchimento, por corte")]
    o.append(legenda_svg([("ponto", COR["s1"], "S0: principal do protocolo"),
                          ("ponto", COR["ink2"], "alternativas exploratórias"),
                          ("vazio", COR["muted"], f"A: {VIES_A}"),
                          ("tracejada", COR["ink2"], "+10 e +20 p.p.")], 6, 14, size=9.5))

    def painel(left: float, ptop: float, pbase: float, df: pd.DataFrame, linhas: list[str], rotulos: bool) -> None:
        X = Linear(lo, hi, left, left + pw)
        for t in range(lo, hi + 1, 10):
            o.append(l_svg(X(t), ptop, X(t), pbase, COR["grid"]))
        for t in (10, 20):
            if lo < t < hi:
                o.append(l_svg(X(t), ptop - 4, X(t), pbase, COR["ink2"], 1, extra='stroke-dasharray="4 3"'))
                o.append(t_svg(X(t), ptop - 7, f"+{t}", anchor="middle", size=8.5, cor=COR["ink2"]))
        o.append(l_svg(X(0), ptop - 4, X(0), pbase, COR["ink"], 1.2))
        o.append(l_svg(left, pbase, left + pw, pbase, COR["axis"]))
        for t in range(lo, hi + 1, 10):
            if t % 20 == 0:
                o.append(l_svg(X(t), pbase, X(t), pbase + 4, COR["axis"]))
                o.append(t_svg(X(t), pbase + 15, sinal(t, 0), anchor="middle", size=9))
        for i, cod in enumerate(linhas):
            yy = ptop + (i + 0.5) * RH
            r = df[df["especificacao"] == cod]
            if not len(r):
                continue
            r = r.iloc[0]
            a, z = X(max(r.ic95_inf * 100, lo)), X(min(r.ic95_sup * 100, hi))
            tt = (f"{ESPEC_E5.get(cod, cod)}, corte {corte_e5(r)}: {pp(r.tau)} p.p. {ic_pp(r.ic95_inf, r.ic95_sup)}, "
                  f"p = {br_p(r.p_valor)}")
            if cod == "S0":
                o.append(l_svg(a, yy, z, yy, COR["s1"], 2.6, extra='stroke-linecap="round"'))
                o.append(ponto(X(r.tau * 100), yy, COR["s1"], r=4.8, titulo=tt, anel=1.5))
            elif cod == "A":
                o.append(l_svg(a, yy, z, yy, COR["muted"], 2, extra='stroke-dasharray="3 2"'))
                o.append(f'<circle cx="{f2(X(r.tau * 100))}" cy="{f2(yy)}" r="3.9" fill="{COR["surface"]}" '
                         f'stroke="{COR["muted"]}" stroke-width="1.7"><title>{esc(tt)}</title></circle>')
            else:
                o.append(l_svg(a, yy, z, yy, COR["ink2"], 2, extra='stroke-linecap="round"'))
                o.append(ponto(X(r.tau * 100), yy, COR["ink2"], r=3.9, titulo=tt, anel=1.2))

    def rotulos(ptop: float, linhas: list[str]) -> None:
        for i, cod in enumerate(linhas):
            yy = ptop + (i + 0.5) * RH
            rot = ESPEC_E5.get(cod, cod)
            if cod == "A":
                o.append(t_svg(lab_w - 10, yy - 1.5, rot, anchor="end", size=9.3, cor=COR["ink2"]))
                o.append(t_svg(lab_w - 10, yy + 8, VIES_A, anchor="end", size=8.2, cor=COR["ink2"],
                               extra='font-style="italic"'))
            else:
                o.append(t_svg(lab_w - 10, yy + 3.5, rot, anchor="end", size=9.3,
                               cor=COR["ink"] if cod == "S0" else COR["ink2"], peso=650 if cod == "S0" else None))

    if "S0" in codigos:  # destaque da linha do principal
        i = codigos.index("S0")
        o.append(f'<rect x="4" y="{f2(top + i * RH)}" width="{f2(W - mr - 4)}" height="{RH}" fill="{COR["wash"]}"/>')
    rotulos(top, codigos)
    for ci, c in enumerate(cortes):
        left = lab_w + ci * (pw + gapx)
        o.append(t_svg(left + pw / 2, leg_h + 12, f"Corte {br(c)}: bolsa {br_mil(vf[fx[ci]])} → {br_mil(vf[fx[ci + 1]])}",
                       anchor="middle", cor=COR["ink"], peso=600, size=10))
        painel(left, top, base, por_corte[c], codigos, ci == 0)
    if len(emp):
        cods_emp = list(emp["especificacao"])
        o.append(t_svg(6, emp_top - 8, f"Cortes empilhados ({' + '.join(br(c) for c in cortes)}): um salto comum",
                       cor=COR["ink"], peso=600, size=10))
        rotulos(emp_top + 14, cods_emp)
        painel(lab_w, emp_top + 14, emp_top + 14 + len(cods_emp) * RH, emp, cods_emp, True)
        nx = lab_w + pw + gapx
        o.append(t_svg(nx, emp_top + 22, "Estimando: média ponderada dos dois saltos.", size=9, cor=COR["ink2"]))
        o.append(t_svg(nx, emp_top + 35, "Se os dois forem diferentes, não descreve", size=9, cor=COR["ink2"]))
        o.append(t_svg(nx, emp_top + 47, "nenhum deles.", size=9, cor=COR["ink2"]))
    o.append(t_svg(lab_w + (W - lab_w - mr) / 2, H - 6, "Salto (p.p.) e IC 95%; D: IC por permutação", anchor="middle",
                   size=9.5))
    o.append("</svg>")
    return "".join(o)


def tabela_y1_e5(ctx, e5) -> str:
    linhas = []
    for r in ordem_e5(y1_e5(e5)).itertuples():
        lin = [rotulo_e5(r.especificacao), corte_e5(r), f"<strong>{pp(r.tau)}</strong>" if r.especificacao == "S0"
               else pp(r.tau), ic_pp(r.ic95_inf, r.ic95_sup), br_p(r.p_valor), n_e5(r), br(r.ep, 3),
               br(100 * r.mde_80, 1)]
        linhas.append(lin)
    return tabela(
        [("Especificação", "txt"), ("Corte", "txt nowrap"), ("Salto (p.p.)", "num"), ("IC 95% (p.p.)", "num"),
         ("p", "num"), ("Municípios abaixo / acima", "num"), ("EP", "num"), ("MDE (p.p.)", "num")], linhas,
        classe="compacta", titulo="Todas as especificações do preenchimento (Y1), ciclo 1" + selo_e5(),
        legenda=legenda_salto(ctx, OUTCOME_FRAC), chave="tab_e5_y1",
        rodape=('<p class="nota">IC 95% pela normal, com EP HC1 por município (E1 e E2: EP agrupado por município); em D, '
                "p de Fisher com 10.000 permutações, IC por inversão sob efeito constante e EP = desvio-padrão da "
                "distribuição de permutação. MDE = 2,8 × EP. S0 reproduz o E3. Todas as especificações calculadas estão "
                "aqui, qualquer que seja o resultado.</p>" + fonte_html(E5_ESPEC, grafico=False)))


def itens_especificacoes_e5(ctx, e5) -> str:
    """O que cada especificacao e (doc 39, secao 2.1), com os numeros lidos do E5."""
    y = y1_e5(e5)
    cortes = ctx["cortes"]

    def tau(cod, c):
        r = y[(y["especificacao"] == cod) & np.isclose(y["corte_num"], c)]
        return float(r["tau"].iloc[0]) if len(r) else np.nan

    def ep(cod, c):
        r = y[(y["especificacao"] == cod) & np.isclose(y["corte_num"], c)]
        return float(r["ep"].iloc[0]) if len(r) else np.nan

    incl = "; ".join(f"{pp(tau('A', c) - tau('S0', c))} p.p. em {br(c)}" for c in cortes)
    queda = [1 - ep(cod, c) / ep("S0", c) for cod in ("C1", "C2") for c in cortes]
    jan_d = "; ".join(
        (f"±{br(float(m.group(1)))} em {br(r.corte_num)}" if (m := re.match(r"\+-\s*([\d.]+)", str(r.janela or "")))
         else f"sem janela em {br(r.corte_num)}") for r in ordem_e5(y[y["especificacao"] == "D"]).itertuples())
    lr = e5["lr"]
    lr_y = lr[lr["outcome"] == "Y1"]
    b = y[y["especificacao"] == "B"]
    duas = b["municipios_em_duas_janelas"].iloc[0] if len(b) else np.nan
    cel = (e5["res"].get("verificacoes") or {}).get("celulas_reproduzem_y1") or {}
    itens = [
        f"<strong>A, local constante.</strong> Diferença das médias ponderadas pelo kernel; não modela a inclinação. "
        f"Difere do principal exatamente pela contribuição das inclinações ({incl}). Se as inclinações forem reais, esse "
        "é o viés de A, e o IC de A não o inclui: <strong>o IC estreito de A não é ganho de precisão</strong>.",
        "<strong>B, cortes empilhados.</strong> Running variable s − c, interceptos e inclinações por corte e lado, "
        f"salto comum. As janelas dos dois cortes não se sobrepõem ({br_int(duas)} municípios nas duas). O estimando "
        "vira uma média ponderada dos dois saltos.",
        "<strong>C1 e C2, covariáveis pré.</strong> C1 usa estrato territorial, macrorregião e log da população 2010; "
        "C2 soma o IDHM 2010. Não entram o IVS e seus subíndices nem nada do arquivo local. O EP cai "
        f"{pct(min(queda), 0)} a {pct(max(queda), 0)}, e a estimativa em {br(cortes[0])} vai de {pp(tau('S0', cortes[0]))} "
        f"para {pp(tau('C1', cortes[0]))} (C1), dentro do IC do principal.",
        f"<strong>D, local randomization.</strong> Janela escolhida só pelo balanço de covariáveis, antes de ler "
        f"outcomes ({jan_d}). Premissa mais forte: dentro da janela, o lado do corte é como sorteado e Y1 não depende "
        f"do IVS. Na sensibilidade de janelas, nenhum p de Y1 abaixo de {br(lr_y['p_valor'].min(), 2)}.",
        f"<strong>E0, E1 e E2, nível célula</strong> ({br_int(cel.get('celulas'))} células CNES–curso). E0 e E1 têm o "
        "mesmo ponto e mudam o estimando para o salto médio por célula. E2 acrescenta efeitos fixos de curso, e a "
        "estimativa muda bastante (" + "; ".join(f"{pp(tau('E1', c))} → {pp(tau('E2', c))} em {br(c)}" for c in cortes)
        + "): a composição de cursos difere entre os lados da janela (não testado formalmente).",
    ]
    return '<ul class="leitura">' + "".join(f"<li>{x}</li>" for x in itens) + "</ul>"


def tabela_presenca_e5(ctx, e5) -> str:
    esp = e5["esp"]
    p = esp[esp["outcome"] != "Y1"].copy()
    ordem_oc = {k: i for i, k in enumerate(["D1", "D2", "D1+D2"])}
    p["_oc"] = p["outcome"].map(ordem_oc).fillna(9)
    linhas = []
    sem = []
    for oc, g in p.sort_values("_oc", kind="stable").groupby("_oc", sort=True):
        for r in ordem_e5(g).itertuples():
            rot = rotulo_e5(r.especificacao, vies=False) + (' <span class="muted">(viesada)</span>'
                                                           if r.especificacao == "A" else "")
            oc_txt = esc(str(r.outcome).replace("+", " + "))
            if not finito(r.tau):
                sem.append(f"{r.outcome} em {corte_e5(r)}")
                linhas.append([oc_txt, rot, corte_e5(r), '<span class="muted">sem janela</span>', "—", "—", "—"])
                continue
            linhas.append([oc_txt, rot, corte_e5(r),
                           f"<strong>{pp(r.tau)}</strong>" if r.especificacao == "S0" else pp(r.tau),
                           ic_pp(r.ic95_inf, r.ic95_sup), br_p(r.p_valor), n_e5(r)])
    val = p[p["p_valor"].notna()]
    menor = val.loc[val["p_valor"].idxmin()] if len(val) else None
    leitura = ""
    if menor is not None:
        s0 = val[(val["especificacao"] == "S0") & (val["outcome"] == menor["outcome"])
                 & np.isclose(val["corte_num"], menor["corte_num"])]
        oposto = len(s0) and np.sign(s0["tau"].iloc[0]) != np.sign(menor["tau"])
        leitura = (f" {'Nenhum' if (val['p_valor'] >= ALFA).all() else 'Algum'} salto de presença é distinguível de zero a "
                   f"5%. O mais próximo é {esc(menor['outcome'])} em {br(menor['corte_num'])}, na especificação "
                   f"{esc(ESPEC_E5.get(menor['especificacao'], menor['especificacao']))}: {pp(menor['tau'])} p.p., "
                   f"p = {br_p(menor['p_valor'])}"
                   + (f", com sinal oposto ao do principal ({pp(s0['tau'].iloc[0])})" if oposto else "")
                   + ": sintoma de baixa precisão e de sensibilidade à especificação, não evidência de efeito.")
    return tabela(
        [("Outcome", "txt"), ("Especificação", "txt"), ("Corte", "txt nowrap"), ("Salto (p.p.)", "num"),
         ("IC 95% (p.p.)", "num"), ("p", "num"), ("Municípios abaixo / acima", "num")], linhas, classe="compacta",
        titulo="Presença de especialista (secundário): todas as especificações" + selo_e5(),
        legenda=legenda_salto(ctx, OUTCOME_D), chave="tab_e5_presenca",
        rodape=(f'<p class="nota">D1 = especialista do ciclo 1 ativo no município; D2 = idem, ciclo 2; D1 + D2 = os '
                "dois ciclos empilhados (F1 e F2), com EP agrupado por município, porque o mesmo município pode estar nos "
                "dois. Sem janela de local randomization"
                + (f" ({'; '.join(sem)})" if sem else "")
                + ": nenhuma janela candidata passou no balanço e, pela regra fixada antes de rodar, não há "
                  f"estimativa.{leitura}</p>"
                + fonte_html(E5_ESPEC, grafico=False)))


def tabela_descarte_e5(ctx, e5) -> str:
    linhas = []
    for r in ordem_e5(y1_e5(e5)).itertuples():
        lin = [rotulo_e5(r.especificacao), corte_e5(r), pp(r.lim_sup_unilateral_95)]
        for tipo in ("p_unilateral_tau_ge_", "p_tost_"):
            for d in MARGENS_E5:
                p = getattr(r, tipo + margem(d))
                lin.append(f"<strong>{br_p(p)}</strong>" if finito(p) and p < ALFA else br_p(p))
        linhas.append(lin)
    cab = ([("Especificação", "txt"), ("Corte", "txt nowrap"), ("Limite sup. 95% (p.p.)", "num")]
           + [(f"p(τ ≥ +{d})", "num") for d in MARGENS_E5] + [(f"TOST ±{d}", "num") for d in MARGENS_E5])
    return tabela(
        cab, linhas, classe="compacta", grupos=[("", 3), ("Descarta saltos de +Δ p.p. ou mais?", 3),
                                                ("Equivalência em [−Δ; +Δ]?", 3)],
        titulo="O que os dados permitem descartar no preenchimento (Y1)" + selo_e5(), chave="tab_e5_descarte",
        legenda=('<p class="legenda-salto"><strong>Como ler.</strong> Salto = lado com bolsa R$ 5 mil maior menos lado com '
                 "bolsa menor. Limite superior unilateral de 95% = τ̂ + 1,645 EP (em D, por inversão do teste de "
                 "permutação unilateral): o maior salto compatível com os dados a 5% unilateral. p(τ ≥ +Δ) testa a "
                 "hipótese de que o salto é de +Δ p.p. ou mais; em negrito, p &lt; 0,05, isto é, saltos de +Δ p.p. ou "
                 "mais são incompatíveis com os dados. TOST: teste de equivalência em [−Δ; +Δ].</p>"),
        rodape=fonte_html(E5_ESPEC, grafico=False))


def lista_cod(cods: list[str]) -> str:
    cods = list(cods)
    if not cods:
        return "nenhuma"
    return cods[0] if len(cods) == 1 else ", ".join(cods[:-1]) + " e " + cods[-1]


def itens_descarte_e5(ctx, e5) -> str:
    """Leitura do que da para descartar (doc 39, secao 3), gerada a partir de E5_especificacoes.csv."""
    y = y1_e5(e5)
    cortes = ctx["cortes"]
    pcol = {d: "p_unilateral_tau_ge_" + margem(d) for d in MARGENS_E5}
    dcol = {d: "descarta_tau_ge_" + margem(d) for d in MARGENS_E5}
    itens = []
    partes = []
    for c in cortes:
        s0 = s0_e5(e5, c)
        desc = [d for d in MARGENS_E5 if s0[dcol[d]]]
        nao = [d for d in MARGENS_E5 if not s0[dcol[d]]]
        txt = f"em {br(c)}, limite superior de {pp(s0['lim_sup_unilateral_95'])} p.p."
        if desc:
            txt += ("; descarta " + " e ".join(f"+{d} p.p. (p = {br_p(s0[pcol[d]])}"
                                              + (", no limite" if s0[pcol[d]] > 0.04 else "") + ")" for d in desc))
        if nao:
            txt += ("; não descarta " + " nem ".join(f"+{d} p.p. (p = {br_p(s0[pcol[d]])})" for d in nao))
        partes.append(txt)
    itens.append("<strong>Principal (S0):</strong> " + "; ".join(partes) + ".")
    d10 = y[y[dcol[10]]]
    proximos = y.sort_values(pcol[10]).head(2)
    itens.append("<strong>+10 p.p.:</strong> " + (
        "nenhuma especificação descarta. As mais próximas são " + " e ".join(
            f"{esc(r.especificacao)}{'' if not finito(r.corte_num) else ' em ' + br(r.corte_num)} "
            f"(p = {br_p(getattr(r, pcol[10]))})" for r in proximos.itertuples()) + "." if not len(d10) else
        "descartam " + lista_cod([f"{r.especificacao} em {corte_e5(r)}" for r in d10.itertuples()]) + "."))
    txt20 = []
    for c in cortes:
        g = y[np.isclose(y["corte_num"], c)]
        sim = list(g[g[dcol[20]]]["especificacao"])
        nao = list(g[~g[dcol[20]]]["especificacao"])
        txt20.append(f"em {br(c)}, {br_int(len(sim))} das {br_int(len(g))} especificações por corte descartam"
                     + (f" (todas menos {lista_cod(nao)})" if 0 < len(nao) <= 2 else f" ({lista_cod(sim)})" if sim else ""))
    b = y[y["corte_num"].isna()]
    btxt = ""
    if len(b):
        rb = b.iloc[0]
        desc_b = [d for d in MARGENS_E5 if rb[dcol[d]]]
        if desc_b:
            btxt = (f" Empilhando os cortes (B), saltos de +{min(desc_b)} p.p. ou mais ficam descartados: limite superior "
                    f"de {pp(rb['lim_sup_unilateral_95'])} p.p. para a média dos dois saltos.")
    itens.append("<strong>+20 p.p.:</strong> " + "; ".join(txt20) + "." + btxt)
    eq = y[y[[c for c in y.columns if c.startswith("equivalencia_")]].any(axis=1)]
    so_a = len(eq) and set(eq["especificacao"]) == {"A"}
    itens.append("<strong>Equivalência:</strong> " + (
        f"só A passa no TOST, e A ignora as inclinações. Fora de A, nenhuma especificação mostra que o salto está dentro "
        f"de ±{max(MARGENS_E5)} p.p." if so_a else
        ("passam no TOST: " + lista_cod(sorted(set(eq["especificacao"]))) + "." if len(eq) else
         f"nenhuma especificação mostra que o salto está dentro de ±{max(MARGENS_E5)} p.p.")))
    esp = e5["esp"]
    pres = esp[(esp["outcome"] != "Y1") & esp["p_valor"].notna()]
    s0p = pres[(pres["especificacao"] == "S0") & pres[dcol[20]]]
    f2_ = pres[(pres["especificacao"] == "F2")]
    ptxt = ("o principal descarta +20 p.p. só para " + lista_cod(
        [f"{r.outcome} em {br(r.corte_num)} (p = {br_p(getattr(r, pcol[20]))})" for r in s0p.itertuples()])
            if len(s0p) else "o principal não descarta +20 p.p. em nenhum ciclo ou corte")
    if len(f2_):
        rf = f2_.iloc[0]
        desc_f = [d for d in MARGENS_E5 if rf[dcol[d]]]
        if desc_f:
            ptxt += (f". F2, com ciclos e cortes empilhados, descarta +{min(desc_f)} p.p. (limite superior de "
                     f"{pp(rf['lim_sup_unilateral_95'])} p.p.)")
    itens.append("<strong>Presença:</strong> " + ptxt + ".")
    return '<ul class="leitura">' + "".join(f"<li>{x}</li>" for x in itens) + "</ul>"


def caixa_afirmar_e5(ctx, e5) -> str:
    """O que podemos e nao podemos afirmar (doc 39, secao 6), com os numeros lidos do E5."""
    y = y1_e5(e5)
    cortes = ctx["cortes"]
    c0, c1 = cortes[0], cortes[-1]
    lr = e5["lr"]
    lr_min = lr[lr["outcome"] == "Y1"]["p_valor"].min()
    s0 = s0_e5(e5, c0)
    s1 = s0_e5(e5, c1)
    dcol = {d: "descarta_tau_ge_" + margem(d) for d in MARGENS_E5}
    pcol = {d: "p_unilateral_tau_ge_" + margem(d) for d in MARGENS_E5}
    desc0 = [d for d in MARGENS_E5 if s0[dcol[d]]]
    b = y[y["corte_num"].isna()]
    desc_b = [d for d in MARGENS_E5 if len(b) and b.iloc[0][dcol[d]]]
    ll = e5["dec"][e5["dec"]["componente"] == "LL_triangular_principal"]["razao_ep_vs_dm_simples"]
    g0 = y[np.isclose(y["corte_num"], c0) & (y["especificacao"] != "A")]
    nenhuma10 = not y[dcol[10]].any()
    dm = e5["dec"][e5["dec"]["componente"] == "DM_simples"]
    n_lado = int(round(float((dm["n_abaixo"] + dm["n_acima"]).max() / 2)))
    podemos = [
        f"<strong>Nenhuma estimativa distinguível de zero.</strong> Nenhuma das {br_int(len(y))} estimativas para Y1 dá "
        f"p &lt; 0,05: o menor p é {br(y['p_valor'].min(), 2)}, e na sensibilidade de janelas da local randomization, "
        f"{br(lr_min, 2)}. A leitura inconclusiva do E3 se mantém em todas as especificações.",
        f"<strong>Saltos positivos grandes descartados em {br(c0)}.</strong> No principal, os dados são incompatíveis, a "
        "5% unilateral, com saltos de " + " e ".join(
            f"+{d} p.p. ou mais (p = {br_p(s0[pcol[d]])})" for d in sorted(desc0, reverse=True)) + " no preenchimento"
        + (f". Empilhando os cortes, saltos médios de +{min(desc_b)} p.p. ou mais ficam descartados." if desc_b else "."),
        f"<strong>Origem da largura do IC.</strong> Ruído de um outcome com poucas células, ~{br_int(n_lado)} municípios "
        f"por lado e a extrapolação do local linear (× {br(ll.min(), 1)} a × {br(ll.max(), 1)} sobre a diferença de "
        "médias). Não é defeito de especificação.",
    ]
    nao_podemos = [
        "<strong>Afirmar ausência de efeito.</strong> Nenhuma especificação válida mostra que o salto está em "
        f"±{max(MARGENS_E5)} p.p." + (" e nenhuma descarta +10 p.p." if nenhuma10 else "")
        + " Inconclusivo não é ausência de efeito.",
        f"<strong>Usar A.</strong> O IC estreito de A não é inferência válida para o salto ({VIES_A}).",
        "<strong>Promover uma alternativa a principal.</strong> As alternativas mudam o estimando ou a premissa, e a "
        f"estimativa pontual oscila entre {pp(g0['tau'].min())} e {pp(g0['tau'].max())} p.p. em {br(c0)} (sem contar A): "
        "sintoma de baixa precisão, não informação sobre o sinal.",
        f"<strong>Ler o descarte em {br(c1)}.</strong> Nesse corte o principal não descarta nada a partir de +10 p.p. "
        f"(limite superior de {pp(s1['lim_sup_unilateral_95'])} p.p.), e o desequilíbrio de covariáveis do E3 limita "
        "ainda mais a leitura." if not any(s1[dcol[d]] for d in MARGENS_E5) else
        f"<strong>Ler o descarte em {br(c1)} sem cautela.</strong> O desequilíbrio de covariáveis do E3 limita a leitura.",
        "<strong>Usar linguagem causal.</strong> Tudo aqui é exploratório e pós-resultado.",
    ]
    return ('<div class="afirmar"><div><p class="afirmar-tit">O que podemos afirmar</p><ul>'
            + "".join(f"<li>{x}</li>" for x in podemos) + '</ul></div><div><p class="afirmar-tit">O que não podemos '
            "afirmar</p><ul>" + "".join(f"<li>{x}</li>" for x in nao_podemos) + "</ul></div></div>")


def paragrafo_desenhos_e5(ctx, e5) -> str:
    """Controle sintetico, DiD e outros desenhos (doc 39, secao 5) e o que aumentaria a precisao."""
    cen = [c for c in (e5["res"].get("cenarios_ilustrativos_rotulados") or [])
           if math.isclose(float(c.get("corte", -1)), ctx["cortes"][0])]
    prec = ""
    if cen:
        c = cen[0]
        prec = (f" Num cenário ilustrativo do E5 (não é observação: supõe o mesmo desvio-padrão e o mesmo desenho), em "
                f"{br(ctx['cortes'][0])} o MDE de {br(100 * c['mde_80_observado'], 1)} p.p. cairia para "
                f"{br(100 * c['ciclos_1_e_2_independentes']['mde_80'], 1)} p.p. com o preenchimento dos ciclos 1 e 2 "
                f"juntos (otimista) e para {br(100 * c['todos_municipios_do_brasil_na_janela']['mde_80'], 1)} p.p. com "
                "todos os municípios do Brasil na janela; detectar 10 p.p. exigiria cerca de "
                f"{br(c['n_para_mde_10pp']['fator_sobre_n_observado'], 0)} vezes o n atual.")
    return (
        "<p><strong>Controle sintético, DiD e outros desenhos.</strong> Controle sintético e DiD sintético exigem poucas "
        "unidades tratadas e uma série longa do mesmo outcome antes do tratamento; aqui o preenchimento de vagas do PMM-E "
        "não existe antes do programa, há centenas de municípios em cada faixa e os doadores disputariam os mesmos "
        "candidatos. DiD e estudo de evento por faixa também exigem pré-período do outcome. RD com múltiplos cortes e "
        "extrapolação pede grupos expostos a cortes diferentes; todos os municípios enfrentam os mesmos dois cortes, e o "
        "que cabe é o empilhamento (B). RD geográfica não se aplica, porque a bolsa segue o IVS municipal, não uma "
        "fronteira. <strong>Esses desenhos não se aplicam ao outcome da hipótese.</strong> Diferença em "
        "descontinuidades com a oferta CNES muda o outcome e exige protocolo próprio: foi feita depois, no protocolo "
        "40 (E7, seção 10). O que aumentaria a precisão, com o mesmo estimando, é <strong>mais coortes com o mesmo "
        f"outcome</strong>.{prec}</p>")


def frase_e5_resumo(ctx) -> str:
    """Frase do resumo sobre o E5, com os numeros lidos de E5_especificacoes.csv."""
    e5 = ctx.get("e5")
    if not e5:
        return ""
    y = y1_e5(e5)
    alt = y[y["rotulo"] != "PRINCIPAL_CONGELADO_REPRODUZIDO"]
    c0 = ctx["cortes"][0]
    s0 = s0_e5(e5, c0)
    desc = [d for d in MARGENS_E5 if s0["descarta_tau_ge_" + margem(d)]]
    nao = [d for d in MARGENS_E5 if not s0["descarta_tau_ge_" + margem(d)]]
    zero = ("nenhuma é distinguível de zero" if (alt["p_valor"] >= ALFA).all()
            else "alguma é distinguível de zero (ver seção 3)")
    txt = (f"Análises exploratórias pós-resultado ({br_int(len(alt))} especificações alternativas) não mudam a leitura: "
           f"{zero}")
    if desc:
        txt += (f"; os dados descartam, a 5% unilateral, saltos de +{min(desc)} p.p. ou mais no corte {br(c0)} "
                f"(limite superior {br(100 * s0['lim_sup_unilateral_95'], 1)} p.p.)")
        if nao and max(nao) < min(desc):
            txt += f", mas não efeitos de +{max(nao)} p.p."
        else:
            txt += "."
    else:
        txt += "."
    return txt


def secao_e5(ctx) -> str:
    e5 = ctx.get("e5")
    o = ['<section class="quebra"><h2>3. Inferência alternativa (exploratória, pós-resultado)</h2>']
    o.append(f'<div class="aviso"><strong>{esc(AVISO_E5)}.</strong> Esta seção foi escrita depois de o E3 ser lido. '
             "Nenhuma especificação daqui substitui a estimativa principal (local linear, kernel triangular, h = 0,050, "
             "EP HC1). A lista de especificações foi fixada no script antes da primeira execução com dados reais, e "
             "todas são relatadas, qualquer que seja o resultado. O relatório só lê as saídas "
             "<code>output/rdd_bolsa/E5_*</code>; nada é recalculado aqui.</div>")
    if e5 is None:
        o.append(caixa_ausente("Saídas do E5 ausentes", E5_ARQS))
        o.append("</section>")
        return "".join(o)
    res = e5["res"]
    if res.get("status") != "CONCLUIDO" or e5["diverg"]:
        o.append('<p class="alerta">Atenção: E5 com status '
                 f"{esc(res.get('status', '—'))}"
                 + (f"; o S0 do E5 não reproduz o E3 atual em {esc(', '.join(e5['diverg']))}" if e5["diverg"] else "")
                 + ". Rodar de novo <code>scripts/rdd_bolsa/11_inferencia_alternativa.py</code>.</p>")
    o.append("<p>Pergunta do autor: por que os IC do E3 são tão largos, se dá para estreitá-los e se outro método daria "
             "inferência melhor ou diferente. O contraste continua sendo o incentivo marginal anunciado de R$ 5 mil, "
             "possivelmente um pacote. Outcome da hipótese: Y1, a fração de células preenchidas na 1ª chamada do ciclo 1; "
             "secundários: presença de especialista (D1, ciclo 1; D2, ciclo 2).</p>")

    o.append("<h3>Por que o IC é largo</h3>")
    o.append(tabela_decomposicao_e5(ctx, e5))
    o.append("<p>A largura vem de três fatores que se multiplicam:</p>" + itens_largura_e5(ctx, e5))
    o.append(tabela_estimadores_e5(ctx, e5))

    o.append("<h3>Todas as especificações</h3>")
    o.append(figura(
        "Forest plot das especificações do preenchimento (Y1), por corte" + selo_e5(), fig_forest_e5(ctx, e5),
        fonte_html(E5_ESPEC, extra="Estimativas e IC lidos do CSV, sem recálculo"),
        legenda=('<p class="legenda-salto"><strong>Como ler.</strong> Salto = lado com bolsa R$ 5 mil maior (IVS acima do '
                 "corte) menos lado com bolsa menor. Positivo = bolsa maior associada a mais preenchimento. Cada linha é "
                 "uma especificação: ponto = salto, traço = IC 95%. Tracejadas: saltos de +10 e +20 p.p.</p>"),
        sub=(f"{esc(AVISO_E5)}. S0 é o principal do protocolo (o E3); as demais são alternativas que mudam o estimador, "
             "o estimando ou a premissa. A, a local constante, aparece vazada e tracejada porque ignora as inclinações: "
             "seu IC estreito não é inferência válida para o salto. B empilha os dois cortes num salto comum e por isso "
             "fica num painel próprio."),
        chave="fig_e5_forest"))
    o.append(tabela_y1_e5(ctx, e5))
    o.append("<p>O que cada uma é, e o que muda em relação ao principal:</p>" + itens_especificacoes_e5(ctx, e5))
    o.append(tabela_presenca_e5(ctx, e5))

    o.append("<h3>O que os dados permitem descartar</h3>")
    o.append(tabela_descarte_e5(ctx, e5))
    o.append(itens_descarte_e5(ctx, e5))
    o.append(caixa_afirmar_e5(ctx, e5))
    o.append(paragrafo_desenhos_e5(ctx, e5))
    o.append(f'<div class="fonte">Situação registrada: <code>{esc(res.get("status", "—"))}</code>, '
             f"<code>{esc(res.get('rotulo', '—'))}</code>; executado em {data_br(res.get('data_execucao'))} por "
             f"<code>{esc((res.get('script') or {}).get('arquivo', '—'))}</code>. Texto de referência: "
             "<code>docs/06_execucao/39_inferencia_alternativa_rdd_bolsa.md</code>.</div>")
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
    o = ['<section class="quebra"><h2>4. Antes do escore completo: E1, E2 e E4 (exploratórios)</h2>']
    o.append(
        "<p>Até se descobrir que o escore administrativo é o IVS 2010 oficial, o escore só estava publicado para os "
        "municípios com especialista ativo — a cobertura dependia do próprio outcome. O protocolo previu então três "
        "leituras exploratórias: <strong>E1</strong>, razão de densidades dos municípios com especialista, sob a "
        "premissa A1 (não testável na época); <strong>E2</strong>, limites para a diferença de presença sem supor "
        "onde estavam os municípios sem escore; <strong>E4</strong> (adendo), limites e Lee para a proporção "
        "preenchida. <strong>Todos ficam superados pelo E3</strong>, que observa o escore de todos os municípios. "
        f"Os cenários “informados” de E2 e E4 usavam como banda o {esc(ctx['rl']['longo'])}; saíram das saídas "
        "em 18/10/2026 (auditoria 19).</p>")
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
        legenda=('<p class="legenda-salto"><strong>Como ler.</strong> Em todas as colunas, o lado com bolsa R$ 5 mil '
                 "maior (IVS acima do corte) vem primeiro. ρ = acima ÷ abaixo (ρ &gt; 1: mais municípios com "
                 "especialista logo acima do corte). Limites, Lee e salto = acima menos abaixo (positivo = bolsa maior "
                 "associada a mais presença ou preenchimento).</p>"),
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
    o = ['<section class="quebra"><h2>5. Leitura e limites</h2>']
    g, info = ctx["categorias"]
    pacote = (f"A categoria de IVS do MS, usada no PMMB, muda exatamente nos dois cortes da bolsa "
              f"({NUM.ref('tab_escore', 'seção 1')}): qualquer "
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
        ("Gradiente de IVS no A4 e covariáveis de IVS, IDHM e população do arquivo local — reestimados com a base "
         "oficial em 18/10/2026 (auditoria 19)",
         [ROOT / "output" / "tema_trabalho" / "A4_figura_02_gradiente_ivs.png",
          ROOT / "output" / "tema_trabalho" / "A4_tabela_03d_ivs_spline.csv"]),
        ("R1 antigo: “a regra não se reproduz pelo IVS”, “177 acima do piso”, “IVS é piso”", [REGRA_ANTIGA, A01B]),
        ("Primeiro estágio público: salto instável em 0,400 e nulo em 0,500 (artefatos do arquivo local)", [A01]),
        ("Cenário “informado” de E2 e E4, que usava o arquivo local como banda — retirado das saídas em "
         "18/10/2026 (auditoria 19)", [E2_RES, E4_RES]),
        ("Comparação “IVS 2010 público × escore” do R1 com escore parcial", [R1_ADMIN]),
    ]
    rever_html = "".join(
        f"<li>{esc(t)}: " + ", ".join(f"<code>{esc(rel(p))}</code>" + ("" if p.exists() else " (ausente)") for p in ps)
        + "</li>" for t, ps in rever)
    varredura = varrer_citacoes_local()
    blocos = [
        ("Conclusão",
         f"<strong>{esc(frase_conclusao(ctx))}</strong> O salto é sempre o lado da bolsa maior menos o da menor "
         f"(conferido na {NUM.ref('tab_sinal', 'seção 2')}). "
         + ("No outcome secundário, presença de especialista, também não há salto distinguível de zero, nos ciclos 1 "
            "e 2." if (pr[pr["outcome"] == OUTCOME_D]["p_valor"] >= ALFA).all() else
            "No outcome secundário, presença de especialista, há salto com p &lt; 0,05 (ver seção 2).")
         + (f" {esc(frase_e5_resumo(ctx))} (seção 3; exploratório, pós-resultado.)" if ctx.get("e5") else "")),
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
         "O arquivo local entrou em análises anteriores do projeto. As que seguem ativas foram corrigidas em "
         "18/10/2026; as demais ficam só como registro do failure mode "
         "(<code>docs/auditorias/19_reestimacao_base_oficial_failure_mode.md</code>):"
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
    """Tabelas-gemeas dos graficos RD: medias por bin de 0,010, por corte (ciclo 1 e ciclo 2)."""
    paineis = ctx["paineis_rd"]
    figs = " e ".join(NUM.ref(k) for k in ("fig_rd_frac", "fig_rd_pres") if k in NUM.refs) or "os gráficos RD"
    o = ['<section class="quebra"><h2>Apêndice A — dados dos gráficos RD</h2>'
         f"<p>Médias por bin dos gráficos RD ({esc(figs)}). Preench. = fração de células preenchidas na 1ª chamada do "
         f"ciclo 1; Presença = especialista do ciclo ativo em {esc(data_relacao_nominal(ctx['prot']))}. Cada município "
         "conta uma vez por bin; as médias são simples entre municípios. O corte cai no bin de baixo.</p>"]
    for c in ctx["cortes"]:
        pc = {(p["pop"], p["outcome"]): p for p in paineis if math.isclose(p["corte"], c)}
        ref = pc[COMBOS_RD[0]]
        linhas = []
        for i, b0 in enumerate(ref["bins"]):
            marca = "" if b0["dentro"] else ' <span class="muted">°</span>'
            lado = "menor" if b0["hi"] <= ref["c_mil"] else "maior"
            lin = [f"({br(b0['lo'] / 1000)}; {br(b0['hi'] / 1000)}]{marca}", lado]
            for (pop, outcome) in COMBOS_RD:
                b = pc[(pop, outcome)]["bins"][i]
                if (pop, outcome) == ("P1", OUTCOME_FRAC) or (pop == "P2" and outcome == OUTCOME_D):
                    lin.append(br_int(b["n"]))
                lin.append(pct(b["media"]))
            linhas.append(lin)
        cab = [("Bin do IVS", "txt nowrap"), ("Bolsa", "txt"), ("n", "num"), ("Preench.", "num"), ("Presença", "num"),
               ("n", "num"), ("Presença", "num")]
        o.append(tabela(
            cab, linhas, classe="compacta", inteiro=True,
            grupos=[("", 2), ("Ciclo 1", 3), ("Ciclo 2", 2)],
            titulo=(f"Médias por bin de 0,010 do IVS oficial em torno do corte {br(c)} (bolsa "
                    f"{br_mil(ref['bolsa_menor'])} → {br_mil(ref['bolsa_maior'])})"),
            rodape=('<p class="nota">° bin fora da janela principal (não entra nas retas). Bolsa = lado do corte '
                    "(menor = IVS até o corte; maior = acima). As estimativas não usam estes bins: o local linear usa "
                    "os municípios individualmente.</p>" + fonte_html(ESCORE, E4_PROP, ATIVOS_ZIP, grafico=False))))
    o.append("</section>")
    return "".join(o)


def secao_proveniencia() -> str:
    resumos = {E1_EST: ler_json(E1_RES), E1_RES: ler_json(E1_RES), E2_LIM: ler_json(E2_RES), E2_RES: ler_json(E2_RES),
               E4_EST: ler_json(E4_RES), E4_RES: ler_json(E4_RES)}
    # Parte II: produtores declarados (as figuras têm nome montado em f-string e não são achadas por busca).
    for script, figs in FIGURAS_MO.items():
        resumos.update({f: {"script": rel(script)} for f in figs})
    resumos.update({p: {"script": rel(E7_SCRIPT)} for p in (E7_EST, E7_EV, E7_RES)})
    resumos.update({p: {"script": rel(FM_SCRIPT)} for p in (FM_CSV, FM_RES)})
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
# Parte II: rodada multi-outcome (protocolo 40). Só lê saídas gravadas; nada é estimado aqui.
# ---------------------------------------------------------------------------


def corte_txt(c) -> str:
    """'0.300' -> '0,300'; 'empilhado' fica como está."""
    s = str(c)
    return s.replace(".", ",") if re.fullmatch(r"\d\.\d{3}", s) else s


def escala_mo(unidade: str) -> tuple[int, float, str]:
    """(casas, fator, sufixo) de exibição de um salto, pela coluna `unidade` das saídas E6/E7."""
    u = str(unidade)
    if u.startswith("fracao"):
        return 1, 100.0, " p.p."
    if u.startswith("desvios"):
        return 2, 1.0, " DP"
    if u.startswith("log"):
        return 3, 1.0, " (log)"
    if u.startswith("horas"):
        return 1, 1.0, ""
    return 3, 1.0, ""


def tau_mo(x, unidade, sufixo: bool = True) -> str:
    nd, f, suf = escala_mo(unidade)
    return "—" if not finito(x) else sinal(float(x) * f, nd) + (suf if sufixo else "")


def ic_mo(lo, hi, unidade) -> str:
    nd, f, _ = escala_mo(unidade)
    if not (finito(lo) and finito(hi)):
        return "—"
    return f"[{sinal(float(lo) * f, nd)}; {sinal(float(hi) * f, nd)}]"


def n_mo(r) -> str:
    return f"{br_int(r['n_abaixo'])} / {br_int(r['n_acima'])}"


def q_mo(q) -> str:
    return "—" if not finito(q) else br(q, 3)


def contem_zero(lo, hi) -> bool | None:
    if not (finito(lo) and finito(hi)):
        return None
    return float(lo) <= 0 <= float(hi)


def unidade_txt(unidade: str) -> str:
    return {"fracao (x100 = p.p.)": "p.p.", "desvios-padrao (indice)": "DP do lado de baixo"}.get(str(unidade),
                                                                                                  str(unidade))


def como_ler(tipo: str, ctx, extra: str = "") -> str:
    """Caixa "Como ler" antes de cada tabela da parte II (pedido do autor, 19/10/2026)."""
    vf, fx = ctx["valor_faixa"], ctx["faixas"]
    passo = br_mil(vf[fx[1]] - vf[fx[0]])
    por_corte = "; ".join(f"em {br(c)}: {br_mil(vf[fx[i]])} → {br_mil(vf[fx[i + 1]])}" for i, c in enumerate(ctx["cortes"]))
    salto = (f"Salto = lado com bolsa maior (IVS acima do corte) − lado com bolsa menor ({por_corte}); empilhado = "
             f"salto comum aos dois cortes. Positivo = mais do outcome onde a bolsa é {passo} maior.")
    textos = {
        "nivel": salto + " Contraste: <strong>RDD em nível = pacote do corte</strong> (bolsa e outras regras dos mesmos "
                         "cortes, seção 7), não a bolsa pura nem a participação no PMM-E.",
        "dird": (f"Salto da DiRD = salto de ΔY (média do pós − média do pré), lado com bolsa maior − lado com bolsa menor "
                 f"({por_corte}); empilhado = salto comum. Contraste: <strong>bolsa + variação, entre pré e pós, das "
                 "outras descontinuidades</strong>; a DiRD tira só a parte constante no tempo, e a RDD em nível mede o "
                 "pacote inteiro."),
        "escolha": "Coef. = variação no log da razão de chances de a célula ser a 1ª opção por +R$ 1 mil na bolsa dela; "
                   "RC por +" + passo + " = exp(5 × coef.); Δ prob. em p.p. Positivo = bolsa maior atrai mais escolhas. "
                   "Identificado pelos degraus em " + " e ".join(br(c) for c in ctx["cortes"]) + " (IVS em spline "
                   "contínuo). Mede realocação entre células do mesmo curso, condicional a candidatar-se; não é efeito "
                   "sobre o total de candidatos.",
        "diagnostico": salto + " Diagnóstico sem hipótese de efeito: o desejável é não haver salto.",
        "failure": "<strong>Antes</strong> = número calculado com o arquivo de IVS errado (linha de subgrupo da base do "
                   "Ipea, auditoria 16): rótulo FAILURE_MODE, só registro, <strong>não citável</strong>. "
                   "<strong>Depois</strong> = reestimado com o IVS 2010 oficial (a08). A comparação não é resultado.",
        "politicas": "[V] = verificado no texto do ato; [V-dados] = verificado por cálculo sobre arquivos do repositório; "
                     "[INFERÊNCIA] = tirado de dois ou mais textos; [NÃO VERIFICADO] = fonte secundária ou não conferida. "
                     "Qualquer regra que mude no corte entra no contraste de uma RDD em nível (pacote).",
        "datas": "Datas de publicação ou início de cada ato e do PMM-E. “Marca principal” = linha tracejada vermelha no "
                 "estudo de evento do E7; as demais são pontilhadas. Uma política que muda entre o pré e o pós entra no "
                 "contraste da DiRD.",
        "protocolo": "Lista fixada antes de abrir os outcomes novos; nenhuma linha foi escolhida depois de ver "
                     "resultados. Sinal pré-especificado: + = mais provimento.",
        "sintese": "Conteúdo lido de <code>output/rdd_bolsa/E8_resumo.json</code> (tarefa E8), sem interpretação "
                   "acrescentada aqui.",
    }
    txt = textos[tipo] + (" " + extra if extra else "")
    return f'<p class="legenda-salto"><strong>Como ler.</strong> {txt}</p>'


def img_png(p: Path, classe: str = "") -> str:
    dados = base64.b64encode(p.read_bytes()).decode("ascii")
    cl = f' class="{classe}"' if classe else ""
    return f'<img{cl} src="data:image/png;base64,{dados}" alt="{esc(p.name)}">'


def figura_png(titulo: str, arquivos: list[Path], produtor: Path, sub: str = "", nota: str = "", legenda: str = "",
               chave: str | None = None, classe: str = "") -> str:
    """Figura gravada pelo pipeline (PNG em output/), incorporada sem alteração."""
    presentes = [p for p in arquivos if p.exists()]
    if not presentes:
        return caixa_ausente(titulo, arquivos)
    imgs = "".join(img_png(p, classe) for p in presentes)
    lista = ", ".join(f"<code>{esc(rel(p))}</code>" for p in presentes)
    fonte = (f'<div class="fonte">Fonte: {lista} (gravada por <code>{esc(rel(produtor))}</code>; incorporada sem '
             "alteração, não redesenhada por este relatório).</div>")
    return figura(titulo, imgs, fonte, sub=sub, nota=nota, chave=chave, legenda=legenda)


def carregar_mo() -> dict:
    """Saídas da rodada multi-outcome. Cada bloco ausente vira caixa "ausente" na seção correspondente."""
    mo: dict = {"prot40": ler_json(PROT40_JSON)}
    if all(p.exists() for p in (E6_EST, E6_DIAG, E6_RES)):
        mo["e6"] = {"est": pd.read_csv(E6_EST, dtype={"corte": str, "ciclo": str}),
                    "diag": pd.read_csv(E6_DIAG, dtype={"corte": str}), "res": ler_json(E6_RES)}
    if all(p.exists() for p in (E7_EST, E7_EV, E7_RES)):
        mo["e7"] = {"est": pd.read_csv(E7_EST, dtype={"corte": str}),
                    "ev": pd.read_csv(E7_EV, dtype={"corte": str, "competencia": str}), "res": ler_json(E7_RES)}
    if all(p.exists() for p in (E9_EST, E9_EFE, E9_ROB, E9_RES)):
        mo["e9"] = {"est": pd.read_csv(E9_EST, dtype={"ciclo": str}), "efe": pd.read_csv(E9_EFE, dtype={"ciclo": str}),
                    "rob": pd.read_csv(E9_ROB, dtype={"ciclo": str}), "res": ler_json(E9_RES)}
    if FM_CSV.exists() and FM_RES.exists():
        mo["fm"] = {"csv": pd.read_csv(FM_CSV), "res": ler_json(FM_RES)}
    mo["a10"] = ler_json(A10_DIAG)
    mo["e8"] = ler_json(E8_RES) if E8_RES.exists() else None
    for k in ("e6", "e7", "e9"):
        if k in mo:
            nat = {str(v).upper() for v in mo[k]["est"]["natureza_dos_dados"].dropna().unique()}
            if nat != {"EMPIRICO"}:
                raise SystemExit(f"{k.upper()}: natureza_dos_dados {sorted(nat)}; o relatório só exibe dado EMPIRICO")
    return mo


# ----- E6 -----------------------------------------------------------------


def e6_linha(est: pd.DataFrame, **f) -> pd.Series | None:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        m &= (est[k].astype(str) == str(v)).to_numpy()
    g = est[m]
    return g.iloc[0] if len(g) else None


def rot_pop_mo(pop: str, ciclo: str) -> str:
    return f"{esc(pop)} <span class=\"muted\">ciclo {esc(ciclo)}</span>" if str(ciclo) not in ("-", "nan") else esc(pop)


def rot_outcome_mo(r, vistos: set, chave: str = "outcome") -> str:
    """Id do outcome; a descrição só na primeira linha de cada outcome (tabelas longas)."""
    k = str(r[chave])
    if k in vistos:
        return f"<span class=\"muted\">{esc(r['outcome_id'])}</span>"
    vistos.add(k)
    return f"<strong>{esc(r['outcome_id'])}</strong> <span class=\"muted\">{esc(r['descricao_outcome'])}</span>"


def tabela_p1(ctx, e6) -> str:
    est = e6["est"]
    p = est[(est["outcome_id"] == "P1") & (est["especificacao"] == "principal")]
    linhas = [[rot_pop_mo(r["populacao"], r["ciclo"]), corte_txt(r["corte"]), n_mo(r),
               f"<strong>{tau_mo(r['tau'], r['unidade'])}</strong>", ic_mo(r["ic95_inf"], r["ic95_sup"], r["unidade"]),
               ic_mo(r["ic_honesto_inf"], r["ic_honesto_sup"], r["unidade"]), br_p(r["p_valor"])]
              for _, r in p.iterrows()]
    cab = [("População", "txt nowrap"), ("Corte", "txt"), ("Municípios<br><span class=\"muted\">menor / maior</span>", "num"),
           ("Salto", "num"), ("IC 95%<br><span class=\"muted\">CR1/HC1</span>", "num"),
           ("IC honesto<br><span class=\"muted\">M do protocolo</span>", "num"), ("p", "num")]
    return tabela(cab, linhas, classe="compacta", titulo="P1 — índice de atração-presença (KLK de F1.1, F1.2, F1.3 e "
                  "F2.1), h = 0,050: a primeira linha é a hipótese primária", legenda=como_ler("nivel", ctx,
                  "Índice em desvios-padrão do lado de baixo, dentro da janela. No ciclo 3 não há F2.1 (não imputado)."),
                  rodape=fonte_html(E6_EST, grafico=False, extra="linhas outcome_id = P1, especificacao = principal"),
                  chave="tab_p1")


def tabela_p1_sens(ctx, e6) -> str:
    est = e6["est"]
    base = (est["populacao"] == "V1+V2+V3") & (est["corte"] == "empilhado")
    p = est[base & (((est["outcome_id"] == "P1") & est["especificacao"].isin(
        ["principal", "sensibilidade_h", "ic_honesto", "ic_honesto_pos_resultado", "S2_donut", "local_randomization"]))
                    | ((est["outcome_id"] == "P1.anderson") & (est["especificacao"] == "indice_anderson")))]
    rot = {"principal": "principal (protocolo)", "sensibilidade_h": "janela h", "ic_honesto": "IC honesto, M × fator",
           "ic_honesto_pos_resultado": "IC honesto POS_RESULTADO (fora do protocolo)", "S2_donut": "S2 donut",
           "local_randomization": "local randomization", "indice_anderson": "índice de Anderson (adição rotulada)"}
    linhas = []
    for _, r in p.iterrows():
        det = []
        if r["especificacao"] in ("principal", "sensibilidade_h", "S2_donut") and finito(r["h"]):
            det.append(f"h = {br(r['h'], 3)}")
        if finito(r["fator_M"]):
            det.append(f"fator {br(r['fator_M'], 1)}")
        linhas.append([esc(rot.get(r["especificacao"], r["especificacao"])), "; ".join(det) or "—",
                       tau_mo(r["tau"], r["unidade"]), ic_mo(r["ic95_inf"], r["ic95_sup"], r["unidade"]),
                       br_p(r["p_valor"]), "sim" if str(r["no_protocolo"]) == "True" else "não"])
    return tabela([("Especificação", "txt"), ("Parâmetro", "txt"), ("Salto", "num"), ("IC 95%", "num"), ("p", "num"),
                   ("No protocolo", "txt")], linhas, classe="compacta",
                  titulo="P1 empilhado (ciclos e cortes): sensibilidades", legenda=como_ler("nivel", ctx),
                  rodape=fonte_html(E6_EST, grafico=False, extra="população V1+V2+V3, corte empilhado"))


def tabela_f0(ctx, e6) -> str:
    est = e6["est"]
    p = est[(est["especificacao"] == "principal") & est["outcome_id"].isin(["F0.1", "F0.2"]) & (est["populacao"] == "U")
            & (est["no_protocolo"].astype(str) == "True")]
    vistos: set = set()
    linhas = [[rot_outcome_mo(r, vistos), esc(r["ciclo"]),
               corte_txt(r["corte"]), n_mo(r), tau_mo(r["tau"], r["unidade"]),
               ic_mo(r["ic95_inf"], r["ic95_sup"], r["unidade"]), br_p(r["p_valor"]), q_mo(r["q_bky"])]
              for _, r in p.iterrows()]
    return tabela([("Outcome (U)", "txt"), ("Ciclo", "num"), ("Corte", "txt"), ("Municípios", "num"), ("Salto", "num"),
                   ("IC 95%", "num"), ("p", "num"), ("q BKY", "num")], linhas, classe="compacta",
                  titulo="F0 — seleção: ter célula no quadro e células ou vagas por 10 mil hab., em todos os municípios (U)",
                  legenda=como_ler("diagnostico", ctx, "V1, V2 e V3 só existem onde houve vaga; se ter vaga saltasse "
                                   "no corte, a comparação dentro de V_k misturaria efeito e seleção."),
                  rodape=fonte_html(E6_EST, grafico=False), inteiro=False, chave="tab_f0")


def tabela_copolitica(ctx, e6) -> str:
    est = e6["est"]
    p = est[(est["especificacao"] == "principal") & est["outcome_id"].isin(["F0.3", "F0.4", "S1"])
            & (est["no_protocolo"].astype(str) == "True")]
    vistos: set = set()
    linhas = [[rot_outcome_mo(r, vistos), esc(r["populacao"]),
               corte_txt(r["corte"]), n_mo(r), tau_mo(r["tau"], r["unidade"]),
               ic_mo(r["ic95_inf"], r["ic95_sup"], r["unidade"]), br_p(r["p_valor"])] for _, r in p.iterrows()]
    return tabela([("Outcome", "txt"), ("População", "txt"), ("Corte", "txt"), ("Municípios", "num"), ("Salto", "num"),
                   ("IC 95%", "num"), ("p", "num")], linhas, classe="compacta",
                  titulo="F0.3, F0.4 e S1 — demanda municipal do ciclo 3 e PMMB (co-intervenção)",
                  legenda=como_ler("diagnostico", ctx, "F0.4 e S1 são retratos do PMMB em uma data: estoque acumulado "
                                   "de todas as políticas, não fluxo do PMM-E. Salto em S1 (coparticipação) seria o "
                                   "sinal de que o teto da Portaria 752/2023 operou no corte."),
                  rodape=fonte_html(E6_EST, grafico=False), inteiro=False)


def tabela_diag_e6(ctx, e6) -> str:
    diag = e6["diag"]
    dens = diag[(diag["diagnostico"] == "densidade_poisson_mass_points") & (diag["especificacao"] == "principal")]
    bal = diag[(diag["diagnostico"] == "balanco_covariavel_pre") & (diag["especificacao"] == "principal")]
    linhas = []
    for _, r in dens.iterrows():
        b = bal[(bal["populacao"] == r["populacao"]) & (bal["corte"] == r["corte"]) & bal["p_valor"].notna()]
        sig = b[b["p_valor"] < ALFA]
        quais = "; ".join(f"{esc(v)} ({sinal(t, 3)}; p = {br_p(pv)})"
                          for v, t, pv in zip(sig["variavel"], sig["tau"], sig["p_valor"])) or "—"
        linhas.append([esc(r["populacao"]), corte_txt(r["corte"]), n_mo(r),
                       f"{br(r['rho'], 2)} [{br(r['rho_ic95_inf'], 2)}; {br(r['rho_ic95_sup'], 2)}]", br_p(r["p_valor"]),
                       f"{br_int(len(sig))} de {br_int(len(b))}", quais])
    return tabela([("População", "txt"), ("Corte", "txt"), ("Municípios", "num"), ("Razão de densidades [IC 95%]", "num"),
                   ("p", "num"), ("Balanço: p &lt; 0,05", "num"), ("Quais (salto; p)", "txt")], linhas,
                  classe="compacta", titulo="Diagnósticos sem outcome: densidade do IVS e balanço de covariáveis "
                  "pré-programa (h = 0,050)",
                  legenda=como_ler("diagnostico", ctx, "Razão de densidades = municípios logo acima ÷ logo abaixo do "
                                   "corte (1 = sem acúmulo). Balanço: subíndices do IVS, IDHM, população, renda, "
                                   "estrato e macrorregião; o próprio IVS não entra (é a running variable). Parte dos "
                                   "p &lt; 0,05 é esperada por acaso."),
                  rodape=fonte_html(E6_DIAG, grafico=False))


def tabela_componentes(ctx, e6) -> str:
    est = e6["est"]
    p = est[(est["especificacao"] == "principal") & est["familia"].isin(["F1", "F2", "F4"])
            & (est["no_protocolo"].astype(str) == "True")
            & (est["populacao"].str.contains(r"\+", regex=True) | (est["outcome_id"] == "F2.2"))]
    vistos: set = set()
    linhas = [[rot_outcome_mo(r, vistos, "outcome_id"),
               rot_pop_mo(r["populacao"], r["ciclo"]), corte_txt(r["corte"]), n_mo(r),
               tau_mo(r["tau"], r["unidade"]), ic_mo(r["ic95_inf"], r["ic95_sup"], r["unidade"]), br_p(r["p_valor"]),
               q_mo(r["q_bky"])] for _, r in p.iterrows()]
    return tabela([("Outcome", "txt"), ("População", "txt nowrap"), ("Corte", "txt"), ("Municípios", "num"),
                   ("Salto", "num"), ("IC 95%", "num"), ("p", "num"), ("q BKY", "num")], linhas, classe="compacta",
                  titulo="Componentes (secundárias): F1 atração, F2 presença e F4 seleção de quem chega, por corte e "
                         "empilhado, com os ciclos juntos",
                  legenda=como_ler("nivel", ctx, "Frações em p.p.; contagens por célula ou por 10 mil hab. na própria "
                                   "escala; F4 em pontos do barema (sinal teórico ambíguo, fora do índice). q BKY = "
                                   "q-valor de Benjamini–Krieger–Yekutieli dentro da família."),
                  rodape=fonte_html(E6_EST, grafico=False, extra="cada ciclo separado está no mesmo CSV e no doc 41"),
                  inteiro=False, chave="tab_comp")


def tabela_testes_e6(ctx, e6) -> str:
    est = e6["est"]
    linhas = []
    for fam in ("F0", "F1", "F2", "F4"):
        g = est[(est["familia"] == fam) & est["entra_bky"].astype(str).eq("True")]
        linhas.append([fam, br_int(len(g)), br_int(int((g["p_valor"] < ALFA).sum())),
                       br_int(int((g["q_bky"] < ALFA).sum())), br_p(g["p_valor"].min()), q_mo(g["q_bky"].min())])
    return tabela([("Família", "txt"), ("Linhas principais no BKY", "num"), ("p &lt; 0,05", "num"),
                   ("q BKY &lt; 0,05", "num"), ("Menor p", "num"), ("Menor q", "num")], linhas,
                  classe="compacta estreita", titulo="Testes múltiplos por família (linhas principais do protocolo)",
                  legenda=como_ler("protocolo", ctx, "p &lt; 0,05 isolado não é evidência: com muitas linhas, algumas "
                                   "passam por acaso; o q BKY controla a taxa de falsas descobertas na família."),
                  rodape=fonte_html(E6_EST, grafico=False, extra="contagens feitas aqui sobre as colunas entra_bky, "
                                                                 "p_valor e q_bky"))


def secao_e6(ctx) -> str:
    mo = ctx["mo"]
    o = ['<section class="quebra" data-rodada="multioutcome"><h2>8. E6 — funil da bolsa: atração, presença e seleção</h2>']
    e6 = mo.get("e6")
    if not e6:
        o.append(caixa_ausente("Saídas do E6 ausentes", [E6_EST, E6_DIAG, E6_RES]))
        return "".join(o) + "</section>"
    res = e6["res"]
    p1 = res.get("p1_para_holm") or {}
    o.append(f"<p>O E6 estima as famílias F0, F1, F2 e F4 do protocolo 40 em todas as populações e especificações "
             f"fixadas (<code>{esc(rel(E6_EST))}</code>). Contraste registrado nas saídas: “{esc(res.get('contraste', ''))}”. "
             "Ordem de leitura: a hipótese primária P1 primeiro; depois os diagnósticos de seleção, que condicionam a "
             "leitura de V1–V3; por fim os componentes.</p>")
    o.append("<h3>Hipótese primária P1</h3>")
    o.append(tabela_p1(ctx, e6))
    cz = contem_zero(p1.get("ic95_inf"), p1.get("ic95_sup"))
    if cz is not None:
        o.append(f"<p>{'O IC 95% de P1 contém zero: não detectamos efeito do pacote do corte sobre o índice.' if cz else '<span class=\"alerta\">O IC 95% de P1 exclui zero.</span>'} "
                 f"O p de P1 para o Holm com P2 (seção 10) é {br_p(p1.get('p_valor'))} "
                 f"(<code>{esc(rel(E6_RES))}</code>, <code>p1_para_holm</code>). Com o M do protocolo, o IC honesto não "
                 "informa (suporte da quártica até o ponto médio entre cortes); a sensibilidade POS_RESULTADO está abaixo, "
                 "rotulada como fora do protocolo.</p>")
    o.append(tabela_p1_sens(ctx, e6))
    o.append(figura_png("Índice P1 com ciclos e cortes agrupados em r = IVS − corte (visual)",
                        [E6_FIG / "E6_indice_P1_agrupado.png"], E6_SCRIPT, classe="meia",
                        sub="Reta comum em r, só visual; a estimativa P1 usa interceptos e inclinações por ciclo × corte "
                            "(tabela acima).", chave="fig_p1"))
    o.append(figura_png("Índice P1 por ciclo, nos dois cortes (V1, V2 e V3)",
                        [E6_FIG / f"E6_indice_P1_V{k}.png" for k in (1, 2, 3)], E6_SCRIPT))
    o.append("<h3>Seleção e diagnósticos (antes de ler V1–V3)</h3>")
    o.append(tabela_f0(ctx, e6))
    o.append(figura_png("F0.1 — município tem célula no quadro do ciclo 1, em todos os municípios (U)",
                        [E6_FIG / "E6_F0_1_U_c1.png"], E6_SCRIPT,
                        sub="Os ciclos 2 e 3 estão em <code>output/rdd_bolsa/E6_figuras/E6_F0_1_U_c2.png</code> e "
                            "<code>E6_F0_1_U_c3.png</code>."))
    o.append(tabela_diag_e6(ctx, e6))
    o.append(tabela_copolitica(ctx, e6))
    o.append("<h3>Componentes</h3>")
    o.append(tabela_componentes(ctx, e6))
    o.append(figura_png("F1.3 — fração de células preenchidas na 1ª chamada, por ciclo (V1, V2 e V3)",
                        [E6_FIG / f"E6_F1_3_V{k}.png" for k in (1, 2, 3)], E6_SCRIPT,
                        sub="Os gráficos de F1.1, F1.2, F2.1 e F2.3 estão em <code>output/rdd_bolsa/E6_figuras/</code>."))
    o.append(tabela_testes_e6(ctx, e6))
    o.append(f'<div class="fonte">Situação: executado em {data_br(res.get("data_execucao"))} por '
             f"<code>{esc(res.get('script', '—'))}</code>; linguagem registrada: “{esc(res.get('linguagem', ''))}”. "
             "Texto de referência: <code>docs/06_execucao/41_resultados_E6_funil.md</code>.</div>")
    return "".join(o) + "</section>"


# ----- E9 -----------------------------------------------------------------


E9_COMBOS = [  # (modelo, conjunto, especificacao, rótulo) — todas as de bolsa linear do protocolo
    ("logit_condicional_1a_opcao", "principal", "spline_linear__bolsa_linear", "condicional, conjunto principal, spline linear (principal)"),
    ("logit_condicional_1a_opcao", "principal", "spline_quadratico__bolsa_linear", "condicional, conjunto principal, spline quadrático"),
    ("logit_condicional_1a_opcao", "sensibilidade", "spline_linear__bolsa_linear", "condicional, só vaga imediata, spline linear"),
    ("logit_condicional_1a_opcao", "sensibilidade", "spline_quadratico__bolsa_linear", "condicional, só vaga imediata, spline quadrático"),
    ("logit_explodido_1a_2a_opcao", "principal", "spline_linear__bolsa_linear", "explodido (1ª > 2ª), spline linear"),
    ("logit_explodido_1a_2a_opcao", "principal", "spline_quadratico__bolsa_linear", "explodido (1ª > 2ª), spline quadrático"),
]
E9_CICLOS = ("1", "2", "3", "empilhado")


def e9_coef(est, ciclo, especificacao, termo="bolsa_mil", modelo="logit_condicional_1a_opcao",
            conjunto="principal") -> pd.Series | None:
    g = est[(est["ciclo"] == ciclo) & (est["especificacao"] == especificacao) & (est["termo"] == termo)
            & (est["modelo"] == modelo) & (est["conjunto"] == conjunto)]
    return g.iloc[0] if len(g) else None


def e9_efe(efe, ciclo, quantidade, especificacao="spline_linear__bolsa_linear", modelo="logit_condicional_1a_opcao",
           conjunto="principal") -> pd.Series | None:
    g = efe[(efe["ciclo"] == ciclo) & (efe["especificacao"] == especificacao) & (efe["quantidade"] == quantidade)
            & (efe["modelo"] == modelo) & (efe["conjunto"] == conjunto) & (efe["termo"] == "bolsa_mil")]
    return g.iloc[0] if len(g) else None


def e9_rob(rob, analise, ciclo, estatistica) -> pd.Series | None:
    g = rob[(rob["analise"] == analise) & (rob["ciclo"] == ciclo) & (rob["estatistica"] == estatistica)]
    return g.iloc[0] if len(g) else None


def coef_ic_txt(r, nd: int = 3) -> str:
    if r is None:
        return "—"
    return f"{br(r['coef'], nd)} [{br(r['ic95_inf'], nd)}; {br(r['ic95_sup'], nd)}]"


def tabela_e9_principal(ctx, e9) -> str:
    est, efe = e9["est"], e9["efe"]
    linhas = []
    for c in E9_CICLOS:
        r = e9_coef(est, c, "spline_linear__bolsa_linear")
        if r is None:
            continue
        rc = e9_efe(efe, c, "razao_chances_por_5mil")
        dp = e9_efe(efe, c, "variacao_prob_media_pp")
        base = e9_efe(efe, c, "prob_media_base_pp")
        linhas.append([esc(c), br_int(r["n_candidatos"]), br_int(r["g_conjuntos"]), f"<strong>{br(r['coef'], 4)}</strong>",
                       br(r["ep_cluster_conjunto"], 4), f"[{br(r['ic95_inf'], 4)}; {br(r['ic95_sup'], 4)}]", br_p(r["p"]),
                       br_p(r["p_t_g_menos_1"]),
                       f"{br(rc['estimativa'], 3)} [{br(rc['ic95_inf'], 3)}; {br(rc['ic95_sup'], 3)}]" if rc is not None else "—",
                       f"{br(dp['estimativa'], 3)} [{br(dp['ic95_inf'], 3)}; {br(dp['ic95_sup'], 3)}]" if dp is not None else "—",
                       br(base["estimativa"], 3) if base is not None else "—"])
    mu = '<span class="muted">'
    return tabela([("Ciclo", "txt"), ("Candidatos", "num"), (f"Conjuntos<br>{mu}G</span>", "num"),
                   (f"Coef.<br>{mu}por R$ 1 mil</span>", "num"), (f"EP<br>{mu}cluster conjunto</span>", "num"),
                   ("IC 95%", "num"), ("p", "num"), (f"p<br>{mu}t, G − 1</span>", "num"),
                   (f"RC por +R$ 5 mil<br>{mu}[IC 95%]</span>", "num"), (f"Δ prob., p.p.<br>{mu}[IC 95%]</span>", "num"),
                   (f"Prob. base<br>{mu}p.p.</span>", "num")], linhas, classe="compacta",
                  titulo="E9 principal: logit condicional da 1ª opção, conjunto principal, spline linear, bolsa linear",
                  legenda=como_ler("escolha", ctx), rodape=fonte_html(E9_EST, E9_EFE, grafico=False), chave="tab_e9")


def tabela_e9_especificacoes(ctx, e9) -> str:
    est = e9["est"]
    linhas = []
    for modelo, conj, espec, rot in E9_COMBOS:
        lin = [esc(rot)]
        for c in E9_CICLOS:
            r = e9_coef(est, c, espec, modelo=modelo, conjunto=conj)
            lin.append("—" if r is None else f"{coef_ic_txt(r)}<br><span class=\"muted\">p {br_p(r['p'])}</span>")
        linhas.append(lin)
    for modelo, conj, espec, rot in [("logit_condicional_1a_opcao", "principal", "spline_linear__degraus_por_corte",
                                      "degraus iguais? p (spline linear)"),
                                     ("logit_condicional_1a_opcao", "principal", "spline_quadratico__degraus_por_corte",
                                      "degraus iguais? p (spline quadrático)")]:
        lin = [esc(rot)]
        for c in E9_CICLOS:
            r = e9_coef(est, c, espec, termo="teste_igualdade_degraus_0300_menos_0400", modelo=modelo, conjunto=conj)
            lin.append("—" if r is None else br_p(r["p"]))
        linhas.append(lin)
    return tabela([("Especificação do protocolo", "txt")] + [(f"Ciclo {c}" if c != "empilhado" else "Empilhado", "num")
                                                           for c in E9_CICLOS], linhas, classe="compacta",
                  titulo="E9: todas as especificações de bolsa linear do protocolo (coef. [IC 95%] e p) e o teste de "
                         "igualdade dos dois degraus",
                  legenda=como_ler("escolha", ctx, "“Degraus iguais?” testa se o degrau em 0,300 e o em 0,400 têm o "
                                   "mesmo coeficiente (p alto = não rejeita)."),
                  rodape=fonte_html(E9_EST, grafico=False))


def flags_e9(e9) -> dict:
    """Leitura da robustez pós-auditoria, calculada das saídas (nada digitado)."""
    est, rob = e9["est"], e9["rob"]
    f: dict = {}
    for c in E9_CICLOS:
        rad = e9_rob(rob, "score_bootstrap_rademacher_cluster_conjunto", c, "p_H0_beta_igual_0")
        web = e9_rob(rob, "score_bootstrap_webb_cluster_conjunto", c, "p_H0_beta_igual_0")
        cv3 = e9_rob(rob, "cv3_cluster_conjunto", c, "coef_ep_cv3")
        inv = e9_rob(rob, "ic_inversao_score_rademacher_cluster_conjunto", c, "coef_ic95_inversao")
        npl = e9_rob(rob, "placebo_cortes", c, "n_placebos")
        nge = e9_rob(rob, "placebo_cortes", c, "n_abs_t_placebo_maior_ou_igual_ao_real")
        ppo = e9_rob(rob, "placebo_cortes", c, "p_posto")
        cub = e9_coef(est, c, "ROBUSTEZ_POS_AUDITORIA:spline_cubico__bolsa_linear")
        f[c] = {"rad": rad, "web": web, "cv3": cv3, "inv": inv, "npl": npl, "nge": nge, "ppo": ppo, "cub": cub,
                "j050c": e9_coef(est, c, "ROBUSTEZ_POS_AUDITORIA:janela_0050__spline_cubico__bolsa_linear"),
                "j050l": e9_coef(est, c, "ROBUSTEZ_POS_AUDITORIA:janela_0050__spline_linear__bolsa_linear"),
                "nos": e9_coef(est, c, "ROBUSTEZ_POS_AUDITORIA:nos_cada_0050__spline_linear__bolsa_linear")}
    f["c13"] = e9_coef(est, "1+3", "ROBUSTEZ_POS_AUDITORIA:ciclos_1_e_3_empilhados__spline_linear__bolsa_linear")
    if f["c13"] is None:
        g = est[est["especificacao"].eq("ROBUSTEZ_POS_AUDITORIA:ciclos_1_e_3_empilhados__spline_linear__bolsa_linear")
                & est["termo"].eq("bolsa_mil")]
        f["c13"] = g.iloc[0] if len(g) else None
    f["cochran"] = e9_rob(rob, "heterogeneidade_ciclos", "1,2,3", "cochran_Q")
    f["z23"] = e9_rob(rob, "heterogeneidade_ciclos", "2 vs 3", "z_ciclo2_menos_ciclo3")
    f["curso"] = e9_rob(rob, "score_bootstrap_rademacher_cluster_curso", "empilhado", "p_H0_beta_igual_0")

    def menor(r, lim=ALFA):
        return r is not None and finito(r["p"]) and float(r["p"]) < lim

    def exclui(r, a="ic95_inf", b="ic95_sup"):
        return r is not None and contem_zero(r[a], r[b]) is False

    c2 = f["2"]
    f["c2_robusto"] = (menor(c2["rad"]) and menor(c2["web"]) and menor(c2["cv3"]) and exclui(c2["inv"])
                       and c2["nge"] is not None and float(c2["nge"]["valor"]) == 0)
    em = f["empilhado"]
    f["emp_motivos"] = [m for m, ok in [
        ("spline cúbico: IC 95% contém zero", em["cub"] is not None and contem_zero(em["cub"]["ic95_inf"], em["cub"]["ic95_sup"])),
        ("janela ±0,050 com spline cúbico: IC 95% contém zero",
         em["j050c"] is not None and contem_zero(em["j050c"]["ic95_inf"], em["j050c"]["ic95_sup"])),
        ("cortes placebo: p por posto ≥ 0,05", em["ppo"] is not None and float(em["ppo"]["valor"]) >= ALFA),
        ("ciclos 1 e 3 sem o 2: IC 95% contém zero", f["c13"] is not None and contem_zero(f["c13"]["ic95_inf"], f["c13"]["ic95_sup"])),
        ("Q de Cochran rejeita ciclos iguais", menor(f["cochran"])),
    ] if ok]
    f["emp_fragil"] = len(f["emp_motivos"]) > 0
    f["c2_cubico_zero"] = c2["cub"] is not None and contem_zero(c2["cub"]["ic95_inf"], c2["cub"]["ic95_sup"])
    return f


def tabela_e9_robustez(ctx, e9, f) -> str:
    def p_(r):
        return "—" if r is None else br_p(r["p"])

    def ic_(r, a="ic95_inf", b="ic95_sup"):
        return "—" if r is None or not finito(r[a]) else f"[{br(r[a], 3)}; {br(r[b], 3)}]"

    def v_(r, nd=2):
        return "—" if r is None else br(r["valor"], nd)

    itens = [
        ("p score bootstrap, Rademacher", lambda d: p_(d["rad"])),
        ("p score bootstrap, Webb", lambda d: p_(d["web"])),
        ("p CV3 (t, G − 1)", lambda d: p_(d["cv3"])),
        ("IC 95% por inversão do score", lambda d: ic_(d["inv"])),
        ("Placebos: t real", lambda d: v_(e9_rob(e9["rob"], "placebo_cortes", d["_c"], "t_real"))),
        ("Placebos: |t placebo| ≥ |t real| (de N)",
         lambda d: "—" if d["nge"] is None else f"{br_int(d['nge']['valor'])} de {br_int(d['npl']['valor'])}"),
        ("Placebos: p por posto", lambda d: v_(d["ppo"], 3)),
        ("Spline cúbico: coef. [IC 95%]", lambda d: coef_ic_txt(d["cub"])),
        ("Nós a cada 0,05: coef. [IC 95%]", lambda d: coef_ic_txt(d["nos"])),
        ("Janela ±0,050, spline linear", lambda d: coef_ic_txt(d["j050l"])),
        ("Janela ±0,050, spline cúbico", lambda d: coef_ic_txt(d["j050c"])),
    ]
    linhas = []
    for rot, fn in itens:
        linhas.append([esc(rot)] + [fn({**f[c], "_c": c}) for c in E9_CICLOS])
    return tabela([("Teste (cluster por conjunto)", "txt")] + [(f"Ciclo {c}" if c != "empilhado" else "Empilhado", "num")
                                                             for c in E9_CICLOS], linhas, classe="compacta",
                  titulo="E9 — robustez pós-auditoria do principal (pós-resultado, fora do protocolo)",
                  legenda=como_ler("escolha", ctx, "Estes testes foram pedidos pela auditoria independente depois de "
                                   "ver os resultados (linhas ROBUSTEZ_POS_AUDITORIA, no_protocolo = False); não "
                                   "substituem a tabela do protocolo."),
                  rodape=fonte_html(E9_ROB, E9_EST, grafico=False))


def tabela_e9_heterogeneidade(ctx, f) -> str:
    linhas = []
    if f["c13"] is not None:
        r = f["c13"]
        linhas.append(["Ciclos 1 e 3 empilhados, sem o ciclo 2: coef. da bolsa", coef_ic_txt(r, 4), br_p(r["p"])])
    for rot, r in (("Q de Cochran, ciclos 1, 2 e 3", f["cochran"]), ("z, ciclo 2 menos ciclo 3", f["z23"])):
        if r is not None:
            linhas.append([esc(rot), br(r["valor"], 2), br_p(r["p"])])
    if f["curso"] is not None:
        linhas.append(["Empilhado com cluster por curso: p do score bootstrap (Rademacher)", "—", br_p(f["curso"]["p"])])
    return tabela([("Teste", "txt"), ("Estimativa", "num"), ("p", "num")], linhas, classe="compacta estreita",
                  titulo="E9 — heterogeneidade entre ciclos e cluster por curso (pós-auditoria)",
                  legenda=como_ler("escolha", ctx, "Se o empilhado depende de um único ciclo, ele é uma média de ciclos "
                                   "heterogêneos, não um efeito comum bem medido."),
                  rodape=fonte_html(E9_ROB, E9_EST, grafico=False))


def leitura_e9(ctx, e9, f) -> str:
    est = e9["est"]
    pr = {c: e9_coef(est, c, "spline_linear__bolsa_linear") for c in E9_CICLOS}
    itens = []
    zeros = [c for c in ("1", "3") if pr[c] is not None and contem_zero(pr[c]["ic95_inf"], pr[c]["ic95_sup"])]
    pos = [c for c in E9_CICLOS if pr[c] is not None and contem_zero(pr[c]["ic95_inf"], pr[c]["ic95_sup"]) is False
           and float(pr[c]["coef"]) > 0]
    itens.append(f"No principal do protocolo, o IC 95% do coeficiente da bolsa fica acima de zero em: "
                 f"{', '.join(('ciclo ' + c) if c != 'empilhado' else 'empilhado' for c in pos) or 'nenhum'}; "
                 f"contém zero em: {', '.join('ciclo ' + c for c in zeros) or 'nenhum'}.")
    c2 = f["2"]
    if f["c2_robusto"]:
        itens.append(f"<strong>O ciclo 2 é robusto</strong> na inferência com poucos clusters: score bootstrap "
                     f"(Rademacher p {br_p(c2['rad']['p'])}; Webb p {br_p(c2['web']['p'])}), CV3 (p {br_p(c2['cv3']['p'])}) "
                     f"e IC por inversão {('[' + br(c2['inv']['ic95_inf'], 3) + '; ' + br(c2['inv']['ic95_sup'], 3) + ']')} "
                     f"excluem zero; nenhum dos {br_int(c2['npl']['valor'])} cortes placebo tem |t| igual ou maior que o "
                     f"real (p por posto {br(c2['ppo']['valor'], 3)})."
                     + (" Ressalva: com spline cúbico na amostra toda, o IC 95% do ciclo 2 contém zero." if f["c2_cubico_zero"]
                        else ""))
    else:
        itens.append('<span class="alerta">A leitura “ciclo 2 robusto” do doc 42 não se confirma nas saídas atuais; '
                     "ver a tabela de robustez.</span>")
    if f["emp_fragil"]:
        itens.append("<strong>O empilhado é frágil</strong>: " + "; ".join(f["emp_motivos"]) + ". Ele é uma média de "
                     "ciclos heterogêneos e não sobrevive à forma funcional nem à calibração por placebos.")
    else:
        itens.append("O empilhado passa em todos os testes pós-auditoria listados.")
    itens.append("Leitura conjunta: há evidência de que a bolsa anunciada desloca a 1ª opção dentro do ciclo 2, "
                 "condicional a candidatar-se; ela não se generaliza aos ciclos 1 e 3. É realocação entre células, "
                 "secundária e exploratória (protocolo §12), não efeito sobre o total de candidatos."
                 if f["c2_robusto"] and f["emp_fragil"] else
                 "Leitura conjunta: ver as tabelas; a combinação de robustez desta versão difere da registrada no doc 42.")
    return '<ul class="leitura">' + "".join(f"<li>{x}</li>" for x in itens) + "</ul>"


def secao_e9(ctx) -> str:
    mo = ctx["mo"]
    o = ['<section class="quebra" data-rodada="multioutcome"><h2>9. E9 — escolha revelada dos candidatos '
         "(secundária, exploratória)</h2>"]
    e9 = mo.get("e9")
    if not e9:
        o.append(caixa_ausente("Saídas do E9 ausentes", [E9_EST, E9_EFE, E9_ROB, E9_RES]))
        return "".join(o) + "</section>"
    res = e9["res"]
    o.append(f"<p>Estimando registrado: “{esc(res.get('estimando', ''))}”. Identificação: “{esc(res.get('identificacao', ''))}”. "
             "O E9 usa a variação <em>dentro do candidato</em>: a mesma pessoa vê células com bolsas diferentes no "
             "quadro do seu curso. Por isso é muito mais potente que a RDD entre municípios, mas responde a outra "
             "pergunta.</p>")
    f = flags_e9(e9)
    o.append(tabela_e9_principal(ctx, e9))
    o.append(tabela_e9_especificacoes(ctx, e9))
    o.append(tabela_e9_robustez(ctx, e9, f))
    o.append(tabela_e9_heterogeneidade(ctx, f))
    o.append("<h3>Leitura (gerada das saídas)</h3>" + leitura_e9(ctx, e9, f))
    o.append(figura_png("Utilidade estimada da célula contra o IVS, relativa a IVS = 0,300 (spline mais bolsa pela faixa)",
                        [E9_FIG / "E9_utilidade_ivs.png"], E9_SCRIPT, classe="tres-quartos",
                        sub="Os saltos em 0,300 e 0,400 só são efeito da bolsa sob a hipótese de identificação "
                            "(nenhuma outra descontinuidade na atratividade da célula nos cortes); a forma entre os "
                            "cortes depende da flexibilidade do spline.", chave="fig_e9"))
    lim = "".join(f"<li>{esc(x)}</li>" for x in (res.get("limites") or []))
    o.append(f"<p class=\"nota\"><strong>Limites registrados.</strong></p><ul class=\"leitura nota\">{lim}</ul>")
    o.append(f'<div class="fonte">Situação: {br_int(res.get("n_modelos_ok"))} de {br_int(res.get("n_modelos"))} modelos '
             f"convergiram; executado em {data_br(res.get('data_execucao'))} por <code>{esc(res.get('script', '—'))}</code>. "
             "Texto de referência: <code>docs/06_execucao/42_resultados_E9_escolha.md</code>.</div>")
    return "".join(o) + "</section>"


# ----- E7 -----------------------------------------------------------------


def importar_e7():
    spec = importlib.util.spec_from_file_location("e7_dird_relatorio", E7_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        sys.modules["e7_dird_relatorio"] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


E7_ORDEM = [("F3.1", "U"), ("F3.1", "V1"), ("F3.2", "U"), ("F3.3", "U"), ("F3.3.sem_filtro_sus", "U"),
            ("F3.3.soma_parcial", "U"), ("F3.P1", "U"), ("F3.P2", "U"), ("S6", "U")]
E7_CORTES = ("0.300", "0.400", "empilhado")


def e7_linha(est, oid, pop, corte, esp) -> pd.Series | None:
    g = est[(est["outcome_id"] == oid) & (est["populacao"] == pop) & (est["corte"] == corte) & (est["especificacao"] == esp)]
    return g.iloc[0] if len(g) else None


def tau_p_e7(r) -> str:
    if r is None or not finito(r["tau"]):
        return "—"
    marca = "" if contem_zero(r["ic95_inf"], r["ic95_sup"]) is not False else " ●"
    return f"{tau_mo(r['tau'], r['unidade'], sufixo=False)}{marca}<br><span class=\"muted\">p {br_p(r['p_valor'])}</span>"


def tabela_p2(ctx, e7) -> str:
    p2 = e7["res"].get("p2_para_holm") or {}
    r = e7_linha(e7["est"], "F3.1", "U", "empilhado", "principal")
    linhas = [[esc(p2.get("hipotese", "P2")), n_mo(r) if r is not None else "—",
               f"<strong>{tau_mo(p2.get('tau'), r['unidade'] if r is not None else '')}</strong>",
               ic_mo(p2.get("ic95_inf"), p2.get("ic95_sup"), r["unidade"] if r is not None else ""),
               ic_mo(p2.get("ic_honesto_inf"), p2.get("ic_honesto_sup"), r["unidade"] if r is not None else ""),
               br_p(p2.get("p_valor")), q_mo(p2.get("q_bky"))]]
    return tabela([("Hipótese primária", "txt"), ("Municípios", "num"), ("Salto (vínculos por 10 mil hab.)", "num"),
                   ("IC 95% CR1", "num"), ("IC honesto (M)", "num"), ("p", "num"), ("q BKY (F3)", "num")], linhas,
                  classe="compacta", titulo="P2 — F3.1 (vínculos nas CBO-alvo do PMM-E por 10 mil hab.) por DiRD em U, "
                  "cortes empilhados", legenda=como_ler("dird", ctx),
                  rodape=fonte_html(E7_RES, E7_EST, grafico=False, extra="p2_para_holm"), chave="tab_p2")


def tabela_e7_familia(ctx, e7) -> str:
    est = e7["est"]
    linhas = []
    for oid, pop in E7_ORDEM:
        for c in E7_CORTES:
            r = e7_linha(est, oid, pop, c, "principal")
            if r is None:
                continue
            linhas.append([f"{esc(oid)} <span class=\"muted\">{esc(r['descricao_outcome'])}</span>" if c == "0.300" else
                           f"<span class=\"muted\">{esc(oid)}</span>", esc(pop), corte_txt(c), n_mo(r),
                           tau_mo(r["tau"], r["unidade"]), ic_mo(r["ic95_inf"], r["ic95_sup"], r["unidade"]),
                           br_p(r["p_valor"]), q_mo(r["q_bky"]), esc(r["papel"]) if c == "0.300" else ""])
    return tabela([("Outcome", "txt"), ("Pop.", "txt"), ("Corte", "txt"), ("Municípios", "num"), ("Salto", "num"),
                   ("IC 95%", "num"), ("p", "num"), ("q BKY", "num"), ("Papel", "txt")], linhas, classe="compacta",
                  titulo="Família F3 por DiRD (h = 0,050): efeitos, sensibilidades de horas do §16 e placebos",
                  legenda=como_ler("dird", ctx, "Unidades: vínculos ou horas SUS semanais por 10 mil hab. (Censo 2022); "
                                   "F3.2 em p.p. Placebos: generalistas (F3.P1, o que a Portaria 752 e o IED movem e a "
                                   "bolsa não), especialistas fora das CBO-alvo (F3.P2) e médico de família (S6). S6 e as "
                                   "sensibilidades de horas ficam fora do BKY."),
                  rodape=fonte_html(E7_EST, grafico=False), inteiro=False, chave="tab_e7")


def tabela_e7_placebos(ctx, e7) -> str:
    est = e7["est"]
    linhas = []
    for oid, pop in [("F3.1", "U"), ("F3.1", "V1"), ("F3.2", "U"), ("F3.P1", "U"), ("S6", "U")]:
        for c in E7_CORTES:
            vals = [tau_p_e7(e7_linha(est, oid, pop, c, esp)) for esp in
                    ("placebo_pre", "S5_pre_menos_pre_extra", "S5_dird_pre_extra", "principal")]
            if all(v == "—" for v in vals):
                continue
            linhas.append([esc(oid), esc(pop), corte_txt(c)] + vals)
    # Atos com data entre um mês antes do pré e o fim do pré (janelas do protocolo), lidos do resumo do E7.
    atos = [d for d in (e7["res"].get("datas_politicas") or []) if "2024-05" <= str(d.get("data", ""))[:7] <= "2025-06"
            and "PMM-E" not in str(d.get("ato", ""))]
    atos_txt = "; ".join(f"{esc(d.get('ato', ''))}, {data_br(d.get('data'))}" for d in sorted(atos, key=lambda d: d["data"]))
    return tabela([("Outcome", "txt"), ("Pop.", "txt"), ("Corte", "txt"),
                   ("Placebo dentro do pré<br><span class=\"muted\">2024-12..2025-05 − 2024-06..2024-11</span>", "num"),
                   ("S5: pré − pré extra<br><span class=\"muted\">antes do PMM-E</span>", "num"),
                   ("S5: DiRD com pré extra", "num"), ("DiRD principal", "num")], linhas, classe="compacta",
                  titulo="Placebos no tempo e pré extra (S5): a descontinuidade se movia antes do PMM-E?",
                  legenda=como_ler("dird", ctx, "Placebo e S5 deveriam ficar em zero se as outras políticas forem "
                                   "constantes no tempo. ● = IC 95% exclui zero. O placebo dentro do pré não é um nulo "
                                   "limpo; atos das outras políticas perto ou dentro do pré (resumo do E7, auditoria 18): "
                                   + (atos_txt or "—") + "."),
                  rodape=fonte_html(E7_EST, grafico=False))


def tabela_e7_nivel(ctx, e7) -> str:
    est = e7["est"]
    linhas = []
    for oid, pop in [("F3.1", "U"), ("F3.1", "V1"), ("F3.2", "U"), ("F3.3", "U"), ("F3.P1", "U"), ("F3.P2", "U")]:
        for c in ("0.300", "0.400"):
            vals = [tau_p_e7(e7_linha(est, oid, pop, c, esp)) for esp in
                    ("nivel_pre_extra", "nivel_pre", "nivel_pos", "principal")]
            if all(v == "—" for v in vals):
                continue
            linhas.append([esc(oid), esc(pop), corte_txt(c)] + vals)
    return tabela([("Outcome", "txt"), ("Pop.", "txt"), ("Corte", "txt"),
                   ("Nível, pré extra<br><span class=\"muted\">2022-01..2023-03</span>", "num"),
                   ("Nível, pré<br><span class=\"muted\">2024-06..2025-06</span>", "num"),
                   ("Nível, pós<br><span class=\"muted\">2025-10..2026-08</span>", "num"), ("DiRD", "num")], linhas,
                  classe="compacta", titulo="RDD em nível (o pacote do corte) ao lado da DiRD",
                  legenda=como_ler("nivel", ctx, "● = IC 95% exclui zero. Uma descontinuidade em nível já no pré extra, "
                                   "antes de todas as regras com corte em 0,3 ou 0,4 encontradas, é a razão para não ler "
                                   "a RDD em nível como efeito da bolsa; a DiRD tira essa parte se ela for constante."),
                  rodape=fonte_html(E7_EST, grafico=False))


def tabela_e7_evento(ctx, e7) -> str:
    ev = e7["ev"]
    jan = [("pre_extra", "pré extra"), ("entre_pre_extra_e_pre", "entre"), ("pre", "pré"), ("transicao", "transição"),
           ("pos", "pós")]
    linhas = []
    for oid, pop in [("F3.1", "U"), ("F3.1", "V1"), ("F3.P1", "U")]:
        for c in E7_CORTES:
            g = ev[(ev["outcome_id"] == oid) & (ev["populacao"] == pop) & (ev["corte"] == c)
                   & ~ev["referencia"].astype(str).eq("True")]
            if not len(g):
                continue
            lin = [esc(oid), esc(pop), corte_txt(c)]
            for j, _ in jan:
                gj = g[g["janela"] == j]
                lin.append(f"{br_int(int((gj['p_valor'] < ALFA).sum()))} / {br_int(len(gj))}" if len(gj) else "—")
            linhas.append(lin)
    return tabela([("Outcome", "txt"), ("Pop.", "txt"), ("Corte", "txt")] + [(r, "num") for _, r in jan], linhas,
                  classe="compacta", titulo="Estudo de evento: meses com p &lt; 0,05 / meses estimados, por janela "
                  "(referência 2025-06)",
                  legenda=como_ler("dird", ctx, "Cada mês é a RDD de Y_t − Y_2025-06. Antes do PMM-E o desejável é não "
                                   "haver meses fora de zero; contagens feitas aqui sobre a coluna p_valor."),
                  rodape=fonte_html(E7_EV, grafico=False))


def leitura_e7_gerada(ctx, e7) -> str:
    """Frases geradas pela própria função do E7 (gerar_leitura), a partir das saídas; mesmas do doc 43."""
    try:
        mod = importar_e7()
        t = mod.gerar_leitura(e7["est"], e7["ev"])
    except Exception as exc:  # noqa: BLE001 - a seção mostra a falha em vez de inventar texto
        return f'<p class="alerta">Leitura do E7 indisponível: {esc(type(exc).__name__)}: {esc(exc)}</p>'
    blocos = [("leitura_p2", "P2"), ("leitura_evento_f31", "Estudo de evento de F3.1 em U"),
              ("leitura_generalistas", "Generalistas (F3.P1) em 0,400"), ("leitura_s5", "Pré extra (S5) de F3.1")]
    return '<dl class="leitura-dl">' + "".join(
        f'<dt>{esc(rot)}</dt><dd><p class="gerado" data-gerador="14_estimar_E7_dird_cnes.gerar_leitura" '
        f'data-chave="{k}">{esc(t[k])}</p></dd>' for k, rot in blocos if k in t) + "</dl>"


def secao_e7(ctx) -> str:
    mo = ctx["mo"]
    o = ['<section class="quebra" data-rodada="multioutcome"><h2>10. E7 — diferença em descontinuidades no CNES '
         "(oferta líquida, F3)</h2>"]
    e7 = mo.get("e7")
    if not e7:
        o.append(caixa_ausente("Saídas do E7 ausentes", [E7_EST, E7_EV, E7_RES]))
        return "".join(o) + "</section>"
    res = e7["res"]
    ct = res.get("contraste") or {}
    o.append(f"<p>Contraste registrado da DiRD: “{esc(ct.get('dird', ''))}”. O E7 mede oferta cadastrada local no CNES "
             "(vínculos de qualquer programa nas CBO-alvo), não a presença do especialista do PMM-E (F2, no E6), nem "
             "retenção individual.</p>")
    o.append("<h3>Hipótese primária P2</h3>")
    o.append(tabela_p2(ctx, e7))
    o.append(figura_png("DiRD de F3.1 em U: ΔY contra o IVS, nos dois cortes", [E7_FIG / "E7_dird_F3_1_U.png"],
                        E7_SCRIPT))
    o.append("<h3>Família F3</h3>")
    o.append(tabela_e7_familia(ctx, e7))
    o.append("<h3>Placebos, pré extra (S5) e descontinuidade em nível</h3>")
    o.append(tabela_e7_placebos(ctx, e7))
    o.append(tabela_e7_nivel(ctx, e7))
    o.append(figura_png("F3.1 em U: RDD em nível no pré extra, no pré e no pós (o pacote do corte)",
                        [E7_FIG / "E7_nivel_F3_1_U.png"], E7_SCRIPT, classe="tres-quartos"))
    o.append("<h3>Estudo de evento (S5: datas das políticas marcadas)</h3>")
    o.append(tabela_e7_evento(ctx, e7))
    for oid, pop, tit in [("F3_1", "U", "F3.1 (CBO-alvo) em U"), ("F3_P1", "U", "F3.P1 (generalistas, placebo) em U"),
                          ("F3_1", "V1", "F3.1 em V1 (municípios do quadro do ciclo 1)")]:
        o.append(figura_png(f"Estudo de evento da DiRD: {tit}", [E7_FIG / f"E7_evento_{oid}_{pop}.png"], E7_SCRIPT,
                            sub="Salto da RDD de Y_t − Y_2025-06 em cada mês. Tracejado vermelho: atos principais e "
                                "datas do PMM-E; pontilhado: demais regras da auditoria 18; quadrado = referência."))
    o.append("<h3>Leitura do E7 (frases geradas das saídas pelo script do E7)</h3>")
    o.append(leitura_e7_gerada(ctx, e7))
    cont = res.get("contagens") or {}
    o.append(f'<div class="fonte">Situação: executado em {data_br(res.get("data_execucao"))} por '
             f"<code>{esc(res.get('gerador', '—'))}</code>; {br_int(cont.get('linhas'))} linhas em "
             f"<code>{esc(rel(E7_EST))}</code> ({br_int(cont.get('linhas_no_protocolo'))} do protocolo). Demais figuras "
             "(F3.2, F3.3, F3.P2, S6; nível e DiRD) em <code>output/rdd_bolsa/E7_figuras/</code>. Texto de referência: "
             "<code>docs/06_execucao/43_resultados_E7_dird_cnes.md</code>.</div>")
    return "".join(o) + "</section>"


# ----- Protocolo 40, auditoria 18, A4 corrigido e síntese E8 -------------------------------


def secao_protocolo40(ctx) -> str:
    mo = ctx["mo"]
    pj = mo.get("prot40")
    o = ['<section class="quebra" data-rodada="multioutcome"><h2>6. Protocolo 40: famílias, métodos, primárias e '
         "adendos</h2>"]
    if not pj:
        o.append(caixa_ausente("Protocolo 40 (versão de máquina) ausente", [PROT40_JSON]))
        return "".join(o) + "</section>"
    sha_md = sha256(PROT40_MD)
    conf = "confere" if sha_md == pj.get("sha256_texto_canonico") else "NÃO confere"
    aut = pj.get("autorizacao_autor") or {}
    o.append(f"<p>O E3 testou um único outcome e ficou inconclusivo. Em {data_br(aut.get('data'))} o autor autorizou a "
             "rodada multi-outcome; o protocolo foi congelado em "
             f"{data_br(pj.get('data_congelamento'))}, antes de abrir qualquer outcome novo (pré-registro externo: "
             f"{'sim' if pj.get('pre_registro') else 'não'}; o SHA-256 do texto canônico <code>{esc(rel(PROT40_MD))}</code> "
             f"{conf} com o registrado em <code>{esc(rel(PROT40_JSON))}</code>). Ele faz três coisas: deriva do edital "
             "uma família de outcomes fixada antes dos dados; ganha precisão empilhando cortes e ciclos, usando o "
             "universo de municípios e a DiRD no CNES; e trata a ameaça de outras políticas nos mesmos cortes.</p>")
    # Famílias: descrições lidas das saídas (E6/E7) ou, na falta, do protocolo.
    desc: dict[str, str] = {}
    pops: dict[str, str] = {}
    for k in ("e6", "e7"):
        if k in mo:
            est = mo[k]["est"]
            pr = est[est["especificacao"] == "principal"]
            for oid, g in pr.groupby("outcome_id", sort=False):
                desc.setdefault(oid, str(g["descricao_outcome"].iloc[0]))
                pops.setdefault(oid, ", ".join(sorted(set(g["populacao"].astype(str)))))
    linhas = []
    for fam, info in (pj.get("familias") or {}).items():
        for oid, txt in (info.get("outcomes") or {}).items():
            linhas.append([f"<strong>{esc(fam)}</strong>" if oid.endswith(".1") else "", esc(oid),
                           esc(desc.get(oid, txt)), esc(pops.get(oid, "—")),
                           esc(info.get("papel", "")) if oid.endswith(".1") else ""])
    o.append(tabela([("Família", "txt"), ("Id", "txt nowrap"), ("Outcome", "txt"), ("Populações estimadas", "txt"),
                     ("Papel no protocolo", "txt")], linhas, classe="compacta",
                    titulo="Família de outcomes derivada do edital (protocolo §5)",
                    legenda=como_ler("protocolo", ctx, "Populações: U = todos os municípios com IVS oficial; V1–V3 = "
                                     "municípios com célula no quadro do ciclo 1, 2 ou 3; G3 = cardápio de gestores do "
                                     "ciclo 3; “+” = ciclos empilhados."),
                    rodape=fonte_html(PROT40_JSON, E6_EST, E7_EST, grafico=False,
                                      extra="descrições lidas das saídas do E6 e do E7"), inteiro=False))
    tm = pj.get("testes_multiplos") or {}
    prim = "".join(f"<li><strong>{esc(x)}</strong></li>" for x in tm.get("primarias_holm") or [])
    ref = tm.get("referencias_magnitude") or {}
    o.append("<h3>Métodos e testes</h3><ul class=\"leitura\">"
             "<li><strong>Principal:</strong> local linear, kernel triangular, h = 0,050, EP HC1 por município, como no "
             "E3; cada corte e os dois cortes empilhados (r = s − c, intercepto e inclinações por corte e lado, "
             "tratamento comum, cluster por município). Ciclos empilhados com intercepto e inclinações por ciclo.</li>"
             "<li><strong>Sensibilidades:</strong> h = 0,030 e 0,080; IC honesto de Armstrong e Kolesár (M pela regra de "
             "bolso, 0,5M e 2M), ao lado do HC1; local randomization na janela escolhida por balanço (regra do E5).</li>"
             "<li><strong>Por tipo:</strong> Poisson local para contagens; ponderado por células e nível célula para "
             "proporções; limites de Lee para F4.1; DiRD (ΔY = média do pós − média do pré) com estudo de evento, "
             "placebo no pré e Y_pós com Y_pré como covariável no CNES.</li>"
             f"<li><strong>Hipóteses primárias, com Holm entre as duas:</strong><ul>{prim}</ul></li>"
             f"<li><strong>Secundárias:</strong> {esc(tm.get('secundarias', ''))}. Índice: {esc(tm.get('indice', ''))}.</li>"
             f"<li><strong>Referências de magnitude:</strong> preenchimento {esc(ref.get('preenchimento', '—'))}; "
             f"candidaturas {esc(ref.get('candidaturas', '—'))}.</li></ul>")
    # Adendos §12–§16
    mapa = [("E9", "§12", "E9: escolha revelada dos candidatos (logit condicional da 1ª opção; explodido como "
                          "sensibilidade); estimando = escolha entre vagas, não total de candidatos"),
            ("politicas_mesmos_cortes", "§13", "Políticas nos mesmos cortes (auditoria 18): RDD em nível = pacote; "
                                               "suplementares S1–S6"),
            ("E9_conjunto_de_escolha", "§14", "E9: conjunto de escolha principal = todas as células do curso e ciclo, "
                                              "com ou sem vaga imediata; sensibilidade = só vaga imediata"),
            ("E9_forma_funcional", "§15", "E9: IVS em spline contínuo com nós nos cortes (sem salto de nível); bolsa "
                                          "linear (principal) e degrau por corte (sensibilidade)"),
            ("horas_sus", "§16", "F3.3 = horas SUS (TP_SUS_NAO_SUS = 'S'); horas em branco ficam sem valor; sem filtro "
                                 "e soma parcial como sensibilidades rotuladas")]
    linhas = []
    for ad in pj.get("adendos") or []:
        for chave, par, txt in mapa:
            if chave in ad:
                antes = [k.replace("_", " ") for k, v in ad.items() if k.startswith("antes_") and v is True]
                sup = ad.get("suplementares") or {}
                extra = ("<br><span class=\"muted\">" + "; ".join(f"{esc(k)}: {esc(v)}" for k, v in sup.items())
                         + "</span>") if sup else ""
                linhas.append([par, data_br(ad.get("data")), esc(txt) + extra, esc(", ".join(antes))])
    o.append(tabela([("§", "txt"), ("Data", "txt nowrap"), ("Conteúdo", "txt"), ("Registrado", "txt")], linhas,
                    classe="compacta", titulo="Adendos e esclarecimentos (§12–§16), todos antes de estimar",
                    legenda=como_ler("protocolo", ctx, "Cada adendo foi registrado antes da etapa que ele afeta "
                                     "(coluna “Registrado”, lida do JSON do protocolo)."),
                    rodape=fonte_html(PROT40_JSON, grafico=False)))
    expo = "".join(f"<li>{esc(x)}</li>" for x in pj.get("exposicao_previa_a_outcomes") or [])
    o.append(f"<p class=\"nota\"><strong>Exposição prévia a outcomes (registrada no protocolo):</strong></p>"
             f"<ul class=\"leitura nota\">{expo}</ul>"
             f"<p class=\"nota\">Regra de relato: “{esc(pj.get('regra_de_relato', ''))}”.</p>")
    return "".join(o) + "</section>"


def tabelas_md(texto: str) -> list[tuple[list[str], list[list[str]]]]:
    """Tabelas Markdown (cabeçalho, linhas) de um texto."""
    out, atual = [], []
    for ln in texto.splitlines() + [""]:
        if ln.startswith("|"):
            atual.append([c.strip() for c in ln.strip().strip("|").split("|")])
        elif atual:
            if len(atual) >= 2 and set("".join(atual[1])) <= set("-: "):
                out.append((atual[0], atual[2:]))
            atual = []
    return out


def md_inline(s: str) -> str:
    """Markdown em linha (negrito, código) para HTML, com escape."""
    h = esc(s)
    h = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", h)
    return re.sub(r"`(.+?)`", r"<code>\1</code>", h)


def secao_politicas(ctx) -> str:
    mo = ctx["mo"]
    o = ['<section class="quebra" data-rodada="multioutcome"><h2>7. Políticas nos mesmos cortes de IVS '
         "(auditoria 18)</h2>"]
    if not AUD18_MD.exists():
        o.append(caixa_ausente("Auditoria 18 ausente", [AUD18_MD]))
        return "".join(o) + "</section>"
    texto = AUD18_MD.read_text(encoding="utf-8")
    o.append("<p>Além da bolsa do PMM-E, outras regras federais mudam em 0,300 e em 0,400. Uma RDD em nível nesses "
             "cortes mede um <strong>pacote</strong>; a DiRD do CNES (seção 10) remove só a parte constante no tempo. "
             "Os outcomes do funil do candidato (E6 F1, E9) são os mais próximos da bolsa, porque as outras regras não "
             "pagam o especialista do PMM-E nos atos arquivados.</p>")
    tabs = tabelas_md(texto)
    imp = next(((c, l) for c, l in tabs if c and c[0] == "Corte" and any("verificado" in x for x in c)), None)
    if imp:
        cab, lin = imp
        o.append(tabela([(md_inline(x), "txt") for x in cab], [[md_inline(x) for x in ln] for ln in lin],
                        classe="compacta", titulo="O que muda em cada corte além da bolsa: verificado × não verificado",
                        legenda=como_ler("politicas", ctx),
                        rodape=fonte_html(AUD18_MD, grafico=False, extra=f"§3, tabela copiada do documento na geração; "
                                                                          f"SHA-256 {sha256(AUD18_MD)[:12]}")))
    else:
        o.append('<p class="alerta">Tabela “Implicações para o estimando” não encontrada na auditoria 18.</p>')
    dird = next(((c, l) for c, l in tabs if c and c[0] == "Política" and any("Constante" in x for x in c)), None)
    if dird:
        cab, lin = dird
        o.append(tabela([(md_inline(x), "txt") for x in cab], [[md_inline(x) for x in ln] for ln in lin],
                        classe="compacta", titulo="A hipótese da DiRD: cada política é constante entre pré e pós?",
                        legenda=como_ler("politicas", ctx, "A DiRD remove só a parte constante; o que muda entre pré e "
                                         "pós continua no contraste."),
                        rodape=fonte_html(AUD18_MD, grafico=False, extra="§3.1")))
    a10 = mo.get("a10") or {}
    sob = a10.get("municipios_sobre_os_limites") or {}
    e7 = mo.get("e7")
    datas = (e7["res"].get("datas_politicas") if e7 else None) or []
    if datas:
        linhas = [[data_br(d.get("data")), esc(d.get("ato", "")), "sim" if d.get("marca_principal") else "não",
                   esc(d.get("fonte", ""))] for d in sorted(datas, key=lambda d: d.get("data", ""))]
        o.append(tabela([("Data", "txt nowrap"), ("Ato ou marco", "txt"), ("Marca principal no estudo de evento", "txt"),
                         ("Fonte", "txt")], linhas, classe="compacta",
                        titulo="Datas das políticas e do PMM-E marcadas no estudo de evento do E7",
                        legenda=como_ler("datas", ctx, "Datas lidas do resumo do E7, que as tirou das auditorias 18 "
                                         "e 01."), rodape=fonte_html(E7_RES, grafico=False, extra="datas_politicas")))
    itens = []
    for c in ("0.300", "0.400"):
        v = sob.get(c) or {}
        if v:
            itens.append(f"{br_int(v.get('n_municipios'))} municípios com IVS exatamente {corte_txt(c)}")
    s3 = ((mo.get("e6") or {}).get("res") or {}).get("S3") or {}
    pm = s3.get("portes_muda") or {}
    if itens or pm:
        o.append("<p class=\"nota\">Onde as convenções de fronteira divergem: "
                 + ("; ".join(itens) + f" (<code>{esc(rel(A10_DIAG))}</code>), excluídos no donut S2. " if itens else "")
                 + ("Classes de porte em que o estrato da APS muda no corte (S3): "
                    + "; ".join(f"{corte_txt(c)}: portes {', '.join(str(x) for x in v)}" for c, v in pm.items())
                    + f" (<code>{esc(rel(E6_RES))}</code>)." if pm else "") + "</p>")
    return "".join(o) + "</section>"


def secao_a4(ctx) -> str:
    mo = ctx["mo"]
    o = ['<section class="quebra" data-rodada="multioutcome"><h2>11. A4 reestimado com a base oficial '
         "(auditoria 19)</h2>"]
    fm = mo.get("fm")
    if not fm:
        o.append(caixa_ausente("Registro do failure mode ausente", [FM_CSV, FM_RES]))
        return "".join(o) + "</section>"
    d, res = fm["csv"], fm["res"]
    nat = set(d["natureza_antes"].astype(str)) | set(d["natureza_depois"].astype(str))
    o.append("<p>O A4 (atração por estrato territorial e gradiente de IVS no ciclo 1) usava covariáveis do arquivo de "
             "IVS errado. Ele foi reestimado com o IVS 2010 oficial e a população do Censo 2022. A coluna "
             "“antes” fica só como registro do failure mode "
             f"(natureza das colunas no arquivo: {esc(', '.join(sorted(nat)))}; referência Git "
             f"<code>{esc(str(res.get('ref_git_antes', ''))[:12])}</code>).</p>")
    a4 = d[d["bloco"].astype(str).str.startswith("A4")]
    linhas, blocos = [], set()
    for _, r in a4.iterrows():
        muda = [m for m, k in (("p", "muda_lado_de_5pct_p"), ("q", "muda_lado_de_5pct_q"), ("sinal", "muda_sinal"))
                if str(r[k]) == "True"]
        novo = r["bloco"] not in blocos
        blocos.add(r["bloco"])
        linhas.append([f"<strong>{esc(r['bloco'])}</strong>" if novo else "", esc(r["termo"]),
                       f'<span class="failure">{br(r["coef_antes_failure_mode"], 3)}</span>',
                       f"<strong>{br(r['coef_depois'], 3)}</strong>",
                       f"{br(r['ep_antes_failure_mode'], 3)} → {br(r['ep_depois'], 3)}",
                       f"{br_p(r['p_antes_failure_mode'])} → {br_p(r['p_depois'])}",
                       (f"{br_p(r['q_antes_failure_mode'])} → {br_p(r['q_depois'])}" if finito(r["q_depois"]) else "—"),
                       ", ".join(muda) or "—"])
    o.append(tabela([("Bloco", "txt"), ("Termo", "txt nowrap"),
                     ("Coef. antes<br><span class=\"muted\">FAILURE_MODE</span>", "num"),
                     ("Coef. depois<br><span class=\"muted\">EMPIRICO</span>", "num"), ("EP antes → depois", "num"),
                     ("p antes → depois", "num"), ("q antes → depois", "num"), ("Cruza 5% / sinal", "txt")], linhas,
                    classe="compacta",
                    titulo="A4: antes (failure mode, não citável) → depois (base oficial)",
                    legenda=como_ler("failure", ctx), rodape=fonte_html(FM_CSV, grafico=False,
                                                                        extra="blocos A4; os blocos A5 estão no mesmo "
                                                                              "arquivo e na auditoria 19"),
                    inteiro=False, chave="tab_a4"))
    mud = [m.lstrip("- ").strip() for m in res.get("mudancas_de_conclusao") or []]
    if mud:
        o.append("<p><strong>Mudanças de conclusão registradas</strong> (sinal ou lado do limiar de 5%):</p>"
                 '<ul class="leitura">' + "".join(f"<li>{md_inline(m)}</li>" for m in mud) + "</ul>")
    cad = res.get("cadeia_rdd") or {}
    idt = cad.get("estimativas_identicas_byte_a_byte") or {}
    if idt:
        n_ok = sum(1 for v in idt.values() if v is True)
        o.append(f"<p class=\"nota\">RDD da bolsa: {br_int(n_ok)} de {br_int(len(idt))} arquivos de estimativas "
                 "reexecutados ficaram idênticos byte a byte (a cadeia da RDD já usava o IVS oficial).</p>")
    o.append(f'<div class="fonte">Fonte: <code>{esc(rel(FM_CSV))}</code> e <code>{esc(rel(FM_RES))}</code> '
             "(gravados por <code>scripts/tema_trabalho/12_registrar_failure_mode_ivs.py</code>). Texto de referência: "
             "<code>docs/auditorias/19_reestimacao_base_oficial_failure_mode.md</code>.</div>")
    return "".join(o) + "</section>"


def valor_e8(v, prof: int = 0) -> str:
    """Renderização genérica de E8_resumo.json (esquema definido pela tarefa E8, não por este relatório)."""
    if isinstance(v, dict):
        if prof >= 3:
            return f"<code>{esc(json.dumps(v, ensure_ascii=False)[:400])}</code>"
        return '<dl class="kv">' + "".join(f"<dt>{esc(k)}</dt><dd>{valor_e8(x, prof + 1)}</dd>" for k, x in v.items()) + "</dl>"
    if isinstance(v, list):
        if v and all(isinstance(x, dict) for x in v):
            chaves = list(dict.fromkeys(k for x in v for k in x))
            if len(chaves) <= 10:
                return tabela([(esc(k), "txt") for k in chaves],
                              [[valor_e8(x.get(k), prof + 1) for k in chaves] for x in v], classe="compacta")
        return "<ul>" + "".join(f"<li>{valor_e8(x, prof + 1)}</li>" for x in v) + "</ul>"
    if isinstance(v, bool):
        return "sim" if v else "não"
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return esc(f"{v}".replace(".", ",")) if isinstance(v, float) else br_int(v)
    return "—" if v is None else md_inline(str(v))


def secao_sintese_e8(ctx, caminho: Path | None = None) -> str:
    """Placeholder marcado da síntese E8: lê E8_resumo.json se existir; senão, 'pendente'. Nunca inventa conteúdo."""
    caminho = caminho or E8_RES
    o = ['<section class="quebra" data-rodada="multioutcome" id="sintese-e8"><h2>12. Síntese (E8)</h2>',
         '<div class="reservado"><p class="pend-tit">Seção reservada à tarefa E8 (síntese, Holm entre P1 e P2 e '
         "doc 44). O relatório não escreve conteúdo próprio aqui.</p>"]
    dados = ler_json(caminho) if caminho.exists() else None
    if not dados:
        o.append(f'<p><span class="pill pill-pend">pendente</span> <code>{esc(rel(caminho))}</code> ainda não existe. '
                 "A seção será preenchida quando a síntese for gravada e o relatório for gerado de novo.</p>")
    else:
        o.append(como_ler("sintese", ctx))
        o.append(f'<p><span class="pill pill-ok">lido</span> <code>{esc(rel(caminho))}</code> '
                 f"(SHA-256 <code>{sha256(caminho)[:12]}</code>).</p>")
        o.append(valor_e8(dados))
        docs44 = sorted((ROOT / "docs" / "06_execucao").glob("44_*.md"))
        if docs44:
            o.append(f'<p class="nota">Texto de referência: <code>{esc(rel(docs44[0]))}</code>.</p>')
    o.append("</div></section>")
    return "".join(o)


# ----- Resumo da rodada (hipóteses primeiro) --------------------------------------------


def secao_resumo_mo(ctx) -> str:
    mo = ctx["mo"]
    o = ['<section class="quebra resumo" data-rodada="multioutcome"><h2>Resumo da rodada multi-outcome '
         "(protocolo 40)</h2>"]
    e6, e7, e9 = mo.get("e6"), mo.get("e7"), mo.get("e9")
    linhas = []
    if e6:
        p1 = e6["res"].get("p1_para_holm") or {}
        r = e6_linha(e6["est"], outcome_id="P1", especificacao="principal", populacao="V1+V2+V3", corte="empilhado")
        u = r["unidade"] if r is not None else "desvios-padrao (indice)"
        linhas.append(["<strong>P1</strong> índice de atração-presença (F1.1, F1.2, F1.3, F2.1)",
                       "RDD em nível: pacote do corte", "V1+V2+V3, ciclos e cortes empilhados",
                       n_mo(r) if r is not None else "—", f"<strong>{tau_mo(p1.get('tau'), u)}</strong>",
                       ic_mo(p1.get("ic95_inf"), p1.get("ic95_sup"), u), br_p(p1.get("p_valor"))])
    if e7:
        p2 = e7["res"].get("p2_para_holm") or {}
        r = e7_linha(e7["est"], "F3.1", "U", "empilhado", "principal")
        u = r["unidade"] if r is not None else ""
        linhas.append(["<strong>P2</strong> F3.1: vínculos nas CBO-alvo do PMM-E por 10 mil hab. (CNES)",
                       "DiRD: bolsa + variação das outras descontinuidades", "U, cortes empilhados",
                       n_mo(r) if r is not None else "—", f"<strong>{tau_mo(p2.get('tau'), u)}</strong>",
                       ic_mo(p2.get("ic95_inf"), p2.get("ic95_sup"), u), br_p(p2.get("p_valor"))])
    holm = "ver seção 12 (E8)" if mo.get("e8") else '<span class="pill pill-pend">pendente</span> (E8)'
    o.append(tabela([("Hipótese primária (ordem do protocolo §7)", "txt"), ("Contraste", "txt"), ("População", "txt"),
                     ("Municípios", "num"), ("Salto", "num"), ("IC 95%", "num"), ("p (antes do Holm)", "num")], linhas,
                    classe="compacta resultados", titulo="As duas hipóteses primárias da rodada, com Holm entre elas",
                    legenda=como_ler("nivel", ctx, "P1 está em desvios-padrão do lado de baixo; P2 em vínculos por 10 mil "
                                     "hab., por DiRD."),
                    rodape=f'<p class="nota">Holm entre P1 e P2: {holm}.</p>'
                           + fonte_html(E6_RES, E7_RES, grafico=False, extra="p1_para_holm e p2_para_holm")))
    itens = []
    if e6:
        p1 = e6["res"].get("p1_para_holm") or {}
        cz = contem_zero(p1.get("ic95_inf"), p1.get("ic95_sup"))
        itens.append("<strong>P1 (funil, E6):</strong> " + ("IC 95% contém zero: não detectamos efeito do pacote do corte "
                     "sobre atração e presença." if cz else "IC 95% exclui zero (ver seção 8).") + " Componentes e "
                     "diagnósticos na seção 8; o F0 de seleção é lido antes de V1–V3.")
    if e7:
        p2 = e7["res"].get("p2_para_holm") or {}
        cz = contem_zero(p2.get("ic95_inf"), p2.get("ic95_sup"))
        itens.append("<strong>P2 (CNES, E7):</strong> " + ("IC 95% contém zero: a DiRD não detecta mudança na oferta "
                     "cadastrada nas CBO-alvo." if cz else "IC 95% exclui zero (ver seção 10).")
                     + " Vínculo no CNES não é médico do PMM-E; placebos, pré extra e estudo de evento na seção 10.")
    if e9:
        f = flags_e9(e9)
        pr = {c: e9_coef(e9["est"], c, "spline_linear__bolsa_linear") for c in E9_CICLOS}
        coefs = "; ".join(f"{'ciclo ' + c if c != 'empilhado' else 'empilhado'} {br(pr[c]['coef'], 3)} (p {br_p(pr[c]['p'])})"
                          for c in E9_CICLOS if pr[c] is not None)
        itens.append("<strong>Secundária (E9, escolha dos candidatos; exploratória):</strong> coeficiente da bolsa por "
                     f"R$ 1 mil: {coefs}. "
                     + ("O ciclo 2 sobrevive à inferência com poucos clusters e aos cortes placebo; o empilhado é frágil "
                        "(forma funcional e placebos). " if f["c2_robusto"] and f["emp_fragil"] else
                        "Robustez: ver seção 9. ")
                     + "É realocação entre células, não efeito sobre o total de candidatos.")
    itens.append("<strong>Pacote:</strong> outras regras federais mudam nos mesmos cortes (seção 7); nenhuma linha em "
                 "nível é o efeito da bolsa pura, nem da participação no PMM-E, nem do Agora Tem Especialistas.")
    if mo.get("fm"):
        itens.append("<strong>A4 corrigido:</strong> o gradiente territorial reestimado com a base oficial está na "
                     "seção 11; os números antigos ficam só como failure mode.")
    o.append('<ul class="resumo-lista">' + "".join(f"<li>{x}</li>" for x in itens) + "</ul>")
    dizer = []
    p1z = contem_zero(*((e6["res"].get("p1_para_holm") or {}).get(k) for k in ("ic95_inf", "ic95_sup"))) if e6 else None
    p2z = contem_zero(*((e7["res"].get("p2_para_holm") or {}).get(k) for k in ("ic95_inf", "ic95_sup"))) if e7 else None
    if p1z and p2z:
        dizer.append("“Com o protocolo congelado, não detectamos efeito do pacote do corte de IVS sobre o funil (P1) nem "
                     "sobre a oferta de especialistas no CNES (P2)”, com os IC ao lado.")
    if e9:
        f = flags_e9(e9)
        if f["c2_robusto"] and f["emp_fragil"]:
            dizer.append("“Entre as vagas do mesmo curso, candidatos do ciclo 2 escolheram mais as células com bolsa "
                         "maior; o resultado não se repete nos ciclos 1 e 3” (E9, exploratório).")
    dizer.append("Evitar: “a bolsa não funciona”, “efeito nulo” e “efeito da bolsa” para resultados em nível.")
    o.append('<div class="dizer"><strong>Como dizer nos slides.</strong><ul>' + "".join(f"<li>{x}</li>" for x in dizer)
             + "</ul></div>")
    return "".join(o) + "</section>"


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
.kicker { font-size: 9pt; color: var(--ink2); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2mm; }
.lead { font-size: 11pt; color: var(--ink2); max-width: 160mm; }
dl.meta { display: grid; grid-template-columns: 42mm 1fr; gap: 3pt 8pt; margin: 7mm 0; font-size: 9.4pt; }
dl.meta dt { color: var(--muted); }
dl.meta dd { margin: 0; }
.aviso { border-left: 3px solid var(--warn); background: var(--warn-bg); padding: 8pt 10pt; margin: 2mm 0 6mm; font-size: 9.6pt; }
table.status td:first-child { font-weight: 600; }
.sumario { list-style: none; padding-left: 0; }
.sumario li { margin-bottom: 1pt; }
.pill { display: inline-block; font-size: 7.4pt; font-weight: 600; padding: 1pt 6pt; border-radius: 8pt;
  text-transform: uppercase; letter-spacing: 0.03em; white-space: nowrap; }
.pill-ok { background: #e3f1e3; color: #006300; }
.pill-pend { background: #fbecd2; color: #7a4d00; }
.pill-hist { background: #ecebe6; color: #52514e; }
.pendente { border: 1px solid var(--axis); background: var(--wash); padding: 8pt 10pt; border-radius: 4px; margin: 6pt 0 10pt; }
.pend-tit { font-weight: 600; }
section.resumo h2 { margin-bottom: 8pt; }
ul.resumo-lista { padding-left: 13pt; margin-bottom: 6pt; }
ul.resumo-lista li { margin-bottom: 4pt; line-height: 1.34; font-size: 8.8pt; }
section.resumo .conclusao { font-size: 9pt; line-height: 1.38; }
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
.legenda-salto { font-size: 8.2pt; line-height: 1.38; color: var(--ink); background: var(--wash);
  border-left: 3px solid var(--s1); padding: 3pt 7pt; margin: 2pt 0 4pt; }
th.grupo { text-align: center; border-bottom: 1px solid var(--grid); padding-bottom: 1pt; color: var(--ink); }
th.grupo.vazio { border-bottom: none; }
table.resultados td { vertical-align: middle; }
.conclusao { border-left: 3px solid var(--ink); background: var(--wash); padding: 6pt 10pt; margin: 2pt 0 8pt;
  font-size: 9.4pt; line-height: 1.42; break-inside: avoid; }
.reservado { border: 1px dashed var(--axis); padding: 6pt 10pt 2pt; border-radius: 4px; margin: 4pt 0 10pt; }
.afirmar { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; border: 1px solid var(--axis);
  border-radius: 4px; padding: 7pt 10pt 4pt; margin: 8pt 0 10pt; font-size: 8.6pt; line-height: 1.38;
  break-inside: avoid; }
.afirmar ul { padding-left: 12pt; margin: 2pt 0 4pt; }
.afirmar li { margin-bottom: 3pt; }
.afirmar-tit { font-weight: 650; margin: 0 0 2pt; }
ol.leitura { padding-left: 16pt; }
figure img { display: block; width: 100%; height: auto; margin: 2pt auto 4pt; }
figure img.meia { width: 62%; }
figure img.tres-quartos { width: 78%; }
.failure { color: var(--muted); text-decoration: line-through; text-decoration-color: #c3c2b7; }
.parte { break-before: page; font-size: 17pt; font-weight: 650; color: var(--ink); border-bottom: 2px solid var(--ink);
  padding-bottom: 4pt; margin: 0 0 10pt; }
.parte + section.quebra { break-before: auto; }
ul.nota li { font-size: 8.2pt; color: var(--ink2); }
.legenda-salto { break-after: avoid; }
ol.sumario { columns: 2; column-gap: 10mm; font-size: 8.8pt; }
section.capa table.status { font-size: 7.8pt; }
section.capa dl.meta { margin: 4mm 0; }
section.capa .aviso { margin-bottom: 3mm; }
section.capa h3 { margin-top: 8pt; }
section.capa table.status td { padding: 1.6pt 4pt; }
ol.leitura li, ul.leitura li { margin-bottom: 3pt; }
"""


def montar_html(commit, sujo, agora) -> str:
    ctx = carregar()
    ctx.update({"commit": commit, "sujo": sujo, "agora": agora})
    ctx["divergencias_pop"] = conferir_populacoes(ctx)
    ctx["n_regra"] = numeros_regra(ctx)
    ctx["cruz"] = cruzamento_grade(ctx)
    ctx["categorias"] = categorias_ivs(ctx)
    ctx["n_e3"] = numeros_e3(ctx)
    ctx["e3"] = importar_e3()
    ctx["pops"] = dados_populacoes(ctx)
    ctx["paineis_rd"] = dados_rd(ctx)
    ctx["globais"] = dados_global(ctx)
    ctx["densidade"] = dados_densidade(ctx)
    ctx["balanco_dp"] = dados_balanco(ctx)
    ctx["nota_suporte"] = nota_suporte(ctx)
    ctx["e5"] = carregar_e5(ctx)
    ctx["mo"] = carregar_mo()
    corpo = [
        secao_capa(ctx),
        secao_resumo(ctx),
        secao_resumo_mo(ctx),
        secao_regra(ctx),
        secao_e3(ctx),
        secao_e5(ctx),
        secao_antes(ctx),
        secao_leitura(ctx),
        '<div class="parte" data-rodada="divisor">Parte II — rodada multi-outcome (protocolo 40)</div>',
        secao_protocolo40(ctx),
        secao_politicas(ctx),
        secao_e6(ctx),
        secao_e9(ctx),
        secao_e7(ctx),
        secao_a4(ctx),
        secao_sintese_e8(ctx),
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
