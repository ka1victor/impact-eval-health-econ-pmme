# Fonte de destaque do tema PMME: Oswald

Arquivos **versionados** da família [Oswald](https://github.com/googlefonts/OswaldFont)
(Vernon Adams e colaboradores), licença **SIL Open Font License 1.1**
([`OFL.txt`](OFL.txt)). A OFL permite redistribuir os arquivos com o projeto e
embuti-los no PDF.

| Arquivo | Uso no deck |
|---|---|
| `Oswald-Regular.ttf` | peso base da família (subseções não correntes da navbar) |
| `Oswald-Bold.ttf` | títulos de frame, capa, sumário, seção corrente da navbar |
| `Oswald-Medium.ttf`, `Oswald-SemiBold.ttf` | pesos intermediários, disponíveis para ajustes (`\fontseries{sb}` não é mapeado por padrão) |

**Por quê.** O título da peça oficial do Projeto Mais Médicos Especialistas é
composto numa grotesca condensada em caixa alta; a Oswald é a fonte livre que
reproduz esse desenho (comparação lado a lado em 16/09/2026: a TeX Gyre Heros
Condensed, alternativa em Type 1, é visivelmente mais larga e mais baixa).

**Como o tema a encontra.** O `.tex` declara
`\pmmefontes{docs/07_apresentacoes/banca1/deck_beamer/fontes/}` (caminho
relativo à raiz, como os demais assets). `beamerthemePMME.sty` carrega a família
com `fontspec` em `\AtBeginDocument`; se o diretório não existir, cai em
TeX Gyre Heros Cn com um aviso no log. Em **pdflatex** o `fontspec` não existe
e o tema usa sempre a Heros Condensed (`qhvc`).

A Oswald não tem itálico: onde o sumário pede negrito-itálico, o tema aplica
`FakeSlant=0.14` sobre o Bold.

**Proveniência.** Fonte é elemento de identidade visual, não saída de análise;
não passa pelo pipeline de `output/`.
