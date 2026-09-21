# Deck Slidev da banca 1

> **Fonte de verdade do conteúdo:** [`../02_conteudo_slides.md`](../02_conteudo_slides.md)<br>
> **Regras de composição:** [`../01_roteiro_narrativo.md`](../01_roteiro_narrativo.md), seção 2<br>
> **Proveniência:** [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md)<br>
> **Atualização:** 21 de setembro de 2026 — reconstruído na estrutura vigente de **17 slides em 3 seções**, com Q&A e apêndice

Este diretório é **artefato derivado**. Regra do projeto: divergência entre deck
e documento de conteúdo é erro do deck, nunca do documento. Nenhuma afirmação,
número, citação ou fonte foi criada aqui.

---

## 1. Como rodar

Pré-requisitos: Node 22 e npm. As versões estão fixadas em `package.json` e
travadas em `package-lock.json`.

```bash
# instalação determinística (a partir da raiz do repositório)
npm ci --prefix docs/07_apresentacoes/banca1/deck_slidev

# apresentação ao vivo, com recarga
npm run dev --prefix docs/07_apresentacoes/banca1/deck_slidev
```

## 2. Como exportar

```bash
# a partir da raiz do repositório
bash scripts/apresentacao/build_deck_slidev.sh          # só o PDF
bash scripts/apresentacao/build_deck_slidev.sh png      # PDF + um PNG por página
```

Saídas:

| Arquivo | Versionado |
|---|:---:|
| `output/apresentacao_banca1/deck_slidev/banca1_slidev.pdf` | sim |
| `output/apresentacao_banca1/deck_slidev/png/NN.png` | não — material de revisão, derivado do mesmo deck |

O script instala as dependências apenas se `node_modules/` não existir, cria os
links das figuras e exporta. Usa caminhos relativos à raiz.

**O PDF não é reprodutível byte a byte**, ao contrário do que este README
afirmava até 21/09/2026. Duas execuções sobre a mesma entrada produzem SHA-256
diferentes: quem escreve o PDF é o Chromium, que carimba identificadores
próprios a cada exportação. O **conteúdo** é o mesmo — mesmas 40 páginas, mesmo
texto —, e é isso que as versões fixadas em `package-lock.json` garantem. Quem
precisa de build byte a byte idêntico tem o deck Beamer, que é
determinístico de verdade por `SOURCE_DATE_EPOCH`.

### Figuras: nenhuma cópia entra no versionamento

O Slidev serve imagens a partir de `public/`. As figuras deste deck **já existem
no repositório** e não podem ser regeradas, editadas nem duplicadas — regra de
proveniência do projeto. Por isso o passo 2 do script cria
`deck_slidev/public/fig/` como **diretório de trabalho não versionado**
(`.gitignore`) com **links simbólicos** para os arquivos originais:

São **sete**, as mesmas do documento canônico e as mesmas do deck Beamer:
`especialistas_por_uf_extremos`, `deslocamento_por_regiao` e
`dupla_pratica_cirurgioes` no slide 4; `bolsa_por_faixa`, `oferta_pre_por_faixa`
e `retaguarda_por_faixa` no slide 5; `preenchimento_ciclo1` no slide 7. Todas
em `output/apresentacao_banca1/`.

`vagas_ciclo1_por_regiao.png` e `curva_custo_laboral_burnout.png` saíram do
deck em 16/09/2026 e não são mais vinculadas. Se algum arquivo faltar, o build
falha em vez de gerar um deck com figura quebrada.

### Playwright

A exportação usa o Chromium já instalado na imagem. O script fixa
`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` e `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`;
**nunca rode `playwright install`**. O pacote `playwright-chromium` é dependência
declarada apenas para fornecer a API; o binário vem do caminho acima.

Três particularidades do ambiente que o script já contorna:

1. `slidev export` é executado com `--per-slide`. Sem essa opção, a exportação em
   peça única falha com `locator.waitFor: Timeout` neste ambiente.
2. `NODE_ENV` **não** é fixado como `production`. O `slidev export` sobe um
   servidor Vite de desenvolvimento; com `NODE_ENV=production` a página não
   monta e a exportação estoura o tempo limite.
3. A exportação é tentada até três vezes: na primeira execução depois de
   qualquer mudança de dependência, o Vite reotimiza o bundle e recarrega a
   página no meio de uma espera do Playwright que tem limite fixo de 30 s.

### Fontes tipográficas

