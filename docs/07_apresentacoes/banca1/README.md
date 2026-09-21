# Banca 1 — apresentação do projeto

> **Formato:** markdown com imagens, para ler no GitHub ou no Obsidian<br>
> **Escopo:** três seções, terminando na viabilidade empírica<br>
> **Fora do escopo:** estratégia de identificação executada, estimadores, resultados e robustez<br>
> **Atualização:** 21 de setembro de 2026

## 1. O que esta entrega é

A banca 1 apresenta a **fundamentação teórica** do trabalho, em **17 slides** e
**três seções**, seguidos de um **Q&A** e de um **apêndice de quatro slides**
que ficam fora da contagem e só entram se alguém perguntar. Cada seção abre com uma divisória e ocupa quantos slides o
argumento pedir — e, desde a reorganização de 16/09/2026, nenhum a mais.

| Seção | Slides | Conteúdo |
|---|:---:|---|
| **Capa e sumário** | 1–2 | a capa e o sumário, que aparece **uma vez** |
| **1. Motivação e Pergunta** | 3–8 | divisória (3); problema (4): o retrato territorial e a dupla prática, **em figura**; política (5): o pacote que é igual em toda vaga, quem fixa o valor e para onde a regra manda o dinheiro; IVS e suas dimensões (6): o que o índice mede; efeitos (7): o ciclo 1 e a literatura, dois de cada lado; pergunta de pesquisa (8): a cadeia que a política supõe, e a pergunta |
| **2. Literatura Teórica e Modelo Microeconômico** | 9–13 | divisória (9); literatura teórica usada (10): as três tradições e as **equações originais** de cada uma; modelo microeconômico conjunto (11): a equação de escolha e a caixa-preta do custo; custo da localidade (12): as equações inferidas e as três desvantagens, termo a termo; remuneração da localidade (13): a bolsa é o **piso**, não o total |
| **3. Hipótese e Viabilidade Empírica** | 14–17 | divisória (14); implicações para o PMM-E (15), com a condição de aceitação e a fronteira entre faixas; hipótese do trabalho (16), sozinha na tela; disponibilidade de dados (17) |
| **Q&A e apêndice** | fora da contagem | Perguntas; e quatro slides de resposta: o diagnóstico da regra que saiu da tela em 17/09 (`A1`), a literatura de reserva (`A2`), as duas notas sobre a regra (`A3`) e as pendências abertas (`A4`) |

**Convenção do documento de conteúdo.** Entre os comentários `deck:inicio` e
`deck:fim` de [02 — Conteúdo](02_conteudo_slides.md), **cada cabeçalho de
primeiro ou segundo nível é um slide**: `#` é layout de capa — a capa e as três
divisórias de seção — e `##` é layout de conteúdo, os treze slides restantes. O
terceiro nível, `###`, **não abre slide**: marca um **build** dentro do slide,
um `\only<n>` no Beamer e um clique no Slidev. São **32 builds nos 17 slides** e,
desde o corte de 17/09/2026, **nenhum slide passa de três builds**. A tabela
"Mapa da apresentação", no topo daquele arquivo, dá a correspondência completa
entre número, layout, builds, seção, rótulo do roteiro e título de tela; é dela
que este README deriva.

**O que não vai à tela.** Duas coisas no corpo do slide são de produção, não de
projeção: a linha `**Fontes:**`, que vira nota de rodapé pequena, e todo bloco
marcado `**Nota de produção.**`, instrução para quem monta o deck. Tudo o mais é
conteúdo de tela.

