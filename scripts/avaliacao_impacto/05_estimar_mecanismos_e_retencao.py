"""Estima fluxos maduros e descreve presença seis meses após a entrada."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / ".matplotlib-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from model_utils import atomic_savefig, atomic_to_csv, fit_absorbed_ols, result_for


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "avaliacao_impacto"
PANEL = OUT / "dados" / "painel_municipio_curso_mes.parquet"
MODELS = OUT / "modelos"
TABLES = OUT / "tabelas"
FIGURES = OUT / "figuras"


def estimate(df: pd.DataFrame, outcome: str, label: str) -> dict[str, Any]:
    usable = df[df[outcome].notna() & ~df["mes_transicao"]].copy()
    model, diag = fit_absorbed_ols(
        usable, outcome, ["treat_x_post"], ["cell_id", "muni_month", "course_month"], "co_ibge_6d"
    )
    result = result_for(model, "treat_x_post")
    result.update(
        {
            "mecanismo": label,
            "outcome": outcome,
            "n_obs": int(len(usable)),
            "n_clusters": int(usable["co_ibge_6d"].nunique()),
            "primeira_competencia_observavel": str(usable["competencia"].min()),
            "ultima_competencia_observavel": str(usable["competencia"].max()),
            "diagnosticos_numericos": diag,
        }
    )
    return result


def main() -> None:
    for directory in (MODELS, TABLES, FIGURES):
        directory.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PANEL)
    df = df[df["amostra_confirmatoria"] & df["within_muni_var_confirmatoria"]].copy()
    df["cell_id"] = df["co_ibge_6d"].astype(str) + "_" + df["cod_curso"].astype(str)
    df["muni_month"] = df["co_ibge_6d"].astype(str) + "_" + df["competencia"].astype(str)
    df["course_month"] = df["cod_curso"].astype(str) + "_" + df["competencia"].astype(str)

    mechanisms = [
        estimate(df, "n_entradas_6m", "Entradas após seis meses de ausência"),
        estimate(df, "n_saidas_confirmadas_3m", "Saídas confirmadas por três meses posteriores"),
        estimate(df, "saldo_liquido", "Saldo líquido nas competências com ambas as margens observáveis"),
        estimate(df, "churn_bruto", "Churn bruto nas competências com ambas as margens observáveis"),
    ]

    cohorts = df[
        df["competencia"].between("202508", "202601")
        & df["coorte_6m_madura"]
        & df["entrantes_elegiveis_6m"].notna()
    ].copy()
    retention: dict[str, Any] = {}
    for treatment, label in ((1, "imediata"), (0, "reserva")):
        part = cohorts[cohorts["immediate_ms"] == treatment]
        entrants = float(part["entrantes_elegiveis_6m"].sum())
        present = float(part["entrantes_presentes_6m"].sum())
        retention[label] = {
            "entrantes_elegiveis": entrants,
            "presentes_6m": present,
            "taxa_presenca_6m_pct": 100 * present / entrants if entrants else None,
        }
    retention["diferenca_pp_descritiva"] = (
        retention["imediata"]["taxa_presenca_6m_pct"] - retention["reserva"]["taxa_presenca_6m_pct"]
        if retention["imediata"]["taxa_presenca_6m_pct"] is not None and retention["reserva"]["taxa_presenca_6m_pct"] is not None
        else None
    )
    result = {
        "amostra": "confirmatória, cursos sem CBO compartilhado",
        "mecanismos_ddd": mechanisms,
        "presenca_6m_descritiva": {
            "coortes_entrada": "2025-08 a 2026-01",
            "definicao": "entrante após seis meses de ausência ainda observado no mesmo município-curso em t+6",
            "nota": "A taxa é descritiva porque condiciona em entrada, que pode ser afetada pelo tratamento.",
            **retention,
        },
        "presenca_12m": {"status": "CENSURADA", "requisito": "CNES até 2027-01 para a coorte encerrada em 2026-01"},
    }
    with (MODELS / "resultados_mecanismos_fluxos.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    rows = []
    for r in mechanisms:
        rows.append(
            {
                "Mecanismo": r["mecanismo"], "Beta DDD": r["beta"], "Erro-padrão": r["se"],
                "IC 95% inferior": r["ci_95"][0], "IC 95% superior": r["ci_95"][1],
                "P-valor": r["p_valor"], "Primeiro mês": r["primeira_competencia_observavel"],
                "Último mês": r["ultima_competencia_observavel"], "N": r["n_obs"], "Clusters": r["n_clusters"],
            }
        )
    rows.append(
        {
            "Mecanismo": "Presença aos 6 meses (descritiva; diferença p.p.)",
            "Beta DDD": retention["diferenca_pp_descritiva"], "Erro-padrão": None,
            "IC 95% inferior": None, "IC 95% superior": None, "P-valor": None,
            "Primeiro mês": "202508", "Último mês": "202601", "N": len(cohorts), "Clusters": cohorts["co_ibge_6d"].nunique(),
        }
    )
    table = pd.DataFrame(rows)
    atomic_to_csv(table, TABLES / "tabela3_mecanismos_fluxos_e_retencao.csv", index=False, encoding="utf-8-sig")
    (TABLES / "tabela3_mecanismos_fluxos_e_retencao.md").write_text(
        "# Tabela 3 — Fluxos e presença posterior\n\n" + table.to_markdown(index=False, floatfmt=".4f") + "\n",
        encoding="utf-8",
    )
    (TABLES / "tabela3_mecanismos_fluxos_e_retencao.tex").write_text(table.to_latex(index=False), encoding="utf-8")

    means = (
        df.groupby(["competencia", "modalidade_ms"], as_index=False)
        .agg(entradas=("n_entradas_6m", "mean"), saidas=("n_saidas_confirmadas_3m", "mean"))
    )
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=200, sharey=True)
    for ax, modality in zip(axes, ["IMEDIATA", "RESERVA"], strict=True):
        part = means[means["modalidade_ms"] == modality]
        ax.plot(part["competencia"], part["entradas"], label="Entradas (6 meses prévios)")
        ax.plot(part["competencia"], part["saidas"], label="Saídas (3 meses posteriores)")
        ax.set_title(modality.title())
        ax.tick_params(axis="x", rotation=60)
        ax.legend()
    fig.suptitle("Fluxos mensais com janelas longitudinais maduras")
    fig.tight_layout()
    atomic_savefig(fig, FIGURES / "figura4_decomposicao_mecanismos_fluxos.png")
    plt.close(fig)
    print("[OK] Mecanismos estimados com censura explícita; presença em 6 meses mantida descritiva.")


if __name__ == "__main__":
    main()
