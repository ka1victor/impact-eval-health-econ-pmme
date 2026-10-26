"""Adendo 48b: H1 só com vagas imediatas (HI-1, HI-2 e HI-s1 a HI-s8).

Especificação congelada antes das contas: `docs/06_execucao/48b_adendo_H1_vagas_imediatas.md` (26/10/2026,
commit 666aee1; SHA-256 conferido abaixo). Estatuto de toda saída: `ADENDO_48B_POS_RESULTADO`;
`natureza_dos_dados = EMPIRICO`. É uma correção de definição registrada como pós-resultado: as medidas que misturam
vaga imediata e cadastro reserva já tinham sido vistas (docs 49, 49b e 57l).

O que faz
---------
1. Reprodução antes de qualquer conta nova, a partir das mesmas entradas (outcomes do 12, IVS oficial do a08) e
   dos mesmos estimadores (`rdd_lib`, funções do 23):
   - A3 (célula aberta preenchida, efeitos fixos de curso × ciclo e tipo de vaga) por corte, contra
     `NA_estimativas.csv` (script 24);
   - N1 S-a (vagas preenchidas com controle das vagas oferecidas) por corte, contra `N_estimativas.csv` (script 23);
   - as linhas do 49b §14 por tipo de célula (taxa nas células só de vagas imediatas e só de cadastro reserva) e com
     só vagas imediatas no denominador, contra `ND_estimativas.csv` (script 23b), e a contagem de células por tipo
     contra `ND_resumo.json`.
   Se algo não bater, o script para sem gravar nada.
2. Primárias (Holm entre as quatro): HI-1 (célula com vaga imediata preenchida na 1ª chamada, efeitos fixos de
   curso × ciclo) e HI-2 (médicos alocados na 1ª chamada em células com vaga imediata, por município, controle =
   vagas imediatas dessas células com coeficiente por ciclo), cada corte separado, ciclos 1–3 empilhados com
   intercepto e inclinações por ciclo, local linear triangular, h = 0,050, CR1 por município.
3. Secundárias HI-s1 a HI-s8, todas relatadas; q-valores BKY entre as secundárias que testam salto zero.

Nota datada §7 do adendo (commit 4326241, depois da auditoria 36): no ciclo 2, o tipo de vaga (imediata, mista,
só de reserva) e as vagas imediatas da amostra e do controle vêm do quadro retificado de 13/02/2026, vigente na
inscrição, lido com `scripts/auditoria_H1/a36_leitura.py` (`ler_quadro`); o quadro de 19/03/2026 do pipeline foi
refeito depois do resultado preliminar. A reprodução usa o quadro do pipeline (é o das saídas reproduzidas), e a
versão com 19/03 sai como sensibilidade rotulada "tipo de vaga pós-resultado (não usar)" (linhas `SENS-19MAR`).

Definições (decisões registradas em `HI_resumo.json`)
-----------------------------------------------------
- "Preenchida" em HI-1 = a do A3 (`n_alocados_ch1 >= 1`; a fonte do "alocado" muda por ciclo: no ciclo 1,
  confirmação de local na alocação sub judice; nos ciclos 2–3, SITUAÇÃO ALOCADO). Como essa definição já é
  "≥ 1 alocado na 1ª chamada" em todos os ciclos, a HI-s2 relata a outra definição que a base tem, a F1.3 do
  protocolo 40 (ciclo 1: confirmação ou homologação), e confere que a forma literal coincide com HI-1.
- A base não registra em que tipo de vaga cada alocado entrou: nas células mistas contam todos os alocados da
  célula, e o controle de HI-2 são as vagas imediatas (limite registrado).
- HI-s5 usa a F1.4 do protocolo 40 (`f1_4_preenchida_ate_ch2`, ciclos 1 e 2).

Integridade: nada simulado nem imputado; ausência fica ausente e é contada; o arquivo local de IVS da auditoria 16
não é lido; nenhum CNES é lido; as saídas `N_*`, `NA_*`, `ND_*`, `DQ_*` não são regravadas.

Uso
---
    python3 scripts/rdd_bolsa/40_h1_vagas_imediatas.py                  # calcula e grava as saídas
    python3 scripts/rdd_bolsa/40_h1_vagas_imediatas.py --atualizar-doc  # idem e regrava o doc 57n
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
import textwrap
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


T23 = _importar(DIR_RDD / "23_estimar_contagem_vagas.py", "contagem_vagas_para_hi")
T36 = _importar(DIR_RDD / "36_equivalencia_H1.py", "equivalencia_para_hi")
# Leitura do quadro de 13/02/2026 do ciclo 2 (auditoria 36; só lê data/raw/, sem nome nem CPF).
A36L = _importar(ROOT / "scripts" / "auditoria_H1" / "a36_leitura.py", "a36_leitura_para_hi")
L = T23.L
E6 = T23.E6

# ---------------------------------------------------------------------------
# Parâmetros do adendo (constantes permitidas: cortes, h, margens, rótulos)
# ---------------------------------------------------------------------------

OUT = T23.OUT
OUTC = T23.OUTC
ARQ_VC = T23.ARQ_VC
ARQ_VM = T23.ARQ_VM
ARQ_U = T23.ARQ_U
A08 = T23.A08
DICIONARIO = T23.DICIONARIO
NA_EST = OUT / "NA_estimativas.csv"
N_EST = OUT / "N_estimativas.csv"
N_RES = OUT / "N_resumo.json"
ND_EST = OUT / "ND_estimativas.csv"
ND_RES = OUT / "ND_resumo.json"
ADENDO = ROOT / "docs" / "06_execucao" / "48b_adendo_H1_vagas_imediatas.md"
DOC = ROOT / "docs" / "06_execucao" / "57n_resultados_H1_vagas_imediatas.md"
NOME_EST = "HI_estimativas.csv"
NOME_RESUMO = "HI_resumo.json"
DIR_FIG = OUT / "HI_figuras"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "ADENDO_48B_POS_RESULTADO"
NATUREZA = "EMPIRICO"
COMMIT_CONGELAMENTO = "666aee1"
SHA_ADENDO_ORIGINAL = "383768d27bf87fc76b3ae1f5d518c318f7d7668360a28cf758a4e0e4a0b0efed"
COMMIT_NOTA_7 = "4326241"           # nota datada §7: tipo de vaga do ciclo 2 pelo quadro de 13/02/2026
SHA_ADENDO_CONGELADO = "0dc4a6737c364d411041f4733f86c0f578b742c972935ee62b8202daa7c1bb64"   # com a §7
AUD36 = ROOT / "docs" / "auditorias" / "36_auditoria_dados_H1.md"
ARQ_C2_13FEV = A36L.ARQ["c2_quadro_ret1"]
VERSOES_C2 = {"13fev": "quadro do ciclo 2 retificado de 13/02/2026, vigente na inscricao (principal; adendo 48b §7)",
              "19mar": "quadro do ciclo 2 retificado de 19/03/2026, refeito depois do resultado preliminar "
                       "(pipeline; tipo de vaga pos-resultado, nao usar)"}
ROTULO_19MAR = "tipo de vaga pós-resultado (não usar)"
CORTES = T23.CORTES                 # (300, 400)
H = T23.H                           # 50
H_SENS = T23.H_SENS                 # (30, 80)
CICLOS = (1, 2, 3)
CICLOS_F14 = (1, 2)
FATORES_M = (0.5, 1.0, 2.0)
FATOR_MDE = 2.8
MARGEM_HI1 = 0.10                   # ±10 p.p. (protocolo 60, parte A)
FRACAO_HI2 = 0.25                   # ±25% da média abaixo do corte na mesma amostra (protocolo 60, parte A)
ALFA = 0.05
TOL_REPRO = 1e-9
ROTULO_CORTE = T23.ROTULO_CORTE     # {300: "0.300", 400: "0.400"}
TXT_CORTE = {300: "0,300", 400: "0,400"}
BOLSA = {300: "R$ 10 mil → R$ 15 mil", 400: "R$ 15 mil → R$ 20 mil"}
POP_123 = "V1+V2+V3"
TIPOS = ("so_imed", "mista", "so_cr")
NOME_TIPO = {"so_imed": "só vagas imediatas", "mista": "mista (imediatas e cadastro reserva)",
             "so_cr": "só cadastro reserva"}

LIMITE_MISTAS = ("a base nao registra em que tipo de vaga (imediata ou cadastro reserva) cada alocado entrou: nas "
                 "celulas mistas contam todos os alocados da celula (HI-1 e HI-2), e o controle de HI-2 sao as "
                 "vagas imediatas dessas celulas; um alocado de celula mista que tenha ocupado vaga de cadastro "
                 "reserva conta como preenchimento de vaga imediata")
DECISAO_DEFINICAO = (
    "O adendo descreve HI-1 com 'a definicao de preenchida de cada ciclo, igual a do A3' e HI-s2 com 'uma definicao "
    "unica (>= 1 alocado na 1a chamada)'. Na base, a definicao do A3 (A3_PREENCHIDA do script 24) ja e "
    "n_alocados_ch1 >= 1 em todos os ciclos; o que muda por ciclo e a fonte do 'alocado' (ciclo 1: confirmacao de "
    "local na alocacao sub judice; ciclos 2-3: SITUACAO ALOCADO). HI-1 segue o A3, como manda o adendo, para que a "
    "comparacao com a medida antiga mude so a amostra. A forma literal da HI-s2 coincide com HI-1 (conferido celula "
    "a celula); por isso a HI-s2 relata a outra definicao que a base tem, a F1.3 do protocolo 40 (ciclo 1: "
    "confirmacao ou homologacao; ciclos 2-3: >= 1 alocado).")
ROTULO_DESCRITIVO = "DESCRITIVO (HI-s6: so celulas de cadastro reserva; mostra onde estava a diferenca)"
CONTRASTE = ("pacote do corte: em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil e em 0,400 de R$ 15 mil "
             "para R$ 20 mil, mas outras regras federais mudam nos mesmos cortes (auditoria 18); nao e efeito da "
             "participacao no PMM-E nem do Agora Tem Especialistas")

COLUNAS = [
    "natureza_dos_dados", "estatuto", "id_linha", "linha", "papel", "outcome", "descricao_outcome",
    "unidade_analise", "amostra", "versao_quadro_c2", "rotulo", "populacao", "ciclo", "corte", "variante",
    "controle", "efeitos_fixos",
    "estimador", "h", "status", "descritivo", "n_abaixo", "n_acima", "n_obs", "n_clusters", "tau", "ep",
    "ic95_inf", "ic95_sup", "p_valor", "media_abaixo", "efeito_relativo_media_abaixo", "mde", "coef_controle",
    "entra_holm", "p_holm", "entra_bky", "q_bky", "ic_honesto_inf", "ic_honesto_sup", "M", "fator_M", "vies_max",
    "margem", "ic90_inf", "ic90_sup", "p_aumento", "p_queda", "p_tost", "leitura_tost", "margem_minima",
    "unidade", "nota",
]
UN_FRAC = "fracao (x100 = p.p.)"
UN_CONT = "medicos alocados por municipio"


class FalhaValidacao(RuntimeError):
    """Conferência obrigatória falhou: o script para sem gravar."""


sha256 = T23.sha256
rotulo = T23.rotulo


def _nan_none(o):
    if isinstance(o, dict):
        return {str(k): _nan_none(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_nan_none(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def _juntar(*notas) -> str:
    return "; ".join(str(n) for n in notas if n)


# ---------------------------------------------------------------------------
# 1. Leitura e montagem (só output/; a running variable é o IVS 2010 oficial do a08)
# ---------------------------------------------------------------------------

def tipo_celula(vi: pd.Series, cr: pd.Series) -> np.ndarray:
    """só imediatas, mista ou só cadastro reserva; célula sem vaga nenhuma levanta erro (não existe no quadro)."""
    vi, cr = vi.astype(float), cr.astype(float)
    if ((vi <= 0) & (cr <= 0)).any() or vi.isna().any() or cr.isna().any():
        raise FalhaValidacao("celula do quadro sem vaga (ou com vaga ausente)")
    return np.where((vi > 0) & (cr > 0), "mista", np.where(vi > 0, "so_imed", "so_cr"))


def agregar_municipio(cel: pd.DataFrame) -> pd.DataFrame:
    """Por ciclo × município: alocados e vagas por tipo de célula (contagens observadas; nada dividido por suposição).

    `aloc_imed` soma os alocados das células com vaga imediata (só imediatas + mistas: nas mistas, todos os
    alocados da célula); `vi_imed` soma as vagas imediatas dessas células; `*_pura` só as células só de imediatas;
    `*_cr` só as células só de cadastro reserva.
    """
    c = cel.copy()
    imed = c["tipo_celula"].isin(["so_imed", "mista"])
    pura = c["tipo_celula"] == "so_imed"
    so_cr = c["tipo_celula"] == "so_cr"
    vi, cr, al = c["vagas_imediatas"].astype(float), c["vagas_cr"].astype(float), c["aloc"].astype(float)
    c["aloc_imed"], c["vi_imed"], c["n_cel_imed"] = np.where(imed, al, 0.0), np.where(imed, vi, 0.0), imed.astype(float)
    c["aloc_pura"], c["vi_pura"], c["n_cel_pura"] = np.where(pura, al, 0.0), np.where(pura, vi, 0.0), pura.astype(float)
    c["aloc_cr"], c["vcr_cr"], c["n_cel_cr"] = np.where(so_cr, al, 0.0), np.where(so_cr, cr, 0.0), so_cr.astype(float)
    c["aloc_mista"] = np.where(c["tipo_celula"] == "mista", al, 0.0)
    c["n_cel_mista"] = (c["tipo_celula"] == "mista").astype(float)
    cols = ["aloc_imed", "vi_imed", "n_cel_imed", "aloc_pura", "vi_pura", "n_cel_pura", "aloc_cr", "vcr_cr",
            "n_cel_cr", "aloc_mista", "n_cel_mista"]
    return c.groupby(["ciclo", "co_ibge"], as_index=False)[cols].sum()


def quadro_c2_13fev(cel_pipe: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Vagas imediatas e de cadastro reserva por célula no quadro do ciclo 2 retificado de 13/02/2026 (vigente na
    inscrição), pela leitura da auditoria 36 (`scripts/auditoria_H1/a36_leitura.py`, `ler_quadro`).

    As células têm de ser as mesmas do quadro do pipeline (19/03/2026); célula sem par levanta erro."""
    q = A36L.ler_quadro(ARQ_C2_13FEV)
    if q["chave"].duplicated().any():
        raise FalhaValidacao("quadro de 13/02/2026 com celula duplicada")
    c2 = cel_pipe[cel_pipe["ciclo"] == 2].copy()
    c2["chave"] = c2["co_cnes_7d"].astype(str).str.zfill(7) + "_" + c2["cod_curso"].astype(int).astype(str).str.zfill(2)
    m = c2[["chave"]].merge(q[["chave", "vagas_imediatas", "vagas_cr"]], on="chave", how="left", validate="one_to_one")
    sem_par = int(m["vagas_imediatas"].isna().sum())
    fora = int((~q["chave"].isin(c2["chave"])).sum())
    if sem_par or fora:
        raise FalhaValidacao(f"quadros de 13/02 e 19/03 do ciclo 2 com celulas diferentes ({sem_par} / {fora})")
    m.index = c2.index
    vi13, cr13 = m["vagas_imediatas"].astype(float), m["vagas_cr"].astype(float)
    vi19, cr19 = c2["vagas_imediatas"].astype(float), c2["vagas_cr"].astype(float)
    so_cr13 = vi13 == 0
    conf = {"arquivo": rotulo(ARQ_C2_13FEV), "sha256": sha256(ARQ_C2_13FEV),
            "leitura": "scripts/auditoria_H1/a36_leitura.py (ler_quadro)", "celulas": int(len(m)),
            "vagas_imediatas_13fev": float(vi13.sum()), "vagas_cr_13fev": float(cr13.sum()),
            "vagas_imediatas_19mar": float(vi19.sum()), "vagas_cr_19mar": float(cr19.sum()),
            "celulas_com_total_diferente": int(((vi13 + cr13) != (vi19 + cr19)).sum()),
            "celulas_so_cr_13fev": int(so_cr13.sum()),
            "celulas_so_cr_13fev_com_imediata_19mar": int((so_cr13 & (vi19 > 0)).sum()),
            "dessas_com_alocado": int((so_cr13 & (vi19 > 0) & (c2["n_alocados_ch1"] > 0)).sum()),
            "vagas_convertidas_cr_em_imediatas": float((vi19 - vi13).clip(lower=0).sum())}
    return pd.DataFrame({"vi": vi13, "cr": cr13}, index=c2.index), conf


