# -*- coding: utf-8 -*-
"""
scripts/gerar_doc_teoria_pmme.py
Gera o documento mestre docs/10_fundamentacao_teorica_problema_pmme.md
com a fundamentação teórica formal completa para o problema do PMM-E.
"""

doc_text = """# 10. Fundamentação Teórica Estrutural do Problema do PMM-E

> **Documento Teórico Central**  
> **Projeto:** Avaliação de Impacto e Economia da Saúde — Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)  
> **Autores:** Equipe de Pesquisa Econômica em Saúde  
> **Data:** 30 de Agosto de 2026  

---

## 1. Visão Geral: Por que a Teoria Microeconômica é Indispensável no PMM-E?

A literatura moderna em Economia da Saúde e Economia do Trabalho (e.g., Acemoglu, Finkelstein, Agarwal, Baicker) estabelece que uma avaliação empírica quase-experimental só alcança validade externa e interpretabilidade causal se estiver firmemente ancorada em um **modelo microeconômico dedutivo**.

No caso do **Programa Mais Médicos Especialistas (PMM-E)**, a intervenção pública não atua sobre um mercado competitivo sem fricções. O programa atua sobre um complexo sistema de equilíbrio geral caracterizado por:
1. **Assimetrias de informação e custos de busca espacial** na distribuição geográfica de médicos especialistas.
2. **Complementaridade estrita de fatores de produção** entre mão de obra médica especializada ($L$) e infraestrutura hospitalar/diagnóstica ($K$).
3. **Agência intergovernamental e oportunismo fiscal**, em que municípios podem substituir gastos próprios com pessoal por bolsas federais (*crowding-out*).
4. **Contratos multitarefa**, nos quais o profissional divide seu esforço entre a produção assistencial imediata e o investimento formativo de longo prazo.

Este documento formaliza os **7 Pilares Teóricos Seminais** que embasam cada faceta do problema econômico do PMM-E e desenvolve um **Modelo Teórico Unificado** que conecta diretamente a teoria à especificação empírica de Tripla Diferença (DDD) adotada no repositório.

```mermaid
graph TD
    subgraph "Arcabouço Teórico Integrado do PMM-E"
        P1["Pilar 1: Equilíbrio Espacial & Diferenciais Compensatórios<br/>(Roback 1982 / Rosen 1986)"] --> M["Modelo Microeconômico Unificado do PMM-E"]
        P2["Pilar 2: Matching Centralizado & Redução de Fricções<br/>(Roth 1984 / Agarwal 2015)"] --> M
        P3["Pilar 3: Função de Produção Hospitalar & Capital Físico<br/>(Acemoglu & Finkelstein 2008 / Chandra & Skinner 2012)"] --> M
        P4["Pilar 4: Federalismo Fiscal & Substituição/Crowding-Out<br/>(Baicker & Staiger 2005 / Gordon 2004)"] --> M
        P5["Pilar 5: Agência Multitarefa em Contratos Públicos<br/>(Holmstrom & Milgrom 1991)"] --> M
        P6["Pilar 6: Políticas Baseadas no Lugar & Bem-Estar Social<br/>(Kline & Moretti 2014 / Glaeser & Gottlieb 2008)"] --> M
        P7["Pilar 7: Decisão sob Incerteza & Resolutividade Diagnóstica<br/>(Currie & MacLeod 2017 / Arrow 1963)"] --> M
    end
    
    M --> TEST["Hipóteses Empíricas Testáveis (DDD, CNES Mensal, IVS 2010)"]
```

---

## 2. Os 7 Pilares Teóricos do Problema Substantivo

---

### PILAR 1 — Equilíbrio Espacial e Diferenciais Salariais Compensatórios
* **Papers Seminais:** **Roback (1982, *JPE*)**; Rosen (1986).
* **Referência:** Roback, Jennifer. (1982). *Wages, Rents, and the Quality of Life: A General Equilibrium Model of Geographic Differences*. **Journal of Political Economy**, 90(6), 1257–1278.
* **Extensão:** 22 páginas | **Foco de Leitura:** **pp. 1257–1272 (Seções 1 a 3: 15 págs)**.
* **Mecanismo Econômico Formal:**  
  O modelo de Roback determina a distribuição espacial de trabalhadores sob livre mobilidade. A condição de equilíbrio exige que a utilidade indireta de um médico especialista seja idêntica entre todas as localidades $m$:
  $$V(w_m, r_m; A_m) = \bar{u}$$
  onde $w_m$ é a remuneração média local, $r_m$ é o custo de vida/moradia e $A_m$ é o vetor de amenidades locais (infraestrutura urbana, escolas, segurança, lazer e amenidades profissionais hospitalares).  
  Diferenciando a utilidade indireta em relação às amenidades:
  $$\frac{\partial w_m}{\partial A_m} = -\frac{V_{A}(w_m, r_m; A_m)}{V_{w}(w_m, r_m; A_m)} < 0$$
* **Aplicação Estrutural ao PMM-E:**  
  Médicos especialistas apresentam alta elasticidade de renda e forte preferência por amenidades de grandes centros urbanos. Municípios com baixo índice de amenidades e alta vulnerabilidade social (mensurados pelo **IVS 2010 do IPEA**) sofrem de escassez crônica não por falta de demanda, mas porque o mercado local não consegue pagar o **diferencial salarial compensatório ($\Delta w$)** exigido para atraí-los. O PMM-E atua diretamente injetando uma bolsa federal que preenche esse gap de diferencial compensatório.

---

### PILAR 2 — Falhas de Busca, Congestionamento e Matching Centralizado
* **Papers Seminais:** **Agarwal (2015, *AER*)**; Roth (1984, *JPE*).
* **Referência:** Agarwal, Nikhil. (2015). *An Empirical Model of the Medical Match*. **American Economic Review**, 105(7), 1939–1978.
* **Extensão:** 40 páginas | **Foco de Leitura:** **pp. 1940–1958 (Seções I a III: 18 págs)**.
* **Mecanismo Econômico Formal:**  
  Mercados descentralizados de médicos residentes e recém-especialistas sofrem com duas falhas severas de mercado:
  1. *Atritos de busca e assimetria informacional:* Hospitais no interior não conseguem sinalizar suas vagas para formandos em grandes centros.
  2. *Externalidades de congestionamento e unraveling temporal:* Processos seletivos descentralizados geram desistências em cascata e vagas ociosas.  
  Agarwal (2015) modela o matching centralizado de médicos sob restrições de capacidade hospitalar $q_m$, mostrando que o clearinghouse centralizado alcança alocações eficientes e estáveis no sentido de Gale-Shapley:
  $$\mu = \arg\max_{\mu \in \mathcal{M}_{\text{estável}}} \sum_{i \in \mathcal{I}} u_i(\mu(i))$$
* **Aplicação Estrutural ao PMM-E:**  
  O edital federal unificado do Ministério da Saúde funciona como uma clearinghouse central. Ele reduz a zero os custos de busca para o médico e permite que vagas em hospitais do interior compitam em igualdade de visibilidade com capitais, explicando o salto descontínuo de preenchimento observado nas vagas imediatas.

---

### PILAR 3 — Função de Produção Hospitalar e Complementaridade Fator-Tecnologia
* **Papers Seminais:** **Acemoglu & Finkelstein (2008, *JPE*)**; Chandra & Skinner (2012, *JEL*).
* **Referência:** Acemoglu, Daron; Finkelstein, Amy. (2008). *Input and Technology Choices in Regulated Industries: Evidence from the Health Care Sector*. **Journal of Political Economy**, 116(5), 837–880.
* **Extensão:** 44 páginas | **Foco de Leitura:** **pp. 839–858 (Seções I a III: 20 págs)**.
* **Mecanismo Econômico Formal:**  
  A produção de cuidados de saúde hospitalares e ambulatoriais especializados é modelada por uma função de produção com complementaridade de insumos:
  $$Y = F(K, L; T)$$
  onde $L$ é o trabalho médico especializado, $K$ é o capital físico (leitos cirúrgicos, tomógrafos, equipamentos de ressonância e hemodinâmica) e $T$ é a tecnologia médica.  
  A hipótese central de complementaridade capital-trabalho estabelece que:
  $$\frac{\partial^2 Y}{\partial L \partial K} > 0 \iff \text{A produtividade marginal do especialista } \left(\frac{\partial Y}{\partial L}\right) \text{ é estritamente crescente no estoque de capital } K$$
* **Aplicação Estrutural ao PMM-E:**  
  Diferentemente da Atenção Primária (onde um estetoscópio e uma UBS básica são suficientes para consultas clínicas gerais), o especialista do PMM-E (e.g., cirurgião geral, ginecologista-obstetra, cardiologista, ortopedista) é um insumo inoperante na ausência de capital físico hospitalar. Isso fundamenta a necessidade de testar empiricamente se o impacto do PMM-E sobre internações e procedimentos locais é heterogêneo em relação à infraestrutura instalada no CNES.

---

### PILAR 4 — Federalismo Fiscal, Agência do Gestor Municipal e Crowding-Out
* **Papers Seminais:** **Baicker & Staiger (2005, *QJE*)**; Gordon (2004, *JPubE*).
* **Referência:** Baicker, Katherine; Staiger, Douglas. (2005). *Fiscal Shenanigans, Targeted Federal Health Care Funds, and Patient Mortality*. **Quarterly Journal of Economics**, 120(1), 345–386.
* **Extensão:** 42 páginas | **Foco de Leitura:** **pp. 348–360 (Seção II: Teoria, 12 págs)**.
* **Mecanismo Econômico Formal:**  
  O gestor público municipal maximiza uma função de utilidade $U(L_m, G_m)$, onde $L_m = L_m^{\text{próprio}} + L_m^{\text{fed}}$ é o estoque total de médicos e $G_m$ são outros gastos públicos municipais. A restrição orçamentária é dada por:
  $$w_m L_m^{\text{próprio}} + p_G G_m \le R_m + w_{\text{bolsa}} L_m^{\text{fed}}$$
  Diferenciando a escolha ótima em relação à alocação federal $L_m^{\text{fed}}$:
  $$\frac{\partial L_m^{\text{total}}}{\partial L_m^{\text{fed}}} = 1 + \frac{\partial L_m^{\text{próprio}}}{\partial L_m^{\text{fed}}}$$
  Se $\frac{\partial L_m^{\text{próprio}}}{\partial L_m^{\text{fed}}} = 0 \implies$ **Adição líquida perfeita** ($\Delta L^{\text{total}} = 1$).  
  Se $-1 < \frac{\partial L_m^{\text{próprio}}}{\partial L_m^{\text{fed}}} < 0 \implies$ **Substituição fiscal parcial (*crowding-out*)**.  
  Se $\frac{\partial L_m^{\text{próprio}}}{\partial L_m^{\text{fed}}} = -1 \implies$ **Crowding-out total** (o município demite exatamente um médico contratado para cada bolsista federal que entra).
* **Aplicação Estrutural ao PMM-E:**  
  Este pilar fornece a microfundamentação direta para o nosso estimador de estoque no CNES: estimar se $\beta_{\text{DDD}} = 1$ (expansão líquida integral) ou se $\beta_{\text{DDD}} < 1$ devido ao remanejamento ou não renovação de contratos municipais preexistentes.

---

### PILAR 5 — Teoria de Contratos Multitarefa e Alocação de Esforço
* **Papers Seminais:** **Holmstrom & Milgrom (1991, *JLEO*)**.
* **Referência:** Holmstrom, Bengt; Milgrom, Paul. (1991). *Multitask Principal-Agent Analyses: Incentive Contracts, Asset Ownership, and Job Design*. **Journal of Law, Economics, & Organization**, 7, 24–52.
* **Extensão:** 29 páginas | **Foco de Leitura:** **pp. 24–38 (Seções 1 a 3: 15 págs)**.
* **Mecanismo Econômico Formal:**  
  O médico participante do PMM-E atua sob um contrato público híbrido que exige dois tipos de esforço:
  - $e_1$: Esforço na produção assistencial direta no hospital municipal (plantões, consultas, cirurgias).
  - $e_2$: Esforço no módulo acadêmico de especialização (tutoria, estudos teóricos, cursos).  
  A função de custo de esforço do médico é convexa com substituição entre tarefas: $C(e_1, e_2)$ com $C_{12} > 0$.  
  Como a tarefa assistencial $e_1$ é diretamente observável pelo gestor do hospital local (gerando receita de SUS e produção ambulatorial) e a tarefa formativa $e_2$ é difusa e observada apenas pelo Ministério da Saúde, o equilíbrio de esforço distorce a dedicação do profissional em direção à tarefa mais pressionada localmente.
* **Aplicação Estrutural ao PMM-E:**  
  Modela por que a retenção e o cumprimento de metas de qualificação médica exigem governança institucional rigorosa e monitoramento para evitar que a carga assistencial local canibalize a formação pedagógica do especialista.

---

### PILAR 6 — Políticas Baseadas no Lugar (Place-Based) e Equilíbrio de Bem-Estar
* **Papers Seminais:** **Kline & Moretti (2014, *Ann. Rev. Econ.*)**; Glaeser & Gottlieb (2008, *JPE*).
* **Referência:** Kline, Patrick; Moretti, Enrico. (2014). *People, Places, and Public Policy: Some Simple Analytics of Local Economic Development Programs*. **Annual Review of Economics**, 6, 629–662.
* **Extensão:** 34 páginas | **Foco de Leitura:** **pp. 631–648 (Seções 1 a 3: 17 págs)**.
* **Mecanismo Econômico Formal:**  
  Analisa o bem-estar agregado social $W$ de políticas que subsidiam a atração de fatores de produção para regiões específicas $m$:
  $$W = \sum_{m=1}^{M} N_m \cdot v_m(w_m, r_m) + \text{Externalidades Espaciais de Saúde e Redução de Iniquidade}$$
  O programa só gera ganho líquido de eficiência social se:
  $$\text{Ganho Marginal Social de Saúde no Município Vulnerável} > \text{Custo Marginal do Subsídio Federal} + \text{Distorção de Realocação Espacial}$$
* **Aplicação Estrutural ao PMM-E:**  
  Permite enquadrar o PMM-E como uma política pública regional de saúde (*place-based health policy*), justificando por que concentrar vagas em municípios com IVS Alto e Muito Alto maximiza o retorno marginal em termos de vidas salvas e redução de custos logísticos de transporte de pacientes.

---

### PILAR 7 — Tomada de Decisão Médica sob Incerteza e Resolutividade Diagnóstica
* **Papers Seminais:** **Currie & MacLeod (2017, *JLE*)**; Arrow (1963, *AER*).
* **Referência:** Currie, Janet; MacLeod, W. Bentley. (2017). *Diagnosing Expertise: Human Capital, Decision Making, and Performance among Physicians*. **Journal of Labor Economics**, 35(1), 1–43.
* **Extensão:** 43 páginas | **Foco de Leitura:** **pp. 4–20 (Modelo Teórico: 16 págs)**.
* **Mecanismo Econômico Formal:**  
  Um paciente chega ao serviço de saúde local com um vetor de sintomas ruidoso $s = \theta^* + \varepsilon$. O médico deve decidir entre:
  1. *Diagnosticar e tratar localmente:* Custo clínico $c_{\text{local}}(\theta)$, cuja eficácia depende do nível de especialização técnica $\theta$ do profissional.
  2. *Encaminhar para a capital (TFD — Tratamento Fora do Domicílio):* Custo logístico e atraso terapêutico $C_{\text{transporte}} + \Delta t$.  
  A probabilidade de encaminhamento desnecessário ou erro de triagem é estritamente decrescente no capital humano especializado:
  $$\frac{\partial P(\text{Encaminhamento Evitável})}{\partial \theta} < 0$$
* **Aplicação Estrutural ao PMM-E:**  
  Fundamenta teoricamente a métrica de **resolutividade local**: a fixação de um médico especialista no município reduz drasticamente os gastos municipais com ambulâncias e transporte sanitário, resolvendo o problema no próprio território.

---

## 3. O Modelo Microeconômico Unificado do PMM-E

Integrando os 7 pilares seminais, o modelo do PMM-E é estruturado em três blocos interligados:

```mermaid
graph LR
    subgraph "Bloco 1: Médicos"
        B1["Maximização de Utilidade Espacial<br/>V(w_bolsa, IVS, esforço)"]
    end
    
    subgraph "Bloco 2: Hospital Municipal"
        B2["Otimização de Custos & Produção<br/>Y = F(K, L_próprio + L_PMM, theta)"]
    end
    
    subgraph "Bloco 3: Ministério da Saúde"
        B3["Clearinghouse Central de Vagas<br/>Imediatas (T=1) vs Reserva (T=0)"]
    end
    
    B1 --> B3
    B3 --> B2
    B2 --> OUT["Desfechos: Estoque CNES, Entradas/Saídas, Resolutividade Local"]
```

### 3.1 A Equação Estimada de Tripla Diferença (DDD)
A agregação do modelo microeconômico unificado em nível de município $m$, especialidade/curso $s$ e mês $t$ gera diretamente a especificação canônica estimada no pipeline:

$$Y_{mst} = \alpha_{ms} + \gamma_{mt} + \delta_{st} + \beta \left( \text{Immediate}_{ms} \times \text{Post}_t \right) + \varepsilon_{mst}$$

Onde:
* $\alpha_{ms}$ (Efeito fixo de município-curso): Absorve amenidades locais invariantes e diferenciais compensatórios estruturais de Roback (1982).
* $\gamma_{mt}$ (Efeito fixo de município-mês): Absorve choques orçamentários locais, oscilações do PIB municipal e decisões fiscais de Baicker & Staiger (2005).
* $\delta_{st}$ (Efeito fixo de curso-mês): Absorve choques tecnológicos nacionais de Chandra & Skinner (2012) e ciclos de formação médica.
* $\beta$: Identifica o impacto causal líquido da exposição ao edital federal na margem intensiva.

---

## 4. Guia de Atribuição e Roteiro de Leitura para os 7 Membros da Equipe

| Membro | Paper Teórico Atribuído | Extensão Recomendada | O que Escrever para a Seção Teórica do Artigo |
|:---:|:---|:---|:---|
| **Membro 1** | **Roback (1982)** | 15 págs (pp. 1257–1272) | Formalizar a curva de oferta médica espacial e a relação entre bolsa federal e IVS 2010. |
| **Membro 2** | **Agarwal (2015)** | 18 págs (pp. 1940–1958) | Modelar o edital centralizado como clearinghouse que elimina fricções de matching no SUS. |
| **Membro 3** | **Acemoglu & Finkelstein (2008)** | 20 págs (pp. 839–858) | Escrever a função de produção hospitalar com complementaridade capital-trabalho ($K, L$). |
| **Membro 4** | **Baicker & Staiger (2005)** | 12 págs (pp. 348–360) | Deduzir a proposição teórica de crowding-out e substituição de vínculos próprios no CNES. |
| **Membro 5** | **Holmstrom & Milgrom (1991)** | 15 págs (pp. 24–38) | Modelar o trade-off de agência entre carga horária assistencial no hospital e formação. |
| **Membro 6** | **Kline & Moretti (2014)** | 17 págs (pp. 631–648) | Redigir o enquadramento de eficiência e bem-estar social de políticas baseadas no lugar. |
| **Membro 7** | **Currie & MacLeod (2017)** | 16 págs (pp. 4–20) | Modelar a decisão de triagem diagnóstica e redução de Tratamento Fora do Domicílio (TFD). |
"""

with open("docs/10_fundamentacao_teorica_problema_pmme.md", "w", encoding="utf-8") as f:
    f.write(doc_text)

print("Documento docs/10_fundamentacao_teorica_problema_pmme.md gerado com sucesso.")
