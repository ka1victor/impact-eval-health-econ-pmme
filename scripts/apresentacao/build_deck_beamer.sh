#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Build determinístico do deck Beamer (tema PMME) da banca 1, em LuaLaTeX.
#
# Entrada : docs/07_apresentacoes/banca1/deck_beamer/banca1_beamer.tex
# Figuras : output/apresentacao_banca1/*.png (as sete usadas pelo deck)
# Saída   : output/apresentacao_banca1/deck_beamer/banca1_beamer.pdf
#
# Todos os caminhos são relativos à raiz do repositório; o script se posiciona
# nela antes de compilar, de modo que \graphicspath resolva as figuras.
#
# Uso:  bash scripts/apresentacao/build_deck_beamer.sh
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${RAIZ}"

# O tema PMME (beamertheme*.sty e pacotes auxiliares) mora ao lado do .tex.
# A fonte de destaque (fontes/Oswald-*.ttf) é resolvida pelo caminho declarado
# no .tex (\pmmefontes), relativo à raiz — por isso o cd acima é obrigatório.
export TEXINPUTS="docs/07_apresentacoes/banca1/deck_beamer//:${TEXINPUTS:-}"

if ! command -v lualatex >/dev/null 2>&1; then
  echo "ERRO: lualatex não encontrado (pacote texlive-luatex)." >&2
  exit 1
fi

TEX_REL="docs/07_apresentacoes/banca1/deck_beamer/banca1_beamer.tex"
OUT_REL="output/apresentacao_banca1/deck_beamer"
BASE="banca1_beamer"

if [[ ! -f "${TEX_REL}" ]]; then
  echo "ERRO: fonte não encontrada: ${TEX_REL}" >&2
  exit 1
fi

# As sete figuras que o deck inclui (documento canônico, slides 4, 5 e 7).
for fig in \
  output/apresentacao_banca1/especialistas_por_uf_extremos.png \
  output/apresentacao_banca1/deslocamento_por_regiao.png \
  output/apresentacao_banca1/dupla_pratica_cirurgioes.png \
  output/apresentacao_banca1/bolsa_por_faixa.png \
  output/apresentacao_banca1/oferta_pre_por_faixa.png \
  output/apresentacao_banca1/retaguarda_por_faixa.png \
  output/apresentacao_banca1/preenchimento_ciclo1.png
do
  if [[ ! -f "${fig}" ]]; then
    echo "ERRO: figura ausente: ${fig}" >&2
    echo "      Regere com: python3 scripts/apresentacao/gerar_figuras_banca1.py" >&2
    exit 1
  fi
done

mkdir -p "${OUT_REL}"

# Reprodutibilidade: congela a data embutida no PDF.
export SOURCE_DATE_EPOCH=1789516800   # 2026-09-16T00:00:00Z
export FORCE_SOURCE_DATE=1

# Duas passadas: a segunda resolve \inserttotalframenumber e as posições
# 'remember picture' da capa e do sumário.
for passada in 1 2; do
  echo "== lualatex, passada ${passada}/2 =="
  if ! lualatex \
    -interaction=nonstopmode \
    -halt-on-error \
    -file-line-error \
    -output-directory="${OUT_REL}" \
    "${TEX_REL}" > "${OUT_REL}/${BASE}.passada${passada}.txt"
  then
    echo "ERRO de LaTeX na passada ${passada}. Últimas linhas:" >&2
    tail -n 40 "${OUT_REL}/${BASE}.passada${passada}.txt" >&2
    echo "Log completo: ${OUT_REL}/${BASE}.log" >&2
    exit 1
  fi
done

# Relatório de composição. O \hbox pega texto que vaza pela lateral; o \vbox,
# frame cujo conteúdo não cabe na altura e invade o rodapé — o modo de falha
# típico quando se comprime conteúdo em menos frames.
falhou=0
if grep -q "Overfull \\\\hbox" "${OUT_REL}/${BASE}.passada2.txt"; then
  echo "AVISO: Overfull \\hbox encontrados:"
  grep "Overfull \\\\hbox" "${OUT_REL}/${BASE}.passada2.txt" || true
  falhou=1
fi
if grep -q "Overfull \\\\vbox" "${OUT_REL}/${BASE}.passada2.txt"; then
  echo "AVISO: Overfull \\vbox encontrados (conteúdo estourando a altura do frame):"
  grep -c "Overfull \\\\vbox" "${OUT_REL}/${BASE}.passada2.txt" | \
    sed 's/^/  ocorrências: /'
  grep -n "Overfull \\\\vbox" "${OUT_REL}/${BASE}.passada2.txt" | head -n 40 || true
  falhou=1
fi
if [[ "${falhou}" -eq 0 ]]; then
  echo "OK: nenhum Overfull \\hbox ou \\vbox."
fi

# Limpeza dos auxiliares.
rm -f \
  "${OUT_REL}/${BASE}.aux" \
  "${OUT_REL}/${BASE}.log" \
  "${OUT_REL}/${BASE}.nav" \
  "${OUT_REL}/${BASE}.out" \
  "${OUT_REL}/${BASE}.snm" \
  "${OUT_REL}/${BASE}.toc" \
  "${OUT_REL}/${BASE}.vrb" \
  "${OUT_REL}/${BASE}.passada1.txt" \
  "${OUT_REL}/${BASE}.passada2.txt"

echo "PDF gerado em: ${OUT_REL}/${BASE}.pdf"
