# Estrutura obrigatória da versão final da apresentação da banca 2

> **Decisão do autor, 26/10/2026.** Vale para toda versão futura do deck da banca
> 2. **Só a versão curta é usada.** As versões longas não serão usadas e não
> precisam mais ser geradas; o deck completo fica só como registro. Um deck que fuja desta estrutura
> está errado e deve ser corrigido no gerador
> (`scripts/apresentacao/gerar_deck_banca2.py`), não à mão.<br>
> **Estatuto:** regra de apresentação. Não muda protocolo nem resultado.

> [!NOTE]
> **Numeração da apresentação a partir de 26/10/2026:** H1 preenchimento; H2
> bolsa × origem (antes H3); H3 oferta (antes H4). A H2 antiga (escolha por
> ciclo) saiu como hipótese própria e virou especificação secundária da H2. Os
> nomes dos documentos de análise (P1h, P4, protocolos) e dos códigos do
> registro de números não mudam.

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
  obrigatória continua na tela, curta.

## 3. Como o conteúdo atual se encaixa (versão de 26/10/2026, a validar)

Numeração nova (H1 preenchimento; H2 bolsa × origem; H3 oferta). O conteúdo
canônico está em [`04_conteudo_deck_curto.md`](04_conteudo_deck_curto.md).

| Seção | Conteúdo |
|---|---|
| Hipótese | candidata central, em destaque: H2 (a bolsa pesa pouco perto da origem do médico, "incentivo limitado"; antes H3). Em cinza, como plano B: H1 (preenchimento) e H3 (oferta; antes H4). A escolha final é do autor, depois da validação dos professores |
| Dados | variáveis principais e secundárias, com fonte e unidade (detalhe de período e cobertura nas notas) |
| Análise descritiva | os três ciclos em números; IVS × faixa; 1ª opção em relação à origem; dados crus em volta dos cortes (scatter IVS × preenchimento com as retas); subida do preenchimento dentro das faixas (doc 57m, em auditoria) |
| Metodologia | especificação de cada estimador em até 4 linhas: H1 do adendo 48b (só vagas imediatas), logit da H2, estudo de evento da H3 |
| Identificação | regra *sharp*, densidade, balanço e placebos; pacote do corte (auditorias 18 e 35); tendências paralelas da H3 |
| Resultados | H1 principal do adendo 48b (HI-1 e HI-2 por corte; "aguardando 48b" até as saídas existirem); H2 (P1h); H3 (P4) |
| Robustez | H1 nas medidas antigas (A3, N1); antes e depois do controle; H1 por ciclo; o passo a passo da queda em 0,300 (estimativa no corte, vagas diferentes, o que dá para afirmar); H2 por ciclo e nas variantes do logit; H3 na nota de corte e Rambachan–Roth |
| Discussão | o sinal negativo da H1 em uma linha simples; incentivo limitado, escolha × preenchimento e substituição |
