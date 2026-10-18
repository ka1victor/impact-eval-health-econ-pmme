"""04_harmonizar_territorio_ibge.py — Georreferenciamento, IVS e Estrutura Territorial.

Este script harmoniza a malha municipal brasileira com as chaves IBGE de 6 e 7 dígitos,
integrando o IVS 2010 oficial do Ipea e seus subíndices, o IDHM 2010, a população de
2010 e a de 2022 e a estrutura de Regiões de Saúde (CIR) e Macrorregiões do SUS.

Fontes (correção de 18/10/2026, `docs/auditorias/19_reestimacao_base_oficial_failure_mode.md`):
- IVS 2010, subíndices, IDHM 2010, população 2010 e renda per capita 2010:
  `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`, linha Total/Total/Total da
  base completa do Atlas da Vulnerabilidade Social (Ipea), 5.565 municípios;
- código IBGE de 7 dígitos e população residente de 2022:
  `output/aquisicao/populacao_censo2022_municipios.csv` (Censo 2022, SIDRA 4709);
- região e macrorregião de saúde: série histórica e lista nominal do PMM-E.

Até 18/10/2026 este script lia `data/ivs_ipea_2010_municipios.csv`, que não é o IVS do
município: é, em cada município, a última linha de subgrupo com IVS preenchido da mesma
base (mulheres negras em área urbana em 78% dos municípios;
`docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md`). IVS, IDHM, população e renda
da malha, da tipologia A2 e dos painéis CNES herdavam esse erro. O arquivo não é mais lido
aqui.

Entregáveis:
- `output/aquisicao/malha_municipios_regioes_saude.parquet`
- `output/aquisicao/painel_municipios_regioes.parquet`
- `output/aquisicao/manifesto_territorio_ibge.json`
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output" / "aquisicao"

IVS_OFICIAL_FILE = OUTPUT_DIR / "a08_ivs_2010_oficial_municipio.csv"
CENSO2022_FILE = OUTPUT_DIR / "populacao_censo2022_municipios.csv"
SERIE_FILE = DATA_DIR / "pmm_especialistas_serie_historica.csv"
NOMINAL_FILE = DATA_DIR / "pmm_especialistas_nominal.csv"

OUT_MALHA = OUTPUT_DIR / "malha_municipios_regioes_saude.parquet"
OUT_PAINEL_MUNI = OUTPUT_DIR / "painel_municipios_regioes.parquet"
OUT_MANIFESTO = OUTPUT_DIR / "manifesto_territorio_ibge.json"

# Códigos e nomes oficiais das 27 UFs (IBGE, estáveis). A coluna `sg_uf` da malha guarda
# o código numérico da UF como texto, convenção mantida desde a versão anterior.
NOME_UF = {
    "11": "Rondônia", "12": "Acre", "13": "Amazonas", "14": "Roraima", "15": "Pará",
    "16": "Amapá", "17": "Tocantins", "21": "Maranhão", "22": "Piauí", "23": "Ceará",
    "24": "Rio Grande do Norte", "25": "Paraíba", "26": "Pernambuco", "27": "Alagoas",
    "28": "Sergipe", "29": "Bahia", "31": "Minas Gerais", "32": "Espírito Santo",
    "33": "Rio de Janeiro", "35": "São Paulo", "41": "Paraná", "42": "Santa Catarina",
    "43": "Rio Grande do Sul", "50": "Mato Grosso do Sul", "51": "Mato Grosso",
    "52": "Goiás", "53": "Distrito Federal",
}

# Coluna da malha <- coluna da base oficial (a08). Os nomes da malha são preservados
# para não mudar a interface dos consumidores (05_integrar, tipologia A2, A4, A5).
COLUNAS_A08 = {
    "ivs_2010": "ivs",
    "ivs_infra_2010": "ivs_infraestrutura_urbana",
    "ivs_ch_2010": "ivs_capital_humano",
    "ivs_rt_2010": "ivs_renda_e_trabalho",
    "idhm_2010": "idhm",
    "populacao_2010": "populacao",
    "rdpc_2010": "renda_per_capita",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


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


def carregar_ivs_oficial(path: Path = IVS_OFICIAL_FILE, censo_path: Path = CENSO2022_FILE) -> pd.DataFrame:
    """Base municipal oficial: a08 + código de 7 dígitos e população do Censo 2022.

    Município da a08 sem código de 7 dígitos no Censo 2022 aborta: a malha de 2010 está
    contida na de 2022, e um código perdido seria erro de chave, não ausência real.
    """
    of = pd.read_csv(path, dtype={"co_ibge": str, "uf": str})
    of["co_ibge_6d"] = of["co_ibge"].str.replace(r"\D", "", regex=True).str.zfill(6)
    if of["co_ibge_6d"].duplicated().any():
        raise ValueError(f"{path.name}: código municipal duplicado")
    censo = pd.read_csv(censo_path, dtype={"co_ibge_6d": str, "co_ibge_7d": str})
    censo["co_ibge_6d"] = censo["co_ibge_6d"].str.zfill(6)
    censo["co_ibge_7d"] = censo["co_ibge_7d"].str.zfill(7)
    base = of.merge(censo[["co_ibge_6d", "co_ibge_7d", "populacao_2022"]], on="co_ibge_6d",
                    how="left", validate="one_to_one")
    sem_7d = base.loc[base["co_ibge_7d"].isna(), "co_ibge_6d"].tolist()
    if sem_7d:
        raise ValueError(f"municípios da a08 sem código no Censo 2022: {sem_7d[:10]}")
    base["sg_uf"] = base["uf"].astype(str).str.strip()
    desconhecidas = sorted(set(base["sg_uf"]) - set(NOME_UF))
    if desconhecidas:
        raise ValueError(f"código de UF desconhecido: {desconhecidas}")
    base["nome_uf"] = base["sg_uf"].map(NOME_UF)
    base["no_municipio"] = base["nome_municipio_uf"].astype(str).map(
        lambda s: s.split("(")[0].strip() if "(" in s else s)
    for destino, origem in COLUNAS_A08.items():
        base[destino] = pd.to_numeric(base[origem], errors="raise")
    base["populacao_2022"] = pd.to_numeric(base["populacao_2022"], errors="raise")
    base["ivs_categoria"] = base["ivs_2010"].apply(classify_ivs_category)
    return base


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print("=== Harmonização territorial: IVS 2010 oficial (Ipea), Censo 2022 e Regiões de Saúde ===")

    # 1. Base municipal oficial (a08 + Censo 2022)
    print(f"Lendo IVS 2010 oficial de {IVS_OFICIAL_FILE.name} e chaves/população 2022 de {CENSO2022_FILE.name}...")
    df_ivs = carregar_ivs_oficial()

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

    df_ivs["macro_regiao_saude"] = [regions_map.get(c, {}).get("macro_regiao", "") for c in df_ivs["co_ibge_6d"]]
    df_ivs["no_regiao_saude"] = [regions_map.get(c, {}).get("regiao_saude", "") for c in df_ivs["co_ibge_6d"]]

    # Definir tabela final de malha municipal (mesmas colunas da versão anterior + população 2022)
    colunas = [
        "co_ibge_6d", "co_ibge_7d", "no_municipio", "sg_uf", "nome_uf",
        "macro_regiao_saude", "no_regiao_saude",
        "ivs_2010", "ivs_infra_2010", "ivs_ch_2010", "ivs_rt_2010", "ivs_categoria",
        "idhm_2010", "populacao_2010", "rdpc_2010", "populacao_2022",
    ]
    df_territorio = df_ivs[colunas].sort_values("co_ibge_6d").reset_index(drop=True)

    # Salvar parquets
    df_territorio.to_parquet(OUT_MALHA, index=False)
    df_territorio.to_parquet(OUT_PAINEL_MUNI, index=False)

    def rel(p: Path) -> str:
        return str(p.relative_to(ROOT)).replace("\\", "/")

    manifesto: dict[str, Any] = {
        "etapa": "04_harmonizar_territorio_ibge",
        "correcao": {
            "data": "2026-10-18",
            "descricao": (
                "IVS, subíndices, IDHM, população 2010 e renda passam a vir da base oficial do Ipea (a08); "
                "código de 7 dígitos e população 2022, do Censo 2022. data/ivs_ipea_2010_municipios.csv "
                "(linha de subgrupo, auditoria 16) deixou de ser lido."
            ),
            "registro": "docs/auditorias/19_reestimacao_base_oficial_failure_mode.md",
        },
        "entradas": {
            rel(IVS_OFICIAL_FILE): {
                "sha256": sha256(IVS_OFICIAL_FILE),
                "fonte": "Atlas da Vulnerabilidade Social (Ipea), base completa, linha Total/Total/Total de 2010",
                "data_referencia": "Censo 2010",
                "unidade": "município (malha 2010)",
                "chave": "co_ibge (6 dígitos)",
                "colunas_usadas": COLUNAS_A08,
            },
            rel(CENSO2022_FILE): {
                "sha256": sha256(CENSO2022_FILE),
                "fonte": "IBGE, Censo Demográfico 2022, SIDRA 4709, variável 93",
                "data_referencia": "2022",
                "unidade": "município (malha 2022)",
                "chave": "co_ibge_6d; co_ibge_7d",
                "colunas_usadas": ["co_ibge_7d", "populacao_2022"],
            },
            rel(SERIE_FILE): {"sha256": sha256(SERIE_FILE), "colunas_usadas": ["co_ibge", "regiao", "regiao_saude"]},
            rel(NOMINAL_FILE): {"sha256": sha256(NOMINAL_FILE), "colunas_usadas": ["co_ibge", "regiao", "regiao_saude"]},
        },
        "cobertura": {
            "municipios": int(len(df_territorio)),
            "ivs_valido": int(df_territorio["ivs_2010"].notna().sum()),
            "populacao_2010_total": int(df_territorio["populacao_2010"].sum()),
            "populacao_2022_total_nos_municipios_da_malha_2010": int(df_territorio["populacao_2022"].sum()),
            "com_regiao_saude": int((df_territorio["no_regiao_saude"] != "").sum()),
        },
        "saidas": {rel(OUT_MALHA): {"sha256": sha256(OUT_MALHA)}, rel(OUT_PAINEL_MUNI): {"sha256": sha256(OUT_PAINEL_MUNI)}},
    }
    OUT_MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] Malha territorial salva em: {OUT_MALHA}")
    print(f"[OK] Painel de municípios salvo em: {OUT_PAINEL_MUNI}")
    print(f"     Total de municípios integrados: {len(df_territorio):,}")
    print(f"     Municípios com IVS válido: {df_territorio['ivs_2010'].notna().sum():,}")
    print(f"     População 2010 (soma): {int(df_territorio['populacao_2010'].sum()):,}")
    print("     Distribuição de vulnerabilidade IVS 2010:")
    for cat, n in df_territorio["ivs_categoria"].value_counts().items():
        print(f"       - {cat}: {n} municípios")


if __name__ == "__main__":
    main()
