"""Gera um inventario deterministico das bases observadas do projeto."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "output"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def nonempty_unique(rows: list[dict[str, str]], field: str) -> set[str]:
    return {row.get(field, "").strip() for row in rows if row.get(field, "").strip()}


def main() -> None:
    nominal_path = DATA / "pmm_especialistas_nominal.csv"
    series_path = DATA / "pmm_especialistas_serie_historica.csv"
    ivs_path = DATA / "ivs_ipea_2010_municipios.csv"

    nominal = read_csv(nominal_path)
    series = read_csv(series_path)
    ivs = read_csv(ivs_path)

    crm_uf = {
        f"{row.get('uf', '').strip()}-{row.get('crm', '').strip()}"
        for row in nominal
        if row.get("uf", "").strip() and row.get("crm", "").strip()
    }
    ivs_values = [float(row["ivs_2010"]) for row in ivs if row.get("ivs_2010", "").strip()]

    result = {
        "escopo": "inventario de dados observados; nao contem estimativas causais",
        "arquivos": {
            nominal_path.name: {
                "sha256": sha256(nominal_path),
                "linhas": len(nominal),
                "colunas": list(nominal[0]) if nominal else [],
                "crm_uf_unicos": len(crm_uf),
                "municipios_unicos": len(nonempty_unique(nominal, "co_ibge")),
                "cnes_unicos": len(nonempty_unique(nominal, "co_cnes")),
                "cursos_unicos": len(nonempty_unique(nominal, "curso")),
                "datas_referencia": sorted(nonempty_unique(nominal, "dt_referencia")),
            },
            series_path.name: {
                "sha256": sha256(series_path),
                "linhas": len(series),
                "colunas": list(series[0]) if series else [],
                "municipios_unicos": len(nonempty_unique(series, "co_ibge")),
                "cnes_unicos_preenchidos": len(nonempty_unique(series, "co_cnes")),
                "cursos_rotulos_unicos": len(nonempty_unique(series, "curso")),
                "competencias": sorted(nonempty_unique(series, "competencia")),
            },
            ivs_path.name: {
                "sha256": sha256(ivs_path),
                "linhas": len(ivs),
                "colunas": list(ivs[0]) if ivs else [],
                "municipios_unicos": len(nonempty_unique(ivs, "cod_ibge6")),
                "ivs_min": min(ivs_values) if ivs_values else None,
                "ivs_max": max(ivs_values) if ivs_values else None,
            },
        },
        "outcomes": {
            "preenchimento_vagas": {"status": "nao calculavel", "bloqueio": "denominador de vagas ausente"},
            "entrada_efetiva": {"status": "parcial", "bloqueio": "somente ativos atuais sao observados"},
            "retencao_individual": {"status": "nao calculavel", "bloqueio": "serie sem identificador individual"},
            "fte_liquido": {"status": "nao calculavel", "bloqueio": "CNES e carga horaria mensal ausentes"},
            "producao_especializada": {"status": "sem dados", "bloqueio": "SIA/SIH ausentes"},
            "tempo_espera": {"status": "sem dados", "bloqueio": "dados de regulacao ausentes"},
            "acesso_local_global": {"status": "sem dados", "bloqueio": "fluxo residencia-prestador ausente"},
            "outcomes_clinicos": {"status": "sem dados", "bloqueio": "APAC/SIH/linha de cuidado ausentes"},
            "custos_bem_estar": {"status": "sem dados", "bloqueio": "custos e transporte observados ausentes"},
            "equidade_ivs": {"status": "base disponivel", "bloqueio": "depende de outcomes observados"},
        },
    }

    OUTPUT.mkdir(exist_ok=True)
    output_path = OUTPUT / "inventario_dados.json"
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Inventario salvo em {output_path}")
    print(f"Nominal: {len(nominal)} linhas | Serie: {len(series)} linhas | IVS: {len(ivs)} municipios")


if __name__ == "__main__":
    main()
