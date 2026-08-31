#!/usr/bin/env python3
"""C3-02B: SIH/RD pre-treatment panel and monthly SIGTAP history.

Only competencies 2024-06--2026-06 are read. DBC/DBF/ZIP inputs live in one
disposable temporary directory. Persistent products are aggregated panels,
file-level manifests and the monthly SIGTAP dictionary.
"""

from __future__ import annotations

import ftplib
import hashlib
import csv
import io
import json
import os
import sys
import tempfile
import threading
import time
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.utils.datasus_dbc import (  # noqa: E402
    compute_sha256,
    decompress_dbc_to_dbf,
    download_datasus_dbc,
    fast_read_dbf_cols,
)


OUTPUT = ROOT / "output" / "avaliacao_ciclo3"
SIH_OUTPUT = OUTPUT / "sih_pre"
DOC = ROOT / "docs" / "auditorias" / "06_piloto_sih_anestesiologia.md"
COHORT = OUTPUT / "coorte_c3_congelada.parquet"

COMPETENCIAS = [
    "202406", "202407", "202408", "202409", "202410", "202411", "202412",
    "202501", "202502", "202503", "202504", "202505", "202506", "202507",
    "202508", "202509", "202510", "202511", "202512", "202601", "202602",
    "202603", "202604", "202605", "202606",
]
UFS_BRASIL = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG",
    "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR",
    "RS", "SC", "SE", "SP", "TO",
]
T0_PROVISORIO = "202609"

# Official versions observed before execution. Pinning prevents silent revision.
SIGTAP_FILES = {
    "202406": "TabelaUnificada_202406_v2406131920.zip",
    "202407": "TabelaUnificada_202407_v2408022004.zip",
    "202408": "TabelaUnificada_202408_v2409111413.zip",
    "202409": "TabelaUnificada_202409_v2409111422.zip",
    "202410": "TabelaUnificada_202410_v2410041744.zip",
    "202411": "TabelaUnificada_202411_v2411071955.zip",
    "202412": "TabelaUnificada_202412_v2501172121.zip",
    "202501": "TabelaUnificada_202501_v2501172128.zip",
    "202502": "TabelaUnificada_202502_v2502131336.zip",
    "202503": "TabelaUnificada_202503_v2503101901.zip",
    "202504": "TabelaUnificada_202504_v2504031832.zip",
    "202505": "TabelaUnificada_202505_v2505061938.zip",
    "202506": "TabelaUnificada_202506_v2506061904.zip",
    "202507": "TabelaUnificada_202507_v2509181303.zip",
    "202508": "TabelaUnificada_202508_v2509181304.zip",
    "202509": "TabelaUnificada_202509_v2602261623.zip",
    "202510": "TabelaUnificada_202510_v2602261632.zip",
    "202511": "TabelaUnificada_202511_v2602261636.zip",
    "202512": "TabelaUnificada_202512_v2602261637.zip",
    "202601": "TabelaUnificada_202601_v2602261640.zip",
    "202602": "TabelaUnificada_202602_v2602261644.zip",
    "202603": "TabelaUnificada_202603_v2605181534.zip",
    "202604": "TabelaUnificada_202604_v2605181544.zip",
    "202605": "TabelaUnificada_202605_v2605210940.zip",
    "202606": "TabelaUnificada_202606_v2606091427.zip",
}
SIGTAP_HOST = "ftp2.datasus.gov.br"
SIGTAP_DIR = "/pub/sistemas/tup/downloads"


