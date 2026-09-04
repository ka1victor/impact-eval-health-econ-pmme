# Pedido focal — corte de seleção de especialistas

> Status: **`não enviado`**. Este é o pacote mínimo para avaliar um trabalho causal curto sobre atração e presença posterior. Ele não solicita endereço nem data de nascimento.

## Finalidade

Reproduzir a ordem final de seleção em cada vaga e estimar, se os portões passarem, o efeito local de ganhar a primeira opção sobre início no PMM-E e presença ativa posterior.

## Tabela `cutoff_candidatos.csv`

Uma linha por inscrição–opção na versão final após recursos.

| Campo | Definição |
|---|---|
| `id_inscricao_pseudo` | chave estável da inscrição |
| `id_profissional_pseudo` | chave estável do profissional entre seleção e eventos |
| `id_vaga_pseudo` | chave estável da vaga física/curso–CNES |
| `ciclo`, `chamada` | estágio do chamamento |
| `ordem_opcao` | primeira ou segunda opção |
| `modalidade` | ampla concorrência, cota ou remanescente |
| `barema_final` | pontuação validada após recursos |
| `prioridade_mesma_uf` | indicador usado no primeiro desempate, calculado pelo controlador |
| `distancia_etaria_cutoff_dias` | idade em dias menos idade do último selecionado no mesmo bloco; não fornecer data de nascimento |
| `classificacao_final` | ordem final aplicada |
| `quantidade_vagas_bloco` | capacidade efetiva por modalidade no processamento |
| `selecionado_primeira_opcao` | resultado da opção |
| `status_recurso` | sem recurso, deferido, indeferido ou sub judice |
| `versao_processamento` | versão do algoritmo/lista |

**Chave:** `id_inscricao_pseudo + id_vaga_pseudo + ordem_opcao + versao_processamento`.

Se não for possível fornecer `distancia_etaria_cutoff_dias`, aceita-se `ordem_desempate_idade` e a idade do cutoff do bloco, desde que o órgão documente como reconstruir distâncias e empates sem revelar a data de nascimento.

## Tabela `cutoff_eventos.csv`

Uma linha por profissional–vaga, com:

| Campo | Definição |
|---|---|
| `id_profissional_pseudo`, `id_vaga_pseudo` | mesmas chaves da seleção |
| `confirmou` e `data_confirmacao` | confirmação administrativa |
| `homologado` e `data_homologacao` | homologação |
| `iniciou` e `data_inicio` | início efetivo |
| `data_saida` | término, quando houver |
| `motivo_saida` | motivo administrativo documentado |
| `ativo_90d`, `ativo_180d` | indicadores calculados a partir dos eventos, com regra descrita |
| `vaga_origem`, `vaga_destino` | realocação, quando houver |

Ausência de evento não deve ser convertida automaticamente em zero. O dicionário precisa distinguir não ocorrência, desconhecido e não aplicável.

## Documentação solicitada

- algoritmo ou pseudocódigo de processamento das duas opções;
- ordem entre cotas, ampla concorrência e vagas remanescentes;
- regra aplicada a empates completos;
- histórico de recursos e listas sub judice;
- capacidade antes e depois de cancelamentos/realocações;
- data de corte, dicionário, versões e hashes.

## Portão de liberação

O desenho só recebe linguagem causal se:

1. a classificação publicada for reproduzida integralmente;
2. houver suporte suficiente em blocos de mesmo barema e mesma prioridade de UF;
3. a potência for calculada antes de abrir os outcomes;
4. covariáveis prévias forem localmente balanceadas;
5. recursos, cotas e cancelamentos não criarem outra mudança no cutoff;
6. o vínculo entre seleção e eventos for determinístico pelas chaves pseudonimizadas.

Se qualquer item falhar, os resultados públicos A7 permanecem descritivos.
