# 64. Protocolo: oferta local de especialistas comparada no corte (DiRD e RDD *fuzzy* da chegada)

> **Data de congelamento:** 26/10/2026, antes de qualquer conta deste protocolo.<br>
> **Pedido do autor (26/10/2026):** "gosto da ideia de olhar para esse desenho,
> especialmente se pudermos comparar quem recebeu e quem não recebeu a partir do
> corte como controle e tratamento. Roda se não tiver feito isso ainda."<br>
> **Estatuto:** `PROTOCOLO_64_POS_RESULTADO`. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.<br>
> **O que já foi visto antes de congelar:**
> - E7 (doc 43): DiRD da bolsa sobre a oferta de especialistas do município,
>   nas populações U (todos os municípios do IVS oficial) e V1 (quadro do
>   ciclo 1). Nenhuma linha rejeita zero.
> - Protocolo 60, parte B (doc 57k): estudo de evento da **chegada** do 1º
>   médico do PMM-E, comparando com municípios ainda não tratados. B1–B4 sobem
>   depois da chegada, mas o pré já subia e a ruptura M̄ fica abaixo de 1.
>
> Este protocolo **não** abre outcome novo. Ele muda a **fonte de variação**: em
> vez do mês da chegada, o lado do corte de IVS.

## 1. Por que este desenho

No doc 57k, quem recebe médico é comparado com quem ainda não recebeu. O
problema é que quem recebe antes já vinha diferente: o pré sobe. O corte de IVS
dá outra comparação. Perto do corte, os municípios dos dois lados são parecidos
antes do programa (balanço e densidade passam, doc 41 e auditoria 16), e o lado
do corte decide a bolsa. Se o lado de cima recebe mais médicos do programa, a
diferença na oferta local entre os lados, dividida pela diferença em receber,
estima o efeito de receber médico para os municípios que recebem **por causa**
do corte.

**O que o corte identifica, com os limites do `CLAUDE.md`:**
- a **forma reduzida** (§3, parte A) mede o **pacote do corte** sobre a mudança
  na oferta: bolsa de R$ 5 mil a mais **e** as outras regras federais nos
  mesmos cortes (auditoria 18). A DiRD remove só a parte dessas regras que é
  constante entre o pré e o pós;
- a razão *fuzzy* (parte B) só é "efeito de receber médico" se o corte afetar a
  oferta local **apenas** por meio do médico do programa (exclusão). O pacote do
  corte viola isso se as outras regras moverem a oferta de especialistas no
  período. Por isso a parte B é **secundária** e lida junto com o placebo de
  generalistas (B5);
- nada aqui é efeito da participação no PMM-E como política nem do Agora Tem
  Especialistas.

## 2. Dados, populações e variáveis

**Running variable:** IVS 2010 oficial do Ipea
(`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`). O arquivo
`data/ivs_ipea_2010_municipios.csv` não é lido.

**Populações:**

| Id | Definição | Papel |
|---|---|---|
| **V** | municípios de U com célula em algum ciclo (1 a 3), a amostra do doc 57k (1.037 municípios, contados em `OL_resumo.json`) | principal |
| U | todos os municípios do IVS oficial (a08) | sensibilidade; não condiciona em ter oferecido vaga |

Condicionar em V pode selecionar: oferecer vaga pode responder ao corte. Por
isso a parte E testa o salto de "ter célula em algum ciclo" em U, e a parte A é
repetida em U.

**Janelas (iguais às do E7):** pré 2024-06 a 2025-06; pós 2025-10 a 2026-08.
Nenhuma competência ≥ 2026-09 é lida. Pré extra para o estudo de evento: todas
as competências do painel a09 entre 2024-06 e 2025-06; mês de referência
2025-06.

**Outcomes** (iguais aos do doc 57k, por 10 mil hab., Censo 2022, CNES nacional
a09, CBO-alvo dos cursos do PMM-E). A construção é **a mesma** do script 37,
importada, não reescrita:

| Id | O que é |
|---|---|
| B1 | vínculos de especialistas nas CBO-alvo |
| B2 | horas SUS semanais nas CBO-alvo |
| B3 | B2 sem as horas dos médicos do PMM-E ligados ao CNES em estabelecimento do município: os **outros** especialistas |
| B4 | horas totais (SUS e não SUS) nas CBO-alvo |
| B5 | vínculos de generalistas (placebo) |

ΔY = média do pós − média do pré, por município. Município sem todos os meses de
uma janela sai daquele outcome, contado, como no E7.

**Variável endógena (parte B):**
- **D1:** o município recebeu ≥ 1 médico do PMM-E dos ciclos 1 e 2 até 202608
  (a definição de "tratado" do doc 57k);
- **D2:** médicos do PMM-E dos ciclos 1 e 2 ligados ao CNES em estabelecimento
  do município até 202608, por 10 mil hab. (sensibilidade).

## 3. Especificações

