"""G1 (portão de viabilidade da onda 1, doc 51 §5): identificar os candidatos do PMM-E e ligá-los ao CNES pré.

Pergunta do portão
------------------
Dá para identificar TODOS os candidatos da 1ª chamada dos ciclos 1–3 (não só os
alocados ou ativos) e ligá-los ao seu local no CNES antes do programa? O portão
bloqueia o T1.1 (DAP por distância) e o T6.2 (RD do candidato na nota de corte).

Estatuto: **portão de viabilidade**. Só diagnóstico de cobertura e de ligação.
Nenhum contraste por IVS, por lado de corte, por faixa da bolsa, por alocação ou
por outcome é calculado. O IVS não é lido. A alocação entra só como estrato da
taxa de LIGAÇÃO (pedido do portão: a ligação não pode depender da alocação, ou o
T6.2 herda seleção). Toda saída leva ``natureza_dos_dados = EMPIRICO``.

Etapas
------
1. Inventário (somente leitura) dos arquivos brutos de classificação e
   resultado em ``data/raw/pmm_e`` e ``data/raw/aquisicao/vagas``: que
   identificadores cada arquivo traz por pessoa (nome, CPF mascarado e o
   molde da máscara, CRM, UF do CRM, número de inscrição, modalidade), por
   ciclo e chamada, e a cobertura contra ``escolhas_candidatos.parquet``.
2. Ligação ao CNES. Os arquivos de candidatos NÃO trazem CRM nem UF do CRM;
   trazem nome e CPF mascarado (dígitos visíveis em posições fixas por
   arquivo). A regra da X1 (CRM+UF; CRM + nome compatível; ambíguos fora) não
   se aplica literalmente. A regra G1 é a análoga, fixada antes de ligar:
     (1) chave do CPF igual e nome normalizado idêntico, com um único
         profissional (``CO_PROFISSIONAL_SUS``). O ``CO_CPF`` público também é
         mascarado (posições 4–9 visíveis): a chave é o SHA-256 dos dígitos nas
         posições visíveis nas DUAS máscaras (6 no ciclo 3; 2 nos ciclos 1 e 2);
     (2) sem (1), chave do CPF igual e nome compatível (definição da X1), com
         um único profissional;
     (3) ambíguos (mais de um profissional, ou um profissional ligado a mais
         de um candidato do mesmo ciclo) e não achados ficam fora, com o motivo.
   Sensibilidade (relatada lado a lado, coluna ``regra_ligacao``): só nome
   normalizado idêntico e único no conjunto de busca, sem CPF.
   Conjunto de busca do ciclo k: profissionais com vínculo médico (CBO 2251,
   2252, 2253, 2231, como no a09 e na X1) em alguma competência do cache da X1
   até a competência de referência do ciclo, e presentes no dicionário de
   profissionais (``tbDadosProfissionalSus``) da competência baixada. Só
   informação pré-programa define quem é procurado.
   Validação independente (rota X1): candidatos alocados da 1ª chamada dos
   ciclos 1 e 2 ligados pela X1 (célula + nome compatível → lista de ativos →
   CRM no CNES, regra D1) têm o mesmo ``CO_PROFISSIONAL_SUS`` pela regra G1?
3. Taxas de ligação por ciclo, por alocado × não alocado e ambiguidade.
4. Município de origem na competência de referência do ciclo e distância
   (círculo máximo entre centroides do IBGE já no repositório) a cada célula
   ranqueada pelo candidato. Só cobertura: nenhuma média de distância por grupo.

Competência de referência (fixada antes de ligar): a última competência do
cache da X1 estritamente anterior ao mês de abertura das inscrições da 1ª
chamada do ciclo (auditoria 01, tabela de prazos): ciclo 1, 28/07/2025 →
202506; ciclo 2, edital de 03/02/2026 → 202510; ciclo 3, julho de 2026 → 202602.

Download mínimo
---------------
O cache da X1 tem os vínculos médicos de 202406, 202501, 202506, 202510, 202602
e 202608, mas o nome só dos CRMs das listas do PMM-E e nenhum CPF. A ligação
dos candidatos precisa de ``tbDadosProfissionalSus`` (``CO_CPF``,
``NO_PROFISSIONAL``). O portão baixa UMA competência (``202602``, a de
referência do ciclo 3; a tabela se mostrou cumulativa e contém todos os médicos
das referências dos ciclos 1 e 2), pelo mesmo servlet HTTPS
do a09, confere o SHA-256 contra o manifesto do a09, extrai só o necessário
para ``output/rdd_bolsa/G1_cache/`` (ignorado pelo Git) e apaga o ZIP. Nada é
gravado em ``data/``. Nenhuma competência >= 202609 é baixada ou lida.

Dados pessoais
--------------
Nome e CPF mascarado ficam só em memória. O cache guarda o nome normalizado e
a chave do CPF em SHA-256 (nunca os dígitos), só dos profissionais com nome
idêntico ao de algum candidato ou com o mesmo primeiro nome e a mesma chave. As saídas em ``output/rdd_bolsa/G1_*``
não trazem nome, CPF, CNS, CRM nem código de profissional: o candidato é o
``id_candidato`` do script 12 (pseudônimo determinístico, reconstruído em
memória e conferido contra ``escolhas_candidatos.parquet``).

Uso
---
``python3 scripts/rdd_bolsa/G1_identificar_candidatos.py --etapa aquisicao``
baixa e extrai o dicionário; ``--etapa analise`` (padrão) liga e grava as
saídas sem rede; ``--atualizar-doc`` reescreve os blocos ``<!-- G1:... -->`` de
``docs/auditorias/G1_viabilidade_candidatos.md`` a partir das saídas.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import re
import sys
import warnings
import zipfile
from pathlib import Path
from typing import Any

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def _importar(nome: str, caminho: Path):
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


SCRIPT_12 = ROOT / "scripts" / "rdd_bolsa" / "12_construir_outcomes_funil.py"
SCRIPT_17 = ROOT / "scripts" / "rdd_bolsa" / "17_ponte_pmme_cnes.py"
SCRIPT_A09 = ROOT / "scripts" / "aquisicao" / "a09_adquirir_cnes_nacional.py"
X1 = _importar("x1_ponte_17_g1", SCRIPT_17)
S12 = _importar("outcomes_funil_12_g1", SCRIPT_12)

# ---------------------------------------------------------------- caminhos
RAW_PMME = ROOT / "data" / "raw" / "pmm_e"
RAW_VAGAS = ROOT / "data" / "raw" / "aquisicao" / "vagas"
ESCOLHAS = ROOT / "output" / "rdd_bolsa" / "outcomes" / "escolhas_candidatos.parquet"
CONJ_PRINCIPAL = ROOT / "output" / "rdd_bolsa" / "outcomes" / "escolhas_conjunto_principal.parquet"
MANIFESTO_A09 = ROOT / "output" / "aquisicao" / "a09_manifesto_cnes_nacional.json"
PLANO_51 = ROOT / "docs" / "06_execucao" / "51_plano_perguntas_reformuladas.md"
AUDITORIA_01 = ROOT / "docs" / "auditorias" / "01_regra_institucional.md"

CACHE_DIR = ROOT / "output" / "rdd_bolsa" / "G1_cache"  # ignorado pelo Git
OUT_DIR = ROOT / "output" / "rdd_bolsa"
OUT_CANDIDATOS = OUT_DIR / "G1_candidatos_origem.parquet"
OUT_DISTANCIAS = OUT_DIR / "G1_distancias_opcoes.parquet"
OUT_INVENTARIO = OUT_DIR / "G1_inventario_identificadores.csv"
OUT_RESUMO = OUT_DIR / "G1_resumo.json"
DOC = ROOT / "docs" / "auditorias" / "G1_viabilidade_candidatos.md"

# ---------------------------------------------------------------- parâmetros (fixados antes de ligar)
NATUREZA = "EMPIRICO"
ESTATUTO = "PORTAO_VIABILIDADE_G1"
LIMITE_EXCLUSIVO = "202609"
COMPETENCIA_DICIONARIO = "202602"
assert COMPETENCIA_DICIONARIO < LIMITE_EXCLUSIVO
COMPETENCIAS_X1 = tuple(X1.COMPETENCIAS)
assert all(c < LIMITE_EXCLUSIVO for c in COMPETENCIAS_X1)
# Mês de abertura das inscrições da 1ª chamada (auditoria 01, tabela de prazos dos editais).
ABERTURA_INSCRICOES = {1: "202507", 2: "202602", 3: "202607"}
FONTES_CICLO = {1: "c1_ch1", 2: "c2_ch1", 3: "c3_ch1"}  # arquivos de escolhas do script 12
CICLOS = (1, 2, 3)
REGRAS = ("g1_cpf_nome", "g1_so_nome")  # principal e sensibilidade
MIN_DIGITOS_VISIVEIS = 6
# Critérios do veredito (fixados antes de ver as taxas).
TAXA_VIAVEL = 0.80
TAXA_PARCIAL = 0.50
AMBIGUO_MAX = 0.02
CONCORDANCIA_MIN = 0.98
CONCORDANCIA_INVIAVEL = 0.90  # abaixo disso a ligação não é confiável: INVIAVEL
COBERTURA_DICIONARIO_MIN = 0.99
DIFERENCA_ALOCACAO_MAX = 0.10
VERSAO_CACHE = 2


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


sha256_arquivo = X1.sha256_arquivo
texto_norm = X1.texto_norm
nomes_compativeis = X1.nomes_compativeis


def _tuplas(df: pd.DataFrame):
    """itertuples sem o '_' inicial das colunas (o pandas renomeia campos que começam com '_')."""
    return df.rename(columns=lambda c: c.lstrip("_")).itertuples(index=False)


def rel(caminho: Path) -> str:
    return Path(caminho).resolve().relative_to(ROOT).as_posix()


def checar_limite(comp: str) -> None:
    if comp >= LIMITE_EXCLUSIVO:
        raise RuntimeError(f"competência {comp} >= {LIMITE_EXCLUSIVO} é vedada (ciclo 3)")


def competencia_referencia(ciclo: int) -> str:
    """Última competência do cache da X1 estritamente anterior à abertura das inscrições do ciclo."""
    anteriores = [c for c in COMPETENCIAS_X1 if c < ABERTURA_INSCRICOES[ciclo]]
    if not anteriores:
        raise AssertionError(f"ciclo {ciclo}: nenhuma competência do cache antes de {ABERTURA_INSCRICOES[ciclo]}")
    return anteriores[-1]


REFERENCIA = {k: competencia_referencia(k) for k in CICLOS}


# ---------------------------------------------------------------- CPF mascarado

def mascara_cpf(valor: object, minimo: int = MIN_DIGITOS_VISIVEIS) -> tuple[str, str] | None:
    """(padrão das posições visíveis, dígitos visíveis) de um CPF mascarado; None se inválido.

    Aceita 11 posições depois de tirar '.', '-' e espaços; cada posição é dígito (visível) ou 'X'/'*' (oculta).
    Exige ao menos ``minimo`` dígitos visíveis (nos candidatos, ``MIN_DIGITOS_VISIVEIS``). Um CPF completo é a
    máscara com as 11 posições visíveis.
    """
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return None
    s = re.sub(r"[.\-\s]", "", str(valor).strip())
    if len(s) != 11:
        return None
    pos, dig = [], []
    for i, ch in enumerate(s):
        if ch.isdigit():
            pos.append(str(i))
            dig.append(ch)
        elif ch not in "Xx*":
            return None
    if len(pos) < minimo:
        return None
    return "-".join(pos), "".join(dig)


def primeiro_nome(nome: object) -> str:
    t = X1.tokens_nome(nome)
    return t[0] if t else ""


def posicoes_comuns(p: str, q: str) -> str:
    """Posições visíveis nas duas máscaras, em ordem ('' se nenhuma)."""
    comum = set(p.split("-")) & set(q.split("-"))
    return "-".join(sorted(comum, key=int))


def chave_cpf(padrao: str, digitos: str, posicoes: str | None = None) -> str | None:
    """SHA-256 das posições `posicoes` (padrão: todas as visíveis) e dos dígitos nelas; None sem posição."""
    posicoes = padrao if posicoes is None else posicoes
    if not posicoes:
        return None
    mapa = dict(zip(padrao.split("-"), digitos))
    if any(i not in mapa for i in posicoes.split("-")):
        return None
    return hashlib.sha256(f"{posicoes}|{''.join(mapa[i] for i in posicoes.split('-'))}".encode()).hexdigest()


def digitos_no_padrao(cpf11: str, padrao: str) -> str:
    return "".join(cpf11[int(i)] for i in padrao.split("-"))


def chaves_candidatos(cands: pd.DataFrame, padrao_cnes: str) -> pd.DataFrame:
    """`_chave`: SHA-256 dos dígitos do candidato nas posições visíveis no candidato E no CO_CPF do CNES."""
    out = cands.copy()
    m = out["_cpf"].map(mascara_cpf)
    out["_posicoes_comuns"] = [posicoes_comuns(x[0], padrao_cnes) if x else None for x in m]
    out["_chave"] = [chave_cpf(x[0], x[1], pc) if x else None for x, pc in zip(m, out["_posicoes_comuns"])]
    return out


def moldes_consistentes(p1: str, d1: str, p2: str, d2: str) -> bool | None:
    """Dígitos visíveis iguais nas posições visíveis nas duas máscaras; None sem posição comum."""
    a = dict(zip(p1.split("-"), d1))
    b = dict(zip(p2.split("-"), d2))
    comum = set(a) & set(b)
    if not comum:
        return None
    return all(a[i] == b[i] for i in comum)


# ---------------------------------------------------------------- candidatos (só em memória)

def ler_candidatos() -> tuple[pd.DataFrame, dict]:
    """Uma linha por candidato da 1ª chamada (ciclos 1–3), com nome e máscara do CPF só em memória.

    Reconstrói o ``id_candidato`` do script 12 (ordem do SHA-256 de nome normalizado + CPF mascarado) e
    confere que a reconstrução reproduz as linhas de ``escolhas_candidatos.parquet`` (fail closed).
    """
    escolhas = pd.read_parquet(ESCOLHAS)
    partes, diag = [], {}
    for k, fonte in FONTES_CICLO.items():
        espec = S12.ESPEC_CANDIDATURAS[fonte]
        cand = S12.ler_candidaturas(espec)
        pid = {h: f"c{k}_{i + 1:05d}" for i, h in enumerate(sorted(cand["_pessoa"].unique()))}
        cab, _, linhas = S12.ler_aba(espec["caminho"], espec["aba"])
        i_cnes, i_curso = S12.coluna(cab, "CNES"), S12.coluna(cab, "CURSO")
        i_nome = S12.coluna(cab, "NOME CANDIDATO A", "NOME")
        i_cpf = S12.coluna(cab, "CPF", "CPF MASC", prefixo=True)
        i_ordem = S12.coluna(cab, "ORDEM DE PRIORIDADE ESCOLHIDA")
        reg = []
        for r in linhas:
            cnes, curso = S12.chave_cnes(S12.valor(r, i_cnes)), S12.chave_curso(S12.valor(r, i_curso))
            if cnes is None or curso is None:
                continue
            nome = S12.texto_norm(S12.valor(r, i_nome))
            cpf = str(S12.valor(r, i_cpf) or "").strip()
            pessoa = hashlib.sha256((nome + "|" + cpf).encode("utf-8")).hexdigest()
            reg.append({"id_candidato": pid[pessoa], "co_cnes_7d": cnes, "cod_curso": curso,
                        "opcao_rank": S12.opcao(S12.valor(r, i_ordem)), "_nome": nome, "_cpf": cpf})
        rec = pd.DataFrame(reg)
        esc_k = escolhas[escolhas["ciclo"] == k]
        chave = ["id_candidato", "co_cnes_7d", "cod_curso", "opcao_rank"]
        a = sorted(rec[chave].astype(str).apply("|".join, axis=1))
        b = sorted(esc_k[chave].astype(str).apply("|".join, axis=1))
        if a != b:
            raise AssertionError(f"ciclo {k}: reconstrução do id_candidato não reproduz escolhas_candidatos")
        pessoas = rec.drop_duplicates("id_candidato")[["id_candidato", "_nome", "_cpf"]].copy()
        if pessoas["id_candidato"].nunique() != esc_k["id_candidato"].nunique():
            raise AssertionError(f"ciclo {k}: número de candidatos difere de escolhas_candidatos")
        pessoas.insert(0, "ciclo", k)
        aloc = esc_k.groupby("id_candidato")["alocado"].max()
        pessoas["alocado_1a_chamada"] = pessoas["id_candidato"].map(aloc).astype(int)
        m = pessoas["_cpf"].map(mascara_cpf)
        pessoas["_padrao"] = m.map(lambda x: x[0] if x else None)
        pessoas["_chave"] = [chave_cpf(x[0], x[1]) if x else None for x in m]
        partes.append(pessoas)
        diag[f"ciclo_{k}"] = {"arquivo": rel(espec["caminho"]), "aba": espec["aba"],
                              "reconstrucao_id_candidato": "reproduz escolhas_candidatos.parquet",
                              "candidatos": int(len(pessoas)),
                              "alocados_1a_chamada": int(pessoas["alocado_1a_chamada"].sum()),
                              "mascara_cpf_invalida": int(pessoas["_padrao"].isna().sum()),
                              "padroes_de_mascara": {p: int(n) for p, n in
                                                     pessoas["_padrao"].value_counts().sort_index().items()}}
    out = pd.concat(partes, ignore_index=True).sort_values(["ciclo", "id_candidato"]).reset_index(drop=True)
    return out, diag


def assinatura_alvo(cands: pd.DataFrame) -> str:
    itens = sorted(set(cands["_nome"]) | set(cands["_chave"].dropna()))
    return hashlib.sha256("|".join(itens).encode()).hexdigest()


# ---------------------------------------------------------------- inventário dos brutos (somente leitura)

# (arquivo, ciclo, chamada, papel). Os quadros de vagas e a adesão de gestores não têm pessoas (conferido).
INVENTARIO = [
    (RAW_VAGAS / "2025_ciclo1_chamada1_alocacao_retificada.xlsx", 1, 1, "resultado da alocação (retificado)"),
    (RAW_VAGAS / "2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx", 1, 1,
     "resultado da alocação (retificado, sub judice); base de escolhas_candidatos"),
    (RAW_VAGAS / "2025_ciclo1_chamada1_realocacao_retificado.xlsx", 1, 1, "realocação (quadro 2)"),
    (RAW_PMME / "2025_ciclo1_chamada1_homologados.xlsx", 1, 1, "homologados"),
    (RAW_PMME / "2025_ciclo1_chamada2_classificacao_final.xlsx", 1, 2, "classificação final"),
    (RAW_PMME / "2025_ciclo1_chamada2_vagas_e_alocados.xlsx", 1, 2, "alocados em vagas imediatas"),
    (RAW_PMME / "2025_ciclo1_chamada2_homologados.xlsx", 1, 2, "homologados"),
    (RAW_PMME / "resultado-preliminar-pmme.xlsx", 2, 1, "resultado preliminar"),
    (RAW_PMME / "resultado-final-pmme-2o-ciclo-25-05.xlsx", 2, 1, "resultado final; base de escolhas_candidatos"),
    (RAW_PMME / "resultado-final-vagas-remanescentes.xlsx", 2, 1, "vagas remanescentes"),
    (RAW_PMME / "2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx", 2, 1, "remanescentes (05/05)"),
    (RAW_PMME / "2026_ciclo2_chamada2_resultado_final.xlsx", 2, 2, "resultado final"),
    (RAW_PMME / "2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx", 3, 1,
     "resultado final (sub judice); base de escolhas_candidatos"),
]
SEM_PESSOAS = [
    RAW_VAGAS / "2025_ciclo1_chamada1_vagas.xlsx", RAW_VAGAS / "2026_ciclo2_chamada1_vagas_e_servicos_original.xlsx",
    RAW_VAGAS / "2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx",
    RAW_VAGAS / "2026_ciclo3_chamada1_vagas_original.xlsx", RAW_VAGAS / "2026_ciclo3_gestores_quadro_vagas_original.xlsx",
    RAW_PMME / "2026_ciclo2_chamada1_vagas_retificadas.xlsx", RAW_PMME / "2026_ciclo2_chamada2_vagas.xlsx",
    RAW_PMME / "2026_ciclo3_adesao_gestores_resultado_final.xlsx",
    RAW_PMME / "2026_ciclo3_chamada1_vagas_retificadas.xlsx", RAW_PMME / "comunicado-oficial-alocados-24-03-2026.pdf",
]


def _abas_com_pessoas(caminho: Path) -> list[tuple[str, list[str], list[tuple]]]:
    """Abas com coluna de CPF: (nome da aba, cabeçalho normalizado, linhas de dados)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
    out = []
    try:
        for ws in wb.worksheets:
            linhas = [tuple(r) for r in ws.iter_rows(values_only=True)]
            for i, linha in enumerate(linhas[:20]):
                cab = [texto_norm(c) for c in linha]
                if any(c.startswith("CPF") for c in cab):
                    dados = [r for r in linhas[i + 1:] if any(v is not None and str(v).strip() for v in r)]
                    out.append((ws.title, cab, dados))
                    break
    finally:
        wb.close()
    return out


