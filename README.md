# Avaliação de impacto do Mais Médicos Especialistas

Este repositório organiza uma avaliação causal do Projeto Mais Médicos Especialistas (PMM-E). A [Lei 12.871/2013, em sua redação atual](https://www2.camara.leg.br/legin/fed/lei/2013/lei-12871-22-outubro-2013-777279-normaatualizada-pl.html), enquadra a redução da carência regional de médicos e a qualificação da assistência especializada entre os objetivos do Programa Mais Médicos. A [Lei 15.233/2025](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15233.htm) criou o projeto de especialistas para prover profissionais em regiões prioritárias com vistas à redução do tempo de espera no SUS.

Por isso, a pergunta central não é apenas quantos médicos aparecem no programa. É se o provimento amplia, de fato, o acesso oportuno e resolutivo à atenção especializada — e não apenas desloca médicos, pacientes ou procedimentos entre municípios.

## Estado atual

O portão integrado A06 foi concluído com a decisão **`aguardar dados administrativos`**. Ainda não há resultado causal validado e o protocolo empírico não foi liberado. As aquisições públicas recuperaram quadros versionados, resultados administrativos publicados, regras normativas e três competências piloto do CNES, mas não entregaram `id_vaga` estável, log completo de eventos, ponte pseudonimizada PMM-E–CNES, regra administrativa reproduzível do IVS ou pagamentos mensais vinculáveis. A decisão e as nove respostas estão em [docs/auditorias/03_portao_apos_aquisicao.md](docs/auditorias/03_portao_apos_aquisicao.md). Os pacotes A07 foram [preparados](docs/pedidos_dados/README.md), mas permanecem **não enviados**; submissão é decisão externa do autor. O prompt 03 continua bloqueado.

## Escopo empírico prioritário

> Quando o incentivo adicional do PMM-E transforma vagas ofertadas em capacidade médica sustentada e líquida, e quando resulta apenas em ocupação transitória, substituição ou remanejamento?

O estudo prioritário avaliará **eficácia operacional do provimento**. O outcome primário será a proporção dos primeiros 180 dias após a oferta em que a vaga permaneceu coberta, com decomposição em preenchimento, entrada, permanência, rotatividade e FTE líquido. Infraestrutura anterior ao programa será a heterogeneidade confirmatória.

Isso não equivale a avaliar a eficácia global do PMM-E. Produção, espera, saúde e bem-estar são níveis posteriores da cadeia e permanecerão fora da conclusão desse primeiro estudo. A validação crítica do escopo está em [docs/04_escopo_eficacia_operacional.md](docs/04_escopo_eficacia_operacional.md).

## A cadeia de efeitos que queremos testar

O programa precisa atravessar uma sequência para produzir bem-estar:

1. vagas e incentivos atraem especialistas;
2. esses profissionais entram, permanecem e aumentam a oferta líquida de horas;
3. a capacidade adicional vira consultas, exames, cirurgias e cuidado coordenado;
4. filas, tempo de espera e deslocamentos diminuem;
5. diagnóstico e tratamento tornam-se mais oportunos, melhorando a saúde;
6. os benefícios superam custos públicos, privados e logísticos;
7. os ganhos alcançam prioritariamente territórios mais vulneráveis, sem apenas transferir escassez para outros lugares.

Cada seta é uma hipótese empírica. Observar uma etapa não autoriza concluir que as seguintes ocorreram.

## O que temos em cada outcome

| Outcome de interesse | Evidência disponível hoje | O que falta para avaliá-lo | Estado |
|---|---|---|---|
| Vagas, candidaturas e preenchimento | Quadros versionados e resultados publicados, com denominadores por publicação | `id_vaga`, deduplicação entre reapresentações, universo de inscrições, aceite e recusa | Parcial |
| Entrada de especialistas | Data de início dos ativos no corte e etapas administrativas publicadas | Fluxo completo de entradas, inclusive de quem saiu antes do snapshot | Parcial |
| Retenção e duração | Série agregada mensal por município entre dez/2025 e ago/2026 | Identificador longitudinal, desligamentos, transferências e carga horária | Não mensurável |
| Oferta líquida de trabalho | Esquema de vínculos e carga horária em três competências piloto do CNES | Painel mensal completo e ponte pseudonimizada PMM-E–CNES | Não mensurável |
| Produção e capacidade | Esquema piloto do CNES para infraestrutura cadastral | Painel validado; SIA/SUS e SIH/SUS permanecem fora do estudo prioritário | Parcial apenas para infraestrutura |
| Acesso e tempo de espera | Nenhuma base de regulação no repositório | Fila, pedidos, agendamentos, atendimento, cancelamento e prioridade clínica | Objetivo final da política; fora do estudo prioritário |
| Resolutividade local e deslocamento | Município do estabelecimento no retrato nominal | Origem-destino dos pacientes e produção comparável antes/depois | Não mensurável |
| Desfechos clínicos | Nenhuma base clínica no repositório | APAC, SIH, mortalidade e linhas de cuidado com datas clínicas | Não mensurável |
| Custos e bem-estar | Nenhuma base de custos no repositório | Gastos do programa, produção, transporte sanitário e custos de pacientes | Não mensurável |
| Equidade territorial | IVS 2010 para 5.565 municípios | Vincular exposição e outcomes válidos ao IVS | Parcial |
| Spillovers e equilíbrio regional | Localização municipal dos vínculos ativos | Origem dos médicos, mobilidade, municípios vizinhos e oferta regional completa | Não mensurável |

“Parcial” significa que há um componente útil, mas insuficiente para estimar o efeito pretendido.

## O que sabemos pelas bases observadas

- O retrato nominal de 12/08/2026 contém 1.480 registros, 1.478 combinações únicas de UF e CRM, 325 municípios, 518 estabelecimentos CNES e 16 cursos/especialidades registrados.
- A série histórica contém 7.276 linhas, cobre 531 municípios e nove competências entre dezembro de 2025 e agosto de 2026. Ela não contém CNES preenchido e usa 40 rótulos distintos de curso/especialidade.
- A base do IPEA contém o IVS 2010 dos 5.565 municípios, variando de 0,066 a 0,752. O IVS é a running variable canônica do projeto, mas seu uso causal depende da auditoria da regra efetiva de elegibilidade e alocação.

Esses fatos descrevem os arquivos, não o impacto do programa.

## Roadmap de execução

Os sete WPs formam a agenda ampla de outcomes; eles não serão executados em sequência neste estudo. O fluxo corrente é:

```text
WP0 completo
  → WP1 completo
  → WP2 apenas para infraestrutura prévia
  → WP6 apenas para heterogeneidade, remanejamento e síntese
```

WP3 — acesso/fila, WP4 — clínica e WP5 — custos/bem-estar estão guardados e não entram no pipeline atual.

A execução será feita em três fases com portões. Entre a auditoria inicial e o
protocolo haverá um sprint de aquisição pública e, se necessário, pedidos
administrativos:

1. auditorias institucional e de dados;
2. aquisições públicas e portão A06 concluídos; pacotes administrativos A07 preparados, mas não enviados;
3. protocolo congelado, somente após os pedidos serem atendidos e integrados e um novo portão permitir;
4. painéis de vagas e CNES;
5. estimação causal;
6. red team e síntese.

O roadmap canônico está em [docs/05_roadmap_execucao.md](docs/05_roadmap_execucao.md), os itens adiados em [docs/06_backlog_wp3_wp4_wp5.md](docs/06_backlog_wp3_wp4_wp5.md) e os prompts executáveis em [prompts/README.md](prompts/README.md).

O desenho amplo permanece em [docs/03_plano_avaliacao_outcomes.md](docs/03_plano_avaliacao_outcomes.md). As definições de outcomes e estimandos estão em [docs/01_outcomes_e_estimandos.md](docs/01_outcomes_e_estimandos.md), o inventário de dados e lacunas em [docs/02_inventario_dados_por_outcome.md](docs/02_inventario_dados_por_outcome.md), e o escopo causal prioritário em [docs/04_escopo_eficacia_operacional.md](docs/04_escopo_eficacia_operacional.md).

## Executar o estado validado do projeto

```bash
python run_all.py
```

No estágio atual, isso atualiza o inventário das bases, a auditoria das fontes
PMM-E, o plano — sem download automático — das competências CNES e reproduz o
portão A06. O pipeline não executa A07, protocolo ou estimação.

## Estrutura

```text
data/      bases observadas preservadas
docs/      desenho, inventário e plano de avaliação
prompts/   tarefas ordenadas para os agentes executores
scripts/   etapas reprodutíveis do pipeline
output/    produtos gerados; atualmente, somente o inventário
```

## Princípio de interpretação

Nenhum eixo será classificado simplesmente como “deu certo” ou “deu errado”. A conclusão deverá nomear o estimando, a população, o período, o contraste causal, a incerteza e quais elos da cadeia de efeitos foram ou não testados. Aumento local de médicos, por exemplo, pode representar expansão real, substituição de vínculos, remanejamento entre municípios ou mudança cadastral; distinguir essas hipóteses é parte da avaliação.
