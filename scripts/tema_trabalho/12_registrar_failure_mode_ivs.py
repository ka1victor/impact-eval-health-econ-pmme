"""Registra o failure mode do arquivo de IVS errado e compara antes e depois.

Até 18/10/2026, IVS, subíndices, IDHM, população 2010 e renda de toda a cadeia
territorial (malha, tipologia A2, painéis CNES, A4, A5 e a Tabela 1 do ciclo 1)
vinham de `data/ivs_ipea_2010_municipios.csv`. Esse arquivo não é o IVS do
município: é, em cada município, a última linha de subgrupo com IVS preenchido da
base do Ipea (auditoria 16). A correção trocou a fonte pela base oficial (a08) e
pelo Censo 2022 e reestimou as etapas afetadas sem mudar especificação, amostra ou
desfecho.

Este script não estima nada. Ele:
1. lê as versões ANTIGAS dos artefatos afetados direto do histórico do Git, no
   commit anterior à correção (`REF_ANTES`), e as versões NOVAS de `output/`;
2. grava a comparação em `output/tema_trabalho/failure_mode_ivs_antes_depois.csv`
   e o resumo em `output/tema_trabalho/failure_mode_ivs_resumo.json`;
3. gera `docs/auditorias/19_reestimacao_base_oficial_failure_mode.md`, em que cada
   número vem desses dois arquivos ou dos artefatos citados.

Os valores antigos são rotulados `FAILURE_MODE` e só existem para documentar o
erro: não alimentam nenhuma etapa. Os novos são `EMPIRICO`.

É um dos três tipos de leitor autorizado de `data/ivs_ipea_2010_municipios.csv`
(documentação do failure mode; ver `tests/test_fonte_ivs_oficial.py`). Exige o
histórico do Git com `REF_ANTES`; sem ele, para.
"""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "tema_trabalho"
DOC = ROOT / "docs" / "auditorias" / "19_reestimacao_base_oficial_failure_mode.md"
OUT_CSV = OUT / "failure_mode_ivs_antes_depois.csv"
OUT_JSON = OUT / "failure_mode_ivs_resumo.json"

# Último commit antes da correção (18/10/2026): artefatos com o arquivo errado.
REF_ANTES = "22eddb528c37aa0bf8721275999423900959070b"

ARQUIVO_ERRADO = ROOT / "data" / "ivs_ipea_2010_municipios.csv"
IVS_OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
CENSO2022 = ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
IDENT_04C = ROOT / "output" / "rdd_bolsa" / "identificacao_arquivo_local_ivs.json"
TIPOLOGIA = "output/tema_trabalho/matriz_tipologia_territorial.parquet"
E3_STATUS = ROOT / "output" / "rdd_bolsa" / "E3_status.json"
E5_RESUMO = ROOT / "output" / "rdd_bolsa" / "E5_resumo.json"
ALFA = 0.05

TT = "output/tema_trabalho/"
# (bloco, arquivo, coluna da especificação, padrão da especificação, termos, colunas)
# Colunas: (coef, ep, p, q); None quando a tabela não tem a coluna.
TABELAS: list[tuple[str, str, str, str, list[str], tuple[str, str | None, str, str | None]]] = [
    ("A4 modelo principal (sem covariadas contínuas)", TT + "A4_tabela_02_modelo_principal_LPM.csv", "espec", "",
     ["estrato_metropolitano", "estrato_capital", "estrato_interior_proximo_polo"],
     ("coef", "se_cluster", "p_valor", "q_fdr_estrato")),
    ("A4 ajuste completo", TT + "A4_tabela_03b_ajuste_completo.csv", "espec", "",
     ["estrato_metropolitano", "estrato_capital", "estrato_interior_proximo_polo", "ivs_2010", "log_pop",
      "estoque_por_10k", "faixa_FAIXA 2", "faixa_FAIXA 3"],
     ("coef", "se_cluster", "p_valor", "q_fdr_estrato")),
    ("A4 ajuste completo winsorizado p99", TT + "A4_tabela_03c_winsorizado.csv", "espec", "",
     ["estrato_metropolitano", "estrato_capital", "estrato_interior_proximo_polo", "ivs_2010", "log_pop",
      "estoque_por_10k"],
     ("coef", "se_cluster", "p_valor", "q_fdr_estrato")),
    ("A4 IVS quadrático", TT + "A4_tabela_03d_ivs_spline.csv", "espec", "",
     ["ivs_2010", "ivs_2010_sq", "estrato_metropolitano"],
     ("coef", "se_cluster", "p_valor", "q_fdr_estrato")),
    ("A4 IVS só (FE)", TT + "A4_tabela_03_separacao_faixa_ivs_remoticidade.csv", "espec", "LPM_ivs_only_FE",
     ["ivs_2010"], ("coef", "se_cluster", "p_valor", None)),
    ("A4 estrato × IVS", TT + "A4_tabela_03_separacao_faixa_ivs_remoticidade.csv", "espec", "LPM_estrato_x_ivs_FE",
     ["ivs_2010", "estrato_capital_x_ivs", "estrato_metropolitano_x_ivs", "estrato_interior_proximo_polo_x_ivs"],
     ("coef", "se_cluster", "p_valor", None)),
    ("A5 estoque em 6 meses, completo", TT + "A5_tabela_03_modelo_estoque_6m.csv", "espec", "full",
     ["atracao_muni", "estrato_capital", "estrato_metropolitano", "estrato_interior_proximo_polo", "ivs_2010",
      "log_pop", "estoque_por_10k"],
     ("coef", "se_cluster", "p_valor", "q_fdr_atracao")),
    ("A5 cobertura em 6 meses, completo", TT + "A5_tabela_03c_modelo_cobertura.csv", "espec", "full",
     ["atracao_muni"], ("coef", "se_cluster", "p_valor", "q_fdr_atracao")),
    ("A5 entradas em 6 meses, completo", TT + "A5_tabela_03d_modelo_entradas.csv", "espec", "full",
     ["atracao_muni"], ("coef", "se_cluster", "p_valor", "q_fdr_atracao")),
    ("A5 presença em 6 meses, completo", TT + "A5_tabela_03e_modelo_presenca.csv", "espec", "full",
     ["atracao_muni"], ("coef", "se_cluster", "p_valor", "q_fdr_atracao")),
    ("A5 heterogeneidade atração × estrato", TT + "A5_tabela_03i_heterogeneidade_estrato.csv", "espec", "",
     ["atracao_muni", "atracao_x_capital", "atracao_x_metropolitano", "atracao_x_interior_proximo_polo"],
     ("coef", "se_cluster", "p_valor", None)),
    ("A5 estudo de evento proporcional, mar/2026 (sem covariadas contínuas)",
     TT + "A5_tabela_08_estudo_evento_proporcional.csv", "competencia", "202603", ["__linha_confirmatoria__"],
     ("beta", "se_cluster", "p_valor", None)),
    ("A5 estudo de evento em nível, mar/2026 (sem covariadas contínuas)",
     TT + "A5_tabela_07_estudo_evento_atracao.csv", "competencia", "202603", ["__linha_confirmatoria__"],
     ("beta", "se_cluster", "p_valor", None)),
]
TABELA1 = "output/avaliacao_impacto/tabelas/tabela1_estatisticas_descritivas_baseline.csv"

