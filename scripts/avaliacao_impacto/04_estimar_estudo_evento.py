"""04_estimar_estudo_evento.py — Estudo de Evento Dinâmico (Event Study DDD).

Este script estima os coeficientes dinâmicos mês a mês para verificar:
1. Pré-tendências paralelas (validade da identificação no período 2024-06 a 2025-06);
2. Trajetória dinâmica pós-tratamento (mês a mês de 2025-08 a 2026-07).

Especificação dinâmica:
    Y_mst = alpha_ms + gamma_mt + delta_st + sum_{k != 202506} beta_k * (Immediate_ms x 1{t = k}) + epsilon_mst

Período de referência: 2025-06 (mês imediatamente anterior ao anúncio).
Erros-padrão clusterizados ao nível de município (co_ibge_6d).

Entregáveis:
- output/avaliacao_impacto/modelos/resultados_estudo_evento.json
- output/avaliacao_impacto/tabelas/tabela_estudo_evento_dinamico.csv
- output/avaliacao_impacto/figuras/figura1_estudo_evento_ddd_dinamico.png
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output" / "avaliacao_impacto"
DADOS_DIR = OUTPUT_DIR / "dados"
MODELOS_DIR = OUTPUT_DIR / "modelos"
TABELAS_DIR = OUTPUT_DIR / "tabelas"
FIGURAS_DIR = OUTPUT_DIR / "figuras"

PAINEL_MUNI_FILE = DADOS_DIR / "painel_municipio_curso_mes.parquet"

ALL_COMPETENCIAS = [
    f"{year}{month:02d}"
    for year, first, last in ((2024, 6, 12), (2025, 1, 12), (2026, 1, 7))
    for month in range(first, last + 1)
]
REF_MONTH = "202506"


def main() -> None:
    print("=== [Etapa 4] Estudo de Evento Dinâmico (Event Study DDD) ===")
    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    TABELAS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(PAINEL_MUNI_FILE)
    df = df[df["amostra_principal"] & df["within_muni_var"]].copy()

    df["cell_id"] = df["co_ibge_6d"].astype(str) + "_" + df["cod_curso"].astype(str)
    df["muni_month"] = df["co_ibge_6d"].astype(str) + "_" + df["competencia"].astype(str)
    df["course_month"] = df["cod_curso"].astype(str) + "_" + df["competencia"].astype(str)

    # Construir dummies de interação mês a mês
    inter_cols = []
    for comp in ALL_COMPETENCIAS:
        if comp == REF_MONTH:
            continue
        col_name = f"treat_x_{comp}"
        df[col_name] = (df["immediate_ms"] * (df["competencia"] == comp)).astype(float)
        inter_cols.append(col_name)

    # Projeção de efeitos fixos: cell_id, muni_month, course_month
    fe_cols = ["cell_id", "muni_month", "course_month"]
    print("Projetando efeitos fixos para variáveis dependentes e dinâmicas...")

    df_temp = pd.DataFrame()
    df_temp["y"] = df["especialistas_mst"].astype(float).values
    for c in inter_cols:
        df_temp[c] = df[c].values
    for fe in fe_cols:
        df_temp[fe] = df[fe].values

    # Iterative MAP
    for iteration in range(12):
        for fe in fe_cols:
            df_temp["y"] -= df_temp.groupby(fe)["y"].transform("mean")
            for c in inter_cols:
                df_temp[c] -= df_temp.groupby(fe)[c].transform("mean")

    # Regressão OLS multivariada com cluster por município
    X = df_temp[inter_cols]
    y = df_temp["y"]
    groups = df["co_ibge_6d"].values

    mod = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groups})

    # Compilar resultados por competência
    event_study_rows: List[Dict[str, Any]] = []
    pre_betas = []
    pre_ses = []

    for comp in ALL_COMPETENCIAS:
        comp_fmt = f"{comp[:4]}-{comp[4:]}"
        is_pre = 1 if comp < "202507" else 0
        is_trans = 1 if comp == "202507" else 0
        is_pos = 1 if comp >= "202508" else 0

        if comp == REF_MONTH:
            beta = 0.0
            se = 0.0
            t_stat = 0.0
            p_val = 1.0
            ci_low = 0.0
            ci_high = 0.0
        else:
            col_name = f"treat_x_{comp}"
            beta = float(mod.params[col_name])
            se = float(mod.bse[col_name])
            t_stat = float(mod.tvalues[col_name])
            p_val = float(mod.pvalues[col_name])
            ci_low = beta - 1.96 * se
            ci_high = beta + 1.96 * se

            if is_pre:
                pre_betas.append(beta)
                pre_ses.append(se)

        event_study_rows.append({
            "competencia": comp,
            "periodo_formatado": comp_fmt,
            "fase": "PRE" if is_pre else ("TRANSICAO" if is_trans else "POS"),
            "beta": beta,
            "se": se,
            "t_stat": t_stat,
            "p_valor": p_val,
            "ci_95_inferior": ci_low,
            "ci_95_superior": ci_high,
            "is_referencia": comp == REF_MONTH,
        })

    # Teste conjunto de pré-tendências (Wald test para H0: betas_pre = 0)
    pre_cols = [f"treat_x_{comp}" for comp in ALL_COMPETENCIAS if comp < "202507" and comp != REF_MONTH]
    r_matrix = np.eye(len(inter_cols))[[inter_cols.index(c) for c in pre_cols]]
    wald_test = mod.wald_test(r_matrix)
    wald_stat = float(wald_test.statistic)
    wald_pval = float(wald_test.pvalue)

    print(f"Teste conjunto de Pré-Tendências (Wald): F = {wald_stat:.4f}, p-valor = {wald_pval:.4f}")

    df_event = pd.DataFrame(event_study_rows)

    # Salvar tabela
    out_csv = TABELAS_DIR / "tabela_estudo_evento_dinamico.csv"
    df_event.to_csv(out_csv, index=False, encoding="utf-8-sig")

    # Salvar JSON
    resultado_json = {
        "mes_referencia": REF_MONTH,
        "n_obs": len(df),
        "n_clusters": int(df["co_ibge_6d"].nunique()),
        "wald_pre_tendencias": {
            "estatistica_f": wald_stat,
            "p_valor": wald_pval,
            "hipotese_nula": "Betas pré-tratamento conjuntamente iguais a zero (pré-tendências paralelas)",
            "conclusao": "Aprovado: não há evidência de desvio de pré-tendências paralelas (p > 0.10)." if wald_pval > 0.10 else "Atenção: pré-tendências apresentam ruído marginal.",
        },
        "coeficientes_dinamicos": event_study_rows,
    }

    out_json = MODELOS_DIR / "resultados_estudo_evento.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(resultado_json, f, ensure_ascii=False, indent=2)

    # 4. Gerar Gráfico do Estudo de Evento
    print("Gerando figura do Estudo de Evento...")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)

    x_labels = df_event["periodo_formatado"].tolist()
    x_pos = np.arange(len(x_labels))
    betas = df_event["beta"].values
    ci_lows = df_event["ci_95_inferior"].values
    ci_highs = df_event["ci_95_superior"].values

    # Linha zero
    ax.axhline(0, color="black", linestyle="--", linewidth=1, alpha=0.7)

    # Linha vertical do anúncio (2025-07)
    trans_idx = x_labels.index("2025-07")
    ax.axvline(trans_idx, color="#d9534f", linestyle=":", linewidth=1.5, label="Anúncio PMM-E Ciclo 1 (2025-07)")

    # Plot de coeficientes com barra de erro
    ax.errorbar(
        x_pos,
        betas,
        yerr=[betas - ci_lows, ci_highs - betas],
        fmt="o",
        color="#0275d8",
        ecolor="#0275d8",
        elinewidth=1.5,
        capsize=3,
        capthick=1.5,
        markersize=6,
        label=r"$\hat{\beta}_k$ (DDD Dinâmica $\pm$ 95% IC)",
    )

    # Destacar ponto de referência
    ref_idx = x_labels.index(f"{REF_MONTH[:4]}-{REF_MONTH[4:]}")
    ax.plot(ref_idx, 0, marker="s", color="#5cb85c", markersize=8, label="Mês de Referência (2025-06 = 0)")

    # Sombrear área pós-tratamento
    ax.axvspan(trans_idx + 0.5, len(x_pos) - 0.5, color="#f0f8ff", alpha=0.5, label="Período Pós-Oferta Madura")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Impacto Estimado no Estoque de Médicos (Níveis)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Competência CNES (Mês/Ano)", fontsize=11, fontweight="bold")
    ax.set_title("Estudo de Evento: Efeito da Oferta de Vagas Imediatas vs Reserva sobre o Estoque Local de Especialistas", fontsize=12, fontweight="bold", pad=15)
    ax.legend(loc="upper left", frameon=True, framealpha=0.9)

    plt.tight_layout()
    out_png = FIGURAS_DIR / "figura1_estudo_evento_ddd_dinamico.png"
    fig.savefig(out_png, dpi=300)
    plt.close(fig)

    print(f"[OK] Estudo de Evento concluído:")
    print(f"     Tabela: {out_csv}")
    print(f"     JSON: {out_json}")
    print(f"     Figura: {out_png}")


if __name__ == "__main__":
    main()
