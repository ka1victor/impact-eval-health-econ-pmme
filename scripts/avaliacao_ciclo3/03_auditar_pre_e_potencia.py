#!/usr/bin/env python3
"""C3-03: diagnósticos exclusivamente pré-tratamento e pré-análise.

O script separa dois portões: o CNES pré-T0 autoriza o torneio de força de
trabalho; a incompletude do SIH bloqueia somente o módulo clínico. Nenhuma
competência >= T0 é lida e nenhum efeito do ciclo 3 é estimado aqui.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "avaliacao_ciclo3"
CNES_OUT = OUT / "cnes_pre"
COHORT = OUT / "coorte_c3_congelada.parquet"
MUNICIPAL = ROOT / "output" / "aquisicao" / "painel_municipios_regioes.parquet"
CNES_MONTHLY = ROOT / "output" / "aquisicao" / "cnes_mensal"
SIH_MANIFEST = OUT / "manifesto_sih_pre.json"
PROTOCOL_DOC = ROOT / "docs" / "05_identificacao" / "13_plano_pre_analise_ciclo3.md"

T0 = "202609"
PRE_START = "202406"
PRE_END = "202607"
MONTHS = pd.period_range(PRE_START, PRE_END, freq="M").strftime("%Y%m").tolist()
SEED = 20260831
COURSES = {
    1: {"module": "anestesiologia", "cbo": "225151", "role": "principal"},
    12: {"module": "oncologia_clinica", "cbo": "225121", "role": "generalizacao"},
    24: {"module": "medicina_intensiva", "cbo": "225150", "role": "generalizacao"},
    2: {"module": "cirurgia_geral_cbo_exclusivo", "cbo": "225225", "role": "sensibilidade"},
}
ARM_TREATED = "imediata_pura"
ARM_CONTROL = "nao_priorizada_pura"
MIN_RELEVANT_CHANGE = 1.0
EQUIV_LEVEL_BOUND = 0.5
EQUIV_SLOPE_BOUND = MIN_RELEVANT_CHANGE / 12.0
N_SIM = 5000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv_if_changed(frame: pd.DataFrame, path: Path) -> None:
    """Evita tocar artefato idêntico e contorna leitores que o mantêm aberto."""
    content = frame.to_csv(index=False, lineterminator="\n")
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    try:
        temporary.replace(path)
    except PermissionError:
        # Alguns leitores do Windows permitem sobrescrever o conteúdo, mas
        # bloqueiam a troca atômica do inode.
        shutil.copyfile(temporary, path)
        temporary.unlink()


def validate_inputs() -> list[Path]:
    if not COHORT.exists() or not MUNICIPAL.exists():
        raise FileNotFoundError("Coorte C3 ou painel municipal ausente")
    files = [CNES_MONTHLY / f"cnes_vinculos_medicos_{m}.parquet" for m in MONTHS]
    missing = [p.name for p in files if not p.exists()]
    if missing:
        raise FileNotFoundError(f"CNES pré incompleto: {missing}")
    found = sorted(CNES_MONTHLY.glob("cnes_vinculos_medicos_*.parquet"))
    post = [p.name for p in found if p.stem.rsplit("_", 1)[-1] >= T0]
    # Arquivos pós podem existir no futuro; este script jamais os inclui.
    if any(m >= T0 for m in MONTHS):
        raise AssertionError("Lista de leitura contém competência >= T0")
    return files


def freeze_municipal_arms(cohort: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    records: list[dict] = []
    excluded: list[dict] = []
    for course, spec in COURSES.items():
        sub = cohort.loc[cohort["cod_curso"].eq(course)].copy()
        for ibge, group in sub.groupby("ibge", sort=True):
            arms = sorted(group["classificacao_braco"].unique().tolist())
            if arms == [ARM_TREATED]:
                arm, treated, eligible = ARM_TREATED, 1, True
            elif arms == [ARM_CONTROL]:
                arm, treated, eligible = ARM_CONTROL, 0, True
            else:
                arm, treated, eligible = "excluido_regra_municipal", np.nan, False
            row = {
                "ibge": str(ibge).zfill(6),
                "cod_curso": course,
                "modulo": spec["module"],
                "cbo": spec["cbo"],
                "papel": spec["role"],
                "bracos_cnes_curso": "|".join(arms),
                "braco_municipal": arm,
                "tratado": treated,
                "elegivel": eligible,
                "n_cnes_propostos": int(group["cnes"].nunique()),
                "n_vagas_imediatas": int(group["qt_vagas_imediatas_gestor"].sum()),
                "n_propostas_nao_priorizadas": int(group["qt_propostas_nao_priorizadas_gestor"].sum()),
                "cointervencao_cirurgica_muni": bool(group["cointervencao_cirurgica_muni"].any()),
                "uf": str(group["uf"].iloc[0]),
                "regiao": str(group["regiao"].iloc[0]),
            }
            (records if eligible else excluded).append(row)
    eligible_df = pd.DataFrame(records).sort_values(["cod_curso", "ibge"]).reset_index(drop=True)
    excluded_df = pd.DataFrame(excluded).sort_values(["cod_curso", "ibge"]).reset_index(drop=True)
    return eligible_df, excluded_df


def freeze_cnes_arms(cohort: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Contraste direto na célula administrativa CNES--curso."""
    records, excluded = [], []
    for course, spec in COURSES.items():
        sub = cohort.loc[cohort["cod_curso"].eq(course)].copy()
        for cnes, group in sub.groupby("cnes", sort=True):
            arms = sorted(group["classificacao_braco"].unique().tolist())
            if arms == [ARM_TREATED]:
                arm, treated, eligible = ARM_TREATED, 1, True
            elif arms == [ARM_CONTROL]:
                arm, treated, eligible = ARM_CONTROL, 0, True
            else:
                arm, treated, eligible = "excluido_regra_cnes", np.nan, False
            row = {
                "cnes": str(cnes).zfill(7), "ibge": str(group["ibge"].iloc[0]).zfill(6),
                "cod_curso": course, "modulo": spec["module"], "cbo": spec["cbo"],
                "papel": spec["role"], "bracos_cnes_curso": "|".join(arms),
                "braco_cnes": arm, "tratado": treated, "elegivel": eligible,
                "n_cnes_propostos": 1,
                "n_vagas_imediatas": int(group["qt_vagas_imediatas_gestor"].sum()),
                "n_propostas_nao_priorizadas": int(group["qt_propostas_nao_priorizadas_gestor"].sum()),
                "cointervencao_cirurgica_muni": bool(group["cointervencao_cirurgica_muni"].any()),
                "uf": str(group["uf"].iloc[0]), "regiao": str(group["regiao"].iloc[0]),
            }
            (records if eligible else excluded).append(row)
    return (
        pd.DataFrame(records).sort_values(["cod_curso", "cnes"]).reset_index(drop=True),
        pd.DataFrame(excluded).sort_values(["cod_curso", "cnes"]).reset_index(drop=True),
    )


