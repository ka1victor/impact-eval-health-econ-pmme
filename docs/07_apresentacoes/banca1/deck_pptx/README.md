# Deck `.pptx` da banca 1 — template do autor

> **Classificação:** `base_modelo_economico.pptx` é **entrada**, não saída<br>
> **Script que monta:** [`../../../../scripts/apresentacao/montar_deck_banca1_pptx.py`](../../../../scripts/apresentacao/montar_deck_banca1_pptx.py)<br>
> **Saída:** `output/apresentacao_banca1/deck_banca1_modelo_economico.pptx`<br>
> **Proveniência:** [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md), seção 1-A<br>
> **Atualização:** 14 de setembro de 2026

---

## 1. O que é este diretório

`base_modelo_economico.pptx` é o **template desenhado pelo autor**: identidade
visual do Insper, capa, os seis slides de sumário, os slides de equação da
literatura e os gabaritos de slide de modelo, estes últimos preenchidos com `X`
onde o conteúdo entra.

Ele é **entrada do pipeline**, e por isso vive em `docs/` e não em `output/`. O
deck que vai à banca não é este arquivo: é a saída em
`output/apresentacao_banca1/deck_banca1_modelo_economico.pptx`, montada pelo
script sobre este template.

| Papel | Arquivo |
|---|---|
| Entrada — desenho | `docs/07_apresentacoes/banca1/deck_pptx/base_modelo_economico.pptx` |
| Entrada — conteúdo | `docs/07_apresentacoes/banca1/02_conteudo_slides.md` |
| Entrada — figuras | `output/apresentacao_banca1/*.png`, geradas por script versionado |
| Processo | `scripts/apresentacao/montar_deck_banca1_pptx.py` |
| Saída — deck | `output/apresentacao_banca1/deck_banca1_modelo_economico.pptx` |
| Saída — equações | `output/apresentacao_banca1/equacoes/*.png` |
| Saída — manifesto | `output/apresentacao_banca1/manifesto_deck_banca1.json` |

## 2. Não edite o template à mão para mudar conteúdo

O que o template carrega é **desenho**: paleta, tipografia, grade, posição dos
elementos e a moldura dos slides. O que ele **não** carrega é a versão vigente
do texto, dos números ou das figuras — isso é aplicado pelo script a cada
execução, e uma edição manual de conteúdo aqui seria sobrescrita na montagem
seguinte, ou pior, sobreviveria sem registro em nenhum manifesto.

Regras de edição:

- **Conteúdo** (texto, número, figura, equação, ordem dos slides) muda no
  documento canônico e no script. Nunca no `.pptx`, nem no de entrada nem no de
  saída.
- **Desenho** (cor, fonte, posição de um elemento do gabarito, um slide novo de
  moldura) pode mudar no template — é para isso que ele existe. Depois de mudar,
  rode o script: o manifesto registra o SHA-256 da base usada, e um template
  alterado sem nova montagem deixa deck e manifesto incoerentes.
- O `.pptx` de **saída** nunca se edita. Divergência entre deck e documento de
  conteúdo é erro do deck, e se corrige na entrada.

O script preserva o desenho e substitui o conteúdo: remove o slide vazio ao fim
do template, duplica dois gabaritos para os dois slides novos (equipe e capital;
o IVS no custo), reescreve títulos, caixas e figuras, corrige os erros de
digitação dos sumários do template (`porposto` → `proposto` e
`Téorica` → `Teórica`, além de completar `Modelo` para `Modelo Teórico`) e
reordena tudo na ordem
final de 21 slides. O número de correções de digitação aplicadas entra no
manifesto.

## 3. Como montar

A partir da raiz do repositório:

```bash
python3 scripts/apresentacao/gerar_figuras_banca1.py            # figuras de dados
python3 scripts/apresentacao/gerar_figura_custo_laboral_deck.py # curva de custo laboral do deck
python3 scripts/apresentacao/montar_deck_banca1_pptx.py         # deck
```

O script de montagem falha se uma figura esperada não existir em
`output/apresentacao_banca1/` — ele não desenha nada por conta própria. A
primeira execução das figuras de dados exige o denominador populacional, obtido
uma única vez por `scripts/aquisicao/06_adquirir_populacao_censo2022.py`.

