"""X2 e X3 do protocolo exploratório pós-síntese: permanência dos alocados e dinâmica dos ativos.

Protocolo: `docs/06_execucao/45_protocolo_exploratorio_pos_sintese.md`, §3
(X2 e X3), congelado em 19/10/2026 antes de abrir estes outcomes. Estatuto:
**exploratório e pós-resultado** (`estatuto = EXPLORATORIO_POS_SINTESE` em toda
linha). Nada aqui muda o protocolo 40, os resultados E3–E9 nem o Holm das
primárias. Estimadores: `scripts/rdd_bolsa/rdd_lib.py` (não reimplementados).

Contraste
---------
Salto = lado com bolsa maior (s > c) menos lado com bolsa menor, no IVS 2010
oficial do Ipea (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`) em
milésimos; cortes 300 e 400; T = 1[s > c]; local linear, kernel triangular,
h = 50 milésimos. Em nível, a RDD mede o pacote do corte (bolsa anunciada de
+R$ 5 mil e as outras regras federais nos mesmos cortes; auditoria 18). Não é
efeito da participação no PMM-E nem do Agora Tem Especialistas. O arquivo local
de IVS da auditoria 16 não é lido.

X2 — permanência dos alocados
-----------------------------
1. Alocados da 1ª chamada, só em memória com nome:
   - ciclo 1: "LOCAL DE ATUAÇÃO CONFIRMADO" na alocação retificada sub judice
     e "HOMOLOGADO" na lista de homologados da 1ª chamada; a célula final da
     pessoa é a da homologação, se houver, e senão a da confirmação;
   - ciclo 2: "ALOCADO*" na aba Classificados de
     `resultado-final-pmme-2o-ciclo-25-05.xlsx`.
   Os arquivos de resultado não têm CRM (conferido pelo cabeçalho): a ligação
   usa nome normalizado + curso + município (o município vem do quadro pela
   célula, como na tarefa B).
2. Ligação contra a relação nominal de ativos (zip publicado em 09/10/2026,
   `dt_referencia` 11/09/2026, o mesmo arquivo do E3) e, em descritivo, contra o
   retrato anterior `data/pmm_especialistas_nominal.csv` (12/08/2026). Regra,
   em ordem: (i) chave exata nome+curso+município única dos dois lados →
   LIGADO; chave repetida em algum lado ou o mesmo ativo ligado a mais de um
   alocado → AMBIGUO; (ii) sem chave exata, ativo não ligado na mesma
   combinação curso+município com nome de similaridade >= LIMIAR_GRAFIA, ou
   com o mesmo primeiro nome e ao menos duas partes do nome em comum →
   INCERTO; (iii) senão NAO_LIGADO, com o motivo (nome e curso ativos em outro
   município; nome ativo em outro curso; sem correspondente). AMBIGUO e INCERTO
   ficam fora do outcome (NaN com motivo). Entre os dois retratos, o CRM liga
   as linhas de ativos (concordância relatada).
3. Outcomes: fração dos alocados (determinados) ainda ativos no município de
   alocação, por célula e por município (condicionais a preencher: limites de
   Lee com seleção = ter alocado determinado); célula com alocado ainda ativo
   e alocados ainda ativos por célula oferecida (incondicionais).
4. RDD por ciclo e corte, cortes empilhados por ciclo, ciclos empilhados por
   corte (interceptos por ciclo = EF de ciclo) e tudo empilhado; Lee por ciclo
   e corte (a biblioteca não tem Lee empilhado: linhas NAO_EXECUTADO).

X3 — dinâmica dos ativos
------------------------
`data/pmm_especialistas_serie_historica.csv` (município × curso × mês, dez/25
a ago/26). Só `co_ibge`, o código do curso (número inicial do rótulo; os
rótulos têm mojibake), a competência e `qtd_ativos` são lidos; a coluna `ivs`
do arquivo (rótulos inconsistentes) e a faixa do arquivo não são usadas.
Antes de qualquer outcome, a completude da listagem é conferida contra o
retrato nominal de 12/08/2026: ago/26 tem de reproduzir o retrato por
município × curso, e cada mês tem de conter ao menos os ativos de 12/08 que já
tinham começado antes do 1º dia do mês. Se todos os meses passam, ausência de
linha vira zero em U; se algum falha, cada mês usa só os municípios listados
naquele mês (regra fixada antes de ver outcomes). Outcomes: ativos no mês
(contagem e por 10 mil hab., Censo 2022), queda do pico ao último mês
(contagem, por 10 mil hab. e relativa) e meses listados com ativo. RDD mês a
mês e da queda, em cada corte e empilhada.

Saídas (output/rdd_bolsa/), todas com natureza_dos_dados = EMPIRICO
--------------------------------------------------------------------
X2_pessoas.csv (pseudônimo, sem nome, CPF ou CRM), X2_celulas.csv,
X2_municipios.csv, X2_descritivo.csv, X2_motivos_ligacao.csv,
X2_estimativas.csv, X2_resumo.json; X3_painel_municipio_curso_mes.csv,
X3_painel_municipio_mes.csv, X3_municipio.csv, X3_completude.csv,
X3_descritivo.csv, X3_estimativas.csv, X3_resumo.json.

Uso
---
    python3 scripts/rdd_bolsa/18_permanencia_ativos.py
    python3 scripts/rdd_bolsa/18_permanencia_ativos.py --atualizar-doc

`--atualizar-doc` regrava, a partir das saídas, as tabelas entre marcadores
`<!-- X2:...` e `<!-- X3:...` de
`docs/06_execucao/46_resultados_exploratorios_pos_sintese.md`. Nenhum número
é digitado no doc. As funções puras são importáveis pelo teste
`tests/test_x2_x3_permanencia.py`.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import io
import json
import math
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_x2x3")
B = _importar(DIR_RDD / "12_construir_outcomes_funil.py", "funil_b_x2x3")
sys.dont_write_bytecode = _bytecode

# ---------------------------------------------------------------------------
# Caminhos e parâmetros do protocolo (constantes permitidas: cortes, h, limiares)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
A08 = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
POP22 = ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
ARQ_VC = OUT / "outcomes" / "outcomes_V_celula.parquet"
ARQ_VM = OUT / "outcomes" / "outcomes_V_municipio.parquet"
ARQ_U = OUT / "outcomes" / "outcomes_U_municipio.parquet"
ATIVOS_ZIP = B.ATIVOS_ZIP
NOMINAL_CSV = ROOT / "data" / "pmm_especialistas_nominal.csv"
SERIE_CSV = ROOT / "data" / "pmm_especialistas_serie_historica.csv"
ALOC_C1 = B.CAND_C1
HOMOLOG_C1 = B.RAW_PMME / "2025_ciclo1_chamada1_homologados.xlsx"
RESULT_C2 = B.CAND_C2
DOC46 = ROOT / "docs" / "06_execucao" / "46_resultados_exploratorios_pos_sintese.md"

DATA_EXECUCAO = "2026-10-19"
ESTATUTO = "EXPLORATORIO_POS_SINTESE"
NATUREZA = "EMPIRICO"
CORTES = L.CORTES_MIL          # (300, 400)
H = L.H_PRINCIPAL_MIL          # 50
ROTULO_CORTE = {300: "0.300", 400: "0.400"}
EMPILHADO = "empilhado"
CICLOS_X2 = (1, 2)
LIMIAR_GRAFIA = 0.85           # similaridade (difflib) para INCERTO; fixado antes de ligar
POR_HAB = 10_000
# Variante do pico pedida pela auditoria independente (19/10/2026), depois dos resultados: sem mai/26 e jun/26.
MESES_EXCLUIDOS_AUDITORIA = ("2026-05", "2026-06")
MESES_PT = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9,
            "out": 10, "nov": 11, "dez": 12}
CONTRASTE = ("salto = lado com bolsa maior (s > c) menos lado com bolsa menor; IVS 2010 oficial (a08) em milesimos; "
             "em nivel mede o pacote do corte (bolsa anunciada +R$ 5 mil e outras regras nos mesmos cortes), "
             "nao a participacao no PMM-E")


class FalhaValidacao(RuntimeError):
    """Validação que não passou: o script para antes de gravar (falha fechada)."""


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def sha256(path: Path) -> str:
    return B.sha256_arquivo(path)


def rotulo(path: Path) -> str:
    return Path(path).resolve().relative_to(ROOT).as_posix()


def _nan_none(obj):
    if isinstance(obj, dict):
        return {str(k): _nan_none(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_nan_none(v) for v in obj]
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return None if not math.isfinite(float(obj)) else float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def gravar_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, lineterminator="\n")


def bloco_entrada(path: Path, papel: str, data_ref: str, cobertura: str, unidade: str, chaves: str,
                  filtros: str) -> dict:
    return {"caminho": rotulo(path), "sha256": sha256(path), "bytes": Path(path).stat().st_size, "papel": papel,
            "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade, "chaves": chaves,
            "filtros": filtros}


def s_mil_de_ivs(ivs: pd.Series) -> pd.Series:
    """IVS com três casas -> milésimos inteiros; ausente fica NaN."""
    v = pd.to_numeric(ivs, errors="raise").astype(float)
    mil = v * 1000.0
    ok = v.notna()
    if (np.abs(mil[ok] - np.round(mil[ok])) > 1e-6).any():
        raise FalhaValidacao("IVS com mais de três casas decimais")
    return pd.Series(np.where(ok, np.round(mil), np.nan), index=ivs.index)


def faixa_regra(s_mil: float) -> str:
    """Faixa pela regra sharp (protocolo do escore): <= 300 F3; <= 400 F2; > 400 F1."""
    if not np.isfinite(s_mil):
        return "SEM IVS OFICIAL"
    if s_mil <= 300:
        return "FAIXA 3"
    if s_mil <= 400:
        return "FAIXA 2"
    return "FAIXA 1"


def competencia_iso(rotulo_mes: str) -> str:
    """'dez/25' -> '2025-12'; rótulo fora do padrão falha fechado."""
    m = re.fullmatch(r"\s*([a-z]{3})/(\d{2})\s*", str(rotulo_mes).lower())
    if not m or m.group(1) not in MESES_PT:
        raise FalhaValidacao(f"competência não reconhecida: {rotulo_mes!r}")
    return f"20{m.group(2)}-{MESES_PT[m.group(1)]:02d}"


def ler_a08() -> pd.DataFrame:
    a08 = pd.read_csv(A08, dtype={"co_ibge": str})
    a08["co_ibge"] = a08["co_ibge"].str.replace(r"\D", "", regex=True).str[:6]
    if a08["co_ibge"].duplicated().any() or (a08["co_ibge"].str.len() != 6).any():
        raise FalhaValidacao("a08 com município duplicado ou inválido")
    a08["s_mil"] = s_mil_de_ivs(a08["ivs"])
    if a08["s_mil"].isna().any():
        raise FalhaValidacao("a08 com IVS ausente")
    return a08[["co_ibge", "s_mil"]]


def ler_populacao() -> pd.Series:
    p = pd.read_csv(POP22, dtype={"co_ibge_6d": str})
    if p["co_ibge_6d"].duplicated().any():
        raise FalhaValidacao("população com município duplicado")
    return p.set_index("co_ibge_6d")["populacao_2022"].astype(float)


# ---------------------------------------------------------------------------
# X2: leitura dos alocados (nomes só em memória)
# ---------------------------------------------------------------------------

def _tem_crm(cab: list[str]) -> bool:
    return any(re.search(r"\bCRM\b", c) for c in cab)


def ler_eventos_alocacao() -> tuple[pd.DataFrame, dict]:
    """Eventos de alocação da 1ª chamada dos ciclos 1 e 2: uma linha por pessoa × evento.

    Colunas: ciclo, evento, prioridade (maior = mais tardio no funil), _nome,
    _cpf (máscara publicada, só para detectar homônimos no mesmo arquivo),
    co_cnes_7d, cod_curso, co_ibge_arquivo. Nada disso com nome é gravado.
    """
    specs = [
        (1, "confirmacao", 1, ALOC_C1, 0, "ALOCACAO", lambda s: s.startswith("LOCAL DE ATUACAO CONFIRMADO")),
        (1, "homologacao", 2, HOMOLOG_C1, 0, "RESULTADO", lambda s: s == "HOMOLOGADO"),
        (2, "alocacao", 1, RESULT_C2, "Classificados", "SITUACAO", lambda s: s.startswith("ALOCADO")),
    ]
    regs, diag = [], {}
    for ciclo, evento, prio, caminho, aba, col_status, filtro in specs:
        cab, _, linhas = B.ler_aba(caminho, aba)
        i_cnes, i_curso = B.coluna(cab, "CNES"), B.coluna(cab, "CURSO")
        i_nome = B.coluna(cab, "NOME CANDIDATO A", "NOME")
        i_cpf = B.coluna(cab, "CPF", "CPF MASC", prefixo=True)
        i_st = B.coluna(cab, col_status)
        try:
            i_ibge = B.coluna(cab, "IBGE")
        except KeyError:
            i_ibge = None
        status = Counter()
        n_sel, sem_chave = 0, 0
        for r in linhas:
            st = B.texto_norm(B.valor(r, i_st))
            status[st] += 1
            if not filtro(st):
                continue
            cnes, curso = B.chave_cnes(B.valor(r, i_cnes)), B.chave_curso(B.valor(r, i_curso))
            if cnes is None or curso is None:
                sem_chave += 1
                continue
            n_sel += 1
            regs.append({"ciclo": ciclo, "evento": evento, "prioridade": prio,
                         "_nome": B.texto_norm(B.valor(r, i_nome)), "_cpf": str(B.valor(r, i_cpf) or "").strip(),
                         "co_cnes_7d": cnes, "cod_curso": curso,
                         "co_ibge_arquivo": B.chave_ibge(B.valor(r, i_ibge)) if i_ibge is not None else None})
        if sem_chave:
            raise FalhaValidacao(f"{rotulo(caminho)}: {sem_chave} linhas selecionadas sem célula válida")
        diag[f"c{ciclo}_{evento}"] = {"arquivo": rotulo(caminho), "aba": aba, "coluna_status": col_status,
                                      "linhas_selecionadas": n_sel, "situacoes_publicadas": dict(status),
                                      "arquivo_tem_coluna_crm": _tem_crm(cab)}
    ev = pd.DataFrame(regs)
    if (ev["_nome"] == "").any():
        raise FalhaValidacao("evento de alocação sem nome")
    return ev, diag


def consolidar_pessoas(ev: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Uma linha por pessoa alocada (ciclo × nome normalizado) com a célula final.

    Célula final = a do evento de maior prioridade (homologação > confirmação
    no ciclo 1). Pessoa fica AMBIGUA na alocação se, no mesmo arquivo, o nome
    normalizado aparece com máscaras de CPF diferentes (homônimos) ou se o
    evento final tem mais de uma célula.
    """
    linhas, trilha = [], Counter()
    for (ciclo, nome), g in ev.groupby(["ciclo", "_nome"], sort=True):
        homonimo = bool((g.groupby("evento")["_cpf"].nunique() > 1).any())
        top = g[g["prioridade"] == g["prioridade"].max()]
        celulas = top[["co_cnes_7d", "cod_curso"]].drop_duplicates()
        amb, motivo = False, ""
        if homonimo:
            amb, motivo = True, "homonimos no mesmo arquivo de resultado (mascaras de CPF diferentes)"
        elif len(celulas) > 1:
            amb, motivo = True, "mais de uma celula no evento final"
        r0 = top.iloc[0]
        eventos = sorted(g["evento"].unique())
        if ciclo == 1:
            conf = g[g["evento"] == "confirmacao"][["co_cnes_7d", "cod_curso"]].drop_duplicates()
            if "homologacao" in eventos and len(conf):
                mesma = ((conf["co_cnes_7d"] == r0["co_cnes_7d"]) & (conf["cod_curso"] == r0["cod_curso"])).any()
                trilha["homologado_na_celula_da_confirmacao" if mesma else "homologado_em_outra_celula"] += 1
            elif "homologacao" in eventos:
                trilha["homologado_sem_confirmacao"] += 1
            else:
                trilha["confirmado_sem_homologacao"] += 1
        linhas.append({"ciclo": int(ciclo), "_nome": nome, "_chave_pessoa": hashlib.sha256(
                           f"{ciclo}|{nome}|{'|'.join(sorted(g['_cpf'].unique()))}".encode("utf-8")).hexdigest(),
                       "co_cnes_7d": r0["co_cnes_7d"], "cod_curso": int(r0["cod_curso"]),
                       "co_ibge_arquivo": r0["co_ibge_arquivo"], "evento_final": r0["evento"],
                       "eventos": ";".join(eventos), "ambiguo_alocacao": amb, "motivo_alocacao": motivo})
    p = pd.DataFrame(linhas)
    # Pseudônimo determinístico: ordem do hash (não reversível a partir da saída).
    p = p.sort_values(["ciclo", "_chave_pessoa"]).reset_index(drop=True)
    p["id_pessoa"] = [f"x2_c{k}_{i + 1:04d}" for k, i in zip(p["ciclo"], p.groupby("ciclo").cumcount())]
    return p, {"trilha_ciclo1": dict(trilha), "pessoas_por_ciclo": p.groupby("ciclo").size().to_dict(),
               "ambiguos_na_alocacao": int(p["ambiguo_alocacao"].sum())}