**A banca 1 é teórica.** Fora da seção 1, nada de estimação, e os slides de
literatura trazem apenas trabalhos teóricos. A seção 1 é a exceção declarada: no
slide 7, antes da pergunta, entra evidência sobre o que se pode esperar da
política. Desde 17/09/2026 a seção 3 **não tem nada de empírico**: o slide de
desafio metodológico, que trazia a reconstrução da regra, saiu do deck a pedido
do autor, e a seção termina no inventário de dados. Nem por isso o achado
desapareceu — ele continua em
[`05_identificacao/16`](../../05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
§3.5, como material de resposta à banca.

A margem tratada é o **preenchimento** das vagas; permanência fica fora. Não
há slide de perguntas: a apresentação termina na viabilidade. Nenhum resultado
é apresentado, porque nenhum está autorizado a ser promovido a evidência causal
no estado atual do projeto — ver
[`docs/06_execucao/05_roadmap_execucao.md`](../../06_execucao/05_roadmap_execucao.md).

A cadeia narrativa é um recorte inicial da cadeia analítica do projeto:

```
implementação → força de trabalho → capacidade → acesso → saúde → custos → equidade
└──────────── escopo da banca 1 ────────────┘
```

## 2. Índice

| Documento | Função |
|---|---|
| [Conteúdo da apresentação](02_conteudo_slides.md) | **a fonte de verdade** — os **17 slides** e **32 builds**, com título, corpo, figuras, fontes e ressalvas. `###` marca build, não slide; a linha de fontes e os blocos de **nota de produção** não vão à tela, e todo o resto do corpo vai. Os decks derivam dele |
| [Roteiro narrativo](01_roteiro_narrativo.md) | arco das seções, lógica de cada bloco, regras de composição — inclusive a do build, na seção 2.6 —, rastreio do feedback e histórico das revisões, inclusive a reorganização de 16/09/2026, a compressão do mesmo dia (4f) e as duas rodadas de 17/09/2026 (4g e 4h) |
| [Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | origem e reprodutibilidade de cada número exibido |
| [Deck Beamer](deck_beamer/) · [Deck Slidev](deck_slidev/) | artefatos derivados, com script de build cada um; PDFs em `output/apresentacao_banca1/`. O **Beamer** foi reconstruído em 19/09/2026 sobre a estrutura vigente: 17 frames, 32 builds, identidade Insper; em 21/09 a moldura perdeu a barra de navegação, ganhou cinco componentes de composição e, depois de `\appendix`, o Q&A e quatro slides de apêndice, com uma [galeria](deck_beamer/exemplos_tema.tex) que serve de ponto de partida para um deck novo. O **Slidev** foi reconstruído em 21/09 sobre a mesma estrutura, com um build por página, 40 no total, e repintado na mesma identidade Insper. A pendência 6 fechou |

## 3. Figuras

Desde 17/09/2026 **todas as figuras do deck saem do pipeline**. São sete, e as
três do slide 4 são novas: o corte daquele dia trocou lista de números por
figura, e pôr mais peso numa figura montada à mão agravaria a violação da regra
de proveniência em vez de tolerá-la.

| Figura | Slide | Origem |
|---|:---:|---|
| Especialistas por 100 mil hab., duas maiores e duas menores UFs | 4 | Demografia Médica 2025 |
| Deslocamento médio para alta complexidade, por região | 4 | atribuído à REGIC 2018, **fonte a confirmar** |
| Setor de atuação dos cirurgiões | 4 | Demografia Médica 2025, cap. 13 |
| Bolsa mensal por faixa | 5 | edital |
| Especialistas por 100 mil habitantes por faixa publicada | 5 | CNES + Censo 2022 |
| Colegas da mesma especialidade por faixa publicada | 5 | CNES |
| Preenchimento do ciclo 1 por faixa e por estrato | 7 | tabelas descritivas do módulo A4 |

As três do slide 4 **não derivam de base do repositório**: os valores são
estatísticas publicadas, declaradas no script como constantes com fonte, página
e cobertura, e repetidas no `manifesto_figuras.json` com o campo
`fonte_primaria_confirmada`. **Gerar por script resolve a forma, não a fonte** —
duas delas seguem sem fonte primária conferida, pendências 1, 2 e 5.

A figura de UF do deck do grupo **não voltou**: medida contra os dois rótulos
impressos, ela punha SP em ≈ 419 e PA em ≈ 135, contra os 244 e 70 da série
citada. A figura nova é dos **quatro** valores com fonte registrada, e o
panorama das 27 unidades só volta quando a tabela por UF da *Demografia Médica
2025* estiver registrada em `data/raw/` com hash.

Para regerar:

```bash
python3 scripts/aquisicao/06_adquirir_populacao_censo2022.py   # denominador, uma vez
python3 scripts/apresentacao/gerar_figuras_banca1.py
```

O script continua gerando a figura regional das vagas e a série mensal de
oferta, que **não são usadas** no deck; a curva de custo laboral de
`docs/02_teoria/figuras/` também saiu do deck em 16/09/2026. As imagens em
`figuras/` são material do deck anterior, preservado mas não usado. Ver
[03 — Proveniência](03_proveniencia_figuras_e_numeros.md#figuras-geradas-e-não-usadas).

Para reconstruir os decks — o Beamer na estrutura vigente de 17 slides; o
Slidev ainda na de 15:

```bash
bash scripts/apresentacao/build_deck_beamer.sh        # LuaLaTeX, 17 frames + apêndice, 40 páginas
bash scripts/apresentacao/build_exemplos_tema.sh      # galeria de componentes do tema
bash scripts/apresentacao/build_deck_slidev.sh        # Node 22, Chromium local, 40 páginas
```

## 4. Estado

| Seção | Slides | Conteúdo | Figuras | Proveniência |
|---|:---:|:---:|:---:|:---:|
| Capa e sumário | 1–2 | ✅ | — | — |
| 1. Motivação e Pergunta | 3–8 | ✅ | ✅ | ⚠️ |
| 2. Literatura Teórica e Modelo Microeconômico | 9–13 | ✅ | — | ✅ |
| 3. Hipótese e Viabilidade Empírica | 14–17 | ✅ | — | ⚠️ |

**Figuras** está ✅ desde 17/09/2026: as sete saem do pipeline. **Proveniência**
está ⚠️ em duas seções, por razões diferentes. Na **motivação**, duas séries do
slide 4 seguem sem fonte primária conferida — gerar por script não confirma
fonte. Na **hipótese e viabilidade**, a tela passou a afirmar que o custo cresce
com o IVS, e o documento canônico trata esse sinal como ambíguo: é divergência
declarada, não erro de rastreio, e está registrada como pendência 9.

As **três ressalvas de conteúdo** continuam encerradas desde 16/09/2026 — a
contagem de cursos ambulatoriais, a figura do custo laboral e a citação direta
da Portaria GM/MS nº 7.177/2025. Abertas há **oito pendências**, listadas com
efeito e critério de fechamento no fim de
[02 — Conteúdo](02_conteudo_slides.md): a cobertura da figura por UF, que hoje é
dos quatro valores com fonte e não das 27 unidades (1), e a fonte primária do
deslocamento por região (2), que são as que tocam a regra de proveniência; o PDF
da *Demografia Médica 2025* a registrar em `data/raw/` com hash, depois de
corrigido o número da dupla prática (3); a tabela de inclinações pré/pós do deck
do grupo, não reproduzível e por isso mantida fora do slide 7 (4); o percentual
do Sudeste conferido em cobertura e não no PDF integral (5); os dois decks, agora
duas estruturas atrás (6); a decisão do autor sobre a fronteira municipal da
medida de retaguarda, vinda do PR de ajuste estrutural (8); e a monotonicidade do
custo no IVS, que a tela afirma e a teoria do projeto não postula (9). A
pendência **7** — a figura que faltava ao desafio metodológico — **fechou** em
17/09/2026, por remoção do slide que a pedia.
O rastreio número a número segue em
[03 — Proveniência](03_proveniencia_figuras_e_numeros.md#3-pendências-e-ressalvas).

## 5. Onde o conteúdo vive na documentação

Esta apresentação não cria conteúdo. Cada bloco tem um documento canônico de
origem, e é lá que a informação deve ser corrigida primeiro:

| Seção · slide | Documento canônico |
|---|---|
| 1 · problema (4) | fontes externas — *Demografia Médica no Brasil 2025* (FMUSP/AMB) e REGIC 2018 — e `output/aquisicao/quadro_vagas_tratamento.parquet`; rastreio em [03 — Proveniência](03_proveniencia_figuras_e_numeros.md) |
| 1 · política (5) | [`auditorias/01_regra_institucional.md`](../../auditorias/01_regra_institucional.md), o edital em `data/raw/aquisicao/ivs_regra/` e a reconstrução da regra em [`05_identificacao/14_...md`](../../05_identificacao/14_plano_implementacao_rdd_bolsa.md) |
| 1 · IVS e suas dimensões (6) | Ipea, *Atlas da Vulnerabilidade Social* (2015); o mapeamento em [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 3.1, e o item 11.1.4 do edital |
| 1 · efeitos (7) | [`03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md), seção 7; números do ciclo 1 em `output/tema_trabalho/` (módulos A4 e A5) |
| 1 · pergunta de pesquisa (8) | [`01_pergunta_escopo/15_...md`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), "Formulação curta canônica" |
| 2 · literatura teórica usada (10) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 1, 2 e 3.2 — as três equações originais |
| 2 · modelo microeconômico conjunto (11) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 1 e 2.4 |
| 2 · custo da localidade (12) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 2.1 a 2.3 e 3.2 |
| 2 · remuneração da localidade (13) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 3, e [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 2 |
| 3 · implicações para o PMM-E (15) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 2.4, 3, 3.1 e 4.1, e [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 3 |
| 3 · hipótese do trabalho (16) | [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 4, e [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 4.2 |
| 3 · disponibilidade de dados (17) | [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md) |

O histórico da reorganização que acompanhou esta entrega está em
[`docs/00_registro_mudancas.md`](../../00_registro_mudancas.md).

## 6. Defeitos do material anterior corrigidos aqui

O arquivo `PEE__Modelo_econômico.pptx` (11 slides) entrou nesta documentação já
corrigido. Os defeitos encontrados e o tratamento dado estão na seção 5 do
[roteiro narrativo](01_roteiro_narrativo.md#5-defeitos-do-material-anterior).
