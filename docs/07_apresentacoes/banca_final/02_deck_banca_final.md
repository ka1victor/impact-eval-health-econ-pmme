# 02 — Deck da banca final: banca 1 ajustada + banca 2 pós-banca

> **Pedido do autor (09/11/2026):** juntar os slides da banca 2 com os da banca 1, adaptados às mudanças do trabalho
> para a banca 2; em seguida, "coloca na main, e ajusta os slides da banca 1 já com base neles": a banca 2 entra na
> versão revista depois da banca de 04/11/2026 ([doc 12 da banca 2](../banca2/12_revisao_pos_banca_0411.md)), e o
> feedback dessa banca vale também para a parte da banca 1.<br>
> **Estatuto:** conteúdo canônico do deck da banca final, **versão 2 (proposta)**. O `.pptx` é derivado: divergência
> entre o deck e este documento é erro do deck (`CLAUDE.md`). A versão 1 (32 slides, com o deck curto de 28/10) fica
> no histórico do Git (commit `1f72330`).<br>
> **Deck:** `output/apresentacao_banca_final/deck_banca_final.pptx` e `.pdf`, gerados por
> [`scripts/apresentacao/gerar_deck_banca_final.py`](../../../scripts/apresentacao/gerar_deck_banca_final.py), com o
> manifesto `manifesto_deck_banca_final.json` (hashes das entradas e das saídas, ordem, adaptações e slides que
> saíram, com o motivo). Conferido por `tests/test_deck_banca_final.py`.<br>
> **Entradas (só `output/`):** o deck do grupo reorganizado com o diagrama da teoria da mudança
> (`deck_proposta_reorganizada.pptx`, doc [01](01_diagrama_teoria_mudanca.md)); o deck da banca 2 revisto depois da
> banca (`output/apresentacao_banca2/deck_banca2_pos_banca.pptx`, doc 12); duas figuras do pipeline da banca 1
> (`output/apresentacao_banca1/especialistas_por_uf_extremos.png` e `vagas_ciclo1_por_regiao.png`).

> [!IMPORTANT]
> **Versão 3 (09/11/2026): a base passou a ser o deck atual do grupo** (`grupo/deck_grupo_banca_final_0911.pptx`,
> "PEE - Modelo econômico", 35 slides), no design do grupo. O diagrama da teoria vem do deck reorganizado e a banca 2
> do deck pós-banca. A ordem e os textos das seções 1 a 3 continuam valendo; os números dos slides do grupo citados
> abaixo são os do deck antigo. A correspondência nova (e o motivo de cada slide que sai) está no gerador (`ORDEM`,
> `FORA_G`) e no manifesto. Em andamento: dois slides novos com o método passo a passo e a revisão do modelo teórico.

> [!IMPORTANT]
> **Versão de 11/11/2026 (tarde): 24 slides, 15 no corpo.** Pedido do autor: "coloca de volta e não tira os que foram
> colocados pelo meu grupo; ao invés disso, condensa os seus, inclusive para deixar menos espaços em branco". Voltaram
> a escassez de especialistas (corpo) e a renda real líquida (apêndice), slides do grupo; a equação do modelo e Bobba
> et al. voltaram ao corpo (Metodologia). Os slides novos do método viraram **um só**: à esquerda, os quatro passos;
> à direita, o exemplo das três vagas com o ×1,47 e os 75 km. Redesenho (`REMOVER_FORMAS`, `redesenhar`): a hipótese
> sem o exemplo A/B (está no slide do método), com a frase e os cartões maiores; a base sem o "formato longo", com a
> tabela na largura toda; o resultado só com bolsa e distância, tabela e caixas maiores e sem a caixa do ciclo 2. Do
> deck do grupo continuam fora só os slides com erro (o "piso" do IVS com a grade do FAQ, números que não se
> reproduzem, a hipótese antiga, o slide de dados com números sobrepostos), os marcadores "X", os "EXEMPLO" de outro
> trabalho, as versões ocultas e os sumários (a decidir). As seções 1 a 3 abaixo descrevem versões anteriores; a
> ordem vigente está no gerador (`ORDEM`) e no manifesto.