# Auditoria de usos de data/ivs_ipea_2010_municipios.csv (tarefa 1 da tarefa E).
# Classes: (a) running variable ou gradiente de IVS; (b) covariável (log_pop, renda,
# IDHM, estoque por habitante); (c) só documenta ou inventaria o erro, com rótulo;
# (d) script retirado, fora do pipeline; (—) não lê nem herda.
# (script, como chega ao arquivo, classe, no run_all, situação depois de 18/10/2026)
AUDITORIA: list[tuple[str, str, str, str, str]] = [
    ("scripts/00_inventario_dados.py", "direto: inventário de data/", "(c)", "sim",
     "mantido como inventário, com rótulo FAILURE MODE na saída"),
    ("scripts/02_auditar_fontes_pmme.py", "direto: hash, linhas e campos", "(c)", "sim",
     "mantido como auditoria de fontes, com rótulo FAILURE MODE"),
    ("scripts/aquisicao/04_harmonizar_territorio_ibge.py", "direto: IVS, subíndices, IDHM, população, renda da malha", "(a) e (b)", "sim",
     "corrigido: a08 + Censo 2022; a07 e a08 sobem no run_all para antes dele"),
    ("scripts/aquisicao/05_integrar_painel_analitico.py", "indireto: colunas da malha no painel mensal", "(b)", "sim",
     "herda a malha corrigida; não roda sem o CNES mensal (>16 GB); consumidores repõem as colunas"),
    ("scripts/avaliacao_impacto/07_gerar_tabelas_e_figuras.py", "indireto: painel município–curso", "(b) descritivo", "sim",
     "corrigido: IVS e população da a08; Tabela 1 regenerada"),
    ("scripts/avaliacao_ciclo3/03_auditar_pre_e_potencia.py", "indireto: painel_municipios_regioes (ivs_2010, log_pop_2010)", "(b)", "não",
     "corrigido por emenda datada (--reestimar-covariaveis-oficiais): painéis pré-T0 congelados, nenhum mês pós-T0 lido"),
    ("scripts/apresentacao/gerar_figuras_banca1.py", "indireto: ivs_categoria do painel município–curso", "(b) descritivo", "não",
     "corrigido: categoria da malha oficial; manifesto das figuras regenerado"),
    ("scripts/tema_trabalho/01_auditar_atracao_provimento_interior.py", "indireto: veredito de rdd_bolsa/00", "(a)", "sim",
     "corrigido: confere a regra com a a08"),
    ("scripts/tema_trabalho/03_construir_tipologia_territorial.py", "indireto: malha", "(b)", "sim",
     "corrigido: colunas da a08; estoque por 10 mil com Censo 2022"),
    ("scripts/tema_trabalho/04_congelar_pre_analise.py", "indireto: hash da malha e da tipologia", "registro", "sim",
     "emenda datada no registro A3"),
    ("scripts/tema_trabalho/05_estimar_atracao.py", "indireto: tipologia", "(a) e (b)", "sim", "reestimado"),
    ("scripts/tema_trabalho/06_avaliar_provimento_cnes.py", "indireto: painel em T0 e tipologia", "(b)", "sim",
     "reestimado; covariadas repostas em memória"),
    ("scripts/tema_trabalho/06b_ameacas_a5_placebo_pretendencia_deslocamento.py", "indireto: painel em T0, sem covariadas contínuas", "(—)", "sim",
     "reexecutado só para atualizar o hash de A5"),
    ("scripts/tema_trabalho/07_red_team_sintese.py", "direto: hash com rótulo; texto do ajuste completo", "(c)", "sim",
     "ajuste completo corrigido; arquivo hasheado só como failure mode"),
    ("scripts/tema_trabalho/08_auditar_cutoff_selecao.py, 09_*, 09b_*", "não leem", "(—)", "sim", "inalterado"),
    ("scripts/tema_trabalho/10_conferir_numeros_artigo.py, 11_*", "comentários", "(c)", "sim", "conferem o ajuste completo corrigido"),
    ("scripts/tema_trabalho/12_registrar_failure_mode_ivs.py", "direto: documenta o erro", "(c)", "não", "este registro"),
    ("scripts/aquisicao/06_adquirir_populacao_censo2022.py", "só docstring", "(—)", "sim",
     "entra no run_all antes da malha; data de aquisição determinística; sem número do arquivo errado"),
    ("scripts/aquisicao/a03_adquirir_ivs_regra.py", "direto: diagnóstico da regra", "(a)", "não", "(d) histórico"),
    ("scripts/aquisicao/a06_integrar_portao.py", "texto da matriz variável–fonte", "(a)", "não", "(d) histórico"),
    ("scripts/aquisicao/a08_adquirir_ivs_2010_oficial.py", "só observação no manifesto", "(c)", "sim", "inalterado"),
    ("scripts/rdd_bolsa/00_*, 01_*, 01b_*", "direto: running variable", "(a)", "não", "(d) retirados em 18/10/2026"),
    ("scripts/rdd_bolsa/02_*, 03_*", "indireto: portões feitos com o arquivo", "(a)", "não", "(d) retirados em 18/10/2026"),
    ("scripts/rdd_bolsa/04_portao_r1_escore_administrativo.py", "direto: correlação com o escore do MS", "(c)", "sim", "inalterado"),
    ("scripts/rdd_bolsa/04b_*, 04c_*", "direto: compara com a base oficial e reproduz o erro", "(c)", "sim", "inalterado"),
    ("scripts/rdd_bolsa/06_estimar_E2_limites.py, 08_estimar_E4_proporcao.py", "direto: banda do cenário \"informado\"", "(a)", "sim",
     "cenário \"informado\" retirado das saídas ativas; pior caso, E4a e E4c idênticos; arquivo não é mais lido"),
    ("scripts/rdd_bolsa/07_*, 08a_*, 09b_*, 11_*", "não leem o arquivo; E3 e E5 leem da tipologia só o estrato", "(—)", "sim",
     "07, 11, 09b reexecutados: estimativas idênticas; só o hash da tipologia muda"),
    ("scripts/rdd_bolsa/09_gerar_relatorio_pdf.py, 10_galeria_figura_regra.py", "direto: figura comparativa", "(c)", "sim", "inalterado"),
    ("scripts/revisao_literatura/historico/gerar_doc_modelagem_micro_comparada.py", "texto histórico", "(d)", "não", "histórico"),
]
DIAG_01 = TT + "diagnostico_atracao_provimento_interior.json"


