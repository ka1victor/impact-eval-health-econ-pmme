# 57t. Seleção pelo tipo de vaga na H1: tipo como outcome, balanço na amostra selecionada e limites de Lee (adendo 48f)

> **Data:** 26/10/2026.<br>
> **Adendo:** [`48f_adendo_selecao_tipo_de_vaga.md`](48f_adendo_selecao_tipo_de_vaga.md), congelado antes destas contas
> (commit `f97e1ca`). SHA-256 do adendo em `adendo` de `SV_resumo.json`, conferido pelo script.<br>
> **Estatuto:** `ADENDO_48F_POS_RESULTADO`. A H1 só com vagas imediatas (48b, doc 57n) e o salto da parte de células
> só de reserva (doc 57l, D-b) já tinham sido vistos. Toda linha de `SV_estimativas.csv` e `SV_balanco.csv` tem
> `natureza_dos_dados = EMPIRICO`.<br>
> **Auditoria:** pendente.<br>
> **Script:** `scripts/rdd_bolsa/46_selecao_tipo_vaga.py` (construtores dos scripts 40 e 44, estimadores de
> `rdd_lib.py` e o IC de Imbens–Manski do script 24, importados). **Saídas:** `output/rdd_bolsa/SV_estimativas.csv`,
> `SV_balanco.csv`, `SV_resumo.json`, `SV_figuras/`. **Testes:** `tests/test_selecao_tipo_vaga.py`.<br>
> **Números:** nenhum é digitado. Os blocos entre marcadores `<!-- SV:... -->` são regravados das saídas por
> `46_selecao_tipo_vaga.py --atualizar-doc`; o teste confere que cada bloco é idêntico ao gerado.

**Contraste.** Em toda linha, o lado com bolsa maior (IVS acima do corte) é comparado com o lado com bolsa menor; o
próprio corte fica no lado de baixo. Em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil e em 0,400 de
R$ 15 mil para R$ 20 mil, mas outras regras federais mudam nos mesmos cortes
([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)). O que se mede é o **pacote do corte**, não o
incentivo de R$ 5 mil isolado, nem a participação no PMM-E, nem o Agora Tem Especialistas. Este adendo é robustez da
H1: o principal continua o 48b.

**A pergunta, em linguagem simples.** A SGTES decide qual município recebe vaga imediata e qual fica no cadastro
reserva, com critério que não está nos dados. A H1 do 48b compara só municípios (e células) com vaga imediata. Se o
corte muda a chance de ter vaga imediata, os municípios com vaga imediata acima e abaixo do corte podem não ser
comparáveis. Este doc mede o tamanho dessa seleção (SV-1), olha se os municípios selecionados são parecidos dos dois
lados (SV-2) e dá um intervalo para o salto da H1 que vale qualquer que tenha sido a regra do Ministério, desde que
ela empurre todos os municípios na mesma direção (SV-3 a SV-5).

## 0. Decisões de implementação (26/10/2026, registradas antes de qualquer estimativa deste adendo)

O adendo deixa alguns pontos abertos. Em cada um, ficou a leitura mais próxima dos scripts 40 (H1 só com vagas
imediatas) e 44 (controles e pareamento). Estas decisões foram escritas e registradas em commit antes de rodar qualquer
conta do adendo, inclusive o portão. Nenhuma depende de resultado.

**Amostra e variáveis**

1. **Unidade.** Município × ciclo, ciclos 1–3, da base `MK` montada por `bases_h1` do script 44 (que chama
   `carregar()` do script 40, versão `13fev`): municípios com IVS 2010 oficial (a08) e pelo menos uma célula no quadro
   da 1ª chamada do ciclo, de qualquer tipo. Municípios sem IVS oficial ficam fora da RDD, como no 48b (contados pelo
   script 40). O script confere que toda linha tem pelo menos uma célula (só imediata, mista ou só de reserva).
2. **Tipo de vaga.** O do quadro da 1ª chamada; no ciclo 2, o do quadro retificado de 13/02/2026 (48b, §7), lido pelo
   script 40 com `scripts/auditoria_H1/a36_leitura.py`.
