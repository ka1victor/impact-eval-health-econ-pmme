# 11. Slides de apoio: como ler e como foi feito o logit condicional com o par de UFs

> **Finalidade:** doze slides de apoio para responder a perguntas da banca sobre o resultado "na mesma UF, a vaga de
> bolsa maior é preferida" (VL-1 do adendo 52e). Eles explicam a razão de chances, o log, o modelo, onde ele é usado e as alternativas mais simples, a base, os coeficientes da especificação principal, o efeito
> fixo do par, o que é fixo e o que é controle, o código e por que a conta perto do corte dá menos.<br>
> **Estatuto:** material de apoio, fora do deck curto (que continua com no máximo 14 slides). Não traz resultado novo:
> todo número vem de `output/rdd_bolsa/VL_estimativas.csv` e `VL_resumo.json` (adendo 52e, doc 57x, auditoria 48),
> e o gerador para se algum número deste doc divergir dessas saídas.<br>
> **Deck derivado:** `output/apresentacao_banca2/slides_explicacoes_logit.pptx` (e `.pdf`), gerado por
> `scripts/apresentacao/gerar_slides_explicacoes_logit.py` com o template do deck curto. Divergência entre o deck e
> este doc é erro do deck.<br>
> **Origem:** perguntas do autor de 04/11/2026, durante a banca 2.

## Formato

Cada `##` entre os marcadores é um slide. As linhas `- campo: valor` dão seção do rodapé, layout, equação, cartões,
cautela, fontes e notas do apresentador. Tabelas em markdown entram como tabela nativa. No layout `codigo`, cada
`### Passo` traz um rótulo, o arquivo e as linhas; o gerador confere que cada linha de código mostrada existe, igual,
nessa posição do arquivo.

<!-- slides:inicio -->

## Razão de chances: vaga A contra vaga B, no mesmo cardápio

- secao: Metodologia
- layout: espec
- equacao: P(A) ÷ P(B) = exp(5·β) = 1,47 [1,15; 1,89]
- cartao: **A e B** iguais em tudo no modelo; A paga +R$ 5 mil por mês
- cartao: **Não é** a chance de escolher A contra a de não escolher A
- cartao: **Na prática** ≈ 107 vagas por candidato: a probabilidade sobe ≈ 47%
- fontes: VL_estimativas.csv (VL-1, ciclos 1–3; adendo 52e); doc 57x §1; auditoria 48.
- notas: A razão de chances compara duas alternativas do mesmo candidato. Pegue duas vagas A e B no cardápio dele, iguais em tudo que está no modelo (mesmo par de UFs, mesma distância, mesmo tipo de vaga); a única diferença é que A paga R$ 5 mil a mais, um degrau da bolsa. Então P(A) ÷ P(B) = exp(5β) = 1,47. No logit condicional essa razão não depende de qual é a vaga B. Como cada candidato tem em média ≈ 107 alternativas no VL-1, cada vaga tem probabilidade pequena e a razão de chances fica perto da razão de probabilidades: a probabilidade de a vaga ser a 1ª opção sobe cerca de 47%. Escolha condicional a se candidatar; a bolsa é o pacote do corte.

## O log está no modelo e no eixo, não na bolsa

- secao: Metodologia
- layout: espec
- equacao: log[P(A) ÷ P(B)] = β·Δbolsa;  5β = 0,385 → exp(0,385) = 1,47
- cartao: **IC** simétrico em log, 0,385 ± 0,25; exponenciado, [1,15; 1,89]
- cartao: **Eixo** em log: 0,5 e 2 ficam à mesma distância de 1
- cartao: **75 km** = 0,385 ÷ 0,514 × 100 km (peso da distância na mesma UF)
- fontes: VL_estimativas.csv (VL-1, ciclos 1–3: razão de chances, distancia_100km e K5); doc 57x §1 (VL-4).
- notas: O logit é linear no log da razão de chances: log[P(A)/P(B)] = β vezes a diferença de bolsa. O coeficiente estimado já é um log-odds; por +R$ 5 mil, 5β ≈ 0,385, e e elevado a 0,385 dá 1,47. O intervalo é calculado nessa escala, onde é simétrico (0,385 ± 0,25), e depois exponenciado; por isso fica assimétrico em torno de 1,47. No gráfico o eixo é log para que dobrar (2) e cortar pela metade (0,5) fiquem à mesma distância do 1, o "sem efeito". Os 75 km saem da razão entre os dois pesos: a bolsa pesa +0,385 por R$ 5 mil e a distância −0,514 por 100 km, dentro da mesma UF; IC delta [28; 122] km. Nenhum log da bolsa entra no modelo.

