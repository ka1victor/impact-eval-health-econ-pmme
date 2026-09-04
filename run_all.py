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
    ROOT / "scripts" / "tema_trabalho" / "01_auditar_atracao_provimento_interior.py",
    ROOT / "scripts" / "tema_trabalho" / "02_reconciliar_funil_ciclo1.py",
    ROOT / "scripts" / "tema_trabalho" / "03_construir_tipologia_territorial.py",
    ROOT / "scripts" / "tema_trabalho" / "04_congelar_pre_analise.py",
    ROOT / "scripts" / "tema_trabalho" / "05_estimar_atracao.py",
    ROOT / "scripts" / "tema_trabalho" / "06_avaliar_provimento_cnes.py",
    ROOT / "scripts" / "tema_trabalho" / "07_red_team_sintese.py",
    ROOT / "scripts" / "tema_trabalho" / "08_auditar_cutoff_selecao.py",
]


def main() -> None:
    print("Iniciando execução do pipeline consolidado do PMM-E...\n")
    for script in STEPS:
        print(f">> Executando {script.relative_to(ROOT)}...")
        subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)
        print()

    print("Pipeline executado com sucesso! Artefatos consolidados salvos em output/aquisicao/, output/avaliacao_impacto/ e output/tema_trabalho/.")


if __name__ == "__main__":
    main()
