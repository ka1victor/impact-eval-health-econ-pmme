# 03. Deck da banca final sobre a versão do grupo (entrada de 14/11/2026)

> **Derivado:** `output/apresentacao_banca_final/deck_banca_final_grupo.pptx` e `.pdf` (32 slides), gerado por
> `scripts/apresentacao/gerar_deck_banca_final_grupo.py`, com as figuras de `gerar_figuras_banca_final.py` e o exemplo
> de `gerar_exemplo_logit_real.py`. O deck é derivado deste documento: divergência é erro do deck.<br>
> **Entrada:** `grupo/deck_grupo_banca_final_1411.pptx` (cópia sem alteração do `PEE - BANCA FINAL` de 14/11/2026;
> SHA-256 `f051366b…64843`; o mesmo de 11/11 com a data dos sumários em 14/11). Antes:
> `grupo/deck_grupo_banca_final_1111.pptx` (SHA-256 `4f645142…44cd5`).<br>
> **Números:** todos lidos de `output/` (VL, VG, P1, S57, portão R1, `numeros_banca2.json` (ESC_*),
> `exemplo_logit_real.json`); nenhum digitado. **Na tela, só fontes públicas** (editais, CNES, Ipea, IBGE, artigos);
> caminhos de arquivos internos ficam nas notas do apresentador e neste documento (teste do deck).<br>
> **Convive com o doc 02:** o deck de 25 slides do doc 02 continua gerado pelo seu script; este é outro arquivo.<br>
> **Preparo da defesa:** [04](04_perguntas_provaveis_logit.md) (perguntas prováveis sobre o logit, com respostas).

## 1. O ponto-chave: o que estimamos e como sai das escolhas

1. O modelo (McFadden, 1974) supõe que o médico dá uma utilidade a cada vaga, U_iv = β₁·bolsa + β₂·distância +
   β₃·IVS + β₄·X + α(par de UFs) + ε_iv (o erro no fim, como na forma usual), e lista em 1º a de maior utilidade.
   **Não observamos U**; observamos só qual vaga foi a 1ª opção. β·x (tudo menos o ε) é a parte que observamos; ε, a
   que não.
2. Se o ε de cada vaga é independente, com distribuição de valor extremo, a chance de a vaga v ser a 1ª opção é
   P(v) = exp(β·x_v) ÷ soma de exp(β·x_k) nas vagas do candidato. É a equação que estimamos. A probabilidade é escrita
   sobre a parte observada, não sobre U inteiro (o erro da banca 2 foi escrevê-la sobre U). α são 254 parâmetros, um
   efeito fixo por par UF de trabalho × UF da vaga: por isso α (a letra usual de efeito fixo), e não um β₅ único.
3. Por máxima verossimilhança, os pesos que melhor explicam
   as 1ªs opções observadas. **Os pesos saem das escolhas** (preferência revelada). Na estimação, o IVS entra como reta
   com dobras nos cortes 0,300 e 0,400 (spline linear contínuo, sem salto); no slide aparece como β₃·IVS.
4. O que **não** sai: o nível do valor (só diferenças entre vagas do mesmo candidato importam) nem a sua unidade (a
   escala é fixada pela variância do ε). Por isso β₁ = 0,077 sozinho não tem leitura em reais nem em "utilidade".
5. O que tem leitura: a **razão de chances entre duas vagas**, P(A) ÷ P(B) = exp(β·x_A − β·x_B), em que o denominador se
   cancela. Duas vagas iguais exceto +R$ 5 mil: e^(5β₁) = e^0,385 = **1,47**. E 5β₁ ÷ |β₂| × 100 = **75 km**.

**Métrica final:** a razão de chances por +R$ 5 mil (×1,47); a tradução para a política é a equivalência em km (75 km).

## 2. Ordem dos slides (32)

