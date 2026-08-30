"""03_adquirir_cnes_mensal.py — Aquisição e Extração Eficiente do CNES Mensal (26 competências).

Este script realiza a aquisição resiliente, validação e extração streaming dos microdados
mensais do CNES (junho de 2024 a julho de 2026 = 26 competências) para avaliação causal do PMM-E.

Fontes e regras:
- Download paralelo e resiliente de `http://cnes.datasus.gov.br/EstatisticasServlet?path=BASE_DE_DADOS_CNES_AAAAMM.ZIP` para `data/raw/cnes/`.
- Idempotência com download temporário `.part` e teste de integridade do ZIP antes da persistência.
- Extração em streaming seletivo: lê diretamente do arquivo ZIP as tabelas `tbCargaHorariaSus` e `tbEstabelecimento`,
  filtrando todos os vínculos de médicos especialistas (famílias CBO 2251, 2252, 2253).
- Preserva todas as variáveis canônicas: CO_UNIDADE, CO_CNES, CO_PROFISSIONAL_SUS, CO_CBO, NU_REGISTRO (CRM),
  SG_UF_CRM, QT_CARGA_HORARIA_AMBULATORIAL, QT_CARGA_HOR_HOSP_SUS, QT_CARGA_HORARIA_OUTROS, TP_SUS_NAO_SUS, IND_VINCULACAO.
- Salva parquets intermediários em `output/aquisicao/cnes_mensal/` e a tabela consolidada
  `output/aquisicao/cnes_vinculos_medicos_2024_2026.parquet`.
- Gera o manifesto detalhado com hash SHA-256 em `output/aquisicao/manifesto_cnes_26_competencias.json`.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import json
import re
import sys
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
RAW_CNES_DIR = ROOT / "data" / "raw" / "cnes"
OUTPUT_DIR = ROOT / "output" / "aquisicao"
MONTHLY_PARQUET_DIR = OUTPUT_DIR / "cnes_mensal"
CONSOLIDATED_PARQUET = OUTPUT_DIR / "cnes_vinculos_medicos_2024_2026.parquet"
MANIFEST_FILE = OUTPUT_DIR / "manifesto_cnes_26_competencias.json"

BASE_URL = "http://cnes.datasus.gov.br/EstatisticasServlet?path="
CATALOG_REFERER = "https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp"

# 26 competências: 2024-06 a 2026-07
ALL_COMPETENCIAS = [
    f"{year}{month:02d}"
    for year, first, last in ((2024, 6, 12), (2025, 1, 12), (2026, 1, 7))
    for month in range(first, last + 1)
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(2 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def download_single_month(competencia: str, timeout: int = 900, max_retries: int = 4) -> Tuple[str, bool, Optional[str], Optional[int], Optional[str]]:
    filename = f"BASE_DE_DADOS_CNES_{competencia}.ZIP"
    destination = RAW_CNES_DIR / filename
    url = f"{BASE_URL}{filename}"

    if destination.exists():
        try:
            if zipfile.is_zipfile(destination):
                with zipfile.ZipFile(destination, "r") as zf:
                    if zf.testzip() is None:
                        file_hash = sha256_file(destination)
                        file_size = destination.stat().st_size
                        print(f"  [OK LOCAL] {filename} ({file_size / (1024*1024):.1f} MB, sha256: {file_hash[:12]}...)", flush=True)
                        return competencia, True, file_hash, file_size, None
        except Exception as e:
            print(f"  [AVISO] Arquivo existente {filename} corrompido: {e}. Rebaixando...", flush=True)

    temp_dest = destination.with_suffix(".zip.part")
    if temp_dest.exists():
        try:
            temp_dest.unlink()
        except Exception:
            pass

    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PMME-CNES-Acquisition/1.0",
            "Referer": CATALOG_REFERER,
            "Accept": "application/zip,*/*",
        },
    )

    for attempt in range(1, max_retries + 1):
        try:
            print(f"  -> Baixando {filename} (tentativa {attempt}/{max_retries})...", flush=True)
            t0 = time.time()
            digest = hashlib.sha256()
            total_bytes = 0

            with urllib.request.urlopen(req, timeout=timeout) as response:
                first_chunk = response.read(2)
                if first_chunk != b"PK":
                    raise RuntimeError(f"Resposta HTTP não é ZIP (magic bytes: {first_chunk!r})")

                with temp_dest.open("wb") as handle:
                    handle.write(first_chunk)
                    digest.update(first_chunk)
                    total_bytes += len(first_chunk)

                    last_log = time.time()
                    while True:
                        chunk = response.read(2 * 1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
                        digest.update(chunk)
                        total_bytes += len(chunk)

                        if time.time() - last_log >= 15:
                            elapsed = time.time() - t0
                            speed = total_bytes / (1024 * 1024 * elapsed) if elapsed > 0 else 0
                            print(f"     {filename}: {total_bytes / (1024*1024):.1f} MB ({speed:.2f} MB/s)", flush=True)
                            last_log = time.time()

            if not zipfile.is_zipfile(temp_dest):
                raise RuntimeError("Arquivo baixado não é ZIP íntegro.")

            with zipfile.ZipFile(temp_dest, "r") as zf:
                if zf.testzip() is not None:
                    raise RuntimeError("Teste de integridade do ZIP falhou.")

            if destination.exists():
                destination.unlink()
            temp_dest.replace(destination)

            elapsed = time.time() - t0
            file_hash = digest.hexdigest()
            print(f"  [CONCLUÍDO] {filename} em {elapsed:.1f}s ({total_bytes / (1024*1024):.1f} MB, sha256: {file_hash[:12]}...)", flush=True)
            return competencia, True, file_hash, total_bytes, None

        except Exception as exc:
            print(f"  [ERRO] Falha no download de {filename} (tentativa {attempt}): {exc}", flush=True)
            if temp_dest.exists():
                try:
                    temp_dest.unlink()
                except Exception:
                    pass
            if attempt == max_retries:
                return competencia, False, None, None, str(exc)
            time.sleep(4)

    return competencia, False, None, None, "Max retries excedido"


def extract_cnes_month(competencia: str, zip_path: Path) -> pd.DataFrame:
    """Extrai e filtra em streaming os microdados de vínculos médicos do CNES para um mês de forma veloz."""
    t0 = time.time()
    with zipfile.ZipFile(zip_path, "r") as zf:
        estab_files = [n for n in zf.namelist() if "tbEstabelecimento" in n and n.lower().endswith(".csv")]
        ch_files = [n for n in zf.namelist() if "tbCargaHoraria" in n and n.lower().endswith(".csv")]

        if not estab_files or not ch_files:
            raise RuntimeError(f"Tabelas essenciais ausentes no ZIP de {competencia}")

        # 1. Ler tbEstabelecimento (CO_UNIDADE -> CO_CNES, CO_MUNICIPIO_GESTOR, TP_UNIDADE, CO_NATUREZA_JUR, TP_GESTAO)
        with zf.open(estab_files[0], "r") as f:
            df_estab = pd.read_csv(
                f,
                sep=";",
                encoding="latin1",
                usecols=["CO_UNIDADE", "CO_CNES", "CO_MUNICIPIO_GESTOR", "TP_UNIDADE", "CO_NATUREZA_JUR", "TP_GESTAO"],
                dtype=str,
            )
        df_estab["CO_CNES"] = df_estab["CO_CNES"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(7)
        df_estab["CO_MUNICIPIO_GESTOR"] = df_estab["CO_MUNICIPIO_GESTOR"].astype(str).str.replace(r"\D", "", regex=True).str[:6]

        # 2. Ler tbCargaHorariaSus filtrando médicos (CBO 2251%, 2252%, 2253%)
        ch_chunks = []
        with zf.open(ch_files[0], "r") as f:
            for chunk in pd.read_csv(
                f,
                sep=";",
                encoding="latin1",
                chunksize=500000,
                dtype=str,
                usecols=[
                    "CO_UNIDADE",
                    "CO_PROFISSIONAL_SUS",
                    "CO_CBO",
                    "TP_SUS_NAO_SUS",
                    "IND_VINCULACAO",
                    "QT_CARGA_HORARIA_AMBULATORIAL",
                    "QT_CARGA_HOR_HOSP_SUS",
                    "QT_CARGA_HORARIA_OUTROS",
                    "NU_REGISTRO",
                    "SG_UF_CRM",
                ],
            ):
                cbo_col = chunk["CO_CBO"].astype(str).str.strip()
                mask_med = cbo_col.str.startswith(("2251", "2252", "2253"))
                ch_chunks.append(chunk[mask_med])

        df_ch = pd.concat(ch_chunks, ignore_index=True) if ch_chunks else pd.DataFrame()

    # Converter numéricos
    for col in ["QT_CARGA_HORARIA_AMBULATORIAL", "QT_CARGA_HOR_HOSP_SUS", "QT_CARGA_HORARIA_OUTROS"]:
        if col in df_ch.columns:
            df_ch[col] = pd.to_numeric(df_ch[col].astype(str).str.replace(",", "."), errors="coerce").fillna(0).astype(int)
        else:
            df_ch[col] = 0

    # Join com Estabelecimento
    df_merged = df_ch.merge(df_estab, on="CO_UNIDADE", how="left")
    df_merged["COMPETENCIA"] = competencia

    # Padronizar nomes de colunas
    df_final = pd.DataFrame({
        "competencia": df_merged["COMPETENCIA"],
        "co_unidade": df_merged["CO_UNIDADE"].astype(str),
        "co_cnes_7d": df_merged["CO_CNES"].astype(str),
        "co_profissional_sus": df_merged["CO_PROFISSIONAL_SUS"].astype(str),
        "co_cbo_6d": df_merged["CO_CBO"].astype(str).str.strip(),
        "nu_registro_crm": df_merged["NU_REGISTRO"].astype(str) if "NU_REGISTRO" in df_merged.columns else "",
        "sg_uf_crm": df_merged["SG_UF_CRM"].astype(str) if "SG_UF_CRM" in df_merged.columns else "",
        "qt_carga_horaria_ambulatorial": df_merged["QT_CARGA_HORARIA_AMBULATORIAL"],
        "qt_carga_hor_hosp_sus": df_merged["QT_CARGA_HOR_HOSP_SUS"],
        "qt_carga_horaria_outros": df_merged["QT_CARGA_HORARIA_OUTROS"],
        "tp_sus_nao_sus": df_merged["TP_SUS_NAO_SUS"].astype(str) if "TP_SUS_NAO_SUS" in df_merged.columns else "",
        "ind_vinculacao": df_merged["IND_VINCULACAO"].astype(str) if "IND_VINCULACAO" in df_merged.columns else "",
        "co_municipio_gestor": df_merged["CO_MUNICIPIO_GESTOR"].astype(str),
        "tp_unidade": df_merged["TP_UNIDADE"].astype(str),
        "co_natureza_jur": df_merged["CO_NATUREZA_JUR"].astype(str),
        "tp_gestao": df_merged["TP_GESTAO"].astype(str),
    })

    elapsed = time.time() - t0
    print(f"  [EXTRAÇÃO OK] {competencia}: {len(df_final):,} vínculos médicos em {elapsed:.1f}s", flush=True)
    return df_final


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force-download", action="store_true", help="Força novo download de todos os arquivos")
    parser.add_argument("--workers", type=int, default=3, help="Número de threads simultâneas para download")
    args = parser.parse_args()

    RAW_CNES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MONTHLY_PARQUET_DIR.mkdir(parents=True, exist_ok=True)

    print("=== [Subagente 2] Aquisição e Extração Resiliente do CNES (26 Competências) ===", flush=True)
    print(f"Período: {ALL_COMPETENCIAS[0]} a {ALL_COMPETENCIAS[-1]} (Total: {len(ALL_COMPETENCIAS)} meses)\n", flush=True)

    # 1. Download paralelo resiliente dos arquivos ausentes
    missing_competencias = [
        comp for comp in ALL_COMPETENCIAS
        if not (RAW_CNES_DIR / f"BASE_DE_DADOS_CNES_{comp}.ZIP").exists() or args.force_download
    ]

    download_results: Dict[str, Tuple[bool, Optional[str], Optional[int], Optional[str]]] = {}
    if missing_competencias:
        print(f"Iniciando download paralelo de {len(missing_competencias)} competências ausentes com {args.workers} workers...", flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(download_single_month, comp): comp for comp in missing_competencias}
            for fut in concurrent.futures.as_completed(futures):
                comp, ok, fhash, fsize, err = fut.result()
                download_results[comp] = (ok, fhash, fsize, err)
    else:
        print("Todas as 26 bases brutas já estão preservadas em data/raw/cnes/.", flush=True)

    # 2. Processar e extrair para Parquet mensal
    manifest_entries = []
    monthly_dfs = []

    for comp in ALL_COMPETENCIAS:
        zip_name = f"BASE_DE_DADOS_CNES_{comp}.ZIP"
        dest_zip = RAW_CNES_DIR / zip_name
        dest_parquet = MONTHLY_PARQUET_DIR / f"cnes_vinculos_medicos_{comp}.parquet"

        if not dest_zip.exists():
            print(f"  [PULANDO] Arquivo bruto {zip_name} ausente.", flush=True)
            manifest_entries.append({
                "competencia": comp,
                "arquivo": zip_name,
                "status": "arquivo_ausente",
                "sha256": None,
                "bytes": None,
            })
            continue

        if dest_parquet.exists() and not args.force_download:
            print(f"  [OK CACHE] Parquet mensal já existe: {dest_parquet.name}", flush=True)
            df_m = pd.read_parquet(dest_parquet)
        else:
            df_m = extract_cnes_month(comp, dest_zip)
            df_m.to_parquet(dest_parquet, index=False)

        monthly_dfs.append(dest_parquet)

        manifest_entries.append({
            "competencia": comp,
            "arquivo": zip_name,
            "caminho_zip": dest_zip.relative_to(ROOT).as_posix(),
            "bytes_zip": dest_zip.stat().st_size,
            "sha256_zip": sha256_file(dest_zip),
            "status": "adquirido_e_extraido",
            "caminho_parquet": dest_parquet.relative_to(ROOT).as_posix(),
            "linhas_vinculos_medicos": len(df_m),
            "profissionais_distintos": int(df_m["co_profissional_sus"].nunique()),
            "estabelecimentos_distintos": int(df_m["co_cnes_7d"].nunique()),
            "data_processamento": datetime.date.today().isoformat(),
        })

    # 3. Consolidar todos os 26 parquets mensais em um único painel nacional
    print("\nConsolidando painel nacional de vínculos médicos...", flush=True)
    tables = [pq.read_table(p) for p in monthly_dfs]
    if tables:
        consolidated_table = pa.concat_tables(tables)
        pq.write_table(consolidated_table, CONSOLIDATED_PARQUET)
        print(f"[OK] Painel consolidado gravado em: {CONSOLIDATED_PARQUET}", flush=True)
        print(f"     Total de vínculos médicos no período: {consolidated_table.num_rows:,}", flush=True)
    else:
        print("[ERRO] Nenhuma tabela mensal foi processada.", flush=True)

    # 4. Salvar manifesto JSON
    with MANIFEST_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "subagente": "Subagente 2 — CNES Mensal",
                "data_execucao": datetime.date.today().isoformat(),
                "periodo_planejado": "2024-06 a 2026-07",
                "total_competencias_planejadas": len(ALL_COMPETENCIAS),
                "total_competencias_processadas": len(monthly_dfs),
                "arquivo_consolidado": CONSOLIDATED_PARQUET.relative_to(ROOT).as_posix(),
                "manifesto_mensal": manifest_entries,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
        f.write("\n")

    print(f"[OK] Manifesto do CNES gravado em: {MANIFEST_FILE}", flush=True)


if __name__ == "__main__":
    main()
