# Reestimação com a base oficial do IVS: registro do failure mode

> **Data:** 18/10/2026.<br>
> **Gerado por:** `scripts/tema_trabalho/12_registrar_failure_mode_ivs.py`. Todo número
> deste documento vem de `output/tema_trabalho/failure_mode_ivs_antes_depois.csv`,
> `output/tema_trabalho/failure_mode_ivs_resumo.json` ou dos artefatos citados. Os
> valores "antes" foram lidos do histórico do Git, no commit `22eddb528c37`, o
> último anterior à correção.<br>
> **Regra do autor:** "reestime tudo com os números certos, da base oficial. Os velhos
> só servem para serem documentados como failure mode e não devem ser usados para NADA
> no trabalho real." Os números da coluna "antes" deste documento têm esse estatuto:
> `FAILURE_MODE`. Não são citáveis como resultado.<br>
> **Antecedente:** [`16`](16_ivs_2010_oficial_e_arquivo_local.md) (o arquivo é uma linha
> de subgrupo); [`06_execucao/38`](../06_execucao/38_estado_e_pendencias_rdd_bolsa.md), D3.<br>
> **Protocolo:** tarefa E de [`06_execucao/40`](../06_execucao/40_protocolo_multioutcome_rdd_bolsa.md).

## 1. O que deu errado

`data/ivs_ipea_2010_municipios.csv` entrou no commit inicial do repositório sem script de
aquisição nem fonte. Ele vem da base completa do Atlas da Vulnerabilidade Social do Ipea,
mas não é a linha do município (cor, sexo e situação de domicílio "Total"): é, em cada
município, a última linha de 2010 com IVS preenchido, na ordem da planilha
(`output/rdd_bolsa/identificacao_arquivo_local_ivs.json`):

| Linha da base que ficou no arquivo | Municípios |
|---|---:|
| Negro / Mulher / Urbano | 4362 |
| Negro / Mulher / Total Situação de Domicílio | 576 |
| Total Cor / Mulher / Urbano | 484 |
| Total Cor / Mulher / Total Situação de Domicílio | 142 |
| Total Cor / Total Sexo / Total Situação de Domicílio | 1 |

Comparado com o IVS oficial do município nos 5.565 municípios, o arquivo
acerta o IVS a 3 casas em 38 e tem correlação de
0,85. A coluna de população soma
41.852.890 habitantes, contra
190.755.799 da linha total (Censo 2010): é a população do
subgrupo.

## 2. Como se propagou

| Etapa | O que herdou | Uso |
|---|---|---|
| `scripts/aquisicao/04_harmonizar_territorio_ibge.py` → `malha_municipios_regioes_saude.parquet` | IVS, subíndices, categoria, IDHM, população 2010, renda | raiz da propagação |
| `scripts/aquisicao/05_integrar_painel_analitico.py` → painel município–curso mensal → `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet` e `A5_painel_T0.parquet` | `ivs_2010`, `ivs_categoria`, `populacao_2010` | covariável (b) |
| `scripts/tema_trabalho/03_construir_tipologia_territorial.py` (A2) | as mesmas colunas e `estoque_pre_por_10k`, dividido pela população do subgrupo | covariável (b); o estrato não dependia do arquivo |
| `scripts/tema_trabalho/05_estimar_atracao.py` (A4) | gradiente de IVS, `log_pop`, `estoque_por_10k` no ajuste completo, winsorizado, quadrático, IVS só e estrato × IVS | gradiente (a) e covariável (b) |
| `scripts/tema_trabalho/06_avaliar_provimento_cnes.py` (A5) | `ivs_2010`, `log_pop`, `estoque_por_10k` nas especificações completas e de heterogeneidade | covariável (b) |
| `scripts/avaliacao_impacto/07_gerar_tabelas_e_figuras.py` | IVS e população da Tabela 1 (descritiva) do ciclo 1 | descritivo (b) |
| `scripts/tema_trabalho/01_auditar_atracao_provimento_interior.py` | o veredito "regra não se reproduz" do script retirado `rdd_bolsa/00` | running variable (a), por via indireta |
| `scripts/tema_trabalho/07_red_team_sintese.py` → `docs/auditorias/09`, `docs/06_execucao/32` | o coeficiente do ajuste completo | texto |