> [!NOTE]
> **Revisão de 11/11/2026 (versão de 24 slides).** Corrigido: a faixa do meio da regra no slide da bolsa dizia
> "0,300 a 0,400" e o diagrama dizia "0,301 a 0,400" (o certo é 0,301: 0,300 fica em R$ 10 mil); a tabela de variáveis
> da base, alargada, tinha letra de ~9 pt (agora 15 pt); no apêndice, a legenda da equação da utilidade e o cartão do
> custo não pecuniário estouravam a caixa; o rótulo "CUSTO GEOGRÁFICO (REDDING & ROSSI-HANSBERG, 2017)" quebrava em
> duas linhas (agora "GEOGRÁFICO (…)" e "LABORAL (…)"); a fonte do slide do IVS citava o item 11.1.4 do edital, que é a
> grade do FAQ (errata E10). Conferido: números da tela contra `output/`, cautelas obrigatórias, navegação, número de
> página e notas de fala ("origem" só nas notas, onde o termo técnico é permitido).

## 0. O método passo a passo (pedido do autor de 09/11/2026)

A banca de 04/11 não entendeu o método e disse nunca ter ouvido falar dele. Por isso, a seção de Metodologia abre com
dois slides novos, **antes** da equação, com pouco texto e no estilo visual do deck do grupo (pedido do autor de 11/11/2026: "texto demais; se inspira no que o grupo mandou") (slide "Modelo: logit condicional da 1ª opção"), no design do grupo e gerados
pelo script (`slides_metodo`):

| Slide | Título | Na tela |
|---|---|---|
| novo 1 | "Método passo a passo: logit condicional" | no estilo do grupo, quase sem frase: "I. Como o modelo lê cada escolha" (McFadden, 1974, Nobel de 2000; o mesmo modelo de Bobba et al.) com quatro linhas — 1 Cardápio (todas as vagas do curso no ciclo, ≈ 107), 2 Escolha (1ª opção = 1; as outras = 0), 3 Pontuação (β·bolsa + γ·distância + par de UFs), 4 Chance (e^pontuação ÷ soma do cardápio); "II. O que sai": caixa escura "β = 0,077 por R$ 1 mil/mês" e "Condicional: só compara vagas do mesmo médico". O resto da explicação vai para as notas de fala |
| novo 2 | "Exemplo: um candidato, três vagas" | "I. Mesmo curso, mesma UF (MG)", com o rótulo "ilustrativo: vagas inventadas, pesos estimados"; tabela A (R$ 10 mil, 50 km, 28,8%), B (R$ 15 mil, 50 km, 42,4%), C (R$ 15 mil, 125 km, 28,8%); "II. O que o exemplo mostra": caixas "B contra A ×1,47" (o resultado) e "C contra A 75 km" (a distância come os R$ 5 mil) |

Os pesos, o 1,47, os 75 km e as chances do exemplo são calculados pelo gerador a partir de
`output/rdd_bolsa/VL_estimativas.csv` (o gerador para se e^(5β) não reproduzir a razão de chances gravada) e ficam no
manifesto (`exemplo_metodo`, rotulado ILUSTRATIVO: as vagas são inventadas; os pesos são os estimados). O deck passa
a ter 25 slides, 16 no corpo.

## 0.1 Revisão do modelo teórico (11/11/2026)

Revisão dos slides de teoria contra [`modelo_micro.md`](../../02_teoria/modelo_micro.md) (§1, §2.1, §2.4, §3.2) e o doc
[01](01_diagrama_teoria_mudanca.md). As trocas estão no gerador (`TROCAS_TEORIA`, `TROCAS_OMML`), cada uma conferindo
o texto antigo:

| Erro (a banca pegaria) | Correção |
|---|---|
| "REDDING & ROSSI, 2017" | "REDDING & ROSSI-HANSBERG, 2017" |
| Equação de Redding & Rossi-Hansberg com Z, W e k, enquanto os rótulos usam w e κ | z, w e κ, como no `modelo_micro` §3.2 |
| Papel de p e de c trocado: amenidades e segurança no cartão do deflator; c era "viver ali" num slide e "exercer ali" no outro; R&RH "gera só p" | p = custo de vida ("Moradia e custo de vida", "Nível de preços da cidade"); c = custo não pecuniário de viver **e** trabalhar ali; R&RH gera p e a parte geográfica de c; Choné & Ma, a parte laboral |
| "max" no lugar de "arg max"; i = localidade, mas i = candidato no modelo empírico | arg max e m para a localidade (equação, rótulos e "Gera m*") |
| "MOEHLING et al. (2020), EQ. 1" sobre uma equação adaptada (com B, r, I_r) | "ADAPTADO DE MOEHLING et al. (2020), EQ. 1, P. 184" |
| δ = desconto na teoria e δ = distância no modelo empírico | distância vira γ no slide do método e no do modelo |

