# Estado executado do novo plano causal

> **Data:** 2026-10-14.
> **Estado geral:** `R1_R2_EXECUTADOS_AGUARDANDO_R3`.

## Portões e ações

| Etapa | Estado | Evidência/decisão |
|---|---|---|
| P0 | `CONCLUIDO` | síntese, diagnóstico público e plano causal versionados |
| P1 | `PRONTO_NAO_ENVIADO` | pacote completo e não enviado; deixou de ser pré-condição do R1, pois o IVS administrativo é público |
| R1 | `APROVADO_SHARP` | IVS administrativo reproduz 4103/4103 município-onda-versão; IVS 2010 público segue reprovado |
| R2 | `VIAVEL_CONTINUIDADE_COM_RESSALVAS` | suporte, seleção na oferta, balanço e PMMB sem outcomes; potência limitada |
| R3 | `PENDENTE_AUTORIZACAO_DO_AUTOR` | rascunho do protocolo em docs/05_identificacao/18; nenhum registro congelado |
| R4 | `BLOQUEADO_ATE_R3` | nenhum efeito RDD de atração estimado |
| R5 | `FORA_DO_NUCLEO_CURTO` | presença/retenção depende de eventos válidos e só segue após R4 |

## O que já está estabelecido

- R1 com o IVS administrativo da SGTES reproduz a faixa anunciada em 4103 de 4103 combinações município–onda–versão, de 2025 e 2026. A regra é a do item 11.2 do Edital SGTES/MS nº 28/2026, com os cortes 0,300 e 0,400.
- O R1 público com o IVS 2010 do Atlas continua reprovado: 177 de 368 municípios (48.1%) divergem. O IVS 2010 não é a running variable administrativa.
- R2 sem outcomes: `VIAVEL_CONTINUIDADE_COM_RESSALVAS`. Cortes viáveis: 0.300, 0.400. O estimador principal candidato é local-linear; a randomização local não balanceia em janela com suporte suficiente.
- A alternativa A7 contém 423 pares, mas continua preliminar até a observação dos desempates e das chaves estáveis.
- O pacote focal de solicitação continua no repositório e nenhum pedido foi enviado; ele deixou de ser pré-condição do R1.

## Próxima ação

As rodadas de 01/10 e 05/10 foram revisadas e integradas (S1a, S1b e S2 de prompts/integracao_rodadas_outubro_2026/README.md). A próxima sessão é a S6 (prompts/integracao_rodadas_outubro_2026/04_conciliar_e_decidir.md): conciliar com a rodada de 14/10, que mostrou que o IVS administrativo é o IVS 2010 oficial e já estimou a RDD por protocolo próprio, e levar ao autor as decisões sobre running variable, papel do R3 (docs/05_identificacao/18_protocolo_r3_rdd_bolsa_rascunho.md) e pendências de 01/10.

## Regra de parada

Protocolo R3 só pode existir com R1 aprovado e R2 viável; resultado R4 só pode existir com protocolo R3 congelado. Até aqui nenhum efeito RDD de atração foi estimado, e a ordem foi verificada nesta execução.

## Verificações de reprodutibilidade

Este documento é gerado por `scripts/rdd_bolsa/02_controlar_execucao_plano_causal.py`. As verificações curadas de reprodutibilidade do estado validado ficam em [`38_verificacoes_reprodutibilidade.md`](38_verificacoes_reprodutibilidade.md).
