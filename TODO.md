# Próximas etapas

> **Estado em 18/11/2026.** O resultado apresentado na banca final é o logit condicional da escolha da 1ª opção com
> vagas da mesma UF (VL-1): ×1,47 por +R$ 5 mil nos ciclos 1–3, exploratório (docs `06_execucao/57x` e `66`). A RDD
> da bolsa é inconclusiva (docs `44` e `57`); o A8 segue como núcleo causal dos dois artigos; A4 e A5 são
> associativos; o ciclo 3 continua congelado até maturidade. Resumo no [`README.md`](README.md).<br>
> **Antes (19/10/2026):** núcleo causal A8; RDD da bolsa reaberta em 14/10/2026 com o IVS 2010 oficial
> (`docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md`), regra sharp,
> E3 inconclusivo (`docs/06_execucao/37_resultados_rdd_bolsa_ivs_oficial.md`); pedido administrativo cancelado sem
> envio, porque o escore é público. Decisão canônica em
> `docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md`; portões em
> `docs/06_execucao/33_status_execucao_plano_causal.md`.

> **Itens concluídos** (filas do ciclo 1, A8, correções pós-auditoria, artigos, decisões, portões, construção dos
> dados, análise e entrega) estão em
> [`docs/90_arquivo_historico/TODO_concluido_ate_18nov2026.md`](docs/90_arquivo_historico/TODO_concluido_ate_18nov2026.md).
> Aqui ficam só as seções com algo em aberto.

## Banca final (estado em 18/11/2026)

Detalhe em [`docs/07_apresentacoes/banca_final/`](docs/07_apresentacoes/banca_final/README.md).

- [x] Deck do grupo sobre a versão do Bernardo, com a rodada 13 e as correções de 15/11
  (`output/apresentacao_banca_final/deck_banca_final_bernardo_r13.pptx`, 40 slides).
- [x] Roteiro de fala em Markdown (doc 05) e em Word (`roteiro_fala_banca_final.docx`).
- [x] Perguntas prováveis sobre o logit condicional (doc 04).
- [ ] **Grupo:** ensaiar com cronômetro; o roteiro estima ≈ 13 min 30 s, e o doc 05 diz o que encurtar.
- [ ] **Grupo:** os anexos do deck do Bernardo ficam sem navbar, por escolha dele; decidir se fica assim.

## Fila imediata — RDD da bolsa (estado em 19/10/2026)

Detalhe em `docs/06_execucao/38_estado_e_pendencias_rdd_bolsa.md`.

- [x] **R1 com o IVS 2010 oficial:** `APROVADO_SHARP` (368/368 no ciclo 1;
  454/454 no ciclo 2).
- [x] **E3 sob protocolo congelado:** inconclusivo.
- [x] **E5 exploratório:** não muda a leitura.
- [x] **Sinal do salto conferido.**
- [x] **Relatório em PDF com os gráficos de RDD.**
- [x] **Pipeline:** cadeia no `run_all.py`, com `--rdd-bolsa`.
- [x] **Testes da cadeia.**
- [x] **Artigos e A6 atualizados.**
- [x] **Protocolo multi-outcome congelado** (`docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`)
  e políticas nos mesmos cortes (`docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md`).
- [x] **D2:** preenchimento do ciclo 2, no E6 (`docs/06_execucao/41_resultados_E6_funil.md`).
- [x] **D3(b):** reestimação com a base oficial e failure mode
  (`docs/auditorias/19_reestimacao_base_oficial_failure_mode.md`).
- [x] **E6, E9 e E7:** funil, escolha e DiRD no CNES (docs 41, 42 e 43).
- [x] **E8:** síntese com o Holm das primárias e proposta de revisão da
  hipótese (`docs/06_execucao/44_sintese_rdd_bolsa_multioutcome.md`).
- [x] **Rodada exploratória X1–X6** (docs 45 e 46), auditada, antes da decisão.
- [ ] **Decisão do autor sobre a revisão da hipótese** (doc 44, §7): manter H1
  e relatar o nulo, ou adotar uma das propostas, com registro datado.