def molde(valor: object) -> str:
    """Forma do valor sem conteúdo: dígito → 'd', outra letra que não X → 'a' (máscara X e '*' ficam)."""
    return re.sub(r"[A-WYZa-wyzÀ-ÿ]", "a", re.sub(r"\d", "d", str(valor).strip()))


def inventario(cands: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Identificadores por arquivo e aba, e cobertura contra os candidatos de escolhas_candidatos do mesmo ciclo."""
    por_ciclo_nome = {k: g.groupby("_nome") for k, g in cands.groupby("ciclo")}
    linhas = []
    for caminho, ciclo, chamada, papel in INVENTARIO:
        for aba, cab, dados in _abas_com_pessoas(caminho):
            i_cpf = next(i for i, c in enumerate(cab) if c.startswith("CPF"))
            i_nome = next((i for i, c in enumerate(cab) if c.startswith("NOME") and "FANTASIA" not in c), None)
            pessoas = set()
            moldes: dict[str, int] = {}
            for r in dados:
                v = r[i_cpf] if i_cpf < len(r) else None
                if v is None or not str(v).strip():
                    continue
                moldes[molde(v)] = moldes.get(molde(v), 0) + 1
                nome = texto_norm(r[i_nome]) if i_nome is not None and i_nome < len(r) else ""
                pessoas.add((nome, str(v).strip()))
            casadas, presentes = 0, set()
            grupos = por_ciclo_nome.get(ciclo)
            for nome, cpf in pessoas:
                if grupos is None or nome not in grupos.groups:
                    continue
                m = mascara_cpf(cpf)
                ok = []
                for r in _tuplas(grupos.get_group(nome)):
                    if m is None or pd.isna(r.padrao):
                        cons = None
                    else:
                        mc = mascara_cpf(r.cpf)
                        cons = moldes_consistentes(m[0], m[1], mc[0], mc[1])
                    if cons is not False:  # nome idêntico e dígitos visíveis comuns iguais (ou sem posição comum)
                        ok.append(r.id_candidato)
                if len(ok) == 1:
                    casadas += 1
                    presentes.add(ok[0])
            n_cand = int((cands["ciclo"] == ciclo).sum())
            linhas.append({
                "natureza_dos_dados": NATUREZA, "arquivo": rel(caminho), "aba": aba, "ciclo": ciclo,
                "chamada": chamada,
                "papel": (papel.split(";")[0] + "; aba de desclassificados") if "DESCLASS" in texto_norm(aba) else papel,
                "linhas": len(dados), "pessoas_nome_cpf": len(pessoas),
                "tem_nome": int(i_nome is not None), "tem_cpf_mascarado": 1,
                "moldes_cpf": "; ".join(f"{k} ({v})" for k, v in sorted(moldes.items(), key=lambda kv: -kv[1])),
                "tem_crm": int(any(("CRM" in c.split() or "REGISTRO" in c or "CONSELHO" in c) for c in cab)),
                "tem_uf_do_crm": int(any("UF" in c.split() and "CRM" in c.split() for c in cab)),
                "tem_numero_inscricao": int(any("INSCRICAO" in c and not c.startswith("TIPO") for c in cab)),
                "tem_modalidade_inscricao": int(any(c.startswith("TIPO DE INSCRICAO") or c.startswith("TIPO DE VAGA")
                                                    for c in cab)),
                "tem_uf_do_posto": int("UF" in cab),
                "pessoas_casadas_a_escolhas": casadas,
                "candidatos_de_escolhas_presentes": len(presentes),
                "candidatos_de_escolhas_no_ciclo": n_cand,
                "regra_casamento": "nome normalizado idêntico e dígitos visíveis comuns do CPF iguais; único",
            })
    inv = pd.DataFrame(linhas)
    sem = []
    for p in SEM_PESSOAS:
        if p.suffix == ".pdf":
            from pypdf import PdfReader
            leitor = PdfReader(str(p))
            texto = texto_norm(" ".join(pg.extract_text() or "" for pg in leitor.pages))
            sem.append({"arquivo": rel(p), "conteudo": "comunicado, sem lista de pessoas", "paginas": len(leitor.pages),
                        "abas_com_cpf": int(bool(re.search(r"\b(CPF|CRM)\b", texto)))})
        else:
            sem.append({"arquivo": rel(p), "conteudo": "quadro de vagas ou adesão de gestores; nenhuma aba com CPF",
                        "abas_com_cpf": len(_abas_com_pessoas(p))})
    if any(s.get("abas_com_cpf", 0) for s in sem):
        raise AssertionError("arquivo listado como sem pessoas tem aba com CPF")
    return inv, {"arquivos_sem_pessoas": sem}


# ---------------------------------------------------------------- aquisição do dicionário

def caminho_zip(comp: str) -> Path:
    return CACHE_DIR / f"BASE_DE_DADOS_CNES_{comp}.ZIP"


def caminho_dicionario(comp: str) -> Path:
    return CACHE_DIR / f"dicionario_alvo_{comp}.parquet"


def caminho_meta(comp: str) -> Path:
    return CACHE_DIR / f"meta_dicionario_{comp}.json"


def profissionais_medicos_x1() -> dict[str, set[str]]:
    """CO_PROFISSIONAL_SUS com vínculo médico em cada competência do cache da X1."""
    out = {}
    for c in COMPETENCIAS_X1:
        checar_limite(c)
        p = X1.caminho_cache(c)
        if not p.exists():
            raise SystemExit(f"cache da X1 ausente para {c} ({rel(p)}); rode o script 17 --etapa aquisicao")
        out[c] = set(pd.read_parquet(p, columns=["co_profissional_sus"])["co_profissional_sus"].dropna())
    return out


def adquirir(comp: str = COMPETENCIA_DICIONARIO, manter_zip: bool = False) -> None:
    """Baixa o ZIP (servlet HTTPS do a09) para o cache do G1, confere o SHA-256 do a09, extrai o dicionário, apaga o ZIP."""
    checar_limite(comp)
    a09 = _importar("a09_g1", SCRIPT_A09)
    cands, _ = ler_candidatos()
    ref = json.loads(MANIFESTO_A09.read_text(encoding="utf-8"))["por_competencia"][comp]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    destino = caminho_zip(comp)
    if destino.exists():
        a09.testar_zip(destino)
        sha, total, data_dl = sha256_arquivo(destino), destino.stat().st_size, "reaproveitado"
    else:
        sha, total = a09._baixar_uma_vez(comp, destino, 600)
        a09.testar_zip(destino)
        data_dl = dt.date.today().isoformat()
    if sha != ref["sha256_zip"]:
        raise AssertionError(f"{comp}: SHA-256 do ZIP difere do manifesto do a09 (fail closed)")
    medicos = profissionais_medicos_x1()
    uniao = set().union(*medicos.values())
    padroes = sorted(set(cands["_padrao"].dropna()))
    meta: dict[str, Any] = {"competencia": comp, "versao_cache": VERSAO_CACHE, "url": a09.URL_BASE + destino.name,
                            "data_download": data_dl, "sha256_zip": sha, "bytes_zip": int(total),
                            "sha256_igual_ao_a09": True, "padroes_cpf_candidatos": padroes}
    colunas = {"CO_PROFISSIONAL_SUS", "CO_CPF", "NO_PROFISSIONAL"}
    with zipfile.ZipFile(destino) as zf:
        m_prof = a09._membro(zf, "tbDadosProfissionalSus")
        m_carga = a09._membro(zf, "tbCargaHorariaSus")
        meta["membros_lidos"] = {"profissional": m_prof, "carga": m_carga}
        cab = a09._cabecalho(zf, m_prof)
        meta["colunas_tbDadosProfissionalSus"] = cab
        faltam = colunas - set(cab)
        if faltam:
            raise RuntimeError(f"{comp}: colunas ausentes em tbDadosProfissionalSus: {sorted(faltam)}")
        # 1ª passada: molde do CO_CPF (dígitos trocados por 'd'; nenhum dígito é guardado).
        moldes: dict[str, int] = {}
        padroes_cnes: dict[str, int] = {}
        linhas = 0
        dist_prof: set[str] = set()
        for bloco in X1._ler_tabela(zf, m_prof, {"CO_PROFISSIONAL_SUS", "CO_CPF"}, chunksize=1_000_000):
            bloco.columns = [c.strip().strip('"').upper() for c in bloco.columns]
            linhas += len(bloco)
            dist_prof.update(bloco["CO_PROFISSIONAL_SUS"].str.strip())
            bruto = bloco["CO_CPF"].fillna("").str.strip()
            for k, n in bruto.str.replace(r"\d", "d", regex=True).value_counts().items():
                moldes[k] = moldes.get(k, 0) + int(n)
            for k, n in bruto.map(lambda v: (mascara_cpf(v, 1) or ("invalido",))[0]).value_counts().items():
                padroes_cnes[k] = padroes_cnes.get(k, 0) + int(n)
        padrao_cnes = max((p for p in padroes_cnes if p != "invalido"), key=lambda p: padroes_cnes[p], default="")
        meta.update({"linhas_tbDadosProfissionalSus": int(linhas), "profissionais_distintos_no_dicionario": len(dist_prof),
                     "moldes_co_cpf": dict(sorted(moldes.items(), key=lambda kv: -kv[1])[:10]),
                     "padroes_co_cpf": dict(sorted(padroes_cnes.items(), key=lambda kv: -kv[1])[:10]),
                     "padrao_co_cpf_dominante": padrao_cnes,
                     "linhas_com_o_padrao_dominante": int(padroes_cnes.get(padrao_cnes, 0)),
                     "posicoes_comuns_por_padrao_candidato": {p: posicoes_comuns(p, padrao_cnes) if padrao_cnes else ""
                                                              for p in padroes}})
        cands = chaves_candidatos(cands, padrao_cnes)
        meta["assinatura_alvo"] = assinatura_alvo(cands)
        nomes_alvo = set(cands["_nome"])
        # Nome compatível exige o mesmo primeiro nome: guarda-se só quem tem (primeiro nome, chave) de algum candidato.
        pares_alvo = {(primeiro_nome(n), c) for n, c in zip(cands["_nome"], cands["_chave"]) if isinstance(c, str)}
        # 2ª passada: médicos do cache da X1 com nome idêntico ao de algum candidato, ou com o mesmo primeiro nome e a
        # mesma chave do CPF.
        guardar = []
        for bloco in X1._ler_tabela(zf, m_prof, colunas, chunksize=1_000_000):
            bloco.columns = [c.strip().strip('"').upper() for c in bloco.columns]
            cod = bloco["CO_PROFISSIONAL_SUS"].str.strip()
            sel = cod.isin(uniao)
            mc = bloco.loc[sel, "CO_CPF"].map(lambda v: mascara_cpf(v, 1))
            b = pd.DataFrame({"co_profissional_sus": cod[sel],
                              "nome_norm": bloco.loc[sel, "NO_PROFISSIONAL"].map(texto_norm)})
            for p in padroes:
                b[f"chave_{p}"] = [chave_cpf(x[0], x[1], posicoes_comuns(p, x[0])) if x else None for x in mc]
            alvo = b["nome_norm"].isin(nomes_alvo)
            primeiro = b["nome_norm"].map(primeiro_nome)
            for p in padroes:
                alvo |= pd.Series([(a, c) in pares_alvo for a, c in zip(primeiro, b[f"chave_{p}"])], index=b.index)
            guardar.append(b.loc[alvo])
        prof_carga: set[str] = set()
        for bloco in X1._ler_tabela(zf, m_carga, {"CO_PROFISSIONAL_SUS"}, chunksize=2_000_000):
            bloco.columns = [c.strip().strip('"').upper() for c in bloco.columns]
            prof_carga.update(bloco["CO_PROFISSIONAL_SUS"].str.strip())
        meta["profissionais_distintos_na_carga_horaria_todas_cbo"] = len(prof_carga)
        meta["profissionais_do_dicionario_sem_vinculo_na_competencia"] = len(dist_prof - prof_carga)
    meta["cobertura_do_dicionario_sobre_medicos_x1"] = {
        c: {"medicos": len(s), "no_dicionario": len(s & dist_prof), "fracao": len(s & dist_prof) / len(s)}
        for c, s in medicos.items()}
    dic = pd.concat(guardar, ignore_index=True).drop_duplicates().sort_values("co_profissional_sus", kind="mergesort")
    meta["linhas_guardadas_no_cache"] = int(len(dic))
    meta["profissionais_com_mais_de_uma_linha"] = int(dic["co_profissional_sus"].duplicated().sum())
    tmp = caminho_dicionario(comp).with_suffix(".tmp")
    dic.reset_index(drop=True).to_parquet(tmp, index=False)
    tmp.replace(caminho_dicionario(comp))
    meta["data_processamento"] = dt.date.today().isoformat()
    meta["status"] = "extraido_zip_mantido" if manter_zip else "extraido_zip_apagado"
    caminho_meta(comp).write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not manter_zip:
        destino.unlink()
    log(f"{comp}: dicionário extraído ({len(dic):,} linhas guardadas); status {meta['status']}")


# ---------------------------------------------------------------- ligação

def ligar(cands: pd.DataFrame, dic: pd.DataFrame, pool: dict[int, set[str]], *, usar_cpf: bool) -> pd.DataFrame:
    """Regra G1 (usar_cpf=True) ou sensibilidade só por nome (usar_cpf=False). Uma linha por candidato.

    `cands`: ciclo, id_candidato, _nome, _padrao, _chave. `dic`: co_profissional_sus, nome_norm, chave_<padrão>.
    `pool[k]`: profissionais procuráveis no ciclo k. Devolve co_profissional_sus (ou <NA>), etapa e motivo.
    """
    nomes_prof = dic.groupby("co_profissional_sus")["nome_norm"].agg(lambda s: sorted(set(s)))
    por_nome = dic.groupby("nome_norm")["co_profissional_sus"].agg(lambda s: sorted(set(s)))
    por_chave = {}
    for col in [c for c in dic.columns if c.startswith("chave_")]:
        por_chave[col.removeprefix("chave_")] = dic.dropna(subset=[col]).groupby(col)["co_profissional_sus"].agg(
            lambda s: sorted(set(s)))
    linhas = []
    for r in _tuplas(cands):
        base = {"ciclo": r.ciclo, "id_candidato": r.id_candidato, "co_profissional_sus": pd.NA,
                "etapa_ligacao": pd.NA, "motivo": ""}
        p = pool[r.ciclo]
        if not usar_cpf:
            c = [x for x in por_nome.get(r.nome, []) if x in p]
            if len(c) == 1:
                linhas.append({**base, "co_profissional_sus": c[0], "etapa_ligacao": "s_nome_identico_unico",
                               "motivo": "ligado"})
            elif len(c) > 1:
                linhas.append({**base, "motivo": "ambiguo_homonimos_no_conjunto_de_busca"})
            else:
                linhas.append({**base, "motivo": "sem_nome_identico_no_conjunto_de_busca"})
            continue
        if pd.isna(r.padrao):
            linhas.append({**base, "motivo": "mascara_cpf_invalida"})
            continue
        if r.padrao not in por_chave:
            raise AssertionError(f"padrão de máscara {r.padrao} ausente do dicionário; refaça a aquisição")
        c = [x for x in por_chave[r.padrao].get(r.chave, []) if x in p]
        if not c:
            linhas.append({**base, "motivo": "sem_profissional_com_cpf_compativel_no_conjunto_de_busca"})
            continue
        exato = [x for x in c if r.nome in nomes_prof.get(x, [])]
        if len(exato) == 1:
            linhas.append({**base, "co_profissional_sus": exato[0], "etapa_ligacao": "1_cpf_nome_identico",
                           "motivo": "ligado"})
            continue
        if len(exato) > 1:
            linhas.append({**base, "motivo": "ambiguo_cpf_nome_identico_com_mais_de_um_profissional"})
            continue
        compat = [x for x in c if any(nomes_compativeis(r.nome, n) for n in nomes_prof.get(x, []))]
        if len(compat) == 1:
            linhas.append({**base, "co_profissional_sus": compat[0], "etapa_ligacao": "2_cpf_nome_compativel",
                           "motivo": "ligado"})
        elif len(compat) > 1:
            linhas.append({**base, "motivo": "ambiguo_cpf_nome_compativel_com_mais_de_um_profissional"})
        else:
            linhas.append({**base, "motivo": "cpf_compativel_sem_nome_compativel"})
    out = pd.DataFrame(linhas)
    # Um profissional ligado a mais de um candidato do mesmo ciclo: ambíguo, todos fora.
    lig = out["co_profissional_sus"].notna()
    dup = lig & out.duplicated(["ciclo", "co_profissional_sus"], keep=False) & lig
    out.loc[dup, ["co_profissional_sus", "etapa_ligacao"]] = pd.NA
    out.loc[dup, "motivo"] = "ambiguo_profissional_ligado_a_mais_de_um_candidato_do_ciclo"
    out["ligado"] = out["co_profissional_sus"].notna().astype(int)
    return out


def rota_x1(vinc: pd.DataFrame, nomes_x1: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Rota X1 (validação): candidato alocado ↔ ativo (célula + nome) ↔ CNES pelo CRM (regra D1 do script 17)."""
    listas, _ = X1.ler_listas_pmme()
    conselho, _ = X1.codigo_conselho_crm(vinc)
    lig, _ = X1.ligar(listas, vinc, nomes_x1, conselho_crm=conselho, exigir_nome_etapa1=True)
    med = listas.merge(lig, on="id_medico", validate="one_to_one")
    med["ligado"] = med["co_profissional_sus"].notna().astype(int)
    pares, diag = X1.ligar_candidatos(med, listas)
    pares = pares.merge(med[["id_medico", "co_profissional_sus"]], on="id_medico", how="left")
    pares = pares.rename(columns={"co_profissional_sus": "co_profissional_sus_x1"})
    return pares[["ciclo", "id_candidato", "co_profissional_sus_x1"]], diag


def validacao_entre_ciclos(cands: pd.DataFrame, lig: pd.DataFrame) -> dict:
    """Mesma pessoa em dois ciclos (nome idêntico e dígitos visíveis comuns do CPF iguais, par único): o
    profissional ligado é o mesmo? Cobre não alocados. No ciclo 3 a chave tem 6 dígitos; nos ciclos 1 e 2, 2."""
    c = cands[["ciclo", "id_candidato", "_nome", "_cpf", "alocado_1a_chamada"]].merge(
        lig[["ciclo", "id_candidato", "co_profissional_sus"]], on=["ciclo", "id_candidato"])
    out = {}
    for a, b in ((1, 2), (1, 3), (2, 3)):
        x, y = c[c["ciclo"] == a], c[c["ciclo"] == b]
        pares = x.merge(y, on="_nome", suffixes=("_a", "_b"))
        ok = []
        for r in _tuplas(pares):
            ma, mb = mascara_cpf(r.cpf_a), mascara_cpf(r.cpf_b)
            if ma and mb and moldes_consistentes(ma[0], ma[1], mb[0], mb[1]):
                ok.append(r)
        pr = pd.DataFrame([r._asdict() for r in ok]) if ok else pd.DataFrame(
            columns=["id_candidato_a", "id_candidato_b", "co_profissional_sus_a", "co_profissional_sus_b",
                     "alocado_1a_chamada_a"])
        if len(pr):
            pr = pr[~pr["id_candidato_a"].duplicated(keep=False) & ~pr["id_candidato_b"].duplicated(keep=False)]
        ambos = pr[pr["co_profissional_sus_a"].notna() & pr["co_profissional_sus_b"].notna()]
        iguais = ambos["co_profissional_sus_a"] == ambos["co_profissional_sus_b"]
        na = ambos["alocado_1a_chamada_a"] == 0
        out[f"ciclos_{a}_e_{b}"] = {
            "pares_mesma_pessoa": int(len(pr)), "ligados_nos_dois": int(len(ambos)),
            "mesmo_profissional": int(iguais.sum()),
            "concordancia": float(iguais.mean()) if len(ambos) else None,
            "nao_alocados_no_ciclo_anterior_ligados_nos_dois": int(na.sum()),
            "concordancia_nao_alocados_no_ciclo_anterior": float(iguais[na].mean()) if na.any() else None}
    return out


# ---------------------------------------------------------------- origem e distância

def origem(lig: pd.DataFrame, vinc: pd.DataFrame) -> pd.DataFrame:
    """Município de origem na competência de referência do ciclo, para os ligados."""
    linhas = []
    for k in CICLOS:
        ref = REFERENCIA[k]
        d = lig[(lig["ciclo"] == k)]
        v = vinc[(vinc["competencia"] == ref) & vinc["co_profissional_sus"].isin(set(d["co_profissional_sus"].dropna()))]
        por_prof = {p: g for p, g in v.groupby("co_profissional_sus")}
        for r in d.itertuples(index=False):
            o: dict[str, Any] = {"ciclo": k, "id_candidato": r.id_candidato, "competencia_referencia": ref}
            if not r.ligado:
                o["motivo_origem_ausente"] = "candidato não ligado"
                linhas.append(o)
                continue
            g = por_prof.get(r.co_profissional_sus)
            if g is None or g.empty:
                o.update({"vinculo_medico_na_referencia": 0, "n_vinculos_referencia": 0, "n_municipios_origem": 0,
                          "motivo_origem_ausente": "sem vínculo médico na competência de referência"})
                linhas.append(o)
                continue
            cont = g["co_municipio"].value_counts()
            topo = sorted(cont[cont == cont.max()].index)
            o.update({"vinculo_medico_na_referencia": 1, "n_vinculos_referencia": int(len(g)),
                      "n_municipios_origem": int(g["co_municipio"].nunique()),
                      "co_ibge_origem": topo[0], "origem_principal_empatada": int(len(topo) > 1),
                      "_munis": tuple(sorted(set(g["co_municipio"])))})
            linhas.append(o)
    return pd.DataFrame(linhas)


def distancias(cand: pd.DataFrame, escolhas: pd.DataFrame, coord: pd.DataFrame) -> pd.DataFrame:
    """Distância (km) de cada célula ranqueada ao município de origem principal e ao mais próximo."""
    xy = coord.set_index("co_ibge")
    base = cand[["ciclo", "id_candidato", "co_ibge_origem", "_munis"]]
    e = escolhas[["ciclo", "id_candidato", "opcao_rank", "co_cnes_7d", "cod_curso", "co_ibge"]].merge(
        base, on=["ciclo", "id_candidato"], how="left", validate="many_to_one")
    linhas = []
    for r in _tuplas(e):
        o = {"ciclo": r.ciclo, "id_candidato": r.id_candidato, "opcao_rank": r.opcao_rank,
             "co_cnes_7d": r.co_cnes_7d, "cod_curso": r.cod_curso, "co_ibge_opcao": r.co_ibge,
             "dist_km_origem_principal": np.nan, "dist_km_origem_mais_proxima": np.nan, "motivo_distancia_ausente": ""}
        if not isinstance(r.munis, tuple):
            o["motivo_distancia_ausente"] = "sem município de origem (não ligado ou sem vínculo na referência)"
        elif pd.isna(r.co_ibge):
            o["motivo_distancia_ausente"] = "célula fora do quadro da 1ª chamada (sem município)"
        elif r.co_ibge not in xy.index or any(m not in xy.index for m in r.munis):
            o["motivo_distancia_ausente"] = "município sem centroide na API do IBGE"
        else:
            d = X1.haversine_km(xy.loc[list(r.munis), "lon"], xy.loc[list(r.munis), "lat"],
                                xy.at[r.co_ibge, "lon"], xy.at[r.co_ibge, "lat"])
            o["dist_km_origem_mais_proxima"] = float(np.min(d))
            o["dist_km_origem_principal"] = float(d[list(r.munis).index(r.co_ibge_origem)])
        linhas.append(o)
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------- taxas e veredito

def taxas(df: pd.DataFrame) -> dict:
    """Taxa de ligação por ciclo, por alocado × não alocado e motivos (df: uma regra)."""
    out: dict[str, Any] = {}
    for k in ("1", "2", "3", "total"):
        d = df if k == "total" else df[df["ciclo"] == int(k)]
        amb = d["motivo"].str.startswith("ambiguo")
        bloco = {"candidatos": int(len(d)), "ligados": int(d["ligado"].sum()), "taxa": float(d["ligado"].mean()),
                 "ambiguos": int(amb.sum()), "fracao_ambiguos": float(amb.mean()),
                 "por_etapa": {e: int(n) for e, n in d["etapa_ligacao"].dropna().value_counts().sort_index().items()},
                 "motivos": {m: int(n) for m, n in d["motivo"].value_counts().sort_index().items()}}
        for nome, a in (("alocados", 1), ("nao_alocados", 0)):
            g = d[d["alocado_1a_chamada"] == a]
            bloco[nome] = {"candidatos": int(len(g)), "ligados": int(g["ligado"].sum()),
                           "taxa": float(g["ligado"].mean()) if len(g) else None}
        if bloco["alocados"]["taxa"] is not None and bloco["nao_alocados"]["taxa"] is not None:
            bloco["diferenca_alocados_menos_nao_alocados"] = bloco["alocados"]["taxa"] - bloco["nao_alocados"]["taxa"]
        lig = d[d["ligado"] == 1]
        bloco["ligados_com_vinculo_na_referencia"] = int(lig["vinculo_medico_na_referencia"].fillna(0).sum())
        bloco["ligados_com_municipio_de_origem"] = int(lig["co_ibge_origem"].notna().sum())
        bloco["taxa_com_municipio_de_origem"] = float(d["co_ibge_origem"].notna().mean())
        out[k] = bloco
    return out


def veredito(tx: dict, validacao: dict, dic_meta: dict, chave_por_ciclo: dict) -> dict:
    """Veredito do portão pelos critérios fixados (TAXA_*, AMBIGUO_MAX, CONCORDANCIA_*, DIFERENCA_ALOCACAO_MAX,
    COBERTURA_DICIONARIO_MIN). `chave_por_ciclo[k]`: posições do CPF comuns ao candidato e ao CNES."""
    motivos, por_ciclo = [], {}
    cpf_util = any(v.get("n_posicoes", 0) > 0 for v in chave_por_ciclo.values())
    for k in ("1", "2", "3"):
        b = tx[k]
        taxa = b["taxa_com_municipio_de_origem"]
        r = []
        if taxa >= TAXA_VIAVEL:
            nivel = "VIAVEL"
        elif taxa >= TAXA_PARCIAL:
            nivel = "VIAVEL_PARCIAL"
            r.append(f"taxa com município de origem {taxa:.3f} < {TAXA_VIAVEL}")
        else:
            nivel = "INVIAVEL"
            r.append(f"taxa com município de origem {taxa:.3f} < {TAXA_PARCIAL}")
        if b["fracao_ambiguos"] > AMBIGUO_MAX:
            r.append(f"ambíguos {b['fracao_ambiguos']:.3f} > {AMBIGUO_MAX}")
            nivel = "VIAVEL_PARCIAL" if nivel == "VIAVEL" else nivel
        dif = b.get("diferenca_alocados_menos_nao_alocados")
        if dif is not None and abs(dif) > DIFERENCA_ALOCACAO_MAX:
            r.append(f"diferença de ligação alocados − não alocados {dif:+.3f} além de ±{DIFERENCA_ALOCACAO_MAX}")
            nivel = "VIAVEL_PARCIAL" if nivel == "VIAVEL" else nivel
        cob = dic_meta["cobertura_do_dicionario_sobre_medicos_x1"][REFERENCIA[int(k)]]["fracao"]
        if cob < COBERTURA_DICIONARIO_MIN:
            r.append(f"dicionário de {COMPETENCIA_DICIONARIO} cobre só {cob:.3f} dos médicos da referência "
                     f"{REFERENCIA[int(k)]}")
            nivel = "VIAVEL_PARCIAL" if nivel == "VIAVEL" else nivel
        npos = chave_por_ciclo[k].get("n_posicoes", 0)
        if npos < MIN_DIGITOS_VISIVEIS:
            r.append(f"a chave do CPF tem só {npos} dígito(s) comum(ns) ao CO_CPF do CNES: a ligação se apoia no "
                     "nome (informativo; a concordância com a rota X1 mede o risco)")
        por_ciclo[k] = {"veredito": nivel, "motivos": r}
    conc = validacao.get("concordancia")
    if conc is None or conc < CONCORDANCIA_MIN:
        motivos.append(f"concordância com a rota X1 {conc} < {CONCORDANCIA_MIN}")
    if not cpf_util:
        motivos.append("nenhuma posição do CPF comum entre as máscaras do candidato e do CNES: só a sensibilidade "
                       "por nome está disponível")
    niveis = [v["veredito"] for v in por_ciclo.values()]
    if all(n == "INVIAVEL" for n in niveis) or not cpf_util or conc is None or conc < CONCORDANCIA_INVIAVEL:
        geral = "INVIAVEL"
    elif all(n == "VIAVEL" for n in niveis) and not motivos:
        geral = "VIAVEL"
    else:
        geral = "VIAVEL_PARCIAL"
    return {"veredito": geral, "por_ciclo": por_ciclo, "motivos_gerais": motivos,
            "criterios": {"taxa_viavel": TAXA_VIAVEL, "taxa_parcial": TAXA_PARCIAL, "ambiguos_max": AMBIGUO_MAX,
                          "concordancia_min": CONCORDANCIA_MIN, "concordancia_inviavel": CONCORDANCIA_INVIAVEL,
                          "cobertura_dicionario_min": COBERTURA_DICIONARIO_MIN,
                          "revisao_antes_de_ligar": ("o critério 'dicionário diferente da competência de referência' "
                                                     "virou 'cobertura do dicionário sobre os médicos da referência < "
                                                     f"{COBERTURA_DICIONARIO_MIN}' depois da extração mostrar que a "
                                                     "tbDadosProfissionalSus é cumulativa, antes de qualquer ligação"),
                          "diferenca_alocacao_max": DIFERENCA_ALOCACAO_MAX,
                          "base_da_taxa": "candidatos com município de origem na competência de referência / "
                                          "candidatos de escolhas_candidatos do ciclo",
                          "fixados": "antes de ligar; regra G1 como principal"}}


# ---------------------------------------------------------------- análise

def _json_default(o: Any) -> Any:
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o) if math.isfinite(o) else None
    if isinstance(o, np.bool_):
        return bool(o)
    if o is pd.NA:
        return None
    raise TypeError(type(o))


