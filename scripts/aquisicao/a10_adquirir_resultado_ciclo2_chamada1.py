"""Adquire o resultado da 1a chamada do ciclo 2 do PMM-E (Edital SGTES/MS 3/2026).

O inventário de 18/10/2026 mostrou que o repositório tinha o quadro de vagas da
1a chamada do ciclo 2 e o resultado das vagas remanescentes de 05/05/2026 (9
linhas), mas não o resultado final da alocação da 1a chamada. O protocolo
multi-outcome (`docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`, F1.3
e F4 do ciclo 2) precisa dele. É publicação pública do Ministério da Saúde, na
página do Chamamento Público SGTES/MS nº 1/2026, bloco "Quadro de vagas e
Resultados" → "1ª chamada"; não é pedido de dados.

Arquivos (nome original da página, gravados em `data/raw/pmm_e/`):
- `resultado-final-pmme-2o-ciclo-25-05.xlsx`: "Resultado final PMME - 2º
  Ciclo", título interno "RESULTADO FINAL DA ALOCAÇÃO DOS(AS) CANDIDATOS(AS) –
  1ª CHAMADA" (aba Classificados: candidato × opção; aba Desclassificados);
- `resultado-final-vagas-remanescentes.xlsx`: "Resultado final com vagas
  remanescentes" (situação ATENDIDO), do mesmo bloco;
- `resultado-preliminar-pmme.xlsx`: "Resultado preliminar PMME - 2º Ciclo",
  usado só para documentar a escala da pontuação (diagnóstico do F4);
- `comunicado-oficial-alocados-24-03-2026.pdf`: comunicado que acompanha o
  resultado final e data a homologação (25/03 a 02/04/2026).

Arquivo presente com o SHA-256 registrado não é baixado de novo; com outro
hash, o script para sem tocar nele. O download vai para `<arquivo>.part` e só
recebe o nome final depois de conferido. Não lê nenhum outcome e não cruza nada
com o IVS: só grava o manifesto.

Saída: `output/aquisicao/a10_manifesto_ciclo2_chamada1.json`.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "pmm_e"
MANIFESTO = ROOT / "output" / "aquisicao" / "a10_manifesto_ciclo2_chamada1.json"

DATA_CAPTURA = "2026-10-18"
PAGINA = (
    "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/"
    "2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e"
)

ARQUIVOS = [
    {
        "arquivo": "resultado-final-pmme-2o-ciclo-25-05.xlsx",
        "rotulo_na_pagina": "Resultado final PMME - 2º Ciclo (bloco 1ª chamada)",
        "sha256": "8e85a28a57db1283cd3103065b04909b637cb76aab73482889e6b5fe50182e3c",
        "papel": "resultado final da alocação da 1a chamada do ciclo 2 (candidato × opção, CNES e curso, sem IBGE)",
        "data_referencia": (
            "não declarada no arquivo; publicado com o comunicado oficial de 24/03/2026 (homologação de 25/03 a "
            "02/04/2026); o sufixo '25-05' do nome não é explicado na página"
        ),
    },
    {
        "arquivo": "resultado-final-vagas-remanescentes.xlsx",
        "rotulo_na_pagina": "Resultado final com vagas remanescentes (bloco 1ª chamada)",
        "sha256": "70d67659cbfb7a3ec78452f76c70e9b9d0fce66ab5bb1b0b15934438edb83ad1",
        "papel": "preenchimento de vagas remanescentes da 1a chamada do ciclo 2 (situação ATENDIDO); só sensibilidade",
        "data_referencia": "não declarada no arquivo nem na página",
    },
    {
        "arquivo": "resultado-preliminar-pmme.xlsx",
        "rotulo_na_pagina": "Resultado preliminar PMME - 2º Ciclo (bloco 1ª chamada)",
        "sha256": "90b4c863f6e07e3eb98dc221dfe1622a7a69041e31b54e95d036e44782144803",
        "papel": "diagnóstico da escala da pontuação (barema do preliminar contra pontuação final); não entra em outcome",
        "data_referencia": "recurso de 12/03 a 13/03/2026 (ComunicadoResultado.pdf da mesma página)",
    },
    {
        "arquivo": "comunicado-oficial-alocados-24-03-2026.pdf",
        "rotulo_na_pagina": "Comunicado oficial - Atendidos (bloco 1ª chamada)",
        "sha256": "e48f31882c5a0b182fc7fe9353ef049e3db35ecb0f0b2b38669fb69289fb36c2",
        "papel": "data da publicação do resultado final da 1a chamada (24/03/2026)",
        "data_referencia": "2026-03-24",
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(1 << 20):
            h.update(bloco)
    return h.hexdigest()


def obter(item: dict, raw: Path = RAW) -> tuple[str, str, int]:
    """Põe no lugar o arquivo conferido; devolve status, SHA-256 e bytes."""
    destino = raw / item["arquivo"]
    if destino.exists():
        h = sha256(destino)
        if h != item["sha256"]:
            raise ValueError(
                f"{destino.name} preservado tem SHA-256 {h}, não o registrado ({item['sha256']}); "
                "arquivo substituído ou republicado. Não sobrescrevo."
            )
        return "ja_preservado", h, destino.stat().st_size
    raw.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".part")
    url = f"{PAGINA}/{item['arquivo']}"
    pedido = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (pesquisa academica PMM-E)"})
    # O portal gov.br derruba conexões de forma intermitente: até 4 tentativas.
    for tentativa in range(4):
        try:
            with urllib.request.urlopen(pedido, timeout=180) as resp, open(parcial, "wb") as f:
                while bloco := resp.read(1 << 20):
                    f.write(bloco)
            break
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if tentativa == 3:
                raise
            time.sleep(2 * (tentativa + 1))
    h = sha256(parcial)
    if h != item["sha256"]:
        parcial.unlink()
        raise ValueError(f"{item['arquivo']} baixado tem SHA-256 {h}, não o registrado ({item['sha256']})")
    parcial.replace(destino)
    return "baixado", h, destino.stat().st_size


def main() -> int:
    fontes = []
    for item in ARQUIVOS:
        status, h, n = obter(item)
        fontes.append(
            {
                "arquivo": item["arquivo"],
                "caminho": (RAW / item["arquivo"]).relative_to(ROOT).as_posix(),
                "url": f"{PAGINA}/{item['arquivo']}",
                "pagina": PAGINA,
                "rotulo_na_pagina": item["rotulo_na_pagina"],
                "fonte": "Ministério da Saúde, SGTES (publicação do PMM-E, Chamamento Público SGTES/MS nº 1/2026)",
                "papel": item["papel"],
                "data_referencia": item["data_referencia"],
                "data_captura": DATA_CAPTURA,
                "sha256": h,
                "tamanho_bytes": n,
            }
        )
        print(f"[{status}] {item['arquivo']} {h[:12]}… {n} bytes")
    manifesto = {
        "documento": "Aquisição do resultado da 1a chamada do ciclo 2 do PMM-E",
        "script": "scripts/aquisicao/a10_adquirir_resultado_ciclo2_chamada1.py",
        "data_captura": DATA_CAPTURA,
        "motivo": (
            "lacuna do inventário de 18/10/2026: o resultado final da alocação da 1a chamada do ciclo 2 não "
            "estava no repositório; necessário para F1.3, F1.1, F1.2 e F4 do ciclo 2 (protocolo E6)"
        ),
        "natureza": "publicação pública do Ministério da Saúde; não é pedido de dados",
        "conferencia_cruzada": (
            "o arquivo 'resultado-final-com-vagas-remanescentes.xlsx' da mesma página tem SHA-256 "
            "db39d51f…6e6, idêntico ao já preservado em data/raw/pmm_e/"
            "2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx"
        ),
        "outcomes_abertos": False,
        "dados_pessoais": (
            "os arquivos publicados contêm nome e CPF mascarado; são preservados como publicados e nenhum "
            "script grava nome ou CPF em output/"
        ),
        "fontes": fontes,
    }
    MANIFESTO.parent.mkdir(parents=True, exist_ok=True)
    tmp = MANIFESTO.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(MANIFESTO)
    print(f"[OK] {MANIFESTO.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
