# 57za. Escolha da 1ª opção com o par de UFs fixado, degrau por degrau (adendo 52h)

> **Gerado por** `scripts/rdd_bolsa/54_VL1_por_corte.py` a partir de `output/rdd_bolsa/VK_*`; não editar à mão (o teste `tests/test_VL1_por_corte.py` confere que este arquivo é igual ao gerado; `--atualizar-doc` o regrava das saídas).<br>
> **Adendo:** [`52h_adendo_VL1_por_corte.md`](52h_adendo_VL1_por_corte.md), congelado em 28/10/2026 antes de rodar (commit `2c8b964`); SHA-256 em `adendo` de `VK_resumo.json`, conferido pelo teste. Especificação de origem: VL-1 do adendo [52e](52e_adendo_escolha_localizacao_par.md), doc [57x](57x_resultados_escolha_localizacao_par.md); por ciclo no [57z](57z_VL1_por_ciclo.md).<br>
> **Estatuto:** `ADENDO_52H_POS_RESULTADO`. O VL-1 já tinha sido visto; isto separa o efeito por corte, não é teste confirmatório novo. Toda linha de `VK_estimativas.csv` e o resumo têm `natureza_dos_dados = EMPIRICO`.<br>
> **Pedido do autor (28/10/2026):** "Faz aí a análise nova p termos ctz" — separar o efeito da bolsa por corte (0,300 e 0,400), comparando vagas da mesma UF.<br>
> **Saídas:** `output/rdd_bolsa/VK_estimativas.csv` e `VK_resumo.json`. `VL_*` e `VG_*` não são regravadas; os docs 57x e 57z não são editados.<br>
> **Auditoria:** pendente. A resposta curta é escolhida por regra fixada no código (`leitura`) no commit das decisões, antes das estimativas.

## 1. Resposta curta

<!-- VK:resposta:inicio -->
**Comparando só vagas da mesma UF, nos ciclos 1–3 (VK-1) o efeito por +R$ 5 mil aparece nos dois cortes, sem diferença detectável entre eles; no ciclo 2 (VK-2), o efeito por +R$ 5 mil aparece nos dois cortes, sem diferença detectável entre eles.**

- **VK-1 (ciclos 1–3):** degrau 0,300, razão de chances 1,41 [1,03; 1,93] (p 0,031, Holm 0,031); degrau 0,400, 1,52 [1,16; 1,99] (p 0,003, Holm 0,008); razão entre eles 0,93 [0,69; 1,26] (p 0,633); 55 conjuntos de escolha. Leitura: `VALE_NOS_DOIS_CORTES` (1ª linha do §4: o efeito por +R$ 5 mil vale nos dois cortes; o efeito linear é adequado). O score bootstrap não confirma a classificação do IC em: 0,300 (com poucos conjuntos, ele merece mais peso).

- **VK-2 (ciclo 2):** degrau 0,300, razão de chances 1,99 [1,38; 2,87] (p < 0,001, Holm < 0,001); degrau 0,400, 1,84 [1,20; 2,82] (p 0,005, Holm 0,010); razão entre eles 1,08 [0,83; 1,40] (p 0,572); 16 conjuntos de escolha. Leitura: `VALE_NOS_DOIS_CORTES` (1ª linha do §4: o efeito por +R$ 5 mil vale nos dois cortes; o efeito linear é adequado).

- **VK-3 (região de saúde, ciclos 1–3):** degrau 0,300, razão de chances 1,42 [1,04; 1,95] (p 0,029); degrau 0,400, 1,54 [1,17; 2,04] (p 0,002); razão entre eles 0,92 [0,69; 1,24] (p 0,587); 55 conjuntos de escolha. Leitura: `VALE_NOS_DOIS_CORTES` (1ª linha do §4: o efeito por +R$ 5 mil vale nos dois cortes; o efeito linear é adequado). *(sensibilidade, fora do Holm)*

- Para comparar, VL-1 (ciclos 1–3) com a bolsa linear: razão de chances por +R$ 5 mil 1,47 [1,15; 1,89].

- Para comparar, VL-1 (ciclo 2) com a bolsa linear: razão de chances por +R$ 5 mil 1,90 [1,30; 2,78].