def carregar() -> dict:
    """Entradas e as duas versões do tipo de vaga do ciclo 2: `13fev` (principal, adendo 48b §7) e `19mar`
    (pipeline, pós-resultado: usada na reprodução e na sensibilidade "não usar")."""
    rv = E6.ler_running_variable()
    pops, conf_pop = E6.chaves_populacoes(rv)
    V, _U, info_v = T23.carregar(rv, pops)
    cel = pd.read_parquet(ARQ_VC)
    if ((cel["com_vagas_imediatas"] == 1) != (cel["vagas_imediatas"] > 0)).any():
        raise FalhaValidacao("com_vagas_imediatas difere de vagas_imediatas > 0")
    q13, conf_c2 = quadro_c2_13fev(cel)
    out = {"conf_c2": conf_c2, "conf_pop": conf_pop}
    for versao in VERSOES_C2:
        c = cel.copy()
        if versao == "13fev":
            c.loc[q13.index, "vagas_imediatas"] = q13["vi"]
            c.loc[q13.index, "vagas_cr"] = q13["cr"]
            c.loc[q13.index, "com_vagas_imediatas"] = (q13["vi"] > 0).astype(int)
        out[versao] = montar(c, pops, V, info_v, versao)
    return out


def montar(cel: pd.DataFrame, pops: dict, V: dict, info_v: dict, versao: str) -> dict:
    cel = cel.copy()
    cel["tipo_celula"] = tipo_celula(cel["vagas_imediatas"], cel["vagas_cr"])
    if cel["n_alocados_ch1"].isna().any():
        raise FalhaValidacao("celula com n_alocados_ch1 ausente")
    cel["aloc"] = cel["n_alocados_ch1"].astype(float)
    cel["preenchida"] = (cel["aloc"] >= 1).astype(float)                       # A3 = HI-1
    cel["preenchida_literal"] = np.where(cel["aloc"] >= 1, 1.0, 0.0)           # HI-s2 literal ('>= 1 alocado')
    cel["preenchida_f13"] = cel["f1_3_preenchida_ch1"].astype(float)          # HI-s2 (F1.3 do protocolo 40)
    cel["preenchida_f14"] = cel["f1_4_preenchida_ate_ch2"].astype(float)      # HI-s5 (F1.4 do protocolo 40)
    cel["tipo_vaga_imediata"] = cel["com_vagas_imediatas"].astype(float)
    cel["fe_curso_ciclo"] = ("c" + cel["ciclo"].astype(int).astype(str) + "_curso"
                             + cel["cod_curso"].astype(int).astype(str).str.zfill(2))
    CK, contagem_cel = {}, {}
    for k in CICLOS:
        c = cel[cel["ciclo"] == k].merge(pops[f"V{k}"], on="co_ibge", how="left", validate="many_to_one")
        sem = c["s_mil"].isna()
        c_ok = c[~sem].copy()
        if (E6.s_mil_de_ivs(c_ok["ivs_2010_oficial"]) != c_ok["s_mil"]).any():
            raise FalhaValidacao(f"V{k}: IVS da celula difere do IVS oficial do municipio")
        cnt = {"celulas_no_quadro": int(len(c)), "celulas_sem_ivs_oficial_fora_da_rdd": int(sem.sum())}
        for t in TIPOS:
            m = c_ok["tipo_celula"] == t
            cnt[f"celulas_{t}"] = int(m.sum())
            cnt[f"vagas_imediatas_{t}"] = float(c_ok.loc[m, "vagas_imediatas"].sum())
            cnt[f"vagas_cr_{t}"] = float(c_ok.loc[m, "vagas_cr"].sum())
            cnt[f"alocados_ch1_{t}"] = float(c_ok.loc[m, "aloc"].sum())
        cnt["celulas_na_amostra_hi"] = cnt["celulas_so_imed"] + cnt["celulas_mista"]
        cnt["celulas_so_cr_fora_da_amostra_hi"] = cnt["celulas_so_cr"]
        cnt["f13_ausente_na_amostra_hi"] = int(c_ok.loc[c_ok["tipo_celula"] != "so_cr", "preenchida_f13"].isna().sum())
        contagem_cel[f"V{k}"] = cnt
        CK[k] = c_ok.reset_index(drop=True)
    agg = agregar_municipio(cel)
    MK, contagem_mun = {}, {}
    for k, d in V.items():
        m = d.merge(agg[agg["ciclo"] == k].drop(columns="ciclo"), on="co_ibge", how="left", validate="one_to_one")
        if m[["aloc_imed", "vi_imed"]].isna().any().any():
            raise FalhaValidacao(f"V{k}: municipio do quadro sem celula no arquivo de celulas")
        if (versao == "19mar" or k != 2) and (np.abs(m["vi_imed"] - m["vagas_imediatas"].astype(float)) > 1e-9).any():
            raise FalhaValidacao(f"V{k}: vagas imediatas das celulas difere do municipio")
        if (np.abs(m["aloc_imed"] + m["aloc_cr"] - m["n_alocados_ch1"].astype(float)) > 1e-9).any():
            raise FalhaValidacao(f"V{k}: alocados das celulas difere do municipio")
        MK[k] = m
        contagem_mun[f"V{k}"] = {
            "municipios_no_quadro_com_ivs_oficial": int(len(m)),
            "municipios_sem_ivs_oficial_fora_da_rdd": int(info_v[f"V{k}"]["municipios_sem_ivs_fora"]),
            "municipios_com_vaga_imediata_na_amostra_hi2": int((m["n_cel_imed"] > 0).sum()),
            "municipios_so_cadastro_reserva_fora_da_hi2": int((m["n_cel_imed"] == 0).sum()),
            "municipios_com_celula_pura_hi_s4": int((m["n_cel_pura"] > 0).sum()),
            "municipios_com_celula_so_cr_hi_s6": int((m["n_cel_cr"] > 0).sum()),
        }
    return {"V": V, "CK": CK, "MK": MK, "cel": cel, "contagem_celulas": contagem_cel,
            "contagem_municipios": contagem_mun, "versao_c2": versao}


# ---------------------------------------------------------------------------
# 2. Amostras e estimadores (rdd_lib e funções do 23)
# ---------------------------------------------------------------------------

def amostra(frames: dict, ks, c: int, filtro=None):
    """Um corte; ciclos `ks` empilhados (grupo = ciclo, como no 23 e no 24) ou um ciclo (grupo = corte)."""
    ks = tuple(ks)
    partes = []
    for k in ks:
        d = frames[k]
        if filtro is not None:
            d = d[filtro(d)]
        partes.append((d, c, f"c{k}" if len(ks) > 1 else str(c)))
    return T23.montar_amostra(partes, empilhada=len(ks) > 1)


def filtro_tipos(*tipos):
    return lambda d: d["tipo_celula"].isin(list(tipos))


def filtro_coluna_positiva(col: str):
    return lambda d: d[col] > 0


def est_celula(a, y: np.ndarray, h=H, *, fe: bool = True, tipo: bool = False) -> dict:
    """Unidade = célula; salto comum, intercepto e inclinações por grupo × lado; EF de curso × ciclo; CR1 por município.

    Com `tipo=True` acrescenta o tipo de vaga como no A3 do 24 (`ajustar_celula`)."""
    r = L.rd_empilhado(a.s, y, a.c, grupo=a.g, h_mil=h, cluster=a.cl, ids_unidade=a.cl,
                       efeitos_fixos=a.d["fe_curso_ciclo"].to_numpy() if fe else None,
                       Z=a.col("tipo_vaga_imediata") if tipo else None,
                       nomes_z=["tipo_vaga_imediata"] if tipo else None, detalhes=True)
    r["media_abaixo"] = float("nan")
    if "_detalhes" in r:
        d = r["_detalhes"]
        ab = d["usa"] & (d["x_mil"] <= 0)
        r["media_abaixo"] = float(np.mean(np.asarray(y, dtype=float)[ab])) if ab.any() else float("nan")
    return r


def est_municipio(a, y: np.ndarray, h=H, *, v: np.ndarray | None = None) -> dict:
    """Unidade = município; controle linear comum aos dois lados com coeficiente por grupo (ciclo), como o S-a do 23.

    Um ciclo: local linear com EP HC1, que com uma linha por município é igual ao CR1 por município."""
    return T23.ajustar(a, y, h, v=v)


def honesto_celula(a, y: np.ndarray, M: float | None = None) -> dict:
    """IC honesto (Armstrong–Kolesár, regra do E6: quártica até o ponto médio entre cortes), EF de curso × ciclo."""
    kw = {"cortes_vizinhos": CORTES} if M is None else {"M": M}
    return L.rd_empilhado_honesto(a.s, y, a.c, grupo=a.g, h_mil=H, cluster=a.cl, ids_unidade=a.cl,
                                  efeitos_fixos=a.d["fe_curso_ciclo"].to_numpy(), **kw)


# ---------------------------------------------------------------------------
# 3. Reprodução (para se não bater)
# ---------------------------------------------------------------------------

def _comparar(nome: str, meu: dict, ref: pd.Series, campos=("tau", "ep", "p_valor"),
              contagens=("n_abaixo", "n_acima", "n_obs")) -> dict:
    difs = {c: abs(float(meu[c]) - float(ref[c])) for c in campos}
    cont = {c: (int(meu[c]), int(ref[c])) for c in contagens}
    ok = all(v <= TOL_REPRO * max(1.0, abs(float(ref[c]))) for c, v in difs.items()) and \
        all(a == b for a, b in cont.values())
    if not ok:
        raise FalhaValidacao(f"reproducao falhou em {nome}: difs {difs}, contagens {cont}")
    return {"linha": nome, "tau": float(meu["tau"]), "ep": float(meu["ep"]), "p_valor": float(meu["p_valor"]),
            "ic95_inf": float(meu["ic95_inf"]), "ic95_sup": float(meu["ic95_sup"]),
            "n_abaixo": int(meu["n_abaixo"]), "n_acima": int(meu["n_acima"]), "n_obs": int(meu["n_obs"]),
            "max_abs_dif": max(difs.values()), "reproduz": True}


def _uma(df: pd.DataFrame, **kw) -> pd.Series:
    m = np.ones(len(df), dtype=bool)
    for k, v in kw.items():
        m &= (df[k] == v).to_numpy()
    sel = df[m]
    if len(sel) != 1:
        raise FalhaValidacao(f"linha de referencia nao unica ({len(sel)}): {kw}")
    return sel.iloc[0]


def reproduzir(dados: dict) -> dict:
    CK, V, MK = dados["CK"], dados["V"], dados["MK"]
    na = pd.read_csv(NA_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    n = pd.read_csv(N_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    nd = pd.read_csv(ND_EST, dtype={"corte": str, "ciclo": str}, low_memory=False)
    out = {"tolerancia_relativa": TOL_REPRO, "linhas": []}
    for c in CORTES:
        ct = ROTULO_CORTE[c]
        # A3 (script 24): todas as células, EF de curso × ciclo e tipo de vaga.
        a = amostra(CK, CICLOS, c)
        r = est_celula(a, a.col("preenchida"), tipo=True)
        ref = _uma(na, outcome_id="A3_PREENCHIDA", especificacao="A3", variante="principal",
                   populacao="V1+V2+V3 (celulas)", corte=ct)
        x = _comparar(f"A3_PREENCHIDA {ct}", r, ref)
        x.update({"fonte": rotulo(NA_EST), "media_abaixo": float(r["media_abaixo"]), "corte": ct, "id": "A3"})
        out["linhas"].append(x)
        # N1 S-a (script 23): controle = vagas imediatas + cadastro reserva, coeficiente por ciclo.
        m = amostra(V, CICLOS, c)
        r = est_municipio(m, m.col("n_alocados_ch1"), v=m.col("vagas_imediatas_mais_cr"))
        ref = _uma(n, outcome_id="N1", especificacao="S-a", variante="principal", populacao=POP_123, corte=ct)
        x = _comparar(f"N1 S-a {ct}", r, ref)
        x.update({"fonte": rotulo(N_EST), "media_abaixo": float(r["media_abaixo"]), "corte": ct, "id": "N1"})
        out["linhas"].append(x)
        # 49b §14 (script 23b, adendo AD2): taxa por tipo de célula e só com vagas imediatas.
        for oid, num, den, filtro in (("TAXA_SO_IMED", "aloc_pura", "vi_pura", "vi_pura"),
                                      ("TAXA_SO_CR", "aloc_cr", "vcr_cr", "vcr_cr"),
                                      ("TAXA_VI", "aloc_tot", "vagas_imediatas", "vagas_imediatas")):
            frames = {}
            for k, d in MK.items():
                d = d.copy()
                d["aloc_tot"] = d["n_alocados_ch1"].astype(float)
                dv = d[den].astype(float)
                d["_y"] = np.where(dv > 0, d[num] / np.where(dv > 0, dv, 1.0), np.nan)
                d["_peso"] = np.where(np.isfinite(d["_y"]), dv, np.nan)
                frames[k] = d
            if oid == "TAXA_VI":
                aa = amostra(frames, CICLOS, c, filtro_coluna_positiva("vagas_imediatas"))
                ref = _uma(nd, adendo="AD2", tipo_linha="estimativa", diagnostico="AD2_A2", variante="vi_vaga_com_vi",
                           corte=ct)
            else:
                aa = amostra(frames, CICLOS, c)
                ref = _uma(nd, adendo="AD2", tipo_linha="estimativa", diagnostico="AD2_A1", outcome=oid,
                           variante="principal", corte=ct)
            r = T23.ajustar(aa, aa.col("_y"), H, peso=aa.col("_peso"))
            x = _comparar(f"49b §14 {oid} {ct}", r, ref)
            x.update({"fonte": rotulo(ND_EST), "corte": ct, "id": oid})
            out["linhas"].append(x)
    # Células por tipo (49b §14) contra ND_resumo.json.
    ref = json.loads(ND_RES.read_text(encoding="utf-8"))["adendo_2026_10_21"]["taxa_separada_por_tipo_de_vaga"][
        "celulas_por_tipo"]
    cel = dados["cel"]
    difs = 0
    for k in CICLOS:
        for t in TIPOS:
            d = cel[(cel["ciclo"] == k) & (cel["tipo_celula"] == t)]
            meu = {"celulas": float(len(d)), "vagas_imediatas": float(d["vagas_imediatas"].sum()),
                   "vagas_cr": float(d["vagas_cr"].sum()), "alocados": float(d["aloc"].sum())}
            r_ = ref[f"ciclo {k} / {t}"]
            difs += sum(abs(meu[c_] - float(r_[c_])) for c_ in meu)
    if difs > 0:
        raise FalhaValidacao("contagem de celulas por tipo difere do ND_resumo.json (49b §14)")
    out["celulas_por_tipo_49b"] = {"fonte": rotulo(ND_RES), "reproduz": True, "soma_abs_dif": difs}
    # HI-s2 literal = HI-1 (célula a célula).
    out["hi_s2_literal_igual_hi1"] = bool((cel["preenchida_literal"] == cel["preenchida"]).all())
    if not out["hi_s2_literal_igual_hi1"]:
        raise FalhaValidacao("a forma literal da HI-s2 deveria coincidir com HI-1")
    out["f13_difere_de_hi1"] = {
        f"V{k}": int(((CK[k]["preenchida_f13"] != CK[k]["preenchida"]) & (CK[k]["tipo_celula"] != "so_cr")).sum())
        for k in CICLOS}
    out["max_abs_dif"] = max(x["max_abs_dif"] for x in out["linhas"])
    out["reproduz"] = True
    return out


# ---------------------------------------------------------------------------
# 4. Linhas de saída
# ---------------------------------------------------------------------------

def nova_linha(linha: str, papel: str, outcome: str, desc: str, unidade_analise: str, amostra_txt: str,
               populacao: str, ciclo: str, corte: str, variante: str, estimador: str, *, h=H, unidade: str,
               controle: str = "", efeitos_fixos: str = "", descritivo: bool = False, nota: str = "",
               versao: str = "13fev", rotulo_: str = "") -> dict:
    ln = {c: np.nan for c in COLUNAS}
    ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "linha": linha, "papel": papel,
               "outcome": outcome, "descricao_outcome": desc, "unidade_analise": unidade_analise,
               "amostra": amostra_txt, "populacao": populacao, "ciclo": ciclo, "corte": corte,
               "variante": variante, "controle": controle, "efeitos_fixos": efeitos_fixos, "estimador": estimador,
               "h": h / 1000.0, "status": "EXECUTADO", "descritivo": bool(descritivo), "unidade": unidade,
               "entra_holm": False, "entra_bky": False, "leitura_tost": "", "nota": nota,
               "versao_quadro_c2": versao, "rotulo": rotulo_})
    ln["id_linha"] = "|".join([linha, outcome, ciclo, corte, variante, f"h={h / 1000:.3f}", f"c2={versao}"])
    return ln


