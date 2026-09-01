"""Reconcilia o funil administrativo público do ciclo 1 do PMM-E.

O script preserva as versões publicadas, agrega eventos em células CNES-curso
e decide se os dados sustentam denominador por vaga, por célula ou somente
contagens. Nenhum nome ou CPF é exportado.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
RAW_VAGAS = ROOT / "data" / "raw" / "aquisicao" / "vagas"
RAW_PMME = ROOT / "data" / "raw" / "pmm_e"

OFFER_C1 = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
ALLOC_C1 = RAW_VAGAS / "2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx"
ALLOC_C1_PRIOR = RAW_VAGAS / "2025_ciclo1_chamada1_alocacao_retificada.xlsx"
REALLOC_C1 = RAW_VAGAS / "2025_ciclo1_chamada1_realocacao_retificado.xlsx"
HOMOLOG_C1 = RAW_PMME / "2025_ciclo1_chamada1_homologados.xlsx"
FRAME_C2 = RAW_PMME / "2025_ciclo1_chamada2_vagas_e_alocados.xlsx"
CLASS_C2 = RAW_PMME / "2025_ciclo1_chamada2_classificacao_final.xlsx"
HOMOLOG_C2 = RAW_PMME / "2025_ciclo1_chamada2_homologados.xlsx"

OUT_DIR = ROOT / "output" / "tema_trabalho"
OUT_MATRIX = OUT_DIR / "matriz_funil_ciclo1.parquet"
OUT_GATE = OUT_DIR / "portao_denominador.json"

KEYS = ["co_cnes_7d", "cod_curso"]


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()


def normalize_id(value: object, width: int) -> str:
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits[:width].zfill(width) if digits else ""


def course_id(value: object) -> int | None:
    if pd.isna(value):
        return None
    match = re.match(r"^\s*(\d{1,2})", str(value))
    if not match:
        return None
    result = int(match.group(1))
    return result if 1 <= result <= 16 else None


def cpf_signature_34(value: object) -> str:
    """Primeiros três e últimos quatro dígitos visíveis, apenas entre homologações."""
    digits = re.sub(r"\D", "", "" if pd.isna(value) else str(value))
    return digits[:3] + digits[-4:] if len(digits) >= 7 else ""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def person_events(
    frame: pd.DataFrame,
    *,
    name_position: int,
    course_position: int,
    cnes_position: int,
    ibge_position: int | None = None,
    cpf_position: int | None = None,
) -> pd.DataFrame:
    result = frame.copy()
    result["_person_name"] = result.iloc[:, name_position].map(normalize_text)
    result["co_cnes_7d"] = result.iloc[:, cnes_position].map(
        lambda value: normalize_id(value, 7)
    )
    result["cod_curso"] = result.iloc[:, course_position].map(course_id)
    result["co_ibge_6d"] = (
        result.iloc[:, ibge_position].map(lambda value: normalize_id(value, 6))
        if ibge_position is not None
        else ""
    )
    result["_cpf_signature_34"] = (
        result.iloc[:, cpf_position].map(cpf_signature_34)
        if cpf_position is not None
        else ""
    )
    valid = (
        (result["_person_name"] != "")
        & (result["co_cnes_7d"] != "")
        & result["cod_curso"].notna()
    )
    result = result.loc[valid].copy()
    result["cod_curso"] = result["cod_curso"].astype(int)
    return result


def aggregate_event(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    return (
        frame.groupby(KEYS, as_index=False)
        .size()
        .rename(columns={"size": column})
    )


def first_nonempty(series: pd.Series) -> str:
    values = [str(value) for value in series if pd.notna(value) and str(value) != ""]
    return values[0] if values else ""


def compare_allocation_versions(
    prior: pd.DataFrame, canonical: pd.DataFrame
) -> dict[str, int]:
    """Compara versões sem somá-las e sem exportar identificadores pessoais."""
    common_columns = min(prior.shape[1], canonical.shape[1], 16)

    def keyed(frame: pd.DataFrame) -> dict[tuple[str, ...], tuple[str, ...]]:
        records: dict[tuple[str, ...], tuple[str, ...]] = {}
        for values in frame.iloc[:, :common_columns].itertuples(index=False, name=None):
            normalized = tuple(normalize_text(value) for value in values)
            key = (
                normalized[6],   # CPF mascarado
                normalized[7],   # nome
                normalized[4],   # CNES
                normalized[0],   # curso
                normalized[11],  # opção
            )
            records[key] = normalized
        return records

    prior_records = keyed(prior)
    canonical_records = keyed(canonical)
    common_keys = set(prior_records) & set(canonical_records)
    extra_columns_nonempty = 0
    if canonical.shape[1] > common_columns:
        extra_columns_nonempty = int(
            canonical.iloc[:, common_columns:]
            .map(normalize_text)
            .ne("")
            .any(axis=1)
            .sum()
        )
    return {
        "registros_versao_anterior": int(len(prior)),
        "registros_versao_canonica": int(len(canonical)),
        "chaves_adicionadas": int(len(set(canonical_records) - set(prior_records))),
        "chaves_removidas": int(len(set(prior_records) - set(canonical_records))),
        "registros_com_conteudo_alterado": int(
            sum(prior_records[key] != canonical_records[key] for key in common_keys)
        ),
        "registros_com_marcacao_em_coluna_adicional": extra_columns_nonempty,
    }


def build_frame(
    base: pd.DataFrame,
    events: list[pd.DataFrame],
    *,
    chamada: int,
    versao: str,
    frame_flag: str,
) -> pd.DataFrame:
    event_keys = pd.concat([event[KEYS] for event in events], ignore_index=True)
    all_keys = pd.concat([base[KEYS], event_keys], ignore_index=True).drop_duplicates()
    result = all_keys.merge(base, on=KEYS, how="left", validate="one_to_one")
    for event in events:
        value_columns = [column for column in event.columns if column not in KEYS]
        result = result.merge(event, on=KEYS, how="left", validate="one_to_one")
        result[value_columns] = result[value_columns].fillna(0).astype(int)
    result[frame_flag] = result[frame_flag].fillna(False).astype(bool)
    result["ciclo"] = 1
    result["chamada"] = chamada
    result["versao_quadro"] = versao
    result["registro_fora_do_quadro_publicado"] = ~result[frame_flag]
    return result


def main() -> None:
    inputs = [
        OFFER_C1,
        ALLOC_C1,
        ALLOC_C1_PRIOR,
        REALLOC_C1,
        HOMOLOG_C1,
        FRAME_C2,
        CLASS_C2,
        HOMOLOG_C2,
    ]
    for path in inputs:
        if not path.exists():
            raise FileNotFoundError(path)

    # Chamada 1: a versão sub judice é canônica; a retificada anterior é
    # preservada apenas como versão de comparação e nunca somada.
    offer_c1 = pd.read_parquet(OFFER_C1).copy()
    offer_c1["co_cnes_7d"] = offer_c1["co_cnes_7d"].map(
        lambda value: normalize_id(value, 7)
    )
    offer_c1["co_ibge_6d"] = offer_c1["co_ibge_6d"].map(
        lambda value: normalize_id(value, 6)
    )
    offer_c1 = offer_c1.rename(
        columns={
            "qt_vagas_imediatas": "vagas_imediatas_publicadas",
            "qt_vagas_reserva": "vagas_reserva_publicadas",
        }
    )
    offer_c1["in_quadro_ch1_original"] = True
    offer_c1 = offer_c1[
        KEYS
        + [
            "co_ibge_6d",
            "sg_uf",
            "no_municipio",
            "no_estabelecimento",
            "faixa_atracao_anunciada",
            "modalidade_original",
            "vagas_imediatas_publicadas",
            "vagas_reserva_publicadas",
            "in_quadro_ch1_original",
        ]
    ].copy()

    alloc_raw = pd.read_excel(ALLOC_C1, dtype=object)
    alloc_prior_raw = pd.read_excel(ALLOC_C1_PRIOR, dtype=object)
    allocation_version_check = compare_allocation_versions(alloc_prior_raw, alloc_raw)
    alloc_all = person_events(
        alloc_raw,
        name_position=7,
        course_position=0,
        cnes_position=4,
        ibge_position=2,
        cpf_position=6,
    )
    alloc_status = alloc_raw.iloc[:, 10].fillna("").map(normalize_text)
    confirmed = alloc_all.loc[
        alloc_status.loc[alloc_all.index].str.contains(
            "LOCAL DE ATUACAO CONFIRMADO", regex=False
        )
    ].copy()
    disregarded = alloc_all.loc[
        alloc_status.loc[alloc_all.index].str.contains(
            "LOCAL DE ATUACAO DESCONSIDERADO", regex=False
        )
    ].copy()

    realloc = person_events(
        pd.read_excel(REALLOC_C1, dtype=object),
        name_position=7,
        course_position=0,
        cnes_position=4,
        ibge_position=2,
        cpf_position=6,
    )
    homolog_c1 = person_events(
        pd.read_excel(HOMOLOG_C1, dtype=object),
        name_position=7,
        course_position=1,
        cnes_position=5,
        ibge_position=3,
        cpf_position=0,
    )

    c1_events = [
        aggregate_event(confirmed, "n_confirmacoes_ch1"),
        aggregate_event(disregarded, "n_locais_desconsiderados_ch1"),
        aggregate_event(realloc, "n_propostas_realocacao_ch1"),
        aggregate_event(homolog_c1, "n_homologacoes_ch1"),
    ]
    matrix_c1 = build_frame(
        offer_c1,
        c1_events,
        chamada=1,
        versao="oferta_original_2025-07-24",
        frame_flag="in_quadro_ch1_original",
    )

    # Chamada 2: a publicação contém um quadro de cadastro de reserva, mas
    # não contém quantidade de vagas imediatas por célula.
    reserve_c2_raw = pd.read_excel(FRAME_C2, sheet_name=1, header=1, dtype=object)
    reserve_c2 = pd.DataFrame(
        {
            "co_cnes_7d": reserve_c2_raw.iloc[:, 5].map(
                lambda value: normalize_id(value, 7)
            ),
            "cod_curso": reserve_c2_raw.iloc[:, 0].map(course_id),
            "co_ibge_6d": reserve_c2_raw.iloc[:, 3].map(
                lambda value: normalize_id(value, 6)
            ),
            "sg_uf": reserve_c2_raw.iloc[:, 2].map(normalize_text),
            "no_municipio": reserve_c2_raw.iloc[:, 4].map(normalize_text),
            "no_estabelecimento": reserve_c2_raw.iloc[:, 6].map(normalize_text),
            "faixa_atracao_anunciada": reserve_c2_raw.iloc[:, 8].map(normalize_text),
            "vagas_reserva_publicadas": pd.to_numeric(
                reserve_c2_raw.iloc[:, 9], errors="coerce"
            ).fillna(0).astype(int),
        }
    )
    reserve_c2 = reserve_c2[
        (reserve_c2["co_cnes_7d"] != "") & reserve_c2["cod_curso"].notna()
    ].copy()
    reserve_c2["cod_curso"] = reserve_c2["cod_curso"].astype(int)
    reserve_c2["vagas_imediatas_publicadas"] = pd.NA
    reserve_c2["modalidade_original"] = "CADASTRO_RESERVA_CH2"
    reserve_c2["in_quadro_reserva_ch2"] = True
    if reserve_c2.duplicated(KEYS).any():
        raise AssertionError("Quadro de reserva da chamada 2 possui chave duplicada")

    preliminary_raw = pd.read_excel(FRAME_C2, sheet_name=0, dtype=object)
    preliminary = person_events(
        preliminary_raw,
        name_position=7,
        course_position=0,
        cnes_position=4,
        ibge_position=2,
        cpf_position=6,
    )
    preliminary_status = preliminary_raw.iloc[:, 9].fillna("").map(normalize_text)
    preliminary_classified = preliminary.loc[
        preliminary_status.loc[preliminary.index].str.startswith("CLASSIFICADO")
    ].copy()

    classification_raw = pd.read_excel(CLASS_C2, sheet_name=0, header=1, dtype=object)
    classification = person_events(
        classification_raw,
        name_position=7,
        course_position=0,
        cnes_position=3,
        cpf_position=6,
    )
    final_status = classification_raw.iloc[:, 9].fillna("").map(normalize_text)
    final_allocated = classification.loc[
        final_status.loc[classification.index].str.startswith("ALOCADO")
    ].copy()

    homolog_c2 = person_events(
        pd.read_excel(HOMOLOG_C2, dtype=object),
        name_position=1,
        course_position=7,
        cnes_position=6,
        cpf_position=0,
    )

    # A segunda lista não é perfeitamente cumulativa: 299 pessoas reaparecem,
    # 17 homologados da lista anterior não reaparecem e 282 são novos registros.
    old_names = set(homolog_c1["_person_name"])
    old_signatures = set(homolog_c1["_cpf_signature_34"])
    repeated_c1 = homolog_c2["_person_name"].isin(old_names) | homolog_c2[
        "_cpf_signature_34"
    ].isin(old_signatures)
    homolog_c2_new = homolog_c2.loc[~repeated_c1].copy()

    c2_events = [
        aggregate_event(preliminary_classified, "n_classificados_preliminares_ch2"),
        aggregate_event(final_allocated, "n_alocados_finais_ch2"),
        aggregate_event(homolog_c2, "n_homologacoes_lista_ch2"),
        aggregate_event(homolog_c2_new, "n_homologacoes_novas_ch2"),
    ]
    matrix_c2 = build_frame(
        reserve_c2,
        c2_events,
        chamada=2,
        versao="cadastro_reserva_oficial_2025-09-29",
        frame_flag="in_quadro_reserva_ch2",
    )

    matrix = pd.concat([matrix_c1, matrix_c2], ignore_index=True, sort=False)
    for column in [
        "vagas_imediatas_publicadas",
        "vagas_reserva_publicadas",
        "n_confirmacoes_ch1",
        "n_locais_desconsiderados_ch1",
        "n_propostas_realocacao_ch1",
        "n_homologacoes_ch1",
        "n_classificados_preliminares_ch2",
        "n_alocados_finais_ch2",
        "n_homologacoes_lista_ch2",
        "n_homologacoes_novas_ch2",
    ]:
        if column not in matrix:
            matrix[column] = 0
    count_columns = [column for column in matrix if column.startswith("n_")]
    matrix[count_columns] = matrix[count_columns].fillna(0).astype(int)
    matrix["outcome_alguma_confirmacao_ou_homologacao"] = (
        matrix[["n_confirmacoes_ch1", "n_homologacoes_ch1", "n_homologacoes_novas_ch2"]]
        .sum(axis=1)
        .gt(0)
        .astype(int)
    )
    matrix = matrix.sort_values(
        ["ciclo", "chamada", "versao_quadro", "co_cnes_7d", "cod_curso"]
    ).reset_index(drop=True)

    if matrix.duplicated(
        ["ciclo", "chamada", "versao_quadro", "co_cnes_7d", "cod_curso"]
    ).any():
        raise AssertionError("Matriz final possui chave analítica duplicada")

    # Trilha individual é usada somente para contagens de reconciliação.
    confirmed_person_cell = set(zip(confirmed["_person_name"], confirmed["co_cnes_7d"], confirmed["cod_curso"]))
    realloc_person_cell = set(zip(realloc["_person_name"], realloc["co_cnes_7d"], realloc["cod_curso"]))
    confirmed_people = set(confirmed["_person_name"])
    realloc_people = set(realloc["_person_name"])
    h1_trace = {
        "confirmacao_exata": 0,
        "realocacao_exata": 0,
        "pessoa_confirmada_local_diferente": 0,
        "pessoa_realocada_local_diferente": 0,
        "sem_evento_anterior_localizado": 0,
    }
    for person, cnes, course in homolog_c1[
        ["_person_name", "co_cnes_7d", "cod_curso"]
    ].itertuples(index=False, name=None):
        person_cell = (person, cnes, course)
        if person_cell in confirmed_person_cell:
            h1_trace["confirmacao_exata"] += 1
        elif person_cell in realloc_person_cell:
            h1_trace["realocacao_exata"] += 1
        elif person in confirmed_people:
            h1_trace["pessoa_confirmada_local_diferente"] += 1
        elif person in realloc_people:
            h1_trace["pessoa_realocada_local_diferente"] += 1
        else:
            h1_trace["sem_evento_anterior_localizado"] += 1

    final_allocated_people = set(final_allocated["_person_name"])
    preliminary_people = set(preliminary_classified["_person_name"])
    c2_trace = {
        "reaparece_da_lista_ch1": int(repeated_c1.sum()),
        "novo_com_alocacao_final": 0,
        "novo_apenas_em_classificacao_preliminar": 0,
        "novo_sem_evento_anterior_localizado": 0,
    }
    for person in homolog_c2_new["_person_name"]:
        if person in final_allocated_people:
            c2_trace["novo_com_alocacao_final"] += 1
        elif person in preliminary_people:
            c2_trace["novo_apenas_em_classificacao_preliminar"] += 1
        else:
            c2_trace["novo_sem_evento_anterior_localizado"] += 1

    original_keys = set(map(tuple, offer_c1[KEYS].to_numpy()))
    reserve_keys = set(map(tuple, reserve_c2[KEYS].to_numpy()))
    h1_keys = list(map(tuple, homolog_c1[KEYS].to_numpy()))
    h2_new_keys = list(map(tuple, homolog_c2_new[KEYS].to_numpy()))

    c1_in_frame = matrix_c1[matrix_c1["in_quadro_ch1_original"]].copy()
    immediate = pd.to_numeric(
        c1_in_frame["vagas_imediatas_publicadas"], errors="coerce"
    ).fillna(0)
    total_capacity = immediate + pd.to_numeric(
        c1_in_frame["vagas_reserva_publicadas"], errors="coerce"
    ).fillna(0)
    over_immediate = (
        (c1_in_frame["n_confirmacoes_ch1"] > immediate) & (immediate > 0)
    )
    over_total = c1_in_frame["n_confirmacoes_ch1"] > total_capacity

    # Condições explícitas do portão.
    vacancy_id_available = False
    immediate_capacity_all_calls = False
    no_capacity_violations = not bool(over_total.any())
    event_keys_valid = bool(
        matrix["co_cnes_7d"].ne("").all() & matrix["cod_curso"].between(1, 16).all()
    )
    analytical_key_unique = not matrix.duplicated(
        ["ciclo", "chamada", "versao_quadro", "co_cnes_7d", "cod_curso"]
    ).any()
    cell_gate = event_keys_valid and analytical_key_unique
    vacancy_gate = (
        vacancy_id_available
        and immediate_capacity_all_calls
        and no_capacity_violations
        and cell_gate
    )
    gate = "APROVADO_VAGA" if vacancy_gate else "APROVADO_CELULA" if cell_gate else "REPROVADO"

    gate_report: dict[str, Any] = {
        "protocolo": "A1_PORTAO_DENOMINADOR_ATRACAO",
        "data_referencia": "2026-09-01",
        "efeitos_estimados": False,
        "portao": gate,
        "decisao": {
            "denominador_por_vaga": False,
            "denominador_por_celula": True,
            "outcome_primario_liberado": "alguma confirmação ou homologação observada na célula CNES-curso",
            "outcomes_bloqueados": [
                "taxa de preenchimento por vaga",
                "candidaturas por vaga",
                "retenção individual do bolsista",
            ],
            "unidade_recomendada": "célula CNES-curso dentro de cada chamada e versão publicada",
        },
        "criterios": {
            "id_vaga_fisica_persistente_disponivel": vacancy_id_available,
            "capacidade_imediata_numerica_em_todas_as_chamadas": immediate_capacity_all_calls,
            "nenhuma_violacao_da_capacidade_total_publicada_ch1": no_capacity_violations,
            "chaves_de_evento_validas": event_keys_valid,
            "chave_analitica_unica": analytical_key_unique,
        },
        "fontes": {
            path.relative_to(ROOT).as_posix(): {"sha256": sha256(path)} for path in inputs
        },
        "chamada_1": {
            "quadro_original": {
                "celulas": int(len(offer_c1)),
                "vagas_imediatas": int(offer_c1["vagas_imediatas_publicadas"].sum()),
                "vagas_reserva": int(offer_c1["vagas_reserva_publicadas"].sum()),
            },
            "versoes_alocacao": {
                "canonica": ALLOC_C1.name,
                "comparacao_nao_somada": ALLOC_C1_PRIOR.name,
                "comparacao": allocation_version_check,
            },
            "confirmacoes": int(len(confirmed)),
            "locais_desconsiderados": int(len(disregarded)),
            "propostas_realocacao": int(len(realloc)),
            "homologacoes": int(len(homolog_c1)),
            "homologacoes_em_celula_do_quadro_original": int(
                sum(key in original_keys for key in h1_keys)
            ),
            "homologacoes_fora_do_quadro_original": int(
                sum(key not in original_keys for key in h1_keys)
            ),
            "celulas_homologacao_fora_do_quadro_original": int(
                len({key for key in h1_keys if key not in original_keys})
            ),
            "trilha_homologacao": h1_trace,
            "celulas_confirmacao_acima_vagas_imediatas": int(over_immediate.sum()),
            "celulas_confirmacao_acima_capacidade_total_publicada": int(over_total.sum()),
            "confirmacoes_excedentes_capacidade_total_publicada": int(
                (c1_in_frame.loc[over_total, "n_confirmacoes_ch1"] - total_capacity[over_total]).sum()
            ),
        },
        "chamada_2": {
            "quadro_cadastro_reserva": {
                "celulas": int(len(reserve_c2)),
                "vagas_reserva_publicadas": int(reserve_c2["vagas_reserva_publicadas"].sum()),
                "vagas_imediatas_numericas_publicadas": False,
            },
            "publicacao_preliminar": {
                "registros": int(len(preliminary)),
                "pessoas_distintas_por_nome": int(preliminary["_person_name"].nunique()),
                "classificados": int(len(preliminary_classified)),
                "nota": "o nome da aba não transforma os 98 registros em 98 alocados",
            },
            "classificacao_final": {
                "registros": int(len(classification)),
                "alocados": int(len(final_allocated)),
            },
            "segunda_lista_homologados": {
                "registros": int(len(homolog_c2)),
                "reaparecem_da_primeira_lista": int(repeated_c1.sum()),
                "novos_na_segunda_lista": int(len(homolog_c2_new)),
                "homologados_ch1_ausentes_na_segunda_lista": int(
                    len(homolog_c1) - repeated_c1.sum()
                ),
                "total_distinto_observado_nas_duas_listas": int(
                    len(homolog_c1) + len(homolog_c2_new)
                ),
                "novos_em_celula_do_quadro_reserva_ch2": int(
                    sum(key in reserve_keys for key in h2_new_keys)
                ),
                "novos_fora_do_quadro_reserva_ch2": int(
                    sum(key not in reserve_keys for key in h2_new_keys)
                ),
                "trilha_novos": c2_trace,
                "nota": "a lista de 581 não é soma simples: há entradas novas e ausências relativas à lista anterior",
            },
        },
        "matriz": {
            "linhas": int(len(matrix)),
            "linhas_chamada_1": int((matrix["chamada"] == 1).sum()),
            "linhas_chamada_2": int((matrix["chamada"] == 2).sum()),
            "registros_fora_do_quadro_publicado": int(
                matrix["registro_fora_do_quadro_publicado"].sum()
            ),
            "contém_dados_pessoais": False,
            "caminho": OUT_MATRIX.relative_to(ROOT).as_posix(),
        },
        "implicacao_econometrica": (
            "A população pode ser congelada por célula CNES-curso e versão. "
            "As quantidades publicadas não identificam vagas físicas persistentes nem "
            "fornecem capacidade imediata comparável nas duas chamadas; por isso, razões "
            "com número de vagas no denominador permanecem proibidas."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    matrix_tmp = OUT_MATRIX.with_suffix(".parquet.tmp")
    matrix.to_parquet(matrix_tmp, index=False)
    matrix_tmp.replace(OUT_MATRIX)
    gate_tmp = OUT_GATE.with_suffix(".json.tmp")
    gate_tmp.write_text(
        json.dumps(gate_report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    gate_tmp.replace(OUT_GATE)

    print(
        f"[OK] A1 concluído: {gate}. "
        f"Matriz com {len(matrix):,} linhas; nenhum dado pessoal exportado."
    )


if __name__ == "__main__":
    main()
