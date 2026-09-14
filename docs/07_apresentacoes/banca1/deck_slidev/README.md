# Deck Slidev da banca 1

> **Fonte de verdade do conteúdo:** [`../02_conteudo_slides.md`](../02_conteudo_slides.md)<br>
> **Regras de composição:** [`../01_roteiro_narrativo.md`](../01_roteiro_narrativo.md), seção 2<br>
> **Proveniência:** [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md)<br>
> **Atualização:** 14 de setembro de 2026

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
links das figuras e exporta. É determinístico e usa caminhos relativos à raiz.

### Figuras: nenhuma cópia entra no versionamento

O Slidev serve imagens a partir de `public/`. As figuras deste deck **já existem
no repositório** e não podem ser regeradas, editadas nem duplicadas — regra de
proveniência do projeto. Por isso o passo 2 do script cria
`deck_slidev/public/fig/` como **diretório de trabalho não versionado**
(`.gitignore`) com **links simbólicos** para os arquivos originais:

| Link em `public/fig/` | Arquivo original |
|---|---|
| `oferta_pre_por_faixa.png` | `output/apresentacao_banca1/oferta_pre_por_faixa.png` |
| `retaguarda_por_faixa.png` | `output/apresentacao_banca1/retaguarda_por_faixa.png` |
| `vagas_ciclo1_por_regiao.png` | `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` |
| `bolsa_por_faixa.png` | `output/apresentacao_banca1/bolsa_por_faixa.png` |
| `preenchimento_ciclo1.png` | `output/apresentacao_banca1/preenchimento_ciclo1.png` |
| `curva_custo_laboral_burnout.png` | `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` |

Se algum arquivo faltar, o build falha em vez de gerar um deck com figura
quebrada.

### Playwright

A exportação usa o Chromium já instalado na imagem. O script fixa
`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers` e `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`;
**nunca rode `playwright install`**. O pacote `playwright-chromium` é dependência
declarada apenas para fornecer a API; o binário vem do caminho acima.

Duas particularidades do ambiente que o script já contorna:

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

### 3.1 Um slide do documento pode virar mais de uma página

O documento tem **18 slides**; o deck tem **36 páginas**. O critério foi sempre
o mesmo: **uma afirmação por página** (roteiro, seção 2.2) e nada de página
sobrecarregada. Quando um slide do documento carregava dois movimentos
distintos do argumento, ele foi partido. Nenhuma informação foi acrescentada,
removida ou alterada nesse processo.

O título literal da seção 2.1 do roteiro é **repetido** em todas as páginas do
mesmo slide; a faixa de rastreio distingue "1 de 2", "2 de 2" e assim por diante.

### 3.2 Mapeamento documento → páginas

| Slide do documento | Título | Páginas | O que ficou em cada página |
|:---:|---|:---:|---|
| 1 | *Capa* | 1 | — |
| 2 | *Sumário* | 2 | — |
| 3 | Especialistas não faltam; faltam no interior | 3–4 | 3: o retrato numérico. 4: a urgência reconhecida e as manchetes |
| 4 | Onde a bolsa é maior, já havia menos especialistas | 5–6 | 5: oferta por habitante (F1). 6: retaguarda de colegas (F2) |
| 5 | O que o médico vê ao decidir | 7–8 | 7: as quatro desvantagens e o que medimos. 8: o que a literatura diz sobre o peso de cada uma |
| 6 | O que é o PMM-E | 9–11 | 9: lei, quem, o quê. 10: como a vaga chega ao médico. 11: onde, no ciclo 1 (F5) |
| 7 | A bolsa remunera o lugar | 12–13 | 12: os três passos, índice → categoria → valor. 13: a grade (F3), as contagens e os dois cuidados |
| 8 | Pagar mais funciona: a evidência a favor | 14–15 | 14: o experimento mexicano. 15: a régua do prêmio e a ressalva |
| 9 | Mas é caro, e não segura: a evidência contra | 16–17 | 16: Austrália e Brasil. 17: Estados Unidos e o fecho do bloco |
| 10 | No primeiro ciclo, a bolsa maior não ordenou o preenchimento | 18–19 | 18: o fato e a figura em dois painéis (F6). 19: as duas leituras e a ressalva descritiva |
| 11 | Pergunta | 20 | — |
| 12 | De onde vem o modelo | 21–22 | 21: as três tradições e Moehling et al. 22: Redding & Rossi-Hansberg, Choné & Ma, e o que falta nas três |
| 13 | Como o médico escolhe onde trabalhar | 23–24 | 23: a equação e a regra de aceitação. 24: a leitura de cada termo |
| 14 | O que a bolsa paga — e o que não paga | 25–26 | 25: a decomposição e o contraste capital/interior. 26: as duas consequências e o deflator |
| 15 | O custo de estar ali | 27–29 | 27: a equação e os componentes. 28: equipe e capital agindo duas vezes. 29: a curva de custo laboral (F4) |
| 16 | O IVS organiza o custo | 30–31 | 30: a redução ao índice e a correspondência com as dimensões. 31: a ambiguidade do sinal e o degrau como objeto |
| 17 | Duas hipóteses | 32–34 | 32: passos 1 e 2. 33: passo 3, H1 e H2. 34: passo 4, a condição de degrau |
| 18 | Viabilidade empírica | 35–36 | 35: o que se mede de cada peça. 36: o que fica de fora, a dificuldade e o primeiro passo |

