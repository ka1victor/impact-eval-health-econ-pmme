# A03 — IVS e regra administrativa do tratamento

## Pré-requisitos

Leia `AGENTS.md`, `CLAUDE.md`, `prompts/aquisicao_dados/README.md`,
`docs/auditorias/01_regra_institucional.md` e
`docs/auditorias/02_disponibilidade_dados.md`. Trabalhe em worktree isolado.

## Missão

Obter a documentação e os dados públicos que mostrem como a administração
atribuiu faixa e incentivo a cada vaga. A base local de IVS 2010 é candidata à
running variable; não presuma que foi a versão, precisão ou transformação usada
pelo PMM-E.

Busque editais e anexos em todas as versões, notas técnicas, memórias de cálculo,
dicionários, decisões de priorização, quadros com escore, respostas oficiais e a
versão exata do IVS usada. Preserve originais e retificações.

## Informações necessárias

- indicador e componente usados, fonte, ano/vintagem e data de extração;
- precisão antes e depois do arredondamento;
- cutoff, lado do cutoff, intervalos e tratamento de igualdade;
- regra para casos ausentes, novos municípios e mudanças territoriais;
- escore, categoria e faixa atribuídos a cada vaga/CNES;
- outras regras que também determinem faixa, valor, priorização ou oferta;
- data e versão da decisão administrativa;
- exceções, revisão manual e possibilidade de recurso.

Compare a classificação administrativa apenas para auditar a regra. Não
substitua IVS por IDHM, PIB ou outro índice e não recalcule silenciosamente a
faixa a partir do arquivo local.

## Entregáveis exclusivos

- brutos em `data/raw/aquisicao/ivs_regra/`;
- script idempotente em `scripts/aquisicao/a03_adquirir_ivs_regra.py`;
- `output/aquisicao/a03_manifesto_ivs_regra.json`;
- `output/aquisicao/a03_matriz_regra_tratamento.json`;
- `docs/auditorias/aquisicao/A03_ivs_e_regra.md`.

O relatório deve declarar separadamente se foi identificado: (a) cutoff
normativo; (b) escore administrativo por vaga; (c) primeiro estágio em valor
anunciado; (d) valor recebido. Informe divergências com a base local e quantas
vagas ficariam ambíguas por arredondamento, sem estimar efeitos.

## Critério de aceite

Classificar o contraste como participação, pacote, incentivo marginal ou ainda
indeterminado e dizer se um RDD pode sequer ser especificado. Resultado negativo
é válido se todas as fontes e consultas estiverem registradas.

Não altere documentação compartilhada, `run_all.py` ou arquivos de outro agente.
Valide, faça commit próprio e informe hash e bloqueios; não faça push ou merge.

