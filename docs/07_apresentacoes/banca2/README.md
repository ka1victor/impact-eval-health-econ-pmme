# Banca 2 — hipótese pela cadeia do modelo, dados, metodologia e resultados (28/10 e 04/11/2026)

> **Formato:** markdown com imagens, para ler no GitHub ou no Obsidian; o deck
> `.pptx` é derivado<br>
> **Estado:** **PRONTO** para 28/10. A H3 entrou com o P1h auditado
> (protocolo 52b, doc 57i, auditoria 31 aprovada com correções de rótulo):
> slide com a figura do P1h, os números lidos de `output/` e a força da
> evidência na cadeia-resumo. O deck proposto foi organizado a pedido do autor
> (26/10): prévios do grupo reutilizados, parte empírica cortada e
> sintetizada, apêndice por seção.<br>
> **Escopo:** os slides novos da banca 2 (hipótese econômica pela cadeia do
> modelo; base de dados e descritivas; metodologia econométrica e
> identificação; resultados, robustez e discussão) e as correções no deck do
> grupo<br>
> **Fora do escopo:** o ciclo 3 pós-T0, congelado; pedidos externos de dados;
> a banca final (`../banca_final/`)<br>
> **Atualização:** 26 de outubro de 2026

> [!IMPORTANT]
> **Versão final (decisão do autor de 26/10/2026):** só o **deck curto** é
> usado (`output/apresentacao_banca2/deck_banca2_curto.pptx` e `.pdf`), na
> estrutura obrigatória do [06](06_estrutura_obrigatoria_versao_final.md)
> (Hipótese, Dados, Análise descritiva, Metodologia, Identificação,
> Resultados, Robustez, Discussão), com no máximo 30 palavras visíveis por
> slide. Conteúdo canônico: [04](04_conteudo_deck_curto.md). O deck completo
> (doc 02) fica como registro e só é refeito com `--completo`.<br>
> **Numeração da apresentação a partir de 26/10/2026:** H1 preenchimento; H2
> bolsa × origem (antes H3); H3 oferta (antes H4). **A H1 é a candidata
> central**; H2 e H3 aparecem em cinza, como plano B, até a validação dos
> professores. Os slides de cada hipótese ficam juntos dentro de cada seção. Nas
> seções abaixo, escritas antes da troca, "H3" é a H2 de hoje e "H4", a H3.<br>
> **H1 principal:** a do adendo 48b (só vagas imediatas); o slide está marcado
> "aguardando 48b" até as saídas `HI_*` existirem. As medidas antigas (A3, N1,
> taxa por vaga), o "antes e depois do controle", a H1 por ciclo e o passo a
> passo da queda em 0,300 estão em Robustez. A queda em 0,300 é explicada pelas
> capitais logo abaixo do corte (auditoria 36, diagnóstico); a explicação pelo
> cadastro reserva do ciclo 2 saiu do deck. O doc 57m entra na versão auditada
> (auditoria 37).

## 1. O que esta entrega é

O conteúdo canônico da parte empírica da banca 2, no padrão da
[banca 1](../banca1/README.md): o roteiro, o conteúdo slide a slide e a
proveniência de cada número e de cada figura. O deck do grupo (template
Insper, 36 slides) continua sendo a base: os slides prévios do grupo
(capa até a hipótese, com sumários, teoria e ocultos) ficam como o grupo os
pôs, só com as correções; a parte empírica é feita dos slides novos, nos
marcadores "X" e entre as divisórias de sumário do grupo; o apêndice vem
depois do divisor "Apêndice". A ordem do deck inteiro e a classificação de
cada slide do grupo estão no [02](02_conteudo_slides.md). Divergência entre o
deck e estes arquivos é erro do deck (`CLAUDE.md`).

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
| [Conteúdo da apresentação](02_conteudo_slides.md) | **a fonte de verdade** do deck completo — slides novos com título, figura, tabela, números, cautela e notas; o quadro de correções do deck do grupo |
| [Conteúdo do deck curto](04_conteudo_deck_curto.md) | a fonte de verdade do deck curto: cada resultado com a hipótese e a ficha antes e a leitura depois |
| [**Estrutura obrigatória da versão final**](06_estrutura_obrigatoria_versao_final.md) | decisão do autor: Hipótese, Dados, Análise descritiva, Metodologia, Identificação, Resultados, Robustez, Discussão; toda versão futura do deck segue esta ordem |
| [Discussão da história empírica](05_discussao_historia_empirica.md) | perguntas do autor sobre a parte empírica, respostas, decisões de apresentação e a ordem da história nos slides |
| [Proveniência de figuras e números](03_proveniencia_figuras_e_numeros.md) | cada figura → arquivo, script e natureza; cada número → arquivo, seletor e formato, num bloco gerado pelo script |
| [Relatório de validação para os professores](../../../output/apresentacao_validacao/relatorio_validacao_rdd_bolsa.pdf) | relatório curto (derivado) com o desenho, os diagnósticos e os resultados de 19/10; não é o deck |

