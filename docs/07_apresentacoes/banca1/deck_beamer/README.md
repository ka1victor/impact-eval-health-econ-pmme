# Deck Beamer da banca 1 — tema PMME (identidade Insper)

> **Classificação:** artefato **derivado**<br>
> **Fonte de verdade do conteúdo:** [`../02_conteudo_slides.md`](../02_conteudo_slides.md)<br>
> **Regras de composição:** [`../01_roteiro_narrativo.md`](../01_roteiro_narrativo.md), seção 2<br>
> **Proveniência:** [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md)<br>
> **Atualização:** 19 de setembro de 2026 — frames reconstruídos na estrutura vigente de **17 slides em 3 seções** (revisão de 17/09), sobre a identidade institucional do Insper

Regra do projeto: *divergência entre deck e documento de conteúdo é erro do
deck*. Nenhuma afirmação, número, citação ou referência deste `.tex` foi criada
aqui; tudo vem de `02_conteudo_slides.md`. Correção de conteúdo se faz primeiro
no documento canônico e só depois no deck.

**Tamanho:** 17 slides do documento, **17 frames**, **32 páginas de PDF**. As
quinze páginas a mais são **builds**: cada `###` do documento é um `\only<n>`
do mesmo frame, com o mesmo título, o mesmo rastreio e o mesmo número no
rodapé — para a banca, um slide que se completa, não um slide novo. São 32
builds em 17 slides, exatamente os do "Mapa da apresentação" do documento.

---

## 1. Como compilar

```bash
# sempre a partir da raiz do repositório
bash scripts/apresentacao/build_deck_beamer.sh
```

O script:

1. posiciona-se na raiz do repositório (todos os caminhos são relativos a ela);
2. confere que as oito figuras existem antes de chamar o LaTeX;
3. roda **`lualatex`** duas vezes (a segunda resolve a contagem total do
   rodapé e as posições da capa e do sumário), com `-halt-on-error`;
4. relata da última passada qualquer `Overfull \hbox` — texto vazando pela
   lateral — **e qualquer `Overfull \vbox`**, que é conteúdo estourando a altura
   do frame e invadindo o rodapé;
5. grava `output/apresentacao_banca1/deck_beamer/banca1_beamer.pdf` e remove os
   auxiliares.

`SOURCE_DATE_EPOCH=1789516800` (16/09/2026, 00:00 UTC) e `FORCE_SOURCE_DATE`
são fixados no script, de modo que duas execuções sobre a mesma entrada
produzam byte a byte o mesmo PDF.

**Requisitos:** **`lualatex`** (`texlive-luatex`) com `beamer`, `fontspec`,
`tikz` (`texlive-pictures`), `texlive-latex-extra`, `texlive-fonts-recommended`,
`lmodern`, `texlive-lang-portuguese` e `tex-gyre`. As fontes (Inter, Playfair
Display, Oswald) vêm com o repositório, em `fontes/`.

O deck também compila em `pdflatex` (mesmas 32 páginas, sem overfull, conferido
em 19/09/2026): o preâmbulo escolhe `inputenc`/`fontenc`/`lmodern` ou
`fontspec` conforme o motor, e o tema usa Latin Modern Sans no corpo, TeX Gyre Pagella
nos títulos e Heros Condensed na capa alternativa quando não há `fontspec`. O PDF oficial é o do LuaLaTeX.

O tema não precisa ser instalado: o script exporta `TEXINPUTS` para o diretório
do deck, onde moram os arquivos abaixo.

| Arquivo | O que é |
|---|---|
| `banca1_beamer.tex` | o deck: metadados, as três seções, as três divisórias e os treze frames de conteúdo |
| `beamerthemePMME.sty` | tema-base: paleta, fontes, barra de navegação, título de frame, rodapé, blocos e utilitários (`\fonte`, `\lead`, `\num`, `destaque`, `\pmmebuild`, `pmmeduas`/`pmmequatro`, `\pmmefundo`) |
| `pmmeinsper.sty` | capa institucional `\inspercapa` e divisória de seção `\pmmedivisoria`, em TikZ |
| `pmmecapa.sty` | capa **alternativa** `\pmmecapa`, no visual do banner do PMM-E |
| `pmmesumario.sty` | sumário em TikZ |
| `insper/` | logo e gráfico institucional do Insper, do tema oficial para Quarto (MIT) — ver [`insper/README.md`](insper/README.md) |
| `assets/` | logo, foto da capa e fundo do sumário; não versionados, com substituto desenhado — ver [`assets/README.md`](assets/README.md) |
| `fontes/` | Inter, Playfair Display e Oswald (OFL) — ver [`fontes/README.md`](fontes/README.md) |

