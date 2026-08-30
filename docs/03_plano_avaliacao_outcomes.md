# 03. Plano de avaliação dos outcomes

> **Status:** agenda de longo prazo, sem tarefas autorizadas na primeira versão.
> O plano corrente e mínimo está em
> [`05_roadmap_execucao.md`](05_roadmap_execucao.md).
>
> Agenda ampla de outcomes do projeto. Ela não é a fila operacional da primeira
> versão e não fixa RDD antes da auditoria institucional.

O desenho anterior foi restringido à cobertura sustentada, seus mecanismos,
adicionalidade e uma heterogeneidade por infraestrutura anterior. Ele está
preservado em [`04_escopo_eficacia_operacional.md`](04_escopo_eficacia_operacional.md).
O plano mínimo vigente está em [`05_roadmap_execucao.md`](05_roadmap_execucao.md).
As frentes abaixo formam apenas a agenda posterior.

## 1. Visão geral

```text
DESENHO ANTERIOR CONGELADO
WP0 Regra e exposição
  → WP1 Provimento e retenção
  → WP2 somente infraestrutura prévia
  → WP6 somente heterogeneidade, remanejamento e síntese

BACKLOG POSTERIOR
WP3 Acesso, fila e geografia
WP4 Linhas clínicas
WP5 Custos e bem-estar
```

WP0 e WP1 são bloqueadores. Sem saber quais vagas receberam qual incentivo e se houve capacidade adicional, não existe tratamento bem definido para os outcomes seguintes.

## 2. WP0 — regra institucional e mapa de exposição

### Objetivo

Reconstruir a regra real de oferta e remuneração em nível vaga-especialidade-chamamento.

### Tarefas

1. Tabular todos os editais, anexos e retificações.
2. Identificar elegibilidade, prioridade, faixa, valor e demais benefícios.
3. Mapear vagas, CNES, especialidade, município e calendário.
4. Verificar se os cortes do IVS alteram apenas o incentivo ou também elegibilidade/composição.
5. Testar continuidade da oferta e de covariáveis nos cortes.

### Entregável

Painel `vaga_especialidade_chamamento` com regra auditável e relatório que decide se o IVS permite sharp RDD, fuzzy RDD, desenho de encorajamento ou nenhum deles.

### Portão

Não usar RDD se a oferta de vagas, especialidades ou outros benefícios mudar de modo não separável no mesmo corte.

## 3. WP1 — provimento, entrada, retenção e FTE

### Objetivo

Estimar o primeiro estágio real da política.

### Tarefas

1. Construir funil vaga → candidato → convocado → aceite → entrada.
2. Medir tempo até preenchimento.
3. Montar painel individual de sobrevivência, com censura.
4. Vincular CNES pré e pós para horas e outros vínculos.
5. Separar entrada líquida de relocalização de médicos já atuantes.
6. Estimar heterogeneidade por especialidade, região, distância e IVS.

### Outputs

- cobertura da vaga nos primeiros 180 dias, outcome primário;
- probabilidade de preenchimento;
- tempo até entrada;
- saída, vacância posterior e rotatividade em 180 dias;
- FTE líquido municipal e regional.

### Portão

Sem descontinuidade/exposição relevante em entrada ou FTE, interromper atribuição dos outcomes a jusante ao incentivo do IVS e buscar outro desenho.

## 4. WP2 — capacidade e produção observada

> **Execução parcial agora:** somente CNES e infraestrutura pré-tratamento necessários para FTE, adicionalidade e heterogeneidade. Produção SIA/SIH permanece na agenda posterior.

### Objetivo

Verificar se profissionais presentes geram capacidade e produção adicionais.

### Tarefas

1. Construir CNES-estabelecimento-especialidade-mês pré e pós.
2. Vincular produção do SIA/SIH aos estabelecimentos e cursos do programa.
3. Harmonizar códigos antes/depois da OCI.
4. Medir consultas, exames, procedimentos e cirurgias observados.
5. Testar substituição entre prestadores e entre municípios.
6. Verificar capacidade instalada prévia e ativação de turnos/equipamentos.

### Portão

Não chamar produção de “atribuível” se não houver ligação temporal, especialidade compatível e contraste contrafactual.

## 5. WP3 — acesso, fila e geografia

> **Guardado:** não adquirir dados, criar scripts ou estimar este WP no estudo atual. Veja [`06_backlog_wp3_wp4_wp5.md`](06_backlog_wp3_wp4_wp5.md).

### Objetivo

Responder diretamente se o paciente espera menos, recebe mais cuidado e viaja menos.

### Tarefas

1. Construir coortes de solicitações por especialidade/procedimento.
2. Medir mediana e cauda do tempo de espera.
3. Medir atendimento em 30/60/90 dias e cancelamentos.
4. Construir fluxos residência-prestador mensais.
5. Decompor $Q_{global}=Q_{local}+Q_{externo}$.
6. Calcular distância e tempo dos atendimentos efetivos.
7. Avaliar efeitos sobre hospitais polos e municípios vizinhos.

