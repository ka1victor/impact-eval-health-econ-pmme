"""a16_cnes_profissional_mensal.py — portão G5: painel CNES médico × mês com registro do conselho.

Plano: ``docs/06_execucao/51_plano_perguntas_reformuladas.md`` (P4, tarefa T4.0, e P6, T6.2), onda 1.
Este script é **portão de viabilidade e construção de painel**. Ele não calcula contraste nenhum: nada
antes ou depois da entrada no PMM-E, nada por IVS, corte, faixa, ciclo ou tratamento. Só diagnósticos de
cobertura (médicos achados por mês) e de estabilidade da chave profissional.

Pergunta do portão
------------------
Dá para montar, de 202406 a 202608 (nunca ≥ 202609), um painel médico × mês com vínculos,
estabelecimentos, municípios, CBO e horas (ambulatorial, hospitalar e outras; vínculo SUS e não SUS),
para (a) os médicos do PMM-E ligados na X1 e (b) os candidatos que o G1 vier a ligar?

Fonte
-----
Base completa mensal do CNES (``BASE_DE_DADOS_CNES_AAAAMM.ZIP``), pelo servlet HTTPS do CNES com o
``Referer`` da página de downloads (o mesmo caminho do a09; o FTP do DATASUS é bloqueado pelo proxy).
De cada ZIP são lidas só:
- ``tbCargaHorariaSus``: uma linha por profissional × estabelecimento × CBO, com
  ``CO_PROFISSIONAL_SUS``, ``CO_CBO``, ``TP_SUS_NAO_SUS``, as três cargas horárias e o registro do
  conselho (``CO_CONSELHO_CLASSE``, ``NU_REGISTRO``, ``SG_UF_CRM``);
- ``tbEstabelecimento``: CNES, município (``CO_MUNICIPIO_GESTOR``, a chave do a09), gestão, tipo de
  unidade e natureza jurídica;
- ``tbDadosProfissionalSus``: só o nome, só nas seis competências da X1 e só dos profissionais cujo
  registro é um CRM das listas do PMM-E (para refazer a ligação da X1 com a mesma regra);
- ``tbOrgaoEmissor`` (202608): o código do CRM no campo ``CO_CONSELHO_CLASSE`` (regra da X1).
Só vínculos com CBO médica (prefixos do a09: 2251, 2252, 2253 e 2231).

O cache do a09 não serve: guarda horas, mas não o registro do conselho. O cache da X1 guarda o registro,
mas só em seis competências e sem horas. Por isso o a16 baixa as 27 competências mensais de novo.

Fluxo (``--etapa``)
-------------------
- ``verificar`` (padrão, usado pelo ``run_all.py``): confere as saídas versionadas contra o manifesto,
  sem rede e sem gravar nada;
- ``baixar``: por competência, baixa o ZIP para ``cache_privado/zip/`` (ou reaproveita ZIP íntegro),
  extrai os vínculos médicos com registro para ``cache_privado/``, grava o metadado (URL, data, SHA-256,
  tamanho, tempo) e apaga o ZIP. Idempotente e retomável;
- ``consolidar``: refaz a ligação da X1 a partir do cache, confere que ela reproduz
  ``output/rdd_bolsa/X1_medicos.parquet``, monta o painel só para as chaves necessárias e grava as saídas;
- ``tudo``: ``baixar`` + ``consolidar``.

Chave pseudônima (convenção da X1)
-----------------------------------
A chave do painel é ``id_prof`` (``g5p_NNNNN``): a ordem do SHA-256 de ``CO_PROFISSIONAL_SUS`` dentro da
união das chaves de uma consolidação, calculada só em memória, como o ``id_medico`` da X1. O código do
profissional, o CRM, a UF do CRM, o nome, o CPF e o CNS não saem de ``cache_privado/`` (ignorado pelo
Git). ``chaves_origem.parquet`` liga ``id_prof`` aos pseudônimos de origem (``id_medico`` da X1, por regra
de ligação). Para juntar o G1: o G1 grava, no seu próprio cache ignorado pelo Git, um parquet com
``origem``, ``id_externo`` e ``co_profissional_sus``; ``--chaves-extra <arquivo>`` na consolidação
acrescenta essas chaves. O ``id_prof`` é renumerado a cada consolidação: painel e tabela de chaves saem
juntos e só se juntam entre si.

Integridade: nada é simulado, imputado ou digitado. Competência não obtida fica sem linhas, com o motivo
no manifesto. Hora vazia é ausente, nunca zero (regra do a09). Zero só existe em competência lida com
sucesso, para quem não tem vínculo médico nela. Toda saída tem ``natureza_dos_dados = EMPIRICO``.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import importlib.util
import json
import shutil
import sys
import threading
import time
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
OUT_AQ = ROOT / "output" / "aquisicao"
OUT_DIR = OUT_AQ / "cnes_profissional"
PRIV = OUT_DIR / "cache_privado"  # ignorado pelo Git: registro do conselho, código do profissional, nomes
ZIP_DIR = PRIV / "zip"
PAINEL_MEDICO = OUT_DIR / "painel_medico_mes.parquet"
PAINEL_VINCULO = OUT_DIR / "painel_vinculo_mes.parquet"
CHAVES = OUT_DIR / "chaves_origem.parquet"
COBERTURA = OUT_DIR / "a16_cobertura_mensal.csv"
RESUMO_MD = OUT_DIR / "a16_resumo.md"
MANIFESTO = OUT_DIR / "a16_manifesto_cnes_profissional.json"
G5_RESUMO = ROOT / "output" / "rdd_bolsa" / "G5_resumo.json"

SCRIPT_A09 = ROOT / "scripts" / "aquisicao" / "a09_adquirir_cnes_nacional.py"
SCRIPT_X1 = ROOT / "scripts" / "rdd_bolsa" / "17_ponte_pmme_cnes.py"
MANIFESTO_A09 = OUT_AQ / "a09_manifesto_cnes_nacional.json"
X1_MEDICOS = ROOT / "output" / "rdd_bolsa" / "X1_medicos.parquet"

NATUREZA = "EMPIRICO"
LIMITE_EXCLUSIVO = "202609"  # ciclo 3: nenhuma competência a partir daqui é baixada ou lida
COMPETENCIAS = [f"{a}{m:02d}" for a, i, f in ((2024, 6, 12), (2025, 1, 12), (2026, 1, 8)) for m in range(i, f + 1)]
assert len(COMPETENCIAS) == 27 and all(c < LIMITE_EXCLUSIVO for c in COMPETENCIAS)
COMPETENCIA_CODIGOS = "202608"  # tbOrgaoEmissor (código do CRM), como na X1
VERSAO_CACHE = 1
ESPACO_MINIMO_LIVRE = 3 * 1024**3
PREFIXO_ID = "g5p_"

# Colunas lidas: nome canônico -> nomes aceitos no cabeçalho.
COLUNAS_CARGA = {
    "CO_UNIDADE": ["CO_UNIDADE"],
    "CO_PROFISSIONAL_SUS": ["CO_PROFISSIONAL_SUS"],
    "CO_CBO": ["CO_CBO"],
    "TP_SUS_NAO_SUS": ["TP_SUS_NAO_SUS"],
    "IND_VINCULACAO": ["IND_VINCULACAO"],
    "TP_TERCEIRO_SIH": ["TP_TERCEIRO_SIH"],
    "TP_PRECEPTOR": ["TP_PRECEPTOR"],
    "TP_RESIDENTE": ["TP_RESIDENTE"],
    "QT_CARGA_HORARIA_AMBULATORIAL": ["QT_CARGA_HORARIA_AMBULATORIAL", "QT_CARGA_HOR_AMBULATORIAL"],
    "QT_CARGA_HOR_HOSP_SUS": ["QT_CARGA_HOR_HOSP_SUS", "QT_CARGA_HORARIA_HOSPITALAR", "QT_CARGA_HOR_HOSPITALAR"],
    "QT_CARGA_HORARIA_OUTROS": ["QT_CARGA_HORARIA_OUTROS", "QT_CARGA_HOR_OUTROS"],
    "CO_CONSELHO_CLASSE": ["CO_CONSELHO_CLASSE"],
    "NU_REGISTRO": ["NU_REGISTRO"],
    "SG_UF_CRM": ["SG_UF_CRM"],
}
CARGA_OBRIGATORIAS = ("CO_UNIDADE", "CO_PROFISSIONAL_SUS", "CO_CBO", "TP_SUS_NAO_SUS",
                      "QT_CARGA_HORARIA_AMBULATORIAL", "QT_CARGA_HOR_HOSP_SUS", "QT_CARGA_HORARIA_OUTROS",
                      "CO_CONSELHO_CLASSE", "NU_REGISTRO", "SG_UF_CRM")
COLUNAS_ESTAB = {
    "CO_UNIDADE": ["CO_UNIDADE"],
    "CO_CNES": ["CO_CNES"],
    "CO_MUNICIPIO_GESTOR": ["CO_MUNICIPIO_GESTOR", "CO_MUNICIPIO"],
    "TP_GESTAO": ["TP_GESTAO"],
    "TP_UNIDADE": ["TP_UNIDADE"],
    "CO_NATUREZA_JUR": ["CO_NATUREZA_JUR"],
}
ESTAB_OBRIGATORIAS = ("CO_UNIDADE", "CO_CNES", "CO_MUNICIPIO_GESTOR")

COLS_CACHE = ["competencia", "co_unidade", "co_cnes", "co_municipio", "co_profissional_sus", "co_cbo",
              "tp_sus_nao_sus", "ind_vinculacao", "tp_terceiro_sih", "tp_preceptor", "tp_residente",
              "qt_ch_ambulatorial", "qt_ch_hosp_sus", "qt_ch_outros",
              "co_conselho_classe", "nu_registro", "sg_uf_crm", "tp_gestao", "tp_unidade", "co_natureza_jur"]
HORAS = ("qt_ch_ambulatorial", "qt_ch_hosp_sus", "qt_ch_outros")

# Saídas versionadas: o que pode e o que não pode aparecer.
COLS_VINCULO = ["id_prof", "competencia", "co_cnes", "co_municipio", "co_cbo", "tp_sus_nao_sus", "ind_vinculacao",
                "tp_terceiro_sih", "tp_preceptor", "tp_residente", "qt_ch_ambulatorial", "qt_ch_hosp_sus",
                "qt_ch_outros", "tp_gestao", "tp_unidade", "co_natureza_jur", "natureza_dos_dados"]
COLS_MEDICO = ["id_prof", "competencia", "tem_vinculo_medico", "n_vinculos", "n_vinculos_sus", "n_vinculos_nao_sus",
               "n_vinculos_tp_sus_outro", "n_estabelecimentos", "n_municipios", "n_cbo",
               "horas_amb_vinc_sus", "horas_hosp_vinc_sus", "horas_outros_vinc_sus",
               "horas_amb_vinc_nao_sus", "horas_hosp_vinc_nao_sus", "horas_outros_vinc_nao_sus",
               "horas_totais", "n_vinculos_horas_ausentes", "natureza_dos_dados"]
COLS_CHAVES = ["id_prof", "origem", "id_externo", "regra_ligacao", "natureza_dos_dados"]
COLUNAS_PROIBIDAS = ("nome", "no_profissional", "nome_norm", "cpf", "co_cpf", "cns", "co_cns", "crm",
                     "nu_registro", "sg_uf_crm", "co_profissional_sus", "co_unidade")

# Critérios do veredito, fixados antes de consolidar (antes de ver cobertura e estabilidade).
CRITERIOS = {
    "C1_competencias": "27 de 27 competências obtidas → ok; ≥ 24 com 202406 e 202608 → parcial; menos → falha",
    "C2_registro_por_vinculo": ("CO_CONSELHO_CLASSE, NU_REGISTRO e SG_UF_CRM presentes em toda competência obtida e "
                                "fração de vínculos médicos com NU_REGISTRO ≥ 0,99 em cada uma → ok; colunas "
                                "presentes com fração menor → parcial; coluna ausente → falha"),
    "C3_horas": ("as três cargas horárias e TP_SUS_NAO_SUS presentes em toda competência obtida e fração de vínculos "
                 "médicos com alguma hora ausente ≤ 0,001 em cada uma → ok; colunas presentes com fração maior → "
                 "parcial; coluna ausente → falha"),
    "C4_reproducao_x1": ("a ligação refeita do cache reproduz X1_medicos.parquet (ligado, etapa e motivo) em 100% dos "
                         "registros nas duas regras → ok; senão → parcial (diferenças registradas)"),
    "C5_estabilidade_chave": ("em toda competência obtida, entre os profissionais ligados pela X1 (regra D1) com vínculo "
                              "médico, fração com vínculo que traz o CRM da lista ≥ 0,95, e fração de registros "
                              "CRM+UF que aparecem em outro código de profissional ≤ 0,01 → ok; senão → parcial"),
    "regra_do_veredito": ("VIAVEL: todos ok; INVIAVEL: C1, C2 ou C3 em falha; VIAVEL_PARCIAL: nos demais casos"),
}
LIMIARES = {"registro_min": 0.99, "hora_ausente_max": 0.001, "registro_igual_min": 0.95, "outro_codigo_max": 0.01,
            "competencias_min_parcial": 24}

_trava_disco = threading.Lock()
_trava_extracao = threading.Lock()  # uma extração por vez: memória compartilhada da máquina


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


_trava_import = threading.RLock()  # os downloads correm em threads: o módulo só é publicado depois de carregado
_modulos: dict[str, Any] = {}


def _importar(nome: str, caminho: Path):
    with _trava_import:
        if nome in _modulos:
            return _modulos[nome]
        bytecode = sys.dont_write_bytecode
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location(nome, caminho)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nome] = mod
        spec.loader.exec_module(mod)
        sys.dont_write_bytecode = bytecode
        _modulos[nome] = mod
        return mod


def a09():
    return _importar("a09_adquirir_cnes_nacional_a16", SCRIPT_A09)


def x1():
    return _importar("ponte_pmme_cnes_17_a16", SCRIPT_X1)


def sha256_arquivo(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while bloco := f.read(4 * 1024 * 1024):
            h.update(bloco)
    return h.hexdigest()


def rel(p: Path) -> str:
    return p.resolve().relative_to(ROOT).as_posix()


def checar_limite(comp: str) -> None:
    if comp >= LIMITE_EXCLUSIVO:
        raise RuntimeError(f"competência {comp} >= {LIMITE_EXCLUSIVO} é vedada (ciclo 3)")


def caminho_zip(comp: str) -> Path:
    return ZIP_DIR / f"BASE_DE_DADOS_CNES_{comp}.ZIP"


def caminho_cache(comp: str) -> Path:
    return PRIV / f"vinculos_medicos_registro_{comp}.parquet"


def caminho_nomes(comp: str) -> Path:
    return PRIV / f"nomes_registro_alvo_{comp}.parquet"


def caminho_meta(comp: str) -> Path:
    return PRIV / f"meta_{comp}.json"


def caminho_orgao_emissor() -> Path:
    return PRIV / f"tbOrgaoEmissor_{COMPETENCIA_CODIGOS}.csv"


def competencias_x1() -> tuple[str, ...]:
    comps = tuple(x1().COMPETENCIAS)
    assert set(comps) <= set(COMPETENCIAS)
    return comps


# ---------------------------------------------------------------- download

def esperar_disco() -> None:
    while True:
        with _trava_disco:
            livre = shutil.disk_usage(ZIP_DIR).free
        if livre >= ESPACO_MINIMO_LIVRE:
            return
        log(f"  disco com {livre / 1024**3:.1f} GB livres; aguardando antes de novo download")
        time.sleep(60)


def baixar(comp: str, tentativas: int = 6, timeout: int = 300) -> dict[str, Any]:
    """Baixa e testa o ZIP (ou reaproveita ZIP local íntegro); devolve a proveniência."""
    checar_limite(comp)
    A = a09()
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    destino = caminho_zip(comp)
    url = A.URL_BASE + destino.name
    if destino.exists():
        try:
            A.testar_zip(destino)
            log(f"  {comp}: ZIP local íntegro reaproveitado")
            return {"url": url, "data_download": dt.datetime.fromtimestamp(destino.stat().st_mtime).date().isoformat(),
                    "sha256_zip": sha256_arquivo(destino), "bytes_zip": destino.stat().st_size,
                    "tentativas_download": 0, "segundos_download": None,
                    "nota_download": ("ZIP já presente em cache_privado/zip, baixado fora desta execução (em 19/10/2026, "
                                      "o teste de viabilidade com curl); sem tempo de download medido")}
        except Exception as exc:  # noqa: BLE001
            log(f"  {comp}: ZIP local inválido ({exc}); baixando de novo")
            destino.unlink()
    ultimo, nao_zip = "", 0
    for tentativa in range(1, tentativas + 1):
        esperar_disco()
        t0 = time.time()
        try:
            log(f"  {comp}: download, tentativa {tentativa}/{tentativas}")
            sha, tamanho = A._baixar_uma_vez(comp, destino, timeout)
            A.testar_zip(destino)
            return {"url": url, "data_download": dt.date.today().isoformat(), "sha256_zip": sha, "bytes_zip": tamanho,
                    "tentativas_download": tentativa, "segundos_download": round(time.time() - t0, 1)}
        except A.Indisponivel as exc:
            nao_zip += 1
            ultimo = str(exc)
            if nao_zip >= 3:
                raise
        except Exception as exc:  # noqa: BLE001
            ultimo = f"{type(exc).__name__}: {exc}"
            log(f"  {comp}: falha ({ultimo})")
        for p in (destino, destino.with_suffix(".ZIP.part")):
            if p.exists():
                p.unlink()
        time.sleep(min(30 * 2 ** (tentativa - 1), 600))
    raise RuntimeError(f"download falhou após {tentativas} tentativas: {ultimo}")


# ---------------------------------------------------------------- extração

def _mapear(cab: list[str], spec: dict[str, list[str]]) -> dict[str, str]:
    mapa = {}
    for canon, nomes in spec.items():
        for nome in nomes:
            if nome in cab:
                mapa[canon] = nome
                break
    return mapa


def _ler(zf: zipfile.ZipFile, membro: str, colunas: set[str], chunksize: int | None = None):
    return pd.read_csv(zf.open(membro), sep=";", encoding="latin1", dtype=str, keep_default_na=False, na_values=[],
                       usecols=lambda c: c.strip().strip('"').upper() in colunas, chunksize=chunksize)


def _txt(m: pd.DataFrame, canon: str) -> pd.Series:
    if canon not in m:
        return pd.Series(pd.NA, index=m.index, dtype="string")
    s = m[canon].astype("string").str.strip()
    return s.mask(s == "")


def extrair(comp: str, zip_path: Path, alvo: set[str], com_nomes: bool) -> tuple[pd.DataFrame, pd.DataFrame | None,
                                                                                 dict[str, Any]]:
    """Vínculos médicos com registro e horas; nomes só do alvo (CRMs das listas) e só se `com_nomes`."""
    checar_limite(comp)
    A, X = a09(), x1()
    t0 = time.time()
    meta: dict[str, Any] = {}
    with zipfile.ZipFile(zip_path) as zf:
        membros = {"carga": A._membro(zf, "tbCargaHorariaSus"), "estab": A._membro(zf, "tbEstabelecimento")}
        if com_nomes:
            membros["profissional"] = A._membro(zf, "tbDadosProfissionalSus")
        if comp == COMPETENCIA_CODIGOS:
            membros["orgao_emissor"] = A._membro(zf, "tbOrgaoEmissor")
        meta["membros_lidos"] = membros
        meta["n_membros_zip"] = len(zf.namelist())
        cab_carga, cab_estab = A._cabecalho(zf, membros["carga"]), A._cabecalho(zf, membros["estab"])
        mc, me = _mapear(cab_carga, COLUNAS_CARGA), _mapear(cab_estab, COLUNAS_ESTAB)
        faltam = [c for c in CARGA_OBRIGATORIAS if c not in mc] + [c for c in ESTAB_OBRIGATORIAS if c not in me]
        if faltam:
            raise RuntimeError(f"{comp}: colunas obrigatórias ausentes: {faltam}")
        meta["colunas_tbCargaHorariaSus"] = cab_carga
        meta["colunas_tbEstabelecimento"] = cab_estab
        meta["colunas_opcionais_ausentes"] = sorted([c for c in COLUNAS_CARGA if c not in mc]
                                                    + [c for c in COLUNAS_ESTAB if c not in me])

        estab = _ler(zf, membros["estab"], set(me.values()))
        estab.columns = [c.strip().strip('"').upper() for c in estab.columns]
        estab = estab.rename(columns={v: k for k, v in me.items()})
        estab["CO_UNIDADE"] = estab["CO_UNIDADE"].str.strip()
        meta["linhas_tbEstabelecimento"] = int(len(estab))
        meta["co_unidade_duplicados_estab"] = int(estab["CO_UNIDADE"].duplicated().sum())
        estab = estab.drop_duplicates("CO_UNIDADE")

        partes, linhas = [], 0
        for bloco in _ler(zf, membros["carga"], set(mc.values()), chunksize=1_000_000):
            bloco.columns = [c.strip().strip('"').upper() for c in bloco.columns]
            linhas += len(bloco)
            cbo = bloco[mc["CO_CBO"]].str.strip()
            partes.append(bloco.loc[cbo.str.startswith(A.PREFIXOS_MEDICOS)])
        meta["linhas_tbCargaHorariaSus"] = int(linhas)
        carga = pd.concat(partes, ignore_index=True).rename(columns={v: k for k, v in mc.items()})
        del partes
        carga["CO_UNIDADE"] = carga["CO_UNIDADE"].str.strip()
        m = carga.merge(estab, on="CO_UNIDADE", how="left", validate="many_to_one").reset_index(drop=True)
        del carga
        n = len(m)
        horas, cont_horas = {}, {}
        for canon, col in (("QT_CARGA_HORARIA_AMBULATORIAL", "qt_ch_ambulatorial"),
                           ("QT_CARGA_HOR_HOSP_SUS", "qt_ch_hosp_sus"), ("QT_CARGA_HORARIA_OUTROS", "qt_ch_outros")):
            horas[col], cont_horas[canon] = A._horas(m.get(canon), n)
        df = pd.DataFrame({
            "competencia": pd.Series([comp] * n, dtype="string"),
            "co_unidade": _txt(m, "CO_UNIDADE"),
            "co_cnes": _txt(m, "CO_CNES").str.replace(r"\D", "", regex=True).str.zfill(7),
            "co_municipio": _txt(m, "CO_MUNICIPIO_GESTOR").str.replace(r"\D", "", regex=True).str[:6],
            "co_profissional_sus": _txt(m, "CO_PROFISSIONAL_SUS"),
            "co_cbo": _txt(m, "CO_CBO"),
            "tp_sus_nao_sus": _txt(m, "TP_SUS_NAO_SUS"),
            "ind_vinculacao": _txt(m, "IND_VINCULACAO"),
            "tp_terceiro_sih": _txt(m, "TP_TERCEIRO_SIH"),
            "tp_preceptor": _txt(m, "TP_PRECEPTOR"),
            "tp_residente": _txt(m, "TP_RESIDENTE"),
            **horas,
            "co_conselho_classe": _txt(m, "CO_CONSELHO_CLASSE"),
            "nu_registro": X.registro_norm(m["NU_REGISTRO"]).astype("string"),
            "sg_uf_crm": _txt(m, "SG_UF_CRM").str.upper(),
            "tp_gestao": _txt(m, "TP_GESTAO"),
            "tp_unidade": _txt(m, "TP_UNIDADE"),
            "co_natureza_jur": _txt(m, "CO_NATUREZA_JUR"),
        })[COLS_CACHE]
        del m
        df = df.sort_values(["co_profissional_sus", "co_unidade", "co_cbo"], kind="mergesort").reset_index(drop=True)

        nomes = None
        if com_nomes:
            prof_alvo = set(df.loc[df["nu_registro"].isin(alvo), "co_profissional_sus"].dropna())
            partes_n = []
            for bloco in _ler(zf, membros["profissional"], {"CO_PROFISSIONAL_SUS", "NO_PROFISSIONAL"},
                              chunksize=1_000_000):
                bloco.columns = [c.strip().strip('"').upper() for c in bloco.columns]
                cod = bloco["CO_PROFISSIONAL_SUS"].str.strip()
                sel = bloco.loc[cod.isin(prof_alvo)]
                partes_n.append(pd.DataFrame({"competencia": comp, "co_profissional_sus": cod[sel.index].astype("string"),
                                              "nome_norm": sel["NO_PROFISSIONAL"].map(X.texto_norm).astype("string")}))
            nomes = pd.concat(partes_n, ignore_index=True).drop_duplicates().sort_values("co_profissional_sus")
            nomes = nomes.reset_index(drop=True)
            meta["profissionais_com_registro_no_alvo"] = len(prof_alvo)
            meta["profissionais_alvo_com_nome"] = int(nomes["co_profissional_sus"].nunique())
        if comp == COMPETENCIA_CODIGOS:
            tb = pd.read_csv(zf.open(membros["orgao_emissor"]), sep=";", encoding="latin1", dtype=str,
                             keep_default_na=False)
            tb.columns = [c.strip().strip('"').upper() for c in tb.columns]
            PRIV.mkdir(parents=True, exist_ok=True)
            tb.to_csv(caminho_orgao_emissor(), index=False)
            meta["tbOrgaoEmissor_linhas"] = int(len(tb))

    meta["linhas_vinculos_medicos"] = int(len(df))
    meta["vinculos_medicos_por_familia_cbo"] = {k: int(v) for k, v in df["co_cbo"].str[:4].value_counts().sort_index().items()}
    meta["vinculos_sem_estabelecimento"] = int(df["co_municipio"].isna().sum())
    meta["vinculos_sem_co_profissional_sus"] = int(df["co_profissional_sus"].isna().sum())
    meta["vinculos_sem_registro"] = int(df["nu_registro"].isna().sum())
    meta["vinculos_sem_uf_crm"] = int(df["sg_uf_crm"].isna().sum())
    meta["fracao_vinculos_com_registro"] = float(df["nu_registro"].notna().mean()) if len(df) else None
    meta["conselho_classe_dos_vinculos_medicos"] = {
        str(k): int(v) for k, v in df["co_conselho_classe"].fillna("<NA>").value_counts().sort_index().items()}
    meta["tp_sus_nao_sus_dos_vinculos_medicos"] = {
        str(k): int(v) for k, v in df["tp_sus_nao_sus"].fillna("<NA>").value_counts().sort_index().items()}
    meta["horas_ausentes_por_campo"] = cont_horas
    aus = df[list(HORAS)].isna().any(axis=1)
    meta["vinculos_com_alguma_hora_ausente"] = int(aus.sum())
    meta["fracao_vinculos_com_alguma_hora_ausente"] = float(aus.mean()) if len(df) else None
    meta["profissionais_distintos"] = int(df["co_profissional_sus"].nunique())
    meta["municipios_distintos"] = int(df["co_municipio"].nunique())
    meta["estabelecimentos_distintos"] = int(df["co_cnes"].nunique())
    meta["segundos_extracao"] = round(time.time() - t0, 1)
    return df, nomes, meta


def processar(comp: str, alvo: set[str], assinatura: str, ref_a09: dict[str, Any]) -> dict[str, Any]:
    """Download → teste → extração → validação → cache → apaga ZIP. Idempotente."""
    checar_limite(comp)
    com_nomes = comp in competencias_x1()
    if caminho_meta(comp).exists() and caminho_cache(comp).exists():
        meta = json.loads(caminho_meta(comp).read_text(encoding="utf-8"))
        ok = meta.get("versao_cache") == VERSAO_CACHE and meta.get("status") == "extraido_zip_apagado"
        if ok and (not com_nomes or (meta.get("assinatura_alvo") == assinatura and caminho_nomes(comp).exists())):
            if comp != COMPETENCIA_CODIGOS or caminho_orgao_emissor().exists():
                return meta
    try:
        info = baixar(comp)
    except Exception as exc:  # noqa: BLE001
        return {"competencia": comp, "status": "falha_download", "erro": f"{type(exc).__name__}: {exc}",
                "data_tentativa": dt.date.today().isoformat()}
    try:
        with _trava_extracao:
            log(f"  {comp}: extraindo")
            df, nomes, meta = extrair(comp, caminho_zip(comp), alvo, com_nomes)
    except Exception as exc:  # noqa: BLE001
        log(f"  {comp}: FALHA NA EXTRAÇÃO, ZIP mantido: {exc}")
        return {"competencia": comp, "status": "falha_extracao", "erro": f"{type(exc).__name__}: {exc}", **info}
    ref = ref_a09.get(comp, {})
    validacao = {"sha256_zip_a09": ref.get("sha256_zip"), "sha256_igual_ao_a09": info["sha256_zip"] == ref.get("sha256_zip"),
                 "linhas_vinculos_medicos_a09": ref.get("linhas_vinculos_medicos"),
                 "linhas_vinculos_medicos_a16": meta["linhas_vinculos_medicos"]}
    validacao["linhas_iguais_ao_a09"] = validacao["linhas_vinculos_medicos_a09"] == meta["linhas_vinculos_medicos"]
    falha = None
    if validacao["sha256_igual_ao_a09"] and not validacao["linhas_iguais_ao_a09"]:
        falha = "mesmo ZIP do a09, mas a contagem de vínculos médicos difere"  # extrator divergente: fail closed
    elif meta["linhas_vinculos_medicos"] < a09().MIN_VINCULOS_MEDICOS_MES:
        falha = f"extração implausível ({meta['linhas_vinculos_medicos']} vínculos médicos)"
    if falha:
        log(f"  {comp}: REPROVADA ({falha}); ZIP mantido")
        return {"competencia": comp, "status": "falha_validacao", "erro": falha, **info, **meta,
                "validacao_contra_a09": validacao}
    PRIV.mkdir(parents=True, exist_ok=True)
    tmp = caminho_cache(comp).with_suffix(".parquet.tmp")
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), tmp, compression="zstd")
    tmp.replace(caminho_cache(comp))
    if nomes is not None:
        nomes.to_parquet(caminho_nomes(comp), index=False)
    registro = {"competencia": comp, "versao_cache": VERSAO_CACHE, "status": "extraido_zip_apagado",
                "arquivo": caminho_zip(comp).name, **info, **meta, "validacao_contra_a09": validacao,
                "assinatura_alvo": assinatura if com_nomes else None,
                "data_processamento": dt.date.today().isoformat()}
    caminho_meta(comp).write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    caminho_zip(comp).unlink()
    log(f"  {comp}: OK — {meta['linhas_vinculos_medicos']:,} vínculos médicos; ZIP apagado")
    return registro


def etapa_baixar(competencias: list[str], workers: int) -> dict[str, dict[str, Any]]:
    X = x1()
    listas, _ = X.ler_listas_pmme()
    alvo = X.crms_alvo(listas)
    assinatura = X.assinatura_alvo(alvo)
    ref = json.loads(MANIFESTO_A09.read_text(encoding="utf-8")).get("por_competencia", {})
    log(f"Aquisição de {len(competencias)} competências com {workers} downloads simultâneos")
    resultados: dict[str, dict[str, Any]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(processar, c, alvo, assinatura, ref): c for c in competencias}
        for fut in concurrent.futures.as_completed(futs):
            c = futs[fut]
            try:
                resultados[c] = fut.result()
            except Exception as exc:  # noqa: BLE001
                resultados[c] = {"competencia": c, "status": "erro", "erro": f"{type(exc).__name__}: {exc}"}
            log(f"{c}: {resultados[c]['status']}")
            if resultados[c]["status"] != "extraido_zip_apagado":
                # falha fica registrada no cache privado para o manifesto (sem dado pessoal)
                PRIV.mkdir(parents=True, exist_ok=True)
                (PRIV / f"falha_{c}.json").write_text(json.dumps(resultados[c], ensure_ascii=False, indent=2) + "\n",
                                                      encoding="utf-8")
            elif (PRIV / f"falha_{c}.json").exists():
                (PRIV / f"falha_{c}.json").unlink()
    return resultados


# ---------------------------------------------------------------- consolidação

def ler_registros() -> dict[str, dict[str, Any]]:
    regs = {}
    for c in COMPETENCIAS:
        if caminho_meta(c).exists():
            regs[c] = json.loads(caminho_meta(c).read_text(encoding="utf-8"))
        elif (PRIV / f"falha_{c}.json").exists():
            regs[c] = json.loads((PRIV / f"falha_{c}.json").read_text(encoding="utf-8"))
    return regs


def codigo_conselho_crm() -> tuple[str, dict[str, Any]]:
    """Mesma regra da X1: na tbOrgaoEmissor, descrição com MEDICINA e CONSELHO REGIONAL e sem VETERINARIA."""
    X = x1()
    if not caminho_orgao_emissor().exists():
        raise SystemExit(f"tbOrgaoEmissor de {COMPETENCIA_CODIGOS} ausente do cache; rode --etapa baixar (fail closed)")
    tb = pd.read_csv(caminho_orgao_emissor(), dtype=str, keep_default_na=False)
    desc = tb["DS_ORGAO_EMISSOR"].map(X.texto_norm)
    crm = tb[desc.str.contains("MEDICINA") & desc.str.contains("CONSELHO REGIONAL") & ~desc.str.contains("VETERINARIA")]
    if len(crm) != 1:
        raise AssertionError(f"tbOrgaoEmissor: esperado um código de CRM, achados {len(crm)}")
    codigo = str(crm["CO_ORGAO_EMISSOR"].iloc[0]).strip()
    return codigo, {"codigo_crm": codigo, "descricao": str(crm["DS_ORGAO_EMISSOR"].iloc[0]).strip(),
                    "competencia": COMPETENCIA_CODIGOS, "regra": "a da X1 (17_ponte_pmme_cnes.codigo_conselho_crm)"}


def _ler_cache(comp: str, colunas: list[str], filtros=None) -> pd.DataFrame:
    df = pq.read_table(caminho_cache(comp), columns=colunas, filters=filtros).to_pandas()
    return df.astype({c: ("Int32" if c in HORAS else "string") for c in colunas})


def refazer_ligacao_x1(listas: pd.DataFrame, conselho: str) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    """A ligação da X1, com a função `ligar` da própria X1, sobre o cache do a16 nas seis competências da X1."""
    X = x1()
    alvo = sorted(X.crms_alvo(listas))
    vinc, nomes = [], []
    for c in competencias_x1():
        vinc.append(_ler_cache(c, ["competencia", "co_profissional_sus", "co_conselho_classe", "nu_registro",
                                   "sg_uf_crm"], [("nu_registro", "in", alvo)]))
        nomes.append(pd.read_parquet(caminho_nomes(c)).astype("string"))
    vinc_df = pd.concat(vinc, ignore_index=True)
    nomes_df = pd.concat(nomes, ignore_index=True)
    ligs, diag = {}, {}
    for regra, exigir in X.REGRAS.items():
        lig, dg = X.ligar(listas, vinc_df, nomes_df, conselho_crm=conselho, exigir_nome_etapa1=exigir)
        ligs[regra] = listas[["id_medico", "crm"]].merge(lig, on="id_medico", validate="one_to_one")
        dg.pop("vinculos_medicos_fora_do_conselho_crm_excluidos_da_busca", None)  # busca já restrita ao alvo
        diag[regra] = dg
    return ligs, diag


def comparar_com_x1(ligs: dict[str, pd.DataFrame]) -> dict[str, Any]:
    ref = pd.read_parquet(X1_MEDICOS, columns=["id_medico", "regra_ligacao", "ligado", "etapa_ligacao",
                                               "motivo_ligacao"])
    out: dict[str, Any] = {"arquivo": rel(X1_MEDICOS), "sha256": sha256_arquivo(X1_MEDICOS), "por_regra": {}}
    for regra, lig in ligs.items():
        r = ref[ref["regra_ligacao"] == regra].set_index("id_medico")
        n = lig.set_index("id_medico")
        comuns = r.index.intersection(n.index)
        a = pd.DataFrame({
            "ligado": (n.loc[comuns, "co_profissional_sus"].notna().astype(int) == r.loc[comuns, "ligado"].astype(int)),
            "etapa": (n.loc[comuns, "etapa_ligacao"].astype("string").fillna("")
                      == r.loc[comuns, "etapa_ligacao"].astype("string").fillna("")),
            "motivo": n.loc[comuns, "motivo"].astype("string") == r.loc[comuns, "motivo_ligacao"].astype("string"),
        })
        iguais = a.all(axis=1)
        out["por_regra"][regra] = {
            "registros_x1": int(len(r)), "registros_a16": int(len(n)), "registros_comuns": int(len(comuns)),
            "registros_identicos": int(iguais.sum()), "ligados_a16": int(n["co_profissional_sus"].notna().sum()),
            "ligados_x1": int(r["ligado"].sum()),
            "diferencas_por_campo": {k: int((~v).sum()) for k, v in a.items()},
        }
    out["reproduz_100pct"] = all(v["registros_identicos"] == v["registros_x1"] == v["registros_a16"]
                                 for v in out["por_regra"].values())
    return out


def ler_chaves_extra(caminho: Path | None) -> tuple[pd.DataFrame, dict[str, Any] | None]:
    vazio = pd.DataFrame(columns=["origem", "id_externo", "regra_ligacao", "co_profissional_sus"], dtype="string")
    if caminho is None:
        return vazio, None
    df = pd.read_parquet(caminho).astype("string")
    falta = {"origem", "id_externo", "co_profissional_sus"} - set(df.columns)
    if falta:
        raise SystemExit(f"--chaves-extra sem as colunas {sorted(falta)}")
    if "regra_ligacao" not in df:
        df["regra_ligacao"] = pd.NA
    df = df.dropna(subset=["co_profissional_sus"])[["origem", "id_externo", "regra_ligacao", "co_profissional_sus"]]
    return df, {"arquivo": str(caminho), "sha256": sha256_arquivo(caminho), "linhas": int(len(df)),
                "origens": sorted(df["origem"].dropna().unique().tolist())}


def atribuir_ids(chaves: pd.DataFrame) -> dict[str, str]:
    """Convenção da X1: ordem do SHA-256 da chave, só em memória."""
    h = {p: hashlib.sha256(str(p).encode()).hexdigest() for p in chaves["co_profissional_sus"].dropna().unique()}
    ordem = sorted(h, key=lambda p: h[p])
    return {p: f"{PREFIXO_ID}{i + 1:05d}" for i, p in enumerate(ordem)}


def _soma_na(valores: pd.Series, mascara: pd.Series, grupo: pd.Series) -> pd.Series:
    """Soma por grupo das horas dos vínculos da máscara; ausente se algum deles tem hora ausente."""
    v = valores.where(mascara)
    soma = v.fillna(0).groupby(grupo, sort=False).sum()
    tem_na = (valores.isna() & mascara).groupby(grupo, sort=False).any()
    return soma.astype("Int64").mask(tem_na)


def agregar_medico_mes(vinc: pd.DataFrame, ids: list[str], competencias: list[str]) -> pd.DataFrame:
    """Uma linha por id_prof × competência obtida; zero só para quem não tem vínculo médico na competência lida."""
    v = vinc.copy()
    tp = v["tp_sus_nao_sus"].astype("string").fillna("")
    sus, nao = (tp == "S"), (tp == "N")
    chave = v["id_prof"].astype(str) + "|" + v["competencia"].astype(str)
    g = v.groupby(chave, sort=False)
    agg = pd.DataFrame({
        "n_vinculos": g.size(),
        "n_vinculos_sus": sus.groupby(chave, sort=False).sum(),
        "n_vinculos_nao_sus": nao.groupby(chave, sort=False).sum(),
        "n_estabelecimentos": g["co_cnes"].nunique(),
        "n_municipios": g["co_municipio"].nunique(),
        "n_cbo": g["co_cbo"].nunique(),
    })
    agg["n_vinculos_tp_sus_outro"] = agg["n_vinculos"] - agg["n_vinculos_sus"] - agg["n_vinculos_nao_sus"]
    for campo, rot in (("qt_ch_ambulatorial", "amb"), ("qt_ch_hosp_sus", "hosp"), ("qt_ch_outros", "outros")):
        x = v[campo].astype("Int64")
        agg[f"horas_{rot}_vinc_sus"] = _soma_na(x, sus, chave)
        agg[f"horas_{rot}_vinc_nao_sus"] = _soma_na(x, nao, chave)
    todas = sum(v[c].astype("Int64").fillna(0) for c in HORAS)
    aus = v[list(HORAS)].isna().any(axis=1)
    agg["horas_totais"] = todas.groupby(chave, sort=False).sum().astype("Int64").mask(aus.groupby(chave, sort=False).any())
    agg["n_vinculos_horas_ausentes"] = aus.groupby(chave, sort=False).sum()
    agg = agg.reset_index(names="_chave")
    esq = pd.MultiIndex.from_product([sorted(ids), sorted(competencias)], names=["id_prof", "competencia"]).to_frame(index=False)
    esq["_chave"] = esq["id_prof"] + "|" + esq["competencia"]
    p = esq.merge(agg, on="_chave", how="left", validate="one_to_one").drop(columns="_chave")
    obs = p["n_vinculos"].notna()
    for c in ("n_vinculos", "n_vinculos_sus", "n_vinculos_nao_sus", "n_vinculos_tp_sus_outro", "n_estabelecimentos",
              "n_municipios", "n_cbo", "n_vinculos_horas_ausentes"):
        p[c] = p[c].fillna(0).astype(np.int32)
    for c in [c for c in COLS_MEDICO if c.startswith("horas_")]:
        p[c] = p[c].astype("Int64").where(obs, 0).astype("Int32")
    p["tem_vinculo_medico"] = obs.astype(np.int8)
    p["natureza_dos_dados"] = NATUREZA
    return p[COLS_MEDICO].sort_values(["id_prof", "competencia"], kind="mergesort").reset_index(drop=True)


def estabilidade(lig: pd.DataFrame, regs: pd.DataFrame, conselho: str, competencias: list[str]) -> pd.DataFrame:
    """Por competência: dos profissionais ligados com vínculo médico, quantos trazem o CRM da lista no vínculo, e
    quantos registros CRM+UF aparecem num código de profissional diferente do ligado.

    `lig`: id_medico, crm, co_profissional_sus (ligados). `regs`: vínculos médicos (competencia, co_profissional_sus,
    co_conselho_classe, nu_registro, sg_uf_crm) dos profissionais ligados e dos registros das listas.
    """
    r = regs[regs["co_conselho_classe"] == conselho]
    pares = lig[["crm", "co_profissional_sus"]].drop_duplicates()
    # UF do CRM do profissional: a mais frequente nos vínculos dele com o CRM da lista (empate: ordem alfabética).
    m = r.merge(pares, left_on=["co_profissional_sus", "nu_registro"], right_on=["co_profissional_sus", "crm"])
    uf = (m.dropna(subset=["sg_uf_crm"]).groupby(["co_profissional_sus", "crm", "sg_uf_crm"]).size().reset_index(name="n")
          .sort_values(["co_profissional_sus", "crm", "n", "sg_uf_crm"], ascending=[True, True, False, True])
          .drop_duplicates(["co_profissional_sus", "crm"]))
    pares = pares.merge(uf[["co_profissional_sus", "crm", "sg_uf_crm"]], on=["co_profissional_sus", "crm"], how="left")
    linhas = []
    profs = set(pares["co_profissional_sus"])
    for c in competencias:
        rc = regs[regs["competencia"] == c]
        presentes = set(rc["co_profissional_sus"]) & profs
        rcc = r[r["competencia"] == c]
        com_crm = set(rcc.merge(pares, left_on=["co_profissional_sus", "nu_registro"],
                                right_on=["co_profissional_sus", "crm"])["co_profissional_sus"])
        outros = rcc.merge(pares.dropna(subset=["sg_uf_crm"]), left_on=["nu_registro", "sg_uf_crm"],
                           right_on=["crm", "sg_uf_crm"], suffixes=("", "_ligado"))
        outros = outros[outros["co_profissional_sus"] != outros["co_profissional_sus_ligado"]]
        com_algum_crm = set(rcc.dropna(subset=["nu_registro"])["co_profissional_sus"]) & presentes
        n_pares_uf = int(pares["sg_uf_crm"].notna().sum())
        n_outro = int(outros[["crm", "sg_uf_crm", "co_profissional_sus_ligado"]].drop_duplicates().shape[0])
        linhas.append({
            "competencia": c, "profissionais_ligados": len(profs), "profissionais_com_vinculo_medico": len(presentes),
            "fracao_com_vinculo_medico": len(presentes) / len(profs) if profs else np.nan,
            "com_vinculo_e_crm_da_lista": len(com_crm & presentes),
            "fracao_com_crm_da_lista_entre_presentes": (len(com_crm & presentes) / len(presentes)) if presentes else np.nan,
            # descritivo do motivo (não entra no critério): outro número de CRM no mesmo código, ou nenhum CRM
            "com_vinculo_so_com_outro_crm": len(com_algum_crm - com_crm),
            "com_vinculo_sem_registro_crm": len(presentes - com_algum_crm),
            "registros_crm_uf_conhecidos": n_pares_uf,
            "registros_crm_uf_em_outro_codigo": n_outro,
            "fracao_registros_em_outro_codigo": (n_outro / n_pares_uf) if n_pares_uf else np.nan,
        })
    return pd.DataFrame(linhas)


def veredito(regs: dict[str, dict[str, Any]], obtidas: list[str], reproducao: dict[str, Any] | None,
             estab_d1: pd.DataFrame | None) -> dict[str, Any]:
    st: dict[str, Any] = {}
    n = len(obtidas)
    if n == len(COMPETENCIAS):
        st["C1_competencias"] = "ok"
    elif n >= LIMIARES["competencias_min_parcial"] and {"202406", "202608"} <= set(obtidas):
        st["C1_competencias"] = "parcial"
    else:
        st["C1_competencias"] = "falha"
    colunas_reg = {"CO_CONSELHO_CLASSE", "NU_REGISTRO", "SG_UF_CRM"}
    colunas_h = {"QT_CARGA_HORARIA_AMBULATORIAL", "QT_CARGA_HOR_HOSP_SUS", "QT_CARGA_HORARIA_OUTROS", "TP_SUS_NAO_SUS"}
    if not obtidas:
        st["C2_registro_por_vinculo"] = st["C3_horas"] = "falha"
    else:
        # o mapa de colunas é o mesmo da extração: obrigatórias ausentes param a extração (falha_extracao)
        frac_reg = [regs[c].get("fracao_vinculos_com_registro") or 0.0 for c in obtidas]
        frac_h = [regs[c].get("fracao_vinculos_com_alguma_hora_ausente") or 0.0 for c in obtidas]
        st["C2_registro_por_vinculo"] = "ok" if min(frac_reg) >= LIMIARES["registro_min"] else "parcial"
        st["C3_horas"] = "ok" if max(frac_h) <= LIMIARES["hora_ausente_max"] else "parcial"
        st["C2_valor_min_fracao_com_registro"] = min(frac_reg)
        st["C3_valor_max_fracao_hora_ausente"] = max(frac_h)
        st["colunas_exigidas"] = sorted(colunas_reg | colunas_h)
    if reproducao is None:
        st["C4_reproducao_x1"] = "parcial"
    else:
        st["C4_reproducao_x1"] = "ok" if reproducao["reproduz_100pct"] else "parcial"
    if estab_d1 is None or estab_d1.empty:
        st["C5_estabilidade_chave"] = "parcial"
    else:
        mi = float(estab_d1["fracao_com_crm_da_lista_entre_presentes"].min())
        ma = float(estab_d1["fracao_registros_em_outro_codigo"].max())
        st["C5_valor_min_fracao_com_crm_da_lista"] = mi
        st["C5_valor_max_fracao_em_outro_codigo"] = ma
        st["C5_estabilidade_chave"] = ("ok" if mi >= LIMIARES["registro_igual_min"] and ma <= LIMIARES["outro_codigo_max"]
                                       else "parcial")
    criterios = ["C1_competencias", "C2_registro_por_vinculo", "C3_horas", "C4_reproducao_x1", "C5_estabilidade_chave"]
    if any(st[c] == "falha" for c in criterios[:3]):
        v = "INVIAVEL"
    elif all(st[c] == "ok" for c in criterios):
        v = "VIAVEL"
    else:
        v = "VIAVEL_PARCIAL"
    return {"veredito": v, "status_por_criterio": st}


def etapa_consolidar(chaves_extra: Path | None) -> int:
    X = x1()
    regs = ler_registros()
    obtidas = [c for c in COMPETENCIAS if regs.get(c, {}).get("status") == "extraido_zip_apagado"
               and caminho_cache(c).exists()]
    for c in obtidas:
        checar_limite(c)
    nao_obtidas = {c: {"status": regs.get(c, {}).get("status", "nao_processada"), "erro": regs.get(c, {}).get("erro")}
                   for c in COMPETENCIAS if c not in obtidas}
    if not obtidas:
        raise SystemExit("nenhuma competência no cache; rode --etapa baixar")
    listas, diag_listas = X.ler_listas_pmme()
    alvo = X.crms_alvo(listas)
    assinatura = X.assinatura_alvo(alvo)
    conselho, diag_conselho = codigo_conselho_crm()

    reproducao, diag_lig, ligs = None, {}, {}
    if all(c in obtidas for c in competencias_x1()):
        if any(regs[c].get("assinatura_alvo") != assinatura for c in competencias_x1()):
            raise SystemExit("listas do PMM-E mudaram desde a extração dos nomes; refaça --etapa baixar (fail closed)")
        ligs, diag_lig = refazer_ligacao_x1(listas, conselho)
        reproducao = comparar_com_x1(ligs)
        log(f"Reprodução da X1: {'idêntica' if reproducao['reproduz_100pct'] else 'COM DIFERENÇAS'}")
    else:
        log("Competências da X1 incompletas: a ligação não pode ser refeita; só chaves extra")

    partes = []
    for regra, lig in ligs.items():
        ll = lig.dropna(subset=["co_profissional_sus"])
        partes.append(pd.DataFrame({"origem": "X1", "id_externo": ll["id_medico"].astype("string"),
                                    "regra_ligacao": regra, "co_profissional_sus": ll["co_profissional_sus"].astype("string")}))
    extra, diag_extra = ler_chaves_extra(chaves_extra)
    partes.append(extra)
    chaves = pd.concat(partes, ignore_index=True).astype("string")
    if chaves.empty:
        raise SystemExit("nenhuma chave de profissional para o painel")
    ids = atribuir_ids(chaves)
    chaves["id_prof"] = chaves["co_profissional_sus"].map(ids)
    profs = sorted(ids)

    alvo_l = sorted(alvo)
    vincs, regs_estab = [], []
    cols_v = [c for c in COLS_CACHE if c not in ("co_unidade",)]
    for c in obtidas:
        t = _ler_cache(c, cols_v, [[("co_profissional_sus", "in", profs)], [("nu_registro", "in", alvo_l)]])
        regs_estab.append(t[["competencia", "co_profissional_sus", "co_conselho_classe", "nu_registro", "sg_uf_crm"]])
        vincs.append(t[t["co_profissional_sus"].isin(set(ids))])
    vinc = pd.concat(vincs, ignore_index=True)
    regs_df = pd.concat(regs_estab, ignore_index=True)
    vinc["id_prof"] = vinc["co_profissional_sus"].map(ids).astype("string")
    for h in HORAS:
        vinc[h] = vinc[h].astype("Int32")
    vinc["natureza_dos_dados"] = NATUREZA
    painel_v = vinc[COLS_VINCULO].sort_values(["id_prof", "competencia", "co_cnes", "co_cbo", "tp_sus_nao_sus"],
                                              kind="mergesort", na_position="last").reset_index(drop=True)
    painel_m = agregar_medico_mes(painel_v, sorted(ids.values()), obtidas)

    # Cobertura e estabilidade por competência (sem quebra por ciclo, faixa, IVS ou tratamento).
    presentes = painel_m[painel_m["tem_vinculo_medico"] == 1]
    partes_cob, estab_por_regra = [], {}
    for (origem, regra), g in chaves.groupby(["origem", "regra_ligacao"], dropna=False):
        idset = set(g["id_prof"])
        cob_g = pd.DataFrame([{
            "origem": origem, "regra_ligacao": regra if pd.notna(regra) else "", "competencia": c,
            "registros_ligados": int(len(g)), "profissionais": len(idset),
            "profissionais_com_vinculo_medico": int(presentes[(presentes["competencia"] == c)
                                                              & presentes["id_prof"].isin(idset)].shape[0]),
        } for c in obtidas])
        cob_g["fracao_com_vinculo_medico"] = cob_g["profissionais_com_vinculo_medico"] / cob_g["profissionais"]
        if origem == "X1":
            e = estabilidade(ligs[regra].dropna(subset=["co_profissional_sus"]), regs_df, conselho, obtidas)
            if not (e["profissionais_com_vinculo_medico"].to_numpy()
                    == cob_g["profissionais_com_vinculo_medico"].to_numpy()).all():
                raise AssertionError(f"{regra}: presença no painel difere da contagem da estabilidade")
            estab_por_regra[regra] = e
            cob_g = cob_g.merge(e[["competencia", "com_vinculo_e_crm_da_lista",
                                   "fracao_com_crm_da_lista_entre_presentes", "com_vinculo_so_com_outro_crm",
                                   "com_vinculo_sem_registro_crm", "registros_crm_uf_conhecidos",
                                   "registros_crm_uf_em_outro_codigo", "fracao_registros_em_outro_codigo"]],
                                on="competencia", how="left", validate="one_to_one")
        partes_cob.append(cob_g)
    cob = pd.concat(partes_cob, ignore_index=True)
    cob["natureza_dos_dados"] = NATUREZA
    cob = cob.sort_values(["origem", "regra_ligacao", "competencia"]).reset_index(drop=True)

    chaves_out = chaves.assign(natureza_dos_dados=NATUREZA)[COLS_CHAVES].sort_values(
        ["origem", "regra_ligacao", "id_externo"], kind="mergesort").reset_index(drop=True)
    ver = veredito(regs, obtidas, reproducao, estab_por_regra.get("d1_pos_hoc"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for df, p in ((painel_v, PAINEL_VINCULO), (painel_m, PAINEL_MEDICO), (chaves_out, CHAVES)):
        pq.write_table(pa.Table.from_pandas(df, preserve_index=False), p, compression="zstd", compression_level=9)
    cob.to_csv(COBERTURA, index=False)
    gravar_manifesto(regs, obtidas, nao_obtidas, painel_v, painel_m, chaves_out, reproducao, diag_lig, diag_listas,
                     diag_conselho, diag_extra, ver, chaves_extra)
    gravar_g5(regs, obtidas, nao_obtidas, cob, ver, reproducao, painel_m)
    gravar_resumo(regs, cob, ver)
    log(f"Painel vínculo-mês: {len(painel_v):,} linhas; médico-mês: {len(painel_m):,}; veredito {ver['veredito']}")
    return 0


# ---------------------------------------------------------------- manifesto e resumos

def _entradas(chaves_extra: Path | None) -> dict[str, Any]:
    X = x1()
    itens = [
        (X.ATIVOS_ZIP, "lista nominal de ativos do PMM-E (CRM, UF do posto, nome só em memória), via X1"),
        (X.NOMINAL_CSV, "lista nominal de 12/08/2026 (registros só dela entram), via X1"),
        (X1_MEDICOS, "conferência: a ligação refeita tem de reproduzir ligado, etapa e motivo da X1"),
        (MANIFESTO_A09, "conferência: SHA-256 do ZIP e contagem de vínculos médicos do a09 por competência"),
        (SCRIPT_X1, "funções da X1 importadas: ler_listas_pmme, ligar, registro_norm, texto_norm"),
        (SCRIPT_A09, "funções do a09 importadas: download, teste do ZIP, leitura de cabeçalho e de horas"),
    ]
    out = {rel(p): {"sha256": sha256_arquivo(p), "bytes": p.stat().st_size, "uso": uso} for p, uso in itens if p.exists()}
    if chaves_extra is not None:
        out[str(chaves_extra)] = {"sha256": sha256_arquivo(chaves_extra), "uso": "chaves extra (G1), fora do Git"}
    return out


def _saida(p: Path, df: pd.DataFrame | None = None) -> dict[str, Any]:
    d = {"arquivo": rel(p), "sha256": sha256_arquivo(p), "bytes": p.stat().st_size}
    if df is not None:
        d["linhas"] = int(len(df))
        d["colunas"] = list(df.columns)
    return d


def gravar_manifesto(regs, obtidas, nao_obtidas, painel_v, painel_m, chaves, reproducao, diag_lig, diag_listas,
                     diag_conselho, diag_extra, ver, chaves_extra) -> None:
    enxutos = {}
    for c in COMPETENCIAS:
        r = regs.get(c)
        if r is None:
            continue
        enxutos[c] = {k: v for k, v in r.items() if k not in ("colunas_tbCargaHorariaSus", "colunas_tbEstabelecimento",
                                                                "assinatura_alvo")}
        if "colunas_tbCargaHorariaSus" in r:
            enxutos[c]["colunas_lidas_presentes"] = sorted(
                set(sum(COLUNAS_CARGA.values(), [])) & set(r["colunas_tbCargaHorariaSus"])
                | set(sum(COLUNAS_ESTAB.values(), [])) & set(r["colunas_tbEstabelecimento"]))
    man = {
        "gerador": "scripts/aquisicao/a16_cnes_profissional_mensal.py",
        "plano": "docs/06_execucao/51_plano_perguntas_reformuladas.md (portão G5, T4.0; insumo de P4 e T6.2)",
        "natureza_dos_dados": NATUREZA,
        "data_execucao": dt.date.today().isoformat(),
        "fonte": {"nome": "CNES — base completa mensal (BASE_DE_DADOS_CNES_AAAAMM.ZIP), DATASUS/MS",
                  "url_modelo": a09().URL_BASE + "BASE_DE_DADOS_CNES_AAAAMM.ZIP", "referer": a09().REFERER,
                  "tabelas": {"tbCargaHorariaSus": "vínculos (profissional × estabelecimento × CBO), registro e horas",
                              "tbEstabelecimento": "CNES, município, gestão, tipo de unidade, natureza jurídica",
                              "tbDadosProfissionalSus": "nome normalizado, só alvo da X1 nas seis competências da X1 (cache privado)",
                              "tbOrgaoEmissor": f"código do CRM ({COMPETENCIA_CODIGOS})"}},
        "competencias_planejadas": COMPETENCIAS,
        "competencias_obtidas": obtidas,
        "competencias_nao_obtidas": nao_obtidas,
        "limite_ciclo3": f"nenhuma competência >= {LIMITE_EXCLUSIVO} é baixada ou lida",
        "regra_competencia_ausente": ("competência não obtida não tem linhas; nada é interpolado ou copiado de outro mês; "
                                      "zero só em competência lida, para quem não tem vínculo médico nela"),
        "filtros": {"vinculos": f"tbCargaHorariaSus com CO_CBO iniciando em {list(a09().PREFIXOS_MEDICOS)}; sem filtro "
                                "de TP_SUS_NAO_SUS, vinculação ou tipo de unidade",
                    "chaves": "profissionais (CO_PROFISSIONAL_SUS) ligados pela X1 em qualquer das duas regras, mais "
                              "as chaves extra (G1) se passadas"},
        "conselho_crm": diag_conselho,
        "listas_pmme": diag_listas,
        "reproducao_x1": reproducao,
        "diagnostico_ligacao": diag_lig,
        "chaves_extra": diag_extra,
        "pseudonimo": ("id_prof = g5p_ + ordem do SHA-256 de CO_PROFISSIONAL_SUS na união das chaves desta consolidação, "
                       "calculado só em memória (convenção da X1); renumerado a cada consolidação"),
        "dados_pessoais": ("nenhum nome, CPF, CNS, CRM, UF do CRM, CO_PROFISSIONAL_SUS ou CO_UNIDADE nas saídas; ficam "
                           "em output/aquisicao/cnes_profissional/cache_privado/ (ignorado pelo Git). O pseudônimo é "
                           "fraco: CNES, CBO e município do vínculo cruzados com o CNES público reidentificam o médico"),
        "definicoes": {
            "painel_vinculo_mes": "uma linha por linha de tbCargaHorariaSus de CBO médica do profissional na competência",
            "painel_medico_mes": "id_prof × competência obtida (balanceado); tem_vinculo_medico = 0 e contagens 0 quando "
                                 "o profissional não tem vínculo médico na competência lida",
            "horas_*_vinc_sus": "soma do campo nos vínculos com TP_SUS_NAO_SUS = 'S'; ausente se algum deles tem o campo vazio",
            "horas_*_vinc_nao_sus": "idem, vínculos com TP_SUS_NAO_SUS = 'N'",
            "campos_de_horas": {"amb": "QT_CARGA_HORARIA_AMBULATORIAL", "hosp": "QT_CARGA_HOR_HOSP_SUS",
                                "outros": "QT_CARGA_HORARIA_OUTROS"},
            "horas_totais": "soma dos três campos em todos os vínculos; ausente se algum vínculo tem algum campo vazio",
            "n_vinculos_tp_sus_outro": "vínculos com TP_SUS_NAO_SUS diferente de 'S' e 'N' (entram só em horas_totais)",
        },
        "criterios_veredito": CRITERIOS,
        "limiares": LIMIARES,
        "veredito": ver,
        "entradas_locais": _entradas(chaves_extra),
        "saidas": {"painel_vinculo_mes": _saida(PAINEL_VINCULO, painel_v), "painel_medico_mes": _saida(PAINEL_MEDICO, painel_m),
                   "chaves_origem": _saida(CHAVES, chaves), "cobertura": _saida(COBERTURA)},
        "por_competencia": enxutos,
        "cegamento": ("nenhum contraste: nada antes ou depois da entrada, por IVS, corte, faixa, ciclo ou tratamento; "
                      "o IVS não é lido"),
    }
    MANIFESTO.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gravar_g5(regs, obtidas, nao_obtidas, cob, ver, reproducao, painel_m) -> None:
    bytes_total = sum(regs[c].get("bytes_zip") or 0 for c in obtidas)
    segs = [regs[c].get("segundos_download") for c in obtidas if regs[c].get("segundos_download") is not None]
    x1_d1 = cob[(cob["origem"] == "X1") & (cob["regra_ligacao"] == "d1_pos_hoc")]
    g5 = {
        "natureza_dos_dados": NATUREZA,
        "portao": "G5",
        "plano": "docs/06_execucao/51_plano_perguntas_reformuladas.md (T4.0)",
        "script": "scripts/aquisicao/a16_cnes_profissional_mensal.py",
        "documento": "docs/auditorias/aquisicao/A16_cnes_profissional.md",
        "data_execucao": dt.date.today().isoformat(),
        "veredito": ver["veredito"],
        "status_por_criterio": ver["status_por_criterio"],
        "criterios": CRITERIOS,
        "competencias_planejadas": len(COMPETENCIAS),
        "competencias_obtidas": obtidas,
        "competencias_nao_obtidas": nao_obtidas,
        "volume": {"bytes_zip_total": int(bytes_total), "gb_zip_total": round(bytes_total / 1024**3, 2),
                   "competencias_com_tempo_medido": len(segs),
                   "segundos_download_soma": round(sum(segs), 1) if segs else None,
                   "nota": "segundos somados por conexão; os downloads correram em paralelo"},
        "reproducao_x1": ({"reproduz_100pct": reproducao["reproduz_100pct"],
                           "por_regra": {k: {kk: v[kk] for kk in ("registros_x1", "registros_identicos", "ligados_a16")}
                                         for k, v in reproducao["por_regra"].items()}} if reproducao else None),
        "painel": {"profissionais": int(painel_m["id_prof"].nunique()), "linhas_medico_mes": int(len(painel_m)),
                   "arquivo_medico_mes": rel(PAINEL_MEDICO), "arquivo_vinculo_mes": rel(PAINEL_VINCULO),
                   "arquivo_chaves": rel(CHAVES), "arquivo_cobertura": rel(COBERTURA)},
        "cobertura_x1_d1_por_competencia": [
            {k: (None if isinstance(v, float) and np.isnan(v) else v) for k, v in r.items()
             if k in ("competencia", "profissionais", "profissionais_com_vinculo_medico", "fracao_com_vinculo_medico",
                      "fracao_com_crm_da_lista_entre_presentes", "com_vinculo_so_com_outro_crm",
                      "com_vinculo_sem_registro_crm", "registros_crm_uf_em_outro_codigo")}
            for r in x1_d1.to_dict(orient="records")],
        "g1": ("pendente: o painel aceita as chaves do G1 por --chaves-extra (origem, id_externo, co_profissional_sus, "
               "num arquivo fora do Git) sem novo download; T6.2 depende do G1 e do G2"),
        "cegamento": "nenhum contraste antes/depois da entrada, por IVS, corte, faixa, ciclo ou tratamento",
    }
    G5_RESUMO.write_text(json.dumps(g5, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _f(x: Any, casas: int = 3) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/d"
    return f"{x:.{casas}f}".replace(".", ",") if isinstance(x, float) else str(x)


def gravar_resumo(regs, cob, ver) -> None:
    linhas = ["# A16 — resumo gerado (portão G5, CNES profissional mensal)", "",
              f"Gerado por `scripts/aquisicao/a16_cnes_profissional_mensal.py` em {dt.date.today().isoformat()}. "
              "Não editar à mão. Natureza dos dados: EMPIRICO. Sem contraste por IVS, corte, faixa, ciclo ou entrada.", "",
              f"**Veredito:** `{ver['veredito']}`.", "",
              "| Critério | Status |", "|---|---|"]
    for k, v in ver["status_por_criterio"].items():
        linhas.append(f"| {k} | {_f(v, 4) if isinstance(v, float) else v} |")
    linhas += ["", "## Competências", "",
               "| Competência | Status | MB do ZIP | SHA-256 (12) | SHA = a09 | s de download | Vínculos médicos | "
               "Profissionais | Fração com registro | Fração com hora ausente |",
               "|---|---|---:|---|---|---:|---:|---:|---:|---:|"]
    for c in COMPETENCIAS:
        r = regs.get(c)
        if r is None:
            linhas.append(f"| {c} | não processada | | | | | | | | |")
            continue
        val = r.get("validacao_contra_a09", {})
        mb = f"{r['bytes_zip'] / 1024**2:.1f}" if r.get("bytes_zip") else ""
        linhas.append(f"| {c} | {r.get('status')} | {mb} | `{(r.get('sha256_zip') or '')[:12]}` | "
                      f"{'sim' if val.get('sha256_igual_ao_a09') else 'não'} | {_f(r.get('segundos_download'), 0)} | "
                      f"{r.get('linhas_vinculos_medicos', '')} | {r.get('profissionais_distintos', '')} | "
                      f"{_f(r.get('fracao_vinculos_com_registro'), 4)} | {_f(r.get('fracao_vinculos_com_alguma_hora_ausente'), 5)} |")
    linhas += ["", "## Cobertura e estabilidade da chave (X1)", "",
               "Profissionais ligados com vínculo médico na competência; entre eles, fração cujo vínculo traz o CRM da "
               "lista; registros CRM+UF que aparecem em outro código de profissional. Sem quebra por ciclo ou faixa.", ""]
    for regra, g in cob.groupby("regra_ligacao"):
        linhas += [f"### {g['origem'].iloc[0]}, regra {regra}", "",
                   "| Competência | Profissionais | Com vínculo médico | Fração | Com o CRM da lista (fração entre presentes) | "
                   "Só com outro número de CRM | Sem CRM no vínculo | Registros CRM+UF em outro código |",
                   "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for r in g.itertuples(index=False):
            linhas.append(f"| {r.competencia} | {r.profissionais} | {r.profissionais_com_vinculo_medico} | "
                          f"{_f(r.fracao_com_vinculo_medico)} | {_f(getattr(r, 'fracao_com_crm_da_lista_entre_presentes', None))} | "
                          f"{_f(getattr(r, 'com_vinculo_so_com_outro_crm', None))} | "
                          f"{_f(getattr(r, 'com_vinculo_sem_registro_crm', None))} | "
                          f"{_f(getattr(r, 'registros_crm_uf_em_outro_codigo', None))} |")
        linhas.append("")
    RESUMO_MD.write_text("\n".join(linhas) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- verificação sem rede

def verificar() -> int:
    """Confere as saídas versionadas contra o manifesto, sem rede e sem gravar nada (fail closed)."""
    if not MANIFESTO.exists():
        raise SystemExit(f"verificar: {rel(MANIFESTO)} ausente; rode --etapa tudo")
    man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    erros = []
    for nome, p in (("painel_vinculo_mes", PAINEL_VINCULO), ("painel_medico_mes", PAINEL_MEDICO),
                    ("chaves_origem", CHAVES), ("cobertura", COBERTURA)):
        reg = man["saidas"].get(nome, {})
        if not p.exists():
            erros.append(f"saída ausente: {rel(p)}")
            continue
        if sha256_arquivo(p) != reg.get("sha256"):
            erros.append(f"SHA-256 de {rel(p)} difere do manifesto")
        if p.suffix == ".parquet":
            meta = pq.read_metadata(p)
            nomes = meta.schema.to_arrow_schema().names
            if meta.num_rows != reg.get("linhas") or nomes != reg.get("colunas"):
                erros.append(f"{rel(p)}: linhas ou colunas diferentes do manifesto")
            if any(c in COLUNAS_PROIBIDAS for c in nomes):
                erros.append(f"{rel(p)}: coluna com dado pessoal")
    for p, cols in ((PAINEL_VINCULO, COLS_VINCULO), (PAINEL_MEDICO, COLS_MEDICO), (CHAVES, COLS_CHAVES)):
        if p.exists() and pq.read_metadata(p).schema.to_arrow_schema().names != cols:
            erros.append(f"{rel(p)}: colunas diferentes das do script")
    if man.get("competencias_planejadas") != COMPETENCIAS:
        erros.append("plano de competências do script mudou desde a construção")
    if any(c >= LIMITE_EXCLUSIVO for c in man.get("competencias_obtidas", [])):
        erros.append("competência >= limite do ciclo 3 no manifesto")
    if PAINEL_MEDICO.exists():
        comps = set(pq.read_table(PAINEL_MEDICO, columns=["competencia"]).column("competencia").to_pylist())
        if comps != set(man.get("competencias_obtidas", [])):
            erros.append("competências do painel diferentes das obtidas no manifesto")
    for r, reg in (man.get("entradas_locais") or {}).items():
        p = ROOT / r
        if not p.exists():
            erros.append(f"entrada registrada ausente: {r}")
        elif sha256_arquivo(p) != reg.get("sha256"):
            erros.append(f"entrada mudou desde a construção: {r}")
    if not G5_RESUMO.exists():
        erros.append(f"{rel(G5_RESUMO)} ausente")
    elif json.loads(G5_RESUMO.read_text(encoding="utf-8")).get("veredito") != man["veredito"]["veredito"]:
        erros.append("veredito do G5_resumo diferente do manifesto")
    if erros:
        for e in erros:
            log(f"VERIFICAÇÃO REPROVADA: {e}")
        raise SystemExit("verificar: saídas do a16 não conferem; refaça com --etapa consolidar ou --etapa tudo")
    log(f"a16 conferido sem rede: {len(man['competencias_obtidas'])} competências, veredito "
        f"{man['veredito']['veredito']}; nada gravado")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=["verificar", "baixar", "consolidar", "tudo"], default="verificar",
                    help="verificar (padrão): confere as saídas sem rede e sem gravar; baixar: ZIPs → cache privado; "
                         "consolidar: painel a partir do cache; tudo: baixar + consolidar")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--competencias", nargs="*", help="subconjunto para --etapa baixar (teste de viabilidade)")
    ap.add_argument("--chaves-extra", type=Path, default=None,
                    help="parquet fora do Git com origem, id_externo e co_profissional_sus (por exemplo, do G1)")
    args = ap.parse_args()
    if args.etapa == "verificar":
        if args.competencias or args.chaves_extra:
            raise SystemExit("--competencias e --chaves-extra não se aplicam a --etapa verificar")
        return verificar()
    comps = sorted(args.competencias) if args.competencias else COMPETENCIAS
    for c in comps:
        checar_limite(c)
        if c not in COMPETENCIAS:
            raise SystemExit(f"competência fora do plano: {c}")
    if args.etapa in ("baixar", "tudo"):
        # os extremos primeiro: detectam cedo mudança de esquema
        ordem = sorted(comps, key=lambda c: (c not in ("202406", "202608"), c))
        etapa_baixar(ordem, args.workers)
    if args.etapa in ("consolidar", "tudo"):
        return etapa_consolidar(args.chaves_extra)
    return 0


if __name__ == "__main__":
    sys.exit(main())
