"""Cria o plano reproduzivel da extracao mensal do CNES.

Por padrao, nao baixa os arquivos nacionais, que sao grandes. O download so e
feito com ``--download --confirm-large-download``. Os ZIPs brutos nunca sao
sobrescritos e recebem SHA-256 no manifesto apos a aquisicao.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "cnes"
MANIFEST = ROOT / "output" / "manifesto_aquisicao_cnes.json"
REFERER = "https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp"
CATALOG_DATE = "2026-08-27"
MONTHS = [
    f"{year}{month:02d}"
    for year, first, last in ((2025, 6, 12), (2026, 1, 7))
    for month in range(first, last + 1)
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0", "Referer": REFERER},
    )
    with urllib.request.urlopen(request, timeout=600) as response:
        first = response.read(2)
        if first != b"PK":
            raise RuntimeError(f"Resposta nao parece ZIP: {url}")
        temporary = destination.with_suffix(".zip.part")
        with temporary.open("wb") as handle:
            handle.write(first)
            for chunk in iter(lambda: response.read(1024 * 1024), b""):
                handle.write(chunk)
        temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--confirm-large-download", action="store_true")
    args = parser.parse_args()
    if args.download and not args.confirm_large_download:
        parser.error("use --confirm-large-download para baixar as bases nacionais")

    RAW.mkdir(parents=True, exist_ok=True)
    entries = []
    for month in MONTHS:
        filename = f"BASE_DE_DADOS_CNES_{month}.ZIP"
        url = f"http://cnes.datasus.gov.br/EstatisticasServlet?path={filename}"
        destination = RAW / filename
        if args.download and not destination.exists():
            print(f"Baixando {filename}...")
            download(url, destination)
        entries.append(
            {
                "competencia": month,
                "arquivo": filename,
                "url": url,
                "pagina_catalogo": REFERER,
                "cobertura": "Brasil, competencia mensal",
                "unidade": "cadastros CNES mensais; tabelas internas por estabelecimento, profissional-vinculo e infraestrutura",
                "caminho": destination.relative_to(ROOT).as_posix() if destination.exists() else None,
                "bytes": destination.stat().st_size if destination.exists() else None,
                "sha256": sha256(destination) if destination.exists() else None,
                "status": "preservado localmente" if destination.exists() else "planejado; bruto grande nao baixado",
            }
        )

    MANIFEST.parent.mkdir(exist_ok=True)
    MANIFEST.write_text(
        json.dumps(
            {
                "escopo": "CNES necessario para baseline, FTE, vinculos anteriores/simultaneos e infraestrutura pre-tratamento",
                "catalogo_consultado_em": CATALOG_DATE,
                "periodo": "2025-06 a 2026-07",
                "justificativa_periodo": "um mes anterior ao primeiro quadro de vagas e toda a janela pos-oferta publicamente disponivel",
                "download_executado": args.download,
                "fontes": entries,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Manifesto salvo em {MANIFEST}")


if __name__ == "__main__":
    main()
