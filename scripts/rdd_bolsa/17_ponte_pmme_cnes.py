"""X1 do protocolo exploratório pós-síntese: ponte PMM-E–CNES pelo registro profissional.

Protocolo: `docs/06_execucao/45_protocolo_exploratorio_pos_sintese.md`, §2 (regras)
e §3 (X1), congelado em 19/10/2026 antes de abrir os outcomes. Estatuto de toda
saída: ``EXPLORATORIO_POS_SINTESE``. Nada aqui é teste confirmatório, nem muda o
protocolo 40, os resultados E3–E9 ou o Holm das primárias.

Pergunta
--------
O especialista do PMM-E já estava no estabelecimento ou no município antes de
entrar? De onde veio (proposta A da síntese, doc 44 §7: substituição e
remanejamento contra entrada líquida; proposta B: distância)?

Ligação (doc 45, §3)
--------------------
- Lado PMM-E: relação nominal de ativos (``tb_profissionais_ativos_pmme``,
  retrato de 11/09/2026, a mesma do E3/E6) e lista nominal de 12/08/2026
  (``data/pmm_especialistas_nominal.csv``). Registros só da lista de agosto entram
  com ``fonte_lista`` próprio. Campos: CRM, UF, CNES do estabelecimento,
  município, curso, data de início, ciclo e nome (o nome só em memória).
  A UF da lista é a do posto do PMM-E; a lista não traz a UF do CRM.
- Lado CNES: competências públicas 202406, 202501, 202506, 202510, 202602 e
  202608 (``BASE_DE_DADOS_CNES_AAAAMM.ZIP``). De ``tbCargaHorariaSus`` saem os
  vínculos médicos (CBO 2251, 2252, 2253 e 2231, os prefixos do a09) com
  ``CO_CONSELHO_CLASSE``, ``NU_REGISTRO`` e ``SG_UF_CRM``; de
  ``tbEstabelecimento``, CNES, município e região de saúde do estabelecimento;
  de ``tbDadosProfissionalSus``, o nome, só dos profissionais cujo registro é um
  CRM das listas do PMM-E.
- Regra, em ordem: (1) CRM + UF exatos (``NU_REGISTRO`` = CRM e ``SG_UF_CRM`` =
  UF do posto) com um único profissional (``CO_PROFISSIONAL_SUS``) nas seis
  competências; (2) sem (1), CRM exato em qualquer UF com nome compatível, com
  um único profissional; (3) ambíguos (mais de um profissional) e não achados
  ficam fora, com o motivo. Só entram na busca vínculos com
  ``CO_CONSELHO_CLASSE`` do CRM (código lido da ``tbConselhoClasse``).
- Duas regras, lado a lado em todas as saídas (coluna ``regra_ligacao``):
  ``literal_doc45`` é a regra do protocolo congelado; ``d1_pos_hoc`` é a correção
  D1, decidida depois da primeira execução completa (a UF das listas é a do
  posto, não a do CRM; na etapa 1, o candidato único só liga com nome
  compatível). O q de BKY é calculado dentro de cada regra.
- Nome compatível (fixado antes de ligar): nomes normalizados (maiúsculas, sem
  acento, sem partículas DE/DA/DO/DAS/DOS/E/D/DI/DU) com o mesmo primeiro nome e
  o mesmo último sobrenome, ou com o mesmo primeiro nome e o conjunto de nomes
  de um contido no do outro.

Outcomes por médico (ciclos 1 e 2)
----------------------------------
Mês de início = AAAAMM de ``dt_inicio_atividade``. Competências pré-início = as
lidas estritamente anteriores ao mês de início; a última delas é a de
referência. Um vínculo médico conta se tem CBO médica.
- (a) vínculo no mesmo estabelecimento (CNES do posto) na última competência
  pré-início; variante: em alguma competência pré-início;
- (b) vínculo no mesmo município do posto, idem; também em meses fixos iguais
  para todos (202406, 202501, 202506) e a persistência dos incumbentes (dos que
  têm (b) na última competência pré-início, quantos já o tinham em 202406);
- (c) origem na última competência pré-início, pela ligação mais próxima:
  ``mesmo_municipio`` > ``mesma_regiao_saude`` > ``mesma_uf`` > ``outra_uf``;
  sem vínculo médico nessa competência: ``sem_vinculo_medico_anterior``;
- (d) distância em km (círculo máximo entre centroides oficiais do IBGE, API de
  malhas v3) do município de origem mais próximo ao do posto; ausente sem
  vínculo pré-início;
- (e) vínculos médicos simultâneos (linhas de ``tbCargaHorariaSus``) na
  competência 202608, para quem começou antes de 202608; também o número de
  estabelecimentos e se há vínculo no estabelecimento do posto (conferência).

Análises
--------
- Descritivo por ciclo e faixa.
- RDD nos cortes, por município de V_k (célula no quadro da 1ª chamada do ciclo
  k), condicional a ter ≥ 1 médico ativo ligado: fração de médicos novos no
  município (1 − (b)), fração de outra UF e distância média (entre os médicos
  com vínculo pré-início). Local linear, h = 0,050, kernel triangular, HC1, por
  corte e ciclo; cortes empilhados por ciclo e ciclos e cortes empilhados (CR1
  por município). Como o outcome existe só onde há médico ligado, cada
  corte × ciclo tem limites de Lee com seleção = ter ≥ 1 médico ligado (o que
  combina preencher a célula, estar ativo no retrato e ligar ao CNES).
- E9 com distância (sensibilidade): candidatos alocados na 1ª chamada ligados
  pelo nome e pela célula a um médico ativo ligado ao CNES com vínculo
  pré-início; logit condicional da 1ª opção com os atributos do E9 principal e
  a distância de cada célula ao município de origem mais próximo dela (mínimo
  sobre todos os municípios com vínculo médico na última competência
  pré-início; independe da célula escolhida). Amostra selecionada (alocados,
  ativos, ligados, com origem): sensibilidade, não estimativa do efeito da
  distância sobre todos os candidatos.
- q de BKY dentro do X1 (todas as linhas com p), uma família por regra.

Uso
---
``python3 scripts/rdd_bolsa/17_ponte_pmme_cnes.py`` (padrão ``--etapa analise``)
lê o cache das seis competências e as entradas locais, sem rede.
``--etapa aquisicao`` baixa (ou reaproveita ZIP íntegro em ``data/raw/cnes/``),
extrai, valida e apaga os ZIPs; baixa também as coordenadas do IBGE se ausentes.
``--etapa tudo`` faz as duas. ``--atualizar-doc`` reescreve só os blocos
``<!-- X1:... -->`` do doc 46 a partir das saídas.

Integridade: nada é simulado, imputado ou digitado. O que falta fica ausente,
com o motivo. As constantes são parâmetros do protocolo (competências, cortes,
h, limite do ciclo 3) e de definição (prefixos de CBO, partículas do nome, raio
da Terra). Saídas sem nome, CPF, CNS, CRM nem código de profissional: o médico
tem pseudônimo determinístico (ordem do SHA-256 de ciclo, CRM, UF, CNES e
curso, calculado só em memória). O pseudônimo é fraco: ciclo, município e faixa,
cruzados com a lista nominal pública e com o CNES, podem reidentificar o médico;
por isso o parquet não traz mês de início nem curso.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import importlib.util
import io
import json
import math
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "rdd_bolsa"))
import rdd_lib as L  # noqa: E402


def _importar(nome: str, caminho: Path):
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


SCRIPT_A09 = ROOT / "scripts" / "aquisicao" / "a09_adquirir_cnes_nacional.py"
SCRIPT_12 = ROOT / "scripts" / "rdd_bolsa" / "12_construir_outcomes_funil.py"
SCRIPT_16 = ROOT / "scripts" / "rdd_bolsa" / "16_estimar_E9_escolha.py"

# ---------------------------------------------------------------- caminhos
ATIVOS_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
PPF_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "ppf_mais_medicos_csv.zip"
NOMINAL_CSV = ROOT / "data" / "pmm_especialistas_nominal.csv"
IVS_OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
MANIFESTO_A09 = ROOT / "output" / "aquisicao" / "a09_manifesto_cnes_nacional.json"
V_MUNICIPIO = ROOT / "output" / "rdd_bolsa" / "outcomes" / "outcomes_V_municipio.parquet"
ESCOLHAS = ROOT / "output" / "rdd_bolsa" / "outcomes" / "escolhas_candidatos.parquet"
CONJ_PRINCIPAL = ROOT / "output" / "rdd_bolsa" / "outcomes" / "escolhas_conjunto_principal.parquet"
PROTOCOLO_45 = ROOT / "docs" / "06_execucao" / "45_protocolo_exploratorio_pos_sintese.md"
COORD_JSON = ROOT / "data" / "raw" / "aquisicao" / "territorio" / "ibge_api_v3_malhas_metadados_municipios.json"
COORD_URL = "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR/metadados?intrarregiao=municipio"
COORD_MANIFESTO = COORD_JSON.with_suffix(".manifesto.json")

CACHE_DIR = ROOT / "output" / "rdd_bolsa" / "X1_cache"  # ignorado pelo Git (registro profissional e nome)
OUT_DIR = ROOT / "output" / "rdd_bolsa"
OUT_RESUMO = OUT_DIR / "X1_ligacao_resumo.json"
OUT_MEDICOS = OUT_DIR / "X1_medicos.parquet"
OUT_ESTIMATIVAS = OUT_DIR / "X1_estimativas.csv"
OUT_DESCRITIVO = OUT_DIR / "X1_descritivo.csv"
DOC_46 = ROOT / "docs" / "06_execucao" / "46_resultados_exploratorios_pos_sintese.md"

# ---------------------------------------------------------------- parâmetros do protocolo
NATUREZA = "EMPIRICO"
ESTATUTO = "EXPLORATORIO_POS_SINTESE"
COMPETENCIAS = ("202406", "202501", "202506", "202510", "202602", "202608")
LIMITE_EXCLUSIVO = "202609"  # ciclo 3: nada a partir daqui é baixado ou lido
assert all(c < LIMITE_EXCLUSIVO for c in COMPETENCIAS)
COMPETENCIA_POS = "202608"  # (e): vínculos simultâneos depois do início
# Pedido da auditoria de X1: "no mesmo município" em meses fixos, iguais para todos (pré-início dos ciclos 1-2).
MESES_FIXOS = ("202406", "202501", "202506")
# Regras de ligação relatadas lado a lado: a literal é a do protocolo congelado; D1 é correção pós-hoc.
REGRAS = {"literal_doc45": False, "d1_pos_hoc": True}
CICLOS_OUTCOME = (1, 2)
CORTES_MIL = L.CORTES_MIL
H_MIL = L.H_PRINCIPAL_MIL
# Definições
PARTICULAS = frozenset({"DE", "DA", "DO", "DAS", "DOS", "E", "D", "DI", "DU"})
RAIO_TERRA_KM = 6371.0088  # raio médio (IUGG)
ESCALA_DISTANCIA_KM = 100.0  # E9 com distância: coeficiente por 100 km
MIN_CANDIDATOS_E9_DIST = 50  # abaixo disso o logit com distância não é estimado (fixado antes de ver)
ORIGENS = ("mesmo_municipio", "mesma_regiao_saude", "mesma_uf", "outra_uf", "sem_vinculo_medico_anterior")

COLS_CACHE_VINC = ["competencia", "co_unidade", "co_cnes", "co_municipio", "co_regiao_saude", "co_profissional_sus",
                   "co_cbo", "tp_sus_nao_sus", "co_conselho_classe", "nu_registro", "sg_uf_crm"]
VERSAO_CACHE = 1


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 22), b""):
            h.update(bloco)
    return h.hexdigest()


def rel(caminho: Path) -> str:
    return caminho.resolve().relative_to(ROOT).as_posix()


def checar_limite(comp: str) -> None:
    if comp >= LIMITE_EXCLUSIVO:
        raise RuntimeError(f"competência {comp} >= {LIMITE_EXCLUSIVO} é vedada (ciclo 3)")


# ---------------------------------------------------------------- normalização

def texto_norm(valor: object) -> str:
    """Maiúsculas, sem acento, só alfanuméricos separados por um espaço (como no script 12)."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)) or valor is pd.NA:
        return ""
    s = unicodedata.normalize("NFKD", str(valor))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).upper()
    return " ".join(re.findall(r"[A-Z0-9]+", s))


def tokens_nome(nome: object) -> tuple[str, ...]:
    return tuple(t for t in texto_norm(nome).split() if t not in PARTICULAS and not t.isdigit())


def nomes_compativeis(a: object, b: object) -> bool:
    """Mesmo primeiro nome e (mesmo último sobrenome ou nomes de um contidos no outro)."""
    ta, tb = tokens_nome(a), tokens_nome(b)
    if not ta or not tb or ta[0] != tb[0]:
        return False
    if ta[-1] == tb[-1]:
        return True
    menor, maior = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return len(menor) >= 2 and set(menor) <= set(maior)


def registro_norm(s: pd.Series) -> pd.Series:
    """Número do registro: só dígitos, sem zeros à esquerda; vazio vira <NA>."""
    d = s.astype("string").str.replace(r"\D", "", regex=True).str.lstrip("0")
    return d.mask(d.fillna("") == "")


def uf_sigla(s: pd.Series) -> pd.Series:
    return s.astype("string").str.strip().str.upper()


# ---------------------------------------------------------------- listas do PMM-E

