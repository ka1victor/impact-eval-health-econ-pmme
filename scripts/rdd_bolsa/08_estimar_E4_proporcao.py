"""E4: proporcao de celulas preenchidas no corte do escore administrativo de IVS.

Executa o adendo congelado `output/rdd_bolsa/protocolo_E4_adendo_proporcao.json`
(14/10/2026) ao protocolo base `output/rdd_bolsa/protocolo_escore_administrativo.json`,
sem alterar janela, corte, populacao, outcome, cenario ou estimador. Os dois
arquivos sao conferidos por SHA-256 e contra as constantes deste script; qualquer
divergencia interrompe a execucao.

Populacao P1: 368 municipios (1.295 celulas CNES-curso) do quadro da 1a chamada
do ciclo 1. Outcomes por municipio (lidos de `output/rdd_bolsa/E4_proporcao_municipio.csv`
e conferidos celula a celula contra a fonte canonica
`output/tema_trabalho/matriz_funil_ciclo1.parquet`, que prevalece; divergencia
interrompe a execucao):

- Y1 (principal): fracao das celulas com alguma confirmacao ou homologacao na
  1a chamada (definicao do A4);
- Y2 (secundario): fracao das celulas com Y1 = 1 ou homologacao nova na 2a
  chamada (ciclo 1 inteiro).

Running variable: escore administrativo `ivs_admin` (a07), em milesimos
inteiros; cortes 0,300 e 0,400; o corte pertence ao lado inferior
(T = 1[s > c]); janelas (c - h, c] e (c, c + h]. S = 1 se o municipio tem
escore (especialista ativo de qualquer ciclo na relacao nominal de 09/10/2026).

- E4a (ingenuo, VIESADO por selecao; so referencia): so S = 1; constante local
  (media de cada lado, kernel uniforme) e local linear triangular, h = 0,050,
  EP HC1 por municipio, IC 95% normal.
- E4b (limites sem premissa de continuidade): Y e conhecido para os 368; para
  os municipios sem escore so a posicao falta. Posicao possivel = intervalo da
  faixa anunciada (`pior_caso`). O cenario `informado` do adendo, que estreitava
  esse intervalo com o arquivo de IVS errado, saiu em 18/10/2026 (auditoria 19;
  ver CENARIO_RETIRADO). Em cada lado, a
  media extrema de Y sai do subconjunto dos "possivelmente dentro" que a
  minimiza/maximiza, somado aos conhecidos e aos "certamente dentro". Para media
  simples ou ponderada, o otimo inclui exatamente os possiveis com Y abaixo
  (acima) do proprio otimo, entao basta testar os prefixos da ordenacao por Y.
  Delta_min = media_sup_min - media_inf_max; Delta_max = media_sup_max -
  media_inf_min, valido porque nenhum municipio pode estar nas duas janelas do
  mesmo corte (conferido em cada especificacao).
- E4c (limites de Lee, sob monotonicidade e A1): rho_S = razao das densidades
  laterais do escore entre os municipios de P1 com S = 1, pelo estimador
  principal do E1 (Poisson log-linear em mass points de 0,001, h = 0,050,
  importado de `05_estimar_E1_densidade.py`). Se rho_S > 1 apara-se a fracao
  1 - 1/rho_S dos selecionados de cima; se rho_S < 1, a fracao 1 - rho_S dos de
  baixo. Aparo pela distribuicao empirica com peso fracionario na observacao de
  fronteira (Y e discreto). Bootstrap de municipios com S = 1 dentro da janela
  (reamostragem conjunta dos dois lados), 999 replicas, semente 20261014
  (gerador reiniciado em cada corte), reestimando rho_S; replicas em que o
  Poisson nao tem MLE finito ou nao converge sao descartadas e contadas. IC 95%
  percentil: 2,5% do limite inferior e 97,5% do superior. Sensibilidade: limites
  com rho_S nos extremos do seu proprio IC 95% (HC0, normal).

Linguagem: exploratorio e descritivo. E4b nao usa continuidade; E4c depende de
monotonicidade e de A1; nada aqui e efeito causal estabelecido. O contraste e o
incentivo marginal anunciado de R$ 5 mil (possivelmente pacote se outra regra
mudar no mesmo corte), nao a participacao no PMM-E nem o Agora Tem Especialistas.
Ciclo 2 e ciclo 3 fora do E4.

Somente numpy, pandas e math.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ADENDO = ROOT / "output" / "rdd_bolsa" / "protocolo_E4_adendo_proporcao.json"
PROTOCOLO = ROOT / "output" / "rdd_bolsa" / "protocolo_escore_administrativo.json"
PROPORCAO = ROOT / "output" / "rdd_bolsa" / "E4_proporcao_municipio.csv"
FUNIL = ROOT / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"
ESCORE = ROOT / "output" / "aquisicao" / "a07_ivs_administrativo_municipio.csv"
QUADRO_C1 = ROOT / "data" / "raw" / "aquisicao" / "vagas" / "2025_ciclo1_chamada1_vagas.xlsx"
SCRIPT_E1 = ROOT / "scripts" / "rdd_bolsa" / "05_estimar_E1_densidade.py"
OUT_CSV = ROOT / "output" / "rdd_bolsa" / "E4_estimativas.csv"
OUT_JSON = ROOT / "output" / "rdd_bolsa" / "E4_resumo.json"

DATA_EXECUCAO = "2026-10-14"

# Hashes congelados: o adendo registra o do protocolo base; o do adendo e o do
# arquivo na data de congelamento (14/10/2026).
SHA_PROTOCOLO_BASE = "7785d58ee1a001a4b61ac677eb3d2f71e56519ec78823f29accc1b0755bc90a4"
SHA_ADENDO = "57eb6ae6dfb0ba96100daa693d2f0345fc4c3d1c752959aa805a6571019728c6"

# Tudo em milesimos inteiros do escore.
CORTES_MIL = (300, 400)
JANELAS_MIL = (50, 30, 80)  # 0,050 principal; 0,030 e 0,080 sensibilidade (ordem do adendo)
H_PRINCIPAL_MIL = 50
INTERVALO_FAIXA_MIL = {"FAIXA 3": (0, 300), "FAIXA 2": (301, 400), "FAIXA 1": (401, 1000)}
# Desvio de 18/10/2026: o cenario `informado` usava como banda
# data/ivs_ipea_2010_municipios.csv, linha de subgrupo populacional e nao o IVS do
# municipio (auditorias 16 e 19). Numeros desse arquivo nao entram em saida ativa.
CENARIOS = ("pior_caso",)
CENARIO_RETIRADO = {
    "cenario": "informado",
    "data": "2026-10-18",
    "motivo": (
        "a banda [ivs_2010 + dmin, ivs_2010 + dmax] usava data/ivs_ipea_2010_municipios.csv, linha de subgrupo "
        "populacional e nao o IVS do municipio; numeros desse arquivo so valem como failure mode"
    ),
    "efeito_em_E4a_E4b_pior_caso_e_E4c": "nenhum: nao leem o arquivo",
    "registro": "docs/auditorias/19_reestimacao_base_oficial_failure_mode.md",
}
OUTCOMES = ("Y1", "Y2")
PONDERACOES = ("simples", "celulas")  # simples = principal; celulas = sensibilidade
N_MUNICIPIOS_P1 = 368
N_CELULAS_P1 = 1295

N_BOOT = 999
SEMENTE = 20261014
ALFA = 0.05

COLUNAS = [
    "componente", "outcome", "corte", "h", "cenario_ou_espec", "ponderacao",
    "n_inf", "n_sup", "estimativa", "limite_inf", "limite_sup", "ic_inf", "ic_sup", "nota",
]

ROTULO_VIES = "VIESADO por selecao (so S = 1); apenas referencia"


# --------------------------------------------------------------------------
# Utilitarios
# --------------------------------------------------------------------------
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(65536):
            h.update(bloco)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def mil(x: float) -> int:
    v = round(float(x) * 1000)
    if abs(float(x) * 1000 - v) > 1e-6:
        raise ValueError(f"valor fora da grade de 0,001: {x}")
    return int(v)


def fmt_mil(v: int) -> str:
    return f"{v / 1000:.3f}"


def carregar_e1():
    """Importa o script do E1 como biblioteca (mesmo estimador Poisson), sem gravar bytecode."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("e1_densidade", SCRIPT_E1)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


