# Deck Beamer da banca 1 — tema PMME

> [!WARNING]
> **O conteúdo deste deck está desatualizado em relação ao documento canônico.**
> Desde **16/09/2026**, [`../02_conteudo_slides.md`](../02_conteudo_slides.md)
> tem **17 slides em 3 seções** (revisão de 17/09), com divisórias de seção e
> convenção nova de cabeçalhos; os frames deste deck continuam na **estrutura
> anterior, de 15 slides em 6 seções**. A reconstrução ficou para depois, por
> decisão do autor.
>
> A divergência é **conhecida e datada** — é a pendência 6 do fim do documento
> de conteúdo — e não altera a regra do projeto: **o documento canônico vence**.
> Enquanto os dois não forem reconciliados, os números de slide, os títulos, as
> entradas do sumário (`\pmmesumarioitem`) e os mapeamentos deste README
> descrevem o **estado anterior**, não o que vai à tela. O **tema** (paleta,
> fontes, capa, sumário, navbar, fundo e layouts) está atual e independe da
> estrutura: a reconstrução é só de conteúdo dos frames.

> **Classificação:** artefato **derivado**<br>
> **Fonte de verdade do conteúdo:** [`../02_conteudo_slides.md`](../02_conteudo_slides.md)<br>
> **Regras de composição:** [`../01_roteiro_narrativo.md`](../01_roteiro_narrativo.md), seção 2<br>
> **Proveniência:** [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md)<br>
> **Atualização:** 16 de setembro de 2026 — identidade visual PMME (paleta e fonte da peça oficial, LuaLaTeX, fundo por frame, layouts em partes); deck ainda na estrutura de 15 slides

Regra do projeto: *divergência entre deck e documento de conteúdo é erro do
deck*. Nenhuma afirmação, número, citação ou referência deste `.tex` foi criada
aqui; tudo vem de `02_conteudo_slides.md`. Correção de conteúdo se faz primeiro
no documento canônico e só depois no deck.

**Tamanho, no estado anterior:** 15 slides do documento, **15 frames**,
**27 páginas de PDF**. As doze páginas a mais são overlays: no rodapé o contador
mostra `frame / 15`, e um frame com overlay não muda de número — para a banca, é
um slide só. Cada slide daquela versão do documento é exatamente um frame.

---

## 1. Como compilar

```bash
# sempre a partir da raiz do repositório
bash scripts/apresentacao/build_deck_beamer.sh
```

O script:

1. posiciona-se na raiz do repositório (todos os caminhos são relativos a ela);
2. confere que as quatro figuras existem antes de chamar o LaTeX;
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
`lmodern`, `texlive-lang-portuguese` e `tex-gyre`. A fonte de destaque
(Oswald) vem com o repositório, em `fontes/`.

O deck também compila em `pdflatex` (mesmas 27 páginas, sem overfull, conferido
em 16/09/2026): o preâmbulo escolhe `inputenc`/`fontenc`/`lmodern` ou
`fontspec` conforme o motor, e o tema usa TeX Gyre Heros Condensed como fonte de
destaque quando não há `fontspec`. O PDF oficial é o do LuaLaTeX.

O tema não precisa ser instalado: o script exporta `TEXINPUTS` para o diretório
do deck, onde moram os arquivos abaixo.

| Arquivo | O que é |
|---|---|
| `banca1_beamer.tex` | o deck: metadados, seções e os quinze frames |
| `beamerthemePMME.sty` | tema-base: paleta, fontes, barra de navegação, título de frame, rodapé, blocos e utilitários (`\fonte`, `\lead`, `\num`, `destaque`) |
| `pmmecapa.sty` | capa em TikZ |
| `pmmesumario.sty` | sumário em TikZ |
| `assets/` | logo, foto da capa e fundo do sumário; não versionados, com substituto desenhado — ver [`assets/README.md`](assets/README.md) |
| `fontes/` | a família Oswald (OFL), fonte de destaque da identidade — ver [`fontes/README.md`](fontes/README.md) |

**Figuras.** O deck lê apenas figuras já versionadas em
`output/apresentacao_banca1/`, por `\graphicspath` relativo à raiz:

