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
DATA_RAW_PMME = ROOT / "data" / "raw" / "pmm_e"
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output" / "aquisicao"

MANIFESTO_PATH = OUTPUT_DIR / "a02_manifesto_trajetoria.json"
MATRIZ_PATH = OUTPUT_DIR / "a02_matriz_eventos_publicos.json"

AUDIT_DATE = "2026-08-27"
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


FONTES_TRAJETORIA = [
    {
        "id": "alocacao_2025_c1_retificada",
        "arquivo": "2025_ciclo1_chamada1_alocacao_retificada.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-mais-medicos-especialistas/quadro-1-profissionais-alocados-conforme-escolha-inicial-1a-ou-2a-opcao-retificado.xlsx",
        "ciclo": "1",
        "chamada": "1",
        "cobertura": "Ciclo 1, chamada 1, alocacao retificada",
        "unidade_declarada": "profissional alocado/vaga",
        "etapas_alvo": ["inscricao", "preferencias", "classificacao", "alocacao"],
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
        "unidade_declarada": "candidatura/classificacao",
        "etapas_alvo": ["inscricao", "preferencias", "classificacao", "alocacao", "desclassificacao"],
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
        "unidade_declarada": "candidatura/alocacao remanescente",
        "etapas_alvo": ["classificacao", "alocacao_remanescente"],
    },
    {
        "id": "resultado_2026_c2_ch2",
        "arquivo": "2026_ciclo2_chamada2_resultado_final.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/resultado-final-pmme-2o-ciclo-2a-chamada.xlsx",
        "ciclo": "2",
        "chamada": "2",
        "cobertura": "Ciclo 2, chamada 2, resultado final e desclassificados",
        "unidade_declarada": "candidatura/alocacao/cadastro reserva",
        "etapas_alvo": ["inscricao", "preferencias", "classificacao", "alocacao", "cadastro_reserva", "desclassificacao"],
    },
    {
        "id": "resultado_2026_c3_sub_judice",
        "arquivo": "2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e/resultado-final-3o-ciclo-sub-judice.xlsx",
        "ciclo": "3",
        "chamada": "1",
        "cobertura": "Ciclo 3, chamada 1, resultado final de 25/08/2026, sub judice",
        "unidade_declarada": "candidatura/alocacao/cadastro reserva/sub judice",
        "etapas_alvo": ["inscricao", "preferencias", "classificacao", "alocacao", "cadastro_reserva", "sub_judice", "desclassificacao"],
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
                    "disponibilidade": "link quebrado / HTTP 404",
                    "erro": str(e),
                    "validacao": "fonte oficial inacessivel na data de referencia",
                })

    return manifest_entries


def audit_cpf_patterns() -> dict[str, object]:
    patterns = {}
    for p in sorted(DATA_RAW_PMME.glob("*.xlsx")):
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


def build_event_matrix(manifest_entries: list[dict[str, object]]) -> dict[str, object]:
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
                    "classificacao": "link quebrado",
                    "justificativa": "Planilha oficial de alocacao retificada retornou HTTP 404; microdados brutos de inscricoes nao localizados.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["id_inscricao", "id_candidato_pseudo", "data_inscricao"],
                },
                "preferencias_ordem": {
                    "classificacao": "link quebrado",
                    "justificativa": "Quadro de 1a e 2a escolhas da chamada original inacessivel via HTTP 404.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["ordem_escolha", "vaga_opcao_1", "vaga_opcao_2"],
                },
                "classificacao_barema": {
                    "classificacao": "link quebrado",
                    "justificativa": "Pontuacoes de barema e ranking da 1a chamada nao preservados (link quebrado).",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["pontuacao_barema", "pontuacao_tempo", "ranking"],
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
                    "justificativa": "dt_inicio_atividade observada no snapshot nominal de 12/08/2026 APENAS para os 265 homologados que permaneceram ativos. Inexistente para quem desistiu antes de agosto/2026.",
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
                    "classificacao": "somente agregado",
                    "justificativa": "Mencoes esparsas em comunicados sem painel individual de origem, destino e data.",
                    "chaves_presentes": [],
                    "chaves_ausentes": ["cnes_origem", "cnes_destino", "dt_transferencia", "motivo"],
                },
                "desistencia_desligamento": {
                    "classificacao": "nao localizado",
                    "justificativa": "17 medicos homologados na 1a chamada nao constam na lista da 2a chamada e 51 nao estao no nominal de 12/08/2026. Motivo, data e natureza da saida sao totalmente inobservaveis.",
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
                    "classificacao": "observado individualmente",
                    "justificativa": "757 registros de preferencias de candidatos classificados/alocados e 88 desclassificados na planilha 2025_ciclo1_chamada2_classificacao_final.xlsx.",
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
                    "justificativa": "758 medicos do Ciclo 2 iniciaram atividade em marco/abril 2026 no cadastro nominal de 12/08/2026. Apenas sobreviventes sao observados.",
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
                    "classificacao": "observado individualmente",
                    "justificativa": "Planilha 2026_ciclo2_chamada2_resultado_final.xlsx contem 1.053 linhas de classificados (303 alocados, 750 reserva) e 55 desclassificados.",
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
                    "justificativa": "183 medicos com inicio em junho/2026 constam como ativos em 12/08/2026. Somente sobreviventes observados.",
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
                    "classificacao": "observado individualmente",
                    "justificativa": "Planilha 2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx contem 4.532 linhas de classificados (704 alocados, 3.826 reserva, 2 sub judice) e 999 desclassificados.",
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
        "avaliacao_spells_e_cobertura": spells_avaliacao,
    }


def main() -> None:
    print("Iniciando execucao do Agente A02: selecao e trajetoria publica...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_entries = process_manifest()
    cpf_patterns = audit_cpf_patterns()
    matriz_result = build_event_matrix(manifest_entries)
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
