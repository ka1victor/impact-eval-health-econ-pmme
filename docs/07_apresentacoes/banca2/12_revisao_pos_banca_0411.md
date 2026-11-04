# 12. Revisão do deck depois da banca 2 de 04/11/2026: o que os professores pediram e o que mudou

> **Finalidade:** registrar o feedback da banca de 04/11/2026 com o ajuste rastreável que cada ponto produziu (regra 4
> do [README da seção](../README.md)) e guardar o conteúdo canônico do deck revisto.<br>
> **Pedido do autor (04/11/2026):** "Edita nossa apresentação p arrumar o q estiver errado e pra ajustar o q os
> professores pediram", usando como insumo a análise metodológica da sessão anterior ([doc 11](11_explicacoes_metodo_logit.md)).<br>
> **Insumo:** o deck que o grupo apresentou, guardado sem alteração em
> [`apresentada/deck_grupo_banca2_0411.pptx`](apresentada/deck_grupo_banca2_0411.pptx) (SHA-256
> `c63bb043…ae7f2`, conferido pelo gerador).<br>
> **Deck derivado:** `output/apresentacao_banca2/deck_banca2_pos_banca.pptx` (e `.pdf`), gerado por
> `scripts/apresentacao/gerar_deck_banca2_pos_banca.py` a partir do deck do grupo, com manifesto em
> `manifesto_deck_banca2_pos_banca.json`. Divergência entre o deck e este doc é erro do deck.<br>
> **Estatuto:** apresentação. Nenhuma estimativa nova: todo número vem de `output/` (`numeros_banca2.json`,
> `VL_estimativas.csv`, `VL_resumo.json`); as contas de leitura (5β, e^5β, km) são refeitas pelo gerador, que para se
> não reproduzirem `VL1_EMP_RC` e `VL1_EMP_K5`. A hipótese, o estimando e a especificação são os do
> [doc 07](07_nova_hipotese.md) (28/10/2026); nada aqui muda protocolo.

## 1. O que a banca pediu e o ajuste de cada ponto

### 1.1 "Não entendemos"

| Pedido | Diagnóstico | Ajuste | Slide |
|---|---|---|---|
| Explicar direito a hipótese | A frase do deck ("um aumento na remuneração da bolsa eleva a probabilidade de uma vaga em um município ser escolhida") estava errada em relação ao doc 07: sugeria uma bolsa que **sobe no tempo** e um efeito **no município**, e omitia que a comparação é **só entre vagas da mesma UF**. Além disso, vinha sobreposta ao slide de motivação. | Slide próprio com a frase vigente ("entre duas vagas do mesmo curso e da mesma UF, a que paga R$ 5 mil a mais por mês tem mais chance de ser a 1ª opção do médico"), um exemplo ilustrativo (um candidato, vaga A de R$ 10 mil e vaga B de R$ 15 mil na mesma UF), o contraste, a medida (razão de chances > 1) e o que a hipótese **não** diz. "Formulada após ver os dados" segue na tela. | 3 |
| Explicar a metodologia além da especificação: justificar, comparar com referência forte, mostrar exemplo de estimação | O slide de modelo mostrava a equação do **modelo base** ("γ · origem", "peso testado"), não a do VL-1, e não justificava a escolha. | (a) Modelo com a equação do VL-1 (efeito fixo do par de UFs no lugar de γ · origem) e o papel de cada termo: testado, pareamento, controle. (b) Slide "Por que logit condicional": Bobba et al. (2026) como referência forte (salário por regra num corte, RDD por vaga + modelo de escolha) e Costa, Nunes e Sanches (2024) (médicos no Brasil); por que não a RDD por vaga (feita: F1.1, IC contém zero) e a equivalência com a Poisson com efeito fixo. (c) Exemplo de estimação no slide de resultados: tabela de coeficientes do VL-1 e a conta 5 × 0,077 = 0,385 → e^0,385 = 1,47 → 0,385 ÷ 0,514 × 100 km = 75 km. | 6, 7, 9 |
| Explicar a construção das variáveis e da base | O slide de dados listava fontes, sem dizer como cada variável é construída nem qual é a unidade da base. | Tabela "variável → construção → fonte", a base em formato longo (linhas ilustrativas, candidato × vaga, y = 1 numa só) e o funil até o modelo principal (5.714 → 5.425 → 5.417; 578.998 linhas, ≈ 107 vagas por candidato). | 4 |
| Conferir se o software considera efeitos fixos de indivíduo e de vaga/município | Conferido no código: `scripts/rdd_bolsa/25_escolha_dap.py` (`_estat`) soma o denominador dentro de cada candidato (`np.add.reduceat` nos inícios dos grupos), então tudo o que é constante no candidato sai da verossimilhança: o efeito fixo de indivíduo **está** no cálculo. `50_escolha_localizacao_par.py` cria uma coluna 0/1 por par (UF de trabalho anterior × UF da vaga), 254 no VL-1. **Não há** efeito fixo de município nem de vaga: a bolsa é a mesma no município inteiro, e um efeito fixo de município a absorveria. A distância, a região e o porte são controles, não pareamento. | Slide de identificação com a tabela "o que o software mantém fixo" (candidato: sim; par de UFs: sim; município/vaga: não; distância, região, porte: controlados) e a variação que identifica β (260 pares, 5.345 candidatos). | 8 |

