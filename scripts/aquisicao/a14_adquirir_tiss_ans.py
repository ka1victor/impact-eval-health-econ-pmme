"""a14_adquirir_tiss_ans.py — TISS/ANS: produção paga por planos, município do prestador × mês × tipo × CBO.

Tarefa a14 do protocolo de produção especializada
(``docs/06_execucao/47_protocolo_producao_especializada.md``, §2, §3, §6 e §9),
insumo de K3, K3a, K3b e K5. **Só aquisição**: este script não lê IVS, não
calcula nada por faixa da bolsa, lado de corte ou tratamento e não estima nada.

Fonte: dados abertos TISS da ANS (``https://dadosabertos.ans.gov.br/FTP/PDA/TISS/``),
conjuntos "Procedimentos Ambulatoriais por UF" e "Procedimentos Hospitalares por
UF". Cada UF × mês de realização tem dois arquivos usados aqui:
- ``<UF>_<AAAAMM>_AMB_CONS.zip`` / ``_HOSP_CONS.zip``: um registro por evento
  (``ID_EVENTO_ATENCAO_SAUDE``), com município e UF do prestador executante, mês
  de realização, modalidade da operadora e, no ambulatorial, o CBO do evento;
- ``<UF>_<AAAAMM>_AMB_DET.zip`` / ``_HOSP_DET.zip``: os itens (procedimentos) de
  cada evento, com tabela TUSS, código e quantidade informada.
O arquivo ``_REM`` (modelo de remuneração) é só listado, não baixado.

Agregação: município do prestador (6 dígitos IBGE) × mês de realização × grupo
de CBO do evento × tipo de procedimento (pela TUSS do item). Medidas: eventos
distintos com pelo menos um item do tipo (``n_eventos``) e soma das quantidades
informadas (``qt_itens``). Os grupos de CBO são os do painel CNES nacional e
são importados de ``a09_adquirir_cnes_nacional.py`` (não redigitados).

Regras de integridade:
- mês de realização: 202201 a 202512 (nenhum arquivo >= 202601 é lido);
- UF × mês sem arquivo, com falha de download ou reprovado na validação fica
  **ausente** (NA) com motivo no painel, nunca zero;
- zero só existe em UF × mês aprovado, para município sem evento reportado, e o
  status diz isso (``arquivo_presente_municipio_sem_evento``);
- evento sem município válido (vazio, omitido pela ANS, fora da lista do IBGE,
  de outra UF ou com mês divergente) nunca é atribuído a município: vai para
  ``painel_tiss_nao_atribuido_uf_mes.parquet`` com o motivo;
- eventos de operadoras odontológicas (CD_MODALIDADE 23 e 26) e itens da TUSS 22
  do capítulo 8 (odontologia) ficam fora das contagens médicas; os totais
  excluídos vão para o manifesto.

Modos (``--etapa``): ``verificar`` (padrão, usado pelo ``run_all.py``) confere o
painel versionado contra o manifesto, sem rede e sem gravar; ``aquisicao`` lista
o FTP, baixa um par CONS/DET por vez, agrega, valida e apaga os ZIPs (cache fora
do Git); ``painel`` monta as saídas versionadas a partir do cache; ``tudo`` faz
as duas. O download exige pedir ``aquisicao`` ou ``tudo``.

Saídas (``output/aquisicao/tiss/``):
- ``painel_tiss_municipio_mes_tipo_cbo.parquet`` (ambulatorial);
- ``painel_tiss_hospitalar_municipio_mes_tipo.parquet`` (hospitalar; sem CBO na fonte);
- ``painel_tiss_nao_atribuido_uf_mes.parquet`` (eventos sem município atribuível);
- ``tiss_itens_por_categoria_uf_mes.parquet`` (categorias finas de item, por UF × mês);
- ``cobertura_tiss_uf_mes.csv``; ``validacao_tiss.json``; ``a14_resumo.md``;
- ``manifesto_tiss.json``.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import datetime as dt
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pcsv
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
OUT_AQ = ROOT / "output" / "aquisicao"
OUT_DIR = OUT_AQ / "tiss"
CACHE_BRUTO = OUT_DIR / "cache_bruto"
CACHE_PACOTE = OUT_DIR / "cache_pacote"
PAINEL_AMB = OUT_DIR / "painel_tiss_municipio_mes_tipo_cbo.parquet"
PAINEL_HOSP = OUT_DIR / "painel_tiss_hospitalar_municipio_mes_tipo.parquet"
NAO_ATRIBUIDO = OUT_DIR / "painel_tiss_nao_atribuido_uf_mes.parquet"
ITENS_FINOS = OUT_DIR / "tiss_itens_por_categoria_uf_mes.parquet"
COBERTURA = OUT_DIR / "cobertura_tiss_uf_mes.csv"
VALIDACAO = OUT_DIR / "validacao_tiss.json"
RESUMO = OUT_DIR / "a14_resumo.md"
MANIFESTO = OUT_DIR / "manifesto_tiss.json"

POPULACAO_FILE = OUT_AQ / "populacao_censo2022_municipios.csv"  # lista de municípios do IBGE (não é IVS)
A09_FILE = ROOT / "scripts" / "aquisicao" / "a09_adquirir_cnes_nacional.py"
PONTE_FILE = OUT_AQ / "ponte_curso_cbo_oficial.json"

URL_BASE = "https://dadosabertos.ans.gov.br/FTP/PDA/TISS/"
URL_DICIONARIOS = {
    "a_partir_de_2023": URL_BASE + "DICIONARIO/Dicionario_de_variaveis_a_partir_de_2023.ods",
    "ate_2022": URL_BASE + "DICIONARIO/Dicionario_de_variaveis_ate_2022.ods",
}
URL_TUSS = "https://dadosabertos.ans.gov.br/FTP/PDA/terminologia_unificada_saude_suplementar_TUSS-049/pda-049-tuss.zip"
URL_SIP = "https://dadosabertos.ans.gov.br/FTP/PDA/SIP/sip_mapa_assistencial_{trimestre}.csv"
USER_AGENT = "Mozilla/5.0 (pesquisa academica PMM-E; a14)"

# ------------------------------------------------------------------ plano
BASES = {"AMB": "AMBULATORIAL", "HOSP": "HOSPITALAR"}
UFS = ("AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI",
       "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO")
LIMITE_EXCLUSIVO = "202601"  # protocolo 47 §6: TISS até 202512; nada >= 202601 é baixado ou lido
COMPETENCIAS = [f"{a}{m:02d}" for a in (2022, 2023, 2024, 2025) for m in range(1, 13)]
assert all(c < LIMITE_EXCLUSIVO for c in COMPETENCIAS)
# Ordem de aquisição (pedido da tarefa): pré e pós do protocolo 47 primeiro.
PRIORIDADE_1 = [c for c in COMPETENCIAS if "202406" <= c <= "202506" or "202510" <= c <= "202512"]
PRIORIDADE_2 = [c for c in COMPETENCIAS if c not in PRIORIDADE_1]

# ------------------------------------------------------------------ classificação
# CBO: grupos do painel CNES nacional, importados do a09 (protocolo 47 §3.1).
_spec = importlib.util.spec_from_file_location("a09_cnes_nacional_para_a14", A09_FILE)
A09 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A09)

# Partição exclusiva do evento pelo CBO; os grupos de saída são somas dela.
PARTICOES_CBO = ("alvo_pmme", "mfc_225130", "especialistas_nao_alvo_exceto_mfc", "generalistas",
                 "outros_medicos", "nao_medicos", "cbo_ausente", "sem_cbo_na_fonte")
GRUPOS_SAIDA_AMB = {
    "alvo_pmme": ("alvo_pmme",),
    "especialistas_nao_alvo": ("mfc_225130", "especialistas_nao_alvo_exceto_mfc"),  # regra do a09: contém a MFC
    A09.GRUPO_MFC: ("mfc_225130",),
    "generalistas": ("generalistas",),
    "outros_medicos": ("outros_medicos",),
    "nao_medicos": ("nao_medicos",),
    "cbo_ausente": ("cbo_ausente",),
    "todos_cbo": ("alvo_pmme", "mfc_225130", "especialistas_nao_alvo_exceto_mfc", "generalistas",
                  "outros_medicos", "nao_medicos", "cbo_ausente"),
}
GRUPOS_SAIDA_HOSP = {"todos_cbo": ("sem_cbo_na_fonte",)}
assert A09.GRUPO_MFC == "mfc_225130"

# Itens: categoria fina pela tabela TUSS e pelo capítulo do código da tabela 22.
CATEGORIAS = (
    "consultas",                     # 0: TUSS 22, código de 8 dígitos começando por 101 (1.01 = consultas)
    "exames",                        # 1: TUSS 22, capítulo 4 (procedimentos diagnósticos e terapêuticos, SADT)
    "cirurgicos",                    # 2: TUSS 22, capítulo 3 (procedimentos cirúrgicos e invasivos)
    "outros_tuss22",                 # 3: TUSS 22, capítulos 1 (exceto 1.01), 2, 5 e outros
    "odontologia_tuss22",            # 4: TUSS 22, capítulo 8 (odontologia): fora das contagens médicas
    "agrupados_tuss63",              # 5: grupos de procedimentos da TUSS 63
    "materiais_medicamentos_taxas",  # 6: TUSS 18, 19 e 20
    "pacote_ou_tabela_propria",      # 7: tabelas 90/98 (pacotes) ou IND_TABELA_PROPRIA = 1
    "outra_tabela_ou_invalido",      # 8: qualquer outra tabela, ou código 22 fora do formato
)
CAT = {c: i for i, c in enumerate(CATEGORIAS)}
NCAT = len(CATEGORIAS)
TIPOS_PAINEL = {  # tipo do painel -> categorias finas (evento conta se tiver item em alguma delas)
    "consultas": ("consultas",),
    "exames": ("exames",),
    "cirurgicos": ("cirurgicos",),
    "outros": ("outros_tuss22", "agrupados_tuss63", "materiais_medicamentos_taxas",
               "pacote_ou_tabela_propria", "outra_tabela_ou_invalido"),
    "agrupados_tuss63": ("agrupados_tuss63",),  # subconjunto de "outros", para adendo futuro
    "todos_nao_odonto": tuple(c for c in CATEGORIAS if c != "odontologia_tuss22"),
}
MODALIDADES_ODONTO = ("23", "26")  # cooperativa odontológica, odontologia de grupo (dicionário TISS)

# Portões por UF × mês, fixados antes de agregar qualquer arquivo completo.
PORTOES = {
    "taxa_juncao_det_min": 0.995,          # linhas DET cujo ID existe no CONS
    "fracao_mes_divergente_cons_max": 0.01,  # eventos com mês de realização diferente do arquivo
}
# Sinais de alerta (não corrigem nada; só registram).
ALERTA_QUEDA = {"razao_mediana_min": 0.5, "razao_mediana_max": 2.0, "queda_mes_a_mes_max": 0.4}
ALERTA_SIP = {"razao_min": 0.67, "razao_max": 1.5}

VERSAO_AGREGACAO = 2  # 2: CBO classificado pela função agregar_mes do a09
ESPACO_MINIMO_LIVRE = 4 * 1024**3
# Unidades de ~200 MB de ZIP por pacote processado em paralelo. Era 6 na primeira rodada de
# 19/10/2026; o cgroup de 14,3 GB matou o processo (OOM) às 13:08 e a capacidade caiu para 4.
CAPACIDADE_MEMORIA = 4

COLUNAS_PAINEL = ["co_ibge", "uf", "competencia_realizacao", "tipo_procedimento", "grupo_cbo", "n_eventos",
                  "qt_itens", "n_linhas_det", "n_linhas_qt_vazia", "status_cobertura", "natureza_dos_dados"]
COLUNAS_NAO_ATRIB = ["base", "uf", "competencia_realizacao", "motivo_nao_atribuido", "tipo_procedimento",
                     "grupo_cbo", "n_eventos", "qt_itens", "n_linhas_det", "natureza_dos_dados"]
STATUS_OBSERVADO = "observado_municipio_com_evento"
STATUS_ZERO = "arquivo_presente_municipio_sem_evento"


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_arquivo(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while bloco := f.read(4 * 1024 * 1024):
            h.update(bloco)
    return h.hexdigest()


def checar_limite(comp: str) -> None:
    if comp >= LIMITE_EXCLUSIVO or comp not in COMPETENCIAS:
        raise RuntimeError(f"Competência {comp} fora do plano do a14 (202201–202512; nada >= {LIMITE_EXCLUSIVO}).")


def ano_mes(comp: str) -> str:
    return f"{comp[:4]}-{comp[4:]}"


def nome_arquivo(base: str, uf: str, comp: str, parte: str) -> str:
    return f"{uf}_{comp}_{base}_{parte}.zip"


def url_arquivo(base: str, uf: str, comp: str, parte: str) -> str:
    return f"{URL_BASE}{BASES[base]}/{comp[:4]}/{uf}/{nome_arquivo(base, uf, comp, parte)}"


def chave_pacote(base: str, uf: str, comp: str) -> str:
    return f"{base}_{uf}_{comp}"


# ------------------------------------------------------------------ municípios (IBGE)

def carregar_municipios() -> pd.DataFrame:
    """Lista de municípios do IBGE usada no repositório (Censo 2022). Só chaves; a população não é usada."""
    df = pd.read_csv(POPULACAO_FILE, dtype=str, usecols=["co_ibge_6d", "no_municipio_uf"])
    df["co_ibge"] = df["co_ibge_6d"].str.strip().str.zfill(6)
    df["uf"] = df["no_municipio_uf"].str.extract(r" - ([A-Z]{2})$", expand=False)
    if df["co_ibge"].duplicated().any() or df["uf"].isna().any() or len(df) < 5_500:
        raise RuntimeError(f"{POPULACAO_FILE.relative_to(ROOT)}: lista de municípios inválida")
    cod_uf = df.assign(p=df["co_ibge"].str[:2]).groupby("uf")["p"].unique()
    if any(len(v) != 1 for v in cod_uf) or set(cod_uf.index) != set(UFS):
        raise RuntimeError("prefixo IBGE da UF não é único por UF na lista de municípios")
    return df[["co_ibge", "uf"]].sort_values("co_ibge").reset_index(drop=True)


def prefixo_uf(municipios: pd.DataFrame) -> dict[str, str]:
    return {uf: g["co_ibge"].str[:2].iloc[0] for uf, g in municipios.groupby("uf")}


# ------------------------------------------------------------------ classificação (funções puras)

def normalizar_cbo(bruto: str | None) -> str:
    return re.sub(r"[^0-9A-Za-z]", "", bruto or "").upper()


def grupos_a09_por_cbo(codigos: Iterable[str], alvo: list[str]) -> dict[str, set[str]]:
    """Grupos do a09 de cada código de CBO, obtidos pela própria função ``A09.agregar_mes``.

    Primeiro aplica o filtro de extração do a09 (CBO começando por ``A09.PREFIXOS_MEDICOS``;
    o resto não é médico e não tem grupo). Depois monta um vínculo fictício por código (um
    "município" por código, horas nulas, sem nenhum dado observado) só para ler em que grupos
    o a09 coloca cada CBO. Assim a regra (inclusive a de ``especialistas_nao_alvo``) é a do
    a09, e não uma cópia.
    """
    cods = sorted({c for c in (normalizar_cbo(x) for x in codigos) if c.startswith(A09.PREFIXOS_MEDICOS)})
    if not cods:
        return {}
    n = len(cods)
    zeros = pd.array([0] * n, dtype="Int32")
    df = pd.DataFrame({
        "co_municipio": pd.Series([f"{i:06d}" for i in range(n)], dtype="string"),
        "co_cbo": pd.Series(cods, dtype="string"),
        "qt_ch_ambulatorial": zeros, "qt_ch_hosp_sus": zeros, "qt_ch_outros": zeros,
        "tp_sus_nao_sus": pd.Series(["S"] * n, dtype="string"),
        "co_profissional_sus": pd.Series([f"c{i}" for i in range(n)], dtype="string"),
    })
    out = A09.agregar_mes(df, alvo)
    grupos: dict[str, set[str]] = {c: set() for c in cods}
    for m, g in zip(out["co_municipio"], out["grupo"], strict=True):
        grupos[cods[int(m)]].add(g)
    return grupos


def classificar_cbo(cbo: Iterable[str], alvo: list[str]) -> np.ndarray:
    """Partição exclusiva do evento pelo CBO a partir dos grupos do a09.

    alvo_pmme > mfc_225130 > generalistas > especialistas_nao_alvo (sem a MFC) >
    outros médicos (só em todos_medicos do a09, como a família 2231) > não médicos; vazio = cbo_ausente.
    """
    cbo = list(cbo)
    g = grupos_a09_por_cbo(cbo, alvo)
    saida = []
    for bruto in cbo:
        c = normalizar_cbo(bruto)
        gs = g.get(c, set())
        if not c:
            saida.append("cbo_ausente")
        elif "alvo_pmme" in gs:
            saida.append("alvo_pmme")
        elif A09.GRUPO_MFC in gs:
            saida.append("mfc_225130")
        elif "generalistas" in gs:
            saida.append("generalistas")
        elif "especialistas_nao_alvo" in gs:
            saida.append("especialistas_nao_alvo_exceto_mfc")
        elif "todos_medicos" in gs:
            saida.append("outros_medicos")
        else:
            saida.append("nao_medicos")
    return np.array(saida, dtype=object)


def normalizar_codigo(arr: pa.Array, largura: int) -> pa.Array:
    """Tira espaços e zeros à esquerda e completa com zeros até a largura ("0" -> "00"; "1" -> "001").

    Os arquivos de 2022 escrevem a tabela 00 como "0" e grupos da TUSS 63 sem zeros à esquerda.
    """
    t = pc.utf8_ltrim(pc.utf8_trim_whitespace(pc.fill_null(arr, "")), characters="0")
    vazio_orig = pc.equal(pc.utf8_trim_whitespace(pc.fill_null(arr, "")), "")
    return pc.if_else(vazio_orig, pa.scalar("", pa.string()), pc.utf8_lpad(t, width=largura, padding="0"))


def classificar_itens(tabela: pa.Array, procedimento: pa.Array, tabela_propria: pa.Array) -> np.ndarray:
    """Categoria fina de cada linha DET (índice em CATEGORIAS)."""
    tab = normalizar_codigo(tabela, 2)
    proc = pc.utf8_trim_whitespace(procedimento)
    prop = pc.equal(pc.utf8_trim_whitespace(tabela_propria), "1")

    def m(arr: pa.Array) -> np.ndarray:
        return np.asarray(pc.fill_null(arr, False).to_numpy(zero_copy_only=False), dtype=bool)

    n = len(tab)
    cat = np.full(n, CAT["outra_tabela_ou_invalido"], dtype=np.int8)
    t22 = m(pc.equal(tab, "22"))
    oito = m(pc.match_substring_regex(proc, r"^[0-9]{8}$"))
    c1 = np.asarray(pc.utf8_slice_codeunits(proc, 0, 1).to_numpy(zero_copy_only=False), dtype=object)
    c3 = np.asarray(pc.utf8_slice_codeunits(proc, 0, 3).to_numpy(zero_copy_only=False), dtype=object)
    v22 = t22 & oito
    cat[v22] = CAT["outros_tuss22"]
    cat[v22 & (c1 == "4")] = CAT["exames"]
    cat[v22 & (c1 == "3")] = CAT["cirurgicos"]
    cat[v22 & (c1 == "8")] = CAT["odontologia_tuss22"]
    cat[v22 & (c3 == "101")] = CAT["consultas"]
    cat[m(pc.equal(tab, "63"))] = CAT["agrupados_tuss63"]
    cat[m(pc.is_in(tab, value_set=pa.array(["18", "19", "20"])))] = CAT["materiais_medicamentos_taxas"]
    cat[m(pc.is_in(tab, value_set=pa.array(["90", "98"])))] = CAT["pacote_ou_tabela_propria"]
    cat[m(prop)] = CAT["pacote_ou_tabela_propria"]  # código criado pela operadora: não é TUSS
    return cat


def converter_quantidade(qt: pa.Array) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Quantidade informada (vírgula decimal). Devolve valores, máscara de vazio e de não numérico.

    Vazio e não numérico ficam NaN (ausentes), nunca zero; o chamador conta cada caso.
    """
    txt = pc.utf8_trim_whitespace(qt)
    vazio = np.asarray(pc.fill_null(pc.equal(txt, ""), True).to_numpy(zero_copy_only=False), dtype=bool)
    norm = pc.replace_substring(txt, ",", ".")
    norm = pc.if_else(pc.equal(norm, ""), pa.scalar(None, pa.string()), norm)
    try:
        val = np.asarray(pc.cast(norm, pa.float64()).to_numpy(zero_copy_only=False), dtype=float)
    except pa.ArrowInvalid:
        val = pd.to_numeric(pd.Series(norm.to_numpy(zero_copy_only=False), dtype=object), errors="coerce").to_numpy(float)
    nao_num = np.isnan(val) & ~vazio
    return val, vazio, nao_num


