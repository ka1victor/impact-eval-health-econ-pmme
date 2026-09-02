"""A3 — Congela a pré-análise do núcleo associativo.

Fixa pergunta, população, outcome, covariadas, estimadores e linguagem antes
de qualquer estimação. Não consulta outcomes além do dicionário já publicado
em A1 (taxa por vaga proibida); potência é calculada sob p assumido.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "output" / "tema_trabalho"
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
MATRIZ_FUNIL = ROOT / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"
MATRIZ_TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
MALHA = ROOT / "output" / "aquisicao" / "malha_municipios_regioes_saude.parquet"
MANIFESTO_TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "manifesto_tipologia_territorial.json"
PORTAO_A1 = ROOT / "output" / "tema_trabalho" / "portao_denominador.json"

OUT_REGISTRO = OUT_DIR / "registro_pre_analise_atracao.json"
OUT_POTENCIA = OUT_DIR / "potencia_atracao.json"

ALPHA = 0.05
POWER = 0.80
Z_ALPHA = stats.norm.ppf(1 - ALPHA / 2)
Z_POWER = stats.norm.ppf(POWER)
# Mínima diferença relevante pre-especificada para atração binária
MIN_DIFF_PP = 0.10  # 10 pontos percentuais
MIN_DIFF_PP_STRICT = 0.05  # 5 pp como sensibilidade


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mde_proporcao(n: int, p: float = 0.5, deff: float = 1.0) -> float:
    """MDE bilateral para diferença de proporções vs baseline (aprox. 2*SE). Usa n total; assume divisão ~50/50 para MDE conservador."""
    # Para comparação de um estrato vs resto, n efetivo ~ 2 / (1/n1+1/n0) — mas aqui reportamos MDE marginal para um grupo vs 0 com n observações
    se = math.sqrt(p * (1 - p) / n) * math.sqrt(deff)
    return (Z_ALPHA + Z_POWER) * se


def mde_diferenca_dois_grupos(n1: int, n2: int, p: float = 0.5, deff: float = 1.0) -> float:
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) * math.sqrt(deff)
    return (Z_ALPHA + Z_POWER) * se


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in [QUADRO, MATRIZ_TIPOLOGIA, MALHA, MANIFESTO_TIPOLOGIA, PORTAO_A1]:
        if not p.exists():
            raise FileNotFoundError(p)

    quadro = pd.read_parquet(QUADRO)
    tipologia = pd.read_parquet(MATRIZ_TIPOLOGIA)
    manif_tip = json.loads(MANIFESTO_TIPOLOGIA.read_text(encoding="utf-8"))
    portao_a1 = json.loads(PORTAO_A1.read_text(encoding="utf-8"))

    # Guard: nunca ler outcome
    assert "outcome_alguma_confirmacao_ou_homologacao" not in quadro.columns

    # População congelada: células CNES–curso da oferta Ch1 (1295) como primária
    n_celulas_ch1 = int(len(quadro))
    n_municipios_ch1 = int(quadro["co_ibge_6d"].nunique())
    # População estendida (A1 funil = 3057 células Ch1+Ch2 versões) — para heterogeneidade chamada
    suporte = pd.read_csv(OUT_DIR / "suporte_estratos_territoriais.csv")
    # clusters: município é unidade de agrupamento da inferência
    m_medio = n_celulas_ch1 / n_municipios_ch1 if n_municipios_ch1 else float("nan")
    # ICC assumido para DEFF (conservador, pré-especificado sem estimar nos dados)
    icc_assumido = 0.05
    deff = 1 + (m_medio - 1) * icc_assumido if not math.isnan(m_medio) else 1.0

    # Distribuição por estrato (quadro Ch1)
    por_estrato = {}
    for _, row in suporte[suporte["estrato"] != "total"].iterrows():
        estr = str(row["estrato"])
        n = int(row["n_celulas_quadro_ch1"])
        g = int(row["n_municipios_populacao_A1"])  # aproxima clusters no estrato (pop A1 tem 540, mas quadro Ch1 tem subset)
        # Para MDE do estrato isolado (taxa vs 0) e diferença estrato vs resto
        # Usa DEFF do estrato (m = n / g)
        m_e = n / g if g else float("nan")
        deff_e = 1 + (m_e - 1) * icc_assumido if g and not math.isnan(m_e) else 1.0
        n_resto = n_celulas_ch1 - n
        por_estrato[estr] = {
            "n_celulas": n,
            "n_municipios": g,
            "m_medio_celulas_por_municipio": round(m_e, 2) if not math.isnan(m_e) else None,
            "deff_assumido": round(deff_e, 3),
            "mde_80_pp_p50": round(mde_proporcao(n, p=0.5, deff=deff_e), 4),
            "mde_80_pp_p30": round(mde_proporcao(n, p=0.30, deff=deff_e), 4),
            "mde_diferenca_vs_resto_p50": round(mde_diferenca_dois_grupos(n, n_resto, p=0.5, deff=deff_e), 4) if n_resto > 0 else None,
        }

    # MDE global
    potencia: dict[str, Any] = {
        "protocolo": "A3_POTENCIA_ATRACAO",
        "data_referencia": "2026-09-02",
        "amostra_primaria": {
            "unidade": "celula CNES-curso (quadro Ch1)",
            "n_celulas": n_celulas_ch1,
            "n_municipios_clusters": n_municipios_ch1,
            "m_medio_celulas_por_municipio": round(m_medio, 2),
            "icc_assumido": icc_assumido,
            "deff_assumido": round(deff, 3),
            "nota": "Potência sob p assumido (0.30 plausível, 0.50 conservador); sem consultar outcome observado. DEFF = 1+(m-1)*ICC.",
        },
        "alfa_bilateral": ALPHA,
        "poder_alvo": POWER,
        "p_assumido_plausivel": 0.30,
        "p_assumido_conservador": 0.50,
        "minima_diferenca_relevante_pp": MIN_DIFF_PP,
        "sensibilidade_5pp": MIN_DIFF_PP_STRICT,
        "mde_global": {
            "mde_80_pp_p50": round(mde_proporcao(n_celulas_ch1, p=0.5, deff=deff), 4),
            "mde_80_pp_p30": round(mde_proporcao(n_celulas_ch1, p=0.30, deff=deff), 4),
        },
        "por_estrato": por_estrato,
        "interpretacao": {
            "regra": f"MDE <= {MIN_DIFF_PP:.0%} é bem potenciado para 10pp; MDE > 10pp indica poder limitado para heterogeneidade fina por estrato/curso.",
            "cursos": "Cursos com <50 células terão MDE >15pp mesmo sob p=0.30; análise por curso será descritiva ou agrupada.",
            "ufs": "UFs com poucos municípios exigem agrupamento por região; não estimar efeito UF isolado com <10 clusters.",
        },
    }

    # Registro de pré-análise
    registro: dict[str, Any] = {
        "protocolo": "A3_REGISTRO_PRE_ANALISE_ATRACAO",
        "data_referencia": "2026-09-02",
        "efeitos_estimados": False,
        "pergunta": "Quais características territoriais e das vagas estão associadas à dificuldade de preenchimento (alguma confirmação/homologação observada na célula) e, condicionalmente, à persistência da oferta médica local?",
        "populacao": {
            "primaria": "1295 células CNES–curso do quadro Ch1 (ciclo 1, chamada 1, oferta 2025-07-24), em 368 municípios",
            "estendida": "3057 células do funil A1 (Ch1 1324 + Ch2 1999 linhas, 266 fora do quadro sem município excluídas da tipologia)",
            "exclusoes": "266 registros fora do quadro publicado sem município na matriz A1; 5 municípios novos pós-2010 mantêm estrato mas sem IVS",
            "unidade_analitica": "célula CNES–curso (chamada mantida como covariada/estratificação; não somar versões como vagas novas)",
            "unidade_inferencia": "município (cluster-robusto; exposição varia no município, células do mesmo município não são independentes)",
        },
        "outcome_primario": {
            "nome": "alguma_confirmacao_ou_homologacao_na_celula",
            "definicao": "1[ n_confirmacoes_ch1 >0 ou n_homologacoes_ch1 >0 na célula CNES–curso da chamada ] (A1 APROVADO_CELULA)",
            "tipo": "binário por célula",
            "denominador": "célula (não taxa por vaga; taxas com vagas no denominador permanecem proibidas)",
            "outcomes_bloqueados": portao_a1["decisao"]["outcomes_bloqueados"],
            "chamada": "Ch1 primária; Ch2 descritiva sem taxa por vaga (Ch2 não publica vagas imediatas numéricas)",
        },
        "outcomes_secundarios_condicionais": {
            "nota": "Somente após validar T0 físico do CNES; não nesta etapa",
            "candidatos": [
                "estoque_especialistas_municipio_curso_mes (CNES, agregado)",
                "persistência da oferta local (presença em 6m, stock)",
            ],
            "bloqueados_hoje": ["retenção individual do bolsista (sem ponte PMM-E–CNES)", "fila/candidaturas por vaga (sem universo de inscrições)"],
        },
        "tipologia_congelada": {
            "fonte": "A2 APROVADO_4_ESTRATOS — REGIC 2018 + RM/RIDE 2022",
            "estratos": ["capital", "metropolitano", "interior_proximo_polo", "interior_remoto"],
            "cobertura_A1": "540/540",
            "uso": "heterogeneidade pre-especificada (efeito por estrato) e covariada; não redefinir após resultados",
        },
        "covariadas_exclusivamente_pre_oferta": {
            "permitidas": [
                "estrato A2 (4 níveis)",
                "ivs_2010 (canônico), ivs_subindices (infra/ch/rt), ivs_categoria",
                "populacao_2010 (log), rdpc_2010, idhm_2010 (descritivo)",
                "macro_regiao_saude, no_regiao_saude",
                "estoque_especialistas_pre_12m_media (CNES 202407–202506) e por 10k",
                "faixa_atracao_anunciada (F1/F2/F3) — descritiva, não efeito causal de salário",
                "cod_curso (16 níveis), sg_uf",
                "chamada (quando Ch1+Ch2)",
            ],
            "proibidas": [
                "qualquer variável pós-oferta (alocação, homologação, CNES pós 202507)",
                "id_vaga física (inexistente), taxa por vaga como outcome",
                "substituição de IVS por IDHM/RDPC sem justificativa",
            ],
            "tratamento_missing": "municípios novos pós-2010: IVS NA mantido, estrato via REGIC/RM; estoque pré NA mantido; NAO_CLASSIFICADO exigiria fallback — não ocorreu (0 casos em A1)",
            "outliers": "população e estoque winsorizados apenas como sensibilidade pre-especificada (p99), não como default",
            "transformacoes": "log1p(populacao_2010); IVS linear + splines como sensibilidade; padronização apenas para regularização se usada",
        },
        "especificacao": {
            "modelos_candidatos_primarios": [
                "LPM com FE de curso e UF, cluster município (primário por interpretabilidade direta em pp)",
                "Logit com FE de curso e UF, AME, cluster município (primário alternativo; OR apenas como robustez)",
            ],
            "modelos_secundarios_robustez": [
                "Binomial com denominador =1 por célula (equivale a logit por célula; fractional logit se taxa tivesse denominador válido — não se aplica aqui)",
                "Poisson/NB apenas para contagens com exposição bem definida (n_confirmacoes como contagem, offset log(1) trivial — descritivo)",
            ],
            "efeitos_fixos": "curso (16) e UF (até 27, colapsar UF com <5 clusters em região); chamada quando Ch1+Ch2",
            "heterogeneidade_pre_especificada": "estrato A2 (4 níveis) interagido com IVS contínuo; curso como modificador descritivo (não testar 16 hipóteses independentes)",
            "pesos": "não ponderar por vagas (denominador inválido); pesos por estrato/UF apenas como sensibilidade com estimando redefinido explicitamente",
            "multiplicidade": "controle FDR (Benjamini-Hochberg) para família de 4 estratos; cursos como exploração, não confirmatória",
            "influencia": "leave-one-municipality-out e DFBETAS clusterizados como diagnóstico; não remover outliers influentes do primário",
        },
        "inferencia": {
            "unidade_cluster": "município (co_ibge_6d)",
            "metodo": "HC cluster-robusto (LPM/logit) com G clusters; se G<30 em subgrupo, reportar também wild cluster bootstrap",
            "graus_liberdade": "G-1",
            "nao_fazer": "não usar SE robusto apenas heterocedástico sem cluster; não tratar células do mesmo município como independentes",
        },
        "potencia_e_relevancia": {
            "minima_diferenca_relevante": f"{MIN_DIFF_PP:.0%} (10pp) na taxa de atração binária; sensibilidade 5pp",
            "referencia_potencia": "output/tema_trabalho/potencia_atracao.json (p assumido 0.30/0.50, DEFF com ICC=0.05)",
            "regra_interpretacao": "MDE >10pp => poder limitado para afirmar nulidade; reportar IC e não apenas p-valor",
        },
        "separacao_explicacao_previsao": {
            "explicacao_associativa": "coeficientes parciais de estrato/IVS ajustados por curso/UF; linguagem associativa (associado a, gradiente), nunca causal",
            "previsao": "apenas se pre-especificada com validação cruzada fora da amostra (k-fold por município); métricas AUC/Brier para LPM/logit, não R2 in-sample como prova",
            "proibido": "chamar coeficiente de faixa de bolsa de efeito do salário; chamar coeficiente de IVS de efeito da vulnerabilidade",
        },
        "linguagem_maxima": {
            "permitido": "atração administrativa (alguma confirmação/homologação observada), preenchimento parcialmente observável, gradiente territorial, persistência da oferta local (quando CNES validado)",
            "proibido": "taxa de preenchimento por vaga, retenção individual do bolsista, efeito causal do PMM-E/bolsa/IVS, candidaturas por vaga",
        },
        "hashes_entradas": {
            str(p.relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(p)}
            for p in [QUADRO, MATRIZ_TIPOLOGIA, MALHA, MANIFESTO_TIPOLOGIA, PORTAO_A1]
        },
        "hashes_artefatos_A1_A2": {
            str((OUT_DIR / "matriz_funil_ciclo1.parquet").relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(MATRIZ_FUNIL)},
            str((OUT_DIR / "suporte_estratos_territoriais.csv").relative_to(ROOT)).replace("\\", "/"): {"sha256": sha256(OUT_DIR / "suporte_estratos_territoriais.csv")},
        },
        "portao_para_A4": "Não executar A4 sem este registro assinado por hash e sem MDE reportado; qualquer desvio deve ser emendado e datado.",
    }

    # Escrita atômica
    tmp_r = OUT_REGISTRO.with_suffix(".json.tmp")
    tmp_r.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_r.replace(OUT_REGISTRO)

    tmp_p = OUT_POTENCIA.with_suffix(".json.tmp")
    tmp_p.write_text(json.dumps(potencia, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_p.replace(OUT_POTENCIA)

    # Seção econométrica congelada — apêndice para documento principal
    secao_path = ROOT / "docs" / "06_execucao" / "31_secao_econometrica_A3.md"
    secao_path.parent.mkdir(parents=True, exist_ok=True)
    secao = f"""# Seção econométrica congelada — A3 (02/09/2026)