A cadeia da RDD da bolsa (`rdd_bolsa/04b` em diante) já usava o IVS oficial desde 14/10/2026.

### Todos os leitores, diretos e indiretos

Classes: (a) running variable ou gradiente de IVS; (b) covariável; (c) só documenta ou
inventaria o erro, com rótulo; (d) retirado, fora do pipeline; (—) não lê nem herda.

| Script | Como chega ao arquivo | Classe | No `run_all.py` | Situação |
|---|---|---|---|---|
| `scripts/00_inventario_dados.py` | direto: inventário de data/ | (c) | sim | mantido como inventário, com rótulo FAILURE MODE na saída |
| `scripts/02_auditar_fontes_pmme.py` | direto: hash, linhas e campos | (c) | sim | mantido como auditoria de fontes, com rótulo FAILURE MODE |
| `scripts/aquisicao/04_harmonizar_territorio_ibge.py` | direto: IVS, subíndices, IDHM, população, renda da malha | (a) e (b) | sim | corrigido: a08 + Censo 2022; a07 e a08 sobem no run_all para antes dele |
| `scripts/aquisicao/05_integrar_painel_analitico.py` | indireto: colunas da malha no painel mensal | (b) | sim | herda a malha corrigida; não roda sem o CNES mensal (>16 GB); consumidores repõem as colunas |
| `scripts/avaliacao_impacto/07_gerar_tabelas_e_figuras.py` | indireto: painel município–curso | (b) descritivo | sim | corrigido: IVS e população da a08; Tabela 1 regenerada |
| `scripts/avaliacao_ciclo3/03_auditar_pre_e_potencia.py` | indireto: painel_municipios_regioes (ivs_2010, log_pop_2010) | (b) | não | PENDENTE: ciclo 3 congelado; herda a malha corrigida na próxima execução, mas as saídas de 31/08/2026 usaram o arquivo errado |
| `scripts/tema_trabalho/01_auditar_atracao_provimento_interior.py` | indireto: veredito de rdd_bolsa/00 | (a) | sim | corrigido: confere a regra com a a08 |
| `scripts/tema_trabalho/03_construir_tipologia_territorial.py` | indireto: malha | (b) | sim | corrigido: colunas da a08; estoque por 10 mil com Censo 2022 |
| `scripts/tema_trabalho/04_congelar_pre_analise.py` | indireto: hash da malha e da tipologia | registro | sim | emenda datada no registro A3 |
| `scripts/tema_trabalho/05_estimar_atracao.py` | indireto: tipologia | (a) e (b) | sim | reestimado |
| `scripts/tema_trabalho/06_avaliar_provimento_cnes.py` | indireto: painel em T0 e tipologia | (b) | sim | reestimado; covariadas repostas em memória |
| `scripts/tema_trabalho/06b_ameacas_a5_placebo_pretendencia_deslocamento.py` | indireto: painel em T0, sem covariadas contínuas | (—) | sim | reexecutado só para atualizar o hash de A5 |
| `scripts/tema_trabalho/07_red_team_sintese.py` | direto: hash com rótulo; texto do ajuste completo | (c) | sim | ajuste completo corrigido; arquivo hasheado só como failure mode |
| `scripts/tema_trabalho/08_auditar_cutoff_selecao.py, 09_*, 09b_*` | não leem | (—) | sim | inalterado |
| `scripts/tema_trabalho/10_conferir_numeros_artigo.py, 11_*` | comentários | (c) | sim | conferem o ajuste completo corrigido |
| `scripts/tema_trabalho/12_registrar_failure_mode_ivs.py` | direto: documenta o erro | (c) | não | este registro |
| `scripts/aquisicao/06_adquirir_populacao_censo2022.py` | só docstring | (—) | não | inalterado |
| `scripts/aquisicao/a03_adquirir_ivs_regra.py` | direto: diagnóstico da regra | (a) | não | (d) histórico |
| `scripts/aquisicao/a06_integrar_portao.py` | texto da matriz variável–fonte | (a) | não | (d) histórico |
| `scripts/aquisicao/a08_adquirir_ivs_2010_oficial.py` | só observação no manifesto | (c) | sim | inalterado |
| `scripts/rdd_bolsa/00_*, 01_*, 01b_*` | direto: running variable | (a) | não | (d) retirados em 18/10/2026 |
| `scripts/rdd_bolsa/02_*, 03_*` | indireto: portões feitos com o arquivo | (a) | não | (d) retirados em 18/10/2026 |
| `scripts/rdd_bolsa/04_portao_r1_escore_administrativo.py` | direto: correlação com o escore do MS | (c) | sim | inalterado |
| `scripts/rdd_bolsa/04b_*, 04c_*` | direto: compara com a base oficial e reproduz o erro | (c) | sim | inalterado |
| `scripts/rdd_bolsa/06_estimar_E2_limites.py, 08_estimar_E4_proporcao.py` | direto: banda do cenário "informado" | (a) | sim | protegidos e congelados; cenário rotulado "sem valor" no relatório; não alterados |
| `scripts/rdd_bolsa/07_*, 08a_*, 09b_*, 11_*` | não leem o arquivo; E3 e E5 leem da tipologia só o estrato | (—) | sim | protegidos; não reexecutados |
| `scripts/rdd_bolsa/09_gerar_relatorio_pdf.py, 10_galeria_figura_regra.py` | direto: figura comparativa | (c) | sim | inalterado |
| `scripts/revisao_literatura/historico/gerar_doc_modelagem_micro_comparada.py` | texto histórico | (d) | não | histórico |

