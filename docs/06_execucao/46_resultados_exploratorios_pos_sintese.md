# Resultados exploratórios pós-síntese (X1–X6)

> **Protocolo:** [`45_protocolo_exploratorio_pos_sintese.md`](45_protocolo_exploratorio_pos_sintese.md),
> congelado em 19/10/2026 antes de abrir os outcomes.<br>
> **Estatuto:** exploratório e pós-resultado. Nada aqui muda o protocolo 40,
> os resultados E3–E9 nem o Holm das primárias. Toda saída leva
> `estatuto = EXPLORATORIO_POS_SINTESE`.<br>
> **Regra dos números:** cada seção é autocontida e seus números estão em
> blocos gerados pelo script da seção, entre marcadores, a partir de
> `output/rdd_bolsa/`.


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
> confere os blocos contra as saídas e a prosa fora deles.<br>
> **Revisão:** a versão desta seção revisada pela auditoria independente de X1
> (19/10/2026) relata a regra literal ao lado de D1, os meses fixos de
> referência e a distância do E9 independente da escolha.

### X1.1 O que foi feito

- **Lado PMM-E:** a relação nominal de ativos (retrato de 11/09/2026, a mesma do
  E3 e do E6) mais os registros da lista nominal de 12/08/2026 que não estão
  nela. O nome é lido só em memória.
- **Lado CNES:** as competências 202406, 202501, 202506, 202510, 202602 e
  202608, baixadas do servlet HTTPS do CNES. Os seis ZIPs têm o mesmo SHA-256 dos
  ZIPs do a09, e a extração reproduz exatamente a contagem de vínculos médicos do
  a09 em cada mês. As duas conferências são portões fail-closed. Os ZIPs foram
  apagados. O extrato com registro profissional e nome normalizado fica em
  `output/rdd_bolsa/X1_cache/`, fora do Git. Nenhum mês a partir de 202609 é
  lido.
- **Conselho:** só entram na busca os vínculos médicos cujo
  `CO_CONSELHO_CLASSE` é o do Conselho Regional de Medicina. O código vem da
  tabela `tbOrgaoEmissor` do próprio CNES. A `tbConselhoClasse` usa outra
  numeração.
- **Região de saúde:** a CIR do painel do PMMB do Ministério da Saúde, por
  município. Ela bate com a região impressa na lista de ativos em todos os
  municípios do PMM-E. O campo `CO_REGIAO_SAUDE` do CNES é texto livre e
  muitas vezes vazio, e não é usado.
- **Distância:** círculo máximo entre os centroides municipais da API de malhas
  v3 do IBGE. A resposta baixada é idêntica, byte a byte, à da malha municipal
  de 2022 (URL, data, SHA-256 e período no resumo).
- **Pseudônimo:** cada registro tem um `id_medico` determinístico. As saídas não
  trazem nome, CPF, CNS, CRM nem código de profissional do CNES. O pseudônimo é
  **fraco**: ciclo, município e faixa, cruzados com a lista nominal pública e
  com o CNES, podem reidentificar o médico. Por isso o parquet não traz mês de
  início nem curso, e não deve ser cruzado com dados nominais.

### X1.2 Duas regras de ligação: a literal (protocolo) e a correção D1

O doc 45 fixa a regra: CRM+UF exato; depois CRM exato com nome compatível;
ambíguos ficam fora. É a regra **literal**, a do protocolo congelado. As listas
do PMM-E, porém, trazem a UF do **posto**, e não a do CRM. Quando o médico tem
CRM de outra UF, o mesmo número pode pertencer a outra pessoa na UF do posto, e
a etapa 1 literal liga a pessoa errada. A conferência de nomes da etapa 1
encontrou ligações sem nenhum nome em comum e sem vínculo no estabelecimento do
posto.

- **D1 (correção pós-hoc):** na etapa 1, o candidato único só liga se o nome for
  compatível; sem isso, o registro segue para a etapa 2.
- **Quando e por quê:** D1 foi decidida depois da primeira execução completa,
  que gravou e exibiu as estimativas com a regra literal. O motivo é a
  qualidade da ligação. Mesmo assim, D1 leva as linhas mais próximas de
  significância em direção a zero. Por isso **todas** as saídas e tabelas
  abaixo trazem as duas regras lado a lado, e a literal vem primeiro.

<!-- X1:ligacao:inicio -->
| Regra | Ciclo | Registros | Ligados | Taxa | Etapa 1 (CRM+UF) | Etapa 2 (CRM+nome) | Ambíguos | Não achados |
|---|---|---|---|---|---|---|---|---|
| literal (protocolo, doc 45) | 1 | 525 | 508 | 96,8% | 468 | 40 | 0 | 17 |
| literal (protocolo, doc 45) | 2 | 968 | 924 | 95,5% | 843 | 81 | 1 | 43 |
| literal (protocolo, doc 45) | 3 | 497 | 469 | 94,4% | 404 | 65 | 0 | 28 |
| D1 (correção pós-hoc) | 1 | 525 | 499 | 95,0% | 428 | 71 | 0 | 26 |
| D1 (correção pós-hoc) | 2 | 968 | 909 | 93,9% | 802 | 107 | 1 | 58 |
| D1 (correção pós-hoc) | 3 | 497 | 468 | 94,2% | 379 | 89 | 0 | 29 |

Motivos, regra literal (protocolo, doc 45): ambiguo_crm_nome_com_mais_de_um_profissional: 1; crm_ausente_na_lista: 2; crm_sem_nome_compativel: 33; crm_sem_vinculo_medico_no_cnes: 53; ligado: 1.901.
Motivos, regra D1 (correção pós-hoc): ambiguo_crm_nome_com_mais_de_um_profissional: 1; crm_ausente_na_lista: 2; crm_sem_nome_compativel: 58; crm_sem_vinculo_medico_no_cnes: 53; ligado: 1.876.
Etapa 1 (CRM + UF do posto) com candidato único: 1.715; com nome compatível: 1.609 (93,8%). Sem nome compatível: 106; a literal os liga, D1 os manda para a etapa 2, onde 81 ligam.
Conferência (ligados com início antes de 202608 com vínculo médico no estabelecimento do posto em 202608): literal (protocolo, doc 45), 1_crm_uf: 76,0% de 1.310; literal (protocolo, doc 45), 2_crm_nome: 72,7% de 121; D1 (correção pós-hoc), 1_crm_uf: 80,6% de 1.229; D1 (correção pós-hoc), 2_crm_nome: 76,4% de 178.
Entre as regras: mesmo profissional em 1.795 registros; profissional diferente em 81; ligado só na literal: 25; só em D1: 0.
Conselho: só entram na busca vínculos com CO_CONSELHO_CLASSE = 71 (MEDICINA, CONSELHO REGIONAL, tbOrgaoEmissor de 202608); vínculos médicos com outro código, fora da busca, somadas as seis competências: 51.384 (0,49%).
<!-- X1:ligacao:fim -->

### X1.3 De onde vieram os especialistas (descritivo)

Médicos ligados dos ciclos 1 e 2, por faixa anunciada. A origem é a da última
competência lida antes do mês de início, pela ligação mais próxima. A distância
é a do município de origem mais próximo, e vale zero para quem já estava no
município. A coluna (e) conta vínculos médicos em 202608. Tudo aqui é
**descritivo**: a faixa acompanha o IVS e o porte do município, e a diferença
entre faixas não é efeito da bolsa.

Regra literal (protocolo):

<!-- X1:descritivo:inicio -->
| Ciclo | Faixa | Ligados | (a) mesmo estab. | (b) mesmo município | Novo no município | Mesma região | Mesma UF | Outra UF | Sem vínculo médico | Distância média (km) | Distância mediana (km) | (e) vínculos em 202608 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | FAIXA 3 | 105 | 31,4% | 57,1% | 42,9% | 5,7% | 19,0% | 11,4% | 6,7% | 200 | 0 | 5,16 |
| 1 | FAIXA 2 | 266 | 31,2% | 50,0% | 50,0% | 9,0% | 32,3% | 6,0% | 2,6% | 133 | 0 | 5,50 |
| 1 | FAIXA 1 | 137 | 8,0% | 13,1% | 86,9% | 17,5% | 55,5% | 11,7% | 2,2% | 201 | 85 | 4,97 |
| 1 | todas | 508 | 25,0% | 41,5% | 58,5% | 10,6% | 35,8% | 8,7% | 3,3% | 165 | 34 | 5,29 |
| 2 | FAIXA 3 | 333 | 31,2% | 64,6% | 35,4% | 4,5% | 18,0% | 11,4% | 1,5% | 129 | 0 | 5,38 |
| 2 | FAIXA 2 | 417 | 31,2% | 61,4% | 38,6% | 8,4% | 20,6% | 7,2% | 2,4% | 108 | 0 | 5,64 |
| 2 | FAIXA 1 | 174 | 13,2% | 19,5% | 80,5% | 29,3% | 39,1% | 8,0% | 4,0% | 169 | 65 | 5,49 |
| 2 | todas | 924 | 27,8% | 54,7% | 45,3% | 10,9% | 23,2% | 8,9% | 2,4% | 127 | 0 | 5,51 |
| 1+2 | FAIXA 3 | 438 | 31,3% | 62,8% | 37,2% | 4,8% | 18,3% | 11,4% | 2,7% | 145 | 0 | 5,32 |
| 1+2 | FAIXA 2 | 683 | 31,2% | 57,0% | 43,0% | 8,6% | 25,2% | 6,7% | 2,5% | 118 | 0 | 5,58 |
| 1+2 | FAIXA 1 | 311 | 10,9% | 16,7% | 83,3% | 24,1% | 46,3% | 9,6% | 3,2% | 183 | 69 | 5,26 |
| 1+2 | todas | 1.432 | 26,8% | 50,0% | 50,0% | 10,8% | 27,7% | 8,8% | 2,7% | 140 | 0 | 5,43 |
<!-- X1:descritivo:fim -->

Correção D1:

<!-- X1:descritivo_d1:inicio -->
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
<!-- X1:descritivo_d1:fim -->

**"Já estava no município" depende do mês de referência.** A última competência
antes do início varia entre os médicos e fica mais perto do início para quem
começou mais tarde. A tabela abaixo refaz a fração com vínculo no município do
posto em meses fixos, os mesmos para todos, e dá a faixa resultante. A
persistência é a fração dos incumbentes da última competência pré-início que já
tinham vínculo no município em 202406.

<!-- X1:mes_referencia:inicio -->
| Regra | Ciclo | Ligados | Última competência pré-início | 202406 | 202501 | 202506 | Faixa (mín.–máx.) | A última é o máximo? | Persistência: incumbentes já presentes em 202406 |
|---|---|---|---|---|---|---|---|---|---|
| literal (protocolo, doc 45) | 1 | 508 | 41,5% | 36,6% | 38,2% | 40,6% | 36,6%–41,5% | sim | 83,9% (177 de 211) |
| literal (protocolo, doc 45) | 2 | 924 | 54,7% | 47,5% | 49,4% | 52,2% | 47,5%–54,7% | sim | 83,2% (420 de 505) |
| literal (protocolo, doc 45) | 1+2 | 1.432 | 50,0% | 43,6% | 45,4% | 48,0% | 43,6%–50,0% | sim | 83,4% (597 de 716) |
| D1 (correção pós-hoc) | 1 | 499 | 42,9% | 37,7% | 39,5% | 41,9% | 37,7%–42,9% | sim | 83,6% (179 de 214) |
| D1 (correção pós-hoc) | 2 | 909 | 55,8% | 48,4% | 50,4% | 53,1% | 48,4%–55,8% | sim | 82,8% (420 de 507) |
| D1 (correção pós-hoc) | 1+2 | 1.408 | 51,2% | 44,6% | 46,5% | 49,1% | 44,6%–51,2% | sim | 83,1% (599 de 721) |
<!-- X1:mes_referencia:fim -->

### X1.4 RDD nos cortes, condicional à alocação, com limites de Lee

Unidade: município de V_k (célula no quadro da 1ª chamada do ciclo k) com ao
menos um médico ativo ligado. Local linear, h = 0,050, kernel triangular, HC1
por corte; nos empilhados, CR1 por município. O outcome só existe onde há
médico ligado. Por isso cada corte e ciclo traz limites de Lee, com seleção =
ter médico ligado (o que junta preencher, estar ativo no retrato e ligar ao
CNES). As linhas empilhadas não têm Lee, porque a `rdd_lib` só faz Lee em um
corte. O contraste é o **pacote** do corte (RDD em nível), condicional à
seleção. Não é efeito da participação no PMM-E nem do Agora Tem Especialistas.
Cada linha aparece nas duas regras de ligação; o q de BKY é calculado dentro de
cada regra.

<!-- X1:rdd:inicio -->
| Outcome | Ciclo | Corte | Regra | Salto | IC 95% | p | q BKY (X1, por regra) | N abaixo / acima | Lee: limites | Lee: IC 95% conservador |
|---|---|---|---|---|---|---|---|---|---|---|
| novos no município | 1 | 0,300 | literal (protocolo, doc 45) | 0,003 | [−0,477; 0,482] | 0,991 | 1,000 | 22 / 31 | [0,008; 0,013] | [−0,473; 0,494] |
| novos no município | 1 | 0,300 | D1 (correção pós-hoc) | −0,047 | [−0,532; 0,438] | 0,850 | 1,000 | 22 / 31 | [−0,042; −0,035] | [−0,528; 0,451] |
| novos no município | 1 | 0,400 | literal (protocolo, doc 45) | 0,024 | [−0,412; 0,461] | 0,913 | 1,000 | 34 / 27 | [−0,160; 0,079] | [−0,565; 0,526] |
| novos no município | 1 | 0,400 | D1 (correção pós-hoc) | 0,055 | [−0,373; 0,483] | 0,802 | 1,000 | 34 / 27 | [−0,113; 0,114] | [−0,511; 0,548] |
| novos no município | 1 | empilhado | literal (protocolo, doc 45) | 0,016 | [−0,308; 0,340] | 0,923 | 1,000 | 56 / 58 | não se aplica (empilhado) | não se aplica (empilhado) |
| novos no município | 1 | empilhado | D1 (correção pós-hoc) | 0,016 | [−0,305; 0,337] | 0,924 | 1,000 | 56 / 58 | não se aplica (empilhado) | não se aplica (empilhado) |
| novos no município | 2 | 0,300 | literal (protocolo, doc 45) | 0,352 | [−0,031; 0,735] | 0,072 | 1,000 | 43 / 39 | [0,276; 0,414] | [−0,126; 0,734] |
| novos no município | 2 | 0,300 | D1 (correção pós-hoc) | 0,260 | [−0,138; 0,657] | 0,201 | 1,000 | 43 / 39 | [0,184; 0,323] | [−0,232; 0,660] |
| novos no município | 2 | 0,400 | literal (protocolo, doc 45) | 0,095 | [−0,161; 0,351] | 0,468 | 1,000 | 36 / 46 | [0,109; 0,118] | [−0,151; 0,352] |
| novos no município | 2 | 0,400 | D1 (correção pós-hoc) | 0,049 | [−0,218; 0,315] | 0,720 | 1,000 | 35 / 45 | [0,051; 0,141] | [−0,221; 0,375] |
| novos no município | 2 | empilhado | literal (protocolo, doc 45) | 0,203 | [−0,019; 0,426] | 0,074 | 1,000 | 79 / 85 | não se aplica (empilhado) | não se aplica (empilhado) |
| novos no município | 2 | empilhado | D1 (correção pós-hoc) | 0,138 | [−0,092; 0,368] | 0,240 | 1,000 | 78 / 84 | não se aplica (empilhado) | não se aplica (empilhado) |
| novos no município | 1+2 | empilhado | literal (protocolo, doc 45) | 0,131 | [−0,062; 0,325] | 0,182 | 1,000 | 94 / 109 | não se aplica (empilhado) | não se aplica (empilhado) |
| novos no município | 1+2 | empilhado | D1 (correção pós-hoc) | 0,091 | [−0,110; 0,292] | 0,374 | 1,000 | 94 / 108 | não se aplica (empilhado) | não se aplica (empilhado) |
| outra UF | 1 | 0,300 | literal (protocolo, doc 45) | −0,197 | [−0,556; 0,162] | 0,283 | 1,000 | 22 / 31 | [−0,197; −0,182] | [−0,557; 0,178] |
| outra UF | 1 | 0,300 | D1 (correção pós-hoc) | −0,199 | [−0,565; 0,167] | 0,287 | 1,000 | 22 / 31 | [−0,199; −0,160] | [−0,566; 0,202] |
| outra UF | 1 | 0,400 | literal (protocolo, doc 45) | −0,088 | [−0,251; 0,075] | 0,291 | 1,000 | 34 / 27 | [−0,110; 0,035] | [−0,288; 0,140] |
| outra UF | 1 | 0,400 | D1 (correção pós-hoc) | −0,112 | [−0,323; 0,100] | 0,300 | 1,000 | 34 / 27 | [−0,143; 0,032] | [−0,375; 0,160] |
| outra UF | 1 | empilhado | literal (protocolo, doc 45) | −0,130 | [−0,301; 0,041] | 0,135 | 1,000 | 56 / 58 | não se aplica (empilhado) | não se aplica (empilhado) |
| outra UF | 1 | empilhado | D1 (correção pós-hoc) | −0,145 | [−0,336; 0,045] | 0,135 | 1,000 | 56 / 58 | não se aplica (empilhado) | não se aplica (empilhado) |
| outra UF | 2 | 0,300 | literal (protocolo, doc 45) | −0,012 | [−0,206; 0,183] | 0,906 | 1,000 | 43 / 39 | [−0,034; 0,021] | [−0,271; 0,152] |
| outra UF | 2 | 0,300 | D1 (correção pós-hoc) | −0,013 | [−0,208; 0,181] | 0,893 | 1,000 | 43 / 39 | [−0,036; 0,020] | [−0,272; 0,150] |
| outra UF | 2 | 0,400 | literal (protocolo, doc 45) | 0,038 | [−0,066; 0,142] | 0,478 | 1,000 | 36 / 46 | [−0,041; 0,058] | [−0,088; 0,177] |
| outra UF | 2 | 0,400 | D1 (correção pós-hoc) | 0,046 | [−0,166; 0,259] | 0,668 | 1,000 | 35 / 45 | [−0,097; 0,088] | [−0,208; 0,331] |
| outra UF | 2 | empilhado | literal (protocolo, doc 45) | 0,017 | [−0,086; 0,119] | 0,748 | 1,000 | 79 / 85 | não se aplica (empilhado) | não se aplica (empilhado) |
| outra UF | 2 | empilhado | D1 (correção pós-hoc) | 0,021 | [−0,127; 0,169] | 0,779 | 1,000 | 78 / 84 | não se aplica (empilhado) | não se aplica (empilhado) |
| outra UF | 1+2 | empilhado | literal (protocolo, doc 45) | −0,040 | [−0,133; 0,054] | 0,405 | 1,000 | 94 / 109 | não se aplica (empilhado) | não se aplica (empilhado) |
| outra UF | 1+2 | empilhado | D1 (correção pós-hoc) | −0,043 | [−0,160; 0,074] | 0,474 | 1,000 | 94 / 108 | não se aplica (empilhado) | não se aplica (empilhado) |
| distância média (km) | 1 | 0,300 | literal (protocolo, doc 45) | −128 | [−472; 217] | 0,467 | 1,000 | 21 / 31 | [−130; −110] | [−475; 233] |
| distância média (km) | 1 | 0,300 | D1 (correção pós-hoc) | −143 | [−486; 199] | 0,412 | 1,000 | 21 / 31 | [−145; −135] | [−489; 206] |
| distância média (km) | 1 | 0,400 | literal (protocolo, doc 45) | −203 | [−558; 153] | 0,263 | 1,000 | 34 / 26 | [−286; 38] | [−705; 176] |
| distância média (km) | 1 | 0,400 | D1 (correção pós-hoc) | −118 | [−463; 226] | 0,501 | 1,000 | 34 / 26 | [−176; 52] | [−593; 186] |
| distância média (km) | 1 | empilhado | literal (protocolo, doc 45) | −174 | [−430; 82] | 0,183 | 1,000 | 55 / 57 | não se aplica (empilhado) | não se aplica (empilhado) |
| distância média (km) | 1 | empilhado | D1 (correção pós-hoc) | −128 | [−376; 120] | 0,312 | 1,000 | 55 / 57 | não se aplica (empilhado) | não se aplica (empilhado) |
| distância média (km) | 2 | 0,300 | literal (protocolo, doc 45) | 8 | [−147; 164] | 0,917 | 1,000 | 43 / 38 | [−7; 17] | [−186; 90] |
| distância média (km) | 2 | 0,300 | D1 (correção pós-hoc) | −7 | [−162; 148] | 0,929 | 1,000 | 43 / 38 | [−23; 2] | [−202; 75] |
| distância média (km) | 2 | 0,400 | literal (protocolo, doc 45) | 11 | [−61; 82] | 0,773 | 1,000 | 36 / 46 | [−16; 20] | [−66; 95] |
| distância média (km) | 2 | 0,400 | D1 (correção pós-hoc) | −28 | [−146; 91] | 0,648 | 1,000 | 34 / 45 | [−63; −18] | [−167; 103] |
| distância média (km) | 2 | empilhado | literal (protocolo, doc 45) | 10 | [−68; 87] | 0,808 | 1,000 | 79 / 84 | não se aplica (empilhado) | não se aplica (empilhado) |
| distância média (km) | 2 | empilhado | D1 (correção pós-hoc) | −19 | [−113; 75] | 0,695 | 1,000 | 77 / 83 | não se aplica (empilhado) | não se aplica (empilhado) |
| distância média (km) | 1+2 | empilhado | literal (protocolo, doc 45) | −61 | [−172; 50] | 0,284 | 1,000 | 93 / 109 | não se aplica (empilhado) | não se aplica (empilhado) |
| distância média (km) | 1+2 | empilhado | D1 (correção pós-hoc) | −61 | [−172; 51] | 0,286 | 1,000 | 93 / 108 | não se aplica (empilhado) | não se aplica (empilhado) |
<!-- X1:rdd:fim -->