**Dependências.** `python-pptx` e `lxml` estão em `requirements.txt` desde
16/09/2026. O que **não** está lá, porque são pacotes de sistema, e sem os quais
a montagem falha ou a conferência fica infiel:

| Pacote | Para quê | Sintoma se faltar |
|---|---|---|
| `texlive-latex-extra`, `dvipng` | renderizar as equações | o script aborta ao gerar o primeiro PNG |
| `cm-super` | fontes vetoriais do LaTeX | erro `Missing cm-super package, required by Matplotlib` |
| `fonts-montserrat` | a fonte do template | o deck monta, mas qualquer render de conferência troca a fonte e mede o texto errado |
| `libreoffice-impress` | converter o `.pptx` em PDF para conferir | `soffice` responde `source file could not be loaded` |

Num ambiente Debian ou Ubuntu:
`apt-get install -y texlive-latex-extra dvipng cm-super fonts-montserrat libreoffice-impress`.

**Dependências além de `requirements.txt`:** `python-pptx` e `lxml`, para
escrever o `.pptx`, e uma instalação de LaTeX com `dvipng` — o script usa
`text.usetex` do matplotlib, e não o `mathtext`, porque as equações pedem
construções que o `mathtext` não cobre, como o `\underbrace` rotulado da
decomposição do custo e da remuneração. Nenhum dos três está
declarado em `requirements.txt` hoje; quem for reproduzir precisa instalá-los.

Saída esperada: o deck, o diretório `equacoes/` e o manifesto. O script imprime
o caminho do deck, o número de slides e o número de correções de digitação.

## 4. Por que as equações novas são imagens, e não OMML

As equações que este script acrescenta são **PNG transparentes renderizados em
LaTeX**, posicionados como figura no slide. Elas não são OMML — não são a
equação nativa do PowerPoint, e não se clica nelas para editar.

A razão é de verificabilidade, não de preferência estética: o OMML nativo do
template não é verificável neste ambiente. Só o que o script escreve pode ser
conferido no render, de modo que uma equação nativa inserida por aqui iria ao
deck sem que ninguém pudesse checar se saiu certa. Uma imagem renderizada em
LaTeX, ao contrário, é gerada pelo próprio script, tem hash no manifesto e pode
ser aberta e conferida fora do PowerPoint.

Consequências práticas:

- Para corrigir uma equação, altere o LaTeX no script e rode-o de novo. Não
  edite a imagem nem o `.pptx`.
- As equações **da literatura** que já vinham no template continuam sendo o OMML
  original do autor. O script copia a árvore XML crua dos slides ao duplicá-los,
  e não a iteração de alto nível do `python-pptx`, justamente para não perder
  esse OMML, que mora dentro de `mc:AlternateContent`.
- Cada PNG de equação tem nome estável (`condicao_aceitacao`,
  `custo_por_ivs`, `decomposicao_custo`, `degrau_fronteira`,
  `derivada_hipotese`, `derivadas_lk`, `remuneracao_total`) e hash registrado no
  manifesto. A correspondência entre cada uma e a seção do documento de teoria
  que a origina está na seção 1-A de
  [`../03_proveniencia_figuras_e_numeros.md`](../03_proveniencia_figuras_e_numeros.md).

## 5. Proveniência

Todo número, figura e equação do deck segue a regra geral do projeto: o que
deriva de base do repositório é gerado por script versionado e lido de
`output/`. Gráfico produzido fora do pipeline não entra em apresentação.

A curva de custo laboral do deck
(`output/apresentacao_banca1/custo_laboral_deck.png`) é **ilustração conceitual
do modelo**: não tem escala cardinal nem dado observado, e não pode ser lida
como simulação, projeção ou magnitude. O registro está na seção 1-A do documento
de proveniência.

O manifesto `output/apresentacao_banca1/manifesto_deck_banca1.json` guarda o
SHA-256 do template e do deck, o hash de cada figura e de cada equação, o
roteiro numerado dos 21 slides e a nota de escopo: a banca 1 termina na
viabilidade empírica e não apresenta resultado de estimação.
