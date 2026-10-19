"""Confere cada numero citado em paper_pmme_submission.tex contra os artefatos.

O script releia os artefatos versionados de A4, A5, A7, A8, da RDD da bolsa no
IVS 2010 oficial (R1, E3 e E5), da rodada multi-outcome da bolsa (E6, E7, E8 e
E9) e do portao de relevancia, reformata cada valor
no padrao usado no artigo e exige que o trecho correspondente exista no arquivo
LaTeX. Nenhuma cifra do artigo pode existir sem uma origem rastreavel; qualquer
divergencia interrompe a execucao com codigo de saida diferente de zero. Todo
decimal com virgula no corpo, apendices incluidos (so a bibliografia fica de
fora), tem de estar contido em algum trecho conferido.

O mapeamento completo e gravado em
`output/tema_trabalho/A8_conferencia_numeros_artigo.csv`, com arquivo-fonte e
linha ou campo de origem por numero.

O script e somente leitura sobre `data/` e sobre os artefatos: a unica escrita e
o CSV de conferencia. Todos os caminhos sao relativos a raiz do repositorio.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
TEX = ROOT / "paper_pmme_submission.tex"
OUT = ROOT / "output" / "tema_trabalho"
CONFERENCIA_CSV = OUT / "A8_conferencia_numeros_artigo.csv"

A8_SUPORTE = "output/tema_trabalho/A8_tabela_01_suporte_escore_estrito.csv"
A8_ESTIM = "output/tema_trabalho/A8_tabela_02_estimativas_escore_estrito.csv"
A8_PLACEBO = "output/tema_trabalho/A8_tabela_03_placebos_escore_estrito.csv"
A8_GAP = "output/tema_trabalho/A8_tabela_04_sensibilidade_gap.csv"
A8_LOO = "output/tema_trabalho/A8_tabela_05_leave_one_out.csv"
A8_JSON = "output/tema_trabalho/A8_estimativas_cutoff_escore.json"
A8_PROTOCOLO = "output/tema_trabalho/A8_protocolo_cutoff_escore.json"
A7_JSON = "output/tema_trabalho/A7_cutoff_selecao_resumo.json"
A4_LPM = "output/tema_trabalho/A4_tabela_02_modelo_principal_LPM.csv"
A4_LOGIT = "output/tema_trabalho/A4_tabela_02b_logit_AME.csv"
A4_ESTAGIO = "output/tema_trabalho/A4_tabela_02c_confirmacao_homologacao.csv"
A4_MUNCURSO = "output/tema_trabalho/A4_tabela_02d_municipio_curso.csv"
A4_AJUSTE = "output/tema_trabalho/A4_tabela_03b_ajuste_completo.csv"
A4_JSON = "output/tema_trabalho/A4_estimativas_atracao.json"
A5_JSON = "output/tema_trabalho/A5_estimativas_provimento.json"
A5_EVENTO = "output/tema_trabalho/A5_tabela_07_estudo_evento_atracao.csv"
# RDD da bolsa no IVS 2010 oficial (docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md).
RDD_R1 = "output/rdd_bolsa/portao_r1_ivs_oficial.json"
RDD_PROTOCOLO = "output/rdd_bolsa/protocolo_escore_administrativo.json"
RDD_E3_STATUS = "output/rdd_bolsa/E3_status.json"
RDD_E3_ESTIM = "output/rdd_bolsa/E3_estimativas.csv"
RDD_E3_DIAG = "output/rdd_bolsa/E3_diagnosticos.csv"
RDD_E5_ESPEC = "output/rdd_bolsa/E5_especificacoes.csv"
RDD_E5_DECOMP = "output/rdd_bolsa/E5_decomposicao_ic.csv"
RDD_GRADE = "output/aquisicao/a04_grade_anunciada_2025.csv"
DDD_PORTAO = "output/avaliacao_impacto/relatorios/01_relatorio_portao_relevancia.json"

CABECALHO = [
    "id",
    "bloco",
    "descricao",
    "valor_no_artigo",
    "fonte_arquivo",
    "fonte_localizador",
    "valor_bruto_na_fonte",
    "transformacao",
    "trecho_esperado_no_tex",
    "ocorrencias_no_tex",
    "status",
]


# ---------------------------------------------------------------- formatadores


def decimal_br(valor: float, casas: int) -> str:
    """Formata em portugues, com virgula decimal e sinal negativo matematico."""
    numero = 0.0 if abs(float(valor)) < 1e-12 else float(valor)
    texto = f"{abs(numero):.{casas}f}".replace(".", ",")
    return f"$-${texto}" if numero < 0 else texto


def pontos(valor: float, casas: int = 1) -> str:
    """Converte proporcao em pontos percentuais no padrao do artigo."""
    return decimal_br(float(valor) * 100.0, casas)


def inteiro(valor: float) -> str:
    return str(int(round(float(valor))))


def milhar(valor: float) -> str:
    return f"{int(round(float(valor))):,}".replace(",", ".")


def p_menor_que(valor: float, limite: float, texto: str) -> str:
    if not float(valor) < limite:
        raise SystemExit(
            f"p-valor {valor} nao satisfaz o limite {limite} usado no artigo"
        )
    return texto


# ------------------------------------------------------------------- leitores

_CSV: dict[str, pd.DataFrame] = {}
_JSON: dict[str, Any] = {}


def csv_frame(rel: str) -> pd.DataFrame:
    if rel not in _CSV:
        caminho = ROOT / rel
        if not caminho.exists():
            raise SystemExit(f"Artefato ausente: {rel}")
        _CSV[rel] = pd.read_csv(caminho)
    return _CSV[rel]


def csv_valor(rel: str, filtros: dict[str, Any], campo: str) -> tuple[Any, str]:
    frame = csv_frame(rel)
    mascara = pd.Series(True, index=frame.index)
    for coluna, alvo in filtros.items():
        if coluna not in frame.columns:
            raise SystemExit(f"Coluna {coluna} ausente em {rel}")
        mascara &= frame[coluna].astype(str).eq(str(alvo))
    selecao = frame[mascara]
    if len(selecao) != 1:
        raise SystemExit(
            f"Filtro {filtros} selecionou {len(selecao)} linhas em {rel}; esperava 1"
        )
    indice = int(selecao.index[0])
    if campo not in frame.columns:
        raise SystemExit(f"Coluna {campo} ausente em {rel}")
    return selecao.iloc[0][campo], f"linha {indice + 2}; coluna {campo}"


def csv_soma(rel: str, filtros_lista: list[dict[str, Any]], campo: str) -> tuple[float, str]:
    total = 0.0
    locais = []
    for filtros in filtros_lista:
        valor, local = csv_valor(rel, filtros, campo)
        total += float(valor)
        locais.append(local.split(";")[0])
    return total, f"soma de {', '.join(locais)}; coluna {campo}"


def json_valor(rel: str, caminho: str) -> tuple[Any, str]:
    if rel not in _JSON:
        arquivo = ROOT / rel
        if not arquivo.exists():
            raise SystemExit(f"Artefato ausente: {rel}")
        _JSON[rel] = json.loads(arquivo.read_text(encoding="utf-8"))
    atual = _JSON[rel]
    for parte in caminho.split("/"):
        atual = atual[int(parte)] if isinstance(atual, list) else atual[parte]
    return atual, f"campo {caminho}"


# -------------------------------------------------------------------- registro

REGISTROS: list[dict[str, Any]] = []


def registrar(
    identificador: str,
    bloco: str,
    descricao: str,
    valor_no_artigo: str,
    fonte: str,
    localizador: str,
    bruto: Any,
    transformacao: str,
    trecho: str,
) -> None:
    REGISTROS.append(
        {
            "id": identificador,
            "bloco": bloco,
            "descricao": descricao,
            "valor_no_artigo": valor_no_artigo,
            "fonte_arquivo": fonte,
            "fonte_localizador": localizador,
            "valor_bruto_na_fonte": bruto,
            "transformacao": transformacao,
            "trecho_esperado_no_tex": trecho,
        }
    )


def registrar_linha_csv(
    prefixo: str,
    bloco: str,
    fonte: str,
    filtros: dict[str, Any],
    campos: list[tuple[str, str, str, Any]],
    modelo: str,
) -> None:
    """Registra uma linha de tabela cujo texto e reconstruido da fonte.

    Cada item de `campos` e (chave_do_modelo, coluna, transformacao, formatador).
    O trecho esperado e o modelo preenchido apenas com valores da fonte, de modo
    que qualquer divergencia de qualquer celula reprova a linha inteira.
    """
    valores: dict[str, str] = {}
    detalhes: list[tuple[str, str, Any, str]] = []
    for chave, coluna, transformacao, formatador in campos:
        bruto, local = csv_valor(fonte, filtros, coluna)
        formatado = formatador(bruto)
        valores[chave] = formatado
        detalhes.append((chave, local, bruto, transformacao))
    trecho = modelo.format(**valores)
    for chave, local, bruto, transformacao in detalhes:
        registrar(
            f"{prefixo}_{chave}",
            bloco,
            f"{bloco}: celula '{chave}' da linha {filtros}",
            valores[chave],
            fonte,
            local,
            bruto,
            transformacao,
            trecho,
        )


# ------------------------------------------------------- A8: tabela de suporte

SUPORTE_LINHAS = [
    ("2025_C1_CH1", "2025, ciclo 1, chamada 1"),
    ("2025_C1_CH2", "2025, ciclo 1, chamada 2"),
    ("2026_C2_CH2", "2026, ciclo 2, chamada 2"),
]

for chave_chamada, rotulo in SUPORTE_LINHAS:
    registrar_linha_csv(
        f"A8_SUPORTE_{chave_chamada}",
        "Tabela 1 (suporte amostral)",
        A8_SUPORTE,
        {"ciclo_chamada": chave_chamada},
        [
            ("adjacentes", "pares_adjacentes", "inteiro", inteiro),
            ("cutoff", "pares_cutoff_ampla_concorrencia", "inteiro", inteiro),
            ("gap1", "pares_gap_1_ac", "inteiro", inteiro),
            ("empates", "pares_empate_excluidos", "inteiro", inteiro),
            ("violacoes", "violacoes_gap_1", "inteiro", inteiro),
            ("placebo_abaixo", "placebos_abaixo_gap_1_ac", "inteiro", inteiro),
            ("placebo_acima", "placebos_acima_gap_1_ac", "inteiro", inteiro),
        ],
        rotulo
        + " & {adjacentes} & {cutoff} & {gap1} & {empates} & {violacoes}"
        + " & {placebo_abaixo} & {placebo_acima} \\\\",
    )


# --------------------------------------------------- A8: tabela principal 2025

PRINCIPAL_2025 = {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": "gap_1_ac"}

PRINCIPAL_LINHAS = [
    (
        "HOMOLOG_LOCAL",
        "homologacao_mesma_celula",
        "Homologação no mesmo curso--CNES",
        lambda p: p_menor_que(p, 1e-6, "$<$0,000001"),
        "p exato < 1e-6 reportado como '$<$0,000001'",
    ),
    (
        "ATIVO_LOCAL",
        "ativo_mesma_celula_snapshot",
        "Ativo no mesmo curso--CNES",
        lambda p: decimal_br(p, 4),
        "p exato com 4 casas",
    ),
    (
        "HOMOLOG_QUALQUER",
        "homologacao_qualquer_local",
        "Homologação em qualquer local",
        lambda p: decimal_br(p, 7),
        "p exato com 7 casas",
    ),
    (
        "ATIVO_QUALQUER",
        "ativo_qualquer_local_snapshot",
        "Ativo em qualquer local",
        lambda p: decimal_br(p, 4),
        "p exato com 4 casas",
    ),
]

for sufixo, desfecho, rotulo, fmt_p, nota_p in PRINCIPAL_LINHAS:
    registrar_linha_csv(
        f"A8_PRINCIPAL_{sufixo}",
        "Tabela 2 (resultado principal de 2025)",
        A8_ESTIM,
        {**PRINCIPAL_2025, "desfecho": desfecho},
        [
            ("acima", "media_acima", "proporcao x100, 1 casa", pontos),
            ("abaixo", "media_abaixo", "proporcao x100, 1 casa", pontos),
            ("dif", "diferenca", "proporcao x100, 1 casa", pontos),
            ("ep", "erro_padrao_pareado", "proporcao x100, 1 casa", pontos),
            ("lo", "ic95_convencional_inferior", "proporcao x100, 1 casa", pontos),
            ("hi", "ic95_convencional_superior", "proporcao x100, 1 casa", pontos),
            ("p", "p_exato_pareado_bicaudal", nota_p, fmt_p),
        ],
        rotulo + " & {acima} & {abaixo} & {dif} & {ep} & [{lo}; {hi}] & {p} \\\\",
    )


# ------------------------------------------------------------ A8: placebos

PLACEBO_LINHAS = [
    ("ABAIXO_HOMOLOG_LOCAL", "placebo_abaixo_gap_1_ac", "homologacao_mesma_celula",
     "Imediatamente abaixo & Homologação no mesmo curso--CNES", 3),
    ("ABAIXO_ATIVO_LOCAL", "placebo_abaixo_gap_1_ac", "ativo_mesma_celula_snapshot",
     "Imediatamente abaixo & Ativo no mesmo curso--CNES", 3),
    ("ABAIXO_HOMOLOG_QUALQUER", "placebo_abaixo_gap_1_ac", "homologacao_qualquer_local",
     "Imediatamente abaixo & Homologação em qualquer local", 4),
    ("ABAIXO_ATIVO_QUALQUER", "placebo_abaixo_gap_1_ac", "ativo_qualquer_local_snapshot",
     "Imediatamente abaixo & Ativo em qualquer local", 3),
    ("ACIMA_HOMOLOG_LOCAL", "placebo_acima_gap_1_ac", "homologacao_mesma_celula",
     "Imediatamente acima & Homologação no mesmo curso--CNES", 3),
    ("ACIMA_ATIVO_LOCAL", "placebo_acima_gap_1_ac", "ativo_mesma_celula_snapshot",
     "Imediatamente acima & Ativo no mesmo curso--CNES", 3),
]

for sufixo, amostra, desfecho, rotulo, casas_p in PLACEBO_LINHAS:
    registrar_linha_csv(
        f"A8_PLACEBO_{sufixo}",
        "Tabela 3 (placebos)",
        A8_PLACEBO,
        {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra, "desfecho": desfecho},
        [
            ("pares", "n_pares", "inteiro", inteiro),
            ("dif", "diferenca", "proporcao x100, 1 casa", pontos),
            ("p", "p_exato_pareado_bicaudal", f"p exato com {casas_p} casas",
             lambda valor, casas=casas_p: decimal_br(valor, casas)),
        ],
        rotulo + " & {pares} & {dif} & {p} \\\\",
    )


# ------------------------------------------------------ A8: janelas de gap

GAP_LINHAS = [
    ("GAP1", "gap_1_ac", "Gap de exatamente 1 ponto (principal)"),
    ("GAP2", "gap_positivo_ate_2_ac", "Gap positivo de até 2 pontos"),
    ("GAPQUALQUER", "qualquer_gap_positivo_ac", "Qualquer gap positivo"),
    ("EMPATES", "empate_descritivo_nao_causal", "Empates (descritivo, não causal)"),
]

for sufixo, amostra, rotulo in GAP_LINHAS:
    homolog_pares, local_pares = csv_valor(
        A8_GAP,
        {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra,
         "desfecho": "homologacao_mesma_celula"},
        "n_pares",
    )
    homolog_dif, local_homolog = csv_valor(
        A8_GAP,
        {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra,
         "desfecho": "homologacao_mesma_celula"},
        "diferenca",
    )
    ativo_dif, local_ativo = csv_valor(
        A8_GAP,
        {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra,
         "desfecho": "ativo_mesma_celula_snapshot"},
        "diferenca",
    )
    trecho_gap = (
        f"{rotulo} & {inteiro(homolog_pares)} & {pontos(homolog_dif)}"
        f" & {pontos(ativo_dif)} \\\\"
    )
    registrar(f"A8_GAP_{sufixo}_pares", "Tabela 4 (janelas de gap)",
              f"Numero de pares no recorte {amostra}", inteiro(homolog_pares),
              A8_GAP, local_pares, homolog_pares, "inteiro", trecho_gap)
    registrar(f"A8_GAP_{sufixo}_homolog", "Tabela 4 (janelas de gap)",
              f"Diferenca de homologacao no recorte {amostra}", pontos(homolog_dif),
              A8_GAP, local_homolog, homolog_dif, "proporcao x100, 1 casa", trecho_gap)
    registrar(f"A8_GAP_{sufixo}_ativo", "Tabela 4 (janelas de gap)",
              f"Diferenca de presenca ativa no recorte {amostra}", pontos(ativo_dif),
              A8_GAP, local_ativo, ativo_dif, "proporcao x100, 1 casa", trecho_gap)


# ------------------------------------------------- A8: numeros do corpo do texto


def registrar_texto(
    identificador: str,
    bloco: str,
    descricao: str,
    valor: str,
    fonte: str,
    localizador: str,
    bruto: Any,
    transformacao: str,
    modelo: str,
) -> None:
    registrar(identificador, bloco, descricao, valor, fonte, localizador, bruto,
              transformacao, modelo.format(v=valor))


n_pares_2025, loc = json_valor(A8_JSON, "resultado_principal_2025/n_pares")
registrar_texto("A8_TXT_N_PARES_RESUMO", "Resumo", "Pares da amostra principal de 2025",
                inteiro(n_pares_2025), A8_JSON, loc, n_pares_2025, "inteiro",
                "Em {v} pares de 2025, ganhar a vaga elevou a homologação")
registrar_texto("A8_TXT_N_PARES_RESULTADO", "Secao 5.1", "Pares da amostra principal de 2025",
                inteiro(n_pares_2025), A8_JSON, loc, n_pares_2025, "inteiro",
                "apresenta o resultado principal nos {v} pares de")
registrar_texto("A8_TXT_N_PARES_LIMITACAO", "Secao 6", "Pares da amostra principal de 2025",
                inteiro(n_pares_2025), A8_JSON, loc, n_pares_2025, "inteiro",
                "amostra principal tem {v} pares, o que limita a precisão")
registrar_texto("A8_TXT_N_PARES_INFERENCIA", "Secao 4.4", "Pares da amostra principal de 2025",
                inteiro(n_pares_2025), A8_JSON, loc, n_pares_2025, "inteiro",
                "aproximações assintóticas com {v} pares")

gap1_ch1, loc_ch1 = csv_valor(A8_SUPORTE, {"ciclo_chamada": "2025_C1_CH1"}, "pares_gap_1_ac")
gap1_ch2, loc_ch2 = csv_valor(A8_SUPORTE, {"ciclo_chamada": "2025_C1_CH2"}, "pares_gap_1_ac")
registrar("A8_TXT_GAP1_CH1_CH2", "Secao 4.2",
          "Pares com gap de um ponto por chamada de 2025",
          f"{inteiro(gap1_ch1)} e {inteiro(gap1_ch2)}", A8_SUPORTE,
          f"{loc_ch1} e {loc_ch2}", f"{gap1_ch1}; {gap1_ch2}", "inteiros",
          f"Em 2025, restam {inteiro(gap1_ch1)} pares na primeira chamada e "
          f"{inteiro(gap1_ch2)} na segunda, totalizando {inteiro(n_pares_2025)} pares")

empates_2025, loc_empates = csv_soma(
    A8_SUPORTE,
    [{"ciclo_chamada": "2025_C1_CH1"}, {"ciclo_chamada": "2025_C1_CH2"}],
    "pares_empate_excluidos",
)
registrar_texto("A8_TXT_EMPATES_METODO", "Secao 4.2", "Pares empatados excluidos em 2025",
                inteiro(empates_2025), A8_SUPORTE, loc_empates, empates_2025,
                "soma das duas chamadas de 2025",
                "{v} pares empatados são excluídos")
registrar_texto("A8_TXT_EMPATES_RESULTADO", "Secao 5.3", "Pares empatados excluidos em 2025",
                inteiro(empates_2025), A8_SUPORTE, loc_empates, empates_2025,
                "soma das duas chamadas de 2025",
                "reporta os {v} pares empatados apenas como")

placebo_abaixo_n, loc_pa = csv_valor(
    A8_PLACEBO,
    {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": "placebo_abaixo_gap_1_ac",
     "desfecho": "homologacao_mesma_celula"},
    "n_pares",
)
registrar_texto("A8_TXT_PLACEBO_ABAIXO_N", "Secao 5.2", "Pares do placebo abaixo do cutoff",
                inteiro(placebo_abaixo_n), A8_PLACEBO, loc_pa, placebo_abaixo_n, "inteiro",
                "Entre os {v} pares de não selecionados separados por um ponto")

placebo_acima_n, loc_pc = csv_valor(
    A8_PLACEBO,
    {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": "placebo_acima_gap_1_ac",
     "desfecho": "homologacao_mesma_celula"},
    "n_pares",
)
registrar_texto("A8_TXT_PLACEBO_ACIMA_N", "Secao 5.2", "Pares do placebo acima do cutoff",
                inteiro(placebo_acima_n), A8_PLACEBO, loc_pc, placebo_acima_n, "inteiro",
                "acima do cutoff tem apenas {v} pares")

for sufixo, desfecho, modelo in [
    ("DISC_HOMOLOG", "homologacao_mesma_celula",
     "Entre os 36 pares, {v} são discordantes e todos favoráveis no desfecho de homologação"),
]:
    disc, loc_disc = csv_valor(A8_ESTIM, {**PRINCIPAL_2025, "desfecho": desfecho},
                               "discordantes_favoraveis")
    registrar_texto(f"A8_TXT_{sufixo}", "Secao 5.1",
                    "Pares discordantes favoraveis em homologacao", inteiro(disc),
                    A8_ESTIM, loc_disc, disc, "inteiro", modelo)

disc_fav, loc_fav = csv_valor(
    A8_ESTIM, {**PRINCIPAL_2025, "desfecho": "ativo_mesma_celula_snapshot"},
    "discordantes_favoraveis")
disc_con, loc_con = csv_valor(
    A8_ESTIM, {**PRINCIPAL_2025, "desfecho": "ativo_mesma_celula_snapshot"},
    "discordantes_contrarios")
registrar("A8_TXT_DISC_ATIVO", "Secao 5.1",
          "Pares discordantes na presenca ativa (favoraveis e contrarios)",
          f"{inteiro(disc_fav)} e {inteiro(disc_con)}", A8_ESTIM,
          f"{loc_fav} e {loc_con}", f"{disc_fav}; {disc_con}", "inteiros",
          f"no desfecho de presença ativa, {inteiro(disc_fav)} são favoráveis e "
          f"{inteiro(disc_con)} contrários")

ch1_homolog, loc_h1 = csv_valor(
    A8_ESTIM,
    {"ciclo_chamada": "2025_C1_CH1", "amostra": "gap_1_ac",
     "desfecho": "homologacao_mesma_celula"}, "diferenca")
ch2_homolog, loc_h2 = csv_valor(
    A8_ESTIM,
    {"ciclo_chamada": "2025_C1_CH2", "amostra": "gap_1_ac",
     "desfecho": "homologacao_mesma_celula"}, "diferenca")
ch1_ativo, loc_a1 = csv_valor(
    A8_ESTIM,
    {"ciclo_chamada": "2025_C1_CH1", "amostra": "gap_1_ac",
     "desfecho": "ativo_mesma_celula_snapshot"}, "diferenca")
trecho_chamadas = (
    f"a diferença de homologação é de {pontos(ch1_homolog)} pontos percentuais nos "
    f"{inteiro(gap1_ch1)} pares da primeira chamada e de {pontos(ch2_homolog)} pontos "
    f"percentuais nos {inteiro(gap1_ch2)} pares da segunda; a diferença de presença "
    f"ativa é de {pontos(ch1_ativo)} pontos percentuais em ambas"
)
registrar("A8_TXT_CH1_HOMOLOG", "Secao 5.1", "Diferenca de homologacao na chamada 1 de 2025",
          pontos(ch1_homolog), A8_ESTIM, loc_h1, ch1_homolog, "proporcao x100, 1 casa",
          trecho_chamadas)
registrar("A8_TXT_CH2_HOMOLOG", "Secao 5.1", "Diferenca de homologacao na chamada 2 de 2025",
          pontos(ch2_homolog), A8_ESTIM, loc_h2, ch2_homolog, "proporcao x100, 1 casa",
          trecho_chamadas)
registrar("A8_TXT_CH1_ATIVO", "Secao 5.1", "Diferenca de presenca ativa por chamada de 2025",
          pontos(ch1_ativo), A8_ESTIM, loc_a1, ch1_ativo, "proporcao x100, 1 casa",
          trecho_chamadas)

loo_homolog_min, loc_lmin = json_valor(A8_JSON, "leave_one_out/homologacao_mesma_celula/min")
loo_homolog_max, loc_lmax = json_valor(A8_JSON, "leave_one_out/homologacao_mesma_celula/max")
loo_ativo_min, loc_amin = json_valor(A8_JSON, "leave_one_out/ativo_mesma_celula_snapshot/min")
loo_ativo_max, loc_amax = json_valor(A8_JSON, "leave_one_out/ativo_mesma_celula_snapshot/max")
loo_n, loc_ln = json_valor(A8_JSON, "leave_one_out/homologacao_mesma_celula/n_exclusoes")

loo_frame = csv_frame(A8_LOO)
n_cursos = loo_frame[loo_frame["dimensao_excluida"].eq("course_code")]["grupo_excluido"].nunique()
n_ufs = loo_frame[loo_frame["dimensao_excluida"].eq("uf")]["grupo_excluido"].nunique()
trecho_loo = (
    f"Excluindo sucessivamente cada um dos {n_cursos} cursos e cada uma das {n_ufs} "
    f"unidades da federação presentes na amostra principal, em {inteiro(loo_n)} exclusões, "
    f"a diferença de homologação permanece entre {pontos(loo_homolog_min)} e "
    f"{pontos(loo_homolog_max)} pontos percentuais e a diferença de presença ativa "
    f"permanece entre {pontos(loo_ativo_min)} e {pontos(loo_ativo_max)} pontos percentuais"
)
for chave, valor, local, bruto, descricao in [
    ("N_CURSOS", str(n_cursos), "coluna grupo_excluido; dimensao_excluida=course_code",
     n_cursos, "Cursos distintos no leave-one-out"),
    ("N_UFS", str(n_ufs), "coluna grupo_excluido; dimensao_excluida=uf", n_ufs,
     "UFs distintas no leave-one-out"),
]:
    registrar(f"A8_TXT_LOO_{chave}", "Secao 5.3", descricao, valor, A8_LOO, local,
              bruto, "contagem de grupos distintos", trecho_loo)
for chave, valor_bruto, local, descricao in [
    ("N_EXCLUSOES", loo_n, loc_ln, "Numero de exclusoes do leave-one-out"),
    ("HOMOLOG_MIN", loo_homolog_min, loc_lmin, "Minimo do leave-one-out em homologacao"),
    ("HOMOLOG_MAX", loo_homolog_max, loc_lmax, "Maximo do leave-one-out em homologacao"),
    ("ATIVO_MIN", loo_ativo_min, loc_amin, "Minimo do leave-one-out em presenca ativa"),
    ("ATIVO_MAX", loo_ativo_max, loc_amax, "Maximo do leave-one-out em presenca ativa"),
]:
    formatado = inteiro(valor_bruto) if chave == "N_EXCLUSOES" else pontos(valor_bruto)
    registrar(f"A8_TXT_LOO_{chave}", "Secao 5.3", descricao, formatado, A8_JSON, local,
              valor_bruto, "inteiro" if chave == "N_EXCLUSOES" else "proporcao x100, 1 casa",
              trecho_loo)

rep_2026 = {"ciclo_chamada": "2026_C2_CH2", "amostra": "gap_1_ac_replicacao",
            "desfecho": "ativo_mesma_celula_snapshot"}
rep_n, loc_rn = csv_valor(A8_ESTIM, rep_2026, "n_pares")
rep_dif, loc_rd = csv_valor(A8_ESTIM, rep_2026, "diferenca")
rep_lo, loc_rl = csv_valor(A8_ESTIM, rep_2026, "ic95_convencional_inferior")
rep_hi, loc_rh = csv_valor(A8_ESTIM, rep_2026, "ic95_convencional_superior")
rep_p, loc_rp = csv_valor(A8_ESTIM, rep_2026, "p_exato_pareado_bicaudal")
rep_disc, loc_rdisc = csv_valor(A8_ESTIM, rep_2026, "discordantes_favoraveis")
trecho_rep = (
    f"{inteiro(rep_n)} pares atendem ao mesmo critério estrito. A diferença de presença "
    f"ativa no mesmo curso--CNES é de {pontos(rep_dif)} pontos percentuais, próxima da "
    f"estimativa de 2025. O intervalo convencional vai de {pontos(rep_lo)} a "
    f"{pontos(rep_hi)} pontos percentuais, mas o teste exato é de {decimal_br(rep_p, 3)}, "
    f"porque há apenas {inteiro(rep_disc)} pares discordantes"
)
for chave, bruto, local, formatado, transformacao, descricao in [
    ("N", rep_n, loc_rn, inteiro(rep_n), "inteiro", "Pares da replicacao de 2026"),
    ("DIF", rep_dif, loc_rd, pontos(rep_dif), "proporcao x100, 1 casa",
     "Diferenca de presenca ativa na replicacao de 2026"),
    ("IC_LO", rep_lo, loc_rl, pontos(rep_lo), "proporcao x100, 1 casa",
     "Limite inferior do IC convencional de 2026"),
    ("IC_HI", rep_hi, loc_rh, pontos(rep_hi), "proporcao x100, 1 casa",
     "Limite superior do IC convencional de 2026"),
    ("P", rep_p, loc_rp, decimal_br(rep_p, 3), "p exato com 3 casas",
     "Teste exato da replicacao de 2026"),
    ("DISC", rep_disc, loc_rdisc, inteiro(rep_disc), "inteiro",
     "Pares discordantes da replicacao de 2026"),
]:
    registrar(f"A8_TXT_REP2026_{chave}", "Secao 5.4", descricao, formatado, A8_ESTIM,
              local, bruto, transformacao, trecho_rep)

registrar_texto("A8_TXT_REP2026_RESUMO", "Resumo", "Pares da replicacao de 2026",
                inteiro(rep_n), A8_ESTIM, loc_rn, rep_n, "inteiro",
                "Em {v} pares do ciclo 2 de 2026")
registrar_texto("A8_TXT_REP2026_DIF_RESUMO", "Resumo",
                "Diferenca de presenca ativa na replicacao de 2026", pontos(rep_dif),
                A8_ESTIM, loc_rd, rep_dif, "proporcao x100, 1 casa",
                "a presença ativa aumenta {v} pontos percentuais")
registrar_texto("A8_TXT_REP2026_P_RESUMO", "Resumo", "Teste exato da replicacao de 2026",
                decimal_br(rep_p, 3), A8_ESTIM, loc_rp, rep_p, "p exato com 3 casas",
                "com teste exato impreciso ($p$ de {v})")

pares_a7, loc_a7 = json_valor(A7_JSON, "suporte/pares_adjacentes_total_quatro_publicacoes")
registrar_texto("A8_TXT_A7_PARES", "Secao 4.6", "Pares adjacentes do diagnostico anterior",
                inteiro(pares_a7), A7_JSON, loc_a7, pares_a7, "inteiro",
                "adjacentes, com {v} pares nas quatro publicações")

data_snapshot, loc_snap = json_valor(A8_PROTOCOLO, "outcome_substantivo_principal")
if "2026-08-12" not in str(data_snapshot):
    raise SystemExit("Data do desfecho substantivo mudou no protocolo A8")
registrar("A8_TXT_DATA_SNAPSHOT", "Secoes 4.3 e 5.1",
          "Data de referencia do desfecho substantivo", "12 de agosto de 2026",
          A8_PROTOCOLO, loc_snap, data_snapshot, "2026-08-12 escrito por extenso",
          "ativo no mesmo curso--CNES em 12 de agosto de 2026")

hashes, loc_hash = json_valor(A8_PROTOCOLO, "hashes_entradas")
if len(hashes) != 6:
    raise SystemExit(f"O protocolo A8 tem {len(hashes)} entradas; o artigo cita seis")
registrar("A8_TXT_N_FONTES", "Secao 4.1", "Numero de arquivos de entrada com hash congelado",
          "seis", A8_PROTOCOLO, loc_hash, len(hashes), "contagem escrita por extenso",
          "As seis entradas têm hash SHA-256 congelado")

# Resumo: valores principais reaproveitados no abstract e na conclusao
homolog_dif, loc_hd = csv_valor(
    A8_ESTIM, {**PRINCIPAL_2025, "desfecho": "homologacao_mesma_celula"}, "diferenca")
homolog_lo, loc_hl = csv_valor(
    A8_ESTIM, {**PRINCIPAL_2025, "desfecho": "homologacao_mesma_celula"},
    "ic95_convencional_inferior")
homolog_hi, loc_hh = csv_valor(
    A8_ESTIM, {**PRINCIPAL_2025, "desfecho": "homologacao_mesma_celula"},
    "ic95_convencional_superior")
ativo_dif, loc_ad = csv_valor(
    A8_ESTIM, {**PRINCIPAL_2025, "desfecho": "ativo_mesma_celula_snapshot"}, "diferenca")
ativo_lo, loc_al = csv_valor(
    A8_ESTIM, {**PRINCIPAL_2025, "desfecho": "ativo_mesma_celula_snapshot"},
    "ic95_convencional_inferior")
ativo_hi, loc_ah = csv_valor(
    A8_ESTIM, {**PRINCIPAL_2025, "desfecho": "ativo_mesma_celula_snapshot"},
    "ic95_convencional_superior")
ativo_p, loc_ap = csv_valor(
    A8_ESTIM, {**PRINCIPAL_2025, "desfecho": "ativo_mesma_celula_snapshot"},
    "p_exato_pareado_bicaudal")

trecho_resumo = (
    f"em {pontos(homolog_dif)} pontos percentuais (intervalo convencional de "
    f"{pontos(homolog_lo)} a {pontos(homolog_hi)}; teste exato pareado com $p$ abaixo de "
    f"0,000001) e a presença ativa no mesmo curso--CNES em 12 de agosto de 2026 em "
    f"{pontos(ativo_dif)} pontos percentuais ({pontos(ativo_lo)} a {pontos(ativo_hi)}; "
    f"$p$ exato de {decimal_br(ativo_p, 4)})"
)
for chave, bruto, local, formatado, descricao in [
    ("HOMOLOG_DIF", homolog_dif, loc_hd, pontos(homolog_dif), "Diferenca de homologacao"),
    ("HOMOLOG_LO", homolog_lo, loc_hl, pontos(homolog_lo), "IC inferior da homologacao"),
    ("HOMOLOG_HI", homolog_hi, loc_hh, pontos(homolog_hi), "IC superior da homologacao"),
    ("ATIVO_DIF", ativo_dif, loc_ad, pontos(ativo_dif), "Diferenca de presenca ativa"),
    ("ATIVO_LO", ativo_lo, loc_al, pontos(ativo_lo), "IC inferior da presenca ativa"),
    ("ATIVO_HI", ativo_hi, loc_ah, pontos(ativo_hi), "IC superior da presenca ativa"),
    ("ATIVO_P", ativo_p, loc_ap, decimal_br(ativo_p, 4), "Teste exato da presenca ativa"),
]:
    registrar(f"A8_RESUMO_{chave}", "Resumo", descricao, formatado, A8_ESTIM, local,
              bruto, "proporcao x100, 1 casa" if chave != "ATIVO_P" else "p exato com 4 casas",
              trecho_resumo)

placebo_homolog, loc_ph = csv_valor(
    A8_PLACEBO,
    {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": "placebo_abaixo_gap_1_ac",
     "desfecho": "homologacao_mesma_celula"}, "diferenca")
placebo_ativo, loc_pv = csv_valor(
    A8_PLACEBO,
    {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": "placebo_abaixo_gap_1_ac",
     "desfecho": "ativo_mesma_celula_snapshot"}, "diferenca")
trecho_placebo_resumo = (
    f"imediatamente abaixo do cutoff é nulo, com {pontos(placebo_homolog)} e "
    f"{pontos(placebo_ativo)} pontos percentuais"
)
registrar("A8_RESUMO_PLACEBO_HOMOLOG", "Resumo", "Placebo abaixo em homologacao",
          pontos(placebo_homolog), A8_PLACEBO, loc_ph, placebo_homolog,
          "proporcao x100, 1 casa", trecho_placebo_resumo)
registrar("A8_RESUMO_PLACEBO_ATIVO", "Resumo", "Placebo abaixo em presenca ativa",
          pontos(placebo_ativo), A8_PLACEBO, loc_pv, placebo_ativo,
          "proporcao x100, 1 casa", trecho_placebo_resumo)

trecho_conclusao = (
    f"curso--CNES em {pontos(homolog_dif)} pontos percentuais e a presença ativa posterior "
    f"naquele mesmo curso--CNES em {pontos(ativo_dif)} pontos percentuais"
)
registrar("A8_CONCLUSAO_HOMOLOG", "Secao 7", "Diferenca de homologacao na conclusao",
          pontos(homolog_dif), A8_ESTIM, loc_hd, homolog_dif, "proporcao x100, 1 casa",
          trecho_conclusao)
registrar("A8_CONCLUSAO_ATIVO", "Secao 7", "Diferenca de presenca ativa na conclusao",
          pontos(ativo_dif), A8_ESTIM, loc_ad, ativo_dif, "proporcao x100, 1 casa",
          trecho_conclusao)

trecho_qualquer = (
    f"a diferença é de {pontos(csv_valor(A8_ESTIM, {**PRINCIPAL_2025, 'desfecho': 'homologacao_qualquer_local'}, 'diferenca')[0])}"
    f" pontos percentuais em homologação e de "
    f"{pontos(csv_valor(A8_ESTIM, {**PRINCIPAL_2025, 'desfecho': 'ativo_qualquer_local_snapshot'}, 'diferenca')[0])}"
    f" pontos percentuais em atividade"
)
for chave, desfecho, descricao in [
    ("HOMOLOG", "homologacao_qualquer_local", "Diferenca de homologacao em qualquer local"),
    ("ATIVO", "ativo_qualquer_local_snapshot", "Diferenca de atividade em qualquer local"),
]:
    bruto, local = csv_valor(A8_ESTIM, {**PRINCIPAL_2025, "desfecho": desfecho}, "diferenca")
    registrar(f"A8_TXT_QUALQUER_{chave}", "Secao 5.1", descricao, pontos(bruto), A8_ESTIM,
              local, bruto, "proporcao x100, 1 casa", trecho_qualquer)

trecho_placebo_texto = (
    f"a diferença é de {pontos(placebo_homolog)} pontos percentuais em homologação e de "
    f"{pontos(placebo_ativo)} ponto percentual em presença ativa, ambas com teste exato de "
    f"{decimal_br(csv_valor(A8_PLACEBO, {'ciclo_chamada': '2025_C1_CH1_E_CH2', 'amostra': 'placebo_abaixo_gap_1_ac', 'desfecho': 'homologacao_mesma_celula'}, 'p_exato_pareado_bicaudal')[0], 3)}"
)
registrar("A8_TXT_PLACEBO_HOMOLOG", "Secao 5.2", "Placebo abaixo em homologacao (corpo)",
          pontos(placebo_homolog), A8_PLACEBO, loc_ph, placebo_homolog,
          "proporcao x100, 1 casa", trecho_placebo_texto)
registrar("A8_TXT_PLACEBO_ATIVO", "Secao 5.2", "Placebo abaixo em presenca ativa (corpo)",
          pontos(placebo_ativo), A8_PLACEBO, loc_pv, placebo_ativo,
          "proporcao x100, 1 casa", trecho_placebo_texto)

placebo_acima_dif, loc_pad = csv_valor(
    A8_PLACEBO,
    {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": "placebo_acima_gap_1_ac",
     "desfecho": "homologacao_mesma_celula"}, "diferenca")
registrar_texto("A8_TXT_PLACEBO_ACIMA_DIF", "Secao 5.2",
                "Diferenca do placebo acima do cutoff", pontos(placebo_acima_dif),
                A8_PLACEBO, loc_pad, placebo_acima_dif, "proporcao x100, 1 casa",
                "e produz {v} pontos percentuais em ambos os desfechos")

for chave, amostra, modelo in [
    ("GAP2", "gap_positivo_ate_2_ac",
     "Com gap positivo de até dois pontos, o efeito é de {h} pontos percentuais em "
     "homologação e de {a} pontos percentuais em presença ativa, em {n} pares"),
    ("GAPQ", "qualquer_gap_positivo_ac",
     "Com qualquer gap positivo, o efeito é de {h} e {a} pontos percentuais, em {n} pares"),
]:
    h_bruto, h_loc = csv_valor(
        A8_GAP, {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra,
                 "desfecho": "homologacao_mesma_celula"}, "diferenca")
    a_bruto, a_loc = csv_valor(
        A8_GAP, {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra,
                 "desfecho": "ativo_mesma_celula_snapshot"}, "diferenca")
    n_bruto, n_loc = csv_valor(
        A8_GAP, {"ciclo_chamada": "2025_C1_CH1_E_CH2", "amostra": amostra,
                 "desfecho": "homologacao_mesma_celula"}, "n_pares")
    trecho = modelo.format(h=pontos(h_bruto), a=pontos(a_bruto), n=inteiro(n_bruto))
    registrar(f"A8_TXT_{chave}_HOMOLOG", "Secao 5.3",
              f"Homologacao no recorte {amostra} (corpo)", pontos(h_bruto), A8_GAP,
              h_loc, h_bruto, "proporcao x100, 1 casa", trecho)
    registrar(f"A8_TXT_{chave}_ATIVO", "Secao 5.3",
              f"Presenca ativa no recorte {amostra} (corpo)", pontos(a_bruto), A8_GAP,
              a_loc, a_bruto, "proporcao x100, 1 casa", trecho)
    registrar(f"A8_TXT_{chave}_N", "Secao 5.3", f"Pares no recorte {amostra} (corpo)",
              inteiro(n_bruto), A8_GAP, n_loc, n_bruto, "inteiro", trecho)


# ------------------------------------------------- Apendice A: A4 (descritivo)

A4_LINHAS = [
    ("LPM", A4_LPM, {"termo": "estrato_metropolitano"}, "Modelo linear pré-especificado"),
    ("LOGIT", A4_LOGIT, {"termo": "estrato_metropolitano"}, "Logit, efeito marginal médio"),
    # Ajuste completo reestimado em 18/10/2026 com a base oficial (IVS e populacao
    # 2010 do Ipea, a08; Censo 2022 no denominador do estoque). A versao anterior
    # usava data/ivs_ipea_2010_municipios.csv, linha de subgrupo populacional
    # (auditorias 16 e 19); seus numeros nao sao citados nos artigos.
    ("AJUSTE", A4_AJUSTE, {"termo": "estrato_metropolitano"}, "Ajuste completo, base oficial"),
    ("CONFIRMACAO", A4_ESTAGIO,
     {"termo": "estrato_metropolitano", "outcome_estagio": "alguma_confirmacao"},
     "Apenas confirmação"),
    ("HOMOLOGACAO", A4_ESTAGIO,
     {"termo": "estrato_metropolitano", "outcome_estagio": "alguma_homologacao"},
     "Apenas homologação"),
    ("MUNCURSO", A4_MUNCURSO, {"termo": "estrato_metropolitano"}, "Unidade município--curso"),
]

for sufixo, fonte, filtros, rotulo in A4_LINHAS:
    coluna_coef = "ame" if fonte == A4_LOGIT else "coef"
    coluna_se = "se_ame" if fonte == A4_LOGIT else "se_cluster"
    registrar_linha_csv(
        f"A4_TAB_{sufixo}",
        "Tabela A1 (gradiente territorial descritivo)",
        fonte,
        filtros,
        [
            ("dif", coluna_coef, "proporcao x100, 1 casa", pontos),
            ("ep", coluna_se, "proporcao x100, 1 casa", pontos),
        ],
        rotulo + " & {dif} & {ep} \\\\",
    )

a4_n, loc_a4n = csv_valor(A4_LPM, {"termo": "estrato_metropolitano"}, "n")
a4_clusters, loc_a4c = csv_valor(A4_LPM, {"termo": "estrato_metropolitano"}, "n_clusters")
a4_media, loc_a4m = csv_valor(A4_LPM, {"termo": "estrato_metropolitano"}, "outcome_medio")
registrar_texto("A4_TXT_N_CELULAS", "Apendice A", "Celulas CNES--curso da coorte A4",
                milhar(a4_n), A4_LPM, loc_a4n, a4_n, "inteiro com separador de milhar",
                "A coorte contém as {v} células CNES--curso do quadro da primeira chamada")
registrar_texto("A4_TXT_N_MUNICIPIOS", "Apendice A", "Municipios da coorte A4",
                inteiro(a4_clusters), A4_LPM, loc_a4c, a4_clusters, "inteiro",
                "do quadro da primeira chamada, em {v} municípios")
registrar_texto("A4_TXT_TAXA", "Apendice A", "Proporcao de celulas com atracao realizada",
                pontos(a4_media), A4_LPM, loc_a4m, a4_media, "proporcao x100, 1 casa",
                "células, ou {v}\\% do total")
registrar_texto("A4_TXT_N_ATRACAO", "Apendice A", "Celulas com atracao realizada",
                inteiro(float(a4_media) * float(a4_n)), A4_LPM, f"{loc_a4m} e {loc_a4n}",
                f"{a4_media} x {a4_n}", "outcome_medio x n, arredondado",
                "Houve atração em {v} células")
registrar_texto("A4_TXT_NOTA_TABELA", "Tabela A1", "Celulas e municipios na nota da tabela",
                milhar(a4_n), A4_LPM, loc_a4n, a4_n, "inteiro com separador de milhar",
                "\\textit{{Nota:}} {v} células e " + inteiro(a4_clusters) + " municípios")

a4_capital, loc_cap = csv_valor(A4_LPM, {"termo": "estrato_capital"}, "coef")
a4_interior, loc_int = csv_valor(A4_LPM, {"termo": "estrato_interior_proximo_polo"}, "coef")
trecho_a4_outros = (
    f"diferenças positivas em relação ao interior remoto, de {pontos(a4_capital)} e "
    f"{pontos(a4_interior)} pontos percentuais"
)
registrar("A4_TXT_CAPITAL", "Apendice A", "Contraste capital x interior remoto",
          pontos(a4_capital), A4_LPM, loc_cap, a4_capital, "proporcao x100, 1 casa",
          trecho_a4_outros)
registrar("A4_TXT_INTERIOR", "Apendice A", "Contraste interior proximo x interior remoto",
          pontos(a4_interior), A4_LPM, loc_int, a4_interior, "proporcao x100, 1 casa",
          trecho_a4_outros)

# Ajuste completo no texto (Apendice A do principal; Secao 3 do curto: mesma redacao)
aj_b, loc_ajb = csv_valor(A4_AJUSTE, {"termo": "estrato_metropolitano"}, "coef")
aj_se, loc_ajse = csv_valor(A4_AJUSTE, {"termo": "estrato_metropolitano"}, "se_cluster")
aj_p, loc_ajp = csv_valor(A4_AJUSTE, {"termo": "estrato_metropolitano"}, "p_valor")
aj_q, loc_ajq = csv_valor(A4_AJUSTE, {"termo": "estrato_metropolitano"}, "q_fdr_estrato")
trecho_ajuste = (
    f"reduz o contraste metropolitano para {pontos(aj_b)} pontos percentuais (erro-padrão "
    f"{pontos(aj_se)}; $p$ = {decimal_br(aj_p, 3)}; $q$ de Benjamini--Hochberg na família dos "
    f"três estratos = {decimal_br(aj_q, 3)})"
)
for chave, bruto, loc, fmt, tr in [
    ("COEF", aj_b, loc_ajb, pontos(aj_b), "proporcao x100, 1 casa"),
    ("EP", aj_se, loc_ajse, pontos(aj_se), "proporcao x100, 1 casa"),
    ("P", aj_p, loc_ajp, decimal_br(aj_p, 3), "3 casas"),
    ("Q", aj_q, loc_ajq, decimal_br(aj_q, 3), "3 casas"),
]:
    registrar(f"A4_TXT_AJUSTE_{chave}", "Apendice A", f"ajuste completo, base oficial: {chave}",
              fmt, A4_AJUSTE, loc, bruto, tr, trecho_ajuste)

bench, loc_bench = json_valor(A4_JSON, "potencia_referencia/benchmark_global_proporcao_p30")
mde, loc_mde = json_valor(
    A4_JSON, "potencia_referencia/contrastes_vs_interior_remoto_p30/metropolitano")
registrar_texto("A4_TXT_BENCHMARK", "Apendice A", "Benchmark global de precisao",
                pontos(bench), A4_JSON, loc_bench, bench, "proporcao x100, 1 casa",
                "o benchmark global de {v} pontos percentuais mede a")
registrar_texto("A4_TXT_MDE", "Apendice A",
                "Efeito minimo detectavel do contraste metropolitano", pontos(mde),
                A4_JSON, loc_mde, mde, "proporcao x100, 1 casa",
                "mínimo detectável aproximado é de {v} pontos percentuais")
registrar("A4_TXT_P30", "Apendice A", "Probabilidade base usada no calculo de potencia",
          "0,30", A4_JSON, "chave potencia_referencia/..._p30", "p30",
          "sufixo p30 da chave de potencia", "sob probabilidade base de 0,30")

# MDE ex-post e inferencia de pequena amostra (emenda 1 do plano 35; itens C-6 e A-2)
mde_post, loc_mde_post = json_valor(
    A4_JSON, "potencia_referencia/mde_ex_post_do_ep_realizado_p80/metropolitano")
registrar_texto("A4_TXT_MDE_EX_POST", "Apendice A",
                "Efeito minimo detectavel ex-post do contraste metropolitano",
                pontos(mde_post), A4_JSON, loc_mde_post, mde_post,
                "proporcao x100, 1 casa",
                "detectável ex-post do mesmo contraste é de {v} pontos percentuais")

a4_g_capital, loc_gcap = csv_valor(
    "output/tema_trabalho/A4_tabela_01_amostra_construcao.csv",
    {"amostra": "primaria_1295_Ch1", "estrato": "capital"}, "n_municipios")
registrar_texto("A4_TXT_G_CAPITAL", "Apendice A",
                "Municipios do estrato capital, gatilho G<30 do protocolo A3",
                inteiro(a4_g_capital),
                "output/tema_trabalho/A4_tabela_01_amostra_construcao.csv",
                loc_gcap, a4_g_capital, "inteiro",
                "e o estrato capital tem {v}")

b_wild, loc_bwild = json_valor(A4_JSON, "inferencia_wild_cluster_bootstrap/b_replicacoes")
registrar_texto("A4_TXT_B_WILD", "Apendice A",
                "Replicacoes do wild cluster bootstrap",
                milhar(b_wild), A4_JSON, loc_bwild, b_wild,
                "inteiro com separador de milhar",
                "por município e {v} replicações")


# ------------------------------------------------ Apendice B: A5 (associativo)

a5_celulas, loc_a5c = json_valor(A5_JSON, "modelos/principal_dinamico_confirmatorio/n_celulas")
a5_clusters, loc_a5g = json_valor(A5_JSON, "modelos/principal_dinamico_confirmatorio/n_clusters")
registrar("A5_TXT_AMOSTRA", "Apendice B", "Celulas e municipios da amostra confirmatoria",
          f"{inteiro(a5_celulas)} e {inteiro(a5_clusters)}", A5_JSON,
          f"{loc_a5c} e {loc_a5g}", f"{a5_celulas}; {a5_clusters}", "inteiros",
          f"A amostra confirmatória tem {inteiro(a5_celulas)} células em "
          f"{inteiro(a5_clusters)} municípios")

a5_f, loc_f = json_valor(A5_JSON, "modelos/principal_dinamico_confirmatorio/pre_F")
a5_pre_p, loc_pp = json_valor(A5_JSON, "modelos/principal_dinamico_confirmatorio/pre_p")
trecho_a5_pre = f"com $F$ de {decimal_br(a5_f, 2)} e $p$ de {decimal_br(a5_pre_p, 3)}"
A5_LOO = "output/tema_trabalho/A5_tabela_09_leave_one_curso_evento.csv"
A5_REF = "output/tema_trabalho/A5_tabela_10_sensibilidade_referencia.csv"

_pp = "modelos/principal_proporcional_confirmatorio"
a5p_f, loc_pf = json_valor(A5_JSON, f"{_pp}/pre_F")
a5p_pp, loc_ppp = json_valor(A5_JSON, f"{_pp}/pre_p")
a5p_b, loc_pb = json_valor(A5_JSON, f"{_pp}/mar2026_beta")
a5p_se, loc_pse = json_valor(A5_JSON, f"{_pp}/mar2026_se")
trecho_a5_pre = f"com $F$ de {decimal_br(a5p_f, 2)} e $p$ de {decimal_br(a5p_pp, 3)}"
trecho_a5_prop = (
    f"é de {decimal_br(a5p_b, 3)} log-ponto por célula, com erro-padrão de "
    f"{decimal_br(a5p_se, 3)} e $p$ inferior a 0,001"
)

a5_beta, loc_b = csv_valor(A5_EVENTO, {"amostra": "confirmatoria_587", "competencia": "202603"}, "beta")
a5_se, loc_s = csv_valor(A5_EVENTO, {"amostra": "confirmatoria_587", "competencia": "202603"}, "se_cluster")
a5_p, loc_p = csv_valor(A5_EVENTO, {"amostra": "confirmatoria_587", "competencia": "202603"}, "p_valor")
trecho_a5_mar = (
    f"em nível é {decimal_br(a5_beta, 2)} profissional por célula, com erro-padrão de "
    f"{decimal_br(a5_se, 2)} e $p$ de {decimal_br(a5_p, 3)}"
)

_fn = {"escala": "nivel", "competencia": "202603"}
loo14_b, loc_l14b = csv_valor(A5_LOO, {**_fn, "subamostra": "sem_curso_14"}, "beta")
loo14_p, loc_l14p = csv_valor(A5_LOO, {**_fn, "subamostra": "sem_curso_14"}, "p_valor")
loo8_b, loc_l8b = csv_valor(A5_LOO, {**_fn, "subamostra": "somente_8_cbo_1_para_1"}, "beta")
loo8_p, loc_l8p = csv_valor(A5_LOO, {**_fn, "subamostra": "somente_8_cbo_1_para_1"}, "p_valor")
trecho_a5_frag = (
    f"cai para {decimal_br(loo14_b, 2)}, com $p$ de {decimal_br(loo14_p, 3)}, e ao restringir "
    f"aos oito cursos cuja correspondência com o CBO é estritamente unívoca cai para "
    f"{decimal_br(loo8_b, 2)}, com $p$ de {decimal_br(loo8_p, 3)}"
)

ref_b, loc_rb = csv_valor(A5_REF, {"escala": "nivel", "referencia": "media_12_meses_pre"}, "beta")
ref_p, loc_rp = csv_valor(A5_REF, {"escala": "nivel", "referencia": "media_12_meses_pre"}, "p_valor")
trecho_a5_ref = (
    f"é {decimal_br(ref_b, 2)} com $p$ de {decimal_br(ref_p, 3)}"
)

_fp = {"escala": "proporcional", "competencia": "202603"}
ploo14_b, loc_p14 = csv_valor(A5_LOO, {**_fp, "subamostra": "sem_curso_14"}, "beta")
ploo8_b, loc_p8 = csv_valor(A5_LOO, {**_fp, "subamostra": "somente_8_cbo_1_para_1"}, "beta")
trecho_a5_psobrev = (
    f"{decimal_br(ploo14_b, 3)} sem o curso de radiologia e {decimal_br(ploo8_b, 3)} nos oito "
    f"cursos estritos"
)

registrar("A5_TXT_PRE_F", "Apendice B", "Teste conjunto pre-referencia na escala proporcional",
          decimal_br(a5p_f, 2), A5_JSON, loc_pf, a5p_f, "2 casas", trecho_a5_pre)
registrar("A5_TXT_PRE_P", "Apendice B", "p-valor do teste conjunto pre-referencia proporcional",
          decimal_br(a5p_pp, 3), A5_JSON, loc_ppp, a5p_pp, "3 casas", trecho_a5_pre)

registrar("A5_TXT_PROP_BETA", "Apendice B", "Diferenca proporcional em marco de 2026",
          decimal_br(a5p_b, 3), A5_JSON, loc_pb, a5p_b, "3 casas", trecho_a5_prop)
registrar("A5_TXT_PROP_SE", "Apendice B", "Erro-padrao da diferenca proporcional",
          decimal_br(a5p_se, 3), A5_JSON, loc_pse, a5p_se, "3 casas", trecho_a5_prop)

registrar("A5_TXT_MAR_BETA", "Apendice B", "Diferenca em nivel em marco de 2026",
          decimal_br(a5_beta, 2), A5_EVENTO, loc_b, a5_beta, "2 casas", trecho_a5_mar)
registrar("A5_TXT_MAR_SE", "Apendice B", "Erro-padrao da diferenca em nivel",
          decimal_br(a5_se, 2), A5_EVENTO, loc_s, a5_se, "2 casas", trecho_a5_mar)
registrar("A5_TXT_MAR_P", "Apendice B", "p-valor da diferenca em nivel",
          decimal_br(a5_p, 3), A5_EVENTO, loc_p, a5_p, "3 casas", trecho_a5_mar)

registrar("A5_TXT_LOO14_BETA", "Apendice B", "Nivel sem o curso de radiologia",
          decimal_br(loo14_b, 2), A5_LOO, loc_l14b, loo14_b, "2 casas", trecho_a5_frag)
registrar("A5_TXT_LOO14_P", "Apendice B", "p-valor em nivel sem radiologia",
          decimal_br(loo14_p, 3), A5_LOO, loc_l14p, loo14_p, "3 casas", trecho_a5_frag)
registrar("A5_TXT_LOO8_BETA", "Apendice B", "Nivel nos oito cursos estritos",
          decimal_br(loo8_b, 2), A5_LOO, loc_l8b, loo8_b, "2 casas", trecho_a5_frag)
registrar("A5_TXT_LOO8_P", "Apendice B", "p-valor em nivel nos oito estritos",
          decimal_br(loo8_p, 3), A5_LOO, loc_l8p, loo8_p, "3 casas", trecho_a5_frag)
registrar("A5_TXT_REF_BETA", "Apendice B", "Nivel contra a media dos doze meses pre",
          decimal_br(ref_b, 2), A5_REF, loc_rb, ref_b, "2 casas", trecho_a5_ref)
registrar("A5_TXT_REF_P", "Apendice B", "p-valor contra a media dos doze meses pre",
          decimal_br(ref_p, 3), A5_REF, loc_rp, ref_p, "3 casas", trecho_a5_ref)
registrar("A5_TXT_PLOO14", "Apendice B", "Proporcional sem o curso de radiologia",
          decimal_br(ploo14_b, 3), A5_LOO, loc_p14, ploo14_b, "3 casas", trecho_a5_psobrev)
registrar("A5_TXT_PLOO8", "Apendice B", "Proporcional nos oito cursos estritos",
          decimal_br(ploo8_b, 3), A5_LOO, loc_p8, ploo8_b, "3 casas", trecho_a5_psobrev)

delta_sem_med, loc_dsm = json_valor(A5_JSON, "modelos/distribuicao_delta_confirmatoria/0/mediana")
delta_sem_media, loc_dsa = json_valor(A5_JSON, "modelos/distribuicao_delta_confirmatoria/0/media")
delta_sem_max, loc_dsx = json_valor(A5_JSON, "modelos/distribuicao_delta_confirmatoria/0/max")
delta_com_med, loc_dcm = json_valor(A5_JSON, "modelos/distribuicao_delta_confirmatoria/1/mediana")
delta_com_media, loc_dca = json_valor(A5_JSON, "modelos/distribuicao_delta_confirmatoria/1/media")
delta_com_max, loc_dcx = json_valor(A5_JSON, "modelos/distribuicao_delta_confirmatoria/1/max")
trecho_delta = (
    f"Sem atração, a mediana é {inteiro(delta_sem_med)} e a média é "
    f"{decimal_br(delta_sem_media, 2)}, com máximo de {inteiro(delta_sem_max)}; com atração, "
    f"a mediana é {inteiro(delta_com_med)} e a média é {decimal_br(delta_com_media, 2)}, "
    f"com máximo de {inteiro(delta_com_max)}"
)
for chave, bruto, local, formatado, descricao in [
    ("SEM_MEDIANA", delta_sem_med, loc_dsm, inteiro(delta_sem_med), "Mediana sem atracao"),
    ("SEM_MEDIA", delta_sem_media, loc_dsa, decimal_br(delta_sem_media, 2), "Media sem atracao"),
    ("SEM_MAX", delta_sem_max, loc_dsx, inteiro(delta_sem_max), "Maximo sem atracao"),
    ("COM_MEDIANA", delta_com_med, loc_dcm, inteiro(delta_com_med), "Mediana com atracao"),
    ("COM_MEDIA", delta_com_media, loc_dca, decimal_br(delta_com_media, 2), "Media com atracao"),
    ("COM_MAX", delta_com_max, loc_dcx, inteiro(delta_com_max), "Maximo com atracao"),
]:
    registrar(f"A5_TXT_DELTA_{chave}", "Apendice B", descricao, formatado, A5_JSON, local,
              bruto, "2 casas" if "MEDIA" in chave and "MEDIANA" not in chave else "inteiro",
              trecho_delta)


# --------------------------- Apendice C: RDD do adicional de bolsa (R1, E3, E5)
#
# Este bloco conferia o descarte da RDD (191 dos 368 municipios reproduzidos,
# portao_regra_ivs.json). Aquele diagnostico lia como IVS 2010 o arquivo
# data/ivs_ipea_2010_municipios.csv, que e a linha de um subgrupo populacional e
# nao o IVS do municipio (docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md).
# Com o IVS 2010 oficial a regra se reproduz por inteiro e o artigo reporta a RDD,
# com a mesma formulacao do artigo curto: os trechos abaixo valem para os dois.

RDD_FRACAO = "fracao_celulas_ch1_com_confirmacao_ou_homologacao"
RDD_PRESENCA = "D_k_especialista_ativo_do_ciclo"


def rdd_corte_id(corte: float) -> str:
    """Corte no identificador do registro, sem virgula: 0,300 vira C0300."""
    return f"C{int(round(float(corte) * 1000)):04d}"


def mil_reais(valor: Any) -> str:
    """Valor de bolsa em reais escrito como no artigo: 15000 vira 'R\\$ 15 mil'."""
    bruto = float(valor)
    if bruto % 1000:
        raise SystemExit(f"Valor de bolsa {valor} nao e multiplo de mil reais")
    return f"R\\$ {int(bruto // 1000)} mil"


rdd_cortes, loc_rdd_cortes = json_valor(RDD_E3_STATUS, "cortes")
if [round(float(c), 3) for c in rdd_cortes] != [0.3, 0.4]:
    raise SystemExit(f"E3: o artigo cita os cortes 0,300 e 0,400; o artefato traz {rdd_cortes}")
rdd_c1, rdd_c2 = (float(c) for c in rdd_cortes)
rdd_lado, loc_rdd_lado = json_valor(RDD_E3_STATUS, "lado_do_corte")
if "lado inferior" not in str(rdd_lado):
    raise SystemExit("E3: o artigo poe o proprio corte na faixa de baixo; o artefato diverge")
registrar("RDD_REGRA_CORTES", "Apendice C", "Cortes do IVS que definem a faixa de bolsa",
          f"{decimal_br(rdd_c1, 3)} e {decimal_br(rdd_c2, 3)}", RDD_E3_STATUS,
          f"{loc_rdd_cortes} e {loc_rdd_lado}", rdd_cortes,
          "3 casas; o corte pertence a faixa de baixo e a seguinte comeca no milesimo seguinte",
          f"até {decimal_br(rdd_c1, 3)}, Faixa 3; de {decimal_br(rdd_c1 + 0.001, 3)} a "
          f"{decimal_br(rdd_c2, 3)}, Faixa 2; acima de {decimal_br(rdd_c2, 3)}, Faixa 1")

# Bolsa anunciada por faixa e salto em cada corte.
rdd_grade = {
    faixa: csv_valor(RDD_GRADE, {"faixa_atracao": faixa, "tipo_valor": "valor_anunciado_mensal"},
                     "valor_anunciado_mensal_brl")
    for faixa in (1, 2, 3)
}
rdd_saltos = set(csv_frame(RDD_E3_ESTIM)["salto_anunciado_brl"].astype(int))
if rdd_saltos != {int(rdd_grade[2][0] - rdd_grade[3][0])} or rdd_saltos != {int(rdd_grade[1][0] - rdd_grade[2][0])}:
    raise SystemExit(f"E3: o salto anunciado {rdd_saltos} nao corresponde a grade de bolsas")
rdd_salto = next(iter(rdd_saltos))
trecho_grade = (f"A bolsa anunciada é de {mil_reais(rdd_grade[3][0])}, {mil_reais(rdd_grade[2][0])} ou "
                f"{mil_reais(rdd_grade[1][0])}")
trecho_grade_nota = (f"de {mil_reais(rdd_grade[3][0])} para {mil_reais(rdd_grade[2][0])} em {decimal_br(rdd_c1, 3)} "
                     f"e de {mil_reais(rdd_grade[2][0])} para {mil_reais(rdd_grade[1][0])} em {decimal_br(rdd_c2, 3)}")
for faixa in (3, 2, 1):
    bruto, local = rdd_grade[faixa]
    registrar(f"RDD_BOLSA_FAIXA{faixa}", "Apendice C", f"Bolsa mensal anunciada na Faixa {faixa}",
              mil_reais(bruto), RDD_GRADE, local, bruto, "reais em mil", trecho_grade)
    registrar(f"RDD_BOLSA_NOTA_FAIXA{faixa}", "Tabela C1 (nota)", f"Bolsa da Faixa {faixa} na nota da tabela",
              mil_reais(bruto), RDD_GRADE, local, bruto, "reais em mil", trecho_grade_nota)
registrar("RDD_SALTO_BRL", "Apendice C", "Salto anunciado da bolsa em cada corte", mil_reais(rdd_salto),
          RDD_E3_ESTIM, "coluna salto_anunciado_brl, todas as linhas", rdd_salto, "reais em mil",
          f"Em cada corte, a bolsa sobe {mil_reais(rdd_salto)} de forma determinística")

# Primeiro estagio: escore do MS = IVS oficial; regra reproduzida por inteiro.
rdd_decisao, loc_rdd_decisao = json_valor(RDD_R1, "decisao_r1")
rdd_iguais, loc_rdd_iguais = json_valor(RDD_R1, "escore_administrativo_e_ivs_2010_oficial/valores_iguais_3_casas")
rdd_n_iguais, rdd_d_iguais = (int(x) for x in str(rdd_iguais).split("/"))
rdd_p1, loc_rdd_p1 = json_valor(RDD_R1, "populacoes/P1/municipios")
rdd_p1_regra, _ = json_valor(RDD_R1, "populacoes/P1/regra_reproduz")
rdd_p2, loc_rdd_p2 = json_valor(RDD_R1, "populacoes/P2/municipios")
rdd_p2_regra, _ = json_valor(RDD_R1, "populacoes/P2/regra_reproduz")
if (rdd_decisao != "APROVADO_SHARP" or rdd_n_iguais != rdd_d_iguais
        or rdd_p1_regra != rdd_p1 or rdd_p2_regra != rdd_p2):
    raise SystemExit("R1: o artigo afirma reproducao integral da regra e do escore; o artefato diverge")
registrar("RDD_R1_ESCORE_MS", "Apendice C", "Municipios com escore do MS igual ao IVS 2010 oficial",
          inteiro(rdd_n_iguais), RDD_R1, loc_rdd_iguais, rdd_iguais, "inteiro",
          f"coincide com o IVS 2010 oficial nos {inteiro(rdd_n_iguais)} municípios em que aparece")
trecho_rdd_regra = (f"a regra reproduz a faixa anunciada nos {inteiro(rdd_p1)} municípios do quadro da primeira "
                    f"chamada do ciclo 1 e nos {inteiro(rdd_p2)} do ciclo 2")
registrar("RDD_R1_REGRA_P1", "Apendice C", "Municipios do ciclo 1 com a faixa reproduzida", inteiro(rdd_p1),
          RDD_R1, loc_rdd_p1, rdd_p1, "inteiro; decisao_r1 = APROVADO_SHARP", trecho_rdd_regra)
registrar("RDD_R1_REGRA_P2", "Apendice C", "Municipios do ciclo 2 com a faixa reproduzida", inteiro(rdd_p2),
          RDD_R1, loc_rdd_p2, rdd_p2, "inteiro; decisao_r1 = APROVADO_SHARP", trecho_rdd_regra)

# Desfecho secundario e janela.
rdd_dk, loc_rdd_dk = json_valor(RDD_PROTOCOLO, "outcome/D_k")
if "09/10/2026" not in str(rdd_dk):
    raise SystemExit("Protocolo da RDD: a data da relacao nominal de ativos mudou")
registrar("RDD_DATA_RELACAO", "Apendice C", "Data da relacao nominal usada na presenca", "9 de outubro de 2026",
          RDD_PROTOCOLO, loc_rdd_dk, "09/10/2026", "data escrita por extenso",
          "relação nominal de 9 de outubro de 2026")
rdd_h, loc_rdd_h = json_valor(RDD_E3_STATUS, "janelas/principal")
registrar("RDD_JANELA", "Apendice C", "Janela principal da estimacao local linear", decimal_br(rdd_h, 3),
          RDD_E3_STATUS, loc_rdd_h, rdd_h, "3 casas",
          f"janela de {decimal_br(rdd_h, 3)} de IVS de cada lado do corte")

# Densidade e balanco no ciclo 1; o IVS 2010 oficial e a propria running
# variable e nao entra na contagem do balanco.
rdd_dens = {}
for corte in (rdd_c1, rdd_c2):
    filtro = {"populacao": "P1", "diagnostico": "densidade_poisson_mass_points", "h": str(rdd_h), "corte": str(corte)}
    rdd_dens[corte] = {campo: csv_valor(RDD_E3_DIAG, filtro, campo) for campo in ("rho", "rho_ic95_inf", "rho_ic95_sup")}
trecho_rdd_dens = (
    f"com razões de {decimal_br(rdd_dens[rdd_c1]['rho'][0], 2)} [{decimal_br(rdd_dens[rdd_c1]['rho_ic95_inf'][0], 2)}; "
    f"{decimal_br(rdd_dens[rdd_c1]['rho_ic95_sup'][0], 2)}] em {decimal_br(rdd_c1, 3)} e de "
    f"{decimal_br(rdd_dens[rdd_c2]['rho'][0], 2)} [{decimal_br(rdd_dens[rdd_c2]['rho_ic95_inf'][0], 2)}; "
    f"{decimal_br(rdd_dens[rdd_c2]['rho_ic95_sup'][0], 2)}] em {decimal_br(rdd_c2, 3)}"
)
for corte in (rdd_c1, rdd_c2):
    for campo, (bruto, local) in rdd_dens[corte].items():
        registrar(f"RDD_DENS_{rdd_corte_id(corte)}_{campo}", "Apendice C", f"Densidade: {campo} em {corte}",
                  decimal_br(bruto, 2), RDD_E3_DIAG, local, bruto, "2 casas", trecho_rdd_dens)

rdd_diag = csv_frame(RDD_E3_DIAG)
rdd_bal = rdd_diag[rdd_diag["diagnostico"].eq("balanco_covariavel_pre") & rdd_diag["populacao"].eq("P1")
                   & rdd_diag["h"].round(3).eq(round(float(rdd_h), 3)) & rdd_diag["variavel"].ne("ivs_2010")]
rdd_n_cov = {c: int(rdd_bal["corte"].round(3).eq(round(c, 3)).sum()) for c in (rdd_c1, rdd_c2)}
rdd_n_rej = {c: int((rdd_bal["corte"].round(3).eq(round(c, 3)) & rdd_bal["p_valor"].lt(0.05)).sum())
             for c in (rdd_c1, rdd_c2)}
if rdd_n_cov != {rdd_c1: 9, rdd_c2: 9} or rdd_n_rej != {rdd_c1: 0, rdd_c2: 3}:
    raise SystemExit(f"E3: o artigo cita 9 covariaveis, 0 e 3 com p<0,05; o artefato traz {rdd_n_cov} e {rdd_n_rej}")
registrar("RDD_BALANCO", "Apendice C", "Covariaveis pre com p<0,05 por corte (ciclo 1)", "nove; nenhuma; três",
          RDD_E3_DIAG, "diagnostico balanco_covariavel_pre, P1, sem ivs_2010", f"{rdd_n_cov}; {rdd_n_rej}",
          "contagem por extenso",
          f"No balanço de nove covariáveis anteriores ao programa, nenhuma difere a 5\\% no corte de "
          f"{decimal_br(rdd_c1, 3)}; no de {decimal_br(rdd_c2, 3)}, três diferem")


# Tabela C1: desfecho da hipotese e presenca, janela principal. Os
# identificadores RDD_TAB_* sao o nucleo que o artigo curto reutiliza.
def rdd_valor(populacao: str, outcome: str, corte: float, campo: str) -> tuple[Any, str]:
    return csv_valor(RDD_E3_ESTIM, {"populacao": populacao, "outcome": outcome, "corte": str(corte),
                                    "h": str(rdd_h), "especificacao": "principal"}, campo)


for rotulo, chave, outcome, populacao in [("Células preenchidas, ciclo 1", "PREENCH", RDD_FRACAO, "P1"),
                                          ("Presença, ciclo 1", "PRESENCA", RDD_PRESENCA, "P1"),
                                          ("Presença, ciclo 2", "PRESENCA", RDD_PRESENCA, "P2")]:
    for corte in (rdd_c1, rdd_c2):
        registrar_linha_csv(
            f"RDD_TAB_{populacao}_{chave}_{rdd_corte_id(corte)}",
            "Tabela C1 (bolsa)",
            RDD_E3_ESTIM,
            {"populacao": populacao, "outcome": outcome, "corte": str(corte), "h": str(rdd_h),
             "especificacao": "principal"},
            [
                ("n_abaixo", "n_abaixo", "inteiro", inteiro),
                ("n_acima", "n_acima", "inteiro", inteiro),
                ("media_abaixo", "media_bruta_abaixo", "proporcao x100, 1 casa", pontos),
                ("media_acima", "media_bruta_acima", "proporcao x100, 1 casa", pontos),
                ("tau", "tau", "proporcao x100, 1 casa", pontos),
                ("lo", "ic95_inf", "proporcao x100, 1 casa", pontos),
                ("hi", "ic95_sup", "proporcao x100, 1 casa", pontos),
                ("p", "p_valor", "3 casas", lambda valor: decimal_br(valor, 3)),
            ],
            f"{rotulo} & {decimal_br(corte, 3)} & {{n_abaixo}}/{{n_acima}} & {{media_abaixo}} & {{media_acima}}"
            " & {tau} & [{lo}; {hi}] & {p} \\\\",
        )

# Texto, resumo e conclusao do apendice: o desfecho da hipotese.
rdd_y = {corte: {campo: rdd_valor("P1", RDD_FRACAO, corte, campo)
                 for campo in ("tau", "ic95_inf", "ic95_sup", "media_bruta_abaixo", "media_bruta_acima",
                               "n_abaixo", "n_acima")}
         for corte in (rdd_c1, rdd_c2)}
rdd_y1, rdd_y2 = rdd_y[rdd_c1], rdd_y[rdd_c2]
trecho_rdd_resumo = (f"primeira chamada é de {pontos(rdd_y1['tau'][0])} pontos percentuais no corte de "
                     f"{decimal_br(rdd_c1, 3)} e de {pontos(rdd_y2['tau'][0])} no de {decimal_br(rdd_c2, 3)}")
trecho_rdd_txt = (f"o salto é de {pontos(rdd_y1['tau'][0])} pontos percentuais no corte de {decimal_br(rdd_c1, 3)}, com "
                  f"intervalo de [{pontos(rdd_y1['ic95_inf'][0])}; {pontos(rdd_y1['ic95_sup'][0])}], e de {pontos(rdd_y2['tau'][0])} "
                  f"no de {decimal_br(rdd_c2, 3)}, com intervalo de [{pontos(rdd_y2['ic95_inf'][0])}; "
                  f"{pontos(rdd_y2['ic95_sup'][0])}]")
for corte, v in ((rdd_c1, rdd_y1), (rdd_c2, rdd_y2)):
    registrar(f"RDD_RESUMO_{rdd_corte_id(corte)}", "Resumo", f"Salto no preenchimento em {corte}",
              pontos(v["tau"][0]), RDD_E3_ESTIM, v["tau"][1], v["tau"][0], "proporcao x100, 1 casa",
              trecho_rdd_resumo)
    for campo in ("tau", "ic95_inf", "ic95_sup"):
        registrar(f"RDD_TXT_{rdd_corte_id(corte)}_{campo}", "Apendice C", f"{campo} do preenchimento em {corte}",
                  pontos(v[campo][0]), RDD_E3_ESTIM, v[campo][1], v[campo][0], "proporcao x100, 1 casa",
                  trecho_rdd_txt)
trecho_rdd_medias = (f"a fração média é de {pontos(rdd_y1['media_bruta_abaixo'][0])}\\% abaixo e "
                     f"{pontos(rdd_y1['media_bruta_acima'][0])}\\% acima")
for campo in ("media_bruta_abaixo", "media_bruta_acima"):
    registrar(f"RDD_TXT_MEDIA_{campo}", "Apendice C", f"{campo} do preenchimento em {rdd_c1}",
              pontos(rdd_y1[campo][0]), RDD_E3_ESTIM, rdd_y1[campo][1], rdd_y1[campo][0], "proporcao x100, 1 casa",
              trecho_rdd_medias)
rdd_ns = [int(v[k][0]) for v in (rdd_y1, rdd_y2) for k in ("n_abaixo", "n_acima")]
registrar("RDD_TXT_N_FAIXA", "Apendice C", "Municipios por lado de cada corte na janela",
          f"{min(rdd_ns)} e {max(rdd_ns)}", RDD_E3_ESTIM, "n_abaixo e n_acima do preenchimento", rdd_ns,
          "minimo e maximo", f"há entre {min(rdd_ns)} e {max(rdd_ns)} municípios de cada lado")

# E5 (exploratorio, pos-resultado): MDE do principal, fator do EP,
# especificacoes alternativas e limites superiores.
rdd_s0 = {corte: {campo: csv_valor(RDD_E5_ESPEC, {"outcome": "Y1", "especificacao": "S0", "corte": str(corte)}, campo)
                  for campo in ("mde_80", "lim_sup_unilateral_95")}
          for corte in (rdd_c1, rdd_c2)}
trecho_rdd_mde = (f"é de {pontos(rdd_s0[rdd_c1]['mde_80'][0])} e {pontos(rdd_s0[rdd_c2]['mde_80'][0])} "
                  f"pontos percentuais")
for corte in (rdd_c1, rdd_c2):
    bruto, local = rdd_s0[corte]["mde_80"]
    registrar(f"RDD_MDE_{rdd_corte_id(corte)}", "Apendice C", f"MDE do principal em {corte}", pontos(bruto),
              RDD_E5_ESPEC, local, bruto, "proporcao x100, 1 casa", trecho_rdd_mde)
rdd_razao = {corte: csv_valor(RDD_E5_DECOMP, {"componente": "LL_triangular_principal", "corte": str(corte)},
                              "razao_ep_vs_dm_simples")
             for corte in (rdd_c1, rdd_c2)}
trecho_rdd_razao = (f"multiplica o erro-padrão por {decimal_br(rdd_razao[rdd_c1][0], 1)} e por "
                    f"{decimal_br(rdd_razao[rdd_c2][0], 1)} em relação a uma diferença de médias simples")
for corte in (rdd_c1, rdd_c2):
    bruto, local = rdd_razao[corte]
    registrar(f"RDD_RAZAO_EP_{rdd_corte_id(corte)}", "Apendice C",
              f"EP local linear sobre EP da diferenca de medias em {corte}", decimal_br(bruto, 1),
              RDD_E5_DECOMP, local, bruto, "1 casa", trecho_rdd_razao)
rdd_e5 = csv_frame(RDD_E5_ESPEC)
rdd_e5_y1 = rdd_e5[rdd_e5["outcome"].eq("Y1")]
rdd_e5_expl = rdd_e5_y1[rdd_e5_y1["rotulo"].eq("EXPLORATORIO_POS_RESULTADO")]
if (rdd_e5_y1["p_valor"] < 0.05).any() or rdd_e5_y1["descarta_tau_ge_010"].astype(bool).any():
    raise SystemExit("E5: o artigo afirma nenhum p<0,05 e nenhum descarte de +10 p.p.; o artefato diverge")
trecho_rdd_expl = (f"nenhuma das {len(rdd_e5_expl)} especificações alternativas do desfecho da hipótese produz "
                   f"salto distinguível de zero; o menor $p$ é {decimal_br(rdd_e5_expl['p_valor'].min(), 2)}")
registrar("RDD_E5_N", "Apendice C", "Especificacoes exploratorias do preenchimento", inteiro(len(rdd_e5_expl)),
          RDD_E5_ESPEC, "outcome=Y1, rotulo=EXPLORATORIO_POS_RESULTADO", len(rdd_e5_expl), "contagem",
          trecho_rdd_expl)
registrar("RDD_E5_PMIN", "Apendice C", "Menor p das especificacoes exploratorias",
          decimal_br(rdd_e5_expl["p_valor"].min(), 2), RDD_E5_ESPEC, "minimo de p_valor nas exploratorias de Y1",
          float(rdd_e5_expl["p_valor"].min()), "2 casas", trecho_rdd_expl)
rdd_lim_b, loc_rdd_lim_b = csv_valor(RDD_E5_ESPEC, {"outcome": "Y1", "especificacao": "B"}, "lim_sup_unilateral_95")
trecho_rdd_lim = (f"o limite superior unilateral de 95\\% do principal é de "
                  f"{pontos(rdd_s0[rdd_c1]['lim_sup_unilateral_95'][0])} pontos percentuais no corte de "
                  f"{decimal_br(rdd_c1, 3)} e de {pontos(rdd_s0[rdd_c2]['lim_sup_unilateral_95'][0])} no de "
                  f"{decimal_br(rdd_c2, 3)}; com os cortes empilhados, é de {pontos(rdd_lim_b)} para a média "
                  f"dos dois saltos")
for corte in (rdd_c1, rdd_c2):
    bruto, local = rdd_s0[corte]["lim_sup_unilateral_95"]
    registrar(f"RDD_LIMSUP_{rdd_corte_id(corte)}", "Apendice C", f"Limite superior unilateral do principal em {corte}",
              pontos(bruto), RDD_E5_ESPEC, local, bruto, "proporcao x100, 1 casa", trecho_rdd_lim)
registrar("RDD_LIMSUP_EMPILHADO", "Apendice C", "Limite superior unilateral com os cortes empilhados",
          pontos(rdd_lim_b), RDD_E5_ESPEC, loc_rdd_lim_b, rdd_lim_b, "proporcao x100, 1 casa", trecho_rdd_lim)


# ------------------- Apendice C: rodada multi-outcome da bolsa (E6, E7, E8, E9)
#
# Protocolo congelado em docs/06_execucao/40; sintese em docs/06_execucao/44.
# Os numeros vem das saidas do E8 (que so copia e conta as do E6, E7 e E9, e
# faz o Holm); P1, P2 e as razoes de chances do E9 sao reconferidas aqui contra
# as saidas de origem. As frases qualitativas (descarta, nao descarta,
# sobrevive, fragil) tem guarda: se o artefato mudar, o conferidor para.
# Os trechos MO_* valem para os dois artigos: o curto reutiliza os que repete.

MO_E8_RESUMO = "output/rdd_bolsa/E8_resumo.json"
MO_E8_TABELA = "output/rdd_bolsa/E8_tabela_sintese.csv"
MO_E6_RESUMO = "output/rdd_bolsa/E6_resumo.json"
MO_E7_RESUMO = "output/rdd_bolsa/E7_resumo.json"
MO_E9_EFM = "output/rdd_bolsa/E9_efeitos_marginais.csv"
MO_PROTOCOLO = "output/rdd_bolsa/protocolo_E6_multioutcome.json"

MO_MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
            "setembro", "outubro", "novembro", "dezembro"]
MO_EXTENSO = {2: "dois", 3: "três", 4: "quatro", 5: "cinco", 6: "seis"}


def mo_mes(competencia: str) -> str:
    """'2025-10', '202510' ou '2025-10-18' -> 'outubro de 2025' (dia, se houver, a parte)."""
    digitos = str(competencia).replace("-", "")
    return f"{MO_MESES[int(digitos[4:6]) - 1]} de {digitos[:4]}"


def mo_data(data_iso: str) -> str:
    """'2026-10-18' -> '18 de outubro de 2026'."""
    return f"{int(str(data_iso)[8:10])} de {mo_mes(data_iso)}"


def mo_exigir(condicao: bool, mensagem: str) -> None:
    if not condicao:
        raise SystemExit(f"Rodada multi-outcome: {mensagem}; o texto dos artigos deixou de valer")


def mo_e8(caminho: str) -> tuple[Any, str]:
    return json_valor(MO_E8_RESUMO, caminho)


def mo_p(valor: float) -> str:
    """p com 3 casas; abaixo de 0,001 o artigo escreve '$<$0,001'."""
    return "$<$0,001" if float(valor) < 0.001 else decimal_br(valor, 3)


def mo_fmt(valor: float, unidade: str) -> str:
    """Formato do E8 por unidade: fracao em p.p. com 1 casa, DP com 2, horas com 1, demais com 3."""
    if str(unidade).startswith("fracao"):
        return pontos(valor)
    if str(unidade).startswith("desvios"):
        return decimal_br(valor, 2)
    if str(unidade).startswith("horas"):
        return decimal_br(valor, 1)
    return decimal_br(valor, 3)


def mo_transf(unidade: str) -> str:
    return {"fracao": "proporcao x100, 1 casa", "desvios": "2 casas", "horas": "1 casa"}.get(
        str(unidade).split(" ")[0].split("-")[0], "3 casas")


def mo_registrar(prefixo: str, bloco: str, trecho: str,
                 itens: list[tuple[str, str, Any, str, str, str]]) -> None:
    """Um registro por numero do trecho: (chave, formatado, bruto, fonte, localizador, transformacao)."""
    for chave, formatado, bruto, fonte, local, transformacao in itens:
        mo_exigir(formatado in trecho, f"{prefixo}_{chave}: '{formatado}' fora do trecho")
        registrar(f"{prefixo}_{chave}", bloco, f"{prefixo}: {chave}", formatado, fonte, local, bruto,
                  transformacao, trecho)


def mo_linha(outcome_id: str, populacao: str, ciclo: str | None = None) -> dict[str, tuple[Any, str]]:
    filtros = {"outcome_id": outcome_id, "populacao": populacao}
    if ciclo is not None:
        filtros["ciclo"] = ciclo
    return {campo: csv_valor(MO_E8_TABELA, filtros, campo)
            for campo in ("estimativa", "ic95_inf", "ic95_sup", "p_valor", "q_bky", "p_holm", "unidade")}


# Protocolo: data de congelamento, janelas da DiRD e referencia de magnitude.
mo_congel, loc_mo_congel = json_valor(MO_PROTOCOLO, "data_congelamento")
mo_registrar("MO_PROTOCOLO_DATA", "Apendice C (multi-outcome)",
             f"congelado em {mo_data(mo_congel)} antes de abrir os desfechos novos",
             [("DATA", mo_data(mo_congel), mo_congel, MO_PROTOCOLO, loc_mo_congel, "data por extenso")])
mo_pre, loc_mo_pre = json_valor(MO_E7_RESUMO, "parametros/pre")
mo_pos, loc_mo_pos = json_valor(MO_E7_RESUMO, "parametros/pos")
mo_ref, loc_mo_ref = json_valor(MO_E7_RESUMO, "parametros/ref")
mo_pre_extra, loc_mo_pre_extra = json_valor(MO_E7_RESUMO, "parametros/pre_extra")
mo_janelas = [("PRE_INI", mo_mes(mo_pre[0]), mo_pre[0], MO_E7_RESUMO, f"{loc_mo_pre}/0", "competencia por extenso"),
              ("PRE_FIM", mo_mes(mo_pre[-1]), mo_pre[-1], MO_E7_RESUMO, f"{loc_mo_pre}/-1", "competencia por extenso"),
              ("POS_INI", mo_mes(mo_pos[0]), mo_pos[0], MO_E7_RESUMO, f"{loc_mo_pos}/0", "competencia por extenso"),
              ("POS_FIM", mo_mes(mo_pos[-1]), mo_pos[-1], MO_E7_RESUMO, f"{loc_mo_pos}/-1", "competencia por extenso")]
mo_registrar("MO_JANELAS_TXT", "Apendice C (multi-outcome)",
             f"entre a média de {mo_mes(mo_pre[0])} a {mo_mes(mo_pre[-1])} e a de {mo_mes(mo_pos[0])} a "
             f"{mo_mes(mo_pos[-1])}", mo_janelas)
mo_registrar("MO_JANELAS_NOTA", "Tabela C2 (nota)",
             f"diferença entre a média de {mo_mes(mo_pos[0])} a {mo_mes(mo_pos[-1])} e a de {mo_mes(mo_pre[0])} a "
             f"{mo_mes(mo_pre[-1])} no CNES", mo_janelas)
mo_ref_pp, loc_mo_ref_pp = mo_e8("descarte/referencias/preenchimento_pp")
mo_ref_prot, _ = json_valor(MO_PROTOCOLO, "testes_multiplos/referencias_magnitude/preenchimento")
mo_exigir(mo_ref_prot.replace(" ", "") == f"+{inteiro(float(mo_ref_pp) * 100)}p.p.",
          "a referencia de preenchimento do E8 difere da do protocolo")
MO_REF_TXT = inteiro(float(mo_ref_pp) * 100)
mo_item_ref = ("REF", MO_REF_TXT, mo_ref_pp, MO_E8_RESUMO, loc_mo_ref_pp, "proporcao x100, inteiro")
mo_registrar("MO_REFERENCIA", "Apendice C (multi-outcome)",
             f"A referência de magnitude fixada de antemão é um aumento de {MO_REF_TXT} pontos percentuais no "
             f"preenchimento", [mo_item_ref])

# Holm: P1 e P2, reconferidos contra o E6 e o E7.
mo_holm = {k: {c: mo_e8(f"holm/{k}/{c}") for c in ("tau", "ic95_inf", "ic95_sup", "p_valor", "p_holm")}
           for k in ("P1", "P2")}
for chave, rel, campo in (("P1", MO_E6_RESUMO, "p1_para_holm"), ("P2", MO_E7_RESUMO, "p2_para_holm")):
    for c in ("tau", "ic95_inf", "ic95_sup", "p_valor"):
        origem, _ = json_valor(rel, f"{campo}/{c}")
        mo_exigir(abs(float(origem) - float(mo_holm[chave][c][0])) < 1e-12, f"{chave}.{c} do E8 difere de {rel}")
mo_exigir(not mo_e8("holm/alguma_rejeitada")[0], "o Holm rejeitou alguma primaria")
mo_exigir(decimal_br(mo_holm["P1"]["p_holm"][0], 3) == decimal_br(mo_holm["P2"]["p_holm"][0], 3),
          "o texto diz o mesmo p de Holm para as duas primarias")


def mo_itens_holm(com_ic: bool = True) -> list[tuple[str, str, Any, str, str, str]]:
    itens = []
    for k, casas in (("P1", 2), ("P2", 3)):
        campos = ("tau", "ic95_inf", "ic95_sup", "p_valor") if com_ic else ()
        for c in campos:
            bruto, local = mo_holm[k][c]
            fmt = decimal_br(bruto, 3) if c == "p_valor" else decimal_br(bruto, casas)
            itens.append((f"{k}_{c}", fmt, bruto, MO_E8_RESUMO, local, "3 casas" if c == "p_valor" else f"{casas} casas"))
        bruto, local = mo_holm[k]["p_holm"]
        itens.append((f"{k}_p_holm", decimal_br(bruto, 3), bruto, MO_E8_RESUMO, local, "3 casas"))
    return itens


h1, h2 = mo_holm["P1"], mo_holm["P2"]
mo_registrar("MO_HOLM_TXT", "Apendice C (multi-outcome)",
             f"o índice P1 tem salto de {decimal_br(h1['tau'][0], 2)} desvio-padrão, com intervalo de "
             f"[{decimal_br(h1['ic95_inf'][0], 2)}; {decimal_br(h1['ic95_sup'][0], 2)}] e $p$ de "
             f"{decimal_br(h1['p_valor'][0], 3)}, e P2 tem salto de {decimal_br(h2['tau'][0], 3)} vínculo por 10 mil "
             f"habitantes, com intervalo de [{decimal_br(h2['ic95_inf'][0], 3)}; {decimal_br(h2['ic95_sup'][0], 3)}] e "
             f"$p$ de {decimal_br(h2['p_valor'][0], 3)}; o $p$ ajustado por Holm é de "
             f"{decimal_br(h1['p_holm'][0], 3)} para os dois", mo_itens_holm())
mo_registrar("MO_HOLM_RESUMO", "Resumo",
             f"não rejeita zero nos dois testes primários depois da correção de Holm ($p$ ajustado de "
             f"{decimal_br(h1['p_holm'][0], 3)} em ambos); o intervalo convencional do preenchimento empilhado "
             f"exclui ganhos de {MO_REF_TXT} pontos percentuais", mo_itens_holm(False) + [mo_item_ref])

# Tabela C2: primarias e componentes (linhas da tabela-sintese do E8).
MO_LINHAS_TAB = [
    ("P1", "V1+V2+V3", None, "P1: índice de atração--presença (DP)", "p_holm"),
    ("F3.1", "U", None, "P2: vínculos nas CBO-alvo por 10 mil hab., DiRD", "p_holm"),
    ("F1.1", "V1+V2+V3", None, "Candidatos de 1ª opção por célula", "q_bky"),
    ("F1.2", "V1+V2+V3", None, "Células com candidato (p.p.)", "q_bky"),
    ("F1.3", "V1+V2+V3", None, "Células preenchidas na 1ª chamada (p.p.)", "q_bky"),
    ("F1.4", "V1+V2", None, "Células preenchidas até a 2ª chamada (p.p.)", "q_bky"),
    ("F2.1", "V1+V2", None, "Especialistas ativos por célula", "q_bky"),
    ("F2.3", "V1+V2", None, "Algum especialista ativo (p.p.)", "q_bky"),
    ("F3.2", "U", None, "Município com especialista nas CBO-alvo (p.p.), DiRD", "q_bky"),
    ("F3.3", "U", None, "Horas SUS nas CBO-alvo por 10 mil hab., DiRD", "q_bky"),
    ("F3.P1", "U", None, "Placebo: generalistas por 10 mil hab., DiRD", "q_bky"),
    ("F3.P2", "U", None, "Placebo: especialistas fora das CBO-alvo, DiRD", "q_bky"),
    ("F0.2", "U", "1", "Vagas imediatas do ciclo 1 por 10 mil hab.", "q_bky"),
    ("F4.2", "V1+V2+V3", None, "Nota dos candidatos de 1ª opção", "q_bky"),
]
MO_TAB: dict[str, dict[str, tuple[Any, str]]] = {}
for outcome_id, populacao, ciclo, rotulo, ajuste in MO_LINHAS_TAB:
    v = mo_linha(outcome_id, populacao, ciclo)
    MO_TAB[outcome_id] = v
    unidade = v["unidade"][0]
    fmts = {"tau": mo_fmt(v["estimativa"][0], unidade), "lo": mo_fmt(v["ic95_inf"][0], unidade),
            "hi": mo_fmt(v["ic95_sup"][0], unidade), "p": decimal_br(v["p_valor"][0], 3),
            "aj": decimal_br(v[ajuste][0], 3)}
    mo_exigir(float(v["p_valor"][0]) >= 0.001, f"{outcome_id}: p abaixo de 0,001 pede outro formato")
    trecho = (f"{rotulo} & {populacao} & {fmts['tau']} & [{fmts['lo']}; {fmts['hi']}] & {fmts['p']} & "
              f"{fmts['aj']} \\\\")
    itens = []
    for chave, campo in (("tau", "estimativa"), ("lo", "ic95_inf"), ("hi", "ic95_sup"), ("p", "p_valor"), ("aj", ajuste)):
        bruto, local = v[campo]
        transf = mo_transf(unidade) if chave in ("tau", "lo", "hi") else "3 casas"
        itens.append((chave, fmts[chave], bruto, MO_E8_TABELA, local, transf))
    mo_registrar(f"MO_TAB_{outcome_id.replace('.', '_')}_{populacao.replace('+', '')}", "Tabela C2 (multi-outcome)",
                 trecho, itens)
for oid in ("F3.1", "F3.2", "F3.3", "F3.P1", "F3.P2"):
    mo_exigir(float(MO_TAB[oid]["p_valor"][0]) >= 0.05, f"{oid}: o texto diz que a DiRD nao detecta mudanca")
registrar("MO_DIRD_NULA", "Apendice C (multi-outcome)", "DiRD sem efeito detectavel em F3 e nos placebos (U)",
          "nao detecta", MO_E8_TABELA, "p_valor das linhas F3.1, F3.2, F3.3, F3.P1 e F3.P2 em U",
          [float(MO_TAB[o]["p_valor"][0]) for o in ("F3.1", "F3.2", "F3.3", "F3.P1", "F3.P2")], "guarda: p >= 0,05",
          "diferença em descontinuidades não detecta mudança na oferta das ocupações-alvo nem nos")
mo_exigir(float(MO_TAB["F0.2"]["p_valor"][0]) < 0.05 and float(MO_TAB["F4.2"]["p_valor"][0]) < 0.05,
          "o texto cita vagas imediatas e nota dos candidatos entre os p isolados abaixo de 5%")

# Familias: nenhuma com q < 0,05; contagem de testes por familia.
mo_familias, loc_mo_fam = mo_e8("familias")
mo_exigir(all(int(f["resumo_testes"]["q_menor_005"]) == 0 for f in mo_familias.values()),
          "alguma familia tem q BKY < 0,05")
mo_n_testes = [int(f["resumo_testes"]["linhas_principais_no_bky"]) for f in mo_familias.values()]
mo_registrar("MO_FAMILIAS", "Apendice C (multi-outcome)",
             f"Nas {MO_EXTENSO[len(mo_familias)]} famílias de desfechos do protocolo, com {min(mo_n_testes)} a "
             f"{max(mo_n_testes)} testes cada, nenhum valor $q$ fica abaixo de 5\\%",
             [("N", MO_EXTENSO[len(mo_familias)], len(mo_familias), MO_E8_RESUMO, loc_mo_fam, "contagem por extenso"),
              ("MIN", inteiro(min(mo_n_testes)), mo_n_testes, MO_E8_RESUMO,
               f"{loc_mo_fam}/*/resumo_testes/linhas_principais_no_bky", "minimo"),
              ("MAX", inteiro(max(mo_n_testes)), mo_n_testes, MO_E8_RESUMO,
               f"{loc_mo_fam}/*/resumo_testes/linhas_principais_no_bky", "maximo")])

# Descarte de +10 p.p. com ciclos e cortes empilhados (F1.3), e o que nao descarta.
mo_desc, loc_mo_desc = mo_e8("descarte/preenchimento")
mo_d = {(d["outcome_id"], d["populacao"]): (i, d) for i, d in enumerate(mo_desc)}
i_emp, d_emp = mo_d[("F1.3", "V1+V2+V3")]
mo_exigir(d_emp["exclui_referencia"] and d_emp["todas_convencionais_excluem_referencia"]
          and d_emp["convencionais_todas_com_salto_negativo"], "F1.3 empilhado deixou de descartar +10 p.p.")
mo_exigir(not any(d["ic_honesto_exclui_referencia"] for d in mo_desc), "algum IC honesto passou a descartar")
mo_exigir(not mo_d[("F1.3", "V1")][1]["exclui_referencia"] and not mo_d[("F1.3", "V2")][1]["exclui_referencia"],
          "o texto diz que, nos ciclos 1 e 2 isolados, o IC ainda admite +10 p.p.")
loc_emp = f"{loc_mo_desc}/{i_emp}"
mo_registrar("MO_DESCARTE_EMPILHADO", "Apendice C (multi-outcome)",
             f"o salto na fração de células preenchidas na primeira chamada é de {pontos(d_emp['tau'])} pontos "
             f"percentuais, com intervalo de [{pontos(d_emp['ic95_inf'])}; {pontos(d_emp['ic95_sup'])}]: um aumento "
             f"de {MO_REF_TXT} pontos percentuais fica fora do intervalo convencional",
             [("TAU", pontos(d_emp["tau"]), d_emp["tau"], MO_E8_RESUMO, f"{loc_emp}/tau", "proporcao x100, 1 casa"),
              ("LO", pontos(d_emp["ic95_inf"]), d_emp["ic95_inf"], MO_E8_RESUMO, f"{loc_emp}/ic95_inf", "proporcao x100, 1 casa"),
              ("HI", pontos(d_emp["ic95_sup"]), d_emp["ic95_sup"], MO_E8_RESUMO, f"{loc_emp}/ic95_sup", "proporcao x100, 1 casa"),
              mo_item_ref])
mo_registrar("MO_DESCARTE_ESPECS", "Apendice C (multi-outcome)",
             f"de cada uma das {inteiro(d_emp['n_especificacoes_convencionais'])} especificações convencionais do "
             f"protocolo, todas com salto negativo",
             [("N", inteiro(d_emp["n_especificacoes_convencionais"]), d_emp["n_especificacoes_convencionais"],
               MO_E8_RESUMO, f"{loc_emp}/n_especificacoes_convencionais", "inteiro")])
registrar("MO_HONESTO_NAO_DESCARTA", "Apendice C (multi-outcome)", "IC honesto (M do protocolo) nao descarta +10 p.p.",
          "não descarta", MO_E8_RESUMO, f"{loc_mo_desc}/*/ic_honesto_exclui_referencia",
          [d["ic_honesto_exclui_referencia"] for d in mo_desc], "guarda booleana",
          "intervalo honesto com a constante do protocolo não descarta nada")
mo_registrar("MO_CICLOS_ISOLADOS", "Apendice C (multi-outcome)",
             f"nos ciclos 1 e 2, o intervalo convencional ainda admite {MO_REF_TXT} pontos percentuais",
             [mo_item_ref])
mo_registrar("MO_CONCLUSAO_DESCARTE", "Conclusao",
             f"o intervalo convencional exclui ganhos de preenchimento de {MO_REF_TXT} pontos percentuais",
             [mo_item_ref])
mo_registrar("MO_E5_CICLO1", "Apendice C",
             f"Nenhuma especificação restrita ao ciclo 1 descarta efeitos de {MO_REF_TXT} pontos percentuais",
             [mo_item_ref])

# P2 relativo a media do pre.
mo_rel = {c: mo_e8(f"e7/p2_sup_relativo_media_pre/{c}/razao_sup_p2") for c in ("0.300", "0.400")}
mo_registrar("MO_P2_RELATIVO", "Apendice C (multi-outcome)",
             f"equivale a {pontos(mo_rel['0.300'][0])}\\% da média do pré abaixo do corte de {decimal_br(rdd_c1, 3)} e "
             f"a {pontos(mo_rel['0.400'][0])}\\% da média abaixo do de {decimal_br(rdd_c2, 3)}",
             [(f"C{c[2:]}", pontos(b), b, MO_E8_RESUMO, l, "proporcao x100, 1 casa") for c, (b, l) in mo_rel.items()])

# Selecao em V1 no corte de 0,400.
mo_vg = {c: mo_e8(f"selecao_v1_0400/vagas_imediatas_c1_0400/{c}") for c in ("tau", "ic95_inf", "ic95_sup")}
mo_dens, loc_mo_dens = mo_e8("selecao_v1_0400/densidade_V1_0400/razao")
mo_bal_n, loc_mo_bal_n = mo_e8("selecao_v1_0400/balanco_V1_0400/covariaveis_testadas")
mo_bal_r, loc_mo_bal_r = mo_e8("selecao_v1_0400/balanco_V1_0400/p_menor_005")
mo_peso, loc_mo_peso = mo_e8("selecao_v1_0400/peso_c1_400_no_P1")
mo_registrar("MO_SELECAO_V1", "Apendice C (multi-outcome)",
             f"com salto de {decimal_br(mo_vg['tau'][0], 3)} [{decimal_br(mo_vg['ic95_inf'][0], 3)}; "
             f"{decimal_br(mo_vg['ic95_sup'][0], 3)}], e, entre os municípios com vaga do ciclo 1 nesse corte, a razão "
             f"de densidades é de {decimal_br(mo_dens, 2)} e {inteiro(mo_bal_r)} de {inteiro(mo_bal_n)} covariáveis "
             f"diferem a 5\\%",
             [(c.upper(), decimal_br(b, 3), b, MO_E8_RESUMO, l, "3 casas") for c, (b, l) in mo_vg.items()]
             + [("DENS", decimal_br(mo_dens, 2), mo_dens, MO_E8_RESUMO, loc_mo_dens, "2 casas"),
                ("BAL_REJ", inteiro(mo_bal_r), mo_bal_r, MO_E8_RESUMO, loc_mo_bal_r, "inteiro"),
                ("BAL_N", inteiro(mo_bal_n), mo_bal_n, MO_E8_RESUMO, loc_mo_bal_n, "inteiro")])
mo_registrar("MO_SELECAO_PESO", "Apendice C (multi-outcome)",
             f"seu peso no índice P1 empilhado é de {pontos(mo_peso)}\\%",
             [("PESO", pontos(mo_peso), mo_peso, MO_E8_RESUMO, loc_mo_peso, "proporcao x100, 1 casa")])

# E7: estudo de evento, nivel pre-existente, generalistas e V1.
mo_seq = {c: mo_e8(f"e7/f31_U_0300/maior_sequencia_p_menor_005/{c}")
          for c in ("n_meses", "inicio", "fim", "janela", "tau_min", "tau_max")}
mo_primeiro_pos, _ = mo_e8("e7/f31_U_0300/primeiro_mes_pos")
mo_depois, loc_mo_depois = mo_e8("e7/f31_U_0300/meses_pos_depois_da_sequencia")
mo_depois_sig, _ = mo_e8("e7/f31_U_0300/meses_pos_depois_da_sequencia_p_menor_005")
mo_antes, loc_mo_antes = mo_e8("e7/f31_U_0300/meses_antes_da_referencia")
mo_antes_sig, _ = mo_e8("e7/f31_U_0300/meses_antes_da_referencia_p_menor_005")
mo_exigir(mo_seq["janela"][0] == ["pos"] and mo_seq["inicio"][0] == mo_primeiro_pos,
          "a sequencia de meses com p < 0,05 deixou de comecar no primeiro mes do pos")
mo_exigir(int(mo_depois_sig) == 0 and int(mo_antes_sig) == 0, "ha meses com p < 0,05 fora da sequencia")
mo_registrar("MO_E7_SEQUENCIA", "Apendice C (multi-outcome)",
             f"No corte de {decimal_br(rdd_c1, 3)}, há {inteiro(mo_seq['n_meses'][0])} meses consecutivos com $p$ abaixo "
             f"de 5\\%, de {mo_mes(mo_seq['inicio'][0])} a {mo_mes(mo_seq['fim'][0])}, com saltos de "
             f"{decimal_br(mo_seq['tau_min'][0], 3)} a {decimal_br(mo_seq['tau_max'][0], 3)} vínculo por 10 mil "
             f"habitantes, e nenhum nos {inteiro(mo_depois)} meses seguintes; antes da referência, nenhum dos "
             f"{inteiro(mo_antes)} meses tem $p$ abaixo de 5\\%",
             [("N", inteiro(mo_seq["n_meses"][0]), mo_seq["n_meses"][0], MO_E8_RESUMO, mo_seq["n_meses"][1], "inteiro"),
              ("INICIO", mo_mes(mo_seq["inicio"][0]), mo_seq["inicio"][0], MO_E8_RESUMO, mo_seq["inicio"][1], "mes por extenso"),
              ("FIM", mo_mes(mo_seq["fim"][0]), mo_seq["fim"][0], MO_E8_RESUMO, mo_seq["fim"][1], "mes por extenso"),
              ("TAU_MIN", decimal_br(mo_seq["tau_min"][0], 3), mo_seq["tau_min"][0], MO_E8_RESUMO, mo_seq["tau_min"][1], "3 casas"),
              ("TAU_MAX", decimal_br(mo_seq["tau_max"][0], 3), mo_seq["tau_max"][0], MO_E8_RESUMO, mo_seq["tau_max"][1], "3 casas"),
              ("DEPOIS", inteiro(mo_depois), mo_depois, MO_E8_RESUMO, loc_mo_depois, "inteiro"),
              ("ANTES", inteiro(mo_antes), mo_antes, MO_E8_RESUMO, loc_mo_antes, "inteiro")])
mo_registrar("MO_E7_REFERENCIA", "Apendice C (multi-outcome)", f"relativo a {mo_mes(mo_ref)}",
             [("REF", mo_mes(mo_ref), mo_ref, MO_E7_RESUMO, loc_mo_ref, "competencia por extenso")])
mo_med = {c: mo_e8(f"e7/f31_U_0300/{c}") for c in ("media_tau_pre_extra", "media_tau_pre", "media_tau_pos")}
mo_exigir(mo_med["media_tau_pre"][0] < min(mo_med["media_tau_pre_extra"][0], mo_med["media_tau_pos"][0]),
          "a referencia deixou de estar num vale entre o pre extra e o pos")
mo_registrar("MO_E7_VALE", "Apendice C (multi-outcome)", f"a referência de {mo_mes(mo_ref)} está num vale",
             [("REF", mo_mes(mo_ref), mo_ref, MO_E7_RESUMO, loc_mo_ref, "competencia por extenso")])
mo_pe_txt = f"de {mo_mes(mo_pre_extra[0])} a {mo_mes(mo_pre_extra[-1])}"
mo_item_pe = [("PRE_EXTRA_INI", mo_mes(mo_pre_extra[0]), mo_pre_extra[0], MO_E7_RESUMO, f"{loc_mo_pre_extra}/0",
               "competencia por extenso"),
              ("PRE_EXTRA_FIM", mo_mes(mo_pre_extra[-1]), mo_pre_extra[-1], MO_E7_RESUMO, f"{loc_mo_pre_extra}/-1",
               "competencia por extenso")]
mo_registrar("MO_E7_MEDIAS", "Apendice C (multi-outcome)",
             f"o salto médio do estudo de evento é de {decimal_br(mo_med['media_tau_pre_extra'][0], 3)} {mo_pe_txt} e "
             f"de {decimal_br(mo_med['media_tau_pos'][0], 3)} no pós",
             [("PRE_EXTRA", decimal_br(mo_med["media_tau_pre_extra"][0], 3), mo_med["media_tau_pre_extra"][0],
               MO_E8_RESUMO, mo_med["media_tau_pre_extra"][1], "3 casas"),
              ("POS", decimal_br(mo_med["media_tau_pos"][0], 3), mo_med["media_tau_pos"][0], MO_E8_RESUMO,
               mo_med["media_tau_pos"][1], "3 casas")] + mo_item_pe)
mo_dird = {c: mo_e8(f"e7/f31_U_0300/dird_principal/{c}") for c in ("tau", "ic95_inf", "ic95_sup", "p_valor")}
mo_registrar("MO_E7_DIRD_0300", "Apendice C (multi-outcome)",
             f"a DiRD principal nesse corte é de {decimal_br(mo_dird['tau'][0], 3)} [{decimal_br(mo_dird['ic95_inf'][0], 3)}; "
             f"{decimal_br(mo_dird['ic95_sup'][0], 3)}], com $p$ de {decimal_br(mo_dird['p_valor'][0], 3)}",
             [(c.upper(), decimal_br(b, 3), b, MO_E8_RESUMO, l, "3 casas") for c, (b, l) in mo_dird.items()])
mo_exigir(bool(mo_e8("e7/f31_U_0300/descontinuidade_preexistente")[0]), "a descontinuidade pre-existente sumiu")
mo_niv = {j: {c: mo_e8(f"e7/f31_U_0300/{j}/{c}") for c in ("tau", "ic95_inf", "ic95_sup")}
          for j in ("nivel_pre_extra", "nivel_pre")}
mo_exigir(all(v["ic95_sup"][0] < 0 for v in mo_niv.values()), "o nivel pre deixou de ser menor do lado de cima")
mo_registrar("MO_E7_NIVEL", "Apendice C (multi-outcome)",
             f"com salto de {decimal_br(mo_niv['nivel_pre_extra']['tau'][0], 3)} "
             f"[{decimal_br(mo_niv['nivel_pre_extra']['ic95_inf'][0], 3)}; "
             f"{decimal_br(mo_niv['nivel_pre_extra']['ic95_sup'][0], 3)}] {mo_pe_txt} e de "
             f"{decimal_br(mo_niv['nivel_pre']['tau'][0], 3)} [{decimal_br(mo_niv['nivel_pre']['ic95_inf'][0], 3)}; "
             f"{decimal_br(mo_niv['nivel_pre']['ic95_sup'][0], 3)}] no pré principal",
             [(f"{j.upper()}_{c.upper()}", decimal_br(b, 3), b, MO_E8_RESUMO, l, "3 casas")
              for j, v in mo_niv.items() for c, (b, l) in v.items()] + mo_item_pe)
mo_gen_n, loc_mo_gen_n = mo_e8("e7/generalistas_U_0400/pre_extra_meses")
mo_gen_s, loc_mo_gen_s = mo_e8("e7/generalistas_U_0400/pre_extra_p_menor_005")
mo_exigir(int(mo_gen_s) > 0, "o placebo de generalistas deixou de se deslocar antes do pre principal")
mo_registrar("MO_E7_GENERALISTAS", "Apendice C (multi-outcome)",
             f"o placebo de generalistas já tem $p$ abaixo de 5\\% em {inteiro(mo_gen_s)} dos {inteiro(mo_gen_n)} meses "
             f"{mo_pe_txt}",
             [("SIG", inteiro(mo_gen_s), mo_gen_s, MO_E8_RESUMO, loc_mo_gen_s, "inteiro"),
              ("N", inteiro(mo_gen_n), mo_gen_n, MO_E8_RESUMO, loc_mo_gen_n, "inteiro")] + mo_item_pe)
mo_exigir(int(mo_e8("e7/f31_U_0400_pos_p_menor_005")[0]) == 0, "ha mes do pos com p < 0,05 no corte de 0,400")
registrar("MO_E7_0400_POS", "Apendice C (multi-outcome)", "meses do pos com p<0,05 em 0,400 (F3.1, U)", "nenhum",
          MO_E8_RESUMO, "campo e7/f31_U_0400_pos_p_menor_005", 0, "guarda: zero",
          "nesse corte, nenhum mês do pós tem $p$ abaixo de 5\\% nas ocupações-alvo")
mo_v1 = {c: mo_e8(f"e7/v1_0300/{c}") for c in ("meses_pre_extra_e_entre", "meses_pre_extra_e_entre_p_menor_005",
                                               "meses_pre_extra_e_entre_tau_positivo")}
mo_exigir(len({int(v[0]) for v in mo_v1.values()}) == 1, "nem todos os meses de V1 em 0,300 tem p < 0,05 e salto positivo")
mo_registrar("MO_E7_V1", "Apendice C (multi-outcome)",
             f"todos os {inteiro(mo_v1['meses_pre_extra_e_entre'][0])} meses anteriores ao pré principal têm salto "
             f"positivo com $p$ abaixo de 5\\%",
             [("N", inteiro(mo_v1["meses_pre_extra_e_entre"][0]), mo_v1["meses_pre_extra_e_entre"][0], MO_E8_RESUMO,
               mo_v1["meses_pre_extra_e_entre"][1], "inteiro")])

# E9: escolha da 1a opcao (secundario e exploratorio), reconferido contra o E9.
mo_e9 = {c: {k: mo_e8(f"e9/principal/{c}/{k}") for k in ("rc_5mil", "rc_5mil_ic95/0", "rc_5mil_ic95/1", "p", "ic_exclui_zero")}
         for c in ("1", "2", "3", "empilhado")}
for c, v in mo_e9.items():
    origem = csv_valor(MO_E9_EFM, {"ciclo": c, "modelo": "logit_condicional_1a_opcao", "conjunto": "principal",
                                   "especificacao": "spline_linear__bolsa_linear", "termo": "bolsa_mil",
                                   "quantidade": "razao_chances_por_5mil"}, "estimativa")[0]
    mo_exigir(abs(float(origem) - float(v["rc_5mil"][0])) < 1e-9, f"razao de chances do ciclo {c} difere do E9")
mo_exigir(mo_e9["2"]["ic_exclui_zero"][0] and mo_e9["empilhado"]["ic_exclui_zero"][0]
          and not mo_e9["1"]["ic_exclui_zero"][0] and not mo_e9["3"]["ic_exclui_zero"][0],
          "o padrao de significancia do E9 por ciclo mudou")


def mo_rc(ciclo: str) -> str:
    v = mo_e9[ciclo]
    return (f"{decimal_br(v['rc_5mil'][0], 2)} [{decimal_br(v['rc_5mil_ic95/0'][0], 2)}; "
            f"{decimal_br(v['rc_5mil_ic95/1'][0], 2)}]")


def mo_itens_rc(ciclo: str) -> list[tuple[str, str, Any, str, str, str]]:
    return [(f"C{ciclo.upper()}_{k.replace('/', '_').upper()}", decimal_br(b, 2), b, MO_E8_RESUMO, l, "2 casas")
            for k, (b, l) in mo_e9[ciclo].items() if k.startswith("rc_5mil")]


c2r = {k: mo_e8(f"e9/ciclo2/{k}") for k in ("p_score_rademacher", "p_score_webb", "placebo/n_placebos",
                                             "placebo/n_abs_t_placebo_ge_real", "placebo/p_posto", "spline_cubico/p")}
emr = {k: mo_e8(f"e9/empilhado/{k}") for k in ("cluster_curso/p_score_rademacher", "cluster_curso/p_score_webb",
                                                "placebo/n_placebos", "placebo/n_abs_t_placebo_ge_real",
                                                "placebo/p_posto", "spline_cubico/p", "ciclos_1_e_3/p", "cochran_Q/p")}
mo_exigir(bool(mo_e8("e9/ciclo2/robusto_inferencia_poucos_clusters")[0]) and bool(mo_e8("e9/ciclo2/nenhum_placebo_supera")[0])
          and bool(mo_e8("e9/ciclo2/ic_cubico_contem_zero")[0]), "a robustez do ciclo 2 mudou")
mo_exigir(bool(mo_e8("e9/empilhado/fragil")[0]) and bool(mo_e8("e9/empilhado/heterogeneidade_rejeitada")[0]),
          "o empilhado do E9 deixou de ser fragil")
mo_exigir(int(c2r["placebo/n_placebos"][0]) == int(emr["placebo/n_placebos"][0]), "numero de placebos difere")
mo_item_salto = ("SALTO_BRL", mil_reais(rdd_salto), rdd_salto, RDD_E3_ESTIM, "coluna salto_anunciado_brl, todas as linhas",
                 "reais em mil")
mo_registrar("MO_E9_C2", "Apendice C (multi-outcome)",
             f"com razão de chances de {mo_rc('2')} por {mil_reais(rdd_salto)} a mais", mo_itens_rc("2") + [mo_item_salto])
mo_registrar("MO_E9_PLACEBOS", "Apendice C (multi-outcome)",
             f"aos {inteiro(c2r['placebo/n_placebos'][0])} cortes placebo, nenhum dos quais tem estatística $t$ maior ou "
             f"igual à real, mas o intervalo inclui o zero com um \\emph{{spline}} cúbico",
             [("N", inteiro(c2r["placebo/n_placebos"][0]), c2r["placebo/n_placebos"][0], MO_E8_RESUMO,
               c2r["placebo/n_placebos"][1], "inteiro")])
mo_registrar("MO_E9_C1_C3", "Apendice C (multi-outcome)",
             f"Nos ciclos 1 e 3, as razões são de {mo_rc('1')} e {mo_rc('3')}", mo_itens_rc("1") + mo_itens_rc("3"))
mo_registrar("MO_E9_EMPILHADO", "Apendice C (multi-outcome)",
             f"O empilhado, de {mo_rc('empilhado')}, é frágil: sem o ciclo 2, o $p$ é de "
             f"{decimal_br(emr['ciclos_1_e_3/p'][0], 3)}; a homogeneidade entre ciclos é rejeitada, com $p$ de "
             f"{decimal_br(emr['cochran_Q/p'][0], 3)}; contra os placebos, o $p$ por posto é de "
             f"{decimal_br(emr['placebo/p_posto'][0], 3)}; e, com \\emph{{spline}} cúbico, é de "
             f"{decimal_br(emr['spline_cubico/p'][0], 3)}",
             mo_itens_rc("empilhado")
             + [(k.replace("/", "_").upper(), decimal_br(b, 3), b, MO_E8_RESUMO, l, "3 casas")
                for k, (b, l) in emr.items() if k in ("ciclos_1_e_3/p", "cochran_Q/p", "placebo/p_posto", "spline_cubico/p")])

# Tabela C3: E9, ciclo 2 contra empilhado.
mo_p_c2, loc_mo_p_c2 = mo_e9["2"]["p"]
mo_p_em, loc_mo_p_em = mo_e9["empilhado"]["p"]
mo_tab_e9 = [
    ("RC", f"Razão de chances por {mil_reais(rdd_salto)} a mais [IC95\\%] & {mo_rc('2')} & {mo_rc('empilhado')} \\\\",
     mo_itens_rc("2") + mo_itens_rc("empilhado") + [mo_item_salto]),
    ("P", f"$p$, \\emph{{cluster}} por conjunto de escolha & {mo_p(mo_p_c2)} & {mo_p(mo_p_em)} \\\\",
     [("C2", mo_p(mo_p_c2), mo_p_c2, MO_E8_RESUMO, loc_mo_p_c2, "3 casas; < 0,001"),
      ("EMP", mo_p(mo_p_em), mo_p_em, MO_E8_RESUMO, loc_mo_p_em, "3 casas")]),
    ("SCORE", f"$p$ do \\emph{{score bootstrap}}, Rademacher / Webb & {mo_p(c2r['p_score_rademacher'][0])} / "
              f"{mo_p(c2r['p_score_webb'][0])} & --- \\\\",
     [(k.upper(), mo_p(c2r[k][0]), c2r[k][0], MO_E8_RESUMO, c2r[k][1], "3 casas; < 0,001")
      for k in ("p_score_rademacher", "p_score_webb")]),
    ("SCORE_CURSO", f"$p$ do \\emph{{score bootstrap}} por curso, Rademacher / Webb & --- & "
                    f"{mo_p(emr['cluster_curso/p_score_rademacher'][0])} / {mo_p(emr['cluster_curso/p_score_webb'][0])} \\\\",
     [(k.split("/")[1].upper(), mo_p(emr[k][0]), emr[k][0], MO_E8_RESUMO, emr[k][1], "3 casas")
      for k in ("cluster_curso/p_score_rademacher", "cluster_curso/p_score_webb")]),
    ("PLACEBO_N", f"Placebos com $|t|$ maior ou igual ao real, de {inteiro(c2r['placebo/n_placebos'][0])} & "
                  f"{inteiro(c2r['placebo/n_abs_t_placebo_ge_real'][0])} & "
                  f"{inteiro(emr['placebo/n_abs_t_placebo_ge_real'][0])} \\\\",
     [("N", inteiro(c2r["placebo/n_placebos"][0]), c2r["placebo/n_placebos"][0], MO_E8_RESUMO,
       c2r["placebo/n_placebos"][1], "inteiro"),
      ("C2", inteiro(c2r["placebo/n_abs_t_placebo_ge_real"][0]), c2r["placebo/n_abs_t_placebo_ge_real"][0],
       MO_E8_RESUMO, c2r["placebo/n_abs_t_placebo_ge_real"][1], "inteiro"),
      ("EMP", inteiro(emr["placebo/n_abs_t_placebo_ge_real"][0]), emr["placebo/n_abs_t_placebo_ge_real"][0],
       MO_E8_RESUMO, emr["placebo/n_abs_t_placebo_ge_real"][1], "inteiro")]),
    ("POSTO", f"$p$ por posto contra os placebos & {decimal_br(c2r['placebo/p_posto'][0], 3)} & "
              f"{decimal_br(emr['placebo/p_posto'][0], 3)} \\\\",
     [("C2", decimal_br(c2r["placebo/p_posto"][0], 3), c2r["placebo/p_posto"][0], MO_E8_RESUMO,
       c2r["placebo/p_posto"][1], "3 casas"),
      ("EMP", decimal_br(emr["placebo/p_posto"][0], 3), emr["placebo/p_posto"][0], MO_E8_RESUMO,
       emr["placebo/p_posto"][1], "3 casas")]),
    ("CUBICO", f"\\emph{{Spline}} cúbico do IVS: $p$ & {decimal_br(c2r['spline_cubico/p'][0], 3)} & "
               f"{decimal_br(emr['spline_cubico/p'][0], 3)} \\\\",
     [("C2", decimal_br(c2r["spline_cubico/p"][0], 3), c2r["spline_cubico/p"][0], MO_E8_RESUMO,
       c2r["spline_cubico/p"][1], "3 casas"),
      ("EMP", decimal_br(emr["spline_cubico/p"][0], 3), emr["spline_cubico/p"][0], MO_E8_RESUMO,
       emr["spline_cubico/p"][1], "3 casas")]),
    ("SEM_C2", f"Sem o ciclo 2 (ciclos 1 e 3): $p$ & --- & {decimal_br(emr['ciclos_1_e_3/p'][0], 3)} \\\\",
     [("EMP", decimal_br(emr["ciclos_1_e_3/p"][0], 3), emr["ciclos_1_e_3/p"][0], MO_E8_RESUMO,
       emr["ciclos_1_e_3/p"][1], "3 casas")]),
    ("COCHRAN", f"Homogeneidade entre os ciclos (Cochran): $p$ & --- & {decimal_br(emr['cochran_Q/p'][0], 3)} \\\\",
     [("EMP", decimal_br(emr["cochran_Q/p"][0], 3), emr["cochran_Q/p"][0], MO_E8_RESUMO, emr["cochran_Q/p"][1],
       "3 casas")]),
]
for chave, trecho, itens in mo_tab_e9:
    mo_registrar(f"MO_TAB_E9_{chave}", "Tabela C3 (E9)", trecho, itens)


# --------------------------------------- Apendice D: rotas avaliadas e descartadas

ddd_cel, loc_dc = json_valor(DDD_PORTAO, "amostra_ddd_municipio_curso/n_celulas")
ddd_mun, loc_dm = json_valor(DDD_PORTAO, "amostra_ddd_municipio_curso/n_municipios")
ddd_beta, loc_db = json_valor(DDD_PORTAO, "resultados_ajustados/tem_alocado_muni_ddd/beta")
ddd_se, loc_ds = json_valor(DDD_PORTAO, "resultados_ajustados/tem_alocado_muni_ddd/se")
ddd_p, loc_dp = json_valor(DDD_PORTAO, "resultados_ajustados/tem_alocado_muni_ddd/p_valor")
trecho_ddd = (
    f"com {inteiro(ddd_cel)} células em {inteiro(ddd_mun)} municípios, a modalidade "
    f"imediata não prediz a alocação confirmada: a diferença ajustada é de "
    f"{pontos(ddd_beta, 2)} pontos percentuais, com erro-padrão de {pontos(ddd_se, 2)} "
    f"pontos percentuais e $p$ de {decimal_br(ddd_p, 4)}"
)
for chave, bruto, local, formatado, transformacao, descricao in [
    ("CELULAS", ddd_cel, loc_dc, inteiro(ddd_cel), "inteiro", "Celulas da amostra DDD"),
    ("MUNICIPIOS", ddd_mun, loc_dm, inteiro(ddd_mun), "inteiro", "Municipios da amostra DDD"),
    ("BETA", ddd_beta, loc_db, pontos(ddd_beta, 2), "proporcao x100, 2 casas",
     "Diferenca ajustada do portao de relevancia"),
    ("SE", ddd_se, loc_ds, pontos(ddd_se, 2), "proporcao x100, 2 casas",
     "Erro-padrao do portao de relevancia"),
    ("P", ddd_p, loc_dp, decimal_br(ddd_p, 4), "4 casas", "p-valor do portao de relevancia"),
]:
    registrar(f"DDD_TXT_{chave}", "Apendice D", descricao, formatado, DDD_PORTAO, local,
              bruto, transformacao, trecho_ddd)


# ------------------------------------------------------ conferencia estrutural


def conferir_estrutura(tex: str) -> list[str]:
    problemas: list[str] = []

    pilha: list[tuple[str, int]] = []
    for achado in re.finditer(r"\\(begin|end)\{([^}]+)\}", tex):
        tipo, ambiente = achado.group(1), achado.group(2)
        linha = tex[: achado.start()].count("\n") + 1
        if tipo == "begin":
            pilha.append((ambiente, linha))
        elif not pilha:
            problemas.append(f"\\end{{{ambiente}}} sem \\begin na linha {linha}")
        else:
            aberto, linha_aberta = pilha.pop()
            if aberto != ambiente:
                problemas.append(
                    f"ambiente desbalanceado: \\begin{{{aberto}}} linha {linha_aberta} "
                    f"fechado por \\end{{{ambiente}}} linha {linha}"
                )
    if pilha:
        problemas.append(f"ambientes sem \\end: {pilha}")

    limpo = re.sub(r"\\[{}%&_$#]", "", tex)
    if limpo.count("{") != limpo.count("}"):
        problemas.append("chaves desbalanceadas no arquivo")

    if len(re.findall(r"(?<!\\)\$", tex)) % 2:
        problemas.append("numero impar de delimitadores de modo matematico")

    for numero_linha, linha in enumerate(tex.split("\n"), 1):
        if re.search(r"(?<!\\)%", linha):
            problemas.append(f"caractere % nao escapado na linha {numero_linha}")

    for achado in re.finditer(
        r"\\begin\{tabular\}\{([^}]*)\}(.*?)\\end\{tabular\}", tex, re.S
    ):
        especificacao, corpo = achado.group(1), achado.group(2)
        colunas = len(re.findall(r"[lcr]|p\{[^}]*\}", especificacao))
        linha_inicial = tex[: achado.start()].count("\n") + 1
        for bruta in corpo.split("\\\\"):
            conteudo = re.sub(r"\\(top|mid|bottom)rule", "", bruta).strip()
            if not conteudo:
                continue
            achadas = len(re.findall(r"(?<!\\)&", conteudo)) + 1
            if achadas != colunas:
                problemas.append(
                    f"tabular iniciado na linha {linha_inicial}: {achadas} colunas "
                    f"em vez de {colunas} na linha '{conteudo[:60]}'"
                )

    rotulos = set(re.findall(r"\\label\{([^}]+)\}", tex))
    referencias = set(re.findall(r"\\ref\{([^}]+)\}", tex))
    if referencias - rotulos:
        problemas.append(f"\\ref sem \\label: {sorted(referencias - rotulos)}")

    chaves = set(re.findall(r"\\bibitem\[[^\]]*\]\{([^}]+)\}", tex))
    citadas: set[str] = set()
    for achado in re.finditer(r"\\cite[tp]?\{([^}]+)\}", tex):
        citadas |= {chave.strip() for chave in achado.group(1).split(",")}
    if citadas - chaves:
        problemas.append(f"citacao sem \\bibitem: {sorted(citadas - chaves)}")
    if chaves - citadas:
        problemas.append(f"\\bibitem nao citado: {sorted(chaves - citadas)}")

    for achado in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex):
        if not (ROOT / achado.group(1)).exists():
            problemas.append(f"figura ausente no disco: {achado.group(1)}")

    return problemas


# ------------------------------------------------- A5: multiplicidade e C-7

A5_C7 = "output/tema_trabalho/A5_ameacas_c7.json"

q_prop, loc_qp = json_valor(A5_JSON, "multiplicidade/mar2026_q_fdr_bh_gl_fe_proporcional_confirmatoria")
q_nivel, loc_qn = json_valor(A5_JSON, "multiplicidade/mar2026_q_fdr_bh_gl_fe_nivel_confirmatoria")
trecho_q = (f"o valor $q$ de Benjamini--Hochberg do coeficiente de março de 2026 é {decimal_br(q_prop, 4)} na "
            f"escala proporcional e {decimal_br(q_nivel, 3)} em nível")
registrar("A5_TXT_Q_PROP", "Apendice B", "q FDR proporcional (B-5)", decimal_br(q_prop, 4), A5_JSON, loc_qp, q_prop, "4 casas", trecho_q)
registrar("A5_TXT_Q_NIVEL", "Apendice B", "q FDR nivel (B-5)", decimal_br(q_nivel, 3), A5_JSON, loc_qn, q_nivel, "3 casas", trecho_q)

c7_pl_n_b, loc_c1 = json_valor(A5_C7, "placebo/resultado/nivel/mar2026_beta")
c7_pl_p_b, loc_c2 = json_valor(A5_C7, "placebo/resultado/proporcional/mar2026_beta")
c7_pl_n_p, loc_c3 = json_valor(A5_C7, "placebo/resultado/nivel/mar2026_p_gl_fe")
c7_pl_p_p, loc_c4 = json_valor(A5_C7, "placebo/resultado/proporcional/mar2026_p_gl_fe")
c7_n_trat, loc_c5 = json_valor(A5_C7, "placebo/resultado/nivel/n_tratadas")
c7_n_ctrl, loc_c6 = json_valor(A5_C7, "placebo/resultado/nivel/n_controle")
trecho_c7_pl = (f"Entre as {inteiro(c7_n_trat + c7_n_ctrl)} células sem atração, estar em um município que atraiu em alguma outra "
                f"célula não muda o estoque: {decimal_br(c7_pl_n_b, 3)} em nível e {decimal_br(c7_pl_p_b, 4)} na escala proporcional, "
                f"com $p$ de {decimal_br(c7_pl_n_p, 3)} e {decimal_br(c7_pl_p_p, 3)}")
for chave, bruto, loc, fmt, tr in [("N", c7_n_trat + c7_n_ctrl, f"soma: {loc_c5} + {loc_c6}", inteiro(c7_n_trat + c7_n_ctrl), "inteiro"),
                                   ("NIVEL", c7_pl_n_b, loc_c1, decimal_br(c7_pl_n_b, 3), "3 casas"),
                                   ("PROP", c7_pl_p_b, loc_c2, decimal_br(c7_pl_p_b, 4), "4 casas"),
                                   ("NIVEL_P", c7_pl_n_p, loc_c3, decimal_br(c7_pl_n_p, 3), "3 casas"),
                                   ("PROP_P", c7_pl_p_p, loc_c4, decimal_br(c7_pl_p_p, 3), "3 casas")]:
    registrar(f"A5_TXT_C7_PLACEBO_{chave}", "Apendice B", f"placebo C-7: {chave}", fmt, A5_C7, loc, bruto, tr, trecho_c7_pl)

c7_tb_b, loc_c7 = json_valor(A5_C7, "deslocamento/transbordo/proporcional/mar2026_beta")
c7_tb_p, loc_c8 = json_valor(A5_C7, "deslocamento/transbordo/proporcional/mar2026_p_gl_fe")
c7_rg_b, loc_c9 = json_valor(A5_C7, "deslocamento/oferta_liquida_regional/proporcional/mar2026_beta")
c7_rg_p, loc_c10 = json_valor(A5_C7, "deslocamento/oferta_liquida_regional/proporcional/mar2026_p_gl_fe")
c7_n_reg, loc_c11 = json_valor(A5_C7, "deslocamento/n_regioes")
trecho_c7_ds = (f"não perdem estoque, com {decimal_br(c7_tb_b, 3)} log-ponto e $p$ de {decimal_br(c7_tb_p, 3)}. A soma do estoque por "
                f"região--curso sobe {decimal_br(c7_rg_b, 3)} log-ponto, com $p$ de {decimal_br(c7_rg_p, 3)}, em {inteiro(c7_n_reg)} regiões")
for chave, bruto, loc, fmt, tr in [("TRANSBORDO", c7_tb_b, loc_c7, decimal_br(c7_tb_b, 3), "3 casas"),
                                   ("TRANSBORDO_P", c7_tb_p, loc_c8, decimal_br(c7_tb_p, 3), "3 casas"),
                                   ("REGIONAL", c7_rg_b, loc_c9, decimal_br(c7_rg_b, 3), "3 casas"),
                                   ("REGIONAL_P", c7_rg_p, loc_c10, decimal_br(c7_rg_p, 3), "3 casas"),
                                   ("N_REGIOES", c7_n_reg, loc_c11, inteiro(c7_n_reg), "inteiro")]:
    registrar(f"A5_TXT_C7_DESLOC_{chave}", "Apendice B", f"deslocamento C-7: {chave}", fmt, A5_C7, loc, bruto, tr, trecho_c7_ds)
# C-7c: a decomposicao que diz o que o agregado regional consegue e nao consegue medir.
c7_rgm_b, loc_c12 = json_valor(A5_C7, "deslocamento/decomposicao_oferta_liquida/multi_municipio/proporcional/mar2026_beta")
c7_rgm_p, loc_c13 = json_valor(A5_C7, "deslocamento/decomposicao_oferta_liquida/multi_municipio/proporcional/mar2026_p_gl_fe")
c7_n_multi, loc_c14 = json_valor(A5_C7, "deslocamento/decomposicao_oferta_liquida/n_regiao_curso_multi_municipio")
c7_n_uni, loc_c15 = json_valor(A5_C7, "deslocamento/decomposicao_oferta_liquida/n_regiao_curso_um_municipio")
c7_n_rc, loc_c16 = json_valor(A5_C7, "deslocamento/n_regiao_curso")
if int(c7_n_multi) + int(c7_n_uni) != int(c7_n_rc):
    raise SystemExit("C-7c: as duas subamostras deveriam somar o total de regiao-curso")
trecho_c7_dec = (f"das {inteiro(c7_n_rc)} região--curso, {inteiro(c7_n_uni)} contêm um único município do quadro e nelas o agregado é a "
                 f"própria célula, e restrito às {inteiro(c7_n_multi)} que de fato agregam mais de um município o coeficiente é "
                 f"{decimal_br(c7_rgm_b, 3)}, com $p$ de {decimal_br(c7_rgm_p, 3)}")
for chave, bruto, loc, fmt, tr in [("MULTI_BETA", c7_rgm_b, loc_c12, decimal_br(c7_rgm_b, 3), "3 casas"),
                                   ("MULTI_P", c7_rgm_p, loc_c13, decimal_br(c7_rgm_p, 3), "3 casas"),
                                   ("N_MULTI", c7_n_multi, loc_c14, inteiro(c7_n_multi), "inteiro"),
                                   ("N_UNI", c7_n_uni, loc_c15, inteiro(c7_n_uni), "inteiro"),
                                   ("N_RC", c7_n_rc, loc_c16, inteiro(c7_n_rc), "inteiro")]:
    registrar(f"A5_TXT_C7_DECOMP_{chave}", "Apendice B", f"decomposicao C-7c: {chave}", fmt, A5_C7, loc, bruto, tr, trecho_c7_dec)
# C-7b: multiplicidade na triagem de pre-tendencia por curso.
c7_q16, loc_c17 = json_valor(A5_C7, "pretendencia_por_curso/multiplicidade/q_por_curso/proporcional/16")
c7_q2, loc_c18 = json_valor(A5_C7, "pretendencia_por_curso/multiplicidade/q_por_curso/proporcional/2")
c7_alpha, loc_c19 = json_valor(A5_C7, "pretendencia_por_curso/multiplicidade/alpha")
c7_cursos_q, loc_c20 = json_valor(A5_C7, "pretendencia_por_curso/multiplicidade/cursos_q_lt_0_05_proporcional")
if c7_cursos_q != [16]:
    raise SystemExit(f"C-7b: o apendice B cita so o curso 16 sobrevivendo ao q; o artefato traz {c7_cursos_q}")
trecho_c7_q = (f"deixa apenas o curso {c7_cursos_q[0]} com $q$ abaixo de {decimal_br(c7_alpha, 2)} na escala "
               f"proporcional, com {decimal_br(c7_q16, 4)}, contra {decimal_br(c7_q2, 3)} do curso 2")
for chave, bruto, loc, fmt, tr in [("Q16", c7_q16, loc_c17, decimal_br(c7_q16, 4), "4 casas"),
                                   ("Q2", c7_q2, loc_c18, decimal_br(c7_q2, 3), "3 casas"),
                                   ("ALPHA", c7_alpha, loc_c19, decimal_br(c7_alpha, 2), "2 casas"),
                                   ("CURSOS", c7_cursos_q, loc_c20, str(c7_cursos_q[0]), "lista")]:
    registrar(f"A5_TXT_C7_MULT_{chave}", "Apendice B", f"multiplicidade C-7b: {chave}", fmt, A5_C7, loc, bruto, tr, trecho_c7_q)


# ------------------------------------------------------------------ execucao


def corpo_sem_bibliografia(tex: str) -> str:
    """Corpo do documento sem o ambiente thebibliography.

    No artigo principal os apêndices vêm depois da bibliografia; cortar o texto
    em `\\begin{thebibliography}` deixava os apêndices fora da varredura de
    órfãos. Aqui só o bloco da bibliografia sai."""
    corpo = tex.split("\\begin{document}", 1)[1].split("\\end{document}", 1)[0]
    return re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}", " ", corpo, flags=re.S)


def decimais_sem_origem(tex: str, registros: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    """Cobertura (como no conferidor do artigo curto): todo decimal com vírgula no corpo
    do artigo, apêndices incluídos, tem de estar contido em algum trecho conferido com
    status OK."""
    corpo = corpo_sem_bibliografia(tex)
    corpo = re.sub(r"\\(label|ref|includegraphics|cite[tp]?)\{[^}]*\}", " ", corpo)
    corpo_norm = re.sub(r"\s+", " ", corpo)
    trechos_ok = " || ".join(r["trecho_esperado_no_tex"] for r in registros if r.get("status") == "OK")
    decimais = sorted(set(re.findall(r"(?<![\d,.])\d+,\d+(?![\d,])", corpo_norm)))
    sem_origem = [d for d in decimais
                  if not re.search(r"(?<![\d,.])" + re.escape(d) + r"(?![\d,])", trechos_ok)]
    return decimais, sem_origem


def main() -> None:
    if not TEX.exists():
        raise SystemExit(f"Arquivo do artigo ausente: {TEX}")
    tex = TEX.read_text(encoding="utf-8")
    tex_normalizado = re.sub(r"\s+", " ", tex)

    for registro in REGISTROS:
        ocorrencias = tex_normalizado.count(registro["trecho_esperado_no_tex"])
        registro["ocorrencias_no_tex"] = ocorrencias
        registro["status"] = "OK" if ocorrencias >= 1 else "DIVERGENTE"

    identificadores = [registro["id"] for registro in REGISTROS]
    if len(identificadores) != len(set(identificadores)):
        repetidos = sorted({i for i in identificadores if identificadores.count(i) > 1})
        raise SystemExit(f"Identificadores repetidos na conferencia: {repetidos}")

    quadro = pd.DataFrame(REGISTROS)[CABECALHO].sort_values("id").reset_index(drop=True)
    temporario = CONFERENCIA_CSV.with_suffix(".csv.tmp")
    quadro.to_csv(temporario, index=False, encoding="utf-8")
    temporario.replace(CONFERENCIA_CSV)

    divergentes = quadro[quadro["status"].ne("OK")]
    problemas = conferir_estrutura(tex)
    decimais, sem_origem = decimais_sem_origem(tex, REGISTROS)

    print(f"Numeros conferidos: {len(quadro)}")
    print(f"Decimais distintos no corpo: {len(decimais)}; sem origem: {len(sem_origem)}")
    print(f"Mapeamento gravado em: {CONFERENCIA_CSV.relative_to(ROOT)}")
    print(f"Problemas estruturais: {len(problemas)}")
    for problema in problemas:
        print(f"  - {problema}")

    if len(divergentes):
        print("\nNumeros do artigo sem correspondencia na fonte:")
        for _, linha in divergentes.iterrows():
            print(f"  - {linha['id']}: esperava '{linha['trecho_esperado_no_tex']}'")

    if sem_origem:
        print("\nDecimais no corpo sem trecho conferido que os contenha:")
        for d in sem_origem:
            print(f"  - {d}")

    if len(divergentes) or problemas or sem_origem:
        raise SystemExit(1)

    print("\nCONFERENCIA APROVADA: toda cifra do artigo corresponde a um artefato.")


if __name__ == "__main__":
    main()