def ler_listas_pmme() -> tuple[pd.DataFrame, dict]:
    """União das duas listas nominais; nome só em memória. Uma linha por registro (ciclo, CRM, UF, CNES, curso)."""
    with zipfile.ZipFile(ATIVOS_ZIP) as z:
        nomes = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(nomes) != 1:
            raise AssertionError(f"esperado um CSV em {rel(ATIVOS_ZIP)}")
        a = pd.read_csv(io.BytesIO(z.read(nomes[0])), sep=";", dtype=str, encoding="latin1", keep_default_na=False)
    n = pd.read_csv(NOMINAL_CSV, dtype=str, keep_default_na=False)

    def padronizar(df: pd.DataFrame, fonte: str, fmt_data: str) -> pd.DataFrame:
        out = pd.DataFrame({
            "ciclo": pd.to_numeric(df["ciclo"].str.strip(), errors="raise").astype(int),
            "crm": registro_norm(df["crm"]),
            "uf": uf_sigla(df["uf"]),
            "co_cnes": df["co_cnes"].astype("string").str.replace(r"\D", "", regex=True).str.zfill(7),
            "co_ibge": df["co_ibge"].astype("string").str.replace(r"\D", "", regex=True).str[:6],
            "curso": df["curso"].astype("string").str.strip(),
            "faixa_atracao": df["faixa_atracao"].astype("string").str.strip(),
            "dt_inicio": pd.to_datetime(df["dt_inicio_atividade"].str.strip(), format=fmt_data, errors="raise"),
            "_nome": df["nome"].map(texto_norm),
            "fonte_lista": fonte,
        })
        out["cod_curso"] = pd.to_numeric(out["curso"].str.extract(r"^\s*(\d+)", expand=False), errors="raise").astype(int)
        return out

    pa = padronizar(a, "ativos_2026-09-11", "%d/%m/%Y")
    pn = padronizar(n, "nominal_2026-08-12", "%Y-%m-%d")
    chave = ["ciclo", "crm", "uf", "co_cnes", "cod_curso"]
    so_nominal = pn.merge(pa[chave].drop_duplicates(), on=chave, how="left", indicator=True)
    so_nominal = so_nominal[so_nominal["_merge"] == "left_only"].drop(columns="_merge")
    em_ambas = int(len(pn) - len(so_nominal))
    u = pd.concat([pa, so_nominal], ignore_index=True)
    dup = int(u.duplicated(chave).sum())
    diag = {
        "registros_ativos_2026_09_11": int(len(pa)),
        "registros_nominal_2026_08_12": int(len(pn)),
        "registros_nominal_tambem_nos_ativos": em_ambas,
        "registros_so_na_nominal": int(len(so_nominal)),
        "registros_uniao": int(len(u)),
        "chave_registro": chave,
        "registros_repetidos_na_chave": dup,
        "crm_ausente": int(u["crm"].isna().sum()),
        "nota_uf": "a UF das listas é a do posto do PMM-E; as listas não trazem a UF do CRM",
    }
    # Pseudônimo determinístico: ordem do SHA-256 da chave do registro (só em memória).
    h = (u["ciclo"].astype(str) + "|" + u["crm"].fillna("") + "|" + u["uf"] + "|" + u["co_cnes"] + "|"
         + u["cod_curso"].astype(str) + "|" + u["fonte_lista"]).map(lambda s: hashlib.sha256(s.encode()).hexdigest())
    ordem = {v: i + 1 for i, v in enumerate(sorted(h))}
    u["id_medico"] = [f"x1m_{ordem[v]:05d}" for v in h]
    u["mes_inicio"] = u["dt_inicio"].dt.strftime("%Y%m")
    return u.sort_values("id_medico").reset_index(drop=True), diag


def crms_alvo(listas: pd.DataFrame) -> set[str]:
    return set(listas["crm"].dropna().tolist())


def assinatura_alvo(alvo: set[str]) -> str:
    return hashlib.sha256("|".join(sorted(alvo)).encode()).hexdigest()


# ---------------------------------------------------------------- aquisição e extração

def _a09():
    return _importar("a09_adquirir_cnes_nacional_x1", SCRIPT_A09)


def caminho_cache(comp: str) -> Path:
    return CACHE_DIR / f"vinculos_medicos_registro_{comp}.parquet"


def caminho_nomes(comp: str) -> Path:
    return CACHE_DIR / f"nomes_registro_alvo_{comp}.parquet"


def caminho_meta(comp: str) -> Path:
    return CACHE_DIR / f"meta_{comp}.json"


def _ler_tabela(zf: zipfile.ZipFile, membro: str, colunas: set[str], chunksize: int | None = None):
    return pd.read_csv(zf.open(membro), sep=";", encoding="latin1", dtype=str, keep_default_na=False, na_values=[],
                       usecols=lambda c: c.strip().strip('"').upper() in colunas, chunksize=chunksize)


def extrair_competencia(comp: str, zip_path: str, alvo: list[str]) -> tuple[str, dict]:
    """Vínculos médicos com registro + município e região do estabelecimento; nomes só do alvo."""
    checar_limite(comp)
    a09 = _a09()
    alvo_set = set(alvo)
    meta: dict[str, Any] = {"competencia": comp}
    with zipfile.ZipFile(zip_path) as zf:
        m_carga = a09._membro(zf, "tbCargaHorariaSus")
        m_estab = a09._membro(zf, "tbEstabelecimento")
        m_prof = a09._membro(zf, "tbDadosProfissionalSus")
        meta["membros_lidos"] = {"carga": m_carga, "estab": m_estab, "profissional": m_prof}
        cab = {k: a09._cabecalho(zf, m) for k, m in meta["membros_lidos"].items()}
        req = {"carga": {"CO_UNIDADE", "CO_PROFISSIONAL_SUS", "CO_CBO", "TP_SUS_NAO_SUS", "CO_CONSELHO_CLASSE",
                         "NU_REGISTRO", "SG_UF_CRM"},
               "estab": {"CO_UNIDADE", "CO_CNES", "CO_MUNICIPIO_GESTOR", "CO_REGIAO_SAUDE"},
               "profissional": {"CO_PROFISSIONAL_SUS", "NO_PROFISSIONAL"}}
        faltam = {k: sorted(v - set(cab[k])) for k, v in req.items() if v - set(cab[k])}
        if faltam:
            raise RuntimeError(f"{comp}: colunas ausentes {faltam}")
        meta["colunas"] = cab

        estab = _ler_tabela(zf, m_estab, req["estab"])
        estab.columns = [c.strip().strip('"').upper() for c in estab.columns]
        estab["CO_UNIDADE"] = estab["CO_UNIDADE"].str.strip()
        meta["co_unidade_duplicados_estab"] = int(estab["CO_UNIDADE"].duplicated().sum())
        estab = estab.drop_duplicates("CO_UNIDADE")

        partes, linhas = [], 0
        for bloco in _ler_tabela(zf, m_carga, req["carga"], chunksize=1_000_000):
            bloco.columns = [c.strip().strip('"').upper() for c in bloco.columns]
            linhas += len(bloco)
            cbo = bloco["CO_CBO"].str.strip()
            partes.append(bloco.loc[cbo.str.startswith(a09.PREFIXOS_MEDICOS)])
        meta["linhas_tbCargaHorariaSus"] = int(linhas)
        carga = pd.concat(partes, ignore_index=True)
        carga["CO_UNIDADE"] = carga["CO_UNIDADE"].str.strip()
        m = carga.merge(estab, on="CO_UNIDADE", how="left", validate="many_to_one")
        df = pd.DataFrame({
            "competencia": comp,
            "co_unidade": m["CO_UNIDADE"].astype("string"),
            "co_cnes": m["CO_CNES"].astype("string").str.replace(r"\D", "", regex=True).str.zfill(7),
            "co_municipio": m["CO_MUNICIPIO_GESTOR"].astype("string").str.replace(r"\D", "", regex=True).str[:6],
            "co_regiao_saude": m["CO_REGIAO_SAUDE"].astype("string").str.strip(),
            "co_profissional_sus": m["CO_PROFISSIONAL_SUS"].astype("string").str.strip(),
            "co_cbo": m["CO_CBO"].astype("string").str.strip(),
            "tp_sus_nao_sus": m["TP_SUS_NAO_SUS"].astype("string").str.strip(),
            "co_conselho_classe": m["CO_CONSELHO_CLASSE"].astype("string").str.strip(),
            "nu_registro": registro_norm(m["NU_REGISTRO"]),
            "sg_uf_crm": uf_sigla(m["SG_UF_CRM"]),
        })[COLS_CACHE_VINC]
        meta["linhas_vinculos_medicos"] = int(len(df))
        meta["vinculos_sem_estabelecimento"] = int(df["co_municipio"].isna().sum())
        meta["vinculos_sem_registro"] = int(df["nu_registro"].isna().sum())
        meta["vinculos_sem_uf_crm"] = int((df["sg_uf_crm"].fillna("") == "").sum())
        meta["conselho_classe_dos_vinculos_medicos"] = {
            str(k): int(v) for k, v in df["co_conselho_classe"].fillna("<NA>").value_counts().sort_index().items()}
        meta["profissionais_distintos"] = int(df["co_profissional_sus"].nunique())
        no_alvo = df["nu_registro"].isin(alvo_set)
        prof_alvo = set(df.loc[no_alvo, "co_profissional_sus"].dropna())
        meta["vinculos_com_registro_no_alvo"] = int(no_alvo.sum())
        meta["profissionais_com_registro_no_alvo"] = len(prof_alvo)

        nomes = []
        for bloco in _ler_tabela(zf, m_prof, req["profissional"], chunksize=1_000_000):
            bloco.columns = [c.strip().strip('"').upper() for c in bloco.columns]
            cod = bloco["CO_PROFISSIONAL_SUS"].str.strip()
            sel = bloco.loc[cod.isin(prof_alvo)]
            nomes.append(pd.DataFrame({"competencia": comp, "co_profissional_sus": cod[sel.index].astype("string"),
                                       "nome_norm": sel["NO_PROFISSIONAL"].map(texto_norm).astype("string")}))
        nomes_df = pd.concat(nomes, ignore_index=True).drop_duplicates()
        meta["profissionais_alvo_com_nome"] = int(nomes_df["co_profissional_sus"].nunique())
        meta["profissionais_alvo_com_mais_de_um_nome"] = int(nomes_df["co_profissional_sus"].duplicated().sum())

    df = df.sort_values(["co_profissional_sus", "co_unidade", "co_cbo"], kind="mergesort").reset_index(drop=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = caminho_cache(comp).with_suffix(".tmp")
    df.to_parquet(tmp, index=False)
    tmp.replace(caminho_cache(comp))
    nomes_df.sort_values(["co_profissional_sus"]).to_parquet(caminho_nomes(comp), index=False)
    return comp, meta


def adquirir(competencias: tuple[str, ...], alvo: set[str], workers: int = 3) -> dict[str, dict]:
    """Download (servlet HTTPS do CNES, ou ZIP local íntegro), extração, validação contra o a09, ZIP apagado."""
    a09 = _a09()
    man_a09 = json.loads(MANIFESTO_A09.read_text(encoding="utf-8")).get("por_competencia", {})
    assinatura = assinatura_alvo(alvo)
    infos: dict[str, dict] = {}
    pendentes = []
    for comp in competencias:
        checar_limite(comp)
        if caminho_meta(comp).exists():
            meta = json.loads(caminho_meta(comp).read_text(encoding="utf-8"))
            if (meta.get("versao_cache") == VERSAO_CACHE and meta.get("assinatura_alvo") == assinatura
                    and caminho_cache(comp).exists() and caminho_nomes(comp).exists()):
                infos[comp] = meta
                continue
        pendentes.append(comp)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        downloads = {comp: ex.submit(a09.baixar, comp) for comp in pendentes}
        for comp, fut in downloads.items():
            infos[comp] = {"download": fut.result()}
    if pendentes:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(extrair_competencia, comp, str(a09.caminho_zip(comp)), sorted(alvo)) for comp in pendentes]
            for fut in concurrent.futures.as_completed(futs):
                comp, meta = fut.result()
                info = infos[comp]["download"]
                ref = man_a09.get(comp, {})
                validacao = {
                    "sha256_igual_ao_a09": info["sha256_zip"] == ref.get("sha256_zip"),
                    "linhas_vinculos_medicos_a09": ref.get("linhas_vinculos_medicos"),
                    "linhas_vinculos_medicos_x1": meta["linhas_vinculos_medicos"],
                }
                # Fail closed: o ZIP tem de ser o mesmo do a09 (SHA-256) e a extração tem de reproduzir a contagem
                # de vínculos médicos do a09.
                if not validacao["sha256_igual_ao_a09"]:
                    raise AssertionError(f"{comp}: SHA-256 do ZIP difere do manifesto do a09: {validacao}")
                if ref.get("linhas_vinculos_medicos") != meta["linhas_vinculos_medicos"]:
                    raise AssertionError(f"{comp}: contagem de vínculos médicos difere do a09 com o mesmo ZIP: {validacao}")
                if meta["linhas_vinculos_medicos"] < a09.MIN_VINCULOS_MEDICOS_MES:
                    raise AssertionError(f"{comp}: extração implausível ({meta['linhas_vinculos_medicos']} vínculos)")
                registro = {"competencia": comp, "versao_cache": VERSAO_CACHE, "assinatura_alvo": assinatura,
                            **info, **meta, "validacao_contra_a09": validacao,
                            "data_processamento": dt.date.today().isoformat(), "status": "extraido_zip_apagado"}
                caminho_meta(comp).write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                a09.caminho_zip(comp).unlink()
                log(f"{comp}: {meta['linhas_vinculos_medicos']:,} vínculos médicos; ZIP apagado")
                infos[comp] = registro
    return infos


