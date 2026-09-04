"""Faz triagem estrutural de eventual resposta administrativa do PMM-E.

O módulo nunca altera os bytes recebidos e nunca persiste linhas dos arquivos.
Ele registra apenas nomes, tamanhos, hashes, dimensões, colunas e violações de
integridade. Na ausência de resposta, produz o estado AGUARDANDO_RECEBIMENTO;
ausência jamais é convertida em zero.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "raw" / "administrativo_rdd_bolsa"
DEFAULT_OUTPUT = ROOT / "output" / "rdd_bolsa" / "triagem_resposta_administrativa.json"

TABLES: dict[str, dict[str, Any]] = {
    "vagas_mestre.csv": {
        "required": {
            "id_vaga_pseudo",
            "ciclo",
            "chamada_origem",
            "cnes",
            "ibge_municipio",
            "curso",
            "modalidade_inicial",
            "data_criacao",
        },
        "key": ("id_vaga_pseudo",),
    },
    "vagas_versoes.csv": {
        "required": {
            "id_vaga_pseudo",
            "id_versao",
            "versao_vigencia_inicio",
            "versao_vigencia_fim",
            "ciclo",
            "chamada",
            "cnes",
            "ibge_municipio",
            "curso",
            "modalidade",
            "status_vaga",
            "fonte_ato",
        },
        "key": ("id_vaga_pseudo", "id_versao"),
    },
    "regra_ivs_vaga.csv": {
        "required": {
            "id_vaga_pseudo",
            "vigencia_inicio",
            "vigencia_fim",
            "escore_ivs_aplicado",
            "vintagem",
            "precisao",
            "regra_arredondamento",
            "cutoff",
            "categoria",
            "faixa",
            "valor_anunciado",
            "excecao_motivo",
            "fonte_regra",
        },
        "key": ("id_vaga_pseudo", "vigencia_inicio"),
    },
    "inscricoes_universo.csv": {
        "required": {
            "id_inscricao_pseudo",
            "id_profissional_pseudo",
            "ciclo",
            "chamada",
            "timestamp_submissao",
            "status_validacao",
            "quantidade_opcoes",
            "versao_registro",
        },
        "key": ("id_inscricao_pseudo",),
    },
    "inscricoes_opcoes.csv": {
        "required": {
            "id_inscricao_pseudo",
            "ordem_opcao",
            "id_vaga_pseudo",
            "status_opcao",
        },
        "key": ("id_inscricao_pseudo", "ordem_opcao"),
    },
    "eventos_longos.csv": {
        "required": {
            "id_evento",
            "id_vaga_pseudo",
            "tipo_evento",
            "timestamp",
            "estado_novo",
            "vigencia_inicio",
            "registrado_em",
            "versao_evento",
            "evento_anulado",
        },
        "key": ("id_evento",),
    },
    "cutoff_candidatos.csv": {
        "required": {
            "id_inscricao_pseudo",
            "id_profissional_pseudo",
            "id_vaga_pseudo",
            "ciclo",
            "chamada",
            "ordem_opcao",
            "modalidade",
            "barema_final",
            "prioridade_mesma_uf",
            "distancia_etaria_cutoff_dias",
            "classificacao_final",
            "quantidade_vagas_bloco",
            "selecionado_primeira_opcao",
            "status_recurso",
            "versao_processamento",
        },
        "key": (
            "id_inscricao_pseudo",
            "id_vaga_pseudo",
            "ordem_opcao",
            "versao_processamento",
        ),
    },
    "cutoff_eventos.csv": {
        "required": {
            "id_profissional_pseudo",
            "id_vaga_pseudo",
            "confirmou",
            "homologado",
            "iniciou",
            "ativo_90d",
            "ativo_180d",
        },
        "key": ("id_profissional_pseudo", "id_vaga_pseudo"),
    },
}

FORBIDDEN_IDENTIFIERS = {
    "nome",
    "nome_completo",
    "cpf",
    "cns",
    "crm",
    "data_nascimento",
    "dt_nascimento",
    "endereco",
    "logradouro",
    "conta_bancaria",
    "agencia_bancaria",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def _nonempty_key(frame: pd.DataFrame, key: tuple[str, ...]) -> pd.Series:
    return frame[list(key)].apply(
        lambda column: column.astype("string").str.strip().notna()
        & column.astype("string").str.strip().ne("")
    ).all(axis=1)


def inspect_table(path: Path, specification: dict[str, Any]) -> tuple[dict[str, Any], pd.DataFrame]:
    frame = pd.read_csv(path, dtype="string", keep_default_na=False)
    columns = [str(column).strip() for column in frame.columns]
    frame.columns = columns
    required = specification["required"]
    key = specification["key"]
    missing = sorted(required - set(columns))
    forbidden = sorted(FORBIDDEN_IDENTIFIERS & {column.lower() for column in columns})
    key_usable = not (set(key) - set(columns))
    blank_keys = None
    duplicate_keys = None
    if key_usable:
        valid = _nonempty_key(frame, key)
        blank_keys = int((~valid).sum())
        duplicate_keys = int(frame.loc[valid, list(key)].duplicated().sum())
    report = {
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "n_linhas": int(len(frame)),
        "n_colunas": int(len(columns)),
        "colunas": columns,
        "colunas_obrigatorias_ausentes": missing,
        "identificadores_pessoais_nao_solicitados": forbidden,
        "chave": list(key),
        "chaves_vazias": blank_keys,
        "chaves_duplicadas": duplicate_keys,
        "estrutura_aprovada": not missing
        and not forbidden
        and blank_keys == 0
        and duplicate_keys == 0,
    }
    return report, frame


def _foreign_key_errors(frames: dict[str, pd.DataFrame]) -> list[str]:
    errors: list[str] = []
    if "vagas_mestre.csv" in frames:
        valid_vagas = set(frames["vagas_mestre.csv"]["id_vaga_pseudo"])
        for filename in (
            "vagas_versoes.csv",
            "regra_ivs_vaga.csv",
            "inscricoes_opcoes.csv",
            "eventos_longos.csv",
            "cutoff_candidatos.csv",
            "cutoff_eventos.csv",
        ):
            if filename in frames and "id_vaga_pseudo" in frames[filename]:
                unresolved = set(frames[filename]["id_vaga_pseudo"]) - valid_vagas - {""}
                if unresolved:
                    errors.append(
                        f"{filename}: {len(unresolved)} id_vaga_pseudo sem vaga mestre"
                    )
    if "inscricoes_universo.csv" in frames:
        valid_inscricoes = set(frames["inscricoes_universo.csv"]["id_inscricao_pseudo"])
        for filename in ("inscricoes_opcoes.csv", "eventos_longos.csv", "cutoff_candidatos.csv"):
            if filename in frames and "id_inscricao_pseudo" in frames[filename]:
                unresolved = (
                    set(frames[filename]["id_inscricao_pseudo"])
                    - valid_inscricoes
                    - {""}
                )
                if unresolved:
                    errors.append(
                        f"{filename}: {len(unresolved)} id_inscricao_pseudo sem universo"
                    )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    input_dir = args.input_dir.resolve()
    output = args.output.resolve()

    all_files = sorted(path for path in input_dir.iterdir() if path.is_file()) if input_dir.exists() else []
    csv_files = [
        path
        for path in all_files
        if path.suffix.lower() == ".csv"
        and not path.name.lower().startswith(("manifesto", "dicionario"))
    ]
    if not all_files:
        report = {
            "data_execucao": date.today().isoformat(),
            "status": "AGUARDANDO_RECEBIMENTO",
            "input_dir": display_path(input_dir),
            "ausencia_interpretada_como_zero": False,
            "arquivos_recebidos": 0,
            "r1_pronto_para_reexecucao": False,
            "estimacao_liberada": False,
            "nota": "Nenhuma resposta foi recebida; diretório bruto não foi criado nem alterado.",
        }
        atomic_text(output, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print("[TRIAGEM] AGUARDANDO_RECEBIMENTO; ausência não convertida em zero.")
        return

    reports: dict[str, Any] = {}
    frames: dict[str, pd.DataFrame] = {}
    unknown = [path.name for path in csv_files if path.name not in TABLES]
    for path in csv_files:
        if path.name not in TABLES:
            reports[path.name] = {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "status": "ARQUIVO_CSV_NAO_MAPEADO",
            }
            continue
        table_report, frame = inspect_table(path, TABLES[path.name])
        reports[path.name] = table_report
        frames[path.name] = frame

    forbidden = {
        filename: item["identificadores_pessoais_nao_solicitados"]
        for filename, item in reports.items()
        if item.get("identificadores_pessoais_nao_solicitados")
    }
    structural_failures = [
        filename
        for filename, item in reports.items()
        if item.get("estrutura_aprovada") is False
    ]
    foreign_key_errors = _foreign_key_errors(frames)
    r1_files = {"vagas_mestre.csv", "vagas_versoes.csv", "regra_ivs_vaga.csv"}
    r1_present = r1_files <= set(frames)
    r1_structural = r1_present and all(
        reports[filename]["estrutura_aprovada"] for filename in r1_files
    )
    metadata_present = any(input_dir.glob("manifesto.*")) and any(
        input_dir.glob("dicionario.*")
    )

    if forbidden:
        status = "INTERROMPIDO_DADO_PESSOAL_NAO_SOLICITADO"
    elif structural_failures or foreign_key_errors or unknown or not metadata_present:
        status = "RESPOSTA_INCOMPLETA"
    elif r1_structural:
        status = "TRIAGEM_ESTRUTURAL_APROVADA_R1_DEVE_SER_REEXECUTADO"
    else:
        status = "RESPOSTA_PARCIAL_SEM_NUCLEO_R1"

    report = {
        "data_execucao": date.today().isoformat(),
        "status": status,
        "input_dir": display_path(input_dir),
        "bytes_brutos_alterados": False,
        "linhas_persistidas_fora_do_bruto": False,
        "arquivos_recebidos": len(all_files),
        "arquivos": reports,
        "csv_nao_mapeados": unknown,
        "identificadores_pessoais_nao_solicitados": forbidden,
        "falhas_estruturais": structural_failures,
        "falhas_integridade_referencial": foreign_key_errors,
        "manifesto_e_dicionario_presentes": metadata_present,
        "r1_pronto_para_reexecucao": bool(
            r1_structural and metadata_present and not foreign_key_errors and not forbidden
        ),
        "estimacao_liberada": False,
        "proximo_passo": (
            "Interromper e isolar a entrega; solicitar versão minimizada."
            if forbidden
            else "Reexecutar o portão substantivo R1; esta triagem não aprova a RDD."
            if r1_structural
            else "Solicitar complementação sem converter ausência em zero."
        ),
    }
    atomic_text(output, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"[TRIAGEM] {status}; estimação liberada=False.")


if __name__ == "__main__":
    main()