def load_cnes_panel(files: list[Path], units: pd.DataFrame) -> pd.DataFrame:
    wanted_munis = set(units["ibge"])
    cbo_to_course = {x["cbo"]: c for c, x in COURSES.items()}
    wanted_cbos = set(cbo_to_course)
    presence: dict[tuple[int, str, str], set[str]] = {}
    generic: dict[tuple[int, str, str], set[str]] = {}

    columns = ["competencia", "co_profissional_sus", "co_cbo_6d", "ind_vinculacao", "co_municipio_gestor"]
    for month, path in zip(MONTHS, files, strict=True):
        frame = pd.read_parquet(path, columns=columns, filters=[("co_cbo_6d", "in", sorted(wanted_cbos))])
        frame["co_municipio_gestor"] = frame["co_municipio_gestor"].astype(str).str.zfill(6)
        frame["co_cbo_6d"] = frame["co_cbo_6d"].astype(str).str.zfill(6)
        frame["co_profissional_sus"] = frame["co_profissional_sus"].fillna("").astype(str).str.strip()
        frame = frame.loc[
            frame["co_municipio_gestor"].isin(wanted_munis)
            & frame["co_cbo_6d"].isin(wanted_cbos)
            & frame["co_profissional_sus"].ne("")
        ].drop_duplicates(["co_municipio_gestor", "co_cbo_6d", "co_profissional_sus"])
        if not frame.empty and not frame["competencia"].astype(str).eq(month).all():
            raise AssertionError(f"Competência interna divergente em {path.name}")
        for (muni, cbo), group in frame.groupby(["co_municipio_gestor", "co_cbo_6d"], sort=False):
            course = cbo_to_course[str(cbo)]
            key = (course, str(muni), month)
            people = set(group["co_profissional_sus"])
            presence[key] = people
            generic[key] = set(group.loc[group["ind_vinculacao"].astype(str).eq("070102"), "co_profissional_sus"])

    rows: list[dict] = []
    by_course_month_munis = {
        course: units.loc[units["cod_curso"].eq(course), "ibge"].tolist()
        for course in COURSES
    }
    for course, munis in by_course_month_munis.items():
        for muni in munis:
            series = [presence.get((course, muni, month), set()) for month in MONTHS]
            generic_series = [generic.get((course, muni, month), set()) for month in MONTHS]
            for idx, month in enumerate(MONTHS):
                current = series[idx]
                entry = np.nan
                exit_ = np.nan
                retained6 = np.nan
                if idx >= 6:
                    prior = set().union(*series[idx - 6:idx])
                    entry_people = current - prior
                    entry = len(entry_people)
                    if idx + 6 < len(MONTHS):
                        retained6 = len(entry_people & series[idx + 6])
                if idx + 3 < len(MONTHS):
                    future = set().union(*series[idx + 1:idx + 4])
                    exit_ = len(current - future)
                rows.append({
                    "ibge": muni,
                    "cod_curso": course,
                    "modulo": COURSES[course]["module"],
                    "cbo": COURSES[course]["cbo"],
                    "competencia": month,
                    "especialistas_distintos": len(current),
                    "vinculo_070102_generico_distintos": len(generic_series[idx]),
                    "n_entradas_apos_6m_ausencia": entry,
                    "n_saidas_confirmadas_3m": exit_,
                    "n_entrantes_presentes_6m": retained6,
                    "churn_observavel": entry + exit_ if not (pd.isna(entry) or pd.isna(exit_)) else np.nan,
                })
    panel = pd.DataFrame(rows).merge(
        units.drop(columns=["modulo", "cbo"]), on=["ibge", "cod_curso"], how="left", validate="many_to_one"
    )
    panel["indice_mes"] = panel["competencia"].map({m: i for i, m in enumerate(MONTHS)}).astype(int)
    if panel.duplicated(["ibge", "cod_curso", "competencia"]).any():
        raise AssertionError("Painel CNES não é único")
    expected = len(units) * len(MONTHS)
    if len(panel) != expected or panel["competencia"].max() >= T0:
        raise AssertionError("Painel CNES desbalanceado ou contaminado pelo pós")
    return panel.sort_values(["cod_curso", "ibge", "competencia"]).reset_index(drop=True)


