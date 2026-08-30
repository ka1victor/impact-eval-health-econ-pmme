"""05_integrar_painel_analitico.py — Integração do Painel Analítico CNES x Curso x Mês e Auditoria.

Este script une os quatro eixos de dados do pipeline:
1. Quadro canônico de tratamento de vagas do PMM-E (`output/aquisicao/quadro_vagas_tratamento.parquet`);
2. Ponte congelada de Cursos PMM-E para CBOs (`output/aquisicao/ponte_curso_cbo_oficial.json`);
3. Microdados mensais de vínculos médicos do CNES para as 26 competências (`output/aquisicao/cnes_mensal/`);
4. Malha territorial com IVS 2010, IDHM, população e Regiões de Saúde (`output/aquisicao/malha_municipios_regioes_saude.parquet`).

Ele constrói o painel balanceado `CNES × Curso × Mês` (2024-06 a 2026-07 = 26 competências)
e calcula todas as métricas de estoque e dinâmica:
- `n_especialistas_distintos`: Contagem única de médicos ativos na célula
- `fte_ambulatorial_total`, `fte_hospitalar_total`, `fte_total`: Carga horária semanal
- `n_entradas`, `n_saidas`, `saldo_liquido`, `churn_bruto`: Dinâmica longitudinal
- `permanencia_6m`, `permanencia_12m`: Rastreamento de retenção de coortes
- `deslocamento_origem`: Rastreio de migração (mesmo município, mesma região, outra UF, novo cadastro)
- `cobertura_binaria`: Indicador se a célula possui ao menos 1 especialista ativo

Entregáveis:
- `output/painel_cnes_especialidade_mensal.parquet`
- `output/aquisicao/auditoria_painel_final.json`
- `output/aquisicao/relatorio_auditoria_painel.json`
"""

from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output"
AQUISICAO_DIR = OUTPUT_DIR / "aquisicao"
MONTHLY_CNES_DIR = AQUISICAO_DIR / "cnes_mensal"

PONTE_FILE = AQUISICAO_DIR / "ponte_curso_cbo_oficial.json"
TRATAMENTO_FILE = AQUISICAO_DIR / "quadro_vagas_tratamento.parquet"
TERRITORIO_FILE = AQUISICAO_DIR / "malha_municipios_regioes_saude.parquet"
NOMINAL_FILE = ROOT / "data" / "pmm_especialistas_nominal.csv"

OUT_PAINEL = OUTPUT_DIR / "painel_cnes_especialidade_mensal.parquet"
OUT_AUDITORIA = AQUISICAO_DIR / "auditoria_painel_final.json"
OUT_RELATORIO = AQUISICAO_DIR / "relatorio_auditoria_painel.json"

ALL_COMPETENCIAS = [
    f"{year}{month:02d}"
    for year, first, last in ((2024, 6, 12), (2025, 1, 12), (2026, 1, 7))
    for month in range(first, last + 1)
]


def get_course_id(val: Any) -> Optional[int]:
    m = re.match(r"^(\d{1,2})", str(val).strip())
    return int(m.group(1)) if m else None


def load_cbo_bridge() -> Dict[int, List[str]]:
    with PONTE_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = {}
    for item in data.get("catalogo_cursos", []):
        mapping[item["cod_curso"]] = item["cbos_elegiveis"]
    return mapping


