# Estrutura obrigatória da versão final da apresentação da banca 2

> **Decisão do autor, 26/10/2026.** Vale para toda versão futura do deck da banca
> 2. **Só a versão curta é usada.** As versões longas não serão usadas e não
> precisam mais ser geradas; o deck completo fica só como registro. Um deck que fuja desta estrutura
> está errado e deve ser corrigido no gerador
> (`scripts/apresentacao/gerar_deck_banca2.py`), não à mão.<br>
> **Estatuto:** regra de apresentação. Não muda protocolo nem resultado.

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
| 8 | **Discussão** | **explicação simples em termos da teoria** (o modelo da banca 1: bolsa, custo do lugar, escolha, preenchimento) | jargão técnico novo |

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
  "some"; o teste central da hipótese é origem × toda a bolsa; números da
  escolha com o quadro do ciclo 2 de 13/02/2026.

## 3. Como o conteúdo atual se encaixa (versão de 27/10/2026: hipótese única)

O conteúdo canônico está em [`04_conteudo_deck_curto.md`](04_conteudo_deck_curto.md); a hipótese e o roteiro, em
[`07_nova_hipotese.md`](07_nova_hipotese.md). 11 slides no corpo e 2 no apêndice:

| Seção | Slides | Conteúdo |
|---|---|---|
| Hipótese | 1 | a hipótese em destaque (o médico escolhe perto de onde trabalha; a bolsa muda qual vaga, mas pesa menos que a origem); em cinza, a motivação numa linha (no corte, não detectamos aumento do preenchimento); "formulada após ver os dados" na tela |
| Dados | 2 | uma tabela: 1ª opção, origem do médico (vínculo anterior no CNES), vagas e bolsa, IVS 2010, distância e UF; em cinza, porte e capital |
| Análise descritiva | 3–5 | os três ciclos em números (células, candidatos de 1ª opção, amostra com origem); a regra *sharp* bolsa × IVS, com "Como ler" na tela; onde os médicos escolhem (G-B: mesma UF, região, município; distância) |
| Metodologia | 6 | o logit condicional da 1ª opção em palavras: a equação, a comparação (o candidato consigo mesmo) e o teste (origem × toda a bolsa); erro-padrão, efeito fixo do par de UFs e detalhes nas notas |
| Identificação | 7 | numa tabela: bolsa por regra (*sharp*); pacote do corte; IIA em parte; localização (par de UFs fixado); origem como preferência revelada; hipótese pós-resultado |
| Resultados | 8–9 | o teste central, origem × toda a bolsa (G-D, quadro do ciclo 2 de 13/02/2026); a bolsa dentro da mesma UF (G-C, adendo pós-resultado, com o Holm da especificação pré-registrada na tela) |
| Robustez | 10 | uma figura: razão de chances por ciclo, ciclo 2 com o quadro refeito (cinza), distância em log, região de saúde, só perto do corte; origem − bolsa por ciclo |
| Discussão | 11 | incentivo limitado em termos do modelo da banca 1: a teoria, o dado (a origem pesa mais que toda a bolsa) e a leitura (o custo de sair da própria região domina), separados (auditoria 53) |
| Apêndice | 12–13 | o fato da antiga H1 (G-A: sem controle, com efeito fixo de UF e o raio, numa amostra menor, e pareando na mesma UF, por corte); a antiga H3 numa frase |

Saíram do corpo, com o essencial nas notas ou no apêndice: a H1 como hipótese (scatter, especificação, premissas,
resultado, robustezes e "por que o sinal sai negativo"), a H3 como plano B e os planos B em cinza.