TABELAS_CODIGOS = ("tbConselhoClasse", "tbOrgaoEmissor")
CONSELHO_META = CACHE_DIR / f"tabelas_codigos_{COMPETENCIA_POS}.json"


def caminho_tabela_codigos(tabela: str) -> Path:
    return CACHE_DIR / f"{tabela}_{COMPETENCIA_POS}.csv"


def adquirir_conselho() -> None:
    """Tabelas de código do CNES (competência 202608): tbConselhoClasse e tbOrgaoEmissor. ZIP conferido contra o a09."""
    a09 = _a09()
    comp = COMPETENCIA_POS
    info = a09.baixar(comp)
    ref = json.loads(MANIFESTO_A09.read_text(encoding="utf-8"))["por_competencia"][comp]
    if info["sha256_zip"] != ref["sha256_zip"]:
        raise AssertionError(f"{comp}: SHA-256 do ZIP difere do a09 (fail closed)")
    membros = {}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(a09.caminho_zip(comp)) as zf:
        for tabela in TABELAS_CODIGOS:
            membro = a09._membro(zf, tabela)
            tb = pd.read_csv(zf.open(membro), sep=";", encoding="latin1", dtype=str, keep_default_na=False)
            tb.columns = [c.strip().strip('"').upper() for c in tb.columns]
            tb.to_csv(caminho_tabela_codigos(tabela), index=False)
            membros[tabela] = {"membro": membro, "linhas": int(len(tb)), "colunas": list(tb.columns)}
    CONSELHO_META.write_text(json.dumps({"competencia": comp, "tabelas": membros, **info, "sha256_igual_ao_a09": True,
                                         "data_processamento": dt.date.today().isoformat()},
                                        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    a09.caminho_zip(comp).unlink()
    log(f"tabelas de código de {comp} extraídas; ZIP apagado")


def codigo_conselho_crm(vinc: pd.DataFrame | None = None) -> tuple[str, dict]:
    """Código do CRM no campo CO_CONSELHO_CLASSE da tbCargaHorariaSus; para se não for único.

    O campo segue a tabela tbOrgaoEmissor do CNES (código → órgão emissor), não a tbConselhoClasse (que tem
    outra numeração). Regra: descrição normalizada contém MEDICINA e CONSELHO REGIONAL e não VETERINARIA.
    """
    if not CONSELHO_META.exists():
        raise SystemExit("tabelas de código do CNES ausentes do cache; rode --etapa aquisicao (fail closed)")
    tb = pd.read_csv(caminho_tabela_codigos("tbOrgaoEmissor"), dtype=str, keep_default_na=False)
    desc = tb["DS_ORGAO_EMISSOR"].map(texto_norm)
    crm = tb[desc.str.contains("MEDICINA") & desc.str.contains("CONSELHO REGIONAL") & ~desc.str.contains("VETERINARIA")]
    if len(crm) != 1:
        raise AssertionError(f"tbOrgaoEmissor: esperado um código de Conselho Regional de Medicina, achados {len(crm)}")
    codigo = str(crm["CO_ORGAO_EMISSOR"].iloc[0]).strip()
    cc = pd.read_csv(caminho_tabela_codigos("tbConselhoClasse"), dtype=str, keep_default_na=False)
    cc_med = cc[cc["DS_CONSELHO_CLASSE"].map(texto_norm).str.contains("MEDICINA")
                & ~cc["DS_CONSELHO_CLASSE"].map(texto_norm).str.contains("VETERINARIA")]
    meta = json.loads(CONSELHO_META.read_text(encoding="utf-8"))
    diag = {"codigo_crm": codigo, "descricao": str(crm["DS_ORGAO_EMISSOR"].iloc[0]).strip(),
            "tabela": meta["tabelas"]["tbOrgaoEmissor"]["membro"], "competencia": meta["competencia"],
            "sha256_zip": meta["sha256_zip"], "url": meta["url"],
            "regra": "tbOrgaoEmissor: descrição contém MEDICINA e CONSELHO REGIONAL e não VETERINARIA; uma linha",
            "nota_tbConselhoClasse": ("a tbConselhoClasse tem outra numeração (medicina = "
                                      + ", ".join(cc_med["CO_CONSELHO_CLASSE"].tolist()) +
                                      "); o campo CO_CONSELHO_CLASSE da carga horária segue a tbOrgaoEmissor")}
    if vinc is not None:
        diag["fracao_dos_vinculos_medicos_com_o_codigo"] = float((vinc["co_conselho_classe"] == codigo).mean())
    return codigo, diag


def verificar_periodo_malha() -> None:
    """Descobre a que período da malha municipal a resposta padrão da API corresponde (bytes idênticos)."""
    import gzip
    import urllib.error
    import urllib.request
    man = json.loads(COORD_MANIFESTO.read_text(encoding="utf-8"))
    alvo = sha256_arquivo(COORD_JSON)
    iguais, testados = [], {}
    for periodo in range(2020, 2026):
        url = f"{COORD_URL}&periodo={periodo}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                corpo = resp.read()
        except urllib.error.HTTPError as erro:  # período sem malha na API
            testados[str(periodo)] = {"erro_http": erro.code}
            continue
        if corpo[:2] == b"\x1f\x8b":
            corpo = gzip.decompress(corpo)
        h = hashlib.sha256(corpo).hexdigest()
        testados[str(periodo)] = {"sha256": h, "bytes": len(corpo)}
        if h == alvo:
            iguais.append(str(periodo))
    if len(iguais) != 1:
        raise AssertionError(f"período da malha não identificado de forma única: {iguais}")
    man.update({"malha_periodo_verificado": iguais[0], "verificacao_periodo": {
        "metodo": "a resposta padrão tem os mesmos bytes que a resposta com &periodo=AAAA",
        "data": dt.date.today().isoformat(), "testados": testados}})
    COORD_MANIFESTO.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log(f"malha municipal da API: período {iguais[0]}")


def baixar_coordenadas() -> None:
    import urllib.request
    COORD_JSON.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(COORD_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        corpo = resp.read()
    if corpo[:2] == b"\x1f\x8b":  # a API responde com gzip mesmo sem Accept-Encoding
        import gzip
        corpo = gzip.decompress(corpo)
    dados = json.loads(corpo)
    if not isinstance(dados, list) or len(dados) < 5500:
        raise AssertionError("resposta da API de malhas do IBGE inesperada")
    COORD_JSON.write_bytes(corpo)
    COORD_MANIFESTO.write_text(json.dumps({
        "url": COORD_URL, "data_download": dt.date.today().isoformat(), "sha256": sha256_arquivo(COORD_JSON),
        "bytes": COORD_JSON.stat().st_size, "fonte": "IBGE, API de malhas geográficas v3, metadados (centroide) por município",
        "natureza_dos_dados": NATUREZA}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- leitura do cache

def ler_cache() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, dict]]:
    vinc, nomes, metas = [], [], {}
    faltam = [c for c in COMPETENCIAS if not (caminho_cache(c).exists() and caminho_meta(c).exists()
                                              and caminho_nomes(c).exists())]
    if faltam:
        raise SystemExit(f"cache do X1 ausente para {faltam}; rode --etapa aquisicao (fail closed)")
    for c in COMPETENCIAS:
        checar_limite(c)
        metas[c] = json.loads(caminho_meta(c).read_text(encoding="utf-8"))
        v = pd.read_parquet(caminho_cache(c))
        if set(v["competencia"].unique()) != {c} or len(v) != metas[c]["linhas_vinculos_medicos"]:
            raise AssertionError(f"cache de {c} incoerente com o metadado")
        vinc.append(v)
        nomes.append(pd.read_parquet(caminho_nomes(c)))
    return pd.concat(vinc, ignore_index=True), pd.concat(nomes, ignore_index=True), metas


def mapa_regiao_saude(vinc: pd.DataFrame) -> tuple[pd.Series, dict]:
    """Município → região de saúde (CIR) do painel do PMMB do Ministério da Saúde (nível MUNICIPAL).

    Chave da região = UF + nome normalizado da CIR (o mesmo nome existe em mais de uma UF). O campo
    CO_REGIAO_SAUDE do tbEstabelecimento não é usado: é texto livre e vem vazio em boa parte das linhas
    (a fração vazia nos estabelecimentos com vínculo médico vai para o diagnóstico).
    """
    with zipfile.ZipFile(PPF_ZIP) as z:
        d = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), sep=";", dtype=str, encoding="latin1",
                        keep_default_na=False)
    m = d[d["nivel"] == "MUNICIPAL"].copy()
    m["co_ibge"] = m["co_ibge"].str.replace(r"\D", "", regex=True).str[:6]
    if m["co_ibge"].duplicated().any():
        raise AssertionError("PPF: co_ibge repetido no nível MUNICIPAL")
    cir = m["cir"].map(texto_norm)
    valido = (cir != "") & (cir != "NA")
    mapa = (m["uf"].str.strip().str.upper() + "|" + cir).where(valido)
    mapa.index = m["co_ibge"]
    vazio = vinc["co_regiao_saude"].fillna("").str.strip() == ""
    diag = {"fonte": rel(PPF_ZIP), "municipios": int(len(mapa)), "municipios_com_regiao": int(mapa.notna().sum()),
            "regioes_distintas": int(mapa.nunique()),
            "regra": "região = UF + nome normalizado da CIR do painel do PMMB (nível MUNICIPAL)",
            "co_regiao_saude_cnes_vazio_nos_vinculos_medicos": float(vazio.mean()),
            "nota_cnes": "CO_REGIAO_SAUDE do CNES é texto livre e muito vazio; não é usado"}
    return mapa.dropna(), diag


def ler_coordenadas() -> tuple[pd.DataFrame, dict]:
    if not COORD_JSON.exists():
        return pd.DataFrame(columns=["co_ibge", "lon", "lat"]), {"status": "INDISPONIVEL", "motivo": "arquivo ausente"}
    dados = json.loads(COORD_JSON.read_text(encoding="utf-8"))
    df = pd.DataFrame([{"co_ibge_7d": str(d["id"]), "lon": float(d["centroide"]["longitude"]),
                        "lat": float(d["centroide"]["latitude"])} for d in dados])
    df["co_ibge"] = df["co_ibge_7d"].str[:6]
    if df["co_ibge"].duplicated().any():
        raise AssertionError("coordenadas: código de 6 dígitos repetido")
    man = json.loads(COORD_MANIFESTO.read_text(encoding="utf-8")) if COORD_MANIFESTO.exists() else {}
    return df[["co_ibge", "lon", "lat"]], {"status": "OBTIDO", "municipios": int(len(df)), **man,
                                           "sha256_atual": sha256_arquivo(COORD_JSON)}


def haversine_km(lon1, lat1, lon2, lat2) -> np.ndarray:
    lon1, lat1, lon2, lat2 = (np.radians(np.asarray(v, dtype=float)) for v in (lon1, lat1, lon2, lat2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 2 * RAIO_TERRA_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


# ---------------------------------------------------------------- ligação

def ligar(listas: pd.DataFrame, vinc: pd.DataFrame, nomes: pd.DataFrame, *, conselho_crm: str,
          exigir_nome_etapa1: bool) -> tuple[pd.DataFrame, dict]:
    """Regra do doc 45 (CRM+UF exato; depois CRM exato com nome compatível; ambíguos fora) e a correção D1.

    `exigir_nome_etapa1=False` é a regra literal do protocolo congelado (doc 45). `True` é a correção D1,
    decidida em 19/10/2026 DEPOIS da primeira execução completa (que gravou e exibiu as estimativas com a
    regra literal): a UF das listas é a do posto, não a do CRM, e na etapa 1 literal um CRM de outra UF
    colide com o de outra pessoa na UF do posto. Com D1, o candidato único da etapa 1 só liga com nome
    compatível; sem ele, o registro segue para a etapa 2 (CRM em qualquer UF com nome compatível). As duas
    regras são relatadas lado a lado.

    Só entram na busca os vínculos médicos cujo `co_conselho_classe` é o do CRM (`conselho_crm`, lido da
    tabela tbConselhoClasse do CNES).

    `listas`: id_medico, crm, uf, _nome. `vinc`: nu_registro, sg_uf_crm, co_conselho_classe,
    co_profissional_sus (só vínculos médicos). `nomes`: co_profissional_sus, nome_norm. Devolve uma linha
    por id_medico com co_profissional_sus (ou <NA>), etapa_ligacao e motivo.
    """
    reg = vinc[vinc["co_conselho_classe"] == conselho_crm].dropna(subset=["nu_registro", "co_profissional_sus"])
    reg = reg[["nu_registro", "sg_uf_crm", "co_profissional_sus"]].drop_duplicates()
    por_crm_uf = reg.groupby(["nu_registro", "sg_uf_crm"])["co_profissional_sus"].agg(lambda s: sorted(set(s)))
    por_crm = reg.groupby("nu_registro")["co_profissional_sus"].agg(lambda s: sorted(set(s)))
    nomes_prof = nomes.dropna().groupby("co_profissional_sus")["nome_norm"].agg(lambda s: sorted(set(s)))
    linhas, compat_etapa1 = [], []
    for r in listas.rename(columns={"_nome": "nome_lista"}).itertuples(index=False):
        base = {"id_medico": r.id_medico, "co_profissional_sus": pd.NA, "etapa_ligacao": pd.NA, "motivo": "",
                "etapa1_rejeitada_por_nome": 0}
        if pd.isna(r.crm):
            linhas.append({**base, "motivo": "crm_ausente_na_lista"})
            continue
        c1 = por_crm_uf.get((r.crm, r.uf), [])
        if len(c1) == 1:
            compat = any(nomes_compativeis(r.nome_lista, n) for n in nomes_prof.get(c1[0], []))
            compat_etapa1.append(compat)
            if compat or not exigir_nome_etapa1:
                linhas.append({**base, "co_profissional_sus": c1[0], "etapa_ligacao": "1_crm_uf", "motivo": "ligado"})
                continue
            base["etapa1_rejeitada_por_nome"] = 1
        elif len(c1) > 1:
            linhas.append({**base, "motivo": "ambiguo_crm_uf_com_mais_de_um_profissional"})
            continue
        c2 = por_crm.get(r.crm, [])
        if not c2:
            linhas.append({**base, "motivo": "crm_sem_vinculo_medico_no_cnes"})
            continue
        ok = [p for p in c2 if any(nomes_compativeis(r.nome_lista, n) for n in nomes_prof.get(p, []))]
        if len(ok) == 1:
            linhas.append({**base, "co_profissional_sus": ok[0], "etapa_ligacao": "2_crm_nome", "motivo": "ligado"})
        elif len(ok) > 1:
            linhas.append({**base, "motivo": "ambiguo_crm_nome_com_mais_de_um_profissional"})
        else:
            linhas.append({**base, "motivo": "crm_sem_nome_compativel"})
    out = pd.DataFrame(linhas)
    diag = {"exigir_nome_etapa1": exigir_nome_etapa1, "conselho_crm": conselho_crm,
            "vinculos_medicos_fora_do_conselho_crm_excluidos_da_busca": int((vinc["co_conselho_classe"]
                                                                              != conselho_crm).sum()),
            "etapa1_candidato_unico": len(compat_etapa1),
            "etapa1_nome_compativel": int(sum(compat_etapa1)),
            "etapa1_fracao_nome_compativel": (sum(compat_etapa1) / len(compat_etapa1)) if compat_etapa1 else None,
            "etapa1_rejeitadas_por_nome": int(out["etapa1_rejeitada_por_nome"].sum()),
            "etapa1_rejeitadas_ligadas_na_etapa2": int(((out["etapa1_rejeitada_por_nome"] == 1)
                                                        & (out["etapa_ligacao"] == "2_crm_nome")).sum())}
    return out, diag


# ---------------------------------------------------------------- outcomes por médico

def outcomes_medico(med: pd.DataFrame, vinc: pd.DataFrame, regiao: pd.Series, coord: pd.DataFrame) -> pd.DataFrame:
    """(a)–(e) para os médicos ligados; `med` tem id_medico, co_profissional_sus, co_cnes, co_ibge, mes_inicio."""
    lig = med.dropna(subset=["co_profissional_sus"])
    v = vinc[vinc["co_profissional_sus"].isin(set(lig["co_profissional_sus"]))].copy()
    v["uf_mun"] = v["co_municipio"].str[:2]
    v["regiao"] = v["co_municipio"].map(regiao)
    xy = coord.set_index("co_ibge") if len(coord) else None
    por_prof = {p: g for p, g in v.groupby("co_profissional_sus")}
    linhas = []
    for r in lig.itertuples(index=False):
        g = por_prof.get(r.co_profissional_sus, v.iloc[0:0])
        pre = [c for c in COMPETENCIAS if c < r.mes_inicio]
        o: dict[str, Any] = {"id_medico": r.id_medico, "competencias_pre_inicio": len(pre),
                             "ultima_competencia_pre": pre[-1] if pre else pd.NA}
        reg_posto = regiao.get(r.co_ibge, pd.NA)
        uf_posto = r.co_ibge[:2]
        if not pre:
            o.update({"motivo_sem_pre": "nenhuma competência lida antes do início"})
        else:
            gp = g[g["competencia"].isin(pre)]
            gu = g[g["competencia"] == pre[-1]]
            o["a_mesmo_estab_ultimo_pre"] = int((gu["co_cnes"] == r.co_cnes).any())
            o["a_mesmo_estab_algum_pre"] = int((gp["co_cnes"] == r.co_cnes).any())
            o["b_mesmo_mun_ultimo_pre"] = int((gu["co_municipio"] == r.co_ibge).any())
            o["b_mesmo_mun_algum_pre"] = int((gp["co_municipio"] == r.co_ibge).any())
            o["vinculo_medico_algum_pre"] = int(len(gp) > 0)
            for mf in MESES_FIXOS:
                if mf < r.mes_inicio:  # mês fixo pré-início para todos os ciclos 1 e 2
                    gf = g[g["competencia"] == mf]
                    o[f"b_mesmo_mun_em_{mf}"] = int((gf["co_municipio"] == r.co_ibge).any())
                    o[f"a_mesmo_estab_em_{mf}"] = int((gf["co_cnes"] == r.co_cnes).any())
            o["vinculos_ultimo_pre"] = int(len(gu))
            if gu.empty:
                o["c_origem"] = "sem_vinculo_medico_anterior"
            elif (gu["co_municipio"] == r.co_ibge).any():
                o["c_origem"] = "mesmo_municipio"
            elif pd.notna(reg_posto) and (gu["regiao"] == reg_posto).any():
                o["c_origem"] = "mesma_regiao_saude"
            elif pd.isna(reg_posto) or gu["regiao"].isna().any():
                # sem região conhecida não se distingue região de UF: fica ausente, com o motivo
                o["c_origem"] = pd.NA
                o["motivo_origem_ausente"] = "região de saúde desconhecida no posto ou na origem"
            elif (gu["uf_mun"] == uf_posto).any():
                o["c_origem"] = "mesma_uf"
            else:
                o["c_origem"] = "outra_uf"
            if not gu.empty:
                muns = sorted(set(gu["co_municipio"].dropna()))
                o["_munis_ultimo_pre"] = tuple(muns)  # só em memória (E9 com distância); não é gravado
                if xy is None:
                    o["motivo_distancia_ausente"] = "coordenadas do IBGE indisponíveis"
                elif r.co_ibge in xy.index and all(m in xy.index for m in muns):
                    d = haversine_km(xy.loc[muns, "lon"], xy.loc[muns, "lat"], xy.at[r.co_ibge, "lon"],
                                     xy.at[r.co_ibge, "lat"])
                    o["d_distancia_km"] = float(np.min(d))
                    o["co_ibge_origem_mais_proxima"] = muns[int(np.argmin(d))]
                else:
                    o["motivo_distancia_ausente"] = "município sem coordenada na API do IBGE"
        if r.mes_inicio < COMPETENCIA_POS:
            gpos = g[g["competencia"] == COMPETENCIA_POS]
            o["e_vinculos_202608"] = int(len(gpos))
            o["e_estabelecimentos_202608"] = int(gpos["co_unidade"].nunique())
            o["e_municipios_202608"] = int(gpos["co_municipio"].nunique())
            o["vinculo_no_estab_do_posto_202608"] = int((gpos["co_cnes"] == r.co_cnes).any())
        linhas.append(o)
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- análises

def faixa_pela_regra(s_mil: np.ndarray) -> np.ndarray:
    return np.where(s_mil > CORTES_MIL[1], "FAIXA 1", np.where(s_mil > CORTES_MIL[0], "FAIXA 2", "FAIXA 3"))


def carregar_ivs() -> pd.Series:
    ivs = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str}, usecols=["co_ibge", "ivs"])
    ivs["co_ibge"] = ivs["co_ibge"].str.zfill(6)
    if not ivs["co_ibge"].is_unique:
        raise AssertionError("a08: co_ibge repetido")
    return ivs.set_index("co_ibge")["ivs"].astype(float)


INDICADORES_DESC = [
    ("ligado", "médico ligado ao CNES", "registros"),
    ("a_mesmo_estab_ultimo_pre", "(a) vínculo no mesmo estabelecimento, última competência pré-início", "ligados"),
    ("a_mesmo_estab_algum_pre", "(a') vínculo no mesmo estabelecimento, alguma competência pré-início", "ligados"),
    ("b_mesmo_mun_ultimo_pre", "(b) vínculo no mesmo município, última competência pré-início", "ligados"),
    ("b_mesmo_mun_algum_pre", "(b') vínculo no mesmo município, alguma competência pré-início", "ligados"),
    ("novo_no_municipio", "novo no município: 1 − (b)", "ligados"),
    ("vinculo_medico_algum_pre", "algum vínculo médico em alguma competência pré-início", "ligados"),
] + [(f"origem_{o}", f"(c) origem: {o}", "ligados") for o in ORIGENS] + [
    ("d_distancia_km", "(d) distância da origem mais próxima (km), média", "ligados com vínculo pré"),
    ("d_distancia_km_mediana", "(d) distância da origem mais próxima (km), mediana", "ligados com vínculo pré"),
    ("e_vinculos_202608", "(e) vínculos médicos em 202608, média", "ligados com início antes de 202608"),
    ("e_estabelecimentos_202608", "(e) estabelecimentos com vínculo médico em 202608, média",
     "ligados com início antes de 202608"),
    ("vinculo_no_estab_do_posto_202608", "conferência: vínculo no estabelecimento do posto em 202608",
     "ligados com início antes de 202608"),
] + [(f"b_mesmo_mun_em_{m}", f"vínculo no mesmo município em {m} (mês fixo)", "ligados") for m in MESES_FIXOS] + [
    (f"a_mesmo_estab_em_{m}", f"vínculo no mesmo estabelecimento em {m} (mês fixo)", "ligados") for m in MESES_FIXOS
] + [(f"persistencia_incumbentes_em_{MESES_FIXOS[0]}",
      f"entre os que tinham vínculo no município na última competência pré-início, fração que já o tinha em "
      f"{MESES_FIXOS[0]}", "ligados com (b) = 1")]


def descritivo(med: pd.DataFrame, regra: str) -> pd.DataFrame:
    linhas = []
    for ciclo in ("1", "2", "1+2", "3"):
        cs = [1, 2] if ciclo == "1+2" else [int(ciclo)]
        for faixa in ("todas", "FAIXA 1", "FAIXA 2", "FAIXA 3"):
            for fonte in ("todas", "ativos_2026-09-11"):
                d = med[med["ciclo"].isin(cs)]
                if faixa != "todas":
                    d = d[d["faixa"] == faixa]
                if fonte != "todas":
                    d = d[d["fonte_lista"] == fonte]
                lig = d[d["ligado"] == 1]
                for col, rotulo, base in INDICADORES_DESC:
                    if ciclo == "3" and col != "ligado":
                        continue  # ciclo 3: só a taxa de ligação (doc 45: outcomes dos ciclos 1 e 2)
                    if col == "ligado":
                        x = d["ligado"]
                    elif col.startswith("origem_"):
                        x = (lig["c_origem"] == col.removeprefix("origem_")).astype(float).where(lig["c_origem"].notna())
                    elif col == "novo_no_municipio":
                        x = 1 - lig["b_mesmo_mun_ultimo_pre"]
                    elif col == "d_distancia_km_mediana":
                        x = lig["d_distancia_km"]
                    elif col.startswith("persistencia_incumbentes_em_"):
                        x = lig.loc[lig["b_mesmo_mun_ultimo_pre"] == 1, f"b_mesmo_mun_em_{MESES_FIXOS[0]}"]
                    else:
                        x = lig[col] if col in lig else pd.Series(dtype=float)
                    x = pd.to_numeric(x, errors="coerce").dropna()
                    valor = (float(x.median()) if col == "d_distancia_km_mediana" else float(x.mean())) if len(x) else np.nan
                    linhas.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "regra_ligacao": regra,
                                   "ciclo": ciclo, "faixa": faixa,
                                   "fonte_lista": fonte, "indicador": col, "descricao": rotulo, "base": base,
                                   "n_base": int(len(x)), "n_registros": int(len(d)), "valor": valor,
                                   "nota": "" if len(x) else "sem observação na base"})
    return pd.DataFrame(linhas)