| Código | Arquivo | Frame (estado anterior) |
|---|---|:---:|
| `F3` | `bolsa_por_faixa.png` | 5, overlay 2 |
| `F1` | `oferta_pre_por_faixa.png` | 6, overlay 1 |
| `F2` | `retaguarda_por_faixa.png` | 6, overlay 2 |
| `F6` | `preenchimento_ciclo1.png` | 8 |

Os quatro arquivos continuam em uso, mas **mudaram de slide** no documento
canônico: `F3`, `F1` e `F2` estão hoje no slide 5 e `F6` no slide 6. Os números
de frame acima são os do deck atual, ainda na estrutura anterior.

Nenhuma figura é gerada, editada ou recortada por este deck. `F4` (curva de
custo laboral) e `F5` (vagas por região) saíram do deck em 16/09/2026. Para
regerar as figuras, ver [`../README.md`](../README.md), seção 3.

---

## 2. Mapeamento: slide do documento → frame do deck (estado anterior, 15 slides)

> [!NOTE]
> A tabela abaixo descreve o deck **como ele está**: mapeia os **15 slides da
> estrutura anterior** do documento de conteúdo. As colunas "Slide = frame" e
> "Título" **não correspondem** ao documento canônico vigente, de 16 slides em 3
> seções. Serve para operar e revisar o PDF existente e como ponto de partida da
> reconstrução, não como descrição do que vai à tela.

O rastreio de seção exibido é sempre o do slide de origem, literal. Um slide é
um frame; quando o conteúdo pede mais de uma tela, o frame usa overlays com o
mesmo título e o mesmo número.

| Slide = frame | Título | Páginas | O que ficou em cada overlay |
|:---:|---|:---:|---|
| 1 | *Capa* | 1 | — |
| 2 | *Sumário* | 2 | as seis seções, em duas colunas |
| 3 | Especialistas faltam no interior, e o médico sabe por quê | 3–4 | **1** retrato nacional e a tabela das quatro desvantagens. **2** o peso de cada uma na literatura e o fecho: urgência em saúde pública e o PMM-E |
| 4 | O que é o PMM-E | 5–6 | **1** Lei, Quem e O quê (com a contagem de 16 cursos). **2** onde, no ciclo 1, e a faixa de bolsa em cada vaga |
| 5 | A bolsa remunera o lugar | 7–8 | **1** os três passos (índice, categoria, valor). **2** tabela categoria–faixa–bolsa com `F3`, 102/107/159, as duas cláusulas e a divergência unidirecional |
| 6 | Onde a bolsa é maior, o médico fica sozinho | 9–10 | **1** `F1`, "por habitante, a bolsa maior não vai para onde falta mais". **2** `F2`, "em número de colegas, vai" |
| 7 | A evidência não decide se R$ 5 mil bastam | 11–12 | **1** a favor e contra lado a lado: México e o degrau de +50%; Austrália e Brasil. **2** Estados Unidos, a ressalva das 20 horas e o fecho |
| 8 | No primeiro ciclo, a bolsa maior não ordenou o preenchimento | 13 | os 30%, `F6` e, ao lado, a leitura por faixa e por território e "descrição, não efeito" |
| 9 | Pergunta | 14 | a pergunta, os dois objetos e a margem observada |
| 10 | A decisão: onde vale a pena estar | 15 | Moehling et al.: equação, glossário e a caixa-preta |
| 11 | Abrindo o custo: o lugar e o trabalho | 16–17 | **1** Redding & Rossi-Hansberg, o bloco geográfico e a limitação de residência. **2** Choné & Ma, o U e o papel duplo de `L` e `K` |
| 12 | Como juntamos os três | 18–19 | **1** a função-valor, a abertura de `c` e a tabela de origem. **2** a decisão e o que nenhuma das três tem |
| 13 | O IVS organiza o custo | 20–22 | **1** `w = B + w^priv`, capital contra interior e o deflator. **2** `c = c₀(IVS) + η` e a correspondência dimensão–bloco. **3** a ambiguidade do sinal e por que o objeto é o degrau |
| 14 | A hipótese | 23–24 | **1** passos 1 a 3 — condição de aceitação, do médico à vaga, H1. **2** passo 4, o custo como obstáculo e a condição de degrau |
| 15 | Viabilidade empírica | 25–27 | **1** a tabela peça a peça e "sim, para o essencial". **2** o enquadramento — é sobre o efeito da bolsa — e os três resultados da reconstrução da regra. **3** a conclusão de viabilidade e "o que fica de pé" |

