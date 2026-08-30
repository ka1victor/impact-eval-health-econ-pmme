"""run_pipeline_avaliacao.py — Execução Completa Ponta a Ponta do Pipeline de Avaliação de Impacto.

Este script orquestra e executa sequencialmente todos os passos da avaliação de impacto
do PMM-E, garantindo que todos os artefatos, dados, tabelas, figuras e relatórios sejam
gerados e persistidos no diretório consolidado `output/avaliacao_impacto/`.

Sequência de Execução:
1. `01_avaliar_portao_relevancia.py`
2. `02_construir_paineis_analiticos.py`
3. `03_estimar_ddd_estatica.py`
4. `04_estimar_estudo_evento.py`
5. `05_estimar_mecanismos_e_retencao.py`
6. `06_avaliar_robustez_e_redistribuicao.py`
7. `07_gerar_tabelas_e_figuras.py`
8. `08_gerar_nota_tecnica_final.py`

Entregáveis:
- Toda a pasta `output/avaliacao_impacto/` (dados, modelos, tabelas, figuras, relatorios).
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "scripts" / "avaliacao_impacto"
OUTPUT_DIR = ROOT / "output" / "avaliacao_impacto"

STEPS = [
    SCRIPTS_DIR / "01_avaliar_portao_relevancia.py",
    SCRIPTS_DIR / "02_construir_paineis_analiticos.py",
    SCRIPTS_DIR / "03_estimar_ddd_estatica.py",
    SCRIPTS_DIR / "04_estimar_estudo_evento.py",
    SCRIPTS_DIR / "05_estimar_mecanismos_e_retencao.py",
    SCRIPTS_DIR / "06_avaliar_robustez_e_redistribuicao.py",
    SCRIPTS_DIR / "07_gerar_tabelas_e_figuras.py",
    SCRIPTS_DIR / "08_gerar_nota_tecnica_final.py",
]


def main() -> None:
    start_time = time.time()
    print("================================================================================")
    print("   PIPELINE DE AVALIAÇÃO CAUSAL DE IMPACTO — PMM-E (LEI Nº 15.233/2025)        ")
    print("================================================================================\n")
    print(f"Diretório Raiz: {ROOT}")
    print(f"Diretório de Destino: {OUTPUT_DIR}\n")

    for i, script in enumerate(STEPS, 1):
        rel_path = script.relative_to(ROOT)
        print(f"[{i}/{len(STEPS)}] Executando {rel_path}...")
        t0 = time.time()
        res = subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
        elapsed = time.time() - t0
        print(f"      Concluído em {elapsed:.2f}s\n")

    total_elapsed = time.time() - start_time
    print("================================================================================")
    print(f"   PIPELINE CONCLUÍDO COM SUCESSO EM {total_elapsed:.2f} SEGUNDOS!            ")
    print(f"   Artefatos consolidados salvos em: {OUTPUT_DIR}")
    print("================================================================================")


if __name__ == "__main__":
    main()