OUTCOMES_RDD = {
    "frac_novos_no_municipio": ("fração de médicos ligados sem vínculo no município na última competência pré-início",
                                "n_ligados"),
    "frac_outra_uf": ("fração de médicos ligados com origem em outra UF (c)", "n_ligados_origem"),
    "distancia_media_km": ("distância média (km) da origem mais próxima, médicos com vínculo pré-início",
                           "n_com_distancia"),
}


def painel_municipio(med: pd.DataFrame, vmun: pd.DataFrame, ivs: pd.Series) -> tuple[pd.DataFrame, dict]:
    """Uma linha por ciclo × município de V_k com as médias dos médicos ligados (ausente sem médico)."""
    partes, diag = [], {}
    for k in CICLOS_OUTCOME:
        vk = vmun[vmun["ciclo"] == k][["co_ibge"]].drop_duplicates().copy()
        mk = med[(med["ciclo"] == k) & (med["fonte_lista"] == "ativos_2026-09-11")]
        fora = mk[~mk["co_ibge"].isin(set(vk["co_ibge"]))]
        diag[f"ciclo_{k}"] = {"municipios_V": int(len(vk)), "registros_ativos": int(len(mk)),
                              "registros_ativos_fora_de_V": int(len(fora)),
                              "registros_ativos_ligados_fora_de_V": int(fora["ligado"].sum())}
        lig = mk[(mk["ligado"] == 1) & mk["co_ibge"].isin(set(vk["co_ibge"]))].copy()
        lig["novo"] = 1 - lig["b_mesmo_mun_ultimo_pre"]
        lig["outra_uf"] = (lig["c_origem"] == "outra_uf").astype(float).where(lig["c_origem"].notna())
        g = lig.groupby("co_ibge")
        agg = pd.DataFrame({
            "n_ligados": g["novo"].count(),
            "frac_novos_no_municipio": g["novo"].mean(),
            "n_ligados_origem": g["outra_uf"].count(),
            "frac_outra_uf": g["outra_uf"].mean(),
            "n_com_distancia": g["d_distancia_km"].count(),
            "distancia_media_km": g["d_distancia_km"].mean(),
        }).reset_index()
        p = vk.merge(agg, on="co_ibge", how="left")
        for c in ("n_ligados", "n_ligados_origem", "n_com_distancia"):
            p[c] = p[c].fillna(0).astype(int)
        p.insert(0, "ciclo", k)
        partes.append(p)
    pm = pd.concat(partes, ignore_index=True)
    pm["ivs"] = pm["co_ibge"].map(ivs)
    diag["municipios_V_sem_ivs_oficial"] = int(pm["ivs"].isna().sum())
    pm = pm[pm["ivs"].notna()].copy()
    pm["s_mil"] = np.round(pm["ivs"].to_numpy() * 1000.0)
    return pm.reset_index(drop=True), diag