### 1.2 "Colocaram conteúdo demais"

| Pedido | Ajuste |
|---|---|
| Menos slides | Corpo de 14 para 12 slides (mais Q&A e 2 de apêndice), mesmo com 3 slides novos pedidos (hipótese, por que o modelo, base). |
| Menos conteúdo por slide; enxugar a descritiva | Motivação sem os dois gráficos (regiões; antes e depois por faixa); descritiva sem os quatro cartões repetidos e sem o histograma; sai o slide "Os dados sugerem que a bolsa é um incentivo limitado" (fundido na Conclusão). |
| Tirar o gráfico que cria expectativa de RDD | Sai do corpo o slide "Perto do corte, a bolsa maior é mais escolhida" (descritiva a ±0,050 do corte). O gráfico bolsa × IVS com os saltos vai para o apêndice (A1); a regra entra na motivação como três faixas. |
| Identificação: "mantido fixo" e "especificação" | "Mantido fixo: candidato, par de UFs, distância" estava errado: a distância é controle, não fixa. Virou a tabela do §1.1. "Especificação: pós-resultado (adendo 52e)" era jargão: virou a cautela "a especificação com o par de UFs foi escolhida depois de ver o modelo base: é exploratória". |
| Robustez: "perto do corte" | Virou "Só IVS a ±0,05 de um corte" na figura e "IVS a ±0,05" no cartão, com "menos dados, IC contém 1 (inconclusivo)". |
| Especificações com nomes pouco claros | Figura de robustez refeita no pipeline só com nomes novos ("Principal: vagas da mesma UF", "Distância em log, não em km", "Região de saúde × UF da vaga", "Só o degrau R$ 10 → 15 mil" etc.); as estimativas são as mesmas. |
| Trocar o nome de "origem" | Na tela, "origem" virou **local de trabalho anterior** (o município do vínculo médico no CNES antes da inscrição, não a residência). Nas notas, o termo técnico continua quando cita documentos. |
| Navbar | Só as seções que existem, na ordem do deck: Motivação, Hipótese, Dados, Análise Descritiva, Metodologia, Identificação, Resultados, Robustez, Discussão. Saem "Pergunta" e "Literatura" (sem slide) e a navbar fica igual em todos os slides; no apêndice, nenhuma seção marcada. |
| Ordem e destaque | Cada slide abre pela mensagem no título; a hipótese, o "o que se estima", a conta 1,47 e a leitura da robustez ficam em caixas escuras; detalhes vão para as notas. |
| Formatação e typos | "escolgas", "inconclusive", "medicos", "Fontes:" vazio (slides 6 e 8), cautela duplicada (antigo 11), placeholders "Click to edit Master" escondidos no Q&A, número de página 15 no Q&A. |

### 1.3 Erros de conteúdo corrigidos

