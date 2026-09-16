# Banca 1 — apresentação do projeto

> **Formato:** markdown com imagens, para ler no GitHub ou no Obsidian<br>
> **Escopo:** três seções, terminando na viabilidade empírica<br>
> **Fora do escopo:** estratégia de identificação executada, estimadores, resultados e robustez<br>
> **Atualização:** 16 de setembro de 2026

## 1. O que esta entrega é

A banca 1 apresenta a **fundamentação teórica** do trabalho, em **16 slides** e
**três seções**. Cada seção abre com uma divisória e ocupa quantos slides o
argumento pedir — e, desde a reorganização de 16/09/2026, nenhum a mais.

| Seção | Slides | Conteúdo |
|---|:---:|---|
| **Capa e sumário** | 1–2 | a capa e o sumário, que aparece **uma vez** |
| **1. Motivação e Pergunta** | 3–7 | divisória (3); problema (4): o retrato territorial e a dupla prática; política (5): o que é o PMM-E, o que determina a bolsa e onde a regra manda o dinheiro; efeitos (6): o ciclo 1 e a literatura dos dois lados; pergunta de pesquisa (7) |
| **2. Literatura Teórica e Modelo Microeconômico** | 8–11 | divisória (8); visão geral (9): as três tradições e a equação de escolha; custo da localidade (10): o lugar e o trabalho; remuneração da localidade (11): a bolsa é parte, não todo |
| **3. Hipótese e Viabilidade Empírica** | 12–16 | divisória (12); implicações para o PMM-E (13); hipótese do trabalho (14); disponibilidade de dados (15); desafio metodológico (16) |

**Convenção do documento de conteúdo.** Entre os comentários `deck:inicio` e
`deck:fim` de [02 — Conteúdo](02_conteudo_slides.md), **cada cabeçalho é um
slide**: `#` é layout de capa — a capa e as três divisórias de seção — e `##` é
layout de conteúdo, os doze slides restantes. A tabela "Mapa da apresentação",
no topo daquele arquivo, dá a correspondência completa entre número, layout,
seção, rótulo do roteiro e título de tela; é dela que este README deriva.

