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

**Tamanho:** 18 slides do documento, **36 frames**, **37 páginas de PDF** — a
página a mais é o segundo overlay do frame 25, que não é um slide novo.

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
4. relata qualquer `Overfull \hbox` da última passada;
5. grava `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` e remove os
   auxiliares.

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
| `F1` | `output/apresentacao_banca1/oferta_pre_por_faixa.png` | 5 |
| `F2` | `output/apresentacao_banca1/retaguarda_por_faixa.png` | 6 |
| `F5` | `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` | 12 |
| `F3` | `output/apresentacao_banca1/bolsa_por_faixa.png` | 14 |
| `F6` | `output/apresentacao_banca1/preenchimento_ciclo1.png` | 20 |
| `F4` | `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` | 30 |

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
| 3 — Especialistas não faltam; faltam no interior | 3–4 | 3–4 | **3** retrato nacional: 353 mil, 55%/6%, 453/68/70, citação do Senado. **4** urgência em saúde pública e as duas manchetes |
| 4 — Onde a bolsa é maior, já havia menos especialistas | 5–6 | 5–6 | **5** figura `F1` com a afirmação "menos da metade". **6** figura `F2` com a afirmação "e quem vai, vai sozinho" |
| 5 — O que o médico vê ao decidir | 7–8 | 7–8 | **7** tabela das quatro desvantagens e do que se mede. **8** as três evidências da literatura sobre o peso de cada uma |
| 6 — O que é o PMM-E | 9–12 | 9–12 | **9** Lei e Quem. **10** O quê: aprimoramento em serviço e os 16 cursos. **11** como a vaga chega ao médico. **12** onde, no primeiro ciclo: os números ao lado da figura `F5` |
| 7 — A bolsa remunera o lugar | 13–15 | 13–15 | **13** os três passos (índice, categoria, valor). **14** tabela categoria–faixa–bolsa ao lado da figura `F3`, com a contagem 102/107/159. **15** os dois cuidados |
| 8 — Pagar mais funciona: a evidência a favor | 16–17 | 16–17 | **16** o experimento mexicano. **17** a régua do prêmio compensatório, o degrau de +50% e a ressalva das 20 horas |
| 9 — Mas é caro, e não segura: a evidência contra | 18–19 | 18–19 | **18** Austrália e Brasil. **19** Estados Unidos e o fecho "dinheiro move alocação, mas…" |
| 10 — No primeiro ciclo, a bolsa maior não ordenou o preenchimento | 20–21 | 20–21 | **20** os 30% e a figura `F6`. **21** a leitura por faixa e por território, sem repetir os números da figura, e "descrição, não efeito" |
| 11 — Pergunta | 22 | 22 | a pergunta, os dois objetos e a margem observada |
| 12 — De onde vem o modelo | 23–24 | 23–24 | **23** a estrutura da decisão (Moehling et al.). **24** o custo geográfico (Redding & Rossi-Hansberg), o custo de trabalhar (Choné & Ma) e o que nenhuma das três trata |
| 13 — Como o médico escolhe onde trabalhar | 25 | 25–26 | **frame único com dois overlays**: a equação fica fixa; no primeiro overlay, a condição de aceitação; no segundo, o glossário termo a termo |
| 14 — O que a bolsa paga — e o que não paga | 26–27 | 27–28 | **26** a decomposição `B + w^priv` e a tabela capital/interior. **27** as duas consequências e o deflator |
| 15 — O custo de estar ali | 28–30 | 29–31 | **28** a equação com os dois blocos e a tabela de componentes. **29** o papel duplo de `L` e `K`. **30** figura `F4` |
| 16 — O IVS organiza o custo | 31–32 | 32–33 | **31** `c = c₀(IVS) + η` e a correspondência dimensão–bloco. **32** a ambiguidade do sinal e por que o objeto é o degrau |
| 17 — Duas hipóteses | 33–34 | 34–35 | **33** passos 1, 2 e 3 — a condição de aceitação, a passagem do médico à vaga e a tabela H1/H2. **34** passo 4 sozinho: a condição de degrau |
| 18 — Viabilidade empírica | 35–36 | 36–37 | **35** a tabela peça a peça. **36** o que fica de fora, a dificuldade e o primeiro passo |

---

## 3. Decisões de composição

### 3.1 O texto não repete o número que a figura já rotula

Regra aplicada em todo o deck: **quando a figura carrega o número rotulado, o
texto ao lado fica só com a afirmação**. A figura prova, a frase interpreta.

| Frame | Números que ficam só na figura | O que o texto diz |
|:---:|---|---|
| 5 | 16,0 / 10,0 / 7,3 | "menos da metade de especialistas por habitante onde a bolsa seria maior" |
| 6 | 5 / 3 / 2 colegas; 15% / 34% / 42% | "encontraria menos colegas da sua especialidade — e é lá que é maior a chance de ser o único, ou de ter um só colega" |
| 20–21 | 23,6% / 37,4% / 31,6%; 35,6% / 44,9% / 26,9% / 20,5% | "pagar o dobro não preencheu mais que pagar uma vez e meia"; "o preenchimento cai do município metropolitano e da capital para o interior conectado a um polo, e é menor no interior remoto" |

Os números continuam todos na tela, dentro da figura, com a mesma redação do
documento de conteúdo. O que desapareceu foi a segunda exibição do mesmo valor
em prosa, que obrigava a plateia a ler tudo duas vezes.

Números que a figura **não** rotula continuam em texto: 295 municípios (frame
5), 1.295 / 460 / 368 / 678 / 1.145 / 39% / 252 / 18 capitais (frame 12),
102 / 107 / 159 (frame 14), 30% das 1.295 vagas (frame 20).

