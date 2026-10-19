# Protocolo multi-outcome da bolsa do PMM-E (E6–E9)

> **Data de congelamento:** 18/10/2026, antes de abrir qualquer outcome novo.<br>
> **Autorização do autor (18/10/2026):** rodar tudo o que for preciso com dados
> do repositório ou públicos (diferença em descontinuidades, preenchimento do
> ciclo 2, outros métodos da literatura), reestimar tudo com a base oficial e
> usar vários outcomes simultâneos, escolhidos a partir do edital. O único
> limite são pedidos externos de dados. Os números do arquivo de IVS errado só
> servem como registro de failure mode.<br>
> **Versão legível por máquina:** [`output/rdd_bolsa/protocolo_E6_multioutcome.json`](../../output/rdd_bolsa/protocolo_E6_multioutcome.json).<br>
> **Pré-registro externo:** não. O congelamento é o commit deste arquivo, antes
> dos scripts que constroem os outcomes novos.

## 1. Por que este protocolo existe

O E3 testou um único outcome, a fração de células preenchidas na 1ª chamada do
ciclo 1, e ficou inconclusivo: o efeito mínimo detectável é de ~45 p.p., três
vezes o maior efeito plausível pela literatura (Dal Bó, Finan e Rossi, 2013:
+15 p.p. de aceitação com +33% de salário). Com esse outcome, um nulo não
informa nada.

Este protocolo faz três coisas:
1. deriva do edital uma **família de outcomes** fixada antes de olhar os dados,
   para que a escolha não seja cherry-picking;
2. troca o desenho onde há ganho de precisão: empilhar cortes e ciclos, usar o
   universo de municípios e usar a diferença em descontinuidades no CNES, que
   tem pré-período;
3. trata uma ameaça que o E3 não tratava: **outra política muda nos mesmos
   cortes** (seção 4).

## 2. O que o edital diz que a bolsa deve fazer

| Fonte | Texto | Margem |
|---|---|---|
| Edital 28/2026, §11.1.5 (idem 2025) | o adicional por faixa serve para "induzir a presença de especialistas em regiões historicamente desassistidas" | **atração e presença** |
| Lei 12.871/2013, art. 22-D (Lei 15.233/2025) | "provimento de profissionais com vistas à redução no tempo de espera" | provimento |
| Edital de gestores 2/2025, §6.2 e §7.3 | "provimento e fixação"; vedada a substituição de médicos existentes, "podendo apenas ampliar a capacidade" | presença líquida, sem substituição |
| Edital 28/2026, §4.1.3.1 e §11.2 | a faixa consta do quadro de vagas, "para subsidiar o candidato na escolha da vaga"; o candidato escolhe até 2 locais | a bolsa é conhecida na inscrição: candidatos podem se reordenar entre municípios |
| Edital 28/2026, §11.12 | desistência só devolve a ajuda de custo, e não devolve por "dificuldades de adaptação ao território" | retenção é margem real |

A bolsa, portanto, deveria mover, nesta ordem: candidaturas → preenchimento →
presença do especialista no município → oferta líquida local de especialistas.
Tempo de espera, produção e saúde exigem SIA/SIH/regulação e ficam fora deste
protocolo (guarda de WP3–WP5).

## 3. Estimando, populações e tratamento

- **Contraste:** efeito de intenção de tratar do anúncio de +R$ 5 mil por mês
  no corte (0,300: R$ 10 mil → 15 mil; 0,400: R$ 15 mil → 20 mil). Salto =
  lado com bolsa maior (s > c) menos lado com bolsa menor.
