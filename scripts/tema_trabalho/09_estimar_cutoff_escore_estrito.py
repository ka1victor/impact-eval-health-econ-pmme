"""A8 - Estima o efeito local de ganhar a primeira opcao no cutoff de escore.

O desenho usa somente publicacoes abertas ja existentes no repositorio. A
amostra principal contem pares da ampla concorrencia, na mesma celula
curso-CNES, cuja primeira opcao e a vaga disputada e cujos escores diferem em
exatamente um ponto no limite de selecao. Empates sao excluidos porque o edital
usa UF e idade como criterios de desempate nao publicados.

Nomes e CPFs sao usados apenas em memoria para ligacao exata. Nenhum
identificador individual, hash de candidato ou linha por pessoa e persistido.
"""

from __future__ import annotations

import json
import math
import re
import runpy
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import pandas as pd
from scipy import stats


matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "tema_trabalho"
A7_SCRIPT = ROOT / "scripts" / "tema_trabalho" / "08_auditar_cutoff_selecao.py"

PROTOCOL_JSON = OUT / "A8_protocolo_cutoff_escore.json"
SUPPORT_TABLE = OUT / "A8_tabela_01_suporte_escore_estrito.csv"
ESTIMATES_TABLE = OUT / "A8_tabela_02_estimativas_escore_estrito.csv"
PLACEBOS_TABLE = OUT / "A8_tabela_03_placebos_escore_estrito.csv"
SENSITIVITY_TABLE = OUT / "A8_tabela_04_sensibilidade_gap.csv"
LEAVE_ONE_OUT_TABLE = OUT / "A8_tabela_05_leave_one_out.csv"
SUMMARY_JSON = OUT / "A8_estimativas_cutoff_escore.json"
REPORT_MD = OUT / "A8_relatorio_cutoff_escore.md"
EFFECT_FIGURE = OUT / "A8_figura_01_efeitos_cutoff_escore.png"

OFFICIAL_NOTICE_2025 = (
    "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/"
    "chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-"
    "mais-medicos-especialistas/edital-de-chamamento-publico-no-3-2025.pdf"
)
OFFICIAL_PAGE_2026 = (
    "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/"
    "chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/"
    "chamamento-publico-sgtes-ms-no-1-2026-pmm-e"
)

OUTCOME_LABELS = {
    "homologated_same_cell": "homologacao_mesma_celula",
    "active_same_cell": "ativo_mesma_celula_snapshot",
    "homologated_anywhere": "homologacao_qualquer_local",
    "active_anywhere": "ativo_qualquer_local_snapshot",
}


