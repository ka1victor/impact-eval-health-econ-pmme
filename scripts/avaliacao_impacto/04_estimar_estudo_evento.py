"""Estudo de evento DDD na amostra confirmatória."""

from __future__ import annotations

import json
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
from model_utils import atomic_savefig, atomic_to_csv, fit_absorbed_ols, result_for


OUT = ROOT / "output" / "avaliacao_impacto"
PANEL = OUT / "dados" / "painel_municipio_curso_mes.parquet"
MODELS = OUT / "modelos"
TABLES = OUT / "tabelas"
FIGURES = OUT / "figuras"
REF = "202506"


def main() -> None:
    setup_editorial_theme()
    for directory in (MODELS, TABLES, FIGURES):
        directory.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PANEL)
    df = df[df["amostra_confirmatoria"] & df["within_muni_var_confirmatoria"]].copy()
    months = sorted(df["competencia"].astype(str).unique())
    df["cell_id"] = df["co_ibge_6d"].astype(str) + "_" + df["cod_curso"].astype(str)
    df["muni_month"] = df["co_ibge_6d"].astype(str) + "_" + df["competencia"].astype(str)
    df["course_month"] = df["cod_curso"].astype(str) + "_" + df["competencia"].astype(str)
    n_cells = int(df[["co_ibge_6d", "cod_curso"]].drop_duplicates().shape[0])
    n_municipalities = int(df["co_ibge_6d"].nunique())
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
        "n_celulas_municipio_curso": n_cells,
        "n_municipios": n_municipalities,
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
    fig, ax = plt.subplots(figsize=(12.2, 5.8), dpi=300)

    transition = int(event.index[event["competencia"] == "202507"][0])

    # Faixa de tratamento sombreada pós-choque
    ax.axvspan(transition - 0.5, len(event) - 0.5, color='#F0F7FF', alpha=0.75, zorder=0)
    ax.axhline(0, color=PMMEPalette.PRIMARY_NAVY, linestyle='-', linewidth=0.85, alpha=0.7, zorder=2)
    ax.axvline(transition, color=PMMEPalette.ACCENT_CRIMSON, linestyle='--', linewidth=1.3, zorder=3)

    # Rótulo de publicação da oferta
    ax.text(transition + 0.35, 0.82, "Publicação da Oferta\n(Jul/2025 = 0)", color=PMMEPalette.ACCENT_CRIMSON,
            fontsize=8.4, fontweight='bold', ha='left', va='top',
            bbox=dict(boxstyle='square,pad=0.25', facecolor='white', edgecolor='#FDA4AF', lw=0.8), zorder=5)

    # Badge diagnóstico de pré-tendências no topo esquerdo com margem segura
    ax.text(3.2, 0.82, f"Coeficientes pré conjuntamente nulos:\nF = {f_stat:.3f} (p = {f_p:.4f})\nNão rejeição não prova paralelismo",
            fontsize=8.2, color='#334155', ha='center', va='top',
            bbox=dict(boxstyle='square,pad=0.35', facecolor='#F8FAFC', edgecolor='#CBD5E1', lw=0.8), zorder=5)

    # Estudo de evento com marcadores elegantes e intervalos 95%
    ax.errorbar(
        x, event["beta"],
        yerr=[event["beta"] - event["ci_95_inferior"], event["ci_95_superior"] - event["beta"]],
        fmt="o", color=PMMEPalette.ACCENT_BLUE, ecolor='#3B82F6', elinewidth=1.2, capsize=3.5, capthick=1.1,
        markersize=5.2, markeredgecolor='white', markeredgewidth=0.9, label="Diferença DDD ajustada (IC 95%)", zorder=4
    )

    add_editorial_header(
        fig,
        title="Comparação DDD: Vagas Inicialmente Imediatas vs. Cadastro de Reserva",
        subtitle=f"Diferenças ajustadas no estoque CNES; {n_cells} células em {n_municipalities} municípios (N = {len(df):,})".replace(",", "."),
        kicker="DIAGNÓSTICO AJUSTADO DE IMPLEMENTAÇÃO",
        y_top=0.97
    )
    add_editorial_footer(
        fig,
        source="Ministério da Saúde (SGTES / PMM-E) e CNES / DATASUS (2024–2026)",
        notes="Associação, não causal. Efeitos fixos município-curso, município-mês e curso-mês; erros agrupados por município.",
        y_bottom=0.020
    )

    ax.set_xticks(x)
    labels = [f"{m[:4]}-{m[4:]}" for m in event["competencia"]]
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8.5, fontweight='bold')
    ax.set_ylabel("Diferença Ajustada no Estoque de Especialistas", fontsize=9.2, labelpad=7)
    ax.set_ylim(-2.35, 1.15)
    ax.set_xlim(-0.6, len(event) - 0.4)
    ax.grid(True, axis='y')

    ax.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.95,
              edgecolor=PMMEPalette.LIGHT_GRAY, fontsize=8.8)

    fig.subplots_adjust(top=0.79, bottom=0.14, left=0.08, right=0.96)
    atomic_savefig(fig, FIGURES / "figura1_estudo_evento_ddd_dinamico.png", dpi=300)
    plt.close(fig)
    print(f"[OK] Pré-tendências: F={f_stat:.3f}, p={f_p:.4f}; figura editorial 1 gerada com sucesso.")


if __name__ == "__main__":
    main()
