# Prompt 05 — CNES, FTE, infraestrutura e remanejamento

Execute somente depois do protocolo congelado e da definição das chaves de ligação.

Leia `AGENTS.md`, `CLAUDE.md`, o roadmap, o protocolo e os relatórios de auditoria.

## Missão

Construir o componente longitudinal do CNES necessário para separar vínculo nominal de capacidade adicional.

Implemente:

- painel profissional–vínculo–mês;
- carga horária e FTE;
- vínculos anteriores e simultâneos;
- município e estabelecimento de origem;
- variação líquida municipal;
- decomposição regional;
- infraestrutura existente antes do tratamento.

A infraestrutura deve ser definida com dados estritamente pré-programa e de forma coerente com a especialidade. Não use atividade posterior para classificar estabelecimentos.

Documente:

- chaves e taxa de ligação;
- falsos positivos e falsos negativos;
- identificadores ausentes;
- mudanças cadastrais;
- múltiplos vínculos;
- regras de FTE;
- limites do rastreamento geográfico.

Remanejamento deve começar como decomposição contábil. Não chame perdas observadas em municípios de origem de efeito causal sem desenho próprio.

## Requisitos de implementação

- Nunca altere dados brutos.
- Grave transformações em `output/`.
- Use caminhos relativos e etapas determinísticas.
- Gere dicionário, hashes, reconciliações e testes de consistência.
- Atualize `run_all.py` somente com etapas reproduzíveis.

## Limites

- Não estimar ainda o efeito principal.
- Não criar infraestrutura com variáveis pós-tratamento.
- Não iniciar produção assistencial de WP2 nem WP3, WP4 ou WP5.
- Não fazer push ou merge.

Ao final, valide outputs, faça commit próprio e informe hash, taxas de ligação e limitações.
