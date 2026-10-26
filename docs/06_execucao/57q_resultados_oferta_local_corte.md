# 57q. Resultados do protocolo 64: oferta local de especialistas comparada no corte

> **Data:** 2026-10-26.<br>
> **Protocolo:** [`64_protocolo_oferta_local_no_corte.md`](64_protocolo_oferta_local_no_corte.md), congelado antes de qualquer conta.<br>
> **Script:** `scripts/rdd_bolsa/43_oferta_local_corte.py`, com os outcomes e a amostra do script 37 (importados) e os estimadores de `scripts/rdd_bolsa/rdd_lib.py`.<br>
> **Saídas:** `output/rdd_bolsa/OC_estimativas.csv`, `OC_estudo_evento.csv`, `OC_resumo.json` e `OC_figuras/`; toda linha tem `natureza_dos_dados = EMPIRICO`.<br>
> **Testes:** `tests/test_oferta_local_corte.py`.<br>
> **Estatuto:** `PROTOCOLO_64_POS_RESULTADO`. O lado do corte de IVS decide a bolsa e também outras regras federais (auditoria 18): o contraste é o **pacote do corte**.<br>
> **Auditoria:** pendente.

Os blocos entre marcadores `<!-- OC:... -->` são gerados pelo script 43 a partir de `output/`
(`python3 scripts/rdd_bolsa/43_oferta_local_corte.py --atualizar-doc`). Não edite esses blocos à mão. Fora
deles, este texto não traz número de resultado.

## 1. O que se mede

**Pergunta.** Perto do corte de IVS, os municípios de cima e os de baixo mudaram a oferta cadastrada de
especialistas de forma diferente entre o pré e o pós? E, se o lado de cima recebe mais médicos do PMM-E, quanto
dessa diferença passa pelo médico do programa?

No doc 57k, quem recebeu médico foi comparado com quem ainda não tinha recebido, e o pré já subia. Aqui a
comparação é outra: o lado do corte. Perto do corte, os dois lados são parecidos antes do programa, e o lado
decide a bolsa.

- **Running variable:** IVS 2010 oficial do Ipea (a08). O arquivo local de IVS da auditoria 16 não é lido.
- **Cortes:** 0,300 e 0,400, cada um separado. Lado de cima = bolsa R$ 5 mil maior.
- **Estimador:** RDD local linear, kernel triangular, h = 0,050, um município por linha, erro-padrão HC1.
- **Outcome:** ΔY = média do pós (2025-10 a 2026-08) − média do pré (2024-06 a 2025-06), por município. Nenhum
  mês ≥ 2026-09 é lido.
- **Outcomes**, por 10 mil habitantes (Censo 2022), no CNES nacional (a09), CBO-alvo dos cursos do PMM-E, os
  mesmos do doc 57k:

| Id | O que é | Papel |
|---|---|---|
| B1 | vínculos de especialistas nas CBO-alvo | OC-A1, primária (Holm) |
| B2 | horas SUS semanais nas CBO-alvo | OC-A2, primária (Holm) |
| B3 | B2 sem as horas dos médicos do PMM-E ligados ao CNES: os **outros** especialistas | OC-A3, secundária (BKY) |
| B4 | horas totais (SUS e não SUS) nas CBO-alvo | OC-A4, secundária (BKY) |
| B5 | vínculos de generalistas (placebo) | OC-A5, secundária (BKY) |

**O que o corte identifica.**

- A **forma reduzida** (parte A) mede o pacote do corte sobre a mudança na oferta: a bolsa maior **e** as outras
  regras federais nos mesmos cortes. A DiRD tira só a parte dessas regras que fica igual entre o pré e o pós.
- A **razão *fuzzy*** (parte B) só é "efeito de receber médico" se o corte mexer na oferta local **apenas** pelo
  médico do programa (exclusão). O pacote do corte pode violar isso. Por isso ela é secundária e é lida junto com
  o placebo de generalistas (B5).
- Nada aqui é efeito da participação no PMM-E como política nem do Agora Tem Especialistas.

## 2. Amostra

**V** (principal): os municípios do doc 57k, de U com célula em algum ciclo (1 a 3). **U** (sensibilidade): todos
os municípios do IVS oficial com população 2022 > 0. Município sem todos os meses de uma janela sai daquele
outcome e é contado.

<!-- OC:amostra:inicio -->
<!-- OC:amostra:fim -->

## 3. Portão de reprodução

Antes de qualquer conta nova, o script refaz o salto do F3.1 do E7 (doc 43) em U no corte 0,300, com a mesma
função da biblioteca, a partir do B1 construído pelo script 37. Se a diferença passar de 1e−8, o script para sem
gravar.

<!-- OC:portao:inicio -->
<!-- OC:portao:fim -->

## 4. Leitura

<!-- OC:leitura:inicio -->
<!-- OC:leitura:fim -->

Leitura pré-registrada (protocolo 64, §4):

