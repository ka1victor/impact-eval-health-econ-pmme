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

## 0. O método passo a passo (pedido do autor de 09/11/2026)

A banca de 04/11 não entendeu o método e disse nunca ter ouvido falar dele. Por isso, a seção de Metodologia abre com
dois slides novos, **antes** da equação (slide "Modelo: logit condicional da 1ª opção"), no design do grupo e gerados
pelo script (`slides_metodo`):

| Slide | Título | Na tela |
|---|---|---|
| novo 1 | "Método passo a passo: como medimos o peso da bolsa" | faixa: logit condicional (McFadden, 1974; Nobel de Economia de 2000), o modelo padrão de escolha entre várias opções, o mesmo de Bobba et al.; quatro passos — 1 o cardápio (≈ 107 vagas por candidato), 2 a escolha (uma linha por candidato × vaga, 1 na 1ª opção), 3 a pontuação (peso × bolsa + peso × distância + par de UFs + controles; chance = e^pontuação ÷ soma do cardápio), 4 os pesos (máxima verossimilhança; o peso da bolsa é o β); por que "condicional"; cautela: mede a vaga marcada na inscrição, não a ida ao município |
| novo 2 | "Exemplo: um candidato, três vagas do mesmo curso em MG" | três vagas **ilustrativas** (A: R$ 10 mil, 50 km; B: R$ 15 mil, 50 km; C: R$ 15 mil, 125 km), com a pontuação e a chance calculadas com os pesos estimados do VL-1 (0,077 por R$ 1 mil; −0,514 por 100 km): A 28,8%, B 42,4%, C 28,8%; B contra A = 1,47 (o resultado); C contra A ≈ 1 (os "75 km"); como se lê o β |

Os pesos, o 1,47, os 75 km e as chances do exemplo são calculados pelo gerador a partir de
`output/rdd_bolsa/VL_estimativas.csv` (o gerador para se e^(5β) não reproduzir a razão de chances gravada) e ficam no
manifesto (`exemplo_metodo`, rotulado ILUSTRATIVO: as vagas são inventadas; os pesos são os estimados). O deck passa
a ter 25 slides, 16 no corpo.

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
| 2 | gráfico de 16 UFs (sem fonte reproduzível, P6) | figura `especialistas_por_uf_extremos.png`, subtítulo "Especialistas por 100 mil habitantes, as duas maiores e as duas menores UFs – dez/2024" |
| 2 | "II. Serviços especializados exigem longos deslocamentos", gráfico de deslocamento (P7) | "II. O ciclo 1 do PMM-E abriu vagas nas cinco regiões"; "Células estabelecimento × curso e vagas imediatas, ciclo 1, 1ª chamada"; figura `vagas_ciclo1_por_regiao.png` |
| 2 | fontes com REGIC 2018 | "Fontes: Medicina S/A; Amado Mundo; Agência Câmara; Scheffer et al., Demografia Médica no Brasil 2025 (FMUSP/AMB), só as UFs com valor citado; quadro de vagas do Edital SGTES/MS nº 3/2025." |
| 4 | "Moradia, deslocamento, amenidades e distância da origem." | "Moradia, deslocamento, amenidades e distância de casa." |
| 19 | "… é a soma das três variáveis que determina se a vaga é preenchida." | "A política mexe em apenas uma variável: eleva E(w\|B) pela bolsa (B). Preços e custo do local continuam contra, e é a soma das três variáveis que decide qual vaga o médico escolhe." |
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