A seleção em si (fração dos municípios de V_k com médico ligado):

<!-- X1:selecao:inicio -->
| Regra | Ciclo | Corte | Salto na fração de municípios de V_k com médico ligado | IC 95% | p |
|---|---|---|---|---|---|
| literal (protocolo, doc 45) | 1 | 0,300 | 0,026 | [−0,415; 0,468] | 0,907 |
| literal (protocolo, doc 45) | 1 | 0,400 | −0,134 | [−0,545; 0,277] | 0,523 |
| literal (protocolo, doc 45) | 2 | 0,300 | −0,133 | [−0,496; 0,230] | 0,473 |
| literal (protocolo, doc 45) | 2 | 0,400 | 0,138 | [−0,120; 0,395] | 0,295 |
| D1 (correção pós-hoc) | 1 | 0,300 | 0,026 | [−0,415; 0,468] | 0,907 |
| D1 (correção pós-hoc) | 1 | 0,400 | −0,134 | [−0,545; 0,277] | 0,523 |
| D1 (correção pós-hoc) | 2 | 0,300 | −0,133 | [−0,496; 0,230] | 0,473 |
| D1 (correção pós-hoc) | 2 | 0,400 | 0,149 | [−0,109; 0,407] | 0,258 |
<!-- X1:selecao:fim -->

<!-- X1:bky:inicio -->
Regra literal (protocolo, doc 45): linhas com p: 32; com p < 0,05: 2; com q BKY < 0,05: 2; menor q: 0,001.
Regra D1 (correção pós-hoc): linhas com p: 32; com p < 0,05: 2; com q BKY < 0,05: 1; menor q: 0,001.
<!-- X1:bky:fim -->

### X1.5 Escolha com distância (sensibilidade do E9)

Os candidatos alocados na 1ª chamada dos ciclos 1 e 2 são ligados, pela célula
e pelo nome, a um médico ativo ligado ao CNES. O pseudônimo do candidato é
reconstruído em memória e confere com o arquivo da tarefa B. A distância de cada
célula do conjunto é a do município de origem mais próximo **daquela célula**:
o mínimo sobre todos os municípios em que o médico tinha vínculo médico na
última competência pré-início. Ela não depende da célula escolhida. A versão
anterior usava a origem mais próxima do posto final, o que embutia a escolha na
distância, e foi retirada. A primeira linha de cada regra é o E9 principal na
mesma amostra, sem a distância.

<!-- X1:e9:inicio -->
| Regra | Especificação | Termo | Coeficiente | IC 95% (cluster por conjunto) | p | q BKY | Candidatos | Conjuntos |
|---|---|---|---|---|---|---|---|---|
| literal (protocolo, doc 45) | e9_principal_mesma_amostra | bolsa_mil | 0,089 | [0,033; 0,145] | 0,002 | 0,030 | 831 | 32 |
| literal (protocolo, doc 45) | e9_com_distancia | bolsa_mil | 0,044 | [−0,007; 0,094] | 0,091 | 1,000 | 831 | 32 |
| literal (protocolo, doc 45) | e9_com_distancia | distancia_100km | −0,821 | [−0,990; −0,653] | < 0,001 | 0,001 | 831 | 32 |
| D1 (correção pós-hoc) | e9_principal_mesma_amostra | bolsa_mil | 0,087 | [0,029; 0,146] | 0,003 | 0,057 | 828 | 32 |
| D1 (correção pós-hoc) | e9_com_distancia | bolsa_mil | 0,043 | [−0,009; 0,096] | 0,105 | 1,000 | 828 | 32 |
| D1 (correção pós-hoc) | e9_com_distancia | distancia_100km | −0,811 | [−0,967; −0,654] | < 0,001 | 0,001 | 828 | 32 |

Amostra, regra literal (protocolo, doc 45): pares candidato alocado–médico ligado: 875; sem vínculo médico na última competência pré-início: 21; sem linha de 1ª opção: 23; 1ª opção fora do conjunto: 0; sem coordenada: 0; no logit: 831, dos quais 425 com distância zero à célula escolhida.
Amostra, regra D1 (correção pós-hoc): pares candidato alocado–médico ligado: 868; sem vínculo médico na última competência pré-início: 17; sem linha de 1ª opção: 23; 1ª opção fora do conjunto: 0; sem coordenada: 0; no logit: 828, dos quais 431 com distância zero à célula escolhida.
<!-- X1:e9:fim -->

**Limites.** A amostra é selecionada pelo resultado: são alocados, ativos,
ligados e com vínculo anterior. Boa parte dela escolheu uma célula no município
em que já trabalhava (contagem no bloco acima). O coeficiente da distância
mede, portanto, sobretudo a escolha de ficar onde já se trabalha, e não uma
elasticidade da escolha à distância para todos os candidatos. A queda do
coeficiente da bolsa ao incluir a distância é uma associação nessa amostra; ela
não decompõe o efeito do E9.

### X1.6 Leitura

- **Proposta A (realocação e substituição):** uma parte grande dos
  especialistas do PMM-E já tinha vínculo médico no município do posto antes de
  começar, e uma parte, no próprio estabelecimento. Isso vale nas duas regras de
  ligação e em todos os meses de referência. O valor da última competência
  pré-início é o topo da faixa dos meses de referência; com 202406 como
  referência comum, a fração é menor (tabela de X1.3). A maior parte dos
  incumbentes já estava no município em 202406, bem antes do programa. Para
  esses médicos, o programa registra no CNES quem já estava lá, e não um médico
  novo. Isso é compatível com a leitura A da síntese, mas não a prova: vínculo
  prévio não diz se a carga horária ou a especialidade mudaram.
- **Gradiente por faixa:** a fração de recém-chegados e a distância percorrida
  diferem entre faixas. Esse gradiente é descritivo e se confunde com o IVS, o
  porte e a oferta prévia de especialistas.
- **Nos cortes:** a RDD condicional não distingue o salto de zero em nenhum
  outcome, em nenhuma das duas regras, nem antes nem depois do BKY. As linhas
  mais próximas de significância estão na regra literal e encolhem com D1. Os
  IC, inclusive os conservadores de Lee, são largos demais para descartar
  saltos de magnitude relevante. A seleção (ter médico ligado) também não salta
  de forma detectável.
- **Proposta B (distância):** na amostra de alocados ligados, a distância
  independente da escolha continua associada negativamente à escolha da 1ª
  opção, e, com ela no modelo, o coeficiente da bolsa cai e deixa de se
  distinguir de zero. Pelos limites de X1.5, a associação reflete em boa parte
  médicos que escolheram o município onde já trabalhavam. É sugestiva, não
  identificada, e não mede a sensibilidade à distância do candidato típico.

### X1.7 Limitações

- Vínculo no CNES não é presença nem trabalho efetivo; a falta de vínculo não
  prova que o médico não atuava.
- As competências pré-início são esparsas (seis meses). A última pode estar
  meses antes do início, e a distância até o início varia entre médicos; daí a
  tabela de meses fixos.
- O retrato de ativos exclui quem saiu antes de 11/09/2026; a lista de
  12/08/2026 recupera só parte.
- A ligação depende do registro no CNES. Médicos sem vínculo médico com o CRM
  da lista, ou sem nome compatível na etapa 2, ficam fora.
- Os limites de Lee supõem monotonicidade da seleção e usam as aproximações da
  `rdd_lib` (quantil no meio-janela, EP sem incerteza do aparo).

## X2

> **Script:** `scripts/rdd_bolsa/18_permanencia_ativos.py`.<br>
> **Saídas:** `output/rdd_bolsa/X2_*` (`natureza_dos_dados = EMPIRICO`;
> fontes, SHA-256, regras de ligação e conferências em `X2_resumo.json`).<br>
> **Testes:** `tests/test_x2_x3_permanencia.py`.<br>
> **Pergunta (doc 45, §3):** quem foi alocado na 1ª chamada dos ciclos 1 e 2
> continua ativo? A saída é maior do lado de bolsa menor?

### Construção

- **Alocados.**
  - Ciclo 1: local confirmado na alocação retificada sub judice e
    homologados da 1ª chamada. A célula final é a da homologação, se houver;
    senão, a da confirmação.
  - Ciclo 2: situação "ALOCADO" na aba Classificados de
    `resultado-final-pmme-2o-ciclo-25-05.xlsx`.
  - As contagens por célula reproduzem as colunas da tarefa B (doc 41a), e o
    script para se não reproduzirem.
- **Ligação.**
  - Os arquivos de resultado não têm CRM (o script confere o cabeçalho). Por
    isso a ligação usa nome normalizado + curso + município, e o município vem
    do quadro pela célula.
  - Chave exata e única dos dois lados: LIGADO. Chave repetida, ou o mesmo
    ativo ligado a dois alocados: AMBÍGUO.
  - Sem chave exata, mas com um ativo não ligado no mesmo curso e município e
    nome próximo: INCERTO. Nome próximo é similaridade ≥ 0,85 ou o mesmo
    primeiro nome com ao menos duas partes do nome em comum. Ele só
    reclassifica alocados de "sem correspondente" para INCERTO.
  - **Ordem de execução (divulgação).** A primeira execução usou a regra
    estreita, com INCERTO só por similaridade. Ela imprimiu as taxas de
    ligação, os motivos e a tabela de permanência por ciclo e faixa. Só depois
    de ver essa tabela entrou o critério das partes (regra ampla), após um
    diagnóstico de quase-correspondências. Nenhuma estimativa RDD tinha sido
    aberta. As duas regras estão nas saídas (coluna `regra_ligacao`). A ampla
    é a principal e a única no BKY. A estreita aparece ao lado, na seção
    "Regra estreita".
  - O resto é NÃO LIGADO, com o motivo.
  - AMBÍGUO e INCERTO ficam fora do outcome.
  - O CRM entra entre os dois retratos de ativos: a relação nominal de
    09/10/2026 (`dt_referencia` 11/09/2026) e `data/pmm_especialistas_nominal.csv`
    (12/08/2026).
- **Outcomes.**
  - X2.1 e X2.2: fração dos alocados determinados ainda ativos no município
    de alocação, por célula e por município. São condicionais a preencher e
    recebem limites de Lee, com seleção = ter alocado determinado.
  - X2.3: célula com alocado ainda ativo. X2.4: alocados ainda ativos por
    célula oferecida. Os dois são incondicionais e são **adições ao
    protocolo**: o §3 do doc 45 não os lista.
- **Estimação.**
  - Local linear sharp no IVS 2010 oficial (a08), cortes 0,300 e 0,400,
    h = 0,050, kernel triangular. Células com CR1 por município; municípios
    com HC1.
  - Também, como **adições ao protocolo** (o §3 do X2 não as lista; o §2 só
    cita cortes empilhados de forma genérica): cortes empilhados, ciclos
    empilhados (interceptos por ciclo) e tudo empilhado.
  - Ciclos empilhados misturam horizontes de seguimento diferentes. O ciclo 1
    começou bem antes do ciclo 2 (horizontes medianos no bloco "Leitura").
  - Lee só por ciclo e corte (a biblioteca não tem Lee empilhado).
  - Colunas `no_protocolo_45`, `rotulo` e `condicionamento` em
    `X2_estimativas.csv`. `q_bky` cobre todas as linhas X2 com p da regra
    ampla. `q_bky_so_protocolo` cobre só as do §3.

**O que o outcome mede.** Mede presença, no retrato, no município de
alocação. Não observa a data de saída, nem a diferença entre não começar e
sair depois de começar. No ciclo 1 isso pesa: quem só teve o local
confirmado e não foi homologado quase nunca aparece entre os ativos (linha
"confirmacao" da tabela abaixo). Por isso, no ciclo 1, X2 mistura não adesão
com saída. Em nível, a RDD mede o pacote do corte (auditoria 18), não a
participação no PMM-E.

### Ligação e motivos

<!-- X2:ligacao:inicio -->
| Ciclo | Retrato | Status | Motivo | Alocados |
|---|---|---|---|---:|
| 1 | 12/08/2026 | AMBIGUO | chave nome+curso+municipio repetida entre alocados | 3 |
| 1 | 12/08/2026 | INCERTO | grafia proxima (similaridade >= 0.85 ou mesmo 1o nome e 2 partes em comum) no mesmo curso e municipio | 15 |
| 1 | 12/08/2026 | LIGADO | nome+curso+municipio exato e unico | 249 |
| 1 | 12/08/2026 | NAO_LIGADO | nome ativo em outro curso | 15 |
| 1 | 12/08/2026 | NAO_LIGADO | nome e curso ativos em outro municipio | 27 |
| 1 | 12/08/2026 | NAO_LIGADO | sem correspondente na lista de ativos | 185 |
| 1 | 11/09/2026 | AMBIGUO | chave nome+curso+municipio repetida entre alocados | 3 |
| 1 | 11/09/2026 | INCERTO | grafia proxima (similaridade >= 0.85 ou mesmo 1o nome e 2 partes em comum) no mesmo curso e municipio | 15 |
| 1 | 11/09/2026 | LIGADO | nome+curso+municipio exato e unico | 249 |
| 1 | 11/09/2026 | NAO_LIGADO | nome ativo em outro curso | 19 |
| 1 | 11/09/2026 | NAO_LIGADO | nome e curso ativos em outro municipio | 36 |
| 1 | 11/09/2026 | NAO_LIGADO | sem correspondente na lista de ativos | 172 |
| 2 | 12/08/2026 | AMBIGUO | chave nome+curso+municipio repetida entre alocados | 3 |
| 2 | 12/08/2026 | INCERTO | grafia proxima (similaridade >= 0.85 ou mesmo 1o nome e 2 partes em comum) no mesmo curso e municipio | 42 |
| 2 | 12/08/2026 | LIGADO | nome+curso+municipio exato e unico | 680 |
| 2 | 12/08/2026 | NAO_LIGADO | nome e curso ativos em outro municipio | 22 |
| 2 | 12/08/2026 | NAO_LIGADO | sem correspondente na lista de ativos | 310 |
| 2 | 11/09/2026 | AMBIGUO | chave nome+curso+municipio repetida entre alocados | 3 |
| 2 | 11/09/2026 | INCERTO | grafia proxima (similaridade >= 0.85 ou mesmo 1o nome e 2 partes em comum) no mesmo curso e municipio | 42 |
| 2 | 11/09/2026 | LIGADO | nome+curso+municipio exato e unico | 667 |
| 2 | 11/09/2026 | NAO_LIGADO | nome e curso ativos em outro municipio | 29 |
| 2 | 11/09/2026 | NAO_LIGADO | sem correspondente na lista de ativos | 316 |
<!-- X2:ligacao:fim -->

CRM entre os dois retratos (a lista não traz a UF do CRM, então a presença
do CRM é indício, não prova):

<!-- X2:crm:inicio -->
| Medida | Pessoas |
|---|---:|
| ligados nos dois retratos | 911 |
| ligados nos dois com mesmo crm | 911 |
| ligados em ago e nao ligados em set | 18 |
| desses crm presente no retrato de set | 2 |
| desses crm ausente do retrato de set | 16 |
<!-- X2:crm:fim -->

### Permanência por ciclo e faixa (descritivo)

A faixa vem da regra sharp no IVS a08. "Incertos como ativos" e "incertos como
saídos" dão os dois extremos para os INCERTOS. "Presença no programa" também
conta como presente quem tem nome e curso ativos em outro município ou nome
ativo em outro curso.

<!-- X2:descritivo:inicio -->
| Ciclo | Subgrupo | Faixa | Alocados | Ligados | Não ligados | Ambíguos | Incertos | Ligação | Permanência (11/09) | Incertos como ativos | Incertos como saídos | Permanência (12/08) | Presença no programa |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | confirmacao | FAIXA 1 | 33 | 1 | 31 | 1 | 0 | 3,0% | 3,1% | 3,1% | 3,1% | 3,1% | 15,6% |
| 1 | confirmacao | FAIXA 2 | 66 | 0 | 66 | 0 | 0 | 0,0% | 0,0% | 0,0% | 0,0% | 0,0% | 24,2% |
| 1 | confirmacao | FAIXA 3 | 79 | 0 | 77 | 2 | 0 | 0,0% | 0,0% | 0,0% | 0,0% | 0,0% | 18,2% |
| 1 | confirmacao | TOTAL | 178 | 1 | 174 | 3 | 0 | 0,6% | 0,6% | 0,6% | 0,6% | 0,6% | 20,0% |
| 1 | homologacao | FAIXA 1 | 88 | 78 | 5 | 0 | 5 | 88,6% | 94,0% | 94,3% | 88,6% | 94,0% | 96,4% |
| 1 | homologacao | FAIXA 2 | 138 | 109 | 22 | 0 | 7 | 79,0% | 83,2% | 84,1% | 79,0% | 84,0% | 90,1% |
| 1 | homologacao | FAIXA 3 | 90 | 61 | 26 | 0 | 3 | 67,8% | 70,1% | 71,1% | 67,8% | 69,0% | 81,6% |
| 1 | homologacao | TOTAL | 316 | 248 | 53 | 0 | 15 | 78,5% | 82,4% | 83,2% | 78,5% | 82,4% | 89,4% |
| 1 | todos | FAIXA 1 | 121 | 79 | 36 | 1 | 5 | 65,3% | 68,7% | 70,0% | 65,8% | 68,7% | 73,9% |
| 1 | todos | FAIXA 2 | 204 | 109 | 88 | 0 | 7 | 53,4% | 55,3% | 56,9% | 53,4% | 55,8% | 68,0% |
| 1 | todos | FAIXA 3 | 169 | 61 | 103 | 2 | 3 | 36,1% | 37,2% | 38,3% | 36,5% | 36,6% | 51,8% |
| 1 | todos | TOTAL | 494 | 249 | 227 | 3 | 15 | 50,4% | 52,3% | 53,8% | 50,7% | 52,3% | 63,9% |
| 2 | todos | FAIXA 1 | 178 | 128 | 43 | 1 | 6 | 71,9% | 74,9% | 75,7% | 72,3% | 75,4% | 79,5% |
| 2 | todos | FAIXA 2 | 425 | 297 | 111 | 0 | 17 | 69,9% | 72,8% | 73,9% | 69,9% | 75,0% | 75,2% |
| 2 | todos | FAIXA 3 | 454 | 242 | 191 | 2 | 19 | 53,3% | 55,9% | 57,7% | 53,5% | 56,6% | 58,4% |
| 2 | todos | TOTAL | 1057 | 667 | 345 | 3 | 42 | 63,1% | 65,9% | 67,3% | 63,3% | 67,2% | 68,8% |
<!-- X2:descritivo:fim -->

