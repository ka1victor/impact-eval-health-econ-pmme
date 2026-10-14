"""E1: razao de densidades laterais do escore administrativo de IVS.

Implementa o estimador E1 do protocolo congelado
`output/rdd_bolsa/protocolo_escore_administrativo.json` (14/10/2026), sem
alterar janela, corte, populacao, outcome ou estimador.

Estimando: rho(c, k) = P(D_k = 1 | s = c+) / P(D_k = 1 | s = c-) entre os
municipios de P_k. Sob a premissa A1 (densidade do escore continua em c entre
todos os municipios de P_k, nao testavel com dados publicos), a razao das
densidades laterais do escore entre os municipios com D_k = 1 iguala rho.

- P1: municipios do quadro do ciclo 1, chamada 1 (principal).
- P2: uniao dos quadros do ciclo 2, chamadas 1 e 2 (replicacao, sem Holm).
- D_k(m) = 1 se ha especialista ativo com `ciclo` == k em co_ibge == m na
  Relacao Nominal Ativos - PMM-E de 09/10/2026. Da relacao nominal so se leem
  as colunas `co_ibge` e `ciclo`.
- Ciclo 3 excluido (prospectivo e congelado).

Estimador principal: Poisson log-linear nas contagens por mass point de 0,001
(inclusive mass points com contagem zero), log mu = a + b x + tau T + d T x,
x = s - c, T = 1[s > c]; rho = exp(tau); EP sanduiche HC0; IC 95% e p pela
normal. Complemento exato: binomial 1/2 com constante local e h = 0,020.

Resultado exploratorio, condicional a A1. Nao e efeito causal estabelecido;
o contraste e o incentivo marginal anunciado de R$ 5 mil (possivelmente um
pacote), nao a participacao no PMM-E.

Sem scipy/statsmodels: IRLS de Poisson em numpy, normal via math.erf/erfc e
binomial exata via math.comb.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROTOCOLO = ROOT / "output" / "rdd_bolsa" / "protocolo_escore_administrativo.json"
ESCORE = ROOT / "output" / "aquisicao" / "a07_ivs_administrativo_municipio.csv"
MANIFESTO_A07 = ROOT / "output" / "aquisicao" / "a07_manifesto_ivs_administrativo.json"
RELACAO_NOMINAL = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
OUT_ESTIMATIVAS = ROOT / "output" / "rdd_bolsa" / "E1_densidade_estimativas.csv"
OUT_CONTAGENS = ROOT / "output" / "rdd_bolsa" / "E1_densidade_contagens.csv"
OUT_RESUMO = ROOT / "output" / "rdd_bolsa" / "E1_densidade_resumo.json"

DATA_EXECUCAO = "2026-10-14"

POPULACOES = {
    1: [("c1_ch1", "data/raw/aquisicao/vagas/2025_ciclo1_chamada1_vagas.xlsx")],
    2: [
        ("c2_ch1", "data/raw/pmm_e/2026_ciclo2_chamada1_vagas_retificadas.xlsx"),
        ("c2_ch2", "data/raw/pmm_e/2026_ciclo2_chamada2_vagas.xlsx"),
    ],
}
CICLOS_VALIDOS = {"1", "2", "3"}

# Escore em milesimos inteiros, para evitar erro de ponto flutuante nas janelas.
CORTES_MIL = [300, 400]
PLACEBOS_MIL = [250, 350, 450]
H_PRINCIPAL_MIL = 50
H_EXATO_MIL = 20
FAIXA_CONTAGENS_MIL = (200, 500)

ALFA = 0.05
MAX_ITER = 100
TOL_DEVIANCE = 1e-12


# --------------------------------------------------------------------------
# Utilitarios
# --------------------------------------------------------------------------
def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(65536):
            h.update(bloco)
    return h.hexdigest()


def ler_quadro(caminho: str) -> pd.DataFrame:
    """Copiada de 04_portao_r1_escore_administrativo.py."""
    bruto = pd.read_excel(ROOT / caminho, header=None)
    linha = next(
        i for i in range(10) if bruto.iloc[i].astype(str).str.upper().str.contains("FAIXA").any()
    )
    df = pd.read_excel(ROOT / caminho, header=linha)
    df.columns = [str(c).strip().upper() for c in df.columns]
    col_ibge = next(c for c in df.columns if c.startswith("IBGE"))
    col_faixa = next(c for c in df.columns if "FAIXA" in c)
    m = df[[col_ibge, col_faixa]].dropna()
    m.columns = ["co_ibge", "faixa_anunciada"]
    m["co_ibge"] = m["co_ibge"].astype(str).str.split(".").str[0].str[:6]
    m = m[m["co_ibge"].str.isnumeric()]
    m["faixa_anunciada"] = m["faixa_anunciada"].astype(str).str.strip().str.upper()
    return m.drop_duplicates()


def ler_relacao_nominal() -> pd.DataFrame:
    """Le apenas `co_ibge` e `ciclo` da relacao nominal (nenhum dado pessoal)."""
    with zipfile.ZipFile(RELACAO_NOMINAL) as z:
        nomes = [n for n in z.namelist() if n.lower().endswith(".csv")]
        assert len(nomes) == 1, f"esperado um CSV no zip, encontrado {nomes}"
        conteudo = z.read(nomes[0])
    rel = pd.read_csv(
        io.BytesIO(conteudo), sep=";", encoding="latin1", dtype=str, usecols=["co_ibge", "ciclo"]
    )
    rel["co_ibge"] = rel["co_ibge"].str.strip()
    rel["ciclo"] = rel["ciclo"].str.strip()
    return rel


def fmt_mil(v: int) -> str:
    return f"{v / 1000:.3f}"


def phi_sup(z: float) -> float:
    """P(Z > z) para Z normal padrao."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def quantil_normal(p: float) -> float:
    """Inversa da normal padrao por bisseccao sobre math.erf (deterministica)."""
    lo, hi = -10.0, 10.0
    for _ in range(200):
        meio = 0.5 * (lo + hi)
        if 0.5 * (1.0 + math.erf(meio / math.sqrt(2.0))) < p:
            lo = meio
        else:
            hi = meio
    return 0.5 * (lo + hi)


