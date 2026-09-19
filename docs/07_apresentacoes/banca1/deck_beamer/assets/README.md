# Imagens opcionais do deck

Arquivos **não versionados** de imagem que a capa alternativa (`\pmmecapa`, no
visual do banner do PMM-E) e o sumário podem usar. O deck compila sem eles: cada
um tem substituto desenhado em TikZ, de modo que o PDF nunca sai com um buraco
no lugar da imagem. O logo e o gráfico institucional do Insper **estão**
versionados, em [`../insper/`](../insper/README.md).

| Arquivo esperado | Onde aparece | Sem o arquivo |
|---|---|---|
| `capa_foto.jpg` | metade direita da capa alternativa `\pmmecapa`, recortada | painel com degradê e chevrons da paleta |
| `sumario_fundo.jpg` | canto superior direito do sumário, esmaecido | listras diagonais do gráfico institucional do Insper |

Os caminhos estão declarados no preâmbulo de
[`../banca1_beamer.tex`](../banca1_beamer.tex) (`\pmmefoto`,
`\pmmesumariofundo`), relativos à raiz do repositório. Para trocar de arquivo,
edite lá — não há caminho embutido nos `.sty`.

**Requisitos da foto da capa:** paisagem ou quadrada, com o motivo à direita ou
ao centro, altura ≥ 1000 px. A porção esquerda fica atrás do bloco azul.

**Imagem de fundo em qualquer frame.** Além dos três arquivos acima, qualquer
PNG/JPG/PDF pode servir de fundo esmaecido a um frame com `\pmmefundo` (ver
[`../README.md`](../README.md), seção 3.1). Coloque o arquivo aqui e passe o
caminho relativo à raiz.

**Proveniência.** Estas imagens são elementos de identidade visual, não saída de
análise: não representam dado do repositório e por isso não passam pelo
pipeline de `output/`. Qualquer **figura de resultado** continua sob a regra do
projeto — gerada por script versionado e lida de `output/`.
