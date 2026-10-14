"""Preserva a fonte publica do IVS administrativo usado pela SGTES/MS.

O IVS 2010 do Atlas (`data/ivs_ipea_2010_municipios.csv`) nao reproduz a faixa
da bolsa do PMM-E. O quadro de vagas do Chamamento SGTES/MS n. 2/2026 do PMMB
publica, para todos os municipios, o IVS que a propria SGTES usa e a categoria
que ela deriva dele. Este script baixa esse quadro e o edital correspondente
para `data/raw/aquisicao/ivs_regra/`, sem transformar nada, e registra URL,
data de aquisicao, tamanho e SHA-256 em manifesto.

Arquivo ja presente nao e baixado de novo: o bruto preservado e o observado, e
o hash do manifesto e o do arquivo em disco.
"""

from __future__ import annotations

import hashlib
import json
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "aquisicao" / "ivs_regra"
MANIFESTO = ROOT / "output" / "aquisicao" / "a07_manifesto_ivs_administrativo.json"

BASE = (
    "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/"
    "chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-2-2026-pmmb/"
)
FONTES = [
    {
        "id": "pmmb_2026_quadro_de_vagas",
        "arquivo": "pmmb_2026_quadro_de_vagas.xlsx",
        "url": BASE + "quadro-de-vagas.xlsx",
        "descricao": (
            "Quadro de vagas do Chamamento Publico SGTES/MS n. 2/2026 (PMMB). A aba "
            "'Lista de Municipios-Tipo Equipe' traz, para cada municipio, o IVS usado "
            "pela SGTES (tres casas decimais) e a 'CATEGORIA IVS' derivada dele."
        ),
        "uso": "running variable administrativa do RDD da bolsa (portao R1)",
    },
    {
        "id": "pmmb_2026_edital",
        "arquivo": "pmmb_2026_edital_22_2026.pdf",
        "url": BASE + "edital",
        "descricao": (
            "Edital SGTES/MS n. 22/2026 do PMMB. Cita o IVS/IPEA como criterio de "
            "priorizacao de vagas novas de eSF; nao publica safra nem algoritmo."
        ),
        "uso": "contexto normativo e cointervencao candidata no R2",
    },
]
CABECALHO = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def adquirir(fonte: dict, hoje: str) -> dict:
    destino = RAW_DIR / fonte["arquivo"]
    status = "JA_PRESERVADO"
    if not destino.exists():
        pedido = urllib.request.Request(fonte["url"], headers=CABECALHO)
        with urllib.request.urlopen(pedido, timeout=120) as resposta:
            conteudo = resposta.read()
        destino.write_bytes(conteudo)
        status = "BAIXADO_AGORA"
    return {
        "id": fonte["id"],
        "arquivo_local": str(destino.relative_to(ROOT)).replace("\\", "/"),
        "url_oficial": fonte["url"],
        "descricao": fonte["descricao"],
        "uso": fonte["uso"],
        "status_aquisicao": status,
        "data_verificacao": hoje,
        "tamanho_bytes": destino.stat().st_size,
        "sha256": sha256(destino),
    }


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    hoje = date.today().isoformat()
    anterior = json.loads(MANIFESTO.read_text(encoding="utf-8")) if MANIFESTO.exists() else {}
    datas = {f["id"]: f.get("data_aquisicao") for f in anterior.get("fontes", [])}
    fontes = []
    for fonte in FONTES:
        registro = adquirir(fonte, hoje)
        # A data de aquisicao e a do primeiro download; reexecucoes so verificam.
        registro["data_aquisicao"] = datas.get(fonte["id"]) or hoje
        fontes.append(registro)
    manifesto = {
        "manifesto": "A07 - IVS administrativo da SGTES/MS",
        "natureza": "bruto oficial preservado sem transformacao; hashes do arquivo em disco",
        "fontes": fontes,
        "limite": (
            "O quadro publica o valor e a categoria do IVS, mas nem ele nem o edital "
            "informam a safra ou a base de calculo. Os valores diferem do IVS 2010 do "
            "Atlas; a origem precisa ser documentada antes de qualquer afirmacao sobre "
            "a safra."
        ),
    }
    MANIFESTO.parent.mkdir(parents=True, exist_ok=True)
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for registro in fontes:
        print(f"[A07] {registro['id']}: {registro['status_aquisicao']} sha256={registro['sha256'][:12]}")


if __name__ == "__main__":
    main()
