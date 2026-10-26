# Banca 2 — hipótese pela cadeia do modelo, dados, metodologia e resultados (28/10 e 04/11/2026)

> **Formato:** markdown com imagens, para ler no GitHub ou no Obsidian; o deck
> `.pptx` é derivado<br>
> **Estado:** **PRONTO** para 28/10, com a **H3 PENDENTE**: o resultado vem do
> protocolo 52b (script 25c, doc 57i), em estimação em outra sessão e sujeito
> a auditoria independente. O slide da H3 está reservado e marcado.<br>
> **Escopo:** os slides novos da banca 2 (hipótese econômica pela cadeia do
> modelo; base de dados e descritivas; metodologia econométrica e
> identificação; resultados, robustez e discussão) e as correções no deck do
> grupo<br>
> **Fora do escopo:** o ciclo 3 pós-T0, congelado; pedidos externos de dados;
> a banca final (`../banca_final/`)<br>
> **Atualização:** 26 de outubro de 2026

## 1. O que esta entrega é

O conteúdo canônico da parte empírica da banca 2, no padrão da
[banca 1](../banca1/README.md): o roteiro, o conteúdo slide a slide e a
proveniência de cada número e de cada figura. O deck do grupo (template
Insper, 36 slides) continua sendo o deck: os slides novos entram nos
marcadores "X" e na seção de hipótese. Divergência entre o deck e estes
arquivos é erro do deck (`CLAUDE.md`).

A síntese vigente dos resultados é a do
[doc 57](../../06_execucao/57_sintese_perguntas_reformuladas.md), com os blocos
57a–57h; a anterior, de 19/10, é a do
[doc 44](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md), que segue
valendo para o E9, o E7 e a literatura de magnitude.

## 2. Índice

| Documento | Função |
|---|---|
| [Plano da entrega empírica](04_plano_entrega_empirica.md) | o que falta por bloco da banca, erros do deck, hipóteses pela cadeia do modelo, metodologia econométrica e o registro de decisões |
| [Roteiro narrativo](01_roteiro_narrativo.md) | o arco, a lógica de cada bloco e as frases que não podem mudar |
| [Conteúdo da apresentação](02_conteudo_slides.md) | **a fonte de verdade** — slides novos com título, figura, tabela, números, cautela e notas; o quadro de correções do deck do grupo |
| [Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | cada figura → arquivo, script e natureza; cada número → arquivo, seletor e formato, num bloco gerado pelo script |
| [Relatório de validação para os professores](../../../output/apresentacao_validacao/relatorio_validacao_rdd_bolsa.pdf) | relatório curto (derivado) com o desenho, os diagnósticos e os resultados de 19/10; não é o deck |

## 3. Decisões

| Data | Decisão | Quem |
|---|---|---|
| 26/10/2026 | "Metodologia" é a metodologia **econométrica** | autor |
| 26/10/2026 | o arco testa cada seta do modelo: H1 preenchimento, H2 escolha, H3 incentivo limitado, H4 capacidade líquida; H3 central como proposta revisável | autor delegou (plano, §9) |
| 26/10/2026 | a variável de efeito da H1 é o número de vagas preenchidas controlando as vagas oferecidas (N1), com a célula aberta (A3) e o que o IC descarta | grupo e autor |
| 26/10/2026 | a H3 entra só depois da auditoria do protocolo 52b; até lá, slide PENDENTE | plano, §6.1 |

Em aberto com o autor: a hipótese central (H3 ou H1), já revisável; quem
apresenta em 28/10 e quem em 04/11.

## 4. Figuras, tabelas e deck

Tudo sai do pipeline, lendo só de `output/`:

```bash
python3 scripts/apresentacao/gerar_figuras_banca2.py                 # figuras, tabelas, números e bloco do 03
PMME_DECK_GRUPO="<deck do grupo>" python3 scripts/apresentacao/gerar_deck_banca2.py   # deck
PMME_DECK_GRUPO="<deck do grupo>" python3 -m unittest tests.test_conteudo_banca2
```

Saídas em `output/apresentacao_banca2/`: as figuras (`h1_preenchimento.png`,
`h2_escolha.png`, `h4_horas_medico.png`, `cadeia_resumo_doc57.png`,
`regra_bolsa_ivs_oficial.png`), as tabelas (`tabela_descritiva_ciclos` e
`tabela_fontes`, em CSV e PNG), o registro de números
(`numeros_banca2.json`), o manifesto das figuras, o deck proposto
(`deck_banca2_proposta.pptx`), só os slides novos
(`slides_empiricos_banca2.pptx`), o manifesto do deck e as imagens de
conferência em `qa_render/`. Os geradores não estão no `run_all.py`; a
inclusão fica para o coordenador do pipeline.

## 5. Estado

| Bloco | Conteúdo | Figuras | Proveniência |
|---|:---:|:---:|:---:|
| Hipótese econômica | ✅ | ✅ (formas nativas) | ✅ |
| Base de dados e descritivas | ✅ | ✅ (tabelas nativas) | ✅ |
| Metodologia econométrica | ✅ | ✅ (tabelas nativas) | ✅ |
| Resultados: regra, H1, H2, H4, cadeia | ✅ | ✅ | ✅ |
| Resultados: H3 | ⚠️ PENDENTE | ⚠️ | — |
| Robustez e discussão | ✅ | ✅ | ✅ |
| Correções no deck do grupo | ✅ | — | ✅ |

Proveniência ✅ quer dizer: todo número no corpo, nas notas e nos títulos
está registrado no bloco gerado de [03](03_proveniencia_figuras_e_numeros.md)
e conferido por `tests/test_conteudo_banca2.py` contra os arquivos de
`output/`; toda figura existe e foi produzida por script versionado.

## 6. Onde o conteúdo vive na documentação

| Bloco | Documento canônico |
|---|---|
| hipótese e modelo | [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md); plano, §3 e §4.3 |
| regra e failure mode | [`auditorias/16`](../../auditorias/16_ivs_2010_oficial_e_arquivo_local.md), [`auditorias/19`](../../auditorias/19_reestimacao_base_oficial_failure_mode.md) |
| H1 | [`06_execucao/49`](../../06_execucao/49_resultados_contagem_vagas_preenchidas.md), §3 e §15; [`49b`](../../06_execucao/49b_diagnostico_contagem_porte.md) |
| H2 | [`06_execucao/57a`](../../06_execucao/57a_resultados_P1_escolha.md); E9 no [doc 44](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md), §5.2 |
| H3 | [`06_execucao/52b`](../../06_execucao/52b_protocolo_P1h_magnitudes.md) (protocolo; resultado pendente) |
| H4 | [`06_execucao/57d`](../../06_execucao/57d_resultados_P4_trajetoria.md), [`57f`](../../06_execucao/57f_resultados_P6_mecanismo.md), [`57h`](../../06_execucao/57h_resultados_P3P4_sensibilidade.md) |
| síntese e cadeia | [`06_execucao/57`](../../06_execucao/57_sintese_perguntas_reformuladas.md) |
| co-políticas | [`auditorias/18`](../../auditorias/18_politicas_nos_mesmos_cortes_ivs.md) |
| literatura de magnitude | [`06_execucao/44`](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md), §6 |
