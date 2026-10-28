# 57z. Escolha da 1ª opção com o par de UFs fixado, ciclo a ciclo (adendo 52g)

> **Gerado por** `scripts/rdd_bolsa/53_VL1_por_ciclo.py` a partir de `output/rdd_bolsa/VG_*`; não editar à mão (o teste `tests/test_VL1_por_ciclo.py` confere que este arquivo é igual ao gerado; `--atualizar-doc` o regrava das saídas).<br>
> **Adendo:** [`52g_adendo_VL1_por_ciclo.md`](52g_adendo_VL1_por_ciclo.md), congelado em 28/10/2026 antes de rodar (commit `e9740a5`); SHA-256 em `adendo` de `VG_resumo.json`, conferido pelo teste. Especificação de origem: VL-1 do adendo [52e](52e_adendo_escolha_localizacao_par.md), doc [57x](57x_resultados_escolha_localizacao_par.md), com as 13 decisões de implementação de lá.<br>
> **Estatuto:** `ADENDO_52G_POS_RESULTADO`. O VL-1 dos ciclos 1–3 e do ciclo 2 já tinha sido visto; isto é robustez por ciclo, não teste confirmatório novo. Toda linha de `VG_estimativas.csv` e o resumo têm `natureza_dos_dados = EMPIRICO`.<br>
> **Decisão do autor (28/10/2026):** "a hipótese é simplesmente sobre o efeito bolsa → 1ª opção", com "só comparação entre municípios da mesma UF".<br>
> **Saídas:** `output/rdd_bolsa/VG_estimativas.csv` e `VG_resumo.json`. As saídas `VL_*` não são regravadas, e o doc 57x não é editado.<br>
> **Auditoria:** pendente. A resposta curta é escolhida por regra fixada no código (`leitura`) no commit das decisões, antes das estimativas.

## 1. Resposta curta

<!-- VG:resposta:inicio -->
**Comparando só vagas da mesma UF, o peso da bolsa na escolha da 1ª opção é forte só no ciclo 2.** Nos ciclos 1 e 3, separados, o IC da razão de chances contém 1 (1ª linha do §2 do adendo, como na especificação base).

- **Ciclo 1:** razão de chances 1,15 [0,66; 2,01], p 0,628, p do score bootstrap 0,635, com 16 conjuntos de escolha; IC que contém 1.

- **Ciclo 2:** razão de chances 1,90 [1,30; 2,78], p < 0,001, p do score bootstrap 0,004, com 16 conjuntos de escolha (VL-1 do 57x, reproduzido).

- **Ciclo 3:** razão de chances 1,25 [0,90; 1,73], p 0,184, p do score bootstrap 0,363, com 23 conjuntos de escolha; IC que contém 1.

- **Ciclos 1–3:** razão de chances 1,47 [1,15; 1,89], p 0,002, p do score bootstrap 0,011, com 55 conjuntos de escolha (VL-1 do 57x, reproduzido).

**km (VG-4).** Comparando vagas da mesma UF, +R$ 5 mil pesam como 24 km no ciclo 1 (IC delta [−73; 121]), com IC do β que contém zero: o IC dos km também contém zero e o número é instável; e 46 km no ciclo 3 (IC delta [−23; 114]), com IC do β que contém zero: o IC dos km também contém zero e o número é instável. No ciclo 2, 117 km.

**Em linguagem simples.** A pergunta era se o que se vê no ciclo 2 (o candidato escolhe mais a vaga com bolsa maior, mesmo comparando só vagas da mesma UF) também aparece nos ciclos 1 e 3, olhados um de cada vez. Cada ciclo tem poucos cursos, e o cluster é o curso: por isso o número de conjuntos vai ao lado de cada linha e o score bootstrap pesa. A bolsa aqui é o pacote do corte de IVS (bolsa e outras regras federais que mudam nos mesmos cortes), não a participação no PMM-E; a origem do candidato é preferência revelada, não efeito causal; e tudo vale para quem se candidatou, dentro das vagas abertas.
<!-- VG:resposta:fim -->