Z975 = quantil_normal(1.0 - ALFA / 2.0)


def holm(pvals: list[float]) -> list[float]:
    m = len(pvals)
    ordem = sorted(range(m), key=lambda i: pvals[i])
    ajust = [float("nan")] * m
    acumulado = 0.0
    for posto, i in enumerate(ordem):
        acumulado = max(acumulado, min(1.0, (m - posto) * pvals[i]))
        ajust[i] = acumulado
    return ajust


# --------------------------------------------------------------------------
# Binomial exata
# --------------------------------------------------------------------------
def binom_pmf(k: int, n: int, p: float) -> float:
    if p <= 0.0:
        return 1.0 if k == 0 else 0.0
    if p >= 1.0:
        return 1.0 if k == n else 0.0
    return math.comb(n, k) * p**k * (1.0 - p) ** (n - k)


def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(binom_pmf(i, n, p) for i in range(0, k + 1))


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k)."""
    return sum(binom_pmf(i, n, p) for i in range(k, n + 1))


def binom_teste_bicaudal(k: int, n: int, p0: float = 0.5) -> float:
    """Teste exato bicaudal (soma das probabilidades <= P(X = k)), como binom.test do R."""
    d = binom_pmf(k, n, p0)
    tol = 1.0 + 1e-7
    return min(1.0, sum(binom_pmf(i, n, p0) for i in range(n + 1) if binom_pmf(i, n, p0) <= d * tol))


def clopper_pearson(k: int, n: int, alfa: float = ALFA) -> tuple[float, float]:
    """IC exato de Clopper-Pearson para a proporcao, por bisseccao nas somas binomiais."""
    def bissec(f, alvo: float) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(200):
            meio = 0.5 * (lo + hi)
            if f(meio) < alvo:
                lo = meio
            else:
                hi = meio
        return 0.5 * (lo + hi)

    inf = 0.0 if k == 0 else bissec(lambda p: binom_sf(k, n, p), alfa / 2.0)  # crescente em p
    sup = 1.0 if k == n else bissec(lambda p: 1.0 - binom_cdf(k, n, p), 1.0 - alfa / 2.0)
    return inf, sup


# --------------------------------------------------------------------------
# Poisson log-linear por IRLS com EP sanduiche HC0
# --------------------------------------------------------------------------
def poisson_irls(X: np.ndarray, y: np.ndarray) -> dict:
    n, p = X.shape
    beta = np.zeros(p)
    beta[0] = math.log(max(y.mean(), 1e-8))
    dev_ant = math.inf
    convergiu = False
    it = 0
    for it in range(1, MAX_ITER + 1):
        eta = X @ beta
        mu = np.exp(eta)
        z = eta + (y - mu) / mu
        XtW = X.T * mu
        beta = np.linalg.solve(XtW @ X, XtW @ z)
        mu = np.exp(X @ beta)
        with np.errstate(divide="ignore", invalid="ignore"):
            termo = np.where(y > 0, y * np.log(y / mu), 0.0)
        dev = float(2.0 * np.sum(termo - (y - mu)))
        if abs(dev - dev_ant) / (abs(dev) + 0.1) < TOL_DEVIANCE:
            convergiu = True
            break
        dev_ant = dev
    mu = np.exp(X @ beta)
    escore = X.T @ (y - mu)
    A = (X.T * mu) @ X
    B = (X.T * (y - mu) ** 2) @ X
    A_inv = np.linalg.inv(A)
    V = A_inv @ B @ A_inv
    return {
        "beta": beta,
        "V_hc0": V,
        "convergiu": bool(convergiu and np.max(np.abs(escore)) < 1e-6 and np.all(np.isfinite(beta))),
        "iteracoes": it,
        "deviance": dev,
        "max_abs_escore": float(np.max(np.abs(escore))),
    }


def mle_finita_no_lado(x: np.ndarray, y: np.ndarray, linear: bool) -> tuple[bool, str]:
    """Condicao de existencia do MLE de Poisson em um lado da janela.

    Constante: requer contagem total > 0. Linear (a + b x): requer contagem
    total > 0 e media de x ponderada pelas contagens estritamente dentro de
    (min x, max x); do contrario a inclinacao diverge.
    """
    total = float(y.sum())
    if total <= 0:
        return False, "contagem zero no lado"
    if linear:
        xm = float((x * y).sum() / total)
        if not (x.min() < xm < x.max()):
            return False, "contagens concentradas no mass point extremo do lado; inclinacao sem MLE finito"
    return True, ""


def ajustar_poisson(cont: pd.Series, c_mil: int, h_mil: int, linear: bool, excluir_corte: bool) -> dict:
    """Ajusta o Poisson log-linear nos mass points da janela.

    Lado inferior: c - h + 1 .. c (milesimos), ou .. c - 1 se excluir_corte.
    Lado superior: c + 1 .. c + h.
    """
    fim_inf = c_mil - 1 if excluir_corte else c_mil
    s_inf = np.arange(c_mil - h_mil + 1, fim_inf + 1)
    s_sup = np.arange(c_mil + 1, c_mil + h_mil + 1)
    s = np.concatenate([s_inf, s_sup])
    y = cont.reindex(s, fill_value=0).to_numpy(dtype=float)
    T = (s > c_mil).astype(float)
    x = (s - c_mil) / 1000.0
    n_esq = int(y[T == 0].sum())
    n_dir = int(y[T == 1].sum())
    base = {
        "n_esq": n_esq,
        "n_dir": n_dir,
        "mass_points_esq": int(len(s_inf)),
        "mass_points_dir": int(len(s_sup)),
        "mass_points_esq_com_contagem": int((y[T == 0] > 0).sum()),
        "mass_points_dir_com_contagem": int((y[T == 1] > 0).sum()),
    }
    problemas = []
    for lado, msk in (("inferior", T == 0), ("superior", T == 1)):
        ok, motivo = mle_finita_no_lado(x[msk], y[msk], linear)
        if not ok:
            problemas.append(f"lado {lado}: {motivo}")
    if problemas:
        return {**base, "estimado": False, "nota": "nao estimado: " + "; ".join(problemas)}

    if linear:
        X = np.column_stack([np.ones_like(x), x, T, T * x])
    else:
        X = np.column_stack([np.ones_like(x), T])
    fit = poisson_irls(X, y)
    if not fit["convergiu"]:
        return {
            **base,
            "estimado": False,
            "nota": f"nao estimado: IRLS nao convergiu em {fit['iteracoes']} iteracoes "
                    f"(max |escore| = {fit['max_abs_escore']:.3g})",
            "iteracoes": fit["iteracoes"],
        }
    j = 2 if linear else 1
    tau = float(fit["beta"][j])
    ep = float(math.sqrt(fit["V_hc0"][j, j]))
    z = tau / ep
    return {
        **base,
        "estimado": True,
        "tau": tau,
        "ep_tau_hc0": ep,
        "z": z,
        "rho": math.exp(tau),
        "ic_inf": math.exp(tau - Z975 * ep),
        "ic_sup": math.exp(tau + Z975 * ep),
        "p_valor": 2.0 * phi_sup(abs(z)),
        "coeficientes": {nome: float(v) for nome, v in zip(
            ["a", "b", "tau", "d"] if linear else ["a", "tau"], fit["beta"])},
        "iteracoes": fit["iteracoes"],
        "deviance": fit["deviance"],
        "max_abs_escore": fit["max_abs_escore"],
        "nota": f"IRLS convergiu em {fit['iteracoes']} iteracoes",
    }


def teste_exato(cont: pd.Series, c_mil: int, h_mil: int) -> dict:
    s_inf = np.arange(c_mil - h_mil + 1, c_mil + 1)
    s_sup = np.arange(c_mil + 1, c_mil + h_mil + 1)
    n_esq = int(cont.reindex(s_inf, fill_value=0).sum())
    n_dir = int(cont.reindex(s_sup, fill_value=0).sum())
    n = n_esq + n_dir
    base = {"n_esq": n_esq, "n_dir": n_dir, "mass_points_esq": int(len(s_inf)), "mass_points_dir": int(len(s_sup))}
    if n == 0:
        return {**base, "estimado": False, "nota": "nao estimado: nenhuma contagem na janela"}
    p = binom_teste_bicaudal(n_dir, n, 0.5)
    pi_inf, pi_sup = clopper_pearson(n_dir, n)
    rho = n_dir / n_esq if n_esq > 0 else math.inf
    nota = ("binomial exata n_dir | n ~ Bin(n, 1/2) sob H0; rho = n_dir/n_esq (lados com 20 mass points); "
            "IC = Clopper-Pearson para pi = rho/(1+rho), transformado")
    if n_esq == 0 or n_dir == 0:
        nota += "; um lado com contagem zero: rho no limite (0 ou infinito)"
    return {
        **base,
        "estimado": True,
        "rho": rho,
        "ic_inf": pi_inf / (1.0 - pi_inf) if pi_inf < 1.0 else math.inf,
        "ic_sup": pi_sup / (1.0 - pi_sup) if pi_sup < 1.0 else math.inf,
        "p_valor": p,
        "nota": nota,
    }


# --------------------------------------------------------------------------
# Especificacoes do protocolo
# --------------------------------------------------------------------------
ESPECIFICACOES = [
    # (codigo, papel no ciclo 1, h_mil, tipo, linear, excluir_corte, cortes)
    ("poisson_linear_h050", "principal", 50, "poisson", True, False, CORTES_MIL),
    ("binomial_exata_constante_h020", "exato", 20, "exato", False, False, CORTES_MIL),
    ("poisson_linear_h030", "sensibilidade", 30, "poisson", True, False, CORTES_MIL),
    ("poisson_linear_h080", "sensibilidade", 80, "poisson", True, False, CORTES_MIL),
    ("poisson_constante_h050", "sensibilidade", 50, "poisson", False, False, CORTES_MIL),
    ("poisson_linear_h050_sem_mass_point_do_corte", "sensibilidade", 50, "poisson", True, True, CORTES_MIL),
    ("poisson_linear_h050", "placebo", 50, "poisson", True, False, PLACEBOS_MIL),
]


def main() -> None:
    protocolo = json.loads(PROTOCOLO.read_text(encoding="utf-8"))
    assert protocolo["data_congelamento"] == "2026-10-14"

    # Proveniencia da relacao nominal: hash igual ao do manifesto a07.
    manifesto = json.loads(MANIFESTO_A07.read_text(encoding="utf-8"))
    sha_manifesto = next(f["sha256"] for f in manifesto["fontes"] if f["id"] == "pmme_relacao_nominal_ativos")
    sha_rel = sha256(RELACAO_NOMINAL)
    assert sha_rel == sha_manifesto, "relacao nominal difere da versao registrada no manifesto a07"

    # Escore administrativo: unico por municipio, grade de 0,001.
    escore = pd.read_csv(ESCORE, dtype={"co_ibge": str})[["co_ibge", "ivs_admin"]]
    assert escore["co_ibge"].is_unique
    assert escore["ivs_admin"].notna().all()
    escore["s_mil"] = (escore["ivs_admin"] * 1000).round().astype(int)
    assert np.allclose(escore["ivs_admin"] * 1000, escore["s_mil"], atol=1e-6), "escore fora da grade de 0,001"

    # Outcome D_k a partir de co_ibge e ciclo.
    rel = ler_relacao_nominal()
    valores_ciclo = {str(k): int(v) for k, v in rel["ciclo"].value_counts(dropna=False).sort_index().items()}
    assert set(rel["ciclo"].dropna().unique()) <= CICLOS_VALIDOS, f"valores inesperados de ciclo: {valores_ciclo}"
    assert rel["ciclo"].notna().all() and rel["co_ibge"].notna().all()
    assert rel["co_ibge"].str.fullmatch(r"\d{6}").all()

    estimativas = []
    diagnosticos = []
    contagens = []
    resumo_pop = {}
    fontes_quadros = {}

    for ciclo, quadros in POPULACOES.items():
        municipios = set()
        for chave, caminho in quadros:
            q = ler_quadro(caminho)
            municipios |= set(q["co_ibge"])
            fontes_quadros[caminho] = {"quadro": chave, "sha256": sha256(ROOT / caminho),
                                       "municipios": int(q["co_ibge"].nunique())}
        pop = pd.DataFrame({"co_ibge": sorted(municipios)})
        com_D = set(rel.loc[rel["ciclo"] == str(ciclo), "co_ibge"])
        pop["D"] = pop["co_ibge"].isin(com_D).astype(int)
        pop = pop.merge(escore, on="co_ibge", how="left")

        # Propriedade do protocolo: todo municipio com D_k = 1 tem escore observado.
        sem_escore = pop[(pop["D"] == 1) & pop["ivs_admin"].isna()]
        assert sem_escore.empty, f"ciclo {ciclo}: {len(sem_escore)} municipios com D_k=1 sem escore"

        trat = pop[pop["D"] == 1]
        cont = trat.groupby("s_mil").size()

        resumo_pop[f"P{ciclo}"] = {
            "quadros": [c for c, _ in quadros],
            "municipios": int(len(pop)),
            "municipios_com_escore": int(pop["ivs_admin"].notna().sum()),
            "municipios_D1": int(pop["D"].sum()),
            "municipios_com_ciclo_k_fora_de_P_k": int(len(com_D - municipios)),
            "nota_fora_de_P_k": "municipios com especialista ativo do ciclo k que nao estao no(s) quadro(s) de P_k; "
                                "fora da populacao do protocolo, nao entram em E1",
        }

        for s_mil in range(FAIXA_CONTAGENS_MIL[0], FAIXA_CONTAGENS_MIL[1] + 1):
            contagens.append({"ciclo": ciclo, "s": fmt_mil(s_mil), "n_D": int(cont.get(s_mil, 0))})

        for codigo, papel1, h_mil, tipo, linear, excluir, cortes in ESPECIFICACOES:
            for c_mil in cortes:
                if tipo == "exato":
                    r = teste_exato(cont, c_mil, h_mil)
                else:
                    r = ajustar_poisson(cont, c_mil, h_mil, linear, excluir)
                papel = papel1
                nota = r["nota"]
                if ciclo == 2:
                    nota = "replicacao ciclo 2 (P2, D_2), sem Holm; " + nota
                    if papel1 == "principal":
                        papel = "replicacao"
                estimativas.append({
                    "ciclo": ciclo,
                    "corte": fmt_mil(c_mil),
                    "papel": papel,
                    "especificacao": codigo,
                    "h": fmt_mil(h_mil),
                    "n_esq": r["n_esq"],
                    "n_dir": r["n_dir"],
                    "rho": r.get("rho", float("nan")),
                    "ic_inf": r.get("ic_inf", float("nan")),
                    "ic_sup": r.get("ic_sup", float("nan")),
                    "p_valor": r.get("p_valor", float("nan")),
                    "p_holm": float("nan"),
                    "nota": nota,
                })
                diagnosticos.append({"ciclo": ciclo, "corte": fmt_mil(c_mil), "papel": papel,
                                     "especificacao": codigo, "h": fmt_mil(h_mil),
                                     **{k: v for k, v in r.items() if k != "nota"}, "nota": nota})

    est = pd.DataFrame(estimativas)

    # Holm sobre os dois cortes do ciclo 1 (estimador principal).
    msk = (est["ciclo"] == 1) & (est["papel"] == "principal")
    holm_status = "aplicado aos dois cortes do ciclo 1"
    if msk.sum() == 2 and est.loc[msk, "p_valor"].notna().all():
        est.loc[msk, "p_holm"] = holm(est.loc[msk, "p_valor"].tolist())
    else:
        holm_status = "nao aplicado: estimativa principal ausente em algum corte do ciclo 1"

    est.to_csv(OUT_ESTIMATIVAS, index=False, float_format="%.6g")
    pd.DataFrame(contagens).to_csv(OUT_CONTAGENS, index=False)

    def linha(ciclo: int, corte: str, papel: str) -> dict:
        r = est[(est["ciclo"] == ciclo) & (est["corte"] == corte) & (est["papel"] == papel)
                & (est["especificacao"] == "poisson_linear_h050")].iloc[0]
        return {k: (None if isinstance(v, float) and math.isnan(v) else (v.item() if hasattr(v, "item") else v))
                for k, v in r.items()}

    resumo = {
        "documento": "E1 - razao de densidades laterais do escore administrativo de IVS",
        "status": "EXPLORATORIO_CONDICIONAL_A1",
        "data_execucao": DATA_EXECUCAO,
        "script": str(Path(__file__).resolve().relative_to(ROOT)),
        "protocolo": {"arquivo": str(PROTOCOLO.relative_to(ROOT)), "sha256": sha256(PROTOCOLO),
                      "data_congelamento": protocolo["data_congelamento"]},
        "outcomes_abertos": True,
        "outcome": "D_k: presenca no municipio de especialista ativo com ingresso no ciclo k na Relacao Nominal "
                   "Ativos - PMM-E de 09/10/2026; nao e preenchimento de vaga nem retencao individual",
        "estimando": protocolo["E1_densidade"]["estimando"],
        "premissa_A1": protocolo["E1_densidade"]["premissa_A1"],
        "contraste": protocolo["linguagem"]["contraste"],
        "linguagem": protocolo["linguagem"]["E1_E2"],
        "fontes": {
            str(PROTOCOLO.relative_to(ROOT)): {"sha256": sha256(PROTOCOLO)},
            str(ESCORE.relative_to(ROOT)): {"sha256": sha256(ESCORE), "municipios": int(len(escore)),
                                            "colunas_lidas": ["co_ibge", "ivs_admin"]},
            str(MANIFESTO_A07.relative_to(ROOT)): {"sha256": sha256(MANIFESTO_A07)},
            str(RELACAO_NOMINAL.relative_to(ROOT)): {
                "sha256": sha_rel, "sha256_confere_manifesto_a07": True,
                "versao": "09/10/2026", "linhas": int(len(rel)), "colunas_lidas": ["co_ibge", "ciclo"],
                "valores_ciclo": valores_ciclo,
            },
            **fontes_quadros,
        },
        "populacoes": resumo_pop,
        "ciclo_3": "excluido (prospectivo e congelado)",
        "metodo": {
            "unidade": "mass point de 0,001 do escore (inteiros em milesimos); contagem de municipios com D_k = 1",
            "janela": "lado inferior c-h+0,001..c (o corte pertence ao lado inferior); superior c+0,001..c+h; "
                      "mass points com contagem zero incluidos",
            "principal": protocolo["E1_densidade"]["estimador_principal"],
            "irls": {"max_iter": MAX_ITER, "tol_deviance_relativa": TOL_DEVIANCE,
                     "criterio_convergencia": "variacao relativa da deviance e max |X'(y-mu)| < 1e-6"},
            "existencia_mle": "nao se estima quando um lado tem contagem zero ou, no modelo linear, quando a "
                              "media de x ponderada pelas contagens nao fica estritamente dentro do lado",
            "normal": {"z_0975": Z975, "fonte": "bisseccao sobre math.erf"},
            "exato": "binomial 1/2 exata bicaudal (soma das probabilidades <= P(X=k)); IC de Clopper-Pearson "
                     "para pi = n_dir/n transformado em rho = pi/(1-pi)",
            "multiplicidade": f"Holm {holm_status}; nenhum outro ajuste",
            "papel": "ciclo 1: principal/exato/sensibilidade/placebo; ciclo 2: o estimador principal nos cortes "
                     "reais leva papel 'replicacao' e as demais especificacoes mantem o papel do ciclo 1",
        },
        "estimativas_principais_ciclo1": {c: linha(1, c, "principal") for c in ("0.300", "0.400")},
        "replicacao_ciclo2": {c: linha(2, c, "replicacao") for c in ("0.300", "0.400")},
        "diagnosticos": diagnosticos,
        "saidas": {
            str(OUT_ESTIMATIVAS.relative_to(ROOT)): {"linhas": int(len(est))},
            str(OUT_CONTAGENS.relative_to(ROOT)): {"linhas": int(len(contagens)),
                                                   "faixa_s": [fmt_mil(FAIXA_CONTAGENS_MIL[0]),
                                                               fmt_mil(FAIXA_CONTAGENS_MIL[1])]},
        },
        "regra_de_relato": protocolo["regra_de_relato"],
    }
    OUT_RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=float) + "\n", encoding="utf-8")

    pd.set_option("display.width", 220)
    print(json.dumps(resumo_pop, ensure_ascii=False, indent=2))
    print(est.drop(columns=["nota"]).to_string(index=False))
    for _, r in est[est["rho"].isna()].iterrows():
        print("NAO ESTIMADO:", r["ciclo"], r["corte"], r["especificacao"], r["nota"])


if __name__ == "__main__":
    main()