**Em linguagem simples.** A pergunta do grupo era se o peso da bolsa na escolha vale nos dois cortes de IVS ou só num deles. Aqui cada corte tem o seu peso, e se compara vaga com vaga dentro da mesma UF. Cada degrau é o pacote do corte (bolsa e outras regras federais que mudam no mesmo ponto), não a participação no PMM-E; mede a vaga marcada como 1ª opção na inscrição, não a ida ao município; vale para quem se candidatou, dentro das vagas abertas; e é pós-resultado: o VL-1 já era conhecido antes deste adendo.
<!-- VK:resposta:fim -->

## 2. Portão de reprodução (VK-R)

<!-- VK:portao:inicio -->
**Portão de reprodução (VK-R): PASSOU.** Antes de qualquer conta nova, as funções do script 50 e o portão do script 53, importados sem alteração, reproduzem o VL-1 já gravado. A coluna mostra a maior diferença entre todas as quantidades comparadas da linha (absoluta quando o valor gravado tem módulo até 1, relativa acima disso); a lista completa está em `portao` de `VK_resumo.json`.

| Linha | Dif. máx. | Contagens de identificação iguais | Portão |
|---|---|---|---|
| VL-1, ciclo 2 (bolsa linear, reproduzido) | 3,4e−10 | sim | passou |
| VL-1, ciclos 1–3 (bolsa linear, reproduzido) | 3,2e−10 | sim | passou |

**Degraus conferidos (decisão 2).** Nas 5125 células do conjunto, os degraus do E9 batem com a regra do IVS oficial (bruto e em milésimos) e com bolsa = 10 + 5·degraus: 0 discordâncias. O desenho de VK-1 e VK-2 é o do VL-1: contagens de identificação iguais às de `VL_resumo.json`.
<!-- VK:portao:fim -->

## 3. Quem identifica cada degrau (VK-5)

<!-- VK:identificacao:inicio -->
**Quem identifica cada degrau (VK-5).** O peso de um degrau vem só de candidatos que veem, dentro do mesmo par (UF de origem, UF da vaga), vagas dos dois lados daquele corte: no VK-1 (ciclos 1–3), 5245 candidatos veem vagas dos dois lados de 0,300 e 4968 dos dois lados de 0,400 (de 5417), em 52 e 41 conjuntos de escolha; no VK-2 (ciclo 2), 1931 candidatos veem vagas dos dois lados de 0,300 e 1690 dos dois lados de 0,400 (de 2012), em 16 e 10 conjuntos de escolha.

Colunas: conjuntos de escolha (clusters), pares (origem, UF da vaga), UFs (ou regiões de saúde, no VK-3) de origem e candidatos com o critério em algum par, sobre o total do modelo; e candidatos cuja 1ª opção está num par com o critério. "Faixas vizinhas" separa quem compara vagas com só aquele corte entre elas; quem compara a faixa até 0,300 com a acima de 0,400 passa os dois cortes de uma vez.