## 3. Decisões

| Data | Decisão | Quem |
|---|---|---|
| 26/10/2026 | "Metodologia" é a metodologia **econométrica** | autor |
| 26/10/2026 | o arco testa cada seta do modelo: H1 preenchimento, H2 escolha, H3 incentivo limitado, H4 capacidade líquida; H3 central como proposta revisável | autor delegou (plano, §9) |
| 26/10/2026 | a variável de efeito da H1 é o número de vagas preenchidas controlando as vagas oferecidas (N1), com a célula aberta (A3) e o que o IC descarta | grupo e autor |
| 26/10/2026 | a H3 entra só depois da auditoria do protocolo 52b; até lá, o slide ficou reservado | plano, §6.1 |
| 26/10/2026 | a H3 entra com o P1h auditado (auditoria 31): título "no modelo de escolha", θ_UF como "mesma UF, outra região de saúde", o km sem valor de prova (o teste bilateral do P1a não rejeita) | coordenador |
| 26/10/2026 | "Focar em fazer a parte empírica e ajustar o que precisa nos prévios; reutilizar tudo o que der": prévios do grupo na ordem e com a visibilidade do grupo, só com as correções; na parte empírica, título-afirmação, no máximo três marcadores, uma cautela, detalhe nas notas; o importante mas não central vai para o apêndice; discussão num slide; regra sharp na metodologia | autor |
| 26/10/2026 | saem do deck só os três marcadores "X" e os dois slides "EXEMPLO" (aplicativo de vinhos), modelo de outro trabalho | autor (critério); agente (aplicação) |
| 26/10/2026 | cronologia dos ciclos ("já rolou em 3 edições?"); fichas de especificação de cada estimador na metodologia ("esse tipo de coisa precisa estar toda nos slides"); antes e depois do controle, por corte; H2 só por ciclo; H3 responde na tela "qual a metodologia?" e "é causal?"; lugar reservado para "Por que o preenchimento cai em 0,300" (protocolo 61) | autor |
| 26/10/2026 | "Não mostre o empilhado; mostre os efeitos separados para cada corte": na H1, no corpo, 0,300 e 0,400 separados, com o TOST do protocolo 60 (doc 57j, auditoria 32); o empilhado só no apêndice, rotulado "só referência" | autor |
| 26/10/2026 | um arquivo só (`deck_banca2.pptx`); resultados abrem pela cadeia-síntese, e H1–H4 aprofundam cada linha; bloco "O que isso quer dizer" nos slides de hipótese, metodologia, resultados e robustez; conteúdo ocupando a área útil (corpo ≥ 16 pt, tabelas ≥ 14 pt, figuras no tamanho do slide) | autor |

| 26/10/2026 | especificação de cada estimador nos slides, numa ficha com os mesmos campos (outcome, amostra, equação em palavras, comum e por ciclo, erro-padrão, leitura, cuidado, sensibilidades); no curto, recortes dessas fichas, com o mesmo texto | autor |
| 26/10/2026 | slide "Por que o preenchimento cai em 0,300" logo depois de "antes e depois do controle", nos dois decks (protocolo 61, doc 57l); com a auditoria 33, sai o selo de preliminar e a explicação fica em duas ideias, fiel à frase validada (§8) | autor |
| 26/10/2026 | N1 sem controle ("efeito total: abrir vagas + preenchê-las") e com controle ("preenchimento dado o número de vagas") em dois gráficos separados, na mesma escala; a H3 traduz o 0,21 em chance (cerca de 24% maior), sem distinção de zero e sem ser efeito no preenchimento | autor |
| 26/10/2026 | bloco exploratório no completo, entre Base de Dados e Metodologia: IVS × faixa, distribuição do IVS com o E1, RDD crua e escolha × origem | autor |
| 26/10/2026 | deck curto em blocos antes → resultado → depois: capa; regra; H1 (ficha, antes e depois do controle com o TOST, queda em 0,300); H3, que absorve a H2 (ficha, resultado, incentivo limitado e a ponte P1g); H4 (ficha, resultado, substituição e "em análise"); conclusão. Saem a H2 como slide, "Um estimador por hipótese", "Quatro hipóteses" e os dados crus | autor |

Em aberto com o autor: a hipótese central (H3 ou H1), já revisável; quem
apresenta em 28/10 e quem em 04/11.