### RDD e limites de Lee

Nas linhas `limites_lee`, τ é o local linear ingênuo nos selecionados. O
efeito só é limitado pelo par Lee [inf; sup], e o IC de Lee é conservador.

<!-- X2:estimativas:inicio -->
| Outcome | Ciclo | Corte | Especificação | Protocolo | τ | IC 95% | p | q BKY | q BKY só protocolo | Lee [inf; sup] | IC 95% Lee | n abaixo/acima |
|---|---|---|---|---|---:|---|---:|---:|---:|---|---|---|
| X2.1 | 1 | 0.300 | principal | sim | 0,130 | [−0,302; 0,562] | 0,555 | 1,000 | 1,000 | — | — | 31/35 |
| X2.1 | 1 | 0.300 | limites_lee | sim | 0,130 | — | — | — | — | [0,035; 0,339] | [−0,465; 0,777] | 31/35 |
| X2.1 | 1 | 0.400 | principal | sim | −0,055 | [−0,356; 0,246] | 0,719 | 1,000 | 1,000 | — | — | 41/25 |
| X2.1 | 1 | 0.400 | limites_lee | sim | −0,055 | — | — | — | — | [−0,063; −0,032] | [−0,364; 0,264] | 41/25 |
| X2.1 | 1 | empilhado | cortes_empilhados | adição | 0,037 | [−0,232; 0,306] | 0,789 | 1,000 | — | — | — | 72/60 |
| X2.1 | 2 | 0.300 | principal | sim | −0,021 | [−0,256; 0,213] | 0,858 | 1,000 | 1,000 | — | — | 53/45 |
| X2.1 | 2 | 0.300 | limites_lee | sim | −0,021 | — | — | — | — | [−0,399; 0,312] | [−0,609; 0,603] | 53/45 |
| X2.1 | 2 | 0.400 | principal | sim | −0,093 | [−0,305; 0,118] | 0,388 | 1,000 | 1,000 | — | — | 42/45 |
| X2.1 | 2 | 0.400 | limites_lee | sim | −0,093 | — | — | — | — | [−0,140; 0,034] | [−0,392; 0,192] | 42/45 |
| X2.1 | 2 | empilhado | cortes_empilhados | adição | −0,057 | [−0,218; 0,103] | 0,485 | 1,000 | — | — | — | 95/90 |
| X2.1 | 1+2 | 0.300 | ciclos_empilhados | adição | 0,031 | [−0,209; 0,270] | 0,802 | 1,000 | — | — | — | 64/58 |
| X2.1 | 1+2 | 0.400 | ciclos_empilhados | adição | −0,080 | [−0,241; 0,081] | 0,329 | 1,000 | — | — | — | 59/57 |
| X2.1 | 1+2 | empilhado | ciclos_e_cortes_empilhados | adição | −0,025 | [−0,173; 0,123] | 0,743 | 1,000 | — | — | — | 123/115 |
| X2.2 | 1 | 0.300 | principal | sim | 0,035 | [−0,456; 0,525] | 0,890 | 1,000 | 1,000 | — | — | 31/35 |
| X2.2 | 1 | 0.300 | limites_lee | sim | 0,035 | — | — | — | — | [0,039; 0,041] | [−0,452; 0,531] | 31/35 |
| X2.2 | 1 | 0.400 | principal | sim | 0,062 | [−0,322; 0,445] | 0,753 | 1,000 | 1,000 | — | — | 41/25 |
| X2.2 | 1 | 0.400 | limites_lee | sim | 0,062 | — | — | — | — | [−0,292; 0,295] | [−0,614; 0,664] | 41/25 |
| X2.2 | 1 | empilhado | cortes_empilhados | adição | 0,050 | [−0,253; 0,353] | 0,746 | 1,000 | — | — | — | 72/60 |
| X2.2 | 2 | 0.300 | principal | sim | −0,078 | [−0,425; 0,269] | 0,661 | 1,000 | 1,000 | — | — | 53/45 |
| X2.2 | 2 | 0.300 | limites_lee | sim | −0,078 | — | — | — | — | [−0,288; 0,028] | [−0,601; 0,364] | 53/45 |
| X2.2 | 2 | 0.400 | principal | sim | −0,109 | [−0,335; 0,116] | 0,341 | 1,000 | 1,000 | — | — | 42/45 |
| X2.2 | 2 | 0.400 | limites_lee | sim | −0,109 | — | — | — | — | [−0,140; 0,020] | [−0,388; 0,192] | 42/45 |
| X2.2 | 2 | empilhado | cortes_empilhados | adição | −0,094 | [−0,298; 0,109] | 0,364 | 1,000 | — | — | — | 95/90 |
| X2.2 | 1+2 | 0.300 | ciclos_empilhados | adição | −0,039 | [−0,344; 0,266] | 0,802 | 1,000 | — | — | — | 64/58 |
| X2.2 | 1+2 | 0.400 | ciclos_empilhados | adição | −0,042 | [−0,229; 0,144] | 0,656 | 1,000 | — | — | — | 59/57 |
| X2.2 | 1+2 | empilhado | ciclos_e_cortes_empilhados | adição | −0,041 | [−0,214; 0,132] | 0,643 | 1,000 | — | — | — | 123/115 |
| X2.3 | 1 | 0.300 | principal | adição | 0,003 | [−0,200; 0,205] | 0,978 | 1,000 | — | — | — | 61/53 |
| X2.3 | 1 | 0.400 | principal | adição | −0,037 | [−0,245; 0,171] | 0,725 | 1,000 | — | — | — | 53/41 |
| X2.3 | 1 | empilhado | cortes_empilhados | adição | −0,016 | [−0,162; 0,130] | 0,832 | 1,000 | — | — | — | 114/94 |
| X2.3 | 2 | 0.300 | principal | adição | −0,175 | [−0,361; 0,011] | 0,066 | 1,000 | — | — | — | 82/61 |
| X2.3 | 2 | 0.400 | principal | adição | 0,007 | [−0,243; 0,258] | 0,954 | 1,000 | — | — | — | 52/53 |
| X2.3 | 2 | empilhado | cortes_empilhados | adição | −0,099 | [−0,248; 0,051] | 0,197 | 1,000 | — | — | — | 134/114 |
| X2.3 | 1+2 | 0.300 | ciclos_empilhados | adição | −0,100 | [−0,246; 0,046] | 0,180 | 1,000 | — | — | — | 100/80 |
| X2.3 | 1+2 | 0.400 | ciclos_empilhados | adição | −0,014 | [−0,186; 0,159] | 0,878 | 1,000 | — | — | — | 69/71 |
| X2.3 | 1+2 | empilhado | ciclos_e_cortes_empilhados | adição | −0,062 | [−0,173; 0,049] | 0,271 | 1,000 | — | — | — | 169/151 |
| X2.4 | 1 | 0.300 | principal | adição | −0,007 | [−0,286; 0,271] | 0,959 | 1,000 | — | — | — | 59/53 |
| X2.4 | 1 | 0.400 | principal | adição | −0,011 | [−0,325; 0,303] | 0,945 | 1,000 | — | — | — | 47/38 |
| X2.4 | 1 | empilhado | cortes_empilhados | adição | −0,009 | [−0,221; 0,202] | 0,931 | 1,000 | — | — | — | 106/91 |
| X2.4 | 2 | 0.300 | principal | adição | −0,088 | [−0,382; 0,207] | 0,559 | 1,000 | — | — | — | 74/56 |
| X2.4 | 2 | 0.400 | principal | adição | −0,339 | [−1,160; 0,482] | 0,419 | 1,000 | — | — | — | 48/50 |
| X2.4 | 2 | empilhado | cortes_empilhados | adição | −0,200 | [−0,606; 0,206] | 0,334 | 1,000 | — | — | — | 122/106 |
| X2.4 | 1+2 | 0.300 | ciclos_empilhados | adição | −0,055 | [−0,278; 0,168] | 0,628 | 1,000 | — | — | — | 97/79 |
| X2.4 | 1+2 | 0.400 | ciclos_empilhados | adição | −0,176 | [−0,598; 0,246] | 0,413 | 1,000 | — | — | — | 66/68 |
| X2.4 | 1+2 | empilhado | ciclos_e_cortes_empilhados | adição | −0,114 | [−0,351; 0,123] | 0,344 | 1,000 | — | — | — | 163/147 |
<!-- X2:estimativas:fim -->

### Regra estreita (divulgação)

Esta é a permanência por ciclo e faixa com a regra estreita, a da tabela
impressa na primeira execução. Ela é recalculada pelo script.

<!-- X2:descritivo_estreita:inicio -->
| Ciclo | Subgrupo | Faixa | Alocados | Ligados | Não ligados | Ambíguos | Incertos | Ligação | Permanência (11/09) | Incertos como ativos | Incertos como saídos | Permanência (12/08) | Presença no programa |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | todos | FAIXA 1 | 121 | 79 | 37 | 1 | 4 | 65,3% | 68,1% | 69,2% | 65,8% | 68,1% | 73,3% |
| 1 | todos | FAIXA 2 | 204 | 109 | 91 | 0 | 4 | 53,4% | 54,5% | 55,4% | 53,4% | 55,0% | 67,0% |
| 1 | todos | FAIXA 3 | 169 | 61 | 104 | 2 | 2 | 36,1% | 37,0% | 37,7% | 36,5% | 36,4% | 51,5% |
| 1 | todos | TOTAL | 494 | 249 | 232 | 3 | 10 | 50,4% | 51,8% | 52,7% | 50,7% | 51,8% | 63,2% |
| 2 | todos | FAIXA 1 | 178 | 128 | 46 | 1 | 3 | 71,9% | 73,6% | 74,0% | 72,3% | 74,1% | 78,2% |
| 2 | todos | FAIXA 2 | 425 | 297 | 119 | 0 | 9 | 69,9% | 71,4% | 72,0% | 69,9% | 73,6% | 73,8% |
| 2 | todos | FAIXA 3 | 454 | 242 | 197 | 2 | 13 | 53,3% | 55,1% | 56,4% | 53,5% | 55,8% | 57,6% |
| 2 | todos | TOTAL | 1057 | 667 | 362 | 3 | 25 | 63,1% | 64,8% | 65,7% | 63,3% | 66,1% | 67,6% |
<!-- X2:descritivo_estreita:fim -->

As estimativas abaixo comparam as duas regras na mesma especificação. As da
regra estreita ficam fora do BKY.

<!-- X2:estimativas_estreita:inicio -->
| Outcome | Ciclo | Corte | Especificação | τ ampla | τ estreita | p ampla | p estreita | Lee ampla | Lee estreita |
|---|---|---|---|---:|---:|---:|---:|---|---|
| X2.1 | 1 | 0.300 | principal | 0,130 | 0,144 | 0,555 | 0,516 | — | — |
| X2.1 | 1 | 0.300 | limites_lee | 0,130 | 0,144 | — | — | [0,035; 0,339] | [0,032; 0,390] |
| X2.1 | 1 | 0.400 | principal | −0,055 | −0,060 | 0,719 | 0,696 | — | — |
| X2.1 | 1 | 0.400 | limites_lee | −0,055 | −0,060 | — | — | [−0,063; −0,032] | [−0,073; −0,030] |
| X2.1 | 1 | empilhado | cortes_empilhados | 0,037 | 0,041 | 0,789 | 0,765 | — | — |
| X2.1 | 2 | 0.300 | principal | −0,021 | 0,010 | 0,858 | 0,937 | — | — |
| X2.1 | 2 | 0.300 | limites_lee | −0,021 | 0,010 | — | — | [−0,399; 0,312] | [−0,395; 0,361] |
| X2.1 | 2 | 0.400 | principal | −0,093 | −0,063 | 0,388 | 0,568 | — | — |
| X2.1 | 2 | 0.400 | limites_lee | −0,093 | −0,063 | — | — | [−0,140; 0,034] | [−0,103; 0,069] |
| X2.1 | 2 | empilhado | cortes_empilhados | −0,057 | −0,027 | 0,485 | 0,746 | — | — |
| X2.1 | 1+2 | 0.300 | ciclos_empilhados | 0,031 | 0,056 | 0,802 | 0,651 | — | — |
| X2.1 | 1+2 | 0.400 | ciclos_empilhados | −0,080 | −0,062 | 0,329 | 0,452 | — | — |
| X2.1 | 1+2 | empilhado | ciclos_e_cortes_empilhados | −0,025 | −0,003 | 0,743 | 0,966 | — | — |
| X2.2 | 1 | 0.300 | principal | 0,035 | 0,035 | 0,890 | 0,890 | — | — |
| X2.2 | 1 | 0.300 | limites_lee | 0,035 | 0,035 | — | — | [0,039; 0,041] | [0,039; 0,041] |
| X2.2 | 1 | 0.400 | principal | 0,062 | 0,058 | 0,753 | 0,768 | — | — |
| X2.2 | 1 | 0.400 | limites_lee | 0,062 | 0,058 | — | — | [−0,292; 0,295] | [−0,296; 0,318] |
| X2.2 | 1 | empilhado | cortes_empilhados | 0,050 | 0,048 | 0,746 | 0,756 | — | — |
| X2.2 | 2 | 0.300 | principal | −0,078 | −0,072 | 0,661 | 0,684 | — | — |
| X2.2 | 2 | 0.300 | limites_lee | −0,078 | −0,072 | — | — | [−0,288; 0,028] | [−0,280; 0,032] |
| X2.2 | 2 | 0.400 | principal | −0,109 | −0,104 | 0,341 | 0,367 | — | — |
| X2.2 | 2 | 0.400 | limites_lee | −0,109 | −0,104 | — | — | [−0,140; 0,020] | [−0,134; 0,025] |
| X2.2 | 2 | empilhado | cortes_empilhados | −0,094 | −0,089 | 0,364 | 0,393 | — | — |
| X2.2 | 1+2 | 0.300 | ciclos_empilhados | −0,039 | −0,035 | 0,802 | 0,820 | — | — |
| X2.2 | 1+2 | 0.400 | ciclos_empilhados | −0,042 | −0,041 | 0,656 | 0,669 | — | — |
| X2.2 | 1+2 | empilhado | ciclos_e_cortes_empilhados | −0,041 | −0,038 | 0,643 | 0,664 | — | — |
| X2.3 | 1 | 0.300 | principal | 0,003 | 0,005 | 0,978 | 0,965 | — | — |
| X2.3 | 1 | 0.400 | principal | −0,037 | −0,038 | 0,725 | 0,721 | — | — |
| X2.3 | 1 | empilhado | cortes_empilhados | −0,016 | −0,015 | 0,832 | 0,838 | — | — |
| X2.3 | 2 | 0.300 | principal | −0,175 | −0,169 | 0,066 | 0,075 | — | — |
| X2.3 | 2 | 0.400 | principal | 0,007 | 0,013 | 0,954 | 0,920 | — | — |
| X2.3 | 2 | empilhado | cortes_empilhados | −0,099 | −0,093 | 0,197 | 0,223 | — | — |
| X2.3 | 1+2 | 0.300 | ciclos_empilhados | −0,100 | −0,096 | 0,180 | 0,200 | — | — |
| X2.3 | 1+2 | 0.400 | ciclos_empilhados | −0,014 | −0,011 | 0,878 | 0,901 | — | — |
| X2.3 | 1+2 | empilhado | ciclos_e_cortes_empilhados | −0,062 | −0,059 | 0,271 | 0,298 | — | — |
| X2.4 | 1 | 0.300 | principal | −0,007 | −0,001 | 0,959 | 0,992 | — | — |
| X2.4 | 1 | 0.400 | principal | −0,011 | −0,013 | 0,945 | 0,933 | — | — |
| X2.4 | 1 | empilhado | cortes_empilhados | −0,009 | −0,008 | 0,931 | 0,941 | — | — |
| X2.4 | 2 | 0.300 | principal | −0,088 | −0,090 | 0,559 | 0,548 | — | — |
| X2.4 | 2 | 0.400 | principal | −0,339 | −0,355 | 0,419 | 0,395 | — | — |
| X2.4 | 2 | empilhado | cortes_empilhados | −0,200 | −0,209 | 0,334 | 0,313 | — | — |
| X2.4 | 1+2 | 0.300 | ciclos_empilhados | −0,055 | −0,054 | 0,628 | 0,633 | — | — |
| X2.4 | 1+2 | 0.400 | ciclos_empilhados | −0,176 | −0,186 | 0,413 | 0,387 | — | — |
| X2.4 | 1+2 | empilhado | ciclos_e_cortes_empilhados | −0,114 | −0,118 | 0,344 | 0,326 | — | — |
<!-- X2:estimativas_estreita:fim -->

### Leitura

<!-- X2:leitura:inicio -->
- Ciclo 1: 494 alocados da 1ª chamada; 50,4% ligados a um ativo no município de alocação em 11/09/2026; permanência entre os determinados 52,3% (12/08/2026: 52,3%); com a regra estreita, 10 incertos (ampla: 15) e permanência 51,8%.
- Ciclo 2: 1057 alocados da 1ª chamada; 63,1% ligados a um ativo no município de alocação em 11/09/2026; permanência entre os determinados 65,9% (12/08/2026: 67,2%); com a regra estreita, 25 incertos (ampla: 42) e permanência 64,8%.
- Ciclo 1 por evento final: permanência 82,4% entre os homologados e 0,6% entre os que só tiveram o local confirmado.
- Horizonte mediano do início de atividade ao retrato de 11/09/2026, entre os ligados: ciclo 1: 11,8 meses; ciclo 2: 5,4 meses.
- CRM entre os dois retratos: 911 de 911 pessoas ligadas nos dois têm o mesmo CRM.
- RDD, regra ampla: 36 estimativas com p (8 do protocolo); 0 com p < 0,05; menor q de BKY = 1,000 (só protocolo: 1,000); 8 de 8 ICs de Lee contêm zero.
- RDD, regra estreita: 36 estimativas com p (8 do protocolo); 0 com p < 0,05; fora do BKY; 8 de 8 ICs de Lee contêm zero.
<!-- X2:leitura:fim -->

- Os números estão no bloco acima.
- Como em todo o protocolo 45, nada aqui é confirmatório: os q de BKY valem
  dentro do X2.
- A leitura relevante para H2 e para a proposta C é se os limites de Lee e os
  ICs incondicionais descartam saídas grandes do lado de bolsa menor. Não
  basta olhar se o ponto é zero.

## X3

> **Script:** `scripts/rdd_bolsa/18_permanencia_ativos.py`.<br>
> **Saídas:** `output/rdd_bolsa/X3_*` (`natureza_dos_dados = EMPIRICO`;
> conferência de completude e populações em `X3_resumo.json`).<br>
> **Pergunta (doc 45, §3):** como evolui o número de ativos por município e
> curso, mês a mês, de dez/25 a ago/26?

### Fonte e completude

- **Leitura.**
  - De `data/pmm_especialistas_serie_historica.csv` só se leem `co_ibge`, o
    código do curso (número inicial do rótulo, que tem mojibake), a
    competência e `qtd_ativos`.
  - A coluna `ivs` do arquivo (rótulos inconsistentes) e a faixa do arquivo
    não são usadas. A running variable é o IVS a08.
  - Linhas repetidas de município × curso × mês são somadas.
- **Conferência de completude** (antes de qualquer outcome), contra o retrato
  nominal de 12/08/2026:
  - (i) o último mês tem de reproduzir o retrato por município × curso;
  - (ii) cada mês tem de conter, por município × curso, ao menos os ativos do
    retrato que começaram antes do 1º dia do mês.
- **Regra fixada.** Se todos os meses passam, ausência de linha vira zero em
  U. Se algum falha, cada mês usa só os municípios listados naquele mês. A
  queda usa zero no último mês para quem não está listado nele, porque o
  último mês reproduz o retrato.
