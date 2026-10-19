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