COLS_EST = ["natureza_dos_dados", "estatuto", "regra_ligacao", "analise", "outcome", "ciclo", "corte", "especificacao", "condicional",
            "tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "q_bky_x1", "n_abaixo", "n_acima", "n_obs", "n_clusters",
            "h_mil", "media_bruta_abaixo", "media_bruta_acima", "lee_tau_inf", "lee_tau_sup", "lee_q_aparo",
            "lee_lado_aparado", "lee_salto_selecao", "lee_p0_selecao", "lee_p1_selecao", "nota"]


def _linha(analise: str, outcome: str, ciclo: str, corte: str, espec: str, condicional: str, r: dict) -> dict:
    out = {c: np.nan for c in COLS_EST}
    out.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "analise": analise, "outcome": outcome,
                "ciclo": ciclo, "corte": corte, "especificacao": espec, "condicional": condicional,
                "nota": r.get("nota", "")})
    for c in ("tau", "ep", "ic95_inf", "ic95_sup", "p_valor", "n_abaixo", "n_acima", "n_obs", "n_clusters", "h_mil",
              "media_bruta_abaixo", "media_bruta_acima"):
        if c in r:
            out[c] = r[c]
    return out


def _juntar(*notas: str) -> str:
    return "; ".join(n for n in notas if n)


def estimar_rdd(pm: pd.DataFrame) -> list[dict]:
    linhas, vistas = [], {}
    cond = "município de V_k com >= 1 médico ativo ligado (e, na distância, com vínculo pré-início)"
    for y, (_, n_col) in OUTCOMES_RDD.items():
        sel_all = (pm[n_col] > 0).astype(float)
        for k in CICLOS_OUTCOME:
            d = pm[pm["ciclo"] == k]
            sel = (d[n_col] > 0)
            ds = d[sel]
            for c in CORTES_MIL:
                r = L.rd_local_linear(ds["s_mil"], ds[y], c, H_MIL)
                linhas.append(_linha("rdd_condicional", y, str(k), f"{c / 1000:.3f}", "local_linear_h050_hc1", cond, r))
                lee = L.limites_lee_rd(d["s_mil"], d[y].where(sel), sel.astype(float), c, H_MIL)
                ll = _linha("limites_lee", y, str(k), f"{c / 1000:.3f}", "lee_selecao_ter_medico_ligado",
                            "população V_k; selecionado = " + n_col + " > 0", {"nota": lee["nota"]})
                ll.update({"ic95_inf": lee["ic95_inf"], "ic95_sup": lee["ic95_sup"], "lee_tau_inf": lee["tau_inf"],
                           "lee_tau_sup": lee["tau_sup"], "lee_q_aparo": lee["q_aparo"],
                           "lee_lado_aparado": lee["lado_aparado"], "lee_salto_selecao": lee["salto_selecao"],
                           "lee_p0_selecao": lee["p0_selecao"], "lee_p1_selecao": lee["p1_selecao"],
                           "n_abaixo": lee["n_abaixo"], "n_acima": lee["n_acima"], "h_mil": H_MIL})
                linhas.append(ll)
                chave_sel = (k, c, tuple(sel.astype(int).tolist()))
                if chave_sel not in vistas:
                    vistas[chave_sel] = n_col
                    rs = L.rd_local_linear(d["s_mil"], sel.astype(float), c, H_MIL)
                    linhas.append(_linha("rdd_selecao", f"selecao_{n_col}_maior_que_0", str(k), f"{c / 1000:.3f}",
                                         "local_linear_h050_hc1", "população V_k (sem condicionar)", rs))
                else:
                    ll["nota"] = _juntar(ll["nota"], f"seleção idêntica a {vistas[chave_sel]} > 0 (linha rdd_selecao única)")
            ds2 = pd.concat([ds.assign(corte=c) for c in CORTES_MIL], ignore_index=True)
            r = L.rd_empilhado(ds2["s_mil"], ds2[y], ds2["corte"], h_mil=H_MIL, cluster=ds2["co_ibge"])
            linhas.append(_linha("rdd_condicional", y, str(k), "empilhado", "cortes_empilhados_h050_cr1_municipio",
                                 cond, r))
        dsel = pm[sel_all == 1]
        d3 = pd.concat([dsel.assign(corte=c) for c in CORTES_MIL], ignore_index=True)
        grupo = d3["ciclo"].astype(str) + "x" + d3["corte"].astype(str)
        r = L.rd_empilhado(d3["s_mil"], d3[y], d3["corte"], grupo=grupo, h_mil=H_MIL, cluster=d3["co_ibge"])
        linhas.append(_linha("rdd_condicional", y, "1+2", "empilhado",
                             "ciclos_e_cortes_empilhados_h050_cr1_municipio", cond, r))
    return linhas


# ---------------------------------------------------------------- E9 com distância (sensibilidade)

