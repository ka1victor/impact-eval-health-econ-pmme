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
  obrigatória continua na tela, curta;
- **no máximo 14 slides** (decisão do autor de 26/10/2026: "esses últimos
  decks tão muito grandes. pode deixar mais curtos mesmo, só com os
  principais slides, idealmente <15 slides"). Só os slides principais; o
  que for cortado vai para as notas do apresentador, não para um apêndice. O
  teto é aplicado pelo gerador e pelo teste.

## 3. Como o conteúdo atual se encaixa (versão de 26/10/2026, a validar)

Numeração nova (H1 preenchimento; H2 bolsa × origem; H3 oferta). O conteúdo
canônico está em [`04_conteudo_deck_curto.md`](04_conteudo_deck_curto.md).

14 slides (versão de 26/10/2026, depois do teto de 14):

| Seção | Slides | Conteúdo |
|---|---|---|
| Hipótese | 1 | candidata central, em destaque: **H1** (preenchimento). Em cinza, como plano B: H2 (a bolsa pesa pouco perto da origem do médico, "incentivo limitado"; antes H3) e H3 (oferta; antes H4). Decisão do autor de 26/10/2026; a escolha final vem depois da validação dos professores |
| Dados | 2 | uma tabela só: variáveis principais e, em cinza, as secundárias, com a fonte de cada uma (unidade, período e cobertura nas notas) |
| Análise descritiva | 3–5 | os três ciclos em números, com a explicação dos ciclos numa linha; IVS × faixa (regra *sharp*); scatter IVS × preenchimento só de vagas imediatas, com as retas de cada lado, por corte (a subida dentro das faixas, doc 57m, nas notas) |
| Metodologia | 6 | H1 do adendo 48b em até 4 linhas, com a equação em palavras no centro, h, kernel e erro-padrão; H2 (logit da 1ª opção) e H3 (estudo de evento) numa linha cinza cada |
| Identificação | 7 | da H1, numa tabela: regra *sharp*; sem manipulação e balanço, com a ressalva das capitais em 0,300 (auditoria 36); pacote do corte (auditoria 18); nenhum outro incentivo individual em 0,300 (auditoria 35); tipo de vaga decidido pelo MS, premissa não testada (doc 05, §2.12) |
| Resultados | 8 | H1 principal do adendo 48b (HI-1 e HI-2 por corte), "em auditoria", com o TOST numa linha |
| Robustez | 9–11 | H1: antes e depois do controle (com e sem controle em painéis separados); por ciclo; controlando a capital |
| Discussão | 12–14 | por que o sinal é negativo, uma frase por explicação; planos B em cinza num slide (H2 com um número por ciclo; H3 nos dois níveis, doc 05, §2.13); a teoria: incentivo limitado, pacote do corte, vínculo cadastrado não é presença |

Saíram do rascunho de 26 slides, com o essencial nas notas: a capa, a tabela
separada das secundárias, os dois slides da subida dentro das faixas, "H2 e
H3: como estimamos", o slide do pacote, os resultados e as robustezes de H2 e
H3 em slides próprios, a medida antiga contra só vagas imediatas, a reta em
0,300 e o TOST em slide próprio.

Dentro de cada seção, os slides da mesma hipótese ficam juntos, em sequência (H1, depois H2, depois H3); o título
leva a hipótese ("H1 · …"), e os de plano B levam "plano B", em cinza.