## 2. Portão de reprodução (VG-R)

<!-- VG:portao:inicio -->
**Portão de reprodução (VG-R): PASSOU.** Antes de qualquer conta nova, as funções do script 50, importadas sem alteração, reproduzem o VL-1 já gravado. A coluna mostra a maior diferença entre todas as quantidades comparadas da linha (absoluta quando o valor gravado tem módulo até 1, relativa acima disso); a lista completa está em `portao` de `VG_resumo.json`.

| Linha | Dif. máx. | Contagens de identificação iguais | Portão |
|---|---|---|---|
| VL-1 no ciclo 2 (reproduzido) | 3,4e−10 | sim | passou |
| VL-1 nos ciclos 1–3 (reproduzido) | 3,2e−10 | sim | passou |
<!-- VG:portao:fim -->

## 3. Quem identifica em cada ciclo (VG-5)

<!-- VG:identificacao:inicio -->
**Quem identifica o peso da bolsa em cada ciclo (VG-5).** O peso vem só de candidatos que veem, dentro de uma mesma UF, vagas com bolsas diferentes: no ciclo 1, 127 pares (UF de origem, UF da vaga) com bolsas diferentes, 869 dos 890 candidatos do modelo veem essa variação e 16 conjuntos de escolha (cursos); no ciclo 3, 167 pares (UF de origem, UF da vaga) com bolsas diferentes, 2345 dos 2464 candidatos do modelo veem essa variação e 23 conjuntos de escolha (cursos).

Colunas: G = conjuntos de escolha (clusters); pares no desenho → pares que ficam no modelo (os sem escolha saem, decisão 2 do 57x); pares com variação de bolsa; UFs de origem com algum par com variação; alternativas retiradas por par sem escolha + por separação; candidatos retirados por ficarem com uma só alternativa; candidatos no modelo; candidatos com variação de bolsa dentro de algum par; candidatos com a 1ª opção num par com variação; colunas de efeito fixo.

| Ciclo | G | Pares (desenho → modelo) | Pares com variação | Origens com variação | Alternativas retiradas | Candidatos retirados | Candidatos no modelo | Candidatos com variação | 1ª opção em par com variação | Colunas de efeito fixo |
|---|---|---|---|---|---|---|---|---|---|---|
| ciclo 1 | 16 | 713 → 140 | 127 | 27 de 27 | 45926 + 227 de 80522 | 25 | 890 | 869 | 660 | 111 |
| ciclo 2 | 16 | 729 → 169 | 151 | 27 de 27 | 206094 + 297 de 380022 | 20 | 2012 | 1956 | 1509 | 140 |
| ciclo 3 | 23 | 701 → 185 | 167 | 26 de 27 | 242108 + 318 de 472033 | 10 | 2464 | 2345 | 1768 | 155 |
| ciclos 1–3 | 55 | 729 → 281 | 260 | 27 de 27 | 353575 + 0 de 932577 | 4 | 5417 | 5345 | 3937 | 254 |
<!-- VG:identificacao:fim -->

## 4. Resultados

### 4.1 Razão de chances por ciclo (VG-1 e VG-3)

<!-- VG:principais:inicio -->
Razão de chances da 1ª opção por +R$ 5 mil de bolsa, comparando só vagas da mesma UF vistas por médicos da mesma UF de origem. IC 95% e p (H0: β = 0) com cluster por conjunto de escolha (curso × ciclo); p com t de G − 1; p do score bootstrap (Kline–Santos, Rademacher e Webb), que pesa mais quando G é pequeno; Holm descritivo nas duas linhas novas (decisão 4). As linhas do ciclo 2 e dos ciclos 1–3 são o VL-1 do 57x, reproduzido pelo portão.

