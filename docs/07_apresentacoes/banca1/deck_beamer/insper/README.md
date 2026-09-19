# Marca institucional do Insper

Arquivos copiados do tema oficial do Insper para Quarto/reveal.js,
[padsInsper/quarto-insper-theme](https://github.com/padsInsper/quarto-insper-theme)
(licença MIT, em [`LICENSE-quarto-insper-theme.md`](LICENSE-quarto-insper-theme.md)).
O tema PMME reproduz dele a identidade: página branca, texto preto, serifa de
exibição nos títulos, vermelho `#E50505` como acento e o gráfico institucional
na capa.

| Arquivo | Onde aparece | Sem o arquivo |
|---|---|---|
| `logo.png` | rodapé de todos os frames, à direita; faixa da capa alternativa `\pmmecapa` | a palavra *Insper* composta em Playfair Display |
| `insper-bg.png` | metade direita da capa `\inspercapa` (wordmark, quadrados preto e vermelho sobre listras) | quadrados e listras desenhados em TikZ |

Os caminhos estão declarados no preâmbulo de
[`../banca1_beamer.tex`](../banca1_beamer.tex) (`\pmmeinsperlogo`,
`\pmmeinsperfundo`), relativos à raiz do repositório.

**Fonte dos títulos.** O tema oficial usa a *GT Ultra Fine* (Grilli Type), que
é comercial e não pode ser redistribuída neste repositório. No lugar dela o
deck usa a *Playfair Display* (OFL), serifa de exibição de alto contraste com
desenho próximo — ver [`../fontes/README.md`](../fontes/README.md).

**Proveniência.** Marca e gráfico são elementos de identidade visual, não saída
de análise; não passam pelo pipeline de `output/`.
