"""05_estimar_mecanismos_e_retencao.py — Mecanismos Dinâmicos, Fluxos e Retenção Longitudinal.

Este script investiga os mecanismos que explicam a dinâmica do estoque médico:
1. Decomposição de Fluxos: DDD sobre Entradas (Inflows), Saídas (Outflows) e Saldo Líquido;
2. Coorte Madura de Retenção a 6 Meses (Entradas entre 2025-08 e 2026-01 rastreadas até 2026-02 a 2026-07);
3. Censura explícita de horizontes sem seguimento comum maduro (12 meses).

Conforme as Seções 4.4 e 5 de docs/05_roadmap_execucao.md:
- Entradas e saídas são tratadas em contagens (níveis), sem condicionar a causalidade aos entrantes.
- A taxa de permanência é apresentada como análise descritiva de sobrevivência de coortes.

Entregáveis:
- output/avaliacao_impacto/modelos/resultados_mecanismos_fluxos.json
- output/avaliacao_impacto/tabelas/tabela3_mecanismos_fluxos_e_retencao.csv
- output/avaliacao_impacto/tabelas/tabela3_mecanismos_fluxos_e_retencao.md
- output/avaliacao_impacto/tabelas/tabela3_mecanismos_fluxos_e_retencao.tex
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
    """Projeção FWL via MAP para efeitos fixos."""
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


def estimate_mechanism_ddd(df: pd.DataFrame, y_col: str, label: str) -> Dict[str, Any]:
    fe_cols = ["cell_id", "muni_month", "course_month"]
    y_proj, d_proj = project_fe(df, y_col, "treat_x_post", fe_cols)
    
    reg_df = pd.DataFrame({
        "y": y_proj,
        "d": d_proj,
        "cluster": df["co_ibge_6d"].values,
    })
    
    mod = sm.OLS(reg_df["y"], reg_df["d"]).fit(
        cov_type="cluster", cov_kwds={"groups": reg_df["cluster"]}
    )
    
    beta = float(mod.params.iloc[0])
    se = float(mod.bse.iloc[0])
    t_stat = float(mod.tvalues.iloc[0])
    p_val = float(mod.pvalues.iloc[0])
    ci_low = float(mod.conf_int().iloc[0, 0])
    ci_high = float(mod.conf_int().iloc[0, 1])
    
    mean_pre_treat = float(df[(df["post_t"] == 0) & (df["immediate_ms"] == 1)][y_col].mean())
    mean_pre_ctrl = float(df[(df["post_t"] == 0) & (df["immediate_ms"] == 0)][y_col].mean())
    mean_post_treat = float(df[(df["post_t"] == 1) & (df["immediate_ms"] == 1)][y_col].mean())
    mean_post_ctrl = float(df[(df["post_t"] == 1) & (df["immediate_ms"] == 0)][y_col].mean())

    return {
        "mecanismo": label,
        "outcome": y_col,
        "beta_ddd": beta,
        "se": se,
        "t_stat": t_stat,
        "p_valor": p_val,
        "ci_95": [ci_low, ci_high],
        "media_pre_trat": mean_pre_treat,
        "media_pre_ctrl": mean_pre_ctrl,
        "media_pos_trat": mean_post_treat,
        "media_pos_ctrl": mean_post_ctrl,
        "n_obs": len(df),
        "n_clusters": int(df["co_ibge_6d"].nunique()),
    }


def main() -> None:
    print("=== [Etapa 5] Mecanismos Dinâmicos, Fluxos e Retenção Longitudinal ===")
    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    TABELAS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_parquet(PAINEL_MUNI_FILE)
    df = df[df["amostra_principal"] & (~df["mes_transicao"]) & df["within_muni_var"]].copy()

    df["cell_id"] = df["co_ibge_6d"].astype(str) + "_" + df["cod_curso"].astype(str)
    df["muni_month"] = df["co_ibge_6d"].astype(str) + "_" + df["competencia"].astype(str)
    df["course_month"] = df["cod_curso"].astype(str) + "_" + df["competencia"].astype(str)

    # 1. Estimação DDD para Mecanismos de Fluxo
    print("Estimando DDD sobre Entradas (Inflows)...")
    res_entradas = estimate_mechanism_ddd(df, "n_entradas", "1. Entradas Mensais (Inflows)")

    print("Estimando DDD sobre Saídas (Outflows)...")
    res_saidas = estimate_mechanism_ddd(df, "n_saidas", "2. Saídas Mensais (Outflows)")

    print("Estimando DDD sobre Saldo Líquido...")
    res_saldo = estimate_mechanism_ddd(df, "saldo_liquido", "3. Saldo Líquido (Entradas - Saídas)")

    print("Estimando DDD sobre Churn Bruto...")
    res_churn = estimate_mechanism_ddd(df, "churn_bruto", "4. Churn Bruto (Entradas + Saídas)")

    # 2. Análise da Coorte Madura de Retenção a 6 Meses
    # Coorte de entrantes de 2025-08 a 2026-01 observados até 2026-02 a 2026-07
    df_all_months = pd.read_parquet(PAINEL_MUNI_FILE)
    df_all_months = df_all_months[df_all_months["amostra_principal"]].copy()

    # Janela de seguimento de permanência a 6 meses (202602 a 202607)
    df_pos_ret = df_all_months[df_all_months["competencia"].between("202602", "202607")].copy()
    
    ret_imed = df_pos_ret[df_pos_ret["immediate_ms"] == 1]
    ret_res = df_pos_ret[df_pos_ret["immediate_ms"] == 0]

    soma_entradas_coorte_imed = float(df_all_months[(df_all_months["competencia"].between("202508", "202601")) & (df_all_months["immediate_ms"] == 1)]["n_entradas"].sum())
    soma_retidos_6m_imed = float(ret_imed["permanencia_6m"].sum())
    taxa_retencao_6m_imed = (soma_retidos_6m_imed / soma_entradas_coorte_imed * 100) if soma_entradas_coorte_imed > 0 else 0.0

    soma_entradas_coorte_res = float(df_all_months[(df_all_months["competencia"].between("202508", "202601")) & (df_all_months["immediate_ms"] == 0)]["n_entradas"].sum())
    soma_retidos_6m_res = float(ret_res["permanencia_6m"].sum())
    taxa_retencao_6m_res = (soma_retidos_6m_res / soma_entradas_coorte_res * 100) if soma_entradas_coorte_res > 0 else 0.0

    # 3. Montar Tabela 3 Consolidada
    mecanismos_list = [res_entradas, res_saidas, res_saldo, res_churn]

    rows_tab3 = []
    for r in mecanismos_list:
        stars = ""
        p = r["p_valor"]
        if p < 0.01:
            stars = "***"
        elif p < 0.05:
            stars = "**"
        elif p < 0.10:
            stars = "*"

        rows_tab3.append({
            "Mecanismo Analisado": r["mecanismo"],
            "Efeito DDD (Beta)": f"{r['beta_ddd']:.4f}{stars}",
            "Erro-Padrão": f"({r['se']:.4f})",
            "P-valor": f"{r['p_valor']:.4f}",
            "Média Pré (Trat)": f"{r['media_pre_trat']:.3f}",
            "Média Pré (Ctrl)": f"{r['media_pre_ctrl']:.3f}",
            "Média Pós (Trat)": f"{r['media_pos_trat']:.3f}",
            "Média Pós (Ctrl)": f"{r['media_pos_ctrl']:.3f}",
            "N Obs": f"{r['n_obs']:,}",
        })

    # Adicionar bloco de retenção de coortes
    rows_tab3.append({
        "Mecanismo Analisado": "5. Retenção 6 Meses (Coorte 2025-08 a 2026-01)",
        "Efeito DDD (Beta)": f"{taxa_retencao_6m_imed - taxa_retencao_6m_res:+.1f} p.p.",
        "Erro-Padrão": "-",
        "P-valor": "Descritivo",
        "Média Pré (Trat)": "-",
        "Média Pré (Ctrl)": "-",
        "Média Pós (Trat)": f"{taxa_retencao_6m_imed:.1f}% ({int(soma_retidos_6m_imed)}/{int(soma_entradas_coorte_imed)})",
        "Média Pós (Ctrl)": f"{taxa_retencao_6m_res:.1f}% ({int(soma_retidos_6m_res)}/{int(soma_entradas_coorte_res)})",
        "N Obs": f"{len(df_pos_ret):,}",
    })
    rows_tab3.append({
        "Mecanismo Analisado": "6. Retenção 12 Meses (Seguimento Completo)",
        "Efeito DDD (Beta)": "Censurado",
        "Erro-Padrão": "-",
        "P-valor": "-",
        "Média Pré (Trat)": "-",
        "Média Pré (Ctrl)": "-",
        "Média Pós (Trat)": "Requer extensão até 2027-01",
        "Média Pós (Ctrl)": "Requer extensão até 2027-01",
        "N Obs": "-",
    })

    df_tab3 = pd.DataFrame(rows_tab3)

    # Salvar CSV, Markdown e LaTeX
    out_csv = TABELAS_DIR / "tabela3_mecanismos_fluxos_e_retencao.csv"
    out_md = TABELAS_DIR / "tabela3_mecanismos_fluxos_e_retencao.md"
    out_tex = TABELAS_DIR / "tabela3_mecanismos_fluxos_e_retencao.tex"

    df_tab3.to_csv(out_csv, index=False, encoding="utf-8-sig")

    with out_md.open("w", encoding="utf-8") as f:
        f.write("# Tabela 3 — Mecanismos de Dinâmica da Oferta: Entradas, Saídas e Retenção\n\n")
        f.write(df_tab3.to_markdown(index=False))
        f.write("\n\n*Notas: Modelos 1 a 4 estimados por Tripla Diferença com efeitos fixos de Célula (ms), Município-Mês (mt) e Curso-Mês (st), com erros-padrão clusterizados por município. O item 5 apresenta a taxa de sobrevivência descritiva da coorte madura pós-oferta. O item 6 é pré-especificado e marcado como censurado na janela atual.*\n")

    with out_tex.open("w", encoding="utf-8") as f:
        f.write(df_tab3.to_latex(index=False, caption="Mecanismos de Dinâmica da Oferta Médica — Entradas, Saídas e Retenção", label="tab:mecanismos_fluxos"))

    # Salvar JSON
    resultado_json = {
        "mecanismos_ddd": mecanismos_list,
        "analise_retencao_6m": {
            "coorte_entrada": "2025-08 a 2026-01",
            "janela_avaliacao": "2026-02 a 2026-07",
            "imediata": {
                "entradas_totais": soma_entradas_coorte_imed,
                "retidos_6m": soma_retidos_6m_imed,
                "taxa_retencao_pct": taxa_retencao_6m_imed,
            },
            "reserva": {
                "entradas_totais": soma_entradas_coorte_res,
                "retidos_6m": soma_retidos_6m_res,
                "taxa_retencao_pct": taxa_retencao_6m_res,
            },
            "diferenca_taxa_retencao_pp": taxa_retencao_6m_imed - taxa_retencao_6m_res,
        },
        "retencao_12m": {
            "status": "CENSURADO",
            "justificativa": "Para avaliar 12 meses de retenção de toda a coorte de entradas 2025-08 a 2026-01, é necessário estender o painel até 2027-01.",
        },
    }

    out_json = MODELOS_DIR / "resultados_mecanismos_fluxos.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(resultado_json, f, ensure_ascii=False, indent=2)

    print(f"[OK] Mecanismos e Retenção estimados com sucesso:")
    print(f"     Tabela 3 CSV: {out_csv}")
    print(f"     Tabela 3 MD:  {out_md}")
    print(f"     Modelos JSON: {out_json}")


if __name__ == "__main__":
    main()