def preencher(ln: dict, r: dict) -> dict:
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters",
              "media_abaixo"):
        if r.get(k) is not None:
            ln[k] = r[k]
    if r.get("gamma"):
        ln["coef_controle"] = json.dumps({g: round(v, 10) for g, v in sorted(r["gamma"].items())})
    ln["nota"] = _juntar(ln["nota"], r.get("nota", ""),
                         f"colunas descartadas: {r['covariaveis_descartadas']}" if r.get("covariaveis_descartadas") else "")
    tau, ep, media = float(ln["tau"]), float(ln["ep"]), float(ln["media_abaixo"])
    if np.isfinite(ep):
        ln["mde"] = FATOR_MDE * ep
    if np.isfinite(media) and media != 0 and np.isfinite(tau):
        ln["efeito_relativo_media_abaixo"] = tau / media
    if not np.isfinite(tau):
        ln["status"] = "SEM_ESTIMATIVA"
        ln["nota"] = ln["nota"] or "biblioteca devolveu NaN sem motivo"
    return ln


EST_CEL = ("celula do quadro da 1a chamada; local linear, kernel triangular; intercepto e inclinacoes por ciclo x "
           "lado, salto comum; EF de curso x ciclo; CR1 por municipio")
EST_CEL_1 = ("celula do quadro da 1a chamada (um ciclo); local linear, kernel triangular; EF de curso; "
             "CR1 por municipio")
EST_MUN = ("municipio; local linear, kernel triangular; intercepto e inclinacoes por ciclo x lado, salto comum; "
           "CR1 por municipio")
EST_MUN_1 = "municipio (um ciclo); local linear, kernel triangular; EP HC1 (= CR1 com uma linha por municipio)"
EST_CTRL = "; controle linear comum aos dois lados, um coeficiente por ciclo (como o S-a do protocolo 48)"

DESC = {
    "HI-1": "celula com vaga imediata preenchida na 1a chamada (n_alocados_ch1 >= 1, definicao do A3)",
    "HI-2": "medicos alocados na 1a chamada em celulas com vaga imediata, por municipio",
    "HI-1_F13": "celula com vaga imediata preenchida na 1a chamada, definicao F1.3 do protocolo 40",
    "HI-1_LITERAL": "celula com vaga imediata com >= 1 alocado na 1a chamada (forma literal da HI-s2)",
    "HI-1_PURA": "celula so de vagas imediatas preenchida na 1a chamada",
    "HI-2_PURA": "medicos alocados na 1a chamada em celulas so de vagas imediatas, por municipio",
    "F14_TODAS": "celula preenchida ate a 2a chamada (F1.4 do protocolo 40), todas as celulas, inclusive so de CR",
    "CR_CELULA": "celula so de cadastro reserva preenchida na 1a chamada",
    "CR_MUN": "medicos alocados na 1a chamada em celulas so de cadastro reserva, por municipio",
}


def _ciclo_txt(ks) -> str:
    return "+".join(str(k) for k in ks)


def _pop(ks) -> str:
    return "+".join(f"V{k}" for k in ks)


def linha_cel(linha, papel, oid, a, y_col, c, ks, variante, h=H, amostra_txt="celulas com vaga imediata (so "
              "imediatas + mistas)", descritivo=False, nota="", versao="13fev", rot="") -> tuple[dict, dict]:
    r = est_celula(a, a.col(y_col), h)
    ln = nova_linha(linha, papel, oid, DESC[oid], "celula", amostra_txt, _pop(ks) + " (celulas)", _ciclo_txt(ks),
                    ROTULO_CORTE[c], variante, EST_CEL if len(ks) > 1 else EST_CEL_1, h=h, unidade=UN_FRAC,
                    efeitos_fixos="curso x ciclo", descritivo=descritivo,
                    nota=_juntar(nota, "n_abaixo/n_acima = municipios; n_obs = celulas"), versao=versao, rotulo_=rot)
    return preencher(ln, r), r


def linha_mun(linha, papel, oid, a, y_col, v_col, c, ks, variante, h=H, amostra_txt="municipios com >= 1 celula "
              "com vaga imediata", descritivo=False, nota="", versao="13fev", rot="") -> tuple[dict, dict]:
    v = a.col(v_col) if v_col else None
    r = est_municipio(a, a.col(y_col), h, v=v)
    est = (EST_MUN if len(ks) > 1 else EST_MUN_1) + (EST_CTRL if v_col else "; sem controle")
    ln = nova_linha(linha, papel, oid, DESC[oid], "municipio", amostra_txt, _pop(ks), _ciclo_txt(ks),
                    ROTULO_CORTE[c], variante, est, h=h, unidade=UN_CONT, controle=v_col or "",
                    descritivo=descritivo, nota=nota, versao=versao, rotulo_=rot)
    return preencher(ln, r), r


def linhas_honestas(base_ln: dict, a, y: np.ndarray, *, celula: bool, r_main: dict) -> tuple[list[dict], dict]:
    """HI-s8: IC honesto M × {0,5; 1; 2} (regra do E6) no h = 0,050; na HI-2, y residualizado pelo controle (S-g)."""
    linhas, base = [], None
    if celula:
        base = honesto_celula(a, y)
    else:
        ytil = T23.residualizar(y, r_main)
        base = T23.honesto(a, ytil)
    if not abs(base["tau"] - r_main["tau"]) <= 1e-8 * max(1.0, abs(r_main["tau"])):
        raise FalhaValidacao(f"IC honesto com salto diferente da linha principal: {base['tau']} vs {r_main['tau']}")
    M0 = base["M"]
    for f in FATORES_M:
        if f == 1.0:
            hon = base
        elif celula:
            hon = honesto_celula(a, y, M=f * M0)
        else:
            hon = T23.honesto(a, T23.residualizar(y, r_main), M=f * M0)
        ln = nova_linha("HI-s8", "secundaria", base_ln["outcome"], base_ln["descricao_outcome"],
                        base_ln["unidade_analise"], base_ln["amostra"], base_ln["populacao"], base_ln["ciclo"],
                        base_ln["corte"], f"ic_honesto_M_x{f:g}",
                        "IC honesto Armstrong-Kolesar (classe de Taylor, CR1; M pela regra de bolso do E6 com "
                        "suporte ate o ponto medio entre cortes)" + (
                            "; outcome residualizado pelo controle, gamma tratado como fixo" if not celula else
                            "; EF de curso x ciclo"), unidade=base_ln["unidade"], controle=base_ln["controle"],
                        efeitos_fixos=base_ln["efeitos_fixos"])
        for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "M", "vies_max"):
            if hon.get(k) is not None:
                ln[k] = hon[k]
        ln["ic_honesto_inf"], ln["ic_honesto_sup"], ln["fator_M"] = hon["ic95_inf"], hon["ic95_sup"], f
        ln["n_obs"] = base_ln["n_obs"]
        ln["media_abaixo"] = base_ln["media_abaixo"]
        ln["nota"] = _juntar("ep = EP usado no IC honesto; p = p do teste que inverte o IC honesto; fora do BKY",
                             hon.get("nota", ""))
        if not np.isfinite(float(ln["ic95_inf"])):
            ln["status"] = "SEM_ESTIMATIVA"
        linhas.append(ln)
    return linhas, base


def linhas_tost(base_ln: dict, hon: dict, margem: float, regra: str) -> list[dict]:
    """HI-s7: TOST com as margens do protocolo 60 (funções do script 36), no IC convencional e no honesto."""
    out = []
    for tipo, tau, ep, vies in (("TOST_convencional", base_ln["tau"], base_ln["ep"], 0.0),
                                ("TOST_honesto", hon["tau"], hon["ep"], hon["vies_max"])):
        r = T36.tost(float(tau), float(ep), margem, float(vies))
        ln = nova_linha("HI-s7", "secundaria", base_ln["outcome"], base_ln["descricao_outcome"],
                        base_ln["unidade_analise"], base_ln["amostra"], base_ln["populacao"], base_ln["ciclo"],
                        base_ln["corte"], tipo, "TOST (dois testes unilaterais a 5%; IC 90%), funcao tost do script 36"
                        + ("; vies maximo do IC honesto M x1" if vies else "; EP CR1 da linha principal"),
                        unidade=base_ln["unidade"], controle=base_ln["controle"], efeitos_fixos=base_ln["efeitos_fixos"],
                        nota=f"margem: {regra}; fora do BKY (outra hipotese nula)")
        ln.update({"tau": tau, "ep": ep, "vies_max": vies, "margem": margem, "media_abaixo": base_ln["media_abaixo"],
                   "n_abaixo": base_ln["n_abaixo"], "n_acima": base_ln["n_acima"], "n_obs": base_ln["n_obs"],
                   **{k: r[k] for k in ("ic90_inf", "ic90_sup", "p_aumento", "p_queda", "p_tost", "margem_minima")}})
        ln["leitura_tost"] = T36.classificar(r["p_aumento"] < ALFA, r["p_queda"] < ALFA)
        out.append(ln)
    return out


# ---------------------------------------------------------------------------
# 5. Estimação
# ---------------------------------------------------------------------------

