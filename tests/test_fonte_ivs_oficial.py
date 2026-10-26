"""Nenhuma etapa do pipeline usa o arquivo de IVS errado, salvo para documentá-lo.

`data/ivs_ipea_2010_municipios.csv` não é o IVS do município (auditoria 16). Desde
18/10/2026 a malha, a tipologia A2, A4, A5 e a Tabela 1 do ciclo 1 usam a base
oficial do Ipea (a08) e o Censo 2022 (auditoria 19). Estes testes:

1. leem, por AST, os scripts do `run_all.py` e do pipeline de avaliação de impacto
   e reprovam qualquer um que construa o caminho do arquivo errado (ou de uma saída
   derivada dele) fora da lista de documentadores do failure mode;
2. conferem a malha e a tipologia contra a a08 e o Censo 2022, município a município;
3. conferem que os documentos e os artigos citam o ajuste completo corrigido e não o
   antigo, lido do registro de failure mode em `output/`;
4. varrem o texto bruto de todo `.py` sob `scripts/` e na raiz, com contagem exata de
   ocorrências autorizada por script, e provam a guarda injetando violações numa
   cópia temporária fora do repositório.

Usa só dados observados do repositório. Os únicos trechos fabricados são as
violações injetadas na cópia temporária do teste 4, apagada ao final.
"""

from __future__ import annotations

import ast
import fnmatch
import importlib.util
import io
import json
import re
import shutil
import tempfile
import tokenize
import unittest
import warnings
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
    S + "rdd_bolsa/09_gerar_relatorio_pdf.py": "figura comparativa do arquivo errado",
    S + "rdd_bolsa/10_galeria_figura_regra.py": "figura comparativa do arquivo errado",
    S + "tema_trabalho/07_red_team_sintese.py": "hash no manifesto A6, rotulado como failure mode",
}
# Leitores autorizados de saídas de scripts retirados: só como histórico rotulado.
LEITORES_DERIVADOS_AUTORIZADOS = {
    S + "rdd_bolsa/09_gerar_relatorio_pdf.py",
    S + "rdd_bolsa/09b_conferir_sinal.py",
    S + "tema_trabalho/10_conferir_numeros_artigo.py",
    # E9 lê de a03_matriz_regra_tratamento.json só o bloco mapeamento_regras_por_edital
    # (faixa impressa -> bolsa anunciada, transcrito dos editais), nenhum IVS, e o confere
    # contra a grade da FAQ (a04); declarado no manifesto do E9.
    S + "rdd_bolsa/16_estimar_E9_escolha.py",
}


# Pastas varridas além do run_all: o ciclo 3 (C3-03 lê a malha) e as figuras da banca.
PASTAS_EXTRAS = ("avaliacao_ciclo3", "apresentacao")
# Painéis versionados que guardam colunas territoriais da malha antiga (não regeneráveis
# sem o CNES mensal). Quem os lê e usa essas colunas tem de repô-las da fonte oficial.
PAINEIS_COM_COLUNAS_ANTIGAS = {"painel_municipio_curso_mes.parquet", "A5_painel_T0.parquet",
                               "painel_municipio_curso_mensal.parquet"}
COLUNAS_TERRITORIAIS = {"ivs_2010", "ivs_categoria", "populacao_2010"}
FONTES_OFICIAIS = {"a08_ivs_2010_oficial_municipio.csv", "malha_municipios_regioes_saude.parquet",
                   "matriz_tipologia_territorial.parquet", "painel_municipios_regioes.parquet"}


