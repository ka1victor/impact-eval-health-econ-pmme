"""Gera descritivas de baseline e trajetória bruta da amostra confirmatória."""

from __future__ import annotations

import os
from pathlib import Path
import sys

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / ".matplotlib-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "scripts" / "utils"))
from theme_pmme import PMMEPalette, setup_editorial_theme, add_editorial_header, add_editorial_footer
from model_utils import atomic_savefig, atomic_to_csv


OUT = ROOT / "output" / "avaliacao_impacto"
PANEL = OUT / "dados" / "painel_municipio_curso_mes.parquet"
TABLES = OUT / "tabelas"
FIGURES = OUT / "figuras"


def smd(a: pd.Series, b: pd.Series) -> float:
    pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return float((a.mean() - b.mean()) / pooled) if pooled > 0 else 0.0


def main() -> None:
    setup_editorial_theme()
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PANEL)
    df = df[df["amostra_confirmatoria"] & df["within_muni_var_confirmatoria"]].copy()
    pre = df[df["competencia"] <= "202506"]
    baseline = (
        pre.groupby(["co_ibge_6d", "cod_curso"], as_index=False)
        .agg(
            immediate_ms=("immediate_ms", "first"),
            estoque_pre=("especialistas_mst", "mean"),
            cobertura_pre=("cobertura_binaria_mst", "mean"),
            qt_vagas_total=("qt_vagas_total", "first"),
            populacao_2010=("populacao_2010", "first"),
            ivs_2010=("ivs_2010", "first"),
        )
    )
    n_cells = int(baseline.shape[0])
    n_municipalities = int(baseline["co_ibge_6d"].nunique())
    variables = [
        ("Estoque médio pré", "estoque_pre"),
        ("Proporção de meses com cobertura pré", "cobertura_pre"),
        ("Vagas anunciadas na célula", "qt_vagas_total"),
        ("População municipal 2010", "populacao_2010"),
        ("IVS 2010", "ivs_2010"),
    ]
    rows = []
    for label, col in variables:
        a = baseline.loc[baseline["immediate_ms"] == 1, col].dropna()
        b = baseline.loc[baseline["immediate_ms"] == 0, col].dropna()
        rows.append(
            {
                "Variável": label,
                "Imediata média": a.mean(), "Imediata DP": a.std(),
                "Reserva média": b.mean(), "Reserva DP": b.std(),
                "Diferença bruta": a.mean() - b.mean(), "Diferença padronizada": smd(a, b),
                "N imediata": len(a), "N reserva": len(b),
            }
        )
    table = pd.DataFrame(rows)
    atomic_to_csv(table, TABLES / "tabela1_estatisticas_descritivas_baseline.csv", index=False, encoding="utf-8-sig")
    (TABLES / "tabela1_estatisticas_descritivas_baseline.md").write_text(
        "# Tabela 1 — Baseline da amostra confirmatória\n\n" + table.to_markdown(index=False, floatfmt=".3f") +
        "\n\nDiferenças são descritivas; a classificação imediata não foi aleatória.\n",
        encoding="utf-8",
    )
    (TABLES / "tabela1_estatisticas_descritivas_baseline.tex").write_text(table.to_latex(index=False), encoding="utf-8")

    trajectory = df.groupby(["competencia", "modalidade_ms"])["especialistas_mst"].mean().unstack()
    x = np.arange(len(trajectory))
    labels = [f"{m[:4]}-{m[4:]}" for m in trajectory.index]

    fig, ax = plt.subplots(figsize=(12.2, 5.8), dpi=300)

    transition = labels.index("2025-07")

    # Faixa de transição e pós-choque sombreada
    ax.axvspan(transition - 0.5, len(trajectory) - 0.5, color='#F0F7FF', alpha=0.75, zorder=0)
    ax.axvline(transition, color=PMMEPalette.ACCENT_CRIMSON, linestyle='--', linewidth=1.3, zorder=3)

    # Rótulo de publicação da oferta
    ax.text(transition + 0.35, 12.4, "Oferta Publicada\n(Jul/2025)", color=PMMEPalette.ACCENT_CRIMSON,
            fontsize=8.4, fontweight='bold', ha='left', va='top',
            bbox=dict(boxstyle='square,pad=0.25', facecolor='white', edgecolor='#FDA4AF', lw=0.8), zorder=5)

    # Inset badge explicando nível estrutural
    ax.text(3.5, 11.5,
            "Diferença pré-existente de nível:\n• Reserva: ~11 médicos/célula\n• Imediata: ~7 médicos/célula\n(Grupos administrativos não aleatórios)",
            fontsize=8.2, color='#334155', ha='left', va='center',
            bbox=dict(boxstyle='square,pad=0.35', facecolor='#F8FAFC', edgecolor='#CBD5E1', lw=0.8), zorder=5)

    # Curvas de trajetória com marcadores elegantes
    ax.plot(x, trajectory["IMEDIATA"], marker="o", color=PMMEPalette.ACCENT_BLUE, linewidth=2.2,
            markersize=5.2, markeredgecolor='white', markeredgewidth=0.8, label="Inicialmente imediata", zorder=4)
    ax.plot(x, trajectory["RESERVA"], marker="s", color=PMMEPalette.ACCENT_CRIMSON, linestyle="--", linewidth=2.0,
            markersize=5.2, markeredgecolor='white', markeredgewidth=0.8, label="Inicialmente em reserva", zorder=4)

    add_editorial_header(
        fig,
        title="Trajetórias Brutas do Estoque Cadastrado por Modalidade Inicial",
        subtitle=f"Comparação descritiva de {n_cells} células município-curso em {n_municipalities} municípios (CNES 2024–2026)",
        kicker="DESCRIÇÃO DA AMOSTRA IDENTIFICADORA",
        y_top=0.97
    )
    add_editorial_footer(
        fig,
        source="CNES / DATASUS e Ministério da Saúde (2024–2026)",
        notes="Não compara centros vs. interior nem participantes do PMM-E vs. não participantes. Grupos diferem em nível antes da oferta.",
        y_bottom=0.022
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8.5, fontweight='bold')
    ax.set_ylabel("Especialistas Distintos por Município-Curso", fontsize=9.2, labelpad=7)
    ax.set_ylim(6.2, 13.5)
    ax.set_xlim(-0.6, len(trajectory) - 0.4)
    ax.grid(True, axis='y')

    ax.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.95,
              edgecolor=PMMEPalette.LIGHT_GRAY, fontsize=8.8)

    fig.subplots_adjust(top=0.79, bottom=0.14, left=0.08, right=0.96)
    atomic_savefig(fig, FIGURES / "figura3_trajetoria_estoque_por_modalidade.png", dpi=300)
    plt.close(fig)
    print("[OK] Baseline e trajetória bruta gerados; figura editorial 3 gerada com sucesso.")


if __name__ == "__main__":
    main()