O Chromium do Playwright não alcança `fonts.googleapis.com`. As fontes são
empacotadas localmente via `@fontsource` e importadas em `style.css`
(`fonts.provider: none` no cabeçalho do `slides.md`), de modo que o build não
depende de rede e o resultado é sempre o mesmo:

- **Montserrat** — títulos, rótulos e números em destaque (é a fonte do tema
  `slidev-theme-academic`, preservada onde ela define a identidade)
- **Source Sans 3** — corpo de texto, tabelas e legendas; mais econômica em
  largura que a Montserrat, o que importa nos slides mais densos

---

## 3. Decisões de composição

### 3.1 Um build do documento é uma página

O documento canônico tem **17 slides** e **32 builds**, mais o Q&A e **4
slides de apêndice** com 7 builds. Aqui cada **build** é uma página: são
**40 páginas**, exatamente as do deck Beamer.

A convenção é a mesma desde a origem deste deck, e difere da do Beamer de
propósito. No Beamer um `###` é um `\only<n>` do mesmo frame, e o rodapé
repete o número do slide. No Slidev não há overlay que substitua conteúdo, e
o deck sempre resolveu isso repetindo o título e marcando o build no rastreio:
`1 de 3`, `2 de 3`, `3 de 3`. Para quem assiste, o efeito é o mesmo — o slide
se completa —, e a numeração de página do rastreio conta páginas, não slides.

| Documento | Páginas aqui |
|---|:---:|
| capa, sumário | 1–2 |
| divisória 1 e slides 4 a 8 | 3–16 |
| divisória 2 e slides 10 a 13 | 17–25 |
| divisória 3 e slides 15 a 17 | 26–32 |
| Q&A e apêndice `A1` a `A4` | 33–40 |

### 3.2 Divisórias, Q&A e apêndice

As três divisórias de seção e o Q&A usam a classe `divisoria`, definida em
`style.css`: número grande em sage, título e subtítulo, os mesmos do
documento. O Q&A não tem número. É o equivalente do `\pmmedivisoria` do deck
Beamer, na identidade própria deste deck.

No apêndice o rastreio recebe a propriedade `semnum`, que **tira o contador de
página**: continuar a numeração da parte principal sugeriria que o apêndice é
parte da fala, e ele não é. O rastreio passa a dizer `Apêndice · A1`.

### 3.3 Matemática em prosa

Inline math **não renderiza dentro de um `<p>` solto**: um bloco HTML de nível
de bloco é passado adiante sem processamento de Markdown, e o KaTeX não chega
nele. Onde a prosa tem `$...$`, o parágrafo é escrito como

```html
<div class="sm">

texto com $\delta$ e $c_{im}$

</div>
```

com as linhas em branco, que devolvem o conteúdo ao parser de Markdown. Vale
também a regra do `markdown-it`: `$...$` seguido imediatamente de dígito não é
tratado como matemática, e por isso se escreve `$\pm 0{,}050$`, e não
`$\pm$0,050`.

## 4. Ressalvas

**Nenhuma aberta.** A pendência 6 — decks na estrutura de 15 slides — fecha
aqui em 21/09/2026, depois de ter fechado para o Beamer em 19/09. As
pendências de conteúdo (1, 2, 5, 8, 9) são do documento canônico e aparecem
na tela como ele as escreve, inclusive no slide `A4` do apêndice.

**Duas diferenças deliberadas em relação ao deck Beamer**, que não são
divergência com o documento: a identidade visual, que aqui é a do
`slidev-theme-academic` com a paleta verde própria e lá é a institucional do
Insper; e a numeração do rodapé, que aqui conta páginas de ponta a ponta e lá
para em `17 / 17`, porque lá um build não é uma página.

A ressalva de conteúdo da versão anterior — a divergência entre "10
ambulatoriais" e a lista de oito, transcrita por fidelidade — foi encerrada no
documento canônico em 16/09/2026: o slide passou a dar só a contagem, conferida
no edital e no quadro de vagas.

---

## 5. Arquivos

| Arquivo | Função |
|---|---|
| `slides.md` | o deck |
| `style.css` | estilo sobre o `slidev-theme-academic`: paleta, tipografia, cartões, tabelas, faixas |
| `components/Rastreio.vue` | faixa de rastreio de seção, no topo; `cont` marca o build e `semnum` tira o contador, no apêndice |
| `components/Fonte.vue` | faixa de fontes, no rodapé |
| `components/Fig.vue` | figura com altura máxima controlada, sem distorção de proporção |
| `package.json`, `package-lock.json` | versões exatas: `@slidev/cli` 52.19.1, `slidev-theme-academic` 3.0.1 |