def scripts_do_pipeline() -> list[Path]:
    caminhos = list(RA.STEPS)
    for pasta in PASTAS_EXTRAS:
        caminhos += sorted((ROOT / S / pasta).glob("*.py"))
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

    def test_quem_le_painel_com_colunas_antigas_repoe_da_fonte_oficial(self) -> None:
        for p in scripts_do_pipeline():
            c = constantes(p)
            if c & PAINEIS_COM_COLUNAS_ANTIGAS and c & COLUNAS_TERRITORIAIS:
                self.assertTrue(c & FONTES_OFICIAIS,
                                f"{rel(p)} usa {sorted(c & COLUNAS_TERRITORIAIS)} de painel com colunas da malha antiga "
                                "sem repô-las da fonte oficial")

    def test_e2_e4_sem_o_cenario_informado(self) -> None:
        e2 = pd.read_csv(ROOT / "output/rdd_bolsa/E2_limites.csv")
        e4 = pd.read_csv(ROOT / "output/rdd_bolsa/E4_estimativas.csv")
        self.assertNotIn("informado", set(e2["cenario"]))
        self.assertNotIn("informado", set(e4["cenario_ou_espec"]))
        for f in ("E2_limites_resumo.json", "E4_resumo.json"):
            txt = (ROOT / "output/rdd_bolsa" / f).read_text(encoding="utf-8")
            self.assertNotIn('"data/ivs_ipea_2010_municipios.csv"', txt, f)

    def test_censo_2022_roda_antes_da_malha(self) -> None:
        censo = RA.STEPS.index(ROOT / S / "aquisicao/06_adquirir_populacao_censo2022.py")
        self.assertLess(censo, RA.STEPS.index(ROOT / S / "aquisicao/04_harmonizar_territorio_ibge.py"))

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
        self.assertIn("correcao_de_dado_de_entrada", emendas["2026-10-18"]["tipo"])
        self.assertIn("Censo 2022", emendas["2026-10-18"]["o_que_e"])


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


# --- Guarda sobre o texto bruto de todo .py (scripts/ e raiz) ----------------------
# A varredura por AST acima só vê o pipeline e só vê constantes inteiras. Esta conta,
# em todo `.py` sob `scripts/` (inclusive `utils/`, `rdd_lib.py` e `historico/`) e na
# raiz, as ocorrências de "ivs_ipea" sem distinguir maiúsculas, no texto bruto, e soma
# as que só aparecem depois de juntar literais concatenados ("ivs_" + "ipea...",
# concatenação implícita, escapes) e os padrões de glob que casam com o arquivo
# ("ivs_*.csv", "*ipea*"). Cada script autorizado tem a contagem exata esperada: um
# uso novo, mesmo num script autorizado, reprova.
PADRAO_ERRADO = re.compile(r"ivs_ipea", re.IGNORECASE)
NOME_ERRADO = "ivs_ipea_2010_municipios.csv"
CAMINHO_ERRADO = re.compile(r"^[\w./\\-]*ivs_ipea_2010_municipios\.csv$", re.IGNORECASE)
_JUNTA = {"+", "(", ")"}

