#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Build determinístico da galeria de componentes do tema PMME/Insper.
#
# Entrada : docs/07_apresentacoes/banca1/deck_beamer/exemplos_tema.tex
# Saída   : output/apresentacao_banca1/deck_beamer/exemplos_tema.pdf
#
# A galeria não é uma apresentação: é a referência visual do tema, para montar
# um deck novo. Não usa nenhuma figura nem nenhum número do repositório.
#
# Uso:  bash scripts/apresentacao/build_exemplos_tema.sh
# ---------------------------------------------------------------------------
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${RAIZ}"

export TEXINPUTS="docs/07_apresentacoes/banca1/deck_beamer//:${TEXINPUTS:-}"

if ! command -v lualatex >/dev/null 2>&1; then
  echo "ERRO: lualatex não encontrado (pacote texlive-luatex)." >&2
  exit 1
fi

TEX_REL="docs/07_apresentacoes/banca1/deck_beamer/exemplos_tema.tex"
OUT_REL="output/apresentacao_banca1/deck_beamer"
BASE="exemplos_tema"

if [[ ! -f "${TEX_REL}" ]]; then
  echo "ERRO: fonte não encontrada: ${TEX_REL}" >&2
  exit 1
fi

mkdir -p "${OUT_REL}"
export SOURCE_DATE_EPOCH=1789516800   # 2026-09-16T00:00:00Z
export FORCE_SOURCE_DATE=1

for passada in 1 2; do
  echo "== lualatex, passada ${passada}/2 =="
  if ! lualatex \
    -interaction=nonstopmode -halt-on-error -file-line-error \
    -output-directory="${OUT_REL}" "${TEX_REL}" \
    > "${OUT_REL}/${BASE}.passada${passada}.txt"
  then
    echo "ERRO de LaTeX na passada ${passada}. Últimas linhas:" >&2
    tail -n 40 "${OUT_REL}/${BASE}.passada${passada}.txt" >&2
    exit 1
  fi
done

falhou=0
for tipo in hbox vbox; do
  if grep -q "Overfull \\\\${tipo}" "${OUT_REL}/${BASE}.passada2.txt"; then
    echo "AVISO: Overfull \\${tipo} encontrados:"
    grep -n "Overfull \\\\${tipo}" "${OUT_REL}/${BASE}.passada2.txt" | head -n 20
    falhou=1
  fi
done
[[ "${falhou}" -eq 0 ]] && echo "OK: nenhum Overfull \\hbox ou \\vbox."

rm -f "${OUT_REL}/${BASE}".{aux,log,nav,out,snm,toc,vrb} \
      "${OUT_REL}/${BASE}".passada{1,2}.txt

echo "PDF gerado em: ${OUT_REL}/${BASE}.pdf"
