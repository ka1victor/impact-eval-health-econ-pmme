# Estado executado do plano causal público

> **Data:** 2026-09-04.
> **Estado geral:** `A8_EXECUTADO_EFEITO_LOCAL_CONDICIONAL`.
> **Dependência externa:** nenhuma.

## Decisão vigente

O pedido administrativo não foi enviado. A RDD da bolsa pelo IVS público
permanece bloqueada, mas o diagnóstico foi corrigido em 09/09/2026: a regra
administrativa **é** determinística — o rótulo de IVS determina a faixa em 527 de
527 municípios — e o que falta é o **escore contínuo** que gera essa categoria.
Nenhuma regra de corte sobre o IVS 2010 do IPEA pode recuperá-lo; o teto
demonstrado é 78,0%. Isso não bloqueia o trabalho curto.
**Nenhum pedido foi enviado e nenhum efeito RDD da bolsa foi estimado.**

O núcleo causal agora é o cutoff de seleção por escore. A amostra principal
compara o último selecionado ao primeiro não selecionado na mesma primeira
opção, em ampla concorrência, exclui empates e exige diferença exata de um
ponto.

## Portões executados

| Etapa | Estado | Evidência/decisão |
|---|---|---|
| A8-P0 | `CONCLUIDO_RETROSPECTIVO` | pergunta, estimando, amostra, outcomes e linguagem proibida congelados após abertura prévia dos outcomes no A7 |
| A8-P1 | `APROVADO_SUPORTE` | 36 pares em 2025: 30 na chamada 1 e 6 na chamada 2 |
| A8-P2 | `APROVADO_SEM_EMPATES` | ampla concorrência, primeira opção, gap de um ponto; desempates por UF/idade não determinam os pares principais |
| A8-P3 | `ESTIMADO` | +63,9 p.p. em homologação e +33,3 p.p. em presença ativa no mesmo curso–CNES |
| A8-P4 | `APROVADO_DIAGNOSTICOS` | placebo abaixo nulo; gaps alternativos e leave-one-out sem inversão de sinal |
| A8-P5 | `REPLICACAO_DIRECIONAL` | 11 pares em 2026; +36,4 p.p. em presença ativa, teste exato `p=0,125` |
| A8-P6 | `AUDITADO` | outputs agregados sem PII, hashes de entrada e testes automatizados |
| RDD-IVS | `ARQUIVADO_ESCORE_NAO_OBSERVADO` | a regra é determinística (527/527), mas nenhuma regra de corte sobre o IVS 2010 público a recupera: teto de 78,0% para qualquer regra de dois cortes |
| Pedido administrativo | `CANCELADO_NAO_ENVIADO` | nenhum recebimento ou espera integra o plano atual |

## Resultado e alcance

Sob comparabilidade local, ganhar marginalmente a vaga de primeira opção
aumentou a adesão e a presença posterior naquele curso–CNES. O grau de rigor é
**moderado**: a comparação é muito próxima e institucionalmente bem definida,
mas o score é discreto, a amostra é pequena e a hipótese de comparabilidade
entre candidatos separados por um ponto não é integralmente testável.

O resultado não identifica o efeito da bolsa, do IVS, do programa sobre o
estoque geral, da decisão de se candidatar nem retenção individual contínua.

## Próxima ação interna

Redigir o trabalho curto com:

1. A4 como motivação descritiva do gradiente territorial;
2. A8 como resultado causal principal;
3. replicação de 2026, placebos e sensibilidades como validação;
4. A5 no apêndice como evidência associativa, sem usá-la para reforçar
   causalidade;
5. RDD-IVS e DDD apenas como rotas avaliadas e descartadas.

O plano completo está em
[`17_plano_causal_publico_cutoff_escore.md`](../05_identificacao/17_plano_causal_publico_cutoff_escore.md).
