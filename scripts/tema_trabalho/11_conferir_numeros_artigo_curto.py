"""Confere cada numero citado em paper_pmme_curto.tex contra os artefatos.

Mesma regra do artigo principal (`10_conferir_numeros_artigo.py`): nenhuma
cifra pode existir sem origem rastreavel em `output/`. Este script reutiliza os
leitores, formatadores e a conferencia estrutural do conferidor principal e
acrescenta as origens que so o artigo curto cita — intervalo exato de A8, wild
cluster bootstrap e MDE ex-post de A4, valores q de multiplicidade, as tres
ameacas do C-7 em A5 e as frases da rodada multi-outcome da bolsa (E6 a E9)
que o curto escreve de modo proprio; as que repetem o principal reutilizam os
trechos MO_* dele.

Dois portoes:

1. Cada trecho esperado, reconstruido a partir da fonte, tem de existir no
   `.tex` do artigo curto. Os trechos do conferidor principal sao reutilizados
   quando o artigo curto repete a mesma formulacao; os demais sao declarados
   aqui.
2. Cobertura: todo numero com virgula decimal no corpo do artigo curto (sem a
   bibliografia) tem de estar contido em algum trecho conferido. Um decimal que
   nao esteja e numero sem origem, e reprova.

Mapeamento gravado em `output/tema_trabalho/A8_conferencia_numeros_artigo_curto.csv`.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
TEX = ROOT / "paper_pmme_curto.tex"
OUT = ROOT / "output" / "tema_trabalho"
CONFERENCIA_CSV = OUT / "A8_conferencia_numeros_artigo_curto.csv"

# Carrega o conferidor principal como modulo: o carregamento registra as 193
# cifras do artigo principal em `REGISTROS`, que reutilizamos abaixo.
_spec = importlib.util.spec_from_file_location(
    "conferidor_principal", ROOT / "scripts" / "tema_trabalho" / "10_conferir_numeros_artigo.py"
)
cp = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(cp)

decimal_br, pontos, inteiro = cp.decimal_br, cp.pontos, cp.inteiro
csv_valor, json_valor = cp.csv_valor, cp.json_valor

A8_TAB06 = "output/tema_trabalho/A8_tabela_06_intervalos_exatos.csv"
A4_WILD = "output/tema_trabalho/A4_tabela_08_wild_cluster_bootstrap.csv"
A4_MDE = "output/tema_trabalho/A4_tabela_09_mde_ex_ante_ex_post.csv"
A5_C7 = "output/tema_trabalho/A5_ameacas_c7.json"
RDD_R1 = "output/rdd_bolsa/portao_r1_ivs_oficial.json"
RDD_E3_STATUS = "output/rdd_bolsa/E3_status.json"
RDD_E3_ESTIM = "output/rdd_bolsa/E3_estimativas.csv"
RDD_E3_DIAG = "output/rdd_bolsa/E3_diagnosticos.csv"
RDD_E5_ESPEC = "output/rdd_bolsa/E5_especificacoes.csv"
RDD_E5_DECOMP = "output/rdd_bolsa/E5_decomposicao_ic.csv"

REGISTROS: list[dict[str, Any]] = []


def registrar(identificador: str, bloco: str, descricao: str, valor: str, fonte: str,
              localizador: str, bruto: Any, transformacao: str, trecho: str) -> None:
    REGISTROS.append({
        "id": identificador, "bloco": bloco, "descricao": descricao, "valor_no_artigo": valor,
        "fonte_arquivo": fonte, "fonte_localizador": localizador, "valor_bruto_na_fonte": bruto,
        "transformacao": transformacao, "trecho_esperado_no_tex": trecho,
    })


def p_texto(valor: float, casas: int = 3) -> str:
    """p-valor com o numero de casas usado no artigo curto."""
    return decimal_br(valor, casas)


# ------------------------------------------------------------- A8: artigo curto

principal = {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": "gap_1_ac"}
hom, loc_h = csv_valor(cp.A8_ESTIM, {**principal, "desfecho": "homologacao_mesma_celula"}, "diferenca")
atv, loc_a = csv_valor(cp.A8_ESTIM, {**principal, "desfecho": "ativo_mesma_celula_snapshot"}, "diferenca")
registrar("CURTO_RESUMO_HOMOLOG", "Resumo", "Efeito em homologacao no mesmo curso-CNES", pontos(hom), cp.A8_ESTIM, loc_h, hom,
          "proporcao x100, 1 casa", f"elevou a homologação no mesmo curso--CNES em {pontos(hom)} pontos percentuais")
registrar("CURTO_RESUMO_ATIVO", "Resumo", "Efeito em presenca ativa no mesmo curso-CNES", pontos(atv), cp.A8_ESTIM, loc_a, atv,
          "proporcao x100, 1 casa", f"em 12 de agosto de 2026, em {pontos(atv)} pontos percentuais")

# Tabela de validacao: principal, placebos, janelas, empates, replicacao.
for rotulo, amostra in [("Principal & Gap de exatamente 1 ponto, 2025", "gap_1_ac"),
                        ("Janela & Gap positivo de até 2 pontos, 2025", "gap_positivo_ate_2_ac"),
                        ("Janela & Qualquer gap positivo, 2025", "qualquer_gap_positivo_ac"),
                        ("Descritivo & Empates, 2025 (não causal)", "empate_descritivo_nao_causal")]:
    filtro_h = {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra, "desfecho": "homologacao_mesma_celula"}
    filtro_a = {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra, "desfecho": "ativo_mesma_celula_snapshot"}
    n, loc_n = csv_valor(cp.A8_GAP, filtro_h, "n_pares")
    dh, loc_dh = csv_valor(cp.A8_GAP, filtro_h, "diferenca")
    da, loc_da = csv_valor(cp.A8_GAP, filtro_a, "diferenca")
    trecho = f"{rotulo} & {inteiro(n)} & {pontos(dh)} & {pontos(da)} \\\\"
    registrar(f"CURTO_VAL_{amostra}_n", "Tabela 2 (validacao)", f"pares em {amostra}", inteiro(n), cp.A8_GAP, loc_n, n, "inteiro", trecho)
    registrar(f"CURTO_VAL_{amostra}_homolog", "Tabela 2 (validacao)", f"homologacao em {amostra}", pontos(dh), cp.A8_GAP, loc_dh, dh, "proporcao x100, 1 casa", trecho)
    registrar(f"CURTO_VAL_{amostra}_ativo", "Tabela 2 (validacao)", f"presenca ativa em {amostra}", pontos(da), cp.A8_GAP, loc_da, da, "proporcao x100, 1 casa", trecho)

for rotulo, amostra in [("Placebo & Imediatamente abaixo do cutoff, 2025", "placebo_abaixo_gap_1_ac"),
                        ("Placebo & Imediatamente acima do cutoff, 2025", "placebo_acima_gap_1_ac")]:
    filtro_h = {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra, "desfecho": "homologacao_mesma_celula"}
    filtro_a = {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra, "desfecho": "ativo_mesma_celula_snapshot"}
    n, loc_n = csv_valor(cp.A8_PLACEBO, filtro_h, "n_pares")
    dh, loc_dh = csv_valor(cp.A8_PLACEBO, filtro_h, "diferenca")
    da, loc_da = csv_valor(cp.A8_PLACEBO, filtro_a, "diferenca")
    trecho = f"{rotulo} & {inteiro(n)} & {pontos(dh)} & {pontos(da)} \\\\"
    registrar(f"CURTO_VAL_{amostra}_n", "Tabela 2 (validacao)", f"pares em {amostra}", inteiro(n), cp.A8_PLACEBO, loc_n, n, "inteiro", trecho)
    registrar(f"CURTO_VAL_{amostra}_homolog", "Tabela 2 (validacao)", f"homologacao em {amostra}", pontos(dh), cp.A8_PLACEBO, loc_dh, dh, "proporcao x100, 1 casa", trecho)
    registrar(f"CURTO_VAL_{amostra}_ativo", "Tabela 2 (validacao)", f"presenca ativa em {amostra}", pontos(da), cp.A8_PLACEBO, loc_da, da, "proporcao x100, 1 casa", trecho)

rep = {"ciclo_chamada": "2026_C2_CH2", "amostra": "gap_1_ac_replicacao", "desfecho": "ativo_mesma_celula_snapshot"}
rep_n, loc_rn = csv_valor(cp.A8_ESTIM, rep, "n_pares")
rep_d, loc_rd = csv_valor(cp.A8_ESTIM, rep, "diferenca")
rep_lo, loc_rl = csv_valor(cp.A8_ESTIM, rep, "ic95_convencional_inferior")
rep_hi, loc_rh = csv_valor(cp.A8_ESTIM, rep, "ic95_convencional_superior")
rep_p, loc_rp = csv_valor(cp.A8_ESTIM, rep, "p_exato_pareado_bicaudal")
rep_disc, loc_rdisc = csv_valor(cp.A8_ESTIM, rep, "discordantes_favoraveis")
trecho_rep_tab = f"Replicação & Gap de exatamente 1 ponto, 2026 & {inteiro(rep_n)} & --- & {pontos(rep_d)} \\\\"
registrar("CURTO_VAL_REP2026_n", "Tabela 2 (validacao)", "pares da replicacao", inteiro(rep_n), cp.A8_ESTIM, loc_rn, rep_n, "inteiro", trecho_rep_tab)
registrar("CURTO_VAL_REP2026_ativo", "Tabela 2 (validacao)", "presenca ativa na replicacao", pontos(rep_d), cp.A8_ESTIM, loc_rd, rep_d, "proporcao x100, 1 casa", trecho_rep_tab)
registrar("CURTO_TXT_REP2026_N", "Secao 2.1", "pares da replicacao", inteiro(rep_n), cp.A8_ESTIM, loc_rn, rep_n, "inteiro",
          f"Em 2026, {inteiro(rep_n)} pares atendem ao mesmo critério")
registrar("CURTO_TXT_REP2026_DIF", "Secao 2.4", "presenca ativa na replicacao", pontos(rep_d), cp.A8_ESTIM, loc_rd, rep_d, "proporcao x100, 1 casa",
          f"a diferença de presença ativa no mesmo curso--CNES é de {pontos(rep_d)} pontos percentuais, próxima da estimativa de 2025")
trecho_rep_nota = (f"tem intervalo convencional de {pontos(rep_lo)} a {pontos(rep_hi)} pontos percentuais e teste exato de "
                   f"{p_texto(rep_p)}, com {inteiro(rep_disc)} pares discordantes")
for chave, bruto, loc, fmt, tr in [("IC_LO", rep_lo, loc_rl, pontos(rep_lo), "proporcao x100, 1 casa"),
                                   ("IC_HI", rep_hi, loc_rh, pontos(rep_hi), "proporcao x100, 1 casa"),
                                   ("P", rep_p, loc_rp, p_texto(rep_p), "p exato, 3 casas"),
                                   ("DISC", rep_disc, loc_rdisc, inteiro(rep_disc), "inteiro")]:
    registrar(f"CURTO_VAL_REP2026_{chave}", "Tabela 2 (nota)", f"replicacao 2026: {chave}", fmt, cp.A8_ESTIM, loc, bruto, tr, trecho_rep_nota)
registrar("CURTO_TXT_REP2026_DISC", "Secao 2.4", "discordantes da replicacao", inteiro(rep_disc), cp.A8_ESTIM, loc_rdisc, rep_disc, "inteiro",
          f"porque há apenas {inteiro(rep_disc)} pares discordantes")

# Empates no texto.
emp = {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": "empate_descritivo_nao_causal"}
emp_h, loc_eh = csv_valor(cp.A8_GAP, {**emp, "desfecho": "homologacao_mesma_celula"}, "diferenca")
emp_a, loc_ea = csv_valor(cp.A8_GAP, {**emp, "desfecho": "ativo_mesma_celula_snapshot"}, "diferenca")
trecho_emp = f"mostram {pontos(emp_h)} e {pontos(emp_a)} pontos percentuais"
registrar("CURTO_TXT_EMPATES_H", "Secao 2.4", "empates: homologacao", pontos(emp_h), cp.A8_GAP, loc_eh, emp_h, "proporcao x100, 1 casa", trecho_emp)
registrar("CURTO_TXT_EMPATES_A", "Secao 2.4", "empates: presenca ativa", pontos(emp_a), cp.A8_GAP, loc_ea, emp_a, "proporcao x100, 1 casa", trecho_emp)

# Intervalo exato da segunda chamada de 2025 (errata E-1).
ch2 = {"ciclo_chamada": "2025_C1_CH2", "amostra": "gap_1_ac", "desfecho": "homologacao_mesma_celula"}
ex_lo, loc_xl = csv_valor(A8_TAB06, ch2, "ic95_exato_inferior")
ex_hi, loc_xh = csv_valor(A8_TAB06, ch2, "ic95_exato_superior")
ex_p, loc_xp = csv_valor(A8_TAB06, ch2, "p_exato_pareado_bicaudal")
fora, loc_fora = csv_valor(A8_TAB06, ch2, "ic95_convencional_fora_do_espaco")
if not bool(fora):
    raise SystemExit("A8_tabela_06: a linha da segunda chamada deixou de ter intervalo convencional fora do espaco; revisar o texto")
trecho_exato = (f"de {pontos(ex_lo)} a {pontos(ex_hi)} pontos percentuais, cobre o zero e é coerente com o $p$ exato de {decimal_br(ex_p, 4)}")
for chave, bruto, loc, fmt, tr in [("LO", ex_lo, loc_xl, pontos(ex_lo), "proporcao x100, 1 casa"),
                                   ("HI", ex_hi, loc_xh, pontos(ex_hi), "proporcao x100, 1 casa"),
                                   ("P", ex_p, loc_xp, decimal_br(ex_p, 4), "p exato, 4 casas")]:
    registrar(f"CURTO_A8_CH2_EXATO_{chave}", "Secao 2.3", f"intervalo exato CH2: {chave}", fmt, A8_TAB06, loc, bruto, tr, trecho_exato)

# ------------------------------------------------------------- A4: artigo curto

metro, loc_m = csv_valor(cp.A4_LPM, {"termo": "estrato_metropolitano"}, "coef")
registrar("CURTO_RESUMO_A4", "Resumo", "contraste metropolitano", pontos(metro), cp.A4_LPM, loc_m, metro, "proporcao x100, 1 casa",
          f"é {pontos(metro)} pontos percentuais maior em células metropolitanas")
wild = {}
for estr, termo in [("metropolitano", "estrato_metropolitano"), ("capital", "estrato_capital"), ("interior próximo", "estrato_interior_proximo_polo")]:
    wild[estr] = csv_valor(A4_WILD, {"termo": termo}, "p_wild_cluster")
trecho_wild = (f"os valores $p$ são {decimal_br(wild['metropolitano'][0], 4)} para metropolitano, {decimal_br(wild['capital'][0], 4)} para capital "
               f"e {decimal_br(wild['interior próximo'][0], 4)} para interior próximo")
for estr, (bruto, loc) in wild.items():
    registrar(f"CURTO_A4_WILD_{estr.replace(' ', '_')}", "Secao 3", f"p wild cluster {estr}", decimal_br(bruto, 4), A4_WILD, loc, bruto, "p bootstrap, 4 casas", trecho_wild)
b_rep, loc_b = csv_valor(A4_WILD, {"termo": "estrato_metropolitano"}, "b_replicacoes")
registrar("CURTO_A4_WILD_B", "Secao 3", "replicacoes do bootstrap", cp.milhar(b_rep), A4_WILD, loc_b, b_rep, "inteiro com ponto de milhar",
          f"por município e {cp.milhar(b_rep)} replicações")
mde_ante, loc_ma = csv_valor(A4_MDE, {"estrato": "metropolitano"}, "mde_ex_ante_A3_p80_p30")
mde_post, loc_mp = csv_valor(A4_MDE, {"estrato": "metropolitano"}, "mde_ex_post_p80")
trecho_mde = (f"era de {pontos(mde_ante)} pontos percentuais; o ex-post, calculado do erro-padrão realizado, é de {pontos(mde_post)} pontos percentuais")
registrar("CURTO_A4_MDE_ANTE", "Secao 3", "MDE ex-ante metropolitano", pontos(mde_ante), A4_MDE, loc_ma, mde_ante, "proporcao x100, 1 casa", trecho_mde)
registrar("CURTO_A4_MDE_POST", "Secao 3", "MDE ex-post metropolitano", pontos(mde_post), A4_MDE, loc_mp, mde_post, "proporcao x100, 1 casa", trecho_mde)

# ------------------------------------------------------------- A5: artigo curto

pp = "modelos/principal_proporcional_confirmatorio"
pn = "modelos/principal_dinamico_confirmatorio"
beta_p, loc_bp = json_valor(cp.A5_JSON, f"{pp}/mar2026_beta")
se_p, loc_sp = json_valor(cp.A5_JSON, f"{pp}/mar2026_se")
p_p, loc_pp_ = json_valor(cp.A5_JSON, f"{pp}/mar2026_p")
registrar("CURTO_RESUMO_A5", "Resumo", "estoque proporcional em marco/2026", decimal_br(beta_p, 3), cp.A5_JSON, loc_bp, beta_p, "3 casas",
          f"é {decimal_br(beta_p, 3)} log-ponto maior")
trecho_a5_tab_p = (f"Atração da célula (primário) & proporcional & {decimal_br(beta_p, 3)} & {decimal_br(se_p, 3)} & "
                   f"{cp.p_menor_que(p_p, 0.001, '$<$0,001')} \\\\")
registrar("CURTO_A5_TAB_PROP_beta", "Tabela 4 (CNES)", "beta proporcional", decimal_br(beta_p, 3), cp.A5_JSON, loc_bp, beta_p, "3 casas", trecho_a5_tab_p)
registrar("CURTO_A5_TAB_PROP_se", "Tabela 4 (CNES)", "EP proporcional", decimal_br(se_p, 3), cp.A5_JSON, loc_sp, se_p, "3 casas", trecho_a5_tab_p)
registrar("CURTO_A5_TAB_PROP_p", "Tabela 4 (CNES)", "p proporcional", "$<$0,001", cp.A5_JSON, loc_pp_, p_p, "p < 0,001", trecho_a5_tab_p)
ev = {"amostra": "confirmatoria_587", "competencia": "202603"}
beta_n, loc_bn = csv_valor(cp.A5_EVENTO, ev, "beta")
se_n, loc_sn = csv_valor(cp.A5_EVENTO, ev, "se_cluster")
p_n, loc_pn_ = csv_valor(cp.A5_EVENTO, ev, "p_valor")
trecho_a5_tab_n = f"Atração da célula (sensibilidade) & nível & {decimal_br(beta_n, 2)} & {decimal_br(se_n, 2)} & {decimal_br(p_n, 3)} \\\\"
registrar("CURTO_A5_TAB_NIVEL_beta", "Tabela 4 (CNES)", "beta nivel", decimal_br(beta_n, 2), cp.A5_EVENTO, loc_bn, beta_n, "2 casas", trecho_a5_tab_n)
registrar("CURTO_A5_TAB_NIVEL_se", "Tabela 4 (CNES)", "EP nivel", decimal_br(se_n, 2), cp.A5_EVENTO, loc_sn, se_n, "2 casas", trecho_a5_tab_n)
registrar("CURTO_A5_TAB_NIVEL_p", "Tabela 4 (CNES)", "p nivel", decimal_br(p_n, 3), cp.A5_EVENTO, loc_pn_, p_n, "3 casas", trecho_a5_tab_n)
q_p, loc_qp = json_valor(cp.A5_JSON, "multiplicidade/mar2026_q_fdr_bh_gl_fe_proporcional_confirmatoria")
q_n, loc_qn = json_valor(cp.A5_JSON, "multiplicidade/mar2026_q_fdr_bh_gl_fe_nivel_confirmatoria")
registrar("CURTO_A5_Q_PROP", "Secao 4", "q FDR proporcional", decimal_br(q_p, 4), cp.A5_JSON, loc_qp, q_p, "4 casas",
          f"valor $q$ de Benjamini--Hochberg desse coeficiente é {decimal_br(q_p, 4)}")
registrar("CURTO_A5_Q_NIVEL", "Secao 4", "q FDR nivel", decimal_br(q_n, 3), cp.A5_JSON, loc_qn, q_n, "3 casas",
          f"seu valor $q$ é {decimal_br(q_n, 3)}")

# C-7: placebo, pre-tendencia e deslocamento.
def c7(caminho: str) -> tuple[Any, str]:
    return json_valor(A5_C7, caminho)

pl_p_b, l1 = c7("placebo/resultado/proporcional/mar2026_beta")
pl_p_se, l2 = c7("placebo/resultado/proporcional/mar2026_se_gl_fe")
pl_p_p, l3 = c7("placebo/resultado/proporcional/mar2026_p_gl_fe")
pl_n_b, l4 = c7("placebo/resultado/nivel/mar2026_beta")
pl_n_se, l5 = c7("placebo/resultado/nivel/mar2026_se_gl_fe")
pl_n_p, l6 = c7("placebo/resultado/nivel/mar2026_p_gl_fe")
trecho_pl_p = (f"Placebo: município com atração, célula sem & proporcional & {decimal_br(pl_p_b, 4)} & {decimal_br(pl_p_se, 3)} & {p_texto(pl_p_p)} \\\\")
trecho_pl_n = (f"Placebo: município com atração, célula sem & nível & {decimal_br(pl_n_b, 3)} & {decimal_br(pl_n_se, 3)} & {p_texto(pl_n_p)} \\\\")
for chave, bruto, loc, fmt, tr in [("PROP_beta", pl_p_b, l1, decimal_br(pl_p_b, 4), trecho_pl_p), ("PROP_se", pl_p_se, l2, decimal_br(pl_p_se, 3), trecho_pl_p),
                                   ("PROP_p", pl_p_p, l3, p_texto(pl_p_p), trecho_pl_p), ("NIVEL_beta", pl_n_b, l4, decimal_br(pl_n_b, 3), trecho_pl_n),
                                   ("NIVEL_se", pl_n_se, l5, decimal_br(pl_n_se, 3), trecho_pl_n), ("NIVEL_p", pl_n_p, l6, p_texto(pl_n_p), trecho_pl_n)]:
    registrar(f"CURTO_C7_PLACEBO_{chave}", "Tabela 4 (CNES)", f"placebo {chave}", fmt, A5_C7, loc, bruto, "arredondamento do artigo", tr)
registrar("CURTO_C7_PLACEBO_TXT_N", "Secao 4", "placebo nivel no texto", decimal_br(pl_n_b, 3), A5_C7, l4, pl_n_b, "3 casas",
          f"com {decimal_br(pl_n_b, 3)} em nível e {decimal_br(pl_p_b, 4)} na escala proporcional")
registrar("CURTO_C7_PLACEBO_TXT_P", "Secao 4", "placebo proporcional no texto", decimal_br(pl_p_b, 4), A5_C7, l1, pl_p_b, "4 casas",
          f"com {decimal_br(pl_n_b, 3)} em nível e {decimal_br(pl_p_b, 4)} na escala proporcional")
n_trat, l7 = c7("placebo/resultado/nivel/n_tratadas")
n_ctrl, l8 = c7("placebo/resultado/nivel/n_controle")
tr_trat, l9 = c7("deslocamento/transbordo/nivel/n_tratadas")
tr_ctrl, l10 = c7("deslocamento/transbordo/nivel/n_controle")
trecho_n = (f"são as {inteiro(n_trat + n_ctrl)} células sem atração; no placebo, {inteiro(n_trat)} estão em municípios com atração em alguma célula "
            f"e {inteiro(n_ctrl)} em municípios sem nenhuma; no transbordo, {inteiro(tr_trat)} têm")
if int(tr_trat + tr_ctrl) != int(n_trat + n_ctrl):
    raise SystemExit("C-7: placebo e transbordo deveriam partilhar as mesmas celulas sem atracao")
for chave, bruto, loc in [("TOTAL", n_trat + n_ctrl, f"soma: {l7} + {l8}"), ("TRAT", n_trat, l7), ("CTRL", n_ctrl, l8), ("TRANSBORDO", tr_trat, l9)]:
    registrar(f"CURTO_C7_N_{chave}", "Tabela 4 (nota)", f"contagem {chave}", inteiro(bruto), A5_C7, loc, bruto, "inteiro", trecho_n)
tb_b, l11 = c7("deslocamento/transbordo/proporcional/mar2026_beta")
tb_se, l12 = c7("deslocamento/transbordo/proporcional/mar2026_se_gl_fe")
tb_p, l13 = c7("deslocamento/transbordo/proporcional/mar2026_p_gl_fe")
trecho_tb = f"Transbordo: vizinho da região com atração & proporcional & {decimal_br(tb_b, 3)} & {decimal_br(tb_se, 3)} & {p_texto(tb_p)} \\\\"
for chave, bruto, loc, fmt in [("beta", tb_b, l11, decimal_br(tb_b, 3)), ("se", tb_se, l12, decimal_br(tb_se, 3)), ("p", tb_p, l13, p_texto(tb_p))]:
    registrar(f"CURTO_C7_TRANSBORDO_{chave}", "Tabela 4 (CNES)", f"transbordo {chave}", fmt, A5_C7, loc, bruto, "3 casas", trecho_tb)
rg_b, l14 = c7("deslocamento/oferta_liquida_regional/proporcional/mar2026_beta")
rg_se, l15 = c7("deslocamento/oferta_liquida_regional/proporcional/mar2026_se_gl_fe")
rg_p, l16 = c7("deslocamento/oferta_liquida_regional/proporcional/mar2026_p_gl_fe")
n_reg, l17 = c7("deslocamento/n_regioes")
trecho_rg = f"Oferta líquida por região--curso & proporcional & {decimal_br(rg_b, 3)} & {decimal_br(rg_se, 3)} & {p_texto(rg_p)} \\\\"
for chave, bruto, loc, fmt in [("beta", rg_b, l14, decimal_br(rg_b, 3)), ("se", rg_se, l15, decimal_br(rg_se, 3)), ("p", rg_p, l16, p_texto(rg_p))]:
    registrar(f"CURTO_C7_REGIONAL_{chave}", "Tabela 4 (CNES)", f"oferta liquida regional {chave}", fmt, A5_C7, loc, bruto, "3 casas", trecho_rg)
trecho_rg_txt = f"sobe {decimal_br(rg_b, 3)} log-ponto com $p$ de {p_texto(rg_p)} em {inteiro(n_reg)} regiões"
registrar("CURTO_C7_REGIONAL_TXT_beta", "Secao 4", "oferta liquida regional no texto", decimal_br(rg_b, 3), A5_C7, l14, rg_b, "3 casas", trecho_rg_txt)
registrar("CURTO_C7_REGIONAL_TXT_p", "Secao 4", "p regional no texto", p_texto(rg_p), A5_C7, l16, rg_p, "3 casas", trecho_rg_txt)
registrar("CURTO_C7_REGIONAL_TXT_n", "Secao 4", "regioes", inteiro(n_reg), A5_C7, l17, n_reg, "inteiro", trecho_rg_txt)
# C-7c: a subamostra informativa do teste de oferta liquida e as contagens que
# dizem por que as demais regiao-curso nao informam nada sobre realocacao.
rgm_b, l22 = c7("deslocamento/decomposicao_oferta_liquida/multi_municipio/proporcional/mar2026_beta")
rgm_se, l23 = c7("deslocamento/decomposicao_oferta_liquida/multi_municipio/proporcional/mar2026_se_gl_fe")
rgm_p_, l24 = c7("deslocamento/decomposicao_oferta_liquida/multi_municipio/proporcional/mar2026_p_gl_fe")
n_multi, l25 = c7("deslocamento/decomposicao_oferta_liquida/n_regiao_curso_multi_municipio")
n_uni, l26 = c7("deslocamento/decomposicao_oferta_liquida/n_regiao_curso_um_municipio")
n_rc, l27 = c7("deslocamento/n_regiao_curso")
if int(n_multi) + int(n_uni) != int(n_rc):
    raise SystemExit("C-7c: as duas subamostras deveriam somar o total de regiao-curso")
trecho_rgm = (f"\\quad só as que agregam $>$1 município & proporcional & {decimal_br(rgm_b, 3)} & "
              f"{decimal_br(rgm_se, 3)} & {p_texto(rgm_p_)} \\\\")
for chave, bruto, loc, fmt in [("beta", rgm_b, l22, decimal_br(rgm_b, 3)), ("se", rgm_se, l23, decimal_br(rgm_se, 3)), ("p", rgm_p_, l24, p_texto(rgm_p_))]:
    registrar(f"CURTO_C7_REGIONAL_MULTI_{chave}", "Tabela 4 (CNES)", f"oferta liquida, so multi-municipio: {chave}", fmt, A5_C7, loc, bruto, "3 casas", trecho_rgm)
trecho_rgm_nota = (f"das {inteiro(n_rc)} região--curso, {inteiro(n_uni)} contêm um único município do quadro, e nelas o agregado "
                   f"regional é a própria célula, de modo que só as {inteiro(n_multi)} restantes distinguem oferta líquida de oferta da célula")
for chave, bruto, loc in [("TOTAL", n_rc, l27), ("UNI", n_uni, l26), ("MULTI", n_multi, l25)]:
    registrar(f"CURTO_C7_REGIONAL_NOTA_{chave}", "Tabela 4 (nota)", f"regiao-curso {chave}", inteiro(bruto), A5_C7, loc, bruto, "inteiro", trecho_rgm_nota)
trecho_rgm_txt = (f"das {inteiro(n_rc)} região--curso, {inteiro(n_uni)} contêm um único município do quadro, e nelas o agregado regional "
                  f"é a própria célula; restrito às {inteiro(n_multi)} que de fato agregam mais de um município, o coeficiente é "
                  f"{decimal_br(rgm_b, 3)}, com $p$ de {p_texto(rgm_p_)}")
registrar("CURTO_C7_REGIONAL_MULTI_TXT_beta", "Secao 4", "oferta liquida multi-municipio no texto", decimal_br(rgm_b, 3), A5_C7, l22, rgm_b, "3 casas", trecho_rgm_txt)
registrar("CURTO_C7_REGIONAL_MULTI_TXT_p", "Secao 4", "p multi-municipio no texto", p_texto(rgm_p_), A5_C7, l24, rgm_p_, "3 casas", trecho_rgm_txt)
registrar("CURTO_C7_REGIONAL_MULTI_TXT_n", "Secao 4", "regiao-curso que agregam", inteiro(n_multi), A5_C7, l25, n_multi, "inteiro", trecho_rgm_txt)

# C-7b: multiplicidade na triagem de pre-tendencia por curso.
q16, l28 = c7("pretendencia_por_curso/multiplicidade/q_por_curso/proporcional/16")
q2, l29 = c7("pretendencia_por_curso/multiplicidade/q_por_curso/proporcional/2")
alpha_pre, l30 = c7("pretendencia_por_curso/multiplicidade/alpha")
cursos_q, l31 = c7("pretendencia_por_curso/multiplicidade/cursos_q_lt_0_05_proporcional")
if cursos_q != [16]:
    raise SystemExit(f"C-7b: o artigo curto cita so o curso 16 sobrevivendo ao q; o artefato traz {cursos_q}")
trecho_q = (f"só o curso {cursos_q[0]} mantém $q$ abaixo de {decimal_br(alpha_pre, 2)} na escala proporcional, com "
            f"{decimal_br(q16, 4)}, enquanto o curso 2 vai a {decimal_br(q2, 3)}")
registrar("CURTO_C7_Q_CURSO16", "Secao 4", "q BH do curso 16", decimal_br(q16, 4), A5_C7, l28, q16, "4 casas", trecho_q)
registrar("CURTO_C7_Q_CURSO2", "Secao 4", "q BH do curso 2", decimal_br(q2, 3), A5_C7, l29, q2, "3 casas", trecho_q)
registrar("CURTO_C7_Q_ALPHA", "Secao 4", "alfa do protocolo", decimal_br(alpha_pre, 2), A5_C7, l30, alpha_pre, "2 casas", trecho_q)
registrar("CURTO_C7_Q_CURSOS", "Secao 4", "cursos com q<alfa", str(cursos_q[0]), A5_C7, l31, cursos_q, "lista", trecho_q)

cursos_rej, l18 = c7("pretendencia_por_curso/cursos_pre_p_lt_0_05_proporcional")
if len(cursos_rej) != 2:
    raise SystemExit(f"C-7: o texto do artigo curto cita dois cursos rejeitados; o artefato traz {cursos_rej}")
trecho_cursos = f"rejeita a 5\\% nos cursos {cursos_rej[0]} e {cursos_rej[1]} na escala proporcional"
registrar("CURTO_C7_CURSOS_REJ", "Secao 4", "cursos com pre-p<0,05", " e ".join(str(c) for c in cursos_rej), A5_C7, l18, cursos_rej, "lista", trecho_cursos)
sx_b, l19 = c7("pretendencia_por_curso/sensibilidade_excluindo_cursos_rejeitados/proporcional/mar2026_beta")
sx_p, l20 = c7("pretendencia_por_curso/sensibilidade_excluindo_cursos_rejeitados/proporcional/mar2026_p_gl_fe")
sx_n, l21 = c7("pretendencia_por_curso/sensibilidade_excluindo_cursos_rejeitados/proporcional/n_unidades")
trecho_sx = f"é {decimal_br(sx_b, 3)}, com $p$ de {decimal_br(sx_p, 4)}, sobre {inteiro(sx_n)} células"
registrar("CURTO_C7_EXCL_beta", "Secao 4", "beta excluindo cursos rejeitados", decimal_br(sx_b, 3), A5_C7, l19, sx_b, "3 casas", trecho_sx)
registrar("CURTO_C7_EXCL_p", "Secao 4", "p excluindo cursos rejeitados", decimal_br(sx_p, 4), A5_C7, l20, sx_p, "4 casas", trecho_sx)
registrar("CURTO_C7_EXCL_n", "Secao 4", "celulas excluindo cursos rejeitados", inteiro(sx_n), A5_C7, l21, sx_n, "inteiro", trecho_sx)


# ------------------------------------------------------- RDD da bolsa (E3, E5)

# Regra: cortes do protocolo; o lado inferior inclui o corte, de modo que a
# Faixa 2 comeca no milesimo seguinte.
cortes, loc_cortes = json_valor(RDD_E3_STATUS, "cortes")
if [round(float(c), 3) for c in cortes] != [0.3, 0.4]:
    raise SystemExit(f"E3: o artigo curto cita os cortes 0,300 e 0,400; o artefato traz {cortes}")
c1, c2 = (float(c) for c in cortes)
trecho_regra = (f"até {decimal_br(c1, 3)}, Faixa 3; de {decimal_br(c1 + 0.001, 3)} a {decimal_br(c2, 3)}, Faixa 2; "
                f"acima de {decimal_br(c2, 3)}, Faixa 1")
registrar("CURTO_RDD_REGRA_CORTES", "Secao 3.1", "cortes da regra", f"{decimal_br(c1, 3)} e {decimal_br(c2, 3)}", RDD_E3_STATUS,
          loc_cortes, cortes, "3 casas; Faixa 2 comeca no milesimo seguinte ao corte", trecho_regra)
h_princ, loc_h = json_valor(RDD_E3_STATUS, "janelas/principal")
registrar("CURTO_RDD_JANELA", "Secao 3.2", "janela principal", decimal_br(h_princ, 3), RDD_E3_STATUS, loc_h, h_princ, "3 casas",
          f"janela de {decimal_br(h_princ, 3)} de IVS de cada lado do corte")

# Primeiro estagio: escore do MS = IVS oficial; regra reproduzida por inteiro.
iguais, loc_ig = json_valor(RDD_R1, "escore_administrativo_e_ivs_2010_oficial/valores_iguais_3_casas")
n_ig, d_ig = (int(x) for x in str(iguais).split("/"))
p1_n, loc_p1 = json_valor(RDD_R1, "populacoes/P1/municipios")
p1_r, _ = json_valor(RDD_R1, "populacoes/P1/regra_reproduz")
p2_n, loc_p2 = json_valor(RDD_R1, "populacoes/P2/municipios")
p2_r, _ = json_valor(RDD_R1, "populacoes/P2/regra_reproduz")
if n_ig != d_ig or p1_r != p1_n or p2_r != p2_n:
    raise SystemExit("R1: o artigo curto afirma reproducao integral da regra e do escore; o artefato diverge")
registrar("CURTO_RDD_ESCORE_MS", "Secao 3.1", "escore do MS igual ao IVS oficial", inteiro(n_ig), RDD_R1, loc_ig, iguais, "inteiro",
          f"coincide com o IVS 2010 oficial nos {inteiro(n_ig)} municípios em que aparece")
trecho_regra_n = (f"a regra reproduz a faixa anunciada nos {inteiro(p1_n)} municípios do quadro da primeira chamada do ciclo 1 "
                  f"e nos {inteiro(p2_n)} do ciclo 2")
registrar("CURTO_RDD_REGRA_P1", "Secao 3.1", "municipios do ciclo 1 com regra reproduzida", inteiro(p1_n), RDD_R1, loc_p1, p1_n, "inteiro", trecho_regra_n)
registrar("CURTO_RDD_REGRA_P2", "Secao 3.1", "municipios do ciclo 2 com regra reproduzida", inteiro(p2_n), RDD_R1, loc_p2, p2_n, "inteiro", trecho_regra_n)

# Densidade no ciclo 1.
dens = {}
for c in (c1, c2):
    filtro = {"populacao": "P1", "diagnostico": "densidade_poisson_mass_points", "h": str(h_princ), "corte": str(c)}
    dens[c] = {campo: csv_valor(RDD_E3_DIAG, filtro, campo) for campo in ("rho", "rho_ic95_inf", "rho_ic95_sup")}
trecho_dens = (f"com razões de {decimal_br(dens[c1]['rho'][0], 2)} [{decimal_br(dens[c1]['rho_ic95_inf'][0], 2)}; "
               f"{decimal_br(dens[c1]['rho_ic95_sup'][0], 2)}] em {decimal_br(c1, 3)} e de {decimal_br(dens[c2]['rho'][0], 2)} "
               f"[{decimal_br(dens[c2]['rho_ic95_inf'][0], 2)}; {decimal_br(dens[c2]['rho_ic95_sup'][0], 2)}] em {decimal_br(c2, 3)}")
for c in (c1, c2):
    for campo, (bruto, loc) in dens[c].items():
        registrar(f"CURTO_RDD_DENS_{decimal_br(c, 3)}_{campo}", "Secao 3.1", f"densidade {campo} em {c}", decimal_br(bruto, 2),
                  RDD_E3_DIAG, loc, bruto, "2 casas", trecho_dens)

# Balanco: o IVS 2010 oficial e a propria running variable e nao entra na contagem.
diag = pd.read_csv(ROOT / RDD_E3_DIAG)
bal = diag[diag["diagnostico"].eq("balanco_covariavel_pre") & diag["populacao"].eq("P1")
           & diag["h"].round(3).eq(round(float(h_princ), 3)) & diag["variavel"].ne("ivs_2010")]
n_cov = {c: int(bal["corte"].round(3).eq(round(c, 3)).sum()) for c in (c1, c2)}
n_rej = {c: int((bal["corte"].round(3).eq(round(c, 3)) & bal["p_valor"].lt(0.05)).sum()) for c in (c1, c2)}
if n_cov != {c1: 9, c2: 9} or n_rej != {c1: 0, c2: 3}:
    raise SystemExit(f"E3: o artigo curto cita 9 covariaveis, 0 e 3 com p<0,05; o artefato traz {n_cov} e {n_rej}")
registrar("CURTO_RDD_BALANCO", "Secao 3.1", "covariaveis com p<0,05 por corte (ciclo 1)", "nove; nenhuma; três", RDD_E3_DIAG,
          "balanco_covariavel_pre, P1, sem ivs_2010", f"{n_cov}; {n_rej}", "contagem por extenso",
          "No balanço de nove covariáveis anteriores ao programa, nenhuma difere a 5\\% no corte de 0,300; no de 0,400, três diferem")

# Tabela do E3: desfecho da hipotese e presenca, janela principal.
FRACAO = "fracao_celulas_ch1_com_confirmacao_ou_homologacao"
PRESENCA = "D_k_especialista_ativo_do_ciclo"
e3 = {}
for rotulo, outcome, pop in [("Células preenchidas, ciclo 1", FRACAO, "P1"), ("Presença, ciclo 1", PRESENCA, "P1"),
                             ("Presença, ciclo 2", PRESENCA, "P2")]:
    for c in (c1, c2):
        filtro = {"populacao": pop, "outcome": outcome, "corte": str(c), "h": str(h_princ), "especificacao": "principal"}
        v = {campo: csv_valor(RDD_E3_ESTIM, filtro, campo) for campo in
             ("n_abaixo", "n_acima", "media_bruta_abaixo", "media_bruta_acima", "tau", "ic95_inf", "ic95_sup", "p_valor")}
        e3[(outcome, pop, c)] = v
        trecho = (f"{rotulo} & {decimal_br(c, 3)} & {inteiro(v['n_abaixo'][0])}/{inteiro(v['n_acima'][0])} & "
                  f"{pontos(v['media_bruta_abaixo'][0])} & {pontos(v['media_bruta_acima'][0])} & {pontos(v['tau'][0])} & "
                  f"[{pontos(v['ic95_inf'][0])}; {pontos(v['ic95_sup'][0])}] & {p_texto(v['p_valor'][0])} \\\\")
        for campo, (bruto, loc) in v.items():
            fmt = (inteiro(bruto) if campo.startswith("n_") else p_texto(bruto) if campo == "p_valor" else pontos(bruto))
            registrar(f"CURTO_RDD_TAB_{pop}_{outcome[:8]}_{decimal_br(c, 3)}_{campo}", "Tabela da bolsa", f"{campo} {outcome} {pop} {c}",
                      fmt, RDD_E3_ESTIM, loc, bruto, "proporcao x100, 1 casa; p com 3 casas; n inteiro", trecho)

y03, y04 = e3[(FRACAO, "P1", c1)], e3[(FRACAO, "P1", c2)]
trecho_resumo = (f"primeira chamada é de {pontos(y03['tau'][0])} pontos percentuais no corte de {decimal_br(c1, 3)} e de "
                 f"{pontos(y04['tau'][0])} no de {decimal_br(c2, 3)}")
trecho_txt = (f"o salto é de {pontos(y03['tau'][0])} pontos percentuais no corte de {decimal_br(c1, 3)}, com intervalo de "
              f"[{pontos(y03['ic95_inf'][0])}; {pontos(y03['ic95_sup'][0])}], e de {pontos(y04['tau'][0])} no de {decimal_br(c2, 3)}, "
              f"com intervalo de [{pontos(y04['ic95_inf'][0])}; {pontos(y04['ic95_sup'][0])}]")
for c, v in ((c1, y03), (c2, y04)):
    registrar(f"CURTO_RDD_RESUMO_{decimal_br(c, 3)}", "Resumo", f"salto no preenchimento em {c}", pontos(v["tau"][0]), RDD_E3_ESTIM,
              v["tau"][1], v["tau"][0], "proporcao x100, 1 casa", trecho_resumo)
    for campo in ("tau", "ic95_inf", "ic95_sup"):
        registrar(f"CURTO_RDD_TXT_{decimal_br(c, 3)}_{campo}", "Secao 3.3", f"{campo} do preenchimento em {c}", pontos(v[campo][0]),
                  RDD_E3_ESTIM, v[campo][1], v[campo][0], "proporcao x100, 1 casa", trecho_txt)
trecho_medias = (f"a fração média é de {pontos(y03['media_bruta_abaixo'][0])}\\% abaixo e {pontos(y03['media_bruta_acima'][0])}\\% acima")
for campo in ("media_bruta_abaixo", "media_bruta_acima"):
    registrar(f"CURTO_RDD_TXT_MEDIA_{campo}", "Secao 3.3", f"{campo} do preenchimento em {c1}", pontos(y03[campo][0]), RDD_E3_ESTIM,
              y03[campo][1], y03[campo][0], "proporcao x100, 1 casa", trecho_medias)
ns = [int(y[k][0]) for y in (y03, y04) for k in ("n_abaixo", "n_acima")]
registrar("CURTO_RDD_TXT_N_FAIXA", "Secao 3.3", "municipios por lado na janela", f"{min(ns)} e {max(ns)}", RDD_E3_ESTIM,
          "n_abaixo e n_acima do preenchimento", ns, "minimo e maximo", f"há entre {min(ns)} e {max(ns)} municípios de cada lado")

# E5 (exploratorio): MDE do principal, fator de inflacao do EP, alternativas e limites.
s0 = {c: {campo: csv_valor(RDD_E5_ESPEC, {"outcome": "Y1", "especificacao": "S0", "corte": str(c)}, campo)
          for campo in ("mde_80", "lim_sup_unilateral_95")} for c in (c1, c2)}
trecho_mde = f"é de {pontos(s0[c1]['mde_80'][0])} e {pontos(s0[c2]['mde_80'][0])} pontos percentuais"
for c in (c1, c2):
    registrar(f"CURTO_RDD_MDE_{decimal_br(c, 3)}", "Secao 3.3", f"MDE do principal em {c}", pontos(s0[c]["mde_80"][0]), RDD_E5_ESPEC,
              s0[c]["mde_80"][1], s0[c]["mde_80"][0], "proporcao x100, 1 casa", trecho_mde)
razao = {c: csv_valor(RDD_E5_DECOMP, {"componente": "LL_triangular_principal", "corte": str(c)}, "razao_ep_vs_dm_simples") for c in (c1, c2)}
trecho_razao = (f"multiplica o erro-padrão por {decimal_br(razao[c1][0], 1)} e por {decimal_br(razao[c2][0], 1)} em relação a uma "
                f"diferença de médias simples")
for c in (c1, c2):
    registrar(f"CURTO_RDD_RAZAO_EP_{decimal_br(c, 3)}", "Secao 3.3", f"EP local linear / EP diferenca de medias em {c}",
              decimal_br(razao[c][0], 1), RDD_E5_DECOMP, razao[c][1], razao[c][0], "1 casa", trecho_razao)
e5 = pd.read_csv(ROOT / RDD_E5_ESPEC)
y1 = e5[e5["outcome"].eq("Y1")]
expl = y1[y1["rotulo"].eq("EXPLORATORIO_POS_RESULTADO")]
if (y1["p_valor"] < 0.05).any() or y1["descarta_tau_ge_010"].astype(bool).any():
    raise SystemExit("E5: o artigo curto afirma nenhum p<0,05 e nenhum descarte de +10 p.p.; o artefato diverge")
trecho_expl = (f"nenhuma das {len(expl)} especificações alternativas do desfecho da hipótese produz salto distinguível de zero; "
               f"o menor $p$ é {decimal_br(expl['p_valor'].min(), 2)}")
registrar("CURTO_RDD_E5_N", "Secao 3.3", "especificacoes exploratorias do preenchimento", inteiro(len(expl)), RDD_E5_ESPEC,
          "outcome=Y1, rotulo=EXPLORATORIO_POS_RESULTADO", len(expl), "contagem", trecho_expl)
registrar("CURTO_RDD_E5_PMIN", "Secao 3.3", "menor p das exploratorias", decimal_br(expl["p_valor"].min(), 2), RDD_E5_ESPEC,
          "min de p_valor nas exploratorias de Y1", float(expl["p_valor"].min()), "2 casas", trecho_expl)
lim_b, loc_lb = csv_valor(RDD_E5_ESPEC, {"outcome": "Y1", "especificacao": "B"}, "lim_sup_unilateral_95")
trecho_lim = (f"o limite superior unilateral de 95\\% do principal é de {pontos(s0[c1]['lim_sup_unilateral_95'][0])} pontos percentuais "
              f"no corte de {decimal_br(c1, 3)} e de {pontos(s0[c2]['lim_sup_unilateral_95'][0])} no de {decimal_br(c2, 3)}; com os cortes "
              f"empilhados, é de {pontos(lim_b)} para a média dos dois saltos")
for c in (c1, c2):
    registrar(f"CURTO_RDD_LIMSUP_{decimal_br(c, 3)}", "Secao 3.3", f"limite superior unilateral do principal em {c}",
              pontos(s0[c]["lim_sup_unilateral_95"][0]), RDD_E5_ESPEC, s0[c]["lim_sup_unilateral_95"][1],
              s0[c]["lim_sup_unilateral_95"][0], "proporcao x100, 1 casa", trecho_lim)
registrar("CURTO_RDD_LIMSUP_EMPILHADO", "Secao 3.3", "limite superior unilateral com cortes empilhados", pontos(lim_b), RDD_E5_ESPEC,
          loc_lb, lim_b, "proporcao x100, 1 casa", trecho_lim)


# ------------------------------------- RDD da bolsa: rodada multi-outcome (E6-E9)
# Os trechos com numero que o artigo curto repete do principal (Holm, descarte
# empilhado, nivel pre-existente no CNES, E9) sao os MO_* do conferidor
# principal, reutilizados abaixo em main(). Aqui ficam so as frases que o curto
# escreve de outro modo; as guardas do principal ja rodaram ao carrega-lo e sao
# repetidas onde a frase do curto depende delas.

MO_E8 = cp.MO_E8_RESUMO
seq_janela, loc_seq_j = cp.mo_e8("e7/f31_U_0300/maior_sequencia_p_menor_005/janela")
seq_inicio, loc_seq_i = cp.mo_e8("e7/f31_U_0300/maior_sequencia_p_menor_005/inicio")
primeiro_pos, loc_pp1 = cp.mo_e8("e7/f31_U_0300/primeiro_mes_pos")
depois_sig, loc_dsig = cp.mo_e8("e7/f31_U_0300/meses_pos_depois_da_sequencia_p_menor_005")
if seq_janela != ["pos"] or seq_inicio != primeiro_pos or int(depois_sig) != 0:
    raise SystemExit("E7: o curto diz que a sequencia de meses significativos comeca no pos e depois se desfaz")
registrar("CURTO_MO_E7_SEQUENCIA", "Secao 3.4", "sequencia de meses com p<0,05 em 0,300 no inicio do pos",
          "sequência no início do pós", MO_E8, f"{loc_seq_j}; {loc_seq_i}; {loc_pp1}; {loc_dsig}",
          [seq_janela, seq_inicio, primeiro_pos, depois_sig], "guarda: janela pos, inicio = 1o mes do pos, 0 depois",
          f"o corte de {decimal_br(c1, 3)} tem uma sequência de meses significativos logo no início do pós, que depois "
          f"se desfaz")
gen_sig, loc_gen = cp.mo_e8("e7/generalistas_U_0400/pre_extra_p_menor_005")
if int(gen_sig) <= 0:
    raise SystemExit("E7: o curto diz que o placebo de generalistas se desloca antes do pre principal")
registrar("CURTO_MO_E7_GENERALISTAS", "Secao 3.4", "placebo de generalistas com p<0,05 antes do pre principal (0,400)",
          "já se desloca", MO_E8, loc_gen, gen_sig, "guarda: > 0",
          f"no corte de {decimal_br(c2, 3)}, o placebo de generalistas já se desloca antes do pré principal")
alguma, loc_alg = cp.mo_e8("holm/alguma_rejeitada")
if alguma:
    raise SystemExit("E8: o resumo do curto diz que o segundo desenho nao detecta efeito")
registrar("CURTO_MO_RESUMO_NAO_DETECTA", "Resumo", "nenhuma primaria rejeitada pelo Holm", "não detecta", MO_E8,
          loc_alg, alguma, "guarda: False",
          "e não detecta efeito sobre preenchimento, presença ou oferta cadastrada")


# ------------------------------------------------------------------ execucao

# Numeros que aparecem no artigo curto sem serem cifra estimada: datas, lei,
# numeros de secao e rotulos. Sao inteiros e nao entram na cobertura decimal.
def main() -> None:
    if not TEX.exists():
        raise SystemExit(f"Arquivo do artigo ausente: {TEX}")
    tex = TEX.read_text(encoding="utf-8")
    tex_norm = re.sub(r"\s+", " ", tex)

    # 1. Trechos proprios do artigo curto.
    for r in REGISTROS:
        r["ocorrencias_no_tex"] = tex_norm.count(r["trecho_esperado_no_tex"])
        r["status"] = "OK" if r["ocorrencias_no_tex"] >= 1 else "DIVERGENTE"
        r["origem_registro"] = "artigo_curto"

    # 2. Trechos do conferidor principal reutilizados pelo artigo curto.
    reutilizados = []
    for r in cp.REGISTROS:
        occ = tex_norm.count(r["trecho_esperado_no_tex"])
        if occ >= 1:
            c = dict(r)
            c["id"] = f"REUSO_{r['id']}"
            c["ocorrencias_no_tex"] = occ
            c["status"] = "OK"
            c["origem_registro"] = "conferidor_principal"
            reutilizados.append(c)
    todos = REGISTROS + reutilizados

    ids = [r["id"] for r in todos]
    if len(ids) != len(set(ids)):
        raise SystemExit("Identificadores repetidos na conferencia do artigo curto")

    # 3. Cobertura: todo decimal com virgula no corpo tem de estar num trecho OK.
    corpo = cp.corpo_sem_bibliografia(tex)
    corpo = re.sub(r"\\(label|ref|includegraphics|cite[tp]?)\{[^}]*\}", " ", corpo)
    corpo_norm = re.sub(r"\s+", " ", corpo)
    trechos_ok = " || ".join(r["trecho_esperado_no_tex"] for r in todos if r["status"] == "OK")
    decimais = sorted(set(re.findall(r"(?<![\d,.])\d+,\d+(?![\d,])", corpo_norm)))
    sem_origem = []
    for d in decimais:
        if not re.search(r"(?<![\d,.])" + re.escape(d) + r"(?![\d,])", trechos_ok):
            sem_origem.append(d)

    quadro = pd.DataFrame(todos)[cp.CABECALHO + ["origem_registro"]].sort_values("id").reset_index(drop=True)
    tmp = CONFERENCIA_CSV.with_suffix(".csv.tmp")
    quadro.to_csv(tmp, index=False, encoding="utf-8")
    tmp.replace(CONFERENCIA_CSV)

    divergentes = quadro[quadro["status"].ne("OK")]
    problemas = cp.conferir_estrutura(tex)

    print(f"Numeros conferidos no artigo curto: {len(quadro)} "
          f"({len(REGISTROS)} proprios, {len(reutilizados)} reutilizados do conferidor principal)")
    print(f"Decimais distintos no corpo: {len(decimais)}; sem origem: {len(sem_origem)}")
    print(f"Mapeamento gravado em: {CONFERENCIA_CSV.relative_to(ROOT)}")
    print(f"Problemas estruturais: {len(problemas)}")
    for p in problemas:
        print(f"  - {p}")
    if len(divergentes):
        print("\nNumeros do artigo curto sem correspondencia na fonte:")
        for _, l in divergentes.iterrows():
            print(f"  - {l['id']}: esperava '{l['trecho_esperado_no_tex']}'")
    if sem_origem:
        print("\nDecimais no corpo sem trecho conferido que os contenha:")
        for d in sem_origem:
            print(f"  - {d}")
    if len(divergentes) or problemas or sem_origem:
        raise SystemExit(1)
    print("\nCONFERENCIA APROVADA: toda cifra do artigo curto corresponde a um artefato.")


if __name__ == "__main__":
    main()
