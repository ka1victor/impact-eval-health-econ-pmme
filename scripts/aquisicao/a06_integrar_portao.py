"""A06 — integra as evidências A01–A05 e decide o portão de viabilidade.

Não constrói painel analítico, não imputa eventos e não estima efeitos.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "aquisicao"
REPORT = ROOT / "docs" / "auditorias" / "03_portao_apos_aquisicao.md"
PORTAO_PATH = OUT / "portao_integrado.json"
MATRIX_PATH = OUT / "matriz_variavel_fonte_final.json"

INPUTS = [
    "output/aquisicao/a01_inventario_versoes.json",
    "output/aquisicao/a01_manifesto_vagas.json",
    "output/aquisicao/a02_manifesto_trajetoria.json",
    "output/aquisicao/a02_matriz_eventos_publicos.json",
    "output/aquisicao/a03_manifesto_ivs_regra.json",
    "output/aquisicao/a03_matriz_regra_tratamento.json",
    "output/aquisicao/a04_grade_anunciada_2025.csv",
    "output/aquisicao/a04_manifesto_pagamentos.json",
    "output/aquisicao/a04_matriz_dose_financeira.json",
    "output/aquisicao/a04_normas_regras_financeiras_pmme.json",
    "output/aquisicao/a05_auditoria_universos_cnes.json",
    "output/aquisicao/a05_dicionario_tabelas_cnes.json",
    "output/aquisicao/a05_manifesto_cnes.json",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(relative_path: str) -> Any:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8-sig"))


def evidence(path: str, detail: str) -> dict[str, str]:
    return {"caminho": path, "evidencia": detail}


def build_questions() -> list[dict[str, Any]]:
    return [
        {
            "id": 1,
            "pergunta": "Existe universo versionado e denominador de vagas?",
            "status": "passou",
            "resposta": (
                "Existem quadros oficiais versionados e denominadores fechados por publicação. "
                "Uma linha é uma célula CNES–curso e seus campos de quantidade medem vagas na versão. "
                "Não existe denominador cumulativo deduplicado entre chamadas, pois ofertas podem ser reapresentadas."
            ),
            "evidencias": [
                evidence("output/aquisicao/a01_inventario_versoes.json", "19 planilhas auditadas; denominador válido por versão, não pela soma de chamadas."),
                evidence("output/aquisicao/a05_auditoria_universos_cnes.json", "Cinco quadros finais formam união cadastral de 1.930 CNES, sem somar suas vagas."),
            ],
        },
        {
            "id": 2,
            "pergunta": "Existe id_vaga estável entre retificações e reapresentações?",
            "status": "falhou",
            "resposta": (
                "Não. CNES + curso + chamada identifica uma célula agregada, não uma vaga individual, "
                "e não demonstra identidade entre reapresentações."
            ),
            "evidencias": [evidence("output/aquisicao/a01_inventario_versoes.json", "id_vaga_existe=false e chave candidata explicitamente agregada.")],
        },
        {
            "id": 3,
            "pergunta": "Existem eventos suficientes para spells e cobertura_90/120/180?",
            "status": "falhou",
            "resposta": (
                "Não. Faltam aceite/recusa, entradas completas, afastamentos, retornos, saídas, reocupações e id_vaga. "
                "Os 1.671 registros publicados da primeira chamada são 993 chaves de candidato dentro da publicação, "
                "não o universo de inscrições. Nenhuma cobertura pode ser declarada."
            ),
            "evidencias": [evidence("output/aquisicao/a02_matriz_eventos_publicos.json", "Spells e coberturas de 90/120/180 dias classificados como incalculáveis.")],
        },
        {
            "id": 4,
            "pergunta": "Existe chave pseudonimizada PMM-E–CNES?",
            "status": "falhou",
            "resposta": (
                "Não. PMM-E publica combinações incompletas de nome, CRM ou CPF mascarado; o CNES usa CNS/identificador próprio. "
                "Pareamento nominal não é ponte determinística."
            ),
            "evidencias": [evidence("output/aquisicao/a05_auditoria_universos_cnes.json", "Ausência de chave primária compartilhada entre participante PMM-E e vínculo CNES.")],
        },
        {
            "id": 5,
            "pergunta": "O IVS, sua vintagem, precisão e cutoff aplicados estão observados por vaga?",
            "status": "falhou",
            "resposta": (
                "Não. O IVS 2010 do IPEA permanece a running variable canônica, mas não há escore administrativo contínuo por vaga, "
                "vintagem, precisão, regra de arredondamento ou cutoff do PMM-E. A divergência de 42,56% não identifica sua causa."
            ),
            "evidencias": [evidence("output/aquisicao/a03_matriz_regra_tratamento.json", "Cutoff não confirmado; escore por vaga ausente; 226/531 municípios divergem do recálculo local.")],
        },
        {
            "id": 6,
            "pergunta": "A dose é faixa anunciada, valor devido ou valor pago?",
            "status": "parcial",
            "resposta": (
                "Somente a faixa e a grade anunciada de 2025 são parcialmente observadas. Valor devido, empenhado, liquidado e pago "
                "não foram adquiridos em nível e proveniência adequados; não há dose recebida nem primeiro estágio financeiro."
            ),
            "evidencias": [evidence("output/aquisicao/a04_matriz_dose_financeira.json", "Grade normativa 2025 preservada; demais estágios financeiros não observados.")],
        },
        {
            "id": 7,
            "pergunta": "O CNES permite baseline, vínculos simultâneos, FTE cadastral e infraestrutura?",
            "status": "parcial",
            "resposta": (
                "O esquema público contém os campos necessários para essas mensurações cadastrais, mas só três de 26 competências foram inspecionadas. "
                "Presença cadastral não prova participação no PMM-E, horas realizadas ou capacidade líquida atribuível ao programa."
            ),
            "evidencias": [
                evidence("output/aquisicao/a05_dicionario_tabelas_cnes.json", "Esquemas de estabelecimento, carga horária, profissional, leitos, equipamentos e serviços nas três competências piloto."),
                evidence("output/aquisicao/a05_manifesto_cnes.json", "3 competências preservadas de 26 planejadas; 23 não baixadas."),
            ],
        },
        {
            "id": 8,
            "pergunta": "Qual é a maior janela comum madura antes de olhar efeitos?",
            "status": "parcial",
            "resposta": (
                "A maturidade é apenas calendárica: 180 dias para as duas chamadas de 2025; 90 dias ao incluir chamadas até abril de 2026; "
                "19 dias ao incluir também a oferta do ciclo 3 no corte de 12/08/2026. Sem população congelada e log de eventos, nenhuma dessas "
                "janelas é uma janela mensurável de cobertura."
            ),
            "evidencias": [evidence("output/aquisicao/a02_matriz_eventos_publicos.json", "Dias potenciais por coorte e bloqueio explícito da mensuração de cobertura.")],
        },
        {
            "id": 9,
            "pergunta": "Qual contraste é identificável: participação, pacote ou incentivo marginal?",
            "status": "falhou",
            "resposta": (
                "Nenhum contraste causal está identificado. Institucionalmente, o candidato mais estreito é o incentivo marginal anunciado, "
                "condicional à vaga; porém regra, escore e primeiro estágio recebido não foram reconstruídos. Participação não é determinada pelo IVS, "
                "e não se exclui pacote de componentes simultâneos."
            ),
            "evidencias": [evidence("output/aquisicao/a03_matriz_regra_tratamento.json", "RDD inviável com dados públicos atuais; contraste candidato não estimável.")],
        },
    ]


def build_gaps() -> list[dict[str, Any]]:
    return [
        {
            "id": "A07-01",
            "objeto": "Cadastro mestre e versionamento de vagas",
            "campos_minimos": ["id_vaga_pseudo", "ciclo", "chamada", "versao_vigencia", "CNES", "curso", "quantidade", "modalidade", "reapresentacao_origem", "motivo_alteracao"],
            "desbloqueia": ["unidade vaga individual", "denominador deduplicado", "reocupação"],
        },
        {
            "id": "A07-02",
            "objeto": "Universo de inscrições e log longitudinal de eventos",
            "campos_minimos": ["id_inscricao_pseudo", "id_vaga_pseudo", "id_profissional_pseudo", "id_evento", "timestamp", "estado_anterior", "estado_novo", "motivo"],
            "eventos_minimos": ["inscrição", "classificação", "convocação", "aceite/recusa", "homologação", "entrada", "afastamento", "retorno", "transferência", "saída", "reocupação"],
            "desbloqueia": ["spells", "cobertura_90/120/180", "permanência", "rotatividade"],
        },
        {
            "id": "A07-03",
            "objeto": "Ponte pseudonimizada PMM-E–CNES",
            "campos_minimos": ["id_profissional_pseudo", "identificador_CNES_pseudo", "inicio_validade", "fim_validade", "regra_crosswalk"],
            "desbloqueia": ["atribuição de vínculo CNES ao PMM-E", "FTE cadastral individual", "vínculos simultâneos"],
        },
        {
            "id": "A07-04",
            "objeto": "Regra administrativa histórica do IVS por vaga",
            "campos_minimos": ["id_vaga_pseudo", "escore_IVS_aplicado", "vintagem", "precisao", "regra_arredondamento", "cutoff", "categoria", "faixa", "vigencia", "excecao_motivo"],
            "desbloqueia": ["reconstrução da atribuição", "teste de primeiro estágio anunciado", "avaliação futura de desenho RDD"],
        },
        {
            "id": "A07-05",
            "objeto": "Folha mensal individualizada e execução financeira vinculável",
            "campos_minimos": ["competencia", "id_vaga_pseudo", "id_profissional_pseudo", "valor_anunciado", "valor_devido", "valor_pago", "data_pagamento", "glosa", "suspensao", "estorno", "retroativo", "componente"],
            "desbloqueia": ["dose recebida", "primeiro estágio financeiro", "distinção entre devido e pago"],
        },
        {
            "id": "A07-06",
            "objeto": "Documentação e historicização dos painéis administrativos",
            "campos_minimos": ["definicao_ativo", "data_corte", "regra_atualizacao", "tratamento_afastamento_transferencia", "politica_revisao", "historicizacao_faixa", "dicionario"],
            "desbloqueia": ["interpretação do snapshot", "interpretação da série agregada", "auditoria de revisões"],
        },
    ]


def build_matrix() -> list[dict[str, Any]]:
    rows = [
        ("celula_cnes_curso", "célula agregada por publicação", "observado", "output/aquisicao/a01_inventario_versoes.json", "Não é quantidade nem vaga individual."),
        ("quantidade_vagas_publicacao", "vaga contada na versão", "observado", "output/aquisicao/a01_inventario_versoes.json", "Não somar chamadas ou versões."),
        ("id_vaga_estavel", "vaga individual longitudinal", "não observado", "output/aquisicao/a01_inventario_versoes.json", "Chave construída não substitui id administrativo."),
        ("universo_inscricoes", "inscrição submetida", "não observado", "output/aquisicao/a02_matriz_eventos_publicos.json", "Resultados publicados não demonstram universo completo."),
        ("registro_publicado_c1_ch1", "linha de preferência/resultado", "observado", "output/aquisicao/a02_matriz_eventos_publicos.json", "1.671 linhas; não são candidatos únicos."),
        ("candidato_na_publicacao_c1_ch1", "CPF mascarado + nome dentro da publicação", "parcial", "output/aquisicao/a02_matriz_eventos_publicos.json", "993 chaves; não é identificador estável global."),
        ("aceite_recusa", "evento individual", "não observado", "output/aquisicao/a02_matriz_eventos_publicos.json", "Necessário para trajetória."),
        ("entrada_saida_afastamento", "evento individual com timestamp", "não observado", "output/aquisicao/a02_matriz_eventos_publicos.json", "Snapshot só contém sobreviventes ativos."),
        ("cobertura_90_120_180", "dias cobertos por vaga", "não mensurável", "output/aquisicao/a02_matriz_eventos_publicos.json", "Faltam eventos e id_vaga."),
        ("ivs_ipea_2010", "município", "observado como referência", "data/ivs_ipea_2010_municipios.csv", "Running variable canônica, mas não prova aplicação administrativa."),
        ("escore_ivs_aplicado_por_vaga", "vaga/publicação", "não observado", "output/aquisicao/a03_matriz_regra_tratamento.json", "Vintagem, precisão e cutoff não confirmados."),
        ("faixa_anunciada", "célula/vaga publicada", "parcial", "output/aquisicao/a04_grade_anunciada_2025.csv", "Grade monetária verificável somente para 2025."),
        ("valor_devido", "profissional-vaga-competência", "não observado", "output/aquisicao/a04_matriz_dose_financeira.json", "Anunciado não implica devido."),
        ("empenhado_liquidado", "execução orçamentária", "não adquirido", "output/aquisicao/a04_manifesto_pagamentos.json", "Sem consulta oficial reproduzível preservada."),
        ("valor_pago", "profissional-vaga-competência", "não observado", "output/aquisicao/a04_matriz_dose_financeira.json", "Sem microdados vinculáveis."),
        ("snapshot_nominal", "registro de participante ativo", "observado", "data/pmm_especialistas_nominal.csv", "1.480 registros e 518 CNES; não é o universo ofertado."),
        ("uniao_cnes_quadros_a01", "estabelecimento em cinco versões", "observado", "output/aquisicao/a05_auditoria_universos_cnes.json", "1.930 CNES; não somar quantidades entre chamadas."),
        ("presenca_estabelecimento_cnes", "CNES-competência", "observado em piloto", "output/aquisicao/a05_auditoria_universos_cnes.json", "Presença cadastral não prova participação ou capacidade líquida."),
        ("vinculos_e_fte_cadastral", "profissional-CNES-competência", "esquema observado; painel incompleto", "output/aquisicao/a05_dicionario_tabelas_cnes.json", "Três competências não formam painel mensal completo."),
        ("infraestrutura", "CNES-competência", "esquema observado; painel incompleto", "output/aquisicao/a05_dicionario_tabelas_cnes.json", "Leitos, equipamentos e serviços disponíveis cadastralmente."),
        ("ponte_pmme_cnes", "profissional pseudonimizado", "não observado", "output/aquisicao/a05_auditoria_universos_cnes.json", "Nome não é chave determinística."),
        ("participacao_pmme", "profissional-vaga-tempo", "não identificada no CNES", "output/aquisicao/a05_auditoria_universos_cnes.json", "Cadastro CNES não contém marcador defensável do programa."),
    ]
    return [
        {"variavel": variable, "unidade": unit, "disponibilidade": status, "fonte": source, "limite": limit}
        for variable, unit, status, source, limit in rows
    ]


def render_report(portao: dict[str, Any]) -> str:
    status = Counter(item["status"] for item in portao["requisitos"])
    lines = [
        "# A06 — Portão integrado após a aquisição",
        "",
        "> **Data de referência:** 29 de agosto de 2026",
        "> **Escopo:** integração crítica de A01–A05, sem estimação de efeitos.",
        f"> **Decisão:** `{portao['decisao_final']}`",
        "",
        "## Decisão",
        "",
        "A decisão é **aguardar dados administrativos**. As aquisições públicas melhoraram o versionamento das ofertas, "
        "a observação de resultados publicados, a documentação normativa e a viabilidade de esquema do CNES. Ainda assim, "
        "o outcome primário de cobertura sustentada não é mensurável e nenhum contraste causal foi identificado.",
        "",
        f"Resumo do portão: **{status['passou']} passou**, **{status['parcial']} parciais**, **{status['falhou']} falharam** e "
        f"**{status['não aplicável']} não aplicáveis**.",
        "",
        "Essa decisão não autoriza o prompt 03. O próximo prompt é A07, exclusivamente para converter a lista fechada de lacunas em pedidos administrativos; não deve haver protocolo ou estimação antes da resposta e integração desses pedidos.",
        "",
        "## Respostas obrigatórias",
        "",
    ]
    for item in portao["requisitos"]:
        lines += [
            f"### {item['id']}. {item['pergunta']}",
            "",
            f"**Status: `{item['status']}`.** {item['resposta']}",
            "",
            "Evidência: " + "; ".join(f"`{ev['caminho']}` — {ev['evidencia']}" for ev in item["evidencias"]),
            "",
        ]
    lines += [
        "## Janela e contraste antes de efeitos",
        "",
        "A única afirmação possível é sobre maturidade de calendário, não cobertura observada. Restringir às duas chamadas de 2025 produz 180 dias potenciais; incluir chamadas até abril de 2026 reduz a janela comum a 90 dias; incluir o ciclo 3 reduz a 19 dias no corte nominal. Nenhuma escolha é congelada porque faltam população comparável, eventos e chave da vaga.",
        "",
        "O IVS não determina participação. O contraste institucional candidato é o incentivo marginal **anunciado** condicional à oferta, mas ele não é causalmente identificável: o escore administrativo, a regra histórica e o primeiro estágio recebido não estão observados, e outros componentes simultâneos não foram excluídos. RDD, DiD e estudo de evento permanecem bloqueados.",
        "",
        "## Distinções preservadas",
        "",
        "- célula CNES–curso, quantidade publicada e vaga individual são unidades diferentes;",
        "- registro publicado, candidato distinto dentro da publicação e universo de inscrições são universos diferentes;",
        "- o snapshot nominal de 518 CNES e a união cadastral de 1.930 CNES dos quadros não são intercambiáveis;",
        "- faixa anunciada, valor devido, empenhado, liquidado e pago são estágios financeiros diferentes;",
        "- presença cadastral no CNES não demonstra participação no PMM-E nem capacidade líquida;",
        "- 202406, 202506 e 202607 são três competências piloto, não um painel mensal completo.",
        "",
        "## Lista fechada para A07",
        "",
    ]
    for gap in portao["lacunas_fechadas_para_a07"]:
        fields = ", ".join(f"`{field}`" for field in gap["campos_minimos"])
        lines += [f"### {gap['id']} — {gap['objeto']}", "", f"Campos mínimos: {fields}.", ""]
        if gap.get("eventos_minimos"):
            events = ", ".join(f"`{event}`" for event in gap["eventos_minimos"])
            lines += [f"Eventos mínimos: {events}.", ""]
    lines += [
        "A07 deve preparar esses seis pedidos, com pseudonimização, dicionário, vigência, regras de atualização, política de revisão e indicação explícita de quando ausência significa zero, não aplicável ou não registrado. A07 não deve enviar pedidos nem estimar efeitos sem autorização posterior.",
        "",
        "## Reprodutibilidade",
        "",
        "Execute:",
        "",
        "```powershell",
        "python scripts/aquisicao/a06_integrar_portao.py",
        "python run_all.py",
        "```",
        "",
        "Os caminhos e SHA-256 das 13 entradas integradas estão em `output/aquisicao/portao_integrado.json`. A matriz final de observabilidade está em `output/aquisicao/matriz_variavel_fonte_final.json`.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    for relative_path in INPUTS:
        path = ROOT / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"Entrada obrigatória ausente: {relative_path}")
        if path.suffix == ".json":
            read_json(relative_path)

    a05 = read_json("output/aquisicao/a05_manifesto_cnes.json")
    pilots = [entry for entry in a05["fontes"] if entry.get("is_piloto")]
    if len(pilots) != 3 or a05.get("total_competencias_baixadas") != 3:
        raise ValueError("A06 exige exatamente as três competências piloto do A05.")
    for entry in pilots:
        path = ROOT / entry["caminho"]
        if path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            raise ValueError(f"ZIP CNES diverge do manifesto: {entry['competencia']}")

    questions = build_questions()
    summary = Counter(item["status"] for item in questions)
    source_inventory = [
        {"caminho": relative_path, "bytes": (ROOT / relative_path).stat().st_size, "sha256": sha256(ROOT / relative_path)}
        for relative_path in INPUTS
    ]
    portao = {
        "portao": "A06",
        "data_referencia": "2026-08-29",
        "commit_base": "c8b4cc6dc2941a720b2095029076cc15b3054a57",
        "escopo": "Integração de evidências A01–A05 sem protocolo empírico ou estimação causal",
        "decisao_final": "aguardar dados administrativos",
        "proximo_prompt": "prompts/aquisicao_dados/A07_pedidos_administrativos.md",
        "protocolo_03_liberado": False,
        "estimacao_causal_liberada": False,
        "resumo_status": {key: summary.get(key, 0) for key in ("passou", "parcial", "falhou", "não aplicável")},
        "requisitos": questions,
        "lacunas_fechadas_para_a07": build_gaps(),
        "entradas_integradas": source_inventory,
    }
    matrix = {
        "matriz": "A06 — variável × fonte final",
        "data_referencia": "2026-08-29",
        "decisao_do_portao": portao["decisao_final"],
        "regras_de_leitura": [
            "Observado não implica adequado para identificação causal.",
            "Não somar versões ou chamadas que possam reapresentar vagas.",
            "Não inferir participação no PMM-E a partir de presença no CNES.",
            "Não converter maturidade de calendário em cobertura mensurável.",
        ],
        "variaveis": build_matrix(),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    PORTAO_PATH.write_text(json.dumps(portao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MATRIX_PATH.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(portao), encoding="utf-8")
    print(f"Portão A06: {portao['decisao_final']}")
    print(f"Resumo: {portao['resumo_status']}")
    print(f"Próximo prompt: {portao['proximo_prompt']}")


if __name__ == "__main__":
    main()
