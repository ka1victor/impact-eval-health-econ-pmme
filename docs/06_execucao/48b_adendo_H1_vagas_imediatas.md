# 48b. Adendo ao protocolo 48: H1 só com vagas imediatas (nova especificação principal)

> **Data de congelamento:** 26/10/2026, antes de rodar as contas novas deste
> adendo.<br>
> **Decisão do autor (26/10/2026):** "faz o adendo e coloca no deck como
> principal". A especificação deste adendo passa a ser a **principal da H1 na
> apresentação**. As do protocolo 48 (S-a e S-b) e do adendo §7 (A3) continuam
> relatadas, ao lado.<br>
> **Estatuto:** `ADENDO_48B_POS_RESULTADO`. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.<br>
> **O que já foi visto** (docs 49, 49b, 57l):
> - As medidas que misturam vaga imediata e cadastro reserva (N1 com controle,
>   taxa por vaga oferecida) dão salto negativo em 0,300 com IC que exclui zero.
> - As medidas restritas a vagas imediatas (taxa nas células só de vaga
>   imediata; taxa com vagas imediatas no denominador) dão ponto negativo e IC
>   que contém zero.
>
> Este adendo **não é** uma primeira olhada. É uma correção de definição,
> justificada pela regra de uso da reserva, e é registrada como pós-resultado.

## 1. Justificativa: por que só vagas imediatas

A vaga de cadastro reserva é uma vaga de espera. Na 1ª chamada, ela compete de
forma diferente da vaga imediata: no ciclo 2, nenhuma célula só de reserva teve
alocado na 1ª chamada (doc 49b, §14). Comparar o preenchimento na 1ª chamada
entre municípios com proporções diferentes de reserva mede, em parte, a
composição do quadro, e não o preenchimento de vagas comparáveis. A comparação
correta é entre **vagas do mesmo tipo**.

A regra de cada edital sobre o uso da reserva na 1ª chamada é verificada pela
auditoria 36, em curso. O item de cada edital é citado no doc de resultados
quando estiver disponível. Se o edital de algum ciclo permitir preencher a
reserva na 1ª chamada, isso é relatado. A especificação deste adendo não muda,
porque a comparação entre vagas do mesmo tipo continua sendo a correta.

## 2. Especificação principal (nova)

**Amostra:** células com pelo menos uma vaga imediata no quadro da 1ª chamada
(células "só de vagas imediatas" e células "mistas"), ciclos 1–3. As células
só de cadastro reserva ficam fora e são contadas.

| Id | Outcome | Unidade | Controle | Papel |
|---|---|---|---|---|
| **HI-1** | célula com vaga imediata preenchida na 1ª chamada, com a definição de "preenchida" de cada ciclo, igual à do A3 | célula | efeitos fixos de curso × ciclo | **primária** |
| **HI-2** | médicos alocados na 1ª chamada em células com vaga imediata, por município | município | vagas imediatas dessas células, com coeficiente por ciclo, como no S-a | **primária** |

**Comum às duas:**
- RDD *sharp* local linear, kernel triangular, h = 0,050;
- **cada corte separado** (0,300 e 0,400);
- ciclos 1–3 empilhados, com intercepto e inclinações por ciclo;
- erro-padrão agrupado por município.

**Holm:** entre as quatro linhas primárias (HI-1 e HI-2 × dois cortes).

## 3. Linhas secundárias e de sensibilidade (todas relatadas)

| Id | Linha |
|---|---|
| HI-s1 | HI-1 e HI-2 por ciclo (1, 2, 3), em cada corte |
| HI-s2 | HI-1 com uma definição única de "preenchida" em todos os ciclos (≥ 1 alocado na 1ª chamada) |
| HI-s3 | HI-2 sem controle (efeito total entre vagas imediatas) |
| HI-s4 | só células "puras" de vaga imediata, sem as mistas |
| HI-s5 | preenchimento até a 2ª chamada, com todas as células, inclusive as de reserva (ciclos 1 e 2), como contraste: é a medida em que a reserva entra em jogo |
| HI-s6 | as células só de reserva, sozinhas, salto no corte, descritivo: mostra onde estava a diferença |
| HI-s7 | TOST de HI-1 e HI-2 com as margens do protocolo 60 (±10 p.p.; ±25% da média abaixo do corte) |
| HI-s8 | h = 0,030 e 0,080; IC honesto como no protocolo 48 |

BKY entre as secundárias.

## 4. Leitura pré-registrada

| Resultado | Leitura |
|---|---|
| HI-1 e HI-2 com IC que contém zero nos dois cortes | "comparando vagas do mesmo tipo, não se detecta diferença de preenchimento no corte" (pacote do corte) |
| alguma linha primária rejeita zero depois do Holm | relatar o sinal e o tamanho, com as ressalvas do diagnóstico 61 (poucos municípios, estimativa no corte) |
| HI-s6 mostra a diferença concentrada nas células só de reserva | a queda das medidas antigas era composição do quadro |

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/40_h1_vagas_imediatas.py` |
| estimativas | `output/rdd_bolsa/HI_estimativas.csv`, `HI_resumo.json`, `HI_figuras/` |
| resultados | `docs/06_execucao/57n_resultados_H1_vagas_imediatas.md` |
| testes | `tests/test_h1_vagas_imediatas.py` |

## 6. Integridade

- Nada imputado.
- Célula fora da amostra é contada, não descartada em silêncio.
- O arquivo de IVS errado não é lido.
- Nenhum CNES ≥ 202609.
- As saídas dos protocolos 48 e 61 não são regravadas.

## 7. Nota datada de 26/10/2026: o tipo de vaga do ciclo 2 vem do quadro anterior à alocação

A auditoria 36 (`docs/auditorias/36_auditoria_dados_H1.md`) mostrou que o
quadro do ciclo 2 usado no pipeline (retificado de 19/03/2026) foi refeito
**depois** do resultado preliminar (10/03/2026). A SGTES converteu 630 vagas de
reserva em imediatas em 301 células, e 297 delas tinham recebido alocado. Pelo
quadro vigente na inscrição (retificado de 13/02/2026), 42% dos alocados do
ciclo 2 estavam em células só de reserva. Logo, a frase da §1 "no ciclo 2,
nenhuma célula só de reserva teve alocado na 1ª chamada" descreve o quadro
pós-resultado, não a regra.

**Consequência para este adendo, antes de qualquer resultado dele ter sido
visto:**
- no ciclo 2, o tipo de vaga (imediata, mista, só de reserva) e as vagas
  imediatas usadas na amostra e no controle de HI-1 e HI-2 vêm do **quadro de
  13/02/2026**;
- nos ciclos 1 e 3 nada muda.

A comparação entre vagas do mesmo tipo continua sendo a principal. O que muda é
o tipo ser medido **antes** da alocação, como precisa ser para não condicionar
no resultado.