def sha256_bytes(conteudo: bytes) -> str:
    return hashlib.sha256(conteudo).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_antes(rel: str) -> bytes:
    """Conteúdo de `rel` no commit anterior à correção; ausente aborta."""
    try:
        return subprocess.run(["git", "-C", str(ROOT), "show", f"{REF_ANTES}:{rel}"],
                              check=True, capture_output=True).stdout
    except subprocess.CalledProcessError as erro:
        raise SystemExit(f"histórico do Git sem {REF_ANTES}:{rel} ({erro.stderr.decode().strip()})")


def ler_csv(rel: str, antes: bool) -> pd.DataFrame:
    conteudo = git_antes(rel) if antes else (ROOT / rel).read_bytes()
    return pd.read_csv(io.BytesIO(conteudo))


def num(v: float | None, casas: int = 3) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    texto = f"{v:.{casas}f}".replace(".", ",")
    return texto.replace("-", "−")


def milhar(v: int) -> str:
    return f"{int(v):,}".replace(",", ".")


def conferir_leitura(linhas: list[dict[str, Any]], inalterados: list[str], rdd_global: dict[str, Any]) -> None:
    """Cada frase fixa da seção 6 tem de valer nos dados; senão o script para.

    Fail closed: a leitura não é ajustada aos números; se um destes testes falhar,
    o texto do documento precisa ser revisto à mão antes de regenerar.
    """
    def r(bloco: str, termo: str) -> dict[str, Any]:
        return next(x for x in linhas if x["bloco"] == bloco and x["termo"] == termo)

    checagens = {
        "modelo principal de A4 idêntico": "A4 modelo principal (sem covariadas contínuas)" in inalterados,
        "estudos de evento de A5 idênticos": all(b in inalterados for b in linhas_evento(linhas)),
        "ajuste completo: contraste metropolitano menor": (
            r("A4 ajuste completo", "estrato_metropolitano")["coef_depois"]
            < r("A4 ajuste completo", "estrato_metropolitano")["coef_antes_failure_mode"]),
        "IVS só: p >= 5% depois": r("A4 IVS só (FE)", "ivs_2010")["p_depois"] >= ALFA,
        "IVS no ajuste completo: p >= 5% depois": r("A4 ajuste completo", "ivs_2010")["p_depois"] >= ALFA,
        "capital × IVS: p < 5% antes e depois": (
            r("A4 estrato × IVS", "estrato_capital_x_ivs")["p_depois"] < ALFA
            and r("A4 estrato × IVS", "estrato_capital_x_ivs")["p_antes_failure_mode"] < ALFA),
        "RDD: estimativas idênticas": all(rdd_global["estimativas_identicas_byte_a_byte"].values())
        and rdd_global["e2_pior_caso_identico"] and rdd_global["e4_demais_identicas"],
        "A5 completo: nenhum termo de atração vira significante": all(
            x["p_depois"] >= ALFA or x["p_antes_failure_mode"] < ALFA
            for x in linhas if x["bloco"].startswith("A5") and x["termo"].startswith("atracao")),
    }
    falhas = [k for k, ok in checagens.items() if not ok]
    if falhas:
        raise SystemExit(f"leitura fixa do documento não vale mais: {falhas}; revisar o texto")


def linhas_evento(linhas: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(x["bloco"] for x in linhas if "estudo de evento" in x["bloco"]))


def linha_tabela(df: pd.DataFrame, col_espec: str, padrao: str, termo: str) -> pd.Series:
    if termo == "__linha_confirmatoria__":
        sel = df[(df[col_espec].astype(str) == padrao) & (df["amostra"].astype(str).str.startswith("confirmatoria"))]
    else:
        sel = df[df["termo"] == termo]
        if padrao:
            sel = sel[sel[col_espec].astype(str).str.contains(padrao, regex=False)]
    if len(sel) != 1:
        raise SystemExit(f"{termo}/{padrao}: {len(sel)} linhas, esperava 1")
    return sel.iloc[0]


def comparar_tabelas() -> list[dict[str, Any]]:
    linhas = []
    for bloco, rel, col_espec, padrao, termos, (c_coef, c_se, c_p, c_q) in TABELAS:
        velho, novo = ler_csv(rel, True), ler_csv(rel, False)
        for termo in termos:
            a, b = linha_tabela(velho, col_espec, padrao, termo), linha_tabela(novo, col_espec, padrao, termo)

            def val(s: pd.Series, c: str | None) -> float | None:
                return None if c is None or c not in s.index or pd.isna(s[c]) else float(s[c])

            p_a, p_b = val(a, c_p), val(b, c_p)
            linhas.append({
                "bloco": bloco,
                "termo": termo if termo != "__linha_confirmatoria__" else "atracao (amostra confirmatória)",
                "fonte_arquivo": rel,
                "coef_antes_failure_mode": val(a, c_coef),
                "coef_depois": val(b, c_coef),
                "ep_antes_failure_mode": val(a, c_se),
                "ep_depois": val(b, c_se),
                "p_antes_failure_mode": p_a,
                "p_depois": p_b,
                "q_antes_failure_mode": val(a, c_q),
                "q_depois": val(b, c_q),
                "muda_lado_de_5pct_p": bool(p_a is not None and p_b is not None and (p_a < ALFA) != (p_b < ALFA)),
                "muda_lado_de_5pct_q": bool(val(a, c_q) is not None and val(b, c_q) is not None
                                            and (val(a, c_q) < ALFA) != (val(b, c_q) < ALFA)),
                "muda_sinal": bool(val(a, c_coef) is not None and val(b, c_coef) is not None
                                   and np.sign(val(a, c_coef)) != np.sign(val(b, c_coef))),
                "natureza_antes": "FAILURE_MODE",
                "natureza_depois": "EMPIRICO",
            })
    return linhas


