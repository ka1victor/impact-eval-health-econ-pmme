"""Adquire o escore administrativo de IVS publicado nos dados abertos do PMM.

O dicionario de dados do Ministerio da Saude (versao de 13/07/2026) passou a
documentar, na "Relacao Nominal Ativos - PMM-E", a coluna `ivs` ("Valor do
Indice de Vulnerabilidade Social (IVS) calculado pelo IPEA"), alem de
`categoria_ivs` e `faixa_atracao`. O consolidado do Programa Mais Medicos
(PMMB) traz `categoria_ivs` para todos os municipios do pais.

Este script pertence ao portao R1 da RDD da bolsa e **nao abre outcome**:

- os brutos sao preservados em `data/raw/aquisicao/ivs_administrativo/`, com
  URL, data de captura, tamanho e SHA-256 no manifesto;
- das bases, extrai apenas as colunas da regra (municipio, escore, categoria e
  faixa). Nome, CRM, contagens de ativos e datas de inicio nao sao lidos.

A presenca de um municipio na relacao nominal depende de haver especialista
ativo nele. A cobertura do escore e, portanto, selecionada pelo desfecho; o
portao R1 trata isso como bloqueio, nao como detalhe.
"""

from __future__ import annotations

import hashlib
import io
import json
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo"
OUT = ROOT / "output" / "aquisicao"

DATA_CAPTURA = "2026-10-14"
S3 = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/MaisMedicos"
PAGINA = "https://dadosabertos.saude.gov.br/dataset/provimento-federal-programa-mais-medicos"

FONTES = [
    {
        "id": "pmme_relacao_nominal_ativos",
        "arquivo": "tb_profissionais_ativos_pmme_csv.zip",
        "url": f"{S3}/csv/tb_profissionais_ativos_pmme_csv.zip",
        "descricao": "Relacao Nominal Ativos - PMM-E (dados abertos MS), versao de 09/10/2026",
        "papel": "escore administrativo continuo `ivs`, `categoria_ivs` e `faixa_atracao` por municipio com ativo",
    },
    {
        "id": "pmmb_consolidado",
        "arquivo": "ppf_mais_medicos_csv.zip",
        "url": f"{S3}/csv/ppf_mais_medicos.csv.zip",
        "descricao": "Programa Mais Medicos - Consolidado (dados abertos MS), versao de 09/10/2026",
        "papel": "`categoria_ivs` administrativa para todos os municipios do pais",
    },
    {
        "id": "dicionario_dados_ppf",
        "arquivo": "Dicionario_de_dados_PPF_Mais_Medicos.pdf",
        "url": f"{S3}/Dicionario_de_dados_PPF_Mais_Medicos.pdf",
        "descricao": "Dicionario de dados - PPF - PMMB e PMpB (inclui PMM-E), versao de 13/07/2026",
        "papel": "define `ivs` como valor numerico do IVS e `categoria_ivs` como classe do IVS/Ipea",
    },
]

