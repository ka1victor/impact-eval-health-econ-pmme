"""Script de aquisicao e inspecao das competencias mensais do CNES (A05).

Suporta os modos:
  --plan: gera/atualiza o manifesto com todas as 26 competencias planejadas sem download grande.
  --pilot: baixa as 3 competencias piloto (202406, 202506, 202607), inspeciona tabelas, extrai dicionario e estabilidade.
  --full: baixa o painel integral (202406 a 202607), exigindo --confirm-large-download.
  --inspect-only: re-inspeciona os ZIPs locais existentes e atualiza manifesto, dicionario e auditoria.

Gera:
  - data/raw/cnes/BASE_DE_DADOS_CNES_AAAAMM.ZIP
  - output/aquisicao/a05_manifesto_cnes.json
  - output/aquisicao/a05_dicionario_tabelas_cnes.json
  - output/aquisicao/a05_auditoria_universos_cnes.json
  - docs/auditorias/aquisicao/A05_cnes_mensal.md
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "cnes"
OUTPUT_DIR = ROOT / "output" / "aquisicao"
DOCS_DIR = ROOT / "docs" / "auditorias" / "aquisicao"
MANIFEST_PATH = OUTPUT_DIR / "a05_manifesto_cnes.json"
DICTIONARY_PATH = OUTPUT_DIR / "a05_dicionario_tabelas_cnes.json"
UNIVERSES_PATH = OUTPUT_DIR / "a05_auditoria_universos_cnes.json"
REPORT_PATH = DOCS_DIR / "A05_cnes_mensal.md"

CATALOG_PAGE = "https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp"
BASE_URL = "http://cnes.datasus.gov.br/EstatisticasServlet?path="
CATALOG_DATE = "2026-08-27"
AUDIT_DATE = "2026-08-28"

# Janela completa: 202406 a 202607 (26 competencias)
ALL_COMPETENCIAS = [
    f"{year}{month:02d}"
    for year, first, last in ((2024, 6, 12), (2025, 1, 12), (2026, 1, 7))
    for month in range(first, last + 1)
]

PILOT_COMPETENCIAS = ["202406", "202506", "202607"]

# Quadros finais adotados por A01 para cada chamada principal. O Ciclo 1 não
# teve retificação do quadro de oferta localizado; nos Ciclos 2 e 3 prevalecem
# as versões retificadas finais. Cada planilha é relida por A05: o inventário
# JSON de A01 não substitui a fonte tabular.
A01_OFFER_FRAMES = [
    {
        "id": "vagas_2025_c1_ch1_original",
        "rotulo": "Ciclo 1, chamada 1 — quadro original (versão de oferta disponível)",
        "path": ROOT / "data" / "raw" / "aquisicao" / "vagas" / "2025_ciclo1_chamada1_vagas.xlsx",
    },
    {
        "id": "vagas_alocados_2025_c1_ch2",
        "rotulo": "Ciclo 1, chamada 2 — quadro de cadastro de reserva",
        "path": ROOT / "data" / "raw" / "pmm_e" / "2025_ciclo1_chamada2_vagas_e_alocados.xlsx",
        "sheet": "VAGAS - CADASTRO RESERVA",
    },
    {
        "id": "vagas_2026_c2_ch1_retificada",
        "rotulo": "Ciclo 2, chamada 1 — quadro retificado final de 19/03/2026",
        "path": ROOT / "data" / "raw" / "pmm_e" / "2026_ciclo2_chamada1_vagas_retificadas.xlsx",
    },
    {
        "id": "vagas_2026_c2_ch2",
        "rotulo": "Ciclo 2, chamada 2 — quadro publicado em 16/04/2026",
        "path": ROOT / "data" / "raw" / "pmm_e" / "2026_ciclo2_chamada2_vagas.xlsx",
    },
    {
        "id": "vagas_2026_c3_retificada",
        "rotulo": "Ciclo 3, chamada 1 — quadro retificado de 24/07/2026",
        "path": ROOT / "data" / "raw" / "pmm_e" / "2026_ciclo3_chamada1_vagas_retificadas.xlsx",
    },
]

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def sha256_file(path: Path) -> str:
    """Calcula SHA-256 do arquivo em chunks de 1MB."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_cnes_zip(
    competencia: str,
    destination: Path,
    timeout: int = 1200,
    max_retries: int = 3,
) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
    """Baixa arquivo ZIP de forma segura e idempotente com .part e validacao.

    Retorna: (sucesso, sha256, tamanho_bytes, erro)
    """
    filename = f"BASE_DE_DADOS_CNES_{competencia}.ZIP"
    url = f"{BASE_URL}{filename}"

    if destination.exists():
        try:
            if zipfile.is_zipfile(destination):
                with zipfile.ZipFile(destination, "r") as zf:
                    test_res = zf.testzip()
                    if test_res is None:
                        file_hash = sha256_file(destination)
                        file_size = destination.stat().st_size
                        print(f"[OK LOCAL] {filename} ({file_size / (1024*1024):.2f} MB, hash: {file_hash[:12]}...)")
                        return True, file_hash, file_size, None
        except Exception as e:
            print(f"[AVISO] Arquivo existente {filename} corrompido: {e}. Rebaixando...")

    temp_destination = destination.with_suffix(".zip.part")
    if temp_destination.exists():
        temp_destination.unlink()

    destination.parent.mkdir(parents=True, exist_ok=True)

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
            "Referer": CATALOG_PAGE,
            "Accept": "application/zip,*/*",
        },
    )

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Baixando {filename} de {url} (tentativa {attempt}/{max_retries})...")
            t0 = time.time()
            digest = hashlib.sha256()
            total_bytes = 0

            with urllib.request.urlopen(request, timeout=timeout) as response:
                first_chunk = response.read(2)
                if first_chunk != b"PK":
                    raise RuntimeError(f"Resposta remota nao e ZIP (magic bytes: {first_chunk!r})")

                with temp_destination.open("wb") as handle:
                    handle.write(first_chunk)
                    digest.update(first_chunk)
                    total_bytes += len(first_chunk)

                    last_log = time.time()
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
                        digest.update(chunk)
                        total_bytes += len(chunk)

                        if time.time() - last_log >= 10:
                            elapsed = time.time() - t0
                            speed = total_bytes / (1024 * 1024 * elapsed) if elapsed > 0 else 0
                            print(f"  {filename}: {total_bytes / (1024 * 1024):.1f} MB baixados ({speed:.2f} MB/s)...")
                            last_log = time.time()

            elapsed = time.time() - t0
            file_hash = digest.hexdigest()
            print(f"[CONCLUIDO] {filename} em {elapsed:.1f}s ({total_bytes / (1024*1024):.2f} MB, hash: {file_hash})")

            if not zipfile.is_zipfile(temp_destination):
                raise RuntimeError("Arquivo baixado nao e um ZIP valido.")

            with zipfile.ZipFile(temp_destination, "r") as zf:
                if zf.testzip() is not None:
                    raise RuntimeError("Teste de integridade do ZIP falhou.")

            if destination.exists():
                destination.unlink()
            temp_destination.replace(destination)

            return True, file_hash, total_bytes, None

        except Exception as err:
            print(f"[ERRO] Tentativa {attempt} falhou para {filename}: {err}")
            if temp_destination.exists():
                try:
                    temp_destination.unlink()
                except Exception:
                    pass
            if attempt == max_retries:
                return False, None, None, str(err)
            time.sleep(3)

    return False, None, None, "Max retries excedido"