class PeakDiskTracker:
    """Peak at controlled file lifecycle transitions."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sizes: dict[str, int] = {}
        self.peak_bytes = 0
        self.peak_files: list[str] = []
        self.peak_at_utc: str | None = None

    def register(self, path: Path) -> None:
        size = path.stat().st_size
        with self._lock:
            self._sizes[str(path)] = size
            total = sum(self._sizes.values())
            if total > self.peak_bytes:
                self.peak_bytes = total
                self.peak_files = sorted(Path(x).name for x in self._sizes)
                self.peak_at_utc = datetime.now(timezone.utc).isoformat()

    def unregister(self, path: Path) -> None:
        with self._lock:
            self._sizes.pop(str(path), None)


class DirectoryPeakMonitor:
    """Observe every temporary file, including in-progress .part downloads."""

    def __init__(self, directory: Path, interval_s: float = 0.01) -> None:
        self.directory = directory
        self.interval_s = interval_s
        self.peak_bytes = 0
        self.peak_files: list[str] = []
        self.peak_at_utc: str | None = None
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join()
        self._sample()

    def _sample(self) -> None:
        try:
            files = [p for p in self.directory.iterdir() if p.is_file()]
            total = sum(p.stat().st_size for p in files)
        except (FileNotFoundError, OSError):
            return
        if total > self.peak_bytes:
            self.peak_bytes = total
            self.peak_files = sorted(p.name for p in files)
            self.peak_at_utc = datetime.now(timezone.utc).isoformat()

    def _run(self) -> None:
        while not self._stop.wait(self.interval_s):
            self._sample()


def _ftp_download(host: str, remote_dir: str, filename: str, dest: Path) -> dict:
    last_error: Exception | None = None
    part = dest.with_suffix(dest.suffix + ".part")
    for _attempt in range(3):
        ftp = None
        try:
            ftp = ftplib.FTP(host, timeout=60)
            ftp.login()
            ftp.cwd(remote_dir)
            with part.open("wb") as handle:
                ftp.retrbinary(f"RETR {filename}", handle.write)
            ftp.quit()
            part.replace(dest)
            return {
                "arquivo": filename,
                "source_url": f"ftp://{host}{remote_dir}/{filename}",
                "size_bytes": dest.stat().st_size,
                "sha256": compute_sha256(str(dest)),
            }
        except Exception as exc:  # pragma: no cover - network-dependent
            last_error = exc
            if ftp is not None:
                try:
                    ftp.close()
                except Exception:
                    pass
            part.unlink(missing_ok=True)
    raise OSError(f"Falha ao baixar {filename}: {last_error}")


def _parse_sigtap_layout(raw: bytes) -> dict[str, tuple[int, int]]:
    text = raw.decode("latin-1").replace("\r\n", "\n")
    rows = csv.DictReader(io.StringIO(text))
    layout = {
        row["Coluna"].strip(): (int(row["Inicio"]) - 1, int(row["Fim"]))
        for row in rows
    }
    required = {
        "CO_PROCEDIMENTO", "NO_PROCEDIMENTO", "TP_COMPLEXIDADE", "TP_SEXO",
        "CO_FINANCIAMENTO", "CO_RUBRICA", "DT_COMPETENCIA",
    }
    if not required.issubset(layout):
        raise ValueError(f"Layout SIGTAP incompleto: {sorted(required - set(layout))}")
    return layout


def _parse_sigtap_procedures(
    raw: bytes, layout_raw: bytes, competencia: str, source: dict
) -> pd.DataFrame:
    """Parse official fixed-width tb_procedimento.txt; keep candidate group 04."""
    rows: list[dict] = []
    layout = _parse_sigtap_layout(layout_raw)
    expected_length = max(end for _start, end in layout.values())

    def field(line: bytes, name: str, encoding: str = "ascii") -> str:
        start, end = layout[name]
        return line[start:end].decode(encoding).strip()

    for line in raw.splitlines():
        if len(line) < expected_length:
            raise ValueError(f"Linha SIGTAP curta em {competencia}: {len(line)} bytes")
        code = field(line, "CO_PROCEDIMENTO")
        row_comp = field(line, "DT_COMPETENCIA")
        if row_comp != competencia:
            raise ValueError(f"Competência interna SIGTAP {row_comp} != {competencia}")
        if not code.startswith("04"):
            continue
        rows.append({
            "competencia": competencia,
            "co_procedimento": code,
            "no_procedimento": field(line, "NO_PROCEDIMENTO", "latin-1"),
            "tp_complexidade": field(line, "TP_COMPLEXIDADE"),
            "tp_sexo": field(line, "TP_SEXO"),
            "co_financiamento": field(line, "CO_FINANCIAMENTO"),
            "co_rubrica": field(line, "CO_RUBRICA"),
            "grupo_sigtap": code[:2],
            "subgrupo_sigtap": code[:4],
            "forma_organizacao_sigtap": code[:6],
            "regra_operacional": "procedimento vigente na competencia e CO_PROCEDIMENTO inicia por 04",
            "status_clinico": "CANDIDATO_AMPLO_NAO_ESPECIFICO_A_ANESTESIOLOGIA",
            "arquivo_fonte": source["arquivo"],
            "source_url": source["source_url"],
            "sha256_fonte": source["sha256"],
        })
    if not rows:
        raise ValueError(f"Nenhum procedimento do grupo 04 no SIGTAP {competencia}")
    return pd.DataFrame(rows)


def acquire_sigtap(
    temp_dir: Path, tracker: PeakDiskTracker
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, frozenset[str]], int]:
    frames: list[pd.DataFrame] = []
    manifests: list[dict] = []
    total_bytes = 0
    for competencia in COMPETENCIAS:
        filename = SIGTAP_FILES[competencia]
        path = temp_dir / filename
        acquired_at = datetime.now(timezone.utc).isoformat()
        try:
            source = _ftp_download(SIGTAP_HOST, SIGTAP_DIR, filename, path)
            tracker.register(path)
            total_bytes += source["size_bytes"]
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                if "tb_procedimento.txt" not in names or "tb_procedimento_layout.txt" not in names:
                    raise ValueError("ZIP SIGTAP sem tabela/layout de procedimento")
                raw = archive.read("tb_procedimento.txt")
                layout_raw = archive.read("tb_procedimento_layout.txt")
                layout_hash = hashlib.sha256(layout_raw).hexdigest()
            frame = _parse_sigtap_procedures(
                raw, layout_raw, competencia, source
            )
            frames.append(frame)
            manifests.append({
                **source,
                "competencia": competencia,
                "adquirido_em_utc": acquired_at,
                "linhas_tb_procedimento": len(raw.splitlines()),
                "linhas_grupo04": len(frame),
                "sha256_layout_tb_procedimento": layout_hash,
                "status": "SUCCESS",
            })
        except Exception as exc:
            manifests.append({
                "arquivo": filename,
                "source_url": f"ftp://{SIGTAP_HOST}{SIGTAP_DIR}/{filename}",
                "competencia": competencia,
                "adquirido_em_utc": acquired_at,
                "status": f"ERROR: {str(exc).strip()}",
            })
            raise
        finally:
            tracker.unregister(path)
            path.unlink(missing_ok=True)

    dictionary = pd.concat(frames, ignore_index=True).sort_values(
        ["competencia", "co_procedimento"], kind="stable"
    ).reset_index(drop=True)
    manifest = pd.DataFrame(manifests).sort_values("competencia").reset_index(drop=True)
    if len(manifest) != 25 or manifest["competencia"].nunique() != 25:
        raise AssertionError("Manifesto SIGTAP deve ter 25 competências únicas")
    codes = {
        comp: frozenset(group["co_procedimento"].astype(str))
        for comp, group in dictionary.groupby("competencia")
    }
    return dictionary, manifest, codes, total_bytes


def _persist_sigtap(dictionary: pd.DataFrame, manifest: pd.DataFrame) -> tuple[Path, Path]:
    dictionary_path = OUTPUT / "dicionario_procedimentos_anestesia.csv"
    manifest_path = OUTPUT / "manifesto_sigtap_pre.csv"
    dictionary_tmp = dictionary_path.with_suffix(".csv.tmp")
    manifest_tmp = manifest_path.with_suffix(".csv.tmp")
    dictionary.to_csv(
        dictionary_tmp, index=False, encoding="utf-8", lineterminator="\n"
    )
    manifest.to_csv(
        manifest_tmp, index=False, encoding="utf-8", lineterminator="\n"
    )
    for source, target in [
        (dictionary_tmp, dictionary_path),
        (manifest_tmp, manifest_path),
    ]:
        last_error: OSError | None = None
        for _attempt in range(10):
            try:
                os.replace(source, target)
                last_error = None
                break
            except PermissionError as exc:
                last_error = exc
                time.sleep(0.5)
        if last_error is not None:
            raise last_error
    return dictionary_path, manifest_path


def _sih_remote_catalog() -> set[str]:
    ftp = ftplib.FTP("ftp.datasus.gov.br", timeout=60)
    try:
        ftp.login()
        ftp.cwd("/dissemin/publicos/SIHSUS/200801_/Dados")
        return set(ftp.nlst())
    finally:
        try:
            ftp.quit()
        except Exception:
            ftp.close()


def _required_sih_files() -> dict[tuple[str, str], str]:
    return {
        (uf, comp): f"RD{uf}{comp[2:4]}{comp[4:6]}.dbc"
        for uf in UFS_BRASIL
        for comp in COMPETENCIAS
    }


def construir_meta_municipal(df_anes: pd.DataFrame) -> pd.DataFrame:
    """Classify all local anaesthesiology cells; never select an arbitrary row."""
    records = []
    for ibge, group in df_anes.groupby("ibge", sort=True):
        arms = set(group["classificacao_braco"])
        immediate = "imediata_pura" in arms
        control = "nao_priorizada_pura" in arms
        reserved_or_mixed = bool(arms & {"reserva_pura", "mista"})
        if immediate and not reserved_or_mixed:
            exposure = "imediata_pura"
        elif control and not immediate and not reserved_or_mixed:
            exposure = "nao_priorizada_pura"
        else:
            exposure = "excluida_reserva_mista"
        cointervention = bool(group["cointervencao_cirurgica_muni"].any())
        eligible = exposure in {"imediata_pura", "nao_priorizada_pura"}
        records.append({
            "ibge": str(ibge).zfill(6),
            "uf": group["uf"].iloc[0],
            "classificacao_braco": exposure,
            "bracos_anestesia_no_municipio": "|".join(sorted(arms)),
            "amostra_anestesia_total": eligible,
            "cointervencao_cirurgica_muni": cointervention,
            "amostra_anestesia_isolada": eligible and not cointervention,
        })
    return pd.DataFrame(records)


def _normalise_sih(
    df: pd.DataFrame, competencia: str, active_codes: frozenset[str]
) -> pd.DataFrame:
    string_widths = {
        "ANO_CMPT": 4, "MES_CMPT": 2, "CNES": 7, "MUNIC_RES": 6,
        "MUNIC_MOV": 6, "PROC_REA": 10, "CAR_INT": 2,
    }
    for col, width in string_widths.items():
        df[col] = df[col].astype(str).str.strip().str.zfill(width)
    df["IDENT"] = df["IDENT"].astype(str).str.strip()
    for col in ["DT_INTER", "DT_SAIDA"]:
        df[col] = df[col].astype(str).str.strip().str.zfill(8)
    for col in ["DIAS_PERM", "MORTE", "VAL_TOT"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df["competencia_processamento"] = df["ANO_CMPT"] + df["MES_CMPT"]
    df["is_inicial"] = df["IDENT"].eq("1")
    df["is_continuidade"] = df["IDENT"].eq("5")
    df["is_ident_outro"] = ~(df["is_inicial"] | df["is_continuidade"])
    df["is_eletiva"] = df["CAR_INT"].eq("01")
    df["is_urgencia"] = df["CAR_INT"].eq("02")
    df["is_grupo04_vigente"] = df["PROC_REA"].isin(active_codes)
    df["is_cirurgica_inicial"] = df["is_grupo04_vigente"] & df["is_inicial"]
    df["is_cirurgica_eletiva"] = df["is_cirurgica_inicial"] & df["is_eletiva"]
    df["is_cirurgica_urgencia"] = df["is_cirurgica_inicial"] & df["is_urgencia"]
    df["dt_inter_valida"] = pd.to_datetime(
        df["DT_INTER"], format="%Y%m%d", errors="coerce"
    )
    df["dt_saida_valida"] = pd.to_datetime(
        df["DT_SAIDA"], format="%Y%m%d", errors="coerce"
    )
    if not df["competencia_processamento"].eq(competencia).all():
        raise ValueError(f"Competência interna divergente em {competencia}")
    return df


def process_single_file(
    uf: str,
    competencia: str,
    target_cnes: frozenset[str],
    target_ibge: frozenset[str],
    active_codes: frozenset[str],
    temp_dir: Path,
    tracker: PeakDiskTracker,
) -> dict:
    filename = f"RD{uf}{competencia[2:4]}{competencia[4:6]}.dbc"
    dbc = temp_dir / f"{filename}_{uuid.uuid4().hex[:8]}.dbc"
    dbf = temp_dir / f"{filename}_{uuid.uuid4().hex[:8]}.dbf"
    result = {"cnes": [], "muni": [], "res": [], "manifest": None, "bytes": 0}
    acquired_at = datetime.now(timezone.utc).isoformat()
    try:
        source = download_datasus_dbc(filename, str(dbc))
        tracker.register(dbc)
        result["bytes"] = source["size_bytes"]
        decompress_dbc_to_dbf(str(dbc), str(dbf))
        tracker.register(dbf)
        columns = [
            "UF_ZI", "ANO_CMPT", "MES_CMPT", "CNES", "MUNIC_RES", "MUNIC_MOV",
            "PROC_REA", "CAR_INT", "IDENT", "DT_INTER", "DT_SAIDA", "DIAS_PERM",
            "MORTE", "VAL_TOT",
        ]
        raw = fast_read_dbf_cols(
            str(dbf), target_cols=columns, encoding="iso-8859-1"
        )
        df = _normalise_sih(raw, competencia, active_codes)

        cnes_target = df[df["CNES"].isin(target_cnes)]
        for cnes, group in cnes_target.groupby("CNES", sort=False):
            elective = group[group["is_cirurgica_eletiva"]]
            result["cnes"].append({
                "cnes": cnes,
                "competencia": competencia,
                "uf": uf,
                "n_aih_total_cnes": len(group),
                "n_aih_inicial_total_cnes": int(group["is_inicial"].sum()),
                "n_aih_continuidade_cnes": int(group["is_continuidade"].sum()),
                "n_cirurgias_candidatas_iniciais_cnes": int(group["is_cirurgica_inicial"].sum()),
                "n_cirurgias_eletivas_cnes": int(group["is_cirurgica_eletiva"].sum()),
                "n_cirurgias_urgencia_cnes": int(group["is_cirurgica_urgencia"].sum()),
                "dias_perm_cirurgica_eletiva": float(elective["DIAS_PERM"].sum()),
                "obitos_cirurgicos_eletivos": int(elective["MORTE"].sum()),
                "val_tot_cirurgico_eletivo": float(elective["VAL_TOT"].sum()),
            })

        occurrence_target = df[df["MUNIC_MOV"].isin(target_ibge)]
        for ibge, group in occurrence_target.groupby("MUNIC_MOV", sort=False):
            result["muni"].append({
                "ibge": ibge,
                "competencia": competencia,
                "uf": uf,
                "n_aih_total_ocorrencia": len(group),
                "n_aih_inicial_total_ocorrencia": int(group["is_inicial"].sum()),
                "n_aih_continuidade_ocorrencia": int(group["is_continuidade"].sum()),
                "n_cirurgias_candidatas_iniciais_ocorrencia": int(group["is_cirurgica_inicial"].sum()),
                "n_cirurgias_eletivas_ocorrencia": int(group["is_cirurgica_eletiva"].sum()),
                "n_cirurgias_urgencia_ocorrencia": int(group["is_cirurgica_urgencia"].sum()),
            })

        residence_target = df[df["MUNIC_RES"].isin(target_ibge)]
        for ibge, group in residence_target.groupby("MUNIC_RES", sort=False):
            elective = group[group["is_cirurgica_eletiva"]]
            local = elective["MUNIC_MOV"].eq(ibge)
            same_uf = elective["MUNIC_MOV"].str[:2].eq(str(ibge)[:2])
            result["res"].append({
                "ibge": ibge,
                "competencia": competencia,
                "uf_destino_arquivo": uf,
                "n_cirurgias_eletivas_res_local": int(local.sum()),
                "n_cirurgias_eletivas_res_outro_muni_mesma_uf": int((~local & same_uf).sum()),
                "n_cirurgias_eletivas_res_outra_uf": int((~same_uf).sum()),
                "n_cirurgias_eletivas_res_fora": int((~local).sum()),
                "n_cirurgias_eletivas_res_total": len(elective),
            })

        result["manifest"] = {
            "arquivo": filename,
            "source_url": source["source_url"],
            "uf": uf,
            "competencia": competencia,
            "size_bytes": source["size_bytes"],
            "sha256": source["sha256"],
            "adquirido_em_utc": acquired_at,
            "linhas_lidas": len(df),
            "linhas_aih_inicial": int(df["is_inicial"].sum()),
            "linhas_aih_continuidade": int(df["is_continuidade"].sum()),
            "linhas_ident_outro": int(df["is_ident_outro"].sum()),
            "linhas_grupo04_vigente_inicial": int(df["is_cirurgica_inicial"].sum()),
            "linhas_grupo04_eletiva_inicial": int(df["is_cirurgica_eletiva"].sum()),
            "linhas_grupo04_urgencia_inicial": int(df["is_cirurgica_urgencia"].sum()),
            "linhas_cnes_alvo": len(cnes_target),
            "linhas_ocorrencia_muni_alvo": len(occurrence_target),
            "linhas_residencia_muni_alvo": len(residence_target),
            "datas_internacao_invalidas": int(df["dt_inter_valida"].isna().sum()),
            "datas_saida_invalidas": int(df["dt_saida_valida"].isna().sum()),
            "data_internacao_min": (
                df["dt_inter_valida"].min().strftime("%Y-%m-%d")
                if df["dt_inter_valida"].notna().any() else ""
            ),
            "data_internacao_max": (
                df["dt_inter_valida"].max().strftime("%Y-%m-%d")
                if df["dt_inter_valida"].notna().any() else ""
            ),
            "data_saida_min": (
                df["dt_saida_valida"].min().strftime("%Y-%m-%d")
                if df["dt_saida_valida"].notna().any() else ""
            ),
            "data_saida_max": (
                df["dt_saida_valida"].max().strftime("%Y-%m-%d")
                if df["dt_saida_valida"].notna().any() else ""
            ),
            "status": "SUCCESS",
        }
    except Exception as exc:  # pragma: no cover - network-dependent
        result["manifest"] = {
            "arquivo": filename,
            "source_url": f"ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados/{filename}",
            "uf": uf,
            "competencia": competencia,
            "adquirido_em_utc": acquired_at,
            "status": f"ERROR: {str(exc).strip()}",
        }
    finally:
        for path in [dbf, dbc]:
            tracker.unregister(path)
            path.unlink(missing_ok=True)
    return result


def _write_reproducible_parquet(
    df: pd.DataFrame, path: Path, sort_by: list[str], temp_dir: Path
) -> str:
    ordered = df.sort_values(sort_by, kind="stable").reset_index(drop=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered.to_parquet(path, index=False, engine="pyarrow", compression="zstd")
    check = temp_dir / f"repro_{path.name}"
    ordered.to_parquet(check, index=False, engine="pyarrow", compression="zstd")
    first = compute_sha256(str(path))
    second = compute_sha256(str(check))
    check.unlink()
    if first != second:
        raise AssertionError(f"Parquet não reproduzível: {path.name}")
    return first


def _build_panels(
    df_anes: pd.DataFrame,
    cnes_records: list[dict],
    muni_records: list[dict],
    residence_records: list[dict],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    target_cnes = sorted(df_anes["cnes"].astype(str).str.zfill(7).unique())
    target_ibge = sorted(df_anes["ibge"].astype(str).str.zfill(6).unique())

    cnes_values = pd.DataFrame(cnes_records)
    cnes_grid = pd.MultiIndex.from_product(
        [target_cnes, COMPETENCIAS], names=["cnes", "competencia"]
    ).to_frame(index=False)
    cnes_meta = df_anes[[
        "cnes", "ibge", "uf", "classificacao_braco", "amostra_anestesia_total",
        "amostra_anestesia_isolada", "cointervencao_cirurgica_muni",
    ]].drop_duplicates("cnes")
    cnes_grid = cnes_grid.merge(
        cnes_meta, on="cnes", how="left", validate="many_to_one"
    )
    cnes_panel = cnes_grid.merge(
        cnes_values, on=["cnes", "competencia", "uf"], how="left", validate="one_to_one"
    )
    cnes_numeric = [
        col for col in cnes_values.columns if col not in {"cnes", "competencia", "uf"}
    ]
    cnes_panel[cnes_numeric] = cnes_panel[cnes_numeric].fillna(0)

    muni_values = pd.DataFrame(muni_records)
    residence_raw = pd.DataFrame(residence_records)
    residence_numeric = [
        "n_cirurgias_eletivas_res_local",
        "n_cirurgias_eletivas_res_outro_muni_mesma_uf",
        "n_cirurgias_eletivas_res_outra_uf",
        "n_cirurgias_eletivas_res_fora",
        "n_cirurgias_eletivas_res_total",
    ]
    residence = residence_raw.groupby(
        ["ibge", "competencia"], as_index=False
    )[residence_numeric].sum()
    dest_counts = (
        residence_raw[residence_raw["n_cirurgias_eletivas_res_total"] > 0]
        .groupby(["ibge", "competencia"])["uf_destino_arquivo"]
        .nunique()
        .rename("n_ufs_destino_eletivas")
        .reset_index()
    )
    residence = residence.merge(
        dest_counts, on=["ibge", "competencia"], how="left"
    )
    residence["n_ufs_destino_eletivas"] = (
        residence["n_ufs_destino_eletivas"].fillna(0).astype(int)
    )

    muni_meta = construir_meta_municipal(df_anes)
    muni_grid = pd.MultiIndex.from_product(
        [target_ibge, COMPETENCIAS], names=["ibge", "competencia"]
    ).to_frame(index=False)
    muni_grid = muni_grid.merge(
        muni_meta, on="ibge", how="left", validate="many_to_one"
    )
    muni_panel = (
        muni_grid.merge(
            muni_values,
            on=["ibge", "competencia", "uf"],
            how="left",
            validate="one_to_one",
        )
        .merge(
            residence,
            on=["ibge", "competencia"],
            how="left",
            validate="one_to_one",
        )
    )
    muni_numeric = [
        col for col in muni_panel.columns
        if col.startswith("n_aih_") or col.startswith("n_cirurgias_")
    ] + ["n_ufs_destino_eletivas"]
    muni_panel[muni_numeric] = muni_panel[muni_numeric].fillna(0)
    muni_panel["taxa_resolutividade_cirurgica"] = np.where(
        muni_panel["n_cirurgias_eletivas_res_total"] > 0,
        muni_panel["n_cirurgias_eletivas_res_local"]
        / muni_panel["n_cirurgias_eletivas_res_total"],
        np.nan,
    )
    return cnes_panel, muni_panel, muni_meta


def _validate(
    file_manifest: pd.DataFrame,
    sigtap_manifest: pd.DataFrame,
    cnes_panel: pd.DataFrame,
    muni_panel: pd.DataFrame,
    muni_meta: pd.DataFrame,
) -> dict:
    if len(file_manifest) != 675 or file_manifest[["uf", "competencia"]].duplicated().any():
        raise AssertionError("Manifesto SIH deve ter 675 pares UF--competência únicos")
    if not file_manifest["status"].eq("SUCCESS").all():
        raise AssertionError("Nem todos os 675 arquivos SIH tiveram sucesso")
    if file_manifest["sha256"].fillna("").str.len().ne(64).any():
        raise AssertionError("Hash SIH ausente ou inválido")
    if not sigtap_manifest["status"].eq("SUCCESS").all():
        raise AssertionError("SIGTAP incompleto")
    if cnes_panel[["cnes", "competencia"]].duplicated().any():
        raise AssertionError("Painel CNES duplicado")
    if muni_panel[["ibge", "competencia"]].duplicated().any():
        raise AssertionError("Painel municipal duplicado")
    if not cnes_panel.groupby("cnes")["competencia"].nunique().eq(25).all():
        raise AssertionError("CNES sem 25 competências")
    if not muni_panel.groupby("ibge")["competencia"].nunique().eq(25).all():
        raise AssertionError("Município sem 25 competências")
    if (
        (cnes_panel["competencia"] >= T0_PROVISORIO).any()
        or (muni_panel["competencia"] >= T0_PROVISORIO).any()
    ):
        raise AssertionError("Competência pós-T0 encontrada")
    flow = (
        muni_panel["n_cirurgias_eletivas_res_local"]
        + muni_panel["n_cirurgias_eletivas_res_fora"]
    )
    if not flow.eq(muni_panel["n_cirurgias_eletivas_res_total"]).all():
        raise AssertionError("Fluxo residência local + fora != total")
    outside = (
        muni_panel["n_cirurgias_eletivas_res_outro_muni_mesma_uf"]
        + muni_panel["n_cirurgias_eletivas_res_outra_uf"]
    )
    if not outside.eq(muni_panel["n_cirurgias_eletivas_res_fora"]).all():
        raise AssertionError("Decomposição intra/inter-UF inconsistente")
    identity = (
        file_manifest["linhas_aih_inicial"]
        + file_manifest["linhas_aih_continuidade"]
        + file_manifest["linhas_ident_outro"]
    )
    if not identity.eq(file_manifest["linhas_lidas"]).all():
        raise AssertionError("Linhas por IDENT não reconciliam")

    counts = muni_meta["classificacao_braco"].value_counts().to_dict()
    if counts.get("imediata_pura") != 77 or counts.get("nao_priorizada_pura") != 247:
        raise AssertionError(f"Braços municipais inesperados: {counts}")
    overlap = int(
        muni_meta["bracos_anestesia_no_municipio"]
        .eq("imediata_pura|reserva_pura")
        .sum()
    )
    if overlap != 1:
        raise AssertionError(
            f"Esperado um município imediata+reserva; observado {overlap}"
        )
    contaminated = muni_meta[
        muni_meta["bracos_anestesia_no_municipio"].eq(
            "imediata_pura|reserva_pura"
        )
    ]
    if contaminated["amostra_anestesia_total"].any():
        raise AssertionError("Município imediata+reserva entrou como puro")
    return {
        "arquivos_sih": len(file_manifest),
        "ufs": int(file_manifest["uf"].nunique()),
        "competencias": int(file_manifest["competencia"].nunique()),
        "linhas_sih_lidas": int(file_manifest["linhas_lidas"].sum()),
        "municipios_imediata_pura": counts.get("imediata_pura", 0),
        "municipios_nao_priorizada_pura": counts.get("nao_priorizada_pura", 0),
        "municipios_excluidos": counts.get("excluida_reserva_mista", 0),
        "municipios_imediata_e_reserva": overlap,
        "painel_cnes_linhas": len(cnes_panel),
        "painel_municipio_linhas": len(muni_panel),
    }


def _write_report(manifest: dict) -> None:
    metrics = manifest["validacoes"]
    traffic = manifest["trafego"]
    disk = manifest["armazenamento_temporario"]
    hashes = manifest["arquivos_gerados_hashes"]
    content = f"""# Auditoria do SIH pré-tratamento — Anestesiologia (C3-02B)