| Linha | Candidatos | Conjuntos (G) | RC [IC 95%] | p | p (t, G − 1) | p score (Rademacher) | p score (Webb) | Score: método | p Holm | p Holm (score) |
|---|---|---|---|---|---|---|---|---|---|---|
| VG-1: VL-1 no ciclo 1 | 890 | 16 | 1,15 [0,66; 2,01] | 0,628 | 0,635 | 0,635 | 0,645 | enumeração completa dos 2^G sinais | 0,628 | 0,726 |
| VL-1 no ciclo 2 (reproduzido) | 2012 | 16 | 1,90 [1,30; 2,78] | < 0,001 | 0,005 | 0,004 | 0,011 | enumeração completa dos 2^G sinais | — | — |
| VG-3: VL-1 no ciclo 3 | 2464 | 23 | 1,25 [0,90; 1,73] | 0,184 | 0,197 | 0,363 | 0,359 | enumeração completa dos 2^G sinais | 0,367 | 0,726 |
| VL-1 nos ciclos 1–3 (reproduzido) | 5417 | 55 | 1,47 [1,15; 1,89] | 0,002 | 0,004 | 0,011 | 0,011 | 199999 sorteios, semente 20261018 | — | — |
<!-- VG:principais:fim -->

### 4.2 km equivalentes (VG-4)

<!-- VG:km:inicio -->
VG-4: quantos km a menos de distância origem–vaga pesam na escolha como +R$ 5 mil (K5) ou +R$ 10 mil (K10), comparando vagas da mesma UF: 100 · passo · β / (−γ), com γ o peso da distância por 100 km. IC pelo método delta e por Fieller; descritivo, sem teste. Fieller com limite infinito quer dizer que o IC do β contém zero.

| Linha | Passo | km equivalentes | IC 95% (delta) | IC 95% (Fieller) |
|---|---|---|---|---|
| VG-1: VL-1 no ciclo 1 | K5 | 24 km | [−73; 121] | [−68; 127] |
| VG-1: VL-1 no ciclo 1 | K10 | 47 km | [−147; 241] | [−137; 254] |
| VL-1 no ciclo 2 (reproduzido) | K5 | 117 km | [56; 178] | [52; 176] |
| VL-1 no ciclo 2 (reproduzido) | K10 | 233 km | [111; 355] | [104; 352] |
| VG-3: VL-1 no ciclo 3 | K5 | 46 km | [−23; 114] | [−22; 116] |
| VG-3: VL-1 no ciclo 3 | K10 | 92 km | [−45; 229] | [−43; 232] |
| VL-1 nos ciclos 1–3 (reproduzido) | K5 | 75 km | [28; 122] | [27; 122] |
| VL-1 nos ciclos 1–3 (reproduzido) | K10 | 150 km | [55; 244] | [54; 243] |
<!-- VG:km:fim -->

### 4.3 Os outros pesos do modelo

<!-- VG:controles:inicio -->
Os coeficientes que não são indicadores de par (log-chance; IC 95% com cluster por conjunto). "—" é termo omitido por não variar dentro de nenhum candidato naquele ciclo. Todas as linhas estão em `VG_estimativas.csv`.