**Slides "EXEMPLO" 32 e 33 do deck do grupo:** saíram do deck proposto pelo
critério do autor (saem se forem claramente modelo de outro trabalho; são de
um aplicativo de vinhos, marcados "EXEMPLO"). Para trazê-los de volta, basta
mudar o destino deles na tabela de classificação do 02 e pôr os marcadores
`<!-- grupo: 32 -->` e `<!-- grupo: 33 -->` onde devem entrar.

## 4. Figuras, tabelas e deck

Tudo sai do pipeline, lendo só de `output/`:

```bash
python3 scripts/apresentacao/gerar_figuras_banca2.py                 # figuras, tabelas, números e bloco do 03
PMME_DECK_GRUPO="<deck do grupo>" python3 scripts/apresentacao/gerar_deck_banca2.py   # deck completo
PMME_DECK_GRUPO="<deck do grupo>" python3 scripts/apresentacao/gerar_deck_banca2.py --curto   # deck curto e PDF
PMME_DECK_GRUPO="<deck do grupo>" python3 -m unittest tests.test_conteudo_banca2 tests.test_deck_curto_banca2
```

Saídas em `output/apresentacao_banca2/`: as figuras (`h1_preenchimento.png`,
`h2_escolha.png`, `h4_horas_medico.png`, `cadeia_resumo_doc57.png`,
`regra_bolsa_ivs_oficial.png`; a figura da H3 é a do P1h,
`output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png`, usada sem redesenho e
conferida pelo hash), as tabelas (`tabela_descritiva_ciclos` e
`tabela_fontes`, em CSV e PNG), o registro de números
(`numeros_banca2.json`), o manifesto das figuras, **o deck, num arquivo
só** (`deck_banca2.pptx`: slides do grupo, parte empírica e apêndice), o
manifesto do deck e as imagens de conferência em `qa_render/`, com a grade de
miniaturas da parte empírica (`grade_empirica.png`), e o deck curto
(`deck_banca2_curto.pptx` e `.pdf`, com o manifesto e a grade
`qa_render/grade_curto.png`), com as figuras próprias dele
(`curto_dispersao_a3.png`, `curto_reta_0300.png`, `curto_h1_por_ciclo.png`,
`curto_h3_horas.png`, `curto_h3_nota_corte.png` e `curto_tost.png`) e as da
subida dentro das faixas (`output/rdd_bolsa/GF_figuras/`, doc 57m, em
auditoria). O slide da queda em 0,300 usa o diagnóstico do
protocolo 61 auditado (auditoria 33). Os geradores não estão no `run_all.py`; a
inclusão fica para o coordenador do pipeline.

## 5. Estado

| Bloco | Conteúdo | Figuras | Proveniência |
|---|:---:|:---:|:---:|
| Hipótese econômica | ✅ | ✅ (formas nativas) | ✅ |
| Base de dados e descritivas | ✅ | ✅ (tabelas nativas) | ✅ |
| Metodologia econométrica | ✅ | ✅ (tabelas nativas) | ✅ |
| Resultados: regra, H1, H2, H3, H4, cadeia | ✅ | ✅ | ✅ |
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
| H1 | [`06_execucao/49`](../../06_execucao/49_resultados_contagem_vagas_preenchidas.md), §3 e §15; [`49b`](../../06_execucao/49b_diagnostico_contagem_porte.md); TOST por corte em [`57j`](../../06_execucao/57j_resultados_equivalencia_H1.md) e [`auditorias/32`](../../auditorias/32_auditoria_equivalencia_H1.md) |
| H2 | [`06_execucao/57a`](../../06_execucao/57a_resultados_P1_escolha.md); E9 no [doc 44](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md), §5.2 |
| H3 | [`06_execucao/57i`](../../06_execucao/57i_resultados_P1h_magnitudes.md) (resultado); [`52b`](../../06_execucao/52b_protocolo_P1h_magnitudes.md) (protocolo); [`auditorias/31`](../../auditorias/31_auditoria_P1h_magnitudes.md) |
| H4 | [`06_execucao/57d`](../../06_execucao/57d_resultados_P4_trajetoria.md), [`57f`](../../06_execucao/57f_resultados_P6_mecanismo.md), [`57h`](../../06_execucao/57h_resultados_P3P4_sensibilidade.md) |
| síntese e cadeia | [`06_execucao/57`](../../06_execucao/57_sintese_perguntas_reformuladas.md) |
| co-políticas | [`auditorias/18`](../../auditorias/18_politicas_nos_mesmos_cortes_ivs.md) |
| literatura de magnitude | [`06_execucao/44`](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md), §6 |
