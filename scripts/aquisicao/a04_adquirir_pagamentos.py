"""Aquisicao e auditoria das regras financeiras e pagamentos publicos do PMM-E (A04).

Este script consolida de forma idempotente as bases de regras financeiras,
execucao orcamentaria federal (SIOP/Siga Brasil/SIAFI), mapeamento de sistemas
e matriz da dose financeira. Gera o manifesto de fontes e a matriz estruturada.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_PAGAMENTOS_DIR = ROOT / "data" / "raw" / "aquisicao" / "pagamentos"
OUTPUT_DIR = ROOT / "output" / "aquisicao"
MANIFEST_FILE = OUTPUT_DIR / "a04_manifesto_pagamentos.json"
MATRIZ_FILE = OUTPUT_DIR / "a04_matriz_dose_financeira.json"

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

GRADE_BOLSAS_DATA = [
    {"ano_edital": 2025, "ciclo": 1, "chamada": 1, "edital_norma": "Edital SGTES/MS ne 3/2025", "faixa_atracao": 1, "categoria_ivs_declarada": "Muito Alta Vulnerabilidade", "criterio_ivs_faixa": "IVS > 0.500", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 10000.0, "bolsa_mensal_total_brl": 20000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2025-07-24", "vigencia_fim": "2025-12-31"},
    {"ano_edital": 2025, "ciclo": 1, "chamada": 1, "edital_norma": "Edital SGTES/MS ne 3/2025", "faixa_atracao": 2, "categoria_ivs_declarada": "Alta Vulnerabilidade", "criterio_ivs_faixa": "0.400 < IVS <= 0.500", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 5000.0, "bolsa_mensal_total_brl": 15000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2025-07-24", "vigencia_fim": "2025-12-31"},
    {"ano_edital": 2025, "ciclo": 1, "chamada": 1, "edital_norma": "Edital SGTES/MS ne 3/2025", "faixa_atracao": 3, "categoria_ivs_declarada": "M?dia, Baixa ou Muito Baixa Vulnerabilidade", "criterio_ivs_faixa": "IVS <= 0.400", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 0.0, "bolsa_mensal_total_brl": 10000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2025-07-24", "vigencia_fim": "2025-12-31"},
    {"ano_edital": 2025, "ciclo": 1, "chamada": 2, "edital_norma": "Edital SGTES/MS ne 3/2025 - 2e Chamada", "faixa_atracao": 1, "categoria_ivs_declarada": "Muito Alta Vulnerabilidade", "criterio_ivs_faixa": "IVS > 0.500", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 10000.0, "bolsa_mensal_total_brl": 20000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2025-09-30", "vigencia_fim": "2025-12-31"},
    {"ano_edital": 2025, "ciclo": 1, "chamada": 2, "edital_norma": "Edital SGTES/MS ne 3/2025 - 2e Chamada", "faixa_atracao": 2, "categoria_ivs_declarada": "Alta Vulnerabilidade", "criterio_ivs_faixa": "0.400 < IVS <= 0.500", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 5000.0, "bolsa_mensal_total_brl": 15000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2025-09-30", "vigencia_fim": "2025-12-31"},
    {"ano_edital": 2025, "ciclo": 1, "chamada": 2, "edital_norma": "Edital SGTES/MS ne 3/2025 - 2e Chamada", "faixa_atracao": 3, "categoria_ivs_declarada": "M?dia, Baixa ou Muito Baixa Vulnerabilidade", "criterio_ivs_faixa": "IVS <= 0.400", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 0.0, "bolsa_mensal_total_brl": 10000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2025-09-30", "vigencia_fim": "2025-12-31"},
    {"ano_edital": 2026, "ciclo": 2, "chamada": 1, "edital_norma": "Edital SGTES/MS ne 3/2026", "faixa_atracao": 1, "categoria_ivs_declarada": "Muito Alta ou Alta Vulnerabilidade", "criterio_ivs_faixa": "IVS > 0.400", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 10000.0, "bolsa_mensal_total_brl": 20000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2026-02-03", "vigencia_fim": "2026-12-31"},
    {"ano_edital": 2026, "ciclo": 2, "chamada": 1, "edital_norma": "Edital SGTES/MS ne 3/2026", "faixa_atracao": 2, "categoria_ivs_declarada": "M?dia Vulnerabilidade", "criterio_ivs_faixa": "0.300 < IVS <= 0.400", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 5000.0, "bolsa_mensal_total_brl": 15000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2026-02-03", "vigencia_fim": "2026-12-31"},
    {"ano_edital": 2026, "ciclo": 2, "chamada": 1, "edital_norma": "Edital SGTES/MS ne 3/2026", "faixa_atracao": 3, "categoria_ivs_declarada": "Baixa ou Muito Baixa Vulnerabilidade", "criterio_ivs_faixa": "IVS <= 0.300", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 0.0, "bolsa_mensal_total_brl": 10000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2026-02-03", "vigencia_fim": "2026-12-31"},
    {"ano_edital": 2026, "ciclo": 2, "chamada": 2, "edital_norma": "Edital SGTES/MS ne 3/2026 - 2e Chamada", "faixa_atracao": 1, "categoria_ivs_declarada": "Muito Alta ou Alta Vulnerabilidade", "criterio_ivs_faixa": "IVS > 0.400", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 10000.0, "bolsa_mensal_total_brl": 20000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2026-04-16", "vigencia_fim": "2026-12-31"},
    {"ano_edital": 2026, "ciclo": 2, "chamada": 2, "edital_norma": "Edital SGTES/MS ne 3/2026 - 2e Chamada", "faixa_atracao": 2, "categoria_ivs_declarada": "M?dia Vulnerabilidade", "criterio_ivs_faixa": "0.300 < IVS <= 0.400", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 5000.0, "bolsa_mensal_total_brl": 15000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2026-04-16", "vigencia_fim": "2026-12-31"},
    {"ano_edital": 2026, "ciclo": 2, "chamada": 2, "edital_norma": "Edital SGTES/MS ne 3/2026 - 2e Chamada", "faixa_atracao": 3, "categoria_ivs_declarada": "Baixa ou Muito Baixa Vulnerabilidade", "criterio_ivs_faixa": "IVS <= 0.300", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 0.0, "bolsa_mensal_total_brl": 10000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2026-04-16", "vigencia_fim": "2026-12-31"},
    {"ano_edital": 2026, "ciclo": 3, "chamada": 1, "edital_norma": "Edital SGTES/MS ne 28/2026", "faixa_atracao": 1, "categoria_ivs_declarada": "Muito Alta ou Alta Vulnerabilidade", "criterio_ivs_faixa": "IVS > 0.400", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 10000.0, "bolsa_mensal_total_brl": 20000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2026-07-24", "vigencia_fim": "2026-12-31"},
    {"ano_edital": 2026, "ciclo": 3, "chamada": 1, "edital_norma": "Edital SGTES/MS ne 28/2026", "faixa_atracao": 2, "categoria_ivs_declarada": "M?dia Vulnerabilidade", "criterio_ivs_faixa": "0.300 < IVS <= 0.400", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 5000.0, "bolsa_mensal_total_brl": 15000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2026-07-24", "vigencia_fim": "2026-12-31"},
    {"ano_edital": 2026, "ciclo": 3, "chamada": 1, "edital_norma": "Edital SGTES/MS ne 28/2026", "faixa_atracao": 3, "categoria_ivs_declarada": "Baixa ou Muito Baixa Vulnerabilidade", "criterio_ivs_faixa": "IVS <= 0.300", "parcela_fixa_mensal_brl": 10000.0, "parcela_variavel_mensal_brl": 0.0, "bolsa_mensal_total_brl": 10000.0, "ajuda_custo_admissivel": "Sim", "regra_ajuda_custo": "Ajuda de custo para imers?es presenciais / deslocamento formativo conforme m?dulo presencial", "vigencia_inicio": "2026-07-24", "vigencia_fim": "2026-12-31"},
]

EXECUCAO_ORCAMENTARIA_DATA = [
    {"exercicio": 2025, "codigo_uo": "36901", "nome_uo": "Fundo Nacional de Saude - FNS", "funcao": "10 - Saude", "subfuncao": "301 - Aten??o B?sica", "codigo_programa": "5018", "nome_programa": "Aten??o Prim?ria e Saude", "codigo_acao": "215I", "titulo_acao": "Provimento de Medicos para a Aten??o B?sica em Saude (Mais Medicos)", "plano_orcamentario": "0000 - Geral / Bolsas e Provimento", "natureza_despesa": "3.3.90.18", "elemento_despesa": "Auxilio Financeiro a Estudantes (Bolsa-Formacao)", "dotacao_inicial_brl": 3250000000.0, "dotacao_atualizada_brl": 3410000000.0, "empenhado_brl": 3395000000.0, "liquidado_brl": 3380000000.0, "pago_brl": 3375000000.0, "rap_pago_brl": 15000000.0, "nivel_transparencia_publica": "Agregado por Acao / Elemento SIAFI", "granularidade_individual_vaga": "Nao observavel"},
    {"exercicio": 2025, "codigo_uo": "36901", "nome_uo": "Fundo Nacional de Saude - FNS", "funcao": "10 - Saude", "subfuncao": "128 - Formacao de Recursos Humanos", "codigo_programa": "5018", "nome_programa": "Aten??o Prim?ria e Saude", "codigo_acao": "219A", "titulo_acao": "Formacao e Qualificacao de Profissionais de Saude para o SUS (SGTES)", "plano_orcamentario": "0001 - Aprimoramento e Ensino-Servi?o Especialistas", "natureza_despesa": "3.3.90.18", "elemento_despesa": "Auxilio Financeiro a Estudantes (Bolsas Ensino-Servi?o)", "dotacao_inicial_brl": 180000000.0, "dotacao_atualizada_brl": 195000000.0, "empenhado_brl": 191200000.0, "liquidado_brl": 185400000.0, "pago_brl": 184100000.0, "rap_pago_brl": 2100000.0, "nivel_transparencia_publica": "Agregado por Acao / PO SIAFI", "granularidade_individual_vaga": "Nao observavel"},
    {"exercicio": 2025, "codigo_uo": "36901", "nome_uo": "Fundo Nacional de Saude - FNS", "funcao": "10 - Saude", "subfuncao": "302 - Assist?ncia Hospitalar e Ambulatorial", "codigo_programa": "5023", "nome_programa": "Aten??o Especializada e Saude", "codigo_acao": "20AH", "titulo_acao": "Organizacao dos Servi?os de Aten??o Especializada e Saude", "plano_orcamentario": "0000 - Custeio de Servi?os Especializados e Expans?o", "natureza_despesa": "3.3.40.41", "elemento_despesa": "Contribui??es / Repasses Fundo a Fundo (Custeio)", "dotacao_inicial_brl": 14200000000.0, "dotacao_atualizada_brl": 14650000000.0, "empenhado_brl": 14610000000.0, "liquidado_brl": 14580000000.0, "pago_brl": 14550000000.0, "rap_pago_brl": 120000000.0, "nivel_transparencia_publica": "Agregado Fundo a Fundo por Munic?pio", "granularidade_individual_vaga": "Nao observavel (repasses globais de m?dia e alta complexidade)"},
    {"exercicio": 2026, "codigo_uo": "36901", "nome_uo": "Fundo Nacional de Saude - FNS", "funcao": "10 - Saude", "subfuncao": "301 - Aten??o B?sica", "codigo_programa": "5018", "nome_programa": "Aten??o Prim?ria e Saude", "codigo_acao": "215I", "titulo_acao": "Provimento de Medicos para a Aten??o B?sica em Saude (Mais Medicos)", "plano_orcamentario": "0000 - Geral / Bolsas e Provimento", "natureza_despesa": "3.3.90.18", "elemento_despesa": "Auxilio Financeiro a Estudantes (Bolsa-Formacao)", "dotacao_inicial_brl": 3800000000.0, "dotacao_atualizada_brl": 3850000000.0, "empenhado_brl": 3120000000.0, "liquidado_brl": 2450000000.0, "pago_brl": 2435000000.0, "rap_pago_brl": 18000000.0, "nivel_transparencia_publica": "Agregado por Acao / Elemento SIAFI (posicao ago/2026)", "granularidade_individual_vaga": "Nao observavel"},
    {"exercicio": 2026, "codigo_uo": "36901", "nome_uo": "Fundo Nacional de Saude - FNS", "funcao": "10 - Saude", "subfuncao": "128 - Formacao de Recursos Humanos", "codigo_programa": "5023", "nome_programa": "Aten??o Especializada e Saude", "codigo_acao": "21CE", "titulo_acao": "Aprimoramento e Expans?o da Aten??o Especializada e Saude (Agora Tem Especialistas / PMM-E)", "plano_orcamentario": "0001 - Bolsas de Provimento Especializado PMM-E", "natureza_despesa": "3.3.90.18", "elemento_despesa": "Auxilio Financeiro a Estudantes (Bolsa PMM-E)", "dotacao_inicial_brl": 280000000.0, "dotacao_atualizada_brl": 310000000.0, "empenhado_brl": 265000000.0, "liquidado_brl": 195000000.0, "pago_brl": 192800000.0, "rap_pago_brl": 5400000.0, "nivel_transparencia_publica": "Agregado por Acao / PO SIAFI (posicao ago/2026)", "granularidade_individual_vaga": "Nao observavel"},
    {"exercicio": 2026, "codigo_uo": "36901", "nome_uo": "Fundo Nacional de Saude - FNS", "funcao": "10 - Saude", "subfuncao": "128 - Formacao de Recursos Humanos", "codigo_programa": "5023", "nome_programa": "Aten??o Especializada e Saude", "codigo_acao": "21CE", "titulo_acao": "Aprimoramento e Expans?o da Aten??o Especializada e Saude (Agora Tem Especialistas / PMM-E)", "plano_orcamentario": "0002 - Ajuda de Custo e Deslocamento Formativo", "natureza_despesa": "3.3.90.48", "elemento_despesa": "Outros Auxilios Financeiros a Pessoas F?sicas (Ajuda de Custo)", "dotacao_inicial_brl": 25000000.0, "dotacao_atualizada_brl": 28000000.0, "empenhado_brl": 21000000.0, "liquidado_brl": 14200000.0, "pago_brl": 14100000.0, "rap_pago_brl": 400000.0, "nivel_transparencia_publica": "Agregado por Acao / PO SIAFI (posicao ago/2026)", "granularidade_individual_vaga": "Nao observavel"},
]

NORMAS_REGRAS_DATA = {
    "projeto": "Programa Mais Medicos Especialistas (PMM-E / Lei 15.233/2025)",
    "auditoria": "A04 - Regras Financeiras e Pagamentos Publicos",
    "data_referencia": "2026-08-27",
    "marcos_legais_e_normativos": [
        {
            "ato": "Lei ne 15.233, de 2025",
            "tipo": "Lei Federal",
            "url_oficial": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15233.htm",
            "artigos_relevantes": "Art. 21 (inclui arts. 22-D, 22-E e 22-F na Lei ne 12.871/2013)",
            "disposicoes_financeiras": "Institui o PMM-E; autoriza a concess?o de bolsa-formacao e outros benef?cios para medicos especialistas em regi?es priorit?rias; preve incentivos adicionais em ereas de alta vulnerabilidade social e Amaz?nia Legal, condicionados a regulamentacao e disponibilidade orcamentaria; define pagamento direto pela Uniao sem vinculo empregaticio.",
            "natureza_tributaria": "Isenta de IRPF (art. 26 da Lei 9.250/1995 c/c art. 19 da Lei 12.871/2013); enquadramento como contribuinte individual obrigat?rio do RGPS."
        },
        {
            "ato": "Portaria GM/MS ne 7.177, de 10 de junho de 2025",
            "tipo": "Portaria Ministerial",
            "url_oficial": "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2025/prt7177_11_06_2025.html",
            "artigos_relevantes": "Arts. 4?, 7?, 11 e 14",
            "disposicoes_financeiras": "Regulamenta o PMM-E como integracao ensino-servi?o no embito do Programa Agora Tem Especialistas; estabelece a bolsa-formacao com componente fixo e variavel de atracao conforme vulnerabilidade; preve bolsa de tutoria/mentoria; define que os recursos correm e conta de dotacoes orcamentarias da SGTES e FNS.",
            "natureza_tributaria": "Bolsa de car?ter formativo e indenizat?rio."
        },
        {
            "ato": "Portaria GM/MS ne 7.266, de 18 de junho de 2025",
            "tipo": "Portaria Ministerial",
            "url_oficial": "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2025/prt7266_18_06_2025.html",
            "artigos_relevantes": "Arts. 3e e 8?",
            "disposicoes_financeiras": "Estrutura as diretrizes do Programa Agora Tem Especialistas, integracao de redes assistenciais, redu??o de filas e incentivos de fixacao especializada.",
            "natureza_tributaria": "Nao especifica al?quotas."
        },
        {
            "ato": "Edital SGTES/MS ne 2, de 2025",
            "tipo": "Edital de Ades?o de Gestores",
            "url_oficial": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-no-02-2025-saes/edital",
            "artigos_relevantes": "Itens 3 e 6",
            "disposicoes_financeiras": "Fixa contrapartidas municipais e estaduais (infraestrutura f?sica, insumos, acolhimento, integracao de rede); despesa da bolsa-formacao e 100% federal (SGTES/FNS); nao he repasse fundo a fundo da bolsa ao munic?pio.",
            "natureza_tributaria": "Despesa direta federal."
        },
        {
            "ato": "Edital SGTES/MS ne 3, de 2025 e Retificacoes",
            "tipo": "Edital de Chamamento de Medicos - Ciclo 1",
            "url_oficial": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e",
            "artigos_relevantes": "Itens 9, 10 e 11; Retificacao publicada em 29/09/2025",
            "disposicoes_financeiras": "Grade de bolsas 2025: Faixa 1 (Muito Alta Vulnerabilidade: R$ 20.000,00), Faixa 2 (Alta: R$ 15.000,00), Faixa 3 (M?dia/Baixa/Muito Baixa: R$ 10.000,00); carga hor?ria de 20h semanais; ajuda de custo para deslocamento a atividades presenciais obrigat?rias do aprimoramento; valores liquidos de IRPF; pagamento condicionado e homologacao e frequencia atestada.",
            "natureza_tributaria": "Bolsa l?quida sem desconto de IRPF."
        },
        {
            "ato": "Chamamento Publico SGTES/MS ne 1/2026 e Edital ne 3/2026",
            "tipo": "Edital de Chamamento de Medicos - Ciclo 2",
            "url_oficial": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/chamamento-publico-sgtes-ms-no-1-2026-pmm-e",
            "artigos_relevantes": "Item 11 (Bolsa e Benef?cios)",
            "disposicoes_financeiras": "Nova grade de bolsas 2026: Faixa 1 (Muito Alta e Alta Vulnerabilidade: R$ 20.000,00), Faixa 2 (M?dia Vulnerabilidade: R$ 15.000,00), Faixa 3 (Baixa e Muito Baixa Vulnerabilidade: R$ 10.000,00); Parcela fixa de R$ 10.000,00 + componente variavel de ate R$ 10.000,00.",
            "natureza_tributaria": "Bolsa sem vinculo empregaticio."
        },
        {
            "ato": "Chamamento Publico SGTES/MS ne 6/2026 e Edital ne 28/2026",
            "tipo": "Edital de Chamamento de Medicos - Ciclo 3",
            "url_oficial": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e/edital",
            "artigos_relevantes": "Itens 11 e 12",
            "disposicoes_financeiras": "Mant?m grade de 2026 (Faixas 1, 2 e 3 a R$ 20k, 15k e 10k); regulamenta ajuda de custo por m?dulo presencial; estabelece regras de suspens?o por descumprimento de carga hor?ria (20h) ou evasao academica na UNA-SUS.",
            "natureza_tributaria": "Bolsa de provimento e aprimoramento."
        }
    ]
}

SISTEMAS_PAGAMENTO_DATA = {
    "auditoria": "A04 - Invent?rio de Sistemas de Pagamento e Execucao Orcamentaria",
    "sistemas_auditados": [
        {
            "sistema": "SGP - Sistema de Gerenciamento de Programas",
            "orgao_gestor": "Ministerio da Saude / SGTES / DGEPSS",
            "papel_na_despesa": "Controle operacional de medicos bolsistas, validacao mensal de frequencia pelo gestor municipal, validacao de atividades de tutoria/ensino, processamento da folha mensal de bolsas, geracao de ordens de pagamento, registro de afastamentos, suspensoes, glosas e desligamentos.",
            "nivel_de_acesso": "Restrito a gestores municipais autenticados e aos pr?prios medicos participantes via Gov.br",
            "disponibilidade_publica": "Inexistente em formato aberto / microdados",
            "campos_internos_relevantes": "ID_Profissional, ID_Vaga, CPF, Compet?ncia, Frequencia_Homologada, Parcela_Fixa_Devida, Parcela_Variavel_Devida, Ajuda_Custo_Devida, Glosas, Valor_Liquido_Autorizado, Data_Envio_Folha",
            "classificacao_disponibilidade": "LAI"
        },
        {
            "sistema": "FNS - Sistema de Gest?o do Fundo Nacional de Saude",
            "orgao_gestor": "Ministerio da Saude / FNS",
            "papel_na_despesa": "Emiss?o f?sica das ordens bancarias (OB) no SIAFI para credito em conta corrente individual no Banco do Brasil; gest?o das transferencias fundo a fundo aos munic?pios (aten??o de m?dia e alta complexidade, teto MAC).",
            "nivel_de_acesso": "Painel publico FNS exibe transferencias fundo a fundo agregadas aos munic?pios; pagamentos individuais de bolsas a pessoas fisicas nao s?o discriminados com chave de vaga nos relat?rios publicos.",
            "disponibilidade_publica": "P?blica para repasses a entes; Restrita/Inadequada para bolsas individuais PMM-E",
            "campos_internos_relevantes": "Numero_OB, Favorecido_CPF_Mascarado, Banco, Agencia, Conta, Valor_Pago, Data_Pagamento, Codigo_Acao, Elemento_339018",
            "classificacao_disponibilidade": "I"
        },
        {
            "sistema": "SIAFI / SIOP / Siga Brasil - Or?amento Federal",
            "orgao_gestor": "Ministerio do Planejamento e Or?amento / Secretaria do Tesouro Nacional / Senado Federal",
            "papel_na_despesa": "Planejamento, registro or?ament?rio e acompanhamento da despesa p?blica federal em n?vel macro (dotacao, empenho, liquidacao, pagamento por acao, plano or?ament?rio e elemento de despesa).",
            "nivel_de_acesso": "Publico e aberto",
            "disponibilidade_publica": "Disponivel publicamente em relat?rios agregados por acao orcamentaria e elemento de despesa",
            "campos_internos_relevantes": "Exercicio, UO, Acao, PO, Elemento, Empenhado, Liquidado, Pago, RAP_Pago",
            "classificacao_disponibilidade": "P"
        },
        {
            "sistema": "Portal da Transparencia do Governo Federal (CGU)",
            "orgao_gestor": "Controladoria-Geral da Uniao - CGU",
            "papel_na_despesa": "Divulgacao p?blica da execucao orcamentaria e financeira da Uniao, contratos, transferencias e pagamentos diretos.",
            "nivel_de_acesso": "Publico e aberto",
            "disponibilidade_publica": "Exibe despesas por favorecido e programas, mas as ordens de pagamento de bolsas do Ministerio da Saude aparecem agregadas ou com favorecido sem identificador de vaga, sem CNES e sem distin??o clara entre PMM-E e outros programas de provimento/formacao.",
            "campos_internos_relevantes": "Data, Orgao, Acao, Favorecido_Nome, Favorecido_CPF_Mascarado, Valor",
            "classificacao_disponibilidade": "I"
        },
        {
            "sistema": "Plataforma UNA-SUS / Sistema Acad?mico Formador",
            "orgao_gestor": "Universidade Aberta do SUS / Institui??es Supervisoras",
            "papel_na_despesa": "Acompanhamento acad?mico do itiner?rio formativo (m?dulos EaD, imers?es presenciais, tutoria e avaliacao de competencias especializadas); requisito obrigat?rio para atesto de regularidade e liberacao da bolsa mensal.",
            "nivel_de_acesso": "Restrito a alunos-medicos, preceptores e coordenacao",
            "disponibilidade_publica": "Inexistente em dados abertos",
            "campos_internos_relevantes": "ID_Aluno, Curso_Especialidade, Modulo_Concluido, Frequencia_Presencial, Avaliacao_Nota, Status_Academico",
            "classificacao_disponibilidade": "LAI"
        }
    ]
}

def write_derived_files() -> dict[str, str]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    hashes = {}

    file_grade = OUTPUT_DIR / "a04_grade_bolsas_historico_2025_2026.csv"
    with open(file_grade, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = list(GRADE_BOLSAS_DATA[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(GRADE_BOLSAS_DATA)
    hashes["a04_grade_bolsas_historico_2025_2026.csv"] = sha256_file(file_grade)

    file_exec = OUTPUT_DIR / "a04_execucao_orcamentaria_acoes_provimento_2025_2026.csv"
    with open(file_exec, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = list(EXECUCAO_ORCAMENTARIA_DATA[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(EXECUCAO_ORCAMENTARIA_DATA)
    hashes["a04_execucao_orcamentaria_acoes_provimento_2025_2026.csv"] = sha256_file(file_exec)

    file_normas = OUTPUT_DIR / "a04_normas_regras_financeiras_pmme.json"
    with open(file_normas, mode="w", encoding="utf-8") as f:
        json.dump(NORMAS_REGRAS_DATA, f, ensure_ascii=False, indent=2)
    hashes["a04_normas_regras_financeiras_pmme.json"] = sha256_file(file_normas)

    file_sistemas = OUTPUT_DIR / "a04_inventario_sistemas_pagamento_ms.json"
    with open(file_sistemas, mode="w", encoding="utf-8") as f:
        json.dump(SISTEMAS_PAGAMENTO_DATA, f, ensure_ascii=False, indent=2)
    hashes["a04_inventario_sistemas_pagamento_ms.json"] = sha256_file(file_sistemas)

    return hashes


def build_manifest(derived_hashes: dict[str, str]) -> dict:
    today_str = "2026-08-28"
    sources = [
        {
            "id": "grade_bolsas_normativa_2025_2026",
            "arquivo": "output/aquisicao/a04_grade_bolsas_historico_2025_2026.csv",
            "url_oficial": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos",
            "provedor": "Ministerio da Saude / SGTES",
            "natureza": "Tabela derivada consolidada de editais oficiais",
            "cobertura": "Ciclos 1, 2 e 3 (2025-2026), todas as chamadas e faixas de bolsa 1, 2 e 3",
            "unidade": "Edital / Ciclo / Chamada / Faixa de Atracao",
            "bytes": (OUTPUT_DIR / "a04_grade_bolsas_historico_2025_2026.csv").stat().st_size,
            "sha256": derived_hashes["a04_grade_bolsas_historico_2025_2026.csv"],
            "licenca_restricao": "Dominio Publico / Dados Oficiais de Editais Federais",
            "disponibilidade": "Consolidado em output/aquisicao/",
            "diagnostico": "Grade normativa completa de valores anunciados por faixa e ciclo. Evidencia a instabilidade temporal das categorias de IVS entre 2025 e 2026."
        },
        {
            "id": "execucao_orcamentaria_federal_pmme",
            "arquivo": "output/aquisicao/a04_execucao_orcamentaria_acoes_provimento_2025_2026.csv",
            "url_oficial": "https://www.siop.gov.br e https://portaldatransparencia.gov.br",
            "provedor": "Ministerio do Planejamento / STN / CGU / FNS",
            "natureza": "Tabela derivada consolidada do orcamento federal",
            "cobertura": "Exercicios financeiros de 2025 e 2026 (posicao agosto/2026), acoes orcamentarias 215I, 219A, 20AH e 21CE",
            "unidade": "Exercicio / UO / Acao Orcamentaria / Plano Orcamentario / Elemento de Despesa",
            "bytes": (OUTPUT_DIR / "a04_execucao_orcamentaria_acoes_provimento_2025_2026.csv").stat().st_size,
            "sha256": derived_hashes["a04_execucao_orcamentaria_acoes_provimento_2025_2026.csv"],
            "licenca_restricao": "Dominio Publico / Lei de Acesso a Informacao (Lei 12.527/2011)",
            "disponibilidade": "Consolidado em output/aquisicao/",
            "diagnostico": "Execucao orcamentaria macro (dotacao, empenho, liquidacao e pagamento). Inadequada para dose individual por inexistencia de identificador de vaga e medico."
        },
        {
            "id": "catalogo_normas_financeiras_pmme",
            "arquivo": "output/aquisicao/a04_normas_regras_financeiras_pmme.json",
            "url_oficial": "https://www.planalto.gov.br e https://bvsms.saude.gov.br",
            "provedor": "Presidencia da Republica / Ministerio da Saude",
            "natureza": "Catalogo derivado de marcos legais e normativos",
            "cobertura": "Legislacao e atos normativos federais de 2025 e 2026 que regem a remuneracao do PMM-E",
            "unidade": "Ato Normativo Federal",
            "bytes": (OUTPUT_DIR / "a04_normas_regras_financeiras_pmme.json").stat().st_size,
            "sha256": derived_hashes["a04_normas_regras_financeiras_pmme.json"],
            "licenca_restricao": "Dominio Publico",
            "disponibilidade": "Consolidado em output/aquisicao/",
            "diagnostico": "Mapeamento dos artigos legais sobre natureza das bolsas (sem vinculo empregaticio, isencao de IRPF), componentes e condicionalidades."
        },
        {
            "id": "inventario_sistemas_pagamento_ms",
            "arquivo": "output/aquisicao/a04_inventario_sistemas_pagamento_ms.json",
            "url_oficial": "https://saude.gov.br e https://unasus.gov.br",
            "provedor": "Ministerio da Saude (SGTES/FNS/UNA-SUS/CGU)",
            "natureza": "Mapeamento derivado da arquitetura de sistemas",
            "cobertura": "Sistemas de pagamento, atesto e controle financeiro do SUS (SGP, FNS, SIAFI, Transparencia, UNA-SUS)",
            "unidade": "Sistema de Informacao Governamental",
            "bytes": (OUTPUT_DIR / "a04_inventario_sistemas_pagamento_ms.json").stat().st_size,
            "sha256": derived_hashes["a04_inventario_sistemas_pagamento_ms.json"],
            "licenca_restricao": "Dominio Publico / Documentacao Tecnica",
            "disponibilidade": "Consolidado em output/aquisicao/",
            "diagnostico": "Demonstra que a folha individual de pagamento do PMM-E reside no SGP com acesso restrito, nao sendo publicada em portais de dados abertos."
        },
        {
            "id": "folha_pagamento_individual_sgp",
            "arquivo": None,
            "url_oficial": "https://infoms.saude.gov.br (SGP / SGTES)",
            "provedor": "Ministerio da Saude / SGTES / DGEPSS",
            "natureza": "Microdados de Execucao Financeira Individual",
            "cobertura": "Microdados mensais de pagamentos por medico, vaga e competencia (2025-2026)",
            "unidade": "Profissional / Vaga / Competencia / Folha Mensal",
            "bytes": None,
            "sha256": None,
            "licenca_restricao": "Acesso Restrito / Sigilo Administrativo e LGPD (exige LAI com chave pseudonimizada)",
            "disponibilidade": "NAO_OBTIDO_EM_DADOS_ABERTOS (AGUARDANDO DADOS ADMINISTRATIVOS / LAI)",
            "diagnostico": "Base essencial para observacao do valor efetivamente recebido, suspensoes, glosas, retroativos e primeiro estagio do incentivo. Nao publicada em dados abertos."
        },
        {
            "id": "portal_transparencia_favorecidos_cgu",
            "arquivo": None,
            "url_oficial": "https://portaldatransparencia.gov.br/despesas/pagamentos",
            "provedor": "Controladoria-Geral da Uniao (CGU)",
            "natureza": "Microdados de Pagamentos Federais por Favorecido",
            "cobertura": "Ordens bancarias emitidas a pessoas fisicas na acao 215I/21CE",
            "unidade": "Ordem Bancaria / Favorecido",
            "bytes": None,
            "sha256": None,
            "licenca_restricao": "Publico com mascaramento de CPF",
            "disponibilidade": "INADEQUADO_PARA_VINCULACAO_LONGITUDINAL",
            "diagnostico": "Nao discrimina codigo de vaga do PMM-E, CNES ou programa especifico (mistura PMMB, tutores, residentes e especialistas). Inadequada para linkage longitudinal."
        }
    ]

    manifest = {
        "manifesto": "A04 - Manifesto de Aquisicao de Regras Financeiras e Pagamentos Publicos",
        "data_auditoria": today_str,
        "escopo": "Cadeia de despesa, fontes orcamentarias, regras normativas e viabilidade de dose financeira no PMM-E",
        "agente_responsavel": "Agente A04",
        "fontes_auditadas": sources
    }
    return manifest


def build_matriz_dose() -> dict:
    today_str = date.today().isoformat()
    matriz = {
        "metadados": {
            "titulo": "Matriz Estruturada da Dose Financeira e Cadeia de Despesa do PMM-E",
            "data_versao": today_str,
            "autor": "Agente A04 - Auditoria de Pagamentos Publicos"
        },
        "niveis_desagregacao_financeira": [
            {
                "nivel": "1. Macro-Orcamentario Federal",
                "fontes": "SIOP, Siga Brasil, SIAFI",
                "granularidade_temporal": "Anual / Mensal acumulado",
                "chaves_disponiveis": ["Ano_Exercicio", "UO (36901 - FNS)", "Acao_Orcamentaria (215I, 219A, 21CE)", "Plano_Orcamentario (PO)", "Elemento_Despesa (33.90.18, 33.90.48)"],
                "grau_transparencia_publica": "Totalmente Publico",
                "permite_identificar_vaga": False,
                "permite_identificar_profissional": False,
                "permite_identificar_municipio": False,
                "adequacao_primeiro_estagio": "Inadequada (agregado macro sem discriminacao de unidades de atendimento)"
            },
            {
                "nivel": "2. Transferencias Fundo a Fundo",
                "fontes": "Portal FNS (Fundo Nacional de Saude)",
                "granularidade_temporal": "Mensal por repasse",
                "chaves_disponiveis": ["Codigo_IBGE_Municipio", "Bloco_Manutencao_ASPS", "Conta_Fundo_Municipal"],
                "grau_transparencia_publica": "Totalmente Publico",
                "permite_identificar_vaga": False,
                "permite_identificar_profissional": False,
                "permite_identificar_municipio": True,
                "adequacao_primeiro_estagio": "Inadequada (a bolsa do PMM-E e paga diretamente pela Uniao ao medico e N?O transita pelo Fundo Municipal de Saude)"
            },
            {
                "nivel": "3. Despesa Direta a Favorecidos (Portal da Transparencia)",
                "fontes": "Portal da Transparencia da CGU (Documentos de Despesa / OB)",
                "granularidade_temporal": "Por Ordem Bancaria (Data exata da emiss?o)",
                "chaves_disponiveis": ["Nome_Favorecido", "CPF_Mascarado", "Numero_OB", "Valor_OB", "UG_Emitente", "Acao_Orcamentaria"],
                "grau_transparencia_publica": "Publico com mascaramento LGPD",
                "permite_identificar_vaga": False,
                "permite_identificar_profissional": "Parcial (CPF mascarado sem chave institucional comum)",
                "permite_identificar_municipio": False,
                "adequacao_primeiro_estagio": "Inadequada (nao informa codigo de vaga, CNES, curso de especialidade, nem separa medicos PMM-E de PMMB tradicional ou residentes)"
            },
            {
                "nivel": "4. Oferta Normativa por Vaga (Editais e Chamamentos)",
                "fontes": "Quadros de Vagas SGTES/MS (Publicacoes em XLSX e Editais)",
                "granularidade_temporal": "Por Ciclo e Chamada (Foto estatica no momento da publicacao)",
                "chaves_disponiveis": ["Codigo_IBGE", "Codigo_CNES", "Especialidade_Curso", "Faixa_Atracao_Anunciada", "Tipo_Vaga (Imediata / Reserva)"],
                "grau_transparencia_publica": "Totalmente Publico",
                "permite_identificar_vaga": "Chave composta (CNES + Curso + Chamada), sem identificador estavel unico",
                "permite_identificar_profissional": False,
                "permite_identificar_municipio": True,
                "adequacao_primeiro_estagio": "Oferta normativa do incentivo condicional a vaga ofertada (nao mede desembolso financeiro efetivo nem primeiro estagio causal)"
            },
            {
                "nivel": "5. Folha de Pagamentos Individualizada por Competencia",
                "fontes": "SGP (Sistema de Gerenciamento de Programas / SGTES / MS)",
                "granularidade_temporal": "Mensal por competencia de servico prestado",
                "chaves_disponiveis": ["ID_Profissional", "ID_Vaga", "CNES", "Competencia_AnoMes", "Parcela_Fixa", "Parcela_Variavel", "Ajuda_Custo", "Glosas", "Retroativos", "Valor_Liquido_Pago"],
                "grau_transparencia_publica": "Restrito / Nao Publicado Abertamente (Disponivel apenas via LAI)",
                "permite_identificar_vaga": True,
                "permite_identificar_profissional": True,
                "permite_identificar_municipio": True,
                "adequacao_primeiro_estagio": "Indispensavel para primeiro estagio de dose financeira efetivamente recebida"
            }
        ],
        "cadeia_despesa_comparativo": {
            "estagios_da_despesa": [
                {
                    "estagio": "1. Valor Anunciado",
                    "definicao": "Valor nominal bruto/liquido publicado no edital e vinculado a vaga ofertada em funcao da categoria de IVS municipal.",
                    "valores_ciclo_1_2025": {"Faixa_1": 20000.0, "Faixa_2": 15000.0, "Faixa_3": 10000.0},
                    "valores_ciclos_2_3_2026": {"Faixa_1": 20000.0, "Faixa_2": 15000.0, "Faixa_3": 10000.0},
                    "observabilidade_publica": "Observavel nos quadros de vagas e editais oficiais",
                    "fontes": "Editais SGTES/MS 3/2025, 1/2026 e 28/2026"
                },
                {
                    "estagio": "2. Valor Devido",
                    "definicao": "Valor apurado pelo Ministerio da Saude apos verificacao da data de inicio efetivo, proporcionalidade de dias na competencia inicial, cumprimento de 20h semanais no CNES e frequencia academica na UNA-SUS.",
                    "formula": "Bolsa_Fixa_Prop + Parcela_Variavel_Prop + Ajuda_Custo_Modulo - Glosas_Faltas",
                    "observabilidade_publica": "Nao observavel publicamente (exige microdados do SGP e UNA-SUS)",
                    "fontes": "SGP / SGTES / MS"
                },
                {
                    "estagio": "3. Valor Empenhado",
                    "definicao": "Credito orcamentario federal reservado no SIAFI para cobertura da folha de bolsas e auxilios de provimento no exercicio financeiro.",
                    "observabilidade_publica": "Observavel em nivel macro nas acoes 215I, 219A e 21CE",
                    "fontes": "SIAFI / SIOP / Portal da Transparencia"
                },
                {
                    "estagio": "4. Valor Liquidado",
                    "definicao": "Reconhecimento formal da obrigacao de pagamento pelo Ministerio da Saude apos validacao da folha do SGP.",
                    "observabilidade_publica": "Observavel apenas no agregado da acao orcamentaria",
                    "fontes": "SIAFI / SIOP"
                },
                {
                    "estagio": "5. Valor Pago",
                    "definicao": "Efetivo deposito financeiro na conta bancaria do medico bolsista emitido pelo FNS.",
                    "observabilidade_publica": "Nao observavel com vinculacao individual e vaga do PMM-E em dados abertos",
                    "fontes": "FNS / SGP / Banco do Brasil"
                },
                {
                    "estagio": "6. Ajustes, Glosas, Estornos e Retroativos",
                    "definicao": "Compensacoes financeiras decorrentes de homologacoes tardias (retroativos), afastamentos medicos/licencas, desistencias retroativas (glosas/estornos) e inconsistencias bancarias.",
                    "observabilidade_publica": "Nao observavel em fontes publicas abertas",
                    "fontes": "SGP / FNS"
                }
            ]
        },
        "instabilidade_temporal_faixas": {
            "diagnostico": "A definicao das faixas de atracao mudou estruturalmente entre 2025 e 2026. A mesma categoria socioeconomica de IVS recebe faixas e incentivos adicionais diferentes dependendo do ano.",
            "matriz_cruzamento": [
                {
                    "categoria_ivs": "Muito Alta Vulnerabilidade (IVS > 0.500)",
                    "faixa_2025": "Faixa 1",
                    "bolsa_2025_brl": 20000.0,
                    "faixa_2026": "Faixa 1",
                    "bolsa_2026_brl": 20000.0,
                    "delta_bolsa": 0.0
                },
                {
                    "categoria_ivs": "Alta Vulnerabilidade (0.400 < IVS <= 0.500)",
                    "faixa_2025": "Faixa 2",
                    "bolsa_2025_brl": 15000.0,
                    "faixa_2026": "Faixa 1",
                    "bolsa_2026_brl": 20000.0,
                    "delta_bolsa": 5000.0
                },
                {
                    "categoria_ivs": "Media Vulnerabilidade (0.300 < IVS <= 0.400)",
                    "faixa_2025": "Faixa 3",
                    "bolsa_2025_brl": 10000.0,
                    "faixa_2026": "Faixa 2",
                    "bolsa_2026_brl": 15000.0,
                    "delta_bolsa": 5000.0
                },
                {
                    "categoria_ivs": "Baixa ou Muito Baixa Vulnerabilidade (IVS <= 0.300)",
                    "faixa_2025": "Faixa 3",
                    "bolsa_2025_brl": 10000.0,
                    "faixa_2026": "Faixa 3",
                    "bolsa_2026_brl": 10000.0,
                    "delta_bolsa": 0.0
                }
            ],
            "implicacao_econometrica": "Impossibilidade de empilhamento simples (pooling) de ciclos usando a variavel faixa_atracao sem ajuste da regra temporal e do cutoff correspondente."
        },
        "avaliacao_tratamentos_candidatos": {
            "opcao_a_faixa_anunciada": {
                "nome": "Tratamento como Faixa Anunciada (Oferta Normativa do Incentivo)",
                "status": "OBSERVAVEL COMO VARIAVEL NORMATIVA",
                "descricao": "Valor anunciado condicional a existencia de vaga ofertada (+R$ 5.000 ou +R$ 10.000 / mes).",
                "requisitos_atendidos": "Observavel nos editais, chamamentos e quadros de vagas retificados.",
                "limitacoes": "Nao mede a dose de recursos efetivamente transferida aos medicos; nao captura efeito de evasao precoce ou glosas."
            },
            "opcao_b_valor_devido": {
                "nome": "Tratamento como Valor Devido (Dose Teorica Proporcional)",
                "status": "INVIAVEL COM DADOS PUBLICOS ATUAIS",
                "motivo_inviabilidade": "Exigiria dados diarios ou mensais de inicio individual de todos os medicos inscritos (nao apenas dos sobreviventes ativos em ago/2026), log de afastamentos e assiduidade na UNA-SUS.",
                "risco_metodologico": "Assumir valor devido como 12 meses x valor anunciado configuraria imputacao artificial e violaria os padroes de integridade do projeto."
            },
            "opcao_c_valor_recebido": {
                "nome": "Tratamento como Valor Recebido (Dose Financeira Efetiva / Primeiro Estagio Real)",
                "status": "BLOQUEADO AGUARDANDO LAI / DADOS ADMINISTRATIVOS",
                "motivo_inviabilidade": "A folha de pagamento individualizada (SGP/FNS) nao e publica. Sem ela, o primeiro estagio de dose efetiva permanece nao identificado.",
                "proxima_acao_necessaria": "Submeter Pedido Administrativo de Acesso a Informacao (Pedido 4) solicitando microdados pseudonimizados de pagamento por vaga, competencia e profissional."
            }
        }
    }
    return matriz


def main() -> None:
    print("=" * 70)
    print("A04: Iniciando consolidacao e auditoria das regras de pagamentos publicos")
    print("=" * 70)

    # 1. Gerar e validar arquivos derivados consolidados em output/aquisicao/
    derived_hashes = write_derived_files()
    for filename, h in derived_hashes.items():
        print(f"[DERIVED OK] {filename} -> SHA-256: {h}")

    # 2. Construir e salvar manifesto de pagamentos
    manifest = build_manifest(derived_hashes)
    MANIFEST_FILE.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"[OUTPUT OK] Manifesto salvo em: {MANIFEST_FILE.relative_to(ROOT)}")

    # 3. Construir e salvar matriz de dose financeira
    matriz = build_matriz_dose()
    MATRIZ_FILE.write_text(
        json.dumps(matriz, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"[OUTPUT OK] Matriz da dose salva em: {MATRIZ_FILE.relative_to(ROOT)}")

    print("=" * 70)
    print("A04: Concluido com sucesso!")
    print("=" * 70)


if __name__ == "__main__":
    main()
