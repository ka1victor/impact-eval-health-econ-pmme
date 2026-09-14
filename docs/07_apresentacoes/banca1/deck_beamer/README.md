# Deck Beamer da banca 1 — tema Warsaw

> **Classificação:** artefato **derivado**<br>
> **Fonte de verdade do conteúdo:** [`../02_conteudo_slides.md`](../02_conteudo_slides.md)<br>
> **Regras de composição:** [`../01_roteiro_narrativo.md`](../01_roteiro_narrativo.md), seção 2<br>
> **Proveniência:** [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md)<br>
> **Atualização:** 14 de setembro de 2026

Regra do projeto: *divergência entre deck e documento de conteúdo é erro do
deck*. Nenhuma afirmação, número, citação ou referência deste `.tex` foi criada
aqui; tudo vem de `02_conteudo_slides.md`. Correção de conteúdo se faz primeiro
no documento canônico e só depois no deck.

**Tamanho:** 18 slides do documento, **22 frames**, **29 páginas de PDF**. As
sete páginas a mais são segundos overlays: no rodapé o contador mostra
`frame / 22`, e um frame com overlay não muda de número — para a banca, é um
slide só.

---

## 1. Como compilar

```bash
# sempre a partir da raiz do repositório
bash scripts/apresentacao/build_deck_beamer.sh
```

O script:

1. posiciona-se na raiz do repositório (todos os caminhos são relativos a ela);
2. confere que as seis figuras existem antes de chamar o LaTeX;
3. roda `pdflatex` duas vezes (a segunda resolve a contagem total do rodapé),
   com `-halt-on-error`;
4. relata da última passada qualquer `Overfull \hbox` — texto vazando pela
   lateral — **e qualquer `Overfull \vbox`**, que é conteúdo estourando a altura
   do frame e invadindo o rodapé;
5. grava `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` e remove os
   auxiliares.

O relatório de `\vbox` foi acrescentado nesta versão: com o deck comprimido,
transbordo vertical passou a ser o modo de falha típico, e ele não aparece em
nenhum aviso de `\hbox`.

`SOURCE_DATE_EPOCH=1789344000` (14/09/2026, 00:00 UTC) e `FORCE_SOURCE_DATE`
são fixados no script, de modo que duas execuções sobre a mesma entrada
produzam byte a byte o mesmo PDF.

**Requisitos:** `pdflatex` com `beamer`, `beamerthemeWarsaw.sty`,
`texlive-latex-extra`, `texlive-fonts-recommended`, `lmodern` e
`texlive-lang-portuguese`.

**Figuras.** O deck lê apenas figuras já versionadas, por `\graphicspath`
relativo à raiz:

| Código | Arquivo | Frame |
|---|---|:---:|
| `F1` | `output/apresentacao_banca1/oferta_pre_por_faixa.png` | 4, overlay 1 |
| `F2` | `output/apresentacao_banca1/retaguarda_por_faixa.png` | 4, overlay 2 |
| `F5` | `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` | 8 |
| `F3` | `output/apresentacao_banca1/bolsa_por_faixa.png` | 10 |
| `F6` | `output/apresentacao_banca1/preenchimento_ciclo1.png` | 13 |
| `F4` | `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` | 19 |

Nenhuma figura é gerada, editada ou recortada por este deck. Para regerar as
cinco de `output/`, ver [`../README.md`](../README.md), seção 3.

---

## 2. Mapeamento: slide do documento → frames do deck

O rastreio de seção exibido é sempre o do slide de origem, literal; quando um
slide vira mais de um frame, todos repetem o mesmo rastreio e o mesmo título.

