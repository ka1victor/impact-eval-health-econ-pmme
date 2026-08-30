"""01_congelar_ponte_cbo.py — Ponte operacional Curso PMM-E -> CBOs CNES.

Este script estabelece e congela a correspondência determinística entre os 16 cursos
de formação/aprimoramento do Programa Mais Médicos Especialistas (PMM-E / Lei 15.233/2025)
e a Classificação Brasileira de Ocupações (CBO 2002 de 6 dígitos, famílias 2251, 2252, 2253).

O script audita a univocidade, sinaliza sobreposições (cursos concorrentes no mesmo CBO)
e gera o arquivo estruturado `output/aquisicao/ponte_curso_cbo_oficial.json`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output" / "aquisicao"
OUTPUT_FILE = OUTPUT_DIR / "ponte_curso_cbo_oficial.json"

# Catálogo canônico dos 16 cursos do PMM-E
CURSOS_PMME_CBO: List[Dict[str, Any]] = [
    {
        "cod_curso": 1,
        "no_curso_padronizado": "ANESTESIOLOGIA PERIOPERATORIA E SEDACAO SEGURA",
        "nome_edital": "01. ANESTESIOLOGIA PERIOPERATÓRIA E SEDAÇÃO SEGURA",
        "especialidade_cfm": "Anestesiologia",
        "cbo_primario": "225151",
        "ds_cbo_primario": "MEDICO ANESTESIOLOGISTA",
        "cbos_elegiveis": ["225151"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "UNIVOCA",
        "observacoes": "Mapeamento 1:1 estrito sem concorrência com outros cursos do programa.",
    },
    {
        "cod_curso": 2,
        "no_curso_padronizado": "CIRURGIA GERAL MINIMAMENTE INVASIVA",
        "nome_edital": "02. CIRURGIA GERAL MINIMAMENTE INVASIVA",
        "especialidade_cfm": "Cirurgia Geral",
        "cbo_primario": "225225",
        "ds_cbo_primario": "MEDICO CIRURGIAO GERAL",
        "cbos_elegiveis": ["225225"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "UNIVOCA",
        "observacoes": "Mapeamento 1:1 estrito para cirurgiões gerais.",
    },
    {
        "cod_curso": 3,
        "no_curso_padronizado": "CIRURGIA ONCOLOGICA AVANCADA",
        "nome_edital": "03. CIRURGIA ONCOLÓGICA AVANÇADA",
        "especialidade_cfm": "Cirurgia Oncológica / Cancerologia Cirúrgica",
        "cbo_primario": "225290",
        "ds_cbo_primario": "MEDICO CANCEROLOGISTA CIRURGICO",
        "cbos_elegiveis": ["225290"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "UNIVOCA",
        "observacoes": "Mapeamento 1:1 para cirurgia oncológica.",
    },
    {
        "cod_curso": 4,
        "no_curso_padronizado": "CIRURGIA COLOPROCTOLOGICA COM FOCO EM TUMORES COLORRETAIS",
        "nome_edital": "04. CIRURGIA COLOPROCTOLÓGICA COM FOCO EM TUMORES COLORRETAIS",
        "especialidade_cfm": "Coloproctologia",
        "cbo_primario": "225280",
        "ds_cbo_primario": "MEDICO COLOPROCTOLOGISTA",
        "cbos_elegiveis": ["225280"],
        "sobreposicao": True,
        "cursos_compartilhados": [7],
        "grau_univocidade": "SOBREPOSTA_SECUNDARIA",
        "observacoes": "CBO 225280 é primário do curso 04 e compõe conjunto ampliado do curso 07 (Colonoscopia).",
    },
    {
        "cod_curso": 5,
        "no_curso_padronizado": "CIRURGIA DO APARELHO DIGESTIVO COM FOCO EM TUMORES DIGESTIVOS",
        "nome_edital": "05. CIRURGIA DO APARELHO DIGESTIVO COM FOCO EM TUMORES DIGESTIVOS",
        "especialidade_cfm": "Cirurgia do Aparelho Digestivo",
        "cbo_primario": "225220",
        "ds_cbo_primario": "MEDICO CIRURGIAO DO APARELHO DIGESTIVO",
        "cbos_elegiveis": ["225220"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "UNIVOCA",
        "observacoes": "Mapeamento 1:1 para cirurgia do aparelho digestivo.",
    },
    {
        "cod_curso": 6,
        "no_curso_padronizado": "CIRURGIA GINECOLOGICA COM FOCO EM TUMORES GINECOLOGICOS",
        "nome_edital": "06. CIRURGIA GINECOLÓGICA COM FOCO EM TUMORES GINECOLÓGICOS",
        "especialidade_cfm": "Ginecologia e Obstetrícia",
        "cbo_primario": "225250",
        "ds_cbo_primario": "MEDICO GINECOLOGISTA E OBSTETRA",
        "cbos_elegiveis": ["225250"],
        "sobreposicao": True,
        "cursos_compartilhados": [8],
        "grau_univocidade": "SOBREPOSTA_DIRETA",
        "observacoes": "Compartilha CBO 225250 diretamente com o curso 08 (Colposcopia).",
    },
    {
        "cod_curso": 7,
        "no_curso_padronizado": "COLONOSCOPIA DIAGNOSTICA E TERAPEUTICA NO SUS",
        "nome_edital": "07. COLONOSCOPIA DIAGNÓSTICA E TERAPÊUTICA NO SUS",
        "especialidade_cfm": "Endoscopia / Coloproctologia / Gastroenterologia",
        "cbo_primario": "225310",
        "ds_cbo_primario": "MEDICO EM ENDOSCOPIA",
        "cbos_elegiveis": ["225310", "225280", "225165"],
        "sobreposicao": True,
        "cursos_compartilhados": [4, 10, 11],
        "grau_univocidade": "MULTIESPECIALIDADE",
        "observacoes": "Procedimento realizado por endoscopistas (225310), coloproctologistas (225280) e gastroenterologistas (225165).",
    },
    {
        "cod_curso": 8,
        "no_curso_padronizado": "COLPOSCOPIA E DOENCAS DO TRATO GENITAL INFERIOR",
        "nome_edital": "08. COLPOSCOPIA E DOENÇAS DO TRATO GENITAL INFERIOR",
        "especialidade_cfm": "Ginecologia e Obstetrícia",
        "cbo_primario": "225250",
        "ds_cbo_primario": "MEDICO GINECOLOGISTA E OBSTETRA",
        "cbos_elegiveis": ["225250"],
        "sobreposicao": True,
        "cursos_compartilhados": [6],
        "grau_univocidade": "SOBREPOSTA_DIRETA",
        "observacoes": "Compartilha CBO 225250 diretamente com o curso 06 (Cirurgia Ginecológica).",
    },
    {
        "cod_curso": 9,
        "no_curso_padronizado": "ECOCARDIOGRAFIA TRANSTORACICA APLICADA AO SUS",
        "nome_edital": "09. ECOCARDIOGRAFIA TRANSTORÁCICA APLICADA AO SUS",
        "especialidade_cfm": "Cardiologia",
        "cbo_primario": "225120",
        "ds_cbo_primario": "MEDICO CARDIOLOGISTA",
        "cbos_elegiveis": ["225120"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "UNIVOCA",
        "observacoes": "Mapeamento 1:1 para cardiologistas executores de ecocardiografia.",
    },
    {
        "cod_curso": 10,
        "no_curso_padronizado": "ENDOSCOPIA DIGESTIVA AVANCADA E PROCEDIMENTOS TERAPEUTICOS",
        "nome_edital": "10. ENDOSCOPIA DIGESTIVA AVANÇADA E PROCEDIMENTOS TERAPÊUTICOS",
        "especialidade_cfm": "Endoscopia / Gastroenterologia",
        "cbo_primario": "225310",
        "ds_cbo_primario": "MEDICO EM ENDOSCOPIA",
        "cbos_elegiveis": ["225310", "225165"],
        "sobreposicao": True,
        "cursos_compartilhados": [7, 11],
        "grau_univocidade": "SOBREPOSTA_DIRETA",
        "observacoes": "Compartilha CBOs com os cursos 07 e 11.",
    },
    {
        "cod_curso": 11,
        "no_curso_padronizado": "ENDOSCOPIA DIGESTIVA: ALTA DIAGNOSTICA E TERAPEUTICA",
        "nome_edital": "11. ENDOSCOPIA DIGESTIVA: ALTA DIAGNÓSTICA E TERAPÊUTICA",
        "especialidade_cfm": "Endoscopia / Gastroenterologia",
        "cbo_primario": "225310",
        "ds_cbo_primario": "MEDICO EM ENDOSCOPIA",
        "cbos_elegiveis": ["225310", "225165"],
        "sobreposicao": True,
        "cursos_compartilhados": [7, 10],
        "grau_univocidade": "SOBREPOSTA_DIRETA",
        "observacoes": "Compartilha CBOs com os cursos 07 e 10.",
    },
    {
        "cod_curso": 12,
        "no_curso_padronizado": "ONCOLOGIA CLINICA: CANCERES PREVALENTES NO SUS",
        "nome_edital": "12. ONCOLOGIA CLÍNICA: CÂNCERES PREVALENTES NO SUS",
        "especialidade_cfm": "Oncologia Clínica / Cancerologia Clínica",
        "cbo_primario": "225121",
        "ds_cbo_primario": "MEDICO ONCOLOGISTA CLINICO",
        "cbos_elegiveis": ["225121"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "UNIVOCA",
        "observacoes": "Mapeamento 1:1 para oncologia clínica.",
    },
    {
        "cod_curso": 13,
        "no_curso_padronizado": "RADIOTERAPIA: PLANEJAMENTO E EXECUCAO NO SUS",
        "nome_edital": "13. RADIOTERAPIA: PLANEJAMENTO E EXECUÇÃO NO SUS",
        "especialidade_cfm": "Radioterapia",
        "cbo_primario": "225330",
        "ds_cbo_primario": "MEDICO RADIOTERAPEUTA",
        "cbos_elegiveis": ["225330"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "UNIVOCA",
        "observacoes": "Mapeamento 1:1 para médicos radioterapeutas.",
    },
    {
        "cod_curso": 14,
        "no_curso_padronizado": "ULTRASSONOGRAFIA MAMARIA DIAGNOSTICA E INTERVENCIONISTA",
        "nome_edital": "14. ULTRASSONOGRAFIA MAMÁRIA DIAGNÓSTICA E INTERVENCIONISTA",
        "especialidade_cfm": "Radiologia e Diagnóstico por Imagem / Mastologia",
        "cbo_primario": "225320",
        "ds_cbo_primario": "MEDICO EM RADIOLOGIA E DIAGNOSTICO POR IMAGEM",
        "cbos_elegiveis": ["225320", "225255"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "MULTIESPECIALIDADE_EXCLUSIVA",
        "observacoes": "Abrange CBOs 225320 e 225255 sem colisão com outros cursos PMM-E.",
    },
    {
        "cod_curso": 15,
        "no_curso_padronizado": "VIDEOLARINGOSCOPIA E ENDOSCOPIA NASOFARINGEA",
        "nome_edital": "15. VIDEOLARINGOSCOPIA E ENDOSCOPIA NASOFARÍNGEA",
        "especialidade_cfm": "Otorrinolaringologia",
        "cbo_primario": "225275",
        "ds_cbo_primario": "MEDICO OTORRINOLARINGOLOGISTA",
        "cbos_elegiveis": ["225275"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "UNIVOCA",
        "observacoes": "Mapeamento 1:1 para otorrinolaringologistas.",
    },
    {
        "cod_curso": 16,
        "no_curso_padronizado": "ANATOMIA PATOLOGICA COM ENFASE EM ONCOLOGIA E DIAGNOSTICO INTEGRADO",
        "nome_edital": "16. ANATOMIA PATOLÓGICA COM ÊNFASE EM ONCOLOGIA E DIAGNÓSTICO INTEGRADO",
        "especialidade_cfm": "Anatomopatologia / Patologia",
        "cbo_primario": "225148",
        "ds_cbo_primario": "MEDICO ANATOMOPATOLOGISTA",
        "cbos_elegiveis": ["225148", "225325", "225305"],
        "sobreposicao": False,
        "cursos_compartilhados": [],
        "grau_univocidade": "FAMILIA_PATOLOGIA",
        "observacoes": "Abrange CBOs 225148 (Anatomopatologista), 225325 (Patologista) e 225305 (Citopatologista).",
    },
]


def construir_dicionario_cbo() -> Dict[str, Any]:
    """Compila e audita o mapa de CBOs, identificando cursos por CBO."""
    cbo_to_cursos: Dict[str, List[int]] = {}
    todos_cbos_unicos: set[str] = set()

    for item in CURSOS_PMME_CBO:
        for cbo in item["cbos_elegiveis"]:
            todos_cbos_unicos.add(cbo)
            if cbo not in cbo_to_cursos:
                cbo_to_cursos[cbo] = []
            cbo_to_cursos[cbo].append(item["cod_curso"])

    cursos_estritamente_univocos = [
        item["cod_curso"] for item in CURSOS_PMME_CBO if not item["sobreposicao"]
    ]
    cursos_sobrepostos = [
        item["cod_curso"] for item in CURSOS_PMME_CBO if item["sobreposicao"]
    ]

    catalogo_auditado: List[Dict[str, Any]] = []
    for item in CURSOS_PMME_CBO:
        registro = dict(item)
        registro["status_uso"] = "CONFIRMATORIO_SEM_SOBREPOSICAO" if not item["sobreposicao"] else "SENSIBILIDADE_AMPLIADA"
        registro["natureza_correspondencia"] = (
            "Correspondência operacional entre a especialidade/area indicada pelo curso e o titulo da CBO; "
            "não é uma crosswalk publicada pelo controlador do PMM-E."
        )
        catalogo_auditado.append(registro)

    resultado: Dict[str, Any] = {
        "versao_ponte": "2.0_operacional_auditada",
        "status_substantivo": "OPERACIONAL_NAO_PUBLICADA_COMO_CROSSWALK_OFICIAL",
        "data_congelamento": "2026-08-30",
        "total_cursos_pmme": len(CURSOS_PMME_CBO),
        "total_cbos_distintos": len(todos_cbos_unicos),
        "cursos_estritamente_univocos": cursos_estritamente_univocos,
        "cursos_sobrepostos": cursos_sobrepostos,
        "catalogo_cursos": catalogo_auditado,
        "cbo_para_cursos_map": cbo_to_cursos,
        "fontes_institucionais": [
            {
                "titulo": "Chamamento Público SGTES/MS nº 3/2025 — requisitos de participação",
                "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/faq/quem-pode-participar-do-chamamento",
                "uso": "Confirma que os participantes devem ser especialistas nas especialidades ou áreas listadas no edital e possuir RQE ou qualificação equivalente.",
            },
            {
                "titulo": "Página institucional do Projeto Mais Médicos Especialistas",
                "url": "https://www.gov.br/saude/pt-br/composicao/sgtes/mais-medicos/medico-e-medica/especialistas",
                "uso": "Confirma objetivo de provimento, aprimoramento em serviço e especialidades contempladas.",
            },
            {
                "titulo": "Consulta oficial da Classificação Brasileira de Ocupações",
                "url": "https://consulta.trabalho.gov.br/empregador/cbo/procuracbo/default.asp",
                "uso": "Fonte dos códigos e títulos ocupacionais usados no CNES.",
            },
        ],
        "limite_de_validade": (
            "As fontes sustentam especialidades elegíveis e títulos CBO, mas não publicam uma ponte curso-CBO. "
            "Por isso, cursos com CBO compartilhado ficam fora da análise confirmatória."
        ),
        "regras_resolucao_sobreposicao": {
            "especificacao_principal_puro": "Utilizar os cursos com mapeamento estrito 1:1 sem sobreposição para inferência basal incontaminada.",
            "especificacao_agregada": "Em células com cursos sobrepostos no mesmo CNES, consolidar ao nível de especialidade compartilhada ou colapsar no CNES.",
        },
    }
    return resultado


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ponte = construir_dicionario_cbo()

    with OUTPUT_FILE.open("w", encoding="utf-8") as handle:
        json.dump(ponte, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(f"[OK] Ponte CBO congelada com sucesso em: {OUTPUT_FILE}")
    print(f"     Total de cursos: {ponte['total_cursos_pmme']}")
    print(f"     Cursos unívocos: {len(ponte['cursos_estritamente_univocos'])} (Cursos {ponte['cursos_estritamente_univocos']})")
    print(f"     Cursos sobrepostos: {len(ponte['cursos_sobrepostos'])} (Cursos {ponte['cursos_sobrepostos']})")
    print(f"     Total CBOs 6d mapeados: {ponte['total_cbos_distintos']}")


if __name__ == "__main__":
    main()
