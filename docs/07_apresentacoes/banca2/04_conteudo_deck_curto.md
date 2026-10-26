---
documento: Conteúdo do deck curto — banca 2 (parte empírica)
papel: fonte de verdade do deck curto, o único usado na versão final; o deck é derivado
escopo: estrutura obrigatória da versão final (doc 06) — Hipótese, Dados, Análise descritiva, Metodologia, Identificação, Resultados, Robustez e Discussão; sem os slides do grupo, sem divisórias, sem o diagrama da teoria e sem apêndice
slides: 14
estado: em produção; H1 central; H1 principal com as saídas do adendo 48b (HI_*, em auditoria); queda em 0,300 explicada pelas capitais (auditoria 36, diagnóstico); doc 57m auditado (auditoria 37); reduzido a 14 slides em 26/10/2026
atualizacao: 26 de outubro de 2026
---

> [!IMPORTANT]
> **Pedidos do autor (26/10/2026), nesta versão.**
> - **No máximo 14 slides** ("esses últimos decks tão muito grandes. pode
>   deixar mais curtos mesmo, só com os principais slides, idealmente <15
>   slides"). O rascunho de 26 slides foi cortado: saíram a capa, a tabela
>   separada das variáveis secundárias (fundida na de Dados), os dois slides
>   da subida dentro das faixas (doc 57m), o slide "H2 e H3: como estimamos"
>   (virou duas linhas cinzentas na especificação da H1), o slide do pacote
>   do corte (fundido na Identificação), os resultados e as robustezes de H2 e
>   H3 em slides próprios (viraram um slide de planos B na Discussão), a medida
>   antiga contra só vagas imediatas, o slide da reta em 0,300 e o TOST em
>   slide próprio (viraram uma linha nos Resultados e uma frase na Discussão).
>   O conteúdo cortado que importa foi para as notas do apresentador.
> - **Estrutura obrigatória** ([06](06_estrutura_obrigatoria_versao_final.md)):
>   Hipótese, Dados, Análise descritiva, Metodologia, Identificação,
>   Resultados, Robustez, Discussão. Só este deck é gerado; o completo
>   ([02](02_conteudo_slides.md)) fica como registro.
> - **Numeração da apresentação a partir de 26/10/2026:** H1 preenchimento;
>   H2 bolsa × origem (antes H3); H3 oferta (antes H4). A H2 antiga (escolha
>   por ciclo) saiu como hipótese própria e não tem slide. Os nomes dos
>   documentos de análise (P1h, P4, protocolos) e dos códigos de número
>   (`H3_*` é o P1h) não mudam.
> - **H1 é a candidata central** (correção do autor de 26/10/2026), em
>   destaque; H2 e H3 aparecem em cinza, como plano B, até a validação dos
>   professores: na hipótese, nas duas linhas da metodologia e no slide de
>   planos B da Discussão.
> - **Auditoria 36:** sai do deck a explicação de que, no ciclo 2, a vaga de
>   reserva não podia ser preenchida na 1ª chamada (está errada: o quadro do
>   ciclo 2 foi refeito depois do resultado). A queda em 0,300 é explicada
>   pela reta levada até o corte, puxada por poucos municípios (capitais e
>   Nordeste logo abaixo); controlando a capital, ou só com vagas imediatas, a
>   queda encolhe. Diagnóstico pós-resultado; o adendo 48c fará a versão
>   padronizada.
> - **Tipo de vaga** (doc 05, §2.12): o Ministério decide se a vaga é imediata
>   ou de reserva, e isso pode responder ao corte; a premissa entra na
>   Identificação como "não testado".
> - **H3 em dois níveis** (doc 05, §2.13): o +6,6 h/sem é do próprio médico;
>   no nível do município não dá para afirmar aumento de oferta, e os outros
>   especialistas não saem.
> - **H2:** os números atuais valem até a reestimação do ciclo 2 (adendo 52c);
>   a nota fica só nas notas do apresentador.
> - **H1 principal = adendo 48b** (só vagas imediatas: HI-1 e HI-2 por corte,
>   com Holm), com as saídas `HI_*` e o doc 57n, ainda em auditoria: a
>   cautela do slide de resultados e as linhas de fontes dizem "em auditoria".
> - **"Texto demais":** no máximo **30 palavras visíveis por slide**, fora o
>   título, a figura e a linha de fontes. Especificação em até 4 linhas
>   curtas, com a equação em palavras grande no centro. O resto vai para as
>   notas do apresentador.
>
> **Formato.** Cada `#` é uma seção da estrutura obrigatória; cada `##` é um
> slide: título-afirmação (no máximo 58 caracteres), a figura (ou a tabela)
> grande e poucas linhas curtas. As linhas são os marcadores `- `; a cautela é
> a citação em negrito. Layouts: `curto_figura`, `curto_tabela`, `curto_texto`,
> `curto_capa` (frase grande, com cautela opcional), `curto_hipotese` (a
> central em destaque, os planos B em cinza) e `curto_espec` (a 1ª linha, sem
> rótulo, é a equação em palavras). Rótulo que começa por H2 ou H3, ou que diz
> "plano B", sai em cinza; numa tabela, a linha toda em itálico (`*…*`) sai em
> cinza (variável secundária). O gerador
> (`scripts/apresentacao/gerar_deck_banca2.py`, modo padrão) para se as seções
> fugirem da estrutura, se houver mais de 14 slides, se um slide passar de 30
> palavras ou se uma linha não couber.
>
> **Regra dos números.** Todo número de um slide, notas incluídas, é o valor de
> um código listado na linha `**Números:**` ou um parâmetro do protocolo
> ([03, §3](03_proveniencia_figuras_e_numeros.md#3-parâmetros-que-podem-aparecer-sem-código)).
> As linhas do doc 57m (protocolo 62) vêm da versão auditada (auditoria 37).
> `tests/test_deck_curto_banca2.py` confere a estrutura, a
> contagem de palavras, os números, as cautelas e o pacote gerado.

<!-- deck:inicio -->

# Hipótese

## Hipóteses: a H1 é a candidata central

`Hipótese`

<!-- layout: curto_hipotese -->

- **H1 · central** bolsa maior, mais vagas preenchidas
- **H2 · plano B** a bolsa pesa pouco perto da origem
- **H3 · plano B** a chegada soma oferta ou remaneja?

> **H2 é pós-resultado.**

**Fontes:** plano da banca 2, §3; doc 06 da banca 2; doc 57i (P1h, protocolo 52b, auditoria 31).

**Números:** nenhum

> **Notas do apresentador.** O efeito candidato é o incentivo marginal de
> R$ 5 mil anunciado nos cortes do IVS, como pacote do corte: em 0,300 e
> 0,400 mudam também outras regras federais. Não é a participação no PMM-E
> nem o efeito do Agora Tem Especialistas. Numeração desta apresentação a
> partir de 26/10/2026: H1 preenchimento; H2 bolsa × origem (antes H3);
> H3 oferta (antes H4). A H1 é a hipótese central (decisão do autor de
> 26/10/2026): onde a bolsa é maior, mais vagas são preenchidas. H2 e H3 ficam
> em cinza, como plano B, até a validação dos professores. A H2 é o "incentivo
> limitado" do modelo da banca 1: toda a bolsa pesa menos que trabalhar na UF
> de origem do médico; foi formulada depois de ver os coeficientes do modelo
> de escolha, e por isso é pós-resultado. A H3 pergunta se a chegada do
> médico soma oferta ou só remaneja.

---

# Dados

## Dados: as variáveis e de onde vêm

`Dados`

<!-- layout: curto_tabela -->

| Variável: principal · *secundária* | Fonte |
|---|---|
| Bolsa | editais SGTES/MS |
| IVS 2010 | Ipea |
| Preenchimento, tipo de vaga | quadros SGTES/MS |
| 1ª opção, origem | editais + CNES |
| Horas | CNES |
| *Capital, porte* | *IBGE* |
| *Regras no corte* | *portarias* |

**Fontes:** `output/apresentacao_banca2/tabela_fontes.csv`; auditorias 16, 18, 35 e 36; portão G1.

**Números:** nenhum

> **Notas do apresentador.** Principais. Bolsa: a faixa anunciada nos
> quadros dos editais do PMM-E (SGTES/MS), por município, ciclos 1–3. IVS
> 2010 oficial: Plataforma IVS do Ipea, Censo 2010, por município; é a
> variável de corte. Preenchimento e tipo de vaga: quadros de vagas e
> resultados da 1ª e da 2ª chamada, por célula (estabelecimento × curso),
> 2025–2026; o tipo (vaga imediata ou cadastro reserva) vem do quadro, e no
> ciclo 2 do quadro de 13/02/2026, anterior à alocação (auditoria 36). 1ª
> opção e origem: listas de classificação dos editais, ligadas ao cadastro de
> profissionais do CNES pelo portão G1; a origem é onde o médico tinha
> vínculo no CNES antes das inscrições, não residência. Horas: CNES mensal do
> DATASUS, por médico e mês, de 2022-01 a 2026-08. Secundárias, em cinza:
> capital pelo código IBGE (auditoria 36); porte pela população do Censo
> 2022; regras no mesmo corte nas portarias do MS (auditoria 18) e incentivos
> ligados à vulnerabilidade (auditoria 35). Servem para o diagnóstico da
> queda e para a leitura do pacote do corte; não entram na especificação
> principal. Dados pessoais só em memória ou em cache fora do Git.

---

# Análise descritiva

## Os três ciclos em números

`Análise descritiva · Ciclos`

<!-- layout: curto_tabela -->

| | Ciclo 1 | Ciclo 2 | Ciclo 3 |
|---|---|---|---|
| Municípios | 368 | 454 | 748 |
| Células | 1.295 | 1.547 | 2.293 |
| Preenchidas (1ª chamada) | 30,3% | 47,1% | 21,7% |

- **Ciclo** = edital de vagas: 2025, início e meio de 2026

**Fontes:** `output/apresentacao_banca2/tabela_descritiva_ciclos.csv`; `cronologia_ciclos.csv`.

**Números:** `D_C1_MUN`, `D_C2_MUN`, `D_C3_MUN`, `D_C1_CEL`, `D_C2_CEL`, `D_C3_CEL`, `D_C1_PRE1_PCT`, `D_C2_PRE1_PCT`, `D_C3_PRE1_PCT`, `D_C1_P1`, `D_C2_P1`, `D_C3_P1`

> **Notas do apresentador.** Cada ciclo é um chamamento do PMM-E com quadro
> de vagas próprio: o ciclo 1 com quadro de 24/07/2025, o ciclo 2 com quadro
> de 03/02/2026 e o ciclo 3 com quadro de 16/07/2026 (ciclo 3 congelado).
> Municípios: os que tinham vaga no quadro. Célula = estabelecimento × curso
> no quadro da 1ª chamada. Nesta tabela, no ciclo 1, "preenchida" é alguma
> confirmação ou homologação; nos ciclos 2 e 3, alocado. As estimativas da H1
> usam ao menos um alocado nos três ciclos (no ciclo 1, o confirmado), como
> conferiu a auditoria 36. Amostra da escolha (H2, plano B): 915, 2.032 e
> 2.474 candidatos com 1ª opção numa célula do quadro, ligados ao CNES e com
> município de origem.

---

## A bolsa é função exata do IVS: a regra é sharp

`Análise descritiva · IVS × faixa`

<!-- layout: curto_figura -->

![Bolsa anunciada contra o IVS 2010 oficial, ciclo 1, um ponto por município](../../../output/apresentacao_banca2/regra_bolsa_ivs_oficial.png)

- **Ciclos 1 e 2:** a regra reproduz a faixa de 368 de 368 e de 454 de 454 municípios.

**Fontes:** `output/rdd_bolsa/portao_r1_ivs_oficial.json`; `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`; auditoria 16.

**Números:** `R_C1_REPR`, `R_C1_MUN`, `R_C2_REPR`, `R_C2_MUN`, `R_ESCORE_IGUAIS`, `R_C3_REPR`, `R_C3_MUN`

> **Notas do apresentador.** Até 0,300, R$ 10 mil; até 0,400, R$ 15 mil;
> acima, R$ 20 mil. O escore da relação nominal do MS é o IVS 2010 oficial em
> 404/404 municípios. No ciclo 3, congelado, 747 de 748: o que falta foi
> criado depois de 2010. Em 0,300 e 0,400 mudam também outras regras
> federais: pacote do corte.

---

## H1 · Dados crus, só vagas imediatas

`Análise descritiva · H1 · Dados crus`

<!-- layout: curto_figura -->

![Só células com vaga imediata: médias por faixa de 0,010 de IVS e reta local de cada lado, nos cortes 0,300 e 0,400](../../../output/rdd_bolsa/HI_figuras/HI_scatter_imediatas.png)

- **Em 0,300**, a reta de baixo sobe forte até o corte e chega alta.
- Dados crus; com curso e ciclo, a HI-1 fica bem menor.

**Fontes:** `output/rdd_bolsa/HI_figuras/HI_scatter_imediatas.png`, `HI_resumo.json` e `HI_estimativas.csv` (adendo 48b; doc 57n; em auditoria); doc 57m (auditoria 37); figura usada sem redesenho.

**Números:** `HI1_300_TAU`, `HI1_300_INF`, `HI1_300_SUP`, `HI1_400_TAU`, `HI1_300_MEDIA`, `GF_10_ORIG`, `GF_10_ORIG_INF`, `GF_10_ORIG_SUP`, `GF_10_UF`, `GF_10_NE_PRE`

> **Notas do apresentador.** Só células com pelo menos uma vaga imediata
> (no ciclo 2, pelo quadro de 13/02/2026, anterior à alocação). Cada ponto é
> a fração de células preenchidas numa faixa de 0,010 de IVS; cada linha, a
> reta local de um lado. Abaixo de 0,300, 56,1% dessas células são
> preenchidas. A distância crua entre as retas não é a estimativa: a HI-1
> compara células do mesmo curso e ciclo, com uma reta por ciclo, e dá −3,7
> p.p. [−21,3; +13,9] em 0,300 e −2,3 em 0,400. Saídas do adendo 48b, em
> auditoria. Por que a reta de baixo sobe (protocolo 62, doc 57m,
> auditoria 37; descritivo e pós-resultado): na faixa de R$ 10 mil, a fração de células
> preenchidas sobe +11,9 p.p. a cada 0,100 de IVS [+6,0; +17,7]; comparando
> só células da mesma UF, sobram +1,3 p.p. O Nordeste é a região que mais
> preenche nessa faixa (43% das células) e a de IVS mais alto. Diz com o que
> a subida anda junto, não por quê.

---

# Metodologia

## H1 · O salto no corte, só com vagas imediatas

`Metodologia · H1 · adendo 48b`

<!-- layout: curto_espec -->

- alocados = ciclo + salto × lado de bolsa maior + retas por lado e ciclo + ciclo × vagas imediatas
- **h = 0,050** triangular; erro-padrão por município
- **H2** logit da 1ª opção
- **H3** estudo de evento

**Fontes:** adendo 48b ao protocolo 48 (`docs/06_execucao/48b_adendo_H1_vagas_imediatas.md`); protocolos 52, 52b, 54, 59 e 60.

**Números:** `M1_N`

> **Notas do apresentador.** Especificação principal da H1 desde 26/10/2026
> (adendo 48b, pós-resultado), RDD sharp local linear em cada corte
> separado. A equação da tela é a HI-2: médicos alocados na 1ª chamada em
> vagas imediatas, por município, com intercepto por ciclo, o salto do lado
> de bolsa maior, uma reta de cada lado por ciclo e o controle das vagas
> imediatas com coeficiente por ciclo. A HI-1 é a célula com vaga imediata
> preenchida na 1ª chamada, com efeitos fixos de curso × ciclo. Amostra: só
> células com pelo menos uma vaga imediata, ciclos 1–3; as demais ficam fora
> e são contadas. Kernel triangular, h = 0,050, erro-padrão agrupado por
> município; Holm entre as quatro linhas primárias. Comparamos vagas do mesmo
> tipo; a reserva se preenche por remanejamento e pela priorização da SGTES,
> outro mecanismo (doc 57n). No ciclo 2, o tipo de vaga é o do quadro de
> 13/02/2026 (auditoria 36). Em cinza, os planos B. H2: logit condicional
> (McFadden); cada um dos 5.421 candidatos escolhe a vaga de maior utilidade
> entre as do seu curso e ciclo: utilidade = bolsa + IVS + distância +
> origem; a curva do IVS é um spline com nós nos cortes, e só o salto da bolsa
> nos cortes identifica o peso dela; erro-padrão agrupado por conjunto de
> escolha; o teste é o peso da UF de origem menos o de toda a bolsa,
> unilateral e pós-resultado. H3: estudo de evento escalonado (Callaway e
> Sant'Anna) no médico e no município × mês; erro-padrão por bootstrap
> multiplicador agrupado; sensibilidades: Rambachan–Roth e a comparação na
> nota de corte. Cuidado: pacote do corte.

---

# Identificação

## H1 · RDD: as premissas e o nosso caso

`Identificação · RDD`

<!-- layout: curto_tabela -->

| Premissa | Aderência |
|---|---|
| Regra sharp | 368/368, 454/454 |
| Sem manipulação, balanço | passam, salvo capitais |
| Só a bolsa | não: pacote |
| Outro incentivo individual em 0,300 | nenhum |
| Tipo de vaga (MS) exógeno | não testado |

**Fontes:** auditorias 16, 18, 35 e 36; docs 37, 41, 49 e 05 (§2.12) da banca 2; `output/rdd_bolsa/E1_densidade_estimativas.csv`; `output/auditoria_H1/a36_estimativas.csv`.

**Números:** `R_C1_REPR`, `R_C1_MUN`, `R_C2_REPR`, `R_C2_MUN`, `E1_300_HOLM`, `E1_400_HOLM`, `A36_CAPMUN_TAU`, `A36_CAPMUN_INF`, `A36_CAPMUN_SUP`

> **Notas do apresentador.** Regra sharp: o IVS 2010 oficial reproduz a
> faixa de todos os municípios dos ciclos 1 e 2. Sem manipulação: o IVS foi
> medido em 2010, antes do programa, e o teste de densidade não acusa acúmulo
> no ciclo 1 (p de Holm 0,707 em 0,300 e 0,658 em 0,400). Balanço: covariáveis
> pré e placebos de outcome e de corte passam; ressalvas: em 0,400, seleção
> suspeita no ciclo 1; em 0,300, a parte dos municípios que são capitais cai
> −17,8 p.p. [−34,1; −1,5] no corte (auditoria 36, diagnóstico). Pacote do
> corte: a única regra federal que muda em 0,300 e não em 0,400 é o
> acréscimo no teto de emendas e nas parcelas de custeio da APS e da MAC do
> município (auditoria 18); nenhum incentivo individual ao especialista além
> da bolsa muda em 0,300; em 0,400 mudam incentivos de médicos da APS (AgSUS
> e PMMB) (auditoria 35). Por isso o contraste é o pacote do corte, não a
> bolsa sozinha. Tipo de vaga: a SGTES/MS decide se a vaga é imediata ou de
> cadastro reserva, por critério que não está nos dados nem nos editais, e a
> decisão pode responder ao corte; comparar só vagas imediatas pode então
> comparar grupos selecionados de forma diferente. O teste da seleção (limites
> de Lee, "ter vaga imediata" como outcome, balanço dentro da amostra
> imediata) está pendente e precisa de adendo congelado antes de rodar
> (doc 05, §2.12). Na H3 (plano B), o teste conjunto do pré falha nas horas no
> município do posto; na H2, a independência de alternativas irrelevantes é
> violada em parte, e o peso da bolsa muda pouco.

---

# Resultados

## H1 · Só vagas imediatas: nada passa no Holm

`Resultados · H1 · adendo 48b`

<!-- layout: curto_figura -->

<!-- linhas: 3 -->

![H1 principal: HI-1 (célula com vaga imediata preenchida) e HI-2 (alocados em vagas imediatas por município), por corte, com IC 95% e p de Holm](../../../output/rdd_bolsa/HI_figuras/HI_principal.png)

- Nada passa no Holm; HI-1: IC contém zero nos dois cortes.
- **TOST:** HI-2 em 0,300 descarta aumento ≥ 25% da média, não descarta queda.

> **Em auditoria (adendo 48b); pacote do corte.**

**Fontes:** `output/rdd_bolsa/HI_estimativas.csv`, `HI_resumo.json` e `HI_figuras/HI_principal.png` (adendo 48b; doc 57n; em auditoria); figura usada sem redesenho.

**Números:** `HI1_300_TAU`, `HI1_300_INF`, `HI1_300_SUP`, `HI1_300_HOLM`, `HI1_400_TAU`, `HI1_400_INF`, `HI1_400_SUP`, `HI1_400_HOLM`, `HI2_300_TAU`, `HI2_300_INF`, `HI2_300_SUP`, `HI2_300_HOLM`, `HI2_400_TAU`, `HI2_400_INF`, `HI2_400_SUP`, `HI2_400_HOLM`, `HI2_300_MEDIA`, `HI_EQ1_300_I90I`, `HI_EQ1_300_I90S`, `HI_EQ1_400_I90I`, `HI_EQ1_400_I90S`, `HI_EQ2_300_I90I`, `HI_EQ2_300_I90S`, `HI_EQ2_300_MARG`, `HI_EQ2_400_MARG`

> **Notas do apresentador.** Especificação principal da H1 (adendo 48b, em
> auditoria; pós-resultado). HI-1, a chance de uma célula com vaga imediata
> ser preenchida na 1ª chamada: −3,7 p.p. [−21,3; +13,9] em 0,300 e −2,3 p.p.
> [−24,0; +19,4] em 0,400, p de Holm 1,000 nos dois. HI-2, médicos alocados
> nessas vagas por município, comparando municípios com as mesmas vagas
> imediatas: −1,13 [−2,15; −0,10] em 0,300, p de Holm 0,126 (média abaixo
> 2,77); −0,16 [−0,99; +0,68] em 0,400, p de Holm 1,000. O IC convencional
> exclui zero só em HI-2 em 0,300, mas o sinal não sobrevive à correção para
> quatro testes. IC que contém zero não é efeito zero. TOST (HI-s7), com IC de
> 90% e as margens do protocolo 60: HI-1 [−18,4; +11,1] em 0,300 e [−20,5;
> +15,9] em 0,400, contra ±10 p.p.: inconclusivo. HI-2 em 0,300: [−1,99;
> −0,26] contra ±0,69 médico por município (25% da média abaixo): não houve
> aumento igual ou maior que a margem, mas uma queda desse tamanho não fica
> descartada. HI-2 em 0,400, contra ±0,50: inconclusivo. No IC convencional,
> sob a aproximação local linear e para o pacote do corte. Não dá para dizer
> que nada mudou. Tudo se refere ao pacote do corte, não à bolsa isolada.

---

# Robustez

## H1 · Antes e depois do controle das vagas

`Robustez · H1 · controle`

<!-- layout: curto_figura -->

![Antes e depois do controle das vagas oferecidas, por corte: sem controle e com controle em dois gráficos na mesma escala; ao lado, o salto nas vagas oferecidas](../../../output/apresentacao_banca2/h1_controle.png)

- **0,400:** a queda passa pelas vagas: cidades grandes logo abaixo; com o controle, some.
- **0,300:** a oferta não muda; cai o preenchimento por vaga.

**Fontes:** `output/rdd_bolsa/N_estimativas.csv` (decomposição e S-c; doc 49, §3 a §5); `ND_estimativas.csv` (doc 49b, §3); `HI_estimativas.csv` (adendo 48b; doc 57n; em auditoria).

**Números:** `VIC_400_TAU`, `N1_400_DTOT`, `N1_400_VIA`, `N1_400_DSA`, `N1_300_DTOT`, `N1_300_VIA`, `N1_300_DSA`, `VIC_300_TAU`, `A3_300_TAU`, `A3_300_INF`, `A3_300_SUP`, `HI1_300_TAU`, `N1_300_INF`, `N1_300_SUP`, `HI2_300_TAU`

> **Notas do apresentador.** Especificação secundária da H1: a medida
> antiga, alocados por município (N1), que mistura vaga imediata e cadastro
> reserva. Sem controle, o efeito total de abrir vagas e preenchê-las; com
> controle, o preenchimento dado o número de vagas. A decomposição é exata:
> sem controle = via vagas + com controle. Em 0,400: −1,36 = −1,22 + −0,14; do
> lado de bolsa maior há menos vagas oferecidas (−3,59), sobretudo por alguns
> municípios grandes logo abaixo do corte. Em 0,300: −1,56 = −0,11 + −1,45
> [−2,67; −0,22]; a oferta não muda (+0,39). Só com vagas imediatas, os saltos
> em 0,300 encolhem: N1 com controle de −1,45 para −1,13 (HI-2); a célula
> aberta preenchida (A3) de −8,4 p.p. [−18,5; +1,7] para −3,7 p.p. (HI-1).
> Linhas por corte, sem correção múltipla.

---

## H1 · Por ciclo: a queda em 0,300 vem do ciclo 2

`Robustez · H1 · por ciclo`

<!-- layout: curto_figura -->

![H1 por ciclo e por corte: célula aberta preenchida (A3) e taxa por vaga oferecida, ciclos 1, 2 e 3 e juntos, com IC 95%](../../../output/apresentacao_banca2/curto_h1_por_ciclo.png)

- A queda em 0,300 vem sobretudo do ciclo 2; por ciclo, os intervalos são largos.

> **Tipo de vaga do ciclo 2: quadro refeito depois do resultado (auditoria 36).**

**Fontes:** `output/rdd_bolsa/NA_estimativas.csv` (A3 por ciclo); `ND_estimativas.csv` (taxa por vaga, adendo AD2; doc 49b); auditoria 36.

**Números:** `PC_TX_2_300_TAU`, `PC_TX_2_300_INF`, `PC_TX_2_300_SUP`, `PC_TX_J_300_TAU`, `ND_TX300_C2_PCT`, `PC_A3_2_300_TAU`

> **Notas do apresentador.** Todas as combinações de ciclo, corte e medida
> estão gravadas; nada foi estimado para este slide. Na taxa por vaga
> oferecida, o ciclo 2 dá −27,8 p.p. [−49,0; −6,7] em 0,300, contra −16,0
> com os ciclos juntos, e responde por 51% do salto conjunto. Na A3, o ciclo 2
> dá −10,2 p.p., com IC que contém zero. "Preenchida" é ao menos um alocado
> nos três ciclos (no ciclo 1, o confirmado), conferido pela auditoria 36. A
> A3 usa o tipo de vaga do ciclo 2 do quadro retificado de 19/03/2026, refeito
> depois do resultado preliminar; com o tipo de vaga de antes da alocação, a
> queda aumenta. A H1 principal (adendo 48b) usa o quadro de 13/02/2026.

---

## H1 · Controlando a capital, a queda encolhe

`Robustez · H1 · capitais`

<!-- layout: curto_figura -->

<!-- linhas: 3 -->

![Queda em 0,300 nas três medidas: como estimada, com dummy de capital e só com células de vaga imediata, com IC 95% (auditoria 36)](../../../output/apresentacao_banca2/curto_queda_capital.png)

- Controlando a capital, a queda encolhe e o IC contém zero; só com vagas imediatas, encolhe.
- 13 capitais abaixo de 0,300 e 6 acima.

> **Auditoria 36, diagnóstico pós-resultado.**

**Fontes:** `output/auditoria_H1/a36_estimativas.csv` e `a36_resumo.json` (auditoria 36); o adendo 48c fará a versão padronizada.

**Números:** `HI2_300_TAU`, `A36_CAP_ABX`, `A36_CAP_ACI`, `A36_A3_PIPE_TAU`, `A36_A3_CAP_TAU`, `A36_A3_CAP_INF`, `A36_A3_CAP_SUP`, `A36_A3_VI_TAU`, `A36_TX_PIPE_TAU`, `A36_TX_CAP_TAU`, `A36_TX_CAP_INF`, `A36_TX_CAP_SUP`, `A36_TX_VI_TAU`, `A36_N1_PIPE_TAU`, `A36_N1_CAP_TAU`, `A36_N1_CAP_INF`, `A36_N1_CAP_SUP`, `A36_CAPMUN_TAU`, `A36_CAPMUN_INF`, `A36_CAPMUN_SUP`

> **Notas do apresentador.** Diagnóstico da auditoria 36, descritivo e
> pós-resultado, sem estatuto causal. Na janela de 0,050 há 13 capitais abaixo
> de 0,300 e 6 acima; a menos de 0,010 do corte, São Paulo, Goiânia, Natal e
> Brasília ficam abaixo e nenhuma capital acima. No corte, a parte dos
> municípios que são capitais cai −17,8 p.p. [−34,1; −1,5]. Com uma dummy de
> capital: A3 de −8,4 para −2,6 p.p. [−11,8; +6,6]; taxa por vaga de −16,0
> para −10,9 p.p. [−22,6; +0,8]; N1 de −1,45 para −0,92 [−1,98; +0,14]. Só
> com células de vaga imediata (tipo de vaga de antes da alocação): A3 −3,7
> p.p. e taxa −13,2 p.p., com IC que contém zero; nos alocados por município
> (HI-2, adendo 48b), −1,13, com IC que exclui zero, que não passa no Holm. O adendo 48c vai estimar
> capitais e UF de forma padronizada; quando sair, a fonte deste slide muda.

---

# Discussão

## H1 · Por que o sinal sai negativo

`Discussão · H1 · sinal`

<!-- layout: curto_texto -->

- **Reta** puxada por capitais e Nordeste logo abaixo de 0,300
- **Vagas** diferentes do lado de cima
- **Porte** municípios grandes logo abaixo de 0,400
- **Incentivo** nenhum individual muda em 0,300

**Fontes:** síntese da Robustez; doc 49b; doc 57l (auditoria 33); doc 57m (auditoria 37); auditorias 18, 35 e 36.

**Números:** `DQ_FUN_PRE_ABX`, `DQ_FUN_PRE_ACI`, `DQ_PPOSTO_Q1`, `DQ_PCOMP_Q1`

> **Notas do apresentador.** Uma frase por explicação; todas são
> diagnósticos pós-resultado e medem o pacote do corte. Reta: nas médias
> simples da janela, 33,3% das células são preenchidas abaixo de 0,300 e
> 33,5% acima; a RDD compara as duas retas no ponto do corte, e a de baixo
> carrega uma subida que só existe nos últimos municípios antes de 0,300, com
> capitais e Nordeste logo abaixo do corte. Vagas: do lado de cima há mais
> vagas de cadastro reserva e de cursos que preenchem pouco em qualquer lugar;
> só com vagas imediatas, a queda encolhe. Porte: em 0,400, municípios grandes
> logo abaixo abrem e preenchem muitas vagas; com o controle das vagas, o
> salto quase some. Incentivo: nos atos lidos, nenhum incentivo individual
> além da bolsa muda em 0,300 (auditoria 35); muda o teto de emendas do
> município (auditoria 18). Acaso: com os 3 cortes falsos do protocolo, o p
> por posto é 0,250, o menor possível; numa grade maior, fora do protocolo,
> 0,031; não fica descartado nem confirmado. Nada disso mostra que a bolsa
> reduz o preenchimento.

---

## H2 e H3 · plano B: origem pesa; oferta incerta

`Discussão · H2 e H3 · plano B`

<!-- layout: curto_texto -->

- **H2** origem supera toda a bolsa: 2,34 · 1,31 · 2,37 (ciclos 1–3)
- **H3** +6,6 h/sem do próprio médico; metade já estava lá
- **H3 · município** aumento não afirmável; outros especialistas não saem

**Fontes:** `output/rdd_bolsa/P1h_magnitudes.csv` (doc 57i; auditoria 31); `S57_resumo.json` (doc 57d); `CA_estimativas.csv` (doc 57h); `OL_resumo.json` (doc 57k; em auditoria).

**Números:** `H3_S_M5C1`, `H3_S_M5C2`, `H3_S_M5C3`, `H3_DUF`, `H3_DUF_INF`, `H3_DUF_SUP`, `H3_10B`, `H3_THETA`, `P4_HT_ATT`, `P4_HT_INF`, `P4_HT_SUP`, `P4_HM_ATT`, `P4_HF_ATT`, `P4_ORIGEM`, `P4_ORIGEM_INF`, `P4_ORIGEM_SUP`, `CA_HT_EST`, `CA_HT_INF`, `CA_HT_SUP`

> **Notas do apresentador.** Planos B, em cinza. H2 (P1h, pós-resultado):
> diferença, em log-chance, entre o peso de a vaga ficar na mesma UF de
> origem do médico e o peso de toda a bolsa, no modelo de escolha da 1ª
> opção, estimado em cada ciclo: 2,34 no ciclo 1, 1,31 no ciclo 2 e 2,37 no
> ciclo 3. Com os ciclos juntos, toda a bolsa pesa 0,42 e a mesma UF 2,40;
> diferença 1,98 [1,56; 2,40]. Origem é preferência revelada, não efeito
> causal; escolha não é expansão: o que uma vaga ganha, outra do mesmo curso
> perde. Reestimação em curso (52c): o ciclo 2 será refeito com o tipo de
> vaga do quadro de 13/02/2026; até lá, valem estes números. H3, nível do
> médico (P4): as horas cadastradas do próprio médico do PMM-E sobem +6,6
> h/sem [+5,4; +7,8] depois da entrada (+8,7 no município do posto, −2,1 fora
> dele), e 51,0% [48,4; 53,7] já tinham vínculo no município do posto; na
> comparação na nota de corte, +7,91 h/sem [−0,63; +16,45]. Associação; não
> diz nada sobre os outros médicos do município e não é efeito da bolsa nem
> da participação no PMM-E. H3, nível do município (protocolo 60, parte B,
> em auditoria): depois da chegada do 1º médico do programa, vínculos e horas
> dos especialistas sobem, mas o pré já vinha subindo e a conclusão não
> aguenta Rambachan–Roth; não dá para afirmar aumento da oferta local; as
> horas dos outros especialistas não caem. Horas cadastradas não são
> presença.

---

## Discussão: por que não sobe? Um incentivo limitado

`Discussão · Teoria`

<!-- layout: curto_texto -->

- **Incentivo limitado** a bolsa mexe numa variável; o custo do lugar continua contra
- **Pacote do corte** com a bolsa, mudam outras regras
- **Oferta** vínculo cadastrado não é presença

**Fontes:** síntese dos slides anteriores; modelo da banca 1; docs 57, 57d, 57i e 57k; auditorias 18 e 35.

**Números:** nenhum

> **Notas do apresentador.** A história parte da H1. No modelo da banca 1, o
> médico aceita a vaga se a bolsa compensa o custo do lugar. O preenchimento
> não sobe no corte; o sinal negativo é a estimativa no corte, puxada por
> poucos municípios. Incentivo limitado: a política mexe numa variável, e o
> custo do lugar (longe da origem, da família e da rede) continua contra; a
> bolsa reordena os candidatos entre as vagas abertas (H2, plano B). Pacote do
> corte: em 0,300 e 0,400 mudam também outras regras federais, então o
> contraste não isola a bolsa. Vínculo não é presença: na oferta (H3, plano
> B), o médico soma horas cadastradas, mas metade já trabalhava no município
> do posto, e no município não dá para afirmar aumento. Associação não é
> efeito; inconclusivo não é efeito zero. Próximos passos: a auditoria 38 do
> adendo 48b, o adendo 48c (capitais e UF), o teste da seleção pelo tipo de
> vaga, o ciclo 3 com a competência 202703 madura e o universo de inscritos.

<!-- deck:fim -->

<!-- apendice:fim -->
