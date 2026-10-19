# 46 — Resultados exploratórios pós-síntese (X1–X6)

## X1

> **Protocolo:** [`45_protocolo_exploratorio_pos_sintese.md`](45_protocolo_exploratorio_pos_sintese.md),
> §2 e §3 (X1), congelado em 19/10/2026.<br>
> **Estatuto:** `EXPLORATORIO_POS_SINTESE`. Nada aqui é teste confirmatório nem
> muda o protocolo 40, os resultados E3–E9 ou o Holm das primárias.<br>
> **Script:** `scripts/rdd_bolsa/17_ponte_pmme_cnes.py`.<br>
> **Saídas:** `output/rdd_bolsa/X1_ligacao_resumo.json`, `X1_medicos.parquet`,
> `X1_estimativas.csv` e `X1_descritivo.csv`. Natureza dos dados: **EMPIRICO**.<br>
> **Testes:** `tests/test_x1_ponte_cnes.py`.<br>
> **Números:** todo número de resultado está entre marcadores `<!-- X1:... -->`,
> gerados só das saídas por
> `python3 scripts/rdd_bolsa/17_ponte_pmme_cnes.py --atualizar-doc`. O teste
> confere os blocos contra as saídas e a prosa fora deles.

### X1.1 O que foi feito

- **Lado PMM-E:** a relação nominal de ativos (retrato de 11/09/2026, a mesma do
  E3 e do E6) mais os registros da lista nominal de 12/08/2026 que não estão
  nela. O nome é lido só em memória.
- **Lado CNES:** as competências 202406, 202501, 202506, 202510, 202602 e
  202608, baixadas do servlet HTTPS do CNES. Os seis ZIPs têm o mesmo SHA-256 dos
  ZIPs do a09, e a extração reproduz exatamente a contagem de vínculos médicos do
  a09 em cada mês (portão fail-closed). Os ZIPs foram apagados. O extrato com
  registro profissional e nome normalizado fica em `output/rdd_bolsa/X1_cache/`,
  fora do Git. Nenhum mês a partir de 202609 é lido.
- **Região de saúde:** a CIR do painel do PMMB do Ministério da Saúde, por
  município. Ela bate com a região impressa na lista de ativos em todos os
  municípios do PMM-E. O campo `CO_REGIAO_SAUDE` do CNES é texto livre e
  muitas vezes vazio, e não é usado.
- **Distância:** círculo máximo entre os centroides municipais da API de malhas
  v3 do IBGE (URL, data e SHA-256 no resumo).
- **Pseudônimo:** cada registro tem um `id_medico` determinístico. As saídas não
  trazem nome, CPF, CNS, CRM nem código de profissional do CNES.

### X1.2 Desvio D1 na regra de ligação

O doc 45 fixa a regra: CRM+UF exato; depois CRM exato com nome compatível;
ambíguos ficam fora. As listas do PMM-E, porém, trazem a UF do **posto**, e não
a do CRM. Quando o médico tem CRM de outra UF, o mesmo número pode pertencer a
outra pessoa na UF do posto, e a etapa 1 literal liga a pessoa errada. A
conferência de nomes da etapa 1 encontrou ligações sem nenhum nome em comum e
sem vínculo no estabelecimento do posto.

- **Principal (D1):** na etapa 1, o candidato único só liga se o nome for
  compatível. Sem isso, o registro segue para a etapa 2.
- **Sensibilidade:** a regra literal é relatada (taxa e descritivo).
- **Honestidade:** o desvio foi decidido depois da primeira execução completa,
  que gravou e exibiu as estimativas com a regra literal. O motivo é a
  qualidade da ligação, não o resultado.

<!-- X1:ligacao:inicio -->
| Ciclo | Registros | Ligados | Taxa | Etapa 1 (CRM+UF) | Etapa 2 (CRM+nome) | Ambíguos | Não achados |
|---|---|---|---|---|---|---|---|
| 1 | 525 | 499 | 95,0% | 428 | 71 | 0 | 26 |
| 2 | 968 | 909 | 93,9% | 802 | 107 | 1 | 58 |
| 3 | 497 | 468 | 94,2% | 379 | 89 | 0 | 29 |

Motivos (todos os ciclos): ambiguo_crm_nome_com_mais_de_um_profissional: 1; crm_ausente_na_lista: 2; crm_sem_nome_compativel: 58; crm_sem_vinculo_medico_no_cnes: 53; ligado: 1.876.
Etapa 1 (CRM + UF do posto) com candidato único: 1.715; com nome compatível: 1.609 (93,8%). Sem nome compatível (desvio D1, vão para a etapa 2): 106, das quais 81 ligam na etapa 2.
Conferência (ligados com início antes de 202608 que têm vínculo médico no estabelecimento do posto em 202608): principal_d1, 1_crm_uf: 80,6% de 1.229; principal_d1, 2_crm_nome: 76,4% de 178; literal_doc45, 1_crm_uf: 76,0% de 1.310; literal_doc45, 2_crm_nome: 72,7% de 121.
Regra literal do doc 45 (sensibilidade): 1.901 registros ligados; mesmo profissional nas duas regras: 1.795; profissional diferente: 81; ligado só na literal: 25.
<!-- X1:ligacao:fim -->

