"""Adquire o IVS 2010 municipal oficial da Plataforma IVS do Ipea.

A busca de 14/10/2026 mostrou que o escore administrativo de IVS que o
Ministério da Saúde publica na relação nominal do PMM-E é o IVS 2010 oficial
do Ipea, e que `data/ivs_ipea_2010_municipios.csv` não reproduz o IVS 2010
oficial. Este script baixa a base completa da plataforma, preserva o zip
(fora do Git: 201 MB), confere o SHA-256 e extrai as linhas municipais de
2010 para o total da população (cor, sexo e situação de domicílio "Total").

Cache: zip e planilha extraída ficam em `data/raw/aquisicao/ivs_oficial/`
(ignorado pelo Git). Zip presente com o SHA-256 registrado não é baixado de
novo; com outro hash, o script para sem tocar nele. O download vai para um
`.part` e só recebe o nome final depois de conferido. A planilha extraída é
reaproveitada se o hash confere e, senão, extraída de novo do zip conferido.

Não abre outcome. A validação contra o escore administrativo está em
`scripts/rdd_bolsa/04b_validar_ivs_oficial_escore_administrativo.py`.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
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
# Planilha `atlasivs_dadosbrutos_pt_v2.xlsx` dentro do zip (manifesto de 14/10/2026).
SHA256_XLSX_ESPERADO = "a06616fe6cbdcd8c2a1851da2c4e7b17d47c1237c45b5cad32c44da27a1903eb"
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


def obter_zip(destino: Path = ZIP, url: str = URL, esperado: str = SHA256_ESPERADO) -> tuple[str, str]:
    """Põe no lugar o zip conferido; devolve o status e o SHA-256.

    Zip já preservado com o hash registrado é reaproveitado. Com outro hash, o
    script para sem apagar nem sobrescrever o arquivo. O download vai para
    `<zip>.part` e só recebe o nome final depois de conferido: transferência
    interrompida não passa por base preservada.
    """
    if destino.exists():
        h = sha256(destino)
        if h != esperado:
            raise ValueError(
                f"{destino.name} preservado tem SHA-256 {h}, não o registrado ({esperado}): arquivo "
                "corrompido ou substituído. Apague-o para baixar de novo."
            )
        return "ja_preservado", h
    parcial = destino.with_name(destino.name + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=600) as resp, open(parcial, "wb") as f:
            shutil.copyfileobj(resp, f, 1 << 20)
        h = sha256(parcial)
        if h != esperado:
            raise ValueError(f"SHA-256 do zip mudou: {h}; a base do Ipea foi substituída")
        parcial.replace(destino)
    finally:
        parcial.unlink(missing_ok=True)
    return "baixado_agora", h


def extrair_planilha(arquivo_zip: Path = ZIP, esperado: str = SHA256_XLSX_ESPERADO) -> tuple[Path, str]:
    """Põe a planilha conferida ao lado do zip; devolve o caminho e o SHA-256.

    Extração anterior com o hash registrado é reaproveitada. Senão, a planilha é
    extraída de novo do zip, num diretório temporário, e só depois de conferida
    substitui o arquivo: extração interrompida não fica no lugar.
    """
    with zipfile.ZipFile(arquivo_zip) as z:
        nome = z.namelist()[0]
        destino = arquivo_zip.parent / nome
        if destino.exists() and sha256(destino) == esperado:
            return destino, esperado
        with tempfile.TemporaryDirectory(dir=arquivo_zip.parent) as tmp:
            extraido = Path(z.extract(nome, tmp))
            h = sha256(extraido)
            if h != esperado:
                raise ValueError(f"{nome} extraído tem SHA-256 {h}, não o registrado ({esperado})")
            extraido.replace(destino)
    return destino, h


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    status, hash_zip = obter_zip()
    destino, hash_xlsx = extrair_planilha()

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
            "sha256_xlsx": hash_xlsx,
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