3. **Seleção.** S = 1 quando o município × ciclo tem pelo menos uma célula com vaga imediata (só imediata ou mista),
   isto é, `n_cel_imed > 0` do script 40.
4. **Outcomes.** Y1 = `frac_preenchida` e Y2 = `aloc_por_vi` do `bases_h1` do script 44: as mesmas versões municipais
   da H1 usadas no pareamento do 48d (H1M-FRAC e H1M-ALOC). Y1 é a fração das células com vaga imediata do município
   preenchidas na 1ª chamada (`n_alocados_ch1 >= 1`, a definição do A3 e da HI-1); Y2 é o número de médicos alocados
   na 1ª chamada nessas células dividido pelas vagas imediatas delas. Nas células mistas contam todos os alocados da
   célula (limite herdado do 48b). O script confere que Y1 e Y2 são observados exatamente quando S = 1; quando S = 0
   ficam ausentes, nunca zero.
5. **Covariáveis do SV-2.** As do balanço CL-0 do 48d, construídas por `construir_covariaveis` do script 44: capital,
   uma indicadora por macrorregião (as cinco), log da população do Censo 2022, médicos (CBO 2251, 2252, 2253) por
   10 mil hab. no município, especialistas nas CBO-alvo (todas) por 10 mil hab. no município e no resto da região de
   saúde, média de 2024-06 a 2025-06 do painel a09. Valor ausente fica ausente; a `rdd_lib` descarta a linha e conta.

**SV-1 (tamanho da seleção)**

6. **RDD de S no município.** `ajustar` do script 23 sem controle, na amostra empilhada de `amostra` do script 40
   (intercepto e inclinações por ciclo × lado, salto comum, local linear, kernel triangular, h = 0,050, CR1 por
   município), cada corte separado: a especificação comum do adendo.
7. **RDD de "célula tem vaga imediata".** `est_celula` do script 40 (efeitos fixos de curso × ciclo, CR1 por
   município) com todas as células do quadro, de qualquer tipo; outcome = `tipo_vaga_imediata` (1 se a célula tem
   vaga imediata; ciclo 2 pelo quadro de 13/02).
8. **Qual linha entra na leitura do §4.** A de S no município × ciclo, que é a unidade dos limites de Lee. A da célula
   é relatada ao lado; se as duas discordarem (uma com IC que exclui zero e a outra não), isso é dito.

**Taxas de seleção e aparagem (SV-3; mesmas regras no SV-4 e no SV-5)**

9. **Janela e pesos.** x = IVS − corte em milésimos (`normalizar_s_mil`); peso = kernel triangular da `rdd_lib`
   (`pesos_kernel(x, 50)`), positivo em |x| < 0,050 (em |x| = 0,050 o peso triangular já é zero). Lado de cima:
   x > 0; o corte fica no lado de baixo, como em toda a RDD.
10. **Taxas por ciclo.** Em cada ciclo k, p_acima,k e p_abaixo,k = média de S ponderada pelo kernel entre as
    unidades de cada lado na janela.
11. **Fração aparada por ciclo.** q_k = (p_maior − p_menor) / p_maior, no lado de taxa maior. Taxas iguais: q_k = 0
    e nada é aparado.
12. **Quantis ponderados.** Apara-se q_k da massa de peso do kernel das unidades com S = 1 do lado aparado, pela função
    `_multiplicador_aparo` da `rdd_lib` com `empates="proporcional"` (auditoria 22): Y1 é uma fração com muitos
    valores repetidos (0, 1/2, 1), e assim o bloco de valores iguais na fronteira perde a mesma fração de peso em todas
    as suas unidades, sem depender da ordem das linhas. A unidade da fronteira é aparada em parte (peso fracionário).
13. **Direção (§3, passo 2, literal).** Salto = acima − abaixo. Lado aparado de **cima**: no limite inferior saem as
    unidades de **maior** Y; no superior, as de **menor** Y. Lado aparado de **baixo**: no limite inferior saem as de
    **menor** Y; no superior, as de **maior** Y.