def bloco_entrada(caminho: Path, papel: str, data_ref: str, cobertura: str, unidade: str, chaves: str,
                  filtros: str) -> dict:
    return {"caminho": rel(caminho), "sha256": sha256_arquivo(caminho), "bytes": caminho.stat().st_size,
            "papel": papel, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade,
            "chaves": chaves, "filtros": filtros}


COLS_CAND = ["natureza_dos_dados", "estatuto", "regra_ligacao", "ciclo", "id_candidato", "alocado_1a_chamada",
             "ligado", "etapa_ligacao", "motivo", "competencia_referencia", "vinculo_medico_na_referencia",
             "n_vinculos_referencia", "n_municipios_origem", "co_ibge_origem", "uf_origem",
             "origem_principal_empatada", "motivo_origem_ausente", "ligado_rota_x1", "mesmo_profissional_rota_x1"]


def analisar() -> None:
    cands, diag_cand = ler_candidatos()
    meta_p = caminho_meta(COMPETENCIA_DICIONARIO)
    if not (meta_p.exists() and caminho_dicionario(COMPETENCIA_DICIONARIO).exists()):
        raise SystemExit("dicionário do G1 ausente; rode --etapa aquisicao (fail closed)")
    dic_meta = json.loads(meta_p.read_text(encoding="utf-8"))
    cands = chaves_candidatos(cands, dic_meta["padrao_co_cpf_dominante"])
    if dic_meta.get("assinatura_alvo") != assinatura_alvo(cands) or dic_meta.get("versao_cache") != VERSAO_CACHE:
        raise SystemExit("candidatos mudaram desde a extração do dicionário; refaça a aquisição (fail closed)")
    dic = pd.read_parquet(caminho_dicionario(COMPETENCIA_DICIONARIO))
    vinc, nomes_x1, metas_x1 = X1.ler_cache()
    sem_a09 = [c for c, m in metas_x1.items() if not m.get("validacao_contra_a09", {}).get("sha256_igual_ao_a09")]
    if sem_a09:
        raise AssertionError(f"cache da X1 com SHA-256 diferente do a09: {sem_a09}")
    if any(c >= LIMITE_EXCLUSIVO for c in vinc["competencia"].unique()):
        raise AssertionError("competência >= 202609 no cache")

    # Conjunto de busca do ciclo: vínculo médico em alguma competência até a referência, e no dicionário.
    no_dic = set(dic["co_profissional_sus"])
    pool, diag_pool = {}, {}
    for k in CICLOS:
        comps = [c for c in COMPETENCIAS_X1 if c <= REFERENCIA[k]]
        medicos = set(vinc.loc[vinc["competencia"].isin(comps), "co_profissional_sus"].dropna())
        pool[k] = medicos & no_dic
        diag_pool[str(k)] = {"competencias": comps, "competencia_referencia": REFERENCIA[k],
                             "abertura_inscricoes": ABERTURA_INSCRICOES[k],
                             "profissionais_do_cache_guardados_e_procuraveis": len(pool[k])}

    inv, diag_inv = inventario(cands)
    pares_x1, diag_x1 = rota_x1(vinc, nomes_x1)
    coord, diag_coord = X1.ler_coordenadas()
    escolhas = pd.read_parquet(ESCOLHAS)

    saidas, dists, tx, validacao, extra = [], [], {}, {}, {}
    for regra in REGRAS:
        lig = ligar(cands, dic, pool, usar_cpf=(regra == "g1_cpf_nome"))
        lig = lig.merge(cands[["ciclo", "id_candidato", "alocado_1a_chamada"]], on=["ciclo", "id_candidato"],
                        validate="one_to_one")
        org = origem(lig, vinc)
        m = lig.merge(org, on=["ciclo", "id_candidato"], how="left", validate="one_to_one")
        m["uf_origem"] = m["co_ibge_origem"].str[:2]
        v = m.merge(pares_x1, on=["ciclo", "id_candidato"], how="left", validate="one_to_one")
        tem_x1 = v["co_profissional_sus_x1"].notna()
        m["ligado_rota_x1"] = np.where(m["ciclo"].isin([1, 2]), tem_x1.astype(int), np.nan)
        ambos = tem_x1 & v["co_profissional_sus"].notna()
        m["mesmo_profissional_rota_x1"] = np.where(ambos, (v["co_profissional_sus"] == v["co_profissional_sus_x1"]),
                                                   np.nan).astype(float)
        validacao[regra] = {
            "candidatos_ligados_pela_rota_x1": int(tem_x1.sum()),
            "ligados_tambem_pela_regra": int(ambos.sum()),
            "mesmo_profissional": int((v.loc[ambos, "co_profissional_sus"] == v.loc[ambos, "co_profissional_sus_x1"]).sum()),
            "concordancia": float((v.loc[ambos, "co_profissional_sus"] == v.loc[ambos, "co_profissional_sus_x1"]).mean())
            if ambos.any() else None,
            "rota_x1_sem_ligacao_pela_regra": int((tem_x1 & v["co_profissional_sus"].isna()).sum()),
            "motivos_dos_nao_ligados_pela_regra_entre_os_da_rota_x1": {
                k: int(n) for k, n in v.loc[tem_x1 & v["co_profissional_sus"].isna(), "motivo"].value_counts().items()},
        }
        tx[regra] = taxas(m)
        validacao[regra]["entre_ciclos"] = validacao_entre_ciclos(cands, lig)
        if regra == "g1_cpf_nome":
            d = distancias(m, escolhas, coord)
            d.insert(0, "regra_ligacao", regra)
            dists.append(d)
            conj = pd.read_parquet(CONJ_PRINCIPAL, columns=["ciclo", "co_ibge"])
            xy = set(coord["co_ibge"])
            extra["distancias"] = {
                "linhas_candidato_opcao": int(len(d)),
                "com_distancia": int(d["dist_km_origem_mais_proxima"].notna().sum()),
                "motivos_ausencia": {k: int(n) for k, n in
                                     d.loc[d["dist_km_origem_mais_proxima"].isna(), "motivo_distancia_ausente"]
                                     .value_counts().items()},
                "por_ciclo": {str(k): {"linhas": int((d["ciclo"] == k).sum()),
                                       "com_distancia": int(d.loc[d["ciclo"] == k, "dist_km_origem_mais_proxima"]
                                                            .notna().sum())} for k in CICLOS},
                "municipios_do_conjunto_principal_com_centroide": {
                    str(k): {"municipios": int(g["co_ibge"].nunique()),
                             "com_centroide": int(g["co_ibge"].drop_duplicates().isin(xy).sum())}
                    for k, g in conj.groupby("ciclo")},
                "municipios_de_origem_com_centroide": {
                    "municipios": int(m["co_ibge_origem"].dropna().nunique()),
                    "com_centroide": int(m["co_ibge_origem"].dropna().drop_duplicates().isin(xy).sum())},
            }
        m["regra_ligacao"] = regra
        m["natureza_dos_dados"] = NATUREZA
        m["estatuto"] = ESTATUTO
        for c in COLS_CAND:
            if c not in m:
                m[c] = pd.NA
        saidas.append(m[COLS_CAND])
    # Concordância entre as regras (mesmo candidato, mesmo profissional?)
    a = saidas[0].merge(saidas[1], on=["ciclo", "id_candidato"], suffixes=("_cpf", "_nome"))
    comparacao = {"ligados_nas_duas": int(((a["ligado_cpf"] == 1) & (a["ligado_nome"] == 1)).sum()),
                  "ligado_so_na_principal": int(((a["ligado_cpf"] == 1) & (a["ligado_nome"] == 0)).sum()),
                  "ligado_so_na_sensibilidade": int(((a["ligado_cpf"] == 0) & (a["ligado_nome"] == 1)).sum()),
                  "mesma_origem_quando_ligado_nas_duas": int(
                      (a.loc[(a["ligado_cpf"] == 1) & (a["ligado_nome"] == 1), "co_ibge_origem_cpf"]
                       .fillna("NA") == a.loc[(a["ligado_cpf"] == 1) & (a["ligado_nome"] == 1), "co_ibge_origem_nome"]
                       .fillna("NA")).sum())}
    out = pd.concat(saidas, ignore_index=True).sort_values(["regra_ligacao", "ciclo", "id_candidato"])
    for c in ("vinculo_medico_na_referencia", "n_vinculos_referencia", "n_municipios_origem", "origem_principal_empatada"):
        out[c] = pd.to_numeric(out[c], errors="coerce").astype("Int64")
    out["etapa_ligacao"] = out["etapa_ligacao"].astype("string")
    out["co_ibge_origem"] = out["co_ibge_origem"].astype("string")
    out["uf_origem"] = out["uf_origem"].astype("string")
    out["motivo_origem_ausente"] = out["motivo_origem_ausente"].astype("string")
    out = out.reset_index(drop=True)
    dist = pd.concat(dists, ignore_index=True)
    dist.insert(0, "natureza_dos_dados", NATUREZA)
    dist["co_ibge_opcao"] = dist["co_ibge_opcao"].astype("string")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_CANDIDATOS, index=False)
    dist.sort_values(["ciclo", "id_candidato", "opcao_rank", "co_cnes_7d", "cod_curso"]).reset_index(drop=True).to_parquet(
        OUT_DISTANCIAS, index=False)
    inv.to_csv(OUT_INVENTARIO, index=False)

    chave_por_ciclo = {}
    for k in CICLOS:
        g = cands[cands["ciclo"] == k]
        pc = g["_posicoes_comuns"].dropna()
        dom = pc.mode().iloc[0] if len(pc) else ""
        chave_por_ciclo[str(k)] = {"padrao_candidato": g["_padrao"].dropna().mode().iloc[0],
                                   "posicoes_comuns_com_co_cpf": dom,
                                   "n_posicoes": len(dom.split("-")) if dom else 0,
                                   "candidatos_sem_chave": int(g["_chave"].isna().sum())}
    ver = veredito(tx["g1_cpf_nome"], validacao["g1_cpf_nome"], dic_meta, chave_por_ciclo)
    entradas = [bloco_entrada(p, papel, "publicação do edital", f"ciclo {k}, chamada {ch}", "candidato × opção",
                              "nome, CPF mascarado (só em memória)", "somente leitura")
                for p, k, ch, papel in INVENTARIO]
    entradas += [
        bloco_entrada(ESCOLHAS, "universo de candidatos (id_candidato) e alocação da 1ª chamada", "ciclos 1–3",
                      "candidatos da 1ª chamada", "candidato × opção", "ciclo, id_candidato, opcao_rank", "nenhum"),
        bloco_entrada(CONJ_PRINCIPAL, "municípios do conjunto de escolha (cobertura de centroides)", "ciclos 1–3",
                      "células", "célula", "ciclo, co_cnes_7d, cod_curso", "colunas ciclo e co_ibge"),
        bloco_entrada(MANIFESTO_A09, "SHA-256 do ZIP do CNES (validação)", "2026-10-18", "competências do a09",
                      "competência", "competencia", "por_competencia"),
        bloco_entrada(X1.ATIVOS_ZIP, "rota X1 de validação: lista de ativos (CRM, UF do posto, nome em memória)",
                      "11/09/2026", "ciclos 1–3", "médico ativo", "ciclo, crm, uf, co_cnes, curso", "nenhum gravado"),
        bloco_entrada(X1.NOMINAL_CSV, "rota X1 de validação: lista nominal", "2026-08-12", "ciclos 1–2", "médico ativo",
                      "ciclo, crm, uf, co_cnes, curso", "nenhum gravado"),
        bloco_entrada(X1.COORD_JSON, "centroides municipais do IBGE (distância)", "malha da API v3", "Brasil",
                      "município", "id (7 dígitos)", "centroide"),
        bloco_entrada(PLANO_51, "plano (portão G1, §5 onda 1)", "19/10/2026", "—", "—", "—", "—"),
    ]
    cache_x1 = {c: {k: metas_x1[c].get(k) for k in ("url", "sha256_zip", "linhas_vinculos_medicos",
                                                    "profissionais_distintos", "validacao_contra_a09")}
                for c in COMPETENCIAS_X1}
    resumo = {
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "documento": "portão G1 do plano das perguntas reformuladas (doc 51, §5, onda 1; T1.0)",
        "script": rel(Path(__file__)),
        "data_execucao": dt.date.today().isoformat(),
        "contraste": "nenhum: só cobertura e ligação; IVS não lido; nada por lado de corte, faixa, alocação ou outcome",
        "entradas": entradas,
        "limite_ciclo3": f"nenhuma competência >= {LIMITE_EXCLUSIVO} é baixada ou lida",
        "identificadores": {
            "conclusao": ("os arquivos de classificação e resultado trazem nome e CPF mascarado de todos os "
                          "candidatos classificados (e dos desclassificados, em aba própria); nenhum traz CRM, "
                          "UF do CRM ou número de inscrição. A coluna UF é a do posto/estabelecimento. A modalidade "
                          "(AC, ER, PCD) não identifica a pessoa. O CRM só existe nas listas de ativos do PMM-E"),
            "candidatos_escolhas": diag_cand,
            "inventario": OUT_INVENTARIO.name,
            **diag_inv,
        },
        "dicionario_cnes": {k: dic_meta.get(k) for k in (
            "competencia", "url", "data_download", "sha256_zip", "bytes_zip", "sha256_igual_ao_a09", "membros_lidos",
            "colunas_tbDadosProfissionalSus", "linhas_tbDadosProfissionalSus", "profissionais_distintos_no_dicionario",
            "moldes_co_cpf", "padroes_co_cpf", "padrao_co_cpf_dominante", "linhas_com_o_padrao_dominante",
            "posicoes_comuns_por_padrao_candidato", "profissionais_distintos_na_carga_horaria_todas_cbo",
            "profissionais_do_dicionario_sem_vinculo_na_competencia", "cobertura_do_dicionario_sobre_medicos_x1",
            "linhas_guardadas_no_cache", "profissionais_com_mais_de_uma_linha", "padroes_cpf_candidatos", "status")},
        "chave_cpf_por_ciclo": chave_por_ciclo,
        "cache_x1": cache_x1,
        "competencia_referencia": {str(k): REFERENCIA[k] for k in CICLOS},
        "conjunto_de_busca": diag_pool,
        "regra_ligacao": {
            "g1_cpf_nome": ("principal: (1) chave dos dígitos visíveis do CPF mascarado = mesma posição do CO_CPF e "
                            "nome normalizado idêntico, um único profissional; (2) sem (1), chave igual e nome "
                            "compatível (definição da X1), um único profissional; ambíguos e não achados fora; "
                            "profissional ligado a mais de um candidato do ciclo: todos fora"),
            "g1_so_nome": ("sensibilidade: nome normalizado idêntico e único no conjunto de busca do ciclo, sem CPF"),
            "por_que_nao_a_regra_da_x1": ("os arquivos de candidatos não trazem CRM nem UF do CRM; a regra da X1 "
                                          "só vale para quem está na lista de ativos (rota X1, usada como validação)"),
            "nome_compativel": ("tokens normalizados sem partículas " + ",".join(sorted(X1.PARTICULAS)) +
                                "; mesmo primeiro nome e (mesmo último ou um conjunto contido no outro, ≥ 2 nomes)"),
            "mascara": f"11 posições (dígito visível ou X/*), ao menos {MIN_DIGITOS_VISIVEIS} dígitos visíveis",
        },
        "taxas_ligacao": tx,
        "comparacao_entre_regras": comparacao,
        "validacao_rota_x1": {"diagnostico_rota": diag_x1, **validacao},
        "origem_e_distancia": {
            "definicao_origem": ("municípios (CO_MUNICIPIO_GESTOR do estabelecimento) com vínculo médico na "
                                 "competência de referência do ciclo; principal = o de mais vínculos (empate: menor "
                                 "código, marcado em origem_principal_empatada)"),
            "definicao_distancia": (f"círculo máximo (raio {X1.RAIO_TERRA_KM} km) entre centroides do IBGE: do "
                                    "município da célula ranqueada ao de origem principal e ao mais próximo"),
            "coordenadas": {k: diag_coord.get(k) for k in ("status", "municipios", "url", "sha256",
                                                           "malha_periodo_verificado")},
            **extra.get("distancias", {}),
        },
        "veredito": ver,
        "o_que_os_protocolos_podem_usar": None,  # preenchido abaixo, a partir do veredito
        "download_para_o_g1_completo": {
            "necessario": [f"tbDadosProfissionalSus de {REFERENCIA[k]} (referência do ciclo {k})" for k in CICLOS
                           if dic_meta["cobertura_do_dicionario_sobre_medicos_x1"][REFERENCIA[k]]["fracao"]
                           < COBERTURA_DICIONARIO_MIN],
            "nota": (f"a tbDadosProfissionalSus de {COMPETENCIA_DICIONARIO} é cumulativa (traz profissionais sem "
                     "vínculo na competência) e contém todos os médicos das competências de referência; nenhum "
                     "download adicional é necessário para a identidade. Os locais vêm do cache da X1"),
            "como": ("BASE_DE_DADOS_CNES_AAAAMM.ZIP pelo servlet HTTPS do a09 (URL_BASE), conferido contra o SHA-256 do "
                     "manifesto do a09, extraído para output/rdd_bolsa/G1_cache/ e apagado; mesma função adquirir()"),
        },
        "limitacoes": [
            "o universo é o de escolhas_candidatos (classificados com opção na 1ª chamada); desclassificados, 2ª "
            "chamada e quem não se inscreveu não entram",
            "um único dicionário de profissionais (competência 202602, cumulativo) identifica as pessoas dos três "
            "ciclos; o nome é o de 202602 (mudança de nome depois da referência pode impedir a ligação)",
            "o CO_CPF público é mascarado (posições 4 a 9); nos ciclos 1 e 2 só 2 dígitos são comuns à máscara dos "
            "candidatos, e a ligação se apoia no nome; a validação só cobre alocados (rota X1) e pessoas que "
            "voltaram em outro ciclo",
            "o conjunto de busca usa o cache da X1 (seis competências); vínculo só em meses não lidos não conta",
            "vínculo no CNES não é presença nem trabalho efetivo; ausência de vínculo não prova ausência de atividade",
            "a origem é o município do estabelecimento (gestor), não a residência do candidato",
        ],
        "dados_pessoais": ("nenhum nome, CPF, CNS, CRM ou código de profissional é gravado em output/rdd_bolsa/G1_*; "
                           "o cache em output/rdd_bolsa/G1_cache/ (ignorado pelo Git) guarda nome normalizado e chave "
                           "do CPF em SHA-256 só dos profissionais com nome idêntico ao de algum candidato ou com o "
                           "mesmo primeiro nome e a mesma chave. "
                           "id_candidato é pseudônimo FRACO: reconstrói-se a partir dos arquivos públicos de "
                           "resultado; com a origem, liga duas fontes públicas. Não cruzar com dados nominais"),
        "saidas": {},
    }
    resumo["o_que_os_protocolos_podem_usar"] = uso_protocolos(resumo)
    resumo["saidas"] = {rel(p): sha256_arquivo(p) for p in (OUT_CANDIDATOS, OUT_DISTANCIAS, OUT_INVENTARIO)}
    OUT_RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=_json_default) + "\n",
                          encoding="utf-8")
    t = tx["g1_cpf_nome"]["total"]
    log(f"G1: {t['ligados']} de {t['candidatos']} ligados (regra principal); veredito {ver['veredito']}")


