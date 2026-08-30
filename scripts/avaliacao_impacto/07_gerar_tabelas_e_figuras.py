"""07_gerar_tabelas_e_figuras.py — Geração Consolidada da Tabela 1 (Baseline) e Figuras Analíticas.

Este script produz:
1. Tabela 1: Estatísticas Descritivas e Balanço de Baseline (Pré-Tratamento: 2024-06 a 2025-06);
2. Figura 3: Trajetória Temporal do Estoque de Especialistas por Modalidade (2024-06 a 2026-07);
3. Figura 4: Decomposição de Fluxos Mensais (Entradas, Saídas e Saldo Líquido).

Entregáveis:
- output/avaliacao_impacto/tabelas/tabela1_estatisticas_descritivas_baseline.csv
- output/avaliacao_impacto/tabelas/tabela1_estatisticas_descritivas_baseline.md
- output/avaliacao_impacto/tabelas/tabela1_estatisticas_descritivas_baseline.tex
- output/avaliacao_impacto/figuras/figura3_trajetoria_estoque_por_modalidade.png
- output/avaliacao_impacto/figuras/figura4_decomposicao_mecanismos_fluxos.png
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output" / "avaliacao_impacto"
DADOS_DIR = OUTPUT_DIR / "dados"
TABELAS_DIR = OUTPUT_DIR / "tabelas"
FIGURAS_DIR = OUTPUT_DIR / "figuras"

PAINEL_MUNI_FILE = DADOS_DIR / "painel_municipio_curso_mes.parquet"


def main() -> None:
    print("=== [Etapa 7] Geração da Tabela 1 (Baseline) e Figuras Analíticas ===")
    TABELAS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    df_muni = pd.read_parquet(PAINEL_MUNI_FILE)
    df_main = df_muni[df_muni["amostra_principal"]].copy()

    # 1. Construção da Tabela 1: Balanço de Baseline (Pré-tratamento: 2024-06 a 2025-06)
    print("Construindo Tabela 1: Estatísticas Descritivas e Balanço de Baseline...")
    df_pre = df_main[df_main["post_t"] == 0].copy()

    # Agregar ao nível de célula no baseline
    cell_baseline = df_pre.groupby(["co_ibge_6d", "cod_curso"]).agg({
        "immediate_ms": "first",
        "modalidade_ms": "first",
        "especialistas_mst": "mean",
        "cobertura_binaria_mst": "mean",
        "fte_total": "mean",
        "fte_ambulatorial_total": "mean",
        "fte_hospitalar_total": "mean",
        "qt_vagas_imediatas": "first",
        "qt_vagas_reserva": "first",
        "qt_vagas_total": "first",
        "populacao_2010": "first",
        "ivs_2010": "first",
        "idhm_2010": "first",
        "rdpc_2010": "first",
    }).reset_index()

    imed_cells = cell_baseline[cell_baseline["immediate_ms"] == 1]
    res_cells = cell_baseline[cell_baseline["immediate_ms"] == 0]

    vars_baseline = [
        ("Estoque Pré-Tratamento de Especialistas (Médicos)", "especialistas_mst"),
        ("Taxa de Cobertura Pré-Tratamento (>=1 Médico)", "cobertura_binaria_mst"),
        ("Carga Horária Semanal Total (Horas/Semana)", "fte_total"),
        ("Carga Horária Ambulatorial (Horas/Semana)", "fte_ambulatorial_total"),
        ("Carga Horária Hospitalar (Horas/Semana)", "fte_hospitalar_total"),
        ("Total de Vagas PMM-E Anunciadas na Célula", "qt_vagas_total"),
        ("População Municipal (Censo 2010)", "populacao_2010"),
        ("Índice de Vulnerabilidade Social (IVS IPEA 2010)", "ivs_2010"),
        ("IDHM Municipal (2010)", "idhm_2010"),
        ("Renda Domiciliar Per Capita (R$ 2010)", "rdpc_2010"),
    ]

    tabela1_rows = []
    for label, col in vars_baseline:
        v_imed = imed_cells[col].dropna()
        v_res = res_cells[col].dropna()

        m_imed = float(v_imed.mean())
        sd_imed = float(v_imed.std())
        m_res = float(v_res.mean())
        sd_res = float(v_res.std())

        diff = m_imed - m_res
        t_res = stats.ttest_ind(v_imed, v_res, equal_var=False)

        stars = ""
        p = float(t_res.pvalue)
        if p < 0.01:
            stars = "***"
        elif p < 0.05:
            stars = "**"
        elif p < 0.10:
            stars = "*"

        tabela1_rows.append({
            "Variável de Caracterização": label,
            "Vagas Imediatas (Média)": f"{m_imed:.2f}",
            "Vagas Imediatas (DP)": f"({sd_imed:.2f})",
            "Cadastro Reserva (Média)": f"{m_res:.2f}",
            "Cadastro Reserva (DP)": f"({sd_res:.2f})",
            "Diferença": f"{diff:+.2f}{stars}",
            "P-valor": f"{p:.4f}",
        })

    df_tab1 = pd.DataFrame(tabela1_rows)

    out_csv1 = TABELAS_DIR / "tabela1_estatisticas_descritivas_baseline.csv"
    out_md1 = TABELAS_DIR / "tabela1_estatisticas_descritivas_baseline.md"
    out_tex1 = TABELAS_DIR / "tabela1_estatisticas_descritivas_baseline.tex"

    df_tab1.to_csv(out_csv1, index=False, encoding="utf-8-sig")

    with out_md1.open("w", encoding="utf-8") as f:
        f.write("# Tabela 1 — Estatísticas Descritivas e Balanço de Baseline (Pré-Tratamento: 2024-06 a 2025-06)\n\n")
        f.write(df_tab1.to_markdown(index=False))
        f.write(f"\n\n*Notas: Médias e desvios-padrão (DP) calculados sobre 1.172 células município-curso na amostra principal (463 imediatas e 709 reserva) no período pré-tratamento de 13 meses. *** p<0.01, ** p<0.05, * p<0.10.*\n")

    with out_tex1.open("w", encoding="utf-8") as f:
        f.write(df_tab1.to_latex(index=False, caption="Estatísticas Descritivas e Balanço de Baseline — PMM-E Ciclo 1", label="tab:baseline_balance"))

    print(f"[OK] Tabela 1 salva em: {out_csv1}")

    # 2. Gerar Figura 3: Trajetória Temporal do Estoque
    print("Gerando Figura 3: Trajetória Temporal do Estoque...")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)

    ts = df_main.groupby(["competencia", "modalidade_ms"])["especialistas_mst"].mean().unstack()
    comps = ts.index.tolist()
    labels = [f"{c[:4]}-{c[4:]}" for c in comps]
    x = np.arange(len(labels))

    ax.plot(x, ts["IMEDIATA"].values, marker="o", linewidth=2.2, color="#0275d8", label="Vagas Imediatas (Tratamento Inicial)")
    ax.plot(x, ts["RESERVA"].values, marker="s", linewidth=2.2, color="#f0ad4e", linestyle="--", label="Cadastro de Reserva (Comparação Inicial)")

    # Linha vertical do anúncio (2025-07)
    trans_idx = labels.index("2025-07")
    ax.axvline(trans_idx, color="#d9534f", linestyle=":", linewidth=1.5, label="Anúncio Ciclo 1 Chamada 1 (2025-07)")
    ax.axvspan(trans_idx + 0.5, len(x) - 0.5, color="#f0f8ff", alpha=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Média de Médicos Especialistas por Célula", fontsize=11, fontweight="bold")
    ax.set_xlabel("Competência Mensal", fontsize=11, fontweight="bold")
    ax.set_title("Evolução Temporal do Estoque Médio de Especialistas por Célula Município-Curso (2024-06 a 2026-07)", fontsize=12, fontweight="bold", pad=15)
    ax.legend(loc="upper left", frameon=True, framealpha=0.9)

    plt.tight_layout()
    out_fig3 = FIGURAS_DIR / "figura3_trajetoria_estoque_por_modalidade.png"
    fig.savefig(out_fig3, dpi=300)
    plt.close(fig)
    print(f"[OK] Figura 3 salva em: {out_fig3}")

    # 3. Gerar Figura 4: Decomposição de Fluxos (Entradas, Saídas e Saldo)
    print("Gerando Figura 4: Decomposição de Fluxos...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=300, sharey=True)

    fluxos_imed = df_main[df_main["modalidade_ms"] == "IMEDIATA"].groupby("competencia")[["n_entradas", "n_saidas", "saldo_liquido"]].mean()
    fluxos_res = df_main[df_main["modalidade_ms"] == "RESERVA"].groupby("competencia")[["n_entradas", "n_saidas", "saldo_liquido"]].mean()

    ax1.plot(x, fluxos_imed["n_entradas"], label="Entradas (Inflows)", color="#5cb85c", linewidth=2)
    ax1.plot(x, fluxos_imed["n_saidas"], label="Saídas (Outflows)", color="#d9534f", linewidth=2, linestyle="--")
    ax1.plot(x, fluxos_imed["saldo_liquido"], label="Saldo Líquido", color="#0275d8", linewidth=2.5)
    ax1.axvline(trans_idx, color="black", linestyle=":", linewidth=1)
    ax1.set_xticks(x[::2])
    ax1.set_xticklabels(labels[::2], rotation=45, ha="right")
    ax1.set_title("Vagas Imediatas", fontweight="bold")
    ax1.set_ylabel("Média de Médicos por Célula", fontweight="bold")
    ax1.legend(loc="upper left")

    ax2.plot(x, fluxos_res["n_entradas"], label="Entradas (Inflows)", color="#5cb85c", linewidth=2)
    ax2.plot(x, fluxos_res["n_saidas"], label="Saídas (Outflows)", color="#d9534f", linewidth=2, linestyle="--")
    ax2.plot(x, fluxos_res["saldo_liquido"], label="Saldo Líquido", color="#0275d8", linewidth=2.5)
    ax2.axvline(trans_idx, color="black", linestyle=":", linewidth=1)
    ax2.set_xticks(x[::2])
    ax2.set_xticklabels(labels[::2], rotation=45, ha="right")
    ax2.set_title("Cadastro de Reserva", fontweight="bold")
    ax2.legend(loc="upper left")

    fig.suptitle("Decomposição Dinâmica de Fluxos: Entradas, Saídas e Saldo Líquido Mensal", fontsize=12, fontweight="bold")
    plt.tight_layout()
    out_fig4 = FIGURAS_DIR / "figura4_decomposicao_mecanismos_fluxos.png"
    fig.savefig(out_fig4, dpi=300)
    plt.close(fig)
    print(f"[OK] Figura 4 salva em: {out_fig4}")


if __name__ == "__main__":
    main()