## Logit condicional: cada médico comparado consigo mesmo

- secao: Metodologia
- layout: espec
- equacao: V_ij = β·bolsa_j + f(IVS_j) + γ·dist_ij + α_par + …;  P_ij = exp(V_ij) ÷ Σ_k exp(V_ik)
- cartao: **Estima** o β que maximiza Σ log P(vaga que cada um escolheu)
- cartao: **Cancela** tudo que é do médico: idade, nota, perfil
- cartao: **Erro-padrão** com cluster por conjunto de escolha (curso × ciclo): 55
- fontes: scripts/rdd_bolsa/25_escolha_dap.py (_estat, ajustar_cl); protocolo 52; adendo 52e; doc 57x.
- notas: Cada candidato i tem um cardápio: as vagas (CNES × curso) do seu curso e ciclo no quadro da 1ª chamada. Cada vaga j recebe uma atratividade V_ij: bolsa (linear, por R$ 1 mil), curva contínua do IVS (spline com dobras em 0,300 e 0,400, sem salto), distância por 100 km, mesma região de saúde e mesmo município da origem, porte, capital, estrato, vaga imediata e o efeito fixo do par (UF de origem, UF da vaga). A probabilidade de j ser a 1ª opção é e^V_ij dividido pela soma sobre o cardápio. O software escolhe os parâmetros que maximizam a soma, sobre os candidatos, do log da probabilidade da vaga de fato escolhida (Newton–Raphson próprio, conferido contra o ConditionalLogit do statsmodels no doc 42). Como a soma do denominador é dentro de cada candidato, o que é constante entre as vagas dele se cancela. O número do slide é exp(5β).

## Especificação principal: coeficientes do VL-1

- secao: Resultados
- layout: coeficientes
- modelo: VL1_emp
- cautela: Mais 254 dummies do par, não mostradas; estrato-base: interior perto de polo
- fontes: VL_estimativas.csv (VL-1, ciclos 1–3, tipo_linha = coeficiente); doc 57x §4.4; auditoria 48.
- notas: Especificação principal do adendo 52e (pós-resultado): logit condicional da 1ª opção, ciclos 1–3, 5.417 candidatos, com efeito fixo do par (UF de origem, UF da vaga). Cada coeficiente é o peso do termo na utilidade, em log-chance, por unidade do termo; exp(coeficiente) é a razão de chances entre duas vagas do mesmo cardápio que só diferem nesse termo. A bolsa pesa 0,077 por R$ 1 mil; vezes 5 dá 0,385, a razão de chances de 1,47 por +R$ 5 mil. A distância pesa −0,514 por 100 km. IC 95% e p bilaterais com cluster por conjunto de escolha (55 conjuntos), sem correção para múltiplos testes; o p de Holm da bolsa, na família das três principais do 52e, é 0,005. As dobras do IVS mudam a inclinação da curva contínua nos cortes, sem salto: o salto nos cortes é o da bolsa. Os controles são preferência revelada entre vagas, não efeitos causais: mesmo município, mesma região, porte e vaga imediata descrevem quais vagas os candidatos escolhem.