def uso_protocolos(resumo: dict) -> dict:
    tx = resumo["taxas_ligacao"]["g1_cpf_nome"]
    ver = resumo["veredito"]
    linhas_p1 = [f"ciclo {k}: {fmt_pct(tx[k]['taxa_com_municipio_de_origem'])} dos candidatos com município de origem "
                 f"em {resumo['competencia_referencia'][k]} ({ver['por_ciclo'][k]['veredito']})" for k in ("1", "2", "3")]
    return {
        "P1_T1_1": ("distância origem–célula para todos os candidatos ligados com vínculo na referência, não só "
                    "alocados; " + "; ".join(linhas_p1) + ". Candidatos sem origem ficam fora com o motivo, e a "
                    "amostra com distância entra como limite e sensibilidade (doc 51, P1, ameaças)"),
        "P6_T6_2": ("outcomes CNES individuais dos ciclos 1 e 2 pelo CO_PROFISSIONAL_SUS ligado (painel mensal do "
                    "G5); a ligação usa só informação pré-programa no conjunto de busca e o dicionário cumulativo "
                    "cobre todos os médicos da referência. A taxa de ligação por alocação vai para o protocolo 56 "
                    "como diagnóstico de seleção; não ligados ficam fora com o motivo, com limites para a ligação "
                    "diferencial. Nos ciclos 1 e 2 a chave do CPF tem 2 dígitos, e o nome faz a maior parte da "
                    "ligação: a sensibilidade só por nome (mesma origem em quase todos) deve ser repetida no T6.2"),
    }


