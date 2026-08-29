"""Executa o pipeline validado do projeto no seu estado atual."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
STEPS = [
    ROOT / "scripts" / "00_inventario_dados.py",
    ROOT / "scripts" / "02_auditar_fontes_pmme.py",
    ROOT / "scripts" / "03_planejar_aquisicao_cnes.py",
    ROOT / "scripts" / "aquisicao" / "a06_integrar_portao.py",
]


def main() -> None:
    for script in STEPS:
        print(f"Executando {script.relative_to(ROOT)}")
        subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)

    print("Pipeline concluído. Consulte os inventários e manifestos em output/.")


if __name__ == "__main__":
    main()