**A banca 1 é teórica.** Fora da seção 1, nada de estimação, e os slides de
literatura trazem apenas trabalhos teóricos. A seção 1 é a exceção declarada: no
slide 6, antes da pergunta, entra evidência sobre o que se pode esperar da
política. Na seção 3 o que aparece de empírico é a reconstrução da regra de
alocação da bolsa — diagnóstico de viabilidade do desenho, não resultado.

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
| [Conteúdo da apresentação](02_conteudo_slides.md) | **a fonte de verdade** — os 16 slides com título, corpo, figuras, fontes e ressalvas. Diz exatamente o que vai à tela, e nada além; os decks derivam dele |
| [Roteiro narrativo](01_roteiro_narrativo.md) | arco das seções, lógica de cada bloco, regras de composição, rastreio do feedback e histórico das revisões, inclusive a reorganização de 16/09/2026 |
| [Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | origem e reprodutibilidade de cada número exibido |
| [Deck Beamer](deck_beamer/) · [Deck Slidev](deck_slidev/) | artefatos derivados, com script de build cada um; PDFs em `output/apresentacao_banca1/`. Em 16/09/2026 os dois ainda estão na **estrutura anterior, de 15 slides** — divergência conhecida e datada, a resolver na próxima reconstrução |

## 3. Figuras

As quatro figuras geradas por script continuam em uso e mudaram de slide na
reorganização de 16/09/2026: as três do bloco da política ficaram juntas no
slide 5, e o preenchimento do ciclo 1 passou ao slide 6.

| Figura | Slide | Origem |
|---|:---:|---|
| Bolsa mensal por faixa | 5 | edital |
| Especialistas por 100 mil habitantes por faixa publicada | 5 | CNES + Censo 2022 |
| Colegas da mesma especialidade por faixa publicada | 5 | CNES |
| Preenchimento do ciclo 1 por faixa e por estrato | 6 | tabelas descritivas do módulo A4 |

O **slide 4 pede duas figuras que ainda não são geradas por script** —
especialistas por 100 mil habitantes por UF e deslocamento médio para serviços
de alta complexidade por região. As duas vêm hoje do deck do grupo e, enquanto
não forem produzidas pelo pipeline e lidas de `output/`, estão fora da regra de
proveniência do projeto: são as pendências 1 e 2 do fim de
[02 — Conteúdo](02_conteudo_slides.md). Fora essas duas, nenhuma figura de fonte
externa entra no deck; números externos entram em texto, com fonte.

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

Para reconstruir os decks — que continuam produzindo a versão anterior, de 15
slides:

```bash
bash scripts/apresentacao/build_deck_beamer.sh        # pdflatex, 15 frames
bash scripts/apresentacao/build_deck_slidev.sh        # Node 22, Chromium local
```

## 4. Estado

| Seção | Slides | Conteúdo | Figuras | Proveniência |
|---|:---:|:---:|:---:|:---:|
| Capa e sumário | 1–2 | ✅ | — | — |
| 1. Motivação e Pergunta | 3–7 | ✅ | ⚠️ | ✅ |
| 2. Literatura Teórica e Modelo Microeconômico | 8–11 | ✅ | — | ✅ |
| 3. Hipótese e Viabilidade Empírica | 12–16 | ✅ | — | ✅ |

O ⚠️ é do slide 4: as quatro figuras dos slides 5 e 6 saem do pipeline, as duas
do slide 4 ainda não.

As **três ressalvas de conteúdo** continuam encerradas desde 16/09/2026 — a
contagem de cursos ambulatoriais, a figura do custo laboral e a citação direta
da Portaria GM/MS nº 7.177/2025. Abertas há **sete pendências**, listadas com
efeito e critério de fechamento no fim de
[02 — Conteúdo](02_conteudo_slides.md): as duas figuras do slide 4 fora do
pipeline (1) e a fonte primária do deslocamento por região (2), que são as que
tocam a regra de proveniência; o PDF da *Demografia Médica 2025* a registrar em
`data/raw/` com hash, depois de corrigido o número da dupla prática (3); a
tabela de inclinações pré/pós do deck do grupo, não reproduzível e por isso
mantida fora do slide 6 (4); o percentual do Sudeste conferido em cobertura e
não no PDF integral (5); os dois decks ainda na estrutura de 15 slides (6); e a
figura que falta ao slide 16 — IVS contra faixa publicada, com os cortes
marcados, que é o que sustenta o achado de viabilidade (7).
O rastreio número a número segue em
[03 — Proveniência](03_proveniencia_figuras_e_numeros.md#3-pendências-e-ressalvas).

## 5. Onde o conteúdo vive na documentação

Esta apresentação não cria conteúdo. Cada bloco tem um documento canônico de
origem, e é lá que a informação deve ser corrigida primeiro:

| Seção · slide | Documento canônico |
|---|---|
| 1 · problema (4) | fontes externas — *Demografia Médica no Brasil 2025* (FMUSP/AMB) e REGIC 2018 — e `output/aquisicao/quadro_vagas_tratamento.parquet`; rastreio em [03 — Proveniência](03_proveniencia_figuras_e_numeros.md) |
| 1 · política (5) | [`auditorias/01_regra_institucional.md`](../../auditorias/01_regra_institucional.md), o edital em `data/raw/aquisicao/ivs_regra/` e a reconstrução da regra em [`05_identificacao/14_...md`](../../05_identificacao/14_plano_implementacao_rdd_bolsa.md) |
| 1 · efeitos (6) | [`03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md), seção 7; números do ciclo 1 em `output/tema_trabalho/` (módulos A4 e A5) |
| 1 · pergunta de pesquisa (7) | [`01_pergunta_escopo/15_...md`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), "Formulação curta canônica" |
| 2 · visão geral (9) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 1 |
| 2 · custo da localidade (10) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 2.1 a 2.3 e 3.2 |
| 2 · remuneração da localidade (11) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 3, e [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 2 |
| 3 · implicações para o PMM-E (13) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 2.4, 3 e 3.1, e [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 3 |
| 3 · hipótese do trabalho (14) | [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 4, e [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 4.1 e 4.2 |
| 3 · disponibilidade de dados (15) | [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md) |
| 3 · desafio metodológico (16) | [`05_identificacao/14_...md`](../../05_identificacao/14_plano_implementacao_rdd_bolsa.md), [`05_identificacao/16_...md`](../../05_identificacao/16_sintese_achados_e_novo_plano_causal.md) e [`06_execucao/36_backlog_pos_auditoria.md`](../../06_execucao/36_backlog_pos_auditoria.md), item D-3 |

O histórico da reorganização que acompanhou esta entrega está em
[`docs/00_registro_mudancas.md`](../../00_registro_mudancas.md).

## 6. Defeitos do material anterior corrigidos aqui

O arquivo `PEE__Modelo_econômico.pptx` (11 slides) entrou nesta documentação já
corrigido. Os defeitos encontrados e o tratamento dado estão na seção 5 do
[roteiro narrativo](01_roteiro_narrativo.md#5-defeitos-do-material-anterior).