def estimar(dados: dict, dados_19: dict | None = None) -> tuple[pd.DataFrame, dict]:
    CK, MK = dados["CK"], dados["MK"]
    imed = filtro_tipos("so_imed", "mista")
    pura = filtro_tipos("so_imed")
    so_cr = filtro_tipos("so_cr")
    mun_imed = filtro_coluna_positiva("n_cel_imed")
    linhas: list[dict] = []
    extras: dict = {"janela": {}}
    for c in CORTES:
        ct = ROTULO_CORTE[c]
        # --- primárias
        a1 = amostra(CK, CICLOS, c, imed)
        l1, r1 = linha_cel("HI-1", "primaria", "HI-1", a1, "preenchida", c, CICLOS, "principal",
                           nota=LIMITE_MISTAS)
        l1["entra_holm"] = True
        a2 = amostra(MK, CICLOS, c, mun_imed)
        l2, r2 = linha_mun("HI-2", "primaria", "HI-2", a2, "aloc_imed", "vi_imed", c, CICLOS, "principal",
                           nota=LIMITE_MISTAS)
        l2["entra_holm"] = True
        linhas += [l1, l2]
        # Fora da amostra, na janela (contadas, não descartadas em silêncio).
        at = amostra(CK, CICLOS, c)
        xt = L.normalizar_s_mil(at.s) - at.c
        jan = L.pesos_kernel(xt, H) > 0
        fora_cr = jan & (at.d["tipo_celula"] == "so_cr").to_numpy()
        am = amostra(MK, CICLOS, c)
        xm = L.normalizar_s_mil(am.s) - am.c
        janm = L.pesos_kernel(xm, H) > 0
        fora_m = janm & (am.d["n_cel_imed"] == 0).to_numpy()
        extras["janela"][ct] = {
            "celulas_na_janela": int(jan.sum()), "celulas_hi1_abaixo": int((jan & ~fora_cr & (xt <= 0)).sum()),
            "celulas_hi1_acima": int((jan & ~fora_cr & (xt > 0)).sum()),
            "celulas_so_cr_fora_abaixo": int((fora_cr & (xt <= 0)).sum()),
            "celulas_so_cr_fora_acima": int((fora_cr & (xt > 0)).sum()),
            "linhas_municipio_ciclo_na_janela": int(janm.sum()),
            "municipio_ciclo_so_cr_fora_abaixo": int((fora_m & (xm <= 0)).sum()),
            "municipio_ciclo_so_cr_fora_acima": int((fora_m & (xm > 0)).sum()),
        }
        # --- HI-s8: IC honesto (e preenche a coluna da primária) e h.
        hon_lin1, hon1 = linhas_honestas(l1, a1, a1.col("preenchida"), celula=True, r_main=r1)
        hon_lin2, hon2 = linhas_honestas(l2, a2, a2.col("aloc_imed"), celula=False, r_main=r2)
        for ln, hon in ((l1, hon1), (l2, hon2)):
            ln["ic_honesto_inf"], ln["ic_honesto_sup"] = hon["ic95_inf"], hon["ic95_sup"]
            ln["M"], ln["fator_M"], ln["vies_max"] = hon["M"], 1.0, hon["vies_max"]
        linhas += hon_lin1 + hon_lin2
        for h in H_SENS:
            lh1, _ = linha_cel("HI-s8", "secundaria", "HI-1", a1, "preenchida", c, CICLOS, f"h={h / 1000:.3f}", h=h)
            lh2, _ = linha_mun("HI-s8", "secundaria", "HI-2", a2, "aloc_imed", "vi_imed", c, CICLOS,
                               f"h={h / 1000:.3f}", h=h)
            lh1["entra_bky"] = lh2["entra_bky"] = True
            linhas += [lh1, lh2]
        # --- HI-s7: TOST.
        linhas += linhas_tost(l1, hon1, MARGEM_HI1, "+-10 p.p. (protocolo 60, parte A)")
        linhas += linhas_tost(l2, hon2, FRACAO_HI2 * float(l2["media_abaixo"]),
                              "+-25% da media abaixo do corte na mesma amostra (protocolo 60, parte A)")
        # --- HI-s1: por ciclo.
        for k in CICLOS:
            ak = amostra(CK, (k,), c, imed)
            lk, _ = linha_cel("HI-s1", "secundaria", "HI-1", ak, "preenchida", c, (k,), "por_ciclo")
            mk = amostra(MK, (k,), c, mun_imed)
            lm, _ = linha_mun("HI-s1", "secundaria", "HI-2", mk, "aloc_imed", "vi_imed", c, (k,), "por_ciclo")
            lk["entra_bky"] = lm["entra_bky"] = True
            linhas += [lk, lm]
        # --- HI-s2: definição de "preenchida".
        lit, rl = linha_cel("HI-s2", "secundaria", "HI-1_LITERAL", a1, "preenchida_literal", c, CICLOS,
                            "definicao_literal_alocado",
                            nota="identica a HI-1 (a definicao do A3 ja e >= 1 alocado); fora do BKY para nao contar "
                                 "a mesma hipotese duas vezes")
        if not abs(rl["tau"] - r1["tau"]) <= 1e-12 * max(1.0, abs(r1["tau"])):
            raise FalhaValidacao("HI-s2 literal deveria repetir HI-1")
        f13, _ = linha_cel("HI-s2", "secundaria", "HI-1_F13", a1, "preenchida_f13", c, CICLOS, "definicao_F1.3",
                           nota="F1.3 do protocolo 40: ciclo 1 = confirmacao ou homologacao; ciclos 2-3 = >= 1 alocado")
        f13["entra_bky"] = True
        linhas += [lit, f13]
        # --- HI-s3: HI-2 sem controle (efeito total entre vagas imediatas).
        l3, _ = linha_mun("HI-s3", "secundaria", "HI-2", a2, "aloc_imed", None, c, CICLOS, "sem_controle")
        l3["entra_bky"] = True
        linhas.append(l3)
        # --- HI-s4: só células puras de vaga imediata.
        ap = amostra(CK, CICLOS, c, pura)
        l4a, _ = linha_cel("HI-s4", "secundaria", "HI-1_PURA", ap, "preenchida", c, CICLOS, "so_celulas_puras",
                           amostra_txt="celulas so de vagas imediatas (sem as mistas)")
        mp = amostra(MK, CICLOS, c, filtro_coluna_positiva("n_cel_pura"))
        l4b, _ = linha_mun("HI-s4", "secundaria", "HI-2_PURA", mp, "aloc_pura", "vi_pura", c, CICLOS,
                           "so_celulas_puras", amostra_txt="municipios com >= 1 celula so de vagas imediatas")
        l4a["entra_bky"] = l4b["entra_bky"] = True
        linhas += [l4a, l4b]
        # --- HI-s5: até a 2ª chamada, todas as células (ciclos 1 e 2), F1.4.
        a5 = amostra(CK, CICLOS_F14, c)
        l5, _ = linha_cel("HI-s5", "secundaria", "F14_TODAS", a5, "preenchida_f14", c, CICLOS_F14,
                          "ate_2a_chamada_todas_as_celulas",
                          amostra_txt="todas as celulas do quadro, inclusive so de cadastro reserva (ciclos 1 e 2)",
                          nota="contraste: medida em que a reserva entra em jogo")
        l5["entra_bky"] = True
        linhas.append(l5)
        # --- HI-s6: só células de cadastro reserva (descritivo).
        a6 = amostra(CK, CICLOS, c, so_cr)
        l6a, _ = linha_cel("HI-s6", "secundaria", "CR_CELULA", a6, "preenchida", c, CICLOS, "so_cadastro_reserva",
                           amostra_txt="celulas so de cadastro reserva", descritivo=True, nota=ROTULO_DESCRITIVO)
        m6 = amostra(MK, CICLOS, c, filtro_coluna_positiva("n_cel_cr"))
        l6b, _ = linha_mun("HI-s6", "secundaria", "CR_MUN", m6, "aloc_cr", "vcr_cr", c, CICLOS,
                           "so_cadastro_reserva", amostra_txt="municipios com >= 1 celula so de cadastro reserva",
                           descritivo=True, nota=_juntar(ROTULO_DESCRITIVO, "controle = vagas de cadastro reserva "
                                                                            "dessas celulas"))
        l6a["entra_bky"] = l6b["entra_bky"] = True
        linhas += [l6a, l6b]
        # --- Sensibilidade pedida com a nota §7: tipo de vaga do ciclo 2 pelo quadro de 19/03 (pós-resultado).
        if dados_19 is not None:
            nota19 = ("SO PARA MOSTRAR A DIFERENCA: no ciclo 2, tipo de vaga e vagas imediatas do quadro de 19/03/2026, "
                      "refeito depois do resultado preliminar (auditoria 36); fora do Holm e do BKY")
            b1 = amostra(dados_19["CK"], CICLOS, c, imed)
            s1, _ = linha_cel("SENS-19MAR", "sensibilidade_nao_usar", "HI-1", b1, "preenchida", c, CICLOS,
                              "tipo_vaga_pos_resultado_19mar", nota=nota19, versao="19mar", rot=ROTULO_19MAR)
            b2 = amostra(dados_19["MK"], CICLOS, c, mun_imed)
            s2, _ = linha_mun("SENS-19MAR", "sensibilidade_nao_usar", "HI-2", b2, "aloc_imed", "vi_imed", c, CICLOS,
                              "tipo_vaga_pos_resultado_19mar", nota=nota19, versao="19mar", rot=ROTULO_19MAR)
            linhas += [s1, s2]
            for oid, frames, y, v, filt in (("HI-1", dados_19["CK"], "preenchida", None, imed),
                                            ("HI-2", dados_19["MK"], "aloc_imed", "vi_imed", mun_imed)):
                bk = amostra(frames, (2,), c, filt)
                if oid == "HI-1":
                    sk, _ = linha_cel("SENS-19MAR", "sensibilidade_nao_usar", oid, bk, y, c, (2,),
                                      "tipo_vaga_pos_resultado_19mar", nota=nota19, versao="19mar", rot=ROTULO_19MAR)
                else:
                    sk, _ = linha_mun("SENS-19MAR", "sensibilidade_nao_usar", oid, bk, y, v, c, (2,),
                                      "tipo_vaga_pos_resultado_19mar", nota=nota19, versao="19mar", rot=ROTULO_19MAR)
                linhas.append(sk)
    est = pd.DataFrame(linhas)[COLUNAS]
    est["entra_holm"] = est["entra_holm"].astype(bool)
    est["entra_bky"] = est["entra_bky"].astype(bool)
    m = est["entra_holm"]
    est.loc[m, "p_holm"] = L.holm(est.loc[m, "p_valor"].to_numpy(dtype=float))
    b = est["entra_bky"]
    est.loc[b, "q_bky"] = L.qvalores_bky(est.loc[b, "p_valor"].to_numpy(dtype=float))
    if est["id_linha"].duplicated().any():
        raise FalhaValidacao("id_linha duplicado")
    return est, extras


# ---------------------------------------------------------------------------
# 6. Leituras (regras fixas no código, pela leitura pré-registrada do §4 do adendo)
# ---------------------------------------------------------------------------

def _prim(est: pd.DataFrame, oid: str, c: int) -> pd.Series:
    return _uma(est, linha=oid, outcome=oid, variante="principal", corte=ROTULO_CORTE[c])


def _sec(est: pd.DataFrame, linha: str, outcome: str, c: int, variante: str, ciclo: str | None = None) -> pd.Series:
    kw = {"linha": linha, "outcome": outcome, "corte": ROTULO_CORTE[c], "variante": variante}
    if ciclo is not None:
        kw["ciclo"] = ciclo
    return _uma(est, **kw)


def _contem_zero(r) -> bool:
    return float(r["ic95_inf"]) <= 0.0 <= float(r["ic95_sup"])


def leitura_primaria(est: pd.DataFrame) -> dict:
    prim = est[est["entra_holm"]]
    todas_contem = bool(all(_contem_zero(r) for _, r in prim.iterrows()))
    rejeita_holm = prim[prim["p_holm"] < ALFA]
    if len(rejeita_holm):
        codigo = "ALGUMA_REJEITA_DEPOIS_DO_HOLM"
    elif todas_contem:
        codigo = "TODAS_CONTEM_ZERO"
    else:
        codigo = "IC_CONVENCIONAL_EXCLUI_ZERO_SEM_HOLM"
    return {"codigo": codigo, "todas_ic_contem_zero": todas_contem,
            "linhas_que_rejeitam_depois_do_holm": [_rot_linha(r) for _, r in rejeita_holm.iterrows()],
            "linhas_com_ic_convencional_sem_zero": [_rot_linha(r) for _, r in prim.iterrows() if not _contem_zero(r)]}


def _rot_linha(r) -> str:
    return f"{r['linha']} em {TXT_CORTE[int(round(float(r['corte']) * 1000))]}"


def leitura_hi_s6(est: pd.DataFrame, repro: dict) -> dict:
    """Regra fixa: a diferença se mostra 'concentrada nas células só de reserva' em 0,300 (onde as medidas antigas
    caíam) se (a) a HI-s6 por célula tiver IC 95% que exclui zero, com sinal negativo, e (b) HI-1 tiver IC que contém
    zero. Senão, a HI-s6 não mostra a diferença concentrada nas células de reserva."""
    s6 = _sec(est, "HI-s6", "CR_CELULA", 300, "so_cadastro_reserva")
    h1 = _prim(est, "HI-1", 300)
    concentrada = bool((not _contem_zero(s6)) and float(s6["tau"]) < 0 and _contem_zero(h1))
    return {"codigo": "CONCENTRADA_NAS_CELULAS_DE_RESERVA" if concentrada else "NAO_SE_MOSTRA_CONCENTRADA",
            "regra": "HI-s6 (celula) em 0,300 com IC 95% sem zero e salto negativo, e HI-1 em 0,300 com IC com zero"}


# ---------------------------------------------------------------------------
# 7. Formatação (pt-BR)
# ---------------------------------------------------------------------------

MENOS = "−"


def fn(x, casas=2, sinal=True) -> str:
    x = float(x)
    if not math.isfinite(x):
        return "—"
    v = round(x, casas)
    s = f"{abs(v):.{casas}f}".replace(".", ",")
    if v < 0:
        return MENOS + s
    return ("+" if sinal else "") + s


def fpp(x, casas=1, sinal=True) -> str:
    return fn(100.0 * float(x), casas, sinal)


def fp(p) -> str:
    p = float(p)
    if not math.isfinite(p):
        return "—"
    return "< 0,001" if p < 0.001 else f"{p:.3f}".replace(".", ",")


def fv(r, col="tau", casas_c=2) -> str:
    """Valor na escala da linha: p.p. para frações, vagas para contagens."""
    return fpp(r[col]) + " p.p." if r["unidade"] == UN_FRAC else fn(r[col], casas_c)


def fic(r, a="ic95_inf", b="ic95_sup") -> str:
    if r["unidade"] == UN_FRAC:
        return f"[{fpp(r[a])}; {fpp(r[b])}]"
    return f"[{fn(r[a])}; {fn(r[b])}]"


def fmedia(r) -> str:
    return fpp(r["media_abaixo"], 1, False) + " %" if r["unidade"] == UN_FRAC else fn(r["media_abaixo"], 2, False)


def fint(x) -> str:
    return "—" if not np.isfinite(float(x)) else f"{int(x)}"


# ---------------------------------------------------------------------------
# 8. Figuras (16:9, legíveis em slide, com "Como ler")
# ---------------------------------------------------------------------------

AZUL = "#2a78d6"
LARANJA = "#eb6834"
CINZA = "#898781"
TINTA = "#0b0b0b"
TINTA2 = "#52514e"
VERDE_ESC = "#114719"
FONTE = "Fonte: outcomes_V_celula.parquet e outcomes_V_municipio.parquet (ciclos 1–3), IVS 2010 oficial (a08). " \
        "EMPIRICO · scripts/rdd_bolsa/40_h1_vagas_imediatas.py"

COMO_LER = {
    "HI_principal.png": (
        "Como ler: cada ponto é o salto no corte (lado de bolsa maior menos lado de bolsa menor) e a barra é o IC 95%. "
        "Em cima, a chance de uma célula com vaga imediata ser preenchida na 1ª chamada; embaixo, os médicos alocados "
        "nessas células por município, comparando municípios com o mesmo número de vagas imediatas. Azul: o IC exclui "
        "zero; cinza: contém zero. Barra que cruza a linha do zero quer dizer que não se detecta diferença, não que ela "
        "seja zero. Pacote do corte, não só a bolsa."),
    "HI_scatter_imediatas.png": (
        "Como ler: só células com vaga imediata. Cada ponto é a fração de células preenchidas na 1ª chamada numa faixa "
        "de IVS de 0,010 (tamanho = número de células); cada linha é a reta local de um lado (kernel triangular, "
        "h = 0,050); a distância entre as retas no corte é o salto cru. Azul: bolsa menor; laranja: bolsa maior; "
        "tracejada: o corte. Dados crus, ciclos 1–3 juntos, sem efeitos fixos. A HI-1 do subtítulo compara células "
        "do mesmo curso e ciclo, com uma reta por ciclo; por isso pode diferir, até no sinal, da distância crua."),
    "HI_antiga_vs_imediatas.png": (
        "Como ler: em cada corte, a linha cinza é a medida antiga, que mistura vagas imediatas e de cadastro reserva "
        "(A3: todas as células abertas; N1: controle por vagas imediatas + reserva), e a azul é a mesma pergunta só "
        "com vagas imediatas (HI-1 e HI-2; no ciclo 2, tipo de vaga pelo quadro de 13/02/2026, anterior às escolhas). "
        "Ponto = salto no corte; barra = IC 95%. Mostra quanto do sinal antigo vinha de comparar vagas de tipos "
        "diferentes."),
    "HI_por_ciclo.png": (
        "Como ler: HI-1 e HI-2 estimadas em cada ciclo separado (HI-s1), por corte, e a linha empilhada (ciclos 1–3) "
        "como referência. Ponto = salto no corte; barra = IC 95%; azul: IC exclui zero; cinza: contém zero. Cada ciclo "
        "tem poucos municípios perto do corte, e os IC são largos."),
}


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["text.parse_math"] = False      # "R$ 10 mil" não pode virar fórmula
    import matplotlib.pyplot as plt
    return plt


def _wrap(txt: str, largura: int = 132) -> list[str]:
    return textwrap.wrap(txt, largura)


