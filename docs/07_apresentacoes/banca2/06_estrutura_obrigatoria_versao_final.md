# Estrutura obrigatória da versão final da apresentação da banca 2

> **Decisão do autor, 26/10/2026.** Vale para toda versão futura do deck da banca
> 2. **Só a versão curta é usada.** As versões longas não serão usadas e não
> precisam mais ser geradas; o deck completo fica só como registro. Um deck que fuja desta estrutura
> está errado e deve ser corrigido no gerador
> (`scripts/apresentacao/gerar_deck_banca2.py`), não à mão.<br>
> **Estatuto:** regra de apresentação. Não muda protocolo nem resultado.

> [!IMPORTANT]
> **Hipótese de 28/10/2026** (decisão do autor; [doc 07](07_nova_hipotese.md)): "a hipótese é simplesmente sobre o
> efeito bolsa → 1ª opção", com "só comparação entre municípios da mesma UF"; "UF, origem etc. é tudo
> controle/pareamento". Nenhum slide, nem do apêndice, interpreta o coeficiente da origem; o D_UF sai da tela. A
> estrutura das oito seções, os tetos e a rubrica não mudam; o encaixe vigente está no §3.

> [!NOTE]
> **Hipótese única a partir de 27/10/2026** ([doc 07](07_nova_hipotese.md)): o corpo do deck tem só a antiga H2
> (bolsa × origem), formulada depois de ver os dados e dita assim no slide de Hipótese. A antiga H1 (preenchimento
> no corte) é uma linha de motivação no slide de Hipótese e um gráfico no apêndice; a antiga H3 (oferta) é uma
> frase no apêndice. A numeração de 26/10/2026 (H1 preenchimento; H2 bolsa × origem, antes H3; H3 oferta, antes H4)
> continua nos documentos de análise e no campo `hipotese_apresentacao` do registro de números.

## 1. As seções, nesta ordem

| # | Seção | O que entra | O que não entra |
|---|---|---|---|
| 1 | **Hipótese** | **uma só** na versão final, depois que os professores validarem. Até lá pode haver mais de uma, mas as de plano B aparecem **em cinza**, visivelmente secundárias | várias hipóteses com o mesmo peso visual |
| 2 | **Dados** | variáveis principais e secundárias e a **fonte de cada uma** (base, órgão, período, unidade) | resultados |
| 3 | **Análise descritiva** | visão básica das variáveis importantes para o problema: tamanho das amostras, médias e distribuição das variáveis críticas (por exemplo, IVS × faixa, distribuição do IVS, vagas e preenchimento por ciclo) | estimativas causais |
| 4 | **Metodologia** | o método econométrico e a **especificação do nosso caso**: outcome, amostra, equação em palavras, o que é por ciclo, erro-padrão | premissas e testes de validade (vão para Identificação) |
| 5 | **Identificação** | as **premissas do método** e a **aderência do nosso caso** a cada uma: regra *sharp*, sem manipulação, continuidade, pacote do corte, tendências paralelas etc., cada uma com o teste ou argumento | resultados |
| 6 | **Resultados** | **gráficos da especificação principal** | especificações secundárias |
| 7 | **Robustez** | **gráficos das especificações secundárias**: controles a mais, outras janelas, outras medidas, placebos, IC honesto etc. | — |
| 8 | **Discussão** | **explicação simples em termos da teoria** (o modelo da banca 1: bolsa, custo do lugar, escolha, preenchimento); desde 27/10/2026, em dois slides: **Conclusão** (retoma a pergunta e sintetiza os resultados) e **Limitações** (cada uma com a sua implicação), que a rubrica da banca avalia em separado (§4) | jargão técnico novo |

## 2. Regras que continuam valendo

Todas as decisões anteriores do autor
([`05_discussao_historia_empirica.md`](05_discussao_historia_empirica.md), §1)
continuam, desde que caibam nesta estrutura:
- efeitos por corte, sem empilhado no corpo;
- pouco texto;
- figura grande com "Como ler";
- especificação em linguagem simples;
- números só de `output/`, com cautelas obrigatórias;
- **só o deck curto** (`output/apresentacao_banca2/deck_banca2_curto.pptx`
  e `.pdf`). O completo não é mais gerado nem atualizado; o gerador só o
  refaz com `--completo`.
- **no máximo cerca de 30 palavras visíveis por slide** (pedido do autor de
  26/10/2026: "slides 4, 7 etc. têm texto demais"), fora o título, a figura e
  a linha de fontes. Conta como palavra todo trecho com letra ou algarismo;
  o teto aplicado pelo gerador e pelo teste é 30;
- **especificação em até 4 linhas curtas**, em frases telegráficas: a equação
  em palavras numa linha grande no centro e, embaixo, outcome, amostra ou
  comparação e cuidado. Erro-padrão, o que é comum e o que é por ciclo,
  sensibilidades e detalhes de amostra vão para as notas do apresentador;
- nos demais slides, o detalhe também vai para as notas; a cautela
  obrigatória continua na tela, curta;
