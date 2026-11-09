# 02 — Deck da banca final: banca 1 adaptada + banca 2

> **Pedido do autor (09/11/2026):** juntar os slides da banca 2 com os da banca 1, "adaptados pras mudanças que
> fizemos no trabalho pra banca 2", para apresentar na banca final.<br>
> **Estatuto:** conteúdo canônico do deck da banca final, **versão 1 (proposta)**. O `.pptx` é derivado: divergência
> entre o deck e este documento é erro do deck (`CLAUDE.md`).<br>
> **Deck:** `output/apresentacao_banca_final/deck_banca_final.pptx` e `.pdf`, gerados por
> [`scripts/apresentacao/gerar_deck_banca_final.py`](../../../scripts/apresentacao/gerar_deck_banca_final.py), com o
> manifesto `manifesto_deck_banca_final.json` (hashes das entradas e das saídas, ordem e adaptações).
> Conferido por `tests/test_deck_banca_final.py`.<br>
> **Entradas (só `output/`):** o deck do grupo reorganizado com o diagrama da teoria da mudança
> (`deck_proposta_reorganizada.pptx`, doc [01](01_diagrama_teoria_mudanca.md)); o deck curto da banca 2
> (`output/apresentacao_banca2/deck_banca2_curto.pptx`, conteúdo no
> [doc 04 da banca 2](../banca2/04_conteudo_deck_curto.md)); duas figuras do pipeline da banca 1
> (`output/apresentacao_banca1/especialistas_por_uf_extremos.png` e `vagas_ciclo1_por_regiao.png`).

## 1. O que muda da banca 1 para a banca final

A banca 2 trocou a hipótese: de "municípios com maior remuneração têm maior preenchimento de vagas" para a escolha da
1ª opção, comparando vagas da mesma UF (decisão do autor de 28/10/2026, [doc 07 da banca 2](../banca2/07_nova_hipotese.md)).
A parte da banca 1 foi adaptada a isso e às erratas da [versão apresentada](../banca1/04_versao_apresentada.md), §3:

| Tema | Banca 1 (apresentada) | Banca final |
|---|---|---|
| Pergunta | "Um aumento na remuneração do PMM-E consegue atrair especialistas para municípios mais vulneráveis?" | **"Uma bolsa maior do PMM-E muda a vaga que o especialista escolhe como 1ª opção?"** — a margem que os dados medem |
| Hipótese | preenchimento de vagas | **"Comparando vagas da mesma UF, a de bolsa maior tem mais chance de ser a 1ª opção do especialista (formulada após ver os dados)."** |
| Regra da bolsa | "o IVS é o piso"; R$ 20 mil só em vulnerabilidade muito alta (grade do FAQ) | regra aplicada, com o IVS 2010 oficial: até 0,300, R$ 10 mil; de 0,301 a 0,400, R$ 15 mil; acima de 0,400, R$ 20 mil (errata E10, auditoria 16) |
| Motivação com números | figura de 16 UFs (P6), deslocamento por região (P7), crescimento por faixa (P12), distribuição regional (P13) | só o que se reproduz: as UFs com valor citado na Demografia Médica 2025 e as vagas do ciclo 1 por região, do quadro de vagas |
| "Há indícios de efetividade" | antes/depois sem comparação (errata E6) | sai |
| Viabilidade empírica | o desafio de separar bolsa e vulnerabilidade; 35,6% e 30% (erratas E4, E5) | substituída pelos dados, descritivas, método, identificação e resultados da banca 2 |
| Teoria | equações no corpo | diagrama da teoria da mudança no corpo; equações no apêndice (doc 01) |
| Hipótese no diagrama | "BOLSA → PREENCHIMENTO", colchete nos passos 2 e 3 | **"HIPÓTESE: BOLSA → 1ª OPÇÃO"**, colchete só no passo 2 (escolha); os passos seguintes ficam como cadeia não testada |

## 2. Ordem do deck (32 slides)