### X1.3 De onde vieram os especialistas (descritivo)

Médicos ligados dos ciclos 1 e 2, por faixa anunciada. A origem é a da última
competência lida antes do mês de início, pela ligação mais próxima. A distância
é a do município de origem mais próximo, e vale zero para quem já estava no
município. A coluna (e) conta vínculos médicos em 202608. Tudo aqui é
**descritivo**: a faixa acompanha o IVS e o porte do município, e a diferença
entre faixas não é efeito da bolsa.

<!-- X1:descritivo:inicio -->
| Ciclo | Faixa | Ligados | (a) mesmo estab. | (b) mesmo município | Novo no município | Mesma região | Mesma UF | Outra UF | Sem vínculo médico | Distância média (km) | Distância mediana (km) | (e) vínculos em 202608 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FAIXA 3 | 104 | 31,7% | 57,7% | 42,3% | 5,8% | 18,3% | 11,5% | 6,7% | 198 | 0 | 5,19 |
| 1 | FAIXA 2 | 261 | 32,6% | 51,7% | 48,3% | 9,2% | 26,8% | 10,0% | 2,3% | 114 | 0 | 5,57 |
| 1 | FAIXA 1 | 134 | 9,0% | 14,2% | 85,8% | 19,4% | 47,8% | 16,4% | 2,2% | 197 | 69 | 5,37 |
| 1 | todas | 499 | 26,1% | 42,9% | 57,1% | 11,2% | 30,7% | 12,0% | 3,2% | 153 | 30 | 5,44 |
| 2 | FAIXA 3 | 326 | 31,3% | 65,0% | 35,0% | 4,6% | 17,2% | 11,7% | 1,5% | 129 | 0 | 5,44 |
| 2 | FAIXA 2 | 412 | 31,6% | 62,4% | 37,6% | 8,5% | 18,0% | 8,7% | 2,4% | 118 | 0 | 5,69 |
| 2 | FAIXA 1 | 171 | 15,8% | 22,2% | 77,8% | 28,7% | 32,7% | 13,5% | 2,9% | 161 | 59 | 5,61 |
| 2 | todas | 909 | 28,5% | 55,8% | 44,2% | 10,9% | 20,5% | 10,7% | 2,2% | 130 | 0 | 5,58 |
| 1+2 | FAIXA 3 | 430 | 31,4% | 63,3% | 36,7% | 4,9% | 17,4% | 11,6% | 2,8% | 145 | 0 | 5,38 |
| 1+2 | FAIXA 2 | 673 | 31,9% | 58,2% | 41,8% | 8,8% | 21,4% | 9,2% | 2,4% | 116 | 0 | 5,64 |
| 1+2 | FAIXA 1 | 305 | 12,8% | 18,7% | 81,3% | 24,6% | 39,3% | 14,8% | 2,6% | 177 | 67 | 5,51 |
| 1+2 | todas | 1.408 | 27,6% | 51,2% | 48,8% | 11,0% | 24,1% | 11,2% | 2,6% | 138 | 0 | 5,53 |
<!-- X1:descritivo:fim -->

Sensibilidade à regra de ligação (todas as faixas):

<!-- X1:sensibilidade_regra:inicio -->
| Ciclo | Regra de ligação | Ligados | Novo no município | Outra UF | Sem vínculo médico | Distância mediana (km) |
|---|---|---|---|---|---|---|
| 1 | principal_d1 | 499 | 57,1% | 12,0% | 3,2% | 30 |
| 1 | literal_doc45 | 508 | 58,5% | 8,7% | 3,3% | 34 |
| 2 | principal_d1 | 909 | 44,2% | 10,7% | 2,2% | 0 |
| 2 | literal_doc45 | 924 | 45,3% | 8,9% | 2,4% | 0 |
| 1+2 | principal_d1 | 1.408 | 48,8% | 11,2% | 2,6% | 0 |
| 1+2 | literal_doc45 | 1.432 | 50,0% | 8,8% | 2,7% | 0 |
<!-- X1:sensibilidade_regra:fim -->

### X1.4 RDD nos cortes, condicional à alocação, com limites de Lee