def ligar_candidatos(med: pd.DataFrame, listas: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Candidato alocado na 1ª chamada (pseudônimo da tarefa B) ↔ médico ativo ligado: mesma célula e nome compatível.

    Reconstrói, só em memória, o pseudônimo `id_candidato` do script 12 (ordem do hash de nome + CPF mascarado)
    e confere que a reconstrução reproduz as linhas de `escolhas_candidatos.parquet`; para se não reproduzir.
    """
    s12 = _importar("outcomes_funil_12_x1", SCRIPT_12)
    escolhas = pd.read_parquet(ESCOLHAS)
    fontes = {1: "c1_ch1", 2: "c2_ch1"}
    lig_partes, diag = [], {}
    for k, fonte in fontes.items():
        espec = s12.ESPEC_CANDIDATURAS[fonte]
        cand = s12.ler_candidaturas(espec)
        pid = {h: f"c{k}_{i + 1:05d}" for i, h in enumerate(sorted(cand["_pessoa"].unique()))}
        cab, _, linhas = s12.ler_aba(espec["caminho"], espec["aba"])
        i_cnes, i_curso = s12.coluna(cab, "CNES"), s12.coluna(cab, "CURSO")
        i_nome = s12.coluna(cab, "NOME CANDIDATO A", "NOME")
        i_cpf = s12.coluna(cab, "CPF", "CPF MASC", prefixo=True)
        i_ordem = s12.coluna(cab, "ORDEM DE PRIORIDADE ESCOLHIDA")
        reg = []
        for r in linhas:
            cnes, curso = s12.chave_cnes(s12.valor(r, i_cnes)), s12.chave_curso(s12.valor(r, i_curso))
            if cnes is None or curso is None:
                continue
            nome = s12.texto_norm(s12.valor(r, i_nome))
            pessoa = hashlib.sha256((nome + "|" + str(s12.valor(r, i_cpf) or "").strip()).encode("utf-8")).hexdigest()
            reg.append({"id_candidato": pid[pessoa], "co_cnes_7d": cnes, "cod_curso": curso,
                        "opcao_rank": s12.opcao(s12.valor(r, i_ordem)), "_nome": nome})
        rec = pd.DataFrame(reg)
        esc_k = escolhas[escolhas["ciclo"] == k]
        chave = ["id_candidato", "co_cnes_7d", "cod_curso", "opcao_rank"]
        a = rec[chave].astype(str).apply("|".join, axis=1)
        b = esc_k[chave].astype(str).apply("|".join, axis=1)
        if sorted(a) != sorted(b):
            raise AssertionError(f"ciclo {k}: reconstrução do pseudônimo não reproduz escolhas_candidatos (fail closed)")
        nomes_cand = rec.drop_duplicates("id_candidato").set_index("id_candidato")["_nome"]
        aloc = esc_k[esc_k["alocado"] == 1][["id_candidato", "co_cnes_7d", "cod_curso"]].drop_duplicates()
        aloc["_nome"] = aloc["id_candidato"].map(nomes_cand)
        mk = med[(med["ciclo"] == k) & (med["ligado"] == 1)][["id_medico", "co_cnes", "cod_curso"]].merge(
            listas[["id_medico", "_nome"]], on="id_medico")
        pares = aloc.merge(mk, left_on=["co_cnes_7d", "cod_curso"], right_on=["co_cnes", "cod_curso"],
                           suffixes=("_cand", "_med"))
        pares = pares[[nomes_compativeis(x, y) for x, y in zip(pares["_nome_cand"], pares["_nome_med"])]]
        unicos = pares[~pares["id_candidato"].duplicated(keep=False) & ~pares["id_medico"].duplicated(keep=False)]
        diag[f"ciclo_{k}"] = {"reconstrucao_pseudonimo": "reproduz escolhas_candidatos.parquet",
                              "candidatos_alocados_ch1": int(aloc["id_candidato"].nunique()),
                              "medicos_ativos_ligados": int(len(mk)),
                              "pares_mesma_celula_nome_compativel": int(len(pares)),
                              "pares_unicos": int(len(unicos))}
        lig_partes.append(unicos[["id_candidato", "id_medico"]].assign(ciclo=k))
    return pd.concat(lig_partes, ignore_index=True), diag


def e9_com_distancia(med: pd.DataFrame, listas: pd.DataFrame, coord: pd.DataFrame) -> tuple[list[dict], dict]:
    """Logit condicional da 1a opção com a distância de cada célula à origem pré-início do médico.

    A distância a uma célula é o mínimo, sobre TODOS os municípios em que o médico tinha vínculo médico na
    última competência pré-início, da distância ao município da célula. Ela não depende da célula escolhida
    nem do posto final (a versão anterior usava a origem mais próxima do posto final, o que embutia a
    escolha na distância; pedido da auditoria de X1).
    """
    e9 = _importar("e9_escolha_16_x1", SCRIPT_16)
    pares, diag = ligar_candidatos(med, listas)
    m = med.set_index("id_medico")
    diag["pares_total"] = int(len(pares))
    pares["_munis"] = pares["id_medico"].map(m["_munis_ultimo_pre"])
    sem_origem = pares["_munis"].isna()
    diag["excluidos_sem_vinculo_medico_na_ultima_competencia_pre"] = int(sem_origem.sum())
    pares = pares[~sem_origem]
    diag["pares_com_origem"] = int(len(pares))
    esc = pd.read_parquet(ESCOLHAS)
    r1 = esc[(esc["opcao_rank"] == 1) & esc["id_candidato"].isin(set(pares["id_candidato"]))]
    diag["excluidos_sem_linha_de_1a_opcao"] = int(len(set(pares["id_candidato"]) - set(r1["id_candidato"])))
    conj = pd.read_parquet(CONJ_PRINCIPAL)
    conj = conj[conj["ciclo"].isin(CICLOS_OUTCOME)]
    mapa, _ = e9.mapa_bolsa_por_faixa()
    conj, _ = e9.preparar_conjunto(conj, carregar_ivs(), mapa)
    macros = sorted(conj["macrorregiao"].unique())
    estratos = sorted(conj["estrato_territorial"].unique())
    xy = coord.set_index("co_ibge")
    munis_por_cand = pares.set_index("id_candidato")["_munis"]
    linhas_long, esc_idx, clus = [], [], []
    fora_conj = sem_coord = 0
    for r in r1.itertuples(index=False):
        alt = conj[conj["id_conjunto_escolha"] == r.id_conjunto_escolha].copy()
        pos = np.flatnonzero((alt["co_cnes_7d"] == r.co_cnes_7d).to_numpy() & (alt["cod_curso"] == r.cod_curso).to_numpy())
        if len(pos) != 1:
            fora_conj += 1
            continue
        munis = list(munis_por_cand.loc[r.id_candidato])
        if not all(mu in xy.index for mu in munis) or not alt["co_ibge"].isin(xy.index).all():
            sem_coord += 1
            continue
        lon_c, lat_c = xy.loc[alt["co_ibge"], "lon"].to_numpy(), xy.loc[alt["co_ibge"], "lat"].to_numpy()
        dist = np.min(np.vstack([haversine_km(xy.at[mu, "lon"], xy.at[mu, "lat"], lon_c, lat_c) for mu in munis]),
                      axis=0)
        alt["distancia_100km"] = dist / ESCALA_DISTANCIA_KM
        alt["_grupo"] = r.id_candidato
        esc_idx.append(sum(len(x) for x in linhas_long) + int(pos[0]))
        clus.append(r.id_conjunto_escolha)
        linhas_long.append(alt)
    diag["excluidos_1a_opcao_fora_do_conjunto"] = fora_conj
    diag["excluidos_sem_coordenada"] = sem_coord
    diag["candidatos_no_logit"] = len(linhas_long)
    diag["minimo_fixado"] = MIN_CANDIDATOS_E9_DIST
    diag["distancia"] = ("mínimo, sobre os municípios com vínculo médico na última competência pré-início, da "
                         "distância ao município da célula; independe da célula escolhida")
    if linhas_long:
        longo0 = pd.concat(linhas_long, ignore_index=True)
        escolhida = np.zeros(len(longo0), dtype=bool)
        escolhida[np.asarray(esc_idx)] = True
        diag["candidatos_com_distancia_zero_a_celula_escolhida"] = int((longo0.loc[escolhida, "distancia_100km"] == 0).sum())
        diag["fracao_das_alternativas_com_distancia_zero"] = float((longo0["distancia_100km"] == 0).mean())
    linhas = []
    if len(linhas_long) < MIN_CANDIDATOS_E9_DIST:
        nota = f"não estimado: {len(linhas_long)} candidatos < mínimo fixado de {MIN_CANDIDATOS_E9_DIST}"
        for espec in ("e9_principal_mesma_amostra", "e9_com_distancia"):
            linhas.append(_linha("e9_distancia", "bolsa_mil", "1+2", "—", espec, "alocados ligados com origem",
                                 {"nota": nota}))
        return linhas, diag
    longo = pd.concat(linhas_long, ignore_index=True)
    _, grupo_cel = np.unique(longo["_grupo"].to_numpy(), return_inverse=True)
    esc_arr = np.asarray(esc_idx)
    clus_arr = np.asarray(clus)
    from scipy import stats
    for espec, extra in (("e9_principal_mesma_amostra", []), ("e9_com_distancia", ["distancia_100km"])):
        X = e9.matriz_atributos(longo, 1, "linear", macros, estratos)
        for c in extra:
            X[c] = longo[c].to_numpy()
        omit = e9.colunas_sem_variacao(X, grupo_cel, np.arange(len(X)))
        X = X.drop(columns=omit)
        Xa = X.to_numpy(dtype=float)
        try:
            fit = e9.ajustar_logit(Xa, grupo_cel, esc_arr)
        except (np.linalg.LinAlgError, FloatingPointError) as erro:
            linhas.append(_linha("e9_distancia", "bolsa_mil", "1+2", "—", espec, "alocados ligados com origem",
                                 {"nota": f"estimação falhou ({type(erro).__name__})"}))
            continue
        info_inv = np.linalg.inv(fit["info"])
        V, G = e9.covariancia_cluster(info_inv, fit["scores"], clus_arr)
        for termo in ["bolsa_mil"] + extra:
            if termo not in X.columns:
                continue
            j = list(X.columns).index(termo)
            b, ep = float(fit["theta"][j]), float(math.sqrt(max(V[j, j], 0.0)))
            ep_mv = float(math.sqrt(max(info_inv[j, j], 0.0)))
            z = b / ep if ep > 0 else np.nan
            p = float(2 * stats.norm.sf(abs(z))) if np.isfinite(z) else np.nan
            nota = (f"logit condicional da 1a opção, ciclos 1+2; EP sanduíche por conjunto (curso × ciclo), "
                    f"G = {G}; EP de MV = {ep_mv:.6g}; convergiu = {fit['convergiu']}; omitidas: {', '.join(omit) or '—'}"
                    "; amostra selecionada (alocados, ativos, ligados, com vínculo pré-início)")
            lin = _linha("e9_distancia", termo, "1+2", "—", espec, "alocados ligados com origem",
                         {"tau": b, "ep": ep, "ic95_inf": b - L.Z_975 * ep, "ic95_sup": b + L.Z_975 * ep,
                          "p_valor": p, "n_obs": len(esc_arr), "n_clusters": G, "nota": nota})
            linhas.append(lin)
    return linhas, diag


# ---------------------------------------------------------------- doc 46

MARCA = re.compile(r"(<!-- X1:(?P<nome>[A-Za-z0-9_]+):inicio -->\n)(?P<corpo>.*?)(\n<!-- X1:(?P=nome):fim -->)", re.S)


def fmt(x: Any, casas: int = 3) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)) or x is pd.NA:
        return "—"
    return f"{float(x):.{casas}f}".replace("-", "−").replace(".", ",")


def fmt_pct(x: Any, casas: int = 1) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    return fmt(100 * float(x), casas) + "%"


def fmt_p(p: Any) -> str:
    if p is None or (isinstance(p, float) and not math.isfinite(p)):
        return "—"
    return "< 0,001" if p < 0.001 else fmt(p, 3)


def fmt_int(x: Any) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    return f"{int(x):,}".replace(",", ".")


def ler_saidas() -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    resumo = json.loads(OUT_RESUMO.read_text(encoding="utf-8"))
    est = pd.read_csv(OUT_ESTIMATIVAS, dtype={"ciclo": str, "corte": str})
    desc = pd.read_csv(OUT_DESCRITIVO, dtype={"ciclo": str})
    return resumo, est, desc


ROTULO_REGRA = {"literal_doc45": "literal (protocolo, doc 45)", "d1_pos_hoc": "D1 (correção pós-hoc)"}


def blocos_doc(resumo: dict, est: pd.DataFrame, desc: pd.DataFrame) -> dict[str, str]:
    b: dict[str, str] = {}
    # Ligação, nas duas regras.
    t = ["| Regra | Ciclo | Registros | Ligados | Taxa | Etapa 1 (CRM+UF) | Etapa 2 (CRM+nome) | Ambíguos | Não achados |",
         "|---|---|---|---|---|---|---|---|---|"]
    for regra in REGRAS:
        for ciclo in ("1", "2", "3"):
            r = resumo["taxas_ligacao"][regra][ciclo]
            t.append(f"| {ROTULO_REGRA[regra]} | {ciclo} | {fmt_int(r['registros'])} | {fmt_int(r['ligados'])} | "
                     f"{fmt_pct(r['taxa'])} | {fmt_int(r['etapa_1_crm_uf'])} | {fmt_int(r['etapa_2_crm_nome'])} | "
                     f"{fmt_int(r['ambiguos'])} | {fmt_int(r['nao_ligados_sem_ambiguidade'])} |")
    t.append("")
    for regra in REGRAS:
        mot = resumo["taxas_ligacao"][regra]["motivos"]
        t.append(f"Motivos, regra {ROTULO_REGRA[regra]}: " + "; ".join(f"{k}: {fmt_int(v)}" for k, v in mot.items()) + ".")
    d1 = resumo["diagnostico_ligacao"]["d1_pos_hoc"]
    t.append(f"Etapa 1 (CRM + UF do posto) com candidato único: {fmt_int(d1['etapa1_candidato_unico'])}; com nome "
             f"compatível: {fmt_int(d1['etapa1_nome_compativel'])} ({fmt_pct(d1['etapa1_fracao_nome_compativel'])}). "
             f"Sem nome compatível: {fmt_int(d1['etapa1_rejeitadas_por_nome'])}; a literal os liga, D1 os manda para a "
             f"etapa 2, onde {fmt_int(d1['etapa1_rejeitadas_ligadas_na_etapa2'])} ligam.")
    t.append("Conferência (ligados com início antes de 202608 com vínculo médico no estabelecimento do posto em "
             "202608): " + "; ".join(
                 f"{ROTULO_REGRA[regra]}, {etapa}: {fmt_pct(v['fracao_com_vinculo_no_estab_do_posto_202608'])} de "
                 f"{fmt_int(v['n'])}"
                 for regra in REGRAS
                 for etapa, v in resumo["diagnostico_ligacao"][regra]["conferencia_vinculo_no_estab_do_posto_202608"].items())
             + ".")
    cr = resumo["comparacao_entre_regras"]
    t.append(f"Entre as regras: mesmo profissional em {fmt_int(cr['mesmo_profissional_nas_duas_regras'])} registros; "
             f"profissional diferente em {fmt_int(cr['profissional_diferente_entre_as_regras'])}; ligado só na literal: "
             f"{fmt_int(cr['ligado_so_na_literal'])}; só em D1: {fmt_int(cr['ligado_so_na_d1'])}.")
    cc = resumo["conselho_classe"]
    fora = resumo["diagnostico_ligacao"]["d1_pos_hoc"]["vinculos_medicos_fora_do_conselho_crm_excluidos_da_busca"]
    t.append(f"Conselho: só entram na busca vínculos com CO_CONSELHO_CLASSE = {cc['codigo_crm']} ({cc['descricao']}, "
             f"tbOrgaoEmissor de {cc['competencia']}); vínculos médicos com outro código, fora da busca, somadas as "
             f"seis competências: {fmt_int(fora)} ({fmt_pct(1 - cc['fracao_dos_vinculos_medicos_com_o_codigo'], 2)}).")
    b["ligacao"] = "\n".join(t)

    def tab_desc(regra: str) -> str:
        d = desc[(desc["fonte_lista"] == "todas") & (desc["regra_ligacao"] == regra)]

        def v(ciclo, faixa, ind):
            x = d[(d["ciclo"] == ciclo) & (d["faixa"] == faixa) & (d["indicador"] == ind)]
            return x.iloc[0]

        t = ["| Ciclo | Faixa | Ligados | (a) mesmo estab. | (b) mesmo município | Novo no município | Mesma região | "
             "Mesma UF | Outra UF | Sem vínculo médico | Distância média (km) | Distância mediana (km) | "
             "(e) vínculos em 202608 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for ciclo in ("1", "2", "1+2"):
            for faixa in ("FAIXA 3", "FAIXA 2", "FAIXA 1", "todas"):
                cel = [fmt_pct(v(ciclo, faixa, i)["valor"]) for i in (
                    "a_mesmo_estab_ultimo_pre", "b_mesmo_mun_ultimo_pre", "novo_no_municipio",
                    "origem_mesma_regiao_saude", "origem_mesma_uf", "origem_outra_uf",
                    "origem_sem_vinculo_medico_anterior")]
                t.append(f"| {ciclo} | {faixa} | {fmt_int(v(ciclo, faixa, 'b_mesmo_mun_ultimo_pre')['n_base'])} | "
                         + " | ".join(cel) + f" | {fmt(v(ciclo, faixa, 'd_distancia_km')['valor'], 0)} | "
                         f"{fmt(v(ciclo, faixa, 'd_distancia_km_mediana')['valor'], 0)} | "
                         f"{fmt(v(ciclo, faixa, 'e_vinculos_202608')['valor'], 2)} |")
        return "\n".join(t)

    b["descritivo"] = tab_desc("literal_doc45")
    b["descritivo_d1"] = tab_desc("d1_pos_hoc")

    # Mês de referência de "já estava no município".
    t = ["| Regra | Ciclo | Ligados | Última competência pré-início | " + " | ".join(MESES_FIXOS) +
         " | Faixa (mín.–máx.) | A última é o máximo? | Persistência: incumbentes já presentes em " + MESES_FIXOS[0] + " |",
         "|---|---|---|---|" + "---|" * len(MESES_FIXOS) + "---|---|---|"]
    for regra in REGRAS:
        for ciclo, r in resumo["mesmo_municipio_por_mes_de_referencia"][regra].items():
            fr = r["fracao_por_referencia"]
            ps = r["persistencia"]
            t.append(f"| {ROTULO_REGRA[regra]} | {ciclo} | {fmt_int(r['n_ligados'])} | {fmt_pct(fr['ultima_competencia_pre'])} | "
                     + " | ".join(fmt_pct(fr[m]) for m in MESES_FIXOS) +
                     f" | {fmt_pct(r['minimo'])}–{fmt_pct(r['maximo'])} | "
                     f"{'sim' if r['ultima_competencia_pre_e_o_maximo'] else 'não'} | {fmt_pct(ps['fracao'])} "
                     f"({fmt_int(ps['ja_presentes_em_' + MESES_FIXOS[0]])} de "
                     f"{fmt_int(ps['incumbentes_na_ultima_competencia_pre'])}) |")
    b["mes_referencia"] = "\n".join(t)

    # RDD condicional e Lee, lado a lado nas duas regras.
    rot = {"frac_novos_no_municipio": "novos no município", "frac_outra_uf": "outra UF",
           "distancia_media_km": "distância média (km)"}
    e = est[est["analise"] == "rdd_condicional"]
    lee = est[est["analise"] == "limites_lee"]
    t = ["| Outcome | Ciclo | Corte | Regra | Salto | IC 95% | p | q BKY (X1, por regra) | N abaixo / acima | "
         "Lee: limites | Lee: IC 95% conservador |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for y in rot:
        casas = 0 if y == "distancia_media_km" else 3
        chaves = e[e["outcome"] == y][["ciclo", "corte"]].drop_duplicates().itertuples(index=False)
        for ciclo, corte in chaves:
            for regra in REGRAS:
                r = e[(e["outcome"] == y) & (e["ciclo"] == ciclo) & (e["corte"] == corte)
                      & (e["regra_ligacao"] == regra)].iloc[0]
                lr = lee[(lee["outcome"] == y) & (lee["ciclo"] == ciclo) & (lee["corte"] == corte)
                         & (lee["regra_ligacao"] == regra)]
                if len(lr):
                    l0 = lr.iloc[0]
                    lim = f"[{fmt(l0['lee_tau_inf'], casas)}; {fmt(l0['lee_tau_sup'], casas)}]"
                    lic = f"[{fmt(l0['ic95_inf'], casas)}; {fmt(l0['ic95_sup'], casas)}]"
                else:
                    lim = lic = "não se aplica (empilhado)"
                cr_ = corte.replace(".", ",") if corte != "empilhado" else "empilhado"
                t.append(f"| {rot[y]} | {ciclo} | {cr_} | {ROTULO_REGRA[regra]} | {fmt(r['tau'], casas)} | "
                         f"[{fmt(r['ic95_inf'], casas)}; {fmt(r['ic95_sup'], casas)}] | {fmt_p(r['p_valor'])} | "
                         f"{fmt(r['q_bky_x1'], 3)} | {fmt_int(r['n_abaixo'])} / {fmt_int(r['n_acima'])} | {lim} | {lic} |")
    b["rdd"] = "\n".join(t)

    # Seleção.
    s_ = est[(est["analise"] == "rdd_selecao") & (est["outcome"] == "selecao_n_ligados_maior_que_0")]
    t = ["| Regra | Ciclo | Corte | Salto na fração de municípios de V_k com médico ligado | IC 95% | p |",
         "|---|---|---|---|---|---|"]
    for _, r in s_.iterrows():
        t.append(f"| {ROTULO_REGRA[r['regra_ligacao']]} | {r['ciclo']} | {r['corte'].replace('.', ',')} | "
                 f"{fmt(r['tau'], 3)} | [{fmt(r['ic95_inf'], 3)}; {fmt(r['ic95_sup'], 3)}] | {fmt_p(r['p_valor'])} |")
    b["selecao"] = "\n".join(t)

    # E9 com distância.
    e9 = est[est["analise"] == "e9_distancia"]
    t = ["| Regra | Especificação | Termo | Coeficiente | IC 95% (cluster por conjunto) | p | q BKY | Candidatos | Conjuntos |",
         "|---|---|---|---|---|---|---|---|---|"]
    for _, r in e9.iterrows():
        t.append(f"| {ROTULO_REGRA[r['regra_ligacao']]} | {r['especificacao']} | {r['outcome']} | {fmt(r['tau'], 3)} | "
                 f"[{fmt(r['ic95_inf'], 3)}; {fmt(r['ic95_sup'], 3)}] | {fmt_p(r['p_valor'])} | {fmt(r['q_bky_x1'], 3)} | "
                 f"{fmt_int(r['n_obs'])} | {fmt_int(r['n_clusters'])} |")
    t.append("")
    for regra in REGRAS:
        de = resumo["e9_distancia"]["diagnostico"][regra]
        t.append(f"Amostra, regra {ROTULO_REGRA[regra]}: pares candidato alocado–médico ligado: "
                 f"{fmt_int(de['pares_total'])}; sem vínculo médico na última competência pré-início: "
                 f"{fmt_int(de['excluidos_sem_vinculo_medico_na_ultima_competencia_pre'])}; sem linha de 1ª opção: "
                 f"{fmt_int(de['excluidos_sem_linha_de_1a_opcao'])}; 1ª opção fora do conjunto: "
                 f"{fmt_int(de['excluidos_1a_opcao_fora_do_conjunto'])}; sem coordenada: "
                 f"{fmt_int(de['excluidos_sem_coordenada'])}; no logit: {fmt_int(de['candidatos_no_logit'])}, dos quais "
                 f"{fmt_int(de['candidatos_com_distancia_zero_a_celula_escolhida'])} com distância zero à célula "
                 f"escolhida.")
    b["e9"] = "\n".join(t)

    # Contagens de BKY, por regra.
    partes = []
    for regra in REGRAS:
        x = est[est["regra_ligacao"] == regra]
        q, pv = x["q_bky_x1"].dropna(), x["p_valor"].dropna()
        partes.append(f"Regra {ROTULO_REGRA[regra]}: linhas com p: {fmt_int(len(pv))}; com p < 0,05: "
                      f"{fmt_int((pv < 0.05).sum())}; com q BKY < 0,05: {fmt_int((q < 0.05).sum())}; menor q: "
                      f"{fmt(q.min() if len(q) else np.nan, 3)}.")
    b["bky"] = "\n".join(partes)
    return b


def blocos_no_doc(texto: str) -> dict[str, str]:
    return {m.group("nome"): m.group("corpo") for m in MARCA.finditer(texto)}


def atualizar_doc() -> None:
    resumo, est, desc = ler_saidas()
    gerados = blocos_doc(resumo, est, desc)
    texto = DOC_46.read_text(encoding="utf-8")
    no_doc = blocos_no_doc(texto)
    if set(no_doc) != set(gerados):
        raise SystemExit(f"blocos do doc 46 ({sorted(no_doc)}) diferem dos gerados ({sorted(gerados)})")
    novo = MARCA.sub(lambda m: m.group(1) + gerados[m.group("nome")] + m.group(4), texto)
    DOC_46.write_text(novo, encoding="utf-8")
    log(f"doc 46: {len(gerados)} blocos X1 atualizados")


# ---------------------------------------------------------------- principal

def bloco_entrada(caminho: Path, papel: str, data_ref: str, cobertura: str, unidade: str, chaves: str,
                  filtros: str) -> dict:
    return {"caminho": rel(caminho), "sha256": sha256_arquivo(caminho), "bytes": caminho.stat().st_size,
            "papel": papel, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade,
            "chaves": chaves, "filtros": filtros}


def taxas_ligacao(mm: pd.DataFrame) -> dict:
    out = {}
    for k in ("1", "2", "3", "total"):
        d = mm if k == "total" else mm[mm["ciclo"] == int(k)]
        amb = d["motivo"].str.startswith("ambiguo")
        out[k] = {"registros": int(len(d)), "ligados": int(d["ligado"].sum()), "taxa": float(d["ligado"].mean()),
                  "etapa_1_crm_uf": int((d["etapa_ligacao"] == "1_crm_uf").sum()),
                  "etapa_2_crm_nome": int((d["etapa_ligacao"] == "2_crm_nome").sum()),
                  "ambiguos": int(amb.sum()), "nao_ligados_sem_ambiguidade": int(((d["ligado"] == 0) & ~amb).sum())}
    out["por_fonte_lista"] = {f: {"registros": int(len(g)), "ligados": int(g["ligado"].sum()),
                                  "taxa": float(g["ligado"].mean())} for f, g in mm.groupby("fonte_lista")}
    out["motivos"] = {k: int(v) for k, v in mm["motivo"].value_counts().sort_index().items()}
    return out


def faixa_mesmo_municipio(mm: pd.DataFrame) -> dict:
    """Fração com vínculo no município do posto conforme o mês de referência, e persistência dos incumbentes."""
    out = {}
    for ciclo, cs in (("1", [1]), ("2", [2]), ("1+2", [1, 2])):
        lig = mm[mm["ciclo"].isin(cs) & (mm["ligado"] == 1)]
        valores = {"ultima_competencia_pre": float(lig["b_mesmo_mun_ultimo_pre"].dropna().mean())}
        for mf in MESES_FIXOS:
            valores[mf] = float(lig[f"b_mesmo_mun_em_{mf}"].dropna().mean())
        inc = lig[lig["b_mesmo_mun_ultimo_pre"] == 1]
        out[ciclo] = {"n_ligados": int(len(lig)), "fracao_por_referencia": valores,
                      "minimo": min(valores.values()), "maximo": max(valores.values()),
                      "ultima_competencia_pre_e_o_maximo": valores["ultima_competencia_pre"] == max(valores.values()),
                      "persistencia": {"incumbentes_na_ultima_competencia_pre": int(len(inc)),
                                       f"ja_presentes_em_{MESES_FIXOS[0]}":
                                           int(inc[f"b_mesmo_mun_em_{MESES_FIXOS[0]}"].sum()),
                                       "fracao": float(inc[f"b_mesmo_mun_em_{MESES_FIXOS[0]}"].mean())}}
    return out


def analisar() -> None:
    listas, diag_listas = ler_listas_pmme()
    vinc, nomes, metas = ler_cache()
    if assinatura_alvo(crms_alvo(listas)) != metas[COMPETENCIAS[0]]["assinatura_alvo"]:
        raise SystemExit("listas do PMM-E mudaram desde a extração; refaça a aquisição (fail closed)")
    ivs = carregar_ivs()
    regiao, diag_reg = mapa_regiao_saude(vinc)
    coord, diag_coord = ler_coordenadas()

    # Faixa: a da lista, conferida contra a regra de dois cortes do IVS oficial.
    s_mil = np.round(listas["co_ibge"].map(ivs).to_numpy() * 1000.0)
    regra = np.where(np.isnan(s_mil), "", faixa_pela_regra(np.nan_to_num(s_mil)))
    tem = ~np.isnan(s_mil)
    discord = int((regra[tem] != listas["faixa_atracao"].to_numpy()[tem]).sum())
    if discord:
        raise AssertionError(f"faixa da lista difere da regra do IVS oficial em {discord} registros (fail closed)")
    listas["faixa"] = listas["faixa_atracao"]

    conselho_crm, diag_conselho = codigo_conselho_crm(vinc)
    # Fail closed: toda competência do cache veio de ZIP com o mesmo SHA-256 do a09.
    sem_a09 = [c for c, m in metas.items() if not m.get("validacao_contra_a09", {}).get("sha256_igual_ao_a09")]
    if sem_a09:
        raise AssertionError(f"competências com SHA-256 diferente do a09: {sem_a09} (fail closed)")
    meds: dict[str, pd.DataFrame] = {}
    diags_lig: dict[str, dict] = {}
    for regra, exigir in REGRAS.items():
        lig, dg = ligar(listas, vinc, nomes, conselho_crm=conselho_crm, exigir_nome_etapa1=exigir)
        mm = listas.merge(lig, on="id_medico", validate="one_to_one")
        mm["ligado"] = mm["co_profissional_sus"].notna().astype(int)
        dup = mm[mm["ligado"] == 1].duplicated(["ciclo", "co_profissional_sus"], keep=False)
        dg["profissional_ligado_a_mais_de_um_registro_do_mesmo_ciclo"] = int(dup.sum())
        meds[regra], diags_lig[regra] = mm, dg
    comp = meds["d1_pos_hoc"][["id_medico", "co_profissional_sus"]].merge(
        meds["literal_doc45"][["id_medico", "co_profissional_sus"]], on="id_medico", suffixes=("_d1", "_lit"))
    a_, b_ = comp["co_profissional_sus_d1"], comp["co_profissional_sus_lit"]
    comparacao_regras = {
        "mesmo_profissional_nas_duas_regras": int((a_.notna() & b_.notna() & (a_ == b_)).sum()),
        "profissional_diferente_entre_as_regras": int((a_.notna() & b_.notna() & (a_ != b_)).sum()),
        "ligado_so_na_literal": int((a_.isna() & b_.notna()).sum()),
        "ligado_so_na_d1": int((a_.notna() & b_.isna()).sum())}

    # Validação da região: CIR do painel do PMMB × regiao_saude da lista de ativos, nos municípios do PMM-E.
    with zipfile.ZipFile(ATIVOS_ZIP) as z:
        a = pd.read_csv(io.BytesIO(z.read(z.namelist()[0])), sep=";", dtype=str, encoding="latin1",
                        usecols=["co_ibge", "uf", "regiao_saude"])
    a["co_ibge"] = a["co_ibge"].str[:6]
    a = a.drop_duplicates()
    a["lista"] = a["uf"].str.strip().str.upper() + "|" + a["regiao_saude"].map(texto_norm)
    a["ppf"] = a["co_ibge"].map(regiao)
    diag_reg["conferencia_lista_ativos"] = {
        "municipios": int(len(a)), "com_regiao_no_ppf": int(a["ppf"].notna().sum()),
        "regiao_igual": int((a["ppf"] == a["lista"]).sum())}
    if diag_reg["conferencia_lista_ativos"]["regiao_igual"] != len(a):
        raise AssertionError(f"região de saúde do PPF difere da lista de ativos: {diag_reg['conferencia_lista_ativos']}")

    vmun = pd.read_parquet(V_MUNICIPIO, columns=["ciclo", "co_ibge"])
    descs, ests, saidas_med, diag_pm, diags_e9, taxas, faixa_mes = [], [], [], {}, {}, {}, {}
    for regra, mm in meds.items():
        out = outcomes_medico(mm[mm["ciclo"].isin(CICLOS_OUTCOME)], vinc, regiao, coord)
        mm = mm.merge(out, on="id_medico", how="left", validate="one_to_one")
        meds[regra] = mm
        cp = {}
        for etapa in ("1_crm_uf", "2_crm_nome"):
            x = mm.loc[(mm["etapa_ligacao"] == etapa), "vinculo_no_estab_do_posto_202608"].dropna()
            cp[etapa] = {"n": int(len(x)),
                         "fracao_com_vinculo_no_estab_do_posto_202608": float(x.mean()) if len(x) else None}
        diags_lig[regra]["conferencia_vinculo_no_estab_do_posto_202608"] = cp
        # E9 com distância (usa nome só em memória).
        if diag_coord["status"] == "OBTIDO":
            linhas_e9, diags_e9[regra] = e9_com_distancia(mm, listas, coord)
        else:
            linhas_e9, diags_e9[regra] = [], {"status": "não estimado: coordenadas indisponíveis"}
        descs.append(descritivo(mm, regra))
        pm, diag_pm[regra] = painel_municipio(mm, vmun, ivs)
        e = pd.DataFrame(estimar_rdd(pm) + linhas_e9)
        e["regra_ligacao"] = regra
        # BKY dentro do X1, uma família por regra de ligação (as duas regras repetem as mesmas hipóteses).
        e["q_bky_x1"] = L.qvalores_bky(e["p_valor"].to_numpy(dtype=float))
        ests.append(e[COLS_EST])
        taxas[regra] = taxas_ligacao(mm)
        faixa_mes[regra] = faixa_mesmo_municipio(mm)
        cols_med = ["id_medico", "ciclo", "fonte_lista", "co_ibge", "faixa", "ligado", "etapa_ligacao",
                    "etapa1_rejeitada_por_nome", "motivo", "competencias_pre_inicio", "ultima_competencia_pre",
                    "a_mesmo_estab_ultimo_pre", "a_mesmo_estab_algum_pre", "b_mesmo_mun_ultimo_pre",
                    "b_mesmo_mun_algum_pre"] + [f"b_mesmo_mun_em_{m}" for m in MESES_FIXOS] + [
                    f"a_mesmo_estab_em_{m}" for m in MESES_FIXOS] + [
                    "vinculo_medico_algum_pre", "vinculos_ultimo_pre", "c_origem", "motivo_origem_ausente",
                    "d_distancia_km", "motivo_distancia_ausente", "e_vinculos_202608", "e_estabelecimentos_202608",
                    "e_municipios_202608", "vinculo_no_estab_do_posto_202608"]
        for c in cols_med:
            if c not in mm:
                mm[c] = pd.NA
        sm = mm[cols_med].rename(columns={"motivo": "motivo_ligacao"}).copy()
        sm.insert(1, "regra_ligacao", regra)
        saidas_med.append(sm)
    desc = pd.concat(descs, ignore_index=True)
    est = pd.concat(ests, ignore_index=True)
    saida_med = pd.concat(saidas_med, ignore_index=True)
    saida_med["natureza_dos_dados"] = NATUREZA
    saida_med["estatuto"] = ESTATUTO
    saida_med = saida_med.sort_values(["regra_ligacao", "id_medico"]).reset_index(drop=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    saida_med.to_parquet(OUT_MEDICOS, index=False)
    est.to_csv(OUT_ESTIMATIVAS, index=False)
    desc.to_csv(OUT_DESCRITIVO, index=False)

    competencias = {}
    for c, m in metas.items():
        competencias[c] = {k: m.get(k) for k in (
            "url", "data_download", "sha256_zip", "bytes_zip", "membros_lidos", "linhas_tbCargaHorariaSus",
            "linhas_vinculos_medicos", "vinculos_sem_estabelecimento", "vinculos_sem_registro", "vinculos_sem_uf_crm",
            "conselho_classe_dos_vinculos_medicos", "profissionais_distintos", "vinculos_com_registro_no_alvo",
            "profissionais_com_registro_no_alvo", "profissionais_alvo_com_nome", "validacao_contra_a09",
            "data_processamento", "status")}
    entradas = [
        bloco_entrada(ATIVOS_ZIP, "lista nominal de ativos do PMM-E (CRM, UF do posto, CNES, curso, início, ciclo, nome)",
                      "dt_referencia 11/09/2026", "ciclos 1–3, Brasil", "registro de médico ativo",
                      "ciclo, crm, uf, co_cnes, curso", "nenhum; nome só em memória"),
        bloco_entrada(NOMINAL_CSV, "lista nominal de 12/08/2026 (registros que não estão nos ativos de 11/09 entram)",
                      "dt_referencia 2026-08-12", "ciclos 1–2", "registro de médico ativo",
                      "ciclo, crm, uf, co_cnes, curso", "nenhum; nome só em memória"),
        bloco_entrada(IVS_OFICIAL, "running variable (IVS 2010 oficial) e conferência da faixa", "Censo 2010",
                      f"{len(ivs)} municípios", "município", "co_ibge", "colunas co_ibge e ivs"),
        bloco_entrada(V_MUNICIPIO, "populações V1 e V2 (municípios com célula no quadro da 1a chamada)", "ciclos 1–2",
                      "V1, V2", "ciclo × município", "ciclo, co_ibge", "colunas ciclo e co_ibge"),
        bloco_entrada(MANIFESTO_A09, "SHA-256 e contagem de vínculos médicos por competência (validação)",
                      "2026-10-18", "competências do a09", "competência", "competencia", "por_competencia"),
        bloco_entrada(ESCOLHAS, "E9 com distância: escolhas e alocação da 1a chamada", "ciclos 1–2",
                      "candidatos", "candidato × opção", "ciclo, id_candidato, opcao_rank", "ciclos 1 e 2"),
        bloco_entrada(CONJ_PRINCIPAL, "E9 com distância: conjunto de escolha principal", "ciclos 1–2",
                      "células", "célula", "ciclo, co_cnes_7d, cod_curso", "ciclos 1 e 2"),
        bloco_entrada(PPF_ZIP, "região de saúde (CIR) por município, painel do PMMB do MS", "dt_referencia 2026-10-09",
                      f"{diag_reg['municipios']} municípios (nível MUNICIPAL)", "município", "co_ibge", "nivel = MUNICIPAL; colunas uf, cir"),
        bloco_entrada(PROTOCOLO_45, "protocolo congelado do X1", "19/10/2026", "—", "—", "—", "—"),
    ]
    if COORD_JSON.exists():
        entradas.append(bloco_entrada(COORD_JSON, "centroides municipais oficiais (distância)",
                                      f"malha municipal {diag_coord.get('malha_periodo_verificado', 'não verificada')}",
                                      "municípios do Brasil", "município", "id (7 dígitos)", "centroide"))
    s12 = _importar("outcomes_funil_12_x1_ent", SCRIPT_12)
    for fonte in ("c1_ch1", "c2_ch1"):
        p = s12.ESPEC_CANDIDATURAS[fonte]["caminho"]
        entradas.append(bloco_entrada(p, f"E9 com distância: nomes dos candidatos ({fonte}), só em memória",
                                      "resultado da 1a chamada", "candidatos", "candidato × opção",
                                      "CNES, curso, nome, CPF mascarado", "nenhum gravado"))
    resumo = {
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "documento": "X1 do protocolo exploratório pós-síntese (doc 45, §3)",
        "script": rel(Path(__file__)),
        "protocolo": rel(PROTOCOLO_45),
        "data_execucao": dt.date.today().isoformat(),
        "contraste": ("descritivo da origem dos médicos do PMM-E; RDD condicional à alocação com limites de Lee: "
                      "pacote do corte (RDD em nível), não efeito da participação no PMM-E nem do Agora Tem "
                      "Especialistas"),
        "entradas": entradas,
        "competencias_cnes": competencias,
        "limite_ciclo3": f"nenhuma competência >= {LIMITE_EXCLUSIVO} é baixada ou lida",
        "regra_ligacao": {
            "literal_doc45": ("regra do protocolo congelado (doc 45): (1) NU_REGISTRO = CRM e SG_UF_CRM = UF da lista, um "
                              "único CO_PROFISSIONAL_SUS nas seis competências; (2) sem (1), NU_REGISTRO = CRM em qualquer "
                              "UF com nome compatível, um único profissional; ambíguos e não achados ficam fora"),
            "d1_pos_hoc": ("correção pós-hoc D1: igual à literal, mas o candidato único da etapa 1 só liga com nome "
                           "compatível; sem ele, o registro vai para a etapa 2"),
            "conselho": "só vínculos médicos com CO_CONSELHO_CLASSE do CRM entram na busca",
        },
        "conselho_classe": diag_conselho,
        "regra_nome_compativel": ("tokens normalizados sem partículas " + ",".join(sorted(PARTICULAS)) +
                                  "; mesmo primeiro nome e (mesmo último ou um conjunto contido no outro, ≥ 2 nomes)"),
        "listas_pmme": diag_listas,
        "taxas_ligacao": taxas,
        "diagnostico_ligacao": diags_lig,
        "comparacao_entre_regras": comparacao_regras,
        "mesmo_municipio_por_mes_de_referencia": faixa_mes,
        "desvios": [{
            "id": "D1", "data": "2026-10-19",
            "o_que": "etapa 1 (CRM+UF) passa a exigir nome compatível; sem ele, o registro vai para a etapa 2",
            "motivo": ("a UF das listas do PMM-E é a do posto, não a do CRM; na regra literal, um CRM de outra UF "
                       "colide com o registro de outra pessoa na UF do posto. A conferência de nomes da etapa 1 "
                       "mostrou ligações sem nenhum nome em comum e sem vínculo no estabelecimento do posto"),
            "honestidade": ("correção pós-hoc: decidida depois da primeira execução completa do script, que gravou e "
                            "exibiu as estimativas com a regra literal. Ela leva as linhas mais próximas de "
                            "significância em direção a zero; por isso a regra literal, que é a do protocolo, é "
                            "relatada lado a lado em todas as saídas"),
            "relato": "todas as saídas trazem as duas regras (coluna regra_ligacao)",
        }],
        "regiao_saude": diag_reg,
        "coordenadas": diag_coord,
        "painel_municipio": diag_pm,
        "e9_distancia": {"diagnostico": diags_e9,
                         "substitui": ("versão de e02d83a, em que a distância usava a origem mais próxima do posto "
                                       "final (escolha embutida na distância); retirada pela auditoria de X1")},
        "definicoes": {
            "mes_inicio": "AAAAMM de dt_inicio_atividade",
            "competencias_pre_inicio": "competências lidas estritamente anteriores ao mês de início",
            "vinculo_medico": "linha de tbCargaHorariaSus com CBO iniciando em 2251, 2252, 2253 ou 2231",
            "origem": "última competência pré-início; mesmo_municipio > mesma_regiao_saude > mesma_uf > outra_uf; "
                      "sem linha nessa competência: sem_vinculo_medico_anterior",
            "distancia": f"círculo máximo (raio médio de {RAIO_TERRA_KM} km) entre centroides do IBGE, do município de "
                         "origem mais próximo ao do posto (descritivo e RDD); no E9, mínimo sobre os municípios de "
                         "origem até cada célula do conjunto",
            "meses_fixos": (f"(b) e (a) também em {', '.join(MESES_FIXOS)}, os mesmos para todos; persistência = "
                            f"fração, entre os que têm (b) na última competência pré-início, dos que já o tinham em "
                            f"{MESES_FIXOS[0]}"),
            "e": f"vínculos médicos na competência {COMPETENCIA_POS}, para mês de início < {COMPETENCIA_POS}",
            "rdd": "local linear, kernel triangular, h = 0,050, HC1 por corte; CR1 por município nos empilhados",
            "lee": "rdd_lib.limites_lee_rd por ciclo × corte; selecionado = município de V_k com >= 1 médico ligado "
                   "(n_ligados, n_ligados_origem ou n_com_distancia > 0, conforme o outcome)",
            "bky": ("q aguçados de Benjamini, Krieger e Yekutieli sobre todas as linhas do X1 com p, uma família por "
                    "regra de ligação"),
        },
        "limitacoes": [
            "a UF das listas é a do posto; CRM em outra UF só liga pela etapa 2 (nome)",
            "vínculo no CNES não é presença nem trabalho efetivo; ausência de vínculo não prova ausência de atividade",
            "competências pré-início são esparsas (seis meses lidos); a última pode estar meses antes do início",
            "outcome condicional à alocação e à ligação: a RDD condicional não é causal; os limites de Lee supõem "
            "monotonicidade da seleção",
            "o retrato de ativos exclui quem saiu antes de 11/09/2026 (só a lista de 12/08 recupera parte)",
            "E9 com distância: amostra de alocados ligados, selecionada pela alocação; a origem é a do CNES pré-início",
        ],
        "dados_pessoais": ("nenhum nome, CPF, CNS, CRM ou código de profissional é gravado em output/rdd_bolsa/X1_*; "
                           "o cache com registro e nome normalizado fica em output/rdd_bolsa/X1_cache/ (ignorado pelo "
                           "Git). O pseudônimo id_medico é FRACO: ciclo, município e faixa, cruzados com a lista nominal "
                           "pública do PMM-E e com o CNES público, podem reidentificar o médico. Por isso o parquet não "
                           "traz mês de início nem curso; não deve ser cruzado com dados nominais"),
        "saidas": {rel(p): sha256_arquivo(p) for p in (OUT_MEDICOS, OUT_ESTIMATIVAS, OUT_DESCRITIVO)},
    }
    OUT_RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=_json_default) + "\n",
                          encoding="utf-8")
    log("X1: " + "; ".join(f"{r}: {taxas[r]['total']['ligados']} de {taxas[r]['total']['registros']} ligados"
                           for r in REGRAS) + f"; {len(est)} linhas de estimativa")


def _json_default(o: Any) -> Any:
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o) if math.isfinite(o) else None
    if o is pd.NA:
        return None
    raise TypeError(type(o))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=("analise", "aquisicao", "tudo"), default="analise")
    ap.add_argument("--atualizar-doc", action="store_true")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    if args.etapa in ("aquisicao", "tudo"):
        listas, _ = ler_listas_pmme()
        if not COORD_JSON.exists():
            baixar_coordenadas()
        if "malha_periodo_verificado" not in json.loads(COORD_MANIFESTO.read_text(encoding="utf-8")):
            verificar_periodo_malha()
        if not CONSELHO_META.exists():
            adquirir_conselho()
        adquirir(COMPETENCIAS, crms_alvo(listas), args.workers)
    if args.etapa in ("analise", "tudo"):
        analisar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
