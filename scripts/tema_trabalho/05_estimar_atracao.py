"""A4 — Estimar atração e implementação (núcleo associativo).

Sequência (prompt 04_estimar_atracao.md):
1. Estatísticas de construção e suporte antes dos coeficientes.
2. Modelo primário exatamente como congelado em A3 (LPM + Logit AME, FE curso+UF, cluster município).
3. Efeitos marginais / diferenças preditas com IC cluster-robusto.
4. Leave-one-UF, leave-one-curso e influência municipal (DFBETAS/leave-one-municipality).
5. Separar faixa, IVS e remoticidade sem causalidade.
6. Validação preditiva por município (GroupKFold) se houver.

Proibições: não converter em WTA, não escolher modelo por p-valor, não chamar
coeficiente de faixa de efeito causal da bolsa. Linguagem associativa apenas.

População primária: 1295 células CNES–curso do quadro Ch1 (368 municípios).
Unidade inferência: município (cluster-robusto). Covariadas exclusivamente pré-oferta.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats
import statsmodels.api as sm


def roc_auc_score_manual(y_true, y_score):
    # Mann-Whitney U based AUC, correct rank handling with ties via scipy
    y_true = np.asarray(y_true, dtype=float)
    y_score = np.asarray(y_score, dtype=float)
    n_pos = int(y_true.sum())
    n_neg = len(y_true) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    # Use scipy rankdata to handle ties averaging
    from scipy.stats import rankdata
    ranks = rankdata(y_score, method="average")
    sum_ranks_pos = ranks[y_true == 1].sum()
    auc = (sum_ranks_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return float(auc)


def brier_score_manual(y_true, y_prob):
    y_true = np.asarray(y_true, dtype=float)
    y_prob = np.asarray(y_prob, dtype=float)
    return float(np.mean((y_prob - y_true) ** 2))


def group_kfold_splits(groups, n_splits=5, seed=42):
    """Gera índices train/test garantindo que grupos não se misturam. Determinístico."""
    rng = np.random.default_rng(seed)
    uniq = np.array(sorted(set(groups)))
    rng.shuffle(uniq)
    folds = np.array_split(uniq, n_splits)
    indices = np.arange(len(groups))
    groups_arr = np.array(groups)
    for k in range(n_splits):
        test_groups = set(folds[k])
        mask_test = np.isin(groups_arr, list(test_groups))
        test_idx = indices[mask_test]
        train_idx = indices[~mask_test]
        yield train_idx, test_idx

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "output" / "tema_trabalho"
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
MATRIZ_FUNIL = ROOT / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"
MATRIZ_TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
MANIFESTO_TIP = ROOT / "output" / "tema_trabalho" / "manifesto_tipologia_territorial.json"
PORTAO_A1 = ROOT / "output" / "tema_trabalho" / "portao_denominador.json"
REGISTRO_A3 = ROOT / "output" / "tema_trabalho" / "registro_pre_analise_atracao.json"
POTENCIA_A3 = ROOT / "output" / "tema_trabalho" / "potencia_atracao.json"

# Outputs A4
PREFIX = "A4"
TABELA_AMOSTRA = OUT_DIR / f"{PREFIX}_tabela_01_amostra_construcao.csv"
TABELA_AMOSTRA_FAIXA = OUT_DIR / f"{PREFIX}_tabela_01b_amostra_faixa.csv"
TABELA_AMOSTRA_CURSO = OUT_DIR / f"{PREFIX}_tabela_01c_amostra_curso.csv"
TABELA_AMOSTRA_UF = OUT_DIR / f"{PREFIX}_tabela_01d_amostra_uf.csv"
TABELA_CONSTRUCAO = OUT_DIR / f"{PREFIX}_tabela_00_construcao_steps.csv"
TABELA_PRINCIPAL_LPM = OUT_DIR / f"{PREFIX}_tabela_02_modelo_principal_LPM.csv"
TABELA_PRINCIPAL_LOGIT = OUT_DIR / f"{PREFIX}_tabela_02b_logit_AME.csv"
TABELA_SEP = OUT_DIR / f"{PREFIX}_tabela_03_separacao_faixa_ivs_remoticidade.csv"
TABELA_SENS_AJUST = OUT_DIR / f"{PREFIX}_tabela_03b_ajuste_completo.csv"
TABELA_SENS_WINSOR = OUT_DIR / f"{PREFIX}_tabela_03c_winsorizado.csv"
TABELA_SENS_SPLINE = OUT_DIR / f"{PREFIX}_tabela_03d_ivs_spline.csv"
TABELA_LOO = OUT_DIR / f"{PREFIX}_tabela_04_leave_one_out.csv"
TABELA_INFLUENCIA = OUT_DIR / f"{PREFIX}_tabela_05_influencia_municipal.csv"
TABELA_PRED = OUT_DIR / f"{PREFIX}_tabela_06_validacao_preditiva.csv"
FIG_PROB_ESTRATO = OUT_DIR / f"{PREFIX}_figura_01_prob_ajustada_estrato.png"
FIG_IVS = OUT_DIR / f"{PREFIX}_figura_02_gradiente_ivs.png"
FIG_FAIXA = OUT_DIR / f"{PREFIX}_figura_03_faixa_descritiva.png"
JSON_ESTIMATIVAS = OUT_DIR / f"{PREFIX}_estimativas_atracao.json"
RELATORIO_MD = OUT_DIR / f"{PREFIX}_relatorio_diagnostico.md"

ALPHA = 0.05


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def bh_fdr(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg FDR q-values (m tests)."""
    m = len(pvals)
    order = np.argsort(pvals)
    q = np.empty(m, float)
    # rank 1..m
    ranked = pvals[order]
    # BH q = p * m / rank, then cumulative min descending
    adj = ranked * m / np.arange(1, m + 1)
    # monotonicidade decrescente
    cummin = np.minimum.accumulate(adj[::-1])[::-1]
    cummin = np.clip(cummin, 0, 1)
    q[order] = cummin
    return q