| Termo | Coeficiente (log-chance) | IC 95% | p |
|---|---|---|---|
| Bolsa (por R$ 1 mil/mês) | 0,077 | [0,027; 0,127] | 0,002 |
| IVS: inclinação | −0,170 | [−0,410; 0,071] | 0,166 |
| IVS: dobra em 0,300 | 0,435 | [0,085; 0,786] | 0,015 |
| IVS: dobra em 0,400 | −0,426 | [−0,724; −0,128] | 0,005 |
| Distância (por 100 km) | −0,514 | [−0,555; −0,474] | < 0,001 |
| Mesma região de saúde | 1,103 | [0,845; 1,361] | < 0,001 |
| Mesmo município | 0,587 | [0,314; 0,860] | < 0,001 |
| Tem vaga imediata | 0,254 | [0,043; 0,465] | 0,018 |
| log(vagas imediatas + 1) | 0,491 | [0,247; 0,734] | < 0,001 |
| log(população 2022) | 0,140 | [0,081; 0,198] | < 0,001 |
| Capital | −0,313 | [−0,654; 0,028] | 0,072 |
| Interior remoto | −0,188 | [−0,379; 0,003] | 0,054 |
| Metropolitano | 0,104 | [−0,050; 0,258] | 0,186 |

## Literatura: logits mais ricos; nós usamos o mais simples

- secao: Metodologia
- layout: ficha
- cautela: A bolsa vem de regra: o degrau já identifica, sem instrumento nem equilíbrio
- fontes: doc 03_literatura_empirica/20 (A1, B5, C1, D3, D4); Bobba et al., NBER WP 29068, rev. 22/01/2026, seção 4.1 e nota 13; protocolo 52 (M8, M9); doc 57a.
- notas: A nossa literatura empírica de escolha de local usa a família logit, quase sempre em versões mais ricas que a nossa, e cada uma por um motivo. Bobba et al., o desenho mais parecido, usam logit multinomial com cardápio personalizado porque lá o professor escolhe na sua vez, vendo só as vagas que restam, e incluem a opção de não aceitar nenhuma. Costa, Nunes e Sanches usam logit de coeficientes aleatórios com instrumento porque o salário de mercado é endógeno: é alto onde a vaga é ruim. Holmes usa logit multinomial com correção de seleção porque mede a participação num programa. Os experimentos de escolha (Miranda; Kurniati) usam logit condicional, mas com vagas hipotéticas. No PMM-E a bolsa é fixada por regra com corte, a vulnerabilidade entra como curva contínua e o candidato lista as opções na inscrição, antes do resultado. Por isso o logit condicional, o mais simples da família, basta para identificar o peso da bolsa: é a mesma lógica da nota 13 de Bobba et al. O logit misto (M8) e o aninhado por região de saúde (M9) entram como sensibilidade no protocolo 52; não foram refeitos com o par de UFs. McFadden (1974) é a referência do estimador.

| Estudo | Método | Por que precisam disso |
|---|---|---|
| Bobba et al. (2026) | logit multinomial, cardápio personalizado | escolhe na sua vez; pode recusar tudo |
| Costa, Nunes e Sanches (2024) | logit de coeficientes aleatórios + instrumento | salário de mercado é endógeno |
| Holmes (2005) | logit multinomial com seleção | mede participação no programa |
| Miranda (2012); Kurniati (2024) | logit condicional | vagas hipotéticas (DCE) |
| **Nós (VL-1)** | **logit condicional + efeito fixo do par** | **bolsa por regra; opções listadas na inscrição** |

## Por que não um método mais simples?

- secao: Metodologia
- layout: ficha
- cautela: Trocar de estimador agora seria escolha pós-resultado: só como robustez
- fontes: doc 44 (F1.1); doc 57a §9 (P1g); Guimarães, Figueiredo e Woodward (2003), *REStat* 85(1).
- notas: A alternativa mais usual na avaliação de política seria a RDD por vaga, com o número de candidatos de 1ª opção como outcome. Ela foi feita (F1.1, e a ponte P1g do protocolo 52) e o IC contém zero: só usa a variação entre vagas e perde a informação de que o mesmo candidato viu vagas com bolsas diferentes. Um MQO com efeito fixo do candidato (modelo de probabilidade linear) faz a mesma comparação dentro do candidato, mas a probabilidade de cada vaga é perto de 1% e o modelo prevê probabilidades fora de [0, 1]; não está no protocolo. A Poisson das contagens de escolhas, com efeito fixo de cada grupo de candidatos com o mesmo cardápio e a mesma origem, dá exatamente o mesmo β do logit condicional (Guimarães, Figueiredo e Woodward, 2003); é o atalho usual na literatura de localização de firmas. Ou seja: o logit condicional já é o modelo simples dessa família; os papers mais parecidos usam versões mais ricas. Pelas regras do projeto, não se troca o estimador depois de ver o resultado; uma alternativa entraria só como robustez rotulada.

