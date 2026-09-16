# Deck Beamer da banca 1 — tema Warsaw

> **Classificação:** artefato **derivado**<br>
> **Fonte de verdade do conteúdo:** [`../02_conteudo_slides.md`](../02_conteudo_slides.md)<br>
> **Regras de composição:** [`../01_roteiro_narrativo.md`](../01_roteiro_narrativo.md), seção 2<br>
> **Proveniência:** [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md)<br>
> **Atualização:** 16 de setembro de 2026

Regra do projeto: *divergência entre deck e documento de conteúdo é erro do
deck*. Nenhuma afirmação, número, citação ou referência deste `.tex` foi criada
aqui; tudo vem de `02_conteudo_slides.md`. Correção de conteúdo se faz primeiro
no documento canônico e só depois no deck.

**Tamanho:** 15 slides do documento, **15 frames**, **27 páginas de PDF**. As
doze páginas a mais são overlays: no rodapé o contador mostra `frame / 15`, e um
frame com overlay não muda de número — para a banca, é um slide só. Cada slide
do documento é exatamente um frame.

---

## 1. Como compilar

```bash
# sempre a partir da raiz do repositório
bash scripts/apresentacao/build_deck_beamer.sh
```

O script:

1. posiciona-se na raiz do repositório (todos os caminhos são relativos a ela);
2. confere que as quatro figuras existem antes de chamar o LaTeX;
3. roda `pdflatex` duas vezes (a segunda resolve a contagem total do rodapé),
   com `-halt-on-error`;
4. relata da última passada qualquer `Overfull \hbox` — texto vazando pela
   lateral — **e qualquer `Overfull \vbox`**, que é conteúdo estourando a altura
   do frame e invadindo o rodapé;
5. grava `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` e remove os
   auxiliares.

`SOURCE_DATE_EPOCH=1789516800` (16/09/2026, 00:00 UTC) e `FORCE_SOURCE_DATE`
são fixados no script, de modo que duas execuções sobre a mesma entrada
produzam byte a byte o mesmo PDF.

**Requisitos:** `pdflatex` com `beamer`, `beamerthemeWarsaw.sty`,
`texlive-latex-extra`, `texlive-fonts-recommended`, `lmodern` e
`texlive-lang-portuguese`.

**Figuras.** O deck lê apenas figuras já versionadas em
`output/apresentacao_banca1/`, por `\graphicspath` relativo à raiz:

| Código | Arquivo | Frame |
|---|---|:---:|
| `F3` | `bolsa_por_faixa.png` | 5, overlay 2 |
| `F1` | `oferta_pre_por_faixa.png` | 6, overlay 1 |
| `F2` | `retaguarda_por_faixa.png` | 6, overlay 2 |
| `F6` | `preenchimento_ciclo1.png` | 8 |

Nenhuma figura é gerada, editada ou recortada por este deck. `F4` (curva de
custo laboral) e `F5` (vagas por região) saíram do deck em 16/09/2026. Para
regerar as figuras, ver [`../README.md`](../README.md), seção 3.

---

## 2. Mapeamento: slide do documento → frame do deck

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

Também saíram as sombras das caixas de destaque (`shadow=true`). Os blocos
arredondados do tema interno `rounded` continuam.

### 3.2 Um slide, um frame

Desde o corte de 16/09/2026 o documento tem 15 slides e o deck tem 15 frames.
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

Todas as equações dos slides 10 a 14 do documento são reproduzidas em `amsmath`
como display, sem redução de corpo.

### 3.7 Vocabulário

Nenhuma palavra escrita fora do documento de conteúdo introduz econometria ou
estimação. As substituições da seção 2.5 do roteiro já vêm resolvidas do
documento e foram preservadas.

---

## 4. Ressalvas

Nenhuma aberta. As duas registradas na versão anterior — a figura `F4`
ilegível em projeção e a divergência entre "10 ambulatoriais" e a lista de oito
— foram encerradas no documento canônico em 16/09/2026: `F4` saiu do deck e a
enumeração de cursos foi substituída pela contagem conferida.

---

## 5. Verificação feita nesta versão

- `bash scripts/apresentacao/build_deck_beamer.sh` termina sem erro de LaTeX e
  sem nenhum `Overfull \hbox` **ou `\vbox`**. Os três `\vbox` da primeira
  compilação (frame 4 com quatro blocos numa tela; frame 7 nos dois overlays)
  foram resolvidos com um overlay a mais no frame 4 e espaçamento menor no 7.
- As 27 páginas foram convertidas em PNG (`pdftoppm -png -r 60`) e revistas em
  folha de contato: nenhuma com texto vazando do frame, tabela cortada, bloco de
  fonte sobreposto ao rodapé ou figura deformada.
- Os 15 slides do documento estão representados, na ordem, com os 13 títulos
  literais dos slides 3 a 15.