| Modelo | Critério | Conjuntos | Pares | Origens | Candidatos | 1ª opção no par |
|---|---|---|---|---|---|---|
| VK-1 (ciclos 1–3) | dois lados de 0,300 | 52 de 55 | 203 de 281 | 27 de 27 | 5245 de 5417 | 2782 |
| VK-1 (ciclos 1–3) | faixas 3 e 2 (só 0,300) | 52 de 55 | 198 de 281 | 26 de 27 | 5213 de 5417 | 2598 |
| VK-1 (ciclos 1–3) | dois lados de 0,400 | 41 de 55 | 206 de 281 | 27 de 27 | 4968 de 5417 | 3011 |
| VK-1 (ciclos 1–3) | faixas 2 e 1 (só 0,400) | 38 de 55 | 201 de 281 | 27 de 27 | 4850 de 5417 | 2827 |
| VK-1 (ciclos 1–3) | as três faixas | 32 de 55 | 144 de 281 | 26 de 27 | 4273 de 5417 | 1672 |
| VK-2 (ciclo 2) | dois lados de 0,300 | 16 de 16 | 119 de 169 | 26 de 27 | 1931 de 2012 | 1322 |
| VK-2 (ciclo 2) | faixas 3 e 2 (só 0,300) | 16 de 16 | 117 de 169 | 26 de 27 | 1930 de 2012 | 1296 |
| VK-2 (ciclo 2) | dois lados de 0,400 | 10 de 16 | 111 de 169 | 25 de 27 | 1690 de 2012 | 1097 |
| VK-2 (ciclo 2) | faixas 2 e 1 (só 0,400) | 10 de 16 | 109 de 169 | 25 de 27 | 1676 de 2012 | 1071 |
| VK-2 (ciclo 2) | as três faixas | 9 de 16 | 77 de 169 | 24 de 27 | 1616 de 2012 | 884 |
| VK-3 (região de saúde, ciclos 1–3) | dois lados de 0,300 | 52 de 55 | 574 de 787 | 269 de 316 | 4836 de 5360 | 2782 |
| VK-3 (região de saúde, ciclos 1–3) | faixas 3 e 2 (só 0,300) | 52 de 55 | 561 de 787 | 263 de 316 | 4761 de 5360 | 2598 |
| VK-3 (região de saúde, ciclos 1–3) | dois lados de 0,400 | 41 de 55 | 540 de 787 | 234 de 316 | 4488 de 5360 | 3011 |
| VK-3 (região de saúde, ciclos 1–3) | faixas 2 e 1 (só 0,400) | 38 de 55 | 529 de 787 | 231 de 316 | 4373 de 5360 | 2827 |
| VK-3 (região de saúde, ciclos 1–3) | as três faixas | 32 de 55 | 408 de 787 | 209 de 316 | 3647 de 5360 | 1672 |
<!-- VK:identificacao:fim -->

## 4. Resultados

### 4.1 Razão de chances por degrau (VK-1, VK-2, VK-3)

<!-- VK:principais:inicio -->
Razão de chances da 1ª opção por degrau de bolsa (+R$ 5 mil no corte), comparando só vagas da mesma UF vistas por médicos da mesma UF de origem (no VK-3, da mesma região de saúde de origem), com o IVS em spline contínua. IC 95% e p (H0: δ = 0) com cluster por conjunto de escolha (curso × ciclo); p com t de G − 1; p do score bootstrap (Kline–Santos, Rademacher), que pesa mais quando G é pequeno; Holm nos quatro degraus de VK-1 e VK-2 (decisão 4). As linhas do VL-1 são as do 57x, reproduzidas pelo portão, para comparar.

| Modelo | Termo | Candidatos | Conjuntos (G) | RC [IC 95%] | p | p (t, G − 1) | p score (Rademacher) | p Holm | p Holm (score) |
|---|---|---|---|---|---|---|---|---|---|
| VK-1 (ciclos 1–3) | degrau 0,300 | 5417 | 55 | 1,41 [1,03; 1,93] | 0,031 | 0,036 | 0,064 | 0,031 | 0,098 |
| VK-1 (ciclos 1–3) | degrau 0,400 | 5417 | 55 | 1,52 [1,16; 1,99] | 0,003 | 0,004 | 0,015 | 0,008 | 0,046 |
| VL-1 (ciclos 1–3) | bolsa linear (+R$ 5 mil) | 5417 | 55 | 1,47 [1,15; 1,89] | 0,002 | 0,004 | 0,011 | — | — |
| VK-2 (ciclo 2) | degrau 0,300 | 2012 | 16 | 1,99 [1,38; 2,87] | < 0,001 | 0,002 | 0,005 | < 0,001 | 0,021 |
| VK-2 (ciclo 2) | degrau 0,400 | 2012 | 16 | 1,84 [1,20; 2,82] | 0,005 | 0,013 | 0,049 | 0,010 | 0,098 |
| VL-1 (ciclo 2) | bolsa linear (+R$ 5 mil) | 2012 | 16 | 1,90 [1,30; 2,78] | < 0,001 | 0,005 | 0,004 | — | — |
| VK-3 (região de saúde, ciclos 1–3) | degrau 0,300 | 5360 | 55 | 1,42 [1,04; 1,95] | 0,029 | 0,033 | — | — | — |
| VK-3 (região de saúde, ciclos 1–3) | degrau 0,400 | 5360 | 55 | 1,54 [1,17; 2,04] | 0,002 | 0,003 | — | — | — |
<!-- VK:principais:fim -->

