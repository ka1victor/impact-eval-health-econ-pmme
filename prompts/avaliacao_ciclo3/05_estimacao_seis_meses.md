# C3-05 — Estimação prospectiva com seis meses

## Condição de execução

Execute somente quando todas as unidades congeladas tiverem seis competências
pós-`T0` completas e publicadas em CNES e, para o módulo selecionado, SIH ou
SIA. Confirme a maturidade sem abrir resultados agregados por braço.

## Objetivo

Atualizar as bases até seis meses e executar exatamente o plano congelado em
`output/avaliacao_ciclo3/registro_pre_analise.json`.

## Regras

- não reescolha amostra, ponte, procedimento, horizonte, peso ou estimador;
- registre toda revisão inevitável antes de calcular efeitos, com justificativa,
  impacto e novo hash;
- mantenha imediata versus não priorizada como ITT;
- trate conversões e novas chamadas conforme a regra já congelada;
- não promova associação a causalidade se o portão prévio falhou.

## Trabalho

1. Verifique hashes, worktree e maturidade comum.
2. Adquira somente as seis competências necessárias, com o mesmo pipeline e
   validações do pré-período.
3. Rode testes de cobertura e esquema antes de unir tratamento e outcome.
4. Estime DDD/event study do núcleo geral e o módulo assistencial autorizado.
5. Reporte wild cluster bootstrap, intervalos, MDE e testes de equivalência.
6. Rode apenas placebos e robustez pré-especificados: leads, data falsa prévia,
   negativos, pesos de sobreposição, leave-one-region-out e synthetic DiD.
7. Decomponha estoque, entradas, saídas e entrantes presentes no sexto mês.
8. Quando a assinatura da Nota 59 tiver passado o portão, reporte cobertura,
   entrada, saída e permanência dos participantes PMM-E identificados no CNES,
   sem divulgar identificadores e sem confundi-los com o estoque total.
9. Diferencie resultado em CNES, município e região.
10. Produza tabela de desvios do protocolo, inclusive “nenhum”.

## Entregáveis mínimos

- scripts versionados de atualização e estimação em `scripts/avaliacao_ciclo3/`;
- painel analítico e manifestos em `output/avaliacao_ciclo3/`;
- tabelas e figuras reproduzíveis;
- relatório `docs/14_resultados_ciclo3_seis_meses.md`;
- auditoria independente dos estimadores e do wild bootstrap;
- atualização do `run_all.py` somente depois de todos os testes.

Valide hashes, esquemas, links, sintaxe, testes, `git diff --check` e ausência de
mudança em brutos existentes. Crie commit próprio e não faça push.
