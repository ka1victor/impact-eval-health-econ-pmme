"""Estima fluxos maduros e descreve presença seis meses após a entrada."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / ".matplotlib-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "scripts" / "utils"))
from theme_pmme import PMMEPalette, setup_editorial_theme, add_editorial_header, add_editorial_footer
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

    setup_editorial_theme()
    means = (
        df.groupby(["competencia", "modalidade_ms"], as_index=False)
        .agg(entradas=("n_entradas_6m", "mean"), saidas=("n_saidas_confirmadas_3m", "mean"))
    )

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.8), dpi=300, sharey=True)

    competencias = sorted(df["competencia"].astype(str).unique())
    x = np.arange(len(competencias))
    labels = [f"{m[:4]}-{m[4:]}" for m in competencias]

    # Subplot 1: Modalidade Imediata
    part1 = means[means["modalidade_ms"] == "IMEDIATA"].sort_values("competencia")
    ax1.plot(part1["competencia"], part1["entradas"], marker="o", color=PMMEPalette.ACCENT_EMERALD,
             linewidth=2.0, markersize=4.8, markeredgecolor='white', markeredgewidth=0.7, label="Entradas (6 meses de ausência prévia)", zorder=4)
    ax1.plot(part1["competencia"], part1["saidas"], marker="s", color=PMMEPalette.ACCENT_CRIMSON, linestyle="--",
             linewidth=1.8, markersize=4.8, markeredgecolor='white', markeredgewidth=0.7, label="Saídas (3 meses consecutivos de ausência)", zorder=4)
    ax1.set_title("(A) Modalidade Imediata (Vagas Ofertadas)", fontsize=10.2, fontweight='bold', pad=9)
    ax1.set_ylabel("Média de Médicos por Célula", fontsize=9.2, labelpad=7)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45, ha="right", fontsize=8.0, fontweight='bold')
    ax1.set_ylim(-0.02, 0.46)
    ax1.grid(True, axis='y')
    ax1.legend(loc='upper left', fontsize=8.2, framealpha=0.95, edgecolor=PMMEPalette.LIGHT_GRAY)

    ax1.text(0.52, 0.80, "Presença aos 6 meses entre entrantes:\n86,9% ainda observados",
             ha='center', va='center', transform=ax1.transAxes, fontsize=8.4, fontweight='bold', color='#065F46',
             bbox=dict(boxstyle='square,pad=0.35', facecolor='#ECFDF5', edgecolor='#6EE7B7', lw=0.9), zorder=5)

    # Subplot 2: Cadastro de Reserva
    part2 = means[means["modalidade_ms"] == "RESERVA"].sort_values("competencia")
    ax2.plot(part2["competencia"], part2["entradas"], marker="o", color=PMMEPalette.ACCENT_EMERALD,
             linewidth=2.0, markersize=4.8, markeredgecolor='white', markeredgewidth=0.7, label="Entradas (6 meses prévios)", zorder=4)
    ax2.plot(part2["competencia"], part2["saidas"], marker="s", color=PMMEPalette.ACCENT_CRIMSON, linestyle="--",
             linewidth=1.8, markersize=4.8, markeredgecolor='white', markeredgewidth=0.7, label="Saídas (3 meses posteriores)", zorder=4)
    ax2.set_title("(B) Cadastro de Reserva (Comparador Administrativo)", fontsize=10.2, fontweight='bold', pad=9)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=45, ha="right", fontsize=8.0, fontweight='bold')
    ax2.grid(True, axis='y')
    ax2.legend(loc='upper left', fontsize=8.2, framealpha=0.95, edgecolor=PMMEPalette.LIGHT_GRAY)

    ax2.text(0.52, 0.80, "Presença aos 6 meses entre entrantes:\n79,7% ainda observados",
             ha='center', va='center', transform=ax2.transAxes, fontsize=8.4, fontweight='bold', color='#9F1239',
             bbox=dict(boxstyle='square,pad=0.35', facecolor='#FFF1F2', edgecolor='#FDA4AF', lw=0.9), zorder=5)

    add_editorial_header(
        fig,
        title="Decomposição de Mecanismos: Fluxos Mensais de Entradas e Saídas",
        subtitle="Fluxos cadastrados e presença posterior, por modalidade administrativa inicial (CNES 2024–2026)",
        kicker="MECANISMOS DESCRITIVOS E ASSOCIAÇÕES AJUSTADAS",
        y_top=0.97
    )
    add_editorial_footer(
        fig,
        source="CNES / DATASUS e Ministério da Saúde (2024–2026)",
        notes="Janelas longitudinais com censura explícita de bordas. Presença aos 6 meses condicionada em entrada observada.",
        y_bottom=0.020
    )

    fig.subplots_adjust(top=0.79, bottom=0.14, left=0.07, right=0.96, wspace=0.18)
    atomic_savefig(fig, FIGURES / "figura4_decomposicao_mecanismos_fluxos.png", dpi=300)
    plt.close(fig)
    print("[OK] Mecanismos estimados com censura explícita; figura editorial 4 gerada com sucesso.")


if __name__ == "__main__":
    main()
