# 03. Deck da banca final sobre a versão do grupo de 11/11/2026

> **Pedido do autor (11/11/2026, noite):** partir do deck atual do grupo (`PEE - BANCA FINAL`, 33 slides, 1 oculto) e
> comunicar melhor o trabalho com o que foi feito no deck da banca final ([02](02_deck_banca_final.md)), seção por seção.<br>
> **Derivado:** `output/apresentacao_banca_final/deck_banca_final_grupo.pptx` e `.pdf` (32 slides), gerado por
> `scripts/apresentacao/gerar_deck_banca_final_grupo.py`. O deck é derivado deste documento: divergência é erro do deck.<br>
> **Entrada:** `grupo/deck_grupo_banca_final_1111.pptx` (cópia sem alteração; SHA-256 `4f645142…44cd5`).<br>
> **Números:** todos lidos de `output/` (VL, VG, P1, S57, portão R1, `exemplo_logit_real.json`); nenhum digitado.<br>
> **Convive com o doc 02:** o deck de 25 slides do doc 02 continua gerado pelo seu script; este é outro arquivo.

## 1. O ponto-chave: o que estimamos e como sai das escolhas

**Estamos estimando utilidade a partir da escolha?** Em parte, e é preciso dizer exatamente qual parte.

1. O modelo (McFadden, 1974) supõe que o médico dá um valor a cada vaga, U = V + ε, e lista em 1º a de maior
   valor. **Não observamos U nem V**; observamos só qual vaga foi a 1ª opção.
2. Se o ε de cada vaga é independente com distribuição de valor extremo, a chance de a vaga v ser a 1ª opção é
   P(v) = exp(V_v) / Σ_k exp(V_k), somando nas vagas do cardápio do candidato. Esta é a equação que estimamos.
   A equação antiga do slide (U = … + ε e a probabilidade escrita sobre U) misturava as duas coisas: era o erro.
3. V = β·bolsa + γ·distância + f(IVS) + α(par de UFs) + θ·X. Por máxima verossimilhança, o computador acha os pesos
   (β, γ, …) que tornam as 1ªs opções observadas as mais prováveis. **Os pesos saem das escolhas** (preferência
   revelada).
4. O que **não** sai: o nível do valor de uma vaga (só diferenças entre vagas do mesmo cardápio importam) nem a sua
   unidade (a escala é fixada pela variância do ε). Por isso β = 0,077 sozinho não tem leitura em reais nem em
   "utilidade".
5. O que tem leitura: a **razão de chances entre duas vagas**. P(A) ÷ P(B) = exp(V_A − V_B): o cardápio (o
   denominador) se cancela. Duas vagas iguais exceto +R$ 5 mil: P(A) ÷ P(B) = e^(5β) = e^0,385 = **1,47**. A razão
   entre coeficientes também tem leitura: 5β ÷ |γ| × 100 = **75 km**.

**Por que a razão de chances e não o coeficiente?** É o mesmo número em outra escala: ln(1,47) = 0,385 = 5β, e o
teste é o mesmo (IC da razão exclui 1 ⇔ IC do β exclui 0). No logit condicional, a razão entre as chances de duas
vagas é a leitura natural: é exata, vale para qualquer par e não depende do tamanho do cardápio. A diferença de
probabilidade em pontos percentuais dependeria do cardápio (com ≈ 107 vagas, cada chance é pequena, como no
exemplo real: 2,53% e 3,62%). **Métrica final do trabalho:** a razão de chances por +R$ 5 mil (×1,47); a tradução
mais intuitiva para a política é a equivalência em km (75 km). O deck mostra o β, a conta e as duas leituras.

**Consequência para a cadeia causal:** o "valor da vaga para o médico" (utilidade) entra no diagrama como **não
observado**, a 1ª opção como **observada**, e a métrica (×1,47 ≈ 75 km) aparece numa faixa de destaque entre as duas.