| Resultado | Leitura |
|---|---|
| OC-A1 e OC-A2 com IC que contém zero nos dois cortes | a mudança na oferta local não se distingue entre os lados; o corte não detecta efeito do pacote sobre a oferta local |
| alguma primária rejeita zero depois do Holm, OC-A5 não rejeita e o pré do OC-C é plano | sinal e tamanho como efeito do **pacote do corte** sobre a mudança na oferta local |
| alguma primária rejeita zero, mas OC-A5 também rejeita ou o pré do OC-C não é plano | não ler como efeito da bolsa nem da chegada |
| primeiro estágio (OC-B0, D1) com F robusto < 10 | instrumento fraco: só o IC de Anderson–Rubin, sem ponto |
| primeiro estágio com F robusto ≥ 10 | razão *fuzzy* com IC de Anderson–Rubin, sob exclusão, com a ressalva do pacote do corte |
| OC-A3 negativo com IC que exclui zero | sinal de deslocamento dos outros especialistas no corte |
| OC-D: diferença entre lados com IC que contém zero | não se detecta que a chegada mude a oferta de forma diferente onde a bolsa é maior |
| OC-E salta no corte | V é selecionada: dar peso a OC-A-U |

Como o código aplica as regras está na seção 9 (decisões D14 e D15).

## 5. Tabelas

### 5.1 Parte A: salto de ΔY no corte (forma reduzida), em V

Salto = lado de cima (bolsa maior) menos lado de baixo. IC 95% pela normal, EP HC1.

<!-- OC:principal:inicio -->
<!-- OC:principal:fim -->

### 5.2 Parte A em U e sensibilidades

<!-- OC:sensibilidades:inicio -->
<!-- OC:sensibilidades:fim -->

### 5.3 Parte B: primeiro estágio (OC-B0)

<!-- OC:primeiro_estagio:inicio -->
<!-- OC:primeiro_estagio:fim -->

### 5.4 Parte B: razão *fuzzy* com IC de Anderson–Rubin (OC-B1 a OC-B5)

<!-- OC:fuzzy:inicio -->
<!-- OC:fuzzy:fim -->

### 5.5 Parte C: estudo de evento no corte (OC-C)

Salto, mês a mês, de Y_t − Y_2025-06. O pré deve ficar plano. Por mês: `output/rdd_bolsa/OC_estudo_evento.csv`.

<!-- OC:evento:inicio -->
<!-- OC:evento:fim -->

### 5.6 Parte D: chegada abaixo e acima do corte (OC-D)

ATT médio dos meses 0 a 6 depois da chegada (o estimador do doc 57k), só com os tratados a menos de 0,050 abaixo
ou acima de cada corte. Pouca potência esperada: veja o número de tratados em cada grupo.

<!-- OC:chegada_lados:inicio -->
<!-- OC:chegada_lados:fim -->

### 5.7 Parte E: seleção de V (OC-E)

<!-- OC:selecao:inicio -->
<!-- OC:selecao:fim -->

## 6. Figuras

<!-- OC:figuras:inicio -->
<!-- OC:figuras:fim -->

## 7. Limites

- **Pacote do corte.** Em 0,300 e 0,400 mudam também o teto do PMMB, o estrato do cofinanciamento da APS, as
  emendas e, em 0,400, a ajuda de custo (auditoria 18). A forma reduzida mede tudo isso junto. A DiRD tira só a
  parte constante no tempo.
- **Exclusão.** A razão *fuzzy* supõe que o corte só mexe na oferta local pelo médico do programa. As outras regras
  do corte podem mexer também. O placebo de generalistas (B5) testa parte disso, não tudo.
- **Seleção de V.** V são os municípios que ofereceram vaga. Oferecer vaga pode responder ao corte. A parte E testa
  isso, e a parte A é repetida em U.
- **Pouca potência da parte D.** Poucos tratados ficam a menos de 0,050 de cada corte.
- **Vínculo cadastrado não é presença.** O CNES registra vínculo e carga horária declarada, não atendimento.
- **B3 e a ligação.** O B3 só tira os médicos do PMM-E ligados ao CNES; os não ligados ficam dentro (doc 57k, 5.4).

## 8. Desvios e esclarecimentos datados

Nenhum desvio mudou o protocolo. As decisões de implementação da seção 9 foram fixadas antes de abrir as
estimativas.

<!-- OC:desvios:inicio -->
<!-- OC:desvios:fim -->

## 9. Decisões de implementação

Fixadas em **2026-10-26, antes de olhar qualquer estimativa do protocolo 64**. Onde o protocolo não decide, vale a
leitura mais próxima do E7 (doc 43, script 14) e do script 37 (doc 57k).

