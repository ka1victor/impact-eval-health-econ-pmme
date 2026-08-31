# Prompts operacionais dos agentes

> **Fila histórica congelada.** Estes prompts pertencem ao desenho individual
> anterior e não devem ser usados para executar a primeira versão. A sequência
> autorizada é o plano público agregado em
> [`docs/05_roadmap_execucao.md`](../docs/05_roadmap_execucao.md): relevância de
> imediata versus reserva, ponte curso–CBO, painel municipal, estoque, fluxos,
> presença posterior, DDD e diagnósticos.
>
Esta pasta preserva as tarefas do roadmap anterior. A ordem abaixo é histórica e
não constitui uma fila autorizada.

## Ordem

| Ordem | Prompt | Dependência | Pode rodar em paralelo? |
|---:|---|---|---|
| 1 | `01_auditoria_institucional.md` | Nenhuma | Com 02, em worktree isolado |
| 2 | `02_auditoria_dados.md` | Nenhuma | Com 01, em worktree isolado |
| 2A | [`aquisicao_dados/A01–A05`](aquisicao_dados/README.md) | 01 e 02; portão indicou `aguardando dados` | Sim, em cinco worktrees isolados |
| 2B | `aquisicao_dados/A05R_saneamento_pre_a06.md` | A01–A05 incorporados e revisão pré-A06 | Não |
| 2C | `aquisicao_dados/A06_integracao_e_portao.md` | A05R declarou entradas aptas | Não |
| 2D | `aquisicao_dados/A07_pedidos_administrativos.md` | A06; somente se restarem lacunas | Não |
| 3 | `03_protocolo_empirico.md` | A06 liberou o protocolo ou pedidos de A07 foram atendidos e integrados | Não |
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

As auditorias 01 e 02 concluíram que o estudo está `aguardando dados`. Portanto,
o sprint extraordinário em [`aquisicao_dados/`](aquisicao_dados/README.md) é agora
obrigatório antes do prompt 03. A01–A05 dividem aquisições públicas sem
sobreposição; A05R saneia e valida; A06 integra; A07 prepara, mas não envia,
pedidos administrativos.

O A06 foi concluído com a decisão **`aguardar dados administrativos`**. O A07
preparou os pacotes limitados às seis lacunas fechadas no portão, todos com
status `não enviado`. A submissão depende de decisão externa do autor. O prompt
03 não está liberado e não deve ser executado até que eventuais respostas
administrativas sejam incorporadas e reavaliadas em novo portão.

Esse bloqueio continua válido para o desenho individual anterior. Ele não
impede o plano agregado vigente, que não identifica bolsistas nem usa os pedidos
administrativos. Nenhum prompt desta fila deve ser reinterpretado para pular os
portões definidos no roadmap atual.

O plano agregado foi executado em 30/08/2026 e terminou como **comparação
ajustada**: imediata versus reserva não apresentou primeiro estágio na amostra
município–curso da DDD. Essa execução não libera o prompt 03, não transforma
os pedidos A07 em enviados e não autoriza escolher um novo estimador depois do
resultado. Veja
[`docs/auditorias/04_auditoria_pipeline_agregado.md`](../docs/auditorias/04_auditoria_pipeline_agregado.md).

WP3, WP4 e WP5 não têm prompts de execução no pipeline principal porque estão guardados (ver [`docs/06_backlog_wp3_wp4_wp5.md`](../docs/06_backlog_wp3_wp4_wp5.md)). No entanto, o módulo de engenharia de dados preparatório está documentado em [`infraestrutura_datasus_dbc.md`](infraestrutura_datasus_dbc.md) (100% paralelizável, com foco em ingestão leve e eficiente em disco).

## Nova fila prospectiva

O resultado do ciclo 1 permanece fechado como comparação ajustada. A avaliação
prospectiva separada do ciclo 3 deve seguir
[`avaliacao_ciclo3/README.md`](avaliacao_ciclo3/README.md): a coorte foi
congelada e o SIH pilotado; agora é obrigatório corrigir o piloto pelo C3-02B
antes de congelar o protocolo no C3-03.
Os efeitos de seis e doze meses não podem ser estimados antes da maturidade
comum. Essa fila não libera o prompt 03 do desenho individual nem envia A07.
