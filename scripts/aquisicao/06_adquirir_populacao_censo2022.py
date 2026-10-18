"""Adquire a população residente municipal do Censo 2022 (IBGE/SIDRA).

Motivo: a coluna `populacao_2010` de `data/ivs_ipea_2010_municipios.csv` NÃO é
população residente total: é a população de um subgrupo (a linha de subgrupo da
base do Ipea que o arquivo traz; auditorias 16 e 19). Qualquer taxa "por
habitante" construída com ela sai inflada e distorcida de forma não uniforme.
Desde 18/10/2026 a população de 2010 vem da base oficial do Ipea (a08) e esta é a
de 2022, denominador do estoque por habitante.

Fonte: SIDRA, tabela 4709 (Censo Demográfico 2022), variável 93 (população
residente), nível territorial 6 (município), período 2022.

Roda sem rede quando o bruto já está em `data/raw/aquisicao/populacao/`. Para ser
determinístico, a data de aquisição é a do manifesto anterior quando o bruto tem o
mesmo SHA-256 registrado; só um download novo usa a data do dia.

Saídas:
- data/raw/aquisicao/populacao/sidra_4709_populacao_residente_2022.json (bruto)
- output/aquisicao/populacao_censo2022_municipios.csv (limpo)
- output/aquisicao/manifesto_populacao_censo2022.json (fonte, URL, data, hash)
"""

from __future__ import annotations

import csv
import hashlib
import json
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw" / "aquisicao" / "populacao"
OUT = RAIZ / "output" / "aquisicao"
URL = "https://apisidra.ibge.gov.br/values/t/4709/n6/all/v/93/p/2022?formato=json"
MANIFESTO = OUT / "manifesto_populacao_censo2022.json"


def sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def data_aquisicao(bruto: Path, baixado_agora: bool) -> str:
    """Data do download do bruto: do manifesto anterior, se o bruto é o mesmo."""
    if not baixado_agora and MANIFESTO.exists():
        anterior = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        if anterior.get("sha256_bruto") == sha256(bruto) and anterior.get("data_aquisicao"):
            return anterior["data_aquisicao"]
    return date.today().isoformat()


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    bruto = RAW / "sidra_4709_populacao_residente_2022.json"
    baixado_agora = not bruto.exists()
    if baixado_agora:
        with urllib.request.urlopen(URL, timeout=180) as resposta:
            bruto.write_bytes(resposta.read())

    registros = json.loads(bruto.read_text(encoding="utf-8"))
    cabecalho, linhas = registros[0], registros[1:]
    assert cabecalho["D2N"] == "Variável" and cabecalho["V"] == "Valor"

    limpo = OUT / "populacao_censo2022_municipios.csv"
    with limpo.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo, lineterminator="\n")  # LF: o hash registrado e o do arquivo versionado
        escritor.writerow(["co_ibge_7d", "co_ibge_6d", "no_municipio_uf", "populacao_2022"])
        total = 0
        for linha in linhas:
            if linha["D2N"] != "População residente" or linha["V"] in ("...", "-", "X"):
                continue
            codigo = linha["D1C"]
            valor = int(linha["V"])
            total += valor
            escritor.writerow([codigo, codigo[:6], linha["D1N"], valor])

    manifesto = {
        "natureza_dos_dados": "EMPIRICO",
        "fonte": "IBGE, Censo Demográfico 2022, via SIDRA tabela 4709, variável 93 (população residente)",
        "url": URL,
        "data_aquisicao": data_aquisicao(bruto, baixado_agora),
        "nivel_territorial": "município (n6)",
        "periodo": "2022",
        "registros_municipais": len(linhas),
        "populacao_total": total,
        "arquivo_bruto": str(bruto.relative_to(RAIZ)),
        "sha256_bruto": sha256(bruto),
        "arquivo_limpo": str(limpo.relative_to(RAIZ)),
        "sha256_limpo": sha256(limpo),
        "observacao": (
            "Denominador populacional de taxas por habitante (estoque pré por 10 mil na tipologia A2). "
            "Substitui a coluna populacao_2010 de data/ivs_ipea_2010_municipios.csv, que é a população de um "
            "subgrupo e não a residente total (auditorias 16 e 19)."
        ),
    }
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"municípios: {len(linhas)} | população total 2022: {total:,}".replace(",", "."))
    print("limpo:", limpo.relative_to(RAIZ))


if __name__ == "__main__":
    main()