# Classes: LE_PARA_DOCUMENTAR monta o caminho e lê o arquivo para documentar o erro;
# RETIRADO é script fora do pipeline que usava o arquivo (registro histórico);
# TEXTO_FAILURE_MODE só cita o arquivo em docstring, comentário, nota ou rótulo, sem
# montar o caminho.
LE, RET, TXT = "LE_PARA_DOCUMENTAR", "RETIRADO", "TEXTO_FAILURE_MODE"
OCORRENCIAS_AUTORIZADAS: dict[str, tuple[int, str]] = {
    "run_all.py": (2, TXT),  # comentários sobre a ordem a07/a08/Censo
    "scripts/00_inventario_dados.py": (1, LE),  # inventário de data/, com rótulo FAILURE MODE
    "scripts/02_auditar_fontes_pmme.py": (3, LE),  # auditoria de fontes de data/, com rótulo FAILURE MODE
    "scripts/apresentacao/gerar_figuras_banca1.py": (1, TXT),  # comentário: ivs_categoria vem da malha oficial
    "scripts/aquisicao/04_harmonizar_territorio_ibge.py": (2, TXT),  # docstring e nota do manifesto
    "scripts/aquisicao/06_adquirir_populacao_censo2022.py": (2, TXT),  # docstring e nota do manifesto
    "scripts/aquisicao/a03_adquirir_ivs_regra.py": (3, RET),  # aquisição retirada que lia o arquivo
    "scripts/aquisicao/a06_integrar_portao.py": (2, RET),  # portão retirado que citava o arquivo como running variable
    "scripts/aquisicao/a08_adquirir_ivs_2010_oficial.py": (2, TXT),  # docstring e nota do manifesto
    "scripts/avaliacao_ciclo3/03_auditar_pre_e_potencia.py": (2, TXT),  # comentário e motivo da emenda de 18/10/2026
    "scripts/avaliacao_impacto/07_gerar_tabelas_e_figuras.py": (1, TXT),  # comentário: Tabela 1 lê a a08
    "scripts/auditoria_H1/a36_reconstruir_H1.py": (1, TXT),  # guarda: confere que os scripts da H1 não citam o arquivo
    "scripts/auditoria_H1/a42_auditoria_capitais_uf.py": (1, TXT),  # guarda: confere que nenhum arquivo aberto é o errado
    "scripts/rdd_bolsa/00_diagnosticar_viabilidade_salario_ivs.py": (1, RET),  # diagnóstico retirado (running variable errada)
    "scripts/rdd_bolsa/01_auditar_primeiro_estagio_publico.py": (1, RET),  # auditoria retirada (running variable errada)
    "scripts/rdd_bolsa/01_auditar_regra_e_suporte.py": (2, RET),  # auditoria retirada (running variable errada)
    "scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py": (1, RET),  # reconstrução retirada (running variable errada)
    "scripts/rdd_bolsa/04_portao_r1_escore_administrativo.py": (1, LE),  # compara o escore do MS com o arquivo
    "scripts/rdd_bolsa/04b_validar_ivs_oficial_escore_administrativo.py": (1, LE),  # compara o arquivo com a base oficial
    "scripts/rdd_bolsa/04c_identificar_recorte_arquivo_local.py": (3, LE),  # reproduz a extração errada
    "scripts/rdd_bolsa/06_estimar_E2_limites.py": (2, TXT),  # comentário e desvio: cenário informado retirado
    "scripts/rdd_bolsa/07_estimar_E3_rdd_completa.py": (2, TXT),  # comentário e nota da fonte oficial
    "scripts/rdd_bolsa/08_estimar_E4_proporcao.py": (2, TXT),  # comentário e desvio: cenário informado retirado
    "scripts/rdd_bolsa/09_gerar_relatorio_pdf.py": (3, LE),  # figura comparativa do arquivo errado
    "scripts/rdd_bolsa/10_galeria_figura_regra.py": (3, LE),  # figura comparativa do arquivo errado
    "scripts/revisao_literatura/historico/gerar_doc_modelagem_micro_comparada.py": (1, RET),  # gerador histórico de documento
    "scripts/tema_trabalho/01_auditar_atracao_provimento_interior.py": (1, TXT),  # comentário sobre o rdd_bolsa/00 retirado
    "scripts/tema_trabalho/03_construir_tipologia_territorial.py": (2, TXT),  # docstring e bloco de correção do manifesto
    "scripts/tema_trabalho/04_congelar_pre_analise.py": (1, TXT),  # texto da emenda de 18/10/2026
    "scripts/tema_trabalho/05_estimar_atracao.py": (2, TXT),  # bloco de correção e texto do relatório
    "scripts/tema_trabalho/06_avaliar_provimento_cnes.py": (2, TXT),  # comentário e bloco de correção
    "scripts/tema_trabalho/07_red_team_sintese.py": (4, LE),  # hash no manifesto A6, rotulado como failure mode
    "scripts/tema_trabalho/10_conferir_numeros_artigo.py": (2, TXT),  # comentários do conferidor
    "scripts/tema_trabalho/12_registrar_failure_mode_ivs.py": (6, LE),  # documentador do failure mode (lê para comparar)
}


