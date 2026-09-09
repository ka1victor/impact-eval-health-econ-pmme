# Banca 1 — apresentação do projeto

> **Formato:** markdown com imagens, para ler no GitHub ou no Obsidian<br>
> **Escopo:** seis seções, terminando na viabilidade empírica<br>
> **Fora do escopo:** estratégia de identificação executada, estimadores, resultados e robustez<br>
> **Atualização:** 9 de setembro de 2026

## 1. O que esta entrega é

A banca 1 apresenta a **fundamentação teórica** do trabalho, em seis seções.
Cada seção ocupa quantos slides o argumento pedir.

| Seção | Slides | Conteúdo |
|---|:---:|---|
| **1. Motivação** | 3–10 | problema (retrato nacional; os dados do programa; as desvantagens na visão do médico), política (o que é o PMM-E; a regra da bolsa) e efeito incerto (a favor; contra; o ciclo 1) |
| **2. Pergunta** | 11 | a pergunta e sua leitura em dois objetos |
| **3. Literatura teórica** | 12 | as três tradições que o modelo junta |
| **4. Modelo microeconômico** | 13–16 | decisão; remuneração; custo; o IVS como organizador do custo |
| **5. Hipóteses** | 17 | derivação em quatro passos |
| **6. Viabilidade empírica** | 18 | o que se mede, o que falta, a dificuldade |

**A banca 1 é teórica.** Fora da motivação, nada de econometria ou estimação, e
o slide de literatura traz apenas trabalhos teóricos. A motivação é a exceção
declarada: ali, antes da pergunta, entra evidência sobre o que se pode esperar
da política.

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
| [Conteúdo da apresentação](02_conteudo_slides.md) | **o documento principal** — os 18 slides, com título, corpo, figuras e fontes, para ler de ponta a ponta |
| [Roteiro narrativo](01_roteiro_narrativo.md) | arco das seis seções, lógica de cada bloco da motivação, regras de composição e rastreio do feedback |
| [Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | origem e reprodutibilidade de cada número exibido |

## 3. Figuras

Todas as seis figuras usadas são geradas por script ou são ilustração
conceitual do modelo. Nenhuma figura de fonte externa entra no deck; números
externos entram em texto, com fonte.

| Figura | Slide | Origem |
|---|:---:|---|
| Especialistas por 100 mil habitantes por faixa | 4 | CNES + Censo 2022 |
| Colegas da mesma especialidade por faixa | 4 | CNES |
| Células e vagas imediatas do ciclo 1 por região | 6 | quadro de vagas |
| Bolsa mensal por faixa | 7 | edital |
| Preenchimento do ciclo 1 por faixa e por estrato | 10 | tabelas descritivas do módulo A4 |
| Curva de custo laboral | 15 | ilustração do modelo |

Para regerar:

```bash
python3 scripts/aquisicao/06_adquirir_populacao_censo2022.py   # denominador, uma vez
python3 scripts/apresentacao/gerar_figuras_banca1.py
```

As imagens em `figuras/` são material do deck anterior, preservado mas **não
usado**. Ver [03 — Proveniência](03_proveniencia_figuras_e_numeros.md#figuras-geradas-e-não-usadas).

## 4. Estado

| Seção | Slides | Conteúdo | Figuras | Proveniência |
|---|:---:|:---:|:---:|:---:|
| Capa e sumário | 1–2 | ✅ | — | — |
| 1. Motivação | 3–10 | ✅ | ✅ | ✅ |
| 2. Pergunta | 11 | ✅ | — | — |
| 3. Literatura teórica | 12 | ✅ | — | ✅ |
| 4. Modelo microeconômico | 13–16 | ✅ | ✅ | ✅ |
| 5. Hipóteses | 17 | ✅ | — | — |
| 6. Viabilidade empírica | 18 | ✅ | — | ✅ |

Cinco ressalvas registradas, nenhuma bloqueante: a comparação do degrau com a
régua australiana ser leitura do projeto, a comparabilidade do prêmio com uma
bolsa de 20 horas, o denominador populacional, a diferença entre faixa
recalculada e faixa publicada nas figuras, e a Demografia Médica 2025
conferida em cobertura e não no PDF. Detalhe em
[03 — Proveniência](03_proveniencia_figuras_e_numeros.md#3-pendências-e-ressalvas).

## 5. Onde o conteúdo vive na documentação

Esta apresentação não cria conteúdo. Cada seção tem um documento canônico de
origem, e é lá que a informação deve ser corrigida primeiro:

| Seção | Documento canônico |
|---|---|
| Motivação · política | [`auditorias/01_regra_institucional.md`](../../auditorias/01_regra_institucional.md) e o edital em `data/raw/aquisicao/ivs_regra/` |
| Motivação · efeito incerto | [`03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md), seção 7 |
| Pergunta | [`01_pergunta_escopo/15_...md`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), "Formulação curta canônica" |
| Literatura teórica | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 5 |
| Modelo micro | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 1 a 4 |
| Hipóteses | [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 4 |
| Viabilidade empírica | [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md) e [`auditorias/08_portao_denominador_atracao.md`](../../auditorias/08_portao_denominador_atracao.md) |

O histórico da reorganização que acompanhou esta entrega está em
[`docs/00_registro_mudancas.md`](../../00_registro_mudancas.md).

## 6. Defeitos do material anterior corrigidos aqui

O arquivo `PEE__Modelo_econômico.pptx` (11 slides) entrou nesta documentação já
corrigido. Os defeitos encontrados e o tratamento dado estão na seção 5 do
[roteiro narrativo](01_roteiro_narrativo.md#5-defeitos-do-material-anterior).
