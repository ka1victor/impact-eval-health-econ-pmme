# Auditoria A3 — potência por estrato (documentação de pendências, sem correção dos artefatos)

> **Data da auditoria:** 02/09/2026
> **Artefatos auditados:** `output/tema_trabalho/potencia_atracao.json`, `output/tema_trabalho/registro_pre_analise_atracao.json`, `docs/06_execucao/31_secao_econometrica_A3.md`, `scripts/tema_trabalho/04_congelar_pre_analise.py`
> **Decisão:** A3 permanece **congelado** como publicado em `30463d9`. As pendências abaixo são documentadas mas **não corrigidas** neste commit, por instrução explícita de só documentar A3 e concentrar correções em A2. A4 permanece liberado sobre o registro congelado; emenda futura de A3 deve ser datada e com hashes atualizados.

## 1. Pendência crítica — denominador de clusters por estrato

- **Onde:** `scripts/tema_trabalho/04_congelar_pre_analise.py:88-104` (`g = n_municipios_populacao_A1`) e `output/tema_trabalho/potencia_atracao.json:24-59`
- **O que:** MDE por estrato usa `n_municipios_populacao_A1` (540 mun. da população A1 completa, Ch1+Ch2) como `g` (clusters), quando a população primária de potência é o **quadro Ch1** (`output/aquisicao/quadro_vagas_tratamento.parquet:1295` células em **368** municípios). O correto para cada estrato é o nº de municípios **do quadro Ch1** naquele estrato: `capital 18` (não 25), `metropolitano 75` (não 104), `interior_proximo 200` (não 235), `interior_remoto 75` (não 176). `suporte_estratos_territoriais.csv` já distingue `n_municipios_populacao_A1` de `n_celulas_quadro_ch1`, mas a potência misturou os dois.
- **Consequência numérica (ICC=0.05, `DEFF=1+(m-1)*ICC`):**
  - `capital 73/25 m2.92 deff1.096 mde30 15.7%` → correto `73/18 m4.06 deff1.153 mde30 16.1%`
  - `metropolitano 289/104 m2.78 deff1.089 mde30 7.9%` → correto `289/75 m3.85 deff1.142 mde30 8.1%`
  - `interior_proximo 787/235 m3.35 deff1.117 mde30 4.8%` → correto `787/200 m3.94 deff1.147 mde30 4.9%`
  - `interior_remoto 146/176 m0.83 deff0.991 mde30 10.6%` → correto `146/75 m1.95 deff1.047 mde30 10.9%`
  - Global `1295/368 deff1.126 mde30 3.8%` permanece correto. O `deff<1` para remoto (`0.991`) é fisicamente impossível (`m<1` indica mais clusters que observações, artefato do denominador errado) e deveria ser `max(1, deff)`.
- **Implicação:** MDE por estrato publicado está **otimista 3–5%** (subestima incerteza). Não altera conclusão global (bem potenciado para 10pp), mas capital/remoto já no limite ficam ligeiramente mais limitados. `registro_pre_analise_atracao.json:7` está correto (`368 municípios`); a inconsistência é entre registro (368) e potência por estrato (540).
- **Ação futura (não executada aqui):** recalcular `potencia_atracao.json` usando `quadro Ch1` por estrato, aplicar `deff=max(1,1+(m-1)*ICC)`, atualizar `registro_pre_analise_atracao.json:hashes_entradas` e `docs/06_execucao/31_secao_econometrica_A3.md:25-28` (hoje só lista 2 estratos).

## 2. Outras observações documentadas (não bloqueantes)

- **Hashes território ausentes em A3:** `registro_pre_analise_atracao.json:102-117` lista 5 entradas + 2 artefatos, mas omite os dois XLSX de território (`data/raw/aquisicao/territorio/REGIC...xlsx`, `Composicao_RMs...xlsx`) que fundamentam A2. A2 os registra em `manifesto_tipologia_territorial.json:43-48`; A3 deveria herdar para proveniência completa.
- **Seção econométrica truncada:** `docs/06_execucao/31_secao_econometrica_A3.md:25-28` resume só `remoto ≈10.6%, metropolitano ≈7.9%`, omitindo `capital` e `próximo`. O completo está em `potencia_atracao.json:por_estrato`.
- **Transformação população:** `registro:65` `log1p(populacao_2010)` vs menção `log(pop)` em comentários — padronizar em `log1p` (já correto no registro).
- **Testes não pegaram:** `tests/test_pre_analise_atracao.py:53-62` checa `mde<0.05` global mas não `deff>=1` nem `g` por estrato.

## 3. Registro de decisão

Nenhum artefato de A3 foi reescrito nesta auditoria. Esta nota congela o diagnóstico para emenda futura datada, sem reabrir estimações. Correções de A3 ficarão para ciclo de emenda posterior; o foco imediato é deixar A2 perfeito.
