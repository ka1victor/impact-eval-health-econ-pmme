# Fontes do tema PMME

Arquivos **versionados**, todos sob a **SIL Open Font License 1.1**, que permite
redistribuí-los com o projeto e embuti-los no PDF. O `.tex` declara o diretório
com `\pmmefontes{docs/07_apresentacoes/banca1/deck_beamer/fontes/}` (caminho
relativo à raiz, como os demais assets); `beamerthemePMME.sty` carrega as
famílias com `fontspec` em `\AtBeginDocument`. Em **pdflatex** o `fontspec` não
existe e o tema usa os equivalentes Type 1 indicados.

| Família | Arquivos | Licença | Uso no deck | Em pdflatex |
|---|---|---|---|---|
| **Inter** (rsms) | `Inter-{Regular,Italic,SemiBold,Bold,BoldItalic}.otf` | [`LICENSE-Inter.txt`](LICENSE-Inter.txt) | corpo do texto, navbar, rodapé — a fonte de corpo do tema oficial do Insper | Latin Modern Sans |
| **Playfair Display** (Claus Eggers Sørensen) | `PlayfairDisplay-{Regular,Bold,Italic,BoldItalic}.ttf` | [`OFL-Playfair.txt`](OFL-Playfair.txt) | `\pmmeDisplay`: títulos de frame, capa, sumário, divisórias, títulos de `pmmeparte`; substitui a GT Ultra Fine (comercial) do tema oficial | TeX Gyre Pagella |
| **Oswald** (Vernon Adams e col.) | `Oswald-{Regular,Medium,SemiBold,Bold}.ttf` | [`OFL-Oswald.txt`](OFL-Oswald.txt) | `\pmmeCondensada`: só a capa alternativa `\pmmecapa`, que reproduz o banner do PMM-E | TeX Gyre Heros Condensed |

**Playfair Display: como foi gerada.** O repositório da fonte
([clauseggers/Playfair](https://github.com/clauseggers/Playfair), v2.2) publica
só fontes variáveis (eixos `opsz`, `wdth`, `wght`). Os quatro arquivos aqui são
instâncias estáticas geradas com `fontTools.varLib.instancer` em
`opsz=48, wdth=100` e `wght=400/700`, nome interno *Playfair Display PMME*. A
OFL permite a derivação; o nome reservado *Playfair* não é usado como nome de
família da instância.

**Oswald sem itálico.** Onde a capa alternativa pede itálico, o tema aplica
`FakeSlant=0.14` sobre o Bold.

**Tamanho de corpo.** A Inter tem altura-x maior e é mais larga que a Latin
Modern; o deck compila a **10pt** (antes 11pt) para ocupar na tela o mesmo que
antes e manter os frames compostos cabendo.

**Proveniência.** Fonte é elemento de identidade visual, não saída de análise;
não passa pelo pipeline de `output/`.