## 2. Ordem dos slides (32)

| # | Origem | Seção | Slide | O que mudou |
|---|---|---|---|---|
| 1–2 | grupo 1–2 | — | capa; sumário | nada |
| 3 | grupo 3 | Motivação | escassez | nada |
| 4–6 | grupo 4–6 | Motivação | IVS e bolsa (3 etapas) | faixas pelo IVS efetivo (§3.1); "remuneração"; sem item 11.1.4 |
| 7 | grupo 7 | Motivação | política direciona incentivos | nada |
| 8–10 | grupo 8–10 | — | sumário; pergunta; sumário | nada (ver §4, ponto 1) |
| 11 | grupo 11 | Literatura | o modelo combina dois elementos | nada |
| 12–13 | novos | Literatura | cadeia causal (etapas 1–2; depois 1–3) | §3.2 |
| 14 | grupo 13 | — | sumário | nada |
| 15 | novo | Hipótese | maior remuneração, maior chance de ser escolhida | §3.3 |
| 16–17 | grupo 15–16 | Base de Dados | sumário; dados ligam editais ao CNES | nada |
| 18 | novo | Base de Dados | cada candidato vira uma linha por vaga | §3.4 |
| 19 | grupo 17 | Análise Descritiva | 3 em 4 escolhem uma vaga a até 189 km | só o título |
| 20 | grupo 18 | — | sumário | nada |
| 21 | novo | Metodologia | modelo: logit condicional da 1ª opção | §3.5 |
| 22 | novo | Metodologia | método passo a passo, com exemplo real | §3.6 |
| 23 | novo | Identificação | as premissas do logit condicional | §3.7 |
| 24 | grupo 23 | — | sumário | nada |
| 25 | novo | Resultados | +R$ 5 mil multiplicam a chance por 1,47 | §3.8 |
| 26 | novo | Robustez | o ×1,47 se mantém nas variantes com mais dados | §3.9 |
| 27 | novo | Discussão | metade de quem ocupa a vaga já trabalhava no município | §3.10 |
| 28 | novo | Discussão | conclusão: a bolsa pesa na escolha, mas pouco | §3.11 |
| 29 | novo | Discussão | limitações (duas caixas) | §3.12 |
| 30–32 | grupo 31–33 | — | Q&A; anexo 1; a bolsa segue o IVS | nada |

**Fora** (slides do grupo): 12 (rascunho em branco), 14 (hipótese em sobreposição), 19–20 (equação da utilidade e
duplicata), 21 (oculto), 22 (identificação), 24–26 (resultados, "incentivo limitado", tabela), 27 (metade, refeito),
28 (robustez, refeito), 29–30 (conclusão e limitações, refeitas). As caixas de comentário do grupo ("Esse tá ruim…",
"Estética ruim", "Evidenciar…", "Escolha das palavras…") saem dos slides mantidos.

## 3. Conteúdo de cada slide novo ou alterado

### 3.1 Slides 4–6 (IVS e bolsa)

Nas caixas da bolsa, "Vulnerabilidade: Muito alta / Alta / Média, baixa e muito baixa" passa a "IVS acima de 0,400 /
de 0,301 a 0,400 / até 0,300": a legenda do mapa no mesmo slide chama 0,301–0,400 de "média", e a regra efetiva
(portão R1) tem cortes em 0,300 e 0,400. A nota: "fixada, por regra, pelo IVS 2010 do município: cortes em 0,300 e
0,400". Sai "(item 11.1.4)" das fontes (é a grade do FAQ, não a aplicada; errata E10).

### 3.2 Cadeia causal (12–13)

