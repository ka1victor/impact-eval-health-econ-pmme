# Integração das rodadas de outubro de 2026

> **O que é:** a ordem das próximas sessões para levar à `main` duas rodadas
> que partiram do mesmo commit (`127e3be`) e ainda não se encontraram.<br>
> **Não autoriza:** push ou merge na `main` sem o autor; abrir outcome do RDD
> antes do R3 commitado; reabrir A1–A8; enviar pedido administrativo;
> descongelar o ciclo 3. As regras do [`CLAUDE.md`](../../CLAUDE.md) valem sobre
> tudo o que está aqui.

## As duas rodadas

| Rodada | Branch | Commits | O que trouxe |
|---|---|---|---|
| Sessão remota de 01/10/2026 | `claude/admiring-tesla-bduu1t` | `e40c6b1`, `b57eb4e`, `6fd3a82`, `1951d70`, `e5a1872`, merges até `355e868`, prompts em `2487099` | auditoria documental, decks da banca, verificação de reprodutibilidade, diagnóstico dos cursos 2 e 16, prompts em `prompts/fechamento_sessao_remota/` |
| RDD da bolsa de 05/10/2026 | `claude/compassionate-feynman-d70ipe` | `1faf0f4`, `be12956` e o commit destes planos | R1 sharp e R2 com o IVS administrativo; fila do RDD reescrita; estes prompts |

**Por que importa a ordem:** os prompts de 01/10 foram escritos antes do R1 de
05/10. A seção A do `02_resolver_pendencias.md` daquela rodada propõe declarar
a RDD "arquivada porque o escore administrativo não é observado", e o escore é
observado. O adendo [`03_adendo_pendencias_fechamento.md`](03_adendo_pendencias_fechamento.md)
corrige isso e precisa ser lido junto com aquele prompt.

## Ordem das sessões

| Sessão | Prompt | O que faz | Depende de |
|---|---|---|---|
| S1a | `prompts/fechamento_sessao_remota/01_revisar_trabalho_sessao_remota.md`, no branch de 01/10 | revisão da rodada remota, como está escrita | — |
| S1b | [`01_revisar_rdd_ivs_administrativo.md`](01_revisar_rdd_ivs_administrativo.md) | revisão adversarial do R1 e do R2 de 05/10 | — |
| S2 | [`02_integrar_branches.md`](02_integrar_branches.md) | junta os dois branches, resolve os dois conflitos e alinha os estados | S1a e S1b sem `BLOQUEADO` |
| S3 | `prompts/fechamento_sessao_remota/02_resolver_pendencias.md` **com** [`03_adendo_pendencias_fechamento.md`](03_adendo_pendencias_fechamento.md) | decisões e pendências da rodada remota | S2 |
| S4 | [`../avaliacao_rdd_bolsa/02_congelar_protocolo_r3.md`](../avaliacao_rdd_bolsa/02_congelar_protocolo_r3.md) | decisões do autor e congelamento do R3 | S2 |
| S5 | [`../avaliacao_rdd_bolsa/03_estimar_r4_atracao.md`](../avaliacao_rdd_bolsa/03_estimar_r4_atracao.md) | estimação do R4 | S4 commitado |

- S1a e S1b podem correr em paralelo, cada uma em worktree isolado.
- S3 e S4 também podem, em worktrees isolados. O registro de mudanças e o
  roadmap vão conflitar; resolva mantendo as entradas por data.
- Sem resposta do autor, S3 (seção A) e S4 (passo 1) param e registram as
  perguntas; não há decisão por padrão.

## Decisões do autor que destravam cada sessão

| Sessão | Decisão |
|---|---|
| S2 | integrar só num branch de integração ou também na `main` |
| S3 | as sete decisões da seção A, com as respostas corrigidas do adendo |
| S4 | as treze decisões do rascunho 18, a começar pela troca da running variable |
| S5 | nenhuma nova: só executa o registro |

## O que mudou desde 01/10, em uma linha cada

- A RDD do IVS foi **reaberta**, não arquivada: R1 sharp com o IVS
  administrativo, R2 viável, R3 aguardando o autor.
- O D-3 continua não enviado e deixou de ser pré-condição do R1.
- O doc 33 é gerado pelo controlador; o registro curado de 01/10 que está nele
  precisa mudar de arquivo na integração.
- O `run_all.py` tem 27 etapas e continua abortando na etapa 8 sem os
  microdados do CNES.
- O ambiente fixado funciona no container da nuvem com `python3.12` e `uv`; o
  R1 e o R2 reproduzem byte a byte nele.