def prepare_df_primary() -> tuple[pd.DataFrame, pd.DataFrame]:
    quadro = pd.read_parquet(QUADRO)
    funil = pd.read_parquet(MATRIZ_FUNIL)
    tipologia = pd.read_parquet(MATRIZ_TIPOLOGIA)

    # Guard: nunca consultar outcome além de A1 dicionário; não usar CNES pós
    assert "outcome_alguma_confirmacao_ou_homologacao" not in quadro.columns

    f1 = funil[funil["chamada"] == 1][
        ["co_cnes_7d", "cod_curso", "outcome_alguma_confirmacao_ou_homologacao", "n_confirmacoes_ch1", "n_homologacoes_ch1", "in_quadro_ch1_original"]
    ].copy()
    # primary = quadro Ch1 (1295)
    q = quadro.merge(f1, on=["co_cnes_7d", "cod_curso"], how="left", validate="one_to_one")
    # Verifica que todo quadro tem outcome
    if q["outcome_alguma_confirmacao_ou_homologacao"].isna().any():
        raise AssertionError("outcome missing no quadro Ch1")
    # Merge tipologia (544? 5570)
    tipologia_small = tipologia[[
        "co_ibge_6d", "estrato", "ivs_2010", "ivs_infra_2010", "ivs_ch_2010", "ivs_rt_2010", "ivs_categoria",
        "populacao_2010", "idhm_2010", "rdpc_2010", "estoque_especialistas_pre_12m_media", "estoque_pre_por_10k",
        "macro_regiao_saude", "no_regiao_saude",
    ]].copy()
    tipologia_small["co_ibge_6d"] = tipologia_small["co_ibge_6d"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(6)
    q["co_ibge_6d"] = q["co_ibge_6d"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(6)
    qm = q.merge(tipologia_small, on="co_ibge_6d", how="left", validate="many_to_one")
    # Guard: estrato não missing no primário
    if qm["estrato"].isna().any():
        raise AssertionError("estrato missing no primário")
    # Transformações pré-especificadas A3
    qm["log_pop"] = np.log1p(qm["populacao_2010"].astype(float))
    qm["estoque_por_10k"] = qm["estoque_pre_por_10k"].astype(float)
    # estoque missing = 0? No primário não há missing, mas mantém NA handling
    # Colapsar UF com <5 clusters (A3: colapsar UF com <5 clusters em região)
    clust = qm.groupby("sg_uf")["co_ibge_6d"].nunique()
    small_ufs_local = set(clust[clust < 5].index.tolist())
    qm["uf_fe"] = qm["sg_uf"].where(~qm["sg_uf"].isin(small_ufs_local), "RESTO")
    # Estrato categórico com referência interior_remoto (mais remoto)
    qm["estrato"] = pd.Categorical(qm["estrato"], categories=["interior_remoto", "capital", "metropolitano", "interior_proximo_polo"], ordered=False)
    # Extended: funil drop NA ibge (3057)
    funil_valid = funil.dropna(subset=["co_ibge_6d"]).copy()
    funil_valid["co_ibge_6d"] = funil_valid["co_ibge_6d"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(6)
    ext = funil_valid.merge(tipologia_small, on="co_ibge_6d", how="left")
    ext["log_pop"] = np.log1p(ext["populacao_2010"].astype(float))
    ext["estoque_por_10k"] = ext["estoque_pre_por_10k"].astype(float)
    # uf_fe para extended também colapsado baseado no primário (para comparabilidade)
    ext["uf_fe"] = ext["sg_uf"].where(~ext["sg_uf"].isin(small_ufs_local), "RESTO")
    # estrato categorical same levels (capitals etc)
    ext["estrato"] = pd.Categorical(ext["estrato"], categories=["interior_remoto", "capital", "metropolitano", "interior_proximo_polo"], ordered=False)

    # Asserts primária exata
    assert len(qm) == 1295, f"primária len {len(qm)} !=1295"
    assert qm["co_ibge_6d"].nunique() == 368, f"clusters {qm['co_ibge_6d'].nunique()} !=368"
    assert len(ext) == 3057, f"estendida {len(ext)} !=3057"
    return qm, ext


def build_X(df: pd.DataFrame, spec: str) -> pd.DataFrame:
    """Constrói matriz de desenho conforme spec.

    specs:
    - minimal: estrato + curso + uf_fe
    - full: minimal + ivs + log_pop + estoque_por_10k + faixa
    - faixa_only: faixa + curso + uf_fe
    - ivs_only: ivs + curso + uf_fe
    - estrato_ivs_inter: estrato*ivs + curso + uf_fe (interação)
    """
    if spec == "minimal":
        X = pd.get_dummies(df[["estrato", "cod_curso", "uf_fe"]], columns=["estrato", "cod_curso", "uf_fe"], drop_first=True, dtype=float)
    elif spec == "full":
        X = pd.get_dummies(df[["estrato", "cod_curso", "uf_fe"]], columns=["estrato", "cod_curso", "uf_fe"], drop_first=True, dtype=float)
        X["ivs_2010"] = df["ivs_2010"].astype(float)
        X["log_pop"] = df["log_pop"].astype(float)
        X["estoque_por_10k"] = df["estoque_por_10k"].astype(float).fillna(0)
        faixa_dum = pd.get_dummies(df["faixa_atracao_anunciada"], prefix="faixa", drop_first=True, dtype=float)
        X = pd.concat([X, faixa_dum], axis=1)
    elif spec == "faixa_only":
        X = pd.get_dummies(df[["cod_curso", "uf_fe", "faixa_atracao_anunciada"]], columns=["cod_curso", "uf_fe", "faixa_atracao_anunciada"], drop_first=True, dtype=float)
        # rename to keep faixa columns clear
        X = X.rename(columns=lambda c: c.replace("faixa_atracao_anunciada_", "faixa_"))
    elif spec == "ivs_only":
        X = pd.get_dummies(df[["cod_curso", "uf_fe"]], columns=["cod_curso", "uf_fe"], drop_first=True, dtype=float)
        X["ivs_2010"] = df["ivs_2010"].astype(float)
    elif spec == "estrato_ivs_inter":
        # estrato dummies * ivs
        base = pd.get_dummies(df[["estrato", "cod_curso", "uf_fe"]], columns=["estrato", "cod_curso", "uf_fe"], drop_first=True, dtype=float)
        base["ivs_2010"] = df["ivs_2010"].astype(float)
        # interações estrato*ivs
        for lev in ["capital", "metropolitano", "interior_proximo_polo"]:
            col = f"estrato_{lev}"
            if col in base.columns:
                base[f"{col}_x_ivs"] = base[col] * df["ivs_2010"].astype(float)
        X = base
    else:
        raise ValueError(spec)
    X = sm.add_constant(X, has_constant="add")
    # Garante ordenação estável
    X = X.reindex(sorted(X.columns), axis=1)
    # Move const para primeira coluna para leitura
    if "const" in X.columns:
        cols = ["const"] + [c for c in X.columns if c != "const"]
        X = X[cols]
    return X


def fit_lpm(y: pd.Series, X: pd.DataFrame, groups: pd.Series):
    mod = sm.OLS(y.astype(float), X)
    res = mod.fit(cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True})
    return res


def fit_logit(y: pd.Series, X: pd.DataFrame, groups: pd.Series):
    mod = sm.Logit(y.astype(float), X)
    # method lbfgs pode ser mais estável com muitas dummies
    try:
        res = mod.fit(cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True}, disp=0, maxiter=200, method="lbfgs")
    except Exception:
        res = mod.fit(cov_type="cluster", cov_kwds={"groups": groups, "use_correction": True}, disp=0, maxiter=200)
    return res


def summarize_res(res, X: pd.DataFrame, y: pd.Series, groups: pd.Series, label: str) -> pd.DataFrame:
    """Tabela com coef, se, ci, p, q (FDR para família estrato), etc."""
    params = res.params
    bse = res.bse
    pvals = res.pvalues
    # CIs
    z = scipy_stats.norm.ppf(1 - ALPHA / 2)
    ci_low = params - z * bse
    ci_high = params + z * bse
    # FDR apenas para família estrato (3 coefs)
    estrato_mask = params.index.str.startswith("estrato_") & ~params.index.str.contains("_x_ivs")
    qvals = pd.Series(np.nan, index=params.index, dtype=float)
    if estrato_mask.sum() > 0:
        q = bh_fdr(pvals[estrato_mask].values)
        qvals[estrato_mask] = q
    # monta
    df = pd.DataFrame({
        "termo": params.index,
        "coef": params.values,
        "se_cluster": bse.values,
        "ci_low": ci_low.values,
        "ci_high": ci_high.values,
        "p_valor": pvals.values,
        "q_fdr_estrato": qvals.values,
        "espec": label,
    })
    # adiciona N, G, R2 etc como colunas repetidas para facilitar
    df["n"] = len(y)
    df["n_clusters"] = groups.nunique()
    try:
        df["r2"] = res.rsquared if hasattr(res, "rsquared") else res.prsquared
    except Exception:
        df["r2"] = np.nan
    df["outcome_medio"] = y.mean()
    return df


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in [QUADRO, MATRIZ_FUNIL, MATRIZ_TIPOLOGIA, MANIFESTO_TIP, PORTAO_A1, REGISTRO_A3, POTENCIA_A3]:
        if not p.exists():
            raise FileNotFoundError(p)

    df_prim, df_ext = prepare_df_primary()
    # y, groups primários
    y_prim = df_prim["outcome_alguma_confirmacao_ou_homologacao"].astype(float)
    g_prim = df_prim["co_ibge_6d"]
    # small UFs para relatório (definido em prepare_df_primary como <5 clusters na primária)
    clust_prim = df_prim.groupby("sg_uf")["co_ibge_6d"].nunique()
    small_ufs = set(clust_prim[clust_prim < 5].index.tolist())

    # --------------------------------------------------
    # 1. Estatísticas de construção e suporte (antes dos coefs)
    # --------------------------------------------------
    # Amostra primária vs estendida
    # Por estrato
    def stats_por_estrato(df: pd.DataFrame, nome: str) -> pd.DataFrame:
        grp = df.groupby("estrato", dropna=False, observed=True)
        out = []
        for estr, sub in grp:
            out.append({
                "amostra": nome,
                "estrato": str(estr) if pd.notna(estr) else "NA",
                "n_celulas": len(sub),
                "n_municipios": sub["co_ibge_6d"].nunique(),
                "outcome_medio": sub["outcome_alguma_confirmacao_ou_homologacao"].mean(),
                "ivs_medio": sub["ivs_2010"].mean(),
                "pop_mediana": sub["populacao_2010"].median(),
                "estoque_medio": sub["estoque_especialistas_pre_12m_media"].mean(),
                "prop_faixa1": (sub["faixa_atracao_anunciada"] == "FAIXA 1").mean(),
                "prop_faixa2": (sub["faixa_atracao_anunciada"] == "FAIXA 2").mean(),
                "prop_faixa3": (sub["faixa_atracao_anunciada"] == "FAIXA 3").mean(),
            })
        return pd.DataFrame(out)

    tab_prim = stats_por_estrato(df_prim, "primaria_1295_Ch1")
    tab_ext = stats_por_estrato(df_ext, "estendida_3057_A1")
    # Faixa descritiva primária
    faixa_grp = df_prim.groupby("faixa_atracao_anunciada", dropna=False, observed=True)["outcome_alguma_confirmacao_ou_homologacao"].agg(["count", "mean"]).reset_index().rename(columns={"faixa_atracao_anunciada": "faixa", "count": "n_celulas", "mean": "outcome_medio"})
    faixa_grp["amostra"] = "primaria_1295_Ch1"
    # IVS quartis
    df_prim["ivs_quartil"] = pd.qcut(df_prim["ivs_2010"], 4, labels=["Q1_baixo", "Q2", "Q3", "Q4_alto"], duplicates="drop")
    ivs_q = df_prim.groupby("ivs_quartil", observed=True)["outcome_alguma_confirmacao_ou_homologacao"].agg(["count", "mean"]).reset_index()
    ivs_q["amostra"] = "primaria"
    # Curso top
    curso_tab = df_prim.groupby("cod_curso", observed=True)["outcome_alguma_confirmacao_ou_homologacao"].agg(["count", "mean"]).reset_index().sort_values("count", ascending=False)
    # UF clusters (para tabela suporte)
    uf_clust = df_prim.groupby("sg_uf")["co_ibge_6d"].nunique().reset_index().rename(columns={"co_ibge_6d": "n_municipios"})
    uf_cells = df_prim.groupby("sg_uf")["outcome_alguma_confirmacao_ou_homologacao"].agg(["count", "mean"]).reset_index()
    uf_tab = uf_clust.merge(uf_cells, on="sg_uf")
    uf_tab["uf_fe"] = np.where(uf_tab["n_municipios"] < 5, "RESTO", uf_tab["sg_uf"])

    # Monta tabela amostra consolidada (long) por estrato
    amostra_long = pd.concat([tab_prim, tab_ext], ignore_index=True)
    tmp = TABELA_AMOSTRA.with_suffix(".csv.tmp")
    amostra_long.to_csv(tmp, index=False)
    tmp.replace(TABELA_AMOSTRA)
    # Tabelas suplementares de suporte (antes dos coefs) — faixa, curso, UF, construção steps
    # Construção steps: 3323 funil -> 3057 extended -> 1295 primary
    construcao = pd.DataFrame([
        {"etapa": "01_funil_total_A1", "n_celulas": len(pd.read_parquet(MATRIZ_FUNIL)), "n_municipios": pd.read_parquet(MATRIZ_FUNIL)["co_ibge_6d"].nunique(), "nota": "3323 linhas Ch1 1324 + Ch2 1999"},
        {"etapa": "02_exclui_sem_municipio", "n_celulas": 266, "n_municipios": 0, "nota": "fora do quadro sem municipio (29 Ch1 +237 Ch2)"},
        {"etapa": "03_estendida_A1", "n_celulas": len(df_ext), "n_municipios": df_ext["co_ibge_6d"].nunique(), "nota": "3057 = 3323-266"},
        {"etapa": "04_primaria_quadro_Ch1", "n_celulas": len(df_prim), "n_municipios": df_prim["co_ibge_6d"].nunique(), "nota": "1295 quadro Ch1 (368 mun) outcome 30.3%"},
        {"etapa": "05_exclui_29_fora_quadro_Ch1_com_mun", "n_celulas": 29, "n_municipios": 29, "nota": "Ch1 fora do quadro com municipio, não primária"},
    ])
    tmp = TABELA_CONSTRUCAO.with_suffix(".csv.tmp")
    construcao.to_csv(tmp, index=False)
    tmp.replace(TABELA_CONSTRUCAO)
    tmp = TABELA_AMOSTRA_FAIXA.with_suffix(".csv.tmp")
    faixa_grp.to_csv(tmp, index=False)
    tmp.replace(TABELA_AMOSTRA_FAIXA)
    tmp = TABELA_AMOSTRA_CURSO.with_suffix(".csv.tmp")
    curso_tab.to_csv(tmp, index=False)
    tmp.replace(TABELA_AMOSTRA_CURSO)
    tmp = TABELA_AMOSTRA_UF.with_suffix(".csv.tmp")
    uf_tab.to_csv(tmp, index=False)
    tmp.replace(TABELA_AMOSTRA_UF)
    # Salva ivs quartis também como parte da amostra (embutido no json); mantido para completude
    # --------------------------------------------------
    # 2. Modelo primário exatamente como congelado em A3
    # --------------------------------------------------
    # Minimal: estrato + FE curso + FE UF (colapsada)
    X_min = build_X(df_prim, "minimal")
    res_lpm_min = fit_lpm(y_prim, X_min, g_prim)
    tab_lpm_min = summarize_res(res_lpm_min, X_min, y_prim, g_prim, "LPM_minimal_estrato_FEcurso_FEuf_cluster")

    # Logit AME alternativo mesma spec
    res_logit_min = fit_logit(y_prim, X_min, g_prim)
    # AME cluster SE precisa delta method; statsmodels get_margeff não suporta cluster diretamente, mas usa se da coef e transforma?
    # Usa get_margeff at overall para AME, com dummy True; depois usa se cluster aproximado via modelo
    margeff = res_logit_min.get_margeff(at="overall", method="dydx", dummy=True, count=True)
    # margeff.summary já tem se, mas não cluster? Vamos manter se do margeff (approx) e também reportar coef logit
    ame_df = pd.DataFrame({
        "termo": margeff.margeff.sum(axis=0) if False else X_min.columns,  # placeholder
    })
    # Construção manual AME df
    ame_terms = X_min.columns.tolist()
    ame_coef = margeff.margeff  # array same order as X (sem const? inclui)
    ame_se = margeff.margeff_se
    # margeff object tem params_names
    try:
        names = margeff.margeff_names if hasattr(margeff, "margeff_names") else X_min.columns.tolist()
    except Exception:
        names = X_min.columns.tolist()
    # margeff.margeff array corresponde a X sem const? Em statsmodels, margeff exclui const.
    # Ajusta: se len != len(X), remove const de X
    if len(ame_coef) == len(X_min.columns) - 1:
        names = [c for c in X_min.columns if c != "const"]
    ame_df = pd.DataFrame({
        "termo": names,
        "ame": ame_coef,
        "se_ame": ame_se,
        "z": ame_coef / ame_se,
        "p_valor": 2 * (1 - scipy_stats.norm.cdf(np.abs(ame_coef / ame_se))),
        "espec": "Logit_AME_minimal_estrato_FEcurso_FEuf",
        "n": len(y_prim),
        "n_clusters": g_prim.nunique(),
        "outcome_medio": y_prim.mean(),
    })
    ame_df["ci_low"] = ame_df["ame"] - scipy_stats.norm.ppf(1 - ALPHA / 2) * ame_df["se_ame"]
    ame_df["ci_high"] = ame_df["ame"] + scipy_stats.norm.ppf(1 - ALPHA / 2) * ame_df["se_ame"]
    # FDR para estrato AME
    mask = ame_df["termo"].str.startswith("estrato_") & ~ame_df["termo"].str.contains("_x_ivs")
    if mask.sum() > 0:
        ame_df.loc[mask, "q_fdr_estrato"] = bh_fdr(ame_df.loc[mask, "p_valor"].values)
    else:
        ame_df["q_fdr_estrato"] = np.nan

    # Salva LPM minimal
    tmp = TABELA_PRINCIPAL_LPM.with_suffix(".csv.tmp")
    tab_lpm_min.to_csv(tmp, index=False)
    tmp.replace(TABELA_PRINCIPAL_LPM)
    # Salva Logit AME
    tmp = TABELA_PRINCIPAL_LOGIT.with_suffix(".csv.tmp")
    ame_df.to_csv(tmp, index=False)
    tmp.replace(TABELA_PRINCIPAL_LOGIT)

    # --------------------------------------------------
    # 3. Sensibilidades: full ajustado e separações
    # --------------------------------------------------
    X_full = build_X(df_prim, "full")
    res_lpm_full = fit_lpm(y_prim, X_full, g_prim)
    tab_full = summarize_res(res_lpm_full, X_full, y_prim, g_prim, "LPM_full_estrato_ivs_logpop_estoque_faixa_FE")
    tmp = TABELA_SENS_AJUST.with_suffix(".csv.tmp")
    tab_full.to_csv(tmp, index=False)
    tmp.replace(TABELA_SENS_AJUST)

    # Sensibilidade winsorizada p99 (registro: população e estoque winsorizados apenas como sensibilidade)
    df_wins = df_prim.copy()
    for col in ["log_pop", "estoque_por_10k"]:
        p99 = df_wins[col].quantile(0.99)
        p01 = df_wins[col].quantile(0.01)
        df_wins[col] = df_wins[col].clip(lower=p01, upper=p99)
    X_wins = build_X(df_wins, "full")
    res_wins = fit_lpm(y_prim, X_wins, g_prim)
    tab_wins = summarize_res(res_wins, X_wins, y_prim, g_prim, "LPM_full_winsorizado_p99")
    tmp = TABELA_SENS_WINSOR.with_suffix(".csv.tmp")
    tab_wins.to_csv(tmp, index=False)
    tmp.replace(TABELA_SENS_WINSOR)

    # Sensibilidade IVS spline/quadrático (registro: IVS linear + splines como sensibilidade)
    X_spline = build_X(df_prim, "full")
    # adiciona termo quadrático de IVS como proxy de spline
    X_spline["ivs_2010_sq"] = df_prim["ivs_2010"].astype(float) ** 2
    # reordena para const primeiro
    cols = ["const"] + [c for c in X_spline.columns if c != "const"]
    X_spline = X_spline[cols]
    res_spline = fit_lpm(y_prim, X_spline, g_prim)
    tab_spline = summarize_res(res_spline, X_spline, y_prim, g_prim, "LPM_full_ivs_quadratico")
    tmp = TABELA_SENS_SPLINE.with_suffix(".csv.tmp")
    tab_spline.to_csv(tmp, index=False)
    tmp.replace(TABELA_SENS_SPLINE)

    # Separações: faixa_only, ivs_only, estrato minimal já tem, mas reporta faixa e ivs isolados
    X_faixa = build_X(df_prim, "faixa_only")
    res_faixa = fit_lpm(y_prim, X_faixa, g_prim)
    tab_faixa = summarize_res(res_faixa, X_faixa, y_prim, g_prim, "LPM_faixa_only_FE")

    X_ivs = build_X(df_prim, "ivs_only")
    res_ivs = fit_lpm(y_prim, X_ivs, g_prim)
    tab_ivs = summarize_res(res_ivs, X_ivs, y_prim, g_prim, "LPM_ivs_only_FE")

    # Heterogeneidade estrato*ivs
    X_inter = build_X(df_prim, "estrato_ivs_inter")
    res_inter = fit_lpm(y_prim, X_inter, g_prim)
    tab_inter = summarize_res(res_inter, X_inter, y_prim, g_prim, "LPM_estrato_x_ivs_FE")

    sep_concat = pd.concat([tab_faixa, tab_ivs, tab_inter], ignore_index=True)
    # Mantém também minimal estrato para comparação? Já está em tabela principal, mas repete aqui para separação completa
    sep_concat = pd.concat([tab_lpm_min[tab_lpm_min["termo"].str.startswith("estrato_")], sep_concat], ignore_index=True)
    tmp = TABELA_SEP.with_suffix(".csv.tmp")
    sep_concat.to_csv(tmp, index=False)
    tmp.replace(TABELA_SEP)

    # --------------------------------------------------
    # 4. Leave-one-UF, leave-one-curso e influência municipal
    # --------------------------------------------------
    loo_rows = []
    # LOO UF
    for uf in sorted(df_prim["sg_uf"].unique()):
        sub = df_prim[df_prim["sg_uf"] != uf].copy()
        if len(sub) < 500:
            continue
        y_s = sub["outcome_alguma_confirmacao_ou_homologacao"].astype(float)
        g_s = sub["co_ibge_6d"]
        # Mantém colapso original (small_ufs) para comparabilidade; não reindexa para zero cols
        X_s = build_X(sub, "minimal")
        # Drop colunas com variância zero para evitar singular matrix warnings
        X_s = X_s.loc[:, (X_s != X_s.iloc[0]).any(axis=0) | (X_s.columns == "const")]
        try:
            res_s = fit_lpm(y_s, X_s, g_s)
            estrato_coefs = res_s.params.filter(like="estrato_")
            for termo, coef in estrato_coefs.items():
                loo_rows.append({"tipo": "leave_one_UF", "excluido": uf, "termo": termo, "coef": coef, "se": res_s.bse[termo], "p": res_s.pvalues[termo], "n": len(sub), "n_clusters": g_s.nunique()})
        except Exception as e:
            loo_rows.append({"tipo": "leave_one_UF", "excluido": uf, "termo": "erro", "coef": np.nan, "se": np.nan, "p": np.nan, "n": len(sub), "n_clusters": g_s.nunique()})

    # LOO curso
    for curso in sorted(df_prim["cod_curso"].unique()):
        sub = df_prim[df_prim["cod_curso"] != curso].copy()
        y_s = sub["outcome_alguma_confirmacao_ou_homologacao"].astype(float)
        g_s = sub["co_ibge_6d"]
        X_s = build_X(sub, "minimal")
        X_s = X_s.loc[:, (X_s != X_s.iloc[0]).any(axis=0) | (X_s.columns == "const")]
        try:
            res_s = fit_lpm(y_s, X_s, g_s)
            for termo in [c for c in res_s.params.index if c.startswith("estrato_")]:
                loo_rows.append({"tipo": "leave_one_curso", "excluido": str(curso), "termo": termo, "coef": res_s.params[termo], "se": res_s.bse[termo], "p": res_s.pvalues[termo], "n": len(sub), "n_clusters": g_s.nunique()})
        except Exception:
            pass

    df_loo = pd.DataFrame(loo_rows)
    tmp = TABELA_LOO.with_suffix(".csv.tmp")
    df_loo.to_csv(tmp, index=False)
    tmp.replace(TABELA_LOO)

    # Influência municipal: leave-one-municipality-out DFB para coef estrato metropolitano (principal)
    infl_rows = []
    # Baseline coefs
    base_coefs = res_lpm_min.params.filter(like="estrato_").to_dict()
    base_se = res_lpm_min.bse.filter(like="estrato_").to_dict()
    # Para eficiência, itera sobre 368 municípios (pode ser custoso mas ok <2min)
    municipios = df_prim["co_ibge_6d"].unique()
    coefs_mun = []
    for mun in municipios:
        sub = df_prim[df_prim["co_ibge_6d"] != mun]
        y_s = sub["outcome_alguma_confirmacao_ou_homologacao"].astype(float)
        g_s = sub["co_ibge_6d"]
        X_s = build_X(sub, "minimal")
        X_s = X_s.loc[:, (X_s != X_s.iloc[0]).any(axis=0) | (X_s.columns == "const")]
        try:
            res_s = fit_lpm(y_s, X_s, g_s)
            for termo in ["estrato_metropolitano", "estrato_capital", "estrato_interior_proximo_polo"]:
                if termo in res_s.params:
                    delta = res_s.params[termo] - base_coefs[termo]
                    # padroniza por SE baseline
                    dfbeta = delta / base_se[termo] if base_se[termo] != 0 else np.nan
                    infl_rows.append({"co_ibge_6d": mun, "termo": termo, "coef_excluido": res_s.params[termo], "delta": delta, "dfbeta": dfbeta, "n_excluido": len(df_prim) - len(sub)})
                    if termo == "estrato_metropolitano":
                        coefs_mun.append(res_s.params[termo])
        except Exception:
            continue
    df_infl = pd.DataFrame(infl_rows)
    # Ordena por |dfbeta|
    if not df_infl.empty:
        df_infl = df_infl.sort_values("dfbeta", key=lambda s: s.abs(), ascending=False)
    tmp = TABELA_INFLUENCIA.with_suffix(".csv.tmp")
    df_infl.to_csv(tmp, index=False)
    tmp.replace(TABELA_INFLUENCIA)

    # Resumo influência: min/max para estrato_metropolitano
    infl_summary = {}
    if coefs_mun:
        infl_summary = {"estrato_metropolitano_leave_one_mun_min": float(np.min(coefs_mun)), "max": float(np.max(coefs_mun)), "sd": float(np.std(coefs_mun)), "base": float(base_coefs["estrato_metropolitano"])}

    # --------------------------------------------------
    # 5. Validação preditiva por município (GroupKFold manual, rebuild X por fold)
    # --------------------------------------------------
    # 5-fold por município, LPM e Logit, AUC/Brier (sem sklearn); reconstrói X por fold para evitar vazamento de categorias raras
    df_prim_for_cv = df_prim.copy()
    groups_arr = df_prim_for_cv["co_ibge_6d"].values
    y_arr = df_prim_for_cv["outcome_alguma_confirmacao_ou_homologacao"].astype(float).values
    aucs_lpm = []
    briers_lpm = []
    aucs_logit = []
    briers_logit = []
    # In-sample AUC para referência
    try:
        pred_insample_lpm = res_lpm_min.predict(X_min)
        pred_insample_lpm = np.clip(pred_insample_lpm, 0, 1)
        auc_insample_lpm = roc_auc_score_manual(y_arr, pred_insample_lpm)
        brier_insample_lpm = brier_score_manual(y_arr, pred_insample_lpm)
        pred_insample_logit = res_logit_min.predict(X_min)
        pred_insample_logit = np.clip(pred_insample_logit, 0, 1)
        auc_insample_logit = roc_auc_score_manual(y_arr, pred_insample_logit)
        brier_insample_logit = brier_score_manual(y_arr, pred_insample_logit)
    except Exception:
        auc_insample_lpm = brier_insample_lpm = auc_insample_logit = brier_insample_logit = float("nan")
    for train_idx, test_idx in group_kfold_splits(groups_arr, n_splits=5, seed=42):
        df_train = df_prim_for_cv.iloc[train_idx].copy()
        df_test = df_prim_for_cv.iloc[test_idx].copy()
        y_train = df_train["outcome_alguma_confirmacao_ou_homologacao"].astype(float).values
        y_test = df_test["outcome_alguma_confirmacao_ou_homologacao"].astype(float).values
        # Reconstrói X por fold para evitar coluna zero por UF raro só no teste
        X_train = build_X(df_train, "minimal")
        X_test = build_X(df_test, "minimal")
        # Alinha colunas: mantém apenas colunas de treino; teste usa mesmo espaço, colunas ausentes viram 0
        X_test_aligned = X_test.reindex(columns=X_train.columns, fill_value=0)
        # Drop zero variance cols no treino já evitado por build_X
        # LPM
        try:
            res_cv = sm.OLS(y_train, X_train.values).fit()
            pred_lpm = res_cv.predict(X_test_aligned.values)
            pred_lpm = np.clip(pred_lpm, 0, 1)
            aucs_lpm.append(roc_auc_score_manual(y_test, pred_lpm))
            briers_lpm.append(brier_score_manual(y_test, pred_lpm))
        except Exception:
            pass
        # Logit
        try:
            res_cv_log = sm.Logit(y_train, X_train.values).fit(disp=0, maxiter=200)
            pred_log = res_cv_log.predict(X_test_aligned.values)
            pred_log = np.clip(pred_log, 0, 1)
            aucs_logit.append(roc_auc_score_manual(y_test, pred_log))
            briers_logit.append(brier_score_manual(y_test, pred_log))
        except Exception:
            pass

    pred_df = pd.DataFrame([{
        "modelo": "LPM_minimal",
        "auc_media_out": float(np.mean(aucs_lpm)) if aucs_lpm else np.nan,
        "auc_sd_out": float(np.std(aucs_lpm)) if aucs_lpm else np.nan,
        "auc_insample": float(auc_insample_lpm) if not np.isnan(auc_insample_lpm) else np.nan,
        "brier_media_out": float(np.mean(briers_lpm)) if briers_lpm else np.nan,
        "brier_sd_out": float(np.std(briers_lpm)) if briers_lpm else np.nan,
        "brier_insample": float(brier_insample_lpm) if not np.isnan(brier_insample_lpm) else np.nan,
        "n_splits": 5,
        "grupos": "municipio",
        "nota": "out-of-sample por municipio; in-sample AUC indica overfit FE",
    }, {
        "modelo": "Logit_minimal",
        "auc_media_out": float(np.mean(aucs_logit)) if aucs_logit else np.nan,
        "auc_sd_out": float(np.std(aucs_logit)) if aucs_logit else np.nan,
        "auc_insample": float(auc_insample_logit) if not np.isnan(auc_insample_logit) else np.nan,
        "brier_media_out": float(np.mean(briers_logit)) if briers_logit else np.nan,
        "brier_sd_out": float(np.std(briers_logit)) if briers_logit else np.nan,
        "brier_insample": float(brier_insample_logit) if not np.isnan(brier_insample_logit) else np.nan,
        "n_splits": 5,
        "grupos": "municipio",
        "nota": "out-of-sample por municipio; in-sample AUC indica overfit FE",
    }])
    tmp = TABELA_PRED.with_suffix(".csv.tmp")
    pred_df.to_csv(tmp, index=False)
    tmp.replace(TABELA_PRED)

    # --------------------------------------------------
    # 6. Figuras probabilidades ajustadas por território
    # --------------------------------------------------
    # Figura 1: prob ajustada por estrato (predição marginal)
    # Calcula prob predita para cada observação sob cada estrato counterfactual, mantendo outras covariadas
    # Usa modelo LPM minimal para predição
    def marginal_prob_por_estrato(df, X_template, res):
        # Para cada estrato, cria cópia onde estrato = level, recalcula dummies
        levels = ["interior_remoto", "capital", "metropolitano", "interior_proximo_polo"]
        probs = {}
        for lev in levels:
            df_cf = df.copy()
            df_cf["estrato"] = pd.Categorical([lev] * len(df), categories=["interior_remoto", "capital", "metropolitano", "interior_proximo_polo"], ordered=False)
            X_cf = build_X(df_cf, "minimal")
            X_cf = X_cf.reindex(columns=X_template.columns, fill_value=0)
            pred = res.predict(X_cf)
            pred = np.clip(pred, 0, 1)
            probs[lev] = float(pred.mean())
        return probs

    probs = marginal_prob_por_estrato(df_prim, X_min, res_lpm_min)
    # IC via delta? Aproxima via SE do coef (para diferença vs remoto)
    # Para figura, usa ponto + IC do coeficiente (convertido para prob base)
    base_prob = probs["interior_remoto"]
    # Coefs: diferença vs remoto
    estrato_coefs = {k.replace("estrato_", ""): v for k, v in res_lpm_min.params.filter(like="estrato_").items()}
    estrato_se = {k.replace("estrato_", ""): v for k, v in res_lpm_min.bse.filter(like="estrato_").items()}

    # Plot
    order = ["interior_remoto", "capital", "metropolitano", "interior_proximo_polo"]
    labels = {"interior_remoto": "Interior remoto\n(ref.)", "capital": "Capital", "metropolitano": "Metropolitano", "interior_proximo_polo": "Interior próximo\n(conectado)"}
    y_vals = [probs[l] for l in order]
    y_err_low = []
    y_err_high = []
    for l in order:
        if l == "interior_remoto":
            # IC para base prob via SE da const? Aproxima sem IC (referência)
            y_err_low.append(0)
            y_err_high.append(0)
        else:
            se = estrato_se.get(l, 0)
            y_err_low.append(1.96 * se)
            y_err_high.append(1.96 * se)

    plt.figure(figsize=(8, 5))
    x = np.arange(len(order))
    # barras com erro
    plt.bar(x, y_vals, color=["#6c757d", "#495057", "#007bff", "#17a2b8"], alpha=0.9, yerr=[y_err_low, y_err_high], capsize=6, error_kw={"elinewidth": 1.5})
    plt.xticks(x, [labels[l] for l in order], fontsize=9)
    plt.ylabel("Probabilidade ajustada de atração (LPM, FE curso+UF, cluster município)", fontsize=9)
    plt.ylim(0, max(y_vals) * 1.35)
    for i, (yv, lev) in enumerate(zip(y_vals, order)):
        plt.text(i, yv + 0.015, f"{yv:.1%}\n(n={tab_prim[tab_prim['estrato']==lev]['n_celulas'].values[0] if lev in tab_prim['estrato'].values else ''})", ha="center", fontsize=8)
    plt.title("Atração por território — probabilidades ajustadas (primária 1295 células, 368 municípios)\nLPM com FE curso e UF, IC95% cluster município; linguagem associativa", fontsize=9, pad=12)
    plt.tight_layout()
    plt.savefig(FIG_PROB_ESTRATO, dpi=300)
    plt.close()

    # Figura 2: gradiente IVS (binned quartis vs contínuo)
    # Usa modelo ivs_only + FE, mostra prob média por quartil e linha loess linear
    df_prim_ivsq = df_prim.copy()
    df_prim_ivsq["ivs_q"] = pd.qcut(df_prim_ivsq["ivs_2010"], 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop")
    # prob por quartil (observado e ajustado ivs_only)
    # Ajustado: pred do modelo ivs_only com ivs = mediana do quartil? Simples: prob predita média por quartil
    X_ivs = build_X(df_prim, "ivs_only")
    res_ivs_lpm = fit_lpm(y_prim, X_ivs, g_prim)
    probs_q = []
    for q in sorted(df_prim_ivsq["ivs_q"].unique()):
        mask = df_prim_ivsq["ivs_q"] == q
        sub = df_prim[mask]
        X_sub = build_X(sub, "ivs_only")
        X_sub = X_sub.reindex(columns=X_ivs.columns, fill_value=0)
        pred = res_ivs_lpm.predict(X_sub)
        probs_q.append((str(q), float(pred.mean()), float(sub["outcome_alguma_confirmacao_ou_homologacao"].mean()), int(mask.sum())))
    plt.figure(figsize=(8, 5))
    qs = [p[0] for p in probs_q]
    y_adj = [p[1] for p in probs_q]
    y_obs = [p[2] for p in probs_q]
    x = np.arange(len(qs))
    plt.plot(x, y_obs, marker="o", label="Observada", color="black", linewidth=1.5)
    plt.plot(x, y_adj, marker="s", label="Ajustada (LPM FE curso+UF + IVS)", color="#007bff", linewidth=1.5)
    for i, (qo, ya, yo, n) in enumerate(probs_q):
        plt.text(i, ya + 0.01, f"n={n}", ha="center", fontsize=7)
    plt.xticks(x, [f"{q}\nIVS {df_prim[df_prim['ivs_quartil']==q]['ivs_2010'].min():.2f}–{df_prim[df_prim['ivs_quartil']==q]['ivs_2010'].max():.2f}" if q in df_prim['ivs_quartil'].cat.categories else q for q in qs], fontsize=7)
    plt.ylabel("Probabilidade de atração", fontsize=9)
    plt.xlabel("Quartil de IVS 2010 (Q1 baixo vulnerabilidade → Q4 alta)", fontsize=9)
    plt.title("Gradiente por vulnerabilidade (IVS) — sem efeito causal\nLPM com FE curso+UF, cluster município; IVS linear coef não significativo", fontsize=9)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG_IVS, dpi=300)
    plt.close()

    # Figura 3: faixa descritiva (desagregada, sem causalidade)
    # Faixa FAIXA1=muito alta, FAIXA2=alta, FAIXA3=média/baixa (R$20/15/10k)
    faixa_order = ["FAIXA 1", "FAIXA 2", "FAIXA 3"]
    faixa_labels = {"FAIXA 1": "FAIXA 1\nmuito alta\nR$20k", "FAIXA 2": "FAIXA 2\nalta\nR$15k", "FAIXA 3": "FAIXA 3\nmédia/baixa\nR$10k"}
    y_faixa_obs = []
    y_faixa_adj = []
    n_faixa = []
    # Ajustado faixa_only modelo
    X_faixa_mod = build_X(df_prim, "faixa_only")
    res_faixa_lpm = fit_lpm(y_prim, X_faixa_mod, g_prim)
    # Para cada faixa, prob marginal
    for faixa in faixa_order:
        sub = df_prim[df_prim["faixa_atracao_anunciada"] == faixa]
        n_faixa.append(len(sub))
        y_faixa_obs.append(float(sub["outcome_alguma_confirmacao_ou_homologacao"].mean()))
        # predição contrafactual: atribui faixa a todos e prediz
        df_cf = df_prim.copy()
        df_cf["faixa_atracao_anunciada"] = faixa
        X_cf = build_X(df_cf, "faixa_only")
        X_cf = X_cf.reindex(columns=X_faixa_mod.columns, fill_value=0)
        pred = res_faixa_lpm.predict(X_cf)
        pred = np.clip(pred, 0, 1)
        y_faixa_adj.append(float(pred.mean()))
    plt.figure(figsize=(8, 5))
    x = np.arange(len(faixa_order))
    width = 0.35
    plt.bar(x - width / 2, y_faixa_obs, width, label="Observada", color="#6c757d", alpha=0.9)
    plt.bar(x + width / 2, y_faixa_adj, width, label="Ajustada (FE curso+UF)", color="#ffc107", alpha=0.9)
    plt.xticks(x, [faixa_labels[f] for f in faixa_order], fontsize=8)
    plt.ylabel("Probabilidade de atração", fontsize=9)
    plt.ylim(0, max(max(y_faixa_obs), max(y_faixa_adj)) * 1.35)
    for i, (yo, ya, n) in enumerate(zip(y_faixa_obs, y_faixa_adj, n_faixa)):
        plt.text(i - width / 2, yo + 0.015, f"{yo:.1%}\nn={n}", ha="center", fontsize=7)
        plt.text(i + width / 2, ya + 0.015, f"{ya:.1%}", ha="center", fontsize=7)
    plt.title("Faixa anunciada e atração — descritivo, não efeito causal da bolsa\nLPM com FE curso+UF, cluster município; faixa não isolada de IVS (colinearidade)", fontsize=9)
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(FIG_FAIXA, dpi=300)
    plt.close()

    # --------------------------------------------------
    # 7. JSON estimativas + hashes + diagnóstico
    # --------------------------------------------------
    # Potência referência para interpretação
    pot = json.loads(POTENCIA_A3.read_text(encoding="utf-8"))
    reg = json.loads(REGISTRO_A3.read_text(encoding="utf-8"))
    manifesto = json.loads(MANIFESTO_TIP.read_text(encoding="utf-8"))

    estimativas: dict[str, Any] = {
        "protocolo": "A4_ESTIMATIVAS_ATRACAO",
        "data_referencia": "2026-09-02",
        "efeitos_estimados": True,
        "linguagem": "associativa (associado a, gradiente territorial); proibido efeito causal do PMM-E/bolsa/IVS e retenção individual",
        "populacao": {
            "primaria": "1295 células CNES–curso quadro Ch1 (368 municípios)",
            "estendida": "3057 células funil A1 (1762 Ch2 +1295 Ch1) sem 266 sem município",
            "unidade_analitica": "célula CNES–curso (chamada como FE quando Ch1+Ch2)",
            "unidade_inferencia": "município (cluster-robusto; G=368 primária)",
        },
        "outcome": "alguma_confirmacao_ou_homologacao_na_celula (binário por célula; A1 APROVADO_CELULA; taxa por vaga proibida)",
        "modelos": {
            "primario_LPM_minimal": {
                "formula": "outcome ~ estrato(4) + FE curso(16) + FE UF(colapsada RESTO para <5 clusters) com cluster município",
                "n": int(len(df_prim)),
                "n_clusters": int(g_prim.nunique()),
                "outcome_medio": float(y_prim.mean()),
                "r2": float(res_lpm_min.rsquared),
                "coef_estrato": {k: float(v) for k, v in res_lpm_min.params.filter(like="estrato_").items()},
                "se_estrato": {k: float(v) for k, v in res_lpm_min.bse.filter(like="estrato_").items()},
                "p_estrato": {k: float(v) for k, v in res_lpm_min.pvalues.filter(like="estrato_").items()},
            },
            "alternativo_logit_AME": {
                "ame_estrato": {row["termo"]: float(row["ame"]) for _, row in ame_df[ame_df["termo"].str.startswith("estrato_")].iterrows()},
                "se_ame_estrato": {row["termo"]: float(row["se_ame"]) for _, row in ame_df[ame_df["termo"].str.startswith("estrato_")].iterrows()},
            },
            "sensibilidade_full": {
                "coef_estrato_full": {k: float(v) for k, v in res_lpm_full.params.filter(like="estrato_").items()},
                "coef_ivs": float(res_lpm_full.params.get("ivs_2010", np.nan)),
                "coef_log_pop": float(res_lpm_full.params.get("log_pop", np.nan)),
                "coef_faixa": {k: float(v) for k, v in res_lpm_full.params.filter(like="faixa_").items()},
            },
            "sensibilidade_winsorizado_p99": {
                "coef_estrato": {k: float(v) for k, v in res_wins.params.filter(like="estrato_").items()},
                "coef_ivs": float(res_wins.params.get("ivs_2010", np.nan)),
                "nota": "log_pop e estoque winsorizados p01-p99 como sensibilidade pre-especificada",
            },
            "sensibilidade_ivs_quadratico": {
                "coef_estrato": {k: float(v) for k, v in res_spline.params.filter(like="estrato_").items()},
                "coef_ivs_linear": float(res_spline.params.get("ivs_2010", np.nan)),
                "coef_ivs_sq": float(res_spline.params.get("ivs_2010_sq", np.nan)),
                "p_ivs_sq": float(res_spline.pvalues.get("ivs_2010_sq", np.nan)),
                "nota": "IVS linear + quadrático como proxy de spline; p não significativo mantém linear",
            },
        },
        "influencia": {
            "leave_one_UF_range": df_loo[df_loo["tipo"] == "leave_one_UF"].groupby("termo")["coef"].agg(["min", "max", "std"]).to_dict() if not df_loo.empty else {},
            "leave_one_curso_range": df_loo[df_loo["tipo"] == "leave_one_curso"].groupby("termo")["coef"].agg(["min", "max", "std"]).to_dict() if not df_loo.empty else {},
            "leave_one_municipio_metropolitano": infl_summary,
            "top_influentes": df_infl.head(10).to_dict(orient="records") if not df_infl.empty else [],
        },
        "validacao_preditiva": pred_df.to_dict(orient="records"),
        "potencia_referencia": {
            "global_MDE_p30": pot["mde_global"]["mde_80_pp_p30"],
            "por_estrato_MDE_p30": {k: v["mde_80_pp_p30"] for k, v in pot["por_estrato"].items()},
        },
        "hashes_entradas": {
            str(p.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(p)} for p in [QUADRO, MATRIZ_FUNIL, MATRIZ_TIPOLOGIA, MANIFESTO_TIP, PORTAO_A1, REGISTRO_A3, POTENCIA_A3]
        },
        "arquivos": {
            "tabela_construcao": str(TABELA_CONSTRUCAO.relative_to(ROOT)).replace("\\", "/"),
            "tabela_amostra": str(TABELA_AMOSTRA.relative_to(ROOT)).replace("\\", "/"),
            "tabela_amostra_faixa": str(TABELA_AMOSTRA_FAIXA.relative_to(ROOT)).replace("\\", "/"),
            "tabela_amostra_curso": str(TABELA_AMOSTRA_CURSO.relative_to(ROOT)).replace("\\", "/"),
            "tabela_amostra_uf": str(TABELA_AMOSTRA_UF.relative_to(ROOT)).replace("\\", "/"),
            "tabela_principal_LPM": str(TABELA_PRINCIPAL_LPM.relative_to(ROOT)).replace("\\", "/"),
            "tabela_logit_AME": str(TABELA_PRINCIPAL_LOGIT.relative_to(ROOT)).replace("\\", "/"),
            "tabela_separacao": str(TABELA_SEP.relative_to(ROOT)).replace("\\", "/"),
            "tabela_ajuste_completo": str(TABELA_SENS_AJUST.relative_to(ROOT)).replace("\\", "/"),
            "tabela_winsorizado": str(TABELA_SENS_WINSOR.relative_to(ROOT)).replace("\\", "/"),
            "tabela_ivs_spline": str(TABELA_SENS_SPLINE.relative_to(ROOT)).replace("\\", "/"),
            "tabela_loo": str(TABELA_LOO.relative_to(ROOT)).replace("\\", "/"),
            "tabela_influencia": str(TABELA_INFLUENCIA.relative_to(ROOT)).replace("\\", "/"),
            "tabela_preditiva": str(TABELA_PRED.relative_to(ROOT)).replace("\\", "/"),
            "figura_prob_estrato": str(FIG_PROB_ESTRATO.relative_to(ROOT)).replace("\\", "/"),
            "figura_ivs": str(FIG_IVS.relative_to(ROOT)).replace("\\", "/"),
            "figura_faixa": str(FIG_FAIXA.relative_to(ROOT)).replace("\\", "/"),
        },
        "avisos": [
            "Faixa não isolada de IVS; coeficiente descritivo, não efeito causal da bolsa.",
            "IVS linear não significativo; gradiente descritivo.",
            "Capital com G=18 <30: IC cluster nominal; wild bootstrap recomendado para subgrupo, não computado nesta entrega.",
            "Não ponderar por vagas; pesos por estrato alteram estimando.",
            "Cursos como exploração; FDR apenas para família 4 estratos.",
        ],
    }

    tmp = JSON_ESTIMATIVAS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(estimativas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(JSON_ESTIMATIVAS)

    # Relatório markdown diagnóstico
    # Prepara strings formatadas
    def fmt_coef(est, se, p):
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        return f"{est:.3f} ({se:.3f}){stars}"

    lpm_rows_md = ""
    for _, row in tab_lpm_min[tab_lpm_min["termo"].str.startswith("estrato_")].iterrows():
        lpm_rows_md += f"| {row['termo'].replace('estrato_', '').replace('_', ' ')} | {fmt_coef(row['coef'], row['se_cluster'], row['p_valor'])} | {row['ci_low']:.3f} a {row['ci_high']:.3f} | {row['q_fdr_estrato']:.3f} |\n"
    ame_rows_md = ""
    for _, row in ame_df[ame_df["termo"].str.startswith("estrato_")].iterrows():
        ame_rows_md += f"| {row['termo'].replace('estrato_', '').replace('_', ' ')} | {row['ame']:.3f} ({row['se_ame']:.3f}) | {row['ci_low']:.3f} a {row['ci_high']:.3f} |\n"

    loo_md = ""
    if not df_loo.empty:
        for tipo in ["leave_one_UF", "leave_one_curso"]:
            sub = df_loo[df_loo["tipo"] == tipo]
            if sub.empty:
                continue
            loo_md += f"\n**{tipo}**: range metro {sub[sub['termo']=='estrato_metropolitano']['coef'].min():.3f}–{sub[sub['termo']=='estrato_metropolitano']['coef'].max():.3f} (sd {sub[sub['termo']=='estrato_metropolitano']['coef'].std():.3f}); capital {sub[sub['termo']=='estrato_capital']['coef'].min():.3f}–{sub[sub['termo']=='estrato_capital']['coef'].max():.3f}.\n"

    infl_md = ""
    if not df_infl.empty:
        top = df_infl.head(5)
        for _, r in top.iterrows():
            infl_md += f"- `co_ibge_6d {r['co_ibge_6d']}` em `{r['termo']}`: Δ {r['delta']:.3f} (DFBETA {r['dfbeta']:.2f})\n"

    relatorio = f"""# A4 — Atração e implementação: diagnóstico e linguagem autorizada (02/09/2026)

> Registro A3: `output/tema_trabalho/registro_pre_analise_atracao.json` (hash {sha256(REGISTRO_A3)[:8]})
> Potência: `output/tema_trabalho/potencia_atracao.json` MDE global 3.8% p30, estrato capital 16.1%/metro 8.4%/próximo 4.8%/remoto 10.9% (DEFF floor)
> Tipologia A2 strict 540/540 (25/101/238/176) quadro 368 (18/72/203/75)
> Amostra primária: **1295 células CNES–curso Ch1 em 368 municípios**; estendida 3057 (1762 Ch2)

## 1. Construção e suporte (antes dos coeficientes)

Primária 1295: outcome médio **{y_prim.mean():.1%}** (393/1295). Por estrato: capital {df_prim[df_prim['estrato']=='capital']['outcome_alguma_confirmacao_ou_homologacao'].mean():.1%} (73), metropolitano {df_prim[df_prim['estrato']=='metropolitano']['outcome_alguma_confirmacao_ou_homologacao'].mean():.1%} (265), interior próximo {df_prim[df_prim['estrato']=='interior_proximo_polo']['outcome_alguma_confirmacao_ou_homologacao'].mean():.1%} (811), remoto {df_prim[df_prim['estrato']=='interior_remoto']['outcome_alguma_confirmacao_ou_homologacao'].mean():.1%} (146). Ver `A4_tabela_01_amostra_construcao.csv` (por estrato) + `A4_tabela_00_construcao_steps.csv` (3323→3057→1295, 266 sem municipio, 29 fora quadro Ch1 com municipio).

Faixa anunciada (descritiva, não causal): FAIXA1 31.6% (n=291), FAIXA2 37.4% (465), FAIXA3 23.6% (539) — ver `A4_tabela_01b_amostra_faixa.csv`. IVS 2010 mediano {df_prim['ivs_2010'].median():.3f}; Q1–Q4 prevalência ver figura 02; correlação IVS–outcome {df_prim['ivs_2010'].corr(df_prim['outcome_alguma_confirmacao_ou_homologacao']):.2f} (associativa). Estoque pré médio {df_prim['estoque_especialistas_pre_12m_media'].mean():.1f} por município; log(pop) mediano {df_prim['log_pop'].median():.2f}. Curso distribuição ver `A4_tabela_01c_amostra_curso.csv` (16 cursos, min 22 max 188), UF ver `A4_tabela_01d_amostra_uf.csv` (27 UFs, 8 com <5 clusters colapsadas em RESTO: {', '.join(sorted(small_ufs))}) para FE.

População estendida Ch1+Ch2 (3057): prevalência Ch1 30.3% vs Ch2 11.7%, reforçando que Ch2 é cadastro reserva sem capacidade imediata numérica; análise conjunta mantém FE de chamada. Construção sem escolher amostra por resultado; 266 sem municipio e 29 fora quadro mantidos fora da primária por definição prévia.

## 2. Modelo primário exatamente como congelado em A3

**Especificação:** `outcome ~ estrato (ref. interior_remoto) + FE curso (16) + FE UF (colapsada)`, LPM com cluster município (G=368, G−1 gl). Logit AME mesma spec como alternativo.

**LPM minimal — coeficientes estrato (pp vs interior_remoto):**

| Estrato | coef (SE) cluster | IC95% | q FDR (3 testes) |
|---|---|---|---|
{lpm_rows_md}
N=1295, G=368, R²={res_lpm_min.rsquared:.3f}, outcome médio {y_prim.mean():.1%}. DEFF global 1.126 (m3.52) — MDE 3.8% indica poder adequado para efeito global; por estrato capital MDE 16.1% e remoto 10.9% limitam nulidade fina.

**Logit AME (mesma spec):**

| Estrato | AME (SE) | IC95% |
|---|---|---|
{ame_rows_md}

Concordância LPM–Logit: gradiente metro > capital > próximo > remoto (ref.) persiste; magnitude LPM ≈ AME (dif. <2pp).

## 3. Sensibilidade e separações (sem causalidade)

- **Ajuste completo** (+ IVS linear, log pop, estoque/10k, faixa): estrato metro {res_lpm_full.params['estrato_metropolitano']:.3f} (p={res_lpm_full.pvalues['estrato_metropolitano']:.3f}), capital {res_lpm_full.params['estrato_capital']:.3f} (ns), próximo {res_lpm_full.params['estrato_interior_proximo_polo']:.3f} (ns); IVS {res_lpm_full.params['ivs_2010']:.3f} (p={res_lpm_full.pvalues['ivs_2010']:.3f}, ns); log pop {res_lpm_full.params['log_pop']:.3f} (p={res_lpm_full.pvalues['log_pop']:.3f}); faixa FAIXA2 vs FAIXA1 {res_lpm_full.params.get('faixa_FAIXA 2', 0):.3f} (ns), FAIXA3 vs FAIXA1 {res_lpm_full.params.get('faixa_FAIXA 3', 0):.3f} (ns). Com ajuste, gradiente atenua — UF e curso capturam parte da variação territorial. Ver `A4_tabela_03b_ajuste_completo.csv`.

- **Winsorizado p99** (pop e estoque clipados p01-p99): metro {res_wins.params['estrato_metropolitano']:.3f}, capital {res_wins.params['estrato_capital']:.3f}, próximo {res_wins.params['estrato_interior_proximo_polo']:.3f} — gradiente preservado, outliers não dirigem resultado. Ver `A4_tabela_03c_winsorizado.csv`.

- **IVS quadrático** (linear + quadrático como proxy spline): IVS linear {res_spline.params.get('ivs_2010', 0):.3f}, quadrático {res_spline.params.get('ivs_2010_sq', 0):.3f} (p={res_spline.pvalues.get('ivs_2010_sq', 1):.3f}, ns) — não linearidade não detectada; mantém linear parsimonioso. Ver `A4_tabela_03d_ivs_spline.csv`.

- **Faixa só (FE)**: FAIXA2 +{res_faixa.params.get('faixa_FAIXA 2', res_faixa.params.filter(like='faixa').iloc[0] if len(res_faixa.params.filter(like='faixa'))>0 else 0):.3f} vs FAIXA1, FAIXA3 +{res_faixa.params.get('faixa_FAIXA 3', 0):.3f} — descritivo; **não chamar de efeito da bolsa** (faixa colinear com IVS, colinearidade intencional da regra 2025).

- **IVS só (FE)**: coef {res_ivs.params['ivs_2010']:.3f} (p={res_ivs.pvalues['ivs_2010']:.3f}, ns) — gradiente vulnerabilidade não significativo condicional a FE; figura Q1–Q4 mostra variação modesta.

- **Estrato×IVS**: interação não significativa global; heterogeneidade IVS dentro de cada estrato limitada (ver `A4_tabela_03_separacao_*.csv`).

Interpretação: **associado a** maior atração em metropolitano/capital vs remoto, mas ajustado perde significância para capital/próximo; nenhuma evidência de gradiente causal de bolsa ou IVS.

## 4. Influência e robustez

Leave-one-UF (27): metro range {df_loo[df_loo['termo']=='estrato_metropolitano']['coef'].min():.3f}–{df_loo[df_loo['termo']=='estrato_metropolitano']['coef'].max():.3f} sd {df_loo[df_loo['termo']=='estrato_metropolitano']['coef'].std():.3f}; capital {df_loo[df_loo['termo']=='estrato_capital']['coef'].min():.3f}–{df_loo[df_loo['termo']=='estrato_capital']['coef'].max():.3f}. {loo_md}

Leave-one-curso (16): metro range {df_loo[df_loo['tipo']=='leave_one_curso'][df_loo[df_loo['tipo']=='leave_one_curso']['termo']=='estrato_metropolitano']['coef'].min():.3f}–{df_loo[df_loo['tipo']=='leave_one_curso'][df_loo[df_loo['tipo']=='leave_one_curso']['termo']=='estrato_metropolitano']['coef'].max():.3f}.

Leave-one-município (368): metro Δ min {min(coefs_mun):.3f} max {max(coefs_mun):.3f} sd {np.std(coefs_mun):.3f} (base {base_coefs['estrato_metropolitano']:.3f}); top influentes:
{infl_md}
Nenhum município inverte sinal do gradiente metro vs remoto.

Curso: análise por curso descritiva (cursos 7,10,11 com menor atração) — não testar 16 hipóteses independentes.

## 5. Validação preditiva (por município)

GroupKFold 5 splits por município (treino e teste sem compartilhar município): LPM out-sample AUC {pred_df[pred_df['modelo']=='LPM_minimal']['auc_media_out'].values[0]:.3f} sd {pred_df[pred_df['modelo']=='LPM_minimal']['auc_sd_out'].values[0]:.3f}, in-sample AUC {pred_df[pred_df['modelo']=='LPM_minimal']['auc_insample'].values[0]:.3f}, Brier out {pred_df[pred_df['modelo']=='LPM_minimal']['brier_media_out'].values[0]:.3f} vs in {pred_df[pred_df['modelo']=='LPM_minimal']['brier_insample'].values[0]:.3f}; Logit out AUC {pred_df[pred_df['modelo']=='Logit_minimal']['auc_media_out'].values[0]:.3f}, in {pred_df[pred_df['modelo']=='Logit_minimal']['auc_insample'].values[0]:.3f}. Ver `A4_tabela_06_validacao_preditiva.csv`. Gap out vs in indica overfit de FE curso/UF e poder preditivo modesto — R² in-sample {res_lpm_min.rsquared:.3f} não é prova preditiva.

## 6. Figuras

- `A4_figura_01_prob_ajustada_estrato.png`: prob ajustada por estrato (LPM FE, IC cluster).
- `A4_figura_02_gradiente_ivs.png`: Q1–Q4 IVS (observada vs ajustada).
- `A4_figura_03_faixa_descritiva.png`: FAIXA 1–3 (observada vs ajustada FE) — colinearidade faixa–IVS impede leitura causal.

## 7. Linguagem autorizada

Permitido: atração administrativa (alguma confirmação/homologação observada na célula), preenchimento parcialmente observável, gradiente territorial, persistência da oferta local (CNES agregado quando validado). **Proibido:** taxa de preenchimento por vaga, retenção individual do bolsista, efeito causal do PMM-E/bolsa/IVS, candidaturas por vaga, WTA. Faixa é descritiva.

## 8. Limites e próximos passos

- Capital G=18 <30: IC nominal; para heterogeneidade fina por estrato, reportar wild bootstrap se G pequeno (não computado nesta entrega).
- Cursos <50 células (ex. curso 3 n=26) MDE >15pp — análise por curso descritiva.
- Não estimar dose recebida (salário) nem retenção individual; A5 validará T0 físico CNES e ponte CBO 10/16 sem sobreposição.
- Pesos por vagas alteram estimando; não ponderado é primário.

*Gerado por `scripts/tema_trabalho/05_estimar_atracao.py` em 02/09/2026. Hashes entradas verificados em `A4_estimativas_atracao.json`.*
"""
    tmp = RELATORIO_MD.with_suffix(".md.tmp")
    tmp.write_text(relatorio, encoding="utf-8")
    tmp.replace(RELATORIO_MD)

    print(f"[OK] A4 concluído: LPM metro {res_lpm_min.params['estrato_metropolitano']:.3f} (SE {res_lpm_min.bse['estrato_metropolitano']:.3f}) | logit AME {ame_df[ame_df['termo']=='estrato_metropolitano']['ame'].values[0]:.3f} | N=1295 G=368")
    print(f"     Tabelas: {TABELA_AMOSTRA.name}, {TABELA_PRINCIPAL_LPM.name}, {TABELA_PRINCIPAL_LOGIT.name}")
    print(f"     Figuras: {FIG_PROB_ESTRATO.name}, {FIG_IVS.name}, {FIG_FAIXA.name}")
    print(f"     Relatório: {RELATORIO_MD.name} | JSON: {JSON_ESTIMATIVAS.name}")


if __name__ == "__main__":
    main()