| # | Origem | Seção | Slide |
|---|---|---|---|
| 1–2 | grupo 1–2 | — | capa; sumário |
| 3 | grupo 3 | Motivação | Escassez de especialistas já é tratada como urgência sanitária |
| 4–6 | grupo 4–6 | Motivação | Vulnerabilidade social define o valor da bolsa do PMM-E |
| 7 | grupo 7 | Motivação | Política direciona incentivos aos territórios mais vulneráveis |
| 8–10 | grupo 8–10 | — | sumário; pergunta; sumário |
| 11 | grupo 11 | Literatura | Modelo combina dois elementos da teoria |
| 12–13 | novos | Literatura | Cadeia causal: da bolsa aos desfechos na saúde |
| 14 | grupo 13 | — | sumário |
| 15 | novo | Hipótese | Maior remuneração, maior chance de ser escolhida |
| 16–17 | grupo 15–16 | Base de Dados | sumário; Dados ligam os editais do PMM-E ao CNES |
| 18 | novo | Base de Dados | Cada candidato vira uma linha por vaga possível |
| 19 | grupo 17 | Análise Descritiva | Candidatos escolhem perto de onde trabalham |
| 20 | grupo 18 | — | sumário |
| 21 | novo | Metodologia | Modelo: logit condicional da 1ª opção |
| 22 | novo | Metodologia | Método passo a passo: da escolha à razão de chances |
| 23 | novo | Metodologia | Estimação: de onde vem o β |
| 24 | novo | Identificação | Identificação: as premissas do logit condicional |
| 25 | grupo 23 | — | sumário |
| 26 | novo | Resultados | Resultados: +R$ 5 mil multiplicam a chance por 1,47 |
| 27 | novo | Robustez | Robustez: ×1,47 se mantém com mais dados |
| 28 | novo | Discussão | Conclusão: bolsa pesa na escolha, mas pouco (com quem ocupa a vaga) |
| 29 | novo | Discussão | Limitações |
| 30–32 | grupo 31–33 | — | Q&A; anexo 1; anexo 2: bolsa segue exatamente o IVS do município |

**Ideias do deck v4.1 de um colega, desligadas** (`COM_IDEIAS_COLEGA = False` no gerador): o slide "Cada médico
escolhe a vaga que mais vale a pena" (antes do modelo) e os anexos 3 (modelo formal) e 4 (por que não outro método),
§3.5a, §3.13 e §3.14. Pedido do autor de 14/11: esta versão vai para o colega conciliar com a dele; para juntar, basta
ligar a chave (35 slides).

**Fora** (slides do grupo): 12 (rascunho em branco), 14 (hipótese em sobreposição), 19–20 (equação da utilidade e
duplicata), 21 (oculto), 22 (identificação), 24–26 (resultados, "incentivo limitado", tabela), 27 (metade, fundido na
conclusão), 28 (robustez, refeito), 29–30 (conclusão e limitações, refeitas). As caixas de comentário do grupo saem.

**Regras de forma (pedidos do autor de 14/11):** título com a mensagem e sem artigo no começo; título centrado na faixa
verde; corpo curto e letra grande; detalhe, fórmula e número de apoio nas notas; cautelas na tela em forma curta;
"cardápio" fora da tela (é "vagas possíveis"); âmbar marca o que o trabalho estima e observa e o que muda no exemplo.

## 3. Conteúdo de cada slide alterado ou novo

### 3.1 Slides do grupo

- **3, 4–6, 11, 16, 33:** títulos sem artigo (o 33 vira "Anexo 2: bolsa segue…") no começo; títulos centrados na faixa (vinham colados no topo).
- **4–6:** faixas da bolsa pelo IVS efetivo ("IVS acima de 0,400 / de 0,301 a 0,400 / até 0,300"; cortes do portão R1);
  "valor", não "piso"; "remuneração"; sem o item 11.1.4 (errata E10).
- **7 e 9:** "médicos" com acento na manchete. **9:** pergunta "Uma bolsa maior aumenta a chance de uma vaga ser a 1ª
  opção do médico?" (decisão do autor de 11/11). **Sumários:** "Modelo e identificação".
- **17 (dados):** "Local de trabalho anterior" no lugar de "Origem do médico" (banca de 04/11); linha da tabela "Com
  local anterior e região"; amostra do modelo 5.417 (o principal; 5.421 é o modelo base).
