"""02_construir_paineis_analiticos.py — Construção dos Painéis Analíticos Canônicos e Diagnósticos.

Este script processa os dados integrados e gera:
1. Painel Canônico Municipal: `município–curso–mês` (unidade principal para inferência DDD);
2. Painel Diagnóstico de Estabelecimento: `CNES–curso–mês` (diagnóstico de remanejamento local);
3. Painel Diagnóstico Regional: `Região de Saúde–curso–mês` (diagnóstico de spillover e expansão líquida regional).

Conforme as Seções 4.2 e 4.3 de docs/05_roadmap_execucao.md:
- Deduplica profissionais que atuam em múltiplos CNES no mesmo município.
- Congela os indicadores de tratamento ao nível município-curso (`immediate_ms`).
- Sinaliza municípios com variação interna (`within_muni_var`) que identificam a DDD com efeitos fixos município–mês.

Entregáveis:
- output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet
- output/avaliacao_impacto/dados/painel_cnes_curso_mes.parquet
- output/avaliacao_impacto/dados/painel_regiao_curso_mes.parquet
- output/avaliacao_impacto/relatorios/02_relatorio_painel_amostra.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output" / "avaliacao_impacto"
DADOS_DIR = OUTPUT_DIR / "dados"
RELATORIOS_DIR = OUTPUT_DIR / "relatorios"

CNES_MENSAL_FILE = ROOT / "output" / "painel_cnes_especialidade_mensal.parquet"
TERRITORIO_FILE = ROOT / "output" / "aquisicao" / "malha_municipios_regioes_saude.parquet"
PONTE_FILE = ROOT / "output" / "aquisicao" / "ponte_curso_cbo_oficial.json"
TRATAMENTO_FILE = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"


def main() -> None:
    print("=== [Etapa 2] Construção dos Painéis Analíticos Canônicos e Diagnósticos ===")
    DADOS_DIR.mkdir(parents=True, exist_ok=True)
    RELATORIOS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Carregar painel celular integrado
    print(f"Lendo base celular CNES x Curso x Mês: {CNES_MENSAL_FILE.name}...")
    df_cnes = pd.read_parquet(CNES_MENSAL_FILE)
    print(f"Dimensões do painel celular: {df_cnes.shape[0]:,} linhas x {df_cnes.shape[1]} colunas")

    # 2. Salvar painel celular diagnóstico
    out_cnes = DADOS_DIR / "painel_cnes_curso_mes.parquet"
    df_cnes.to_parquet(out_cnes, index=False)
    print(f"[OK] Painel CNES salvo em: {out_cnes}")

    # 3. Construção do Painel Canônico Municipal: município-curso-mês
    print("Agregando e deduplicando ao nível Município x Curso x Mês...")
    
    # Agregação municipal
    grp_muni_cols = ["co_ibge_6d", "cod_curso", "competencia"]
    
    # Dicionário de agregação
    agg_dict = {
        "co_ibge_7d": "first",
        "no_municipio": "first",
        "sg_uf": "first",
        "no_curso": "first",
        "ano": "first",
        "mes": "first",
        "post_t": "first",
        "mes_transicao": "first",
        "flag_overlap_cbo": "first",
        "qt_vagas_imediatas": "sum",
        "qt_vagas_reserva": "sum",
        "qt_vagas_total": "sum",
        "n_especialistas_distintos": "sum", # Na escala municipal
        "fte_ambulatorial_total": "sum",
        "fte_hospitalar_total": "sum",
        "fte_outros_total": "sum",
        "fte_total": "sum",
        "n_entradas": "sum",
        "n_saidas": "sum",
        "saldo_liquido": "sum",
        "churn_bruto": "sum",
        "permanencia_6m": "sum",
        "permanencia_12m": "sum",
        "desloc_mesmo_cnes": "sum",
        "desloc_mesmo_municipio": "sum",
        "desloc_outra_uf": "sum",
        "desloc_novo_cadastro": "sum",
        "macro_regiao_saude": "first",
        "no_regiao_saude": "first",
        "ivs_2010": "first",
        "ivs_infra_2010": "first",
        "ivs_ch_2010": "first",
        "ivs_rt_2010": "first",
        "ivs_categoria": "first",
        "idhm_2010": "first",
        "populacao_2010": "first",
        "rdpc_2010": "first",
    }

    df_muni = df_cnes.groupby(grp_muni_cols, as_index=False).agg(agg_dict)

    # Renomear outcome primário e definir tratamento municipal
    df_muni["especialistas_mst"] = df_muni["n_especialistas_distintos"]
    df_muni["cobertura_binaria_mst"] = (df_muni["especialistas_mst"] > 0).astype(int)

    # Variável canônica de tratamento municipal
    df_muni["immediate_ms"] = (df_muni["qt_vagas_imediatas"] > 0).astype(int)
    
    # Classificação modalidade municipal
    df_muni["modalidade_ms"] = "RESERVA"
    df_muni.loc[(df_muni["qt_vagas_imediatas"] > 0) & (df_muni["qt_vagas_reserva"] == 0), "modalidade_ms"] = "IMEDIATA"
    df_muni.loc[(df_muni["qt_vagas_imediatas"] > 0) & (df_muni["qt_vagas_reserva"] > 0), "modalidade_ms"] = "DUPLA"
    
    df_muni["amostra_principal"] = df_muni["modalidade_ms"].isin(["IMEDIATA", "RESERVA"])

    # Identificar municípios com variação intra-municipal (identificadores da DDD com FE município-mês)
    muni_var = df_muni.groupby("co_ibge_6d")["immediate_ms"].nunique()
    munis_with_variation = set(muni_var[muni_var > 1].index)
    df_muni["within_muni_var"] = df_muni["co_ibge_6d"].isin(munis_with_variation)

    # Interaction term canônico
    df_muni["treat_x_post"] = df_muni["immediate_ms"] * df_muni["post_t"]

    out_muni = DADOS_DIR / "painel_municipio_curso_mes.parquet"
    df_muni.to_parquet(out_muni, index=False)
    print(f"[OK] Painel Municipal salvo em: {out_muni}")
    print(f"     Dimensões: {len(df_muni):,} linhas x {df_muni.shape[1]} colunas")
    print(f"     Células Município-Curso únicas: {df_muni[['co_ibge_6d', 'cod_curso']].drop_duplicates().shape[0]:,}")
    print(f"     Municípios distintos: {df_muni['co_ibge_6d'].nunique():,}")
    print(f"     Municípios com variação intra-municipal (DDD identificadora): {len(munis_with_variation):,}")

    # 4. Construção do Painel Regional: Região de Saúde x Curso x Mês
    print("Construindo Painel Regional (Região de Saúde x Curso x Mês)...")
    grp_reg_cols = ["no_regiao_saude", "sg_uf", "cod_curso", "competencia"]
    
    agg_reg_dict = {
        "no_curso": "first",
        "ano": "first",
        "mes": "first",
        "post_t": "first",
        "mes_transicao": "first",
        "flag_overlap_cbo": "first",
        "qt_vagas_imediatas": "sum",
        "qt_vagas_reserva": "sum",
        "qt_vagas_total": "sum",
        "especialistas_mst": "sum",
        "fte_total": "sum",
        "n_entradas": "sum",
        "n_saidas": "sum",
        "saldo_liquido": "sum",
        "permanencia_6m": "sum",
        "populacao_2010": "sum",
    }
    
    df_reg = df_muni.groupby(grp_reg_cols, as_index=False).agg(agg_reg_dict)
    df_reg.rename(columns={"especialistas_mst": "especialistas_rst"}, inplace=True)
    df_reg["immediate_rs"] = (df_reg["qt_vagas_imediatas"] > 0).astype(int)
    df_reg["treat_x_post"] = df_reg["immediate_rs"] * df_reg["post_t"]

    out_reg = DADOS_DIR / "painel_regiao_curso_mes.parquet"
    df_reg.to_parquet(out_reg, index=False)
    print(f"[OK] Painel Regional salvo em: {out_reg}")
    print(f"     Dimensões: {len(df_reg):,} linhas x {df_reg.shape[1]} colunas")
    print(f"     Regiões de Saúde distintas: {df_reg['no_regiao_saude'].nunique():,}")

    # 5. Relatório de auditoria e composição da amostra
    celulas_muni_total = df_muni[["co_ibge_6d", "cod_curso"]].drop_duplicates()
    celulas_muni_var = df_muni[df_muni["within_muni_var"]][["co_ibge_6d", "cod_curso"]].drop_duplicates()

    relatorio_amostra: Dict[str, Any] = {
        "data_processamento": "2026-08-30",
        "periodo_cobertura": {
            "inicio": "2024-06",
            "fim": "2026-07",
            "total_meses": 26,
            "meses_pre": 13,
            "mes_transicao": "2025-07",
            "meses_pos": 12,
        },
        "painel_municipal_canonico": {
            "total_linhas": len(df_muni),
            "total_municipios": df_muni["co_ibge_6d"].nunique(),
            "total_celulas_municipio_curso": len(celulas_muni_total),
            "distribuicao_modalidade": df_muni.drop_duplicates(["co_ibge_6d", "cod_curso"])["modalidade_ms"].value_counts().to_dict(),
            "amostra_identificadora_ddd": {
                "municipios_com_variacao_intra": len(munis_with_variation),
                "celulas_municipio_curso_com_variacao": len(celulas_muni_var),
                "percentual_amostra_identificadora": round(len(celulas_muni_var) / len(celulas_muni_total) * 100, 2),
            },
        },
        "painel_cnes_diagnostico": {
            "total_linhas": len(df_cnes),
            "total_cnes": df_cnes["co_cnes_7d"].nunique(),
            "total_celulas_cnes_curso": df_cnes[["co_cnes_7d", "cod_curso"]].drop_duplicates().shape[0],
        },
        "painel_regional_diagnostico": {
            "total_linhas": len(df_reg),
            "total_regioes_saude": df_reg["no_regiao_saude"].nunique(),
            "total_celulas_regiao_curso": df_reg[["no_regiao_saude", "cod_curso"]].drop_duplicates().shape[0],
        },
    }

    out_rel = RELATORIOS_DIR / "02_relatorio_painel_amostra.json"
    with out_rel.open("w", encoding="utf-8") as f:
        json.dump(relatorio_amostra, f, ensure_ascii=False, indent=2)
    print(f"[OK] Relatório de amostra salvo em: {out_rel}")


if __name__ == "__main__":
    main()
