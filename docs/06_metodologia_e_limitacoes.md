# 06. Rigor Metodológico, Proveniência dos Dados e Limitações

---

## 1. As Regras Metodológicas Obrigatórias

1. **Rigor de RDD:**
   * Running variable pré-determinada historicamente (IVS 2010 do IPEA, Censo 2010);
   * Teste contínuo de densidade em torno dos cortes (McCrary proxy com razão $> 0{,}85$);
   * Avaliação de sensibilidade em 4 janelas locais ($h \in [0{,}015; 0{,}030]$);
   * Testes de falsos cortes (placebos) em $IVS = 0{,}250$ e $0{,}350$ com efeito estritamente nulo.
2. **Inferência Robusta:**
   * Erros-padrão robustos clusterizados no nível municipal e testes exatos de permutação de Fisher-Pitman (2.000 repetições);
   * Controle de taxa de falsas descobertas (FDR de Anderson / Benjamini-Hochberg) e Índice Padronizado KLK (Kling, Liebman & Katz, 2007).
3. **Regra de Proveniência dos Dados:**
   * ✅ **Verificado e Auditado:** Microdados nominais SGTES, SIA-PA mensal, SIH-RD mensal, bases do IPEA e diários oficiais.
   * ⚠️ **Aproximação/Premissa Paramétrica:** Custos unitários operacionais de vans sanitárias (R\$ 85/viagem) e parâmetros de QALYs (CONITEC/OMS).
   * ❓ **Não Observável / Descartado:** Gasto orçamentário agregado do SIOPS (inviável por piso de 15% e fungibilidade).

---

## 2. Ameaças à Identificação Causal e Defesas

| Ameaça Metodológica | Risco Potencial | Defesa Empírica Aplicada |
|---|---|---|
| **Manipulação do IVS por Prefeitos (*Sorting*)** | Prefeitos tentarem empurrar a nota do município para $IVS > 0{,}300$ para ganhar mais bolsa. | **Impossível:** O IVS foi calculado pelo IPEA no Censo de 2010, 14 anos antes da criação da Lei nº 15.233/2025. |
| **Demanda Induzida por Médicos (*Supplier-Induced Demand*)** | Especialistas alocados inflarem exames fúteis para faturar procedimentos. | **Descartada:** A decomposição de resolutividade global no SIA (3,77M linhas) comprova neutralidade do volume per capita total e substituição quase perfeita de viagens. |
| **Confusão de Tendência Temporal (*Pre-Post Bias*)** | Atribuir o crescimento de atendimentos a uma tendência de expansão do SUS pós-pandemia. | **Isolada:** Comparamos quem está imediatamente acima com quem está imediatamente abaixo do corte ($IVS = 0{,}300$), cancelando tendências macroeconômicas comuns. |
| **Subnotificação no SIOPS Municipal** | Ocultação de despesas com transporte em rubricas genéricas de custeio. | **Superada:** Não usamos o SIOPS; calculamos a economia via fluxos físicos reais de pares residência-prestador no SIA multiplicados pelo custo operacional unitário. |