- **Running variable:** IVS 2010 oficial do Ipea
  (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`). O arquivo
  `data/ivs_ipea_2010_municipios.csv` não é lido por nenhuma etapa deste
  protocolo, nem para covariáveis.
- **Populações:**

  | Código | Universo | Para quê |
  |---|---|---|
  | U | todos os municípios com IVS oficial (5.565) | margem extensiva (o município recebeu vaga, médico, oferta) e CNES; a amostra não é condicionada a ter vaga |
  | V1, V2, V3 | municípios com célula no quadro de vagas do ciclo 1, 2 ou 3 | margem intensiva (candidatura, preenchimento, presença por célula) |
  | G3 | municípios do cardápio de gestores do ciclo 3 (2.699) | demanda municipal: adesão, vagas pedidas e priorizadas |

- **Seleção.** V_k é condicionada a ter vaga, e ter vaga pode depender do
  corte. Por isso a continuidade, em U, de "ter vaga no ciclo k" e do número de
  células é um **diagnóstico obrigatório** antes de ler V_k (família F0).
- **Ciclo 3.** Este protocolo usa só o funil administrativo do ciclo 3
  (cardápio, adesão, quadro e resultado da 1ª chamada), não o estoque CNES pós-T0.
  O plano de pré-análise do ciclo 3 (doc 13 da seção 05) continua intacto:
  nenhum mês CNES a partir de 202609 é lido.

## 4. Ameaça: outra política nos mesmos cortes

As categorias de IVS do Mais Médicos para o Brasil (PMMB) usam os mesmos
limites do Ipea: 0,200, 0,300, 0,400 e 0,500
(`output/aquisicao/a07_categoria_ivs_pmmb_municipio.csv`, 5.565/5.565). A
Portaria GM/MS 752/2023 limitaria a expansão de equipes do PMMB por faixa de
IVS: até 10% abaixo de 0,3, até 40% entre 0,3 e 0,4 e até 100% acima de 0,4.
**Isso ainda precisa ser confirmado na fonte primária (tarefa D).**

Se confirmada, uma RDD em nível no corte mede o **pacote** bolsa PMM-E + teto
PMMB. O protocolo responde em três camadas:
1. **Diferença em descontinuidades (DiRD) no CNES,** com pré-período depois da
   Portaria 752 e antes do PMM-E: remove a parte fixa da descontinuidade do PMMB.
2. **Placebo de generalistas:** clínico geral e médico de família (CBO 225125,
   225142, 225170). Esse é o outcome que a Portaria 752 mexe e a bolsa do
   PMM-E não; ele mostra a descontinuidade do confundidor.
3. **Estudo de evento da DiRD** desde antes de junho de 2023. A
   descontinuidade dos especialistas deve ser plana antes do PMM-E.

Os outcomes do funil do PMM-E (candidaturas, preenchimento) só existem com o
programa. Para eles, o PMMB entra só como co-intervenção possível no lado da
demanda municipal, e isso fica registrado como limite.

## 5. Família de outcomes

Sinal pré-especificado: **+ = mais provimento**. Desistência e tempo até
preencher entram com o sinal trocado no índice.

### F0 — Diagnósticos de seleção e co-intervenção (sem hipótese de efeito)

| Id | Outcome | População | Tipo |
|---|---|---|---|
| F0.1 | município tem ≥ 1 célula no quadro do ciclo k | U | binário |
| F0.2 | células e vagas imediatas oferecidas por 10 mil habitantes | U | contagem por habitante |
| F0.3 | ciclo 3: aderiu (pediu ≥ 1 vaga); vagas pedidas; fração priorizada | G3 | binário, contagem, proporção |
| F0.4 | PMMB: vagas e médicos ativos por 10 mil habitantes (retrato de 09/10/2026) | U | contagem por habitante |

### F1 — Atração (primária)

| Id | Outcome | População | Tipo |
|---|---|---|---|
| F1.1 | candidatos de 1ª opção por célula oferecida | V1, V2, V3 | contagem |
| F1.2 | fração de células com ≥ 1 candidato (qualquer opção) | V1, V2, V3 | proporção |
| F1.3 | fração de células preenchidas na 1ª chamada (ciclo 1: definição do E3; ciclos 2 e 3: ≥ 1 alocado) | V1, V2, V3 | proporção |
| F1.4 | fração de células preenchidas até a 2ª chamada (ciclo 1: Y2 do E4; ciclo 2: alocados da 2ª chamada) | V1, V2 | proporção |

### F2 — Presença e fixação

| Id | Outcome | População | Tipo |
|---|---|---|---|
| F2.1 | especialistas ativos do ciclo k no retrato de 09/10/2026, por célula oferecida | V1, V2 | contagem |
| F2.2 | idem, por 10 mil habitantes, com zeros fora do quadro | U | contagem por habitante |
| F2.3 | D_k (≥ 1 ativo do ciclo k): o outcome do E3, mantido como âncora | V1, V2 | binário |

### F3 — Oferta líquida no CNES (primária para provimento)

| Id | Outcome | População | Tipo |
|---|---|---|---|
| F3.1 | vínculos de especialistas nas CBO-alvo dos cursos do PMM-E, por 10 mil habitantes | U e V1 | DiRD |
| F3.2 | município com ≥ 1 especialista nas CBO-alvo (cobertura) | U | DiRD, binário |
| F3.3 | horas SUS semanais das CBO-alvo por 10 mil habitantes | U | DiRD |
| F3.P1 | **placebo/confundidor:** generalistas (225125, 225142, 225170) por 10 mil | U | DiRD e estudo de evento |
| F3.P2 | **placebo:** especialistas fora das CBO-alvo por 10 mil | U | DiRD |

### F4 — Seleção de quem chega (secundária, sinal teórico ambíguo)

| Id | Outcome | População | Tipo |
|---|---|---|---|
| F4.1 | nota média do barema dos alocados | V1, V2, V3 (condicional a preencher; reportar limites de Lee) | contínuo |
| F4.2 | nota média do barema dos candidatos de 1ª opção | V1, V2, V3 | contínuo |

## 6. Métodos por tipo de outcome

Comum a todos, salvo indicação:
- **Principal:** local linear, kernel triangular, h = 0,050, EP HC1 por
  município, como no E3. Cada corte separado e, como **estimando primário
  agregado**, os dois cortes empilhados ("degrau de R$ 5 mil"): r = s − c,
  intercepto e inclinações por corte e lado, tratamento comum, cluster por
  município.
- **Ciclos:** V1, V2 e V3 empilhados com efeito fixo de ciclo e cluster por
  município. Cada ciclo também é reportado separado.
- **Inferência bias-aware (Armstrong e Kolesár, 2018, 2020):** IC honesto com
  limite de suavidade M pela regra de bolso (quártica global por lado, máx
  |f''|), mais sensibilidade em 0,5M e 2M. É reportada ao lado do HC1, sem
  substituí-lo.
- **Sensibilidade:** h = 0,030 e 0,080; local randomization na janela escolhida
  por balanço (E5), com teste de Fisher.

Por tipo:

| Tipo | Estimador adicional |
|---|---|
| contagem por célula ou por habitante | Poisson local com kernel (IRLS), offset log(células) ou log(população); efeito em escala log, comparável aos +26% de Dal Bó et al. |
| proporção por município | local linear ponderado pelo número de células (sensibilidade) e no nível célula com cluster por município |
| contínuo condicional (F4.1) | limites de Lee (2009) para a seleção por preencher |
| painel CNES (F3) | DiRD: ΔY_m = média(pós) − média(pré) e RDD sobre ΔY_m. Pré principal 2024-06 a 2025-06; pós 2025-10 a 2026-08. Estudo de evento: RDD mês a mês relativo a 2025-06, desde 2022-01, com meses trimestrais antes de 2024-06. Placebo dentro do pré: 2024-06..2024-11 vs 2024-12..2025-05. Alternativa: Y_pós com Y_pré como covariável |

## 7. Testes múltiplos e índice

- **Índice de atração-presença (Kling, Liebman e Katz, 2007):** média de
  z-scores de F1.1, F1.2, F1.3 e F2.1, padronizados pelo lado abaixo do corte
  dentro da janela, por ciclo. F4 fica fora porque o sinal é ambíguo.
- **Hipóteses primárias, duas, com Holm:** (P1) índice de atração-presença,
  cortes e ciclos empilhados; (P2) F3.1 por DiRD em U, cortes empilhados.
- **Secundárias:** todos os componentes, cortes e ciclos, com q-valores
  aguçados de Benjamini, Krieger e Yekutieli (2006) dentro de cada família.
- **Equivalência:** além do teste de zero, relatar o maior efeito que o IC 95%
  ainda admite. Referências de magnitude: +10 p.p. de preenchimento e +25% de
  candidaturas.

## 8. Covariáveis e insumos oficiais

- **População:** Censo 2022 (`output/aquisicao/populacao_censo2022_municipios.csv`).
- **IVS e subíndices, IDHM, população 2010:** base oficial do Ipea (a08).
- **Estrato territorial:** REGIC/RM (tipologia A2), só a coluna `estrato`.
- **Estoque CNES pré:** do painel novo (tarefa C), nunca da tipologia antiga.

## 9. Regras de relato

- Todas as especificações acima são relatadas, qualquer que seja o resultado.
- Nenhuma janela, corte, outcome, amostra ou estimador é reescolhido depois de
  ver resultados. Desvio necessário (por exemplo, um arquivo que não existe)
  vai para a seção de desvios do relatório, com a data e o motivo.
- Construção de outcome não olha o outcome por lado de corte nem contra o IVS.
- O resultado diz qual contraste identifica: bolsa marginal, pacote bolsa +
  PMMB (RDD em nível) ou bolsa líquida da parte fixa do PMMB (DiRD).
- A pergunta econômica do artigo pode ser revista **depois** dos resultados.
  A revisão é registrada como tal e não reescreve este protocolo.

## 10. Exposição prévia a outcomes (honestidade)

Antes deste congelamento já tinham sido vistos:
- **E3:** F1.3 do ciclo 1 e F2.3 dos ciclos 1 e 2, nos cortes;
- **E4/E5:** F1.4 do ciclo 1 (Y2) e 15 especificações do E5;
- **A4:** preenchimento por faixa;
- **A5:** trajetórias do CNES por estrato e atração nos 368 municípios do
  ciclo 1, sem corte de IVS;
- **inventário de 18/10/2026:** contagens agregadas de linhas e municípios por
  arquivo, sem quebra por corte.

Nenhum dos outcomes F0, F1.1, F1.2, F2.1, F2.2, F3 e F4 foi visto por lado de
corte. F1.3 dos ciclos 2 e 3 também não.

## 11. Execução

| Tarefa | Conteúdo | Saída |
|---|---|---|
| A | biblioteca de estimação (local linear, empilhado, honesto, Poisson local, DiRD, índice, q-valores, Lee) com testes sintéticos | `scripts/rdd_bolsa/rdd_lib.py`, `tests/test_rdd_lib.py` |
| B | construção dos outcomes F0, F1, F2 e F4 dos ciclos 1–3 | `scripts/rdd_bolsa/12_construir_outcomes_funil.py`, `output/rdd_bolsa/outcomes/` |
| C | CNES nacional: aquisição e painel município × grupo de CBO × mês | `scripts/aquisicao/a09_*`, `output/aquisicao/cnes_nacional/` |
| D | política nos mesmos cortes (Portaria 752/2023 e correlatas) | `docs/auditorias/18_*` |
| E | reestimação, com a base oficial, de tudo que dependia do arquivo errado (D3b), e registro de failure mode | `docs/auditorias/19_*` |
| E6 | estimação de F0, F1, F2 e F4 | `scripts/rdd_bolsa/13_*`, `output/rdd_bolsa/E6_*` |
| E7 | DiRD no CNES (F3) | `scripts/rdd_bolsa/14_*`, `output/rdd_bolsa/E7_*` |
| E8 | índice, testes múltiplos, síntese e relatório | `scripts/rdd_bolsa/15_*`, `output/rdd_bolsa/E8_*`, doc 41 |

## 12. Adendo de 18/10/2026 (antes de abrir os outcomes novos): escolha dos candidatos

Revisão do plano contra o pedido do autor ("outro método potencialmente mais
apropriado na literatura") encontrou uma lacuna. O arquivo de alocação traz,
para cada candidato, a 1ª e a 2ª opção entre todas as células do mesmo curso.
Isso dá variação **dentro do candidato**: a mesma pessoa vê municípios com
bolsas diferentes. Um modelo de escolha discreta usa essa variação e é muito
mais potente que a RDD entre municípios (Dal Bó, Finan e Rossi, 2013, usam
candidaturas; McFadden, 1974, para o logit condicional).

- **E9, escolha revelada (secundária, exploratória):** logit condicional da
  1ª opção do candidato no conjunto de células do seu curso e ciclo com vaga
  imediata. Atributos: bolsa anunciada (R$ mil); função contínua do IVS
  (polinômio de grau 1 e 2 por faixa, para que a bolsa seja identificada pelo
  degrau nos cortes e não pelo gradiente do IVS); log da população (Censo
  2022); macrorregião; estrato territorial. A 2ª opção entra como sensibilidade
  (logit ordenado por ranking, "exploded logit").
- **Leitura:** efeito da bolsa sobre a **escolha** entre vagas, ou seja,
  realocação entre municípios. Não é efeito líquido sobre o total de
  candidatos. Sem a residência do candidato, a distância não entra; essa
  limitação é declarada.
- **Ciclos:** 1, 2 (se a 1ª chamada for obtida de fonte oficial) e 3, em
  separado e empilhados.
- **Saídas:** `scripts/rdd_bolsa/16_*`, `output/rdd_bolsa/E9_*`.

## 13. Adendo de 18/10/2026 (antes de abrir os outcomes novos): políticas nos mesmos cortes

A tarefa D ([`auditorias/18`](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md))
verificou em fonte primária que outras regras federais mudam nos mesmos cortes:
- **Portaria 752/2023 (PMMB):** teto de vagas por faixa de IVS, em 0,3 e 0,4,
  com o limite no lado de cima;
- **Portaria 3.493/2024 (financiamento da APS):** estrato = IVS × porte. Muda
  em 0,300 só nas classes de porte 2 e 3, e em 0,400 só nas classes 1, 2 e 4;
- **emendas e incrementos de APS e MAC, 2024–2027:** +20% de teto com "IVS
  maior que 0,3";
- **ajuda de custo do PMMB (Portaria Interministerial 604/2023):** muda em
  0,400, fora da Amazônia Legal e da faixa de fronteira;
- regras menores (lista na auditoria 18).

**Consequência:** a RDD em nível mede um **pacote**. A DiRD só remove a parte
dessas políticas que é constante entre pré e pós. Especificações
suplementares, fixadas agora:

| Id | Especificação | Para quê |
|---|---|---|
| S1 | RDD em `ativas_coparticipacao` do PMMB (retrato a07) | ver se a 752 aparece no corte |
| S2 | donut: excluir os municípios com IVS exatamente 0,300 e 0,400 | regra de limite oposta (752 e bolsa) |
| S3 | heterogeneidade por classe de porte: o estrato da APS muda × não muda no corte | isolar o canal da APS |
| S4 | em 0,400: dentro × fora da Amazônia Legal e faixa de fronteira | isolar a ajuda de custo do PMMB |
| S5 | estudo de evento da DiRD com as datas de cada política marcadas; pré extra de 2022-01 a 2023-03, antes de todas | a descontinuidade das CBO-alvo deve ser plana antes do PMM-E |
| S6 | placebo de generalistas com a CBO 225130 (medicina de família) em separado | desvio do §5, registrado antes de abrir |

**O que é mais robusto a esse pacote:** outcomes do funil do candidato
(candidaturas, escolha, E9). As outras políticas não mudam a remuneração do
especialista do PMM-E. A exceção é o +20% da MAC em 0,3, que pode mudar a
estrutura do serviço; isso é declarado como limite.

## 14. Esclarecimento de 18/10/2026 (antes de estimar o E9): conjunto de escolha

A construção dos dados (tarefa B, doc 41a) mostrou que muitas 1ªs opções caem
em células só com cadastro de reserva, sem vaga imediata. Isso é contagem de
arquivo, sem quebra por corte ou faixa. Restringir o conjunto de escolha às
células com vaga imediata descartaria essas escolhas reais. Fica fixado:
- **E9 principal:** o conjunto de escolha são todas as células do curso e
  ciclo no quadro da 1ª chamada, com ou sem vaga imediata. Entra o atributo
  "tem vaga imediata" (e o log de vagas imediatas + 1).
- **Sensibilidade:** só células com vaga imediata e só candidatos cuja 1ª
  opção está nelas (a definição original do §12).

## 15. Esclarecimento de 18/10/2026 (antes de estimar o E9): forma funcional

"Polinômio por faixa" (§12), com intercepto próprio em cada faixa, deixaria a
bolsa colinear com as faixas, e ela não seria identificada. A forma fica fixada
assim, para que a bolsa seja identificada só pelos degraus nos cortes:

- **IVS como spline contínuo,** com nós em 0,300 e 0,400: inclinações livres
  por faixa e sem salto de nível. Variante: termos quadráticos por segmento,
  também contínuos nos nós.
- **Principal:** bolsa em R$ mil, linear (um coeficiente para os dois degraus de
  R$ 5 mil).
- **Sensibilidade:** um indicador de degrau por corte, para testar se os dois
  efeitos são iguais.
- **Demais atributos** (§12 e §14): tem vaga imediata, log(vagas imediatas + 1),
  log da população (Censo 2022), macrorregião e estrato.
- **Erros-padrão:** sanduíche com cluster por conjunto de escolha (curso ×
  ciclo); também o EP de máxima verossimilhança e o cluster por candidato.
- **Relato:** o coeficiente da bolsa, a razão de chances por +R$ 5 mil e a
  variação média da probabilidade de escolha de uma célula quando a bolsa sobe
  R$ 5 mil, mantido o resto.

## 16. Esclarecimento de 19/10/2026 (antes de estimar o E7): horas no CNES

A auditoria independente do painel nacional (tarefa C) levantou duas questões
de definição. Nenhum outcome do CNES foi aberto por lado de corte.

1. **"Horas SUS" (F3.3)** passa a ser a soma das horas ambulatoriais e
   hospitalares dos vínculos com `TP_SUS_NAO_SUS = 'S'`. A soma sem esse filtro
   misturava vínculos não SUS; ela continua no painel como `horas_totais` e
   entra só como sensibilidade rotulada.
2. **Horas em branco.** São 22 vínculos por mês, os mesmos em todos os meses.
   - **Principal:** célula com campo de hora em branco fica sem valor de horas,
     e o município sai do F3.3 com nota (regra atual da tarefa C).
   - **Sensibilidade rotulada:** a soma parcial das horas observadas, com a
     contagem de vínculos em branco ao lado.
3. **`todos_medicos`** inclui residentes (CBO 2231F9). Entra também uma
   variante sem residentes; nenhuma das duas é outcome primário.
