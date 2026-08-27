# A01 — Universo de vagas e versionamento público

## Pré-requisitos

Leia `AGENTS.md`, `CLAUDE.md`, `prompts/aquisicao_dados/README.md` e
`docs/auditorias/02_disponibilidade_dados.md`. Parta do commit comum definido
pelo coordenador e trabalhe em worktree isolado.

## Missão

Recuperar o universo público de vagas do PMM-E e todas as versões localizáveis
dos quadros, inclusive originais, retificações, retiradas e reapresentações. A
prioridade é recuperar os dois arquivos de 2025 cujos links oficiais estão
quebrados e determinar quando uma linha representa a mesma vaga em nova versão,
uma vaga reapresentada ou uma vaga nova.

Pesquise páginas do Ministério da Saúde, Diário Oficial, dados.gov.br,
repositórios oficiais e cópias arquivadas verificáveis. Uma cópia arquivada só é
aceitável se o domínio/URL original, a data arquivada e o hash forem registrados.

## Campos necessários

- ciclo, edital, chamada, publicação, retificação e data de vigência;
- identificador administrativo da vaga, se existir;
- ente solicitante, IBGE, município, CNES e estabelecimento;
- curso/especialidade e tipo de prática;
- vaga imediata ou cadastro de reserva e quantidade;
- faixa, valor anunciado e categoria territorial;
- motivo de inclusão, alteração, retirada, cancelamento ou reapresentação;
- chave explícita que ligue versões, quando publicada.

Não invente `id_vaga`. Se precisar de uma chave técnica para auditar versões,
rotule-a `chave_candidata`, publique sua fórmula e liste colisões.

## Entregáveis exclusivos

- brutos em `data/raw/aquisicao/vagas/`;
- script idempotente em `scripts/aquisicao/a01_adquirir_vagas.py`;
- `output/aquisicao/a01_manifesto_vagas.json`;
- `output/aquisicao/a01_inventario_versoes.json`, com relação entre documentos;
- `docs/auditorias/aquisicao/A01_vagas_e_versionamento.md`.

O relatório deve conter uma tabela por ciclo/chamada com denominador de vagas,
versões encontradas, datas, campos, duplicidades potenciais e lacunas. Registre
se os arquivos quebrados de 2025 foram recuperados byte a byte, apenas
reconstruídos por outra publicação oficial ou permaneceram indisponíveis.

## Critério de aceite

A frente só está completa se for possível explicar, sem somar publicações
indevidamente, quais versões existem e se há ou não um denominador confiável de
vagas. Não construa o painel analítico final e não estime preenchimento.

Não altere documentação compartilhada, `run_all.py` ou arquivos de outro agente.
Valide, faça commit próprio e informe hash e bloqueios; não faça push ou merge.

