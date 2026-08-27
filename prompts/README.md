# Prompts operacionais dos agentes

Esta pasta contém as tarefas executáveis do roadmap definido em [`docs/05_roadmap_execucao.md`](../docs/05_roadmap_execucao.md).

## Ordem

| Ordem | Prompt | Dependência | Pode rodar em paralelo? |
|---:|---|---|---|
| 1 | `01_auditoria_institucional.md` | Nenhuma | Com 02, em worktree isolado |
| 2 | `02_auditoria_dados.md` | Nenhuma | Com 01, em worktree isolado |
| 3 | `03_protocolo_empirico.md` | 01 e 02 incorporados | Não |
| 4 | `04_painel_vagas_cobertura.md` | Protocolo autoriza | Com 05, após chaves definidas |
| 5 | `05_cnes_fte_infraestrutura.md` | Protocolo e chaves | Com 04, em worktree isolado |
| 6 | `06_estimacao_causal.md` | 04 e 05 validados | Não |
| 7 | `07_red_team.md` | Estimações concluídas | Não |
| 8 | `08_sintese_final.md` | Red team resolvido | Não |

## Uso

1. Entregue um prompt inteiro ao agente.
2. O agente deve partir do commit que contém todos os pré-requisitos anteriores.
3. Cada agente cria commit próprio e não faz push ou merge.
4. Revise e incorpore o commit antes de iniciar uma tarefa dependente.
5. Se um portão falhar, pare a sequência; não pule para a estimação.

WP3, WP4 e WP5 não têm prompts de execução porque estão guardados. Seu backlog está em [`docs/06_backlog_wp3_wp4_wp5.md`](../docs/06_backlog_wp3_wp4_wp5.md).
