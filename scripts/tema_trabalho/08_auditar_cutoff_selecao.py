"""A7 — Audita o corte de seleção por vaga como candidato a desenho causal.

O módulo trabalha apenas com agregados. Nomes e CPFs são usados em memória para
ligação exata entre publicações, mas nunca são persistidos nos artefatos.

O resultado é deliberadamente classificado como descontinuidade preliminar,
não como efeito causal. O edital usa pertencimento à mesma UF e idade como
desempates, e esses campos não aparecem nas planilhas públicas.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "tema_trabalho"

CALL1_RESULT = ROOT / "data" / "raw" / "aquisicao" / "vagas" / "2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx"
CALL1_HOMOLOG = ROOT / "data" / "raw" / "pmm_e" / "2025_ciclo1_chamada1_homologados.xlsx"
CALL2_RESULT = ROOT / "data" / "raw" / "pmm_e" / "2025_ciclo1_chamada2_classificacao_final.xlsx"
CALL2_HOMOLOG = ROOT / "data" / "raw" / "pmm_e" / "2025_ciclo1_chamada2_homologados.xlsx"
CYCLE2_CALL2 = ROOT / "data" / "raw" / "pmm_e" / "2026_ciclo2_chamada2_resultado_final.xlsx"
CYCLE3_CALL1 = ROOT / "data" / "raw" / "pmm_e" / "2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx"
ACTIVE_SNAPSHOT = ROOT / "data" / "pmm_especialistas_nominal.csv"

SUPPORT_TABLE = OUT / "A7_tabela_01_suporte_cutoffs.csv"
RESULTS_TABLE = OUT / "A7_tabela_02_descontinuidades_preliminares.csv"
SUMMARY_JSON = OUT / "A7_cutoff_selecao_resumo.json"
REPORT_MD = OUT / "A7_relatorio_cutoff_selecao.md"

OFFICIAL_NOTICE = (
    "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/"
    "chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-"
    "mais-medicos-especialistas/edital-de-chamamento-publico-no-3-2025.pdf"
)


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode().upper().strip()
    return re.sub(r"\s+", " ", text)


def digits(value: Any) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\D", "", str(value))


def candidate_key(cpf: pd.Series, name: pd.Series) -> pd.Series:
    raw = cpf.fillna("").astype(str) + "|" + name.fillna("").astype(str)
    return raw.map(lambda value: hashlib.sha256(value.encode()).hexdigest())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_text(path: Path, value: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(value, encoding="utf-8")
    tmp.replace(path)


def atomic_csv(path: Path, frame: pd.DataFrame) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(tmp, index=False, encoding="utf-8")
    tmp.replace(path)


def read_names(path: Path, sheet_name: str | int, column: int, header: int = 0) -> set[str]:
    frame = pd.read_excel(path, sheet_name=sheet_name, header=header)
    names = frame.iloc[:, column].map(normalize_text)
    return set(names[names.ne("")])


def read_call1(homologated_names: set[str], active_names: set[str]) -> pd.DataFrame:
    raw = pd.read_excel(CALL1_RESULT, sheet_name=0)
    columns = list(raw.columns)
    if len(columns) < 16:
        raise AssertionError("Quadro da primeira chamada perdeu colunas esperadas")
    frame = pd.DataFrame(
        {
            "course": raw[columns[0]].map(normalize_text),
            "uf": raw[columns[1]].map(normalize_text),
            "cnes": raw[columns[4]].map(digits),
            "cpf": raw[columns[6]].map(digits),
            "name": raw[columns[7]].map(normalize_text),
            "registration_type": raw[columns[8]].map(normalize_text),
            "result": raw[columns[9]].map(normalize_text),
            "allocation": raw[columns[10]].map(normalize_text),
            "preference": raw[columns[11]].map(normalize_text),
            "score": pd.to_numeric(raw[columns[12]], errors="coerce"),
            "rank": pd.to_numeric(raw[columns[13]], errors="coerce"),
        }
    )
    frame["candidate"] = candidate_key(frame["cpf"], frame["name"])
    frame["first_choice"] = frame["preference"].str.match(r"^1(\D|$)")
    frame["row_selected"] = frame["result"].str.startswith("CLASSIFICACAO")
    frame["row_selected_ac"] = frame["result"].str.contains("AMPLA CONCORRENCIA")
    frame["row_confirmed"] = frame["allocation"].str.contains("CONFIRMADO")
    frame["homologated"] = frame["name"].isin(homologated_names)
    frame["active_snapshot"] = frame["name"].isin(active_names)
    return frame


def read_call2(homologated_names: set[str], active_names: set[str]) -> pd.DataFrame:
    raw = pd.read_excel(CALL2_RESULT, sheet_name="ALOCADOS", header=1)
    columns = list(raw.columns)
    if len(columns) < 15:
        raise AssertionError("Resultado da segunda chamada perdeu colunas esperadas")
    frame = pd.DataFrame(
        {
            "course": raw[columns[0]].map(normalize_text),
            "uf": raw[columns[1]].map(normalize_text),
            "cnes": raw[columns[3]].map(digits),
            "cpf": raw[columns[6]].map(digits),
            "name": raw[columns[7]].map(normalize_text),
            "registration_type": raw[columns[8]].map(normalize_text),
            "result": raw[columns[9]].map(normalize_text),
            "preference": raw[columns[10]].map(normalize_text),
            "score": pd.to_numeric(raw[columns[11]], errors="coerce"),
            "rank": pd.to_numeric(raw[columns[12]], errors="coerce"),
        }
    )
    frame = frame[frame["name"].ne("")].copy()
    frame["candidate"] = candidate_key(frame["cpf"], frame["name"])
    frame["first_choice"] = frame["preference"].str.match(r"^1(\D|$)")
    frame["row_selected"] = frame["result"].str.startswith("ALOCADO")
    frame["row_selected_ac"] = frame["result"].str.contains("EM AC")
    frame["row_confirmed"] = frame["row_selected"]
    frame["homologated"] = frame["name"].isin(homologated_names)
    frame["active_snapshot"] = frame["name"].isin(active_names)
    return frame


def read_support_2026(path: Path, label: str) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name="Classificados")
    raw.columns = [normalize_text(column) for column in raw.columns]
    if label == "2026_C2_CH2":
        score_column = "PONTUACAO FINAL"
    else:
        score_column = "PONTUACAO NO BAREMA (GERAL)"
    required = {
        "CURSO",
        "CNES",
        "NOME",
        "TIPO DE INSCRICAO",
        "SITUACAO",
        "ORDEM DE PRIORIDADE ESCOLHIDA",
        "CLASSIFICACAO",
        score_column,
    }
    if not required.issubset(raw.columns):
        raise AssertionError(f"{label}: esquema mudou: {sorted(required - set(raw.columns))}")
    frame = pd.DataFrame(
        {
            "course": raw["CURSO"].map(normalize_text),
            "cnes": raw["CNES"].map(digits),
            "name": raw["NOME"].map(normalize_text),
            "registration_type": raw["TIPO DE INSCRICAO"].map(normalize_text),
            "result": raw["SITUACAO"].map(normalize_text),
            "preference": raw["ORDEM DE PRIORIDADE ESCOLHIDA"].map(normalize_text),
            "rank": pd.to_numeric(raw["CLASSIFICACAO"], errors="coerce"),
            "score": pd.to_numeric(raw[score_column], errors="coerce"),
        }
    )
    frame = frame[frame["name"].ne("") & ~frame["result"].str.contains("SUB JUDICE")].copy()
    frame["candidate"] = frame["name"].map(lambda value: hashlib.sha256(value.encode()).hexdigest())
    frame["first_choice"] = frame["preference"].str.match(r"^1(\D|$)")
    frame["row_selected"] = frame["result"].str.startswith("ALOCADO")
    frame["row_selected_ac"] = frame["result"].eq("ALOCADO - AC") | frame["result"].eq("ALOCADO")
    frame["row_confirmed"] = frame["row_selected"]
    return frame


def add_candidate_outcomes(frame: pd.DataFrame) -> pd.DataFrame:
    candidate = (
        frame.groupby("candidate", as_index=False)
        .agg(
            any_selection=("row_selected", "max"),
            any_confirmation=("row_confirmed", "max"),
            homologated=("homologated", "max"),
            active_snapshot=("active_snapshot", "max"),
        )
    )
    columns = ["any_selection", "any_confirmation", "homologated", "active_snapshot"]
    base = frame.drop(columns=columns, errors="ignore")
    return base.merge(candidate, on="candidate", how="left", validate="many_to_one")


def cutoff_pairs(frame: pd.DataFrame, label: str) -> tuple[dict[str, Any], pd.DataFrame]:
    sample = frame[
        frame["first_choice"]
        & frame["rank"].notna()
        & frame["score"].notna()
        & frame["course"].ne("")
        & frame["cnes"].ne("")
    ].copy()
    sample["cell"] = sample["course"] + "|" + sample["cnes"]
    n_mixed = 0
    n_sharp = 0
    pairs: list[dict[str, Any]] = []
    for _, group in sample.groupby("cell", sort=True):
        selected = group[group["row_selected"]]
        nonselected = group[~group["row_selected"]]
        if selected.empty or nonselected.empty:
            continue
        n_mixed += 1
        cutoff = float(selected["rank"].max())
        sharp = cutoff < float(nonselected["rank"].min())
        if sharp:
            n_sharp += 1
        if not sharp or not (nonselected["rank"] == cutoff + 1).any():
            continue
        winner_rows = selected[selected["rank"] == cutoff]
        runner_rows = nonselected[nonselected["rank"] == cutoff + 1]
        if len(winner_rows) != 1 or len(runner_rows) != 1:
            raise AssertionError(f"{label}: ranking não é único no corte de uma célula")
        winner = winner_rows.iloc[0]
        runner = runner_rows.iloc[0]
        record: dict[str, Any] = {
            "cycle_call": label,
            "winner_score": float(winner["score"]),
            "runner_score": float(runner["score"]),
            "same_published_score": bool(winner["score"] == runner["score"]),
            "clean_open_competition": bool(
                winner["row_selected_ac"]
                and winner["registration_type"] == "AC"
                and runner["registration_type"] == "AC"
            ),
        }
        for outcome in ["any_selection", "any_confirmation", "homologated", "active_snapshot"]:
            if outcome in group.columns:
                record[f"winner_{outcome}"] = int(winner[outcome])
                record[f"runner_{outcome}"] = int(runner[outcome])
        pairs.append(record)
    pair_frame = pd.DataFrame(pairs)
    support = {
        "ciclo_chamada": label,
        "registros_publicados": int(len(frame)),
        "candidatos_publicados": int(frame["candidate"].nunique()),
        "primeiras_opcoes_com_rank_e_escore": int(len(sample)),
        "celulas_curso_cnes": int(sample["cell"].nunique()),
        "celulas_competitivas": int(n_mixed),
        "celulas_com_corte_sharp_no_rank": int(n_sharp),
        "pares_adjacentes": int(len(pair_frame)),
        "pares_mesmo_escore_publicado": int(pair_frame["same_published_score"].sum()) if len(pair_frame) else 0,
        "pares_ampla_concorrencia": int(pair_frame["clean_open_competition"].sum()) if len(pair_frame) else 0,
    }
    return support, pair_frame


def paired_result(
    pairs: pd.DataFrame,
    cycle_call: str,
    sample: str,
    outcome: str,
) -> dict[str, Any]:
    winner = pairs[f"winner_{outcome}"].astype(float)
    runner = pairs[f"runner_{outcome}"].astype(float)
    difference = winner - runner
    n = len(difference)
    if n < 2:
        raise AssertionError(f"Amostra insuficiente para {cycle_call}/{sample}/{outcome}")
    estimate = float(difference.mean())
    se = float(difference.std(ddof=1) / math.sqrt(n))
    critical = float(stats.t.ppf(0.975, n - 1))
    if se == 0:
        p_value = 0.0 if estimate != 0 else 1.0
    else:
        p_value = float(2 * stats.t.sf(abs(estimate / se), n - 1))
    return {
        "ciclo_chamada": cycle_call,
        "amostra": sample,
        "desfecho": outcome,
        "n_pares": n,
        "media_ultimo_selecionado": float(winner.mean()),
        "media_primeiro_nao_selecionado": float(runner.mean()),
        "diferenca": estimate,
        "erro_padrao_pareado": se,
        "ic95_inferior": estimate - critical * se,
        "ic95_superior": estimate + critical * se,
        "p_valor_t_pareado": p_value,
        "classificacao_inferencial": "DESCONTINUIDADE_PRELIMINAR_NAO_CAUSAL",
    }


def results_for_call(pairs: pd.DataFrame, label: str) -> list[dict[str, Any]]:
    outcomes = [
        outcome
        for outcome in ["any_selection", "any_confirmation", "homologated", "active_snapshot"]
        if f"winner_{outcome}" in pairs.columns
    ]
    rows = [paired_result(pairs, label, "todos_pares_adjacentes", outcome) for outcome in outcomes]
    same_score = pairs[pairs["same_published_score"]].copy()
    for outcome in ["homologated", "active_snapshot"]:
        if f"winner_{outcome}" in pairs.columns and len(same_score) >= 2:
            rows.append(paired_result(same_score, label, "mesmo_escore_publicado", outcome))
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    inputs = [
        CALL1_RESULT,
        CALL1_HOMOLOG,
        CALL2_RESULT,
        CALL2_HOMOLOG,
        CYCLE2_CALL2,
        CYCLE3_CALL1,
        ACTIVE_SNAPSHOT,
    ]
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(path)

    homolog1 = read_names(CALL1_HOMOLOG, "Quadro 1", 7)
    homolog2_cumulative = read_names(CALL2_HOMOLOG, "Homologados", 1)
    homolog2_new = homolog2_cumulative - homolog1
    nominal = pd.read_csv(ACTIVE_SNAPSHOT)
    if {"nome", "ciclo", "dt_referencia"} - set(nominal.columns):
        raise AssertionError("Snapshot nominal perdeu nome, ciclo ou data de referência")
    active_cycle1 = set(nominal.loc[nominal["ciclo"].eq(1), "nome"].map(normalize_text))
    active_cycle1.discard("")
    reference_dates = sorted(nominal.loc[nominal["ciclo"].eq(1), "dt_referencia"].dropna().astype(str).unique())
    if len(reference_dates) != 1:
        raise AssertionError("Snapshot do ciclo 1 não tem uma única data de referência")

    call1 = add_candidate_outcomes(read_call1(homolog1, active_cycle1))
    call2 = add_candidate_outcomes(read_call2(homolog2_new, active_cycle1))
    if call1["name"].nunique() != call1["candidate"].nunique():
        raise AssertionError("Primeira chamada contém nomes duplicados entre candidatos")
    if call2["name"].nunique() != call2["candidate"].nunique():
        raise AssertionError("Segunda chamada contém nomes duplicados entre candidatos")

    support1, pairs1 = cutoff_pairs(call1, "2025_C1_CH1")
    support2, pairs2 = cutoff_pairs(call2, "2025_C1_CH2")
    support3, _ = cutoff_pairs(read_support_2026(CYCLE2_CALL2, "2026_C2_CH2"), "2026_C2_CH2")
    support4, _ = cutoff_pairs(read_support_2026(CYCLE3_CALL1, "2026_C3_CH1"), "2026_C3_CH1")
    support = pd.DataFrame([support1, support2, support3, support4])

    results = results_for_call(pairs1, "2025_C1_CH1") + results_for_call(pairs2, "2025_C1_CH2")
    common_columns = [
        "cycle_call",
        "winner_score",
        "runner_score",
        "same_published_score",
        "clean_open_competition",
        "winner_homologated",
        "runner_homologated",
        "winner_active_snapshot",
        "runner_active_snapshot",
    ]
    pooled = pd.concat([pairs1[common_columns], pairs2[common_columns]], ignore_index=True)
    results.extend(
        [
            paired_result(pooled, "2025_C1_CH1_E_CH2", "todos_pares_adjacentes", "homologated"),
            paired_result(pooled, "2025_C1_CH1_E_CH2", "todos_pares_adjacentes", "active_snapshot"),
            paired_result(
                pooled[pooled["same_published_score"]],
                "2025_C1_CH1_E_CH2",
                "mesmo_escore_publicado",
                "homologated",
            ),
            paired_result(
                pooled[pooled["same_published_score"]],
                "2025_C1_CH1_E_CH2",
                "mesmo_escore_publicado",
                "active_snapshot",
            ),
        ]
    )
    result_table = pd.DataFrame(results)

    # Guards substantivos: se mudarem, a interpretação deve ser reaberta.
    expected_pairs = {"2025_C1_CH1": 136, "2025_C1_CH2": 57, "2026_C2_CH2": 56, "2026_C3_CH1": 174}
    observed_pairs = dict(zip(support["ciclo_chamada"], support["pares_adjacentes"], strict=True))
    if observed_pairs != expected_pairs:
        raise AssertionError(f"Suporte no corte mudou: {observed_pairs}")
    if len(homolog1) != 316 or len(active_cycle1) != 521:
        raise AssertionError("Universos públicos de homologação/ativos do ciclo 1 mudaram")

    total_pairs = int(support["pares_adjacentes"].sum())
    total_same_score = int(support["pares_mesmo_escore_publicado"].sum())
    r1_hom = result_table.query(
        "ciclo_chamada == '2025_C1_CH1' and amostra == 'todos_pares_adjacentes' and desfecho == 'homologated'"
    ).iloc[0]
    r1_active = result_table.query(
        "ciclo_chamada == '2025_C1_CH1' and amostra == 'todos_pares_adjacentes' and desfecho == 'active_snapshot'"
    ).iloc[0]
    r2_hom = result_table.query(
        "ciclo_chamada == '2025_C1_CH2' and amostra == 'todos_pares_adjacentes' and desfecho == 'homologated'"
    ).iloc[0]
    r2_active = result_table.query(
        "ciclo_chamada == '2025_C1_CH2' and amostra == 'todos_pares_adjacentes' and desfecho == 'active_snapshot'"
    ).iloc[0]

    matched_homolog1 = len(homolog1 & set(call1["name"]))
    matched_homolog2 = len(homolog2_new & set(call2["name"]))
    linkage = {
        "metodo_publico_exploratorio": "nome_normalizado_exato_e_unico_sem_fuzzy_match",
        "cpf": "mascaras_incompativeis_entre_publicacoes",
        "homologados_ch1": len(homolog1),
        "homologados_ch1_ligados": matched_homolog1,
        "novos_homologados_ch2": len(homolog2_new),
        "novos_homologados_ch2_ligados": matched_homolog2,
        "ativos_ciclo1_em_snapshot": len(active_cycle1),
        "data_snapshot": reference_dates[0],
        "limite": "ausencia_no_snapshot_mede_nao_estar_ativo_na_data; nao_reconstroi_duracao_ou_saida",
    }

    summary = {
        "status": "DESENHO_PROMISSOR_MAS_NAO_CAUSAL_COM_DADOS_PUBLICOS",
        "pergunta_recomendada": "Efeito local de ganhar a vaga de primeira opção sobre homologação e presença ativa posterior no PMM-E.",
        "unidade": "par de candidatos no mesmo curso-CNES: último selecionado e primeiro não selecionado",
        "suporte": {
            "pares_adjacentes_total_quatro_publicacoes": total_pairs,
            "pares_com_mesmo_escore_publicado": total_same_score,
            "pares_com_outcome_2025": int(len(pooled)),
            "pares_mesmo_escore_com_outcome_2025": int(pooled["same_published_score"].sum()),
        },
        "resultados_preliminares": {
            "ch1_homologacao_diferenca_pp": 100 * float(r1_hom["diferenca"]),
            "ch1_ativo_snapshot_diferenca_pp": 100 * float(r1_active["diferenca"]),
            "ch2_homologacao_diferenca_pp": 100 * float(r2_hom["diferenca"]),
            "ch2_ativo_snapshot_diferenca_pp": 100 * float(r2_active["diferenca"]),
        },
        "por_que_ainda_nao_causal": [
            "ranking é discreto e candidatos adjacentes diferem em escore e desempates",
            "o edital desempata por mesma UF de domicílio/nascimento e depois maior idade",
            "os campos individuais de desempate não estão nas planilhas públicas",
            "recursos, cotas, realocações e locais desconsiderados precisam ser reconstruídos",
            "a ligação pública usa nome exato; falta identificador pseudonimizado estável",
        ],
        "dados_minimos_para_upgrade": [
            "id_profissional_pseudo e id_vaga_pseudo estáveis",
            "barema final e histórico de recursos",
            "indicador do desempate mesma UF para cada candidato-vaga",
            "idade em dias no corte ou distância em dias ao limiar etário, sem data de nascimento",
            "quantidade de vagas por modalidade e ordem completa de alocação",
            "eventos de confirmação, homologação, início e saída com datas",
        ],
        "estimando_causal_condicional": "ITT local de ser selecionado na primeira opção; desfechos: homologação, início e ativo aos 90/180 dias.",
        "desenho_condicional": "RDD empilhado na idade dentro de blocos curso-CNES x barema x indicador mesma-UF, ou randomização local somente após demonstrar comparabilidade.",
        "fontes_oficiais": {"edital_3_2025": OFFICIAL_NOTICE},
        "linkage": linkage,
        "hashes_entradas": {str(path.relative_to(ROOT)): sha256(path) for path in inputs},
        "arquivos": {
            "suporte": str(SUPPORT_TABLE.relative_to(ROOT)),
            "resultados": str(RESULTS_TABLE.relative_to(ROOT)),
            "relatorio": str(REPORT_MD.relative_to(ROOT)),
        },
        "privacidade": "Nenhum nome, CPF, hash de candidato ou linha individual foi persistido.",
    }

    report = f"""# A7 — Corte de seleção, atração e presença ativa