Título: "Cadeia causal: da bolsa aos desfechos na saúde". Sem notação. Etapas:
1. **Regra:** IVS do município → bolsa (até 0,300: R$ 10 mil; 0,301–0,400: R$ 15 mil; acima de 0,400: R$ 20 mil).
2. **Escolha do médico:** primeiro o que reduz o valor — custo de viver ali (**deslocamento**, moradia e distância
   de casa; Redding & Rossi-Hansberg, 2017) e custo de trabalhar ali (**esforço**: equipe e equipamentos que faltam;
   Choné & Ma, 2011) — e depois o que eleva — remuneração (**bolsa** maior: salário esperado maior; Moehling et al.,
   2020). As três setas chegam ao **valor da vaga para o médico** (a utilidade; NÃO OBSERVADO) → **1ª opção**
   (OBSERVADA). Faixa: "O que estimamos: o peso da bolsa no valor da vaga, lido nas escolhas. +R$ 5 mil = chance ×1,47
   ≈ 75 km mais perto".
3. **Da vaga à saúde:** quantos médicos a escolhem → vaga preenchida → capacidade → produção e acesso → saúde; "fora
   do que estimamos". No slide 12 esta etapa aparece apagada; no 13, inteira.

Termos fixos, no rodapé dos dois slides e usados em todo o deck: **vaga** (estabelecimento × curso), **cardápio**
(vagas que o médico podia escolher), **1ª opção** (a vaga listada em 1º), **chance** (probabilidade de a vaga ser a
1ª opção).

### 3.3 Hipótese (15)

Frase central, em destaque: "A vaga que paga mais tem mais chance de ser a 1ª opção do médico" (comparando vagas do
mesmo curso, na mesma UF, iguais no resto). Exemplo real (o mesmo do método): um médico de Cirurgia Geral
Minimamente Invasiva que trabalhava em MG, ciclo 2, diante de Araçuaí (IVS 0,397; R$ 15 mil; 169 km) e Itamarandiba
(IVS 0,401; R$ 20 mil; 175 km). Hipótese no exemplo: chance(Itamarandiba) > chance(Araçuaí). Blocos: "O que
comparamos" e "O que não dizemos". Sem cautela; a medida passa para o slide de dados.

### 3.4 Linhas candidato × vaga (18)

Formato longo do mesmo médico (222 linhas; y = 1 em Brasília de Minas, a vaga que ele pôs em 1º). Base do modelo
principal: 578.998 linhas, 5.417 candidatos, ≈ 107 vagas por candidato (mediana 82; de 2 a 438). Funil:
5.714 com 1ª opção → 5.425 com local de trabalho anterior no CNES → 5.421 com região de saúde → 5.417 no modelo
principal (4 ficaram com uma só vaga possível depois de fixar o par de UFs). "CNES → modelo principal": o CNES dá o
ponto de partida da distância; quem não tinha vínculo médico anterior fica fora; no modelo principal saem também as
vagas de UFs que nenhum médico da mesma UF escolheu (não informam o peso da bolsa). Faixa "Medida": razão de chances
da 1ª opção por +R$ 5 mil; hipótese: maior que 1.

### 3.5 Modelo (21)

Equação do logit condicional, no estilo do grupo (Cambria Math): P(i escolhe v) = exp(V_iv) / Σ_{k ∈ cardápio de i}
exp(V_ik), com V_iv = β·bolsa_v + γ·dist_iv + f(IVS_v) + α_{UF(i),UF(v)} + θ·X_iv. "O que se estima": os pesos que
tornam as 1ªs opções observadas as mais prováveis. "Como ler cada coeficiente": P(A) ÷ P(B) = exp[β·(bolsa_A −
bolsa_B) + γ·(dist_A − dist_B) + …] e uma linha por termo (β testado; γ, f(IVS) e θ·X controles; α pareamento).
Anexo pequeno "Por que este modelo": intuição (escolha de uma entre ≈ 107; o que é do médico se cancela) e
referências — McFadden (1974; Nobel de 2000), Bobba et al. (2026), Costa, Nunes & Sanches (2024), Holmes (2005),
Scott et al. (2013) e Kolstad (2011) (docs/03_literatura_empirica/19 e 20).

