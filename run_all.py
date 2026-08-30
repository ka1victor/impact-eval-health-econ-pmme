"""Executa o pipeline validado do projeto no seu estado atual ponta a ponta."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
STEPS = [
    ROOT / "scripts" / "00_inventario_dados.py",
    ROOT / "scripts" / "02_auditar_fontes_pmme.py",
    ROOT / "scripts" / "aquisicao" / "01_congelar_ponte_cbo.py",
    ROOT / "scripts" / "aquisicao" / "02_consolidar_quadro_vagas.py",
    ROOT / "scripts" / "aquisicao" / "04_harmonizar_territorio_ibge.py",
    ROOT / "scripts" / "aquisicao" / "05_integrar_painel_analitico.py",
    ROOT / "scripts" / "avaliacao_impacto" / "run_pipeline_avaliacao.py",
]


def main() -> None:
    print("Iniciando execução do pipeline consolidado do PMM-E...\n")
    for script in STEPS:
        print(f">> Executando {script.relative_to(ROOT)}...")
        subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
        print()

    print("Pipeline executado com sucesso! Todos os artefatos consolidados foram salvos em output/avaliacao_impacto/ e output/aquisicao/.")


if __name__ == "__main__":
    main()
