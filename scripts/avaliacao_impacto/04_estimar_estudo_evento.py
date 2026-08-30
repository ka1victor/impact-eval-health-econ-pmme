"""Estudo de evento DDD na amostra confirmatória."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / ".matplotlib-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model_utils import atomic_savefig, atomic_to_csv, fit_absorbed_ols, result_for


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "avaliacao_impacto"
PANEL = OUT / "dados" / "painel_municipio_curso_mes.parquet"
MODELS = OUT / "modelos"
TABLES = OUT / "tabelas"
FIGURES = OUT / "figuras"
REF = "202506"


def main() -> None:
    for directory in (MODELS, TABLES, FIGURES):
        directory.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PANEL)
    df = df[df["amostra_confirmatoria"] & df["within_muni_var_confirmatoria"]].copy()
    months = sorted(df["competencia"].astype(str).unique())
    df["cell_id"] = df["co_ibge_6d"].astype(str) + "_" + df["cod_curso"].astype(str)
    df["muni_month"] = df["co_ibge_6d"].astype(str) + "_" + df["competencia"].astype(str)
    df["course_month"] = df["cod_curso"].astype(str) + "_" + df["competencia"].astype(str)
    terms = []
    for month in months:
        if month == REF:
            continue
        term = f"event_{month}"
        df[term] = df["immediate_ms"] * (df["competencia"] == month).astype(int)
        terms.append(term)
    model, diagnostics = fit_absorbed_ols(
        df, "especialistas_mst", terms, ["cell_id", "muni_month", "course_month"], "co_ibge_6d"
    )

    rows = []
    for month in months:
        if month == REF:
            r = {"beta": 0.0, "se": 0.0, "t_stat": 0.0, "p_valor": 1.0, "ci_95": [0.0, 0.0]}
        else:
            r = result_for(model, f"event_{month}")
        rows.append(
            {
                "competencia": month,
                "fase": "PRE" if month < "202507" else ("TRANSICAO" if month == "202507" else "POS"),
                "beta": r["beta"],
                "se": r["se"],
                "t_stat": r["t_stat"],
                "p_valor": r["p_valor"],
                "ci_95_inferior": r["ci_95"][0],
                "ci_95_superior": r["ci_95"][1],
                "referencia": month == REF,
            }
        )
    event = pd.DataFrame(rows)
    pre_terms = [f"event_{m}" for m in months if m < "202507" and m != REF]
    restriction = np.zeros((len(pre_terms), len(terms)))
    for i, term in enumerate(pre_terms):
        restriction[i, terms.index(term)] = 1
    ftest = model.f_test(restriction)
    f_stat = float(np.asarray(ftest.fvalue).item())
    f_p = float(np.asarray(ftest.pvalue).item())
    pre = event[(event["fase"] == "PRE") & ~event["referencia"]]
    max_abs_pre = float(pre["beta"].abs().max())
    max_ci_bound = float(pd.concat([pre["ci_95_inferior"].abs(), pre["ci_95_superior"].abs()]).max())

    result = {
        "mes_referencia": REF,
        "n_obs": int(len(df)),
        "n_clusters": int(df["co_ibge_6d"].nunique()),
        "diagnosticos_numericos": diagnostics,
        "wald_pre_tendencias": {
            "estatistica_f": f_stat,
            "graus_liberdade_numerador": len(pre_terms),
            "graus_liberdade_denominador": int(df["co_ibge_6d"].nunique() - 1),
            "p_valor": f_p,
            "max_abs_beta_pre": max_abs_pre,
            "max_abs_limite_ic95_pre": max_ci_bound,
            "interpretacao": "Não rejeitar coeficientes pré iguais a zero não prova paralelismo; magnitude e intervalos também devem ser avaliados.",
        },
        "coeficientes_dinamicos": rows,
    }
    with (MODELS / "resultados_estudo_evento.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    atomic_to_csv(event, TABLES / "tabela_estudo_evento_dinamico.csv", index=False, encoding="utf-8-sig")

    x = np.arange(len(event))
    fig, ax = plt.subplots(figsize=(12, 6), dpi=200)
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    transition = int(event.index[event["competencia"] == "202507"][0])
    ax.axvline(transition, color="#c44e52", linestyle=":", label="Oferta publicada (2025-07)")
    ax.errorbar(
        x, event["beta"],
        yerr=[event["beta"] - event["ci_95_inferior"], event["ci_95_superior"] - event["beta"]],
        fmt="o", color="#1f77b4", capsize=3, label="DDD dinâmica e IC 95%",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(event["competencia"].str[:4] + "-" + event["competencia"].str[4:], rotation=45, ha="right")
    ax.set_ylabel("Diferença estimada no estoque de especialistas")
    ax.set_xlabel("Competência CNES")
    ax.set_title("Estudo de evento — amostra confirmatória sem CBO compartilhado")
    ax.legend()
    fig.tight_layout()
    atomic_savefig(fig, FIGURES / "figura1_estudo_evento_ddd_dinamico.png")
    plt.close(fig)
    print(f"[OK] Pré-tendências: F={f_stat:.3f}, p={f_p:.4f}; interpretação não automática.")


if __name__ == "__main__":
    main()