def figura_floresta(paineis: list[dict], titulo: str, como_ler: str, destino: Path) -> None:
    """Paineis empilhados; cada linha: rótulo à esquerda, ponto + IC no meio, valor à direita."""
    plt = _plt()
    W = 12.3
    ALT_LIN, ALT_TIT, ALT_EIXO = 0.46, 0.42, 0.55
    linhas_txt = _wrap(como_ler)
    h_rodape = 0.30 * len(linhas_txt) + 0.45
    H_ = 0.55 + sum(ALT_TIT + ALT_LIN * len(p["linhas"]) + ALT_EIXO for p in paineis) + h_rodape
    fig = plt.figure(figsize=(W, H_))
    fig.text(0.1 / W, (H_ - 0.1) / H_, titulo, fontsize=15, weight="bold", color=TINTA, va="top")
    y = H_ - 0.55
    x_plot, w_plot = 3.0, 5.4
    for p in paineis:
        fig.text(0.1 / W, (y - 0.05) / H_, p["titulo"], fontsize=13, weight="bold", color=VERDE_ESC, va="top")
        n = len(p["linhas"])
        y0 = y - ALT_TIT - ALT_LIN * n
        ax = fig.add_axes([x_plot / W, y0 / H_, w_plot / W, (ALT_LIN * n) / H_])
        esc = p.get("esc", 1.0)
        vals = [0.0]
        for ln in p["linhas"]:
            vals += [esc * ln["lo"], esc * ln["hi"]]
        lo, hi = min(vals), max(vals)
        pad = 0.06 * (hi - lo if hi > lo else 1.0)
        ax.set_xlim(lo - pad, hi + pad)
        ax.set_ylim(n - 0.5, -0.5)
        ax.axvline(0, color="#2b2b2b", lw=1.3, zorder=1)
        for i, ln in enumerate(p["linhas"]):
            cor = ln["cor"]
            ax.plot([esc * ln["lo"], esc * ln["hi"]], [i, i], color=cor, lw=3.2, solid_capstyle="butt", zorder=2)
            ax.scatter([esc * ln["tau"]], [i], s=95, color=cor, edgecolor="white", zorder=3)
            ax.text(-0.02, i, ln["rot"], transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=12,
                    color=TINTA)
            ax.text(1.02, i, ln["valor"], transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=12,
                    color=TINTA)
        ax.set_yticks([])
        ax.tick_params(axis="x", labelsize=11.5, colors=TINTA2)
        ax.xaxis.set_major_formatter(_fmt_eixo())
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
        ax.set_xlabel(p["eixo"], fontsize=11.5, color=TINTA2, labelpad=3)
        y = y0 - ALT_EIXO
    yy = h_rodape - 0.15
    for t in linhas_txt:
        fig.text(0.1 / W, yy / H_, t, fontsize=12, color=TINTA, va="top")
        yy -= 0.30
    fig.text(0.1 / W, 0.05 / H_, FONTE, fontsize=8.5, color=CINZA, va="bottom")
    fig.savefig(destino, dpi=200, facecolor="white", metadata={"Software": None})
    plt.close(fig)


def _fmt_eixo():
    from matplotlib.ticker import FuncFormatter
    return FuncFormatter(lambda v, _=None: fn(v, 0 if abs(v - round(v)) < 1e-9 else 1, sinal=False)
                         if v >= 0 else fn(v, 0 if abs(v - round(v)) < 1e-9 else 1))


def _cor_ic(r) -> str:
    return CINZA if _contem_zero(r) else AZUL


def _valor(r, holm: bool = False) -> str:
    base = f"{fv(r)} {fic(r)}"
    if holm:
        return base + f"; p Holm {fp(r['p_holm'])}"
    return base + f"; p {fp(r['p_valor'])}"


def _item(r, rot: str, cor: str | None = None, holm=False) -> dict:
    """Linha de figura na escala da estimativa (fração ou contagem); `_escala` passa para a escala exibida."""
    return {"rot": rot, "tau": float(r["tau"]), "lo": float(r["ic95_inf"]), "hi": float(r["ic95_sup"]),
            "cor": cor or _cor_ic(r), "valor": _valor(r, holm)}


def gerar_figuras(est: pd.DataFrame, dados: dict, repro: dict) -> list[dict]:
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    feitas = []
    # (1) principal.
    p1 = {"titulo": "HI-1 · célula com vaga imediata preenchida na 1ª chamada", "eixo": "salto no corte (p.p.)",
          "esc": 100.0, "linhas": [_item(_prim(est, "HI-1", c), f"{TXT_CORTE[c]}: {BOLSA[c]}", holm=True)
                                   for c in CORTES]}
    p2 = {"titulo": "HI-2 · médicos alocados em vagas imediatas por município (mesmas vagas imediatas)",
          "eixo": "salto no corte (médicos por município)", "esc": 1.0,
          "linhas": [_item(_prim(est, "HI-2", c), f"{TXT_CORTE[c]}: {BOLSA[c]}", holm=True) for c in CORTES]}
    nome = "HI_principal.png"
    figura_floresta(_escala([p1, p2]), "Comparando só vagas imediatas: salto no corte, ciclos 1–3", COMO_LER[nome],
                    DIR_FIG / nome)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "HI_estimativas.csv: HI-1 e HI-2, variante principal"})
    # (2) scatter só com células de vaga imediata.
    nome = "HI_scatter_imediatas.png"
    crus = figura_scatter(est, dados, DIR_FIG / nome)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "distancia_retas_cruas_fracao": crus,
                   "nota": "retas cruas: ciclos juntos, sem EF, kernel triangular h = 0,050, sem EP (so ilustracao)",
                   "fonte": "outcomes_V_celula.parquet (celulas so imediatas + mistas, ciclos 1-3) e HI-1 de "
                            "HI_estimativas.csv"})
    # (3) antiga × só imediatas.
    rep = {(x["id"], x["corte"]): x for x in repro["linhas"]}
    pa, pb = [], []
    for c in CORTES:
        ct = ROTULO_CORTE[c]
        a3 = rep[("A3", ct)]
        n1 = rep[("N1", ct)]
        h1, h2 = _prim(est, "HI-1", c), _prim(est, "HI-2", c)
        pa.append({"rot": f"{TXT_CORTE[c]} · antiga (A3)", "tau": a3["tau"], "lo": a3["ic95_inf"],
                   "hi": a3["ic95_sup"], "cor": CINZA,
                   "valor": f"{fpp(a3['tau'])} p.p. [{fpp(a3['ic95_inf'])}; {fpp(a3['ic95_sup'])}]"})
        pa.append({"rot": f"{TXT_CORTE[c]} · só imediatas (HI-1)", "tau": float(h1["tau"]),
                   "lo": float(h1["ic95_inf"]), "hi": float(h1["ic95_sup"]), "cor": AZUL,
                   "valor": f"{fv(h1)} {fic(h1)}"})
        pb.append({"rot": f"{TXT_CORTE[c]} · antiga (N1 S-a)", "tau": n1["tau"], "lo": n1["ic95_inf"],
                   "hi": n1["ic95_sup"], "cor": CINZA,
                   "valor": f"{fn(n1['tau'])} [{fn(n1['ic95_inf'])}; {fn(n1['ic95_sup'])}]"})
        pb.append({"rot": f"{TXT_CORTE[c]} · só imediatas (HI-2)", "tau": float(h2["tau"]),
                   "lo": float(h2["ic95_inf"]), "hi": float(h2["ic95_sup"]), "cor": AZUL,
                   "valor": f"{fv(h2)} {fic(h2)}"})
    nome = "HI_antiga_vs_imediatas.png"
    figura_floresta(_escala([{"titulo": "Célula preenchida na 1ª chamada", "eixo": "salto no corte (p.p.)",
                              "esc": 100.0, "linhas": pa},
                             {"titulo": "Médicos alocados por município, com controle das vagas",
                              "eixo": "salto no corte (médicos por município)", "esc": 1.0, "linhas": pb}]),
                    "Medida antiga (com cadastro reserva) × só vagas imediatas", COMO_LER[nome], DIR_FIG / nome)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "medida antiga: reproducao de NA_estimativas.csv (A3) e N_estimativas.csv (N1 S-a) em "
                            "HI_resumo.json; so imediatas: HI_estimativas.csv"})
    # (4) HI-s1 por ciclo.
    paineis = []
    for oid, tit, eixo, esc in (("HI-1", "HI-1 por ciclo · célula com vaga imediata preenchida", "salto no corte (p.p.)",
                                 100.0),
                                ("HI-2", "HI-2 por ciclo · médicos alocados em vagas imediatas por município",
                                 "salto no corte (médicos por município)", 1.0)):
        its = []
        for c in CORTES:
            for k in CICLOS:
                r = _sec(est, "HI-s1", oid, c, "por_ciclo", str(k))
                its.append(_item(r, f"{TXT_CORTE[c]} · ciclo {k}"))
            r = _prim(est, oid, c)
            its.append(_item(r, f"{TXT_CORTE[c]} · ciclos 1–3"))
        paineis.append({"titulo": tit, "eixo": eixo, "esc": esc, "linhas": its})
    nome = "HI_por_ciclo.png"
    figura_floresta(_escala(paineis), "HI-s1: só vagas imediatas, ciclo a ciclo", COMO_LER[nome], DIR_FIG / nome)
    feitas.append({"arquivo": rotulo(DIR_FIG / nome), "como_ler": COMO_LER[nome],
                   "fonte": "HI_estimativas.csv: HI-s1 (por ciclo) e HI-1/HI-2 principais"})
    return feitas


def _escala(paineis: list[dict]) -> list[dict]:
    """Ponto, IC e eixo na escala exibida (p.p. para frações)."""
    out = []
    for p in paineis:
        esc = p.get("esc", 1.0)
        q = dict(p)
        q["esc"] = 1.0
        q["linhas"] = [{**ln, "tau": esc * ln["tau"], "lo": esc * ln["lo"], "hi": esc * ln["hi"]} for ln in p["linhas"]]
        out.append(q)
    return out


def bins_e_retas(x_mil: np.ndarray, y: np.ndarray, corte: int, h: int = H, largura: int = 10):
    """Médias por faixa de 0,010 e reta local (kernel triangular) de cada lado, sobre dados crus (o corte no lado
    de baixo, como na rdd_lib)."""
    dist = L.normalizar_s_mil(x_mil) - corte
    dentro = (dist > -h) & (dist < h)
    dist, y = dist[dentro], y[dentro]
    pontos = []
    for a in range(-h, h, largura):
        m = (dist > a) & (dist <= a + largura)          # (a, a + 0,010]: a faixa (-0,010; 0] inclui o corte
        if m.any():
            pontos.append(((corte + a + largura / 2) / 1000.0, float(np.mean(y[m])), int(m.sum())))
    retas = []
    for lado in (-1, 1):
        m = dist <= 0 if lado < 0 else dist > 0
        k = 1.0 - np.abs(dist[m]) / h
        X = np.column_stack([np.ones(int(m.sum())), dist[m] / 1000.0])
        beta = np.linalg.lstsq(X * np.sqrt(k)[:, None], y[m] * np.sqrt(k), rcond=None)[0]
        xs = np.array([0.0, lado * h / 1000.0])
        retas.append((corte / 1000.0 + xs, beta[0] + beta[1] * xs))
    return pontos, retas


def figura_scatter(est: pd.DataFrame, dados: dict, destino: Path) -> None:
    plt = _plt()
    linhas_txt = _wrap(COMO_LER["HI_scatter_imediatas.png"])
    rodape = 0.30 * len(linhas_txt) + 0.35
    larg, alt = 5.0, 2.85
    y_ax = rodape + 0.70
    W, H_ = 12.3, y_ax + alt + 1.25
    fig = plt.figure(figsize=(W, H_))
    cel = pd.concat([dados["CK"][k] for k in CICLOS], ignore_index=True)
    cel = cel[cel["tipo_celula"].isin(["so_imed", "mista"])]
    crus = {}
    for j, c in enumerate(CORTES):
        x0 = 0.9 + j * 6.1
        r = _prim(est, "HI-1", c)
        pontos, retas = bins_e_retas(cel["s_mil"].to_numpy(float), 100.0 * cel["preenchida"].to_numpy(float), c)
        cru = float(retas[1][1][0] - retas[0][1][0])
        crus[ROTULO_CORTE[c]] = cru / 100.0
        fig.text((x0 - 0.75) / W, (H_ - 0.12) / H_, f"Corte {TXT_CORTE[c]}: {BOLSA[c]}", fontsize=14, weight="bold",
                 color=VERDE_ESC, va="top")
        fig.text((x0 - 0.75) / W, (H_ - 0.55) / H_, f"distância entre as retas cruas no corte: {fn(cru, 1)} p.p.",
                 fontsize=12, color=TINTA2, va="top")
        fig.text((x0 - 0.75) / W, (H_ - 0.85) / H_, f"HI-1 (EF de curso × ciclo, retas por ciclo): {fv(r)} {fic(r)}",
                 fontsize=12, color=TINTA2, va="top")
        ax = fig.add_axes([x0 / W, y_ax / H_, larg / W, alt / H_])
        nmax = max(n for _, _, n in pontos)
        for xm, ym, n in pontos:
            cor = AZUL if xm < c / 1000.0 else LARANJA
            ax.scatter([xm], [ym], s=40 + 220 * n / nmax, color=cor, alpha=0.85, edgecolor="white", zorder=3)
        for (xs, ys), cor in zip(retas, (AZUL, LARANJA)):
            ax.plot(xs, ys, color=cor, lw=2.4, zorder=2)
        ax.axvline(c / 1000.0, color="#2b2b2b", lw=1.2, ls=(0, (4, 3)))
        ax.set_xlim(c / 1000.0 - 0.054, c / 1000.0 + 0.054)
        xt = [c / 1000.0 - 0.05, c / 1000.0, c / 1000.0 + 0.05]
        ax.set_xticks(xt)
        ax.set_xticklabels([fn(v, 2, False) for v in xt], fontsize=12, color=TINTA2)
        ax.tick_params(axis="y", labelsize=12, colors=TINTA2)
        ax.yaxis.set_major_formatter(_fmt_eixo())
        for lado in ("top", "right"):
            ax.spines[lado].set_visible(False)
        ax.set_ylabel("células preenchidas (%)", fontsize=12, color=TINTA2)
        ax.set_xlabel("IVS 2010 oficial do município", fontsize=12, color=TINTA2)
    yy = rodape
    for t in linhas_txt:
        fig.text(0.1 / W, yy / H_, t, fontsize=12, color=TINTA, va="top")
        yy -= 0.30
    fig.text(0.1 / W, 0.04 / H_, FONTE, fontsize=8.5, color=CINZA, va="bottom")
    fig.savefig(destino, dpi=200, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    return crus


# ---------------------------------------------------------------------------
# 9. Documento 57n (gerado inteiro a partir de output/)
# ---------------------------------------------------------------------------

def bloco(nome: str, corpo: str) -> str:
    return f"<!-- HI:{nome}:inicio -->\n{corpo.rstrip()}\n<!-- HI:{nome}:fim -->"


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(l) + " |" for l in linhas]
    return "\n".join(out)


def _nab(r) -> str:
    return f"{fint(r['n_abaixo'])} / {fint(r['n_acima'])}"


NOME_LINHA = {"HI-1": "HI-1 célula com vaga imediata preenchida", "HI-2": "HI-2 alocados em vagas imediatas, por município",
              "HI-1_F13": "HI-1 com a F1.3", "HI-1_LITERAL": "HI-1 com '≥ 1 alocado' (literal)",
              "HI-1_PURA": "HI-1 só células puras", "HI-2_PURA": "HI-2 só células puras",
              "F14_TODAS": "preenchida até a 2ª chamada, todas as células", "CR_CELULA": "célula só de reserva preenchida",
              "CR_MUN": "alocados em células só de reserva, por município"}


