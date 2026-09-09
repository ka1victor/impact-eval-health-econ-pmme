"""Adquire a população residente municipal do Censo 2022 (IBGE/SIDRA).

Motivo: a única variável populacional do repositório, `populacao_2010` em
`data/ivs_ipea_2010_municipios.csv`, NÃO é população residente total. Soma
41.852.890 contra 190.755.799 do Censo 2010, e a razão para o valor real varia
de 0,10 a 0,42 entre municípios. Qualquer taxa "por habitante" construída com
ela sai inflada em ~4,5x e distorcida de forma não uniforme.

Fonte: SIDRA, tabela 4709 (Censo Demográfico 2022), variável 93 (população
residente), nível territorial 6 (município), período 2022.

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


def sha256(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    bruto = RAW / "sidra_4709_populacao_residente_2022.json"
    if not bruto.exists():
        with urllib.request.urlopen(URL, timeout=180) as resposta:
            bruto.write_bytes(resposta.read())

    registros = json.loads(bruto.read_text(encoding="utf-8"))
    cabecalho, linhas = registros[0], registros[1:]
    assert cabecalho["D2N"] == "Variável" and cabecalho["V"] == "Valor"

    limpo = OUT / "populacao_censo2022_municipios.csv"
    with limpo.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
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
        "fonte": "IBGE, Censo Demográfico 2022, via SIDRA tabela 4709, variável 93 (população residente)",
        "url": URL,
        "data_aquisicao": date.today().isoformat(),
        "nivel_territorial": "município (n6)",
        "periodo": "2022",
        "registros_municipais": len(linhas),
        "populacao_total": total,
        "arquivo_bruto": str(bruto.relative_to(RAIZ)),
        "sha256_bruto": sha256(bruto),
        "arquivo_limpo": str(limpo.relative_to(RAIZ)),
        "sha256_limpo": sha256(limpo),
        "observacao": (
            "Substitui `populacao_2010` como denominador populacional. Aquela coluna "
            "não é população residente total (soma 41.852.890 em 2010)."
        ),
    }
    (OUT / "manifesto_populacao_censo2022.json").write_text(
        json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"municípios: {len(linhas)} | população total 2022: {total:,}".replace(",", "."))
    print("limpo:", limpo.relative_to(RAIZ))


if __name__ == "__main__":
    main()