Unidade: município de V_k (célula no quadro da 1ª chamada do ciclo k) com ao
menos um médico ativo ligado. Local linear, h = 0,050, kernel triangular, HC1
por corte; nos empilhados, CR1 por município. O outcome só existe onde há
médico ligado. Por isso cada corte e ciclo traz limites de Lee, com seleção =
ter médico ligado (o que junta preencher, estar ativo no retrato e ligar ao
CNES). As linhas empilhadas não têm Lee, porque a `rdd_lib` só faz Lee em um
corte. O contraste é o **pacote** do corte (RDD em nível), condicional à
seleção. Não é efeito da participação no PMM-E nem do Agora Tem Especialistas.

<!-- X1:rdd:inicio -->
| Outcome | Ciclo | Corte | Salto | IC 95% | p | q BKY (X1) | N abaixo / acima | Lee: limites | Lee: IC 95% conservador |
|---|---|---|---|---|---|---|---|---|---|
| novos no município | 1 | 0,300 | −0,047 | [−0,532; 0,438] | 0,850 | 1,000 | 22 / 31 | [−0,042; −0,035] | [−0,528; 0,451] |
| novos no município | 1 | 0,400 | 0,055 | [−0,373; 0,483] | 0,802 | 1,000 | 34 / 27 | [−0,113; 0,114] | [−0,511; 0,548] |
| novos no município | 1 | empilhado | 0,016 | [−0,305; 0,337] | 0,924 | 1,000 | 56 / 58 | não se aplica (empilhado) | não se aplica (empilhado) |
| novos no município | 2 | 0,300 | 0,260 | [−0,138; 0,657] | 0,201 | 1,000 | 43 / 39 | [0,184; 0,323] | [−0,232; 0,660] |
| novos no município | 2 | 0,400 | 0,049 | [−0,218; 0,315] | 0,720 | 1,000 | 35 / 45 | [0,051; 0,141] | [−0,221; 0,375] |
| novos no município | 2 | empilhado | 0,138 | [−0,092; 0,368] | 0,240 | 1,000 | 78 / 84 | não se aplica (empilhado) | não se aplica (empilhado) |
| novos no município | 1+2 | empilhado | 0,091 | [−0,110; 0,292] | 0,374 | 1,000 | 94 / 108 | não se aplica (empilhado) | não se aplica (empilhado) |
| outra UF | 1 | 0,300 | −0,199 | [−0,565; 0,167] | 0,287 | 1,000 | 22 / 31 | [−0,199; −0,160] | [−0,566; 0,202] |
| outra UF | 1 | 0,400 | −0,112 | [−0,323; 0,100] | 0,300 | 1,000 | 34 / 27 | [−0,143; 0,032] | [−0,375; 0,160] |
| outra UF | 1 | empilhado | −0,145 | [−0,336; 0,045] | 0,135 | 1,000 | 56 / 58 | não se aplica (empilhado) | não se aplica (empilhado) |
| outra UF | 2 | 0,300 | −0,013 | [−0,208; 0,181] | 0,893 | 1,000 | 43 / 39 | [−0,036; 0,020] | [−0,272; 0,150] |
| outra UF | 2 | 0,400 | 0,046 | [−0,166; 0,259] | 0,668 | 1,000 | 35 / 45 | [−0,097; 0,088] | [−0,208; 0,331] |
| outra UF | 2 | empilhado | 0,021 | [−0,127; 0,169] | 0,779 | 1,000 | 78 / 84 | não se aplica (empilhado) | não se aplica (empilhado) |
| outra UF | 1+2 | empilhado | −0,043 | [−0,160; 0,074] | 0,474 | 1,000 | 94 / 108 | não se aplica (empilhado) | não se aplica (empilhado) |
| distância média (km) | 1 | 0,300 | −143 | [−486; 199] | 0,412 | 1,000 | 21 / 31 | [−145; −135] | [−489; 206] |
| distância média (km) | 1 | 0,400 | −118 | [−463; 226] | 0,501 | 1,000 | 34 / 26 | [−176; 52] | [−593; 186] |
| distância média (km) | 1 | empilhado | −128 | [−376; 120] | 0,312 | 1,000 | 55 / 57 | não se aplica (empilhado) | não se aplica (empilhado) |
| distância média (km) | 2 | 0,300 | −7 | [−162; 148] | 0,929 | 1,000 | 43 / 38 | [−23; 2] | [−202; 75] |
| distância média (km) | 2 | 0,400 | −28 | [−146; 91] | 0,648 | 1,000 | 34 / 45 | [−63; −18] | [−167; 103] |
| distância média (km) | 2 | empilhado | −19 | [−113; 75] | 0,695 | 1,000 | 77 / 83 | não se aplica (empilhado) | não se aplica (empilhado) |
| distância média (km) | 1+2 | empilhado | −61 | [−172; 51] | 0,286 | 1,000 | 93 / 108 | não se aplica (empilhado) | não se aplica (empilhado) |
<!-- X1:rdd:fim -->

