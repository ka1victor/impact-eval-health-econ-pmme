# Fechamento da sessão remota de 01/10/2026

> **O que é:** a fila de seguimento da rodada remota de 01/10/2026, executada por
> quatro subagentes em worktrees isolados e integrada no branch
> `claude/admiring-tesla-bduu1t`.<br>
> **Base:** o branch `claude/admiring-tesla-bduu1t`, a partir do merge `355e868`.<br>
> **Não autoriza:** reabrir A1–A8, reestimar fora dos portões, enviar pedido
> administrativo nem descongelar o ciclo 3. As regras do [`CLAUDE.md`](../../CLAUDE.md) valem
> sobre tudo o que está aqui.

## Ordem

| Ordem | Prompt | O que faz | Depende de |
|---:|---|---|---|
| 1 | [`01_revisar_trabalho_sessao_remota.md`](01_revisar_trabalho_sessao_remota.md) | Revisão adversarial dos cinco commits da rodada antes de a `main` recebê-los | — |
| 2 | [`02_resolver_pendencias.md`](02_resolver_pendencias.md) | Decisões do autor, pendências executáveis e passos condicionados a dado externo | 1 sem achado bloqueante |

O prompt 1 pode ser entregue sozinho, como contexto para um agente revisar a
rodada. O prompt 2 pressupõe a revisão feita, mas cada seção dele é
independente e pode ir para um agente separado.

## O que a rodada produziu

| Commit | Tema | Arquivos principais |
|---|---|---|
| `e40c6b1` | Auditoria documental | `README.md`, `TODO.md`, `tests/README.md`, `docs/00_registro_mudancas.md` |
| `1951d70` | Decks da banca 1 alinhados ao documento de conteúdo | `docs/07_apresentacoes/banca1/deck_slidev/`, `deck_beamer/banca1_beamer.tex`, READMEs, `output/apresentacao_banca1/deck_slidev/banca1_slidev.pdf` |
| `6fd3a82` | Reprodutibilidade do `run_all.py` sob o ambiente fixado | `docs/06_execucao/33_status_execucao_plano_causal.md`, subseção de 01/10/2026 |
| `b57eb4e` | Protocolo do diagnóstico dos cursos 2 e 16, commitado antes do código | `docs/06_execucao/36_backlog_pos_auditoria.md` |
| `e5a1872` | Execução do diagnóstico | `scripts/tema_trabalho/06c_diagnostico_cadastral_cursos_pretendencia.py`, `output/tema_trabalho/A5_tabela_16_*`, `A5_tabela_17_*`, `A5_diagnostico_cadastral_cursos_2_16.json`, `tests/test_provimento_cnes_a5.py` |

Os quatro branches foram integrados por merge `--no-ff` (`7532aae`, `97315bc`,
`61a3d6f`, `355e868`), sem conflito. A suíte passou depois da integração, com
189 testes sob Python 3.12.3, numpy 2.5.2 e pandas 3.0.5.

## Achados da rodada que ainda não viraram ação

1. **O `run_all.py` não roda ponta a ponta sem os microdados do CNES.** Ele
   aborta na etapa 8 de 25. As etapas 10 a 25 reproduzem byte a byte, exceto
   A5/A6 (ver item 2).
2. **A5/A6 foram gravados sob Python 3.11.15 e numpy 2.4.6.** No ambiente fixado,
   `A5_tabela_13` difere no F dos cursos 3 e 13 a partir da 4ª casa.
   Nenhuma rejeição a 5% muda e nenhuma cifra dos artigos muda.
3. **O `run_all.py` sobrescreve documentação curada.**
   `02_controlar_execucao_plano_causal.py` reescreve o doc 33 a partir de um
   modelo de 04/09.
4. **Hash vencido.** `quadro_vagas_tratamento.parquet` aparece com hash
   vencido em dois JSON de `output/rdd_bolsa/`.
5. **D-4 é mais estreito do que está registrado.** O painel mensal existe em
   `output/avaliacao_impacto/dados/`; o que falta é só o microdado.
6. **Estados divergentes.** D-3 e a RDD-IVS aparecem com estados diferentes no
   JSON de status, no doc 33, no backlog 36 e no `TODO.md`.
7. **`CLAUDE.md` e `AGENTS.md` desatualizados.** Ainda dão a RDD da bolsa como
   fila imediata.
8. **Hook `SessionStart` do `.venv` não criado.** Foi bloqueado pelo sistema de
   permissões da sessão remota.