> **Veredito:** existe uma descontinuidade administrativa observável e substantivamente grande, mas os dados públicos ainda não autorizam chamá-la de efeito causal.

## 1. O que foi encontrado

As listas publicadas permitem formar pares dentro da mesma célula curso–CNES: o último candidato selecionado em sua primeira opção e o primeiro candidato não selecionado. Há **{total_pairs} pares adjacentes** em quatro publicações; **{total_same_score}** têm o mesmo escore publicado. Os dois estágios de 2025 fornecem **{len(pooled)} pares** com homologação e presença ativa observáveis; **{int(pooled['same_published_score'].sum())}** têm o mesmo escore.

Na primeira chamada de 2025, entre {int(r1_hom['n_pares'])} pares, a homologação foi {100*r1_hom['media_ultimo_selecionado']:.1f}% para o último selecionado e {100*r1_hom['media_primeiro_nao_selecionado']:.1f}% para o primeiro não selecionado: diferença de **{100*r1_hom['diferenca']:.1f} p.p.** (IC95% {100*r1_hom['ic95_inferior']:.1f} a {100*r1_hom['ic95_superior']:.1f}). No snapshot de {reference_dates[0]}, a presença ativa no ciclo 1 foi {100*r1_active['media_ultimo_selecionado']:.1f}% versus {100*r1_active['media_primeiro_nao_selecionado']:.1f}%, diferença de **{100*r1_active['diferenca']:.1f} p.p.** (IC95% {100*r1_active['ic95_inferior']:.1f} a {100*r1_active['ic95_superior']:.1f}).

