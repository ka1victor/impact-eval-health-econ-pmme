# Plano da entrega empírica da banca 2 (28/10 e 04/11/2026)

> **Data:** 26/10/2026.<br>
> **Pedido do autor:** revisar o que já temos e o que ainda não temos de
> resultado, e decidir como fechar as etapas que a banca 2 cobra: hipótese
> econômica, base de dados e descritivas, metodologia e hipóteses de
> identificação, resultados, robustez e discussão.<br>
> **Insumos:** o deck atual do grupo (`PEE - Modelo econômico 1.pptx`, 36
> slides, recebido em 26/10/2026, fora do repositório); a síntese
> [doc 57](../../06_execucao/57_sintese_perguntas_reformuladas.md) e os blocos
> 57a–57h, todos auditados (auditorias 20–30).<br>
> **Estatuto:** plano e recomendação. A escolha da hipótese central continua
> sendo do autor (doc 57, §7). Este documento não traz número novo: os números
> citados estão nos docs de resultado indicados em cada linha.

## 1. Onde estamos, bloco a bloco da banca

| Bloco cobrado | O que já existe | O que falta | Estado |
|---|---|---|:---:|
| Hipótese econômica | modelo da banca 1 (Moehling; Redding e Rossi-Hansberg; Choné e Ma; Burdett, Shi e Wright) e a hipótese H1 de preenchimento | decompor a H1 na cadeia do próprio modelo (seção 3) e dizer qual elo é a hipótese central | ⚠️ decisão do autor |
| Base de dados e descritivas | todas as bases adquiridas e auditadas: quadros e listas dos ciclos 1–3, candidatos ligados ao CNES (G1), CNES profissional mês a mês (a16), SIA, SIH, TISS | **uma tabela descritiva única** (células, municípios, candidatos, preenchimento e bolsa por faixa e ciclo), gerada por script | ❌ |
| Metodologia e hipóteses de identificação | protocolos congelados 40, 47, 48, 52, 54–59; RDD sharp com IVS oficial validada (R1); logit condicional com IVS em spline | um slide que mostre o modelo da banca 1 virando a equação estimada (seção 4) | ⚠️ |
| Resultados | doc 57: nenhuma primária rejeita zero depois do Holm; P1 no limite (p 0,065); P4 e P3 como associações | escolher o recorte (seção 5) e as 3–4 figuras | ⚠️ |
| Robustez | E5 (15 especificações, IC honesto), placebos de corte e de outcome, densidade, balanço, Holm e BKY, M0–M9 do P1, Rambachan–Roth e comparação alternativa (57h) | só seleção e figura de resumo | ✅ |
| Discussão | doc 44 §5–§8, doc 57 §5–§7, literatura de magnitude (doc 44 §6) | texto curto por hipótese | ⚠️ |

## 2. Erros do deck atual que precisam sair antes de 28/10

| Slides | Problema | Correção | Fonte |
|---|---|---|---|
| 5–8, 10 | grade da bolsa do FAQ (R$ 20 mil só acima de 0,500; R$ 10 mil até 0,400). **Não é a grade aplicada.** | aplicada: até 0,300 → R$ 10 mil; 0,301–0,400 → R$ 15 mil; acima de 0,400 → R$ 20 mil. Reproduz 368/368, 454/454 e 747/748 municípios | [auditoria 16](../../auditorias/16_ivs_2010_oficial_e_arquivo_local.md), §2 |
| 8 | "O IVS é o piso, não o critério: 177 dos 368" | artefato do arquivo de IVS errado. Com o IVS oficial a regra é sharp, sem exceção. Se o tema aparecer, é o slide do failure mode, uma vez | auditoria 16, §3; [auditoria 19](../../auditorias/19_reestimacao_base_oficial_failure_mode.md) |
| 11, 14 | "indícios de efetividade" a partir de crescimento antes × depois por faixa | antes × depois sem comparação não é efeito. A DiRD no CNES (E7) não detecta mudança. Rebaixar para descritivo ou retirar | doc 44, §5.3 |
| 9, 11, 14 | gráficos de crescimento por faixa sem proveniência no slide | só entram se saírem de `output/` por script, com a faixa pela grade aplicada | `CLAUDE.md`, proveniência |
| 34, 35 | "proporção de **vagas** preenchidas", 35,6% num slide e 30% no outro | é a fração de **células** (estabelecimento × curso) com alguma confirmação ou homologação. 30,3% na 1ª chamada e 35,6% somando a 2ª. Dizer qual | notas do próprio slide 31 |
| 34, 35 | "SGETS" e "especialidade" | SGTES; "curso" (a ponte para CBO é outra coisa) | idem |
| 35 | IVS como "custo territorial agregado" | no desenho, o IVS é a running variable e entra contínuo (spline). Ele **controla** o custo do lugar; a bolsa é o que salta. Dizer assim, porque é a hipótese de identificação | doc 44, §2 |

