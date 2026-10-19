# Protocolo: número de vagas preenchidas, controlando pelas vagas oferecidas

> **Data de congelamento:** 19/10/2026, antes de estimar qualquer especificação
> abaixo.<br>
> **Diretriz do autor (19/10/2026):** trocar a variável de efeito da fração de
> vagas preenchidas para o **número de vagas preenchidas**, controlando pelo
> **número de vagas disponibilizadas**, que o autor considera um confundidor,
> ainda que indireto, do número de vagas preenchidas. Rodar tudo de novo com
> essa variável, com prioridade, sem descartar o que já foi feito.<br>
> **Estatuto:** pós-resultado. A fração (F1.3) já foi vista em todos os ciclos.
> Toda saída leva `estatuto = PROTOCOLO_48_POS_RESULTADO` e
> `natureza_dos_dados = EMPIRICO`. Nada aqui altera o protocolo 40, o Holm das
> primárias P1 e P2 nem os docs 41–46.<br>
> **Numeração:** o doc 47 (produção especializada) continua valendo. Os
> resultados deste protocolo vão para o doc 49, e os da família K passam para o
> doc 50.

## 1. Outcome e controle

| Papel | Variável (`output/rdd_bolsa/outcomes/outcomes_V_municipio.parquet`) | Definição |
|---|---|---|
| **N1, outcome principal** | `n_alocados_ch1` | vagas preenchidas na 1ª chamada do ciclo k: médicos alocados, contados por município |
| **controle principal** | vagas oferecidas no quadro da 1ª chamada | `vagas_imediatas` + `vagas_cr`, se o alocado puder ocupar cadastro reserva; senão, só `vagas_imediatas` |
| N2, secundário | `n_celulas_preenchidas_ch1` | células (estabelecimento × curso) com ≥ 1 alocado; controle: `n_celulas` |
| N3, secundário | `n_celulas_preenchidas_ate_ch2` | o mesmo, até a 2ª chamada (ciclos 1 e 2); controle: `n_celulas` |
| N4, secundário | `n_ativos_ciclo` | especialistas ativos do ciclo no retrato de 09/10/2026; controle: vagas oferecidas |

**Escolha do controle principal.** A regra entre "imediatas + CR" e "só
imediatas" é decidida **antes de estimar**: verifica-se nos quadros e
resultados se um alocado da 1ª chamada pode ocupar cadastro reserva, e a
verificação é registrada. A outra forma é relatada como sensibilidade.

**População:**
- principal: municípios com célula no quadro do ciclo k (V1, V2, V3), ciclos 1 a 3;
- secundária: U (todos os municípios, com zero fora do quadro), sem controle,
  como efeito total.

## 2. Por que controlar pelas vagas oferecidas exige cuidado

Numa RDD, um controle não é necessário para a identificação. Ele só ajuda,
reduzindo variância, quando é pré-determinado, isto é, não afetado pelo
tratamento (Calonico, Cattaneo, Farrell e Titiunik, 2019).

As vagas oferecidas são definidas pelo gestor **antes** de os candidatos
escolherem, mas **depois** de a faixa da bolsa ser conhecida, e por isso podem
responder ao corte. O E6 já estimou isso:

- F0.2, vagas imediatas por 10 mil habitantes no ciclo 1;
- o resultado está em `output/rdd_bolsa/E6_estimativas.csv`.

Se as vagas oferecidas saltam no corte:
- o número de vagas preenchidas *sem* controle mede o **efeito total** da faixa,
  isto é, oferta de vagas mais preenchimento;
- *com* controle, mede o preenchimento **dado o número de vagas**. Essa leitura
  só é causal se o salto nas vagas não carregar seleção.

Por isso o protocolo relata as duas e a decomposição, e não só a especificação
com controle.

## 3. Especificações (todas relatadas)

Base comum a todas as linhas, igual ao E3/E6:
- local linear;
- kernel triangular;
- h = 0,050, com sensibilidade 0,030 e 0,080;
- HC1, ou CR1 por município quando os ciclos são empilhados;
- funções de `scripts/rdd_bolsa/rdd_lib.py`;
- cada linha por corte (0,300 e 0,400) e empilhada.