def municipio_pela_celula(p: pd.DataFrame, cel: pd.DataFrame) -> pd.DataFrame:
    """Município do quadro pela célula do ciclo; fora do quadro, o IBGE impresso no arquivo (marcado)."""
    q = cel[["ciclo", "co_cnes_7d", "cod_curso", "co_ibge"]]
    out = p.merge(q, on=["ciclo", "co_cnes_7d", "cod_curso"], how="left", validate="many_to_one")
    out["celula_no_quadro"] = out["co_ibge"].notna()
    out["co_ibge"] = out["co_ibge"].where(out["celula_no_quadro"], out["co_ibge_arquivo"])
    return out


def ler_ativos_nominais() -> dict[str, pd.DataFrame]:
    """Os dois retratos de ativos, com nome e CRM só em memória."""
    with zipfile.ZipFile(ATIVOS_ZIP) as z:
        nomes = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(nomes) != 1:
            raise FalhaValidacao("zip de ativos sem CSV único")
        bruto = z.read(nomes[0])
    a = pd.read_csv(io.BytesIO(bruto), sep=";", dtype=str, encoding="latin1",
                    usecols=["co_ibge", "co_cnes", "curso", "ciclo", "nome", "crm", "dt_referencia",
                             "dt_inicio_atividade"])
    n = pd.read_csv(NOMINAL_CSV, dtype=str,
                    usecols=["co_ibge", "co_cnes", "curso", "ciclo", "nome", "crm", "dt_referencia",
                             "dt_inicio_atividade"])
    out = {}
    for nome, df in (("set", a), ("ago", n)):
        d = pd.DataFrame({
            "_nome": df["nome"].map(B.texto_norm), "_crm": df["crm"].fillna("").str.strip(),
            "co_ibge": df["co_ibge"].astype(str).str.split(".").str[0].str.replace(r"\D", "", regex=True).str[:6],
            "co_cnes_7d": df["co_cnes"].map(B.chave_cnes), "cod_curso": df["curso"].map(B.chave_curso),
            "ciclo_k": pd.to_numeric(df["ciclo"].str.strip(), errors="coerce"),
            "dt_referencia": df["dt_referencia"],
        })
        fmt = "%d/%m/%Y" if nome == "set" else "%Y-%m-%d"
        d["dt_inicio"] = pd.to_datetime(df["dt_inicio_atividade"], format=fmt, errors="raise")
        d["dt_ref"] = pd.to_datetime(df["dt_referencia"], format=fmt, errors="raise")
        if d[["cod_curso", "ciclo_k"]].isna().any().any() or (d["co_ibge"].str.len() != 6).any() or (
                d["_nome"] == "").any():
            raise FalhaValidacao(f"retrato {nome}: curso, ciclo, IBGE ou nome inválido")
        d["cod_curso"] = d["cod_curso"].astype(int)
        d["ciclo_k"] = d["ciclo_k"].astype(int)
        out[nome] = d.reset_index(drop=True)
    return out


# ---------------------------------------------------------------------------
# X2: ligação (função pura)
# ---------------------------------------------------------------------------