def load_cnes_establishment_panel(files: list[Path], units: pd.DataFrame) -> pd.DataFrame:
    wanted = set(units["cnes"])
    cbo_to_course = {x["cbo"]: c for c, x in COURSES.items()}
    wanted_cbos = set(cbo_to_course)
    presence, generic = {}, {}
    columns = ["competencia", "co_cnes_7d", "co_profissional_sus", "co_cbo_6d", "ind_vinculacao"]
    for month, path in zip(MONTHS, files, strict=True):
        frame = pd.read_parquet(path, columns=columns, filters=[("co_cbo_6d", "in", sorted(wanted_cbos))])
        frame["co_cnes_7d"] = frame["co_cnes_7d"].astype(str).str.zfill(7)
        frame["co_cbo_6d"] = frame["co_cbo_6d"].astype(str).str.zfill(6)
        frame["co_profissional_sus"] = frame["co_profissional_sus"].fillna("").astype(str).str.strip()
        frame = frame.loc[
            frame["co_cnes_7d"].isin(wanted) & frame["co_cbo_6d"].isin(wanted_cbos)
            & frame["co_profissional_sus"].ne("")
        ].drop_duplicates(["co_cnes_7d", "co_cbo_6d", "co_profissional_sus"])
        for (cnes, cbo), group in frame.groupby(["co_cnes_7d", "co_cbo_6d"], sort=False):
            key = (cbo_to_course[str(cbo)], str(cnes), month)
            presence[key] = set(group["co_profissional_sus"])
            generic[key] = set(group.loc[group["ind_vinculacao"].astype(str).eq("070102"), "co_profissional_sus"])
    rows = []
    for course in COURSES:
        for cnes in units.loc[units["cod_curso"].eq(course), "cnes"]:
            series = [presence.get((course, cnes, month), set()) for month in MONTHS]
            generic_series = [generic.get((course, cnes, month), set()) for month in MONTHS]
            for idx, month in enumerate(MONTHS):
                current = series[idx]
                entry = exit_ = retained6 = np.nan
                if idx >= 6:
                    entrants = current - set().union(*series[idx - 6:idx])
                    entry = len(entrants)
                    if idx + 6 < len(MONTHS):
                        retained6 = len(entrants & series[idx + 6])
                if idx + 3 < len(MONTHS):
                    exit_ = len(current - set().union(*series[idx + 1:idx + 4]))
                rows.append({
                    "cnes": cnes, "cod_curso": course, "modulo": COURSES[course]["module"],
                    "cbo": COURSES[course]["cbo"], "competencia": month,
                    "especialistas_distintos": len(current),
                    "vinculo_070102_generico_distintos": len(generic_series[idx]),
                    "n_entradas_apos_6m_ausencia": entry, "n_saidas_confirmadas_3m": exit_,
                    "n_entrantes_presentes_6m": retained6,
                    "churn_observavel": entry + exit_ if not (pd.isna(entry) or pd.isna(exit_)) else np.nan,
                })
    panel = pd.DataFrame(rows).merge(
        units.drop(columns=["modulo", "cbo"]), on=["cnes", "cod_curso"], how="left", validate="many_to_one"
    )
    panel["indice_mes"] = panel["competencia"].map({m: i for i, m in enumerate(MONTHS)}).astype(int)
    if panel.duplicated(["cnes", "cod_curso", "competencia"]).any() or len(panel) != len(units) * len(MONTHS):
        raise AssertionError("Painel CNES-estabelecimento não é balanceado e único")
    return panel.sort_values(["cod_curso", "cnes", "competencia"]).reset_index(drop=True)


def two_way_demean(values: np.ndarray, unit: np.ndarray, time: np.ndarray, weights: np.ndarray) -> np.ndarray:
    frame = pd.DataFrame({"unit": unit, "time": time, "w": weights})
    result = np.empty_like(values, dtype=float)
    for j in range(values.shape[1]):
        frame["v"] = values[:, j]
        unit_mean = frame.groupby("unit", sort=False)["v"].transform("mean").to_numpy()
        time_num = (frame["v"] * frame["w"]).groupby(frame["time"], sort=False).transform("sum")
        time_den = frame["w"].groupby(frame["time"], sort=False).transform("sum")
        time_mean = (time_num / time_den).to_numpy()
        overall = float(np.average(frame["v"], weights=frame["w"]))
        result[:, j] = values[:, j] - unit_mean - time_mean + overall
    return result