**Figuras.** O deck lê apenas figuras já versionadas em
`output/apresentacao_banca1/`, por `\graphicspath` relativo à raiz:

| Código | Arquivo | Frame, build |
|---|---|:---:|
| `E1` | `especialistas_por_uf_extremos.png` | 4, build 1 |
| `E2` | `deslocamento_por_regiao.png` | 4, build 1 |
| `E3` | `dupla_pratica_cirurgioes.png` | 4, build 2 |
| `F3` | `bolsa_por_faixa.png` | 5, build 1 |
| `F1` | `oferta_pre_por_faixa.png` | 5, build 3 |
| `F2` | `retaguarda_por_faixa.png` | 5, build 3 |
| `F6` | `preenchimento_ciclo1.png` | 7, build 1 |
| `F7` | `oferta_total_mensal.png` | 7, build 1 |

Os códigos são os de [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md),
seção 1. As oito são as figuras do documento canônico, nos mesmos slides.

Nenhuma figura é gerada, editada ou recortada por este deck. `F4` (curva de
custo laboral) e `F5` (vagas por região) saíram do deck em 16/09/2026 e
continuam fora. Para
regerar as figuras, ver [`../README.md`](../README.md), seção 3.

---

## 2. Mapeamento: slide do documento → frame do deck

Um slide do documento é um frame; um `###` do documento é um build (`\only<n>`)
do mesmo frame, aberto pelo título do build em Playfair com traço vermelho
(`\pmmebuild`). Os títulos de frame são os títulos de tela do documento,
literais; o rastreio do rodapé é a linha em código sob cada cabeçalho, literal.
Os slides de layout de capa (`#`) são a capa institucional e as três
divisórias `\pmmedivisoria`, com o número da seção.

| Slide = frame | Layout | Título | Páginas | Builds |
|:---:|:---:|---|:---:|---|
| 1 | capa | *Capa* | 1 | — |
| 2 | conteúdo | *Sumário* | 2 | as três seções, com o subtítulo da divisória como descrição |
| 3 | capa | **1. Motivação e Pergunta** | 3 | — |
| 4 | conteúdo | O especialista está longe do interior — e quase nunca é só do SUS | 4–6 | **1** onde eles estão: `E1` e `E2` lado a lado. **2** de quem é o tempo: `E3`. **3** quais faltam |
| 5 | conteúdo | A bolsa é do município, não do médico nem da especialidade | 7–9 | **1** o que o programa oferece: `F3` e o pacote igual em toda vaga. **2** quem fixa o valor: as duas cláusulas. **3** para onde a regra manda o dinheiro: `F1` e `F2` |
| 6 | conteúdo | Quanto maior o IVS, mais difícil é exercer ali | 10–11 | **1** o que o índice mede. **2** as três dimensões |
| 7 | conteúdo | O programa já deu sinais; a literatura aponta para os dois lados | 12–14 | **1** o ciclo 1: `F6`. **2** a leitura. **3** a literatura, dois de cada lado, em `pmmeduas` |
| 8 | conteúdo | A pergunta que organiza o trabalho | 15–16 | **1** a cadeia que a política supõe, em TikZ. **2** a pergunta |
| 9 | capa | **2. Literatura Teórica e Modelo Microeconômico** | 17 | — |
| 10 | conteúdo | Três tradições sustentam uma equação | 18 | tela única: a tabela das três tradições com as equações originais |
| 11 | conteúdo | A escolha locacional maximiza a renda real líquida | 19–20 | **1** a equação de escolha e os termos. **2** interpretação |
| 12 | conteúdo | O custo da localidade tem duas metades: o lugar e o trabalho | 21–23 | **1** o lugar. **2** o trabalho. **3** as três desvantagens |
| 13 | conteúdo | A bolsa é o piso da remuneração, não o total | 24–25 | **1** a remuneração total. **2** interpretação |
| 14 | capa | **3. Hipótese e Viabilidade Empírica** | 26 | — |
| 15 | conteúdo | No PMM-E, a regra fixa a remuneração e o IVS organiza o custo | 27–29 | **1** o modelo integrado. **2** a condição de aceitação. **3** na fronteira entre faixas |
| 16 | conteúdo | Mais remuneração real, mais vagas preenchidas | 30 | tela única: H1 sozinha |
| 17 | conteúdo | Há dado para quase todo termo — e sabemos quais faltam | 31–32 | **1** o que observamos. **2** o que falta |