| Slide do documento | Frames | Páginas | O que ficou em cada frame |
|---|:---:|:---:|---|
| 1 — Capa | 1 | 1 | capa |
| 2 — Sumário | 2 | 2 | as seis seções, em duas colunas |
| 3 — Especialistas não faltam; faltam no interior | 3 | 3 | retrato nacional (353 mil, 55%/6%, 453/68/70), os 10% que atendem no SUS e a urgência em saúde pública de 24 meses |
| 4 — Onde a bolsa é maior, já havia menos especialistas | 4 | 4–5 | **overlay:** cada figura ocupa a largura inteira com a sua afirmação — `F1` "menos da metade", `F2` "e quem vai, vai sozinho" |
| 5 — O que o médico vê ao decidir | 5 | 6 | a tabela das quatro desvantagens e, abaixo, o peso de cada uma nas três evidências da literatura |
| 6 — O que é o PMM-E | 6–8 | 7–9 | **6** Lei, Quem e O quê. **7** os 16 cursos e como a vaga chega ao médico. **8** onde, no primeiro ciclo: os números ao lado da figura `F5` |
| 7 — A bolsa remunera o lugar | 9–10 | 10–11 | **9** os três passos (índice, categoria, valor). **10** tabela categoria–faixa–bolsa com a figura `F3` e a contagem 102/107/159, mais os dois cuidados |
| 8 — Pagar mais funciona: a evidência a favor | 11 | 12–13 | **overlay:** o experimento mexicano; depois a régua do prêmio compensatório, o degrau de +50% e a ressalva das 20 horas |
| 9 — Mas é caro, e não segura: a evidência contra | 12 | 14–15 | **overlay:** Austrália e Brasil; depois Estados Unidos e o fecho "dinheiro move alocação, mas…" |
| 10 — No primeiro ciclo, a bolsa maior não ordenou o preenchimento | 13 | 16 | os 30%, a figura `F6` e, em coluna ao lado, a leitura por faixa e por território e "descrição, não efeito" |
| 11 — Pergunta | 14 | 17 | a pergunta, os dois objetos e a margem observada |
| 12 — De onde vem o modelo | 15 | 18–19 | **overlay:** a estrutura da decisão (Moehling et al.); depois o custo geográfico (Redding & Rossi-Hansberg), o custo de trabalhar (Choné & Ma) e o que nenhuma das três trata |
| 13 — Como o médico escolhe onde trabalhar | 16 | 20 | a função-valor, a alternativa `m = 0` e o glossário termo a termo, **tudo na mesma tela** |
| 14 — O que a bolsa paga — e o que não paga | 17 | 21 | a decomposição `B + w^priv`, a tabela capital/interior, as duas consequências e o deflator |
| 15 — O custo de estar ali | 18–19 | 22–23 | **18** a equação com os dois blocos, a tabela de componentes e o papel duplo de `L` e `K`. **19** figura `F4` e o fecho |
| 16 — O IVS organiza o custo | 20 | 24–25 | **overlay:** `c = c₀(IVS) + η` e a correspondência dimensão–bloco; depois a ambiguidade do sinal e por que o objeto é o degrau |
| 17 — A hipótese | 21 | 26–27 | **overlay:** passos 1, 2 e 3 — a condição de aceitação, a passagem do médico à vaga e H1; depois o passo 4, o custo como obstáculo e a condição de degrau |
| 18 — Viabilidade empírica | 22 | 28–29 | **overlay:** a tabela peça a peça e as duas peças não observadas; depois a dificuldade e o primeiro passo |

---

## 3. Decisões de composição

### 3.1 Uma barra só, embaixo

O Warsaw original gasta duas faixas: a barra de navegação de seções no topo e
três caixas com autor, título e data no rodapé. As duas juntas comem cerca de
0,7 cm dos 9 cm de altura, e o título do trabalho repetido em todas as páginas
não diz nada a quem já leu a capa.

Nesta versão a `headline` foi esvaziada e o **rastreio de seção desceu para o
rodapé**, no lugar antes ocupado pelo título: faixa fina única, em verde muito
claro, com a linha de rastreio do slide à esquerda e `frame / total` à direita.
A faixa de `frametitle` do Warsaw — degradê e sombra, o que torna o tema
reconhecível — ficou, encostada no corpo por
`\addtobeamertemplate{frametitle}{}{\vspace*{-0.55em}}`.

O topo livre e a folga recuperada da faixa de título valem cerca de uma linha e
meia de texto em **todos** os 22 frames. É esse espaço que paga a compressão da
seção 3.4.

Também saíram as sombras das caixas de destaque (`shadow=true`), que eram o
ornamento mais barulhento sobrando depois da limpeza das barras. Os blocos
arredondados do tema interno `rounded` continuam.