E1 = carregar_e1()
Z975 = E1.Z975


def conferir_protocolos() -> tuple[dict, dict]:
    """Falha fechada se adendo ou protocolo base mudaram ou divergem das constantes."""
    assert sha256(PROTOCOLO) == SHA_PROTOCOLO_BASE, "protocolo base difere do congelado"
    assert sha256(ADENDO) == SHA_ADENDO, "adendo E4 difere do congelado"
    base = json.loads(PROTOCOLO.read_text(encoding="utf-8"))
    ad = json.loads(ADENDO.read_text(encoding="utf-8"))
    assert ad["protocolo_base"]["sha256"] == SHA_PROTOCOLO_BASE
    assert ad["protocolo_base"]["arquivo"] == rel(PROTOCOLO)
    assert ad["data_congelamento"] == base["data_congelamento"] == "2026-10-14"

    cortes = sorted(mil(float(c)) for c in base["running_variable"]["cortes"])
    assert tuple(cortes) == CORTES_MIL, cortes
    assert "s > c" in base["running_variable"]["lado"]
    intervalos = {f: (mil(a), mil(b)) for f, (a, b) in base["running_variable"]["intervalos_por_faixa"].items()}
    assert intervalos == INTERVALO_FAIXA_MIL, intervalos

    janelas = tuple(mil(float(re.search(r"h = (\d,\d+)", j).group(1).replace(",", ".")))
                    for j in ad["E4b_limites_pior_caso"]["janelas"])
    assert janelas == JANELAS_MIL, janelas
    assert "principal" in ad["E4b_limites_pior_caso"]["janelas"][0]
    assert ad["E4b_limites_pior_caso"]["outcomes"] == list(OUTCOMES)
    assert "pior_caso" in ad["E4b_limites_pior_caso"]["cenarios"]
    # O adendo congelado lista tambem o `informado`, retirado em 18/10/2026 (CENARIO_RETIRADO).
    assert "informado" in ad["E4b_limites_pior_caso"]["cenarios"]
    assert "h = 0,050" in ad["E4a_ingenuo"]["descricao"]
    assert "constante local" in ad["E4a_ingenuo"]["descricao"]
    assert "local linear triangular" in ad["E4a_ingenuo"]["descricao"]
    assert "h = 0,050" in ad["E4c_limites_de_Lee"]["janela"]
    assert "constante local" in ad["E4c_limites_de_Lee"]["janela"]
    assert "999" in ad["E4c_limites_de_Lee"]["inferencia"]
    assert str(SEMENTE) in ad["E4c_limites_de_Lee"]["inferencia"]
    assert "h = 0,050" in ad["E4c_limites_de_Lee"]["razao_de_selecao"]
    assert "1.295" in ad["populacao"] and "368" in ad["populacao"]
    # O estimador principal do E1 no protocolo base e o Poisson log-linear com h = 0,050.
    assert "h = 0,050" in base["E1_densidade"]["estimador_principal"]
    assert "log mu(s) = a + b*x + tau*T + d*T*x" in base["E1_densidade"]["estimador_principal"]
    return base, ad


# --------------------------------------------------------------------------
# Leitura de P1, outcomes e escore
# --------------------------------------------------------------------------
def normalizar_faixa(v: pd.Series) -> pd.Series:
    return v.astype(str).str.strip().str.upper().str.replace(r"\s+", " ", regex=True)


