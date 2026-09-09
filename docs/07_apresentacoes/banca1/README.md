# Banca 1 — apresentação do projeto

> **Formato:** markdown com imagens, para ler no GitHub ou no Obsidian<br>
> **Escopo:** três partes, terminando na viabilidade empírica<br>
> **Fora do escopo:** estratégia de identificação executada, estimadores, resultados e robustez<br>
> **Atualização:** 9 de setembro de 2026

## 1. O que esta entrega é

A banca 1 apresenta o **desenho conceitual** do trabalho, em três partes:

| Parte | Conteúdo |
|:---:|---|
| **I — Introdução** | Motivação, Pergunta — slides 3 a 6 |
| **II — Teoria** | Literatura teórica, Modelo microeconômico, Hipóteses — slides 7 a 10 |
| **III — Empiria** | Viabilidade empírica — slide 11 |

**A banca 1 é teórica.** Fora da motivação, nada de econometria ou estimação, e
o slide de literatura traz apenas trabalhos teóricos. A motivação é a exceção
declarada: ali, antes da pergunta, entra evidência sobre o que se pode esperar
da política.

A Parte III declara como cada hipótese aparece nos dados e por que separá-las é
difícil. A margem tratada é o **preenchimento** das vagas; permanência fica
fora. Não há slide de perguntas: a apresentação termina na viabilidade.
Nenhum resultado é apresentado, porque nenhum está autorizado a ser promovido a
evidência causal no estado atual do projeto — ver
[`docs/06_execucao/05_roadmap_execucao.md`](../../06_execucao/05_roadmap_execucao.md).

A cadeia narrativa é um recorte inicial da cadeia analítica do projeto:

```
implementação → força de trabalho → capacidade → acesso → saúde → custos → equidade
└──────────── escopo da banca 1 ────────────┘
```

## 2. Índice

| Documento | Função |
|---|---|
| [Conteúdo da apresentação](02_conteudo_slides.md) | **o documento principal** — os 11 slides, com título, corpo, figuras e fontes, para ler de ponta a ponta |
| [Roteiro narrativo](01_roteiro_narrativo.md) | arco das três partes, regras de composição e rastreio do feedback dos professores |
| [Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | origem e reprodutibilidade de cada número exibido |

## 3. Figuras

Todas as quatro figuras usadas são geradas por script ou são ilustração
conceitual do modelo. Nenhuma figura de fonte externa entra no deck.

| Figura | Slide | Origem |
|---|:---:|---|
| Especialistas por 100 mil habitantes por faixa | 3 | CNES + Censo 2022 |
| Colegas da mesma especialidade por faixa | 3 | CNES |
| Bolsa mensal por faixa | 4 | edital |
| Curva de custo laboral | 9 | ilustração do modelo |

Para regerar:

```bash
python3 scripts/aquisicao/06_adquirir_populacao_censo2022.py   # denominador, uma vez
python3 scripts/apresentacao/gerar_figuras_banca1.py
```

As imagens em `figuras/` são material do deck anterior, preservado mas **não
usado**. Ver [03 — Proveniência](03_proveniencia_figuras_e_numeros.md#figuras-geradas-e-não-usadas).

## 4. Estado

| Parte | Slides | Conteúdo | Figuras | Proveniência |
|---|:---:|:---:|:---:|:---:|
| Capa e sumário | 1–2 | ✅ | — | — |
| I — Introdução | 3–6 | ✅ | ✅ | ✅ |
| II — Teoria | 7–10 | ✅ | ✅ | ✅ |
| III — Empiria | 11 | ✅ | — | ✅ |

Três ressalvas registradas, nenhuma bloqueante: a régua de 35–65% ser síntese do
projeto, a comparabilidade do prêmio com uma bolsa de 20 horas, e o denominador
populacional. Reinhardt foi retirado do slide 7 — ver a mesma seção. Detalhe em
[03 — Proveniência](03_proveniencia_figuras_e_numeros.md#3-pendências-e-ressalvas).

## 5. Onde o conteúdo vive na documentação

Esta apresentação não cria conteúdo. Cada parte tem um documento canônico de
origem, e é lá que a informação deve ser corrigida primeiro:

| Parte | Documento canônico |
|---|---|
| Pergunta | [`01_pergunta_escopo/15_...md`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), "Formulação curta canônica" |
| Literatura teórica | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 5 |
| Evidência sobre incentivos (só na motivação) | [`03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md), seção 7 |
| Modelo micro | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 1 a 4 |
| Hipóteses | [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 4 |
| Viabilidade empírica | [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md) e [`auditorias/08_portao_denominador_atracao.md`](../../auditorias/08_portao_denominador_atracao.md) |

O histórico da reorganização que acompanhou esta entrega está em
[`docs/00_registro_mudancas.md`](../../00_registro_mudancas.md).

## 6. Defeitos do material anterior corrigidos aqui

O arquivo `PEE__Modelo_econômico.pptx` (11 slides) entrou nesta documentação já
corrigido. Os defeitos encontrados e o tratamento dado estão na seção 4 do
[roteiro narrativo](01_roteiro_narrativo.md#4-defeitos-do-deck-anterior-e-tratamento).