### 3.2 O texto não repete o número que a figura já rotula

Regra aplicada em todo o deck: **quando a figura carrega o número rotulado, o
texto ao lado fica só com a afirmação**. A figura prova, a frase interpreta.

| Frame | Números que ficam só na figura | O que o texto diz |
|:---:|---|---|
| 4 | 16,0 / 10,0 / 7,3; 5 / 3 / 2 colegas; 15% / 34% / 42% | "menos da metade de especialistas por habitante onde a bolsa seria maior"; "encontraria menos colegas da sua especialidade" |
| 13 | 23,6% / 37,4% / 31,6%; 35,6% / 44,9% / 26,9% / 20,5% | "pagar o dobro não preencheu mais que pagar uma vez e meia"; "o preenchimento cai da capital e da região metropolitana para o interior ligado a um polo, e é menor no interior remoto" |

Os números continuam todos na tela, dentro da figura, com a mesma redação do
documento de conteúdo. O que desapareceu foi a segunda exibição do mesmo valor
em prosa, que obrigava a plateia a ler tudo duas vezes.

Números que a figura **não** rotula continuam em texto: 295 municípios (frame
4), 1.295 / 460 / 368 / 678 / 1.145 / 39% / 252 / 18 capitais (frame 8),
102 / 107 / 159 (frame 10), 30% das 1.295 vagas (frame 13).

### 3.3 Overlay em vez de frame novo

`\insertframenumber` conta **frames**, não páginas: em um frame com `\only`, os
dois overlays exibem o mesmo número no rodapé, sob o mesmo título e o mesmo
rastreio. Para quem assiste, é um slide que se completa — não um slide novo.

Isso resolve dois problemas de uma vez. O primeiro é o do slide 13 do
documento, em que o glossário explica **aquela** equação: nesta versão nem
overlay é preciso, porque a altura recuperada pela barra única fez equação,
nota e glossário caberem juntos no frame 16. O segundo é o dos blocos densos —
os frames 4, 11, 12, 15, 20, 21 e 22 — em que juntar tudo em uma tela estática
só caberia encolhendo a fonte até o ilegível ou cortando número e afirmação.
Nesses, o overlay entrega o conteúdo inteiro em corpo legível sem gastar um
slide a mais.

Overlay não custa tempo de fala além do que o conteúdo já custa; frame novo,
sim. Contra o orçamento de 28 minutos da seção 6 do roteiro, a diferença
importa.

### 3.4 O que foi comprimido, e como

A versão anterior tinha **36 frames** para 18 slides: vários slides apareciam
repartidos em três ou quatro frames de mesmo título dentro de uma só subseção.
Esta tem **22**.

Fundidos em um frame estático:

- **Slide 3** (2 → 1): saíram as duas manchetes de jornal em caixa, que apenas
  repetiam em outras palavras a frase sobre a urgência em saúde pública.
- **Slide 5** (2 → 1): a tabela das quatro desvantagens e o peso de cada uma na
  literatura, esta última reduzida de três marcadores longos a uma tira
  corrida.
- **Slide 7** (3 → 2): os dois cuidados desceram para o frame da tabela e da
  figura, em duas caixas lado a lado.
- **Slide 10** (2 → 1): a figura `F6` foi para uma coluna e a leitura por faixa
  e por território para a outra.
- **Slide 13** (1 frame com 2 overlays → 1 frame estático): equação, nota e
  glossário na mesma tela, sem clique.
- **Slide 14** (2 → 1): as duas consequências viraram caixas lado a lado em vez
  de blocos empilhados.
- **Slide 15** (3 → 2): o papel duplo de `L` e `K` desceu para o frame da
  equação e da tabela, como uma frase corrida.

Convertidos de dois frames para **um frame com dois overlays**: slides 4, 8, 9,
12, 16, 17 e 18.

Nenhuma afirmação e nenhum número do documento de conteúdo saíram. O que saiu
foi prosa de ligação, citação que ilustrava sem acrescentar fato, manchete
decorativa e vão morto. Os números foram conferidos um a um contra a versão
anterior do `.tex`.

### 3.5 Uma só legenda por figura, no formato do resto do deck