- **Sensibilidade.**
  - A conferência mostrou meses em que municípios da cota somem da listagem.
    O total do mês se mantém, porque alguns municípios aparecem com mais
    ativos que nos meses vizinhos.
  - Daí uma sensibilidade: pico só nos meses sem município da cota ausente
    (X3.3s–X3.5s, rotulada `ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO`).
  - **Ordem de execução (divulgação).** Essa sensibilidade foi definida antes
    de abrir qualquer estimativa X3. Mas foi definida depois de impressos o
    descritivo mensal e o descritivo da queda por faixa.
  - Ela não tira só os meses da redistribuição. Mantém apenas os meses sem
    município da cota ausente e exclui a maior parte da série (contagem no
    bloco "Leitura"). Por isso muda a definição do pico, e não só remove o
    artefato.
  - A auditoria independente de 19/10/2026, já com os resultados vistos,
    pediu uma variante que exclui só mai/26 e jun/26 (X3.3m–X3.5m, também
    adição). As duas estão nas tabelas.

<!-- X3:completude:inicio -->
| Mês | Municípios listados | Células município × curso | Ativos na série | Cota inferior do retrato | Células com violação | Déficit | Municípios da cota ausentes | Municípios acima dos meses vizinhos | Excesso |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2025-12 | 186 | 407 | 577 | 507 | 58 | 70 | 9 | 9 | 14 |
| 2026-01 | 151 | 375 | 583 | 516 | 96 | 123 | 37 | 17 | 78 |
| 2026-02 | 188 | 416 | 569 | 518 | 19 | 19 | 1 | 5 | 5 |
| 2026-03 | 181 | 400 | 551 | 519 | 19 | 19 | 1 | 0 | 0 |
| 2026-04 | 318 | 781 | 1350 | 830 | 21 | 21 | 0 | 52 | 116 |
| 2026-05 | 245 | 639 | 1363 | 1279 | 235 | 304 | 75 | 6 | 8 |
| 2026-06 | 257 | 692 | 1501 | 1295 | 232 | 302 | 72 | 14 | 45 |
| 2026-07 | 513 | 1346 | 1511 | 1478 | 4 | 4 | 0 | 9 | 10 |
| 2026-08 | 325 | 838 | 1480 | 1480 | 0 | 0 | 0 | 4 | 4 |
<!-- X3:completude:fim -->

### Descritivo por mês e faixa

Os municípios listados mudam de mês a mês, e a ausência não é zero. As médias
mensais não são comparáveis entre meses com listagens diferentes.

<!-- X3:descritivo_mensal:inicio -->
| Mês | FAIXA 3: municípios / ativos / média por 10 mil | FAIXA 2: municípios / ativos / média por 10 mil | FAIXA 1: municípios / ativos / média por 10 mil | TOTAL: municípios / ativos / média por 10 mil |
|---|---|---|---|---|
| 2025-12 | 57 / 149 / 0,292 | 75 / 306 / 0,486 | 54 / 122 / 0,677 | 186 / 577 / 0,482 |
| 2026-01 | 49 / 161 / 0,343 | 64 / 335 / 0,527 | 38 / 87 / 0,812 | 151 / 583 / 0,539 |
| 2026-02 | 59 / 149 / 0,299 | 76 / 282 / 0,505 | 53 / 138 / 0,739 | 188 / 569 / 0,506 |
| 2026-03 | 54 / 138 / 0,256 | 75 / 276 / 0,505 | 52 / 137 / 0,752 | 181 / 551 / 0,502 |
| 2026-04 | 112 / 443 / 0,302 | 101 / 630 / 0,933 | 105 / 277 / 0,769 | 318 / 1350 / 0,657 |
| 2026-05 | 95 / 476 / 0,301 | 77 / 707 / 1,019 | 73 / 180 / 0,841 | 245 / 1363 / 0,688 |
| 2026-06 | 97 / 524 / 0,328 | 78 / 776 / 1,057 | 82 / 201 / 0,825 | 257 / 1501 / 0,708 |
| 2026-07 | 193 / 481 / 0,196 | 153 / 712 / 0,660 | 167 / 318 / 0,556 | 513 / 1511 / 0,452 |
| 2026-08 | 108 / 467 / 0,337 | 105 / 697 / 0,903 | 112 / 316 / 0,826 | 325 / 1480 / 0,688 |
<!-- X3:descritivo_mensal:fim -->

<!-- X3:descritivo_queda:inicio -->
| Faixa | Municípios com ativo em algum mês | Com ativo no último mês | Queda média (ativos) | Queda média por 10 mil | Fração com queda | Queda relativa média | Meses com ativo (média) | Queda média (meses sem ausência) | Queda relativa média (meses sem ausência) | Queda média (sem mai/jun) | Queda relativa média (sem mai/jun) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAIXA 1 | 115 | 112 | 0,078 | 0,016 | 7,0% | 4,1% | 5,93 | 0,053 | 2,1% | 0,078 | 4,1% |
| FAIXA 2 | 111 | 105 | 2,117 | 0,097 | 29,7% | 12,8% | 6,82 | 0,302 | 5,0% | 0,766 | 11,0% |
| FAIXA 3 | 131 | 108 | 1,427 | 0,088 | 40,5% | 25,6% | 5,68 | 0,435 | 17,0% | 0,580 | 23,4% |
| TOTAL | 357 | 325 | 1,207 | 0,068 | 26,3% | 14,7% | 6,11 | 0,268 | 8,4% | 0,476 | 13,4% |
<!-- X3:descritivo_queda:fim -->

### RDD mês a mês e da queda

- Outcomes:
  - X3.1 e X3.2: ativos no mês (contagem e por 10 mil habitantes, Censo 2022);
  - X3.3 a X3.5: queda do pico ao último mês (contagem, por 10 mil habitantes
    e relativa);
  - X3.6: meses listados com ativo.
- Estimação: local linear sharp, h = 0,050, HC1, cortes 0,300 e 0,400. Os
  cortes empilhados e as duas variantes do pico são **adições ao
  protocolo**: o §3 do X3 pede RDD mês a mês e da queda.
- **Condicionamento.**
  - As RDD mensais condicionam à listagem do mês. Ser listado é
    pós-tratamento e pode depender do lado do corte.
  - A queda e os meses com ativo condicionam a ter pico positivo nas
    listagens, também pós-tratamento.
  - Não há limites de Lee para esse condicionamento: as linhas são
    descritivas da população listada, não efeitos sobre todos os municípios.
- **Horizontes.**
  - Municípios do ciclo 1 têm seguimento muito mais longo que os do ciclo 2
    (medianas no bloco "Leitura").
  - A queda do pico e os meses de abril em diante misturam os dois
    horizontes, e o empilhamento também.
- Em `X3_estimativas.csv`, a coluna `condicionamento` e a nota de cada linha
  mensal registram se o mês falha a conferência de completude.

<!-- X3:estimativas:inicio -->
| Outcome | Mês | Corte | Especificação | Protocolo | τ | IC 95% | p | q BKY | q BKY só protocolo | n abaixo/acima |
|---|---|---|---|---|---:|---|---:|---:|---:|---|
| X3.1 | 2025-12 | 0.300 | principal | sim | 2,800 | [−2,413; 8,013] | 0,293 | 1,000 | 1,000 | 31/36 |
| X3.1 | 2025-12 | 0.400 | principal | sim | 0,419 | [−2,488; 3,325] | 0,778 | 1,000 | 1,000 | 37/29 |
| X3.1 | 2025-12 | empilhado | cortes_empilhados | adição | 1,404 | [−1,347; 4,155] | 0,317 | 1,000 | — | 68/65 |
| X3.1 | 2026-01 | 0.300 | principal | sim | 1,485 | [−4,454; 7,424] | 0,624 | 1,000 | 1,000 | 27/35 |
| X3.1 | 2026-01 | 0.400 | principal | sim | 2,040 | [−2,044; 6,124] | 0,328 | 1,000 | 1,000 | 28/20 |
| X3.1 | 2026-01 | empilhado | cortes_empilhados | adição | 1,764 | [−1,832; 5,361] | 0,336 | 1,000 | — | 55/55 |
| X3.1 | 2026-02 | 0.300 | principal | sim | 2,338 | [−2,417; 7,094] | 0,335 | 1,000 | 1,000 | 32/39 |
| X3.1 | 2026-02 | 0.400 | principal | sim | −0,089 | [−3,043; 2,865] | 0,953 | 1,000 | 1,000 | 36/29 |
| X3.1 | 2026-02 | empilhado | cortes_empilhados | adição | 1,022 | [−1,675; 3,719] | 0,458 | 1,000 | — | 68/68 |
| X3.1 | 2026-03 | 0.300 | principal | sim | 2,700 | [−2,297; 7,696] | 0,290 | 1,000 | 1,000 | 32/38 |
| X3.1 | 2026-03 | 0.400 | principal | sim | −0,142 | [−3,127; 2,842] | 0,926 | 1,000 | 1,000 | 36/28 |
| X3.1 | 2026-03 | empilhado | cortes_empilhados | adição | 1,100 | [−1,675; 3,875] | 0,437 | 1,000 | — | 68/66 |
| X3.1 | 2026-04 | 0.300 | principal | sim | −1,460 | [−7,735; 4,814] | 0,648 | 1,000 | 1,000 | 54/51 |
| X3.1 | 2026-04 | 0.400 | principal | sim | −4,434 | [−10,357; 1,489] | 0,142 | 1,000 | 1,000 | 49/57 |
| X3.1 | 2026-04 | empilhado | cortes_empilhados | adição | −3,213 | [−7,563; 1,138] | 0,148 | 1,000 | — | 103/108 |
| X3.1 | 2026-05 | 0.300 | principal | sim | −7,404 | [−20,530; 5,721] | 0,269 | 1,000 | 1,000 | 43/41 |
| X3.1 | 2026-05 | 0.400 | principal | sim | −4,181 | [−12,465; 4,103] | 0,323 | 1,000 | 1,000 | 34/40 |
| X3.1 | 2026-05 | empilhado | cortes_empilhados | adição | −5,574 | [−12,912; 1,763] | 0,136 | 1,000 | — | 77/81 |
| X3.1 | 2026-06 | 0.300 | principal | sim | −6,954 | [−20,822; 6,915] | 0,326 | 1,000 | 1,000 | 45/42 |
| X3.1 | 2026-06 | 0.400 | principal | sim | −4,637 | [−14,710; 5,436] | 0,367 | 1,000 | 1,000 | 34/43 |
| X3.1 | 2026-06 | empilhado | cortes_empilhados | adição | −5,649 | [−13,917; 2,620] | 0,181 | 1,000 | — | 79/85 |
| X3.1 | 2026-07 | 0.300 | principal | sim | −4,238 | [−9,759; 1,282] | 0,132 | 1,000 | 1,000 | 75/75 |
| X3.1 | 2026-07 | 0.400 | principal | sim | −3,693 | [−10,230; 2,844] | 0,268 | 1,000 | 1,000 | 76/75 |
| X3.1 | 2026-07 | empilhado | cortes_empilhados | adição | −3,942 | [−8,290; 0,406] | 0,076 | 1,000 | — | 151/150 |
| X3.1 | 2026-08 | 0.300 | principal | sim | −3,243 | [−10,100; 3,613] | 0,354 | 1,000 | 1,000 | 51/56 |
| X3.1 | 2026-08 | 0.400 | principal | sim | −4,773 | [−12,291; 2,745] | 0,213 | 1,000 | 1,000 | 48/60 |
| X3.1 | 2026-08 | empilhado | cortes_empilhados | adição | −4,137 | [−9,366; 1,092] | 0,121 | 1,000 | — | 99/116 |
| X3.2 | 2025-12 | 0.300 | principal | sim | 0,239 | [−0,247; 0,726] | 0,335 | 1,000 | 1,000 | 31/36 |
| X3.2 | 2025-12 | 0.400 | principal | sim | 0,470 | [−1,604; 2,544] | 0,657 | 1,000 | 1,000 | 37/29 |
| X3.2 | 2025-12 | empilhado | cortes_empilhados | adição | 0,375 | [−0,852; 1,601] | 0,549 | 1,000 | — | 68/65 |
| X3.2 | 2026-01 | 0.300 | principal | sim | 0,313 | [−0,191; 0,816] | 0,223 | 1,000 | 1,000 | 27/35 |
| X3.2 | 2026-01 | 0.400 | principal | sim | 1,331 | [−1,998; 4,660] | 0,433 | 1,000 | 1,000 | 28/20 |
| X3.2 | 2026-01 | empilhado | cortes_empilhados | adição | 0,825 | [−0,859; 2,509] | 0,337 | 1,000 | — | 55/55 |
| X3.2 | 2026-02 | 0.300 | principal | sim | 0,199 | [−0,234; 0,631] | 0,368 | 1,000 | 1,000 | 32/39 |
| X3.2 | 2026-02 | 0.400 | principal | sim | 0,405 | [−1,688; 2,498] | 0,704 | 1,000 | 1,000 | 36/29 |
| X3.2 | 2026-02 | empilhado | cortes_empilhados | adição | 0,311 | [−0,835; 1,456] | 0,595 | 1,000 | — | 68/68 |
| X3.2 | 2026-03 | 0.300 | principal | sim | 0,217 | [−0,261; 0,694] | 0,374 | 1,000 | 1,000 | 32/38 |
| X3.2 | 2026-03 | 0.400 | principal | sim | 0,388 | [−1,716; 2,493] | 0,718 | 1,000 | 1,000 | 36/28 |
| X3.2 | 2026-03 | empilhado | cortes_empilhados | adição | 0,313 | [−0,882; 1,509] | 0,608 | 1,000 | — | 68/66 |
| X3.2 | 2026-04 | 0.300 | principal | sim | −0,241 | [−0,674; 0,193] | 0,277 | 1,000 | 1,000 | 54/51 |
| X3.2 | 2026-04 | 0.400 | principal | sim | −1,629 | [−5,466; 2,209] | 0,405 | 1,000 | 1,000 | 49/57 |
| X3.2 | 2026-04 | empilhado | cortes_empilhados | adição | −1,059 | [−3,340; 1,223] | 0,363 | 1,000 | — | 103/108 |
| X3.2 | 2026-05 | 0.300 | principal | sim | −0,152 | [−0,586; 0,281] | 0,491 | 1,000 | 1,000 | 43/41 |
| X3.2 | 2026-05 | 0.400 | principal | sim | −2,088 | [−7,075; 2,899] | 0,412 | 1,000 | 1,000 | 34/40 |
| X3.2 | 2026-05 | empilhado | cortes_empilhados | adição | −1,251 | [−4,110; 1,608] | 0,391 | 1,000 | — | 77/81 |
| X3.2 | 2026-06 | 0.300 | principal | sim | −0,117 | [−0,586; 0,353] | 0,626 | 1,000 | 1,000 | 45/42 |
| X3.2 | 2026-06 | 0.400 | principal | sim | −2,056 | [−7,035; 2,923] | 0,418 | 1,000 | 1,000 | 34/43 |
| X3.2 | 2026-06 | empilhado | cortes_empilhados | adição | −1,209 | [−4,043; 1,625] | 0,403 | 1,000 | — | 79/85 |
| X3.2 | 2026-07 | 0.300 | principal | sim | −0,381 | [−0,711; −0,052] | 0,023 | 1,000 | 1,000 | 75/75 |
| X3.2 | 2026-07 | 0.400 | principal | sim | −1,023 | [−4,197; 2,150] | 0,527 | 1,000 | 1,000 | 76/75 |
| X3.2 | 2026-07 | empilhado | cortes_empilhados | adição | −0,730 | [−2,462; 1,002] | 0,409 | 1,000 | — | 151/150 |
| X3.2 | 2026-08 | 0.300 | principal | sim | −0,315 | [−0,729; 0,099] | 0,136 | 1,000 | 1,000 | 51/56 |
| X3.2 | 2026-08 | 0.400 | principal | sim | −1,538 | [−5,400; 2,324] | 0,435 | 1,000 | 1,000 | 48/60 |
| X3.2 | 2026-08 | empilhado | cortes_empilhados | adição | −1,029 | [−3,301; 1,243] | 0,375 | 1,000 | — | 99/116 |
| X3.3 | dez/25-ago/26 | 0.300 | principal | sim | −4,424 | [−9,606; 0,757] | 0,094 | 1,000 | 1,000 | 60/58 |
| X3.3 | dez/25-ago/26 | 0.400 | principal | sim | −0,086 | [−0,848; 0,675] | 0,824 | 1,000 | 1,000 | 51/61 |
| X3.3 | dez/25-ago/26 | empilhado | cortes_empilhados | adição | −1,927 | [−4,199; 0,345] | 0,096 | 1,000 | — | 111/119 |
| X3.3m | 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 | 0.300 | sensibilidade_sem_mai_jun | adição | −0,571 | [−1,844; 0,702] | 0,379 | 1,000 | — | 60/58 |
| X3.3m | 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 | 0.400 | sensibilidade_sem_mai_jun | adição | −0,208 | [−0,609; 0,194] | 0,311 | 1,000 | — | 51/61 |
| X3.3m | 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 | empilhado | sensibilidade_sem_mai_jun_cortes_empilhados | adição | −0,362 | [−0,950; 0,226] | 0,228 | 1,000 | — | 111/119 |
| X3.3s | 2026-04,2026-07,2026-08 | 0.300 | sensibilidade_meses_sem_ausencia | adição | −0,432 | [−1,171; 0,306] | 0,251 | 1,000 | — | 58/56 |
| X3.3s | 2026-04,2026-07,2026-08 | 0.400 | sensibilidade_meses_sem_ausencia | adição | −0,242 | [−0,545; 0,062] | 0,118 | 1,000 | — | 49/60 |
| X3.3s | 2026-04,2026-07,2026-08 | empilhado | sensibilidade_meses_sem_ausencia_cortes_empilhados | adição | −0,324 | [−0,686; 0,037] | 0,079 | 1,000 | — | 107/116 |
| X3.4 | dez/25-ago/26 | 0.300 | principal | sim | −0,099 | [−0,186; −0,011] | 0,027 | 1,000 | 1,000 | 60/58 |
| X3.4 | dez/25-ago/26 | 0.400 | principal | sim | −0,038 | [−0,140; 0,064] | 0,461 | 1,000 | 1,000 | 51/61 |
| X3.4 | dez/25-ago/26 | empilhado | cortes_empilhados | adição | −0,064 | [−0,133; 0,005] | 0,069 | 1,000 | — | 111/119 |
| X3.4m | 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 | 0.300 | sensibilidade_sem_mai_jun | adição | −0,053 | [−0,120; 0,013] | 0,118 | 1,000 | — | 60/58 |
| X3.4m | 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 | 0.400 | sensibilidade_sem_mai_jun | adição | −0,040 | [−0,141; 0,062] | 0,446 | 1,000 | — | 51/61 |
| X3.4m | 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 | empilhado | sensibilidade_sem_mai_jun_cortes_empilhados | adição | −0,045 | [−0,110; 0,019] | 0,170 | 1,000 | — | 111/119 |
| X3.4s | 2026-04,2026-07,2026-08 | 0.300 | sensibilidade_meses_sem_ausencia | adição | −0,024 | [−0,085; 0,037] | 0,434 | 1,000 | — | 58/56 |
| X3.4s | 2026-04,2026-07,2026-08 | 0.400 | sensibilidade_meses_sem_ausencia | adição | 0,006 | [−0,086; 0,098] | 0,894 | 1,000 | — | 49/60 |
| X3.4s | 2026-04,2026-07,2026-08 | empilhado | sensibilidade_meses_sem_ausencia_cortes_empilhados | adição | −0,007 | [−0,065; 0,051] | 0,815 | 1,000 | — | 107/116 |
| X3.5 | dez/25-ago/26 | 0.300 | principal | sim | −0,250 | [−0,488; −0,013] | 0,039 | 1,000 | 1,000 | 60/58 |
| X3.5 | dez/25-ago/26 | 0.400 | principal | sim | −0,139 | [−0,311; 0,033] | 0,114 | 1,000 | 1,000 | 51/61 |
| X3.5 | dez/25-ago/26 | empilhado | cortes_empilhados | adição | −0,186 | [−0,327; −0,045] | 0,010 | 1,000 | — | 111/119 |
| X3.5m | 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 | 0.300 | sensibilidade_sem_mai_jun | adição | −0,172 | [−0,407; 0,063] | 0,151 | 1,000 | — | 60/58 |
| X3.5m | 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 | 0.400 | sensibilidade_sem_mai_jun | adição | −0,138 | [−0,310; 0,034] | 0,116 | 1,000 | — | 51/61 |
| X3.5m | 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 | empilhado | sensibilidade_sem_mai_jun_cortes_empilhados | adição | −0,153 | [−0,293; −0,012] | 0,033 | 1,000 | — | 111/119 |
| X3.5s | 2026-04,2026-07,2026-08 | 0.300 | sensibilidade_meses_sem_ausencia | adição | −0,069 | [−0,275; 0,136] | 0,509 | 1,000 | — | 58/56 |
| X3.5s | 2026-04,2026-07,2026-08 | 0.400 | sensibilidade_meses_sem_ausencia | adição | −0,008 | [−0,063; 0,046] | 0,769 | 1,000 | — | 49/60 |
| X3.5s | 2026-04,2026-07,2026-08 | empilhado | sensibilidade_meses_sem_ausencia_cortes_empilhados | adição | −0,035 | [−0,129; 0,059] | 0,471 | 1,000 | — | 107/116 |
| X3.6 | dez/25-ago/26 | 0.300 | principal | sim | −0,352 | [−2,353; 1,649] | 0,730 | 1,000 | 1,000 | 60/58 |
| X3.6 | dez/25-ago/26 | 0.400 | principal | sim | −1,148 | [−2,968; 0,671] | 0,216 | 1,000 | 1,000 | 51/61 |
| X3.6 | dez/25-ago/26 | empilhado | cortes_empilhados | adição | −0,810 | [−2,155; 0,534] | 0,238 | 1,000 | — | 111/119 |
<!-- X3:estimativas:fim -->