| Alternativa | O que compara | Por que não é a principal |
|---|---|---|
| RDD por vaga (nº de 1ªs opções) | vagas dos dois lados do corte | feita: IC contém zero; perde a variação dentro do candidato |
| MQO com efeito fixo do candidato | vagas do mesmo candidato, em p.p. | probabilidade ≈ 1% por vaga; fora do protocolo |
| Poisson das contagens com efeito fixo | vagas do mesmo cardápio e origem | dá o mesmo β do logit condicional |

## A base: uma linha por candidato × vaga do cardápio

- secao: Dados
- layout: ficha
- cautela: Linhas ilustrativas. VL-1: 5.417 candidatos, 578.998 linhas, 55 conjuntos
- fontes: VL_resumo.json (identificacao, VL-1 ciclos 1–3); VL_estimativas.csv; scripts/rdd_bolsa/25_escolha_dap.py (montar_desenho).
- notas: A base de estimação está em formato longo. Cada candidato ocupa um bloco de linhas, uma por vaga do seu cardápio; a coluna "escolheu" vale 1 só na 1ª opção. As colunas são os atributos da vaga (bolsa, IVS, vaga imediata, porte) e da relação com o candidato (distância entre os centroides do município de origem e o da vaga, mesma região de saúde, mesmo município), mais as dummies do par. No VL-1 dos ciclos 1–3 sobram 5.417 candidatos e 578.998 linhas, depois de retirar os pares de UF que ninguém escolheu (a dummy deles iria a menos infinito). Os valores da tabela são ilustrativos, não são linhas reais.

| Candidato | Vaga | Escolheu | Bolsa (mil) | Distância (100 km) | MG→SP | MG→BA |
|---|---|---|---|---|---|---|
| A (MG) | v1 em MG | 0 | 10 | 1,2 | 0 | 0 |
| A (MG) | v2 em MG | **1** | 15 | 3,4 | 0 | 0 |
| A (MG) | v3 em SP | 0 | 10 | 5,1 | 1 | 0 |
| A (MG) | v4 na BA | 0 | 20 | 9,8 | 0 | 1 |
| B (BA) | v1 em MG | 0 | 10 | 11,0 | — | — |

## De onde vem cada coluna da base

- secao: Dados
- layout: ficha
- cautela: Nada é imputado: escolha fora do cardápio faz o script parar
- fontes: dicionario_outcomes_funil.json; scripts/rdd_bolsa/12, G1 e 25 (carregar, montar_desenho).
- notas: As escolhas vêm do arquivo de classificação da 1ª chamada (1ª e 2ª opção de cada candidato). O cardápio é o quadro de vagas da 1ª chamada: todas as células CNES × curso do curso e ciclo, com ou sem vaga imediata. O município de origem vem da ligação do candidato ao CNES antes do programa (G1: CPF mascarado e nome, ambíguos fora). A bolsa sai da regra do IVS 2010 oficial (cortes 0,300 e 0,400). A distância é a de haversine entre os centroides do IBGE; a região de saúde é a CIR do TabNet.

| Ingrediente | Arquivo em output/ | Unidade |
|---|---|---|
| Escolhas (1ª e 2ª opção) | outcomes/escolhas_candidatos.parquet | candidato × opção |
| Cardápio de vagas | outcomes/escolhas_conjunto_principal.parquet | CNES × curso × ciclo |
| Município de origem | G1_candidatos_origem.parquet | candidato (CNES pré) |
| Bolsa | aquisicao/a08 (IVS 2010 oficial) | município |
| Distância e região | centroides IBGE; CIR TabNet | origem × vaga |