def fit_fe_cluster(
    data: pd.DataFrame,
    y_col: str,
    x_cols: list[str],
    weight_col: str = "peso",
    unit_col: str = "ibge",
    cluster_col: str = "ibge",
) -> dict:
    clean = data.dropna(subset=[y_col, *x_cols, weight_col]).copy()
    y = clean[[y_col]].to_numpy(float)
    x = clean[x_cols].to_numpy(float)
    w = clean[weight_col].to_numpy(float)
    unit = clean[unit_col].to_numpy()
    cluster_values = clean[cluster_col].to_numpy()
    time = clean["competencia"].to_numpy()
    yd = two_way_demean(y, unit, time, w)[:, 0]
    xd = two_way_demean(x, unit, time, w)
    sw = np.sqrt(w)
    yw, xw = yd * sw, xd * sw[:, None]
    xtx_inv = np.linalg.pinv(xw.T @ xw)
    beta = xtx_inv @ (xw.T @ yw)
    resid = yw - xw @ beta
    clusters = pd.unique(cluster_values)
    n, k, g = len(clean), len(x_cols), len(clusters)
    vcov = cluster_vcov(xw, resid, cluster_values)
    se = np.sqrt(np.maximum(np.diag(vcov), 0))
    tval = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se > 0)
    pval = 2 * stats.t.sf(np.abs(tval), df=max(g - 1, 1))
    return {
        "coef": beta, "se": se, "p": pval, "vcov": vcov,
        "n": n, "clusters": g, "resid": resid, "x_within_weighted": xw,
        "unit": cluster_values, "df": max(g - 1, 1), "y_within_weighted": yw,
    }


def cluster_vcov(x: np.ndarray, residual: np.ndarray, clusters: np.ndarray) -> np.ndarray:
    unique = pd.unique(clusters)
    n, k, g = len(residual), x.shape[1], len(unique)
    inv = np.linalg.pinv(x.T @ x)
    meat = np.zeros((k, k))
    for cluster in unique:
        idx = clusters == cluster
        score = x[idx].T @ residual[idx]
        meat += np.outer(score, score)
    correction = (g / (g - 1)) * ((n - 1) / max(n - k, 1)) if g > 1 else np.nan
    return correction * inv @ meat @ inv


def wild_cluster_pvalue(fit: dict, coefficient: int = 0, reps: int = 999, seed: int = SEED) -> float:
    """Wild cluster bootstrap-t restrito e reestudantizado, pesos Rademacher."""
    rng = np.random.default_rng(seed)
    x = fit["x_within_weighted"]
    y = fit["y_within_weighted"]
    clusters = fit["unit"]
    unique = pd.unique(clusters)
    inv = np.linalg.pinv(x.T @ x)
    observed = abs(fit["coef"][coefficient] / fit["se"][coefficient])
    x_restricted = np.delete(x, coefficient, axis=1)
    if x_restricted.shape[1]:
        beta_restricted = np.linalg.pinv(x_restricted.T @ x_restricted) @ (x_restricted.T @ y)
        fitted_restricted = x_restricted @ beta_restricted
    else:
        fitted_restricted = np.zeros_like(y)
    residual_restricted = y - fitted_restricted
    exceed = 0
    for _ in range(reps):
        signs = dict(zip(unique, rng.choice([-1.0, 1.0], len(unique)), strict=True))
        y_star = fitted_restricted + residual_restricted * np.array([signs[u] for u in clusters])
        beta_star = inv @ (x.T @ y_star)
        residual_star = y_star - x @ beta_star
        se_star = math.sqrt(max(cluster_vcov(x, residual_star, clusters)[coefficient, coefficient], 0))
        t_star = abs(beta_star[coefficient] / se_star) if se_star > 0 else math.inf
        exceed += t_star >= observed
    return (exceed + 1) / (reps + 1)


def audit_estimators() -> dict:
    """Compara o estimador within com uma regressão de dummies independente."""
    rng = np.random.default_rng(9127)
    units = [f"u{i}" for i in range(12)]
    months = [f"m{i}" for i in range(8)]
    frame = pd.MultiIndex.from_product([units, months], names=["ibge", "competencia"]).to_frame(index=False)
    frame["x"] = rng.normal(size=len(frame))
    u_fe = {u: rng.normal() for u in units}
    t_fe = {m: rng.normal() for m in months}
    frame["y"] = 0.7 * frame["x"] + frame["ibge"].map(u_fe) + frame["competencia"].map(t_fe) + rng.normal(0, .1, len(frame))
    frame["peso"] = 1.0
    within = fit_fe_cluster(frame, "y", ["x"])
    design = pd.concat([
        frame[["x"]],
        pd.get_dummies(frame["ibge"], drop_first=True, dtype=float),
        pd.get_dummies(frame["competencia"], drop_first=True, dtype=float),
    ], axis=1)
    design.insert(0, "const", 1.0)
    explicit = np.linalg.lstsq(design.to_numpy(float), frame["y"].to_numpy(float), rcond=None)[0][1]
    difference = abs(float(within["coef"][0]) - float(explicit))
    p1 = wild_cluster_pvalue(within, reps=199, seed=77)
    p2 = wild_cluster_pvalue(within, reps=199, seed=77)
    if difference > 1e-10 or p1 != p2:
        raise AssertionError("Auditoria independente do estimador/bootstrap falhou")
    return {
        "status": "APROVADA",
        "coeficiente_within": float(within["coef"][0]),
        "coeficiente_dummies": float(explicit),
        "diferenca_absoluta": difference,
        "bootstrap_deterministico": True,
        "observacao": "Auditoria sintética de construção FE, clusters e reprodutibilidade; nenhum efeito real estimado.",
    }