### Leitura

<!-- X3:leitura:inicio -->
- Último mês (2026-08) reproduz o retrato nominal por município × curso: sim.
- Listagem completa em todos os meses: não; meses que falham a cota inferior: 2025-12, 2026-01, 2026-02, 2026-03, 2026-04, 2026-05, 2026-06, 2026-07; meses sem município da cota ausente: 2026-04, 2026-07, 2026-08.
- População de estimação mensal: municipios listados no mes (listagem incompleta: ausencia nao e zero).
- Horizonte mediano do início de atividade ao retrato de 12/08/2026, por ciclo do ativo: ciclo 1: 10,7 meses; ciclo 2: 4,4 meses.
- Especificações por corte do protocolo (§3): 44 estimativas com p; com p < 0,05: X3.2 2026-07 0.300 (τ = −0,381, p = 0,023, q = 1,000); X3.4 dez/25-ago/26 0.300 (τ = −0,099, p = 0,027, q = 1,000); X3.5 dez/25-ago/26 0.300 (τ = −0,250, p = 0,039, q = 1,000).
- Cortes empilhados (adição): 22 estimativas com p; com p < 0,05: X3.5 dez/25-ago/26 empilhado (τ = −0,186, p = 0,010, q = 1,000).
- Sensibilidade de meses sem ausência (pico em 3 dos 9 meses: 2026-04, 2026-07, 2026-08): 9 estimativas com p; com p < 0,05: nenhuma.
- Variante sem 2026-05, 2026-06 (pico em 7 dos 9 meses; pedido da auditoria): 9 estimativas com p; com p < 0,05: X3.5m 2025-12,2026-01,2026-02,2026-03,2026-04,2026-07,2026-08 empilhado (τ = −0,153, p = 0,033, q = 1,000).
- Menor q de BKY no X3: 1,000 (só protocolo: 1,000).
<!-- X3:leitura:fim -->

- A série é agregada e sem identificador individual. Uma queda de ativos num
  município não separa saída, transferência, correção cadastral e mudança na
  regra de listagem.
- Nos meses em que a listagem falha a conferência, o pico pode vir da
  redistribuição de ativos entre municípios, não de presença real.
- As três definições do pico não contam a mesma história. Com a
  sensibilidade de meses sem ausência, nenhuma linha tem p < 0,05. Essa
  sensibilidade, porém, descarta a maior parte da série.
- Na variante que exclui só mai/26 e jun/26, a queda relativa empilhada
  continua negativa com p < 0,05 (bloco acima). Portanto não é correto
  dizer que todos os sinais da queda somem quando se tira o artefato.
- Todas as linhas X3 têm q de BKY no teto, e o condicionamento à listagem
  impede leitura causal.

## X4 — Heterogeneidade da escolha (E9)

> **Data:** 19/10/2026.<br>
> **Estatuto:** `EXPLORATORIO_POS_SINTESE` (protocolo
> [`45`](45_protocolo_exploratorio_pos_sintese.md), §2 e §3). Pós-resultado: nada
> aqui é teste confirmatório, e nada muda o protocolo 40, o E9 ou o Holm das
> primárias.<br>
> **Script:** `scripts/rdd_bolsa/19_escolha_heterogeneidade.py` (importa do
> `16_estimar_E9_escolha.py` a preparação dos dados, a verossimilhança, o
> sanduíche por cluster e o score bootstrap).<br>
> **Saídas:** `output/rdd_bolsa/X4_estimativas.csv`, `X4X5_resumo.json`
> (entradas com SHA-256, conferências, decisões, desvios) e
> `X4X5_tabelas_relato.md`.<br>
> **Testes:** `tests/test_x4_x5_escolha.py` (recuperação de interações em dados
> sintéticos, invariantes das saídas, blocos abaixo iguais aos gerados, frases
> desta seção conferidas contra os CSVs).

Nenhum número desta seção foi digitado: as tabelas são copiadas do bloco X4 de
`output/rdd_bolsa/X4X5_tabelas_relato.md`, e um teste confere que são idênticas
e que, fora delas, só aparecem números do protocolo.

### Especificação

- **Base:** o principal do E9 (logit condicional da 1a opção, conjunto
  principal, spline linear contínuo com nós em 0,300 e 0,400, bolsa linear em
  R$ mil). O script reestima esse modelo e para se o coeficiente e o EP da bolsa
  não reproduzirem `E9_estimativas.csv` (conferência em `X4X5_resumo.json`).
- **Interações**, uma dimensão por modelo, por ciclo e empilhado; bolsa (grupo
  de base) mais bolsa × grupo para os demais:
  - (a) **tercil da pontuação** do candidato dentro do ciclo (a pontuação do
    F4), calculado antes da estimação; empate no corte vai para o tercil de
    baixo (Tabela X4.3). Quem não tem pontuação (os "SEM PRÉ-REQUISITO" do ciclo
    1) é um grupo próprio, sem imputação. Como a pontuação é do candidato, cada
    conjunto é replicado por grupo de candidato; sem interação, a
    verossimilhança é a do E9 (conferido no script e no teste);
  - (b) **curso**, com ao menos 100 candidatos de 1a opção na amostra do
    modelo; os demais juntos; base = grupo com mais candidatos;
  - (c) **escassez pré-programa** da especialidade no município: vínculos das
    CBO do curso (ponte curso–CBO) por 10 mil habitantes (Censo 2022), média de
    202406 a 202506 no painel CNES nacional; tercis dentro do conjunto de
    escolha (tercil 1 = mais escasso). Os indicadores de tercil também entram
    como atributo da célula. Os cursos novos do ciclo 3 não têm ponte (lista na
    Tabela X4.6) e formam o grupo `sem_ponte_curso_cbo`;
  - (d) **estrato territorial** (base capital, como no E9).
- **Inferência:** cluster por conjunto (principal do E9), por curso (no
  empilhado; por ciclo coincide com o conjunto), máxima verossimilhança (MV) e
  cluster por candidato; score bootstrap de Kline–Santos dos termos de
  interação; Wald da igualdade de todas as inclinações. q de
  Benjamini–Krieger–Yekutieli dentro do X4, sobre interações e Wald, com o p de
  cluster por conjunto.
- **Curso:** o termo próprio de um curso só varia nos conjuntos desse curso. Com
  cluster por conjunto ou por curso, o G efetivo de cada termo é 1 por ciclo
  (coluna `g_efetivo_conjunto`), e o EP por cluster não tem sentido. Essas
  linhas ficam marcadas (`inferencia_cluster_degenerada`), fora do BKY, com o EP
  de MV e o de cluster por candidato ao lado.

### Resultados

<!-- X4_TABELAS_INICIO -->
<!-- gerado por scripts/rdd_bolsa/19_escolha_heterogeneidade.py; não editar à mão -->

**Tabela X4.1. Inclinação da bolsa por grupo (coef. por R$ 1 mil; logit condicional, principal do E9 com interações).** IC 95% e p pela normal com EP de cluster por conjunto; na dimensão curso, em que o EP por cluster é degenerado, com o EP de máxima verossimilhança (MV), que ignora o choque comum do conjunto (coluna inferência).

| dimensão | ciclo | grupo | candidatos | coef. | IC 95% | p | inferência |
|---|---|---|---:|---:|---|---:|---|
| nota_tercil | 1 | tercil1 | 323 | 0,0450 | [−0,0376; 0,1276] | 0,286 | cluster por conjunto |
| nota_tercil | 1 | tercil2 | 284 | 0,0695 | [−0,0203; 0,1593] | 0,129 | cluster por conjunto |
| nota_tercil | 1 | tercil3 | 272 | 0,1001 | [−0,0041; 0,2044] | 0,060 | cluster por conjunto |
| nota_tercil | 1 | sem_pontuacao | 114 | 0,0354 | [−0,0722; 0,1429] | 0,519 | cluster por conjunto |
| nota_tercil | 2 | tercil1 | 1372 | 0,1455 | [0,0898; 0,2012] | < 0,001 | cluster por conjunto |
| nota_tercil | 2 | tercil2 | 120 | 0,1027 | [0,0029; 0,2025] | 0,044 | cluster por conjunto |
| nota_tercil | 2 | tercil3 | 648 | 0,1107 | [0,0679; 0,1534] | < 0,001 | cluster por conjunto |
| nota_tercil | 3 | tercil1 | 1635 | 0,0137 | [−0,0532; 0,0806] | 0,688 | cluster por conjunto |
| nota_tercil | 3 | tercil2 | 184 | −0,0032 | [−0,0931; 0,0866] | 0,944 | cluster por conjunto |
| nota_tercil | 3 | tercil3 | 762 | 0,0016 | [−0,0555; 0,0586] | 0,957 | cluster por conjunto |
| nota_tercil | empilhado | tercil1 | 3330 | 0,0756 | [0,0275; 0,1237] | 0,002 | cluster por conjunto |
| nota_tercil | empilhado | tercil2 | 588 | 0,0383 | [−0,0074; 0,0840] | 0,100 | cluster por conjunto |
| nota_tercil | empilhado | tercil3 | 1682 | 0,0609 | [0,0226; 0,0992] | 0,002 | cluster por conjunto |
| nota_tercil | empilhado | sem_pontuacao | 114 | −0,0145 | [−0,0716; 0,0426] | 0,618 | cluster por conjunto |
| curso | 1 | curso02 | 106 | 0,0880 | [0,0230; 0,1530] | 0,008 | MV (cluster degenerado) |
| curso | 1 | curso08 | 185 | 0,0362 | [−0,0196; 0,0920] | 0,203 | MV (cluster degenerado) |
| curso | 1 | curso14 | 115 | 0,1013 | [0,0366; 0,1660] | 0,002 | MV (cluster degenerado) |
| curso | 1 | demais_cursos | 587 | 0,0656 | [0,0175; 0,1138] | 0,008 | MV (cluster degenerado) |
| curso | 2 | curso01 | 510 | 0,2073 | [0,1709; 0,2437] | < 0,001 | MV (cluster degenerado) |
| curso | 2 | curso02 | 408 | 0,1005 | [0,0624; 0,1385] | < 0,001 | MV (cluster degenerado) |
| curso | 2 | curso07 | 103 | 0,0566 | [−0,0110; 0,1243] | 0,101 | MV (cluster degenerado) |
| curso | 2 | curso08 | 400 | 0,1210 | [0,0841; 0,1580] | < 0,001 | MV (cluster degenerado) |
| curso | 2 | curso11 | 119 | 0,0950 | [0,0388; 0,1511] | < 0,001 | MV (cluster degenerado) |
| curso | 2 | curso14 | 162 | 0,1093 | [0,0581; 0,1605] | < 0,001 | MV (cluster degenerado) |
| curso | 2 | curso15 | 139 | 0,1306 | [0,0758; 0,1853] | < 0,001 | MV (cluster degenerado) |
| curso | 2 | demais_cursos | 299 | 0,1286 | [0,0788; 0,1785] | < 0,001 | MV (cluster degenerado) |
| curso | 3 | curso01 | 597 | 0,0716 | [0,0388; 0,1043] | < 0,001 | MV (cluster degenerado) |
| curso | 3 | curso02 | 349 | 0,0326 | [−0,0062; 0,0715] | 0,100 | MV (cluster degenerado) |
| curso | 3 | curso08 | 222 | −0,0197 | [−0,0646; 0,0253] | 0,392 | MV (cluster degenerado) |
| curso | 3 | curso17 | 155 | −0,0112 | [−0,0545; 0,0321] | 0,613 | MV (cluster degenerado) |
| curso | 3 | curso18 | 216 | −0,0186 | [−0,0625; 0,0254] | 0,407 | MV (cluster degenerado) |
| curso | 3 | curso24 | 230 | −0,1697 | [−0,2250; −0,1145] | < 0,001 | MV (cluster degenerado) |
| curso | 3 | demais_cursos | 812 | −0,0049 | [−0,0380; 0,0283] | 0,774 | MV (cluster degenerado) |
| curso | empilhado | curso01 | 1200 | 0,1367 | [0,1140; 0,1594] | < 0,001 | MV (cluster degenerado) |
| curso | empilhado | curso02 | 863 | 0,0774 | [0,0526; 0,1022] | < 0,001 | MV (cluster degenerado) |
| curso | empilhado | curso06 | 206 | −0,0323 | [−0,0868; 0,0223] | 0,246 | MV (cluster degenerado) |
| curso | empilhado | curso07 | 206 | 0,0149 | [−0,0313; 0,0610] | 0,528 | MV (cluster degenerado) |
| curso | empilhado | curso08 | 807 | 0,0486 | [0,0242; 0,0731] | < 0,001 | MV (cluster degenerado) |
| curso | empilhado | curso09 | 139 | 0,1003 | [0,0495; 0,1512] | < 0,001 | MV (cluster degenerado) |
| curso | empilhado | curso11 | 249 | 0,0469 | [0,0064; 0,0874] | 0,023 | MV (cluster degenerado) |
| curso | empilhado | curso14 | 372 | 0,0660 | [0,0337; 0,0983] | < 0,001 | MV (cluster degenerado) |
| curso | empilhado | curso15 | 318 | 0,0681 | [0,0336; 0,1026] | < 0,001 | MV (cluster degenerado) |
| curso | empilhado | curso16 | 121 | 0,0233 | [−0,0405; 0,0872] | 0,474 | MV (cluster degenerado) |
| curso | empilhado | curso17 | 155 | 0,0430 | [0,0043; 0,0817] | 0,029 | MV (cluster degenerado) |
| curso | empilhado | curso18 | 216 | 0,0305 | [−0,0085; 0,0696] | 0,126 | MV (cluster degenerado) |
| curso | empilhado | curso24 | 230 | −0,1174 | [−0,1691; −0,0658] | < 0,001 | MV (cluster degenerado) |
| curso | empilhado | demais_cursos | 632 | 0,0309 | [−0,0015; 0,0634] | 0,062 | MV (cluster degenerado) |
| escassez_tercil | 1 | tercil1 | 300 | 0,0653 | [−0,0216; 0,1522] | 0,141 | cluster por conjunto |
| escassez_tercil | 1 | tercil2 | 302 | −0,0056 | [−0,0971; 0,0859] | 0,904 | cluster por conjunto |
| escassez_tercil | 1 | tercil3 | 391 | 0,1116 | [0,0066; 0,2167] | 0,037 | cluster por conjunto |
| escassez_tercil | 2 | tercil1 | 563 | 0,1417 | [0,0685; 0,2149] | < 0,001 | cluster por conjunto |
| escassez_tercil | 2 | tercil2 | 793 | 0,1514 | [0,1003; 0,2026] | < 0,001 | cluster por conjunto |
| escassez_tercil | 2 | tercil3 | 784 | 0,1292 | [0,0653; 0,1931] | < 0,001 | cluster por conjunto |
| escassez_tercil | 3 | tercil1 | 549 | 0,0590 | [−0,0184; 0,1364] | 0,135 | cluster por conjunto |
| escassez_tercil | 3 | tercil2 | 554 | 0,0140 | [−0,0554; 0,0835] | 0,692 | cluster por conjunto |
| escassez_tercil | 3 | tercil3 | 691 | 0,0149 | [−0,0433; 0,0730] | 0,617 | cluster por conjunto |
| escassez_tercil | 3 | sem_ponte_curso_cbo | 787 | −0,0430 | [−0,1027; 0,0168] | 0,159 | cluster por conjunto |
| escassez_tercil | empilhado | tercil1 | 1412 | 0,0948 | [0,0470; 0,1426] | < 0,001 | cluster por conjunto |
| escassez_tercil | empilhado | tercil2 | 1649 | 0,0642 | [0,0142; 0,1142] | 0,012 | cluster por conjunto |
| escassez_tercil | empilhado | tercil3 | 1866 | 0,0747 | [0,0311; 0,1183] | < 0,001 | cluster por conjunto |
| escassez_tercil | empilhado | sem_ponte_curso_cbo | 787 | 0,0006 | [−0,0574; 0,0587] | 0,983 | cluster por conjunto |
| estrato | 1 | capital | 73 | 0,0292 | [−0,0996; 0,1581] | 0,656 | cluster por conjunto |
| estrato | 1 | interior_proximo_polo | 510 | 0,0537 | [−0,0390; 0,1465] | 0,256 | cluster por conjunto |
| estrato | 1 | interior_remoto | 84 | 0,0453 | [−0,0300; 0,1205] | 0,238 | cluster por conjunto |
| estrato | 1 | metropolitano | 326 | 0,0998 | [−0,0071; 0,2068] | 0,067 | cluster por conjunto |
| estrato | 2 | capital | 714 | 0,0933 | [0,0333; 0,1533] | 0,002 | cluster por conjunto |
| estrato | 2 | interior_proximo_polo | 665 | 0,1249 | [0,0726; 0,1772] | < 0,001 | cluster por conjunto |
| estrato | 2 | interior_remoto | 135 | 0,1331 | [0,0845; 0,1817] | < 0,001 | cluster por conjunto |
| estrato | 2 | metropolitano | 626 | 0,1575 | [0,0796; 0,2354] | < 0,001 | cluster por conjunto |
| estrato | 3 | capital | 985 | −0,0615 | [−0,1406; 0,0175] | 0,127 | cluster por conjunto |
| estrato | 3 | interior_proximo_polo | 746 | 0,0355 | [−0,0214; 0,0923] | 0,222 | cluster por conjunto |
| estrato | 3 | interior_remoto | 214 | −0,0031 | [−0,0456; 0,0394] | 0,886 | cluster por conjunto |
| estrato | 3 | metropolitano | 636 | 0,0788 | [−0,0126; 0,1702] | 0,091 | cluster por conjunto |
| estrato | empilhado | capital | 1772 | 0,0072 | [−0,0493; 0,0636] | 0,803 | cluster por conjunto |
| estrato | empilhado | interior_proximo_polo | 1921 | 0,0672 | [0,0267; 0,1077] | 0,001 | cluster por conjunto |
| estrato | empilhado | interior_remoto | 433 | 0,0581 | [0,0170; 0,0991] | 0,006 | cluster por conjunto |
| estrato | empilhado | metropolitano | 1588 | 0,1106 | [0,0573; 0,1640] | < 0,001 | cluster por conjunto |

**Tabela X4.2. Termos de interação (diferença para o grupo de base) e Wald da igualdade das inclinações.** IC e p como na Tabela X4.1 (na dimensão curso, MV; o Wald de curso também é o de MV); p do score bootstrap (Rademacher, enumeração completa com G ≤ 24, senão sorteios) com cluster por conjunto e, no empilhado, por curso; não relatado na dimensão curso. q de BKY dentro do X4 (linhas fora da família: —).

