"""Diagnósticos de local de alocação, amostra e placebo temporal."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / ".matplotlib-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model_utils import atomic_savefig, atomic_to_csv, fit_absorbed_ols, result_for


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "avaliacao_impacto"
DATA = OUT / "dados"
MODELS = OUT / "modelos"
TABLES = OUT / "tabelas"
FIGURES = OUT / "figuras"


def estimate(
    df: pd.DataFrame, outcome: str, treatment: str, cell: str, unit_month: str,
    cluster: str, label: str, group: str,
) -> dict[str, Any]:
    model, diag = fit_absorbed_ols(df, outcome, [treatment], [cell, unit_month, "course_month"], cluster)
    result = result_for(model, treatment)
    result.update(
        {
            "grupo_analise": group, "especificacao": label, "outcome": outcome,
            "n_obs": int(len(df)), "n_clusters": int(df[cluster].nunique()),
            "diagnosticos_numericos": diag,
        }
    )
    return result


def main() -> None:
    for directory in (MODELS, TABLES, FIGURES):
        directory.mkdir(parents=True, exist_ok=True)
    muni = pd.read_parquet(DATA / "painel_municipio_curso_mes.parquet")
    cnes = pd.read_parquet(DATA / "painel_cnes_curso_mes.parquet")
    reg = pd.read_parquet(DATA / "painel_regiao_curso_mes.parquet")

    muni = muni[muni["mes_transicao"] == 0].copy()
    muni["cell_id"] = muni["co_ibge_6d"].astype(str) + "_" + muni["cod_curso"].astype(str)
    muni["muni_month"] = muni["co_ibge_6d"].astype(str) + "_" + muni["competencia"].astype(str)
    muni["course_month"] = muni["cod_curso"].astype(str) + "_" + muni["competencia"].astype(str)
    confirm = muni[muni["amostra_confirmatoria"] & muni["within_muni_var_confirmatoria"]].copy()

    cnes = cnes[(cnes["mes_transicao"] == 0) & cnes["amostra_principal"] & cnes["curso_sem_sobreposicao"]].copy()
    variation = cnes.groupby("co_cnes_7d")["immediate_is"].nunique()
    cnes = cnes[cnes["co_cnes_7d"].isin(variation[variation > 1].index)].copy()
    cnes["treat_x_post"] = cnes["immediate_is"] * cnes["post_t"]
    cnes["cell_id"] = cnes["co_cnes_7d"].astype(str) + "_" + cnes["cod_curso"].astype(str)
    cnes["cnes_month"] = cnes["co_cnes_7d"].astype(str) + "_" + cnes["competencia"].astype(str)
    cnes["course_month"] = cnes["cod_curso"].astype(str) + "_" + cnes["competencia"].astype(str)

    results = [
        estimate(
            confirm, "especialistas_mst", "treat_x_post", "cell_id", "muni_month", "co_ibge_6d",
            "Município completo (principal)", "Escala geográfica",
        ),
        estimate(
            cnes, "especialistas_ist", "treat_x_post", "cell_id", "cnes_month", "co_cnes_7d",
            "Estabelecimento ofertante (diagnóstico)", "Escala geográfica",
        ),
    ]

    top = confirm.drop_duplicates(["co_ibge_6d", "cod_curso"]).groupby("co_ibge_6d")["qt_vagas_total"].sum().nlargest(3).index
    no_top = confirm[~confirm["co_ibge_6d"].isin(top)].copy()
    results.append(
        estimate(
            no_top, "especialistas_mst", "treat_x_post", "cell_id", "muni_month", "co_ibge_6d",
            "Principal sem os 3 municípios com mais vagas", "Sensibilidade amostral",
        )
    )

    placebo = confirm[confirm["competencia"] <= "202506"].copy()
    placebo["placebo_post"] = (placebo["competencia"] >= "202501").astype(int)
    placebo["treat_x_placebo"] = placebo["immediate_ms"] * placebo["placebo_post"]
    results.append(
        estimate(
            placebo, "especialistas_mst", "treat_x_placebo", "cell_id", "muni_month", "co_ibge_6d",
            "Placebo: falso início em 2025-01 usando apenas o pré", "Placebo temporal",
        )
    )

    region_summary = {
        "status": "DESCRITIVO_NAO_CAUSAL",
        "regioes": int(reg["region_id"].nunique()),
        "celulas_regiao_curso": int(reg[["region_id", "cod_curso"]].drop_duplicates().shape[0]),
        "motivo": "A exposição é municipal e pode gerar interferência; reclassificar região como tratada por qualquer vaga mudaria o estimando.",
    }
    payload = {"modelos": results, "diagnostico_regional": region_summary}
    with (MODELS / "resultados_robustez_e_redistribuicao.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    table = pd.DataFrame(
        [
            {
                "Grupo": r["grupo_analise"], "Especificação": r["especificacao"], "Beta": r["beta"],
                "Erro-padrão": r["se"], "IC 95% inferior": r["ci_95"][0], "IC 95% superior": r["ci_95"][1],
                "P-valor": r["p_valor"], "N": r["n_obs"], "Clusters": r["n_clusters"],
            }
            for r in results
        ]
    )
    atomic_to_csv(table, TABLES / "tabela4_diagnosticos_robustez_e_redistribuicao.csv", index=False, encoding="utf-8-sig")
    (TABLES / "tabela4_diagnosticos_robustez_e_redistribuicao.md").write_text(
        "# Tabela 4 — Diagnósticos e sensibilidades\n\n" + table.to_markdown(index=False, floatfmt=".4f") +
        "\n\nO painel regional é descritivo; não identifica spillovers causais.\n",
        encoding="utf-8",
    )
    (TABLES / "tabela4_diagnosticos_robustez_e_redistribuicao.tex").write_text(table.to_latex(index=False), encoding="utf-8")

    geo = [r for r in results if r["grupo_analise"] == "Escala geográfica"]
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=200)
    y = np.arange(len(geo))
    beta = np.array([r["beta"] for r in geo])
    low = np.array([r["ci_95"][0] for r in geo])
    high = np.array([r["ci_95"][1] for r in geo])
    ax.axvline(0, color="black", linestyle="--")
    ax.errorbar(beta, y, xerr=[beta - low, high - beta], fmt="o", capsize=4)
    ax.set_yticks(y)
    ax.set_yticklabels([r["especificacao"] for r in geo])
    ax.set_xlabel("Diferença estimada no estoque")
    ax.set_title("Município completo versus estabelecimento ofertante")
    fig.tight_layout()
    atomic_savefig(fig, FIGURES / "figura2_diagnostico_redistribuicao.png")
    plt.close(fig)
    print("[OK] Robustez concluída; região preservada como diagnóstico descritivo.")


if __name__ == "__main__":
    main()