### Resultados possíveis

- expansão de acesso com fila menor;
- substituição espacial com benefício de proximidade;
- produção maior sem fila menor;
- localização melhor, mas acesso global pior;
- nenhum efeito detectável com intervalo informativo ou impreciso.

Nenhum padrão será resumido automaticamente como sucesso/fracasso global.

## 6. WP4 — linhas clínicas

> **Guardado:** não selecionar linha clínica, vincular bases ou estimar este WP no estudo atual. Veja [`06_backlog_wp3_wp4_wp5.md`](06_backlog_wp3_wp4_wp5.md).

### Objetivo

Verificar se acesso mais oportuno altera processos e desfechos específicos.

### Sequência

1. Escolher linhas com correspondência clara entre cursos do PMM-E e dados observáveis.
2. Pré-especificar uma cadeia curta por linha: exame → diagnóstico → terapia → desfecho.
3. Avaliar tempo e conclusão da cadeia antes de desfechos finais.
4. Incorporar estadiamento, caráter da internação, complicação e reinternação.
5. Usar horizontes clínicos plausíveis.

### Prioridade sugerida

1. Cirurgia/anestesiologia, pela concentração observada de participantes.
2. Oncologia/diagnóstico, se APAC e ligação terapia estiverem disponíveis.
3. Saúde da mulher e digestiva, com conclusão da investigação.
4. Cardiologia, se houver definição de internação evitável específica.

A concentração de profissionais define prioridade de investigação, não expectativa de efeito.

## 7. WP5 — custos e bem-estar

> **Guardado:** não construir cenários, adquirir dados ou estimar este WP no estudo atual. Veja [`06_backlog_wp3_wp4_wp5.md`](06_backlog_wp3_wp4_wp5.md).

### Objetivo

Comparar custos incrementais com acesso, tempo e saúde efetivamente produzidos.

### Tarefas

1. Definir perspectivas federal, municipal, SUS e social.
2. Estimar custos do programa e do uso adicional de serviços.
3. Microcustear transporte em amostra representativa.
4. Medir tempo do paciente e acompanhante.
5. Quantificar capacidade liberada nos polos sem tratá-la como economia automática.
6. Fazer análise probabilística de sensibilidade.
7. Calcular custo-efetividade apenas para desfechos clínicos estimados.

## 8. WP6 — síntese, equidade e transbordamentos

> **Execução parcial agora:** uma heterogeneidade confirmatória por infraestrutura prévia, decomposição contábil de remanejamento e síntese. Atribuição causal de spillovers regionais amplos permanece para trabalho posterior.

### Tarefas

1. Definir famílias de outcomes e primários antes da estimação final.
2. Corrigir multiplicidade dentro de cada família.
3. Reportar efeitos e intervalos, não apenas significância.
4. Testar heterogeneidade pré-especificada por IVS, região e capacidade inicial.
5. Somar efeitos municipais e transbordamentos para obter efeito regional líquido.
6. Produzir uma matriz final de evidência por elo causal.

## 9. Estratégia de identificação: decisão condicional

| Situação institucional | Estratégia candidata |
|---|---|
| Incentivo muda deterministicamente no IVS e oferta é contínua | Sharp RDD para intenção de tratamento local |
| Incentivo muda, mas entrada/FTE responde imperfeitamente | Fuzzy RDD, com primeiro estágio observado |
| Vagas entram em datas escalonadas com regra comparável | Evento/painel com testes de pré-tendência |
| Seleção de vagas depende de capacidade e necessidade | Pareamento/ponderação mais painel, com interpretação associativa forte ou desenho alternativo |
| Não há contraste plausível | Descrição rigorosa; não promover causalidade |

O IVS 2010 continuará sendo a running variable canônica quando a regra institucional justificar RDD. Não será substituído por IDHM ou renda.

## 10. Ordem prática das próximas sessões

1. Fechar WP0 e determinar se o contraste identifica participação, pacote ou incentivo marginal.
2. Obter o universo de vagas e reconstruir trajetórias de 180 dias.
3. Resolver identidade longitudinal e CNES para FTE, vínculos anteriores e infraestrutura prévia.
4. Definir a mínima mudança substantivamente relevante e executar análise de potência.
5. Pré-especificar outcome primário, decomposição, uma heterogeneidade confirmatória e regras de linguagem.
6. Estimar o efeito sobre cobertura sustentada e só então decompor os modos de falha.
7. Tratar remanejamento inicialmente como decomposição contábil; ampliar a identificação apenas se os dados sustentarem.

Fila, produção assistencial, clínica e custos ficam adiados conforme [`06_backlog_wp3_wp4_wp5.md`](06_backlog_wp3_wp4_wp5.md). O primeiro produto publicável será a avaliação de quando o incentivo produz capacidade médica sustentada e adicional. A execução deve seguir os prompts ordenados em [`../prompts/README.md`](../prompts/README.md).
