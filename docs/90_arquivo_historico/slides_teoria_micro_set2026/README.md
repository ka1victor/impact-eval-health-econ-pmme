# Rascunhos de slides do modelo microeconômico (04/09/2026)

> **Estatuto:** arquivo histórico. São testes de formato feitos em 04/09/2026, antes da banca 1, para apresentar o
> modelo de [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md) na versão daquela data. Não acompanham
> as revisões posteriores do modelo e não são fonte de nada que se apresente.<br>
> **Versão vigente do que foi apresentado:** banca 1 em [`07_apresentacoes/banca1/`](../../07_apresentacoes/banca1/README.md);
> banca final em [`07_apresentacoes/banca_final/`](../../07_apresentacoes/banca_final/README.md).<br>
> **Entrou no Git em 18/11/2026**, quando o repositório foi organizado; até então os arquivos ficavam fora do
> controle de versão em `docs/02_teoria/`.

## O que há aqui

Uma variante por ferramenta testada, todas com o mesmo conteúdo de teoria:

| Arquivo | Ferramenta |
|---|---|
| `slides_teoria_micro_beamer.tex` / `.pdf` | Beamer |
| `slides_teoria_micro_beamer_curto.md`, `.tex` / `.pdf` | Beamer, versão curta |
| `slides_modelo_micro_madrid.tex` / `.pdf` | Beamer, tema Madrid |
| `slides_teoria_micro_katex.html` / `.pdf` | HTML com KaTeX |
| `slides_teoria_micro_md.pdf` | Markdown exportado |
| `slides_teoria_micro.pptx` / `.pdf` | PowerPoint |
| `slides_teoria_micro_presenton_executive.pptx` / `.pdf` | Presenton, template Executive |
| `prompt_presenton_teoria_micro.md` | prompt usado no Presenton |

## Para recompilar

- **`.tex`:** a figura vem de `figuras/curva_custo_laboral_burnout.png`, caminho relativo à pasta de origem. Ela
  continua em [`docs/02_teoria/figuras/`](../../02_teoria/figuras/). Para recompilar, copie a pasta `figuras/` para
  cá ou ajuste o caminho no `\includegraphics`.
- **`.html`:** carrega o KaTeX de uma cópia local em `katex/`, que fica fora do Git (`.gitignore`). Para abrir, use o
  PDF, ou troque os caminhos `katex/katex/...` pelos de um CDN.

Os subprodutos da compilação LaTeX (`.aux`, `.log`, `.nav`, `.out`, `.snm`, `.toc`) foram apagados.
