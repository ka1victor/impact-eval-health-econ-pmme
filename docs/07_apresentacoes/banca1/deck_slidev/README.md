# Deck Slidev da banca 1

> [!WARNING]
> **Este deck está desatualizado em relação ao documento canônico.** Desde
> **16/09/2026**, [`../02_conteudo_slides.md`](../02_conteudo_slides.md) tem
> **16 slides em 3 seções**, com divisórias de seção e convenção nova de
> cabeçalhos; este deck continua na **estrutura anterior, de 15 slides em 6
> seções**, exportada em 26 páginas. A reconstrução ficou para depois, por
> decisão do autor.
>
> A divergência é **conhecida e datada** — é a pendência 6 do fim do documento
> de conteúdo — e não altera a regra do projeto: **o documento canônico vence**.
> Enquanto os dois não forem reconciliados, os números de slide, os títulos e os
> mapeamentos deste README descrevem o **estado anterior**, não o que vai à tela.

> **Fonte de verdade do conteúdo:** [`../02_conteudo_slides.md`](../02_conteudo_slides.md)<br>
> **Regras de composição:** [`../01_roteiro_narrativo.md`](../01_roteiro_narrativo.md), seção 2<br>
> **Proveniência:** [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md)<br>
> **Atualização:** 16 de setembro de 2026 (corte de 19 para 15 slides; deck
> parado nessa estrutura)

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
| `bolsa_por_faixa.png` | `output/apresentacao_banca1/bolsa_por_faixa.png` |
| `oferta_pre_por_faixa.png` | `output/apresentacao_banca1/oferta_pre_por_faixa.png` |
| `retaguarda_por_faixa.png` | `output/apresentacao_banca1/retaguarda_por_faixa.png` |
| `preenchimento_ciclo1.png` | `output/apresentacao_banca1/preenchimento_ciclo1.png` |
| `oferta_total_mensal.png` | `output/apresentacao_banca1/oferta_total_mensal.png` |

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

### 3.1 Um slide do documento pode virar mais de uma página

Na estrutura anterior, à qual este deck corresponde, o documento tinha **15
slides** e o deck tem **26 páginas**. O critério foi sempre o mesmo: **uma
afirmação por página** (roteiro, seção 2.2), sem página sobrecarregada e sem
página curta demais para existir sozinha. Quando um slide do documento carrega
dois movimentos distintos do argumento, ele é partido; quando a divisão deixaria
duas metades magras, elas ficam juntas. Nenhuma informação é acrescentada,
removida ou alterada nesse processo.

O título literal da seção 2.1 do roteiro é **repetido** em todas as páginas do
mesmo slide; a faixa de rastreio distingue "1 de 2", "2 de 2" e assim por diante.

O orçamento de fala registrado para aquela estrutura era o da seção 6 do
roteiro: **24 minutos para os 15 slides**. Ele é um dos itens a rever na
reconstrução sobre os 16 slides atuais.

### 3.2 Mapeamento documento → páginas (estado anterior, 15 slides)

> [!NOTE]
> A tabela abaixo descreve o deck **como ele está**: mapeia os **15 slides da
> estrutura anterior** do documento de conteúdo. A coluna "Slide do documento" e
> os títulos **não correspondem** ao documento canônico vigente, de 16 slides em
> 3 seções. Serve para operar e revisar o PDF existente e como ponto de partida
> da reconstrução, não como descrição do que vai à tela.

| Slide do documento | Título | Páginas | O que ficou em cada página |
|:---:|---|:---:|---|
| 1 | *Capa* | 1 | — |
| 2 | *Sumário* | 2 | — |
| 3 | Especialistas faltam no interior, e o médico sabe por quê | 3–4 | 3: o retrato nacional e a tabela das quatro desvantagens. 4: o peso de cada uma na literatura e o fecho — urgência em saúde pública e o PMM-E |
| 4 | O que é o PMM-E | **5** | lei, quem, o quê e onde, em quatro cartões, e a faixa de bolsa em cada vaga |
| 5 | A bolsa remunera o lugar | 6–7 | 6: os três passos. 7: a grade (F3), as contagens e as cláusulas |
| 6 | Onde a bolsa é maior, o médico fica sozinho | 8–9 | 8: oferta por habitante (F1). 9: retaguarda de colegas (F2) |
| 7 | A evidência não decide se R$ 5 mil bastam | 10–11 | 10: a favor e contra lado a lado — México e o degrau; Austrália e Brasil. 11: Estados Unidos, a ressalva das 20 horas e o fecho |
| 8 | No primeiro ciclo, a bolsa maior não ordenou o preenchimento | **12** | a figura em dois painéis (F6), que já rotula os sete números, mais a leitura e a ressalva descritiva |
| 9 | Pergunta | 13 | — |
| 10 | A decisão: onde vale a pena estar | 14 | Moehling et al.: equação, glossário e a caixa-preta |
| 11 | Abrindo o custo: o lugar e o trabalho | 15–16 | 15: Redding & Rossi-Hansberg, o bloco geográfico e a limitação de residência. 16: Choné & Ma, o U e o papel duplo de equipe e capital |
| 12 | Como juntamos os três | 17–18 | 17: a função-valor, a abertura de `c` e a tabela de origem. 18: a decisão e o que nenhuma das três tem |
| 13 | O IVS organiza o custo | 19–21 | 19: `w = B + w^priv`, capital contra interior e o deflator. 20: a redução ao índice e a correspondência dimensão–bloco. 21: a ambiguidade do sinal e o degrau como objeto |
| 14 | A hipótese | 22–23 | 22: passos 1 e 2. 23: passos 3 e 4 — H1 e a condição de degrau |
| 15 | Viabilidade empírica | 24–26 | 24: o que se mede de cada peça. 25: o enquadramento e os três resultados da reconstrução da regra. 26: a conclusão de viabilidade e "o que fica de pé" |