A seleção em si (fração dos municípios de V_k com médico ligado):

<!-- X1:selecao:inicio -->
| Ciclo | Corte | Salto na fração de municípios de V_k com médico ligado | IC 95% | p |
|---|---|---|---|---|
| 1 | 0,300 | 0,026 | [−0,415; 0,468] | 0,907 |
| 1 | 0,400 | −0,134 | [−0,545; 0,277] | 0,523 |
| 2 | 0,300 | −0,133 | [−0,496; 0,230] | 0,473 |
| 2 | 0,400 | 0,149 | [−0,109; 0,407] | 0,258 |
<!-- X1:selecao:fim -->

<!-- X1:bky:inicio -->
Linhas com p no X1: 32; com p < 0,05: 2; com q BKY < 0,05: 1; menor q: 0,001.
<!-- X1:bky:fim -->

### X1.5 Escolha com distância (sensibilidade do E9)

Os candidatos alocados na 1ª chamada dos ciclos 1 e 2 são ligados, pela célula
e pelo nome, a um médico ativo ligado ao CNES. O pseudônimo do candidato é
reconstruído em memória e confere com o arquivo da tarefa B. Para quem tem
vínculo médico antes do início, a distância da origem a cada célula do conjunto
entra no logit condicional da 1ª opção, junto com os atributos do E9 principal.
A primeira linha é o E9 principal na mesma amostra, sem a distância.

<!-- X1:e9:inicio -->
| Especificação | Termo | Coeficiente | IC 95% (cluster por conjunto) | p | Candidatos | Conjuntos |
|---|---|---|---|---|---|---|
| e9_principal_mesma_amostra | bolsa_mil | 0,087 | [0,029; 0,146] | 0,003 | 828 | 32 |
| e9_com_distancia | bolsa_mil | 0,033 | [−0,024; 0,090] | 0,250 | 828 | 32 |
| e9_com_distancia | distancia_100km | −0,867 | [−1,037; −0,696] | < 0,001 | 828 | 32 |

Amostra: ciclo 1: 216 pares candidato alocado–médico ligado; ciclo 2: 652 pares candidato alocado–médico ligado; 851 com vínculo pré-início; 828 no logit.
<!-- X1:e9:fim -->

**Limites.** A amostra é selecionada pelo resultado: são alocados, ativos,
ligados e com vínculo anterior. Para quem já trabalhava no município, a
distância à célula escolhida é zero por construção. Assim, o coeficiente da
distância mede sobretudo "escolher onde já se trabalha", e não uma elasticidade
da escolha à distância para todos os candidatos. A queda do coeficiente da bolsa
ao incluir a distância é uma associação nessa amostra; ela não decompõe o
efeito do E9.

### X1.6 Leitura

- **Proposta A (realocação e substituição):** o descritivo mostra que parte
  grande dos especialistas do PMM-E já tinha vínculo médico no município do
  posto, e parte no próprio estabelecimento, antes de começar. Para esses, o
  programa registra no CNES um vínculo de quem já estava lá, e não um médico
  novo. Isso é compatível com a leitura A da síntese, mas não a prova: vínculo
  prévio não diz se a carga horária ou a especialidade mudaram.
- **Gradiente por faixa:** a fração de recém-chegados e a distância percorrida
  diferem entre faixas. Esse gradiente é descritivo e se confunde com o IVS, o
  porte e a oferta prévia de especialistas.
- **Nos cortes:** a RDD condicional não distingue o salto de zero em nenhum
  outcome, nem antes nem depois do BKY. Os IC, inclusive os conservadores de
  Lee, são largos demais para descartar saltos de magnitude relevante. A
  seleção (ter médico ligado) também não salta de forma detectável.
- **Proposta B (distância):** na amostra de alocados, a escolha da 1ª opção
  está fortemente associada à proximidade da origem. Com a distância no
  modelo, o coeficiente da bolsa cai e deixa de se distinguir de zero. Pelos
  limites acima, isso é sugestivo, não identificado.

### X1.7 Limitações

- Vínculo no CNES não é presença nem trabalho efetivo; a falta de vínculo não
  prova que o médico não atuava.
- As competências pré-início são esparsas (seis meses). A última pode estar
  meses antes do início.
- O retrato de ativos exclui quem saiu antes de 11/09/2026; a lista de
  12/08/2026 recupera só parte.
- A ligação depende do registro no CNES. Médicos sem vínculo médico com o CRM
  da lista, ou sem nome compatível, ficam fora.
- Os limites de Lee supõem monotonicidade da seleção e usam as aproximações da
  `rdd_lib` (quantil no meio-janela, EP sem incerteza do aparo).
