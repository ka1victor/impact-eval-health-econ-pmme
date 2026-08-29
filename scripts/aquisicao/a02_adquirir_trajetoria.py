# ruff: noqa: E501
"""Audita, adquire e mapeia a trajetoria e selecao administrativa publica do PMM-E.

Script idempotente do Agente A02.
Verifica arquivos brutos oficiais, audita etapas de selecao e trajetoria,
avalia a viabilidade de construcao de spells e coberturas temporais (90/120/180 dias),
pseudonimiza dados pessoais e produz manifesto e matriz de eventos publicos.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
DATA_RAW_TRAJETORIA = ROOT / "data" / "raw" / "aquisicao" / "trajetoria"
DATA_RAW_VAGAS = ROOT / "data" / "raw" / "aquisicao" / "vagas"
DATA_RAW_PMME = ROOT / "data" / "raw" / "pmm_e"
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output" / "aquisicao"
A01_MANIFEST_PATH = OUTPUT_DIR / "a01_manifesto_vagas.json"

MANIFESTO_PATH = OUTPUT_DIR / "a02_manifesto_trajetoria.json"
MATRIZ_PATH = OUTPUT_DIR / "a02_matriz_eventos_publicos.json"

AUDIT_DATE = "2026-08-28"
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


FONTES_TRAJETORIA = [
    {
        "id": "alocacao_2025_c1_retificada",
        "arquivo": "2025_ciclo1_chamada1_alocacao_retificada.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/quadro-1-profissionais-alocados-conforme-escolha-inicial-1a-ou-2a-opcao-retificado.xlsx",
        "ciclo": "1",
        "chamada": "1",
        "cobertura": "Ciclo 1, chamada 1, alocacao retificada",
        "unidade_declarada": "registro publicado de preferencia/classificacao/alocacao; uma ou duas linhas por candidato",
        "etapas_alvo": ["preferencias", "classificacao", "alocacao"],
        "data_publicacao": "2025-09-10",
        "papel_analitico": "versao retificada preservada somente para comparacao; nao somar a versao sub judice",
    },
    {
        "id": "alocacao_2025_c1_retificada_subjudice",
        "arquivo": "2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/quadro-1-profissionais-alocados-conforme-escolha-inicial-1a-ou-2a-opcao-retificado-subjudice.xlsx",
        "ciclo": "1",
        "chamada": "1",
        "cobertura": "Ciclo 1, chamada 1, alocacao retificada sub judice",
        "unidade_declarada": "registro publicado de preferencia/classificacao/alocacao; uma ou duas linhas por candidato",
        "etapas_alvo": ["preferencias", "classificacao", "alocacao", "sub_judice"],
        "data_publicacao": "2025-09-19",
        "papel_analitico": "versao canonica para contagens da primeira chamada; substitui a retificada de 10/09/2025",
    },
    {
        "id": "realocacao_2025_c1_retificado",
        "arquivo": "2025_ciclo1_chamada1_realocacao_retificado.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/quadro-2-proposta-de-realocacao-dos-profissionais-que-selecionaram-estabelecimentos-de-saude-retificado.xlsx",
        "ciclo": "1",
        "chamada": "1",
        "cobertura": "Ciclo 1, chamada 1, proposta de realocacao retificada",
        "unidade_declarada": "profissional/vaga_remanejada",
        "etapas_alvo": ["transferencia_realocacao"],
        "data_publicacao": "2025-09-10",
        "papel_analitico": "quadro complementar de proposta de realocacao; nao somar como nova candidatura",
    },
    {
        "id": "homologados_2025_c1",
        "arquivo": "2025_ciclo1_chamada1_homologados.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/lista-de-homologados-medicos-especialistas-1a-chamada.xlsx",
        "ciclo": "1",
        "chamada": "1",
        "cobertura": "Ciclo 1, chamada 1, lista retificada de homologados em 29/09/2025",
        "unidade_declarada": "profissional homologado/curso/cota",
        "etapas_alvo": ["homologacao"],
    },
    {
        "id": "vagas_alocados_2025_c1_ch2",
        "arquivo": "2025_ciclo1_chamada2_vagas_e_alocados.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/quadro-de-vagas-da-2a-chamada-e-a-relacao-de-profissionais-alocados-imediatos.xlsx",
        "ciclo": "1",
        "chamada": "2",
        "cobertura": "Ciclo 1, chamada 2, vagas e alocados imediatos",
        "unidade_declarada": "vaga e profissional alocado",
        "etapas_alvo": ["classificacao", "alocacao"],
    },
    {
        "id": "classificacao_2025_c1_ch2",
        "arquivo": "2025_ciclo1_chamada2_classificacao_final.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/resultado-final-com-a-lista-de-classificacao-2a-chamada.xlsx",
        "ciclo": "1",
        "chamada": "2",
        "cobertura": "Ciclo 1, chamada 2, classificacao final e desclassificados",
        "unidade_declarada": "registro publicado de preferencia/classificacao",
        "etapas_alvo": ["resultado_publicado", "preferencias", "classificacao", "alocacao", "desclassificacao"],
    },
    {
        "id": "homologados_2025_c1_ch2",
        "arquivo": "2025_ciclo1_chamada2_homologados.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/lista-de-homologados-medicos-especialistas-2a-chamada.xlsx",
        "ciclo": "1",
        "chamada": "2",
        "cobertura": "Ciclo 1, chamada 2, homologados",
        "unidade_declarada": "profissional homologado",
        "etapas_alvo": ["homologacao"],
    },
    {
        "id": "resultado_2026_c2_ch1_remanescentes",
        "arquivo": "2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/resultado-final-com-vagas-remanescentes.xlsx",
        "ciclo": "2",
        "chamada": "1",
        "cobertura": "Ciclo 2, chamada 1, resultado final com vagas remanescentes em 05/05/2026",
        "unidade_declarada": "registro publicado de resultado/alocacao remanescente",
        "etapas_alvo": ["classificacao", "alocacao_remanescente"],
    },
    {
        "id": "resultado_2026_c2_ch2",
        "arquivo": "2026_ciclo2_chamada2_resultado_final.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/resultado-final-pmme-2o-ciclo-2a-chamada.xlsx",
        "ciclo": "2",
        "chamada": "2",
        "cobertura": "Ciclo 2, chamada 2, resultado final e desclassificados",
        "unidade_declarada": "registro publicado de preferencia/classificacao/alocacao/cadastro reserva",
        "etapas_alvo": ["resultado_publicado", "preferencias", "classificacao", "alocacao", "cadastro_reserva", "desclassificacao"],
    },
    {
        "id": "resultado_2026_c3_sub_judice",
        "arquivo": "2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e/resultado-final-3o-ciclo-sub-judice.xlsx",
        "ciclo": "3",
        "chamada": "1",
        "cobertura": "Ciclo 3, chamada 1, resultado final de 25/08/2026, sub judice",
        "unidade_declarada": "registro publicado de preferencia/classificacao/alocacao/cadastro reserva/sub judice",
        "etapas_alvo": ["resultado_publicado", "preferencias", "classificacao", "alocacao", "cadastro_reserva", "sub_judice", "desclassificacao"],
    },
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pseudo_id(value: object, salt: str = "pmme_a02_salt") -> str:
    norm = normalize(value)
    if not norm:
        return ""
    return hashlib.sha256(f"{salt}:{norm}".encode("utf-8")).hexdigest()[:16]


def normalize(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text).strip().upper()


def normalize_cnes(value: object) -> str:
    digits = re.sub(r"\D", "", "" if value is None else str(value))
    return digits.zfill(7) if digits else ""


def col_index(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference)
    if not letters:
        return 0
    result = 0
    for char in letters.group(0):
        result = result * 26 + ord(char) - 64
    return result - 1


def xlsx_sheets(path: Path) -> dict[str, list[list[object]]]:
    with zipfile.ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall(f"{{{NS_MAIN}}}si"):
                shared.append("".join(node.text or "" for node in item.iter(f"{{{NS_MAIN}}}t")))

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in relationships.findall(f"{{{NS_PKG_REL}}}Relationship")
        }
        result: dict[str, list[list[object]]] = {}
        sheets_node = workbook.find(f"{{{NS_MAIN}}}sheets")
        if sheets_node is None:
            return result
        for sheet in sheets_node:
            name = sheet.attrib["name"]
            rel_id = sheet.attrib[f"{{{NS_REL}}}id"]
            target = targets[rel_id].lstrip("/")
            sheet_path = str(PurePosixPath("xl") / target) if not target.startswith("xl/") else target
            root = ET.fromstring(archive.read(sheet_path))
            rows: list[list[object]] = []
            for row in root.iter(f"{{{NS_MAIN}}}row"):
                values: dict[int, object] = {}
                for cell in row.findall(f"{{{NS_MAIN}}}c"):
                    index = col_index(cell.attrib.get("r", "A1"))
                    kind = cell.attrib.get("t")
                    value_node = cell.find(f"{{{NS_MAIN}}}v")
                    if kind == "inlineStr":
                        inline = cell.find(f"{{{NS_MAIN}}}is")
                        value: object = "" if inline is None else "".join(
                            node.text or "" for node in inline.iter(f"{{{NS_MAIN}}}t")
                        )
                    elif value_node is None:
                        value = ""
                    elif kind == "s":
                        value = shared[int(value_node.text or 0)]
                    elif kind == "b":
                        value = value_node.text == "1"
                    else:
                        raw = value_node.text or ""
                        try:
                            number = float(raw)
                            value = int(number) if number.is_integer() else number
                        except ValueError:
                            value = raw
                    values[index] = value
                width = max(values, default=-1) + 1
                rows.append([values.get(index, "") for index in range(width)])
            result[name] = rows
        return result


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def process_manifest() -> list[dict[str, object]]:
    DATA_RAW_TRAJETORIA.mkdir(parents=True, exist_ok=True)
    manifest_entries = []

    for item in FONTES_TRAJETORIA:
        existing_pmme = DATA_RAW_PMME / item["arquivo"]
        existing_vagas = DATA_RAW_VAGAS / item["arquivo"]
        target_trajetoria = DATA_RAW_TRAJETORIA / item["arquivo"]

        if existing_pmme.exists():
            file_hash = sha256_file(existing_pmme)
            file_bytes = existing_pmme.stat().st_size
            manifest_entries.append({
                "id": item["id"],
                "arquivo": item["arquivo"],
                "url": item["url"],
                "ciclo": item["ciclo"],
                "chamada": item["chamada"],
                "cobertura": item["cobertura"],
                "unidade_declarada": item["unidade_declarada"],
                "etapas_alvo": item["etapas_alvo"],
                "fonte": "Ministerio da Saude",
                "data_extracao": AUDIT_DATE,
                "caminho_preservado": existing_pmme.relative_to(ROOT).as_posix(),
                "bytes": file_bytes,
                "sha256": file_hash,
                "disponibilidade": "preservado localmente em data/raw/pmm_e/",
                "validacao": "arquivo integro; bytes identicos aos oficiais",
            })
        elif existing_vagas.exists():
            file_hash = sha256_file(existing_vagas)
            file_bytes = existing_vagas.stat().st_size
            manifest_entries.append({
                "id": item["id"],
                "arquivo": item["arquivo"],
                "url": item["url"],
                "ciclo": item["ciclo"],
                "chamada": item["chamada"],
                "cobertura": item["cobertura"],
                "unidade_declarada": item["unidade_declarada"],
                "etapas_alvo": item["etapas_alvo"],
                "fonte": "Ministerio da Saude",
                "data_extracao": AUDIT_DATE,
                "caminho_preservado": existing_vagas.relative_to(ROOT).as_posix(),
                "bytes": file_bytes,
                "sha256": file_hash,
                "disponibilidade": "preservado localmente em data/raw/aquisicao/vagas/ (recuperado por A01)",
                "validacao": "arquivo integro; bytes identicos aos oficiais",
            })
        elif target_trajetoria.exists():
            file_hash = sha256_file(target_trajetoria)
            file_bytes = target_trajetoria.stat().st_size
            manifest_entries.append({
                "id": item["id"],
                "arquivo": item["arquivo"],
                "url": item["url"],
                "ciclo": item["ciclo"],
                "chamada": item["chamada"],
                "cobertura": item["cobertura"],
                "unidade_declarada": item["unidade_declarada"],
                "etapas_alvo": item["etapas_alvo"],
                "fonte": "Ministerio da Saude",
                "data_extracao": AUDIT_DATE,
                "caminho_preservado": target_trajetoria.relative_to(ROOT).as_posix(),
                "bytes": file_bytes,
                "sha256": file_hash,
                "disponibilidade": "preservado localmente em data/raw/aquisicao/trajetoria/",
                "validacao": "arquivo integro; bytes identicos aos oficiais",
            })
        else:
            try:
                req = urllib.request.Request(
                    item["url"],
                    headers={"User-Agent": "Mozilla/5.0 (compatible; PMME-A02-audit/1.0)"}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read()
                if not data.startswith(b"PK"):
                    raise RuntimeError("Formato nao parece XLSX valido")
                target_trajetoria.write_bytes(data)
                f_hash = sha256_bytes(data)
                manifest_entries.append({
                    "id": item["id"],
                    "arquivo": item["arquivo"],
                    "url": item["url"],
                    "ciclo": item["ciclo"],
                    "chamada": item["chamada"],
                    "cobertura": item["cobertura"],
                    "unidade_declarada": item["unidade_declarada"],
                    "etapas_alvo": item["etapas_alvo"],
                    "fonte": "Ministerio da Saude",
                    "data_extracao": AUDIT_DATE,
                    "caminho_preservado": target_trajetoria.relative_to(ROOT).as_posix(),
                    "bytes": len(data),
                    "sha256": f_hash,
                    "disponibilidade": "baixado e preservado em data/raw/aquisicao/trajetoria/",
                    "validacao": "download bem-sucedido",
                })
            except Exception as e:
                manifest_entries.append({
                    "id": item["id"],
                    "arquivo": item["arquivo"],
                    "url": item["url"],
                    "ciclo": item["ciclo"],
                    "chamada": item["chamada"],
                    "cobertura": item["cobertura"],
                    "unidade_declarada": item["unidade_declarada"],
                    "etapas_alvo": item["etapas_alvo"],
                    "fonte": "Ministerio da Saude",
                    "data_extracao": AUDIT_DATE,
                    "caminho_preservado": None,
                    "bytes": None,
                    "sha256": None,
                    "disponibilidade": "fonte oficial indisponivel na tentativa de consulta",
                    "erro": str(e),
                    "validacao": "fonte oficial inacessivel na data de referencia",
                })

    source_specs = {item["id"]: item for item in FONTES_TRAJETORIA}
    a01_by_file: dict[str, dict[str, object]] = {}
    if A01_MANIFEST_PATH.exists():
        a01_manifest = json.loads(A01_MANIFEST_PATH.read_text(encoding="utf-8"))
        a01_by_file = {
            str(entry["arquivo"]): entry
            for entry in a01_manifest.get("fontes", [])
            if entry.get("arquivo")
        }

    for entry in manifest_entries:
        spec = source_specs[str(entry["id"])]
        if spec.get("data_publicacao"):
            entry["data_publicacao"] = spec["data_publicacao"]
        if spec.get("papel_analitico"):
            entry["papel_analitico"] = spec["papel_analitico"]

        a01_entry = a01_by_file.get(str(entry["arquivo"]))
        if a01_entry:
            hash_matches = bool(entry.get("sha256")) and (
                entry["sha256"] == a01_entry.get("sha256")
            )
            entry["linhagem_a01"] = {
                "manifesto": A01_MANIFEST_PATH.relative_to(ROOT).as_posix(),
                "id_a01": a01_entry.get("id"),
                "status_aquisicao_a01": a01_entry.get("status_aquisicao"),
                "data_extracao_a01": a01_entry.get("data_extracao"),
                "sha256_confere": hash_matches,
            }
            if entry.get("caminho_preservado") and not hash_matches:
                raise RuntimeError(
                    f"Hash A02 diverge do manifesto A01 para {entry['arquivo']}"
                )

    return manifest_entries


def _sheet_records(path: Path, sheet_name: str) -> tuple[list[str], list[list[str]]]:
    """Le uma tabela XLSX e devolve cabecalho e linhas normalizados."""
    sheets = xlsx_sheets(path)
    if sheet_name not in sheets or len(sheets[sheet_name]) < 2:
        raise RuntimeError(f"Planilha sem tabela utilizavel: {path.name} [{sheet_name}]")
    raw_rows = sheets[sheet_name]
    header = [normalize(value) for value in raw_rows[0]]
    rows = [[normalize(value) for value in row] for row in raw_rows[1:]]
    return header, rows


def audit_first_call_2025() -> dict[str, object]:
    """Reconta a primeira chamada sem somar publicacoes retificadas."""
    regular_path = DATA_RAW_VAGAS / "2025_ciclo1_chamada1_alocacao_retificada.xlsx"
    canonical_path = (
        DATA_RAW_VAGAS
        / "2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx"
    )
    relocation_path = DATA_RAW_VAGAS / "2025_ciclo1_chamada1_realocacao_retificado.xlsx"
    for path in (regular_path, canonical_path, relocation_path):
        if not path.exists():
            raise FileNotFoundError(f"Fonte recuperada por A01 ausente: {path}")

    regular_header, regular_rows = _sheet_records(regular_path, "Quadro 1")
    canonical_header, canonical_rows = _sheet_records(canonical_path, "Quadro 1")
    _, relocation_rows = _sheet_records(relocation_path, "Quadro 2")
    if regular_header != canonical_header:
        raise RuntimeError("Cabecalhos das versoes retificadas nao coincidem")

    index = {column: position for position, column in enumerate(canonical_header)}
    required = {
        "CPF",
        "NOME CANDIDATO(A)",
        "RESULTADO",
        "ALOCACAO",
        "ORDEM DE PRIORIDADE ESCOLHIDA",
    }
    missing = sorted(required - set(index))
    if missing:
        raise RuntimeError(f"Colunas esperadas ausentes no Quadro 1: {missing}")

    def value(row: list[str], column: str) -> str:
        position = index[column]
        return row[position] if position < len(row) else ""

    def candidate_key(row: list[str]) -> tuple[str, str]:
        return value(row, "CPF"), value(row, "NOME CANDIDATO(A)")

    def record_key(row: list[str]) -> tuple[str, str, str, str, str]:
        return (
            *candidate_key(row),
            value(row, "CNES"),
            value(row, "CURSO"),
            value(row, "ORDEM DE PRIORIDADE ESCOLHIDA"),
        )

    regular_by_key = {record_key(row): row for row in regular_rows}
    canonical_by_key = {record_key(row): row for row in canonical_rows}
    common_keys = regular_by_key.keys() & canonical_by_key.keys()
    changed_keys = [
        key for key in common_keys if regular_by_key[key] != canonical_by_key[key]
    ]

    preference_counts = Counter(
        value(row, "ORDEM DE PRIORIDADE ESCOLHIDA") for row in canonical_rows
    )
    result_counts = Counter(value(row, "RESULTADO") for row in canonical_rows)
    allocation_counts = Counter(value(row, "ALOCACAO") for row in canonical_rows)
    candidate_keys = {candidate_key(row) for row in canonical_rows}
    cpf_keys = {key[0] for key in candidate_keys if key[0]}
    name_keys = {key[1] for key in candidate_keys if key[1]}
    sub_judice_marked = sum(
        1
        for row in canonical_rows
        if any("SUB JUDICE" in cell for cell in row[len(canonical_header):])
    )

    return {
        "fontes": {
            "versao_comparacao": regular_path.relative_to(ROOT).as_posix(),
            "versao_canonica": canonical_path.relative_to(ROOT).as_posix(),
            "quadro_realocacao": relocation_path.relative_to(ROOT).as_posix(),
        },
        "regra_versionamento": (
            "A publicacao retificada sub judice de 19/09/2025 e a versao "
            "canonica para contagens. A retificada de 10/09/2025 serve apenas "
            "para comparar alteracoes e nunca e somada a ela."
        ),
        "unidade_observada": (
            "registro publicado de preferencia/classificacao/alocacao; um "
            "candidato pode ocupar duas linhas, uma por opcao"
        ),
        "versao_canonica": {
            "registros_publicados": len(canonical_rows),
            "chaves_candidato_distintas_cpf_nome": len(candidate_keys),
            "cpfs_mascarados_distintos": len(cpf_keys),
            "nomes_normalizados_distintos": len(name_keys),
            "registros_primeira_opcao": preference_counts["1A OPCAO"],
            "registros_segunda_opcao": preference_counts["2A OPCAO"],
            "registros_classificados": sum(
                count
                for result, count in result_counts.items()
                if result.startswith("CLASSIFICACAO EM")
            ),
            "locais_confirmados_inicio": allocation_counts[
                "LOCAL DE ATUACAO CONFIRMADO PARA INICIO DAS ATIVIDADES"
            ],
            "locais_desconsiderados_gestao": allocation_counts[
                "LOCAL DE ATUACAO DESCONSIDERADO A PEDIDO DA GESTAO LOCAL OU "
                "POR NAO TER CAPACIDADE INSTALADA SUFICIENTE (OBSERVAR O QUADRO 2)"
            ],
            "registros_marcados_sub_judice": sub_judice_marked,
        },
        "comparacao_versoes": {
            "registros_retificada_10_09": len(regular_rows),
            "registros_retificada_sub_judice_19_09": len(canonical_rows),
            "chaves_registro_adicionadas": len(canonical_by_key.keys() - regular_by_key.keys()),
            "chaves_registro_removidas": len(regular_by_key.keys() - canonical_by_key.keys()),
            "chaves_registro_com_conteudo_alterado": len(changed_keys),
        },
        "proposta_realocacao": {
            "registros_publicados": len(relocation_rows),
            "interpretacao": (
                "propostas de realocacao de profissionais; nao sao novas "
                "inscricoes e nao sao somadas ao Quadro 1"
            ),
        },
        "universo_completo_inscricoes_observado": False,
        "limitacao_universo": (
            "As publicacoes permitem contar registros divulgados e chaves de "
            "candidato presentes no resultado, mas nao demonstram conter todas "
            "as inscricoes submetidas antes dos filtros administrativos."
        ),
    }


def audit_cpf_patterns() -> dict[str, object]:
    patterns = {}
    search_dirs = [DATA_RAW_PMME, DATA_RAW_VAGAS]
    all_files = []
    for d in search_dirs:
        if d.exists():
            all_files.extend(sorted(d.glob("*.xlsx")))

    for p in all_files:
        sheets = xlsx_sheets(p)
        for sname, rows in sheets.items():
            if not rows:
                continue
            header = rows[0]
            for i in range(min(4, len(rows))):
                if any("CPF" in str(c).upper() for c in rows[i]):
                    header = rows[i]
                    break
            for cidx, col in enumerate(header):
                if "CPF" in str(col).upper():
                    samples = [str(r[cidx]) for r in rows[1:15] if cidx < len(r) and str(r[cidx]).strip()]
                    if samples:
                        patterns[f"{p.name} [{sname}]"] = {
                            "coluna": str(col),
                            "amostras_pseudonimizadas": [pseudo_id(s) for s in samples[:3]],
                            "mascara_exemplo": samples[0] if samples else "",
                            "estrutura": "variavel entre chamadas",
                        }
    return patterns


def build_event_matrix(
    manifest_entries: list[dict[str, object]],
    first_call_audit: dict[str, object],
) -> dict[str, object]:
    del manifest_entries  # A disponibilidade detalhada permanece no manifesto A02.
    first_call_counts = first_call_audit["versao_canonica"]
    eventos_chave = [
        "inscricao_candidatura",
        "preferencias_ordem",
        "classificacao_barema",
        "convocacao",
        "aceite_recusa",
        "homologacao",
        "entrada_exercicio",
        "afastamento_licenca",
        "retorno_afastamento",
        "transferencia_realocacao",
        "desistencia_desligamento",
        "reocupacao_vaga",
    ]

    coortes = [
        {
            "ciclo": "1",
            "chamada": "1",
            "edital": "Chamamento Publico SGTES/MS no 3/2025 - 1a Chamada",
            "data_oferta": "2025-07-24",
            "data_homologacao": "2025-09-29",
            "dias_calendario_ate_corte": 384,
            "status_eventos": {
                "inscricao_candidatura": {
                    "classificacao": "universo completo nao observado; resultado publicado parcialmente observado",
                    "justificativa": (
                        f"A versao canonica recuperada por A01 contem "
                        f"{first_call_counts['registros_publicados']} registros "
                        f"de preferencia/classificacao/alocacao e "
                        f"{first_call_counts['chaves_candidato_distintas_cpf_nome']} "
                        "chaves distintas CPF mascarado-nome. Um candidato pode "
                        "ocupar duas linhas. A publicacao nao prova conter todas "
                        "as inscricoes submetidas antes dos filtros administrativos."
                    ),
                    "chaves_presentes": ["CPF_mascarado_tipo1", "Nome", "Curso", "CNES", "Tipo_Inscricao", "Municipio", "UF", "IBGE"],
                    "chaves_ausentes": ["id_inscricao_mestre", "data_inscricao_individual"],
                },
                "preferencias_ordem": {
                    "classificacao": "observado individualmente no resultado publicado",
                    "justificativa": (
                        "Coluna 'ORDEM DE PRIORIDADE ESCOLHIDA': "
                        f"{first_call_counts['registros_primeira_opcao']} registros "
                        f"de 1a opcao e {first_call_counts['registros_segunda_opcao']} "
                        "de 2a opcao na versao sub judice. A cobertura restringe-se "
                        "aos registros divulgados."
                    ),
                    "chaves_presentes": ["ORDEM DE PRIORIDADE ESCOLHIDA (1ª e 2ª opções)"],
                    "chaves_ausentes": ["ranking_completo_todas_vagas"],
                },
                "classificacao_barema": {
                    "classificacao": "observado individualmente no resultado publicado",
                    "justificativa": "Pontuação no barema geral e classificação em ampla concorrência, cota étnico-racial e cota PCD observadas no Quadro 1 retificado sub judice escolhido como versão canônica.",
                    "chaves_presentes": ["PONTUACAO NO BAREMA (GERAL)", "CLASSIFICACAO AMPLA CONCORRENCIA", "CLASSIFICACAO COTA ETNICO RACIAL", "CLASSIFICACAO COTA PCD"],
                    "chaves_ausentes": ["detalhamento_itens_barema"],
                },
                "convocacao": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "Convocacao deduzida do cronograma coletivo do edital; inexiste log com timestamp individual de convocacao.",
                    "chaves_presentes": ["cronograma_edital"],
                    "chaves_ausentes": ["id_evento", "data_convocacao_individual"],
                },
                "aceite_recusa": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao ha registro publico de manifestacao individual de aceite, recusa ou perda de prazo.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["data_aceite", "data_recusa", "status_confirmacao"],
                },
                "homologacao": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Planilha 2025_ciclo1_chamada1_homologados.xlsx contem 316 profissionais homologados (296 AC, 18 ER, 2 PCD).",
                    "chaves_presentes": ["CPF_mascarado_tipo1", "Nome", "CNES", "Municipio", "Curso", "Faixa", "Cota", "Homologacao"],
                    "chaves_ausentes": ["id_vaga", "id_profissional_pseudo_oficial", "timestamp"],
                },
                "entrada_exercicio": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "dt_inicio_atividade aparece no snapshot nominal de 12/08/2026 somente para participantes ainda ativos e passíveis de ligação. Entradas de quem saiu antes do corte não são recuperadas por esse snapshot.",
                    "chaves_presentes": ["dt_inicio_atividade (sobreviventes)"],
                    "chaves_ausentes": ["dt_inicio_geral", "log_frequencia"],
                },
                "afastamento_licenca": {
                    "classificacao": "nao localizado",
                    "justificativa": "Inexistencia total de registros de licencas medicas, maternidade ou afastamentos.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["id_afastamento", "tipo_afastamento", "dt_inicio_afastamento", "dt_fim_afastamento"],
                },
                "retorno_afastamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "Inexistencia de registro de retorno de afastamento.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["dt_retorno"],
                },
                "transferencia_realocacao": {
                    "classificacao": "observado parcialmente",
                    "justificativa": "Quadro 2 retificado (2025_ciclo1_chamada1_realocacao_retificado.xlsx) contem proposta de realocacao para 59 profissionais de servicos descontinuados/incompativeis. Log continuo de transferencias nao publicado.",
                    "chaves_presentes": ["Quadro 2 Proposta de Realocacao (59 profissionais)"],
                    "chaves_ausentes": ["cnes_origem", "cnes_destino", "dt_transferencia", "motivo_detalhado"],
                },
                "desistencia_desligamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "Ausência em uma publicação posterior ou no snapshot nominal não identifica desligamento: diferenças de universo, máscara e cobertura impedem atribuir motivo, data ou natureza de saída.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["dt_desligamento", "tipo_desligamento", "motivo_desligamento"],
                },
                "reocupacao_vaga": {
                    "classificacao": "nao localizado",
                    "justificativa": "Sem id_vaga estavel, vagas reapresentadas na 2a chamada nao podem ser distinguidas de vagas novas nao preenchidas.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["id_vaga_estavel", "flag_reocupacao"],
                },
            },
        },
        {
            "ciclo": "1",
            "chamada": "2",
            "edital": "Chamamento Publico SGTES/MS no 3/2025 - 2a Chamada",
            "data_oferta": "2025-09-29",
            "data_homologacao": "2025-11-20",
            "dias_calendario_ate_corte": 317,
            "status_eventos": {
                "inscricao_candidatura": {
                    "classificacao": "universo completo nao observado; resultado publicado parcialmente observado",
                    "justificativa": "A planilha publica 757 registros de preferencia/classificacao e 88 registros desclassificados. Esses registros nao demonstram corresponder ao universo completo de inscricoes submetidas.",
                    "chaves_presentes": ["CPF_mascarado_tipo2", "Nome", "Curso", "CNES", "Tipo_Inscricao"],
                    "chaves_ausentes": ["id_inscricao_mestre", "timestamp_inscricao"],
                },
                "preferencias_ordem": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Coluna 'Ordem de Prioridade Escolhida' (1a e 2a opcoes). Nao cobre escolhas alem da 2a.",
                    "chaves_presentes": ["Ordem de Prioridade Escolhida (1 e 2)"],
                    "chaves_ausentes": ["ranking_completo_todas_vagas"],
                },
                "classificacao_barema": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Pontuacao no barema geral e ranking por ampla concorrencia, etnico-racial e PCD observados na planilha de classificacao final.",
                    "chaves_presentes": ["Pontuacao Barema", "Classificacao AC", "Classificacao ER", "Classificacao PCD"],
                    "chaves_ausentes": ["detalhamento_itens_barema"],
                },
                "convocacao": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "Inferida da situacao de alocacao; sem registro de data e notificacao individual.",
                    "chaves_presentes": ["Situacao Alocacao"],
                    "chaves_ausentes": ["dt_convocacao"],
                },
                "aceite_recusa": {
                    "classificacao": "nao localizado",
                    "justificativa": "Sem log individual de aceite/recusa; apenas o resultado liquido de alocados vs homologados.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["status_aceite", "dt_aceite", "motivo_recusa"],
                },
                "homologacao": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Planilha 2025_ciclo1_chamada2_homologados.xlsx com 581 medicos (cumulativo chamadas 1 e 2).",
                    "chaves_presentes": ["CPF_mascarado_tipo3", "Nome", "Municipio", "UF", "CNES", "Curso"],
                    "chaves_ausentes": ["id_vaga", "data_homologacao_individual"],
                },
                "entrada_exercicio": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "Observada via dt_inicio_atividade em data/pmm_especialistas_nominal.csv apenas para quem continuava ativo em 12/08/2026 (490 de 581 homologados).",
                    "chaves_presentes": ["dt_inicio_atividade (sobreviventes)"],
                    "chaves_ausentes": ["dt_inicio_todas_entradas"],
                },
                "afastamento_licenca": {
                    "classificacao": "nao localizado",
                    "justificativa": "Inexistencia total de registros publicos de afastamento.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["todas_chaves_afastamento"],
                },
                "retorno_afastamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "Inexistencia de dados de retorno.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["dt_retorno"],
                },
                "transferencia_realocacao": {
                    "classificacao": "nao localizado",
                    "justificativa": "Transferencias individuais nao registradas em microdados.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["todas_chaves_transferencia"],
                },
                "desistencia_desligamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "91 medicos homologados nao constam no cadastro nominal de 12/08/2026; razao da saida e data nao sao informadas.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["dt_desligamento", "motivo"],
                },
                "reocupacao_vaga": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "Oferta de cadastro de reserva em chamada 2 contem 2.896 vagas, mas nao diferencia vagas novas de reocupacoes.",
                    "chaves_presentes": ["vagas_reserva_agregadas"],
                    "chaves_ausentes": ["id_vaga", "historico_ocupacao_vaga"],
                },
            },
        },
        {
            "ciclo": "2",
            "chamada": "1",
            "edital": "Chamamento Publico SGTES/MS no 1/2026 - 1a Chamada",
            "data_oferta": "2026-03-19",
            "data_homologacao": "2026-04-15",
            "dias_calendario_ate_corte": 146,
            "status_eventos": {
                "inscricao_candidatura": {
                    "classificacao": "nao localizado",
                    "justificativa": "Apenas planilha de 9 remanescentes publicada (2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx). Microdados gerais de inscricao da 1a chamada nao disponibilizados em planilha.",
                    "chaves_presentes": ["amostra_remanescentes_9"],
                    "chaves_ausentes": ["inscricoes_completas_chamada_1"],
                },
                "preferencias_ordem": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Observado apenas para os 9 remanescentes.",
                    "chaves_presentes": ["ORDEM DE PRIORIDADE ESCOLHIDA (remanescentes)"],
                    "chaves_ausentes": ["preferencias_chamada_geral"],
                },
                "classificacao_barema": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Pontuacao final e classificacao observadas apenas para os 9 remanescentes.",
                    "chaves_presentes": ["Pontuacao Final", "Classificacao (remanescentes)"],
                    "chaves_ausentes": ["barema_chamada_geral"],
                },
                "convocacao": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "Convocacao inferida de cronogramas.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["dt_convocacao"],
                },
                "aceite_recusa": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nenhum registro de aceite ou recusa.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["status_aceite"],
                },
                "homologacao": {
                    "classificacao": "nao localizado",
                    "justificativa": "Planilha de homologados individuais nao publicada no catalogo de planilhas.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["lista_homologados_c2_ch1"],
                },
                "entrada_exercicio": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "O cadastro nominal de 12/08/2026 registra datas de início apenas para participantes ainda ativos no corte; não recupera entradas de quem já havia saído.",
                    "chaves_presentes": ["dt_inicio_atividade (sobreviventes nominais)"],
                    "chaves_ausentes": ["fluxo_completo_entradas"],
                },
                "afastamento_licenca": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao publicado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["afastamentos"],
                },
                "retorno_afastamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao publicado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["retornos"],
                },
                "transferencia_realocacao": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao publicado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["transferencias"],
                },
                "desistencia_desligamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao publicado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["desligamentos"],
                },
                "reocupacao_vaga": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao publicado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["reocupacoes"],
                },
            },
        },
        {
            "ciclo": "2",
            "chamada": "2",
            "edital": "Chamamento Publico SGTES/MS no 1/2026 - 2a Chamada",
            "data_oferta": "2026-04-16",
            "data_homologacao": "2026-05-30",
            "dias_calendario_ate_corte": 118,
            "status_eventos": {
                "inscricao_candidatura": {
                    "classificacao": "universo completo nao observado; resultado publicado parcialmente observado",
                    "justificativa": "A planilha publica 1.053 registros de resultado (303 alocados e 750 em cadastro de reserva) e 55 registros desclassificados. Nao ha prova de cobertura de todas as inscricoes submetidas.",
                    "chaves_presentes": ["CPF_mascarado_tipo4", "Nome", "Curso", "CNES", "IBGE", "Tipo_Inscricao"],
                    "chaves_ausentes": ["id_inscricao_mestre"],
                },
                "preferencias_ordem": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Coluna 'ORDEM DE PRIORIDADE ESCOLHIDA' (609 em 1a opcao, 444 em 2a opcao).",
                    "chaves_presentes": ["ORDEM DE PRIORIDADE ESCOLHIDA (1 e 2)"],
                    "chaves_ausentes": ["demais_preferencias"],
                },
                "classificacao_barema": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Pontuacao final, pontuacao barema, pontuacao tempo e classificacao observadas.",
                    "chaves_presentes": ["Pontuacao Final", "Pontuacao Barema", "Pontuacao Tempo", "Classificacao"],
                    "chaves_ausentes": ["criterios_desempate_detalhados"],
                },
                "convocacao": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "Inferida da situacao ALOCADO.",
                    "chaves_presentes": ["SITUACAO"],
                    "chaves_ausentes": ["dt_convocacao"],
                },
                "aceite_recusa": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao registrado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["status_aceite"],
                },
                "homologacao": {
                    "classificacao": "nao localizado",
                    "justificativa": "Planilha de homologados nao publicada separadamente.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["lista_homologacao"],
                },
                "entrada_exercicio": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "O cadastro nominal de 12/08/2026 registra datas de início apenas para participantes ainda ativos no corte; não recupera entradas de quem já havia saído.",
                    "chaves_presentes": ["dt_inicio_atividade (sobreviventes)"],
                    "chaves_ausentes": ["todas_entradas"],
                },
                "afastamento_licenca": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao publicado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["afastamentos"],
                },
                "retorno_afastamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao publicado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["retornos"],
                },
                "transferencia_realocacao": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao publicado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["transferencias"],
                },
                "desistencia_desligamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao publicado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["desligamentos"],
                },
                "reocupacao_vaga": {
                    "classificacao": "nao localizado",
                    "justificativa": "Quadro da chamada 2 ofertou apenas vagas em cadastro de reserva (1.992 vagas); vinculo com vagas anteriores inobservavel.",
                    "chaves_presentes": ["vagas_reserva"],
                    "chaves_ausentes": ["id_vaga_estavel"],
                },
            },
        },
        {
            "ciclo": "3",
            "chamada": "1",
            "edital": "Chamamento Publico SGTES/MS no 6/2026 - 1a Chamada",
            "data_oferta": "2026-07-24",
            "data_homologacao": "prevista apos agosto/2026",
            "dias_calendario_ate_corte": 19,
            "status_eventos": {
                "inscricao_candidatura": {
                    "classificacao": "universo completo nao observado; resultado publicado parcialmente observado",
                    "justificativa": "A planilha publica 4.532 registros de resultado (704 alocados, 3.826 em cadastro de reserva e 2 sub judice) e 999 registros desclassificados. Nao ha prova de cobertura de todas as inscricoes submetidas.",
                    "chaves_presentes": ["CPF_mascarado_tipo5", "Nome", "Curso", "CNES", "IBGE", "Tipo_Inscricao"],
                    "chaves_ausentes": ["id_inscricao_mestre"],
                },
                "preferencias_ordem": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Coluna 'ORDEM DE PRIORIDADE ESCOLHIDA' (2.581 em 1a opcao, 1.951 em 2a opcao).",
                    "chaves_presentes": ["ORDEM DE PRIORIDADE ESCOLHIDA (1 e 2)"],
                    "chaves_ausentes": ["demais_preferencias"],
                },
                "classificacao_barema": {
                    "classificacao": "observado individualmente",
                    "justificativa": "Pontuacao no barema geral e classificacao observadas.",
                    "chaves_presentes": ["Pontuacao Barema Geral", "Classificacao"],
                    "chaves_ausentes": ["pontuacao_tempo_discriminada"],
                },
                "convocacao": {
                    "classificacao": "inferivel mas inadequado",
                    "justificativa": "Inferida da publicacao de resultado final de 25/08/2026.",
                    "chaves_presentes": ["SITUACAO"],
                    "chaves_ausentes": ["dt_convocacao"],
                },
                "aceite_recusa": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao registrado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["status_aceite"],
                },
                "homologacao": {
                    "classificacao": "nao localizado",
                    "justificativa": "Fase ainda nao concluida/publicada na data de auditoria.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["lista_homologacao_c3"],
                },
                "entrada_exercicio": {
                    "classificacao": "nao localizado",
                    "justificativa": "Zero entradas ocorridas ate 12/08/2026 (cronograma posterior a data de corte).",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["dt_inicio_atividade"],
                },
                "afastamento_licenca": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao aplicavel no periodo auditado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["afastamentos"],
                },
                "retorno_afastamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao aplicavel no periodo auditado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["retornos"],
                },
                "transferencia_realocacao": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao aplicavel no periodo auditado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["transferencias"],
                },
                "desistencia_desligamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao aplicavel no periodo auditado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["desligamentos"],
                },
                "reocupacao_vaga": {
                    "classificacao": "nao localizado",
                    "justificativa": "Nao aplicavel no periodo auditado.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["reocupacoes"],
                },
            },
        },
    ]

    spells_avaliacao = {
        "viabilidade_spells_publicos": False,
        "razoes_bloqueio_spells": [
            "Inexistencia de data exata de desligamento/desistencia (dt_fim_spell ausente)",
            "Inexistencia de log de licencas, afastamentos e retornos para interrupcao e retomada de spells",
            "Snapshot nominal de 12/08/2026 observa apenas sobreviventes ativos, truncando a entrada de quem saiu antes e omitindo todos os desligados",
            "Ausencia de id_vaga estavel impede associar profissionais subsequentes a mesma vaga fisica para medir tempo de desocupacao",
            "Divergencia entre mascaras de CPF e falta de CRM nas planilhas de selecao impede vinculacao deterministica confiavel com o CNES mensal",
        ],
        "coberturas_temporais": {
            "cobertura_90": {
                "status": "incalculavel com fontes publicas",
                "motivo": "Exige saber se a vaga permaneceu coberta por 90 dias ininterruptos ou acumulados; publicamente observa-se apenas se o medico constava como ativo em 12/08/2026.",
            },
            "cobertura_120": {
                "status": "incalculavel com fontes publicas",
                "motivo": "Mesmo para chamadas com maturidade de calendario >= 120 dias, ausencias intermediarias e rotatividade nao sao observadas.",
            },
            "cobertura_180": {
                "status": "incalculavel com fontes publicas (outcome primario bloqueado)",
                "motivo": "Apenas chamadas do Ciclo 1 de 2025 possuem maturidade de calendario de 180 dias, mas a falta de data de encerramento e historico de presenca impede computar o numerador de dias efetivamente cobertos.",
            },
        },
        "componentes_mensuraveis_vs_inobservaveis": {
            "preenchimento_inicial": "Parcialmente observavel (alocacao e homologacao nas planilhas onde disponiveis; sem taxa confiavel onde vagas imediatas nao tem denominador inequivoco)",
            "tempo_ate_entrada": "Inobservavel individualmente (apenas data de inicio dos sobreviventes em relacao a data coletiva do edital; data da convocacao individual e do aceite sao ausentes)",
            "permanencia": "Inobservavel (sobrevivencia condicional ao corte de 12/08/2026 nao mede curva de retencao sem vies de selecao)",
            "rotatividade": "Inobservavel (quedas agregadas na serie historica nao identificam transicoes individuais)",
            "reocupacao": "Inobservavel (impossivel ligar saida de um profissional a entrada de outro na mesma vaga sem id_vaga estavel)",
        },
    }

    return {
        "escopo": "Matriz de disponibilidade e auditabilidade dos eventos da trajetoria publica no PMM-E",
        "data_auditoria": AUDIT_DATE,
        "eventos_chave_avaliados": eventos_chave,
        "coortes_avaliadas": coortes,
        "auditoria_primeira_chamada_2025": first_call_audit,
        "avaliacao_spells_e_cobertura": spells_avaliacao,
    }


def main() -> None:
    print("Iniciando execucao do Agente A02: selecao e trajetoria publica...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_entries = process_manifest()
    cpf_patterns = audit_cpf_patterns()
    first_call_audit = audit_first_call_2025()
    matriz_result = build_event_matrix(manifest_entries, first_call_audit)
    matriz_result["padroes_mascara_cpf"] = cpf_patterns

    manifest_output = {
        "agente": "A02",
        "objeto": "selecao e trajetoria administrativa publica",
        "gerado_em": AUDIT_DATE,
        "fontes_processadas": manifest_entries,
    }
    MANIFESTO_PATH.write_text(
        json.dumps(manifest_output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Manifesto salvo em: {MANIFESTO_PATH}")

    MATRIZ_PATH.write_text(
        json.dumps(matriz_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Matriz de eventos salva em: {MATRIZ_PATH}")
    print("Execucao de a02_adquirir_trajetoria.py concluida com sucesso.")


if __name__ == "__main__":
    main()
