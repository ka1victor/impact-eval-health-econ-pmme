# Próximas etapas

> Ordem operacional resumida. A especificação completa está em `docs/05_roadmap_execucao.md`, e cada tarefa tem um prompt em `prompts/`.

## Concluído

- [x] Remover artefatos sem sustentação nas bases observadas.
- [x] Preservar as três bases observadas e o histórico do Git.
- [x] Organizar outcomes e inventariar lacunas.
- [x] Definir eficácia operacional como primeiro estudo.
- [x] Definir cobertura sustentada como outcome primário pretendido.
- [x] Formalizar modos de falha e limites da conclusão.
- [x] Separar agenda ampla de roadmap executável.
- [x] Criar prompts ordenados para os agentes.
- [x] Guardar explicitamente WP3, WP4 e WP5.

## Fase 1 — viabilidade e aquisição de dados

- [x] Executar `prompts/01_auditoria_institucional.md` (`docs/auditorias/01_regra_institucional.md`).
- [x] Executar `prompts/02_auditoria_dados.md` (`docs/auditorias/02_disponibilidade_dados.md`).
- [x] Executar Sprint de Aquisição A01–A05 (vagas, trajetórias, IVS/regras, pagamentos e CNES mensal).
- [ ] Executar `prompts/aquisicao_dados/A06_integracao_e_portao.md`.
- [ ] Executar `prompts/aquisicao_dados/A07_pedidos_administrativos.md`.
- [ ] Executar `prompts/03_protocolo_empirico.md`, se liberado pelo portão A06.
- [ ] Registrar decisão do portão: prosseguir, parcial, aguardar dados ou parar.

## Fase 2 — construção e estimação

- [ ] Executar `prompts/04_painel_vagas_cobertura.md`, se autorizado.
- [ ] Executar `prompts/05_cnes_fte_infraestrutura.md`, se autorizado.
- [ ] Reconciliar chaves, perdas amostrais, cobertura e FTE.
- [ ] Executar `prompts/06_estimacao_causal.md`.
- [ ] Confirmar que `run_all.py` reproduz todas as etapas validadas.

## Fase 3 — auditoria e entrega

- [ ] Executar `prompts/07_red_team.md`.
- [ ] Resolver ameaças sérias ou reduzir a linguagem.
- [ ] Executar `prompts/08_sintese_final.md`.
- [ ] Validar reprodução ponta a ponta e documentação final.

## Fora da execução atual

- [ ] WP3 — acesso, fila e deslocamento: guardado.
- [ ] WP4 — desfechos clínicos: guardado.
- [ ] WP5 — custos e bem-estar: guardado.

Não marcar esses itens como pendências operacionais. As condições futuras de reabertura estão em `docs/06_backlog_wp3_wp4_wp5.md`.

## Critério para inserir uma etapa no pipeline

- [ ] Pré-requisitos anteriores incorporados.
- [ ] Base observada com proveniência e hash.
- [ ] Outcome, denominador, unidade e janela definidos.
- [ ] Contraste causal e hipótese identificadora documentados.
- [ ] Diagnósticos e incerteza reproduzíveis.
- [ ] Linguagem limitada ao que foi identificado.
