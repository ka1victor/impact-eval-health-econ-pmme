"""Executa o pipeline validado do projeto no seu estado atual ponta a ponta.

Uso:

    python run_all.py              # pipeline inteiro
    python run_all.py --rdd-bolsa  # só a cadeia da RDD da bolsa (a07 a 10)

A opção `--rdd-bolsa` roda a cadeia sobre os insumos já versionados das etapas
anteriores (quadro de vagas, funil e tipologia do ciclo 1).
"""

from pathlib import Path
import argparse
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from utils.ambiente import verificar_ambiente  # noqa: E402

# Mudar STEPS exige regerar o manifesto A6: scripts/tema_trabalho/07_red_team_sintese.py
# deriva desta lista, por AST, a sequência de reprodução, e tests/test_red_team_a6.py
# confere as duas. Por isso cada passo é um caminho literal `ROOT / "..."`.
STEPS = [
    ROOT / "scripts" / "00_inventario_dados.py",
    ROOT / "scripts" / "02_auditar_fontes_pmme.py",
    ROOT / "scripts" / "aquisicao" / "01_congelar_ponte_cbo.py",
    ROOT / "scripts" / "aquisicao" / "02_consolidar_quadro_vagas.py",
    # Retirados em 18/10/2026: rdd_bolsa/01_auditar_regra_e_suporte.py e
    # rdd_bolsa/01_auditar_primeiro_estagio_publico.py usam como running variable
    # data/ivs_ipea_2010_municipios.csv, que não é o IVS do município
    # (docs/auditorias/16_ivs_2010_oficial_e_arquivo_local.md). Ver o bloco da RDD abaixo.
    #
    # a07 e a08 vêm antes da malha territorial desde 18/10/2026: 04_harmonizar e
    # tema_trabalho/01 leem o IVS 2010 oficial gravado pelo a08, e não mais o arquivo
    # local (docs/auditorias/19_reestimacao_base_oficial_failure_mode.md). Os dois só leem
    # insumos brutos; a ordem relativa da cadeia da RDD (a07 < a08 < 04 < ... < 10) fica igual.
    ROOT / "scripts" / "aquisicao" / "a07_adquirir_ivs_administrativo.py",
    ROOT / "scripts" / "aquisicao" / "a08_adquirir_ivs_2010_oficial.py",
    ROOT / "scripts" / "aquisicao" / "04_harmonizar_territorio_ibge.py",
    ROOT / "scripts" / "aquisicao" / "05_integrar_painel_analitico.py",
    ROOT / "scripts" / "avaliacao_impacto" / "run_pipeline_avaliacao.py",
    ROOT / "scripts" / "tema_trabalho" / "01_auditar_atracao_provimento_interior.py",
    ROOT / "scripts" / "tema_trabalho" / "02_reconciliar_funil_ciclo1.py",
    ROOT / "scripts" / "tema_trabalho" / "03_construir_tipologia_territorial.py",
    ROOT / "scripts" / "tema_trabalho" / "04_congelar_pre_analise.py",
    ROOT / "scripts" / "tema_trabalho" / "05_estimar_atracao.py",
    ROOT / "scripts" / "tema_trabalho" / "06_avaliar_provimento_cnes.py",
    ROOT / "scripts" / "tema_trabalho" / "06b_ameacas_a5_placebo_pretendencia_deslocamento.py",
    # A síntese A6 (07_red_team_sintese.py) roda depois da cadeia da RDD, cujas saídas lê.
    ROOT / "scripts" / "tema_trabalho" / "08_auditar_cutoff_selecao.py",
    ROOT / "scripts" / "tema_trabalho" / "09_estimar_cutoff_escore_estrito.py",
    ROOT / "scripts" / "tema_trabalho" / "09b_intervalos_exatos_escore.py",
    # RDD da bolsa, na ordem de dependência (docs/06_execucao/38_estado_e_pendencias_rdd_bolsa.md, §4).
    # A running variable é o IVS 2010 oficial do Ipea (a08). 07, 08a e 08 leem o funil do
    # ciclo 1 (tema_trabalho/02); 07, a tipologia (tema_trabalho/03); 08a, o quadro de
    # tratamento (aquisicao/02).
    #
    # Retirados em 18/10/2026, sem apagar os scripts nem as saídas já versionadas, que
    # ficam como registro superado (09, 09b e tema_trabalho/10 ainda leem a01b_*,
    # a01_* e portao_regra_ivs.json como histórico): rdd_bolsa/01b_reconstruir_regra_faixa.py lê
    # data/ivs_ipea_2010_municipios.csv como IVS 2010; rdd_bolsa/02_controlar_execucao_plano_causal.py
    # consolida os portões feitos com esse arquivo (01, 01_primeiro_estagio) e regrava
    # docs/06_execucao/33; rdd_bolsa/03_triagem_resposta_administrativa.py faz a triagem da
    # resposta ao pedido do escore ao MS, cancelado porque o escore é público (auditoria 16, §4).
    # a07 e a08, as aquisições desta cadeia, rodam no início (ver acima).
    ROOT / "scripts" / "rdd_bolsa" / "04_portao_r1_escore_administrativo.py",
    ROOT / "scripts" / "rdd_bolsa" / "04b_validar_ivs_oficial_escore_administrativo.py",
    ROOT / "scripts" / "rdd_bolsa" / "04c_identificar_recorte_arquivo_local.py",
    ROOT / "scripts" / "rdd_bolsa" / "05_estimar_E1_densidade.py",
    ROOT / "scripts" / "rdd_bolsa" / "06_estimar_E2_limites.py",
    ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py",
    ROOT / "scripts" / "rdd_bolsa" / "08a_reconstruir_proporcao_preenchida.py",
    ROOT / "scripts" / "rdd_bolsa" / "08_estimar_E4_proporcao.py",
    # E5, exploratório e pós-resultado: reproduz o principal do E3 e lê a proporção do 08a.
    ROOT / "scripts" / "rdd_bolsa" / "11_inferencia_alternativa.py",
    # O relatório para se a conferência do sinal não corresponder ao E3 atual.
    ROOT / "scripts" / "rdd_bolsa" / "09b_conferir_sinal.py",
    ROOT / "scripts" / "rdd_bolsa" / "09_gerar_relatorio_pdf.py",
    ROOT / "scripts" / "rdd_bolsa" / "10_galeria_figura_regra.py",
    # A6 lê R1, E3 e E5 e registra os hashes deles no manifesto.
    ROOT / "scripts" / "tema_trabalho" / "07_red_team_sintese.py",
    ROOT / "scripts" / "tema_trabalho" / "10_conferir_numeros_artigo.py",
    ROOT / "scripts" / "tema_trabalho" / "11_conferir_numeros_artigo_curto.py",
]