---

## 3. Decisões de composição

### 3.1 Identidade visual própria, no lugar do Warsaw

Até 16/09/2026 o deck usava o tema Warsaw repintado de verde. Agora usa o tema
**PMME**, que reproduz a identidade da peça oficial do Projeto Mais Médicos
Especialistas.

**Paleta.** Amostrada pixel a pixel do banner oficial (bloco azul, título
amarelo, chevrons e tira de quatro cores). Os quatro tons principais são
exatos; os azuis auxiliares são derivados do azul principal.

| Nome no tema | Hex | Origem | Onde aparece |
|---|---|---|---|
| `pmmeAzul` | `#0D28A9` | bloco azul do banner | capa, sumário, navbar (linha 2), estrutura, `\num` |
| `pmmeAmarelo` | `#EDB601` | título do banner | título da capa, chevrons, barra do frametitle, losangos |
| `pmmeAmareloFaixa` | `#F1BB00` | tira inferior do banner | tira de quatro cores (capa e rodapé) |
| `pmmeVerde` | `#00B300` | tira inferior | blocos *example*, tira |
| `pmmeVermelho` | `#C40000` | tira inferior e filete da diagonal | blocos *alert*, filete da capa, tira |
| `pmmeAzulEscuro` | `#081A72` | derivado | navbar (linha 1), `\lead` |
| `pmmeAzulClaro` / `pmmeAzulPalido` | `#E4E8F7` / `#F2F4FB` | derivados | filetes, anel do sumário, fundo de blocos e rodapé |

Para trocar um tom, edite só o `\definecolor` correspondente em
`beamerthemePMME.sty`; capa e sumário herdam.

**Fonte de destaque.** Títulos, capa, sumário e barra de navegação são
compostos em **Oswald** (LuaLaTeX, arquivos em `fontes/`), a grotesca
condensada que corresponde ao título da peça oficial; em pdflatex, TeX Gyre
Heros Condensed. **O corpo do texto continua em Latin Modern Sans**, de
propósito — trocar a fonte do corpo mudaria as quebras de linha de todos os
frames e, com elas, a paginação já verificada. A troca de motor foi conferida:
nenhuma quebra de linha do corpo mudou entre o PDF do pdflatex e o do LuaLaTeX.

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
uma grade 2×2. Cada `pmmeparte{Título}` tem o título na fonte de destaque, um
traço amarelo e o corpo; as partes alinham pelo topo. `pmmequatro` fixa a
altura de cada parte em 0,36 `\textheight` e usa `\small`; ambos aceitam
`[altura]` opcional.

```latex
\begin{pmmequatro}
  \begin{pmmeparte}{Implementação} ... \end{pmmeparte}
  \begin{pmmeparte}{Força de trabalho} ... \end{pmmeparte}
  \begin{pmmeparte}{Capacidade} ... \end{pmmeparte}
  \begin{pmmeparte}{Acesso} ... \end{pmmeparte}
\end{pmmequatro}
```

Nenhum frame da banca 1 usa fundo ou layout em partes: o conteúdo canônico não
os pede. Estão no tema para os próximos decks.

**Capa.** Bloco azul na metade esquerda com a borda direita em diagonal,
filetes amarelo e vermelho correndo ao longo dela, chevrons amarelo sobre verde
junto ao rótulo, título em amarelo condensado e, abaixo do subtítulo, os slots
de **autoria** e de **orientação**. A faixa branca inferior traz o logo do
Insper à esquerda, instituição e data à direita, e a tira de quatro cores nas
proporções do banner (vão branco à esquerda; amarelo, vermelho, verde, azul;
margem branca abaixo). A foto ocupa a metade direita, recortada. Sem os arquivos de imagem, o
logo vira a palavra *Insper* composta e a foto vira um painel com chevrons.