Também: legenda da equação liga m*_r à 1ª opção e I_r ao cardápio; "Curso" no lugar de "Especialidade"; "distância de
casa"; "o saldo" (E/p − c não é soma); "E(w | B)". As equações em OMML têm uma imagem de reserva (que o LibreOffice e o
PDF mostram); as três que mudaram foram redesenhadas pelo gerador em `output/apresentacao_banca_final/equacoes/`. A
referência de Burdett, Shi & Wright (2001) entrou no `modelo_micro.md`, §5.

**Decisões do autor (11/11/2026):**
1. O choque ε **não** entra na equação teórica.
2. Testamos o **elo da remuneração**: a nota do diagrama da teoria diz isso na tela ("Diagrama teórico: testamos só o elo da remuneração (bolsa → valor da vaga → 1ª opção)."), e a nota do slide da agregação
   também ("Testamos só o elo da remuneração: B ↑ → V ↑ → π ↑ (a 1ª opção)").
3. O altruísmo **não aparece mais como equação**: Choné & Ma fica U = R − C(q; L, K); sai o chip "B(q): benefício ao
   paciente" (entra "L, K: equipe e capital") e a frase do altruísmo (α). Com isso, α fica só para o par de UFs. A
   menção verbal ao altruísmo no diagrama ("esforço e altruísmo do médico") continua.
4. A lista sincera entra como premissa, porque a grade de Limitações (6 cartões) está cheia: no slide de Identificação,
   "Conjunto de escolha: supomos que viu todas as vagas do curso e listou sem estratégia" (SUPOSTO); nas notas das
   Limitações, o que ela implica (com estratégia, o ×1,47 mistura preferência e chance de ser alocado).

Segue em aberto: a colisão de β (bolsa × parcela da moradia 1 − β em Redding & Rossi-Hansberg); atualizar o doc 01 e
o gerador do diagrama para "distância de casa".

## 0.2 Enxugamento do texto (11/11/2026)

Pedido do autor: "texto demais"; um agente revisor escreveu a mensagem de cada slide e propôs cortes. As trocas estão no
gerador (`TROCAS_ENXUGAR`, `REMOVER_GRUPOS`), cada uma conferindo o trecho antigo; o detalhe cortado fica nas notas de
fala. As cautelas obrigatórias ficam (exploratório; pacote do corte; vaga marcada, não ida ao município; forte só no
ciclo 2; sem o par de UFs, IC contém 1; local de trabalho anterior = vínculo no CNES). No diagrama da teoria, saem as
linhas descritivas dos nós e a faixa "elos da política" vira "Cadeia do programa: não estimada aqui". Nas Limitações,
o texto de cada cartão foi encurtado, sem apagar cartão. As notas do divisor "Apêndice" estavam com uma resposta de
chat colada (do deck do grupo) e foram limpas. O slide da equação continua no corpo (a banca pediu a especificação),
enxugado.

