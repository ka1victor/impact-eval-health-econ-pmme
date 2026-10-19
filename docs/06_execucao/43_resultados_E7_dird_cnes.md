# 43 — Resultados do E7: diferença em descontinuidades no CNES (família F3)

> **Protocolo:** [`40_protocolo_multioutcome_rdd_bolsa.md`](40_protocolo_multioutcome_rdd_bolsa.md)
> (§3, §4, §5 F3, §6 painel CNES, §7 P2, §13 S1–S6), congelado em 18/10/2026,
> e [`output/rdd_bolsa/protocolo_E6_multioutcome.json`](../../output/rdd_bolsa/protocolo_E6_multioutcome.json).<br>
> **Script:** [`scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py`](../../scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py),
> com os estimadores de [`rdd_lib.py`](../../scripts/rdd_bolsa/rdd_lib.py).<br>
> **Saídas:** `output/rdd_bolsa/E7_estimativas.csv`, `E7_estudo_evento.csv`,
> `E7_resumo.json` e `E7_figuras/`. Natureza dos dados: **EMPIRICO**.<br>
> **Painel:** CNES nacional município × grupo de CBO × mês (tarefa C,
> [`auditorias/aquisicao/A09`](../auditorias/aquisicao/A09_cnes_nacional.md)).<br>
> **Números:** todas as tabelas entre marcadores `E7:*` são geradas das saídas
> por `python3 scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py --atualizar-doc`, e o
> teste `tests/test_e7_dird.py` confere que o doc bate com os CSV. Fora delas
> este texto não traz número de resultado.

## 1. O que a DiRD identifica

A bolsa do PMM-E sobe R$ 5 mil por mês em `s > 0,300` e em `s > 0,400` (IVS
2010 oficial do Ipea). Outras regras federais mudam nos mesmos cortes
([`auditorias/18`](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)): o
teto de vagas do PMMB (Portaria 752/2023), o estrato do cofinanciamento da APS
(Portaria 3.493/2024), o teto de emendas e parcelas de custeio com "IVS maior
que 0,3" e, em 0,400, a ajuda de custo do PMMB.

- **RDD em nível** (média do pré ou do pós, sem diferenciar) mede o **pacote
  do corte**: bolsa anunciada mais todas essas regras.
- **DiRD** (ΔY = média do pós − média do pré, RDD sobre ΔY) mede a **bolsa mais
  a variação, entre pré e pós, das descontinuidades das outras políticas**. Ela
  remove só a parte dessas políticas que é constante no tempo.
- **Ameaça que a DiRD não remove:** co-política cujo efeito no corte muda entre
  pré e pós. A auditoria 18 (§3.1) aponta o estoque de médicos de coparticipação
  do PMMB, o IED da APS (desde 05/2024), as emendas e parcelas de MAC e APS
  (atos e montantes novos a cada ano; em 2026 incluem o Agora Tem Especialistas)
  e o Eixo Vínculo (12/2025, dentro do pós). Duas ferramentas avaliam isso: o
  **placebo de generalistas** (F3.P1, e a CBO 225130 em separado, S6), que essas
  políticas movem e a bolsa do PMM-E não; e o **estudo de evento**, em que o
  salto das CBO-alvo deve ficar plano antes do PMM-E e não acompanhar as datas
  das outras políticas.
- **Nenhum resultado aqui é efeito da participação no PMM-E** nem do Agora Tem
  Especialistas. O contraste é o anúncio do incentivo marginal, nos limites
  acima.

## 2. Dados, outcomes e amostras

| Id | Outcome (grupo do painel a09) | População |
|---|---|---|
| F3.1 | vínculos nas CBO-alvo do PMM-E (`alvo_pmme`) por 10 mil hab. | U e V1 |
| F3.2 | município com ≥ 1 profissional nas CBO-alvo | U |
| F3.3 | horas SUS semanais nas CBO-alvo por 10 mil hab. | U |
| F3.P1 | vínculos de generalistas (225125, 225142, 225170) por 10 mil hab. | U |
| S6 | vínculos de médico de família e comunidade (225130) por 10 mil hab. | U |
| F3.P2 | vínculos de especialistas fora das CBO-alvo por 10 mil hab. | U |

- **Populações:** U = todos os municípios do IVS 2010 oficial (a08); V1 =
  municípios do quadro do ciclo 1. Denominador: população do Censo 2022.
- **Janelas:** pré 2024-06 a 2025-06; pós 2025-10 a 2026-08 (contém o início
  do ciclo 1 e do ciclo 2); referência do estudo de evento 2025-06; placebo
  dentro do pré 2024-12..2025-05 contra 2024-06..2024-11; pré extra (S5)
  2022-01..2023-03, competências disponíveis. Nenhuma competência a partir de
  2026-09 é lida.
- **Horas ausentes (F3.3):** horas nulas no painel ficam ausentes, nunca zero.
  O município sem todos os meses de uma janela sai daquele outcome naquela
  especificação; a contagem está na `nota` das linhas e em
  `validacoes.horas_ausentes` do resumo.
- **Estimadores:** local linear, kernel triangular, h = 0,050, HC1 por corte;
  empilhado com intercepto e inclinações por corte e lado, salto comum, CR1 por
  município. Sensibilidade h = 0,030 e 0,080; IC honesto com M da regra de bolso
  (suporte até o ponto médio entre cortes), 0,5M e 2M; Y_pós com Y_pré como
  covariável; local randomization na janela do E5 (só covariáveis).

