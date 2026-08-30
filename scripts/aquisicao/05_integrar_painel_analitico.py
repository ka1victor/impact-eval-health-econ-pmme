"""Constrói painéis CNES-only para a avaliação agregada do PMM-E.

Regras substantivas:
- exige as 26 competências reais; nunca carrega o último mês;
- usa todos os CNES dos municípios incluídos no quadro do ciclo 1;
- conta CO_PROFISSIONAL_SUS uma vez por município-curso-mês;
- não incorpora a lista nominal do PMM-E e não imputa carga horária;
- entrada requer seis meses anteriores de ausência observada;
- saída requer três meses posteriores consecutivos de ausência;
- presença em seis meses é calculada sobre coortes individuais maduras.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output"
AQUISICAO = OUT / "aquisicao"
MONTHLY = AQUISICAO / "cnes_mensal"

PONTE_FILE = AQUISICAO / "ponte_curso_cbo_oficial.json"
TRATAMENTO_FILE = AQUISICAO / "quadro_vagas_tratamento.parquet"
TERRITORIO_FILE = AQUISICAO / "malha_municipios_regioes_saude.parquet"

OUT_MUNI = OUT / "painel_municipio_curso_mensal.parquet"
OUT_CNES = OUT / "painel_cnes_especialidade_mensal.parquet"
OUT_REGIAO = OUT / "painel_regiao_curso_mensal.parquet"
OUT_AUDITORIA = AQUISICAO / "auditoria_painel_final.json"
OUT_RELATORIO = AQUISICAO / "relatorio_auditoria_painel.json"

COMPETENCIAS = [
    f"{ano}{mes:02d}"
    for ano, inicio, fim in ((2024, 6, 12), (2025, 1, 12), (2026, 1, 7))
    for mes in range(inicio, fim + 1)
]


def _modalidade(imediatas: pd.Series, reserva: pd.Series) -> pd.Series:
    out = pd.Series("INDEFINIDA", index=imediatas.index, dtype="string")
    out[(imediatas > 0) & (reserva == 0)] = "IMEDIATA"
    out[(imediatas == 0) & (reserva > 0)] = "RESERVA"
    out[(imediatas > 0) & (reserva > 0)] = "MISTA"
    return out


def _load_bridge() -> tuple[dict[str, list[int]], dict[int, dict[str, Any]], dict[str, Any]]:
    with PONTE_FILE.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    catalogo = {int(x["cod_curso"]): x for x in raw["catalogo_cursos"]}
    cbo_to_courses: dict[str, list[int]] = {}
    for curso, item in catalogo.items():
        for cbo in item["cbos_elegiveis"]:
            cbo_to_courses.setdefault(str(cbo).zfill(6), []).append(curso)
    return cbo_to_courses, catalogo, raw


def _prepare_treatments(
    trat: pd.DataFrame, territorio: pd.DataFrame, catalogo: dict[int, dict[str, Any]]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    trat = trat.copy()
    trat["co_cnes_7d"] = trat["co_cnes_7d"].astype("string").str.replace(r"\D", "", regex=True).str.zfill(7)
    trat["co_ibge_6d"] = trat["co_ibge_6d"].astype("string").str.replace(r"\D", "", regex=True).str.zfill(6)
    trat["cod_curso"] = trat["cod_curso"].astype(int)
    curso_sem_sobreposicao = {
        curso: not bool(item.get("sobreposicao", True)) for curso, item in catalogo.items()
    }
    trat["curso_sem_sobreposicao"] = trat["cod_curso"].map(curso_sem_sobreposicao).fillna(False)

    t_cnes = trat[
        [
            "co_cnes_7d", "co_ibge_6d", "cod_curso", "no_curso",
            "qt_vagas_imediatas", "qt_vagas_reserva", "qt_vagas_total",
            "modalidade_original", "immediate_is", "curso_sem_sobreposicao",
        ]
    ].drop_duplicates(["co_cnes_7d", "cod_curso"])
    t_cnes["amostra_principal"] = t_cnes["modalidade_original"].isin(["IMEDIATA", "RESERVA"])

    t_muni = (
        trat.groupby(["co_ibge_6d", "cod_curso"], as_index=False)
        .agg(
            no_curso=("no_curso", "first"),
            qt_vagas_imediatas=("qt_vagas_imediatas", "sum"),
            qt_vagas_reserva=("qt_vagas_reserva", "sum"),
            qt_vagas_total=("qt_vagas_total", "sum"),
            n_cnes_ofertantes=("co_cnes_7d", "nunique"),
            curso_sem_sobreposicao=("curso_sem_sobreposicao", "first"),
        )
    )
    t_muni["modalidade_ms"] = _modalidade(t_muni["qt_vagas_imediatas"], t_muni["qt_vagas_reserva"])
    t_muni["immediate_ms"] = (t_muni["modalidade_ms"] == "IMEDIATA").astype(int)
    t_muni["amostra_principal"] = t_muni["modalidade_ms"].isin(["IMEDIATA", "RESERVA"])
    t_muni["amostra_confirmatoria"] = t_muni["amostra_principal"] & t_muni["curso_sem_sobreposicao"]

    for sample_col, out_col in (
        ("amostra_principal", "within_muni_var_ampliada"),
        ("amostra_confirmatoria", "within_muni_var_confirmatoria"),
    ):
        nmod = t_muni.loc[t_muni[sample_col]].groupby("co_ibge_6d")["immediate_ms"].nunique()
        valid = set(nmod[nmod > 1].index)
        t_muni[out_col] = t_muni["co_ibge_6d"].isin(valid)

    terr_cols = [
        "co_ibge_6d", "co_ibge_7d", "no_municipio", "sg_uf", "macro_regiao_saude",
        "no_regiao_saude", "ivs_2010", "ivs_categoria", "populacao_2010",
    ]
    terr = territorio[terr_cols].drop_duplicates("co_ibge_6d").copy()
    terr["co_ibge_6d"] = terr["co_ibge_6d"].astype("string").str.zfill(6)
    terr["region_id"] = terr["sg_uf"].astype("string") + "|" + terr["no_regiao_saude"].astype("string")
    t_muni = t_muni.merge(terr, on="co_ibge_6d", how="left", validate="many_to_one")

    t_regiao = (
        t_muni.dropna(subset=["region_id"])
        .groupby(["region_id", "sg_uf", "no_regiao_saude", "cod_curso"], as_index=False)
        .agg(
            no_curso=("no_curso", "first"),
            qt_vagas_imediatas=("qt_vagas_imediatas", "sum"),
            qt_vagas_reserva=("qt_vagas_reserva", "sum"),
            qt_vagas_total=("qt_vagas_total", "sum"),
            curso_sem_sobreposicao=("curso_sem_sobreposicao", "first"),
        )
    )
    t_regiao["modalidade_rs"] = _modalidade(t_regiao["qt_vagas_imediatas"], t_regiao["qt_vagas_reserva"])
    t_regiao["immediate_rs"] = (t_regiao["modalidade_rs"] == "IMEDIATA").astype(int)
    t_regiao["amostra_principal"] = t_regiao["modalidade_rs"].isin(["IMEDIATA", "RESERVA"])
    return t_muni, t_cnes, t_regiao


def _expand_courses(df: pd.DataFrame, cbo_to_courses: dict[str, list[int]]) -> pd.DataFrame:
    out = df.copy()
    out["co_cbo_6d"] = out["co_cbo_6d"].astype("string").str.replace(r"\D", "", regex=True).str.zfill(6)
    out["cod_curso"] = out["co_cbo_6d"].map(cbo_to_courses)
    out = out.dropna(subset=["cod_curso"]).explode("cod_curso")
    out["cod_curso"] = out["cod_curso"].astype(int)
    return out


def _balanced_skeleton(keys: pd.DataFrame) -> pd.DataFrame:
    months = pd.DataFrame({"competencia": COMPETENCIAS})
    return keys.assign(_join=1).merge(months.assign(_join=1), on="_join").drop(columns="_join")


def _add_time(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.copy()
    panel["ano"] = panel["competencia"].str[:4].astype(int)
    panel["mes"] = panel["competencia"].str[4:].astype(int)
    panel["post_t"] = (panel["competencia"] >= "202508").astype(int)
    panel["mes_transicao"] = (panel["competencia"] == "202507").astype(int)
    return panel


def _sets_by_cell(long: pd.DataFrame, cell_cols: list[str]) -> dict[tuple[Any, ...], list[set[str]]]:
    month_index = {m: i for i, m in enumerate(COMPETENCIAS)}
    cells: dict[tuple[Any, ...], list[set[str]]] = {}
    for key, part in long.groupby(cell_cols, sort=False):
        if not isinstance(key, tuple):
            key = (key,)
        months = [set() for _ in COMPETENCIAS]
        for comp, pmonth in part.groupby("competencia", sort=False):
            months[month_index[str(comp)]] = set(pmonth["co_profissional_sus"].astype(str))
        cells[key] = months
    return cells


def _longitudinal_id_diagnostics(long: pd.DataFrame) -> dict[str, Any]:
    """Quantifica continuidade observada sem alegar validação externa da chave."""
    monthly: dict[str, set[tuple[str, int, str]]] = {}
    for comp, part in long.groupby("competencia", sort=False):
        monthly[str(comp)] = set(
            part[["co_ibge_6d", "cod_curso", "co_profissional_sus"]]
            .itertuples(index=False, name=None)
        )
    adjacent: list[dict[str, Any]] = []
    for previous, current in zip(COMPETENCIAS[:-1], COMPETENCIAS[1:], strict=True):
        prev_set = monthly.get(previous, set())
        curr_set = monthly.get(current, set())
        overlap = len(prev_set & curr_set)
        adjacent.append(
            {
                "de": previous,
                "para": current,
                "sobrevivencia_sobre_mes_anterior_pct": 100 * overlap / len(prev_set) if prev_set else None,
                "participacao_de_ids_ja_observados_pct": 100 * overlap / len(curr_set) if curr_set else None,
            }
        )
    survival = [x["sobrevivencia_sobre_mes_anterior_pct"] for x in adjacent if x["sobrevivencia_sobre_mes_anterior_pct"] is not None]
    carryover = [x["participacao_de_ids_ja_observados_pct"] for x in adjacent if x["participacao_de_ids_ja_observados_pct"] is not None]
    return {
        "campo": "CO_PROFISSIONAL_SUS",
        "escopo": "continuidade de pessoa-município-curso entre competências adjacentes",
        "mediana_sobrevivencia_sobre_mes_anterior_pct": float(np.median(survival)),
        "min_sobrevivencia_sobre_mes_anterior_pct": float(np.min(survival)),
        "mediana_participacao_de_ids_ja_observados_pct": float(np.median(carryover)),
        "min_participacao_de_ids_ja_observados_pct": float(np.min(carryover)),
        "pares_adjacentes": adjacent,
        "limite": (
            "Continuidade empírica elevada é compatível com chave longitudinal estável, "
            "mas não substitui documentação externa do identificador nem distingue mudança real de cadastro."
        ),
    }


def _build_municipal_panel(long: pd.DataFrame, treatment: pd.DataFrame) -> pd.DataFrame:
    skeleton = _balanced_skeleton(treatment)
    active = _sets_by_cell(long, ["co_ibge_6d", "cod_curso"])
    records: list[dict[str, Any]] = []
    for row in treatment[["co_ibge_6d", "cod_curso"]].itertuples(index=False):
        key = (row.co_ibge_6d, row.cod_curso)
        months = active.get(key, [set() for _ in COMPETENCIAS])
        entries: list[set[str] | None] = []
        exits: list[set[str] | None] = []
        for idx, current in enumerate(months):
            prior = set().union(*months[idx - 6:idx]) if idx >= 6 else None
            future = set().union(*months[idx + 1:idx + 4]) if idx + 3 < len(months) else None
            entries.append(current - prior if prior is not None else None)
            exits.append(current - future if future is not None else None)
        for idx, comp in enumerate(COMPETENCIAS):
            ent = entries[idx]
            ex = exits[idx]
            mature6 = ent is not None and idx + 6 < len(months)
            present6 = len(ent & months[idx + 6]) if mature6 else np.nan
            n_ent = len(ent) if ent is not None else np.nan
            n_exit = len(ex) if ex is not None else np.nan
            records.append(
                {
                    "co_ibge_6d": row.co_ibge_6d,
                    "cod_curso": row.cod_curso,
                    "competencia": comp,
                    "especialistas_mst": len(months[idx]),
                    "cobertura_binaria_mst": int(bool(months[idx])),
                    "n_entradas_6m": n_ent,
                    "n_saidas_confirmadas_3m": n_exit,
                    "saldo_liquido": n_ent - n_exit if not (pd.isna(n_ent) or pd.isna(n_exit)) else np.nan,
                    "churn_bruto": n_ent + n_exit if not (pd.isna(n_ent) or pd.isna(n_exit)) else np.nan,
                    "entrantes_elegiveis_6m": n_ent if mature6 else np.nan,
                    "entrantes_presentes_6m": present6,
                    "coorte_6m_madura": bool(mature6),
                    "entrada_observavel": ent is not None,
                    "saida_observavel": ex is not None,
                }
            )
    metrics = pd.DataFrame(records)
    panel = skeleton.merge(metrics, on=["co_ibge_6d", "cod_curso", "competencia"], how="left", validate="one_to_one")
    panel["treat_x_post"] = panel["immediate_ms"] * (panel["competencia"] >= "202508").astype(int)
    return _add_time(panel)


def _build_stock_panel(
    long: pd.DataFrame, treatment: pd.DataFrame, key_cols: list[str], outcome: str
) -> pd.DataFrame:
    skeleton = _balanced_skeleton(treatment)
    stock = (
        long.groupby(key_cols + ["competencia"], as_index=False)["co_profissional_sus"]
        .nunique()
        .rename(columns={"co_profissional_sus": outcome})
    )
    panel = skeleton.merge(stock, on=key_cols + ["competencia"], how="left", validate="one_to_one")
    panel[outcome] = panel[outcome].fillna(0).astype(int)
    return _add_time(panel)


def _require_months() -> list[Path]:
    paths = [MONTHLY / f"cnes_vinculos_medicos_{comp}.parquet" for comp in COMPETENCIAS]
    missing = [p.name for p in paths if not p.exists()]
    if missing:
        raise RuntimeError(f"Painel CNES incompleto; competências ausentes: {', '.join(missing)}")
    return paths


def main() -> None:
    print("=== Integração CNES-only: município-curso-mês ===")
    paths = _require_months()
    cbo_to_courses, catalogo, bridge_raw = _load_bridge()
    trat = pd.read_parquet(TRATAMENTO_FILE)
    territorio = pd.read_parquet(TERRITORIO_FILE)
    t_muni, t_cnes, t_regiao = _prepare_treatments(trat, territorio, catalogo)

    target_munis = set(t_muni["co_ibge_6d"])
    target_cnes = set(t_cnes["co_cnes_7d"])
    target_regions = set(t_regiao["region_id"])
    terr_map = territorio[["co_ibge_6d", "sg_uf", "no_regiao_saude"]].drop_duplicates("co_ibge_6d").copy()
    terr_map["co_ibge_6d"] = terr_map["co_ibge_6d"].astype("string").str.zfill(6)
    terr_map["region_id"] = terr_map["sg_uf"].astype("string") + "|" + terr_map["no_regiao_saude"].astype("string")
    muni_to_region = terr_map.set_index("co_ibge_6d")["region_id"].to_dict()

    muni_keys = t_muni[["co_ibge_6d", "cod_curso"]].drop_duplicates()
    cnes_keys = t_cnes[["co_cnes_7d", "cod_curso"]].drop_duplicates()
    reg_keys = t_regiao[["region_id", "cod_curso"]].drop_duplicates()

    muni_parts: list[pd.DataFrame] = []
    cnes_parts: list[pd.DataFrame] = []
    reg_parts: list[pd.DataFrame] = []
    monthly_audit: list[dict[str, Any]] = []
    required_cols = ["competencia", "co_cnes_7d", "co_profissional_sus", "co_cbo_6d", "co_municipio_gestor"]

    for comp, path in zip(COMPETENCIAS, paths, strict=True):
        month = pd.read_parquet(path, columns=required_cols)
        if set(month["competencia"].astype(str).unique()) != {comp}:
            raise RuntimeError(f"Competência interna incompatível em {path.name}")
        month["co_municipio_gestor"] = month["co_municipio_gestor"].astype("string").str.replace(r"\D", "", regex=True).str.zfill(6)
        month["co_cnes_7d"] = month["co_cnes_7d"].astype("string").str.replace(r"\D", "", regex=True).str.zfill(7)
        prof = month["co_profissional_sus"].astype("string").str.strip()
        valid_prof = prof.notna() & ~prof.isin(["", "nan", "None", "<NA>"])
        invalid_prof = int((~valid_prof).sum())
        month = month.loc[valid_prof].copy()
        month["co_profissional_sus"] = prof.loc[valid_prof]
        expanded = _expand_courses(month, cbo_to_courses)

        muni = expanded.loc[expanded["co_municipio_gestor"].isin(target_munis)].rename(columns={"co_municipio_gestor": "co_ibge_6d"})
        muni = muni.merge(muni_keys, on=["co_ibge_6d", "cod_curso"], how="inner")
        muni = muni[["competencia", "co_ibge_6d", "cod_curso", "co_cnes_7d", "co_profissional_sus"]]
        before_muni = len(muni)
        muni = muni.drop_duplicates(["competencia", "co_ibge_6d", "cod_curso", "co_profissional_sus"])
        muni_parts.append(muni)

        cnes = expanded.loc[expanded["co_cnes_7d"].isin(target_cnes)]
        cnes = cnes.merge(cnes_keys, on=["co_cnes_7d", "cod_curso"], how="inner")
        cnes = cnes[["competencia", "co_cnes_7d", "cod_curso", "co_profissional_sus"]].drop_duplicates()
        cnes_parts.append(cnes)

        expanded["region_id"] = expanded["co_municipio_gestor"].map(muni_to_region)
        reg = expanded.loc[expanded["region_id"].isin(target_regions)]
        reg = reg.merge(reg_keys, on=["region_id", "cod_curso"], how="inner")
        reg = reg[["competencia", "region_id", "cod_curso", "co_profissional_sus"]].drop_duplicates()
        reg_parts.append(reg)

        monthly_audit.append(
            {
                "competencia": comp,
                "linhas_fonte": int(len(month)),
                "ids_profissionais_invalidos_descartados": invalid_prof,
                "registros_municipais_antes_deduplicacao": int(before_muni),
                "profissionais_municipio_curso": int(len(muni)),
                "duplicacoes_intramunicipais_removidas": int(before_muni - len(muni)),
                "cnes_observados_nos_municipios": int(expanded.loc[expanded["co_municipio_gestor"].isin(target_munis), "co_cnes_7d"].nunique()),
            }
        )
        print(f"  {comp}: {len(muni):,} profissionais município-curso após deduplicação")

    long_muni = pd.concat(muni_parts, ignore_index=True)
    long_cnes = pd.concat(cnes_parts, ignore_index=True)
    long_reg = pd.concat(reg_parts, ignore_index=True)
    id_diagnostics = _longitudinal_id_diagnostics(long_muni)

    panel_muni = _build_municipal_panel(long_muni, t_muni)
    panel_cnes = _build_stock_panel(long_cnes, t_cnes, ["co_cnes_7d", "cod_curso"], "especialistas_ist")
    panel_reg = _build_stock_panel(long_reg, t_regiao, ["region_id", "cod_curso"], "especialistas_rst")

    checks = {
        "26_competencias_presentes": len(paths) == 26,
        "painel_municipal_balanceado": len(panel_muni) == len(t_muni) * 26 and not panel_muni.duplicated(["co_ibge_6d", "cod_curso", "competencia"]).any(),
        "painel_cnes_balanceado": len(panel_cnes) == len(t_cnes) * 26,
        "painel_regional_balanceado": len(panel_reg) == len(t_regiao) * 26,
        "nenhuma_lista_nominal_incorporada": True,
        "estoque_municipal_nao_negativo": bool((panel_muni["especialistas_mst"] >= 0).all()),
        "censura_entradas_primeiros_6_meses": bool(panel_muni.loc[panel_muni["competencia"] < "202412", "n_entradas_6m"].isna().all()),
        "censura_saidas_ultimos_3_meses": bool(panel_muni.loc[panel_muni["competencia"] > "202604", "n_saidas_confirmadas_3m"].isna().all()),
    }
    if not all(checks.values()):
        failed = [k for k, ok in checks.items() if not ok]
        raise RuntimeError(f"Portão de integridade falhou: {', '.join(failed)}")

    panel_muni.to_parquet(OUT_MUNI, index=False)
    panel_cnes.to_parquet(OUT_CNES, index=False)
    panel_reg.to_parquet(OUT_REGIAO, index=False)

    audit = {
        "status": "APROVADO_PARA_ESTIMACAO",
        "data_execucao": dt.datetime.now().isoformat(timespec="seconds"),
        "desenho": "CNES-only; universo municipal completo; sem identificação nominal de bolsistas",
        "ponte": {
            "arquivo": str(PONTE_FILE.relative_to(ROOT)).replace("\\", "/"),
            "versao": bridge_raw.get("versao_ponte"),
            "status_substantivo": bridge_raw.get("status_substantivo", "OPERACIONAL_NAO_OFICIAL"),
            "cursos_sem_sobreposicao": sorted(int(k) for k, v in catalogo.items() if not v.get("sobreposicao", True)),
        },
        "cobertura": {"inicio": COMPETENCIAS[0], "fim": COMPETENCIAS[-1], "n_competencias": len(COMPETENCIAS)},
        "amostra": {
            "municipios": int(t_muni["co_ibge_6d"].nunique()),
            "celulas_municipio_curso": int(len(t_muni)),
            "celulas_confirmatorias": int(t_muni["amostra_confirmatoria"].sum()),
            "municipios_identificadores_confirmatorios": int(t_muni.loc[t_muni["within_muni_var_confirmatoria"], "co_ibge_6d"].nunique()),
            "cnes_ofertantes": int(t_cnes["co_cnes_7d"].nunique()),
            "cnes_observados_em_todos_os_municipios_max_mensal": int(max(x["cnes_observados_nos_municipios"] for x in monthly_audit)),
        },
        "definicoes": {
            "estoque": "CO_PROFISSIONAL_SUS distinto em qualquer CNES do município, dentro dos CBOs operacionais do curso",
            "entrada": "presente em t e ausente nos seis meses anteriores observados",
            "saida": "presente em t e ausente nos três meses posteriores observados",
            "presenca_6m": "entrante elegível em t observado no mesmo município-curso em t+6",
            "zero": "competência presente sem profissional elegível na célula",
            "ausente": "métrica censurada por janela longitudinal insuficiente",
        },
        "checks": checks,
        "auditoria_mensal": monthly_audit,
        "diagnostico_identificador_longitudinal": id_diagnostics,
    }
    for path in (OUT_AUDITORIA, OUT_RELATORIO):
        with path.open("w", encoding="utf-8") as handle:
            json.dump(audit, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
    print(f"[OK] Painel municipal: {OUT_MUNI} ({len(panel_muni):,} linhas)")
    print(f"[OK] Portão de integridade: {audit['status']}")


if __name__ == "__main__":
    main()
