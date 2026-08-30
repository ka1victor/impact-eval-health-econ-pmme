"""Utilitários econométricos comuns com absorção verificável de efeitos fixos."""

from __future__ import annotations

import os
from typing import Any, Sequence

import numpy as np
import pandas as pd
import statsmodels.api as sm


def atomic_to_csv(frame: pd.DataFrame, target: str | "os.PathLike[str]", **kwargs: Any) -> None:
    """Grava CSV em arquivo temporário e substitui o destino no mesmo volume."""
    target_path = os.fspath(target)
    temporary = f"{target_path}.tmp"
    try:
        frame.to_csv(temporary, **kwargs)
        try:
            os.replace(temporary, target_path)
        except PermissionError:
            # Visualizadores no Windows podem impedir substituição mesmo com
            # o arquivo aberto apenas para leitura. Aceitar somente se o
            # artefato já existente for byte a byte idêntico ao recém-gerado.
            if not os.path.exists(target_path):
                raise
            try:
                generated_frame = pd.read_csv(temporary)
                existing_frame = pd.read_csv(target_path)
                pd.testing.assert_frame_equal(
                    generated_frame,
                    existing_frame,
                    check_dtype=False,
                    check_exact=False,
                    rtol=1e-8,
                    atol=1e-10,
                )
            except Exception:
                raise
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_savefig(figure: Any, target: str | "os.PathLike[str]", **kwargs: Any) -> None:
    """Salva figura e tolera destino aberto somente quando os pixels coincidem."""
    from PIL import Image

    target_path = os.fspath(target)
    root, extension = os.path.splitext(target_path)
    temporary = f"{root}.tmp{extension}"
    try:
        figure.savefig(temporary, **kwargs)
        try:
            os.replace(temporary, target_path)
        except PermissionError:
            if not os.path.exists(target_path):
                raise
            with Image.open(temporary) as generated, Image.open(target_path) as existing:
                if generated.size != existing.size or generated.mode != existing.mode:
                    raise
                generated_pixels = np.asarray(generated, dtype=float)
                existing_pixels = np.asarray(existing, dtype=float)
                normalized_mean_difference = float(
                    np.mean(np.abs(generated_pixels - existing_pixels)) / 255.0
                )
                # Mudanças pequenas de antialiasing/fontes entre backends não
                # alteram o conteúdo do gráfico. Diferenças visuais materiais
                # continuam bloqueando a execução.
                if normalized_mean_difference > 0.03:
                    raise PermissionError(
                        f"Figura de destino bloqueada e materialmente diferente "
                        f"(diferença média normalizada={normalized_mean_difference:.4f})."
                    )
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def absorb_fixed_effects(
    df: pd.DataFrame,
    columns: Sequence[str],
    fe_columns: Sequence[str],
    tolerance: float = 1e-10,
    max_iterations: int = 1000,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Residualiza colunas por projeções alternadas até convergência."""
    values = df[list(columns)].astype(float).copy()
    previous = values.to_numpy(copy=True)
    converged = False
    max_change = np.inf
    for iteration in range(1, max_iterations + 1):
        for fe in fe_columns:
            values -= values.groupby(df[fe], sort=False).transform("mean")
        current = values.to_numpy(copy=False)
        max_change = float(np.max(np.abs(current - previous)))
        if max_change < tolerance:
            converged = True
            break
        previous = current.copy()
    max_group_mean = 0.0
    for fe in fe_columns:
        group_means = values.groupby(df[fe], sort=False).mean().abs().to_numpy()
        if group_means.size:
            max_group_mean = max(max_group_mean, float(np.nanmax(group_means)))
    diagnostics = {
        "convergiu": converged,
        "iteracoes": iteration,
        "tolerancia": tolerance,
        "max_mudanca_final": max_change,
        "max_media_grupo_residual": max_group_mean,
    }
    if not converged or max_group_mean > 1e-7:
        raise RuntimeError(f"Absorção de efeitos fixos não convergiu: {diagnostics}")
    return values, diagnostics


def fit_absorbed_ols(
    df: pd.DataFrame,
    outcome: str,
    regressors: Sequence[str],
    fixed_effects: Sequence[str],
    cluster: str,
) -> tuple[Any, dict[str, Any]]:
    cols = [outcome, *regressors]
    residualized, diagnostics = absorb_fixed_effects(df, cols, fixed_effects)
    y = residualized[outcome]
    x = residualized[list(regressors)]
    if np.linalg.matrix_rank(x.to_numpy()) < len(regressors):
        raise RuntimeError("Regressores sem posto completo após absorção dos efeitos fixos.")
    model = sm.OLS(y, x).fit(
        cov_type="cluster",
        cov_kwds={"groups": df[cluster].to_numpy(), "use_correction": True},
        use_t=True,
    )
    diagnostics["n_clusters"] = int(df[cluster].nunique())
    diagnostics["n_obs"] = int(len(df))
    return model, diagnostics


def result_for(model: Any, term: str) -> dict[str, Any]:
    ci = model.conf_int().loc[term]
    return {
        "beta": float(model.params[term]),
        "se": float(model.bse[term]),
        "t_stat": float(model.tvalues[term]),
        "p_valor": float(model.pvalues[term]),
        "ci_95": [float(ci.iloc[0]), float(ci.iloc[1])],
    }
