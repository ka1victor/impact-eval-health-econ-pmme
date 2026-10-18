"""a09_adquirir_cnes_nacional.py — CNES nacional: painel município × grupo de CBO × mês.

Tarefa C do protocolo multi-outcome da bolsa (doc 06_execucao/40, família F3).
Constrói, para os 5.565 municípios do IVS 2010 oficial, o painel balanceado de
médicos do CNES por grupo de CBO, para a diferença em descontinuidades do E7.

Competências (nenhuma >= 202609 é baixada ou lida: plano de pré-análise do ciclo 3):
- mensais 202406 a 202608;
- trimestrais 202201, 202204, ..., 202404 (pré-período que atravessa a
  Portaria GM/MS 752, de junho de 2023);
- 202302 e 202303, pelo adendo §13 (S5) do protocolo 40: a janela
  2022-01..2023-03 antecede todas as políticas nos mesmos cortes.

Grupos (adendo §13, S6): além dos generalistas, a CBO 225130 (medicina de
família e comunidade) tem grupo próprio, ``mfc_225130``.

Fonte: base completa mensal do CNES (``BASE_DE_DADOS_CNES_AAAAMM.ZIP``), baixada
por HTTPS do servlet de downloads do CNES (o FTP do DATASUS é bloqueado pelo
proxy deste ambiente). De cada ZIP são lidas só ``tbCargaHorariaSus`` (vínculos),
``tbEstabelecimento`` (município do estabelecimento) e ``tbAtividadeProfissional``
(rótulos de CBO). O ZIP fica em ``data/raw/cnes/`` só até a extração ser
validada; o SHA-256 e o tamanho vão para o manifesto e o ZIP é apagado.

Chave municipal: ``tbEstabelecimento.CO_MUNICIPIO_GESTOR`` (6 dígitos), o único
código de município da tabela, que é o município de localização do
estabelecimento (estabelecimentos sob gestão estadual também o têm, espalhados
pelos municípios; o diagnóstico vai para o manifesto). É a mesma chave do
painel do ciclo 1 (``03_adquirir_cnes_mensal.py``/``05_integrar_painel_analitico.py``).

Regra de cegamento: este script não lê IVS além da lista de municípios do
universo, não quebra nada por faixa ou lado de corte e não estima RDD.

Saídas:
- ``output/aquisicao/cnes_nacional/mensal/`` (cache por competência, ignorado pelo Git);
- ``output/aquisicao/cnes_nacional/painel_municipio_cbo_mes.parquet``;
- ``output/aquisicao/cnes_nacional/a09_validacao_painel_ciclo1.json``;
- ``output/aquisicao/cnes_nacional/a09_rotulos_cbo_medicos.csv``;
- ``output/aquisicao/a09_manifesto_cnes_nacional.json``.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import io
import json
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw" / "cnes"
OUT_AQ = ROOT / "output" / "aquisicao"
OUT_DIR = OUT_AQ / "cnes_nacional"
CACHE_DIR = OUT_DIR / "mensal"
PAINEL_FILE = OUT_DIR / "painel_municipio_cbo_mes.parquet"
VALIDACAO_FILE = OUT_DIR / "a09_validacao_painel_ciclo1.json"
ROTULOS_FILE = OUT_DIR / "a09_rotulos_cbo_medicos.csv"
RESUMO_FILE = OUT_DIR / "a09_resumo.md"
MANIFESTO_FILE = OUT_AQ / "a09_manifesto_cnes_nacional.json"

UNIVERSO_FILE = OUT_AQ / "a08_ivs_2010_oficial_municipio.csv"
PONTE_FILE = OUT_AQ / "ponte_curso_cbo_oficial.json"
MANIFESTO_CICLO1 = OUT_AQ / "manifesto_cnes_26_competencias.json"
PAINEL_CICLO1 = ROOT / "output" / "avaliacao_impacto" / "dados" / "painel_municipio_curso_mes.parquet"

URL_BASE = "https://cnes.datasus.gov.br/EstatisticasServlet?path="
REFERER = "https://cnes.datasus.gov.br/pages/downloads/arquivosBaseDados.jsp"

LIMITE_EXCLUSIVO = "202609"  # ciclo 3: nenhum mês a partir daqui é baixado ou lido
COMPETENCIAS_TRIMESTRAIS = [
    f"{ano}{mes:02d}" for ano in (2022, 2023) for mes in (1, 4, 7, 10)
] + ["202401", "202404"]
COMPETENCIAS_MENSAIS = [
    f"{ano}{mes:02d}"
    for ano, ini, fim in ((2024, 6, 12), (2025, 1, 12), (2026, 1, 8))
    for mes in range(ini, fim + 1)
]
# Adendo §13 do protocolo 40 (S5): meses extras na janela 2022-01..2023-03, antes de
# todas as políticas nos mesmos cortes (Portaria 752 de 06/2023; Portaria 3.493/2024).
COMPETENCIAS_PRE_ADICIONAIS = ["202302", "202303"]
COMPETENCIAS = sorted(COMPETENCIAS_TRIMESTRAIS + COMPETENCIAS_PRE_ADICIONAIS + COMPETENCIAS_MENSAIS)
assert all(c < LIMITE_EXCLUSIVO for c in COMPETENCIAS)

# Prefixos médicos: CBO 2002 (2251 clínicos, 2252 cirúrgicos, 2253 diagnóstico e
# terapêutica) e a família antiga 2231 (CBO 94/2002 provisória), se aparecer.
PREFIXOS_MEDICOS = ("2251", "2252", "2253", "2231")
GENERALISTAS = ("225125", "225142", "225170")
# Adendo §13 (S6): medicina de família e comunidade em grupo próprio, além dos
# generalistas. Continua contida em especialistas_nao_alvo (não é CBO-alvo).
MFC = "225130"
GRUPO_MFC = f"mfc_{MFC}"
GRUPOS_AGREGADOS = ("alvo_pmme", "generalistas", GRUPO_MFC, "especialistas_nao_alvo", "todos_medicos")

TABELAS = {
    "carga": "tbCargaHorariaSus",
    "estab": "tbEstabelecimento",
    "cbo": "tbAtividadeProfissional",
}
# Nome canônico -> nomes aceitos no cabeçalho (a primeira presença vence).
COLUNAS_CARGA = {
    "CO_UNIDADE": ["CO_UNIDADE"],
    "CO_PROFISSIONAL_SUS": ["CO_PROFISSIONAL_SUS"],
    "CO_CBO": ["CO_CBO"],
    "TP_SUS_NAO_SUS": ["TP_SUS_NAO_SUS"],
    "IND_VINCULACAO": ["IND_VINCULACAO"],
    "QT_CARGA_HORARIA_AMBULATORIAL": ["QT_CARGA_HORARIA_AMBULATORIAL", "QT_CARGA_HOR_AMBULATORIAL"],
    "QT_CARGA_HOR_HOSP_SUS": ["QT_CARGA_HOR_HOSP_SUS", "QT_CARGA_HORARIA_HOSPITALAR", "QT_CARGA_HOR_HOSPITALAR"],
    "QT_CARGA_HORARIA_OUTROS": ["QT_CARGA_HORARIA_OUTROS", "QT_CARGA_HOR_OUTROS"],
}
COLUNAS_CARGA_OBRIGATORIAS = ("CO_UNIDADE", "CO_PROFISSIONAL_SUS", "CO_CBO", "QT_CARGA_HORARIA_AMBULATORIAL")
COLUNAS_ESTAB = {
    "CO_UNIDADE": ["CO_UNIDADE"],
    "CO_CNES": ["CO_CNES"],
    "CO_MUNICIPIO_GESTOR": ["CO_MUNICIPIO_GESTOR", "CO_MUNICIPIO"],
    "CO_ESTADO_GESTOR": ["CO_ESTADO_GESTOR"],
    "TP_GESTAO": ["TP_GESTAO"],
}
COLUNAS_ESTAB_OBRIGATORIAS = ("CO_UNIDADE", "CO_MUNICIPIO_GESTOR")

# Parâmetros de validação fixados antes de ver o resultado (portão fail-closed).
TOLERANCIA_VALIDACAO = {"fracao_celulas_identicas_min": 0.99, "dif_relativa_soma_max": 0.005}
# Piso de plausibilidade de uma extração mensal nacional (abaixo disso, falha).
MIN_VINCULOS_MEDICOS_MES = 500_000
MIN_MUNICIPIOS_MES = 4_000

ESPACO_MINIMO_LIVRE = 3 * 1024**3  # bytes livres exigidos antes de iniciar um download
_trava_disco = threading.Lock()


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_arquivo(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while bloco := f.read(4 * 1024 * 1024):
            h.update(bloco)
    return h.hexdigest()


def tipo_competencia(comp: str) -> str:
    if comp in COMPETENCIAS_TRIMESTRAIS:
        return "trimestral"
    if comp in COMPETENCIAS_PRE_ADICIONAIS:
        return "pre_adicional"
    return "mensal"


def caminho_zip(comp: str) -> Path:
    return RAW_DIR / f"BASE_DE_DADOS_CNES_{comp}.ZIP"


def caminho_cache(comp: str) -> Path:
    return CACHE_DIR / f"cnes_medicos_{comp}.parquet"


def caminho_meta(comp: str) -> Path:
    return CACHE_DIR / f"meta_{comp}.json"


def checar_limite(comp: str) -> None:
    if comp >= LIMITE_EXCLUSIVO:
        raise RuntimeError(f"Competência {comp} >= {LIMITE_EXCLUSIVO} é vedada (ciclo 3).")


# ---------------------------------------------------------------- download

class Indisponivel(RuntimeError):
    """O servidor respondeu, mas não com um ZIP (competência não publicada)."""


def _baixar_uma_vez(comp: str, destino: Path, timeout: int) -> tuple[str, int]:
    nome = destino.name
    url = URL_BASE + nome
    parcial = destino.with_suffix(".ZIP.part")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": REFERER})
    h = hashlib.sha256()
    total = 0
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        inicio = resp.read(4)
        if inicio[:2] != b"PK":
            resto = inicio + resp.read(2048)
            raise Indisponivel(f"resposta não é ZIP ({resp.headers.get('Content-Type')}): {resto[:120]!r}")
        with parcial.open("wb") as f:
            f.write(inicio)
            h.update(inicio)
            total += len(inicio)
            ultimo = time.time()
            while True:
                bloco = resp.read(1024 * 1024)
                if not bloco:
                    break
                f.write(bloco)
                h.update(bloco)
                total += len(bloco)
                if time.time() - ultimo > 120:
                    vel = total / 1024**2 / max(time.time() - t0, 1e-9)
                    log(f"  {comp}: {total / 1024**2:.0f} MB ({vel:.2f} MB/s)")
                    ultimo = time.time()
    parcial.replace(destino)
    log(f"  {comp}: download concluído, {total / 1024**2:.1f} MB em {time.time() - t0:.0f}s")
    return h.hexdigest(), total


def testar_zip(path: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        ruim = zf.testzip()
        if ruim is not None:
            raise zipfile.BadZipFile(f"CRC inválido em {ruim}")


def esperar_disco() -> None:
    while True:
        with _trava_disco:
            livre = shutil.disk_usage(RAW_DIR).free
        if livre >= ESPACO_MINIMO_LIVRE:
            return
        log(f"  disco com {livre / 1024**3:.1f} GB livres; aguardando antes de novo download")
        time.sleep(60)


def baixar(comp: str, tentativas: int = 6, timeout: int = 300) -> dict[str, Any]:
    """Baixa e testa o ZIP; devolve metadados. Reaproveita ZIP local íntegro."""
    checar_limite(comp)
    destino = caminho_zip(comp)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if destino.exists():
        try:
            testar_zip(destino)
            log(f"  {comp}: ZIP local íntegro reaproveitado")
            return {
                "url": URL_BASE + destino.name,
                "data_download": dt.datetime.fromtimestamp(destino.stat().st_mtime).date().isoformat(),
                "sha256_zip": sha256_arquivo(destino),
                "bytes_zip": destino.stat().st_size,
                "tentativas_download": 0,
            }
        except Exception as exc:  # noqa: BLE001
            log(f"  {comp}: ZIP local inválido ({exc}); baixando de novo")
            destino.unlink()
    nao_zip = 0
    ultimo_erro = ""
    for tentativa in range(1, tentativas + 1):
        esperar_disco()
        try:
            log(f"  {comp}: download, tentativa {tentativa}/{tentativas}")
            sha, tamanho = _baixar_uma_vez(comp, destino, timeout)
            testar_zip(destino)
            return {
                "url": URL_BASE + destino.name,
                "data_download": dt.date.today().isoformat(),
                "sha256_zip": sha,
                "bytes_zip": tamanho,
                "tentativas_download": tentativa,
            }
        except Indisponivel as exc:
            nao_zip += 1
            ultimo_erro = str(exc)
            log(f"  {comp}: {exc}")
            if nao_zip >= 3:
                raise
        except Exception as exc:  # noqa: BLE001
            ultimo_erro = f"{type(exc).__name__}: {exc}"
            log(f"  {comp}: falha ({ultimo_erro})")
        for p in (destino, destino.with_suffix(".ZIP.part")):
            if p.exists():
                p.unlink()
        time.sleep(min(30 * 2 ** (tentativa - 1), 600))
    raise RuntimeError(f"download falhou após {tentativas} tentativas: {ultimo_erro}")


# ---------------------------------------------------------------- extração

def _membro(zf: zipfile.ZipFile, base: str) -> str:
    candidatos = [
        n for n in zf.namelist()
        if Path(n).name.lower().startswith(base.lower()) and n.lower().endswith(".csv")
    ]
    # tbCargaHorariaSus não pode casar com nomes mais longos de outra tabela
    exatos = [n for n in candidatos if Path(n).stem.lower().rstrip("0123456789") == base.lower()]
    escolha = exatos or candidatos
    if not escolha:
        raise KeyError(f"tabela {base} ausente do ZIP")
    return sorted(escolha)[0]


def _cabecalho(zf: zipfile.ZipFile, membro: str) -> list[str]:
    with zf.open(membro) as f:
        linha = f.readline().decode("latin1").strip()
    return [c.strip().strip('"').upper() for c in linha.split(";")]


def _mapear(cabecalho: list[str], spec: dict[str, list[str]]) -> dict[str, str]:
    mapa = {}
    for canon, nomes in spec.items():
        for nome in nomes:
            if nome in cabecalho:
                mapa[canon] = nome
                break
    return mapa


def _so_digitos(s: pd.Series) -> pd.Series:
    return s.astype("string").str.replace(r"\D", "", regex=True)


def _horas(s: pd.Series | None, n: int) -> np.ndarray:
    if s is None:
        return np.zeros(n, dtype=np.int32)
    v = pd.to_numeric(s.astype("string").str.replace(",", ".", regex=False), errors="coerce")
    return v.fillna(0).round().astype(np.int32).to_numpy()


def extrair(comp: str, zip_path: Path) -> tuple[pd.DataFrame, dict[str, Any], pd.DataFrame]:
    """Lê do ZIP os vínculos médicos e o município do estabelecimento."""
    t0 = time.time()
    meta: dict[str, Any] = {}
    with zipfile.ZipFile(zip_path) as zf:
        membros = {k: _membro(zf, base) for k, base in TABELAS.items() if k != "cbo"}
        try:
            membros["cbo"] = _membro(zf, TABELAS["cbo"])
        except KeyError:
            membros["cbo"] = None
        meta["membros_lidos"] = {k: v for k, v in membros.items() if v}
        meta["n_membros_zip"] = len(zf.namelist())

        cab_carga = _cabecalho(zf, membros["carga"])
        cab_estab = _cabecalho(zf, membros["estab"])
        mapa_carga = _mapear(cab_carga, COLUNAS_CARGA)
        mapa_estab = _mapear(cab_estab, COLUNAS_ESTAB)
        faltam = [c for c in COLUNAS_CARGA_OBRIGATORIAS if c not in mapa_carga]
        faltam += [c for c in COLUNAS_ESTAB_OBRIGATORIAS if c not in mapa_estab]
        if faltam:
            raise RuntimeError(f"{comp}: colunas obrigatórias ausentes: {faltam}")
        meta["colunas_tbCargaHorariaSus"] = cab_carga
        meta["colunas_tbEstabelecimento"] = cab_estab
        meta["mapa_colunas_carga"] = mapa_carga
        meta["mapa_colunas_estab"] = mapa_estab
        meta["colunas_canonicas_ausentes"] = sorted(
            [c for c in COLUNAS_CARGA if c not in mapa_carga] + [c for c in COLUNAS_ESTAB if c not in mapa_estab]
        )

        # cabeçalhos são lidos com aspas removidas; pandas usa os nomes do arquivo
        with zf.open(membros["estab"]) as f:
            estab = pd.read_csv(
                f, sep=";", encoding="latin1", dtype=str,
                usecols=lambda c: c.strip().strip('"').upper() in set(mapa_estab.values()),
            )
        estab.columns = [c.strip().strip('"').upper() for c in estab.columns]
        estab = estab.rename(columns={v: k for k, v in mapa_estab.items()})
        meta["linhas_tbEstabelecimento"] = int(len(estab))
        estab["CO_UNIDADE"] = estab["CO_UNIDADE"].astype("string").str.strip()
        estab["co_municipio"] = _so_digitos(estab["CO_MUNICIPIO_GESTOR"]).str[:6]
        dup = int(estab["CO_UNIDADE"].duplicated().sum())
        meta["co_unidade_duplicados_estab"] = dup
        estab = estab.drop_duplicates("CO_UNIDADE")

        partes = []
        linhas_carga = 0
        with zf.open(membros["carga"]) as f:
            for bloco in pd.read_csv(
                f, sep=";", encoding="latin1", dtype=str, chunksize=1_000_000,
                usecols=lambda c: c.strip().strip('"').upper() in set(mapa_carga.values()),
            ):
                bloco.columns = [c.strip().strip('"').upper() for c in bloco.columns]
                linhas_carga += len(bloco)
                cbo = bloco[mapa_carga["CO_CBO"]].astype("string").str.strip()
                partes.append(bloco.loc[cbo.str.startswith(PREFIXOS_MEDICOS).fillna(False)])
        meta["linhas_tbCargaHorariaSus"] = int(linhas_carga)
        carga = pd.concat(partes, ignore_index=True).rename(columns={v: k for k, v in mapa_carga.items()})

        rotulos = pd.DataFrame(columns=["co_cbo", "ds_cbo"])
        if membros["cbo"]:
            with zf.open(membros["cbo"]) as f:
                tb = pd.read_csv(f, sep=";", encoding="latin1", dtype=str)
            tb.columns = [c.strip().strip('"').upper() for c in tb.columns]
            col_cod = next((c for c in tb.columns if c in ("CO_CBO", "CO_ATIVIDADE_PROFISSIONAL")), tb.columns[0])
            col_ds = next((c for c in tb.columns if c.startswith("DS_")), tb.columns[1])
            rotulos = pd.DataFrame({
                "co_cbo": tb[col_cod].astype("string").str.strip(),
                "ds_cbo": tb[col_ds].astype("string").str.strip(),
            })
            rotulos = rotulos[rotulos["co_cbo"].str.startswith(PREFIXOS_MEDICOS).fillna(False)]

    carga["CO_UNIDADE"] = carga["CO_UNIDADE"].astype("string").str.strip()
    m = carga.merge(estab, on="CO_UNIDADE", how="left", validate="many_to_one")
    n = len(m)
    df = pd.DataFrame({
        "competencia": pd.Series([comp] * n, dtype="string"),
        "co_unidade": m["CO_UNIDADE"].astype("string"),
        "co_cnes": _so_digitos(m["CO_CNES"]).str.zfill(7) if "CO_CNES" in m else pd.Series([pd.NA] * n, dtype="string"),
        "co_municipio": m["co_municipio"].astype("string"),
        "co_profissional_sus": m["CO_PROFISSIONAL_SUS"].astype("string").str.strip(),
        "co_cbo": m["CO_CBO"].astype("string").str.strip(),
        "qt_ch_ambulatorial": _horas(m.get("QT_CARGA_HORARIA_AMBULATORIAL"), n),
        "qt_ch_hosp_sus": _horas(m.get("QT_CARGA_HOR_HOSP_SUS"), n),
        "qt_ch_outros": _horas(m.get("QT_CARGA_HORARIA_OUTROS"), n),
        "tp_sus_nao_sus": m["TP_SUS_NAO_SUS"].astype("string") if "TP_SUS_NAO_SUS" in m else pd.Series([pd.NA] * n, dtype="string"),
        "ind_vinculacao": m["IND_VINCULACAO"].astype("string") if "IND_VINCULACAO" in m else pd.Series([pd.NA] * n, dtype="string"),
        "tp_gestao": m["TP_GESTAO"].astype("string") if "TP_GESTAO" in m else pd.Series([pd.NA] * n, dtype="string"),
    })
    df = df.sort_values(["co_municipio", "co_unidade", "co_profissional_sus", "co_cbo"], kind="mergesort", na_position="last")
    df = df.reset_index(drop=True)

    # diagnóstico da chave municipal: gestão estadual espalhada pelos municípios
    estab_gestao = estab.assign(TP_GESTAO=estab.get("TP_GESTAO", pd.Series(pd.NA, index=estab.index)))
    diag = {}
    for g, parte in estab_gestao.groupby(estab_gestao["TP_GESTAO"].fillna("NA"), sort=True):
        diag[str(g)] = {
            "estabelecimentos": int(len(parte)),
            "municipios_distintos": int(parte["co_municipio"].nunique()),
        }
    uf_ok = None
    if "CO_ESTADO_GESTOR" in estab:
        uf = _so_digitos(estab["CO_ESTADO_GESTOR"]).str.zfill(2)
        uf_ok = float((estab["co_municipio"].str[:2] == uf).mean())
    meta["diagnostico_chave_municipal"] = {
        "por_tp_gestao": diag,
        "fracao_uf_do_municipio_igual_co_estado_gestor": uf_ok,
    }
    prefixo4 = df["co_cbo"].str[:4]
    meta["vinculos_medicos_por_familia_cbo"] = {
        k: int(v) for k, v in prefixo4.value_counts().sort_index().items()
    }
    meta["linhas_vinculos_medicos"] = int(n)
    meta["vinculos_sem_estabelecimento"] = int(df["co_municipio"].isna().sum())
    prof_valido = df["co_profissional_sus"].notna() & (df["co_profissional_sus"] != "")
    meta["vinculos_sem_co_profissional_sus"] = int((~prof_valido).sum())
    meta["profissionais_distintos"] = int(df.loc[prof_valido, "co_profissional_sus"].nunique())
    meta["municipios_distintos"] = int(df["co_municipio"].nunique())
    meta["estabelecimentos_distintos"] = int(df["co_unidade"].nunique())
    meta["segundos_extracao"] = round(time.time() - t0, 1)
    return df, meta, rotulos.drop_duplicates().sort_values("co_cbo").reset_index(drop=True)


def processar(comp: str) -> dict[str, Any]:
    """Download → teste → extração → cache → apaga ZIP. Idempotente."""
    checar_limite(comp)
    if caminho_cache(comp).exists() and caminho_meta(comp).exists():
        return json.loads(caminho_meta(comp).read_text(encoding="utf-8"))
    try:
        info = baixar(comp)
    except Indisponivel as exc:
        return {"competencia": comp, "status": "indisponivel", "erro": str(exc), "data_tentativa": dt.date.today().isoformat()}
    except Exception as exc:  # noqa: BLE001
        return {"competencia": comp, "status": "falha_download", "erro": str(exc), "data_tentativa": dt.date.today().isoformat()}
    try:
        df, meta, rotulos = extrair(comp, caminho_zip(comp))
    except Exception as exc:  # noqa: BLE001
        log(f"  {comp}: FALHA NA EXTRAÇÃO, ZIP mantido: {exc}")
        return {"competencia": comp, "status": "falha_extracao", "erro": f"{type(exc).__name__}: {exc}", **info}
    if meta["linhas_vinculos_medicos"] < MIN_VINCULOS_MEDICOS_MES or meta["municipios_distintos"] < MIN_MUNICIPIOS_MES:
        log(f"  {comp}: extração implausível ({meta['linhas_vinculos_medicos']} linhas); ZIP mantido")
        return {"competencia": comp, "status": "falha_validacao", **info, **meta}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = caminho_cache(comp).with_suffix(".parquet.tmp")
    df.to_parquet(tmp, index=False)
    tmp.replace(caminho_cache(comp))
    rotulos.to_csv(CACHE_DIR / f"rotulos_cbo_{comp}.csv", index=False)
    registro = {
        "competencia": comp,
        "tipo": tipo_competencia(comp),
        "status": "adquirido_extraido_zip_apagado",
        "arquivo": caminho_zip(comp).name,
        **info,
        **meta,
        "cache_parquet": caminho_cache(comp).relative_to(ROOT).as_posix(),
        "data_processamento": dt.date.today().isoformat(),
    }
    caminho_meta(comp).write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    caminho_zip(comp).unlink()
    log(f"  {comp}: OK — {meta['linhas_vinculos_medicos']:,} vínculos médicos, "
        f"{meta['municipios_distintos']} municípios; ZIP apagado")
    return registro


def etapa_aquisicao(competencias: list[str], workers: int) -> dict[str, dict[str, Any]]:
    log(f"Aquisição de {len(competencias)} competências com {workers} downloads simultâneos")
    resultados: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(processar, c): c for c in competencias}
        for fut in concurrent.futures.as_completed(futs):
            c = futs[fut]
            try:
                resultados[c] = fut.result()
            except Exception as exc:  # noqa: BLE001
                resultados[c] = {"competencia": c, "status": "erro", "erro": f"{type(exc).__name__}: {exc}"}
            log(f"{c}: {resultados[c]['status']}")
    return resultados


# ---------------------------------------------------------------- painel

def carregar_ponte() -> tuple[list[str], dict[str, list[int]], str]:
    raw = json.loads(PONTE_FILE.read_text(encoding="utf-8"))
    alvo: set[str] = set()
    cbo_cursos: dict[str, list[int]] = {}
    for curso in raw["catalogo_cursos"]:
        for cbo in curso["cbos_elegiveis"]:
            cbo = str(cbo).zfill(6)
            alvo.add(cbo)
            cbo_cursos.setdefault(cbo, []).append(int(curso["cod_curso"]))
    return sorted(alvo), cbo_cursos, raw.get("versao_ponte", "")


def carregar_universo() -> list[str]:
    u = pd.read_csv(UNIVERSO_FILE, usecols=["co_ibge"], dtype={"co_ibge": str})
    cod = u["co_ibge"].str.replace(r"\D", "", regex=True).str.zfill(6)
    if cod.duplicated().any() or len(cod) < 5_500:
        raise RuntimeError("universo municipal do a08 inválido")
    return sorted(cod)


def grupos_do_cbo(alvo: list[str]) -> list[str]:
    return [f"cbo_{c}" for c in alvo] + list(GRUPOS_AGREGADOS)


def agregar_mes(df: pd.DataFrame, alvo: list[str]) -> pd.DataFrame:
    """Uma linha por município × grupo (só células com vínculo)."""
    df = df.loc[df["co_municipio"].notna()].copy()
    df["eh_alvo"] = df["co_cbo"].isin(alvo)
    df["eh_generalista"] = df["co_cbo"].isin(GENERALISTAS)
    df["eh_2251_3"] = df["co_cbo"].str.startswith(("2251", "2252", "2253"))
    df["horas_sus"] = df["qt_ch_ambulatorial"].astype(np.int64) + df["qt_ch_hosp_sus"].astype(np.int64)
    df["horas_tot"] = df["horas_sus"] + df["qt_ch_outros"].astype(np.int64)
    prof = df["co_profissional_sus"].where(df["co_profissional_sus"].fillna("") != "")
    df["prof"] = prof

    def _agg(sub: pd.DataFrame, grupo: pd.Series | str) -> pd.DataFrame:
        g = sub.assign(grupo=grupo).groupby(["co_municipio", "grupo"], sort=True)
        return g.agg(
            n_vinculos=("co_cbo", "size"),
            n_profissionais_distintos=("prof", "nunique"),
            horas_sus_semanais=("horas_sus", "sum"),
            horas_totais=("horas_tot", "sum"),
        ).reset_index()

    partes = [
        _agg(df.loc[df["eh_alvo"]], "cbo_" + df.loc[df["eh_alvo"], "co_cbo"]),
        _agg(df.loc[df["eh_alvo"]], "alvo_pmme"),
        _agg(df.loc[df["eh_generalista"]], "generalistas"),
        _agg(df.loc[df["co_cbo"] == MFC], GRUPO_MFC),
        _agg(df.loc[df["eh_2251_3"] & ~df["eh_alvo"] & ~df["eh_generalista"]], "especialistas_nao_alvo"),
        _agg(df, "todos_medicos"),
    ]
    return pd.concat(partes, ignore_index=True)


def construir_painel(competencias: list[str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    alvo, _, _ = carregar_ponte()
    universo = carregar_universo()
    grupos = grupos_do_cbo(alvo)
    fora: dict[str, dict[str, int]] = {}
    partes = []
    for comp in competencias:
        checar_limite(comp)
        df = pd.read_parquet(caminho_cache(comp))
        if set(df["competencia"].unique()) != {comp}:
            raise RuntimeError(f"competência interna incompatível no cache de {comp}")
        agg = agregar_mes(df, alvo)
        fora_mes = agg.loc[(agg["grupo"] == "todos_medicos") & ~agg["co_municipio"].isin(universo)]
        for r in fora_mes.itertuples(index=False):
            d = fora.setdefault(r.co_municipio, {})
            d[comp] = int(r.n_vinculos)
        agg = agg.loc[agg["co_municipio"].isin(universo)]
        agg.insert(1, "competencia", comp)
        partes.append(agg)
    obs = pd.concat(partes, ignore_index=True).rename(columns={"co_municipio": "co_ibge"})
    esqueleto = pd.MultiIndex.from_product(
        [universo, competencias, grupos], names=["co_ibge", "competencia", "grupo"]
    ).to_frame(index=False)
    painel = esqueleto.merge(obs, on=["co_ibge", "competencia", "grupo"], how="left", validate="one_to_one")
    for col in ("n_vinculos", "n_profissionais_distintos", "horas_sus_semanais", "horas_totais"):
        painel[col] = painel[col].fillna(0).astype(np.int32)
    painel["tem_profissional"] = (painel["n_profissionais_distintos"] >= 1).astype(np.int8)
    # zeros só em competência lida com sucesso; competência não obtida fica sem linhas
    painel["natureza_dos_dados"] = "EMPIRICO"
    painel = painel.sort_values(["co_ibge", "competencia", "grupo"], kind="mergesort").reset_index(drop=True)
    info = {
        "municipios_universo": len(universo),
        "grupos": grupos,
        "linhas": int(len(painel)),
        "municipios_cnes_fora_do_universo": {
            k: {"competencias": len(v), "vinculos_medicos_max_mes": max(v.values())}
            for k, v in sorted(fora.items())
        },
    }
    return painel, info


def gravar_painel(painel: pd.DataFrame) -> None:
    tabela = pa.Table.from_pandas(painel, preserve_index=False)
    PAINEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(tabela, PAINEL_FILE, compression="zstd", compression_level=9, use_dictionary=True)


# ---------------------------------------------------------------- validação

def validar_contra_ciclo1(competencias: list[str]) -> dict[str, Any]:
    """Compara o estoque por município × curso com o painel de 368 municípios do ciclo 1.

    Lê do painel antigo apenas chaves e o estoque (`especialistas_mst`).
    """
    _, cbo_cursos, _ = carregar_ponte()
    antigo = pd.read_parquet(PAINEL_CICLO1, columns=["co_ibge_6d", "cod_curso", "competencia", "especialistas_mst"])
    antigo["co_ibge_6d"] = antigo["co_ibge_6d"].astype(str).str.zfill(6)
    antigo["competencia"] = antigo["competencia"].astype(str)
    comuns = sorted(set(antigo["competencia"]) & set(competencias))
    chaves = antigo[["co_ibge_6d", "cod_curso"]].drop_duplicates()
    munis = set(chaves["co_ibge_6d"])
    sha_antigo = {}
    if MANIFESTO_CICLO1.exists():
        man = json.loads(MANIFESTO_CICLO1.read_text(encoding="utf-8"))
        sha_antigo = {e["competencia"]: e.get("sha256_zip") for e in man.get("manifesto_mensal", [])}
    novos = []
    por_mes = []
    for comp in comuns:
        df = pd.read_parquet(caminho_cache(comp), columns=["co_municipio", "co_profissional_sus", "co_cbo"])
        df = df.loc[df["co_municipio"].isin(munis) & df["co_cbo"].isin(cbo_cursos.keys())]
        df = df.loc[df["co_profissional_sus"].fillna("") != ""]
        df["cod_curso"] = df["co_cbo"].map(cbo_cursos)
        df = df.explode("cod_curso")
        df["cod_curso"] = df["cod_curso"].astype(int)
        est = (df.groupby(["co_municipio", "cod_curso"])["co_profissional_sus"].nunique()
               .rename("estoque_novo").reset_index().rename(columns={"co_municipio": "co_ibge_6d"}))
        est["competencia"] = comp
        novos.append(est)
        meta = json.loads(caminho_meta(comp).read_text(encoding="utf-8"))
        por_mes.append({
            "competencia": comp,
            "sha256_igual_ao_manifesto_ciclo1": meta.get("sha256_zip") == sha_antigo.get(comp),
        })
    novo = pd.concat(novos, ignore_index=True) if novos else pd.DataFrame(
        columns=["co_ibge_6d", "cod_curso", "estoque_novo", "competencia"])
    a = antigo.loc[antigo["competencia"].isin(comuns)]
    cmp_ = a.merge(novo, on=["co_ibge_6d", "cod_curso", "competencia"], how="left")
    cmp_["estoque_novo"] = cmp_["estoque_novo"].fillna(0).astype(int)
    cmp_["dif"] = cmp_["estoque_novo"] - cmp_["especialistas_mst"]
    for r in por_mes:
        parte = cmp_.loc[cmp_["competencia"] == r["competencia"]]
        r["celulas"] = int(len(parte))
        r["celulas_identicas"] = int((parte["dif"] == 0).sum())
        r["soma_estoque_ciclo1"] = int(parte["especialistas_mst"].sum())
        r["soma_estoque_a09"] = int(parte["estoque_novo"].sum())
        r["max_abs_dif"] = int(parte["dif"].abs().max()) if len(parte) else 0
    total_antigo = int(cmp_["especialistas_mst"].sum())
    resultado = {
        "painel_comparado": PAINEL_CICLO1.relative_to(ROOT).as_posix(),
        "colunas_lidas_do_painel_antigo": ["co_ibge_6d", "cod_curso", "competencia", "especialistas_mst"],
        "definicao": "CO_PROFISSIONAL_SUS distinto por município (CO_MUNICIPIO_GESTOR) × curso (CBOs elegíveis da ponte) × competência, como em 05_integrar_painel_analitico.py",
        "competencias_comparadas": comuns,
        "municipios": len(munis),
        "celulas_municipio_curso_mes": int(len(cmp_)),
        "celulas_identicas": int((cmp_["dif"] == 0).sum()),
        "fracao_celulas_identicas": float((cmp_["dif"] == 0).mean()) if len(cmp_) else None,
        "soma_estoque_ciclo1": total_antigo,
        "soma_estoque_a09": int(cmp_["estoque_novo"].sum()),
        "dif_relativa_soma": (float(cmp_["estoque_novo"].sum() - total_antigo) / total_antigo) if total_antigo else None,
        "max_abs_dif_celula": int(cmp_["dif"].abs().max()) if len(cmp_) else 0,
        "por_competencia": por_mes,
        "tolerancia_teste": TOLERANCIA_VALIDACAO,
        "nota_cegamento": "comparação só de contagens; nenhuma coluna de IVS ou faixa é lida",
        "natureza_dos_dados": "EMPIRICO",
    }
    aprovado = (
        len(cmp_) > 0
        and resultado["fracao_celulas_identicas"] >= TOLERANCIA_VALIDACAO["fracao_celulas_identicas_min"]
        and abs(resultado["dif_relativa_soma"]) <= TOLERANCIA_VALIDACAO["dif_relativa_soma_max"]
    )
    resultado["status"] = "APROVADO" if aprovado else "REPROVADO"
    return resultado


# ---------------------------------------------------------------- manifesto

def _comparar_esquemas(registros: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ok = {c: r for c, r in registros.items() if "colunas_tbCargaHorariaSus" in r}
    if not ok:
        return {}
    ref_comp = max(ok)
    ref = ok[ref_comp]
    saida: dict[str, Any] = {"referencia": ref_comp, "diferencas": {}}
    for c, r in sorted(ok.items()):
        dif = {}
        for tab in ("colunas_tbCargaHorariaSus", "colunas_tbEstabelecimento"):
            a, b = set(r[tab]), set(ref[tab])
            if a != b:
                dif[tab] = {"so_nesta": sorted(a - b), "so_na_referencia": sorted(b - a)}
        nomes = {k: Path(v).name for k, v in r.get("membros_lidos", {}).items()}
        if dif or r.get("colunas_canonicas_ausentes"):
            dif["colunas_canonicas_ausentes"] = r.get("colunas_canonicas_ausentes", [])
        if dif:
            dif["membros_lidos"] = nomes
            saida["diferencas"][c] = dif
    return saida


def gravar_manifesto(registros: dict[str, dict[str, Any]], painel_info: dict[str, Any] | None,
                     validacao: dict[str, Any] | None, rotulos: pd.DataFrame | None) -> None:
    alvo, cbo_cursos, versao = carregar_ponte()
    enxutos = {}
    for c, r in sorted(registros.items()):
        e = {k: v for k, v in r.items() if k not in ("colunas_tbCargaHorariaSus", "colunas_tbEstabelecimento")}
        enxutos[c] = e
    obtidas = sorted(c for c, r in registros.items() if r.get("status") == "adquirido_extraido_zip_apagado")
    manifesto = {
        "gerador": "scripts/aquisicao/a09_adquirir_cnes_nacional.py",
        "protocolo": "docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md (tarefa C, família F3)",
        "fonte": {
            "nome": "CNES — base completa mensal (BASE_DE_DADOS_CNES_AAAAMM.ZIP), DATASUS/MS",
            "url_modelo": URL_BASE + "BASE_DE_DADOS_CNES_AAAAMM.ZIP",
            "referer": REFERER,
            "nota": "FTP do DATASUS bloqueado pelo proxy; servlet HTTPS do CNES serve o mesmo arquivo (sem Content-Length)",
            "tabelas": TABELAS,
        },
        "natureza_dos_dados": "EMPIRICO",
        "data_execucao": dt.date.today().isoformat(),
        "entradas_locais": {
            p.relative_to(ROOT).as_posix(): {"sha256": sha256_arquivo(p), "bytes": p.stat().st_size, "uso": uso}
            for p, uso in (
                (UNIVERSO_FILE, "só a lista co_ibge do universo (IVS não é lido)"),
                (PONTE_FILE, "CBO-alvo (cbos_elegiveis dos 16 cursos)"),
                (PAINEL_CICLO1, "validação: co_ibge_6d, cod_curso, competencia, especialistas_mst"),
                (MANIFESTO_CICLO1, "validação: SHA-256 dos ZIPs do ciclo 1"),
            )
            if p.exists()
        },
        "competencias_planejadas": COMPETENCIAS,
        "regra_competencia_ausente": (
            "competência não obtida ou reprovada não tem linhas no painel; nada é interpolado ou "
            "copiado de outro mês. Zeros só existem em competências lidas com sucesso."
        ),
        "competencias_trimestrais": COMPETENCIAS_TRIMESTRAIS,
        "competencias_pre_adicionais": COMPETENCIAS_PRE_ADICIONAIS,
        "competencias_mensais": COMPETENCIAS_MENSAIS,
        "competencias_obtidas": obtidas,
        "competencias_nao_obtidas": {
            c: {"status": r.get("status"), "erro": r.get("erro")}
            for c, r in sorted(registros.items()) if c not in obtidas
        },
        "limite_ciclo3": f"nenhuma competência >= {LIMITE_EXCLUSIVO} é baixada ou lida",
        "filtros": {
            "vinculos": f"tbCargaHorariaSus com CO_CBO iniciando em {list(PREFIXOS_MEDICOS)}; sem filtro de TP_SUS_NAO_SUS, vinculação ou tipo de unidade",
            "municipio": "tbEstabelecimento.CO_MUNICIPIO_GESTOR (6 dígitos) via CO_UNIDADE: município de localização do estabelecimento",
            "universo": f"{UNIVERSO_FILE.relative_to(ROOT).as_posix()} (só a lista de co_ibge; IVS não é lido)",
            "profissional": "CO_PROFISSIONAL_SUS não vazio para contagem de distintos; vínculos sem ID entram em n_vinculos e horas",
        },
        "definicoes": {
            "n_vinculos": "linhas de tbCargaHorariaSus (profissional × estabelecimento × CBO × vínculo) no município-grupo-mês",
            "n_profissionais_distintos": "CO_PROFISSIONAL_SUS distintos no município-grupo-mês (agregados contam a pessoa uma vez)",
            "horas_sus_semanais": "soma de QT_CARGA_HORARIA_AMBULATORIAL + QT_CARGA_HOR_HOSP_SUS",
            "horas_totais": "horas_sus_semanais + QT_CARGA_HORARIA_OUTROS",
            "tem_profissional": "n_profissionais_distintos >= 1",
            "grupos": {
                "cbo_XXXXXX": "cada CBO-alvo da ponte (cbos_elegiveis dos 16 cursos)",
                "alvo_pmme": "união das CBO-alvo",
                "generalistas": list(GENERALISTAS),
                GRUPO_MFC: f"CBO {MFC} (médico de família e comunidade), grupo próprio pelo adendo §13 (S6); também contido em especialistas_nao_alvo",
                "especialistas_nao_alvo": "CBO 2251/2252/2253 fora das CBO-alvo e dos generalistas",
                "todos_medicos": "CBO 2251/2252/2253 e 2231 (a família 2231 só entra se aparecer)",
            },
        },
        "ponte": {"arquivo": PONTE_FILE.relative_to(ROOT).as_posix(), "versao": versao,
                  "cbos_alvo": alvo, "cbo_para_cursos": cbo_cursos},
        "rotulos_cbo_verificados": (
            rotulos.loc[rotulos["co_cbo"].isin(list(GENERALISTAS) + [MFC] + alvo)].to_dict(orient="records")
            if rotulos is not None else None
        ),
        "diferencas_de_esquema": _comparar_esquemas(registros),
        "painel": ({"arquivo": PAINEL_FILE.relative_to(ROOT).as_posix(), "sha256": sha256_arquivo(PAINEL_FILE),
                    **painel_info} if painel_info else None),
        "validacao_ciclo1": ({"arquivo": VALIDACAO_FILE.relative_to(ROOT).as_posix(),
                              "status": validacao.get("status"),
                              "fracao_celulas_identicas": validacao.get("fracao_celulas_identicas"),
                              "dif_relativa_soma": validacao.get("dif_relativa_soma")} if validacao else None),
        "por_competencia": enxutos,
        "cegamento": "nenhum outcome foi tabulado por faixa, lado de corte ou contra o IVS",
    }
    MANIFESTO_FILE.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fmt(x: float | None) -> str:
    return "n/d" if x is None else f"{x:.6f}"


def gravar_resumo(registros: dict[str, dict[str, Any]], painel: pd.DataFrame | None,
                  validacao: dict[str, Any] | None, rotulos: pd.DataFrame) -> None:
    """Resumo legível gerado do manifesto e do painel (só totais nacionais, sem IVS)."""
    linhas = [
        "# A09 — resumo gerado do CNES nacional",
        "",
        f"Gerado por `scripts/aquisicao/a09_adquirir_cnes_nacional.py` em {dt.date.today().isoformat()}. "
        "Não editar à mão. Natureza dos dados: EMPIRICO. Totais nacionais apenas; nada por faixa ou lado de corte.",
        "",
        "## Competências",
        "",
        "| Competência | Tipo | Status | MB do ZIP | SHA-256 (12) | Vínculos médicos | Profissionais distintos | Municípios | 2231 | 2251 | 2252 | 2253 |",
        "|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for c in COMPETENCIAS:
        r = registros.get(c)
        if r is None:
            linhas.append(f"| {c} | {tipo_competencia(c)} | não processada | | | | | | | | | |")
            continue
        fam = r.get("vinculos_medicos_por_familia_cbo", {})
        mb = f"{r['bytes_zip'] / 1024**2:.1f}" if r.get("bytes_zip") else ""
        sha = (r.get("sha256_zip") or "")[:12]
        linhas.append(
            f"| {c} | {r.get('tipo', '')} | {r.get('status')} | {mb} | `{sha}` | "
            f"{r.get('linhas_vinculos_medicos', '')} | {r.get('profissionais_distintos', '')} | "
            f"{r.get('municipios_distintos', '')} | {fam.get('2231', 0)} | {fam.get('2251', 0)} | "
            f"{fam.get('2252', 0)} | {fam.get('2253', 0)} |"
        )
    if painel is not None:
        tot = (painel.groupby(["competencia", "grupo"])[["n_vinculos", "n_profissionais_distintos", "tem_profissional"]]
               .sum().reset_index())
        linhas += [
            "",
            "## Totais nacionais por grupo (universo do a08)",
            "",
            "Profissionais = soma dos distintos por município (quem atua em dois municípios conta duas vezes). "
            "Municípios com profissional = número de municípios com `tem_profissional = 1`.",
            "",
        ]
        for grupo in ("todos_medicos", "alvo_pmme", "generalistas", GRUPO_MFC, "especialistas_nao_alvo"):
            linhas += [f"### {grupo}", "", "| Competência | Vínculos | Profissionais (soma municipal) | Municípios com profissional |",
                       "|---|---:|---:|---:|"]
            for r in tot.loc[tot["grupo"] == grupo].itertuples(index=False):
                linhas.append(f"| {r.competencia} | {r.n_vinculos} | {r.n_profissionais_distintos} | {r.tem_profissional} |")
            linhas.append("")
    if validacao is not None:
        linhas += [
            f"## Validação contra o painel do ciclo 1 ({validacao['municipios']} municípios)",
            "",
            f"Status: **{validacao['status']}**. Células município × curso × mês comparadas: "
            f"{validacao['celulas_municipio_curso_mes']}; idênticas: {validacao['celulas_identicas']} "
            f"(fração {_fmt(validacao['fracao_celulas_identicas'])}); soma do estoque ciclo 1 = "
            f"{validacao['soma_estoque_ciclo1']}, a09 = {validacao['soma_estoque_a09']} "
            f"(diferença relativa {_fmt(validacao['dif_relativa_soma'])}); maior diferença absoluta numa célula = "
            f"{validacao['max_abs_dif_celula']}.",
            "",
            "| Competência | SHA-256 igual ao do ciclo 1 | Células | Idênticas | Soma ciclo 1 | Soma a09 | Máx. dif. |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
        for r in validacao["por_competencia"]:
            linhas.append(
                f"| {r['competencia']} | {'sim' if r['sha256_igual_ao_manifesto_ciclo1'] else 'não'} | {r['celulas']} | "
                f"{r['celulas_identicas']} | {r['soma_estoque_ciclo1']} | {r['soma_estoque_a09']} | {r['max_abs_dif']} |"
            )
        linhas.append("")
    if len(rotulos):
        linhas += ["## Rótulos de CBO médicos lidos de tbAtividadeProfissional", "",
                   "| CBO | Rótulo | Primeira | Última | Competências |", "|---|---|---|---|---:|"]
        for r in rotulos.itertuples(index=False):
            linhas.append(f"| {r.co_cbo} | {r.ds_cbo} | {r.primeira} | {r.ultima} | {r.n_competencias} |")
        linhas.append("")
    RESUMO_FILE.write_text("\n".join(linhas), encoding="utf-8")


def ler_registros() -> dict[str, dict[str, Any]]:
    regs = {}
    for c in COMPETENCIAS:
        if caminho_meta(c).exists():
            regs[c] = json.loads(caminho_meta(c).read_text(encoding="utf-8"))
    return regs


def consolidar_rotulos(obtidas: list[str]) -> pd.DataFrame:
    partes = []
    for c in obtidas:
        p = CACHE_DIR / f"rotulos_cbo_{c}.csv"
        if p.exists():
            r = pd.read_csv(p, dtype=str)
            r["competencia"] = c
            partes.append(r)
    if not partes:
        return pd.DataFrame(columns=["co_cbo", "ds_cbo"])
    r = pd.concat(partes, ignore_index=True)
    r = (r.sort_values(["co_cbo", "competencia"]).groupby(["co_cbo", "ds_cbo"], as_index=False)
         .agg(primeira=("competencia", "min"), ultima=("competencia", "max"), n_competencias=("competencia", "nunique")))
    return r


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=["aquisicao", "painel", "tudo"], default="tudo")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--competencias", nargs="*", help="subconjunto (para depuração)")
    args = ap.parse_args()
    comps = sorted(args.competencias) if args.competencias else COMPETENCIAS
    for c in comps:
        checar_limite(c)
        if c not in COMPETENCIAS:
            raise SystemExit(f"competência fora do plano: {c}")

    resultados: dict[str, dict[str, Any]] = {}
    if args.etapa in ("aquisicao", "tudo"):
        # ordem: uma trimestral antiga cedo para detectar mudança de esquema
        ordem = sorted(comps, key=lambda c: (c != "202201", c != "202608", c))
        resultados = etapa_aquisicao(ordem, args.workers)
    registros = ler_registros()
    for c, r in resultados.items():
        registros.setdefault(c, r)
    obtidas = sorted(c for c, r in registros.items() if r.get("status") == "adquirido_extraido_zip_apagado")

    painel_info = validacao = painel = None
    rotulos = consolidar_rotulos(obtidas)
    if args.etapa in ("painel", "tudo"):
        if not obtidas:
            raise SystemExit("nenhuma competência em cache")
        log(f"Construindo painel com {len(obtidas)} competências")
        painel, painel_info = construir_painel(obtidas)
        gravar_painel(painel)
        painel_info["competencias"] = obtidas
        log(f"Painel: {len(painel):,} linhas, {PAINEL_FILE.stat().st_size / 1024**2:.1f} MB")
        validacao = validar_contra_ciclo1(obtidas)
        VALIDACAO_FILE.write_text(json.dumps(validacao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        log(f"Validação ciclo 1: {validacao['fracao_celulas_identicas']} das células idênticas")
        rotulos.to_csv(ROTULOS_FILE, index=False)
    gravar_manifesto(registros, painel_info, validacao, rotulos)
    log(f"Manifesto: {MANIFESTO_FILE.relative_to(ROOT)}")
    if args.etapa in ("painel", "tudo"):
        gravar_resumo(registros, painel, validacao, rotulos)
        log(f"Resumo: {RESUMO_FILE.relative_to(ROOT)}")
    faltantes = sorted(set(comps) - set(obtidas))
    if faltantes:
        log(f"Competências não obtidas: {faltantes}")
    if validacao is not None and validacao["status"] != "APROVADO":
        log("PORTÃO REPROVADO: o painel não reproduz o ciclo 1 dentro da tolerância")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