O teste `tests/test_fonte_ivs_oficial.py` impede que um script novo do pipeline leia o
arquivo fora da lista de documentadores do failure mode.

## 3. Como foi detectado

Em 14/10/2026, o escore administrativo publicado pelo Ministério da Saúde não batia com o
arquivo local, mas batia com a linha total da base oficial do Ipea (a08). O script
`scripts/rdd_bolsa/04c_identificar_recorte_arquivo_local.py` reproduziu o arquivo inteiro a
partir da base oficial e identificou o erro de extração ([`16`](16_ivs_2010_oficial_e_arquivo_local.md)).
Naquela data a RDD passou a usar o IVS oficial, mas A2, A4, A5 e a Tabela 1 do ciclo 1
continuaram a ler a malha antiga; a decisão D3(b) adiou a reestimação, aplicada aqui.

## 4. O que foi corrigido

- A malha (`04_harmonizar`) lê IVS, subíndices, IDHM, população 2010 e renda da a08 e o
  código de 7 dígitos e a população 2022 do Censo 2022; manifesto em
  `output/aquisicao/manifesto_territorio_ibge.json`.
- A tipologia A2 ganha `populacao_2022`, denominador de `estoque_pre_por_10k`. O registro
  A3 recebe a emenda datada de 18/10/2026: especificação, amostras e desfechos não mudam;
  mudam os insumos e os hashes de entrada.
- A4 e A5 foram reexecutados. A5 troca em memória as covariadas do painel em T0 congelado,
  que não é regravado (é a âncora de hash da reestimação).
- A Tabela 1 do ciclo 1 repõe IVS e população da a08.
- `tema_trabalho/01` confere a regra com o IVS oficial.
- Os artigos citam o ajuste completo corrigido, conferido contra `output/` pelos scripts
  `10` e `11`.

Tipologia: o estrato é idêntico antes e depois (sim);
o estoque pré também (sim). Depois da correção,
`ivs_2010` é igual ao IVS oficial em 5565 de
5565 municípios; antes e depois coincidem a 3 casas em
38 e a categoria de IVS em
2999 de 5570.