## 3. Proposta de hipóteses: a cadeia do próprio modelo

O slide 21 do deck já tem a cadeia B ↑ → V ↑ → π ↑ → Pr(Y = 1) ↑. A banca 2 pode
testar **cada seta** em vez de só a última. Com isso o resultado nulo do
preenchimento deixa de ser o fim da história e passa a ter explicação dentro do
modelo.

| Hipótese | Seta do modelo | Teste | Onde está | Leitura hoje |
|---|---|---|---|---|
| **H1** (banca 1) | B → Pr(Y = 1) | RDD do preenchimento da célula aberta, ciclos 1–3 | [49](../../06_execucao/49_resultados_contagem_vagas_preenchidas.md) §15 (A3); [57](../../06_execucao/57_sintese_perguntas_reformuladas.md) §4.2 | inconclusivo; os dados descartam aumentos grandes com cortes empilhados |
| **H2** | B → V → π | logit condicional: peso da bolsa na escolha entre vagas abertas | [57a](../../06_execucao/57a_resultados_P1_escolha.md) (P1a) | no limite (p 0,065); robusto só no ciclo 2 |
| **H3** (título do deck: "incentivo limitado") | peso da bolsa contra o custo do lugar em V | mesmos coeficientes do M1: bolsa contra distância e origem | 57a §5–§6 | ver seção 6.1: falta o teste formal |
| **H4** | chegada → capacidade líquida | trajetória do médico (P4) e comparação por pouco (P6, 57h parte B) | [57d](../../06_execucao/57d_resultados_P4_trajetoria.md), [57h](../../06_execucao/57h_resultados_P3P4_sensibilidade.md) | associação: o médico soma horas, mas metade já estava no município |

