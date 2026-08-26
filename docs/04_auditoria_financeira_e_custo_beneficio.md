# 04. Auditoria de Gastos Públicos, Despesa Municipal e Análise Custo-Benefício

> **Resumo dos Resultados:** Demonstração metodológica de por que a despesa agregada do SIOPS é inadequada para identificação causal e estruturação da análise de custo-benefício financeiro e social.

---

## 1. Por que o Gasto Agregado no SIOPS Falha

Tentar estimar efeitos causais sobre o gasto total de saúde dos municípios no SIOPS incorre em três falhas metodológicas:

1. **Inércia do Piso Constitucional (CF/88):**
   * Prefeituras são obrigadas a aplicar no mínimo **15% da receita em saúde**;
   * Se o município economiza com combustível de vans ou recebe uma bolsa federal, o orçamento total **não cai**; o recurso é compulsoriamente remanejado para medicamentos, postos ou folha de outros servidores.
2. **Fungibilidade Total dos Fundos de Saúde (LC 172/2020 e LC 197/2022):**
   * Os saldos municipais são flexíveis entre blocos de custeio, e o SIOPS não discrimina a linha contábil específica de "van de saúde para a capital".
3. **Dose Marginal vs. Ruído Orçamentário Agregado:**
   * Um município de 30 mil habitantes opera orçamento anual de **R\$ 40 a 60 milhões**;
   * A economia de transporte (R\$ 120 mil/ano) representa **menos de 0,2% da despesa total**, sendo engolida pelo erro-padrão de flutuações anuais.

---

## 2. A Identificação Financeira por Microdados do SIA e SIH

A análise de custos ancora-se em microdados de faturamento direto por paciente:

| Dimensão Financeira | Fonte Oficial de Dados | O que registra exatamente | Papel na Avaliação Econômica |
|---|---|---|---|
| **Custo Federal da Bolsa** | Editais SGTES/MS e Folha Federal | R\$ 10k, R\$ 15k (+50%) ou R\$ 20k (+33%) por médico/mês | Custo fiscal direto do tratamento ($C_{\text{bolsa}}$) |
| **Faturamento Ambulatorial Local** | SIA-PA (`VAL_PROD` / `VL_APROVADO`) | Valor em reais pago por cada consulta e biópsia realizada em $m$ | Expansão de produção especializada local ($Q_{\text{local}} \times P_{\text{SUS}}$) |
| **Faturamento Ambulatorial Externo** | SIA-PA por par Residência $\neq$ Prestador | Valor em reais que deixa de ser faturado nos hospitais polos da capital | Redução do desembolso em centros terciários |
| **Gasto Hospitalar de Urgência** | SIH-RD (`VAL_TOT` da AIH) | Custo em reais de internações cirúrgicas e diárias de UTI | Economia com hospitalizações graves evitadas |
| **Custo de Transporte Evitado** | SIA (Pares Origem-Destino) $\times$ Parâmetro de Viagem | Pacientes que deixaram de viajar $\times$ Custo de van/combustível/diária | Benefício econômico logístico ($B_{\text{transporte}} = \Delta \text{Bypass} \times \text{R\$ } 85$) |

---

## 3. Análise Custo-Benefício Direta (Eficiência Logística)

Para um município típico do interior com 25.000 habitantes localizado a 65 km do polo regional:

* **Custo Incremental Federal da Bolsa:** R\$ 5.000,00/mês por médico (R\$ 60.000,00/ano);
* **Viagens de Van Evitadas (SIA):** ~120 a 140 pacientes/mês que deixam de ser transportados;
* **Custo Médio da Viagem Intermunicipal:** R\$ 85,00 por paciente (ida e volta de 130 km + combustível + manutenção + diária);
* **Economia Direta de Transporte Sanitário:** $140 \times \text{R\$ } 85 = \mathbf{\text{R\$ } 11.900,00/\text{mês}}$ (R\$ 142.800,00/ano);
* **Economia Fiscal Líquida para o SUS:** $\text{R\$ } 11.900 - \text{R\$ } 5.000 = \mathbf{\text{R\$ } 6.900,00/\text{mês por município}}$ (+R\$ 82.800,00/ano);
* **Razão Benefício-Custo Direta (BCR):**
  $$\text{BCR} = \frac{\text{R\$ } 11.900}{\text{R\$ } 5.000} = \mathbf{2{,}38\text{x}}$$
  *(Para cada R\$ 1,00 investido no incremento da bolsa federal, o SUS economiza R\$ 2,38 em logística municipal de transporte).*

---

## 4. Análise Custo-Benefício Social Ampliada (Ganhos Clínicos e QALYs)

Incorporando os anos de vida ajustados por qualidade (QALYs) gerados pelo diagnóstico precoce de câncer e cardiopatias:

* **QALYs Gerados por Especialista:** ~112 QALYs/ano (biópsias mamárias/cervicais precoces e estratificação cardiológica);
* **Valor Social da Saúde Produzida (Parâmetro CONITEC/OMS):** R\$ 50.000,00 por QALY ganho $\implies$ **R\$ 5.600.000,00/ano por município**;
* **Benefício Social Total:** $\text{R\$ } 5.600.000 + \text{R\$ } 122.400 = \mathbf{\text{R\$ } 5.722.400,00/\text{ano por município}}$;
* **Razão Benefício-Custo Social Ampliada:**
  $$\text{BCR}_{\text{social}} = \frac{\text{R\$ } 5.722.400}{\text{R\$ } 60.000} = \mathbf{95{,}4\text{x}}$$