def similaridade(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def nome_proximo(a: str, b: str, limiar: float = LIMIAR_GRAFIA, partes: bool = True) -> bool:
    """Grafia próxima: similaridade >= limiar, ou (regra ampla) mesmo 1º nome e ao menos 2 partes em comum."""
    if similaridade(a, b) >= limiar:
        return True
    if not partes:
        return False
    ta, tb = a.split(), b.split()
    return bool(ta and tb and ta[0] == tb[0] and len(set(ta) & set(tb)) >= 2)


def ligar(pessoas: pd.DataFrame, ativos: pd.DataFrame, limiar: float = LIMIAR_GRAFIA,
          partes: bool = True) -> pd.DataFrame:
    """Liga alocados a uma lista de ativos por nome normalizado + curso + município.

    Entradas: `pessoas` com _nome, cod_curso, co_ibge, co_cnes_7d, ciclo,
    ambiguo_alocacao, motivo_alocacao; `ativos` com _nome, cod_curso, co_ibge,
    co_cnes_7d, ciclo_k (índice = posição). Saída: as pessoas com status
    (LIGADO, AMBIGUO, INCERTO, NAO_LIGADO), motivo, índice do ativo ligado,
    `ativo` (1/0/NaN), `ativo_no_programa` (1/0/NaN: nome e curso em outro
    município ou nome em outro curso contam como presentes), `cnes_igual` e
    `ciclo_igual` para os ligados. `partes=False` é a regra estreita (só
    similaridade), a da primeira execução, relatada ao lado da ampla.
    """
    p = pessoas.copy().reset_index(drop=True)
    a = ativos.reset_index(drop=True)
    chave = lambda n, c, m: (n, int(c), m)  # noqa: E731
    idx_chave, idx_nome_curso, idx_nome, idx_cel = (defaultdict(list) for _ in range(4))
    for i, r in a.iterrows():
        idx_chave[chave(r["_nome"], r["cod_curso"], r["co_ibge"])].append(i)
        idx_nome_curso[(r["_nome"], int(r["cod_curso"]))].append(i)
        idx_nome[r["_nome"]].append(i)
        idx_cel[(int(r["cod_curso"]), r["co_ibge"])].append(i)
    chaves_p = [chave(n, c, m) for n, c, m in zip(p["_nome"], p["cod_curso"], p["co_ibge"])]
    cont_p = Counter(k for k, amb in zip(chaves_p, p["ambiguo_alocacao"]) if not amb)
    status, motivo, idx = [""] * len(p), [""] * len(p), [None] * len(p)
    for j, (k, amb) in enumerate(zip(chaves_p, p["ambiguo_alocacao"])):
        if amb:
            status[j], motivo[j] = "AMBIGUO", f"alocacao: {p.at[j, 'motivo_alocacao']}"
        elif k[2] is None or (isinstance(k[2], float) and np.isnan(k[2])):
            status[j], motivo[j] = "AMBIGUO", "municipio de alocacao desconhecido"
        elif cont_p[k] > 1:
            status[j], motivo[j] = "AMBIGUO", "chave nome+curso+municipio repetida entre alocados"
        elif len(idx_chave[k]) > 1:
            status[j], motivo[j] = "AMBIGUO", "chave nome+curso+municipio repetida na lista de ativos"
        elif len(idx_chave[k]) == 1:
            status[j], motivo[j], idx[j] = "LIGADO", "nome+curso+municipio exato e unico", idx_chave[k][0]
    usados = Counter(i for i in idx if i is not None)
    for j, i in enumerate(idx):
        if i is not None and usados[i] > 1:
            status[j], motivo[j], idx[j] = "AMBIGUO", "mesmo ativo ligado a mais de um alocado", None
    ligados_exatos = {i for i in idx if i is not None}
    no_programa = [np.nan] * len(p)
    for j, k in enumerate(chaves_p):
        if status[j]:
            continue
        nome, curso, mun = k
        proximos = [i for i in idx_cel[(curso, mun)] if i not in ligados_exatos
                    and nome_proximo(nome, a.at[i, "_nome"], limiar, partes)]
        if proximos:
            status[j], motivo[j] = "INCERTO", (f"grafia proxima (similaridade >= {limiar}"
                                               + (" ou mesmo 1o nome e 2 partes em comum" if partes else "")
                                               + ") no mesmo curso e municipio")
        elif idx_nome_curso[(nome, curso)]:
            status[j], motivo[j], no_programa[j] = "NAO_LIGADO", "nome e curso ativos em outro municipio", 1.0
        elif idx_nome[nome]:
            status[j], motivo[j], no_programa[j] = "NAO_LIGADO", "nome ativo em outro curso", 1.0
        else:
            status[j], motivo[j], no_programa[j] = "NAO_LIGADO", "sem correspondente na lista de ativos", 0.0
    p["status_ligacao"], p["motivo_ligacao"], p["_idx_ativo"] = status, motivo, idx
    p["ativo"] = np.select([p["status_ligacao"] == "LIGADO", p["status_ligacao"] == "NAO_LIGADO"], [1.0, 0.0],
                           default=np.nan)
    p["ativo_no_programa"] = np.where(p["status_ligacao"] == "LIGADO", 1.0, no_programa)
    lig = p["_idx_ativo"].notna()
    p["cnes_igual"] = np.nan
    p["ciclo_igual"] = np.nan
    if lig.any():
        ia = p.loc[lig, "_idx_ativo"].astype(int).to_numpy()
        p.loc[lig, "cnes_igual"] = (a.loc[ia, "co_cnes_7d"].to_numpy() == p.loc[lig, "co_cnes_7d"].to_numpy()) * 1.0
        p.loc[lig, "ciclo_igual"] = (a.loc[ia, "ciclo_k"].to_numpy() == p.loc[lig, "ciclo"].to_numpy()) * 1.0
    return p


def concordancia_crm(lig_set: pd.DataFrame, lig_ago: pd.DataFrame, at: dict[str, pd.DataFrame]) -> dict:
    """Entre os retratos: CRM das linhas ligadas e destino de quem estava ativo em 12/08 e não liga em set."""
    a, n = at["set"], at["ago"]
    m = lig_set[["id_pessoa", "_idx_ativo", "status_ligacao"]].merge(
        lig_ago[["id_pessoa", "_idx_ativo", "status_ligacao"]], on="id_pessoa", suffixes=("_set", "_ago"))
    ambos = m[(m["status_ligacao_set"] == "LIGADO") & (m["status_ligacao_ago"] == "LIGADO")]
    crm_set = a.loc[ambos["_idx_ativo_set"].astype(int), "_crm"].to_numpy()
    crm_ago = n.loc[ambos["_idx_ativo_ago"].astype(int), "_crm"].to_numpy()
    so_ago = m[(m["status_ligacao_ago"] == "LIGADO") & (m["status_ligacao_set"] == "NAO_LIGADO")]
    crms_set = set(a["_crm"]) - {""}
    crm_so_ago = n.loc[so_ago["_idx_ativo_ago"].astype(int), "_crm"]
    return {
        "ligados_nos_dois_retratos": int(len(ambos)),
        "ligados_nos_dois_com_mesmo_crm": int(np.sum((crm_set == crm_ago) & (crm_set != ""))),
        "ligados_em_ago_e_nao_ligados_em_set": int(len(so_ago)),
        "desses_crm_presente_no_retrato_de_set": int(crm_so_ago.isin(crms_set).sum()),
        "desses_crm_ausente_do_retrato_de_set": int((~crm_so_ago.isin(crms_set)).sum()),
        "nota": "CRM sem UF do conselho (a lista de ativos nao traz a UF do CRM): presenca do CRM e indicio, "
                "nao prova, de que a pessoa segue ativa em outro municipio ou curso",
    }


# ---------------------------------------------------------------------------
# X2: agregação (funções puras)
# ---------------------------------------------------------------------------

def agregar_celulas(pessoas: pd.DataFrame, cel: pd.DataFrame) -> pd.DataFrame:
    """Outcomes por célula do quadro da 1ª chamada (ciclo × CNES × curso)."""
    chave = ["ciclo", "co_cnes_7d", "cod_curso"]
    pp = pessoas[pessoas["celula_no_quadro"]]
    g = pp.groupby(chave)
    agg = pd.DataFrame({
        "n_alocados": g.size(),
        "n_determinados": g["ativo"].count(),
        "n_ativos": g["ativo"].sum(min_count=1),
        "n_excluidos": g["ativo"].apply(lambda s: int(s.isna().sum())),
    })
    out = cel[chave + ["co_ibge", "s_mil", "faixa_anunciada"]].merge(agg.reset_index(), on=chave, how="left",
                                                                     validate="one_to_one")
    for c in ("n_alocados", "n_determinados", "n_ativos", "n_excluidos"):
        out[c] = out[c].fillna(0).astype(int)
    out["selecionada"] = (out["n_determinados"] > 0).astype(int)
    out["x2_frac_ativos_celula"] = np.where(out["n_determinados"] > 0,
                                            out["n_ativos"] / out["n_determinados"].where(out["n_determinados"] > 0),
                                            np.nan)
    out["x2_celula_com_alocado_ativo"] = np.where(
        out["n_ativos"] > 0, 1.0, np.where(out["n_excluidos"] > 0, np.nan, 0.0))
    out["so_excluidos"] = ((out["n_alocados"] > 0) & (out["n_determinados"] == 0)).astype(int)
    motivos = []
    for r in out.itertuples(index=False):
        m = {}
        if r.n_determinados == 0:
            m["x2_frac_ativos_celula"] = ("celula sem alocado" if r.n_alocados == 0
                                          else "so alocados ambiguos ou incertos (fora da ligacao)")
        if r.n_ativos == 0 and r.n_excluidos > 0:
            m["x2_celula_com_alocado_ativo"] = "sem ativo ligado e com alocado ambiguo ou incerto"
        motivos.append(json.dumps(m, ensure_ascii=False, sort_keys=True))
    out["motivos_ausencia"] = motivos
    return out


def agregar_municipios(celulas: pd.DataFrame) -> pd.DataFrame:
    """Outcomes por município × ciclo a partir das células do quadro."""
    g = celulas.groupby(["ciclo", "co_ibge"])
    out = pd.DataFrame({
        "s_mil": g["s_mil"].first(), "n_celulas": g.size(), "n_alocados": g["n_alocados"].sum(),
        "n_determinados": g["n_determinados"].sum(), "n_ativos": g["n_ativos"].sum(),
        "n_excluidos": g["n_excluidos"].sum(),
    }).reset_index()
    if (g["s_mil"].nunique(dropna=False) > 1).any():
        raise FalhaValidacao("IVS varia dentro do município")
    out["selecionado"] = (out["n_determinados"] > 0).astype(int)
    out["so_excluidos"] = ((out["n_alocados"] > 0) & (out["n_determinados"] == 0)).astype(int)
    out["x2_frac_ativos_municipio"] = np.where(
        out["n_determinados"] > 0, out["n_ativos"] / out["n_determinados"].where(out["n_determinados"] > 0), np.nan)
    out["x2_alocados_ativos_por_celula"] = np.where(out["n_excluidos"] > 0, np.nan,
                                                    out["n_ativos"] / out["n_celulas"])
    motivos = []
    for r in out.itertuples(index=False):
        m = {}
        if r.n_determinados == 0:
            m["x2_frac_ativos_municipio"] = ("municipio sem alocado" if r.n_alocados == 0
                                             else "so alocados ambiguos ou incertos")
        if r.n_excluidos > 0:
            m["x2_alocados_ativos_por_celula"] = "municipio com alocado ambiguo ou incerto"
        motivos.append(json.dumps(m, ensure_ascii=False, sort_keys=True))
    out["motivos_ausencia"] = motivos
    return out


# ---------------------------------------------------------------------------
# X3: série histórica (funções puras)
# ---------------------------------------------------------------------------

def ler_serie(caminho: Path = SERIE_CSV) -> tuple[pd.DataFrame, dict]:
    """Série município × curso × mês: soma `qtd_ativos` das linhas do mesmo município, curso e mês.

    O arquivo tem mais de uma linha por município × curso × mês (rótulos de
    curso com e sem mojibake; linhas por estabelecimento com `co_cnes` vazio).
    """
    s = pd.read_csv(caminho, dtype=str, usecols=["co_cnes", "curso", "co_ibge", "competencia", "qtd_ativos"])
    diag = {"linhas": int(len(s)), "co_cnes_preenchido": int(s["co_cnes"].notna().sum()),
            "rotulos_de_curso": int(s["curso"].nunique())}
    s["cod_curso"] = s["curso"].map(B.chave_curso)
    s["co_ibge"] = s["co_ibge"].str.replace(r"\D", "", regex=True)
    if s["cod_curso"].isna().any() or (s["co_ibge"].str.len() != 6).any():
        raise FalhaValidacao("série: curso ou IBGE inválido")
    s["mes"] = s["competencia"].map(competencia_iso)
    s["qtd_ativos"] = pd.to_numeric(s["qtd_ativos"], errors="raise")
    if (s["qtd_ativos"] < 0).any() or s["qtd_ativos"].isna().any():
        raise FalhaValidacao("série: qtd_ativos negativa ou ausente")
    diag["codigos_de_curso"] = int(s["cod_curso"].nunique())
    diag["linhas_alem_da_primeira_por_municipio_curso_mes"] = int(s.duplicated(["co_ibge", "cod_curso", "mes"]).sum())
    diag["linhas_com_qtd_zero_por_mes"] = s[s["qtd_ativos"] == 0].groupby("mes").size().to_dict()
    painel = s.groupby(["co_ibge", "cod_curso", "mes"], as_index=False)["qtd_ativos"].sum()
    painel = painel.rename(columns={"qtd_ativos": "ativos"})
    painel["cod_curso"] = painel["cod_curso"].astype(int)
    diag["meses"] = sorted(painel["mes"].unique().tolist())
    return painel, diag


def verificar_completude(painel: pd.DataFrame, nominal: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Confere se cada mês da série lista todos os ativos que o retrato nominal implica.

    (i) O último mês tem de reproduzir o retrato nominal por município × curso.
    (ii) Em cada mês m, a série tem de ter, em cada município × curso, ao menos
    os ativos do retrato que começaram antes do 1º dia de m (cota inferior:
    quem saiu antes do retrato não está nele). Violação = célula com menos.
    """
    meses = sorted(painel["mes"].unique())
    ultimo = meses[-1]
    nom = nominal.assign(cod_curso=nominal["cod_curso"].astype(int))
    linhas = []
    for m in meses:
        inicio = pd.Timestamp(f"{m}-01")
        cota = nom[nom["dt_inicio"] < inicio].groupby(["co_ibge", "cod_curso"]).size().rename("cota")
        serie = painel[painel["mes"] == m].set_index(["co_ibge", "cod_curso"])["ativos"]
        c = pd.concat([serie.rename("serie"), cota], axis=1).fillna(0)
        cota_m = nom[nom["dt_inicio"] < inicio].groupby("co_ibge").size()
        mun_listados = set(painel.loc[painel["mes"] == m, "co_ibge"])
        linhas.append({
            "mes": m, "municipios_listados": len(mun_listados),
            "celulas_municipio_curso_listadas": int(len(serie)), "ativos_na_serie": int(serie.sum()),
            "cota_inferior_do_retrato": int(cota.sum()),
            "celulas_com_violacao": int((c["serie"] < c["cota"]).sum()),
            "deficit_de_ativos": int((c["cota"] - c["serie"]).clip(lower=0).sum()),
            "municipios_da_cota_ausentes_da_listagem": int((~cota_m.index.isin(list(mun_listados))).sum()),
        })
    tab = pd.DataFrame(linhas)
    # Redistribuição: município com mais ativos que o máximo dos meses vizinhos listados.
    larga = painel.groupby(["co_ibge", "mes"])["ativos"].sum().unstack("mes").reindex(columns=meses)
    exc_n, exc_tot = [], []
    for j, m in enumerate(meses):
        viz = [meses[i] for i in (j - 1, j + 1) if 0 <= i < len(meses)]
        ref = larga[viz].max(axis=1, skipna=True)
        e = (larga[m] - ref)[larga[m].notna() & ref.notna()]
        exc_n.append(int((e > 0).sum()))
        exc_tot.append(int(e[e > 0].sum()))
    tab["municipios_acima_do_maximo_dos_meses_vizinhos"] = exc_n
    tab["excesso_sobre_o_maximo_dos_meses_vizinhos"] = exc_tot
    tab["cota_inferior_respeitada"] = (tab["celulas_com_violacao"] == 0).astype(int)
    tab["sem_municipio_da_cota_ausente"] = (tab["municipios_da_cota_ausentes_da_listagem"] == 0).astype(int)
    ult = painel[painel["mes"] == ultimo].set_index(["co_ibge", "cod_curso"])["ativos"]
    ret = nom.groupby(["co_ibge", "cod_curso"]).size()
    cc = pd.concat([ult.rename("serie"), ret.rename("retrato")], axis=1).fillna(0)
    ultimo_reproduz = bool((cc["serie"] == cc["retrato"]).all())
    completa = ultimo_reproduz and bool((tab["celulas_com_violacao"] == 0).all())
    return tab, {"ultimo_mes": ultimo, "ultimo_mes_reproduz_retrato_nominal": ultimo_reproduz,
                 "celulas_divergentes_no_ultimo_mes": int((cc["serie"] != cc["retrato"]).sum()),
                 "listagem_completa_em_todos_os_meses": completa,
                 "meses_com_violacao": tab.loc[tab["celulas_com_violacao"] > 0, "mes"].tolist(),
                 "meses_sem_municipio_da_cota_ausente": tab.loc[tab["sem_municipio_da_cota_ausente"] == 1,
                                                                "mes"].tolist()}


def outcomes_x3(painel: pd.DataFrame, rv: pd.DataFrame, pop: pd.Series, *, completa: bool,
                ultimo_completo: bool, universo: pd.Index | None = None,
                meses_sensibilidade: list[str] | dict[str, list[str]] | None = None
                ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Painel município × mês e outcomes por município (queda e meses com ativo).

    `completa`: ausência de linha vira zero em `universo` (U). Senão, cada mês
    usa só os municípios listados naquele mês. A queda usa o último mês: se ele
    reproduz o retrato nominal (`ultimo_completo`), município listado antes e
    ausente no último mês tem zero no último mês; senão a queda fica NaN.
    População da queda e dos meses com ativo: municípios com pico > 0.
    Sensibilidades (`meses_sensibilidade`: {prefixo: meses}; uma lista vira
    {"x3s": lista}): o pico só nos meses dados. x3s = meses sem município da
    cota ausente; x3m = todos menos mai/26 e jun/26 (pedido da auditoria).
    """
    if isinstance(meses_sensibilidade, (list, tuple)):
        meses_sensibilidade = {"x3s": list(meses_sensibilidade)}
    meses_sensibilidade = meses_sensibilidade or {}
    meses = sorted(painel["mes"].unique())
    ultimo = meses[-1]
    pm = painel.groupby(["co_ibge", "mes"], as_index=False)["ativos"].sum()
    pm["listado"] = 1
    if completa:
        if universo is None:
            raise ValueError("universo exigido quando a listagem é completa")
        grade = pd.MultiIndex.from_product([sorted(universo), meses], names=["co_ibge", "mes"]).to_frame(index=False)
        pm = grade.merge(pm, on=["co_ibge", "mes"], how="left")
        pm["listado"] = pm["listado"].fillna(0).astype(int)
        pm["ativos"] = pm["ativos"].fillna(0.0)
    pm = pm.merge(rv, on="co_ibge", how="left")
    pm["populacao_2022"] = pm["co_ibge"].map(pop)
    pm["ativos_por_10k"] = pm["ativos"] / pm["populacao_2022"] * POR_HAB
    larga = pm.pivot(index="co_ibge", columns="mes", values="ativos")
    obs = larga.notna()
    pico = larga.max(axis=1)
    mun = pd.DataFrame({"co_ibge": larga.index, "meses_listados": obs.sum(axis=1).to_numpy(),
                        "pico": pico.to_numpy(),
                        "mes_do_pico": larga.fillna(-1).idxmax(axis=1).to_numpy()})
    ult = larga[ultimo] if ultimo in larga else pd.Series(np.nan, index=larga.index)
    ult_val = ult.fillna(0.0) if (ultimo_completo or completa) else ult
    mun["ativos_ultimo_mes"] = ult_val.to_numpy()
    mun["listado_no_ultimo_mes"] = obs[ultimo].astype(int).to_numpy() if ultimo in obs else 0
    mun = mun.merge(rv, on="co_ibge", how="left")
    mun["populacao_2022"] = mun["co_ibge"].map(pop)
    mun["com_ativo_em_algum_mes"] = (mun["pico"] > 0).astype(int)
    pos = mun["pico"] > 0
    mun["x3_queda_pico_ultimo"] = np.where(pos, mun["pico"] - mun["ativos_ultimo_mes"], np.nan)
    mun["x3_queda_pico_ultimo_por_10k"] = mun["x3_queda_pico_ultimo"] / mun["populacao_2022"] * POR_HAB
    mun["x3_queda_relativa"] = np.where(pos, mun["x3_queda_pico_ultimo"] / mun["pico"].where(pos), np.nan)
    mun["x3_meses_com_ativo"] = np.where(pos, (larga > 0).sum(axis=1).reindex(mun["co_ibge"]).to_numpy(), np.nan)
    for pre, lista in meses_sensibilidade.items():
        ms = [m for m in meses if m in set(lista)]
        if ultimo not in ms:
            raise ValueError("a sensibilidade exige o ultimo mes")
        pico_s = larga[ms].max(axis=1).reindex(mun["co_ibge"]).to_numpy()
        pos_s = np.nan_to_num(pico_s, nan=0.0) > 0
        suf = "" if pre == "x3s" else f"_{pre}"
        mun[f"pico_meses_sensibilidade{suf}"] = pico_s
        mun[f"com_ativo_nos_meses_sensibilidade{suf}"] = pos_s.astype(int)
        mun[f"{pre}_queda_pico_ultimo"] = np.where(pos_s, pico_s - mun["ativos_ultimo_mes"], np.nan)
        mun[f"{pre}_queda_pico_ultimo_por_10k"] = mun[f"{pre}_queda_pico_ultimo"] / mun["populacao_2022"] * POR_HAB
        mun[f"{pre}_queda_relativa"] = np.where(pos_s, mun[f"{pre}_queda_pico_ultimo"] / np.where(pos_s, pico_s, 1.0),
                                                np.nan)
    motivos = []
    for r in mun.itertuples(index=False):
        m = {}
        if not r.pico > 0:
            for c in ("x3_queda_pico_ultimo", "x3_queda_pico_ultimo_por_10k", "x3_queda_relativa",
                      "x3_meses_com_ativo"):
                m[c] = "sem ativo em nenhum mes listado (fora da populacao da queda)"
        elif not np.isfinite(r.ativos_ultimo_mes):
            m["x3_queda_pico_ultimo"] = "ultimo mes nao listado e listagem do ultimo mes nao validada"
        if not np.isfinite(r.populacao_2022) and "x3_queda_pico_ultimo_por_10k" not in m:
            m["x3_queda_pico_ultimo_por_10k"] = "sem populacao do Censo 2022"
        for pre in meses_sensibilidade:
            suf = "" if pre == "x3s" else f"_{pre}"
            if not getattr(r, f"com_ativo_nos_meses_sensibilidade{suf}"):
                for c in ("queda_pico_ultimo", "queda_pico_ultimo_por_10k", "queda_relativa"):
                    m[f"{pre}_{c}"] = "sem ativo nos meses da sensibilidade (fora da populacao)"
        motivos.append(json.dumps(m, ensure_ascii=False, sort_keys=True))
    mun["motivos_ausencia"] = motivos
    return pm, mun


# ---------------------------------------------------------------------------
# Linhas de estimativa
# ---------------------------------------------------------------------------

COLUNAS_EST = [
    "natureza_dos_dados", "estatuto", "x_id", "outcome_id", "outcome", "descricao_outcome", "nivel", "populacao",
    "ciclo", "mes", "corte", "especificacao", "estimador", "status", "h", "n_abaixo", "n_acima", "n_obs",
    "n_clusters", "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "entra_bky", "q_bky", "lee_tau_inf",
    "lee_tau_sup", "lee_ic95_inf", "lee_ic95_sup", "lee_q_aparo", "lee_salto_selecao", "lee_p0_selecao",
    "lee_p1_selecao", "media_bruta_abaixo", "media_bruta_acima", "pesos_grupos", "unidade", "contraste",
    "no_protocolo_45", "rotulo", "condicionamento", "regra_ligacao", "q_bky_so_protocolo", "nota",
]
ADICIONAL = "ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO"
REGRA_AMPLA = "ampla (principal): similaridade ou mesmo 1o nome e 2 partes"
REGRA_ESTREITA = "estreita (1a execucao): so similaridade"
COND_X2_CONDICIONAL = "condicional a preencher (pos-tratamento): limites de Lee por ciclo e corte"
COND_X2_INCONDICIONAL = "incondicional: todas as celulas (municipios) oferecidas"
COND_X3_MES = ("condicional a listagem do mes (pos-tratamento: a listagem pode depender do lado do corte); "
               "sem limites de Lee")
COND_X3_QUEDA = ("condicional a pico > 0 nas listagens (pos-tratamento); sem limites de Lee; mistura municipios "
                 "com horizontes diferentes (ciclo 1 e ciclo 2)")


def nova_linha(meta: dict, especificacao: str, estimador: str) -> dict:
    linha = {c: np.nan for c in COLUNAS_EST}
    linha.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "mes": "", "ciclo": "", **meta,
                  "especificacao": especificacao, "estimador": estimador, "status": "EXECUTADO",
                  "h": H / 1000.0, "entra_bky": False, "contraste": CONTRASTE, "no_protocolo_45": True,
                  "rotulo": "", "condicionamento": "", "regra_ligacao": "", "nota": ""})
    return linha