---

## 3. Decisões de composição

### 3.1 Identidade visual: institucional Insper, com o PMM-E como acento

Até 16/09/2026 o deck usava o tema Warsaw repintado de verde; em 16/09 ganhou
o tema próprio **PMME**, no visual do banner do Projeto Mais Médicos
Especialistas; em **19/09/2026**, a pedido do autor, a base passou a ser a
identidade **institucional do Insper**, reproduzida do tema oficial para
Quarto/reveal.js ([padsInsper/quarto-insper-theme](https://github.com/padsInsper/quarto-insper-theme)):
página branca, texto preto, serifa de exibição nos títulos, vermelho como
acento e o gráfico institucional na capa. A paleta do PMM-E ficou como acento
e na capa alternativa.

**Paleta.** Tons do Insper amostrados do `insper.scss` e do `insper-bg.png` do
tema oficial; tons do PMM-E amostrados do banner do programa.

| Nome no tema | Hex | Onde aparece |
|---|---|---|
| `insperPreto` | `#1D1D1B` | texto, títulos, navbar (linha 1), blocos, `\lead`, `destaque` |
| `insperVermelho` | `#E50505` | losangos da navbar e do sumário, barra do título, filete do rodapé, número da divisória, `\num`, blocos *alert* |
| `insperVerde` | `#3ACC9F` | blocos *example* |
| `insperListra` / `insperCreme` | `#7F8F85` / `#F2E8DC` | listras do gráfico institucional (sumário, divisória, reservas) |
| `insperCinza` / `insperCinzaClaro` / `insperCinzaFundo` | `#6B6B6B` / `#E6E6E6` / `#F5F5F5` | texto secundário, filetes, fundo de blocos |
| `pmmeAzul`, `pmmeAmarelo`, `pmmeAmareloFaixa`, `pmmeVerde`, `pmmeVermelho` | `#0D28A9`, `#EDB601`, `#F1BB00`, `#00B300`, `#C40000` | capa alternativa `\pmmecapa` e acentos do PMM-E |

Para trocar um tom, edite só o `\definecolor` correspondente em
`beamerthemePMME.sty`; capa, sumário e divisória herdam.

**Fontes.** Como no tema oficial: **Inter** no corpo, navbar e rodapé;
**Playfair Display** (`\pmmeDisplay`) nos títulos de frame, capa, sumário,
divisórias e títulos de `pmmeparte` — substitui a GT Ultra Fine do tema
oficial, que é comercial e não pode ser redistribuída; **Oswald**
(`\pmmeCondensada`) só na capa alternativa do PMM-E. Todas OFL, em `fontes/`.
Com a Inter, mais larga que a Latin Modern, o deck passou de 11pt para
**10pt**: na tela ocupa o mesmo, e os frames compostos continuam cabendo.

**Capa (`\inspercapa`).** Como o slide de título do tema oficial: rótulo
pequeno e traço vermelho, título em Playfair preta à esquerda, subtítulo em
cinza, e abaixo os slots de **autoria**, **orientação**, instituição e data; à
direita, o gráfico institucional (wordmark *Insper*, quadrados preto e vermelho
sobre listras). Sem o `insper-bg.png`, o gráfico é desenhado em TikZ. A capa no
visual do banner do PMM-E continua disponível como `\pmmecapa`.

**Divisória de seção (`\pmmedivisoria{Título}{Subtítulo}`).** Página branca,
número da seção grande em vermelho, título em Playfair, subtítulo em cinza;
à direita, arcos de listras (o motivo do gráfico institucional, em curva) e
um filete vermelho vertical. É o layout de capa (`#`) do documento canônico:
os frames 3, 9 e 14. O título e o subtítulo são os do documento, literais.

**Sumário.** Página branca, título em Playfair com traço vermelho, as três
seções à direita e, em cada linha, a descrição curta em cinza — o subtítulo da
divisória correspondente —, um filete e o losango vermelho numerado; no canto
inferior esquerdo, arcos de listras. `\pmmesumariopasso{1.6}` abre o passo
vertical para três itens (o padrão, 1,10 cm, foi pensado para seis).
`\pmmesumario[k]` destaca a seção `k` e esmaece as demais; o deck usa a forma
sem argumento, porque o sumário aparece uma vez.

**Barra de navegação, no topo.** Duas faixas finas, **0,60 cm somadas**, em
Inter miúda: em cima, fundo preto com as seções numeradas, a corrente em
branco negrito precedida de um losango vermelho e as demais a meio-tom;
embaixo, fundo cinza-claro com as subseções da seção corrente, a atual em
preto negrito com losango. A segunda faixa **mantém a altura mesmo vazia**,
para que o título do frame não mude de posição entre seções com e sem
subseções.

**Título do frame e rodapé.** O título é Playfair preta sobre branco, com uma
barra vermelha curta à esquerda e um filete cinza abaixo. O rodapé tem um
filete cinza acima, o rastreio à esquerda, `frame / total` e o **logo do
Insper** à direita, e um filete vermelho de 1,2 pt na borda inferior da
página — o acento do tema oficial.

**Imagem de fundo em um frame.** `\pmmefundo[opacidade]{arquivo}` antes do
`\begin{frame}` cobre a página inteira com a imagem, recortada e centrada,
esmaecida (padrão 0,18) para o texto continuar legível; navbar, título e
rodapé ficam por cima. Vale até `\pmmesemfundo`, ou até o fim do grupo se
usado entre chaves. Com opacidade 1 e frame `[plain]`, é uma página de foto
plena.

```latex
{\pmmefundo[0.15]{docs/07_apresentacoes/banca1/deck_beamer/assets/fundo.jpg}
\begin{frame}{Título} ... \end{frame}}
```

**Layouts em partes.** `pmmeduas` põe duas partes lado a lado; `pmmequatro`,
uma grade 2×2. Cada `pmmeparte{Título}` tem o título em Playfair, um traço
vermelho e o corpo; as partes alinham pelo topo. `pmmequatro` fixa a altura de
cada parte em 0,36 `\textheight` e usa `\small`; ambos aceitam `[altura]`
opcional.

```latex
\begin{pmmequatro}
  \begin{pmmeparte}{Implementação} ... \end{pmmeparte}
  \begin{pmmeparte}{Força de trabalho} ... \end{pmmeparte}
  \begin{pmmeparte}{Capacidade} ... \end{pmmeparte}
  \begin{pmmeparte}{Acesso} ... \end{pmmeparte}
\end{pmmequatro}
```

**Título de build (`\pmmebuild{Título}`).** O mesmo formato do título de
`pmmeparte` — Playfair negrito, traço vermelho —, no topo de cada `\only<n>`.
É a marca visual do `###` do documento; frames de tela única (10 e 16) não o
usam.

No deck da banca 1: as três divisórias são `\pmmedivisoria`; o frame 7, build
3, usa `pmmeduas` para os dois lados da literatura; nenhum frame usa
`\pmmefundo` nem `pmmequatro` — estão no tema, disponíveis.

### 3.2 Um slide, um frame; um `###`, um build

O documento tem 17 slides e o deck tem 17 frames, na mesma ordem e com os
mesmos títulos. Onde o documento tem `###`, o frame tem overlays:
`\insertframenumber` conta **frames**, não páginas, de modo que os builds
exibem o mesmo número no rodapé, sob o mesmo título e o mesmo rastreio. Para
quem assiste, é um slide que se completa — não um slide novo. Build não custa
tempo de fala além do que o conteúdo já custa; frame novo, sim.

Frames de tela única: 1, 2, 3, 9, 10, 14, 16. Com dois builds: 6, 8, 11, 13,
17. Com três: 4, 5, 7, 12, 15. Total: 32 builds, os do mapa do documento.

O corpo de um frame **não pode começar por `{`**: com `\begin{frame}{Título}`,
o Beamer toma o grupo seguinte como `framesubtitle` — a tabela some do corpo
e aparece, na fonte do título, colada a ele. Os frames de tela única começam
por um `\vspace`; os demais, por `\only<1>{...}`.

### 3.3 O texto não repete o número que a figura já rotula

Regra aplicada em todo o deck: **quando a figura carrega o número rotulado, o
texto ao lado fica só com a afirmação**. A figura prova, a frase interpreta.

| Frame, build | Números que ficam só na figura | O que o texto diz |
|:---:|---|---|
| 4, 1 | 453 / 244 / 70 / 68 por 100 mil; 276 km … 101 km | "a escassez é territorial — e onde há menos especialista o paciente anda mais" |
| 4, 2 | 72,4% / 19,9% / 7,7% e a cobertura de 1.544 cirurgiões | "o SUS não compra a carreira do especialista; compra uma fração dela" |
| 5, 1 | R$ 10 / 15 / 20 mil por faixa | o pacote igual em toda vaga; "o valor é a única coisa que varia" |
| 5, 3 | 15,0 / 14,4 / 18,3 por 100 mil | "por habitante, a bolsa maior não vai para onde falta mais" |
| 7, 1 | 23,6% / 37,4% / 31,6%; 44,9% / 35,6% / 26,9% / 20,5% | "das 1.295 células, 393 (30,3%) tiveram alguém confirmado ou homologado" |
| 7, 1 | 14,5 e 17,7 por 100 mil, rotulados nos extremos de `F7` | **exceção declarada:** o texto os repete, porque o documento canônico os enuncia no corpo do slide |

Números que a figura **não** rotula continuam em texto, como no documento: as
medianas 6,5 e 2,5 de colegas (frame 5, build 3), 1.295 / 368 / 678 (frame 5,
build 1), 177 dos 368 (frame 5, build 2), e as taxas 31,6% / 37,4% / 44,9% /
20,5% repetidas na leitura do frame 7, build 2, porque o documento as repete.

### 3.4 O que a reconstrução de 19/09/2026 mudou no deck

A versão anterior tinha 15 frames em 6 seções, duas estruturas atrás do
documento. Esta tem 17 frames em 3 seções, e segue a convenção de cabeçalhos
de 16/09/2026: `#` é capa ou divisória, `##` é frame, `###` é build.

- **Três divisórias** (`\pmmedivisoria`) no lugar das quatro repetições do
  sumário; o sumário aparece uma vez, com três itens.
- **Um build por `###`**, com título de build (`\pmmebuild`): 32 builds, como
  no documento. Nenhum conteúdo foi redistribuído entre slides pelo deck.
- **Sete figuras**, todas de `output/apresentacao_banca1/`, nos slides 4, 5 e
  7 — as três de 17/09/2026 (`E1`, `E2`, `E3`) entram pela primeira vez.
- **A cadeia da teoria da mudança** (slide 8) é TikZ: seis nós em `\tiny`,
  verde-cheio para o que está em ato oficial e laranja-tracejado para
  suposição, com as cores do diagrama canônico; `\resizebox` ajusta a cadeia
  à largura do texto.
- **Frames de tela única** exatamente onde o documento os tem: o 10 (as três
  tradições) e o 16 (a hipótese sozinha).
- Os círculos verde e amarelo da tabela do slide 17 (`🟢 direto`, `🟡 proxy`)
  são desenhados em TikZ, nas cores `pmmeVerde` e `pmmeAmarelo` da paleta do
  PMM-E.
- Saíram, porque saíram do documento: o slide do desafio metodológico, o bloco
  "o que fica de pé", a tabela capital/interior em caixas, os slides de
  hipótese em quatro passos.

Ajustes de composição para caber, sem mudar palavra: figuras limitadas pela
altura (0,27 a 0,46 `\textheight`); tabelas em `\footnotesize`, e em
`\scriptsize` nas mais densas (frames 10, 15 build 1 e 17 build 2); a tabela
das três tradições em duas colunas — trabalho e papel numa, equação na outra
—, porque em três as células quebravam em cinco linhas; entrelinha 0,92 nas
duas partes do frame 7, build 3; `\sum\nolimits` na equação do frame 15.

### 3.5 Uma só legenda por figura, no formato do resto do deck

As figuras geradas por script trazem, dentro do próprio PNG, uma linha de
proveniência em corpo minúsculo. O deck **não** acrescenta uma segunda legenda
centralizada: a fonte aparece uma única vez, no bloco `Fontes:` em negrito,
alinhado à esquerda, separado por filete fino — exatamente como nos frames de
texto. Referência bibliográfica vai sempre no bloco `Fontes:` do rodapé do
frame.

### 3.6 Tabelas, figuras e matemática

As figuras que dividem frame com texto são limitadas pela **altura**, não pela
largura. Onde o documento põe duas figuras no mesmo build (frame 4, build 1;
frame 5, build 3; frame 7, build 1 desde 20/09/2026), elas ficam lado a lado em
`columns`, com a mesma altura máxima. No frame 7 o par é a exceção: as duas são
largas o bastante para que, em meia largura, **a largura limite antes da
altura** — `preenchimento_ciclo1` fica em cerca de 0,32 `\textheight` e
`oferta_total_mensal` em 0,36, sob o teto de 0,42 —, de modo que o build usa
menos altura com duas figuras do que usava com uma.

Caixas de destaque mais estreitas que o bloco de texto são centradas pelo
ambiente `destaque` ou por `minipage`. `booktabs` em todas as tabelas;
`tabularx` quando alguma coluna quebra linha; valores monetários à direita.
Onde a tabela não cabia com folga, reduziu-se para `\footnotesize` com
`\arraystretch` menor.

Todas as equações em display do documento (slides 11 a 16) são reproduzidas em
`amsmath` como display, sem redução de corpo; as equações originais da tabela
do slide 10 são inline, em `\scriptsize`, como no documento (célula de tabela).
`\mathbf{B}_m` e `\mathbf{w}^{\text{priv}}` seguem em negrito na seção 3, como
o documento pede.

### 3.7 Vocabulário

Nenhuma palavra escrita fora do documento de conteúdo introduz econometria ou
estimação. As substituições da seção 2.5 do roteiro já vêm resolvidas do
documento e foram preservadas.

---

## 4. Ressalvas

Nenhuma ressalva própria do deck. A pendência 6 do documento canônico —
decks na estrutura de 15 slides — fecha para o Beamer com esta versão e
continua aberta para o Slidev. As pendências de conteúdo (1, 2, 5, 8, 9) são do
documento e aparecem na tela exatamente como ele as escreve: por exemplo, o
rodapé do frame 4 diz "REGIC 2018 (IBGE), a confirmar", e os frames 6, 15 e 17
afirmam que o custo cresce com o IVS, a simplificação declarada da pendência 9.

Slots da capa: o documento não traz orientação; `\orientacao{}` vazio suprime
a linha. A data (`\date{2026}`) não está no documento e é metadado do deck.

---

## 5. Verificação feita nesta versão

- `bash scripts/apresentacao/build_deck_beamer.sh` (LuaLaTeX) termina sem erro
  de LaTeX e sem nenhum `Overfull \hbox` **ou `\vbox`**; duas execuções
  seguidas produzem o mesmo SHA-256. O deck também compila em pdflatex, com
  32 páginas e sem overfull.
- As 32 páginas foram convertidas em PNG (`pdftoppm -png -r 75`) e revistas
  uma a uma: nenhuma com texto vazando do frame, tabela cortada, bloco de
  fontes sobreposto ao rodapé ou figura deformada. Conferidos em detalhe a
  capa, o sumário, as três divisórias, a cadeia do frame 8 e os builds mais
  densos (7.3, 10, 15.1, 17.2).
- Os 17 slides do documento estão representados, na ordem, com os 13 títulos
  literais dos slides de conteúdo, os 3 títulos e subtítulos das divisórias, os
  32 builds e os 12 rastreios literais.
- Nenhuma palavra do corpo dos slides foi criada pelo deck; as únicas
  inserções são as legendas "direto"/"proxy" ao lado dos círculos do frame 17,
  que traduzem os emojis do documento, e os rótulos "suposição" da cadeia, que
  o diagrama canônico já traz.