CATEGORIAS = {
    "MUITO BAIXA VULNERABILIDADE": 1,
    "BAIXA VULNERABILIDADE": 2,
    "MEDIA VULNERABILIDADE": 3,
    "ALTA VULNERABILIDADE": 4,
    "MUITO ALTA VULNERABILIDADE": 5,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(65536):
            h.update(bloco)
    return h.hexdigest()


def adquirir(fonte: dict) -> dict:
    destino = RAW / fonte["arquivo"]
    status = "ja_preservado"
    if not destino.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(fonte["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            destino.write_bytes(resp.read())
        status = "baixado_agora"
    return {
        **fonte,
        "caminho": str(destino.relative_to(ROOT)),
        "pagina_dataset": PAGINA,
        "data_captura": DATA_CAPTURA,
        "status": status,
        "tamanho_bytes": destino.stat().st_size,
        "sha256": sha256(destino),
    }


def ler_csv_zip(path: Path, colunas: list[str]) -> pd.DataFrame:
    with zipfile.ZipFile(path) as z:
        nome = z.namelist()[0]
        bruto = z.read(nome)
    return pd.read_csv(io.BytesIO(bruto), sep=";", dtype=str, encoding="latin1", usecols=colunas)


def normalizar_categoria(valor) -> str | None:
    """`1 - Muito alta vulnerabilidade` e `5 - MUITO ALTA ...` viram o mesmo rotulo.

    A numeracao do prefixo inverte entre bases; so o texto e confiavel.
    """
    if pd.isna(valor):
        return None
    s = unicodedata.normalize("NFKD", str(valor)).encode("ascii", "ignore").decode().upper()
    s = s.split(" - ", 1)[-1].strip()
    return s if s in CATEGORIAS else None


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifesto = [adquirir(f) for f in FONTES]

    nominal = ler_csv_zip(
        RAW / FONTES[0]["arquivo"],
        ["co_ibge", "uf", "municipio", "faixa_atracao", "ivs", "categoria_ivs"],
    )
    nominal["ivs_admin"] = (
        pd.to_numeric(nominal["ivs"].str.replace(",", "."), errors="raise") / 10_000
    ).round(4)
    nominal["categoria_ivs_admin"] = nominal["categoria_ivs"].map(normalizar_categoria)
    nominal["faixa_atracao"] = nominal["faixa_atracao"].str.strip().str.upper()
    escore = (
        nominal[["co_ibge", "uf", "municipio", "ivs_admin", "categoria_ivs_admin", "faixa_atracao"]]
        .drop_duplicates()
        .sort_values("co_ibge")
        .reset_index(drop=True)
    )
    if escore["co_ibge"].duplicated().any():
        raise ValueError("municipio com mais de um escore, categoria ou faixa na relacao nominal")
    escore.to_csv(OUT / "a07_ivs_administrativo_municipio.csv", index=False)

    pmmb = ler_csv_zip(RAW / FONTES[1]["arquivo"], ["nivel", "co_ibge", "categoria_ivs"])
    pmmb = pmmb[pmmb["nivel"] == "MUNICIPAL"].copy()
    pmmb["categoria_ivs_admin"] = pmmb["categoria_ivs"].map(normalizar_categoria)
    categoria = (
        pmmb[["co_ibge", "categoria_ivs_admin"]].drop_duplicates().sort_values("co_ibge").reset_index(drop=True)
    )
    if categoria["co_ibge"].duplicated().any():
        raise ValueError("municipio com mais de uma categoria no consolidado PMMB")
    categoria.to_csv(OUT / "a07_categoria_ivs_pmmb_municipio.csv", index=False)

    resumo = {
        "data_execucao": DATA_CAPTURA,
        "outcomes_abertos": False,
        "colunas_lidas": {
            FONTES[0]["id"]: ["co_ibge", "uf", "municipio", "faixa_atracao", "ivs", "categoria_ivs"],
            FONTES[1]["id"]: ["nivel", "co_ibge", "categoria_ivs"],
        },
        "unidade_escore": "o campo `ivs` vem multiplicado por 10.000 (ex.: 3930,0 = 0,393); dividido na extracao",
        "fontes": manifesto,
        "saidas": {
            "output/aquisicao/a07_ivs_administrativo_municipio.csv": {
                "linhas": len(escore),
                "escore_ausente": int(escore["ivs_admin"].isna().sum()),
                "categoria_nao_reconhecida": int(escore["categoria_ivs_admin"].isna().sum()),
            },
            "output/aquisicao/a07_categoria_ivs_pmmb_municipio.csv": {
                "linhas": len(categoria),
                "categoria_ausente": int(categoria["categoria_ivs_admin"].isna().sum()),
            },
        },
        "selecao_da_cobertura": (
            "a relacao nominal so contem municipios com especialista ativo na data de referencia; "
            "a ausencia de escore e funcao do desfecho"
        ),
    }
    (OUT / "a07_manifesto_ivs_administrativo.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(resumo["saidas"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