> **Execução:** {manifest['data_execucao']}<br>
> **Status:** aprovado para C3-03 exclusivamente pré-tratamento<br>
> **Janela:** 2024-06 a 2026-06; 2026-07/08 não foram solicitadas e podem ter defasagem de publicação

## Resultado do corretivo

Foram processados **{metrics['arquivos_sih']} arquivos** ({metrics['ufs']} UFs ×
{metrics['competencias']} competências), todos com URL, tamanho, SHA-256, horário,
linhas e status em `output/avaliacao_ciclo3/manifesto_arquivos_sih_pre.csv`.
Nenhuma competência igual ou posterior ao T0 provisório (`2026-09`) foi lida.

O tráfego SIH dos 675 arquivos foi **{traffic['sih_675_mib']:.2f} MiB**. O
benchmark repetido consumiu {traffic['benchmark_mib']:.2f} MiB e as 25 versões
SIGTAP consumiram {traffic['sigtap_mib']:.2f} MiB; tráfego real total:
**{traffic['total_real_mib']:.2f} MiB**. O pico observado a cada 10 ms foi
**{disk['pico_mib']:.2f} MiB**, com DBC/DBF/ZIP apagados ao final.

## Braço municipal corrigido

- imediata pura: **{metrics['municipios_imediata_pura']}**;
- não priorizada pura: **{metrics['municipios_nao_priorizada_pura']}**;
- excluídos por reserva/mistura: **{metrics['municipios_excluidos']}**;
- imediata + reserva, obrigatoriamente excluído: **{metrics['municipios_imediata_e_reserva']}**.

