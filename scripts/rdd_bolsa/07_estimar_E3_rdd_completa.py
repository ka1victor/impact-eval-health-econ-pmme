"""E3 do protocolo congelado: RDD sharp completa pelo escore administrativo de IVS.

Implementa a especificacao `E3_rdd_completa` de
`output/rdd_bolsa/protocolo_escore_administrativo.json` (congelado em
14/10/2026). O protocolo nao e alterado por este script; seu SHA-256 e gravado
no status de cada execucao.

Condicao de execucao (falha fechada)
------------------------------------
A RDD so roda com o escore para 100% dos municipios de P1 **e** de P2. Hoje o
escore administrativo so existe para os municipios com especialista ativo
(`output/aquisicao/a07_ivs_administrativo_municipio.csv`), ou seja, a cobertura
e funcao do desfecho. Enquanto faltar escore para qualquer municipio de qualquer
populacao, o script grava `E3_status.json` com status
`AGUARDANDO_ESCORE_COMPLETO` e a cobertura por populacao, remove saidas E3
anteriores e sai **sem ler nenhum outcome**. P1 (principal) e P2 (replicacao)
sao exigidas juntas para que a replicacao nao seja decidida depois de ver P1.

Ordem quando o escore esta completo
-----------------------------------
1. Validacao do escore (unico por municipio, em [0, 1], tres casas decimais).
2. Primeiro estagio: a faixa implicada pelo escore (corte no lado inferior,
   T = 1[s > c]) tem de reproduzir a faixa anunciada em 100% dos municipios de
   P_k; senao, status `PRIMEIRO_ESTAGIO_NAO_SHARP` e nenhum outcome e lido.
3. Diagnosticos sem outcome (gravados antes de qualquer leitura de outcome):
   densidade do escore em P_k no corte (Poisson log-linear em mass points de
   0,001 do protocolo E1), balanco de covariaveis pre e suporte por janela.
4. Outcomes: D_k (relacao nominal de ativos de 09/10/2026, so `co_ibge` e
   `ciclo`) e, em P1, a fracao de celulas CNES-curso do quadro da 1a chamada do
   ciclo 1 com alguma confirmacao ou homologacao (definicao do A4).
5. Estimador: local linear, kernel triangular, h = 0,050 fixo; sensibilidade
   h = 0,030 e 0,080; EP HC1 no nivel do municipio; IC e p pela normal.

O escore e tratado em milesimos inteiros (s_mil = 1000 * s). A janela de
largura h tem lado inferior c-h+0,001..c (o proprio corte incluido) e lado
superior c+0,001..c+h, como no E1. No local linear, o peso triangular e
max(0, 1 - |s - c| / h).

Contraste identificado: incentivo marginal anunciado de R$ 5 mil em cada corte
(possivelmente um pacote, se outra politica mudar no mesmo corte). Nao e efeito
da participacao no PMM-E nem do Agora Tem Especialistas.

Uso
---
    python3 scripts/rdd_bolsa/07_estimar_E3_rdd_completa.py
    python3 scripts/rdd_bolsa/07_estimar_E3_rdd_completa.py --escore CAMINHO.csv

`--escore` aceita um CSV com as colunas `co_ibge` e `ivs_admin`.

As funcoes sao importaveis para o teste sintetico
(`tests/test_e3_rdd_sintetico.py`). Dados sinteticos so podem ser gravados
fora de `output/` e `data/` (guarda em `executar`).
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

PROTOCOLO = ROOT / "output" / "rdd_bolsa" / "protocolo_escore_administrativo.json"
ESCORE_PADRAO = ROOT / "output" / "aquisicao" / "a07_ivs_administrativo_municipio.csv"
IVS_PUBLICO = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
ATIVOS_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
FUNIL = ROOT / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"
SAIDA_DIR = ROOT / "output" / "rdd_bolsa"

NOME_STATUS = "E3_status.json"
NOME_DIAGNOSTICOS = "E3_diagnosticos.csv"
NOME_ESTIMATIVAS = "E3_estimativas.csv"

# SHA-256 da Relacao Nominal Ativos - PMM-E de 09/10/2026 no manifesto a07 no
# congelamento do protocolo. Outra versao do arquivo nao e o outcome do protocolo.
SHA256_ATIVOS_PROTOCOLO = "e57edeb50946395fa90fe510f4a658501f9b0e92069fcc53aa41b9e893e89c1c"

POPULACOES = {
    "P1": {
        "papel": "principal",
        "ciclo": 1,
        "quadros": ["data/raw/aquisicao/vagas/2025_ciclo1_chamada1_vagas.xlsx"],
    },
    "P2": {
        "papel": "replicacao",
        "ciclo": 2,
        "quadros": [
            "data/raw/pmm_e/2026_ciclo2_chamada1_vagas_retificadas.xlsx",
            "data/raw/pmm_e/2026_ciclo2_chamada2_vagas.xlsx",
        ],
    },
}

CORTES_MIL = (300, 400)
H_PRINCIPAL_MIL = 50
H_SENSIBILIDADE_MIL = (30, 80)
JANELAS_MIL = (H_PRINCIPAL_MIL,) + H_SENSIBILIDADE_MIL
SALTO_ANUNCIADO_BRL = 5_000
Z_975 = 1.959963984540054

COVARIAVEIS_IVS = ["ivs_2010", "ivs_infra_2010", "ivs_ch_2010", "ivs_rt_2010", "log_populacao_2010", "rdpc_2010"]

OUTCOME_D = "D_k_especialista_ativo_do_ciclo"
OUTCOME_PREENCHIMENTO = "fracao_celulas_ch1_com_confirmacao_ou_homologacao"

CONTRASTE = (
    "incentivo marginal anunciado de R$ 5 mil (Faixa 3->2 em 0,300; Faixa 2->1 em 0,400), "
    "possivelmente pacote se outra politica mudar no mesmo corte; nao e efeito do PMM-E "
    "nem do Agora Tem Especialistas"
)


class EscoreInvalido(ValueError):
    """Escore estruturalmente invalido: o script nao estima nada."""


# ---------------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(65536):
            h.update(bloco)
    return h.hexdigest()


def rotulo(path: Path) -> str:
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def normalizar_ibge(serie: pd.Series) -> pd.Series:
    """Seis primeiros digitos do codigo IBGE (aceita 6 ou 7 digitos)."""
    return serie.astype(str).str.split(".").str[0].str.replace(r"\D", "", regex=True).str[:6]


def p_normal(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0)) if math.isfinite(z) else float("nan")


def faixa_por_mil(s_mil: int) -> str:
    """Regra do protocolo: o corte pertence ao lado inferior."""
    if s_mil <= CORTES_MIL[0]:
        return "FAIXA 3"
    if s_mil <= CORTES_MIL[1]:
        return "FAIXA 2"
    return "FAIXA 1"


# ---------------------------------------------------------------------------
# Leitura de quadros e do escore (sem outcome)
# ---------------------------------------------------------------------------

def ler_quadro(caminho: Path) -> pd.DataFrame:
    """Copia da leitura de quadros de `04_portao_r1_escore_administrativo.py`."""
    bruto = pd.read_excel(caminho, header=None)
    linha = next(
        i for i in range(10) if bruto.iloc[i].astype(str).str.upper().str.contains("FAIXA").any()
    )
    df = pd.read_excel(caminho, header=linha)
    df.columns = [str(c).strip().upper() for c in df.columns]
    col_ibge = next(c for c in df.columns if c.startswith("IBGE"))
    col_faixa = next(c for c in df.columns if "FAIXA" in c)
    m = df[[col_ibge, col_faixa]].dropna()
    m.columns = ["co_ibge", "faixa_anunciada"]
    m["co_ibge"] = m["co_ibge"].astype(str).str.split(".").str[0].str[:6]
    m = m[m["co_ibge"].str.isnumeric()]
    m["faixa_anunciada"] = m["faixa_anunciada"].astype(str).str.strip().str.upper()
    return m.drop_duplicates()


def carregar_populacoes(root: Path = ROOT) -> dict[str, pd.DataFrame]:
    """P_k: municipios (com a faixa anunciada em cada quadro) da uniao dos quadros."""
    pops = {}
    for nome, spec in POPULACOES.items():
        partes = [ler_quadro(root / q) for q in spec["quadros"]]
        pops[nome] = (
            pd.concat(partes, ignore_index=True)
            .drop_duplicates()
            .sort_values(["co_ibge", "faixa_anunciada"])
            .reset_index(drop=True)
        )
    return pops


def ler_escore(caminho: Path) -> pd.DataFrame:
    """Le `co_ibge`, `ivs_admin` e devolve o escore em milesimos inteiros.

    Linhas sem valor contam como municipio sem escore (nao como zero).
    """
    bruto = pd.read_csv(caminho, dtype=str)
    faltando = {"co_ibge", "ivs_admin"} - set(bruto.columns)
    if faltando:
        raise EscoreInvalido(f"colunas ausentes no escore: {sorted(faltando)}")
    return validar_escore(bruto[["co_ibge", "ivs_admin"]])


def validar_escore(bruto: pd.DataFrame) -> pd.DataFrame:
    df = bruto.copy()
    df["co_ibge"] = normalizar_ibge(df["co_ibge"])
    if (df["co_ibge"].str.len() != 6).any():
        raise EscoreInvalido("co_ibge com menos de 6 digitos")
    texto = df["ivs_admin"].astype("string").str.strip().str.replace(",", ".", regex=False)
    valor = pd.to_numeric(texto.replace("", pd.NA), errors="coerce")
    nao_numerico = texto.notna() & (texto != "") & valor.isna()
    if nao_numerico.any():
        raise EscoreInvalido(f"{int(nao_numerico.sum())} valores de ivs_admin nao numericos")
    df["ivs_admin"] = valor.astype(float)
    df = df.dropna(subset=["ivs_admin"]).drop_duplicates()
    if df["co_ibge"].duplicated().any():
        raise EscoreInvalido("municipio com mais de um escore")
    if ((df["ivs_admin"] < 0) | (df["ivs_admin"] > 1)).any():
        raise EscoreInvalido("ivs_admin fora de [0, 1]")
    mil = df["ivs_admin"] * 1000
    if (np.abs(mil - np.round(mil)) > 1e-6).any():
        raise EscoreInvalido(
            "ivs_admin com mais de tres casas decimais: arredondar a milesimos mudaria a faixa "
            "perto do corte; o protocolo fixa tres casas"
        )
    df["s_mil"] = np.round(mil).astype(int)
    return df[["co_ibge", "ivs_admin", "s_mil"]].sort_values("co_ibge").reset_index(drop=True)


def cobertura(populacoes: dict[str, pd.DataFrame], escore: pd.DataFrame) -> dict:
    com = set(escore["co_ibge"])
    out = {}
    for nome, pop in populacoes.items():
        municipios = pop.drop_duplicates("co_ibge")
        tem = municipios["co_ibge"].isin(com)
        por_faixa = {}
        for faixa, g in pop.groupby("faixa_anunciada"):
            t = g.drop_duplicates("co_ibge")["co_ibge"].isin(com)
            por_faixa[faixa] = {
                "municipios": int(len(t)),
                "com_escore": int(t.sum()),
                "pct": round(100 * float(t.mean()), 1),
            }
        out[nome] = {
            "papel": POPULACOES.get(nome, {}).get("papel"),
            "municipios": int(len(municipios)),
            "com_escore": int(tem.sum()),
            "sem_escore": int((~tem).sum()),
            "pct": round(100 * float(tem.mean()), 1) if len(tem) else 0.0,
            "por_faixa_anunciada": por_faixa,
            "completa": bool(len(tem) > 0 and tem.all()),
        }
    return out


def primeiro_estagio(pop: pd.DataFrame, escore: pd.DataFrame) -> dict:
    """Faixa pelo escore contra faixa anunciada (todas as faixas de cada municipio)."""
    m = pop.merge(escore[["co_ibge", "s_mil"]], on="co_ibge", how="inner")
    m["bate"] = m["faixa_anunciada"] == m["s_mil"].map(faixa_por_mil)
    por_mun = m.groupby("co_ibge").agg(n_faixas=("faixa_anunciada", "nunique"), bate=("bate", "all"))
    reproduzidos = int((por_mun["bate"] & (por_mun["n_faixas"] == 1)).sum())
    return {
        "municipios": int(len(por_mun)),
        "reproduzidos": reproduzidos,
        "municipios_com_mais_de_uma_faixa": int((por_mun["n_faixas"] > 1).sum()),
        "sharp": bool(len(por_mun) > 0 and reproduzidos == len(por_mun)),
    }


# ---------------------------------------------------------------------------
# Estimadores (numpy)
# ---------------------------------------------------------------------------

def _janela(x_mil: np.ndarray, h_mil: int) -> np.ndarray:
    return (x_mil > -h_mil) & (x_mil <= h_mil)


def suporte(s_mil, corte_mil: int, h_mil: int) -> dict:
    s = np.asarray(s_mil, dtype=int)
    x = s - corte_mil
    ab = (x > -h_mil) & (x <= 0)
    ac = (x > 0) & (x <= h_mil)
    return {
        "n_abaixo": int(ab.sum()),
        "n_acima": int(ac.sum()),
        "mass_points_abaixo": int(np.unique(s[ab]).size),
        "mass_points_acima": int(np.unique(s[ac]).size),
    }


def rdd_local_linear(s_mil, y, corte_mil: int, h_mil: int) -> dict:
    """RDD sharp local linear, kernel triangular, EP HC1 (uma linha por municipio).

    y = a + b*x + tau*T + d*T*x por MQP com pesos max(0, 1 - |x|/h), x = s - c
    (em unidades de IVS), T = 1[s > c]. tau e o salto em E[y|s] no corte.
    """
    s = np.asarray(s_mil, dtype=int)
    yv = np.asarray(y, dtype=float)
    x_mil = s - corte_mil
    w = np.clip(1.0 - np.abs(x_mil) / h_mil, 0.0, None)
    usa = _janela(x_mil, h_mil) & (w > 0) & np.isfinite(yv)
    abaixo = usa & (x_mil <= 0)
    acima = usa & (x_mil > 0)
    res = {
        "n_abaixo": int(abaixo.sum()),
        "n_acima": int(acima.sum()),
        "mass_points_abaixo": int(np.unique(s[abaixo]).size),
        "mass_points_acima": int(np.unique(s[acima]).size),
        "media_bruta_abaixo": float(yv[abaixo].mean()) if abaixo.any() else float("nan"),
        "media_bruta_acima": float(yv[acima].mean()) if acima.any() else float("nan"),
        "tau": float("nan"),
        "ep": float("nan"),
        "ic95_inf": float("nan"),
        "ic95_sup": float("nan"),
        "p_valor": float("nan"),
        "nota": "",
    }
    if res["mass_points_abaixo"] < 2 or res["mass_points_acima"] < 2:
        res["nota"] = "suporte insuficiente: menos de 2 mass points com peso positivo em algum lado"
        return res
    xs = x_mil[usa] / 1000.0
    t = (x_mil[usa] > 0).astype(float)
    X = np.column_stack([np.ones_like(xs), xs, t, t * xs])
    W = w[usa]
    yy = yv[usa]
    n, k = X.shape
    if n <= k:
        res["nota"] = "graus de liberdade insuficientes"
        return res
    XtWX = X.T @ (X * W[:, None])
    bread = np.linalg.inv(XtWX)
    beta = bread @ (X.T @ (W * yy))
    e = yy - X @ beta
    score = X * (W * e)[:, None]
    V = bread @ (score.T @ score) @ bread * (n / (n - k))
    tau = float(beta[2])
    ep = float(math.sqrt(max(V[2, 2], 0.0)))
    res.update({"tau": tau, "ep": ep, "ic95_inf": tau - Z_975 * ep, "ic95_sup": tau + Z_975 * ep})
    if ep > 0:
        res["p_valor"] = p_normal(tau / ep)
    else:
        res["nota"] = "EP nulo: outcome sem variacao residual na janela"
    return res


def densidade_poisson(s_mil, corte_mil: int, h_mil: int, max_iter: int = 200, tol: float = 1e-10) -> dict:
    """Estimador principal do E1 aplicado a todos os municipios de P_k.

    Contagem de municipios em cada mass point de 0,001 da janela (inclusive os
    vazios): log mu(s) = a + b*x + tau*T + d*T*x; rho = exp(tau); EP sanduiche
    HC0; IC e p pela normal.
    """
    s = np.asarray(s_mil, dtype=int)
    grade = np.arange(corte_mil - h_mil + 1, corte_mil + h_mil + 1)
    valores, contagens = np.unique(s, return_counts=True)
    mapa = dict(zip(valores.tolist(), contagens.tolist()))
    y = np.array([mapa.get(g, 0) for g in grade], dtype=float)
    x = (grade - corte_mil) / 1000.0
    t = (grade > corte_mil).astype(float)
    res = {
        "n_abaixo": int(y[t == 0].sum()),
        "n_acima": int(y[t == 1].sum()),
        "mass_points_abaixo": int((y[t == 0] > 0).sum()),
        "mass_points_acima": int((y[t == 1] > 0).sum()),
        "tau": float("nan"),
        "ep": float("nan"),
        "ic95_inf": float("nan"),
        "ic95_sup": float("nan"),
        "p_valor": float("nan"),
        "rho": float("nan"),
        "rho_ic95_inf": float("nan"),
        "rho_ic95_sup": float("nan"),
        "nota": "",
    }
    if res["n_abaixo"] == 0 or res["n_acima"] == 0:
        res["nota"] = "lado sem municipios: razao de densidades nao identificada"
        return res
    X = np.column_stack([np.ones_like(x), x, t, t * x])
    mu = y + 0.5
    eta = np.log(mu)
    beta = np.linalg.lstsq(X, eta, rcond=None)[0]
    convergiu = False
    for _ in range(max_iter):
        eta = X @ beta
        mu = np.exp(eta)
        z = eta + (y - mu) / mu
        XtWX = X.T @ (X * mu[:, None])
        novo = np.linalg.solve(XtWX, X.T @ (mu * z))
        if np.max(np.abs(novo - beta)) < tol:
            beta = novo
            convergiu = True
            break
        beta = novo
    if not convergiu:
        res["nota"] = "IRLS nao convergiu"
        return res
    mu = np.exp(X @ beta)
    bread = np.linalg.inv(X.T @ (X * mu[:, None]))
    sc = X * (y - mu)[:, None]
    V = bread @ (sc.T @ sc) @ bread
    tau = float(beta[2])
    ep = float(math.sqrt(max(V[2, 2], 0.0)))
    res.update(
        {
            "tau": tau,
            "ep": ep,
            "ic95_inf": tau - Z_975 * ep,
            "ic95_sup": tau + Z_975 * ep,
            "p_valor": p_normal(tau / ep) if ep > 0 else float("nan"),
            "rho": math.exp(tau),
            "rho_ic95_inf": math.exp(tau - Z_975 * ep),
            "rho_ic95_sup": math.exp(tau + Z_975 * ep),
        }
    )
    return res


# ---------------------------------------------------------------------------
# Covariaveis pre (sem outcome)
# ---------------------------------------------------------------------------

def carregar_covariaveis(root: Path = ROOT) -> tuple[pd.DataFrame, dict]:
    notas: dict = {}
    ivs = pd.read_csv(root / "data" / "ivs_ipea_2010_municipios.csv", dtype={"cod_ibge6": str})
    ivs["co_ibge"] = normalizar_ibge(ivs["cod_ibge6"]).str.zfill(6)
    pop = pd.to_numeric(ivs["populacao_2010"], errors="coerce")
    ivs["log_populacao_2010"] = np.where(pop > 0, np.log(pop.where(pop > 0)), np.nan)
    cov = ivs[["co_ibge"] + [c for c in COVARIAVEIS_IVS]].copy()
    notas[rotulo(root / "data" / "ivs_ipea_2010_municipios.csv")] = {
        "sha256": sha256(root / "data" / "ivs_ipea_2010_municipios.csv"),
        "colunas": ["cod_ibge6", "ivs_2010", "ivs_infra_2010", "ivs_ch_2010", "ivs_rt_2010",
                    "populacao_2010", "rdpc_2010"],
    }
    tip_path = root / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
    try:
        tip = pd.read_parquet(tip_path, columns=["co_ibge_6d", "estrato"])
        tip["co_ibge"] = tip["co_ibge_6d"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(6)
        estratos = sorted(tip["estrato"].dropna().astype(str).unique())
        for e in estratos:
            tip[f"estrato_{e}"] = np.where(tip["estrato"].isna(), np.nan, (tip["estrato"].astype(str) == e).astype(float))
        cov = cov.merge(tip[["co_ibge"] + [f"estrato_{e}" for e in estratos]], on="co_ibge", how="left")
        notas[rotulo(tip_path)] = {"sha256": sha256(tip_path), "status": "lido", "estratos": estratos}
    except Exception as erro:  # pyarrow/fastparquet podem faltar
        notas[rotulo(tip_path)] = {
            "status": "nao_lido",
            "motivo": f"{type(erro).__name__}: {erro}",
            "efeito": "balanco do estrato territorial nao calculado; demais covariaveis inalteradas",
        }
    return cov, notas


# ---------------------------------------------------------------------------
# Outcomes (so lidos depois dos diagnosticos, e so com escore completo)
# ---------------------------------------------------------------------------

_CICLO = re.compile(r"(?:ciclo\s*)?0*(\d{1,2})(?:[.,]0+)?", re.IGNORECASE)


def parse_ciclo(valor) -> int | None:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return None
    m = _CICLO.fullmatch(str(valor).strip())
    if not m:
        return None
    k = int(m.group(1))
    return k if 1 <= k <= 20 else None


def ler_ativos(zip_path: Path) -> pd.DataFrame:
    """Le apenas `co_ibge` e `ciclo` da relacao nominal (CSV ';' latin1 no zip).

    Ciclo nao reconhecido ou ausente falha fechado: a pessoa nao pode ser
    atribuida a um ciclo e D_k ficaria indefinido.
    """
    with zipfile.ZipFile(zip_path) as z:
        nomes = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(nomes) != 1:
            raise ValueError(f"esperado um CSV no zip, encontrados {len(nomes)}")
        bruto = z.read(nomes[0])
    df = pd.read_csv(io.BytesIO(bruto), sep=";", dtype=str, encoding="latin1", usecols=["co_ibge", "ciclo"])
    df["co_ibge"] = normalizar_ibge(df["co_ibge"])
    df["ciclo_k"] = df["ciclo"].map(parse_ciclo)
    invalidos = df[df["ciclo_k"].isna()]["ciclo"]
    if len(invalidos):
        exemplos = sorted({str(v) for v in invalidos.unique()})[:10]
        raise ValueError(f"{len(invalidos)} registros com ciclo nao reconhecido: {exemplos}")
    if (df["co_ibge"].str.len() != 6).any():
        raise ValueError("co_ibge invalido na relacao nominal")
    return df[["co_ibge", "ciclo_k"]].astype({"ciclo_k": int}).drop_duplicates()


def construir_d_k(municipios: pd.Series, ativos: pd.DataFrame, k: int) -> pd.Series:
    com_k = set(ativos.loc[ativos["ciclo_k"] == k, "co_ibge"])
    mun = pd.Index(sorted(set(municipios)), name="co_ibge")
    return pd.Series([1.0 if m in com_k else 0.0 for m in mun], index=mun, name=f"D_{k}")


def ler_funil(path: Path) -> pd.DataFrame:
    return pd.read_parquet(
        path,
        columns=["chamada", "in_quadro_ch1_original", "co_ibge_6d", "co_cnes_7d", "cod_curso",
                 "outcome_alguma_confirmacao_ou_homologacao"],
    )


def preenchimento_ch1_por_municipio(funil: pd.DataFrame, municipios_p1: pd.Series) -> pd.Series:
    """Fracao de celulas CNES-curso do quadro Ch1 com alguma confirmacao ou homologacao.

    Celulas = linhas da matriz do funil (A1) com chamada == 1 e
    in_quadro_ch1_original (a amostra primaria do A4, 1.295 celulas). O outcome
    da celula e `outcome_alguma_confirmacao_ou_homologacao`, como no A4.
    Municipio de P1 sem celula, ou celula fora de P1, falha fechado.
    """
    flag = funil["in_quadro_ch1_original"].fillna(False).astype(bool)
    c = funil[(pd.to_numeric(funil["chamada"]) == 1) & flag].copy()
    if c.duplicated(["co_cnes_7d", "cod_curso"]).any():
        raise ValueError("celula CNES-curso duplicada no quadro Ch1")
    c["co_ibge"] = normalizar_ibge(c["co_ibge_6d"]).str.zfill(6)
    y = pd.to_numeric(c["outcome_alguma_confirmacao_ou_homologacao"], errors="raise").astype(float)
    if not y.isin([0.0, 1.0]).all():
        raise ValueError("outcome de celula fora de {0, 1}")
    c["y"] = y
    frac = c.groupby("co_ibge")["y"].mean()
    p1 = set(municipios_p1)
    sem_celula = p1 - set(frac.index)
    fora = set(frac.index) - p1
    if sem_celula or fora:
        raise ValueError(
            f"celulas do funil nao casam com P1: {len(sem_celula)} municipios de P1 sem celula, "
            f"{len(fora)} municipios com celula fora de P1"
        )
    frac.index.name = "co_ibge"
    return frac.rename(OUTCOME_PREENCHIMENTO).sort_index()


def carregar_outcomes_reais(root: Path = ROOT) -> Callable[[str, pd.Series], list[dict]]:
    """Devolve o leitor de outcomes empiricos; nada e lido ate ele ser chamado."""
    cache: dict = {}

    def ativos() -> pd.DataFrame:
        if "ativos" not in cache:
            zp = root / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
            h = sha256(zp)
            if h != SHA256_ATIVOS_PROTOCOLO:
                raise ValueError(
                    f"relacao nominal com SHA-256 {h}, diferente da versao de 09/10/2026 fixada no protocolo"
                )
            cache["ativos"] = ler_ativos(zp)
        return cache["ativos"]

    def leitor(nome_pop: str, municipios: pd.Series) -> list[dict]:
        k = POPULACOES[nome_pop]["ciclo"]
        itens = []
        try:
            itens.append({"outcome": OUTCOME_D, "ciclo": k, "serie": construir_d_k(municipios, ativos(), k),
                          "fonte": rotulo(root / "data/raw/aquisicao/ivs_administrativo/tb_profissionais_ativos_pmme_csv.zip")})
        except Exception as erro:
            itens.append({"outcome": OUTCOME_D, "ciclo": k, "serie": None,
                          "motivo": f"{type(erro).__name__}: {erro}"})
        if nome_pop == "P1":
            fp = root / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"
            try:
                serie = preenchimento_ch1_por_municipio(ler_funil(fp), municipios)
                itens.append({"outcome": OUTCOME_PREENCHIMENTO, "ciclo": 1, "serie": serie,
                              "fonte": rotulo(fp), "sha256": sha256(fp)})
            except Exception as erro:  # pyarrow pode faltar
                itens.append({"outcome": OUTCOME_PREENCHIMENTO, "ciclo": 1, "serie": None,
                              "motivo": f"{type(erro).__name__}: {erro}"})
        return itens

    return leitor


# ---------------------------------------------------------------------------
# Execucao
# ---------------------------------------------------------------------------

def _guarda_saida(saida_dir: Path, natureza: str, root: Path) -> None:
    if natureza == "EMPIRICO":
        return
    alvo = Path(saida_dir).resolve()
    for proibido in (root / "output", root / "data"):
        p = proibido.resolve()
        if alvo == p or p in alvo.parents:
            raise ValueError(f"dados {natureza} nao podem ser gravados em {rotulo(p)}")


def _gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _remover_saidas_antigas(saida_dir: Path) -> list[str]:
    removidas = []
    for nome in (NOME_DIAGNOSTICOS, NOME_ESTIMATIVAS):
        p = saida_dir / nome
        if p.exists():
            p.unlink()
            removidas.append(nome)
    return removidas


def diagnosticos_sem_outcome(pop_s: pd.DataFrame, covariaveis: pd.DataFrame | None, nome_pop: str) -> pd.DataFrame:
    """Suporte, densidade e balanco; recebe so escore e covariaveis pre."""
    linhas = []
    s = pop_s["s_mil"].to_numpy()
    cov = (
        pop_s[["co_ibge", "s_mil"]].merge(covariaveis, on="co_ibge", how="left", validate="many_to_one")
        if covariaveis is not None else None
    )
    colunas_cov = [c for c in (covariaveis.columns if covariaveis is not None else []) if c != "co_ibge"]
    for corte in CORTES_MIL:
        for h in JANELAS_MIL:
            esp = "principal" if h == H_PRINCIPAL_MIL else "sensibilidade"
            base = {"populacao": nome_pop, "corte": corte / 1000, "h": h / 1000, "especificacao": esp}
            linhas.append({**base, "diagnostico": "suporte", "variavel": "municipios_e_mass_points",
                           **suporte(s, corte, h)})
            d = densidade_poisson(s, corte, h)
            linhas.append({**base, "diagnostico": "densidade_poisson_mass_points", "variavel": "escore_ivs_admin",
                           "metrica": "tau = log(rho); rho = razao das densidades lateral superior/inferior", **d})
            for c in colunas_cov:
                r = rdd_local_linear(cov["s_mil"].to_numpy(), cov[c].to_numpy(dtype=float), corte, h)
                linhas.append({**base, "diagnostico": "balanco_covariavel_pre", "variavel": c,
                               "metrica": "salto local linear (kernel triangular, HC1)", **r})
    return pd.DataFrame(linhas)


def estimar_outcomes(pop_s: pd.DataFrame, itens: list[dict], nome_pop: str) -> tuple[pd.DataFrame, list[dict]]:
    linhas, situacao = [], []
    for item in itens:
        if item.get("serie") is None:
            situacao.append({"populacao": nome_pop, "outcome": item["outcome"], "ciclo": item["ciclo"],
                             "estimado": False, "motivo": item.get("motivo", "")})
            continue
        serie = item["serie"]
        m = pop_s[["co_ibge", "s_mil"]].merge(serie.rename("y").reset_index(), on="co_ibge", how="left")
        faltam = int(m["y"].isna().sum())
        if faltam:
            situacao.append({"populacao": nome_pop, "outcome": item["outcome"], "ciclo": item["ciclo"],
                             "estimado": False, "motivo": f"{faltam} municipios de {nome_pop} sem outcome"})
            continue
        situacao.append({"populacao": nome_pop, "outcome": item["outcome"], "ciclo": item["ciclo"],
                         "estimado": True, "fonte": item.get("fonte"), "n_municipios": int(len(m))})
        for corte in CORTES_MIL:
            for h in JANELAS_MIL:
                r = rdd_local_linear(m["s_mil"].to_numpy(), m["y"].to_numpy(dtype=float), corte, h)
                linhas.append({
                    "populacao": nome_pop,
                    "papel": POPULACOES.get(nome_pop, {}).get("papel"),
                    "outcome": item["outcome"],
                    "ciclo_outcome": item["ciclo"],
                    "corte": corte / 1000,
                    "salto_anunciado_brl": SALTO_ANUNCIADO_BRL,
                    "h": h / 1000,
                    "especificacao": "principal" if h == H_PRINCIPAL_MIL else "sensibilidade",
                    "estimador": "local linear sharp, kernel triangular, EP HC1 por municipio",
                    **r,
                })
    return pd.DataFrame(linhas), situacao


def executar(
    escore: pd.DataFrame,
    populacoes: dict[str, pd.DataFrame],
    *,
    saida_dir: Path,
    natureza: str,
    carregar_covariaveis_fn: Callable[[], tuple[pd.DataFrame | None, dict]],
    carregar_outcomes_fn: Callable[[str, pd.Series], list[dict]],
    meta: dict | None = None,
    root: Path = ROOT,
) -> dict:
    """Roda o E3; `carregar_outcomes_fn` so e chamado com escore completo e regra sharp."""
    _guarda_saida(saida_dir, natureza, root)
    saida_dir = Path(saida_dir)
    saida_dir.mkdir(parents=True, exist_ok=True)
    status: dict = {
        "etapa": "E3_rdd_completa",
        "natureza_dos_dados": natureza,
        **(meta or {}),
        "outcomes_abertos": False,
        "cortes": [c / 1000 for c in CORTES_MIL],
        "lado_do_corte": "o proprio corte pertence ao lado inferior; T = 1[s > c]",
        "janelas": {"principal": H_PRINCIPAL_MIL / 1000, "sensibilidade": [h / 1000 for h in H_SENSIBILIDADE_MIL]},
        "contraste": CONTRASTE,
    }
    cob = cobertura(populacoes, escore)
    status["cobertura_do_escore"] = cob

    if not all(v["completa"] for v in cob.values()):
        status.update({
            "status": "AGUARDANDO_ESCORE_COMPLETO",
            "motivo": (
                "falta escore para municipios de P1 e/ou P2; o escore publicado so cobre municipios com "
                "especialista ativo, entao a falta e funcao do desfecho e a RDD na subamostra coberta "
                "condicionaria no proprio desfecho"
            ),
            "outcomes_lidos": [],
            "o_que_destrava": "escore `ivs` administrativo para 100% dos municipios de P1 e de P2 (ou para os 5.570)",
            "como_rodar": "python3 scripts/rdd_bolsa/07_estimar_E3_rdd_completa.py --escore <CSV com co_ibge, ivs_admin>",
            "saidas_anteriores_removidas": _remover_saidas_antigas(saida_dir),
        })
        _gravar_json(saida_dir / NOME_STATUS, status)
        return status

    pops_s = {
        nome: pop.drop_duplicates("co_ibge")[["co_ibge"]].merge(escore[["co_ibge", "s_mil"]], on="co_ibge", how="inner")
        .sort_values("co_ibge").reset_index(drop=True)
        for nome, pop in populacoes.items()
    }
    pe = {nome: primeiro_estagio(pop, escore) for nome, pop in populacoes.items()}
    status["primeiro_estagio"] = pe
    if not all(v["sharp"] for v in pe.values()):
        status.update({
            "status": "PRIMEIRO_ESTAGIO_NAO_SHARP",
            "motivo": "a faixa implicada pelo escore nao reproduz a faixa anunciada em 100% dos municipios",
            "outcomes_lidos": [],
            "saidas_anteriores_removidas": _remover_saidas_antigas(saida_dir),
        })
        _gravar_json(saida_dir / NOME_STATUS, status)
        return status

    # (a) Diagnosticos sem outcome, gravados antes de qualquer leitura de outcome.
    covariaveis, notas_cov = carregar_covariaveis_fn()
    status["covariaveis_pre"] = notas_cov
    diag = pd.concat(
        [diagnosticos_sem_outcome(pops_s[nome], covariaveis, nome) for nome in pops_s], ignore_index=True
    )
    diag.insert(0, "natureza_dos_dados", natureza)
    diag.to_csv(saida_dir / NOME_DIAGNOSTICOS, index=False)

    # (b) Outcomes.
    estimativas, situacao = [], []
    for nome, pop_s in pops_s.items():
        itens = carregar_outcomes_fn(nome, pop_s["co_ibge"])
        est, sit = estimar_outcomes(pop_s, itens, nome)
        estimativas.append(est)
        situacao.extend(sit)
    est = pd.concat(estimativas, ignore_index=True) if estimativas else pd.DataFrame()
    est.insert(0, "natureza_dos_dados", natureza)
    est.to_csv(saida_dir / NOME_ESTIMATIVAS, index=False)

    principais = est[est["especificacao"] == "principal"] if len(est) else est
    status.update({
        "status": "CONCLUIDO" if all(s["estimado"] for s in situacao) else "CONCLUIDO_COM_OUTCOME_PENDENTE",
        "outcomes_abertos": True,
        "outcomes_lidos": situacao,
        "diagnosticos": NOME_DIAGNOSTICOS,
        "estimativas": NOME_ESTIMATIVAS,
        "resumo_principal": [
            {k: (None if isinstance(v, float) and math.isnan(v) else v)
             for k, v in r.items() if k in ("populacao", "outcome", "corte", "h", "n_abaixo", "n_acima",
                                            "tau", "ep", "ic95_inf", "ic95_sup", "p_valor")}
            for r in principais.to_dict("records")
        ],
        "regra_de_relato": "todas as especificacoes sao relatadas; nenhuma janela, corte, outcome ou amostra reescolhido",
    })
    _gravar_json(saida_dir / NOME_STATUS, status)
    return status


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--escore", type=Path, default=ESCORE_PADRAO,
                    help="CSV com co_ibge e ivs_admin (padrao: saida do a07, escore parcial)")
    args = ap.parse_args(argv)

    protocolo = json.loads(PROTOCOLO.read_text(encoding="utf-8"))
    if sorted(protocolo["running_variable"]["cortes"]) != [f"{c / 1000:.3f}" for c in CORTES_MIL]:
        raise SystemExit("cortes do script divergem do protocolo congelado")
    escore_path = args.escore.resolve()
    meta = {
        "protocolo": {
            "arquivo": rotulo(PROTOCOLO),
            "sha256": sha256(PROTOCOLO),
            "data_congelamento": protocolo.get("data_congelamento"),
            "condicao": protocolo["E3_rdd_completa"]["condicao"],
        },
        "escore": {"arquivo": rotulo(escore_path), "sha256": sha256(escore_path)},
        "populacoes": {
            nome: {"papel": spec["papel"], "ciclo_do_outcome": spec["ciclo"],
                   "quadros": {q: sha256(ROOT / q) for q in spec["quadros"]}}
            for nome, spec in POPULACOES.items()
        },
    }
    try:
        escore = ler_escore(escore_path)
    except EscoreInvalido as erro:
        SAIDA_DIR.mkdir(parents=True, exist_ok=True)
        status = {"etapa": "E3_rdd_completa", "natureza_dos_dados": "EMPIRICO", **meta,
                  "status": "ESCORE_INVALIDO", "motivo": str(erro), "outcomes_abertos": False,
                  "outcomes_lidos": [], "saidas_anteriores_removidas": _remover_saidas_antigas(SAIDA_DIR)}
        _gravar_json(SAIDA_DIR / NOME_STATUS, status)
        print(json.dumps({"status": status["status"], "motivo": status["motivo"]}, ensure_ascii=False))
        return 1
    meta["escore"]["municipios_com_escore"] = int(len(escore))

    status = executar(
        escore,
        carregar_populacoes(ROOT),
        saida_dir=SAIDA_DIR,
        natureza="EMPIRICO",
        carregar_covariaveis_fn=lambda: carregar_covariaveis(ROOT),
        carregar_outcomes_fn=carregar_outcomes_reais(ROOT),
        meta=meta,
    )
    print(json.dumps({"status": status["status"],
                      "cobertura": {k: {c: v[c] for c in ("municipios", "com_escore", "pct")}
                                    for k, v in status["cobertura_do_escore"].items()}},
                     ensure_ascii=False, indent=2))
    return 0 if status["status"] in ("AGUARDANDO_ESCORE_COMPLETO", "CONCLUIDO") else 1


if __name__ == "__main__":
    sys.exit(main())
