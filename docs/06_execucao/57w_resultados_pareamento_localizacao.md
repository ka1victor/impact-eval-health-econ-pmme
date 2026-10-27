# 57w. H1 pareada pela localização da unidade (UF) e dos médicos (especialistas num raio de 100 km) (adendo 48h)

> **Data:** 27/10/2026.<br>
> **Adendo:** [`48h_adendo_pareamento_localizacao_unidade_e_medicos.md`](48h_adendo_pareamento_localizacao_unidade_e_medicos.md),
> congelado antes destas contas (commit `243160d`). SHA-256 do adendo em `adendo` de `PL_resumo.json`, conferido pelo
> script.<br>
> **Estatuto:** `ADENDO_48H_POS_RESULTADO`. A H1 (48b), os controles e pareamentos por macrorregião (48d, 48e), a UF
> (48c) e o porte (48g) já tinham sido vistos. Toda linha de `PL_estimativas.csv`, `PL_balanco.csv` e
> `PL_excluidos.csv` tem `natureza_dos_dados = EMPIRICO`.<br>
> **Auditoria:** pendente.<br>
> **Script:** `scripts/rdd_bolsa/49_pareamento_localizacao.py` (importa o 44 e o 45; não os reescreve). **Saídas:**
> `output/rdd_bolsa/PL_estimativas.csv`, `PL_balanco.csv`, `PL_excluidos.csv`, `PL_resumo.json`, `PL_figuras/`.
> **Testes:** `tests/test_pareamento_localizacao.py`.<br>
> **Números:** nenhum é digitado. Os blocos entre marcadores `<!-- PL:... -->` são regravados das saídas por
> `49_pareamento_localizacao.py --atualizar-doc`; o teste confere que cada bloco é idêntico ao gerado.

**Contraste.** Em toda linha, o lado com bolsa maior (IVS acima do corte) é comparado com o lado com bolsa menor; o
próprio corte fica no lado de baixo. Em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil e em 0,400 de
R$ 15 mil para R$ 20 mil, mas outras regras federais mudam nos mesmos cortes
([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)). O que se mede é o **pacote do corte**, não o
incentivo de R$ 5 mil isolado, nem a participação no PMM-E, nem o Agora Tem Especialistas. Este adendo é robustez: o
principal da H1 continua o 48b.

## 0. Decisões de implementação (27/10/2026, registradas antes de qualquer estimativa deste adendo)

O adendo segue o 48d, o 48e e as decisões das seções 0 dos docs 57r e 57s, salvo onde o 48h muda. Nos pontos que o
48h deixa abertos, ficou a leitura mais próxima dos scripts 44 e 45. Estas decisões foram escritas antes de rodar
qualquer conta nova do adendo. Para escrevê-las, olhei só a estrutura das entradas (colunas, cobertura da X1 e dos
centroides); nenhum outcome por lado do corte foi olhado.

**Base**

1. **Unidade e outcomes.** Só a H1: unidades município × ciclo montadas por `bases_h1` do 44 (ciclos 1 a 3; ciclo 2
   pelo quadro de 13/02/2026). Y1 = fração das células com vaga imediata preenchidas na 1ª chamada; Y2 = alocados na
   1ª chamada em células com vaga imediata ÷ vagas imediatas (decisão 10 do 57r). Janela |IVS − corte| ≤ 0,050
   (`_janela` do 44), cada corte separado. O IVS é o oficial do a08.
2. **Escore.** Logit de P(acima do corte | X), com X = log(população 2022), médicos por 10 mil hab. no município,
   especialistas nas CBO-alvo por 10 mil hab. no município e o **raio** (decisões 3 a 6). As três primeiras são as
   do 44, na unidade município × ciclo como no 48d/48e: os especialistas do município são a soma das CBO-alvo de
   todos os cursos (o adendo diz que "o resto do escore segue o 48d/48e"). Capital e UF **não** entram no escore:
   entram como pareamento exato (decisão 10). A macrorregião e o resto da região de saúde saem do escore (o raio e a
   UF tomam o lugar deles). Os três ciclos juntos num só logit, como na decisão 13 do 57r.

**O raio de 100 km**

3. **Distância.** Círculo máximo entre os centroides do IBGE do arquivo do script 17
   (`ibge_api_v3_malhas_metadados_municipios.json`), lidos por `ler_coordenadas` e medidos por `haversine_km`, as duas
   funções do 17, importadas. Antes de qualquer conta, o SHA-256 do arquivo é conferido contra o manifesto do 17
   (`.manifesto.json`) e contra a entrada do arquivo em `X1_ligacao_resumo.json`. Todo município do a08 tem de ter
   centroide; se faltar algum, o script para.