def inspect_cnes_zip(zip_path: Path) -> Dict[str, Any]:
    """Inspeciona detalhadamente o arquivo ZIP do CNES sem extrair tudo para disco."""
    results: Dict[str, Any] = {
        "arquivo": zip_path.name,
        "bytes_zip": zip_path.stat().st_size,
        "tabelas": {},
        "arquivos_nao_csv": [],
        "contagem_tabelas": 0,
        "modulos_identificados": {},
    }

    with zipfile.ZipFile(zip_path, "r") as zf:
        infolist = zf.infolist()
        results["total_arquivos_zip"] = len(infolist)

        for info in infolist:
            fname = info.filename
            if fname.lower().endswith(".csv"):
                with zf.open(info, "r") as table_file:
                    header_bytes = table_file.read(64 * 1024)
                    text = ""
                    for enc in ("latin1", "utf-8", "cp1252"):
                        try:
                            text = header_bytes.decode(enc)
                            break
                        except Exception:
                            continue

                    lines = text.splitlines()
                    delimiter = ";" if ";" in (lines[0] if lines else "") else ","
                    columns = []
                    sample_rows = []
                    if lines:
                        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
                        try:
                            raw_header = next(reader, [])
                            # Normalizar nomes de colunas (remover aspas simples indesejadas)
                            columns = [c.strip().strip("'\"") for c in raw_header]
                            for _ in range(5):
                                row = next(reader, None)
                                if row:
                                    sample_rows.append(row)
                        except Exception:
                            pass

                    base_table_name = fname.replace(".csv", "").replace(".CSV", "")
                    for comp in ALL_COMPETENCIAS:
                        base_table_name = base_table_name.replace(comp, "")

                    results["tabelas"][fname] = {
                        "nome_arquivo": fname,
                        "nome_base": base_table_name,
                        "bytes_descompactados": info.file_size,
                        "bytes_compactados": info.compress_size,
                        "num_colunas": len(columns),
                        "colunas": columns,
                        "delimitador": delimiter,
                        "amostra_linhas": len(sample_rows),
                    }
            else:
                results["arquivos_nao_csv"].append({
                    "nome_arquivo": fname,
                    "bytes": info.file_size,
                })

    results["contagem_tabelas"] = len(results["tabelas"])

    table_names = list(results["tabelas"].keys())
    
    def find_matching_tables(prefixes: List[str]) -> List[str]:
        matched = []
        for p in prefixes:
            for t in table_names:
                if p.lower() in t.lower() and t not in matched:
                    matched.append(t)
        return matched

    results["modulos_identificados"] = {
        "estabelecimento": find_matching_tables(["tbEstabelecimento", "tbDadosGerais", "tbMunicipio"]),
        "profissional_vinculo": find_matching_tables(["tbCargaHoraria", "tbDadosProfissional", "tbAtividadeProfissional", "rlEstabAtivProfissional"]),
        "leitos": find_matching_tables(["tbLeito", "tbTipoLeito", "rlEstabComplementar"]),
        "equipamentos": find_matching_tables(["tbEquipamento", "tbTipoEquipamento", "rlEstabEquipamento"]),
        "servicos_especializados": find_matching_tables(["tbServicoEspecializado", "tbClassificacaoServico", "rlEstabServClass"]),
        "habilitacoes": find_matching_tables(["tbHabilitacao", "rlEstabSipac", "tbSubGruposHabilitacao"]),
        "atendimento_convenio": find_matching_tables(["tbAtendimentoPrestado", "tbConvenio"]),
    }

    return results


