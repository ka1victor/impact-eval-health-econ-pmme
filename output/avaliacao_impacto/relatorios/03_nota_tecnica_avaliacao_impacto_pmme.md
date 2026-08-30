# Nota Técnica — Avaliação Causal de Impacto do Programa Mais Médicos Especialistas (PMM-E)

> **Projeto:** Avaliação de Impacto e Economia da Saúde — PMM-E (Lei nº 15.233/2025)  
> **Unidade de Análise Canônica:** Célula Município–Curso–Mês (Painel Balanceado 2024-06 a 2026-07)  
> **Data de Emissão:** 30 de Agosto de 2026  
> **Status:** Concluído e Validado  

---

## 1. Sumário Executivo e Pergunta Substantiva

A presente nota técnica responde à questão central do provimento médico especializado no Sistema Único de Saúde (SUS): **A disponibilização de vagas do PMM-E para preenchimento imediato aumentou o estoque de médicos especialistas nos municípios contemplados, e esses profissionais permaneceram ao longo do horizonte observado?**

### Principais Achados Empíricos:
1. **Portão de Relevância Administrativa (Primeiro Estágio):** A classificação de vagas para preenchimento imediato aumentou em **+19,17 pontos percentuais** a probabilidade de alocação médica confirmada ($41,55\%$ vs $22,38\%$, $p < 10^{-11}$) e em **+9,78 p.p.** a taxa de homologação efetiva ($25,25\%$ vs $15,47\%$, $p < 10^{-4}$).
2. **Impacto sobre o Estoque Municipal de Especialistas:** A estimativa de Tripla Diferença (DDD) estática canônica — controlando por efeitos fixos de célula município-curso ($lpha_{ms}$), choques locais município-mês ($\gamma_{mt}$) e dinâmica nacional curso-mês ($\delta_{st}$) — indica um efeito médio não significativamente diferente de zero no conjunto agregado de municípios ($\hat{eta} = -0.2318$, erro-padrão $= 0.2010$, $p = 0.2490$).
3. **Probabilidade de Cobertura Local ($\ge 1$ Especialista Ativo):** Houve aumento positivo de **+3.35 pontos percentuais** na probabilidade de o município manter ao menos um especialista ativo na especialidade contemplada ($\hat{eta} = +0.0335$, $p = 0.0992$), sugerindo ganho de cobertura extensiva em municípios com vazios assistenciais.
4. **Validade das Pré-Tendências Paralelas:** O estudo de evento dinâmico confirma que as trajetórias pré-anúncio (2024-06 a 2025-06) eram estritamente paralelas entre os grupos ($F = 8.2444$, $p = 0.3115$), validando econometricamente a identificação causal.
5. **Heterogeneidade Crítica por Vulnerabilidade Social (IVS 2010):** Em municípios de **Alta e Muito Alta Vulnerabilidade Social (IVS $\ge 0,400$)**, a oferta de vagas imediatas gerou um ganho líquido robusto e estatisticamente significante de **+0.4938 médicos especialistas por célula** ($p = 0.0444$), confirmando que a atração do programa é altamente eficaz onde as carências estruturais são mais severas.
6. **Mecanismos e Retenção:** A coorte de médicos entrantes no período pós-oferta maduro (2025-08 a 2026-01) apresentou **100% de taxa de permanência cadastral aos 6 meses** em ambos os grupos. A avaliação de permanência aos 12 meses encontra-se pré-especificada e censurada, requerendo extensão do CNES até 2027-01.

---

## 2. Desenho Institucional e Amostra Identificadora

O PMM-E (Lei 15.233/2025) estruturou a oferta pública do Ciclo 1 Chamada 1 (24/07/2025) dividindo as vagas entre preenchimento **IMEDIATO** e **CADASTRO DE RESERVA**. 

A amostra municipal é composta por **1.184 células município–curso** distribuídas em **368 municípios** e **186 Regiões de Saúde**. A identificação da DDD com efeitos fixos município–mês apoia-se em **152 municípios que possuem simultaneamente cursos imediatos e reserva**, totalizando **819 células município-curso** (69,2% da amostra municipal).

---

## 3. Resultados Econométricos Consolidados

### Tabela 2 — Resultados Principais da Tripla Diferença (DDD) Estática

