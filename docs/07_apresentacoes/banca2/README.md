# Banca 2 — resultados da RDD da bolsa (28/10/2026)

> **Formato:** markdown com imagens, para ler no GitHub ou no Obsidian<br>
> **Estado:** **RASCUNHO**. Depende de duas decisões do autor: (1) a revisão
> da hipótese econômica proposta no
> [doc 44, §7](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md#7-revisão-da-pergunta-e-da-hipótese-econômica-proposta-ao-autor-não-decisão)
> — manter H1 e relatar o nulo, ou adotar a proposta A, B ou C —; (2) a
> **mensagem principal** da apresentação (ver §3). Até lá, os slides 20 e 21
> e o título da capa ficam em aberto, e o resto não muda.<br>
> **Escopo:** da hipótese levada à banca 1 até o que a RDD da bolsa permite
> afirmar, elo a elo da cadeia, e as opções de revisão da hipótese<br>
> **Fora do escopo:** o deck (`.pptx`/`.tex`), que é derivado deste conteúdo e
> não foi montado; o ciclo 3 pós-T0, congelado; pedidos externos de dados<br>
> **Atualização:** 19 de outubro de 2026

## 1. O que esta entrega é

O conteúdo canônico da apresentação de 28/10/2026, no padrão da
[banca 1](../banca1/README.md): o roteiro, o conteúdo slide a slide e a
proveniência de cada número e de cada figura. Divergência entre um deck
futuro e estes arquivos é erro do deck (`CLAUDE.md`).

A banca 1 terminou na viabilidade empírica, com a hipótese *"municípios com
maior remuneração oferecida pelo PMM-E têm maior preenchimento de vagas"*. A
banca 2 diz o que aconteceu com essa hipótese: a regra da bolsa foi
reconstruída com o IVS 2010 oficial, o desenho de descontinuidade foi
estimado sob protocolo congelado, e a resposta, elo a elo, é a da síntese
[E8 (doc 44)](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md).

| Seção | Slides | Conteúdo |
|---|:---:|---|
| **Capa e sumário** | 1–2 | |
| **1. Da hipótese à regra** | 3–6 | a hipótese da banca 1; a regra com o IVS oficial; o failure mode do arquivo errado |
| **2. Desenho** | 7–8 | três contrastes, nenhum é "o efeito do PMM-E" |
| **3. Resultados, elo a elo** | 9–16 | a cadeia em uma figura; primárias com Holm; atração; o que o IC descarta; escolha (E9); presença e oferta no CNES (E7); os p < 0,05 isolados |
| **4. Leitura e revisão** | 17–21 | o que podemos e não podemos afirmar; co-políticas nos mesmos cortes; opções de revisão da hipótese; o que vem depois |
| **Apêndice** | B1–B7 | fora da contagem |

## 2. Índice

| Documento | Função |
|---|---|
| [Roteiro narrativo](01_roteiro_narrativo.md) | o arco, a lógica de cada bloco, as frases que não podem mudar e as que dependem do autor |
| [Conteúdo da apresentação](02_conteudo_slides.md) | **a fonte de verdade** — 21 slides e 7 de apêndice, com título, afirmação, figura com caminho exato, linha de números e notas do apresentador |
| [Plano da entrega empírica](04_plano_entrega_empirica.md) | revisão de 26/10/2026: o que falta por bloco da banca, erros do deck atual, proposta de hipóteses pela cadeia do modelo e tarefas até 28/10 e 04/11 |
| [Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | cada figura → arquivo, script e natureza; cada número → arquivo, chave e formato, num bloco gerado pelo script |
| [Relatório de validação para os professores](../../../output/apresentacao_validacao/relatorio_validacao_rdd_bolsa.pdf) | relatório curto (derivado, gerado por `scripts/apresentacao/gerar_relatorio_validacao_professores.py`) com o desenho, os diagnósticos e os resultados atuais, para validação metodológica; não é o deck |

## 3. Decisões em aberto do autor

| Decisão | Opções | Onde pesa |
|---|---|---|
| Revisão da hipótese (doc 44, §7) | manter H1 como pergunta e relatar o nulo; A — realocação entre vagas sem expansão líquida detectável; B — elasticidade da escolha à remuneração, relativa aos fatores não pecuniários; C — "quanto e em que margem?" | slide 20 e o fecho do roteiro |
| Mensagem principal | ver as três candidatas em [01, §3](01_roteiro_narrativo.md#3-a-mensagem-principal-decisão-do-autor) | capa, slide 10 e fecho |
| Título da capa | provisório; ver nota de produção do slide 1 | slide 1 |

Nenhuma das opções muda um número ou uma figura. Todas preservam a frase
segura dos nulos e a distinção entre pacote, DiRD e escolha.

## 4. Figuras

Todas saem do pipeline. As que já existiam vêm das etapas E6, E7 e E9 da RDD
(`output/rdd_bolsa/E6_figuras/`, `E7_figuras/`, `E9_figuras/`). As que
faltavam — a figura da regra em arquivo próprio, a da cadeia e a do descarte —
são geradas por
[`scripts/apresentacao/gerar_figuras_banca2.py`](../../../scripts/apresentacao/gerar_figuras_banca2.py)
em `output/apresentacao_banca2/`, com manifesto e hashes. A figura da regra é
a **variante A colorida** escolhida pelo autor (doc 38, D1), desenhada pela
mesma função do relatório. A figura do arquivo errado fica em
`output/apresentacao_banca2/failure_mode/`, rotulada `FAILURE_MODE`.

Para regerar:

```bash
python3 scripts/apresentacao/gerar_figuras_banca2.py                  # figuras, números e bloco do 03
python3 scripts/apresentacao/gerar_figuras_banca2.py --atualizar-doc  # só o bloco do 03
python3 -m unittest tests.test_conteudo_banca2
```

O script não está no `run_all.py`; a inclusão fica para o coordenador do
pipeline.

## 5. Estado

| Seção | Conteúdo | Figuras | Proveniência |
|---|:---:|:---:|:---:|
| Capa e sumário | ⚠️ título provisório | — | — |
| 1. Da hipótese à regra | ✅ | ✅ | ✅ |
| 2. Desenho | ✅ | — | ✅ |
| 3. Resultados, elo a elo | ✅ | ✅ | ✅ |
| 4. Leitura e revisão | ⚠️ depende da decisão do autor | — | ✅ |

Proveniência ✅ quer dizer: todo número no corpo, nas notas e nos títulos
está registrado no bloco gerado de [03](03_proveniencia_figuras_e_numeros.md)
e conferido por `tests/test_conteudo_banca2.py` contra os arquivos de
`output/`; toda figura existe e foi produzida por script versionado.

## 6. Onde o conteúdo vive na documentação

| Bloco | Documento canônico |
|---|---|
| hipótese (4) | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), §4.2; banca 1, [versão apresentada](../banca1/04_versao_apresentada.md) |
| regra e failure mode (5–6) | [`auditorias/16`](../../auditorias/16_ivs_2010_oficial_e_arquivo_local.md), [`auditorias/19`](../../auditorias/19_reestimacao_base_oficial_failure_mode.md) |
| desenho (8) | [`06_execucao/40`](../../06_execucao/40_protocolo_multioutcome_rdd_bolsa.md), §3, §6 e §7 |
| resultados (10–16) | [`06_execucao/44`](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md); detalhes em [`37`](../../06_execucao/37_resultados_rdd_bolsa_ivs_oficial.md), [`39`](../../06_execucao/39_inferencia_alternativa_rdd_bolsa.md), [`41`](../../06_execucao/41_resultados_E6_funil.md), [`42`](../../06_execucao/42_resultados_E9_escolha.md), [`43`](../../06_execucao/43_resultados_E7_dird_cnes.md) |
| co-políticas (19) | [`auditorias/18`](../../auditorias/18_politicas_nos_mesmos_cortes_ivs.md), §3 |
| revisão da hipótese (20) | [`06_execucao/44`](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md), §7 |
| estado e pendências | [`06_execucao/38`](../../06_execucao/38_estado_e_pendencias_rdd_bolsa.md) |