Na segunda chamada, as diferenças correspondentes foram **{100*r2_hom['diferenca']:.1f} p.p.** em homologação e **{100*r2_active['diferenca']:.1f} p.p.** em presença ativa. A repetição do sinal em chamadas separadas torna o padrão relevante, mas não resolve a identificação.

## 2. Por que isso ainda não é causal

O ranking não é um sorteio. O Edital nº 3/2025 determina que empates sejam resolvidos primeiro pela escolha de vaga na mesma UF do domicílio ou nascimento e depois pela maior idade. Localidade prévia e idade também podem afetar aceitação e permanência. Esses campos não são publicados. Logo, nem comparar rank 1 com rank 2 nem restringir ao mesmo barema elimina seleção não observada.

O vínculo entre arquivos foi feito somente por nome normalizado exato e único, sem aproximação textual. Todos os {len(homolog1)} homologados da primeira chamada aparecem na lista de seleção, mas as máscaras de CPF são incompatíveis. O snapshot de ativos mede estar ativo em uma data fixa; ele não reconstrói início, interrupções ou duração contínua.

## 3. Trabalho pequeno recomendado

**Pergunta:** ganhar marginalmente a vaga de primeira opção aumenta a entrada e a presença posterior do especialista no PMM-E?

**Estimando principal:** intenção de tratamento local de ganhar a primeira opção sobre início em até 30 dias. Homologação e presença ativa em 90 e 180 dias serão secundários. O desfecho de presença deve ser incondicional à entrada, evitando selecionar apenas quem começou.