## Efeito fixo do par: uma dummy por origem × UF da vaga

- secao: Identificação
- layout: tabela_cartoes
- cartao: **Absorve** apego à própria UF, atratividade do estado, macrorregião
- cartao: **Sobra** bolsa diferente dentro do par: 260 pares, 5.345 candidatos
- cartao: **Tamanho** 729 → 281 pares com escolha; 254 dummies
- fontes: VL_resumo.json (identificacao, VL-1 ciclos 1–3); doc 57x §3 e decisões 1–3.
- notas: Sim, é um conjunto de dummies: uma por par (UF de origem do médico, UF da vaga), menos uma base por origem, o par da própria UF. Como a UF de origem é constante dentro do cardápio de cada candidato, cada origem ganha o seu próprio jogo de dummies de UF da vaga: o mineiro pode gostar de SP de um jeito e o baiano de outro. O par absorve tudo que é comum às vagas de uma UF para médicos de uma origem: o apego à própria UF, laços em nível de estado, a atratividade do estado e a macrorregião; por isso mesma_uf e as macrorregiões saem do modelo. O β da bolsa só aprende com vagas do mesmo par com bolsas diferentes: 260 pares e 5.345 candidatos. Pares sem variação de bolsa ficam no modelo e ajudam só os controles.

| Candidato de MG | Candidato da BA |
|---|---|
| MG→MG = base | BA→BA = base |
| dummy MG→SP | dummy BA→SP |
| dummy MG→BA | dummy BA→MG |

## Fixo por construção ou controlado?

- secao: Identificação
- layout: ficha
- cautela: Com log da distância: 1,45 [1,15; 1,83]; a leitura não muda
- fontes: VL_estimativas.csv (VL-1 e VL-1 com log da distância, ciclos 1–3); doc 57x §1 e decisão 4.
- notas: Candidato e par de UFs são fixos por construção: o candidato porque o logit condicional só compara as vagas de cada um; o par porque há uma constante por par. A distância não é pareada; entra como controle linear (−0,514 por 100 km dentro da mesma UF). "Mesma distância" vem do modelo, que supõe efeito linear em km. Com log(1 + km) no lugar, a razão de chances fica em 1,45 [1,15; 1,83]. Mesma região de saúde e mesmo município também são controles. Frase pronta: candidato e par de UFs são fixos por construção; a distância é controle paramétrico, e o resultado não muda em log.

| Item | Como entra | Fixo de fato? |
|---|---|---|
| Candidato | logit condicional: só compara as vagas dele | **sim** |
| Par de UFs | uma dummy por (origem, UF da vaga) | **sim** |
| Distância | controle linear: −0,514 por 100 km | **não**: controlada |
| Região e município | dummies de mesma região e mesmo município | **não**: controlados |

## No código, o par é só mais uma coluna da matriz X

- secao: Metodologia
- layout: codigo
- fontes: scripts/rdd_bolsa/50_escolha_localizacao_par.py (colunas_ef, matriz_vl); scripts/rdd_bolsa/25_escolha_dap.py (_estat); auditoria 48.
- notas: Três passos. (a) Cada linha recebe o rótulo do par, origem|vaga, e a base de cada origem é o par da própria UF. (b) mesma_uf e as macrorregiões saem, porque o par as absorve, e entra uma coluna 0/1 por par. (c) A verossimilhança soma dentro de cada candidato: com uma constante por par, a bolsa só explica a escolha pela diferença entre vagas do mesmo par. Duas salvaguardas: coluna que não varia dentro de nenhum candidato sai (25_escolha_dap.py, colunas_sem_variacao), e par sem escolha sai do modelo (50, filtrar_pares). A contracao_ef só dá o ponto de partida do Newton; a auditoria 48 refez a conta de forma independente.

### Passo: (a) rótulo do par e base | scripts/rdd_bolsa/50_escolha_localizacao_par.py:525,540

