# Banca 1 — apresentação do projeto

> **Formato:** markdown com imagens, para ler no GitHub ou no Obsidian<br>
> **Escopo:** três partes, terminando na viabilidade empírica<br>
> **Fora do escopo:** estratégia de identificação executada, estimadores, resultados e robustez<br>
> **Atualização:** 9 de setembro de 2026

## 1. O que esta entrega é

A banca 1 apresenta o **desenho conceitual** do trabalho, em três partes:

| Parte | Conteúdo |
|:---:|---|
| **1** | Motivação e pergunta |
| **2** | Literatura teórica, modelo micro e hipóteses |
| **3** | Viabilidade empírica |

A Parte 3 apenas declara **onde estão os dados** e o que ainda falta adquirir.
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
| [Conteúdo da apresentação](02_conteudo_slides.md) | **o documento principal** — os 15 slides, com título, corpo, figuras e notas, para ler de ponta a ponta |
| [Roteiro narrativo](01_roteiro_narrativo.md) | arco das três partes, regras de composição e rastreio do feedback dos professores |
| [Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | origem e reprodutibilidade de cada número exibido |

## 3. Figuras

| Onde | O quê |
|---|---|
| `figuras/` | imagens de fonte externa, preservadas do material anterior: manchetes, especialistas por UF e deslocamento por região |
| `output/apresentacao_banca1/` | figuras geradas por [`scripts/apresentacao/gerar_figuras_banca1.py`](../../../scripts/apresentacao/gerar_figuras_banca1.py): bolsa por faixa e distribuição regional, com manifesto e hash da base de entrada |

Para regerar:

```bash
python3 scripts/apresentacao/gerar_figuras_banca1.py
```

## 4. Estado

| Parte | Conteúdo | Figuras | Proveniência |
|---|:---:|:---:|:---:|
| Capa e roteiro | ✅ | não se aplica | não se aplica |
| 1. Motivação e pergunta | ✅ | ✅ | ⚠️ duas figuras externas sem manifesto |
| 2. Literatura, modelo e hipóteses | ✅ | não usa figura | ✅ |
| 3. Viabilidade empírica | ✅ | não usa figura | ✅ |

Uma pendência aberta, não bloqueante: registrar edição, tabela, data e hash das
duas figuras de fonte externa. Detalhe em
[03 — Proveniência](03_proveniencia_figuras_e_numeros.md#3-pendência-aberta).

## 5. Onde o conteúdo vive na documentação

Esta apresentação não cria conteúdo. Cada parte tem um documento canônico de
origem, e é lá que a informação deve ser corrigida primeiro:

| Parte | Documento canônico |
|---|---|
| Pergunta | [`01_pergunta_escopo/15_...md`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), "Formulação curta canônica" |
| Literatura teórica | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 5, e [`03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md), seções 2 e 7 |
| Modelo micro | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 1 a 4 |
| Hipóteses | [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 4 |
| Viabilidade empírica | [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md) e [`auditorias/08_portao_denominador_atracao.md`](../../auditorias/08_portao_denominador_atracao.md) |

O histórico da reorganização que acompanhou esta entrega está em
[`docs/00_registro_mudancas.md`](../../00_registro_mudancas.md).

## 6. Defeitos do material anterior corrigidos aqui

O arquivo `PEE__Modelo_econômico.pptx` (11 slides) entrou nesta documentação já
corrigido. Os defeitos encontrados e o tratamento dado estão na seção 4 do
[roteiro narrativo](01_roteiro_narrativo.md#4-defeitos-do-deck-anterior-e-tratamento).