### 4.2 Teste de igualdade dos degraus (VK-D)

<!-- VK:igualdade:inicio -->
VK-D: razão das razões de chances, RC(0,300) ÷ RC(0,400) = exp(δ300 − δ400). Igual a 1 quer dizer o mesmo efeito nos dois cortes (o VL-1). Wald com cluster por conjunto (qui-quadrado com 1 gl); p com t de G − 1; p do score bootstrap da igualdade (decisão 5, descritivo).

| Modelo | Razão [IC 95%] | Wald (χ², 1 gl) | p | p (t, G − 1) | p score (Rademacher) | Conjuntos (G) |
|---|---|---|---|---|---|---|
| VK-1 (ciclos 1–3) | 0,93 [0,69; 1,26] | 0,23 | 0,633 | 0,635 | 0,635 | 55 |
| VK-2 (ciclo 2) | 1,08 [0,83; 1,40] | 0,32 | 0,572 | 0,580 | 0,585 | 16 |
| VK-3 (região de saúde, ciclos 1–3) | 0,92 [0,69; 1,24] | 0,30 | 0,587 | 0,589 | — | 55 |
<!-- VK:igualdade:fim -->

### 4.3 Os outros pesos do modelo

<!-- VK:controles:inicio -->
Os coeficientes que não são indicadores de par (log-chance; IC 95% com cluster por conjunto). "—" é termo omitido. Todas as linhas estão em `VK_estimativas.csv`.

| Termo | VK-1 (ciclos 1–3) | VK-2 (ciclo 2) | VK-3 (região de saúde, ciclos 1–3) |
|---|---|---|---|
| `degrau_0300` | 0,345 [0,031; 0,658] | 0,687 [0,321; 1,054] | 0,352 [0,037; 0,667] |
| `degrau_0400` | 0,418 [0,146; 0,690] | 0,611 [0,185; 1,037] | 0,434 [0,156; 0,712] |
| `ivs_inclinacao` | −0,139 [−0,460; 0,183] | −0,491 [−0,816; −0,166] | −0,114 [−0,432; 0,204] |
| `ivs_mudanca_inclinacao_0300` | 0,404 [−0,009; 0,818] | 0,939 [0,253; 1,625] | 0,376 [−0,036; 0,787] |
| `ivs_mudanca_inclinacao_0400` | −0,445 [−0,758; −0,131] | −0,580 [−1,211; 0,051] | −0,433 [−0,752; −0,114] |
| `tem_vaga_imediata` | 0,255 [0,044; 0,466] | 0,472 [0,185; 0,759] | 0,281 [0,062; 0,501] |
| `log_vagas_imediatas_mais_1` | 0,488 [0,241; 0,736] | 0,601 [0,326; 0,876] | 0,473 [0,213; 0,733] |
| `log_populacao_2022` | 0,139 [0,082; 0,197] | 0,102 [0,013; 0,190] | 0,159 [0,099; 0,219] |
| `capital` | −0,314 [−0,655; 0,026] | 0,111 [−0,418; 0,639] | −0,361 [−0,729; 0,007] |
| `estrato_interior_remoto` | −0,189 [−0,379; 0,000] | −0,377 [−0,621; −0,134] | −0,177 [−0,361; 0,006] |
| `estrato_metropolitano` | 0,105 [−0,047; 0,256] | 0,205 [−0,006; 0,415] | 0,120 [−0,026; 0,265] |
| `distancia_100km` | −0,515 [−0,555; −0,474] | −0,552 [−0,645; −0,460] | −0,585 [−0,639; −0,531] |
| `mesma_regiao_saude` | 1,099 [0,845; 1,353] | 0,929 [0,695; 1,163] | 1,023 [0,752; 1,293] |
| `mesmo_municipio` | 0,590 [0,321; 0,859] | 0,788 [0,310; 1,267] | 0,573 [0,305; 0,841] |
<!-- VK:controles:fim -->

## 5. Leitura do §4 por regra

<!-- VK:leitura:inicio -->
Regra fixada no código antes de rodar (decisão 8). Sinal de referência: o do VL-1 reproduzido na mesma amostra. Leitura geral: VK-1 `VALE_NOS_DOIS_CORTES`; VK-2 `VALE_NOS_DOIS_CORTES`; VK-3 é descritivo.