4. **Taxa do raio de um curso.** Para o município m e o curso k: vizinhos de m são os municípios do universo do a08
   (o mesmo universo do 44) com distância ≤ 100 km, sem o próprio m. Estoque = soma, nos vizinhos, da média mensal
   de vínculos de 2024-06 a 2025-06 do a09 nas CBO-alvo do curso k (ponte do a09; a mesma média `_media_pre` do 44).
   População do raio = soma da população do Censo 2022 dos vizinhos. Taxa = estoque ÷ população × 10 mil. Fica
   ausente, como no `_resto_regiao` do 44, quando não há vizinho no raio ou quando algum vizinho não tem a média ou
   a população. Os municípios criados depois de 2010 não estão no a08 e não entram no raio, como não entram no resto
   da região de saúde do 44.
5. **Média das CBO-alvo dos cursos com vaga imediata do município × ciclo, ponderada pelas vagas imediatas.** As
   células com vaga imediata da unidade são as do 48b (`tipo_celula` só imediatas ou mista). Peso de cada célula =
   suas vagas imediatas (`vagas_imediatas`); valor = taxa do raio do curso da célula (decisão 4). O raio da unidade é
   Σ peso × taxa ÷ Σ peso. Confere-se que a soma dos pesos de todas as células com vaga imediata é igual a `vi_imed`
   do 40. Células de cursos fora da ponte do a09 (17 a 20, só no ciclo 3) não têm CBO-alvo e ficam fora da média;
   são contadas. Se nenhuma célula com vaga imediata da unidade tiver curso na ponte, o raio fica ausente e a unidade
   sai das linhas que o usam, contada (nada é imputado).
6. **Na célula** (só na PH-4, HI-1): o raio é a taxa do curso da célula (decisão 4); células de cursos 17 a 20 saem
   dessa linha, como saem das linhas com M no 44. **Raios de 50 e 200 km** (PH-2): a mesma construção, trocando só a
   distância máxima.

**Regra 2 na UF**

7. **Categorias.** Capital, não capital e cada UF presente na amostra; a UF toma o lugar da macrorregião do 45. Uma
   categoria é "de um lado só" quando tem pelo menos uma unidade e todas do mesmo lado do corte. A conferência é feita
   por corte, na janela de 0,050, com os três ciclos juntos (decisão 2 do 57s), depois da saída por covariável
   ausente, numa passada só (decisão 3 do 57s): saem de uma vez todas as unidades das categorias de um lado só; o
   que sobrar de um lado só depois é registrado. A função é a `amostra` do 45, com a lista de categorias trocada
   durante a chamada.
8. **Quem sai é listado** em `PL_excluidos.csv` (código IBGE, nome, UF, ciclo, lado, categorias que o tiraram, IVS),
   para a PH-1 e para cada raio da PH-2. **"Mais de 25% de um lado"** (§3): denominador = unidades daquele lado na
   janela depois da saída por covariável ausente (decisão 6 do 57s), na amostra da PH-1.
9. **PH-2:** a regra 2 é refeita na amostra de cada raio, porque quem não tem vizinho em 50 km sai por covariável
   ausente antes dela. **PH-3:** mesma amostra, mesmo escore e mesma regra 2 da PH-1; só o exato muda (decisão 11).

**Pareamento**

10. **Exato na UF e em capital, regra literal.** As candidatas a par são as do `parear_psm` do 44 (mesmo ciclo, as
    duas no suporte comum, |diferença no logit| ≤ *caliper*), filtradas para mesma UF e mesma condição de capital.
    Sobre elas roda a `regra_literal` do 45: em cada ciclo, o lado com menos unidades (contadas na amostra da regra 2)
    procura par; empate, o de cima; ordem decrescente do escore; cada uma fica com a candidata livre mais próxima no
    logit; sem reposição; sem candidata, fica sem par. *Caliper* = 0,2 × desvio-padrão do logit do escore na amostra
    da regra 2; suporte comum mínimo–máximo nessa amostra (decisões 11 do 57s e 13–14 do 57r).
11. **PH-3:** o mesmo, com exato na região de saúde (CIR oficial do TabNet, a do 44) no lugar da UF, mais capital e
    ciclo. Unidade sem CIR não tem par. "Onde houver pares" = forma par quem tiver candidata na mesma CIR.
12. **Implementação.** O script chama `pareamentos` do 44 e troca, só durante a chamada, três coisas, como o 45 troca
    o último passo: o conjunto de variáveis do escore (o L+M do 44 vira o X da decisão 2), as variáveis do balanço
    (decisão 18) e o último passo (`guloso_global`) pelo filtro exato + regra literal. Tudo é devolvido depois. A
    inferência, o balanço, o suporte e a montagem das linhas são os do 44.

**PH-4 (comparação com a reta)**

13. RDD do 48b pela `rd_h1` do 44: HI-1 (célula, EF de curso × ciclo) e HI-2 (município × ciclo, controle das vagas
    imediatas por ciclo), local linear, kernel triangular, h = 0,050, CR1 por município, cada corte separado, com
    **efeito fixo de UF** e a taxa do raio de 100 km como covariáveis lineares de coeficiente comum (CCFT). Ao lado,
    o salto sem controle na mesma amostra. Fica fora do Holm e do BKY.

