"""04_harmonizar_territorio_ibge.py — Georreferenciamento, IVS e Estrutura Territorial.

Este script harmoniza a malha municipal brasileira com as chaves IBGE de 6 e 7 dígitos,
integrando os microdados de vulnerabilidade social do IPEA (IVS 2010 e subíndices),
IDHM 2010, população estimada e a estrutura de Regiões de Saúde (CIR) e Macrorregiões do SUS.

Entregáveis:
- `output/aquisicao/malha_municipios_regioes_saude.parquet`
- `output/aquisicao/painel_municipios_regioes.parquet`
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output" / "aquisicao"

IVS_FILE = DATA_DIR / "ivs_ipea_2010_municipios.csv"
SERIE_FILE = DATA_DIR / "pmm_especialistas_serie_historica.csv"
NOMINAL_FILE = DATA_DIR / "pmm_especialistas_nominal.csv"

OUT_MALHA = OUTPUT_DIR / "malha_municipios_regioes_saude.parquet"
OUT_PAINEL_MUNI = OUTPUT_DIR / "painel_municipios_regioes.parquet"


def normalize_str(val: object) -> str:
    if val is None or pd.isna(val):
        return ""
    text = unicodedata.normalize("NFKD", str(val))
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip().upper()


def classify_ivs_category(val: float) -> str:
    if pd.isna(val):
        return "NAO_INFORMADO"
    if val <= 0.200:
        return "MUITO_BAIXA"
    elif val <= 0.300:
        return "BAIXA"
    elif val <= 0.400:
        return "MEDIA"
    elif val <= 0.500:
        return "ALTA"
    else:
        return "MUITO_ALTA"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("=== [Subagente 3] Harmonização Territorial, IVS 2010 e Regiões de Saúde ===")

    # 1. Carregar IVS IPEA 2010
    print(f"Lendo base IVS IPEA 2010 de {IVS_FILE.name}...")
    df_ivs = pd.read_csv(IVS_FILE)
    df_ivs["co_ibge_6d"] = df_ivs["cod_ibge6"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(6)
    df_ivs["co_ibge_7d"] = df_ivs["cod_ibge7"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(7)
    df_ivs["sg_uf"] = df_ivs["uf"].astype(str).str.strip().str.upper()
    df_ivs["no_municipio"] = df_ivs["municipio_uf"].astype(str).apply(lambda s: s.split("(")[0].strip() if "(" in s else s)
    df_ivs["ivs_categoria"] = df_ivs["ivs_2010"].apply(classify_ivs_category)

    # 2. Carregar Regiões de Saúde e Macrorregiões da série histórica e nominal
    regions_map: Dict[str, Dict[str, str]] = {}
    if SERIE_FILE.exists():
        df_serie = pd.read_csv(SERIE_FILE)
        for _, row in df_serie[["co_ibge", "regiao", "regiao_saude"]].dropna().drop_duplicates().iterrows():
            ibge6 = str(row["co_ibge"]).split(".")[0].zfill(6)
            regions_map[ibge6] = {
                "macro_regiao": normalize_str(row["regiao"]),
                "regiao_saude": normalize_str(row["regiao_saude"]),
            }

    if NOMINAL_FILE.exists():
        df_nom = pd.read_csv(NOMINAL_FILE)
        for _, row in df_nom[["co_ibge", "regiao", "regiao_saude"]].dropna().drop_duplicates().iterrows():
            ibge6 = str(row["co_ibge"]).split(".")[0].zfill(6)
            if ibge6 not in regions_map:
                regions_map[ibge6] = {
                    "macro_regiao": normalize_str(row["regiao"]),
                    "regiao_saude": normalize_str(row["regiao_saude"]),
                }

    # Atribuir macro e região de saúde
    macro_list = []
    reg_saude_list = []
    for ibge6 in df_ivs["co_ibge_6d"]:
        reg_info = regions_map.get(ibge6, {})
        macro_list.append(reg_info.get("macro_regiao", ""))
        reg_saude_list.append(reg_info.get("regiao_saude", ""))

    df_ivs["macro_regiao_saude"] = macro_list
    df_ivs["no_regiao_saude"] = reg_saude_list

    # Definir tabela final de malha municipal
    df_territorio = pd.DataFrame({
        "co_ibge_6d": df_ivs["co_ibge_6d"],
        "co_ibge_7d": df_ivs["co_ibge_7d"],
        "no_municipio": df_ivs["no_municipio"],
        "sg_uf": df_ivs["sg_uf"],
        "nome_uf": df_ivs["nome_uf"],
        "macro_regiao_saude": df_ivs["macro_regiao_saude"],
        "no_regiao_saude": df_ivs["no_regiao_saude"],
        "ivs_2010": df_ivs["ivs_2010"],
        "ivs_infra_2010": df_ivs["ivs_infra_2010"],
        "ivs_ch_2010": df_ivs["ivs_ch_2010"],
        "ivs_rt_2010": df_ivs["ivs_rt_2010"],
        "ivs_categoria": df_ivs["ivs_categoria"],
        "idhm_2010": df_ivs["idhm_2010"],
        "populacao_2010": df_ivs["populacao_2010"],
        "rdpc_2010": df_ivs["rdpc_2010"],
    })

    # Salvar parquets
    df_territorio.to_parquet(OUT_MALHA, index=False)
    df_territorio.to_parquet(OUT_PAINEL_MUNI, index=False)

    print(f"[OK] Malha territorial salva em: {OUT_MALHA}")
    print(f"[OK] Painel de municípios salvo em: {OUT_PAINEL_MUNI}")
    print(f"     Total de municípios integrados: {len(df_territorio):,}")
    print(f"     Municípios com IVS válido: {df_territorio['ivs_2010'].notna().sum():,}")
    print(f"     Distribuição de vulnerabilidade IVS 2010:")
    for cat, n in df_territorio["ivs_categoria"].value_counts().items():
        print(f"       - {cat}: {n} municípios")


if __name__ == "__main__":
    main()