| dimensão | ciclo | termo | base | coef. | IC 95% | p | p score (conjunto) | p score (curso) | q BKY | inferência |
|---|---|---|---|---:|---|---:|---:|---:|---:|---|
| nota_tercil | 1 | bolsa_x_tercil2 | tercil1 | 0,0245 | [−0,0131; 0,0621] | 0,201 | 0,270 | — | 0,204 | cluster por conjunto |
| nota_tercil | 1 | bolsa_x_tercil3 | tercil1 | 0,0551 | [0,0074; 0,1029] | 0,024 | 0,064 | — | 0,064 | cluster por conjunto |
| nota_tercil | 1 | bolsa_x_sem_pontuacao | tercil1 | −0,0096 | [−0,0596; 0,0404] | 0,706 | 0,712 | — | 0,435 | cluster por conjunto |
| nota_tercil | 1 | Wald (χ², 3 gl) = 5,17 | tercil1 | — | — | 0,160 | — | — | 0,182 | cluster por conjunto |
| nota_tercil | 2 | bolsa_x_tercil2 | tercil1 | −0,0428 | [−0,1159; 0,0303] | 0,251 | 0,343 | — | 0,214 | cluster por conjunto |
| nota_tercil | 2 | bolsa_x_tercil3 | tercil1 | −0,0348 | [−0,0691; −0,0006] | 0,046 | 0,129 | — | 0,092 | cluster por conjunto |
| nota_tercil | 2 | Wald (χ², 2 gl) = 6,47 | tercil1 | — | — | 0,039 | — | — | 0,087 | cluster por conjunto |
| nota_tercil | 3 | bolsa_x_tercil2 | tercil1 | −0,0169 | [−0,1043; 0,0704] | 0,704 | 0,732 | — | 0,435 | cluster por conjunto |
| nota_tercil | 3 | bolsa_x_tercil3 | tercil1 | −0,0121 | [−0,0427; 0,0184] | 0,436 | 0,502 | — | 0,333 | cluster por conjunto |
| nota_tercil | 3 | Wald (χ², 2 gl) = 0,71 | tercil1 | — | — | 0,700 | — | — | 0,435 | cluster por conjunto |
| nota_tercil | empilhado | bolsa_x_tercil2 | tercil1 | −0,0373 | [−0,0721; −0,0025] | 0,036 | 0,038 | 0,121 | 0,087 | cluster por conjunto |
| nota_tercil | empilhado | bolsa_x_tercil3 | tercil1 | −0,0147 | [−0,0405; 0,0111] | 0,265 | 0,329 | 0,414 | 0,219 | cluster por conjunto |
| nota_tercil | empilhado | bolsa_x_sem_pontuacao | tercil1 | −0,0901 | [−0,1458; −0,0345] | 0,002 | 0,018 | 0,030 | 0,010 | cluster por conjunto |
| nota_tercil | empilhado | Wald (χ², 3 gl) = 12,38 | tercil1 | — | — | 0,006 | — | — | 0,023 | cluster por conjunto |
| curso | 1 | bolsa_x_curso02 | demais_cursos | 0,0224 | [−0,0321; 0,0768] | 0,421 | — | — | — | MV (cluster degenerado) |
| curso | 1 | bolsa_x_curso08 | demais_cursos | −0,0294 | [−0,0735; 0,0147] | 0,192 | — | — | — | MV (cluster degenerado) |
| curso | 1 | bolsa_x_curso14 | demais_cursos | 0,0357 | [−0,0185; 0,0898] | 0,197 | — | — | — | MV (cluster degenerado) |
| curso | 1 | Wald MV (χ², 3 gl) = 5,41 | demais_cursos | — | — | 0,144 | — | — | — | MV (cluster degenerado) |
| curso | 2 | bolsa_x_curso02 | curso01 | −0,1069 | [−0,1423; −0,0714] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | 2 | bolsa_x_curso07 | curso01 | −0,1507 | [−0,2185; −0,0829] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | 2 | bolsa_x_curso08 | curso01 | −0,0863 | [−0,1218; −0,0508] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | 2 | bolsa_x_curso11 | curso01 | −0,1123 | [−0,1674; −0,0573] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | 2 | bolsa_x_curso14 | curso01 | −0,0980 | [−0,1477; −0,0484] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | 2 | bolsa_x_curso15 | curso01 | −0,0768 | [−0,1299; −0,0236] | 0,005 | — | — | — | MV (cluster degenerado) |
| curso | 2 | bolsa_x_demais_cursos | curso01 | −0,0787 | [−0,1268; −0,0306] | 0,001 | — | — | — | MV (cluster degenerado) |
| curso | 2 | Wald MV (χ², 7 gl) = 51,96 | curso01 | — | — | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | 3 | bolsa_x_curso01 | demais_cursos | 0,0764 | [0,0442; 0,1087] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | 3 | bolsa_x_curso02 | demais_cursos | 0,0375 | [−0,0003; 0,0753] | 0,052 | — | — | — | MV (cluster degenerado) |
| curso | 3 | bolsa_x_curso08 | demais_cursos | −0,0148 | [−0,0595; 0,0299] | 0,517 | — | — | — | MV (cluster degenerado) |
| curso | 3 | bolsa_x_curso17 | demais_cursos | −0,0063 | [−0,0491; 0,0365] | 0,772 | — | — | — | MV (cluster degenerado) |
| curso | 3 | bolsa_x_curso18 | demais_cursos | −0,0137 | [−0,0562; 0,0288] | 0,527 | — | — | — | MV (cluster degenerado) |
| curso | 3 | bolsa_x_curso24 | demais_cursos | −0,1649 | [−0,2192; −0,1105] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | 3 | Wald MV (χ², 6 gl) = 88,24 | demais_cursos | — | — | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso02 | curso01 | −0,0593 | [−0,0832; −0,0353] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso06 | curso01 | −0,1690 | [−0,2237; −0,1142] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso07 | curso01 | −0,1218 | [−0,1679; −0,0757] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso08 | curso01 | −0,0880 | [−0,1125; −0,0636] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso09 | curso01 | −0,0364 | [−0,0871; 0,0143] | 0,160 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso11 | curso01 | −0,0898 | [−0,1300; −0,0497] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso14 | curso01 | −0,0707 | [−0,1024; −0,0389] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso15 | curso01 | −0,0686 | [−0,1030; −0,0342] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso16 | curso01 | −0,1134 | [−0,1767; −0,0500] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso17 | curso01 | −0,0937 | [−0,1321; −0,0552] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso18 | curso01 | −0,1062 | [−0,1448; −0,0676] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_curso24 | curso01 | −0,2541 | [−0,3058; −0,2025] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | bolsa_x_demais_cursos | curso01 | −0,1058 | [−0,1383; −0,0733] | < 0,001 | — | — | — | MV (cluster degenerado) |
| curso | empilhado | Wald MV (χ², 13 gl) = 167,76 | curso01 | — | — | < 0,001 | — | — | — | MV (cluster degenerado) |
| escassez_tercil | 1 | bolsa_x_tercil2 | tercil1 | −0,0709 | [−0,1507; 0,0089] | 0,082 | 0,058 | — | 0,125 | cluster por conjunto |
| escassez_tercil | 1 | bolsa_x_tercil3 | tercil1 | 0,0463 | [−0,0238; 0,1165] | 0,195 | 0,303 | — | 0,204 | cluster por conjunto |
| escassez_tercil | 1 | Wald (χ², 2 gl) = 14,38 | tercil1 | — | — | < 0,001 | — | — | 0,008 | cluster por conjunto |
| escassez_tercil | 2 | bolsa_x_tercil2 | tercil1 | 0,0097 | [−0,0268; 0,0462] | 0,602 | 0,602 | — | 0,400 | cluster por conjunto |
| escassez_tercil | 2 | bolsa_x_tercil3 | tercil1 | −0,0125 | [−0,0709; 0,0459] | 0,674 | 0,674 | — | 0,435 | cluster por conjunto |
| escassez_tercil | 2 | Wald (χ², 2 gl) = 1,55 | tercil1 | — | — | 0,460 | — | — | 0,343 | cluster por conjunto |
| escassez_tercil | 3 | bolsa_x_tercil2 | tercil1 | −0,0450 | [−0,0907; 0,0007] | 0,054 | 0,194 | — | 0,097 | cluster por conjunto |
| escassez_tercil | 3 | bolsa_x_tercil3 | tercil1 | −0,0442 | [−0,0944; 0,0061] | 0,085 | 0,247 | — | 0,125 | cluster por conjunto |
| escassez_tercil | 3 | bolsa_x_sem_ponte_curso_cbo | tercil1 | −0,1020 | [−0,1801; −0,0239] | 0,010 | 0,006 | — | 0,034 | cluster por conjunto |
| escassez_tercil | 3 | Wald (χ², 3 gl) = 7,75 | tercil1 | — | — | 0,052 | — | — | 0,097 | cluster por conjunto |
| escassez_tercil | empilhado | bolsa_x_tercil2 | tercil1 | −0,0306 | [−0,0657; 0,0046] | 0,088 | 0,108 | 0,178 | 0,125 | cluster por conjunto |
| escassez_tercil | empilhado | bolsa_x_tercil3 | tercil1 | −0,0201 | [−0,0564; 0,0163] | 0,279 | 0,334 | 0,438 | 0,225 | cluster por conjunto |
| escassez_tercil | empilhado | bolsa_x_sem_ponte_curso_cbo | tercil1 | −0,0941 | [−0,1577; −0,0306] | 0,004 | 0,012 | 0,035 | 0,018 | cluster por conjunto |
| escassez_tercil | empilhado | Wald (χ², 3 gl) = 9,83 | tercil1 | — | — | 0,020 | — | — | 0,059 | cluster por conjunto |
| estrato | 1 | bolsa_x_interior_proximo_polo | capital | 0,0245 | [−0,1130; 0,1620] | 0,727 | 0,738 | — | 0,438 | cluster por conjunto |
| estrato | 1 | bolsa_x_interior_remoto | capital | 0,0160 | [−0,1122; 0,1442] | 0,807 | 0,807 | — | 0,462 | cluster por conjunto |
| estrato | 1 | bolsa_x_metropolitano | capital | 0,0706 | [−0,0730; 0,2142] | 0,335 | 0,382 | — | 0,262 | cluster por conjunto |
| estrato | 1 | Wald (χ², 3 gl) = 2,52 | capital | — | — | 0,472 | — | — | 0,343 | cluster por conjunto |
| estrato | 2 | bolsa_x_interior_proximo_polo | capital | 0,0316 | [−0,0044; 0,0675] | 0,085 | 0,060 | — | 0,125 | cluster por conjunto |
| estrato | 2 | bolsa_x_interior_remoto | capital | 0,0398 | [−0,0250; 0,1046] | 0,229 | 0,185 | — | 0,204 | cluster por conjunto |
| estrato | 2 | bolsa_x_metropolitano | capital | 0,0642 | [−0,0167; 0,1452] | 0,120 | 0,113 | — | 0,143 | cluster por conjunto |
| estrato | 2 | Wald (χ², 3 gl) = 3,60 | capital | — | — | 0,308 | — | — | 0,244 | cluster por conjunto |
| estrato | 3 | bolsa_x_interior_proximo_polo | capital | 0,0970 | [0,0347; 0,1592] | 0,002 | 0,009 | — | 0,013 | cluster por conjunto |
| estrato | 3 | bolsa_x_interior_remoto | capital | 0,0584 | [−0,0207; 0,1375] | 0,148 | 0,220 | — | 0,174 | cluster por conjunto |
| estrato | 3 | bolsa_x_metropolitano | capital | 0,1403 | [0,0806; 0,2001] | < 0,001 | 0,003 | — | 0,001 | cluster por conjunto |
| estrato | 3 | Wald (χ², 3 gl) = 25,07 | capital | — | — | < 0,001 | — | — | 0,001 | cluster por conjunto |
| estrato | empilhado | bolsa_x_interior_proximo_polo | capital | 0,0600 | [0,0177; 0,1023] | 0,005 | 0,007 | 0,015 | 0,023 | cluster por conjunto |
| estrato | empilhado | bolsa_x_interior_remoto | capital | 0,0509 | [0,0022; 0,0995] | 0,040 | 0,030 | 0,047 | 0,087 | cluster por conjunto |
| estrato | empilhado | bolsa_x_metropolitano | capital | 0,1035 | [0,0517; 0,1553] | < 0,001 | < 0,001 | 0,001 | 0,002 | cluster por conjunto |
| estrato | empilhado | Wald (χ², 3 gl) = 16,60 | capital | — | — | < 0,001 | — | — | 0,008 | cluster por conjunto |

**Tabela X4.3. Pontos de corte dos tercis da pontuação (1/3 e 2/3, quantil linear; empate no corte vai para o tercil de baixo).**

| ciclo | corte 1/3 | corte 2/3 | tercil 1 | tercil 2 | tercil 3 | sem pontuação |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 4,00 | 5,00 | 323 | 284 | 272 | 114 |
| 2 | 5,00 | 6,00 | 1372 | 120 | 648 | 0 |
| 3 | 5,00 | 6,00 | 1635 | 184 | 762 | 0 |

**Tabela X4.4. Estrato: candidatos de 1a opção por ciclo e inclinação da bolsa de cada estrato no modelo do ciclo (Tabela X4.1).** A fração no ciclo 3 mostra a composição que o empilhado, com uma só inclinação para os três ciclos, mistura com o estrato. Em cada ciclo, * marca a menor inclinação.

| estrato | ciclo 1 | ciclo 2 | ciclo 3 | fração no ciclo 3 | coef. ciclo 1 | coef. ciclo 2 | coef. ciclo 3 |
|---|---:|---:|---:|---:|---:|---:|---:|
| capital | 73 | 714 | 985 | 0,556 | 0,0292* | 0,0933* | −0,0615* |
| interior_proximo_polo | 510 | 665 | 746 | 0,388 | 0,0537 | 0,1249 | 0,0355 |
| interior_remoto | 84 | 135 | 214 | 0,494 | 0,0453 | 0,1331 | −0,0031 |
| metropolitano | 326 | 626 | 636 | 0,401 | 0,0998 | 0,1575 | 0,0788 |

**Tabela X4.5. Adição pós-auditoria (fora do doc 45 e do BKY): empilhado com inclinação da bolsa própria de cada ciclo (estrato de base, capital) e diferenças por estrato comuns aos ciclos.** IC e p com cluster por conjunto; p do score bootstrap com cluster por conjunto e por curso.

| termo | coef. | IC 95% | p | p score (conjunto) | p score (curso) |
|---|---:|---|---:|---:|---:|
| capital, ciclo 1 | −0,0522 | [−0,1049; 0,0005] | 0,052 | — | — |
| capital, ciclo 2 | 0,0360 | [−0,0191; 0,0910] | 0,200 | — | — |
| capital, ciclo 3 | −0,0064 | [−0,0662; 0,0533] | 0,833 | — | — |
| bolsa_x_interior_proximo_polo | 0,0720 | [0,0316; 0,1125] | < 0,001 | < 0,001 | 0,002 |
| bolsa_x_interior_remoto | 0,0586 | [0,0110; 0,1063] | 0,016 | 0,009 | 0,016 |
| bolsa_x_metropolitano | 0,1070 | [0,0547; 0,1594] | < 0,001 | < 0,001 | < 0,001 |
| Wald (χ², 3 gl) = 18,44 | — | — | < 0,001 | — | — |

**Tabela X4.6. Cursos sem ponte curso → CBO (grupo sem_ponte_curso_cbo da escassez) e curso de menor inclinação no ciclo 3 (Tabela X4.1).**

| cursos sem ponte | curso de menor inclinação no ciclo 3 |
|---|---|
| 17, 18, 19, 20, 21, 22, 23, 24 | curso24 |

<!-- X4_TABELAS_FIM -->

### Leitura

- **Nota do candidato:** dentro de cada ciclo, nenhum tercil difere do tercil 1
  com q < 0,05, e o Wald da igualdade não rejeita com q < 0,05 em nenhum ciclo.
  No empilhado, o Wald rejeita, mas por causa do grupo sem pontuação, que só
  existe no ciclo 1. No empilhado, esse grupo é comparado a um tercil 1 que
  junta os três ciclos; dentro do ciclo 1, a diferença não tem q < 0,05. Não
  há evidência de que candidatos de nota alta e baixa respondam à bolsa de
  forma diferente. Por causa dos empates, o tercil 2 é o menor nos ciclos 2 e
  3 (Tabela X4.3).
- **Escassez:** entre os tercis, nenhuma interação tem q < 0,05. O Wald só
  rejeita com q < 0,05 no ciclo 1, e com o tercil do meio abaixo dos outros dois: um padrão
  não monotônico, que não sustenta "a bolsa pesa mais onde a especialidade é
  mais escassa". O grupo sem ponte (cursos novos do ciclo 3, Tabela X4.6)
  responde menos que o tercil 1, com q < 0,05. Isso é diferença entre cursos,
  não entre níveis de escassez: o curso de menor inclinação no ciclo 3 é um dos
  cursos sem ponte (Tabela X4.6), e a inclinação dele é negativa também pelo EP
  de MV.
- **Estrato:** no ciclo 3 e no empilhado, o Wald rejeita a igualdade com
  q < 0,05. No empilhado, todas as interações são positivas: a capital
  responde menos que os outros estratos, e a inclinação da capital tem IC 95%
  que inclui zero. Parte disso é composição: o empilhado tem uma só inclinação
  da bolsa para os três ciclos, e a capital é o estrato com a maior fração de
  candidatos no ciclo 3, o ciclo de menor resposta (Tabela X4.4). Por ciclo, a
  capital tem a menor inclinação nos três ciclos (Tabela X4.4), mas a diferença
  só tem q < 0,05 no ciclo 3; nos ciclos 1 e 2 não há rejeição. Na adição
  pós-auditoria, com inclinação própria de cada ciclo e diferenças por estrato
  comuns aos ciclos (Tabela X4.5, fora do doc 45 e do BKY), as três diferenças
  continuam positivas, com IC 95% acima de zero e p do score bootstrap abaixo
  de 0,05 por conjunto e por curso. A composição por ciclo não explica sozinha
  a diferença; como ela só é significativa dentro do ciclo 3, a leitura é de
  um padrão concentrado nesse ciclo. O estrato não é aleatório e anda junto com
  outros atributos da célula; a diferença é descritiva da escolha.
- **Ciclo 2:** a inclinação é positiva, com IC 95% acima de zero, em todos os
  grupos de nota, escassez e estrato. A resposta do ciclo 2 não vem de um grupo
  só.
- **Curso:** pelo EP de MV, o Wald entre cursos rejeita nos ciclos 2, 3 e
  empilhado, e não no ciclo 1. O E9 mostrou que o EP de MV ignora o choque
  comum dentro do conjunto e subestima a incerteza; nos termos próprios de
  curso, o EP por cluster fica ainda menor que o de MV, o que é sintoma da
  degeneração, não precisão. A heterogeneidade entre cursos é descritiva.
- **Para as propostas do doc 44 (§7):** a resposta não se concentra em
  candidatos de nota alta ou baixa nem nos municípios de especialidade mais
  escassa. Dentro de ciclo, fora da dimensão curso, as linhas com q < 0,05 são
  só três grupos de achados: a menor resposta das capitais no ciclo 3, o padrão
  não monotônico da escassez no ciclo 1 e a menor resposta dos cursos sem ponte
  no ciclo 3. A das capitais é compatível com a leitura B (atributos não
  pecuniários pesam mais em algumas células), mas não a distingue de outras
  explicações.

### Desvios e limites

- **Cursos sem ponte curso–CBO (Tabela X4.6):** sem escassez calculada; grupo
  próprio, sem imputação.
- **Grupo sem pontuação:** existe só no ciclo 1; no empilhado, a comparação
  mistura grupo e ciclo.
- **Tercis com empate:** pontuações discretas fazem tercis desiguais; a regra
  (empate para baixo) foi fixada antes da estimação.
- **Curso:** inferência por cluster degenerada (acima); fora do BKY. Nas
  Tabelas X4.1 e X4.2, as linhas de curso trazem IC e p de MV, marcados na
  coluna inferência.
- **Adição pós-auditoria:** a Tabela X4.5 (linhas com
  `adicao_pos_auditoria = True`) foi pedida pela auditoria independente de
  X4/X5 depois de ver os resultados; não substitui as especificações do doc 45.
- **Limites do E9 valem aqui:** IIA, atributos não observados, seleção para
  candidatar-se e escolha estratégica.

