"""03_estimar_ddd_estatica.py — Estimação Econométrica da DDD Estática Canônica.

Este script estima a especificação principal de Tripla Diferença (DDD) estática:
    Y_mst = alpha_ms + gamma_mt + delta_st + beta * (Immediate_ms x Post_t) + epsilon_mst

Modelos estimados:
1. Modelo 1 (DiD Básico): Efeitos fixos Célula (ms) + Tempo (t);
2. Modelo 2 (Two-Way FE com Curso-Mês): Efeitos fixos Célula (ms) + Curso-Mês (st);
3. Modelo 3 (DDD Canônica Principal): Efeitos fixos Célula (ms) + Município-Mês (mt) + Curso-Mês (st);
4. Modelo 4 (CBOs Estritamente Unívocos): DDD Canônica restrita a cursos sem sobreposição de CBO;
5. Modelo 5 (Cobertura Binária): DDD Canônica sobre indicador de ter ao menos 1 especialista ativo;
6. Modelo 6 (Carga Horária Semanal Total): DDD Canônica sobre FTE Total (horas semanais).

Todos os modelos utilizam erros-padrão clusterizados por município (co_ibge_6d).

Entregáveis:
- output/avaliacao_impacto/modelos/resultados_ddd_estatica.json
- output/avaliacao_impacto/tabelas/tabela2_ddd_estatica_resultado_primario.csv
- output/avaliacao_impacto/tabelas/tabela2_ddd_estatica_resultado_primario.md
- output/avaliacao_impacto/tabelas/tabela2_ddd_estatica_resultado_primario.tex
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output" / "avaliacao_impacto"
DADOS_DIR = OUTPUT_DIR / "dados"
MODELOS_DIR = OUTPUT_DIR / "modelos"
TABELAS_DIR = OUTPUT_DIR / "tabelas"

PAINEL_MUNI_FILE = DADOS_DIR / "painel_municipio_curso_mes.parquet"


def project_fe(df: pd.DataFrame, y_col: str, d_col: str, fe_cols: List[str], iterations: int = 15) -> tuple[np.ndarray, np.ndarray]:
    """Aplica o Método de Projeções Alternadas (MAP) para absorção exata de múltiplos efeitos fixos."""
    y = df[y_col].astype(float).values.copy()
    d = df[d_col].astype(float).values.copy()
    
    df_temp = pd.DataFrame({"y": y, "d": d})
    for fe in fe_cols:
        df_temp[fe] = df[fe].values

    for _ in range(iterations):
        for fe in fe_cols:
            df_temp["y"] -= df_temp.groupby(fe)["y"].transform("mean")
            df_temp["d"] -= df_temp.groupby(fe)["d"].transform("mean")

    return df_temp["y"].values, df_temp["d"].values


def estimate_model(
    df: pd.DataFrame,
    y_col: str,
    d_col: str,
    fe_cols: List[str],
    cluster_col: str,
    nome_modelo: str,
    descricao: str,
) -> Dict[str, Any]:
    y_proj, d_proj = project_fe(df, y_col, d_col, fe_cols)
    
    reg_df = pd.DataFrame({
        "y": y_proj,
        "d": d_proj,
        "cluster": df[cluster_col].values,
    })
    
    mod = sm.OLS(reg_df["y"], reg_df["d"]).fit(
        cov_type="cluster", cov_kwds={"groups": reg_df["cluster"]}
    )
    
    beta = float(mod.params.iloc[0])
    se = float(mod.bse.iloc[0])
    t_stat = float(mod.tvalues.iloc[0])
    p_val = float(mod.pvalues.iloc[0])
    ci_lower = float(mod.conf_int().iloc[0, 0])
    ci_upper = float(mod.conf_int().iloc[0, 1])
    
    y_orig = df[y_col].astype(float)
    r2_within = float(mod.rsquared)
    mean_dep = float(y_orig.mean())
    std_dep = float(y_orig.std())
    mean_pre_treat = float(df[(df["post_t"] == 0) & (df["immediate_ms"] == 1)][y_col].mean())
    mean_pre_ctrl = float(df[(df["post_t"] == 0) & (df["immediate_ms"] == 0)][y_col].mean())
    
    return {
        "nome_modelo": nome_modelo,
        "descricao": descricao,
        "outcome": y_col,
        "beta": beta,
        "se": se,
        "t_stat": t_stat,
        "p_valor": p_val,
        "ci_95": [ci_lower, ci_upper],
        "r2_within": r2_within,
        "n_obs": len(df),
        "n_clusters": int(df[cluster_col].nunique()),
        "media_dep_var": mean_dep,
        "desv_padrao_dep_var": std_dep,
        "media_pre_tratamento": mean_pre_treat,
        "media_pre_controle": mean_pre_ctrl,
        "efeitos_fixos": fe_cols,
    }


def main() -> None:
    print("=== [Etapa 3] Estimação Econométrica da DDD Estática Canônica ===")
    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    TABELAS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(PAINEL_MUNI_FILE)
    # Filtrar para amostra principal (Imediata vs Reserva) e excluir mês de transição (2025-07)
    df = df[df["amostra_principal"] & (~df["mes_transicao"])].copy()

    # Criar identificadores de efeitos fixos
    df["cell_id"] = df["co_ibge_6d"].astype(str) + "_" + df["cod_curso"].astype(str)
    df["muni_month"] = df["co_ibge_6d"].astype(str) + "_" + df["competencia"].astype(str)
    df["course_month"] = df["cod_curso"].astype(str) + "_" + df["competencia"].astype(str)

    # Subamostras
    df_var = df[df["within_muni_var"]].copy()
    df_univoco = df_var[~df_var["flag_overlap_cbo"]].copy()

    resultados: List[Dict[str, Any]] = []

    # 1. Modelo 1: DiD Básico (Cell FE + Month FE)
    print("Estimando Modelo 1: DiD Básico...")
    m1 = estimate_model(
        df=df,
        y_col="especialistas_mst",
        d_col="treat_x_post",
        fe_cols=["cell_id", "competencia"],
        cluster_col="co_ibge_6d",
        nome_modelo="M1_DiD_Basico",
        descricao="DiD com FE Célula e Mês",
    )
    resultados.append(m1)

    # 2. Modelo 2: Two-Way FE com Curso-Mês
    print("Estimando Modelo 2: DiD com FE Curso-Mês...")
    m2 = estimate_model(
        df=df,
        y_col="especialistas_mst",
        d_col="treat_x_post",
        fe_cols=["cell_id", "course_month"],
        cluster_col="co_ibge_6d",
        nome_modelo="M2_DiD_Curso_Mes",
        descricao="DiD com FE Célula e Curso-Mês",
    )
    resultados.append(m2)

    # 3. Modelo 3: DDD Canônica Principal (Cell FE + Muni-Month FE + Course-Month FE)
    print("Estimando Modelo 3: DDD Canônica Principal...")
    m3 = estimate_model(
        df=df_var,
        y_col="especialistas_mst",
        d_col="treat_x_post",
        fe_cols=["cell_id", "muni_month", "course_month"],
        cluster_col="co_ibge_6d",
        nome_modelo="M3_DDD_Principal",
        descricao="DDD Canônica com FE Célula, Município-Mês e Curso-Mês",
    )
    resultados.append(m3)

    # 4. Modelo 4: DDD Canônica - CBOs Estritamente Unívocos
    print("Estimando Modelo 4: DDD Canônica (CBOs Unívocos)...")
    m4 = estimate_model(
        df=df_univoco,
        y_col="especialistas_mst",
        d_col="treat_x_post",
        fe_cols=["cell_id", "muni_month", "course_month"],
        cluster_col="co_ibge_6d",
        nome_modelo="M4_DDD_Univocos",
        descricao="DDD Canônica em CBOs Estritamente Unívocos (sem sobreposição)",
    )
    resultados.append(m4)

    # 5. Modelo 5: DDD Canônica - Cobertura Binária
    print("Estimando Modelo 5: DDD Canônica (Cobertura Binária)...")
    m5 = estimate_model(
        df=df_var,
        y_col="cobertura_binaria_mst",
        d_col="treat_x_post",
        fe_cols=["cell_id", "muni_month", "course_month"],
        cluster_col="co_ibge_6d",
        nome_modelo="M5_DDD_Cobertura_Binaria",
        descricao="DDD Canônica sobre Probabilidade de Cobertura Local (>=1 Médico)",
    )
    resultados.append(m5)

    # 6. Modelo 6: DDD Canônica - Carga Horária Semanal Total (FTE)
    print("Estimando Modelo 6: DDD Canônica (Carga Horária Semanal)...")
    m6 = estimate_model(
        df=df_var,
        y_col="fte_total",
        d_col="treat_x_post",
        fe_cols=["cell_id", "muni_month", "course_month"],
        cluster_col="co_ibge_6d",
        nome_modelo="M6_DDD_Carga_Horaria_FTE",
        descricao="DDD Canônica sobre Carga Horária Semanal Total (Horas/Semana)",
    )
    resultados.append(m6)

    # Salvar modelos JSON
    out_json = MODELOS_DIR / "resultados_ddd_estatica.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"[OK] Resultados JSON salvos em: {out_json}")

    # Montar Tabela 2 Consolidada
    rows_tab2 = []
    for r in resultados:
        stars = ""
        p = r["p_valor"]
        if p < 0.01:
            stars = "***"
        elif p < 0.05:
            stars = "**"
        elif p < 0.10:
            stars = "*"

        rows_tab2.append({
            "Modelo": r["nome_modelo"],
            "Descrição / Especificação": r["descricao"],
            "Outcome Analisado": r["outcome"],
            "Coeficiente Beta (DDD)": f"{r['beta']:.4f}{stars}",
            "Erro-Padrão Clusterizado": f"({r['se']:.4f})",
            "IC 95%": f"[{r['ci_95'][0]:.4f}, {r['ci_95'][1]:.4f}]",
            "Estatística t": f"{r['t_stat']:.3f}",
            "P-valor": f"{r['p_valor']:.4f}",
            "Média Pre-Tratamento": f"{r['media_pre_tratamento']:.3f}",
            "Média Pre-Controle": f"{r['media_pre_controle']:.3f}",
            "N Observações": f"{r['n_obs']:,}",
            "N Clusters (Municípios)": f"{r['n_clusters']:,}",
            "R² Within": f"{r['r2_within']:.4f}",
        })

    df_tab2 = pd.DataFrame(rows_tab2)

    # Salvar CSV, Markdown e LaTeX
    out_csv = TABELAS_DIR / "tabela2_ddd_estatica_resultado_primario.csv"
    out_md = TABELAS_DIR / "tabela2_ddd_estatica_resultado_primario.md"
    out_tex = TABELAS_DIR / "tabela2_ddd_estatica_resultado_primario.tex"

    df_tab2.to_csv(out_csv, index=False, encoding="utf-8-sig")
    
    with out_md.open("w", encoding="utf-8") as f:
        f.write("# Tabela 2 — Resultados Principais da Tripla Diferença (DDD) Estática\n\n")
        f.write(df_tab2.to_markdown(index=False))
        f.write("\n\n*Notas: Erros-padrão clusterizados ao nível de município entre parênteses. *** p<0.01, ** p<0.05, * p<0.10. Janela pré: 2024-06 a 2025-06; mês de transição 2025-07 excluído; janela pós: 2025-08 a 2026-07.*\n")

    with out_tex.open("w", encoding="utf-8") as f:
        f.write(df_tab2.to_latex(index=False, caption="Resultados Principais da Tripla Diferença (DDD) Estática — PMM-E Ciclo 1", label="tab:ddd_principal"))

    print(f"[OK] Tabela 2 gerada com sucesso:")
    print(f"     CSV: {out_csv}")
    print(f"     Markdown: {out_md}")
    print(f"     LaTeX: {out_tex}")


if __name__ == "__main__":
    main()
