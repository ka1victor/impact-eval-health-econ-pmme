# Auditoria independente do protocolo 60, parte A: equivalência no preenchimento (H1)

> **Data:** 26/10/2026.<br>
> **Objeto:** commits `f47624f` (protocolo) e `af8e21f` (execução):
> `scripts/rdd_bolsa/36_equivalencia_H1.py`, `output/rdd_bolsa/EQ_estimativas.csv`, `EQ_resumo.json`,
> `EQ_figuras/EQ_tost_ic90.png`, o [doc 57j](../06_execucao/57j_resultados_equivalencia_H1.md) e
> `tests/test_equivalencia_H1.py`, contra a parte A do
> [protocolo 60](../06_execucao/60_protocolo_equivalencia_e_oferta_local.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.**
> - Nenhum número mudou.
> - As 21 linhas de `EQ_estimativas.csv` foram recalculadas com código próprio a partir de
>   `NA_estimativas.csv` e `N_estimativas.csv`. Diferença relativa máxima: 3,4e-10.
> - Todas as decisões (rejeita aumento, rejeita queda, equivalência, leitura) batem.
> - As correções são de texto, rótulo e figura: duas de gravidade média e duas baixas (seção 5). Foram
>   feitas no script 36 e regeneradas por ele.<br>
> **Proveniência dos números:** lidos de `output/rdd_bolsa/NA_estimativas.csv`, `N_estimativas.csv` e
> `EQ_*` depois da correção. A conferência que fica no repositório é `TestCorrecoesAuditoria32` em
> `tests/test_equivalencia_H1.py`, junto com os recálculos que o teste já fazia.

## 1. Ordem dos commits

- `f47624f` toca dois arquivos: o protocolo 60 e o registro de mudanças.
- `af8e21f` é o filho direto. Traz o script, as saídas, o doc 57j, os testes, a linha do `run_all.py` e a
  do manifesto A6.
- O protocolo não mudou entre os dois commits. O SHA-256 do texto atual (`4c7cb1d0…`) é igual ao do texto
  congelado gravado no resumo.
- O protocolo declara o estatuto `PROTOCOLO_60_POS_RESULTADO`. Ele também diz que, pelos IC publicados,
  a parte A já era previsível em boa parte. O doc 57j repete isso no topo e nos limites.

## 2. Como a auditoria foi feita

O código foi escrito do zero. Não importa o script 36, a `rdd_lib` nem o scipy; a normal vem de
`math.erfc`, e z₀,₉₅ sai por bisseção (1,644853627).

**Seleção das linhas** (filtros próprios, uma linha por filtro, senão para):

| Linha | Arquivo | Filtro |
|---|---|---|
| A3 | `NA_estimativas.csv` | `outcome_id = A3_PREENCHIDA`, `especificacao = A3`, `variante = principal`, população e corte da linha |
| N1 | `N_estimativas.csv` | `outcome_id = N1`, `familia = N`, `especificacao = S-a`, `variante = principal` |
| N1, IC honesto | `N_estimativas.csv` | `especificacao = S-g`, `variante = S-a: ic_honesto_M_x1` (e M×0,5, M×2, pós-resultado) |

**Contas:**
- Margem: A3 0,10; N1 0,25 × `media_abaixo` da própria linha.
- Teste do aumento: p = Φ((τ̂ − m + B)/EP).
- Teste da queda: p = Φ((−m − τ̂ + B)/EP).
- B = 0 no IC convencional; B = `vies_max` gravado no IC honesto.
- IC 90% = τ̂ ∓ (B + z·EP). Margem mínima = max(|IC90 inf|, |IC90 sup|).
- Holm escrito de novo, entre as duas primárias, para p do aumento, p da queda e p do TOST.

**Conferências do insumo:**
- IC 95% gravado = τ̂ ± 1,96·EP pela normal nas nove linhas (diferença ≤ 7e-16).
- p de zero gravado = p normal bilateral (igual na quarta casa).
- A3 não tem IC honesto gravado: `ic_honesto_inf`, `vies_max` e `M` estão vazios nas 12 linhas
  principais de A3 em `NA_estimativas.csv`.

## 3. Recálculo

### 3.1 Primárias e secundárias (IC convencional)

A3 em p.p.; N1 em vagas por município. "Holm" só nas primárias. Todos os campos batem com o gravado,
com diferença relativa máxima de 3,4e-10 (o CSV tem 10 algarismos significativos).

| Linha | Papel | τ̂ | EP | Margem | IC 90% | p aumento (Holm) | p queda (Holm) | Margem mínima | Leitura (recálculo = gravado) |
|---|---|---|---|---|---|---|---|---|---|
| A3 empilhado, ciclos 1–3 | primária | −4,86 | 4,11 | ±10 | [−11,61; +1,90] | 0,00015 (0,00022) | 0,105 (0,211) | 11,61 | só o aumento |
| N1 empilhado, ciclos 1–3 | primária | −0,756 | 0,350 | ±0,539 | [−1,332; −0,180] | 0,00011 (0,00022) | 0,732 (0,732) | 1,332 (62% da média) | só o aumento |
| A3 0,300, ciclos 1–3 | secundária | −8,39 | 5,16 | ±10 | [−16,88; +0,10] | 0,00018 | 0,378 | 16,88 | só o aumento |
| A3 0,400, ciclos 1–3 | secundária | −1,32 | 6,46 | ±10 | [−11,94; +9,30] | 0,0398 | 0,0894 | 11,94 | só o aumento |
| A3 0,300, ciclo 1 | secundária | +0,91 | 12,45 | ±10 | [−19,57; +21,40] | 0,233 | 0,190 | 21,40 | inconclusivo |
| A3 0,400, ciclo 1 | secundária | −12,45 | 12,78 | ±10 | [−33,47; +8,58] | 0,0395 | 0,576 | 33,47 | só o aumento |
| A3 empilhado, ciclo 1 | secundária | −3,31 | 8,95 | ±10 | [−18,04; +11,41] | 0,0685 | 0,227 | 18,04 | inconclusivo |
| N1 0,300, ciclos 1–3 | secundária | −1,447 | 0,625 | ±0,581 | [−2,476; −0,419] | 0,00059 | 0,917 | 2,476 (107%) | só o aumento |
| N1 0,400, ciclos 1–3 | secundária | −0,142 | 0,347 | ±0,489 | [−0,712; +0,428] | 0,0344 | 0,159 | 0,712 (36%) | só o aumento |

Holm do p do TOST nas primárias: 0,211 (A3) e 0,732 (N1). Igual ao gravado.

### 3.2 IC honesto de N1

As 12 linhas (3 amostras × 4 variantes) batem com o gravado. Em todas, B é de 6,6 a 175 vagas por
município, contra margens de 0,49 a 0,58. Os dois p são 1,000, e a leitura é "inconclusivo".

| Amostra | B (regra do E6) | IC 90% honesto | Margem mínima |
|---|---|---|---|
| N1 empilhado | 78,25 | [−79,58; +78,07] | 79,58 |
| N1 0,300 | 87,76 | [−90,23; +87,34] | 90,23 |
| N1 0,400 | 46,36 | [−47,07; +46,79] | 47,07 |

Com B/EP desta ordem, o IC 90% do TOST honesto coincide com o IC 95% honesto bilateral gravado pelo
bloco. Isso é esperado: o valor crítico de Armstrong–Kolesár tende a B/EP + z₀,₉₅ quando B/EP é grande.

### 3.3 Robustez das decisões ao ajuste

As decisões das primárias não dependem da forma do Holm:
- sem ajuste: as duas rejeitam o aumento e não rejeitam a queda;
- Holm sobre os 4 p direcionais (2 outcomes × 2 sentidos): aumento 0,00044 e 0,00043, queda 0,211 e
  0,732. Mesma leitura.

## 4. Fidelidade ao protocolo 60, parte A

| Regra | Situação |
|---|---|
| Margens: A3 ±10 p.p.; N1 ±25% da média abaixo do corte na mesma amostra | ok; `media_abaixo` da própria linha gravada pelo bloco (achado B1 sobre a origem dos 25%) |
| TOST a 5% por lado, com os dois testes relatados separadamente | ok; colunas `p_aumento`, `p_queda`, `rejeita_*` e duas colunas na tabela do doc |
| Primárias com Holm entre as duas: A3 e N1 empilhados (ciclos 1–3) | ok |
| Secundárias: A3 por corte e no ciclo 1; N1 por corte | ok, com a interpretação 1 abaixo |
| Insumos: só `NA_estimativas.csv` e `N_estimativas.csv`, nada reestimado | ok; o script lê só esses dois CSV, o doc 57 (conferência) e os protocolos |
| IC honesto onde o bloco o gravou | ok; só em N1, com as quatro variantes gravadas; a principal é a regra do E6 |
| Margem mínima, descritiva | ok |
| Leitura pré-registrada | ok nas categorias; achado M1 sobre os qualificadores |
| Saídas, doc gerado entre marcadores, testes | ok |
| Integridade | ok (seção 7) |

### 4.1 As decisões de interpretação do agente

| # | Decisão | Defensável? | Muda a conclusão? |
|---|---|---|---|
| 1 | **Secundárias de A3:** "A3 por corte e no ciclo 1" = as outras cinco linhas de preenchimento do doc 57, §4.2 (ciclos 1–3 por corte; ciclo 1 por corte e empilhado). N1 por corte nos ciclos 1–3 | Sim. É a leitura mais literal ("por corte" na população das primárias; "no ciclo 1" com o mesmo detalhe), e coincide com as linhas já publicadas no doc 57. Ficaram de fora A3 e N1 por ciclo 2 e 3, que o protocolo não pede | Não: secundárias sem ajuste não entram na conclusão, e as primárias são as do protocolo |
| 2 | **Holm sobre três p:** Holm entre as duas primárias no p do aumento, no da queda e no do TOST; o script para se a decisão de equivalência pelas duas vias divergir | Sim. O Holm do p do TOST é a forma canônica para a hipótese de não equivalência. O Holm por sentido é o que sustenta as leituras direcionais ("só o aumento"). A parada em caso de divergência não é regra pré-registrada, mas é conservadora e não foi acionada | Não: com Holm em 2 ou em 4 p, ou sem ajuste, as leituras das primárias são as mesmas (3.3) |
| 3 | **TOST com o IC honesto:** p = Φ((τ̂ − m + B)/EP) e Φ((−m − τ̂ + B)/EP); IC 90% = τ̂ ∓ (B + 1,645·EP) | Sim. É o teste unilateral honesto de Armstrong e Kolesár: no limite de H0, o pior viés empurra τ̂ na direção de H0. O IC unilateral honesto usa B + z₀,₉₅·EP, não o valor crítico bilateral cv(B/EP). O teste sintético do script confere que B = 0 reproduz o convencional | Não: com qualquer das quatro variantes, nenhum teste rejeita |
| 4 | **Caso "só a queda":** não listado no protocolo; lido como o espelho do "só o aumento" | Sim. É a única leitura simétrica possível, e o doc diz que foi acrescentada | Não: nenhuma linha cai nesse caso |

## 5. Achados e correções

| # | Gravidade | Achado | Correção |
|---|---|---|---|
| M1 | média | A leitura pré-registrada só autoriza "não houve aumento de X ou mais" sob a aproximação local linear e para o pacote do corte. No CSV (coluna `leitura`), nas nove frases por linha do §3 do doc e na frase-síntese ("os dados descartam um aumento do tamanho das margens"), a frase aparecia sem qualificador. Os qualificadores só estavam nos limites e no parágrafo do IC honesto. Quem copia a frase da tabela ou da síntese para um slide perde a ressalva, e com o IC honesto de N1 o aumento **não** fica descartado | `QUALIF` no script: "(no IC convencional, sob a aproximação local linear e para o pacote do corte)" nas leituras `SO_AUMENTO` e `SO_QUEDA` do CSV e do doc. A síntese passa a dizer "no IC convencional e sob a aproximação local linear" e "Com o IC honesto de N1, nem isso se sustenta". O "Como ler" ganhou o mesmo qualificador e o caso "só do lado direito" |
| M2 | média | Na primária N1, o IC 90% fica **inteiro abaixo de zero**: [−1,33; −0,18]. O IC 95% do bloco também, com p = 0,031 sem ajuste. Na figura, a barra está toda à esquerda do zero, e a de N1 em 0,300 também. O doc não dizia isso. Dizia só que "o teste da queda não rejeita, mas isso não é evidência de queda". Num slide, a barra convida a ler queda | O sub-item de N1 do §3 agora diz que o IC 90% fica inteiro abaixo de zero (com o p sem ajuste, lido do bloco e gravado em `EQ_resumo.json["teste_zero_do_bloco"]`). Ele dá os quatro motivos de não ler queda: (i) Holm N1–N4 p = 0,124, com a ressalva do doc 49 de que com coeficiente único N1 rejeitaria; (ii) IC honesto com zero; (iii) placebo do ciclo 2; (iv) pacote. A figura ganhou rodapé gerado das saídas: nenhuma linha é equivalente; IC convencional e aproximação local linear; pacote do corte; "a figura não é teste de zero: barra à esquerda do zero não é lida como queda". O "Como ler" do doc ganhou o item "Barra inteira à esquerda do zero" |
| B1 | baixa | O protocolo 40, §7, dá +25% como referência para **candidaturas**, não para vagas preenchidas. O protocolo 60 aplica esses 25% a N1. O doc 57j e a coluna `regra_margem` diziam "referência do protocolo 40, §7", como se a referência fosse para N1. A margem é a do protocolo congelado e não muda | §1 do doc: frase explicando que a margem de N1 é escolha do protocolo 60, transplantada da referência de candidaturas. A coluna `regra_margem` de N1 diz o mesmo. A síntese diz "margens do protocolo 60" |
| B2 | baixa | "O placebo acusa forma não linear (doc 49, §9)" simplificava o doc 49. No ciclo 2, o corte placebo do segmento acusa salto **sem** controle (S-b, p = 0,010) e fica **no limiar** com controle (S-a, p = 0,052). N1 aqui é S-a | Texto novo, no motivo (iii): "o corte placebo do segmento acusa salto sem controle e fica no limiar com controle, e a reta local não capta a forma do outcome (doc 49, §3 e §9)" |

**Hashes depois da correção:**
- CSV: `9d0272f2…` → `c3ec87e5…`. Só mudaram as colunas `leitura` e `regra_margem`, conferido coluna a
  coluna; nenhum número mudou.
- PNG: `980e755c…` → `f1dd7792…` (rodapé; altura de 7,2 para 7,8 polegadas).
- `EQ_resumo.json`: `f4f5df2f…` → `1395fffd…`. Mudaram só a chave nova `teste_zero_do_bloco` e os hashes
  das saídas.

**Mudanças no código e nos testes:**
- Script 36: só textos e o rodapé da figura (`REGRA_MARGEM`, `QUALIF`, `LEITURAS`, `_frase`, `leitura`,
  `gerar_doc`, `gerar_figura`). O resumo ganhou a chave `teste_zero_do_bloco`, lida da linha de origem.
- Teste: classe `TestCorrecoesAuditoria32` (2 testes). Ela confere o qualificador em toda leitura
  direcional e o p de zero e o p de Holm de N1 contra `N_estimativas.csv`. Também confere que, com o
  IC 90% abaixo de zero, o doc diz "o IC 90% fica inteiro abaixo de zero" e "Isso não é lido como queda".

**Observações sem correção:**
- O "Como ler" fica no doc, não dentro do PNG, como nas figuras anteriores (auditorias 28 e 31). Agora a
  figura tem rodapé com a ressalva de linguagem.
- A fonte dos rótulos é de 8 pt numa figura de 8,2 polegadas. Fica legível em slide de largura inteira
  (conferido no PNG), mas não em meia largura.
- O script 36 importa a `rdd_lib` (`holm`, `p_normal`, `cv_honesto`). Por isso o recálculo desta
  auditoria não a usa.

## 6. Linguagem

| Ponto | Situação |
|---|---|
| Equivalência só quando os dois testes rejeitam | ok: nenhuma linha é equivalente, e o doc diz "Nenhuma linha mostra equivalência". O teste `test_linguagem` proíbe "os dois testes rejeitam" na leitura quando não há equivalência |
| "Não houve aumento de X ou mais" só sob a aproximação local linear e para o pacote do corte | corrigido (M1) |
| Estimativa pontual negativa de N1 não vendida como queda | ok antes, reforçado (M2). Nenhuma frase diz que houve queda, que caiu ou que a bolsa reduz o preenchimento |
| Nada de "a bolsa não funciona" | ok: só aparece negado ("nada aqui diz que a bolsa 'funciona' ou 'não funciona'") |
| Contraste: pacote do corte, não a bolsa isolada nem a participação no PMM-E | ok, no §5 (limites), na síntese, no resumo (`contraste`) e agora no rodapé da figura |
| Pós-resultado | ok: o topo e os limites dizem que as margens foram fixadas depois de ver os IC 95% e que o teste "é formal, mas não é confirmatório" |

## 7. Integridade

- **`data/`.** `git diff --stat 62e1539 af8e21f -- data/` vem vazio, e esta auditoria não escreve em
  `data/`.
- **Arquivo de IVS errado.** `ivs_ipea_2010_municipios` não aparece no script 36 nem na `rdd_lib` (grep).
  O script não lê IVS nenhum: só estimativas gravadas.
- **Saídas de outros blocos.** O commit `af8e21f` não toca `NA_estimativas.csv`, `N_estimativas.csv` nem
  outro arquivo de `output/` além de `EQ_*` e do manifesto A6. Depois de rodar o script 36 nesta
  auditoria, `git status` mostra só `EQ_*`, o doc 57j, o script e o teste.
- **Manifesto A6.** O diff de `af8e21f` é uma linha só (o comando do script 36, depois do 34).
  `scripts/tema_trabalho/07_red_team_sintese.py` foi reexecutado e regravou o manifesto byte a byte igual.
  As correções não mudam a lista de passos.
- **Hashes de proveniência.** As cinco entradas de `EQ_resumo.json["entradas"]` batem com os arquivos.
  Saídas e figura também (teste `test_hashes`).
- **Determinismo.** Duas execuções seguidas de `36_equivalencia_H1.py --atualizar-doc` dão CSV, JSON, PNG
  e doc com o mesmo SHA-256, antes e depois das correções.
- **CNES.** Nenhum mês é lido.
- **Rótulo.** `natureza_dos_dados = EMPIRICO` e `estatuto = PROTOCOLO_60_POS_RESULTADO` em toda linha e no
  resumo.

## 8. Testes

Cada execução foi gravada em log, e o código de saída foi conferido. A suíte inteira e o `run_all.py` não
foram rodados.

| Comando | Resultado | Código de saída |
|---|---|---|
| `pytest tests/test_equivalencia_H1.py` (antes das correções) | 23 passam | 0 |
| `pytest tests/test_equivalencia_H1.py` (depois das correções) | 25 passam | 0 |
| `pytest tests/test_integridade_dados.py` | 4 passam | 0 |
| `pytest tests/test_pipeline_rdd_bolsa.py` | 15 passam | 0 |
