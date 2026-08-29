"""Audita a observabilidade financeira do PMM-E sem fabricar dados brutos.

A04 produz somente artefatos derivados. Valores anunciados sao extraidos de
uma fonte oficial preservada localmente. Na ausencia de resposta oficial
reproduzivel para execucao orcamentaria ou folha individual, o script registra
a lacuna e nao publica valores exatos.
"""

from __future__ import annotations

import csv
import hashlib
import html
import io
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW_REGRA_DIR = ROOT / "data" / "raw" / "aquisicao" / "ivs_regra"
OUTPUT_DIR = ROOT / "output" / "aquisicao"
GRADE_FILE = OUTPUT_DIR / "a04_grade_anunciada_2025.csv"
CATALOGO_FILE = OUTPUT_DIR / "a04_normas_regras_financeiras_pmme.json"
MANIFEST_FILE = OUTPUT_DIR / "a04_manifesto_pagamentos.json"
MATRIZ_FILE = OUTPUT_DIR / "a04_matriz_dose_financeira.json"

DATA_AUDITORIA = "2026-08-28"
FAQ_2025 = RAW_REGRA_DIR / "edital_sgtes_03_2025_faq_bolsa.html"
FAQ_2025_URL = (
    "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/"
    "chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/"
    "faq/qual-o-valor-da-bolsa-formacao"
)