**Sumário.** Página inteira em azul, com um anel claro semitransparente à
esquerda, as seis seções à direita e, em cada linha, a descrição curta, um
filete e o losango numerado. `\pmmesumario[k]` destaca a seção `k` e esmaece as
demais — útil se um dia quisermos repetir o sumário entre partes.

**Barra de navegação, no topo.** Duas faixas finas, **0,60 cm somadas**: em
cima, fundo azul-escuro com as seis seções numeradas, a corrente em branco
negrito precedida de um losango amarelo e as demais a meio-tom; embaixo, fundo
azul com as subseções da seção corrente. A segunda faixa **mantém a altura
mesmo vazia**, para que o título do frame não mude de posição entre seções com
e sem subseções. As seções e subseções do `.tex` foram derivadas do rastreio de
cada slide, que continua literal.

**Título do frame e rodapé.** O título é azul sobre branco, com uma barra
amarela curta à esquerda e um filete claro abaixo — sem o degradê e a sombra do
Warsaw. O rodapé continua sendo uma faixa fina com o rastreio à esquerda e
`frame / total` à direita, agora com a tira de quatro cores na borda inferior
da página.

A barra de navegação custa altura que antes era do corpo. O único frame que
não coube foi o 7, resolvido com espaçamento menor: entrelinha a 0,95 nos dois
blocos e recuo de 1 em antes das colunas. As maiúsculas da Oswald são mais
altas que as da Heros; os struts e os `\vskip` do frametitle foram
recalibrados para ela (cinco frames densos estouravam por 1–3 pt) e o frame 10
perdeu 0,1 em antes da nota final. Nenhuma palavra mudou.

### 3.2 Um slide, um frame

Na estrutura anterior, à qual este deck corresponde, o documento tinha 15
slides e o deck tem 15 frames. A correspondência de um para um é a regra a
preservar quando o deck for reconstruído sobre os 16 slides atuais.

Onde o documento tem mais conteúdo do que cabe numa tela legível, o frame usa
overlays: `\insertframenumber` conta **frames**, não páginas, de modo que os
overlays exibem o mesmo número no rodapé, sob o mesmo título e o mesmo
rastreio. Para quem assiste, é um slide que se completa — não um slide novo.
Overlay não custa tempo de fala além do que o conteúdo já custa; frame novo,
sim.

Frames estáticos: 1, 2, 8, 9, 10. Com dois overlays: 3, 4, 5, 6, 7, 11, 12, 14.
Com três: 13 e 15.

### 3.3 O texto não repete o número que a figura já rotula

Regra aplicada em todo o deck: **quando a figura carrega o número rotulado, o
texto ao lado fica só com a afirmação**. A figura prova, a frase interpreta.

| Frame | Números que ficam só na figura | O que o texto diz |
|:---:|---|---|
| 6 | as taxas por 100 mil e as medianas de colegas por faixa publicada | "por habitante, a bolsa maior não vai para onde falta mais"; "em número de colegas, vai" |
| 8 | 23,6% / 37,4% / 31,6%; 35,6% / 44,9% / 26,9% / 20,5% | "pagar o dobro não preencheu mais que pagar uma vez e meia"; "menor no interior remoto" |

Números que a figura **não** rotula continuam em texto: 295 municípios (frame
6), 1.295 / 460 / 368 / 39% / 18 capitais (frame 4), 102 / 107 / 159 (frame 5),
30% das 1.295 vagas (frame 8).

### 3.4 O que o corte de 16/09/2026 mudou no deck

A versão anterior tinha 22 frames para 19 slides. Esta tem 15 para 15.

- **Frames 3 e 4 antigos** (retrato nacional; o que o médico vê) viraram o
  frame 3, com dois overlays.
- **Frame 5 antigo** (PMM-E, em três frames) virou o frame 4, com dois
  overlays: saíram a enumeração dos cursos, o fluxo em passos e a figura
  regional.