def atomic_text(path: Path, value: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(value, encoding="utf-8")
    tmp.replace(path)


def atomic_csv(path: Path, frame: pd.DataFrame) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(tmp, index=False, encoding="utf-8")
    tmp.replace(path)


def course_code(value: Any, normalize_text: Any) -> str:
    text = normalize_text(value)
    match = re.match(r"^\s*(\d{1,2})\b", text)
    return match.group(1).zfill(2) if match else ""


def location_key(
    name: Any,
    course: Any,
    cnes: Any,
    *,
    normalize_text: Any,
    digits: Any,
) -> str:
    return "|".join(
        [
            normalize_text(name),
            course_code(course, normalize_text),
            digits(cnes),
        ]
    )


def add_public_outcomes(
    frame: pd.DataFrame,
    *,
    homologated_names: set[str],
    homologated_locations: set[str],
    active_names: set[str],
    active_locations: set[str],
    normalize_text: Any,
    digits: Any,
) -> pd.DataFrame:
    result = frame.copy()
    keys = [
        location_key(
            name,
            course,
            cnes,
            normalize_text=normalize_text,
            digits=digits,
        )
        for name, course, cnes in zip(
            result["name"], result["course"], result["cnes"], strict=True
        )
    ]
    result["homologated_same_cell"] = [key in homologated_locations for key in keys]
    result["active_same_cell"] = [key in active_locations for key in keys]
    result["homologated_anywhere"] = result["name"].isin(homologated_names)
    result["active_anywhere"] = result["name"].isin(active_names)
    return result


def build_contrasts(frame: pd.DataFrame, cycle_call: str) -> pd.DataFrame:
    sample = frame[
        frame["first_choice"]
        & frame["rank"].notna()
        & frame["score"].notna()
        & frame["course"].ne("")
        & frame["cnes"].ne("")
    ].copy()
    sample["cell"] = sample["course"] + "|" + sample["cnes"]
    rows: list[dict[str, Any]] = []
    specifications = [
        ("cutoff", 0, 1, True, False),
        ("placebo_acima", -1, 0, True, True),
        ("placebo_abaixo", 1, 2, False, False),
    ]

    for cell, group in sample.groupby("cell", sort=True):
        selected = group[group["row_selected"]]
        nonselected = group[~group["row_selected"]]
        if selected.empty or nonselected.empty:
            continue
        cutoff = float(selected["rank"].max())
        if cutoff >= float(nonselected["rank"].min()):
            continue

        for contrast_type, high_offset, low_offset, high_selected, low_selected in specifications:
            high_rows = group[group["rank"].eq(cutoff + high_offset)]
            low_rows = group[group["rank"].eq(cutoff + low_offset)]
            if len(high_rows) != 1 or len(low_rows) != 1:
                continue
            high = high_rows.iloc[0]
            low = low_rows.iloc[0]
            if bool(high["row_selected"]) != high_selected:
                continue
            if bool(low["row_selected"]) != low_selected:
                continue
            if high["registration_type"] != "AC" or low["registration_type"] != "AC":
                continue
            if contrast_type == "cutoff" and not bool(high["row_selected_ac"]):
                continue
            if contrast_type == "placebo_acima" and not (
                bool(high["row_selected_ac"]) and bool(low["row_selected_ac"])
            ):
                continue

            record: dict[str, Any] = {
                "cycle_call": cycle_call,
                "contrast_type": contrast_type,
                "score_gap": float(high["score"] - low["score"]),
                "course_code": course_code(high["course"], lambda value: str(value)),
                "uf": str(high.get("uf", "")),
                "cell_internal": cell,
                "high_name_internal": str(high["name"]),
                "low_name_internal": str(low["name"]),
            }
            for outcome in OUTCOME_LABELS:
                record[f"high_{outcome}"] = int(bool(high[outcome]))
                record[f"low_{outcome}"] = int(bool(low[outcome]))
            rows.append(record)
    return pd.DataFrame(rows)


def paired_estimate(
    frame: pd.DataFrame,
    *,
    cycle_call: str,
    sample: str,
    outcome: str,
    classification: str,
) -> dict[str, Any]:
    high = frame[f"high_{outcome}"].astype(float)
    low = frame[f"low_{outcome}"].astype(float)
    difference = high - low
    n = len(frame)
    if n < 2:
        raise AssertionError(f"Amostra insuficiente: {cycle_call}/{sample}/{outcome}")
    estimate = float(difference.mean())
    standard_error = float(difference.std(ddof=1) / math.sqrt(n))
    critical = float(stats.t.ppf(0.975, n - 1))
    positive = int(difference.eq(1).sum())
    negative = int(difference.eq(-1).sum())
    discordant = positive + negative
    exact_p = (
        float(stats.binomtest(positive, discordant, 0.5).pvalue)
        if discordant
        else 1.0
    )
    return {
        "ciclo_chamada": cycle_call,
        "amostra": sample,
        "desfecho": OUTCOME_LABELS[outcome],
        "n_pares": n,
        "media_acima": float(high.mean()),
        "media_abaixo": float(low.mean()),
        "diferenca": estimate,
        "erro_padrao_pareado": standard_error,
        "ic95_convencional_inferior": estimate - critical * standard_error,
        "ic95_convencional_superior": estimate + critical * standard_error,
        "discordantes_favoraveis": positive,
        "discordantes_contrarios": negative,
        "p_exato_pareado_bicaudal": exact_p,
        "classificacao_inferencial": classification,
    }


def leave_one_out(
    frame: pd.DataFrame,
    *,
    group_column: str,
    outcome: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for value in sorted(frame[group_column].dropna().astype(str).unique()):
        remaining = frame[frame[group_column].astype(str).ne(value)]
        if len(remaining) < 2:
            continue
        difference = (
            remaining[f"high_{outcome}"].astype(float)
            - remaining[f"low_{outcome}"].astype(float)
        )
        rows.append(
            {
                "dimensao_excluida": group_column,
                "grupo_excluido": value,
                "desfecho": OUTCOME_LABELS[outcome],
                "n_pares_restantes": len(remaining),
                "diferenca": float(difference.mean()),
            }
        )
    return rows


def render_figure(estimates: pd.DataFrame, placebos: pd.DataFrame) -> None:
    def pick(frame: pd.DataFrame, call: str, sample: str, outcome: str) -> pd.Series:
        row = frame[
            frame["ciclo_chamada"].eq(call)
            & frame["amostra"].eq(sample)
            & frame["desfecho"].eq(outcome)
        ]
        if len(row) != 1:
            raise AssertionError(f"Linha ausente para figura: {call}/{sample}/{outcome}")
        return row.iloc[0]

    items = [
        (
            "2025: homologação no local",
            pick(estimates, "2025_C1_CH1_E_CH2", "gap_1_ac", "homologacao_mesma_celula"),
            "#006D77",
        ),
        (
            "2025: ativo no local",
            pick(estimates, "2025_C1_CH1_E_CH2", "gap_1_ac", "ativo_mesma_celula_snapshot"),
            "#006D77",
        ),
        (
            "Placebo abaixo: homologação",
            pick(placebos, "2025_C1_CH1_E_CH2", "placebo_abaixo_gap_1_ac", "homologacao_mesma_celula"),
            "#7A7A7A",
        ),
        (
            "Placebo abaixo: ativo",
            pick(placebos, "2025_C1_CH1_E_CH2", "placebo_abaixo_gap_1_ac", "ativo_mesma_celula_snapshot"),
            "#7A7A7A",
        ),
        (
            "2026: ativo no local",
            pick(estimates, "2026_C2_CH2", "gap_1_ac_replicacao", "ativo_mesma_celula_snapshot"),
            "#D97706",
        ),
    ]
    labels = [item[0] for item in items]
    points = np.array([float(item[1]["diferenca"]) for item in items]) * 100
    lower = np.array([float(item[1]["ic95_convencional_inferior"]) for item in items]) * 100
    upper = np.array([float(item[1]["ic95_convencional_superior"]) for item in items]) * 100
    colors = [item[2] for item in items]
    y = np.arange(len(items))[::-1]

    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    ax.axvline(0, color="#333333", linewidth=1, linestyle="--")
    for idx in range(len(items)):
        ax.errorbar(
            points[idx],
            y[idx],
            xerr=[[points[idx] - lower[idx]], [upper[idx] - points[idx]]],
            fmt="o",
            color=colors[idx],
            ecolor=colors[idx],
            capsize=4,
            markersize=7,
        )
    ax.set_yticks(y, labels)
    ax.set_xlabel("Diferença entre candidatos acima e abaixo do limite (p.p.)")
    ax.set_title("Efeito local da alocação de primeira opção")
    ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.set_xlim(min(-25, float(lower.min()) - 5), max(90, float(upper.max()) + 5))
    fig.text(
        0.01,
        0.01,
        "IC95% convencional pareado; a inferência principal usa também teste exato entre pares.",
        fontsize=9,
        color="#555555",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    tmp = EFFECT_FIGURE.with_suffix(".png.tmp")
    fig.savefig(tmp, dpi=180, bbox_inches="tight", format="png")
    plt.close(fig)
    tmp.replace(EFFECT_FIGURE)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a7 = runpy.run_path(str(A7_SCRIPT))
    normalize_text = a7["normalize_text"]
    digits = a7["digits"]
    read_names = a7["read_names"]
    read_call1 = a7["read_call1"]
    read_call2 = a7["read_call2"]
    read_support_2026 = a7["read_support_2026"]
    cutoff_pairs = a7["cutoff_pairs"]
    sha256 = a7["sha256"]

    call1_result: Path = a7["CALL1_RESULT"]
    call1_homolog: Path = a7["CALL1_HOMOLOG"]
    call2_result: Path = a7["CALL2_RESULT"]
    call2_homolog: Path = a7["CALL2_HOMOLOG"]
    cycle2_call2: Path = a7["CYCLE2_CALL2"]
    active_snapshot: Path = a7["ACTIVE_SNAPSHOT"]
    inputs = [
        call1_result,
        call1_homolog,
        call2_result,
        call2_homolog,
        cycle2_call2,
        active_snapshot,
    ]
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(path)

    homolog1_raw = pd.read_excel(call1_homolog, sheet_name="Quadro 1")
    homolog2_raw = pd.read_excel(call2_homolog, sheet_name="Homologados")
    if len(homolog1_raw.columns) < 8 or len(homolog2_raw.columns) < 8:
        raise AssertionError("Planilhas de homologacao perderam colunas esperadas")

    homolog1_names = set(homolog1_raw.iloc[:, 7].map(normalize_text)) - {""}
    homolog2_all_names = set(homolog2_raw.iloc[:, 1].map(normalize_text)) - {""}
    homolog2_names = homolog2_all_names - homolog1_names
    homolog1_locations = {
        location_key(
            row.iloc[7],
            row.iloc[1],
            row.iloc[5],
            normalize_text=normalize_text,
            digits=digits,
        )
        for _, row in homolog1_raw.iterrows()
    }
    homolog2_locations = {
        location_key(
            row.iloc[1],
            row.iloc[7],
            row.iloc[6],
            normalize_text=normalize_text,
            digits=digits,
        )
        for _, row in homolog2_raw.iterrows()
        if normalize_text(row.iloc[1]) in homolog2_names
    }

    nominal = pd.read_csv(active_snapshot)
    required_nominal = {"nome", "curso", "co_cnes", "ciclo", "dt_referencia"}
    if required_nominal - set(nominal.columns):
        raise AssertionError("Snapshot nominal perdeu colunas necessarias")
    reference_dates = sorted(nominal["dt_referencia"].dropna().astype(str).unique())
    if reference_dates != ["2026-08-12"]:
        raise AssertionError(f"Data inesperada no snapshot: {reference_dates}")

    def active_sets(cycle: int) -> tuple[set[str], set[str]]:
        subset = nominal[nominal["ciclo"].eq(cycle)]
        names = set(subset["nome"].map(normalize_text)) - {""}
        locations = {
            location_key(
                row["nome"],
                row["curso"],
                row["co_cnes"],
                normalize_text=normalize_text,
                digits=digits,
            )
            for _, row in subset.iterrows()
        }
        return names, locations

    active1_names, active1_locations = active_sets(1)
    active2_names, active2_locations = active_sets(2)

    call1 = add_public_outcomes(
        read_call1(set(), set()),
        homologated_names=homolog1_names,
        homologated_locations=homolog1_locations,
        active_names=active1_names,
        active_locations=active1_locations,
        normalize_text=normalize_text,
        digits=digits,
    )
    call2 = add_public_outcomes(
        read_call2(set(), set()),
        homologated_names=homolog2_names,
        homologated_locations=homolog2_locations,
        active_names=active1_names,
        active_locations=active1_locations,
        normalize_text=normalize_text,
        digits=digits,
    )
    cycle2 = read_support_2026(cycle2_call2, "2026_C2_CH2")
    cycle2 = add_public_outcomes(
        cycle2,
        homologated_names=set(),
        homologated_locations=set(),
        active_names=active2_names,
        active_locations=active2_locations,
        normalize_text=normalize_text,
        digits=digits,
    )

    contrast1 = build_contrasts(call1, "2025_C1_CH1")
    contrast2 = build_contrasts(call2, "2025_C1_CH2")
    contrast_cycle2 = build_contrasts(cycle2, "2026_C2_CH2")
    if any(frame.empty for frame in [contrast1, contrast2, contrast_cycle2]):
        raise AssertionError("Alguma chamada perdeu todos os contrastes no cutoff")

    primary1 = contrast1[
        contrast1["contrast_type"].eq("cutoff") & contrast1["score_gap"].eq(1)
    ].copy()
    primary2 = contrast2[
        contrast2["contrast_type"].eq("cutoff") & contrast2["score_gap"].eq(1)
    ].copy()
    primary_2025 = pd.concat([primary1, primary2], ignore_index=True)
    replication = contrast_cycle2[
        contrast_cycle2["contrast_type"].eq("cutoff")
        & contrast_cycle2["score_gap"].eq(1)
    ].copy()
    if (len(primary1), len(primary2), len(primary_2025), len(replication)) != (
        30,
        6,
        36,
        11,
    ):
        raise AssertionError("Suporte estrito mudou; revisar o protocolo A8")

    support_rows: list[dict[str, Any]] = []
    for label, frame, contrast in [
        ("2025_C1_CH1", call1, contrast1),
        ("2025_C1_CH2", call2, contrast2),
        ("2026_C2_CH2", cycle2, contrast_cycle2),
    ]:
        _, adjacent = cutoff_pairs(frame, label)
        cutoff = contrast[contrast["contrast_type"].eq("cutoff")]
        support_rows.append(
            {
                "ciclo_chamada": label,
                "pares_adjacentes": len(adjacent),
                "pares_cutoff_ampla_concorrencia": len(cutoff),
                "pares_gap_1_ac": int(cutoff["score_gap"].eq(1).sum()),
                "pares_gap_2_ac": int(cutoff["score_gap"].eq(2).sum()),
                "pares_empate_excluidos": int(cutoff["score_gap"].eq(0).sum()),
                "violacoes_gap_1": int((cutoff["score_gap"] < 0).sum()),
                "placebos_abaixo_gap_1_ac": int(
                    (
                        contrast["contrast_type"].eq("placebo_abaixo")
                        & contrast["score_gap"].eq(1)
                    ).sum()
                ),
                "placebos_acima_gap_1_ac": int(
                    (
                        contrast["contrast_type"].eq("placebo_acima")
                        & contrast["score_gap"].eq(1)
                    ).sum()
                ),
            }
        )
    support = pd.DataFrame(support_rows)

    estimate_rows: list[dict[str, Any]] = []
    for label, frame, sample in [
        ("2025_C1_CH1", primary1, "gap_1_ac"),
        ("2025_C1_CH2", primary2, "gap_1_ac"),
        ("2025_C1_CH1_E_CH2", primary_2025, "gap_1_ac"),
    ]:
        for outcome in OUTCOME_LABELS:
            estimate_rows.append(
                paired_estimate(
                    frame,
                    cycle_call=label,
                    sample=sample,
                    outcome=outcome,
                    classification="EFEITO_LOCAL_CONDICIONAL_A_RANDOMIZACAO_LOCAL",
                )
            )
    for outcome in ["active_same_cell", "active_anywhere"]:
        estimate_rows.append(
            paired_estimate(
                replication,
                cycle_call="2026_C2_CH2",
                sample="gap_1_ac_replicacao",
                outcome=outcome,
                classification="REPLICACAO_DIRECIONAL_IMPRECISA",
            )
        )
    estimates = pd.DataFrame(estimate_rows)

    placebo_rows: list[dict[str, Any]] = []
    for contrast_type in ["placebo_abaixo", "placebo_acima"]:
        pooled = pd.concat(
            [
                contrast1[
                    contrast1["contrast_type"].eq(contrast_type)
                    & contrast1["score_gap"].eq(1)
                ],
                contrast2[
                    contrast2["contrast_type"].eq(contrast_type)
                    & contrast2["score_gap"].eq(1)
                ],
            ],
            ignore_index=True,
        )
        if len(pooled) < 2:
            continue
        for outcome in OUTCOME_LABELS:
            placebo_rows.append(
                paired_estimate(
                    pooled,
                    cycle_call="2025_C1_CH1_E_CH2",
                    sample=f"{contrast_type}_gap_1_ac",
                    outcome=outcome,
                    classification="PLACEBO",
                )
            )
    placebos = pd.DataFrame(placebo_rows)

    cutoff_2025 = pd.concat(
        [
            contrast1[contrast1["contrast_type"].eq("cutoff")],
            contrast2[contrast2["contrast_type"].eq("cutoff")],
        ],
        ignore_index=True,
    )
    sensitivity_rows: list[dict[str, Any]] = []
    sensitivity_rules = {
        "gap_1_ac": cutoff_2025["score_gap"].eq(1),
        "gap_positivo_ate_2_ac": cutoff_2025["score_gap"].between(1, 2),
        "qualquer_gap_positivo_ac": cutoff_2025["score_gap"].gt(0),
        "empate_descritivo_nao_causal": cutoff_2025["score_gap"].eq(0),
    }
    for sample, mask in sensitivity_rules.items():
        subset = cutoff_2025[mask]
        if len(subset) < 2:
            continue
        classification = (
            "DESCRITIVO_CONTAMINADO_POR_DESEMPATES"
            if sample == "empate_descritivo_nao_causal"
            else "SENSIBILIDADE"
        )
        for outcome in ["homologated_same_cell", "active_same_cell"]:
            sensitivity_rows.append(
                paired_estimate(
                    subset,
                    cycle_call="2025_C1_CH1_E_CH2",
                    sample=sample,
                    outcome=outcome,
                    classification=classification,
                )
            )
    sensitivity = pd.DataFrame(sensitivity_rows)

    leave_rows: list[dict[str, Any]] = []
    for dimension in ["course_code", "uf"]:
        for outcome in ["homologated_same_cell", "active_same_cell"]:
            leave_rows.extend(
                leave_one_out(
                    primary_2025,
                    group_column=dimension,
                    outcome=outcome,
                )
            )
    leave_table = pd.DataFrame(leave_rows)

    repeated_cells = int(primary_2025["cell_internal"].duplicated(keep=False).sum())
    repeated_names = int(
        pd.concat(
            [
                primary_2025["high_name_internal"],
                primary_2025["low_name_internal"],
            ],
            ignore_index=True,
        ).duplicated(keep=False).sum()
    )

    main_hom = estimates.query(
        "ciclo_chamada == '2025_C1_CH1_E_CH2' and "
        "amostra == 'gap_1_ac' and desfecho == 'homologacao_mesma_celula'"
    ).iloc[0]
    main_active = estimates.query(
        "ciclo_chamada == '2025_C1_CH1_E_CH2' and "
        "amostra == 'gap_1_ac' and desfecho == 'ativo_mesma_celula_snapshot'"
    ).iloc[0]
    placebo_hom = placebos.query(
        "amostra == 'placebo_abaixo_gap_1_ac' and "
        "desfecho == 'homologacao_mesma_celula'"
    ).iloc[0]
    placebo_active = placebos.query(
        "amostra == 'placebo_abaixo_gap_1_ac' and "
        "desfecho == 'ativo_mesma_celula_snapshot'"
    ).iloc[0]
    replication_active = estimates.query(
        "ciclo_chamada == '2026_C2_CH2' and "
        "desfecho == 'ativo_mesma_celula_snapshot'"
    ).iloc[0]

    protocol = {
        "protocolo": "A8_PROTOCOLO_RETROSPECTIVO_CUTOFF_ESCORE_ESTRITO",
        "data_congelamento": "2026-09-04",
        "pre_registro": False,
        "outcomes_previamente_observados": True,
        "nota": (
            "O A7 e os calculos de viabilidade precederam este congelamento. "
            "O documento organiza uma analise retrospectiva e nao deve ser descrito "
            "como pre-registrado ou confirmatorio prospectivo."
        ),
        "pergunta": (
            "Qual e o efeito local de ganhar a vaga de primeira opcao sobre "
            "homologacao e presenca posterior no mesmo curso-CNES?"
        ),
        "populacao_principal": (
            "2025, primeira opcao, ampla concorrencia, corte sharp no rank, "
            "ultimo selecionado e primeiro nao selecionado separados por um ponto."
        ),
        "tratamento": "ganhar a alocacao da primeira opcao",
        "running_variable": "pontuacao publicada centrada no cutoff especifico da celula",
        "estimando": "ITT local entre candidatos marginais da mesma celula curso-CNES",
        "outcome_de_processo": "homologacao no mesmo curso-CNES",
        "outcome_substantivo_principal": "ativo no mesmo curso-CNES em 2026-08-12",
        "sensibilidades": [
            "homologacao ou atividade em qualquer local",
            "gap positivo de ate dois pontos",
            "qualquer gap positivo",
            "primeira e segunda chamadas separadas",
            "leave-one-course e leave-one-UF",
            "replicacao no ciclo 2 de 2026",
        ],
        "placebos": [
            "duas posicoes imediatamente abaixo do cutoff",
            "duas posicoes imediatamente acima do cutoff quando houver suporte",
        ],
        "inferencia": (
            "diferenca pareada, IC t convencional identificado como tal e teste "
            "exato bicaudal condicionado aos pares discordantes"
        ),
        "hipotese_identificadora": (
            "dentro da janela de um ponto, os resultados potenciais seriam "
            "comparaveis na ausencia da alocacao; o score nao gera outra "
            "descontinuidade no cutoff especifico da vaga"
        ),
        "linguagem_proibida": [
            "efeito da bolsa ou do IVS",
            "efeito total do PMM-E",
            "efeito sobre candidaturas ex ante",
            "retencao individual continua ou duracao ate saida",
        ],
        "fontes": {
            "edital_2025": OFFICIAL_NOTICE_2025,
            "pagina_publicacoes_2026": OFFICIAL_PAGE_2026,
        },
        "hashes_entradas": {str(path.relative_to(ROOT)): sha256(path) for path in inputs},
        "privacidade": (
            "Nomes e CPFs sao processados somente em memoria; nenhum identificador "
            "individual ou par reidentificavel e persistido."
        ),
    }

    loo_summary: dict[str, dict[str, float]] = {}
    for outcome in ["homologacao_mesma_celula", "ativo_mesma_celula_snapshot"]:
        subset = leave_table[leave_table["desfecho"].eq(outcome)]
        loo_summary[outcome] = {
            "min": float(subset["diferenca"].min()),
            "max": float(subset["diferenca"].max()),
            "n_exclusoes": int(len(subset)),
        }

    summary = {
        "status": "EFEITO_LOCAL_CAUSAL_CONDICIONAL",
        "grau_de_rigor": "MODERADO",
        "por_que_nao_alto": [
            "score discreto e apenas um mass point de cada lado",
            "hipotese de comparabilidade local nao e integralmente testavel",
            "protocolo retrospectivo apos o A7 ter aberto os outcomes",
            "ligacao entre publicacoes usa nome normalizado e curso-CNES",
            "homologacao e um outcome administrativo proximo da propria alocacao",
        ],
        "estimando": (
            "ITT local de ganhar a primeira opcao entre candidatos de ampla "
            "concorrencia separados por um ponto no mesmo curso-CNES"
        ),
        "resultado_principal_2025": {
            "n_pares": int(main_hom["n_pares"]),
            "homologacao_mesma_celula": {
                "selecionado": float(main_hom["media_acima"]),
                "nao_selecionado": float(main_hom["media_abaixo"]),
                "diferenca": float(main_hom["diferenca"]),
                "ic95_convencional": [
                    float(main_hom["ic95_convencional_inferior"]),
                    float(main_hom["ic95_convencional_superior"]),
                ],
                "p_exato": float(main_hom["p_exato_pareado_bicaudal"]),
            },
            "ativo_mesma_celula_snapshot": {
                "selecionado": float(main_active["media_acima"]),
                "nao_selecionado": float(main_active["media_abaixo"]),
                "diferenca": float(main_active["diferenca"]),
                "ic95_convencional": [
                    float(main_active["ic95_convencional_inferior"]),
                    float(main_active["ic95_convencional_superior"]),
                ],
                "p_exato": float(main_active["p_exato_pareado_bicaudal"]),
            },
        },
        "placebo_imediatamente_abaixo_2025": {
            "n_pares": int(placebo_hom["n_pares"]),
            "homologacao_diferenca": float(placebo_hom["diferenca"]),
            "ativo_diferenca": float(placebo_active["diferenca"]),
        },
        "replicacao_2026": {
            "n_pares": int(replication_active["n_pares"]),
            "ativo_mesma_celula_diferenca": float(replication_active["diferenca"]),
            "ic95_convencional": [
                float(replication_active["ic95_convencional_inferior"]),
                float(replication_active["ic95_convencional_superior"]),
            ],
            "p_exato": float(replication_active["p_exato_pareado_bicaudal"]),
            "interpretacao": "direcao consistente, mas poucos discordantes e inferencia imprecisa",
        },
        "dependencia": {
            "linhas_em_celulas_repetidas_entre_chamadas_2025": repeated_cells,
            "nomes_repetidos_nos_pares_primarios_2025": repeated_names,
        },
        "leave_one_out": loo_summary,
        "interpretacao_autorizada": (
            "Sob comparabilidade local, ganhar marginalmente a primeira opcao "
            "aumentou a adesao e a presenca posterior naquele curso-CNES."
        ),
        "interpretacao_proibida": (
            "Os resultados nao identificam o efeito da bolsa, do IVS, do PMM-E "
            "sobre o estoque geral nem a decisao de se candidatar."
        ),
        "privacidade": protocol["privacidade"],
        "arquivos": {
            "protocolo": str(PROTOCOL_JSON.relative_to(ROOT)),
            "suporte": str(SUPPORT_TABLE.relative_to(ROOT)),
            "estimativas": str(ESTIMATES_TABLE.relative_to(ROOT)),
            "placebos": str(PLACEBOS_TABLE.relative_to(ROOT)),
            "sensibilidade": str(SENSITIVITY_TABLE.relative_to(ROOT)),
            "leave_one_out": str(LEAVE_ONE_OUT_TABLE.relative_to(ROOT)),
            "figura": str(EFFECT_FIGURE.relative_to(ROOT)),
            "relatorio": str(REPORT_MD.relative_to(ROOT)),
        },
    }

    report = f"""# A8 - Cutoff de escore e alocacao da primeira opcao

> **Veredito:** o recorte sem empates sustenta uma estimativa causal local sob a
> hipotese explicita de comparabilidade entre candidatos separados por um ponto.
> O grau de rigor e moderado, nao alto, e o protocolo e retrospectivo.

## 1. Pergunta e desenho

A pergunta e: **ganhar marginalmente a vaga de primeira opcao aumenta a adesao
e a presenca posterior do especialista naquele curso-CNES?** O tratamento e a
alocacao da primeira opcao. A running variable e a pontuacao publicada,
centrada no cutoff especifico de cada celula curso-CNES.

A amostra principal usa somente ampla concorrencia, primeira opcao, um corte
sharp no ranking e diferenca exata de um ponto entre o ultimo selecionado e o
primeiro nao selecionado. Empates sao excluidos. Assim, os desempates por UF e
idade previstos no edital nao determinam a atribuicao dentro do recorte.

## 2. Resultado principal de 2025

Ha **{int(main_hom['n_pares'])} pares**, sendo {len(primary1)} na primeira
chamada e {len(primary2)} na segunda.

| Desfecho no mesmo curso-CNES | Selecionado | Nao selecionado | Diferenca | IC95% convencional | p exato |
|---|---:|---:|---:|---:|---:|
| Homologacao | {100*main_hom['media_acima']:.1f}% | {100*main_hom['media_abaixo']:.1f}% | **{100*main_hom['diferenca']:.1f} p.p.** | {100*main_hom['ic95_convencional_inferior']:.1f} a {100*main_hom['ic95_convencional_superior']:.1f} | {main_hom['p_exato_pareado_bicaudal']:.6f} |
| Ativo em 12/08/2026 | {100*main_active['media_acima']:.1f}% | {100*main_active['media_abaixo']:.1f}% | **{100*main_active['diferenca']:.1f} p.p.** | {100*main_active['ic95_convencional_inferior']:.1f} a {100*main_active['ic95_convencional_superior']:.1f} | {main_active['p_exato_pareado_bicaudal']:.4f} |

O primeiro resultado mede conversao administrativa imediata e esta proximo da
propria elegibilidade criada pela alocacao. O resultado substantivamente mais
informativo e o segundo: presenca em uma data posterior. Ele nao reconstrui
duracao continua nem data de saida.

## 3. Placebos e sensibilidades

O placebo imediatamente abaixo do cutoff contem
**{int(placebo_hom['n_pares'])} pares** de nao selecionados separados por um
ponto. A diferenca foi {100*placebo_hom['diferenca']:.1f} p.p. em homologacao e
{100*placebo_active['diferenca']:.1f} p.p. em presenca ativa. O salto principal
nao se repete onde a alocacao nao muda.

Os resultados com gap de ate dois pontos, qualquer gap positivo, desfechos em
qualquer local e exclusao sucessiva de curso e UF estao nas tabelas de
sensibilidade. Esses exercicios nao redefinem a especificacao principal.

## 4. Replicacao publica de 2026

Na segunda chamada do ciclo 2 de 2026 ha
**{int(replication_active['n_pares'])} pares** no mesmo recorte. A presenca no
mesmo curso-CNES foi {100*replication_active['media_acima']:.1f}% acima e
{100*replication_active['media_abaixo']:.1f}% abaixo do cutoff: diferenca de
**{100*replication_active['diferenca']:.1f} p.p.**. O IC95% convencional vai de
{100*replication_active['ic95_convencional_inferior']:.1f} a
{100*replication_active['ic95_convencional_superior']:.1f} p.p., mas o teste
exato e impreciso (`p={replication_active['p_exato_pareado_bicaudal']:.3f}`),
pois ha apenas quatro pares discordantes.

## 5. O que sustenta a causalidade condicional

O contraste mantem curso, estabelecimento, chamada, primeira preferencia e
modalidade de concorrencia constantes. O cutoff e especifico da vaga e os
candidatos nao observam antecipadamente a pontuacao dos concorrentes. A
identificacao ainda exige que um ponto no barema nao gere, por outro mecanismo,
uma mudanca descontínua na propensao de homologar ou permanecer.

O score e discreto e ha apenas um mass point de cada lado. Por isso, o trabalho
nao usa erros agrupados por valor do score como solucao para especificacao
incorreta. A inferencia principal combina diferencas pareadas e teste exato; os
ICs t sao rotulados como convencionais.

## 6. Grau de rigor e linguagem autorizada

O grau de rigor e **moderado**. A amostra e pequena, a hipotese de
comparabilidade local nao e integralmente testavel e o desenho foi refinado
depois que o A7 abriu os outcomes. O protocolo A8 registra isso e nunca deve ser
apresentado como pre-registro prospectivo.

Linguagem autorizada:

> Sob a hipotese de comparabilidade local, ganhar marginalmente a primeira
> opcao aumentou a homologacao e a presenca posterior naquele curso-CNES.

O desenho **nao identifica** o efeito da bolsa, do IVS, do programa sobre o
estoque geral, da vulnerabilidade ou sobre a decisao de se candidatar.

## 7. Papel dos resultados anteriores

A4 permanece como motivacao descritiva sobre desigualdade territorial. A5
permanece no apendice como associacao longitudinal no CNES. A RDD da bolsa pelo
IVS publico, a DDD imediata versus reserva e a DiD sem variacao de faixa em
unidades repetidas nao integram o nucleo causal.

Fontes oficiais: [Edital de 2025]({OFFICIAL_NOTICE_2025}) e
[publicacoes do ciclo 2 de 2026]({OFFICIAL_PAGE_2026}).
"""

    atomic_text(PROTOCOL_JSON, json.dumps(protocol, ensure_ascii=False, indent=2))
    atomic_csv(SUPPORT_TABLE, support)
    atomic_csv(ESTIMATES_TABLE, estimates)
    atomic_csv(PLACEBOS_TABLE, placebos)
    atomic_csv(SENSITIVITY_TABLE, sensitivity)
    atomic_csv(LEAVE_ONE_OUT_TABLE, leave_table)
    atomic_text(SUMMARY_JSON, json.dumps(summary, ensure_ascii=False, indent=2))
    atomic_text(REPORT_MD, report)
    render_figure(estimates, placebos)
    print(
        "[OK] A8: cutoff de escore estrito estimado; "
        f"{len(primary_2025)} pares em 2025 e {len(replication)} na replicacao de 2026."
    )


if __name__ == "__main__":
    main()