## 3. Hipótese primária P2

P2 é F3.1 por DiRD em U, cortes empilhados. O p abaixo entra no Holm com o p de
P1 (E6), feito pelo coordenador.

<!-- E7:p2:inicio -->
(gerado pelo script)
<!-- E7:p2:fim -->

## 4. Estimativas principais (DiRD, h = 0,050)

q BKY: dentro da família F3, sobre as linhas principais de F3.1 (U e V1), F3.2,
F3.3, F3.P1 e F3.P2, nos dois cortes e empilhado. S6 fica fora do BKY.

<!-- E7:principal:inicio -->
(gerado pelo script)
<!-- E7:principal:fim -->

Figuras: `output/rdd_bolsa/E7_figuras/E7_dird_<outcome>_<população>.png`.

## 5. Sensibilidades e IC honesto

<!-- E7:sensibilidades:inicio -->
(gerado pelo script)
<!-- E7:sensibilidades:fim -->

<!-- E7:honesto:inicio -->
(gerado pelo script)
<!-- E7:honesto:fim -->

## 6. Placebo dentro do pré

Não é um nulo limpo: o IED da APS começou em 05/2024, o incentivo de nutrição
em 11/2024 e as emendas de 2025 em 04–05/2025 (auditoria 18, §3.1).

<!-- E7:placebo_pre:inicio -->
(gerado pelo script)
<!-- E7:placebo_pre:fim -->

## 7. RDD em nível: o pacote do corte

<!-- E7:niveis:inicio -->
(gerado pelo script)
<!-- E7:niveis:fim -->

Figuras: `output/rdd_bolsa/E7_figuras/E7_nivel_<outcome>_<população>.png`.

## 8. Pré extra (S5)

`S5_pre_menos_pre_extra` testa se a descontinuidade se moveu entre 2022–2023 e
o pré principal, antes do PMM-E; `S5_dird_pre_extra` é a DiRD com o pré extra.
O pré extra antecede todas as regras com corte em 0,3 ou 0,4 encontradas, mas
contém as Portarias 377/2022 e 1.054/2022, que usam o IVS dentro de índice
composto (auditoria 18, §3.2).

<!-- E7:s5:inicio -->
(gerado pelo script)
<!-- E7:s5:fim -->

## 9. Estudo de evento

Salto da RDD de (Y_t − Y_2025-06) em cada competência. Resumo por janela:

<!-- E7:evento:inicio -->
(gerado pelo script)
<!-- E7:evento:fim -->

Figuras: `output/rdd_bolsa/E7_figuras/E7_evento_<outcome>_<população>.png`,
com as datas da Portaria 752/2023, da Portaria 3.493/2024 (parcela de
05/2024), do quadro e do início do ciclo 1 e do edital e início do ciclo 2
(tracejado), e das demais regras da auditoria 18 (pontilhado).

## 10. Heterogeneidade pelas co-políticas (S3 e S4)

S3: portes em que o estrato do IED muda no corte contra os em que não muda
(Anexo VI da Portaria 3.493/2024). S4 (só 0,400): dentro contra fora da
Amazônia Legal ou faixa de fronteira, onde a ajuda de custo do PMMB não salta.

<!-- E7:s3_s4:inicio -->
(gerado pelo script)
<!-- E7:s3_s4:fim -->

## 11. Leitura

(preenchida depois da execução, sem números digitados)

## 12. Limites

- **Vínculo no CNES não é médico do PMM-E.** O grupo `alvo_pmme` conta todos os
  vínculos nas CBO-alvo, de qualquer programa ou contratação. O E7 mede oferta
  cadastrada local, não a presença do especialista do PMM-E (isso é F2, no E6).
- **Ponte curso–CBO operacional.** As CBO-alvo vêm da ponte
  `ponte_curso_cbo_oficial.json`, que não é crosswalk oficial; cursos diferentes
  compartilham CBO, e especialistas fora do PMM-E nas mesmas CBO entram no
  outcome.
- **Vínculo não é retenção.** O painel conta vínculos e profissionais distintos
  por município e mês; não segue a pessoa. Quem atua em dois municípios conta
  nos dois. Persistência de oferta não equivale a retenção individual.
- **Cadastro não é atendimento:** vínculo e carga horária são declarados.
- **Co-políticas variáveis no tempo** (§1) ameaçam a DiRD nos dois cortes; o
  canal da MAC em 0,300 não tem outcome próprio aqui (auditoria 18, recomendação
  9).
- **Pós curto e acumulado:** o pós junta os ciclos 1 e 2 e termina em 2026-08.

## 13. Desvios e esclarecimentos

<!-- E7:desvios:inicio -->
(gerado pelo script)
<!-- E7:desvios:fim -->

## 14. Proveniência e validações

<!-- E7:validacoes:inicio -->
(gerado pelo script)
<!-- E7:validacoes:fim -->

<!-- E7:entradas:inicio -->
(gerado pelo script)
<!-- E7:entradas:fim -->

## 15. Reprodução

```bash
python3 scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py --somente-validar   # esquema do painel, sem estimar
python3 scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py                     # estimação, saídas e tabelas do doc
python3 -m unittest tests.test_e7_dird
```
