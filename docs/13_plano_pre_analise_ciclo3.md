# Plano de Pré-Análise Oficial — Avaliação Causal do Ciclo 3 (PMM-E)

> **Identificador do Protocolo:** `PMM-E-C3-PROSPECTIVE-2026`  
> **Data de Congelamento:** 2026-08-30  
> **Status:** Registrado e Congelado Pré-Tratamento (Hashes Criptográficos Auditados)  
> **Data Prevista de Início do Programa ($T_0$):** Setembro de 2026  
> **Janela Pré-Tratamento:** Junho de 2024 a Agosto de 2026 (25 competências mensais)

---

## 1. Pergunta Substantiva e Estimando Causal

Este estudo avalia o impacto do **Programa Mais Médicos Especialistas (PMM-E / Lei nº 15.233/2025)** no Ciclo 3 por meio de uma estratégia comparativa estrita por **Intenção de Tratar (ITT)**:

> **Pergunta Primária:** Qual é o efeito de obter priorização de vaga imediata no PMM-E, em comparação com propostas submetidas por gestores que não foram priorizadas no mesmo processo seletivo, sobre a oferta líquida de médicos especialistas e a produção de cirurgias eletivas locais aos 6 e 12 meses?

### 1.1 Contraste Institucional do Tratamento
- **Tratamento ($D=1$):** Propostas com vagas exclusivamente priorizadas como imediatas (`imediata_pura`).
- **Controle ($D=0$):** Propostas submetidas por gestores que foram deferidas administrativamente mas **não foram priorizadas** pela SGTES/MS (`nao_priorizada_pura`).
- **Exclusões:** Cadastro de reserva puro e células mistas são formalmente excluídos da análise confirmatória primária.

---

## 2. Decisão do Torneio Pré-Tratamento

A arbitragem metodológica foi conduzida exclusivamente sobre dados anteriores a $T_0$, comparando pré-tendências, placebos temporais e poder estatístico (MDE):

| Módulo | Amostra Prévia | Placebo 2025-06 ($p$-valor) | MDE (80% poder) | Diagnóstico Pré |
|---|---|---:|---:|---|
| **Cirurgias Eletivas CNES (SIH)** | Anestesiologia Imediata vs Nao Priorizada | $p = 0.7000$ | 13.873 | **COMPATIVEL** |
| **Cirurgias Eletivas Municipio Total (SIH)** | Anestesiologia Total | $p = 0.1876$ | 41.512 | **COMPATIVEL** |
| **Cirurgias Eletivas Municipio Isolado (SIH)** | Anestesiologia Isolada | $p = 0.4130$ | 34.197 | **COMPATIVEL** |
| **Força de Trabalho Médica Geral (DDD CNES)** | 7 Cursos Unívocos C3 | $p = 0.0365$ | 1.317 | **ALERTA_TENDENCIA** |


---

## 3. Especificação Econométrica Confirmatória

### 3.1 Modelo 1: Núcleo de Força de Trabalho Médica (DDD Hospitalar)
```latex
Y_ist = alpha_is + gamma_it + delta_st + sum_k beta_k * (Imediata_is * 1[t - T0 = k]) + epsilon_ist
```
- $lpha_{is}$: Efeitos fixos de estabelecimento–especialidade (absorve capacidades permanentes).
- $\gamma_{it}$: Efeitos fixos de estabelecimento–mês (absorve choques gerenciais e orçamentários do hospital).
- $\delta_{st}$: Efeitos fixos de especialidade–mês (absorve tendências nacionais da área médica).
- Cluster de erros-padrão no nível do **Município** com Wild Cluster Bootstrap.

### 3.2 Modelo 2: Módulo Assistencial de Cirurgias Eletivas (SIH/SUS)
```latex
C_it = alpha_i + gamma_t + beta * (Imediata_i * Pos_t) + epsilon_it
```
- $C_{it}$: Número mensal de AIHs cirúrgicas iniciais eletivas (Grupo 04 do SIGTAP) realizadas no estabelecimento.

---

## 4. Família de Outcomes e Horizontes

### 4.1 Outcomes Primários Congelados
1. **Estoque de Médicos Especialistas:** Contagem mensal de profissionais distintos com CBO compatível no CNES.
2. **Cirurgias Eletivas Realizadas:** Volume mensal de AIHs cirúrgicas eletivas faturadas no CNES.

### 4.2 Outcomes Secundários e Mecanismos
1. **Participantes com Assinatura PMM-E:** Vínculo `070102` + CNPJ MS (`00394544012787`) no `tbCargaHorariaSus`.
2. **Retenção de Médicos Entrantes:** Entrantes presentes 6 e 12 meses após a alocação.
3. **Resolutividade Cirúrgica Municipal:** Cirurgias eletivas de residentes operados no próprio município vs. evasão regional.

---

## 5. Regras de Integridade e Cláusula de Bloqueio

1. **Vedação a Redesenho Posterior:** Nenhuma amostra, estimador ou janela poderá ser alterada após a abertura dos dados pós-tratamento.
2. **Linguagem Causal Condicional:** Se o teste conjunto pós-tratamento de pré-tendências falhar, o status do estudo será formalmente rebaixado para **associação ajustada**.
3. **Hashes Imutáveis:** Este documento e os dados analíticos pré-tratamento estão selados no manifesto criptográfico `registro_pre_analise.json`.