| Modelo | Degrau 0,300 | Degrau 0,400 | IC da razão contém 1 | Regra | Score concorda (0,300 / 0,400 / razão) |
|---|---|---|---|---|---|
| VK-1 (ciclos 1–3) | `EXCLUI_1_MESMO_LADO` | `EXCLUI_1_MESMO_LADO` | sim | `VALE_NOS_DOIS_CORTES` | **não** / sim / sim |
| VK-2 (ciclo 2) | `EXCLUI_1_MESMO_LADO` | `EXCLUI_1_MESMO_LADO` | sim | `VALE_NOS_DOIS_CORTES` | sim / sim / sim |
| VK-3 (região de saúde, ciclos 1–3) | `EXCLUI_1_MESMO_LADO` | `EXCLUI_1_MESMO_LADO` | sim | `VALE_NOS_DOIS_CORTES` | — / — / — |
<!-- VK:leitura:fim -->

## 6. Decisões de implementação

<!-- VK:decisoes:inicio -->
Decisões de implementação onde o adendo não fixava o detalhe. Foram registradas e commitadas antes de qualquer estimativa deste adendo (o histórico do Git mostra o commit deste bloco antes do commit dos números). As 13 decisões do 57x e as do 57z continuam valendo; em qualquer ambiguidade nova, vale a leitura mais próxima do script 50.

