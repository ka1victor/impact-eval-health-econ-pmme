# Avaliação de impacto do Mais Médicos Especialistas

Este repositório organiza uma avaliação causal do Projeto Mais Médicos Especialistas (PMM-E). A [Lei 12.871/2013, em sua redação atual](https://www2.camara.leg.br/legin/fed/lei/2013/lei-12871-22-outubro-2013-777279-normaatualizada-pl.html), enquadra a redução da carência regional de médicos e a qualificação da assistência especializada entre os objetivos do Programa Mais Médicos. A [Lei 15.233/2025](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15233.htm) criou o projeto de especialistas para prover profissionais em regiões prioritárias com vistas à redução do tempo de espera no SUS.

Por isso, a pergunta central não é apenas quantos médicos aparecem no programa. É se o provimento amplia, de fato, o acesso oportuno e resolutivo à atenção especializada — e não apenas desloca médicos, pacientes ou procedimentos entre municípios.

## Estado atual

O projeto está na fase de desenho e prontidão dos dados. Ainda não há resultado causal validado. O pipeline atual produz somente um inventário auditável das bases observadas; números de sessões anteriores que dependiam de dados simulados, premissas não documentadas ou inferências incompatíveis com as bases disponíveis foram removidos dos arquivos correntes. O histórico do Git foi preservado.

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
| Vagas, candidaturas e preenchimento | Relação de profissionais ativos em 12/08/2026 | Editais, vagas ofertadas, candidatos, convocações e recusas | Não mensurável |
| Entrada de especialistas | Data de início dos vínculos ativos e série municipal agregada | Estoque pré-programa comparável, vínculo individual longitudinal e regra de exposição | Parcial |
| Retenção e duração | Série agregada mensal por município entre dez/2025 e ago/2026 | Identificador longitudinal, desligamentos, transferências e carga horária | Não mensurável |
| Oferta líquida de trabalho | Contagem de vínculos ativos | Horas/FTE, vínculos anteriores, substituições e demais vínculos CNES | Não mensurável |
| Produção e capacidade | Nenhuma base assistencial no repositório | SIA/SUS, SIH/SUS, CNES e definição de procedimentos-alvo | Não mensurável |
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

A execução será feita em três fases com portões:

1. auditorias institucional e de dados;
2. protocolo congelado;
3. painéis de vagas e CNES;
4. estimação causal;
5. red team e síntese.

O roadmap canônico está em [docs/05_roadmap_execucao.md](docs/05_roadmap_execucao.md), os itens adiados em [docs/06_backlog_wp3_wp4_wp5.md](docs/06_backlog_wp3_wp4_wp5.md) e os prompts executáveis em [prompts/README.md](prompts/README.md).

O desenho amplo permanece em [docs/03_plano_avaliacao_outcomes.md](docs/03_plano_avaliacao_outcomes.md). As definições de outcomes e estimandos estão em [docs/01_outcomes_e_estimandos.md](docs/01_outcomes_e_estimandos.md), o inventário de dados e lacunas em [docs/02_inventario_dados_por_outcome.md](docs/02_inventario_dados_por_outcome.md), e o escopo causal prioritário em [docs/04_escopo_eficacia_operacional.md](docs/04_escopo_eficacia_operacional.md).

## Executar o estado validado do projeto

```bash
python run_all.py
```

No estágio atual, isso gera `output/inventario_dados.json`, com hashes, cobertura das bases e disponibilidade de cada outcome. Novas etapas só devem entrar no pipeline quando usarem dados observados, tiverem proveniência documentada e responderem a um estimando definido.

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