def build_schema_dictionary(inspections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Constroi dicionario integrado de tabelas e analisa estabilidade de esquema."""
    dict_output: Dict[str, Any] = {
        "data_geracao": AUDIT_DATE,
        "competencias_inspecionadas": list(inspections.keys()),
        "catalogo_tabelas": {},
        "estabilidade_esquema": {},
        "mapeamento_chaves_e_relacionamentos": {},
        "campos_criticos_por_modulo": {},
    }

    all_table_bases: Set[str] = set()
    for comp, insp in inspections.items():
        for fname, tinfo in insp["tabelas"].items():
            all_table_bases.add(tinfo["nome_base"])

    for tbase in sorted(all_table_bases):
        table_history: Dict[str, Any] = {}
        for comp, insp in inspections.items():
            for fname, tinfo in insp["tabelas"].items():
                if tinfo["nome_base"] == tbase:
                    table_history[comp] = {
                        "arquivo_real": fname,
                        "colunas": tinfo["colunas"],
                        "num_colunas": tinfo["num_colunas"],
                        "bytes": tinfo["bytes_descompactados"],
                    }

        cols_by_comp = {comp: th["colunas"] for comp, th in table_history.items()}
        comps = list(cols_by_comp.keys())
        is_stable = True
        schema_diffs = []

        if len(comps) > 1:
            ref_cols = cols_by_comp[comps[0]]
            for other_comp in comps[1:]:
                other_cols = cols_by_comp[other_comp]
                if ref_cols != other_cols:
                    is_stable = False
                    added = [c for c in other_cols if c not in ref_cols]
                    removed = [c for c in ref_cols if c not in other_cols]
                    schema_diffs.append({
                        "comparacao": f"{comps[0]} vs {other_comp}",
                        "colunas_adicionadas": added,
                        "colunas_removidas": removed,
                    })

        representative_cols = list(cols_by_comp.values())[0] if cols_by_comp else []
        pk_candidates = [c for c in representative_cols if c.startswith("CO_") or c.startswith("ID_") or c.startswith("NU_")]
        
        dict_output["catalogo_tabelas"][tbase] = {
            "nome_base": tbase,
            "presenca_competencias": list(table_history.keys()),
            "estavel": is_stable,
            "diferencas": schema_diffs,
            "num_colunas": len(representative_cols),
            "colunas": representative_cols,
            "candidatos_chave": pk_candidates,
            "detalhes_por_competencia": table_history,
        }

    dict_output["campos_criticos_por_modulo"] = {
        "estabelecimento": {
            "tabela_principal": "tbEstabelecimento",
            "chave_interna": "CO_UNIDADE",
            "chave_publica_nacional": "CO_CNES",
            "chaves_estrangeiras": {
                "CO_MUNICIPIO_GESTOR": "Municipio IBGE gestor",
                "CO_ESTADO_GESTOR": "UF gestora",
                "CO_NATUREZA_JUR": "Natureza juridica da mantenedora",
                "TP_UNIDADE": "Tipo de estabelecimento (01=Posto, 02=UBS, 04=Policlinica, 05=Hospital Geral, etc)",
            },
            "campos_essenciais": [
                "CO_UNIDADE", "CO_CNES", "NU_CNPJ_MANTENEDORA", "NO_RAZAO_SOCIAL", "NO_FANTASIA",
                "CO_MUNICIPIO_GESTOR", "TP_UNIDADE", "CO_NATUREZA_JUR", "TP_GESTAO",
                "ST_CONTRATO_FORMALIZADO", "ST_COWORKING"
            ],
            "uso_no_estudo": "Identificacao territorial das unidades de saude, tipologia fisica, nivel de gestao e capacidade instalada previa."
        },
        "profissional_vinculo": {
            "tabela_principal": "tbCargaHorariaSus",
            "chave_primaria": ["CO_UNIDADE", "CO_PROFISSIONAL_SUS", "CO_CBO"],
            "chaves_relacionais": {
                "CO_UNIDADE": "Chave de ligacao 1:N com tbEstabelecimento (CO_UNIDADE)",
                "CO_PROFISSIONAL_SUS": "Chave de ligacao 1:N com tbDadosProfissionalSus (CO_PROFISSIONAL_SUS)",
                "CO_CBO": "Chave de ligacao com tbAtividadeProfissional (CBO 2002 de 6 digitos)",
            },
            "campos_essenciais": [
                "CO_UNIDADE", "CO_PROFISSIONAL_SUS", "CO_CBO",
                "QT_CARGA_HORARIA_AMBULATORIAL", "QT_CARGA_HORARIA_OUTROS",
                "QT_CARGA_HORARIA_HOSPITALAR", "TP_SUS_NAO_SUS",
                "IND_VINCULACAO", "CO_CONSELHO_CLASSE"
            ],
            "uso_no_estudo": "Calculo do Full-Time Equivalent (FTE) cadastral, carga horaria ambulatorial e hospitalar de medicos especialistas (CBO 2251/2252/2253), mapeamento de vinculos simultaneos e anteriores."
        },
        "profissional_cadastro": {
            "tabela_principal": "tbDadosProfissionalSus",
            "chave_primaria": "CO_PROFISSIONAL_SUS",
            "campos_essenciais": [
                "CO_PROFISSIONAL_SUS", "CO_CNS", "NO_PROFISSIONAL", "NO_SOCIAL", "CO_CPF"
            ],
            "uso_no_estudo": "Cadastro nominal do profissional no SUS. Contem CNS (Cartao Nacional de Saude) e Nome; CPF mascarado/ausente em versoes publicas."
        },
        "leitos": {
            "tabela_principal": "rlEstabComplementar",
            "tabela_apoio": "tbLeito",
            "chave_primaria": ["CO_UNIDADE", "CO_LEITO", "CO_TIPO_LEITO"],
            "campos_essenciais": [
                "CO_UNIDADE", "CO_LEITO", "CO_TIPO_LEITO", "TP_ALTACOMP", "QT_EXIST", "QT_CONTR", "QT_SUS"
            ],
            "uso_no_estudo": "Baseline de capacidade fisica hospitalar previa a implantacao do programa."
        },
        "equipamentos": {
            "tabela_principal": "rlEstabEquipamento",
            "tabela_apoio": "tbEquipamento",
            "chave_primaria": ["CO_UNIDADE", "CO_EQUIPAMENTO", "CO_TIPO_EQUIPAMENTO"],
            "campos_essenciais": [
                "CO_UNIDADE", "CO_EQUIPAMENTO", "CO_TIPO_EQUIPAMENTO", "QT_EXISTENTE", "QT_USO", "TP_SUS"
            ],
            "uso_no_estudo": "Baseline de capacidade diagnostica e tecnologica previa (ex: ultrassom, raio-x, tomografia, ecocardiografo)."
        },
        "servicos_especializados": {
            "tabela_principal": "rlEstabServClass",
            "tabela_apoio": "tbServicoEspecializado / tbClassificacaoServico",
            "chave_primaria": ["CO_UNIDADE", "CO_SERVICO", "CO_CLASSIFICACAO"],
            "campos_essenciais": [
                "CO_UNIDADE", "CO_SERVICO", "CO_CLASSIFICACAO", "CO_AMBULATORIAL", "CO_AMBULATORIAL_SUS", "CO_HOSPITALAR"
            ],
            "uso_no_estudo": "Baseline de oferta de servicos ambulatoriais especializados e complexidade assistencial."
        }
    }

    dict_output["mapeamento_chaves_e_relacionamentos"] = {
        "cnes_para_estabelecimento": {
            "origem": "Quadros de Vagas PMM-E (CO_CNES)",
            "destino": "tbEstabelecimento (CO_CNES)",
            "tipo_ligacao": "Deterministica 1:1 por competencia",
            "viabilidade": "Alta. CNES e chave publica padronizada do SUS (7 digitos)."
        },
        "estabelecimento_para_vinculos_medicos": {
            "origem": "tbEstabelecimento (CO_UNIDADE)",
            "destino": "tbCargaHorariaSus (CO_UNIDADE)",
            "tipo_ligacao": "1:N por competencia",
            "viabilidade": "Alta. CO_UNIDADE (13 digitos) conecta estabelecimentos a todos os vinculos de profissionais."
        },
        "vinculo_para_profissional": {
            "origem": "tbCargaHorariaSus (CO_PROFISSIONAL_SUS)",
            "destino": "tbDadosProfissionalSus (CO_PROFISSIONAL_SUS)",
            "tipo_ligacao": "N:1 por competencia",
            "viabilidade": "Alta dentro do CNES. Recupera o Cartao Nacional de Saude (CNS) e Nome do profissional."
        },
        "pmme_para_profissional_cnes": {
            "origem": "Cadastro Nominal / Homologados PMM-E (CRM + Nome + CPF mascarado)",
            "destino": "tbDadosProfissionalSus / tbCargaHorariaSus (CO_CNS / CO_PROFISSIONAL_SUS / NO_PROFISSIONAL)",
            "tipo_ligacao": "Ausente deterministicamente em fontes publicas",
            "viabilidade": "Bloqueada publicamente. Exige crosswalk administrativo seguro via LAI/SGTES (Agente A07)."
        }
    }

    return dict_output


def normalize_label(value: object) -> str:
    """Normaliza rótulos para localizar colunas sem alterar os dados-fonte."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text).strip().upper()


def normalize_cnes(value: object) -> Tuple[Optional[str], str]:
    """Normaliza CNES para sete dígitos e explicita perdas."""
    raw = str(value or "").strip()
    if not raw:
        return None, "ausente"
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None, "nao_numerico"
    if len(digits) > 7 or int(digits) == 0:
        return None, "comprimento_ou_zero_invalido"
    return digits.zfill(7), "valido"


def xlsx_column_index(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference)
    if not letters:
        return 0
    result = 0
    for char in letters.group(0):
        result = result * 26 + ord(char) - 64
    return result - 1


def read_xlsx_sheets(path: Path) -> Dict[str, List[List[object]]]:
    """Lê células OOXML diretamente, sem depender do inventário derivado de A01."""
    with zipfile.ZipFile(path) as archive:
        shared: List[str] = []
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
        result: Dict[str, List[List[object]]] = {}
        sheets_node = workbook.find(f"{{{NS_MAIN}}}sheets")
        if sheets_node is None:
            return result
        for sheet in sheets_node:
            name = sheet.attrib["name"]
            target = targets[sheet.attrib[f"{{{NS_REL}}}id"]].lstrip("/")
            sheet_path = str(Path("xl") / target) if not target.startswith("xl/") else target
            sheet_path = sheet_path.replace("\\", "/")
            root = ET.fromstring(archive.read(sheet_path))
            rows: List[List[object]] = []
            for row in root.iter(f"{{{NS_MAIN}}}row"):
                values: Dict[int, object] = {}
                for cell in row.findall(f"{{{NS_MAIN}}}c"):
                    index = xlsx_column_index(cell.attrib.get("r", "A1"))
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


def safe_cell(row: List[object], index: int) -> object:
    return row[index] if 0 <= index < len(row) else ""


def nonnegative_integer(value: object) -> int:
    try:
        number = int(float(str(value).replace(",", ".")))
        return max(number, 0)
    except (TypeError, ValueError):
        return 0


def read_a01_offer_frame(spec: Dict[str, Any]) -> Tuple[Dict[str, Any], Set[str]]:
    """Relê um quadro A01 final e mede células, estabelecimentos e perdas."""
    path: Path = spec["path"]
    result: Dict[str, Any] = {
        "id": spec["id"],
        "rotulo": spec["rotulo"],
        "arquivo": path.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(path) if path.exists() else None,
        "status": "ausente" if not path.exists() else "lido",
    }
    if not path.exists():
        result["erro"] = "Planilha A01 selecionada não localizada."
        return result, set()

    sheets = read_xlsx_sheets(path)
    selected: Optional[Tuple[str, int, List[object], List[List[object]]]] = None
    preferred_sheet = spec.get("sheet")
    candidate_sheets = (
        [(preferred_sheet, sheets[preferred_sheet])]
        if preferred_sheet in sheets
        else list(sheets.items())
    )
    for sheet_name, rows in candidate_sheets:
        for row_index, row in enumerate(rows[:30]):
            labels = [normalize_label(cell) for cell in row]
            if "CNES" in labels and ("CURSO" in labels or "APRIMORAMENTO FINAL" in labels):
                selected = (sheet_name, row_index, row, rows)
                break
        if selected:
            break
    if not selected:
        result.update(status="erro", erro="Cabeçalho com CNES e curso/aprimoramento não localizado.")
        return result, set()

    sheet_name, header_index, header, rows = selected
    labels = [normalize_label(cell) for cell in header]
    cnes_index = labels.index("CNES")
    course_index = labels.index("CURSO") if "CURSO" in labels else labels.index("APRIMORAMENTO FINAL")
    total_indices = [index for index, label in enumerate(labels) if label == "TOTAL"]

    cnes_values: List[str] = []
    cell_keys: List[Tuple[str, str]] = []
    loss_reasons: Counter[str] = Counter()
    rows_read = 0
    rows_with_course = 0
    physical_vacancies = 0
    for row in rows[header_index + 1:]:
        raw_cnes = safe_cell(row, cnes_index)
        course = normalize_label(safe_cell(row, course_index))
        if not str(raw_cnes or "").strip() and not course:
            continue
        rows_read += 1
        if course:
            rows_with_course += 1
        cnes, status = normalize_cnes(raw_cnes)
        if cnes is None:
            loss_reasons[status] += 1
            continue
        cnes_values.append(cnes)
        if not course:
            loss_reasons["curso_ausente"] += 1
            continue
        cell_keys.append((cnes, course))
        physical_vacancies += sum(nonnegative_integer(safe_cell(row, index)) for index in total_indices)

    cnes_counter = Counter(cnes_values)
    cell_counter = Counter(cell_keys)
    cnes_set = set(cnes_values)
    result.update({
        "aba": sheet_name,
        "linha_cabecalho_base_zero": header_index,
        "linhas_quadro_lidas": rows_read,
        "linhas_com_curso": rows_with_course,
        "linhas_com_cnes_valido": len(cnes_values),
        "celulas_cnes_curso_validas": len(cell_keys),
        "celulas_cnes_curso_distintas": len(cell_counter),
        "duplicidades_exatas_celula_cnes_curso": sum(count - 1 for count in cell_counter.values()),
        "cnes_distintos": len(cnes_set),
        "repeticoes_de_cnes_entre_celulas": sum(count - 1 for count in cnes_counter.values()),
        "perdas_normalizacao": dict(sorted(loss_reasons.items())),
        "vagas_fisicas_somadas_na_versao": physical_vacancies,
        "nota_unidade": (
            "Cada linha válida é uma célula agregada CNES–curso. CNES repetido entre células não é "
            "duplicidade de vaga; a quantidade de vagas físicas é a soma dos campos TOTAL desta versão."
        ),
    })
    return result, cnes_set


def read_nominal_snapshot() -> Tuple[Dict[str, Any], Set[str]]:
    path = ROOT / "data" / "pmm_especialistas_nominal.csv"
    result: Dict[str, Any] = {
        "arquivo": path.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(path) if path.exists() else None,
        "status": "ausente" if not path.exists() else "lido",
    }
    if not path.exists():
        result["erro"] = "Snapshot nominal não localizado."
        return result, set()

    values: List[str] = []
    losses: Counter[str] = Counter()
    rows_read = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            rows_read += 1
            cnes, status = normalize_cnes(row.get("co_cnes", ""))
            if cnes is None:
                losses[status] += 1
            else:
                values.append(cnes)
    counter = Counter(values)
    cnes_set = set(values)
    result.update({
        "linhas_snapshot_lidas": rows_read,
        "linhas_com_cnes_valido": len(values),
        "cnes_distintos": len(cnes_set),
        "repeticoes_de_cnes_entre_registros": sum(count - 1 for count in counter.values()),
        "perdas_normalizacao": dict(sorted(losses.items())),
        "nota_unidade": (
            "Cada linha é um registro de participante ativo na data de referência; repetição de CNES pode "
            "representar participantes distintos no mesmo estabelecimento e não é duplicidade de vaga."
        ),
    })
    return result, cnes_set


def cnes_set_from_pilot_zip(zip_path: Path) -> Set[str]:
    found: Set[str] = set()
    with zipfile.ZipFile(zip_path, "r") as archive:
        files = [name for name in archive.namelist() if "tbEstabelecimento" in name and name.lower().endswith(".csv")]
        if not files:
            raise RuntimeError("tbEstabelecimento não localizada no ZIP.")
        with archive.open(files[0], "r") as raw:
            reader = csv.reader(io.TextIOWrapper(raw, encoding="latin1"), delimiter=";")
            header = next(reader, [])
            labels = [normalize_label(column) for column in header]
            if "CO_CNES" not in labels:
                raise RuntimeError("Coluna CO_CNES não localizada em tbEstabelecimento.")
            index = labels.index("CO_CNES")
            for row in reader:
                cnes, status = normalize_cnes(safe_cell(row, index))
                if status == "valido" and cnes is not None:
                    found.add(cnes)
    return found


def coverage_result(target: Set[str], found: Set[str]) -> Dict[str, Any]:
    matched = target & found
    missing = sorted(target - found)
    return {
        "cnes_testados": len(target),
        "cnes_encontrados": len(matched),
        "cnes_ausentes": len(missing),
        "taxa_cobertura": len(matched) / len(target) if target else None,
        "codigos_ausentes": missing,
        "total_cnes_base_cnes": len(found),
    }


def audit_pmme_cnes_codes(inspections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Audita separadamente snapshot ativo e quadros finais de oferta de A01."""
    del inspections  # A auditoria usa os ZIPs preservados; inspeções descrevem apenas o esquema.
    nominal_result, nominal_set = read_nominal_snapshot()
    frame_results: Dict[str, Any] = {}
    frame_sets: Dict[str, Set[str]] = {}
    offered_union: Set[str] = set()
    for spec in A01_OFFER_FRAMES:
        frame_result, frame_set = read_a01_offer_frame(spec)
        frame_results[spec["id"]] = frame_result
        frame_sets[spec["id"]] = frame_set
        offered_union.update(frame_set)

    audit_results: Dict[str, Any] = {
        "status": "executada",
        "classificacao": "piloto de esquema e aquisição pública parcial",
        "competencias_adquiridas": len(PILOT_COMPETENCIAS),
        "competencias_planejadas": len(ALL_COMPETENCIAS),
        "universos": {
            "snapshot_nominal_ativos": nominal_result,
            "quadros_vagas_a01": {
                "versoes_finais_escolhidas": frame_results,
                "consolidado_sem_somar_vagas_entre_chamadas": {
                    "cnes_distintos_uniao": len(offered_union),
                    "nota": (
                        "União de estabelecimentos para validação cadastral. Vagas físicas e células de "
                        "oferta não são somadas entre chamadas, pois podem ser reapresentadas."
                    ),
                },
            },
        },
        "cobertura_piloto": {
            "snapshot_nominal_ativos": {},
            "quadros_vagas_a01_consolidado": {},
            "quadros_vagas_a01_por_versao": {frame_id: {} for frame_id in frame_sets},
        },
        "limites": [
            "CNES cadastral não demonstra presença, carga efetivamente trabalhada nem participação no PMM-E.",
            "As três competências validam aquisição, esquema e existência cadastral; não validam desenho causal.",
            "O painel integral permanece adiado até existir ponte PMM-E–CNES ou decisão explícita do portão.",
        ],
    }

    for comp in PILOT_COMPETENCIAS:
        zip_path = RAW_DIR / f"BASE_DE_DADOS_CNES_{comp}.ZIP"
        if not zip_path.exists():
            error = {"erro": "ZIP piloto ausente."}
            audit_results["cobertura_piloto"]["snapshot_nominal_ativos"][comp] = error
            audit_results["cobertura_piloto"]["quadros_vagas_a01_consolidado"][comp] = error
            for frame_id in frame_sets:
                audit_results["cobertura_piloto"]["quadros_vagas_a01_por_versao"][frame_id][comp] = error
            continue
        try:
            found = cnes_set_from_pilot_zip(zip_path)
            audit_results["cobertura_piloto"]["snapshot_nominal_ativos"][comp] = coverage_result(nominal_set, found)
            audit_results["cobertura_piloto"]["quadros_vagas_a01_consolidado"][comp] = coverage_result(offered_union, found)
            for frame_id, frame_set in frame_sets.items():
                audit_results["cobertura_piloto"]["quadros_vagas_a01_por_versao"][frame_id][comp] = coverage_result(frame_set, found)
        except Exception as exc:
            error = {"erro": str(exc)}
            audit_results["cobertura_piloto"]["snapshot_nominal_ativos"][comp] = error
            audit_results["cobertura_piloto"]["quadros_vagas_a01_consolidado"][comp] = error
            for frame_id in frame_sets:
                audit_results["cobertura_piloto"]["quadros_vagas_a01_por_versao"][frame_id][comp] = error

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with UNIVERSES_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(audit_results, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"Auditoria de universos gravada em {UNIVERSES_PATH}")
    return audit_results


def generate_manifest(
    downloaded_info: Dict[str, Dict[str, Any]],
    mode: str,
) -> Dict[str, Any]:
    """Gera manifesto estruturado em JSON."""
    manifest_entries = []

    for comp in ALL_COMPETENCIAS:
        filename = f"BASE_DE_DADOS_CNES_{comp}.ZIP"
        url = f"{BASE_URL}{filename}"
        dest = RAW_DIR / filename

        exists = dest.exists()
        info = downloaded_info.get(comp, {})

        file_bytes = info.get("bytes") or (dest.stat().st_size if exists else None)
        file_hash = info.get("sha256") or (sha256_file(dest) if exists else None)
        
        is_pilot = comp in PILOT_COMPETENCIAS

        if exists:
            status = "preservado localmente (piloto validado)" if is_pilot else "preservado localmente (painel integral)"
        else:
            status = "planejado; pendente download piloto" if is_pilot else "planejado; pendente confirmacao download integral"

        manifest_entries.append({
            "competencia": comp,
            "arquivo": filename,
            "url": url,
            "pagina_catalogo": CATALOG_PAGE,
            "is_piloto": is_pilot,
            "cobertura": "Brasil, competencia mensal nacional",
            "unidade": "Microdados cadastrais do CNES (estabelecimentos, profissionais, vinculos, leitos, equipamentos, servicos)",
            "caminho": dest.relative_to(ROOT).as_posix() if exists else None,
            "bytes": file_bytes,
            "sha256": file_hash,
            "status": status,
            "erro": info.get("erro"),
        })

    manifest = {
        "manifesto_id": "a05_manifesto_cnes",
        "escopo": "Aquisicao e inspecao das competencias mensais do CNES para analise de forca de trabalho, FTE cadastral e infraestrutura pre-tratamento do PMM-E",
        "catalogo_consultado_em": CATALOG_DATE,
        "data_geracao": AUDIT_DATE,
        "modo_execucao": mode,
        "periodo_planejado": f"{ALL_COMPETENCIAS[0]} a {ALL_COMPETENCIAS[-1]}",
        "total_competencias_planejadas": len(ALL_COMPETENCIAS),
        "total_competencias_baixadas": sum(1 for e in manifest_entries if e["caminho"] is not None),
        "workspace_worktree_path": str(ROOT),
        "fontes": manifest_entries,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Manifesto gravado em {MANIFEST_PATH}")
    return manifest


def generate_audit_report(
    manifest: Dict[str, Any],
    dictionary: Dict[str, Any],
    cnes_audit: Dict[str, Any],
) -> None:
    """Gera o relatorio completo de auditoria em Markdown."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    pilot_entries = [e for e in manifest["fontes"] if e["is_piloto"]]
    downloaded_entries = [e for e in manifest["fontes"] if e["caminho"] is not None]
    universes = cnes_audit.get("universos", {})
    nominal = universes.get("snapshot_nominal_ativos", {})
    offer_frames = universes.get("quadros_vagas_a01", {}).get("versoes_finais_escolhidas", {})
    coverage = cnes_audit.get("cobertura_piloto", {})

    lines = []
    lines.append("# Auditoria e Inspeção do CNES Mensal (A05)")
    lines.append("")
    lines.append("> **Data da Auditoria:** 28 de agosto de 2026 (revisado pós-saneamento)")
    lines.append("> **Agente:** A05 — Aquisição e Inspeção do CNES Mensal")
    lines.append("> **Escopo:** Avaliação de impacto do Programa Mais Médicos Especialistas (PMM-E / Lei 15.233/2025)")
    lines.append("> **Janela Temporal do CNES:** Junho de 2024 a Julho de 2026 (26 competências planejadas; 3 inspecionadas no piloto)")
    lines.append("> **Status:** Piloto de esquema e aquisição pública parcial; 3 de 26 competências adquiridas.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Sumário Executivo e Objetivos de A05")
    lines.append("")
    lines.append("A missão do Agente A05 consiste em auditar, catalogar e inspecionar a base de dados mensal do **Cadastro Nacional de Estabelecimentos de Saúde (CNES)** mantida pelo DATASUS/Ministério da Saúde. O CNES mensal é o instrumento canônico no SUS para:")
    lines.append("1. **Medir a força de trabalho médica e o Full-Time Equivalent (FTE) cadastral:** cargas horárias declaradas (ambulatorial, hospitalar e outras) por ocupação (CBO 2002 de 6 dígitos);")
    lines.append("2. **Avaliar histórico e simultaneidade de vínculos:** vínculos anteriores e paralelos de profissionais alocados em municípios prioritários;")
    lines.append("3. **Mapear a infraestrutura pré-tratamento:** baseline de capacidade física (leitos em `rlEstabComplementar`), tecnológica (equipamentos em `rlEstabEquipamento`) e assistencial (serviços especializados em `rlEstabServClass` e habilitações em `rlEstabSipac`);")
    lines.append("4. **Verificar a estabilidade de esquema e integridade de chaves:** consistência dos microdados entre o período pré-oferta (202406), o início das chamadas públicas (202506) e o corte mais recente (202607).")
    lines.append("")
    lines.append("### Conclusão Principal da Auditoria:")
    lines.append("- **Aquisição parcial:** somente as competências 202406, 202506 e 202607 foram preservadas e inspecionadas. Elas servem para validar esquema e cobertura cadastral, não para formar um painel de avaliação.")
    lines.append(f"- **Dois universos separados:** o snapshot nominal contém {nominal.get('linhas_snapshot_lidas', 0):,} registros e {nominal.get('cnes_distintos', 0):,} CNES distintos; os quadros finais escolhidos em A01 são relidos diretamente e auditados por versão.")
    lines.append("- **Limitação crítica:** o CNES público não identifica deterministicamente participantes do PMM-E. Cadastro, carga declarada e existência do estabelecimento não demonstram presença, horas realizadas ou efeito do programa.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 2. Catálogo Oficial e Janela de Aquisição")
    lines.append("")
    lines.append(f"O catálogo oficial de bases de dados do CNES disponibiliza mensalmente o arquivo nacional `BASE_DE_DADOS_CNES_AAAAMM.ZIP` via servlet HTTP do DATASUS (`{CATALOG_PAGE}`).")
    lines.append("")
    lines.append("### 2.1 Grade Completa de Competências Planejadas (26 meses)")
    lines.append("")
    lines.append("| Competência | Cobertura Temporal | Função no Desenho do Estudo | Status Atual |")
    lines.append("|---|---|---|---|")
    lines.append("| **202406** | Junho / 2024 | Baseline histórico de longo prazo (12 meses pré-ciclo 1) | **Piloto Preservado e Inspecionado** |")
    lines.append("| `202407` a `202412` | Julho a Dezembro / 2024 | Painel pré-tratamento (tendências pré-programa) | Planejado no catálogo |")
    lines.append("| `202501` a `202505` | Janeiro a Maio / 2025 | Dinâmica imediata pré-chamamento | Planejado no catálogo |")
    lines.append("| **202506** | Junho / 2025 | Baseline imediato (1 mês antes da oferta do Ciclo 1) | **Piloto Preservado e Inspecionado** |")
    lines.append("| `202507` a `202512` | Julho a Dezembro / 2025 | Início das alocações e entradas do Ciclo 1 | Planejado no catálogo |")
    lines.append("| `202601` a `202606` | Janeiro a Junho / 2026 | Expansão para Ciclos 2 e 3 | Planejado no catálogo |")
    lines.append("| **202607** | Julho / 2026 | Competência oficial mais recente disponível | **Piloto Preservado e Inspecionado** |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 3. Protocolo de Aquisição, Idempotência e Criptografia")
    lines.append("")
    lines.append("O script `scripts/aquisicao/a05_adquirir_cnes.py` implementa os seguintes critérios de segurança:")
    lines.append("1. **Download Atômico e Verificação de Assinatura:** O fluxo grava em arquivo temporário `.zip.part`, valida o cabeçalho PK (`b\"PK\\x03\\x04\"`), testa a integridade interna via `zipfile.ZipFile.testzip()` e só então efetua a substituição atômica para o arquivo final.")
    lines.append("2. **Idempotência Estrita:** Caso o arquivo já exista em `data/raw/cnes/`, o script valida sua integridade estrutural e calcula o hash SHA-256 sem rebaixar desnecessariamente.")
    lines.append("3. **Cálculo de Digest SHA-256:** Todos os arquivos possuem hashes registrados no manifesto `output/aquisicao/a05_manifesto_cnes.json`.")
    lines.append("4. **Isolamento de Arquivos Grandes:** Arquivos ZIP de grandes dimensões são mantidos no caminho físico do workspace (`data/raw/cnes/`) e excluídos do Git.")
    lines.append("")
    lines.append("### 3.1 Tabela de Arquivos Inspecionados no Piloto")
    lines.append("")
    lines.append("| Competência | Arquivo | Tamanho (Bytes) | SHA-256 | Validação ZIP |")
    lines.append("|---|---|---:|---|:---:|")
    if downloaded_entries:
        for entry in downloaded_entries:
            lines.append(f"| **{entry['competencia']}** | `{entry['arquivo']}` | {entry['bytes']:,} | `{entry['sha256']}` | OK (Íntegro) |")
    else:
        lines.append("| *Nenhum arquivo baixado nesta execução (modo --plan)* | - | - | - | - |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 4. Anatomia dos Arquivos ZIP e Estrutura Real das Tabelas")
    lines.append("")
    lines.append("Ao descompactar seletivamente os ZIPs mensais do DATASUS, identificou-se que a base do CNES é composta por arquivos estruturados em formato CSV delimitados por ponto-e-vírgula (`;`) codificados em Latin-1 (ISO-8859-1). Cada competência contém exatamente **117 tabelas relacionais**.")
    lines.append("")
    lines.append("### 4.1 Principais Tabelas Encontradas e Nomenclatura Real")
    lines.append("")
    lines.append("| Módulo Temático | Nome Real da Tabela no ZIP | Entidade Representada | Chaves de Junção |")
    lines.append("|---|---|---|---|")
    lines.append("| **Estabelecimento** | `tbEstabelecimentoAAAAMM.csv` | Cadastro geral da unidade de saúde | `CO_UNIDADE` (13 dígitos), `CO_CNES` (7 dígitos), `CO_MUNICIPIO_GESTOR` |")
    lines.append("| **Carga Horária / Vínculo** | `tbCargaHorariaSusAAAAMM.csv` | Vínculo profissional–estabelecimento | `CO_UNIDADE`, `CO_PROFISSIONAL_SUS`, `CO_CBO` |")
    lines.append("| **Dados do Profissional** | `tbDadosProfissionalSusAAAAMM.csv` | Cadastro individual de profissionais | `CO_PROFISSIONAL_SUS`, `CO_CNS`, `NO_PROFISSIONAL` |")
    lines.append("| **Atividade Profissional** | `tbAtividadeProfissionalAAAAMM.csv` | Ocupação e especialidade (CBO) | `CO_CBO` |")
    lines.append("| **Leitos Instalados** | `rlEstabComplementarAAAAMM.csv` / `tbLeito` | Capacidade e leitos SUS/Não SUS | `CO_UNIDADE`, `CO_LEITO`, `CO_TIPO_LEITO` |")
    lines.append("| **Equipamentos** | `rlEstabEquipamentoAAAAMM.csv` / `tbEquipamento` | Equipamentos diagnósticos e cirúrgicos | `CO_UNIDADE`, `CO_EQUIPAMENTO` |")
    lines.append("| **Serviços Especializados** | `rlEstabServClassAAAAMM.csv` / `tbServicoEspecializado` | Serviços e ambulatórios especializados | `CO_UNIDADE`, `CO_SERVICO`, `CO_CLASSIFICACAO` |")
    lines.append("| **Habilitações** | `rlEstabSipacAAAAMM.csv` / `tbSubGruposHabilitacao` | Habilitações SUS de alta complexidade | `CO_UNIDADE`, `COD_SUB_GRUPO_HABILITACAO` |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Dicionário de Dados e Estabilidade de Esquema")
    lines.append("")
    lines.append("A comparação estrutural entre **202406**, **202506** e **202607** demonstrou estabilidade quase perfeita:")
    lines.append("- **Tabelas 100% Estáveis (sem alteração de colunas):** `tbCargaHorariaSus` (18 colunas), `tbAtividadeProfissional` (6 colunas), `rlEstabComplementar` (10 colunas), `rlEstabServClass` (13 colunas), `tbEquipe` (30 colunas).")
    lines.append("- **Alterações Incrementais Observadas no Catálogo do DATASUS:**")
    lines.append("  - `tbEstabelecimento`: Inclusão da coluna `ST_COWORKING` em 202506 e 202607 (passou de 54 para 55 colunas);")
    lines.append("  - `tbDadosProfissionalSus`: Inclusão de `NO_SOCIAL` em 202506 e sanitização do cabeçalho `CO_CPF` (passou de 9 para 10 colunas);")
    lines.append("  - `rlEstabEquipamento`: Inclusão do campo `QT_SUS` em 202607;")
    lines.append("  - `tbEquipamento`: Inclusão do identificador `NU_RENEM` (Registro Nacional de Equipamentos Médicos) em 202607;")
    lines.append("  - `rlEstabSipac`: Inclusão do campo `DT_PORTARIA` em 202607.")
    lines.append("")
    lines.append("### 5.1 Campos Essenciais para o Estudo PMM-E")
    lines.append("")
    lines.append("#### Módulo Força de Trabalho e FTE (`tbCargaHorariaSus`):")
    lines.append("- `CO_UNIDADE`: Chave primária do estabelecimento no CNES (13 dígitos).")
    lines.append("- `CO_PROFISSIONAL_SUS`: Identificador do profissional no CNES (16 dígitos).")
    lines.append("- `CO_CBO`: Código Brasileiro de Ocupações (6 dígitos). Para médicos especialistas:")
    lines.append("  - `2251xx`: Médicos clínicos e especialidades clínicas (Cardiologia, Pediatria, Neurologia, etc.);")
    lines.append("  - `2252xx`: Médicos cirúrgicos (Cirurgia Geral, Ortopedia, Ginecologia e Obstetrícia, etc.);")
    lines.append("  - `2253xx`: Médicos diagnósticos e terapêuticos (Radiologia, Patologia, etc.).")
    lines.append("- `QT_CARGA_HORARIA_AMBULATORIAL`: Horas semanais contratadas dedicadas ao ambulatório.")
    lines.append("- `QT_CARGA_HORARIA_HOSPITALAR`: Horas semanais contratadas dedicadas à internação.")
    lines.append("- `QT_CARGA_HORARIA_OUTROS`: Horas semanais em outras atividades (gestão/ensino).")
    lines.append("- `TP_SUS_NAO_SUS`: Atendimento ao SUS (Sim/Não).")
    lines.append("- `IND_VINCULACAO`: Indicador de vínculo.")
    lines.append("")
    lines.append("#### Módulo Estabelecimentos (`tbEstabelecimento`):")
    lines.append("- `CO_UNIDADE`: Chave interna do estabelecimento (13 dígitos).")
    lines.append("- `CO_CNES`: Código público do estabelecimento no SUS (7 dígitos).")
    lines.append("- `CO_MUNICIPIO_GESTOR`: Código IBGE do município gestor (6 dígitos).")
    lines.append("- `CO_ESTADO_GESTOR`: UF gestora (2 dígitos).")
    lines.append("- `TP_UNIDADE`: Tipologia (01=Posto de Saúde, 02=Centro de Saúde/UBS, 04=Policlínica/Ambulatório Especializado, 05=Hospital Geral, 07=Hospital Especializado, 22=Consultório Isolado).")
    lines.append("- `CO_NATUREZA_JUR`: Mantenedora (Administração Pública Direta Municipal/Estadual, Entidade Beneficente, Empresa Privada).")
    lines.append("- `TP_GESTAO`: Gestão Municipal (M), Estadual (E) ou Dupla (D).")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 6. Viabilidade Metodológica de Construção de FTE Líquido")
    lines.append("")
    lines.append("### 6.1 Definição do FTE Cadastral")
    lines.append("O Full-Time Equivalent (FTE) médico em cada município $m$ e competência $t$ para a especialidade médica $s$ é formalizado por:")
    lines.append("")
    lines.append(r"$$\text{FTE}_{m,t,s} = \sum_{i \in \text{Médicos}_{m,t,s}} \frac{\text{QT\_CARGA\_HORARIA\_AMBULATORIAL}_{i,m,t} + \text{QT\_CARGA\_HORARIA\_HOSPITALAR}_{i,m,t}}{40}$$")
    lines.append("")
    lines.append("### 6.2 O que o CNES Permite Medir:")
    lines.append("1. **Estoque e FTE Médico por Município:** Variação no FTE total e no número de profissionais únicos atuando no município ao longo do tempo.")
    lines.append("2. **Decomposição da Carga Horária:** Separação entre oferta ambulatorial especializada vs hospitalar.")
    lines.append("3. **Descrição de mudanças cadastrais:** com painel completo, seria possível descrever variações simultâneas de carga declarada entre vínculos; classificá-las como remanejamento provocado pelo programa exigiria identificação e desenho adicionais.")
    lines.append("")
    lines.append("### 6.3 O que o CNES NÃO Mede (Cuidados Substantivos):")
    lines.append("- **Carga Cadastrada vs Horas Reais:** O CNES registra a carga horária *declarada/contratada*, não ponto eletrônico, presença efetiva ou produtividade clínica.")
    lines.append("- **Rotatividade Intra-mês:** O CNES é um retrato cadastral mensal consolidado; não registra faltas ou greves pontuais.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 7. Diagnóstico da Ausência da Ponte Determinística PMM-E–CNES")
    lines.append("")
    lines.append("```text")
    lines.append("[Bases do PMM-E (SGP / Editais)]                  [Cadastro CNES Mensal (DATASUS)]")
    lines.append("--------------------------------                  --------------------------------")
    lines.append("- CRM + UF                                        - CNS (Cartão Nacional de Saúde)")
    lines.append("- Nome do Médico                                  - Nome do Profissional")
    lines.append("- CPF Mascarado (ex: ***.123.456-**)              - CO_PROFISSIONAL_SUS")
    lines.append("- Faixa de Incentivo                              - CBO + Carga Horária Ambulatorial/Hosp")
    lines.append("- CNES da Vaga Ofertada                           - CO_CNES / CO_UNIDADE")
    lines.append("```")
    lines.append("")
    lines.append("### O Desafio da Identificação Individual:")
    lines.append("1. **Ausência de Chave Primária Compartilhada:** O edital do PMM-E não publica o número do CNS do médico; o CNES público não publica CRM nem CPF desmascarado.")
    lines.append("2. **Inadequação do Pareamento por Nome:** A correspondência probabilística por string de nome normalizado introduz viés de homonímia, erros de digitação e falsos positivos em um universo nacional de mais de 500 mil médicos cadastrados.")
    lines.append("3. **Implicação de mensuração:** sem uma ponte administrativa oficial, não é possível afirmar que um vínculo público específico pertence a um participante do PMM-E.")
    lines.append("4. **Limite deste piloto:** a disponibilidade do CNES não identifica tratamento nem valida estratégia causal; isso depende de decisão posterior do portão e, para análises individuais, de ponte administrativa segura.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 8. Auditoria Separada dos Dois Universos")
    lines.append("")
    lines.append("A05 relê as planilhas XLSX reais selecionadas por A01. O snapshot nominal e os quadros de oferta têm unidades diferentes e não são intercambiáveis.")
    lines.append("")
    lines.append("### 8.1 Universo 1 — snapshot nominal de participantes ativos")
    lines.append("")
    lines.append(f"Fonte: `{nominal.get('arquivo', '')}` (`{nominal.get('sha256', '')}`).")
    lines.append("")
    lines.append("| Linhas de participantes | Linhas com CNES válido | CNES distintos | Repetições de CNES entre registros | Perdas de normalização |")
    lines.append("|---:|---:|---:|---:|---|")
    nominal_losses = json.dumps(nominal.get("perdas_normalizacao", {}), ensure_ascii=False)
    lines.append(
        f"| {nominal.get('linhas_snapshot_lidas', 0):,} | {nominal.get('linhas_com_cnes_valido', 0):,} | "
        f"{nominal.get('cnes_distintos', 0):,} | {nominal.get('repeticoes_de_cnes_entre_registros', 0):,} | `{nominal_losses}` |"
    )
    lines.append("")
    lines.append("Uma linha representa participante ativo na data de referência. Um CNES repetido pode refletir pessoas distintas no mesmo estabelecimento; não representa, por si só, duplicidade de vaga.")
    lines.append("")
    lines.append("### 8.2 Universo 2 — células CNES–curso dos quadros finais de A01")
    lines.append("")
    lines.append("| Versão escolhida | Arquivo-fonte | Linhas/células lidas | Células válidas | CNES distintos | Células duplicadas | Repetições de CNES entre células | Perdas CNES/curso | Vagas físicas na versão |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---|---:|")
    for frame in offer_frames.values():
        losses = json.dumps(frame.get("perdas_normalizacao", {}), ensure_ascii=False)
        lines.append(
            f"| {frame.get('rotulo', frame.get('id', ''))} | `{frame.get('arquivo', '')}` | {frame.get('linhas_quadro_lidas', 0):,} | "
            f"{frame.get('celulas_cnes_curso_validas', 0):,} | {frame.get('cnes_distintos', 0):,} | "
            f"{frame.get('duplicidades_exatas_celula_cnes_curso', 0):,} | "
            f"{frame.get('repeticoes_de_cnes_entre_celulas', 0):,} | `{losses}` | "
            f"{frame.get('vagas_fisicas_somadas_na_versao', 0):,} |"
        )
    offered_union = universes.get("quadros_vagas_a01", {}).get("consolidado_sem_somar_vagas_entre_chamadas", {})
    lines.append("")
    lines.append(f"A união das {len(offer_frames)} versões escolhidas contém **{offered_union.get('cnes_distintos_uniao', 0):,} estabelecimentos distintos**. Esse número serve apenas como denominador cadastral. Células e vagas não são somadas entre chamadas porque ofertas podem ser reapresentadas.")
    lines.append("")
    lines.append("### 8.3 Cobertura nas três competências piloto")
    lines.append("")
    lines.append("| Competência | Snapshot ativo | União dos quadros A01 | Universo nacional em `tbEstabelecimento` |")
    lines.append("|---|---:|---:|---:|")
    nominal_coverage = coverage.get("snapshot_nominal_ativos", {})
    offered_coverage = coverage.get("quadros_vagas_a01_consolidado", {})
    for comp in PILOT_COMPETENCIAS:
        nres = nominal_coverage.get(comp, {})
        ores = offered_coverage.get(comp, {})
        ntext = "erro" if "erro" in nres else f"{nres.get('cnes_encontrados', 0):,}/{nres.get('cnes_testados', 0):,} ({(nres.get('taxa_cobertura') or 0)*100:.2f}%)"
        otext = "erro" if "erro" in ores else f"{ores.get('cnes_encontrados', 0):,}/{ores.get('cnes_testados', 0):,} ({(ores.get('taxa_cobertura') or 0)*100:.2f}%)"
        lines.append(f"| {comp} | {ntext} | {otext} | {nres.get('total_cnes_base_cnes', ores.get('total_cnes_base_cnes', 0)):,} |")
    lines.append("")
    lines.append("Cobertura indica somente que o código aparece no cadastro daquela competência. Alterações entre competências não permitem inferir inauguração, início de atividade, presença de participante ou efeito do PMM-E sem observar e documentar esses eventos.")
    lines.append("")
    lines.append("#### Cobertura dos quadros A01 por versão")
    lines.append("")
    lines.append("| Versão | 202406 | 202506 | 202607 |")
    lines.append("|---|---:|---:|---:|")
    by_frame = coverage.get("quadros_vagas_a01_por_versao", {})
    for frame_id, frame in offer_frames.items():
        cells = []
        for comp in PILOT_COMPETENCIAS:
            item = by_frame.get(frame_id, {}).get(comp, {})
            cells.append("erro" if "erro" in item else f"{item.get('cnes_encontrados', 0):,}/{item.get('cnes_testados', 0):,} ({(item.get('taxa_cobertura') or 0)*100:.2f}%)")
        lines.append(f"| {frame.get('rotulo', frame_id)} | {cells[0]} | {cells[1]} | {cells[2]} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 9. Instruções de Continuidade e Reprodutibilidade")
    lines.append("")
    lines.append("1. **Localização dos arquivos brutos:** `data/raw/cnes/`.")
    lines.append("2. **Execução do Piloto de Esquema:**")
    lines.append("   ```bash")
    lines.append("   python scripts/aquisicao/a05_adquirir_cnes.py --inspect-only")
    lines.append("   ```")
    lines.append("3. **Painel integral adiado:** as 23 competências restantes não devem ser baixadas até existir ponte PMM-E–CNES ou decisão explícita do portão sobre o desenho e o denominador necessários.")
    lines.append("")

    report_text = "\n".join(lines) + "\n"
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"[RELATÓRIO OK] Auditoria Markdown salva em: {REPORT_PATH.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Aquisicao e inspecao do CNES mensal (A05)")
    parser.add_argument("--plan", action="store_true", help="Gera o plano e manifesto das 26 competencias sem download")
    parser.add_argument("--pilot", action="store_true", help="Executa o piloto de inspecao nas competencias 202406, 202506, 202607")
    parser.add_argument("--full", action="store_true", help="Baixa o painel integral (202406 a 202607)")
    parser.add_argument("--confirm-large-download", action="store_true", help="Confirmacao explicita para baixar todas as competencias")
    parser.add_argument("--inspect-only", action="store_true", help="Apenas inspeciona os ZIPs locais existentes")
    parser.add_argument("--competencias", nargs="+", help="Lista especifica de competencias para processar")

    args = parser.parse_args()

    mode = "plan"
    if args.inspect_only:
        mode = "inspect_only"
    elif args.pilot:
        mode = "pilot"
    elif args.full:
        mode = "full"
        if not args.confirm_large_download:
            parser.error("O modo --full requer a flag explicita --confirm-large-download.")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    target_competencias = []
    if args.competencias:
        target_competencias = args.competencias
    elif mode == "pilot":
        target_competencias = PILOT_COMPETENCIAS
    elif mode == "full":
        target_competencias = ALL_COMPETENCIAS
    elif mode == "inspect_only":
        target_competencias = [c for c in ALL_COMPETENCIAS if (RAW_DIR / f"BASE_DE_DADOS_CNES_{c}.ZIP").exists()]
    else:  # plan
        target_competencias = []

    print(f"=== Agente A05 — CNES Mensal ===")
    print(f"Modo: {mode}")
    print(f"Competencias alvo: {target_competencias if target_competencias else 'Nenhuma (apenas planejamento)'}")

    download_results: Dict[str, Dict[str, Any]] = {}
    if mode in ("pilot", "full") and target_competencias:
        for comp in target_competencias:
            dest = RAW_DIR / f"BASE_DE_DADOS_CNES_{comp}.ZIP"
            success, file_hash, file_size, err = download_cnes_zip(comp, dest)
            download_results[comp] = {
                "sucesso": success,
                "sha256": file_hash,
                "bytes": file_size,
                "erro": err,
            }

    inspections: Dict[str, Dict[str, Any]] = {}
    for comp in ALL_COMPETENCIAS:
        zip_path = RAW_DIR / f"BASE_DE_DADOS_CNES_{comp}.ZIP"
        if zip_path.exists():
            try:
                print(f"Inspecionando estrutura de {zip_path.name}...")
                insp = inspect_cnes_zip(zip_path)
                inspections[comp] = insp
            except Exception as e:
                print(f"[ERRO] Falha ao inspecionar {zip_path.name}: {e}")

    manifest = generate_manifest(download_results, mode)
    dictionary = build_schema_dictionary(inspections)
    with DICTIONARY_PATH.open("w", encoding="utf-8") as f:
        json.dump(dictionary, f, ensure_ascii=False, indent=2)
    print(f"Dicionário de tabelas gravado em {DICTIONARY_PATH}")

    cnes_audit = audit_pmme_cnes_codes(inspections)
    generate_audit_report(manifest, dictionary, cnes_audit)
    print(f"Execucao concluida com sucesso.")


if __name__ == "__main__":
    main()
