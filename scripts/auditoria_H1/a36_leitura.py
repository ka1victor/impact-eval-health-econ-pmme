"""Leitura independente dos arquivos brutos do PMM-E para a auditoria 36 (H1).

Não importa nenhum script de `scripts/rdd_bolsa/` nem de `scripts/aquisicao/`.
Só lê `data/raw/` (sem escrever) e `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`.
Nenhuma função devolve nome ou CPF: as colunas pessoais são descartadas na leitura.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw"
V = RAW / "aquisicao" / "vagas"
P = RAW / "pmm_e"

ARQ = {
    # ciclo 1
    "c1_quadro": V / "2025_ciclo1_chamada1_vagas.xlsx",
    "c1_aloc": V / "2025_ciclo1_chamada1_alocacao_retificada.xlsx",
    "c1_aloc_sj": V / "2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx",
    "c1_realoc": V / "2025_ciclo1_chamada1_realocacao_retificado.xlsx",
    "c1_homol": P / "2025_ciclo1_chamada1_homologados.xlsx",
    "c1_ch2_quadro_aloc": P / "2025_ciclo1_chamada2_vagas_e_alocados.xlsx",
    "c1_ch2_homol": P / "2025_ciclo1_chamada2_homologados.xlsx",
    # ciclo 2
    "c2_quadro_orig": V / "2026_ciclo2_chamada1_vagas_e_servicos_original.xlsx",
    "c2_quadro_ret1": V / "2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx",
    "c2_quadro_ret2": P / "2026_ciclo2_chamada1_vagas_retificadas.xlsx",
    "c2_prelim": P / "resultado-preliminar-pmme.xlsx",
    "c2_final": P / "resultado-final-pmme-2o-ciclo-25-05.xlsx",
    "c2_reman9": P / "2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx",
    "c2_reman81": P / "resultado-final-vagas-remanescentes.xlsx",
    "c2_ch2_quadro": P / "2026_ciclo2_chamada2_vagas.xlsx",
    "c2_ch2_result": P / "2026_ciclo2_chamada2_resultado_final.xlsx",
    # ciclo 3
    "c3_quadro_orig": V / "2026_ciclo3_chamada1_vagas_original.xlsx",
    "c3_quadro_ret": P / "2026_ciclo3_chamada1_vagas_retificadas.xlsx",
    "c3_result_sj": P / "2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx",
    "c3_adesao": P / "2026_ciclo3_adesao_gestores_resultado_final.xlsx",
}
IVS_OFICIAL = RAIZ / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"

PESSOAIS = re.compile(r"CPF|NOME", re.I)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def norm(s) -> str:
    s = "" if s is None or (isinstance(s, float) and np.isnan(s)) else str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().upper()


def cod_curso(rotulo) -> int:
    m = re.match(r"\s*(\d+)", str(rotulo))
    if not m:
        raise ValueError(f"rótulo de curso sem número: {rotulo!r}")
    return int(m.group(1))


def nome_curso(rotulo) -> str:
    s = norm(rotulo)
    s = re.sub(r"^\d+\s*[\.\-]?\s*-?\s*", "", s)
    return s.replace("\xa0", " ").strip()


def cnes7(v) -> str:
    return str(int(float(str(v).strip()))).zfill(7)


def ibge6(v):
    if v is None or (isinstance(v, float) and np.isnan(v)) or str(v).strip() in ("", "-"):
        return None
    s = str(int(float(str(v).strip())))
    return s[:6]


def ibge_ndig(v):
    if v is None or (isinstance(v, float) and np.isnan(v)) or str(v).strip() in ("", "-"):
        return None
    return len(str(int(float(str(v).strip()))))


def _ler_bruto(p: Path, sheet=0) -> pd.DataFrame:
    return pd.read_excel(p, sheet_name=sheet, header=None, dtype=object)


def _achar_cabecalho(df: pd.DataFrame) -> int:
    for i in range(min(40, len(df))):
        vals = [norm(x) for x in df.iloc[i].tolist()]
        if "CURSO" in vals and "CNES" in vals:
            return i
    raise ValueError("cabeçalho não encontrado")


def ler_quadro(p: Path, sheet=0) -> pd.DataFrame:
    """Quadro de vagas: uma linha por célula (CNES × curso), imediatas e CR pelo bloco do cabeçalho.

    O primeiro 'TOTAL' do cabeçalho é o bloco de vagas imediatas e o segundo, o de cadastro
    reserva (linha acima do cabeçalho: 'VAGAS IMEDIATAS' | 'CADASTRO RESERVA'). Quadro com um só
    'TOTAL' (2ª chamada do ciclo 1, aba CR) devolve imediatas = 0.
    """
    df = _ler_bruto(p, sheet)
    h = _achar_cabecalho(df)
    cab = [norm(x) for x in df.iloc[h].tolist()]
    super_ = [norm(x) for x in df.iloc[h - 1].tolist()] if h > 0 else [""] * len(cab)
    idx_total = [j for j, c in enumerate(cab) if c == "TOTAL"]
    corpo = df.iloc[h + 1:].reset_index(drop=True)
    corpo = corpo[corpo[cab.index("CNES")].notna() & corpo[cab.index("CURSO")].notna()]

    def col(nome):
        return corpo[cab.index(nome)]

    out = pd.DataFrame({
        "rotulo_curso": col("CURSO").astype(str),
        "cod_curso": col("CURSO").map(cod_curso),
        "nome_curso": col("CURSO").map(nome_curso),
        "uf": col("UF").map(norm),
        "ibge_impresso": col("IBGE").map(ibge6),
        "ibge_ndig": col("IBGE").map(ibge_ndig),
        "municipio_impresso": col("MUNICIPIO").map(norm),
        "cnes": col("CNES").map(cnes7),
    })
    out["faixa_impressa"] = col("FAIXA DE ATRACAO").map(norm).str.extract(r"(\d)")[0].astype(float) \
        if "FAIXA DE ATRACAO" in cab else np.nan
    out["gestao"] = col("GESTAO").map(norm) if "GESTAO" in cab else None
    out["tipo_municipio"] = col("TIPO DE MUNICIPIO").map(norm).values if "TIPO DE MUNICIPIO" in cab else None
    if len(idx_total) >= 2:
        out["vagas_imediatas"] = pd.to_numeric(corpo[idx_total[0]], errors="raise").astype(int).values
        out["vagas_cr"] = pd.to_numeric(corpo[idx_total[1]], errors="raise").astype(int).values
        out["blocos"] = f"{super_[idx_total[0]] or super_[idx_total[0]-1]}|{super_[idx_total[1]]}"
    elif len(idx_total) == 1:
        out["vagas_imediatas"] = 0
        out["vagas_cr"] = pd.to_numeric(corpo[idx_total[0]], errors="raise").astype(int).values
        out["blocos"] = "so_cr"
    if "SITUACAO DAS VAGAS" in cab:
        out["situacao_impressa"] = col("SITUACAO DAS VAGAS").map(norm).values
    out["chave"] = out["cnes"] + "_" + out["cod_curso"].astype(str).str.zfill(2)
    return out.reset_index(drop=True)


def _sem_pessoais(df: pd.DataFrame) -> pd.DataFrame:
    return df[[c for c in df.columns if not PESSOAIS.search(str(c))]]


def ler_resultado(p: Path, sheet=0) -> pd.DataFrame:
    """Linhas candidato × opção de um arquivo de resultado (sem nome nem CPF).

    Um pseudônimo de candidato por arquivo (`id_cand`) é derivado do CPF mascarado em memória
    só para contar pessoas; ele não é gravado.
    """
    df = _ler_bruto(p, sheet)
    h = _achar_cabecalho(df)
    cab = [norm(x) for x in df.iloc[h].tolist()]
    corpo = df.iloc[h + 1:].reset_index(drop=True)
    corpo.columns = [c if c else f"_col{j}" for j, c in enumerate(cab)]
    corpo = corpo[corpo["CNES"].notna() & corpo["CURSO"].notna()].reset_index(drop=True)
    cpf_col = [c for c in corpo.columns if "CPF" in c]
    nome_col = [c for c in corpo.columns if c.startswith("NOME")]
    ident = (corpo[cpf_col[0]].astype(str) + "|" + (corpo[nome_col[0]].astype(str) if nome_col else ""))
    id_cand = ident.map(lambda s: hashlib.sha256(s.encode()).hexdigest()[:12])
    # Pseudônimo só do nome normalizado: casa a mesma pessoa entre arquivos com máscaras de CPF diferentes.
    id_nome = (corpo[nome_col[0]].map(norm) if nome_col else ident).map(
        lambda s: hashlib.sha256(s.encode()).hexdigest()[:12])
    out = pd.DataFrame({
        "id_cand": id_cand,
        "id_nome": id_nome,
        "cod_curso": corpo["CURSO"].map(cod_curso),
        "nome_curso": corpo["CURSO"].map(nome_curso),
        "uf": corpo["UF"].map(norm) if "UF" in corpo else None,
        "ibge_impresso": corpo["IBGE"].map(ibge6) if "IBGE" in corpo else None,
        "ibge_ndig": corpo["IBGE"].map(ibge_ndig) if "IBGE" in corpo else None,
        "municipio_impresso": corpo["MUNICIPIO"].map(norm) if "MUNICIPIO" in corpo else None,
        "cnes": corpo["CNES"].map(cnes7),
    })
    for c in corpo.columns:
        if c in ("CNES", "CURSO", "UF", "IBGE", "MUNICIPIO") or PESSOAIS.search(c):
            continue
        out[c] = corpo[c].map(lambda v: norm(v) if isinstance(v, str) else v).values
    out["chave"] = out["cnes"] + "_" + out["cod_curso"].astype(str).str.zfill(2)
    return out


def opcao(v) -> int:
    m = re.match(r"\s*(\d+)", str(v))
    return int(m.group(1)) if m else -1


def ler_ivs() -> pd.DataFrame:
    d = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str})
    d["co_ibge"] = d["co_ibge"].str[:6]
    return d[["co_ibge", "ivs", "nome_municipio_uf", "uf"]]


def faixa_regra(ivs: float) -> int:
    """Regra publicada (Edital 3/2025, 11.1.4; Edital 28/2026): IVS ≤ 0,300 → faixa 3 (R$ 10 mil);
    0,300 < IVS ≤ 0,400 → faixa 2 (R$ 15 mil); IVS > 0,400 → faixa 1 (R$ 20 mil)."""
    if ivs is None or np.isnan(ivs):
        return -1
    r = round(ivs * 1000)
    return 3 if r <= 300 else (2 if r <= 400 else 1)
