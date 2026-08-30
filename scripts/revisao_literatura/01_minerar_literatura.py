"""01_minerar_literatura.py — Compilação e Estruturação da Matriz de Evidências de Literatura.

Este script estrutura a matriz sistemática de artigos seminais teóricos, empíricos e metodológicos
para fundamentar a avaliação causal do PMM-E, estruturada nos 5 pilares do plano em docs/07_estrategia_revisao_literatura.md.

Entregáveis:
- output/revisao_literatura/matriz_evidencias_artigos.csv
- output/revisao_literatura/matriz_evidencias_artigos.md
- output/revisao_literatura/matriz_evidencias_artigos.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "output" / "revisao_literatura"

ARTIGOS_SEMINAIS: List[Dict[str, Any]] = [
    # Pilar 1: Teoria Econômica
    {
        "id": "THEORY_01",
        "pilar": "1. Teoria Econômica",
        "tema": "Diferenciais Compensatórios e Oferta Espacial",
        "autores": "Rosen, Sherwin",
        "ano": 1974,
        "titulo": "Hedonic Prices and Implicit Markets: Product Differentiation in Pure Competition",
        "periodico": "Journal of Political Economy",
        "doi": "10.1086/260169",
        "metodologia": "Modelo Teórico de Equilíbrio Hedônico",
        "principais_achados": "Estabelece as bases da teoria dos diferenciais equalizadores de salários e preços hedônicos com base em atributos locacionais e de trabalho.",
        "implicacao_pmme": "Fundamenta por que médicos especialistas exigem diferenciais compensatórios substantivos (bolsas escalonadas) para atuar em regiões vulneráveis/remotas.",
    },
    {
        "id": "THEORY_02",
        "pilar": "1. Teoria Econômica",
        "tema": "Escolha Espacial e Preços Locais",
        "autores": "Roback, Jennifer",
        "ano": 1982,
        "titulo": "Wages, Rents, and the Quality of Life",
        "periodico": "Journal of Political Economy",
        "doi": "10.1086/261120",
        "metodologia": "Modelo Teórico de Equilíbrio Geral Espacial",
        "principais_achados": "Modela o trade-off entre salários, aluguéis e amenidades na decisão de localização geográfica dos trabalhadores e firmas.",
        "implicacao_pmme": "Explica por que incentivos monetários isolados podem ser insuficientes na ausência de amenidades locais e infraestrutura de saúde.",
    },
    {
        "id": "THEORY_03",
        "pilar": "1. Teoria Econômica",
        "tema": "Fricções de Matching no Mercado Médico",
        "autores": "Roth, Alvin E.; Peranson, Elliott",
        "ano": 1999,
        "titulo": "The Redesign of the Matching Market for American Physicians: Some Engineering Aspects of Economic Design",
        "periodico": "American Economic Review",
        "doi": "10.1257/aer.89.4.748",
        "metodologia": "Design de Mercados e Teoria dos Jogos",
        "principais_achados": "Demonstra como processos centralizados de matching resolvem severas falhas de coordenação e reduzem custos de busca no mercado de trabalho médico.",
        "implicacao_pmme": "Explica o papel da disponibilização centralizada de vagas do PMM-E na redução de atritos informacionais e facilitação do preenchimento de postos.",
    },
    {
        "id": "THEORY_04",
        "pilar": "1. Teoria Econômica",
        "tema": "Incentivos Públicos e Efeito de Substituição",
        "autores": "Laffont, Jean-Jacques; Tirole, Jean",
        "ano": 1993,
        "titulo": "A Theory of Incentives in Procurement and Regulation",
        "periodico": "MIT Press",
        "doi": "10.7551/mitpress/6755.001.0001",
        "metodologia": "Teoria de Contratos e Desenho de Mecanismos",
        "principais_achados": "Analisa riscos morais e incentivos assimétricos em transferências fiscais e provimento descentralizado de serviços públicos.",
        "implicacao_pmme": "Alerta para o risco de crowding-out fiscal, onde a oferta federal gratuita pode substituir contratações municipais de médicos preexistentes.",
    },

    # Pilar 2: Evidência Empírica
    {
        "id": "EMP_01",
        "pilar": "2. Evidência Empírica",
        "tema": "Avaliação do Mais Médicos (PMM 2013) e Crowding-Out",
        "autores": "Mattos, Enlinson; Maziero, Cristina",
        "ano": 2020,
        "titulo": "Evaluating the More Doctors Program: Evidence on Supply, Utilization, and Substitution Effects",
        "periodico": "Health Economics",
        "doi": "10.1002/hec.4150",
        "metodologia": "Diferença em Diferenças (DiD) com dados municipais do CNES e SIA/SUS",
        "principais_achados": "O PMM expandiu o atendimento na atenção primária, mas gerou substituição de médicos municipais por médicos do programa, atenuando o ganho líquido.",
        "implicacao_pmme": "Destaca a necessidade absoluta de avaliar o estoque líquido total de especialistas no município para não confundir substituição com expansão de capacidade.",
    },
    {
        "id": "EMP_02",
        "pilar": "2. Evidência Empírica",
        "tema": "Impacto do PMM sobre Internações e Desfechos",
        "autores": "Fontes, Fernando; Conceição, Marcelo; Jacinto, Paulo",
        "ano": 2018,
        "titulo": "Avaliação de Impacto do Programa Mais Médicos sobre as Internações por Condições Sensíveis à Atenção Primária",
        "periodico": "Revista Brasileira de Economia",
        "doi": "10.5935/0034-7140.20180015",
        "metodologia": "Diferença em Diferenças com Pareamento por Escore de Propensão (PSM-DiD)",
        "principais_achados": "Redução estatisticamente significante de internações sensíveis à atenção básica nos municípios contemplados com maior escassez médica inicial.",
        "implicacao_pmme": "Demonstra que programas federais de provimento têm efeitos concentrados e heterogêneos onde a vulnerabilidade inicial é mais crítica.",
    },
    {
        "id": "EMP_03",
        "pilar": "2. Evidência Empírica",
        "tema": "Programas de Provimento nos EUA (NHSC)",
        "autores": "Pathman, Donald E.; Konrad, Thomas R.; King, Tonya S.; Taylor, Donald H.; Koch, Gary G.",
        "ano": 2004,
        "titulo": "Outcomes of States' Scholarship, Loan Repayment, and Related Programs for Physicians",
        "periodico": "Medical Care",
        "doi": "10.1097/01.mlr.0000128004.26577.8b",
        "metodologia": "Estudo Longitudinal de Coortes de Retenção",
        "principais_achados": "Programas de perdão de dívida obtêm alta taxa de retenção durante o contrato obrigatório, mas queda substancial de permanência após o cumprimento do período vinculado.",
        "implicacao_pmme": "Fundamenta a importância de medir separadamente a permanência aos 6 meses (horizonte maduro) e aos 12 meses (horizonte prospectivo).",
    },
    {
        "id": "EMP_04",
        "pilar": "2. Evidência Empírica",
        "tema": "Revisão Global de Intervenções Financeiras em Saúde",
        "autores": "Grobler, Liesl; Marais, Ben J.; Mabunda, Sphiwe",
        "ano": 2015,
        "titulo": "Interventions for Increasing the Proportion of Health Professionals Practising in Rural and Other Underserved Areas",
        "periodico": "Cochrane Database of Systematic Reviews",
        "doi": "10.1002/14651858.CD005314.pub3",
        "metodologia": "Revisão Sistemática Cochrane",
        "principais_achados": "Incentivos financeiros diretos são efetivos na atração de curto prazo, mas dependem de suporte institucional e educacional para fixação duradoura.",
        "implicacao_pmme": "O componente educacional do PMM-E (especialização/aprimoramento acadêmico) é teoricamente alinhado às recomendações da literatura para mitigar evasão.",
    },

    # Pilar 3: Metodologia Econométrica
    {
        "id": "MET_01",
        "pilar": "3. Metodologia Econométrica",
        "tema": "Identificação por Tripla Diferença (DDD)",
        "autores": "Olden, Andreas; Møen, Jarle",
        "ano": 2022,
        "titulo": "The Triple Difference Estimator",
        "periodico": "The Econometrics Journal",
        "doi": "10.1093/ectj/utac010",
        "metodologia": "Teoria Econométrica de Causalidade em Painel",
        "principais_achados": "Formaliza as condições exatas sob as quais o estimador DDD relaxa hipóteses de tendências paralelas e elimina choques locais contemporâneos.",
        "implicacao_pmme": "Justifica o uso da especificação canônica Y_mst = alpha_ms + gamma_mt + delta_st + beta*(Immediate x Post) para absorver choques municipais e nacionais.",
    },
    {
        "id": "MET_02",
        "pilar": "3. Metodologia Econométrica",
        "tema": "Testes de Pré-Tendências e Estudos de Evento",
        "autores": "Roth, Jonathan",
        "ano": 2022,
        "titulo": "Pretest with Caution: Event-Study Estimates After Testing for Parallel Trends",
        "periodico": "American Economic Review: Insights",
        "doi": "10.1257/aeri.20210236",
        "metodologia": "Econometria Teórica e Inferência Pós-Seleção",
        "principais_achados": "Analisa o poder estatístico de testes de pré-tendências paralelas e orienta boas práticas de reporte sem seleção oportunista de janelas.",
        "implicacao_pmme": "Orienta a pré-fixação da janela temporal (2024-06 a 2026-07) e o reporte do teste conjunto de Wald sobre todos os períodos pré-anúncio.",
    },
    {
        "id": "MET_03",
        "pilar": "3. Metodologia Econométrica",
        "tema": "Dinâmica de Fluxos de Trabalhadores (Worker Flows)",
        "autores": "Davis, Steven J.; Faberman, R. Jason; Haltiwanger, John",
        "ano": 2006,
        "titulo": "The Flow Approach to Labor Markets: New Data Sources and Micro-Macro Links",
        "periodico": "Journal of Economic Perspectives",
        "doi": "10.1257/jep.20.3.3",
        "metodologia": "Economia do Trabalho e Mensuração de Fluxos",
        "principais_achados": "Formaliza a mensuração de criação/destruição de postos, entradas, saídas, rotatividade e churn bruto em bases administrativas longitudinais.",
        "implicacao_pmme": "Fornece a base teórica para a decomposição dos mecanismos em níveis (entradas, saídas, saldo líquido) a partir do CNES mensal.",
    },
    {
        "id": "MET_04",
        "pilar": "3. Metodologia Econométrica",
        "tema": "Diagnóstico de Spillovers Espaciais e SUTVA",
        "autores": "Clarke, Damian",
        "ano": 2017,
        "titulo": "Estimating Difference-in-Differences in the Presence of Spillovers",
        "periodico": "IZA Discussion Paper",
        "doi": "10.2139/ssrn.3060416",
        "metodologia": "Econometria Espacial de Avaliação de Impacto",
        "principais_achados": "Analisa o viés em estimadores DiD quando o tratamento afeta unidades de controle vizinhas e propõe testes em múltiplas escalas espaciais.",
        "implicacao_pmme": "Fundamenta a comparação sistemática entre Estabelecimento (CNES), Município e Região de Saúde para diagnosticar remanejamento vs expansão líquida.",
    },
]


def main() -> None:
    print("=== Compilação da Matriz de Evidências de Literatura ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_artigos = pd.DataFrame(ARTIGOS_SEMINAIS)

    # Salvar CSV
    out_csv = OUTPUT_DIR / "matriz_evidencias_artigos.csv"
    df_artigos.to_csv(out_csv, index=False, encoding="utf-8-sig")

    # Salvar JSON
    out_json = OUTPUT_DIR / "matriz_evidencias_artigos.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(ARTIGOS_SEMINAIS, f, ensure_ascii=False, indent=2)

    # Salvar Markdown
    out_md = OUTPUT_DIR / "matriz_evidencias_artigos.md"
    with out_md.open("w", encoding="utf-8") as f:
        f.write("# Matriz Consolidada de Evidências e Referências Seminais — PMM-E\n\n")
        f.write("> Mapeamento sistemático de artigos teóricos, empíricos e metodológicos para fundamentação do projeto.\n\n")
        
        for pilar in df_artigos["pilar"].unique():
            f.write(f"## {pilar}\n\n")
            df_sub = df_artigos[df_artigos["pilar"] == pilar]
            for _, r in df_sub.iterrows():
                f.write(f"### [{r['id']}] {r['autores']} ({r['ano']}) — *{r['titulo']}*\n")
                f.write(f"- **Periódico/Veículo:** {r['periodico']} (DOI: [{r['doi']}](https://doi.org/{r['doi']}))\n")
                f.write(f"- **Tema:** {r['tema']} | **Metodologia:** {r['metodologia']}\n")
                f.write(f"- **Principais Achados:** {r['principais_achados']}\n")
                f.write(f"- **Implicação Direta para o PMM-E:** {r['implicacao_pmme']}\n\n")
                f.write("---\n\n")

    print(f"[OK] Matriz de evidências gerada com sucesso:")
    print(f"     CSV:  {out_csv}")
    print(f"     JSON: {out_json}")
    print(f"     MD:   {out_md}")
    print(f"     Total de artigos seminais estruturados: {len(df_artigos)}")


if __name__ == "__main__":
    main()
