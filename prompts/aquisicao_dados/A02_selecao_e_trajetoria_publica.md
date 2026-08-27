# A02 — Seleção e trajetória administrativa pública

## Pré-requisitos

Leia `AGENTS.md`, `CLAUDE.md`, `prompts/aquisicao_dados/README.md` e
`docs/auditorias/02_disponibilidade_dados.md`. Trabalhe em worktree isolado.

## Missão

Localizar e preservar todas as publicações oficiais que observem etapas entre a
inscrição e o encerramento do exercício no PMM-E: candidaturas, preferências,
classificação, convocação, aceite, recusa, homologação, entrada, afastamento,
retorno, transferência, desistência, desligamento e reocupação.

Inclua quadros dos chamamentos, comunicados, listas de homologação, versões do
portal de dados abertos e snapshots oficiais. Não trate cronograma coletivo como
data individual e não trate ausência em uma lista posterior como saída.

## Unidade e chaves procuradas

A unidade desejada é um evento com:

- `id_evento`, `id_vaga` e `id_profissional_pseudo`, quando publicados;
- ciclo, chamada, CNES, município, curso e preferência;
- timestamp ou data de vigência;
- estado anterior, estado novo e motivo;
- fonte e versão do registro.

Nomes, CRM, CPF mascarado e CNS podem ser inventariados como chaves presentes,
mas não devem ser propagados para outputs processados desnecessariamente. Não
faça record linkage probabilístico e não declare duas pessoas iguais apenas por
nome normalizado.

## Entregáveis exclusivos

- brutos em `data/raw/aquisicao/trajetoria/`;
- script idempotente em `scripts/aquisicao/a02_adquirir_trajetoria.py`;
- `output/aquisicao/a02_manifesto_trajetoria.json`;
- `output/aquisicao/a02_matriz_eventos_publicos.json`;
- `docs/auditorias/aquisicao/A02_selecao_e_trajetoria.md`.

A matriz deve cruzar ciclo/chamada com cada evento necessário, distinguindo
`observado individualmente`, `inferível mas inadequado`, `somente agregado`,
`não localizado` e `link quebrado`. Informe se existe uma chave estável entre as
etapas e se os eventos permitem spells e `cobertura_90/120/180`.

## Critério de aceite

Concluir explicitamente quais componentes de preenchimento, tempo até entrada,
permanência, rotatividade e reocupação são mensuráveis só com fontes públicas.
Não estimar nenhuma taxa e não transformar estoque de ativos em trajetória.

Não altere documentação compartilhada, `run_all.py` ou arquivos de outro agente.
Valide, faça commit próprio e informe hash e bloqueios; não faça push ou merge.

