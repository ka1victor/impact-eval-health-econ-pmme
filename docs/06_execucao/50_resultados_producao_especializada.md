# 50 — Resultados da produção especializada (família K: D1 nos cortes da bolsa e D2 na chegada do especialista)

> **Protocolo:** [`47_protocolo_producao_especializada.md`](47_protocolo_producao_especializada.md),
> congelado em 19/10/2026, com os adendos §10 (depois da aquisição do SIA e do
> SIH) e §11 (depois da aquisição do TISS), ambos anteriores a qualquer
> contraste; desenho do D1 igual ao do E7 (protocolo
> [`40`](40_protocolo_multioutcome_rdd_bolsa.md), §5–§6 e §13).<br>
> **Scripts:** [`scripts/rdd_bolsa/21_producao_dird.py`](../../scripts/rdd_bolsa/21_producao_dird.py) (D1) e
> [`scripts/rdd_bolsa/22_chegada_pmme_evento.py`](../../scripts/rdd_bolsa/22_chegada_pmme_evento.py) (D2),
> com os estimadores de [`rdd_lib.py`](../../scripts/rdd_bolsa/rdd_lib.py) e as funções do E7
> ([`14_estimar_E7_dird_cnes.py`](../../scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py)).<br>
> **Saídas:** `output/rdd_bolsa/K_D1_estimativas.csv`, `K_D1_estudo_evento.csv`,
> `K_D1_resumo.json`, `K_D1_figuras/`; `K_D2_att_gt.csv`, `K_D2_estudo_evento.csv`,
> `K_D2_estimativas.csv`, `K_D2_resumo.json`, `K_D2_figuras/`. Natureza dos dados:
> **EMPIRICO**. Estatuto: `PROTOCOLO_47_POS_SINTESE` (D1) e
> `EXPLORATORIO_PARTICIPACAO` (D2), em toda linha.<br>
> **Números:** todo número de resultado está entre marcadores `<!-- K:...-->`
> (gerados por `python3 scripts/rdd_bolsa/21_producao_dird.py --atualizar-doc`) ou
> `<!-- KD2:...-->` (por `python3 scripts/rdd_bolsa/22_chegada_pmme_evento.py --atualizar-doc`),
> e `tests/test_producao_K.py` confere que o doc bate com os CSV. Fora deles o
> texto só tem parâmetros do protocolo.<br>
> **Estatuto:** teste posterior à síntese E8 (doc 44) e à rodada X (doc 46). A
> família K tem Holm próprio (K1–K3) e **não altera** o Holm de P1 e P2 do
> protocolo 40.

## 1. O que se mede, na cadeia da política

Na cadeia implementação → força de trabalho → capacidade → **acesso** → saúde,
a família K fica na margem do acesso: a **produção** de consultas, exames e
cirurgias que exigem médico especialista, no município onde o serviço é
prestado. Não é tempo de espera (a regulação não é pública), não é saúde e não
é retenção individual.

| Margem | Fonte | O que conta | O que não conta |
|---|---|---|---|
| SUS ambulatorial (K1, K1a–K1f, K3b, KP1, KP2) | SIA/SUS, TabNet, município de atendimento, **mês de processamento** | quantidade aprovada pelo SUS (inclusive prestador privado contratado) com o CBO do executante | produção paga fora do SUS |
| SUS hospitalar (K2) | SIH/SUS, TabNet, município de internação, mês de processamento | AIH aprovadas do grupo 04 (cirúrgico) | o CBO de quem opera (o TabNet não filtra) |
| Planos de saúde (K3a, K3c; parte de K3 e K5) | TISS/ANS, município do prestador, **mês de realização** | quantidade informada pelos planos, com o CBO do evento (só ambulatorial) | pagamento do próprio bolso |
| Capacidade privada (K4) | CNES nacional | vínculos e horas **não SUS** das CBO-alvo | produção |

"Exige especialista" = o CBO do executante é uma das CBO-alvo dos cursos do
PMM-E (`alvo_pmme`, regra importada do a09). Os grupos de procedimento seguem o
§3.2 e o §10.2 do protocolo: consultas = subgrupo 0301; exames = grupo 02;
cirurgias = grupo 04; OCI (Ofertas de Cuidados Integrados) = grupo 09, que
entra em K1 porque substitui procedimentos antes cobrados um a um. Unidade:
município × mês; taxa por 10 mil habitantes (Censo 2022) por mês.

## 2. O que cada desenho identifica

- **D1 (DiRD nos cortes 0,300 e 0,400).** Para cada município, ΔY = média
  mensal do pós − média mensal do pré; RDD local linear de ΔY no corte (kernel
  triangular, h = 0,050). O salto mede o **incentivo marginal anunciado de
  R$ 5 mil por mês** (lado de bolsa maior − lado de bolsa menor) **mais** o
  que mudou, entre pré e pós, nas descontinuidades das outras políticas com o
  mesmo corte ([`auditorias/18`](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)):
  teto do PMMB, estrato da APS, emendas e incrementos de MAC e APS, ajuda de
  custo do PMMB. A diferença remove só a parte dessas políticas que é fixa no
  tempo. **Não é efeito da participação no PMM-E** nem do Agora Tem
  Especialistas. As linhas `nivel_*` (RDD em nível) medem o pacote do corte.
