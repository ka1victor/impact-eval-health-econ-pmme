"""Consolida o estado executado do plano causal e aplica bloqueios fail-closed.

Este controlador não estima efeitos. Ele lê os portões já produzidos, verifica
se o pacote de solicitação está pronto e impede que artefatos de R3/R4 existam
quando R1 não foi aprovado.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
R1 = ROOT / "output" / "rdd_bolsa" / "portao_regra_ivs.json"
FIRST_STAGE = ROOT / "output" / "rdd_bolsa" / "a01_primeiro_estagio_publico.json"
A7 = ROOT / "output" / "tema_trabalho" / "A7_cutoff_selecao_resumo.json"
TRIAGE = ROOT / "output" / "rdd_bolsa" / "triagem_resposta_administrativa.json"
REQUESTS = (
    ROOT / "docs" / "pedidos_dados" / "solicitacao_focal_rdd_bolsa.md",
    ROOT / "docs" / "pedidos_dados" / "vagas_e_regra_ivs.md",
    ROOT / "docs" / "pedidos_dados" / "eventos_e_ponte_cnes.md",
    ROOT / "docs" / "pedidos_dados" / "cutoff_selecao_causal.md",
)
OUT_JSON = ROOT / "output" / "rdd_bolsa" / "status_execucao_plano_causal.json"
OUT_MD = ROOT / "docs" / "06_execucao" / "33_status_execucao_plano_causal.md"

PROHIBITED_WHILE_R1_FAILS = (
    ROOT / "output" / "rdd_bolsa" / "registro_pre_analise.json",
    ROOT / "output" / "rdd_bolsa" / "resultados_rdd_atracao.csv",
    ROOT / "output" / "rdd_bolsa" / "resultados_rdd_atracao.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def _markdown(report: dict[str, Any]) -> str:
    rows = []
    for key in ("P0", "P1", "R1", "R2", "R3", "R4", "R5"):
        item = report["etapas"][key]
        rows.append(f"| {key} | `{item['status']}` | {item['evidencia']} |")
    return "\n".join(
        [
            "# Estado executado do novo plano causal",
            "",
            f"> **Data:** {report['data_execucao']}.",
            f"> **Estado geral:** `{report['status_geral']}`.",
            "",
            "## Portões e ações",
            "",
            "| Etapa | Estado | Evidência/decisão |",
            "|---|---|---|",
            *rows,
            "",
            "## O que já está estabelecido",
            "",
            f"- R1 público auditou {report['r1']['n_municipios']} municípios: "
            f"{report['r1']['n_divergentes']} faixas ({report['r1']['pct_divergentes']:.1f}%) "
            "não são reproduzidas pela taxonomia externa.",
            "- A fuzzy pública também está reprovada: o valor anunciado não salta de "
            "forma estável no IVS disponível.",
            f"- A alternativa A7 contém {report['alternativa_a7']['pares_adjacentes']} "
            "pares, mas continua preliminar até a observação dos desempates e das chaves estáveis.",
            "- O pacote focal de solicitação está completo no repositório, mas nenhum "
            "pedido foi enviado.",
            f"- A triagem administrativa está em `{report['triagem_resposta']['status']}`; "
            f"foram recebidos {report['triagem_resposta']['arquivos_recebidos']} arquivos.",
            "",
            "## Próxima ação externa necessária",
            "",
            "O autor precisa escolher e autorizar o canal de submissão ao Ministério da "
            "Saúde. Após o recebimento, os bytes devem ser preservados fora do controle "
            "de versão em `data/raw/administrativo_rdd_bolsa/`; R1 será repetido antes "
            "de qualquer outcome.",
            "",
            "## Regra de parada",
            "",
            "Enquanto R1 não for `APROVADO_SHARP` ou `APROVADO_FUZZY`, não criar "
            "pré-análise R3 nem resultados R4. A ausência desses artefatos foi verificada "
            "nesta execução.",
            "",
        ]
    )


def main() -> None:
    required = (R1, FIRST_STAGE, A7, TRIAGE, *REQUESTS)
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Artefatos necessários ausentes: {missing}")

    r1 = load_json(R1)
    first_stage = load_json(FIRST_STAGE)
    a7 = load_json(A7)
    triage = load_json(TRIAGE)
    approved = r1["decisao_r1"] in {"APROVADO_SHARP", "APROVADO_FUZZY"}
    prohibited_present = [
        str(path.relative_to(ROOT)).replace("\\", "/")
        for path in PROHIBITED_WHILE_R1_FAILS
        if path.exists()
    ]
    if not approved and prohibited_present:
        raise RuntimeError(
            "Violação fail-closed: R1 não passou, mas há artefatos de R3/R4: "
            + ", ".join(prohibited_present)
        )

    request_hashes = {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
        for path in REQUESTS
    }
    diagnostic = r1["diagnostico_publico"]
    support = a7["suporte"]
    report: dict[str, Any] = {
        "data_execucao": date.today().isoformat(),
        "status_geral": (
            "PRONTO_PARA_R2" if approved else "PARCIAL_EXECUTADO_AGUARDANDO_DADOS_ADMINISTRATIVOS"
        ),
        "estimacao_rdd_atracao_autorizada": approved,
        "fail_closed_verificado": not prohibited_present,
        "artefatos_proibidos_encontrados": prohibited_present,
        "etapas": {
            "P0": {
                "status": "CONCLUIDO",
                "evidencia": "síntese, diagnóstico público e plano causal versionados",
            },
            "P1": {
                "status": "PRONTO_NAO_ENVIADO",
                "evidencia": "texto focal, layouts e pedidos técnicos completos; falta canal autorizado",
            },
            "R1": {
                "status": r1["decisao_r1"],
                "evidencia": "matriz municipal e portão público reproduzíveis",
            },
            "R2": {
                "status": "PENDENTE" if approved else "BLOQUEADO_POR_R1",
                "evidencia": "não abrir outcomes; escore administrativo ainda ausente",
            },
            "R3": {
                "status": "BLOQUEADO_ATE_R1_R2",
                "evidencia": "pré-análise prospectiva não criada prematuramente",
            },
            "R4": {
                "status": "BLOQUEADO_ATE_R1_R3",
                "evidencia": "nenhum efeito RDD de atração estimado",
            },
            "R5": {
                "status": "FORA_DO_NUCLEO_CURTO",
                "evidencia": "presença/retenção depende de eventos válidos e só segue após R4",
            },
        },
        "r1": {
            "n_municipios": diagnostic["n_municipios"],
            "n_divergentes": diagnostic["n_divergentes"],
            "pct_divergentes": diagnostic["pct_divergentes"],
        },
        "primeiro_estagio_publico": first_stage["portao_fuzzy_com_ivs_publico"],
        "alternativa_a7": {
            "status": a7["status"],
            "pares_adjacentes": support["pares_adjacentes_total_quatro_publicacoes"],
            "pares_outcome_2025": support["pares_com_outcome_2025"],
            "pares_mesmo_escore_outcome_2025": support[
                "pares_mesmo_escore_com_outcome_2025"
            ],
        },
        "pacote_solicitacao": {
            "status": "PRONTO_NAO_ENVIADO",
            "arquivos_sha256": request_hashes,
            "canal_submissao": None,
            "protocolo": None,
        },
        "triagem_resposta": {
            "status": triage["status"],
            "arquivos_recebidos": triage["arquivos_recebidos"],
            "ausencia_interpretada_como_zero": triage.get(
                "ausencia_interpretada_como_zero", False
            ),
            "r1_pronto_para_reexecucao": triage["r1_pronto_para_reexecucao"],
            "estimacao_liberada": triage["estimacao_liberada"],
        },
        "proxima_acao": (
            "Autor escolher e autorizar o canal; submeter conjuntamente regra/vagas e "
            "inscrições/eventos; ao receber, preservar bruto e repetir R1."
        ),
    }

    atomic_text(OUT_JSON, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    atomic_text(OUT_MD, _markdown(report))
    print(
        f"[PLANO] {report['status_geral']}; "
        f"RDD de atração autorizada={report['estimacao_rdd_atracao_autorizada']}."
    )


if __name__ == "__main__":
    main()
