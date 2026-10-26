# 07 — Apresentações

> **Finalidade:** manter, para cada banca ou seminário, uma versão canônica do
> conteúdo apresentado, separada dos documentos de pesquisa que a fundamentam.

## 1. Regra da seção

1. Esta seção **não cria conteúdo novo**. Todo número, equação ou afirmação
   apresentada em slide deve ter origem declarada em um documento canônico das
   seções 01–06 ou em fonte externa citada com edição, tabela e data.
2. O conteúdo vive em markdown, com as figuras versionadas junto. Qualquer deck
   montado a partir dele — `.pptx`, `.tex` ou outro — é artefato derivado.
3. Quando um número exibido em slide não for reprodutível por script do
   repositório, isso é registrado como pendência de proveniência antes da
   apresentação, e não depois.
4. Feedback de banca é registrado no roteiro da apresentação correspondente, com
   o ajuste que ele produziu. Feedback sem ajuste rastreável não é considerado
   incorporado.

## 2. Apresentações

| Apresentação | Escopo | Estado | Documentos |
|---|---|---|---|
| [Banca 1](banca1/) | **apresentada** em cinco seções — motivação, pergunta, literatura, hipótese e viabilidade empírica —, 21 páginas, 17 numeradas; a versão de preparação de 21/09/2026 tinha 17 slides em três seções | versão apresentada transcrita, com errata e proveniência, e o PDF exibido; a versão de preparação segue em markdown, com figuras, e é dela que derivam os decks Beamer e Slidev, que **não** reproduzem a versão apresentada | [README](banca1/README.md), [**versão apresentada**](banca1/04_versao_apresentada.md), [PDF exibido](banca1/apresentada/banca1_apresentada.pdf), [roteiro](banca1/01_roteiro_narrativo.md), [conteúdo de preparação](banca1/02_conteudo_slides.md), [proveniência](banca1/03_proveniencia_figuras_e_numeros.md) |
| [Banca 2](banca2/) | parte empírica para 28/10 e 04/11/2026: hipóteses H1–H4 pela cadeia do modelo, base de dados e descritivas, metodologia econométrica e identificação, resultados (doc 57), robustez e discussão; correções no deck do grupo | conteúdo canônico **pronto**, com a H3 **pendente** (protocolo 52b); figuras e tabelas do pipeline; deck derivado em `output/apresentacao_banca2/` | [README](banca2/README.md), [roteiro](banca2/01_roteiro_narrativo.md), [conteúdo](banca2/02_conteudo_slides.md), [proveniência](banca2/03_proveniencia_figuras_e_numeros.md) |
| [Banca final](banca_final/) | pedido do grupo de 26/10/2026: diagrama causal (teoria da mudança) na seção de teoria e slides de equações no apêndice; 2 slides novos | **proposta**: conteúdo canônico do diagrama e da nova ordem; deck reorganizado derivado, em `output/apresentacao_banca_final/`; roteiro da banca final ainda não existe | [README](banca_final/README.md), [diagrama e ordem dos slides](banca_final/01_diagrama_teoria_mudanca.md) |

## 3. O que não entra em apresentação

Resultado de estimação só aparece em slide depois de passar pelos portões
registrados em [`docs/06_execucao/05_roadmap_execucao.md`](../06_execucao/05_roadmap_execucao.md).
Comparação ajustada, gradiente descritivo e associação não recebem linguagem
causal em slide, título ou fala.