| Tipologia, população A1 (540 municípios) | Antes (failure mode) | Depois |
|---|---:|---:|
| IVS médio | 0,329 | **0,327** |
| População 2010 mediana | 9.092 | **45.185** |
| Estoque pré por 10 mil hab., mediana (368 municípios do quadro) | 4,43 | **0,81** |

## 5. Antes e depois, por estimativa

Blocos sem covariadas contínuas, que servem de controle da reexecução (coeficientes
iguais a 1e-9): A4 modelo principal (sem covariadas contínuas), A5 estudo de evento proporcional, mar/2026 (sem covariadas contínuas), A5 estudo de evento em nível, mar/2026 (sem covariadas contínuas).

### A4 modelo principal (sem covariadas contínuas)

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `estrato_metropolitano` | 0,279 | **0,279** | 0,059 → 0,059 | 0,000 → 0,000 | 0,000 → 0,000 |
| `estrato_capital` | 0,326 | **0,326** | 0,072 → 0,072 | 0,000 → 0,000 | 0,000 → 0,000 |
| `estrato_interior_proximo_polo` | 0,121 | **0,121** | 0,043 → 0,043 | 0,005 → 0,005 | 0,005 → 0,005 |

### A4 ajuste completo

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `estrato_metropolitano` | 0,209 | **0,185** | 0,078 → 0,078 | 0,008 → 0,018 | 0,023 → 0,055 |
| `estrato_capital` | 0,198 | **0,154** | 0,122 → 0,121 | 0,106 → 0,204 | 0,120 → 0,204 |
| `estrato_interior_proximo_polo` | 0,082 | **0,071** | 0,053 → 0,052 | 0,120 → 0,173 | 0,120 → 0,204 |
| `ivs_2010` | −0,245 | **−0,310** | 0,281 → 0,325 | 0,384 → 0,340 | — → — |
| `log_pop` | 0,036 | **0,051** | 0,023 → 0,025 | 0,117 → 0,042 | — → — |
| `estoque_por_10k` | 0,001 | **0,004** | 0,001 → 0,006 | 0,257 → 0,462 | — → — |
| `faixa_FAIXA 2` | −0,011 | **−0,028** | 0,047 → 0,056 | 0,816 → 0,623 | — → — |
| `faixa_FAIXA 3` | −0,100 | **−0,131** | 0,064 → 0,082 | 0,119 → 0,109 | — → — |

### A4 ajuste completo winsorizado p99

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `estrato_metropolitano` | 0,212 | **0,187** | 0,078 → 0,078 | 0,007 → 0,017 | 0,020 → 0,050 |
| `estrato_capital` | 0,205 | **0,162** | 0,122 → 0,122 | 0,093 → 0,185 | 0,106 → 0,185 |
| `estrato_interior_proximo_polo` | 0,086 | **0,073** | 0,053 → 0,052 | 0,106 → 0,161 | 0,106 → 0,185 |
| `ivs_2010` | −0,243 | **−0,308** | 0,281 → 0,325 | 0,387 → 0,343 | — → — |
| `log_pop` | 0,034 | **0,050** | 0,023 → 0,025 | 0,139 → 0,048 | — → — |
| `estoque_por_10k` | 0,001 | **0,005** | 0,001 → 0,006 | 0,474 → 0,429 | — → — |

### A4 IVS quadrático

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `ivs_2010` | −0,957 | **−1,587** | 1,166 → 1,071 | 0,412 → 0,138 | — → — |
| `ivs_2010_sq` | 0,952 | **1,550** | 1,516 → 1,222 | 0,530 → 0,205 | — → — |
| `estrato_metropolitano` | 0,211 | **0,194** | 0,078 → 0,078 | 0,007 → 0,012 | 0,021 → 0,037 |

### A4 IVS só (FE)

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `ivs_2010` | −0,102 | **−0,186** | 0,241 → 0,203 | 0,671 → 0,360 | — → — |