| Onde | Erro | Correção |
|---|---|---|
| Conclusão e Limitações | "Nos ciclos 1 e 3, ele some (+7% e 0%)": 1,07 e 1,00 são do **modelo base** por ciclo, não do VL-1 | VL-1 por ciclo (adendo 52g): ×1,15 [0,66; 2,01] e ×1,25 [0,90; 1,73], "IC que contém 1" |
| Slide "incentivo limitado", Conclusão, antiga H3 | "Origem ×11,0 vs. bolsa ×1,57" e "estar no estado de origem pesa ×11" | Saem da tela (decisão do autor de 28/10/2026, doc 07 §6: a origem é controle; o D_UF vem do modelo base e compara a UF de origem com outras UFs, fora da hipótese). Fica nas notas de Limitações, como resposta de reserva. |
| Conclusão | "Para a política: [...] não tira o médico do seu estado" | Afirmação sobre a UF, que é controle. Virou "a bolsa maior reordena a escolha entre vagas da mesma UF; não mostramos que leve mais médicos ao município". |
| Modelo | Equação com "γ · origem" e "peso testado" | Equação do VL-1, com α do par de UFs como pareamento |
| Dados e Descritiva | 5.421 (modelo base) e 5.425 (descritiva) apresentados como "amostra do modelo" | Funil explícito: 5.425 com local de trabalho anterior; 5.417 no modelo principal (VL-1). 5.421, do modelo base, só nas notas. |
| Notas | Notas dos slides 6, 8, 13 e 14 eram cópia de outros slides (as de 13 e 14 eram da antiga H3) | Notas reescritas: roteiro de fala e detalhe em todos os slides do corpo |

## 2. Conteúdo canônico do deck revisto

Corpo de 12 slides, Q&A e apêndice de 2. "Números" lista os códigos de `numeros_banca2.json` ou a linha de
`VL_estimativas.csv`/`VL_resumo.json` de onde o gerador lê.

| # | Seção | Título | Na tela | Números |
|---|---|---|---|---|
| 1 | — | capa do grupo (sem mudança) | — | — |
| 2 | Motivação | A bolsa do PMM-E é maior onde o município é mais vulnerável | as quatro notícias; a regra em três faixas (até 0,300: R$ 10 mil; 0,300 a 0,400: R$ 15 mil; acima de 0,400: R$ 20 mil); a pergunta em destaque | parâmetros do edital |
| 3 | Hipótese | Hipótese: na mesma UF, a bolsa maior atrai a 1ª opção | a hipótese; exemplo ilustrativo; contraste, medida e o que não é; cautela "formulada depois de ver os dados" e pacote do corte | nenhum |
| 4 | Dados | Base: uma linha por candidato × vaga possível | variáveis e construção; formato longo ilustrativo; funil | `AM_TOT_R1`, `AM_TOT_ORI`; VL-1 `n_candidatos`, `n_linhas_candidato_celula` |
| 5 | Análise Descritiva | 79% escolhem uma vaga na UF onde já trabalhavam | barras mesma UF / região / município; 51 km; 3 em 4 a até 189 km; "por isso, comparamos só vagas da mesma UF" | `ESC_UF`, `ESC_REG`, `ESC_MUN`, `ESC_N`, `ESC_DIST_P50`, `ESC_DIST_P75` |
| 6 | Metodologia | Modelo: logit condicional da 1ª opção | U_iv = β·bolsa_v + f(IVS_v) + δ·dist_iv + α_UF(i),UF(v) + θ·X_iv + ε_iv; P = exp(U_iv)/Σ exp(U_ik); e^5β; papel de cada termo; por que "condicional" | — |
| 7 | Metodologia | Por que logit condicional, e não só uma RDD por vaga | literatura (Bobba et al.; Costa, Nunes e Sanches; nós); RDD por vaga, logit condicional, Poisson; cautela sobre trocar de estimador | F1.1 (doc 44); ≈ 107 |
| 8 | Identificação | Identificação: o que fica fixo e o que supomos | tabela do que o software mantém fixo; premissas (regra, pacote, conjunto de escolha); 260 pares e 5.345 candidatos; cautela pós-resultado | `R_C1_REPR`, `R_C1_MUN`, `R_C2_REPR`, `R_C2_MUN`; `VL_resumo.json` (`colunas_de_efeito_fixo`, `pares_com_variacao_de_bolsa`, `candidatos_com_variacao_de_bolsa_em_algum_par`); VL-1 `distancia_100km` |
| 9 | Resultados | Na mesma UF, +R$ 5 mil multiplicam a chance por 1,47 | coeficientes do VL-1 (bolsa, distância, mesma região, mesmo município, população, capital); a conta até 1,47 e 75 km; ciclo 2; pré-registrada na cautela | VL-1 `coeficiente`; `VL1_EMP_RC/RCI/RCS/HOLM/K5`; `VL1_C2_RC/RCI/RCS/K5`; `VLB_EMP_RC/RCI/RCS` |
| 10 | Robustez | Robustez: sempre comparando vagas da mesma UF | `final_robustez_escolha.png`; cartões Mantém, Por ciclo, IVS a ±0,05; leitura: entre ×1,41 e ×1,52 com todos os dados | `VL1_EMP_*`, `VLLOG_EMP_*`, `VL3_EMP_*`, `VL2_EMP_*`, `VL3P_EMP_*`, `VK1_300_*`, `VK1_400_*`, `VG1_*`, `VL1_C2_*`, `VG3_*`, `VL1_EMP_PSR` |
| 11 | Discussão | Conclusão: a bolsa maior aumenta a 1ª opção? Sim | resposta ×1,47; força ×1,90 só no ciclo 2 (1 e 3: IC contém 1); teoria: 75 km, "os dados sugerem"; política sem afirmação sobre o município | `VL1_EMP_*`, `VL1_C2_*`, `VG1_RC`, `VG3_RC`, `VL1_EMP_K5/K5I/K5S` |
| 12 | Discussão | Limitações e o que cada uma implica | seis limitações com implicação (pós-resultado; sem o par, IC contém 1; só inscrição; pacote; só ciclo 2; local de trabalho anterior vem do CNES) | `VLB_EMP_*`, `VL1_C2_RC`, `VG1_RC`, `VG3_RC` |
| 13 | — | Q&A | — | — |
| A1 | Apêndice | Apêndice A1: a bolsa segue exatamente o IVS | `regra_bolsa_ivs_oficial.png` (o gráfico do grupo é esse arquivo, conferido pelo hash) | `R_C1_*`, `R_C2_*` |
| A2 | Apêndice | Apêndice A2: metade de quem entra já estava no município | antiga H3, descritiva, sem o cartão que a ligava ao "×11" | como no deck do grupo (doc 57d) |