A regra usa todas as células locais. Não há `drop_duplicates` para escolher um
braço municipal.

## SIGTAP e definição do candidato

As 25 tabelas mensais oficiais foram obtidas do
[FTP DATASUS](ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/). O arquivo
`dicionario_procedimentos_anestesia.csv` contém uma linha por
competência--procedimento vigente do grupo 04 e a proveniência do ZIP. O
manifesto mensal está em `manifesto_sigtap_pre.csv`.

O outcome continua chamado **candidato amplo de AIH cirúrgica eletiva**. Grupo
04 não prova sensibilidade específica a anestesiologia. Só AIH inicial
(`IDENT=1`) conta como nova cirurgia; continuidade (`IDENT=5`) fica separada.
Caráter eletivo (`01`) e urgência (`02`), competência de processamento, data de
internação e data de saída foram auditados separadamente. Zeros à esquerda foram
preservados.

## Reconciliação e produtos

- linhas SIH lidas: **{metrics['linhas_sih_lidas']:,}**;
- painel CNES--competência: **{metrics['painel_cnes_linhas']:,}** linhas;
- painel município--competência: **{metrics['painel_municipio_linhas']:,}** linhas;
- cada unidade possui exatamente 25 competências;
- residência usa destinos nas 27 UFs e satisfaz `local + fora = total`;
- hashes Parquet reproduzidos por duas gravações idênticas.

