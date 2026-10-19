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