| Id | Item | Decisão |
|---|---|---|
| D1 | amostra V e outcomes | refeitos pelas funções importadas do script 37 (`ler_amostra`, `ler_chegadas` do 22, `ler_painel`, `contagem`, `ler_ligados`, `cbos_alvo`, `horas_ligados`), na mesma ordem do `main` do 37: V = U com célula em algum ciclo, menos os tratados da lista nominal sem célula nos ciclos 1 ou 2. O script para se o tamanho de V diferir do `OL_resumo.json`. |
| D2 | U | `ler_universo` do script 21 (a08 com população 2022 > 0), a mesma base do script 37. Município sem população fica fora e é contado. |
| D3 | ΔY | `diferenca_pos_pre` da biblioteca com `exigir_completo = True` (como no E7): pré 2024-06 a 2025-06, pós 2025-10 a 2026-08. Município sem algum mês sai do outcome e é contado. |
| D4 | portão | B1 em U (função do 37) → ΔB1 → `rd_dird_delta` em 0,300, h = 0,050; compara com o `tau` da linha F3.1, U, 0,300, `principal` de `E7_estimativas.csv`. Tolerância 1e−8. Também confere o EP e os n. |
| D5 | D1 | município com chegada do 1º médico dos ciclos 1 e 2 (lista nominal) até 2026-08: o "tratado" do script 37. Em U, os dois tratados sem célula nos ciclos 1 ou 2 têm D1 = 1. |
| D6 | D2 | médicos distintos ligados ao CNES (regra D1 da X1) cujo registro na X1 é do ciclo 1 ou 2, com algum vínculo SUS em CBO-alvo (o mesmo filtro do B3) em estabelecimento do município em algum mês entre o 1º mês de chegada da lista nominal e 2026-08, por 10 mil hab. Médico não ligado não entra (nada é imputado). |
| D7 | razão *fuzzy* | forma reduzida e primeiro estágio na mesma amostra (municípios com ΔBk observado); razão = salto de ΔBk ÷ salto de D1. Linha principal com D1 em V; D1 em U e D2 em V são sensibilidade (fora do BKY). Sem EP pontual: só o IC de Anderson–Rubin. |
| D8 | grade de Anderson–Rubin | para cada β, `rd_local_linear` de ΔBk − β·D1 (mesmo kernel, h e HC1); β aceito se p ≥ 0,05. Grade de 4.001 pontos igualmente espaçados em [−L; L], L = 2 × o maior \|ΔBk\| entre os municípios com peso de kernel no corte. Cada fronteira interna é refinada por bisseção (60 passos) com o mesmo teste. Conjunto que toca a borda da grade sai como aberto daquele lado. Conjunto com mais de um intervalo é relatado pela envoltória, com o número de intervalos. |
| D9 | F robusto | (salto ÷ EP HC1)² do primeiro estágio com D1 em V, em toda V (todos têm D1). É o F que a leitura usa. |
| D10 | família BKY | 24 testes, todos em V e h = 0,050: OC-A3, A4 e A5 nos dois cortes (6); OC-B0 com D1 nos dois cortes (2); OC-B1 a B5 com D1 nos dois cortes (10), com p = p de Anderson–Rubin em β = 0 (que é o p da forma reduzida na mesma amostra); OC-D, diferença entre lados de B1, B2 e B3 nos dois cortes (6). |
| D11 | OC-C | `rd_estudo_evento` em cada corte, meses 2024-06 a 2026-08, referência 2025-06, em V. "Pré plano": Wald conjunto dos 12 meses de 2024-06 a 2025-05 = 0, com covariância HC1 conjunta das mesmas regressões mensais (pesos lineares da biblioteca), nos municípios com todos esses meses e a referência observados; plano se p ≥ 0,05. |
| D12 | OC-D | tratados de V com −0,050 < IVS − corte ≤ 0 (abaixo) ou 0 < IVS − corte < 0,050 (acima), a convenção da biblioteca. Controles: os mesmos do script 37 em toda V. O tratado fora do grupo é controle até a sua chegada e sai dos controles a partir dela (a regra do 37 para início fora das coortes). Diferença = acima − abaixo. EP pelo bootstrap de Mammen do 37 (B = 9.999, semente 20261026, os mesmos pesos para todos), aplicado à diferença das funções de influência. |
| D13 | OC-E | indicador de ter célula em algum ciclo (1 a 3), em U, `rd_local_linear` h = 0,050. "Salta" = p < 0,05 em algum corte. |
| D14 | regras da leitura | "IC contém zero" = IC 95% convencional. "Rejeita depois do Holm" = p de Holm < 0,05. "OC-A5 rejeita" = q BKY < 0,05 no mesmo corte (regra do 37 para o placebo). O pré do OC-C é conferido no outcome e no corte da primária que rejeita. "OC-A3 negativo com IC que exclui zero" = salto < 0 e IC convencional < 0 em algum corte. OC-D lida pelo IC da diferença. |
| D15 | caso que a tabela não cobre | primária com IC que exclui zero, mas sem rejeitar depois do Holm: relatada como descritiva, sem ler efeito do pacote. |
| D16 | sensibilidades | h = 0,030 e 0,080; IC honesto (`rd_honesto_relato`, M da regra de bolso com suporte até o ponto médio entre cortes, fator 1, h = 0,050, como no E7); média do pós com a média do pré como covariável. Em OC-A1 a A5, em V e em U. Fora do Holm e do BKY. |