- **19 (descritiva; pedido de 14/11):** histograma da distância à esquerda e barras de localização à direita. Os
  cartões de números saíram (repetiam os gráficos); no lugar, "Como montamos esta análise": quem (5.425 candidatos
  com 1ª opção nos ciclos 1–3 e local de trabalho anterior conhecido; ESC_N de `numeros_banca2.json`), distância
  (do município do vínculo no CNES antes da inscrição ao da vaga posta em 1º) e onde (mesma UF, região de saúde ou
  município); títulos "I. A que distância fica a 1ª opção" e "II. Onde fica a 1ª opção"; nada
  sobre o modelo (é descritiva).
- **32 (anexo):** índice da soma t = 0; sem o altruísmo (α fica só para o par de UFs); "pela bolsa (B)" e "decide qual
  vaga o médico escolhe" (decisões do doc 02).
- Página 11 sem quebra no número.

### 3.2 Cadeia causal (12–13)

Etapa 1, regra: IVS do município → bolsa (R$ 10/15/20 mil). Etapa 2, escolha do médico: **remuneração primeiro**
(eleva o valor; Moehling et al., 2020), depois custo de viver ali (Redding & Rossi-Hansberg, 2017) e de trabalhar ali
(Choné & Ma, 2011); as três chegam ao **valor da vaga** (não observado) → **1ª opção** (observada). Em âmbar, a
remuneração (o que estimamos) e a 1ª opção (o que observamos). Faixa grande: "O que estimamos: o peso da remuneração na
chance de a vaga ser a 1ª opção; chance = probabilidade de o médico pôr a vaga em 1º lugar". **Sem número de
resultado** (pedido de 14/11). Etapa 3, da vaga à saúde, "fora do que estimamos": apagada no 12, inteira no 13.

### 3.3 Hipótese (15)

Frase numa linha: "A vaga que paga mais tem mais chance de ser a 1ª opção do médico" (entre vagas do mesmo curso, na
mesma UF, iguais no resto). Exemplo real em forma de quadro: Araçuaí e Itamarandiba (MG, ciclo 2) com IVS (0,397 e
0,401) e distância (169 e 175 km) em cinza, "≈ igual", e a bolsa (R$ 15 mil e R$ 20 mil) em âmbar, "+R$ 5 mil".
Hipótese no exemplo: chance (Itamarandiba) > chance (Araçuaí). Observação: "medimos a escolha de quem se inscreveu, não
a chegada de médicos ao município".

### 3.4 Linhas candidato × vaga (18)

O mesmo candidato em todas as linhas, em negrito (CRM 123456/MG, ilustrativo: a base não guarda identificação); y = 1
em Brasília de Minas; "… mais 219 vagas não escolhidas por ele". À direita, a base como conta: 5.417 candidatos × ≈ 107
vagas = 578.998 linhas. Faixa de transição: "Assim, para cada candidato temos todas as vagas que ele podia escolher e
qual ele escolheu. A seguir: onde ficam essas escolhas." O funil (5.714 → 5.425 → 5.421 → 5.417) e as linhas
(932.577 → 578.998, saem pares de UFs sem nenhuma 1ª opção) ficam nas notas.

### 3.5a Intuição: três vagas (desligado; seria o 21)

Pedido de 14/11 (rodada 6), a partir do deck v4.1 de um colega do grupo: porta de entrada do logit antes da equação.
Faixa: "Não sabemos o que o médico pensa. Vemos só a vaga que ele pôs em 1º lugar." Três etapas: (1) vê a lista de
vagas do seu curso: vagas A (R$ 10 mil, 50 km de onde trabalha), B (R$ 15 mil, 50 km) e C (R$ 15 mil, 125 km); (2)
pesa a favor (bolsa maior, perto), contra (longe, município sem estrutura) e o que não vemos (família, gosto); (3)
escolhe a que mais vale a pena; chance de cada vaga: A 29%, B 42%, C 29%. "B ganha de A pela bolsa; C paga como B,
mas fica 75 km mais longe: a distância anula a bolsa extra." Embaixo, a analogia do apartamento e "O que queremos
descobrir: quanto a bolsa pesa nessa escolha". **Vagas inventadas; chances calculadas no script com os pesos do VL-1**
(β₁ = 0,077 por R$ 1 mil, β₂ = −0,514 por 100 km; C fica a 50 + 75 km); o script para se B ÷ A não for e^(5β₁) ou se
A e C diferirem mais de 0,5 p.p.