### 3.3 Rastreio de seção

A linha em `código` de cada slide do documento aparece **fora do título**, em
faixa fina no topo da página, em corpo pequeno e cor esmaecida — componente
`components/Rastreio.vue`. À direita da mesma faixa ficam o marcador de
continuação ("2 de 3") e o número da página. A paginação nativa do tema foi
desativada (`themeConfig.paginationX/Y` vazios) para não duplicar o contador.

### 3.4 Fontes dos números

Toda página que exibe número traz a fonte em faixa fina no rodapé — componente
`components/Fonte.vue`, corpo 0,545 rem, cinza esverdeado. Fonte nunca compete
com o conteúdo. As figuras trazem ainda a própria legenda embutida, gerada pelo
script de figuras; a faixa de rodapé complementa com cobertura, unidade e
recorte.

### 3.5 Hierarquia visual

- **Título** em Montserrat, verde escuro, com filete esverdeado embaixo.
- **Afirmação central** em caixa verde sólida (`.callout`) — é o que a banca lê
  primeiro se olhar a página por dois segundos.
- **Números exibidos** em cartões (`.stat`), com o valor grande e a leitura em
  corpo menor logo abaixo. Nenhum número aparece solto no meio de um parágrafo
  quando é o ponto do slide.
- **Ressalvas** em caixa neutra de contorno fino, em corpo menor: presentes,
  mas visualmente subordinadas.
- **Equações** em faixa clara com filete verde à esquerda, sempre isoladas do
  texto corrido.
- **Tabelas** sem grade vertical, só filetes horizontais, com cabeçalho em
  versalete. Nenhuma tabela excede seis linhas.

A paleta foi tirada das próprias figuras do repositório (o verde escuro e o
sálvia do matplotlib), para que figura e slide pareçam a mesma peça.

### 3.6 Equilíbrio vertical

Todas as páginas usam a classe `centrado`: o título fica ancorado no alto, fora
do fluxo, e o corpo é centrado no espaço restante. Sem isso, o conteúdo se
acumulava no topo com um vazio grande embaixo. Todos os títulos do deck cabem em
uma linha, o que mantém constante o recuo do corpo.

### 3.7 Matemática

As equações dos slides 13 a 17 do documento são renderizadas por KaTeX.
Alterações de notação em relação ao documento: **nenhuma**. Foi conferido
página a página que `\underbrace`, `\gtrless`, `\mathbb{E}`, `\arg\max`,
`\text{R\$ }` e as derivadas parciais renderizam.

Um cuidado de estilo: o cabeçalho de tabela é em caixa alta, e `text-transform`
transformaria o símbolo `c` em `C`. A regra é anulada dentro de `.katex` — um
símbolo matemático não pode mudar de caixa.

### 3.8 O que não foi feito

- **Sem páginas de divisão de seção.** A faixa de rastreio já nomeia a seção em
  toda página; páginas extras só para anunciar a seção custariam tempo de fala
  sem acrescentar informação.
- **Sem slide de perguntas.** A apresentação termina na viabilidade empírica,
  como manda o escopo da banca 1.
- **Sem notas de apresentador.** Regra 2.3 do roteiro: o que precisa ser dito
  está no slide ou não está.
- **Sem animação ou transição.** `transition: none`. Cliques progressivos
  fragmentariam a leitura de páginas que já são uma afirmação cada.

---

## 4. Arquivos

| Arquivo | Função |
|---|---|
| `slides.md` | o deck |
| `style.css` | estilo sobre o `slidev-theme-academic`: paleta, tipografia, cartões, tabelas, faixas |
| `components/Rastreio.vue` | faixa de rastreio de seção, no topo |
| `components/Fonte.vue` | faixa de fontes, no rodapé |
| `components/Fig.vue` | figura com altura máxima controlada, sem distorção de proporção |
| `package.json`, `package-lock.json` | versões exatas: `@slidev/cli` 52.19.1, `slidev-theme-academic` 3.0.1 |