| Id | Especificação | Leitura |
|---|---|---|
| S-a | **N1 com controle linear das vagas oferecidas** (ajuste por covariável comum aos dois lados, como em CCFT 2019) | **principal pedido pelo autor** |
| S-b | N1 sem controle | efeito total da faixa |
| S-c | vagas oferecidas como outcome (V e U) | primeiro passo da decomposição |
| S-d | Poisson local de N1 com log(vagas oferecidas) como covariável (elasticidade livre) e como offset (taxa) | contagem com exposição; o offset equivale à fração ponderada por vaga |
| S-e | fração ponderada pelas vagas (vagas preenchidas ÷ oferecidas, com peso = vagas) | probabilidade de preenchimento no nível da vaga |
| S-f | controle por vagas oferecidas com inclinação diferente de cada lado | robustez |
| S-g | IC honesto (Armstrong–Kolesár), mesma regra do E6 | robustez de inferência |
| S-h | randomização local (Fisher) na janela mínima do E5 | robustez com poucos municípios |
| S-i | cortes placebo nas médias de cada lado, como no E9 | validade |
| S-j | donut (sem os municípios com IVS a menos de 0,002 do corte) | validade |

**Empilhamentos:**
- ciclos 1–3 com efeito fixo de ciclo e cluster por município;
- cortes empilhados.

A linha principal da família N é **S-a, ciclos e cortes empilhados**. Ciclo 1
e ciclo 2 separados são secundárias.

**Holm** entre as quatro linhas S-a empilhadas: N1, N2, N3 e N4.

**Relato:** efeito em vagas por município e em relação à média abaixo do corte,
além do efeito mínimo detectável (2,8 × EP).

## 4. Figuras

Para N1 com controle e sem controle, nos ciclos 1 e 2 e no empilhado:
- gráfico RDD tradicional: médias em faixas de IVS e reta de cada lado;
- com controle, o eixo é o resíduo de N1 depois de tirar a parte explicada
  pelas vagas oferecidas, estimada na janela.

Toda figura sai do script e tem legenda que explica cada elemento.

## 5. Integridade

Valem as regras de integridade:
- nada simulado ou imputado;
- números lidos de `output/`;
- o arquivo de IVS errado não é lido.

Um município com vagas oferecidas ausentes sai da linha e é contado na saída,
nunca recebe zero.

**Exposição prévia:**
- vistas as frações F1.3 e F1.4 de todos os ciclos;
- vista a F0.2 (células e vagas por 10 mil);
- as contagens N1–N4 por lado de corte não foram vistas.

## 6. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/23_estimar_contagem_vagas.py` |
| estimativas e resumo | `output/rdd_bolsa/N_estimativas.csv`, `N_resumo.json` |
| figuras | `output/rdd_bolsa/N_figuras/` |
| resultados | `docs/06_execucao/49_resultados_contagem_vagas_preenchidas.md` |

## 7. Adendo de 19/10/2026: abertura de vagas como seleção (antes de estimar)

**Por que este adendo.** Pedido do autor depois de ver a S-c e o perfil
descritivo das vagas oferecidas ao longo do IVS. Vagas oferecidas e preenchidas
andam juntas e acompanham o porte do município. A abertura de vagas é decisão
do gestor e pode responder ao corte. Por isso, quatro análises novas:

**Estatuto.** Toda saída leva `estatuto = PROTOCOLO_48_ADENDO_7_POS_RESULTADO`.
Nenhuma muda as linhas S-a a S-j nem o Holm do §3.

**Base comum.** Mesmos estimadores do §3:
- h = 0,050;
- ciclos 1–3;
- cortes separados e empilhados;
- CR1 por município.

### A1 — Efeito total por habitante (sem condicionar na abertura)

| Item | Especificação |
|---|---|
| População | U (todos os municípios com IVS oficial), com zero onde não houve vaga |
| Outcomes | vagas preenchidas por 10 mil habitantes; vagas oferecidas por 10 mil habitantes |
| Denominador | população do Censo 2022 (`populacao_2022`) |
| Robustez | Poisson local das contagens com offset log(população) |
| Leitura | efeito total da faixa sobre o provimento por habitante, sem condicionar na abertura |

### A2 — Limites de Lee para a abertura

**Margem extensiva.** Seleção = ter ≥ 1 vaga. Outcome = vagas preenchidas
÷ oferecidas. Os limites de Lee usam a taxa local de abertura de cada lado do
corte.

**Margem intensiva, no nível da vaga.**
- Taxa de seleção de cada lado = vagas oferecidas por 10 mil habitantes,
  estimada localmente no corte.
- Fração a aparar: p = (s_maior − s_menor) / s_maior, aplicada ao lado com
  mais vagas por habitante.
- Outcome binário: vaga preenchida ou não. As vagas são contadas pelo número de
  alocados, limitado às vagas oferecidas de cada célula.
- Limites, com f = taxa de preenchimento:
  - inferior = max(0, (f − p) / (1 − p));
  - superior = min(1, f / (1 − p)).
- O IC usa Imbens–Manski, com bootstrap por município (semente fixa).

**Monotonicidade.** A suposição de que a abertura muda num só sentido no corte
é declarada.