def preencher(linha: dict, res: dict) -> dict:
    for k in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters",
              "media_bruta_abaixo", "media_bruta_acima"):
        if res.get(k) is not None:
            linha[k] = res[k]
    if res.get("pesos_grupos"):
        linha["pesos_grupos"] = json.dumps({k: round(v, 12) for k, v in res["pesos_grupos"].items()})
    linha["nota"] = "; ".join(x for x in (linha["nota"], res.get("nota", "")) if x)
    if not np.isfinite(float(linha["tau"])):
        linha["status"] = "SEM_ESTIMATIVA"
        linha["nota"] = linha["nota"] or "biblioteca devolveu NaN sem motivo"
    else:
        linha["entra_bky"] = True
    return linha


def linha_lee(meta: dict, rl: dict, sel_desc: str) -> dict:
    ll = nova_linha(meta, "limites_lee", f"limites de Lee locais (rdd_lib.limites_lee_rd; selecionado = {sel_desc})")
    ll.update({"lee_tau_inf": rl["tau_inf"], "lee_tau_sup": rl["tau_sup"], "lee_ic95_inf": rl["ic95_inf"],
               "lee_ic95_sup": rl["ic95_sup"], "lee_q_aparo": rl["q_aparo"], "lee_salto_selecao": rl["salto_selecao"],
               "lee_p0_selecao": rl["p0_selecao"], "lee_p1_selecao": rl["p1_selecao"], "n_abaixo": rl["n_abaixo"],
               "n_acima": rl["n_acima"], "tau": rl["tau_selecionados"], "ep": rl["ep_selecionados"]})
    ll["nota"] = "; ".join(x for x in (
        "tau e ep = local linear ingenuo nos selecionados; o efeito so e limitado por lee_tau_inf e lee_tau_sup; "
        "IC 95% de Lee conservador", f"lado aparado = {rl['lado_aparado']}", rl.get("nota", "")) if x)
    if not np.isfinite(rl["tau_inf"]):
        ll["status"] = "SEM_ESTIMATIVA"
    return ll


def nao_executado(meta: dict, especificacao: str, estimador: str, motivo: str) -> dict:
    linha = nova_linha(meta, especificacao, estimador)
    linha.update({"status": "NAO_EXECUTADO", "nota": motivo})
    return linha


def _arr(d: pd.DataFrame, col: str) -> np.ndarray:
    return d[col].to_numpy(dtype=float)


def empilhar(partes: list[tuple[pd.DataFrame, int, str]], cols: list[str]) -> pd.DataFrame:
    blocos = []
    for d, corte, grupo in partes:
        b = d[["co_ibge", "s_mil"] + cols].copy()
        b["corte_mil"] = corte
        b["grupo"] = grupo
        blocos.append(b)
    return pd.concat(blocos, ignore_index=True)


def rd_empilhado_df(e: pd.DataFrame, col: str) -> dict:
    cl = e["co_ibge"].to_numpy()
    return L.rd_empilhado(_arr(e, "s_mil"), _arr(e, col), _arr(e, "corte_mil"), grupo=e["grupo"].to_numpy(),
                          h_mil=H, cluster=cl, ids_unidade=cl)


# ---------------------------------------------------------------------------
# X2: especificações
# ---------------------------------------------------------------------------

OUTCOMES_X2 = [
    {"id": "X2.1", "nivel": "celula", "col": "x2_frac_ativos_celula", "lee": "selecionada",
     "desc": "fracao dos alocados determinados da celula ainda ativos no municipio de alocacao (retrato 11/09/2026); "
             "condicional a preencher", "unidade": "fracao (0-1); salto em p.p./100"},
    {"id": "X2.2", "nivel": "municipio", "col": "x2_frac_ativos_municipio", "lee": "selecionado",
     "desc": "fracao dos alocados determinados do municipio ainda ativos no municipio; condicional a preencher",
     "unidade": "fracao (0-1); salto em p.p./100"},
    {"id": "X2.3", "nivel": "celula", "col": "x2_celula_com_alocado_ativo", "lee": None,
     "desc": "celula oferecida com ao menos um alocado da 1a chamada ainda ativo (0 se nao preenchida); "
             "incondicional", "unidade": "proporcao (0-1)"},
    {"id": "X2.4", "nivel": "municipio", "col": "x2_alocados_ativos_por_celula", "lee": None,
     "desc": "alocados da 1a chamada ainda ativos por celula oferecida no municipio; incondicional",
     "unidade": "alocados ativos por celula"},
]
EST_CEL = "local linear sharp, kernel triangular, h = 0,050; celula com peso do municipio; EP CR1 por municipio"
EST_MUN = "local linear sharp, kernel triangular, h = 0,050; EP HC1 por municipio"
EST_EMP = ("empilhado: local linear triangular, intercepto e inclinacoes por grupo x lado, tau comum; "
           "EP CR1 por municipio")
SEM_LEE_EMP = "rdd_lib so tem limites de Lee em um corte e um ciclo; relatados por ciclo e corte"


def estimar_x2(cel: pd.DataFrame, mun: pd.DataFrame, regra: str = REGRA_AMPLA, bky: bool = True) -> pd.DataFrame:
    """Todas as linhas X2. Rótulos: X2.3, X2.4 e as especificações empilhadas são adições ao doc 45 (§3 do X2
    lista RDD com Lee e descritivo; não lista outcomes incondicionais nem empilhamento). `bky=False` (regra
    estreita) deixa as linhas fora do BKY."""
    linhas: list[dict] = []
    for sp in OUTCOMES_X2:
        base = {"x_id": "X2", "outcome_id": sp["id"], "outcome": sp["col"], "descricao_outcome": sp["desc"],
                "nivel": sp["nivel"], "unidade": sp["unidade"]}
        cond = COND_X2_CONDICIONAL if sp["lee"] else COND_X2_INCONDICIONAL
        outcome_no_prot = sp["lee"] is not None
        rot_out = "" if outcome_no_prot else "outcome incondicional nao listado no doc 45"
        dados = {k: (cel if sp["nivel"] == "celula" else mun).query("ciclo == @k").reset_index(drop=True)
                 for k in CICLOS_X2}

        def m(i0: int, empilhado: bool) -> None:
            no_prot = outcome_no_prot and not empilhado
            extra = "; ".join(x for x in (rot_out, "especificacao empilhada nao listada no §3 do doc 45 "
                                                   "(o §2 cita cortes empilhados de forma generica)" if empilhado
                                          else "") if x)
            marcar(linhas, i0, no_protocolo=no_prot, rotulo_extra=extra, condicionamento=cond, regra=regra, bky=bky)

        for k in CICLOS_X2:
            d = dados[k]
            for corte in CORTES:
                i0 = len(linhas)
                meta = {**base, "populacao": f"V{k}", "ciclo": str(k), "corte": ROTULO_CORTE[corte]}
                if sp["nivel"] == "celula":
                    r = L.rd_local_linear(_arr(d, "s_mil"), _arr(d, sp["col"]), corte, H,
                                          cluster=d["co_ibge"].to_numpy(), ids_unidade=d["co_ibge"].to_numpy())
                    est = EST_CEL
                else:
                    r = L.rd_local_linear(_arr(d, "s_mil"), _arr(d, sp["col"]), corte, H)
                    est = EST_MUN
                linhas.append(preencher(nova_linha(meta, "principal", est), r))
                if sp["lee"]:
                    cl = d["co_ibge"].to_numpy() if sp["nivel"] == "celula" else None
                    rl = L.limites_lee_rd(_arr(d, "s_mil"), _arr(d, sp["col"]), _arr(d, sp["lee"]), corte, H,
                                          cluster=cl, ids_unidade=cl)
                    linhas.append(linha_lee(meta, rl, f"{sp['lee']} (ter alocado determinado)"))
                m(i0, False)
            i0 = len(linhas)
            meta = {**base, "populacao": f"V{k}", "ciclo": str(k), "corte": EMPILHADO}
            e = empilhar([(d, c, str(c)) for c in CORTES], [sp["col"]])
            linhas.append(preencher(nova_linha(meta, "cortes_empilhados", EST_EMP), rd_empilhado_df(e, sp["col"])))
            if sp["lee"]:
                linhas.append(nao_executado(meta, "limites_lee", "limites de Lee empilhados", SEM_LEE_EMP))
            m(i0, True)
        i0 = len(linhas)
        for corte in CORTES:
            meta = {**base, "populacao": "V1+V2", "ciclo": "1+2", "corte": ROTULO_CORTE[corte]}
            e = empilhar([(dados[k], corte, f"c{k}") for k in CICLOS_X2], [sp["col"]])
            linhas.append(preencher(nova_linha(meta, "ciclos_empilhados", EST_EMP + "; interceptos por ciclo = EF de "
                                                                                    "ciclo"),
                                    rd_empilhado_df(e, sp["col"])))
            if sp["lee"]:
                linhas.append(nao_executado(meta, "limites_lee", "limites de Lee empilhados", SEM_LEE_EMP))
        meta = {**base, "populacao": "V1+V2", "ciclo": "1+2", "corte": EMPILHADO}
        e = empilhar([(dados[k], c, f"c{k}_{c}") for k in CICLOS_X2 for c in CORTES], [sp["col"]])
        linhas.append(preencher(nova_linha(meta, "ciclos_e_cortes_empilhados",
                                           EST_EMP + "; grupos ciclo x corte (EF de ciclo)"),
                                rd_empilhado_df(e, sp["col"])))
        if sp["lee"]:
            linhas.append(nao_executado(meta, "limites_lee", "limites de Lee empilhados", SEM_LEE_EMP))
        m(i0, True)
        for linha in linhas[i0:]:
            linha["nota"] = "; ".join(x for x in (linha["nota"], "ciclos empilhados misturam horizontes de "
                                                  "seguimento diferentes (ver horizonte_por_ciclo no resumo)") if x)
    return aplicar_bky(pd.DataFrame(linhas, columns=COLUNAS_EST))


