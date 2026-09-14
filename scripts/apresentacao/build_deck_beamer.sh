#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Build determinístico do deck Beamer (tema Warsaw) da banca 1.
#
# Entrada : docs/07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex
# Figuras : output/apresentacao_banca1/*.png
#           docs/02_teoria/figuras/curva_custo_laboral_burnout.png
# Saída   : output/apresentacao_banca1/deck_beamer/banca1_warsaw.pdf
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

TEX_REL="docs/07_apresentacoes/banca1/deck_beamer/banca1_warsaw.tex"
OUT_REL="output/apresentacao_banca1/deck_beamer"
BASE="banca1_warsaw"

if [[ ! -f "${TEX_REL}" ]]; then
  echo "ERRO: fonte não encontrada: ${TEX_REL}" >&2
  exit 1
fi

for fig in \
  output/apresentacao_banca1/oferta_pre_por_faixa.png \
  output/apresentacao_banca1/retaguarda_por_faixa.png \
  output/apresentacao_banca1/vagas_ciclo1_por_regiao.png \
  output/apresentacao_banca1/bolsa_por_faixa.png \
  output/apresentacao_banca1/preenchimento_ciclo1.png \
  docs/02_teoria/figuras/curva_custo_laboral_burnout.png
do
  if [[ ! -f "${fig}" ]]; then
    echo "ERRO: figura ausente: ${fig}" >&2
    echo "      Regere com: python3 scripts/apresentacao/gerar_figuras_banca1.py" >&2
    exit 1
  fi
done

mkdir -p "${OUT_REL}"

# Reprodutibilidade: congela a data embutida no PDF.
export SOURCE_DATE_EPOCH=1789344000   # 2026-09-14T00:00:00Z
export FORCE_SOURCE_DATE=1

# Duas passadas: a segunda resolve \inserttotalframenumber.
for passada in 1 2; do
  echo "== pdflatex, passada ${passada}/2 =="
  if ! pdflatex \
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