**Comum a todas:** RDD *sharp* local linear (forma reduzida) ou *fuzzy*, kernel
triangular, h = 0,050, **cada corte separado** (0,300 e 0,400), um município
por linha, erro-padrão HC1. Sem empilhar cortes no principal.

| Parte | Id | O que estima | Papel |
|---|---|---|---|
| A | **OC-A1** | salto de ΔB1 no corte, em V | **primária** |
| A | **OC-A2** | salto de ΔB2 no corte, em V | **primária** |
| A | OC-A3 | salto de ΔB3 (outros especialistas) | secundária |
| A | OC-A4 | salto de ΔB4 | secundária |
| A | OC-A5 | salto de ΔB5 (placebo de generalistas) | secundária; deve ser zero se a exclusão vale |
| A | OC-A-U | OC-A1 a A5 em U | sensibilidade |
| B | OC-B0 | **primeiro estágio:** salto de D1 (e de D2) no corte, em V e em U | secundária; relatar F robusto (t²) |
| B | OC-B1 a B5 | razão *fuzzy*: salto de ΔBk / salto de D1, com IC de **Anderson–Rubin** (inversão do teste da forma reduzida ΔBk − β·D1 numa grade de β, mesmo kernel e janela) | secundária |
| C | OC-C | estudo de evento no corte: salto mês a mês de Y_t − Y_2025-06 para B1, B2 e B3, de 2024-06 a 2026-08, em V | diagnóstico; o pré deve ser plano |
| D | OC-D | o ATT da chegada do doc 57k (média dos meses 0 a 6, B1–B3), estimado à parte para os tratados de V a menos de 0,050 **abaixo** e **acima** de cada corte, e a diferença, com o mesmo estimador e bootstrap do script 37 | secundária; heterogeneidade por condição pré-tratamento (lado do corte); pouca potência esperada, relatar o número de tratados por grupo |
| E | OC-E | salto de "ter célula em algum ciclo" em U | diagnóstico da seleção de V |

**Testes múltiplos:** Holm entre as quatro primárias (OC-A1 e OC-A2 × dois
cortes). BKY entre as secundárias (A3–A5, B0–B5, D).

**Sensibilidades (todas relatadas):** h = 0,030 e 0,080; IC honesto
(Armstrong–Kolesár) com M da regra de bolso, como no E7; Y_pós com Y_pré como
covariável em vez de ΔY.

## 4. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| OC-A1 e OC-A2 com IC que contém zero nos dois cortes | "comparando os dois lados do corte, a mudança na oferta local de especialistas não se distingue; o corte não detecta efeito do pacote sobre a oferta local" |
| alguma primária rejeita zero depois do Holm, OC-A5 (placebo) não rejeita e o pré do OC-C é plano | relatar sinal e tamanho como efeito do **pacote do corte** sobre a mudança na oferta local |
| alguma primária rejeita zero, mas OC-A5 também rejeita ou o pré do OC-C não é plano | não ler como efeito da bolsa nem da chegada: outra regra no corte ou tendência |
| primeiro estágio (OC-B0, D1) com F robusto < 10 | **instrumento fraco**: a razão *fuzzy* não tem estimativa pontual utilizável; relatar só o IC de Anderson–Rubin e não pôr ponto no deck |
| primeiro estágio com F robusto ≥ 10 | relatar a razão *fuzzy* com IC de Anderson–Rubin, como efeito de receber médico para os municípios que recebem por causa do corte, **sob exclusão**, com a ressalva do pacote do corte |
| OC-A3 (outros especialistas) negativo com IC que exclui zero | sinal de deslocamento dos outros especialistas no corte |
| OC-D: diferença entre lados com IC que contém zero | não se detecta que a chegada mude a oferta de forma diferente onde a bolsa é maior |
| OC-E salta no corte | V é selecionada: dar peso a OC-A-U |

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/43_oferta_local_corte.py` |
| estimativas | `output/rdd_bolsa/OC_estimativas.csv`, `OC_estudo_evento.csv`, `OC_resumo.json`, `OC_figuras/` |
| resultados | `docs/06_execucao/57q_resultados_oferta_local_corte.md`, blocos gerados pelo script (`--atualizar-doc`) |
| testes | `tests/test_oferta_local_corte.py`: esquema, `natureza_dos_dados`, nenhuma competência ≥ 202609, IVS oficial, doc bate com CSV, reprodução de um salto do E7 (F3.1 em U, 0,300) com a mesma função antes de estimar |

**Portão de reprodução:** antes de qualquer conta nova, o script reproduz o
F3.1 em U no corte 0,300 do E7 (doc 43) com diferença ≤ 1e−8. Se não
reproduzir, para e relata.

## 6. Integridade

- Nada imputado; ausência fica ausente e contada.
- Nada em `data/` é escrito.
- O arquivo de IVS errado não é lido.
- Nenhuma competência ≥ 202609.
- As saídas do E7 e do protocolo 60 não são regravadas.
- Nenhuma especificação, janela ou população é trocada depois de ver
  resultado; qualquer mudança vira adendo datado.