As cinco figuras geradas por script trazem, dentro do próprio PNG, uma linha de
proveniência em corpo minúsculo. O deck **não** acrescenta uma segunda legenda
centralizada: a fonte aparece uma única vez, no bloco `Fontes:` em negrito,
alinhado à esquerda, separado por filete fino — exatamente como nos frames de
texto. A linha interna do PNG é parte da figura e não pode ser alterada.

O mesmo vale para as citações: em todo o deck, referência bibliográfica vai no
bloco `Fontes:` do rodapé do frame. Nenhuma referência aparece solta em cinza
dentro do corpo.

### 3.6 Tabelas, figuras e matemática

As figuras que dividem frame com texto são limitadas pela **altura**, não pela
largura: o teto de altura de cada uma foi ajustado até o limite em que o bloco
`Fontes:` ainda cabe acima do rodapé. No frame 4 o overlay existe justamente
para que cada figura fique com a **largura inteira** do frame — lado a lado,
as duas caíam a menos de metade da largura e o eixo ficava ilegível.

Caixas de destaque mais estreitas que o bloco de texto são centradas via
`minipage` ou pelo ambiente `destaque`: `\centering` sozinho não centra um
`beamercolorbox` de largura fixa.

`booktabs` em todas as tabelas; `tabularx` quando alguma coluna quebra linha;
valores monetários à direita. Onde a tabela não cabia com folga, reduziu-se para
`\footnotesize` com `\arraystretch` menor, em vez de encolher a fonte até o
ilegível.

Todas as equações dos slides 12 a 17 do documento são reproduzidas em `amsmath`
como display, sem redução de corpo, inclusive a função-valor com o `\arg\max`
na mesma linha, como no documento.

### 3.7 Vocabulário

Nenhuma palavra escrita fora do documento de conteúdo introduz econometria ou
estimação. As substituições da seção 2.5 do roteiro já vêm resolvidas do
documento — "célula com alguma confirmação ou homologação", "presença cadastral
no CNES", "gradiente" — e foram preservadas.

---

## 4. Ressalvas registradas

### 4.1 `F4` — a figura do custo laboral é ilegível em projeção

A ilustração conceitual `docs/02_teoria/figuras/curva_custo_laboral_burnout.png`
tem 3.473 × 2.130 px e carrega uma legenda de cinco entradas mais quatro
anotações de zona, todas em corpo pequeno em relação à altura da imagem. No
frame 19 ela ocupa a largura inteira do frame; mesmo assim, **a legenda e as
anotações de zona ficam em torno de 5 pt na tela projetada** e não são legíveis
do fundo da sala. As três curvas e os dois pontos de inflexão continuam
legíveis.

O deck não regera, não recorta e não edita a figura — regra de proveniência do
projeto. **A decisão sobre regerar `F4` com tipografia maior é do autor**, e
teria de ser feita no script que a produz, não aqui.

### 4.2 Divergência herdada no número de cursos ambulatoriais

O slide 6 de `02_conteudo_slides.md` anuncia **10 cursos ambulatoriais** e
enumera oito itens entre parênteses. O deck transcreve a lista como está, por
fidelidade. A correção, se houver, é no documento canônico.

---

## 5. Verificação feita nesta versão

- `bash scripts/apresentacao/build_deck_beamer.sh` termina sem erro de LaTeX e
  sem nenhum `Overfull \hbox` **ou `\vbox`** — nenhum frame estoura a altura.
- Duas execuções seguidas produzem o mesmo PDF, byte a byte
  (`sha256 = 6fb557a2…`).
- As 29 páginas foram convertidas em PNG (`pdftoppm -png -r 90`) e revistas uma
  a uma: nenhuma tem texto vazando do frame, tabela cortada, bloco de fonte
  sobreposto ao rodapé, figura deformada, legenda duplicada ou caixa de destaque
  fora de eixo; nenhuma ficou com menos de dois terços da altura ocupada.
- Todo número exibido na versão anterior do `.tex` foi reconferido no novo, um a
  um: nenhum se perdeu na compressão.
- Os 18 slides do documento estão representados, na ordem, com os 16 títulos
  literais dos slides 3 a 18 — o do slide 17 agora é **A hipótese**.