```python
    par = pd.Series(o_lin, dtype=object) + "|" + pd.Series(v_lin, dtype=object)
        propria = f"{o}|{uf_da_origem[o]}"
```

### Passo: (b) tira o absorvido e cria as dummies | scripts/rdd_bolsa/50_escolha_localizacao_par.py:616,619,621

```python
    X = X.drop(columns=[c for c in X.columns if c in ABSORVIDOS or c.startswith("macro_")])
    Z = np.zeros((len(X), len(ef["nomes"])))
    Z[np.flatnonzero(m), ef["col"][m]] = 1.0
```

### Passo: (c) verossimilhança dentro de cada candidato | scripts/rdd_bolsa/25_escolha_dap.py:490,493,494,495

```python
    v = X @ theta
    S = np.add.reduceat(e, st)
    p = e / S[grp]
    ll_g = v[esc] - vmax - np.log(S)
```

## Perto do corte, o salto é medido contra outra reta

- secao: Robustez
- layout: ficha
- cautela: 1,47 cabe no IC do VL-2: inconclusivo, não "efeito menor"
- fontes: VL_estimativas.csv (VL-1 e VL-2, ciclos 1–3); doc 57x §4; auditoria 48.
- notas: A bolsa só muda nos cortes, e o IVS entra como uma linha contínua com dobras em 0,300 e 0,400. O efeito da bolsa é o salto que sobra no corte depois de descontar essa linha. Com todas as vagas (VL-1), a inclinação perto do corte é extrapolada de vagas com IVS de 0,10 a 0,70; se a atratividade faz curva ao longo do IVS, o erro da linha aparece como efeito da bolsa. Só com vagas a até 0,050 de um corte (VL-2), a inclinação sai das vizinhas e a forma muda bastante (a dobra em 0,400 troca de sinal); com outra linha de base, o salto que sobra é menor. Mas há menos informação e o IC é largo; 1,47 está dentro do IC do VL-2. É a sensibilidade à largura da janela típica de RDD: a conta local é inconclusiva, não confirma nem derruba o 1,47. Análise pós-resultado (adendo 52e).

| | Todas as vagas (VL-1) | Só ±0,050 do corte (VL-2) |
|---|---|---|
| Razão de chances (+R$ 5 mil) | 1,47 [1,15; 1,89] | 1,28 [0,95; 1,72] |
| Dobra da reta do IVS em 0,300 | 0,44 | 0,12 |
| Dobra da reta do IVS em 0,400 | −0,43 | 0,30 |
| Candidatos | 5.417 | 4.288 |

<!-- slides:fim -->

## Números e de onde vêm

O gerador recalcula cada número abaixo de `output/rdd_bolsa/VL_estimativas.csv` e `VL_resumo.json` e para se o texto
acima não trouxer exatamente o valor recalculado.

| Número no doc | Linha de `output/` |
|---|---|
| 1,47 [1,15; 1,89]; 0,385; ± 0,25 | `VL1_emp`, `razao_chances_por_5mil` e `coeficiente` de `bolsa_mil` |
| −0,514 por 100 km | `VL1_emp`, `coeficiente`, `distancia_100km` |
| 75 km | `VL1_emp`, `km_equivalentes`, `K5` |
| 1,45 [1,15; 1,83] | `VL1log_emp`, `razao_chances_por_5mil` |
| 1,28 [0,95; 1,72]; 4.288 | `VL2_emp`, `razao_chances_por_5mil` |
| 0,44; −0,43; 0,12; 0,30 | `VL1_emp` e `VL2_emp`, `ivs_mudanca_inclinacao_0300` e `_0400` |
| 5.417; 578.998; 55; ≈ 107 | `VL1_emp`: `n_candidatos`, `n_linhas_candidato_celula`, `n_conjuntos` e a razão linhas ÷ candidatos |
| Tabela de coeficientes | `VL1_emp`, `tipo_linha = coeficiente`: conferida célula a célula |
| 729 → 281; 260; 254; 5.345 | `VL_resumo.json`, `identificacao.VL1_emp` |
