"""Confere cada numero citado em paper_pmme_submission.tex contra os artefatos.

O script releia os artefatos versionados de A4, A5, A7, A8, do portao da regra
do IVS e do portao de relevancia, reformata cada valor no padrao usado no
artigo e exige que o trecho correspondente exista no arquivo LaTeX. Nenhuma
cifra do artigo pode existir sem uma origem rastreavel; qualquer divergencia
interrompe a execucao com codigo de saida diferente de zero.

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
A4_FULL = "output/tema_trabalho/A4_tabela_03b_ajuste_completo.csv"
A4_JSON = "output/tema_trabalho/A4_estimativas_atracao.json"
A5_JSON = "output/tema_trabalho/A5_estimativas_provimento.json"
A5_EVENTO = "output/tema_trabalho/A5_tabela_07_estudo_evento_atracao.csv"
RDD_PORTAO = "output/rdd_bolsa/portao_regra_ivs.json"
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
    ("FULL", A4_FULL, {"termo": "estrato_metropolitano"}, "Ajuste completo"),
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

a4_full_coef, loc_fc = csv_valor(A4_FULL, {"termo": "estrato_metropolitano"}, "coef")
a4_full_p, loc_fp = csv_valor(A4_FULL, {"termo": "estrato_metropolitano"}, "p_valor")
a4_full_q, loc_fq = csv_valor(A4_FULL, {"termo": "estrato_metropolitano"}, "q_fdr_estrato")
trecho_a4_full = (
    f"o contraste metropolitano permanece em {pontos(a4_full_coef)} pontos percentuais, "
    f"com $p$ de {decimal_br(a4_full_p, 3)} e valor $q$ de {decimal_br(a4_full_q, 3)} "
    f"após correção FDR entre estratos"
)
registrar("A4_TXT_FULL_COEF", "Apendice A", "Contraste metropolitano no ajuste completo",
          pontos(a4_full_coef), A4_FULL, loc_fc, a4_full_coef, "proporcao x100, 1 casa",
          trecho_a4_full)
registrar("A4_TXT_FULL_P", "Apendice A", "p-valor do contraste metropolitano ajustado",
          decimal_br(a4_full_p, 3), A4_FULL, loc_fp, a4_full_p, "3 casas", trecho_a4_full)
registrar("A4_TXT_FULL_Q", "Apendice A", "q FDR do contraste metropolitano ajustado",
          decimal_br(a4_full_q, 3), A4_FULL, loc_fq, a4_full_q, "3 casas", trecho_a4_full)

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


# --------------------------------------- Apendice C: rotas avaliadas e descartadas

rdd_n, loc_rdd_n = json_valor(RDD_PORTAO, "diagnostico_publico/n_municipios")
rdd_ok, loc_rdd_ok = json_valor(RDD_PORTAO, "diagnostico_publico/n_reproduzidos")
rdd_div, loc_rdd_div = json_valor(RDD_PORTAO, "diagnostico_publico/n_divergentes")
rdd_pct, loc_rdd_pct = json_valor(RDD_PORTAO, "diagnostico_publico/pct_divergentes")
trecho_rdd = (
    f"{inteiro(rdd_ok)} dos {inteiro(rdd_n)} municípios são reproduzidos e "
    f"{inteiro(rdd_div)} divergem, ou {decimal_br(rdd_pct, 1)}\\% do total"
)
for chave, bruto, local, formatado, transformacao, descricao in [
    ("REPRODUZIDOS", rdd_ok, loc_rdd_ok, inteiro(rdd_ok), "inteiro",
     "Municipios com faixa reproduzida"),
    ("TOTAL", rdd_n, loc_rdd_n, inteiro(rdd_n), "inteiro", "Municipios do quadro"),
    ("DIVERGENTES", rdd_div, loc_rdd_div, inteiro(rdd_div), "inteiro",
     "Municipios com faixa divergente"),
    ("PCT", rdd_pct, loc_rdd_pct, decimal_br(rdd_pct, 1), "1 casa",
     "Percentual de divergencia"),
]:
    registrar(f"RDD_TXT_{chave}", "Apendice C", descricao, formatado, RDD_PORTAO, local,
              bruto, transformacao, trecho_rdd)

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
    registrar(f"DDD_TXT_{chave}", "Apendice C", descricao, formatado, DDD_PORTAO, local,
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


# ------------------------------------------------------------------ execucao


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

    print(f"Numeros conferidos: {len(quadro)}")
    print(f"Mapeamento gravado em: {CONFERENCIA_CSV.relative_to(ROOT)}")
    print(f"Problemas estruturais: {len(problemas)}")
    for problema in problemas:
        print(f"  - {problema}")

    if len(divergentes):
        print("\nNumeros do artigo sem correspondencia na fonte:")
        for _, linha in divergentes.iterrows():
            print(f"  - {linha['id']}: esperava '{linha['trecho_esperado_no_tex']}'")

    if len(divergentes) or problemas:
        raise SystemExit(1)

    print("\nCONFERENCIA APROVADA: toda cifra do artigo corresponde a um artefato.")


if __name__ == "__main__":
    main()
