"""Consolida o estado executado do plano causal e aplica bloqueios fail-closed.

Este controlador não estima efeitos. Ele lê os portões já produzidos e impede
que artefatos de R3/R4 existam fora de ordem: protocolo R3 só depois de R1 e
R2 aprovados, e resultado R4 só depois de protocolo R3 congelado.

Desde 05/10/2026 o R1 vigente é o do IVS administrativo da SGTES
(`a01c_regra_ivs_administrativo.json`). O R1 público com o IVS 2010 do Atlas
(`portao_regra_ivs.json`) continua lido como diagnóstico: ele segue reprovado
para aquela running variable.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
R1 = ROOT / "output" / "rdd_bolsa" / "portao_regra_ivs.json"
R1_ADM = ROOT / "output" / "rdd_bolsa" / "a01c_regra_ivs_administrativo.json"
R2 = ROOT / "output" / "rdd_bolsa" / "r2_portao.json"
R3 = ROOT / "output" / "rdd_bolsa" / "registro_pre_analise.json"
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

RESULTADOS_R4 = (
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
    r1 = report["r1"]
    r2 = report["r2"]
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
            f"- R1 com o IVS administrativo da SGTES reproduz a faixa anunciada em "
            f"{r1['acertos']} de {r1['total']} combinações município–onda–versão, de 2025 e 2026. "
            "A regra é a do item 11.2 do Edital SGTES/MS nº 28/2026, com os cortes "
            "0,300 e 0,400.",
            f"- O R1 público com o IVS 2010 do Atlas continua reprovado: "
            f"{report['r1_publico']['n_divergentes']} de {report['r1_publico']['n_municipios']} "
            f"municípios ({report['r1_publico']['pct_divergentes']:.1f}%) divergem. "
            "O IVS 2010 não é a running variable administrativa.",
            f"- R2 sem outcomes: `{r2['decisao']}`. Cortes viáveis: {', '.join(r2['cortes_viaveis']) or 'nenhum'}. "
            "O estimador principal candidato é local-linear; a randomização local não balanceia "
            "em janela com suporte suficiente.",
            f"- A alternativa A7 contém {report['alternativa_a7']['pares_adjacentes']} "
            "pares, mas continua preliminar até a observação dos desempates e das chaves estáveis.",
            "- O pacote focal de solicitação continua no repositório e nenhum pedido foi "
            "enviado; ele deixou de ser pré-condição do R1.",
            "",
            "## Próxima ação",
            "",
            report["proxima_acao"],
            "",
            "## Regra de parada",
            "",
            "Protocolo R3 só pode existir com R1 aprovado e R2 viável; resultado R4 só "
            "pode existir com protocolo R3 congelado. Até aqui nenhum efeito RDD de atração "
            "foi estimado, e a ordem foi verificada nesta execução.",
            "",
        ]
    )


def main() -> None:
    required = (R1, R1_ADM, R2, FIRST_STAGE, A7, TRIAGE, *REQUESTS)
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Artefatos necessários ausentes: {missing}")

    r1_publico = load_json(R1)
    r1 = load_json(R1_ADM)
    r2 = load_json(R2)
    first_stage = load_json(FIRST_STAGE)
    a7 = load_json(A7)
    triage = load_json(TRIAGE)
    r1_aprovado = r1["decisao_r1"] in {"APROVADO_SHARP", "APROVADO_FUZZY"}
    r2_viavel = r2["decisao_r2"].startswith("VIAVEL")
    r3_congelado = R3.exists()
    resultados = [
        str(path.relative_to(ROOT)).replace("\\", "/") for path in RESULTADOS_R4 if path.exists()
    ]
    if r3_congelado and not (r1_aprovado and r2_viavel):
        raise RuntimeError("Violação fail-closed: protocolo R3 existe sem R1 aprovado e R2 viável.")
    if resultados and not r3_congelado:
        raise RuntimeError(
            "Violação fail-closed: há resultados R4 sem protocolo R3 congelado: " + ", ".join(resultados)
        )
    autorizada = r1_aprovado and r2_viavel and r3_congelado
    if not r1_aprovado:
        status_geral = "PARCIAL_EXECUTADO_AGUARDANDO_DADOS_ADMINISTRATIVOS"
    elif not r2_viavel:
        status_geral = "R2_REPROVADO_SEM_ESTIMACAO"
    elif not r3_congelado:
        status_geral = "R1_R2_EXECUTADOS_AGUARDANDO_R3"
    else:
        status_geral = "R3_CONGELADO_R4_AUTORIZAVEL"

    request_hashes = {
        str(path.relative_to(ROOT)).replace("\\", "/"): sha256(path)
        for path in REQUESTS
    }
    diagnostic = r1_publico["diagnostico_publico"]
    reproducao = r1["reproducao_da_faixa_anunciada"]
    support = a7["suporte"]
    report: dict[str, Any] = {
        "data_execucao": date.today().isoformat(),
        "status_geral": status_geral,
        "estimacao_rdd_atracao_autorizada": autorizada,
        "fail_closed_verificado": True,
        "artefatos_proibidos_encontrados": [] if r3_congelado else resultados,
        "etapas": {
            "P0": {
                "status": "CONCLUIDO",
                "evidencia": "síntese, diagnóstico público e plano causal versionados",
            },
            "P1": {
                "status": "PRONTO_NAO_ENVIADO",
                "evidencia": "pacote completo e não enviado; deixou de ser pré-condição do R1, pois o IVS administrativo é público",
            },
            "R1": {
                "status": r1["decisao_r1"],
                "evidencia": (
                    f"IVS administrativo reproduz {reproducao['acertos']}/{reproducao['total_municipio_onda_versao']} "
                    "município-onda-versão; IVS 2010 público segue reprovado"
                ),
            },
            "R2": {
                "status": r2["decisao_r2"],
                "evidencia": "suporte, seleção na oferta, balanço e PMMB sem outcomes; potência limitada",
            },
            "R3": {
                "status": "CONGELADO" if r3_congelado else (
                    "PENDENTE_AUTORIZACAO_DO_AUTOR" if r1_aprovado and r2_viavel else "BLOQUEADO_ATE_R1_R2"
                ),
                "evidencia": (
                    "registro de pré-análise congelado" if r3_congelado
                    else "rascunho do protocolo em docs/05_identificacao/18; nenhum registro congelado"
                ),
            },
            "R4": {
                "status": "AUTORIZAVEL" if autorizada else "BLOQUEADO_ATE_R3",
                "evidencia": "nenhum efeito RDD de atração estimado" if not resultados else "resultados R4 presentes",
            },
            "R5": {
                "status": "FORA_DO_NUCLEO_CURTO",
                "evidencia": "presença/retenção depende de eventos válidos e só segue após R4",
            },
        },
        "r1": {
            "running_variable": r1["running_variable"],
            "decisao": r1["decisao_r1"],
            "acertos": reproducao["acertos"],
            "total": reproducao["total_municipio_onda_versao"],
        },
        "r1_publico": {
            "decisao": r1_publico["decisao_r1"],
            "n_municipios": diagnostic["n_municipios"],
            "n_divergentes": diagnostic["n_divergentes"],
            "pct_divergentes": diagnostic["pct_divergentes"],
        },
        "r2": {
            "decisao": r2["decisao_r2"],
            "cortes_viaveis": r2["cortes_viaveis"],
            "ressalvas": r2["ressalvas"],
            "mde_conjunto_dois_cortes_pp": r2["mde_conjunto_dois_cortes_pp"],
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
            "precondicao_do_r1": False,
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
            "Revisar as rodadas de 01/10 e 05/10 e integrar os branches, na ordem de "
            "prompts/integracao_rodadas_outubro_2026/README.md. Depois, o autor decide unidade, "
            "banda, outcomes e linguagem do R3 "
            "(docs/05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md) e autoriza o congelamento, "
            "pelo prompt prompts/avaliacao_rdd_bolsa/02_congelar_protocolo_r3.md. Só então R4 pode ser executado."
            if r1_aprovado and r2_viavel and not r3_congelado
            else "Seguir a ordem dos portões."
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