- **D2 (chegada do especialista, exploratório).** Entre os municípios que
  ofereceram células nos ciclos 1 ou 2, compara a mudança da produção nos que
  receberam o 1º especialista do PMM-E com a dos que ainda não tinham recebido
  (Callaway e Sant'Anna, 2021). É um **ATT sob tendências paralelas**, não um
  efeito com fonte de exogeneidade validada: quem chega escolhe o município. Se
  o pré não é plano, a leitura é só associativa.

## 3. Dados, zeros e ausências

- **Zero e ausente.** No SIA, `-` do TabNet é zero e subgrupo que não veio como
  coluna é zero daquela consulta (validação V4 do a12); município ausente da
  resposta seria ausente (não houve). No SIH, UF-mês sem dado
  (`ausente_uf_mes_sem_dado`) fica ausente; UF-mês atípico fica na amostra e
  sai só na sensibilidade. No TISS, `ausente_*` fica ausente e
  `arquivo_presente_municipio_sem_evento` é zero de eventos reportados. Nada é
  imputado; o principal usa a média dos meses com dado e a especificação
  `media_completa` só os municípios com todos os meses.
- **Janelas** (§4, §10.1, §11): pré jun/2024–jun/2025 em todos; pós de K1, K2,
  das secundárias SIA/SIH e de K4 out/2025–mai/2026 (os dois últimos meses do
  SIA e do SIH são imaturos; o pós até jul/2026 é sensibilidade, e K4 também
  tem o pós do E7, até ago/2026); pós de K3, K3a, K3b, K3c e K5
  out/2025–dez/2025 (o TISS acaba em dez/2025; out–nov/2025 é sensibilidade).
  Placebo dentro do pré (KP3): dez/2024–mai/2025 contra jun–nov/2024. Pré
  extra (S5): jan/2022–mar/2023. Nenhum mês CNES a partir de set/2026 é lido.
- **Populações:** U = todos os municípios com IVS 2010 oficial (a08) e
  população 2022, principal; V1 = municípios do quadro do ciclo 1,
  secundária. Município sem IVS ou sem população fica fora e é contado
  (tabela de validações).

<!-- K:validacoes:inicio -->
| Conferência | Resultado |
|---|---|
| SHA-256 dos painéis SIA, SIH, TISS (amb. e hosp.) e CNES = manifestos | True |
| municípios em U (IVS oficial e população 2022) / em V1 | 5565 / 368 |
| U sem população 2022 (fora) | 0 |
| municípios do Censo 2022 sem IVS oficial (fora) | 150475, 421265, 422000, 431454, 500627 |
| municípios do SIA fora de U (fora, sem IVS ou população) | 150475, 421265, 422000, 431454, 500627, 510183 |
| municípios do SIH fora de U | 150475, 421265, 422000, 431454, 500627, 510183 |
| células SIA ausentes (município × mês × conjunto × tipo) | 0 |
| UF-meses SIH sem dado (ausentes) | 12\|202607, 14\|202607 |
| UF-meses SIH atípicos (só na sensibilidade) | 14\|202206, 14\|202309, 14\|202606 |
| células TISS ausentes (amb. / hosp.) | 0 / 0 |
| UF-meses TISS sinalizados (amb.; só na sensibilidade) | 11 |
| maior mês lido: SIA e SIH / TISS / CNES | 202607 / 202512 / 202608 |
| linhas em K_D1_estimativas.csv / SEM_ESTIMATIVA / NAO_EXECUTADO | 1758 / 6 / 0 |
| linhas em K_D1_estudo_evento.csv | 3387 |
<!-- K:validacoes:fim -->

## 4. D1 — primárias (Holm entre K1, K2 e K3)

Linha principal: U, cortes empilhados. O efeito relativo divide o salto pela
média mensal do pré dos municípios logo abaixo do corte; o MDE é 2,8 × EP (80%
de poder a 5%).

<!-- K:primarias:inicio -->
| Outcome | n abaixo / acima | Salto (por 10 mil hab./mês) | IC 95% (CR1) | p | p Holm | IC honesto (M) | MDE (2,8 × EP) | Efeito relativo [IC 95%] | Média do pré abaixo do corte |
|---|---|---|---|---|---|---|---|---|---|
| K1 | 1446 / 1257 | +7,92 | [−27,58; +43,42] | 0,662 | **1,000** | [−929,32; +945,16] | 50,72 | +2,7 % [−9,6; +15,1] | 288,29 |
| K2 | 1446 / 1257 | +0,42 | [−0,58; +1,41] | 0,415 | **1,000** | [−64,03; +64,86] | 1,43 | +3,8 % [−5,4; +13,1] | 10,81 |
| K3 | 1446 / 1257 | −1,85 | [−22,90; +19,19] | 0,863 | **1,000** | [−549,98; +546,27] | 30,07 | −1,3 % [−16,1; +13,5] | 141,89 |
<!-- K:primarias:fim -->

<!-- K:leitura_primarias:inicio -->
Produção SUS ambulatorial das CBO-alvo (K1): salto +7,92 por 10 mil hab. por mês (IC 95% [−27,58; +43,42], p = 0,662, p de Holm = 1,000); a média mensal do pré abaixo do corte é 288,29, então o salto equivale a +2,7 % [−9,6; +15,1] dela; o menor efeito que o desenho detectaria com 80% de poder é 50,72 (17,6 % da média). Cirurgias SUS hospitalares (K2): salto +0,42 por 10 mil hab. por mês (IC 95% [−0,58; +1,41], p = 0,415, p de Holm = 1,000); a média mensal do pré abaixo do corte é 10,81, então o salto equivale a +3,8 % [−5,4; +13,1] dela; o menor efeito que o desenho detectaria com 80% de poder é 1,43 (13,2 % da média). Consultas especializadas SUS + planos (K3): salto −1,85 por 10 mil hab. por mês (IC 95% [−22,90; +19,19], p = 0,863, p de Holm = 1,000); a média mensal do pré abaixo do corte é 141,89, então o salto equivale a −1,3 % [−16,1; +13,5] dela; o menor efeito que o desenho detectaria com 80% de poder é 30,07 (21,2 % da média). Nenhuma das 3 primárias rejeita zero a 5% depois do Holm.
<!-- K:leitura_primarias:fim -->

<!-- K:leitura_simples:inicio -->
Em linguagem simples: a pergunta é se, nos municípios logo acima de 0,300 ou de 0,400, onde a bolsa anunciada é R$ 5 mil maior, a produção que exige especialista cresceu mais entre antes e depois do início do PMM-E do que nos municípios logo abaixo. Consultas, exames, cirurgias e OCI feitos no SUS pelos especialistas-alvo (K1): não se vê diferença entre os dois lados; o IC 95% vai de −9,6 % a +15,1 % da produção média do pré abaixo do corte, e uma diferença menor que cerca de 17,6 % dela não seria detectada; cirurgias com internação no SUS (K2): não se vê diferença entre os dois lados; o IC 95% vai de −5,4 % a +13,1 % da produção média do pré abaixo do corte, e uma diferença menor que cerca de 13,2 % dela não seria detectada; consultas dos especialistas-alvo no SUS e nos planos de saúde, somadas (K3): não se vê diferença entre os dois lados; o IC 95% vai de −16,1 % a +13,5 % da produção média do pré abaixo do corte, e uma diferença menor que cerca de 21,2 % dela não seria detectada. Um intervalo que inclui zero não prova que a bolsa não tem efeito: diz que, com estes municípios e estes meses, um efeito do tamanho que o intervalo admite não se distingue de zero. E mesmo um salto nítido mediria o incentivo marginal de R$ 5 mil somado ao que outras políticas com o mesmo corte mudaram no período, não o efeito de ter um especialista do PMM-E.
<!-- K:leitura_simples:fim -->

Por corte e em V1:

<!-- K:primarias_cortes:inicio -->
| Outcome | População | Corte | n abaixo / acima | Salto | IC 95% | p | IC honesto (M) | MDE | Efeito relativo [IC 95%] |
|---|---|---|---|---|---|---|---|---|---|
| K1 | U | 0,300 | 859 / 654 | −3,96 | [−54,68; +46,75] | 0,878 | [−945,19; +937,27] | 72,45 | −1,1 % [−15,7; +13,4] |
| K1 | U | 0,400 | 587 / 603 | +23,16 | [−25,23; +71,56] | 0,348 | [−801,85; +848,18] | 69,13 | +11,6 % [−12,7; +35,9] |
| K1 | U | empilhado | 1446 / 1257 | +7,92 | [−27,58; +43,42] | 0,662 | [−929,32; +945,16] | 50,72 | +2,7 % [−9,6; +15,1] |
| K1 | V1 | 0,300 | 61 / 53 | −18,85 | [−200,64; +162,93] | 0,839 | [−2418,22; +2380,52] | 259,70 | −2,2 % [−23,4; +19,0] |
| K1 | V1 | 0,400 | 53 / 41 | +185,37 | [−199,05; +569,78] | 0,345 | [−2669,96; +3040,70] | 549,17 | +30,3 % [−32,6; +93,2] |
| K1 | V1 | empilhado | 114 / 94 | +93,05 | [−129,84; +315,95] | 0,413 | [−3416,96; +3603,07] | 318,43 | +12,5 % [−17,5; +42,5] |
| K2 | U | 0,300 | 859 / 654 | +0,42 | [−0,64; +1,48] | 0,441 | [−21,54; +22,37] | 1,52 | +3,5 % [−5,4; +12,5] |
| K2 | U | 0,400 | 587 / 603 | +0,41 | [−1,41; +2,24] | 0,659 | [−65,51; +66,34] | 2,61 | +4,4 % [−15,3; +24,1] |
| K2 | U | empilhado | 1446 / 1257 | +0,42 | [−0,58; +1,41] | 0,415 | [−64,03; +64,86] | 1,43 | +3,8 % [−5,4; +13,1] |
| K2 | V1 | 0,300 | 61 / 53 | +0,56 | [−7,92; +9,03] | 0,897 | [−180,51; +181,63] | 12,11 | +1,3 % [−18,9; +21,6] |
| K2 | V1 | 0,400 | 53 / 41 | +2,97 | [−10,90; +16,85] | 0,674 | [−168,54; +174,49] | 19,82 | +6,9 % [−25,2; +38,9] |
| K2 | V1 | empilhado | 114 / 94 | +1,88 | [−6,62; +10,39] | 0,664 | [−216,11; +219,88] | 12,15 | +4,4 % [−15,6; +24,5] |
| K3 | U | 0,300 | 859 / 654 | −19,45 | [−47,00; +8,10] | 0,166 | [−318,96; +280,06] | 39,36 | −10,8 % [−26,0; +4,5] |
| K3 | U | 0,400 | 587 / 603 | +20,73 | [−11,71; +53,17] | 0,210 | [−543,53; +584,99] | 46,35 | +24,4 % [−13,8; +62,7] |
| K3 | U | empilhado | 1446 / 1257 | −1,85 | [−22,90; +19,19] | 0,863 | [−549,98; +546,27] | 30,07 | −1,3 % [−16,1; +13,5] |
| K3 | V1 | 0,300 | 61 / 53 | +17,34 | [−41,61; +76,29] | 0,564 | [−1883,42; +1918,09] | 84,22 | +3,8 % [−9,0; +16,5] |
| K3 | V1 | 0,400 | 53 / 41 | +90,15 | [−121,38; +301,68] | 0,404 | [−922,89; +1103,19] | 302,19 | +35,5 % [−47,8; +118,7] |
| K3 | V1 | empilhado | 114 / 94 | +57,24 | [−59,80; +174,27] | 0,338 | [−1469,97; +1584,44] | 167,20 | +15,7 % [−16,4; +47,8] |
<!-- K:primarias_cortes:fim -->

### 4.1 Robustez das primárias

`media_completa` = só municípios com todos os meses; `sensibilidade_h` com
h = 0,035 e 0,075; `poisson_dird` = Poisson local nas contagens da janela com
exposição = população × meses (salto em log; o efeito relativo é exp(salto) − 1);
`S2_donut` sem os municípios com IVS exatamente no corte; `sens|...` são as
variantes dos adendos (§10: até jul/2026 e sem o grupo 09; §11: pós só
out–nov/2025 e sem as UF-meses sinalizadas pela A14; sem as UF-meses atípicas
do SIH).

<!-- K:robustez:inicio -->
| Outcome | População | Corte | Especificação | n abaixo / acima | Salto | IC 95% | p | Efeito relativo |
|---|---|---|---|---|---|---|---|---|
| K1 | U | 0,300 | media_completa | 859 / 654 | −3,96 | [−54,68; +46,75] | 0,878 | −1,1 % [−15,7; +13,4] |
| K1 | U | 0,300 | sensibilidade_h h = 0,035 | 585 / 456 | −7,63 | [−66,17; +50,91] | 0,798 | −2,2 % [−18,9; +14,6] |
| K1 | U | 0,300 | sensibilidade_h h = 0,075 | 1303 / 954 | −6,82 | [−50,96; +37,32] | 0,762 | −2,0 % [−14,6; +10,7] |
| K1 | U | 0,300 | poisson_dird | 859 / 654 | −0,0032 (log) | [−0,1231; +0,1167] | 0,958 | −0,3 % [−11,6; +12,4] |
| K1 | U | 0,300 | S2_donut | 841 / 654 | −3,24 | [−58,05; +51,56] | 0,908 | −0,9 % [−16,6; +14,8] |
| K1 | U | 0,300 | sens\|pos_ate_202607 | 859 / 654 | +2,85 | [−49,00; +54,71] | 0,914 | +0,8 % [−14,0; +15,7] |
| K1 | U | 0,300 | sens\|sem_grupo_09 | 859 / 654 | −2,30 | [−52,44; +47,83] | 0,928 | −0,7 % [−15,0; +13,7] |
| K1 | U | 0,400 | media_completa | 587 / 603 | +23,16 | [−25,23; +71,56] | 0,348 | +11,6 % [−12,7; +35,9] |
| K1 | U | 0,400 | sensibilidade_h h = 0,035 | 407 / 412 | +21,68 | [−37,85; +81,21] | 0,475 | +10,9 % [−19,0; +40,8] |
| K1 | U | 0,400 | sensibilidade_h h = 0,075 | 896 / 896 | +15,38 | [−34,87; +65,62] | 0,549 | +7,7 % [−17,5; +33,0] |
| K1 | U | 0,400 | poisson_dird | 587 / 603 | +0,1995 (log) | [+0,0019; +0,3971] | 0,048 | +22,1 % [+0,2; +48,8] |
| K1 | U | 0,400 | S2_donut | 574 / 603 | +31,12 | [−16,02; +78,25] | 0,196 | +15,6 % [−8,0; +39,3] |
| K1 | U | 0,400 | sens\|pos_ate_202607 | 587 / 603 | +15,19 | [−30,69; +61,07] | 0,516 | +7,6 % [−15,4; +30,7] |
| K1 | U | 0,400 | sens\|sem_grupo_09 | 587 / 603 | +22,71 | [−25,54; +70,95] | 0,356 | +11,4 % [−12,8; +35,6] |
| K1 | U | empilhado | media_completa | 1446 / 1257 | +7,92 | [−27,58; +43,42] | 0,662 | +2,7 % [−9,6; +15,1] |
| K1 | U | empilhado | sensibilidade_h h = 0,035 | 992 / 868 | +5,17 | [−36,78; +47,12] | 0,809 | +1,8 % [−12,8; +16,3] |
| K1 | U | empilhado | sensibilidade_h h = 0,075 | 2199 / 1850 | +2,94 | [−30,11; +36,00] | 0,861 | +1,0 % [−10,4; +12,5] |
| K1 | U | empilhado | poisson_dird | 1446 / 1257 | +0,0358 (log) | [−0,0691; +0,1407] | 0,504 | +3,6 % [−6,7; +15,1] |
| K1 | U | empilhado | S2_donut | 1415 / 1257 | +11,79 | [−25,29; +48,87] | 0,533 | +4,1 % [−8,8; +17,0] |
| K1 | U | empilhado | sens\|pos_ate_202607 | 1446 / 1257 | +8,26 | [−27,13; +43,64] | 0,647 | +2,9 % [−9,4; +15,1] |
| K1 | U | empilhado | sens\|sem_grupo_09 | 1446 / 1257 | +8,65 | [−26,55; +43,85] | 0,630 | +3,0 % [−9,2; +15,2] |
| K1 | V1 | 0,300 | media_completa | 61 / 53 | −18,85 | [−200,64; +162,93] | 0,839 | −2,2 % [−23,4; +19,0] |
| K1 | V1 | 0,300 | sensibilidade_h h = 0,035 | 39 / 34 | −77,67 | [−235,69; +80,34] | 0,335 | −9,0 % [−27,4; +9,4] |
| K1 | V1 | 0,300 | sensibilidade_h h = 0,075 | 90 / 71 | +7,45 | [−193,93; +208,82] | 0,942 | +0,9 % [−22,6; +24,3] |
| K1 | V1 | 0,300 | poisson_dird | 61 / 53 | +0,0034 (log) | [−0,1558; +0,1626] | 0,967 | +0,3 % [−14,4; +17,7] |
| K1 | V1 | 0,300 | S2_donut | 61 / 53 | −18,85 | [−200,64; +162,93] | 0,839 | −2,2 % [−23,4; +19,0] |
| K1 | V1 | 0,300 | sens\|pos_ate_202607 | 61 / 53 | +2,13 | [−177,40; +181,66] | 0,981 | +0,2 % [−20,6; +21,1] |
| K1 | V1 | 0,300 | sens\|sem_grupo_09 | 61 / 53 | −10,31 | [−189,21; +168,60] | 0,910 | −1,2 % [−22,0; +19,6] |
| K1 | V1 | 0,400 | media_completa | 53 / 41 | +185,37 | [−199,05; +569,78] | 0,345 | +30,3 % [−32,6; +93,2] |
| K1 | V1 | 0,400 | sensibilidade_h h = 0,035 | 42 / 30 | +123,36 | [−254,52; +501,24] | 0,522 | +20,2 % [−41,6; +82,0] |
| K1 | V1 | 0,400 | sensibilidade_h h = 0,075 | 84 / 49 | +153,44 | [−337,57; +644,46] | 0,540 | +25,1 % [−55,2; +105,4] |
| K1 | V1 | 0,400 | poisson_dird | 53 / 41 | +0,2267 (log) | [−0,0861; +0,5396] | 0,156 | +25,4 % [−8,3; +71,5] |
| K1 | V1 | 0,400 | S2_donut | 50 / 41 | +240,50 | [−139,01; +620,02] | 0,214 | +39,3 % [−22,7; +101,4] |
| K1 | V1 | 0,400 | sens\|pos_ate_202607 | 53 / 41 | +113,23 | [−242,61; +469,06] | 0,533 | +18,5 % [−39,7; +76,7] |
| K1 | V1 | 0,400 | sens\|sem_grupo_09 | 53 / 41 | +182,96 | [−201,67; +567,60] | 0,351 | +29,9 % [−33,0; +92,9] |
| K1 | V1 | empilhado | media_completa | 114 / 94 | +93,05 | [−129,84; +315,95] | 0,413 | +12,5 % [−17,5; +42,5] |
| K1 | V1 | empilhado | sensibilidade_h h = 0,035 | 81 / 64 | +43,66 | [−188,31; +275,62] | 0,712 | +5,9 % [−25,3; +37,1] |
| K1 | V1 | empilhado | sensibilidade_h h = 0,075 | 174 / 120 | +83,25 | [−188,59; +355,10] | 0,548 | +11,2 % [−25,4; +47,7] |
| K1 | V1 | empilhado | poisson_dird | 114 / 94 | +0,0580 (log) | [−0,0899; +0,2060] | 0,442 | +6,0 % [−8,6; +22,9] |
| K1 | V1 | empilhado | S2_donut | 111 / 94 | +115,21 | [−97,47; +327,89] | 0,288 | +15,5 % [−13,1; +44,1] |
| K1 | V1 | empilhado | sens\|pos_ate_202607 | 114 / 94 | +63,01 | [−145,87; +271,88] | 0,554 | +8,5 % [−19,6; +36,5] |
| K1 | V1 | empilhado | sens\|sem_grupo_09 | 114 / 94 | +95,60 | [−126,99; +318,19] | 0,400 | +12,9 % [−17,1; +42,8] |
| K2 | U | 0,300 | media_completa | 859 / 654 | +0,42 | [−0,64; +1,48] | 0,441 | +3,5 % [−5,4; +12,5] |
| K2 | U | 0,300 | sensibilidade_h h = 0,035 | 585 / 456 | +1,04 | [−0,14; +2,22] | 0,085 | +8,7 % [−1,2; +18,7] |
| K2 | U | 0,300 | sensibilidade_h h = 0,075 | 1303 / 954 | −0,01 | [−1,03; +1,00] | 0,978 | −0,1 % [−8,7; +8,4] |
| K2 | U | 0,300 | poisson_dird | 859 / 654 | +0,0484 (log) | [−0,0088; +0,1056] | 0,097 | +5,0 % [−0,9; +11,1] |
| K2 | U | 0,300 | S2_donut | 841 / 654 | +0,50 | [−0,62; +1,61] | 0,381 | +4,2 % [−5,2; +13,5] |
| K2 | U | 0,300 | sens\|pos_ate_202607 | 859 / 654 | +0,59 | [−0,55; +1,74] | 0,311 | +5,0 % [−4,7; +14,6] |
| K2 | U | 0,300 | sens\|sem_uf_mes_atipico | 859 / 654 | +0,42 | [−0,64; +1,48] | 0,441 | +3,5 % [−5,4; +12,5] |
| K2 | U | 0,400 | media_completa | 587 / 603 | +0,41 | [−1,41; +2,24] | 0,659 | +4,4 % [−15,3; +24,1] |
| K2 | U | 0,400 | sensibilidade_h h = 0,035 | 407 / 412 | +1,25 | [−0,99; +3,48] | 0,276 | +13,4 % [−10,7; +37,6] |
| K2 | U | 0,400 | sensibilidade_h h = 0,075 | 896 / 896 | −0,21 | [−1,69; +1,27] | 0,780 | −2,3 % [−18,3; +13,7] |
| K2 | U | 0,400 | poisson_dird | 587 / 603 | −0,0933 (log) | [−0,2402; +0,0537] | 0,213 | −8,9 % [−21,4; +5,5] |
| K2 | U | 0,400 | S2_donut | 574 / 603 | −0,43 | [−2,04; +1,18] | 0,598 | −4,7 % [−22,1; +12,7] |
| K2 | U | 0,400 | sens\|pos_ate_202607 | 587 / 603 | +0,12 | [−1,80; +2,03] | 0,905 | +1,3 % [−19,4; +22,0] |
| K2 | U | 0,400 | sens\|sem_uf_mes_atipico | 587 / 603 | +0,41 | [−1,41; +2,24] | 0,659 | +4,4 % [−15,3; +24,1] |
| K2 | U | empilhado | media_completa | 1446 / 1257 | +0,42 | [−0,58; +1,41] | 0,415 | +3,8 % [−5,4; +13,1] |
| K2 | U | empilhado | sensibilidade_h h = 0,035 | 992 / 868 | +1,13 | [−0,05; +2,31] | 0,061 | +10,4 % [−0,5; +21,4] |
| K2 | U | empilhado | sensibilidade_h h = 0,075 | 2199 / 1850 | −0,10 | [−0,96; +0,76] | 0,819 | −0,9 % [−8,9; +7,1] |
| K2 | U | empilhado | poisson_dird | 1446 / 1257 | +0,0146 (log) | [−0,0416; +0,0708] | 0,611 | +1,5 % [−4,1; +7,3] |
| K2 | U | empilhado | S2_donut | 1415 / 1257 | +0,09 | [−0,85; +1,03] | 0,852 | +0,8 % [−7,9; +9,5] |
| K2 | U | empilhado | sens\|pos_ate_202607 | 1446 / 1257 | +0,38 | [−0,67; +1,44] | 0,477 | +3,5 % [−6,2; +13,3] |
| K2 | U | empilhado | sens\|sem_uf_mes_atipico | 1446 / 1257 | +0,42 | [−0,58; +1,41] | 0,415 | +3,8 % [−5,4; +13,1] |
| K2 | V1 | 0,300 | media_completa | 61 / 53 | +0,56 | [−7,92; +9,03] | 0,897 | +1,3 % [−18,9; +21,6] |
| K2 | V1 | 0,300 | sensibilidade_h h = 0,035 | 39 / 34 | +4,20 | [−3,64; +12,03] | 0,294 | +10,0 % [−8,7; +28,8] |
| K2 | V1 | 0,300 | sensibilidade_h h = 0,075 | 90 / 71 | −0,68 | [−9,54; +8,18] | 0,881 | −1,6 % [−22,8; +19,6] |
| K2 | V1 | 0,300 | poisson_dird | 61 / 53 | +0,0483 (log) | [−0,0426; +0,1391] | 0,298 | +4,9 % [−4,2; +14,9] |
| K2 | V1 | 0,300 | S2_donut | 61 / 53 | +0,56 | [−7,92; +9,03] | 0,897 | +1,3 % [−18,9; +21,6] |
| K2 | V1 | 0,300 | sens\|pos_ate_202607 | 61 / 53 | +0,68 | [−7,52; +8,88] | 0,871 | +1,6 % [−18,0; +21,3] |
| K2 | V1 | 0,300 | sens\|sem_uf_mes_atipico | 61 / 53 | +0,56 | [−7,92; +9,03] | 0,897 | +1,3 % [−18,9; +21,6] |
| K2 | V1 | 0,400 | media_completa | 53 / 41 | +2,97 | [−10,90; +16,85] | 0,674 | +6,9 % [−25,2; +38,9] |
| K2 | V1 | 0,400 | sensibilidade_h h = 0,035 | 42 / 30 | +8,64 | [−7,78; +25,05] | 0,302 | +20,0 % [−18,0; +57,9] |
| K2 | V1 | 0,400 | sensibilidade_h h = 0,075 | 84 / 49 | −1,62 | [−13,23; +10,00] | 0,785 | −3,7 % [−30,6; +23,1] |
| K2 | V1 | 0,400 | poisson_dird | 53 / 41 | −0,1641 (log) | [−0,3381; +0,0099] | 0,065 | −15,1 % [−28,7; +1,0] |
| K2 | V1 | 0,400 | S2_donut | 50 / 41 | −3,85 | [−15,62; +7,91] | 0,521 | −8,9 % [−36,1; +18,3] |
| K2 | V1 | 0,400 | sens\|pos_ate_202607 | 53 / 41 | +1,50 | [−12,85; +15,85] | 0,838 | +3,5 % [−29,7; +36,6] |
| K2 | V1 | 0,400 | sens\|sem_uf_mes_atipico | 53 / 41 | +2,97 | [−10,90; +16,85] | 0,674 | +6,9 % [−25,2; +38,9] |
| K2 | V1 | empilhado | media_completa | 114 / 94 | +1,88 | [−6,62; +10,39] | 0,664 | +4,4 % [−15,6; +24,5] |
| K2 | V1 | empilhado | sensibilidade_h h = 0,035 | 81 / 64 | +6,88 | [−3,52; +17,27] | 0,195 | +16,2 % [−8,3; +40,7] |
| K2 | V1 | empilhado | sensibilidade_h h = 0,075 | 174 / 120 | −1,16 | [−8,52; +6,19] | 0,756 | −2,7 % [−20,0; +14,6] |
| K2 | V1 | empilhado | poisson_dird | 114 / 94 | −0,0099 (log) | [−0,0934; +0,0736] | 0,816 | −1,0 % [−8,9; +7,6] |
| K2 | V1 | empilhado | S2_donut | 111 / 94 | −1,72 | [−9,03; +5,59] | 0,644 | −4,1 % [−21,3; +13,2] |
| K2 | V1 | empilhado | sens\|pos_ate_202607 | 114 / 94 | +1,13 | [−7,54; +9,80] | 0,799 | +2,7 % [−17,7; +23,1] |
| K2 | V1 | empilhado | sens\|sem_uf_mes_atipico | 114 / 94 | +1,88 | [−6,62; +10,39] | 0,664 | +4,4 % [−15,6; +24,5] |
| K3 | U | 0,300 | media_completa | 859 / 654 | −19,45 | [−47,00; +8,10] | 0,166 | −10,8 % [−26,0; +4,5] |
| K3 | U | 0,300 | sensibilidade_h h = 0,035 | 585 / 456 | −23,57 | [−56,82; +9,68] | 0,165 | −13,0 % [−31,4; +5,4] |
| K3 | U | 0,300 | sensibilidade_h h = 0,075 | 1303 / 954 | −15,07 | [−37,64; +7,51] | 0,191 | −8,3 % [−20,8; +4,2] |
| K3 | U | 0,300 | poisson_dird | 859 / 654 | +0,0046 (log) | [−0,0780; +0,0872] | 0,913 | +0,5 % [−7,5; +9,1] |
| K3 | U | 0,300 | S2_donut | 841 / 654 | −20,66 | [−51,09; +9,78] | 0,183 | −11,4 % [−28,2; +5,4] |
| K3 | U | 0,300 | sens\|pos_202510_202511 | 859 / 654 | −22,69 | [−57,75; +12,38] | 0,205 | −12,5 % [−31,9; +6,8] |
| K3 | U | 0,300 | sens\|sem_uf_mes_atipico | 859 / 653 | −19,54 | [−47,09; +8,02] | 0,165 | −10,8 % [−26,0; +4,4] |
| K3 | U | 0,400 | media_completa | 587 / 603 | +20,73 | [−11,71; +53,17] | 0,210 | +24,4 % [−13,8; +62,7] |
| K3 | U | 0,400 | sensibilidade_h h = 0,035 | 407 / 412 | +13,35 | [−22,58; +49,28] | 0,467 | +15,7 % [−26,6; +58,1] |
| K3 | U | 0,400 | sensibilidade_h h = 0,075 | 896 / 896 | +24,04 | [−8,05; +56,14] | 0,142 | +28,4 % [−9,5; +66,2] |
| K3 | U | 0,400 | poisson_dird | 587 / 603 | +0,1777 (log) | [−0,0671; +0,4224] | 0,155 | +19,4 % [−6,5; +52,6] |
| K3 | U | 0,400 | S2_donut | 574 / 603 | +20,15 | [−12,93; +53,24] | 0,232 | +23,8 % [−15,2; +62,8] |
| K3 | U | 0,400 | sens\|pos_202510_202511 | 587 / 603 | +25,15 | [−7,60; +57,90] | 0,132 | +29,7 % [−9,0; +68,3] |
| K3 | U | 0,400 | sens\|sem_uf_mes_atipico | 587 / 600 | +20,74 | [−11,69; +53,18] | 0,210 | +24,5 % [−13,8; +62,7] |
| K3 | U | empilhado | media_completa | 1446 / 1257 | −1,85 | [−22,90; +19,19] | 0,863 | −1,3 % [−16,1; +13,5] |
| K3 | U | empilhado | sensibilidade_h h = 0,035 | 992 / 868 | −7,45 | [−31,92; +17,02] | 0,551 | −5,2 % [−22,5; +12,0] |
| K3 | U | empilhado | sensibilidade_h h = 0,075 | 2199 / 1850 | +2,14 | [−16,50; +20,78] | 0,822 | +1,5 % [−11,6; +14,6] |
| K3 | U | empilhado | poisson_dird | 1446 / 1257 | +0,0289 (log) | [−0,0509; +0,1088] | 0,477 | +2,9 % [−5,0; +11,5] |
| K3 | U | empilhado | S2_donut | 1415 / 1257 | −2,80 | [−25,25; +19,65] | 0,807 | −2,0 % [−17,8; +13,9] |
| K3 | U | empilhado | sens\|pos_202510_202511 | 1446 / 1257 | −1,74 | [−26,16; +22,69] | 0,889 | −1,2 % [−18,4; +16,0] |
| K3 | U | empilhado | sens\|sem_uf_mes_atipico | 1446 / 1253 | −1,90 | [−22,94; +19,15] | 0,860 | −1,3 % [−16,2; +13,5] |
| K3 | V1 | 0,300 | media_completa | 61 / 53 | +17,34 | [−41,61; +76,29] | 0,564 | +3,8 % [−9,0; +16,5] |
| K3 | V1 | 0,300 | sensibilidade_h h = 0,035 | 39 / 34 | +32,23 | [−40,11; +104,56] | 0,383 | +7,0 % [−8,7; +22,7] |
| K3 | V1 | 0,300 | sensibilidade_h h = 0,075 | 90 / 71 | −0,51 | [−50,78; +49,76] | 0,984 | −0,1 % [−11,0; +10,8] |
| K3 | V1 | 0,300 | poisson_dird | 61 / 53 | +0,0607 (log) | [−0,0063; +0,1277] | 0,076 | +6,3 % [−0,6; +13,6] |
| K3 | V1 | 0,300 | S2_donut | 61 / 53 | +17,34 | [−41,61; +76,29] | 0,564 | +3,8 % [−9,0; +16,5] |
| K3 | V1 | 0,300 | sens\|pos_202510_202511 | 61 / 53 | +30,41 | [−42,01; +102,83] | 0,411 | +6,6 % [−9,1; +22,3] |
| K3 | V1 | 0,300 | sens\|sem_uf_mes_atipico | 61 / 52 | +16,14 | [−42,99; +75,26] | 0,593 | +3,5 % [−9,3; +16,3] |
| K3 | V1 | 0,400 | media_completa | 53 / 41 | +90,15 | [−121,38; +301,68] | 0,404 | +35,5 % [−47,8; +118,7] |
| K3 | V1 | 0,400 | sensibilidade_h h = 0,035 | 42 / 30 | −12,54 | [−105,66; +80,58] | 0,792 | −4,9 % [−41,6; +31,7] |
| K3 | V1 | 0,400 | sensibilidade_h h = 0,075 | 84 / 49 | +146,26 | [−160,55; +453,07] | 0,350 | +57,6 % [−63,2; +178,3] |
| K3 | V1 | 0,400 | poisson_dird | 53 / 41 | +0,1949 (log) | [−0,0933; +0,4831] | 0,185 | +21,5 % [−8,9; +62,1] |
| K3 | V1 | 0,400 | S2_donut | 50 / 41 | +92,74 | [−119,17; +304,65] | 0,391 | +36,5 % [−46,9; +119,9] |
| K3 | V1 | 0,400 | sens\|pos_202510_202511 | 53 / 41 | +89,35 | [−120,61; +299,31] | 0,404 | +35,2 % [−47,5; +117,8] |
| K3 | V1 | 0,400 | sens\|sem_uf_mes_atipico | 53 / 40 | +88,85 | [−119,80; +297,51] | 0,404 | +35,0 % [−47,2; +117,1] |
| K3 | V1 | empilhado | media_completa | 114 / 94 | +57,24 | [−59,80; +174,27] | 0,338 | +15,7 % [−16,4; +47,8] |
| K3 | V1 | empilhado | sensibilidade_h h = 0,035 | 81 / 64 | +5,21 | [−58,65; +69,07] | 0,873 | +1,4 % [−16,1; +18,9] |
| K3 | V1 | empilhado | sensibilidade_h h = 0,075 | 174 / 120 | +75,70 | [−83,50; +234,90] | 0,351 | +20,7 % [−22,9; +64,4] |
| K3 | V1 | empilhado | poisson_dird | 114 / 94 | +0,0779 (log) | [+0,0073; +0,1485] | 0,031 | +8,1 % [+0,7; +16,0] |
| K3 | V1 | empilhado | S2_donut | 111 / 94 | +56,31 | [−55,07; +167,69] | 0,322 | +15,4 % [−15,1; +46,0] |
| K3 | V1 | empilhado | sens\|pos_202510_202511 | 114 / 94 | +62,71 | [−55,06; +180,48] | 0,297 | +17,2 % [−15,1; +49,5] |
| K3 | V1 | empilhado | sens\|sem_uf_mes_atipico | 114 / 92 | +56,03 | [−59,60; +171,65] | 0,342 | +15,4 % [−16,3; +47,0] |
<!-- K:robustez:fim -->

IC honesto (Armstrong e Kolesár), M pela regra de bolso e 0,5M e 2M; a linha
`ic_honesto_h_otimo` é especificação adicional rotulada. Como no E7, o IC
honesto em h = 0,050 é muito mais largo que o convencional: a regra de bolso
ajusta uma quártica global à mudança por habitante em todo o suporte (até o
ponto médio entre os cortes), o M resultante é grande nessas unidades, e o viés
máximo cresce com M e com h (coluna M da tabela).
Ele diz o que sobra de incerteza se a curvatura for tão grande quanto a regra de
bolso admite:

<!-- K:honesto:inicio -->
| Outcome | População | Corte | Especificação | fator de M | M | h | IC honesto | p honesto |
|---|---|---|---|---|---|---|---|---|
| K1 | U | 0,300 | ic_honesto | 0,5 | 979775,3 | 0,050 | [−495,97; +488,05] | 1,000 |
| K1 | U | 0,300 | ic_honesto_h_otimo | 0,5 | 979775,3 | 0,020 | [−114,15; +153,59] | 0,912 |
| K1 | U | 0,300 | ic_honesto | 1,0 | 1959550,6 | 0,050 | [−945,19; +937,27] | 1,000 |
| K1 | U | 0,300 | ic_honesto_h_otimo | 1,0 | 1959550,6 | 0,020 | [−184,04; +223,48] | 0,999 |
| K1 | U | 0,300 | ic_honesto | 2,0 | 3919101,2 | 0,050 | [−1843,62; +1835,70] | 1,000 |
| K1 | U | 0,300 | ic_honesto_h_otimo | 2,0 | 3919101,2 | 0,020 | [−323,81; +363,25] | 1,000 |
| K1 | U | 0,400 | ic_honesto | 0,5 | 836589,7 | 0,050 | [−409,49; +455,82] | 1,000 |
| K1 | U | 0,400 | ic_honesto_h_otimo | 0,5 | 836589,7 | 0,020 | [−122,54; +116,05] | 0,985 |
| K1 | U | 0,400 | ic_honesto | 1,0 | 1673179,4 | 0,050 | [−801,85; +848,18] | 1,000 |
| K1 | U | 0,400 | ic_honesto_h_otimo | 1,0 | 1673179,4 | 0,020 | [−184,71; +178,23] | 1,000 |
| K1 | U | 0,400 | ic_honesto | 2,0 | 3346358,8 | 0,050 | [−1586,56; +1632,89] | 1,000 |
| K1 | U | 0,400 | ic_honesto_h_otimo | 2,0 | 3346358,8 | 0,020 | [−309,06; +302,58] | 1,000 |
| K1 | U | empilhado | ic_honesto | 0,5 | 979775,3 | 0,050 | [−475,60; +491,44] | 1,000 |
| K1 | U | empilhado | ic_honesto | 1,0 | 1959550,6 | 0,050 | [−929,32; +945,16] | 1,000 |
| K1 | U | empilhado | ic_honesto | 2,0 | 3919101,2 | 0,050 | [−1836,77; +1852,61] | 1,000 |
| K1 | V1 | 0,300 | ic_honesto | 0,5 | 1841692,0 | 0,050 | [−1293,84; +1256,14] | 1,000 |
| K1 | V1 | 0,300 | ic_honesto_h_otimo | 0,5 | 1841692,0 | 0,020 | [−563,52; +316,03] | 0,732 |
| K1 | V1 | 0,300 | ic_honesto | 1,0 | 3683384,1 | 0,050 | [−2418,22; +2380,52] | 1,000 |
| K1 | V1 | 0,300 | ic_honesto_h_otimo | 1,0 | 3683384,1 | 0,020 | [−770,50; +523,01] | 0,980 |
| K1 | V1 | 0,300 | ic_honesto | 2,0 | 7366768,1 | 0,050 | [−4666,98; +4629,28] | 1,000 |
| K1 | V1 | 0,300 | ic_honesto_h_otimo | 2,0 | 7366768,1 | 0,020 | [−1184,47; +936,98] | 1,000 |
| K1 | V1 | 0,400 | ic_honesto | 0,5 | 3525677,0 | 0,050 | [−1413,53; +1784,26] | 1,000 |
| K1 | V1 | 0,400 | ic_honesto_h_otimo | 0,5 | 3525677,0 | 0,020 | [−813,23; +458,77] | 0,615 |
| K1 | V1 | 0,400 | ic_honesto | 1,0 | 7051354,1 | 0,050 | [−2669,96; +3040,70] | 1,000 |
| K1 | V1 | 0,400 | ic_honesto_h_otimo | 1,0 | 7051354,1 | 0,020 | [−1019,04; +664,58] | 0,831 |
| K1 | V1 | 0,400 | ic_honesto | 2,0 | 14102708,2 | 0,050 | [−5182,84; +5553,57] | 1,000 |
| K1 | V1 | 0,400 | ic_honesto_h_otimo | 2,0 | 14102708,2 | 0,020 | [−1433,61; +1079,16] | 0,994 |
| K1 | V1 | empilhado | ic_honesto | 0,5 | 3525677,0 | 0,050 | [−1755,48; +1941,59] | 1,000 |
| K1 | V1 | empilhado | ic_honesto | 1,0 | 7051354,1 | 0,050 | [−3416,96; +3603,07] | 1,000 |
| K1 | V1 | empilhado | ic_honesto | 2,0 | 14102708,2 | 0,050 | [−6739,92; +6926,03] | 1,000 |
| K2 | U | 0,300 | ic_honesto | 0,5 | 22962,6 | 0,050 | [−11,01; +11,84] | 1,000 |
| K2 | U | 0,300 | ic_honesto_h_otimo | 0,5 | 22962,6 | 0,020 | [−1,10; +4,86] | 0,383 |
| K2 | U | 0,300 | ic_honesto | 1,0 | 45925,2 | 0,050 | [−21,54; +22,37] | 1,000 |
| K2 | U | 0,300 | ic_honesto_h_otimo | 1,0 | 45925,2 | 0,020 | [−2,74; +6,49] | 0,957 |
| K2 | U | 0,300 | ic_honesto | 2,0 | 91850,3 | 0,050 | [−42,59; +43,43] | 1,000 |
| K2 | U | 0,300 | ic_honesto_h_otimo | 2,0 | 91850,3 | 0,020 | [−6,01; +9,77] | 1,000 |
| K2 | U | 0,400 | ic_honesto | 0,5 | 68680,4 | 0,050 | [−33,30; +34,12] | 1,000 |
| K2 | U | 0,400 | ic_honesto_h_otimo | 0,5 | 68680,4 | 0,020 | [−4,60; +10,69] | 0,909 |
| K2 | U | 0,400 | ic_honesto | 1,0 | 137360,9 | 0,050 | [−65,51; +66,34] | 1,000 |
| K2 | U | 0,400 | ic_honesto_h_otimo | 1,0 | 137360,9 | 0,020 | [−9,70; +15,79] | 1,000 |
| K2 | U | 0,400 | ic_honesto | 2,0 | 274721,8 | 0,050 | [−129,93; +130,76] | 1,000 |
| K2 | U | 0,400 | ic_honesto_h_otimo | 2,0 | 274721,8 | 0,020 | [−19,91; +26,00] | 1,000 |
| K2 | U | empilhado | ic_honesto | 0,5 | 68680,4 | 0,050 | [−32,23; +33,06] | 1,000 |
| K2 | U | empilhado | ic_honesto | 1,0 | 137360,9 | 0,050 | [−64,03; +64,86] | 1,000 |
| K2 | U | empilhado | ic_honesto | 2,0 | 274721,8 | 0,050 | [−127,64; +128,47] | 1,000 |
| K2 | V1 | 0,300 | ic_honesto | 0,5 | 142292,9 | 0,050 | [−93,64; +94,76] | 1,000 |
| K2 | V1 | 0,300 | ic_honesto_h_otimo | 0,5 | 142292,9 | 0,020 | [−18,63; +37,81] | 0,806 |
| K2 | V1 | 0,300 | ic_honesto | 1,0 | 284585,9 | 0,050 | [−180,51; +181,63] | 1,000 |
| K2 | V1 | 0,300 | ic_honesto_h_otimo | 1,0 | 284585,9 | 0,020 | [−34,62; +53,80] | 0,999 |
| K2 | V1 | 0,300 | ic_honesto | 2,0 | 569171,7 | 0,050 | [−354,26; +355,37] | 1,000 |
| K2 | V1 | 0,300 | ic_honesto_h_otimo | 2,0 | 569171,7 | 0,020 | [−66,60; +85,79] | 1,000 |
| K2 | V1 | 0,400 | ic_honesto | 0,5 | 223720,0 | 0,050 | [−88,82; +94,77] | 1,000 |
| K2 | V1 | 0,400 | ic_honesto_h_otimo | 0,5 | 223720,0 | 0,020 | [−17,56; +46,58] | 0,461 |
| K2 | V1 | 0,400 | ic_honesto | 1,0 | 447439,9 | 0,050 | [−168,54; +174,49] | 1,000 |
| K2 | V1 | 0,400 | ic_honesto_h_otimo | 1,0 | 447439,9 | 0,020 | [−30,71; +59,73] | 0,848 |
| K2 | V1 | 0,400 | ic_honesto | 2,0 | 894879,9 | 0,050 | [−328,00; +333,95] | 1,000 |
| K2 | V1 | 0,400 | ic_honesto_h_otimo | 2,0 | 894879,9 | 0,020 | [−57,02; +86,04] | 1,000 |
| K2 | V1 | empilhado | ic_honesto | 0,5 | 223720,0 | 0,050 | [−110,68; +114,45] | 1,000 |
| K2 | V1 | empilhado | ic_honesto | 1,0 | 447439,9 | 0,050 | [−216,11; +219,88] | 1,000 |
| K2 | V1 | empilhado | ic_honesto | 2,0 | 894879,9 | 0,050 | [−426,97; +430,73] | 1,000 |
| K3 | U | 0,300 | ic_honesto | 0,5 | 301387,6 | 0,050 | [−180,78; +141,88] | 1,000 |
| K3 | U | 0,300 | ic_honesto_h_otimo | 0,5 | 301387,6 | 0,020 | [−81,29; +28,69] | 0,416 |
| K3 | U | 0,300 | ic_honesto | 1,0 | 602775,2 | 0,050 | [−318,96; +280,06] | 1,000 |
| K3 | U | 0,300 | ic_honesto_h_otimo | 1,0 | 602775,2 | 0,020 | [−102,77; +50,18] | 0,794 |
| K3 | U | 0,300 | ic_honesto | 2,0 | 1205550,5 | 0,050 | [−595,33; +556,43] | 1,000 |
| K3 | U | 0,300 | ic_honesto_h_otimo | 2,0 | 1205550,5 | 0,020 | [−145,77; +93,17] | 0,998 |
| K3 | U | 0,400 | ic_honesto | 0,5 | 572740,4 | 0,050 | [−274,92; +316,38] | 1,000 |
| K3 | U | 0,400 | ic_honesto_h_otimo | 0,5 | 572740,4 | 0,020 | [−65,13; +92,19] | 0,912 |
| K3 | U | 0,400 | ic_honesto | 1,0 | 1145480,7 | 0,050 | [−543,53; +584,99] | 1,000 |
| K3 | U | 0,400 | ic_honesto_h_otimo | 1,0 | 1145480,7 | 0,020 | [−107,69; +134,76] | 0,999 |
| K3 | U | 0,400 | ic_honesto | 2,0 | 2290961,5 | 0,050 | [−1080,76; +1122,21] | 1,000 |
| K3 | U | 0,400 | ic_honesto_h_otimo | 2,0 | 2290961,5 | 0,020 | [−192,83; +219,89] | 1,000 |
| K3 | U | empilhado | ic_honesto | 0,5 | 572740,4 | 0,050 | [−284,75; +281,04] | 1,000 |
| K3 | U | empilhado | ic_honesto | 1,0 | 1145480,7 | 0,050 | [−549,98; +546,27] | 1,000 |
| K3 | U | empilhado | ic_honesto | 2,0 | 2290961,5 | 0,050 | [−1080,44; +1076,73] | 1,000 |
| K3 | V1 | 0,300 | ic_honesto | 0,5 | 1516157,2 | 0,050 | [−957,78; +992,45] | 1,000 |
| K3 | V1 | 0,300 | ic_honesto_h_otimo | 0,5 | 1516157,2 | 0,020 | [−224,91; +300,52] | 0,991 |
| K3 | V1 | 0,300 | ic_honesto | 1,0 | 3032314,5 | 0,050 | [−1883,42; +1918,09] | 1,000 |
| K3 | V1 | 0,300 | ic_honesto_h_otimo | 1,0 | 3032314,5 | 0,020 | [−395,31; +470,92] | 1,000 |
| K3 | V1 | 0,300 | ic_honesto | 2,0 | 6064629,0 | 0,050 | [−3734,70; +3769,37] | 1,000 |
| K3 | V1 | 0,300 | ic_honesto_h_otimo | 2,0 | 6064629,0 | 0,020 | [−736,10; +811,72] | 1,000 |
| K3 | V1 | 0,400 | ic_honesto | 0,5 | 1149955,5 | 0,050 | [−513,08; +693,38] | 0,997 |
| K3 | V1 | 0,400 | ic_honesto_h_otimo | 0,5 | 1149955,5 | 0,035 | [−301,72; +276,64] | 1,000 |
| K3 | V1 | 0,400 | ic_honesto | 1,0 | 2299911,0 | 0,050 | [−922,89; +1103,19] | 1,000 |
| K3 | V1 | 0,400 | ic_honesto_h_otimo | 1,0 | 2299911,0 | 0,020 | [−473,05; +293,94] | 0,687 |
| K3 | V1 | 0,400 | ic_honesto | 2,0 | 4599822,0 | 0,050 | [−1742,50; +1922,80] | 1,000 |
| K3 | V1 | 0,400 | ic_honesto_h_otimo | 2,0 | 4599822,0 | 0,020 | [−607,84; +428,74] | 0,893 |
| K3 | V1 | empilhado | ic_honesto | 0,5 | 1516157,2 | 0,050 | [−755,48; +869,95] | 1,000 |
| K3 | V1 | empilhado | ic_honesto | 1,0 | 3032314,5 | 0,050 | [−1469,97; +1584,44] | 1,000 |
| K3 | V1 | empilhado | ic_honesto | 2,0 | 6064629,0 | 0,050 | [−2898,95; +3013,42] | 1,000 |
<!-- K:honesto:fim -->

RDD em nível (pacote do corte) e S5 (o salto mudou entre o pré extra e o pré,
antes do PMM-E?):

<!-- K:niveis_s5:inicio -->
| Outcome | Corte | Especificação | Salto | IC 95% | p |
|---|---|---|---|---|---|
| K1 | 0,300 | nivel_pre | −36,79 | [−158,44; +84,86] | 0,553 |
| K1 | 0,300 | nivel_pos | −40,75 | [−172,06; +90,57] | 0,543 |
| K1 | 0,300 | S5_pre_menos_pre_extra | −24,82 | [−94,36; +44,71] | 0,484 |
| K1 | 0,400 | nivel_pre | +50,39 | [−22,93; +123,71] | 0,178 |
| K1 | 0,400 | nivel_pos | +73,55 | [−23,01; +170,12] | 0,135 |
| K1 | 0,400 | S5_pre_menos_pre_extra | +23,95 | [−17,38; +65,28] | 0,256 |
| K1 | empilhado | nivel_pre | +1,39 | [−74,23; +77,02] | 0,971 |
| K1 | empilhado | nivel_pos | +9,31 | [−75,82; +94,45] | 0,830 |
| K1 | empilhado | S5_pre_menos_pre_extra | −3,46 | [−46,56; +39,64] | 0,875 |
| K2 | 0,300 | nivel_pre | −1,54 | [−5,52; +2,45] | 0,449 |
| K2 | 0,300 | nivel_pos | −1,12 | [−5,34; +3,10] | 0,603 |
| K2 | 0,300 | S5_pre_menos_pre_extra | +0,70 | [−0,78; +2,19] | 0,353 |
| K2 | 0,400 | nivel_pre | −1,02 | [−11,37; +9,32] | 0,846 |
| K2 | 0,400 | nivel_pos | −0,61 | [−10,13; +8,90] | 0,900 |
| K2 | 0,400 | S5_pre_menos_pre_extra | −0,72 | [−4,59; +3,15] | 0,714 |
| K2 | empilhado | nivel_pre | −1,31 | [−6,37; +3,74] | 0,610 |
| K2 | empilhado | nivel_pos | −0,90 | [−5,69; +3,90] | 0,713 |
| K2 | empilhado | S5_pre_menos_pre_extra | +0,08 | [−1,81; +1,97] | 0,935 |
| K3 | 0,300 | nivel_pre | −23,16 | [−70,59; +24,27] | 0,338 |
| K3 | 0,300 | nivel_pos | −42,61 | [−96,74; +11,51] | 0,123 |
| K3 | 0,300 | S5_pre_menos_pre_extra | −14,37 | [−38,99; +10,26] | 0,253 |
| K3 | 0,400 | nivel_pre | +21,09 | [−10,12; +52,31] | 0,185 |
| K3 | 0,400 | nivel_pos | +41,82 | [−3,94; +87,58] | 0,073 |
| K3 | 0,400 | S5_pre_menos_pre_extra | +5,37 | [−18,73; +29,48] | 0,662 |
| K3 | empilhado | nivel_pre | −3,78 | [−33,79; +26,23] | 0,805 |
| K3 | empilhado | nivel_pos | −5,63 | [−42,18; +30,92] | 0,763 |
| K3 | empilhado | S5_pre_menos_pre_extra | −5,72 | [−23,14; +11,69] | 0,520 |
| KP1 | 0,300 | nivel_pre | −234,17 | [−604,03; +135,68] | 0,215 |
| KP1 | 0,300 | nivel_pos | −270,87 | [−690,64; +148,91] | 0,206 |
| KP1 | 0,300 | S5_pre_menos_pre_extra | −179,86 | [−470,34; +110,63] | 0,225 |
| KP1 | 0,400 | nivel_pre | +248,54 | [−186,32; +683,41] | 0,263 |
| KP1 | 0,400 | nivel_pos | +199,62 | [−224,95; +624,18] | 0,357 |
| KP1 | 0,400 | S5_pre_menos_pre_extra | +160,81 | [−349,85; +671,47] | 0,537 |
| KP1 | empilhado | nivel_pre | −22,75 | [−305,48; +259,99] | 0,875 |
| KP1 | empilhado | nivel_pos | −64,80 | [−365,96; +236,36] | 0,673 |
| KP1 | empilhado | S5_pre_menos_pre_extra | −30,65 | [−307,90; +246,61] | 0,828 |
| KP2 | 0,300 | nivel_pre | +37,49 | [−130,52; +205,49] | 0,662 |
| KP2 | 0,300 | nivel_pos | +20,37 | [−171,27; +212,00] | 0,835 |
| KP2 | 0,300 | S5_pre_menos_pre_extra | +24,78 | [−63,71; +113,27] | 0,583 |
| KP2 | 0,400 | nivel_pre | −17,85 | [−128,54; +92,84] | 0,752 |
| KP2 | 0,400 | nivel_pos | −22,67 | [−133,46; +88,13] | 0,688 |
| KP2 | 0,400 | S5_pre_menos_pre_extra | −37,34 | [−93,21; +18,53] | 0,190 |
| KP2 | empilhado | nivel_pre | +13,25 | [−92,89; +119,38] | 0,807 |
| KP2 | empilhado | nivel_pos | +1,52 | [−116,61; +119,65] | 0,980 |
| KP2 | empilhado | S5_pre_menos_pre_extra | −2,43 | [−57,83; +52,98] | 0,932 |
<!-- K:niveis_s5:fim -->

S3 (porte em que o estrato da APS muda no corte × não muda) e S4 (em 0,400,
Amazônia Legal ou faixa de fronteira × fora):

<!-- K:s3_s4:inicio -->
| Outcome | Corte | Especificação | n abaixo / acima | Salto | IC 95% | p |
|---|---|---|---|---|---|---|
| K1 | 0,300 | S3_porte_muda | 185 / 109 | +20,60 | [−124,37; +165,57] | 0,781 |
| K1 | 0,300 | S3_porte_nao_muda | 674 / 545 | −11,08 | [−63,51; +41,36] | 0,679 |
| K1 | 0,300 | S3_diferenca | 859 / 654 | +31,67 | [−122,48; +185,83] | 0,687 |
| K1 | 0,400 | S3_porte_muda | 551 / 567 | +22,40 | [−27,52; +72,32] | 0,379 |
| K1 | 0,400 | S3_porte_nao_muda | 36 / 36 | −5,38 | [−170,91; +160,15] | 0,949 |
| K1 | 0,400 | S3_diferenca | 587 / 603 | +27,77 | [−145,12; +200,67] | 0,753 |
| K1 | 0,400 | S4_dentro | 135 / 87 | −71,97 | [−148,66; +4,72] | 0,066 |
| K1 | 0,400 | S4_fora | 452 / 516 | +44,14 | [−9,64; +97,92] | 0,108 |
| K1 | 0,400 | S4_diferenca | 587 / 603 | −116,11 | [−209,78; −22,44] | 0,015 |
| K2 | 0,300 | S3_porte_muda | 185 / 109 | +0,00 | [−4,33; +4,34] | 0,999 |
| K2 | 0,300 | S3_porte_nao_muda | 674 / 545 | +0,53 | [−0,31; +1,37] | 0,212 |
| K2 | 0,300 | S3_diferenca | 859 / 654 | −0,53 | [−4,95; +3,89] | 0,814 |
| K2 | 0,400 | S3_porte_muda | 551 / 567 | +1,14 | [−0,59; +2,86] | 0,196 |
| K2 | 0,400 | S3_porte_nao_muda | 36 / 36 | −11,84 | [−26,06; +2,38] | 0,103 |
| K2 | 0,400 | S3_diferenca | 587 / 603 | +12,98 | [−1,35; +27,31] | 0,076 |
| K2 | 0,400 | S4_dentro | 135 / 87 | −2,30 | [−4,78; +0,18] | 0,070 |
| K2 | 0,400 | S4_fora | 452 / 516 | +1,09 | [−1,09; +3,26] | 0,327 |
| K2 | 0,400 | S4_diferenca | 587 / 603 | −3,38 | [−6,68; −0,09] | 0,044 |
| K3 | 0,300 | S3_porte_muda | 185 / 109 | −18,73 | [−65,57; +28,10] | 0,433 |
| K3 | 0,300 | S3_porte_nao_muda | 674 / 545 | −19,62 | [−51,99; +12,74] | 0,235 |
| K3 | 0,300 | S3_diferenca | 859 / 654 | +0,89 | [−56,04; +57,82] | 0,976 |
| K3 | 0,400 | S3_porte_muda | 551 / 567 | +21,00 | [−13,18; +55,19] | 0,229 |
| K3 | 0,400 | S3_porte_nao_muda | 36 / 36 | +15,81 | [−34,71; +66,34] | 0,540 |
| K3 | 0,400 | S3_diferenca | 587 / 603 | +5,19 | [−55,82; +66,20] | 0,868 |
| K3 | 0,400 | S4_dentro | 135 / 87 | −1,83 | [−42,99; +39,32] | 0,930 |
| K3 | 0,400 | S4_fora | 452 / 516 | +24,71 | [−12,83; +62,24] | 0,197 |
| K3 | 0,400 | S4_diferenca | 587 / 603 | −26,54 | [−82,24; +29,17] | 0,350 |
<!-- K:s3_s4:fim -->

## 5. D1 — secundárias e placebos

Secundárias (q de BKY dentro de K, linha empilhada):

<!-- K:secundarias:inicio -->
| Outcome | Descrição | Corte | n abaixo / acima | Salto | IC 95% | p | q BKY | Efeito relativo [IC 95%] |
|---|---|---|---|---|---|---|---|---|
| K1a | K1, só consultas (0301) | 0,300 | 859 / 654 | −9,62 | [−38,87; +19,63] | 0,519 | — | −7,6 % [−30,8; +15,5] |
| K1a | K1, só consultas (0301) | 0,400 | 587 / 603 | +15,95 | [−16,19; +48,10] | 0,331 | — | +22,4 % [−22,7; +67,5] |
| K1a | K1, só consultas (0301) | empilhado | 1446 / 1257 | +1,58 | [−20,07; +23,23] | 0,886 | 1,000 | +1,5 % [−19,3; +22,3] |
| K1b | K1, só exames (grupo 02) | 0,300 | 859 / 654 | +6,83 | [−25,99; +39,65] | 0,683 | — | +3,1 % [−12,0; +18,3] |
| K1b | K1, só exames (grupo 02) | 0,400 | 587 / 603 | +7,43 | [−19,33; +34,19] | 0,586 | — | +5,9 % [−15,4; +27,3] |
| K1b | K1, só exames (grupo 02) | empilhado | 1446 / 1257 | +7,09 | [−14,76; +28,95] | 0,525 | 1,000 | +3,9 % [−8,2; +16,1] |
| K1c | K1, só cirurgias ambulatoriais (grupo 04) | 0,300 | 859 / 654 | +0,49 | [−1,26; +2,24] | 0,585 | — | +8,2 % [−21,2; +37,6] |
| K1c | K1, só cirurgias ambulatoriais (grupo 04) | 0,400 | 587 / 603 | −0,68 | [−2,23; +0,87] | 0,392 | — | −26,4 % [−86,7; +34,0] |
| K1c | K1, só cirurgias ambulatoriais (grupo 04) | empilhado | 1446 / 1257 | −0,02 | [−1,22; +1,18] | 0,970 | 1,000 | −0,5 % [−26,6; +25,6] |
| K1d | K1 com todos os especialistas (alvo + não alvo) | 0,300 | 859 / 654 | −21,08 | [−123,53; +81,36] | 0,687 | — | −2,8 % [−16,2; +10,7] |
| K1d | K1 com todos os especialistas (alvo + não alvo) | 0,400 | 587 / 603 | +18,35 | [−53,17; +89,87] | 0,615 | — | +4,2 % [−12,2; +20,7] |
| K1d | K1 com todos os especialistas (alvo + não alvo) | empilhado | 1446 / 1257 | −3,81 | [−69,33; +61,70] | 0,909 | 1,000 | −0,6 % [−11,0; +9,8] |
| K1f | K1, só OCI (grupo 09, Ofertas de Cuidados Integrados) | 0,300 | 859 / 654 | −1,66 | [−3,83; +0,51] | 0,134 | — | −3881,6 % [−8961,2; +1197,9] |
| K1f | K1, só OCI (grupo 09, Ofertas de Cuidados Integrados) | 0,400 | 587 / 603 | +0,46 | [−0,54; +1,45] | 0,367 | — | +1359,8 % [−1592,9; +4312,5] |
| K1f | K1, só OCI (grupo 09, Ofertas de Cuidados Integrados) | empilhado | 1446 / 1257 | −0,73 | [−2,03; +0,57] | 0,270 | 1,000 | −1872,3 % [−5195,9; +1451,3] |
| K3a.consultas | planos (TISS): consultas pelas CBO-alvo | 0,300 | 859 / 654 | −3,17 | [−9,40; +3,06] | 0,318 | — | −5,8 % [−17,2; +5,6] |
| K3a.consultas | planos (TISS): consultas pelas CBO-alvo | 0,400 | 587 / 603 | −1,67 | [−4,31; +0,97] | 0,215 | — | −12,3 % [−31,9; +7,2] |
| K3a.consultas | planos (TISS): consultas pelas CBO-alvo | empilhado | 1446 / 1257 | −2,51 | [−6,20; +1,17] | 0,181 | 1,000 | −6,6 % [−16,4; +3,1] |
| K3a.exames | planos (TISS): exames (família 4) pelas CBO-alvo; piso (CBO ausente em parte dos eventos) | 0,300 | 859 / 654 | +13,22 | [−19,62; +46,05] | 0,430 | — | +14,8 % [−22,0; +51,7] |
| K3a.exames | planos (TISS): exames (família 4) pelas CBO-alvo; piso (CBO ausente em parte dos eventos) | 0,400 | 587 / 603 | −4,22 | [−27,02; +18,59] | 0,717 | — | −12,9 % [−82,7; +56,9] |
| K3a.exames | planos (TISS): exames (família 4) pelas CBO-alvo; piso (CBO ausente em parte dos eventos) | empilhado | 1446 / 1257 | +5,58 | [−15,41; +26,57] | 0,602 | 1,000 | +8,4 % [−23,3; +40,2] |
| K3a.cirurgias | planos (TISS): procedimentos cirúrgicos (família 3) pelas CBO-alvo; piso | 0,300 | 859 / 654 | +0,05 | [−0,14; +0,23] | 0,626 | — | +5,1 % [−15,3; +25,5] |
| K3a.cirurgias | planos (TISS): procedimentos cirúrgicos (família 3) pelas CBO-alvo; piso | 0,400 | 587 / 603 | −0,02 | [−0,17; +0,12] | 0,740 | — | −12,8 % [−88,2; +62,6] |
| K3a.cirurgias | planos (TISS): procedimentos cirúrgicos (família 3) pelas CBO-alvo; piso | empilhado | 1446 / 1257 | +0,01 | [−0,11; +0,14] | 0,810 | 1,000 | +2,4 % [−17,4; +22,2] |
| K3b | parte SIA de K3 (consultas 0301 pelas CBO-alvo) no mesmo pós 202510-202512 | 0,300 | 859 / 654 | −16,28 | [−43,21; +10,66] | 0,236 | — | −12,9 % [−34,2; +8,4] |
| K3b | parte SIA de K3 (consultas 0301 pelas CBO-alvo) no mesmo pós 202510-202512 | 0,400 | 587 / 603 | +22,40 | [−9,75; +54,54] | 0,172 | — | +31,4 % [−13,7; +76,5] |
| K3b | parte SIA de K3 (consultas 0301 pelas CBO-alvo) no mesmo pós 202510-202512 | empilhado | 1446 / 1257 | +0,66 | [−20,04; +21,36] | 0,950 | 1,000 | +0,6 % [−19,3; +20,5] |
| K3c | planos (TISS hospitalar): procedimentos cirúrgicos, total municipal sem filtro de CBO | 0,300 | 859 / 654 | +0,34 | [−0,15; +0,84] | 0,177 | — | +7,8 % [−3,5; +19,2] |
| K3c | planos (TISS hospitalar): procedimentos cirúrgicos, total municipal sem filtro de CBO | 0,400 | 587 / 603 | −0,16 | [−0,60; +0,28] | 0,483 | — | −17,1 % [−64,8; +30,6] |
| K3c | planos (TISS hospitalar): procedimentos cirúrgicos, total municipal sem filtro de CBO | empilhado | 1446 / 1257 | +0,12 | [−0,22; +0,46] | 0,475 | 1,000 | +4,2 % [−7,2; +15,6] |
| K4.vinculos | capacidade privada: vínculos não SUS das CBO-alvo (CNES; total − SUS) | 0,300 | 859 / 654 | +0,04 | [−0,09; +0,16] | 0,565 | — | +1,6 % [−3,8; +7,0] |
| K4.vinculos | capacidade privada: vínculos não SUS das CBO-alvo (CNES; total − SUS) | 0,400 | 587 / 603 | +0,13 | [+0,01; +0,26] | 0,040 | — | +16,0 % [+0,7; +31,3] |
| K4.vinculos | capacidade privada: vínculos não SUS das CBO-alvo (CNES; total − SUS) | empilhado | 1446 / 1257 | +0,08 | [−0,01; +0,17] | 0,084 | 1,000 | +4,6 % [−0,6; +9,9] |
| K4.horas | capacidade privada: horas semanais não SUS das CBO-alvo (CNES; amb. + hosp. total − SUS) | 0,300 | 856 / 654 | −0,25 | [−1,40; +0,91] | 0,675 | — | −1,1 % [−6,4; +4,1] |
| K4.horas | capacidade privada: horas semanais não SUS das CBO-alvo (CNES; amb. + hosp. total − SUS) | 0,400 | 587 / 603 | +1,24 | [−0,35; +2,83] | 0,126 | — | +15,5 % [−4,3; +35,4] |
| K4.horas | capacidade privada: horas semanais não SUS das CBO-alvo (CNES; amb. + hosp. total − SUS) | empilhado | 1443 / 1257 | +0,41 | [−0,55; +1,36] | 0,403 | 1,000 | +2,5 % [−3,4; +8,4] |
| K5 | composição: participação do SUS nas consultas de K3 (SIA / (SIA + TISS)), razão das somas da janela | 0,300 | 625 / 427 | −0,2 p.p. | [−6,9; +6,4] | 0,944 | — | −0,3 % [−9,8; +9,1] |
| K5 | composição: participação do SUS nas consultas de K3 (SIA / (SIA + TISS)), razão das somas da janela | 0,400 | 359 / 372 | +6,8 p.p. | [+0,5; +13,1] | 0,033 | — | +8,3 % [+0,7; +15,9] |
| K5 | composição: participação do SUS nas consultas de K3 (SIA / (SIA + TISS)), razão das somas da janela | empilhado | 984 / 799 | +2,6 p.p. | [−2,1; +7,3] | 0,279 | 1,000 | +3,5 % [−2,8; +9,8] |
<!-- K:secundarias:fim -->

K3a de exames e cirurgias é um **piso**: o CBO falta na maior parte dos
eventos de exames e cirurgias do TISS (A14, §11.2). K3c não tem filtro de
especialista. Em K1f (OCI) o efeito relativo não tem leitura útil, porque o
grupo 09 começa em jan/2025, no meio do pré, e a média do pré é quase zero.

Placebos de profissional (KP1 generalistas, KP2 especialistas fora das
CBO-alvo; KP1.mfc = medicina de família, S6, à parte) e placebo dentro do
pré (KP3):

<!-- K:placebos:inicio -->
| Placebo | Descrição | Corte | n abaixo / acima | Salto | IC 95% | p | Efeito relativo [IC 95%] |
|---|---|---|---|---|---|---|---|
| KP1 | placebo: produção SIA dos generalistas (225125, 225142, 225170) | 0,300 | 859 / 654 | −36,69 | [−283,49; +210,11] | 0,771 | −1,9 % [−14,8; +11,0] |
| KP1 | placebo: produção SIA dos generalistas (225125, 225142, 225170) | 0,400 | 587 / 603 | −48,93 | [−374,09; +276,24] | 0,768 | −3,4 % [−26,0; +19,2] |
| KP1 | placebo: produção SIA dos generalistas (225125, 225142, 225170) | empilhado | 1446 / 1257 | −42,05 | [−240,81; +156,71] | 0,678 | −2,4 % [−14,0; +9,1] |
| KP2 | placebo: produção SIA dos especialistas fora das CBO-alvo | 0,300 | 859 / 654 | −17,12 | [−96,85; +62,60] | 0,674 | −4,1 % [−23,4; +15,1] |
| KP2 | placebo: produção SIA dos especialistas fora das CBO-alvo | 0,400 | 587 / 603 | −4,81 | [−51,49; +41,86] | 0,840 | −2,0 % [−21,8; +17,7] |
| KP2 | placebo: produção SIA dos especialistas fora das CBO-alvo | empilhado | 1446 / 1257 | −11,73 | [−60,97; +37,51] | 0,641 | −3,4 % [−17,9; +11,0] |
| KP1.mfc | S6: produção SIA de medicina de família e comunidade (225130), à parte (§3.1) | 0,300 | 859 / 654 | +9,43 | [−9,28; +28,13] | 0,323 | +145,4 % [−143,2; +433,9] |
| KP1.mfc | S6: produção SIA de medicina de família e comunidade (225130), à parte (§3.1) | 0,400 | 587 / 603 | +4,26 | [−4,24; +12,77] | 0,326 | +345,5 % [−344,0; +1035,1] |
| KP1.mfc | S6: produção SIA de medicina de família e comunidade (225130), à parte (§3.1) | empilhado | 1446 / 1257 | +7,16 | [−3,99; +18,32] | 0,208 | +164,6 % [−91,7; +421,0] |
<!-- K:placebos:fim -->

<!-- K:kp3:inicio -->
| Outcome | Corte | n abaixo / acima | Salto (dentro do pré) | IC 95% | p |
|---|---|---|---|---|---|
| K1 | 0,300 | 859 / 654 | −3,71 | [−41,18; +33,76] | 0,846 |
| K1 | 0,400 | 587 / 603 | +18,31 | [−18,20; +54,82] | 0,326 |
| K1 | empilhado | 1446 / 1257 | +5,93 | [−20,50; +32,37] | 0,660 |
| K2 | 0,300 | 859 / 654 | +0,31 | [−0,70; +1,33] | 0,543 |
| K2 | 0,400 | 587 / 603 | +0,76 | [−2,22; +3,75] | 0,617 |
| K2 | empilhado | 1446 / 1257 | +0,51 | [−0,92; +1,94] | 0,483 |
| K3 | 0,300 | 859 / 654 | +4,90 | [−15,01; +24,81] | 0,630 |
| K3 | 0,400 | 587 / 603 | −4,47 | [−18,10; +9,15] | 0,520 |
| K3 | empilhado | 1446 / 1257 | +0,79 | [−11,88; +13,47] | 0,902 |
| K1a | 0,300 | 859 / 654 | +2,09 | [−16,89; +21,08] | 0,829 |
| K1a | 0,400 | 587 / 603 | −3,08 | [−16,45; +10,29] | 0,652 |
| K1a | empilhado | 1446 / 1257 | −0,17 | [−12,34; +12,00] | 0,978 |
| K1b | 0,300 | 859 / 654 | −6,72 | [−37,65; +24,20] | 0,670 |
| K1b | 0,400 | 587 / 603 | +22,68 | [−8,66; +54,02] | 0,156 |
| K1b | empilhado | 1446 / 1257 | +6,16 | [−15,99; +28,30] | 0,586 |
| K1c | 0,300 | 859 / 654 | +0,88 | [−0,97; +2,72] | 0,353 |
| K1c | 0,400 | 587 / 603 | −1,41 | [−3,03; +0,22] | 0,090 |
| K1c | empilhado | 1446 / 1257 | −0,12 | [−1,39; +1,14] | 0,847 |
| K1d | 0,300 | 859 / 654 | −0,65 | [−109,71; +108,42] | 0,991 |
| K1d | 0,400 | 587 / 603 | +25,24 | [−44,27; +94,75] | 0,477 |
| K1d | empilhado | 1446 / 1257 | +10,69 | [−57,74; +79,13] | 0,759 |
| K1f | 0,300 | 859 / 654 | +0,04 | [−0,07; +0,15] | 0,503 |
| K1f | 0,400 | 587 / 603 | +0,12 | [−0,05; +0,28] | 0,155 |
| K1f | empilhado | 1446 / 1257 | +0,07 | [−0,02; +0,17] | 0,131 |
| K3a.consultas | 0,300 | 859 / 654 | +2,80 | [−2,36; +7,97] | 0,287 |
| K3a.consultas | 0,400 | 587 / 603 | −1,39 | [−3,49; +0,70] | 0,193 |
| K3a.consultas | empilhado | 1446 / 1257 | +0,97 | [−2,08; +4,01] | 0,533 |
| K3a.exames | 0,300 | 859 / 654 | +9,74 | [−12,60; +32,08] | 0,393 |
| K3a.exames | 0,400 | 587 / 603 | −0,06 | [−9,27; +9,16] | 0,990 |
| K3a.exames | empilhado | 1446 / 1257 | +5,45 | [−7,75; +18,65] | 0,418 |
| K3a.cirurgias | 0,300 | 859 / 654 | −0,10 | [−0,29; +0,09] | 0,313 |
| K3a.cirurgias | 0,400 | 587 / 603 | −0,03 | [−0,15; +0,09] | 0,671 |
| K3a.cirurgias | empilhado | 1446 / 1257 | −0,07 | [−0,19; +0,05] | 0,274 |
| K3b | 0,300 | 859 / 654 | +2,09 | [−16,89; +21,08] | 0,829 |
| K3b | 0,400 | 587 / 603 | −3,08 | [−16,45; +10,29] | 0,652 |
| K3b | empilhado | 1446 / 1257 | −0,17 | [−12,34; +12,00] | 0,978 |
| K3c | 0,300 | 859 / 654 | +0,08 | [−0,36; +0,52] | 0,732 |
| K3c | 0,400 | 587 / 603 | +0,05 | [−0,07; +0,18] | 0,400 |
| K3c | empilhado | 1446 / 1257 | +0,07 | [−0,19; +0,32] | 0,607 |
| K4.vinculos | 0,300 | 859 / 654 | −0,07 | [−0,16; +0,03] | 0,154 |
| K4.vinculos | 0,400 | 587 / 603 | +0,06 | [−0,03; +0,16] | 0,202 |
| K4.vinculos | empilhado | 1446 / 1257 | −0,01 | [−0,08; +0,06] | 0,748 |
| K4.horas | 0,300 | 856 / 654 | −0,35 | [−1,15; +0,46] | 0,398 |
| K4.horas | 0,400 | 587 / 603 | +1,18 | [+0,05; +2,32] | 0,041 |
| K4.horas | empilhado | 1443 / 1257 | +0,32 | [−0,35; +1,00] | 0,345 |
| K5 | 0,300 | 617 / 428 | +1,6 p.p. | [−2,4; +5,7] | 0,431 |
| K5 | 0,400 | 343 / 350 | −1,2 p.p. | [−7,8; +5,3] | 0,717 |
| K5 | empilhado | 960 / 778 | +0,5 p.p. | [−3,1; +4,1] | 0,782 |
| KP1 | 0,300 | 859 / 654 | −226,09 | [−466,74; +14,57] | 0,066 |
| KP1 | 0,400 | 587 / 603 | −57,06 | [−440,17; +326,05] | 0,770 |
| KP1 | empilhado | 1446 / 1257 | −152,05 | [−367,42; +63,31] | 0,166 |
| KP2 | 0,300 | 859 / 654 | +3,06 | [−99,33; +105,46] | 0,953 |
| KP2 | 0,400 | 587 / 603 | +6,93 | [−37,97; +51,83] | 0,762 |
| KP2 | empilhado | 1446 / 1257 | +4,76 | [−56,05; +65,57] | 0,878 |
| KP1.mfc | 0,300 | 859 / 654 | −14,02 | [−34,71; +6,66] | 0,184 |
| KP1.mfc | 0,400 | 587 / 603 | +4,14 | [−4,77; +13,04] | 0,362 |
| KP1.mfc | empilhado | 1446 / 1257 | −6,07 | [−18,34; +6,20] | 0,332 |
<!-- K:kp3:fim -->

<!-- K:leitura_placebos:inicio -->
Placebos de profissional (U, empilhado): KP1 −42,05 [−240,81; +156,71] (p = 0,678); KP2 −11,73 [−60,97; +37,51] (p = 0,641); KP1.mfc +7,16 [−3,99; +18,32] (p = 0,208). Placebo dentro do pré (KP3, U, empilhado): K1 +5,93 (p = 0,660); K2 +0,51 (p = 0,483); K3 +0,79 (p = 0,902).
<!-- K:leitura_placebos:fim -->

## 6. D1 — estudo de evento

RDD mês a mês de (Y_t − Y_jun/2025), desde jan/2022, em U (e em V1 para as
primárias, no CSV). Resumo por janela; as figuras mostram cada mês com as datas
das políticas S1–S6 da auditoria 18 e dos ciclos do PMM-E.

<!-- K:evento:inicio -->
| Outcome | Corte | Janela | Meses estimados | p < 0,05 | maior abs(salto) | salto médio |
|---|---|---|---|---|---|---|
| K1 | 0,300 | pre_extra | 15 | 0 | 77,07 | +13,80 |
| K1 | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 73,40 | +24,14 |
| K1 | 0,300 | pre | 12 | 0 | 66,32 | −11,95 |
| K1 | 0,300 | transicao | 3 | 0 | 71,35 | −24,19 |
| K1 | 0,300 | pos | 8 | 0 | 70,93 | −14,99 |
| K1 | 0,300 | pos_sensibilidade | 2 | 0 | 21,96 | +19,08 |
| K1 | 0,400 | pre_extra | 15 | 0 | 75,07 | −34,18 |
| K1 | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 150,16 | −7,98 |
| K1 | 0,400 | pre | 12 | 0 | 67,84 | −11,08 |
| K1 | 0,400 | transicao | 3 | 0 | 24,53 | +11,40 |
| K1 | 0,400 | pos | 8 | 0 | 41,18 | +12,93 |
| K1 | 0,400 | pos_sensibilidade | 2 | 0 | 69,79 | −26,93 |
| K1 | empilhado | pre_extra | 15 | 0 | 72,66 | −7,22 |
| K1 | empilhado | entre_pre_extra_e_pre | 14 | 0 | 63,60 | +10,07 |
| K1 | empilhado | pre | 12 | 0 | 66,99 | −11,57 |
| K1 | empilhado | transicao | 3 | 0 | 39,31 | −8,60 |
| K1 | empilhado | pos | 8 | 0 | 31,23 | −2,76 |
| K1 | empilhado | pos_sensibilidade | 2 | 0 | 18,23 | −1,07 |
| K2 | 0,300 | pre_extra | 15 | 1 | 2,58 | −1,31 |
| K2 | 0,300 | entre_pre_extra_e_pre | 14 | 4 | 2,33 | −1,38 |
| K2 | 0,300 | pre | 12 | 1 | 2,23 | −0,65 |
| K2 | 0,300 | transicao | 3 | 0 | 0,93 | −0,01 |
| K2 | 0,300 | pos | 8 | 0 | 0,95 | −0,19 |
| K2 | 0,300 | pos_sensibilidade | 2 | 0 | 1,08 | +0,68 |
| K2 | 0,400 | pre_extra | 15 | 0 | 5,21 | +1,92 |
| K2 | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 4,08 | −0,88 |
| K2 | 0,400 | pre | 12 | 0 | 4,04 | +1,30 |
| K2 | 0,400 | transicao | 3 | 0 | 3,81 | +1,28 |
| K2 | 0,400 | pos | 8 | 0 | 3,92 | +1,61 |
| K2 | 0,400 | pos_sensibilidade | 2 | 0 | 1,32 | +0,11 |
| K2 | empilhado | pre_extra | 15 | 0 | 2,00 | +0,11 |
| K2 | empilhado | entre_pre_extra_e_pre | 14 | 4 | 2,45 | −1,16 |
| K2 | empilhado | pre | 12 | 0 | 1,61 | +0,20 |
| K2 | empilhado | transicao | 3 | 0 | 1,87 | +0,56 |
| K2 | empilhado | pos | 8 | 0 | 1,50 | +0,60 |
| K2 | empilhado | pos_sensibilidade | 2 | 0 | 0,74 | +0,43 |
| K3 | 0,300 | pre_extra | 15 | 0 | 88,68 | −2,63 |
| K3 | 0,300 | entre_pre_extra_e_pre | 14 | 1 | 53,71 | −12,79 |
| K3 | 0,300 | pre | 12 | 2 | 39,45 | −18,42 |
| K3 | 0,300 | transicao | 3 | 0 | 39,25 | −35,19 |
| K3 | 0,300 | pos | 3 | 2 | 41,42 | −36,45 |
| K3 | 0,400 | pre_extra | 15 | 0 | 36,46 | +1,08 |
| K3 | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 19,83 | +9,57 |
| K3 | 0,400 | pre | 12 | 1 | 23,79 | +6,99 |
| K3 | 0,400 | transicao | 3 | 0 | 16,57 | +11,29 |
| K3 | 0,400 | pos | 3 | 1 | 40,23 | +27,18 |
| K3 | empilhado | pre_extra | 15 | 0 | 61,68 | −1,01 |
| K3 | empilhado | entre_pre_extra_e_pre | 14 | 1 | 30,98 | −3,00 |
| K3 | empilhado | pre | 12 | 0 | 19,11 | −7,29 |
| K3 | empilhado | transicao | 3 | 0 | 20,18 | −14,83 |
| K3 | empilhado | pos | 3 | 0 | 13,22 | −8,58 |
| K1a | 0,300 | pre_extra | 15 | 0 | 85,16 | −2,03 |
| K1a | 0,300 | entre_pre_extra_e_pre | 14 | 1 | 49,83 | −13,32 |
| K1a | 0,300 | pre | 12 | 2 | 34,83 | −17,64 |
| K1a | 0,300 | transicao | 3 | 0 | 35,24 | −31,39 |
| K1a | 0,300 | pos | 8 | 0 | 41,10 | −25,90 |
| K1a | 0,300 | pos_sensibilidade | 2 | 0 | 24,58 | −20,71 |
| K1a | 0,400 | pre_extra | 15 | 0 | 36,31 | +0,95 |
| K1a | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 19,06 | +8,21 |
| K1a | 0,400 | pre | 12 | 1 | 23,13 | +7,67 |
| K1a | 0,400 | transicao | 3 | 0 | 17,02 | +11,65 |
| K1a | 0,400 | pos | 8 | 1 | 42,56 | +23,04 |
| K1a | 0,400 | pos_sensibilidade | 2 | 0 | 28,05 | +8,91 |
| K1a | empilhado | pre_extra | 15 | 0 | 59,77 | −0,73 |
| K1a | empilhado | entre_pre_extra_e_pre | 14 | 1 | 29,83 | −3,89 |
| K1a | empilhado | pre | 12 | 0 | 17,63 | −6,55 |
| K1a | empilhado | transicao | 3 | 0 | 17,53 | −12,54 |
| K1a | empilhado | pos | 8 | 0 | 10,40 | −4,47 |
| K1a | empilhado | pos_sensibilidade | 2 | 0 | 18,29 | −7,74 |
| K1b | 0,300 | pre_extra | 15 | 0 | 58,49 | +12,88 |
| K1b | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 75,40 | +35,31 |
| K1b | 0,300 | pre | 12 | 0 | 44,46 | +5,17 |
| K1b | 0,300 | transicao | 3 | 0 | 34,16 | +7,73 |
| K1b | 0,300 | pos | 8 | 0 | 47,91 | +11,60 |
| K1b | 0,300 | pos_sensibilidade | 2 | 0 | 44,93 | +38,82 |
| K1b | 0,400 | pre_extra | 15 | 2 | 49,72 | −34,49 |
| K1b | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 138,39 | −15,68 |
| K1b | 0,400 | pre | 12 | 0 | 68,58 | −18,55 |
| K1b | 0,400 | transicao | 3 | 0 | 13,13 | +0,77 |
| K1b | 0,400 | pos | 8 | 0 | 36,55 | −9,69 |
| K1b | 0,400 | pos_sensibilidade | 2 | 1 | 56,90 | −34,98 |
| K1b | empilhado | pre_extra | 15 | 0 | 40,11 | −7,87 |
| K1b | empilhado | entre_pre_extra_e_pre | 14 | 0 | 56,70 | +12,98 |
| K1b | empilhado | pre | 12 | 0 | 49,40 | −5,22 |
| K1b | empilhado | transicao | 3 | 0 | 24,61 | +4,68 |
| K1b | empilhado | pos | 8 | 0 | 21,42 | +2,27 |
| K1b | empilhado | pos_sensibilidade | 2 | 0 | 12,66 | +6,50 |
| K1c | 0,300 | pre_extra | 15 | 3 | 5,10 | +2,57 |
| K1c | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 5,75 | +1,76 |
| K1c | 0,300 | pre | 12 | 1 | 1,23 | +0,13 |
| K1c | 0,300 | transicao | 3 | 0 | 1,68 | −0,12 |
| K1c | 0,300 | pos | 8 | 0 | 1,11 | +0,60 |
| K1c | 0,300 | pos_sensibilidade | 2 | 0 | 2,48 | +1,75 |
| K1c | 0,400 | pre_extra | 15 | 0 | 1,02 | −0,27 |
| K1c | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 2,89 | −0,15 |
| K1c | 0,400 | pre | 12 | 0 | 2,16 | +0,09 |
| K1c | 0,400 | transicao | 3 | 0 | 1,36 | −0,97 |
| K1c | 0,400 | pos | 8 | 0 | 2,55 | −0,60 |
| K1c | 0,400 | pos_sensibilidade | 2 | 1 | 3,02 | −1,61 |
| K1c | empilhado | pre_extra | 15 | 1 | 2,57 | +1,33 |
| K1c | empilhado | entre_pre_extra_e_pre | 14 | 0 | 2,96 | +0,93 |
| K1c | empilhado | pre | 12 | 0 | 0,62 | +0,11 |
| K1c | empilhado | transicao | 3 | 0 | 1,09 | −0,49 |
| K1c | empilhado | pos | 8 | 0 | 0,88 | +0,08 |
| K1c | empilhado | pos_sensibilidade | 2 | 0 | 0,48 | +0,28 |
| K1d | 0,300 | pre_extra | 15 | 0 | 140,86 | −43,81 |
| K1d | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 65,31 | +1,86 |
| K1d | 0,300 | pre | 12 | 0 | 159,77 | −47,51 |
| K1d | 0,300 | transicao | 3 | 0 | 120,67 | −43,05 |
| K1d | 0,300 | pos | 8 | 2 | 142,28 | −64,94 |
| K1d | 0,300 | pos_sensibilidade | 2 | 0 | 131,63 | −107,24 |
| K1d | 0,400 | pre_extra | 15 | 0 | 148,08 | +40,60 |
| K1d | 0,400 | entre_pre_extra_e_pre | 14 | 1 | 240,63 | +58,36 |
| K1d | 0,400 | pre | 12 | 1 | 71,93 | +29,48 |
| K1d | 0,400 | transicao | 3 | 0 | 47,16 | +37,32 |
| K1d | 0,400 | pos | 8 | 1 | 119,98 | +45,56 |
| K1d | 0,400 | pos_sensibilidade | 2 | 0 | 64,89 | +3,94 |
| K1d | empilhado | pre_extra | 15 | 0 | 83,39 | −6,84 |
| K1d | empilhado | entre_pre_extra_e_pre | 14 | 0 | 94,29 | +26,61 |
| K1d | empilhado | pre | 12 | 0 | 66,62 | −13,79 |
| K1d | empilhado | transicao | 3 | 0 | 56,12 | −7,85 |
| K1d | empilhado | pos | 8 | 0 | 67,18 | −16,54 |
| K1d | empilhado | pos_sensibilidade | 2 | 0 | 71,53 | −58,54 |
| K1f | 0,300 | pre_extra | 15 | 0 | 0,38 | +0,38 |
| K1f | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 0,38 | +0,38 |
| K1f | 0,300 | pre | 12 | 3 | 0,63 | +0,40 |
| K1f | 0,300 | transicao | 3 | 0 | 0,78 | −0,41 |
| K1f | 0,300 | pos | 8 | 0 | 1,93 | −1,29 |
| K1f | 0,300 | pos_sensibilidade | 2 | 0 | 0,87 | −0,78 |
| K1f | 0,400 | pre_extra | 15 | 0 | 0,36 | −0,36 |
| K1f | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 0,36 | −0,36 |
| K1f | 0,400 | pre | 12 | 0 | 0,36 | −0,30 |
| K1f | 0,400 | transicao | 3 | 0 | 0,13 | −0,04 |
| K1f | 0,400 | pos | 8 | 1 | 1,62 | +0,18 |
| K1f | 0,400 | pos_sensibilidade | 2 | 0 | 1,14 | +0,74 |
| K1f | empilhado | pre_extra | 15 | 0 | 0,06 | +0,06 |
| K1f | empilhado | entre_pre_extra_e_pre | 14 | 0 | 0,06 | +0,06 |
| K1f | empilhado | pre | 12 | 0 | 0,30 | +0,09 |
| K1f | empilhado | transicao | 3 | 0 | 0,49 | −0,25 |
| K1f | empilhado | pos | 8 | 0 | 1,23 | −0,64 |
| K1f | empilhado | pos_sensibilidade | 2 | 0 | 0,34 | −0,11 |
| K3a.consultas | 0,300 | pre_extra | 15 | 0 | 3,51 | −0,60 |
| K3a.consultas | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 3,88 | +0,53 |
| K3a.consultas | 0,300 | pre | 12 | 0 | 4,62 | −0,78 |
| K3a.consultas | 0,300 | transicao | 3 | 0 | 4,43 | −3,80 |
| K3a.consultas | 0,300 | pos | 3 | 0 | 4,70 | −3,89 |
| K3a.consultas | 0,400 | pre_extra | 15 | 0 | 0,92 | +0,13 |
| K3a.consultas | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 2,87 | +1,35 |
| K3a.consultas | 0,400 | pre | 12 | 1 | 2,08 | −0,69 |
| K3a.consultas | 0,400 | transicao | 3 | 0 | 0,89 | −0,36 |
| K3a.consultas | 0,400 | pos | 3 | 0 | 2,43 | −2,31 |
| K3a.consultas | empilhado | pre_extra | 15 | 0 | 1,91 | −0,28 |
| K3a.consultas | empilhado | entre_pre_extra_e_pre | 14 | 0 | 2,41 | +0,89 |
| K3a.consultas | empilhado | pre | 12 | 0 | 2,53 | −0,74 |
| K3a.consultas | empilhado | transicao | 3 | 0 | 2,65 | −2,29 |
| K3a.consultas | empilhado | pos | 3 | 0 | 3,66 | −3,20 |
| K3a.exames | 0,300 | pre_extra | 15 | 0 | 50,04 | +4,41 |
| K3a.exames | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 37,78 | −18,68 |
| K3a.exames | 0,300 | pre | 12 | 0 | 21,62 | −8,43 |
| K3a.exames | 0,300 | transicao | 3 | 0 | 24,26 | +7,70 |
| K3a.exames | 0,300 | pos | 3 | 0 | 19,20 | +5,44 |
| K3a.exames | 0,400 | pre_extra | 15 | 0 | 20,67 | −14,24 |
| K3a.exames | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 17,07 | −14,33 |
| K3a.exames | 0,400 | pre | 12 | 0 | 10,88 | +0,10 |
| K3a.exames | 0,400 | transicao | 3 | 0 | 9,89 | −3,84 |
| K3a.exames | 0,400 | pos | 3 | 0 | 7,20 | −4,12 |
| K3a.exames | empilhado | pre_extra | 15 | 0 | 34,78 | −3,76 |
| K3a.exames | empilhado | entre_pre_extra_e_pre | 14 | 0 | 28,69 | −16,77 |
| K3a.exames | empilhado | pre | 12 | 0 | 10,19 | −4,69 |
| K3a.exames | empilhado | transicao | 3 | 0 | 15,71 | +2,64 |
| K3a.exames | empilhado | pos | 3 | 0 | 10,98 | +1,25 |
| K3a.cirurgias | 0,300 | pre_extra | 15 | 0 | 0,19 | +0,01 |
| K3a.cirurgias | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 0,38 | +0,29 |
| K3a.cirurgias | 0,300 | pre | 12 | 0 | 0,46 | +0,18 |
| K3a.cirurgias | 0,300 | transicao | 3 | 0 | 0,08 | −0,04 |
| K3a.cirurgias | 0,300 | pos | 3 | 1 | 0,41 | +0,21 |
| K3a.cirurgias | 0,400 | pre_extra | 15 | 0 | 0,08 | +0,02 |
| K3a.cirurgias | 0,400 | entre_pre_extra_e_pre | 14 | 2 | 0,23 | +0,12 |
| K3a.cirurgias | 0,400 | pre | 12 | 1 | 0,17 | +0,08 |
| K3a.cirurgias | 0,400 | transicao | 3 | 0 | 0,11 | +0,06 |
| K3a.cirurgias | 0,400 | pos | 3 | 0 | 0,10 | +0,05 |
| K3a.cirurgias | empilhado | pre_extra | 15 | 0 | 0,10 | +0,02 |
| K3a.cirurgias | empilhado | entre_pre_extra_e_pre | 14 | 3 | 0,29 | +0,21 |
| K3a.cirurgias | empilhado | pre | 12 | 2 | 0,30 | +0,13 |
| K3a.cirurgias | empilhado | transicao | 3 | 0 | 0,01 | +0,00 |
| K3a.cirurgias | empilhado | pos | 3 | 2 | 0,24 | +0,14 |
| K3b | 0,300 | pre_extra | 15 | 0 | 85,16 | −2,03 |
| K3b | 0,300 | entre_pre_extra_e_pre | 14 | 1 | 49,83 | −13,32 |
| K3b | 0,300 | pre | 12 | 2 | 34,83 | −17,64 |
| K3b | 0,300 | transicao | 3 | 0 | 35,24 | −31,39 |
| K3b | 0,300 | pos | 3 | 0 | 36,92 | −32,56 |
| K3b | 0,300 | pos_sensibilidade | 7 | 0 | 41,10 | −21,57 |
| K3b | 0,400 | pre_extra | 15 | 0 | 36,31 | +0,95 |
| K3b | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 19,06 | +8,21 |
| K3b | 0,400 | pre | 12 | 1 | 23,13 | +7,67 |
| K3b | 0,400 | transicao | 3 | 0 | 17,02 | +11,65 |
| K3b | 0,400 | pos | 3 | 1 | 42,56 | +29,48 |
| K3b | 0,400 | pos_sensibilidade | 7 | 0 | 40,75 | +16,24 |
| K3b | empilhado | pre_extra | 15 | 0 | 59,77 | −0,73 |
| K3b | empilhado | entre_pre_extra_e_pre | 14 | 1 | 29,83 | −3,89 |
| K3b | empilhado | pre | 12 | 0 | 17,63 | −6,55 |
| K3b | empilhado | transicao | 3 | 0 | 17,53 | −12,54 |
| K3b | empilhado | pos | 3 | 0 | 9,62 | −5,39 |
| K3b | empilhado | pos_sensibilidade | 7 | 0 | 18,29 | −5,01 |
| K3c | 0,300 | pre_extra | 15 | 0 | 1,05 | +0,57 |
| K3c | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 0,74 | +0,47 |
| K3c | 0,300 | pre | 12 | 0 | 0,49 | −0,06 |
| K3c | 0,300 | transicao | 3 | 0 | 0,47 | −0,35 |
| K3c | 0,300 | pos | 3 | 0 | 0,72 | +0,28 |
| K3c | 0,400 | pre_extra | 15 | 0 | 0,20 | −0,04 |
| K3c | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 0,33 | −0,17 |
| K3c | 0,400 | pre | 12 | 0 | 0,17 | −0,08 |
| K3c | 0,400 | transicao | 3 | 0 | 0,11 | +0,00 |
| K3c | 0,400 | pos | 3 | 0 | 0,44 | −0,23 |
| K3c | empilhado | pre_extra | 15 | 0 | 0,57 | +0,31 |
| K3c | empilhado | entre_pre_extra_e_pre | 14 | 0 | 0,35 | +0,19 |
| K3c | empilhado | pre | 12 | 0 | 0,34 | −0,07 |
| K3c | empilhado | transicao | 3 | 0 | 0,26 | −0,20 |
| K3c | empilhado | pos | 3 | 0 | 0,34 | +0,06 |
| K4.vinculos | 0,300 | pre_extra | 7 | 1 | 0,25 | +0,20 |
| K4.vinculos | 0,300 | entre_pre_extra_e_pre | 5 | 0 | 0,15 | +0,13 |
| K4.vinculos | 0,300 | pre | 12 | 0 | 0,10 | +0,03 |
| K4.vinculos | 0,300 | transicao | 3 | 0 | 0,03 | −0,03 |
| K4.vinculos | 0,300 | pos | 8 | 4 | 0,15 | +0,07 |
| K4.vinculos | 0,300 | pos_sensibilidade | 3 | 1 | 0,11 | +0,07 |
| K4.vinculos | 0,400 | pre_extra | 7 | 3 | 0,28 | −0,21 |
| K4.vinculos | 0,400 | entre_pre_extra_e_pre | 5 | 3 | 0,22 | −0,20 |
| K4.vinculos | 0,400 | pre | 12 | 7 | 0,19 | −0,12 |
| K4.vinculos | 0,400 | transicao | 3 | 0 | 0,01 | −0,01 |
| K4.vinculos | 0,400 | pos | 8 | 0 | 0,04 | +0,03 |
| K4.vinculos | 0,400 | pos_sensibilidade | 3 | 0 | 0,03 | −0,02 |
| K4.vinculos | empilhado | pre_extra | 7 | 0 | 0,03 | +0,02 |
| K4.vinculos | empilhado | entre_pre_extra_e_pre | 5 | 0 | 0,03 | −0,01 |
| K4.vinculos | empilhado | pre | 12 | 0 | 0,05 | −0,03 |
| K4.vinculos | empilhado | transicao | 3 | 0 | 0,02 | −0,02 |
| K4.vinculos | empilhado | pos | 8 | 4 | 0,10 | +0,05 |
| K4.vinculos | empilhado | pos_sensibilidade | 3 | 0 | 0,05 | +0,03 |
| K4.horas | 0,300 | pre_extra | 7 | 0 | 1,73 | +1,37 |
| K4.horas | 0,300 | entre_pre_extra_e_pre | 5 | 0 | 0,90 | +0,72 |
| K4.horas | 0,300 | pre | 12 | 0 | 0,89 | +0,41 |
| K4.horas | 0,300 | transicao | 3 | 0 | 0,62 | −0,29 |
| K4.horas | 0,300 | pos | 8 | 0 | 0,90 | +0,13 |
| K4.horas | 0,300 | pos_sensibilidade | 3 | 0 | 0,47 | +0,31 |
| K4.horas | 0,400 | pre_extra | 7 | 7 | 3,08 | −2,73 |
| K4.horas | 0,400 | entre_pre_extra_e_pre | 5 | 5 | 2,59 | −2,43 |
| K4.horas | 0,400 | pre | 12 | 12 | 2,51 | −1,41 |
| K4.horas | 0,400 | transicao | 3 | 0 | 0,44 | −0,21 |
| K4.horas | 0,400 | pos | 8 | 0 | 0,41 | −0,06 |
| K4.horas | 0,400 | pos_sensibilidade | 3 | 0 | 0,14 | −0,03 |
| K4.horas | empilhado | pre_extra | 7 | 0 | 0,63 | −0,43 |
| K4.horas | empilhado | entre_pre_extra_e_pre | 5 | 0 | 0,81 | −0,66 |
| K4.horas | empilhado | pre | 12 | 0 | 0,70 | −0,39 |
| K4.horas | empilhado | transicao | 3 | 0 | 0,54 | −0,26 |
| K4.horas | empilhado | pos | 8 | 0 | 0,69 | +0,04 |
| K4.horas | empilhado | pos_sensibilidade | 3 | 0 | 0,30 | +0,16 |
| K5 | 0,300 | pre_extra | 15 | 4 | 12,1 | −7,8 |
| K5 | 0,300 | entre_pre_extra_e_pre | 14 | 10 | 14,1 | −8,8 |
| K5 | 0,300 | pre | 12 | 2 | 6,6 | −3,6 |
| K5 | 0,300 | transicao | 3 | 0 | 1,5 | +0,3 |
| K5 | 0,300 | pos | 3 | 0 | 4,5 | −3,9 |
| K5 | 0,400 | pre_extra | 15 | 0 | 6,3 | +1,4 |
| K5 | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 5,6 | −0,8 |
| K5 | 0,400 | pre | 12 | 0 | 6,5 | −4,0 |
| K5 | 0,400 | transicao | 3 | 0 | 1,4 | +1,1 |
| K5 | 0,400 | pos | 3 | 1 | 9,0 | +5,3 |
| K5 | empilhado | pre_extra | 15 | 1 | 8,9 | −4,4 |
| K5 | empilhado | entre_pre_extra_e_pre | 14 | 7 | 8,2 | −5,8 |
| K5 | empilhado | pre | 12 | 4 | 5,9 | −3,8 |
| K5 | empilhado | transicao | 3 | 0 | 1,2 | +0,6 |
| K5 | empilhado | pos | 3 | 0 | 1,4 | −0,3 |
| KP1 | 0,300 | pre_extra | 15 | 8 | 905,77 | +459,54 |
| KP1 | 0,300 | entre_pre_extra_e_pre | 14 | 1 | 444,26 | +229,51 |
| KP1 | 0,300 | pre | 12 | 6 | 524,95 | +302,99 |
| KP1 | 0,300 | transicao | 3 | 0 | 4910,02 | −1642,53 |
| KP1 | 0,300 | pos | 8 | 1 | 619,54 | +242,99 |
| KP1 | 0,300 | pos_sensibilidade | 2 | 0 | 208,67 | +200,85 |
| KP1 | 0,400 | pre_extra | 15 | 2 | 3580,67 | +131,01 |
| KP1 | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 1986,97 | +56,08 |
| KP1 | 0,400 | pre | 12 | 2 | 1089,93 | +316,14 |
| KP1 | 0,400 | transicao | 3 | 1 | 380,51 | +218,84 |
| KP1 | 0,400 | pos | 8 | 2 | 504,20 | +242,90 |
| KP1 | 0,400 | pos_sensibilidade | 2 | 0 | 341,86 | +308,33 |
| KP1 | empilhado | pre_extra | 15 | 11 | 1245,25 | +315,65 |
| KP1 | empilhado | entre_pre_extra_e_pre | 14 | 5 | 935,11 | +153,55 |
| KP1 | empilhado | pre | 12 | 7 | 664,39 | +308,75 |
| KP1 | empilhado | transicao | 3 | 1 | 2754,09 | −827,26 |
| KP1 | empilhado | pos | 8 | 2 | 393,38 | +242,95 |
| KP1 | empilhado | pos_sensibilidade | 2 | 0 | 267,00 | +247,93 |
| KP2 | 0,300 | pre_extra | 15 | 0 | 83,72 | −57,61 |
| KP2 | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 47,02 | −22,28 |
| KP2 | 0,300 | pre | 12 | 0 | 172,04 | −35,56 |
| KP2 | 0,300 | transicao | 3 | 0 | 49,32 | −18,85 |
| KP2 | 0,300 | pos | 8 | 0 | 84,65 | −49,95 |
| KP2 | 0,300 | pos_sensibilidade | 2 | 0 | 147,83 | −126,31 |
| KP2 | 0,400 | pre_extra | 15 | 3 | 198,11 | +74,78 |
| KP2 | 0,400 | entre_pre_extra_e_pre | 14 | 5 | 130,16 | +66,34 |
| KP2 | 0,400 | pre | 12 | 1 | 68,45 | +40,56 |
| KP2 | 0,400 | transicao | 3 | 0 | 30,22 | +25,92 |
| KP2 | 0,400 | pos | 8 | 1 | 78,80 | +32,63 |
| KP2 | 0,400 | pos_sensibilidade | 2 | 0 | 48,96 | +30,87 |
| KP2 | empilhado | pre_extra | 15 | 0 | 50,41 | +0,38 |
| KP2 | empilhado | entre_pre_extra_e_pre | 14 | 0 | 35,20 | +16,53 |
| KP2 | empilhado | pre | 12 | 0 | 76,13 | −2,22 |
| KP2 | empilhado | transicao | 3 | 0 | 16,82 | +0,75 |
| KP2 | empilhado | pos | 8 | 0 | 48,99 | −13,78 |
| KP2 | empilhado | pos_sensibilidade | 2 | 0 | 61,63 | −57,47 |
| KP1.mfc | 0,300 | pre_extra | 15 | 0 | 12,59 | +11,55 |
| KP1.mfc | 0,300 | entre_pre_extra_e_pre | 14 | 0 | 24,08 | +16,68 |
| KP1.mfc | 0,300 | pre | 12 | 0 | 21,87 | +4,68 |
| KP1.mfc | 0,300 | transicao | 3 | 0 | 12,18 | +8,66 |
| KP1.mfc | 0,300 | pos | 8 | 0 | 16,96 | +13,75 |
| KP1.mfc | 0,300 | pos_sensibilidade | 2 | 0 | 12,36 | +12,21 |
| KP1.mfc | 0,400 | pre_extra | 15 | 0 | 0,51 | +0,10 |
| KP1.mfc | 0,400 | entre_pre_extra_e_pre | 14 | 0 | 11,00 | −0,52 |
| KP1.mfc | 0,400 | pre | 12 | 0 | 15,02 | −6,09 |
| KP1.mfc | 0,400 | transicao | 3 | 0 | 0,14 | +0,04 |
| KP1.mfc | 0,400 | pos | 8 | 0 | 9,80 | −1,36 |
| KP1.mfc | 0,400 | pos_sensibilidade | 2 | 0 | 9,93 | −9,41 |
| KP1.mfc | empilhado | pre_extra | 15 | 0 | 7,17 | +6,54 |
| KP1.mfc | empilhado | entre_pre_extra_e_pre | 14 | 0 | 13,51 | +9,15 |
| KP1.mfc | empilhado | pre | 12 | 0 | 7,40 | −0,04 |
| KP1.mfc | empilhado | transicao | 3 | 0 | 6,84 | +4,88 |
| KP1.mfc | empilhado | pos | 8 | 0 | 9,49 | +7,13 |
| KP1.mfc | empilhado | pos_sensibilidade | 2 | 0 | 2,88 | +2,74 |
<!-- K:evento:fim -->

<!-- K:leitura_evento:inicio -->
Estudo de evento, cortes empilhados, U (mês a mês contra jun/2025): K1: 0 de 41 meses antes de jun/2025 com p < 0,05; no pós principal, 0 de 8; K2: 4 de 41 meses antes de jun/2025 com p < 0,05; no pós principal, 0 de 8; K3: 1 de 41 meses antes de jun/2025 com p < 0,05; no pós principal, 0 de 3; KP1: 23 de 41 meses antes de jun/2025 com p < 0,05; no pós principal, 2 de 8; KP2: 0 de 41 meses antes de jun/2025 com p < 0,05; no pós principal, 0 de 8. Com 5% de nível, cerca de 1 mês em 20 dá p < 0,05 por acaso, sem correção para muitos meses.
<!-- K:leitura_evento:fim -->

## 7. D2 — chegada do especialista do PMM-E (EXPLORATORIO_PARTICIPACAO)

Amostra e coortes trimestrais de chegada (menor `dt_inicio_atividade` da lista
nominal no município; o retrato só traz quem estava ativo, então quem saiu antes
some e o município pode contar como não tratado):

<!-- KD2:amostra:inicio -->
| Item | Valor |
|---|---|
| municípios com célula nos ciclos 1 ou 2 e em U | 598 |
| municípios com célula fora de U (fora) | 0 |
| municípios tratados (≥ 1 especialista ativo) na amostra | 315 |
| municípios nunca tratados na amostra | 283 |
| municípios da lista nominal fora da amostra (fora) | 10 |
| especialistas da lista nominal nesses municípios | 13 |
| sensibilidade: municípios com alocado e sem ativo (excluídos) | 100 |
| coorte 2025-07 (trimestre): municípios / especialistas | 130 / 894 |
| coorte 2025-10 (trimestre): municípios / especialistas | 34 / 197 |
| coorte 2026-01 (trimestre): municípios / especialistas | 47 / 150 |
| coorte 2026-04 (trimestre): municípios / especialistas | 104 / 226 |
<!-- KD2:amostra:fim -->

ATT médio do pós (média de θ(e) de 0 a +9 meses, ou até onde a série vai),
teste conjunto da pré-tendência (θ(e) = 0 de −24 a −2) e dose descritiva por
especialista. "Nunca tratados" = sem chegada dentro do horizonte da série (para
K3, que vai até dez/2025, inclui as coortes de 2026):

<!-- KD2:att:inicio -->
| Outcome | Tratados / nunca tratados | Coortes | ATT médio do pós | IC 95% (bootstrap) | p | θ médio do pré (−24 a −2) | Pré: Wald (gl), p | Pré: p sup-t | Dose por especialista (descritivo) |
|---|---|---|---|---|---|---|---|---|---|
| K1 | 315 / 283 | 4 | +31,37 | [−5,14; +67,88] | 0,092 | −20,80 | 23,1 (23), 0,454 | 0,611 | +6,74 |
| K1a | 315 / 283 | 4 | +30,73 | [−10,38; +71,84] | 0,143 | +1,27 | 22,1 (23), 0,512 | 0,516 | +6,60 |
| K1b | 315 / 283 | 4 | +0,59 | [−50,05; +51,23] | 0,982 | −21,22 | 29,1 (23), 0,176 | 0,330 | +0,13 |
| K1c | 315 / 283 | 4 | +0,23 | [−0,96; +1,43] | 0,702 | −0,15 | 30,2 (23), 0,145 | 0,621 | +0,05 |
| K1d | 315 / 283 | 4 | +65,03 | [+1,72; +128,33] | 0,044 | +9,15 | 26,5 (23), 0,276 | 0,792 | +13,96 |
| K2 | 315 / 283 | 4 | +0,77 | [−0,97; +2,52] | 0,385 | +2,60 | 38,9 (23), 0,020 | 0,012 | +0,17 |
| KP1 | 315 / 283 | 4 | −110,66 | [−429,29; +207,96] | 0,496 | −126,67 | 31,3 (23), 0,115 | 0,148 | −23,76 |
| KP2 | 315 / 283 | 4 | +33,66 | [−15,15; +82,46] | 0,176 | +29,95 | 29,2 (23), 0,174 | 0,545 | +7,23 |
| K4.vinculos | 315 / 283 | 4 | −0,13 | [−0,25; −0,01] | 0,035 | −0,08 | 26,0 (22), 0,250 | 0,359 | −0,03 |
| K4.horas | 315 / 283 | 4 | −1,88 | [−3,88; +0,11] | 0,064 | +0,01 | 13,2 (22), 0,928 | 0,904 | −0,40 |
| K3 | 164 / 434 | 2 | +32,32 | [−23,46; +88,11] | 0,256 | +5,22 | 25,9 (23), 0,307 | 0,608 | +4,86 |
<!-- KD2:att:fim -->

<!-- KD2:leitura_d2:inicio -->
K1: ATT médio do pós +31,37 por 10 mil hab. por mês (IC 95% [−5,14; +67,88], p = 0,092); pré compatível com plano (p do Wald = 0,454); K1a: ATT médio do pós +30,73 por 10 mil hab. por mês (IC 95% [−10,38; +71,84], p = 0,143); pré compatível com plano (p do Wald = 0,512); K1b: ATT médio do pós +0,59 por 10 mil hab. por mês (IC 95% [−50,05; +51,23], p = 0,982); pré compatível com plano (p do Wald = 0,176); K1c: ATT médio do pós +0,23 por 10 mil hab. por mês (IC 95% [−0,96; +1,43], p = 0,702); pré compatível com plano (p do Wald = 0,145); K1d: ATT médio do pós +65,03 por 10 mil hab. por mês (IC 95% [+1,72; +128,33], p = 0,044); pré compatível com plano (p do Wald = 0,276); K2: ATT médio do pós +0,77 por 10 mil hab. por mês (IC 95% [−0,97; +2,52], p = 0,385); pré não plano (p do Wald = 0,020); KP1: ATT médio do pós −110,66 por 10 mil hab. por mês (IC 95% [−429,29; +207,96], p = 0,496); pré compatível com plano (p do Wald = 0,115); KP2: ATT médio do pós +33,66 por 10 mil hab. por mês (IC 95% [−15,15; +82,46], p = 0,176); pré compatível com plano (p do Wald = 0,174); K4.vinculos: ATT médio do pós −0,13 por 10 mil hab. por mês (IC 95% [−0,25; −0,01], p = 0,035); pré compatível com plano (p do Wald = 0,250); K4.horas: ATT médio do pós −1,88 por 10 mil hab. por mês (IC 95% [−3,88; +0,11], p = 0,064); pré compatível com plano (p do Wald = 0,928); K3: ATT médio do pós +32,32 por 10 mil hab. por mês (IC 95% [−23,46; +88,11], p = 0,256); pré compatível com plano (p do Wald = 0,307). 10 de 11 outcomes têm pré compatível com tendências paralelas pelo teste conjunto a 5%. Onde o pré não é plano, a diferença do pós é só uma associação; onde é plano, continua sendo ATT sob tendências paralelas, porque a chegada depende da escolha do candidato, sem fonte de exogeneidade validada. Em K2 (θ médio do pré +2,60 contra ATT do pós +0,77); KP1 (θ médio do pré −126,67 contra ATT do pós −110,66); KP2 (θ médio do pré +29,95 contra ATT do pós +33,66); K4.vinculos (θ médio do pré −0,08 contra ATT do pós −0,13), o θ médio do pré tem o mesmo sinal e pelo menos metade do tamanho do ATT do pós: boa parte da diferença do pós já aparece antes da chegada, em relação ao mês-base, e não pode ser lida como mudança causada pela chegada.
<!-- KD2:leitura_d2:fim -->

<!-- KD2:leitura_simples_d2:inicio -->
Em linguagem simples, depois que o 1º especialista do PMM-E começou no município: produção SUS dos especialistas-alvo (K1): a mudança não se distingue da dos comparáveis; cirurgias com internação no SUS (K2): a mudança não se distingue da dos comparáveis (mas o município já vinha diferente antes da chegada); vínculos privados (não SUS) dos especialistas-alvo (K4.vinculos): a mudança ficou menor do que nos comparáveis (mas boa parte dessa diferença já aparecia antes da chegada, em relação ao mês-base); consultas SUS + planos dos especialistas-alvo (K3): a mudança não se distingue da dos comparáveis. Os comparáveis são municípios que também ofereceram vaga e ainda não tinham recebido especialista. Como quem chega escolhe o município, isso é uma comparação, não a prova de um efeito.
<!-- KD2:leitura_simples_d2:fim -->

Sensibilidade do §5 D2 (sem os municípios com alocado na 1ª chamada e sem
especialista ativo):

<!-- KD2:sensibilidade:inicio -->
| Outcome | Variante | ATT médio do pós | IC 95% | p | Pré: p Wald | Tratados / nunca tratados |
|---|---|---|---|---|---|---|
| K1 | sem_alocado_sem_ativo | +22,78 | [−11,26; +56,82] | 0,190 | 0,381 | 315 / 183 |
| K1a | sem_alocado_sem_ativo | +29,15 | [−11,92; +70,23] | 0,164 | 0,419 | 315 / 183 |
| K1b | sem_alocado_sem_ativo | −6,78 | [−56,41; +42,85] | 0,789 | 0,345 | 315 / 183 |
| K1c | sem_alocado_sem_ativo | +0,26 | [−1,03; +1,54] | 0,694 | 0,233 | 315 / 183 |
| K1d | sem_alocado_sem_ativo | +51,17 | [−11,86; +114,21] | 0,112 | 0,113 | 315 / 183 |
| K2 | sem_alocado_sem_ativo | +1,08 | [−0,74; +2,89] | 0,244 | 0,195 | 315 / 183 |
| KP1 | sem_alocado_sem_ativo | −177,26 | [−540,19; +185,67] | 0,338 | 0,133 | 315 / 183 |
| KP2 | sem_alocado_sem_ativo | +28,39 | [−23,15; +79,93] | 0,280 | 0,079 | 315 / 183 |
| K4.vinculos | sem_alocado_sem_ativo | −0,10 | [−0,22; +0,02] | 0,114 | 0,342 | 315 / 183 |
| K4.horas | sem_alocado_sem_ativo | −1,48 | [−3,45; +0,49] | 0,142 | 0,904 | 315 / 183 |
| K3 | sem_alocado_sem_ativo | +32,64 | [−22,71; +87,99] | 0,248 | 0,248 | 164 / 334 |
<!-- KD2:sensibilidade:fim -->

Resumo do estudo de evento por janela (θ(e) mês a mês no CSV e nas figuras):

<!-- KD2:evento:inicio -->
| Outcome | Janela | Tempos de evento estimados | p < 0,05 | maior abs(θ) | θ médio |
|---|---|---|---|---|---|
| K1 | pre | 23 | 0 | 242,91 | −20,80 |
| K1 | pos | 10 | 1 | 103,02 | +31,37 |
| K1a | pre | 23 | 0 | 31,92 | +1,27 |
| K1a | pos | 10 | 0 | 48,78 | +30,73 |
| K1b | pre | 23 | 0 | 247,14 | −21,22 |
| K1b | pos | 10 | 0 | 58,62 | +0,59 |
| K1c | pre | 23 | 0 | 6,35 | −0,15 |
| K1c | pos | 10 | 0 | 1,47 | +0,23 |
| K1d | pre | 23 | 0 | 290,10 | +9,15 |
| K1d | pos | 10 | 1 | 161,50 | +65,03 |
| K2 | pre | 23 | 10 | 5,42 | +2,60 |
| K2 | pos | 10 | 1 | 2,16 | +0,77 |
| KP1 | pre | 23 | 1 | 356,71 | −126,67 |
| KP1 | pos | 10 | 0 | 201,40 | −110,66 |
| KP2 | pre | 23 | 0 | 83,31 | +29,95 |
| KP2 | pos | 10 | 1 | 71,51 | +33,66 |
| K4.vinculos | pre | 22 | 0 | 0,29 | −0,08 |
| K4.vinculos | pos | 10 | 4 | 0,21 | −0,13 |
| K4.horas | pre | 22 | 0 | 1,53 | +0,01 |
| K4.horas | pos | 10 | 1 | 3,25 | −1,88 |
| K3 | pre | 23 | 0 | 51,17 | +5,22 |
| K3 | pos | 6 | 0 | 64,25 | +32,32 |
<!-- KD2:evento:fim -->

## 8. Leitura de substituição (§5 do protocolo)

A X1 mostrou que parte grande dos especialistas já estava no município antes do
início; por isso a pergunta central é se a produção SUS das CBO-alvo cresce às
custas do privado na mesma especialidade (migração), se o total cresce (ganho
líquido) ou se outra especialidade perde (remanejamento). A classificação
abaixo é feita pelo IC 95% de cada margem e é gerada das saídas.

<!-- K:leitura_substituicao:inicio -->
D1 (DiRD nos cortes, U, empilhado). Sinal de cada margem pelo IC 95% ('sobe' = IC acima de zero; 'cai' = abaixo; 'indeterminado' = inclui zero): SUS nas CBO-alvo (K1): indeterminado; vínculos não SUS das CBO-alvo (K4.vinculos): indeterminado; horas não SUS das CBO-alvo (K4.horas): indeterminado; consultas dos planos nas CBO-alvo (K3a.consultas): indeterminado; consultas SUS + planos nas CBO-alvo (K3): indeterminado; SUS dos especialistas fora das CBO-alvo (KP2): indeterminado. Nenhum dos três padrões do §5 (migração, ganho líquido, remanejamento) aparece, porque nenhuma das margens necessárias tem IC que exclua zero no sentido exigido. Isso não mostra ausência de substituição: mostra que os dados não a distinguem de zero.
<!-- K:leitura_substituicao:fim -->

<!-- KD2:leitura_substituicao_d2:inicio -->
D2 (chegada, ATT médio do pós). Sinal de cada margem pelo IC 95% ('sobe' = IC acima de zero; 'cai' = abaixo; 'indeterminado' = inclui zero): SUS nas CBO-alvo (K1): indeterminado; vínculos não SUS das CBO-alvo (K4.vinculos): cai; horas não SUS das CBO-alvo (K4.horas): indeterminado; consultas SUS + planos nas CBO-alvo (K3, coortes até 2025-12): indeterminado; SUS dos especialistas fora das CBO-alvo (KP2): indeterminado. Nenhum dos três padrões do §5 (migração, ganho líquido, remanejamento) aparece, porque nenhuma das margens necessárias tem IC que exclua zero no sentido exigido. Isso não mostra ausência de substituição: mostra que os dados não a distinguem de zero.
<!-- KD2:leitura_substituicao_d2:fim -->

"Privado" aqui é a capacidade não SUS no CNES (K4) e o que os planos pagam
(TISS); o desembolso direto não tem fonte pública por município e não entra.

## 9. Figuras

Todas com o bloco "COMO LER" dentro da imagem, no estilo de
`output/rdd_bolsa/N_figuras/`.

- D1, mudança entre pré e pós nos cortes (pontos por faixa de IVS de 0,010,
  retas de cada lado, seta do salto):
  [K1](../../output/rdd_bolsa/K_D1_figuras/K_D1_dird_K1_U.png),
  [K2](../../output/rdd_bolsa/K_D1_figuras/K_D1_dird_K2_U.png),
  [K3](../../output/rdd_bolsa/K_D1_figuras/K_D1_dird_K3_U.png),
  [K1d](../../output/rdd_bolsa/K_D1_figuras/K_D1_dird_K1d_U.png),
  [KP1](../../output/rdd_bolsa/K_D1_figuras/K_D1_dird_KP1_U.png),
  [KP2](../../output/rdd_bolsa/K_D1_figuras/K_D1_dird_KP2_U.png),
  [K4.vinculos](../../output/rdd_bolsa/K_D1_figuras/K_D1_dird_K4_vinculos_U.png).
- D1, estudo de evento (salto mês a mês contra jun/2025):
  [K1](../../output/rdd_bolsa/K_D1_figuras/K_D1_evento_K1_U.png),
  [K2](../../output/rdd_bolsa/K_D1_figuras/K_D1_evento_K2_U.png),
  [K3](../../output/rdd_bolsa/K_D1_figuras/K_D1_evento_K3_U.png),
  [K1d](../../output/rdd_bolsa/K_D1_figuras/K_D1_evento_K1d_U.png),
  [KP1](../../output/rdd_bolsa/K_D1_figuras/K_D1_evento_KP1_U.png),
  [KP2](../../output/rdd_bolsa/K_D1_figuras/K_D1_evento_KP2_U.png),
  [K4.vinculos](../../output/rdd_bolsa/K_D1_figuras/K_D1_evento_K4_vinculos_U.png).
- D2, estudo de evento da chegada: um arquivo por outcome em
  `output/rdd_bolsa/K_D2_figuras/` (por exemplo,
  [K1](../../output/rdd_bolsa/K_D2_figuras/K_D2_evento_K1.png),
  [K2](../../output/rdd_bolsa/K_D2_figuras/K_D2_evento_K2.png),
  [K3](../../output/rdd_bolsa/K_D2_figuras/K_D2_evento_K3.png),
  [K4.vinculos](../../output/rdd_bolsa/K_D2_figuras/K_D2_evento_K4_vinculos.png)).

## 10. Limites

- **Pacote no corte.** Mesmo um salto nítido no D1 seria o incentivo marginal
  mais a variação das outras políticas com o mesmo corte (auditoria 18). O
  placebo de generalistas (KP1) e o estudo de evento são as checagens; nenhuma
  remove a ameaça.
- **Teste posterior à síntese.** R4 e R5 (sem salto no preenchimento e no CNES)
  já eram conhecidos; a família K não é confirmação independente.
- **Mês de processamento** no SIA e no SIH (produção tardia entra no mês em que é
  processada) contra **mês de realização** no TISS; K3 soma os dois.
- **Local de atendimento**, não residência: deslocamento de pacientes entre
  municípios aparece como mudança de produção local.
- **TISS.** Só planos (sem desembolso direto); CBO ausente em parte dos eventos
  (K3a de exames e cirurgias é piso); hospitalar sem CBO; possível
  subnotificação no último trimestre de 2025 (§11.4), que numa DiRD só pesa se
  for diferente dos dois lados do corte; pós de três meses, só do ciclo 1.
- **SIH sem CBO:** K2 conta toda AIH cirúrgica do município.
- **Municípios instalados depois do Censo 2022 ou depois de 2010** (sem
  população ou sem IVS) ficam fora; a produção dos municípios de origem pode ter
  quebra de série.
- **D2.** A lista nominal é um retrato de quem estava ativo; a coorte trimestral
  data a chegada pelo início do trimestre (o tratamento efetivo pode começar até
  dois meses depois); as coortes de 2026 têm poucos meses de pós; o ATT do pós
  médio mistura tempos de evento com coortes diferentes.
- **Poder.** O MDE das primárias está na tabela da seção 4: efeitos menores que
  ele não seriam detectados.

## 11. Desvios e esclarecimentos

<!-- K:desvios:inicio -->
| Data | Tipo | Item | Descrição |
|---|---|---|---|
| 2026-10-19 | esclarecimento | K1e | o protocolo 47 (§4, §10, §11) define K1a, K1b, K1c, K1d e K1f; nao existe K1e. Nada foi estimado com esse nome. |
| 2026-10-19 | esclarecimento | K3b | 'K3 com SIA no mesmo pos 202510-202512, para separar janela de fonte' foi lido como a parte SIA de K3 (consultas 0301 das CBO-alvo) com pre 202406-202506 e pos 202510-202512: K3 = K3b + K3a.consultas, e K3b contra K1a separa a janela; K3 contra K3b separa a fonte. |
| 2026-10-19 | esclarecimento | janela de K4 | o protocolo nao da o pos de K4 (CNES). Fixado antes de estimar: o mesmo pos de K1 (202510-202605), para que a leitura de substituicao SUS x privado (§5) compare a mesma janela; o pos do E7 (202510-202608) e sensibilidade. Nenhum mes CNES >= 202609 e lido. |
| 2026-10-19 | esclarecimento | medida de K3c e K4.horas | K3c usa a quantidade informada (qt_itens, §3.2) dos itens cirurgicos do TISS hospitalar; o numero de internacoes com item cirurgico (n_eventos) e variante. K4.horas = horas_totais_amb_hosp - horas_sus_semanais (ambulatorial + hospitalar, total menos SUS, regra do §16 do protocolo 40); hora em branco fica ausente. |
| 2026-10-19 | esclarecimento | K5 | participacao do SUS = soma(SIA) / soma(SIA + TISS) das consultas das CBO-alvo nos meses da janela com os dois dados; municipio sem nenhuma consulta na janela tem a razao indefinida e sai (contado). Sem Poisson (nao e contagem). |
| 2026-10-19 | esclarecimento | principal com meses de dado | a robustez 'media do pos em vez da media de meses com dado' (§5 D1) fixa o principal como a media dos meses com dado e a robustez (media_completa) como so os municipios com todos os meses. Ausencia nunca vira zero. |
| 2026-10-19 | esclarecimento | testes multiplos | Holm entre K1, K2 e K3 (linha principal, U, cortes empilhados); BKY nas secundarias (mesma linha, uma por outcome). Placebos e KP1.mfc ficam fora dos dois. |
| 2026-10-19 | esclarecimento | S1 a S6 | S2, S3 e S4 por outcome como no E7; S5 = linhas S5_pre_menos_pre_extra e o pre extra do estudo de evento; S6 = KP1.mfc; S1 (RDD no PMMB) nao depende do outcome e esta no E6. Local randomization nao esta no protocolo 47 e nao foi estimada. |
| 2026-10-19 | esclarecimento | efeito relativo | efeito relativo = salto / media simples de Y_pre dos municipios abaixo do corte na janela (-h < x <= 0) com delta definido; no empilhado, as linhas dos dois cortes juntas. MDE = 2,8 x EP. |
| 2026-10-19 | esclarecimento | variantes por fonte | 'ate 202607' vale para todo outcome SIA/SIH; 'sem grupo 09' para todo outcome SIA que inclui OCI; 'sem UF-mes atipico' e 'pos 202510-202511' para os outcomes TISS; 'com TUSS 63' so para exames. |
<!-- K:desvios:fim -->

<!-- KD2:desvios:inicio -->
| Data | Tipo | Item | Descrição |
|---|---|---|---|
| 2026-10-19 | esclarecimento | data da coorte | coorte trimestral datada pelo primeiro mês do trimestre da chegada; tempo de evento em meses a partir desse mês; base universal b = g - 1 (o mês antes do trimestre), que é anterior à chegada de todos da coorte. |
| 2026-10-19 | esclarecimento | fim da série | SIA, SIH e CNES até 202605 (o pós principal do D1 pelo adendo §10.1, meses imaturos fora); K3 até 202512 (TISS). Nenhum mês CNES >= 202609 é lido. |
| 2026-10-19 | esclarecimento | K4 no D2 | K4 entra como duas linhas, vínculos e horas não SUS; o CNES é trimestral antes de 202406, então tempos de evento sem competência ficam sem ATT (não são preenchidos). |
| 2026-10-19 | esclarecimento | inferência | bootstrap multiplicador (Mammen) implementado no script, sem pacote externo; a unidade do bootstrap é o município, que é o cluster pedido. O IF de θ(e) inclui o termo da estimação dos pesos de coorte. |
| 2026-10-19 | esclarecimento | tratado fora da amostra | município da lista nominal que não ofereceu célula nos ciclos 1 ou 2 (ou sem IVS/população) fica fora e é contado no resumo. |
<!-- KD2:desvios:fim -->

## 12. Entradas (D1)

<!-- K:entradas:inicio -->
| Entrada | SHA-256 | Papel |
|---|---|---|
| `output/aquisicao/sia/painel_sia_municipio_mes_subgrupo_cbo.parquet` | `2f0c8353deb58eeb…` | SIA/SUS: K1, K1a-K1f, K3, K3b, K5, KP1, KP2 |
| `output/aquisicao/sia/sia_subgrupos_por_consulta.csv` | `3b9b4d4aa060147d…` | SIA: subgrupos presentes em cada consulta (zero de subgrupo omitido) |
| `output/aquisicao/sia/sia_municipios_tabnet.csv` | `fbc96adae2ba4b4d…` | SIA: lista de municipios do formulario |
| `output/aquisicao/sia/manifesto_sia.json` | `aa31915d31d2f354…` | manifesto SIA (SHA-256 do painel) |
| `output/aquisicao/sih/painel_sih_municipio_mes_grupo.parquet` | `3428600a111838d7…` | SIH/SUS: K2 |
| `output/aquisicao/sih/manifesto_sih.json` | `9d2648760c23e568…` | manifesto SIH (SHA-256 do painel) |
| `output/aquisicao/tiss/painel_tiss_municipio_mes_tipo_cbo.parquet` | `5ebd922df41456c8…` | TISS ambulatorial: K3, K3a, K5 |
| `output/aquisicao/tiss/painel_tiss_hospitalar_municipio_mes_tipo.parquet` | `840c05d0c9293f0c…` | TISS hospitalar: K3c |
| `output/aquisicao/tiss/validacao_tiss.json` | `344f4e6be5362e9e…` | TISS: UF-meses sinalizados (alertas_queda) |
| `output/aquisicao/tiss/manifesto_tiss.json` | `8201939a1d5f65f3…` | manifesto TISS (SHA-256 dos paineis) |
| `output/aquisicao/cnes_nacional/painel_municipio_cbo_mes.parquet` | `08aec0e3b4b4fafa…` | CNES: K4 (vinculos e horas nao SUS das CBO-alvo) |
| `output/aquisicao/a09_manifesto_cnes_nacional.json` | `666d3283f36e323a…` | manifesto CNES (SHA-256 do painel) |
| `output/aquisicao/a08_ivs_2010_oficial_municipio.csv` | `0632a7a313e1179f…` | running variable (IVS 2010 oficial) e universo U |
| `output/aquisicao/populacao_censo2022_municipios.csv` | `b51fc6cf27a49fd5…` | denominador por 10 mil hab. |
| `output/rdd_bolsa/outcomes/outcomes_V_municipio.parquet` | `36ced6f6a4c41407…` | lista de V1 (quadro do ciclo 1) |
| `output/aquisicao/a10_ied_aps_2024_municipio.csv` | `2bd4aec48a14e610…` | S3: porte e estrato IED |
| `data/raw/aquisicao/ivs_administrativo/ppf_mais_medicos_csv.zip` | `15083f8127917e52…` | S4: Amazonia Legal / faixa de fronteira |
| `docs/06_execucao/47_protocolo_producao_especializada.md` | `27b8f4535798dba2…` | protocolo congelado (com adendos §10 e §11) |
| `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md` | `9afe8cc10cc28edc…` | datas das politicas nos mesmos cortes |
<!-- K:entradas:fim -->