def comparar_tabela1() -> list[dict[str, Any]]:
    velho, novo = ler_csv(TABELA1, True), ler_csv(TABELA1, False)
    linhas = []
    for variavel in ["População municipal 2010", "IVS 2010"]:
        a = velho[velho["Variável"] == variavel].iloc[0]
        b = novo[novo["Variável"] == variavel].iloc[0]
        for col in ["Imediata média", "Reserva média", "Diferença padronizada"]:
            linhas.append({"variavel": variavel, "coluna": col,
                           "antes_failure_mode": float(a[col]), "depois": float(b[col])})
    return linhas


def comparar_tipologia() -> dict[str, Any]:
    bruto_antes = git_antes(TIPOLOGIA)
    velho = pd.read_parquet(io.BytesIO(bruto_antes))
    novo = pd.read_parquet(ROOT / TIPOLOGIA)
    m = velho.merge(novo, on="co_ibge_6d", suffixes=("_a", "_d"), validate="one_to_one")
    a1 = m[m["in_populacao_A1_d"]]
    quadro = a1[a1["estoque_especialistas_pre_12m_media_d"].notna()]
    of = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str})
    of["co_ibge_6d"] = of["co_ibge"].str.zfill(6)
    conf = novo.merge(of, on="co_ibge_6d", how="inner")
    return {
        "municipios": int(len(m)),
        "estrato_identico": bool((m["estrato_a"] == m["estrato_d"]).all()),
        "estoque_pre_identico": bool(((m["estoque_especialistas_pre_12m_media_a"] == m["estoque_especialistas_pre_12m_media_d"])
                                      | (m["estoque_especialistas_pre_12m_media_a"].isna()
                                         & m["estoque_especialistas_pre_12m_media_d"].isna())).all()),
        "ivs_igual_ao_oficial_depois": int((conf["ivs_2010"] == conf["ivs"]).sum()),
        "ivs_comparados_com_oficial": int(len(conf)),
        "ivs_igual_antes_e_depois_3_casas": int((m["ivs_2010_a"].round(3) == m["ivs_2010_d"].round(3)).sum()),
        "ivs_categoria_igual_antes_e_depois": int((m["ivs_categoria_a"] == m["ivs_categoria_d"]).sum()),
        "a1_municipios": int(len(a1)),
        "a1_ivs_medio": {"antes_failure_mode": float(a1["ivs_2010_a"].mean()), "depois": float(a1["ivs_2010_d"].mean())},
        "a1_populacao_2010_mediana": {"antes_failure_mode": float(a1["populacao_2010_a"].median()),
                                      "depois": float(a1["populacao_2010_d"].median())},
        "quadro_municipios_com_estoque": int(len(quadro)),
        "quadro_estoque_pre_por_10k_mediana": {
            "antes_failure_mode": float(quadro["estoque_pre_por_10k_a"].median()),
            "depois": float(quadro["estoque_pre_por_10k_d"].median()),
        },
        "sha256_antes": sha256_bytes(bruto_antes),
        "sha256_depois": sha256(ROOT / TIPOLOGIA),
    }


RDD_ESTIMATIVAS = ["output/rdd_bolsa/E1_densidade_estimativas.csv", "output/rdd_bolsa/E3_estimativas.csv",
                   "output/rdd_bolsa/E3_diagnosticos.csv", "output/rdd_bolsa/E4_proporcao_municipio.csv",
                   "output/rdd_bolsa/E5_especificacoes.csv", "output/rdd_bolsa/E5_decomposicao_ic.csv",
                   "output/rdd_bolsa/E5_decomposicao_lados.csv", "output/rdd_bolsa/E5_lr_selecao_janela.csv",
                   "output/rdd_bolsa/E5_lr_sensibilidade_janelas.csv"]


def cadeia_rdd(tip: dict[str, Any]) -> dict[str, Any]:
    """E3/E5 reexecutados: registram a tipologia nova e as estimativas são idênticas.

    E2 e E4: o cenário `informado` saiu; as demais linhas são idênticas às de antes.
    """
    e3 = json.loads(E3_STATUS.read_text(encoding="utf-8"))
    e5 = json.loads(E5_RESUMO.read_text(encoding="utf-8"))
    identicos = {rel: sha256_bytes(git_antes(rel)) == sha256(ROOT / rel) for rel in RDD_ESTIMATIVAS}
    e2a, e2d = ler_csv("output/rdd_bolsa/E2_limites.csv", True), ler_csv("output/rdd_bolsa/E2_limites.csv", False)
    e4a, e4d = ler_csv("output/rdd_bolsa/E4_estimativas.csv", True), ler_csv("output/rdd_bolsa/E4_estimativas.csv", False)
    e2_pior = e2a[e2a["cenario"] != "informado"].reset_index(drop=True).equals(e2d)
    e4_resto = e4a[e4a["cenario_ou_espec"] != "informado"].reset_index(drop=True).equals(e4d)
    return {
        "e3_registra_tipologia_nova": e3["covariaveis_pre"][TIPOLOGIA]["sha256"] == tip["sha256_depois"],
        "e5_registra_tipologia_nova": e5["entradas"][TIPOLOGIA]["sha256"] == tip["sha256_depois"],
        "estrato_identico": tip["estrato_identico"],
        "estimativas_identicas_byte_a_byte": identicos,
        "e2_linhas_antes": int(len(e2a)), "e2_linhas_depois": int(len(e2d)),
        "e2_linhas_informado_retiradas": int((e2a["cenario"] == "informado").sum()),
        "e2_pior_caso_identico": bool(e2_pior),
        "e4_linhas_antes": int(len(e4a)), "e4_linhas_depois": int(len(e4d)),
        "e4_linhas_informado_retiradas": int((e4a["cenario_ou_espec"] == "informado").sum()),
        "e4_demais_identicas": bool(e4_resto),
    }


