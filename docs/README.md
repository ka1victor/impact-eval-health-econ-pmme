# Documentação do PMM-E

> **Finalidade:** separar pergunta, literatura empírica, teoria econômica, hipótese, dados, identificação e resultados, seguindo a arquitetura do trabalho autoral.

## 1. Regra de navegação

Pergunta e contexto → literatura empírica → viabilidade empírica → dados e descritivas.

Pergunta e contexto → literatura teórica → modelo microeconômico → hipóteses econômicas.

Dados e hipóteses → metodologia e identificação → resultados, robustez e discussão.

A literatura empírica informa fatos, comparações, covariáveis candidatas e heterogeneidades. A literatura teórica fornece primitivas e mecanismos. O modelo autoral deriva hipóteses. A metodologia traduz essas hipóteses em estimandos e especificações. Nenhum desses blocos substitui outro.

## 2. Seções e documentos canônicos

| Seção | Documentos | Função |
|---|---|---|
| [01 — Pergunta e escopo](01_pergunta_escopo/) | [outcomes e estimandos](01_pergunta_escopo/01_outcomes_e_estimandos.md), [escopo operacional](01_pergunta_escopo/04_escopo_eficacia_operacional.md), [dossiê executivo](01_pergunta_escopo/13_dossie_executivo_avaliacao_impacto_pmme.md) e [pergunta do artigo](01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md) | definir pergunta, sucesso, estimandos e limites do estudo |
| [02 — Teoria](02_teoria/) | [modelo microeconômico](02_teoria/17_fundamentacao_teorica_formacao_utilidade_regressores.md) e [versão para slides](02_teoria/18_modelo_teorico_slides_apresentacao.md) | apresentar primitivas, derivações, hipóteses e extensões autorais |
| [03 — Literatura empírica](03_literatura_empirica/) | [catálogo de escolha locacional de médicos](03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md) | reunir fatos e evidência externa, incluindo Diamond, Moehling e Costa–Nunes–Sanches |
| [04 — Dados](04_dados/) | [inventário por outcome](04_dados/02_inventario_dados_por_outcome.md) e [pedidos administrativos](pedidos_dados/) | mapear fontes, layouts, chaves e critérios de completude |
| [05 — Identificação](05_identificacao/) | [plano amplo](05_identificacao/03_plano_avaliacao_outcomes.md), [estratégia prospectiva](05_identificacao/12_estrategia_causal_prospectiva_ciclo3.md), [pré-análise](05_identificacao/13_plano_pre_analise_ciclo3.md) e [RDD da bolsa](05_identificacao/14_plano_implementacao_rdd_bolsa.md) | registrar identificação, estimandos e especificações econométricas |
| [06 — Execução](06_execucao/) | [roadmap](06_execucao/05_roadmap_execucao.md) e [backlog](06_execucao/06_backlog_wp3_wp4_wp5.md) | ordenar entregas, portões e frentes adiadas |
| [Auditorias](auditorias/) | auditorias institucionais, de disponibilidade e aquisição | registrar o estado observado dos dados e da implementação |
| [90 — Arquivo histórico](90_arquivo_historico/) | versões anteriores de revisão e modelagem | preservar rastreabilidade sem concorrer com os documentos canônicos |

## 3. Regra de classificação de referências

| Tipo de trabalho | Destino | Pode fundamentar equação teórica? |
|---|---|---:|
| teoria pura ou síntese teórica sem estimação própria | documento 17 | sim, no limite exato do modelo |
| modelo estrutural estimado, experimento, quase-experimento ou estudo observacional | documento 19 | não |
| paper de método econométrico | documentos 12–14 | não; fundamenta o estimador |
| documento normativo ou administrativo | inventário/auditorias | não; fundamenta a regra institucional |

Se um artigo tem teoria e estimação, o projeto o classifica como empírico para evitar contaminação entre blocos. Sua estrutura pode inspirar a ponte teoria–dados, mas não serve como autoridade para primitivas ou sinais.

## 4. Arquivos históricos mistos

Os documentos 07–11, o dossiê 15 de papers e as versões 16 sobre seleção de modelos e “equações dos papers” estão em [`90_arquivo_historico/`](90_arquivo_historico/). Foram produzidos antes desta demarcação e misturam teoria, evidência e econometria.

Eles são **cadernos históricos de trabalho**, não fontes canônicas para a redação final. Equações de Cox, logit/probit, DiD, DDD e RDD neles reproduzidas pertencem à metodologia; resultados de Sivey, Gravelle, Russell, Pathman, Somville, Diamond, Moehling e Costa–Nunes–Sanches pertencem à literatura empírica.

## 5. Checklist antes de incluir uma referência

1. O paper usa dados para estimar, calibrar, testar ou simular parâmetros? Se sim, classificar como empírico.
2. A equação é uma condição de escolha/equilíbrio ou uma regressão/estimador?
3. O sinal decorre de hipóteses declaradas ou foi observado nos dados?
4. A equação foi copiada do paper, adaptada ou criada no projeto? Identificar explicitamente.
5. A proxy é realmente o primitivo teórico? O IVS 2010 não é sinônimo automático de amenidades, necessidade ou custo de vida.
6. A variável é pré-tratamento? Se não, avaliar risco de controle pós-tratamento.

## 6. Regra de precedência

Em caso de conflito:

1. o documento 17 prevalece para teoria;
2. o documento 19 prevalece para classificação da literatura empírica;
3. os documentos 12–14 prevalecem para identificação;
4. as auditorias prevalecem para o estado observado dos dados.
