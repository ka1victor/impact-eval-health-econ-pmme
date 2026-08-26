"""Script mestre para reproducao integral dos resultados do Mais Medicos Especialistas (PMM-E).

Executa sequencialmente:
1. scripts/01_estima_rdd_completo.py (Primeiro estagio e elasticidades RDD)
2. scripts/02_estima_resolutividade_local_global.py (Decomposicao de fluxo e resolutividade)
3. scripts/03_analise_descritiva_pacientes.py (Estatisticas descritivas clinicas)
"""
import os
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(RAIZ, "scripts")

def executa_etapa(nome_script, descricao):
    print("\n" + "=" * 80)
    print(f" EXECUTANDO: {descricao}")
    print(f" Script: {nome_script}")
    print("=" * 80)
    
    caminho = os.path.join(SCRIPTS, nome_script)
    t0 = time.time()
    res = subprocess.run([sys.executable, caminho], cwd=RAIZ)
    dt = time.time() - t0
    
    if res.returncode == 0:
        print(f"\n[SUCESSO] {nome_script} finalizado em {dt:.2f}s.")
    else:
        print(f"\n[ERRO] Falha na execucao de {nome_script} (codigo de saida: {res.returncode}).")
        sys.exit(res.returncode)

def main():
    print("*" * 80)
    print("   PROGRAMA MAIS MEDICOS ESPECIALISTAS (PMM-E): REPRODUCAO INTEGRAL")
    print("*" * 80)
    
    t_inicio = time.time()
    
    executa_etapa("01_estima_rdd_completo.py", "1. Primeiro Estagio, RDD e Elasticidade-Salario")
    executa_etapa("02_estima_resolutividade_local_global.py", "2. Decomposicao de Resolutividade Local vs. Global (SIA/SIH)")
    executa_etapa("03_analise_descritiva_pacientes.py", "3. Estatisticas Descritivas Clinicas de Atendimento")
    
    t_total = time.time() - t_inicio
    print("\n" + "*" * 80)
    print(f" PIPELINE COMPLETO EXECUTADO COM SUCESSO EM {t_total:.2f}s!")
    print(f" Todos os resultados foram consolidados na pasta 'output/'.")
    print("*" * 80)

if __name__ == "__main__":
    main()