def comparar_c3() -> list[dict[str, Any]]:
    rel_c3 = "output/avaliacao_ciclo3/diagnosticos_pre.csv"
    a, d = ler_csv(rel_c3, True), ler_csv(rel_c3, False)
    m = a.merge(d, on=["modulo", "nivel"], suffixes=("_a", "_d"), validate="one_to_one")
    linhas = []
    for r in m.itertuples(index=False):
        g = r._asdict()
        linhas.append({
            "modulo": g["modulo"], "nivel": g["nivel"],
            "mde_80_antes_failure_mode": g["mde_80_especialistas_a"], "mde_80_depois": g["mde_80_especialistas_d"],
            "suporte_t_antes": g["suporte_retido_tratado_a"], "suporte_t_depois": g["suporte_retido_tratado_d"],
            "suporte_c_antes": g["suporte_retido_controle_a"], "suporte_c_depois": g["suporte_retido_controle_d"],
            "suporte_aprovado_antes": bool(g["suporte_aprovado_a"]), "suporte_aprovado_depois": bool(g["suporte_aprovado_d"]),
            "decisao_antes": g["decisao_a"], "decisao_depois": g["decisao_d"],
        })
    return linhas


def comparar_banca1() -> dict[str, Any]:
    rel_m = "output/apresentacao_banca1/manifesto_figuras.json"
    a = json.loads(git_antes(rel_m).decode("utf-8"))["cobertura"]["detalhe_por_categoria_ivs_em_202506"]
    d = json.loads((ROOT / rel_m).read_text(encoding="utf-8"))["cobertura"]["detalhe_por_categoria_ivs_em_202506"]
    return {"antes_failure_mode": a, "depois": d}


def failure_mode_arquivo() -> dict[str, Any]:
    """Números do próprio erro, lidos do arquivo errado (documentação) e da base oficial."""
    errado = pd.read_csv(ARQUIVO_ERRADO, dtype={"cod_ibge6": str})
    of = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str})
    errado["c6"] = errado["cod_ibge6"].str.zfill(6)
    of["c6"] = of["co_ibge"].str.zfill(6)
    m = errado.merge(of, on="c6", validate="one_to_one")
    ident = json.loads(IDENT_04C.read_text(encoding="utf-8"))
    return {
        "municipios": int(len(m)),
        "ivs_igual_3_casas": int((m["ivs_2010"].round(3) == m["ivs"].round(3)).sum()),
        "correlacao_ivs": float(m[["ivs_2010", "ivs"]].corr().iloc[0, 1]),
        "populacao_2010_soma_arquivo_errado": int(errado["populacao_2010"].sum()),
        "populacao_2010_soma_oficial": int(of["populacao"].sum()),
        "linha_escolhida_por_municipio": ident["mecanismo"]["linha_escolhida_por_municipio"],
        "fonte_mecanismo": str(IDENT_04C.relative_to(ROOT)),
    }


def diag01() -> dict[str, str]:
    def modulo(conteudo: bytes) -> str:
        d = json.loads(conteudo.decode("utf-8"))
        return next(r["evidencia"] for r in d["decisao_por_modulo"] if r["modulo"] == "rdd_bolsa")
    return {"antes_failure_mode": modulo(git_antes(DIAG_01)), "depois": modulo((ROOT / DIAG_01).read_bytes())}


# ------------------------------------------------------------------ documento


def tabela_md(linhas: list[dict[str, Any]], bloco: str) -> str:
    sel = [r for r in linhas if r["bloco"] == bloco]
    out = ["| Termo | Coef. antes (failure mode) | Coef. depois | EP antes → depois | p antes → depois | q antes → depois |",
           "|---|---:|---:|---|---|---|"]
    for r in sel:
        out.append(
            f"| `{r['termo']}` | {num(r['coef_antes_failure_mode'])} | **{num(r['coef_depois'])}** | "
            f"{num(r['ep_antes_failure_mode'])} → {num(r['ep_depois'])} | "
            f"{num(r['p_antes_failure_mode'])} → {num(r['p_depois'])} | "
            f"{num(r['q_antes_failure_mode'])} → {num(r['q_depois'])} |")
    return "\n".join(out)


def conclusoes(linhas: list[dict[str, Any]]) -> list[str]:
    out = []
    for r in linhas:
        if r["muda_sinal"] or r["muda_lado_de_5pct_p"] or r["muda_lado_de_5pct_q"]:
            o_que = []
            if r["muda_sinal"]:
                o_que.append("o sinal muda")
            if r["muda_lado_de_5pct_p"]:
                o_que.append(f"o p cruza 5% ({num(r['p_antes_failure_mode'])} → {num(r['p_depois'])})")
            if r["muda_lado_de_5pct_q"]:
                o_que.append(f"o q de FDR cruza 5% ({num(r['q_antes_failure_mode'])} → {num(r['q_depois'])})")
            out.append(f"- **{r['bloco']}, `{r['termo']}`:** {num(r['coef_antes_failure_mode'])} → "
                       f"{num(r['coef_depois'])}; " + "; ".join(o_que) + ".")
    return out


