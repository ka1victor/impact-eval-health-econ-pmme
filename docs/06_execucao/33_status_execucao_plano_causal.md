# Estado executado do novo plano causal

> **Data:** 2026-09-04.
> **Estado geral:** `PARCIAL_EXECUTADO_AGUARDANDO_DADOS_ADMINISTRATIVOS`.

## Portões e ações

| Etapa | Estado | Evidência/decisão |
|---|---|---|
| P0 | `CONCLUIDO` | síntese, diagnóstico público e plano causal versionados |
| P1 | `PRONTO_NAO_ENVIADO` | texto focal, layouts e pedidos técnicos completos; falta canal autorizado |
| R1 | `REPROVADO_PENDENTE_DE_RECONSTRUCAO` | matriz municipal e portão público reproduzíveis |
| R2 | `BLOQUEADO_POR_R1` | não abrir outcomes; escore administrativo ainda ausente |
| R3 | `BLOQUEADO_ATE_R1_R2` | pré-análise prospectiva não criada prematuramente |
| R4 | `BLOQUEADO_ATE_R1_R3` | nenhum efeito RDD de atração estimado |
| R5 | `FORA_DO_NUCLEO_CURTO` | presença/retenção depende de eventos válidos e só segue após R4 |

## O que já está estabelecido

- R1 público auditou 368 municípios: 177 faixas (48.1%) não são reproduzidas pela taxonomia externa.
- A fuzzy pública também está reprovada: o valor anunciado não salta de forma estável no IVS disponível.
- A alternativa A7 contém 423 pares, mas continua preliminar até a observação dos desempates e das chaves estáveis.
- O pacote focal de solicitação está completo no repositório, mas nenhum pedido foi enviado.
- A triagem administrativa está em `AGUARDANDO_RECEBIMENTO`; foram recebidos 0 arquivos.

## Próxima ação externa necessária

O autor precisa escolher e autorizar o canal de submissão ao Ministério da Saúde. Após o recebimento, os bytes devem ser preservados fora do controle de versão em `data/raw/administrativo_rdd_bolsa/`; R1 será repetido antes de qualquer outcome.

## Regra de parada

Enquanto R1 não for `APROVADO_SHARP` ou `APROVADO_FUZZY`, não criar pré-análise R3 nem resultados R4. A ausência desses artefatos foi verificada nesta execução.