### 3.6 Método passo a passo (22)

Diagrama em seis passos: cardápio → escolha (y) → valor (V) → chance (exp(V) ÷ soma) → pesos (máxima
verossimilhança) → métrica (chance(A) ÷ chance(B)). Exemplo real com os pesos estimados (VL-1 reestimado, igual ao
gravado): Araçuaí 2,53%; Itamarandiba 3,62%; 3,62 ÷ 2,53 = 1,43 = ×1,47 (bolsa) × 0,97 (6 km a mais) × 1,00 (IVS,
porte e o resto). Só as duas: 59% contra 41%. "Por que razão, e não diferença".

**Regra de escolha do exemplo** (fixa, sem olhar a escolha): entre todos os candidatos e pares de vagas da UF onde o
candidato trabalhava com bolsas que diferem em R$ 5 mil, o par mais parecido no resto (IVS × 10, distância,
vaga imediata, porte, capital, estratos, mesma região, mesmo município). Script:
`scripts/apresentacao/gerar_exemplo_logit_real.py`; saída sem município de origem nem identificador do candidato.

### 3.7 Identificação (23)

Só as premissas do logit condicional e como atendemos: escolha sincera (SUPOSTO); cardápio conhecido (SUPOSTO);
bolsa sem relação com o que não medimos (EM PARTE: regra do IVS 368/368 e 454/454, mas pacote no corte);
alternativas independentes (NÃO VALE, β ESTÁVEL: aninhado λ = 0,45; β 0,043 contra 0,042 no modelo base). Faixa: o
β vem de 260 pares de UFs e 5.345 candidatos com variação de bolsa.

### 3.8 Resultados (25)

Gráfico no lugar da tabela: cada coeficiente como "×" com IC (bolsa +R$ 5 mil ×1,47; +100 km ×0,60; mesma região
×3,01; mesmo município ×1,80), com o coeficiente escrito. Três cartões: ×1,47 (IC 1,15–1,89; Holm 0,005); 75 km;
×1,90 só no ciclo 2. Sem cautela.

### 3.9 Robustez (26)

Gráfico das variantes (VL-1, log da distância, região anterior × UF, perto do corte, por ciclo, pré-registrado).
Conclusão explícita (anotação do grupo): com todos os dados e sempre na mesma UF, ×1,45 a ×1,49; onde há menos
informação, o IC contém 1 (inconclusivo, não contrário). "Por que o × e não o coeficiente" (§1).

### 3.10 Metade de quem ocupa a vaga (27)

51% já tinham vínculo no município (IC 48%–54%); +6,6 h/sem cadastradas (IC +5,4 a +7,8). Três leituras e a nota de
descritivo. Fonte: S57_resumo.json (P4).

### 3.11 Conclusão (28)

Resposta (×1,47 ≈ 75 km; forte só no ciclo 2), "Dá para afirmar" e "Não dá para afirmar" (três itens cada) e a
leitura para a política. Funde os slides 25 e 29 do grupo.

### 3.12 Limitações (29)

Duas caixas: "O que o resultado não mostra" (escolher não é ir; pacote; local anterior pelo CNES) e "Quão firme é o
resultado" (comparação pós-resultado; sem fixar a UF ×1,25; só o ciclo 2 forte), cada item com o que implica.

## 4. Para o grupo decidir

1. **Pergunta (slide 9):** fala em "probabilidade de preenchimento das vagas"; o que testamos é a chance de a vaga
   ser a 1ª opção. Sugestão: "Uma bolsa maior aumenta a chance de uma vaga em município mais vulnerável ser a 1ª
   opção do médico?". Não foi trocada (o pedido era manter a motivação).
2. **Descritiva (slide 19):** o cartão "3 em 4…" repete o novo título; pode virar outro número.
3. **Slide 17:** "Amostra do modelo: 5.421" é a do modelo base; o principal tem 5.417 (explicado no slide 18).