def gerar_doc(linhas, tab1, tip, rdd, fm, d01, hashes, c3, banca) -> str:
    c3_md = "\n".join(
        f"| {r['modulo']} | {r['nivel']} | {num(r['mde_80_antes_failure_mode'], 2)} | **{num(r['mde_80_depois'], 2)}** | "
        f"{num(r['suporte_t_antes'])} / {num(r['suporte_c_antes'])} → {num(r['suporte_t_depois'])} / {num(r['suporte_c_depois'])} | "
        f"{'sim' if r['suporte_aprovado_antes'] else 'não'} → {'sim' if r['suporte_aprovado_depois'] else 'não'} | "
        f"{r['decisao_antes']} → **{r['decisao_depois']}** |" for r in c3)
    c3_mudou = [r for r in c3 if r["decisao_antes"] != r["decisao_depois"]]
    c3_texto = ("Nenhuma decisão do torneio muda." if not c3_mudou else
                "Decisões que mudam: " + "; ".join(f"{r['modulo']}/{r['nivel']}: {r['decisao_antes']} → {r['decisao_depois']}" for r in c3_mudou) + ".")
    c3_sup = [r for r in c3 if r["suporte_aprovado_antes"] != r["suporte_aprovado_depois"]]
    c3_sup_texto = ("" if not c3_sup else
                    " O suporte comum muda de aprovado para reprovado (ou o inverso) em " +
                    ", ".join(f"{r['modulo']}/{r['nivel']}" for r in c3_sup) + ", sem mudar a decisão.")
    cats = sorted(set(banca["antes_failure_mode"]) | set(banca["depois"]))
    banca_md = "\n".join(
        f"| {c} | {banca['antes_failure_mode'].get(c, {}).get('municipios', '—')} / {num(banca['antes_failure_mode'].get(c, {}).get('por_100k'), 2)} | "
        f"**{banca['depois'].get(c, {}).get('municipios', '—')} / {num(banca['depois'].get(c, {}).get('por_100k'), 2)}** |" for c in cats)
    e_ident = rdd["estimativas_identicas_byte_a_byte"]
    e_ident_md = "\n".join(f"| `{k}` | {'idêntico' if v else 'DIFERENTE'} |" for k, v in e_ident.items())
    blocos = list(dict.fromkeys(r["bloco"] for r in linhas))
    inalterados = [b for b in blocos if all(
        r["coef_antes_failure_mode"] is not None and r["coef_depois"] is not None
        and abs(r["coef_antes_failure_mode"] - r["coef_depois"]) <= 1e-9 * max(1.0, abs(r["coef_antes_failure_mode"]))
        for r in linhas if r["bloco"] == b)]
    aj = next(r for r in linhas if r["bloco"] == "A4 ajuste completo" and r["termo"] == "estrato_metropolitano")
    linhas_escolhidas = "\n".join(f"| {k} | {v} |" for k, v in fm["linha_escolhida_por_municipio"].items())
    t1 = "\n".join(f"| {r['variavel']} | {r['coluna']} | {num(r['antes_failure_mode'])} | **{num(r['depois'])}** |"
                   for r in tab1)
    secoes = "\n\n".join(f"### {b}\n\n{tabela_md(linhas, b)}" for b in blocos)
    conferir_leitura(linhas, inalterados, rdd)
    concl = conclusoes(linhas) or ["- Nenhuma estimativa muda de sinal nem cruza 5%."]
    auditoria_md = "\n".join(f"| `{a}` | {b} | {c} | {d} | {e} |" for a, b, c, d, e in AUDITORIA)
    hashes_md = "\n".join(f"| `{k}` | `{v}` |" for k, v in hashes.items())
    return f"""# Reestimação com a base oficial do IVS: registro do failure mode

> **Data:** 18/10/2026.<br>
> **Gerado por:** `scripts/tema_trabalho/12_registrar_failure_mode_ivs.py`. Todo número
> deste documento vem de `output/tema_trabalho/failure_mode_ivs_antes_depois.csv`,
> `output/tema_trabalho/failure_mode_ivs_resumo.json` ou dos artefatos citados. Os
> valores "antes" foram lidos do histórico do Git, no commit `{REF_ANTES[:12]}`, o
> último anterior à correção.<br>
> **Regra do autor:** "reestime tudo com os números certos, da base oficial. Os velhos
> só servem para serem documentados como failure mode e não devem ser usados para NADA
> no trabalho real." Os números da coluna "antes" deste documento têm esse estatuto:
> `FAILURE_MODE`. Não são citáveis como resultado.<br>
> **Antecedente:** [`16`](16_ivs_2010_oficial_e_arquivo_local.md) (o arquivo é uma linha
> de subgrupo); [`06_execucao/38`](../06_execucao/38_estado_e_pendencias_rdd_bolsa.md), D3.<br>
> **Protocolo:** tarefa E de [`06_execucao/40`](../06_execucao/40_protocolo_multioutcome_rdd_bolsa.md).

## 1. O que deu errado

`data/ivs_ipea_2010_municipios.csv` entrou no commit inicial do repositório sem script de
aquisição nem fonte. Ele vem da base completa do Atlas da Vulnerabilidade Social do Ipea,
mas não é a linha do município (cor, sexo e situação de domicílio "Total"): é, em cada
município, a última linha de 2010 com IVS preenchido, na ordem da planilha
(`{fm['fonte_mecanismo']}`):

| Linha da base que ficou no arquivo | Municípios |
|---|---:|
{linhas_escolhidas}

Comparado com o IVS oficial do município nos {milhar(fm['municipios'])} municípios, o arquivo
acerta o IVS a 3 casas em {fm['ivs_igual_3_casas']} e tem correlação de
{num(fm['correlacao_ivs'], 2)}. A coluna de população soma
{milhar(fm['populacao_2010_soma_arquivo_errado'])} habitantes, contra
{milhar(fm['populacao_2010_soma_oficial'])} da linha total (Censo 2010): é a população do
subgrupo.

## 2. Como se propagou

| Etapa | O que herdou | Uso |
|---|---|---|
| `scripts/aquisicao/04_harmonizar_territorio_ibge.py` → `malha_municipios_regioes_saude.parquet` | IVS, subíndices, categoria, IDHM, população 2010, renda | raiz da propagação |
| `scripts/aquisicao/05_integrar_painel_analitico.py` → painel município–curso mensal → `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet` e `A5_painel_T0.parquet` | `ivs_2010`, `ivs_categoria`, `populacao_2010` | covariável (b) |
| `scripts/tema_trabalho/03_construir_tipologia_territorial.py` (A2) | as mesmas colunas e `estoque_pre_por_10k`, dividido pela população do subgrupo | covariável (b); o estrato não dependia do arquivo |
| `scripts/tema_trabalho/05_estimar_atracao.py` (A4) | gradiente de IVS, `log_pop`, `estoque_por_10k` no ajuste completo, winsorizado, quadrático, IVS só e estrato × IVS | gradiente (a) e covariável (b) |
| `scripts/tema_trabalho/06_avaliar_provimento_cnes.py` (A5) | `ivs_2010`, `log_pop`, `estoque_por_10k` nas especificações completas e de heterogeneidade | covariável (b) |
| `scripts/avaliacao_impacto/07_gerar_tabelas_e_figuras.py` | IVS e população da Tabela 1 (descritiva) do ciclo 1 | descritivo (b) |
| `scripts/tema_trabalho/01_auditar_atracao_provimento_interior.py` | o veredito "regra não se reproduz" do script retirado `rdd_bolsa/00` | running variable (a), por via indireta |
| `scripts/tema_trabalho/07_red_team_sintese.py` → `docs/auditorias/09`, `docs/06_execucao/32` | o coeficiente do ajuste completo | texto |

A cadeia da RDD da bolsa (`rdd_bolsa/04b` em diante) já usava o IVS oficial desde 14/10/2026.

### Todos os leitores, diretos e indiretos

Classes: (a) running variable ou gradiente de IVS; (b) covariável; (c) só documenta ou
inventaria o erro, com rótulo; (d) retirado, fora do pipeline; (—) não lê nem herda.

| Script | Como chega ao arquivo | Classe | No `run_all.py` | Situação |
|---|---|---|---|---|
{auditoria_md}

O teste `tests/test_fonte_ivs_oficial.py` impede que um script novo do pipeline leia o
arquivo fora da lista de documentadores do failure mode.

## 3. Como foi detectado

Em 14/10/2026, o escore administrativo publicado pelo Ministério da Saúde não batia com o
arquivo local, mas batia com a linha total da base oficial do Ipea (a08). O script
`scripts/rdd_bolsa/04c_identificar_recorte_arquivo_local.py` reproduziu o arquivo inteiro a
partir da base oficial e identificou o erro de extração ([`16`](16_ivs_2010_oficial_e_arquivo_local.md)).
Naquela data a RDD passou a usar o IVS oficial, mas A2, A4, A5 e a Tabela 1 do ciclo 1
continuaram a ler a malha antiga; a decisão D3(b) adiou a reestimação, aplicada aqui.

## 4. O que foi corrigido

- A malha (`04_harmonizar`) lê IVS, subíndices, IDHM, população 2010 e renda da a08 e o
  código de 7 dígitos e a população 2022 do Censo 2022; manifesto em
  `output/aquisicao/manifesto_territorio_ibge.json`.
- A tipologia A2 ganha `populacao_2022`, denominador de `estoque_pre_por_10k`. O registro
  A3 mantém os hashes congelados em 02/09/2026 e recebe a emenda datada de 18/10/2026
  (correção de dado de entrada e de denominador), com os hashes dos insumos em vigor;
  especificação, amostras e desfechos não mudam.
- A4 e A5 foram reexecutados. A5 troca em memória as covariadas do painel em T0 congelado,
  que não é regravado (é a âncora de hash da reestimação).
- A Tabela 1 do ciclo 1 repõe IVS e população da a08.
- `tema_trabalho/01` confere a regra com o IVS oficial.
- O cenário "informado" de E2 e E4, cuja banda usava o arquivo errado, saiu das saídas
  ativas. E3, E5, a conferência do sinal, o relatório e a galeria da RDD foram
  reexecutados.
- O C3-03 do ciclo 3 recebeu emenda datada: propensão, suporte, pesos e potência com as
  covariadas oficiais, sobre os painéis CNES pré-T0 congelados (conferidos por hash),
  sem ler mês a partir de 202609.
- As figuras da banca 1 passam a usar a categoria de IVS da malha oficial.
- O Censo 2022 (`aquisicao/06`) entra no `run_all.py` antes da malha.
- Os artigos citam o ajuste completo corrigido, conferido contra `output/` pelos scripts
  `10` e `11`.

Tipologia: o estrato é idêntico antes e depois ({'sim' if tip['estrato_identico'] else 'NÃO'});
o estoque pré também ({'sim' if tip['estoque_pre_identico'] else 'NÃO'}). Depois da correção,
`ivs_2010` é igual ao IVS oficial em {tip['ivs_igual_ao_oficial_depois']} de
{tip['ivs_comparados_com_oficial']} municípios; antes e depois coincidem a 3 casas em
{tip['ivs_igual_antes_e_depois_3_casas']} e a categoria de IVS em
{tip['ivs_categoria_igual_antes_e_depois']} de {tip['municipios']}.

| Tipologia, população A1 ({tip['a1_municipios']} municípios) | Antes (failure mode) | Depois |
|---|---:|---:|
| IVS médio | {num(tip['a1_ivs_medio']['antes_failure_mode'])} | **{num(tip['a1_ivs_medio']['depois'])}** |
| População 2010 mediana | {milhar(tip['a1_populacao_2010_mediana']['antes_failure_mode'])} | **{milhar(tip['a1_populacao_2010_mediana']['depois'])}** |
| Estoque pré por 10 mil hab., mediana ({tip['quadro_municipios_com_estoque']} municípios do quadro) | {num(tip['quadro_estoque_pre_por_10k_mediana']['antes_failure_mode'], 2)} | **{num(tip['quadro_estoque_pre_por_10k_mediana']['depois'], 2)}** |

## 5. Antes e depois, por estimativa

Blocos sem covariadas contínuas, que servem de controle da reexecução (coeficientes
iguais a 1e-9): {', '.join(inalterados) if inalterados else 'nenhum'}.

{secoes}

### Tabela 1 do ciclo 1 (descritiva)

| Variável | Coluna | Antes (failure mode) | Depois |
|---|---|---:|---:|
{t1}

### RDD da bolsa (E1–E5)

Estimativas reexecutadas e comparadas byte a byte com as do commit `{REF_ANTES[:12]}`:

| Arquivo | Antes × depois |
|---|---|
{e_ident_md}

E2: {rdd['e2_linhas_antes']} → {rdd['e2_linhas_depois']} linhas ({rdd['e2_linhas_informado_retiradas']} do cenário
"informado" retiradas); o pior caso é {'idêntico' if rdd['e2_pior_caso_identico'] else 'DIFERENTE'}.
E4: {rdd['e4_linhas_antes']} → {rdd['e4_linhas_depois']} linhas ({rdd['e4_linhas_informado_retiradas']} do "informado"
retiradas); as demais são {'idênticas' if rdd['e4_demais_identicas'] else 'DIFERENTES'}. E3 e E5 registram o hash da
tipologia corrigida (E3: {'sim' if rdd['e3_registra_tipologia_nova'] else 'não'}; E5:
{'sim' if rdd['e5_registra_tipologia_nova'] else 'não'}).

### C3-03 do ciclo 3 (diagnósticos pré-tratamento)

| Módulo | Nível | MDE 80% antes (failure mode) | MDE 80% depois | Suporte retido T / C, antes → depois | Suporte aprovado | Decisão |
|---|---|---:|---:|---|---|---|
{c3_md}

{c3_texto}{c3_sup_texto}

### Figuras da banca 1: especialistas por 100 mil em 202506, por categoria de IVS (manifesto)

| Categoria de IVS | Antes (failure mode): municípios / por 100 mil | Depois |
|---|---|---|
{banca_md}

As figuras não usam essa quebra; ela só consta do manifesto.

### Diagnóstico do tema (`tema_trabalho/01`), módulo da RDD

- Antes (failure mode): "{d01['antes_failure_mode']}".
- Depois: "{d01['depois']}".

## 6. Que conclusões mudam

Mudanças de sinal ou de lado do limiar de 5% (p, ou q de FDR quando a tabela o publica):

{chr(10).join(concl)}

Leitura:
- **O gradiente territorial de A4 não muda.** O modelo principal, o logit, os estágios e o
  colapso município–curso não usam covariadas contínuas e são idênticos.
- **O ajuste completo enfraquece.** O contraste metropolitano cai de
  {num(100 * aj['coef_antes_failure_mode'], 1)} para {num(100 * aj['coef_depois'], 1)} p.p.;
  o p passa de {num(aj['p_antes_failure_mode'])} a {num(aj['p_depois'])} e o q de FDR dos
  três estratos, de {num(aj['q_antes_failure_mode'])} a {num(aj['q_depois'])}. A leitura
  "associado a maior atração mesmo com ajuste" vale só pelo p nominal.
- **O gradiente de IVS continua indistinguível de zero** condicional aos efeitos fixos, com
  ou sem estrato. A interação capital × IVS continua distinta de zero.
- **A5:** o estudo de evento, que é o resultado secundário citado, não muda. As
  especificações completas mudam pouco e nenhuma vira significante.
- **RDD da bolsa:** nenhuma estimativa muda (tabela da seção 5). O cenário "informado"
  de E2 e E4 deixa de existir nas saídas ativas.
- **C3-03 do ciclo 3:** {c3_texto[0].lower() + c3_texto[1:]}

## 7. Onde os números antigos ainda aparecem

Só como failure mode, rotulados:
- **este documento**, coluna "antes";
- `output/tema_trabalho/failure_mode_ivs_antes_depois.csv` e `failure_mode_ivs_resumo.json`;
- o histórico do Git até `{REF_ANTES[:12]}`;
- colunas `ivs_2010`, `ivs_categoria`, `populacao_2010` e `estoque_*` gravadas em
  `A5_painel_T0.parquet` e em `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet`,
  que não são regeneráveis sem o CNES mensal e não entram em nenhum modelo nem tabela
  (A5 e a Tabela 1 as substituem em memória);
- `output/rdd_bolsa/diagnostico_viabilidade_salario_ivs.json` e as saídas dos scripts
  retirados `rdd_bolsa/00`, `01`, `01b`, `02`, `03` e `aquisicao/a03`, `a06`;
- as linhas do cenário "informado" de E2 e E4, só no histórico do Git (saíram das saídas);
- a seção 6 de [`05_identificacao/13`](../05_identificacao/13_plano_pre_analise_ciclo3.md)
  (C3-03), com errata de failure mode;
- a errata E-7 de [`14`](14_erratas_artefatos_congelados.md), com nota de failure mode;
- [`16`](16_ivs_2010_oficial_e_arquivo_local.md), [`17`](17_guia_conferencia_manual_ivs.md)
  e a figura comparativa do relatório da RDD, que documentam o erro.

## 8. Proveniência

| Arquivo | SHA-256 |
|---|---|
{hashes_md}

*Gerado por `scripts/tema_trabalho/12_registrar_failure_mode_ivs.py`.*
"""


