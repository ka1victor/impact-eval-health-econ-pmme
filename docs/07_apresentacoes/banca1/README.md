# Banca 1 — apresentação do projeto

> **Formato:** markdown com imagens, para ler no GitHub ou no Obsidian<br>
> **Escopo:** seis seções, terminando na viabilidade empírica<br>
> **Fora do escopo:** estratégia de identificação executada, estimadores, resultados e robustez<br>
> **Atualização:** 16 de setembro de 2026

## 1. O que esta entrega é

A banca 1 apresenta a **fundamentação teórica** do trabalho, em seis seções.
Cada seção ocupa quantos slides o argumento pedir — e, desde o corte de
16/09/2026, nenhum a mais.

| Seção | Slides | Conteúdo |
|---|:---:|---|
| **1. Motivação** | 3–8 | problema (retrato nacional e as desvantagens na visão do médico, num slide), política (o que é o PMM-E; a regra da bolsa) e efeito incerto (onde a bolsa é maior; a evidência a favor e contra; o ciclo 1) |
| **2. Pergunta** | 9 | a pergunta e sua leitura em dois objetos |
| **3. Literatura teórica** | 10–11 | a estrutura da decisão; o custo aberto em lugar e trabalho |
| **4. Modelo microeconômico** | 12–13 | a junção das três tradições; o que a bolsa paga e o IVS como organizador do custo |
| **5. Hipótese** | 14 | derivação em quatro passos, com uma hipótese |
| **6. Viabilidade empírica** | 15 | o que se mede, o que a reconstrução da regra mostrou, o que fica de pé |

**A banca 1 é teórica.** Fora da motivação, nada de econometria ou estimação, e
os slides de literatura trazem apenas trabalhos teóricos. A motivação é a
exceção declarada: ali, antes da pergunta, entra evidência sobre o que se pode
esperar da política.

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
| [Conteúdo da apresentação](02_conteudo_slides.md) | **a fonte de verdade** — os 15 slides com título, corpo, figuras, fontes e ressalvas. Diz exatamente o que vai à tela, e nada além; os decks derivam dele |
| [Roteiro narrativo](01_roteiro_narrativo.md) | arco das seis seções, lógica de cada bloco da motivação, regras de composição, rastreio do feedback e histórico das revisões, inclusive o corte de 16/09/2026 (seção 4d) |
| [Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | origem e reprodutibilidade de cada número exibido |
| [Deck Beamer](deck_beamer/) · [Deck Slidev](deck_slidev/) | artefatos derivados, com script de build cada um; PDFs em `output/apresentacao_banca1/` |

## 3. Figuras

As quatro figuras usadas são geradas por script. Nenhuma figura de fonte
externa entra no deck; números externos entram em texto, com fonte.

| Figura | Slide | Origem |
|---|:---:|---|
| Bolsa mensal por faixa | 5 | edital |
| Especialistas por 100 mil habitantes por faixa publicada | 6 | CNES + Censo 2022 |
| Colegas da mesma especialidade por faixa publicada | 6 | CNES |
| Preenchimento do ciclo 1 por faixa e por estrato | 8 | tabelas descritivas do módulo A4 |

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

Para reconstruir os decks:

```bash
bash scripts/apresentacao/build_deck_beamer.sh        # pdflatex, 15 frames
bash scripts/apresentacao/build_deck_slidev.sh        # Node 22, Chromium local
```

## 4. Estado

| Seção | Slides | Conteúdo | Figuras | Proveniência |
|---|:---:|:---:|:---:|:---:|
| Capa e sumário | 1–2 | ✅ | — | — |
| 1. Motivação | 3–8 | ✅ | ✅ | ✅ |
| 2. Pergunta | 9 | ✅ | — | — |
| 3. Literatura teórica | 10–11 | ✅ | — | ✅ |
| 4. Modelo microeconômico | 12–13 | ✅ | — | ✅ |
| 5. Hipótese | 14 | ✅ | — | — |
| 6. Viabilidade empírica | 15 | ✅ | — | ✅ |

Cinco ressalvas de proveniência registradas, nenhuma bloqueante: a comparação
do degrau com a régua australiana ser leitura do projeto, a comparabilidade do
prêmio com uma bolsa de 20 horas, o denominador populacional, a diferença entre
faixa recalculada e faixa publicada, e a Demografia Médica 2025 conferida em
cobertura e não no PDF. Detalhe em
[03 — Proveniência](03_proveniencia_figuras_e_numeros.md#3-pendências-e-ressalvas).
As duas ressalvas de conteúdo que estavam abertas — a contagem de cursos
ambulatoriais e a legibilidade da figura do custo laboral — foram encerradas
em 16/09/2026; ver o fim de [02 — Conteúdo](02_conteudo_slides.md).

## 5. Onde o conteúdo vive na documentação

Esta apresentação não cria conteúdo. Cada seção tem um documento canônico de
origem, e é lá que a informação deve ser corrigida primeiro:

| Seção | Documento canônico |
|---|---|
| Motivação · política | [`auditorias/01_regra_institucional.md`](../../auditorias/01_regra_institucional.md), o edital em `data/raw/aquisicao/ivs_regra/` e a reconstrução da regra em [`05_identificacao/14_...md`](../../05_identificacao/14_plano_implementacao_rdd_bolsa.md) |
| Motivação · efeito incerto | [`03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md), seção 7 |
| Pergunta | [`01_pergunta_escopo/15_...md`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), "Formulação curta canônica" |
| Literatura teórica | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 1, 2 e 5 |
| Modelo micro | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 2.4 e 3 |
| Hipótese | [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 4 |
| Viabilidade empírica | [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md), [`05_identificacao/14_...md`](../../05_identificacao/14_plano_implementacao_rdd_bolsa.md) e [`06_execucao/36_backlog_pos_auditoria.md`](../../06_execucao/36_backlog_pos_auditoria.md), item D-3 |

O histórico da reorganização que acompanhou esta entrega está em
[`docs/00_registro_mudancas.md`](../../00_registro_mudancas.md).

## 6. Defeitos do material anterior corrigidos aqui

O arquivo `PEE__Modelo_econômico.pptx` (11 slides) entrou nesta documentação já
corrigido. Os defeitos encontrados e o tratamento dado estão na seção 5 do
[roteiro narrativo](01_roteiro_narrativo.md#5-defeitos-do-material-anterior).