14. **Limites por ciclo.** Diferença entre a média de Y ponderada pelo kernel (já aparada) das unidades com S = 1 de
    cima e a de baixo. A mesma diferença sem aparo é relatada como "sem aparo" (referência, não é limite).
15. **Combinação dos ciclos.** n_k = número de unidades município × ciclo com S = 1 e peso positivo na janela (os dois
    lados). Limite do corte = Σ n_k × limite_k ÷ Σ n_k; o mesmo para o "sem aparo". Ciclo sem unidade com S = 1 e peso
    positivo em algum dos lados fica fora da combinação (contado); sem ciclo, a linha fica sem estimativa.
16. **Taxas e q do corte (para relatar e para a leitura).** p_acima e p_abaixo do corte = médias das taxas por ciclo
    com os mesmos pesos n_k; q do corte = (maior − menor) ÷ maior dessas duas. É esse q que entra na regra "q < 0,05"
    do §4. As taxas, o q e o lado aparado de cada ciclo ficam nas linhas por ciclo.

**Bootstrap e IC de Imbens–Manski**

17. **Bootstrap em blocos de município.** Em cada corte e janela, o bloco é o município (todas as suas linhas
    município × ciclo na janela). Sorteiam-se municípios com reposição **dentro de cada lado do corte** (o lado é fixo
    pelo IVS; cada lado mantém o seu número de municípios); a multiplicidade entra como peso de frequência, como no
    bootstrap do script 24. 1.999 reamostras. Cada combinação corte × janela começa um gerador novo
    (`numpy.random.default_rng(20261026)`); os mesmos sorteios servem a Y1 e a Y2 e às versões sem e com a reta.
18. **Refazer tudo em cada reamostra.** Taxas, lado aparado, q_k, aparagem e combinação são refeitos com os pesos
    kernel × multiplicidade. Reamostra em que um limite não fica definido é descartada e contada.
19. **IC 95% de Imbens e Manski (2004).** EP de cada limite = desvio-padrão (ddof = 1) das reamostras válidas; IC =
    [inf − c × ep_inf; sup + c × ep_sup], com c de Φ(c + Δ / máx(ep)) − Φ(−c) = 0,95 e Δ = sup − inf (função
    `ic_imbens_manski` do script 24, importada). O "sem aparo" leva EP do mesmo bootstrap e IC normal (±1,96 EP).

**SV-4 e SV-5**

20. **SV-4 (janela 0,020).** O SV-3 inteiro com kernel triangular de h = 0,020 (a janela define o suporte do kernel,
    como 0,050 no SV-3).
21. **SV-5 (com a reta).** Em cada ciclo × lado, entre as unidades com S = 1 e peso positivo, ajusta-se por mínimos
    quadrados ponderados pelo kernel a reta de Y em x. A aparagem (mesmo q_k, mesma direção da decisão 13) é feita nos
    resíduos. Limite do ciclo = (intercepto de cima − intercepto de baixo) + (média ponderada dos resíduos que ficaram
    em cima − a de baixo); do lado não aparado essa média é zero. Ciclo × lado com menos de dois valores distintos de
    x com peso positivo fica fora (contado). No bootstrap a reta é reajustada em cada reamostra.

**SV-2 (balanço)**

22. **Estimador.** `ajustar` do script 23 sem controle, como o CL-0 do 48d, cada covariável como outcome, em duas
    amostras: só S = 1 (que é a amostra da HI-2 e reproduz as linhas município × ciclo do CL-0 em `CL_balanco.csv`;
    conferido) e a amostra toda (todo município × ciclo do quadro).
23. **Escala comum.** Salto padronizado = salto ÷ desvio-padrão da covariável na janela da amostra toda (peso
    positivo, valor observado). O mesmo denominador nas duas amostras.
24. **Regra de leitura do SV-2.** Em cada corte, "desbalanço maior entre S = 1" se o número de covariáveis com IC 95%
    que exclui zero for maior entre S = 1 do que na amostra toda. A média do |salto padronizado| é relatada, sem
    entrar na regra.