| # | Slide | Mensagem |
|:---:|---|---|
| 2 | Escassez | faltam especialistas, de forma desigual entre UFs; o PMM-E abriu vagas nas cinco regiões |
| 3 | A bolsa e a regra | a bolsa sai de uma regra (R$ 10, 15 ou 20 mil pelo IVS); a pergunta: a bolsa maior faz a vaga ser a 1ª opção? |
| 4 | Teoria da mudança | a bolsa eleva o valor da vaga contra o custo do lugar; testamos só o elo da remuneração |
| 5 | Hipótese | entre duas vagas do mesmo curso e da mesma UF, a de R$ 5 mil a mais tem mais chance de ser a 1ª opção (exploratória) |
| 6 | Base | uma linha por candidato × vaga possível: 5.417 candidatos, 578.998 linhas |
| 7 | Descritiva | 79% escolhem na UF onde já trabalhavam; por isso o modelo compara só vagas da mesma UF |
| 8–9 | Método e exemplo | cardápio, escolha, pontuação, chance; +R$ 5 mil = ×1,47 = 75 km |
| 10 | Modelo | a bolsa é testada; o par de UFs é pareamento; IVS contínuo e distância são controles |
| 11 | Bobba et al. | a referência forte usa o mesmo desenho |
| 12 | Identificação | o β aprende só com vagas do mesmo par de UFs com bolsas diferentes; mede o pacote do corte |
| 13 | Resultado | +R$ 5 mil multiplicam por 1,47 a chance da 1ª opção (IC 1,15 a 1,89); exploratório |
| 14 | Robustez | ×1,41 a ×1,52 com todos os dados; com menos dados, o IC contém 1 |
| 15 | Conclusão | sim, ×1,47; forte só no ciclo 2; reordena a 1ª opção, não mostra mais médicos no município |
| 16 | Limitações | as seis cautelas e o que cada uma implica |

## 1. O feedback de 04/11 aplicado à parte da banca 1

| Pedido da banca (doc 12, §1.2 e §1.3) | Na parte da banca 1 |
|---|---|
| Menos slides, menos conteúdo | saem os sete sumários do grupo; sai o slide do IVS e da bolsa (a regra em três faixas está no slide 3, do pós-banca; o IVS em detalhe vai para o apêndice); sai o slide separado da pergunta (ela está em destaque no slide 3); sai o diagrama B (a hipótese tem slide próprio; os pontos frágeis estão na Identificação e nas Limitações) |
| Navegação só com as seções que existem, igual em todos os slides | o rodapé de todos os slides passa a ser "Motivação \| Literatura \| Hipótese \| Dados \| Análise Descritiva \| Metodologia \| Identificação \| Resultados \| Robustez \| Discussão", com a seção corrente em negrito; "Literatura" entra porque agora tem slide (o diagrama); na capa, no Q&A e no apêndice nenhuma seção fica marcada |
| Trocar "origem" na tela | diagrama da teoria: "distância da origem" vira "distância de casa" (a casa do médico, como em Moehling et al.) |
| Capa: "incentivo limitado" saiu | capa do grupo com o título do pós-banca: "A bolsa maior atrai a 1ª opção? Um modelo de escolha para o Programa Mais Médicos Especialistas" |
| Tirar o gráfico que cria expectativa de RDD | o gráfico bolsa × IVS fica só no apêndice (A1), como no pós-banca |

E, como na versão 1, as erratas da [versão apresentada da banca 1](../banca1/04_versao_apresentada.md), §3: os
gráficos do grupo sem fonte reproduzível (P6, P7, P8, P12, P13) saem ou são trocados por figuras do pipeline; o
"piso" e a grade do FAQ (E10) não aparecem; "transporte" (E8).

## 2. Ordem do deck (23 slides)

| # | Origem | Seção | Slide |
|:---:|---|---|---|
| 1 | grupo 1 | — | Capa: "A bolsa maior atrai a 1ª opção? Um modelo de escolha para o Programa Mais Médicos Especialistas" |
| 2 | grupo 3 | Motivação | A escassez de especialistas já é tratada como urgência sanitária (figuras do pipeline) |
| 3 | pós-banca 2 | Motivação | A bolsa do PMM-E é maior onde o município é mais vulnerável (notícias, a regra em três faixas e a pergunta) |
| 4 | grupo 16 | Literatura | Da regra da bolsa à saúde: teoria da mudança |
| 5 | pós-banca 3 | Hipótese | Hipótese: na mesma UF, a bolsa maior atrai a 1ª opção |
| 6 | pós-banca 4 | Dados | Base: uma linha por candidato × vaga possível |
| 7 | pós-banca 5 | Análise Descritiva | 79% escolhem uma vaga na UF onde já trabalhavam |
| 8 | pós-banca 6 | Metodologia | Modelo: logit condicional da 1ª opção |
| 9 | pós-banca 7 | Metodologia | Por que este modelo: o desenho de Bobba et al. (2026) |
| 10 | pós-banca 8 | Identificação | Identificação: o que fica fixo e o que supomos |
| 11 | pós-banca 9 | Resultados | Na mesma UF, +R$ 5 mil multiplicam a chance por 1,47 |
| 12 | pós-banca 10 | Robustez | Robustez: sempre comparando vagas da mesma UF |
| 13 | pós-banca 11 | Discussão | Conclusão: a bolsa maior aumenta a 1ª opção? Sim |
| 14 | pós-banca 12 | Discussão | Limitações e o que cada uma implica |
| 15 | grupo 25 | — | Q&A |
| 16 | grupo 26 | — | Apêndice |
| 17 | pós-banca 14 | — | Apêndice A1: a bolsa segue exatamente o IVS |
| 18–22 | grupo 27, 28, 30, 31, 29 | — | equações: três elementos da teoria; escolha locacional (utilidade e renda real líquida); custo geográfico e laboral; da escolha individual ao agregado |
| 23 | grupo 38 | — | O IVS mede a vulnerabilidade social dos territórios brasileiros |