def proporcao_canonica() -> pd.DataFrame:
    """Y1 e Y2 por municipio a partir da fonte canonica (matriz do funil, A1).

    Celulas = linhas com chamada == 1 e in_quadro_ch1_original (amostra primaria
    do A4). Y1_celula = outcome_alguma_confirmacao_ou_homologacao. Y2_celula =
    Y1_celula ou n_homologacoes_novas_ch2 > 0 na linha da 2a chamada da mesma
    celula CNES-curso (como em scripts/tema_trabalho/07_red_team_sintese.py).
    """
    chave = ["co_cnes_7d", "cod_curso"]
    f = pd.read_parquet(FUNIL)
    flag = f["in_quadro_ch1_original"].fillna(False).astype(bool)
    c1 = f[(f["chamada"] == 1) & flag].copy()
    assert not c1.duplicated(chave).any(), "celula duplicada no quadro Ch1"
    c2 = f.loc[f["chamada"] == 2, chave + ["n_homologacoes_novas_ch2"]]
    assert not c2.duplicated(chave).any(), "celula duplicada na 2a chamada"
    c1 = c1.drop(columns=["n_homologacoes_novas_ch2"]).merge(c2, on=chave, how="left", validate="one_to_one")
    y1 = c1["outcome_alguma_confirmacao_ou_homologacao"].astype(int)
    assert y1.isin([0, 1]).all()
    c1["y1"] = y1
    c1["y2"] = ((y1 == 1) | (c1["n_homologacoes_novas_ch2"].fillna(0) > 0)).astype(int)
    c1["co_ibge"] = c1["co_ibge_6d"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(6)
    c1["faixa_anunciada"] = normalizar_faixa(c1["faixa_atracao_anunciada"])
    assert (c1.groupby("co_ibge")["faixa_anunciada"].nunique() == 1).all(), "municipio com duas faixas"
    m = c1.groupby("co_ibge").agg(
        faixa_anunciada=("faixa_anunciada", "first"),
        n_celulas=("y1", "size"),
        n_celulas_y1=("y1", "sum"),
        n_celulas_y2=("y2", "sum"),
    ).reset_index()
    return m


def ler_proporcao() -> tuple[pd.DataFrame, dict]:
    if not PROPORCAO.exists():
        raise FileNotFoundError(f"insumo do E4 ausente: {rel(PROPORCAO)}")
    d = pd.read_csv(PROPORCAO, dtype={"co_ibge": str})
    esperadas = ["co_ibge", "faixa_anunciada", "n_celulas", "n_celulas_y1", "n_celulas_y2", "y1", "y2"]
    faltam = [c for c in esperadas if c not in d.columns]
    assert not faltam, f"colunas ausentes em {rel(PROPORCAO)}: {faltam}"
    d = d[esperadas].copy()
    d["co_ibge"] = d["co_ibge"].str.strip().str.zfill(6)
    d["faixa_anunciada"] = normalizar_faixa(d["faixa_anunciada"])
    assert d["co_ibge"].is_unique and len(d) == N_MUNICIPIOS_P1, len(d)
    for c in ["n_celulas", "n_celulas_y1", "n_celulas_y2"]:
        assert (d[c] == d[c].round()).all()
        d[c] = d[c].astype(int)
    assert int(d["n_celulas"].sum()) == N_CELULAS_P1, int(d["n_celulas"].sum())
    assert (d["n_celulas"] > 0).all()
    assert ((d["n_celulas_y1"] >= 0) & (d["n_celulas_y1"] <= d["n_celulas_y2"])
            & (d["n_celulas_y2"] <= d["n_celulas"])).all(), "contagens incoerentes (Y1 <= Y2 <= celulas)"
    assert np.allclose(d["y1"], d["n_celulas_y1"] / d["n_celulas"], rtol=0, atol=1e-6)
    assert np.allclose(d["y2"], d["n_celulas_y2"] / d["n_celulas"], rtol=0, atol=1e-6)
    assert d["faixa_anunciada"].isin(list(INTERVALO_FAIXA_MIL)).all(), d["faixa_anunciada"].unique()

    # Conferencia contra a fonte canonica: municipio a municipio, contagens inteiras.
    can = proporcao_canonica()
    cmp = d.merge(can, on="co_ibge", how="outer", suffixes=("", "_can"), indicator=True)
    so_um_lado = int((cmp["_merge"] != "both").sum())
    divergentes = cmp[(cmp["_merge"] == "both") & (
        (cmp["faixa_anunciada"] != cmp["faixa_anunciada_can"])
        | (cmp["n_celulas"] != cmp["n_celulas_can"])
        | (cmp["n_celulas_y1"] != cmp["n_celulas_y1_can"])
        | (cmp["n_celulas_y2"] != cmp["n_celulas_y2_can"])
    )]
    if so_um_lado or len(divergentes):
        raise AssertionError(
            f"{rel(PROPORCAO)} diverge da fonte canonica: {so_um_lado} municipios em so uma das bases, "
            f"{len(divergentes)} com contagens divergentes; a canonica prevalece e o E4 nao roda"
        )
    # Y exato a partir das contagens inteiras (o CSV pode trazer y arredondado).
    d["y1"] = d["n_celulas_y1"] / d["n_celulas"]
    d["y2"] = d["n_celulas_y2"] / d["n_celulas"]
    conf = {
        "municipios": int(len(d)),
        "celulas": int(d["n_celulas"].sum()),
        "celulas_y1": int(d["n_celulas_y1"].sum()),
        "celulas_y2": int(d["n_celulas_y2"].sum()),
        "confere_com_fonte_canonica": True,
        "criterio": "mesmos municipios, faixa, n_celulas, n_celulas_y1 e n_celulas_y2 (inteiros); "
                    "y1/y2 do CSV iguais a contagem/celulas com tolerancia 1e-6",
    }
    return d.sort_values("co_ibge").reset_index(drop=True), conf


def montar_p1() -> tuple[pd.DataFrame, dict]:
    d, conf = ler_proporcao()

    # P1 do protocolo base: municipios do quadro bruto da 1a chamada do ciclo 1.
    quadro = E1.ler_quadro(rel(QUADRO_C1))
    assert (quadro.groupby("co_ibge")["faixa_anunciada"].nunique() == 1).all()
    quadro = quadro.drop_duplicates("co_ibge")
    assert set(quadro["co_ibge"]) == set(d["co_ibge"]), "P1 do quadro bruto != municipios do E4"
    fq = d.merge(quadro, on="co_ibge", suffixes=("", "_quadro"))
    assert (fq["faixa_anunciada"] == normalizar_faixa(fq["faixa_anunciada_quadro"])).all(), \
        "faixa do E4 difere da faixa do quadro bruto"

    escore = pd.read_csv(ESCORE, dtype={"co_ibge": str})[["co_ibge", "ivs_admin"]]
    assert escore["co_ibge"].is_unique and escore["ivs_admin"].notna().all()
    escore["s_mil"] = escore["ivs_admin"].map(mil)
    assert len(escore) == 404, len(escore)

    p = d.merge(escore[["co_ibge", "s_mil"]], on="co_ibge", how="left")
    p["S"] = p["s_mil"].notna().astype(int)
    com = p[p["S"] == 1]
    faixa_escore = com["s_mil"].astype(int).map(
        lambda s: next(f for f, (a, b) in INTERVALO_FAIXA_MIL.items() if a <= s <= b))
    assert (faixa_escore == com["faixa_anunciada"]).all(), "escore nao reproduz a faixa anunciada"
    p["faixa_lo"] = p["faixa_anunciada"].map(lambda f: INTERVALO_FAIXA_MIL[f][0])
    p["faixa_hi"] = p["faixa_anunciada"].map(lambda f: INTERVALO_FAIXA_MIL[f][1])

    meta = {
        "outcomes_conferencia": conf,
        "municipios": int(len(p)),
        "com_escore_S1": int(p["S"].sum()),
        "sem_escore_S0": int((p["S"] == 0).sum()),
        "por_faixa_anunciada": {
            f: {
                "municipios": int(len(g)),
                "S1": int(g["S"].sum()),
                "celulas": int(g["n_celulas"].sum()),
                "media_simples_Y1": float(g["y1"].mean()),
                "media_simples_Y1_S1": float(g.loc[g["S"] == 1, "y1"].mean()),
                "media_simples_Y1_S0": float(g.loc[g["S"] == 0, "y1"].mean()),
            }
            for f, g in p.groupby("faixa_anunciada")
        },
    }
    return p, meta


# --------------------------------------------------------------------------
# E4a: diferenca local ingenua (so S = 1)
# --------------------------------------------------------------------------
def wls_hc1(X: np.ndarray, y: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n, k = X.shape
    XtWX = X.T @ (X * w[:, None])
    bread = np.linalg.inv(XtWX)
    beta = bread @ (X.T @ (w * y))
    e = y - X @ beta
    score = X * (w * e)[:, None]
    V = bread @ (score.T @ score) @ bread * (n / (n - k))
    return beta, V


def e4a(s_mil: np.ndarray, y: np.ndarray, peso: np.ndarray, c: int, h: int, linear: bool) -> dict:
    """Constante local (kernel uniforme) ou local linear triangular, EP HC1 por municipio."""
    x = s_mil - c
    na_janela = (x > -h) & (x <= h)
    k = np.clip(1.0 - np.abs(x) / h, 0.0, None) if linear else np.ones_like(x, dtype=float)
    w = np.where(na_janela, k * peso, 0.0)
    usa = w > 0
    ab, ac = usa & (x <= 0), usa & (x > 0)
    res = {"n_inf": int(ab.sum()), "n_sup": int(ac.sum()), "estimativa": math.nan,
           "ic_inf": math.nan, "ic_sup": math.nan, "ep": math.nan}
    mp_ab, mp_ac = np.unique(s_mil[ab]).size, np.unique(s_mil[ac]).size
    minimo = 2 if linear else 1
    if mp_ab < minimo or mp_ac < minimo:
        res["nota"] = f"nao estimado: menos de {minimo} mass point(s) com peso positivo em algum lado"
        return res
    xs = x[usa] / 1000.0
    t = (x[usa] > 0).astype(float)
    X = np.column_stack([np.ones_like(xs), xs, t, t * xs]) if linear else np.column_stack([np.ones_like(xs), t])
    if usa.sum() <= X.shape[1]:
        res["nota"] = "nao estimado: graus de liberdade insuficientes"
        return res
    beta, V = wls_hc1(X, y[usa], w[usa])
    j = 2 if linear else 1
    tau, ep = float(beta[j]), float(math.sqrt(max(V[j, j], 0.0)))
    media_inf = float(np.average(y[ab], weights=(peso[ab]))) if ab.any() else math.nan
    media_sup = float(np.average(y[ac], weights=(peso[ac]))) if ac.any() else math.nan
    res.update({"estimativa": tau, "ep": ep, "ic_inf": tau - Z975 * ep, "ic_sup": tau + Z975 * ep,
                "nota": f"{ROTULO_VIES}; EP HC1 = {ep:.6f}; IC 95% normal; mass points {mp_ab}/{mp_ac}; "
                        f"medias brutas dos lados (peso da ponderacao, sem kernel) {media_inf:.6f}/{media_sup:.6f}"})
    return res


# --------------------------------------------------------------------------
# E4b: limites exatos com posicao desconhecida dos municipios sem escore
# --------------------------------------------------------------------------
def media_extrema(y_fix: np.ndarray, w_fix: np.ndarray, y_poss: np.ndarray, w_poss: np.ndarray,
                  maximizar: bool) -> tuple[float, int]:
    """Min (ou max) da media ponderada de Y sobre fixos + subconjunto dos possiveis.

    No otimo lambda*, um possivel entra sse Y < lambda* (min) ou Y > lambda* (max);
    logo o otimo e um prefixo da ordenacao por Y. Conjunto vazio nao e admissivel.
    Devolve (valor, numero de possiveis incluidos).
    """
    A, B = float(np.sum(w_fix * y_fix)), float(np.sum(w_fix))
    ordem = np.argsort(-y_poss if maximizar else y_poss, kind="stable")
    yw = np.concatenate([[0.0], np.cumsum((w_poss * y_poss)[ordem])])
    ww = np.concatenate([[0.0], np.cumsum(w_poss[ordem])])
    den = B + ww
    ok = den > 0
    if not ok.any():
        return math.nan, 0
    medias = np.where(ok, (A + yw) / np.where(ok, den, 1.0), np.nan)
    i = int(np.nanargmax(medias) if maximizar else np.nanargmin(medias))
    return float(medias[i]), i


def conjuntos_possiveis(sem: pd.DataFrame, cenario: str) -> tuple[np.ndarray, np.ndarray, int]:
    """Intervalo possivel do escore de cada municipio sem escore: o intervalo da faixa (como no E2)."""
    if cenario != "pior_caso":
        raise ValueError(f"cenario {cenario!r} fora do E4 (o `informado` saiu em 18/10/2026; auditoria 19)")
    return sem["faixa_lo"].to_numpy(dtype=int), sem["faixa_hi"].to_numpy(dtype=int), 0


def e4b(p: pd.DataFrame, conj: tuple[np.ndarray, np.ndarray], outcome: str, ponderacao: str,
        c: int, h: int) -> dict:
    ycol = outcome.lower()
    com = p[p["S"] == 1]
    sem = p[p["S"] == 0]
    s = com["s_mil"].to_numpy(dtype=int)
    y_c, y_s = com[ycol].to_numpy(dtype=float), sem[ycol].to_numpy(dtype=float)
    if ponderacao == "simples":
        w_c, w_s = np.ones(len(com)), np.ones(len(sem))
    else:
        w_c, w_s = com["n_celulas"].to_numpy(dtype=float), sem["n_celulas"].to_numpy(dtype=float)
    lo, hi = conj
    l0, l1, u0, u1 = c - h + 1, c, c + 1, c + h
    in_l, in_u = (s >= l0) & (s <= l1), (s >= u0) & (s <= u1)
    cert_l, cert_u = (lo >= l0) & (hi <= l1), (lo >= u0) & (hi <= u1)
    cruza_l, cruza_u = (lo <= l1) & (hi >= l0), (lo <= u1) & (hi >= u0)
    poss_l, poss_u = cruza_l & ~cert_l, cruza_u & ~cert_u
    # Exclusividade: nenhum municipio sem escore pode estar nas duas janelas.
    n_ambas = int((cruza_l & cruza_u).sum())
    assert n_ambas == 0, f"{n_ambas} municipios sem escore podem estar nas duas janelas (c={c}, h={h})"

    fix_l_y = np.concatenate([y_c[in_l], y_s[cert_l]])
    fix_l_w = np.concatenate([w_c[in_l], w_s[cert_l]])
    fix_u_y = np.concatenate([y_c[in_u], y_s[cert_u]])
    fix_u_w = np.concatenate([w_c[in_u], w_s[cert_u]])
    inf_min, k_inf_min = media_extrema(fix_l_y, fix_l_w, y_s[poss_l], w_s[poss_l], maximizar=False)
    inf_max, k_inf_max = media_extrema(fix_l_y, fix_l_w, y_s[poss_l], w_s[poss_l], maximizar=True)
    sup_min, k_sup_min = media_extrema(fix_u_y, fix_u_w, y_s[poss_u], w_s[poss_u], maximizar=False)
    sup_max, k_sup_max = media_extrema(fix_u_y, fix_u_w, y_s[poss_u], w_s[poss_u], maximizar=True)
    return {
        "n_inf": int(in_l.sum() + cert_l.sum()),
        "n_sup": int(in_u.sum() + cert_u.sum()),
        "n_conhecidos_inf": int(in_l.sum()), "n_conhecidos_sup": int(in_u.sum()),
        "n_certos_inf": int(cert_l.sum()), "n_certos_sup": int(cert_u.sum()),
        "n_possiveis_inf": int(poss_l.sum()), "n_possiveis_sup": int(poss_u.sum()),
        "n_sem_escore_nas_duas_janelas": n_ambas,
        "media_inf_min": inf_min, "media_inf_max": inf_max,
        "media_sup_min": sup_min, "media_sup_max": sup_max,
        "possiveis_incluidos": {"inf_min": k_inf_min, "inf_max": k_inf_max,
                                "sup_min": k_sup_min, "sup_max": k_sup_max},
        "limite_inf": sup_min - inf_max,
        "limite_sup": sup_max - inf_min,
    }


# --------------------------------------------------------------------------
# E4c: limites de Lee
# --------------------------------------------------------------------------
def media_aparada(y: np.ndarray, manter: float, manter_baixos: bool) -> float:
    """Media dos `manter` (fracao) menores (ou maiores) valores de y.

    Distribuicao empirica com peso fracionario na observacao de fronteira:
    mantem k = n * manter observacoes; com Y discreto e o aparo exato da fracao.
    """
    n = len(y)
    k = n * manter
    if n == 0 or k <= 0:
        return math.nan
    ys = np.sort(y) if manter_baixos else np.sort(y)[::-1]
    inteiras = int(math.floor(k + 1e-12))
    inteiras = min(inteiras, n)
    soma = float(ys[:inteiras].sum())
    frac = k - inteiras
    if frac > 1e-12 and inteiras < n:
        soma += frac * float(ys[inteiras])
    return soma / k


def lee(y_inf: np.ndarray, y_sup: np.ndarray, rho: float) -> dict:
    """Limites de Lee para mean(Y | sup) - mean(Y | inf) entre os sempre-selecionados."""
    if rho > 1.0:
        p = 1.0 - 1.0 / rho
        m_inf = float(np.mean(y_inf))
        lb = media_aparada(y_sup, 1.0 - p, manter_baixos=True) - m_inf
        ub = media_aparada(y_sup, 1.0 - p, manter_baixos=False) - m_inf
        lado = "superior"
    elif rho < 1.0:
        p = 1.0 - rho
        m_sup = float(np.mean(y_sup))
        lb = m_sup - media_aparada(y_inf, 1.0 - p, manter_baixos=False)
        ub = m_sup - media_aparada(y_inf, 1.0 - p, manter_baixos=True)
        lado = "inferior"
    else:
        p = 0.0
        lb = ub = float(np.mean(y_sup) - np.mean(y_inf))
        lado = "nenhum"
    return {"limite_inf": lb, "limite_sup": ub, "fracao_aparada": p, "lado_aparado": lado}


def rho_s(s_mil_s1: np.ndarray, c: int) -> dict:
    """Estimador principal do E1 (Poisson log-linear, h = 0,050) nas contagens de S = 1."""
    cont = pd.Series(s_mil_s1).value_counts().sort_index()
    return E1.ajustar_poisson(cont, c, H_PRINCIPAL_MIL, linear=True, excluir_corte=False)


def e4c(p: pd.DataFrame, c: int) -> dict:
    h = H_PRINCIPAL_MIL
    com = p[p["S"] == 1]
    s = com["s_mil"].to_numpy(dtype=int)
    y = com["y1"].to_numpy(dtype=float)
    janela = (s > c - h) & (s <= c + h)
    s_w, y_w = s[janela], y[janela]
    n = len(s_w)

    r = rho_s(s, c)
    assert r["estimado"], f"rho_S nao estimado no corte {c}: {r['nota']}"
    assert r["n_esq"] == int((s_w <= c).sum()) and r["n_dir"] == int((s_w > c).sum())
    principal = lee(y_w[s_w <= c], y_w[s_w > c], r["rho"])

    rng = np.random.default_rng(SEMENTE)
    lbs, ubs, rhos = [], [], []
    degeneradas: dict[str, int] = {}
    for _ in range(N_BOOT):
        idx = rng.integers(0, n, size=n)
        sb, yb = s_w[idx], y_w[idx]
        rb = rho_s(sb, c)
        if not rb["estimado"]:
            motivo = rb["nota"]
            degeneradas[motivo] = degeneradas.get(motivo, 0) + 1
            continue
        lb = lee(yb[sb <= c], yb[sb > c], rb["rho"])
        if not (math.isfinite(lb["limite_inf"]) and math.isfinite(lb["limite_sup"])):
            degeneradas["limites nao finitos"] = degeneradas.get("limites nao finitos", 0) + 1
            continue
        lbs.append(lb["limite_inf"])
        ubs.append(lb["limite_sup"])
        rhos.append(rb["rho"])
    lbs_a, ubs_a, rhos_a = np.array(lbs), np.array(ubs), np.array(rhos)
    validas = len(lbs_a)
    ic_inf = float(np.quantile(lbs_a, ALFA / 2.0)) if validas else math.nan
    ic_sup = float(np.quantile(ubs_a, 1.0 - ALFA / 2.0)) if validas else math.nan

    sens = {}
    for nome, rr in (("rho_S_ic_inf", r["ic_inf"]), ("rho_S_ic_sup", r["ic_sup"])):
        sens[nome] = {"rho_S": rr, **lee(y_w[s_w <= c], y_w[s_w > c], rr)}

    return {
        "n_inf": int((s_w <= c).sum()),
        "n_sup": int((s_w > c).sum()),
        "media_inf": float(y_w[s_w <= c].mean()),
        "media_sup": float(y_w[s_w > c].mean()),
        "rho_S": {"rho": r["rho"], "ic_inf": r["ic_inf"], "ic_sup": r["ic_sup"], "tau": r["tau"],
                  "ep_tau_hc0": r["ep_tau_hc0"], "p_valor": r["p_valor"], "n_esq": r["n_esq"],
                  "n_dir": r["n_dir"], "iteracoes": r["iteracoes"]},
        **principal,
        "ic_inf": ic_inf,
        "ic_sup": ic_sup,
        "bootstrap": {
            "replicas": N_BOOT,
            "semente": SEMENTE,
            "validas": validas,
            "degeneradas": N_BOOT - validas,
            "motivos_degeneradas": degeneradas,
            "reamostragem": "municipios com S = 1 dentro da janela (c - 0,050, c + 0,050], com reposicao, "
                            "tamanho n, dois lados juntos (contagens laterais aleatorias)",
            "quantil": "numpy.quantile, metodo 'linear' (padrao)",
            "rho_S_percentis_2.5_50_97.5": ([float(v) for v in np.quantile(rhos_a, [0.025, 0.5, 0.975])]
                                            if validas else None),
            "fracao_replicas_rho_maior_que_1": float((rhos_a > 1.0).mean()) if validas else None,
            "limite_inf_percentis_2.5_50": ([float(v) for v in np.quantile(lbs_a, [0.025, 0.5])]
                                            if validas else None),
            "limite_sup_percentis_50_97.5": ([float(v) for v in np.quantile(ubs_a, [0.5, 0.975])]
                                             if validas else None),
        },
        "sensibilidade_rho_extremos_ic": sens,
    }


# --------------------------------------------------------------------------
# Execucao
# --------------------------------------------------------------------------
def linha(componente, outcome, c, h, espec, ponderacao, n_inf, n_sup, estimativa=math.nan,
          limite_inf=math.nan, limite_sup=math.nan, ic_inf=math.nan, ic_sup=math.nan, nota="") -> dict:
    return {"componente": componente, "outcome": outcome, "corte": fmt_mil(c), "h": fmt_mil(h),
            "cenario_ou_espec": espec, "ponderacao": ponderacao, "n_inf": n_inf, "n_sup": n_sup,
            "estimativa": estimativa, "limite_inf": limite_inf, "limite_sup": limite_sup,
            "ic_inf": ic_inf, "ic_sup": ic_sup, "nota": nota}


def main() -> None:
    base, adendo = conferir_protocolos()
    p, meta = montar_p1()

    linhas: list[dict] = []
    detalhes_e4b: list[dict] = []

    # E4a ---------------------------------------------------------------
    com = p[p["S"] == 1]
    s1 = com["s_mil"].to_numpy(dtype=int)
    for outcome in OUTCOMES:
        y = com[outcome.lower()].to_numpy(dtype=float)
        for ponderacao in PONDERACOES:
            peso = np.ones(len(com)) if ponderacao == "simples" else com["n_celulas"].to_numpy(dtype=float)
            for c in CORTES_MIL:
                for espec, linear in (("constante_local_uniforme", False), ("local_linear_triangular", True)):
                    r = e4a(s1, y, peso, c, H_PRINCIPAL_MIL, linear)
                    linhas.append(linha("E4a", outcome, c, H_PRINCIPAL_MIL, espec, ponderacao, r["n_inf"],
                                        r["n_sup"], estimativa=r["estimativa"], ic_inf=r["ic_inf"],
                                        ic_sup=r["ic_sup"], nota=r["nota"]))

    # E4b ---------------------------------------------------------------
    sem = p[p["S"] == 0]
    conjuntos = {cen: conjuntos_possiveis(sem, cen) for cen in CENARIOS}
    for outcome in OUTCOMES:
        for c in CORTES_MIL:
            for h in JANELAS_MIL:
                for cenario in CENARIOS:
                    for ponderacao in PONDERACOES:
                        lo, hi, _ = conjuntos[cenario]
                        r = e4b(p, (lo, hi), outcome, ponderacao, c, h)
                        nota = (
                            f"inf: {r['n_conhecidos_inf']} com escore + {r['n_certos_inf']} certos + "
                              f"{r['n_possiveis_inf']} possiveis, media em [{r['media_inf_min']:.6f}, "
                              f"{r['media_inf_max']:.6f}]; sup: {r['n_conhecidos_sup']} com escore + "
                              f"{r['n_certos_sup']} certos + {r['n_possiveis_sup']} possiveis, media em "
                              f"[{r['media_sup_min']:.6f}, {r['media_sup_max']:.6f}]; "
                              "sem premissa de continuidade"
                        )
                        linhas.append(linha("E4b", outcome, c, h, cenario, ponderacao, r["n_inf"], r["n_sup"],
                                            limite_inf=r["limite_inf"], limite_sup=r["limite_sup"], nota=nota))
                        detalhes_e4b.append({"outcome": outcome, "corte": fmt_mil(c), "h": fmt_mil(h),
                                             "cenario": cenario, "ponderacao": ponderacao,
                                             **{k: v for k, v in r.items()}})

    # E4c ---------------------------------------------------------------
    resultados_e4c = {}
    for c in CORTES_MIL:
        r = e4c(p, c)
        resultados_e4c[fmt_mil(c)] = r
        rs = r["rho_S"]
        nota = (f"sob monotonicidade e A1; rho_S = {rs['rho']:.6f} (IC 95% {rs['ic_inf']:.6f}-{rs['ic_sup']:.6f}, "
                f"Poisson linear h = 0,050, n {rs['n_esq']}/{rs['n_dir']}); apara {r['fracao_aparada']:.6f} "
                f"do lado {r['lado_aparado']}; IC bootstrap percentil {r['bootstrap']['validas']} replicas validas, "
                f"{r['bootstrap']['degeneradas']} degeneradas; medias sem aparo {r['media_inf']:.6f}/{r['media_sup']:.6f}")
        linhas.append(linha("E4c", "Y1", c, H_PRINCIPAL_MIL, "lee_constante_local", "simples", r["n_inf"], r["n_sup"],
                            limite_inf=r["limite_inf"], limite_sup=r["limite_sup"],
                            ic_inf=r["ic_inf"], ic_sup=r["ic_sup"], nota=nota))
        for nome, sv in r["sensibilidade_rho_extremos_ic"].items():
            linhas.append(linha(
                "E4c", "Y1", c, H_PRINCIPAL_MIL, f"lee_constante_local_{nome}", "simples", r["n_inf"], r["n_sup"],
                limite_inf=sv["limite_inf"], limite_sup=sv["limite_sup"],
                nota=f"sensibilidade: rho_S fixado em {sv['rho_S']:.6f} (extremo do IC 95% de rho_S); apara "
                     f"{sv['fracao_aparada']:.6f} do lado {sv['lado_aparado']}; sem IC"))

    tabela = pd.DataFrame(linhas, columns=COLUNAS)
    tabela.to_csv(OUT_CSV, index=False, float_format="%.6f")

    fontes = {
        rel(PROPORCAO): sha256(PROPORCAO),
        rel(FUNIL): sha256(FUNIL),
        rel(ESCORE): sha256(ESCORE),
        rel(QUADRO_C1): sha256(QUADRO_C1),
        rel(SCRIPT_E1): sha256(SCRIPT_E1),
    }
    resumo = {
        "documento": "E4 - proporcao de celulas preenchidas no corte do escore administrativo de IVS",
        "status": "ESTIMACAO_EXPLORATORIA_E4",
        "natureza_dos_dados": "EMPIRICO",
        "desvio_do_adendo": CENARIO_RETIRADO,
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__).resolve()),
        "adendo": {"arquivo": rel(ADENDO), "sha256": sha256(ADENDO),
                   "data_congelamento": adendo["data_congelamento"], "alterado": False},
        "protocolo_base": {"arquivo": rel(PROTOCOLO), "sha256": sha256(PROTOCOLO),
                           "sha256_confere_adendo": True, "alterado": False},
        "fontes_sha256": fontes,
        "papel_das_fontes": {
            rel(PROPORCAO): "outcomes Y1/Y2 por municipio (insumo lido)",
            rel(FUNIL): "fonte canonica; usada so para conferir o insumo, municipio a municipio",
            rel(ESCORE): "running variable s (ivs_admin) e S = 1[tem escore]",
            rel(QUADRO_C1): "P1 e faixa anunciada do quadro bruto (conferencia)",
            rel(SCRIPT_E1): "biblioteca: estimador Poisson do E1 (ajustar_poisson) e leitura do quadro",
        },
        "linguagem": adendo["linguagem"],
        "contraste": "incentivo marginal anunciado de R$ 5 mil no corte (possivelmente pacote se outra regra "
                     "mudar no mesmo corte); nao e participacao no PMM-E nem o Agora Tem Especialistas",
        "hipotese_do_adendo": adendo["hipotese"],
        "exposicao_previa_a_outcomes": adendo["exposicao_previa_a_outcomes"],
        "populacao": meta,
        "outcomes": {
            "Y1": adendo["outcomes"]["Y1_principal"],
            "Y2": adendo["outcomes"]["Y2_secundario"],
            "ponderacao": adendo["outcomes"]["ponderacao"],
        },
        "running_variable": {
            "fonte": rel(ESCORE) + ", coluna ivs_admin, milesimos inteiros",
            "cortes": [c / 1000 for c in CORTES_MIL],
            "janela_inferior": "(c - h, c]",
            "janela_superior": "(c, c + h]",
            "intervalos_por_faixa": {f: [a / 1000, b / 1000] for f, (a, b) in INTERVALO_FAIXA_MIL.items()},
        },
        "E4a": {
            "rotulo": adendo["E4a_ingenuo"]["rotulo"],
            "especificacoes": {
                "constante_local_uniforme": "diferenca das medias (ponderadas) de Y entre (c-h, c] e (c, c+h] "
                                            "entre municipios com S = 1; MQP de Y em [1, T]; EP HC1",
                "local_linear_triangular": "MQP de Y em [1, x, T, T x], pesos max(0, 1 - |x|/h) (vezes "
                                           "n_celulas na ponderacao por celulas); EP HC1; minimo de 2 mass "
                                           "points com peso positivo por lado",
            },
            "ponderacao": "simples (principal) e por celulas (sensibilidade, conforme o item ponderacao do adendo)",
            "ic": "normal, z = %.6f" % Z975,
        },
        "E4b": {
            "estimando": adendo["E4b_limites_pior_caso"]["estimando"],
            "cenarios": {
                "pior_caso": "municipio sem escore em qualquer ponto do intervalo da sua faixa anunciada",
                "informado": "retirado em 18/10/2026 (ver desvio_do_adendo)",
            },
            "metodo": "em cada lado, fixos = municipios com escore na janela + sem escore cujo intervalo "
                      "possivel cabe na janela; possiveis = sem escore cujo intervalo cruza a janela sem caber. "
                      "Media minima (maxima) = menor (maior) media de fixos + prefixo dos possiveis ordenados "
                      "por Y crescente (decrescente), inclusive o prefixo vazio quando ha fixos; janela vazia "
                      "nao e admissivel. limite_inf = media_sup_min - media_inf_max; limite_sup = media_sup_max "
                      "- media_inf_min",
            "exclusividade": "conferida em todas as especificacoes: nenhum municipio sem escore cruza as duas "
                             "janelas do mesmo corte (cada intervalo possivel esta dentro de uma faixa e o corte "
                             "separa faixas adjacentes), entao os extremos marginais sao atingiveis conjuntamente",
            "ponderacao": "simples (principal) e por celulas (sensibilidade): media ponderada = soma de celulas "
                          "com Y / soma de celulas",
            "detalhe_por_especificacao": detalhes_e4b,
        },
        "E4c": {
            "estimando": adendo["E4c_limites_de_Lee"]["estimando"],
            "premissa": adendo["E4c_limites_de_Lee"]["premissa"],
            "razao_de_selecao": "rho_S = exp(tau) do Poisson log-linear do E1 (log mu = a + b x + tau T + d T x) "
                                "nas contagens por mass point de 0,001 dos municipios de P1 com S = 1, lado "
                                "inferior c-0,049..c, superior c+0,001..c+0,050; IC 95% por EP sanduiche HC0 "
                                "e normal (funcao ajustar_poisson importada do script do E1)",
            "aparo": adendo["E4c_limites_de_Lee"]["corte_do_excesso"]
                     + "; implementado na distribuicao empirica com peso fracionario na observacao de fronteira",
            "janela_medias": "constante local: medias simples de Y1 entre os municipios com S = 1 em (c-0,050, c] "
                             "e (c, c+0,050]",
            "inferencia": adendo["E4c_limites_de_Lee"]["inferencia"]
                          + "; gerador numpy default_rng(20261014) reiniciado em cada corte; replicas sem MLE "
                            "finito do Poisson sao descartadas e contadas",
            "sensibilidade": adendo["E4c_limites_de_Lee"]["sensibilidade"]
                             + " (IC de rho_S calculado aqui com o mesmo estimador; nao e o IC de rho para D_1)",
            "ponderacao": "so simples: o adendo nao especifica aparo ponderado por celulas para o E4c, e aparar "
                          "uma fracao de municipios para extremar uma media ponderada por celulas nao e o "
                          "procedimento de Lee; nao estimado",
            "por_corte": resultados_e4c,
        },
        "rho_S_por_corte": {k: v["rho_S"] for k, v in resultados_e4c.items()},
        "saidas": {rel(OUT_CSV): {"linhas": int(len(tabela))}, rel(OUT_JSON): {}},
        "regra_de_relato": adendo["regra_de_relato"],
    }
    OUT_JSON.write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=float) + "\n", encoding="utf-8")

    with pd.option_context("display.width", 250, "display.max_columns", 30, "display.max_rows", 500):
        print(tabela.drop(columns=["nota"]).to_string(index=False))
    print(json.dumps({"populacao": {k: v for k, v in meta.items() if k != "por_faixa_anunciada"},
                      "rho_S": resumo["rho_S_por_corte"],
                      "bootstrap": {k: {kk: vv for kk, vv in v["bootstrap"].items()
                                        if kk in ("validas", "degeneradas", "motivos_degeneradas")}
                                    for k, v in resultados_e4c.items()}},
                     ensure_ascii=False, indent=2, default=float))


if __name__ == "__main__":
    main()
