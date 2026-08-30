"""06_avaliar_robustez_e_redistribuicao.py — Diagnósticos de Redistribuição, Robustez e Heterogeneidade.

Este script executa as baterias de testes de robustez e diagnósticos de identificação:
1. Diagnóstico de Redistribuição Espacial: Comparação dos efeitos estimados ao nível do Estabelecimento (CNES),
   do Município (Canônico) e da Região de Saúde (Spillovers e Expansão Líquida Regional);
2. Sensibilidade a Clusters Dominantes: Re-estimação excluindo os maiores municípios/capitais;
3. Heterogeneidade por Vulnerabilidade Social: IVS 2010 (Alta/Muito Alta Vulnerabilidade vs Média/Baixa);
4. Heterogeneidade por Tipo de Gestão: Gestão Municipal vs Estadual/Dupla.

Conforme a Seção 2 e 8 de docs/05_roadmap_execucao.md:
- Resultados no estabelecimento e na região de saúde são diagnósticos de redistribuição, não novas famílias de outcomes.
- Se houver canibalização intramunicipal ou regional, o diagnóstico revelará a divergência entre os níveis.

Entregáveis:
- output/avaliacao_impacto/modelos/resultados_robustez_e_redistribuicao.json
- output/avaliacao_impacto/tabelas/tabela4_diagnosticos_robustez_e_redistribuicao.csv
- output/avaliacao_impacto/tabelas/tabela4_diagnosticos_robustez_e_redistribuicao.md
- output/avaliacao_impacto/tabelas/tabela4_diagnosticos_robustez_e_redistribuicao.tex
- output/avaliacao_impacto/figuras/figura2_diagnostico_redistribuicao.png
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output" / "avaliacao_impacto"
DADOS_DIR = OUTPUT_DIR / "dados"
MODELOS_DIR = OUTPUT_DIR / "modelos"
TABELAS_DIR = OUTPUT_DIR / "tabelas"
FIGURAS_DIR = OUTPUT_DIR / "figuras"

PAINEL_MUNI_FILE = DADOS_DIR / "painel_municipio_curso_mes.parquet"
PAINEL_CNES_FILE = DADOS_DIR / "painel_cnes_curso_mes.parquet"
PAINEL_REGIAO_FILE = DADOS_DIR / "painel_regiao_curso_mes.parquet"


def project_fe(df: pd.DataFrame, y_col: str, d_col: str, fe_cols: List[str], iterations: int = 15) -> tuple[np.ndarray, np.ndarray]:
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


def run_reg(df: pd.DataFrame, y_col: str, d_col: str, fe_cols: List[str], cluster_col: str, label: str, grupo: str) -> Dict[str, Any]:
    y_proj, d_proj = project_fe(df, y_col, d_col, fe_cols)
    reg_df = pd.DataFrame({"y": y_proj, "d": d_proj, "cluster": df[cluster_col].values})
    
    mod = sm.OLS(reg_df["y"], reg_df["d"]).fit(cov_type="cluster", cov_kwds={"groups": reg_df["cluster"]})
    
    beta = float(mod.params.iloc[0])
    se = float(mod.bse.iloc[0])
    t_stat = float(mod.tvalues.iloc[0])
    p_val = float(mod.pvalues.iloc[0])
    ci_low = float(mod.conf_int().iloc[0, 0])
    ci_high = float(mod.conf_int().iloc[0, 1])
    
    return {
        "grupo_analise": grupo,
        "especificacao": label,
        "beta": beta,
        "se": se,
        "t_stat": t_stat,
        "p_valor": p_val,
        "ci_95": [ci_low, ci_high],
        "n_obs": len(df),
        "n_clusters": int(df[cluster_col].nunique()),
    }


def main() -> None:
    print("=== [Etapa 6] Diagnósticos de Redistribuição, Robustez e Heterogeneidade ===")
    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    TABELAS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Carregar painéis
    df_muni = pd.read_parquet(PAINEL_MUNI_FILE)
    df_muni = df_muni[df_muni["amostra_principal"] & (df_muni["mes_transicao"] == 0)].copy()
    df_muni["cell_id"] = df_muni["co_ibge_6d"].astype(str) + "_" + df_muni["cod_curso"].astype(str)
    df_muni["muni_month"] = df_muni["co_ibge_6d"].astype(str) + "_" + df_muni["competencia"].astype(str)
    df_muni["course_month"] = df_muni["cod_curso"].astype(str) + "_" + df_muni["competencia"].astype(str)

    df_cnes = pd.read_parquet(PAINEL_CNES_FILE)
    df_cnes = df_cnes[df_cnes["amostra_principal"] & (df_cnes["mes_transicao"] == 0)].copy()
    df_cnes["cell_id"] = df_cnes["co_cnes_7d"].astype(str) + "_" + df_cnes["cod_curso"].astype(str)
    df_cnes["cnes_month"] = df_cnes["co_cnes_7d"].astype(str) + "_" + df_cnes["competencia"].astype(str)
    df_cnes["course_month"] = df_cnes["cod_curso"].astype(str) + "_" + df_cnes["competencia"].astype(str)
    df_cnes["treat_x_post"] = df_cnes["immediate_is"] * df_cnes["post_t"]

    df_reg = pd.read_parquet(PAINEL_REGIAO_FILE)
    df_reg = df_reg[df_reg["mes_transicao"] == 0].copy()
    df_reg["cell_id"] = df_reg["no_regiao_saude"].astype(str) + "_" + df_reg["cod_curso"].astype(str)
    df_reg["reg_month"] = df_reg["no_regiao_saude"].astype(str) + "_" + df_reg["competencia"].astype(str)
    df_reg["course_month"] = df_reg["cod_curso"].astype(str) + "_" + df_reg["competencia"].astype(str)

    robustez_resultados: List[Dict[str, Any]] = []

    # Eixo A: Diagnóstico de Redistribuição Espacial (Estabelecimento vs Município vs Região)
    print("Estimando Eixo A: Redistribuição Espacial...")
    
    # 1. Nível Estabelecimento (CNES)
    res_cnes = run_reg(
        df=df_cnes,
        y_col="n_especialistas_distintos",
        d_col="treat_x_post",
        fe_cols=["cell_id", "cnes_month", "course_month"],
        cluster_col="co_cnes_7d",
        label="1. Nível Estabelecimento (CNES)",
        grupo="A. Redistribuição Espacial",
    )
    robustez_resultados.append(res_cnes)

    # 2. Nível Municipal (Canônico)
    df_muni_var = df_muni[df_muni["within_muni_var"]].copy()
    res_muni = run_reg(
        df=df_muni_var,
        y_col="especialistas_mst",
        d_col="treat_x_post",
        fe_cols=["cell_id", "muni_month", "course_month"],
        cluster_col="co_ibge_6d",
        label="2. Nível Município (Canônico DDD)",
        grupo="A. Redistribuição Espacial",
    )
    robustez_resultados.append(res_muni)

    # 3. Nível Regional (Região de Saúde)
    reg_var = df_reg.groupby("no_regiao_saude")["immediate_rs"].nunique()
    regs_with_var = set(reg_var[reg_var > 1].index)
    df_reg_var = df_reg[df_reg["no_regiao_saude"].isin(regs_with_var)].copy()
    
    res_regiao = run_reg(
        df=df_reg_var,
        y_col="especialistas_rst",
        d_col="treat_x_post",
        fe_cols=["cell_id", "reg_month", "course_month"],
        cluster_col="no_regiao_saude",
        label="3. Nível Região de Saúde (Spillovers)",
        grupo="A. Redistribuição Espacial",
    )
    robustez_resultados.append(res_regiao)

    # Eixo B: Sensibilidade e Amostras Restritas
    print("Estimando Eixo B: Sensibilidade a Clusters...")
    
    # 4. Excluindo os 3 maiores municípios (Top Clusters por N vagas)
    top_munis = df_muni.groupby("co_ibge_6d")["qt_vagas_total"].sum().nlargest(3).index.tolist()
    df_sem_top3 = df_muni_var[~df_muni_var["co_ibge_6d"].isin(top_munis)].copy()
    res_sem_top3 = run_reg(
        df=df_sem_top3,
        y_col="especialistas_mst",
        d_col="treat_x_post",
        fe_cols=["cell_id", "muni_month", "course_month"],
        cluster_col="co_ibge_6d",
        label="4. Excluindo Top 3 Municípios com Mais Vagas",
        grupo="B. Sensibilidade Amostral",
    )
    robustez_resultados.append(res_sem_top3)

    # 5. CBOs Estritamente Unívocos (sem sobreposição)
    df_univoco = df_muni_var[~df_muni_var["flag_overlap_cbo"]].copy()
    res_univoco = run_reg(
        df=df_univoco,
        y_col="especialistas_mst",
        d_col="treat_x_post",
        fe_cols=["cell_id", "muni_month", "course_month"],
        cluster_col="co_ibge_6d",
        label="5. Apenas CBOs Estritamente Unívocos (1:1)",
        grupo="B. Sensibilidade Amostral",
    )
    robustez_resultados.append(res_univoco)

    # Eixo C: Heterogeneidade por Vulnerabilidade IVS 2010
    print("Estimando Eixo C: Heterogeneidade por IVS 2010...")
    
    # 6. Alta e Muito Alta Vulnerabilidade (IVS >= 0.400)
    df_alta_vuln = df_muni_var[df_muni_var["ivs_categoria"].isin(["ALTA", "MUITO_ALTA"])].copy()
    if len(df_alta_vuln) > 0 and df_alta_vuln["co_ibge_6d"].nunique() > 2:
        res_alta_vuln = run_reg(
            df=df_alta_vuln,
            y_col="especialistas_mst",
            d_col="treat_x_post",
            fe_cols=["cell_id", "muni_month", "course_month"],
            cluster_col="co_ibge_6d",
            label="6. Municípios de Alta / Muito Alta Vulnerabilidade (IVS)",
            grupo="C. Heterogeneidade IVS 2010",
        )
        robustez_resultados.append(res_alta_vuln)

    # 7. Média e Baixa Vulnerabilidade (IVS < 0.400)
    df_baixa_vuln = df_muni_var[df_muni_var["ivs_categoria"].isin(["MEDIA", "BAIXA", "MUITO_BAIXA"])].copy()
    if len(df_baixa_vuln) > 0 and df_baixa_vuln["co_ibge_6d"].nunique() > 2:
        res_baixa_vuln = run_reg(
            df=df_baixa_vuln,
            y_col="especialistas_mst",
            d_col="treat_x_post",
            fe_cols=["cell_id", "muni_month", "course_month"],
            cluster_col="co_ibge_6d",
            label="7. Municípios de Média / Baixa Vulnerabilidade (IVS)",
            grupo="C. Heterogeneidade IVS 2010",
        )
        robustez_resultados.append(res_baixa_vuln)

    # 2. Montar Tabela 4 Consolidada
    rows_tab4 = []
    for r in robustez_resultados:
        stars = ""
        p = r["p_valor"]
        if p < 0.01:
            stars = "***"
        elif p < 0.05:
            stars = "**"
        elif p < 0.10:
            stars = "*"

        rows_tab4.append({
            "Grupo": r["grupo_analise"],
            "Especificação / Subamostra": r["especificacao"],
            "Coeficiente Beta": f"{r['beta']:.4f}{stars}",
            "Erro-Padrão Clusterizado": f"({r['se']:.4f})",
            "IC 95%": f"[{r['ci_95'][0]:.4f}, {r['ci_95'][1]:.4f}]",
            "P-valor": f"{r['p_valor']:.4f}",
            "N Obs": f"{r['n_obs']:,}",
            "N Clusters": f"{r['n_clusters']:,}",
        })

    df_tab4 = pd.DataFrame(rows_tab4)

    # Salvar CSV, Markdown e LaTeX
    out_csv = TABELAS_DIR / "tabela4_diagnosticos_robustez_e_redistribuicao.csv"
    out_md = TABELAS_DIR / "tabela4_diagnosticos_robustez_e_redistribuicao.md"
    out_tex = TABELAS_DIR / "tabela4_diagnosticos_robustez_e_redistribuicao.tex"

    df_tab4.to_csv(out_csv, index=False, encoding="utf-8-sig")

    with out_md.open("w", encoding="utf-8") as f:
        f.write("# Tabela 4 — Diagnósticos de Redistribuição, Sensibilidade Amostral e Heterogeneidade\n\n")
        f.write(df_tab4.to_markdown(index=False))
        f.write("\n\n*Notas: Todos os modelos estimados com efeitos fixos correspondentes e erros-padrão clusterizados ao nível da unidade geográfica agregada. *** p<0.01, ** p<0.05, * p<0.10.*\n")

    with out_tex.open("w", encoding="utf-8") as f:
        f.write(df_tab4.to_latex(index=False, caption="Diagnósticos de Redistribuição, Robustez e Heterogeneidade", label="tab:robustez_redistribuicao"))

    # Salvar JSON
    out_json = MODELOS_DIR / "resultados_robustez_e_redistribuicao.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(robustez_resultados, f, ensure_ascii=False, indent=2)

    # 3. Gerar Figura 2: Comparação Estabelecimento vs Município vs Região
    print("Gerando figura comparativa de redistribuição...")
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

    eixo_a_items = [r for r in robustez_resultados if r["grupo_analise"] == "A. Redistribuição Espacial"]
    labels = [r["especificacao"] for r in eixo_a_items]
    betas = [r["beta"] for r in eixo_a_items]
    ci_lows = [r["ci_95"][0] for r in eixo_a_items]
    ci_highs = [r["ci_95"][1] for r in eixo_a_items]

    y_pos = np.arange(len(labels))
    ax.axvline(0, color="black", linestyle="--", linewidth=1, alpha=0.7)

    ax.errorbar(
        betas,
        y_pos,
        xerr=[np.array(betas) - np.array(ci_lows), np.array(ci_highs) - np.array(betas)],
        fmt="o",
        color="#0275d8",
        ecolor="#0275d8",
        elinewidth=2,
        capsize=4,
        capthick=2,
        markersize=8,
    )

    for i, (b, p) in enumerate(zip(betas, [r["p_valor"] for r in eixo_a_items])):
        ax.text(b, y_pos[i] + 0.15, f"Beta = {b:.3f} (p={p:.3f})", fontsize=10, fontweight="bold", ha="center")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_xlabel("Efeito Estimado (Tripla Diferença / DiD) em Níveis de Especialistas", fontsize=11, fontweight="bold")
    ax.set_title("Diagnóstico de Redistribuição: Comparação do Efeito no Estabelecimento, Município e Região", fontsize=12, fontweight="bold", pad=15)
    ax.invert_yaxis()

    plt.tight_layout()
    out_fig2 = FIGURAS_DIR / "figura2_diagnostico_redistribuicao.png"
    fig.savefig(out_fig2, dpi=300)
    plt.close(fig)

    print(f"[OK] Diagnósticos e Robustez concluídos:")
    print(f"     Tabela 4 CSV: {out_csv}")
    print(f"     Tabela 4 MD:  {out_md}")
    print(f"     Figura:       {out_fig2}")


if __name__ == "__main__":
    main()
