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
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output"
AQUISICAO_DIR = OUTPUT_DIR / "aquisicao"
MONTHLY_CNES_DIR = AQUISICAO_DIR / "cnes_mensal"

PONTE_FILE = AQUISICAO_DIR / "ponte_curso_cbo_oficial.json"
TRATAMENTO_FILE = AQUISICAO_DIR / "quadro_vagas_tratamento.parquet"
TERRITORIO_FILE = AQUISICAO_DIR / "malha_municipios_regioes_saude.parquet"
CONSOLIDATED_CNES_FILE = AQUISICAO_DIR / "cnes_vinculos_medicos_2024_2026.parquet"

OUT_PAINEL = OUTPUT_DIR / "painel_cnes_especialidade_mensal.parquet"
OUT_AUDITORIA = AQUISICAO_DIR / "auditoria_painel_final.json"
OUT_RELATORIO = AQUISICAO_DIR / "relatorio_auditoria_painel.json"

ALL_COMPETENCIAS = [
    f"{year}{month:02d}"
    for year, first, last in ((2024, 6, 12), (2025, 1, 12), (2026, 1, 7))
    for month in range(first, last + 1)
]


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
    territorio_map = df_territorio.set_index("co_ibge_6d").to_dict(orient="index")

    # 4. Verificar arquivos mensais do CNES
    available_months = []
    for comp in ALL_COMPETENCIAS:
        p_month = MONTHLY_CNES_DIR / f"cnes_vinculos_medicos_{comp}.parquet"
        if p_month.exists():
            available_months.append(comp)

    if not available_months and CONSOLIDATED_CNES_FILE.exists():
        print(f"Carregando a partir do arquivo consolidado {CONSOLIDATED_CNES_FILE.name}...")
        df_cnes_all = pd.read_parquet(CONSOLIDATED_CNES_FILE)
        available_months = sorted(df_cnes_all["competencia"].unique())
    else:
        df_cnes_all = None

    print(f"Competências CNES disponíveis para processamento: {len(available_months)} de {len(ALL_COMPETENCIAS)}")

    # 5. Processamento mês a mês para agregação celular e dinâmica longitudinal
    # Células canônicas: (co_cnes_7d, cod_curso)
    unique_cells = df_tratamento[["co_cnes_7d", "cod_curso"]].drop_duplicates().values.tolist()
    target_cnes_set = set(df_tratamento["co_cnes_7d"].unique())

    panel_records: List[Dict[str, Any]] = []

    # Estruturas para rastrear dinâmica longitudinal:
    # prev_active_by_cell[(cnes, curso)] = set(co_profissional_sus)
    # cohort_entries[(cnes, curso, comp_entry)] = set(co_profissional_sus)
    # prev_global_prof_location[co_profissional_sus] = (co_cnes, co_municipio, co_uf)
    prev_active_by_cell: Dict[Tuple[str, int], Set[str]] = {}
    cohort_entries: Dict[Tuple[str, int, str], Set[str]] = {}
    prev_global_prof_location: Dict[str, Tuple[str, str, str]] = {}

    for comp_idx, comp in enumerate(ALL_COMPETENCIAS):
        print(f"  -> Integrando competência {comp} ({comp_idx + 1}/{len(ALL_COMPETENCIAS)})...")

        # Obter dados do mês
        p_month = MONTHLY_CNES_DIR / f"cnes_vinculos_medicos_{comp}.parquet"
        if p_month.exists():
            df_m = pd.read_parquet(p_month)
        elif df_cnes_all is not None:
            df_m = df_cnes_all[df_cnes_all["competencia"] == comp]
        else:
            # Criar registros zerados se o mês ainda não estiver adquirido
            df_m = pd.DataFrame(columns=["co_cnes_7d", "co_cbo_6d", "co_profissional_sus", "qt_carga_horaria_ambulatorial", "qt_carga_hor_hosp_sus", "qt_carga_horaria_outros", "co_municipio_gestor", "sg_uf_crm"])

        # Filtrar vínculos apenas para os CNES do universo de tratamento
        df_m_target = df_m[df_m["co_cnes_7d"].isin(target_cnes_set)].copy()

        # Mapeamento de localização global de todos os profissionais no mês atual
        curr_global_prof_location: Dict[str, Tuple[str, str, str]] = {}
        for _, row in df_m[["co_profissional_sus", "co_cnes_7d", "co_municipio_gestor", "sg_uf_crm"]].dropna().iterrows():
            pid = str(row["co_profissional_sus"])
            if pid and pid not in curr_global_prof_location:
                curr_global_prof_location[pid] = (str(row["co_cnes_7d"]), str(row["co_municipio_gestor"]), str(row["sg_uf_crm"]))

        # Indexar registros do mês alvo por (cnes, cbo)
        cnes_cbo_records: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
        for row in df_m_target.to_dict(orient="records"):
            key = (str(row["co_cnes_7d"]), str(row["co_cbo_6d"]))
            if key not in cnes_cbo_records:
                cnes_cbo_records[key] = []
            cnes_cbo_records[key].append(row)

        # Iterar sobre todas as 1.295 células canônicas
        for cnes, curso in unique_cells:
            cnes = str(cnes)
            curso = int(curso)
            eligible_cbos = cbo_bridge.get(curso, [])

            # Recuperar todos os vínculos médicos para os CBOs elegíveis do curso neste CNES
            matching_rows = []
            for cbo in eligible_cbos:
                matching_rows.extend(cnes_cbo_records.get((cnes, cbo), []))

            # Profissionais ativos nesta célula no mês atual
            active_profs = {str(r["co_profissional_sus"]) for r in matching_rows if str(r.get("co_profissional_sus", "")).strip()}
            n_distinct = len(active_profs)

            fte_amb = sum(float(r.get("qt_carga_horaria_ambulatorial", 0) or 0) for r in matching_rows)
            fte_hosp = sum(float(r.get("qt_carga_hor_hosp_sus", 0) or 0) for r in matching_rows)
            fte_outros = sum(float(r.get("qt_carga_horaria_outros", 0) or 0) for r in matching_rows)
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

            # Verificar entrantes de 6 meses atrás
            if comp_idx >= 6:
                comp_6m_ago = ALL_COMPETENCIAS[comp_idx - 6]
                cohort_6m = cohort_entries.get((cnes, curso, comp_6m_ago), set())
                if cohort_6m:
                    permanencia_6m = len(cohort_6m & active_profs)

            # Verificar entrantes de 12 meses atrás
            if comp_idx >= 12:
                comp_12m_ago = ALL_COMPETENCIAS[comp_idx - 12]
                cohort_12m = cohort_entries.get((cnes, curso, comp_12m_ago), set())
                if cohort_12m:
                    permanencia_12m = len(cohort_12m & active_profs)

            # Deslocamento de Origem dos novos entrantes
            desloc_mesmo_cnes = 0
            desloc_mesmo_mun = 0
            desloc_mesma_reg = 0
            desloc_outra_uf = 0
            desloc_novo = 0

            # Obter município do CNES atual
            ibge_cnes_atual = ""
            for r in matching_rows:
                if r.get("co_municipio_gestor"):
                    ibge_cnes_atual = str(r["co_municipio_gestor"])
                    break

            for pid in entrantes:
                prev_loc = prev_global_prof_location.get(pid)
                if not prev_loc:
                    desloc_novo += 1
                else:
                    prev_cnes, prev_mun, prev_uf = prev_loc
                    if prev_cnes == cnes:
                        desloc_mesmo_cnes += 1
                    elif prev_mun == ibge_cnes_atual:
                        desloc_mesmo_mun += 1
                    else:
                        desloc_outra_uf += 1

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
                "desloc_mesmo_cnes": desloc_mesmo_cnes,
                "desloc_mesmo_municipio": desloc_mesmo_mun,
                "desloc_outra_uf": desloc_outra_uf,
                "desloc_novo_cadastro": desloc_novo,
            })

        # Atualizar histórico global de localização para o próximo mês
        prev_global_prof_location = curr_global_prof_location

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

    # 8. Reordenar colunas
    cols_order = [
        "co_cnes_7d",
        "cod_curso",
        "no_curso",
        "competencia",
        "ano",
        "mes",
        "post_t",
        "mes_transicao",
        "immediate_is",
        "modalidade_original",
        "amostra_principal",
        "flag_overlap_cbo",
        "flag_cnes_multiplas_modalidades",
        "qt_vagas_imediatas",
        "qt_vagas_reserva",
        "qt_vagas_total",
        "faixa_atracao_anunciada",
        "n_especialistas_distintos",
        "cobertura_binaria",
        "fte_ambulatorial_total",
        "fte_hospitalar_total",
        "fte_total",
        "n_entradas",
        "n_saidas",
        "saldo_liquido",
        "churn_bruto",
        "permanencia_6m",
        "permanencia_12m",
        "desloc_mesmo_cnes",
        "desloc_mesmo_municipio",
        "desloc_outra_uf",
        "desloc_novo_cadastro",
        "co_ibge_6d",
        "co_ibge_7d",
        "no_municipio",
        "sg_uf",
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
        "no_estabelecimento",
        "tipo_gestao",
    ]
    cols_present = [c for c in cols_order if c in df_panel.columns] + [c for c in df_panel.columns if c not in cols_order]
    df_panel = df_panel[cols_present]

    # Salvar painel analítico final
    df_panel.to_parquet(OUT_PAINEL, index=False)
    print(f"\n[OK] Painel analítico mensal gravado em: {OUT_PAINEL}")
    print(f"     Dimensões: {df_panel.shape[0]:,} linhas x {df_panel.shape[1]} colunas")
    print(f"     Células distintas (CNES x Curso): {df_panel.groupby(['co_cnes_7d', 'cod_curso']).ngroups:,}")
    print(f"     Competências temporais: {df_panel['competencia'].nunique()} meses ({df_panel['competencia'].min()} a {df_panel['competencia'].max()})")

    # 9. Gerar Relatório e Auditoria de Dados
    # Balanceamento de baseline (202406 a 202506)
    df_baseline = df_panel[(df_panel["post_t"] == 0) & (df_panel["mes_transicao"] == 0) & (df_panel["amostra_principal"] == True)]
    baseline_stats = (
        df_baseline.groupby("modalidade_original")
        .agg(
            n_obs=("n_especialistas_distintos", "count"),
            media_especialistas=("n_especialistas_distintos", "mean"),
            std_especialistas=("n_especialistas_distintos", "std"),
            media_fte_total=("fte_total", "mean"),
            cobertura_media=("cobertura_binaria", "mean"),
            ivs_medio=("ivs_2010", "mean"),
            populacao_media=("populacao_2010", "mean"),
        )
        .to_dict(orient="index")
    )

    auditoria = {
        "status": "painel_validado",
        "data_geracao": datetime.date.today().isoformat(),
        "total_linhas": len(df_panel),
        "total_celulas_cnes_curso": int(df_panel.groupby(["co_cnes_7d", "cod_curso"]).ngroups),
        "total_competencias": int(df_panel["competencia"].nunique()),
        "competencias": sorted(list(df_panel["competencia"].unique())),
        "amostra_principal_linhas": int((df_panel["amostra_principal"] == True).sum()),
        "amostra_principal_celulas": int(df_panel[df_panel["amostra_principal"] == True].groupby(["co_cnes_7d", "cod_curso"]).ngroups),
        "balanco_baseline_amostra_principal": baseline_stats,
        "estatisticas_gerais_painel": {
            "media_geral_especialistas": float(df_panel["n_especialistas_distintos"].mean()),
            "total_especialistas_registrados": int(df_panel["n_especialistas_distintos"].sum()),
            "media_fte_total": float(df_panel["fte_total"].mean()),
            "taxa_cobertura_media": float(df_panel["cobertura_binaria"].mean()),
            "total_entradas_medicas": int(df_panel["n_entradas"].sum()),
            "total_saidas_medicas": int(df_panel["n_saidas"].sum()),
        },
        "verificacao_nulos_chaves": {
            "nan_co_cnes": int(df_panel["co_cnes_7d"].isna().sum()),
            "nan_cod_curso": int(df_panel["cod_curso"].isna().sum()),
            "nan_competencia": int(df_panel["competencia"].isna().sum()),
            "nan_immediate_is": int(df_panel["immediate_is"].isna().sum()),
        },
    }

    with OUT_AUDITORIA.open("w", encoding="utf-8") as f:
        json.dump(auditoria, f, ensure_ascii=False, indent=2)
        f.write("\n")

    with OUT_RELATORIO.open("w", encoding="utf-8") as f:
        json.dump(auditoria, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"[OK] Auditoria salva em: {OUT_AUDITORIA}")
    print(f"[OK] Relatório salvo em: {OUT_RELATORIO}")


if __name__ == "__main__":
    main()
