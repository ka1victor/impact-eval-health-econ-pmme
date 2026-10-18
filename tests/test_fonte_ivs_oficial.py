"""Nenhuma etapa do pipeline usa o arquivo de IVS errado, salvo para documentá-lo.

`data/ivs_ipea_2010_municipios.csv` não é o IVS do município (auditoria 16). Desde
18/10/2026 a malha, a tipologia A2, A4, A5 e a Tabela 1 do ciclo 1 usam a base
oficial do Ipea (a08) e o Censo 2022 (auditoria 19). Estes testes:

1. leem, por AST, os scripts do `run_all.py` e do pipeline de avaliação de impacto
   e reprovam qualquer um que construa o caminho do arquivo errado (ou de uma saída
   derivada dele) fora da lista de documentadores do failure mode;
2. conferem a malha e a tipologia contra a a08 e o Censo 2022, município a município;
3. conferem que os documentos e os artigos citam o ajuste completo corrigido e não o
   antigo, lido do registro de failure mode em `output/`.

Usa só dados observados do repositório; nada é sintético.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("run_all_fonte_ivs", ROOT / "run_all.py")
RA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RA)

ARQUIVO_ERRADO = {"ivs_ipea_2010_municipios.csv", "data/ivs_ipea_2010_municipios.csv"}
# Saídas de scripts retirados que usavam o arquivo errado como running variable.
DERIVADOS_ERRADOS = {
    "diagnostico_viabilidade_salario_ivs.json",
    "a01b_reconstrucao_regra_faixa.json",
    "portao_regra_ivs.json",
    "matriz_municipio_regra_ivs.csv",
    "a01_primeiro_estagio_publico.csv",
    "a03_matriz_regra_tratamento.json",
}

S = "scripts/"
# Leitores autorizados do arquivo errado no pipeline, e por quê.
LEITORES_AUTORIZADOS = {
    S + "00_inventario_dados.py": "inventário de data/, com rótulo FAILURE MODE",
    S + "02_auditar_fontes_pmme.py": "auditoria de fontes de data/, com rótulo FAILURE MODE",
    S + "rdd_bolsa/04_portao_r1_escore_administrativo.py": "compara o escore do MS com o arquivo (documenta a divergência)",
    S + "rdd_bolsa/04b_validar_ivs_oficial_escore_administrativo.py": "compara o arquivo com a base oficial",
    S + "rdd_bolsa/04c_identificar_recorte_arquivo_local.py": "reproduz a extração errada",
    S + "rdd_bolsa/06_estimar_E2_limites.py": "cenário 'informado' congelado, rotulado 'sem valor' no relatório",
    S + "rdd_bolsa/08_estimar_E4_proporcao.py": "cenário 'informado' congelado, rotulado 'sem valor' no relatório",
    S + "rdd_bolsa/09_gerar_relatorio_pdf.py": "figura comparativa do arquivo errado",
    S + "rdd_bolsa/10_galeria_figura_regra.py": "figura comparativa do arquivo errado",
    S + "tema_trabalho/07_red_team_sintese.py": "hash no manifesto A6, rotulado como failure mode",
}
# Leitores autorizados de saídas de scripts retirados: só como histórico rotulado.
LEITORES_DERIVADOS_AUTORIZADOS = {
    S + "rdd_bolsa/09_gerar_relatorio_pdf.py",
    S + "rdd_bolsa/09b_conferir_sinal.py",
    S + "tema_trabalho/10_conferir_numeros_artigo.py",
}


def scripts_do_pipeline() -> list[Path]:
    caminhos = list(RA.STEPS)
    # O pipeline de avaliação de impacto é um passo do run_all que roda outros scripts.
    arvore = ast.parse((ROOT / S / "avaliacao_impacto/run_pipeline_avaliacao.py").read_text(encoding="utf-8"))
    for no in ast.walk(arvore):
        if isinstance(no, ast.Constant) and isinstance(no.value, str) and no.value.endswith(".py") \
                and no.value[:2].isdigit():
            caminhos.append(ROOT / S / "avaliacao_impacto" / no.value)
    return caminhos


def constantes(path: Path) -> set[str]:
    arvore = ast.parse(path.read_text(encoding="utf-8"))
    return {no.value for no in ast.walk(arvore) if isinstance(no, ast.Constant) and isinstance(no.value, str)}


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT)).replace("\\", "/")


class TestPipelineNaoLeArquivoErrado(unittest.TestCase):
    def test_so_documentadores_constroem_o_caminho_do_arquivo_errado(self) -> None:
        leitores = {rel(p) for p in scripts_do_pipeline() if constantes(p) & ARQUIVO_ERRADO}
        intrusos = leitores - set(LEITORES_AUTORIZADOS)
        self.assertEqual(intrusos, set(), f"script do pipeline lê o arquivo de IVS errado: {sorted(intrusos)}")

    def test_lista_de_autorizados_nao_fica_obsoleta(self) -> None:
        for script in LEITORES_AUTORIZADOS:
            self.assertTrue(constantes(ROOT / script) & ARQUIVO_ERRADO, f"{script} não lê mais o arquivo; tire da lista")

    def test_saidas_de_scripts_retirados_so_como_historico(self) -> None:
        leitores = {rel(p) for p in scripts_do_pipeline() if constantes(p) & DERIVADOS_ERRADOS}
        self.assertEqual(leitores - LEITORES_DERIVADOS_AUTORIZADOS, set())

    def test_cadeia_territorial_le_a_base_oficial(self) -> None:
        for script in ("aquisicao/04_harmonizar_territorio_ibge.py", "tema_trabalho/03_construir_tipologia_territorial.py",
                       "tema_trabalho/01_auditar_atracao_provimento_interior.py",
                       "avaliacao_impacto/07_gerar_tabelas_e_figuras.py"):
            self.assertIn("a08_ivs_2010_oficial_municipio.csv", constantes(ROOT / S / script), script)

    def test_a08_roda_antes_de_quem_le_a_base_oficial(self) -> None:
        a08 = RA.STEPS.index(ROOT / S / "aquisicao/a08_adquirir_ivs_2010_oficial.py")
        for script in ("aquisicao/04_harmonizar_territorio_ibge.py", "tema_trabalho/01_auditar_atracao_provimento_interior.py",
                       "tema_trabalho/03_construir_tipologia_territorial.py"):
            self.assertLess(a08, RA.STEPS.index(ROOT / S / script), script)

    def test_auditoria_19_lista_os_autorizados(self) -> None:
        doc = (ROOT / "docs/auditorias/19_reestimacao_base_oficial_failure_mode.md").read_text(encoding="utf-8")
        for script in LEITORES_AUTORIZADOS:
            nome = Path(script).name
            prefixo = nome.split("_")[0]
            self.assertTrue(nome in doc or f"{Path(script).parent.name}/{prefixo}_" in doc
                            or f"{prefixo}_*" in doc, f"{script} ausente da auditoria 19")


class TestColunasTerritoriaisOficiais(unittest.TestCase):
    """Malha e tipologia regeneradas batem com a a08 e o Censo 2022 em todo município."""

    @classmethod
    def setUpClass(cls) -> None:
        a08 = pd.read_csv(ROOT / "output/aquisicao/a08_ivs_2010_oficial_municipio.csv", dtype={"co_ibge": str})
        a08["co_ibge_6d"] = a08["co_ibge"].str.zfill(6)
        cls.a08 = a08.set_index("co_ibge_6d")
        censo = pd.read_csv(ROOT / "output/aquisicao/populacao_censo2022_municipios.csv", dtype={"co_ibge_6d": str})
        cls.censo = censo.assign(co_ibge_6d=censo["co_ibge_6d"].str.zfill(6)).set_index("co_ibge_6d")
        cls.malha = pd.read_parquet(ROOT / "output/aquisicao/malha_municipios_regioes_saude.parquet").set_index("co_ibge_6d")
        cls.tip = pd.read_parquet(ROOT / "output/tema_trabalho/matriz_tipologia_territorial.parquet").set_index("co_ibge_6d")

    PARES = {"ivs_2010": "ivs", "ivs_infra_2010": "ivs_infraestrutura_urbana", "ivs_ch_2010": "ivs_capital_humano",
             "ivs_rt_2010": "ivs_renda_e_trabalho", "idhm_2010": "idhm", "populacao_2010": "populacao",
             "rdpc_2010": "renda_per_capita"}

    def _conferir(self, base: pd.DataFrame, nome: str) -> None:
        comum = base.index.intersection(self.a08.index)
        self.assertEqual(len(comum), len(self.a08), f"{nome}: municípios da a08 ausentes")
        for col, origem in self.PARES.items():
            np.testing.assert_array_equal(base.loc[comum, col].to_numpy(float), self.a08.loc[comum, origem].to_numpy(float),
                                          err_msg=f"{nome}.{col} difere da a08")

    def test_malha_igual_a_a08(self) -> None:
        self._conferir(self.malha, "malha")
        self.assertEqual(int(self.malha["populacao_2010"].sum()), int(self.a08["populacao"].sum()))

    def test_tipologia_igual_a_a08(self) -> None:
        self._conferir(self.tip, "tipologia")
        sem_ivs = self.tip.index.difference(self.a08.index)
        self.assertTrue(self.tip.loc[sem_ivs, "ivs_2010"].isna().all(), "município sem IVS oficial recebeu valor")

    def test_estoque_por_10k_usa_censo_2022(self) -> None:
        np.testing.assert_array_equal(self.tip["populacao_2022"].to_numpy(float),
                                      self.censo.loc[self.tip.index, "populacao_2022"].to_numpy(float))
        com = self.tip["estoque_especialistas_pre_12m_media"].notna()
        esperado = self.tip.loc[com, "estoque_especialistas_pre_12m_media"] / (self.tip.loc[com, "populacao_2022"] / 10000)
        np.testing.assert_allclose(self.tip.loc[com, "estoque_pre_por_10k"].astype(float), esperado, rtol=1e-12)

    def test_registro_a3_tem_emenda_datada(self) -> None:
        reg = json.loads((ROOT / "output/tema_trabalho/registro_pre_analise_atracao.json").read_text(encoding="utf-8"))
        emendas = {e["data"]: e for e in reg["emendas"]}
        self.assertIn("2026-10-18", emendas)
        self.assertIn("sem_mudanca_de_especificacao", emendas["2026-10-18"]["tipo"])


class TestNumerosAntigosSoComoFailureMode(unittest.TestCase):
    """O ajuste completo antigo não volta aos documentos vigentes nem aos artigos."""

    @classmethod
    def setUpClass(cls) -> None:
        tab = pd.read_csv(ROOT / "output/tema_trabalho/failure_mode_ivs_antes_depois.csv")
        cls.tab = tab
        linha = tab[(tab["bloco"] == "A4 ajuste completo") & (tab["termo"] == "estrato_metropolitano")].iloc[0]
        cls.antes = f"{100 * linha['coef_antes_failure_mode']:.1f}".replace(".", ",")
        cls.depois = f"{100 * linha['coef_depois']:.1f}".replace(".", ",")

    def test_registro_rotula_as_duas_colunas(self) -> None:
        self.assertEqual(set(self.tab["natureza_antes"]), {"FAILURE_MODE"})
        self.assertEqual(set(self.tab["natureza_depois"]), {"EMPIRICO"})

    def test_registro_bate_com_o_artefato_corrente(self) -> None:
        aj = pd.read_csv(ROOT / "output/tema_trabalho/A4_tabela_03b_ajuste_completo.csv").set_index("termo")
        linha = self.tab[(self.tab["bloco"] == "A4 ajuste completo") & (self.tab["termo"] == "estrato_metropolitano")].iloc[0]
        self.assertAlmostEqual(float(linha["coef_depois"]), float(aj.loc["estrato_metropolitano", "coef"]), places=12)

    def test_documentos_vigentes_citam_o_valor_corrigido(self) -> None:
        self.assertNotEqual(self.antes, self.depois)
        for rel_doc in ("docs/auditorias/09_red_team_atracao_provimento.md",
                        "docs/auditorias/09_matriz_afirmacao_evidencia_limite.md",
                        "docs/06_execucao/32_sintese_A6_resumo_intro_metodos_conclusao.md"):
            txt = (ROOT / rel_doc).read_text(encoding="utf-8")
            self.assertNotIn(f"{self.antes} pp no ajuste completo", txt, rel_doc)
            self.assertNotIn(f"Ajuste completo: +{self.antes}", txt, rel_doc)
            self.assertNotIn(f"{self.antes} pontos no ajuste completo", txt, rel_doc)
        for tex in ("paper_pmme_curto.tex", "paper_pmme_submission.tex"):
            txt = " ".join((ROOT / tex).read_text(encoding="utf-8").split())
            self.assertIn(f"metropolitano para {self.depois} pontos percentuais", txt, tex)
            self.assertNotIn(f"para {self.antes} pontos percentuais", txt, tex)

    def test_auditoria_19_rotula_a_coluna_antiga(self) -> None:
        doc = (ROOT / "docs/auditorias/19_reestimacao_base_oficial_failure_mode.md").read_text(encoding="utf-8")
        self.assertIn("FAILURE_MODE", doc)
        self.assertIn("Coef. antes (failure mode)", doc)


if __name__ == "__main__":
    unittest.main()