Hashes principais:

- painel CNES: `{hashes['painel_sih_cnes_pre.parquet']}`;
- painel municipal: `{hashes['painel_sih_muni_pre.parquet']}`;
- dicionário SIGTAP: `{hashes['dicionario_procedimentos_anestesia.csv']}`.

## Portão

O C3-02B libera somente o C3-03 pré-tratamento. Não há efeito estimado, outcome
pós-tratamento ou protocolo clínico promovido a confirmatório nesta etapa. O
C3-05 continua bloqueado até seis meses comuns maduros e publicados.
"""
    DOC.write_text(content, encoding="utf-8")


def run_benchmark(
    temp_dir: Path, tracker: PeakDiskTracker, active_codes: frozenset[str]
) -> dict:
    start = time.perf_counter()
    result = process_single_file(
        "GO", "202501", frozenset(), frozenset(), active_codes, temp_dir, tracker
    )
    elapsed = time.perf_counter() - start
    if result["manifest"]["status"] != "SUCCESS":
        raise RuntimeError(result["manifest"]["status"])
    return {
        "arquivo": result["manifest"]["arquivo"],
        "size_bytes": result["bytes"],
        "tempo_total_s": round(elapsed, 3),
        "linhas_lidas": result["manifest"]["linhas_lidas"],
        "sha256": result["manifest"]["sha256"],
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    SIH_OUTPUT.mkdir(parents=True, exist_ok=True)
    if max(COMPETENCIAS) >= T0_PROVISORIO:
        raise AssertionError("Janela C3-02B alcança T0")
    if set(SIGTAP_FILES) != set(COMPETENCIAS):
        raise AssertionError("Mapa SIGTAP não cobre exatamente as 25 competências")

    cohort = pd.read_parquet(COHORT)
    df_anes = cohort[cohort["cod_curso"].eq(1)].copy()
    df_anes["cnes"] = df_anes["cnes"].astype(str).str.zfill(7)
    df_anes["ibge"] = df_anes["ibge"].astype(str).str.zfill(6)
    target_cnes = frozenset(df_anes["cnes"])
    target_ibge = frozenset(df_anes["ibge"])
    tracker = PeakDiskTracker()

    print("C3-02B: SIGTAP mensal + 27 UFs x 25 competências", flush=True)
    with tempfile.TemporaryDirectory(prefix="pmme_c3_02b_") as tmp:
        temp_dir = Path(tmp)
        monitor = DirectoryPeakMonitor(temp_dir)
        monitor.start()
        try:
            print("[1/5] Historicizando 25 competências SIGTAP...", flush=True)
            dictionary, sigtap_manifest, codes_by_month, sigtap_bytes = acquire_sigtap(
                temp_dir, tracker
            )
            _persist_sigtap(dictionary, sigtap_manifest)

            remote_catalog = _sih_remote_catalog()
            missing_remote = sorted(
                filename
                for filename in _required_sih_files().values()
                if filename not in remote_catalog
            )
            if missing_remote:
                raise RuntimeError(
                    "Catálogo SIH oficial incompleto antes da aquisição: "
                    + ", ".join(missing_remote)
                )

            print("[2/5] Benchmark medido GO 2025-01...", flush=True)
            benchmark = run_benchmark(
                temp_dir, tracker, codes_by_month["202501"]
            )

            print("[3/5] Processando 675 arquivos SIH/RD...", flush=True)
            tasks = [(uf, comp) for uf in UFS_BRASIL for comp in COMPETENCIAS]
            cnes_records: list[dict] = []
            muni_records: list[dict] = []
            residence_records: list[dict] = []
            file_manifests: list[dict] = []
            sih_bytes = 0
            started = time.perf_counter()
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(
                        process_single_file,
                        uf,
                        comp,
                        target_cnes,
                        target_ibge,
                        codes_by_month[comp],
                        temp_dir,
                        tracker,
                    ): (uf, comp)
                    for uf, comp in tasks
                }
                for completed, future in enumerate(as_completed(futures), start=1):
                    result = future.result()
                    cnes_records.extend(result["cnes"])
                    muni_records.extend(result["muni"])
                    residence_records.extend(result["res"])
                    file_manifests.append(result["manifest"])
                    sih_bytes += result["bytes"]
                    if completed % 25 == 0 or completed == 675:
                        elapsed = time.perf_counter() - started
                        print(
                            f"  {completed}/675 ({completed / elapsed:.2f} arquivos/s)",
                            flush=True,
                        )

            file_manifest = pd.DataFrame(file_manifests).sort_values(
                ["competencia", "uf"], kind="stable"
            ).reset_index(drop=True)
            file_manifest_path = OUTPUT / "manifesto_arquivos_sih_pre.csv"
            file_manifest.to_csv(
                file_manifest_path,
                index=False,
                encoding="utf-8",
                lineterminator="\n",
            )
            if (
                len(file_manifest) != 675
                or not file_manifest["status"].eq("SUCCESS").all()
            ):
                raise RuntimeError(
                    "Aquisição SIH incompleta; painéis não serão balanceados"
                )

            print("[4/5] Construindo e validando painéis...", flush=True)
            cnes_panel, muni_panel, muni_meta = _build_panels(
                df_anes, cnes_records, muni_records, residence_records
            )
            validation = _validate(
                file_manifest,
                sigtap_manifest,
                cnes_panel,
                muni_panel,
                muni_meta,
            )

            cnes_path = SIH_OUTPUT / "painel_sih_cnes_pre.parquet"
            muni_path = SIH_OUTPUT / "painel_sih_muni_pre.parquet"
            cnes_hash = _write_reproducible_parquet(
                cnes_panel, cnes_path, ["cnes", "competencia"], temp_dir
            )
            muni_hash = _write_reproducible_parquet(
                muni_panel, muni_path, ["ibge", "competencia"], temp_dir
            )

            dict_path, sigtap_manifest_path = _persist_sigtap(
                dictionary, sigtap_manifest
            )
            muni_meta_path = OUTPUT / "classificacao_municipal_anestesia.csv"
            muni_meta.to_csv(
                muni_meta_path,
                index=False,
                encoding="utf-8",
                lineterminator="\n",
            )

            monitor.stop()
            print("[5/5] Selando manifesto e auditoria...", flush=True)
            total_real = sih_bytes + benchmark["size_bytes"] + sigtap_bytes
            peak_bytes = max(monitor.peak_bytes, tracker.peak_bytes)
            peak_files = (
                monitor.peak_files
                if monitor.peak_bytes >= tracker.peak_bytes
                else tracker.peak_files
            )
            peak_at = (
                monitor.peak_at_utc
                if monitor.peak_bytes >= tracker.peak_bytes
                else tracker.peak_at_utc
            )
            manifest = {
                "protocolo": "C3-02B_SIH_PRE_TRATAMENTO_ANESTESIOLOGIA",
                "status_portao_c3_03": "APROVADO_EXCLUSIVAMENTE_PRE_TRATAMENTO",
                "data_execucao": datetime.now(timezone.utc).date().isoformat(),
                "t0_provisorio": T0_PROVISORIO,
                "janela_pre": {
                    "inicio": COMPETENCIAS[0],
                    "fim": COMPETENCIAS[-1],
                    "n_competencias": 25,
                },
                "observacao_disponibilidade": (
                    "2026-07/08 não solicitadas; podem ainda sofrer defasagem de "
                    "disseminação SIH"
                ),
                "ufs_processadas": UFS_BRASIL,
                "validacoes": validation,
                "benchmark": benchmark,
                "trafego": {
                    "sih_675_bytes": sih_bytes,
                    "sih_675_mib": round(sih_bytes / 2**20, 2),
                    "benchmark_bytes": benchmark["size_bytes"],
                    "benchmark_mib": round(benchmark["size_bytes"] / 2**20, 2),
                    "sigtap_bytes": sigtap_bytes,
                    "sigtap_mib": round(sigtap_bytes / 2**20, 2),
                    "total_real_bytes": total_real,
                    "total_real_mib": round(total_real / 2**20, 2),
                },
                "armazenamento_temporario": {
                    "metodo": (
                        "pico observado a cada 10 ms no diretório temporário, "
                        "com conferência nas transições controladas DBC/DBF/ZIP"
                    ),
                    "pico_bytes": peak_bytes,
                    "pico_mib": round(peak_bytes / 2**20, 2),
                    "arquivos_no_pico": peak_files,
                    "pico_em_utc": peak_at,
                    "temporarios_remanescentes_antes_da_remocao": len(
                        list(temp_dir.iterdir())
                    ),
                },
                "definicao_outcome": {
                    "nome": "candidato amplo de AIH cirúrgica eletiva",
                    "procedimento": (
                        "vigente no SIGTAP da competência e prefixo 04"
                    ),
                    "aih": "somente IDENT=1; IDENT=5 separado como continuidade",
                    "carater": (
                        "eletivo CAR_INT=01; urgência CAR_INT=02 separada"
                    ),
                    "status_clinico": "não específico a anestesiologia",
                },
                "arquivos_gerados_hashes": {
                    "painel_sih_cnes_pre.parquet": cnes_hash,
                    "painel_sih_muni_pre.parquet": muni_hash,
                    "manifesto_arquivos_sih_pre.csv": compute_sha256(
                        str(file_manifest_path)
                    ),
                    "dicionario_procedimentos_anestesia.csv": compute_sha256(
                        str(dict_path)
                    ),
                    "manifesto_sigtap_pre.csv": compute_sha256(
                        str(sigtap_manifest_path)
                    ),
                    "classificacao_municipal_anestesia.csv": compute_sha256(
                        str(muni_meta_path)
                    ),
                },
            }
            manifest_path = OUTPUT / "manifesto_sih_pre.json"
            manifest_path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            _write_report(manifest)
        finally:
            if monitor._thread.is_alive():
                monitor.stop()

    print("C3-02B aprovado. C3-03 pré-tratamento liberado.", flush=True)


def finalize_blocked_attempt() -> None:
    """Seal the audited failed attempt without fabricating structural zeros."""
    file_manifest_path = OUTPUT / "manifesto_arquivos_sih_pre.csv"
    file_manifest = pd.read_csv(file_manifest_path, dtype={"uf": str, "competencia": str})
    if len(file_manifest) != 675:
        raise AssertionError("Tentativa bloqueada não contém 675 linhas de manifesto")
    errors = file_manifest[~file_manifest["status"].eq("SUCCESS")].copy()
    expected_missing = {"RDAC2606.dbc", "RDRR2606.dbc"}
    if set(errors["arquivo"]) != expected_missing:
        raise AssertionError(f"Falhas inesperadas: {errors['arquivo'].tolist()}")

    dict_path = OUTPUT / "dicionario_procedimentos_anestesia.csv"
    sigtap_manifest_path = OUTPUT / "manifesto_sigtap_pre.csv"
    dictionary = pd.read_csv(
        dict_path,
        dtype={"competencia": str, "co_procedimento": str},
        low_memory=False,
    )
    sigtap_manifest = pd.read_csv(
        sigtap_manifest_path, dtype={"competencia": str}
    )
    if (
        sigtap_manifest["competencia"].nunique() != 25
        or not sigtap_manifest["status"].eq("SUCCESS").all()
    ):
        raise AssertionError("Historicização SIGTAP persistida está incompleta")
    sigtap_bytes = int(pd.to_numeric(sigtap_manifest["size_bytes"]).sum())

    catalog = _sih_remote_catalog()
    required = _required_sih_files()
    missing_catalog = sorted(filename for filename in required.values() if filename not in catalog)
    if set(missing_catalog) != expected_missing:
        raise AssertionError(f"Catálogo oficial mudou: {missing_catalog}")

    successful = file_manifest[file_manifest["status"].eq("SUCCESS")].copy()
    successful_bytes = int(pd.to_numeric(successful["size_bytes"]).sum())
    benchmark_bytes = int(
        pd.to_numeric(
            successful.loc[
                successful["arquivo"].eq("RDGO2501.dbc"), "size_bytes"
            ]
        ).iloc[0]
    )
    main_partial_bytes = successful_bytes + benchmark_bytes + sigtap_bytes
    old_cnes = SIH_OUTPUT / "painel_sih_cnes_pre.parquet"
    old_muni = SIH_OUTPUT / "painel_sih_muni_pre.parquet"
    checked_at = datetime.now(timezone.utc).isoformat()
    blocked = {
        "protocolo": "C3-02B_SIH_PRE_TRATAMENTO_ANESTESIOLOGIA",
        "status_portao_c3_03": "BLOQUEADO_FONTE_OFICIAL_INCOMPLETA",
        "data_execucao": datetime.now(timezone.utc).date().isoformat(),
        "t0_provisorio": T0_PROVISORIO,
        "janela_solicitada": {
            "inicio": COMPETENCIAS[0],
            "fim": COMPETENCIAS[-1],
            "n_competencias": 25,
            "ufs": 27,
            "arquivos_esperados": 675,
        },
        "resultado_tentativa": {
            "manifestos": len(file_manifest),
            "sucessos": len(successful),
            "falhas": len(errors),
            "arquivos_ausentes_no_catalogo_oficial": missing_catalog,
            "catalogo_consultado_em_utc": checked_at,
            "regra": "não criar zero estrutural; não construir painéis C3-02B",
        },
        "sigtap": {
            "status": "HISTORICIZADO_25_COMPETENCIAS",
            "competencias": int(sigtap_manifest["competencia"].nunique()),
            "linhas_grupo04_competencia_procedimento": len(dictionary),
        },
        "trafego_tentativa_principal": {
            "sih_673_sucessos_bytes": successful_bytes,
            "sih_673_sucessos_mib": round(successful_bytes / 2**20, 2),
            "benchmark_repetido_bytes": benchmark_bytes,
            "sigtap_25_bytes": sigtap_bytes,
            "total_parcial_bytes": main_partial_bytes,
            "total_parcial_mib": round(main_partial_bytes / 2**20, 2),
            "observacao": "falhas FTP 550 não transferiram arquivos; reaquisicao corretiva do SIGTAP não somada",
        },
        "armazenamento_temporario": {
            "pico_bytes": None,
            "status": "NAO_PERSISTIDO_APOS_FALHA_DO_PORTAO",
            "observacao": "o código agora persiste o estado bloqueado antes de nova execução; nenhum valor foi inferido",
        },
        "paineis_existentes": {
            "status": "PRELIMINARES_C3_02_NAO_APROVADOS_POR_C3_02B",
            "painel_sih_cnes_pre.parquet": compute_sha256(str(old_cnes)),
            "painel_sih_muni_pre.parquet": compute_sha256(str(old_muni)),
        },
        "arquivos_gerados_hashes": {
            "manifesto_arquivos_sih_pre.csv": compute_sha256(str(file_manifest_path)),
            "dicionario_procedimentos_anestesia.csv": compute_sha256(str(dict_path)),
            "manifesto_sigtap_pre.csv": compute_sha256(str(sigtap_manifest_path)),
        },
        "proxima_acao": "repetir C3-02B somente quando RDAC2606.dbc e RDRR2606.dbc aparecerem no FTP oficial",
        "c3_03": "BLOQUEADO",
        "estimacao_pos_tratamento": "PROIBIDA_ATE_SEIS_MESES_MADUROS",
    }
    (OUTPUT / "manifesto_sih_pre.json").write_text(
        json.dumps(blocked, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    report = f"""# Auditoria do SIH pré-tratamento — Anestesiologia (C3-02B)

