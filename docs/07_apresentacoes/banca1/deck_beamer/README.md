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

---

## 1. Como compilar

```bash
# sempre a partir da raiz do repositório
bash scripts/apresentacao/build_deck_beamer.sh
```

O script:

1. posiciona-se na raiz do repositório (todos os caminhos são relativos a ela);
2. confere que as seis figuras existem antes de chamar o LaTeX;
3. roda `pdflatex` duas vezes (a segunda resolve a contagem total de páginas do
   rodapé), com `-halt-on-error`;
4. relata qualquer `Overfull \hbox` da última passada;
5. grava `output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf` e remove os
   auxiliares.

`SOURCE_DATE_EPOCH` e `FORCE_SOURCE_DATE` são fixados no script, de modo que
duas execuções sobre a mesma entrada produzam o mesmo PDF.

**Requisitos:** `pdflatex` com `beamer`, `beamerthemeWarsaw.sty`,
`texlive-latex-extra`, `texlive-fonts-recommended`, `lmodern` e
`texlive-lang-portuguese`.

**Figuras.** O deck lê apenas figuras já versionadas, por `\graphicspath`
relativo à raiz:

| Código | Arquivo | Frame |
|---|---|:---:|
| `F1` | `output/apresentacao_banca1/oferta_pre_por_faixa.png` | 6 |
| `F2` | `output/apresentacao_banca1/retaguarda_por_faixa.png` | 7 |
| `F5` | `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` | 14 |
| `F3` | `output/apresentacao_banca1/bolsa_por_faixa.png` | 17 |
| `F6` | `output/apresentacao_banca1/preenchimento_ciclo1.png` | 23 |
| `F4` | `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` | 34 |

Nenhuma figura é gerada, editada ou recortada por este deck. Para regerar as
cinco de `output/`, ver [`../README.md`](../README.md), seção 3.

---

## 2. Mapeamento: slide do documento → frames do deck

18 slides do documento, **41 frames**. O rastreio de seção exibido é sempre o
do slide de origem, literal; quando um slide vira mais de um frame, todos
repetem o mesmo rastreio e o mesmo título.

| Slide do documento | Frames | O que ficou em cada frame |
|---|:---:|---|
| 1 — Capa | 1 | capa |
| 2 — Sumário | 2 | as seis seções, em duas colunas |
| 3 — Especialistas não faltam; faltam no interior | 3–4 | **3** retrato nacional: 353 mil, 55%/6%, 453/68/70, manchete do Senado. **4** urgência em saúde pública e as duas manchetes |
| 4 — Onde a bolsa é maior, já havia menos especialistas | 5–7 | **5** as duas afirmações numéricas (“menos da metade”, “vai sozinho”) e a fonte completa. **6** figura `F1`. **7** figura `F2` |
| 5 — O que o médico vê ao decidir | 8–9 | **8** tabela das quatro desvantagens e do que se mede. **9** as três evidências da literatura sobre o peso de cada uma |
| 6 — O que é o PMM-E | 10–14 | **10** Lei e Quem. **11** O quê: aprimoramento em serviço e os 16 cursos. **12** como a vaga chega ao médico. **13** onde, no primeiro ciclo: os números. **14** figura `F5` |
| 7 — A bolsa remunera o lugar | 15–18 | **15** os três passos (índice, categoria, valor). **16** tabela categoria–faixa–bolsa e a contagem 102/107/159. **17** figura `F3`. **18** os dois cuidados |
| 8 — Pagar mais funciona: a evidência a favor | 19–20 | **19** o experimento mexicano. **20** a régua do prêmio compensatório, o degrau de +50% e a ressalva das 20 horas |
| 9 — Mas é caro, e não segura: a evidência contra | 21–22 | **21** Austrália e Brasil. **22** Estados Unidos e o fecho “dinheiro move alocação, mas…” |
| 10 — No primeiro ciclo, a bolsa maior não ordenou o preenchimento | 23–24 | **23** os 30% e a figura `F6`. **24** leitura por faixa e por território, e “descrição, não efeito” |
| 11 — Pergunta | 25 | a pergunta, os dois objetos e a margem observada |
| 12 — De onde vem o modelo | 26–27 | **26** a estrutura da decisão (Moehling et al.). **27** o custo geográfico (Redding & Rossi-Hansberg), o custo de trabalhar (Choné & Ma) e o que nenhuma das três trata |
| 13 — Como o médico escolhe onde trabalhar | 28–29 | **28** a equação, a regra de escolha e a condição de aceitação. **29** a tabela termo a termo |
| 14 — O que a bolsa paga — e o que não paga | 30–31 | **30** a decomposição `B + w^priv` e a tabela capital/interior. **31** as duas consequências e o deflator |
| 15 — O custo de estar ali | 32–34 | **32** a equação com os dois blocos e a tabela de componentes. **33** o papel duplo de `L` e `K`. **34** figura `F4` |
| 16 — O IVS organiza o custo | 35–36 | **35** `c = c₀(IVS) + η` e a correspondência dimensão–bloco. **36** a ambiguidade do sinal e por que o objeto é o degrau |
| 17 — Duas hipóteses | 37–39 | **37** passos 1 e 2. **38** passo 3: H1 e H2. **39** passo 4: a condição de degrau |
| 18 — Viabilidade empírica | 40–41 | **40** a tabela peça a peça. **41** o que fica de fora, a dificuldade e o primeiro passo |