- [x] **Rascunho do conteúdo canônico da apresentação de 28/10/2026** em
  `docs/07_apresentacoes/banca2/` (21 slides e apêndice; números conferidos
  por `tests/test_conteudo_banca2.py`).
- [ ] **Mensagem principal da banca 2** (depende da decisão acima) e, depois,
  o deck derivado.
- [x] **Relatório PDF (parte II), artigos e pipeline** atualizados em 19/10/2026.
- [ ] **Artigos:** levar a síntese do doc 44 aos `.tex` (tarefa posterior).
- [ ] **Ambiente:** instalar `scipy`, `statsmodels` e `matplotlib`, que estão no
  `requirements.txt`, para os três testes antigos que dependem deles.

## Fila pós-auditoria — 23 itens em `docs/06_execucao/36_backlog_pos_auditoria.md`

Agrupados por consequência, com alvo numérico medido antes de qualquer alteração.
A ordem de execução do backlog é **normativa**, com estado por sessão e protocolo
de início e encerramento.

> **Fila exaurida em 16/09/2026, no que este ambiente permite.** O autor delegou
> à sessão as seis decisões pendentes, com a instrução de decidir e documentar.
>
> **D-4 parcialmente destravado** (`da4d6f7`): A5 passa a reestimar a partir de
> `A5_painel_T0.parquet`, com o hash conferido contra o A6, e o modo foi validado
> byte a byte antes de qualquer mudança de conteúdo. Isso destravou as sessões 1,
> 3 e 4. O painel mensal e os microdados do CNES continuam ausentes.
>
> **Sessão 1 concluída** (A-1; emenda 2 do `35` em `03ccc1c`, execução em
> `62bb4ed`): efeito fixo de UF colapsado em macrorregião com residual rotulado,
> 24 níveis, a mesma definição do C1; os três alvos reemitidos reproduzem
> (`RESTO` +1,2949; macrorregião **+0,5062**; sem colapso +0,5002) e
> `A5_tabela_11` publica as três variantes. **Sessão 4 concluída** (`3a89233`):
> censura de `presentes_6m` gravada como NaN, relatório de A5 promovido, FDR
> declarado — o nível **não** sobrevive à família de 25 (`q = 0,364`), o
> proporcional sobrevive (`q = 0,0034`) —, rótulo de `03f` corrigido, E-3 e E-4
> em errata, C-9 declarado. **Sessão 3 concluída** (protocolo `1fab57d`, execução
> `fcb94b4`): placebo nulo, pré-tendência rejeita nos cursos 2 e 16, sem sinal de
> deslocamento nos vizinhos do quadro e oferta região–curso positiva.
>
> **Decisões delegadas** (`648f21e`): B-4 e B-7 em errata (E-5, E-6); C-4
> permanece com registro no código; **A8 regravado** sob o ambiente documentado
> (só o 15º dígito dos IC, o PNG e os caminhos POSIX mudaram); D-2 verificado e
> FTP inacessível deste ambiente; **D-3 não enviado**, por ser ato externo fora da
> delegação. Revisão de provas dos dois PDFs feita nesta sessão (D-1).
>
> **Próxima sessão: nenhuma.** O que resta depende de dado externo (`202703`,
> `RDAC2606`/`RDRR2606`, microdados do CNES) ou do autor (envio do pedido D-3).
>
> **Integrado na `main` em 19/09/2026** (PR #3), com autorização do autor.
> Encerramento, decisões que continuam com o autor e sugestões ordenadas em
> `docs/06_execucao/36_backlog_pos_auditoria.md`, seção "Encerramento".

- [x] Grupo A — muda número publicado (3 itens): A-1 concluído em 16/09/2026 sob a
  emenda 2; A-2 e A-3 concluídos em 14/09/2026 sob a emenda 1.
- [x] Grupo B — muda artefato, não muda número publicado (7 itens): B-1, B-2, B-5 e
  o rótulo de B-6 corrigidos em 16/09/2026; B-3 em 14/09/2026; B-4, B-7 e os dois
  itens congelados de B-6 em errata (E-3 a E-6).
- [x] Grupo C — documentação e linguagem (9 itens): C-7 concluído em 16/09/2026
  com as três ameaças testadas sob protocolo congelado; C-9 declarado; C-4
  permanece com registro no código e correção vinculada à primeira reexecução
  legítima de A1→A3; os demais concluídos em 14/09/2026.
- [ ] Grupo D — bloqueado por dado externo ou pelo autor: D-2 (`RDAC2606`,
  `RDRR2606`, `202703`, `T0+12m`); D-3 (envio do pedido, decisão do autor; pacote
  pronto); D-4 (painel mensal e microdados do CNES). D-1 resolvido.

## O que continua com o autor (19/09/2026)

- [x] **D-3** — pedido do escore administrativo de IVS: cancelado sem envio, porque o escore é público
  (IVS 2010 oficial do Ipea, igual ao do MS em 404/404).
- [ ] **D-2** — repetir C3-02B de um ambiente com acesso ao FTP do DATASUS;
  C3-05 só com `202703` madura; C3-06 em setembro/2027.
- [ ] **D-4** — painel mensal e microdados do CNES; ao reexecutar A5, retirar a
  coluna `uf_fe` do painel congelado.
- [ ] **C-4 + E-3** — corrigir juntos na primeira reexecução legítima de A1→A3.
- [ ] Diagnóstico dos cursos 2 e 16 na pré-tendência, sem reescolher amostra.

## Atualização prospectiva e infraestrutura paralela

- [ ] Acrescentar novas competências sem redefinir a janela da primeira versão.
- [ ] Estimar presença doze meses depois somente quando toda a coorte congelada
  possuir seguimento comum maduro, com extensão do CNES até 2027-01 para a
  coorte de entradas encerrada em 2026-01.
- [x] Construir módulo utilitário DBC -> Parquet do DATASUS, começando por um
  benchmark SIH e medindo separadamente tráfego, pico temporário e espaço
  persistente (`scripts/utils/datasus_dbc.py`).

## Ciclo 3 prospectivo

- [x] C3-01 — congelar coorte, exposição e ponte; correção independente fixou
  como núcleo integral somente os cursos 1, 12 e 24
  (`output/avaliacao_ciclo3/coorte_c3_congelada.parquet`,
  `docs/auditorias/05_coorte_c3_e_exposicao.md`).
- [x] C3-02 — executar piloto técnico SIH pré-tratamento para anestesiologia;
  viabilidade confirmada, mas painel ainda não liberado como insumo causal
  (`docs/auditorias/06_piloto_sih_anestesiologia.md`).
- [ ] C3-02B — tentativa de 31/08/2026 persistiu 675 manifestos e historicizou
  25 SIGTAP, mas ficou bloqueada em 673 sucessos: `RDAC2606.dbc` e
  `RDRR2606.dbc` não estavam no FTP oficial. Repetir só após ambos aparecerem;
  não imputar zeros (`prompts/avaliacao_ciclo3/02b_corrigir_e_validar_sih_pre.md`).
- [x] C3-03 — separar portões e executar o torneio de força de trabalho com 26
  competências CNES estritamente pré-T0. Protocolo congelado; anestesiologia
  classificada como `associacao_ajustada` (MDE 2,22 no CNES e 4,44 no
  município). Nenhum efeito foi estimado.
- [x] C3-04 — não acionar: SIA/ecocardiografia não venceu a rubrica nem
  substitui automaticamente o SIH incompleto.
- [ ] C3-05 — estimar a versão de seis meses apenas com seguimento comum maduro
  (aguardando competência CNES `202703` publicada e validada).
- [ ] C3-06 — atualizar a mesma análise aos doze meses, sem redesenho (aguardando T0+12m em setembro/2027).

## Congelado

Não executar agora: efeitos do ciclo 3 antes da maturidade; efeito da dose
recebida sem folha; fila, outcomes clínicos e custos; identificação individual
sem ponte; envio de A07. A RDD do IVS público não deve ser restaurada em
`0,300`, `0,400` ou `0,500` sem recuperar a regra administrativa. Heterogeneidades
do A8 por remoticidade, IVS, curso ou região são exploratórias e não podem virar
conclusão com 36 pares. Não inferir curva de sobrevivência a partir do snapshot,
pois isso seleciona sobreviventes. Synthetic DiD pode ser robustez
pré-especificada, nunca reparo retrospectivo de pré-tendências.