### 3.5 Modelo (21)

Equações sem itálico (Montserrat). ① "Chance de a vaga v ser a 1ª opção do candidato i": P = exp(V_iv) ÷ soma de
exp(V_ik) em todas as vagas k de i. ② "Valor da vaga v para o candidato i": U_iv = V_iv + ε_iv, com V_iv = β₁·bolsa +
β₂·dist + β₃·IVS + β₄·X + α_UF(i),UF(v) ("V: a parte que observamos · ε: a que não observamos"). Abaixo de ②, em
âmbar: "Ligação: vemos só qual vaga tem o maior U (a 1ª opção). Supondo ε de valor extremo, a chance disso é ①,
calculada com o V de ②". Tabela "O que cada termo faz", com o
regressor em destaque: bolsa (TESTADO), distância, IVS, X (CONTROLE), par de UFs (FIXO). "O que se estima" pequeno.
"Por que este modelo" grande, em duas partes: o método (logit condicional, McFadden, 1974, Nobel de Economia de 2000;
compara as vagas do mesmo médico, o que é dele sai da conta; com a bolsa por regra com corte, a forma mais simples
basta) e onde a mesma família é usada (Bobba et al., 2026: logit multinomial, professores no Peru, bônus que salta em
cortes; Costa, Nunes & Sanches, 2024: logit com coeficientes aleatórios, médicos no Brasil; doc 11 da banca 2) e
"outros métodos: anexo 4".

### 3.6 Método passo a passo (22)

Seis passos em três cores com legenda: base de dados (1 vagas, 2 escolha), estimação (3 valor, 4 chance, 5 pesos),
métrica (6 chance (A) ÷ chance (B)). Exemplo real com letra grande: Araçuaí 2,53% e Itamarandiba 3,62%; 3,62 ÷ 2,53 =
1,43 = ×1,47 (bolsa) × 0,97 (6 km a mais) × 1,00 (o resto); só as duas: 59% contra 41%.

**Regra de escolha do exemplo** (fixa, sem olhar a escolha): entre todos os candidatos e pares de vagas da UF onde o
candidato trabalhava com bolsas que diferem em R$ 5 mil, o par mais parecido no resto. Script:
`scripts/apresentacao/gerar_exemplo_logit_real.py`; saída sem município de origem nem identificador do candidato.

### 3.7 Estimação (23)

Dois cartões: **a variação que usamos** (a bolsa salta nos cortes; o IVS entra sem salto; a comparação é dentro da
mesma UF: 260 pares, 5.345 candidatos) e **o que comparamos** (✓ vagas do mesmo candidato; ✓ vagas da mesma UF; ✗ não
dentro do município, porque a bolsa é igual no município inteiro). Faixa "Em resumo": o β mede quanto a chance muda
quando só a bolsa salta, comparando vagas do mesmo candidato na mesma UF; "A seguir: o que precisamos supor para ler
isso como efeito da bolsa". **A ressalva "exploratório" saiu deste slide e foi para Limitações** (pedido do autor de
14/11: é limitação, não parte do método). **A incerteza saiu da tela** (pedido de 14/11) e fica nas notas e no doc 04:
erro-padrão agrupado por curso × ciclo (55 grupos; EP 0,025 contra 0,013), score bootstrap p = 0,011, Holm p = 0,005;
perto do corte ×1,28 (IC 0,95 a 1,72).

**Exploratório não é "não causal"** (dito em Limitações). O desenho (salto da bolsa no corte, dentro da mesma UF) é o mesmo; o que muda é
o estatuto: a especificação com o par de UFs não estava no plano pré-registrado (adendo 52e, pós-resultado). Um
resultado confirmatório exigiria repetir o teste em dados novos (por exemplo, o ciclo 3 maduro). E o contraste é o
pacote do corte, condicional a se candidatar.

### 3.8 Identificação (24)