Do pós-banca saem a capa (1) e o Q&A (13): ficam os do grupo. Do deck do grupo reorganizado, o manifesto
(`slides_do_grupo_fora`) traz cada slide que saiu e o motivo. Os números digitados à mão nos slides passam a ser a
posição no deck final.

## 3. Textos novos na tela

Cada troca confere o texto antigo antes de trocar; se ele não estiver lá, o gerador para. Os slides do pós-banca
entram **sem mudança de texto**, só com o rodapé e o número de página do deck final; as notas (roteiro de fala) vão
junto.

| Slide | Antes | Depois |
|:---:|---|---|
| 1 | "Remuneração como incentivo limitado: um modelo de escolha racional para o Programa Mais Médicos Especialistas" | "A bolsa maior atrai a 1ª opção?" / "Um modelo de escolha para o" / "Programa Mais Médicos Especialistas" |
| 2 | gráfico de 16 UFs (sem fonte reproduzível, P6) | figura `especialistas_por_uf_extremos.png`, subtítulo "Especialistas por 100 mil hab., as duas maiores e as duas menores UFs, dez/2024" |
| 2 | "II. Serviços especializados exigem longos deslocamentos", gráfico de deslocamento (P7) | "II. O ciclo 1 do PMM-E abriu vagas nas cinco regiões"; "Células estabelecimento × curso e vagas imediatas, ciclo 1, 1ª chamada"; figura `vagas_ciclo1_por_regiao.png` |
| 2 | fontes com REGIC 2018 | "Fontes: Medicina S/A; Amado Mundo; Agência Câmara; Scheffer et al., Demografia Médica no Brasil 2025 (FMUSP/AMB), só as UFs com valor citado; quadro de vagas do Edital SGTES/MS nº 3/2025." |
| 4 | "Moradia, deslocamento, amenidades e distância da origem." | "Moradia, deslocamento, amenidades e distância de casa." |
| 19 | "… é a soma das três variáveis que determina se a vaga é preenchida." | "A política mexe em apenas uma variável: eleva E(w\|B) pela bolsa (B). Preços e custo do local continuam contra, e é o saldo das três variáveis que decide qual vaga o médico escolhe." |
| 21 | "Adições ao modelo do slide 11:" | "Adições ao modelo do slide anterior:" |
| 22 | rótulo "HIPÓTESE" na cadeia B ↑ → V ↑ → π ↑ → Pr(Y = 1) ↑ | "CADEIA DO MODELO" |
| 23 | "trasnporte" | "transporte" (errata E8) |

Notas reescritas: slide 2 (por que os gráficos do grupo saíram) e slide 4 (a hipótese testa só o elo da escolha; o
resto da cadeia não é testado aqui).

## 4. Em aberto (decisão do autor)

1. **Tempo.** O corpo tem 14 slides (capa a Limitações); a banca 2 sozinha tinha roteiro de 7:30. Falta saber o
   tempo da banca final para escrever o roteiro de fala dos slides da banca 1 (capa, motivação e teoria).
2. **Diagrama B.** Saiu pelo pedido de menos slides; volta pondo `("G", 18, "Hipótese")` na `ORDEM` do gerador,
   depois do slide da hipótese (a hipótese dele teria de ser trocada, como na versão 1).
3. **Adendos 52g e 52h** (por ciclo e por degrau, no slide de robustez) seguem sem auditoria.
