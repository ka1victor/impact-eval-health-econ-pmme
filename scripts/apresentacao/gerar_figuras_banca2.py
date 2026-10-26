"""Gera as figuras, as tabelas e o registro de números da apresentação da banca 2 (28/10 e 04/11/2026).

Saída: output/apresentacao_banca2/

Não estima nada. Lê saídas já gravadas pela cadeia da RDD da bolsa (E3 a E9, síntese E8), pelos blocos das
perguntas reformuladas (síntese do doc 57: N, A3, P1, P4, P6, K, realocação; protocolo 59: Rambachan–Roth e
comparação alternativa) e pelos portões da regra, e as redesenha para slide. O conteúdo canônico está em
`docs/07_apresentacoes/banca2/`; este script só produz o que ali é exibido. O deck é montado à parte, por
`scripts/apresentacao/gerar_deck_banca2.py`.

Figuras e tabelas
-----------------
1. `regra_bolsa_ivs_oficial.svg` (e `.png`, se houver Chromium) — bolsa anunciada contra o IVS 2010 oficial,
   ciclo 1, um ponto por município; variante A colorida (doc 38, D1), desenhada por `fig_regra_pontos` via
   `scripts/rdd_bolsa/10_galeria_figura_regra.py`. Os dados são lidos aqui (`dados_regra`), só com o IVS oficial.
2. `h1_preenchimento.png`, `h2_escolha.png`, `h4_horas_medico.png` — uma linha por estimativa, com rótulo em
   português, o nulo marcado e o bloco "Como ler" na própria imagem (lição do grupo: gráficos de RDD sem
   explicação ficaram incompreensíveis).
3. `cadeia_resumo_doc57.png` — as linhas do doc 57 (N1, A3, P1 M1, P4, P6, K1, realocação) e a da H3 (P1h,
   D_UF), cada uma na sua escala, com a força da evidência dada por regra (`forca_da_linha`).
   A figura da H3 não é desenhada aqui: o slide usa `output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png`, gravada
   pelo script 25c e auditada (auditoria 31); este script só confere o SHA-256 dela contra `P1h_resumo.json`.
4. `tabela_descritiva_ciclos.{csv,png}` e `tabela_fontes.{csv,png}` — descritivas por ciclo (contadas aqui do
   quadro de células e do portão G1, faixa pela grade aplicada) e tabela de fontes.
5. `cadeia_sintese_principal.png`, `cadeia_sintese_completa.png`, `descarte_preenchimento.png` — figuras do
   rascunho de 19/10 (síntese E8), mantidas.
6. `failure_mode/regra_bolsa_arquivo_errado_FAILURE_MODE.{svg,png}` — **não regeneradas**: refazê-las exigiria
   ler o arquivo de IVS errado. Entram no manifesto com o hash atual e natureza FAILURE_MODE.

Números
-------
`numeros_banca2.json` traz cada número exibido nos slides com o arquivo e a chave de onde vem e o formato.
Nenhum valor é digitado aqui: as listas NUMEROS e NUMEROS_NOVOS só declaram seletores (`json`, `json_lista`,
`csv`, `texto`, `descritiva`, com `transf` opcional). Os números de texto citado (atos normativos e literatura)
são extraídos por expressão regular do arquivo-fonte; se o trecho não existir, o script para. Os números do
failure mode ficam num bloco separado. Os números da H3 (protocolo 52b) são lidos de `P1h_magnitudes.csv` e
`P1h_resumo.json`, já auditados; nada da H3 é calculado aqui.

Com `--atualizar-doc`, regrava o bloco `banca2:numeros` de
`docs/07_apresentacoes/banca2/03_proveniencia_figuras_e_numeros.md` a partir do JSON.

Regras de integridade: nada é lido de `data/`; nada é simulado, imputado ou digitado; o script para se uma
conferência falhar (por exemplo, se algum município ficar do lado errado do corte com o IVS oficial, ou se a
faixa publicada divergir da grade aplicada numa célula com IVS).
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
AUD18 = RAIZ / "docs" / "auditorias" / "18_politicas_nos_mesmos_cortes_ivs.md"
# Entradas da parte nova (26/10/2026): plano da banca 2, §3 a §5
S57 = "output/rdd_bolsa/S57_resumo.json"
N_EST = "output/rdd_bolsa/N_estimativas.csv"
P1_EST = "output/rdd_bolsa/P1_estimativas.csv"
H_EST = "output/rdd_bolsa/H_estimativas.csv"
CA_EST = "output/rdd_bolsa/CA_estimativas.csv"
G1_RES = "output/rdd_bolsa/G1_resumo.json"
A16_MAN = "output/aquisicao/cnes_profissional/a16_manifesto_cnes_profissional.json"
CELULAS = RAIZ / "output" / "rdd_bolsa" / "outcomes" / "outcomes_V_celula.parquet"
POP2022 = RAIZ / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
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
# Números da entrega empírica de 26/10/2026 (plano da banca 2, §3 a §5)
# --------------------------------------------------------------------------
# Lidos da síntese vigente (doc 57, `S57_resumo.json`, chave "v": cada valor já traz o arquivo e o seletor de
# origem) e dos CSVs de estimativas dos blocos (N, P1, P4/H, CA). As descritivas por ciclo são contadas aqui, do
# quadro de células (`outcomes_V_celula.parquet`) e do resumo do portão G1. A H3 (protocolo 52b, doc 57i) é lida
# de `P1h_magnitudes.csv` e `P1h_resumo.json` (auditoria 31), sem recálculo.

def _v(chave: str) -> dict:
    return _j(S57, "v", chave, "v")


def _c(arquivo: str, filtro: dict, coluna: str, transf: list | None = None) -> dict:
    s = {"csv": arquivo, "filtro": filtro, "coluna": coluna}
    if transf:
        s["transf"] = transf
    return s


def _d(chave: str) -> dict:
    return {"descritiva": chave}


N1F = {"outcome_id": "N1", "populacao": "V1+V2+V3", "corte": "empilhado"}
RC5 = [["mul", 5], ["exp"]]  # razão de chances por +R$ 5 mil a partir do coeficiente por R$ 1 mil


def _p1(modelo: str, ciclo: str, coluna: str, termo: str = "bolsa_mil", transf: list | None = None) -> dict:
    return _c(P1_EST, {"modelo": modelo, "ciclo": ciclo, "termo": termo}, coluna, transf)


def _h(id_linha: str, restricao: str, coluna: str, parametro: str | None = None) -> dict:
    f = {"id_linha": id_linha, "alvo": "media_pos", "restricao": restricao}
    if parametro is not None:
        f["parametro"] = parametro
    return _c(H_EST, f, coluna)


def _ca(outcome: str, estatistica: str, coluna: str) -> dict:
    return _c(CA_EST, {"id_linha": "P4-CA", "outcome": outcome, "estatistica": estatistica}, coluna)


P1H_CSV = "output/rdd_bolsa/P1h_magnitudes.csv"
P1H_RES = "output/rdd_bolsa/P1h_resumo.json"
P1H_FIG = "output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png"


def _p1h(filtro: dict, coluna: str) -> dict:
    return _c(P1H_CSV, filtro, coluna)


SENS_H3 = [("M2", "M2", "empilhado", "log da distância"), ("M4", "M4", "empilhado", "efeito fixo de UF da vaga"),
           ("M5C1", "M5", "1", "só o ciclo 1"), ("M5C2", "M5", "2", "só o ciclo 2"), ("M5C3", "M5", "3", "só o ciclo 3"),
           ("M7", "M7", "empilhado", "logit explodido, 1ª e 2ª opção")]


NUMEROS_NOVOS: list[tuple[str, str, dict, str, str]] = [
    # H1: probabilidade de a célula aberta ser preenchida na 1ª chamada (A3, p.p.), doc 49 §15 e doc 57 §4.2
    ("A3_EMP_TAU", "EMPIRICO", _v("a3p_todos_emp_tau"), "d1s", "A3 ciclos 1–3, cortes empilhados: salto (p.p.)"),
    ("A3_EMP_INF", "EMPIRICO", _v("a3p_todos_emp_lo"), "d1s", "A3 empilhado: IC 95% inferior"),
    ("A3_EMP_SUP", "EMPIRICO", _v("a3p_todos_emp_hi"), "d1s", "A3 empilhado: IC 95% superior (maior aumento compatível)"),
    ("A3_EMP_MDE", "EMPIRICO", _v("a3p_todos_emp_mde"), "d1", "A3 empilhado: MDE de 80% (p.p.)"),
    ("A3_EMP_MEDIA", "EMPIRICO", _v("a3p_todos_emp_media"), "d1", "A3 empilhado: média abaixo do corte (%)"),
    ("A3_EMP_P", "EMPIRICO", _v("a3p_todos_emp_p"), "p3", "A3 empilhado: p"),
    ("A3_300_TAU", "EMPIRICO", _v("a3p_todos_300_tau"), "d1s", "A3 ciclos 1–3, corte 0,300: salto (p.p.)"),
    ("A3_300_INF", "EMPIRICO", _v("a3p_todos_300_lo"), "d1s", "A3 0,300: IC inferior"),
    ("A3_300_SUP", "EMPIRICO", _v("a3p_todos_300_hi"), "d1s", "A3 0,300: IC superior"),
    ("A3_300_MDE", "EMPIRICO", _v("a3p_todos_300_mde"), "d1", "A3 0,300: MDE de 80%"),
    ("A3_400_TAU", "EMPIRICO", _v("a3p_todos_400_tau"), "d1s", "A3 ciclos 1–3, corte 0,400: salto (p.p.)"),
    ("A3_400_INF", "EMPIRICO", _v("a3p_todos_400_lo"), "d1s", "A3 0,400: IC inferior"),
    ("A3_400_SUP", "EMPIRICO", _v("a3p_todos_400_hi"), "d1s", "A3 0,400: IC superior"),
    ("A3_400_MDE", "EMPIRICO", _v("a3p_todos_400_mde"), "d1", "A3 0,400: MDE de 80%"),
    ("A3_300_MEDIA", "EMPIRICO", _v("a3p_todos_300_media"), "d1", "A3 0,300: média abaixo do corte (%)"),
    ("A3_400_MEDIA", "EMPIRICO", _v("a3p_todos_400_media"), "d1", "A3 0,400: média abaixo do corte (%)"),
    ("A3_C1_MEDIA", "EMPIRICO", _v("a3p_c1_emp_media"), "d1", "A3 ciclo 1: média abaixo do corte (%)"),
    ("A3_C1_TAU", "EMPIRICO", _v("a3p_c1_emp_tau"), "d1s", "A3 só ciclo 1, cortes empilhados: salto (p.p.)"),
    ("A3_C1_INF", "EMPIRICO", _v("a3p_c1_emp_lo"), "d1s", "A3 ciclo 1: IC inferior"),
    ("A3_C1_SUP", "EMPIRICO", _v("a3p_c1_emp_hi"), "d1s", "A3 ciclo 1: IC superior"),
    ("A3_C1_MDE", "EMPIRICO", _v("a3p_c1_emp_mde"), "d1", "A3 ciclo 1: MDE de 80%"),
    ("A3C_EMP_TAU", "EMPIRICO", _v("a3c_todos_emp_tau"), "d1s", "A3 célula com candidato de 1ª opção, empilhado (p.p.)"),
    ("A3C_EMP_INF", "EMPIRICO", _v("a3c_todos_emp_lo"), "d1s", "IC inferior"),
    ("A3C_EMP_SUP", "EMPIRICO", _v("a3c_todos_emp_hi"), "d1s", "IC superior"),
    # H1: número de vagas preenchidas por município (família N, protocolo 48), doc 49 §3
    ("N1_SA_TAU", "EMPIRICO", _v("n_N1_tau"), "d2s", "N1 com controle das vagas oferecidas (S-a): salto (vagas por município)"),
    ("N1_SA_INF", "EMPIRICO", _v("n_N1_lo"), "d2s", "N1 S-a: IC 95% inferior"),
    ("N1_SA_SUP", "EMPIRICO", _v("n_N1_hi"), "d2s", "N1 S-a: IC 95% superior"),
    ("N1_SA_P", "EMPIRICO", _v("n_N1_p"), "p3", "N1 S-a: p"),
    ("N1_SA_HOLM", "EMPIRICO", _v("n_N1_holm"), "p3", "N1 S-a: p de Holm (família N1–N4)"),
    ("N1_SA_MDE", "EMPIRICO", _v("n_N1_mde"), "d2", "N1 S-a: MDE de 80%"),
    ("N1_SB_TAU", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-b", "variante": "principal"}, "tau"), "d2s",
     "N1 sem controle (S-b, efeito total da faixa): salto"),
    ("N1_SB_INF", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-b", "variante": "principal"}, "ic95_inf"), "d2s",
     "N1 S-b: IC inferior"),
    ("N1_SB_SUP", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-b", "variante": "principal"}, "ic95_sup"), "d2s",
     "N1 S-b: IC superior"),
    ("N1_SB_P", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-b", "variante": "principal"}, "p_valor"), "p3",
     "N1 S-b: p"),
    ("N1_SB_MDE", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-b", "variante": "principal"}, "mde"), "d2",
     "N1 S-b: MDE de 80%"),
    ("N1_MEDIA", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-a", "variante": "principal"}, "media_abaixo"), "d2",
     "N1: média do lado de bolsa menor, na janela (vagas por município)"),
    ("N1_NABX", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-a", "variante": "principal"}, "n_abaixo"), "int",
     "N1: municípios abaixo do corte (h = 0,050, ciclos e cortes empilhados)"),
    ("N1_NACI", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-a", "variante": "principal"}, "n_acima"), "int",
     "N1: municípios acima do corte"),
    ("N1_UNICO_TAU", "EMPIRICO", _c(N_EST, {**N1F, "variante": "controle_coeficiente_unico"}, "tau"), "d2s",
     "N1 com um só coeficiente do controle (auditoria 20, fora do protocolo): salto"),
    ("N1_UNICO_INF", "EMPIRICO", _c(N_EST, {**N1F, "variante": "controle_coeficiente_unico"}, "ic95_inf"), "d2s",
     "IC inferior"),
    ("N1_UNICO_SUP", "EMPIRICO", _c(N_EST, {**N1F, "variante": "controle_coeficiente_unico"}, "ic95_sup"), "d2s",
     "IC superior"),
    ("N1_HON_INF", "EMPIRICO", _c(N_EST, {**N1F, "variante": "S-a: ic_honesto_M_x1"}, "ic95_inf"), "d2s",
     "N1 S-a: IC honesto (M do protocolo), inferior"),
    ("N1_HON_SUP", "EMPIRICO", _c(N_EST, {**N1F, "variante": "S-a: ic_honesto_M_x1"}, "ic95_sup"), "d2s",
     "N1 S-a: IC honesto, superior"),
    ("N1_H030_TAU", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-a", "variante": "h=0.030"}, "tau"), "d2s",
     "N1 S-a com h = 0,030"),
    ("N1_H080_TAU", "EMPIRICO", _c(N_EST, {**N1F, "especificacao": "S-a", "variante": "h=0.080"}, "tau"), "d2s",
     "N1 S-a com h = 0,080"),
    ("N1_DONUT_TAU", "EMPIRICO", _c(N_EST, {**N1F, "variante": "donut (S-a)"}, "tau"), "d2s", "N1 S-a sem os municípios colados ao corte (donut)"),
    ("N1_DONUT_INF", "EMPIRICO", _c(N_EST, {**N1F, "variante": "donut (S-a)"}, "ic95_inf"), "d2s", "IC inferior"),
    ("N1_DONUT_SUP", "EMPIRICO", _c(N_EST, {**N1F, "variante": "donut (S-a)"}, "ic95_sup"), "d2s", "IC superior"),
    *[(f"N{k}_SA_{s}", "EMPIRICO", _v(f"n_N{k}_{c}"), fm, f"N{k} S-a: {d}")
      for k in (2, 3, 4)
      for s, c, fm, d in (("TAU", "tau", "d2s", "salto"), ("INF", "lo", "d2s", "IC inferior"),
                          ("SUP", "hi", "d2s", "IC superior"), ("HOLM", "holm", "p3", "p de Holm"))],
    # H2: logit condicional da 1ª opção (P1, protocolo 52), doc 57a
    ("M1_COEF", "EMPIRICO", _v("m1_coef"), "d4s", "M1: coeficiente da bolsa por R$ 1 mil/mês"),
    ("M1_INF", "EMPIRICO", _v("m1_lo"), "d4s", "M1: IC 95% inferior"),
    ("M1_SUP", "EMPIRICO", _v("m1_hi"), "d4s", "M1: IC 95% superior"),
    ("M1_P", "EMPIRICO", _v("m1_p"), "p3", "M1: p (família de um teste; p de Holm = p)"),
    ("M1_RC", "EMPIRICO", _v("m1_rc"), "d2", "M1: razão de chances por +R$ 5 mil"),
    ("M1_RC_INF", "EMPIRICO", _v("m1_rc_lo"), "d2", "M1: razão de chances, IC inferior"),
    ("M1_RC_SUP", "EMPIRICO", _v("m1_rc_hi"), "d2", "M1: razão de chances, IC superior"),
    ("M1_RC_MDE", "EMPIRICO", _v("m1_rc_mde"), "d2", "M1: MDE de 80% em razão de chances"),
    ("M1_N", "EMPIRICO", _p1("M1", "empilhado", "n_candidatos"), "int", "M1: candidatos de 1ª opção na amostra P1"),
    *[(f"M5_C{c}_{s}", "EMPIRICO", _p1("M5", c, col, transf=t), fm, f"M5 ciclo {c}: {d}")
      for c in ("1", "2", "3")
      for s, col, t, fm, d in (("RC", "coef", RC5, "d2", "razão de chances por +R$ 5 mil"),
                               ("RCI", "ic95_inf", RC5, "d2", "IC inferior"),
                               ("RCS", "ic95_sup", RC5, "d2", "IC superior"),
                               ("P", "p", None, "p3", "p"),
                               ("COEF", "coef", None, "d4s", "coeficiente por R$ 1 mil"))],
    ("M5_WALD_P", "EMPIRICO", _c(P1_EST, {"modelo": "M5", "tipo_linha": "wald_igualdade_ciclos"}, "p"), "p3",
     "M5: Wald da igualdade do coeficiente da bolsa entre os ciclos, p"),
    *[(f"{m}_COEF", "EMPIRICO", _p1(m, "empilhado", "coef", termo=t), "d4s", f"{m}: coeficiente da bolsa ({d})")
      for m, t, d in (("M0", "bolsa_mil", "sem distância"), ("M2", "bolsa_mil", "log da distância"),
                      ("M4", "bolsa_mil", "efeito fixo de UF"), ("M7", "bolsa_mil", "logit explodido"),
                      ("M8", "media_bolsa_mil", "logit misto, média"), ("M9", "bolsa_mil", "logit aninhado"))],
    ("M7_INF", "EMPIRICO", _p1("M7", "empilhado", "ic95_inf"), "d4s", "M7: IC inferior"),
    ("M7_SUP", "EMPIRICO", _p1("M7", "empilhado", "ic95_sup"), "d4s", "M7: IC superior"),
    # H3: peso da bolsa contra o da UF de origem no M1 (P1h, protocolo 52b; doc 57i; auditoria 31)
    ("H3_ESTATUTO", "EMPIRICO", _j(P1H_RES, "estatuto"), "txt",
     "P1h: estatuto do bloco (pós-resultado; regra da força da evidência na figura da cadeia)"),
    ("H3_DUF", "EMPIRICO", _p1h({"id_linha": "P1h-1"}, "estimativa"), "d2",
     "P1h-1: D_UF = θ_UF − 10·β no M1 (log-chance; mesma UF, outra região de saúde, contra toda a amplitude da bolsa)"),
    ("H3_DUF_INF", "EMPIRICO", _p1h({"id_linha": "P1h-1"}, "ic95_inf"), "d2", "P1h-1: IC 95% inferior (cluster por conjunto)"),
    ("H3_DUF_SUP", "EMPIRICO", _p1h({"id_linha": "P1h-1"}, "ic95_sup"), "d2", "P1h-1: IC 95% superior"),
    ("H3_DUF_P", "EMPIRICO", _p1h({"id_linha": "P1h-1"}, "p_unilateral"), "p3", "P1h-1: p unilateral (H0: D_UF ≤ 0)"),
    ("H3_DUF_HOLM", "EMPIRICO", _p1h({"id_linha": "P1h-1"}, "p_holm"), "p3",
     "P1h-1: p de Holm (família de um teste; igual ao p unilateral)"),
    *[(f"H3_{k}{s}", "EMPIRICO", _p1h({"id_linha": lin}, col), "d0", f"{lin}: {d}{dd} (km, método delta)")
      for k, lin, d in (("K5", "P1h-2a", "K5, km a menos de distância com o peso de um degrau de R$ 5 mil (descritivo)"),
                        ("K10", "P1h-2b", "K10, km a menos de distância com o peso de toda a amplitude (descritivo)"))
      for s, col, dd in (("", "estimativa", ""), ("_INF", "ic95_inf", ", IC 95% inferior"),
                         ("_SUP", "ic95_sup", ", IC 95% superior"))],
    ("H3_K5_P", "EMPIRICO", _p1h({"id_linha": "P1h-2a"}, "p_unilateral"), "p3",
     "P1h-2a: p unilateral de K5 (descritivo; não substitui o teste bilateral do P1a)"),
    *[(f"H3_S_{k}", "EMPIRICO", _p1h({"id_linha": "P1h-3", "modelo": m, "ciclo": c}, "estimativa"), "d2",
       f"P1h-3: D_UF em {m} ({d}), sensibilidade com BKY")
      for k, m, c, d in SENS_H3],
    *[(f"H3_{k}{s}", "EMPIRICO", _p1h({"id_linha": "FIG", "componente": comp}, col), "d2", f"peso no M1: {d}{dd}")
      for k, comp, d in (("10B", "10β", "toda a amplitude da bolsa, 10·β"),
                         ("THETA", "θ_UF", "mesma UF, outra região de saúde, θ_UF"))
      for s, col, dd in (("", "estimativa", ""), ("_INF", "ic95_inf", ", IC 95% inferior"),
                         ("_SUP", "ic95_sup", ", IC 95% superior"))],
    # H4: horas do médico (P4, protocolo 54; doc 57d), Rambachan–Roth e comparação local (protocolo 59; doc 57h)
    *[(f"P4_{o}_{s}", "EMPIRICO", _v(f"p4_{o.lower()}_{c}"), fm, f"P4 {d}: {dd}")
      for o, d in (("HT", "horas totais"), ("HM", "horas no município do posto"), ("HF", "horas fora do município do posto"))
      for s, c, fm, dd in (("ATT", "att", "d1s", "média de θ(0..+6), h/sem"), ("INF", "lo", "d1s", "IC inferior"),
                           ("SUP", "hi", "d1s", "IC superior"), ("PRE", "pre", "p3", "p do Wald do pré"))],
    ("P4_ORIGEM", "EMPIRICO", _v("p4_origem"), "d1", "P4: médicos que já tinham vínculo no município do posto (%)"),
    ("P4_ORIGEM_INF", "EMPIRICO", _v("p4_origem_lo"), "d1", "IC inferior (%)"),
    ("P4_ORIGEM_SUP", "EMPIRICO", _v("p4_origem_hi"), "d1", "IC superior (%)"),
    ("RR_HT", "EMPIRICO", _h("H-P4-horas_totais", "RM_ruptura", "parametro"), "d2",
     "Rambachan–Roth, horas totais: ruptura de M̄ (Δ^RM, teste condicional)"),
    ("RR_HM", "EMPIRICO", _h("H-P4-horas_mun_posto", "RM_ruptura", "parametro"), "d2",
     "Rambachan–Roth, horas no município do posto: ruptura de M̄"),
    ("RR_HF", "EMPIRICO", _h("H-P4-horas_fora_mun_posto", "RM_ruptura", "parametro"), "d2",
     "Rambachan–Roth, horas fora do município do posto: ruptura de M̄"),
    ("RR_HT_M1_INF", "EMPIRICO", _h("H-P4-horas_totais", "RM", "ic_inf", "1"), "d2s",
     "Rambachan–Roth, horas totais, M̄ = 1: IC robusto inferior"),
    ("RR_HT_M1_SUP", "EMPIRICO", _h("H-P4-horas_totais", "RM", "ic_sup", "1"), "d2s",
     "Rambachan–Roth, horas totais, M̄ = 1: IC robusto superior"),
    *[(f"CA_{o}_{s}", "EMPIRICO", _ca(out, est, col), fm, f"P4-CA {d}: {dd}")
      for o, out, d in (("HT", "horas_totais", "horas totais"), ("HM", "horas_mun_1a", "horas no município da 1ª opção"),
                        ("HF", "horas_fora_1a", "horas fora do município da 1ª opção"))
      for s, est, col, fm, dd in (("EST", "efeito_pos_medio", "valor", "d2s", "efeito médio do pós (h/sem)"),
                                  ("INF", "efeito_pos_medio", "ic95_inf", "d2s", "IC inferior"),
                                  ("SUP", "efeito_pos_medio", "ic95_sup", "d2s", "IC superior"),
                                  ("HOLM", "efeito_pos_medio", "p_holm", "p3", "p de Holm"),
                                  ("PRE", "wald_pre", "p_valor", "p3", "p do pré (permutação)"))],
    # P6: alocado por pouco (protocolo 56; doc 57f)
    ("P6_ESTATUTO", "EMPIRICO", _j("output/rdd_bolsa/P6_resumo.json", "estatuto"), "txt",
     "P6: estatuto do bloco (regra da força da evidência na figura da cadeia)"),
    ("P6_Y1_EST", "EMPIRICO", _v("p6_y1_media_est"), "d3s", "P6 Y1 vínculo no município da vaga, média do seguimento"),
    ("P6_Y1_INF", "EMPIRICO", _v("p6_y1_media_lo"), "d3s", "P6 Y1: IC inferior"),
    ("P6_Y1_SUP", "EMPIRICO", _v("p6_y1_media_hi"), "d3s", "P6 Y1: IC superior"),
    ("P6_Y1_HOLM", "EMPIRICO", _v("p6_y1_media_holm"), "p3", "P6 Y1: p de Holm"),
    ("P6_Y3_EST", "EMPIRICO", _v("p6_y3_media_est"), "d1s", "P6 Y3 horas totais, média do seguimento (h/sem)"),
    ("P6_Y3_INF", "EMPIRICO", _v("p6_y3_media_lo"), "d1s", "P6 Y3: IC inferior"),
    ("P6_Y3_SUP", "EMPIRICO", _v("p6_y3_media_hi"), "d1s", "P6 Y3: IC superior"),
    ("P6_Y3_HOLM", "EMPIRICO", _v("p6_y3_media_holm"), "p3", "P6 Y3: p de Holm"),
    # P3 D1 (produção nos cortes, protocolo 47) e realocação (protocolo 58)
    ("K1_TAU", "EMPIRICO", _v("kd1_K1_tau"), "d2s", "K1 produção SUS nas CBO-alvo, DiRD nos cortes (por 10 mil hab./mês)"),
    ("K1_INF", "EMPIRICO", _v("kd1_K1_lo"), "d2s", "K1: IC inferior"),
    ("K1_SUP", "EMPIRICO", _v("kd1_K1_hi"), "d2s", "K1: IC superior"),
    ("K1_HOLM", "EMPIRICO", _v("kd1_K1_holm"), "p3", "K1: p de Holm (família K1–K3)"),
    ("R_P1_EST", "EMPIRICO", _v("R_P1_c5"), "d1s", "R-P1 célula preenchida por +R$ 5 mil na bolsa média das concorrentes (p.p.)"),
    ("R_P1_INF", "EMPIRICO", _v("R_P1_lo"), "d1s", "R-P1: IC inferior"),
    ("R_P1_SUP", "EMPIRICO", _v("R_P1_hi"), "d1s", "R-P1: IC superior"),
    ("R_P1_HOLM", "EMPIRICO", _v("R_P1_holm"), "p3", "R-P1: p de Holm"),
    ("R_P1_MDE", "EMPIRICO", _v("R_P1_mde"), "d1", "R-P1: MDE de 80% (p.p.)"),
    # Base de dados: descritivas por ciclo (contadas aqui do quadro de células e do G1) e cobertura das fontes
    *[(f"D_C{c}_{s}", "EMPIRICO", _d(f"C{c}_{s}"), fm, f"ciclo {c}: {d}")
      for c in (1, 2, 3)
      for s, fm, d in (("MUN", "int", "municípios com célula no quadro da 1ª chamada"),
                       ("CEL", "int", "células (estabelecimento × curso) no quadro da 1ª chamada"),
                       ("VI", "int", "vagas imediatas"), ("CR", "int", "vagas de cadastro reserva"),
                       ("CAND1", "int", "candidatos com 1ª opção numa célula do quadro"),
                       ("PRE1", "int", "células com alguma confirmação ou homologação na 1ª chamada"),
                       ("PRE1_PCT", "pct1", "fração de células preenchidas na 1ª chamada (%)"),
                       ("F3", "int", "municípios na faixa de R$ 10 mil (IVS até 0,300) pela grade aplicada"),
                       ("F2", "int", "municípios na faixa de R$ 15 mil (IVS de 0,301 a 0,400)"),
                       ("F1", "int", "municípios na faixa de R$ 20 mil (IVS acima de 0,400)"))],
    *[(f"D_C{c}_{s}", "EMPIRICO", _d(f"C{c}_{s}"), fm, f"ciclo {c}: {d}")
      for c in (1, 2)
      for s, fm, d in (("PRE2", "int", "células com alguma confirmação ou homologação até a 2ª chamada"),
                       ("PRE2_PCT", "pct1", "fração de células preenchidas até a 2ª chamada (%)"))],
    ("D_C3_SEM_IVS", "EMPIRICO", _d("C3_SEM_IVS"), "int", "ciclo 3: municípios com célula e sem IVS 2010 (criados depois de 2010)"),
    *[(f"D_C{c}_{s}", "EMPIRICO", _j(G1_RES, "taxas_ligacao", "g1_cpf_nome", str(c), k), "int", f"ciclo {c}: {d}")
      for c in (1, 2, 3)
      for s, k, d in (("CANDG1", "candidatos", "candidatos no portão G1"),
                      ("LIG", "ligados", "candidatos ligados a um profissional do CNES (G1)"))],
    *[(f"D_C{c}_P1", "EMPIRICO", _j("output/rdd_bolsa/P1_resumo.json", "amostra", "p1_por_ciclo", str(c)), "int",
       f"ciclo {c}: amostra da escolha (P1): 1ª opção numa célula, ligado ao CNES e com município de origem")
      for c in (1, 2, 3)],
    ("D_IVS_MUN", "EMPIRICO", _d("IVS_MUN"), "int", "municípios com IVS 2010 oficial (a08)"),
    ("D_POP_MUN", "EMPIRICO", _d("POP_MUN"), "int", "municípios com população do Censo 2022"),
    ("D_ATIVOS", "EMPIRICO", _j(A16_MAN, "listas_pmme", "registros_ativos_2026_09_11"), "int",
     "registros na lista de especialistas ativos do PMM-E de 11/09/2026"),
]


def descritivas() -> dict[str, float]:
    """Contagens por ciclo do quadro de células da 1ª chamada. A faixa é a da grade aplicada (cortes 0,300 e 0,400 no
    IVS 2010 oficial); o script para se ela divergir da faixa publicada em alguma célula com IVS."""
    d = pd.read_parquet(CELULAS)
    if set(d["natureza_dos_dados"]) != {"EMPIRICO"}:
        raise SystemExit("ERRO: outcomes_V_celula.parquet com linha não EMPIRICO")
    c0, c1 = CORTES
    tem = d["ivs_2010_oficial"].notna()
    regra = np.where(d["ivs_2010_oficial"] <= c0 + 1e-9, "FAIXA 3",
                     np.where(d["ivs_2010_oficial"] <= c1 + 1e-9, "FAIXA 2", "FAIXA 1"))
    if (regra[tem.to_numpy()] != d.loc[tem, "faixa_anunciada"].to_numpy()).any():
        raise SystemExit("ERRO: faixa publicada diverge da grade aplicada em alguma célula com IVS oficial")
    d = d.assign(faixa_regra=np.where(tem, regra, "SEM_IVS"))
    out: dict[str, float] = {}
    for c, g in d.groupby("ciclo"):
        out[f"C{c}_MUN"] = g["co_ibge"].nunique()
        out[f"C{c}_CEL"] = len(g)
        out[f"C{c}_VI"] = g["vagas_imediatas"].sum()
        out[f"C{c}_CR"] = g["vagas_cr"].sum()
        out[f"C{c}_CAND1"] = g["n_cand_1a_opcao"].sum()
        out[f"C{c}_PRE1"] = g["f1_3_preenchida_ch1"].sum()
        out[f"C{c}_PRE1_PCT"] = g["f1_3_preenchida_ch1"].mean()
        if g["f1_4_preenchida_ate_ch2"].notna().all():
            out[f"C{c}_PRE2"] = g["f1_4_preenchida_ate_ch2"].sum()
            out[f"C{c}_PRE2_PCT"] = g["f1_4_preenchida_ate_ch2"].mean()
        for f, k in (("FAIXA 3", "F3"), ("FAIXA 2", "F2"), ("FAIXA 1", "F1")):
            out[f"C{c}_{k}"] = g.loc[g["faixa_regra"] == f, "co_ibge"].nunique()
        out[f"C{c}_SEM_IVS"] = g.loc[g["faixa_regra"] == "SEM_IVS", "co_ibge"].nunique()
    out["IVS_MUN"] = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str})["ivs"].notna().sum()
    out["POP_MUN"] = len(pd.read_csv(POP2022, dtype=str))
    return {k: float(v) for k, v in out.items()}


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


def aplicar_transf(valor, transf: list) -> float:
    """Transformações declaradas no seletor: ["mul", k] multiplica; ["exp"] exponencia."""
    x = float(valor)
    for op in transf:
        if op[0] == "mul":
            x *= float(op[1])
        elif op[0] == "exp":
            x = math.exp(x)
        else:
            raise SystemExit(f"ERRO: transformação desconhecida {op}")
    return x


def resolver(seletor: dict, calculados: dict, ja: dict):
    """Devolve o valor bruto do seletor (com a transformação declarada, se houver)."""
    v = _resolver_bruto(seletor, calculados, ja)
    return aplicar_transf(v, seletor["transf"]) if "transf" in seletor else v


def _resolver_bruto(seletor: dict, calculados: dict, ja: dict):
    """Devolve o valor bruto do seletor. Para quando a chave não existe ou não é única."""
    if "descritiva" in seletor:
        return calculados["descritivas"][seletor["descritiva"]]
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
    if "descritiva" in seletor:
        chave = seletor["descritiva"]
        if chave == "IVS_MUN":
            return "output/aquisicao/a08_ivs_2010_oficial_municipio.csv"
        if chave == "POP_MUN":
            return "output/aquisicao/populacao_censo2022_municipios.csv"
        return "output/rdd_bolsa/outcomes/outcomes_V_celula.parquet"
    for k in ("json", "json_lista", "csv", "texto"):
        if k in seletor:
            return seletor[k]
    return None


def registrar_numeros(calculados: dict) -> dict:
    blocos = {}
    for nome, lista in (("numeros", NUMEROS + NUMEROS_NOVOS), ("failure_mode", NUMEROS_FM),
                        ("texto_citado", NUMEROS_TEXTO)):
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


def dados_regra(g) -> pd.DataFrame:
    """Ciclo 1 (quadro c1_ch1) com o IVS 2010 oficial. Não usa `g.dados()`, que também lê o arquivo errado."""
    m = pd.read_csv(MATRIZ, dtype={"co_ibge": str})
    d = m[m["quadro"] == "c1_ch1"].drop_duplicates("co_ibge")[["co_ibge", "faixa_anunciada"]]
    of = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str})[["co_ibge", "nome_municipio_uf", "ivs"]]
    d = d.merge(of, on="co_ibge")
    d["nivel"] = d["faixa_anunciada"].map({f: i for i, f in enumerate(g.FAIXAS)})
    return d.reset_index(drop=True)


def figuras_failure_mode() -> list[dict]:
    """As figuras do failure mode não são regeneradas: refazê-las exigiria ler o arquivo de IVS errado.

    Ficam como foram gravadas pela versão de 19/10/2026 deste script (commit bacabdc) e entram no manifesto
    com o hash atual, natureza FAILURE_MODE e a nota de que não foram refeitas.
    """
    figs = []
    for nome in ("regra_bolsa_arquivo_errado_FAILURE_MODE.svg", "regra_bolsa_arquivo_errado_FAILURE_MODE.png"):
        p = SAIDA_FM / nome
        if p.exists():
            figs.append({"arquivo": p, "natureza": "FAILURE_MODE",
                         "descricao": "a figura da regra com o arquivo de IVS errado no eixo; só documenta o failure mode "
                                      "(auditoria 16); gravada em 19/10/2026 (commit bacabdc) e não regenerada, para não "
                                      "ler o arquivo errado",
                         "fontes": [MATRIZ]})
    return figs


def figuras_regra(g) -> tuple[list[dict], dict]:
    d = dados_regra(g)
    s_of = d["ivs"].to_numpy(float)
    nivel = d["nivel"].to_numpy(int)
    err_of = np.array([g.faixa_regra(v) != f for v, f in zip(s_of, d["faixa_anunciada"])])
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
    figs += figuras_failure_mode()
    calc = {"municipios_ciclo1": n, "lado_errado_oficial": int(err_of.sum()), "png_gerado": bool(chrome)}
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
# Figuras da entrega de 26/10/2026: intervalos com "Como ler", cadeia do doc 57, tabelas
# --------------------------------------------------------------------------
# Lição do grupo: gráficos de RDD com faixas e pontos sem explicação ficaram incompreensíveis. Estas figuras
# trocam a nuvem de pontos por um intervalo por linha, com rótulo em português na própria linha, o nulo marcado
# e um bloco "Como ler" dentro da imagem. Todo número desenhado é o valor formatado de um código do registro.

VERDE_ESC = "#114719"
VERDE_DADO = "#0f7a3a"
CLARO_FUNDO = "#eef5ef"
LINHA_CLARA = "#c9ded1"
CINZA_DADO = "#8a8a84"
FONTE_FIG = "EMPIRICO · scripts/apresentacao/gerar_figuras_banca2.py"


class Registro:
    """Acumula o texto desenhado numa figura, para o manifesto e o teste de números."""

    def __init__(self) -> None:
        self.textos: list[str] = []
        self.eixos: list[str] = []  # rótulos de marcas do eixo: escala, não resultado

    def t(self, fig, x, y, s, **kw):
        self.textos.append(s)
        return fig.text(x, y, s, parse_math=False, **kw)


def _val(num: dict, cod: str) -> str:
    return num[cod]["valor"]


def _bruto(num: dict, cod: str) -> float:
    return float(num[cod]["valor_bruto"])


def _fmt_eixo(v: float, log: bool) -> str:
    if log:
        return f"{v:.2f}".rstrip("0").rstrip(".").replace(".", ",")
    if abs(v) < 1e-9:
        return "0"
    s = f"{v:+.0f}" if abs(v - round(v)) < 1e-9 else f"{v:+.1f}"
    return s.replace("-", MENOS).replace(".", ",")


def figura_intervalos(num: dict, paineis: list[dict], como_ler: list[str], fonte: str, destino: Path,
                      largura: float = 12.4, como_ler_lado: str = "baixo", w_comoler: float = 3.9) -> dict:
    """Painéis lado a lado; em cada linha, o rótulo em cima e o intervalo embaixo, com o valor à direita.

    Cada linha: dict(rot, sub, est, inf, sup, nota) com códigos do registro. Verde: o IC 95% exclui o nulo; cinza:
    contém. O nulo é a linha preta; as referências do protocolo são tracejadas em laranja. O bloco "Como ler" fica
    embaixo (duas colunas) ou à direita.
    """
    reg = Registro()
    ALT_TIT, ALT_LIN, ALT_EIXO, ALT_FONTE = 0.5, 0.86, 0.62, 0.3
    n_max = max(len(p["linhas"]) for p in paineis)
    alt_paineis = ALT_TIT + ALT_LIN * n_max + ALT_EIXO
    if como_ler_lado == "baixo":
        alt_cl = 0.55 + 0.33 * math.ceil(len(como_ler) / 2)
        H = 0.1 + alt_paineis + alt_cl + ALT_FONTE
        w_paineis = largura - 0.2
    else:
        alt_cl = 0.0
        H = 0.1 + alt_paineis + ALT_FONTE
        w_paineis = largura - 0.2 - w_comoler - 0.25
    W = largura
    fig = plt.figure(figsize=(W, H))
    gap = 0.45
    w_p = (w_paineis - gap * (len(paineis) - 1)) / len(paineis)
    registro = []
    for k, p in enumerate(paineis):
        x_p = 0.1 + k * (w_p + gap)
        w_val = 2.15
        w_plot = w_p - w_val - 0.1
        n = len(p["linhas"])
        y_top = H - 0.1
        reg.t(fig, x_p / W, (y_top - 0.05) / H, p["titulo"], fontsize=14, weight="bold", color=VERDE_ESC, va="top")
        ph = ALT_LIN * n
        y0 = y_top - ALT_TIT - ph
        ax = fig.add_axes([x_p / W, y0 / H, w_plot / W, ph / H])
        v0 = p["nulo"]
        log = p.get("log", False)
        valores = [v0]
        for ln in p["linhas"]:
            valores += [_bruto(num, ln["inf"]), _bruto(num, ln["sup"])]
        valores += [xr for xr, _ in p.get("refs", [])]
        if log:
            lo, hi = min(valores) / 1.12, max(valores) * 1.12
            ax.set_xscale("log")
        else:
            span = max(valores) - min(valores)
            lo, hi = min(valores) - 0.06 * span, max(valores) + 0.06 * span
        ax.set_xlim(lo, hi)
        ax.set_ylim(n - 0.5, -0.62)
        ax.axvline(v0, color="#2b2b2b", lw=1.5, zorder=1)
        for xr, rot in p.get("refs", []):
            ax.axvline(xr, color=LARANJA, lw=1.6, ls=(0, (4, 3)), zorder=1)
            reg.textos.append(rot)
            ax.text(xr, -0.62, rot, color=LARANJA, fontsize=10, ha="center", va="bottom", parse_math=False,
                    clip_on=False)
        trans = ax.get_yaxis_transform()
        for i, ln in enumerate(p["linhas"]):
            est, inf, sup = (_bruto(num, ln[c]) for c in ("est", "inf", "sup"))
            excl = inf > v0 or sup < v0
            cor = VERDE_DADO if excl else CINZA_DADO
            yb = i + 0.12
            ax.plot([inf, sup], [yb, yb], color=cor, lw=4, solid_capstyle="round", zorder=2)
            ax.plot([est], [yb], "o", ms=11, color=cor, mec="white", mew=1.8, zorder=3)
            reg.textos.append(ln["rot"])
            t_rot = ax.text(0.0, i - 0.3, ln["rot"], transform=trans, fontsize=12.5, weight="bold", color=TINTA,
                            va="center", parse_math=False, zorder=5,
                            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
            if ln.get("sub"):
                reg.textos.append(ln["sub"])
                ax.annotate(ln["sub"], xy=(1, 0.5), xycoords=t_rot, xytext=(5, 0), textcoords="offset points",
                            fontsize=10.5, color=TINTA2, va="center", parse_math=False, zorder=5,
                            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
            txt = f"{_val(num, ln['est'])} [{_val(num, ln['inf'])}; {_val(num, ln['sup'])}]"
            reg.textos.append(txt)
            ax.text(1.03, yb - 0.1, txt, transform=trans, fontsize=12.5, weight="bold", color=TINTA, va="center",
                    parse_math=False, clip_on=False)
            if ln.get("nota"):
                reg.textos.append(ln["nota"])
                ax.text(1.03, yb + 0.26, ln["nota"], transform=trans, fontsize=10.5, color=TINTA2, va="center",
                        parse_math=False, clip_on=False)
            registro.append({"painel": p["titulo"], "linha": ln["rot"], "texto": txt,
                             "codigos": [ln["est"], ln["inf"], ln["sup"]], "exclui_nulo": bool(excl)})
        ax.set_yticks([])
        if log:
            ticks = [t for t in (0.5, 0.75, 1, 1.5, 2, 3) if lo <= t <= hi]
        else:
            ticks = [t for t in ax.get_xticks() if lo <= t <= hi]
        ax.set_xticks(ticks)
        rot_ticks = [_fmt_eixo(t, log) for t in ticks]
        ax.set_xticklabels(rot_ticks, fontsize=10.5, color=TINTA2)
        reg.eixos += rot_ticks
        ax.minorticks_off()
        ax.tick_params(axis="x", length=0, pad=4)
        ax.grid(axis="x", color=GRADE, lw=0.8)
        ax.set_axisbelow(True)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
        ax.spines["bottom"].set_color(EIXO)
        reg.t(fig, (x_p + w_plot / 2) / W, (y0 - 0.36) / H, p["eixo"], fontsize=10.5, color=TINTA2, ha="center",
              va="top")
    from matplotlib.patches import FancyBboxPatch
    if como_ler_lado == "baixo":
        yb, xb, wb, hb = ALT_FONTE, 0.1, W - 0.2, alt_cl - 0.12
    else:
        xb, wb = W - 0.1 - w_comoler, w_comoler
        yb, hb = ALT_FONTE + 0.1, alt_paineis - 0.2
    fig.patches.append(FancyBboxPatch((xb / W, yb / H), wb / W, hb / H, boxstyle="round,pad=0,rounding_size=0.012",
                                      transform=fig.transFigure, facecolor=CLARO_FUNDO, edgecolor=LINHA_CLARA, lw=1))
    reg.t(fig, (xb + 0.15) / W, (yb + hb - 0.25) / H, "Como ler", fontsize=13, weight="bold", color=VERDE_ESC,
          va="center")
    if como_ler_lado == "baixo":
        meia = math.ceil(len(como_ler) / 2)
        for k, s in enumerate(como_ler):
            col, lin = divmod(k, meia)
            reg.t(fig, (xb + 0.15 + col * wb / 2) / W, (yb + hb - 0.6 - 0.33 * lin) / H, "•  " + s, fontsize=11,
                  color=TINTA, va="center")
    else:
        import textwrap
        y = yb + hb - 0.62
        for s in como_ler:
            linhas = textwrap.wrap(s, width=int(w_comoler * 8.4))
            for j, t in enumerate(linhas):
                reg.t(fig, (xb + 0.15) / W, y / H, ("•  " if j == 0 else "    ") + t, fontsize=11, color=TINTA,
                      va="center")
                y -= 0.24
            y -= 0.14
    reg.t(fig, 0.1 / W, 0.06 / H, fonte + " " + FONTE_FIG, fontsize=8.5, color=MUDO, va="bottom")
    fig.savefig(destino, dpi=200, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    return {"linhas": registro, "textos": reg.textos, "eixos": reg.eixos}


def figura_h1(num: dict, destino: Path) -> dict:
    paineis = [
        dict(titulo="Vagas preenchidas por município (N1)", nulo=0.0,
             eixo="diferença no corte (vagas por município)",
             linhas=[dict(rot="Com controle das vagas oferecidas", sub="primária",
                          est="N1_SA_TAU", inf="N1_SA_INF", sup="N1_SA_SUP",
                          nota=f"p de Holm {_val(num, 'N1_SA_HOLM')}"),
                     dict(rot="Sem controle", sub="efeito total da faixa",
                          est="N1_SB_TAU", inf="N1_SB_INF", sup="N1_SB_SUP",
                          nota=f"média abaixo do corte {_val(num, 'N1_MEDIA')}")]),
        dict(titulo="Célula aberta preenchida (A3, p.p.)", nulo=0.0,
             eixo="diferença no corte (p.p.)",
             refs=[(10.0, "+10 p.p. (protocolo)")],
             linhas=[dict(rot="Ciclos 1–3, cortes empilhados", sub="principal",
                          est="A3_EMP_TAU", inf="A3_EMP_INF", sup="A3_EMP_SUP",
                          nota=f"MDE {_val(num, 'A3_EMP_MDE')}"),
                     dict(rot="Só o corte 0,300", sub="R$ 10 mil → R$ 15 mil", est="A3_300_TAU", inf="A3_300_INF",
                          sup="A3_300_SUP", nota=f"MDE {_val(num, 'A3_300_MDE')}"),
                     dict(rot="Só o corte 0,400", sub="R$ 15 mil → R$ 20 mil", est="A3_400_TAU", inf="A3_400_INF",
                          sup="A3_400_SUP", nota=f"MDE {_val(num, 'A3_400_MDE')}")]),
    ]
    como_ler = [
        "Ponto: diferença no corte, bolsa maior menos bolsa menor.",
        "Barra: IC 95%; a ponta direita é o maior aumento compatível.",
        "Barra cruzando o zero: não se distingue de zero (não prova zero).",
        "Cinza: o IC contém zero; verde: exclui. MDE: 80% de poder.",
    ]
    return figura_intervalos(num, paineis, como_ler, "Fontes: N_estimativas.csv (doc 49); S57_resumo.json (A3; doc 57).",
                             destino)


def figura_h2(num: dict, destino: Path) -> dict:
    paineis = [
        dict(titulo="Razão de chances da 1ª opção por +R$ 5 mil", nulo=1.0, log=True,
             eixo="razão de chances (escala log); 1 = a bolsa não muda a escolha",
             linhas=[dict(rot="Ciclos 1–3, com distância (M1)", sub="primária",
                          est="M1_RC", inf="M1_RC_INF", sup="M1_RC_SUP", nota=f"p {_val(num, 'M1_P')}"),
                     dict(rot="Só o ciclo 1 (M5)", est="M5_C1_RC", inf="M5_C1_RCI", sup="M5_C1_RCS",
                          nota=f"p {_val(num, 'M5_C1_P')}"),
                     dict(rot="Só o ciclo 2 (M5)", est="M5_C2_RC", inf="M5_C2_RCI", sup="M5_C2_RCS",
                          nota=f"p {_val(num, 'M5_C2_P')}"),
                     dict(rot="Só o ciclo 3 (M5)", est="M5_C3_RC", inf="M5_C3_RCI", sup="M5_C3_RCS",
                          nota=f"p {_val(num, 'M5_C3_P')}"),
                     dict(rot="Ciclo 2, sem distância (E9)", sub="exploratório",
                          est="E9_C2_RC", inf="E9_C2_RCI", sup="E9_C2_RCS", nota=f"p {_val(num, 'E9_C2_P')}")]),
    ]
    como_ler = [
        "Cada linha compara vagas abertas do mesmo curso e ciclo que diferem só no degrau da bolsa, com o IVS "
        "contínuo controlado.",
        "Acima de 1: a vaga de bolsa maior é mais escolhida como 1ª opção.",
        "Barra: o intervalo de 95%. Se cruza a linha do 1, os dados não distinguem a bolsa de efeito nenhum.",
        "Verde: o IC exclui 1; cinza: contém.",
        "É a escolha de quem já se candidatou: não diz quantos médicos o programa atrai.",
    ]
    return figura_intervalos(num, paineis, como_ler, "Fontes: P1_estimativas.csv (doc 57a); E8_resumo.json (E9).",
                             destino, como_ler_lado="direita")


def figura_h4(num: dict, destino: Path) -> dict:
    paineis = [
        dict(titulo="Horas semanais cadastradas do médico no CNES", nulo=0.0,
             eixo="diferença média depois da entrada (horas por semana)",
             linhas=[dict(rot="Horas totais (P4)", est="P4_HT_ATT", inf="P4_HT_INF", sup="P4_HT_SUP",
                          nota=f"pré: p {_val(num, 'P4_HT_PRE')}"),
                     dict(rot="No município do posto (P4)", est="P4_HM_ATT", inf="P4_HM_INF", sup="P4_HM_SUP",
                          nota=f"pré falha: p {_val(num, 'P4_HM_PRE')}"),
                     dict(rot="Fora do município do posto (P4)", est="P4_HF_ATT", inf="P4_HF_INF", sup="P4_HF_SUP",
                          nota=f"pré: p {_val(num, 'P4_HF_PRE')}"),
                     dict(rot="Horas totais (P4-CA)", est="CA_HT_EST", inf="CA_HT_INF", sup="CA_HT_SUP",
                          nota=f"p de Holm {_val(num, 'CA_HT_HOLM')}"),
                     dict(rot="No município da 1ª opção (P4-CA)", est="CA_HM_EST", inf="CA_HM_INF", sup="CA_HM_SUP",
                          nota="quase mecânico")]),
    ]
    como_ler = [
        "P4: médicos que já entraram no PMM-E contra os que ainda não tinham entrado.",
        "P4-CA: aprovados contra não aprovados por um ou dois pontos na nota de corte.",
        "Verde: o IC 95% exclui zero. 'Pré falha': os grupos já se afastavam antes da entrada.",
        "Leia como associação: horas cadastradas não são horas trabalhadas.",
    ]
    return figura_intervalos(num, paineis, como_ler, "Fontes: S57_resumo.json (P4; doc 57d); CA_estimativas.csv (57h).",
                             destino, como_ler_lado="direita")


# Cadeia do doc 57: uma linha por pergunta, cada uma na sua escala (simétrica em torno do nulo)
# A "força da evidência" de cada linha sai de uma regra explícita aplicada a valores de output/ (nunca digitada):
#   ("holm", código do p de Holm): p de Holm >= 0,05 -> "inconclusivo"; < 0,05 -> "rejeita zero (Holm)";
#   ("ic", None): o IC 95% da própria linha contém o nulo -> "inconclusivo"; exclui -> "IC exclui o nulo";
#   ("pre", código do p do Wald do pré): p >= 0,05 -> "ATT sob tendências paralelas"; < 0,05 -> "ATT com pré falhando";
#   ("estatuto", código do estatuto do bloco): começa com EXPLORATORIO -> "exploratório";
#   ("holm", código do p de Holm, código do estatuto): como "holm", mas se o estatuto do bloco termina em
#   POS_RESULTADO e o Holm rejeita -> "rejeita zero, pós-resultado".
# A regra é por linha; o doc 57 classifica a pergunta inteira (no P4, outros outcomes falham no pré).
ALFA = 0.05
POS_RESULTADO = "POS_RESULTADO"


def forca_da_linha(num: dict, regra: tuple, codigos: tuple, nulo_valor: float) -> tuple[str, dict]:
    tipo, cod = regra[:2]
    if tipo == "holm":
        p = float(num[cod]["valor_bruto"])
        entradas = {"regra": tipo, cod: p}
        if p >= ALFA:
            return "inconclusivo", entradas
        if len(regra) == 3:
            e = str(num[regra[2]]["valor_bruto"])
            entradas[regra[2]] = e
            if e.endswith(POS_RESULTADO):
                return "rejeita zero, pós-resultado", entradas
        return "rejeita zero (Holm)", entradas
    if tipo == "ic":
        inf, sup = (float(num[c]["valor_bruto"]) for c in codigos[1:])
        return ("inconclusivo" if inf <= nulo_valor <= sup else "IC exclui o nulo"), {"regra": tipo, "inf": inf,
                                                                                       "sup": sup}
    if tipo == "pre":
        p = float(num[cod]["valor_bruto"])
        return ("ATT sob tendências paralelas" if p >= ALFA else "ATT com pré falhando"), {"regra": tipo, cod: p}
    if tipo == "estatuto":
        e = str(num[cod]["valor_bruto"])
        if not e.startswith("EXPLORATORIO"):
            raise SystemExit(f"ERRO: estatuto {e!r} não é exploratório; a regra da linha não se aplica")
        return "exploratório", {"regra": tipo, cod: e}
    raise SystemExit(f"ERRO: regra de força desconhecida {regra}")


LINHAS_CADEIA_57 = [
    # (elo, rótulo, sub, est, inf, sup, nulo, log, sufixo, leitura curta, regra da força)
    ("ESCOLHA DO MÉDICO", "Peso da bolsa na 1ª opção (P1, M1)", "razão de chances por +R$ 5 mil · pacote do corte",
     "M1_RC", "M1_RC_INF", "M1_RC_SUP", 1.0, True, "", "p de Holm {M1_P}", ("holm", "M1_P")),
    ("ESCOLHA DO MÉDICO", "UF de origem × bolsa (H3, D_UF)", "θ_UF − 10·β, log-chance · no modelo de escolha",
     "H3_DUF", "H3_DUF_INF", "H3_DUF_SUP", 0.0, False, "", "p de Holm {H3_DUF_HOLM} (unilateral)",
     ("holm", "H3_DUF_HOLM", "H3_ESTATUTO")),
    ("PREENCHIMENTO", "Célula aberta preenchida (A3)", "p.p. · ciclos 1–3, cortes empilhados · pacote do corte",
     "A3_EMP_TAU", "A3_EMP_INF", "A3_EMP_SUP", 0.0, False, " p.p.", "MDE {A3_EMP_MDE} p.p.", ("ic", None)),
    ("PREENCHIMENTO", "Vagas preenchidas por município (N1)", "com controle das vagas oferecidas · pacote do corte",
     "N1_SA_TAU", "N1_SA_INF", "N1_SA_SUP", 0.0, False, "", "p de Holm {N1_SA_HOLM}", ("holm", "N1_SA_HOLM")),
    ("ENTRADA DO MÉDICO", "Vínculo no município da vaga (P6, Y1)", "fração · alocado × não alocado por pouco",
     "P6_Y1_EST", "P6_Y1_INF", "P6_Y1_SUP", 0.0, False, "", "p de Holm {P6_Y1_HOLM} · quase mecânico",
     ("estatuto", "P6_ESTATUTO")),
    ("ENTRADA DO MÉDICO", "Horas totais (P6, Y3)", "h/sem · alocado × não alocado por pouco",
     "P6_Y3_EST", "P6_Y3_INF", "P6_Y3_SUP", 0.0, False, "", "p de Holm {P6_Y3_HOLM}", ("estatuto", "P6_ESTATUTO")),
    ("CAPACIDADE", "Horas totais do médico (P4)", "h/sem · entrada no PMM-E, coortes escalonadas",
     "P4_HT_ATT", "P4_HT_INF", "P4_HT_SUP", 0.0, False, "",
     "pré: p {P4_HT_PRE}; ruptura M̄ = {RR_HT}; outros outcomes falham", ("pre", "P4_HT_PRE")),
    ("ACESSO", "Produção SUS nas CBO-alvo (K1)", "por 10 mil hab./mês · DiRD nos cortes",
     "K1_TAU", "K1_INF", "K1_SUP", 0.0, False, "", "p de Holm {K1_HOLM}", ("holm", "K1_HOLM")),
    ("REALOCAÇÃO", "Concorrentes e preenchimento (R-P1)", "p.p. por +R$ 5 mil · região de saúde",
     "R_P1_EST", "R_P1_INF", "R_P1_SUP", 0.0, False, " p.p.", "p de Holm {R_P1_HOLM}", ("holm", "R_P1_HOLM")),
]


def figura_cadeia_57(num: dict, destino: Path) -> dict:
    reg = Registro()
    n = len(LINHAS_CADEIA_57)
    W, ALT = 12.4, 0.76
    H = 1.15 + ALT * n + 1.2
    fig = plt.figure(figsize=(W, H))
    reg.t(fig, 0.15 / W, (H - 0.18) / H, "A cadeia em uma figura: o que os dados dizem, pergunta a pergunta",
          fontsize=15, weight="bold", color=VERDE_ESC, va="top")
    reg.t(fig, 0.15 / W, (H - 0.52) / H, "Cada linha tem a sua escala, simétrica em torno do nulo (0; 1 na razão de "
          "chances). Leia se a barra cruza a linha preta, não o tamanho entre linhas.", fontsize=11, color=TINTA2,
          va="top")
    for x, s in ((4.95, "intervalo de 95%"), (6.6, "estimativa [IC 95%]"), (10.55, "força da evidência")):
        reg.t(fig, x / W, (H - 0.95) / H, s, fontsize=10, color=MUDO, weight="bold", ha="center" if x != 6.6 else "left")
    topo = H - 1.15
    elo_ant = None
    registro = []
    cores_forca = {"inconclusivo": ("#e9ecef", "#3a3a3a"), "exploratório": ("#fff1d6", "#7a4a00"),
                   "ATT com pré falhando": ("#fde2e1", "#8a1c17"), "ATT sob tendências paralelas": ("#e3eefa", "#1f4f8a"),
                   "rejeita zero (Holm)": ("#e3f2e7", "#0f5a2a"), "IC exclui o nulo": ("#e3f2e7", "#0f5a2a"),
                   "rejeita zero, pós-resultado": ("#e3f2e7", "#0f5a2a")}
    for i, (elo, rot, sub, ce, ci, cs, v0, log, suf, leit, regra) in enumerate(LINHAS_CADEIA_57):
        forca, entradas_forca = forca_da_linha(num, regra, (ce, ci, cs), v0)
        y0 = topo - (i + 1) * ALT
        yc = y0 + ALT / 2
        if elo != elo_ant:
            fig.add_artist(plt.Line2D([0.15 / W, (W - 0.15) / W], [(y0 + ALT) / H] * 2, color=LINHA_CLARA, lw=0.8))
            reg.t(fig, 0.15 / W, (y0 + ALT - 0.13) / H, elo, fontsize=9, color=MUDO, weight="bold", va="center")
            elo_ant = elo
        reg.t(fig, 0.15 / W, (yc - 0.03) / H, rot, fontsize=12.5, color=TINTA, weight="bold", va="center")
        reg.t(fig, 0.15 / W, (yc - 0.26) / H, sub, fontsize=9.8, color=TINTA2, va="center")
        est, inf, sup = (_bruto(num, c) for c in (ce, ci, cs))
        ax = fig.add_axes([3.85 / W, (y0 + 0.12) / H, 2.3 / W, (ALT - 0.24) / H])
        lo, hi = limites_simetricos(inf, sup, v0, log)
        if log:
            ax.set_xscale("log")
        ax.set_xlim(lo, hi)
        ax.set_ylim(-1, 1)
        ax.axvline(v0, color="#3a3a3a", lw=1.2)
        excl = inf > v0 or sup < v0
        cor = VERDE_DADO if excl else CINZA_DADO
        ax.plot([inf, sup], [0, 0], color=cor, lw=3, solid_capstyle="round")
        ax.plot([est], [0], "o", ms=8, color=cor, mec="white", mew=1.4)
        ax.set_axis_off()
        txt = f"{_val(num, ce)}{suf} [{_val(num, ci)}; {_val(num, cs)}]"
        reg.t(fig, 6.6 / W, (yc + 0.09) / H, txt, fontsize=12.5, color=TINTA, weight="bold", va="center")
        leitura = leit.format(**{k: _val(num, k) for k in re.findall(r"\{(\w+)\}", leit)})
        reg.t(fig, 6.6 / W, (yc - 0.2) / H, leitura, fontsize=9.8, color=TINTA2, va="center")
        fundo, frente = cores_forca[forca]
        from matplotlib.patches import FancyBboxPatch
        fig.patches.append(FancyBboxPatch((9.3 / W, (yc - 0.17) / H), 2.5 / W, 0.34 / H,
                                          boxstyle="round,pad=0,rounding_size=0.012", transform=fig.transFigure,
                                          facecolor=fundo, edgecolor="none"))
        reg.t(fig, 10.55 / W, yc / H, forca, fontsize=10.5, color=frente, weight="bold", ha="center", va="center")
        registro.append({"linha": rot, "texto": txt, "codigos": [ce, ci, cs], "forca": forca,
                         "forca_regra": entradas_forca, "exclui_nulo": bool(excl)})
    reg.t(fig, 0.15 / W, 0.93 / H, "Força da evidência, por linha: Holm ou IC com o nulo → inconclusivo; pré do Wald → ATT; "
          "estatuto do bloco → exploratório;", fontsize=10, color=TINTA2, va="center")
    reg.t(fig, 0.15 / W, 0.66 / H, "Holm < 0,05 num bloco pós-resultado → rejeita zero, pós-resultado. Nenhuma linha é "
          "causal-limpa; a da H3 compara dois pesos do mesmo modelo de escolha.", fontsize=10, color=TINTA2, va="center")
    reg.t(fig, 0.15 / W, 0.39 / H, "Nada aqui é efeito da participação no PMM-E nem da geografia. Verde: o IC 95% exclui "
          "o nulo; cinza: contém.", fontsize=10, color=TINTA2, va="center")
    reg.t(fig, 0.15 / W, 0.08 / H, "Fontes: S57_resumo.json (doc 57); P4_estimativas.csv; P1h_magnitudes.csv (doc 57i). "
          + FONTE_FIG, fontsize=8.5, color=MUDO, va="bottom")
    fig.savefig(destino, dpi=200, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    return {"linhas": registro, "textos": reg.textos, "eixos": reg.eixos}


def linhas_tabela_descritiva(num: dict) -> list[list[str]]:
    v = lambda c: _val(num, c)  # noqa: E731
    linhas = [["Item", "Ciclo 1", "Ciclo 2", "Ciclo 3"],
              ["Municípios com célula no quadro"] + [v(f"D_C{c}_MUN") for c in (1, 2, 3)],
              ["Células (estabelecimento × curso)"] + [v(f"D_C{c}_CEL") for c in (1, 2, 3)],
              ["Vagas imediatas · cadastro reserva"] + [f"{v(f'D_C{c}_VI')} · {v(f'D_C{c}_CR')}" for c in (1, 2, 3)],
              ["Candidatos nos resultados (universo G1)"] + [v(f"D_C{c}_CANDG1") for c in (1, 2, 3)],
              ["… ligados ao CNES"] + [v(f"D_C{c}_LIG") for c in (1, 2, 3)],
              ["… com 1ª opção numa célula do quadro"] + [v(f"D_C{c}_CAND1") for c in (1, 2, 3)],
              ["Amostra da escolha (P1)"] + [v(f"D_C{c}_P1") for c in (1, 2, 3)],
              ["Células preenchidas na 1ª chamada"] + [f"{v(f'D_C{c}_PRE1')} ({v(f'D_C{c}_PRE1_PCT')}%)" for c in (1, 2, 3)],
              ["Células preenchidas até a 2ª chamada"] + [f"{v(f'D_C{c}_PRE2')} ({v(f'D_C{c}_PRE2_PCT')}%)" for c in (1, 2)]
              + ["não observado"],
              ["Municípios por faixa: R$ 10 · 15 · 20 mil"]
              + [f"{v(f'D_C{c}_F3')} · {v(f'D_C{c}_F2')} · {v(f'D_C{c}_F1')}" for c in (1, 2)]
              + [f"{v('D_C3_F3')} · {v('D_C3_F2')} · {v('D_C3_F1')} (e {v('D_C3_SEM_IVS')} sem IVS)"]]
    return linhas


def linhas_tabela_fontes(num: dict) -> list[list[str]]:
    v = lambda c: _val(num, c)  # noqa: E731
    return [
        ["Base", "Fonte oficial", "Período", "Unidade e chaves", "Cobertura", "Uso"],
        ["Quadros de vagas e resultados", "SGTES/MS: chamamentos dos ciclos 1, 2 e 3", "2025–2026",
         "célula = estabelecimento × curso",
         f"{v('D_C1_CEL')} · {v('D_C2_CEL')} · {v('D_C3_CEL')} células", "H1, descritivas"],
        ["Candidatos e opções", "SGTES/MS: classificação, alocação e homologação", "2025–2026",
         "candidato × opção; CPF mascarado só em memória",
         f"{v('D_C1_CANDG1')} · {v('D_C2_CANDG1')} · {v('D_C3_CANDG1')} candidatos", "H2, H3, P6"],
        ["IVS 2010 oficial", "Ipea, Plataforma IVS (Censo 2010)", "2010", "município (IBGE)",
         f"{v('D_IVS_MUN')} municípios", "running variable"],
        ["CNES: vínculos e horas", "DATASUS/MS, base completa mensal", "2022-01 a 2026-08",
         "profissional × estabelecimento × mês; pseudônimo",
         f"ligados: {v('D_C1_LIG')} · {v('D_C2_LIG')} · {v('D_C3_LIG')}", "H2 (origem), H4"],
        ["Especialistas ativos do PMM-E", "MS, relação nominal", "2026-09", "médico × posto; CRM só em memória",
         f"{v('D_ATIVOS')} registros", "H4 (chegada)"],
        ["Produção ambulatorial e hospitalar", "DATASUS/MS: SIA e SIH", "mensal, pré e pós", "município × mês × grupo",
         "nacional", "K (acesso)"],
        ["População", "IBGE, Censo 2022 (SIDRA)", "2022", "município (IBGE)", f"{v('D_POP_MUN')} municípios",
         "denominadores"],
        ["Atos com corte no IVS", "portarias do MS (auditoria 18)", "2023–2026", "ato × corte", "nos dois cortes",
         "ameaça: pacote do corte"],
    ]


def tabela_png(linhas: list[list[str]], larguras: list[float], destino: Path, titulo: str, nota: str,
               fs: float = 10.5) -> dict:
    """Tabela legível em slide, desenhada com retângulos e texto (sem o estilo padrão do matplotlib)."""
    reg = Registro()
    W = sum(larguras) + 0.3
    alt_lin = 0.42
    H = 0.55 + alt_lin * len(linhas) + 0.55
    fig = plt.figure(figsize=(W, H))
    reg.t(fig, 0.15 / W, (H - 0.12) / H, titulo, fontsize=12, weight="bold", color=VERDE_ESC, va="top")
    from matplotlib.patches import Rectangle
    y = H - 0.55
    for i, ln in enumerate(linhas):
        x = 0.15
        cab = i == 0
        fundo = VERDE_ESC if cab else (CLARO_FUNDO if i % 2 else "white")
        fig.patches.append(Rectangle((0.15 / W, (y - alt_lin) / H), (W - 0.3) / W, alt_lin / H,
                                     transform=fig.transFigure, facecolor=fundo, edgecolor=LINHA_CLARA, lw=0.6))
        for j, (cel, lw) in enumerate(zip(ln, larguras)):
            reg.t(fig, (x + 0.08) / W, (y - alt_lin / 2) / H, cel, fontsize=fs, va="center",
                  color="white" if cab else TINTA, weight="bold" if (cab or j == 0) else "normal")
            x += lw
        y -= alt_lin
    reg.t(fig, 0.15 / W, (y - 0.18) / H, nota, fontsize=8.6, color=TINTA2, va="top")
    reg.t(fig, 0.15 / W, 0.06 / H, FONTE_FIG, fontsize=7.2, color=MUDO, va="bottom")
    fig.savefig(destino, dpi=200, facecolor="white", metadata={"Software": None})
    plt.close(fig)
    return {"textos": reg.textos}


def gravar_csv_tabela(linhas: list[list[str]], destino: Path) -> None:
    pd.DataFrame(linhas[1:], columns=linhas[0]).assign(natureza_dos_dados="EMPIRICO").to_csv(
        destino, index=False, encoding="utf-8", lineterminator="\n")


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
    (AUD18, "parâmetros normativos citados (co-políticas)", "2026-10-18", "atos federais com corte em IVS",
     "texto", "trechos por regex"),
    (GALERIA, "código da variante A colorida (fig_regra_pontos)", "-", "-", "-", "-"),
    (RAIZ / S57, "síntese vigente (doc 57): valores com arquivo e seletor de origem (chave v)", "2026-10-24",
     "P1 a P6, realocação; ciclos 1–3", "várias (ver chaves)", "v.<chave>.v"),
    (RAIZ / N_EST, "família N (protocolo 48): N1 com e sem controle, robustez", "2026-10-19",
     "municípios com célula, ciclos 1–3, cortes 0,300 e 0,400", "vagas por município",
     "outcome_id + populacao + corte + especificacao + variante"),
    (RAIZ / P1_EST, "P1 (protocolo 52): M1, M5 por ciclo, M0–M9", "2026-10-23", "candidatos de 1ª opção, ciclos 1–3",
     "log-chance por R$ 1 mil", "modelo + ciclo + termo"),
    (RAIZ / H_EST, "Rambachan–Roth do P4 (protocolo 59, parte A)", "2026-10-25", "médicos dos ciclos 1 e 2",
     "h/sem; M̄", "id_linha + alvo + restricao + parametro"),
    (RAIZ / CA_EST, "comparação alternativa P4-CA (protocolo 59, parte B)", "2026-10-25",
     "candidatos perto da nota de corte", "h/sem", "id_linha + outcome + estatistica"),
    (RAIZ / G1_RES, "portão G1: candidatos ligados ao CNES por ciclo", "2026-10-19", "ciclos 1–3", "candidatos",
     "taxas_ligacao.g1_cpf_nome.<ciclo>"),
    (RAIZ / A16_MAN, "manifesto do a16: lista de ativos do PMM-E", "2026-10-19", "lista de 11/09/2026", "registros",
     "listas_pmme"),
    (CELULAS, "quadro de células da 1ª chamada (descritivas por ciclo)", "2026-10-19", "ciclos 1–3",
     "célula estabelecimento × curso", "ciclo + co_cnes_7d + cod_curso"),
    (POP2022, "população do Censo 2022 (cobertura da tabela de fontes)", "2022", "municípios", "habitantes",
     "co_ibge_7d"),
    (RAIZ / P1H_CSV, "H3 (P1h, protocolo 52b; doc 57i; auditoria 31): D_UF, km equivalentes, sensibilidades e pesos",
     "2026-10-26", "amostra do P1 (candidatos de 1ª opção, ciclos 1–3), M1 e sensibilidades", "log-chance; km",
     "id_linha + modelo + ciclo (+ componente nas linhas FIG)"),
    (RAIZ / P1H_RES, "H3: estatuto do bloco e hash da figura auditada", "2026-10-26", "P1h", "-", "estatuto; saidas"),
    (RAIZ / P1H_FIG, "H3: figura dos pesos no M1, auditada (auditoria 31, A1 e A2); usada no slide sem redesenho",
     "2026-10-26", "M1, ciclos 1–3", "log-chance", "-"),
]


def conferir_p1h() -> None:
    """A H3 entra só com as saídas auditadas: natureza EMPIRICO e figura com o hash gravado no resumo do P1h."""
    res = _ler_json(P1H_RES)
    if res.get("natureza_dos_dados") != "EMPIRICO":
        raise SystemExit("ERRO: P1h_resumo.json sem natureza EMPIRICO")
    if set(_ler_csv(P1H_CSV)["natureza_dos_dados"]) != {"EMPIRICO"}:
        raise SystemExit("ERRO: P1h_magnitudes.csv com linha não EMPIRICO")
    if sha256(RAIZ / P1H_FIG) != res["saidas"][P1H_FIG] or sha256(RAIZ / P1H_CSV) != res["saidas"][P1H_CSV]:
        raise SystemExit("ERRO: figura ou CSV do P1h diferem do hash gravado em P1h_resumo.json")


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

    conferir_p1h()
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

    calc["descritivas"] = descritivas()
    numeros = registrar_numeros(calc)
    num = {c: e for b in numeros.values() for c, e in b.items()}
    novas = {}
    for nome, fn, desc in (("h1_preenchimento.png", figura_h1, "H1: N1 com e sem controle e A3, com 'Como ler'"),
                           ("h2_escolha.png", figura_h2, "H2: razão de chances da 1ª opção por ciclo, com 'Como ler'"),
                           ("h4_horas_medico.png", figura_h4, "H4: horas do médico (P4 e P4-CA), com 'Como ler'"),
                           ("cadeia_resumo_doc57.png", figura_cadeia_57, "cadeia-resumo com as linhas do doc 57")):
        p = SAIDA / nome
        novas[nome] = fn(num, p)
        figs.append({"arquivo": p, "natureza": "EMPIRICO", "descricao": desc,
                     "fontes": [RAIZ / S57, RAIZ / N_EST, RAIZ / P1_EST, RAIZ / CA_EST, E8_RESUMO]
                     + ([RAIZ / P1H_CSV, RAIZ / P1H_RES] if nome == "cadeia_resumo_doc57.png" else [])})
    t_desc = linhas_tabela_descritiva(num)
    t_font = linhas_tabela_fontes(num)
    gravar_csv_tabela(t_desc, SAIDA / "tabela_descritiva_ciclos.csv")
    gravar_csv_tabela(t_font, SAIDA / "tabela_fontes.csv")
    novas["tabela_descritiva_ciclos.png"] = tabela_png(
        t_desc, [3.9, 2.2, 2.2, 2.9], SAIDA / "tabela_descritiva_ciclos.png", "Os três ciclos em números (descritivo)",
        "Célula = estabelecimento × curso no quadro da 1ª chamada; preenchida = alguma confirmação ou homologação. "
        "Faixa pela grade aplicada.\nAmostra P1 = 1ª opção numa célula do quadro, ligado ao CNES e com município de origem.")
    novas["tabela_fontes.png"] = tabela_png(
        t_font, [2.6, 3.3, 1.5, 3.4, 2.3, 1.7], SAIDA / "tabela_fontes.png", "Bases de dados", "Todas as bases são "
        "oficiais e públicas; dados pessoais só em memória ou em cache fora do Git.", fs=9.2)
    for nome, desc, fonte in (("tabela_descritiva_ciclos.png", "tabela descritiva por ciclo", CELULAS),
                              ("tabela_fontes.png", "tabela de fontes", RAIZ / G1_RES)):
        figs.append({"arquivo": SAIDA / nome, "natureza": "EMPIRICO", "descricao": desc, "fontes": [fonte]})
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
        "figuras_novas": novas,
        "tabelas_csv": [{"arquivo": _rel(SAIDA / n), "sha256": sha256(SAIDA / n)}
                        for n in ("tabela_descritiva_ciclos.csv", "tabela_fontes.csv")],
        "figuras":[{"arquivo": _rel(f["arquivo"]), "sha256": sha256(f["arquivo"]), "natureza": f["natureza"],
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