### A3 — Unidade = célula aberta

| Item | Especificação |
|---|---|
| Unidade | célula (estabelecimento × curso) do quadro da 1ª chamada |
| Outcomes | célula preenchida (≥ 1 alocado); alocados ÷ vagas da célula; candidatos de 1ª opção |
| Estimação | RDD no IVS do município, cluster por município |
| Efeitos fixos | curso × ciclo; tipo de vaga (imediata ou só cadastro reserva); tipo de prática, se disponível |
| Ponte com o E9 | atratividade da célula e preenchimento |
| Leitura | condicional à abertura; os limites do A2 dizem quanto a seleção pode mover esse resultado |

### A4 — Covariáveis pré-determinadas da abertura

S-b e A1 com covariáveis CCFT pré-determinadas:
- log da população de 2022;
- estoque CNES pré-programa (202406–202506) de especialistas das CBO-alvo e de
  generalistas, do painel nacional;
- número de estabelecimentos hospitalares no CNES pré, se o painel trouxer;
- se não trouxer, a lacuna é registrada e nada é imputado.

**Leitura.** Mede se o salto nas contagens vem de diferenças de porte e de
capacidade instalada já existentes antes do programa. Diferenças nascidas da
resposta à faixa não são retiradas.

## 8. Correção de 19/10/2026: quando a faixa da bolsa ficou conhecida

**O que se corrige.** O §2 diz que as vagas oferecidas são definidas pelo
gestor "**depois** de a faixa da bolsa ser conhecida". Para o ciclo 1, as
fontes arquivadas não sustentam essa frase. O texto congelado do §2 fica como
está; esta nota o corrige, ciclo a ciclo.

| Ciclo | O que as fontes arquivadas mostram | Consequência |
|---|---|---|
| 1 | O chamamento de gestores (Edital SGTES/MS nº 2/2025, DOU de 12/06/2025, `data/raw/aquisicao/normas_ivs/edital_sgtes_02_2025_gestores_dou.html`) não menciona IVS, faixa nem valor de bolsa por município: diz só que "serão oferecidas 500 (quinhentas) bolsas de formação para médicos especialistas, conforme chamamento público que será publicado posteriormente" (item 3.9). A grade por faixa de IVS aparece pela primeira vez no Edital de Chamamento Público nº 3/2025 (DOU de 24/07/2025, `data/raw/aquisicao/normas_ivs/edital_sgtes_03_2025_ciclo1_dou.html`, item 11.1.4: "foi estabelecido o critério de faixa de atração com base na categorização municipal do Índice de Vulnerabilidade Social IVS") e na FAQ da bolsa publicada em 24/07/2025 (`data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_faq_bolsa.html`; a página foi atualizada depois, em 25/06/2026), no mesmo dia do quadro de vagas da 1ª chamada (24/07/2025, `docs/auditorias/aquisicao/A01_vagas_e_versionamento.md`) | a adesão dos gestores precedeu o anúncio da faixa. As vagas oferecidas do ciclo 1 não podem ter respondido à faixa da bolsa em si; só a outras regras que mudam nos mesmos cortes (auditoria 18) ou à discricionariedade da SGTES na montagem do quadro |
| 2 | Não há etapa de gestores arquivada no repositório; a cópia do Edital SGTES/MS nº 1/2026 (`data/raw/aquisicao/ivs_regra/edital_sgtes_01_2026_ciclo2.html`) é só a página do chamamento, publicada em 03/02/2026 | indeterminado |
| 3 | A grade de 2026 por faixa estava pública desde o Chamamento nº 1/2026 (fevereiro de 2026; grade de 2026 extraída em `output/aquisicao/a03_matriz_regra_tratamento.json`, `grade_2026_edital_1_2026_e_edital_28_2026`), antes do cardápio de gestores do ciclo 3 (proposta preliminar de 15/05/2026, `docs/auditorias/aquisicao/A01_vagas_e_versionamento.md`) e da adesão de gestores (Chamamento SGTES/MS nº 5/2026, página publicada em 10/06/2026, `data/raw/aquisicao/ivs_regra/edital_sgtes_05_2026_adesao_ciclo3.html`) | a faixa era inferível pelo gestor; a frase do §2 vale |

**Consequência para a leitura.** No ciclo 1, condicionar nas vagas oferecidas
(S-a, A3) é mais defensável do que nos outros ciclos: a oferta pode ter
respondido ao pacote do corte, mas não ao valor anunciado da bolsa. Por isso o
adendo §7 relata o ciclo 1 em separado onde isso muda a leitura. Nenhuma
especificação, amostra ou estimador do §3 ou do §7 muda com esta correção.