**Desenho:** ampla concorrência; exclusão predefinida de casos sub judice; reconstrução integral de preferências, vagas e recursos. Dentro dos empates de barema e do mesmo status de prioridade por UF, usar idade em dias centrada na idade do último selecionado como running variable em RDD empilhado. A análise de pares adjacentes fica como apresentação intuitiva e robustez.

**Dados mínimos:** identificadores pseudonimizados estáveis, barema final, indicador de prioridade pela UF, idade em dias ou distância etária ao cutoff, capacidade por modalidade e eventos datados de confirmação, homologação, início e saída. Não é necessário receber data de nascimento nem endereço.

## 4. Relação com os resultados existentes

A4 continua sendo evidência associativa sobre quais territórios atraíram candidatos. A5 continua sendo evidência associativa sobre estoque municipal no CNES. O RDD do IVS continua encerrado. A7 é um desenho distinto, no nível do candidato, voltado exatamente à margem de atração/entrada; ele não transforma retrospectivamente A4 ou A5 em resultados causais.

## 5. Uso autorizado

- **Hoje:** “há uma grande descontinuidade de homologação e presença ativa no corte publicado de seleção”.
- **Ainda não:** “ganhar a vaga causou o aumento”.
- **Após os dados de desempate e os diagnósticos:** linguagem causal local, se o RDD empilhado passar suporte, continuidade e testes de manipulação/balanceamento.

Fonte normativa: {OFFICIAL_NOTICE}
"""

    atomic_csv(SUPPORT_TABLE, support)
    atomic_csv(RESULTS_TABLE, result_table)
    atomic_text(SUMMARY_JSON, json.dumps(summary, ensure_ascii=False, indent=2))
    atomic_text(REPORT_MD, report)
    print(
        "[OK] A7: corte candidato auditado; "
        f"{total_pairs} pares em quatro publicações, {len(pooled)} com outcomes de 2025."
    )


if __name__ == "__main__":
    main()