def resposta_curta(est: pd.DataFrame, resumo: dict) -> str:
    lp = resumo["leitura_primaria"]
    h1 = {c: _prim(est, "HI-1", c) for c in CORTES}
    h2 = {c: _prim(est, "HI-2", c) for c in CORTES}
    partes = []
    if lp["codigo"] == "TODAS_CONTEM_ZERO":
        partes.append("**Comparando vagas do mesmo tipo, não se detecta diferença de preenchimento no corte** "
                      "(pacote do corte), nem em 0,300 nem em 0,400. Esta é a leitura pré-registrada do adendo para o "
                      "caso em que HI-1 e HI-2 têm IC 95% que contém zero nos dois cortes.")
    elif lp["codigo"] == "ALGUMA_REJEITA_DEPOIS_DO_HOLM":
        partes.append("**Pelo menos uma linha primária rejeita zero depois do Holm** ("
                      + ", ".join(lp["linhas_que_rejeitam_depois_do_holm"]) + "). Pela leitura pré-registrada, "
                      "relatam-se o sinal e o tamanho, com as ressalvas do diagnóstico 61 (poucos municípios, "
                      "estimativa no corte).")
    else:
        partes.append("**Depois do Holm, nenhuma linha primária rejeita zero**, mas o IC 95% convencional exclui zero "
                      "em " + ", ".join(lp["linhas_com_ic_convencional_sem_zero"]) + ". A leitura pré-registrada do "
                      "adendo tem dois casos (todas com IC que contém zero; alguma rejeita depois do Holm) e este fica "
                      "entre os dois: relatam-se o sinal e o tamanho, como sinal sem correção por comparações "
                      "múltiplas, com as ressalvas do diagnóstico 61 (poucos municípios, estimativa no corte). Não é "
                      "a frase \"não se detecta diferença\" do primeiro caso, nem um efeito confirmado.")
    for c in CORTES:
        partes.append(
            f"- **Corte {TXT_CORTE[c]}** ({BOLSA[c]}): na chance de uma célula com vaga imediata ser preenchida na 1ª "
            f"chamada, o salto no corte é {fv(h1[c])} (IC 95% {fic(h1[c])}, p Holm {fp(h1[c]['p_holm'])}; abaixo do "
            f"corte, {fmedia(h1[c])} das células são preenchidas); nos médicos alocados nessas vagas, comparando "
            f"municípios com o mesmo número de vagas imediatas, o salto é {fv(h2[c])} por município (IC 95% "
            f"{fic(h2[c])}, p Holm {fp(h2[c]['p_holm'])}; média abaixo {fmedia(h2[c])}).")
    partes.append("Um IC que contém zero quer dizer que os dados não distinguem a diferença de zero, não que ela seja "
                  "zero: o intervalo inclui quedas e aumentos do tamanho indicado. No ciclo 2, o tipo de vaga vem do "
                  "quadro de 13/02/2026, vigente na inscrição (adendo, §7); com o quadro de 19/03, refeito depois do "
                  "resultado, os números estão na seção 4 (\"tipo de vaga pós-resultado (não usar)\").")
    rep ={(x["id"], x["corte"]): x for x in resumo["reproducao"]["linhas"]}
    a3, n1 = rep[("A3", ROTULO_CORTE[300])], rep[("N1", ROTULO_CORTE[300])]

    def _exclui(x) -> str:
        return "exclui zero" if not (x["ic95_inf"] <= 0 <= x["ic95_sup"]) else "contém zero"
    partes.append(
        "**O que muda em relação à medida antiga, em 0,300.** Com todas as células abertas (A3), o salto era "
        f"{fpp(a3['tau'])} p.p. [{fpp(a3['ic95_inf'])}; {fpp(a3['ic95_sup'])}] (IC que {_exclui(a3)}); só com "
        f"células de vaga imediata (HI-1), {fv(h1[300])} {fic(h1[300])}. Com o controle por vagas imediatas + cadastro "
        f"reserva (N1 S-a), o salto era {fn(n1['tau'])} [{fn(n1['ic95_inf'])}; {fn(n1['ic95_sup'])}] (IC que "
        f"{_exclui(n1)}); só com vagas imediatas (HI-2), {fv(h2[300])} {fic(h2[300])}. Ver a figura "
        "`HI_antiga_vs_imediatas.png`.")
    sec = est[est["entra_bky"]]
    sem_zero = [r for _, r in sec.iterrows() if not _contem_zero(r)]
    if sem_zero:
        partes.append("**Secundárias com IC 95% convencional que exclui zero:** " + "; ".join(
            f"{r['linha']} ({NOME_LINHA.get(r['outcome'], r['outcome'])}, {r['variante']}, ciclos {r['ciclo']}, corte "
            f"{TXT_CORTE[int(round(float(r['corte']) * 1000))]}): {fv(r)} {fic(r)}, q BKY {fp(r['q_bky'])}"
            for r in sem_zero) + ". Nenhuma é primária; o q BKY diz quanto resta depois de considerar as "
            f"{len(sec)} secundárias.")
    else:
        partes.append("Nenhuma secundária tem IC 95% convencional que exclui zero.")
    s6 = resumo["leitura_hi_s6"]
    r6 = _sec(est, "HI-s6", "CR_CELULA", 300, "so_cadastro_reserva")
    if s6["codigo"] == "CONCENTRADA_NAS_CELULAS_DE_RESERVA":
        partes.append(f"**Onde estava a diferença (HI-s6, descritivo):** nas células só de cadastro reserva, em 0,300, "
                      f"o salto é {fv(r6)} {fic(r6)}, com IC que exclui zero, enquanto HI-1 não se distingue de zero: "
                      "pela leitura pré-registrada, a queda das medidas antigas era composição do quadro.")
    else:
        partes.append(f"**Onde estava a diferença (HI-s6, descritivo):** nas células só de cadastro reserva, em 0,300, "
                      f"o salto é {fv(r6)} {fic(r6)}, contra {fv(_prim(est, 'HI-1', 300))} "
                      f"{fic(_prim(est, 'HI-1', 300))} nas células com vaga imediata (HI-1). As células só de reserva "
                      "se preenchem por remanejamento e pela priorização da SGTES, outro mecanismo. Pela regra fixada "
                      "no código" + (", como o IC da HI-s6 contém zero" if _contem_zero(r6) else "")
                      + ", a HI-s6 **não** mostra a diferença concentrada nas células de reserva.")
    t = {(r["outcome"], r["corte"]): r for _, r in est[(est["linha"] == "HI-s7")
                                                       & (est["variante"] == "TOST_convencional")].iterrows()}
    frases = []
    for oid in ("HI-1", "HI-2"):
        for c in CORTES:
            r = t[(oid, ROTULO_CORTE[c])]
            frases.append(f"{oid} em {TXT_CORTE[c]} (margem {_margem_txt(r)}): {LEIT_TOST[r['leitura_tost']]}")
    partes.append("**Equivalência (HI-s7, TOST com as margens do protocolo 60):** " + "; ".join(frases)
                  + f" — {T36.QUALIF}. Com o IC honesto, todas ficam inconclusivas (seção 4, HI-s8).")
    partes.append(f"**Frase para a banca:** {resumo['frase_banca']}")
    return "\n\n".join(partes)


LEIT_TOST = {"EQUIVALENTE": "o salto está dentro de ± a margem", "SO_AUMENTO": "não houve aumento igual ou maior "
             "que a margem, mas uma queda desse tamanho não fica descartada", "SO_QUEDA": "não houve queda igual ou "
             "maior que a margem, mas um aumento desse tamanho não fica descartado",
             "INCONCLUSIVO": "inconclusivo (nenhum dos dois testes rejeita)"}


def _margem_txt(r) -> str:
    if r["unidade"] == UN_FRAC:
        return f"±{fpp(r['margem'], 0, False)} p.p."
    return f"±{fn(r['margem'], 2, False)} médico por município, 25% de {fn(r['media_abaixo'], 2, False)}"


def frase_banca(est: pd.DataFrame, lp: dict) -> str:
    h1 = {c: _prim(est, "HI-1", c) for c in CORTES}
    if lp["codigo"] == "TODAS_CONTEM_ZERO":
        return ("Comparando só vagas imediatas, não se detecta diferença de preenchimento em nenhum dos dois cortes: "
                f"em 0,300 o salto na chance de a célula ser preenchida é {fv(h1[300])} (IC 95% {fic(h1[300])}) e em "
                f"0,400, {fv(h1[400])} (IC 95% {fic(h1[400])}); o intervalo não descarta efeitos moderados nos dois "
                "sentidos, e o contraste é o pacote do corte, não a bolsa isolada.")
    if lp["codigo"] == "ALGUMA_REJEITA_DEPOIS_DO_HOLM":
        return ("Comparando só vagas imediatas, " + ", ".join(lp["linhas_que_rejeitam_depois_do_holm"])
                + " rejeita zero depois do Holm; o sinal e o tamanho estão na seção 3, com poucos municípios perto do "
                  "corte e para o pacote do corte, não para a bolsa isolada.")
    h2 = {c: _prim(est, "HI-2", c) for c in CORTES}
    sem_zero = [(oid, c) for oid in ("HI-1", "HI-2") for c in CORTES
                if not _contem_zero(_prim(est, oid, c))]
    detalhes = "; ".join(f"{oid} em {TXT_CORTE[c]}: {fv(_prim(est, oid, c))} {fic(_prim(est, oid, c))}, p Holm "
                         f"{fp(_prim(est, oid, c)['p_holm'])}" for oid, c in sem_zero)
    return ("Comparando só vagas imediatas, nenhuma das quatro linhas primárias rejeita zero depois do Holm. A chance "
            f"de a célula com vaga imediata ser preenchida não se distingue de zero (0,300: {fv(h1[300])} "
            f"{fic(h1[300])}; 0,400: {fv(h1[400])} {fic(h1[400])}). O IC convencional exclui zero só em "
            f"{detalhes}" + (": do lado de bolsa maior há menos médicos alocados por município, comparando municípios "
                             "com as mesmas vagas imediatas" if all(o == "HI-2" and float(_prim(est, o, c)["tau"]) < 0
                                                                    for o, c in sem_zero) else "")
            + ", mas o sinal não sobrevive à correção para quatro testes. "
            f"Em 0,400, HI-2 fica em {fv(h2[400])} {fic(h2[400])}. Tudo se refere ao pacote do corte, não à bolsa "
            "isolada.")


def tabela_amostra(resumo: dict) -> str:
    cc = resumo["amostra"]["celulas"]
    linhas = []
    for k in CICLOS:
        x = cc[f"V{k}"]
        linhas.append([str(k), fint(x["celulas_no_quadro"]), fint(x["celulas_sem_ivs_oficial_fora_da_rdd"]),
                       fint(x["celulas_so_imed"]), fint(x["celulas_mista"]), fint(x["celulas_na_amostra_hi"]),
                       fint(x["celulas_so_cr_fora_da_amostra_hi"]), fn(x["alocados_ch1_so_cr"], 0, False),
                       fint(x["f13_ausente_na_amostra_hi"])])
    t1 = _tab(["Ciclo", "Células no quadro", "Sem IVS oficial (fora da RDD)", "Só imediatas", "Mistas",
               "Na amostra HI-1", "Só cadastro reserva (fora, contadas)", "Alocados na 1ª chamada em células só de CR",
               "F1.3 ausente na amostra"], linhas)
    mm = resumo["amostra"]["municipios"]
    linhas = []
    for k in CICLOS:
        x = mm[f"V{k}"]
        linhas.append([str(k), fint(x["municipios_no_quadro_com_ivs_oficial"]),
                       fint(x["municipios_sem_ivs_oficial_fora_da_rdd"]),
                       fint(x["municipios_com_vaga_imediata_na_amostra_hi2"]),
                       fint(x["municipios_so_cadastro_reserva_fora_da_hi2"]), fint(x["municipios_com_celula_pura_hi_s4"]),
                       fint(x["municipios_com_celula_so_cr_hi_s6"])])
    t2 = _tab(["Ciclo", "Municípios no quadro com IVS oficial", "Sem IVS oficial (fora da RDD)",
               "Com vaga imediata (amostra HI-2)", "Só cadastro reserva (fora, contados)", "Com célula pura (HI-s4)",
               "Com célula só de CR (HI-s6)"], linhas)
    jj = resumo["amostra"]["janela"]
    linhas = [[TXT_CORTE[c], fint(jj[ROTULO_CORTE[c]]["celulas_hi1_abaixo"]) + " / " + fint(jj[ROTULO_CORTE[c]][
        "celulas_hi1_acima"]), fint(jj[ROTULO_CORTE[c]]["celulas_so_cr_fora_abaixo"]) + " / " + fint(
        jj[ROTULO_CORTE[c]]["celulas_so_cr_fora_acima"]), fint(jj[ROTULO_CORTE[c]]["municipio_ciclo_so_cr_fora_abaixo"])
        + " / " + fint(jj[ROTULO_CORTE[c]]["municipio_ciclo_so_cr_fora_acima"])] for c in CORTES]
    t3 = _tab(["Corte", "Células na janela, na amostra HI-1 (abaixo / acima)",
               "Células só de CR na janela, fora (abaixo / acima)",
               "Município × ciclo na janela só com CR, fora da HI-2 (abaixo / acima)"], linhas)
    return t1 + "\n\nMunicípios:\n\n" + t2 + "\n\nNa janela h = 0,050 de cada corte (ciclos 1–3 juntos):\n\n" + t3


def tabela_reproducao(resumo: dict) -> str:
    linhas = []
    for x in resumo["reproducao"]["linhas"]:
        esc_pp = x["id"] != "N1"
        val = (lambda v: fpp(v) + " p.p.") if esc_pp else (lambda v: fn(v))
        ic = (f"[{fpp(x['ic95_inf'])}; {fpp(x['ic95_sup'])}]" if esc_pp else
              f"[{fn(x['ic95_inf'])}; {fn(x['ic95_sup'])}]")
        linhas.append([x["linha"].replace(" 0.300", "").replace(" 0.400", ""), TXT_CORTE[int(round(float(
            x["corte"]) * 1000))], x["fonte"].split("/")[-1], f"{x['n_abaixo']} / {x['n_acima']}", val(x["tau"]), ic,
            fp(x["p_valor"]), f"{x['max_abs_dif']:.1e}"])
    return _tab(["Linha", "Corte", "Arquivo de referência", "n abaixo / acima", "Salto", "IC 95%", "p",
                 "máx |dif|"], linhas)


def tabela_primarias(est: pd.DataFrame) -> str:
    linhas = []
    for oid in ("HI-1", "HI-2"):
        for c in CORTES:
            r = _prim(est, oid, c)
            hon = f"[{fpp(r['ic_honesto_inf'])}; {fpp(r['ic_honesto_sup'])}]" if r["unidade"] == UN_FRAC else \
                f"[{fn(r['ic_honesto_inf'])}; {fn(r['ic_honesto_sup'])}]"
            mde = fpp(r["mde"], 1, False) + " p.p." if r["unidade"] == UN_FRAC else fn(r["mde"], 2, False)
            linhas.append([NOME_LINHA[oid], TXT_CORTE[c], _nab(r), fint(r["n_obs"]), fmedia(r), fv(r), fic(r),
                           fp(r["p_valor"]), fp(r["p_holm"]), hon, mde])
    return _tab(["Linha", "Corte", "Municípios abaixo / acima", "Linhas (células ou município × ciclo)",
                 "Média abaixo", "Salto", "IC 95% (CR1)", "p", "p Holm", "IC honesto (M ×1)", "MDE"], linhas)