---

## 3. Decisões de composição

### 3.1 O que o tema Warsaw ganhou e o que perdeu

Mantidos, porque são o que torna o tema reconhecível: o `frametitle` em faixa
com degradê e sombra, os blocos arredondados com sombra do tema interno
`rounded`, e a estrutura headline / corpo / footline.

Alterados, em nome da legibilidade:

- **Cor.** O azul padrão foi trocado por um verde escuro que casa com a paleta
  das figuras já versionadas (`#16301F` e `#2A5539`), de modo que gráfico e
  slide não briguem. O degradê do `frametitle` vai de `#2A5539` a `#16301F`.
- **Headline.** A barra de navegação de seções/subseções do Warsaw foi
  substituída por uma **faixa fina de rastreio**, em verde muito claro, com a
  linha de rastreio do slide de origem em `\scriptsize`. Isso atende à regra
  “o rastreio aparece no slide, fora do título” sem a poluição da barra
  original.
- **Footline.** As três caixas coloridas com autor, título, data e página foram
  substituídas por uma faixa fina única: título curto à esquerda, `frame/total`
  à direita.
- **Símbolos de navegação.** Removidos.

### 3.2 Título, rastreio e fontes

- Os 16 títulos dos slides 3 a 18 são usados **literalmente**, como fixados na
  seção 2.1 do roteiro. Nenhum título nomeia a seção.
- O rastreio fica na faixa do topo, nunca no título. Um slide dividido em N
  frames repete o rastreio do documento sem sufixo — o corte é invisível para
  a banca.
- Toda fonte vai ao rodapé do frame, em `\scriptsize` cinza, separada do corpo
  por um filete verde claro. Em frames que são só figura, a fonte vira uma
  linha única de legenda, também em `\scriptsize` cinza.

### 3.3 Por que 41 frames e não 18

A regra “uma afirmação por slide” e a exigência de legibilidade não cabem em 18
telas: o slide 6 do documento, por exemplo, tem lei, público, formato, 16
cursos, fluxo da vaga, números do ciclo 1 e uma figura. O documento continua
sendo a unidade de conteúdo; o frame é a unidade de exibição. Cada divisão
mantém título e rastreio, e nenhuma informação exibida contradiz o documento.

### 3.4 Figuras em frame próprio

As cinco figuras geradas por script trazem eixos, rótulos de categoria e uma
legenda de proveniência dentro da própria imagem. Espremidas em meia largura,
essas marcações ficam ilegíveis em projeção. `F1`, `F2`, `F5`, `F3` e `F4`
ganharam por isso **frame dedicado**, com largura total e altura até
`0,80–0,82\textheight`; o texto que as acompanhava no documento foi para o
frame vizinho, sob o mesmo título. `F6` é larga o bastante (proporção 2,5:1)
para caber com uma linha de texto acima.

Nenhuma figura foi recortada, redimensionada em arquivo ou regerada — só
escalada por `\includegraphics` com `keepaspectratio`.

### 3.5 Tabelas

`booktabs` em todas; `tabularx` quando alguma coluna precisa quebrar linha.
Valores monetários alinhados à direita. Onde a tabela do documento não cabia
com folga — as quatro desvantagens (frame 8) e a correspondência IVS–custo
(frame 35) — reduziu-se para `\footnotesize` com `\arraystretch` menor, em vez
de encolher a fonte até o ilegível. A tabela categoria–faixa–bolsa (frame 16)
foi separada da figura `F3` para que nenhuma das duas ficasse espremida.

### 3.6 Matemática

Todas as equações dos slides 12 a 17 do documento são reproduzidas em `amsmath`
como display, sem redução de corpo. A única reorganização visual é no slide 13:
o `\arg\max` que o documento põe na mesma linha da função-valor, separado por
`\qquad`, foi para uma segunda linha centralizada.

### 3.7 Vocabulário

Nenhuma palavra escrita fora do documento de conteúdo introduz econometria ou
estimação; a única prosa de ligação acrescentada é neutra. As substituições da
seção 2.5 do roteiro já vêm resolvidas do documento — “célula com alguma
confirmação ou homologação”, “presença cadastral no CNES”, “gradiente” — e
foram preservadas.

---

## 4. Verificação feita nesta versão

- `bash scripts/apresentacao/build_deck_beamer.sh` termina sem erro de LaTeX e
  sem nenhum `Overfull \hbox`.
- As 41 páginas foram convertidas em PNG (`pdftoppm -png -r 90`) e revistas uma
  a uma: nenhuma tem texto vazando do frame, tabela cortada, figura deformada
  ou sobreposição com o rodapé.
- Os 18 slides do documento estão representados, na ordem, com os 16 títulos
  literais dos slides 3 a 18.

## 5. Ponto de atenção herdado do documento

No frame 11, a lista dos cursos ambulatoriais é transcrita literalmente do
documento de conteúdo, que anuncia **10 ambulatoriais** e enumera oito itens
entre parênteses. A divergência é do documento canônico, não do deck; corrigi-la
aqui violaria a regra de fidelidade. Registrada para conferência no edital.