O rodapé usa as sete seções do deck do grupo; as oito seções da banca 2 entram nelas: Dados e Análise descritiva em
**Base de Dados**; Metodologia e Identificação em **Metodologia**; Resultados, Robustez e Discussão em
**Resultados**. No apêndice, nenhuma seção fica marcada.

| # | Origem | Seção | Slide |
|:---:|---|---|---|
| 1 | grupo 1 | — | Capa: "Remuneração como incentivo limitado: um modelo de escolha racional para o Programa Mais Médicos Especialistas" |
| 2 | grupo 2 | Motivação | Sumário |
| 3 | grupo 3 | Motivação | A escassez de especialistas já é tratada como urgência sanitária (figuras do pipeline) |
| 4 | grupo 7 | Motivação | A vulnerabilidade social define a faixa da bolsa do PMM-E |
| 5 | grupo 12 | Pergunta | Sumário |
| 6 | grupo 13 | Pergunta | a pergunta |
| 7 | grupo 15 | Literatura | Sumário |
| 8 | grupo 16 | Literatura | Da regra da bolsa à saúde: teoria da mudança |
| 9 | grupo 17 | Hipótese | Sumário |
| 10 | banca 2, 1 | Hipótese | Pergunta e hipótese: a bolsa maior muda a 1ª opção? |
| 11 | grupo 18 | Hipótese | A hipótese e onde a identificação é fraca |
| 12 | grupo 19 | Base de Dados | Sumário |
| 13–16 | banca 2, 2–5 | Base de Dados | dados e amostra; regra *sharp*; onde escolhem; descritivo perto do corte |
| 17 | grupo 21 | Metodologia | Sumário |
| 18–19 | banca 2, 6–7 | Metodologia | modelo; identificação |
| 20 | grupo 23 | Resultados | Sumário |
| 21–24 | banca 2, 8–11 | Resultados | resultado principal; robustez; conclusão; limitações |
| 25 | grupo 25 | — | Q&A |
| 26 | grupo 26 | — | Apêndice |
| 27–31 | grupo 27, 28, 30, 31, 29 | — | equações: três elementos da teoria; escolha locacional (utilidade e renda real líquida); custo geográfico e laboral; da escolha individual ao agregado |
| 32 | grupo 38 | — | O IVS mede a vulnerabilidade social dos territórios brasileiros |

Saem do deck do grupo reorganizado: 4, 5, 6, 8, 9, 10, 11, 14, 20, 22, 24, 32, 33, 34, 35, 36 e 37 (motivo de cada
um no manifesto, `slides_do_grupo_fora`). Os números digitados à mão nos slides do grupo passam a ser a posição no
deck final.

## 3. Textos novos na tela

Cada troca confere o texto antigo antes de trocar; se ele não estiver lá, o gerador para.