1. **O que é o VK** (28/10/2026). O §2 pede o VL-1 com `bolsa_mil` trocada por dois degraus e o resto idêntico. *Resolução:* Desenho, amostra e efeito fixo são os do 50, sem alteração: `subconjunto` (VK-1 e VK-3: ciclos 1–3; VK-2: ciclo 2), `montar_desenho` do 25 e `desenho_ef` do 50 (indicadores de par menos uma base por componente, retirada de pares sem escolha e de efeitos fixos separados, candidato com uma só alternativa sai). Como o desenho não depende da coluna da bolsa, o de VK-1 e VK-2 é o mesmo do VL-1 (conferido pelas contagens de identificação, iguais às de `VL_resumo.json`). A matriz é a `matriz_vl` do 50 (M1 com distância linear por 100 km, sem `mesma_uf` e sem macrorregiões, com o spline do IVS com mudança de inclinação em 0,300 e 0,400) com a coluna `bolsa_mil` substituída, na mesma posição, por `degrau_0300` e `degrau_0400`. Estimação pela `estimar_ef` do 50 (mesma partida do Newton). No logit condicional, a constante 10 some; o VL-1 é o VK com δ300 = δ400 = 5β. Nada é reescrito: o script 54 importa o 53, e por ele o 50.
2. **Codificação dos degraus** (28/10/2026). O pedido manda reusar uma codificação de degraus já existente; o E9 (script 16) tem uma, usada no doc 42 e no 52f. *Resolução:* Reusa-se `termos_bolsa(conj, "degraus")` do script 16: `degrau_0300` = faixa impressa 2 ou 1, `degrau_0400` = faixa impressa 1. Antes de estimar, confere-se em todas as células do conjunto do P1 corrigido: (a) `degrau_0300` = 1[IVS oficial > 0,300] e `degrau_0400` = 1[IVS oficial > 0,400], com o IVS do a08 tanto bruto quanto em milésimos arredondados (`s_mil`, como no E9); (b) `bolsa_mil` = 10 + 5·`degrau_0300` + 5·`degrau_0400`; (c) em cada matriz, a coluna da bolsa que sai é exatamente essa combinação. Qualquer discordância para a execução (`FalhaValidacao`). As contagens vão ao resumo.
3. **Portão VK-R** (28/10/2026). O §2 pede reproduzir o VL-1 dos ciclos 1–3 e do ciclo 2 com tolerância ≤ 1e−8 antes de qualquer conta nova. *Resolução:* Como no 52g, com as funções dele: `estimar_linha` do 50 (chaves `VL1_c2` e `VL1_emp`), linhas no formato do 53 (`linhas_modelo`) e a função `portao` do 53, que compara coeficientes fora dos pares com os três EP, a razão de chances (estimativa, EP, IC, p, p com t de G − 1, p de MV, score bootstrap Rademacher e Webb), K5 e K10, G e candidatos, contra `VL_estimativas.csv`, e as contagens de identificação e o score bootstrap contra `VL_resumo.json` (diferença absoluta ≤ 1e−8 se o valor gravado tem módulo até 1, relativa se maior; NaN só casa com NaN). Falhou, a execução para em `FALHA_REPRODUCAO_<linha>`, nada novo é estimado e só o resumo do portão é gravado.
4. **Inferência, score bootstrap e Holm** (28/10/2026). O §3 pede inferência como no 52e, score bootstrap de Rademacher por degrau se o 50 permitir para um termo arbitrário, e Holm nos quatro degraus principais. *Resolução:* Sanduíche CR1 por conjunto de escolha (curso × ciclo), fator G/(G − 1), IC 95% e p pela normal; p com t de G − 1 também. A `score_bootstrap` do 50 tem o parâmetro `termo`: o ajuste restrito tira só a coluna daquele degrau (o outro degrau fica livre) e parte da estimativa irrestrita sem ela; Rademacher por enumeração completa se G ≤ 24, senão 199.999 sorteios com a semente do 16; Webb também. Calcula-se para cada degrau de VK-1 e VK-2. No VK-3 não (como o VL-3 no 50, que não tem score; o ajuste restrito com o efeito fixo de região de saúde é o mais caro). Holm nos quatro degraus de VK-1 e VK-2 com o p por cluster; Holm nos p do score bootstrap como coluna de robustez. Razão de chances de um degrau = exp(δ) (um degrau = +R$ 5 mil), IC = exp do IC de δ.
5. **Teste de igualdade (VK-D)** (28/10/2026). O §2 pede Wald com cluster por conjunto e a razão das razões de chances com IC. *Resolução:* d = δ300 − δ400, EP CR1 de a'V a com a = (+1, −1); Wald z = d/EP (qui-quadrado 1 gl = z²), p pela normal e com t de G − 1; razão das razões de chances exp(d), IC 95% exp(d ± 1,96·EP). Como robustez descritiva, fora da regra de leitura e do Holm: score bootstrap da igualdade por reparametrização exata (colunas `degrau_0300` e `degrau_0300 + degrau_0400`; o coeficiente da primeira é d, e o modelo restrito d = 0 é o VL-1), com a mesma `score_bootstrap` do 50, em VK-1 e VK-2.
6. **VK-3** (28/10/2026). O §2 pede VK-1 com efeito fixo de região de saúde de origem × UF da vaga, como o VL-3. *Resolução:* Desenho e matriz do `VL3_VL1_emp` do 50 (região de saúde de origem × UF da vaga, ciclos 1–3) com os degraus no lugar da bolsa. Sensibilidade: fora do Holm, sem score bootstrap (decisão 4); a regra de leitura é aplicada como descrição, sem entrar na leitura geral.
7. **Quem identifica cada degrau (VK-5)** (28/10/2026). O §2 pede quantos conjuntos, pares de UF e candidatos têm vagas dos dois lados de cada corte dentro da mesma UF. *Resolução:* No desenho final de cada VK (depois da retirada de pares sem escolha), por candidato e par (origem, UF da vaga): dos dois lados de 0,300 = vê no par vaga com IVS ≤ 0,300 e vaga com IVS > 0,300; dos dois lados de 0,400 = vaga com IVS ≤ 0,400 e vaga com IVS > 0,400. Contam-se, por corte: candidatos com isso em algum par, candidatos com a 1ª opção num par assim, pares (origem, UF da vaga) com algum candidato assim, UFs de origem e conjuntos de escolha (G) com algum candidato assim. Como a faixa acima de 0,400 também passa 0,300, conta-se à parte quem vê faixas vizinhas no mesmo par (só aquele corte entre elas: faixas 3 e 2 para 0,300; 2 e 1 para 0,400), e quem vê as três faixas. Junto, as contagens do `desenho_ef` do 50 (as da seção 3 do 57x).
8. **Leitura do §4 por regra** (28/10/2026). A tabela do §4 tem linhas que se sobrepõem (por exemplo, dois degraus com RC > 1, um com IC que exclui 1) e não diz contra que sinal se lê "sinal oposto". *Resolução:* Para cada degrau: `EXCLUI_1_MESMO_LADO`, `EXCLUI_1_LADO_OPOSTO` (lado contra o do VL-1 reproduzido na mesma amostra: ciclos 1–3 para VK-1 e VK-3, ciclo 2 para VK-2) ou `CONTEM_1`. Para cada modelo, nesta ordem: algum degrau `EXCLUI_1_LADO_OPOSTO` → `SINAL_OPOSTO` (4ª linha); senão, IC da razão das razões de chances que exclui 1 → `DIFERE_ENTRE_CORTES` (3ª linha, com o corte de RC maior); senão, exatamente um degrau `EXCLUI_1_MESMO_LADO` → `APARECE_NUM_CORTE` (2ª linha, com o corte); senão, os dois degraus com RC > 1 → `VALE_NOS_DOIS_CORTES` (1ª linha), e, se nenhum dos dois IC exclui 1, o doc diz que nenhum degrau, sozinho, se distingue de 1; senão → `FORA_DA_TABELA` (relatado linha a linha); sem estimativa → `SEM_ESTIMATIVA`. A 2ª linha vem antes da 1ª porque dizer que vale nos dois cortes com um IC contendo 1 seria dizer mais do que o dado mostra. Leitura geral: a de VK-1 e a de VK-2, lado a lado; VK-3 é descritivo. Peso ao score: por degrau, `score_concorda` = (p do score Rademacher < 0,05) igual a (IC exclui 1); quando não concorda, o doc diz; a regra não muda.
9. **Falha de convergência** (28/10/2026). Com dois degraus no lugar de uma coluna, a matriz pode perder posto num desenho com pouca variação. *Resolução:* Como no 50: a linha fica `NAO_CONVERGIU` com a nota da `estimar_ef`, sem trocar partida, especificação ou amostra; a leitura dela é `SEM_ESTIMATIVA`.
10. **Saídas** (28/10/2026). O §5 lista script, `VK_estimativas.csv`, `VK_resumo.json`, doc 57za e testes; não lista figura nem km. *Resolução:* Não há figura nem km equivalentes. O CSV tem, por modelo VK: os coeficientes fora dos indicadores de par, a razão de chances de cada degrau e a razão das razões de chances (VK-D); e a razão de chances por +R$ 5 mil do VL-1 reproduzido (`papel = reproducao_VK-R`). `VL_*` e `VG_*` não são regravadas (hash conferido antes e depois).
11. **Números do doc 57za** (28/10/2026). O pedido exige números só em blocos gerados. *Resolução:* Todo número de resultado do 57za vem de `VK_*` por `--atualizar-doc`, entre marcadores `<!-- VK:... -->`; o teste confere o doc contra o gerado e que não há número de resultado fora dos blocos. A resposta curta é escolhida por regra (`leitura`), sem texto escrito depois de ver os números.
<!-- VK:decisoes:fim -->