> **Execução:** {blocked['data_execucao']}<br>
> **Status:** bloqueado por fonte oficial incompleta<br>
> **C3-03:** não executado

## Resultado

A execução tentou os **675 pares UF--competência** de 2024-06 a 2026-06.
Houve **673 sucessos**. O diretório oficial do SIH não contém
`RDAC2606.dbc` nem `RDRR2606.dbc`; a ausência foi confirmada por listagem do
[FTP DATASUS](ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados)
em {checked_at}. O cronograma previa disseminação aproximada de junho em
10/08/2026, mas o catálogo observado em 31/08/2026 ainda tinha só 25 UFs.

O manifesto `output/avaliacao_ciclo3/manifesto_arquivos_sih_pre.csv` tem uma
linha para cada um dos 675 pares, com 673 `SUCCESS` e duas falhas FTP 550.
Conforme o prompt, as duas ausências **não foram convertidas em zeros** e os
painéis corrigidos não foram construídos.

## Parte concluída

- as 25 competências mensais do SIGTAP foram historicizadas;
- o dicionário tem {len(dictionary):,} linhas competência--procedimento do grupo 04;
- a classificação municipal continua reconciliada em 77 tratados puros, 247
  controles puros e um município imediata+reserva excluído;
- tráfego parcial da tentativa principal: {main_partial_bytes / 2**20:.2f} MiB;
- o pico de disco não foi inferido: a medição morreu com o processo bloqueado e
  agora o código falha no pré-flight antes de repetir uma aquisição incompleta.

Os Parquets já existentes são produtos preliminares do C3-02 (24 UFs), não
produtos aprovados do C3-02B. Seus hashes ficam no manifesto apenas para impedir
que sejam confundidos com a correção.

## Portão

O C3-03 permanece bloqueado. Próxima ação: verificar novamente o FTP e executar
o C3-02B integral quando os dois arquivos forem publicados. Nenhum outcome
pós-tratamento foi consultado e nenhuma estimação foi feita. C3-05 continua
proibido até seis meses comuns maduros e publicados.
"""
    DOC.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    if "--finalize-blocked-attempt" in sys.argv:
        finalize_blocked_attempt()
    else:
        main()