**Portão**

25. **HI-1 e HI-2 do 48b.** Pela função `portao_hi` do script 44 (funções do script 40, diferença ≤ 1e−8 contra
    `HI_estimativas.csv`, nos dois cortes). Se falhar, o script para sem gravar.
26. **Parte de células só de reserva do doc 57l (D-b).** Refazem-se, com o quadro do ciclo 2 de 19/03/2026 (o que o 57l
    usou, antes da nota §7 do 48b), as linhas "célula só de CR" (célula, sem efeitos fixos) e "parte das células só de
    CR (municípios)" (peso = células) de `DQ_estimativas.csv`, por ciclo e com os ciclos juntos, nos dois cortes:
    salto, EP, n por lado, média abaixo e média acima, ≤ 1e−8. Se não bater, para. **Diferença de definição relatada:**
    o 48f mede S (município × ciclo com alguma vaga imediata), não a parte das células só de reserva, e no ciclo 2 usa
    o quadro de 13/02; a mesma medida do D-b com o quadro de 13/02 é relatada ao lado, descritiva.

**Leitura (regras fixadas no código, pelo §4 do adendo)**

27. **SV-1, por corte:** IC da RDD de S que exclui zero → "o tipo de vaga responde ao corte; dar peso aos limites";
    IC que contém zero e q < 0,05 → "seleção pequena; o 48b não é muito afetado por ela"; IC que contém zero e
    q ≥ 0,05 → caso fora da tabela do §4: "não se detecta salto no tipo de vaga, mas as taxas na janela diferem; dar
    peso aos limites".
28. **SV-3, por corte e outcome:** intervalo identificado [inf; sup] que contém zero (o IC de Imbens–Manski então
    também contém) → "não se detecta diferença de preenchimento no corte, mesmo sem supor nada sobre como o Ministério
    escolheu o tipo, além da monotonicidade"; intervalo inteiro de um lado do zero → "sinal robusto à seleção pelo tipo
    de vaga, com o pacote do corte", dizendo se o IC de Imbens–Manski exclui zero ou não.
29. **SV-4 e SV-5** são sensibilidades: a mesma regra é aplicada e relatada ao lado, sem mudar a leitura do SV-3.
30. **Testes múltiplos.** O adendo não define família; nenhum ajuste de Holm ou BKY é feito.

## 1. Resposta curta

<!-- SV:resposta_curta:inicio -->
(gerado pelo script)
<!-- SV:resposta_curta:fim -->

### 1.1 Portão

<!-- SV:portao:inicio -->
(gerado pelo script)
<!-- SV:portao:fim -->

## 2. Amostra

<!-- SV:amostra:inicio -->
(gerado pelo script)
<!-- SV:amostra:fim -->

## 3. SV-1 — o tipo de vaga responde ao corte?

<!-- SV:sv1:inicio -->
(gerado pelo script)
<!-- SV:sv1:fim -->

## 4. SV-2 — os municípios com vaga imediata são parecidos dos dois lados?

<!-- SV:sv2:inicio -->
(gerado pelo script)
<!-- SV:sv2:fim -->

## 5. SV-3 — limites de Lee para o salto da H1

<!-- SV:sv3:inicio -->
(gerado pelo script)
<!-- SV:sv3:fim -->

## 6. SV-4 (janela 0,020) e SV-5 (com a reta)

<!-- SV:sv4_sv5:inicio -->
(gerado pelo script)
<!-- SV:sv4_sv5:fim -->

## 7. Leitura pela regra pré-registrada

<!-- SV:leitura:inicio -->
(gerado pelo script)
<!-- SV:leitura:fim -->

## 8. Figuras

<!-- SV:figuras:inicio -->
(gerado pelo script)
<!-- SV:figuras:fim -->

## 9. Premissa e limites

<!-- SV:limites:inicio -->
(gerado pelo script)
<!-- SV:limites:fim -->
