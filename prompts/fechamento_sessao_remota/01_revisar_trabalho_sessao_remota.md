# 01. Revisar o trabalho da sessão remota de 01/10/2026

## Papel

Você é revisor independente. Uma sessão remota produziu cinco commits por meio
de quatro subagentes, e eles estão integrados no branch
`claude/admiring-tesla-bduu1t`. Sua tarefa é decidir se cada um pode ir para a
`main` como está, com ajuste ou não pode. Revise **contra o próprio
repositório**, nunca contra o relato dos agentes: o relato é afirmação a
verificar, não evidência.

## Antes de começar

1. Leia [`CLAUDE.md`](../../CLAUDE.md), [`AGENTS.md`](../../AGENTS.md), [`TODO.md`](../../TODO.md), as seções "Encerramento" e
   "Revisão da PR 3 depois do merge" de
   [`docs/06_execucao/36_backlog_pos_auditoria.md`](../../docs/06_execucao/36_backlog_pos_auditoria.md), e o
   [`README.md`](README.md) desta pasta.
2. Rode `git fetch origin claude/admiring-tesla-bduu1t`, depois
   `git checkout claude/admiring-tesla-bduu1t`, e veja o diff da rodada com
   `git diff 127e3be..355e868`.
3. Monte o ambiente em um `.venv` com Python >= 3.12 e as versões fixadas em
   `requirements.txt`. Sob 3.11 o pip falha, e outras versões reescrevem
   artefatos (ver [`scripts/utils/ambiente.py`](../../scripts/utils/ambiente.py)). Rode
   `python run_tests.py`: o esperado são 189 testes verdes.

## O que revisar, commit a commit

### `e40c6b1` — auditoria documental

- Confira cada contagem nova contra a fonte:
  - 188/189 testes, contra a suíte;
  - 214 e 199 cifras, contra os CSVs dos conferidores em `output/`;
  - 101 decimais no artigo curto;
  - +27,9 p.p. em A4, contra a tabela de A4.
- Confira se os três links corrigidos em `docs/00_registro_mudancas.md` apontam
  para o arquivo certo.
- Confira se o bloco A-1b/C-7b/C-7c no `TODO.md` e no `README.md` reproduz o
  backlog 36 sem endurecer nem amolecer a leitura. Em especial: o
  deslocamento dentro da região deve aparecer como **não testado**, não como
  refutado.

### `1951d70` — decks da banca 1

- O documento manda: [`docs/07_apresentacoes/banca1/02_conteudo_slides.md`](../../docs/07_apresentacoes/banca1/02_conteudo_slides.md).
  Confira cada mudança nos decks contra ele e procure divergência que tenha
  ficado para trás.
- Confirme que `02_conteudo_slides.md` e `01_roteiro_narrativo.md` **não**
  mudaram.
- Confirme que nenhum resultado de estimação entrou na banca 1.
- O PDF do Slidev foi reexportado. Confira se tem 40 páginas e se as páginas
  alteradas não vazam do quadro.

### `6fd3a82` — reprodutibilidade

- Leia a subseção de 01/10/2026 do doc 33 e reproduza pelo menos dois pontos:
  - o aborto do `run_all.py` na etapa 8;
  - a diferença de `A5_tabela_13` nos cursos 3 e 13, rodando
    `scripts/tema_trabalho/06b_*` sob o ambiente fixado.
- Confira se a classificação "idêntico / só metadado / numérico" está correta.
- **Cuidado:** o `run_all.py` reescreve o doc 33 e outros documentos de
  `docs/`. Reverta tudo o que ele tocar (`git checkout -- docs/ output/`)
  antes de qualquer commit.

### `b57eb4e` e `e5a1872` — diagnóstico dos cursos 2 e 16

Este é o ponto mais sensível. Verifique:

1. **Ordem dos commits.** O protocolo veio antes do código? Compare as datas e
   o conteúdo de `b57eb4e` com o que `e5a1872` executa.
2. **O que o protocolo fixou.** A execução seguiu o protocolo, ou mudou a regra
   de leitura depois de ver os dados? A tolerância de conferência dos cursos 3
   e 13 foi ajustada durante a execução, e isso está declarado: julgue se o
   ajuste é legítimo.
3. **Nada causal mudou.** Amostra, outcome, especificação primária e regra de
   exclusão de A5 ficaram intactos? Nenhum artefato de A5/A6 foi regravado
   (`git diff 127e3be..355e868 --stat -- output/`)?
4. **Script.** É determinístico, roda duas vezes com os mesmos bytes e tem
   manifesto com SHA-256 das entradas? Use `verificar_ambiente(estrito=True)`
   e rode você mesmo.
5. **Linguagem.** "Compatível com oferta" é leitura descritiva. A compensação
   pelo resto do município (−0,84 e −0,79) está registrada sem promover
   transferência nem reatribuição cadastral? A fragilidade do curso 2 (sinal
   bruto contrário ao ajustado na janela D2) está dita?
6. **Teste novo.** Testa o que importa, ou só que o arquivo existe?
7. **D-4.** Confira que o hash de
   `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet` é o que
   A5 registra (`285db221…`).

## O que entregar

Um relatório com uma linha por commit:

| Commit | Veredito | Achados | Correção proposta |
|---|---|---|---|

O veredito é um de três: `APROVADO`, `APROVADO COM AJUSTE` ou `BLOQUEADO`.

Para cada achado, informe:
- arquivo e linha;
- o que está errado;
- como verificou;
- a gravidade: muda número publicado, muda artefato ou é só texto.

Correções:
- Se a correção for mecânica e sem decisão do autor (link, contagem, erro de
  digitação), faça em commit próprio, com mensagem em português.
- Se mudar número, protocolo ou leitura, **não corrija**: reporte.

Ao terminar:
- Suíte verde e os dois conferidores aprovando (`10_` e `11_`) são portão.
- Não faça push nem merge sem autorização explícita do autor.