As notas de cada slide trazem o roteiro de fala e o detalhe técnico (números com IC, códigos de documento e as
perguntas prováveis da banca, inclusive a resposta de reserva sobre o D_UF).

## 3. Proveniência

- Os gráficos de barras (descritiva e A2) são os gráficos nativos do deck do grupo, com os mesmos valores dos códigos
  `ESC_*` e do doc 57d. O gráfico bolsa × IVS do A1 é `regra_bolsa_ivs_oficial.png` do pipeline.
- Saíram da apresentação os gráficos do grupo sem script no repositório: o forest plot do resultado (substituído pela
  tabela de coeficientes), a figura de robustez (substituída pela do pipeline), o histograma de distâncias e os dois
  gráficos da motivação.
- O exemplo do slide 3 e as linhas da base no slide 4 são **ilustrativos**, rotulados assim na tela; não são dados.
- As afirmações sobre a literatura vêm do [doc 03_literatura_empirica/20](../../03_literatura_empirica/20_evidencia_empirica_hipotese_remuneracao_preenchimento.md)
  (A1, C1) e do [doc 11](11_explicacoes_metodo_logit.md); a RDD por vaga é a F1.1 do
  [doc 44](../../06_execucao/44_sintese_rdd_bolsa_multioutcome.md) (+0,063 [−0,511; +0,636]).

## 4. Em aberto para o autor

1. **Título da capa.** "Remuneração como incentivo limitado" foi mantido. Sem o ×11 da origem, "limitado" se apoia em
   75 km, no efeito forte só no ciclo 2 e no IC que contém 1 sem o par de UFs. Se a banca ler "limitado" como
   comparação com a origem, trocar o título.
2. **Apêndice.** A2 (antiga H3) pode sair: não é da hipótese e não foi pedido pela banca.
3. **Bobba et al.** O slide descreve o modelo de escolha deles como "modelo de escolha de vagas"; o detalhe (logit
   multinomial com cardápio personalizado, seção 4.1) vem do doc 11 e vale conferir no PDF antes da banca final.
4. **Adendos 52g e 52h** (por ciclo e por degrau) seguem com auditoria pendente; o slide de robustez diz isso na linha
   de fontes.