def tabela_sec(est: pd.DataFrame, linha: str) -> str:
    sub = est[(est["linha"] == linha)]
    linhas = []
    for _, r in sub.iterrows():
        q = fp(r["q_bky"]) if r["entra_bky"] else "fora do BKY"
        linhas.append([NOME_LINHA.get(r["outcome"], r["outcome"]), r["variante"], r["ciclo"],
                       TXT_CORTE[int(round(float(r["corte"]) * 1000))], f"h = {fn(r['h'], 3, False)}", _nab(r),
                       fint(r["n_obs"]), fmedia(r), fv(r), fic(r), fp(r["p_valor"]), q])
    return _tab(["Linha", "Variante", "Ciclos", "Corte", "Janela", "Municípios abaixo / acima", "Linhas",
                 "Média abaixo", "Salto", "IC 95%", "p", "q BKY"], linhas)


def tabela_honesta(est: pd.DataFrame) -> str:
    sub = est[(est["linha"] == "HI-s8") & est["variante"].str.startswith("ic_honesto")]
    linhas = []
    for _, r in sub.iterrows():
        esc = r["unidade"] == UN_FRAC
        linhas.append([NOME_LINHA[r["outcome"]], TXT_CORTE[int(round(float(r["corte"]) * 1000))],
                       fn(r["fator_M"], 1, False), fv(r), fic(r), (fpp(r["vies_max"]) + " p.p.") if esc else
                       fn(r["vies_max"]), fp(r["p_valor"])])
    return _tab(["Linha", "Corte", "M (× regra de bolso)", "Salto", "IC honesto 95%", "Viés máximo", "p honesto"],
                linhas)


def tabela_tost(est: pd.DataFrame) -> str:
    sub = est[est["linha"] == "HI-s7"]
    linhas = []
    for _, r in sub.iterrows():
        esc = r["unidade"] == UN_FRAC
        marg = f"±{fpp(r['margem'], 0, False)} p.p." if esc else \
            f"±{fn(r['margem'], 2, False)} (25% de {fn(r['media_abaixo'], 2, False)})"
        mm = (fpp(r["margem_minima"], 1, False) + " p.p.") if esc else fn(r["margem_minima"], 2, False)
        linhas.append([NOME_LINHA[r["outcome"]], TXT_CORTE[int(round(float(r["corte"]) * 1000))],
                       "convencional" if r["variante"] == "TOST_convencional" else "honesto (M ×1)", marg,
                       fic(r, "ic90_inf", "ic90_sup"), fp(r["p_aumento"]), fp(r["p_queda"]),
                       LEIT_TOST[r["leitura_tost"]], mm])
    return _tab(["Linha", "Corte", "IC", "Margem", "IC 90%", "p (aumento ≥ margem)", "p (queda ≥ margem)", "Leitura",
                 "Margem mínima de equivalência"], linhas)


def tabela_quadro_c2(resumo: dict) -> str:
    q = resumo["quadro_ciclo2"]
    cf = q["conferencia"]
    a, b = resumo["amostra"]["celulas"]["V2"], q["contagem_celulas_19mar"]
    ma, mb = resumo["amostra"]["municipios"]["V2"], q["contagem_municipios_19mar"]
    linhas = []
    for rot, x, m in (("13/02/2026, vigente na inscrição (usado)", a, ma),
                      ("19/03/2026, refeito depois do resultado (pipeline; não usar)", b, mb)):
        linhas.append([rot, fint(x["celulas_so_imed"]), fint(x["celulas_mista"]), fint(x["celulas_so_cr"]),
                       fn(x["vagas_imediatas_so_imed"] + x["vagas_imediatas_mista"], 0, False),
                       fn(x["alocados_ch1_so_cr"], 0, False),
                       fint(m["municipios_com_vaga_imediata_na_amostra_hi2"])])
    t = _tab(["Quadro do ciclo 2", "Células só imediatas", "Mistas", "Só cadastro reserva",
              "Vagas imediatas", "Alocados na 1ª chamada em células só de CR", "Municípios na amostra HI-2"], linhas)
    return (t + f"\n\nConferência da leitura (`{cf['arquivo']}`, SHA-256 `{cf['sha256']}`): {cf['celulas']} células, "
            f"as mesmas do quadro de 19/03; {cf['celulas_com_total_diferente']} com total de vagas diferente; das "
            f"{cf['celulas_so_cr_13fev']} células só de reserva em 13/02, {cf['celulas_so_cr_13fev_com_imediata_19mar']} "
            f"ganharam vaga imediata em 19/03, e {cf['dessas_com_alocado']} dessas tinham alocado.")


def tabela_sens(est: pd.DataFrame) -> str:
    linhas = []
    for oid in ("HI-1", "HI-2"):
        for c in CORTES:
            for ciclo in ("1+2+3", "2"):
                base = (_prim(est, oid, c) if ciclo == "1+2+3" else
                        _sec(est, "HI-s1", oid, c, "por_ciclo", "2"))
                s19 = _uma(est, linha="SENS-19MAR", outcome=oid, corte=ROTULO_CORTE[c], ciclo=ciclo)
                linhas.append([NOME_LINHA[oid], TXT_CORTE[c], ciclo, f"{fv(base)} {fic(base)}", _nab(base),
                               f"{fv(s19)} {fic(s19)}", _nab(s19), ROTULO_19MAR])
    return _tab(["Linha", "Corte", "Ciclos", "Quadro de 13/02 (usado): salto [IC 95%]", "n abaixo / acima",
                 "Quadro de 19/03: salto [IC 95%]", "n abaixo / acima", "Rótulo"], linhas)


def tabela_editais(resumo: dict) -> str:
    ed = resumo["regra_reserva_editais"]
    linhas = [[e["edital"], e["item"], "“" + e["trecho"] + "”"] for e in ed["itens_arquivados"]]
    return "Itens de edital já arquivados sobre o cadastro reserva:\n\n" + _tab(["Edital", "Item", "Trecho"], linhas)


def gerar_doc(est: pd.DataFrame, resumo: dict) -> str:
    rep = resumo["reproducao"]
    lp = resumo["leitura_primaria"]
    figs = resumo["figuras"]
    ed = resumo["regra_reserva_editais"]
    dic = resumo["definicoes_da_base"]
    s = []
    s.append("# 57n. Resultados da H1 só com vagas imediatas (adendo 48b)")
    s.append(
        f"> **Data:** {DATA_EXECUCAO[8:10]}/{DATA_EXECUCAO[5:7]}/{DATA_EXECUCAO[:4]}.<br>\n"
        "> **Especificação:** [`48b_adendo_H1_vagas_imediatas.md`](48b_adendo_H1_vagas_imediatas.md), congelada antes "
        f"das contas (commit `{COMMIT_CONGELAMENTO}`), com a nota datada §7 (commit `{COMMIT_NOTA_7}`: no ciclo 2, tipo "
        f"de vaga pelo quadro de 13/02/2026); SHA-256 do adendo com a §7 `{resumo['adendo']['sha256']}`, conferido pelo "
        "script.<br>\n"
        "> **Estatuto:** `ADENDO_48B_POS_RESULTADO`. Pós-resultado: as medidas que misturam vaga imediata e cadastro "
        "reserva já tinham sido vistas (docs 49, 49b e 57l). Toda linha de `HI_estimativas.csv` tem "
        "`natureza_dos_dados = EMPIRICO`.<br>\n"
        "> **Script:** `scripts/rdd_bolsa/40_h1_vagas_imediatas.py` (estimadores de `rdd_lib.py` e funções dos scripts "
        "23 e 36).<br>\n"
        "> **Saídas:** `output/rdd_bolsa/HI_estimativas.csv`, `HI_resumo.json` (entradas com SHA-256, reprodução, "
        "decisões, contagens) e `HI_figuras/`.<br>\n"
        "> **Testes:** `tests/test_h1_vagas_imediatas.py`.<br>\n"
        "> **Números:** nenhum número é digitado aqui. O documento inteiro é gerado por "
        "`40_h1_vagas_imediatas.py --atualizar-doc`, e o teste confere que é idêntico ao gerado a partir de `output/`.")
    s.append("**Contraste.** O salto é o lado com bolsa maior (IVS acima do corte) menos o lado com bolsa menor; o "
             "próprio corte fica no lado de baixo. Em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil e em "
             "0,400 de R$ 15 mil para R$ 20 mil, mas outras regras federais mudam nos mesmos cortes "
             "([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)): o que se mede é o **pacote do "
             "corte**, não o incentivo de R$ 5 mil isolado, nem a participação no PMM-E, nem o Agora Tem "
             "Especialistas.")
    s.append("## 1. Resposta curta")
    s.append(bloco("resposta_curta", resposta_curta(est, resumo)))
    s.append("## 2. Amostra")
    s.append("Unidade de HI-1: célula (estabelecimento × curso) do quadro da 1ª chamada com pelo menos uma vaga "
             "imediata (células só de vagas imediatas e células mistas), ciclos 1–3. Unidade de HI-2: município com "
             "pelo menos uma dessas células, por ciclo. As células só de cadastro reserva ficam fora e são contadas; "
             "nada é imputado. **No ciclo 2, o tipo de vaga e as vagas imediatas vêm do quadro retificado de "
             "13/02/2026, vigente na inscrição** (adendo, §7; leitura de `scripts/auditoria_H1/a36_leitura.py`): o "
             "quadro de 19/03/2026, usado no pipeline, foi refeito depois do resultado preliminar "
             "([auditoria 36](../auditorias/36_auditoria_dados_H1.md), seção 3, item 3). Nos ciclos 1 e 3 nada muda.")
    s.append(bloco("quadro_ciclo2", tabela_quadro_c2(resumo)))
    s.append(bloco("amostra", tabela_amostra(resumo)))
    s.append("### 2.1 Reprodução antes das contas novas")
    s.append("Antes de estimar HI-1 e HI-2, o script refaz, das mesmas entradas e com os mesmos estimadores, o A3 por "
             "corte (`NA_estimativas.csv`), o N1 S-a por corte (`N_estimativas.csv`) e as linhas do 49b §14 por tipo "
             "de célula e só com vagas imediatas (`ND_estimativas.csv`). Se alguma não bater (tolerância relativa "
             f"{TOL_REPRO:.0e} em salto, EP e p; contagens iguais), ele para sem gravar.")
    linhas_rep = tabela_reproducao(resumo)
    s.append(bloco("reproducao", linhas_rep + "\n\n" + (
        f"Resultado: **reproduz** ({len(rep['linhas'])} linhas; máx |dif| = {rep['max_abs_dif']:.1e}). A contagem de "
        "células por tipo do 49b §14 também bate com `ND_resumo.json`. A forma literal da HI-s2 ('≥ 1 alocado') é "
        "idêntica a HI-1 célula a célula; a F1.3 difere de HI-1 em "
        + ", ".join(f"{v} célula(s) com vaga imediata no {k}" for k, v in rep["f13_difere_de_hi1"].items()) + ".")))
    s.append("## 3. Primárias (Holm entre as quatro linhas)")
    s.append("Local linear, kernel triangular, h = 0,050, cada corte separado, ciclos 1–3 empilhados com intercepto e "
             "inclinações por ciclo de cada lado e salto comum; EP agrupado por município (CR1). HI-1 tem efeitos "
             "fixos de curso × ciclo. HI-2 controla pelas vagas imediatas das células com vaga imediata, linear, com "
             "o mesmo coeficiente dos dois lados e um coeficiente por ciclo, como o S-a do protocolo 48. "
             "\"Média abaixo\" é a média simples do outcome nas linhas usadas do lado de baixo; MDE = 2,8 × EP. O IC "
             "honesto segue a regra do E6 (seção 4, HI-s8).")
    s.append(bloco("primarias", tabela_primarias(est)))
    s.append(bloco("leitura_primarias", f"Leitura pela regra pré-registrada (código `{lp['codigo']}`): "
                   + resumo["frase_banca"]))
    s.append("## 4. Secundárias (todas relatadas)")
    s.append("q-valores BKY (Benjamini, Krieger e Yekutieli) entre as secundárias que testam salto zero: HI-s1, HI-s2 "
             "(F1.3), HI-s3, HI-s4, HI-s5, HI-s6 e as janelas h da HI-s8. Ficam fora do BKY: a forma literal da "
             "HI-s2 (repete HI-1), o IC honesto (outra inferência) e o TOST (outra hipótese nula). "
             f"Família BKY: {resumo['bky']['n']} linhas.")
    tit = {"HI-s1": "HI-s1 — HI-1 e HI-2 por ciclo",
           "HI-s2": "HI-s2 — outra definição de \"preenchida\"",
           "HI-s3": "HI-s3 — HI-2 sem controle (efeito total entre vagas imediatas)",
           "HI-s4": "HI-s4 — só células puras de vaga imediata (sem as mistas)",
           "HI-s5": "HI-s5 — preenchimento até a 2ª chamada, todas as células (F1.4; ciclos 1 e 2)",
           "HI-s6": "HI-s6 — só células de cadastro reserva (descritivo)"}
    for lid, t in tit.items():
        s.append(f"### {t}")
        if lid == "HI-s2":
            s.append(bloco("nota_hi_s2", resumo["decisoes"]["definicao_preenchida"]["texto_doc"]))
        if lid == "HI-s6":
            s.append(bloco("leitura_hi_s6", "Regra fixa no código: " + resumo["leitura_hi_s6"]["regra_doc"]
                           + f" Resultado: `{resumo['leitura_hi_s6']['codigo']}`."))
        s.append(bloco(lid.replace("-", "_").lower(), tabela_sec(est, lid)))
    s.append("### HI-s7 — equivalência (TOST com as margens do protocolo 60)")
    s.append("Dois testes unilaterais a 5% (IC 90%), com a função do script 36. Margens: HI-1, ±10 p.p.; HI-2, ±25% "
             "da média abaixo do corte na mesma amostra. \"Honesto\" usa o viés máximo do IC honesto (M ×1). A "
             "margem mínima é a menor margem com o IC 90% dentro dela.")
    s.append(bloco("hi_s7", tabela_tost(est)))
    s.append("### HI-s8 — janelas h = 0,030 e 0,080 e IC honesto")
    s.append(bloco("hi_s8_h", tabela_sec(est[~est["variante"].str.startswith("ic_honesto")], "HI-s8")))
    s.append(bloco("hi_s8_honesto", tabela_honesta(est)))
    s.append("O IC honesto pela regra do E6 ajusta uma quártica num suporte largo; com um outcome binário (HI-1) ou "
             "uma contagem (HI-2) e poucos municípios, o M sai enorme e o intervalo fica muitas vezes mais largo que "
             "a própria escala do outcome, como no doc 49 (§3, item ii). Ele é relatado porque o adendo pede, mas não "
             "é ele que sustenta a leitura.")
    s.append("### Sensibilidade: tipo de vaga do ciclo 2 pelo quadro de 19/03/2026 — \"tipo de vaga pós-resultado "
             "(não usar)\"")
    s.append("Só para mostrar a diferença: as mesmas HI-1 e HI-2, com o tipo de vaga e as vagas imediatas do ciclo 2 "
             "tirados do quadro refeito depois do resultado preliminar. Fora do Holm e do BKY; não é especificação do "
             "adendo.")
    s.append(bloco("sens_19mar", tabela_sens(est)))
    s.append("## 5. Figuras")
    for f in figs:
        nome = Path(f["arquivo"]).name
        s.append(f"![{nome[:-4]}](../../{f['arquivo']})\n\n**{f['como_ler']}**")
    s.append("## 6. Limites")
    lim = [
        "**Pós-resultado.** O adendo foi escrito depois de ver que as medidas com reserva caíam em 0,300 e as "
        "restritas a vagas imediatas não; é uma correção de definição justificada pela regra de uso da reserva, não "
        "uma primeira olhada. A especificação foi congelada antes destas contas, mas a escolha de olhar só vagas "
        "imediatas não é cega ao resultado.",
        "**Pacote do corte.** Em 0,300 e 0,400 mudam a bolsa anunciada e outras regras federais (auditoria 18). Nada "
        "aqui isola o incentivo de R$ 5 mil, a participação no PMM-E ou o Agora Tem Especialistas.",
        "**Definição de \"preenchida\" por ciclo.** " + dic["texto_doc"],
        "**Células mistas.** " + resumo["decisoes"]["celulas_mistas"]["texto_doc"],
        "**Tipo de vaga do ciclo 2 (adendo, §7).** O tipo de vaga do ciclo 2 vem do quadro de 13/02/2026, anterior às "
        "escolhas; o de 19/03/2026 registra o remanejamento feito depois do resultado preliminar e condicionaria no "
        "próprio outcome (auditoria 36). A sensibilidade com 19/03 está na seção 4, rotulada \"tipo de vaga "
        "pós-resultado (não usar)\". " + resumo["exposicao_doc"],
        "**Regra da reserva nos editais.** " + ed["texto_doc"],
        "**Controle de HI-2.** As vagas imediatas são definidas pelo gestor e pela SGTES e podem ter respondido ao "
        "corte (doc 49, §4); com controle, HI-2 compara municípios com as mesmas vagas imediatas, e só é causal se "
        "essa oferta não carregar seleção. A HI-s3 relata a forma sem controle.",
        "**Precisão.** Poucos municípios ficam perto de cada corte e a estimativa é no corte (diagnóstico 61): os "
        "IC são largos, e não detectar diferença não é mostrar que ela é zero (ver o MDE e o TOST).",
    ]
    s.append(bloco("limites", "\n".join(f"- {x}" for x in lim)))
    s.append(bloco("editais", tabela_editais(resumo)))
    return "\n\n".join(s) + "\n"


