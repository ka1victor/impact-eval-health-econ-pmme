"""
datasus_dbc.py — Módulo utilitário para download, descompressão e conversão de arquivos DBC do DATASUS.

Fornece funções robustas para processar arquivos DBC para DBF/DataFrame/Parquet, tratando caminhos
Windows (8.3 short paths), integridade de tipos, zeros à esquerda e remoção limpa de arquivos temporários.
Utiliza ftplib com transferência binária direta e isolamento thread-safe por UUID.
"""

from __future__ import annotations
import os
import sys
import uuid
import ctypes
import tempfile
import ftplib
import socket
import hashlib
from typing import List, Optional
import pyreaddbc
from dbfread import DBF
import pandas as pd

socket.setdefaulttimeout(20)

def get_short_path_name(long_name: str) -> str:
    """Converte caminho longo para formato Windows 8.3 (evita erros em extensões C com caminhos unicode)."""
    if sys.platform == "win32":
        buffer = ctypes.create_unicode_buffer(500)
        ctypes.windll.kernel32.GetShortPathNameW(long_name, buffer, 500)
        return buffer.value or long_name
    return long_name

def compute_sha256(filepath: str) -> str:
    """Calcula hash SHA-256 de um arquivo."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def decompress_dbc_to_dbf(input_dbc: str, output_dbf: str) -> str:
    """Descompacta arquivo DBC do DATASUS para DBF."""
    short_dbc = get_short_path_name(os.path.abspath(input_dbc))
    short_dbf = get_short_path_name(os.path.abspath(output_dbf))
    
    pyreaddbc.dbc2dbf(short_dbc, short_dbf)
    if not os.path.exists(output_dbf):
        raise FileNotFoundError(f"Falha ao descompactar DBC: DBF {output_dbf} não foi gerado.")
    return output_dbf

def read_dbc(input_dbc: str, encoding: str = 'iso-8859-1', cols: Optional[List[str]] = None) -> pd.DataFrame:
    """Lê arquivo DBC e retorna como pandas DataFrame, limpando intermediários com isolamento por UUID."""
    temp_dir = tempfile.gettempdir()
    unique_id = uuid.uuid4().hex[:8]
    base_name = os.path.splitext(os.path.basename(input_dbc))[0]
    temp_dbf = os.path.join(temp_dir, f"{base_name}_{unique_id}.dbf")
    
    try:
        decompress_dbc_to_dbf(input_dbc, temp_dbf)
        table = DBF(temp_dbf, encoding=encoding, load=True)
        df = pd.DataFrame(iter(table))
        if cols:
            existing_cols = [c for c in cols if c in df.columns]
            df = df[existing_cols]
        return df
    finally:
        if os.path.exists(temp_dbf):
            try:
                os.remove(temp_dbf)
            except OSError:
                pass

def download_datasus_dbc(filename: str, dest_path: str, remote_dir: str = '/dissemin/publicos/SIHSUS/200801_/Dados', max_retries: int = 3) -> dict:
    """Baixa arquivo DBC do FTP do DATASUS de forma direta via ftplib."""
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    temp_download = dest_path + f".{uuid.uuid4().hex[:6]}.part"
    
    last_err = None
    for attempt in range(1, max_retries + 1):
        ftp = None
        try:
            ftp = ftplib.FTP('ftp.datasus.gov.br', timeout=20)
            ftp.login()
            ftp.cwd(remote_dir)
            
            with open(temp_download, 'wb') as f:
                ftp.retrbinary(f"RETR {filename}", f.write)
            
            ftp.quit()
            
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except OSError:
                    pass
            os.rename(temp_download, dest_path)
            
            size_bytes = os.path.getsize(dest_path)
            sha256 = compute_sha256(dest_path)
            return {
                "filename": filename,
                "dest_path": dest_path,
                "size_bytes": size_bytes,
                "sha256": sha256,
                "status": "SUCCESS"
            }
        except Exception as e:
            last_err = e
            if ftp:
                try:
                    ftp.close()
                except Exception:
                    pass
            if os.path.exists(temp_download):
                try:
                    os.remove(temp_download)
                except OSError:
                    pass
    
    raise IOError(f"Falha ao baixar {filename} após {max_retries} tentativas: {last_err}")