Quatro premissas, cada uma com explicação na linha inteira: escolha sincera (SUPOSIÇÃO); todas as vagas conhecidas
(SUPOSIÇÃO); bolsa sem relação com o que não medimos (EM PARTE: segue a regra do IVS, mas é um pacote no corte); vagas
próximas como substitutas (β ESTÁVEL: vagas da mesma região concorrem mais entre si; num modelo que permite isso,
testado no modelo base, o peso da bolsa quase não muda). Nas notas: é a premissa de alternativas independentes (IIA);
aninhado λ = 0,45, β 0,043 contra 0,042, rodado sem o par de UFs.

### 3.9 Resultados (26)

Três cartões no topo: ×1,47 (+R$ 5 mil, na mesma UF; IC 1,15 a 1,89), ≈ 75 km, ×1,90 só no ciclo 2 (ciclos 1 e 3: IC
inclui 1). Embaixo, a figura "Para comparar: o que mais pesa na escolha da vaga" (bolsa ×1,47; +100 km ×0,60; mesma
região de saúde ×3,01; mesmo município ×1,80; letra grande) e a leitura: "A bolsa pesa, mas a proximidade pesa mais
… Por isso falamos em incentivo limitado."

### 3.10 Robustez (27)

Figura em quatro grupos, na ordem da leitura: principal (mesma UF, ciclos 1–3); outras medidas com todos os dados
(distância em log ×1,45; região anterior × UF ×1,49); só parte dos dados (perto do corte ×1,28; ciclos 1, 2 e 3);
plano original (sem fixar a UF ×1,25). À direita, um cartão por grupo, na mesma ordem, e a legenda verde/cinza.

### 3.11 Conclusão com quem ocupa a vaga (28)

Resposta (×1,47 ≈ 75 km; forte só no ciclo 2); à esquerda, "quem ocupa a vaga (descritivo)": 51% já tinham vínculo no
município (IC 48% a 54%) e +6,6 h/sem no CNES num programa de 20 h (IC +5,4 a +7,8); "Dá para afirmar" e "Não dá para
afirmar"; "Para a política". Funde os antigos slides "metade de quem ocupa a vaga" e "conclusão" (pedido de 14/11).

### 3.12 Limitações (29)

Duas caixas: o que o resultado não mostra (escolher não é ir; pacote, não só dinheiro; local anterior pelo CNES) e
quão firme ele é, cada item com o que implica: "Mesma UF: decidido depois dos dados → exploratório: o desenho é o
mesmo, mas não foi o teste planejado; confirmar exige dados novos"; "Plano original, sem fixar a UF: ×1,25 → IC
contém 1"; "Só o ciclo 2 é forte". Nas notas, a fala completa: exploratório não quer dizer "não causal"; o par de UFs
foi escolhido depois do modelo base (adendo 52e); confirmar exigiria o ciclo 3 maduro; dizer antes de a banca
perguntar.

### 3.13 Anexo 3: o modelo formal (desligado)

Quatro cartões em sequência: (1) valor não observado, U_iv = V_iv + ε_iv; (2) escolha observada, y_iv = 1 se U_iv >
U_ik para toda outra vaga k; (3) chance, P(y_iv = 1) = exp(V_iv) ÷ soma de exp(V_ik), se ε é de valor extremo, pesos
por máxima verossimilhança; (4) razão de chances, P(B) ÷ P(A) = exp(5β₁) = exp(5 × 0,077) = 1,47. Tabela com as vagas
A, B e C do slide 21 (V, P, y, razão contra A: 28,8%, 42,4% e 28,8%; 42,4 ÷ 28,8 = 1,47). Cartão: "y é o resultado. U é
o mecanismo." (como no logit binário, um valor latente e um limiar, aqui o maior U entre as outras vagas; β sem unidade
própria, por isso lemos ×1,47 ou 75 km).

### 3.14 Anexo 4: por que este modelo e não outro (desligado)