### A4 estrato × IVS

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `ivs_2010` | 0,674 | **0,332** | 0,410 → 0,322 | 0,100 → 0,302 | — → — |
| `estrato_capital_x_ivs` | −3,685 | **−3,210** | 0,785 → 0,840 | 0,000 → 0,000 | — → — |
| `estrato_metropolitano_x_ivs` | −0,572 | **−0,248** | 0,650 → 0,557 | 0,379 → 0,656 | — → — |
| `estrato_interior_proximo_polo_x_ivs` | −0,661 | **−0,252** | 0,441 → 0,337 | 0,134 → 0,454 | — → — |

### A5 estoque em 6 meses, completo

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `atracao_muni` | 0,377 | **0,352** | 0,225 → 0,231 | 0,094 → 0,127 | 0,133 → 0,158 |
| `estrato_capital` | −1,685 | **−1,341** | 0,833 → 0,836 | 0,043 → 0,109 | — → — |
| `estrato_metropolitano` | −0,351 | **−0,203** | 0,437 → 0,442 | 0,422 → 0,646 | — → — |
| `estrato_interior_proximo_polo` | −0,147 | **−0,063** | 0,247 → 0,242 | 0,550 → 0,796 | — → — |
| `ivs_2010` | 2,376 | **2,561** | 2,176 → 1,675 | 0,275 → 0,126 | — → — |
| `log_pop` | 0,224 | **0,185** | 0,119 → 0,133 | 0,060 → 0,164 | — → — |
| `estoque_por_10k` | 0,015 | **0,148** | 0,013 → 0,086 | 0,231 → 0,087 | — → — |

### A5 cobertura em 6 meses, completo

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `atracao_muni` | 0,032 | **0,031** | 0,018 → 0,018 | 0,077 → 0,084 | 0,133 → 0,158 |

### A5 entradas em 6 meses, completo

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `atracao_muni` | 0,119 | **0,116** | 0,074 → 0,074 | 0,106 → 0,117 | 0,133 → 0,158 |

### A5 presença em 6 meses, completo

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `atracao_muni` | 0,016 | **0,019** | 0,039 → 0,039 | 0,679 → 0,632 | 0,679 → 0,632 |

### A5 heterogeneidade atração × estrato

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `atracao_muni` | 0,623 | **0,626** | 0,331 → 0,338 | 0,060 → 0,064 | — → — |
| `atracao_x_capital` | −0,108 | **−0,112** | 1,574 → 1,581 | 0,945 → 0,944 | — → — |
| `atracao_x_metropolitano` | 0,162 | **0,161** | 0,576 → 0,568 | 0,778 → 0,777 | — → — |
| `atracao_x_interior_proximo_polo` | −0,346 | **−0,349** | 0,425 → 0,420 | 0,416 → 0,406 | — → — |

### A5 estudo de evento proporcional, mar/2026 (sem covariadas contínuas)

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `atracao (amostra confirmatória)` | 0,068 | **0,068** | 0,018 → 0,018 | 0,000 → 0,000 | — → — |

### A5 estudo de evento em nível, mar/2026 (sem covariadas contínuas)

| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |
|---|---:|---:|---|---|---|
| `atracao (amostra confirmatória)` | 0,500 | **0,500** | 0,234 → 0,234 | 0,033 → 0,033 | — → — |

### Tabela 1 do ciclo 1 (descritiva)

| Variável | Coluna | Antes (failure mode) | Depois |
|---|---|---:|---:|
| População municipal 2010 | Imediata média | 40625,549 | **139186,874** |
| População municipal 2010 | Reserva média | 30713,394 | **112082,708** |
| População municipal 2010 | Diferença padronizada | 0,140 | **0,137** |
| IVS 2010 | Imediata média | 0,341 | **0,343** |
| IVS 2010 | Reserva média | 0,346 | **0,347** |
| IVS 2010 | Diferença padronizada | −0,073 | **−0,036** |