def fit_propensity(covariates: pd.DataFrame) -> pd.DataFrame:
    data = covariates.copy()
    numeric = ["media_pre", "ultimo_pre", "desvio_pre", "prop_zero_pre", "tendencia_pre", "ivs_2010", "log_pop_2010", "n_cnes_propostos"]
    x_num = data[numeric].astype(float)
    x_num = x_num.fillna(x_num.median())
    sd = x_num.std(ddof=0).replace(0, 1)
    x_num = (x_num - x_num.mean()) / sd
    dummies = pd.get_dummies(data["regiao"].fillna("IGNORADA"), prefix="regiao", drop_first=True, dtype=float)
    x = np.column_stack([np.ones(len(data)), x_num.to_numpy(), dummies.to_numpy()])
    y = data["tratado"].to_numpy(float)

    def objective(beta: np.ndarray) -> tuple[float, np.ndarray]:
        z = np.clip(x @ beta, -30, 30)
        p = 1 / (1 + np.exp(-z))
        penalty = 0.5 * np.sum(beta[1:] ** 2)
        value = -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)) + penalty
        grad = x.T @ (p - y)
        grad[1:] += beta[1:]
        return value, grad

    result = optimize.minimize(lambda b: objective(b), np.zeros(x.shape[1]), jac=True, method="BFGS")
    if not result.success and np.linalg.norm(result.jac) > 1e-4:
        raise RuntimeError(f"Propensão não convergiu: {result.message}")
    p = np.clip(1 / (1 + np.exp(-np.clip(x @ result.x, -30, 30))), 0.001, 0.999)
    data["propensao_pre"] = p
    data["peso_sobreposicao"] = np.where(y == 1, 1 - p, p)
    lo = max(data.loc[y == 1, "propensao_pre"].min(), data.loc[y == 0, "propensao_pre"].min())
    hi = min(data.loc[y == 1, "propensao_pre"].max(), data.loc[y == 0, "propensao_pre"].max())
    data["suporte_comum"] = data["propensao_pre"].between(lo, hi, inclusive="both")
    data["limite_inferior_suporte"] = float(lo)
    data["limite_superior_suporte"] = float(hi)
    return data


def six_month_power(frame: pd.DataFrame, entity_col: str = "ibge") -> dict:
    wide = frame.pivot(index=entity_col, columns="competencia", values="especialistas_distintos")
    change = (wide[PRE_END] - wide["202601"]).rename("mudanca_6m").to_frame()
    unit_info = frame.drop_duplicates(entity_col)
    if entity_col == "ibge":
        arms = unit_info[["ibge", "tratado", "peso_sobreposicao"]].set_index("ibge")
        arms["cluster"] = arms.index
    else:
        arms = unit_info[[entity_col, "tratado", "ibge", "peso_sobreposicao"]].set_index(entity_col).rename(columns={"ibge": "cluster"})
    change = change.join(arms).dropna()
    treated = change.loc[change["tratado"].eq(1), "mudanca_6m"].to_numpy(float)
    control = change.loc[change["tratado"].eq(0), "mudanca_6m"].to_numpy(float)
    if len(treated) < 2 or len(control) < 2:
        return {"mde_80": None, "potencia_efeito_1": None, "n_tratados": len(treated), "n_controles": len(control)}
    weighted_means = change.groupby("tratado").apply(
        lambda x: np.average(x["mudanca_6m"], weights=x["peso_sobreposicao"]),
        include_groups=False,
    )
    change["residuo_ponderado"] = change["peso_sobreposicao"] * (
        change["mudanca_6m"] - change["tratado"].map(weighted_means)
    )
    cluster = change.groupby(["cluster", "tratado"]).agg(
        sum=("residuo_ponderado", "sum"), weight=("peso_sobreposicao", "sum")
    ).unstack(fill_value=0)
    for arm in [0.0, 1.0]:
        for stat_name in ["sum", "weight"]:
            if (stat_name, arm) not in cluster.columns:
                cluster[(stat_name, arm)] = 0.0
    cluster = cluster.sort_index(axis=1)
    rng = np.random.default_rng(SEED + int(frame["cod_curso"].iloc[0]))
    g = len(cluster)
    sampled = rng.integers(0, g, size=(N_SIM, g))
    sums_t = cluster[("sum", 1.0)].to_numpy()[sampled].sum(axis=1)
    sums_c = cluster[("sum", 0.0)].to_numpy()[sampled].sum(axis=1)
    weight_t = cluster[("weight", 1.0)].to_numpy()[sampled].sum(axis=1)
    weight_c = cluster[("weight", 0.0)].to_numpy()[sampled].sum(axis=1)
    valid = (weight_t > 0) & (weight_c > 0)
    diff0 = sums_t[valid] / weight_t[valid] - sums_c[valid] / weight_c[valid]
    critical = float(np.quantile(np.abs(diff0), .95))
    grid = np.round(np.arange(0, 20.001, .02), 2)
    powers = []
    for effect in grid:
        powers.append(float(np.mean(np.abs(diff0 + effect) > critical)))
    mde = next((float(e) for e, power in zip(grid, powers, strict=True) if power >= .8), None)
    p1 = powers[int(round(1 / .02))]
    return {
        "mde_80": mde,
        "potencia_efeito_1": float(p1),
        "n_tratados": len(treated),
        "n_controles": len(control),
        "clusters_municipais": g,
        "simulacoes": N_SIM,
        "semente": SEED + int(frame["cod_curso"].iloc[0]),
        "mudanca": f"especialistas_distintos_{PRE_END}_menos_202601",
    }


