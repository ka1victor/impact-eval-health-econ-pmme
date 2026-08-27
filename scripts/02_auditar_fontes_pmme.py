"""Audita estrutura e vinculacao das fontes locais e das planilhas do PMM-E.

O leitor XLSX usa apenas a biblioteca padrao e nunca modifica os arquivos de
origem. O produto e diagnostico; nao contem estimativas de efeito.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
import zipfile
from collections import Counter
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw" / "pmm_e"
OUTPUT = ROOT / "output" / "auditoria_fontes_pmme.json"
AUDIT_DATE = "2026-08-27"
NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text).strip().upper()


def normalize_course(value: object) -> str:
    text = re.sub(r"^\d+[.\-]?\s*", "", normalize(value))
    return re.sub(r"^APRIMORAMENTO EM\s+", "", text)


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


def nonempty_data_rows(rows: list[list[object]], header_index: int) -> list[list[object]]:
    return [row for row in rows[header_index + 1 :] if any(str(value).strip() for value in row)]


def value(row: list[object], index: int) -> object:
    return row[index] if index < len(row) else ""


def numeric(value_: object) -> int:
    try:
        return int(float(str(value_).replace(",", ".")))
    except (TypeError, ValueError):
        return 0


def summarize_workbooks() -> tuple[dict[str, object], set[str], set[tuple[str, str]]]:
    summaries: dict[str, object] = {}
    public_names: set[str] = set()
    vacancy_keys: set[tuple[str, str]] = set()

    for path in sorted(RAW.glob("*.xlsx")):
        sheets = xlsx_sheets(path)
        summary: dict[str, object] = {
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "sheets": {name: {"linhas_xml": len(rows)} for name, rows in sheets.items()},
        }

        if path.name == "2025_ciclo1_chamada1_homologados.xlsx":
            rows = nonempty_data_rows(sheets["Quadro 1"], 0)
            names = {normalize(value(row, 7)) for row in rows if normalize(value(row, 7))}
            public_names |= names
            summary["homologados"] = len(rows)
            summary["candidatos_unicos_nome"] = len(names)

        elif path.name == "2025_ciclo1_chamada2_vagas_e_alocados.xlsx":
            candidates = nonempty_data_rows(sheets["ALOCADOS - VAGAS IMEDIATAS"], 0)
            reserve = nonempty_data_rows(sheets["VAGAS - CADASTRO RESERVA"], 1)
            names = {normalize(value(row, 7)) for row in candidates if normalize(value(row, 7))}
            public_names |= names
            summary["linhas_candidatos_vaga_imediata"] = len(candidates)
            summary["situacoes_candidatos"] = dict(Counter(normalize(value(row, 9)) for row in candidates))
            summary["linhas_ofertas_cadastro_reserva"] = len(reserve)
            summary["vagas_cadastro_reserva"] = sum(numeric(value(row, 9)) for row in reserve)
            for row in reserve:
                vacancy_keys.add((normalize_cnes(value(row, 5)), normalize_course(value(row, 0))))

        elif path.name == "2025_ciclo1_chamada2_classificacao_final.xlsx":
            allocated = nonempty_data_rows(sheets["ALOCADOS"], 1)
            disqualified = nonempty_data_rows(sheets["DESCLASSIFICADO"], 1)
            names = {normalize(value(row, 7)) for row in allocated if normalize(value(row, 7))}
            names |= {normalize(value(row, 2)) for row in disqualified if normalize(value(row, 2))}
            public_names |= names
            summary["linhas_classificacao"] = len(allocated)
            summary["situacoes"] = dict(Counter(normalize(value(row, 9)) for row in allocated))
            summary["desclassificados"] = len(disqualified)
            summary["candidatos_unicos_nome"] = len(names)

        elif path.name == "2025_ciclo1_chamada2_homologados.xlsx":
            rows = nonempty_data_rows(sheets["Homologados"], 0)
            names = {normalize(value(row, 1)) for row in rows if normalize(value(row, 1))}
            public_names |= names
            summary["homologados_publicados"] = len(rows)
            summary["candidatos_unicos_nome"] = len(names)

        elif path.name in {
            "2026_ciclo2_chamada1_vagas_retificadas.xlsx",
            "2026_ciclo2_chamada2_vagas.xlsx",
        }:
            sheet_name = next(iter(sheets))
            rows = nonempty_data_rows(sheets[sheet_name], 1)
            summary["linhas_oferta"] = len(rows)
            summary["vagas_imediatas"] = sum(numeric(value(row, 10)) for row in rows)
            summary["vagas_cadastro_reserva"] = sum(numeric(value(row, 14)) for row in rows)
            for row in rows:
                vacancy_keys.add((normalize_cnes(value(row, 5)), normalize_course(value(row, 0))))

        elif path.name == "2026_ciclo3_chamada1_vagas_retificadas.xlsx":
            rows = nonempty_data_rows(sheets[next(iter(sheets))], 2)
            summary["linhas_oferta"] = len(rows)
            summary["vagas_imediatas"] = sum(numeric(value(row, 11)) for row in rows)
            summary["vagas_cadastro_reserva"] = sum(numeric(value(row, 15)) for row in rows)
            for row in rows:
                vacancy_keys.add((normalize_cnes(value(row, 5)), normalize_course(value(row, 0))))

        elif path.name == "2026_ciclo3_adesao_gestores_resultado_final.xlsx":
            rows = nonempty_data_rows(sheets["RESULTADO FINAL"], 0)
            summary["linhas_proposta"] = len(rows)
            summary["vagas_priorizadas"] = sum(numeric(value(row, 11)) for row in rows)
            summary["vagas_imediatas"] = sum(numeric(value(row, 12)) for row in rows)
            summary["vagas_cadastro_reserva"] = sum(numeric(value(row, 13)) for row in rows)
            summary["vagas_nao_priorizadas"] = sum(numeric(value(row, 14)) for row in rows)

        elif "resultado" in path.name:
            sheet_name = "Classificados" if "Classificados" in sheets else next(iter(sheets))
            rows = nonempty_data_rows(sheets[sheet_name], 0)
            names = {normalize(value(row, 7)) for row in rows if normalize(value(row, 7))}
            public_names |= names
            summary["linhas_resultado"] = len(rows)
            summary["situacoes"] = dict(Counter(normalize(value(row, 9)) for row in rows))
            summary["candidatos_unicos_nome"] = len(names)
            if "Desclassificados" in sheets:
                disqualified = nonempty_data_rows(sheets["Desclassificados"], 0)
                summary["desclassificados"] = len(disqualified)
                public_names |= {
                    normalize(value(row, 2)) for row in disqualified if normalize(value(row, 2))
                }

        summaries[path.name] = summary

    return summaries, public_names, vacancy_keys


def main() -> None:
    nominal = read_csv(DATA / "pmm_especialistas_nominal.csv")
    series = read_csv(DATA / "pmm_especialistas_serie_historica.csv")
    ivs = read_csv(DATA / "ivs_ipea_2010_municipios.csv")
    workbooks, public_names, vacancy_keys = summarize_workbooks()

    nominal_names = [normalize(row["nome"]) for row in nominal]
    nominal_keys = [
        (normalize_cnes(row["co_cnes"]), normalize_course(row["curso"])) for row in nominal
    ]
    reference = max(datetime.strptime(row["dt_referencia"], "%Y-%m-%d").date() for row in nominal)
    starts = [datetime.strptime(row["dt_inicio_atividade"], "%Y-%m-%d").date() for row in nominal]
    crm_uf = Counter((normalize(row["uf"]), normalize(row["crm"])) for row in nominal)
    series_totals = Counter()
    for row in series:
        series_totals[row["competencia"]] += numeric(row["qtd_ativos"])

    calls = [
        ("2025_ciclo1_chamada1", date(2025, 7, 24)),
        ("2025_ciclo1_chamada2", date(2025, 9, 29)),
        ("2026_ciclo2_chamada1_retificacao_final", date(2026, 3, 19)),
        ("2026_ciclo2_chamada2", date(2026, 4, 16)),
        ("2026_ciclo3_chamada1_retificacao", date(2026, 7, 24)),
    ]
    windows = []
    for call, offer in calls:
        days = (reference - offer).days
        windows.append(
            {
                "chamada": call,
                "data_oferta_usada": offer.isoformat(),
                "fim_observado_local": reference.isoformat(),
                "dias_calendario_potenciais": days,
                "madura_90": days >= 90,
                "madura_120": days >= 120,
                "madura_180": days >= 180,
                "cobertura_mensuravel": False,
                "motivo": "fontes locais nao contem spells vaga-profissional nem eventos diarios",
            }
        )

    result = {
        "escopo": "auditoria descritiva de disponibilidade; nao estima efeitos",
        "data_auditoria": AUDIT_DATE,
        "bases_locais": {
            "pmm_especialistas_nominal.csv": {
                "sha256": sha256(DATA / "pmm_especialistas_nominal.csv"),
                "linhas": len(nominal),
                "campos": list(nominal[0]),
                "referencia": reference.isoformat(),
                "inicio_min": min(starts).isoformat(),
                "inicio_max": max(starts).isoformat(),
                "uf_crm_duplicados": sum(count - 1 for count in crm_uf.values() if count > 1),
                "linhas_com_nome": sum(bool(name) for name in nominal_names),
            },
            "pmm_especialistas_serie_historica.csv": {
                "sha256": sha256(DATA / "pmm_especialistas_serie_historica.csv"),
                "linhas": len(series),
                "campos": list(series[0]),
                "cnes_preenchido": sum(bool(row["co_cnes"].strip()) for row in series),
                "ativos_por_competencia": dict(sorted(series_totals.items())),
            },
            "ivs_ipea_2010_municipios.csv": {
                "sha256": sha256(DATA / "ivs_ipea_2010_municipios.csv"),
                "linhas": len(ivs),
                "campos": list(ivs[0]),
            },
        },
        "planilhas_oficiais": workbooks,
        "vinculacao": {
            "nomes_nominal_unicos": len(set(nominal_names)),
            "nomes_publicos_unicos": len(public_names),
            "linhas_nominal_com_match_exato_de_nome_publico": sum(
                name in public_names for name in nominal_names
            ),
            "linhas_nominal_com_match_cnes_curso_em_quadro_de_vagas": sum(
                key in vacancy_keys for key in nominal_keys
            ),
            "advertencia": "nome e CNES+curso ajudam auditoria, mas nao substituem identificador estavel de vaga ou profissional",
        },
        "janelas": windows,
    }
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Auditoria salva em {OUTPUT}")


if __name__ == "__main__":
    main()