## 7. Limites

- **Pós-resultado.** O VL-1 empilhado, o do ciclo 2 e o por ciclo já eram conhecidos. O adendo foi congelado antes de rodar, mas separar por corte depois de ver o efeito linear não é teste confirmatório novo.
- **Pacote do corte.** Cada degrau é identificado pelo salto no seu corte de IVS, com o IVS em spline contínua; nos mesmos cortes mudam outras regras federais (auditoria 18). Não é efeito da participação no PMM-E nem do Agora Tem Especialistas.
- **Identificação estreita.** O peso de cada degrau vem só de candidatos que veem, na mesma UF, vagas dos dois lados daquele corte (seção 3); quem compara a faixa até 0,300 com a acima de 0,400 passa os dois cortes de uma vez, e o modelo separa os degraus pela faixa do meio e pelo spline.
- **Poucos conjuntos.** O cluster é o conjunto de escolha (curso × ciclo); no ciclo 2 são poucos. O IC com cluster pode ser otimista; por isso o score bootstrap vai ao lado.
- **Escolha condicional.** Tudo vale para quem se candidatou, dentro das vagas abertas do seu curso e ciclo, e mede a vaga marcada como 1ª opção, não a ida ao município; IIA do logit condicional.
- **Origem não é causal.** A origem é o município do vínculo médico no CNES (G1), não a residência; o peso da origem é preferência revelada, não efeito causal.
