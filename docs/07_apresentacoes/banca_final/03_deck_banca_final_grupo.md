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

1. O modelo (McFadden, 1974) supõe que o médico dá um valor a cada vaga, U = V + ε, e lista em 1º a de maior valor.
   **Não observamos U nem V**; observamos só qual vaga foi a 1ª opção. V é a parte que observamos; ε, a que não.
2. Se o ε de cada vaga é independente, com distribuição de valor extremo, a chance de a vaga v ser a 1ª opção é
   P(v) = exp(V_v) ÷ soma de exp(V_k) nas vagas do candidato. É a equação que estimamos. A probabilidade é escrita
   sobre V, não sobre U (o erro da banca 2 foi escrevê-la sobre U).
3. V = β₁·bolsa + β₂·distância + β₃·IVS + β₄·X + α(par de UFs). Por máxima verossimilhança, os pesos que melhor explicam
   as 1ªs opções observadas. **Os pesos saem das escolhas** (preferência revelada). Na estimação, o IVS entra como reta
   com dobras nos cortes 0,300 e 0,400 (spline linear contínuo, sem salto); no slide aparece como β₃·IVS.
4. O que **não** sai: o nível do valor (só diferenças entre vagas do mesmo candidato importam) nem a sua unidade (a
   escala é fixada pela variância do ε). Por isso β₁ = 0,077 sozinho não tem leitura em reais nem em "utilidade".
5. O que tem leitura: a **razão de chances entre duas vagas**, P(A) ÷ P(B) = exp(V_A − V_B), em que o denominador se
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
| 30–32 | grupo 31–33 | — | Q&A; anexo 1; Bolsa segue exatamente o IVS do município |

**Fora** (slides do grupo): 12 (rascunho em branco), 14 (hipótese em sobreposição), 19–20 (equação da utilidade e
duplicata), 21 (oculto), 22 (identificação), 24–26 (resultados, "incentivo limitado", tabela), 27 (metade, fundido na
conclusão), 28 (robustez, refeito), 29–30 (conclusão e limitações, refeitas). As caixas de comentário do grupo saem.

**Regras de forma (pedidos do autor de 14/11):** título com a mensagem e sem artigo no começo; título centrado na faixa
verde; corpo curto e letra grande; detalhe, fórmula e número de apoio nas notas; cautelas na tela em forma curta;
"cardápio" fora da tela (é "vagas possíveis"); âmbar marca o que o trabalho estima e observa e o que muda no exemplo.

## 3. Conteúdo de cada slide alterado ou novo

### 3.1 Slides do grupo

- **3, 4–6, 11, 16, 33:** títulos sem artigo no começo; títulos centrados na faixa (vinham colados no topo).
- **4–6:** faixas da bolsa pelo IVS efetivo ("IVS acima de 0,400 / de 0,301 a 0,400 / até 0,300"; cortes do portão R1);
  "valor", não "piso"; "remuneração"; sem o item 11.1.4 (errata E10).
- **7 e 9:** "médicos" com acento na manchete. **9:** pergunta "Uma bolsa maior aumenta a chance de uma vaga ser a 1ª
  opção do médico?" (decisão do autor de 11/11). **Sumários:** "Modelo e identificação".
- **17 (dados):** "Local de trabalho anterior" no lugar de "Origem do médico" (banca de 04/11); linha da tabela "Com
  local anterior e região"; amostra do modelo 5.417 (o principal; 5.421 é o modelo base).
- **19 (descritiva; pedido de 14/11):** histograma da distância à esquerda e barras de localização à direita; cartões
  em números na ordem dos gráficos: 50% a até 51 km; 75% a até 189 km; 79% na mesma UF; 36% no próprio município
  (ESC_* de `numeros_banca2.json`); títulos "I. A que distância fica a 1ª opção" e "II. Onde fica a 1ª opção"; nada
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

### 3.5 Modelo (21)

Equações sem itálico (Montserrat). ① "Chance de a vaga v ser a 1ª opção do candidato i": P = exp(V_iv) ÷ soma de
exp(V_ik) em todas as vagas k de i. ② "Valor da vaga v para o candidato i": U_iv = V_iv + ε_iv, com V_iv = β₁·bolsa +
β₂·dist + β₃·IVS + β₄·X + α_UF(i),UF(v) ("V: a parte que observamos · ε: a que não observamos"). Abaixo de ②, em
âmbar: "Ligação: supondo ε de valor extremo, a chance ① sai do valor V de ②". Tabela "O que cada termo faz", com o
regressor em destaque: bolsa (TESTADO), distância, IVS, X (CONTROLE), par de UFs (FIXO). "O que se estima" pequeno.
"Por que este modelo" grande, em duas partes: o método (logit condicional, McFadden, 1974, Nobel de Economia de 2000;
compara as vagas do mesmo médico, o que é dele sai da conta; com a bolsa por regra com corte, a forma mais simples
basta) e onde a mesma família é usada (Bobba et al., 2026: logit multinomial, professores no Peru, bônus que salta em
cortes; Costa, Nunes & Sanches, 2024: logit com coeficientes aleatórios, médicos no Brasil; doc 11 da banca 2).

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
dentro do município, porque a bolsa é igual no município inteiro). Faixa "Atenção": comparar só dentro da mesma UF foi
decidido depois de ver o primeiro modelo (×1,25; IC 0,98 a 1,61); por isso o ×1,47 é exploratório: aponta numa
direção, mas não foi o teste planejado. **A incerteza saiu da tela** (pedido de 14/11) e fica nas notas e no doc 04:
erro-padrão agrupado por curso × ciclo (55 grupos; EP 0,025 contra 0,013), score bootstrap p = 0,011, Holm p = 0,005;
perto do corte ×1,28 (IC 0,95 a 1,72).

**Exploratório não é "não causal".** O desenho (salto da bolsa no corte, dentro da mesma UF) é o mesmo; o que muda é
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
quão firme ele é (fixar a UF veio depois dos dados; sem fixar a UF ×1,25; só o ciclo 2 é forte), cada item com o que
implica.

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

## 5. Para o grupo decidir

1. **Slide 23 (estimação):** fica no corpo ou vai para o apêndice? Com ele, a Metodologia tem três slides (21–23).
2. **Roteiro de fala:** depende do tempo da banca final, ainda não informado.