| Termo | ciclo 1 | ciclo 2 | ciclo 3 | ciclos 1–3 |
|---|---|---|---|---|
| `bolsa_mil` | 0,028 [−0,084; 0,140] | 0,129 [0,053; 0,205] | 0,044 [−0,021; 0,110] | 0,077 [0,027; 0,127] |
| `ivs_inclinacao` | −0,432 [−1,012; 0,147] | −0,461 [−0,757; −0,165] | 0,042 [−0,353; 0,437] | −0,170 [−0,410; 0,071] |
| `ivs_mudanca_inclinacao_0300` | 0,722 [−0,430; 1,874] | 0,917 [0,247; 1,587] | 0,350 [−0,004; 0,703] | 0,435 [0,085; 0,786] |
| `ivs_mudanca_inclinacao_0400` | −0,198 [−1,178; 0,783] | −0,606 [−1,238; 0,025] | −0,575 [−0,879; −0,271] | −0,426 [−0,724; −0,128] |
| `tem_vaga_imediata` | 0,239 [−0,386; 0,865] | 0,471 [0,183; 0,759] | 0,248 [−0,147; 0,643] | 0,254 [0,043; 0,465] |
| `log_vagas_imediatas_mais_1` | 0,328 [−0,236; 0,892] | 0,600 [0,323; 0,877] | 0,355 [0,012; 0,698] | 0,491 [0,247; 0,734] |
| `log_populacao_2022` | 0,421 [0,287; 0,554] | 0,103 [0,015; 0,191] | 0,186 [0,133; 0,239] | 0,140 [0,081; 0,198] |
| `capital` | 0,635 [−0,039; 1,309] | 0,108 [−0,421; 0,638] | −0,634 [−0,955; −0,313] | −0,313 [−0,654; 0,028] |
| `estrato_interior_remoto` | 0,244 [−0,094; 0,582] | −0,375 [−0,612; −0,138] | −0,232 [−0,490; 0,027] | −0,188 [−0,379; 0,003] |
| `estrato_metropolitano` | 0,432 [0,223; 0,641] | 0,208 [−0,005; 0,421] | −0,113 [−0,339; 0,114] | 0,104 [−0,050; 0,258] |
| `distancia_100km` | −0,586 [−0,654; −0,517] | −0,553 [−0,644; −0,461] | −0,482 [−0,530; −0,433] | −0,514 [−0,555; −0,474] |
| `mesma_regiao_saude` | 1,590 [1,107; 2,073] | 0,924 [0,687; 1,162] | 1,332 [1,028; 1,636] | 1,103 [0,845; 1,361] |
| `mesmo_municipio` | 0,550 [−0,280; 1,379] | 0,790 [0,308; 1,272] | 0,495 [0,192; 0,797] | 0,587 [0,314; 0,860] |
<!-- VG:controles:fim -->

## 5. Leitura do §2 por regra

<!-- VG:leitura:inicio -->
Regra fixada no código antes de rodar (decisão 5). Sinal de referência: o do VL-1 do ciclo 2. Leitura geral: `FORTE_SO_NO_CICLO_2`.

| Linha | Regra | IC contém 1 | Score bootstrap concorda | Conjuntos (G) |
|---|---|---|---|---|
| VG-1: VL-1 no ciclo 1 | `IC_CONTEM_1` | sim | sim | 16 |
| VG-3: VL-1 no ciclo 3 | `IC_CONTEM_1` | sim | sim | 23 |
<!-- VG:leitura:fim -->

## 6. Decisões de implementação

<!-- VG:decisoes:inicio -->
Decisões de implementação onde o adendo não fixava o detalhe. Foram registradas e commitadas antes de qualquer estimativa deste adendo (o histórico do Git mostra o commit deste bloco antes do commit dos números). As 13 decisões do 57x continuam valendo; em qualquer ambiguidade nova, vale a leitura mais próxima do script 50.