Conteúdo do doc 11 da banca 2 ("Por que não um método mais simples?" e "Literatura"), em cinco linhas com o que faz e
por que não: RDD por vaga (feita; IC contém zero; perde a variação dentro do candidato); MQO 0/1 com efeito fixo do
médico (chance ≈ 1% por vaga; prevê fora de [0, 1]); Poisson das contagens (mesmo β; Guimarães, Figueiredo e
Woodward, 2003); logit misto ou aninhado (servem quando o salário é de mercado ou dá para recusar tudo; aqui ficaram
como teste extra, no modelo base); e o nosso, o logit condicional (por que sim).

### 3.15 Rodada 7 (14/11): comentários do autor sobre a versão de 32 slides

Prevalece sobre o texto acima onde houver conflito.

- **18:** a faixa termina em "qual ele escolheu."; sem "A seguir".
- **21 (modelo):** ② "Utilidade da vaga v para o candidato i": U_iv = β₁·bolsa_v + β₂·dist_iv + β₃·IVS_v + β₄·X_iv +
  α_UF(i),UF(v) + ε_iv, **erro no fim**; legenda "β·x_iv: tudo menos o ε, a parte de U que observamos · ε_iv: a que
  não observamos". ① P(i escolhe v) = exp(β·x_iv) ÷ soma de exp(β·x_ik) em todas as vagas k de i (sem V; a chance não
  se escreve sobre U inteiro). Ligação: "…a chance disso é ①, que depende só da parte observada de ②". Par de UFs: "254
  efeitos fixos, um por par". "O que se estima: os pesos β₁ a β₄ e os efeitos fixos α". "Por que este modelo" ocupa o
  quadro inteiro, letra 13–14: logit condicional (McFadden, 1974; Nobel de 2000); compara as vagas do mesmo médico; a
  bolsa vem de regra, a versão simples basta; **em saúde**, só Costa, Nunes e Sanches (2024), sem Bobba et al. (que fica
  nas notas e no doc 04).
- **22 (passos):** 3 "Utilidade: U = pesos × características + ε"; 4 "Chance: exp(U sem ε) ÷ soma das vagas dele";
  "Se fossem as únicas duas vagas: 59% contra 41%".
- **23 (estimação):** sem "Atenção" e sem "exploratório". Cartão I, "De onde vem a variação da bolsa", sem linguagem de
  RDD: a bolsa é fixada por regra (R$ 10, 15 ou 20 mil, pela faixa de IVS); o IVS também está no modelo; comparamos
  vagas da mesma UF com bolsas diferentes (260 pares, 5.345 candidatos). "Em resumo: o β mede quanto a chance de uma
  vaga muda com a bolsa, comparando vagas do mesmo candidato, na mesma UF, com o IVS controlado." O spline com dobras
  nos cortes fica nas notas.
- **24 (identificação):** grade 2 × 2 de cartões numerados, cada um com o termo usual, uma frase simples e a etiqueta:
  escolha sincera (SUPOSIÇÃO); conjunto de escolha conhecido (SUPOSIÇÃO); exogeneidade da bolsa (VALE EM PARTE);
  independência de alternativas, IIA (TESTADA: logit aninhado no modelo base, β quase igual).
- **26–29: o plano original (modelo sem o par de UFs, ×1,25) sai da apresentação** (tela e notas; pedido do autor). A
  figura de robustez fica com dois grupos além do principal (outras medidas; só parte dos dados) e dois cartões. A
  resposta, se a banca perguntar, está no doc 04 (pergunta 7).
- **28 (conclusão):** "Para a política: pagar mais muda a escolha entre vagas próximas." / "Não mostramos que atraia
  médicos de longe." em duas linhas; "Que o efeito é só da bolsa" no lugar de "é um pacote".
- **29 (limitações), em termos usuais de economia empírica:** "O que o resultado não mede": escolha, não alocação;
  tratamento composto; origem pelo CNES. "Quão forte é o resultado": especificação escolhida após os dados → resultado
  exploratório, confirmar exige dados novos; heterogeneidade entre ciclos → significativo só no ciclo 2, validade
  externa limitada; escolha sincera → premissa não testável.

### 3.16 Rodada 8 (14/11): conclusão e versão conciliada