# ------------------------------------------------------------------ agregação de um par CONS/DET (pura)

def _codigos_unicos(col: pa.ChunkedArray | pa.Array) -> tuple[np.ndarray, list[str]]:
    arr = col.combine_chunks() if isinstance(col, pa.ChunkedArray) else col
    arr = pc.utf8_trim_whitespace(pc.fill_null(arr, ""))
    enc = pc.dictionary_encode(arr)
    return np.asarray(enc.indices.to_numpy(zero_copy_only=False), dtype=np.int32), enc.dictionary.to_pylist()


def agregar_pacote(base: str, uf: str, comp: str, cons: pa.Table | list, det_lotes: Iterable[pa.RecordBatch | pa.Table],
                   alvo: list[str], municipios_validos: set[str], prefixos_uf: dict[str, str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Agrega um par CONS/DET de uma UF × mês.

    Devolve uma tabela por célula (status do município, município, partição de CBO,
    operadora odontológica) × nível (``painel`` com os tipos do painel; ``fino`` com as
    categorias de item) e um diagnóstico com as validações. ``cons`` pode vir numa lista de
    um elemento, que é esvaziada: assim a tabela do CONS é liberada coluna a coluna (memória).
    """
    if isinstance(cons, list):
        cons = cons.pop()
    col_mes = "DT_REALIZACAO" if base == "AMB" else "ANO_MES_EVENTO"
    n_cons = int(cons.num_rows)
    diag: dict[str, Any] = {"linhas_cons": n_cons}
    ids_txt = pc.utf8_trim_whitespace(pc.fill_null(cons.column("ID_EVENTO_ATENCAO_SAUDE").combine_chunks(), ""))
    if n_cons and not pc.all(pc.match_substring_regex(ids_txt, r"^[0-9]{1,18}$")).as_py():
        raise ValueError("ID_EVENTO_ATENCAO_SAUDE do CONS com valor vazio, não numérico ou com mais de 18 dígitos")
    ids = np.asarray(pc.cast(ids_txt, pa.int64()).to_numpy(zero_copy_only=False), dtype=np.int64)
    del ids_txt
    cons = cons.drop_columns(["ID_EVENTO_ATENCAO_SAUDE"])
    ordem = np.argsort(ids, kind="stable")
    ids_ord = ids[ordem]
    del ids
    dup = int((np.diff(ids_ord) == 0).sum()) if len(ids_ord) > 1 else 0
    diag["ids_cons_duplicados"] = dup
    if dup:
        raise ValueError(f"{dup} ID_EVENTO_ATENCAO_SAUDE duplicados no CONS")

    # atributos por valor distinto (poucos), depois mapeados aos eventos; cada coluna sai da tabela ao ser lida
    def pegar(nome: str) -> tuple[np.ndarray, list[str]]:
        nonlocal cons
        r = _codigos_unicos(cons.column(nome))
        cons = cons.drop_columns([nome])
        return r

    mun_idx, mun_vals = pegar("CD_MUNICIPIO_PRESTADOR")
    mes_idx, mes_vals = pegar(col_mes)
    mod_idx, mod_vals = pegar("CD_MODALIDADE")
    uf_idx, uf_vals = pegar("UF_PRESTADOR")
    if base == "AMB":
        cbo_idx, cbo_vals = pegar("CBO")
        part_vals = classificar_cbo(cbo_vals, alvo)
    else:
        cbo_idx, cbo_vals = np.zeros(n_cons, dtype=np.int32), ["<sem CBO no hospitalar>"]
        part_vals = np.array(["sem_cbo_na_fonte"], dtype=object)
    del cons
    part_cod = np.array([PARTICOES_CBO.index(p) for p in part_vals], dtype=np.int32)

    pref = prefixos_uf[uf]
    motivos = ["ok", "mes_divergente", "municipio_ausente", "municipio_omitido_pela_ans",
               "municipio_invalido", "municipio_de_outra_uf"]
    st_mun = []
    for v in mun_vals:
        if v == "":
            st_mun.append(motivos.index("municipio_omitido_pela_ans" if base == "HOSP" else "municipio_ausente"))
        elif not re.fullmatch(r"[0-9]{6}", v) or v not in municipios_validos:
            st_mun.append(motivos.index("municipio_invalido"))
        elif not v.startswith(pref):
            st_mun.append(motivos.index("municipio_de_outra_uf"))
        else:
            st_mun.append(0)
    st_mun = np.array(st_mun, dtype=np.int32)
    mes_ok = np.array([v == ano_mes(comp) for v in mes_vals], dtype=bool)
    odonto_vals = np.array([v in MODALIDADES_ODONTO for v in mod_vals], dtype=bool)

    status = np.where(mes_ok[mes_idx], st_mun[mun_idx], np.int32(1)).astype(np.int32)
    nmun = len(mun_vals) + 1
    npart = len(PARTICOES_CBO)
    # chave da célula = (status, município, partição de CBO, operadora odontológica), em int32
    chave = np.where(status == 0, mun_idx + 1, 0).astype(np.int32)
    chave += status * nmun
    chave *= npart
    chave += part_cod[cbo_idx]
    chave *= 2
    chave += odonto_vals[mod_idx]
    tam_chave = len(motivos) * nmun * npart * 2
    presentes = np.flatnonzero(np.bincount(chave, minlength=tam_chave))
    mapa = np.full(tam_chave, -1, dtype=np.int32)
    mapa[presentes] = np.arange(len(presentes), dtype=np.int32)
    celula = mapa[chave]
    del chave, mapa
    ncel = len(presentes)
    k = presentes.astype(np.int64)
    cel_odonto = k % 2
    k = k // 2
    cel_part = k % npart
    k = k // npart
    cel_mun = k % nmun - 1
    cel_status = k // nmun

    def contar(idx: np.ndarray, vals: list) -> dict[str, int]:
        c = np.bincount(idx, minlength=len(vals))
        return {vals[i]: int(c[i]) for i in np.flatnonzero(c)}

    diag["eventos_por_status_municipio"] = contar(status, motivos)
    diag["eventos_operadora_odontologica"] = int(odonto_vals[mod_idx].sum())
    diag["eventos_por_modalidade"] = contar(mod_idx, mod_vals)
    diag["eventos_por_uf_prestador"] = contar(uf_idx, uf_vals)
    diag["eventos_por_mes_realizacao"] = contar(mes_idx, mes_vals)
    diag["fracao_mes_divergente_cons"] = float((~mes_ok[mes_idx]).mean()) if n_cons else 0.0
    if base == "AMB":
        diag["eventos_por_cbo"] = contar(cbo_idx, cbo_vals)
    invalidos = [v for v, s in zip(mun_vals, st_mun) if s in (4, 5)]
    diag["codigos_municipio_invalidos_ou_de_outra_uf"] = sorted(invalidos)[:50]
    ev_cel = celula[ordem]  # célula na ordem dos IDs ordenados
    del ordem, celula, mun_idx, mes_idx, mod_idx, uf_idx, cbo_idx, status

    flags = np.zeros(len(ids_ord), dtype=np.uint16)
    soma_qt = np.zeros(ncel * NCAT, dtype=np.float64)
    linhas = np.zeros(ncel * NCAT, dtype=np.int64)
    qt_vazia = np.zeros(ncel * NCAT, dtype=np.int64)
    nao_juntado = np.zeros(NCAT, dtype=np.int64)
    tot_det = 0
    cont = {"det_mes_divergente": 0, "qt_vazia_item_de_pacote": 0, "qt_vazia_fora_de_pacote": 0,
            "qt_nao_numerica": 0, "qt_negativa": 0, "qt_nao_inteira": 0}
    por_tabela: dict[str, int] = {}
    por_capitulo_22: dict[str, int] = {}
    por_grupo_63: dict[str, int] = {}
    for lote in det_lotes:
        n = lote.num_rows
        if n == 0:
            continue
        tot_det += n
        col = lote.column
        idt = pc.utf8_trim_whitespace(pc.fill_null(col("ID_EVENTO_ATENCAO_SAUDE"), ""))
        if not pc.all(pc.match_substring_regex(idt, r"^[0-9]{1,18}$")).as_py():
            raise ValueError("ID_EVENTO_ATENCAO_SAUDE do DET com valor vazio, não numérico ou com mais de 18 dígitos")
        idd = np.asarray(pc.cast(idt, pa.int64()).to_numpy(zero_copy_only=False), dtype=np.int64)
        pos = np.searchsorted(ids_ord, idd)
        pos_ok = np.minimum(pos, max(len(ids_ord) - 1, 0))
        casou = (pos < len(ids_ord)) & (ids_ord[pos_ok] == idd) if len(ids_ord) else np.zeros(n, dtype=bool)
        tab = col("CD_TABELA_REFERENCIA")
        proc = col("CD_PROCEDIMENTO")
        cat = classificar_itens(tab, proc, col("IND_TABELA_PROPRIA"))
        val, vazio, nao_num = converter_quantidade(col("QT_ITEM_EVENTO_INFORMADO"))
        pacote = np.asarray(pc.fill_null(pc.equal(pc.utf8_trim_whitespace(col("IND_PACOTE")), "1"), False)
                            .to_numpy(zero_copy_only=False), dtype=bool)
        cont["qt_vazia_item_de_pacote"] += int((vazio & pacote).sum())
        cont["qt_vazia_fora_de_pacote"] += int((vazio & ~pacote).sum())
        cont["qt_nao_numerica"] += int(nao_num.sum())
        fin = ~np.isnan(val)
        cont["qt_negativa"] += int((val[fin] < 0).sum())
        cont["qt_nao_inteira"] += int((val[fin] != np.round(val[fin])).sum())
        mes_det = pc.utf8_trim_whitespace(pc.fill_null(col(col_mes), ""))
        cont["det_mes_divergente"] += int(pc.sum(pc.cast(pc.not_equal(mes_det, ano_mes(comp)), pa.int64())).as_py() or 0)
        tab_n = normalizar_codigo(tab, 2)
        for d in pc.value_counts(tab_n).to_pylist():
            por_tabela[d["values"]] = por_tabela.get(d["values"], 0) + int(d["counts"])
        proc_t = pc.utf8_trim_whitespace(pc.fill_null(proc, ""))
        t22 = pc.equal(tab_n, "22")
        for d in pc.value_counts(pc.utf8_slice_codeunits(pc.filter(proc_t, t22), 0, 1)).to_pylist():
            por_capitulo_22[d["values"]] = por_capitulo_22.get(d["values"], 0) + int(d["counts"])
        t63 = pc.equal(tab_n, "63")
        for d in pc.value_counts(normalizar_codigo(pc.filter(proc, t63), 3)).to_pylist():
            por_grupo_63[d["values"]] = por_grupo_63.get(d["values"], 0) + int(d["counts"])

        nao_juntado += np.bincount(cat[~casou].astype(np.int64), minlength=NCAT)
        p = pos[casou]
        c = cat[casou].astype(np.int64)
        chave_item = ev_cel[p].astype(np.int64) * NCAT + c
        linhas += np.bincount(chave_item, minlength=ncel * NCAT)
        v = val[casou]
        ok = ~np.isnan(v)
        soma_qt += np.bincount(chave_item[ok], weights=v[ok], minlength=ncel * NCAT)
        qt_vazia += np.bincount(chave_item[vazio[casou]], minlength=ncel * NCAT)
        np.bitwise_or.at(flags, p, (np.uint16(1) << c.astype(np.uint16)).astype(np.uint16))

    diag["linhas_det"] = int(tot_det)
    diag["linhas_det_nao_juntadas"] = int(nao_juntado.sum())
    diag["linhas_det_nao_juntadas_por_categoria"] = {CATEGORIAS[i]: int(x) for i, x in enumerate(nao_juntado) if x}
    diag["taxa_juncao_det"] = (1 - nao_juntado.sum() / tot_det) if tot_det else None
    diag["eventos_cons_sem_item_det"] = int((flags == 0).sum())
    diag["quantidades"] = cont
    diag["linhas_det_por_tabela"] = dict(sorted(por_tabela.items()))
    diag["linhas_det_tuss22_por_capitulo"] = dict(sorted(por_capitulo_22.items()))
    diag["linhas_det_tuss63_por_grupo"] = dict(sorted(por_grupo_63.items()))

    # eventos por célula e tipo (não aditivo entre tipos: o evento conta uma vez em cada tipo que tiver)
    registros = []
    linhas2 = linhas.reshape(ncel, NCAT)
    soma2 = soma_qt.reshape(ncel, NCAT)
    vazia2 = qt_vazia.reshape(ncel, NCAT)
    niveis = [("fino", c, (c,)) for c in CATEGORIAS] + [("painel", t, cs) for t, cs in TIPOS_PAINEL.items()]
    for nivel, tipo, cats in niveis:
        mascara = np.uint16(sum(1 << CAT[c] for c in cats))
        tem = (flags & mascara) != 0
        n_ev = np.bincount(ev_cel[tem], minlength=ncel)
        idx = [CAT[c] for c in cats]
        registros.append(pd.DataFrame({
            "nivel": nivel, "tipo": tipo, "celula": np.arange(ncel),
            "n_eventos": n_ev, "qt_itens": soma2[:, idx].sum(axis=1),
            "n_linhas_det": linhas2[:, idx].sum(axis=1), "n_linhas_qt_vazia": vazia2[:, idx].sum(axis=1),
        }))
    sem_item = np.bincount(ev_cel[flags == 0], minlength=ncel)
    registros.append(pd.DataFrame({"nivel": "fino", "tipo": "evento_sem_item_det", "celula": np.arange(ncel),
                                   "n_eventos": sem_item, "qt_itens": 0.0, "n_linhas_det": 0, "n_linhas_qt_vazia": 0}))
    total_ev = np.bincount(ev_cel, minlength=ncel)
    registros.append(pd.DataFrame({"nivel": "fino", "tipo": "evento_qualquer", "celula": np.arange(ncel),
                                   "n_eventos": total_ev, "qt_itens": soma2.sum(axis=1),
                                   "n_linhas_det": linhas2.sum(axis=1), "n_linhas_qt_vazia": vazia2.sum(axis=1)}))
    agg = pd.concat(registros, ignore_index=True)
    celulas = pd.DataFrame({
        "celula": np.arange(ncel),
        "status_municipio": [motivos[s] for s in cel_status],
        "co_ibge": [mun_vals[m] if m >= 0 else "" for m in cel_mun],
        "particao_cbo": [PARTICOES_CBO[p] for p in cel_part],
        "operadora_odontologica": cel_odonto.astype(bool),
    })
    agg = agg.merge(celulas, on="celula", how="left", validate="many_to_one").drop(columns="celula")
    agg = agg.loc[(agg["n_eventos"] > 0) | (agg["n_linhas_det"] > 0)]
    agg.insert(0, "base", base)
    agg.insert(1, "uf", uf)
    agg.insert(2, "competencia_realizacao", comp)
    agg = agg.sort_values(["status_municipio", "co_ibge", "particao_cbo", "operadora_odontologica", "nivel", "tipo"],
                          kind="mergesort").reset_index(drop=True)
    for c in ("n_eventos", "n_linhas_det", "n_linhas_qt_vazia"):
        agg[c] = agg[c].astype(np.int64)
    agg["qt_itens"] = agg["qt_itens"].astype(float)
    return agg, diag


def avaliar_portoes(diag: dict[str, Any]) -> list[str]:
    """Motivos de reprovação de um par CONS/DET (lista vazia = aprovado)."""
    motivos = []
    if diag.get("linhas_cons", 0) == 0 or diag.get("linhas_det", 0) == 0:
        motivos.append("arquivo_vazio")
    tj = diag.get("taxa_juncao_det")
    if tj is not None and tj < PORTOES["taxa_juncao_det_min"]:
        motivos.append("juncao_det_cons_abaixo_do_portao")
    if diag.get("fracao_mes_divergente_cons", 0) > PORTOES["fracao_mes_divergente_cons_max"]:
        motivos.append("mes_divergente_acima_do_portao")
    return motivos


# ------------------------------------------------------------------ rede

def _abrir(url: str, timeout: int = 120, metodo: str = "GET"):
    req = urllib.request.Request(url, method=metodo, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout)


def listar_ftp(workers: int = 8) -> dict[str, dict[str, Any]]:
    """Lista os diretórios <BASE>/<ano>/<UF>/ e devolve {nome_zip: {data_listagem, tamanho_listagem, url}}."""
    alvos = [(b, a, uf) for b in BASES for a in sorted({c[:4] for c in COMPETENCIAS}) for uf in UFS]
    saida: dict[str, dict[str, Any]] = {}
    erros: dict[str, str] = {}

    def um(b: str, a: str, uf: str) -> None:
        url = f"{URL_BASE}{BASES[b]}/{a}/{uf}/"
        for tentativa in range(4):
            try:
                with _abrir(url, timeout=60) as r:
                    html = r.read().decode("utf-8", "replace")
                break
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    erros[url] = "404"
                    return
                erro = str(exc)
            except Exception as exc:  # noqa: BLE001
                erro = f"{type(exc).__name__}: {exc}"
            time.sleep(5 * (tentativa + 1))
        else:
            erros[url] = erro
            return
        for linha in html.split("<tr>"):
            mt = re.search(r'href="([A-Z]{2}_\d{6}_[A-Z]+_[A-Z]+\.zip)"', linha)
            if not mt:
                continue
            texto = re.sub(r"<[^>]+>", " ", linha)
            md = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s+([\d.]+[KMG]?)", texto)
            saida[mt.group(1)] = {
                "url": url + mt.group(1),
                "data_listagem": md.group(1) if md else None,
                "tamanho_listagem": md.group(2) if md else None,
            }

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(lambda t: um(*t), alvos))
    if erros:
        saida["__erros_listagem__"] = erros  # type: ignore[assignment]
    return saida


def tamanho_listagem_bytes(txt: str | None) -> float:
    if not txt:
        return 0.0
    mult = {"K": 1e3, "M": 1e6, "G": 1e9}
    return float(txt[:-1]) * mult[txt[-1]] if txt[-1] in mult else float(txt)


def baixar(url: str, destino: Path, tentativas: int = 5, timeout: int = 300) -> dict[str, Any]:
    """Baixa em fluxo com SHA-256; confere Content-Length; devolve metadados HTTP."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    parcial = destino.with_name(destino.name + ".part")
    ultimo = ""
    for tentativa in range(1, tentativas + 1):
        while shutil.disk_usage(destino.parent).free < ESPACO_MINIMO_LIVRE:
            log(f"  disco abaixo de {ESPACO_MINIMO_LIVRE / 1024**3:.0f} GB livres; aguardando")
            time.sleep(30)
        t0 = time.time()
        h = hashlib.sha256()
        total = 0
        try:
            with _abrir(url, timeout=timeout) as r:
                esperado = r.headers.get("Content-Length")
                info = {"last_modified_http": r.headers.get("Last-Modified"), "etag_http": r.headers.get("ETag"),
                        "content_length_http": int(esperado) if esperado else None}
                with parcial.open("wb") as f:
                    while bloco := r.read(4 * 1024 * 1024):
                        f.write(bloco)
                        h.update(bloco)
                        total += len(bloco)
                    f.flush()
                    os.fsync(f.fileno())  # não deixa páginas sujas acumularem no cgroup de memória
            if info["content_length_http"] is not None and total != info["content_length_http"]:
                raise IOError(f"recebidos {total} bytes; Content-Length {info['content_length_http']}")
            parcial.replace(destino)
            return {**info, "url": url, "bytes": total, "sha256": h.hexdigest(),
                    "data_download_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "segundos_download": round(time.time() - t0, 1), "tentativas": tentativa}
        except urllib.error.HTTPError as exc:
            ultimo = f"HTTP {exc.code}"
            if exc.code == 404:
                break
        except Exception as exc:  # noqa: BLE001
            ultimo = f"{type(exc).__name__}: {exc}"
        if parcial.exists():
            parcial.unlink()
        log(f"  falha em {url.rsplit('/', 1)[-1]} (tentativa {tentativa}): {ultimo}")
        time.sleep(min(20 * tentativa, 120))
    raise IOError(f"download falhou: {ultimo}")


# ------------------------------------------------------------------ leitura dos ZIPs

def _cabecalho_membro(zf: zipfile.ZipFile, membro: str) -> list[str]:
    with zf.open(membro) as f:
        linha = f.readline().decode("utf-8-sig", "replace").strip()
    return [c.strip().strip('"').upper() for c in linha.split(";")]


def _membro_csv(zf: zipfile.ZipFile) -> str:
    csvs = [n for n in zf.namelist() if n.lower().endswith(".csv")]
    if len(csvs) != 1:
        raise ValueError(f"esperado 1 CSV no ZIP, há {len(csvs)}: {zf.namelist()[:5]}")
    return csvs[0]


def colunas_necessarias(base: str, parte: str) -> list[str]:
    mes = "DT_REALIZACAO" if base == "AMB" else "ANO_MES_EVENTO"
    if parte == "CONS":
        cols = ["ID_EVENTO_ATENCAO_SAUDE", "CD_MODALIDADE", "CD_MUNICIPIO_PRESTADOR", "UF_PRESTADOR", mes]
        return cols + (["CBO"] if base == "AMB" else [])
    return ["ID_EVENTO_ATENCAO_SAUDE", mes, "CD_PROCEDIMENTO", "CD_TABELA_REFERENCIA",
            "QT_ITEM_EVENTO_INFORMADO", "IND_PACOTE", "IND_TABELA_PROPRIA"]


def _opcoes(cols: list[str]) -> tuple[pcsv.ReadOptions, pcsv.ParseOptions, pcsv.ConvertOptions]:
    return (pcsv.ReadOptions(block_size=64 << 20),
            pcsv.ParseOptions(delimiter=";", quote_char='"'),
            pcsv.ConvertOptions(include_columns=cols, column_types={c: pa.string() for c in cols},
                                strings_can_be_null=False, quoted_strings_can_be_null=False))


def ler_zip(path: Path, base: str, parte: str) -> tuple[dict[str, Any], Any]:
    """Abre o CSV do ZIP; confere o esquema; devolve (info, leitor ou tabela)."""
    zf = zipfile.ZipFile(path)
    membro = _membro_csv(zf)
    cab = _cabecalho_membro(zf, membro)
    cols = colunas_necessarias(base, parte)
    faltam = [c for c in cols if c not in cab]
    zi = zf.getinfo(membro)
    info = {"membro_csv": membro, "bytes_csv": zi.file_size, "data_membro_zip": "%04d-%02d-%02d %02d:%02d" % zi.date_time[:5],
            "colunas_arquivo": cab, "colunas_lidas": cols}
    if faltam:
        raise ValueError(f"{path.name}: colunas ausentes {faltam}")
    ro, po, co = _opcoes(cols)
    if parte == "CONS":
        with zf, zf.open(membro) as f:
            tab = pcsv.read_csv(f, read_options=ro, parse_options=po, convert_options=co)
        return info, tab
    f = zf.open(membro)
    return info, (zf, f, pcsv.open_csv(f, read_options=ro, parse_options=po, convert_options=co))


# ------------------------------------------------------------------ pacote (UF × mês × base)

def caminho_cache(base: str, uf: str, comp: str) -> Path:
    return CACHE_PACOTE / f"{chave_pacote(base, uf, comp)}.parquet"


def caminho_meta(base: str, uf: str, comp: str) -> Path:
    return CACHE_PACOTE / f"{chave_pacote(base, uf, comp)}.json"


def _gravar_meta(base: str, uf: str, comp: str, meta: dict[str, Any]) -> None:
    CACHE_PACOTE.mkdir(parents=True, exist_ok=True)
    p = caminho_meta(base, uf, comp)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(p)


class Memoria:
    """Semáforo ponderado: limita a soma de 'pesos' (tamanho dos ZIPs) em processamento."""

    def __init__(self, capacidade: int) -> None:
        self.capacidade = capacidade
        self.uso = 0
        self.cond = threading.Condition()

    def adquirir(self, peso: int) -> None:
        peso = min(peso, self.capacidade)
        with self.cond:
            while self.uso + peso > self.capacidade:
                self.cond.wait()
            self.uso += peso

    def liberar(self, peso: int) -> None:
        peso = min(peso, self.capacidade)
        with self.cond:
            self.uso -= peso
            self.cond.notify_all()


def processar_pacote(base: str, uf: str, comp: str, listagem: dict[str, Any], contexto: dict[str, Any],
                     memoria: Memoria) -> dict[str, Any]:
    """Baixa CONS e DET, agrega, valida, grava o cache e apaga os ZIPs. Idempotente."""
    checar_limite(comp)
    if caminho_meta(base, uf, comp).exists():
        # retomada: aprovado (com cache) e reprovado não são refeitos; ausência e falhas são tentadas de novo
        ant = json.loads(caminho_meta(base, uf, comp).read_text(encoding="utf-8"))
        st_ant = ant.get("status", "")
        if ant.get("versao_agregacao") == VERSAO_AGREGACAO and (
                (st_ant == "aprovado" and caminho_cache(base, uf, comp).exists()) or st_ant.startswith("reprovado_")):
            return ant
    meta: dict[str, Any] = {"base": base, "uf": uf, "competencia_realizacao": comp,
                            "versao_agregacao": VERSAO_AGREGACAO, "arquivos": {}}
    nomes = {p: nome_arquivo(base, uf, comp, p) for p in ("CONS", "DET", "REM")}
    meta["rem_listado"] = nomes["REM"] in listagem
    if nomes["REM"] in listagem:
        meta["rem_listagem"] = listagem[nomes["REM"]]
    faltam = [p for p in ("CONS", "DET") if nomes[p] not in listagem]
    if faltam:
        meta["status"] = "ausente_arquivo_nao_publicado"
        meta["detalhe"] = f"não listado no FTP: {[nomes[p] for p in faltam]}"
        _gravar_meta(base, uf, comp, meta)
        return meta
    peso = 1 + int(sum(tamanho_listagem_bytes(listagem[nomes[p]]["tamanho_listagem"]) for p in ("CONS", "DET")) // 200e6)
    t0 = time.time()
    caminhos = {p: CACHE_BRUTO / base / nomes[p] for p in ("CONS", "DET")}
    com_memoria = False
    try:
        for p in ("CONS", "DET"):
            try:
                info = baixar(listagem[nomes[p]]["url"], caminhos[p])
            except Exception as exc:  # noqa: BLE001
                meta["status"] = "falha_download"
                meta["detalhe"] = f"{nomes[p]}: {exc}"
                _gravar_meta(base, uf, comp, meta)
                return meta
            meta["arquivos"][p] = {"nome": nomes[p], **listagem[nomes[p]], **info}
        memoria.adquirir(peso)  # só a leitura e a agregação disputam memória; o download não
        com_memoria = True
        t1 = time.time()
        try:
            info_c, tabela_cons = ler_zip(caminhos["CONS"], base, "CONS")
            cons = [tabela_cons]  # o agregador esvazia a lista e libera a tabela coluna a coluna
            del tabela_cons
            meta["arquivos"]["CONS"].update(info_c)
            info_d, (zf, f, leitor) = ler_zip(caminhos["DET"], base, "DET")
            meta["arquivos"]["DET"].update(info_d)
            try:
                agg, diag = agregar_pacote(base, uf, comp, cons, leitor, contexto["alvo"], contexto["validos"],
                                           contexto["prefixos"])
            finally:
                f.close()
                zf.close()
            del cons
        except Exception as exc:  # noqa: BLE001
            meta["status"] = "falha_leitura_ou_validacao"
            meta["detalhe"] = f"{type(exc).__name__}: {exc}"
            _gravar_meta(base, uf, comp, meta)
            log(f"  {chave_pacote(base, uf, comp)}: FALHA {meta['detalhe']}")
            return meta
        meta["diagnostico"] = diag
        meta["arquivos"]["CONS"]["linhas"] = diag["linhas_cons"]
        meta["arquivos"]["DET"]["linhas"] = diag["linhas_det"]
        motivos = avaliar_portoes(diag)
        meta["segundos_agregacao"] = round(time.time() - t1, 1)
        if motivos:
            meta["status"] = "reprovado_" + "+".join(motivos)
            _gravar_meta(base, uf, comp, meta)
            log(f"  {chave_pacote(base, uf, comp)}: REPROVADO {motivos}")
            return meta
        CACHE_PACOTE.mkdir(parents=True, exist_ok=True)
        tmp = caminho_cache(base, uf, comp).with_suffix(".parquet.tmp")
        agg.to_parquet(tmp, index=False)
        tmp.replace(caminho_cache(base, uf, comp))
        meta["status"] = "aprovado"
        meta["sha256_cache"] = sha256_arquivo(caminho_cache(base, uf, comp))
        meta["segundos_total"] = round(time.time() - t0, 1)
        meta["data_processamento"] = dt.date.today().isoformat()
        _gravar_meta(base, uf, comp, meta)
        log(f"  {chave_pacote(base, uf, comp)}: OK {diag['linhas_cons']:,} eventos, {diag['linhas_det']:,} itens, "
            f"junção {diag['taxa_juncao_det']:.4f}, {meta['segundos_total']:.0f}s")
        return meta
    finally:
        for c in caminhos.values():
            for q in (c, c.with_name(c.name + ".part")):
                if q.exists():
                    q.unlink()
        if com_memoria:
            pa.default_memory_pool().release_unused()
            memoria.liberar(peso)


def contexto_classificacao() -> dict[str, Any]:
    alvo, _, versao = A09.carregar_ponte()
    if A09.MFC in alvo or set(A09.GENERALISTAS) & set(alvo):
        raise RuntimeError("ponte: CBO-alvo inclui MFC ou generalista; a partição do a14 não vale")
    mun = carregar_municipios()
    return {"alvo": alvo, "versao_ponte": versao, "validos": set(mun["co_ibge"]), "prefixos": prefixo_uf(mun)}


def plano_pacotes(bases: list[str], ufs: list[str], comps: list[str]) -> list[tuple[str, str, str]]:
    ordem = []
    for grupo in (PRIORIDADE_1, PRIORIDADE_2):
        for comp in grupo:
            if comp in comps:
                for b in bases:
                    for uf in ufs:
                        ordem.append((b, uf, comp))
    return ordem


def registrar_execucao(t0: float, n_pacotes: int, workers: int, terminou: bool) -> None:
    """Histórico cumulativo das rodadas (a aquisição é retomável); rodada interrompida fica sem fim."""
    p_exec = CACHE_PACOTE / "execucao_aquisicao.json"
    hist = json.loads(p_exec.read_text(encoding="utf-8")) if p_exec.exists() else []
    hist = hist if isinstance(hist, list) else [hist]
    inicio = dt.datetime.fromtimestamp(t0, dt.timezone.utc).isoformat(timespec="seconds")
    hist = [h for h in hist if h.get("inicio_utc") != inicio]
    hist.append({"inicio_utc": inicio, "terminou": terminou,
                 "segundos": round(time.time() - t0, 1) if terminou else None, "pacotes_no_plano": n_pacotes,
                 "workers": workers, "workers_fila_grandes": 2, "capacidade_memoria": CAPACIDADE_MEMORIA})
    p_exec.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")


def etapa_aquisicao(bases: list[str], ufs: list[str], comps: list[str], workers: int) -> None:
    t0 = time.time()
    CACHE_PACOTE.mkdir(parents=True, exist_ok=True)
    registrar_execucao(t0, 0, workers, terminou=False)
    log("Listando o FTP da ANS")
    listagem = listar_ftp()
    erros = listagem.pop("__erros_listagem__", {})
    (CACHE_PACOTE / "listagem_ftp.json").write_text(json.dumps(
        {"data_listagem_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
         "arquivos": listagem, "erros": erros}, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    log(f"Listagem: {len(listagem)} arquivos; erros de diretório: {len(erros)}")
    adquirir_referencias()
    ctx = contexto_classificacao()
    memoria = Memoria(CAPACIDADE_MEMORIA)
    pacotes = plano_pacotes(bases, ufs, comps)
    # dentro da mesma prioridade, os maiores primeiro (os pequenos preenchem as vagas)
    def tam(p: tuple[str, str, str]) -> float:
        return sum(tamanho_listagem_bytes((listagem.get(nome_arquivo(*p, parte)) or {}).get("tamanho_listagem"))
                   for parte in ("CONS", "DET"))
    pri = {c: (0 if c in PRIORIDADE_1 else 1) for c in COMPETENCIAS}
    pacotes.sort(key=lambda p: (pri[p[2]], -tam(p)))
    # duas filas: os pacotes grandes (> 400 MB de ZIP, só SP) numa fila de 2 (um baixa enquanto o
    # outro agrega) e o resto noutra, para os grandes não ocuparem todas as vagas esperando memória
    grandes = [p for p in pacotes if tam(p) > 400e6]
    resto = [p for p in pacotes if tam(p) <= 400e6]
    log(f"{len(pacotes)} pacotes ({len(grandes)} grandes); {workers} em paralelo + 2 na fila dos grandes")
    feitos = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex_g, \
            concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex_g.submit(processar_pacote, b, uf, c, listagem, ctx, memoria): (b, uf, c) for b, uf, c in grandes}
        futs.update({ex.submit(processar_pacote, b, uf, c, listagem, ctx, memoria): (b, uf, c) for b, uf, c in resto})
        for fut in concurrent.futures.as_completed(futs):
            b, uf, c = futs[fut]
            feitos += 1
            try:
                r = fut.result()
                st = r.get("status")
            except Exception as exc:  # noqa: BLE001
                st = f"erro {type(exc).__name__}: {exc}"
                _gravar_meta(b, uf, c, {"base": b, "uf": uf, "competencia_realizacao": c, "status": "erro_inesperado",
                                        "detalhe": st, "versao_agregacao": VERSAO_AGREGACAO})
            if st != "aprovado" or feitos % 25 == 0:
                log(f"[{feitos}/{len(pacotes)}] {chave_pacote(b, uf, c)}: {st} ({(time.time() - t0) / 60:.1f} min)")
    registrar_execucao(t0, len(pacotes), workers, terminou=True)
    log(f"Aquisição terminada em {(time.time() - t0) / 60:.1f} min")


# ------------------------------------------------------------------ referências (dicionários, TUSS, SIP)

def trimestres_sip() -> list[str]:
    return sorted({f"{c[:4]}{((int(c[4:]) - 1) // 3) * 3 + 1:02d}" for c in COMPETENCIAS})


def adquirir_referencias() -> None:
    """Dicionários TISS, TUSS (tabelas 22/24/63/64) e SIP trimestral, no cache bruto, com hash."""
    ref = CACHE_BRUTO / "referencias"
    alvo = {f"dicionario_{k}": u for k, u in URL_DICIONARIOS.items()}
    alvo["tuss"] = URL_TUSS
    for t in trimestres_sip():
        alvo[f"sip_{t}"] = URL_SIP.format(trimestre=t)
    registros = {}
    for chave, url in alvo.items():
        destino = ref / url.rsplit("/", 1)[-1]
        try:
            registros[chave] = {**baixar(url, destino), "arquivo_cache": destino.relative_to(ROOT).as_posix()}
        except Exception as exc:  # noqa: BLE001
            registros[chave] = {"url": url, "status": "falha_download", "erro": str(exc)}
    (CACHE_PACOTE / "referencias.json").write_text(json.dumps(registros, ensure_ascii=False, indent=1, sort_keys=True),
                                                    encoding="utf-8")


def ler_referencias() -> dict[str, Any]:
    p = CACHE_PACOTE / "referencias.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def resumo_tuss(refs: dict[str, Any]) -> dict[str, Any] | None:
    """Estrutura da TUSS 22 por capítulo (primeiro dígito), lida da tabela publicada pela ANS."""
    r = refs.get("tuss") or {}
    p = ROOT / r.get("arquivo_cache", "__ausente__")
    if not p.exists():
        return None
    if sha256_arquivo(p) != r.get("sha256"):
        raise RuntimeError("TUSS em cache com SHA-256 diferente do registrado")
    with zipfile.ZipFile(p) as zf:
        nome = next(n for n in zf.namelist() if "tabela_22_" in n)
        t22 = pd.read_csv(zf.open(nome), sep=";", dtype=str, encoding="utf-8")
        nome63 = next(n for n in zf.namelist() if "tabela_63_" in n)
        t63 = pd.read_csv(zf.open(nome63), sep=";", dtype=str, encoding="utf-8")
    t22["capitulo"] = t22["CD_TERMO"].str[:1]
    cap = {}
    for c, g in t22.groupby("capitulo"):
        cap[c] = {"codigos": int(len(g)), "exemplos": [f"{a} {b}" for a, b in g[["CD_TERMO", "NM_TERMO"]].head(3).values]}
    consultas = t22.loc[t22["CD_TERMO"].str.startswith("101"), ["CD_TERMO", "NM_TERMO"]]
    return {
        "arquivo": "pda-049-tabela_22_procedimentos_e_eventos_em_saude.csv (dentro de pda-049-tuss.zip)",
        "codigos_tabela_22": int(len(t22)),
        "por_capitulo": cap,
        "familia_101_consultas": [f"{a} {b}" for a, b in consultas.values],
        "tabela_63_grupos": {a: b for a, b in t63.iloc[:, :2].values},
    }


def comparar_sip(refs: dict[str, Any], tot_nac: pd.DataFrame, completos: dict[str, bool]) -> dict[str, Any]:
    """Compara totais nacionais trimestrais do TISS com o SIP (mapa assistencial) da ANS. Só alerta."""
    itens = {"A": "consultas médicas", "E": "internações", "E1.02": "internações cirúrgicas"}
    sip: dict[str, dict[str, float]] = {}
    arquivos = {}
    for t in trimestres_sip():
        r = refs.get(f"sip_{t}") or {}
        p = ROOT / r.get("arquivo_cache", "__ausente__")
        if not p.exists():
            continue
        if sha256_arquivo(p) != r.get("sha256"):
            raise RuntimeError(f"SIP {t} em cache com SHA-256 diferente do registrado")
        arquivos[t] = {"url": r["url"], "sha256": r["sha256"], "bytes": r["bytes"]}
        with p.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f, delimiter=";"):
                if row["COBERTURA"] != "MÉDICO-HOSPITALAR" or row["ID_ITEM_ASST"] not in itens:
                    continue
                tri = row["ID_TRIMESTRE"].replace("-", "")
                q = float(row["QT_EVENTOS"] or "nan")
                if np.isnan(q):
                    continue
                sip.setdefault(tri, {}).setdefault(row["ID_ITEM_ASST"], 0.0)
                sip[tri][row["ID_ITEM_ASST"]] += q
    linhas = []
    for t in trimestres_sip():
        meses = [f"{t[:4]}{int(t[4:]) + i:02d}" for i in range(3)]
        comp_ok = all(completos.get(m, False) for m in meses)
        sel = tot_nac.loc[tot_nac["competencia_realizacao"].isin(meses)]

        def v(base: str, tipo: str, col: str) -> float:
            return float(sel.loc[(sel["base"] == base) & (sel["tipo"] == tipo), col].sum())

        pares = [
            ("A", "AMB", "consultas", "qt_itens"),
            ("A", "AMB", "consultas", "n_eventos"),
            ("E", "HOSP", "evento_qualquer", "n_eventos"),
            ("E1.02", "HOSP", "cirurgicos", "n_eventos"),
        ]
        for item, base, tipo, col in pares:
            s = (sip.get(t) or {}).get(item)
            x = v(base, tipo, col) if comp_ok else None
            razao = (x / s) if (x is not None and s) else None
            linhas.append({
                "trimestre": t, "item_sip": item, "descricao_sip": itens[item], "tiss_base": base, "tiss_tipo": tipo,
                "tiss_medida": col, "tiss_trimestre_completo": comp_ok, "valor_tiss": x, "valor_sip": s,
                "razao_tiss_sip": razao,
                "alerta": None if razao is None else bool(razao < ALERTA_SIP["razao_min"] or razao > ALERTA_SIP["razao_max"]),
            })
    return {
        "fonte": "SIP — mapa assistencial trimestral, dados abertos da ANS (FTP/PDA/SIP)",
        "arquivos": arquivos,
        "filtro_sip": "COBERTURA = MÉDICO-HOSPITALAR; soma de QT_EVENTOS em todos os portes, modalidades e contratações",
        "tiss": "soma nacional do TISS em todos os municípios, inclusive eventos não atribuídos, sem operadoras odontológicas, todos os CBO",
        "natureza": "comparação descritiva entre sistemas diferentes (SIP por operadora e beneficiário; TISS por evento); não é portão",
        "faixa_alerta": ALERTA_SIP,
        "linhas": linhas,
    }


# ------------------------------------------------------------------ painel

def ler_metas(bases: list[str], ufs: list[str], comps: list[str]) -> dict[tuple[str, str, str], dict[str, Any]]:
    metas = {}
    for b in bases:
        for uf in ufs:
            for c in comps:
                p = caminho_meta(b, uf, c)
                if p.exists():
                    metas[(b, uf, c)] = json.loads(p.read_text(encoding="utf-8"))
    return metas


def status_ausencia(meta: dict[str, Any] | None) -> str:
    if meta is None:
        return "ausente_nao_processado"
    st = meta.get("status", "")
    if st == "ausente_arquivo_nao_publicado":
        return st
    if st == "falha_download":
        return "ausente_falha_download"
    if st.startswith("reprovado_"):
        return "ausente_" + st
    return "ausente_falha_leitura_ou_validacao"


def montar_paineis(municipios: pd.DataFrame, metas: dict[tuple[str, str, str], dict[str, Any]]) -> dict[str, Any]:
    aprovados = {k for k, m in metas.items() if m.get("status") == "aprovado"}
    partes = []
    for k in sorted(aprovados):
        p = caminho_cache(*k)
        if not p.exists() or sha256_arquivo(p) != metas[k].get("sha256_cache"):
            raise RuntimeError(f"cache de {chave_pacote(*k)} ausente ou com SHA-256 diferente do metadado")
        partes.append(pd.read_parquet(p))
    cache = pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(
        columns=["base", "uf", "competencia_realizacao", "nivel", "tipo", "n_eventos", "qt_itens", "n_linhas_det",
                 "n_linhas_qt_vazia", "status_municipio", "co_ibge", "particao_cbo", "operadora_odontologica"])
    medico = cache.loc[~cache["operadora_odontologica"].astype(bool)]
    atrib = medico.loc[medico["status_municipio"] == "ok"]
    if len(atrib) and not atrib["co_ibge"].isin(set(municipios["co_ibge"])).all():
        raise RuntimeError("código de município atribuído fora da lista do IBGE")
    uf_do_prefixo = {v: k for k, v in prefixo_uf(municipios).items()}
    if len(atrib) and (atrib["co_ibge"].str[:2].map(uf_do_prefixo) != atrib["uf"]).any():
        raise RuntimeError("município atribuído de UF diferente da UF do arquivo")

    saidas: dict[str, Any] = {}
    for base, grupos, destino in (("AMB", GRUPOS_SAIDA_AMB, PAINEL_AMB), ("HOSP", GRUPOS_SAIDA_HOSP, PAINEL_HOSP)):
        sub = atrib.loc[(atrib["base"] == base) & (atrib["nivel"] == "painel")]
        obs = []
        for g, parts in grupos.items():
            s = sub.loc[sub["particao_cbo"].isin(parts)]
            s = (s.groupby(["co_ibge", "competencia_realizacao", "tipo"], as_index=False)
                 [["n_eventos", "qt_itens", "n_linhas_det", "n_linhas_qt_vazia"]].sum())
            s["grupo_cbo"] = g
            obs.append(s)
        obs = pd.concat(obs, ignore_index=True).rename(columns={"tipo": "tipo_procedimento"})
        tem_evento = (atrib.loc[atrib["base"] == base, ["co_ibge", "competencia_realizacao"]]
                      .drop_duplicates().assign(_com_evento=True))
        esq = municipios.merge(pd.DataFrame({"competencia_realizacao": COMPETENCIAS}), how="cross")
        esq = esq.merge(pd.DataFrame({"tipo_procedimento": list(TIPOS_PAINEL)}), how="cross")
        esq = esq.merge(pd.DataFrame({"grupo_cbo": list(grupos)}), how="cross")
        painel = esq.merge(obs, on=["co_ibge", "competencia_realizacao", "tipo_procedimento", "grupo_cbo"],
                           how="left", validate="one_to_one")
        st_pac = pd.DataFrame(
            [{"uf": uf, "competencia_realizacao": c,
              "_status": "aprovado" if (base, uf, c) in aprovados else status_ausencia(metas.get((base, uf, c)))}
             for uf in UFS for c in COMPETENCIAS])
        painel = painel.merge(st_pac, on=["uf", "competencia_realizacao"], how="left", validate="many_to_one")
        painel = painel.merge(tem_evento, on=["co_ibge", "competencia_realizacao"], how="left", validate="many_to_one")
        st = painel["_status"]
        com_ev = painel["_com_evento"].fillna(False).astype(bool)
        aprov = st == "aprovado"
        painel["status_cobertura"] = np.where(aprov & com_ev, STATUS_OBSERVADO, np.where(aprov, STATUS_ZERO, st))
        for c in ("n_eventos", "n_linhas_det", "n_linhas_qt_vazia"):
            painel[c] = painel[c].astype("Int64").where(~aprov | painel[c].notna(), 0).where(aprov, pd.NA).astype("Int64")
        painel["qt_itens"] = painel["qt_itens"].astype("Float64").where(~aprov | painel["qt_itens"].notna(), 0.0) \
            .where(aprov, pd.NA).astype("Float64")
        painel["natureza_dos_dados"] = "EMPIRICO"
        painel = painel[COLUNAS_PAINEL].sort_values(
            ["co_ibge", "competencia_realizacao", "tipo_procedimento", "grupo_cbo"], kind="mergesort").reset_index(drop=True)
        if len(obs) and (painel["n_eventos"].sum() != obs.loc[obs["co_ibge"].isin(set(municipios["co_ibge"])), "n_eventos"].sum()):
            raise RuntimeError(f"{base}: soma de eventos do painel difere da soma do cache")
        saidas[base] = (painel, destino)

    nao = medico.loc[(medico["status_municipio"] != "ok") & (medico["nivel"] == "painel")]
    linhas_nao = []
    for base, grupos in (("AMB", GRUPOS_SAIDA_AMB), ("HOSP", GRUPOS_SAIDA_HOSP)):
        sb = nao.loc[nao["base"] == base]
        for g, parts in grupos.items():
            s = sb.loc[sb["particao_cbo"].isin(parts)]
            s = (s.groupby(["base", "uf", "competencia_realizacao", "status_municipio", "tipo"], as_index=False)
                 [["n_eventos", "qt_itens", "n_linhas_det"]].sum())
            s["grupo_cbo"] = g
            linhas_nao.append(s)
    nao_atr = pd.concat(linhas_nao, ignore_index=True).rename(
        columns={"status_municipio": "motivo_nao_atribuido", "tipo": "tipo_procedimento"})
    nao_atr["natureza_dos_dados"] = "EMPIRICO"
    nao_atr = nao_atr[COLUNAS_NAO_ATRIB].sort_values(COLUNAS_NAO_ATRIB[:6], kind="mergesort").reset_index(drop=True)

    fino = cache.loc[cache["nivel"] == "fino"].copy()
    fino["escopo"] = np.where(fino["operadora_odontologica"].astype(bool), "operadora_odontologica",
                              np.where(fino["status_municipio"] == "ok", "atribuido", "nao_atribuido"))
    itens = (fino.groupby(["base", "uf", "competencia_realizacao", "escopo", "tipo"], as_index=False)
             [["n_eventos", "qt_itens", "n_linhas_det", "n_linhas_qt_vazia"]].sum()
             .rename(columns={"tipo": "categoria_item"}))
    itens["natureza_dos_dados"] = "EMPIRICO"
    itens = itens.sort_values(["base", "uf", "competencia_realizacao", "escopo", "categoria_item"],
                              kind="mergesort").reset_index(drop=True)

    # totais nacionais (todos os municípios e não atribuídos, sem operadora odontológica) para validação;
    # tipos do painel + evento_qualquer e evento_sem_item_det do nível fino (sem nome repetido entre níveis)
    tot = medico.loc[(medico["nivel"] == "painel")
                     | ((medico["nivel"] == "fino") & medico["tipo"].isin(["evento_qualquer", "evento_sem_item_det"]))]
    assert not set(TIPOS_PAINEL) & {"evento_qualquer", "evento_sem_item_det"}
    tot_nac = (tot.groupby(["base", "competencia_realizacao", "tipo"], as_index=False)[["n_eventos", "qt_itens"]].sum())
    tot_uf = (tot.loc[tot["tipo"].isin(["todos_nao_odonto", "evento_qualquer"])]
              .groupby(["base", "uf", "competencia_realizacao", "tipo"], as_index=False)["n_eventos"].sum())
    saidas["nao_atribuido"] = nao_atr
    saidas["itens"] = itens
    saidas["tot_nac"] = tot_nac
    saidas["tot_uf"] = tot_uf
    saidas["aprovados"] = aprovados
    return saidas


def alertas_queda(tot_uf: pd.DataFrame) -> list[dict[str, Any]]:
    """Meses anormais por base × UF (eventos de qualquer tipo). Só sinaliza; nada é corrigido."""
    out = []
    s = tot_uf.loc[tot_uf["tipo"] == "evento_qualquer"]
    for (b, uf), g in s.groupby(["base", "uf"]):
        g = g.sort_values("competencia_realizacao")
        med = float(g["n_eventos"].median())
        ant = None
        for r in g.itertuples(index=False):
            motivos = []
            if med > 0 and r.n_eventos < ALERTA_QUEDA["razao_mediana_min"] * med:
                motivos.append("abaixo_de_metade_da_mediana_da_uf")
            if med > 0 and r.n_eventos > ALERTA_QUEDA["razao_mediana_max"] * med:
                motivos.append("acima_do_dobro_da_mediana_da_uf")
            if ant and ant[1] > 0 and (ant[1] - r.n_eventos) / ant[1] > ALERTA_QUEDA["queda_mes_a_mes_max"]:
                motivos.append(f"queda_de_mais_de_40pct_contra_{ant[0]}")
            if motivos:
                out.append({"base": b, "uf": uf, "competencia_realizacao": r.competencia_realizacao,
                            "n_eventos": int(r.n_eventos), "mediana_uf": med, "motivos": motivos})
            ant = (r.competencia_realizacao, r.n_eventos)
    return out


def gravar_parquet(df: pd.DataFrame, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    tab = pa.Table.from_pandas(df, preserve_index=False)
    tmp = destino.with_suffix(".parquet.tmp")
    pq.write_table(tab, tmp, compression="zstd", compression_level=9, use_dictionary=True)
    tmp.replace(destino)


def _somar_dicts(dicts: Iterable[dict[str, int]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for d in dicts:
        for k, v in (d or {}).items():
            out[k] = out.get(k, 0) + int(v)
    return dict(sorted(out.items()))


def etapa_painel() -> int:
    t0 = time.time()
    municipios = carregar_municipios()
    ctx = contexto_classificacao()
    metas = ler_metas(list(BASES), list(UFS), COMPETENCIAS)
    if not metas:
        raise SystemExit("nenhum pacote em cache; rode --etapa aquisicao")
    refs = ler_referencias()
    s = montar_paineis(municipios, metas)
    aprovados = s["aprovados"]

    # cobertura UF × mês
    cob = []
    for b in BASES:
        for uf in UFS:
            for c in COMPETENCIAS:
                m = metas.get((b, uf, c))
                d = (m or {}).get("diagnostico") or {}
                cob.append({
                    "base": b, "uf": uf, "competencia_realizacao": c,
                    "status": "aprovado" if (b, uf, c) in aprovados else status_ausencia(m),
                    "detalhe": (m or {}).get("detalhe"),
                    "linhas_cons": d.get("linhas_cons"), "linhas_det": d.get("linhas_det"),
                    "taxa_juncao_det": d.get("taxa_juncao_det"),
                    "eventos_sem_item_det": d.get("eventos_cons_sem_item_det"),
                    "fracao_mes_divergente_cons": d.get("fracao_mes_divergente_cons"),
                    "data_publicacao_cons": ((m or {}).get("arquivos", {}).get("CONS") or {}).get("last_modified_http"),
                    "data_publicacao_det": ((m or {}).get("arquivos", {}).get("DET") or {}).get("last_modified_http"),
                    "natureza_dos_dados": "EMPIRICO",
                })
    cob = pd.DataFrame(cob)
    completos = {c: bool((cob.loc[(cob["competencia_realizacao"] == c), "status"] == "aprovado").all())
                 for c in COMPETENCIAS}
    sip = comparar_sip(refs, s["tot_nac"], completos) if refs else None
    alertas = alertas_queda(s["tot_uf"])
    diags = [m.get("diagnostico") or {} for k, m in metas.items() if k in aprovados]
    juncoes = [d["taxa_juncao_det"] for d in diags if d.get("taxa_juncao_det") is not None]
    validacao = {
        "portoes_por_pacote": PORTOES,
        "pacotes_planejados": len(BASES) * len(UFS) * len(COMPETENCIAS),
        "pacotes_aprovados": len(aprovados),
        "pacotes_por_status": cob["status"].value_counts().sort_index().to_dict(),
        "juncao_det_cons": {"minima": min(juncoes) if juncoes else None, "maxima": max(juncoes) if juncoes else None,
                            "pacotes_com_juncao_menor_que_1": int(sum(j < 1 for j in juncoes)),
                            "linhas_det_nao_juntadas": int(sum(d.get("linhas_det_nao_juntadas", 0) for d in diags))},
        "eventos_por_status_municipio": _somar_dicts(d.get("eventos_por_status_municipio") for d in diags),
        "eventos_operadora_odontologica_excluidos": int(sum(d.get("eventos_operadora_odontologica", 0) for d in diags)),
        "eventos_cons_sem_item_det": int(sum(d.get("eventos_cons_sem_item_det", 0) for d in diags)),
        "quantidades": _somar_dicts(d.get("quantidades") for d in diags),
        "linhas_det_por_tabela": _somar_dicts(d.get("linhas_det_por_tabela") for d in diags),
        "linhas_det_tuss22_por_capitulo": _somar_dicts(d.get("linhas_det_tuss22_por_capitulo") for d in diags),
        "linhas_det_tuss63_por_grupo": _somar_dicts(d.get("linhas_det_tuss63_por_grupo") for d in diags),
        "eventos_amb_por_cbo": _somar_dicts(d.get("eventos_por_cbo") for k, m in metas.items() if k in aprovados
                                             for d in [m.get("diagnostico") or {}]),
        "codigos_municipio_invalidos_ou_de_outra_uf": sorted({c for d in diags
                                                              for c in d.get("codigos_municipio_invalidos_ou_de_outra_uf", [])}),
        "municipios_validos": "lista do IBGE em output/aquisicao/populacao_censo2022_municipios.csv (co_ibge_6d)",
        "alertas_queda": alertas,
        "comparacao_sip": sip,
        "totais_nacionais_d_tiss": ("comparação com o D-TISS não feita: a página da ANS "
                                    "(gov.br/ans/.../dados-e-indicadores-do-setor/d-tiss-painel-dos-dados-do-tiss, "
                                    "consultada em 19/10/2026) só publica painéis Power BI, sem arquivo de totais para "
                                    "download reprodutível; o agregado publicado usado é o SIP trimestral"),
        "natureza_dos_dados": "EMPIRICO",
    }
    # gravação (só depois de montar tudo em memória)
    for base in ("AMB", "HOSP"):
        painel, destino = s[base]
        gravar_parquet(painel, destino)
    gravar_parquet(s["nao_atribuido"], NAO_ATRIBUIDO)
    gravar_parquet(s["itens"], ITENS_FINOS)
    cob.to_csv(COBERTURA, index=False)
    VALIDACAO.write_text(json.dumps(validacao, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")
    gravar_manifesto(metas, aprovados, refs, ctx, s, cob, time.time() - t0)
    gravar_resumo(s, cob, validacao)
    log(f"Painéis gravados: AMB {len(s['AMB'][0]):,} linhas, HOSP {len(s['HOSP'][0]):,} linhas; "
        f"{len(aprovados)} pacotes aprovados")
    return 0


def gravar_manifesto(metas: dict, aprovados: set, refs: dict, ctx: dict, s: dict, cob: pd.DataFrame,
                     segundos_painel: float) -> None:
    arquivos = []
    for k in sorted(metas):
        m = metas[k]
        for parte, a in sorted((m.get("arquivos") or {}).items()):
            arquivos.append({
                "pacote": chave_pacote(*k), "parte": parte, "nome": a.get("nome"), "url": a.get("url"),
                "bytes": a.get("bytes"), "sha256": a.get("sha256"), "data_download_utc": a.get("data_download_utc"),
                "last_modified_http": a.get("last_modified_http"), "data_listagem": a.get("data_listagem"),
                "membro_csv": a.get("membro_csv"), "bytes_csv": a.get("bytes_csv"), "linhas": a.get("linhas"),
                "segundos_download": a.get("segundos_download"),
            })
    exec_p = CACHE_PACOTE / "execucao_aquisicao.json"
    execucao = json.loads(exec_p.read_text(encoding="utf-8")) if exec_p.exists() else None
    esquemas: dict[str, list[str]] = {}
    for k, m in metas.items():
        for parte, a in (m.get("arquivos") or {}).items():
            cols = a.get("colunas_arquivo")
            if cols:
                esquemas.setdefault(f"{k[0]}_{parte}:" + ";".join(cols), []).append(chave_pacote(*k))
    paineis = {}
    for base in ("AMB", "HOSP"):
        painel, destino = s[base]
        paineis[base] = {"arquivo": destino.relative_to(ROOT).as_posix(), "sha256": sha256_arquivo(destino),
                         "linhas": int(len(painel)), "colunas": list(painel.columns)}
    for nome, destino, df in (("nao_atribuido", NAO_ATRIBUIDO, s["nao_atribuido"]), ("itens", ITENS_FINOS, s["itens"])):
        paineis[nome] = {"arquivo": destino.relative_to(ROOT).as_posix(), "sha256": sha256_arquivo(destino),
                         "linhas": int(len(df)), "colunas": list(df.columns)}
    for nome, destino in (("cobertura", COBERTURA), ("validacao", VALIDACAO)):
        paineis[nome] = {"arquivo": destino.relative_to(ROOT).as_posix(), "sha256": sha256_arquivo(destino)}
    manifesto = {
        "gerador": "scripts/aquisicao/a14_adquirir_tiss_ans.py",
        "protocolo": "docs/06_execucao/47_protocolo_producao_especializada.md (§2, §3, §6, §9; aquisição TISS)",
        "estatuto": "PROTOCOLO_47_POS_SINTESE",
        "natureza_dos_dados": "EMPIRICO",
        "data_execucao_painel": dt.date.today().isoformat(),
        "fonte": {
            "nome": "ANS — dados abertos TISS: Procedimentos Ambulatoriais por UF e Procedimentos Hospitalares por UF",
            "url_base": URL_BASE,
            "modelo_url": URL_BASE + "{AMBULATORIAL|HOSPITALAR}/<ano>/<UF>/<UF>_<AAAAMM>_{AMB|HOSP}_{CONS|DET}.zip",
            "formato": "CSV ';' entre aspas, UTF-8 com BOM, vírgula decimal, um CSV por ZIP",
            "arquivos_usados": "CONS (evento) e DET (itens); REM só listado",
            "dicionarios": {k: refs.get(f"dicionario_{k}") for k in URL_DICIONARIOS},
            "tuss": refs.get("tuss"),
        },
        "unidade": "município do prestador executante (CD_MUNICIPIO_PRESTADOR, 6 dígitos IBGE) × mês de realização (DT_REALIZACAO no ambulatorial, ANO_MES_EVENTO no hospitalar) × tipo de procedimento × grupo de CBO do evento",
        "chaves": {"juncao": "ID_EVENTO_ATENCAO_SAUDE (DET -> CONS, no mesmo par UF × mês)",
                   "painel": ["co_ibge", "competencia_realizacao", "tipo_procedimento", "grupo_cbo"]},
        "competencias_planejadas": COMPETENCIAS,
        "prioridade_1": PRIORIDADE_1,
        "prioridade_2": PRIORIDADE_2,
        "limite": f"nenhum arquivo de mês >= {LIMITE_EXCLUSIVO} é baixado ou lido",
        "ufs": list(UFS),
        "bases": BASES,
        "entradas_locais": {
            p.relative_to(ROOT).as_posix(): {"sha256": sha256_arquivo(p), "bytes": p.stat().st_size, "uso": uso}
            for p, uso in ((POPULACAO_FILE, "só a lista co_ibge_6d e a UF (validação de código); população não usada"),
                           (PONTE_FILE, "CBO-alvo via a09.carregar_ponte()"),
                           (A09_FILE, "constantes e regra de grupos de CBO importadas"))
        },
        "classificacao": {
            "cbo_alvo": ctx["alvo"], "versao_ponte": ctx["versao_ponte"],
            "generalistas": list(A09.GENERALISTAS), "mfc": A09.MFC, "prefixos_medicos_a09": list(A09.PREFIXOS_MEDICOS),
            "particao_evento": list(PARTICOES_CBO),
            "grupos_saida_ambulatorial": {k: list(v) for k, v in GRUPOS_SAIDA_AMB.items()},
            "grupos_saida_hospitalar": {k: list(v) for k, v in GRUPOS_SAIDA_HOSP.items()},
            "categorias_item": list(CATEGORIAS),
            "tipos_painel": {k: list(v) for k, v in TIPOS_PAINEL.items()},
            "modalidades_odontologicas_excluidas": list(MODALIDADES_ODONTO),
            "estrutura_tuss22": resumo_tuss(refs),
        },
        "status_cobertura": {
            STATUS_OBSERVADO: "UF × mês aprovado e município com pelo menos um evento atribuído no mês (zeros da célula são observados)",
            STATUS_ZERO: "UF × mês aprovado e município sem nenhum evento reportado de plano no mês: zero de eventos reportados, não de produção",
            "ausente_*": "UF × mês sem dado utilizável (não publicado, falha de download, leitura ou validação, ou não processado): NA, nunca zero",
        },
        "portoes": PORTOES,
        "alertas": {"queda": ALERTA_QUEDA, "sip": ALERTA_SIP},
        "execucao_aquisicao": execucao,
        "segundos_montagem_painel": round(segundos_painel, 1),
        "bytes_baixados_total": int(sum(a["bytes"] or 0 for a in arquivos)),
        "arquivos_baixados": len([a for a in arquivos if a.get("sha256")]),
        "pacotes_aprovados": len(aprovados),
        "pacotes_por_status": cob["status"].value_counts().sort_index().to_dict(),
        "esquemas_lidos": {k.split(":", 1)[0] + ": " + k.split(":", 1)[1]: {"pacotes": len(v), "exemplo": sorted(v)[0]}
                           for k, v in sorted(esquemas.items())},
        "saidas": paineis,
        "arquivos": arquivos,
        "cegamento": "nenhum número foi tabulado por faixa de IVS, lado de corte, bolsa ou tratamento; o IVS não é lido",
    }
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=1, default=float) + "\n", encoding="utf-8")


def _n(x: Any) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/d"
    if isinstance(x, (int, np.integer)):
        return f"{int(x):,}".replace(",", ".")
    return f"{float(x):,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gravar_resumo(s: dict, cob: pd.DataFrame, validacao: dict) -> None:
    """Resumo legível gerado das saídas (totais nacionais e cobertura; nada por IVS)."""
    L = ["# A14 — resumo gerado do TISS/ANS", "",
         f"Gerado por `scripts/aquisicao/a14_adquirir_tiss_ans.py` em {dt.date.today().isoformat()}. Não editar à mão. "
         "Natureza dos dados: EMPIRICO. Totais nacionais e cobertura por UF × mês; nada por faixa, corte ou tratamento.", "",
         "## Cobertura (pacotes UF × mês)", "",
         "| Base | Status | Pacotes |", "|---|---|---:|"]
    for (b, st), n in cob.groupby(["base", "status"]).size().items():
        L.append(f"| {b} | {st} | {_n(int(n))} |")
    L += ["", "### Meses com todas as 27 UFs aprovadas", "", "| Base | Meses completos | Primeiro | Último |", "|---|---:|---|---|"]
    for b, g in cob.groupby("base"):
        comp = sorted(c for c, gg in g.groupby("competencia_realizacao") if (gg["status"] == "aprovado").all())
        L.append(f"| {b} | {len(comp)} | {comp[0] if comp else 'n/d'} | {comp[-1] if comp else 'n/d'} |")
    falt = cob.loc[cob["status"] != "aprovado"]
    if len(falt):
        L += ["", "### Pacotes não aprovados", "", "| Base | UF | Mês | Status | Detalhe |", "|---|---|---|---|---|"]
        for r in falt.itertuples(index=False):
            L.append(f"| {r.base} | {r.uf} | {r.competencia_realizacao} | {r.status} | {(r.detalhe or '')[:120]} |")
    j = validacao["juncao_det_cons"]
    L += ["", "## Validações", "",
          f"- Junção DET → CONS por pacote aprovado: mínima {_n(j['minima'])}, máxima {_n(j['maxima'])}; "
          f"pacotes com junção < 1: {_n(j['pacotes_com_juncao_menor_que_1'])}; linhas DET não juntadas: {_n(j['linhas_det_nao_juntadas'])}.",
          f"- Eventos CONS sem item DET: {_n(validacao['eventos_cons_sem_item_det'])}.",
          f"- Eventos de operadoras odontológicas excluídos: {_n(validacao['eventos_operadora_odontologica_excluidos'])}.",
          f"- Alertas de queda ou salto (base × UF × mês): {_n(len(validacao['alertas_queda']))}.", "",
          "### Eventos por status do município (pacotes aprovados, todas as operadoras)", "",
          "| Status | Eventos |", "|---|---:|"]
    for k, v in validacao["eventos_por_status_municipio"].items():
        L.append(f"| {k} | {_n(v)} |")
    L += ["", "### Quantidades informadas (linhas DET)", "", "| Caso | Linhas |", "|---|---:|"]
    for k, v in validacao["quantidades"].items():
        L.append(f"| {k} | {_n(v)} |")
    L += ["", "### Linhas DET por tabela TUSS", "", "| Tabela | Linhas |", "|---|---:|"]
    for k, v in validacao["linhas_det_por_tabela"].items():
        L.append(f"| {k or '(vazio)'} | {_n(v)} |")
    L += ["", "### Linhas DET da TUSS 22 por capítulo", "", "| Capítulo | Linhas |", "|---|---:|"]
    for k, v in validacao["linhas_det_tuss22_por_capitulo"].items():
        L.append(f"| {k or '(vazio)'} | {_n(v)} |")
    amb = s["AMB"][0]
    obs = amb.loc[~amb["status_cobertura"].str.startswith("ausente_")]
    pv = obs.groupby(["tipo_procedimento", "grupo_cbo"])["n_eventos"].sum().unstack()
    grupos = [g for g in GRUPOS_SAIDA_AMB if g != "todos_cbo"]
    L += ["", "## Participação de cada grupo de CBO nos eventos ambulatoriais atribuídos (todos os meses)", "",
          "Fração de `n_eventos` do grupo sobre `todos_cbo`, por tipo; `mfc_225130` está contida em `especialistas_nao_alvo`.", "",
          "| Tipo | " + " | ".join(grupos) + " |", "|---|" + "---:|" * len(grupos)]
    for t in TIPOS_PAINEL:
        L.append(f"| {t} | " + " | ".join(_n(float(pv.loc[t, g] / pv.loc[t, "todos_cbo"])) for g in grupos) + " |")
    tn = s["tot_nac"]
    for base in ("AMB", "HOSP"):
        sub = tn.loc[(tn["base"] == base) & tn["tipo"].isin(list(TIPOS_PAINEL) + ["evento_qualquer"])]
        if not len(sub):
            continue
        pv = sub.pivot_table(index="competencia_realizacao", columns="tipo", values="n_eventos", aggfunc="sum")
        cols = [c for c in ["evento_qualquer", "todos_nao_odonto", "consultas", "exames", "cirurgicos", "outros"] if c in pv]
        L += ["", f"## Eventos por mês, Brasil, {base} (todos os CBO, inclusive não atribuídos; sem operadoras odontológicas)", "",
              "Só meses com pacotes aprovados entram na soma; mês incompleto é marcado.", "",
              "| Mês | Completo | " + " | ".join(cols) + " |", "|---|---|" + "---:|" * len(cols)]
        for c, r in pv.iterrows():
            ok = bool((cob.loc[(cob["base"] == base) & (cob["competencia_realizacao"] == c), "status"] == "aprovado").all())
            L.append(f"| {c} | {'sim' if ok else 'não'} | " + " | ".join(_n(int(r[x])) if pd.notna(r[x]) else "n/d" for x in cols) + " |")
    sip = validacao.get("comparacao_sip")
    if sip:
        L += ["", "## Comparação com o SIP (descritiva, não é portão)", "",
              "| Trimestre | Item SIP | TISS | Medida | Completo | TISS | SIP | Razão | Alerta |", "|---|---|---|---|---|---:|---:|---:|---|"]
        for r in sip["linhas"]:
            L.append(f"| {r['trimestre']} | {r['item_sip']} {r['descricao_sip']} | {r['tiss_base']} {r['tiss_tipo']} | "
                     f"{r['tiss_medida']} | {'sim' if r['tiss_trimestre_completo'] else 'não'} | "
                     f"{_n(r['valor_tiss']) if r['valor_tiss'] is not None else 'n/d'} | {_n(r['valor_sip'])} | "
                     f"{_n(r['razao_tiss_sip'])} | {r['alerta']} |")
    if validacao["alertas_queda"]:
        L += ["", "## Alertas de queda ou salto (sinalizados, não corrigidos)", "",
              "| Base | UF | Mês | Eventos | Mediana da UF | Motivos |", "|---|---|---|---:|---:|---|"]
        for a in validacao["alertas_queda"]:
            L.append(f"| {a['base']} | {a['uf']} | {a['competencia_realizacao']} | {_n(a['n_eventos'])} | "
                     f"{_n(a['mediana_uf'])} | {', '.join(a['motivos'])} |")
    RESUMO.write_text("\n".join(L) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ verificar

def verificar() -> int:
    """Confere as saídas versionadas contra o manifesto, sem rede e sem gravar."""
    erros = []
    if not MANIFESTO.exists():
        raise SystemExit(f"verificar: {MANIFESTO.relative_to(ROOT)} ausente; rode --etapa tudo")
    man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    for nome, reg in (man.get("saidas") or {}).items():
        p = ROOT / reg["arquivo"]
        if not p.exists():
            erros.append(f"saída ausente: {reg['arquivo']}")
            continue
        if sha256_arquivo(p) != reg["sha256"]:
            erros.append(f"SHA-256 de {reg['arquivo']} difere do manifesto")
        if "linhas" in reg and p.suffix == ".parquet":
            meta = pq.read_metadata(p)
            if meta.num_rows != reg["linhas"] or meta.schema.to_arrow_schema().names != reg["colunas"]:
                erros.append(f"{reg['arquivo']}: linhas ou colunas diferentes do manifesto")
    for nome in ("AMB", "HOSP"):
        if (man.get("saidas") or {}).get(nome, {}).get("colunas") != COLUNAS_PAINEL:
            erros.append(f"painel {nome} sem as colunas de COLUNAS_PAINEL")
    if man.get("competencias_planejadas") != COMPETENCIAS:
        erros.append("plano de competências do script mudou desde a construção")
    for rel, reg in (man.get("entradas_locais") or {}).items():
        p = ROOT / rel
        if not p.exists() or sha256_arquivo(p) != reg["sha256"]:
            erros.append(f"entrada local ausente ou alterada: {rel}")
    if erros:
        for e in erros:
            log(f"VERIFICAÇÃO REPROVADA: {e}")
        raise SystemExit("verificar: saídas do a14 não conferem; refaça com --etapa painel ou --etapa tudo")
    log(f"a14 conferido sem rede: {man['pacotes_aprovados']} pacotes aprovados; nada gravado")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=["verificar", "aquisicao", "painel", "tudo"], default="verificar")
    ap.add_argument("--workers", type=int, default=3)  # fila dos pacotes não grandes
    ap.add_argument("--bases", nargs="*", choices=list(BASES), default=list(BASES))
    ap.add_argument("--ufs", nargs="*", default=list(UFS))
    ap.add_argument("--competencias", nargs="*", help="subconjunto (depuração)")
    args = ap.parse_args()
    if args.etapa == "verificar":
        return verificar()
    comps = sorted(args.competencias) if args.competencias else COMPETENCIAS
    for c in comps:
        checar_limite(c)
    for uf in args.ufs:
        if uf not in UFS:
            raise SystemExit(f"UF inválida: {uf}")
    if args.etapa in ("aquisicao", "tudo"):
        etapa_aquisicao(args.bases, args.ufs, comps, args.workers)
    if args.etapa in ("painel", "tudo"):
        return etapa_painel()
    return 0


if __name__ == "__main__":
    sys.exit(main())