### 3.3 A figura prova, a frase interpreta

Onde a figura **já traz o número rotulado na barra**, o texto ao lado fica só
com a afirmação. Repetir em texto um número que a barra já mostra faz a plateia
ler duas vezes e não saber onde olhar. Números que a figura **não** mostra —
295 municípios, 1.295 vagas, 30%, 102/107/159 — seguem em texto normalmente,
com a fonte no rodapé.

### 3.4 Rastreio de seção

A linha em `código` de cada slide do documento aparece **fora do título**, em
faixa fina no topo da página, em corpo pequeno e cor esmaecida — componente
`components/Rastreio.vue`. À direita da mesma faixa ficam o marcador de
continuação ("2 de 3") e o número da página. A paginação nativa do tema foi
desativada (`themeConfig.paginationX/Y` vazios) para não duplicar o contador.

### 3.5 Fontes dos números

Toda página que exibe número traz a fonte em faixa fina no rodapé — componente
`components/Fonte.vue`. Fonte nunca compete com o conteúdo. As figuras trazem
ainda a própria legenda embutida, gerada pelo script de figuras; a faixa de
rodapé complementa com cobertura, unidade e recorte.

### 3.6 Hierarquia visual

- **Título** em Montserrat, verde escuro, com filete esverdeado embaixo.
- **Afirmação central** em caixa verde sólida (`.callout`) — é o que a banca lê
  primeiro se olhar a página por dois segundos.
- **Números exibidos** em cartões (`.stat`), com o valor grande e a leitura em
  corpo menor logo abaixo.
- **Ressalvas** em caixa neutra de contorno fino, em corpo menor.
- **Equações** em faixa clara com filete verde à esquerda, sempre isoladas do
  texto corrido.
- **Tabelas** sem grade vertical, só filetes horizontais, com cabeçalho em
  versalete. Nenhuma tabela excede seis linhas.

A paleta foi tirada das próprias figuras do repositório (o verde escuro e o
sálvia do matplotlib), para que figura e slide pareçam a mesma peça.

### 3.7 Equilíbrio vertical

Todas as páginas usam a classe `centrado`: o título fica ancorado no alto, fora
do fluxo, e o corpo começa logo abaixo do filete. O espaço que sobra é ocupado
por quem ganha com isso: `<Fig h="fill">` consome toda a altura livre até a
barra de fontes (páginas 8, 9 e 12); `fill fill-tbl` estica as tabelas de
quatro linhas ou mais (páginas 3, 14, 15, 17, 20 e 24). Cartões e listas não
são esticados: cartão alto com o texto no topo vira caixa oca.

### 3.8 Matemática

As equações dos slides 10 a 14 do documento (numeração anterior) são
renderizadas por KaTeX, sem alteração de notação. O cabeçalho de tabela é em
caixa alta, e `text-transform` transformaria o símbolo `c` em `C`; a regra é
anulada dentro de `.katex`.

### 3.9 O que não foi feito

- **Sem páginas de divisão de seção.** A faixa de rastreio já nomeia a seção em
  toda página. **Decisão superada** pelo documento canônico de 16/09/2026, que
  passou a abrir cada seção com uma divisória própria (slides 3, 8 e 12): a
  reconstrução terá de acomodá-las.
- **Sem slide de perguntas.** A apresentação termina na viabilidade empírica.
- **Sem notas de apresentador.** Regra 2.3 do roteiro.
- **Sem animação ou transição.** `transition: none`.

### 3.10 O que o corte de 16/09/2026 mudou no deck

De 33 para 26 páginas. Saíram as páginas das manchetes, do fluxo "como a vaga
chega", da figura regional e da curva de custo laboral; a favor e contra
passaram a dividir uma página; a remuneração e o IVS passaram a ser um slide de
três páginas; a viabilidade ganhou uma página para o enquadramento e "o que fica
de pé". Nenhum número do documento cortado ficou fora do deck.

Dois defeitos de renderização herdados foram corrigidos na mesma passagem, ao
revisar as 26 páginas em PNG: o itálico dentro da caixa verde (`.callout em`)
herdava a cor escura do corpo e ficava invisível sobre o fundo — sumiam a
citação de Moehling et al., o *reduz* do custo marginal e *valor da bolsa* na
conclusão; e a matemática dentro do componente `Fonte` não passa pelo KaTeX, de
modo que `$\text{dist}$` e a derivada final apareciam como código. Os dois
trechos de rodapé passaram a texto corrido.

---

## 4. Ressalvas

**Uma aberta:** a divergência com o documento canônico descrita no aviso do topo
— 26 páginas para 15 slides em 6 seções, contra 16 slides em 3 seções —,
registrada como pendência 6 no fim de
[`../02_conteudo_slides.md`](../02_conteudo_slides.md). Fecha com a reconstrução
do deck sobre a estrutura vigente.

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
| `components/Rastreio.vue` | faixa de rastreio de seção, no topo |
| `components/Fonte.vue` | faixa de fontes, no rodapé |
| `components/Fig.vue` | figura com altura máxima controlada, sem distorção de proporção |
| `package.json`, `package-lock.json` | versões exatas: `@slidev/cli` 52.19.1, `slidev-theme-academic` 3.0.1 |