### Diagnóstico do tema (`tema_trabalho/01`), módulo da RDD

- Antes (failure mode): "177 de 368 municípios divergem da regra candidata".
- Depois: "368 de 368 municípios com a faixa anunciada reproduzida pelo IVS 2010 oficial (a08), cortes 0,300 e 0,400; 0 sem IVS oficial".

## 6. Que conclusões mudam

Mudanças de sinal ou de lado do limiar de 5% (p, ou q de FDR quando a tabela o publica):

- **A4 ajuste completo, `estrato_metropolitano`:** 0,209 → 0,185; o q de FDR cruza 5% (0,023 → 0,055).
- **A4 ajuste completo, `log_pop`:** 0,036 → 0,051; o p cruza 5% (0,117 → 0,042).
- **A4 ajuste completo winsorizado p99, `log_pop`:** 0,034 → 0,050; o p cruza 5% (0,139 → 0,048).
- **A5 estoque em 6 meses, completo, `estrato_capital`:** −1,685 → −1,341; o p cruza 5% (0,043 → 0,109).

Leitura:
- **O gradiente territorial de A4 não muda.** O modelo principal, o logit, os estágios e o
  colapso município–curso não usam covariadas contínuas e são idênticos.
- **O ajuste completo enfraquece.** O contraste metropolitano cai de
  20,9 para 18,5 p.p.;
  o p passa de 0,008 a 0,018 e o q de FDR dos
  três estratos, de 0,023 a 0,055. A leitura
  "associado a maior atração mesmo com ajuste" vale só pelo p nominal.
- **O gradiente de IVS continua indistinguível de zero** condicional aos efeitos fixos, com
  ou sem estrato. A interação capital × IVS continua distinta de zero.
- **A5:** o estudo de evento, que é o resultado secundário citado, não muda. As
  especificações completas mudam pouco e nenhuma vira significante.
- **RDD da bolsa:** nada muda. E3 e E5 leem da tipologia só o estrato; o hash de tipologia
  que gravaram é o da versão antiga (E3: sim;
  E5: sim), e o estrato é idêntico.
  Por isso os artefatos protegidos da cadeia (07, 08, 08a, 11, 09b) não foram reexecutados.

## 7. Onde os números antigos ainda aparecem

Só como failure mode, rotulados:
- **este documento**, coluna "antes";
- `output/tema_trabalho/failure_mode_ivs_antes_depois.csv` e `failure_mode_ivs_resumo.json`;
- o histórico do Git até `22eddb528c37`;
- colunas `ivs_2010`, `ivs_categoria`, `populacao_2010` e `estoque_*` gravadas em
  `A5_painel_T0.parquet` e em `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet`,
  que não são regeneráveis sem o CNES mensal e não entram em nenhum modelo nem tabela
  (A5 e a Tabela 1 as substituem em memória);
- `output/rdd_bolsa/diagnostico_viabilidade_salario_ivs.json` e as saídas dos scripts
  retirados `rdd_bolsa/00`, `01`, `01b`, `02`, `03` e `aquisicao/a03`, `a06`;
- o cenário "informado" de E2 e E4, já rotulado "sem valor" no relatório da RDD;
- a errata E-7 de [`14`](14_erratas_artefatos_congelados.md), com nota de failure mode;
- [`16`](16_ivs_2010_oficial_e_arquivo_local.md), [`17`](17_guia_conferencia_manual_ivs.md)
  e a figura comparativa do relatório da RDD, que documentam o erro.

## 8. Proveniência