def _grupos_de_literais(texto: str) -> list[tuple[str, str]]:
    """(valor juntado, texto bruto juntado) de cada sequência de literais encadeados."""
    grupos: list[tuple[str, str]] = []
    valores: list[str] = []
    brutos: list[str] = []
    profundidade_f = 0

    def fechar() -> None:
        if valores:
            grupos.append(("".join(valores), "".join(brutos)))
            valores.clear()
            brutos.clear()

    for tok in tokenize.generate_tokens(io.StringIO(texto).readline):
        nome = tokenize.tok_name[tok.type]
        if tok.type == tokenize.STRING:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                valor = ast.literal_eval(tok.string)
            valores.append(valor.decode("latin-1") if isinstance(valor, bytes) else valor)
            brutos.append(tok.string)
        elif nome == "FSTRING_MIDDLE":
            valores.append(tok.string)
            brutos.append(tok.string)
        elif nome == "FSTRING_START":
            profundidade_f += 1
        elif nome == "FSTRING_END":
            profundidade_f -= 1
        elif tok.type in (tokenize.NL, tokenize.COMMENT):
            continue
        elif tok.type == tokenize.OP and (tok.string in _JUNTA or (profundidade_f and tok.string in "{}")):
            continue
        else:
            fechar()
    fechar()
    return grupos


def _glob_que_casa(valor: str) -> bool:
    v = valor.strip().lower()
    if not any(c in v for c in "*?[") or not ("ivs" in v or "ipea" in v):
        return False
    return any(fnmatch.fnmatchcase(alvo, padrao) for padrao in (v, v.replace("\\", "/").rsplit("/", 1)[-1])
               for alvo in (NOME_ERRADO, "data/" + NOME_ERRADO))


def ocorrencias(texto: str) -> tuple[int, int]:
    """(ocorrências totais, grupos que formam um caminho do arquivo errado)."""
    total = len(PADRAO_ERRADO.findall(texto))
    caminhos = 0
    for valor, bruto in _grupos_de_literais(texto):
        n = len(PADRAO_ERRADO.findall(valor))
        total += max(0, n - len(PADRAO_ERRADO.findall(bruto)))
        if n == 0 and _glob_que_casa(valor):
            total += 1
            caminhos += 1
        elif CAMINHO_ERRADO.match(valor.strip()):
            caminhos += 1
    return total, caminhos


def arquivos_python(raiz: Path) -> list[Path]:
    return sorted(p for p in [*raiz.glob("*.py"), *(raiz / "scripts").rglob("*.py")] if "__pycache__" not in p.parts)


def violacoes(raiz: Path) -> list[str]:
    erros = []
    vistos = set()
    for p in arquivos_python(raiz):
        chave = str(p.relative_to(raiz)).replace("\\", "/")
        vistos.add(chave)
        total, caminhos = ocorrencias(p.read_text(encoding="utf-8"))
        esperado, classe = OCORRENCIAS_AUTORIZADAS.get(chave, (0, None))
        if total != esperado:
            erros.append(f"{chave}: {total} ocorrência(s) do arquivo de IVS errado, autorizadas {esperado}")
        if classe == TXT and caminhos:
            erros.append(f"{chave}: classe {TXT} mas monta {caminhos} caminho(s) do arquivo")
        if classe == LE and not caminhos:
            erros.append(f"{chave}: classe {LE} mas não monta mais o caminho; reclassifique")
    erros += [f"{k}: autorizado mas inexistente" for k in OCORRENCIAS_AUTORIZADAS if k not in vistos]
    return erros