def diagnostic_course(
    panel: pd.DataFrame,
    units: pd.DataFrame,
    municipal: pd.DataFrame,
    course: int,
    level: str = "municipio",
) -> tuple[dict, pd.DataFrame, dict]:
    entity_col = "ibge" if level == "municipio" else "cnes"
    frame = panel.loc[panel["cod_curso"].eq(course)].copy()
    base = frame.groupby(entity_col, as_index=False).agg(
        media_pre=("especialistas_distintos", "mean"),
        ultimo_pre=("especialistas_distintos", "last"),
        desvio_pre=("especialistas_distintos", "std"),
        prop_zero_pre=("especialistas_distintos", lambda x: float((x == 0).mean())),
        media_070102_generico_pre=("vinculo_070102_generico_distintos", "mean"),
    )
    slopes = frame.groupby(entity_col).apply(
        lambda g: np.polyfit(g["indice_mes"], g["especialistas_distintos"], 1)[0],
        include_groups=False,
    ).rename("tendencia_pre").reset_index()
    base = base.merge(slopes, on=entity_col, validate="one_to_one").merge(
        units.loc[units["cod_curso"].eq(course)], on=entity_col, validate="one_to_one"
    )
    mun = municipal.copy()
    mun["co_ibge_6d"] = mun["co_ibge_6d"].astype(str).str.zfill(6)
    keep = ["co_ibge_6d", "ivs_2010", "populacao_2010", "macro_regiao_saude"]
    base = base.merge(
        mun[keep].drop_duplicates("co_ibge_6d"), left_on="ibge", right_on="co_ibge_6d",
        how="left", validate="one_to_one" if level == "municipio" else "many_to_one",
    )
    base["log_pop_2010"] = np.log1p(base["populacao_2010"])
    prop = fit_propensity(base)
    frame = frame.merge(prop[[entity_col, "propensao_pre", "peso_sobreposicao", "suporte_comum"]], on=entity_col, validate="many_to_one")
    frame = frame.loc[frame["suporte_comum"]].copy()
    frame["peso"] = frame["peso_sobreposicao"]
    frame["tratado_tempo"] = frame["tratado"] * (frame["indice_mes"] - frame["indice_mes"].mean())
    trend = fit_fe_cluster(frame, "especialistas_distintos", ["tratado_tempo"], unit_col=entity_col, cluster_col="ibge")
    coef, se = float(trend["coef"][0]), float(trend["se"][0])
    crit90 = stats.t.ppf(.95, trend["df"])
    slope_lo, slope_hi = coef - crit90 * se, coef + crit90 * se

    recent = frame.loc[frame["competencia"].between("202506", PRE_END)].copy()
    lead_months = [m for m in sorted(recent["competencia"].unique()) if m != "202506"]
    for m in lead_months:
        recent[f"lead_{m}"] = recent["tratado"] * recent["competencia"].eq(m).astype(int)
    leads = fit_fe_cluster(recent, "especialistas_distintos", [f"lead_{m}" for m in lead_months], unit_col=entity_col, cluster_col="ibge")
    wald = float(leads["coef"].T @ np.linalg.pinv(leads["vcov"]) @ leads["coef"])
    joint_p = float(stats.chi2.sf(wald, df=len(lead_months)))
    lead_90_lo = leads["coef"] - stats.t.ppf(.95, leads["df"]) * leads["se"]
    lead_90_hi = leads["coef"] + stats.t.ppf(.95, leads["df"]) * leads["se"]
    leads_equiv = bool(np.all(lead_90_lo > -EQUIV_LEVEL_BOUND) and np.all(lead_90_hi < EQUIV_LEVEL_BOUND))
    slope_equiv = bool(slope_lo > -EQUIV_SLOPE_BOUND and slope_hi < EQUIV_SLOPE_BOUND)

    placebo_results = {}
    for cutoff in ["202412", "202506", "202512"]:
        fake = frame.copy()
        fake["placebo"] = fake["tratado"] * fake["competencia"].ge(cutoff).astype(int)
        fit = fit_fe_cluster(fake, "especialistas_distintos", ["placebo"], unit_col=entity_col, cluster_col="ibge")
        placebo_results[cutoff] = {
            "coef": float(fit["coef"][0]), "se_cluster": float(fit["se"][0]), "p": float(fit["p"][0])
        }

    arm_n = prop.groupby("tratado")[entity_col].nunique().to_dict()
    support_n = prop.loc[prop["suporte_comum"]].groupby("tratado")[entity_col].nunique().to_dict()
    retained_t = support_n.get(1.0, 0) / max(arm_n.get(1.0, 0), 1)
    retained_c = support_n.get(0.0, 0) / max(arm_n.get(0.0, 0), 1)
    support_pass = bool(retained_t >= .8 and retained_c >= .8)
    power = six_month_power(frame, entity_col=entity_col)
    enough_clusters = arm_n.get(1.0, 0) >= 20 and arm_n.get(0.0, 0) >= 20
    if course in {12, 24} and not enough_clusters:
        decision = "inviavel"
        reason = "braço tratado tem menos de 20 unidades e ainda menos clusters municipais; generalização apenas descritiva"
    elif support_pass and slope_equiv and leads_equiv and power["mde_80"] is not None and power["mde_80"] <= MIN_RELEVANT_CHANGE:
        decision = "confirmatorio_condicional"
        reason = "suporte, equivalência prévia e potência passaram; causalidade ainda depende de ausência de choques diferenciais pós-T0"
    else:
        decision = "associacao_ajustada"
        failed = []
        if not support_pass: failed.append("suporte")
        if not slope_equiv or not leads_equiv: failed.append("equivalência_pré_tendências")
        if power["mde_80"] is None or power["mde_80"] > MIN_RELEVANT_CHANGE: failed.append("potência")
        reason = "falhou: " + ", ".join(failed)

    result = {
        "modulo": COURSES[course]["module"], "nivel": level, "cod_curso": course, "cbo": COURSES[course]["cbo"],
        "papel": COURSES[course]["role"], "n_tratados": int(arm_n.get(1.0, 0)), "n_controles": int(arm_n.get(0.0, 0)),
        "baseline_tratado": float(prop.loc[prop["tratado"].eq(1), "media_pre"].mean()),
        "baseline_controle": float(prop.loc[prop["tratado"].eq(0), "media_pre"].mean()),
        "suporte_retido_tratado": float(retained_t), "suporte_retido_controle": float(retained_c), "suporte_aprovado": support_pass,
        "pre_tendencia_mensal_coef": coef, "pre_tendencia_mensal_se": se,
        "pre_tendencia_ic90_inf": float(slope_lo), "pre_tendencia_ic90_sup": float(slope_hi),
        "limite_equivalencia_tendencia_mensal": EQUIV_SLOPE_BOUND, "equivalencia_tendencia": slope_equiv,
        "teste_conjunto_leads_p": joint_p, "limite_equivalencia_leads": EQUIV_LEVEL_BOUND, "equivalencia_leads": leads_equiv,
        "placebos_temporais": json.dumps(placebo_results, ensure_ascii=False, sort_keys=True),
        "mde_80_especialistas": power["mde_80"], "potencia_para_um_especialista": power["potencia_efeito_1"],
        "mudanca_minima_relevante": MIN_RELEVANT_CHANGE, "decisao": decision, "razao": reason,
    }
    return result, prop, power


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    CNES_OUT.mkdir(parents=True, exist_ok=True)
    files = validate_inputs()
    cohort = pd.read_parquet(COHORT)
    municipal = pd.read_parquet(MUNICIPAL)
    units, excluded = freeze_municipal_arms(cohort)
    cnes_units, cnes_excluded = freeze_cnes_arms(cohort)
    panel = load_cnes_panel(files, units)
    cnes_panel = load_cnes_establishment_panel(files, cnes_units)

    diagnostics, weights, powers = [], [], {}
    for level, level_panel, level_units in [
        ("cnes_ofertante", cnes_panel, cnes_units),
        ("municipio", panel, units),
    ]:
        for course in COURSES:
            diagnostic, propensity, power = diagnostic_course(level_panel, level_units, municipal, course, level=level)
            diagnostics.append(diagnostic)
            propensity["nivel"] = level
            weights.append(propensity)
            powers[f'{COURSES[course]["module"]}__{level}'] = power
    diagnostic_df = pd.DataFrame(diagnostics)
    weights_df = pd.concat(weights, ignore_index=True)
    audit = audit_estimators()

    panel_path = CNES_OUT / "painel_forca_trabalho_pre.parquet"
    cnes_panel_path = CNES_OUT / "painel_forca_trabalho_cnes_pre.parquet"
    units_path = CNES_OUT / "unidades_elegiveis_congeladas.csv"
    excluded_path = CNES_OUT / "unidades_excluidas_congeladas.csv"
    cnes_units_path = CNES_OUT / "cnes_elegiveis_congelados.csv"
    cnes_excluded_path = CNES_OUT / "cnes_excluidos_congelados.csv"
    weights_path = OUT / "pesos_sobreposicao_pre.csv"
    diagnostics_path = OUT / "diagnosticos_pre.csv"
    panel.to_parquet(panel_path, index=False)
    cnes_panel.to_parquet(cnes_panel_path, index=False)
    write_csv_if_changed(units, units_path)
    write_csv_if_changed(excluded, excluded_path)
    write_csv_if_changed(cnes_units, cnes_units_path)
    write_csv_if_changed(cnes_excluded, cnes_excluded_path)
    write_csv_if_changed(weights_df, weights_path)
    write_csv_if_changed(diagnostic_df, diagnostics_path)

    power_doc = {
        "protocolo": "C3-03-potencia-pre",
        "data_corte": "2026-08-31",
        "t0": T0,
        "outcome": "mudança em especialistas distintos na unidade analítica (CNES ou município) em seis meses",
        "mudanca_minima_relevante": MIN_RELEVANT_CHANGE,
        "metodo": "bootstrap empírico por cluster municipal, no suporte comum e com pesos de sobreposição, de mudanças prévias de seis meses; teste bilateral 5%",
        "resultados": powers,
    }
    write_json(OUT / "potencia_pre.json", power_doc)

    clinical_status = "inviavel"
    clinical_reason = "C3-02B tem 673/675 arquivos; RDAC2606.dbc e RDRR2606.dbc ausentes; nenhum zero imputado"
    decisions = {
        "protocolo": "C3-03-torneio-pre-tratamento",
        "data_decisao": "2026-08-31",
        "t0": T0,
        "regra_interpretacao": "priorização não foi aleatória; p>0,05 isolado não comprova paralelismo",
        "modulos_forca_trabalho": [
            {k: row[k] for k in ["modulo", "nivel", "cod_curso", "cbo", "papel", "n_tratados", "n_controles", "suporte_aprovado", "equivalencia_tendencia", "equivalencia_leads", "mde_80_especialistas", "decisao", "razao"]}
            for row in diagnostics
        ],
        "modulo_clinico_sih": {
            "decisao": clinical_status, "status_operacional": "BLOQUEADO_TEMPORARIAMENTE_FONTE_INCOMPLETA", "razao": clinical_reason,
            "efeito_estimado": False,
        },
        "modulo_sia_ecocardiografia": {
            "decisao": "inviavel", "razao": "não substitui automaticamente o SIH e não venceu critério substantivo prévio; C3-04 não acionado",
        },
        "primeiro_estagio_pmme": {
            "status": "NAO_MENSURAVEL_NOS_PARQUETS_MENSAIS_ATUAIS",
            "razao": "NU_CNPJ_DETALHAMENTO_VINCULO não foi preservado; 070102 isolado não identifica PMM-E ciclo 3",
            "consequencia": "estoque total permanece primário; retenção individual de participantes rebaixada",
        },
        "proxima_estimacao": "somente após seis meses comuns maduros; nunca nesta etapa",
    }
    write_json(OUT / "decisao_torneio_pre.json", decisions)

    generated = [
        panel_path, cnes_panel_path, units_path, excluded_path, cnes_units_path,
        cnes_excluded_path, weights_path, diagnostics_path,
        OUT / "potencia_pre.json", OUT / "decisao_torneio_pre.json", PROTOCOL_DOC,
    ]
    registry = {
        "protocolo": "C3-03-registro-pre-analise",
        "congelado_em": "2026-08-31",
        "t0_calendario": T0,
        "janela_pre": {"inicio": PRE_START, "fim": PRE_END, "competencias": len(MONTHS)},
        "leitura_pos_t0": False,
        "efeitos_pos_tratamento_estimados": False,
        "auditoria_estimadores": audit,
        "assinatura_pmme_completa": False,
        "arquivos_entrada_cnes": {p.name: sha256(p) for p in files},
        "hashes_artefatos_congelados": {str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p) for p in generated},
        "regras": {
            "tratamento_cnes": "todas as observações da célula CNES-curso são imediata_pura",
            "controle_cnes": "todas as observações da célula CNES-curso são nao_priorizada_pura",
            "tratamento_municipio": "todas as células município-curso são imediata_pura",
            "controle_municipio": "todas as células município-curso são nao_priorizada_pura",
            "exclusoes": "qualquer reserva, mista ou combinação local",
            "inferência_futura": "FE de unidade e mês; cluster município; wild cluster bootstrap-t restrito e reestudantizado",
            "synthetic_did": "somente robustez, nunca reparo de pré-tendência",
        },
    }
    write_json(OUT / "registro_pre_analise.json", registry)
    print(diagnostic_df[["modulo", "nivel", "n_tratados", "n_controles", "mde_80_especialistas", "decisao"]].to_string(index=False))
    print("C3-03 concluído sem leitura pós-T0 e sem estimação de efeito.")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] in {"--refresh-protocol-hash", "--refresh-hashes"}:
        registry_path = OUT / "registro_pre_analise.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        if sys.argv[1] == "--refresh-protocol-hash":
            relative = str(PROTOCOL_DOC.relative_to(ROOT)).replace("\\", "/")
            registry["hashes_artefatos_congelados"][relative] = sha256(PROTOCOL_DOC)
        else:
            registry["hashes_artefatos_congelados"] = {
                relative: sha256(ROOT / relative)
                for relative in registry["hashes_artefatos_congelados"]
            }
        write_json(registry_path, registry)
        print("Hashes atualizados sem reler outcomes.")
    else:
        main()
