# Banca 1 — apresentação do projeto

> **Classificação:** conteúdo de apresentação, derivado dos documentos canônicos<br>
> **Escopo da entrega:** motivação, pergunta, literatura, modelo teórico, hipóteses e viabilidade empírica<br>
> **Fora do escopo:** estratégia de identificação executada, estimadores, resultados e robustez<br>
> **Atualização:** 9 de setembro de 2026

## 1. O que esta entrega é

A banca 1 apresenta o **desenho conceitual** do trabalho e termina na
viabilidade empírica, onde apenas se declara **onde estão os dados** e o que
ainda falta adquirir. Nenhum resultado é apresentado, porque nenhum resultado
está autorizado a ser promovido a evidência causal no estado atual do projeto
(ver [`docs/06_execucao/05_roadmap_execucao.md`](../../06_execucao/05_roadmap_execucao.md)).

A cadeia narrativa da apresentação é um recorte inicial da cadeia analítica do
projeto:

```
implementação → força de trabalho → capacidade → acesso → saúde → custos → equidade
└──────────── escopo da banca 1 ────────────┘
```

## 2. Índice

| Documento | Função |
|---|---|
| [01 — Roteiro narrativo](01_roteiro_narrativo.md) | arco da apresentação, regras de título e rastreio do feedback da banca prévia |
| [02 — Conteúdo dos slides](02_conteudo_slides.md) | **fonte de verdade do deck**: título-takeaway, corpo, visual e fonte de cada slide |
| [03 — Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | origem, reprodutibilidade e pendências de cada número exibido |

## 3. Estado da entrega

| Bloco | Conteúdo definido | Visual definido | Proveniência fechada |
|---|:---:|:---:|:---:|
| Capa e roteiro | sim | sim | não se aplica |
| I. Motivação — a dor | sim | sim | **não** (2 gráficos externos sem manifesto) |
| I. Motivação — a política | sim | sim | sim |
| I. Motivação — efeitos observados | sim | sim | **não** (série do gráfico diverge do repositório) |
| II. Pergunta | sim | sim | não se aplica |
| III. Literatura | sim | sim | sim |
| IV. Modelo teórico | sim | parcial (falta figura da condição de aceitação) | sim |
| V. Hipóteses | sim | sim | sim |
| VI. Viabilidade empírica | sim | sim | sim |

## 4. Pendências bloqueantes antes de diagramar o deck final

1. **Regenerar por script** o gráfico de distribuição regional do PMM-E. A série
   exibida no deck anterior não é reprodutível a partir de `data/` — detalhe em
   [03 — Proveniência](03_proveniencia_figuras_e_numeros.md#p1--distribuição-regional-do-pmm-e).
2. **Registrar manifesto** das duas figuras derivadas de fontes externas
   (Demografia Médica 2025 e REGIC 2018), com edição, tabela, data de referência
   e hash, conforme a regra de proveniência do projeto.
3. **Produzir a figura da condição de aceitação** (slide 12), hoje inexistente.

Nenhuma dessas pendências impede escrever o deck em LaTeX: as três são de
figura e manifesto, não de conteúdo. O conteúdo textual está congelado.

## 5. Defeitos do deck anterior corrigidos aqui

O arquivo `PEE__Modelo_econômico.pptx` (11 slides) entrou nesta documentação já
corrigido. Os defeitos encontrados e o tratamento dado estão registrados na
seção 4 do [roteiro narrativo](01_roteiro_narrativo.md#4-defeitos-do-deck-anterior-e-tratamento).