## X5 — Deslocamento regional

> **Data:** 19/10/2026.<br>
> **Estatuto:** `EXPLORATORIO_POS_SINTESE` (protocolo
> [`45`](45_protocolo_exploratorio_pos_sintese.md), §2 e §3).<br>
> **Script:** `scripts/rdd_bolsa/19_escolha_heterogeneidade.py`.<br>
> **Região de saúde:** tabela oficial de conversão município → Região de Saúde
> (CIR) do TabNet/DATASUS (`territorio/br_regsaud.cnv`), baixada com
> `--baixar-regioes` para `data/raw/aquisicao/territorio/datasus_tabnet_br_regsaud.cnv`;
> URL, data e SHA-256 em `output/rdd_bolsa/X5_manifesto_regioes_saude_cir.json`.
> O TabNet não serviu o arquivo por HTTPS e ele veio por HTTP; a integridade é
> conferida pelo SHA-256 do manifesto a cada execução (o script para se o
> arquivo mudar).<br>
> **Saídas:** `output/rdd_bolsa/X5_estimativas.csv`, `X4X5_resumo.json` e
> `X4X5_tabelas_relato.md`.<br>
> **Testes:** `tests/test_x4_x5_escolha.py` (recuperação do efeito de
> vizinhança e de lambda em dados sintéticos; identidade do aninhado com
> lambda = 1 e do condicional; invariantes; blocos e frases conferidos).

Nenhum número desta seção foi digitado: as tabelas são o bloco X5 de
`output/rdd_bolsa/X4X5_tabelas_relato.md`, conferido por teste.

### Especificação

- **Por que não a malha do repositório:** a região de saúde de
  `malha_municipios_regioes_saude.parquet` vem da série e da lista nominal do
  PMM-E, e só existe nos municípios com ativo do programa. Usá-la condicionaria
  a amostra a um resultado pós-tratamento. A malha fica como conferência: nos
  municípios em que as duas fontes têm região, a partição da malha coincide com
  a da CIR oficial (`conferencias.cir_contra_malha` no resumo).
- **Município sem CIR oficial:** um município do quadro não está na tabela do
  TabNet. Suas células e os candidatos que as escolheram saem do X5, sem
  imputação (Tabela X5.3); o principal do E9 é reestimado nessa amostra
  (linhas `sem_vizinhanca`).
- **(i) Logit aninhado:** ninhos = CIR dentro do curso × ciclo, um lambda comum,
  por máxima verossimilhança própria (quase-Newton e polimento por Newton com
  hessiana numérica), iniciado no condicional (lambda = 1). Lambda = 1 é o logit
  condicional; lambda < 1 quer dizer escolhas mais correlacionadas dentro da
  CIR, isto é, mais substituição entre células da mesma região. Relatam-se
  lambda, a bolsa, o Wald de lambda = 1 (cluster por conjunto) e a razão de
  verossimilhança contra o condicional.
- **(ii) Atributos de vizinhança** no logit condicional: número de outras
  células da mesma CIR e do mesmo conjunto com bolsa maior (como no doc 45);
  variante com o total de outras células da CIR no conjunto, para separar ter
  vizinhos de ter vizinhos de bolsa maior; variante com a fração de vizinhos de
  bolsa maior (zero sem vizinho, sempre com o indicador de ter vizinho). A
  proposta A prevê coeficiente negativo.
- **Inferência:** como no X4. q de BKY dentro do X5, sobre os termos de
  vizinhança e o Wald de lambda = 1.

### Resultados

<!-- X5_TABELAS_INICIO -->
<!-- gerado por scripts/rdd_bolsa/19_escolha_heterogeneidade.py; não editar à mão -->

**Tabela X5.1. Bolsa com e sem termos de vizinhança, termos de vizinhança e logit aninhado por região de saúde (CIR).** Amostra do X5 (sem células de município sem CIR oficial). EP e IC 95% com cluster por conjunto; p pela normal; p do score bootstrap Rademacher (cluster por conjunto) nos termos de vizinhança. Na linha lambda − 1, o p é o do Wald de H0: lambda = 1. q de BKY dentro do X5.

| ciclo | especificação | termo | coef. | IC 95% | p | p score (conjunto) | q BKY |
|---|---|---|---:|---|---:|---:|---:|
| 1 | sem_vizinhanca | bolsa_mil | 0,0663 | [−0,0197; 0,1524] | 0,131 | — | — |
| 1 | vizinhos_contagem | bolsa_mil | 0,0623 | [−0,0230; 0,1476] | 0,152 | — | — |
| 1 | vizinhos_contagem | n_vizinhos_bolsa_maior | −0,3873 | [−0,7816; 0,0071] | 0,054 | 0,033 | 0,134 |
| 1 | vizinhos_contagem_e_total | bolsa_mil | 0,0690 | [−0,0131; 0,1511] | 0,100 | — | — |
| 1 | vizinhos_contagem_e_total | n_vizinhos_bolsa_maior | −0,0165 | [−0,3220; 0,2890] | 0,916 | 0,938 | 0,578 |
| 1 | vizinhos_fracao | bolsa_mil | 0,0610 | [−0,0194; 0,1414] | 0,137 | — | — |
| 1 | vizinhos_fracao | fracao_vizinhos_bolsa_maior | −0,2547 | [−0,6208; 0,1114] | 0,173 | 0,206 | 0,238 |
| 1 | aninhado_cir | bolsa_mil | 0,0547 | [−0,0239; 0,1333] | 0,173 | — | — |
| 1 | aninhado_cir | lambda | 0,5633 | [0,4193; 0,7072] | — | — | — |
| 1 | aninhado_cir | lambda_menos_1 | −0,4367 | [−0,5807; −0,2928] | < 0,001 | — | 0,001 |
| 2 | sem_vizinhanca | bolsa_mil | 0,1328 | [0,0778; 0,1878] | < 0,001 | — | — |
| 2 | vizinhos_contagem | bolsa_mil | 0,1328 | [0,0778; 0,1879] | < 0,001 | — | — |
| 2 | vizinhos_contagem | n_vizinhos_bolsa_maior | −0,0183 | [−0,2564; 0,2198] | 0,880 | 0,852 | 0,578 |
| 2 | vizinhos_contagem_e_total | bolsa_mil | 0,1479 | [0,0913; 0,2045] | < 0,001 | — | — |
| 2 | vizinhos_contagem_e_total | n_vizinhos_bolsa_maior | 0,1837 | [−0,1085; 0,4759] | 0,218 | 0,373 | 0,279 |
| 2 | vizinhos_fracao | bolsa_mil | 0,1491 | [0,0884; 0,2099] | < 0,001 | — | — |
| 2 | vizinhos_fracao | fracao_vizinhos_bolsa_maior | 0,3846 | [−0,1620; 0,9311] | 0,168 | 0,385 | 0,238 |
| 2 | aninhado_cir | bolsa_mil | 0,1323 | [0,0806; 0,1839] | < 0,001 | — | — |
| 2 | aninhado_cir | lambda | 0,7497 | [0,6860; 0,8134] | — | — | — |
| 2 | aninhado_cir | lambda_menos_1 | −0,2503 | [−0,3140; −0,1866] | < 0,001 | — | 0,001 |
| 3 | sem_vizinhanca | bolsa_mil | 0,0095 | [−0,0527; 0,0716] | 0,766 | — | — |
| 3 | vizinhos_contagem | bolsa_mil | 0,0134 | [−0,0556; 0,0824] | 0,703 | — | — |
| 3 | vizinhos_contagem | n_vizinhos_bolsa_maior | −0,0420 | [−0,0920; 0,0080] | 0,100 | 0,345 | 0,170 |
| 3 | vizinhos_contagem_e_total | bolsa_mil | 0,0131 | [−0,0426; 0,0688] | 0,644 | — | — |
| 3 | vizinhos_contagem_e_total | n_vizinhos_bolsa_maior | −0,0428 | [−0,1423; 0,0567] | 0,399 | 0,853 | 0,444 |
| 3 | vizinhos_fracao | bolsa_mil | 0,0188 | [−0,0358; 0,0734] | 0,499 | — | — |
| 3 | vizinhos_fracao | fracao_vizinhos_bolsa_maior | 0,0219 | [−0,3255; 0,3693] | 0,902 | 0,912 | 0,578 |
| 3 | aninhado_cir | bolsa_mil | 0,0256 | [−0,0283; 0,0795] | 0,351 | — | — |
| 3 | aninhado_cir | lambda | 0,8520 | [0,7179; 0,9862] | — | — | — |
| 3 | aninhado_cir | lambda_menos_1 | −0,1480 | [−0,2821; −0,0138] | 0,031 | — | 0,111 |
| empilhado | sem_vizinhanca | bolsa_mil | 0,0661 | [0,0227; 0,1095] | 0,003 | — | — |
| empilhado | vizinhos_contagem | bolsa_mil | 0,0686 | [0,0248; 0,1124] | 0,002 | — | — |
| empilhado | vizinhos_contagem | n_vizinhos_bolsa_maior | −0,0477 | [−0,0955; 0,0001] | 0,051 | 0,188 | 0,134 |
| empilhado | vizinhos_contagem_e_total | bolsa_mil | 0,0766 | [0,0327; 0,1206] | < 0,001 | — | — |
| empilhado | vizinhos_contagem_e_total | n_vizinhos_bolsa_maior | 0,0008 | [−0,1272; 0,1288] | 0,990 | 0,996 | 0,591 |
| empilhado | vizinhos_fracao | bolsa_mil | 0,0752 | [0,0313; 0,1190] | < 0,001 | — | — |
| empilhado | vizinhos_fracao | fracao_vizinhos_bolsa_maior | 0,1145 | [−0,1816; 0,4106] | 0,449 | 0,489 | 0,444 |
| empilhado | aninhado_cir | bolsa_mil | 0,0745 | [0,0348; 0,1142] | < 0,001 | — | — |
| empilhado | aninhado_cir | lambda | 0,7563 | [0,6474; 0,8653] | — | — | — |
| empilhado | aninhado_cir | lambda_menos_1 | −0,2437 | [−0,3526; −0,1347] | < 0,001 | — | 0,001 |

**Tabela X5.2. Amostra, ninhos e convergência do logit aninhado.**

| ciclo | candidatos | células | células com vizinho na CIR | ninhos | ninhos de uma célula | lambda no limite | convergiu | LR contra o condicional | p LR |
|---|---:|---:|---:|---:|---:|---|---|---:|---:|
| 1 | 990 | 1289 | 416 | 1044 | 873 | não | sim | 41,78 | < 0,001 |
| 2 | 2140 | 1545 | 783 | 1032 | 762 | não | sim | 52,35 | < 0,001 |
| 3 | 2581 | 2291 | 1676 | 1098 | 615 | não | sim | 23,02 | < 0,001 |
| empilhado | 5711 | 5125 | 2875 | 3174 | 2250 | não | sim | 137,06 | < 0,001 |

**Tabela X5.3. Fora do X5 por falta de CIR oficial (sem imputação).**

| ciclo | células retiradas | candidatos de 1a opção retirados |
|---|---:|---:|
| 1 | 6 | 3 |
| 2 | 2 | 0 |
| 3 | 1 | 0 |

<!-- X5_TABELAS_FIM -->

### Leitura

- **Logit aninhado:** lambda fica abaixo de 1 em todos os ciclos, com IC 95%
  abaixo de 1. O Wald de lambda = 1 tem q < 0,05 nos ciclos 1, 2 e empilhado,
  e não no ciclo 3; a razão de verossimilhança rejeita o condicional em todos
  os ciclos. As 1as opções são mais correlacionadas dentro da região de saúde
  do que o logit condicional permite: o candidato troca mais facilmente uma
  célula por outra da mesma região. Esse padrão é o que a proposta A precisa
  para que uma bolsa maior tire candidatos sobretudo das vizinhas. Mas lambda
  não diz por quê: qualquer fator comum à região (a origem do candidato, que
  não é publicada, ou atributos regionais não observados) gera o mesmo padrão.
- **Bolsa:** o coeficiente muda pouco com os termos de vizinhança e no
  aninhado. Em cada ciclo, o IC 95% da bolsa exclui zero em todas as
  especificações ou em nenhuma, como no E9: as conclusões do E9 por ciclo não
  mudam.
- **Vizinhança:** nenhum termo tem q < 0,05. A contagem de vizinhos de bolsa
  maior, sozinha, tem coeficiente negativo em todos os ciclos; com o total de
  outras células da região no modelo, ela fica perto de zero, com IC 95% que
  inclui zero. O sinal da contagem sozinha acompanha o número de vizinhas, e
  não o fato de elas pagarem mais. A fração de vizinhos de bolsa
  maior também tem IC 95% que inclui zero em todos os ciclos.
- **Para a proposta A:** a forma (ii) não encontra deslocamento específico
  para vizinhas de bolsa menor, além da substituição proporcional do logit. A
  forma (i) mostra substituição concentrada na região, de natureza não
  identificada. Os dados de escolha são compatíveis com realocação regional,
  mas não a demonstram.

### Desvios e limites

- **Fonte da região de saúde:** CIR oficial do TabNet em vez da malha indicada
  na tarefa (motivo acima); download público, permitido pelo §2 do doc 45. É a
  base territorial corrente do TabNet, não uma competência do CNES.
- **Município sem CIR:** fora do X5, com contagem; nada imputado.
- **Ninhos de uma célula:** muitos (Tabela X5.2); lambda é identificado pelos
  ninhos com mais de uma célula.
- **Sem residência do candidato:** a distância e a região de origem não entram;
  lambda < 1 pode refletir preferência pela região de origem.
- **IIA dentro do ninho e um lambda comum** a todos os ninhos, cursos e
  ciclos.

## X6 — Poder e o que se descarta

> **Protocolo:** [`45_protocolo_exploratorio_pos_sintese.md`](45_protocolo_exploratorio_pos_sintese.md), §3 X6,
> congelado em 19/10/2026.<br>
> **Estatuto:** exploratório e pós-resultado (`estatuto = EXPLORATORIO_POS_SINTESE`). Não muda o protocolo 40, os
> resultados E3–E9 nem o Holm das primárias.<br>
> **Script:** `scripts/rdd_bolsa/20_poder_descartes.py`. Nenhuma estimação nova: só aritmética sobre o EP, o IC e as
> médias já publicados no E6, E7, E8 e E9.<br>
> **Saídas:** `output/rdd_bolsa/X6_poder_descartes.csv`, `output/rdd_bolsa/X6_resumo.json` (natureza dos dados:
> **EMPIRICO**; entradas com SHA-256) e `output/rdd_bolsa/X6_figuras/X6_descartes.png`.<br>
> **Testes:** `tests/test_x6_poder.py`. Todo número desta seção está entre marcadores `<!-- X6:... -->`, gerados
> só a partir das saídas do X6 por `python3 scripts/rdd_bolsa/20_poder_descartes.py --atualizar-doc`; o teste
> confere os blocos e que a prosa fora deles só tem parâmetros.

### X6.1 Pergunta e definições

A síntese (doc 44) relata IC, mas não uma tabela de poder comparável entre outcomes. Para cada linha principal do
E6 (P1 e F0–F4, cada corte e empilhado, ciclos empilhados onde definidos, mais o Poisson local de F1.1), do E7
(DiRD da família F3) e do E9 (coeficiente da bolsa, por ciclo e empilhado), o X6 calcula:

- **MDE de 80%:** o menor salto que o desenho detecta com 80% de poder num teste bicaudal a 5%, 2,8 × EP (a
  convenção do E5). Na razão de chances, é a exponencial de 2,8 × EP do log;
- **o que o IC 95% convencional descarta**, em termos absolutos e relativos à média abaixo do corte na janela. Nas
  linhas empilhadas, a base é a média das médias abaixo de cada grupo ponderada pelos mesmos pesos que definem o
  estimando empilhado. No E7, a base é a média do pré abaixo do corte, como no doc 44;
- **equivalência (adicional ao doc 45):** a menor margem simétrica δ tal que o IC 90% fica dentro de [−δ, +δ]; para
  toda margem maior que δ, o TOST a 5% declara o efeito equivalente a zero;
- **comparação** com as referências do protocolo 40 (+10 p.p. de preenchimento, +25% de candidaturas) e com
  magnitudes da literatura lidas do doc 20 da seção 03;
- **se o IC honesto é informativo (critério adicional ao doc 45):** se, com o M do protocolo, ele exclui a
  referência, uma magnitude da literatura aplicável, ou fica dentro de ±100% da base;
- **elasticidades implícitas da escolha (linhas adicionais ao doc 45):** no E9, a variação relativa média da
  probabilidade dividida pelo degrau relativo da bolsa em cada corte, em duas versões: com base na bolsa menor e na
  probabilidade inicial (não é arco) e a elasticidade-arco de ponto médio, com bolsa e probabilidade no ponto médio.

As três adições levam `ESPECIFICACAO_ADICIONAL` na coluna `especificacao_adicional_doc45` do CSV e no resumo.

**Contraste.** E6: pacote do corte (bolsa anunciada e outras regras federais nos mesmos cortes). E7: bolsa mais a
variação das co-políticas. E9: degrau da bolsa na repartição da 1ª opção entre células, não no total de
candidatos. Nenhum é efeito da participação no PMM-E nem do Agora Tem Especialistas.

**Como ler.** "Descartar" quer dizer que o limite do IC fica do outro lado da magnitude, sob o IC convencional e a
aproximação local linear. Um IC que descarta +10 p.p. porque a estimativa pontual é negativa não equivale a um
desenho com poder contra +10 p.p.: a coluna do MDE separa as duas coisas.

### X6.2 Poder e descartes nas linhas que a síntese lê

Linhas empilhadas (cortes e ciclos) e o E9. A tabela completa, com cada corte e cada ciclo, está no CSV.

