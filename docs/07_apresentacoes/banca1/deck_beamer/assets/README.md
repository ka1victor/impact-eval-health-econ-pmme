# Imagens da identidade visual do deck

Arquivos **não versionados** de imagem que a capa e o sumário usam. O deck
compila sem eles: cada um tem substituto desenhado em TikZ, de modo que o PDF
nunca sai com um buraco no lugar da imagem.

| Arquivo esperado | Onde aparece | Sem o arquivo |
|---|---|---|
| `logo_insper.png` | faixa branca inferior da capa, à esquerda | a palavra *Insper* composta em Heros Condensed |
| `capa_foto.jpg` | metade direita da capa, recortada | painel com degradê e chevrons da paleta |
| `sumario_fundo.jpg` | canto superior direito do sumário, esmaecido | padrão de chevrons a 12% de opacidade |

Os caminhos estão declarados no preâmbulo de
[`../banca1_beamer.tex`](../banca1_beamer.tex) (`\pmmelogo`, `\pmmefoto`,
`\pmmesumariofundo`), relativos à raiz do repositório. Para trocar de arquivo,
edite lá — não há caminho embutido nos `.sty`.

**Requisitos da foto da capa:** paisagem ou quadrada, com o motivo à direita ou
ao centro, altura ≥ 1000 px. A porção esquerda fica atrás do bloco azul.

**Proveniência.** Estas imagens são elementos de identidade visual, não saída de
análise: não representam dado do repositório e por isso não passam pelo
pipeline de `output/`. Qualquer **figura de resultado** continua sob a regra do
projeto — gerada por script versionado e lida de `output/`.