1. **O que é o VL-1 num ciclo** (28/10/2026). O §1 manda rodar "exatamente o VL-1 do 52e" em cada ciclo separado. *Resolução:* VG-1 e VG-3 são a especificação `VL1_c2` do script 50 com o ciclo trocado para 1 e 3: a amostra é a do P1 restrita ao ciclo (função `subconjunto` do 50, como o M5 do script 25); o efeito fixo de UF de origem × UF da vaga é montado só com os candidatos e as vagas daquele ciclo (`desenho_ef` do 50, com as decisões 1 a 3 do 57x: indicadores de par menos uma base por componente, retirada de pares sem escolha e de efeitos fixos separados até não mudar, candidato com uma só alternativa sai); a matriz é a do 50 (`matriz_vl`: M1 com distância linear por 100 km, sem `mesma_uf` e sem macrorregiões); a estimação é a `estimar_ef` do 50 (mesmo ponto de partida do Newton, nota de execução 1 do 57x). Nada é reescrito: o script 53 importa o 50.
2. **Tipo de vaga nos ciclos 1 e 3** (28/10/2026). O 52e usa o conjunto do P1 com o tipo de vaga do ciclo 2 pelo quadro de 13/02/2026 (função `corrigir` do 42). *Resolução:* Usa-se o mesmo conjunto corrigido. A correção só muda células do ciclo 2; nos ciclos 1 e 3 o conjunto é o do P1. O resumo grava a contagem de células por ciclo para conferência.
3. **Portão VG-R** (28/10/2026). O §1 pede reproduzir o VL-1 do ciclo 2 e dos ciclos 1–3 com diferença ≤ 1e−8 antes do resto. *Resolução:* Antes de qualquer conta nova, `estimar_linha` do 50 (sem alteração, com as chaves `VL1_c2` e `VL1_emp`) reestima as duas linhas. Compara-se com `VL_estimativas.csv`: todos os coeficientes que não são indicadores de par, com os três EP (mesmos termos, na mesma ordem); a razão de chances (estimativa, três EP, IC, p, p com t de G − 1, p de MV, p do score bootstrap Rademacher e Webb); K5 e K10 (estimativa, três EP, IC delta e Fieller); e G de conjuntos e de candidatos e o número de candidatos. Compara-se com `VL_resumo.json`: as contagens de identificação (iguais) e o resultado do score bootstrap. Diferença absoluta ≤ 1e−8 se o valor gravado tem módulo até 1, relativa se maior; NaN só casa com NaN (`_dif_rel` do 50, decisão 12 do 57x). Falhou, a execução para em `FALHA_REPRODUCAO_<linha>`, nada novo é estimado e só o resumo do portão é gravado. O portão VL-5 do 50 (M1, P1h e M4) não é refeito: o VG-R é o portão que o 52g pede.
4. **Inferência e poucos clusters** (28/10/2026). O §1 pede inferência como no 52e e, com poucos conjuntos num ciclo, relatar o número de clusters e dar peso ao score bootstrap. O 52g não fixa família de testes. *Resolução:* Como no 52e: sanduíche CR1 por conjunto de escolha (curso × ciclo; num ciclo só, é o curso), fator G/(G − 1), IC 95% e p pela normal; também o p com t de G − 1 graus de liberdade. Score bootstrap de Kline–Santos (`score_bootstrap` do 50: ajuste restrito sob β = 0 partindo da estimativa irrestrita sem a bolsa; Rademacher por enumeração completa se G ≤ 24, senão 199.999 sorteios com a semente do 16; Webb também). Cada linha relata G de conjuntos. Não há família confirmatória nova (o 52g chama VG-1 e VG-3 de robustez por ciclo); Holm nas duas (com o p por cluster e com o p do score) vai como coluna descritiva.
5. **Leitura do §2 por regra** (28/10/2026). O §2 lê o IC de VG-1 e VG-3 contra 1 e fala em "mesmo sinal" sem dizer de quê; e pede peso ao score bootstrap. *Resolução:* Para VG-1 e VG-3: IC 95% (CR1) que contém 1 → `IC_CONTEM_1`; IC que exclui 1 com o log da razão de chances do mesmo sinal que o do VL-1 do ciclo 2 reproduzido → `EXCLUI_1_MESMO_SINAL`; do sinal oposto → `EXCLUI_1_SINAL_OPOSTO`; sem estimativa → `SEM_ESTIMATIVA`. Leitura geral: algum `EXCLUI_1_SINAL_OPOSTO` → `DEPENDE_DA_COMPOSICAO` (3ª linha do §2); senão, algum `EXCLUI_1_MESMO_SINAL` → `APARECE_TAMBEM_EM_OUTRO_CICLO` (2ª linha, com o ciclo); senão, os dois `IC_CONTEM_1` → `FORTE_SO_NO_CICLO_2` (1ª linha); com alguma linha sem estimativa, `INCOMPLETA`. Peso ao score: para cada linha, `score_concorda` = (p do score Rademacher < 0,05) igual a (IC exclui 1). Quando não concorda, o doc diz, na resposta curta, que a classificação daquele ciclo não se confirma pelo score bootstrap; a regra não muda.
6. **km equivalentes (VG-4)** (28/10/2026). O §1 pede os km equivalentes de +R$ 5 mil em VG-1 e VG-3, como no VL-4. *Resolução:* Como no VL-4: K5 e K10 pela função `linha_km` do 25c (100 · passo · β / (−γ)), IC pelo método delta e por Fieller, descritivos, sem teste. Se o IC do β contém zero, o doc diz que o IC dos km também contém e que os km ficam instáveis.
7. **Quem identifica (VG-5)** (28/10/2026). O §1 pede a contagem de pares de UF e de candidatos que identificam em cada ciclo. *Resolução:* As contagens do `desenho_ef` do 50, as mesmas da seção 3 do 57x: pares no desenho e no modelo, pares com variação de bolsa, alternativas e candidatos retirados, candidatos no modelo, candidatos com variação de bolsa dentro de algum par e com a 1ª opção num par com variação, colunas de efeito fixo. Para os quatro VL-1 (ciclos 1, 2, 3 e 1–3), com G de conjuntos.
8. **Falha de convergência** (28/10/2026). Num ciclo só há menos candidatos por par; o Newton pode não convergir ou a matriz pode perder posto. *Resolução:* Como no 50: a linha fica `NAO_CONVERGIU` com a nota da `estimar_ef`, sem trocar partida, especificação ou amostra; a leitura dela é `SEM_ESTIMATIVA`. Coluna sem variação dentro de nenhum candidato é omitida, como no 25, e a omissão vai na nota.
9. **Saídas e figura** (28/10/2026). O §3 lista script, `VG_estimativas.csv`, `VG_resumo.json`, doc 57z e testes; não lista figura. *Resolução:* Não há figura. O CSV tem, por linha estimada, os coeficientes fora dos indicadores de par, a razão de chances por +R$ 5 mil e K5 e K10; as linhas reproduzidas (VL-1 dos ciclos 2 e 1–3) entram com `papel = reproducao_VG-R`. `VL_*` não são regravadas.
10. **Números do doc 57z** (28/10/2026). O pedido exige números só em blocos gerados. *Resolução:* Todo número de resultado do 57z vem de `VG_*` por `--atualizar-doc`, entre marcadores `<!-- VG:... -->`; o teste confere o doc contra o gerado e que não há número de resultado fora dos blocos. A redação da resposta curta é escolhida por regra (`leitura`), sem texto escrito depois de ver os números.
<!-- VG:decisoes:fim -->