**Recomendação (proposta ao autor):** H3 como hipótese central, com H2 como o
parâmetro que ela usa e H1 como teste de consistência. Motivos:
- é o título que o grupo já escolheu e o que o modelo da banca 1 prevê
  ("a política mexe em uma variável só; preço e custo do lugar continuam
  contra");
- é a margem em que a bolsa age diretamente e em que a comparação é entre
  vagas já abertas (doc 51, §1);
- os coeficientes de distância e origem são estimados com muita precisão.
  Uma comparação de magnitude com **limite** não depende de o coeficiente da
  bolsa ser significativo, ao contrário da DAP, que é uma razão e explode
  quando o denominador está perto de zero (57a, §5);
- explica o nulo de H1: se a bolsa pesa pouco perto do custo do lugar, ela
  reordena candidatos entre vagas, mas não muda quantas células preenchem
  (P1g; realocação, 57g).

A alternativa (manter H1 como central e relatar o nulo) continua válida e usa o
mesmo material. Ela só muda a ordem dos slides.

## 4. Metodologia econométrica e hipóteses de identificação

> **Definição do autor (26/10/2026):** o bloco "Metodologia" da banca é a
> **metodologia econométrica**: estimadores, unidade, amostra, inferência e
> hipóteses de identificação. A ponte entre o modelo teórico e a equação
> estimada fica no fim do bloco de hipótese (um slide), e as equações do
> modelo vão para o apêndice (ver
> [banca final](../banca_final/01_diagrama_teoria_mudanca.md)).

### 4.1 Um estimador por hipótese

| Hipótese | Estimador | Unidade e amostra | Especificação principal | Inferência |
|---|---|---|---|---|
| H1 (preenchimento) | RDD *sharp* local linear nos cortes 0,300 e 0,400 do IVS 2010 oficial | célula aberta (A3); município (N); ciclos 1–3 | kernel triangular, h = 0,050, uma reta de cada lado por ciclo × corte e salto comum (cortes e ciclos empilhados); efeitos fixos de curso × ciclo e de tipo de vaga | CR1 por município; IC honesto (Armstrong–Kolesár) como sensibilidade; Holm nas primárias e BKY nas secundárias |
| H2 e H3 (escolha e incentivo limitado) | logit condicional (McFadden) da 1ª opção do candidato entre as células do conjunto de escolha | candidato × célula do mesmo curso e ciclo, ciclos 1–3, origem ligada ao CNES (G1) | bolsa linear em R$ mil; IVS em spline com nós em 0,300 e 0,400; distância origem–vaga, mesma UF, mesma região, mesmo município, porte, capital, vaga imediata | sanduíche com cluster por conjunto de escolha; H3 como combinação linear com a covariância conjunta (protocolo 52b) |
| H4 (capacidade líquida) | estudo de evento escalonado (Callaway–Sant'Anna) no médico; comparação local na nota de corte (P6 e 57h parte B) | médico × mês, ciclos 1–2; candidato perto da nota de corte | controles ainda não tratados, base g − 1; efeito fixo de célula na comparação local | bootstrap multiplicador por médico; permutação dentro da célula; Rambachan–Roth para violações de tendência |

### 4.2 Hipóteses de identificação e como foram testadas

| Hipótese | Vale para | Teste ou argumento | Onde |
|---|---|---|---|
| regra *sharp*: a faixa é função determinística do IVS | H1, H2, H3 | IVS oficial reproduz a faixa em todos os municípios dos três ciclos | auditoria 16 |
| sem manipulação da running variable | H1, H2, H3 | IVS medido em 2010, anos antes do programa; teste de densidade | E1 |
| continuidade dos potenciais no corte | H1 | balanço de covariáveis pré-determinadas; placebos de outcome e de corte | docs 37, 41, 49 |
| dado o IVS contínuo, só a bolsa salta | H2, H3 | spline com nós nos cortes; placebos de corte; spline cúbico | E9, 57a |
| independência de alternativas irrelevantes dentro do conjunto | H2, H3 | logit aninhado por região e logit misto como robustez | 57a (M8, M9) |
| tendências paralelas entre coortes de entrada | H4 | teste conjunto do pré; Rambachan–Roth | 57d, 57h |
| alocação quase aleatória perto da nota de corte | H4 (P6) | balanço em r; desempate por regra fixa declarado | 57f |

**Ameaça comum aos cortes:** as co-políticas nos mesmos cortes
([auditoria 18](../../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)).
Por isso o contraste é sempre chamado de "pacote do corte". Na DiRD, só a parte
fixa no tempo dessas políticas sai.

### 4.3 Ponte do modelo para a equação (fim do bloco de hipótese)

```
Modelo (Moehling):  V_rm = Σ_t δ^t [ E(w_m | B_m) / p_m − c_rm ]
Estimado (M1):      U_rm = β·B_m + f(IVS_m) − γ·dist_rm + θ·mesma_UF_rm + λ·X_m + ε_rm
```

- β é a utilidade marginal da bolsa, o 1/p do modelo.
- γ e θ são o custo geográfico de Redding e Rossi-Hansberg.
- f(IVS) absorve o que varia suave com a vulnerabilidade: custo laboral
  (Choné e Ma), amenidades e preços.
- ε tipo valor extremo dá o logit condicional. A agregação de Burdett, Shi e
  Wright leva de π a Pr(Y = 1).

## 5. Resultados: o que mostrar e em que ordem

| Ordem | Slide | Figura | Já existe? |
|---|---|---|---|
| 1 | regra sharp com o IVS oficial | `output/apresentacao_banca2/regra_bolsa_ivs_oficial.png` | ✅ |
| 2 | H1: preenchimento no corte, com limite superior e MDE | `output/apresentacao_banca2/descarte_preenchimento.png` ou figura do A3 (`NA_figuras/`) | ✅ |
| 3 | H2/H3: coeficientes do M1 na mesma escala de utilidade (bolsa de R$ 10 para R$ 20 mil, 100 km, mesma UF, mesma região) | **nova** (seção 6.1) | ❌ |
| 4 | H2 por ciclo | `output/rdd_bolsa/P1_figuras/P1_beta_por_ciclo.png` | ✅ |
| 5 | H4: horas do médico ao redor da entrada | `output/rdd_bolsa/P4_figuras/` | ✅ |
| 6 | cadeia inteira (resumo) | `output/apresentacao_banca2/cadeia_sintese_principal.png` | ✅, mas é de 19/10: atualizar com P1, P4 e P6 |

**Robustez** (um slide de tabela e um de figura):
- H1: E5 (15 especificações), IC honesto, janelas, donut e o nível da célula.
- H2/H3: M0–M9 (sem distância, log da distância, efeito fixo de UF,
  explodido, misto, aninhado), placebos de corte, spline cúbico, cluster por
  curso.
- H4: Rambachan–Roth e a comparação com os não alocados por pouco (57h).
- Em tudo: Holm e BKY.

**Discussão:**
- literatura de magnitude (doc 44, §6);
- pacote do corte;
- escolha condicional a se candidatar, sem a margem extensiva;
- vínculo cadastrado não é presença;
- o ciclo 3 como replicação fora da amostra.

## 6. O que ainda falta rodar ou produzir

### 6.1 Antes de 28/10 (crítico)

| # | Tarefa | Como | Regra |
|---|---|---|---|
| 1 | **H3 formal: comparação de magnitudes no M1.** Testar se o efeito de toda a amplitude da bolsa (10·β) é menor que o de a vaga ficar na UF de origem (θ), e expressar a amplitude da bolsa em km equivalentes, com IC | protocolo [52b](../../06_execucao/52b_protocolo_P1h_magnitudes.md), congelado em 26/10/2026 antes de calcular; o script 25c reestima o M1 só para obter a covariância conjunta, com portão de reprodução contra o CSV do P1 | pós-resultado, rotulado; **feito**: [57i](../../06_execucao/57i_resultados_P1h_magnitudes.md), auditado ([auditoria 31](../../auditorias/31_auditoria_P1h_magnitudes.md), aprovado com correções de rótulo) |
| 2 | Figura do item 3 da seção 5 e tabela de descritivas | `scripts/apresentacao/gerar_figuras_banca2.py`, lendo de `output/` | número do slide sai de `output/` e é conferido por teste |
| 3 | Atualizar a figura da cadeia com P1, P4 e P6 | mesmo script | idem |
| 4 | Reescrever `01_roteiro_narrativo.md` e `02_conteudo_slides.md` da banca 2 no arco das seções 3–5 | depois da decisão do autor | o deck é derivado; divergência é erro do deck |
| 5 | Corrigir o deck (seção 2) | o grupo, no `.pptx` | — |

### 6.2 Até 04/11

- Auditoria independente dos cenários do T1.6 (doc 57, §6). Só depois disso um
  cenário entra num slide, e sempre rotulado como simulação.
- Uma figura do T1.6, se auditada. Ela mostra o limite do modelo: um aumento
  uniforme da bolsa não muda nenhuma escolha no logit condicional (doc 57, §4.2).
  Isso é um argumento para "incentivo limitado" pelo desenho da política, não
  pelos dados.
- Apêndice de robustez completo.

### 6.3 Depois da banca (não cabe no prazo)

| Item | Por quê |
|---|---|
| Pedido do universo de inscritos | responde à margem extensiva; ofício pronto em `docs/pedidos_dados/` |
| Ciclo 3 em 202703 | replicação fora da amostra do sinal do ciclo 2 e oferta líquida município–mês |
| Folha de pagamento | anunciado contra recebido; presença |

## 7. Coordenação

Uma sessão paralela ("Continuação análise P1/P3/P4/P6") roda as análises dos
blocos 57a–57h e a síntese 57 (scripts 33–35). Para não haver retrabalho:
- as análises ficam nela, inclusive a tarefa 1 da seção 6.1, se o autor quiser;
- o conteúdo da banca 2 (este diretório) e as figuras de apresentação ficam
  nesta;
- ninguém edita o doc 57 à mão: ele é gerado pelo script 33.

## 8. Decisões do autor

| Decisão | Opções | Recomendação |
|---|---|---|
| Hipótese central | H3 (incentivo limitado) com H2 e H1 na cadeia; ou H1 com o nulo | H3 |
| Rodar o teste formal de H3 (6.1, item 1) | sim, como adendo datado ao protocolo 52; não, e mostrar só os coeficientes | sim |
| Quem apresenta em 28/10 e quem em 04/11 | depende da escala da banca | — |

## 9. Registro de decisões

| Data | Decisão | Quem |
|---|---|---|
| 26/10/2026 | o bloco "Metodologia" é a metodologia econométrica (§4) | autor |
| 26/10/2026 | fazer o necessário para deixar a entrega pronta; com isso, roda o teste formal de H3 (protocolo 52b) e o arco segue a recomendação da §3, com H1 apresentada como teste da cadeia | autor delegou; a hipótese central continua revisável por ele |
| 26/10/2026 | diagrama causal e equações no apêndice ficam para a banca final ([`banca_final/`](../banca_final/README.md)) | autor |
| 26/10/2026 | o Vinicius faz os dois slides que usam os resultados do modelo; o conteúdo daqui serve de fonte para eles | grupo |
