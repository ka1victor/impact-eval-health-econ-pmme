# C3-06 — Atualização prospectiva com doze meses

## Condição de execução

Execute somente quando toda a coorte congelada tiver doze competências comuns
e maduras após `T0`. A análise de seis meses deve estar incorporada e auditada.

## Objetivo

Atualizar o mesmo estudo, sem redesenho, para medir durabilidade do estoque e o
número de entrantes pós-oferta ainda presentes no décimo segundo mês.

## Trabalho

1. Confirme maturidade e integridade antes de abrir resultados por braço.
2. Acrescente competências com os mesmos scripts, filtros, SIGTAP e manifestos.
3. Reexecute o protocolo congelado, agora com horizonte de doze meses.
4. Reporte lado a lado seis e doze meses; não substitua o primeiro resultado.
5. Meça primeiro o estoque de anestesiologistas, entradas, saídas, churn e
   entrantes ainda presentes; mantenha oncologia clínica e medicina intensiva
   como generalização separada e não use taxa condicionada aos entrantes como
   outcome causal principal.
6. Se a assinatura da Nota 59 estiver validada, atualize também o número de
   participantes PMM-E ainda registrados, saídas e reposições; mantenha o
   estimando ITT por célula ofertada.
7. Atualize produção assistencial somente para o módulo aprovado.
8. Avalie remanejamento em CNES, município e região de saúde.
9. Faça auditoria independente, wild cluster bootstrap e as mesmas robustezes,
   sem criar novos filtros para alterar conclusões.
10. Separe claramente ausência de durabilidade, efeito nulo e imprecisão.

## Entregáveis mínimos

- atualização determinística dos painéis e manifestos;
- tabelas e figuras comparáveis à versão de seis meses;
- `docs/15_resultados_ciclo3_doze_meses.md`;
- síntese explícita sobre atração, permanência e produção;
- tabela final de desvios do protocolo.

Valide referências, JSON, testes, `git diff --check` e integridade dos brutos.
Crie commit próprio e não faça push.
