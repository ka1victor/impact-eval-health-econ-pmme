# Prompt 01 — Auditoria institucional do tratamento

Você está trabalhando no repositório `impact-eval-health-econ-pmme`.

Leia integralmente `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/01_pergunta_escopo/04_escopo_eficacia_operacional.md` e `docs/06_execucao/05_roadmap_execucao.md` antes de agir.

## Missão

Determinar qual é o tratamento causal do estudo. Não estime efeitos e não construa resultados empíricos.

Investigue em fontes oficiais atuais — legislação, portarias, editais, anexos, retificações e documentos do Ministério da Saúde — como foram definidos:

- participação no PMM-E;
- regiões e vagas prioritárias;
- faixas de atração;
- valores e benefícios;
- critérios de vulnerabilidade;
- versão do IVS utilizada;
- cutoffs;
- cronologia dos chamamentos;
- exceções ou decisões discricionárias.

Determine se uma mudança no IVS altera:

1. participação no programa;
2. somente o incentivo marginal;
3. oferta ou composição das vagas;
4. vários componentes simultaneamente;
5. ou nada de forma suficientemente determinística.

O IVS 2010 do IPEA é a running variable canônica. Não o substitua e não presuma cutoffs usados por sessões anteriores.

## Entregáveis

- `docs/auditorias/01_regra_institucional.md`;
- tabela auditável de regras, datas, cutoffs e fontes;
- fluxograma da alocação;
- classificação do estimando possível:
  - efeito da elegibilidade ao programa;
  - efeito do incentivo adicional;
  - efeito de um pacote;
  - ausência de contraste causal;
- lista explícita de ambiguidades ainda não resolvidas;
- manifestação sobre a plausibilidade de sharp RDD, fuzzy RDD, outro desenho ou nenhum desenho causal.

Use links oficiais próximos às afirmações. Diferencie texto legal, regra administrativa e inferência do pesquisador. Não invente regras ausentes.

## Limites

- Não estimar efeitos.
- Não construir outcome.
- Não modificar dados brutos.
- Não iniciar WP3, WP4 ou WP5.
- Não fazer push ou merge.

Ao final, valide os documentos, faça commit próprio e informe hash, arquivos alterados, evidências centrais e bloqueios.
