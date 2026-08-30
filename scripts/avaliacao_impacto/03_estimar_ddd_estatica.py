"""Estima a DDD estática do estoque e da cobertura municipal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from model_utils import atomic_to_csv, fit_absorbed_ols, result_for


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "avaliacao_impacto"
PANEL = OUT / "dados" / "painel_municipio_curso_mes.parquet"
MODELS = OUT / "modelos"
TABLES = OUT / "tabelas"


def estimate(df: pd.DataFrame, outcome: str, name: str, description: str) -> dict[str, Any]:
    model, diagnostics = fit_absorbed_ols(
        df, outcome, ["treat_x_post"], ["cell_id", "muni_month", "course_month"], "co_ibge_6d"
    )
    result = result_for(model, "treat_x_post")
    result.update(
        {
            "nome_modelo": name,
            "descricao": description,
            "outcome": outcome,
            "n_obs": int(len(df)),
            "n_clusters": int(df["co_ibge_6d"].nunique()),
            "media_pre_tratamento": float(df.loc[(df["post_t"] == 0) & (df["immediate_ms"] == 1), outcome].mean()),
            "media_pre_controle": float(df.loc[(df["post_t"] == 0) & (df["immediate_ms"] == 0), outcome].mean()),
            "efeitos_fixos": ["município-curso", "município-mês", "curso-mês"],
            "diagnosticos_numericos": diagnostics,
        }
    )
    return result


def main() -> None:
    MODELS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PANEL)
    df = df[df["mes_transicao"] == 0].copy()
    df["cell_id"] = df["co_ibge_6d"].astype(str) + "_" + df["cod_curso"].astype(str)
    df["muni_month"] = df["co_ibge_6d"].astype(str) + "_" + df["competencia"].astype(str)
    df["course_month"] = df["cod_curso"].astype(str) + "_" + df["competencia"].astype(str)

    confirm = df[df["amostra_confirmatoria"] & df["within_muni_var_confirmatoria"]].copy()
    expanded = df[df["amostra_principal"] & df["within_muni_var_ampliada"]].copy()
    results = [
        estimate(confirm, "especialistas_mst", "M1_DDD_Principal_Confirmatoria", "DDD do estoque; cursos sem CBO compartilhado"),
        estimate(expanded, "especialistas_mst", "M2_DDD_Ampliada", "DDD do estoque; 16 cursos como sensibilidade operacional"),
        estimate(confirm, "cobertura_binaria_mst", "M3_DDD_Cobertura", "DDD da probabilidade de ao menos um especialista"),
    ]
    with (MODELS / "resultados_ddd_estatica.json").open("w", encoding="utf-8") as handle:
        json.dump(results, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    rows = []
    for r in results:
        rows.append(
            {
                "Modelo": r["nome_modelo"],
                "Especificação": r["descricao"],
                "Outcome": r["outcome"],
                "Beta": r["beta"],
                "Erro-padrão cluster": r["se"],
                "IC 95% inferior": r["ci_95"][0],
                "IC 95% superior": r["ci_95"][1],
                "P-valor": r["p_valor"],
                "N": r["n_obs"],
                "Clusters": r["n_clusters"],
                "Média pré imediata": r["media_pre_tratamento"],
                "Média pré reserva": r["media_pre_controle"],
            }
        )
    table = pd.DataFrame(rows)
    atomic_to_csv(table, TABLES / "tabela2_ddd_estatica_resultado_primario.csv", index=False, encoding="utf-8-sig")
    (TABLES / "tabela2_ddd_estatica_resultado_primario.md").write_text(
        "# Tabela 2 — DDD estática\n\n" + table.to_markdown(index=False, floatfmt=".4f") +
        "\n\nErros-padrão agrupados por município, com correção para número finito de clusters.\n",
        encoding="utf-8",
    )
    (TABLES / "tabela2_ddd_estatica_resultado_primario.tex").write_text(table.to_latex(index=False), encoding="utf-8")
    print(f"[OK] DDD principal: beta={results[0]['beta']:.4f}, p={results[0]['p_valor']:.4f}")


if __name__ == "__main__":
    main()
