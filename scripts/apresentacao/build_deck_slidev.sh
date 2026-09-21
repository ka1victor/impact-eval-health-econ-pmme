#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Build determinístico do deck Slidev da banca 1.
#
# Uso, a partir da raiz do repositório:
#   bash scripts/apresentacao/build_deck_slidev.sh            # PDF
#   bash scripts/apresentacao/build_deck_slidev.sh png        # PDF + PNG por página
#
# Saídas:
#   output/apresentacao_banca1/deck_slidev/banca1_slidev.pdf
#   output/apresentacao_banca1/deck_slidev/png/   (apenas com o argumento png)
#
# Proveniência das figuras: nenhuma imagem é gerada, editada ou copiada para
# dentro do versionamento. As figuras vivem em `output/apresentacao_banca1/`;
# este script apenas materializa links simbólicos
# para elas em `<deck>/public/fig/`, diretório de trabalho ignorado pelo Git.
# ---------------------------------------------------------------------------

set -euo pipefail

# Raiz do repositório = duas pastas acima deste script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${ROOT}"

DECK="docs/07_apresentacoes/banca1/deck_slidev"
DEST="output/apresentacao_banca1/deck_slidev"
PDF="${DEST}/banca1_slidev.pdf"

FORMATO="${1:-pdf}"

# O Chromium já está instalado na imagem; nunca baixar navegador.
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}"
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export TZ=UTC

# --- 1. dependências -------------------------------------------------------
if [ ! -d "${DECK}/node_modules" ]; then
  echo "[1/4] instalando dependências fixadas em package-lock.json"
  npm ci --no-audit --no-fund --prefix "${DECK}"
else
  echo "[1/4] node_modules presente; pulando instalação"
fi

# --- 2. figuras em diretório de trabalho não versionado --------------------
echo "[2/4] publicando links simbólicos das figuras em ${DECK}/public/fig"
rm -rf "${DECK}/public/fig"
mkdir -p "${DECK}/public/fig"

link_figura() {
  local origem="$1"
  local nome
  nome="$(basename "${origem}")"
  if [ ! -f "${ROOT}/${origem}" ]; then
    echo "ERRO: figura ausente: ${origem}" >&2
    exit 1
  fi
  ln -sfn "${ROOT}/${origem}" "${DECK}/public/fig/${nome}"
}

# As sete figuras do documento canônico (slides 4, 5 e 7).
link_figura output/apresentacao_banca1/especialistas_por_uf_extremos.png
link_figura output/apresentacao_banca1/deslocamento_por_regiao.png
link_figura output/apresentacao_banca1/dupla_pratica_cirurgioes.png
link_figura output/apresentacao_banca1/bolsa_por_faixa.png
link_figura output/apresentacao_banca1/oferta_pre_por_faixa.png
link_figura output/apresentacao_banca1/retaguarda_por_faixa.png
link_figura output/apresentacao_banca1/preenchimento_ciclo1.png

# --- 3. exportação ---------------------------------------------------------
# `slidev export` sobe um servidor Vite próprio. Na primeira execução depois de
# qualquer mudança de dependência, o Vite reotimiza o bundle e recarrega a
# página no meio da espera do Playwright, que tem limite fixo de 30 s. O
# resultado é um timeout espúrio. A primeira tentativa aquece o cache do
# otimizador; a segunda exporta. Por isso a função tenta até três vezes.
mkdir -p "${DEST}"

exportar() {
  local formato="$1"
  local destino="$2"
  local tentativa
  for tentativa in 1 2 3; do
    if ( cd "${ROOT}/${DECK}" && ./node_modules/.bin/slidev export slides.md \
        --format "${formato}" \
        --per-slide \
        --output "${destino}" \
        --timeout 120000 \
        --dark false ); then
      return 0
    fi
    echo "      tentativa ${tentativa} falhou (cache do Vite frio); repetindo" >&2
  done
  echo "ERRO: exportação ${formato} falhou após três tentativas" >&2
  return 1
}

echo "[3/4] exportando PDF"
exportar pdf "${ROOT}/${PDF}"

if [ "${FORMATO}" = "png" ]; then
  echo "[3b/4] exportando PNG por página"
  rm -rf "${DEST}/png"
  mkdir -p "${DEST}/png"
  exportar png "${ROOT}/${DEST}/png"
fi

# --- 4. conferência --------------------------------------------------------
echo "[4/4] pronto"
ls -l "${PDF}"