> Registro: `output/tema_trabalho/registro_pre_analise_atracao.json`
> Potência: `output/tema_trabalho/potencia_atracao.json`
> Tipologia: A2 `APROVADO_4_ESTRATOS` — 540/540 municípios

**Pergunta.** Quais características territoriais e das vagas estão associadas ao
preenchimento administrativo (alguma confirmação/homologação na célula) e,
condicionalmente, à persistência da oferta local?

**População.** 1.295 células CNES–curso do quadro Ch1 (368 municípios) como
primária; 3.057 células do funil A1 como estendida.

**Outcome primário.** Binário por célula: `1[n_confirmacoes_ch1>0 ou n_homologacoes_ch1>0]`.
Taxa por vaga permanece proibida (A1).

**Unidade de inferência.** Município (cluster-robusto; FE de curso e UF).

**Modelos.** LPM (primário) e logit/AME (alternativo); binomial/logit por célula;
Poisson/NB apenas descritivo para contagens.

**Covariadas.** Estrato A2, IVS 2010 canônico (+ subíndices), log(pop 2010),
região de saúde, estoque pré 202407–202506, faixa anunciada, curso, UF, chamada.

**Potência.** Global MDE 80% ≈ {potencia['mde_global']['mde_80_pp_p30']:.1%} (p=0.30)
a {potencia['mde_global']['mde_80_pp_p50']:.1%} (p=0.50) com DEFF={potencia['amostra_primaria']['deff_assumido']};
por estrato: remoto ≈ {por_estrato['interior_remoto']['mde_80_pp_p30']:.1%},
metropolitano ≈ {por_estrato['metropolitano']['mde_80_pp_p30']:.1%}. Mínima
relevante 10pp (sens. 5pp).

**Linguagem.** Associativa apenas; sem efeito causal do PMM-E/bolsa/IVS.
"""
    tmp_s = secao_path.with_suffix(".md.tmp")
    tmp_s.write_text(secao, encoding="utf-8")
    tmp_s.replace(secao_path)

    print(f"[OK] A3 congelado: registro em {OUT_REGISTRO.name}, potência em {OUT_POTENCIA.name}")
    print(f"     Global MDE 80% (p=0.30): {potencia['mde_global']['mde_80_pp_p30']:.1%} | DEFF {potencia['amostra_primaria']['deff_assumido']}")


if __name__ == "__main__":
    main()
