"""Protocolo 61: por que o preenchimento cai no corte 0,300? Diagnóstico pós-resultado (D-a a D-g).

Especificação: `docs/06_execucao/61_protocolo_diagnostico_queda_0300.md`, congelado em 26/10/2026 antes de qualquer
conta. Estatuto `DIAGNOSTICO_61_POS_RESULTADO`: nada aqui vira especificação principal nem muda o Holm ou a leitura
dos protocolos 40 e 48. Toda linha sai com `natureza_dos_dados = EMPIRICO`.

O que o script faz, na ordem
----------------------------
1. Reproduz Q1, Q2 e Q3 em 0,300 e 0,400 com as especificações e as entradas dos protocolos 48 (§3, §7) e do ND:
   - Q1 = N1 com o controle das vagas oferecidas (S-a), ciclos 1–3 juntos, por corte;
   - Q2 = taxa N1 ÷ vagas oferecidas, ponderada pelas vagas (S-e);
   - Q3 = A3, célula aberta preenchida, efeitos fixos de curso × ciclo e tipo de vaga.
   Os valores têm de bater com `N_estimativas.csv`, `NA_estimativas.csv` e `ND_estimativas.csv` (tolerância 1e-9).
   Se não baterem, o script para sem gravar nada.
2. Roda a lista fechada D-a a D-g, sempre em 0,300 e em 0,400 (contraste):
   - D-a, acaso: cortes placebo (0,250 a 0,450, passo 0,005, sem os pontos a menos de h dos cortes reais) e
     randomização local de Fisher (±0,010 e ±0,020, 999 permutações, semente 20261026);
   - D-b, composição das vagas: saltos da composição; Q3 com e sem a composição; Q2 sem as células só de CR;
   - D-c, funil: ter candidato de 1ª opção e preencher dado o candidato; motivo de não alocação onde a base distingue;
   - D-d, concorrência: células do mesmo curso e ciclo na região de saúde e na UF, e a bolsa delas;
   - D-e, médicos por perto: vínculos pré das CBO do curso na região de saúde, distância à origem dos candidatos
     (G1), hierarquia urbana (REGIC);
   - D-f, ciclo 2 e cadastro reserva: Q2 do ciclo 2 com e sem as células só de CR, só com vagas imediatas, contagem
     das células só de CR e a regra arquivada do ciclo 2;
   - D-g, outras políticas em 0,300: balanço de generalistas e de vínculos SUS pré e a lista da auditoria 18.
3. Monta a tabela "quanto da queda cada explicação leva" e aplica a leitura pré-registrada (§3 do protocolo).

Integridade
-----------
Nada imputado nem simulado; ausente fica ausente e é contado. Running variable = IVS 2010 oficial (a08); o arquivo
local de IVS da auditoria 16 não é lido. O CNES só é lido no pré (202406–202506); a origem dos candidatos vem do
G1 já gravado (competência de referência de cada ciclo, nenhuma posterior a 202609). As listas de candidatos (G1,
escolhas) só são usadas agregadas, em memória: nenhum identificador de pessoa vai para `output/`. As saídas de outros
blocos não são regravadas. Tudo é descritivo e pós-resultado; o contraste é o pacote do corte.

Uso
---
    python3 scripts/rdd_bolsa/38_diagnostico_queda_0300.py
    python3 scripts/rdd_bolsa/38_diagnostico_queda_0300.py --atualizar-doc
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
ND = _importar(DIR_RDD / "23b_diagnostico_contagem_porte.py", "nd_para_dq")
T24 = _importar(DIR_RDD / "24_abertura_vagas_selecao.py", "abertura_para_dq")
T29 = _importar(DIR_RDD / "29_determinantes_abertura.py", "determinantes_para_dq")
T32 = _importar(DIR_RDD / "32_realocacao_bolsa.py", "realocacao_para_dq")
sys.dont_write_bytecode = _bytecode
T23, L, E6 = ND.T23, ND.L, ND.E6
X1 = T32.X1

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo 61 (constantes permitidas: cortes, h, grade placebo, janelas, semente)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
NOME_EST = "DQ_estimativas.csv"
NOME_RESUMO = "DQ_resumo.json"
DIR_FIG = "DQ_figuras"
DOC = ROOT / "docs" / "06_execucao" / "57l_diagnostico_queda_0300.md"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "61_protocolo_diagnostico_queda_0300.md"
AUDITORIA_18 = ROOT / "docs" / "auditorias" / "18_politicas_nos_mesmos_cortes_ivs.md"
N_EST = OUT / "N_estimativas.csv"
NA_EST = OUT / "NA_estimativas.csv"
ND_EST = OUT / "ND_estimativas.csv"
G1_ORIGEM = OUT / "G1_candidatos_origem.parquet"
G1_RESUMO = OUT / "G1_resumo.json"
ESCOLHAS = OUT / "outcomes" / "escolhas_candidatos.parquet"
QUADRO_CONSOLIDADO = ROOT / "output" / "aquisicao" / "quadro_vagas_consolidado.parquet"
ARQ_CNES = ROOT / "output" / "aquisicao" / "cnes_nacional" / "painel_municipio_cbo_mes.parquet"
# D-f: o que está arquivado do ciclo 2 (só leitura).
EDITAL_C2_PAGINA = ROOT / "data" / "raw" / "aquisicao" / "ivs_regra" / "edital_sgtes_01_2026_ciclo2.html"
QUADRO_C2_ORIGINAL = ROOT / "data" / "raw" / "aquisicao" / "vagas" / "2026_ciclo2_chamada1_vagas_e_servicos_original.xlsx"
RESULTADO_C2 = ROOT / "data" / "raw" / "pmm_e" / "resultado-final-pmme-2o-ciclo-25-05.xlsx"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "DIAGNOSTICO_61_POS_RESULTADO"
NATUREZA = "EMPIRICO"
ROT_PROTOCOLO = "PROTOCOLO_61"
ROT_COMPLEMENTAR = "COMPLEMENTAR_FORA_DO_PROTOCOLO_61"
CORTES = L.CORTES_MIL                  # (300, 400)
CICLOS = (1, 2, 3)
H = L.H_PRINCIPAL_MIL                  # 50
RC = T23.ROTULO_CORTE                  # {300: "0.300", 400: "0.400"}
GRADE_PLACEBO = tuple(range(250, 451, 5))
PLACEBOS = tuple(c for c in GRADE_PLACEBO if all(abs(c - k) >= H for k in CORTES))   # "sem os pontos a menos de h"
PLACEBOS_COMPLEMENTARES = tuple(c for c in GRADE_PLACEBO if all(abs(c - k) > 10 for k in CORTES))
JANELAS_FISHER = (10, 20)
N_PERM = 999
SEMENTE = 20261026
COMP_PRE = ("202406", "202506")
LIMITE_CNES = "202609"
POR_HAB = 1e4
LIMIAR_METADE = 0.5
# Correção de 26/10/2026 (auditoria 36; adendo 48b, §7): o quadro do ciclo 2 usado aqui (retificado de 19/03/2026)
# foi refeito depois do resultado preliminar. A frase de que, no ciclo 2, a vaga de reserva não podia ser preenchida
# na 1ª chamada descreve esse quadro, não a regra; pelo quadro de 13/02/2026, vigente na inscrição, havia alocados em
# células só de reserva. Texto, sem número de resultado.
REF_A36 = ("[auditoria 36](../auditorias/36_auditoria_dados_H1.md); "
           "[adendo 48b, §7](48b_adendo_H1_vagas_imediatas.md)")
QUADRO_C2_POS = "quadro de 19/03/2026, refeito depois do resultado preliminar"
NOTA_A36_BANCA = (f"*Correção de 26/10/2026 ({REF_A36}).* A versão anterior desta frase dizia que, no ciclo 2, a vaga "
                  "de reserva não podia ser preenchida na 1ª chamada. Isso descreve o quadro de 19/03/2026, refeito "
                  "depois do resultado preliminar; pelo quadro de 13/02/2026, vigente na inscrição, havia alocados do "
                  "ciclo 2 em células só de reserva.")
NOTA_A36_DF = (f"**Correção de 26/10/2026 ({REF_A36}).** Isso não mostra que a reserva não podia ser preenchida na 1ª "
               "chamada, como dizia a versão anterior deste parágrafo. O quadro de 19/03/2026 foi refeito depois do "
               "resultado preliminar e converteu em imediatas vagas de reserva onde houve alocado; pelo quadro de "
               "13/02/2026, vigente na inscrição, havia alocados do ciclo 2 em células só de reserva.")
# Aviso de 27/10/2026 (auditoria 51, achado C2): como o quadro de 19/03/2026 converteu em imediatas as vagas de
# reserva onde houve alocado, tirar dele as células só de CR do ciclo 2 condiciona no resultado. Texto, sem número.
REF_SELECAO = (f"{REF_A36}; [adendo 48f](48f_adendo_selecao_tipo_de_vaga.md), seleção pelo tipo de vaga")
AVISO_SELECAO_C2 = ("Como esse quadro converteu em imediatas as vagas de reserva onde houve alocado, tirar dele as "
                    "células só de CR condiciona no resultado: essa linha não decompõe a queda com o tipo de vaga "
                    f"medido antes da alocação (aviso de 27/10/2026: {REF_SELECAO}).")
AVISO_SELECAO_DF = (f"*Aviso de 27/10/2026 ({REF_SELECAO}).* No ciclo 2, as linhas sem as células só de CR (nesta "
                    "tabela, na D-b (iii) e na §10) e a linha só com vagas imediatas usam o quadro de 19/03/2026, "
                    "refeito depois do resultado preliminar, que converteu em imediatas as vagas de reserva onde houve "
                    "alocado. Por isso, tirar as células só de CR desse quadro condiciona no resultado, e essas linhas "
                    "não decompõem a queda com o tipo de vaga medido antes da alocação.")
Q = ("Q1", "Q2", "Q3")
DESC_Q = {
    "Q1": "N1 com o controle das vagas oferecidas (S-a), ciclos 1-3 juntos",
    "Q2": "taxa N1 / vagas oferecidas, ponderada pelas vagas (S-e), ciclos 1-3 juntos",
    "Q3": "A3: celula aberta preenchida, efeitos fixos de curso x ciclo e tipo de vaga, ciclos 1-3 juntos",
}
UN_Q = {"Q1": "vagas preenchidas por municipio", "Q2": "fracao (x100 = p.p.)", "Q3": "fracao (x100 = p.p.)"}
CONTRASTE = E6.CONTRASTE
FAIXA_BOLSA_MIL = None   # preenchido por carregar() a partir das grades (E9.mapa_bolsa_por_faixa, via 32)

EXPLICACOES = [
    {"id": "D-a", "nome": "acaso", "teste": "cortes placebo de 0,250 a 0,450 (passo 0,005, sem os pontos a menos de "
     "h = 0,050 dos cortes reais), mesma especificacao de Q1-Q3; p por posto e fracao com |t| > 1,96; randomizacao "
     "local de Fisher (999 permutacoes, semente 20261026) em +-0,010 e +-0,020", "apoio": "p por posto > 0,10"},
    {"id": "D-b", "nome": "composicao das vagas", "teste": "(i) salto da composicao por ciclo; (ii) Q3 com efeitos "
     "fixos de curso x ciclo, indicador de so CR, tipo e gestao do estabelecimento contra Q3 sem eles; (iii) Q2 sem "
     "as celulas so de CR", "apoio": "o salto cai pela metade ou mais ao fixar a composicao"},
    {"id": "D-c", "nome": "funil", "teste": "Q3 = P(candidato de 1a opcao) e P(preenchida | candidato); motivo de nao "
     "alocacao onde a base distingue", "apoio": "a queda se concentra numa das partes"},
    {"id": "D-d", "nome": "concorrencia", "teste": "celulas do mesmo curso e ciclo na regiao de saude e na UF e a "
     "bolsa delas: salto no corte e Q3 controlando por elas",
     "apoio": "as medidas saltam no corte e controlar por elas reduz o salto"},
    {"id": "D-e", "nome": "medicos por perto", "teste": "balanco pre-determinado: vinculos pre das CBO do curso na "
     "regiao de saude por 10 mil hab.; distancia a origem mais proxima entre os candidatos (G1); REGIC",
     "apoio": "as medidas saltam no corte e controlar por elas reduz o salto"},
    {"id": "D-f", "nome": "ciclo 2 e cadastro reserva", "teste": "ciclo 2: Q2 com e sem as celulas so de CR; Q2 so "
     "com vagas imediatas; n de celulas so de CR de cada lado; regra arquivada do ciclo 2",
     "apoio": "a queda do ciclo 2 some sem as celulas so de CR"},
    {"id": "D-g", "nome": "outras politicas em 0,300", "teste": "sem teste causal; balanco de generalistas pre e de "
     "vinculos SUS totais pre por 10 mil hab.; regras da auditoria 18 que mudam em 0,300 e nao em 0,400",
     "apoio": "— (relato)"},
]

# D-g: regras da auditoria 18 (§2.5, §2.6 e §3), com a âncora de texto que o teste confere no documento.
REGRAS_AUDITORIA_18 = [
    {"regra": "acrescimo de 20% no teto de emendas e de parcelas de custeio da APS (PAP) e da MAC para IVS maior que "
              "0,3 (Portarias 3.283/2024 e seguintes, exercicios 2024-2027)",
     "em_0300": "sim", "em_0400": "nao", "fronteira": "a mesma da bolsa (0,300 fica de fora)",
     "secao": "§2.6", "ancora": "**Só 0,300.** Não há regra em 0,400."},
    {"regra": "estrato do IED do cofinanciamento federal da APS (Portaria 3.493/2024): muda em 0,300 so nos portes 2 "
              "e 3; em 0,400, nos portes 1, 2 e 4 (o porte 3, de 50 a 100 mil hab., so muda em 0,300)",
     "em_0300": "sim (portes 2 e 3)", "em_0400": "sim (portes 1, 2 e 4)", "fronteira": "a mesma da bolsa",
     "secao": "§2.5", "ancora": "Em **0,300** (baixa → média): porte 2 e 3"},
    {"regra": "texto da Portaria 752/2023 (teto de vagas do PMMB em coparticipacao), incentivo de nutricao "
              "(5.721/2024) e priorizacao de eMulti (635/2023)",
     "em_0300": "sim", "em_0400": "sim", "fronteira": "oposta a da bolsa (classe de cima)",
     "secao": "§2.1, §2.7 e §3", "ancora": "texto da 752 (10% → 40% de teto de coparticipação, fronteira oposta)"},
]

COLUNAS = [
    "natureza_dos_dados", "estatuto", "rotulo", "id_linha", "explicacao", "bloco", "tipo_linha", "quantidade",
    "outcome", "descricao", "unidade_analise", "populacao", "ciclo", "corte", "corte_placebo", "especificacao",
    "variante", "covariaveis", "efeitos_fixos", "estimador", "h", "janela", "status", "n_abaixo", "n_acima", "n_obs",
    "n_clusters", "n_fora", "motivo_fora", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "t", "q_bky",
    "media_abaixo", "media_acima", "tau_original", "tau_original_mesma_amostra", "razao_fixado_original",
    "reduz_metade", "p_posto", "frac_t_maior_196", "n_placebos", "n_perm", "semente", "valor", "valor_abaixo",
    "valor_acima", "alvo_tau", "alvo_ep", "dif_max", "unidade", "nota",
]


class FalhaValidacao(RuntimeError):
    """Conferência que falhou: o script para sem gravar."""


sha256, rotulo = E6.sha256, E6.rotulo


def _juntar(*notas) -> str:
    return "; ".join(str(n) for n in notas if n)


# ---------------------------------------------------------------------------
# Linhas
# ---------------------------------------------------------------------------

def nova(expl: str, bloco: str, tipo: str, quant: str, corte: str, *, pop: str = "", ciclo: str = "1+2+3",
         esp: str = "", var: str = "", unidade_analise: str = "", **kw) -> dict:
    ln = {c: np.nan for c in COLUNAS}
    ln.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "rotulo": ROT_PROTOCOLO, "explicacao": expl,
               "bloco": bloco, "tipo_linha": tipo, "quantidade": quant, "corte": corte, "populacao": pop,
               "ciclo": ciclo, "especificacao": esp, "variante": var, "unidade_analise": unidade_analise,
               "status": "EXECUTADO", "nota": "", "outcome": "", "descricao": "", "covariaveis": "",
               "efeitos_fixos": "", "estimador": "", "motivo_fora": "", "unidade": "", "reduz_metade": ""})
    ln.update(kw)
    cp = kw.get("corte_placebo", "")
    ln["id_linha"] = "|".join(str(x) for x in (expl, bloco, tipo, quant, pop, ciclo, corte, esp, var,
                                                 "" if pd.isna(cp) else cp))
    return ln


def preencher(ln: dict, r: dict | None) -> dict:
    if r is None:
        ln["status"] = "NAO_EXECUTADO"
        return ln
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters"):
        if r.get(k) is not None:
            ln[k] = r[k]
    if np.isfinite(float(ln["tau"])) and np.isfinite(float(ln["ep"])) and float(ln["ep"]) > 0:
        ln["t"] = float(ln["tau"]) / float(ln["ep"])
    ln["nota"] = _juntar(ln.get("nota", ""), r.get("nota", ""),
                         f"colunas descartadas: {r['covariaveis_descartadas']}" if r.get("covariaveis_descartadas") else "")
    if not np.isfinite(float(ln["tau"])):
        ln["status"] = "SEM_ESTIMATIVA"
        if not ln["nota"]:
            ln["nota"] = "biblioteca devolveu NaN sem motivo"
    return ln


# ---------------------------------------------------------------------------
# Dados (só output/ e brutos de data/ apenas lidos)
# ---------------------------------------------------------------------------

def _normal_ibge(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\D", "", regex=True).str.zfill(6).str[:6]


def _media_ponderada(df: pd.DataFrame, col: str, peso: str, chaves: list[str]) -> pd.Series:
    """Média de `col` ponderada por `peso` nas linhas com `col` definido; ausente se nenhuma linha tem `col`."""
    ok = df[col].notna()
    num = (df[col].where(ok, 0.0) * df[peso].where(ok, 0.0)).groupby([df[c] for c in chaves]).sum()
    den = df[peso].where(ok, 0.0).groupby([df[c] for c in chaves]).sum()
    return (num / den.where(den > 0)).rename(col)


def ler_cnes_sus_pre(universo: list[str]) -> tuple[pd.Series, dict]:
    """Média mensal de vínculos SUS de todos os médicos (a09, grupo todos_medicos), 202406–202506."""
    import pyarrow.parquet as pq
    t = pq.read_table(ARQ_CNES, columns=["co_ibge", "competencia", "grupo", "n_vinculos_sus", "natureza_dos_dados"],
                      filters=[("competencia", ">=", COMP_PRE[0]), ("competencia", "<=", COMP_PRE[1]),
                               ("grupo", "=", "todos_medicos")]).to_pandas()
    comps = sorted(t["competencia"].astype(str).unique().tolist())
    if not comps or comps[0] < COMP_PRE[0] or comps[-1] > COMP_PRE[1] or comps[-1] >= LIMITE_CNES:
        raise FalhaValidacao(f"CNES fora da janela pre: {comps[:1]}..{comps[-1:]}")
    if set(t["natureza_dos_dados"].astype(str)) != {NATUREZA}:
        raise FalhaValidacao("CNES com natureza diferente de EMPIRICO")
    g = t.groupby("co_ibge")["n_vinculos_sus"].agg(["mean", "count"])
    g.loc[g["count"] != len(comps), "mean"] = np.nan
    g.index = g.index.astype(str).str.zfill(6)
    s = g["mean"].reindex(universo)
    return s, {"competencias": comps, "n_competencias": len(comps),
               "municipios_sem_media_completa": int(s.isna().sum()),
               "medida": "media mensal de n_vinculos_sus do grupo todos_medicos (a09), 202406-202506"}


def gestao_por_celula(cel: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Gestão do estabelecimento (municipal, estadual, dupla) no quadro da 1ª chamada do ciclo, por CNES."""
    q = pd.read_parquet(QUADRO_CONSOLIDADO, columns=["ciclo", "chamada", "tipo_documento", "co_cnes_7d",
                                                     "tipo_gestao"])
    q = q[(q["tipo_documento"] == "OFERTA_VAGAS") & (q["chamada"] == 1)].copy()
    q["co_cnes_7d"] = q["co_cnes_7d"].astype(str)
    q["tipo_gestao"] = q["tipo_gestao"].astype(str).str.strip().replace({"": np.nan, "nan": np.nan, "None": np.nan})
    n = q.groupby(["ciclo", "co_cnes_7d"])["tipo_gestao"].nunique()
    conflito = set(n[n > 1].index)
    m = q.dropna(subset=["tipo_gestao"]).drop_duplicates(["ciclo", "co_cnes_7d"]).set_index(
        ["ciclo", "co_cnes_7d"])["tipo_gestao"]
    chave = list(zip(cel["ciclo"].astype(int), cel["co_cnes_7d"].astype(str)))
    s = pd.Series([np.nan if k in conflito else m.get(k, np.nan) for k in chave], index=cel.index, dtype=object)
    return s, {"fonte": rotulo(QUADRO_CONSOLIDADO), "regra": "tipo_gestao do quadro OFERTA_VAGAS da 1a chamada do "
               "ciclo, por (ciclo, CNES); CNES com gestoes diferentes no mesmo ciclo fica ausente",
               "cnes_com_conflito": len(conflito), "celulas_sem_gestao": int(s.isna().sum())}