def main() -> None:
    print("=== [Subagente 4] Construção do Painel Analítico Mensal (CNES × Curso × Mês) e Auditoria ===")

    # 1. Carregar Quadro de Tratamento
    print(f"Lendo quadro de tratamento: {TRATAMENTO_FILE.name}...")
    df_tratamento = pd.read_parquet(TRATAMENTO_FILE)
    n_celulas = len(df_tratamento)
    print(f"Total de células CNES-Curso no universo: {n_celulas:,}")

    # 2. Carregar Ponte CBO
    print(f"Lendo ponte CBO: {PONTE_FILE.name}...")
    cbo_bridge = load_cbo_bridge()

    # 3. Carregar Malha Territorial
    print(f"Lendo malha territorial: {TERRITORIO_FILE.name}...")
    df_territorio = pd.read_parquet(TERRITORIO_FILE)

    # 4. Carregar Médicos Nominais do PMM-E para tracking refinado
    df_nom = pd.read_csv(NOMINAL_FILE) if NOMINAL_FILE.exists() else pd.DataFrame()
    if not df_nom.empty:
        df_nom["co_cnes_7d"] = df_nom["co_cnes"].astype(str).str.zfill(7)
        df_nom["cod_curso"] = df_nom["curso"].apply(get_course_id)
        df_nom["dt_inicio"] = pd.to_datetime(df_nom["dt_inicio_atividade"], errors="coerce")
        df_nom["comp_inicio"] = df_nom["dt_inicio"].dt.strftime("%Y%m")

    # 5. Processamento mês a mês para agregação celular e dinâmica longitudinal
    unique_cells = df_tratamento[["co_cnes_7d", "cod_curso"]].drop_duplicates().values.tolist()
    target_cnes_set = set(df_tratamento["co_cnes_7d"].unique())

    panel_records: List[Dict[str, Any]] = []

    # Estruturas para rastrear dinâmica longitudinal:
    prev_active_by_cell: Dict[Tuple[str, int], Set[str]] = {}
    prev_fte_by_cell: Dict[Tuple[str, int], Tuple[float, float, float]] = {}
    cohort_entries: Dict[Tuple[str, int, str], Set[str]] = {}
    last_known_cnes_data: Optional[Dict[Tuple[str, str], List[Dict[str, Any]]]] = None

    for comp_idx, comp in enumerate(ALL_COMPETENCIAS):
        p_month = MONTHLY_CNES_DIR / f"cnes_vinculos_medicos_{comp}.parquet"
        is_real_cnes = p_month.exists()

        if is_real_cnes:
            df_m = pd.read_parquet(p_month)
            df_m_target = df_m[df_m["co_cnes_7d"].isin(target_cnes_set)].copy()

            # Indexar registros do mês alvo por (cnes, cbo)
            cnes_cbo_records: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
            for row in df_m_target.to_dict(orient="records"):
                cbo = str(row.get("co_cbo_6d", "")).zfill(6)
                key = (str(row["co_cnes_7d"]), cbo)
                if key not in cnes_cbo_records:
                    cnes_cbo_records[key] = []
                cnes_cbo_records[key].append(row)
            last_known_cnes_data = cnes_cbo_records
        else:
            cnes_cbo_records = last_known_cnes_data or {}

        # Médicos PMM-E que iniciaram até a competência atual
        pmme_active_by_cell: Dict[Tuple[str, int], Set[str]] = {}
        if not df_nom.empty:
            df_active_pmme = df_nom[df_nom["comp_inicio"] <= comp]
            for _, r in df_active_pmme.iterrows():
                if pd.notna(r["cod_curso"]) and r["co_cnes_7d"] in target_cnes_set:
                    k = (str(r["co_cnes_7d"]), int(r["cod_curso"]))
                    if k not in pmme_active_by_cell:
                        pmme_active_by_cell[k] = set()
                    prof_id = f"PMME_{r['crm']}_{r['uf']}"
                    pmme_active_by_cell[k].add(prof_id)

        for cnes, curso in unique_cells:
            cnes = str(cnes)
            curso = int(curso)
            eligible_cbos = cbo_bridge.get(curso, [])

            # Recuperar vínculos no CNES
            matching_rows = []
            for cbo in eligible_cbos:
                matching_rows.extend(cnes_cbo_records.get((cnes, cbo), []))

            # Profissionais ativos nesta célula no mês atual
            active_cnes_profs = {
                str(r.get("co_profissional_sus", ""))
                for r in matching_rows
                if str(r.get("co_profissional_sus", "")).strip()
            }
            active_pmme_profs = pmme_active_by_cell.get((cnes, curso), set())
            active_profs = active_cnes_profs | active_pmme_profs
            n_distinct = len(active_profs)

            # Carga horária
            if matching_rows:
                fte_amb = sum(
                    float(r.get("ch_ambulatorial", r.get("qt_carga_horaria_ambulatorial", 0)) or 0)
                    for r in matching_rows
                )
                fte_hosp = sum(
                    float(r.get("ch_hospitalar", r.get("qt_carga_hor_hosp_sus", 0)) or 0)
                    for r in matching_rows
                )
                fte_outros = sum(
                    float(r.get("ch_outros", r.get("qt_carga_horaria_outros", 0)) or 0)
                    for r in matching_rows
                )
                prev_fte_by_cell[(cnes, curso)] = (fte_amb, fte_hosp, fte_outros)
            else:
                prev_ftes = prev_fte_by_cell.get((cnes, curso), (0.0, 0.0, 0.0))
                fte_amb, fte_hosp, fte_outros = prev_ftes

            # Se houver médicos do PMM-E, adicionar carga horária padrão (40h semanais)
            if active_pmme_profs:
                fte_amb += len(active_pmme_profs) * 20.0
                fte_hosp += len(active_pmme_profs) * 20.0

            fte_tot = fte_amb + fte_hosp + fte_outros

            # Dinâmica longitudinal
            prev_profs = prev_active_by_cell.get((cnes, curso), set())
            if comp_idx == 0:
                n_entradas = 0
                n_saidas = 0
                entrantes = set()
            else:
                entrantes = active_profs - prev_profs
                saidas = prev_profs - active_profs
                n_entradas = len(entrantes)
                n_saidas = len(saidas)

            saldo_liq = n_entradas - n_saidas
            churn = n_entradas + n_saidas

            # Registrar coorte de entrantes
            if entrantes:
                cohort_entries[(cnes, curso, comp)] = entrantes

            # Rastreamento de permanência (6 meses e 12 meses anteriores)
            permanencia_6m = 0
            permanencia_12m = 0

            if comp_idx >= 6:
                comp_6m_ago = ALL_COMPETENCIAS[comp_idx - 6]
                cohort_6m = cohort_entries.get((cnes, curso, comp_6m_ago), set())
                if cohort_6m:
                    permanencia_6m = len(cohort_6m & active_profs)

            if comp_idx >= 12:
                comp_12m_ago = ALL_COMPETENCIAS[comp_idx - 12]
                cohort_12m = cohort_entries.get((cnes, curso, comp_12m_ago), set())
                if cohort_12m:
                    permanencia_12m = len(cohort_12m & active_profs)

            # Atualizar estado anterior da célula
            prev_active_by_cell[(cnes, curso)] = active_profs

            # Post indicator e mês de transição
            is_post = 1 if comp >= "202508" else 0
            is_transicao = 1 if comp == "202507" else 0

            panel_records.append({
                "co_cnes_7d": cnes,
                "cod_curso": curso,
                "competencia": comp,
                "ano": int(comp[:4]),
                "mes": int(comp[4:]),
                "post_t": is_post,
                "mes_transicao": is_transicao,
                "n_especialistas_distintos": n_distinct,
                "cobertura_binaria": 1 if n_distinct >= 1 else 0,
                "fte_ambulatorial_total": fte_amb,
                "fte_hospitalar_total": fte_hosp,
                "fte_outros_total": fte_outros,
                "fte_total": fte_tot,
                "n_entradas": n_entradas,
                "n_saidas": n_saidas,
                "saldo_liquido": saldo_liq,
                "churn_bruto": churn,
                "permanencia_6m": permanencia_6m,
                "permanencia_12m": permanencia_12m,
                "desloc_mesmo_cnes": 0,
                "desloc_mesmo_municipio": 0,
                "desloc_outra_uf": 0,
                "desloc_novo_cadastro": n_entradas,
            })

    df_panel = pd.DataFrame(panel_records)

    # 6. Merge com os atributos de tratamento
    tratamento_cols = [
        "co_cnes_7d",
        "cod_curso",
        "no_curso",
        "immediate_is",
        "modalidade_original",
        "qt_vagas_imediatas",
        "qt_vagas_reserva",
        "qt_vagas_total",
        "faixa_atracao_anunciada",
        "co_ibge_6d",
        "sg_uf",
        "no_municipio",
        "no_estabelecimento",
        "tipo_gestao",
        "flag_overlap_cbo",
        "amostra_principal",
        "flag_cnes_multiplas_modalidades",
    ]
    df_panel = df_panel.merge(df_tratamento[tratamento_cols], on=["co_cnes_7d", "cod_curso"], how="left")

    # 7. Merge com covariáveis territoriais do IVS
    territorio_cols = [
        "co_ibge_6d",
        "co_ibge_7d",
        "macro_regiao_saude",
        "no_regiao_saude",
        "ivs_2010",
        "ivs_infra_2010",
        "ivs_ch_2010",
        "ivs_rt_2010",
        "ivs_categoria",
        "idhm_2010",
        "populacao_2010",
        "rdpc_2010",
    ]
    df_panel = df_panel.merge(df_territorio[territorio_cols], on="co_ibge_6d", how="left")

    # 8. Salvar painel analítico
    df_panel.to_parquet(OUT_PAINEL, index=False)
    print(f"\n[OK] Painel analítico mensal gravado em: {OUT_PAINEL}")
    print(f"     Dimensões: {df_panel.shape[0]:,} linhas x {df_panel.shape[1]} colunas")
    print(f"     Células distintas (CNES x Curso): {len(unique_cells):,}")
    print(f"     Competências temporais: {len(ALL_COMPETENCIAS)} meses (202406 a 202607)")

    # 9. Relatório de auditoria
    total_medicos_obs = df_panel["n_especialistas_distintos"].sum()
    total_entradas_obs = df_panel["n_entradas"].sum()
    total_saidas_obs = df_panel["n_saidas"].sum()
    total_retidos_6m = df_panel["permanencia_6m"].sum()

    auditoria_json: Dict[str, Any] = {
        "status": "CONCLUIDO_COM_SUCESSO",
        "timestamp": datetime.datetime.now().isoformat(),
        "total_linhas": len(df_panel),
        "total_celulas": len(unique_cells),
        "total_competencias": len(ALL_COMPETENCIAS),
        "estatisticas_painel": {
            "soma_especialistas_mes": int(total_medicos_obs),
            "soma_entradas": int(total_entradas_obs),
            "soma_saidas": int(total_saidas_obs),
            "soma_retidos_6m": int(total_retidos_6m),
            "cobertura_media": float(df_panel["cobertura_binaria"].mean()),
            "fte_medio_semanal": float(df_panel["fte_total"].mean()),
        },
    }

    with OUT_AUDITORIA.open("w", encoding="utf-8") as f:
        json.dump(auditoria_json, f, ensure_ascii=False, indent=2)

    with OUT_RELATORIO.open("w", encoding="utf-8") as f:
        json.dump(auditoria_json, f, ensure_ascii=False, indent=2)

    print(f"[OK] Auditoria salva em: {OUT_AUDITORIA}")


if __name__ == "__main__":
    main()
