"""Gera as figuras e o registro de números da apresentação da banca 2 (28/10/2026).

Saída: output/apresentacao_banca2/

Não estima nada. Lê saídas já gravadas pela cadeia da RDD da bolsa (E3 a E9 e a
síntese E8) e pelos portões da regra, e as redesenha para slide. O conteúdo
canônico está em `docs/07_apresentacoes/banca2/`; este script só produz o que
ali é exibido.

Figuras
-------
1. `regra_bolsa_ivs_oficial.svg` (e `.png`, se houver Chromium) — bolsa anunciada
   contra o IVS 2010 oficial, ciclo 1, um ponto por município. É a variante A
   colorida escolhida pelo autor em 18/10/2026 (doc 38, D1), desenhada pela
   mesma função do relatório (`fig_regra_pontos`, via
   `scripts/rdd_bolsa/10_galeria_figura_regra.py`).
2. `failure_mode/regra_bolsa_arquivo_errado_FAILURE_MODE.svg` (e `.png`) — a
   mesma figura com o arquivo de IVS errado do repositório (auditoria 16) no
   eixo. Só documenta o failure mode (auditoria 16); fica numa pasta separada e
   com natureza FAILURE_MODE no manifesto. Não é IVS do município.
3. `cadeia_sintese_principal.png` — um outcome por elo da cadeia, lido de
   `output/rdd_bolsa/E8_tabela_sintese.csv`. Cada linha tem a sua escala,
   simétrica em torno do nulo (0, ou 1 na razão de chances, em escala log).
4. `cadeia_sintese_completa.png` — as 23 linhas da tabela-síntese do E8.
5. `descarte_preenchimento.png` — IC 95% convencional do preenchimento (F1.3 e
   F1.4, por ciclo e empilhado, e a âncora do E3) contra a referência de
   +10 p.p. do protocolo, lido de `output/rdd_bolsa/E8_resumo.json`.

Números
-------
`numeros_banca2.json` traz cada número exibido nos slides com o arquivo e a
chave de onde vem e o formato. Nenhum valor é digitado aqui: a lista NUMEROS só
declara seletores. Os números de texto citado (atos normativos e literatura)
são extraídos por expressão regular do arquivo-fonte; se o trecho não existir,
o script para. Os números do failure mode ficam num bloco separado.

Com `--atualizar-doc`, regrava o bloco `banca2:numeros` de
`docs/07_apresentacoes/banca2/03_proveniencia_figuras_e_numeros.md` a partir do
JSON.

Regras de integridade: lê o arquivo de IVS errado (constante
IVS_ARQUIVO_ERRADO) só para a figura 2 e para a contagem do failure mode; nada aqui é simulado, imputado ou
digitado; o script para se uma conferência falhar (por exemplo, se algum
município ficar do lado errado do corte com o IVS oficial).
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib
import matplotlib.ticker
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
OUT_RDD = RAIZ / "output" / "rdd_bolsa"
SAIDA = RAIZ / "output" / "apresentacao_banca2"
SAIDA_FM = SAIDA / "failure_mode"
DOC03 = RAIZ / "docs" / "07_apresentacoes" / "banca2" / "03_proveniencia_figuras_e_numeros.md"

E8_RESUMO = OUT_RDD / "E8_resumo.json"
E8_TABELA = OUT_RDD / "E8_tabela_sintese.csv"
E3_EST = OUT_RDD / "E3_estimativas.csv"
PORTAO_R1 = OUT_RDD / "portao_r1_ivs_oficial.json"
IDENT_LOCAL = OUT_RDD / "identificacao_arquivo_local_ivs.json"
FM_RESUMO = RAIZ / "output" / "tema_trabalho" / "failure_mode_ivs_resumo.json"
MATRIZ = OUT_RDD / "matriz_municipio_escore_administrativo.csv"
IVS_OFICIAL = RAIZ / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
IVS_ARQUIVO_ERRADO = RAIZ / "data" / "ivs_ipea_2010_municipios.csv"  # só failure mode (auditoria 16)
AUD18 = RAIZ / "docs" / "auditorias" / "18_politicas_nos_mesmos_cortes_ivs.md"
GALERIA = RAIZ / "scripts" / "rdd_bolsa" / "10_galeria_figura_regra.py"

# Parâmetros do protocolo (não são resultados).
CORTES = (0.300, 0.400)

# Paleta: a do relatório da RDD (`09_gerar_relatorio_pdf.py`, COR), validada com o
# validador do dataviz contra a superfície branca. Só duas cores de dado: azul para
# "IC exclui o nulo" e cinza de de-ênfase para "IC contém o nulo".
TINTA = "#0b0b0b"
TINTA2 = "#52514e"
MUDO = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"
AZUL = "#2a78d6"
LARANJA = "#eb6834"

MENOS = "−"

# --------------------------------------------------------------------------
# Formatação (pt-BR)
# --------------------------------------------------------------------------


def _dec(x: float, nd: int) -> str:
    s = f"{abs(x):,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def fmt(valor, formato: str) -> str:
    """Formata um valor bruto conforme o formato declarado no registro."""
    if formato == "txt":
        return str(valor)
    if formato == "fracao":  # "a/b" -> com separador de milhar
        a, b = str(valor).split("/")
        return f"{_dec(int(a), 0)}/{_dec(int(b), 0)}"
    x = float(valor)
    if not math.isfinite(x):
        raise ValueError(f"valor não finito: {valor!r}")
    if formato == "int":
        if abs(x - round(x)) > 1e-9:
            raise ValueError(f"esperava inteiro: {valor!r}")
        return _dec(round(x), 0)
    if formato == "p3":
        return "< 0,001" if x < 0.001 else _dec(x, 3)
    m = re.fullmatch(r"(d|pp|pct)(\d)(s?)", formato)
    if not m:
        raise ValueError(f"formato desconhecido: {formato}")
    tipo, nd, com_sinal = m.group(1), int(m.group(2)), m.group(3) == "s"
    if tipo in ("pp", "pct"):
        x = 100.0 * x
    corpo = _dec(x, nd)
    if com_sinal:
        zero = float(corpo.replace(".", "").replace(",", ".")) == 0.0
        sinal = "+" if (x >= 0 or zero) else MENOS
        return sinal + corpo
    return (MENOS + corpo) if x < 0 and float(corpo.replace(".", "").replace(",", ".")) != 0 else corpo


# --------------------------------------------------------------------------
# Registro de números: só seletores, nenhum valor
# --------------------------------------------------------------------------

def _t(outcome_id: str, populacao: str, ciclo: str, coluna: str) -> dict:
    return {"csv": "output/rdd_bolsa/E8_tabela_sintese.csv",
            "filtro": {"outcome_id": outcome_id, "populacao": populacao, "ciclo": ciclo}, "coluna": coluna}


def _j(arquivo: str, *caminho) -> dict:
    return {"json": arquivo, "caminho": list(caminho)}


def _jl(arquivo: str, caminho: list, filtro: dict, campo, indice: int | None = None) -> dict:
    d = {"json_lista": arquivo, "caminho": caminho, "filtro": filtro, "campo": campo}
    if indice is not None:
        d["indice"] = indice
    return d


def _x(arquivo: str, regex: str) -> dict:
    return {"texto": arquivo, "regex": regex}


E8 = "output/rdd_bolsa/E8_resumo.json"
R1 = "output/rdd_bolsa/portao_r1_ivs_oficial.json"
POP = ("F1.3", "V1+V2+V3", "1+2+3")
POS = "pós 2025-10..2026-08"
E3F = {"populacao": "P1", "outcome": "fracao_celulas_ch1_com_confirmacao_ou_homologacao",
       "especificacao": "principal"}


def _e3(corte: str, coluna: str) -> dict:
    return {"csv": "output/rdd_bolsa/E3_estimativas.csv", "filtro": {**E3F, "corte": corte}, "coluna": coluna}


def _desc(oid: str, pop: str, campo: str) -> dict:
    return _jl(E8, ["descarte", "preenchimento"], {"outcome_id": oid, "populacao": pop}, campo)


def _anc(corte: str, campo: str) -> dict:
    return _jl(E8, ["descarte", "ancora_E3_ciclo1"], {"corte": corte}, campo)


def _e9(ciclo: str, campo: str, indice: int | None = None) -> dict:
    s = _j(E8, "e9", "principal", ciclo, campo)
    if indice is not None:
        s["caminho"].append(indice)
    return s


# (código, natureza, seletor, formato, descrição)
NUMEROS: list[tuple[str, str, dict, str, str]] = [
    # Regra (portão R1 com o IVS oficial)
    ("R_ESCORE_IGUAIS", "EMPIRICO", _j(R1, "escore_administrativo_e_ivs_2010_oficial", "valores_iguais_3_casas"),
     "fracao", "escore da relação nominal do MS igual ao IVS 2010 oficial, a 3 casas"),
    ("R_CATEG_IGUAIS", "EMPIRICO", _j(R1, "escore_administrativo_e_ivs_2010_oficial", "categorias_iguais"),
     "fracao", "categoria de IVS do consolidado PMMB igual à classe do IVS oficial"),
    ("R_C1_MUN", "EMPIRICO", _j(R1, "populacoes", "P1", "municipios"), "int", "municípios do ciclo 1"),
    ("R_C1_REPR", "EMPIRICO", _j(R1, "populacoes", "P1", "regra_reproduz"), "int", "ciclo 1: faixa reproduzida"),
    ("R_C2_MUN", "EMPIRICO", _j(R1, "populacoes", "P2", "municipios"), "int", "municípios do ciclo 2"),
    ("R_C2_REPR", "EMPIRICO", _j(R1, "populacoes", "P2", "regra_reproduz"), "int", "ciclo 2: faixa reproduzida"),
    ("R_C3_MUN", "EMPIRICO", _j(R1, "populacoes", "ciclo_3_congelado", "municipios"), "int",
     "municípios do ciclo 3 (congelado)"),
    ("R_C3_REPR", "EMPIRICO", _j(R1, "populacoes", "ciclo_3_congelado", "regra_reproduz"), "int",
     "ciclo 3: faixa reproduzida (um município criado depois de 2010 sem IVS)"),
    ("R_LADO_ERRADO_OFICIAL", "EMPIRICO", {"calculado": "lado_errado_oficial"}, "int",
     "municípios do ciclo 1 do lado errado do corte com o IVS oficial (figura da regra)"),
    # Primárias e Holm
    ("P1_TAU", "EMPIRICO", _j(E8, "holm", "P1", "tau"), "d2s", "P1: salto (DP)"),
    ("P1_INF", "EMPIRICO", _j(E8, "holm", "P1", "ic95_inf"), "d2s", "P1: IC 95% inferior"),
    ("P1_SUP", "EMPIRICO", _j(E8, "holm", "P1", "ic95_sup"), "d2s", "P1: IC 95% superior"),
    ("P1_P", "EMPIRICO", _j(E8, "holm", "P1", "p_valor"), "p3", "P1: p"),
    ("P1_HOLM", "EMPIRICO", _j(E8, "holm", "P1", "p_holm"), "p3", "P1: p Holm"),
    ("P2_TAU", "EMPIRICO", _j(E8, "holm", "P2", "tau"), "d3s", "P2: DiRD (vínculos por 10 mil hab.)"),
    ("P2_INF", "EMPIRICO", _j(E8, "holm", "P2", "ic95_inf"), "d3s", "P2: IC 95% inferior"),
    ("P2_SUP", "EMPIRICO", _j(E8, "holm", "P2", "ic95_sup"), "d3s", "P2: IC 95% superior"),
    ("P2_P", "EMPIRICO", _j(E8, "holm", "P2", "p_valor"), "p3", "P2: p"),
    ("P2_HOLM", "EMPIRICO", _j(E8, "holm", "P2", "p_holm"), "p3", "P2: p Holm"),
    # Atração (F1), empilhado
    ("F11_EST", "EMPIRICO", _t("F1.1", *POP[1:], "estimativa"), "d3s", "F1.1 candidatos de 1ª opção por célula"),
    ("F11_INF", "EMPIRICO", _t("F1.1", *POP[1:], "ic95_inf"), "d3s", "F1.1 IC inferior"),
    ("F11_SUP", "EMPIRICO", _t("F1.1", *POP[1:], "ic95_sup"), "d3s", "F1.1 IC superior"),
    ("F12_EST", "EMPIRICO", _t("F1.2", *POP[1:], "estimativa"), "pp1s", "F1.2 fração de células com candidato"),
    ("F12_INF", "EMPIRICO", _t("F1.2", *POP[1:], "ic95_inf"), "pp1s", "F1.2 IC inferior"),
    ("F12_SUP", "EMPIRICO", _t("F1.2", *POP[1:], "ic95_sup"), "pp1s", "F1.2 IC superior"),
    ("F13_EST", "EMPIRICO", _t(*POP, "estimativa"), "pp1s", "F1.3 preenchidas na 1ª chamada"),
    ("F13_INF", "EMPIRICO", _t(*POP, "ic95_inf"), "pp1s", "F1.3 IC inferior"),
    ("F13_SUP", "EMPIRICO", _t(*POP, "ic95_sup"), "pp1s", "F1.3 IC superior"),
    ("F13_Q", "EMPIRICO", _t(*POP, "q_bky"), "d3", "F1.3 q BKY"),
    ("F14_EST", "EMPIRICO", _t("F1.4", "V1+V2", "1+2", "estimativa"), "pp1s", "F1.4 preenchidas até a 2ª chamada"),
    ("F14_INF", "EMPIRICO", _t("F1.4", "V1+V2", "1+2", "ic95_inf"), "pp1s", "F1.4 IC inferior"),
    ("F14_SUP", "EMPIRICO", _t("F1.4", "V1+V2", "1+2", "ic95_sup"), "pp1s", "F1.4 IC superior"),
    ("F11_Q", "EMPIRICO", _t("F1.1", *POP[1:], "q_bky"), "d3", "F1.1 q BKY"),
    ("F12_Q", "EMPIRICO", _t("F1.2", *POP[1:], "q_bky"), "d3", "F1.2 q BKY"),
    ("F14_Q", "EMPIRICO", _t("F1.4", "V1+V2", "1+2", "q_bky"), "d3", "F1.4 q BKY"),
    # Descarte (+10 p.p.)
    ("D_F13_MAXCONV", "EMPIRICO", _desc("F1.3", "V1+V2+V3", "maior_ic95_sup_convencional"), "pp1s",
     "F1.3 empilhado: maior limite superior entre as especificações convencionais"),
    ("D_F13_NCONV", "EMPIRICO", _desc("F1.3", "V1+V2+V3", "n_especificacoes_convencionais"), "int",
     "F1.3 empilhado: número de especificações convencionais"),
    ("D_F14_MAXCONV", "EMPIRICO", _desc("F1.4", "V1+V2", "maior_ic95_sup_convencional"), "pp1s",
     "F1.4 empilhado: maior limite superior convencional"),
    ("D_F13_V1_SUP", "EMPIRICO", _desc("F1.3", "V1", "ic95_sup"), "pp1s", "F1.3 ciclo 1: IC superior"),
    ("D_F13_V2_SUP", "EMPIRICO", _desc("F1.3", "V2", "ic95_sup"), "pp1s", "F1.3 ciclo 2: IC superior"),
    ("D_F13_V3_SUP", "EMPIRICO", _desc("F1.3", "V3", "ic95_sup"), "pp1s", "F1.3 ciclo 3: IC superior"),
    ("E3_300_TAU", "EMPIRICO", _anc("0.300", "tau"), "pp1s", "E3 âncora 0,300: salto"),
    ("E3_300_INF", "EMPIRICO", _anc("0.300", "ic95_inf"), "pp1s", "E3 âncora 0,300: IC inferior"),
    ("E3_300_SUP", "EMPIRICO", _anc("0.300", "ic95_sup"), "pp1s", "E3 âncora 0,300: IC superior"),
    ("E3_300_MDE", "EMPIRICO", _anc("0.300", "mde_80"), "pp1", "E3 âncora 0,300: MDE de 80% (E5)"),
    ("E3_400_TAU", "EMPIRICO", _anc("0.400", "tau"), "pp1s", "E3 âncora 0,400: salto"),
    ("E3_400_INF", "EMPIRICO", _anc("0.400", "ic95_inf"), "pp1s", "E3 âncora 0,400: IC inferior"),
    ("E3_400_SUP", "EMPIRICO", _anc("0.400", "ic95_sup"), "pp1s", "E3 âncora 0,400: IC superior"),
    ("E3_400_MDE", "EMPIRICO", _anc("0.400", "mde_80"), "pp1", "E3 âncora 0,400: MDE de 80% (E5)"),
    ("E3_300_NABX", "EMPIRICO", _e3("0.3", "n_abaixo"), "int", "E3 0,300: municípios abaixo do corte (h = 0,050)"),
    ("E3_300_NACI", "EMPIRICO", _e3("0.3", "n_acima"), "int", "E3 0,300: municípios acima do corte"),
    ("E3_400_NABX", "EMPIRICO", _e3("0.4", "n_abaixo"), "int", "E3 0,400: municípios abaixo do corte"),
    ("E3_400_NACI", "EMPIRICO", _e3("0.4", "n_acima"), "int", "E3 0,400: municípios acima do corte"),
    # Escolha (E9)
    ("E9_C1_RC", "EMPIRICO", _e9("1", "rc_5mil"), "d2", "E9 ciclo 1: razão de chances por +R$ 5 mil"),
    ("E9_C1_RCI", "EMPIRICO", _e9("1", "rc_5mil_ic95", 0), "d2", "E9 ciclo 1: IC inferior"),
    ("E9_C1_RCS", "EMPIRICO", _e9("1", "rc_5mil_ic95", 1), "d2", "E9 ciclo 1: IC superior"),
    ("E9_C1_P", "EMPIRICO", _e9("1", "p"), "p3", "E9 ciclo 1: p"),
    ("E9_C2_RC", "EMPIRICO", _e9("2", "rc_5mil"), "d2", "E9 ciclo 2: razão de chances"),
    ("E9_C2_RCI", "EMPIRICO", _e9("2", "rc_5mil_ic95", 0), "d2", "E9 ciclo 2: IC inferior"),
    ("E9_C2_RCS", "EMPIRICO", _e9("2", "rc_5mil_ic95", 1), "d2", "E9 ciclo 2: IC superior"),
    ("E9_C2_P", "EMPIRICO", _e9("2", "p"), "p3", "E9 ciclo 2: p"),
    ("E9_C3_RC", "EMPIRICO", _e9("3", "rc_5mil"), "d2", "E9 ciclo 3: razão de chances"),
    ("E9_C3_RCI", "EMPIRICO", _e9("3", "rc_5mil_ic95", 0), "d2", "E9 ciclo 3: IC inferior"),
    ("E9_C3_RCS", "EMPIRICO", _e9("3", "rc_5mil_ic95", 1), "d2", "E9 ciclo 3: IC superior"),
    ("E9_C3_P", "EMPIRICO", _e9("3", "p"), "p3", "E9 ciclo 3: p"),
    ("E9_EMP_RC", "EMPIRICO", _e9("empilhado", "rc_5mil"), "d2", "E9 empilhado: razão de chances"),
    ("E9_EMP_RCI", "EMPIRICO", _e9("empilhado", "rc_5mil_ic95", 0), "d2", "E9 empilhado: IC inferior"),
    ("E9_EMP_RCS", "EMPIRICO", _e9("empilhado", "rc_5mil_ic95", 1), "d2", "E9 empilhado: IC superior"),
    ("E9_EMP_P", "EMPIRICO", _e9("empilhado", "p"), "p3", "E9 empilhado: p"),
    ("E9_EMP_N", "EMPIRICO", _e9("empilhado", "n_candidatos"), "int", "E9 empilhado: candidatos de 1ª opção"),
    ("E9_C2_NPLAC", "EMPIRICO", _j(E8, "e9", "ciclo2", "placebo", "n_placebos"), "int", "E9: cortes placebo"),
    ("E9_C2_PLAC_GE", "EMPIRICO", _j(E8, "e9", "ciclo2", "placebo", "n_abs_t_placebo_ge_real"), "int",
     "E9 ciclo 2: placebos com |t| ≥ t real"),
    ("E9_C2_PPOSTO", "EMPIRICO", _j(E8, "e9", "ciclo2", "placebo", "p_posto"), "p3", "E9 ciclo 2: p por posto"),
    ("E9_C2_WEBB", "EMPIRICO", _j(E8, "e9", "ciclo2", "p_score_webb"), "p3", "E9 ciclo 2: p do score bootstrap (Webb)"),
    ("E9_C2_CV3", "EMPIRICO", _j(E8, "e9", "ciclo2", "p_cv3"), "p3", "E9 ciclo 2: p do CV3"),
    ("E9_C2_CUB_P", "EMPIRICO", _j(E8, "e9", "ciclo2", "spline_cubico", "p"), "p3", "E9 ciclo 2: p com spline cúbico"),
    ("E9_PLAC_FRAC", "EMPIRICO", _j(E8, "e9", "empilhado", "placebo", "fracao_abs_t_maior_1_96"), "pct1",
     "E9 empilhado: fração de cortes placebo com |t| > 1,96 (%)"),
    ("E9_C2_PLAC_FRAC", "EMPIRICO", _j(E8, "e9", "ciclo2", "placebo", "fracao_abs_t_maior_1_96"), "pct1",
     "E9 ciclo 2: fração de cortes placebo com |t| > 1,96 (%)"),
    ("E9_EMP_PLAC_GE", "EMPIRICO", _j(E8, "e9", "empilhado", "placebo", "n_abs_t_placebo_ge_real"), "int",
     "E9 empilhado: placebos com |t| ≥ t real"),
    ("E9_EMP_PPOSTO", "EMPIRICO", _j(E8, "e9", "empilhado", "placebo", "p_posto"), "p3", "E9 empilhado: p por posto"),
    ("E9_EMP_SEM2_P", "EMPIRICO", _j(E8, "e9", "empilhado", "ciclos_1_e_3", "p"), "p3",
     "E9 ciclos 1 e 3 empilhados, sem o 2: p"),
    ("E9_EMP_Q_P", "EMPIRICO", _j(E8, "e9", "empilhado", "cochran_Q", "p"), "p3", "E9: p do Q de Cochran"),
    ("E9_EMP_CUB_P", "EMPIRICO", _j(E8, "e9", "empilhado", "spline_cubico", "p"), "p3",
     "E9 empilhado: p com spline cúbico"),
    ("E9_CURSO_WEBB", "EMPIRICO", _j(E8, "e9", "empilhado", "cluster_curso", "p_score_webb"), "p3",
     "E9 empilhado: p do score (Webb) com cluster por curso"),
    # Presença (F2), oferta (F3), placebos
    ("F21_EST", "EMPIRICO", _t("F2.1", "V1+V2", "1+2", "estimativa"), "d3s", "F2.1 especialistas ativos por célula"),
    ("F21_INF", "EMPIRICO", _t("F2.1", "V1+V2", "1+2", "ic95_inf"), "d3s", "F2.1 IC inferior"),
    ("F21_SUP", "EMPIRICO", _t("F2.1", "V1+V2", "1+2", "ic95_sup"), "d3s", "F2.1 IC superior"),
    ("F23_EST", "EMPIRICO", _t("F2.3", "V1+V2", "1+2", "estimativa"), "pp1s", "F2.3 algum especialista ativo"),
    ("F23_INF", "EMPIRICO", _t("F2.3", "V1+V2", "1+2", "ic95_inf"), "pp1s", "F2.3 IC inferior"),
    ("F23_SUP", "EMPIRICO", _t("F2.3", "V1+V2", "1+2", "ic95_sup"), "pp1s", "F2.3 IC superior"),
    ("F32_EST", "EMPIRICO", _t("F3.2", "U", POS, "estimativa"), "pp1s", "F3.2 município com especialista nas CBO-alvo"),
    ("F32_INF", "EMPIRICO", _t("F3.2", "U", POS, "ic95_inf"), "pp1s", "F3.2 IC inferior"),
    ("F32_SUP", "EMPIRICO", _t("F3.2", "U", POS, "ic95_sup"), "pp1s", "F3.2 IC superior"),
    ("F33_EST", "EMPIRICO", _t("F3.3", "U", POS, "estimativa"), "d1s", "F3.3 horas SUS por 10 mil hab."),
    ("F33_INF", "EMPIRICO", _t("F3.3", "U", POS, "ic95_inf"), "d1s", "F3.3 IC inferior"),
    ("F33_SUP", "EMPIRICO", _t("F3.3", "U", POS, "ic95_sup"), "d1s", "F3.3 IC superior"),
    ("FP1_EST", "EMPIRICO", _t("F3.P1", "U", POS, "estimativa"), "d3s", "placebo: generalistas por 10 mil hab."),
    ("FP1_INF", "EMPIRICO", _t("F3.P1", "U", POS, "ic95_inf"), "d3s", "placebo generalistas: IC inferior"),
    ("FP1_SUP", "EMPIRICO", _t("F3.P1", "U", POS, "ic95_sup"), "d3s", "placebo generalistas: IC superior"),
    ("FP2_EST", "EMPIRICO", _t("F3.P2", "U", POS, "estimativa"), "d3s", "placebo: especialistas fora das CBO-alvo"),
    ("FP2_INF", "EMPIRICO", _t("F3.P2", "U", POS, "ic95_inf"), "d3s", "placebo fora das CBO-alvo: IC inferior"),
    ("FP2_SUP", "EMPIRICO", _t("F3.P2", "U", POS, "ic95_sup"), "d3s", "placebo fora das CBO-alvo: IC superior"),
    # Estudo de evento e ameaças (E7)
    ("E7_SEQ_N", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "maior_sequencia_p_menor_005", "n_meses"), "int",
     "E7 F3.1 U 0,300: meses consecutivos do pós com p < 0,05"),
    ("E7_DEPOIS_N", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "meses_pos_depois_da_sequencia"), "int",
     "E7: meses do pós depois da sequência"),
    ("E7_DEPOIS_SIG", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "meses_pos_depois_da_sequencia_p_menor_005"), "int",
     "E7: desses, com p < 0,05"),
    ("E7_ANTES_N", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "meses_antes_da_referencia"), "int",
     "E7: meses antes da referência"),
    ("E7_ANTES_SIG", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "meses_antes_da_referencia_p_menor_005"), "int",
     "E7: desses, com p < 0,05"),
    ("E7_PREEXT_TAU", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "nivel_pre_extra", "tau"), "d3s",
     "E7 F3.1 U 0,300: descontinuidade em nível no pré extra (2022-01..2023-03)"),
    ("E7_PREEXT_INF", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "nivel_pre_extra", "ic95_inf"), "d3s", "IC inferior"),
    ("E7_PREEXT_SUP", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "nivel_pre_extra", "ic95_sup"), "d3s", "IC superior"),
    ("E7_DIRD300_TAU", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "dird_principal", "tau"), "d3s",
     "E7 F3.1 U 0,300: DiRD principal"),
    ("E7_DIRD300_INF", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "dird_principal", "ic95_inf"), "d3s", "IC inferior"),
    ("E7_DIRD300_SUP", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "dird_principal", "ic95_sup"), "d3s", "IC superior"),
    ("E7_DIRD300_P", "EMPIRICO", _j(E8, "e7", "f31_U_0300", "dird_principal", "p_valor"), "p3", "p"),
    ("E7_GEN_N", "EMPIRICO", _j(E8, "e7", "generalistas_U_0400", "pre_extra_meses"), "int",
     "E7 generalistas U 0,400: meses do pré extra"),
    ("E7_GEN_SIG", "EMPIRICO", _j(E8, "e7", "generalistas_U_0400", "pre_extra_p_menor_005"), "int",
     "E7 generalistas U 0,400: desses, com p < 0,05"),
    ("E7_V1_N", "EMPIRICO", _j(E8, "e7", "v1_0300", "meses_pre_extra_e_entre"), "int",
     "E7 V1 0,300: meses do pré extra e do trecho até o pré"),
    ("E7_V1_SIG", "EMPIRICO", _j(E8, "e7", "v1_0300", "meses_pre_extra_e_entre_p_menor_005"), "int",
     "E7 V1 0,300: desses, com p < 0,05"),
    # Famílias de testes (BKY)
    *[(f"FAM_{f}_{s}", "EMPIRICO", _j(E8, "familias", f, "resumo_testes", k), fm, f"{f}: {d}")
      for f in ("F0", "F1", "F2", "F3", "F4")
      for s, k, fm, d in (("N", "linhas_principais_no_bky", "int", "linhas principais no BKY"),
                          ("P", "p_menor_005", "int", "linhas com p < 0,05"),
                          ("Q", "q_menor_005", "int", "linhas com q BKY < 0,05"),
                          ("MINQ", "menor_q", "d3", "menor q BKY"))],
    # Seleção nas pontas (F0.2, F4) e V1 em 0,400
    ("F02_EST", "EMPIRICO", _t("F0.2", "U", "1", "estimativa"), "d3s", "F0.2 vagas imediatas por 10 mil hab., ciclo 1"),
    ("F02_INF", "EMPIRICO", _t("F0.2", "U", "1", "ic95_inf"), "d3s", "F0.2 IC inferior"),
    ("F02_SUP", "EMPIRICO", _t("F0.2", "U", "1", "ic95_sup"), "d3s", "F0.2 IC superior"),
    ("F02_Q", "EMPIRICO", _t("F0.2", "U", "1", "q_bky"), "d3", "F0.2 q BKY"),
    ("F41_EST", "EMPIRICO", _t("F4.1", *POP[1:], "estimativa"), "d3s", "F4.1 nota média dos alocados"),
    ("F41_INF", "EMPIRICO", _t("F4.1", *POP[1:], "ic95_inf"), "d3s", "F4.1 IC inferior"),
    ("F41_SUP", "EMPIRICO", _t("F4.1", *POP[1:], "ic95_sup"), "d3s", "F4.1 IC superior"),
    ("F42_EST", "EMPIRICO", _t("F4.2", *POP[1:], "estimativa"), "d3s", "F4.2 nota média dos candidatos de 1ª opção"),
    ("F42_INF", "EMPIRICO", _t("F4.2", *POP[1:], "ic95_inf"), "d3s", "F4.2 IC inferior"),
    ("F42_SUP", "EMPIRICO", _t("F4.2", *POP[1:], "ic95_sup"), "d3s", "F4.2 IC superior"),
    ("F42_P", "EMPIRICO", _t("F4.2", *POP[1:], "p_valor"), "p3", "F4.2 p"),
    ("F42_Q", "EMPIRICO", _t("F4.2", *POP[1:], "q_bky"), "d3", "F4.2 q BKY"),
    ("SEL_DENS", "EMPIRICO", _j(E8, "selecao_v1_0400", "densidade_V1_0400", "razao"), "d2",
     "V1 0,400: razão de densidades"),
    ("SEL_DENS_INF", "EMPIRICO", _j(E8, "selecao_v1_0400", "densidade_V1_0400", "ic95", 0), "d2", "IC inferior"),
    ("SEL_DENS_SUP", "EMPIRICO", _j(E8, "selecao_v1_0400", "densidade_V1_0400", "ic95", 1), "d2", "IC superior"),
    ("SEL_BAL_P", "EMPIRICO", _j(E8, "selecao_v1_0400", "balanco_V1_0400", "p_menor_005"), "int",
     "V1 0,400: covariáveis com p < 0,05"),
    ("SEL_BAL_N", "EMPIRICO", _j(E8, "selecao_v1_0400", "balanco_V1_0400", "covariaveis_testadas"), "int",
     "V1 0,400: covariáveis testadas"),
    ("SEL_PESO", "EMPIRICO", _j(E8, "selecao_v1_0400", "peso_c1_400_no_P1"), "pct1",
     "peso do grupo ciclo 1 × 0,400 no P1 empilhado (%)"),
    ("E8_LINHAS", "EMPIRICO", _j(E8, "saidas", "E8_tabela_sintese.csv", "linhas"), "int",
     "linhas principais da tabela-síntese do E8"),
    # Magnitude
    ("MAG_DEG300", "EMPIRICO", _j(E8, "degrau_relativo_bolsa", "0.300", "relativo"), "pct0s",
     "degrau relativo da bolsa em 0,300 (%)"),
    ("MAG_DEG400", "EMPIRICO", _j(E8, "degrau_relativo_bolsa", "0.400", "relativo"), "pct0s",
     "degrau relativo da bolsa em 0,400 (%)"),
]

# Números do failure mode: só documentam o arquivo errado. Bloco separado.
NUMEROS_FM: list[tuple[str, str, dict, str, str]] = [
    ("FM_NMU", "FAILURE_MODE", _j("output/rdd_bolsa/identificacao_arquivo_local_ivs.json", "mecanismo",
                                  "linha_escolhida_por_municipio", "Negro / Mulher / Urbano"), "int",
     "municípios em que o arquivo errado traz a linha Negro / Mulher / Urbano"),
    ("FM_MUN", "FAILURE_MODE", _j("output/rdd_bolsa/identificacao_arquivo_local_ivs.json", "mecanismo",
                                  "conferencia_por_coluna", "municipios"), "int", "municípios do arquivo"),
    ("FM_NMU_PCT", "FAILURE_MODE", {"razao": ["FM_NMU", "FM_MUN"]}, "pct0", "FM_NMU / FM_MUN (%)"),
    ("FM_IGUAIS", "FAILURE_MODE", _j("output/tema_trabalho/failure_mode_ivs_resumo.json", "arquivo_errado",
                                     "ivs_igual_3_casas"), "int",
     "municípios em que o arquivo errado acerta o IVS oficial a 3 casas"),
    ("FM_CORR", "FAILURE_MODE", _j("output/tema_trabalho/failure_mode_ivs_resumo.json", "arquivo_errado",
                                   "correlacao_ivs"), "d2", "correlação entre o arquivo errado e o IVS oficial"),
    ("FM_LADO_ERRADO", "FAILURE_MODE", {"calculado": "lado_errado_arquivo_errado"}, "int",
     "municípios do ciclo 1 do lado errado do corte com o arquivo errado no eixo"),
]

# Texto citado: atos normativos (auditoria 18) e literatura (copiada pelo E8 do doc 20).
NUMEROS_TEXTO: list[tuple[str, str, dict, str, str]] = [
    ("CP_EMENDAS", "TEXTO_NORMATIVO", _x("docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md",
                                          r"parcelas PAP e MAC (\+\d+%)"), "txt",
     "acréscimo no teto de emendas e parcelas de custeio para IVS > 0,3"),
    ("CP_752_300", "TEXTO_NORMATIVO", _x("docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md",
                                          r"\((\d+% → \d+%) de teto de coparticipação"), "txt",
     "Portaria 752/2023: teto de coparticipação do PMMB em 0,3"),
    ("CP_752_400", "TEXTO_NORMATIVO", _x("docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md",
                                          r"texto da 752 \((\d+% → \d+%)\)"), "txt",
     "Portaria 752/2023: teto de coparticipação do PMMB em 0,4"),
    ("CP_IED_300", "TEXTO_NORMATIVO", _x("docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md",
                                          r"estrato IED da APS nos portes (\d e \d)"), "txt",
     "IED da APS: portes em que o estrato muda em 0,300"),
    ("CP_IED_400", "TEXTO_NORMATIVO", _x("docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md",
                                          r"estrato IED nos portes (\d, \d e \d)"), "txt",
     "IED da APS: portes em que o estrato muda em 0,400"),
    ("LIT_DALBO_SAL", "CITACAO_LITERATURA", _x(E8, r"salário anunciado sorteado \((\+\d+%)\)"), "txt",
     "Dal Bó, Finan e Rossi (2013): aumento sorteado do salário anunciado"),
    ("LIT_DALBO_ACEIT", "CITACAO_LITERATURA", _x(E8, r"aceitação (\+\d+,\d) p\.p\."), "txt",
     "Dal Bó, Finan e Rossi (2013): efeito na aceitação (p.p.)"),
    ("LIT_DALBO_CAND", "CITACAO_LITERATURA", _x(E8, r"candidaturas \*\*(\+\d+%)\*\*"), "txt",
     "Dal Bó, Finan e Rossi (2013): efeito nas candidaturas"),
    ("LIT_BOBBA", "CITACAO_LITERATURA", _x(E8, r"define adicional de (\+\d+%)"), "txt",
     "Bobba et al.: adicional por regra"),
]


# --------------------------------------------------------------------------
# Leitura
# --------------------------------------------------------------------------


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


_CACHE: dict[str, object] = {}


def _ler_json(rel: str):
    if rel not in _CACHE:
        _CACHE[rel] = json.loads((RAIZ / rel).read_text(encoding="utf-8"))
    return _CACHE[rel]


def _ler_csv(rel: str) -> pd.DataFrame:
    if rel not in _CACHE:
        _CACHE[rel] = pd.read_csv(RAIZ / rel, dtype=str, keep_default_na=False)
    return _CACHE[rel]


def _texto(rel: str) -> str:
    p = RAIZ / rel
    if p.suffix == ".json":
        return json.dumps(_ler_json(rel), ensure_ascii=False)
    return p.read_text(encoding="utf-8")


def _navegar(obj, caminho):
    for k in caminho:
        obj = obj[k]
    return obj


def resolver(seletor: dict, calculados: dict, ja: dict):
    """Devolve o valor bruto do seletor. Para quando a chave não existe ou não é única."""
    if "json" in seletor:
        return _navegar(_ler_json(seletor["json"]), seletor["caminho"])
    if "json_lista" in seletor:
        lista = _navegar(_ler_json(seletor["json_lista"]), seletor["caminho"])
        achados = [r for r in lista if all(str(r.get(k)) == v for k, v in seletor["filtro"].items())]
        if len(achados) != 1:
            raise SystemExit(f"ERRO: seletor {seletor} achou {len(achados)} linhas")
        v = achados[0][seletor["campo"]]
        return v[seletor["indice"]] if "indice" in seletor else v
    if "csv" in seletor:
        d = _ler_csv(seletor["csv"])
        m = np.ones(len(d), bool)
        for k, v in seletor["filtro"].items():
            m &= (d[k] == v).to_numpy()
        if m.sum() != 1:
            raise SystemExit(f"ERRO: seletor {seletor} achou {int(m.sum())} linhas")
        bruto = d.loc[m, seletor["coluna"]].iloc[0]
        if bruto == "":
            raise SystemExit(f"ERRO: valor vazio em {seletor}")
        return float(bruto)
    if "texto" in seletor:
        achados = re.findall(seletor["regex"], _texto(seletor["texto"]))
        if not achados:
            raise SystemExit(f"ERRO: trecho {seletor['regex']!r} ausente de {seletor['texto']}")
        if len(set(achados)) != 1:
            raise SystemExit(f"ERRO: trecho {seletor['regex']!r} ambíguo em {seletor['texto']}: {achados}")
        return achados[0]
    if "calculado" in seletor:
        return calculados[seletor["calculado"]]
    if "razao" in seletor:
        a, b = seletor["razao"]
        return float(ja[a]) / float(ja[b])
    raise SystemExit(f"ERRO: seletor desconhecido {seletor}")


def arquivo_do_seletor(seletor: dict) -> str | None:
    for k in ("json", "json_lista", "csv", "texto"):
        if k in seletor:
            return seletor[k]
    return None


def registrar_numeros(calculados: dict) -> dict:
    blocos = {}
    for nome, lista in (("numeros", NUMEROS), ("failure_mode", NUMEROS_FM), ("texto_citado", NUMEROS_TEXTO)):
        brutos: dict[str, object] = {}
        saida = {}
        for cod, nat, sel, formato, desc in lista:
            if cod in saida:
                raise SystemExit(f"ERRO: código repetido {cod}")
            bruto = resolver(sel, calculados, brutos)
            brutos[cod] = bruto
            saida[cod] = {"valor": fmt(bruto, formato), "valor_bruto": bruto, "natureza": nat,
                          "arquivo": arquivo_do_seletor(sel) or "calculado por este script", "seletor": sel,
                          "formato": formato, "descricao": desc}
        blocos[nome] = saida
    todos = [c for b in blocos.values() for c in b]
    if len(todos) != len(set(todos)):
        raise SystemExit("ERRO: código repetido entre blocos")
    return blocos


# --------------------------------------------------------------------------
# Figura da regra (variante A colorida, função do relatório)
# --------------------------------------------------------------------------


def _galeria():
    spec = importlib.util.spec_from_file_location("galeria_regra_10", GALERIA)
    g = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g)
    return g


def _localizar_chrome(g) -> str | None:
    return g.R.localizar_chrome()


def svg_para_png(svg: str, destino: Path, largura: int, altura: int, chrome: str | None) -> bool:
    """Rasteriza o SVG com o Chromium headless (escala 2). Sem Chromium, não gera PNG."""
    if not chrome:
        return False
    html = ("<!DOCTYPE html><html><head><meta charset='utf-8'><style>html,body{margin:0;background:#fff}"
            f"svg{{width:{largura}px;height:{altura}px;display:block}}</style></head><body>{svg}</body></html>")
    with tempfile.TemporaryDirectory(prefix="banca2_svg_") as tmp:
        pag = Path(tmp) / "f.html"
        pag.write_text(html, encoding="utf-8")
        if destino.exists():
            destino.unlink()
        bruto = Path(tmp) / "bruto.png"
        # A janela do headless tem viewport menor que o window-size: renderiza numa janela mais alta e recorta
        # a caixa do SVG (escala 2).
        cmd = [chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
               f"--user-data-dir={Path(tmp) / 'perfil'}", "--force-device-scale-factor=2",
               f"--window-size={largura},{altura + 400}", f"--screenshot={bruto}", pag.as_uri()]
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if not bruto.exists() or bruto.stat().st_size == 0:
            return False
        from PIL import Image
        with Image.open(bruto) as im:
            im.crop((0, 0, 2 * largura, 2 * altura)).save(destino, optimize=False)
    return destino.exists() and destino.stat().st_size > 0


def figuras_regra(g) -> tuple[list[dict], dict]:
    d = g.dados()
    s_of = d["ivs"].to_numpy(float)
    s_er = d["ivs_local"].to_numpy(float)
    nivel = d["nivel"].to_numpy(int)
    err_of = np.array([g.faixa_regra(v) != f for v, f in zip(s_of, d["faixa_anunciada"])])
    err_er = np.array([g.faixa_regra(v) != f for v, f in zip(s_er, d["faixa_anunciada"])])
    n = len(d)
    n_r1 = _ler_json("output/rdd_bolsa/portao_r1_ivs_oficial.json")["populacoes"]["P1"]["municipios"]
    if n != n_r1:
        raise SystemExit(f"ERRO: figura da regra com {n} municípios; o portão R1 registra {n_r1}")
    if err_of.any():
        raise SystemExit(f"ERRO: {int(err_of.sum())} municípios do lado errado com o IVS oficial; o R1 diz 0")
    chrome = _localizar_chrome(g)
    W, H = 680, 262  # viewBox de fig_regra_pontos
    figs = []
    SAIDA.mkdir(parents=True, exist_ok=True)
    SAIDA_FM.mkdir(parents=True, exist_ok=True)
    svg_of = g.var_pontos_cor(s_of, nivel, err_of, "IVS 2010 oficial do município (Ipea)")
    p_of = SAIDA / "regra_bolsa_ivs_oficial.svg"
    p_of.write_text(svg_of + "\n", encoding="utf-8")
    figs.append({"arquivo": p_of, "natureza": "EMPIRICO",
                 "descricao": "bolsa anunciada contra o IVS 2010 oficial, ciclo 1 (variante A colorida, doc 38 D1)",
                 "fontes": [MATRIZ, IVS_OFICIAL]})
    png_of = SAIDA / "regra_bolsa_ivs_oficial.png"
    if svg_para_png(svg_of, png_of, W * 2, H * 2, chrome):
        figs.append({"arquivo": png_of, "natureza": "EMPIRICO", "descricao": "rasterização do SVG acima",
                     "fontes": [MATRIZ, IVS_OFICIAL]})
    svg_er = g.var_pontos_cor(s_er, nivel, err_er,
                              "FAILURE MODE: arquivo de IVS errado do repositório, não é o IVS do município")
    p_er = SAIDA_FM / "regra_bolsa_arquivo_errado_FAILURE_MODE.svg"
    p_er.write_text(svg_er + "\n", encoding="utf-8")
    figs.append({"arquivo": p_er, "natureza": "FAILURE_MODE",
                 "descricao": "a mesma figura com o arquivo errado no eixo; só documenta o failure mode (auditoria 16)",
                 "fontes": [MATRIZ, IVS_ARQUIVO_ERRADO]})
    png_er = SAIDA_FM / "regra_bolsa_arquivo_errado_FAILURE_MODE.png"
    if svg_para_png(svg_er, png_er, W * 2, H * 2, chrome):
        figs.append({"arquivo": png_er, "natureza": "FAILURE_MODE", "descricao": "rasterização do SVG acima",
                     "fontes": [MATRIZ, IVS_ARQUIVO_ERRADO]})
    calc = {"municipios_ciclo1": n, "lado_errado_oficial": int(err_of.sum()),
            "lado_errado_arquivo_errado": int(err_er.sum()), "png_gerado": bool(chrome)}
    return figs, calc


# --------------------------------------------------------------------------
# Figuras da cadeia (forest com escala por linha)
# --------------------------------------------------------------------------

LINHAS_PRINCIPAIS = [  # (outcome_id, populacao, ciclo): um outcome por elo, na ordem da cadeia
    ("F0.2", "U", "1"),
    ("P1", "V1+V2+V3", "1+2+3"),
    ("F1.3", "V1+V2+V3", "1+2+3"),
    ("E9", "candidatos de 1ª opção", "2"),
    ("E9", "candidatos de 1ª opção", "1+2+3"),
    ("F2.1", "V1+V2", "1+2"),
    ("F3.1", "U", POS),
    ("F4.2", "V1+V2+V3", "1+2+3"),
]

FORMATO_UNIDADE = {  # unidade de E8_tabela_sintese -> (formato, sufixo)
    "fracao (x100 = p.p.)": ("pp1s", " p.p."),
    "desvios-padrao (indice)": ("d2s", " DP"),
    "razão de chances": ("d2", ""),
}


def _fmt_linha(r: pd.Series, v: float) -> str:
    formato, suf = FORMATO_UNIDADE.get(r["unidade"], ("d3s", ""))
    if r["unidade"].startswith("horas"):
        formato = "d1s"
    return fmt(v, formato), suf


def nulo(r: pd.Series) -> float:
    return 1.0 if r["unidade"] == "razão de chances" else 0.0


def exclui_nulo(est: float, inf: float, sup: float, valor_nulo: float) -> bool:
    return inf > valor_nulo or sup < valor_nulo


def limites_simetricos(inf: float, sup: float, valor_nulo: float, log: bool, folga: float = 1.15) -> tuple[float, float]:
    """Eixo simétrico em torno do nulo, que contém o IC inteiro (em log para razão de chances)."""
    if log:
        a = max(abs(math.log(inf)), abs(math.log(sup))) * folga
        return math.exp(-a), math.exp(a)
    a = max(abs(inf - valor_nulo), abs(sup - valor_nulo)) * folga
    return valor_nulo - a, valor_nulo + a


def _rotulo_curto(r: pd.Series) -> str:
    o = re.sub(r"^(P2 )?", "", r["outcome"])
    if r["outcome_id"] == "E9":
        o = "E9 escolha da 1ª opção (razão de chances)"
    return o


def _leitura_curta(r: pd.Series) -> str:
    lt = r["leitura"]
    if r["p_holm"] != "":
        return f"primária; p Holm {fmt(float(r['p_holm']), 'p3')}"
    if "frágil" in lt:
        return "frágil: placebos, spline cúbico, sem o ciclo 2"
    if "robusto" in lt:
        return "robusto a poucos clusters e placebos; spline cúbico contém 1"
    if r["q_bky"] != "":
        return f"q BKY {fmt(float(r['q_bky']), 'd3')}"
    return ""


def _contraste_curto(c: str) -> str:
    if c.startswith("DiRD"):
        return "DiRD no CNES"
    if c.startswith("degrau"):
        return "escolha entre células"
    return "RDD em nível (pacote)"


def figura_cadeia(tab: pd.DataFrame, destino: Path, titulo: str) -> list[dict]:
    n = len(tab)
    alt_linha = 0.62
    fig = plt.figure(figsize=(11.5, 1.15 + alt_linha * n))
    topo = 1 - 0.75 / (1.15 + alt_linha * n)
    base = 0.45 / (1.15 + alt_linha * n)
    passo = (topo - base) / n
    fig.text(0.01, 1 - 0.18 / (1.15 + alt_linha * n), titulo, fontsize=12.5, color=TINTA, va="top", weight="bold")
    fig.text(0.01, 1 - 0.48 / (1.15 + alt_linha * n),
             "Cada linha tem a sua escala, simétrica em torno do nulo (0; 1 na razão de chances, em escala log). "
             "Leia a posição do IC em relação ao nulo, não o tamanho entre linhas.",
             fontsize=8.8, color=TINTA2, va="top")
    registro = []
    elo_anterior = None
    for i, (_, r) in enumerate(tab.iterrows()):
        y0 = topo - (i + 1) * passo
        est, inf, sup = float(r["estimativa"]), float(r["ic95_inf"]), float(r["ic95_sup"])
        v0 = nulo(r)
        log = v0 == 1.0
        excl = exclui_nulo(est, inf, sup, v0)
        if r["elo"] != elo_anterior:
            fig.text(0.01, y0 + passo * 0.80, r["elo"].upper(), fontsize=7.6, color=MUDO, weight="bold")
            elo_anterior = r["elo"]
        fig.text(0.01, y0 + passo * 0.42, _rotulo_curto(r), fontsize=9.2, color=TINTA, va="center")
        fig.text(0.01, y0 + passo * 0.12, f"{r['populacao']} · ciclo {r['ciclo']} · {_contraste_curto(r['contraste'])}",
                 fontsize=7.6, color=TINTA2, va="center")
        ax = fig.add_axes([0.43, y0 + passo * 0.18, 0.27, passo * 0.55])
        lo, hi = limites_simetricos(inf, sup, v0, log)
        if log:
            ax.set_xscale("log")
        ax.set_xlim(lo, hi)
        ax.set_ylim(-1, 1)
        ax.axvline(v0, color=EIXO, lw=1.2, zorder=1)
        cor = AZUL if excl else MUDO
        ax.plot([inf, sup], [0, 0], color=cor, lw=2.2, solid_capstyle="round", zorder=2)
        ax.plot([est], [0], "o", ms=8, color=cor, mec="white", mew=1.6, zorder=3)
        ax.set_yticks([])
        ax.set_xticks([v0])
        ax.set_xticklabels(["1" if log else "0"], fontsize=7.5, color=MUDO)
        ax.minorticks_off()
        ax.tick_params(axis="x", length=0, pad=1)
        for lado in ("top", "right", "left", "bottom"):
            ax.spines[lado].set_visible(False)
        t_est, suf = _fmt_linha(r, est)
        t_inf, _ = _fmt_linha(r, inf)
        t_sup, _ = _fmt_linha(r, sup)
        fig.text(0.72, y0 + passo * 0.42, f"{t_est}{suf} [{t_inf}; {t_sup}]", fontsize=9.2, color=TINTA, va="center")
        fig.text(0.72, y0 + passo * 0.12, _leitura_curta(r), fontsize=7.6, color=TINTA2, va="center")
        registro.append({"outcome": r["outcome"], "populacao": r["populacao"], "ciclo": r["ciclo"],
                         "texto": f"{t_est}{suf} [{t_inf}; {t_sup}]", "exclui_nulo": bool(excl)})
    fig.text(0.01, 0.12 / (1.15 + alt_linha * n),
             "EMPIRICO. Fonte: output/rdd_bolsa/E8_tabela_sintese.csv (síntese E8, protocolo 40). Azul: IC 95% "
             "exclui o nulo; cinza: contém. Gerado por scripts/apresentacao/gerar_figuras_banca2.py.",
             fontsize=7.6, color=MUDO)
    fig.savefig(destino, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    return registro


def figura_descarte(resumo: dict, destino: Path) -> list[dict]:
    ref = float(resumo["descarte"]["referencias"]["preenchimento_pp"])
    linhas = []
    for a in resumo["descarte"]["ancora_E3_ciclo1"]:
        linhas.append((f"E3, ciclo 1, corte {a['corte'].replace('.', ',')}", "F1.3 · V1", a))
    ordem = [("F1.3", "V1"), ("F1.3", "V2"), ("F1.3", "V3"), ("F1.3", "V1+V2+V3"),
             ("F1.4", "V1"), ("F1.4", "V2"), ("F1.4", "V1+V2")]
    pre = {(r["outcome_id"], r["populacao"]): r for r in resumo["descarte"]["preenchimento"]}
    nomes = {"F1.3": "preenchidas na 1ª chamada", "F1.4": "preenchidas até a 2ª chamada"}
    for oid, pop in ordem:
        r = pre[(oid, pop)]
        emp = "+" in pop
        rot = f"{oid} {nomes[oid]}, " + (f"ciclos {r['ciclo']} empilhados" if emp else f"ciclo {r['ciclo']}")
        linhas.append((rot, f"{pop} · cortes empilhados", r))
    honesto_nenhum = all(not r["ic_honesto_exclui_referencia"] for r in resumo["descarte"]["preenchimento"])
    if not honesto_nenhum:
        raise SystemExit("ERRO: algum IC honesto exclui a referência; a nota da figura não vale")
    n = len(linhas)
    fig, ax = plt.subplots(figsize=(11.5, 1.1 + 0.48 * n))
    fig.subplots_adjust(left=0.34, right=0.74, top=1 - 0.95 / (0.9 + 0.48 * n), bottom=0.9 / (0.9 + 0.48 * n))
    registro = []
    for i, (rot, sub, r) in enumerate(linhas):
        y = n - 1 - i
        tau, inf, sup = 100 * r["tau"], 100 * r["ic95_inf"], 100 * r["ic95_sup"]
        descarta = r["ic95_sup"] < ref
        cor = AZUL if descarta else MUDO
        ax.plot([inf, sup], [y, y], color=cor, lw=2.4, solid_capstyle="round", zorder=2)
        ax.plot([tau], [y], "o", ms=8, color=cor, mec="white", mew=1.6, zorder=3)
        ax.text(-0.02, y + 0.12, rot, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=9.2,
                color=TINTA)
        ax.text(-0.02, y - 0.25, sub, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=7.6,
                color=TINTA2)
        txt = f"{fmt(r['tau'], 'pp1s')} [{fmt(r['ic95_inf'], 'pp1s')}; {fmt(r['ic95_sup'], 'pp1s')}]"
        ax.text(1.02, y + 0.12, txt, transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=9.2,
                color=TINTA)
        if not descarta:
            leit = "não descarta +10 p.p."
        elif r.get("todas_convencionais_excluem_referencia"):
            leit = "descarta +10 p.p. em todas as convencionais"
        else:
            leit = "descarta +10 p.p. só na principal"
        ax.text(1.02, y - 0.25, leit,
                transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=7.6, color=TINTA2)
        registro.append({"linha": rot, "texto": txt, "descarta_referencia": bool(descarta), "leitura": leit})
    ax.axvline(0, color=EIXO, lw=1.2, zorder=1)
    ax.axvline(100 * ref, color=LARANJA, lw=1.4, ls=(0, (4, 3)), zorder=1)
    ax.text(100 * ref, n - 0.35, " referência do protocolo: +10 p.p.", color=TINTA2, fontsize=8, va="bottom",
            ha="left")
    ax.set_ylim(-0.7, n - 0.2)
    ax.set_yticks([])
    ax.set_xlabel("salto no preenchimento (p.p.), lado de bolsa maior menos lado de bolsa menor", fontsize=9,
                  color=TINTA2)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: "0" if abs(v) < 1e-9 else f"{v:+.0f}".replace("-", MENOS)))
    ax.tick_params(axis="x", colors=TINTA2, labelsize=8.5, length=0)
    ax.grid(axis="x", color=GRADE, lw=0.8)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(EIXO)
    fig.text(0.01, 1 - 0.18 / (0.9 + 0.48 * n), "Preenchimento: o que o IC 95% convencional descarta",
             fontsize=12.5, color=TINTA, weight="bold", va="top")
    fig.text(0.01, 1 - 0.46 / (0.9 + 0.48 * n),
             "Azul: o limite superior fica abaixo de +10 p.p. Vale só com IC convencional, aproximação local linear "
             "e para o pacote do corte.\nO IC honesto (M do protocolo) não descarta +10 p.p. em nenhuma linha.",
             fontsize=8.8, color=TINTA2, va="top")
    fig.text(0.01, 0.1 / (0.9 + 0.48 * n),
             "EMPIRICO. Fonte: output/rdd_bolsa/E8_resumo.json (descarte). Gerado por "
             "scripts/apresentacao/gerar_figuras_banca2.py.", fontsize=7.6, color=MUDO)
    fig.savefig(destino, dpi=170, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    return registro


# --------------------------------------------------------------------------
# Manifesto, registro e doc
# --------------------------------------------------------------------------

ENTRADAS = [
    (E8_RESUMO, "síntese E8 (Holm, descarte, E9, E7, seleção, famílias, degrau)", "2026-10-19",
     "RDD da bolsa, ciclos 1-3 e CNES 2022-01..2026-08", "várias (ver chaves)", "chaves JSON"),
    (E8_TABELA, "tabela-síntese por elo (figuras da cadeia e números)", "2026-10-19",
     "23 linhas principais, h = 0,050, cortes empilhados", "por linha (coluna unidade)",
     "outcome_id + populacao + ciclo"),
    (E3_EST, "E3: municípios por lado na âncora do ciclo 1", "2026-10-14", "P1 (ciclo 1), cortes 0,300 e 0,400",
     "municípios", "populacao + outcome + corte + especificacao"),
    (PORTAO_R1, "portão R1 com o IVS oficial (regra)", "2026-10-14", "ciclos 1, 2 e 3", "municípios", "populacoes"),
    (IDENT_LOCAL, "mecanismo do arquivo errado, só failure mode", "2026-10-14", "5.565 municípios (malha 2010)",
     "municípios", "mecanismo"),
    (FM_RESUMO, "registro do failure mode (auditoria 19)", "2026-10-18", "5.565 municípios", "municípios",
     "arquivo_errado"),
    (MATRIZ, "faixa anunciada por município (figura da regra)", "2026-10-14", "quadro c1_ch1, 368 municípios",
     "município", "co_ibge; filtro quadro == c1_ch1"),
    (IVS_OFICIAL, "running variable: IVS 2010 oficial (a08)", "2010 (base Ipea de 28/02/2024)",
     "5.565 municípios", "índice 0-1", "co_ibge"),
    (IVS_ARQUIVO_ERRADO, "SÓ FAILURE MODE: eixo da figura 2 e contagem do lado errado", "desconhecida (sem fonte)",
     "5.565 municípios", "linha de subgrupo, não IVS do município", "cod_ibge6"),
    (AUD18, "parâmetros normativos citados (co-políticas)", "2026-10-18", "atos federais com corte em IVS",
     "texto", "trechos por regex"),
    (GALERIA, "código da variante A colorida (fig_regra_pontos)", "-", "-", "-", "-"),
]


def _rel(p: Path) -> str:
    return str(p.relative_to(RAIZ))


def bloco_doc(numeros: dict) -> str:
    linhas = ["| Código | Valor exibido | Natureza | Arquivo | Seletor | Formato | Descrição |",
              "|---|---|---|---|---|---|---|"]
    for bloco in ("numeros", "failure_mode", "texto_citado"):
        for cod, e in numeros[bloco].items():
            sel = {k: v for k, v in e["seletor"].items() if k not in ("json", "json_lista", "csv", "texto")}
            sel_txt = json.dumps(sel, ensure_ascii=False).replace("|", "\\|")
            arq = e["arquivo"]
            arq_txt = f"`{arq}`" if "/" in arq else arq
            linhas.append(f"| `{cod}` | {e['valor']} | {e['natureza']} | {arq_txt} | `{sel_txt}` | "
                          f"`{e['formato']}` | {e['descricao']} |")
    return "\n".join(linhas)


MARCA_INI = "<!-- banca2:numeros:inicio -->"
MARCA_FIM = "<!-- banca2:numeros:fim -->"


def atualizar_doc(numeros: dict) -> None:
    texto = DOC03.read_text(encoding="utf-8")
    if MARCA_INI not in texto or MARCA_FIM not in texto:
        raise SystemExit(f"ERRO: marcadores do bloco ausentes em {_rel(DOC03)}")
    ini = texto.index(MARCA_INI) + len(MARCA_INI)
    fim = texto.index(MARCA_FIM)
    DOC03.write_text(texto[:ini] + "\n" + bloco_doc(numeros) + "\n" + texto[fim:], encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--atualizar-doc", action="store_true",
                    help="só regrava o bloco de números do doc 03 a partir de numeros_banca2.json")
    args = ap.parse_args()
    if args.atualizar_doc:
        atualizar_doc(json.loads((SAIDA / "numeros_banca2.json").read_text(encoding="utf-8")))
        print("bloco atualizado:", _rel(DOC03))
        return 0

    faltam = [p for p, *_ in ENTRADAS if not p.exists()]
    if faltam:
        raise SystemExit("ERRO: entradas ausentes: " + ", ".join(_rel(p) for p in faltam))
    resumo = _ler_json(_rel(E8_RESUMO))
    if resumo.get("natureza_dos_dados") != "EMPIRICO":
        raise SystemExit("ERRO: E8_resumo.json sem natureza EMPIRICO")
    tab = _ler_csv(_rel(E8_TABELA))
    if set(tab["natureza_dos_dados"]) != {"EMPIRICO"}:
        raise SystemExit("ERRO: E8_tabela_sintese.csv com linha não EMPIRICO")

    g = _galeria()
    figs, calc = figuras_regra(g)

    chave = ["outcome_id", "populacao", "ciclo"]
    sel = []
    for k in LINHAS_PRINCIPAIS:
        m = (tab[chave] == pd.Series(k, index=chave)).all(axis=1)
        if m.sum() != 1:
            raise SystemExit(f"ERRO: linha {k} achada {int(m.sum())} vezes na tabela-síntese")
        sel.append(tab[m])
    principal = pd.concat(sel)
    p_cad = SAIDA / "cadeia_sintese_principal.png"
    reg_principal = figura_cadeia(principal, p_cad, "A cadeia em uma figura: um outcome por elo")
    figs.append({"arquivo": p_cad, "natureza": "EMPIRICO",
                 "descricao": "um outcome por elo da cadeia (forest com escala por linha)", "fontes": [E8_TABELA]})
    tab_ord = tab.assign(_o=tab["ordem"].astype(int)).sort_values("_o").drop(columns="_o")
    p_comp = SAIDA / "cadeia_sintese_completa.png"
    reg_completa = figura_cadeia(tab_ord, p_comp, "Tabela-síntese do E8: as 23 linhas principais")
    figs.append({"arquivo": p_comp, "natureza": "EMPIRICO", "descricao": "as 23 linhas da tabela-síntese do E8",
                 "fontes": [E8_TABELA]})
    p_desc = SAIDA / "descarte_preenchimento.png"
    reg_desc = figura_descarte(resumo, p_desc)
    figs.append({"arquivo": p_desc, "natureza": "EMPIRICO",
                 "descricao": "IC convencional do preenchimento contra a referência de +10 p.p.",
                 "fontes": [E8_RESUMO]})

    numeros = registrar_numeros(calc)
    numeros_doc = {"natureza_dos_dados": "EMPIRICO",
                   "nota": "blocos separados: 'numeros' (EMPIRICO), 'failure_mode' (só documenta o arquivo errado) "
                           "e 'texto_citado' (atos normativos e literatura, extraídos do texto-fonte)",
                   "script": "scripts/apresentacao/gerar_figuras_banca2.py", **numeros}
    (SAIDA / "numeros_banca2.json").write_text(json.dumps(numeros_doc, ensure_ascii=False, indent=2) + "\n",
                                               encoding="utf-8")
    manifesto = {
        "natureza_dos_dados": "EMPIRICO",
        "script": "scripts/apresentacao/gerar_figuras_banca2.py",
        "regra": "nenhuma estimação; figuras e números lidos de output/; o arquivo errado só entra na figura e "
                 "na contagem do failure mode, separadas em failure_mode/",
        "entradas": [{"caminho": _rel(p), "sha256": sha256(p), "papel": papel, "data_referencia": dr,
                      "cobertura": cob, "unidade": un, "chaves": ch} for p, papel, dr, cob, un, ch in ENTRADAS],
        "regra_bolsa": calc,
        "cadeia_sintese_principal": reg_principal,
        "cadeia_sintese_completa": reg_completa,
        "descarte_preenchimento": reg_desc,
        "figuras": [{"arquivo": _rel(f["arquivo"]), "sha256": sha256(f["arquivo"]), "natureza": f["natureza"],
                     "descricao": f["descricao"], "fontes": [_rel(p) for p in f["fontes"]]} for f in figs],
        "numeros": {"arquivo": "output/apresentacao_banca2/numeros_banca2.json",
                    "sha256": sha256(SAIDA / "numeros_banca2.json")},
    }
    (SAIDA / "manifesto_figuras.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")
    if DOC03.exists() and MARCA_INI in DOC03.read_text(encoding="utf-8"):
        atualizar_doc(numeros)
    for f in figs:
        print("gerado:", _rel(f["arquivo"]), f"({f['natureza']})")
    print("números:", sum(len(numeros[b]) for b in numeros), "códigos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