| Slide | Antes | Depois |
|:---:|---|---|
| 3 | gráfico de 16 UFs (sem fonte reproduzível, P6) | figura `especialistas_por_uf_extremos.png`, subtítulo "Especialistas por 100 mil habitantes, as duas maiores e as duas menores UFs – dez/2024" |
| 3 | "II. Serviços especializados exigem longos deslocamentos", gráfico de deslocamento (P7) | "II. O ciclo 1 do PMM-E abriu vagas nas cinco regiões"; "Células estabelecimento × curso e vagas imediatas, ciclo 1, 1ª chamada"; figura `vagas_ciclo1_por_regiao.png` |
| 3 | fontes com REGIC 2018 | "Fontes: Medicina S/A; Amado Mundo; Agência Câmara; Scheffer et al., Demografia Médica no Brasil 2025 (FMUSP/AMB), só as UFs com valor citado; quadro de vagas do Edital SGTES/MS nº 3/2025." |
| 4 | "A vulnerabilidade social define o piso da bolsa do PMM-E" | "A vulnerabilidade social define a faixa da bolsa do PMM-E" |
| 4 | "III. O IVS define a renumeração do PMM-E" | "III. O IVS define a faixa da bolsa do PMM-E" |
| 4 | "Bolsa-formação mensal por categoria do Índice de Vulnerabilidade Social" | "Bolsa-formação mensal por faixa do IVS 2010 oficial (Ipea)" |
| 4 | R$ 20 mil: "Vulnerabilidade: Muito alta" | "IVS acima de 0,400: alta e muito alta" |
| 4 | R$ 15 mil: "Vulnerabilidade: Alta" | "IVS de 0,301 a 0,400: média" |
| 4 | R$ 10 mil: "Vulnerabilidade: Média, baixa e buito baixa" | "IVS até 0,300: baixa e muito baixa" |
| 4 | "… é fixada, por regra, sobre a categoria de IVS do município." | "Instrumento da política. A bolsa de R$ 10 mil, R$ 15 mil ou R$ 20 mil é fixada por regra sobre o IVS 2010 do município, com cortes em 0,300 e 0,400." |
| 4 | fontes com o item 11.1.4 do edital (a grade do FAQ) | "Fontes: Ipea, Atlas da Vulnerabilidade Social (IVS 2010); quadros de vagas SGTES/MS; auditoria 16." |
| 6 | pergunta sobre preenchimento, sobre o fundo do slide 9 (números que não se reproduzem) | "Uma bolsa maior do PMM-E muda a vaga que o especialista escolhe como 1ª opção?", sem o fundo |
| 11 | "Municípios com maior remuneração oferecida pelo PMM-E têm maior probabilidade de preenchimento de vagas." | "Comparando vagas da mesma UF, a de bolsa maior tem mais chance de ser a 1ª opção do especialista (formulada após ver os dados)." |
| 11 | "HIPÓTESE: BOLSA → PREENCHIMENTO", colchete nos passos 2 e 3 | "HIPÓTESE: BOLSA → 1ª OPÇÃO", colchete só no passo 2 |
| 28 | "… é a soma das três variáveis que determina se a vaga é preenchida." | "A política mexe em apenas uma variável: eleva E(w\|B) pela bolsa (B). Preços e custo do local continuam contra, e é a soma das três variáveis que decide qual vaga o médico escolhe." |
| 31 | rótulo "HIPÓTESE" na cadeia B ↑ → V ↑ → π ↑ → Pr(Y = 1) ↑ | "CADEIA DO MODELO" |
| 32 | "trasnporte" | "transporte" (errata E8) |

Os 11 slides da banca 2 entram **sem mudança de texto**, só com o rodapé das sete seções; as notas (roteiro de fala)
vão junto. As propostas da [revisão 56](../../auditorias/56_revisao_deck_banca2_28out.md) ainda não foram aplicadas.

## 4. Notas do apresentador reescritas

Os slides 3, 4, 6 e 11 tinham notas sobre o conteúdo antigo ("valor mínimo pago", preenchimento). As notas novas
estão no gerador (`NOTAS`) e dizem, em resumo: slide 3, que os gráficos do grupo saíram por falta de fonte
reproduzível; slide 4, que a regra é o IVS 2010 oficial e que o "piso" da banca 1 vinha de um arquivo de IVS errado;
slide 6, que a pergunta passou a ser a margem medida (a 1ª opção marcada, não a ida ao município); slide 11, que a
hipótese fica só no passo 2 e foi formulada depois de ver os dados.

## 5. Em aberto (decisão do autor)

1. **Título do trabalho.** "Remuneração como incentivo limitado" foi mantido. Ele combina com a leitura da
   Conclusão (a bolsa compensa só parte do custo do lugar), mas a conclusão diz "Sim": decidir se o título fica.
2. **Revisão 56.** Aplicar ou não as propostas aos slides da banca 2 (identificação com o IVS na tela, "Sim" com
   "exploratório", "aceita vaga", "por degrau"). Os adendos 52g e 52h do slide 22 seguem sem auditoria.
3. **Duração.** O corpo tem 24 slides com 7 sumários; a banca 2 sozinha cabia em 7 minutos. Falta saber o tempo da
   banca final para decidir se os sumários ficam.
4. **Slide da pergunta.** Ficou sobre fundo neutro; o grupo pode trocar o fundo, desde que sem números que não se
   reproduzem.