### 3.2 Overlay onde o segundo frame explicaria o primeiro

O slide 13 do documento traz a função-valor e, logo abaixo, o glossário que
explica **aquela** equação. Separar os dois em frames deixaria o glossário sem
o referente na tela. O frame 25 resolve isso com `\only`: a equação fica fixa
no topo nos dois overlays; muda só o que vem abaixo — primeiro a condição de
aceitação, depois a tabela Termo/Leitura. São duas páginas de PDF e **um** slide
de fala.

Nos slides 15 e 16 o problema não existe: equação e tabela já estão no mesmo
frame (28 e 31).

### 3.3 Uma só legenda por figura, no formato do resto do deck

As cinco figuras geradas por script trazem, dentro do próprio PNG, uma linha de
proveniência em corpo minúsculo. O deck **não** acrescenta uma segunda legenda
centralizada: a fonte aparece uma única vez, no bloco `Fontes:` em negrito,
alinhado à esquerda, separado por filete fino — exatamente como nos frames de
texto. A linha interna do PNG é parte da figura e não pode ser alterada.

O mesmo vale para as citações: em todo o deck, referência bibliográfica vai no
bloco `Fontes:` do rodapé do frame. Nenhuma referência aparece solta em cinza
dentro do corpo.

### 3.4 Fusões e densidade

- **Slide 4** passou de três frames para dois: cada figura ficou com a sua
  afirmação, e o frame de texto que repetia os números deixou de existir.
- **Slide 6**: os números do ciclo 1 e a figura `F5` estavam em frames
  separados e vieram para o mesmo frame, em duas colunas — texto à esquerda,
  figura à direita, que assim ganhou largura em vez de perder.
- **Slide 7**: a tabela categoria–faixa–bolsa e a figura `F3` diziam a mesma
  coisa em dois frames. Foram fundidas em um, lado a lado.
- **Slide 17**: os quatro passos estavam repartidos 2 + 2, com o segundo frame
  carregando a tabela de derivadas e mais duas equações. O passo 3 subiu para o
  primeiro frame; o passo 4 — a condição de degrau, que é a conclusão do bloco
  teórico — ficou sozinho no segundo, em caixa destacada.
- **Slide 13**: dois frames viraram um frame com dois overlays.

O resultado é 36 frames para os 28 minutos previstos na seção 6 do roteiro, com
a motivação em 19 frames. Não houve corte de conteúdo — só de repetição.

### 3.5 O que o tema Warsaw ganhou e o que perdeu

Mantidos, porque são o que torna o tema reconhecível: o `frametitle` em faixa
com degradê e sombra, os blocos arredondados com sombra do tema interno
`rounded`, e a estrutura headline / corpo / footline.

Alterados, em nome da legibilidade:

- **Cor.** O azul padrão foi trocado por um verde escuro que casa com a paleta
  das figuras já versionadas (`#16301F` e `#2A5539`), de modo que gráfico e
  slide não briguem.
- **Headline.** A barra de navegação de seções/subseções do Warsaw foi
  substituída por uma **faixa fina de rastreio**, em verde muito claro, com a
  linha de rastreio do slide de origem em `\scriptsize`.
- **Footline.** As três caixas com autor, título, data e página viraram uma
  faixa fina única: título curto à esquerda, `frame/total` à direita. Em um
  frame com overlays, os dois números são iguais — é o mesmo slide.
- **Símbolos de navegação.** Removidos.

### 3.6 Tabelas e matemática

As figuras que dividem frame com texto são limitadas pela **altura**, não pela
largura: o teto de altura de cada uma foi ajustado até o limite em que o bloco
`Fontes:` ainda cabe acima do rodapé, para que a barra ocupe o máximo de largura
possível e o rótulo de categoria (`Faixa 3 / R$ 10 mil / média, baixa ou muito
baixa`) continue legível em projeção. No frame 12 o texto fica em coluna própria
ao lado da figura, larga o bastante para não picotar as linhas.

Caixas de destaque mais estreitas que o bloco de texto são centradas via
`minipage`: `\centering` sozinho não centra um `beamercolorbox` de largura fixa.

`booktabs` em todas as tabelas; `tabularx` quando alguma coluna quebra linha;
valores monetários à direita. Onde a tabela não cabia com folga — as quatro
desvantagens (frame 7), o glossário da função-valor (frame 25), a
correspondência IVS–custo (frame 31), as duas hipóteses (frame 34) e a
viabilidade (frame 35) — reduziu-se para `\footnotesize` com `\arraystretch`
menor, em vez de encolher a fonte até o ilegível.

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
frame 30 ela ocupa a altura máxima que o frame permite (`0,74\textheight`, com
largura de cerca de 9,5 cm); mesmo assim, **a legenda e as anotações de zona
ficam em torno de 5 pt na tela projetada** e não são legíveis do fundo da sala.
As três curvas e os dois pontos de inflexão continuam legíveis.

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
  sem nenhum `Overfull \hbox`.
- Duas execuções seguidas produzem o mesmo PDF (mesmo `md5sum`).
- As 37 páginas foram convertidas em PNG (`pdftoppm -png -r 90`) e revistas uma
  a uma: nenhuma tem texto vazando do frame, tabela cortada, bloco de fonte
  sobreposto ao rodapé, figura deformada, legenda duplicada ou caixa de destaque
  fora de eixo.
- Os 18 slides do documento estão representados, na ordem, com os 16 títulos
  literais dos slides 3 a 18.
