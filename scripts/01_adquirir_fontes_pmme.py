"""Baixa, sem transformar, planilhas oficiais pequenas do PMM-E.

Os arquivos existentes nunca sao sobrescritos. Se o conteudo remoto mudar, o
script interrompe e exige que a mudanca de versao seja tratada explicitamente.
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "pmm_e"
MANIFEST = ROOT / "output" / "manifesto_fontes_pmme.json"


SOURCES = [
    {
        "id": "vagas_2025_c1",
        "arquivo": "2025_ciclo1_chamada1_vagas.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-mais-medicos-especialistas/quadro-de-vagas-pmm-e.xlsx",
        "cobertura": "ciclo 1, chamada 1, quadro original publicado em 24/07/2025",
        "unidade_declarada": "vaga/estabelecimento/curso",
    },
    {
        "id": "alocacao_2025_c1_retificada",
        "arquivo": "2025_ciclo1_chamada1_alocacao_retificada.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-mais-medicos-especialistas/quadro-1-profissionais-alocados-conforme-escolha-inicial-1a-ou-2a-opcao-retificado.xlsx",
        "cobertura": "ciclo 1, chamada 1, alocacao retificada",
        "unidade_declarada": "profissional alocado/vaga",
    },
    {
        "id": "homologados_2025_c1",
        "arquivo": "2025_ciclo1_chamada1_homologados.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/lista-de-homologados-medicos-especialistas-1a-chamada.xlsx",
        "cobertura": "ciclo 1, chamada 1, lista retificada em 29/09/2025",
        "unidade_declarada": "profissional homologado/curso/cota",
    },
    {
        "id": "vagas_alocados_2025_c1_ch2",
        "arquivo": "2025_ciclo1_chamada2_vagas_e_alocados.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/quadro-de-vagas-da-2a-chamada-e-a-relacao-de-profissionais-alocados-imediatos.xlsx",
        "cobertura": "ciclo 1, chamada 2, vagas e alocacao imediata",
        "unidade_declarada": "vaga e profissional alocado",
    },
    {
        "id": "classificacao_2025_c1_ch2",
        "arquivo": "2025_ciclo1_chamada2_classificacao_final.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/resultado-final-com-a-lista-de-classificacao-2a-chamada.xlsx",
        "cobertura": "ciclo 1, chamada 2, classificacao final",
        "unidade_declarada": "candidatura/classificacao",
    },
    {
        "id": "homologados_2025_c1_ch2",
        "arquivo": "2025_ciclo1_chamada2_homologados.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/lista-de-homologados-medicos-especialistas-2a-chamada.xlsx",
        "cobertura": "ciclo 1, chamada 2, homologados",
        "unidade_declarada": "profissional homologado",
    },
    {
        "id": "vagas_2026_c2_ch1_retificada",
        "arquivo": "2026_ciclo2_chamada1_vagas_retificadas.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/pmm-e-vagas-edital-2o-ciclo-19-de-marco-de-2026.xlsx",
        "cobertura": "ciclo 2, chamada 1, quadro retificado em 19/03/2026",
        "unidade_declarada": "vaga/estabelecimento/curso",
    },
    {
        "id": "resultado_2026_c2_ch1_remanescentes",
        "arquivo": "2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/resultado-final-com-vagas-remanescentes.xlsx",
        "cobertura": "ciclo 2, chamada 1, resultado final com remanescentes em 05/05/2026",
        "unidade_declarada": "candidatura/alocacao",
    },
    {
        "id": "vagas_2026_c2_ch2",
        "arquivo": "2026_ciclo2_chamada2_vagas.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/quadro-de-vagas-2a-chamada-de-16-abril-de-2026.xlsx",
        "cobertura": "ciclo 2, chamada 2, quadro publicado em 16/04/2026",
        "unidade_declarada": "vaga/estabelecimento/curso",
    },
    {
        "id": "resultado_2026_c2_ch2",
        "arquivo": "2026_ciclo2_chamada2_resultado_final.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/resultado-final-pmme-2o-ciclo-2a-chamada.xlsx",
        "cobertura": "ciclo 2, chamada 2, resultado final",
        "unidade_declarada": "candidatura/alocacao",
    },
    {
        "id": "adesao_gestores_2026_c3_final",
        "arquivo": "2026_ciclo3_adesao_gestores_resultado_final.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-5-2026-pmm-e/resultado-final.xlsx",
        "cobertura": "ciclo 3, resultado final da adesao de gestores",
        "unidade_declarada": "proposta de ente/estabelecimento/curso",
    },
    {
        "id": "vagas_2026_c3_retificada",
        "arquivo": "2026_ciclo3_chamada1_vagas_retificadas.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e/quadro-de-vagas-retificado-24-07-2026.xlsx",
        "cobertura": "ciclo 3, chamada 1, quadro retificado em 24/07/2026",
        "unidade_declarada": "vaga/estabelecimento/curso",
    },
    {
        "id": "resultado_2026_c3_sub_judice",
        "arquivo": "2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e/resultado-final-3o-ciclo-sub-judice.xlsx",
        "cobertura": "ciclo 3, chamada 1, resultado final de 25/08/2026, sub judice",
        "unidade_declarada": "candidatura/alocacao",
    },
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; PMME-data-audit/1.0)",
            "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        data = response.read()
    if not data.startswith(b"PK"):
        raise RuntimeError(f"Resposta nao parece XLSX: {url}")
    return data


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(exist_ok=True)
    entries = []

    for source in SOURCES:
        destination = RAW_DIR / source["arquivo"]
        try:
            remote = download(source["url"])
        except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as error:
            entries.append(
                {
                    **source,
                    "fonte": "Ministerio da Saude",
                    "data_extracao": date.today().isoformat(),
                    "caminho": None,
                    "bytes": None,
                    "sha256": None,
                    "transformacao": None,
                    "disponibilidade": "link oficial localizado, mas download falhou",
                    "erro": str(error),
                }
            )
            print(f"FALHA {source['arquivo']} {error}")
            continue
        remote_hash = sha256(remote)

        if destination.exists():
            local = destination.read_bytes()
            local_hash = sha256(local)
            if local_hash != remote_hash:
                raise RuntimeError(
                    f"Fonte mudou no servidor; arquivo local preservado: {destination.name}"
                )
        else:
            destination.write_bytes(remote)
            local_hash = remote_hash

        entries.append(
            {
                **source,
                "fonte": "Ministerio da Saude",
                "data_extracao": date.today().isoformat(),
                "caminho": destination.relative_to(ROOT).as_posix(),
                "bytes": destination.stat().st_size,
                "sha256": local_hash,
                "transformacao": "nenhuma; bytes oficiais preservados",
                "disponibilidade": "baixado e preservado localmente",
            }
        )
        print(f"OK {destination.name} {local_hash}")

    MANIFEST.write_text(
        json.dumps(
            {
                "escopo": "planilhas publicas pequenas do PMM-E",
                "gerado_em": date.today().isoformat(),
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