class TestGuardaTextoBruto(unittest.TestCase):
    def test_contagem_exata_por_script(self) -> None:
        self.assertEqual(violacoes(ROOT), [])

    def test_leitores_do_pipeline_estao_na_classe_certa(self) -> None:
        for script in LEITORES_AUTORIZADOS:
            self.assertIn(OCORRENCIAS_AUTORIZADAS[script][1], {LE}, script)

    def test_guarda_pega_violacoes_injetadas_numa_copia(self) -> None:
        """Injeta cada forma de uso numa cópia temporária (fora do repositório)."""
        casos = {
            "concatenacao": ("scripts/tema_trabalho/99_injetado.py",
                             'from pathlib import Path\nP = Path("data") / ("ivs_" + "ipea_2010_municipios.csv")\n'),
            "concatenacao_implicita_e_escape": ("scripts/tema_trabalho/99_injetado.py",
                                                'P = ("data/ivs" "\\x5fipea_2010_municipios.csv")\n'),
            "glob_com_nome": ("scripts/rdd_bolsa/99_injetado.py",
                              'from pathlib import Path\nA = sorted(Path("data").glob("ivs_ipea_*.csv"))\n'),
            "glob_sem_o_nome_inteiro": ("scripts/rdd_bolsa/99_injetado.py",
                                        'from pathlib import Path\nA = sorted(Path("data").glob("IVS_*_municipios.csv"))\n'),
            "helper_em_utils": ("scripts/utils/ambiente.py", '\nIVS_2010 = "data/" + "IVS_" + "IPEA_2010_municipios.csv"\n'),
            "helper_novo_em_utils": ("scripts/utils/caminhos_injetados.py", 'IVS = "data/ivs_ipea_2010_municipios.csv"\n'),
            "rdd_lib": ("scripts/rdd_bolsa/rdd_lib.py", '\n_IVS = "data/ivs_" "ipea_2010_municipios.csv"\n'),
            "uso_novo_em_script_autorizado": ("scripts/rdd_bolsa/04c_identificar_recorte_arquivo_local.py",
                                              '\nOUTRO = ROOT / "data" / "ivs_ipea_2010_municipios.csv"\n'),
            "caminho_em_script_so_de_texto": ("scripts/aquisicao/a08_adquirir_ivs_2010_oficial.py",
                                              '\nX = ROOT / "data" / "ivs_" "ipea_2010_municipios.csv"\n'),
            "fstring": ("scripts/tema_trabalho/99_injetado.py", 'NOME = "ipea"\nP = f"data/ivs_{"ipea"}_2010_municipios.csv"\n'),
        }
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / "repo"
            shutil.copytree(ROOT / "scripts", copia / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
            for p in ROOT.glob("*.py"):
                shutil.copy2(p, copia / p.name)
            self.assertNotEqual(copia.resolve().parts[:len(ROOT.resolve().parts)], ROOT.resolve().parts)
            self.assertEqual(violacoes(copia), [], "a cópia limpa já viola")
            for caso, (alvo, trecho) in casos.items():
                with self.subTest(caso=caso):
                    arquivo = copia / alvo
                    original = arquivo.read_text(encoding="utf-8") if arquivo.exists() else None
                    arquivo.write_text((original or "") + trecho, encoding="utf-8")
                    try:
                        erros = violacoes(copia)
                        self.assertTrue(any(e.startswith(alvo + ":") for e in erros), f"{caso} passou pela guarda")
                    finally:
                        if original is None:
                            arquivo.unlink()
                        else:
                            arquivo.write_text(original, encoding="utf-8")
            self.assertEqual(violacoes(copia), [], "a cópia não voltou ao estado limpo")


class TestDocumentosCitamAjusteCorrigido(unittest.TestCase):
    """Síntese (doc 16) e proveniência da banca citam o ajuste completo lido de A4_tabela_03b."""

    @classmethod
    def setUpClass(cls) -> None:
        aj = pd.read_csv(ROOT / "output/tema_trabalho/A4_tabela_03b_ajuste_completo.csv").set_index("termo")
        cls.l = aj.loc["estrato_metropolitano"]

    @staticmethod
    def br(v: float, casas: int) -> str:
        return f"{v:.{casas}f}".replace(".", ",")

    def test_doc16(self) -> None:
        l = self.l
        esperado = (f"**+{self.br(100 * l['coef'], 1)} p.p.** (EP {self.br(100 * l['se_cluster'], 1)}; "
                    f"`p={self.br(l['p_valor'], 3)}`; `q={self.br(l['q_fdr_estrato'], 3)}`)")
        txt = (ROOT / "docs/05_identificacao/16_sintese_achados_e_novo_plano_causal.md").read_text(encoding="utf-8")
        self.assertIn(esperado, txt)

    def test_banca1_proveniencia(self) -> None:
        l = self.l
        esperado = (f"**{self.br(l['coef'], 4)}** (EP {self.br(l['se_cluster'], 3)}; p = {self.br(l['p_valor'], 3)}; "
                    f"q = {self.br(l['q_fdr_estrato'], 3)})")
        txt = (ROOT / "docs/07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md").read_text(encoding="utf-8")
        self.assertIn(esperado, txt)


class TestDocumentosC3EmVigor(unittest.TestCase):
    """Plano do ciclo 3, estratégia, roadmap e fila citam o C3-03 reestimado, não o antigo."""

    @classmethod
    def setUpClass(cls) -> None:
        resumo = json.loads((ROOT / "output/tema_trabalho/failure_mode_ivs_resumo.json").read_text(encoding="utf-8"))
        cls.c3 = {(r["modulo"], r["nivel"]): r for r in resumo["c3_03_ciclo3"]}
        diag = pd.read_csv(ROOT / "output/avaliacao_ciclo3/diagnosticos_pre.csv")
        cls.diag = {(r.modulo, r.nivel): r for r in diag.itertuples(index=False)}
        cls.docs = {nome: (ROOT / nome).read_text(encoding="utf-8") for nome in (
            "docs/05_identificacao/13_plano_pre_analise_ciclo3.md", "docs/05_identificacao/12_estrategia_causal_prospectiva_ciclo3.md",
            "docs/06_execucao/05_roadmap_execucao.md", "prompts/avaliacao_ciclo3/README.md")}

    @staticmethod
    def br(v: float, casas: int) -> str:
        return f"{v:.{casas}f}".replace(".", ",")

    def test_mde_da_anestesiologia_em_vigor(self) -> None:
        for nivel in ("cnes_ofertante", "municipio"):
            antes = self.br(self.c3[("anestesiologia", nivel)]["mde_80_antes_failure_mode"], 2)
            depois = self.br(self.diag[("anestesiologia", nivel)].mde_80_especialistas, 2)
            self.assertNotEqual(antes, depois)
            for nome in ("docs/05_identificacao/13_plano_pre_analise_ciclo3.md",
                         "docs/05_identificacao/12_estrategia_causal_prospectiva_ciclo3.md",
                         "docs/06_execucao/05_roadmap_execucao.md"):
                self.assertIn(depois, self.docs[nome], f"{nome}: MDE {nivel} em vigor ausente")
                self.assertNotIn(f"MDE de {antes}", self.docs[nome], nome)
                self.assertNotIn(f"MDE {antes}", self.docs[nome], nome)
                self.assertNotIn(f"| {antes} |", self.docs[nome], nome)

    def test_suporte_que_muda_de_status_esta_explicito(self) -> None:
        viraram = [k for k, r in self.c3.items() if r["suporte_aprovado_antes"] != r["suporte_aprovado_depois"]]
        self.assertTrue(viraram)
        for modulo, nivel in viraram:
            r = self.c3[(modulo, nivel)]
            trecho = (f"{self.br(r['suporte_c_antes'], 3)} → {self.br(r['suporte_t_depois'], 3)}/"
                      f"{self.br(r['suporte_c_depois'], 3)}")
            for nome in ("docs/05_identificacao/13_plano_pre_analise_ciclo3.md", "prompts/avaliacao_ciclo3/README.md"):
                self.assertIn(trecho, self.docs[nome], f"{nome}: virada de suporte de {modulo}/{nivel} ausente")
                self.assertIn("perto do limiar", self.docs[nome], nome)


if __name__ == "__main__":
    unittest.main()