- **28 (conclusão, nossa versão):** "Para a política" na largura toda, letra 17, em duas linhas; em "Dá para afirmar" e
  "Não dá para afirmar", os termos-chave em negrito (bolsa maior é preferida; peso é moderado; metade… já estava no
  município; mais médicos ao município; só da bolsa; todo ciclo).
- **Versão conciliada** (`python scripts/apresentacao/gerar_deck_banca_final_grupo.py --com-colega`, saída
  `deck_banca_final_grupo_conciliado.pptx` e `.pdf`, 35 slides): liga as ideias do deck do colega. (a) O slide das vagas
  A, B e C fica enxuto: faixa "Não vemos o que o médico pensa, só a vaga que ele pôs em 1º lugar."; três cartões (lista
  de vagas; prós e contras; a chance de cada vaga: 29%, 42%, 29%) e "Nossa pergunta: quanto a bolsa pesa?". (b) O slide
  de resultado é o do colega: "Ficar perto de onde trabalha pesa mais que a bolsa", com a figura de seis fatores
  (`figuras/coeficientes_vl1_seis.png`: mesma região ×3,01; mesmo município ×1,80; bolsa ×1,47; população em dobro
  ×1,10; capital ×0,73, IC inclui 1; +100 km ×0,60; todos do VL-1), as três contas (5 × 0,077 = 0,385; exp(0,385) =
  ×1,47; 0,385 ÷ 0,514 × 100 = 75 km) e a leitura. (c) Os anexos 3 e 4. A nossa versão (32 slides, sem as ideias do
  colega) continua em `deck_banca_final_grupo.pptx`.

## 4. Histórico de revisões

- **11/11:** deck sobre a versão do grupo (32 slides); pergunta nova; "valor da bolsa"; anexo com t = 0.
- **14/11, rodada 1:** entrada do grupo de 14/11; slide de estimação; funil das alternativas; aninhado identificado como
  do modelo base.
- **14/11, rodada 2:** revisão no PowerPoint: anexo sem altruísmo; "local de trabalho anterior"; amostra 5.417.
- **14/11, rodada 3:** −42% de palavras na tela nos slides gerados; detalhe nas notas.
- **14/11, rodadas 4 e 5 (comentários do autor slide a slide):** títulos sem artigo e centrados; fontes públicas;
  âmbar para o que estimamos e observamos; sem prévia de resultado na cadeia; exemplo da hipótese em quadro; CRM
  ilustrativo; descritiva reordenada; equações sem itálico, com ε e β₁…β₄; incerteza fora da tela; premissas em linha
  inteira; resultados e robustez refeitos; "metade" fundido na conclusão (32 slides).
- **14/11, rodada 6 (ideias do deck v4.1 de um colega; pedido do autor):** "exploratório" sai da estimação e vai para
  Limitações; slide de intuição com as vagas A, B e C antes do modelo; "Ligação" com o y observado; anexos 3 (modelo
  formal, y e U) e 4 (por que não outro método); 35 slides. Do v4.1 **não** entram: "origem ×11 contra bolsa ×1,57"
  (decisão do autor de 28/10), a curva da verossimilhança desenhada à mão (não sai de script) e o que já tinha sido
  corrigido (origem, cardápio, 5.421, SUPOSTO, arquivos internos nas fontes).
- **14/11, rodada 7 (comentários do autor sobre a versão de 32 slides):** §3.15. As ideias do colega ficam desligadas
  (esta versão vai para ele conciliar); "exploratório" só em Limitações; plano original fora; U com erro no fim;
  identificação em grade; limitações em termos usuais; 32 slides.
- **14/11, rodada 8:** conclusão com "Para a política" maior e termos-chave em negrito; versão conciliada separada
  (`--com-colega`), com o slide de resultado do colega e o slide A, B e C enxuto (§3.16).

## 5. Para o grupo decidir

1. **Slide 23 (estimação):** fica no corpo ou vai para o apêndice? Com ele, a Metodologia tem três slides (21–23).
2. **Ideias do colega (v4.1):** juntar na conciliação (ligar `COM_IDEIAS_COLEGA`).
3. **Roteiro de fala:** depende do tempo da banca final, ainda não informado.
