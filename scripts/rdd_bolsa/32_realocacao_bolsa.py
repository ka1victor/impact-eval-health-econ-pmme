"""Realocação (protocolo 58): a bolsa das concorrentes desloca candidatos e preenchimento entre vagas?

Protocolo congelado: `docs/06_execucao/58_protocolo_realocacao_bolsa.md` (24/10/2026, antes de abrir qualquer
outcome por exposição), estatuto `EXPLORATORIO_REALOCACAO` (E9, P1 e A3 já vistos).

Pergunta
--------
As células do PMM-E disputam o mesmo grupo de candidatos numa alocação centralizada por nota. Uma célula que
tem, entre as concorrentes próximas do mesmo curso e ciclo, bolsa média mais alta que a sua recebe menos
candidatos de 1ª opção e preenche menos? Se sim, a bolsa desloca médicos entre vagas e a RDD nos cortes, que
compara vizinhos que disputam as mesmas pessoas, viola o SUTVA.

Desenho (protocolo §4–§5)
-------------------------
- Unidade: célula aberta (estabelecimento × curso × ciclo) do quadro da 1ª chamada, ciclos 1–3 empilhados.
- Mercado: mesmo curso e ciclo; principal = mesma região de saúde (CIR oficial do TabNet); sensibilidades =
  raio de 200 km entre centroides do IBGE (R1) e mesma UF (R2).
- Exposição E = bolsa média das concorrentes − bolsa da célula (R$ mil); R3 = fração das concorrentes com
  bolsa maior.
- MQO com faixa própria (2 indicadores), spline linear do IVS próprio (nós em 0,300 e 0,400), média da mesma
  spline nas concorrentes, log(1 + nº de concorrentes), efeito fixo de curso × ciclo e as covariáveis do A4
  (log da população 2022, estoques CNES pré das CBO-alvo e de generalistas). EP CR1 por CIR.
- A variação de E que sobra vem dos degraus da bolsa das concorrentes nos cortes.
- Outcomes: R-P1 célula preenchida na 1ª chamada; R-P2 nº de candidatos de 1ª opção (primárias, Holm);
  R-S1 tem candidato de 1ª opção (secundária).
- Sensibilidades R1–R7, por ciclo (C1–C3), placebos PL1 (outros cursos) e PL2 (vagas que só abrem depois),
  MDE com 80% de poder.

O contraste mede o pacote do corte das concorrentes (bolsa +R$ 5 mil e outras regras federais nos mesmos
cortes, auditoria 18) condicional às vagas abertas; não mede participação no PMM-E nem o efeito total do Agora
Tem Especialistas.

Integridade
-----------
Só lê `output/` e, sem alterar, a tabela de CIR e os centroides do IBGE em `data/raw/aquisicao/territorio/`.
O IVS é o oficial do a08, pela função do E9, conferido contra a coluna da célula; o arquivo local de IVS da
auditoria 16 não é lido. O painel CNES é lido só nas competências pré-programa (função do A4). Nada simulado,
imputado ou digitado vira observação; ausente fica ausente, com motivo e contagem; nenhum identificador de
candidato é lido ou gravado; toda saída leva `natureza_dos_dados = EMPIRICO`.

Uso
---
    python3 scripts/rdd_bolsa/32_realocacao_bolsa.py
    python3 scripts/rdd_bolsa/32_realocacao_bolsa.py --atualizar-doc   # só regrava o doc 57g das saídas
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_para_realocacao")
E9 = _importar(DIR_RDD / "16_estimar_E9_escolha.py", "e9_escolha_para_realocacao")
X45 = _importar(DIR_RDD / "19_escolha_heterogeneidade.py", "x4x5_escolha_para_realocacao")
X1 = _importar(DIR_RDD / "17_ponte_pmme_cnes.py", "x1_ponte_para_realocacao")
T24 = _importar(DIR_RDD / "24_abertura_vagas_selecao.py", "abertura_vagas_para_realocacao")

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "58_protocolo_realocacao_bolsa.md"
DOC = ROOT / "docs" / "06_execucao" / "57g_resultados_realocacao.md"
OUT = ROOT / "output" / "rdd_bolsa"
V_CELULA = OUT / "outcomes" / "outcomes_V_celula.parquet"
ARQ_POP = ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
OUT_EST = OUT / "R_estimativas.csv"
OUT_VAR = OUT / "R_variacao_exposicao.csv"
OUT_RESUMO = OUT / "R_resumo.json"
DIR_FIG = OUT / "R_figuras"
FIG_COEF = DIR_FIG / "R_coeficientes.png"
FIG_BINS = DIR_FIG / "R_residuos_principal.png"

# ---------------------------------------------------------------------------
# Parâmetros do protocolo 58 (nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-24"
NATUREZA = "EMPIRICO"
ESTATUTO = "EXPLORATORIO_REALOCACAO"
CICLOS = (1, 2, 3)
CORTES = L.CORTES_MIL                 # (300, 400)
RAIO_KM = 200.0                       # R1
H_VIZINHO_MIL = 50                    # R7: concorrente a até 0,050 de um corte
PASSO_BOLSA = 5.0                     # um degrau de faixa = +R$ 5 mil
ALFA = 0.05
PODER = 0.80
FATOR_MDE = float(stats.norm.ppf(1 - ALFA / 2) + stats.norm.ppf(PODER))   # 2,802
Z95 = float(stats.norm.ppf(0.975))
LIMIAR_MDE_5MIL = {"R_P1": 0.10, "R_P2": 0.25}   # protocolo §9
N_BINS_FIG = 20
COVS = ["log_pop22", "estoque_alvo_pre", "estoque_gen_pre"]
FAIXA_BASE = "FAIXA 3"

OUTCOMES = [
    {"id": "R_P1", "col": "preenchida", "papel": "primaria", "un": "fracao (x100 = p.p.)",
     "desc": "célula preenchida na 1ª chamada (≥ 1 alocado)"},
    {"id": "R_P2", "col": "cand1", "papel": "primaria", "un": "candidatos por célula",
     "desc": "nº de candidatos de 1ª opção da célula"},
    {"id": "R_S1", "col": "tem_cand1", "papel": "secundaria", "un": "fracao (x100 = p.p.)",
     "desc": "célula com ≥ 1 candidato de 1ª opção"},
]
PRIMARIAS = [o["id"] for o in OUTCOMES if o["papel"] == "primaria"]

MERCADOS = {"cir": "mesma região de saúde (CIR)", "raio200": "raio de 200 km entre centroides",
            "uf": "mesma UF"}

# Especificações (protocolo §7 e §8). exp: E (diferença de bolsa) | frac | vizinho | outros_cursos | futuras.
ESPECS = [
    {"id": "PRINCIPAL", "mercado": "cir", "exp": "E", "grau": 1, "covs": True, "cluster": "cir", "ciclos": CICLOS,
     "desc": "CIR, E, ciclos 1–3, cluster CIR, com covariáveis"},
    {"id": "R1", "mercado": "raio200", "exp": "E", "grau": 1, "covs": True, "cluster": "cir", "ciclos": CICLOS,
     "desc": "mercado = raio de 200 km (sensibilidade declarada)"},
    {"id": "R2", "mercado": "uf", "exp": "E", "grau": 1, "covs": True, "cluster": "cir", "ciclos": CICLOS,
     "desc": "mercado = mesma UF"},
    {"id": "R3", "mercado": "cir", "exp": "frac", "grau": 1, "covs": True, "cluster": "cir", "ciclos": CICLOS,
     "desc": "exposição = fração das concorrentes com bolsa maior"},
    {"id": "R4", "mercado": "cir", "exp": "E", "grau": 2, "covs": True, "cluster": "cir", "ciclos": CICLOS,
     "desc": "spline quadrática no IVS próprio e na média das concorrentes"},
    {"id": "R5", "mercado": "cir", "exp": "E", "grau": 1, "covs": True, "cluster": "co_ibge", "ciclos": CICLOS,
     "desc": "cluster por município"},
    {"id": "R6", "mercado": "cir", "exp": "E", "grau": 1, "covs": False, "cluster": "cir", "ciclos": CICLOS,
     "desc": "sem covariáveis, na mesma amostra"},
    {"id": "R7", "mercado": "cir", "exp": "vizinho", "grau": 1, "covs": True, "cluster": "cir", "ciclos": CICLOS,
     "desc": "RDD do vizinho: concorrentes de outro município a até 0,050 de um corte"},
    {"id": "C1", "mercado": "cir", "exp": "E", "grau": 1, "covs": True, "cluster": "cir", "ciclos": (1,),
     "desc": "principal, só o ciclo 1"},
    {"id": "C2", "mercado": "cir", "exp": "E", "grau": 1, "covs": True, "cluster": "cir", "ciclos": (2,),
     "desc": "principal, só o ciclo 2"},
    {"id": "C3", "mercado": "cir", "exp": "E", "grau": 1, "covs": True, "cluster": "cir", "ciclos": (3,),
     "desc": "principal, só o ciclo 3"},
    {"id": "PL1", "mercado": "cir", "exp": "outros_cursos", "grau": 1, "covs": True, "cluster": "cir",
     "ciclos": CICLOS, "desc": "placebo: bolsa média das células de outros cursos na mesma CIR e ciclo"},
    {"id": "PL2", "mercado": "cir", "exp": "futuras", "grau": 1, "covs": True, "cluster": "cir", "ciclos": (1, 2),
     "desc": "placebo: bolsa média das células do mesmo curso na CIR que só abrem em ciclo posterior"},
]
UNIDADE_EXP = {"E": "R$ mil (bolsa média das concorrentes − própria)",
               "frac": "fração das concorrentes com bolsa maior (0 a 1)",
               "vizinho": "R$ mil (5 × fração das concorrentes perto do corte que estão acima dele)",
               "outros_cursos": "R$ mil (bolsa média das células de outros cursos − própria)",
               "futuras": "R$ mil (bolsa média das células que só abrem depois − própria)"}
POR_5MIL = {"E", "vizinho", "outros_cursos", "futuras"}   # exposições em R$ mil (o MDE por R$ 5 mil se aplica)

MOTIVOS = {
    "sem_ivs": "município sem IVS 2010 oficial (a08); célula fora do universo e das concorrentes",
    "sem_cir": "município sem região de saúde na tabela oficial (TabNet); célula fora do universo e das concorrentes",
    "sem_cov": "estoque CNES pré-programa incompleto (a09, 202406–202506) ou população ausente; célula fora da "
               "estimação (continua como concorrente)",
    "sem_conc": "sem concorrente do mesmo curso e ciclo no mercado",
    "sem_vizinho": "sem concorrente de outro município a até 0,050 de um corte (R7)",
    "sem_outros": "sem célula de outro curso no mesmo ciclo e CIR (PL1)",
    "sem_futuras": "sem célula do mesmo curso na CIR que só abre em ciclo posterior (PL2)",
    "ciclo3": "ciclo 3 sem ciclo posterior publicado (PL2)",
}

COMO_LER = {
    "R_coeficientes.png": (
        "Cada ponto é a mudança do outcome da célula quando a bolsa média das concorrentes sobe R$ 5 mil; a barra é "
        "o IC de 95%. Placebos em laranja. A leitura que vale é a da tabela da seção 5, não a de um ponto isolado."),
    "R_residuos_principal.png": (
        "Cada ponto é a média de um grupo de células com exposição parecida, depois de tirar os controles; a reta tem "
        "a inclinação do coeficiente principal. A largura do eixo horizontal é a variação da exposição que sobra "
        "para identificar o efeito."),
}


class FalhaValidacao(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def rel(caminho: Path) -> str:
    return str(Path(caminho).resolve().relative_to(ROOT))


def _nan_none(o):
    if isinstance(o, dict):
        return {str(k): _nan_none(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_nan_none(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not math.isfinite(float(o)) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def gravar_json(caminho: Path, obj: dict) -> None:
    caminho.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bloco_entrada(caminho: Path, papel: str, fonte: str, data_ref: str, cobertura: str, unidade: str, chaves: str,
                  filtros: str) -> dict:
    return {"caminho": rel(caminho), "sha256": sha256(caminho), "bytes": caminho.stat().st_size, "papel": papel,
            "fonte": fonte, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade, "chaves": chaves,
            "filtros": filtros}


def _obj(s: pd.Series) -> np.ndarray:
    return s.astype(str).to_numpy(dtype=object)


# ---------------------------------------------------------------------------
# Insumos
# ---------------------------------------------------------------------------

def carregar() -> dict:
    """Células com IVS oficial, bolsa, CIR, centroide e covariáveis; exclusões com motivo."""
    cel = pd.read_parquet(V_CELULA)
    if not (cel["natureza_dos_dados"] == NATUREZA).all():
        raise FalhaValidacao("outcomes_V_celula com natureza diferente de EMPIRICO")
    if cel.duplicated(["ciclo", "co_cnes_7d", "cod_curso"]).any():
        raise FalhaValidacao("célula repetida (ciclo × estabelecimento × curso)")
    cel = cel.sort_values(["ciclo", "cod_curso", "co_cnes_7d"]).reset_index(drop=True)
    n_total = {int(k): int(v) for k, v in cel.groupby("ciclo").size().items()}
    mapa, diag_mapa = E9.mapa_bolsa_por_faixa()
    ivs = E9.carregar_ivs()
    cel["ivs"] = cel["co_ibge"].map(ivs)
    # IVS da célula = IVS oficial do a08 (onde existe).
    tem = cel["ivs"].notna() & cel["ivs_2010_oficial"].notna()
    if (cel.loc[tem, "ivs"] - cel.loc[tem, "ivs_2010_oficial"]).abs().max() > 1e-12:
        raise FalhaValidacao("IVS da célula difere do IVS oficial do a08")
    if (cel["ivs"].isna() != cel["ivs_2010_oficial"].isna()).any():
        raise FalhaValidacao("presença do IVS da célula difere da do a08")
    cel["s_mil"] = np.round(cel["ivs"].to_numpy() * 1000.0)
    cel["bolsa"] = cel["faixa_anunciada"].map(mapa).astype(float)
    if cel["bolsa"].isna().any():
        raise FalhaValidacao("faixa impressa fora do mapa")
    ok_ivs = cel["ivs"].notna()
    regra = E9.faixa_pela_regra(cel.loc[ok_ivs, "s_mil"].to_numpy())
    if (regra != cel.loc[ok_ivs, "faixa_anunciada"].to_numpy()).any():
        raise FalhaValidacao("faixa impressa difere da regra de dois cortes do IVS oficial")
    # CIR e centroides.
    manifesto_cir = X45.adquirir_cir(False)
    cir, diag_cir = X45.ler_cir()
    cel["cir"] = cel["co_ibge"].map(cir.set_index("co_ibge")["co_cir"])
    coord, diag_coord = X1.ler_coordenadas()
    if diag_coord.get("status") != "OBTIDO":
        raise FalhaValidacao("centroides do IBGE indisponíveis")
    xy = coord.set_index("co_ibge")
    falta_xy = sorted(set(cel["co_ibge"]) - set(xy.index))
    if falta_xy:
        raise FalhaValidacao(f"municípios do quadro sem centroide: {falta_xy}")
    cel["lon"] = cel["co_ibge"].map(xy["lon"]).astype(float)
    cel["lat"] = cel["co_ibge"].map(xy["lat"]).astype(float)
    cel["uf"] = cel["co_ibge"].astype(str).str[:2]
    # Outcomes (mesma construção do A3).
    if cel["n_alocados_ch1"].isna().any() or cel["n_cand_1a_opcao"].isna().any():
        raise FalhaValidacao("outcome ausente em outcomes_V_celula")
    cel["preenchida"] = (cel["n_alocados_ch1"] >= 1).astype(float)
    cel["cand1"] = cel["n_cand_1a_opcao"].astype(float)
    cel["tem_cand1"] = (cel["n_cand_1a_opcao"] > 0).astype(float)
    cel["fe_curso_ciclo"] = "c" + cel["ciclo"].astype(str) + "_curso" + cel["cod_curso"].astype(int).astype(str).str.zfill(2)
    # Covariáveis do A4 (população do Censo 2022 e estoques CNES pré).
    p22 = pd.read_csv(ARQ_POP, dtype={"co_ibge_6d": str})
    p22["co_ibge"] = p22["co_ibge_6d"].str.zfill(6)
    pop = p22.set_index("co_ibge")["populacao_2022"].astype(float)
    cel["log_pop22"] = np.log(cel["co_ibge"].map(pop).where(lambda v: v > 0))
    cov, info_cnes = T24.ler_estoques_cnes(sorted(cel["co_ibge"].astype(str).unique()))
    cov = cov.set_index("co_ibge")
    for c in ("estoque_alvo_pre", "estoque_gen_pre"):
        cel[c] = cel["co_ibge"].map(cov[c]).astype(float)
    # Universo: com IVS e CIR (protocolo §4); covariáveis completas só para estimar.
    motivo = np.full(len(cel), "", dtype=object)
    motivo[cel["ivs"].isna().to_numpy()] = "sem_ivs"
    motivo[(motivo == "") & cel["cir"].isna().to_numpy()] = "sem_cir"
    cel["motivo_universo"] = motivo
    univ = cel[cel["motivo_universo"] == ""].reset_index(drop=True)
    univ["cov_ok"] = univ[COVS].notna().all(axis=1)
    exclusoes = {m: {int(k): int(v) for k, v in cel[cel["motivo_universo"] == m].groupby("ciclo").size().items()}
                 for m in ("sem_ivs", "sem_cir")}
    exclusoes["sem_cov"] = {int(k): int(v) for k, v in univ[~univ["cov_ok"]].groupby("ciclo").size().items()}
    return {"cel": cel, "univ": univ, "n_total": n_total, "mapa": mapa, "diag_mapa": diag_mapa,
            "manifesto_cir": manifesto_cir, "diag_cir": diag_cir, "diag_coord": diag_coord, "cnes": info_cnes,
            "exclusoes": exclusoes,
            "celulas_fora": cel.loc[cel["motivo_universo"] != "", ["ciclo", "co_cnes_7d", "cod_curso", "co_ibge",
                                                                   "motivo_universo"]].to_dict("records")}


# ---------------------------------------------------------------------------
# Mercado e exposição
# ---------------------------------------------------------------------------

def matriz_mercado(a: pd.DataFrame, b: pd.DataFrame, mercado: str) -> np.ndarray:
    """Booleano len(a) × len(b): a célula j de b está no mercado geográfico da célula i de a."""
    if mercado == "cir":
        return _obj(a["cir"])[:, None] == _obj(b["cir"])[None, :]
    if mercado == "uf":
        return _obj(a["uf"])[:, None] == _obj(b["uf"])[None, :]
    if mercado == "raio200":
        d = X1.haversine_km(a["lon"].to_numpy()[:, None], a["lat"].to_numpy()[:, None],
                            b["lon"].to_numpy()[None, :], b["lat"].to_numpy()[None, :])
        return d <= RAIO_KM
    raise ValueError(mercado)


def termos_spline(s_mil: np.ndarray, grau: int) -> pd.DataFrame:
    return E9.base_spline(pd.Series(np.asarray(s_mil, dtype=float)), grau).reset_index(drop=True)


def _resumir(a: pd.DataFrame, b: pd.DataFrame, M: np.ndarray) -> dict[str, np.ndarray]:
    """Médias, sobre as concorrentes (M), da bolsa e da spline do IVS (grau 2 cobre o grau 1)."""
    n = M.sum(axis=1).astype(float)
    den = np.where(n > 0, n, np.nan)
    bb = b["bolsa"].to_numpy(dtype=float)
    out = {"n_conc": n,
           "n_conc_outro_mun": (M & (_obj(a["co_ibge"])[:, None] != _obj(b["co_ibge"])[None, :])).sum(axis=1)
           .astype(float),
           "bolsa_media_conc": (M @ bb) / den,
           "frac_maior": (M & (bb[None, :] > a["bolsa"].to_numpy(dtype=float)[:, None])).sum(axis=1) / den,
           "frac_bolsa_diferente": (M & (bb[None, :] != a["bolsa"].to_numpy(dtype=float)[:, None])).sum(axis=1) / den}
    sp = termos_spline(b["s_mil"].to_numpy(), 2)
    for c in sp.columns:
        out[f"conc_{c}"] = (M @ sp[c].to_numpy()) / den
    return out


def _vizinho(a: pd.DataFrame, b: pd.DataFrame, M: np.ndarray) -> dict[str, np.ndarray]:
    """R7: concorrentes de outro município a até 0,050 de um corte (corte mais próximo; empate → 0,300)."""
    s = b["s_mil"].to_numpy(dtype=float)
    dist = np.abs(s[:, None] - np.array(CORTES, dtype=float)[None, :])
    corte = np.array(CORTES, dtype=float)[np.argmin(dist, axis=1)]
    perto = np.abs(s - corte) <= H_VIZINHO_MIL
    outro = _obj(a["co_ibge"])[:, None] != _obj(b["co_ibge"])[None, :]
    Mv = M & outro & perto[None, :]
    n = Mv.sum(axis=1).astype(float)
    den = np.where(n > 0, n, np.nan)
    acima = (s > corte).astype(float)
    x = (s - corte) / 1000.0 * E9.ESCALA_IVS
    return {"n_vizinho": n, "vizinho_frac_acima": (Mv @ acima) / den,
            "vizinho_x_abaixo": (Mv @ (x * (1 - acima))) / den, "vizinho_x_acima": (Mv @ (x * acima)) / den}


def exposicoes(univ: pd.DataFrame, mercado: str, alvo: str) -> pd.DataFrame:
    """Exposição de cada célula do universo. `alvo`: mesmo_curso | outros_cursos | futuras."""
    partes = []
    if alvo == "mesmo_curso":
        for _, g in univ.groupby(["ciclo", "cod_curso"], sort=True):
            M = matriz_mercado(g, g, mercado)
            np.fill_diagonal(M, False)
            r = _resumir(g, g, M)
            if mercado == "cir":
                r.update(_vizinho(g, g, M))
            partes.append(pd.DataFrame(r, index=g.index))
    elif alvo == "outros_cursos":
        for _, g in univ.groupby("ciclo", sort=True):
            M = matriz_mercado(g, g, mercado) & (g["cod_curso"].to_numpy()[:, None] != g["cod_curso"].to_numpy()[None, :])
            partes.append(pd.DataFrame(_resumir(g, g, M), index=g.index))
    elif alvo == "futuras":
        chaves = {k: set(zip(d["co_cnes_7d"], d["cod_curso"])) for k, d in univ.groupby("ciclo")}
        for k, g in univ.groupby("ciclo", sort=True):
            depois = univ[univ["ciclo"] > k]
            novas = np.array([x not in chaves[k] for x in zip(depois["co_cnes_7d"], depois["cod_curso"])], dtype=bool)
            depois = depois[novas]
            depois = depois.sort_values(["ciclo", "cod_curso", "co_cnes_7d"]).drop_duplicates(
                ["co_cnes_7d", "cod_curso"], keep="first")
            if len(depois) == 0:
                r = {"n_conc": np.full(len(g), np.nan)}
                partes.append(pd.DataFrame(r, index=g.index))
                continue
            M = matriz_mercado(g, depois, mercado) & (g["cod_curso"].to_numpy()[:, None]
                                                      == depois["cod_curso"].to_numpy()[None, :])
            partes.append(pd.DataFrame(_resumir(g, depois, M), index=g.index))
    else:
        raise ValueError(alvo)
    ex = pd.concat(partes).reindex(univ.index)
    ex["E"] = ex["bolsa_media_conc"] - univ["bolsa"]
    return ex


# ---------------------------------------------------------------------------
# Estimação
# ---------------------------------------------------------------------------

def montar_matriz(d: pd.DataFrame, esp: dict) -> tuple[pd.DataFrame, str]:
    """Colunas na ordem: exposição (protegida), controles, efeitos fixos de curso × ciclo, intercepto."""
    grau = esp["grau"]
    cols: dict[str, np.ndarray] = {}
    exp_col = {"E": "E", "frac": "frac_maior", "vizinho": "exp_vizinho", "outros_cursos": "E",
               "futuras": "E"}[esp["exp"]]
    if esp["exp"] == "vizinho":
        cols["exposicao"] = PASSO_BOLSA * d["vizinho_frac_acima"].to_numpy(dtype=float)
    else:
        cols["exposicao"] = d[exp_col].to_numpy(dtype=float)
    faixa = d["faixa_anunciada"].astype(str).to_numpy()
    cols["faixa_2"] = (faixa == "FAIXA 2").astype(float)
    cols["faixa_1"] = (faixa == "FAIXA 1").astype(float)
    sp = termos_spline(d["s_mil"].to_numpy(), grau)
    for c in sp.columns:
        cols[f"proprio_{c}"] = sp[c].to_numpy()
    if esp["exp"] == "vizinho":
        cols["vizinho_x_abaixo"] = d["vizinho_x_abaixo"].to_numpy(dtype=float)
        cols["vizinho_x_acima"] = d["vizinho_x_acima"].to_numpy(dtype=float)
    else:
        for c in sp.columns:
            cols[f"conc_{c}"] = d[f"conc_{c}"].to_numpy(dtype=float)
    cols["log1p_n_conc"] = np.log1p(d["n_conc"].to_numpy(dtype=float))
    if esp["covs"]:
        for c in COVS:
            cols[c] = d[c].to_numpy(dtype=float)
    fe = sorted(d["fe_curso_ciclo"].unique())
    for f in fe[1:]:
        cols[f"fe_{f}"] = (d["fe_curso_ciclo"].to_numpy() == f).astype(float)
    cols["intercepto"] = np.ones(len(d))
    return pd.DataFrame(cols, index=d.index), "exposicao"


def ajustar(d: pd.DataFrame, y: np.ndarray, esp: dict) -> dict:
    """MQO com EP CR1 (cluster do protocolo); devolve coeficiente da exposição, MDE e variação residual."""
    X, nome = montar_matriz(d, esp)
    cl = d["cir"] if esp["cluster"] == "cir" else d["co_ibge"]
    fit = L.mqp_sanduiche(X.to_numpy(), y, np.ones(len(y)), nomes=list(X.columns), protegidas={nome},
                          cluster=_obj(cl))
    if "erro" in fit:
        return {"erro": fit["erro"]}
    j = fit["nomes"].index(nome)
    b = float(fit["beta"][j])
    ep = float(math.sqrt(fit["V"][j, j]))
    G = int(fit["G"])
    # Exposição residualizada nos controles efetivamente usados (Frisch–Waugh).
    outros = [c for c in fit["nomes"] if c != nome]
    Z = X[outros].to_numpy()
    xe = X[nome].to_numpy()
    coef_z, *_ = np.linalg.lstsq(Z, xe, rcond=None)
    res_x = xe - Z @ coef_z
    coef_y, *_ = np.linalg.lstsq(Z, y, rcond=None)
    res_y = y - Z @ coef_y
    var_x = float(np.var(xe))
    r2 = float(1 - np.var(res_x) / var_x) if var_x > 0 else float("nan")
    t = b / ep if ep > 0 else float("nan")
    return {"coef": b, "ep": ep, "ic95_inf": b - Z95 * ep, "ic95_sup": b + Z95 * ep,
            "p": float(2 * stats.norm.sf(abs(t))), "p_t_G1": float(2 * stats.t.sf(abs(t), df=G - 1)),
            "n": int(fit["n"]), "G": G, "k": int(fit["k"]), "descartadas": fit["descartadas"],
            "dp_exposicao": float(np.std(xe, ddof=1)), "dp_exposicao_residual": float(np.std(res_x, ddof=1)),
            "r2_exposicao_controles": r2, "frac_exposicao_nao_nula": float(np.mean(np.abs(xe) > 1e-12)),
            "res_x": res_x, "res_y": res_y}


def amostra_especificacao(univ: pd.DataFrame, ex: pd.DataFrame, esp: dict) -> tuple[pd.DataFrame, dict]:
    """Junta universo e exposição; aplica ciclos, covariáveis e a exigência de concorrente, com contagens."""
    d = pd.concat([univ, ex], axis=1)
    cont: dict[str, dict[int, int]] = {}

    def cortar(mask: np.ndarray, motivo: str):
        nonlocal d
        fora = d[~mask]
        if len(fora):
            cont[motivo] = {int(k): int(v) for k, v in fora.groupby("ciclo").size().items()}
        d = d[mask]

    if esp["exp"] == "futuras":
        cortar(d["ciclo"].isin(esp["ciclos"]).to_numpy() | (d["ciclo"] != 3).to_numpy(), "ciclo3")
    cortar(d["ciclo"].isin(esp["ciclos"]).to_numpy(), "fora_dos_ciclos_da_especificacao")
    cortar(d["cov_ok"].to_numpy(), "sem_cov")
    motivo_conc = {"outros_cursos": "sem_outros", "futuras": "sem_futuras"}.get(esp["exp"], "sem_conc")
    cortar((d["n_conc"].fillna(0) > 0).to_numpy(), motivo_conc)
    if esp["exp"] == "vizinho":
        cortar((d["n_vizinho"].fillna(0) > 0).to_numpy(), "sem_vizinho")
    cont.pop("fora_dos_ciclos_da_especificacao", None)
    return d.copy(), cont


def linha_base(esp: dict, o: dict) -> dict:
    return {"especificacao": esp["id"], "descricao": esp["desc"], "outcome_id": o["id"], "outcome": o["desc"],
            "papel": o["papel"] if esp["id"] == "PRINCIPAL" else
            ("placebo" if esp["id"].startswith("PL") else "sensibilidade" if esp["id"].startswith("R")
             else "por_ciclo"),
            "unidade_outcome": o["un"], "mercado": MERCADOS[esp["mercado"]], "exposicao": esp["exp"],
            "unidade_exposicao": UNIDADE_EXP[esp["exp"]], "ciclos": "+".join(str(c) for c in esp["ciclos"]),
            "grau_spline": esp["grau"], "covariaveis": "sim" if esp["covs"] else "nao",
            "cluster": "CIR" if esp["cluster"] == "cir" else "municipio",
            "estatuto": ESTATUTO, "natureza_dos_dados": NATUREZA}


def estimar_tudo(dados: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    univ = dados["univ"]
    cache: dict[tuple[str, str], pd.DataFrame] = {}
    linhas, variacao, amostras, residuos = [], [], {}, {}
    for esp in ESPECS:
        alvo = {"outros_cursos": "outros_cursos", "futuras": "futuras"}.get(esp["exp"], "mesmo_curso")
        chave = (esp["mercado"], alvo)
        if chave not in cache:
            cache[chave] = exposicoes(univ, esp["mercado"], alvo)
        d, cont = amostra_especificacao(univ, cache[chave], esp)
        amostras[esp["id"]] = {"n_celulas": int(len(d)),
                               "por_ciclo": {int(k): int(v) for k, v in d.groupby("ciclo").size().items()},
                               "fora": cont, "n_cir": int(d["cir"].nunique()), "n_municipios": int(d["co_ibge"].nunique())}
        for o in OUTCOMES:
            ln = linha_base(esp, o)
            y = d[o["col"]].to_numpy(dtype=float)
            r = ajustar(d, y, esp) if len(d) else {"erro": "amostra vazia"}
            if "erro" in r:
                ln.update({"status": "NAO_EXECUTADO", "nota": r["erro"], "n_celulas": int(len(d))})
                linhas.append(ln)
                continue
            fator5 = PASSO_BOLSA if esp["exp"] in POR_5MIL else float("nan")
            ln.update({"status": "EXECUTADO", "nota": ("colunas descartadas por colinearidade: "
                                                       + ", ".join(r["descartadas"])) if r["descartadas"] else "",
                       "n_celulas": r["n"], "n_clusters": r["G"], "n_parametros": r["k"],
                       "media_outcome": float(np.mean(y)), "coef": r["coef"], "ep": r["ep"],
                       "ic95_inf": r["ic95_inf"], "ic95_sup": r["ic95_sup"], "p": r["p"], "p_t_G1": r["p_t_G1"],
                       "coef_por_5mil": r["coef"] * fator5, "ic95_inf_5mil": r["ic95_inf"] * fator5,
                       "ic95_sup_5mil": r["ic95_sup"] * fator5,
                       "mde_por_unidade": FATOR_MDE * r["ep"], "mde_por_5mil": FATOR_MDE * r["ep"] * fator5,
                       "mde_por_dp_residual": FATOR_MDE * r["ep"] * r["dp_exposicao_residual"],
                       "dp_exposicao": r["dp_exposicao"], "dp_exposicao_residual": r["dp_exposicao_residual"],
                       "r2_exposicao_controles": r["r2_exposicao_controles"],
                       "frac_celulas_exposicao_nao_nula": r["frac_exposicao_nao_nula"]})
            linhas.append(ln)
            if esp["id"] == "PRINCIPAL":
                residuos[o["id"]] = (r["res_x"], r["res_y"], r["coef"])
        if len(d):
            xe = montar_matriz(d, esp)[0]["exposicao"].to_numpy()
            variacao.append({"especificacao": esp["id"], "mercado": MERCADOS[esp["mercado"]], "exposicao": esp["exp"],
                             "unidade_exposicao": UNIDADE_EXP[esp["exp"]],
                             "ciclos": "+".join(str(c) for c in esp["ciclos"]), "n_celulas": int(len(d)),
                             "n_conc_mediana": float(np.median(d["n_conc"])), "n_conc_media": float(np.mean(d["n_conc"])),
                             "frac_com_conc_outro_municipio": float(np.mean(d["n_conc_outro_mun"] > 0)),
                             "frac_com_conc_bolsa_diferente": float(np.mean(d["frac_bolsa_diferente"] > 0)),
                             "frac_com_conc_bolsa_maior": float(np.mean(d["frac_maior"] > 0)),
                             "exposicao_media": float(np.mean(xe)), "exposicao_dp": float(np.std(xe, ddof=1)),
                             "exposicao_p10": float(np.quantile(xe, 0.10)), "exposicao_p50": float(np.quantile(xe, 0.50)),
                             "exposicao_p90": float(np.quantile(xe, 0.90)),
                             "estatuto": ESTATUTO, "natureza_dos_dados": NATUREZA})
    est = pd.DataFrame(linhas)
    # Holm nas duas primárias, só na principal.
    est["p_holm"] = np.nan
    m = (est["especificacao"] == "PRINCIPAL") & est["outcome_id"].isin(PRIMARIAS) & (est["status"] == "EXECUTADO")
    if m.sum() == len(PRIMARIAS):
        est.loc[m, "p_holm"] = L.holm(est.loc[m, "p"].to_numpy())
    falta = est["status"] != "EXECUTADO"
    if (falta & (est["nota"].fillna("") == "")).any():
        raise FalhaValidacao("linha não executada sem motivo")
    return est, pd.DataFrame(variacao), {"amostras": amostras, "residuos": residuos}


# ---------------------------------------------------------------------------
# Leitura pré-registrada (protocolo §10)
# ---------------------------------------------------------------------------

def _uma(est: pd.DataFrame, esp: str, oid: str) -> dict | None:
    s = est[(est["especificacao"] == esp) & (est["outcome_id"] == oid) & (est["status"] == "EXECUTADO")]
    return s.iloc[0].to_dict() if len(s) == 1 else None


def classificar(est: pd.DataFrame, oid: str) -> dict:
    p = _uma(est, "PRINCIPAL", oid)
    if p is None:
        return {"classe": "NAO_EXECUTADO", "leitura": "principal não executada"}
    r1, r3 = _uma(est, "R1", oid), _uma(est, "R3", oid)
    pl = [_uma(est, x, oid) for x in ("PL1", "PL2")]
    sig = p["p_holm"] < ALFA
    exclui0 = p["ic95_inf"] > 0 or p["ic95_sup"] < 0
    mesmo_sinal = all(r is not None and np.sign(r["coef"]) == np.sign(p["coef"]) for r in (r1, r3))
    placebos_ok = all(r is not None and r["p"] >= ALFA for r in pl)
    limiar = LIMIAR_MDE_5MIL.get(oid)
    mde_pequeno = limiar is not None and p["mde_por_5mil"] <= limiar
    if sig and p["coef"] < 0 and mesmo_sinal and placebos_ok:
        classe, txt = "DESLOCAMENTO", "evidência de deslocamento"
    elif sig and p["coef"] < 0:
        classe, txt = "NEGATIVO_NAO_ROBUSTO", "sinal negativo não robusto; não é lido como deslocamento"
    elif sig and p["coef"] > 0:
        classe, txt = "CONTRARIO", "contrário à hipótese (coeficiente positivo), sem leitura causal forte"
    elif not exclui0 and mde_pequeno:
        classe, txt = "POUCA_COMPETICAO", "pouca competição local nessa margem"
    elif not exclui0:
        classe, txt = "INCONCLUSIVO", "inconclusivo"
    else:
        classe, txt = "IC_EXCLUI_ZERO_SEM_HOLM", "o IC de 95% exclui zero, mas o p de Holm não passa de 5%; não é lido como evidência"
    return {"classe": classe, "leitura": txt, "p_holm": p["p_holm"], "mde_por_5mil": p["mde_por_5mil"],
            "limiar_mde_5mil": limiar, "mde_pequeno": bool(mde_pequeno), "mesmo_sinal_R1_R3": bool(mesmo_sinal),
            "placebos_p_maior_ou_igual_005": bool(placebos_ok)}


# ---------------------------------------------------------------------------
# Figuras (sem texto de leitura embutido)
# ---------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "r58"})
    return plt


ORDEM_FIG = ["PRINCIPAL", "R1", "R2", "R4", "R5", "R6", "R7", "C1", "C2", "C3", "PL1", "PL2"]


def figuras(est: pd.DataFrame, extra: dict) -> list[dict]:
    plt = _plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    figs = []
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.6), sharey=True)
    for ax, oid, esc, xlab in zip(axes, PRIMARIAS, (100.0, 1.0),
                                  ("célula preenchida (p.p.) por R$ 5 mil", "candidatos de 1ª opção por R$ 5 mil")):
        s = est[(est["outcome_id"] == oid) & est["especificacao"].isin(ORDEM_FIG) & (est["status"] == "EXECUTADO")]
        s = s.set_index("especificacao").reindex(ORDEM_FIG).dropna(subset=["coef"])
        y = np.arange(len(s))[::-1]
        for yi, (eid, r) in zip(y, s.iterrows()):
            cor = "#1b3f73" if eid == "PRINCIPAL" else "#eb6834" if eid.startswith("PL") else "#2a78d6"
            ax.plot([r["ic95_inf_5mil"] * esc, r["ic95_sup_5mil"] * esc], [yi, yi], color=cor, lw=2.0)
            ax.plot([r["coef_por_5mil"] * esc], [yi], "o", color=cor, ms=5)
        ax.axvline(0, color="#52514e", lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels(list(s.index))
        ax.set_xlabel(xlab)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="x", color="#e6e5e0", lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG_COEF, dpi=150, metadata={"Software": None})
    plt.close(fig)
    figs.append({"arquivo": rel(FIG_COEF), "como_ler": COMO_LER[FIG_COEF.name],
                 "descricao": "coeficiente da exposição por R$ 5 mil, principal, sensibilidades, ciclos e placebos"})
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.0))
    for ax, oid, ylab in zip(axes, PRIMARIAS, ("célula preenchida (resíduo)", "candidatos de 1ª opção (resíduo)")):
        if oid not in extra["residuos"]:
            continue
        rx, ry, b = extra["residuos"][oid]
        ordem = np.argsort(rx, kind="mergesort")
        grupos = np.array_split(ordem, N_BINS_FIG)
        mx = np.array([rx[g].mean() for g in grupos])
        my = np.array([ry[g].mean() for g in grupos])
        ax.plot(mx, my, "o", color="#2a78d6", ms=4)
        xs = np.array([rx.min(), rx.max()])
        ax.plot(xs, b * xs, color="#1b3f73", lw=1.4)
        ax.axhline(0, color="#52514e", lw=0.6)
        ax.set_xlabel("exposição residual (R$ mil)")
        ax.set_ylabel(ylab)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(color="#e6e5e0", lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG_BINS, dpi=150, metadata={"Software": None})
    plt.close(fig)
    figs.append({"arquivo": rel(FIG_BINS), "como_ler": COMO_LER[FIG_BINS.name],
                 "descricao": "médias por grupo do outcome e da exposição residualizados, especificação principal"})
    return figs


# ---------------------------------------------------------------------------
# Documento 57g (gerado inteiro pelo script a partir das saídas)
# ---------------------------------------------------------------------------

def _n(v, casas: int = 3, sinal: bool = False) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    s = f"{abs(v):,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if v < 0 and s.strip("0,.") != "":
        return "−" + s
    return ("+" + s) if sinal and s.strip("0,.") != "" else s


def _p(v) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    return "< 0,001" if v < 0.001 else _n(v, 3)


def _ic(lo, hi, casas: int = 3) -> str:
    return f"[{_n(lo, casas)}; {_n(hi, casas)}]"


def _int(v) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    return f"{int(v):,}".replace(",", ".")


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    out += ["| " + " | ".join(l) + " |" for l in linhas]
    return "\n".join(out)


def _escala(oid: str) -> tuple[float, int, str]:
    return (100.0, 1, " p.p.") if oid in ("R_P1", "R_S1") else (1.0, 3, "")


def _efeito5(r: dict) -> str:
    esc, casas, suf = _escala(r["outcome_id"])
    return f"{_n(r['coef_por_5mil'] * esc, casas, True)}{suf} (IC 95% {_ic(r['ic95_inf_5mil'] * esc, r['ic95_sup_5mil'] * esc, casas)})"


def tabela_amostra(resumo: dict) -> str:
    a = resumo["amostra"]
    ex = a["exclusoes_universo"]
    linhas = [["células no quadro da 1ª chamada"] + [_int(a["n_total"].get(str(k))) for k in CICLOS]
              + [_int(sum(a["n_total"].values()))]]
    for m in ("sem_ivs", "sem_cir"):
        linhas.append([f"fora do universo: {MOTIVOS[m]}"] + [_int(ex[m].get(str(k), 0)) for k in CICLOS]
                      + [_int(sum(ex[m].values()))])
    p = a["por_especificacao"]["PRINCIPAL"]
    for m, v in p["fora"].items():
        linhas.append([f"fora da principal: {MOTIVOS[m]}"] + [_int(v.get(str(k), 0)) for k in CICLOS]
                      + [_int(sum(v.values()))])
    linhas.append(["**amostra principal (CIR)**"] + [_int(p["por_ciclo"].get(str(k), 0)) for k in CICLOS]
                  + [_int(p["n_celulas"])])
    t = _tab(["Item", "Ciclo 1", "Ciclo 2", "Ciclo 3", "Total"], linhas)
    t += (f"\n\nNa amostra principal há {_int(p['n_cir'])} regiões de saúde (clusters) e {_int(p['n_municipios'])} "
          "municípios. As células sem covariável continuam como concorrentes das outras; só saem da estimação.")
    linhas2 = []
    for e in ESPECS:
        s = a["por_especificacao"][e["id"]]
        fora = "; ".join(f"{MOTIVOS[m]}: {_int(sum(v.values()))}" for m, v in s["fora"].items()) or "—"
        linhas2.append([e["id"], e["desc"], _int(s["n_celulas"]), _int(s["n_cir"]), fora])
    t += "\n\n" + _tab(["Especificação", "Descrição", "Células", "CIR", "Fora (motivo: células)"], linhas2)
    return t


def tabela_variacao(var: pd.DataFrame, est: pd.DataFrame) -> str:
    linhas = []
    for r in var.itertuples():
        pr = _uma(est, r.especificacao, "R_P1")
        linhas.append([r.especificacao, r.mercado, r.unidade_exposicao, _int(r.n_celulas), _n(r.n_conc_mediana, 1),
                       _n(r.frac_com_conc_bolsa_diferente, 3), _n(r.frac_com_conc_bolsa_maior, 3),
                       _n(r.exposicao_dp, 3), _n(pr["dp_exposicao_residual"] if pr else None, 3),
                       _n(pr["r2_exposicao_controles"] if pr else None, 3),
                       f"{_n(r.exposicao_p10, 2)} / {_n(r.exposicao_p50, 2)} / {_n(r.exposicao_p90, 2)}"])
    return _tab(["Especificação", "Mercado", "Exposição", "Células", "Concorrentes (mediana)",
                 "Fração com concorrente de outra faixa", "Fração com concorrente de bolsa maior", "DP da exposição",
                 "DP residual", "R² da exposição nos controles", "p10 / p50 / p90"], linhas)


def tabela_principal(est: pd.DataFrame) -> str:
    linhas = []
    for o in OUTCOMES:
        r = _uma(est, "PRINCIPAL", o["id"])
        if r is None:
            linhas.append([o["id"], o["desc"]] + ["—"] * 9)
            continue
        esc, casas, suf = _escala(o["id"])
        papel = {"primaria": "primária", "secundaria": "secundária"}[o["papel"]]
        linhas.append([o["id"], o["desc"], papel, _int(r["n_celulas"]), _n(r["media_outcome"] * esc, casas) + suf,
                       f"{_n(r['coef'] * esc, casas + 1, True)}{suf}", _ic(r["ic95_inf"] * esc, r["ic95_sup"] * esc, casas + 1),
                       _p(r["p"]), _p(r["p_t_G1"]), _p(r["p_holm"]),
                       f"{_n(r['mde_por_5mil'] * esc, casas)}{suf}"])
    t = _tab(["Id", "Outcome", "Papel", "Células", "Média", "Coef. por R$ 1 mil", "IC 95%", "p", "p (t, G−1)",
              "p Holm", "MDE por R$ 5 mil"], linhas)
    r = _uma(est, "PRINCIPAL", "R_P1")
    if r:
        t += (f"\n\nEP CR1 com {_int(r['n_clusters'])} clusters (CIR). Os ids R-P1, R-P2 e R-S1 do protocolo são "
              "R_P1, R_P2 e R_S1 nas saídas. Holm só nas duas primárias (R-P1, R-P2) da "
              "principal. MDE = 2,802 × EP (80% de poder, teste bilateral a 5%). Limiares fixados no protocolo (§9), "
              f"por R$ 5 mil: R-P1 {_n(LIMIAR_MDE_5MIL['R_P1'] * 100, 0)} p.p.; R-P2 {_n(LIMIAR_MDE_5MIL['R_P2'], 2)} "
              "candidato.")
    return t


def tabela_espec(est: pd.DataFrame, ids: list[str]) -> str:
    linhas = []
    for eid in ids:
        for o in OUTCOMES:
            r = _uma(est, eid, o["id"])
            if r is None:
                s = est[(est["especificacao"] == eid) & (est["outcome_id"] == o["id"])]
                nota = s.iloc[0]["nota"] if len(s) else "—"
                linhas.append([eid, o["id"], "—", "—", "—", "—", "—", "—", f"NAO_EXECUTADO: {nota}"])
                continue
            esc, casas, suf = _escala(o["id"])
            linhas.append([eid, o["id"], _int(r["n_celulas"]), f"{_n(r['coef'] * esc, casas + 1, True)}{suf}",
                           _ic(r["ic95_inf"] * esc, r["ic95_sup"] * esc, casas + 1), _p(r["p"]),
                           (f"{_n(r['mde_por_5mil'] * esc, casas)}{suf}" if math.isfinite(r["mde_por_5mil"])
                            else f"{_n(r['mde_por_unidade'] * esc, casas)}{suf} (por unidade)"),
                           _n(r["dp_exposicao_residual"], 3), r["nota"] or ""])
    return _tab(["Especificação", "Outcome", "Células", "Coef. por unidade da exposição", "IC 95%", "p",
                 "MDE por R$ 5 mil", "DP residual da exposição", "Nota"], linhas)


def leitura(est: pd.DataFrame, resumo: dict) -> str:
    partes = []
    nomes = {"R_P1": "célula preenchida na 1ª chamada", "R_P2": "candidatos de 1ª opção por célula",
             "R_S1": "célula com candidato de 1ª opção"}
    for oid in PRIMARIAS + ["R_S1"]:
        r = _uma(est, "PRINCIPAL", oid)
        if r is None:
            continue
        esc, casas, suf = _escala(oid)
        frase = (f"**{oid} ({nomes[oid]}).** Na principal ({_int(r['n_celulas'])} células, mercado = CIR), quando a "
                 f"bolsa média das concorrentes sobe R$ 5 mil, o outcome muda {_efeito5(r)}; p = {_p(r['p'])}")
        if oid in PRIMARIAS:
            c = resumo["leitura"][oid]
            frase += (f", p de Holm = {_p(r['p_holm'])}. MDE por R$ 5 mil: {_n(r['mde_por_5mil'] * esc, casas)}{suf} "
                      f"(limiar do protocolo: {_n(c['limiar_mde_5mil'] * esc, casas)}{suf}). Leitura pré-registrada: "
                      f"**{c['leitura']}**.")
        else:
            frase += " (secundária, sem Holm)."
        partes.append(frase)
    sens = []
    for oid in PRIMARIAS:
        for eid in ("R1", "R2", "R3", "R7"):
            r = _uma(est, eid, oid)
            if r is None:
                continue
            esc, casas, suf = _escala(oid)
            ic0 = r["ic95_inf"] <= 0 <= r["ic95_sup"]
            sens.append(f"{eid}/{oid}: {_n(r['coef'] * esc, casas + 1, True)}{suf} por unidade da exposição "
                        f"(IC {_ic(r['ic95_inf'] * esc, r['ic95_sup'] * esc, casas + 1)}; "
                        f"{'contém zero' if ic0 else 'exclui zero'})")
    partes.append("**Sensibilidades (relatadas, não escolhidas).** " + "; ".join(sens) + ".")
    excl = [(eid, oid) for oid in PRIMARIAS for eid in ("R1", "R2", "R3", "R4", "R5", "R6", "R7")
            if (r := _uma(est, eid, oid)) is not None and not (r["ic95_inf"] <= 0 <= r["ic95_sup"])]
    if excl:
        txt = ", ".join(f"{e}/{o}" for e, o in excl)
        comp = []
        for e, o in excl:
            r, q = _uma(est, e, o), _uma(est, "PL1", o)
            if q is not None and e != "R3":
                esc, casas, suf = _escala(o)
                comp.append(f"{e}/{o} {_n(r['coef'] * esc, casas + 1, True)}{suf} contra PL1/{o} "
                            f"{_n(q['coef'] * esc, casas + 1, True)}{suf} (p = {_p(q['p'])}), ambos por R$ 1 mil")
        partes.append(f"Entre as sensibilidades das primárias, o IC de 95% exclui zero em {txt}. São linhas sem Holm "
                      "e não mudam a leitura pré-registrada, que é a da principal. O placebo de outros cursos, que não "
                      "disputa os mesmos candidatos, tem tamanho parecido"
                      + (": " + "; ".join(dict.fromkeys(comp)) if comp else "")
                      + ". Esse sinal, portanto, não é específico das concorrentes do mesmo curso e não é lido como "
                      "deslocamento.")
    pls = []
    for oid in PRIMARIAS:
        for eid in ("PL1", "PL2"):
            r = _uma(est, eid, oid)
            if r is None:
                continue
            pls.append(f"{eid}/{oid}: {_efeito5(r)}, p = {_p(r['p'])}")
    partes.append("**Placebos.** " + "; ".join(pls) + ". Um placebo com p < 0,05 indicaria que a exposição capta "
                  "outra coisa (geografia do IVS ou abertura de vagas).")
    inc = [oid for oid in PRIMARIAS if resumo["leitura"][oid]["classe"] == "INCONCLUSIVO"]
    if inc:
        ics = []
        for oid in inc:
            r = _uma(est, "PRINCIPAL", oid)
            esc, casas, suf = _escala(oid)
            ics.append(f"{oid} de {_n(r['ic95_inf_5mil'] * esc, casas)}{suf} a {_n(r['ic95_sup_5mil'] * esc, casas, True)}{suf}")
        partes.append("**O que \"inconclusivo\" quer dizer.** O IC de 95% por R$ 5 mil vai " + "; ".join(ics) +
                      ", e o MDE fica acima do limiar do protocolo: o desenho não separa deslocamento de zero nessa "
                      "margem. Não é evidência de que não haja deslocamento, nem de que haja.")
    ciclo_ex = [f"{e}/{o}" for e in ("C1", "C2", "C3") for o in ("R_P1", "R_P2", "R_S1")
                if (r := _uma(est, e, o)) is not None and not (r["ic95_inf"] <= 0 <= r["ic95_sup"])]
    partes.append("**Por ciclo.** São 9 estimativas (3 ciclos × 3 outcomes), sem correção de multiplicidade e com MDE "
                  "bem acima do da principal; o IC de 95% exclui zero em " + (", ".join(ciclo_ex) if ciclo_ex else
                  "nenhuma") + ", e os sinais mudam de um ciclo para outro. Isso não é achado nem heterogeneidade "
                  "estabelecida: a leitura continua sendo a da principal.")
    v = resumo["variacao_principal"]
    partes.append(f"**Variação disponível.** Na principal, {_n(v['frac_com_conc_bolsa_diferente'] * 100, 1)}% das "
                  f"células têm alguma concorrente na CIR com bolsa diferente da sua; o desvio-padrão da exposição é "
                  f"R$ {_n(v['exposicao_dp'], 2)} mil e, depois dos controles, R$ {_n(v['dp_exposicao_residual'], 2)} mil "
                  f"(os controles explicam {_n(v['r2_exposicao_controles'] * 100, 1)}% da variância da exposição).")
    partes.append("Tudo acima é condicional às vagas abertas e mede o pacote do corte das concorrentes (bolsa e "
                  "outras regras federais nos mesmos cortes), não a participação no PMM-E. Fora das hipóteses do "
                  "protocolo (§5), os coeficientes são associações condicionais.")
    return "\n\n".join(partes)


def tabela_figuras(resumo: dict) -> str:
    return _tab(["Arquivo", "O que mostra", "Como ler"],
                [[f"`{Path(f['arquivo']).name}`", f["descricao"], f["como_ler"]] for f in resumo["figuras"]])


def tabela_desvios(resumo: dict) -> str:
    if not resumo["desvios"]:
        return "Nenhum desvio do protocolo."
    return "\n".join(f"{i}. **{d['tema']}** ({d['data']}). {d['situacao']} *Resolução:* {d['resolucao']}"
                     for i, d in enumerate(resumo["desvios"], 1))


def gerar_doc(est: pd.DataFrame, var: pd.DataFrame, resumo: dict) -> str:
    def bloco(nome: str, corpo: str) -> str:
        return f"<!-- R:{nome}:inicio -->\n{corpo}\n<!-- R:{nome}:fim -->"

    cab = (
        "# 57g. Resultados da realocação: a bolsa das concorrentes desloca candidatos e preenchimento?\n\n"
        "> **Gerado por** `scripts/rdd_bolsa/32_realocacao_bolsa.py` a partir de `output/rdd_bolsa/R_*`; não editar "
        "à mão (o teste `tests/test_realocacao_bolsa.py` confere que este arquivo é igual ao gerado).<br>\n"
        "> **Protocolo:** [`58_protocolo_realocacao_bolsa.md`](58_protocolo_realocacao_bolsa.md), congelado em "
        "24/10/2026 antes de abrir qualquer outcome por exposição; estatuto `EXPLORATORIO_REALOCACAO` (o E9, o P1 e o "
        "A3 já tinham sido vistos).<br>\n"
        "> **Saídas:** `output/rdd_bolsa/R_estimativas.csv`, `R_variacao_exposicao.csv`, `R_resumo.json` e "
        "`R_figuras/`; toda linha tem `natureza_dos_dados = EMPIRICO`.\n\n"
        "## 1. O que se mede e o que não se pode dizer\n\n"
        "- **Pergunta.** A bolsa maior desloca médicos entre vagas do programa, em vez de preencher mais vagas no "
        "total? As células do mesmo curso e ciclo disputam os mesmos candidatos numa alocação centralizada por nota.\n"
        "- **Estimando.** Quanto mudam o preenchimento e os candidatos de 1ª opção de uma célula quando a bolsa média "
        "das concorrentes do mesmo curso e ciclo na mesma região de saúde sobe, com a própria faixa, o IVS próprio e o "
        "IVS das concorrentes mantidos (spline contínua com nós em 0,300 e 0,400).\n"
        "- **Fonte de variação.** Onde os municípios das concorrentes caem em relação a 0,300 e 0,400: a bolsa delas "
        "muda em degraus, e o IVS delas entra de forma contínua.\n"
        "- **O que o contraste mede.** O pacote do corte das concorrentes (bolsa +R$ 5 mil e outras regras federais "
        "nos mesmos cortes, auditoria 18), condicional às vagas abertas. Não mede a participação no PMM-E, o efeito "
        "total do Agora Tem Especialistas nem a entrada de novos candidatos.\n"
        "- **Por que importa para a RDD.** Se houver deslocamento, a RDD nos cortes, que compara vizinhos que disputam "
        "as mesmas pessoas, mede tratamento mais deslocamento (violação de SUTVA).\n\n"
        "## 2. Amostra\n\n" + bloco("amostra", tabela_amostra(resumo)) + "\n\n"
        "## 3. Leitura em linguagem simples\n\n" + bloco("leitura", leitura(est, resumo)) + "\n\n"
        "## 4. Variação disponível na exposição\n\n"
        "Para cada especificação: quantas células, quantas concorrentes, quantas têm concorrente com bolsa diferente "
        "e quanto da exposição sobra depois dos controles (a variação que identifica o coeficiente).\n\n"
        + bloco("variacao", tabela_variacao(var, est)) + "\n\n"
        "## 5. Resultado principal, Holm e MDE\n\n" + bloco("principal", tabela_principal(est)) + "\n\n"
        "## 6. Sensibilidades (R1–R7)\n\n"
        "Coeficiente por unidade da exposição (R$ 1 mil em todas, menos R3, que é por fração de 0 a 1). Relatadas "
        "para os três outcomes, sem Holm próprio.\n\n"
        + bloco("sensibilidades", tabela_espec(est, ["R1", "R2", "R3", "R4", "R5", "R6", "R7"])) + "\n\n"
        "## 7. Placebos\n\n"
        "PL1 usa as células de outros cursos (não disputam os mesmos candidatos); PL2 usa as células do mesmo curso "
        "que só abrem em ciclo posterior (o candidato do ciclo não podia escolhê-las).\n\n"
        + bloco("placebos", tabela_espec(est, ["PL1", "PL2"])) + "\n\n"
        "## 8. Por ciclo (condição pré-tratamento)\n\n"
        "O ciclo 1 fica à parte porque a adesão dos gestores precedeu o anúncio da faixa. As nove linhas abaixo não têm "
        "correção de multiplicidade e MDE alto: um p < 0,05 isolado aqui não é achado e não muda a leitura da principal.\n\n"
        + bloco("ciclos", tabela_espec(est, ["C1", "C2", "C3"])) + "\n\n"
        "## 9. Figuras\n\n"
        "Nenhuma figura traz texto de leitura dentro da imagem; o \"Como ler\" fica aqui e no campo `como_ler` de "
        "`R_resumo.json`.\n\n" + bloco("figuras", tabela_figuras(resumo)) + "\n\n"
        "## 10. Desvios e decisões de implementação\n\n" + bloco("desvios", tabela_desvios(resumo)) + "\n\n"
        "## 11. Limites\n\n"
        "- **Pacote do corte.** As concorrentes acima do corte estão sob outras regras federais além da bolsa "
        "(auditoria 18).\n"
        "- **Vagas abertas endógenas.** A abertura é decisão do gestor e da SGTES; os limites de Lee do A2 (doc 49, "
        "§15) são largos e, no P5 (doc 57e), a célula pedida salta nos cortes sem passar no BKY. O conjunto de "
        "concorrentes, e portanto a exposição, depende dessa abertura.\n"
        "- **Conjunto de escolha.** Supõe-se que o candidato vê todas as células do curso no ciclo; o mercado "
        "geográfico (CIR, raio, UF) é uma aproximação e não usa a origem do candidato.\n"
        "- **Células com concorrente.** A amostra exige ao menos uma concorrente no mercado: as células isoladas ficam "
        "fora e a amostra pende para regiões com mais células.\n"
        "- **Cluster.** Nas definições de mercado mais largas (raio, UF), as exposições se repetem além da CIR, e o EP "
        "por CIR pode ser otimista.\n"
        "- **Associação.** Fora das hipóteses do §5 do protocolo, os coeficientes são associações condicionais.\n"
    )
    return cab


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def desvios(dados: dict) -> list[dict]:
    """Desvios e decisões de implementação (datados); nenhum depende de outcome."""
    univ = dados["univ"]
    n_empate = int((univ["s_mil"] == 350).sum())
    return [
        {"tema": "Contagem do §4 do protocolo", "data": "24/10/2026",
         "situacao": ("O §4 registrou 2.876 (CIR), 4.533 (raio) e 4.854 (UF) células com concorrente, numa conta de "
                      "desenho feita antes de congelar, em que a célula sem IVS oficial e as 9 células sem CIR ainda "
                      "entravam no universo. O próprio §4 diz que essas células ficam fora."),
         "resolucao": ("Universo = células com IVS oficial e CIR, como o §4 manda; a amostra principal tem o número "
                       "da seção 2. Nada muda na especificação.")},
        {"tema": "R7: concorrente equidistante dos dois cortes", "data": "24/10/2026",
         "situacao": (f"O §7 diz 'a até 0,050 de um corte'; uma célula com IVS 0,350 está a 0,050 dos dois. No "
                      f"universo há {n_empate} células com IVS 0,350."),
         "resolucao": ("Cada concorrente usa o corte mais próximo; no empate, 0,300 (fica acima dele, com bolsa da "
                       "faixa 2). Regra definida sem consultar outcome.")},
        {"tema": "PL2: chave que reaparece em mais de um ciclo posterior", "data": "24/10/2026",
         "situacao": ("Uma célula (estabelecimento × curso) ausente do ciclo 1 pode aparecer nos ciclos 2 e 3."),
         "resolucao": "Entra uma vez, com os atributos do primeiro ciclo posterior em que aparece."},
        {"tema": "Cluster nos mercados largos", "data": "24/10/2026",
         "situacao": ("O §5 fixa cluster por CIR; no raio de 200 km (R1) e na UF (R2) a exposição se repete além "
                      "da CIR."),
         "resolucao": "Mantido o cluster por CIR, como no protocolo; a limitação fica declarada na seção 11."},
        {"tema": "R7: controle do número de concorrentes", "data": "24/10/2026",
         "situacao": ("O §7 manda manter os controles próprios da principal; o log(1 + nº de concorrentes) da "
                      "principal conta todas as concorrentes da CIR, não só as vizinhas do corte."),
         "resolucao": "Mantido o log(1 + nº de concorrentes) da CIR inteira; a média da spline das concorrentes sai "
                      "e entram as médias de (IVS − corte) das vizinhas, como no §7."},
        {"tema": "Intervalo de confiança", "data": "24/10/2026",
         "situacao": "O §5 pede EP CR1 e o p pela t com G − 1 graus de liberdade ao lado.",
         "resolucao": "O IC de 95% e o p principal usam a normal; o p pela t com G − 1 "
                      "fica na coluna `p_t_G1`. Nenhuma conclusão muda de um para o outro."},
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57g a partir das saídas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    dados = carregar()
    est, var, extra = estimar_tudo(dados)
    OUT.mkdir(parents=True, exist_ok=True)
    cols_est = ["especificacao", "descricao", "outcome_id", "outcome", "papel", "unidade_outcome", "mercado",
                "exposicao", "unidade_exposicao", "ciclos", "grau_spline", "covariaveis", "cluster", "status", "nota",
                "n_celulas", "n_clusters", "n_parametros", "media_outcome", "coef", "ep", "ic95_inf", "ic95_sup", "p",
                "p_t_G1", "p_holm", "coef_por_5mil", "ic95_inf_5mil", "ic95_sup_5mil", "mde_por_unidade",
                "mde_por_5mil", "mde_por_dp_residual", "dp_exposicao", "dp_exposicao_residual",
                "r2_exposicao_controles", "frac_celulas_exposicao_nao_nula", "estatuto", "natureza_dos_dados"]
    for c in cols_est:
        if c not in est.columns:
            est[c] = np.nan
    est[cols_est].to_csv(OUT_EST, index=False, float_format="%.10g", lineterminator="\n")
    var.to_csv(OUT_VAR, index=False, float_format="%.10g", lineterminator="\n")
    est = ler_est()      # a leitura e o doc usam os números gravados
    var = ler_var()
    leitura_reg = {oid: classificar(est, oid) for oid in PRIMARIAS}
    pr = _uma(est, "PRINCIPAL", "R_P1")
    vp = var[var["especificacao"] == "PRINCIPAL"].iloc[0].to_dict()
    vp.update({"dp_exposicao_residual": pr["dp_exposicao_residual"],
               "r2_exposicao_controles": pr["r2_exposicao_controles"]})
    figs = figuras(est, extra)
    resumo = {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "data_execucao": DATA_EXECUCAO,
        "protocolo": rel(PROTOCOLO_MD), "script": rel(Path(__file__)), "doc": rel(DOC),
        "estimando": ("efeito, sobre os outcomes da célula aberta, de R$ 1 mil a mais na bolsa média das concorrentes "
                      "do mesmo curso e ciclo no mercado (menos a própria), com a faixa própria, o IVS próprio e o IVS "
                      "das concorrentes controlados; pacote do corte das concorrentes, condicional às vagas abertas"),
        "contraste": "incentivo marginal (e pacote do corte) das concorrentes; não é participação no PMM-E",
        "parametros": {"cortes_mil": list(CORTES), "raio_km": RAIO_KM, "h_vizinho_mil": H_VIZINHO_MIL,
                       "passo_bolsa_mil": PASSO_BOLSA, "alfa": ALFA, "poder": PODER, "fator_mde": FATOR_MDE,
                       "limiar_mde_por_5mil": LIMIAR_MDE_5MIL, "covariaveis": COVS,
                       "mapa_faixa_bolsa_mil": dados["mapa"], "faixa_base": FAIXA_BASE,
                       "especificacoes": [{k: (list(v) if isinstance(v, tuple) else v) for k, v in e.items()}
                                          for e in ESPECS]},
        "amostra": {"n_total": dados["n_total"], "exclusoes_universo": {k: v for k, v in dados["exclusoes"].items()
                                                                        if k != "sem_cov"},
                    "sem_covariaveis_no_universo": dados["exclusoes"]["sem_cov"],
                    "celulas_fora_do_universo": dados["celulas_fora"], "por_especificacao": extra["amostras"],
                    "motivos": MOTIVOS},
        "variacao_principal": vp,
        "leitura": leitura_reg,
        "figuras": figs,
        "desvios": desvios(dados),
        "validacoes": {"ivs_celula_igual_a08": True, "faixa_igual_regra_dois_cortes": True,
                       "cir": dados["diag_cir"], "centroides": {"status": dados["diag_coord"]["status"],
                                                                "municipios": dados["diag_coord"]["municipios"]},
                       "cnes_pre": dados["cnes"], "linhas_nao_executadas_com_motivo": True},
        "entradas": [
            bloco_entrada(V_CELULA, "células do quadro da 1ª chamada e outcomes (n_alocados_ch1, n_cand_1a_opcao)",
                          "tarefa B (script 12)", "quadros e resultados da 1ª chamada, ciclos 1–3",
                          "5.135 células", "célula", "ciclo, co_cnes_7d, cod_curso", "nenhum"),
            bloco_entrada(E9.IVS_OFICIAL, "IVS 2010 oficial (running variable e spline)", "IPEA, Plataforma IVS (a08)",
                          "2010", "municípios", "município", "co_ibge", "coluna ivs"),
            bloco_entrada(E9.GRADES_EDITAIS, "grade faixa → bolsa (editais 2025 e 2026)", "a03", "2025–2026",
                          "faixas 1–3", "faixa", "faixa", "nenhum"),
            bloco_entrada(E9.GRADE_2025, "grade faixa → bolsa (FAQ 2025, conferência)", "a04", "2025", "faixas 1–3",
                          "faixa", "faixa_atracao", "nenhum"),
            bloco_entrada(X45.CIR_BRUTO, "região de saúde (CIR) por município (só lido)",
                          "DATASUS/TabNet (manifesto da X5)", "base territorial corrente no download", "Brasil",
                          "município", "co_ibge (6 dígitos)", "linhas 'Ignorado' fora"),
            bloco_entrada(X1.COORD_JSON, "centroides municipais do IBGE (distância, só lido)", "IBGE, API de malhas v3",
                          "malha corrente no download", "municípios", "município", "id (7 dígitos)", "centroide"),
            bloco_entrada(ARQ_POP, "população do Censo 2022 (covariável)", "IBGE, Censo 2022 (a06)", "2022",
                          "municípios", "município", "co_ibge_6d", "nenhum"),
            bloco_entrada(T24.ARQ_CNES, "estoques CNES pré-programa (covariáveis do A4)", "CNES nacional (a09)",
                          "202406–202506", "municípios × grupo de CBO × mês", "município", "co_ibge, grupo, competencia",
                          "competências 202406–202506; grupos alvo_pmme e generalistas"),
        ],
        "saidas": [rel(OUT_EST), rel(OUT_VAR), rel(OUT_RESUMO)] + [f["arquivo"] for f in figs],
    }
    resumo["hashes_saidas"] = {rel(p): sha256(p) for p in (OUT_EST, OUT_VAR)}
    resumo["hashes_saidas"].update({f["arquivo"]: sha256(ROOT / f["arquivo"]) for f in figs})
    gravar_json(OUT_RESUMO, resumo)
    resumo = json.loads(OUT_RESUMO.read_text(encoding="utf-8"))
    DOC.write_text(gerar_doc(ler_est(), ler_var(), resumo), encoding="utf-8")
    for oid in PRIMARIAS:
        r = _uma(est, "PRINCIPAL", oid)
        print(f"{oid}: coef {r['coef']:.4f} EP {r['ep']:.4f} p {r['p']:.3f} Holm {r['p_holm']:.3f} "
              f"MDE5 {r['mde_por_5mil']:.4f} -> {leitura_reg[oid]['classe']}")
    return 0


def ler_est() -> pd.DataFrame:
    d = pd.read_csv(OUT_EST, dtype={"ciclos": str})
    d["nota"] = d["nota"].fillna("").astype(str)
    return d


def ler_var() -> pd.DataFrame:
    return pd.read_csv(OUT_VAR, dtype={"ciclos": str})


def atualizar_doc() -> None:
    resumo = json.loads(OUT_RESUMO.read_text(encoding="utf-8"))
    DOC.write_text(gerar_doc(ler_est(), ler_var(), resumo), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
