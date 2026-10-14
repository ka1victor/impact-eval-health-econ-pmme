"""Adquire o IVS 2010 municipal oficial da Plataforma IVS do Ipea.

A busca de 14/10/2026 mostrou que o escore administrativo de IVS que o
Ministério da Saúde publica na relação nominal do PMM-E é o IVS 2010 oficial
do Ipea, e que `data/ivs_ipea_2010_municipios.csv` não reproduz o IVS 2010
oficial. Este script baixa a base completa da plataforma, preserva o zip
(fora do Git: 201 MB), confere o SHA-256 e extrai as linhas municipais de
2010 para o total da população (cor, sexo e situação de domicílio "Total").

Não abre outcome. A validação contra o escore administrativo está em
`scripts/rdd_bolsa/04b_validar_ivs_oficial_escore_administrativo.py`.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "aquisicao" / "ivs_oficial"
OUT = ROOT / "output" / "aquisicao"

DATA_CAPTURA = "2026-10-14"
URL = "https://ivs.ipea.gov.br/api/cockpit/storage/uploads/databases/basecompletamunicipal.zip"
PAGINA = "https://ivs.ipea.gov.br/ (Base de Dados e Shapefiles -> Base Completa)"
ZIP = RAW / "basecompletamunicipal.zip"
SHA256_ESPERADO = "56f8a133cb60dc97ff1efdfcaccbb433768cc44e3c2aad366917cf8782e1ebbe"
NUMERICAS = ["ivs", "ivs_infraestrutura_urbana", "ivs_capital_humano", "ivs_renda_e_trabalho",
             "idhm", "idhm_long", "idhm_educ", "idhm_renda", "populacao", "renda_per_capita"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(1 << 20):
            h.update(bloco)
    return h.hexdigest()


def numero(v) -> float | None:
    if v is None or v == "" or v == "-":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", "."))


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    status = "ja_preservado"
    if not ZIP.exists():
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=600) as resp:
            ZIP.write_bytes(resp.read())
        status = "baixado_agora"
    hash_zip = sha256(ZIP)
    if hash_zip != SHA256_ESPERADO:
        raise ValueError(f"SHA-256 do zip mudou: {hash_zip}; a base do Ipea foi substituída")

    with zipfile.ZipFile(ZIP) as z:
        nome = z.namelist()[0]
        destino = RAW / nome
        if not destino.exists():
            z.extract(nome, RAW)

    wb = openpyxl.load_workbook(destino, read_only=True)
    ws = wb["Dados brutos IVS"]
    linhas = ws.iter_rows(values_only=True)
    cab = list(next(linhas))
    ix = {c: i for i, c in enumerate(cab)}
    registros = []
    for r in linhas:
        if r[ix["ano"]] != "2010" or r[ix["nivel"]] != "regiao,uf,rm,municipio":
            continue
        if not (str(r[ix["label_cor"]]).startswith("Total")
                and str(r[ix["label_sexo"]]).startswith("Total")
                and str(r[ix["label_sit_dom"]]).startswith("Total")):
            continue
        reg = {
            "co_ibge": str(r[ix["municipio_6digt"]]).strip()[:6],
            "nome_municipio_uf": r[ix["nome_municipio_uf"]],
            "uf": r[ix["uf"]],
        }
        for c in NUMERICAS:
            reg[c] = numero(r[ix[c]])
        registros.append(reg)
    wb.close()

    base = pd.DataFrame(registros).sort_values("co_ibge").reset_index(drop=True)
    if base["co_ibge"].duplicated().any():
        raise ValueError("município repetido no recorte 2010/total")
    base.to_csv(OUT / "a08_ivs_2010_oficial_municipio.csv", index=False)

    manifesto = {
        "data_execucao": DATA_CAPTURA,
        "fonte": {
            "url": URL,
            "pagina": PAGINA,
            "orgao": "Instituto de Pesquisa Econômica Aplicada (Ipea)",
            "descricao": "Atlas da Vulnerabilidade Social — base completa (dados brutos v2, arquivo de 28/02/2024)",
            "caminho_zip": str(ZIP.relative_to(ROOT)),
            "status": status,
            "tamanho_bytes": ZIP.stat().st_size,
            "sha256_zip": hash_zip,
            "arquivo_extraido": str(destino.relative_to(ROOT)),
            "sha256_xlsx": sha256(destino),
            "no_git": False,
            "motivo_fora_do_git": "201 MB; reprodutível por URL e SHA-256",
        },
        "recorte": "nivel = 'regiao,uf,rm,municipio', ano = 2010, cor/sexo/situação de domicílio = Total",
        "saida": {
            "arquivo": "output/aquisicao/a08_ivs_2010_oficial_municipio.csv",
            "municipios": int(len(base)),
            "ivs_ausente": int(base["ivs"].isna().sum()),
        },
        "observacao": (
            "data/ivs_ipea_2010_municipios.csv, usado até 14/10/2026 como IVS 2010, não reproduz esta base; "
            "ver docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md"
        ),
    }
    (OUT / "a08_manifesto_ivs_2010_oficial.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifesto["saida"], ensure_ascii=False))


if __name__ == "__main__":
    main()