- **no máximo 14 slides** (decisão do autor de 26/10/2026: "esses últimos
  decks tão muito grandes. pode deixar mais curtos mesmo, só com os
  principais slides, idealmente <15 slides"). Só os slides principais; o
  que for cortado vai para as notas do apresentador. O teto vale para o
  corpo e é aplicado pelo gerador e pelo teste;
- **apêndice curto, de no máximo 2 slides, depois da Discussão** (decisão do
  autor de 27/10/2026: "pode tirar todas as hipóteses além da H2 [...]. Deixa
  no apêndice, se quiser, mas bem rápido"): só o que saiu do corpo por ser de
  outra hipótese. No apêndice, nenhuma seção do rodapé fica marcada. O teto
  também é aplicado pelo gerador e pelo teste;
- **redação das auditorias 49 e 50**: "não detectamos aumento", nunca "não
  muda" ou "não encheu"; o sinal negativo em 0,300 "anda junto com a UF", não
  "some"; números da escolha com o quadro do ciclo 2 de 13/02/2026. Desde
  28/10/2026, o resultado principal é o peso da bolsa comparando vagas da
  mesma UF (VL-1, adendo 52e), dito como pós-resultado, com a especificação
  pré-registrada (sem fixar a UF, IC que contém 1) nas limitações; na tela,
  nada de "origem pesa", "×11" ou "D_UF".

## 3. Como o conteúdo atual se encaixa (versão de 28/10/2026: bolsa → 1ª opção, dentro da mesma UF)

O conteúdo canônico está em [`04_conteudo_deck_curto.md`](04_conteudo_deck_curto.md); a hipótese, em
[`07_nova_hipotese.md`](07_nova_hipotese.md); o roteiro, no [doc 09](09_roteiro_fala_7min.md). 11 slides no corpo e 1
no apêndice:

| Seção | Slides | Conteúdo |
|---|---|---|
| Hipótese | 1 | a pergunta no título (a bolsa maior muda a 1ª opção?); a hipótese em destaque ("comparando vagas da mesma UF, a de bolsa maior tem mais chance de ser a 1ª opção"); em cinza, a motivação (no corte, preenchimento sem aumento detectado); "formulada após ver os dados" na tela |
| Dados | 2 | fontes e variáveis, unidade de observação (candidato × vaga) e funil da amostra por ciclo |
| Análise descritiva | 3–5 | a regra *sharp* bolsa × IVS; onde escolhem (79% na própria UF), como **motivação para comparar dentro da UF**; a F2 do doc 66, descritiva da hipótese (perto do corte, na UF de origem, o lado de bolsa maior recebe mais 1ªs opções do que tem de vagas) |
| Metodologia | 6 | logit condicional com efeito fixo de UF de origem × UF da vaga; o candidato comparado consigo mesmo, entre vagas da mesma UF; teste β > zero, erro-padrão agrupado por conjunto de escolha |
| Identificação | 7 | bolsa por regra (*sharp*); o que fica fixo (candidato, par de UFs, distância); pacote do corte; especificação pós-resultado (adendo 52e); conjunto de escolha suposto |
| Resultados | 8 | o VL-1: ciclos 1–3 e ciclo 2, com os km equivalentes; a pré-registrada, sem fixar a UF, na cautela |
| Robustez | 9 | só dentro da mesma UF: distância em log, região de saúde × UF, só vagas perto do corte (inconclusiva) e o VL-1 por ciclo (forte só no ciclo 2; nos ciclos 1 e 3 o IC contém 1; adendo 52g) |
| Discussão | 10–11 | **Conclusão** (a bolsa maior aumenta a 1ª opção, comparando vagas da mesma UF? Sim, forte só no ciclo 2; a leitura pela teoria como "os dados sugerem"); **Limitações** (pós-resultado; sem fixar a UF, IC contém 1; escolha ≠ preenchimento; pacote do corte; só ciclo 2; origem = CNES) |
| Apêndice | 12 | o fato da antiga H1 só pareando municípios da mesma UF |

Saíram em 28/10/2026: o teste central origem × toda a bolsa (D_UF, ×11,0 contra ×1,57), do corpo e do apêndice (fica
numa linha das notas do slide de Limitações); a RDD sem controle do apêndice; a antiga H3. A versão de 27/10/2026 está
no histórico (commit `33d15d9`) e o mapa, no [doc 10](10_mapa_deck_anterior_para_rubrica.md), §6.

## 4. A rubrica da banca (27/10/2026)

A banca dá nota a nove critérios: (1) slides, estrutura e narrativa; (2) apresentador; (3) base de dados, com a origem
dos dados, as variáveis, a **unidade de observação** e a **construção da amostra**; (4) análise descritiva interpretada
e ligada à pergunta; (5) modelo econométrico apresentado e **justificado**; (6) interpretação dos coeficientes e dos
testes; (7) robustez; (8) conclusões que retomam a pergunta; (9) limitações e **as suas implicações**. As oito seções
do §1 continuam; a rubrica pede duas partes que cabem na Discussão, a **Conclusão** e as **Limitações**, cada uma no
seu slide. A apresentação tem cerca de 7 minutos: o corpo cabe em 10 a 11 slides de 30 a 50 s, e cada slide do
corpo leva nas notas um roteiro de fala com tempo-alvo (`> **Roteiro (N s).**` no doc 04; roteiro inteiro no
[doc 09](09_roteiro_fala_7min.md)). O gerador para se a soma sair de 6:30 a 7:30. O mapa do deck anterior para este
está no [doc 10](10_mapa_deck_anterior_para_rubrica.md).
