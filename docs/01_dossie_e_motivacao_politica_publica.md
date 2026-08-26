# 01. Dossiê Institucional, Objetivos Oficiais e Métricas Auditáveis no SUS

> **Escopo Preliminar:** Esta formulação constitui a base conceitual e normativa viva do paper, fundamentada na Lei Federal nº 15.233/2025 (*Agora Tem Especialistas*) e nos Editais SGTES/MS de 2025 e 2026.

---

## 1. O Programa Institucional e a Base Legal

* **Nome Oficial:** *Programa Mais Médicos Especialistas (PMM-E)*, componente de provimento da Política Nacional de Atenção Especializada em Saúde — Programa *Agora Tem Especialistas*.
* **Base Legal:** Lei nº 15.233, de 07 de outubro de 2025 (conversão da MP nº 1.301/2025), Portaria GM/MS nº 7.266/2025 e Editais SGTES/MS nº 3/2025 e 6/2026.
* **Período de Análise:** Ciclos 1 (Edital 3/2025) e 2 (Edital 6/2026), com acompanhamento mensal de provimento ativo de dezembro de 2025 a agosto de 2026.
* **Dilema Econômico Central:** Vale mais a pena para o SUS pagar um incentivo financeiro para fixar o especialista no interior ou continuar bancando o transporte sanitário (vans e ambulâncias) de pacientes até os polos regionais? Qual é o piso salarial ótimo para atrair o médico sem gerar sobrepreço fiscal?
* **Pergunta de Pesquisa:** *Quais os efeitos do Programa Mais Médicos Especialistas sobre os outcomes de saúde dos pacientes e sobre os gastos municipais?*

---

## 2. A Matriz Estratégica: Objetivos Oficiais vs. Métricas Auditáveis no SUS

A avaliação de impacto decompõe os objetivos formais da Lei nº 15.233/2025 em **métricas empiricamente auditáveis** nos microdados do DATASUS:

| # | Objetivo Oficial (Lei 15.233/2025) | Mecanismo Microeconômico | Métrica Empírica Clara no SUS | Fonte Oficial do Dado | Poder Causal |
|---|---|---|---|---|:---:|
| **1** | **Superar Vazios Assistenciais e Atrair Especialistas** (Art. 2º, II) | Aumento da oferta de trabalho médico induzida pelo salto salarial. | **Taxa de Preenchimento da Vaga no 1º Chamamento:** % de vagas ocupadas de imediato no edital.<br>**Retenção aos 6 meses:** % de permanência no CNES. | Editais SGTES/MS e CNES (`tbCargaHorariaSus`) | **Super Alta** ($t > 100$, $p < 0{,}0001$) |
| **2** | **Aumentar a Resolução Local do Cuidado** (Art. 2º, III) | O munícipe passa a ser atendido e diagnosticado dentro do próprio município. | **Taxa de Resolutividade Local ($R_{\text{local}}$):** $\frac{\text{Atendimentos Locais}}{\text{Atendimentos Totais dos Residentes}}$. Salto de **38% para 72% (+34 p.p.)**. | SIA-PA (Pares de Residência $\times$ Prestador) | **Alta** (3,77M linhas) |
| **3** | **Diagnóstico Precoce e Rastreamento** (Art. 2º, I) | Identificação precoce de câncer (mama, colo, digestivo) e risco cardiovascular. | **Volume Mensal de Exames Diagnósticos:** Biópsias, mamografias, endoscopias e colonoscopias locais.<br>**Estadiamento Inicial:** % de casos em estágio precoce. | SIA-PA (Grupos 02 e 03) e SIA-APAC (`AP_ESTAD`) | **Alta** (162 mil exames/mês) |
| **4** | **Destravar Cirurgias Eletivas e Reduzir Urgências** (Art. 2º, I) | 384 anestesistas e 160 cirurgiões destravam centros cirúrgicos municipais preexistentes. | **Composição da Internação (`CAR_INT` no SIH):** Aumento de **Cirurgias Eletivas Locais (`CAR_INT = 01`)** e queda de **Internações de Urgência Transferidas (`CAR_INT = 02`)**. | SIH-RD (AIH por Caráter de Internação) | **Média-Alta** (1,35M linhas) |
| **5** | **Reduzir Custos de Deslocamento e Transporte** (Art. 18) | Eliminação da penosidade de viagens intermunicipais em vans de saúde. | **Viagens Evitadas ($\Delta \text{Bypass}$):** Queda de 140 viagens/mês por médico.<br>**Horas Poupadas:** 1,11 milhão de horas de van poupadas/mês.<br>**Razão Benefício-Custo:** **2,4x**. | SIA (Pares OD) $\times$ Matriz Rodoviária DNIT | **Alta** (Logística e Custos Evitados) |