## 7. Limites

- **Pós-resultado.** O VL-1 empilhado e o do ciclo 2 já eram conhecidos. O adendo foi congelado antes de rodar, mas isto é robustez por ciclo, não teste confirmatório novo.
- **Poucos conjuntos por ciclo.** Num ciclo só, o cluster é o curso, e são poucos. O IC com cluster pode ser otimista; por isso o score bootstrap vai ao lado, e o número de conjuntos de cada linha está na tabela.
- **Identificação estreita.** Com o par de UFs, o peso da bolsa vem só de UFs que têm vagas de faixas diferentes e de candidatos que veem essa variação (seção 3). Num ciclo só, são menos pares e menos candidatos.
- **Pares sem escolha saem.** As vagas de pares que ninguém daquela origem escolheu naquele ciclo saem do conjunto (decisão 2 do 57x); o conjunto de escolha do modelo fica menor que o do M1.
- **Escolha condicional.** Tudo vale para quem se candidatou, dentro das vagas abertas do seu curso e ciclo; IIA do logit condicional.
- **Pacote do corte.** O peso da bolsa é identificado pelos saltos nos cortes de IVS, com o IVS em spline contínua; nos mesmos cortes mudam outras regras federais (auditoria 18). Não é efeito da participação no PMM-E nem do Agora Tem Especialistas.
- **Origem não é causal.** A origem é o município do vínculo médico no CNES (G1), não a residência; o peso da origem é preferência revelada, não efeito causal.
- **km são razões.** Com o peso da bolsa perto de zero, os km equivalentes ficam instáveis e não são preço.