<!-- X6:tabela_poder:inicio -->
| Outcome | Pop. | Ciclo | Contraste | Salto | EP | MDE 80% | IC 95% | Média abaixo | IC 95% relativo | MDE relativo | δ TOST (abs.; rel.) [adicional] | IC honesto informativo? [adicional] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1.1 candidatos de 1ª opção por célula | V1+V2+V3 | 1+2+3 | pacote (nível) | +0,063 | 0,293 | 0,819 | [−0,511; +0,636] | 0,940 | [−54 %; +68 %] | 87 % | 0,544; 58 % | não |
| F1.2 células com candidato | V1+V2+V3 | 1+2+3 | pacote (nível) | −7,0 p.p. | 6,1 p.p. | 17,0 p.p. | [−18,9 p.p.; +4,9 p.p.] | 54,9 p.p. | [−34 %; +9 %] | 31 % | 17,0 p.p.; 31 % | não |
| F1.3 preenchidas na 1ª chamada | V1+V2+V3 | 1+2+3 | pacote (nível) | −7,3 p.p. | 5,4 p.p. | 15,2 p.p. | [−17,9 p.p.; +3,4 p.p.] | 29,0 p.p. | [−62 %; +12 %] | 52 % | 16,2 p.p.; 56 % | não |
| F1.4 preenchidas até a 2ª chamada | V1+V2 | 1+2 | pacote (nível) | −8,0 p.p. | 8,0 p.p. | 22,3 p.p. | [−23,6 p.p.; +7,6 p.p.] | 48,9 p.p. | [−48 %; +15 %] | 46 % | 21,1 p.p.; 43 % | não |
| F2.1 ativos por célula | V1+V2 | 1+2 | pacote (nível) | −0,136 | 0,181 | 0,507 | [−0,491; +0,218] | 0,490 | [−100 %; +45 %] | 103 % | 0,434; 89 % | não |
| F2.2 ativos por 10 mil hab. | U | 1 | pacote (nível) | −0,008 | 0,030 | 0,085 | [−0,068; +0,051] | 0,018 | [−385 %; +291 %] | 483 % | 0,058; 330 % | não |
| F2.2 ativos por 10 mil hab. | U | 2 | pacote (nível) | −0,079 | 0,082 | 0,229 | [−0,239; +0,081] | 0,039 | [−610 %; +207 %] | 584 % | 0,214; 545 % | não |
| F2.3 algum ativo do ciclo | V1+V2 | 1+2 | pacote (nível) | −5,2 p.p. | 10,1 p.p. | 28,3 p.p. | [−25,0 p.p.; +14,7 p.p.] | 58,6 p.p. | [−43 %; +25 %] | 48 % | 21,8 p.p.; 37 % | não |
| F4.1 nota dos alocados | V1+V2+V3 | 1+2+3 | pacote (nível) | −0,40 | 0,28 | 0,78 | [−0,94; +0,15] | 5,72 | [−16 %; +3 %] | 14 % | 0,85; 15 % | não |
| F4.2 nota dos candidatos | V1+V2+V3 | 1+2+3 | pacote (nível) | −0,45 | 0,21 | 0,60 | [−0,87; −0,03] | 5,38 | [−16 %; −1 %] | 11 % | 0,81; 15 % | não |
| P1 índice atração-presença | V1+V2+V3 | 1+2+3 | pacote (nível) | −0,13 DP | 0,16 DP | 0,45 DP | [−0,44 DP; +0,19 DP] | — | — | — | 0,39 DP; — | — |
| F3.1 vínculos CBO-alvo / 10 mil | U | pós | DiRD | +0,083 | 0,200 | 0,561 | [−0,309; +0,476] | 8,622 | [−4 %; +6 %] | 7 % | 0,413; 5 % | não |
| F3.1 vínculos CBO-alvo / 10 mil | V1 | pós | DiRD | −1,234 | 0,854 | 2,391 | [−2,907; +0,439] | 18,749 | [−16 %; +2 %] | 13 % | 2,638; 14 % | não |
| F3.2 tem especialista CBO-alvo | U | pós | DiRD | −2,5 p.p. | 1,8 p.p. | 4,9 p.p. | [−5,9 p.p.; +1,0 p.p.] | 84,9 p.p. | [−7 %; +1 %] | 6 % | 5,4 p.p.; 6 % | não |
| F3.3 horas SUS CBO-alvo / 10 mil | U | pós | DiRD | −2,04 | 2,22 | 6,21 | [−6,38; +2,31] | 72,13 | [−9 %; +3 %] | 9 % | 5,68; 8 % | não |
| F3.P1 placebo generalistas | U | pós | DiRD | −0,088 | 0,562 | 1,575 | [−1,190; +1,014] | 19,347 | [−6 %; +5 %] | 8 % | 1,013; 5 % | não |
| F3.P2 placebo não-alvo | U | pós | DiRD | −0,059 | 0,217 | 0,609 | [−0,485; +0,367] | 9,053 | [−5 %; +4 %] | 7 % | 0,417; 5 % | não |
| E9 escolha da 1ª opção (RC por +R$ 5 mil) | candidatos de 1ª opção | 1 | degrau na escolha | 1,39 | — | 1,85 | [0,90; 2,13] | 1,137 p.p. (prob. base) | [−20 %; +95 %] (Δ prob.) | 82 % (Δ prob.) | RC em [0,50; 1,99]; 86 % (Δ prob.) | — (sem IC honesto) |
| E9 escolha da 1ª opção (RC por +R$ 5 mil) | candidatos de 1ª opção | 2 | degrau na escolha | 1,95 | — | 1,48 | [1,48; 2,57] | 0,539 p.p. (prob. base) | [+40 %; +143 %] (Δ prob.) | 74 % (Δ prob.) | RC em [0,41; 2,45]; 135 % (Δ prob.) | — (sem IC honesto) |
| E9 escolha da 1ª opção (RC por +R$ 5 mil) | candidatos de 1ª opção | 3 | degrau na escolha | 1,05 | — | 1,56 | [0,77; 1,43] | 0,527 p.p. (prob. base) | [−27 %; +37 %] (Δ prob.) | 46 % (Δ prob.) | RC em [0,73; 1,36]; 32 % (Δ prob.) | — (sem IC honesto) |
| E9 escolha da 1ª opção (RC por +R$ 5 mil) | candidatos de 1ª opção | empilhado | degrau na escolha | 1,39 | — | 1,36 | [1,12; 1,73] | 0,586 p.p. (prob. base) | [+9 %; +68 %] (Δ prob.) | 42 % (Δ prob.) | RC em [0,60; 1,67]; 63 % (Δ prob.) | — (sem IC honesto) |
<!-- X6:tabela_poder:fim -->

### X6.3 Referências do protocolo

<!-- X6:referencias_protocolo:inicio -->
| Outcome | Pop. | Ciclo | Corte | Escala | EP | MDE 80% | IC 95% (sup.) | δ TOST | Referência | IC exclui? | MDE < ref.? | TOST dentro? [adicional] | IC honesto exclui? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F1.3 | V1+V2+V3 | 1+2+3 | empilhado | p.p. | 5,4 p.p. | 15,2 p.p. | +3,4 p.p. | 16,2 p.p. | +10 p.p. | sim | não | não | não |
| F1.3 | V1 | 1 | empilhado | p.p. | 11,5 p.p. | 32,3 p.p. | +14,0 p.p. | 27,6 p.p. | +10 p.p. | não | não | não | não |
| F1.3 | V2 | 2 | empilhado | p.p. | 9,9 p.p. | 27,7 p.p. | +14,1 p.p. | 21,7 p.p. | +10 p.p. | não | não | não | não |
| F1.3 | V3 | 3 | empilhado | p.p. | 6,4 p.p. | 17,9 p.p. | +4,7 p.p. | 18,3 p.p. | +10 p.p. | sim | não | não | não |
| F1.4 | V1+V2 | 1+2 | empilhado | p.p. | 8,0 p.p. | 22,3 p.p. | +7,6 p.p. | 21,1 p.p. | +10 p.p. | sim | não | não | não |
| F1.4 | V1 | 1 | empilhado | p.p. | 11,6 p.p. | 32,4 p.p. | +14,4 p.p. | 27,3 p.p. | +10 p.p. | não | não | não | não |
| F1.4 | V2 | 2 | empilhado | p.p. | 9,8 p.p. | 27,4 p.p. | +11,4 p.p. | 23,9 p.p. | +10 p.p. | não | não | não | não |
| F1.1 | V1+V2+V3 | 1+2+3 | empilhado | relativa (linear / média abaixo) | 31 % | 87 % | +68 % | 58 % | +25 % | não | não | não | não |
| F1.1 | V1 | 1 | empilhado | relativa (linear / média abaixo) | 66 % | 185 % | +136 % | 115 % | +25 % | não | não | não | não |
| F1.1 | V2 | 2 | empilhado | relativa (linear / média abaixo) | 48 % | 135 % | +82 % | 92 % | +25 % | não | não | não | não |
| F1.1 | V3 | 3 | empilhado | relativa (linear / média abaixo) | 39 % | 108 % | +99 % | 87 % | +25 % | não | não | não | não |
| F1.1 | V1 | 1 | 0,300 | relativa (Poisson) | 0,596 | 431 % | +61 % | 434 % | +25 % | não | não | não | — |
| F1.1 | V1 | 1 | 0,400 | relativa (Poisson) | 0,720 | 651 % | +718 % | 552 % | +25 % | não | não | não | — |
| F1.1 | V2 | 2 | 0,300 | relativa (Poisson) | 0,380 | 190 % | +0 % | 292 % | +25 % | sim | não | não | — |
| F1.1 | V2 | 2 | 0,400 | relativa (Poisson) | 0,372 | 184 % | +105 % | 87 % | +25 % | não | não | não | — |
| F1.1 | V3 | 3 | 0,300 | relativa (Poisson) | 0,323 | 147 % | +9 % | 193 % | +25 % | sim | não | não | — |
| F1.1 | V3 | 3 | 0,400 | relativa (Poisson) | 0,336 | 156 % | +82 % | 84 % | +25 % | não | não | não | — |
<!-- X6:referencias_protocolo:fim -->

### X6.4 Magnitudes da literatura

A comparação é de ordem de grandeza. Outcome, população e degrau diferem (doc 44, §6): a aceitação de Dal Bó, Finan
e Rossi é de servidores públicos sorteados para um salário maior; o número de Bobba et al. é uma estimativa não
significativa; o líquido de Hone et al. é do Mais Médicos inteiro, sobre generalistas. A elasticidade do E9 é da
repartição da 1ª opção entre células, não do tamanho do pool; as duas versões (base na bolsa menor e arco de ponto
médio) são adicionais ao doc 45 e aparecem lado a lado.

<!-- X6:literatura:inicio -->
| Outcome | Pop. | Ciclo / corte | Estimativa [IC 95%] | MDE 80% | Magnitude da literatura (doc 20) | IC 95% | MDE < magnitude? | IC honesto |
|---|---|---|---|---|---|---|---|---|
| F1.1 | V1+V2+V3 | 1+2+3 / empilhado | +7 % [−54 %; +68 %] | 87 % | Dal Bó, Finan & Rossi (2013): +26 % | não descarta | não | não descarta |
| F1.3 | V1+V2+V3 | 1+2+3 / empilhado | −7,3 p.p. [−17,9 p.p.; +3,4 p.p.] | 15,2 p.p. | Dal Bó, Finan & Rossi (2013): +15,1 p.p. | descarta (IC abaixo) | não | não descarta |
| F1.3 | V1+V2+V3 | 1+2+3 / empilhado | −7,3 p.p. [−17,9 p.p.; +3,4 p.p.] | 15,2 p.p. | Bobba et al. (NBER 2021, rev. 2026): +6,3 p.p. | descarta (IC abaixo) | não | não descarta |
| F1.4 | V1+V2 | 1+2 / empilhado | −8,0 p.p. [−23,6 p.p.; +7,6 p.p.] | 22,3 p.p. | Dal Bó, Finan & Rossi (2013): +15,1 p.p. | descarta (IC abaixo) | não | não descarta |
| F1.4 | V1+V2 | 1+2 / empilhado | −8,0 p.p. [−23,6 p.p.; +7,6 p.p.] | 22,3 p.p. | Bobba et al. (NBER 2021, rev. 2026): +6,3 p.p. | não descarta | não | não descarta |
| F1.1 (Poisson) | V1 | 1 / 0,300 | −50 % [−84 %; +61 %] | 431 % | Dal Bó, Finan & Rossi (2013): +26 % | não descarta | não | — |
| F1.1 (Poisson) | V1 | 1 / 0,400 | +100 % [−51 %; +718 %] | 651 % | Dal Bó, Finan & Rossi (2013): +26 % | não descarta | não | — |
| F1.1 (Poisson) | V2 | 2 / 0,300 | −52 % [−77 %; +0 %] | 190 % | Dal Bó, Finan & Rossi (2013): +26 % | descarta (IC abaixo) | não | — |
| F1.1 (Poisson) | V2 | 2 / 0,400 | −1 % [−52 %; +105 %] | 184 % | Dal Bó, Finan & Rossi (2013): +26 % | não descarta | não | — |
| F1.1 (Poisson) | V3 | 3 / 0,300 | −42 % [−69 %; +9 %] | 147 % | Dal Bó, Finan & Rossi (2013): +26 % | descarta (IC abaixo) | não | — |
| F1.1 (Poisson) | V3 | 3 / 0,400 | −6 % [−51 %; +82 %] | 156 % | Dal Bó, Finan & Rossi (2013): +26 % | não descarta | não | — |
| F3.1 | U | pós / empilhado | +0,083 [−0,309; +0,476] | 0,561 | Hone et al. (2020): +0,570 | descarta (IC abaixo) | sim | não descarta |
| F3.1 | V1 | pós / empilhado | −1,234 [−2,907; +0,439] | 2,391 | Hone et al. (2020): +0,570 | descarta (IC abaixo) | não | não descarta |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 1, degrau de 0,300 | +0,76 [−0,41; +1,93] | 1,67 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | descarta (IC abaixo) | sim | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 1, degrau de 0,300 | +0,76 [−0,41; +1,93] | 1,67 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 1, degrau de 0,300 | +0,80 [−0,57; +1,63] | 1,48 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | descarta (IC abaixo) | sim | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 1, degrau de 0,300 | +0,80 [−0,57; +1,63] | 1,48 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 1, degrau de 0,400 | +1,14 [−0,62; +2,90] | 2,51 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | não descarta | não | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 1, degrau de 0,400 | +1,14 [−0,62; +2,90] | 2,51 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 1, degrau de 0,400 | +1,12 [−0,80; +2,28] | 2,07 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | não descarta | não | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 1, degrau de 0,400 | +1,12 [−0,80; +2,28] | 2,07 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 2, degrau de 0,300 | +1,87 [+0,81; +2,93] | 1,51 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | não descarta | sim | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 2, degrau de 0,300 | +1,87 [+0,81; +2,93] | 1,51 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | descarta (IC acima) | não | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 2, degrau de 0,300 | +1,59 [+0,84; +2,11] | 0,88 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | não descarta | sim | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 2, degrau de 0,300 | +1,59 [+0,84; +2,11] | 0,88 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | descarta (IC acima) | não | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 2, degrau de 0,400 | +2,81 [+1,22; +4,40] | 2,27 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | não descarta | não | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 2, degrau de 0,400 | +2,81 [+1,22; +4,40] | 2,27 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | descarta (IC acima) | não | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 2, degrau de 0,400 | +2,23 [+1,18; +2,96] | 1,23 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | não descarta | sim | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 2, degrau de 0,400 | +2,23 [+1,18; +2,96] | 1,23 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | descarta (IC acima) | não | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 3, degrau de 0,300 | +0,10 [−0,55; +0,75] | 0,93 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | descarta (IC abaixo) | sim | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 3, degrau de 0,300 | +0,10 [−0,55; +0,75] | 0,93 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 3, degrau de 0,300 | +0,12 [−0,80; +0,79] | 1,11 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | descarta (IC abaixo) | sim | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 3, degrau de 0,300 | +0,12 [−0,80; +0,79] | 1,11 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 3, degrau de 0,400 | +0,15 [−0,83; +1,12] | 1,39 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | descarta (IC abaixo) | sim | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | ciclo 3, degrau de 0,400 | +0,15 [−0,83; +1,12] | 1,39 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 3, degrau de 0,400 | +0,17 [−1,12; +1,10] | 1,55 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | descarta (IC abaixo) | sim | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | ciclo 3, degrau de 0,400 | +0,17 [−1,12; +1,10] | 1,55 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | empilhado, degrau de 0,300 | +0,78 [+0,18; +1,38] | 0,86 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | descarta (IC abaixo) | sim | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | empilhado, degrau de 0,300 | +0,78 [+0,18; +1,38] | 0,86 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | empilhado, degrau de 0,300 | +0,81 [+0,21; +1,28] | 0,75 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | descarta (IC abaixo) | sim | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | empilhado, degrau de 0,300 | +0,81 [+0,21; +1,28] | 0,75 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | empilhado, degrau de 0,400 | +1,17 [+0,27; +2,07] | 1,28 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | não descarta | sim | — |
| E9 elasticidade (base na bolsa menor) | candidatos de 1a opcao | empilhado, degrau de 0,400 | +1,17 [+0,27; +2,07] | 1,28 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | empilhado, degrau de 0,400 | +1,14 [+0,30; +1,79] | 1,05 | Dal Bó, Finan & Rossi (2013): ≈ 2,00 | descarta (IC abaixo) | sim | — |
| E9 elasticidade-arco (ponto médio) | candidatos de 1a opcao | empilhado, degrau de 0,400 | +1,14 [+0,30; +1,79] | 1,05 | Costa, Nunes & Sanches (2024): 0,40 a 0,70 | não descarta | não | — |

Trechos copiados do doc 20 (o número de cada linha sai deste texto): Dal Bó, Finan & Rossi (2013): "aceitação +15,1 p.p."; Bobba et al. (NBER 2021, rev. 2026): "preenchimento (0,063, EP 0,048)"; Dal Bó, Finan & Rossi (2013): "candidaturas +26%"; Hone et al. (2020): "+15,1 médicos do programa por 100 mil habitantes, mas líquido de só +5,7"; Dal Bó, Finan & Rossi (2013): "elasticidade ≈ 2;"; Costa, Nunes & Sanches (2024): "elasticidade 0,4–0,7".
<!-- X6:literatura:fim -->

### X6.5 Contagens

<!-- X6:contagens:inicio -->
- Linhas no CSV: 210 (E6: 156; E7: 18; E9: 36).
- Linhas com referência do protocolo (F1.1, F1.3 e F1.4, por ciclo, por corte e empilhadas, mais o Poisson local de F1.1): 39. O IC 95% convencional exclui a referência em 11; o MDE de 80% fica abaixo dela em 0; o TOST declara equivalência dentro de ± a referência em 0; o IC honesto a exclui em 0.
- IC honesto: existe em 168 linhas. É informativo (critério na coluna `ic_honesto_criterios`) em 7, não informativo em 149 e não avaliável em 12 (índice P1: sem referência nem base). Entre as 60 linhas de fração com IC honesto, 56 cobrem todo salto logicamente possível ([−100 p.p.; +100 p.p.]).
- Bases relativas indisponíveis: 0.
<!-- X6:contagens:fim -->

### X6.6 Leitura

<!-- X6:leitura:inicio -->
- **Preenchimento na 1ª chamada (F1.3), ciclos e cortes empilhados:** MDE de 80% = 15,2 p.p., acima da referência do protocolo. O IC 95% convencional vai até +3,4 p.p. e exclui a referência, mas porque a estimativa pontual é negativa (−7,3 p.p.), não porque o desenho tenha poder de 80% contra ela. A equivalência a 5% só vale com margem de ±16,2 p.p. ou mais. A aceitação de Dal Bó, Finan e Rossi (+15,1 p.p.) fica acima do limite superior do IC 95% (descartada sob o IC convencional).
- **Por ciclo**, o MDE de F1.3 vai de 17,9 p.p. a 32,3 p.p.; 0 de 3 ciclos isolados têm poder de 80% contra a referência de preenchimento.
- **Candidaturas (F1.1), linear empilhado relativo à média abaixo:** MDE de 87 %; IC 95% relativo [−54 %; +68 %]. No Poisson local por ciclo e corte, o MDE relativo vai de 147 % a 651 %; 0 de 6 linhas têm poder de 80% contra a referência de candidaturas.
- **P1 (índice):** MDE de 0,45 DP; equivalência a 5% só com margem de ±0,39 DP ou mais.
- **P2 (F3.1 por DiRD em U, empilhado):** MDE de 0,561 vínculo por 10 mil hab., 6,5 % da média do pré abaixo do corte (8,622); IC 95% relativo [−3,6 %; +5,5 %]; IC honesto informativo: não.
- **Menor MDE relativo** entre as linhas empilhadas da tabela de X6.2: F3.2 tem especialista CBO-alvo (U, DiRD), 5,8 % da base.
- **E9 (escolha):** a menor razão de chances detectável com 80% de poder é 1,48 no ciclo 2 (estimada 1,95) e 1,36 no empilhado (estimada 1,39). A elasticidade-arco de ponto médio do ciclo 2 vai de 1,59 a 2,23 conforme o degrau do corte (com base na bolsa menor, de 1,87 a 2,81), contra 0,4 a 0,7 em Costa, Nunes e Sanches. 0 de 8 linhas de elasticidade-arco (e 0 de 8 com base na bolsa menor) têm MDE abaixo do limite inferior dessa faixa.
<!-- X6:leitura:fim -->

O que o X6 acrescenta à síntese, para as propostas A, B e C do doc 44 (§7):

<!-- X6:acrescenta:inicio -->
- **Proposta C (quanto e em que margem):** em 0 de 39 linhas com referência do protocolo o MDE de 80% fica abaixo da referência. Os nulos de preenchimento e candidaturas não são efeito zero: o desenho entre municípios não tem poder contra as magnitudes do protocolo, e o que se descarta vem do sinal das estimativas pontuais, sob o IC convencional.
- **IC honesto:** informativo em 7 de 156 linhas avaliáveis; a precisão relatada depende da aproximação local linear.
- **Propostas A e B:** o IC 95% da elasticidade-arco de ponto médio fica acima da faixa de Costa, Nunes e Sanches em 2 de 8 linhas, abaixo em 0 e a contém nas demais (com base na bolsa menor: acima em 2, abaixo em 0). Nenhuma linha tem MDE abaixo dessa faixa: um nulo da escolha não descarta elasticidades da ordem da literatura brasileira.
<!-- X6:acrescenta:fim -->

![X6: IC relativos à média abaixo do corte e elasticidades do E9](../../output/rdd_bolsa/X6_figuras/X6_descartes.png)
