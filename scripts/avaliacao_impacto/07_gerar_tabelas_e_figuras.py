"""Gera descritivas de baseline e trajetória bruta da amostra confirmatória."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / ".matplotlib-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model_utils import atomic_savefig, atomic_to_csv


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "avaliacao_impacto"
PANEL = OUT / "dados" / "painel_municipio_curso_mes.parquet"
TABLES = OUT / "tabelas"
FIGURES = OUT / "figuras"


def smd(a: pd.Series, b: pd.Series) -> float:
    pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return float((a.mean() - b.mean()) / pooled) if pooled > 0 else 0.0


def main() -> None:
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
    fig, ax = plt.subplots(figsize=(12, 6), dpi=200)
    ax.plot(x, trajectory["IMEDIATA"], marker="o", label="Imediata")
    ax.plot(x, trajectory["RESERVA"], marker="s", linestyle="--", label="Reserva")
    transition = labels.index("2025-07")
    ax.axvline(transition, color="#c44e52", linestyle=":", label="Oferta publicada")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Especialistas distintos por município-curso")
    ax.set_xlabel("Competência CNES")
    ax.set_title("Trajetória bruta — todos os CNES do município, amostra confirmatória")
    ax.legend()
    fig.tight_layout()
    atomic_savefig(fig, FIGURES / "figura3_trajetoria_estoque_por_modalidade.png")
    plt.close(fig)
    print("[OK] Baseline e trajetória bruta gerados.")


if __name__ == "__main__":
    main()