- **Frames 11 e 12 antigos** (a favor; contra) viraram o frame 7: os dois
  blocos ficam lado a lado no primeiro overlay.
- **Frames 16 e 17 antigos** (o lugar; o trabalho) viraram o frame 11, sem a
  figura `F4`.
- **Frames 19 e 20 antigos** (o que a bolsa paga; o IVS organiza o custo)
  viraram o frame 13, com três overlays; a tabela capital/interior virou duas
  caixas.
- **Frame 22 antigo** (viabilidade) ganhou um terceiro overlay para o
  enquadramento e "o que fica de pé".

Nenhum número do documento cortado ficou fora do deck.

### 3.5 Uma só legenda por figura, no formato do resto do deck

As figuras geradas por script trazem, dentro do próprio PNG, uma linha de
proveniência em corpo minúsculo. O deck **não** acrescenta uma segunda legenda
centralizada: a fonte aparece uma única vez, no bloco `Fontes:` em negrito,
alinhado à esquerda, separado por filete fino — exatamente como nos frames de
texto. Referência bibliográfica vai sempre no bloco `Fontes:` do rodapé do
frame.

### 3.6 Tabelas, figuras e matemática

As figuras que dividem frame com texto são limitadas pela **altura**, não pela
largura. No frame 6 o overlay existe justamente para que cada figura fique com
a **largura inteira** do frame.

Caixas de destaque mais estreitas que o bloco de texto são centradas pelo
ambiente `destaque` ou por `minipage`. `booktabs` em todas as tabelas;
`tabularx` quando alguma coluna quebra linha; valores monetários à direita.
Onde a tabela não cabia com folga, reduziu-se para `\footnotesize` com
`\arraystretch` menor.

Todas as equações dos slides 10 a 14 do documento (numeração anterior) são
reproduzidas em `amsmath` como display, sem redução de corpo.

### 3.7 Vocabulário

Nenhuma palavra escrita fora do documento de conteúdo introduz econometria ou
estimação. As substituições da seção 2.5 do roteiro já vêm resolvidas do
documento e foram preservadas.

---

## 4. Ressalvas

**Uma aberta:** a divergência com o documento canônico descrita no aviso do topo
— 15 frames em 6 seções contra 16 slides em 3 seções —, registrada como
pendência 6 no fim de [`../02_conteudo_slides.md`](../02_conteudo_slides.md).
Fecha com a reconstrução do deck sobre a estrutura vigente.

As duas ressalvas de conteúdo da versão anterior — a figura `F4` ilegível em
projeção e a divergência entre "10 ambulatoriais" e a lista de oito — foram
encerradas no documento canônico em 16/09/2026: `F4` saiu do deck e a enumeração
de cursos foi substituída pela contagem conferida.

---

## 5. Verificação feita nesta versão (estrutura de 15 slides)

- `bash scripts/apresentacao/build_deck_beamer.sh` (LuaLaTeX) termina sem erro
  de LaTeX e sem nenhum `Overfull \hbox` **ou `\vbox`**; duas execuções
  seguidas produzem o mesmo SHA-256. O deck também compila em pdflatex, com
  27 páginas e sem overfull.
- Quebras de linha do corpo comparadas página a página (`pdftotext`) entre o
  PDF em pdflatex e o PDF em LuaLaTeX: idênticas nas 27 páginas.
- As 27 páginas foram convertidas em PNG (`pdftoppm -png -r 70`) e revistas:
  nenhuma com texto vazando do frame, tabela cortada, bloco de fonte sobreposto
  ao rodapé ou figura deformada. Conferidos em detalhe a capa, o sumário, um
  frame de cada seção e as páginas de seção sem subseção, onde a segunda faixa
  da barra de navegação fica vazia sem deslocar o título.
- Os 15 slides do documento estão representados, na ordem, com os 13 títulos
  literais dos slides 3 a 15.
- Nada disso foi reverificado contra a estrutura vigente de 17 slides em 3
  seções: a reconstrução do conteúdo dos frames é a pendência registrada no
  aviso do topo.
