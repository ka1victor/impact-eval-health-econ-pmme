"""Avalia se imediata versus reserva produz exposição administrativa distinta.

O portão é estimado no mesmo grão município-curso e na mesma amostra
confirmatória que identifica a DDD. Homologação é tratada como resultado de
candidatura, não como entrada em exercício.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from model_utils import atomic_to_csv, fit_absorbed_ols, result_for


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "avaliacao_impacto"
REL = OUT / "relatorios"
TAB = OUT / "tabelas"
TRATAMENTO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
PONTE = ROOT / "output" / "aquisicao" / "ponte_curso_cbo_oficial.json"
HOMOLOGADOS = ROOT / "data" / "raw" / "pmm_e" / "2025_ciclo1_chamada1_homologados.xlsx"
ALOCACAO = ROOT / "data" / "raw" / "aquisicao" / "vagas" / "2025_ciclo1_chamada1_alocacao_retificada.xlsx"


def norm_cnes(value: Any) -> str:
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(7) if digits else ""


def course_id(value: Any) -> int | None:
    match = re.match(r"^(\d{1,2})", str(value).strip())
    return int(match.group(1)) if match else None


def main() -> None:
    REL.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    trat = pd.read_parquet(TRATAMENTO).copy()
    with PONTE.open("r", encoding="utf-8") as handle:
        bridge = json.load(handle)
    unambiguous = {int(x["cod_curso"]) for x in bridge["catalogo_cursos"] if not x.get("sobreposicao", True)}

    hom = pd.read_excel(HOMOLOGADOS)
    hom["co_cnes_7d"] = hom["CNES"].map(norm_cnes)
    hom["cod_curso"] = hom["CURSO"].map(course_id)
    hom_counts = hom.groupby(["co_cnes_7d", "cod_curso"], as_index=False).size().rename(columns={"size": "n_homologados"})

    aloc = pd.read_excel(ALOCACAO)
    aloc["co_cnes_7d"] = aloc["CNES"].map(norm_cnes)
    aloc["cod_curso"] = aloc["CURSO"].map(course_id)
    col = next(c for c in aloc.columns if "ALOCA" in c)
    aloc = aloc[aloc[col].astype("string").str.contains("CONFIRMADO", case=False, na=False)]
    aloc_counts = aloc.groupby(["co_cnes_7d", "cod_curso"], as_index=False).size().rename(columns={"size": "n_alocados_confirmados"})

    cell = trat.merge(hom_counts, on=["co_cnes_7d", "cod_curso"], how="left").merge(
        aloc_counts, on=["co_cnes_7d", "cod_curso"], how="left"
    )
    cell[["n_homologados", "n_alocados_confirmados"]] = cell[["n_homologados", "n_alocados_confirmados"]].fillna(0)
    muni = (
        cell.groupby(["co_ibge_6d", "cod_curso"], as_index=False)
        .agg(
            qt_vagas_imediatas=("qt_vagas_imediatas", "sum"),
            qt_vagas_reserva=("qt_vagas_reserva", "sum"),
            qt_vagas_total=("qt_vagas_total", "sum"),
            n_alocados_confirmados=("n_alocados_confirmados", "sum"),
            n_homologados=("n_homologados", "sum"),
        )
    )
    muni["modalidade"] = "MISTA"
    muni.loc[(muni["qt_vagas_imediatas"] > 0) & (muni["qt_vagas_reserva"] == 0), "modalidade"] = "IMEDIATA"
    muni.loc[(muni["qt_vagas_imediatas"] == 0) & (muni["qt_vagas_reserva"] > 0), "modalidade"] = "RESERVA"
    muni["immediate_ms"] = (muni["modalidade"] == "IMEDIATA").astype(int)
    muni["curso_sem_sobreposicao"] = muni["cod_curso"].isin(unambiguous)
    muni["tem_alocado"] = (muni["n_alocados_confirmados"] > 0).astype(int)
    muni["tem_homologado"] = (muni["n_homologados"] > 0).astype(int)
    sample = muni[muni["modalidade"].isin(["IMEDIATA", "RESERVA"]) & muni["curso_sem_sobreposicao"]].copy()
    valid_munis = sample.groupby("co_ibge_6d")["immediate_ms"].nunique()
    sample = sample[sample["co_ibge_6d"].isin(valid_munis[valid_munis > 1].index)].copy()
    sample["municipio_fe"] = sample["co_ibge_6d"].astype(str)
    sample["curso_fe"] = sample["cod_curso"].astype(str)

    # Nível Celular (CNES x Curso) - Unidade Canônica de Oferta
    cell["tem_alocado"] = (cell["n_alocados_confirmados"] > 0).astype(int)
    cell["tem_homologado"] = (cell["n_homologados"] > 0).astype(int)
    cell_sample = cell[cell["modalidade_original"].isin(["IMEDIATA", "RESERVA"])].copy()
    cell_sample["immediate_is"] = (cell_sample["modalidade_original"] == "IMEDIATA").astype(int)
    cell_sample["curso_fe"] = cell_sample["cod_curso"].astype(str)
    cell_sample["uf_fe"] = cell_sample["sg_uf"].astype(str)

    cell_i = cell_sample[cell_sample["immediate_is"] == 1]
    cell_r = cell_sample[cell_sample["immediate_is"] == 0]
    raw_aloc_diff = float(cell_i["tem_alocado"].mean() - cell_r["tem_alocado"].mean())
    raw_hom_diff = float(cell_i["tem_homologado"].mean() - cell_r["tem_homologado"].mean())

    rows: list[dict[str, Any]] = []
    model_results: dict[str, Any] = {}
    for outcome, label in (
        ("tem_alocado", "Alocação confirmada para início (Célula CNES-Curso)"),
        ("tem_homologado", "Candidatura homologada (Célula CNES-Curso)"),
    ):
        raw_i = float(cell_i[outcome].mean())
        raw_r = float(cell_r[outcome].mean())
        model, diag = fit_absorbed_ols(cell_sample, outcome, ["immediate_is"], ["curso_fe", "uf_fe"], "co_ibge_6d")
        adjusted = result_for(model, "immediate_is")
        model_results[outcome] = {**adjusted, "diagnosticos": diag}
        rows.append(
            {
                "Nível": "Célula CNES-Curso",
                "Métrica": label,
                "Taxa imediata (%)": round(100 * raw_i, 2),
                "Taxa reserva (%)": round(100 * raw_r, 2),
                "Diferença bruta (p.p.)": round(100 * (raw_i - raw_r), 2),
                "Diferença ajustada FE (p.p.)": round(100 * adjusted["beta"], 2),
                "Erro-padrão ajustado (p.p.)": round(100 * adjusted["se"], 2),
                "P-valor ajustado": adjusted["p_valor"],
                "N células": len(cell_sample),
                "N municípios": cell_sample["co_ibge_6d"].nunique(),
            }
        )

    for outcome, label in (
        ("tem_alocado", "Alocação confirmada (Amostra DDD Município-Curso)"),
        ("tem_homologado", "Candidatura homologada (Amostra DDD Município-Curso)"),
    ):
        raw_i = float(sample.loc[sample["immediate_ms"] == 1, outcome].mean())
        raw_r = float(sample.loc[sample["immediate_ms"] == 0, outcome].mean())
        model, diag = fit_absorbed_ols(sample, outcome, ["immediate_ms"], ["municipio_fe", "curso_fe"], "co_ibge_6d")
        adjusted = result_for(model, "immediate_ms")
        model_results[f"{outcome}_muni_ddd"] = {**adjusted, "diagnosticos": diag}
        rows.append(
            {
                "Nível": "Município-Curso (DDD)",
                "Métrica": label,
                "Taxa imediata (%)": round(100 * raw_i, 2),
                "Taxa reserva (%)": round(100 * raw_r, 2),
                "Diferença bruta (p.p.)": round(100 * (raw_i - raw_r), 2),
                "Diferença ajustada FE (p.p.)": round(100 * adjusted["beta"], 2),
                "Erro-padrão ajustado (p.p.)": round(100 * adjusted["se"], 2),
                "P-valor ajustado": adjusted["p_valor"],
                "N células": len(sample),
                "N municípios": sample["co_ibge_6d"].nunique(),
            }
        )

    table = pd.DataFrame(rows)
    atomic_to_csv(table, TAB / "tabela_portao_relevancia.csv", index=False, encoding="utf-8-sig")

    # A decisão deve usar exatamente o grão, a amostra e a variação que
    # identificam a DDD. O contraste celular amplo fica apenas como descrição:
    # ele não substitui um primeiro estágio na amostra município-curso.
    first_stage = model_results["tem_alocado_muni_ddd"]
    relevant_same_sample = first_stage["beta"] > 0 and first_stage["p_valor"] < 0.10
    status = "APROVADO" if relevant_same_sample else "NAO_APROVADO"
    report = {
        "status_portao": status,
        "criterio_decisao": (
            "associação ajustada positiva entre modalidade imediata e alocação confirmada, "
            "com p < 0,10, no mesmo grão município-curso e na mesma amostra que identifica a DDD"
        ),
        "nota_pre_especificacao": (
            "O roadmap anterior exigia relevância substantiva, mas não registrava limiar numérico. "
            "A regra acima é um portão conservador de execução, não uma pré-especificação ex ante."
        ),
        "diferenca_celular_alocacao_pp": round(100 * raw_aloc_diff, 2),
        "diferenca_celular_homologacao_pp": round(100 * raw_hom_diff, 2),
        "n_celulas_universo": int(len(cell_sample)),
        "n_municipios_universo": int(cell_sample["co_ibge_6d"].nunique()),
        "amostra_ddd_municipio_curso": {
            "n_celulas": int(len(sample)),
            "n_municipios": int(sample["co_ibge_6d"].nunique()),
        },
        "resultados_ajustados": model_results,
        "tabela_resumo": table.to_dict(orient="records"),
        "interpretacao": (
            f"O portão foi {status}. No universo CNES-curso, a diferença bruta foi "
            f"+{raw_aloc_diff*100:.2f} p.p.; isso não se transporta para a amostra identificadora. "
            f"Na amostra município-curso da DDD, a associação ajustada com alocação foi "
            f"{first_stage['beta']*100:+.2f} p.p. (p={first_stage['p_valor']:.4f}). "
            "Homologação registra candidatura homologada, não entrada em exercício."
        ),
    }
    with (REL / "01_relatorio_portao_relevancia.json").open("w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(
        f"[OK] Portão avaliado: {status}; primeiro estágio na amostra DDD "
        f"{first_stage['beta']*100:+.2f} p.p. (p={first_stage['p_valor']:.4f})."
    )


if __name__ == "__main__":
    main()