FONTES_NORMATIVAS = [
    {
        "id": "faq_bolsa_chamamento_sgtes_3_2025",
        "documento": "FAQ oficial do Chamamento Publico SGTES/MS no 3/2025",
        "versao": "pagina preservada em 2026-08-28",
        "url_oficial": FAQ_2025_URL,
        "arquivo_local": "data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_faq_bolsa.html",
        "uso_a04": "fonte da grade de valores anunciados de 2025",
    },
    {
        "id": "lei_15233_2025",
        "documento": "Lei no 15.233, de 7 de outubro de 2025",
        "versao": "texto oficial preservado em 2026-08-28",
        "url_oficial": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15233.htm",
        "arquivo_local": "data/raw/aquisicao/ivs_regra/lei_15233_2025.html",
        "uso_a04": "marco legal; nao e fonte de execucao financeira individual",
    },
    {
        "id": "pagina_chamamento_sgtes_1_2026",
        "documento": "Pagina oficial do Chamamento Publico SGTES/MS no 1/2026",
        "versao": "pagina preservada em 2026-08-28",
        "url_oficial": (
            "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/"
            "chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/"
            "chamamento-publico-sgtes-ms-no-1-2026-pmm-e"
        ),
        "arquivo_local": "data/raw/aquisicao/ivs_regra/edital_sgtes_01_2026_ciclo2.html",
        "uso_a04": "pagina catalogada; o HTML preservado nao sustenta uma grade monetaria exata",
    },
    {
        "id": "pagina_edital_sgtes_28_2026",
        "documento": "Pagina oficial do Edital SGTES/MS no 28/2026",
        "versao": "pagina preservada em 2026-08-28",
        "url_oficial": (
            "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/"
            "chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e/edital"
        ),
        "arquivo_local": "data/raw/aquisicao/ivs_regra/edital_sgtes_06_2026_edital_28_2026_ciclo3.html",
        "uso_a04": "pagina catalogada; o HTML preservado nao sustenta uma grade monetaria exata",
    },
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def text_from_html(fragment: str) -> str:
    without_tags = re.sub(r"<[^>]+>", " ", fragment)
    return " ".join(html.unescape(without_tags).replace("\xa0", " ").split())


def extract_grade_2025() -> list[dict[str, object]]:
    """Extrai faixas e valores do FAQ oficial; falha se a estrutura mudar."""
    source = FAQ_2025.read_text(encoding="utf-8")
    response = re.search(
        r'<div id="form-widgets-resposta"[^>]*>(.*?)</div>',
        source,
        flags=re.DOTALL,
    )
    if response is None:
        raise ValueError("Bloco oficial de resposta nao localizado no FAQ de 2025")

    rows: list[dict[str, object]] = []
    for item in re.findall(r"<li>(.*?)</li>", response.group(1), flags=re.DOTALL):
        item_text = text_from_html(item)
        match = re.search(
            r"Faixa\s+(?P<faixa>\d+)\s*\((?P<categoria>[^)]+)\):\s*"
            r"R\$\s*(?P<valor>[\d.]+,\d{2})\s+mensais",
            item_text,
            flags=re.IGNORECASE,
        )
        if match is None:
            continue
        value = float(match.group("valor").replace(".", "").replace(",", "."))
        rows.append(
            {
                "ano_fonte": 2025,
                "ciclo_coberto": "Chamamento SGTES/MS no 3/2025",
                "faixa_atracao": int(match.group("faixa")),
                "categoria_ivs_declarada": match.group("categoria"),
                "tipo_valor": "valor_anunciado_mensal",
                "valor_anunciado_mensal_brl": value,
                "fonte_id": "faq_bolsa_chamamento_sgtes_3_2025",
                "fonte_url": FAQ_2025_URL,
                "fonte_arquivo": relative(FAQ_2025),
                "fonte_sha256": sha256_file(FAQ_2025),
                "localizador_evidencia": "div#form-widgets-resposta > ul > li",
            }
        )

    if len(rows) != 3 or {row["faixa_atracao"] for row in rows} != {1, 2, 3}:
        raise ValueError("FAQ de 2025 nao produziu exatamente as tres faixas esperadas")
    return sorted(rows, key=lambda row: int(row["faixa_atracao"]))


def write_grade(rows: list[dict[str, object]]) -> None:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    payload = stream.getvalue().encode("utf-8")

    # Evita truncar uma saída idêntica. Além de reduzir escrita desnecessária,
    # isso mantém a reexecução robusta quando um indexador do Windows abre o
    # CSV existente apenas para leitura durante a auditoria.
    if GRADE_FILE.is_file() and GRADE_FILE.read_bytes() == payload:
        return
    GRADE_FILE.write_bytes(payload)


def enrich_local_source(source: dict[str, str]) -> dict[str, object]:
    result: dict[str, object] = dict(source)
    path = ROOT / source["arquivo_local"]
    if not path.is_file():
        raise FileNotFoundError(path)
    result.update(
        {
            "status_aquisicao": "BRUTO_OFICIAL_LOCAL_REUTILIZADO",
            "tamanho_bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    )
    return result


def write_catalog() -> list[dict[str, object]]:
    sources = [enrich_local_source(source) for source in FONTES_NORMATIVAS]
    catalog = {
        "titulo": "Catalogo de fontes normativas usadas pela A04",
        "data_auditoria": DATA_AUDITORIA,
        "natureza": "artefato derivado; nao e resposta oficial bruta",
        "fontes": sources,
        "limite": (
            "Somente o FAQ de 2025 sustenta valores monetarios exatos na A04 atual. "
            "As paginas de 2026 sao catalogadas, mas nao foram usadas para publicar uma grade exata."
        ),
    }
    CATALOGO_FILE.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return sources


def build_manifest(sources: list[dict[str, object]]) -> dict[str, object]:
    derived = []
    for path, unit in (
        (GRADE_FILE, "faixa de atracao anunciada no FAQ de 2025"),
        (CATALOGO_FILE, "fonte normativa catalogada"),
    ):
        derived.append(
            {
                "arquivo": relative(path),
                "natureza": "DERIVADO",
                "unidade": unit,
                "tamanho_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    consultations = [
        {
            "id": "siop_execucao_orcamentaria",
            "url_consultada": "https://www.siop.planejamento.gov.br/",
            "endpoint_ou_recurso": None,
            "consulta": None,
            "filtros": None,
            "exercicio": "2025-2026",
            "unidade": "execucao orcamentaria agregada",
            "posicao_temporal": DATA_AUDITORIA,
            "status": "NAO_ADQUIRIDO",
            "arquivo_local": None,
            "sha256": None,
            "falha": (
                "A consulta anterior nao preservou resposta, endpoint, parametros nem filtros; "
                "por isso nenhum valor exato e publicado."
            ),
        },
        {
            "id": "portal_transparencia_pagamentos",
            "url_consultada": "https://portaldatransparencia.gov.br/despesas/pagamentos",
            "endpoint_ou_recurso": None,
            "consulta": None,
            "filtros": None,
            "exercicio": "2025-2026",
            "unidade": "pagamento federal por documento/favorecido",
            "posicao_temporal": DATA_AUDITORIA,
            "status": "NAO_ADQUIRIDO",
            "arquivo_local": None,
            "sha256": None,
            "falha": (
                "Nao ha resposta oficial local nem consulta reproduzivel que isole o PMM-E e o vincule "
                "simultaneamente a profissional, vaga, CNES e competencia."
            ),
        },
        {
            "id": "folha_individual_pmme",
            "url_consultada": None,
            "endpoint_ou_recurso": None,
            "consulta": None,
            "filtros": None,
            "exercicio": "2025-2026",
            "unidade": "profissional-vaga-competencia",
            "posicao_temporal": DATA_AUDITORIA,
            "status": "NAO_LOCALIZADO_EM_DADOS_ABERTOS",
            "arquivo_local": None,
            "sha256": None,
            "falha": (
                "Nao foi localizada publicacao oficial aberta com valor devido, empenhado, liquidado "
                "ou pago e chave comum de profissional, vaga, CNES e competencia."
            ),
        },
    ]

    return {
        "manifesto": "A04 - proveniencia financeira e observabilidade da dose",
        "data_auditoria": DATA_AUDITORIA,
        "regra_integridade": (
            "Valores exatos so sao publicados quando extraidos de resposta oficial preservada "
            "e acompanhados de URL, arquivo e hash."
        ),
        "fontes_oficiais_locais": sources,
        "consultas_sem_resposta_reproduzivel": consultations,
        "artefatos_derivados": derived,
        "execucao_orcamentaria_exata_publicada": False,
        "microdados_pagamento_individual_obtidos": False,
    }


def build_matrix(grade_rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "metadados": {
            "titulo": "Matriz de observabilidade dos estagios financeiros do PMM-E",
            "data_versao": DATA_AUDITORIA,
            "natureza": "diagnostico de disponibilidade; nao contem estimacao causal",
        },
        "estagios": [
            {
                "estagio": "valor_anunciado",
                "definicao": "valor mensal informado ao potencial participante na oferta normativa",
                "status": "OBSERVADO_PARCIALMENTE",
                "cobertura": "Chamamento SGTES/MS no 3/2025; tres faixas",
                "unidade": "faixa de atracao no chamamento",
                "chave_vaga_cnes_competencia": False,
                "evidencia": relative(GRADE_FILE),
                "limitacao": (
                    "O valor anunciado nao demonstra adesao, inicio, permanencia, valor devido "
                    "nem pagamento. A grade de 2026 nao foi confirmada por extracao local."
                ),
            },
            {
                "estagio": "valor_devido",
                "definicao": "obrigacao apurada para o participante em determinada competencia",
                "status": "NAO_OBSERVADO",
                "unidade_necessaria": "profissional-vaga-CNES-competencia",
                "limitacao": "Nao foram obtidos registros de elegibilidade mensal, glosas ou ajustes.",
            },
            {
                "estagio": "valor_empenhado",
                "definicao": "credito comprometido por nota de empenho",
                "status": "NAO_ADQUIRIDO_NESTA_AUDITORIA",
                "unidade_necessaria": "documento de empenho e classificacao orcamentaria",
                "limitacao": "Nenhuma resposta oficial reproduzivel foi preservada; nao ha valores exatos publicados.",
            },
            {
                "estagio": "valor_liquidado",
                "definicao": "despesa reconhecida apos verificacao do direito do credor",
                "status": "NAO_ADQUIRIDO_NESTA_AUDITORIA",
                "unidade_necessaria": "documento de liquidacao e classificacao orcamentaria",
                "limitacao": "Nenhuma resposta oficial reproduzivel foi preservada; nao ha valores exatos publicados.",
            },
            {
                "estagio": "valor_pago",
                "definicao": "desembolso registrado para o favorecido",
                "status": "NAO_OBSERVADO_COM_VINCULO_PMMe",
                "unidade_necessaria": "profissional-vaga-CNES-competencia e documento de pagamento",
                "limitacao": (
                    "Nao foi obtida fonte aberta com chaves que isolem o PMM-E e permitam ligacao "
                    "defensavel a vaga, CNES e competencia."
                ),
            },
        ],
        "grade_anunciada_observada": grade_rows,
        "tratamentos_candidatos": {
            "faixa_anunciada": {
                "status": "MENSURAVEL_PARCIALMENTE_COMO_REGRA_2025",
                "interpretacao_permitida": "oferta normativa anunciada, nao dose recebida",
            },
            "valor_devido": {
                "status": "NAO_MENSURAVEL_COM_DADOS_ATUAIS",
                "interpretacao_permitida": None,
            },
            "valor_recebido": {
                "status": "NAO_MENSURAVEL_COM_DADOS_ATUAIS",
                "interpretacao_permitida": None,
            },
        },
        "conclusao": (
            "A04 nao identifica efeito causal nem primeiro estagio financeiro. Com as fontes atuais, "
            "observa apenas parte da regra anunciada; a dose devida e recebida permanece ausente."
        ),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    grade = extract_grade_2025()
    write_grade(grade)
    sources = write_catalog()

    manifest = build_manifest(sources)
    MANIFEST_FILE.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    matrix = build_matrix(grade)
    MATRIZ_FILE.write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"[OK] Grade normativa extraida: {relative(GRADE_FILE)}")
    print(f"[OK] Catalogo de fontes: {relative(CATALOGO_FILE)}")
    print(f"[OK] Manifesto: {relative(MANIFEST_FILE)}")
    print(f"[OK] Matriz: {relative(MATRIZ_FILE)}")
    print("[LIMITE] Execucao orcamentaria e pagamento individual nao adquiridos.")


if __name__ == "__main__":
    main()