# Argumentos de linha de comando por passo. Ficam fora de STEPS porque os leitores
# por AST só aceitam caminhos; o manifesto A6 não os registra. O `--escore` do E3
# repete o padrão do script (IVS 2010 oficial, gravado pelo 04b) para deixar a
# running variable explícita; com o escore parcial do a07, o E3 para em
# AGUARDANDO_ESCORE_COMPLETO e apaga as saídas E3.
ARGUMENTOS = {
    ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py": [
        "--escore", "output/rdd_bolsa/escore_completo_ivs2010_oficial.csv",
    ],
}

AQUISICAO_RDD_BOLSA = (
    ROOT / "scripts" / "aquisicao" / "a07_adquirir_ivs_administrativo.py",
    ROOT / "scripts" / "aquisicao" / "a08_adquirir_ivs_2010_oficial.py",
)


def etapas(somente_rdd_bolsa: bool = False) -> list[Path]:
    """Passos a executar, na ordem de STEPS."""
    if not somente_rdd_bolsa:
        return list(STEPS)
    return [p for p in STEPS if p in AQUISICAO_RDD_BOLSA or p.parent == ROOT / "scripts" / "rdd_bolsa"]


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument(
        "--rdd-bolsa",
        action="store_true",
        help="executa só a cadeia da RDD da bolsa (a07 a 10), sobre os insumos versionados",
    )
    args = parser.parse_args(argv)

    # O pipeline grava artefato versionado, cuja proveniencia e ancorada em
    # SHA-256. Ambiente divergente reescreve arquivo em silencio, entao aqui a
    # verificacao aborta em vez de avisar.
    verificar_ambiente(estrito=True)

    alvo = "da cadeia da RDD da bolsa" if args.rdd_bolsa else "consolidado do PMM-E"
    print(f"Iniciando execução do pipeline {alvo}...\n")
    for script in etapas(args.rdd_bolsa):
        extras = ARGUMENTOS.get(script, [])
        print(f">> Executando {' '.join([str(script.relative_to(ROOT)), *extras])}...")
        subprocess.run([sys.executable, str(script), *extras], cwd=ROOT, check=True)
        print()

    destinos = (
        "output/aquisicao/ e output/rdd_bolsa/" if args.rdd_bolsa
        else "output/aquisicao/, output/avaliacao_impacto/, output/tema_trabalho/ e output/rdd_bolsa/"
    )
    print(f"Pipeline executado com sucesso! Artefatos consolidados salvos em {destinos}.")


if __name__ == "__main__":
    main()