def tipo_por_celula(cel: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Tipo do estabelecimento: atributo do CNES no cardápio de gestores do ciclo 3 (a única fonte arquivada)."""
    card = T29.ler_cardapio_com_atributos()
    n = card.groupby("co_cnes_7d")["tipo"].nunique()
    if (n > 1).any():
        raise FalhaValidacao("CNES com mais de um tipo no cardapio do ciclo 3")
    m = card.drop_duplicates("co_cnes_7d").set_index("co_cnes_7d")["tipo"]
    s = cel["co_cnes_7d"].astype(str).map(m)
    cob = {int(k): float(v) for k, v in s.notna().groupby(cel["ciclo"]).mean().items()}
    return s, {"fonte": "cardapio de gestores do ciclo 3 (lido pela funcao do script 29), por CNES",
               "cobertura_por_ciclo": cob, "celulas_sem_tipo": int(s.isna().sum()),
               "motivo_ausente": "CNES fora do cardapio do ciclo 3: tipo ausente, a celula sai das linhas que usam o "
                                 "tipo (contada), nunca recebe tipo por suposicao"}


def distancia_origem(cel: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Distância (km) do município da célula à origem mais próxima entre os candidatos do mesmo curso e ciclo (G1).

    Candidatos do curso = quem pôs alguma opção naquele curso no ciclo (tabela de escolhas do 12); origem = município
    principal de vínculo médico na competência de referência do G1 (regra principal g1_cpf_nome). Só agregado em
    memória: nenhum identificador vai para a saída.
    """
    g1 = pd.read_parquet(G1_ORIGEM, columns=["regra_ligacao", "ciclo", "id_candidato", "co_ibge_origem",
                                             "natureza_dos_dados"])
    if set(g1["natureza_dos_dados"].astype(str)) != {NATUREZA}:
        raise FalhaValidacao("G1 com natureza diferente de EMPIRICO")
    g1 = g1[(g1["regra_ligacao"] == "g1_cpf_nome") & g1["co_ibge_origem"].notna()]
    esc = pd.read_parquet(ESCOLHAS, columns=["ciclo", "id_candidato", "cod_curso"]).drop_duplicates()
    o = esc.merge(g1[["ciclo", "id_candidato", "co_ibge_origem"]], on=["ciclo", "id_candidato"], how="inner")
    o["co_ibge_origem"] = _normal_ibge(o["co_ibge_origem"])
    coord, diag = X1.ler_coordenadas()
    if diag.get("status") != "OBTIDO":
        raise FalhaValidacao("centroides do IBGE indisponiveis")
    xy = coord.set_index("co_ibge")
    origens = {k: sorted(set(g["co_ibge_origem"]) & set(xy.index))
               for k, g in o.groupby(["ciclo", "cod_curso"])}
    dist = np.full(len(cel), np.nan)
    sem_origem = 0
    for i, (k, c, m) in enumerate(zip(cel["ciclo"].astype(int), cel["cod_curso"].astype(int), cel["co_ibge"])):
        orig = origens.get((k, c), [])
        if not orig or m not in xy.index:
            sem_origem += 1
            continue
        d = X1.haversine_km(xy.loc[orig, "lon"].to_numpy(), xy.loc[orig, "lat"].to_numpy(), xy.at[m, "lon"],
                            xy.at[m, "lat"])
        dist[i] = float(np.min(d))
    info = {"regra_ligacao": "g1_cpf_nome (principal do G1)",
            "candidatos_com_origem_por_ciclo": {int(k): int(v) for k, v in
                                                o.drop_duplicates(["ciclo", "id_candidato"]).groupby("ciclo").size().items()},
            "celulas_sem_distancia": sem_origem,
            "definicao": "minimo, entre os candidatos com alguma opcao no curso e ciclo da celula, da distancia de "
                         "circulo maximo entre o centroide do municipio da celula e o do municipio de origem principal",
            "ressalva": "o conjunto de candidatos se forma depois do anuncio da faixa: a medida e de vizinhanca de "
                        "medicos interessados, nao estritamente pre-determinada"}
    return pd.Series(dist, index=cel.index), info


def vinculos_regiao(cel: pd.DataFrame, cir: pd.DataFrame) -> tuple[pd.Series, pd.Series, dict]:
    """Vínculos CNES pré (202406–202506) das CBO do curso na região de saúde por 10 mil hab. (lógica do P5, script 29).

    Região: soma dos vínculos e da população entre os municípios da CIR presentes no painel do a09; uma ausência num
    município da região deixa a região ausente (nunca soma parcial). Devolve também, por município, o mesmo para o
    conjunto alvo (todas as CBO dos cursos do PMM-E).
    """
    ponte = T29.ler_ponte()
    cbos = sorted({c for v in ponte.values() for c in v})
    cnes, info_cnes = T29.ler_cnes_pre(cbos)
    pop = T29.ler_populacao()
    vc = pd.DataFrame({k: cnes[[f"cbo_{c}" for c in cb]].sum(axis=1, min_count=len(cb))
                       for k, cb in sorted(ponte.items())})
    c = cir[["co_ibge", "co_cir"]].copy()
    c["pop22"] = c["co_ibge"].map(pop)
    reg = c[c["co_ibge"].isin(cnes.index) & c["pop22"].notna()].copy()
    soma_pop = reg.groupby("co_cir")["pop22"].sum()
    vr = vc.reindex(reg["co_ibge"]).set_index(reg.index)
    rc = pd.DataFrame({k: vr[k].groupby(reg["co_cir"]).sum(min_count=1) for k in vc.columns})
    rc = rc.where(~vr.isna().groupby(reg["co_cir"]).any()).div(soma_pop, axis=0) * POR_HAB
    va = reg["co_ibge"].map(cnes["alvo_pmme"])
    alvo = (va.groupby(reg["co_cir"]).sum(min_count=1).where(~va.isna().groupby(reg["co_cir"]).any())
            / soma_pop * POR_HAB)
    cir_cel = cel["co_ibge"].map(cir.set_index("co_ibge")["co_cir"])
    v = [rc.at[r, int(k)] if (isinstance(r, str) and r in rc.index and int(k) in rc.columns) else np.nan
         for r, k in zip(cir_cel, cel["cod_curso"])]
    info = {"cnes": info_cnes, "cursos_fora_da_ponte": sorted(int(k) for k in set(cel["cod_curso"]) - set(ponte)),
            "celulas_sem_medida": int(pd.isna(pd.Series(v)).sum()),
            "medida": "soma das CBO do curso (ponte curso-CBO do a09), media mensal de n_vinculos 202406-202506, na "
                      "regiao de saude (CIR do TabNet), por 10 mil hab. do Censo 2022"}
    mun_alvo = cir.set_index("co_ibge")["co_cir"].map(alvo)
    return pd.Series(v, index=cel.index, dtype=float), mun_alvo, info


def motivos_nao_alocacao(cel: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Motivo, por célula com candidato de 1ª opção e sem preenchimento, onde a base distingue.

    Ordem: sem vaga imediata (célula só de CR) > alocação desconsiderada pela gestão (só ciclo 1) > algum candidato de
    1ª opção alocado em outra célula > todos os candidatos de 1ª opção inelegíveis (sem pontuação ou sem pré-requisito;
    só o ciclo 1 os lista) > outro (a base não distingue).
    """
    esc = pd.read_parquet(ESCOLHAS, columns=["ciclo", "id_candidato", "opcao_rank", "co_cnes_7d", "cod_curso",
                                             "alocado", "situacao_publicada", "pontuacao", "sem_pre_requisito"])
    esc["co_cnes_7d"] = esc["co_cnes_7d"].astype(str)
    esc["desc"] = esc["situacao_publicada"].astype(str).str.contains("DESCONSIDERADO", na=False)
    aloc_cand = esc.groupby(["ciclo", "id_candidato"])["alocado"].transform("max")
    esc["alocado_outra"] = (aloc_cand == 1) & (esc["alocado"] != 1)
    esc["inelegivel"] = esc["pontuacao"].isna() | (esc["sem_pre_requisito"] == 1)
    p1 = esc[esc["opcao_rank"] == 1]
    g = p1.groupby(["ciclo", "co_cnes_7d", "cod_curso"]).agg(n=("id_candidato", "size"), desc=("desc", "any"),
                                                              outra=("alocado_outra", "any"),
                                                              ineleg=("inelegivel", "all"))
    chave = list(zip(cel["ciclo"].astype(int), cel["co_cnes_7d"].astype(str), cel["cod_curso"].astype(int)))
    gi = g.reindex(chave)
    n_esc = gi["n"].fillna(0).to_numpy()
    difere = int((n_esc != cel["n_cand_1a_opcao"].fillna(-1).to_numpy()).sum())
    mot = np.full(len(cel), "", dtype=object)
    alvo = (cel["tem_cand1"] == 1).to_numpy() & (cel["preenchida"] == 0).to_numpy()
    so_cr = (cel["tipo_vaga_imediata"] == 0).to_numpy()
    c1 = (cel["ciclo"] == 1).to_numpy()
    desc = gi["desc"].fillna(False).to_numpy(dtype=bool)
    outra = gi["outra"].fillna(False).to_numpy(dtype=bool)
    ineleg = gi["ineleg"].fillna(False).to_numpy(dtype=bool)
    for i in np.flatnonzero(alvo):
        if so_cr[i]:
            mot[i] = "sem_vaga_imediata"
        elif c1[i] and desc[i]:
            mot[i] = "desconsiderada_pela_gestao"
        elif outra[i]:
            mot[i] = "candidato_alocado_em_outra_celula"
        elif c1[i] and ineleg[i]:
            mot[i] = "candidatos_inelegiveis"
        else:
            mot[i] = "outro_nao_distinguido"
    info = {"celulas_em_que_a_contagem_de_1a_opcao_das_escolhas_difere_do_quadro": difere,
            "ordem": ["sem_vaga_imediata", "desconsiderada_pela_gestao (so ciclo 1)",
                      "candidato_alocado_em_outra_celula", "candidatos_inelegiveis (so ciclo 1)",
                      "outro_nao_distinguido"],
            "o_que_a_base_nao_distingue": {
                "nota_insuficiente_contra_a_2a_opcao": "nao distinguivel: a base nao registra o motivo da rejeicao "
                    "por celula; no mecanismo reconstruido pelo G2 quem pos a celula em 1a opcao tem prioridade sobre "
                    "quem a pos em 2a, entao esse motivo nao e esperado numa celula com vaga imediata",
                "desclassificacao_ciclos_2_e_3": "nao distinguivel: as listas de escolhas dos ciclos 2 e 3 trazem so os "
                    "classificados; a aba 'Desclassificados' do resultado do ciclo 2 tem so curso, CPF mascarado e "
                    "nome, sem as opcoes de celula (cabecalho conferido)",
                "desistencia_ou_nao_homologacao": "nao distinguivel na 1a chamada dos ciclos 2 e 3"}}
    return pd.Series(mot, index=cel.index), info


def carregar() -> dict:
    """Bases do ND (municípios) e do adendo §7 (células), mais os atributos de cada explicação."""
    global FAIXA_BOLSA_MIL
    dados = T24.carregar_tudo()
    a08 = pd.read_csv(T23.A08, dtype={"co_ibge": str}, usecols=["co_ibge", "nome_municipio_uf"])
    a08["co_ibge"] = a08["co_ibge"].str.zfill(6)
    V = ND.preparar(dados["V"], a08.set_index("co_ibge")["nome_municipio_uf"])
    cel_raw = pd.read_parquet(T23.ARQ_VC, columns=["ciclo", "co_ibge", "vagas_imediatas", "vagas_cr",
                                                   "n_alocados_ch1"])
    agg, _ = ND.agregar_celulas(cel_raw)
    V = ND.preparar_adendo2(V, agg)
    CK = {k: d.copy() for k, d in dados["CK"].items()}
    cel = pd.concat(CK.values(), ignore_index=True)
    info: dict = {}
    # Concorrência (D-d): células com IVS e CIR, exposição do protocolo 58 (script 32), mercado CIR e UF.
    d32 = T32.carregar()
    FAIXA_BOLSA_MIL = dict(d32["mapa"])
    univ = d32["univ"]
    ex = {}
    for mercado in ("cir", "uf"):
        e = T32.exposicoes(univ, mercado, "mesmo_curso")
        n = e["n_conc"].to_numpy(dtype=float)
        ge = np.where(n > 0, n * (e["frac_maior"].fillna(0) + 1.0 - e["frac_bolsa_diferente"].fillna(0)), 0.0)
        ex[mercado] = pd.DataFrame({"ciclo": univ["ciclo"].astype(int), "co_cnes_7d": univ["co_cnes_7d"].astype(str),
                                    "cod_curso": univ["cod_curso"].astype(int), f"n_conc_{mercado}": n,
                                    f"n_ge_{mercado}": ge,
                                    f"bolsa_media_{mercado}": e["bolsa_media_conc"].to_numpy(dtype=float)})
    conc = ex["cir"].merge(ex["uf"], on=["ciclo", "co_cnes_7d", "cod_curso"], validate="one_to_one")
    info["concorrencia"] = {"fonte": "script 32 (protocolo 58): exposicoes(mercado, 'mesmo_curso')",
                            "exclusoes_do_universo_32": d32["exclusoes"],
                            "n_ge": "n de concorrentes com bolsa igual ou maior = n_conc x (fracao maior + fracao "
                                    "igual); zero concorrentes e contagem zero verdadeira"}
    cir, info_cir = T29.ler_cir()
    gest, info["gestao"] = gestao_por_celula(cel)
    tipo, info["tipo_estabelecimento"] = tipo_por_celula(cel)
    dist, info["distancia_origem"] = distancia_origem(cel)
    vreg, mun_alvo_reg, info["vinculos_regiao"] = vinculos_regiao(cel, cir)
    regic, info_regic = T29.ler_regic()
    cel["so_cr"] = 1.0 - cel["tipo_vaga_imediata"].astype(float)
    cel["gestao"], cel["tipo_estab"], cel["dist_origem_km"] = gest.to_numpy(), tipo.to_numpy(), dist.to_numpy()
    cel["vinc_curso_regiao_10k"] = vreg.to_numpy()
    cel["regic_nivel"] = cel["co_ibge"].map(regic).str[0].astype(float)
    cel["gestao_estadual"] = np.where(cel["gestao"].isna(), np.nan, (cel["gestao"] == "ESTADUAL").astype(float))
    cel["hospital_geral"] = np.where(cel["tipo_estab"].isna(), np.nan,
                                     (cel["tipo_estab"] == "05 HOSPITAL GERAL").astype(float))
    cel["co_cnes_7d"] = cel["co_cnes_7d"].astype(str)
    cel["cod_curso"] = cel["cod_curso"].astype(int)
    cel = cel.merge(conc, on=["ciclo", "co_cnes_7d", "cod_curso"], how="left", validate="one_to_one")
    mot, info["motivos"] = motivos_nao_alocacao(cel)
    cel["motivo"] = mot.to_numpy()
    # Índices de composição: preenchimento médio da categoria fora das janelas dos dois cortes (|IVS - corte| >= h).
    fora = np.all([np.abs(cel["s_mil"].to_numpy() - c) >= H for c in CORTES], axis=0)
    info["indices_composicao"] = {"regra": "para cada categoria (curso x ciclo; tipo do estabelecimento x ciclo; "
                                           "gestao x ciclo), a fracao de celulas preenchidas entre as celulas com "
                                           "|IVS - corte| >= 0,050 nos dois cortes (fora de qualquer janela); "
                                           "categoria sem celula fora das janelas fica ausente",
                                  "celulas_fora_das_janelas": int(fora.sum())}
    for nome, cat in (("idx_curso", "fe_curso_ciclo"), ("idx_tipo", "tipo_estab"), ("idx_gestao", "gestao")):
        chave = cel["ciclo"].astype(str) + "|" + cel[cat].astype(str)
        m = cel.loc[fora & cel[cat].notna().to_numpy()].groupby(chave[fora & cel[cat].notna().to_numpy()])[
            "preenchida"].mean()
        cel[nome] = np.where(cel[cat].notna(), chave.map(m), np.nan)
    cel["vic"] = cel["vic"].astype(float)
    CK = {k: g.reset_index(drop=True) for k, g in cel.groupby("ciclo")}
    # Agregados municipais (por ciclo × município) a partir das células com IVS.
    chaves = ["ciclo", "co_ibge"]
    cel["vic_cand1"] = cel["vic"] * cel["tem_cand1"]
    base = cel.groupby(chaves).agg(n_cel=("so_cr", "size"), n_cel_so_cr=("so_cr", "sum"),
                                   n_cel_cand1=("tem_cand1", "sum"), vic_cel=("vic", "sum"),
                                   vic_cand1=("vic_cand1", "sum"))
    for col in ("idx_curso", "idx_tipo", "idx_gestao", "n_conc_cir", "n_conc_uf", "n_ge_cir", "n_ge_uf",
                "dist_origem_km", "vinc_curso_regiao_10k"):
        base[f"m_{col}"] = _media_ponderada(cel, col, "vic", chaves)
    base = base.reset_index()
    p22 = T29.ler_populacao()
    sus, info["cnes_sus"] = ler_cnes_sus_pre(sorted(dados["base"]["co_ibge"]))
    bmap = dados["base"].set_index("co_ibge")
    for k in CICLOS:
        d = V[k]
        b = base[base["ciclo"] == k].drop(columns="ciclo")
        d = d.merge(b, on="co_ibge", how="left", validate="one_to_one")
        if (d["vic_cel"] != d["vagas_imediatas_mais_cr"]).any():
            raise FalhaValidacao(f"V{k}: soma das celulas difere das vagas oferecidas do municipio")
        d["frac_cel_so_cr"] = d["n_cel_so_cr"] / d["n_cel"]
        d["vi_por_cel"] = d["vagas_imediatas"].astype(float) / d["n_celulas"].astype(float)
        d["frac_vic_cand1"] = d["vic_cand1"] / d["vagas_imediatas_mais_cr"]
        # D-b (iii): sem as células só de CR, em todos os ciclos.
        d["vic_sem_cr"] = d["vagas_imediatas_mais_cr"] - d["vagas_cr_so_cr"]
        d["n1_sem_cr"] = d["n_alocados_ch1"] - d["n_alocados_ch1_so_cr"]
        d["taxa_sem_cr"] = np.where(d["vic_sem_cr"] > 0, d["n1_sem_cr"] / d["vic_sem_cr"].where(d["vic_sem_cr"] > 0),
                                    np.nan)
        # D-f: sem as células só de CR só no ciclo 2.
        if k == 2:
            if (d["n_alocados_ch1_so_cr"] != 0).any():
                raise FalhaValidacao("ciclo 2 com alocado em celula so de CR: a regra do D-f nao vale")
            d["vic_f"], d["n1_f"] = d["vic_sem_cr"], d["n_alocados_ch1"].astype(float)
        else:
            d["vic_f"], d["n1_f"] = d["vagas_imediatas_mais_cr"].astype(float), d["n_alocados_ch1"].astype(float)
        d["taxa_f"] = np.where(d["vic_f"] > 0, d["n1_f"] / d["vic_f"].where(d["vic_f"] > 0), np.nan)
        d["regic_nivel"] = d["co_ibge"].map(regic).str[0].astype(float)
        for nv in (1, 2, 3, 4):
            d[f"regic_{nv}"] = np.where(d["regic_nivel"].isna(), np.nan, (d["regic_nivel"] == nv).astype(float))
        d["vinc_alvo_regiao_10k"] = d["co_ibge"].map(mun_alvo_reg).astype(float)
        d["gen_pre_10k"] = d["co_ibge"].map(bmap["estoque_gen_pre_10k"]).astype(float)
        d["sus_pre_10k"] = d["co_ibge"].map(sus).astype(float) / d["co_ibge"].map(p22).astype(float) * POR_HAB
        V[k] = d
    U = dados["base"][["co_ibge", "s_mil", "pop", "estoque_gen_pre_10k"]].copy()
    U["gen_pre_10k"] = U["estoque_gen_pre_10k"]
    U["sus_pre_10k"] = U["co_ibge"].map(sus).astype(float) / U["pop"] * POR_HAB
    U["regic_nivel"] = U["co_ibge"].map(regic).str[0].astype(float)
    info.update({"cir": info_cir, "regic": info_regic,
                 "celulas_por_ciclo": {int(k): int(len(g)) for k, g in CK.items()},
                 "municipios_por_ciclo": {int(k): int(len(d)) for k, d in V.items()}})
    return {"V": V, "CK": CK, "U": U, "dados": dados, "info": info}


# ---------------------------------------------------------------------------
# Amostras e estimadores (todos da rdd_lib, pelas funções do ND, do 23 e do 24)
# ---------------------------------------------------------------------------

def am_mun(V: dict, c: int, filtro=None, ks=CICLOS):
    partes = []
    for k in ks:
        d = V[k] if filtro is None else V[k][filtro(V[k])]
        partes.append((d, c, f"c{k}"))
    return T23.montar_amostra(partes, empilhada=True) if len(ks) > 1 else \
        T23.montar_amostra([(partes[0][0], c, str(c))], empilhada=False)


def am_cel(CK: dict, c: int, filtro=None, ks=CICLOS):
    return T23.montar_amostra([(CK[k] if filtro is None else CK[k][filtro(CK[k])], c, f"c{k}") for k in ks],
                              empilhada=True)


def fit_q1(a, extra=(), ctrl="vagas_imediatas_mais_cr", y="n_alocados_ch1") -> dict:
    covs = (("vagas_oferecidas", a.col(ctrl)),) + tuple((n, a.col(c)) for n, c in extra)
    return ND.ajustar(a, a.col(y), H, covs)


def fit_q2(a, extra=(), taxa="taxa_vic", peso="vagas_imediatas_mais_cr") -> dict:
    y = a.col(taxa)
    pw = np.where(np.isfinite(y), a.col(peso), np.nan)
    return ND.ajustar(a, y, H, tuple((n, a.col(c)) for n, c in extra), peso=pw)


def fit_cel(a, y, *, fe=True, tipo=True, z=(), cats=()) -> dict:
    """Q3 e variantes: rd_empilhado na célula, cluster por município (como `ajustar_celula` do 24)."""
    Zs, nomes = [], []
    if tipo:
        Zs.append(a.col("tipo_vaga_imediata"))
        nomes.append("tipo_vaga_imediata")
    for nome, col in z:
        Zs.append(a.col(col))
        nomes.append(nome)
    for col in cats:
        vals = a.d[col]
        for nv in sorted(vals.dropna().unique().tolist())[1:]:
            Zs.append(np.where(vals.isna(), np.nan, (vals == nv).astype(float)))
            nomes.append(f"{col}[{nv}]")
    Z = np.column_stack(Zs) if Zs else None
    return L.rd_empilhado(a.s, y, a.c, grupo=a.g, h_mil=H, cluster=a.cl, ids_unidade=a.cl,
                          efeitos_fixos=a.d["fe_curso_ciclo"].to_numpy() if fe else None, Z=Z,
                          nomes_z=nomes or None, detalhes=True)


def fit_q(q: str, V: dict, CK: dict, c: int, **kw) -> dict:
    if q == "Q1":
        return fit_q1(am_mun(V, c), **kw)
    if q == "Q2":
        return fit_q2(am_mun(V, c), **kw)
    a = am_cel(CK, c)
    return fit_cel(a, a.col("preenchida"), **kw)


def medias_lados(r: dict, y: np.ndarray, peso=None) -> tuple[float, float]:
    return ND.medias_lados(r, y, peso)


def limites(r: dict) -> tuple[float, float]:
    """Limite do lado de baixo (média dos interceptos por grupo com os pesos omega) e de cima (+ salto)."""
    const, om = T24.interceptos_lib(r, True)
    lo = T24.media_lado_baixo({"const": const}, om)
    return lo, lo + float(r["tau"])


# ---------------------------------------------------------------------------
# 1. Reprodução de Q1–Q3
# ---------------------------------------------------------------------------

def reproduzir(V: dict, CK: dict) -> tuple[list[dict], dict]:
    n = pd.read_csv(N_EST, dtype={"corte": str})
    na = pd.read_csv(NA_EST, dtype={"corte": str})
    nd = pd.read_csv(ND_EST, dtype={"corte": str})
    linhas, refs, difs = [], {}, []
    for c in CORTES:
        rc = RC[c]
        alvo = {
            "Q1": [n[(n.outcome_id == "N1") & (n.populacao == "V1+V2+V3") & (n.corte == rc)
                     & (n.especificacao == "S-a") & (n.variante == "principal")],
                   nd[(nd.diagnostico == "D4") & (nd.amostra == "POR_CORTE") & (nd.corte == rc)
                      & (nd.outcome == "N1") & (nd.especificacao == "controle_protocolo_48")
                      & (nd.variante == "principal") & (nd.tipo_linha == "estimativa")]],
            "Q2": [n[(n.outcome_id == "N1") & (n.populacao == "V1+V2+V3") & (n.corte == rc)
                     & (n.especificacao == "S-e") & (n.variante == "fracao_ponderada_pelo_controle")],
                   nd[(nd.diagnostico == "D1") & (nd.amostra == "POR_CORTE") & (nd.corte == rc)
                      & (nd.outcome == "TAXA_VIC") & (nd.especificacao == "taxa_ponderada")
                      & (nd.variante == "principal") & (nd.tipo_linha == "estimativa")]],
            "Q3": [na[(na.outcome_id == "A3_PREENCHIDA") & (na.populacao == "V1+V2+V3 (celulas)")
                      & (na.corte == rc) & (na.especificacao == "A3") & (na.variante == "principal")]],
        }
        a_c = am_cel(CK, c)
        r_lib24 = T24.ajustar_celula(a_c, a_c.col("preenchida"), H, fe=True, tipo=True)
        for q in Q:
            r = fit_q(q, V, CK, c)
            if q == "Q3" and abs(r["tau"] - r_lib24["tau"]) > 1e-12:
                raise FalhaValidacao("fit_cel difere de ajustar_celula do script 24")
            fontes = []
            for df in alvo[q]:
                if len(df) != 1:
                    raise FalhaValidacao(f"reproducao {q} {rc}: {len(df)} linhas-alvo")
                d = max(abs(float(df["tau"].iloc[0]) - r["tau"]), abs(float(df["ep"].iloc[0]) - r["ep"]))
                difs.append(d)
                fontes.append(d)
                if not d <= 1e-9:
                    raise FalhaValidacao(f"{q} em {rc} nao reproduz o alvo: dif {d}")
            y = (am_mun(V, c).col("n_alocados_ch1") if q == "Q1" else am_mun(V, c).col("taxa_vic") if q == "Q2"
                 else a_c.col("preenchida"))
            pw = am_mun(V, c).col("vagas_imediatas_mais_cr") if q == "Q2" else None
            ma, mc = medias_lados(r, y, pw)
            ln = nova("Q", "reproducao", "reproducao", q, rc, pop="V1+V2+V3", esp="principal", var="principal",
                      unidade_analise="celula" if q == "Q3" else "municipio x ciclo", descricao=DESC_Q[q],
                      unidade=UN_Q[q], h=H / 1000.0, media_abaixo=ma, media_acima=mc,
                      alvo_tau=float(alvo[q][0]["tau"].iloc[0]), alvo_ep=float(alvo[q][0]["ep"].iloc[0]),
                      dif_max=max(fontes),
                      nota=("alvo: N_estimativas (S-a principal) e ND_estimativas (D4)" if q == "Q1" else
                            "alvo: N_estimativas (S-e) e ND_estimativas (D1 TAXA_VIC)" if q == "Q2" else
                            "alvo: NA_estimativas (A3_PREENCHIDA principal)"))
            linhas.append(preencher(ln, r))
            refs[(q, c)] = r
    return linhas, {"max_abs_dif": max(difs), "linhas_alvo": len(difs), "tolerancia": 1e-9}


# ---------------------------------------------------------------------------
# D-a: placebos e randomização local
# ---------------------------------------------------------------------------

def _segmento(s_mil: np.ndarray, c: int) -> np.ndarray:
    if c <= 300:
        return s_mil <= 300
    if c <= 400:
        return (s_mil > 300) & (s_mil <= 400)
    return s_mil > 400


def placebo_q(q: str, V: dict, CK: dict, c: int, *, segmento: bool) -> dict:
    filtro = (lambda d: _segmento(d["s_mil"].to_numpy(dtype=float), c)) if segmento else None
    if q == "Q3":
        a = am_cel(CK, c, filtro)
        return fit_cel(a, a.col("preenchida"))
    a = am_mun(V, c, filtro)
    return fit_q1(a) if q == "Q1" else fit_q2(a)


def p_posto(t_real: float, ts: np.ndarray) -> float:
    ts = ts[np.isfinite(ts)]
    return float((1 + np.sum(np.abs(ts) >= abs(t_real))) / (1 + ts.size))


def fisher_fwl(y, w, X0, mun, t_row, n_perm=N_PERM, semente=(SEMENTE,)) -> dict:
    """Randomização local no nível do município: estatística = coeficiente de T na MQP de y em [X0, T] (peso w).

    Sob o nulo exato (efeito zero em toda unidade da janela), y fica fixo e T é permutado entre os municípios (n1
    fixo; matriz da rdd_lib). Frisch–Waugh–Lovell: o coeficiente é (T~' y~) / (T~' T~), com ~ = resíduo da projeção
    ponderada em X0. p bicaudal = (1 + #{|T_perm| >= |T_obs|}) / (R + 1).
    """
    y, w = np.asarray(y, float), np.asarray(w, float)
    ok = np.isfinite(y) & np.isfinite(w) & (w > 0) & np.isfinite(X0).all(axis=1)
    y, w, X0, mun, t_row = y[ok], w[ok], X0[ok], np.asarray(mun)[ok], np.asarray(t_row, float)[ok]
    codigos, inv = np.unique(mun, return_inverse=True)
    t_mun = np.zeros(codigos.size)
    t_mun[inv] = t_row
    if np.any(np.abs(t_mun[inv] - t_row) > 0):
        raise FalhaValidacao("tratamento varia dentro do municipio na janela")
    n_mun, n1 = codigos.size, int(t_mun.sum())
    res = {"tau": float("nan"), "p_valor": float("nan"), "n_abaixo": n_mun - n1, "n_acima": n1, "n_obs": int(ok.sum()),
           "n_perm": n_perm, "nota": ""}
    if n1 < 1 or n_mun - n1 < 1:
        res["nota"] = "lado vazio na janela"
        return res
    sw = np.sqrt(w)
    Xw = X0 * sw[:, None]
    B = np.linalg.pinv(Xw)
    yt = y * sw - Xw @ (B @ (y * sw))

    def estat(Tm: np.ndarray) -> np.ndarray:
        Tr = Tm[:, inv] * sw[None, :]
        Tt = Tr - (Tr @ B.T) @ Xw.T
        den = np.einsum("ij,ij->i", Tt, Tt)
        return np.where(den > 1e-12, (Tt @ yt) / np.where(den > 1e-12, den, 1.0), np.nan)

    obs = float(estat(t_mun[None, :])[0])
    if not np.isfinite(obs):
        res["nota"] = "T colinear com os controles na janela"
        return res
    P = L.matriz_permutacao(n_mun, n1, n_perm, semente)
    perm = estat(P)
    perm = perm[np.isfinite(perm)]
    res.update({"tau": obs, "p_valor": float((1 + np.sum(np.abs(perm) >= abs(obs) - 1e-10)) / (perm.size + 1)),
                "n_perm_validas": int(perm.size)})
    return res


def _dummies(rotulos: np.ndarray) -> np.ndarray:
    niveis = sorted(np.unique(rotulos).tolist())
    return np.column_stack([(rotulos == nv).astype(float) for nv in niveis])


def fisher_q(q: str, V: dict, CK: dict, c: int, w_mil: int) -> dict:
    a = am_cel(CK, c) if q == "Q3" else am_mun(V, c)
    x = L.normalizar_s_mil(a.s) - a.c
    jan = (x > -w_mil) & (x <= w_mil)
    s = a.subconjunto(jan)
    t = s.t
    g = _dummies(s.g)
    if q == "Q1":
        v = s.col("vagas_imediatas_mais_cr")
        X0 = np.column_stack([g, g * v[:, None]])
        return fisher_fwl(s.col("n_alocados_ch1"), np.ones(len(t)), X0, s.cl, t)
    if q == "Q2":
        y = s.col("taxa_vic")
        return fisher_fwl(y, s.col("vagas_imediatas_mais_cr"), g, s.cl, t)
    X0 = np.column_stack([_dummies(s.d["fe_curso_ciclo"].to_numpy()), s.col("tipo_vaga_imediata")])
    return fisher_fwl(s.col("preenchida"), np.ones(len(t)), X0, s.cl, t)


def bloco_da(V, CK, refs) -> tuple[list[dict], dict]:
    linhas, resumo = [], {}
    for comp, grade, seg in ((False, PLACEBOS, False), (True, PLACEBOS_COMPLEMENTARES, True)):
        rot = ROT_COMPLEMENTAR if comp else ROT_PROTOCOLO
        for q in Q:
            ts = []
            for cp in grade:
                r = placebo_q(q, V, CK, cp, segmento=seg)
                ln = nova("D-a", "placebo_complementar" if comp else "placebo", "placebo", q, "placebo",
                          esp="mesma de Q", var="segmento_da_bolsa" if seg else "janela_inteira",
                          corte_placebo=f"{cp / 1000:.3f}", rotulo=rot, h=H / 1000.0, unidade=UN_Q[q],
                          unidade_analise="celula" if q == "Q3" else "municipio x ciclo",
                          nota=("so as observacoes do mesmo segmento de bolsa do corte placebo (a janela nunca "
                                "atravessa 0,300 nem 0,400), como o S-i do protocolo 48; fora do protocolo 61"
                                if seg else ""))
                preencher(ln, r)
                linhas.append(ln)
                ts.append(ln["t"] if ln["status"] == "EXECUTADO" else np.nan)
            ts = np.array(ts, dtype=float)
            for c in CORTES:
                rr = refs[(q, c)]
                tr = rr["tau"] / rr["ep"]
                pp = p_posto(tr, ts)
                ln = nova("D-a", "placebo_complementar" if comp else "placebo", "resumo_placebo", q, RC[c],
                          rotulo=rot, tau=rr["tau"], ep=rr["ep"], t=tr, p_posto=pp,
                          frac_t_maior_196=float(np.mean(np.abs(ts[np.isfinite(ts)]) > 1.96)) if np.isfinite(ts).any()
                          else np.nan, n_placebos=int(np.isfinite(ts).sum()), unidade=UN_Q[q],
                          valor=float(1.0 / (1 + np.isfinite(ts).sum())),
                          nota=("valor = menor p por posto possivel com esse numero de placebos; " +
                                ("apoio do D-a (p por posto > 0,10)" if pp > 0.10 else "sem apoio do D-a")))
                linhas.append(ln)
                resumo[(rot, q, c)] = {"p_posto": pp, "t_real": tr, "n_placebos": int(np.isfinite(ts).sum()),
                                       "p_minimo_possivel": float(1.0 / (1 + np.isfinite(ts).sum()))}
    for q in Q:
        for c in CORTES:
            for w in JANELAS_FISHER:
                r = fisher_q(q, V, CK, c, w)
                ln = nova("D-a", "fisher", "salto", q, RC[c], var=f"janela_{w / 1000:.3f}", janela=w / 1000.0,
                          n_perm=N_PERM, semente=str(SEMENTE), unidade=UN_Q[q],
                          unidade_analise="celula" if q == "Q3" else "municipio x ciclo",
                          estimador=("randomizacao local: coeficiente de T com intercepto por ciclo"
                                     + (" e vagas oferecidas por ciclo" if q == "Q1" else
                                        ", peso = vagas oferecidas" if q == "Q2" else
                                        ", efeitos fixos de curso x ciclo e tipo de vaga") +
                                     "; T permutado entre municipios; p de Fisher"),
                          nota="n abaixo/acima = municipios; n_obs = linhas")
                ln.update({k: r[k] for k in ("tau", "p_valor", "n_abaixo", "n_acima", "n_obs")})
                ln["nota"] = _juntar(ln["nota"], r.get("nota", ""))
                if not np.isfinite(ln["tau"]):
                    ln["status"] = "SEM_ESTIMATIVA"
                linhas.append(ln)
    return linhas, resumo


# ---------------------------------------------------------------------------
# Linhas de salto genéricas
# ---------------------------------------------------------------------------

def salto_mun(expl, bloco, V, c, outcome, *, peso=None, ks=CICLOS, filtro=None, var="principal", desc="",
              unidade="", extra=(), nota="") -> dict:
    a = am_mun(V, c, filtro, ks)
    y = a.col(outcome)
    pw = np.where(np.isfinite(y), a.col(peso), np.nan) if peso else None
    r = ND.ajustar(a, y, H, tuple((n, a.col(cc)) for n, cc in extra), peso=pw)
    ma, mc = medias_lados(r, y, pw)
    pop = "+".join(f"V{k}" for k in ks)
    ln = nova(expl, bloco, "salto", outcome, RC[c], pop=pop, ciclo="+".join(str(k) for k in ks), esp="local_linear",
              var=var, outcome=outcome, descricao=desc, unidade=unidade, unidade_analise="municipio x ciclo",
              h=H / 1000.0, media_abaixo=ma, media_acima=mc, covariaveis=";".join(cc for _, cc in extra),
              estimador=("local linear, kernel triangular, h = 0,050; " + ("intercepto e inclinacoes por ciclo, "
                         "salto comum, CR1 por municipio" if len(ks) > 1 else "EP HC1") +
                         (f"; peso = kernel x {peso}" if peso else "")),
              nota=nota)
    fora = int(((L.pesos_kernel(L.normalizar_s_mil(a.s) - a.c, H) > 0) & ~np.isfinite(y)).sum())
    if fora:
        ln["n_fora"], ln["motivo_fora"] = fora, "outcome ausente (denominador zero ou atributo ausente; nunca zero)"
    return preencher(ln, r)


def salto_cel(expl, bloco, CK, c, outcome, *, fe=False, tipo=False, ks=CICLOS, filtro=None, var="sem_efeitos_fixos",
              desc="", unidade="", z=(), cats=(), nota="", quant=None) -> tuple[dict, dict]:
    a = am_cel(CK, c, filtro, ks)
    y = a.col(outcome)
    r = fit_cel(a, y, fe=fe, tipo=tipo, z=z, cats=cats)
    ma, mc = medias_lados(r, y)
    efs = ", ".join(x for x, ok in (("curso x ciclo", fe), ("tipo de vaga", tipo)) if ok)
    ln = nova(expl, bloco, "salto", quant or outcome, RC[c], pop="+".join(f"V{k}" for k in ks) + " (celulas)",
              ciclo="+".join(str(k) for k in ks), esp="celula", var=var, outcome=outcome, descricao=desc,
              unidade=unidade, unidade_analise="celula", h=H / 1000.0, media_abaixo=ma, media_acima=mc,
              efeitos_fixos=efs, covariaveis=";".join([cc for _, cc in z] + list(cats)),
              estimador="celula do quadro; RDD no IVS do municipio; intercepto e inclinacoes por ciclo x lado, salto "
                        "comum; CR1 por municipio" + (f"; efeitos fixos: {efs}" if efs else ""),
              nota=_juntar(nota, "n abaixo/acima = municipios"))
    fora = int(((L.pesos_kernel(L.normalizar_s_mil(a.s) - a.c, H) > 0) & ~np.isfinite(y)).sum())
    if fora:
        ln["n_fora"], ln["motivo_fora"] = fora, "atributo ausente (nunca imputado)"
    return preencher(ln, r), r


# ---------------------------------------------------------------------------
# "Fixar o fator": Q1, Q2, Q3 com o fator, ao lado do original na mesma amostra
# ---------------------------------------------------------------------------

def fixar(expl: str, var: str, V: dict, CK: dict, refs: dict, *, q1=None, q2=None, q3=None) -> list[dict]:
    """Cada argumento qN é um dict com: extra (covariáveis), filtro (linhas mantidas), e opcionais ctrl/y/taxa/peso/z/cats.

    Dois modos (decisão registrada no resumo):
    - covariável (o fator entra como covariável ou efeito fixo): a razão é fixado ÷ original na mesma amostra (a
      amostra com o fator definido), para não confundir o efeito do fator com o da perda de linhas;
    - retirada (`filtro` sem covariável: o fator é retirar um conjunto de células ou de vagas): a razão é fixado ÷
      original (Q da reprodução, amostra inteira), porque retirar as linhas é o próprio fator.
    """
    linhas = []
    for q, spec in (("Q1", q1), ("Q2", q2), ("Q3", q3)):
        for c in CORTES:
            ln = nova(expl, "fixar_fator", "fixado", q, RC[c], pop="V1+V2+V3", esp="fixar_fator", var=var,
                      unidade=UN_Q[q], unidade_analise="celula" if q == "Q3" else "municipio x ciclo",
                      h=H / 1000.0, tau_original=refs[(q, c)]["tau"])
            if spec is None:
                ln["status"] = "NAO_EXECUTADO"
                ln["nota"] = "o teste do protocolo nao define como fixar este fator nesta quantidade"
                linhas.append(ln)
                continue
            filtro = spec.get("filtro")
            extra = spec.get("extra", ())
            if q == "Q3":
                a = am_cel(CK, c, filtro)
                cols = [cc for _, cc in spec.get("z", ())] + list(spec.get("cats", ()))
                ok = np.ones(len(a.s), dtype=bool)
                for cc in cols:
                    ok &= a.d[cc].notna().to_numpy()
                a = a.subconjunto(ok)
                y = a.col("preenchida")
                r0 = fit_cel(a, y)
                r = fit_cel(a, y, z=spec.get("z", ()), cats=spec.get("cats", ()))
                ln["covariaveis"] = ";".join(cols)
                ln["efeitos_fixos"] = "curso x ciclo, tipo de vaga"
            else:
                a = am_mun(V, c, filtro)
                ok = np.ones(len(a.s), dtype=bool)
                for _, cc in extra:
                    ok &= np.isfinite(a.col(cc))
                taxa = spec.get("taxa", "taxa_vic")
                peso = spec.get("peso", "vagas_imediatas_mais_cr")
                ctrl = spec.get("ctrl", "vagas_imediatas_mais_cr")
                if q == "Q2":
                    ok &= np.isfinite(a.col(taxa))
                a = a.subconjunto(ok)
                if q == "Q1":
                    r0 = fit_q1(a, ctrl=spec.get("ctrl0", "vagas_imediatas_mais_cr"))
                    r = fit_q1(a, extra, ctrl=ctrl, y=spec.get("y", "n_alocados_ch1"))
                else:
                    r0 = fit_q2(a, taxa=spec.get("taxa0", "taxa_vic"), peso=spec.get("peso0", "vagas_imediatas_mais_cr"))
                    r = fit_q2(a, extra, taxa=taxa, peso=peso)
                ln["covariaveis"] = ";".join(cc for _, cc in extra)
            preencher(ln, r)
            retirada = filtro is not None or spec.get("retirada", False)
            ln["tau_original_mesma_amostra"] = np.nan if retirada else r0["tau"]
            base = refs[(q, c)]["tau"] if retirada else r0["tau"]
            ln["n_fora"] = int((~ok).sum())
            ln["nota"] = _juntar("modo: retirada (razao contra o Q original, amostra inteira)" if retirada else
                                 "modo: covariavel (razao contra o Q original na mesma amostra)",
                                 spec.get("nota", ""), ln["nota"],
                                 f"{int((~ok).sum())} linhas sem o fator definido fora (ausente, nunca imputado)"
                                 if (~ok).any() else "")
            if np.isfinite(base) and abs(base) > 0 and np.isfinite(ln["tau"]):
                ln["razao_fixado_original"] = ln["tau"] / base
                ln["reduz_metade"] = "sim" if abs(ln["tau"]) <= LIMIAR_METADE * abs(base) else "nao"
            linhas.append(ln)
    return linhas


# ---------------------------------------------------------------------------
# D-b a D-g
# ---------------------------------------------------------------------------

COMP_CEL = [("so_cr", "celula so de cadastro reserva (sem vaga imediata)", UN_Q["Q3"]),
            ("idx_curso", "indice de curso: preenchimento medio do curso x ciclo fora das janelas", UN_Q["Q3"]),
            ("idx_tipo", "indice de tipo do estabelecimento: preenchimento medio do tipo x ciclo fora das janelas",
             UN_Q["Q3"]),
            ("idx_gestao", "indice de gestao: preenchimento medio da gestao x ciclo fora das janelas", UN_Q["Q3"]),
            ("gestao_estadual", "estabelecimento de gestao estadual", UN_Q["Q3"]),
            ("hospital_geral", "estabelecimento do tipo 05 hospital geral", UN_Q["Q3"])]
COMP_MUN = [("frac_cr", "vagas de cadastro reserva / vagas oferecidas (peso = vagas oferecidas)",
             "vagas_imediatas_mais_cr"),
            ("frac_cel_so_cr", "celulas so de CR / celulas (peso = celulas)", "n_celulas"),
            ("vi_por_cel", "vagas imediatas por celula (peso = celulas)", "n_celulas")]


def bloco_db(V, CK, refs) -> list[dict]:
    linhas = []
    for c in CORTES:
        for ks in [(1,), (2,), (3,), CICLOS]:
            for col, desc, un in COMP_CEL:
                ln, _ = salto_cel("D-b", "composicao", CK, c, col, ks=ks, desc=desc, unidade=un,
                                  var="por_ciclo" if len(ks) == 1 else "ciclos_juntos")
                linhas.append(ln)
            for col, desc, peso in COMP_MUN:
                linhas.append(salto_mun("D-b", "composicao", V, c, col, peso=peso, ks=ks, desc=desc,
                                        unidade="fracao (x100 = p.p.)" if col != "vi_por_cel" else "vagas por celula",
                                        var="por_ciclo" if len(ks) == 1 else "ciclos_juntos"))
        # (ii) Q3 com e sem a composição, na mesma amostra (células com tipo e gestão).
        filtro = lambda d: d["tipo_estab"].notna() & d["gestao"].notna()  # noqa: E731
        a = am_cel(CK, c, filtro)
        y = a.col("preenchida")
        for var, kw in (("sem_composicao", dict(fe=False, tipo=False)),
                        ("original_Q3", dict()),
                        ("com_composicao", dict(cats=("tipo_estab", "gestao")))):
            r = fit_cel(a, y, **kw)
            ln = nova("D-b", "q3_composicao", "salto", "Q3", RC[c], pop="V1+V2+V3 (celulas)", esp="celula", var=var,
                      unidade=UN_Q["Q3"], unidade_analise="celula", h=H / 1000.0, tau_original=refs[("Q3", c)]["tau"],
                      efeitos_fixos=("nenhum" if var == "sem_composicao" else "curso x ciclo, tipo de vaga (= so CR)"
                                     + (", tipo e gestao do estabelecimento" if var == "com_composicao" else "")),
                      nota="mesma amostra: celulas com tipo do estabelecimento e gestao definidos; o indicador de so "
                           "CR e o complemento do tipo de vaga, ja presente em Q3")
            linhas.append(preencher(ln, r))
        # (iii) Q2 sem as células só de CR (todos os ciclos).
        a = am_mun(V, c)
        r = fit_q2(a, taxa="taxa_sem_cr", peso="vic_sem_cr")
        ln = nova("D-b", "q2_sem_so_cr", "salto", "Q2", RC[c], pop="V1+V2+V3", esp="taxa_ponderada",
                  var="sem_celulas_so_cr", unidade=UN_Q["Q2"], unidade_analise="municipio x ciclo", h=H / 1000.0,
                  tau_original=refs[("Q2", c)]["tau"],
                  nota="N1 e vagas oferecidas sem as celulas so de CR; municipio-ciclo so com celulas so de CR fica fora "
                       "(taxa indefinida, nunca zero)")
        y = a.col("taxa_sem_cr")
        ln["n_fora"] = int(((L.pesos_kernel(L.normalizar_s_mil(a.s) - a.c, H) > 0) & ~np.isfinite(y)).sum())
        linhas.append(preencher(ln, r))
    comp_mun = (("frac_cr", "frac_cr"), ("frac_cel_so_cr", "frac_cel_so_cr"), ("vi_por_cel", "vi_por_cel"),
                ("idx_curso", "m_idx_curso"), ("idx_tipo", "m_idx_tipo"), ("idx_gestao", "m_idx_gestao"))
    linhas += fixar("D-b", "composicao", V, CK, refs,
                    q1={"extra": comp_mun}, q2={"extra": comp_mun},
                    q3={"cats": ("tipo_estab", "gestao"),
                        "nota": "Q3 ja fixa curso x ciclo e tipo de vaga; aqui se somam tipo e gestao do estabelecimento"})
    linhas += fixar("D-b", "sem_celulas_so_cr", V, CK, refs,
                    q1={"y": "n1_sem_cr", "ctrl": "vic_sem_cr", "filtro": lambda d: d["vic_sem_cr"] > 0,
                        "nota": "N1 e controle sem as celulas so de CR; municipio-ciclo so com celulas so de CR fora"},
                    q2={"taxa": "taxa_sem_cr", "peso": "vic_sem_cr", "retirada": True,
                        "nota": "(iii) Q2 sem as celulas so de CR; municipio-ciclo so com celulas so de CR fora"},
                    q3={"filtro": lambda d: d["tipo_vaga_imediata"] == 1,
                        "nota": "so as celulas com vaga imediata"})
    return linhas


def bloco_dc(V, CK, refs) -> tuple[list[dict], dict]:
    linhas, info = [], {}
    for c in CORTES:
        # Funil bruto (para a figura): frações simples nas células da janela (|x| < 0,050), por lado.
        a = am_cel(CK, c)
        x = L.normalizar_s_mil(a.s) - a.c
        jan = np.abs(x) < H
        ab, ac = jan & (x <= 0), jan & (x > 0)
        tc, pf, so = a.col("tem_cand1"), a.col("preenchida"), a.col("so_cr")
        for nome, v, m_ab, m_ac in (("celulas", np.ones(len(x)), ab, ac), ("so_cr", so, ab, ac),
                                    ("tem_cand1", tc, ab, ac), ("preenchida_dado_cand1", pf, ab & (tc == 1),
                                                                ac & (tc == 1)),
                                    ("preenchida", pf, ab, ac)):
            linhas.append(nova("D-c", "funil_bruto", "funil_bruto", nome, RC[c], pop="V1+V2+V3 (celulas)",
                               esp="media_simples_janela", var=nome, unidade_analise="celula",
                               valor_abaixo=float(v[m_ab].sum()) if nome == "celulas" else float(v[m_ab].mean()),
                               valor_acima=float(v[m_ac].sum()) if nome == "celulas" else float(v[m_ac].mean()),
                               n_abaixo=int(m_ab.sum()), n_acima=int(m_ac.sum()),
                               unidade="celulas" if nome == "celulas" else "fracao (x100 = p.p.)",
                               nota="descritivo: media simples nas celulas da janela (|IVS - corte| < 0,050), sem "
                                    "reta nem efeitos fixos; n = celulas"))
        partes = {}
        for nome, filtro, outcome, desc in (
                ("P_C", None, "tem_cand1", "celula com candidato de 1a opcao"),
                ("P_F_dado_C", lambda d: d["tem_cand1"] == 1, "preenchida", "preenchida | tem candidato de 1a opcao"),
                ("P_F_dado_semC", lambda d: d["tem_cand1"] == 0, "preenchida",
                 "preenchida | sem candidato de 1a opcao (so por 2a opcao)"),
                ("P_F", None, "preenchida", "celula preenchida (= Q3)")):
            for fe in (True, False):
                ln, r = salto_cel("D-c", "funil", CK, c, outcome, fe=fe, tipo=fe, filtro=filtro, quant=nome,
                                  var="especificacao_Q3" if fe else "sem_efeitos_fixos", desc=desc,
                                  unidade=UN_Q["Q3"],
                                  nota="subamostra condicional: descritivo" if filtro is not None else "")
                linhas.append(ln)
                if not fe:
                    partes[nome] = r
        # Decomposição aproximada nos limites (sem efeitos fixos; regressões separadas, por isso há resíduo).
        try:
            (c0, c1), (a0, a1), (b0, b1), (f0, f1) = (limites(partes[k]) for k in ("P_C", "P_F_dado_C",
                                                                                     "P_F_dado_semC", "P_F"))
            contrib = {"candidatos": (c1 - c0) * (a0 - b0), "preencher_dado_candidato": c1 * (a1 - a0),
                       "preencher_sem_candidato": (1 - c1) * (b1 - b0)}
            for nome, v in contrib.items():
                linhas.append(nova("D-c", "decomposicao", "decomposicao", nome, RC[c], pop="V1+V2+V3 (celulas)",
                                   esp="limites_sem_efeitos_fixos", var=nome, valor=v, tau=f1 - f0,
                                   valor_abaixo=c0 if nome == "candidatos" else a0 if "dado" in nome else b0,
                                   valor_acima=c1 if nome == "candidatos" else a1 if "dado" in nome else b1,
                                   unidade=UN_Q["Q3"], unidade_analise="celula",
                                   nota="valor = contribuicao para o salto de P(preenchida) sem efeitos fixos (tau): "
                                        "dC x (a- - b-), C+ x da, (1 - C+) x db; limites = interceptos ponderados "
                                        "pelos pesos omega"))
            resid = (f1 - f0) - sum(contrib.values())
            linhas.append(nova("D-c", "decomposicao", "identidade", "residuo", RC[c], pop="V1+V2+V3 (celulas)",
                               esp="limites_sem_efeitos_fixos", var="residuo", valor=resid, tau=f1 - f0,
                               unidade=UN_Q["Q3"], unidade_analise="celula",
                               nota="residuo = salto de P(preenchida) - soma das contribuicoes; vem de as quatro "
                                    "regressoes usarem amostras diferentes"))
            info[RC[c]] = {"contribuicoes": contrib, "residuo": resid, "salto_P_F_sem_ef": f1 - f0}
        except (KeyError, TypeError):
            info[RC[c]] = {"nota": "decomposicao nao calculada (alguma parte sem estimativa)"}
        # Motivos de não alocação (células com candidato de 1ª opção): saltos somam o salto de P(F | C) com o sinal
        # trocado (mesma amostra, mesmos pesos: identidade linear exata).
        filtro = lambda d: d["tem_cand1"] == 1  # noqa: E731
        soma = 0.0
        for mot in ("sem_vaga_imediata", "desconsiderada_pela_gestao", "candidato_alocado_em_outra_celula",
                    "candidatos_inelegiveis", "outro_nao_distinguido"):
            for k in CK:
                CK[k][f"mot_{mot}"] = (CK[k]["motivo"] == mot).astype(float)
            ln, r = salto_cel("D-c", "motivos", CK, c, f"mot_{mot}", fe=True, tipo=True, filtro=filtro, quant=mot,
                              var="especificacao_Q3", desc=f"nao preenchida por: {mot}", unidade=UN_Q["Q3"],
                              nota="celulas com candidato de 1a opcao; outcome = 1 se nao preenchida por este motivo")
            a = am_cel(CK, c, filtro)
            x = L.normalizar_s_mil(a.s) - a.c
            jan = L.pesos_kernel(x, H) > 0
            y = a.col(f"mot_{mot}")
            ln["valor_abaixo"], ln["valor_acima"] = float(y[jan & (x <= 0)].sum()), float(y[jan & (x > 0)].sum())
            ln["nota"] = _juntar(ln["nota"], "valor_abaixo/acima = numero de celulas com esse motivo na janela")
            soma += r["tau"]
            linhas.append(ln)
        rpf = [x for x in linhas if x["bloco"] == "funil" and x["quantidade"] == "P_F_dado_C" and x["corte"] == RC[c]
               and x["variante"] == "especificacao_Q3"][0]
        resid = rpf["tau"] + soma
        if not abs(resid) <= 1e-9:
            raise FalhaValidacao(f"identidade dos motivos nao fecha em {c}: {resid}")
        linhas.append(nova("D-c", "motivos", "identidade", "soma_motivos", RC[c], pop="V1+V2+V3 (celulas)",
                           esp="especificacao_Q3", var="identidade", tau=-soma, valor=resid, unidade=UN_Q["Q3"],
                           unidade_analise="celula",
                           nota="tau = -(soma dos saltos dos motivos) = salto de P(preenchida | candidato); valor = "
                                "residuo"))
    linhas += fixar("D-c", "funil", V, CK, refs,
                    q1={"extra": (("n_cel_cand1", "n_cel_cand1"),)}, q2={"extra": (("frac_vic_cand1", "frac_vic_cand1"),)},
                    q3={"z": (("tem_cand1", "tem_cand1"),),
                        "nota": "mediador pos-anuncio: descritivo (quanto do salto fica depois de igualar quem teve "
                                "candidato de 1a opcao)"})
    return linhas, info


def bloco_dd(V, CK, refs) -> list[dict]:
    linhas = []
    medidas = [("n_conc_cir", "celulas do mesmo curso e ciclo na regiao de saude (CIR)", "celulas"),
               ("n_conc_uf", "celulas do mesmo curso e ciclo na UF", "celulas"),
               ("n_ge_cir", "dessas, na CIR, com bolsa igual ou maior", "celulas"),
               ("n_ge_uf", "dessas, na UF, com bolsa igual ou maior", "celulas"),
               ("bolsa_media_cir", "bolsa media das concorrentes na CIR (ausente sem concorrente)", "R$ mil"),
               ("bolsa_media_uf", "bolsa media das concorrentes na UF (ausente sem concorrente)", "R$ mil")]
    for c in CORTES:
        for col, desc, un in medidas:
            ln, _ = salto_cel("D-d", "medidas", CK, c, col, desc=desc, unidade=un)
            linhas.append(ln)
    z = (("n_conc_cir", "n_conc_cir"), ("n_conc_uf", "n_conc_uf"), ("n_ge_cir", "n_ge_cir"), ("n_ge_uf", "n_ge_uf"))
    zm = tuple((n, f"m_{cc}") for n, cc in z)
    linhas += fixar("D-d", "concorrencia", V, CK, refs, q1={"extra": zm}, q2={"extra": zm}, q3={"z": z})
    return linhas


def bloco_de(V, CK, U, refs) -> list[dict]:
    linhas = []
    for c in CORTES:
        for col, desc, un in (("vinc_curso_regiao_10k", "vinculos pre das CBO do curso na CIR por 10 mil hab.",
                               "vinculos por 10 mil hab."),
                              ("dist_origem_km", "distancia a origem mais proxima entre os candidatos do curso (G1)",
                               "km"),
                              ("regic_nivel", "nivel REGIC do municipio da celula (1 metropole ... 5 centro local)",
                               "nivel")):
            ln, _ = salto_cel("D-e", "balanco", CK, c, col, desc=desc, unidade=un)
            linhas.append(ln)
        for col, desc, un in (("regic_nivel", "nivel REGIC (1 metropole ... 5 centro local)", "nivel"),
                              ("vinc_alvo_regiao_10k", "vinculos pre das CBO-alvo na CIR por 10 mil hab.",
                               "vinculos por 10 mil hab.")):
            linhas.append(salto_mun("D-e", "balanco", V, c, col, desc=desc, unidade=un))
        a = T23.montar_amostra([(U, c, str(c))], empilhada=False)
        r = ND.ajustar(a, a.col("regic_nivel"), H)
        ln = nova("D-e", "balanco", "salto", "regic_nivel", RC[c], pop="U", ciclo="-", esp="local_linear", var="U",
                  outcome="regic_nivel", descricao="nivel REGIC (1 metropole ... 5 centro local), todos os municipios",
                  unidade="nivel", unidade_analise="municipio", h=H / 1000.0,
                  estimador="local linear, kernel triangular, h = 0,050; EP HC1")
        linhas.append(preencher(ln, r))
    z = (("vinc_curso_regiao_10k", "vinc_curso_regiao_10k"), ("dist_origem_km", "dist_origem_km"))
    zm = (("vinc_curso_regiao_10k", "m_vinc_curso_regiao_10k"), ("dist_origem_km", "m_dist_origem_km"),
          ("regic_1", "regic_1"), ("regic_2", "regic_2"), ("regic_3", "regic_3"), ("regic_4", "regic_4"))
    for k in CK:
        CK[k]["regic_cat"] = CK[k]["regic_nivel"].map(lambda v: f"n{int(v)}" if np.isfinite(v) else np.nan)
    linhas += fixar("D-e", "medicos_por_perto", V, CK, refs, q1={"extra": zm}, q2={"extra": zm},
                    q3={"z": z, "cats": ("regic_cat",)})
    return linhas


def citar_regra_c2() -> dict:
    """O que o repositório arquiva do ciclo 2 sobre o cadastro reserva na 1ª chamada (só leitura de data/raw)."""
    import openpyxl
    t = EDITAL_C2_PAGINA.read_bytes().decode("utf-8", "replace")
    txt = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<script.*?</script>|<style.*?"
                                                                          r"</style>", " ", t))))
    ocorr = len(re.findall(r"(?i)cadastro\s+(?:de\s+)?reserva|remanej", txt))
    lista_anexo = "Edital nº 3/2026" in txt
    wb = openpyxl.load_workbook(QUADRO_C2_ORIGINAL, read_only=True, data_only=True)
    achado = None
    try:
        for ws in wb.worksheets:
            for i, linha in enumerate(ws.iter_rows(values_only=True), 1):
                for j, v in enumerate(linha, 1):
                    if isinstance(v, str) and "cadastro reserva corresponde" in v.lower():
                        achado = {"aba": ws.title, "linha": i, "coluna": j, "texto": " ".join(v.split())}
                        break
                if achado or i > 50:
                    break
            if achado:
                break
    finally:
        wb.close()
    wb = openpyxl.load_workbook(RESULTADO_C2, read_only=True, data_only=True)
    try:
        cab = [str(x) for x in next(wb["Desclassificados"].iter_rows(min_row=1, max_row=1, values_only=True))
               if x is not None]
    finally:
        wb.close()
    textos = sorted(p.name for p in (ROOT / "data" / "raw").rglob("*")
                    if p.is_file() and re.search(r"(?i)edital\D*0?3[_-]2026", p.name))
    return {"pagina_do_chamamento": {"arquivo": rotulo(EDITAL_C2_PAGINA), "sha256": sha256(EDITAL_C2_PAGINA),
                                     "ocorrencias_de_cadastro_reserva_ou_remanejamento": ocorr,
                                     "lista_o_edital_3_2026_como_anexo": lista_anexo},
            "texto_do_edital_3_2026_arquivado": textos,
            "nota_do_quadro_original": ({**achado, "arquivo": rotulo(QUADRO_C2_ORIGINAL),
                                         "sha256": sha256(QUADRO_C2_ORIGINAL)} if achado else None),
            "cabecalho_desclassificados_c2": cab,
            "conclusao": ("o texto do Edital no 3/2026 (ciclo 2) nao esta arquivado em data/raw: a copia e so a pagina "
                          "do Chamamento SGTES/MS no 1/2026, que lista o edital como anexo e nao menciona cadastro "
                          "reserva; nao ha item do edital a citar. A regra arquivada mais proxima e a observacao do "
                          "quadro de vagas original do ciclo 2, citada aqui")}


def bloco_df(V, CK, refs) -> tuple[list[dict], dict]:
    linhas = []
    for c in CORTES:
        for var, taxa, peso, nota in (("todas_as_celulas", "taxa_vic", "vagas_imediatas_mais_cr", ""),
                                      ("sem_celulas_so_cr", "taxa_f", "vic_f",
                                       "N1 / vagas oferecidas sem as celulas so de CR (no ciclo 2 nenhuma foi "
                                       "preenchida na 1a chamada)"),
                                      ("so_vagas_imediatas", "taxa_vi", "vagas_imediatas", "N1 / vagas imediatas")):
            ln = salto_mun("D-f", "ciclo2", V, c, taxa, peso=peso, ks=(2,), var=var, desc=f"Q2 do ciclo 2: {var}",
                           unidade=UN_Q["Q2"], nota=nota)
            ln["quantidade"] = "Q2_ciclo2"
            ln["id_linha"] = ln["id_linha"].replace(f"|{taxa}|", "|Q2_ciclo2|")
            linhas.append(ln)
        ln = salto_mun("D-f", "ciclo2", V, c, "n_cel_so_cr", ks=(2,), var="contagem", desc="celulas so de CR por "
                       "municipio, ciclo 2", unidade="celulas por municipio")
        a = am_mun(V, c, ks=(2,))
        x = L.normalizar_s_mil(a.s) - a.c
        jan = np.abs(x) < H
        y = a.col("n_cel_so_cr")
        ln["valor_abaixo"], ln["valor_acima"] = float(y[jan & (x <= 0)].sum()), float(y[jan & (x > 0)].sum())
        ln["nota"] = _juntar(ln["nota"], "valor_abaixo/acima = total de celulas so de CR na janela (|x| < 0,050)")
        linhas.append(ln)
        vt = a.col("n_celulas")
        linhas.append(nova("D-f", "ciclo2", "contagem", "n_celulas", RC[c], pop="V2", ciclo="2", var="contagem",
                           valor_abaixo=float(vt[jan & (x <= 0)].sum()), valor_acima=float(vt[jan & (x > 0)].sum()),
                           unidade="celulas", unidade_analise="municipio",
                           nota="total de celulas do ciclo 2 na janela, por lado"))
    linhas += fixar("D-f", "sem_so_cr_ciclo2", V, CK, refs,
                    q1={"ctrl": "vic_f", "filtro": lambda d: d["vic_f"] > 0,
                        "nota": "controle = vagas oferecidas sem as celulas so de CR do ciclo 2; municipio-ciclo sem "
                                "celula restante fora"},
                    q2={"taxa": "taxa_f", "peso": "vic_f", "filtro": lambda d: d["vic_f"] > 0},
                    q3={"filtro": lambda d: ~((d["ciclo"] == 2) & (d["tipo_vaga_imediata"] == 0))})
    return linhas, citar_regra_c2()


def bloco_dg(V, U) -> list[dict]:
    linhas = []
    for c in CORTES:
        for col, desc in (("gen_pre_10k", "generalistas pre (profissionais distintos, media 202406-202506) por 10 "
                                          "mil hab."),
                          ("sus_pre_10k", "vinculos SUS de todos os medicos pre (media 202406-202506) por 10 mil hab.")):
            linhas.append(salto_mun("D-g", "balanco", V, c, col, desc=desc, unidade="por 10 mil hab."))
            a = T23.montar_amostra([(U, c, str(c))], empilhada=False)
            r = ND.ajustar(a, a.col(col), H)
            ln = nova("D-g", "balanco", "salto", col, RC[c], pop="U", ciclo="-", esp="local_linear", var="U",
                      outcome=col, descricao=desc, unidade="por 10 mil hab.", unidade_analise="municipio",
                      h=H / 1000.0, estimador="local linear, kernel triangular, h = 0,050; EP HC1")
            linhas.append(preencher(ln, r))
    for i, rg in enumerate(REGRAS_AUDITORIA_18, 1):
        linhas.append(nova("D-g", "regras_auditoria_18", "regra", f"regra_{i}", "0.300 e 0.400", var=rg["secao"],
                           descricao=rg["regra"], valor_abaixo=np.nan,
                           nota=f"0,300: {rg['em_0300']}; 0,400: {rg['em_0400']}; fronteira: {rg['fronteira']}"))
    return linhas


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------

def aplicar_bky(est: pd.DataFrame) -> pd.DataFrame:
    est["q_bky"] = np.nan
    for e in est["explicacao"].unique():
        m = (est["explicacao"] == e) & (est["tipo_linha"] == "salto") & est["p_valor"].notna() \
            & (est["rotulo"] == ROT_PROTOCOLO)
        if m.sum():
            est.loc[m, "q_bky"] = L.qvalores_bky(est.loc[m, "p_valor"].to_numpy(dtype=float))
    return est


def leitura_preregistrada(est: pd.DataFrame, info_da: dict, info_dc: dict) -> dict:
    c = RC[300]
    da = {q: info_da[(ROT_PROTOCOLO, q, 300)] for q in Q}
    da_apoia = all(v["p_posto"] > 0.10 for v in da.values())
    da_comp = {q: info_da[(ROT_COMPLEMENTAR, q, 300)] for q in Q}
    fix = est[(est["tipo_linha"] == "fixado") & (est["corte"] == c) & (est["status"] == "EXECUTADO")]
    reduz = {}
    for _, r in fix.iterrows():
        if r["reduz_metade"] == "sim":
            reduz.setdefault(f"{r['explicacao']} ({r['variante']})", []).append(r["quantidade"])
    dfc = est[(est["explicacao"] == "D-f") & (est["bloco"] == "ciclo2") & (est["corte"] == c)
              & (est["quantidade"] == "Q2_ciclo2")].set_index("variante")
    df_com, df_sem = float(dfc.at["todas_as_celulas", "tau"]), float(dfc.at["sem_celulas_so_cr", "tau"])
    df_apoia = abs(df_sem) <= LIMIAR_METADE * abs(df_com)
    contrib = info_dc.get(c, {}).get("contribuicoes", {})
    tot = sum(abs(v) for v in contrib.values()) if contrib else float("nan")
    maior = max(contrib, key=lambda k: abs(contrib[k])) if contrib else None
    dc_concentra = bool(contrib) and abs(contrib[maior]) >= (2 / 3) * tot
    if da_apoia:
        principal = "ACASO_MAIS_POUCOS_MUNICIPIOS"
    elif reduz or df_apoia:
        principal = "EXPLICACOES_CANDIDATAS_DESCRITIVAS"
    else:
        principal = "SEM_EXPLICACAO_NOS_DADOS"
    candidatas = sorted({k.split(" ")[0] for k in reduz} | ({"D-f"} if df_apoia else set()))
    return {
            "descritivas_que_reduzem_metade": candidatas,"D-a": {"p_posto_por_q": {q: v["p_posto"] for q, v in da.items()},
                    "p_minimo_possivel": da["Q1"]["p_minimo_possivel"], "n_placebos": da["Q1"]["n_placebos"],
                    "apoia": da_apoia,
                    "ressalva": "com a grade do protocolo sobram 3 cortes placebo (0,250; 0,350; 0,450): o menor p por "
                                "posto possivel e 1/4 = 0,25 > 0,10, entao o criterio 'p por posto > 0,10' e cumprido "
                                "por construcao e nao informa se o salto se destaca",
                    "complementar_fora_do_protocolo": {q: {"p_posto": v["p_posto"], "n_placebos": v["n_placebos"]}
                                                       for q, v in da_comp.items()}},
            "fixar_reduz_metade_em_0300": reduz,
            "D-c": {"contribuicoes": contrib, "maior": maior, "concentra": dc_concentra,
                    "regra": "concentra se a maior contribuicao em modulo for >= 2/3 da soma dos modulos"},
            "D-f": {"tau_q2_ciclo2_todas": df_com, "tau_q2_ciclo2_sem_so_cr": df_sem, "apoia": df_apoia,
                    "regra": "some = o salto do ciclo 2 sem as celulas so de CR cai pela metade ou mais"},
            "leitura_principal": principal,
            "regra": "§3 do protocolo 61: D-a apoia -> acaso mais poucos municipios; senao, D-b a D-f que reduzem o "
                     "salto pela metade ou mais -> explicacoes candidatas, descritivas; senao, nao ha explicacao"}


def estimar_tudo(log=print) -> tuple[pd.DataFrame, dict]:
    B = carregar()
    V, CK, U = B["V"], B["CK"], B["U"]
    log("  dados carregados")
    lin_rep, conf = reproduzir(V, CK)
    refs = {}
    for c in CORTES:
        for q in Q:
            refs[(q, c)] = fit_q(q, V, CK, c)
    log(f"  reproducao de Q1-Q3: max dif {conf['max_abs_dif']:.2e}")
    linhas = list(lin_rep)
    l_da, info_da = bloco_da(V, CK, refs)
    linhas += l_da
    log(f"  D-a: {len(l_da)} linhas")
    linhas += bloco_db(V, CK, refs)
    log("  D-b")
    l_dc, info_dc = bloco_dc(V, CK, refs)
    linhas += l_dc
    log("  D-c")
    linhas += bloco_dd(V, CK, refs)
    log("  D-d")
    linhas += bloco_de(V, CK, U, refs)
    log("  D-e")
    l_df, regra_c2 = bloco_df(V, CK, refs)
    linhas += l_df
    log("  D-f")
    linhas += bloco_dg(V, U)
    log("  D-g")
    est = pd.DataFrame(linhas)[COLUNAS]
    if est["id_linha"].duplicated().any():
        raise FalhaValidacao(f"id_linha duplicado: {est.loc[est['id_linha'].duplicated(), 'id_linha'].tolist()[:5]}")
    est = aplicar_bky(est)
    leitura = leitura_preregistrada(est, info_da, info_dc)
    extras = {"reproducao": conf, "info_dados": B["info"], "regra_ciclo2": regra_c2, "leitura": leitura,
              "decomposicao_funil": info_dc,
              "placebos": {"grade_protocolo_mil": list(PLACEBOS), "grade_complementar_mil": list(PLACEBOS_COMPLEMENTARES)}}
    return est, extras


# ---------------------------------------------------------------------------
# Formatação (números sempre lidos das saídas)
# ---------------------------------------------------------------------------

def _num(v, casas=2, sinal=True) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if not math.isfinite(v):
        return "—"
    if round(v, casas) == 0:
        v = 0.0
    return (f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}").replace("-", "−").replace(".", ",")


def _pp(v, casas=1, sinal=True) -> str:
    try:
        return _num(float(v) * 100, casas, sinal)
    except (TypeError, ValueError):
        return "—"


def _fq(q: str, v, sinal=True) -> str:
    """Valor na unidade da quantidade: Q1 em vagas (2 casas); Q2, Q3 e frações em p.p. (1 casa)."""
    return _num(v, 2, sinal) if q == "Q1" else _pp(v, 1, sinal) + " p.p."


def _ic(r, q="Q1") -> str:
    f = (lambda v: _num(v, 2)) if q == "Q1" else (lambda v: _pp(v))
    return f"[{f(r['ic95_inf'])}; {f(r['ic95_sup'])}]"


def _p(v) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    return "—" if not math.isfinite(v) else ("< 0,001" if v < 0.001 else f"{v:.3f}".replace(".", ","))


def _e(v) -> str:
    return f"{float(v):.1e}".replace(".", ",").replace("-", "−")


def _int(v) -> str:
    try:
        return str(int(round(float(v))))
    except (TypeError, ValueError):
        return "—"


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    out += ["| " + " | ".join(str(x) for x in ln) + " |" for ln in linhas]
    return "\n".join(out)


def _bloco(nome: str, corpo: str) -> str:
    return f"<!-- DQ:{nome}:inicio -->\n{corpo.strip()}\n<!-- DQ:{nome}:fim -->"


def _sel(est: pd.DataFrame, **f) -> pd.DataFrame:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        m &= (est[k].astype(str) == str(v)).to_numpy()
    return est[m]


def _um(est: pd.DataFrame, **f) -> pd.Series:
    s = _sel(est, **f)
    if len(s) != 1:
        raise FalhaValidacao(f"esperada 1 linha para {f}, achadas {len(s)}")
    return s.iloc[0]


def _excl(r) -> bool:
    return (float(r["ic95_inf"]) > 0) or (float(r["ic95_sup"]) < 0)


ROT_C = {RC[300]: "0,300", RC[400]: "0,400"}
NOME_FATOR = {
    ("D-b", "composicao"): "D-b composição (parte de CR, células só de CR, vagas imediatas por célula, índices de "
                           "curso, tipo e gestão; em Q3, tipo e gestão do estabelecimento)",
    ("D-b", "sem_celulas_so_cr"): "D-b (iii) sem as células só de CR",
    ("D-c", "funil"): "D-c funil: igualando quem teve candidato de 1ª opção",
    ("D-d", "concorrencia"): "D-d concorrência (células do mesmo curso na CIR e na UF, e as de bolsa igual ou maior)",
    ("D-e", "medicos_por_perto"): "D-e médicos por perto (vínculos do curso na CIR, distância à origem, REGIC)",
    ("D-f", "sem_so_cr_ciclo2"): "D-f sem as células só de CR do ciclo 2",
}
NOME_CURTO = {("D-b", "composicao"): "D-b composição", ("D-b", "sem_celulas_so_cr"): "D-b sem as células só de CR",
              ("D-c", "funil"): "D-c funil", ("D-d", "concorrencia"): "D-d concorrência",
              ("D-e", "medicos_por_perto"): "D-e médicos por perto",
              ("D-f", "sem_so_cr_ciclo2"): "D-f sem as células só de CR do ciclo 2"}
ROT_VAR_DF = {"todas_as_celulas": "todas as células", "sem_celulas_so_cr": "sem as células só de CR",
              "so_vagas_imediatas": "só vagas imediatas (N1 / vagas imediatas)"}
ROT_MOTIVO = {"sem_vaga_imediata": "sem vaga imediata (célula só de CR)",
              "desconsiderada_pela_gestao": "alocação desconsiderada pela gestão (ciclo 1)",
              "candidato_alocado_em_outra_celula": "candidato alocado em outra célula",
              "candidatos_inelegiveis": "todos os candidatos inelegíveis (ciclo 1)",
              "outro_nao_distinguido": "outro (a base não distingue)"}
ROT_MED = {
    "so_cr": "célula só de CR", "idx_curso": "índice de curso", "idx_tipo": "índice de tipo do estabelecimento",
    "idx_gestao": "índice de gestão", "gestao_estadual": "gestão estadual", "hospital_geral": "hospital geral",
    "frac_cr": "parte das vagas em CR (municípios)", "frac_cel_so_cr": "parte das células só de CR (municípios)",
    "vi_por_cel": "vagas imediatas por célula (municípios)",
    "n_conc_cir": "concorrentes na CIR", "n_conc_uf": "concorrentes na UF", "n_ge_cir": "na CIR com bolsa ≥",
    "n_ge_uf": "na UF com bolsa ≥", "bolsa_media_cir": "bolsa média das concorrentes na CIR (R$ mil)",
    "bolsa_media_uf": "bolsa média das concorrentes na UF (R$ mil)",
    "vinc_curso_regiao_10k": "vínculos pré do curso na CIR por 10 mil hab.", "dist_origem_km": "distância à origem (km)",
    "regic_nivel": "nível REGIC", "vinc_alvo_regiao_10k": "vínculos pré das CBO-alvo na CIR por 10 mil hab.",
    "gen_pre_10k": "generalistas pré por 10 mil hab.", "sus_pre_10k": "vínculos SUS pré por 10 mil hab.",
}
FRACOES = {"so_cr", "idx_curso", "idx_tipo", "idx_gestao", "gestao_estadual", "hospital_geral", "frac_cr",
           "frac_cel_so_cr"}


def _fm(col: str, v) -> str:
    if col in FRACOES:
        return _pp(v) + " p.p."
    casas = 1 if col in ("dist_origem_km", "sus_pre_10k") else 2
    return _num(v, casas)


def _icm(col: str, r) -> str:
    if col in FRACOES:
        return f"[{_pp(r['ic95_inf'])}; {_pp(r['ic95_sup'])}]"
    casas = 1 if col in ("dist_origem_km", "sus_pre_10k") else 2
    return f"[{_num(r['ic95_inf'], casas)}; {_num(r['ic95_sup'], casas)}]"


# ---------------------------------------------------------------------------
# Figuras (legíveis em slide; "Como ler" fica no doc e no resumo, nunca dentro da imagem)
# ---------------------------------------------------------------------------

COR_300 = "#eb6834"
COR_400 = "#2a78d6"
CINZA = "#a3a29c"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
SUPERF = "#fcfcfb"
COMO_LER = {
    "DQ_placebos.png": "Cada ponto é o salto medido num corte que não existe (corte falso), em erros-padrão (t); quanto "
                       "mais longe do zero, maior. Os pontos pretos são os 3 cortes falsos do protocolo; os cinza "
                       "vazados, a grade maior, fora do protocolo. O losango laranja é o salto no corte real 0,300 e o "
                       "azul, em 0,400. Se o laranja fica no meio dos outros, um salto daquele tamanho é comum; se fica "
                       "mais longe que todos, é raro. Os cortes falsos vizinhos usam quase os mesmos municípios, então "
                       "não são sorteios independentes.",
    "DQ_quanto_da_queda.png": "A primeira linha de cada painel é a queda em 0,300 como foi medida. Cada linha abaixo é a "
                              "mesma queda depois de igualar um fator entre os dois lados do corte. Se o ponto chega "
                              "perto do zero (passa da linha tracejada, metade da queda), aquele fator acompanha boa "
                              "parte da queda; isso descreve, não prova causa.",
    "DQ_funil.png": "Cada par de barras compara as células logo abaixo (azul) e logo acima (laranja) do corte: quantas "
                    "eram só de cadastro reserva, quantas tiveram alguém que as escolheu em 1º lugar, quantas destas "
                    "foram preenchidas e quantas foram preenchidas no total. Mostra em que passo os dois lados se "
                    "separam.",
}
DETALHE_FIG = {
    "DQ_placebos.png": "Estatística t do salto (mesma especificação de Q1, Q2 e Q3: local linear, h = 0,050, kernel "
                       "triangular, ciclos 1–3 juntos, CR1 por município). Pontos pretos: os 3 cortes placebo do "
                       "protocolo 61 (0,250; 0,350; 0,450). Pontos cinza vazados: grade complementar fora do protocolo "
                       "(0,250 a 0,450, passo 0,005, a mais de 0,010 dos cortes reais, só observações do mesmo segmento "
                       "de bolsa). Linhas tracejadas: |t| = 1,96.",
    "DQ_quanto_da_queda.png": "Salto em 0,300 com IC 95% (CR1 por município): Q1 em vagas por município; Q2 e Q3 em "
                              "p.p. 'Original' = Q reproduzido. Fatores como covariável comparam-se ao original na "
                              "mesma amostra; fatores que retiram células, ao original (DQ_estimativas.csv, "
                              "tipo_linha = fixado). Linha tracejada = metade do original.",
    "DQ_funil.png": "Médias simples nas células da janela (|IVS − corte| < 0,050), ciclos 1–3 juntos, sem reta nem efeitos "
                    "fixos (tipo_linha = funil_bruto). Os saltos com a especificação de Q3 estão na tabela do D-c.",
}


def gerar_figuras(est: pd.DataFrame, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    plt.rcParams.update({"font.size": 14, "axes.titlesize": 16, "axes.labelsize": 14, "xtick.labelsize": 12,
                         "ytick.labelsize": 12, "axes.edgecolor": TINTA_2, "axes.labelcolor": TINTA,
                         "text.color": TINTA, "xtick.color": TINTA_2, "ytick.color": TINTA_2,
                         "figure.facecolor": SUPERF, "axes.facecolor": SUPERF, "savefig.facecolor": SUPERF})
    feitas = []
    titulos_q = {"Q1": "Q1: vagas preenchidas\n(com controle)", "Q2": "Q2: taxa por vaga\noferecida",
                 "Q3": "Q3: célula aberta\npreenchida"}
    # (1) placebos
    fig, eixos = plt.subplots(1, 3, figsize=(16, 7.2), sharey=True)
    for ax, q in zip(eixos, Q):
        comp = _sel(est, tipo_linha="placebo", quantidade=q, rotulo=ROT_COMPLEMENTAR)
        prot = _sel(est, tipo_linha="placebo", quantidade=q, rotulo=ROT_PROTOCOLO)
        ax.axhline(0, color=TINTA_2, lw=1)
        for y0 in (-1.96, 1.96):
            ax.axhline(y0, color=CINZA, lw=1.2, ls="--")
        ax.scatter(comp["corte_placebo"].astype(float), comp["t"].astype(float), s=70, facecolors="none",
                   edgecolors=CINZA, lw=1.6, label="cortes falsos (grade ampla, fora do protocolo)")
        ax.scatter(prot["corte_placebo"].astype(float), prot["t"].astype(float), s=90, color=TINTA_2,
                   label="cortes falsos do protocolo", zorder=3)
        for c, cor in ((300, COR_300), (400, COR_400)):
            r = _um(est, tipo_linha="resumo_placebo", quantidade=q, rotulo=ROT_PROTOCOLO, corte=RC[c])
            ax.scatter([c / 1000], [float(r["t"])], marker="D", s=170, color=cor, zorder=4, edgecolors=SUPERF,
                       lw=1.5, label=f"corte real {ROT_C[RC[c]]}")
            ax.annotate(f"t = {_num(r['t'], 2, False if float(r['t']) >= 0 else True)}", (c / 1000, float(r["t"])),
                        textcoords="offset points", xytext=(10, -4), fontsize=13, color=cor)
        ax.set_title(titulos_q[q])
        ax.set_xlabel("corte (IVS 2010)")
        ax.set_xticks([0.25, 0.30, 0.35, 0.40, 0.45])
        ax.set_xticklabels(["0,25", "0,30", "0,35", "0,40", "0,45"])
        ax.spines[["top", "right"]].set_visible(False)
    eixos[0].set_ylabel("tamanho do salto (estatística t)")
    h, lab = eixos[0].get_legend_handles_labels()
    fig.legend(h, lab, loc="lower center", ncol=4, frameon=False, fontsize=12)
    fig.suptitle("Saltos em cortes falsos e nos cortes reais", fontsize=18)
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    nome = "DQ_placebos.png"
    fig.savefig(dir_fig / nome, dpi=150)
    plt.close(fig)
    feitas.append(nome)
    # (2) quanto da queda cada explicação leva (0,300)
    fig, eixos = plt.subplots(1, 3, figsize=(16, 7.2))
    rot_lin = [("original", "Queda medida"), (("D-b", "composicao"), "composição das vagas"),
               (("D-b", "sem_celulas_so_cr"), "sem células só de CR"), (("D-c", "funil"), "candidato de 1ª opção"),
               (("D-d", "concorrencia"), "concorrência"), (("D-e", "medicos_por_perto"), "médicos por perto"),
               (("D-f", "sem_so_cr_ciclo2"), "sem CR do ciclo 2")]
    for ax, q in zip(eixos, Q):
        orig = _um(est, tipo_linha="reproducao", quantidade=q, corte=RC[300])
        esc = 1.0 if q == "Q1" else 100.0
        ys, xs, los, his, cores = [], [], [], [], []
        for i, (chave, _) in enumerate(rot_lin):
            r = orig if chave == "original" else _um(est, tipo_linha="fixado", quantidade=q, corte=RC[300],
                                                       explicacao=chave[0], variante=chave[1])
            ys.append(len(rot_lin) - 1 - i)
            xs.append(float(r["tau"]) * esc)
            los.append(float(r["ic95_inf"]) * esc)
            his.append(float(r["ic95_sup"]) * esc)
            cores.append(COR_300 if chave == "original" else TINTA_2)
        ax.axvline(0, color=TINTA_2, lw=1)
        ax.axvline(float(orig["tau"]) * esc / 2, color=CINZA, lw=1.2, ls="--")
        for y, x, lo, hi, cor in zip(ys, xs, los, his, cores):
            if np.isfinite(x):
                ax.plot([lo, hi], [y, y], color=cor, lw=2.5, solid_capstyle="round")
                ax.scatter([x], [y], s=110, color=cor, zorder=3, edgecolors=SUPERF, lw=1.5)
        ax.set_yticks(ys)
        ax.set_yticklabels([lab for _, lab in rot_lin] if q == "Q1" else [""] * len(rot_lin))
        ax.set_title(titulos_q[q])
        ax.set_xlabel("salto em 0,300 (vagas por município)" if q == "Q1" else "salto em 0,300 (p.p.)")
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Quanto da queda em 0,300 sobra ao igualar cada fator (IC 95%)", fontsize=18)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    nome = "DQ_quanto_da_queda.png"
    fig.savefig(dir_fig / nome, dpi=150)
    plt.close(fig)
    feitas.append(nome)
    # (3) funil de cada lado
    fig, eixos = plt.subplots(1, 2, figsize=(16, 7.2), sharey=True)
    passos = [("so_cr", "só cadastro\nreserva"), ("tem_cand1", "tem candidato\nde 1ª opção"),
              ("preenchida_dado_cand1", "preenchida, entre\nas com candidato"), ("preenchida", "preenchida\n(todas)")]
    for ax, c in zip(eixos, CORTES):
        n = _um(est, tipo_linha="funil_bruto", quantidade="celulas", corte=RC[c])
        xs = np.arange(len(passos))
        for desl, lado, cor, rot in ((-0.2, "valor_abaixo", COR_400, f"abaixo do corte ({_int(n['valor_abaixo'])} células)"),
                                     (0.2, "valor_acima", COR_300, f"acima do corte ({_int(n['valor_acima'])} células)")):
            vals = [float(_um(est, tipo_linha="funil_bruto", quantidade=p, corte=RC[c])[lado]) * 100 for p, _ in passos]
            ax.bar(xs + desl, vals, width=0.38, color=cor, label=rot, edgecolor=SUPERF, linewidth=2)
            for x, v in zip(xs + desl, vals):
                ax.text(x, v + 1.2, f"{v:.0f}%", ha="center", va="bottom", fontsize=13, color=TINTA)
        ax.set_xticks(xs)
        ax.set_xticklabels([lab for _, lab in passos])
        ax.set_title(f"Corte {ROT_C[RC[c]]}")
        ax.set_ylim(0, 100)
        ax.legend(frameon=False, fontsize=12, loc="upper right")
        ax.spines[["top", "right"]].set_visible(False)
    eixos[0].set_ylabel("% das células da janela")
    fig.suptitle("O caminho da célula até ser preenchida, de cada lado do corte (|IVS − corte| < 0,050)", fontsize=18)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    nome = "DQ_funil.png"
    fig.savefig(dir_fig / nome, dpi=150)
    plt.close(fig)
    feitas.append(nome)
    return [{"arquivo": rotulo(dir_fig / f), "como_ler": COMO_LER[f], "detalhe_tecnico": DETALHE_FIG[f]}
            for f in feitas]


# ---------------------------------------------------------------------------
# Documento 57l (gerado inteiro a partir das saídas)
# ---------------------------------------------------------------------------

def resposta_curta(est: pd.DataFrame, resumo: dict) -> str:
    lt = resumo["leitura"]
    q = {k: _um(est, tipo_linha="reproducao", quantidade=k, corte=RC[300]) for k in Q}
    q4 = {k: _um(est, tipo_linha="reproducao", quantidade=k, corte=RC[400]) for k in Q}
    da = lt["D-a"]
    comp = da["complementar_fora_do_protocolo"]
    fis = {(k, w): _um(est, explicacao="D-a", bloco="fisher", quantidade=k, corte=RC[300], variante=f"janela_{w / 1000:.3f}")
           for k in Q for w in JANELAS_FISHER}
    p = []
    p.append(f"**O que cai.** Em 0,300, com os ciclos 1–3 juntos, o lado de bolsa maior tem {_fq('Q1', q['Q1']['tau'])} "
             f"vaga preenchida por município, dadas as vagas oferecidas (Q1, IC 95% {_ic(q['Q1'])}); a taxa por vaga "
             f"oferecida é {_fq('Q2', q['Q2']['tau'])} (Q2, IC {_ic(q['Q2'], 'Q2')}); a chance de uma célula aberta ser "
             f"preenchida é {_fq('Q3', q['Q3']['tau'])} (Q3, IC {_ic(q['Q3'], 'Q3')}"
             f"{', que contém zero' if not _excl(q['Q3']) else ''}). Em 0,400 nada disso aparece (Q1 "
             f"{_fq('Q1', q4['Q1']['tau'])}, Q2 {_fq('Q2', q4['Q2']['tau'])}, Q3 {_fq('Q3', q4['Q3']['tau'])}).")
    destaca = [k for k in Q if comp[k]["p_posto"] <= 0.10]
    nao_destaca = [k for k in Q if comp[k]["p_posto"] > 0.10]
    p.append(f"**Acaso.** A regra pré-registrada dá apoio ao acaso (p por posto = "
             + ", ".join(f"{k} {_p(da['p_posto_por_q'][k])}" for k in Q)
             + f"), mas esse teste não podia dar outra coisa: a grade do protocolo deixa só "
             f"{da['n_placebos']} cortes falsos, e o menor p possível é {_p(da['p_minimo_possivel'])}. Numa grade "
             f"maior, fora do protocolo ({comp['Q1']['n_placebos']} cortes falsos), "
             + ((f"a queda de {' e de '.join(destaca)} fica entre as maiores (p por posto "
                 + ", ".join(f"{k} {_p(comp[k]['p_posto'])}" for k in destaca) + ")"
                 + (f", e a de {' e de '.join(nao_destaca)} não se destaca (p por posto "
                    + ", ".join(f"{k} {_p(comp[k]['p_posto'])}" for k in nao_destaca) + "). "
                    if nao_destaca else ". "))
                if destaca else "nenhuma das três se destaca (p por posto "
                + ", ".join(f"{k} {_p(comp[k]['p_posto'])}" for k in Q) + "). ")
             + f"Comparando só os municípios a até 0,010 do corte (randomização local), p = "
             + ", ".join(f"{k} {_p(fis[(k, 10)]['p_valor'])}" for k in Q) + "; a até 0,020, p = "
             + ", ".join(f"{k} {_p(fis[(k, 20)]['p_valor'])}" for k in Q) + ". Acaso não fica descartado nem "
             "confirmado.")
    # Descrições
    fx = _sel(est, tipo_linha="fixado", corte=RC[300])
    frases = []
    for (e, v), nome in NOME_FATOR.items():
        s = fx[(fx["explicacao"] == e) & (fx["variante"] == v) & (fx["reduz_metade"] == "sim")]
        if len(s):
            frases.append(f"{NOME_CURTO[(e, v)]} ({', '.join(s['quantidade'])})")
    comp_cel = {m: _um(est, explicacao="D-b", bloco="composicao", quantidade=m, ciclo="1+2+3", corte=RC[300])
                for m in ("so_cr", "idx_curso")}
    comp_cel4 = {m: _um(est, explicacao="D-b", bloco="composicao", quantidade=m, ciclo="1+2+3", corte=RC[400])
                 for m in ("so_cr", "idx_curso")}
    fun = {k: _um(est, explicacao="D-c", bloco="funil", quantidade=k, corte=RC[300], variante="especificacao_Q3")
           for k in ("P_C", "P_F_dado_C")}
    d2 = lt["D-f"]
    cr_tambem_0400 = float(comp_cel4["so_cr"]["tau"]) >= LIMIAR_METADE * float(comp_cel["so_cr"]["tau"]) > 0
    fb = {k: _um(est, tipo_linha="funil_bruto", quantidade="preenchida", corte=RC[k]) for k in CORTES}
    p.append("**Sem a reta.** Nas células da janela inteira (|IVS − corte| < 0,050), sem reta nem efeitos fixos, a "
             f"fração preenchida é {_pp(fb[300]['valor_abaixo'], 1, False)}% abaixo e {_pp(fb[300]['valor_acima'], 1, False)}% "
             "acima de 0,300 (figura do funil): a queda aparece quando a reta de cada lado é levada até o corte, e "
             "depende de poucos municípios perto dele (doc 49b, §6).")
    p.append("**O que acompanha a queda (descritivo).** "
             + (f"Acima de 0,300, a parte das células que são só de cadastro reserva é {_fm('so_cr', comp_cel['so_cr']['tau'])} "
                f"maior (IC {_icm('so_cr', comp_cel['so_cr'])}) e as células são de cursos que preenchem "
                f"{_fm('idx_curso', -float(comp_cel['idx_curso']['tau'])).lstrip('+')} menos fora da janela (índice de curso "
                f"{_fm('idx_curso', comp_cel['idx_curso']['tau'])}, IC {_icm('idx_curso', comp_cel['idx_curso'])}); em 0,400, "
                f"{_fm('so_cr', comp_cel4['so_cr']['tau'])} e {_fm('idx_curso', comp_cel4['idx_curso']['tau'])}"
                + ("; o excesso de células só de CR aparece também em 0,400, onde não há queda, e por isso não explica "
                   "sozinho a queda em 0,300" if cr_tambem_0400 else "") + ". ")
             + f"No funil, a chance de a célula ter um candidato de 1ª opção muda {_fm('so_cr', fun['P_C']['tau'])} "
               f"(IC {_icm('so_cr', fun['P_C'])}), e a de ser preenchida quando tem esse candidato muda "
               f"{_fm('so_cr', fun['P_F_dado_C']['tau'])} (IC {_icm('so_cr', fun['P_F_dado_C'])}). "
             + f"No ciclo 2, a queda da taxa vai de {_pp(d2['tau_q2_ciclo2_todas'])} p.p. para "
               f"{_pp(d2['tau_q2_ciclo2_sem_so_cr'])} p.p. sem as células só de CR do {QUADRO_C2_POS}, que não "
               f"registra alocado nelas (correção de 26/10/2026: {REF_A36}). {AVISO_SELECAO_C2} "
             + ("Igualar um fator entre os lados reduz a queda em 0,300 pela metade ou mais em: " + "; ".join(frases) + "."
                if frases else "Nenhum fator, igualado entre os lados, reduz a queda pela metade."))
    de = _sel(est, explicacao="D-e", bloco="balanco", corte=RC[300])
    de_salta = [r["quantidade"] for _, r in de.iterrows() if _excl(r)]
    dg = _sel(est, explicacao="D-g", bloco="balanco", corte=RC[300])
    dg_salta = [f"{ROT_MED.get(r['quantidade'], r['quantidade'])} ({r['populacao']})" for _, r in dg.iterrows() if _excl(r)]
    p.append("**O que não explica.** "
             + ("Médicos por perto (D-e): nenhuma medida salta no corte e igualá-las não reduz a queda pela metade. "
                if not de_salta and "D-e" not in lt["descritivas_que_reduzem_metade"] else
                f"Médicos por perto (D-e): saltam {', '.join(de_salta) or 'nenhuma'}. ")
             + "Outras políticas (D-g) não têm teste causal; no balanço pré, "
             + (f"salta só {', '.join(dg_salta)}, " if dg_salta else "nada salta, ")
             + "e a única regra federal da auditoria 18 que muda em 0,300 e não em 0,400 é o acréscimo de 20% no teto de "
               "emendas e de parcelas de custeio da APS e da MAC.")
    p.append("**Leitura pré-registrada.** "
             + {"ACASO_MAIS_POUCOS_MUNICIPIOS": "Pela regra do §3, a explicação principal é acaso mais poucos "
                "municípios, e as demais viram descrição; mas, como o teste de acaso não podia reprovar, essa leitura "
                "vale como 'acaso não descartado', não como 'acaso demonstrado'.",
                "EXPLICACOES_CANDIDATAS_DESCRITIVAS": "As explicações que reduzem a queda pela metade são candidatas, "
                "descritivas.",
                "SEM_EXPLICACAO_NOS_DADOS": "Não há explicação nos dados disponíveis."}[lt["leitura_principal"]])
    # Frase para a banca (corrigida pela auditoria 33): cada cláusula sai das saídas e só entra com o sinal e a
    # incerteza que o CSV sustenta; a unidade dos índices é a célula (não a vaga); estimativa com IC que contém zero
    # leva "estimativa imprecisa"; a queda é dita como estimada no corte, ao lado das médias brutas da janela.
    reduz_por = {}
    for _, r in fx[fx["reduz_metade"] == "sim"].iterrows():
        reduz_por.setdefault((r["explicacao"], r["variante"]), set()).add(r["quantidade"])
    nenhum_nas_tres = not any(len(v) == len(Q) for v in reduz_por.values())
    conc_uf = _um(est, explicacao="D-d", bloco="medidas", quantidade="n_conc_uf", corte=RC[300])
    cr_c2 = _um(est, explicacao="D-b", bloco="composicao", quantidade="so_cr", ciclo="2", corte=RC[300])
    clausulas = []
    if _excl(comp_cel["idx_curso"]) and float(comp_cel["idx_curso"]["tau"]) < 0:
        clausulas.append("mais células de cursos que preenchem pouco em qualquer lugar")
    if _excl(comp_cel["so_cr"]) and float(comp_cel["so_cr"]["tau"]) > 0 and not cr_tambem_0400:
        clausulas.append("mais células só de cadastro reserva")
    if "D-d" in lt["descritivas_que_reduzem_metade"] and _excl(conc_uf) and float(conc_uf["tau"]) > 0:
        clausulas.append("mais células do mesmo curso na mesma UF")
    itens = [("o lado de cima tinha " + " e ".join(clausulas))] if clausulas else []
    if float(fun["P_C"]["tau"]) < 0 and "D-c" in lt["descritivas_que_reduzem_metade"]:
        itens.append("menos células desse lado tiveram candidato de 1ª opção"
                     + ("" if _excl(fun["P_C"]) else " (estimativa imprecisa)"))
    if d2["apoia"]:
        itens.append(f"no ciclo 2, mais células desse lado eram só de reserva no {QUADRO_C2_POS}"
                     if (_excl(cr_c2) and float(cr_c2["tau"]) > 0) else
                     f"no ciclo 2 a queda diminui sem as células só de reserva do {QUADRO_C2_POS}")
    descr = ("; ".join(itens[:-1]) + "; e " + itens[-1]) if len(itens) > 1 else (itens[0] if itens else "")
    acaso = ("acaso não está descartado" if lt["leitura_principal"] == "ACASO_MAIS_POUCOS_MUNICIPIOS" or
             any(comp[k]["p_posto"] > 0.10 for k in Q) else "a queda é maior que a dos cortes falsos")
    fb0, fb1 = float(fb[300]["valor_abaixo"]), float(fb[300]["valor_acima"])
    reta = (f"A queda aparece quando a reta de cada lado é levada até o corte (nas médias da janela, "
            f"{_pp(fb0, 0, False)}% das células preenchidas abaixo e {_pp(fb1, 0, False)}% acima), e {acaso}. "
            if abs(fb1 - fb0) < LIMIAR_METADE * abs(float(q["Q3"]["tau"])) else f"E {acaso}. ")
    if descr:
        frase = (f"Em 0,300 o preenchimento estimado no corte cai, mas os dados só descrevem a queda. No corte, {descr}. "
                 + (("Igualando esses fatores entre os lados, a queda diminui pela metade ou mais em parte das medidas"
                     + (", nenhum fator nas três. " if nenhum_nas_tres else ". "))
                    if lt["descritivas_que_reduzem_metade"] else "Igualar esses fatores não reduz a queda pela metade. ")
                 + reta + "Nada disso mostra que a bolsa reduz o preenchimento: o corte junta a bolsa com outras regras.")
    else:
        frase = ("Em 0,300 o preenchimento estimado no corte cai, e os dados disponíveis não explicam por quê. "
                 + reta + "Nada disso mostra que a bolsa reduz o preenchimento: o corte junta a bolsa com outras regras.")
    p.append(f"**Para dizer na banca.** \"{frase}\"")
    if d2["apoia"]:
        p.append(NOTA_A36_BANCA)
    return "\n\n".join(p)


def tabela_reproducao(est) -> str:
    linhas = []
    for c in CORTES:
        for q in Q:
            r = _um(est, tipo_linha="reproducao", quantidade=q, corte=RC[c])
            linhas.append([ROT_C[RC[c]], q, DESC_Q[q].split(",")[0], f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}",
                           _fq(q, r["tau"]), _ic(r, q), _p(r["p_valor"]), _fq(q, r["alvo_tau"]),
                           _e(r["dif_max"])])
    return _tab(["Corte", "Q", "Definição", "municípios abaixo / acima", "Salto", "IC 95%", "p", "Alvo (N/NA/ND)",
                 "maior diferença (salto e EP)"], linhas)


def tabela_placebos(est, rot) -> str:
    linhas = []
    for q in Q:
        for c in CORTES:
            r = _um(est, tipo_linha="resumo_placebo", quantidade=q, corte=RC[c], rotulo=rot)
            linhas.append([q, ROT_C[RC[c]], _num(r["t"]), _int(r["n_placebos"]), _p(r["p_posto"]),
                           _p(r["valor"]), _pp(r["frac_t_maior_196"], 1, False) + "%"])
    return _tab(["Q", "Corte real", "t do salto real", "cortes falsos", "p por posto", "menor p possível",
                 "cortes falsos com |t| > 1,96"], linhas)


def tabela_placebos_lista(est) -> str:
    linhas = []
    for q in Q:
        for _, r in _sel(est, tipo_linha="placebo", quantidade=q, rotulo=ROT_PROTOCOLO).iterrows():
            linhas.append([q, str(r["corte_placebo"]).replace(".", ","), _fq(q, r["tau"]), _num(r["t"]),
                           f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}"])
    return _tab(["Q", "Corte falso", "Salto", "t", "municípios abaixo / acima"], linhas)


def tabela_fisher(est) -> str:
    linhas = []
    for q in Q:
        for c in CORTES:
            for w in JANELAS_FISHER:
                r = _um(est, explicacao="D-a", bloco="fisher", quantidade=q, corte=RC[c], variante=f"janela_{w / 1000:.3f}")
                linhas.append([q, ROT_C[RC[c]], f"±{w / 1000:.3f}".replace(".", ","), f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}",
                               _fq(q, r["tau"]), _p(r["p_valor"]), _p(r["q_bky"])])
    return _tab(["Q", "Corte", "Janela", "municípios abaixo / acima", "Diferença ajustada", "p de Fisher", "q BKY (D-a)"],
                linhas)


def _linha_salto(r, rot=None) -> list[str]:
    col = r["quantidade"]
    return [rot or ROT_MED.get(col, col), f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}", _fm(col, r["media_abaixo"]).lstrip("+"),
            _fm(col, r["tau"]), _icm(col, r), _p(r["p_valor"]), _p(r["q_bky"])]


CAB_SALTO = ["Medida", "municípios abaixo / acima", "Média abaixo", "Salto", "IC 95%", "p", "q BKY"]


def tabela_db_comp(est, ciclo) -> str:
    linhas = []
    for c in CORTES:
        for col, _, _ in COMP_CEL:
            r = _um(est, explicacao="D-b", bloco="composicao", quantidade=col, ciclo=ciclo, corte=RC[c])
            linhas.append([ROT_C[RC[c]]] + _linha_salto(r))
        for col, _, _ in COMP_MUN:
            r = _um(est, explicacao="D-b", bloco="composicao", quantidade=col, ciclo=ciclo, corte=RC[c])
            linhas.append([ROT_C[RC[c]]] + _linha_salto(r))
    return _tab(["Corte"] + CAB_SALTO, linhas)


def tabela_db_ciclos(est) -> str:
    linhas = []
    for col in ("so_cr", "idx_curso", "gestao_estadual", "frac_cr", "vi_por_cel"):
        ln = [ROT_MED[col]]
        for c in CORTES:
            for k in ("1", "2", "3"):
                r = _um(est, explicacao="D-b", bloco="composicao", quantidade=col, ciclo=k, corte=RC[c])
                ln.append(_fm(col, r["tau"]) + ("*" if _excl(r) else ""))
        linhas.append(ln)
    return _tab(["Medida"] + [f"{ROT_C[RC[c]]}, ciclo {k}" for c in CORTES for k in (1, 2, 3)], linhas)


def tabela_db_q3(est) -> str:
    linhas = []
    for c in CORTES:
        for var, rot in (("sem_composicao", "sem efeitos fixos"), ("original_Q3", "Q3 (curso × ciclo, tipo de vaga)"),
                         ("com_composicao", "Q3 + tipo e gestão do estabelecimento")):
            r = _um(est, explicacao="D-b", bloco="q3_composicao", corte=RC[c], variante=var)
            linhas.append([ROT_C[RC[c]], rot, f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}", _fq("Q3", r["tau"]),
                           _ic(r, "Q3"), _p(r["p_valor"])])
        r = _um(est, explicacao="D-b", bloco="q2_sem_so_cr", corte=RC[c])
        linhas.append([ROT_C[RC[c]], "(iii) Q2 sem as células só de CR", f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}",
                       _fq("Q2", r["tau"]), _ic(r, "Q2"), _p(r["p_valor"])])
    return _tab(["Corte", "Especificação", "municípios abaixo / acima", "Salto", "IC 95%", "p"], linhas)


def leitura_db_ii(est) -> str:
    """Teste (ii) do D-b lido como o protocolo o escreve: Q3 com toda a composição contra Q3 sem ela (auditoria 33)."""
    r = {v: _um(est, explicacao="D-b", bloco="q3_composicao", corte=RC[300], variante=v)
         for v in ("sem_composicao", "original_Q3", "com_composicao")}
    t0, tq, tc = (float(r[v]["tau"]) for v in ("sem_composicao", "original_Q3", "com_composicao"))
    return (f"**Leitura do teste (ii) como o protocolo o escreve** (acréscimo da auditoria 33). Em 0,300, do salto sem "
            f"efeitos fixos ({_fq('Q3', t0)}) ao salto com curso × ciclo, tipo de vaga, tipo e gestão do estabelecimento "
            f"({_fq('Q3', tc)}) sobram {_num(tc / t0 * 100, 0, False)}%: "
            + ("o salto cai pela metade ou mais" if abs(tc) <= LIMIAR_METADE * abs(t0) else "o salto não cai pela metade")
            + f". A maior parte da redução já vem de curso × ciclo e tipo de vaga ({_fq('Q3', tq)}), que o Q3 original "
              f"fixa; por isso a tabela da §10 compara a composição com o Q3 original (sobram "
              f"{_num(tc / tq * 100, 0, False)}%). As duas leituras são descritivas, e o D-b já está entre as explicações "
              "que reduzem a queda pela metade (§11); a leitura pré-registrada não muda.")


ROT_FUNIL = {"P_C":"P(candidato de 1ª opção)", "P_F_dado_C": "P(preenchida | candidato de 1ª opção)",
             "P_F_dado_semC": "P(preenchida | sem candidato de 1ª opção)", "P_F": "P(preenchida) = Q3"}


def tabela_dc(est) -> str:
    linhas = []
    for c in CORTES:
        for k, rot in ROT_FUNIL.items():
            r = _um(est, explicacao="D-c", bloco="funil", quantidade=k, corte=RC[c], variante="especificacao_Q3")
            r0 = _um(est, explicacao="D-c", bloco="funil", quantidade=k, corte=RC[c], variante="sem_efeitos_fixos")
            linhas.append([ROT_C[RC[c]], rot, f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}",
                           _pp(r["media_abaixo"], 1, False) + "%", _fq("Q3", r["tau"]), _ic(r, "Q3"), _p(r["p_valor"]),
                           _fq("Q3", r0["tau"])])
    return _tab(["Corte", "Parte", "municípios abaixo / acima", "Média abaixo", "Salto (espec. de Q3)", "IC 95%", "p",
                 "Salto sem efeitos fixos"], linhas)


def tabela_dc_decomp(est) -> str:
    linhas = []
    for c in CORTES:
        for k, rot in (("candidatos", "menos células com candidato de 1ª opção"),
                       ("preencher_dado_candidato", "preencher menos, tendo o candidato"),
                       ("preencher_sem_candidato", "preencher menos sem candidato de 1ª opção (por 2ª opção)"),
                       ("residuo", "resíduo (amostras diferentes)")):
            r = _um(est, explicacao="D-c", bloco="decomposicao", quantidade=k, corte=RC[c])
            linhas.append([ROT_C[RC[c]], rot, _pp(r["valor"]) + " p.p.",
                           (_pp(r["valor_abaixo"], 1, False) + "% → " + _pp(r["valor_acima"], 1, False) + "%")
                           if k != "residuo" else "—", _pp(r["tau"]) + " p.p."])
    return _tab(["Corte", "Parte", "Contribuição", "nível abaixo → acima", "Salto de P(preenchida), sem efeitos fixos"],
                linhas)


def tabela_dc_motivos(est) -> str:
    linhas = []
    for c in CORTES:
        for _, r in _sel(est, explicacao="D-c", bloco="motivos", tipo_linha="salto", corte=RC[c]).iterrows():
            linhas.append([ROT_C[RC[c]], ROT_MOTIVO[r["quantidade"]], f"{_int(r['valor_abaixo'])} / {_int(r['valor_acima'])}",
                           _fq("Q3", r["tau"]), _ic(r, "Q3") if np.isfinite(float(r["ep"])) and float(r["ep"]) > 0 else "—",
                           _p(r["p_valor"])])
        i = _um(est, explicacao="D-c", bloco="motivos", tipo_linha="identidade", corte=RC[c])
        linhas.append([ROT_C[RC[c]], "soma (= salto de P(preenchida | candidato), sinal trocado)", "—",
                       _fq("Q3", -float(i["tau"])), f"resíduo {_e(i['valor'])}", "—"])
    return _tab(["Corte", "Motivo (células com candidato de 1ª opção e não preenchidas)", "células abaixo / acima",
                 "Salto", "IC 95%", "p"], linhas)


def tabela_medidas(est, expl, bloco) -> str:
    linhas = []
    for c in CORTES:
        for _, r in _sel(est, explicacao=expl, bloco=bloco, tipo_linha="salto", corte=RC[c]).iterrows():
            unid = "célula" if r["unidade_analise"] == "celula" else ("município (U)" if r["populacao"] == "U"
                                                                     else "município × ciclo")
            linhas.append([ROT_C[RC[c]], unid] + _linha_salto(r))
    return _tab(["Corte", "Unidade"] + CAB_SALTO, linhas)


def tabela_df(est) -> str:
    linhas = []
    for c in CORTES:
        for _, r in _sel(est, explicacao="D-f", bloco="ciclo2", tipo_linha="salto", corte=RC[c]).iterrows():
            if r["quantidade"] == "Q2_ciclo2":
                linhas.append([ROT_C[RC[c]], f"Q2, ciclo 2: {ROT_VAR_DF[r['variante']]}",
                               f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}", _fq("Q2", r["tau"]), _ic(r, "Q2"),
                               _p(r["p_valor"]), "—"])
            else:
                n = _um(est, explicacao="D-f", tipo_linha="contagem", corte=RC[c])
                linhas.append([ROT_C[RC[c]], "células só de CR por município, ciclo 2",
                               f"{_int(r['n_abaixo'])} / {_int(r['n_acima'])}", _num(r["tau"]),
                               f"[{_num(r['ic95_inf'])}; {_num(r['ic95_sup'])}]", _p(r["p_valor"]),
                               f"{_int(r['valor_abaixo'])} de {_int(n['valor_abaixo'])} / {_int(r['valor_acima'])} de "
                               f"{_int(n['valor_acima'])}"])
    return _tab(["Corte", "Linha", "municípios abaixo / acima", "Salto", "IC 95%", "p",
                 "células só de CR / células na janela (abaixo / acima)"], linhas)


def tabela_resumo(est) -> str:
    linhas = []
    for c in CORTES:
        for q in Q:
            r = _um(est, tipo_linha="reproducao", quantidade=q, corte=RC[c])
            linhas.append([ROT_C[RC[c]], q, "**salto original (Q reproduzido)**", _fq(q, r["tau"]), _ic(r, q), "—", "—",
                           "—"])
        for q in Q:
            rp = _um(est, tipo_linha="resumo_placebo", quantidade=q, corte=RC[c], rotulo=ROT_PROTOCOLO)
            rc = _um(est, tipo_linha="resumo_placebo", quantidade=q, corte=RC[c], rotulo=ROT_COMPLEMENTAR)
            linhas.append([ROT_C[RC[c]], q, "D-a acaso (não fixa fator)", "—", "—", "—",
                           f"p por posto {_p(rp['p_posto'])} (complementar: {_p(rc['p_posto'])})", "—"])
        for (e, v), nome in NOME_FATOR.items():
            for q in Q:
                r = _um(est, tipo_linha="fixado", quantidade=q, corte=RC[c], explicacao=e, variante=v)
                if r["status"] != "EXECUTADO":
                    linhas.append([ROT_C[RC[c]], q, nome, "—", "—", "—", "não definido", "—"])
                    continue
                base = r["tau_original_mesma_amostra"] if pd.notna(r["tau_original_mesma_amostra"]) else r["tau_original"]
                linhas.append([ROT_C[RC[c]], q, nome, _fq(q, r["tau"]), _ic(r, q), _fq(q, base),
                               (_num(float(r["razao_fixado_original"]) * 100, 0, False) + "% do original"
                                if pd.notna(r["razao_fixado_original"]) else "—"),
                               r["reduz_metade"] if c == 300 else f"({r['reduz_metade']}; contraste)"])
        linhas.append([ROT_C[RC[c]], "—", "D-g outras políticas (sem teste causal)", "—", "—", "—", "relato", "—"])
    return _tab(["Corte", "Q", "Fator fixado", "Salto depois de fixar", "IC 95%", "Comparado com", "Quanto sobra",
                 "Reduz pela metade?"], linhas)


def gerar_doc(est: pd.DataFrame, resumo: dict) -> str:
    lt = resumo["leitura"]
    figs = resumo["saidas"]["figuras"]
    rc2 = resumo["regra_ciclo2"]
    nota = rc2["nota_do_quadro_original"]
    info = resumo["info_dados"]
    partes = []
    partes.append(f"""# 57l. Por que o preenchimento cai no corte 0,300? (diagnóstico, protocolo 61)

> **Data:** {DATA_EXECUCAO[8:]}/{DATA_EXECUCAO[5:7]}/{DATA_EXECUCAO[:4]}.<br>
> **Protocolo:** [`61_protocolo_diagnostico_queda_0300.md`](61_protocolo_diagnostico_queda_0300.md), congelado antes de
> qualquer conta (SHA-256 em `protocolo` de `DQ_resumo.json`).<br>
> **Estatuto:** `{ESTATUTO}`. Diagnóstico **descritivo e pós-resultado**: nada aqui vira especificação principal nem
> muda o Holm ou a leitura dos protocolos 40 e 48. Toda linha de `DQ_estimativas.csv` tem
> `natureza_dos_dados = EMPIRICO`.<br>
> **Contraste:** o **pacote do corte** — em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil, mas outras regras
> federais mudam no mesmo corte ([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)). Nada aqui é
> efeito da bolsa sozinha, da participação no PMM-E ou do Agora Tem Especialistas.<br>
> **Script:** `scripts/rdd_bolsa/38_diagnostico_queda_0300.py`. **Saídas:** `output/rdd_bolsa/DQ_estimativas.csv`,
> `DQ_resumo.json`, `DQ_figuras/`. **Testes:** `tests/test_diagnostico_queda_0300.py`.<br>
> **Números:** nenhum é digitado. Os blocos entre marcadores `<!-- DQ:... -->` são regravados das saídas por
> `38_diagnostico_queda_0300.py --atualizar-doc`; o teste confere que o documento é idêntico ao gerado.""")
    partes.append("## 1. Resposta curta\n\n" + _bloco("resposta_curta", resposta_curta(est, resumo)))
    partes.append("## 2. O que se quer explicar (reprodução de Q1–Q3)\n\n"
                  "Antes de qualquer teste, o script refaz Q1, Q2 e Q3 com as especificações e as entradas dos "
                  "protocolos 48 (§3, §7) e do ND, e para se não baterem com `N_estimativas.csv`, "
                  "`NA_estimativas.csv` e `ND_estimativas.csv`. Local linear, kernel triangular, h = 0,050, uma reta "
                  "de cada lado por ciclo, salto comum, CR1 por município.\n\n"
                  + _bloco("reproducao", tabela_reproducao(est)
                           + f"\n\nConferência: {resumo['validacoes']['reproducao']['linhas_alvo']} comparações, maior "
                             f"diferença {_e(resumo['validacoes']['reproducao']['max_abs_dif'])} (tolerância 1e−9)."))
    da = lt["D-a"]
    partes.append("## 3. D-a — acaso\n\n"
                  "**Teste do protocolo.** Cortes placebo de 0,250 a 0,450, passo 0,005, sem os pontos a menos de "
                  "h = 0,050 dos cortes reais, com a mesma especificação de Q1, Q2 e Q3; posição do salto real entre "
                  "os placebos (p por posto) e fração com |t| > 1,96. Apoio se p por posto > 0,10.\n\n"
                  + _bloco("da_placebos", tabela_placebos(est, ROT_PROTOCOLO) + "\n\n" + tabela_placebos_lista(est))
                  + "\n\n" + _bloco("da_ressalva",
                                    f"**Ressalva (desvio datado, {DATA_EXECUCAO[8:]}/{DATA_EXECUCAO[5:7]}/"
                                    f"{DATA_EXECUCAO[:4]}).** A regra de exclusão deixa só {da['n_placebos']} cortes "
                                    f"placebo ({', '.join(f'{c / 1000:.3f}'.replace('.', ',') for c in PLACEBOS)}). Com "
                                    f"{da['n_placebos']} placebos o menor p por posto possível é "
                                    f"{_p(da['p_minimo_possivel'])}, maior que 0,10: o critério de apoio é cumprido por "
                                    "construção e não informa se o salto se destaca. O protocolo não muda; a leitura "
                                    "literal é relatada e, ao lado dela, uma grade complementar **fora do protocolo** "
                                    "(rótulo `COMPLEMENTAR_FORA_DO_PROTOCOLO_61`): mesmos cortes de 0,250 a 0,450 a mais "
                                    "de 0,010 dos cortes reais, usando só as observações do mesmo segmento de bolsa do "
                                    "corte falso, como o S-i do protocolo 48 (a janela nunca atravessa 0,300 nem 0,400). "
                                    "Nessa grade, cortes falsos vizinhos compartilham quase todos os municípios e, perto "
                                    "dos cortes reais, a janela fica truncada de um lado, enquanto o salto real usa a "
                                    "janela inteira: o p por posto dela é indicativo, não um teste (nota da auditoria "
                                    "33).")
                  + "\n\n" + _bloco("da_complementar", tabela_placebos(est, ROT_COMPLEMENTAR))
                  + "\n\n**Randomização local (Fisher).** Janelas ±0,010 e ±0,020, 999 permutações, semente 20261026. "
                    "O lado do corte é sorteado entre os municípios da janela (todas as linhas de ciclo do município "
                    "andam juntas); a estatística é o coeficiente do lado de cima numa regressão com intercepto por "
                    "ciclo (Q1: e vagas oferecidas por ciclo; Q2: peso = vagas oferecidas; Q3: efeitos fixos de curso × "
                    "ciclo e tipo de vaga).\n\n" + _bloco("da_fisher", tabela_fisher(est)))
    partes.append("## 4. D-b — composição das vagas\n\n"
                  "**(i) A composição salta no corte?** Unidade célula (sem efeitos fixos) ou município × ciclo, "
                  "ciclos 1–3 juntos. Os índices de curso, de tipo e de gestão são o preenchimento médio da categoria "
                  "no mesmo ciclo entre as células fora das janelas dos dois cortes (|IVS − corte| ≥ 0,050): um salto "
                  "negativo quer dizer que, acima do corte, as células são de categorias que preenchem menos em "
                  "qualquer lugar. O tipo do estabelecimento vem do cardápio de gestores do ciclo 3 (única fonte "
                  "arquivada; CNES fora dele fica ausente, contado em `n_fora`); a gestão, do quadro da 1ª chamada.\n\n"
                  + _bloco("db_composicao", tabela_db_comp(est, "1+2+3"))
                  + "\n\nPor ciclo (`*` = IC 95% que exclui zero):\n\n" + _bloco("db_ciclos", tabela_db_ciclos(est))
                  + "\n\n**(ii) Q3 com e sem a composição** e **(iii) Q2 sem as células só de CR.** Mesma amostra nas "
                    "três linhas de Q3 (células com tipo e gestão definidos). O indicador de célula só de CR é o "
                    "complemento do tipo de vaga, que Q3 já fixa.\n\n" + _bloco("db_q3", tabela_db_q3(est))
                  + "\n\n" + _bloco("db_q3_leitura", leitura_db_ii(est)))
    partes.append("## 5. D-c — funil\n\n"
                  "Q3 se decompõe em ter candidato de 1ª opção e ser preenchida dado esse candidato (e, sem ele, por "
                  "candidatos de 2ª opção). Os saltos condicionais comparam subamostras escolhidas depois do anúncio: "
                  "são descritivos.\n\n" + _bloco("dc_funil", tabela_dc(est))
                  + "\n\nDecomposição aproximada nos limites de cada lado (sem efeitos fixos, porque efeitos fixos não "
                    "dão nível; as quatro regressões usam amostras diferentes, daí o resíduo). Regra do script, não do "
                    "protocolo (que diz só \"a queda se concentra numa das partes\"): concentra se a maior contribuição, "
                    "em módulo, for ao menos 2/3 da soma dos módulos. O histórico do Git não mostra quando ela foi "
                    "fixada. Em 0,300 a maior parte leva "
                    + _num(100 * max(abs(v) for v in lt["D-c"]["contribuicoes"].values())
                           / sum(abs(v) for v in lt["D-c"]["contribuicoes"].values()), 0, False)
                    + "% da soma dos módulos; qualquer limiar acima disso dá a mesma leitura (nota da auditoria 33)."
                      "\n\n" + _bloco("dc_decomposicao", tabela_dc_decomp(est))
                  + "\n\n**Motivo de não alocação.** Entre as células com candidato de 1ª opção e não preenchidas, o "
                    "motivo onde a base distingue (ordem: sem vaga imediata; alocação desconsiderada pela gestão, só "
                    "ciclo 1; candidato alocado em outra célula; todos os candidatos inelegíveis, só ciclo 1; outro). "
                    "Os saltos somam exatamente o salto de P(preenchida | candidato) com o sinal trocado.\n\n"
                  + _bloco("dc_motivos", tabela_dc_motivos(est))
                  + "\n\n" + _bloco("dc_ausencias", "O que a base **não** distingue (registrado, nada suposto):\n\n"
                                    + "\n".join(f"- **{k.replace('_', ' ')}:** {v}" for k, v in
                                                info["motivos"]["o_que_a_base_nao_distingue"].items())
                                    + f"\n- células em que a contagem de 1ª opção das escolhas difere do quadro: "
                                      f"{info['motivos']['celulas_em_que_a_contagem_de_1a_opcao_das_escolhas_difere_do_quadro']}."))
    partes.append("## 6. D-d — concorrência\n\n"
                  "Para cada célula: células do mesmo curso e ciclo na mesma região de saúde (CIR) e na mesma UF, "
                  "quantas delas têm bolsa igual ou maior, e a bolsa média delas (exposições do script 32, protocolo "
                  "58). Célula sem concorrente tem bolsa média ausente (contada), nunca zero.\n\n"
                  + _bloco("dd_medidas", tabela_medidas(est, "D-d", "medidas")))
    partes.append("## 7. D-e — médicos por perto\n\n"
                  "Balanço pré-determinado: vínculos CNES pré (202406–202506) das CBO do curso na região de saúde por "
                  "10 mil hab. (lógica do P5); distância do município da célula à origem mais próxima entre os "
                  "candidatos do mesmo curso e ciclo (G1, regra principal; o conjunto de candidatos se forma depois do "
                  "anúncio); nível REGIC.\n\n" + _bloco("de_balanco", tabela_medidas(est, "D-e", "balanco"))
                  + "\n\n" + _bloco("de_origem", "A origem dos candidatos vem do G1 já gravado, que a mediu no CNES da "
                                    "competência de referência de cada ciclo ("
                                    + ", ".join(f"ciclo {k}: {v}" for k, v in sorted(
                                        json.loads(G1_RESUMO.read_text(encoding="utf-8"))["competencia_referencia"]
                                        .items()))
                                    + "), não na janela pré 202406–202506 das outras medidas; nenhuma é posterior a "
                                      "202609. Esta nota é da auditoria 33."))
    partes.append("## 8. D-f — ciclo 2 e cadastro reserva\n\n" + _bloco("df_tabela", tabela_df(est))
                  + "\n\n" + AVISO_SELECAO_DF
                  + "\n\n" + _bloco("df_edital",
                                    "**A regra do ciclo 2 sobre o cadastro reserva na 1ª chamada.** "
                                    f"O texto do Edital nº 3/2026 não está arquivado em `data/raw/`: a cópia "
                                    f"(`{rc2['pagina_do_chamamento']['arquivo']}`) é só a página do Chamamento SGTES/MS "
                                    "nº 1/2026, que lista o edital como anexo "
                                    f"({'sim' if rc2['pagina_do_chamamento']['lista_o_edital_3_2026_como_anexo'] else 'não'}) "
                                    f"e tem {rc2['pagina_do_chamamento']['ocorrencias_de_cadastro_reserva_ou_remanejamento']} "
                                    "menções a cadastro reserva ou remanejamento; nenhum outro arquivo de `data/raw/` é o "
                                    "texto do edital"
                                    + (f" (achados pelo nome: {', '.join(rc2['texto_do_edital_3_2026_arquivado'])})"
                                       if rc2["texto_do_edital_3_2026_arquivado"] else "")
                                    + ". Não há item do edital a citar. A regra arquivada mais próxima é a observação do "
                                    "quadro de vagas original do ciclo 2"
                                    + (f" (`{nota['arquivo']}`, aba `{nota['aba']}`, linha {nota['linha']}): "
                                       f"“{nota['texto']}”" if nota else ": não encontrada")
                                    + ". Ela diz que o cadastro reserva não tem vaga imediata e só recebe vaga “em "
                                    "chamadas futuras”. No quadro de 19/03/2026, usado no pipeline, nenhuma célula só de "
                                    "CR do ciclo 2 tem alocado na 1ª chamada (doc 49, §2). " + NOTA_A36_DF
                                    + " Nos ciclos 1 e 3, os editais preveem "
                                    "remanejamento para o cadastro reserva (doc 49, §2, itens 4.1.3.4 e 5.7)."))
    partes.append("## 9. D-g — outras políticas em 0,300\n\n"
                  "Sem teste causal possível. Placebo de balanço com dados pré (202406–202506) e a lista da auditoria "
                  "18.\n\n" + _bloco("dg_balanco", tabela_medidas(est, "D-g", "balanco"))
                  + "\n\n" + _bloco("dg_regras", _tab(["Regra (auditoria 18)", "Seção", "Muda em 0,300", "Muda em 0,400",
                                                       "Fronteira"],
                                                      [[r["regra"], r["secao"], r["em_0300"], r["em_0400"], r["fronteira"]]
                                                       for r in REGRAS_AUDITORIA_18])))
    partes.append("## 10. Quanto da queda cada explicação leva\n\n"
                  "Cada linha traz o salto de Q1, Q2 e Q3 depois de fixar o fator, ao lado do salto com que se compara. "
                  "Fator que entra como covariável ou efeito fixo: comparado com o original **na mesma amostra**; fator "
                  "que retira células: comparado com o original. \"Reduz pela metade\" = |salto fixado| ≤ 0,5 × "
                  "|salto comparado|; aplicado só em 0,300 (em 0,400 o original é quase zero e a razão não informa). "
                  "Igualar fatores escolhidos ou formados depois do anúncio é descritivo.\n\n"
                  + _bloco("tabela_resumo", tabela_resumo(est)))
    candid = lt["descritivas_que_reduzem_metade"]
    pelo_fixar = {k.split(" ")[0] for k in lt["fixar_reduz_metade_em_0300"]}
    candid_txt = [e if e in pelo_fixar else f"{e} (só pelo critério do ciclo 2; na §10 não reduz)" for e in candid]
    partes.append("## 11. Leitura pré-registrada (§3)\n\n" + _bloco("leitura", _tab(
        ["Situação do §3", "Ocorre?", "Leitura"],
        [["D-a apoia", "sim (por construção: 3 placebos)" if da["apoia"] else "não",
          "acaso mais poucos municípios; as outras viram descrição"],
         ["uma ou mais de D-b a D-f reduzem o salto pela metade ou mais",
          ("sim: " + ", ".join(candid_txt)) if candid else "não","explicações candidatas, ditas como descritivas"],
         ["nada reduz o salto e D-a não apoia", "não" if (candid or da["apoia"]) else "sim",
          "não há explicação nos dados disponíveis"]])
        + f"\n\nLeitura aplicada: **{lt['leitura_principal']}**. "
        + ("Como o teste de acaso não podia reprovar, a leitura vale como \"acaso não descartado\"; as explicações que "
           "reduzem a queda pela metade ficam como descrição." if lt["leitura_principal"] == "ACASO_MAIS_POUCOS_MUNICIPIOS"
           else "")
        + f" D-c: a maior parte é \"{lt['D-c']['maior']}\"; concentra pela regra de 2/3: "
          f"{'sim' if lt['D-c']['concentra'] else 'não'}. D-f: o salto do ciclo 2 sem as células só de CR "
          f"{'cai pela metade ou mais' if lt['D-f']['apoia'] else 'não cai pela metade'}, linha que, no quadro de "
          "19/03/2026, condiciona no resultado (§8)."))
    figtxt = []
    for f in figs:
        nome = Path(f["arquivo"]).name
        figtxt.append(f"![{nome}](../../{f['arquivo']})\n\n**Como ler:** {f['como_ler']}\n\n*Detalhe técnico:* "
                      f"{f['detalhe_tecnico']}")
    partes.append("## 12. Figuras\n\n" + _bloco("figuras", "\n\n".join(figtxt)))
    partes.append("## 13. Limites\n\n" + _bloco("limites", "\n".join([
        "- **Descritivo e pós-resultado.** As quedas já eram conhecidas (docs 49 e 49b) quando a lista foi fixada. "
        "Nenhuma linha é primária; o BKY corre entre as linhas de salto de cada explicação (coluna `q_bky`).",
        "- **Pacote do corte.** O salto mede tudo o que muda em 0,300, não o degrau de R$ 5 mil isolado. A queda não "
        "pode ser atribuída à bolsa.",
        "- **Fatores pós-anúncio.** Composição das vagas, candidatos de 1ª opção e concorrência se formam depois de a "
        "faixa ser conhecida (exceto a oferta do ciclo 1, protocolo 48, §8). Igualá-los entre os lados mostra o que "
        "acompanha a queda, não o que a causa.",
        "- **Poucos municípios.** São 145 abaixo e 120 acima na janela de 0,300; uma reta por ciclo de cada lado.",
        "- **Acaso.** O teste do protocolo não podia reprovar (3 placebos); a grade complementar está fora do protocolo.",
        "- **Ausências registradas, nada imputado:** tipo do estabelecimento fora do cardápio do ciclo 3; motivo da "
        "não alocação nos ciclos 2 e 3; texto do Edital nº 3/2026; CIR, distância ou vínculos onde a fonte não cobre "
        "(contados em `n_fora`)."])))
    dec = resumo["decisoes"]
    partes.append("## 14. Decisões e desvios\n\n" + _bloco("decisoes", "\n".join(f"- {d}" for d in dec)))
    v = resumo["validacoes"]
    partes.append("## 15. Validações\n\n" + _bloco("validacoes", _tab(["Conferência", "Resultado"], [
        ["Q1–Q3 reproduzem N, NA e ND", f"{v['reproducao']['linhas_alvo']} comparações; max dif {_e(v['reproducao']['max_abs_dif'])}"],
        ["linhas em DQ_estimativas.csv", str(v["linhas"])],
        ["EXECUTADO / SEM_ESTIMATIVA / NAO_EXECUTADO", f"{v['executado']} / {v['sem_estimativa']} / {v['nao_executado']}"],
        ["identidade dos motivos (D-c)", f"max resíduo {_e(v['max_residuo_motivos'])}"],
        ["células por ciclo (Q3)", ", ".join(f"{k}: {n}" for k, n in info["celulas_por_ciclo"].items())],
        ["municípios × ciclo (Q1, Q2)", ", ".join(f"{k}: {n}" for k, n in info["municipios_por_ciclo"].items())],
        ["células sem tipo do estabelecimento", str(info["tipo_estabelecimento"]["celulas_sem_tipo"])],
        ["células sem gestão", str(info["gestao"]["celulas_sem_gestao"])],
        ["células sem distância à origem", str(info["distancia_origem"]["celulas_sem_distancia"])],
        ["células sem vínculos do curso na CIR", str(info["vinculos_regiao"]["celulas_sem_medida"])],
        ["competências CNES lidas", f"{info['cnes_sus']['competencias'][0]}–{info['cnes_sus']['competencias'][-1]}"],
    ]) + "\n\nNada imputado ou simulado; IVS 2010 oficial (a08); o arquivo local de IVS da auditoria 16 não é lido; "
         "`data/` é só lido; nenhum identificador de pessoa em `output/`."))
    return "\n\n".join(partes) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

DECISOES = [
    "Q1, Q2 e Q3 por corte, ciclos 1-3 juntos (intercepto e inclinacoes por ciclo, salto comum, CR1 por municipio), "
    "com as funcoes do ND (23b) e do adendo §7 (24); conferidos contra N_, NA_ e ND_estimativas antes de qualquer teste.",
    "D-a: grade do protocolo = 0,250 a 0,450, passo 0,005, sem |c - corte real| < 0,050 -> 0,250; 0,350; 0,450. "
    "Grade complementar fora do protocolo: mesma grade a mais de 0,010 dos cortes reais, so observacoes do mesmo "
    "segmento de bolsa (como o S-i do protocolo 48).",
    "D-a, Fisher: lado do corte permutado entre municipios (n acima fixo), 999 permutacoes, semente [20261026]; "
    "estatistica = coeficiente do lado de cima (Frisch-Waugh-Lovell) com intercepto por ciclo e os controles de cada Q.",
    "Saltos de composicao, de concorrencia e de balanco na celula: sem efeitos fixos (o efeito fixo de curso absorveria "
    "o indice de curso); saltos das partes do funil e dos motivos: especificacao de Q3.",
    "Indices de composicao (curso, tipo, gestao): preenchimento medio da categoria no ciclo entre as celulas com "
    "|IVS - corte| >= 0,050 nos dois cortes.",
    "Tipo do estabelecimento: cardapio de gestores do ciclo 3 por CNES (unica fonte arquivada); gestao: quadro "
    "OFERTA_VAGAS da 1a chamada do ciclo, por CNES.",
    "Fixar o fator: covariavel (um coeficiente por ciclo, comum aos dois lados, centrada na media do kernel, como o "
    "controle do protocolo 48) ou efeito fixo; razao contra o original na mesma amostra. Fator que retira celulas: razao "
    "contra o original. Reduz pela metade = |fixado| <= 0,5 |comparado|, so em 0,300.",
    "D-c: decomposicao nos limites sem efeitos fixos (interceptos ponderados pelos pesos omega), aproximada; "
    "'concentra' se a maior contribuicao em modulo for >= 2/3 da soma dos modulos (regra do script, nao do protocolo; "
    "o historico nao mostra quando foi fixada, conforme a auditoria 33).",
    "D-f: 'some' operacionalizado como o salto do ciclo 2 sem as celulas so de CR caindo pela metade ou mais (o mesmo "
    "criterio do §3).",
    "BKY entre as linhas tipo_linha = salto de cada explicacao, so do protocolo (a grade complementar fica fora).",
]


def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str, "corte_placebo": str, "semente": str})
    for c in ("nota", "motivo_fora", "covariaveis", "efeitos_fixos", "estimador", "outcome", "descricao", "unidade",
              "reduz_metade", "populacao", "variante", "especificacao", "unidade_analise", "corte_placebo"):
        est[c] = est[c].fillna("")
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, resumo


def atualizar_doc() -> None:
    est, resumo = ler_saidas()
    DOC.write_text(gerar_doc(est, resumo), encoding="utf-8")


def _chaves_tuplas(o):
    if isinstance(o, dict):
        return {("|".join(map(str, k)) if isinstance(k, tuple) else str(k)): _chaves_tuplas(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_chaves_tuplas(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    return o


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava o doc 57l a partir das saidas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    est, extras = estimar_tudo()
    nucleo = ["tau", "ep", "ic95_inf", "ic95_sup", "p_valor"]
    sem_nota = est[(est["tipo_linha"] == "salto") & est[nucleo].isna().any(axis=1) & (est["nota"] == "")
                   & (est["bloco"] != "fisher")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas de salto com NaN sem nota")
    proibidas = {"id_candidato", "cpf", "nome"}
    if proibidas & set(c.lower() for c in est.columns):
        raise FalhaValidacao("coluna de identificador pessoal na saida")
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    est_lido = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "ciclo": str, "corte_placebo": str, "semente": str})
    for c in ("nota", "reduz_metade", "populacao", "variante", "corte_placebo", "explicacao", "rotulo"):
        est_lido[c] = est_lido[c].fillna("")
    figs = gerar_figuras(est_lido, OUT / DIR_FIG)
    ent = [
        E6.bloco_entrada(PROTOCOLO_MD, "protocolo 61 (congelado antes de rodar)", "docs/06_execucao", "2026-10-26",
                         "-", "texto", "-", "-"),
        E6.bloco_entrada(T23.A08, "running variable (IVS 2010 oficial)", "Ipea (a08)", "Censo 2010", "Brasil",
                         "municipio", "co_ibge", "ivs"),
        E6.bloco_entrada(T23.ARQ_VM, "N1, vagas oferecidas, populacao (V1-V3)", "tarefa B (12)", "ciclos 1-3",
                         "municipios do quadro", "municipio x ciclo", "ciclo, co_ibge", "municipios sem IVS fora"),
        E6.bloco_entrada(T23.ARQ_VC, "celulas do quadro (Q3, composicao, funil)", "tarefa B (12)", "ciclos 1-3",
                         "5135 celulas", "celula x ciclo", "ciclo, co_cnes_7d, cod_curso", "celulas sem IVS fora"),
        E6.bloco_entrada(T23.ARQ_U, "U (todos os municipios) e conferencias", "tarefa B (12)", "-", "Brasil",
                         "municipio", "co_ibge", "-"),
        E6.bloco_entrada(N_EST, "alvo da reproducao de Q1 e Q2", "script 23", "2026-10-19", "-", "linha", "-",
                         "N1, V1+V2+V3, S-a e S-e"),
        E6.bloco_entrada(NA_EST, "alvo da reproducao de Q3", "script 24", "2026-10-19", "-", "linha", "-",
                         "A3_PREENCHIDA principal"),
        E6.bloco_entrada(ND_EST, "alvo da reproducao de Q1 e Q2 (ND)", "script 23b", "2026-10-21", "-", "linha", "-",
                         "POR_CORTE, D4 e D1"),
        E6.bloco_entrada(ESCOLHAS, "escolhas dos candidatos (D-c motivos; D-e candidatos do curso)", "tarefa B (12)",
                         "ciclos 1-3", "-", "candidato x opcao", "ciclo, id_candidato", "so agregado, em memoria"),
        E6.bloco_entrada(G1_ORIGEM, "municipio de origem dos candidatos (D-e)", "portao G1", "competencia de referencia "
                         "do ciclo", "-", "candidato", "ciclo, id_candidato", "regra g1_cpf_nome; so agregado"),
        E6.bloco_entrada(QUADRO_CONSOLIDADO, "gestao do estabelecimento (D-b)", "aquisicao (02)", "quadros 1a chamada",
                         "-", "linha do quadro", "ciclo, co_cnes_7d", "OFERTA_VAGAS, chamada 1"),
        E6.bloco_entrada(ARQ_CNES, "CNES pre (D-e, D-g)", "a09", "202406-202506", "Brasil", "municipio x grupo x mes",
                         "co_ibge, competencia, grupo", "so 202406-202506"),
        E6.bloco_entrada(T32.V_CELULA, "exposicoes de concorrencia (via script 32)", "tarefa B (12)", "ciclos 1-3", "-",
                         "celula", "ciclo, co_cnes_7d, cod_curso", "celulas com IVS e CIR"),
        E6.bloco_entrada(T29.CIR_CNV, "regiao de saude (CIR)", "DATASUS/TabNet", "base corrente", "Brasil",
                         "municipio", "co_ibge", "-"),
        E6.bloco_entrada(T29.REGIC_XLSX, "hierarquia urbana (REGIC 2018)", "IBGE", "2018", "Brasil", "municipio",
                         "codmun", "-"),
        E6.bloco_entrada(T29.PONTE, "ponte curso-CBO", "a09/ponte", "-", "cursos PMM-E", "curso", "cod_curso", "-"),
        E6.bloco_entrada(EDITAL_C2_PAGINA, "pagina do chamamento do ciclo 2 (D-f)", "MS", "2026", "-", "texto", "-",
                         "so leitura"),
        E6.bloco_entrada(QUADRO_C2_ORIGINAL, "quadro original do ciclo 2: observacao sobre o CR (D-f)", "MS", "2026",
                         "-", "planilha", "-", "so a celula da observacao"),
        E6.bloco_entrada(RESULTADO_C2, "resultado do ciclo 2: cabecalho da aba Desclassificados (D-c)", "MS", "2026",
                         "-", "planilha", "-", "so o cabecalho"),
        E6.bloco_entrada(AUDITORIA_18, "regras nos mesmos cortes (D-g)", "auditoria 18", "2026-10-18", "-", "texto",
                         "-", "-"),
    ]
    mot = est[(est["bloco"] == "motivos") & (est["tipo_linha"] == "identidade")]
    resumo = {
        "etapa": "DQ_diagnostico_queda_0300",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "protocolo": {"texto": rotulo(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD)},
        "contraste": CONTRASTE,
        "salto": "tau = lado com bolsa maior (s > c) menos lado com bolsa menor; o corte pertence ao lado inferior",
        "nao_muda": "nada aqui vira especificacao principal nem muda o Holm ou a leitura dos protocolos 40 e 48",
        "quantidades": DESC_Q,
        "explicacoes": EXPLICACOES,
        "parametros": {"h_mil": H, "placebos_protocolo_mil": list(PLACEBOS),
                       "placebos_complementares_mil": list(PLACEBOS_COMPLEMENTARES), "janelas_fisher_mil":
                       list(JANELAS_FISHER), "n_permutacoes": N_PERM, "semente": SEMENTE, "limiar_metade": LIMIAR_METADE,
                       "cnes_pre": list(COMP_PRE)},
        "leitura": extras["leitura"],
        "decomposicao_funil": extras["decomposicao_funil"],
        "regra_ciclo2": extras["regra_ciclo2"],
        "regras_auditoria_18": REGRAS_AUDITORIA_18,
        "info_dados": extras["info_dados"],
        "decisoes": DECISOES,
        "desvios": [{"data": DATA_EXECUCAO, "o_que": "D-a: a grade do protocolo deixa 3 cortes placebo; o menor p por "
                     "posto possivel e 0,25 > 0,10, entao o criterio de apoio e cumprido por construcao. O protocolo nao "
                     "muda: a leitura literal e relatada, e uma grade complementar fora do protocolo (rotulo "
                     f"{ROT_COMPLEMENTAR}) e relatada ao lado, sem entrar na leitura pre-registrada.",
                     "forcado_por": "aritmetica da grade do protocolo"},
                    {"data": DATA_EXECUCAO, "o_que": "D-f: o texto do Edital no 3/2026 (ciclo 2) nao esta arquivado; cita-se "
                     "a observacao do quadro de vagas original do ciclo 2 e registra-se a ausencia",
                     "forcado_por": "dados arquivados"},
                    {"data": DATA_EXECUCAO, "o_que": "D-b: tipo do estabelecimento so existe no cardapio do ciclo 3; celulas "
                     "de CNES fora dele ficam ausentes (contadas) nas linhas que usam o tipo",
                     "forcado_por": "dados arquivados"}],
        "entradas": ent,
        "validacoes": {"reproducao": extras["reproducao"], "linhas": int(len(est)),
                       "executado": int((est["status"] == "EXECUTADO").sum()),
                       "sem_estimativa": int((est["status"] == "SEM_ESTIMATIVA").sum()),
                       "nao_executado": int((est["status"] == "NAO_EXECUTADO").sum()),
                       "max_residuo_motivos": float(mot["valor"].abs().max())},
        "saidas": {NOME_EST: {"arquivo": rotulo(OUT / NOME_EST), "sha256": sha256(OUT / NOME_EST)},
                   "figuras": [dict(f, sha256=sha256(ROOT / f["arquivo"])) for f in figs]},
        "linguagem": "diagnostico descritivo e pos-resultado do pacote do corte; nada aqui diz que a bolsa causa a queda",
    }
    T23._gravar_json(OUT / NOME_RESUMO, _chaves_tuplas(resumo))
    atualizar_doc()
    print(f"DQ: {len(est)} linhas; leitura {extras['leitura']['leitura_principal']}; doc {rotulo(DOC)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
