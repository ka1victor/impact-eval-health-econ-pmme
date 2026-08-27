# A04 — Regras financeiras e pagamentos públicos

## Pré-requisitos

Leia `AGENTS.md`, `CLAUDE.md`, `prompts/aquisicao_dados/README.md` e as duas
auditorias. Trabalhe em worktree isolado.

## Missão

Determinar se fontes oficiais públicas permitem observar a dose financeira do
PMM-E por vaga, profissional e competência. Procure atos normativos, portais de
transparência, execução orçamentária, dados abertos e relatórios oficiais.

Preserve a separação entre valor anunciado, valor devido, empenhado, liquidado e
pago. Despesa agregada do programa não é pagamento individual; faixa corrente
não é histórico de dose.

## Campos necessários

- identificador pseudonimizado de vaga e profissional, quando disponível;
- competência e data do pagamento;
- componente fixo, componente variável e ajuda de custo;
- faixa e regra aplicadas;
- valor devido e valor pago;
- suspensão, glosa, estorno, retroativo e correção;
- unidade gestora, ação orçamentária e fonte;
- cobertura e regime de atualização da fonte.

Minimize dados pessoais. Não replique CPF, conta bancária ou outro identificador
sensível em outputs processados. Não tente reidentificar beneficiários.

## Entregáveis exclusivos

- brutos em `data/raw/aquisicao/pagamentos/`;
- script idempotente em `scripts/aquisicao/a04_adquirir_pagamentos.py`;
- `output/aquisicao/a04_manifesto_pagamentos.json`;
- `output/aquisicao/a04_matriz_dose_financeira.json`;
- `docs/auditorias/aquisicao/A04_pagamentos.md`.

O relatório deve mostrar o nível mais desagregado realmente disponível, o
período, a chave, a diferença entre regra e execução e se há ligação defensável
com a vaga e o CNES. Se só houver totais, documente-os como fonte inadequada para
o primeiro estágio individual, sem convertê-los em dose média presumida.

## Critério de aceite

Concluir se o tratamento pode ser medido como (a) faixa anunciada, (b) valor
devido ou (c) valor recebido. Não estimar primeiro estágio nem efeitos.

Não altere documentação compartilhada, `run_all.py` ou arquivos de outro agente.
Valide, faça commit próprio e informe hash e bloqueios; não faça push ou merge.