**PH-5 (de onde vem o médico)**

14. **Fonte.** `X1_medicos.parquet` (saída versionada do 17; SHA-256 conferido contra `X1_ligacao_resumo.json`),
    regra de ligação D1 (a principal no script 28), lista de ativos de 11/09/2026 (como o painel municipal do 17),
    médicos ligados ao CNES. A célula de cada médico (CNES e curso) vem da função `ler_listas_pmme` do 17, que
    reconstrói o mesmo `id_medico`; nome, CRM e UF do CRM são descartados na hora, e a reconstrução é conferida
    contra a X1 (ciclo, município e lista), como no 28. Entram só médicos em células com vaga imediata do quadro do
    ciclo (decisão 5).
15. **Origem.** "Mesma UF da vaga" = `c_origem` mesmo município, mesma região de saúde ou mesma UF; "outra UF" =
    `outra_uf`. Sem vínculo médico anterior, origem ausente na X1 ou médico não ligado: "origem desconhecida",
    contada e mostrada na figura, sem linha estimada. A origem é **outcome**, nunca controle: não entra no escore,
    no exato nem na amostra.
16. **Outcomes.** Por município × ciclo: médicos com origem na mesma UF ÷ vagas imediatas, e médicos de outra UF ÷
    vagas imediatas. Só nos ciclos 1 e 2: a X1 não tem origem no ciclo 3 (lá o outcome fica ausente). Os pares são
    os da PH-1 (a mesma chamada de `pareamentos`); pares do ciclo 3 saem por outcome ausente e são contados. Não é a
    decomposição exata de Y2: Y2 conta os alocados da 1ª chamada; a X1, os ativos em 11/09/2026 (limitação).

**Inferência e testes múltiplos**

17. Inferência pareada do 44 (permutação de sinais, 9.999 sorteios, semente 20261026, IC por inversão; IC t
    pareado ao lado; o p do Holm e do BKY é o da permutação). Menos de 2 pares: sem estimativa. **Holm** nas quatro
    linhas da PH-1 (dois outcomes × dois cortes), família de tamanho fixo: linha sem estimativa entra com p = 1.
    **BKY** nas 16 linhas de PH-2 (oito), PH-3 (quatro) e PH-5 (quatro), do mesmo jeito.
18. **Balanço (PH-6).** Diferença padronizada do 44 (desvio-padrão combinado antes do pareamento), na amostra que
    entrou no pareamento, de log(população), médicos, especialistas, raio, capital e uma dummy por UF presente. Depois
    do exato, capital e UF têm diferença zero por construção. **Comparação limpa:** todas as |DP| depois ≤ 0,25.

**Leitura do §3, fixada no código**

19. **`NAO_SE_DETECTA_DIFERENCA`** (1ª linha): as quatro linhas da PH-1 com estimativa, IC de permutação contendo
    zero e comparação limpa.
20. **`REJEITA_ZERO_DEPOIS_DO_HOLM`** (2ª linha), por linha da PH-1 com p de Holm < 0,05: relatar sinal e tamanho, o
    pacote do corte e quem saiu pela regra 2 naquele corte.
21. **`VALE_SO_PARA_UFS_DOS_DOIS_LADOS`** (3ª linha), por corte: a regra 2 tira mais de 25% de um lado (decisão 8).
22. **`INDICIO_ATRAI_DE_LONGE`** (4ª linha), por corte: na PH-5, a linha "outra UF" tem diferença positiva e IC de
    permutação sem zero. Se não, `SEM_INDICIO_DE_ATRAIR_DE_LONGE`. O q de BKY vai ao lado.
23. Quando a 1ª linha não vale, o código diz por quê, linha a linha: `SEM_ESTIMATIVA`, `BALANCO_NAO_LIMPO` ou
    `IC_EXCLUI_ZERO_SEM_HOLM`.

**Portão e integridade**

24. **Portão.** Antes de qualquer conta nova, o script refaz o PM-1 do 48e em 0,300 com as funções do 45 sem troca
    nenhuma e compara com `PM_estimativas.csv` (estimativa, p, IC de permutação e IC t, diferença ≤ 1e−8; mesmo
    número de pares) e com os pares de `PM_resumo.json`. Confere também o SHA-256 dos centroides (decisão 3) e o da
    X1 (decisão 14). Se algo falhar, para sem gravar nada.
25. **Saídas de outros adendos.** O script guarda o SHA-256 de cada arquivo `HI_*`, `CL_*`, `PM_*`, `PO_*` e `X1_*`
    antes de começar e confere de novo antes de gravar; se algum mudar, para sem gravar. Estatuto
    `ADENDO_48H_POS_RESULTADO` e `natureza_dos_dados = EMPIRICO` em toda saída; SHA-256 do adendo 48h conferido; nada
    escrito em `data/`; o arquivo de IVS errado não é lido; nenhuma competência do CNES ≥ 202609.
