# Prompt 06 — Identificação e estimação causal

Execute somente depois que o protocolo estiver congelado e os painéis dos prompts 04 e 05 estiverem validados.

Leia `AGENTS.md`, `CLAUDE.md`, o roadmap, o protocolo, os relatórios de auditoria, o fluxo de exclusões e os diagnósticos de ligação.

## Missão

Implementar exatamente o desenho autorizado pelo protocolo. Não force RDD se a auditoria não o sustentar.

Ordem obrigatória:

1. verificar primeiro estágio do tratamento;
2. examinar densidade da running variable;
3. testar continuidade de covariáveis e composição das vagas;
4. reportar potência e efeito mínimo detectável;
5. estimar o efeito sobre cobertura sustentada;
6. decompor entrada, velocidade, permanência e rotatividade;
7. estimar FTE líquido;
8. descrever remanejamento;
9. estimar a única heterogeneidade confirmatória;
10. separar análises exploratórias.

## Requisitos

- IVS 2010 como running variable canônica, quando o desenho institucional justificar.
- Sementes fixas e resultados determinísticos.
- Bandwidth e especificações definidos pelo protocolo ou por regra reproduzível.
- Intervalos de confiança e efeitos em unidades substantivas.
- Nenhum resultado selecionado por p-valor.
- Estimativas imprecisas não podem ser chamadas de zero.
- A linguagem deve nomear o tratamento realmente identificado.
- Tabelas, figuras e resultados estruturados devem ser produzidos por scripts.
- `run_all.py` deve reproduzir o estado validado ponta a ponta.

## Limites

- Não inferir produção, fila, saúde ou bem-estar.
- Não criar novas heterogeneidades confirmatórias depois de observar resultados.
- Não promover análise exploratória à conclusão principal.
- Não fazer push ou merge.

Ao final, execute todas as validações, faça commit próprio e informe hash, especificação principal e quaisquer portões que falharam.