MARCA = re.compile(r"<!-- HI:(?P<nome>[A-Za-z0-9_]+):inicio -->\n(?P<corpo>.*?)\n<!-- HI:(?P=nome):fim -->", re.S)


# ---------------------------------------------------------------------------
# 10. Resumo, gravação e CLI
# ---------------------------------------------------------------------------

def entradas() -> list[dict]:
    arqs = [ARQ_VC, ARQ_VM, ARQ_U, E6.ARQ_G3, A08, DICIONARIO, NA_EST, N_EST, N_RES, ND_EST, ND_RES, ADENDO,
            ARQ_C2_13FEV, AUD36]
    out = []
    for p in arqs:
        out.append({"arquivo": rotulo(p), "sha256": sha256(p)})
    return out


def regra_editais() -> dict:
    """Regra da reserva na 1ª chamada: veredito da auditoria 36 (seção 3, item 2) e itens já arquivados (doc 49, §2)."""
    n = json.loads(N_RES.read_text(encoding="utf-8"))["verificacao_cadastro_reserva"]
    if not AUD36.exists():
        raise FalhaValidacao("auditoria 36 ausente: a nota §7 do adendo depende dela")
    itens = [{"edital": e["edital"], "item": e["item"], "trecho": e["trecho"], "arquivo": e["arquivo"]}
             for e in n["editais"]]
    texto = (f"A auditoria 36 (`{rotulo(AUD36)}`, seção 3, item 2) conclui que os editais dos ciclos 1 e 3 permitem "
             "preencher a reserva na 1ª chamada (itens 4.1.3.3, 4.1.3.4 e 5.7, tabela abaixo) e que, no ciclo 2, sem "
             "o texto do edital no repositório, a reserva foi preenchida na 1ª chamada pela conversão registrada no "
             "quadro de 19/03/2026 (por isso o tipo de vaga do ciclo 2 vem do quadro de 13/02). A célula só de "
             "reserva se preenche por remanejamento e pela priorização da SGTES (item 5.7), mecanismo diferente do da "
             "vaga imediata. Pela especificação do adendo, a comparação continua sendo entre vagas do mesmo tipo.")
    return {"auditoria_36": rotulo(AUD36), "itens_arquivados": itens,
            "fonte": rotulo(N_RES) + " (verificacao_cadastro_reserva.editais)", "texto_doc": texto}


def definicoes_da_base() -> dict:
    d = json.loads(DICIONARIO.read_text(encoding="utf-8"))["variaveis"]["V_celula"]
    desc = {x["coluna"]: x["descricao"] for x in d}
    cols = ["n_alocados_ch1", "f1_3_preenchida_ch1", "f1_4_preenchida_ate_ch2"]
    texto = ("No dicionário dos outcomes (`dicionario_outcomes_funil.json`): "
             + "; ".join(f"`{c}` = {desc[c]}" for c in cols)
             + ". HI-1 usa `n_alocados_ch1 >= 1` (a definição do A3); a HI-s2 relata a F1.3 e a HI-s5 a F1.4. "
               "\"Alocado\" não é a mesma operação administrativa nos três ciclos, e o empilhamento usa intercepto e "
               "efeitos fixos por ciclo, não uma definição idêntica.")
    return {"colunas": {c: desc[c] for c in cols}, "texto_doc": texto}


def montar_resumo(est: pd.DataFrame, extras: dict, dados: dict, repro: dict, conf_c2: dict, dados_19: dict) -> dict:
    lp = leitura_primaria(est)
    s6 = leitura_hi_s6(est, repro)
    s6["regra_doc"] = ("a diferença se mostra concentrada nas células só de reserva se, em 0,300 (onde as medidas "
                       "antigas caíam), a HI-s6 por célula tiver IC 95% que exclui zero, com salto negativo, e HI-1 "
                       "tiver IC que contém zero.")
    prim = est[est["entra_holm"]]
    resumo = {
        "etapa": "Adendo 48b: H1 so com vagas imediatas (HI-1, HI-2, HI-s1 a HI-s8)",
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "data_execucao": DATA_EXECUCAO,
        "script": "scripts/rdd_bolsa/40_h1_vagas_imediatas.py",
        "adendo": {"arquivo": rotulo(ADENDO), "sha256": sha256(ADENDO), "commit_congelamento": COMMIT_CONGELAMENTO,
                   "sha256_original": SHA_ADENDO_ORIGINAL, "commit_nota_7": COMMIT_NOTA_7,
                   "sha256_com_nota_7": SHA_ADENDO_CONGELADO},
        "quadro_ciclo2": {"principal": VERSOES_C2["13fev"], "sensibilidade_nao_usar": VERSOES_C2["19mar"],
                          "auditoria_36": rotulo(AUD36), "conferencia": conf_c2,
                          "contagem_celulas_19mar": dados_19["contagem_celulas"]["V2"],
                          "contagem_municipios_19mar": dados_19["contagem_municipios"]["V2"]},
        "exposicao_previa_deste_script": (
            "Antes da nota §7 chegar, este script ja tinha sido rodado uma vez com o tipo de vaga do ciclo 2 pelo quadro "
            "de 19/03/2026 (o do pipeline), e o autor do script viu HI-1 e HI-2 dessa versao (todas com IC 95% que "
            "contem zero). A nota §7 foi escrita pelo coordenador a partir da auditoria 36, sem esses resultados. Essa "
            "versao e a sensibilidade SENS-19MAR ('tipo de vaga pos-resultado (nao usar)')."),
        "contraste": CONTRASTE,
        "salto": "lado com bolsa maior (IVS acima do corte) menos lado com bolsa menor; o corte fica no lado de baixo",
        "especificacao_comum": "local linear, kernel triangular, h = 0,050; cada corte separado; ciclos 1-3 empilhados "
                               "com intercepto e inclinacoes por ciclo x lado; CR1 por municipio",
        "entradas": entradas(),
        "reproducao": repro,
        "amostra": {"celulas": dados["contagem_celulas"], "municipios": dados["contagem_municipios"],
                    "janela": extras["janela"]},
        "holm": {"linhas": [r["id_linha"] for _, r in prim.iterrows()],
                 "p": [float(r["p_valor"]) for _, r in prim.iterrows()],
                 "p_holm": [float(r["p_holm"]) for _, r in prim.iterrows()]},
        "bky": {"n": int(est["entra_bky"].sum()), "linhas": est.loc[est["entra_bky"], "id_linha"].tolist(),
                "fora": "HI-s2 literal (repete HI-1), IC honesto (HI-s8) e TOST (HI-s7)"},
        "leitura_primaria": lp,
        "leitura_hi_s6": s6,
        "decisoes": {
            "definicao_preenchida": {"texto": DECISAO_DEFINICAO, "texto_doc": (
                "O adendo descreve HI-1 com \"a definição de preenchida de cada ciclo, igual à do A3\" e a HI-s2 com "
                "\"uma definição única (≥ 1 alocado na 1ª chamada)\". Na base, a definição do A3 já é `n_alocados_ch1 "
                ">= 1` em todos os ciclos; o que muda por ciclo é a fonte do \"alocado\". HI-1 segue o A3, para que a "
                "comparação com a medida antiga mude só a amostra. A forma literal da HI-s2 repete HI-1 (conferido "
                "célula a célula; linha `definicao_literal_alocado`, fora do BKY); por isso a HI-s2 relata também a "
                "outra definição da base, a F1.3 do protocolo 40 (ciclo 1: confirmação ou homologação).")},
            "celulas_mistas": {"texto": LIMITE_MISTAS, "texto_doc": (
                "A base não registra em que tipo de vaga cada alocado entrou. Nas células mistas contam todos os "
                "alocados da célula (HI-1 e HI-2), e o controle de HI-2 são as vagas imediatas dessas células: um "
                "alocado de célula mista que tenha ocupado vaga de cadastro reserva conta como preenchimento de vaga "
                "imediata. A HI-s4 (só células puras) mostra o resultado sem as mistas.")},
            "erro_padrao_por_ciclo": "HI-s1 da HI-2 (um ciclo, uma linha por municipio): EP HC1, igual ao CR1 por "
                                     "municipio nesse caso (fator n/(n-k) nos dois)",
            "hi_s5": "F1.4 do protocolo 40 (f1_4_preenchida_ate_ch2), ciclos 1 e 2, todas as celulas, EF de curso x "
                     "ciclo, como HI-1",
            "hi_s6": "descritivo: celulas so de CR (EF de curso x ciclo) e alocados nelas por municipio (controle = "
                     "vagas de CR dessas celulas, coeficiente por ciclo)",
            "tost": "funcao tost do script 36; margem de HI-2 = 25% da media abaixo do corte da propria linha",
        },
        "definicoes_da_base": definicoes_da_base(),
        "regra_reserva_editais": regra_editais(),
        "contagens": {"linhas": int(len(est)), "por_status": est["status"].value_counts().sort_index().to_dict(),
                      "por_linha": est["linha"].value_counts().sort_index().to_dict()},
        "integridade": {"ivs": "IVS 2010 oficial (a08); o arquivo local de IVS da auditoria 16 nao e lido",
                        "cnes": "nenhum CNES lido", "imputacao": "nada imputado nem simulado",
                        "saidas_nao_regravadas": ["N_*", "NA_*", "ND_*", "DQ_*"],
                        "dados_pessoais": "nenhum identificador pessoal (unidades: celula e municipio)"},
        "saidas": {"estimativas": rotulo(OUT / NOME_EST), "resumo": rotulo(OUT / NOME_RESUMO),
                   "figuras": rotulo(DIR_FIG), "doc": rotulo(DOC)},
        "linguagem": "pacote do corte; 'nao se detecta' nao e 'zero'; nada de 'a bolsa reduz'",
    }
    resumo["frase_banca"] = frase_banca(est, lp)
    resumo["exposicao_doc"] = (
        "Exposição: antes de a nota §7 chegar, este script já tinha sido rodado uma vez com o quadro de 19/03 no "
        "ciclo 2, e o autor do script viu essa versão de HI-1 e HI-2; a nota §7 foi escrita a partir da auditoria 36, "
        "sem esses números. A versão com 19/03 é a da sensibilidade.")
    resumo["primarias"] = {f"{r['linha']} {r['corte']}": {k: float(r[k]) for k in (
        "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "p_holm", "media_abaixo", "ic_honesto_inf", "ic_honesto_sup")}
        for _, r in prim.iterrows()}
    return resumo


def gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str, "coef_controle": str})
    for c in ("entra_holm", "entra_bky", "descritivo"):
        est[c] = est[c].astype(bool)
    for c in ("leitura_tost", "controle", "efeitos_fixos", "nota"):
        est[c] = est[c].fillna("")
    return est, json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))


def atualizar_doc() -> None:
    est, resumo = ler_saidas()
    DOC.write_text(gerar_doc(est, resumo), encoding="utf-8")


def executar(atualizar: bool) -> int:
    if sha256(ADENDO) != SHA_ADENDO_CONGELADO:
        raise FalhaValidacao("o adendo 48b mudou depois do congelamento")
    print("Carregando entradas (IVS oficial a08, outcomes do 12)...")
    todos = carregar()
    dados, dados_19 = todos["13fev"], todos["19mar"]
    print("Reproduzindo A3, N1 S-a e 49b §14 (quadro do pipeline, ciclo 2 de 19/03/2026)...")
    repro = reproduzir(dados_19)
    repro["f13_difere_de_hi1"] = {   # na amostra principal (ciclo 2 pelo quadro de 13/02)
        f"V{k}": int(((dados["CK"][k]["preenchida_f13"] != dados["CK"][k]["preenchida"])
                      & (dados["CK"][k]["tipo_celula"] != "so_cr")).sum()) for k in CICLOS}
    print(f"  reproduz: {len(repro['linhas'])} linhas, max |dif| = {repro['max_abs_dif']:.2e}")
    print("Estimando HI-1, HI-2 e HI-s1 a HI-s8...")
    est, extras = estimar(dados, dados_19)
    resumo = montar_resumo(est, extras, dados, repro, todos["conf_c2"], dados_19)
    est.to_csv(OUT / NOME_EST, index=False)
    resumo["figuras"] = gerar_figuras(est, dados, repro)
    gravar_json(OUT / NOME_RESUMO, resumo)
    for _, r in est[est["entra_holm"]].iterrows():
        print(f"  {r['linha']} {r['corte']}: tau = {r['tau']:.4f} [{r['ic95_inf']:.4f}; {r['ic95_sup']:.4f}] "
              f"p = {r['p_valor']:.4f} p_holm = {r['p_holm']:.4f}")
    if atualizar:
        atualizar_doc()
        print(f"Doc regravado: {rotulo(DOC)}")
    print(f"Gravado: {rotulo(OUT / NOME_EST)} ({len(est)} linhas), {rotulo(OUT / NOME_RESUMO)}, {rotulo(DIR_FIG)}/")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="regrava o doc 57n a partir das saidas")
    args = ap.parse_args(argv)
    try:
        return executar(args.atualizar_doc)
    except FalhaValidacao as erro:
        print(f"FALHA: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