| Arquivo | SHA-256 |
|---|---|
| `data/ivs_ipea_2010_municipios.csv` | `84d23a156d2afc327ad193fb71a165f1092cfc7e53c3dd7faca21d6aa131818c` |
| `output/aquisicao/a08_ivs_2010_oficial_municipio.csv` | `0632a7a313e1179ffd2f0096769143794907ccfcedfec560f6043ed9b2db31fe` |
| `output/aquisicao/populacao_censo2022_municipios.csv` | `b51fc6cf27a49fd559415280fa7cfb7e89c28f92125720b280b9455e7f36c96b` |
| `output/rdd_bolsa/identificacao_arquivo_local_ivs.json` | `674e8f36243ad433f0925bcd554df05d028b2523f29a4965e85a4343846e8eff` |
| `output/tema_trabalho/matriz_tipologia_territorial.parquet` | `63707c3c235ad099bb88542c4428d5a2091cab28c2b5b5c033afaf7482d9a8da` |
| `output/rdd_bolsa/E3_status.json` | `1bdda808efa70a3c1066872a5631fa4cf4dc0b1ce483e7db79c10161e391dd0a` |
| `output/rdd_bolsa/E5_resumo.json` | `eff1cf2e33a236b8fb674571fe40d85a30eb1352c8e605cab678557c38db05b4` |
| `output/avaliacao_impacto/tabelas/tabela1_estatisticas_descritivas_baseline.csv` | `ff48ffe42de3e050c56b5fae733bf6fe4362195213771a316f0f8c1e1db4e949` |
| `output/tema_trabalho/A4_tabela_02_modelo_principal_LPM.csv` | `3e7cf00700b2990967c83ffddc05fd58163e2890fd547e7bd1194e3d59b8ee0e` |
| `output/tema_trabalho/A4_tabela_03_separacao_faixa_ivs_remoticidade.csv` | `4731e7caac1dc11b88cdc883e8f8ebffc09c3d92e7d740fc42f8930c87fa081b` |
| `output/tema_trabalho/A4_tabela_03b_ajuste_completo.csv` | `fa2d4c960145ace687f92313926d0860defbe617db7223724710ec14c99efa42` |
| `output/tema_trabalho/A4_tabela_03c_winsorizado.csv` | `fb21b8a6fa1161e901bff7187f80c44c46ddb790aab0e0e331fd7e91211085f8` |
| `output/tema_trabalho/A4_tabela_03d_ivs_spline.csv` | `7c8c968be21a1c159cc0a7f7d7a65f8085a06e5d6eb9cea9516383f25758cf39` |
| `output/tema_trabalho/A5_tabela_03_modelo_estoque_6m.csv` | `27ea0b675238d450e3d653aefaa6d38936d94e9f245866e5783081d22158e488` |
| `output/tema_trabalho/A5_tabela_03c_modelo_cobertura.csv` | `4bc3305c1f1cfc18c0a9cfc70022093aef2e4685ee8d900ac41820e5dbba8065` |
| `output/tema_trabalho/A5_tabela_03d_modelo_entradas.csv` | `1b1845c0e31cf14c2de22417a48ca996dce0620ebc7e8f0914e22955e042754b` |
| `output/tema_trabalho/A5_tabela_03e_modelo_presenca.csv` | `fd185c8b3a184bdc857c609d0368843d76b5f82047fe0f34ac0b2f9d49e7fb05` |
| `output/tema_trabalho/A5_tabela_03i_heterogeneidade_estrato.csv` | `b37ae8fe90f73ea1227bcfc52c9444e78a96903f802c5a626e7d2d9cb4bb22c2` |
| `output/tema_trabalho/A5_tabela_07_estudo_evento_atracao.csv` | `b21797f18a15f71d7ed54fe33c3a673f9d3b659b7dd0323a48f22a3d7bb01680` |
| `output/tema_trabalho/A5_tabela_08_estudo_evento_proporcional.csv` | `fd342fac1e479502320ab1d9b00e4c685d4280ba13fa81ff216002c780393ea2` |
| `output/tema_trabalho/diagnostico_atracao_provimento_interior.json` | `27f01389dfb2bb4e436b9198544c4902dcc881949ccf2ca6bf76fc847e7dabb8` |

*Gerado por `scripts/tema_trabalho/12_registrar_failure_mode_ivs.py`.*