---

## 3. Armadilhas Metodológicas: Objetivos Oficiais sem Métricas Adequadas

É essencial registrar por que certas metas institucionais **não são adequadas como desfechos primários de identificação causal**:

1. **Despesa Orçamentária Total Municipal no SIOPS:**
   * *Inércia do Piso de 15% (CF/88):* Municípios são obrigados a gastar 15% da receita própria em saúde; recursos poupados em transporte são compulsoriamente remanejados para outros custeios.
   * *Fungibilidade:* O SIOPS agrega gastos em rubricas amplas (pessoal/custeio), tornando impossível isolar a despesa de transporte da especialidade.
   * *Solução Adotada:* Mensurar o **custo contábil direto evitado em faturamento SIA/SIH e viagens físicas evitadas ($P \times Q$)**.
2. **Tempo de Espera Bruto em Filas de Regulação (SISREG / CROSS):**
   * *Opacidade e Heterogeneidade:* As centrais de regulação são estaduais, com regras de priorização distintas e sujeitas a reordenamentos administrativos.
   * *Solução Adotada:* Utilizar o **tempo decorrido entre o primeiro exame diagnóstico e a primeira intervenção terapêutica** nos microdados do SIA/SIH.
3. **Mortalidade Geral no Curto Prazo (SIM):**
   * *Ruído e Defasagem:* Consultas ambulatoriais não reduzem a mortalidade geral de um município em uma janela de 12 meses.
   * *Solução Adotada:* Focar em **outcomes intermediários de alta sensibilidade biológica** (diagnósticos precoces e resolução eletiva).

---

## 4. Os 4 Achados Inesperados e Contra-Intuitivos

1. **O Colapso da Elasticidade Salarial (Pagar R\$ 20k não atrai muito mais que R\$ 15k):**  
   A oferta médica responde com altíssima sensibilidade ao salto de R\$ 10k para R\$ 15k (+35,5 p.p., $\varepsilon = 1{,}48$), mas a resposta satura entre R\$ 15k e R\$ 20k (+9,1 p.p., $\varepsilon = 0{,}31$). Acima de R\$ 15k/mês, o gargalo deixa de ser salário e passa a ser isolamento geográfico, precariedade de infraestrutura física e falta de serviços/escolas para a família do médico.
2. **O Paradoxo da Retenção (Cidades de R\$ 20k perdem médicos mais rápido):**  
   A taxa de retenção aos 6 meses no corte de R\$ 20k é **negativa e estatisticamente significativa** ($\tau = -4{,}4\text{ p.p.}$, $p = 0{,}013$). O especialista aceita a vaga atraído pelo valor nominal da bolsa, mas abandona o município precocemente devido à impossibilidade técnica de atuar em cidades com $IVS > 0{,}400$ sem suporte diagnóstico mínimo.
3. **A Ausência de Demanda Induzida por Médicos:**  
   O aumento de consultas e exames locais operou como **substituição geográfica pura**: a produção local cresceu exatamente na proporção em que as viagens de van para capitais caíram, sem gerar inflação artificial de procedimentos supérfluos.
4. **O Gargalo Oculto do SUS (O problema não era prédio, era Anestesista):**  
   A especialidade mais demandada e alocada foi **Anestesiologia (384 médicos, >25% do programa)**, destravando centros cirúrgicos municipais preexistentes que estavam ociosos e paralisados por falta do profissional habilitado.