def main() -> None:
    linhas = comparar_tabelas()
    tab1 = comparar_tabela1()
    tip = comparar_tipologia()
    rdd = cadeia_rdd(tip)
    fm = failure_mode_arquivo()
    d01 = diag01()
    c3 = comparar_c3()
    banca = comparar_banca1()
    hashes = {str(p.relative_to(ROOT)): sha256(p) for p in
              [ARQUIVO_ERRADO, IVS_OFICIAL, CENSO2022, IDENT_04C, ROOT / TIPOLOGIA, E3_STATUS, E5_RESUMO]}
    hashes.update({rel: sha256(ROOT / rel) for rel in sorted({t[1] for t in TABELAS} | {TABELA1, DIAG_01})})

    tmp = OUT_CSV.with_suffix(".csv.tmp")
    pd.DataFrame(linhas).to_csv(tmp, index=False)
    tmp.replace(OUT_CSV)
    resumo = {
        "natureza_dos_dados": "EMPIRICO",
        "natureza_coluna_antes": "FAILURE_MODE (só documentação; não é resultado)",
        "ref_git_antes": REF_ANTES,
        "data_referencia": "2026-10-18",
        "arquivo_errado": fm,
        "tipologia": tip,
        "cadeia_rdd": rdd,
        "tabela1_ciclo1": tab1,
        "diagnostico_tema_01": d01,
        "c3_03_ciclo3": c3,
        "banca1_detalhe_por_categoria_ivs": banca,
        "mudancas_de_conclusao": conclusoes(linhas),
        "hashes_entradas": hashes,
    }
    OUT_JSON.write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DOC.write_text(gerar_doc(linhas, tab1, tip, rdd, fm, d01, hashes, c3, banca), encoding="utf-8")
    print(f"[OK] {len(linhas)} estimativas comparadas; {len(conclusoes(linhas))} mudanças de conclusão; "
          f"documento em {DOC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
