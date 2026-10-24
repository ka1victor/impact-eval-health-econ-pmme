# 57b. Cenários contrafactuais de bolsa (T1.6): SIMULAÇÃO, NÃO OBSERVAÇÃO

> **ATENÇÃO: tudo neste documento é simulação (`natureza_dos_dados = CENARIO_CONTRAFACTUAL`).** Nenhum número abaixo foi observado: são alocações refeitas com um modelo de escolha estimado e o mecanismo do G2, sob hipóteses fixas. Não use estes números como resultado empírico nem como efeito causal estimado.<br>
> **Gerado por** `scripts/rdd_bolsa/25b_cenarios_bolsa.py` a partir de `output/cenarios/P1_*`; não editar à mão (o teste `tests/test_cenarios_bolsa.py` confere que este arquivo é igual ao gerado).<br>
> **Protocolo:** [adendo §7 do protocolo 52](52_protocolo_P1_escolha_dap.md#7-adendo-de-24102026-t16-cenários), congelado em 24/10/2026 antes de simular. Modelo de escolha: [doc 57a](57a_resultados_P1_escolha.md) (M1), auditado na auditoria 26. Mecanismo: [portão G2](../auditorias/G2_viabilidade_mecanismo.md).

## 1. A pergunta e o que a simulação faz

**Pergunta do autor:** quantas vagas a mais seriam preenchidas no total se a bolsa subisse R$ 5 mil, levando em conta que todas as vagas disputam o mesmo grupo de candidatos numa alocação centralizada por nota? A RDD não responde isso: ela compara células perto do corte, e uma vaga que ganha um candidato pode estar tirando esse candidato de outra.

**O que a simulação faz**, para a 1ª chamada dos ciclos 1, 2 e 3:
1. parte das listas de opções observadas e sorteia a parte da preferência que o modelo não explica, de modo que, sem mudar a bolsa, cada candidato repete exatamente a lista que fez;
2. muda a bolsa das células segundo o cenário e refaz a lista de cada candidato com o peso da bolsa do M1;
3. refaz a alocação com o mecanismo do G2 (aceitação adiada por opção e nota, cotas, capacidade efetiva);
4. compara com a alocação sem mudança (B0) da mesma réplica.

**Hipóteses (todas fixas):** vagas e capacidade fixas; o grupo de candidatos é fixo (ninguém novo entra, ninguém desiste); cada candidato mantém o número de opções que listou; alocação por nota como no G2; só a 1ª chamada; sem 2ª chamada, desistência, homologação ou custo fiscal (o custo abaixo é aritmética simples). Bolsas sempre dentro de R$ 10–20 mil, a faixa observada.

**O que o contraste mede:** o incentivo da bolsa como o M1 o identifica (o pacote do corte, auditoria 18), aplicado a quem já se candidatou. Não mede participação no PMM-E nem quantos médicos a mais o programa atrairia.

## 2. Mercado

| Ciclo | Candidatos elegíveis | Respondem ao cenário (amostra P1) | Lista fixa (fora da amostra P1) | Capacidade efetiva | Vagas preenchidas publicadas |
|---|---|---|---|---|---|
| ciclo 1 | 879 | 820 | 59 | 921 | 527 |
| ciclo 2 | 2179 | 2032 | 147 | 1836 | 1057 |
| ciclo 3 | 2604 | 2474 | 130 | 1295 | 704 |

- Unidades de simulação: 5639 (tipo A, 1ª e 2ª opção no mesmo curso: 3645; tipo B, só a 1ª opção modelada: 1776; tipo C, 2ª opção em outro curso: 218).
- M1 reestimado igual ao gravado (diferença máxima 2.9e-10); β_bolsa = 0,0424 (IC 95% [−0,0027; +0,0874]).
- R = 200 réplicas, semente 20261024; S4 com 100 sorteios por candidato (ESS mediano 69,8).

## 3. Validação de base

O cenário sem mudança (B0) precisa reproduzir as vagas preenchidas publicadas na 1ª chamada, por ciclo e faixa, com |B0 − observado| ≤ max(3; 2% do observado) em todas as réplicas (fixado antes de simular). A coluna do G2 principal usa a classificação publicada como desempate; o B0 usa o sorteio por candidato do adendo, porque a classificação não existe para pares candidato × célula novos.

| Ciclo | Faixa | Observado (1ª chamada publicada) | G2 principal (classificação publicada) | B0 nas réplicas (mín.–máx.) | Desvio máximo | Tolerância | Passa |
|---|---|---|---|---|---|---|---|
| ciclo 1 | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | 183 | 184 | 182–188 | 5 | 3,7 | **não** |
| ciclo 1 | Faixa 2 (0,300–0,400; R$ 15 mil) | 212 | 212 | 210–214 | 2 | 4,2 | sim |
| ciclo 1 | Faixa 1 (IVS > 0,400; R$ 20 mil) | 132 | 133 | 130–133 | 2 | 3,0 | sim |
| ciclo 1 | total | 527 | 529 | 525–534 | 7 | 10,5 | sim |
| ciclo 2 | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | 454 | 454 | 446–453 | 8 | 9,1 | sim |
| ciclo 2 | Faixa 2 (0,300–0,400; R$ 15 mil) | 425 | 425 | 419–425 | 6 | 8,5 | sim |
| ciclo 2 | Faixa 1 (IVS > 0,400; R$ 20 mil) | 178 | 178 | 176–178 | 2 | 3,6 | sim |
| ciclo 2 | total | 1057 | 1057 | 1044–1055 | 13 | 21,1 | sim |
| ciclo 3 | Faixa 3 (IVS ≤ 0,300; R$ 10 mil) | 331 | 331 | 331–331 | 0 | 6,6 | sim |
| ciclo 3 | Faixa 2 (0,300–0,400; R$ 15 mil) | 248 | 249 | 247–249 | 1 | 5,0 | sim |
| ciclo 3 | Faixa 1 (IVS > 0,400; R$ 20 mil) | 125 | 125 | 125–125 | 0 | 3,0 | sim |
| ciclo 3 | total | 704 | 705 | 703–705 | 1 | 14,1 | sim |

**Resultado da validação: FALHOU.**

## 4. Falha da validação de base

`FALHA_VALIDACAO_BASE`. Onde falhou: ciclo 1, Faixa 3 (IVS ≤ 0,300; R$ 10 mil): observado 183, B0 entre 182 e 188 (média 185,1), desvio máximo 5 > tolerância 3,66.

Conforme o adendo, nada foi calibrado e **os cenários não foram calculados**: não há resposta simulada à pergunta do autor nesta execução. Não há arquivo de réplicas, tabela, fluxos nem figura de cenário em `output/cenarios/`.

**O que a falha mostra.** O mecanismo foi conferido: com o mesmo desempate, a alocação montada pelo script é idêntica à do `alocar` do G2 sobre as linhas publicadas. A diferença vem do desempate por sorteio por candidato, fixado no adendo porque a classificação publicada não existe para pares candidato × célula novos. Com a classificação publicada (coluna do G2 principal), a reconstrução fica a no máximo 2 vaga(s) do observado em cada linha da tabela. Onde há empate de nota no corte da célula (G2, seção 4), o sorteio troca quem fica, e o perdedor pode ocupar ou não a vaga da 2ª opção; isso desloca vagas entre faixas em parte das réplicas.

**Decisões em aberto, do autor (nenhuma foi executada):**
1. aceitar um desempate que use a classificação publicada nos pares observados e o sorteio só nos pares novos, com nova validação;
2. trocar a regra "em todas as réplicas" por uma regra sobre a média ou sobre um percentil das réplicas;
3. rodar só os ciclos 2 e 3, que passaram;
4. manter a falha como resultado: com o desempate do edital fora dos dados, o mecanismo não é reproduzido com a precisão exigida em todas as réplicas.

Qualquer uma delas exige um adendo datado antes de rodar, que registre que esta falha já foi vista.

## 5. Nota de processo

Antes da execução com R = 200, o script foi rodado três vezes com R = 2 para depurar o código (24/10/2026, depois do commit do adendo). A 1ª parou numa conferência interna (instabilidade numérica no S4, corrigida no sorteio condicional); a 2ª parou num erro do código das figuras; a 3ª passou a validação de base com 2 réplicas e calculou os cenários, e o agente viu esses números de 2 réplicas. A execução com R = 200 falhou na validação de base. Depois disso só mudaram o texto do doc e a limpeza das saídas de cenário da depuração (apagadas); nada mudou no modelo, no mecanismo, na tolerância ou no desempate.