def aplicar_bky(est: pd.DataFrame) -> pd.DataFrame:
    """q de BKY dentro do X: `q_bky` sobre todas as linhas com `entra_bky` (protocolo e adições, regra de
    ligação principal); `q_bky_so_protocolo` só sobre as linhas que estão no §3 do doc 45."""
    est = est.copy()
    for col, extra in (("q_bky", None), ("q_bky_so_protocolo", "no_protocolo_45")):
        est[col] = np.nan
        m = est["entra_bky"].astype(bool) & est["p_valor"].notna()
        if extra:
            m &= est[extra].astype(bool)
        if m.any():
            est.loc[m, col] = L.qvalores_bky(est.loc[m, "p_valor"].to_numpy(dtype=float))
    return est


def marcar(linhas: list[dict], i0: int, *, no_protocolo: bool, rotulo_extra: str = "", condicionamento: str = "",
           regra: str = "", bky: bool = True) -> None:
    """Rótulos das linhas linhas[i0:] (adição ao protocolo, condicionamento, regra de ligação)."""
    for linha in linhas[i0:]:
        linha["no_protocolo_45"] = no_protocolo
        linha["rotulo"] = "" if no_protocolo else f"{ADICIONAL}{': ' + rotulo_extra if rotulo_extra else ''}"
        linha["condicionamento"] = condicionamento
        linha["regra_ligacao"] = regra
        if not bky:
            linha["entra_bky"] = False


# ---------------------------------------------------------------------------
# X3: especificações
# ---------------------------------------------------------------------------

def estimar_x3(pm: pd.DataFrame, mun: pd.DataFrame, pop_desc: str, comp_tab: pd.DataFrame) -> pd.DataFrame:
    """Linhas X3. Por corte: protocolo (§3 do X3: RDD mês a mês e da queda). Cortes empilhados e as
    sensibilidades do pico são adições ao protocolo."""
    linhas: list[dict] = []
    qual = comp_tab.set_index("mes")

    def rodar(d: pd.DataFrame, col: str, meta: dict, cond: str, esp: str = "principal", nota: str = "",
              rotulo_extra: str = "") -> None:
        d = d[d["s_mil"].notna()].reset_index(drop=True)
        for corte in CORTES:
            r = L.rd_local_linear(_arr(d, "s_mil"), _arr(d, col), corte, H)
            linha = nova_linha({**meta, "corte": ROTULO_CORTE[corte]}, esp, EST_MUN)
            linha["nota"] = nota
            linhas.append(preencher(linha, r))
            marcar(linhas, len(linhas) - 1, no_protocolo=esp == "principal", rotulo_extra=rotulo_extra,
                   condicionamento=cond)
        e = empilhar([(d, c, str(c)) for c in CORTES], [col])
        linha = nova_linha({**meta, "corte": EMPILHADO}, "cortes_empilhados" if esp == "principal" else
                           f"{esp}_cortes_empilhados", EST_EMP)
        linha["nota"] = nota
        linhas.append(preencher(linha, rd_empilhado_df(e, col)))
        marcar(linhas, len(linhas) - 1, no_protocolo=False, condicionamento=cond,
               rotulo_extra="; ".join(x for x in (rotulo_extra, "cortes empilhados nao listados no §3 do doc 45 "
                                                  "(o §2 cita cortes empilhados de forma generica)") if x))

    for mes in sorted(pm["mes"].unique()):
        d = pm[pm["mes"] == mes]
        q = qual.loc[mes]
        nota_mes = "; ".join(x for x in (
            "" if q["cota_inferior_respeitada"] else
            f"listagem do mes falha a cota inferior do retrato ({int(q['celulas_com_violacao'])} celulas)",
            "" if q["sem_municipio_da_cota_ausente"] else
            f"{int(q['municipios_da_cota_ausentes_da_listagem'])} municipios da cota ausentes da listagem",
            "" if not q["municipios_acima_do_maximo_dos_meses_vizinhos"] else
            f"{int(q['municipios_acima_do_maximo_dos_meses_vizinhos'])} municipios acima do maximo dos meses "
            f"vizinhos (excesso {int(q['excesso_sobre_o_maximo_dos_meses_vizinhos'])})") if x)
        for oid, col, un, desc in (
                ("X3.1", "ativos", "ativos (contagem)", "ativos do PMM-E no municipio no mes (soma dos cursos)"),
                ("X3.2", "ativos_por_10k", "ativos por 10 mil hab. (Censo 2022)",
                 "ativos do PMM-E no municipio no mes por 10 mil habitantes")):
            rodar(d, col, {"x_id": "X3", "outcome_id": oid, "outcome": col, "descricao_outcome": desc,
                           "nivel": "municipio", "populacao": pop_desc, "mes": mes, "unidade": un}, COND_X3_MES,
                  nota=nota_mes)
    for oid, col, un, desc in (
            ("X3.3", "x3_queda_pico_ultimo", "ativos (contagem)", "queda do pico ao ultimo mes (pico - ultimo)"),
            ("X3.4", "x3_queda_pico_ultimo_por_10k", "ativos por 10 mil hab.", "queda do pico ao ultimo mes por "
                                                                              "10 mil habitantes"),
            ("X3.5", "x3_queda_relativa", "fracao do pico", "queda relativa ao pico ((pico - ultimo) / pico)"),
            ("X3.6", "x3_meses_com_ativo", "meses (0-9)", "meses listados com ao menos um ativo")):
        rodar(mun[mun["com_ativo_em_algum_mes"] == 1], col,
              {"x_id": "X3", "outcome_id": oid, "outcome": col, "descricao_outcome": desc, "nivel": "municipio",
               "populacao": "municipios com ativo em algum mes listado", "mes": "dez/25-ago/26", "unidade": un},
              COND_X3_QUEDA, nota="pico entre os meses listados, inclusive meses que falham a conferencia de "
                                  "completude")
    sens = []
    if "x3s_queda_pico_ultimo" in mun:
        meses_s = ",".join(qual.index[qual["sem_municipio_da_cota_ausente"] == 1])
        sens.append(("x3s", "s", "", meses_s, "sensibilidade_meses_sem_ausencia",
                     f"pico so nos meses sem municipio da cota ausente ({meses_s})",
                     "definida pelo diagnostico de completude, antes de abrir qualquer estimativa X3, mas depois de "
                     "impresso o descritivo da queda por faixa"))
    if "x3m_queda_pico_ultimo" in mun:
        meses_m = ",".join(m for m in qual.index if m not in MESES_EXCLUIDOS_AUDITORIA)
        sens.append(("x3m", "m", "_x3m", meses_m, "sensibilidade_sem_mai_jun",
                     f"pico em todos os meses menos {', '.join(MESES_EXCLUIDOS_AUDITORIA)}",
                     "pedida pela auditoria independente de 19/10/2026, depois de vistos os resultados X3"))
    for pre, letra, suf, meses_x, esp, desc_pico, origem in sens:
        for oid, col, un, desc in (
                (f"X3.3{letra}", f"{pre}_queda_pico_ultimo", "ativos (contagem)", "queda do pico ao ultimo mes"),
                (f"X3.4{letra}", f"{pre}_queda_pico_ultimo_por_10k", "ativos por 10 mil hab.", "queda por 10 mil hab."),
                (f"X3.5{letra}", f"{pre}_queda_relativa", "fracao do pico", "queda relativa ao pico")):
            rodar(mun[mun[f"com_ativo_nos_meses_sensibilidade{'' if pre == 'x3s' else suf}"] == 1], col,
                  {"x_id": "X3", "outcome_id": oid, "outcome": col, "descricao_outcome": f"{desc}, {desc_pico}",
                   "nivel": "municipio", "populacao": "municipios com ativo nesses meses", "mes": meses_x,
                   "unidade": un}, COND_X3_QUEDA, esp=esp, rotulo_extra=origem)
    return aplicar_bky(pd.DataFrame(linhas, columns=COLUNAS_EST))


# ---------------------------------------------------------------------------
# Descritivos
# ---------------------------------------------------------------------------

def descritivo_x2(pessoas: pd.DataFrame) -> pd.DataFrame:
    """Por ciclo e faixa (regra sharp no IVS a08): ligação e permanência; 'TOTAL' agrega as faixas.

    `subgrupo` = 'todos', ou o evento final da pessoa no ciclo 1 (homologação
    ou só confirmação de local), por faixa e no total.
    """
    p = pessoas.assign(faixa=pessoas["s_mil"].map(faixa_regra))
    grupos = [((k, f, "todos"), g) for (k, f), g in p.groupby(["ciclo", "faixa"])]
    grupos += [((k, "TOTAL", "todos"), g) for k, g in p.groupby("ciclo")]
    c1 = p[p["ciclo"] == 1]
    grupos += [((1, f, ev), g) for (f, ev), g in c1.groupby(["faixa", "evento_final"])]
    grupos += [((1, "TOTAL", ev), g) for ev, g in c1.groupby("evento_final")]
    linhas = []
    for (k, f, sub), g in grupos:
        st = g["status_ligacao"].value_counts()
        det = g["ativo"].notna().sum()
        inc = int(st.get("INCERTO", 0))
        lig = int(st.get("LIGADO", 0))
        linhas.append({
            "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "x_id": "X2", "ciclo": int(k), "faixa": f,
            "subgrupo": sub,
            "n_alocados": int(len(g)), "n_ligados": lig, "n_nao_ligados": int(st.get("NAO_LIGADO", 0)),
            "n_ambiguos": int(st.get("AMBIGUO", 0)), "n_incertos": inc,
            "taxa_ligacao": lig / len(g) if len(g) else np.nan,
            "permanencia_set": g["ativo"].mean() if det else np.nan,
            "permanencia_set_incertos_como_ativos": (lig + inc) / (det + inc) if det + inc else np.nan,
            "permanencia_set_incertos_como_saidos": lig / (det + inc) if det + inc else np.nan,
            "permanencia_ago": g["ativo_ago"].mean() if g["ativo_ago"].notna().any() else np.nan,
            "n_determinados_ago": int(g["ativo_ago"].notna().sum()),
            "presenca_no_programa_set": g["ativo_no_programa"].mean() if g["ativo_no_programa"].notna().any()
            else np.nan,
            "n_celula_fora_do_quadro": int((~g["celula_no_quadro"]).sum()),
        })
    return pd.DataFrame(linhas).sort_values(["ciclo", "subgrupo", "faixa"]).reset_index(drop=True)


def descritivo_x3(pm: pd.DataFrame, painel_mc: pd.DataFrame, mun: pd.DataFrame) -> pd.DataFrame:
    """Por mês e faixa (regra sharp no IVS a08): municípios e células listados, ativos e queda."""
    pm = pm.assign(faixa=pm["s_mil"].map(lambda v: faixa_regra(v) if pd.notna(v) else "SEM IVS OFICIAL"))
    mc = painel_mc.merge(pm[["co_ibge", "faixa"]].drop_duplicates(), on="co_ibge", how="left")
    linhas = []
    for (mes, f), g in list(pm.groupby(["mes", "faixa"])) + [((m, "TOTAL"), g) for m, g in pm.groupby("mes")]:
        gc = mc[(mc["mes"] == mes) & ((mc["faixa"] == f) if f != "TOTAL" else True)]
        linhas.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "x_id": "X3", "mes": mes, "faixa": f,
                       "municipios_listados": int(g["listado"].sum()),
                       "municipios_com_ativo": int((g["ativos"] > 0).sum()), "ativos": float(g["ativos"].sum()),
                       "media_ativos_por_municipio_listado": float(g["ativos"].mean()),
                       "media_ativos_por_10k": float(g["ativos_por_10k"].mean()),
                       "celulas_municipio_curso_listadas": int(len(gc)),
                       "celulas_municipio_curso_com_ativo": int((gc["ativos"] > 0).sum())})
    mun = mun.assign(faixa=mun["s_mil"].map(lambda v: faixa_regra(v) if pd.notna(v) else "SEM IVS OFICIAL"))
    pos = mun[mun["com_ativo_em_algum_mes"] == 1]
    for f, g in list(pos.groupby("faixa")) + [("TOTAL", pos)]:
        linhas.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "x_id": "X3", "mes": "queda", "faixa": f,
                       "municipios_listados": int(len(g)),
                       "municipios_com_ativo": int((g["ativos_ultimo_mes"] > 0).sum()),
                       "ativos": float(g["pico"].sum()),
                       "media_ativos_por_municipio_listado": float(g["x3_queda_pico_ultimo"].mean()),
                       "media_ativos_por_10k": float(g["x3_queda_pico_ultimo_por_10k"].mean()),
                       "celulas_municipio_curso_listadas": np.nan, "celulas_municipio_curso_com_ativo": np.nan,
                       "fracao_com_queda": float((g["x3_queda_pico_ultimo"] > 0).mean()),
                       "queda_relativa_media": float(g["x3_queda_relativa"].mean()),
                       "meses_com_ativo_media": float(g["x3_meses_com_ativo"].mean()),
                       "queda_media_sensibilidade": float(g["x3s_queda_pico_ultimo"].mean())
                       if "x3s_queda_pico_ultimo" in g else np.nan,
                       "queda_relativa_media_sensibilidade": float(g["x3s_queda_relativa"].mean())
                       if "x3s_queda_relativa" in g else np.nan,
                       "queda_media_sem_mai_jun": float(g["x3m_queda_pico_ultimo"].mean())
                       if "x3m_queda_pico_ultimo" in g else np.nan,
                       "queda_relativa_media_sem_mai_jun": float(g["x3m_queda_relativa"].mean())
                       if "x3m_queda_relativa" in g else np.nan})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def carregar_celulas_v(rv: pd.DataFrame) -> pd.DataFrame:
    cel = pd.read_parquet(ARQ_VC, columns=["ciclo", "co_ibge", "co_cnes_7d", "cod_curso", "faixa_anunciada",
                                           "ivs_2010_oficial", "n_alocados_ch1", "n_confirmacoes_ch1",
                                           "n_homologacoes_ch1"])
    cel = cel[cel["ciclo"].isin(CICLOS_X2)].copy()
    cel["cod_curso"] = cel["cod_curso"].astype(int)
    cel["s_mil"] = cel["co_ibge"].map(rv.set_index("co_ibge")["s_mil"])
    s_b = s_mil_de_ivs(cel["ivs_2010_oficial"])
    ok = s_b.notna()
    if ((cel.loc[ok, "s_mil"] - s_b[ok]).abs() > 0).any() or cel.loc[ok, "s_mil"].isna().any():
        raise FalhaValidacao("IVS das células difere do a08")
    return cel


