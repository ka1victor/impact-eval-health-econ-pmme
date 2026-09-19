"""Confere cada numero citado em paper_pmme_curto.tex contra os artefatos.

Mesma regra do artigo principal (`10_conferir_numeros_artigo.py`): nenhuma
cifra pode existir sem origem rastreavel em `output/`. Este script reutiliza os
leitores, formatadores e a conferencia estrutural do conferidor principal e
acrescenta as origens que so o artigo curto cita — intervalo exato de A8, wild
cluster bootstrap e MDE ex-post de A4, valores q de multiplicidade e as tres
ameacas do C-7 em A5.

Dois portoes:

1. Cada trecho esperado, reconstruido a partir da fonte, tem de existir no
   `.tex` do artigo curto. Os trechos do conferidor principal sao reutilizados
   quando o artigo curto repete a mesma formulacao; os demais sao declarados
   aqui.
2. Cobertura: todo numero com virgula decimal no corpo do artigo curto tem de
   estar contido em algum trecho conferido. Um decimal que nao esteja e
   numero sem origem, e reprova.

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
for chave, bruto, loc in [("TOTAL", n_trat + n_ctrl, l7), ("TRAT", n_trat, l7), ("CTRL", n_ctrl, l8), ("TRANSBORDO", tr_trat, l9)]:
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
trecho_rg_txt = f"também sobe, {decimal_br(rg_b, 3)} log-ponto com $p$ de {p_texto(rg_p)} em {inteiro(n_reg)} regiões"
registrar("CURTO_C7_REGIONAL_TXT_beta", "Secao 4", "oferta liquida regional no texto", decimal_br(rg_b, 3), A5_C7, l14, rg_b, "3 casas", trecho_rg_txt)
registrar("CURTO_C7_REGIONAL_TXT_p", "Secao 4", "p regional no texto", p_texto(rg_p), A5_C7, l16, rg_p, "3 casas", trecho_rg_txt)
registrar("CURTO_C7_REGIONAL_TXT_n", "Secao 4", "regioes", inteiro(n_reg), A5_C7, l17, n_reg, "inteiro", trecho_rg_txt)
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
    corpo = tex.split("\\begin{document}", 1)[1].split("\\begin{thebibliography}", 1)[0]
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