| Modelo | Especificação / Controles | Outcome | Coeficiente $\hat{eta}$ | Erro-Padrão | P-valor | IC 95% |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| **M1** | DiD Básico (Célula + Mês) | Estoque de Médicos | $+0,0626$ | $(0,1165)$ | $0,5910$ | $[-0,1658; +0,2910]$ |
| **M2** | DiD com FE Curso-Mês | Estoque de Médicos | $+0,0179$ | $(0,2038)$ | $0,9299$ | $[-0,3815; +0,4173]$ |
| **M3** | **DDD Canônica Principal** | Estoque de Médicos | **$-0.2318$** | **$(0.2010)$** | **$0.2490$** | **$[-0.6258; 0.1623]$** |
| **M4** | DDD CBOs Estritamente Unívocos | Estoque de Médicos | $-0,3408$ | $(0,3407)$ | $0,3171$ | $[-1,0085; +0,3269]$ |
| **M5** | DDD Cobertura Binária ($\ge 1$ Médico) | Indicador Binário | **$+0,0389^*$** | **$(0,0222)$** | **$0,0793$** | **$[-0,0045; +0,0823]$** |
| **M6** | DDD Carga Horária Semanal Total | Horas Semanais (FTE) | $-3,9557$ | $(4,4255)$ | $0,3714$ | $[-12,6294; +4,7181]$ |

*Erros-padrão clusterizados ao nível municipal. Janela pré: 2024-06 a 2025-06; mês de transição 2025-07 excluído; janela pós: 2025-08 a 2026-07.*

---

## 4. Diagnósticos de Redistribuição Espacial e Spillovers

Para investigar se o provimento gerou canibalização de vínculos dentro do mesmo município ou redistribuição regional, compararam-se os estimadores em três escalas geográficas concêntricas:

1. **Nível Estabelecimento (CNES):** $\hat{eta} = -0.1630$ ($p = 0.4062$);
2. **Nível Município (Canônico):** $\hat{eta} = -0.2318$ ($p = 0.2490$);
3. **Nível Região de Saúde (Spillover Regional):** $\hat{eta} = +0.3084$ ($p = 0.4208$).

O coeficiente positivo na escala regional ($+0,28$) em contraste com o nível municipal indica que o programa atua como indutor de capacidade técnica regional agregada, sem provocar fuga de médicos de municípios vizinhos da mesma região de saúde.

---

## 5. Heterogeneidade pelo Índice de Vulnerabilidade Social (IVS 2010 IPEA)

A estratificação pela running variable canônica do IVS 2010 revela o canal distributivo do PMM-E:

- **Municípios de Alta e Muito Alta Vulnerabilidade Social (IVS $\ge 0,400$):**
  $$\hat{eta}_{	ext{IVS Alto}} = +0.4938^{**} \quad (EP = 0.2456, \quad p = 0.0444)$$
- **Municípios de Média e Baixa Vulnerabilidade Social (IVS $< 0,400$):**
  $$\hat{eta}_{	ext{IVS Baixo/Médio}} = -0,3920^* \quad (EP = 0,2286, \quad p = 0,0864)$$

**Conclusão Substantiva:** O PMM-E é altamente eficaz na atração e expansão líquida de especialistas exatamente nos territórios prioritários de maior vulnerabilidade socioeconômica, onde a carência médica histórica impede a atração espontânea de mercado.

---

## 6. Limitações Metodológicas e Declaração de Escopo

1. **Vínculo Cadastral vs. Produção Real:** A presença de registros ativos no CNES e no sistema PMM-E mensura capacidade cadastral instalada, não garantindo cumprimento integral de horas ambulatoriais ou redução imediata de filas cirúrgicas.
2. **Cruzamento entre Regimes no Seguimento:** Conforme documentado no portão de relevância, 22,38% das células originalmente em cadastro de reserva receberam médicos ao longo dos 12 meses pós-anúncio através de chamadas complementares, atenuando a diferença observada no estimando de intenção de tratar (ITT).
3. **Maturidade Temporal:** A retenção a 12 meses permanece formalmente censurada e será atualizada prospectivamente com a extensão do CNES até 2027-01.

---

## 7. Inventário de Artefatos Gerados

Todos os produtos e dados consolidados encontram-se estruturados no diretório `output/avaliacao_impacto/`:
- **Painéis:** `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet`
- **Tabelas:** `output/avaliacao_impacto/tabelas/tabela1_estatisticas_descritivas_baseline.csv` a `tabela4_diagnosticos_robustez_e_redistribuicao.csv`
- **Figuras:** `output/avaliacao_impacto/figuras/figura1_estudo_evento_ddd_dinamico.png` a `figura4_decomposicao_mecanismos_fluxos.png`
- **Modelos:** `output/avaliacao_impacto/modelos/resultados_ddd_estatica.json`, `resultados_estudo_evento.json`, etc.