def conferir_eventos_contra_tarefa_b(ev: pd.DataFrame, cel: pd.DataFrame) -> dict:
    """Contagens por célula dos eventos lidos aqui = colunas da tarefa B (falha fechada)."""
    chave = ["ciclo", "co_cnes_7d", "cod_curso"]
    conf = {}
    for ciclo, evento, col in ((1, "confirmacao", "n_confirmacoes_ch1"), (1, "homologacao", "n_homologacoes_ch1"),
                               (2, "alocacao", "n_alocados_ch1")):
        e = ev[(ev["ciclo"] == ciclo) & (ev["evento"] == evento)].groupby(chave).size().rename("aqui")
        c = cel[cel["ciclo"] == ciclo].set_index(chave)[col].rename("b")
        m = pd.concat([c, e], axis=1)
        dentro = m["b"].notna()
        dif = int((m.loc[dentro, "aqui"].fillna(0) != m.loc[dentro, "b"]).sum())
        if dif:
            raise FalhaValidacao(f"c{ciclo} {evento}: {dif} células com contagem diferente da tarefa B ({col})")
        conf[f"c{ciclo}_{evento}_igual_a_{col}"] = True
        conf[f"c{ciclo}_{evento}_eventos_fora_do_quadro"] = int(m.loc[~dentro, "aqui"].sum())
    return conf


def horizonte_por_ciclo(lig_set: pd.DataFrame, at: dict[str, pd.DataFrame]) -> dict:
    """Meses entre o início de atividade (dos ativos ligados) e as datas de referência, por ciclo de alocação.

    X2 (retrato de set): só os alocados ligados têm data de início; quem saiu não tem, então a mediana é dos que
    ficaram. X3 (retrato de 12/08/2026): ativos do retrato pelo ciclo do próprio ativo.
    """
    a, n = at["set"], at["ago"]
    out = {}
    lig = lig_set[lig_set["_idx_ativo"].notna()]
    for k, g in lig.groupby("ciclo"):
        ia = g["_idx_ativo"].astype(int).to_numpy()
        meses = (a.loc[ia, "dt_ref"] - a.loc[ia, "dt_inicio"]).dt.days / 30.4375
        out[f"ciclo_{k}"] = {"x2_mediana_meses_inicio_ate_retrato_set": float(meses.median()),
                             "x2_inicio_min": str(a.loc[ia, "dt_inicio"].min().date()),
                             "x2_inicio_max": str(a.loc[ia, "dt_inicio"].max().date())}
    for k, g in n.groupby("ciclo_k"):
        meses = (g["dt_ref"] - g["dt_inicio"]).dt.days / 30.4375
        out.setdefault(f"ciclo_{k}", {})["x3_mediana_meses_inicio_ate_retrato_ago"] = float(meses.median())
    return out


def executar() -> dict:
    sha_ativos = sha256(ATIVOS_ZIP)
    if sha_ativos != B.SHA256_ATIVOS_PROTOCOLO:
        raise FalhaValidacao("relação nominal de ativos diferente da usada no E3")
    rv = ler_a08()
    pop = ler_populacao()
    cel_v = carregar_celulas_v(rv)

    # ------------------------------ X2 ------------------------------------
    ev, diag_ev = ler_eventos_alocacao()
    conf_b = conferir_eventos_contra_tarefa_b(ev, cel_v)
    pessoas, diag_p = consolidar_pessoas(ev)
    pessoas = municipio_pela_celula(pessoas, cel_v)
    pessoas["s_mil"] = pessoas["co_ibge"].map(rv.set_index("co_ibge")["s_mil"])
    at = ler_ativos_nominais()
    base_pessoas = pessoas

    def montar(partes: bool) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        ls, la = ligar(base_pessoas, at["set"], partes=partes), ligar(base_pessoas, at["ago"], partes=partes)
        pp = ls.copy()
        pp["status_ligacao_ago"] = la["status_ligacao"].to_numpy()
        pp["ativo_ago"] = la["ativo"].to_numpy()
        return pp, ls, la

    pessoas, lig_set, lig_ago = montar(True)
    pessoas_e, lig_set_e, _ = montar(False)          # regra estreita (1a execucao), relatada ao lado
    crm = concordancia_crm(lig_set, lig_ago, at)
    horizonte = horizonte_por_ciclo(lig_set, at)
    # Ativos do retrato sem alocado da 1a chamada ligado (cobertura da ligação, por ciclo do ativo).
    usados = set(lig_set["_idx_ativo"].dropna().astype(int))
    a_set = at["set"].assign(ligado=lambda d: d.index.isin(list(usados)))
    cobertura_ativos = {f"ciclo_{k}": {"ativos": int(len(g)), "ligados_a_alocado_da_1a_chamada": int(g["ligado"].sum())}
                        for k, g in a_set.groupby("ciclo_k")}
    celulas = agregar_celulas(pessoas, cel_v)
    municipios = agregar_municipios(celulas)
    conf_sel = {}
    c1 = celulas[celulas["ciclo"] == 1].merge(
        cel_v[cel_v["ciclo"] == 1][["co_cnes_7d", "cod_curso", "n_confirmacoes_ch1", "n_homologacoes_ch1"]],
        on=["co_cnes_7d", "cod_curso"])
    y1 = ((c1["n_confirmacoes_ch1"] > 0) | (c1["n_homologacoes_ch1"] > 0)).astype(int)
    conf_sel["c1_celulas_com_alocado_final"] = int((c1["n_alocados"] > 0).sum())
    conf_sel["c1_celulas_com_confirmacao_ou_homologacao"] = int(y1.sum())
    conf_sel["c1_celulas_que_divergem"] = int(((c1["n_alocados"] > 0).astype(int) != y1).sum())
    c2 = celulas[celulas["ciclo"] == 2]
    c2 = c2.merge(cel_v[cel_v["ciclo"] == 2][["co_cnes_7d", "cod_curso", "n_alocados_ch1"]],
                  on=["co_cnes_7d", "cod_curso"], validate="one_to_one")
    conf_sel["c2_n_alocados_por_celula_igual_a_n_alocados_ch1"] = bool((c2["n_alocados"] == c2["n_alocados_ch1"]).all())
    if not conf_sel["c2_n_alocados_por_celula_igual_a_n_alocados_ch1"]:
        raise FalhaValidacao("ciclo 2: pessoas alocadas por celula diferem de n_alocados_ch1 da tarefa B")
    est_x2 = estimar_x2(celulas[celulas["s_mil"].notna() & (celulas["so_excluidos"] == 0)],
                        municipios[municipios["s_mil"].notna() & (municipios["so_excluidos"] == 0)])
    cel_e = agregar_celulas(pessoas_e, cel_v)
    mun_e = agregar_municipios(cel_e)
    est_x2_e = estimar_x2(cel_e[cel_e["s_mil"].notna() & (cel_e["so_excluidos"] == 0)],
                          mun_e[mun_e["s_mil"].notna() & (mun_e["so_excluidos"] == 0)], regra=REGRA_ESTREITA,
                          bky=False)
    est_x2 = aplicar_bky(pd.concat([est_x2, est_x2_e], ignore_index=True))
    desc_x2 = pd.concat([descritivo_x2(pessoas).assign(regra_ligacao=REGRA_AMPLA),
                         descritivo_x2(pessoas_e).assign(regra_ligacao=REGRA_ESTREITA)], ignore_index=True)
    pessoas["status_ligacao_regra_estreita"] = pessoas_e["status_ligacao"].to_numpy()
    pessoas["ativo_regra_estreita"] = pessoas_e["ativo"].to_numpy()
    motivos = (pessoas.groupby(["ciclo", "status_ligacao", "motivo_ligacao"]).size().rename("n").reset_index()
               .assign(natureza_dos_dados=NATUREZA, estatuto=ESTATUTO, x_id="X2", retrato="11/09/2026"))
    motivos_ago = (pessoas.assign(m=lig_ago["motivo_ligacao"].to_numpy())
                   .groupby(["ciclo", "status_ligacao_ago", "m"]).size().rename("n").reset_index()
                   .rename(columns={"status_ligacao_ago": "status_ligacao", "m": "motivo_ligacao"})
                   .assign(natureza_dos_dados=NATUREZA, estatuto=ESTATUTO, x_id="X2", retrato="12/08/2026"))
    motivos = pd.concat([motivos, motivos_ago], ignore_index=True)
    pessoas_out = pessoas[["id_pessoa", "ciclo", "co_cnes_7d", "cod_curso", "co_ibge", "celula_no_quadro", "s_mil",
                           "evento_final", "eventos", "status_ligacao", "motivo_ligacao", "ativo", "ativo_no_programa",
                           "cnes_igual", "ciclo_igual", "status_ligacao_ago", "ativo_ago",
                           "status_ligacao_regra_estreita", "ativo_regra_estreita"]].copy()
    pessoas_out["faixa_regra"] = pessoas_out["s_mil"].map(faixa_regra)
    pessoas_out.insert(0, "estatuto", ESTATUTO)
    pessoas_out.insert(0, "natureza_dos_dados", NATUREZA)
    for df in (celulas, municipios):
        df.insert(0, "estatuto", ESTATUTO)
        df.insert(0, "natureza_dos_dados", NATUREZA)

    # ------------------------------ X3 ------------------------------------
    painel_mc, diag_serie = ler_serie()
    comp_tab, comp = verificar_completude(painel_mc, at["ago"])
    universo = pd.Index(rv["co_ibge"]) if comp["listagem_completa_em_todos_os_meses"] else None
    pm, mun3 = outcomes_x3(painel_mc, rv, pop, completa=comp["listagem_completa_em_todos_os_meses"],
                           ultimo_completo=comp["ultimo_mes_reproduz_retrato_nominal"], universo=universo,
                           meses_sensibilidade={
                               "x3s": comp["meses_sem_municipio_da_cota_ausente"],
                               "x3m": [m for m in sorted(painel_mc["mes"].unique())
                                       if m not in MESES_EXCLUIDOS_AUDITORIA]})
    pop_desc = ("U com zero onde nao ha linha (listagem completa)" if comp["listagem_completa_em_todos_os_meses"]
                else "municipios listados no mes (listagem incompleta: ausencia nao e zero)")
    est_x3 = estimar_x3(pm, mun3, pop_desc, comp_tab)
    desc_x3 = descritivo_x3(pm, painel_mc, mun3)
    v12 = set(cel_v["co_ibge"])
    listados = set(pm["co_ibge"])
    diag_pop_x3 = {
        "municipios_listados_em_algum_mes": len(listados),
        "listados_sem_ivs_oficial": sorted(set(pm.loc[pm["s_mil"].isna(), "co_ibge"])),
        "listados_sem_populacao_2022": sorted(set(pm.loc[pm["populacao_2022"].isna(), "co_ibge"])),
        "listados_fora_de_V1_uniao_V2": int(len(listados - v12)),
        "municipios_de_V1_uniao_V2_nunca_listados": int(len(v12 - listados)),
        "regra": "se a listagem fosse completa em todos os meses, ausencia de linha seria zero em U (todos os "
                 "municipios do a08); como nao e, cada mes usa so os municipios listados naquele mes; a queda usa "
                 "zero no ultimo mes para quem nao esta listado nele so porque o ultimo mes reproduz o retrato",
    }
    for df in (painel_mc, pm, mun3, comp_tab):
        df.insert(0, "estatuto", ESTATUTO)
        df.insert(0, "natureza_dos_dados", NATUREZA)

    # ------------------------------ Gravação -------------------------------
    saidas = {
        "X2_pessoas.csv": pessoas_out, "X2_celulas.csv": celulas, "X2_municipios.csv": municipios,
        "X2_descritivo.csv": desc_x2, "X2_motivos_ligacao.csv": motivos, "X2_estimativas.csv": est_x2,
        "X3_painel_municipio_curso_mes.csv": painel_mc, "X3_painel_municipio_mes.csv": pm,
        "X3_municipio.csv": mun3, "X3_completude.csv": comp_tab, "X3_descritivo.csv": desc_x3,
        "X3_estimativas.csv": est_x3,
    }
    for nome, df in saidas.items():
        gravar_csv(df, OUT / nome)
    hashes = {nome: sha256(OUT / nome) for nome in saidas}
    entradas_comuns = [
        bloco_entrada(A08, "running variable (IVS 2010 oficial)", "Censo 2010 (Plataforma IVS)",
                      f"{len(rv)} municipios", "municipio", "co_ibge", "nenhum"),
        bloco_entrada(POP22, "populacao (X3 por 10 mil hab.)", "Censo 2022", "municipios do Censo 2022", "municipio",
                      "co_ibge_6d", "nenhum"),
        bloco_entrada(ARQ_VC, "celulas do quadro da 1a chamada (V1, V2) e contagens da tarefa B para conferencia",
                      "quadros da 1a chamada (ciclo 1 jul/2025; ciclo 2 retificado 19/03/2026)", "ciclos 1 e 2",
                      "celula CNES x curso x ciclo", "ciclo, co_cnes_7d, cod_curso", "ciclo em {1, 2}"),
        bloco_entrada(ATIVOS_ZIP, "relacao nominal de ativos (retrato principal)", "publicada 09/10/2026; "
                      "dt_referencia " + ";".join(sorted(at["set"]["dt_referencia"].unique())), "ciclos 1 a 3",
                      "profissional ativo", "nome normalizado + curso + municipio (so em memoria); CRM entre retratos",
                      "todas as linhas; nome e CRM nao gravados"),
        bloco_entrada(NOMINAL_CSV, "retrato nominal anterior (X2 descritivo; X3 conferencia de completude)",
                      "dt_referencia " + ";".join(sorted(at["ago"]["dt_referencia"].unique())), "ciclos 1 e 2",
                      "profissional ativo", "nome normalizado + curso + municipio; CRM", "nome e CRM nao gravados"),
    ]
    resumo_x2 = {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "x_id": "X2", "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)), "protocolo": "docs/06_execucao/45_protocolo_exploratorio_pos_sintese.md, "
                                                       "secao 3 (X2)",
        "contraste": CONTRASTE, "h_mil": H, "cortes_mil": list(CORTES), "limiar_grafia": LIMIAR_GRAFIA,
        "regra_de_ligacao": [
            "arquivos de resultado sem coluna CRM (conferido no cabecalho): ligacao por nome normalizado (maiusculas, "
            "sem acento, so alfanumericos) + codigo do curso + municipio (do quadro pela celula)",
            "LIGADO: chave exata e unica entre alocados e entre ativos; mesmo ativo ligado a dois alocados -> AMBIGUO",
            "INCERTO: sem chave exata, ativo nao ligado no mesmo curso e municipio com similaridade de nome >= "
            "limiar_grafia (difflib.SequenceMatcher) ou com o mesmo primeiro nome e ao menos 2 partes do nome em "
            "comum (criterio de partes acrescentado depois de um diagnostico de quase-correspondencias e antes de "
            "qualquer estimativa RDD ser aberta)",
            "NAO_LIGADO: motivo = nome e curso em outro municipio / nome em outro curso / sem correspondente",
            "AMBIGUO e INCERTO ficam fora do outcome (NaN com motivo)",
        ],
        "ordem_de_execucao": [
            "1a execucao com a regra estreita (INCERTO so por similaridade): impressos as taxas de ligacao, os motivos "
            "e a tabela descritiva de permanencia por ciclo e faixa",
            "diagnostico de quase-correspondencias (nomes com o mesmo 1o nome e partes em comum, sem chave exata); "
            "o criterio de partes foi acrescentado DEPOIS de vista a tabela de permanencia por faixa da regra "
            "estreita e ANTES de abrir qualquer estimativa RDD",
            "as duas regras sao relatadas: regra_ligacao nas saidas (estreita fora do BKY)",
            "auditoria independente (19/10/2026): rotulos de adicao ao protocolo (X2.3, X2.4 e especificacoes "
            "empilhadas) e de condicionamento acrescentados sem mudar estimativa",
        ],
        "horizonte_por_ciclo": horizonte,
        "eventos_de_alocacao": diag_ev, "conferencia_contra_tarefa_b": conf_b, "pessoas": diag_p,
        "conferencia_selecao": conf_sel,
        "ligacao_por_ciclo": {
            f"ciclo_{k}": {"retrato_11_09_2026": g["status_ligacao"].value_counts().to_dict(),
                           "retrato_12_08_2026": g["status_ligacao_ago"].value_counts().to_dict(),
                           "taxa_ligacao_11_09_2026": float((g["status_ligacao"] == "LIGADO").mean()),
                           "ligados_com_mesmo_cnes": int(g["cnes_igual"].sum()),
                           "ligados_com_ciclo_do_ativo_igual": int(g["ciclo_igual"].sum())}
            for k, g in pessoas.groupby("ciclo")},
        "cobertura_dos_ativos_do_retrato": cobertura_ativos,
        "crm_entre_retratos": crm,
        "selecao_lee": "celula (ou municipio) com ao menos um alocado determinado (LIGADO ou NAO_LIGADO); celulas so "
                       "com alocados AMBIGUO/INCERTO saem da amostra da RDD (contagem em celulas_so_excluidos)",
        "celulas_so_excluidos": int(celulas["so_excluidos"].sum()),
        "especificacoes": sorted(est_x2["especificacao"].unique().tolist()),
        "n_linhas_bky": int(est_x2["entra_bky"].sum()),
        "dados_pessoais_gravados": "nenhum: id_pessoa e pseudonimo deterministico (ordem de hash); sem nome, CPF ou CRM",
        "entradas": entradas_comuns + [
            bloco_entrada(ALOC_C1, "alocados ciclo 1 (confirmacao de local)", "alocacao retificada sub judice, "
                          "1a chamada ciclo 1", "ciclo 1", "candidato x opcao", "CNES, CURSO, nome (memoria)",
                          "ALOCACAO comeca com LOCAL DE ATUACAO CONFIRMADO"),
            bloco_entrada(HOMOLOG_C1, "homologados ciclo 1, 1a chamada", "lista de homologados da 1a chamada",
                          "ciclo 1", "pessoa homologada", "CNES, CURSO, nome (memoria)", "RESULTADO = HOMOLOGADO"),
            bloco_entrada(RESULT_C2, "alocados ciclo 2, 1a chamada", "resultado final 1a chamada ciclo 2 (25/05)",
                          "ciclo 2", "candidato x opcao", "CNES, CURSO, nome (memoria)",
                          "aba Classificados; SITUACAO comeca com ALOCADO"),
        ],
        "saidas": {k: v for k, v in hashes.items() if k.startswith("X2_")},
        "linguagem": "exploratorio pos-resultado; permanencia no municipio de alocacao no retrato, nao retencao "
                     "individual completa (saida antes do retrato e retorno nao sao observados separadamente)",
    }
    resumo_x3 = {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "x_id": "X3", "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)), "protocolo": "docs/06_execucao/45_protocolo_exploratorio_pos_sintese.md, "
                                                       "secao 3 (X3)",
        "contraste": CONTRASTE, "h_mil": H, "cortes_mil": list(CORTES),
        "serie": diag_serie, "completude": comp, "populacao": diag_pop_x3, "populacao_estimacao_mensal": pop_desc,
        "colunas_nao_usadas": "ivs e faixa_atracao do arquivo (rotulos inconsistentes); municipio, uf, regiao e "
                              "regiao_saude; co_cnes e estabelecimento (vazios)",
        "especificacoes": sorted(est_x3["especificacao"].unique().tolist()),
        "ordem_de_execucao": [
            "conferencia de completude e outcomes do protocolo; impressos o descritivo mensal e o descritivo da queda "
            "por faixa",
            "diagnostico da redistribuicao em mai/26 e jun/26 (municipios da cota ausentes e capitais acima dos "
            "meses vizinhos); a sensibilidade x3s (pico so nos meses sem municipio da cota ausente) foi definida "
            "DEPOIS de impresso o descritivo da queda por faixa e ANTES de abrir qualquer estimativa X3",
            "x3s exclui 6 dos 9 meses, nao so mai/26 e jun/26; a variante x3m (exclui so mai/26 e jun/26) foi pedida "
            "pela auditoria independente de 19/10/2026, depois de vistos os resultados X3",
            "rotulos de condicionamento (listagem e pico pos-tratamento, sem Lee) e de adicao ao protocolo "
            "acrescentados na mesma auditoria sem mudar estimativa",
        ],
        "meses_excluidos_na_variante_x3m": list(MESES_EXCLUIDOS_AUDITORIA),
        "horizonte_por_ciclo": horizonte,
        "nota_horizonte": "municipios do ciclo 1 tem seguimento mais longo que os do ciclo 2; a queda do pico e as RDD "
                          "mensais misturam os dois horizontes",
        "n_linhas_bky": int(est_x3["entra_bky"].sum()),
        "entradas": entradas_comuns[:2] + [
            bloco_entrada(SERIE_CSV, "serie historica de ativos", "competencias dez/25 a ago/26",
                          "municipios com linha no mes", "municipio x curso x mes (linhas por estabelecimento vazio)",
                          "co_ibge, codigo do curso, competencia", "nenhum; soma de qtd_ativos por chave"),
            entradas_comuns[4],
            bloco_entrada(ARQ_VC, "V1 uniao V2 (diagnostico de cobertura)", "quadros da 1a chamada", "ciclos 1 e 2",
                          "celula", "co_ibge", "ciclo em {1, 2}"),
        ],
        "saidas": {k: v for k, v in hashes.items() if k.startswith("X3_")},
        "linguagem": "exploratorio pos-resultado; descritivo da serie e RDD por mes sem pre-periodo",
    }
    gravar_json(OUT / "X2_resumo.json", resumo_x2)
    gravar_json(OUT / "X3_resumo.json", resumo_x3)
    return {"X2": resumo_x2, "X3": resumo_x3}