# ---------------------------------------------------------------- documento

MARCA = re.compile(r"(<!-- G1:(?P<nome>[a-z_0-9]+):inicio -->\n)(?P<corpo>.*?)(<!-- G1:(?P=nome):fim -->)", re.S)


def fmt_int(x: Any) -> str:
    return f"{int(x):,}".replace(",", ".")


def fmt_pct(x: Any, casas: int = 1) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{100 * x:.{casas}f}%".replace(".", ",")


def blocos_doc(resumo: dict, inv: pd.DataFrame, cand: pd.DataFrame) -> dict[str, str]:
    b: dict[str, str] = {}
    # Inventário
    linhas = ["| Arquivo | Aba | Ciclo | Chamada | Papel | Pessoas (nome + CPF) | Nome | CPF mascarado (molde) | CRM | UF do CRM | Nº de inscrição | Candidatos de `escolhas` presentes |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in inv.itertuples(index=False):
        linhas.append(f"| `{Path(r.arquivo).name}` | {r.aba} | {r.ciclo} | {r.chamada} | {r.papel} | "
                      f"{fmt_int(r.pessoas_nome_cpf)} | {'sim' if r.tem_nome else 'não'} | `{r.moldes_cpf}` | "
                      f"{'sim' if r.tem_crm else 'não'} | {'sim' if r.tem_uf_do_crm else 'não'} | "
                      f"{'sim' if r.tem_numero_inscricao else 'não'} | {fmt_int(r.candidatos_de_escolhas_presentes)} "
                      f"de {fmt_int(r.candidatos_de_escolhas_no_ciclo)} |")
    b["inventario"] = "\n".join(linhas) + "\n"
    # Dicionário
    d = resumo["dicionario_cnes"]
    cob = d["cobertura_do_dicionario_sobre_medicos_x1"]
    linhas = [f"- Competência baixada: {d['competencia']} (SHA-256 igual ao do a09: {'sim' if d['sha256_igual_ao_a09'] else 'não'}).",
              f"- `tbDadosProfissionalSus`: {fmt_int(d['linhas_tbDadosProfissionalSus'])} linhas; "
              f"o `CO_CPF` público é mascarado: molde mais comum `{next(iter(d['moldes_co_cpf']))}`, posições "
              f"visíveis {d['padrao_co_cpf_dominante']} em {fmt_int(d['linhas_com_o_padrao_dominante'])} linhas.",
              "- Posições do CPF comuns ao candidato e ao CNES (base da chave): " + "; ".join(
                  f"ciclo {k}: {v['posicoes_comuns_com_co_cpf'] or 'nenhuma'} ({v['n_posicoes']} dígitos)"
                  for k, v in resumo["chave_cpf_por_ciclo"].items()) + " (posições contadas a partir de 0).",
              f"- Profissionais do dicionário sem vínculo na própria competência: "
              f"{fmt_int(d['profissionais_do_dicionario_sem_vinculo_na_competencia'])}.",
              "- Médicos de cada competência do cache da X1 presentes no dicionário: " + "; ".join(
                  f"{c}: {fmt_pct(v['fracao'])}" for c, v in cob.items()) + "."]
    b["dicionario"] = "\n".join(linhas) + "\n"
    # Taxas
    linhas = ["| Regra | Ciclo | Referência | Candidatos | Ligados | Taxa | Com município de origem | Ambíguos | Alocados: taxa | Não alocados: taxa |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    rot = {"g1_cpf_nome": "G1 (CPF + nome), principal", "g1_so_nome": "só nome, sensibilidade"}
    for regra, tx in resumo["taxas_ligacao"].items():
        for k in ("1", "2", "3", "total"):
            t = tx[k]
            linhas.append(f"| {rot[regra]} | {k} | {resumo['competencia_referencia'].get(k, '—')} | "
                          f"{fmt_int(t['candidatos'])} | {fmt_int(t['ligados'])} | {fmt_pct(t['taxa'])} | "
                          f"{fmt_pct(t['taxa_com_municipio_de_origem'])} | {fmt_int(t['ambiguos'])} "
                          f"({fmt_pct(t['fracao_ambiguos'])}) | {fmt_pct(t['alocados']['taxa'])} | "
                          f"{fmt_pct(t['nao_alocados']['taxa'])} |")
    b["taxas"] = "\n".join(linhas) + "\n"
    # Motivos (regra principal)
    tx = resumo["taxas_ligacao"]["g1_cpf_nome"]
    motivos = sorted(set().union(*(tx[k]["motivos"] for k in ("1", "2", "3"))))
    linhas = ["| Motivo | Ciclo 1 | Ciclo 2 | Ciclo 3 |", "|---|---|---|---|"]
    for mo in motivos:
        linhas.append(f"| `{mo}` | " + " | ".join(fmt_int(tx[k]["motivos"].get(mo, 0)) for k in ("1", "2", "3")) + " |")
    etapas = sorted(set().union(*(tx[k]["por_etapa"] for k in ("1", "2", "3"))))
    for e in etapas:
        linhas.append(f"| ligado pela etapa `{e}` | " + " | ".join(fmt_int(tx[k]["por_etapa"].get(e, 0))
                                                                  for k in ("1", "2", "3")) + " |")
    b["motivos"] = "\n".join(linhas) + "\n"
    # Validação
    v = resumo["validacao_rota_x1"]
    linhas = []
    for regra in ("g1_cpf_nome", "g1_so_nome"):
        x = v[regra]
        linhas.append(f"- {rot[regra]}: dos {fmt_int(x['candidatos_ligados_pela_rota_x1'])} candidatos alocados "
                      f"ligados pela rota X1, {fmt_int(x['ligados_tambem_pela_regra'])} também ligam pela regra; o "
                      f"profissional é o mesmo em {fmt_int(x['mesmo_profissional'])} "
                      f"(concordância {fmt_pct(x['concordancia'], 2)}); "
                      f"{fmt_int(x['rota_x1_sem_ligacao_pela_regra'])} não ligam pela regra.")
    for par, x in v["g1_cpf_nome"]["entre_ciclos"].items():
        ca, cb = par.removeprefix("ciclos_").split("_e_")
        linhas.append(f"- Mesma pessoa nos ciclos {ca} e {cb} (nome idêntico e dígitos comuns do CPF iguais): "
                      f"{fmt_int(x['pares_mesma_pessoa'])} pares, {fmt_int(x['ligados_nos_dois'])} ligados nos dois "
                      f"pela regra principal, mesmo profissional em {fmt_int(x['mesmo_profissional'])} "
                      f"(concordância {fmt_pct(x['concordancia'], 2)}; entre os não alocados no ciclo {ca}: "
                      f"{fmt_pct(x['concordancia_nao_alocados_no_ciclo_anterior'], 2)} de "
                      f"{fmt_int(x['nao_alocados_no_ciclo_anterior_ligados_nos_dois'])}).")
    c = resumo["comparacao_entre_regras"]
    linhas.append(f"- Entre as regras: {fmt_int(c['ligados_nas_duas'])} ligados nas duas, "
                  f"{fmt_int(c['ligado_so_na_principal'])} só na principal, "
                  f"{fmt_int(c['ligado_so_na_sensibilidade'])} só na sensibilidade; mesma origem em "
                  f"{fmt_int(c['mesma_origem_quando_ligado_nas_duas'])} dos ligados nas duas.")
    b["validacao"] = "\n".join(linhas) + "\n"
    # Distância
    o = resumo["origem_e_distancia"]
    linhas = [f"- Linhas candidato × opção: {fmt_int(o['linhas_candidato_opcao'])}; com distância: "
              f"{fmt_int(o['com_distancia'])} (" + "; ".join(
                  f"ciclo {k}: {fmt_int(x['com_distancia'])} de {fmt_int(x['linhas'])}" for k, x in o["por_ciclo"].items())
              + ").",
              "- Sem distância, por motivo: " + "; ".join(f"{k}: {fmt_int(n)}" for k, n in o["motivos_ausencia"].items())
              + ".",
              "- Municípios do conjunto de escolha com centroide: " + "; ".join(
                  f"ciclo {k}: {fmt_int(x['com_centroide'])} de {fmt_int(x['municipios'])}"
                  for k, x in o["municipios_do_conjunto_principal_com_centroide"].items()) + ".",
              f"- Municípios de origem com centroide: {fmt_int(o['municipios_de_origem_com_centroide']['com_centroide'])} "
              f"de {fmt_int(o['municipios_de_origem_com_centroide']['municipios'])}."]
    b["distancia"] = "\n".join(linhas) + "\n"
    # Veredito
    ver = resumo["veredito"]
    linhas = [f"**Veredito: `{ver['veredito']}`.**", ""]
    for k, x in ver["por_ciclo"].items():
        linhas.append(f"- Ciclo {k}: `{x['veredito']}`" + (" — " + "; ".join(x["motivos"]) if x["motivos"] else "") + ".")
    for mo in ver["motivos_gerais"]:
        linhas.append(f"- Geral: {mo}.")
    u = resumo["o_que_os_protocolos_podem_usar"]
    linhas += ["", f"- **P1 (T1.1):** {u['P1_T1_1']}.", f"- **P6 (T6.2):** {u['P6_T6_2']}."]
    dl = resumo["download_para_o_g1_completo"]
    linhas.append("- Download adicional: " + ("; ".join(dl["necessario"]) if dl["necessario"] else
                                             "nenhum; " + dl["nota"]) + ".")
    b["veredito"] = "\n".join(linhas) + "\n"
    return b


def ler_saidas() -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    resumo = json.loads(OUT_RESUMO.read_text(encoding="utf-8"))
    return resumo, pd.read_csv(OUT_INVENTARIO), pd.read_parquet(OUT_CANDIDATOS)


def atualizar_doc() -> None:
    resumo, inv, cand = ler_saidas()
    gerados = blocos_doc(resumo, inv, cand)
    texto = DOC.read_text(encoding="utf-8")
    no_doc = {m.group("nome") for m in MARCA.finditer(texto)}
    if no_doc != set(gerados):
        raise SystemExit(f"blocos do doc ({sorted(no_doc)}) diferem dos gerados ({sorted(gerados)})")
    DOC.write_text(MARCA.sub(lambda m: m.group(1) + gerados[m.group("nome")] + m.group(4), texto), encoding="utf-8")
    log(f"doc G1: {len(gerados)} blocos atualizados")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--etapa", choices=("analise", "aquisicao", "tudo"), default="analise")
    ap.add_argument("--atualizar-doc", action="store_true")
    ap.add_argument("--manter-zip", action="store_true", help="não apaga o ZIP depois da extração")
    args = ap.parse_args()
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    if args.etapa in ("aquisicao", "tudo"):
        adquirir(manter_zip=args.manter_zip)
    if args.etapa in ("analise", "tudo"):
        analisar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