# ---------------------------------------------------------------------------
# Tabelas do doc 46 (geradas das saídas)
# ---------------------------------------------------------------------------

def _n(v, casas: int = 3) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)) or pd.isna(v):
        return "—"
    return f"{float(v):.{casas}f}".replace(".", ",").replace("-", "−")


def _pct(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{100 * float(v):.1f}%".replace(".", ",")


def _int(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{int(v)}"


def _ic(a, b, casas: int = 3) -> str:
    return f"[{_n(a, casas)}; {_n(b, casas)}]"


def _prot(r) -> str:
    return "sim" if str(r.no_protocolo_45) == "True" else "adição"


def _tabela_desc_x2(d: pd.DataFrame) -> str:
    cab = ("| Ciclo | Subgrupo | Faixa | Alocados | Ligados | Não ligados | Ambíguos | Incertos | Ligação | Permanência "
           "(11/09) | Incertos como ativos | Incertos como saídos | Permanência (12/08) | Presença no programa |\n"
           "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
    linhas = [f"| {int(r.ciclo)} | {r.subgrupo} | {r.faixa} | {_int(r.n_alocados)} | {_int(r.n_ligados)} | "
              f"{_int(r.n_nao_ligados)} | {_int(r.n_ambiguos)} | {_int(r.n_incertos)} | {_pct(r.taxa_ligacao)} | "
              f"{_pct(r.permanencia_set)} | {_pct(r.permanencia_set_incertos_como_ativos)} | "
              f"{_pct(r.permanencia_set_incertos_como_saidos)} | {_pct(r.permanencia_ago)} | "
              f"{_pct(r.presenca_no_programa_set)} |" for r in d.itertuples()]
    return cab + "\n".join(linhas)


def gerar_tabelas_doc(dados: dict) -> dict[str, str]:
    d2, m2, e2, r2 = dados["X2_descritivo"], dados["X2_motivos_ligacao"], dados["X2_estimativas"], dados["X2_resumo"]
    d3, c3, e3, r3 = dados["X3_descritivo"], dados["X3_completude"], dados["X3_estimativas"], dados["X3_resumo"]
    d2a, d2e = d2[d2["regra_ligacao"] == REGRA_AMPLA], d2[d2["regra_ligacao"] == REGRA_ESTREITA]
    e2a, e2e = e2[e2["regra_ligacao"] == REGRA_AMPLA], e2[e2["regra_ligacao"] == REGRA_ESTREITA]
    t = {}
    # X2: ligação.
    cab = "| Ciclo | Retrato | Status | Motivo | Alocados |\n|---|---|---|---|---:|\n"
    linhas = [f"| {int(r.ciclo)} | {r.retrato} | {r.status_ligacao} | {r.motivo_ligacao} | {_int(r.n)} |"
              for r in m2.sort_values(["ciclo", "retrato", "status_ligacao", "motivo_ligacao"],
                                      ascending=[True, False, True, True]).itertuples()]
    t["ligacao"] = cab + "\n".join(linhas)
    crm = r2["crm_entre_retratos"]
    t["crm"] = ("| Medida | Pessoas |\n|---|---:|\n"
                + "\n".join(f"| {k.replace('_', ' ')} | {_int(v)} |" for k, v in crm.items() if k != "nota"))
    t["descritivo"] = _tabela_desc_x2(d2a)
    t["descritivo_estreita"] = _tabela_desc_x2(d2e[d2e["subgrupo"] == "todos"])
    cab = ("| Outcome | Ciclo | Corte | Especificação | Protocolo | τ | IC 95% | p | q BKY | q BKY só protocolo | "
           "Lee [inf; sup] | IC 95% Lee | n abaixo/acima |\n|---|---|---|---|---|---:|---|---:|---:|---:|---|---|---|\n")
    linhas = []
    for oid, g in e2a.groupby("outcome_id", sort=True):
        for r in g.itertuples():
            if r.status == "NAO_EXECUTADO":
                continue
            lee = r.especificacao == "limites_lee"
            linhas.append(
                f"| {oid} | {r.ciclo} | {r.corte} | {r.especificacao} | {_prot(r)} | {_n(r.tau)} | "
                f"{'—' if lee else _ic(r.ic95_inf, r.ic95_sup)} | {'—' if lee else _n(r.p_valor)} | "
                f"{'—' if lee else _n(r.q_bky)} | {'—' if lee else _n(r.q_bky_so_protocolo)} | "
                f"{_ic(r.lee_tau_inf, r.lee_tau_sup) if lee else '—'} | "
                f"{_ic(r.lee_ic95_inf, r.lee_ic95_sup) if lee else '—'} | {_int(r.n_abaixo)}/{_int(r.n_acima)} |")
    t["estimativas"] = cab + "\n".join(linhas)
    chave = ["outcome_id", "ciclo", "corte", "especificacao"]
    cmp_ = e2a[e2a["status"] != "NAO_EXECUTADO"].merge(e2e, on=chave, suffixes=("_a", "_e"))
    cab = ("| Outcome | Ciclo | Corte | Especificação | τ ampla | τ estreita | p ampla | p estreita | Lee ampla | "
           "Lee estreita |\n|---|---|---|---|---:|---:|---:|---:|---|---|\n")
    linhas = []
    for r in cmp_.itertuples():
        lee = r.especificacao == "limites_lee"
        linhas.append(f"| {r.outcome_id} | {r.ciclo} | {r.corte} | {r.especificacao} | {_n(r.tau_a)} | {_n(r.tau_e)} | "
                      f"{'—' if lee else _n(r.p_valor_a)} | {'—' if lee else _n(r.p_valor_e)} | "
                      f"{_ic(r.lee_tau_inf_a, r.lee_tau_sup_a) if lee else '—'} | "
                      f"{_ic(r.lee_tau_inf_e, r.lee_tau_sup_e) if lee else '—'} |")
    t["estimativas_estreita"] = cab + "\n".join(linhas)
    # X3.
    cab = ("| Mês | Municípios listados | Células município × curso | Ativos na série | Cota inferior do retrato | "
           "Células com violação | Déficit | Municípios da cota ausentes | Municípios acima dos meses vizinhos | "
           "Excesso |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
    linhas = [f"| {r.mes} | {_int(r.municipios_listados)} | {_int(r.celulas_municipio_curso_listadas)} | "
              f"{_int(r.ativos_na_serie)} | {_int(r.cota_inferior_do_retrato)} | {_int(r.celulas_com_violacao)} | "
              f"{_int(r.deficit_de_ativos)} | {_int(r.municipios_da_cota_ausentes_da_listagem)} | "
              f"{_int(r.municipios_acima_do_maximo_dos_meses_vizinhos)} | "
              f"{_int(r.excesso_sobre_o_maximo_dos_meses_vizinhos)} |" for r in c3.itertuples()]
    t["completude"] = cab + "\n".join(linhas)
    mens = d3[d3["mes"] != "queda"]
    faixas = [f for f in ("FAIXA 3", "FAIXA 2", "FAIXA 1", "TOTAL") if f in set(mens["faixa"])]
    cab = ("| Mês | " + " | ".join(f"{f}: municípios / ativos / média por 10 mil" for f in faixas) + " |\n|---|"
           + "---|" * len(faixas) + "\n")
    linhas = []
    for mes, g in mens.groupby("mes", sort=True):
        g = g.set_index("faixa")
        cel = [f"{_int(g.at[f, 'municipios_listados'])} / {_int(g.at[f, 'ativos'])} / "
               f"{_n(g.at[f, 'media_ativos_por_10k'])}" if f in g.index else "—" for f in faixas]
        linhas.append(f"| {mes} | " + " | ".join(cel) + " |")
    t["descritivo_mensal"] = cab + "\n".join(linhas)
    q = d3[d3["mes"] == "queda"]
    cab = ("| Faixa | Municípios com ativo em algum mês | Com ativo no último mês | Queda média (ativos) | "
           "Queda média por 10 mil | Fração com queda | Queda relativa média | Meses com ativo (média) | "
           "Queda média (meses sem ausência) | Queda relativa média (meses sem ausência) | "
           "Queda média (sem mai/jun) | Queda relativa média (sem mai/jun) |\n"
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
    linhas = [f"| {r.faixa} | {_int(r.municipios_listados)} | {_int(r.municipios_com_ativo)} | "
              f"{_n(r.media_ativos_por_municipio_listado)} | {_n(r.media_ativos_por_10k)} | {_pct(r.fracao_com_queda)} | "
              f"{_pct(r.queda_relativa_media)} | {_n(r.meses_com_ativo_media, 2)} | {_n(r.queda_media_sensibilidade)} | "
              f"{_pct(r.queda_relativa_media_sensibilidade)} | {_n(r.queda_media_sem_mai_jun)} | "
              f"{_pct(r.queda_relativa_media_sem_mai_jun)} |" for r in q.itertuples()]
    t["descritivo_queda"] = cab + "\n".join(linhas)
    cab = ("| Outcome | Mês | Corte | Especificação | Protocolo | τ | IC 95% | p | q BKY | q BKY só protocolo | "
           "n abaixo/acima |\n|---|---|---|---|---|---:|---|---:|---:|---:|---|\n")
    linhas = [f"| {r.outcome_id} | {r.mes} | {r.corte} | {r.especificacao} | {_prot(r)} | {_n(r.tau)} | "
              f"{_ic(r.ic95_inf, r.ic95_sup)} | {_n(r.p_valor)} | {_n(r.q_bky)} | {_n(r.q_bky_so_protocolo)} | "
              f"{_int(r.n_abaixo)}/{_int(r.n_acima)} |"
              for r in e3.sort_values(["outcome_id", "mes", "corte"]).itertuples()]
    t["x3_estimativas"] = cab + "\n".join(linhas)
    t["x2_leitura"] = leitura_x2(d2a, d2e, e2a, e2e, r2)
    t["x3_leitura"] = leitura_x3(e3, r3)
    return t


def _p_menor(est: pd.DataFrame, limite: float) -> pd.DataFrame:
    return est[est["p_valor"].notna() & (est["p_valor"] < limite)]


def _horizontes(r: dict, chave: str) -> str:
    h = r["horizonte_por_ciclo"]
    return "; ".join(f"{k.replace('_', ' ')}: {_n(v.get(chave), 1)} meses" for k, v in sorted(h.items())
                     if v.get(chave) is not None)


def leitura_x2(d2a: pd.DataFrame, d2e: pd.DataFrame, e2a: pd.DataFrame, e2e: pd.DataFrame, r2: dict) -> str:
    """Frases com os números-chave do X2, geradas das saídas."""
    tot = d2a[(d2a["faixa"] == "TOTAL") & (d2a["subgrupo"] == "todos")].set_index("ciclo")
    tot_e = d2e[(d2e["faixa"] == "TOTAL") & (d2e["subgrupo"] == "todos")].set_index("ciclo")
    sub = d2a[(d2a["faixa"] == "TOTAL") & (d2a["ciclo"] == 1)].set_index("subgrupo")
    itens = []
    for k, r in tot.iterrows():
        itens.append(f"- Ciclo {k}: {_int(r['n_alocados'])} alocados da 1ª chamada; {_pct(r['taxa_ligacao'])} ligados "
                     f"a um ativo no município de alocação em 11/09/2026; permanência entre os determinados "
                     f"{_pct(r['permanencia_set'])} (12/08/2026: {_pct(r['permanencia_ago'])}); com a regra estreita, "
                     f"{_int(tot_e.at[k, 'n_incertos'])} incertos (ampla: {_int(r['n_incertos'])}) e permanência "
                     f"{_pct(tot_e.at[k, 'permanencia_set'])}.")
    if {"homologacao", "confirmacao"} <= set(sub.index):
        itens.append(f"- Ciclo 1 por evento final: permanência {_pct(sub.at['homologacao', 'permanencia_set'])} entre "
                     f"os homologados e {_pct(sub.at['confirmacao', 'permanencia_set'])} entre os que só tiveram o "
                     f"local confirmado.")
    itens.append(f"- Horizonte mediano do início de atividade ao retrato de 11/09/2026, entre os ligados: "
                 f"{_horizontes(r2, 'x2_mediana_meses_inicio_ate_retrato_set')}.")
    crm = r2["crm_entre_retratos"]
    itens.append(f"- CRM entre os dois retratos: {_int(crm['ligados_nos_dois_com_mesmo_crm'])} de "
                 f"{_int(crm['ligados_nos_dois_retratos'])} pessoas ligadas nos dois têm o mesmo CRM.")
    for nome, e in (("regra ampla", e2a), ("regra estreita", e2e)):
        rd = e[(e["especificacao"] != "limites_lee") & e["p_valor"].notna()]
        prot = rd[rd["no_protocolo_45"].astype(str) == "True"]
        lee = e[(e["especificacao"] == "limites_lee") & (e["status"] == "EXECUTADO")]
        cobre = ((lee["lee_ic95_inf"] <= 0) & (lee["lee_ic95_sup"] >= 0)).sum()
        q = (f"; menor q de BKY = {_n(rd['q_bky'].min())} (só protocolo: {_n(rd['q_bky_so_protocolo'].min())})"
             if rd["q_bky"].notna().any() else "; fora do BKY")
        itens.append(f"- RDD, {nome}: {_int(len(rd))} estimativas com p ({_int(len(prot))} do protocolo); "
                     f"{_int(len(_p_menor(rd, 0.05)))} com p < 0,05{q}; {_int(cobre)} de {_int(len(lee))} ICs de Lee "
                     f"contêm zero.")
    return "\n".join(itens)


def leitura_x3(e3: pd.DataFrame, r3: dict) -> str:
    """Frases com os números-chave do X3, geradas das saídas."""
    c = r3["completude"]
    n_meses = len(r3["serie"]["meses"])
    itens = [
        f"- Último mês ({c['ultimo_mes']}) reproduz o retrato nominal por município × curso: "
        f"{'sim' if c['ultimo_mes_reproduz_retrato_nominal'] else 'não'}.",
        f"- Listagem completa em todos os meses: {'sim' if c['listagem_completa_em_todos_os_meses'] else 'não'}; "
        f"meses que falham a cota inferior: {', '.join(c['meses_com_violacao']) or 'nenhum'}; meses sem município "
        f"da cota ausente: {', '.join(c['meses_sem_municipio_da_cota_ausente'])}.",
        f"- População de estimação mensal: {r3['populacao_estimacao_mensal']}.",
        f"- Horizonte mediano do início de atividade ao retrato de 12/08/2026, por ciclo do ativo: "
        f"{_horizontes(r3, 'x3_mediana_meses_inicio_ate_retrato_ago')}.",
    ]
    n_s = len(c["meses_sem_municipio_da_cota_ausente"])
    grupos = (("especificações por corte do protocolo (§3)", e3[e3["especificacao"] == "principal"]),
              ("cortes empilhados (adição)", e3[e3["especificacao"] == "cortes_empilhados"]),
              (f"sensibilidade de meses sem ausência (pico em {n_s} dos {n_meses} meses: "
               f"{', '.join(c['meses_sem_municipio_da_cota_ausente'])})",
               e3[e3["especificacao"].str.startswith("sensibilidade_meses_sem_ausencia")]),
              (f"variante sem {', '.join(r3['meses_excluidos_na_variante_x3m'])} (pico em "
               f"{n_meses - len(r3['meses_excluidos_na_variante_x3m'])} dos {n_meses} meses; pedido da auditoria)",
               e3[e3["especificacao"].str.startswith("sensibilidade_sem_mai_jun")]))
    for nome, d in grupos:
        sig = _p_menor(d, 0.05)
        lista = "; ".join(f"{r.outcome_id} {r.mes} {r.corte} (τ = {_n(r.tau)}, p = {_n(r.p_valor)}, "
                          f"q = {_n(r.q_bky)})" for r in sig.itertuples()) or "nenhuma"
        itens.append(f"- {nome[0].upper() + nome[1:]}: {_int(len(d[d['p_valor'].notna()]))} estimativas com p; "
                     f"com p < 0,05: {lista}.")
    itens.append(f"- Menor q de BKY no X3: {_n(e3['q_bky'].min())} (só protocolo: "
                 f"{_n(e3['q_bky_so_protocolo'].min())}).")
    return "\n".join(itens)


MARCA = re.compile(r"(<!-- (?P<x>X[23]):(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)"
                   r"(<!-- (?P=x):(?P=nome):fim -->)", re.S)
MAPA_MARCAS = {("X2", "ligacao"): "ligacao", ("X2", "crm"): "crm", ("X2", "descritivo"): "descritivo",
               ("X2", "estimativas"): "estimativas", ("X3", "completude"): "completude",
               ("X3", "descritivo_mensal"): "descritivo_mensal", ("X3", "descritivo_queda"): "descritivo_queda",
               ("X3", "estimativas"): "x3_estimativas", ("X2", "leitura"): "x2_leitura",
               ("X3", "leitura"): "x3_leitura", ("X2", "descritivo_estreita"): "descritivo_estreita",
               ("X2", "estimativas_estreita"): "estimativas_estreita"}


def aplicar_tabelas_doc(texto: str, tabelas: dict[str, str]) -> str:
    def sub(m):
        chave = MAPA_MARCAS[(m.group("x"), m.group("nome"))]
        return m.group(1) + tabelas[chave] + "\n" + m.group(5)
    return MARCA.sub(sub, texto)


def tabelas_no_doc(texto: str) -> dict[tuple[str, str], str]:
    return {(m.group("x"), m.group("nome")): m.group("corpo").removesuffix("\n") for m in MARCA.finditer(texto)}


def ler_saidas() -> dict:
    d = {}
    for nome in ("X2_descritivo", "X2_motivos_ligacao", "X2_estimativas", "X3_descritivo", "X3_completude",
                 "X3_estimativas"):
        d[nome] = pd.read_csv(OUT / f"{nome}.csv", dtype={"ciclo": str, "corte": str, "mes": str})
    d["X2_descritivo"]["ciclo"] = d["X2_descritivo"]["ciclo"].astype(int)
    d["X2_motivos_ligacao"]["ciclo"] = d["X2_motivos_ligacao"]["ciclo"].astype(int)
    for nome in ("X2_resumo", "X3_resumo"):
        d[nome] = json.loads((OUT / f"{nome}.json").read_text(encoding="utf-8"))
    return d


def atualizar_doc() -> None:
    texto = DOC46.read_text(encoding="utf-8")
    novo = aplicar_tabelas_doc(texto, gerar_tabelas_doc(ler_saidas()))
    DOC46.write_text(novo, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava as tabelas do doc 46 a partir das saídas")
    args = ap.parse_args(argv)
    if not args.atualizar_doc:
        res = executar()
        for x, r in res.items():
            print(f"{x}: {len(r['saidas'])} saidas gravadas; linhas no BKY = {r['n_linhas_bky']}")
    if DOC46.exists():
        atualizar_doc()
        print(f"tabelas X2/X3 regravadas em {rotulo(DOC46)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
