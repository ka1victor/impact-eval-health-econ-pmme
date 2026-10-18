"""Tarefa B do protocolo E6: outcomes F0, F1, F2 e F4 do funil do PMM-E, ciclos 1 a 3.

Constrói, de forma determinística e só a partir de arquivos do repositório, as
bases de outcome do protocolo congelado
`docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`
(`output/rdd_bolsa/protocolo_E6_multioutcome.json`), em
`output/rdd_bolsa/outcomes/`:

- `outcomes_U_municipio.parquet`: U, todos os municípios com IVS 2010 oficial
  (F0.1, F0.2, F0.4, F2.2);
- `outcomes_G3_municipio.parquet`: G3, os municípios do cardápio de gestores do
  ciclo 3 (F0.3);
- `outcomes_V_municipio.parquet`: V1, V2 e V3 empilhados, uma linha por
  município e ciclo (F1.1–F1.4, F2.1, F2.3, F4.1, F4.2);
- `outcomes_V_celula.parquet`: as mesmas medidas por célula CNES × curso do
  quadro da 1a chamada de cada ciclo, com o município, a faixa impressa no
  quadro e o código do curso;
- `escolhas_candidatos.parquet`, `escolhas_conjunto_principal.parquet` e
  `escolhas_conjunto_sensibilidade_vaga_imediata.parquet`: E9 (adendo §12,
  conjunto fixado no §14), uma linha por candidato × opção ranqueada; o
  conjunto principal (todas as células do curso e ciclo no quadro da 1a
  chamada, com atributos) e o de sensibilidade (só células com vaga imediata);
- `dicionario_outcomes_funil.json`: fontes (caminho, SHA-256, data de
  referência, cobertura, unidade, chaves, filtros), definição de cada coluna,
  decisões de construção, taxas de casamento entre arquivos e desvios.

Regra de cegamento (protocolo, §9): nenhum outcome é quebrado por lado de
corte, por faixa da bolsa ou contra o IVS. O IVS 2010 oficial
(`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`) entra só como coluna
de chave levada para a saída; o arquivo local de IVS da auditoria 16 não é lido.
A faixa impressa no quadro é atributo da célula e só é conferida quanto a ser
única por município. Os resumos gravados no dicionário são distribuições
globais (contagem, ausentes, média, mínimo, máximo), nunca por lado.

Nenhum nome ou CPF é gravado. Os arquivos em `data/` são somente lidos.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import unicodedata
import warnings
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

PROTOCOLO = ROOT / "output" / "rdd_bolsa" / "protocolo_E6_multioutcome.json"
IVS_OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
POPULACAO = ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
MATRIZ_FUNIL = ROOT / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"
QUADRO_CANONICO_C1 = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
E4_MUNICIPIO = ROOT / "output" / "rdd_bolsa" / "E4_proporcao_municipio.csv"
MANIFESTO_FONTES = ROOT / "output" / "manifesto_fontes_pmme.json"
QUADRO_CONSOLIDADO = ROOT / "output" / "aquisicao" / "quadro_vagas_consolidado.parquet"
MANIFESTO_A07 = ROOT / "output" / "aquisicao" / "a07_manifesto_ivs_administrativo.json"
MANIFESTO_A11 = ROOT / "output" / "aquisicao" / "a11_manifesto_ciclo2_chamada1.json"

RAW_VAGAS = ROOT / "data" / "raw" / "aquisicao" / "vagas"
RAW_PMME = ROOT / "data" / "raw" / "pmm_e"
RAW_ADM = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo"

ATIVOS_ZIP = RAW_ADM / "tb_profissionais_ativos_pmme_csv.zip"
PPF_ZIP = RAW_ADM / "ppf_mais_medicos_csv.zip"
# Mesma versão da relação nominal usada pelo E3 (07_estimar_E3_rdd_completa.py).
SHA256_ATIVOS_PROTOCOLO = "e57edeb50946395fa90fe510f4a658501f9b0e92069fcc53aa41b9e893e89c1c"

# Quadros da 1a chamada que definem as células de V_k.
QUADRO_C1 = RAW_VAGAS / "2025_ciclo1_chamada1_vagas.xlsx"
QUADRO_C2 = RAW_PMME / "2026_ciclo2_chamada1_vagas_retificadas.xlsx"  # versão de 19/03/2026, a do E3 (P2)
QUADRO_C3 = RAW_PMME / "2026_ciclo3_chamada1_vagas_retificadas.xlsx"  # retificação de 24/07/2026
# Quadros auxiliares.
QUADRO_C1_CH2_CR = RAW_PMME / "2025_ciclo1_chamada2_vagas_e_alocados.xlsx"  # aba de cadastro reserva
QUADRO_C2_CH2 = RAW_PMME / "2026_ciclo2_chamada2_vagas.xlsx"
QUADROS_C2_VERSOES = {
    "original_2026-02-03": RAW_VAGAS / "2026_ciclo2_chamada1_vagas_e_servicos_original.xlsx",
    "retificado_servicos": RAW_VAGAS / "2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx",
    "retificado_2026-03-19 (usado)": QUADRO_C2,
}

# Arquivos de candidatura × opção.
CAND_C1 = RAW_VAGAS / "2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx"
CAND_C2 = RAW_PMME / "resultado-final-pmme-2o-ciclo-25-05.xlsx"
CAND_C2_PRELIMINAR = RAW_PMME / "resultado-preliminar-pmme.xlsx"
CAND_C2_REMANESC = RAW_PMME / "resultado-final-vagas-remanescentes.xlsx"
CAND_C2_REMANESC_0505 = RAW_PMME / "2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx"
CAND_C2_CH2 = RAW_PMME / "2026_ciclo2_chamada2_resultado_final.xlsx"
CAND_C3 = RAW_PMME / "2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx"

# Ciclo 3, gestores.
CARDAPIO_C3 = RAW_VAGAS / "2026_ciclo3_gestores_quadro_vagas_original.xlsx"
ADESAO_C3 = RAW_PMME / "2026_ciclo3_adesao_gestores_resultado_final.xlsx"

OUT_DIR = ROOT / "output" / "rdd_bolsa" / "outcomes"
OUT_U = OUT_DIR / "outcomes_U_municipio.parquet"
OUT_G3 = OUT_DIR / "outcomes_G3_municipio.parquet"
OUT_V_MUN = OUT_DIR / "outcomes_V_municipio.parquet"
OUT_V_CEL = OUT_DIR / "outcomes_V_celula.parquet"
OUT_DICIONARIO = OUT_DIR / "dicionario_outcomes_funil.json"
OUT_ESCOLHAS = OUT_DIR / "escolhas_candidatos.parquet"
OUT_CONJUNTO = OUT_DIR / "escolhas_conjunto_principal.parquet"
OUT_CONJUNTO_SENS = OUT_DIR / "escolhas_conjunto_sensibilidade_vaga_imediata.parquet"
OUT_CONJUNTO_ANTIGO = OUT_DIR / "escolhas_conjunto_celulas.parquet"
TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"

CHAVE = ["co_cnes_7d", "cod_curso"]
CICLOS = (1, 2, 3)
# Codificação oficial do IBGE: 1o dígito do código do município = grande região.
REGIAO_POR_DIGITO_IBGE = {"1": "NORTE", "2": "NORDESTE", "3": "SUDESTE", "4": "SUL", "5": "CENTRO OESTE"}
SCRIPT_E3 = ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py"
CICLOS_PRESENCA = (1, 2)  # F2 só para ciclos 1 e 2 (protocolo §3 e §5; ciclo 3 congelado)
POR_HAB = 10_000

DATA_EXECUCAO = "2026-10-18"


# --------------------------------------------------------------------------
# Utilitários
# --------------------------------------------------------------------------

def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def rel(caminho: Path) -> str:
    return Path(caminho).resolve().relative_to(ROOT).as_posix()


def texto_norm(valor: object) -> str:
    """Maiúsculas, sem acento, só alfanuméricos separados por um espaço."""
    if valor is None or (isinstance(valor, float) and np.isnan(valor)):
        return ""
    s = unicodedata.normalize("NFKD", str(valor))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).upper()
    return " ".join(re.findall(r"[A-Z0-9]+", s))


def chave_cnes(valor: object) -> str | None:
    """CNES com 7 dígitos; inteiros do Excel perdem zeros à esquerda."""
    if valor is None or isinstance(valor, bool):
        return None
    if isinstance(valor, float):
        if np.isnan(valor) or not valor.is_integer():
            return None
        valor = int(valor)
    digitos = "".join(ch for ch in str(valor) if ch.isdigit())
    if not digitos or len(digitos) > 7:
        return None
    return digitos.rjust(7, "0")


def chave_curso(valor: object) -> int | None:
    """Código do curso: número inicial do rótulo ("01 - ...", "01. ...")."""
    if valor is None:
        return None
    m = re.match(r"\s*(\d+)\s*[.\-–]", str(valor))
    if not m:
        return None
    codigo = int(m.group(1))
    return codigo if 1 <= codigo <= 24 else None


def chave_ibge(valor: object) -> str | None:
    """Seis dígitos do código IBGE (aceita 6 ou 7 dígitos, inteiro ou texto)."""
    if valor is None:
        return None
    if isinstance(valor, float):
        if np.isnan(valor) or not valor.is_integer():
            return None
        valor = int(valor)
    digitos = "".join(ch for ch in str(valor) if ch.isdigit())
    if len(digitos) == 7:
        digitos = digitos[:6]
    return digitos if len(digitos) == 6 else None


def numero(valor: object) -> float:
    if valor is None or isinstance(valor, bool):
        return float("nan")
    if isinstance(valor, (int, float)):
        return float(valor)
    try:
        return float(str(valor).strip().replace(",", "."))
    except ValueError:
        return float("nan")


def opcao(valor: object) -> int | None:
    """Ordem de prioridade: '1ª OPÇÃO', '2A OPCAO', 1, 2."""
    m = re.match(r"\s*([12])", str(valor if valor is not None else ""))
    return int(m.group(1)) if m else None


def ler_aba(caminho: Path, aba: str | int = 0) -> tuple[list[str], list[str], list[tuple]]:
    """Devolve (cabeçalho normalizado, linha acima do cabeçalho, linhas de dados).

    O cabeçalho é a primeira linha, entre as 20 primeiras, que tem uma coluna
    "CNES" e uma coluna "CURSO" ou "APRIMORAMENTO FINAL". As colunas são
    localizadas pelo nome normalizado, nunca pela posição.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
    try:
        ws = wb[aba] if isinstance(aba, str) else wb.worksheets[aba]
        linhas = [tuple(r) for r in ws.iter_rows(values_only=True)]
    finally:
        wb.close()
    for i, linha in enumerate(linhas[:20]):
        cab = [texto_norm(c) for c in linha]
        if "CNES" in cab and ("CURSO" in cab or "APRIMORAMENTO FINAL" in cab):
            acima = [texto_norm(c) for c in linhas[i - 1]] if i > 0 else [""] * len(cab)
            dados = [r for r in linhas[i + 1:] if any(v is not None and str(v).strip() for v in r)]
            return cab, acima, dados
    raise ValueError(f"cabeçalho não localizado em {rel(caminho)} / {aba}")


def coluna(cab: list[str], *nomes: str, prefixo: bool = False) -> int:
    for nome in nomes:
        for i, c in enumerate(cab):
            if c == nome or (prefixo and c.startswith(nome)):
                return i
    raise KeyError(f"nenhuma das colunas {nomes} no cabeçalho {cab}")


def valor(linha: tuple, i: int) -> object:
    return linha[i] if i < len(linha) else None


# --------------------------------------------------------------------------
# Leitura: quadros de vagas
# --------------------------------------------------------------------------

def ler_quadro(caminho: Path, aba: str | int = 0) -> pd.DataFrame:
    """Células CNES × curso de um quadro de vagas, com vagas imediatas e de reserva.

    As duas colunas TOTAL são identificadas pela linha acima do cabeçalho
    ("VAGAS IMEDIATAS" e "CADASTRO RESERVA"). Quadro só de reserva tem uma.
    """
    cab, acima, linhas = ler_aba(caminho, aba)
    i_cnes, i_curso = coluna(cab, "CNES"), coluna(cab, "CURSO")
    i_ibge = coluna(cab, "IBGE")
    i_faixa = coluna(cab, "FAIXA DE ATRACAO")
    totais = [i for i, c in enumerate(cab) if c == "TOTAL"]
    i_imed = i_cr = None
    for i in totais:
        rotulo = acima[i] if i < len(acima) else ""
        if "IMEDIATA" in rotulo:
            i_imed = i
        elif "RESERVA" in rotulo:
            i_cr = i
    por_posicao = False
    sem_rotulo = all(not (acima[i] if i < len(acima) else "") for i in totais)
    if i_imed is None and i_cr is None and len(totais) == 2 and sem_rotulo:
        # Quadro sem linha de rótulos acima do cabeçalho (versão original do
        # ciclo 2): leiaute TOTAL, AC, ER, PCD (imediatas) e TOTAL, AC, ER, PCD
        # (reserva), o mesmo dos quadros rotulados. Uso só diagnóstico.
        i_imed, i_cr = totais
        por_posicao = True
    if i_cr is None:
        raise KeyError(f"coluna TOTAL de cadastro reserva não localizada em {rel(caminho)}")
    try:
        i_sit = coluna(cab, "SITUACAO DAS VAGAS")
    except KeyError:
        i_sit = None
    try:
        i_reg = coluna(cab, "REGIAO")
    except KeyError:
        i_reg = None
    registros, sem_chave = [], 0
    for r in linhas:
        cnes, curso = chave_cnes(valor(r, i_cnes)), chave_curso(valor(r, i_curso))
        if cnes is None or curso is None:
            sem_chave += 1
            continue
        registros.append(
            {
                "co_cnes_7d": cnes,
                "cod_curso": curso,
                "co_ibge": chave_ibge(valor(r, i_ibge)),
                "faixa_anunciada": texto_norm(valor(r, i_faixa)),
                "vagas_imediatas": numero(valor(r, i_imed)) if i_imed is not None else float("nan"),
                "vagas_cr": numero(valor(r, i_cr)),
                "situacao_vagas": texto_norm(valor(r, i_sit)) if i_sit is not None else "",
                "regiao": texto_norm(valor(r, i_reg)) if i_reg is not None else "",
            }
        )
    q = pd.DataFrame(registros)
    q.attrs["linhas_sem_chave"] = sem_chave
    q.attrs["totais_identificados_por_posicao"] = por_posicao
    if q.duplicated(CHAVE).any():
        raise AssertionError(f"quadro {rel(caminho)} com chave CNES–curso duplicada")
    if q["co_ibge"].isna().any():
        raise AssertionError(f"quadro {rel(caminho)} com IBGE inválido")
    if (q.groupby("co_ibge")["faixa_anunciada"].nunique() != 1).any():
        raise AssertionError(f"quadro {rel(caminho)}: município com mais de uma faixa impressa")
    out = q.sort_values(CHAVE).reset_index(drop=True)
    out.attrs = {"linhas_sem_chave": sem_chave, "totais_identificados_por_posicao": por_posicao}
    return out


# --------------------------------------------------------------------------
# Leitura: candidaturas, alocações e ativos
# --------------------------------------------------------------------------

def _alocado_confirmado_c1(status: str) -> bool:
    return status.startswith("LOCAL DE ATUACAO CONFIRMADO")


def _alocado_situacao(status: str) -> bool:
    return status.startswith("ALOCADO")


def _sub_judice(status: str) -> bool:
    return status == "SUB JUDICE"


def _atendido_remanescente(status: str) -> bool:
    return status in ("ATENDIDO", "ALOCADO")


ESPEC_CANDIDATURAS: dict[str, dict[str, Any]] = {
    "c1_ch1": {
        "caminho": CAND_C1, "aba": 0, "status": ("ALOCACAO",), "pontuacao": ("PONTUACAO NO BAREMA GERAL",),
        "alocado": _alocado_confirmado_c1, "regra_alocado": "ALOCAÇÃO começa com 'LOCAL DE ATUAÇÃO CONFIRMADO'",
        "classificacao": ("RESULTADO",),
        "regra_classificado": "RESULTADO começa com 'CLASSIFICAÇÃO' (ampla concorrência ou cota)",
    },
    "c2_ch1": {
        "caminho": CAND_C2, "aba": "Classificados", "status": ("SITUACAO",), "pontuacao": ("PONTUACAO FINAL",),
        "alocado": _alocado_situacao, "regra_alocado": "SITUAÇÃO começa com 'ALOCADO' (AC, ER, PCD)",
    },
    "c2_ch1_preliminar": {
        "caminho": CAND_C2_PRELIMINAR, "aba": "Classificados", "status": ("SITUACAO",),
        "pontuacao": ("PONTUACAO NO BAREMA GERAL",), "alocado": _alocado_situacao,
        "regra_alocado": "diagnóstico de escala da pontuação; não entra em outcome",
    },
    "c2_ch1_remanescentes": {
        "caminho": CAND_C2_REMANESC, "aba": 0, "status": ("SITUACAO",), "pontuacao": ("PONTUACAO FINAL",),
        "alocado": _atendido_remanescente, "regra_alocado": "SITUAÇÃO = 'ATENDIDO'",
    },
    "c2_ch1_remanescentes_0505": {
        "caminho": CAND_C2_REMANESC_0505, "aba": 0, "status": ("SITUACAO",), "pontuacao": ("PONTUACAO FINAL",),
        "alocado": _atendido_remanescente, "regra_alocado": "SITUAÇÃO = 'ALOCADO'",
    },
    "c2_ch2": {
        "caminho": CAND_C2_CH2, "aba": "Classificados", "status": ("SITUACAO",), "pontuacao": ("PONTUACAO FINAL",),
        "alocado": _alocado_situacao, "regra_alocado": "SITUAÇÃO começa com 'ALOCADO'",
    },
    "c3_ch1": {
        "caminho": CAND_C3, "aba": "Classificados", "status": ("SITUACAO",),
        "pontuacao": ("PONTUACAO NO BAREMA GERAL",), "alocado": _alocado_situacao,
        "regra_alocado": "SITUAÇÃO começa com 'ALOCADO' (AC, ER, PCD); 'SUB JUDICE' só na sensibilidade",
    },
}


def ler_candidaturas(espec: dict[str, Any]) -> pd.DataFrame:
    """Linhas candidato × opção: célula, opção, alocado, pontuação.

    A pessoa é identificada só em memória (nome normalizado + CPF mascarado,
    em hash) para os diagnósticos de duplicidade; nada disso é gravado.
    """
    cab, _, linhas = ler_aba(espec["caminho"], espec["aba"])
    i_cnes, i_curso = coluna(cab, "CNES"), coluna(cab, "CURSO")
    i_status = coluna(cab, *espec["status"])
    i_pont = coluna(cab, *espec["pontuacao"])
    i_ordem = coluna(cab, "ORDEM DE PRIORIDADE ESCOLHIDA")
    i_nome = coluna(cab, "NOME CANDIDATO A", "NOME")
    i_cpf = coluna(cab, "CPF", "CPF MASC", prefixo=True)
    try:
        i_ibge = coluna(cab, "IBGE")
    except KeyError:
        i_ibge = None
    i_class = coluna(cab, *espec["classificacao"]) if "classificacao" in espec else None
    i_mun = coluna(cab, "MUNICIPIO")
    registros, sem_chave = [], 0
    for r in linhas:
        cnes, curso = chave_cnes(valor(r, i_cnes)), chave_curso(valor(r, i_curso))
        if cnes is None or curso is None:
            sem_chave += 1
            continue
        status = texto_norm(valor(r, i_status))
        bruto_pont = valor(r, i_pont)
        pont = numero(bruto_pont)
        pessoa = hashlib.sha256(
            (texto_norm(valor(r, i_nome)) + "|" + str(valor(r, i_cpf) or "").strip()).encode("utf-8")
        ).hexdigest()
        registros.append(
            {
                "co_cnes_7d": cnes,
                "cod_curso": curso,
                "co_ibge_arquivo": chave_ibge(valor(r, i_ibge)) if i_ibge is not None else None,
                "opcao": opcao(valor(r, i_ordem)),
                "status": status,
                "alocado": bool(espec["alocado"](status)),
                "sub_judice": _sub_judice(status),
                "pontuacao": pont,
                "sem_pre_requisito": bool(np.isnan(pont) and "PRE REQUISITO" in texto_norm(bruto_pont)),
                # Ciclo 1: coluna RESULTADO. Ciclos 2-3: a aba 'Classificados' só tem
                # classificados (desclassificados ficam em outra aba, sem célula).
                "classificado": (texto_norm(valor(r, i_class)).startswith("CLASSIFICACAO")
                                 if i_class is not None else True),
                "_municipio_nome": texto_norm(valor(r, i_mun)),
                "_pessoa": pessoa,
            }
        )
    df = pd.DataFrame(registros)
    df.attrs["linhas_sem_chave"] = sem_chave
    return df


def ler_ativos(zip_path: Path = ATIVOS_ZIP) -> pd.DataFrame:
    """Relação nominal de ativos do PMM-E: município, célula e ciclo (só essas colunas).

    `co_ibge` e `ciclo` seguem a leitura do E3 (`07_estimar_E3_rdd_completa.py`):
    CSV ';' latin1, seis primeiros dígitos do IBGE, ciclo inteiro. Ciclo não
    reconhecido falha fechado.
    """
    with zipfile.ZipFile(zip_path) as z:
        nomes = [n for n in z.namelist() if n.lower().endswith(".csv")]
        if len(nomes) != 1:
            raise ValueError(f"esperado um CSV no zip, encontrados {len(nomes)}")
        bruto = z.read(nomes[0])
    df = pd.read_csv(io.BytesIO(bruto), sep=";", dtype=str, encoding="latin1",
                     usecols=["co_ibge", "co_cnes", "curso", "ciclo", "dt_referencia"])
    df["co_ibge"] = df["co_ibge"].astype(str).str.split(".").str[0].str.replace(r"\D", "", regex=True).str[:6]
    ciclo = df["ciclo"].astype(str).str.strip().str.extract(r"^(?:ciclo\s*)?0*(\d{1,2})(?:[.,]0+)?$", expand=False)
    if ciclo.isna().any():
        raise ValueError(f"{int(ciclo.isna().sum())} registros com ciclo não reconhecido")
    df["ciclo_k"] = ciclo.astype(int)
    df["co_cnes_7d"] = df["co_cnes"].map(chave_cnes)
    df["cod_curso"] = df["curso"].map(chave_curso)
    if (df["co_ibge"].str.len() != 6).any():
        raise ValueError("co_ibge inválido na relação nominal")
    return df[["co_ibge", "co_cnes_7d", "cod_curso", "ciclo_k", "dt_referencia"]]


def ler_pmmb(zip_path: Path = PPF_ZIP) -> pd.DataFrame:
    """PMMB consolidado: vagas ativas e vagas ocupadas por município (nível MUNICIPAL)."""
    with zipfile.ZipFile(zip_path) as z:
        bruto = z.read(z.namelist()[0])
    df = pd.read_csv(io.BytesIO(bruto), sep=";", dtype=str, encoding="latin1")
    df = df[df["nivel"] == "MUNICIPAL"].copy()
    cols = ["total_vagas_ativas", "total_ocupadas", "em_processo_ocupacao", "total_desocupadas"]
    for c in cols:
        df[c] = pd.to_numeric(df[c], errors="raise")
    df["co_ibge"] = df["co_ibge"].map(chave_ibge)
    if df["co_ibge"].isna().any() or df["co_ibge"].duplicated().any():
        raise AssertionError("PMMB: co_ibge inválido ou duplicado no nível MUNICIPAL")
    identidade = df["total_vagas_ativas"] == df["total_ocupadas"] + df["em_processo_ocupacao"] + df["total_desocupadas"]
    df.attrs["identidade_vagas"] = float(identidade.mean())
    df.attrs["dt_referencia"] = sorted(df["dt_referencia"].dropna().unique().tolist())
    return df[["co_ibge"] + cols]


def ler_cardapio(caminho: Path = CARDAPIO_C3) -> pd.DataFrame:
    cab, _, linhas = ler_aba(caminho)
    i_cnes, i_curso = coluna(cab, "CNES"), coluna(cab, "APRIMORAMENTO FINAL")
    i_ibge, i_vagas = coluna(cab, "IBGE"), coluna(cab, "VAGAS")
    reg = [
        {"co_cnes_7d": chave_cnes(valor(r, i_cnes)), "cod_curso": chave_curso(valor(r, i_curso)),
         "co_ibge": chave_ibge(valor(r, i_ibge)), "vagas_cardapio": numero(valor(r, i_vagas))}
        for r in linhas
    ]
    df = pd.DataFrame(reg)
    if df[["co_cnes_7d", "cod_curso", "co_ibge"]].isna().any().any() or df.duplicated(CHAVE).any():
        raise AssertionError("cardápio do ciclo 3 com chave inválida ou duplicada")
    return df


def ler_adesao(caminho: Path = ADESAO_C3) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Resultado final da adesão de gestores (aba principal).

    A aba 'Adesão_CNES gestão dupla' repete linhas da aba principal (mesma
    chave, mesmos números); é só conferida, nunca somada.
    """
    cab, _, linhas = ler_aba(caminho, "RESULTADO FINAL")
    ic = {n: coluna(cab, n) for n in ("CNES", "APRIMORAMENTO FINAL", "IBGE", "PRIORIZADAS", "VAGAS IMEDIATAS",
                                      "CADASTRO DE RESERVA", "NAO PRIORIZADAS")}
    df = pd.DataFrame(
        [
            {"co_cnes_7d": chave_cnes(valor(r, ic["CNES"])), "cod_curso": chave_curso(valor(r, ic["APRIMORAMENTO FINAL"])),
             "co_ibge": chave_ibge(valor(r, ic["IBGE"])), "priorizadas": numero(valor(r, ic["PRIORIZADAS"])),
             "priorizadas_imediatas": numero(valor(r, ic["VAGAS IMEDIATAS"])),
             "priorizadas_cr": numero(valor(r, ic["CADASTRO DE RESERVA"])),
             "nao_priorizadas": numero(valor(r, ic["NAO PRIORIZADAS"]))}
            for r in linhas
        ]
    )
    if df[["co_cnes_7d", "cod_curso", "co_ibge"]].isna().any().any() or df.duplicated(CHAVE).any():
        raise AssertionError("adesão do ciclo 3 com chave inválida ou duplicada")
    if df[["priorizadas", "priorizadas_imediatas", "priorizadas_cr", "nao_priorizadas"]].isna().any().any():
        raise AssertionError("adesão do ciclo 3 com contagem ausente")
    cab_d, _, linhas_d = ler_aba(caminho, "Adesão_CNES gestão dupla")
    i_c, i_a, i_p = coluna(cab_d, "CNES"), coluna(cab_d, "APRIMORAMENTO FINAL"), coluna(cab_d, "PRIORIZADAS")
    dupla = pd.DataFrame([{"co_cnes_7d": chave_cnes(valor(r, i_c)), "cod_curso": chave_curso(valor(r, i_a)),
                           "priorizadas_dupla": numero(valor(r, i_p))} for r in linhas_d])
    m = dupla.merge(df, on=CHAVE, how="left")
    diag = {
        "linhas_aba_principal": int(len(df)),
        "linhas_aba_gestao_dupla": int(len(dupla)),
        "linhas_gestao_dupla_presentes_na_principal": int(m["priorizadas"].notna().sum()),
        "linhas_gestao_dupla_com_mesmas_priorizadas": int((m["priorizadas"] == m["priorizadas_dupla"]).sum()),
        "identidade_priorizadas_igual_imediatas_mais_cr": float(
            (df["priorizadas"] == df["priorizadas_imediatas"] + df["priorizadas_cr"]).mean()
        ),
    }
    return df, diag


# --------------------------------------------------------------------------
# Ciclo 1: fonte canônica de Y1 e Y2 (definição do E3/E4)
# --------------------------------------------------------------------------

def carregar_canonica_c1() -> pd.DataFrame:
    """Y1 e Y2 por célula como em `08a_reconstruir_proporcao_preenchida.py`.

    Quadro de tratamento (população primária do A4) unido 1:1 às linhas da chamada 1 da
    matriz do funil do A1; Y2 soma a homologação nova da chamada 2.
    """
    quadro = pd.read_parquet(QUADRO_CANONICO_C1)
    funil = pd.read_parquet(MATRIZ_FUNIL)
    f1 = funil.loc[funil["chamada"] == 1, CHAVE + ["outcome_alguma_confirmacao_ou_homologacao",
                                                   "n_confirmacoes_ch1", "n_homologacoes_ch1"]]
    pop = quadro[CHAVE + ["co_ibge_6d"]].merge(f1, on=CHAVE, how="left", validate="one_to_one")
    if pop["outcome_alguma_confirmacao_ou_homologacao"].isna().any():
        raise AssertionError("célula do quadro sem outcome na matriz canônica")
    f2 = funil.loc[funil["chamada"] == 2].groupby(CHAVE, as_index=False)["n_homologacoes_novas_ch2"].sum()
    pop = pop.merge(f2, on=CHAVE, how="left", validate="one_to_one")
    pop["n_homologacoes_novas_ch2"] = pop["n_homologacoes_novas_ch2"].fillna(0).astype(int)
    pop["cod_curso"] = pop["cod_curso"].astype(int)
    pop["y1"] = pop["outcome_alguma_confirmacao_ou_homologacao"].astype(int)
    pop["y2"] = ((pop["y1"] == 1) | (pop["n_homologacoes_novas_ch2"] > 0)).astype(int)
    return pop[CHAVE + ["co_ibge_6d", "n_confirmacoes_ch1", "n_homologacoes_ch1", "n_homologacoes_novas_ch2", "y1", "y2"]]


# --------------------------------------------------------------------------
# Construção (funções puras, testadas com dados sintéticos)
# --------------------------------------------------------------------------

def casar_com_quadro(quadro: pd.DataFrame, linhas: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Separa as linhas cuja célula CNES × curso está no quadro e conta as demais."""
    chaves = set(zip(quadro["co_cnes_7d"], quadro["cod_curso"]))
    dentro = np.array([k in chaves for k in zip(linhas["co_cnes_7d"], linhas["cod_curso"])], dtype=bool)
    cnes_quadro = set(quadro["co_cnes_7d"])
    fora = linhas.loc[~dentro]
    diag = {
        "linhas": int(len(linhas)),
        "linhas_casadas": int(dentro.sum()),
        "taxa_casamento": float(dentro.mean()) if len(linhas) else float("nan"),
        "linhas_fora_do_quadro": int((~dentro).sum()),
        "linhas_fora_com_cnes_no_quadro_e_curso_diferente": int(fora["co_cnes_7d"].isin(cnes_quadro).sum()),
        "celulas_distintas_casadas": int(len(set(zip(linhas.loc[dentro, "co_cnes_7d"], linhas.loc[dentro, "cod_curso"])))),
    }
    if "co_ibge_arquivo" in linhas and linhas["co_ibge_arquivo"].notna().any():
        m = linhas.loc[dentro, CHAVE + ["co_ibge_arquivo"]].merge(quadro[CHAVE + ["co_ibge"]], on=CHAVE)
        m = m[m["co_ibge_arquivo"].notna()]
        diag["linhas_casadas_com_ibge_do_arquivo_igual_ao_do_quadro"] = int((m["co_ibge_arquivo"] == m["co_ibge"]).sum())
        diag["linhas_casadas_com_ibge_no_arquivo"] = int(len(m))
    return linhas.loc[dentro].copy(), diag


def _contar(idx: pd.MultiIndex, df: pd.DataFrame | None, mascara: pd.Series | None = None) -> np.ndarray:
    if df is None or df.empty:
        return np.zeros(len(idx), dtype=int)
    d = df if mascara is None else df.loc[mascara]
    return d.groupby(CHAVE).size().reindex(idx, fill_value=0).to_numpy().astype(int)


def _soma_pontuacao(idx: pd.MultiIndex, df: pd.DataFrame, mascara: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    d = df.loc[mascara & df["pontuacao"].notna()]
    g = d.groupby(CHAVE)["pontuacao"]
    soma = g.sum().reindex(idx, fill_value=0.0).to_numpy().astype(float)
    n = g.size().reindex(idx, fill_value=0).to_numpy().astype(int)
    return soma, n


def outcomes_celula(
    quadro: pd.DataFrame,
    cand: pd.DataFrame,
    ciclo: int,
    canonica: pd.DataFrame | None = None,
    alocacao_ch2: pd.DataFrame | None = None,
    alocacoes_extra: dict[str, pd.DataFrame] | None = None,
    ativos: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Outcomes por célula do quadro da 1a chamada do ciclo.

    `cand`, `alocacao_ch2` e `alocacoes_extra` já vêm restritos às células do
    quadro. `canonica` (só ciclo 1) traz Y1 e Y2 do E3/E4. `ativos` são os
    ativos do ciclo, com célula.
    """
    cel = quadro.copy().sort_values(CHAVE).reset_index(drop=True)
    idx = pd.MultiIndex.from_frame(cel[CHAVE])
    cel.insert(0, "ciclo", ciclo)
    cel["com_vagas_imediatas"] = (cel["vagas_imediatas"].fillna(0) > 0).astype(int)

    cel["n_cand_1a_opcao"] = _contar(idx, cand, cand["opcao"] == 1)
    cel["n_cand_2a_opcao"] = _contar(idx, cand, cand["opcao"] == 2)
    cel["n_cand_1a_opcao_com_pre_requisito"] = _contar(idx, cand, (cand["opcao"] == 1) & ~cand["sem_pre_requisito"])
    cel["n_candidaturas"] = _contar(idx, cand)
    cel["f1_1_cand_1a_opcao"] = cel["n_cand_1a_opcao"].astype(float)
    cel["f1_2_tem_candidato"] = (cel["n_candidaturas"] > 0).astype(int)
    cel["n_alocados_ch1"] = _contar(idx, cand, cand["alocado"])

    if canonica is not None:
        c = canonica.set_index(CHAVE).reindex(idx)
        if c["y1"].isna().any():
            raise AssertionError("célula do quadro do ciclo 1 sem Y1 canônico")
        cel["n_confirmacoes_ch1"] = c["n_confirmacoes_ch1"].to_numpy().astype(int)
        cel["n_homologacoes_ch1"] = c["n_homologacoes_ch1"].to_numpy().astype(int)
        cel["n_homologacoes_novas_ch2"] = c["n_homologacoes_novas_ch2"].to_numpy().astype(int)
        cel["f1_3_preenchida_ch1"] = c["y1"].to_numpy().astype(float)
        cel["f1_4_preenchida_ate_ch2"] = c["y2"].to_numpy().astype(float)
    else:
        cel["f1_3_preenchida_ch1"] = (cel["n_alocados_ch1"] > 0).astype(float)
        if alocacao_ch2 is not None:
            cel["n_alocados_ch2"] = _contar(idx, alocacao_ch2, alocacao_ch2["alocado"])
            cel["f1_4_preenchida_ate_ch2"] = (
                (cel["f1_3_preenchida_ch1"] > 0) | (cel["n_alocados_ch2"] > 0)
            ).astype(float)
        else:
            cel["f1_4_preenchida_ate_ch2"] = np.nan

    for nome, df in (alocacoes_extra or {}).items():
        mascara = df["sub_judice"] if nome == "sub_judice" else df["alocado"]
        cel[f"n_{nome}"] = _contar(idx, df, mascara)
        cel[f"f1_3s_preenchida_ch1_com_{nome}"] = (
            (cel["f1_3_preenchida_ch1"] > 0) | (cel[f"n_{nome}"] > 0)
        ).astype(float)

    if ativos is not None:
        cel["f2_1_ativos_na_celula"] = _contar(idx, ativos).astype(float)
    else:
        cel["f2_1_ativos_na_celula"] = np.nan

    soma, n = _soma_pontuacao(idx, cand, cand["alocado"])
    cel["soma_pontuacao_alocados"], cel["n_alocados_com_pontuacao"] = soma, n
    cel["f4_1_pontuacao_media_alocados"] = np.where(n > 0, soma / np.maximum(n, 1), np.nan)
    soma, n = _soma_pontuacao(idx, cand, cand["opcao"] == 1)
    cel["soma_pontuacao_cand_1a_opcao"], cel["n_cand_1a_opcao_com_pontuacao"] = soma, n
    cel["f4_2_pontuacao_media_cand_1a_opcao"] = np.where(n > 0, soma / np.maximum(n, 1), np.nan)
    return cel


def outcomes_municipio(cel: pd.DataFrame, ativos_ciclo: pd.DataFrame | None) -> pd.DataFrame:
    """Agrega as células por município; F2 conta todos os ativos do ciclo no município."""
    soma = lambda s: s.sum(min_count=1)  # noqa: E731 - NaN se todas as células são NaN
    g = cel.groupby("co_ibge", sort=True)
    mun = g.agg(
        ciclo=("ciclo", "first"),
        faixa_anunciada=("faixa_anunciada", "first"),
        n_celulas=("cod_curso", "size"),
        n_celulas_com_imediatas=("com_vagas_imediatas", "sum"),
        vagas_imediatas=("vagas_imediatas", soma),
        vagas_cr=("vagas_cr", soma),
        n_cand_1a_opcao=("n_cand_1a_opcao", "sum"),
        n_cand_1a_opcao_com_pre_requisito=("n_cand_1a_opcao_com_pre_requisito", "sum"),
        n_candidaturas=("n_candidaturas", "sum"),
        n_celulas_com_candidato=("f1_2_tem_candidato", "sum"),
        n_alocados_ch1=("n_alocados_ch1", "sum"),
        n_celulas_preenchidas_ch1=("f1_3_preenchida_ch1", "sum"),
        n_celulas_preenchidas_ate_ch2=("f1_4_preenchida_ate_ch2", soma),
        n_ativos_em_celula_do_quadro=("f2_1_ativos_na_celula", soma),
        soma_pontuacao_alocados=("soma_pontuacao_alocados", "sum"),
        n_alocados_com_pontuacao=("n_alocados_com_pontuacao", "sum"),
        soma_pontuacao_cand_1a_opcao=("soma_pontuacao_cand_1a_opcao", "sum"),
        n_cand_1a_opcao_com_pontuacao=("n_cand_1a_opcao_com_pontuacao", "sum"),
        n_celulas_imediatas_preenchidas_ch1=(
            "f1_3_preenchida_ch1", lambda s: float((s * cel.loc[s.index, "com_vagas_imediatas"]).sum())
        ),
    ).reset_index()
    extras = [c for c in cel.columns if c.startswith("f1_3s_")]
    for c in extras:
        mun["n_celulas_" + c[len("f1_3s_"):]] = g[c].sum().to_numpy()

    n = mun["n_celulas"].astype(float)
    mun["f1_1_cand_1a_opcao_por_celula"] = mun["n_cand_1a_opcao"] / n
    mun["f1_1s_cand_1a_opcao_com_pre_requisito_por_celula"] = mun["n_cand_1a_opcao_com_pre_requisito"] / n
    mun["f1_2_fracao_celulas_com_candidato"] = mun["n_celulas_com_candidato"] / n
    mun["f1_3_fracao_celulas_preenchidas_ch1"] = mun["n_celulas_preenchidas_ch1"] / n
    mun["f1_3s_fracao_celulas_imediatas_preenchidas_ch1"] = np.where(
        mun["n_celulas_com_imediatas"] > 0,
        mun["n_celulas_imediatas_preenchidas_ch1"] / mun["n_celulas_com_imediatas"].clip(lower=1),
        np.nan,
    )
    for c in extras:
        nome = c[len("f1_3s_preenchida_ch1_com_"):]
        mun[f"f1_3s_fracao_celulas_preenchidas_ch1_com_{nome}"] = mun["n_celulas_" + c[len("f1_3s_"):]] / n
    mun["f1_4_fracao_celulas_preenchidas_ate_ch2"] = mun["n_celulas_preenchidas_ate_ch2"] / n

    if ativos_ciclo is not None:
        cont = ativos_ciclo.groupby("co_ibge").size()
        mun["n_ativos_ciclo"] = mun["co_ibge"].map(cont).fillna(0).astype(float)
        mun["f2_1_ativos_por_celula"] = mun["n_ativos_ciclo"] / n
        mun["f2_3_d_k_algum_ativo_do_ciclo"] = (mun["n_ativos_ciclo"] > 0).astype(float)
    else:
        mun["n_ativos_ciclo"] = np.nan
        mun["f2_1_ativos_por_celula"] = np.nan
        mun["f2_3_d_k_algum_ativo_do_ciclo"] = np.nan

    mun["f4_1_pontuacao_media_alocados"] = np.where(
        mun["n_alocados_com_pontuacao"] > 0,
        mun["soma_pontuacao_alocados"] / mun["n_alocados_com_pontuacao"].clip(lower=1), np.nan)
    mun["f4_2_pontuacao_media_cand_1a_opcao"] = np.where(
        mun["n_cand_1a_opcao_com_pontuacao"] > 0,
        mun["soma_pontuacao_cand_1a_opcao"] / mun["n_cand_1a_opcao_com_pontuacao"].clip(lower=1), np.nan)
    return mun


def outcomes_g3(cardapio: pd.DataFrame, adesao: pd.DataFrame, populacao: pd.Series) -> tuple[pd.DataFrame, dict]:
    """F0.3 por município do cardápio. Município do cardápio sem linha de adesão não aderiu."""
    card = cardapio.groupby("co_ibge").agg(n_celulas_cardapio=("cod_curso", "size"),
                                           vagas_cardapio=("vagas_cardapio", "sum"))
    g3 = set(card.index)
    ad = adesao[adesao["co_ibge"].isin(g3)].copy()
    ad["pedidas"] = ad["priorizadas"] + ad["nao_priorizadas"]
    chaves_card = set(zip(cardapio["co_cnes_7d"], cardapio["cod_curso"]))
    ad["celula_no_cardapio"] = [k in chaves_card for k in zip(ad["co_cnes_7d"], ad["cod_curso"])]
    soma = ad.groupby("co_ibge").agg(
        n_linhas_adesao=("cod_curso", "size"),
        vagas_pedidas=("pedidas", "sum"),
        vagas_priorizadas=("priorizadas", "sum"),
        vagas_priorizadas_imediatas=("priorizadas_imediatas", "sum"),
        vagas_priorizadas_cr=("priorizadas_cr", "sum"),
        vagas_nao_priorizadas=("nao_priorizadas", "sum"),
    )
    out = card.join(soma, how="left")
    # Observado: o município consta (1) ou não consta (0) do resultado final da adesão.
    # Não consta não é "não pediu": nenhum documento diz que o resultado lista todas as
    # propostas enviadas. Pedidos e frações só existem para quem consta; os demais ficam NaN.
    out["f0_3a_consta_do_resultado_final_adesao"] = out["n_linhas_adesao"].notna().astype(int)
    out["n_linhas_adesao"] = out["n_linhas_adesao"].fillna(0).astype(int)  # linhas no arquivo: contagem observada
    out["f0_3_vagas_pedidas"] = out["vagas_pedidas"]
    out["f0_3_fracao_priorizada"] = np.where(
        out["vagas_pedidas"] > 0, out["vagas_priorizadas"] / out["vagas_pedidas"].clip(lower=1), np.nan)
    out["f0_3_vagas_imediatas_priorizadas"] = out["vagas_priorizadas_imediatas"]
    out = out.reset_index()
    out["populacao_2022"] = out["co_ibge"].map(populacao)
    out["f0_3s_vagas_pedidas_por_10k"] = out["vagas_pedidas"] / out["populacao_2022"] * POR_HAB
    fora = adesao[~adesao["co_ibge"].isin(g3)]
    diag = {
        "municipios_cardapio": int(len(card)),
        "municipios_com_adesao_no_arquivo": int(adesao["co_ibge"].nunique()),
        "municipios_com_adesao_fora_do_cardapio": int(fora["co_ibge"].nunique()),
        "linhas_adesao_de_municipios_fora_do_cardapio": int(len(fora)),
        "linhas_adesao_em_municipios_g3_com_celula_fora_do_cardapio": int((~ad["celula_no_cardapio"]).sum()),
        "regra": "linhas de adesão de municípios fora do cardápio não entram em G3; linhas de municípios de G3 "
                 "com célula fora do cardápio entram (o pedido é do município)",
    }
    return out, diag


def por_10k(contagem: pd.Series, populacao: pd.Series) -> pd.Series:
    return contagem.astype(float) / populacao.astype(float) * POR_HAB


NATUREZA = "EMPIRICO"


def _nan_admitido(df: pd.DataFrame, condicao: Any) -> pd.Series:
    """Onde o NaN é admitido: None = qualquer linha; set = ciclos; (coluna, valor) = df[coluna] == valor."""
    if condicao is None:
        return pd.Series(True, index=df.index)
    if isinstance(condicao, set):
        return df["ciclo"].isin(condicao)
    coluna_cond, valor_cond = condicao
    return df[coluna_cond] == valor_cond


def anotar_ausencias(df: pd.DataFrame, motivos: dict[str, tuple[str, Any]]) -> pd.Series:
    """Coluna `motivos_ausencia`: objeto JSON {coluna: motivo} das colunas NaN da linha ("{}" se nenhuma).

    JSON evita separador ambíguo: o motivo pode conter qualquer caractere.
    `motivos` mapeia coluna -> (motivo, onde o NaN é admitido; ver
    `_nan_admitido`). Falha fechada se alguma coluna tem NaN sem motivo
    registrado ou NaN fora de onde o motivo se aplica: nenhum valor ausente fica
    sem explicação e nenhum é preenchido.
    """
    sem_motivo = [c for c in df.columns if df[c].isna().any() and c not in motivos]
    if sem_motivo:
        raise AssertionError(f"colunas com NaN sem motivo registrado: {sem_motivo}")
    por_linha: list[dict[str, str]] = [{} for _ in range(len(df))]
    for c, (motivo, condicao) in motivos.items():
        if c not in df.columns:
            continue
        nulo = df[c].isna()
        if (nulo & ~_nan_admitido(df, condicao)).any():
            raise AssertionError(f"{c}: NaN fora de onde se admite '{motivo}' ({condicao})")
        for i in np.flatnonzero(nulo.to_numpy()):
            por_linha[i][c] = motivo
    return pd.Series([json.dumps(d, ensure_ascii=False, sort_keys=True) for d in por_linha], index=df.index)


_SO_C3 = "F2 não construído para o ciclo 3 (protocolo §3 e §5; ciclo 3 congelado)"
MOTIVOS_V: dict[str, tuple[str, set[int] | None]] = {
    "ivs_2010_oficial": ("município criado depois de 2010, sem IVS 2010 oficial", None),
    "n_confirmacoes_ch1": ("coluna só do ciclo 1 (fonte canônica A1)", {2, 3}),
    "n_homologacoes_ch1": ("coluna só do ciclo 1 (fonte canônica A1)", {2, 3}),
    "n_homologacoes_novas_ch2": ("coluna só do ciclo 1 (fonte canônica A1)", {2, 3}),
    "n_alocados_ch2": ("coluna só do ciclo 2 (resultado final da 2a chamada)", {1, 3}),
    "f1_4_preenchida_ate_ch2": ("F1.4 não definido para V3 (protocolo: V1 e V2)", {3}),
    "n_celulas_preenchidas_ate_ch2": ("F1.4 não definido para V3 (protocolo: V1 e V2)", {3}),
    "f1_4_fracao_celulas_preenchidas_ate_ch2": ("F1.4 não definido para V3 (protocolo: V1 e V2)", {3}),
    "n_remanescentes": ("sensibilidade definida só no ciclo 2", {1, 3}),
    "f1_3s_preenchida_ch1_com_remanescentes": ("sensibilidade definida só no ciclo 2", {1, 3}),
    "n_celulas_preenchida_ch1_com_remanescentes": ("sensibilidade definida só no ciclo 2", {1, 3}),
    "f1_3s_fracao_celulas_preenchidas_ch1_com_remanescentes": ("sensibilidade definida só no ciclo 2", {1, 3}),
    "n_sub_judice": ("sensibilidade definida só no ciclo 3", {1, 2}),
    "f1_3s_preenchida_ch1_com_sub_judice": ("sensibilidade definida só no ciclo 3", {1, 2}),
    "n_celulas_preenchida_ch1_com_sub_judice": ("sensibilidade definida só no ciclo 3", {1, 2}),
    "f1_3s_fracao_celulas_preenchidas_ch1_com_sub_judice": ("sensibilidade definida só no ciclo 3", {1, 2}),
    "f2_1_ativos_na_celula": (_SO_C3, {3}),
    "n_ativos_em_celula_do_quadro": (_SO_C3, {3}),
    "n_ativos_ciclo": (_SO_C3, {3}),
    "f2_1_ativos_por_celula": (_SO_C3, {3}),
    "f2_3_d_k_algum_ativo_do_ciclo": (_SO_C3, {3}),
    "f4_1_pontuacao_media_alocados": ("nenhum alocado com pontuação numérica: média condicional indefinida", None),
    "f4_2_pontuacao_media_cand_1a_opcao": ("nenhum candidato de 1a opção com pontuação numérica: média indefinida", None),
    "f1_3s_fracao_celulas_imediatas_preenchidas_ch1": ("município sem célula com vaga imediata", None),
}
_NAO_CONSTA = ("não consta do resultado final de adesão", ("f0_3a_consta_do_resultado_final_adesao", 0))
MOTIVOS_G3: dict[str, tuple[str, Any]] = {
    "ivs_2010_oficial": ("município criado depois de 2010, sem IVS 2010 oficial", None),
    **{c: _NAO_CONSTA for c in ("vagas_pedidas", "vagas_priorizadas", "vagas_priorizadas_imediatas",
                                "vagas_priorizadas_cr", "vagas_nao_priorizadas", "f0_3_vagas_pedidas",
                                "f0_3_fracao_priorizada", "f0_3_vagas_imediatas_priorizadas",
                                "f0_3s_vagas_pedidas_por_10k")},
}
MOTIVOS_U: dict[str, tuple[str, set[int] | None]] = {
    "pmmb_vagas_ativas": ("município sem linha no PMMB consolidado (nível MUNICIPAL)", None),
    "pmmb_medicos_ativos": ("município sem linha no PMMB consolidado (nível MUNICIPAL)", None),
    "f0_4_pmmb_vagas_por_10k": ("município sem linha no PMMB consolidado (nível MUNICIPAL)", None),
    "f0_4_pmmb_medicos_por_10k": ("município sem linha no PMMB consolidado (nível MUNICIPAL)", None),
}


# --------------------------------------------------------------------------
# E9 (adendo §12): escolhas dos candidatos e conjunto de escolha
# --------------------------------------------------------------------------

def tabela_escolhas(cand: pd.DataFrame, quadro: pd.DataFrame, ciclo: int) -> pd.DataFrame:
    """Uma linha por candidato × opção ranqueada no resultado da 1a chamada.

    `id_candidato` é pseudônimo determinístico do ciclo (ordem do hash de nome
    normalizado + CPF mascarado, calculado só em memória); nome e CPF não são
    gravados. Município e faixa vêm do quadro pela célula; linha cuja célula não
    está no quadro fica com município e faixa NaN e motivo registrado.
    """
    pessoas = sorted(cand["_pessoa"].unique())
    pid = {h: f"c{ciclo}_{i + 1:05d}" for i, h in enumerate(pessoas)}
    esc = cand.assign(ciclo=ciclo, id_candidato=cand["_pessoa"].map(pid))
    q = quadro[CHAVE + ["co_ibge", "faixa_anunciada", "vagas_imediatas"]]
    esc = esc.merge(q, on=CHAVE, how="left", validate="many_to_one")
    esc["celula_no_quadro"] = esc["co_ibge"].notna().astype(int)
    esc["celula_com_vaga_imediata"] = np.where(
        esc["celula_no_quadro"] == 1, (esc["vagas_imediatas"].fillna(0) > 0).astype(float), np.nan)
    esc["classificado"] = esc["classificado"].astype(int)
    esc["alocado"] = esc["alocado"].astype(int)
    esc["sem_pre_requisito"] = esc["sem_pre_requisito"].astype(int)
    esc = esc.rename(columns={"opcao": "opcao_rank", "status": "situacao_publicada"})
    # O conjunto de escolha de cada linha é o do curso da própria opção (a 2a opção pode
    # ser de outro curso que a 1a).
    esc["id_conjunto_escolha"] = [f"c{ciclo}_curso{int(c):02d}" for c in esc["cod_curso"]]
    curso1 = esc[esc["opcao_rank"] == 1].groupby("id_candidato")["cod_curso"].first()
    curso2 = esc[esc["opcao_rank"] == 2].groupby("id_candidato")["cod_curso"].first()
    esc["curso_da_1a_opcao"] = esc["id_candidato"].map(curso1).astype(float)
    ambos = curso1.index.intersection(curso2.index)
    difere = (curso1.loc[ambos] != curso2.loc[ambos]).astype(float)
    esc["opcoes_em_cursos_diferentes"] = esc["id_candidato"].map(difere)
    cols = ["ciclo", "id_candidato", "cod_curso", "opcao_rank", "id_conjunto_escolha", "co_cnes_7d", "co_ibge",
            "faixa_anunciada", "celula_no_quadro", "celula_com_vaga_imediata", "curso_da_1a_opcao",
            "opcoes_em_cursos_diferentes", "classificado", "alocado", "situacao_publicada", "pontuacao",
            "sem_pre_requisito"]
    return esc[cols].sort_values(["ciclo", "id_candidato", "opcao_rank", "co_cnes_7d", "cod_curso"]).reset_index(drop=True)


def conjunto_escolha(quadro: pd.DataFrame, ciclo: int, populacao: pd.Series, estrato: pd.Series) -> pd.DataFrame:
    """Conjunto de escolha PRINCIPAL do E9 (protocolo §14): todas as células do curso e ciclo
    no quadro da 1a chamada, com ou sem vaga imediata, e os atributos da célula.

    A sensibilidade (§12) é o subconjunto `tem_vaga_imediata == 1`.
    """
    c = quadro[["cod_curso", "co_cnes_7d", "co_ibge", "faixa_anunciada", "vagas_imediatas", "regiao"]].copy()
    c.insert(0, "ciclo", ciclo)
    c.insert(1, "id_conjunto_escolha", [f"c{ciclo}_curso{int(k):02d}" for k in c["cod_curso"]])
    c["tem_vaga_imediata"] = (c["vagas_imediatas"].fillna(0) > 0).astype(int)
    c["log_vagas_imediatas_mais_1"] = np.log(c["vagas_imediatas"] + 1.0)
    c["populacao_2022"] = c["co_ibge"].map(populacao)
    c["macrorregiao"] = c.pop("regiao")
    c["estrato_territorial"] = c["co_ibge"].map(estrato)
    return c.sort_values(["ciclo", "cod_curso", "co_cnes_7d"]).reset_index(drop=True)


MOTIVOS_CONJUNTO: dict[str, tuple[str, Any]] = {
    "estrato_territorial": ("município sem estrato na tipologia territorial (A2)", None),
    "populacao_2022": ("município sem população do Censo 2022", None),
}
MOTIVOS_ESCOLHAS: dict[str, tuple[str, Any]] = {
    "co_ibge": ("célula escolhida fora do quadro da 1a chamada", ("celula_no_quadro", 0)),
    "faixa_anunciada": ("célula escolhida fora do quadro da 1a chamada", ("celula_no_quadro", 0)),
    "celula_com_vaga_imediata": ("célula escolhida fora do quadro da 1a chamada", ("celula_no_quadro", 0)),
    "curso_da_1a_opcao": ("candidato sem linha de 1a opção no arquivo publicado", None),
    "opcoes_em_cursos_diferentes": ("candidato com uma só opção no arquivo publicado", None),
    "pontuacao": ("pontuação não numérica no arquivo publicado (ex.: 'SEM PRÉ-REQUISITO')", None),
    "opcao_rank": ("ordem de prioridade ilegível no arquivo publicado", None),
}


# --------------------------------------------------------------------------
# Proveniência e dicionário
# --------------------------------------------------------------------------

def conferir_contra_e3(municipios: dict[int, pd.DataFrame]) -> dict[str, Any]:
    """Compara V1/V2 e D_k com `carregar_populacoes`, `ler_ativos` e `construir_d_k` do E3."""
    import importlib.util
    import sys

    bytecode = sys.dont_write_bytecode
    spec = importlib.util.spec_from_file_location("e3_rdd_completa", SCRIPT_E3)
    e3 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(e3)
    sys.dont_write_bytecode = bytecode
    pops = e3.carregar_populacoes(ROOT)
    ativos_e3 = e3.ler_ativos(ATIVOS_ZIP)
    out = {}
    for nome, k in (("P1", 1), ("P2", 2)):
        vk = municipios[k].set_index("co_ibge")
        if sorted(vk.index) != sorted(set(pops[nome]["co_ibge"])):
            raise AssertionError(f"V{k} difere da população {nome} do E3")
        d = e3.construir_d_k(pops[nome]["co_ibge"], ativos_e3, k)
        iguais = int((vk.loc[d.index, "f2_3_d_k_algum_ativo_do_ciclo"] == d).sum())
        if iguais != len(d):
            raise AssertionError(f"F2.3 do ciclo {k} não reproduz D_{k} do E3")
        out[f"V{k}_igual_{nome}_e_F2_3_igual_D_{k}"] = True
    return out


def _manifestos() -> dict[str, dict]:
    por_arquivo: dict[str, dict] = {}
    if MANIFESTO_FONTES.exists():
        for f in json.loads(MANIFESTO_FONTES.read_text(encoding="utf-8")).get("fontes", []):
            if f.get("arquivo"):
                por_arquivo.setdefault(f["arquivo"], f)
    for mpath in (MANIFESTO_A07, MANIFESTO_A11):
        if mpath.exists():
            for f in json.loads(mpath.read_text(encoding="utf-8")).get("fontes", []):
                if f.get("arquivo"):
                    por_arquivo[f["arquivo"]] = {**f, "_manifesto": rel(mpath)}
    return por_arquivo


def bloco_entrada(caminho: Path, papel: str, data_referencia: str, cobertura: str, unidade: str,
                  chaves: str, filtros: str, manifestos: dict[str, dict]) -> dict[str, Any]:
    sha = sha256_arquivo(caminho)
    m = manifestos.get(caminho.name, {})
    bloco: dict[str, Any] = {
        "caminho": rel(caminho), "sha256": sha, "bytes": caminho.stat().st_size, "papel": papel,
        "fonte": m.get("fonte") or ("Ministério da Saúde (publicação do PMM-E)" if "raw" in caminho.parts
                                    else "pipeline do repositório"),
        "data_referencia": data_referencia, "cobertura": cobertura, "unidade": unidade,
        "chaves": chaves, "filtros": filtros,
    }
    if m:
        bloco["manifesto"] = {
            "arquivo": m.get("_manifesto", rel(MANIFESTO_FONTES)), "url": m.get("url"),
            "data_extracao": m.get("data_extracao") or m.get("data_captura"),
            "sha256_no_manifesto": m.get("sha256"),
            "sha256_confere": (m.get("sha256") == sha) if m.get("sha256") else None,
        }
    return bloco


def resumo_global(df: pd.DataFrame, colunas: list[str]) -> dict[str, dict]:
    """Distribuição global (nunca por lado de corte, faixa ou IVS)."""
    out = {}
    for c in colunas:
        s = pd.to_numeric(df[c], errors="coerce")
        out[c] = {
            "n": int(s.notna().sum()), "ausentes": int(s.isna().sum()),
            "media": None if s.notna().sum() == 0 else round(float(s.mean()), 6),
            "min": None if s.notna().sum() == 0 else round(float(s.min()), 6),
            "max": None if s.notna().sum() == 0 else round(float(s.max()), 6),
        }
    return out


def gravar_parquet(df: pd.DataFrame, caminho: Path) -> None:
    tmp = caminho.with_name(caminho.name + ".tmp")
    df.to_parquet(tmp, index=False, engine="pyarrow")
    tmp.replace(caminho)


DESCRICOES_V = {
    "ciclo": "ciclo do PMM-E (1, 2 ou 3); a população é V_ciclo",
    "co_ibge": "código IBGE do município (6 dígitos)",
    "co_cnes_7d": "CNES do estabelecimento (7 dígitos)",
    "cod_curso": "código do curso de aprimoramento (número inicial do rótulo)",
    "faixa_anunciada": "faixa de atração impressa no quadro da 1a chamada (atributo; nunca cruzada com outcome)",
    "ivs_2010_oficial": "IVS 2010 oficial do Ipea (a08), só coluna de chave; NaN para município criado depois de 2010",
    "populacao_2022": "população residente do Censo 2022",
    "vagas_imediatas": "vagas imediatas publicadas no quadro da 1a chamada",
    "vagas_cr": "vagas de cadastro reserva publicadas no quadro da 1a chamada",
    "situacao_vagas": "situação da célula no quadro ('COM VAGAS IMEDIATAS' ou 'APENAS CADASTRO DE RESERVA')",
    "regiao": "macrorregião impressa no quadro (conferida com o 1o dígito do IBGE)",
    "com_vagas_imediatas": "1 se a célula tem vaga imediata",
    "n_celulas": "células CNES × curso no quadro da 1a chamada do ciclo",
    "n_celulas_com_imediatas": "células com vaga imediata",
    "n_cand_1a_opcao": "linhas candidato × opção com a célula como 1a opção no resultado da 1a chamada",
    "n_cand_2a_opcao": "idem, 2a opção",
    "n_cand_1a_opcao_com_pre_requisito": "1a opção, excluindo 'SEM PRÉ-REQUISITO' (só existe no ciclo 1)",
    "n_candidaturas": "linhas candidato × opção na célula (qualquer opção)",
    "f1_1_cand_1a_opcao": "F1.1 na célula: candidatos de 1a opção",
    "f1_1_cand_1a_opcao_por_celula": "F1.1: candidatos de 1a opção / células oferecidas",
    "f1_1s_cand_1a_opcao_com_pre_requisito_por_celula": "sensibilidade de F1.1 sem os 'SEM PRÉ-REQUISITO' do ciclo 1",
    "f1_2_tem_candidato": "F1.2 na célula: 1 se há ≥1 candidatura (qualquer opção)",
    "n_celulas_com_candidato": "células com ≥1 candidatura",
    "f1_2_fracao_celulas_com_candidato": "F1.2: fração de células com ≥1 candidatura",
    "n_alocados_ch1": "alocados na 1a chamada (ciclo 1: confirmações na alocação sub judice; ciclos 2-3: SITUAÇÃO ALOCADO)",
    "n_confirmacoes_ch1": "ciclo 1: confirmações de local na alocação sub judice (fonte canônica A1)",
    "n_homologacoes_ch1": "ciclo 1: homologações da lista da 1a chamada (fonte canônica A1)",
    "n_homologacoes_novas_ch2": "ciclo 1: homologações novas da lista da 2a chamada (fonte canônica A1)",
    "f1_3_preenchida_ch1": "F1.3 na célula: ciclo 1 = Y1 do E3/E4; ciclos 2-3 = ≥1 alocado na 1a chamada",
    "n_celulas_preenchidas_ch1": "células preenchidas na 1a chamada",
    "f1_3_fracao_celulas_preenchidas_ch1": "F1.3: fração de células preenchidas na 1a chamada",
    "n_celulas_imediatas_preenchidas_ch1": "células com vaga imediata e preenchidas na 1a chamada",
    "f1_3s_fracao_celulas_imediatas_preenchidas_ch1": "sensibilidade de F1.3 só sobre células com vaga imediata",
    "n_alocados_ch2": "ciclo 2: alocados no resultado final da 2a chamada",
    "f1_4_preenchida_ate_ch2": "F1.4 na célula: ciclo 1 = Y2 do E4; ciclo 2 = F1.3 ou ≥1 alocado na 2a chamada; ciclo 3 NaN",
    "n_celulas_preenchidas_ate_ch2": "células preenchidas até a 2a chamada",
    "f1_4_fracao_celulas_preenchidas_ate_ch2": "F1.4: fração de células preenchidas até a 2a chamada",
    "n_remanescentes": "ciclo 2: atendidos nas duas listas de vagas remanescentes da 1a chamada",
    "f1_3s_preenchida_ch1_com_remanescentes": "sensibilidade de F1.3 (ciclo 2) contando os remanescentes",
    "n_celulas_preenchida_ch1_com_remanescentes": "células preenchidas contando os remanescentes (ciclo 2)",
    "f1_3s_fracao_celulas_preenchidas_ch1_com_remanescentes": "sensibilidade de F1.3 (ciclo 2) com remanescentes",
    "n_sub_judice": "ciclo 3: linhas com SITUAÇÃO 'SUB JUDICE'",
    "f1_3s_preenchida_ch1_com_sub_judice": "sensibilidade de F1.3 (ciclo 3) contando 'SUB JUDICE' como alocado",
    "n_celulas_preenchida_ch1_com_sub_judice": "células preenchidas contando 'SUB JUDICE' (ciclo 3)",
    "f1_3s_fracao_celulas_preenchidas_ch1_com_sub_judice": "sensibilidade de F1.3 (ciclo 3) com 'SUB JUDICE'",
    "f2_1_ativos_na_celula": "ativos do ciclo na célula (relação nominal); ciclo 3 NaN",
    "n_ativos_em_celula_do_quadro": "ativos do ciclo em células do quadro do município; ciclo 3 NaN",
    "n_ativos_ciclo": "ativos do ciclo no município, em qualquer estabelecimento; ciclo 3 NaN",
    "f2_1_ativos_por_celula": "F2.1: ativos do ciclo no município / células oferecidas; ciclo 3 NaN",
    "f2_3_d_k_algum_ativo_do_ciclo": "F2.3: D_k do E3 (≥1 ativo do ciclo no município); ciclo 3 NaN",
    "soma_pontuacao_alocados": "soma da pontuação dos alocados (para médias ponderadas por pessoa)",
    "n_alocados_com_pontuacao": "alocados com pontuação numérica",
    "f4_1_pontuacao_media_alocados": "F4.1: pontuação média dos alocados na 1a chamada (média por pessoa)",
    "soma_pontuacao_cand_1a_opcao": "soma da pontuação dos candidatos de 1a opção",
    "n_cand_1a_opcao_com_pontuacao": "candidatos de 1a opção com pontuação numérica",
    "f4_2_pontuacao_media_cand_1a_opcao": "F4.2: pontuação média dos candidatos de 1a opção (média por pessoa)",
    "tem_ivs_oficial": "1 se o município tem IVS 2010 oficial",
    "motivos_ausencia": "para cada coluna NaN da linha, 'coluna: motivo' (NaN nunca é preenchido)",
    "natureza_dos_dados": "EMPIRICO: construído só de arquivos observados; nada simulado, imputado ou assumido",
}


DESCRICOES_ESCOLHAS = {
    "id_candidato": "pseudônimo determinístico do candidato no ciclo (c<k>_<n>); nome e CPF não são gravados",
    "opcao_rank": "ordem de prioridade publicada (1 = 1a opção, 2 = 2a opção)",
    "celula_no_quadro": "1 se a célula escolhida está no quadro da 1a chamada do ciclo",
    "celula_com_vaga_imediata": "1 se a célula escolhida tem vaga imediata (está no conjunto de sensibilidade do E9)",
    "id_conjunto_escolha": "conjunto de escolha da linha: c<ciclo>_curso<curso> (o curso da própria opção)",
    "curso_da_1a_opcao": "curso da 1a opção do candidato",
    "opcoes_em_cursos_diferentes": "1 se a 1a e a 2a opção do candidato são de cursos diferentes",
    "tem_vaga_imediata": "1 se a célula tem vaga imediata no quadro da 1a chamada",
    "log_vagas_imediatas_mais_1": "log(vagas imediatas + 1)",
    "macrorregiao": "macrorregião impressa no quadro (conferida com o 1o dígito do IBGE)",
    "estrato_territorial": "estrato da tipologia territorial A2 (matriz_tipologia_territorial, coluna estrato)",
    "classificado": "ciclo 1: RESULTADO começa com 'CLASSIFICAÇÃO'; ciclos 2-3: linha da aba 'Classificados' (=1)",
    "alocado": "alocado na 1a chamada (ciclo 1: local confirmado; ciclos 2-3: SITUAÇÃO 'ALOCADO*')",
    "situacao_publicada": "status publicado, normalizado (ALOCAÇÃO no ciclo 1; SITUAÇÃO nos ciclos 2-3)",
    "pontuacao": "pontuação usada na classificação (ciclos 1 e 3: barema geral; ciclo 2: pontuação final)",
    "sem_pre_requisito": "1 se a pontuação publicada é 'SEM PRÉ-REQUISITO' (só ciclo 1)",
}


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def main() -> int:
    if sha256_arquivo(ATIVOS_ZIP) != SHA256_ATIVOS_PROTOCOLO:
        raise AssertionError("relação nominal de ativos não é a versão do protocolo (SHA-256 difere)")
    protocolo = json.loads(PROTOCOLO.read_text(encoding="utf-8"))

    # Chaves municipais: IVS oficial (só chave) e população.
    ivs = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str}, usecols=["co_ibge", "ivs"])
    ivs["co_ibge"] = ivs["co_ibge"].str.zfill(6)
    if ivs["co_ibge"].duplicated().any() or ivs["co_ibge"].str.len().ne(6).any() or ivs["ivs"].isna().any():
        raise AssertionError("base do IVS oficial com código duplicado, inválido ou IVS ausente")
    ivs_map = ivs.set_index("co_ibge")["ivs"]
    pop = pd.read_csv(POPULACAO, dtype={"co_ibge_6d": str})
    pop_map = pop.set_index("co_ibge_6d")["populacao_2022"].astype(float)
    nomes_censo = pop.set_index("co_ibge_6d")["no_municipio_uf"].map(lambda t: texto_norm(str(t).rsplit(" - ", 1)[0]))

    # Quadros.
    quadros = {1: ler_quadro(QUADRO_C1), 2: ler_quadro(QUADRO_C2), 3: ler_quadro(QUADRO_C3)}
    q_c1_ch2 = ler_quadro(QUADRO_C1_CH2_CR, "VAGAS - CADASTRO RESERVA")
    q_c2_ch2 = ler_quadro(QUADRO_C2_CH2)
    # V2 é a união dos quadros da 1a e da 2a chamada (protocolo). As células de V2 são as do
    # quadro da 1a chamada; isso só vale se a 2a chamada não acrescenta célula nem município.
    chaves_c2_ch1 = set(zip(quadros[2]["co_cnes_7d"], quadros[2]["cod_curso"]))
    n_c2_ch2_fora = sum(1 for x in zip(q_c2_ch2["co_cnes_7d"], q_c2_ch2["cod_curso"]) if x not in chaves_c2_ch1)
    n_mun_c2_ch2_fora = len(set(q_c2_ch2["co_ibge"]) - set(quadros[2]["co_ibge"]))
    if n_c2_ch2_fora or n_mun_c2_ch2_fora:
        raise AssertionError("a 2a chamada do ciclo 2 acrescenta células ou municípios ao quadro da 1a: "
                             "V2 teria de ser construído pela união")
    # Macrorregião impressa no quadro confere com o 1o dígito do código IBGE.
    for k in CICLOS:
        reg = quadros[k]["co_ibge"].str[0].map(REGIAO_POR_DIGITO_IBGE)
        if (quadros[k]["regiao"] != reg).any():
            raise AssertionError(f"ciclo {k}: macrorregião do quadro difere do 1o dígito do IBGE")
    versoes_c2 = {nome: ler_quadro(p) for nome, p in QUADROS_C2_VERSOES.items()}

    # Ciclo 1 canônico (E3/E4) e conferência com o quadro bruto.
    canon = carregar_canonica_c1()
    k_raw = set(zip(quadros[1]["co_cnes_7d"], quadros[1]["cod_curso"]))
    k_can = set(zip(canon["co_cnes_7d"], canon["cod_curso"]))
    if k_raw != k_can:
        raise AssertionError("células do quadro bruto do ciclo 1 diferem da população canônica do A4/E4")
    m = quadros[1].merge(canon[CHAVE + ["co_ibge_6d"]], on=CHAVE)
    if (m["co_ibge"] != m["co_ibge_6d"]).any():
        raise AssertionError("IBGE do quadro bruto do ciclo 1 difere da fonte canônica")

    # Candidaturas e casamento com o quadro.
    cand_bruto = {nome: ler_candidaturas(esp) for nome, esp in ESPEC_CANDIDATURAS.items()}
    alvo = {"c1_ch1": 1, "c2_ch1": 2, "c2_ch1_preliminar": 2, "c2_ch1_remanescentes": 2,
            "c2_ch1_remanescentes_0505": 2, "c2_ch2": 2, "c3_ch1": 3}
    cand, casamento = {}, {}
    for nome, df in cand_bruto.items():
        casado, diag = casar_com_quadro(quadros[alvo[nome]], df)
        diag["linhas_sem_chave_no_arquivo"] = int(df.attrs.get("linhas_sem_chave", 0))
        diag["pessoas_distintas"] = int(df["_pessoa"].nunique())
        diag["linhas_pessoa_celula_duplicadas"] = int(df.duplicated(["_pessoa"] + CHAVE).sum())
        diag["linhas_por_opcao"] = {str(k): int(v) for k, v in sorted(Counter(df["opcao"].fillna(0).astype(int)).items())}
        diag["pessoas_sem_linha_de_1a_opcao"] = int(
            df.groupby("_pessoa")["opcao"].apply(lambda s: (s == 1).sum() == 0).sum())
        diag["situacoes"] = {k: int(v) for k, v in sorted(Counter(df["status"].str[:60]).items())}
        diag["linhas_alocadas"] = int(df["alocado"].sum())
        diag["linhas_sem_pontuacao_numerica"] = int(df["pontuacao"].isna().sum())
        diag["linhas_sem_pre_requisito"] = int(df["sem_pre_requisito"].sum())
        if "linhas_casadas_com_ibge_no_arquivo" in diag:
            # IBGE do arquivo diferente do IBGE do quadro: qual dos dois bate com o nome do município
            # escrito no próprio arquivo (nome do Censo 2022)?
            x = casado.merge(quadros[alvo[nome]][CHAVE + ["co_ibge"]], on=CHAVE)
            x = x[x["co_ibge_arquivo"].notna() & (x["co_ibge_arquivo"] != x["co_ibge"])]
            diag["linhas_ibge_divergente_nome_bate_com_ibge_do_arquivo"] = int(
                (x["co_ibge_arquivo"].map(nomes_censo) == x["_municipio_nome"]).sum())
            diag["linhas_ibge_divergente_nome_bate_com_ibge_do_quadro"] = int(
                (x["co_ibge"].map(nomes_censo) == x["_municipio_nome"]).sum())
        casamento[nome] = diag
        cand[nome] = casado.drop(columns=["_pessoa", "_municipio_nome"])
    # Ciclo 2: alocados da 2a chamada casados contra o quadro da 2a chamada (diagnóstico).
    _, casamento["c2_ch2_contra_quadro_ch2"] = casar_com_quadro(q_c2_ch2, cand_bruto["c2_ch2"])
    for nome in ("c2_ch1", "c2_ch1_remanescentes", "c2_ch2"):
        casamento[nome]["linhas_alocadas_em_celula_so_cadastro_reserva"] = int(
            cand[nome].merge(quadros[2][CHAVE + ["vagas_imediatas"]], on=CHAVE)
            .query("vagas_imediatas == 0")["alocado"].sum())
    casamento["c3_ch1"]["linhas_alocadas_em_celula_so_cadastro_reserva"] = int(
        cand["c3_ch1"].merge(quadros[3][CHAVE + ["vagas_imediatas"]], on=CHAVE)
        .query("vagas_imediatas == 0")["alocado"].sum())

    # Escala da pontuação do ciclo 2 (diagnóstico do F4, sem outcome por lado).
    pb = cand_bruto["c2_ch1"].merge(
        cand_bruto["c2_ch1_preliminar"][["_pessoa"] + CHAVE + ["pontuacao"]],
        on=["_pessoa"] + CHAVE, suffixes=("_final", "_preliminar"))
    escala_c2 = {
        "linhas_pareadas_final_preliminar": int(len(pb)),
        "pontuacao_final_igual_barema_preliminar": int((pb["pontuacao_final"] == pb["pontuacao_preliminar"]).sum()),
        "valores_barema_preliminar": sorted(int(v) for v in cand_bruto["c2_ch1_preliminar"]["pontuacao"].dropna().unique()),
        "valores_pontuacao_final": sorted(int(v) for v in cand_bruto["c2_ch1"]["pontuacao"].dropna().unique()),
    }
    ch2 = pd.read_excel(CAND_C2_CH2, sheet_name="Classificados")
    ch2.columns = [texto_norm(c) for c in ch2.columns]
    escala_c2["ch2_linhas_final_igual_barema_mais_tempo"] = int(
        (ch2["PONTUACAO FINAL"] == ch2["PONTUACAO BAREMA"] + ch2["PONTUACAO TEMPO"]).sum())
    escala_c2["ch2_linhas"] = int(len(ch2))

    # Ativos.
    ativos = ler_ativos()
    ativos_k = {k: ativos[ativos["ciclo_k"] == k] for k in CICLOS_PRESENCA}
    casamento_ativos = {}
    for k in CICLOS_PRESENCA:
        a = ativos_k[k]
        chaves_q = set(zip(quadros[k]["co_cnes_7d"], quadros[k]["cod_curso"]))
        casamento_ativos[f"ciclo_{k}"] = {
            "ativos": int(len(a)),
            "em_municipio_de_V": int(a["co_ibge"].isin(set(quadros[k]["co_ibge"])).sum()),
            "em_celula_do_quadro_ch1": int(sum(1 for x in zip(a["co_cnes_7d"], a["cod_curso"]) if x in chaves_q)),
            "municipios_com_ativo": int(a["co_ibge"].nunique()),
        }
    k1 = ativos_k[1]
    chaves_c1_ch1_ch2 = set(zip(quadros[1]["co_cnes_7d"], quadros[1]["cod_curso"])) | set(
        zip(q_c1_ch2["co_cnes_7d"], q_c1_ch2["cod_curso"]))
    casamento_ativos["ciclo_1"]["em_celula_do_quadro_ch1_ou_ch2"] = int(
        sum(1 for x in zip(k1["co_cnes_7d"], k1["cod_curso"]) if x in chaves_c1_ch1_ch2))
    casamento_ativos["ciclo_3"] = {"ativos": int((ativos["ciclo_k"] == 3).sum()),
                                   "uso": "não usado: F2 do ciclo 3 fora do protocolo (ciclo 3 congelado)"}

    # Células e municípios de V_k.
    celulas = {
        1: outcomes_celula(quadros[1], cand["c1_ch1"], 1, canonica=canon,
                           ativos=ativos_k[1].dropna(subset=CHAVE)),
        2: outcomes_celula(quadros[2], cand["c2_ch1"], 2, alocacao_ch2=cand["c2_ch2"],
                           alocacoes_extra={"remanescentes": pd.concat(
                               [cand["c2_ch1_remanescentes"], cand["c2_ch1_remanescentes_0505"]], ignore_index=True)},
                           ativos=ativos_k[2].dropna(subset=CHAVE)),
        3: outcomes_celula(quadros[3], cand["c3_ch1"], 3, alocacoes_extra={"sub_judice": cand["c3_ch1"]}),
    }
    municipios = {k: outcomes_municipio(celulas[k], ativos_k.get(k)) for k in CICLOS}

    # F2.3 e as populações V1/V2 têm de reproduzir o E3 (funções do próprio E3; falha fechada).
    conferencia_e3 = conferir_contra_e3(municipios)

    # Ciclo 1: F1.3 e F1.4 têm de reproduzir o E4 (falha fechada).
    e4 = pd.read_csv(E4_MUNICIPIO, dtype={"co_ibge": str})
    m1 = municipios[1].merge(e4, on="co_ibge", how="outer", indicator=True, suffixes=("", "_e4"))
    if not ((m1["_merge"] == "both").all()
            and (m1["n_celulas"] == m1["n_celulas_e4"]).all()
            and (m1["n_celulas_preenchidas_ch1"] == m1["n_celulas_y1"]).all()
            and (m1["n_celulas_preenchidas_ate_ch2"] == m1["n_celulas_y2"]).all()):
        raise AssertionError("F1.3/F1.4 do ciclo 1 não reproduzem o E4_proporcao_municipio.csv")

    # Empilhamento V.
    colunas_cel = None
    partes_cel, partes_mun = [], []
    for k in CICLOS:
        c = celulas[k].copy()
        c["ivs_2010_oficial"] = c["co_ibge"].map(ivs_map)
        partes_cel.append(c)
        mm = municipios[k].copy()
        mm["ivs_2010_oficial"] = mm["co_ibge"].map(ivs_map)
        mm["tem_ivs_oficial"] = mm["ivs_2010_oficial"].notna().astype(int)
        mm["populacao_2022"] = mm["co_ibge"].map(pop_map)
        partes_mun.append(mm)
    v_cel = pd.concat(partes_cel, ignore_index=True, sort=False)
    v_mun = pd.concat(partes_mun, ignore_index=True, sort=False)
    primeiras = ["ciclo", "co_ibge", "co_cnes_7d", "cod_curso", "faixa_anunciada", "ivs_2010_oficial"]
    v_cel = v_cel[primeiras + [c for c in v_cel.columns if c not in primeiras]]
    v_cel = v_cel.sort_values(["ciclo", "co_ibge"] + CHAVE).reset_index(drop=True)
    primeiras_m = ["ciclo", "co_ibge", "faixa_anunciada", "ivs_2010_oficial", "tem_ivs_oficial", "populacao_2022"]
    v_mun = v_mun[primeiras_m + [c for c in v_mun.columns if c not in primeiras_m]]
    v_mun = v_mun.sort_values(["ciclo", "co_ibge"]).reset_index(drop=True)
    colunas_cel = list(v_cel.columns)

    # U.
    u = ivs.rename(columns={"ivs": "ivs_2010_oficial"})[["co_ibge", "ivs_2010_oficial"]].sort_values("co_ibge")
    u = u.reset_index(drop=True)
    u["populacao_2022"] = u["co_ibge"].map(pop_map)
    if u["populacao_2022"].isna().any():
        raise AssertionError("município de U sem população do Censo 2022")
    for k in CICLOS:
        q = quadros[k]
        cont = q.groupby("co_ibge").agg(n=("cod_curso", "size"), im=("vagas_imediatas", "sum"), cr=("vagas_cr", "sum"))
        mun_k = set(q["co_ibge"])
        if k == 2:
            mun_k |= set(q_c2_ch2["co_ibge"])
        u[f"f0_1_tem_celula_c{k}"] = u["co_ibge"].isin(mun_k).astype(int)
        u[f"n_celulas_c{k}"] = u["co_ibge"].map(cont["n"]).fillna(0).astype(int)
        u[f"vagas_imediatas_c{k}"] = u["co_ibge"].map(cont["im"]).fillna(0.0)
        u[f"vagas_cr_c{k}"] = u["co_ibge"].map(cont["cr"]).fillna(0.0)
        u[f"f0_2_celulas_por_10k_c{k}"] = por_10k(u[f"n_celulas_c{k}"], u["populacao_2022"])
        u[f"f0_2_vagas_imediatas_por_10k_c{k}"] = por_10k(u[f"vagas_imediatas_c{k}"], u["populacao_2022"])
    u["f0_1s_tem_celula_c1_ch1_ou_ch2"] = u["co_ibge"].isin(set(quadros[1]["co_ibge"]) | set(q_c1_ch2["co_ibge"])).astype(int)
    pmmb = ler_pmmb()
    pm = pmmb.set_index("co_ibge")
    u["pmmb_vagas_ativas"] = u["co_ibge"].map(pm["total_vagas_ativas"]).astype(float)
    u["pmmb_medicos_ativos"] = u["co_ibge"].map(pm["total_ocupadas"]).astype(float)
    u["f0_4_pmmb_vagas_por_10k"] = por_10k(u["pmmb_vagas_ativas"], u["populacao_2022"])
    u["f0_4_pmmb_medicos_por_10k"] = por_10k(u["pmmb_medicos_ativos"], u["populacao_2022"])
    for k in CICLOS_PRESENCA:
        cont = ativos_k[k].groupby("co_ibge").size()
        u[f"n_ativos_pmme_c{k}"] = u["co_ibge"].map(cont).fillna(0).astype(int)
        u[f"f2_2_ativos_pmme_por_10k_c{k}"] = por_10k(u[f"n_ativos_pmme_c{k}"], u["populacao_2022"])
    ativos_fora_u = {f"ciclo_{k}": int((~ativos_k[k]["co_ibge"].isin(set(u["co_ibge"]))).sum()) for k in CICLOS_PRESENCA}

    # G3.
    cardapio = ler_cardapio()
    adesao, diag_adesao = ler_adesao()
    g3, diag_g3 = outcomes_g3(cardapio, adesao, pop_map)
    g3["ivs_2010_oficial"] = g3["co_ibge"].map(ivs_map)
    g3["tem_ivs_oficial"] = g3["ivs_2010_oficial"].notna().astype(int)
    primeiras_g = ["co_ibge", "ivs_2010_oficial", "tem_ivs_oficial", "populacao_2022"]
    g3 = g3[primeiras_g + [c for c in g3.columns if c not in primeiras_g]].sort_values("co_ibge").reset_index(drop=True)

    # E9 (adendo §12, conjunto de escolha fixado no §14): escolhas e conjuntos, ciclos 1-3.
    estrato = pd.read_parquet(TIPOLOGIA, columns=["co_ibge_6d", "estrato"]).set_index("co_ibge_6d")["estrato"]
    fontes_escolha = {1: "c1_ch1", 2: "c2_ch1", 3: "c3_ch1"}
    escolhas = pd.concat([tabela_escolhas(cand_bruto[fontes_escolha[k]], quadros[k], k) for k in CICLOS],
                         ignore_index=True)
    conjunto = pd.concat([conjunto_escolha(quadros[k], k, pop_map, estrato) for k in CICLOS], ignore_index=True)
    conjunto_sens = conjunto[conjunto["tem_vaga_imediata"] == 1].reset_index(drop=True)
    escolhas["motivos_ausencia"] = anotar_ausencias(escolhas, MOTIVOS_ESCOLHAS)
    conjunto["motivos_ausencia"] = anotar_ausencias(conjunto, MOTIVOS_CONJUNTO)
    conjunto_sens = conjunto_sens.assign(motivos_ausencia=anotar_ausencias(conjunto_sens, MOTIVOS_CONJUNTO))
    diag_escolhas = {}
    for k in CICLOS:
        e = escolhas[escolhas["ciclo"] == k]
        um = e["opcao_rank"] == 1
        cj = conjunto[conjunto["ciclo"] == k]
        por_cand = e.drop_duplicates("id_candidato")
        diag_escolhas[f"ciclo_{k}"] = {
            "linhas_candidato_opcao": int(len(e)),
            "candidatos": int(e["id_candidato"].nunique()),
            "linhas_com_celula_no_quadro_conjunto_principal": int(e["celula_no_quadro"].sum()),
            "taxa_casamento_celula_quadro": float(e["celula_no_quadro"].mean()) if len(e) else None,
            "linhas_1a_opcao": int(um.sum()),
            "linhas_1a_opcao_no_conjunto_principal": int((um & (e["celula_no_quadro"] == 1)).sum()),
            "linhas_1a_opcao_no_conjunto_sensibilidade_vaga_imediata": int((um & (e["celula_com_vaga_imediata"] == 1)).sum()),
            "linhas_2a_opcao_no_conjunto_principal": int((~um & (e["celula_no_quadro"] == 1)).sum()),
            "linhas_2a_opcao_no_conjunto_sensibilidade_vaga_imediata": int((~um & (e["celula_com_vaga_imediata"] == 1)).sum()),
            "candidatos_com_1a_e_2a_opcao": int(por_cand["opcoes_em_cursos_diferentes"].notna().sum()),
            "candidatos_com_1a_e_2a_opcao_em_cursos_diferentes": int((por_cand["opcoes_em_cursos_diferentes"] == 1).sum()),
            "celulas_no_conjunto_principal": int(len(cj)),
            "celulas_no_conjunto_sensibilidade_vaga_imediata": int(cj["tem_vaga_imediata"].sum()),
            "cursos_no_conjunto_principal": int(cj["cod_curso"].nunique()),
            "cursos_escolhidos_sem_celula_no_conjunto_principal": int(len(set(e["cod_curso"]) - set(cj["cod_curso"]))),
            "cursos_escolhidos_sem_celula_com_vaga_imediata": int(
                len(set(e["cod_curso"]) - set(cj.loc[cj["tem_vaga_imediata"] == 1, "cod_curso"]))),
            "linhas_por_situacao_publicada": {kk: int(v) for kk, v in sorted(Counter(e["situacao_publicada"].str[:60]).items())},
        }

    # Integridade: todo NaN tem motivo registrado (falha fechada); natureza dos dados.
    v_cel["motivos_ausencia"] = anotar_ausencias(v_cel, MOTIVOS_V)
    v_mun["motivos_ausencia"] = anotar_ausencias(v_mun, MOTIVOS_V)
    g3["motivos_ausencia"] = anotar_ausencias(g3, MOTIVOS_G3)
    u["motivos_ausencia"] = anotar_ausencias(u, MOTIVOS_U)
    for df in (u, g3, v_mun, v_cel, escolhas, conjunto, conjunto_sens):
        df["natureza_dos_dados"] = NATUREZA
    colunas_cel = list(v_cel.columns)
    for nome, df, chave in (("U", u, ["co_ibge"]), ("G3", g3, ["co_ibge"]), ("V_municipio", v_mun, ["ciclo", "co_ibge"]),
                            ("V_celula", v_cel, ["ciclo"] + CHAVE),
                            ("escolhas", escolhas, ["ciclo", "id_candidato", "opcao_rank", "co_cnes_7d", "cod_curso"]),
                            ("conjunto", conjunto, ["ciclo"] + CHAVE),
                            ("conjunto_sensibilidade", conjunto_sens, ["ciclo"] + CHAVE)):
        if df.duplicated(chave).any():
            raise AssertionError(f"{nome}: chave {chave} duplicada")

    # Gravação.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gravar_parquet(u, OUT_U)
    gravar_parquet(g3, OUT_G3)
    gravar_parquet(v_mun, OUT_V_MUN)
    gravar_parquet(v_cel, OUT_V_CEL)
    gravar_parquet(escolhas, OUT_ESCOLHAS)
    gravar_parquet(conjunto, OUT_CONJUNTO)
    gravar_parquet(conjunto_sens, OUT_CONJUNTO_SENS)
    if OUT_CONJUNTO_ANTIGO.exists():  # nome anterior (só vagas imediatas), substituído pelo §14
        OUT_CONJUNTO_ANTIGO.unlink()

    # Dicionário.
    manifestos = _manifestos()
    pmmb_ref = ", ".join(pmmb.attrs.get("dt_referencia", []))
    ativos_ref = ", ".join(sorted(ativos["dt_referencia"].dropna().unique()))
    consolidado = pd.read_parquet(QUADRO_CONSOLIDADO, columns=["arquivo_origem", "dt_publicacao"])
    datas_pub = consolidado.groupby("arquivo_origem")["dt_publicacao"].agg(lambda s: ", ".join(sorted(s.unique())))
    a11 = {f["arquivo"]: f for f in json.loads(MANIFESTO_A11.read_text(encoding="utf-8"))["fontes"]}

    def data_pub(caminho: Path) -> str:
        if caminho.name in datas_pub.index:
            return f"publicação {datas_pub[caminho.name]} (quadro_vagas_consolidado, A1)"
        if caminho.name in a11:
            return a11[caminho.name]["data_referencia"] + " (manifesto a11)"
        return "não registrada"

    def cob_q(q: pd.DataFrame) -> str:
        return f"{len(q)} células, {q['co_ibge'].nunique()} municípios"

    def cob_linhas(df: pd.DataFrame, rotulo: str) -> str:
        return f"{len(df)} linhas candidato × opção, {rotulo}"

    entradas = [
        bloco_entrada(PROTOCOLO, "protocolo congelado E6 (somente lido)", protocolo.get("data_congelamento", ""),
                      "-", "documento", "-", "-", manifestos),
        bloco_entrada(IVS_OFICIAL, "IVS 2010 oficial: define U e entra só como coluna de chave",
                      "IVS 2010 (manifesto a08)", f"{len(ivs)} municípios (malha de 2010)", "município", "co_ibge",
                      "colunas co_ibge e ivs apenas", manifestos),
        bloco_entrada(POPULACAO, "população para as taxas por 10 mil habitantes", "Censo 2022",
                      f"{len(pop)} municípios", "município", "co_ibge_6d", "nenhum", manifestos),
        bloco_entrada(QUADRO_CONSOLIDADO, "datas de publicação dos arquivos do PMM-E (só metadado)", "A1",
                      f"{len(consolidado)} linhas", "linha de documento", "arquivo_origem", "colunas arquivo_origem e "
                      "dt_publicacao", manifestos),
        bloco_entrada(QUADRO_C1, "células de V1 (quadro da 1a chamada do ciclo 1)", data_pub(QUADRO_C1),
                      cob_q(quadros[1]), "célula CNES × curso", "CNES, curso", "linhas com CNES e curso válidos", manifestos),
        bloco_entrada(QUADRO_CANONICO_C1, "população canônica do A4 (conferência das células do ciclo 1)",
                      data_pub(QUADRO_C1), f"{len(canon)} células", "célula CNES × curso", "co_cnes_7d, cod_curso",
                      "nenhum", manifestos),
        bloco_entrada(MATRIZ_FUNIL, "fonte canônica de F1.3 (Y1) e F1.4 (Y2) do ciclo 1, como no E3/E4",
                      "data de referência do A1", "ciclo 1, chamadas 1 e 2", "célula × chamada",
                      "co_cnes_7d, cod_curso, chamada",
                      "chamada 1 (Y1); chamada 2, n_homologacoes_novas_ch2 (Y2)", manifestos),
        bloco_entrada(E4_MUNICIPIO, "conferência: F1.3 e F1.4 do ciclo 1 têm de reproduzir Y1 e Y2 do E4",
                      "saída do 08a", f"{len(e4)} municípios", "município", "co_ibge", "nenhum", manifestos),
        bloco_entrada(CAND_C1, "candidaturas e alocação da 1a chamada do ciclo 1 (F1.1, F1.2, F4)",
                      data_pub(CAND_C1) + "; versão sub judice da alocação retificada",
                      cob_linhas(cand_bruto["c1_ch1"], "ciclo 1, chamada 1"), "candidato × opção", "CNES, curso",
                      ESPEC_CANDIDATURAS["c1_ch1"]["regra_alocado"], manifestos),
        bloco_entrada(QUADRO_C1_CH2_CR, "diagnóstico de F0.1 (ciclo 1 com o quadro de reserva da 2a chamada)",
                      data_pub(QUADRO_C1_CH2_CR), cob_q(q_c1_ch2), "célula CNES × curso", "CNES, curso",
                      "aba 'VAGAS - CADASTRO RESERVA'", manifestos),
        bloco_entrada(QUADRO_C2, "células de V2 (quadro da 1a chamada do ciclo 2, versão do E3/P2)",
                      data_pub(QUADRO_C2), cob_q(quadros[2]), "célula CNES × curso", "CNES, curso",
                      "linhas com CNES e curso válidos", manifestos),
        bloco_entrada(QUADRO_C2_CH2, "municípios de V2 (união) e conferência das células da 2a chamada",
                      data_pub(QUADRO_C2_CH2), cob_q(q_c2_ch2), "célula CNES × curso", "CNES, curso", "nenhum", manifestos),
        bloco_entrada(QUADROS_C2_VERSOES["original_2026-02-03"], "diagnóstico da escolha de versão do quadro do ciclo 2",
                      data_pub(QUADROS_C2_VERSOES["original_2026-02-03"]), cob_q(versoes_c2["original_2026-02-03"]),
                      "célula CNES × curso", "CNES, curso",
                      "não entra em outcome; colunas TOTAL identificadas pela posição (arquivo sem linha de rótulos)",
                      manifestos),
        bloco_entrada(QUADROS_C2_VERSOES["retificado_servicos"], "diagnóstico da escolha de versão do quadro do ciclo 2",
                      data_pub(QUADROS_C2_VERSOES["retificado_servicos"]), cob_q(versoes_c2["retificado_servicos"]),
                      "célula CNES × curso", "CNES, curso", "não entra em outcome", manifestos),
        bloco_entrada(CAND_C2, "candidaturas e alocação final da 1a chamada do ciclo 2 (F1.1, F1.2, F1.3, F4)",
                      data_pub(CAND_C2), cob_linhas(cand_bruto["c2_ch1"], "ciclo 2, chamada 1"), "candidato × opção",
                      "CNES, curso (sem IBGE)", ESPEC_CANDIDATURAS["c2_ch1"]["regra_alocado"], manifestos),
        bloco_entrada(CAND_C2_PRELIMINAR, "diagnóstico da escala da pontuação do ciclo 2", data_pub(CAND_C2_PRELIMINAR),
                      cob_linhas(cand_bruto["c2_ch1_preliminar"], "ciclo 2, chamada 1"), "candidato × opção",
                      "CNES, curso", "não entra em outcome", manifestos),
        bloco_entrada(CAND_C2_REMANESC, "sensibilidade de F1.3 do ciclo 2 (vagas remanescentes)", data_pub(CAND_C2_REMANESC),
                      cob_linhas(cand_bruto["c2_ch1_remanescentes"], "ciclo 2, chamada 1"), "candidato × opção",
                      "CNES, curso", ESPEC_CANDIDATURAS["c2_ch1_remanescentes"]["regra_alocado"], manifestos),
        bloco_entrada(CAND_C2_REMANESC_0505, "sensibilidade de F1.3 do ciclo 2 (remanescentes)",
                      data_pub(CAND_C2_REMANESC_0505),
                      cob_linhas(cand_bruto["c2_ch1_remanescentes_0505"], "ciclo 2, chamada 1"), "candidato × opção",
                      "CNES, curso", ESPEC_CANDIDATURAS["c2_ch1_remanescentes_0505"]["regra_alocado"], manifestos),
        bloco_entrada(CAND_C2_CH2, "F1.4 do ciclo 2 (alocados da 2a chamada)", data_pub(CAND_C2_CH2),
                      cob_linhas(cand_bruto["c2_ch2"], "ciclo 2, chamada 2"), "candidato × opção", "CNES, curso",
                      ESPEC_CANDIDATURAS["c2_ch2"]["regra_alocado"], manifestos),
        bloco_entrada(QUADRO_C3, "células de V3 (quadro da 1a chamada do ciclo 3)", data_pub(QUADRO_C3),
                      cob_q(quadros[3]), "célula CNES × curso", "CNES, curso", "linhas com CNES e curso válidos", manifestos),
        bloco_entrada(CAND_C3, "candidaturas e alocação da 1a chamada do ciclo 3 (F1.1–F1.3, F4)",
                      data_pub(CAND_C3) + "; sub judice", cob_linhas(cand_bruto["c3_ch1"], "ciclo 3, chamada 1"),
                      "candidato × opção", "CNES, curso", ESPEC_CANDIDATURAS["c3_ch1"]["regra_alocado"], manifestos),
        bloco_entrada(CARDAPIO_C3, "G3: cardápio de gestores do ciclo 3", data_pub(CARDAPIO_C3),
                      f"{len(cardapio)} células, {cardapio['co_ibge'].nunique()} municípios",
                      "célula CNES × curso", "CNES, aprimoramento", "nenhum", manifestos),
        bloco_entrada(ADESAO_C3, "F0.3: adesão de gestores do ciclo 3", data_pub(ADESAO_C3),
                      f"{len(adesao)} células, {adesao['co_ibge'].nunique()} municípios", "célula CNES × curso",
                      "CNES, aprimoramento", "aba 'RESULTADO FINAL'; aba de gestão dupla só conferida", manifestos),
        bloco_entrada(ATIVOS_ZIP, "F2.1, F2.2 e F2.3: relação nominal de ativos do PMM-E (versão do E3)",
                      f"dt_referencia no arquivo: {ativos_ref}; versão do manifesto a07 (SHA-256 do protocolo E3)",
                      f"{len(ativos)} ativos, ciclos {sorted(ativos['ciclo_k'].unique().tolist())}", "pessoa ativa",
                      "co_ibge, co_cnes, curso, ciclo",
                      "ciclos 1 e 2; só as colunas co_ibge, co_cnes, curso, ciclo, dt_referencia são lidas", manifestos),
        bloco_entrada(TIPOLOGIA, "E9: estrato territorial das células do conjunto de escolha (só a coluna estrato)",
                      "tipologia A2", f"{len(estrato)} municípios", "município", "co_ibge_6d", "coluna estrato apenas",
                      manifestos),
        bloco_entrada(PPF_ZIP, "F0.4: PMMB consolidado (vagas ativas e ocupadas)", f"dt_referencia no arquivo: {pmmb_ref}",
                      f"{len(pmmb)} municípios no nível MUNICIPAL", "município", "co_ibge", "nivel == 'MUNICIPAL'",
                      manifestos),
    ]

    def bloco_saida(caminho: Path, df: pd.DataFrame, chave: list[str], populacao: str, unidade: str) -> dict:
        return {
            "arquivo": rel(caminho), "sha256": sha256_arquivo(caminho), "linhas": int(len(df)),
            "chave": chave, "chave_unica": bool(not df.duplicated(chave).any()),
            "populacao": populacao, "unidade": unidade, "colunas": list(df.columns),
        }

    desc_u = {
        "co_ibge": "código IBGE (6 dígitos)",
        "ivs_2010_oficial": "IVS 2010 oficial do Ipea, só coluna de chave",
        "populacao_2022": "população residente do Censo 2022",
        "f0_1s_tem_celula_c1_ch1_ou_ch2": "diagnóstico: célula no quadro da 1a ou da 2a chamada (reserva) do ciclo 1",
        "pmmb_vagas_ativas": "PMMB: total_vagas_ativas (vagas aderidas, confirmadas e disponíveis)",
        "pmmb_medicos_ativos": "PMMB: total_ocupadas (vagas ocupadas por profissionais em atividade)",
        "f0_4_pmmb_vagas_por_10k": "F0.4: vagas ativas do PMMB por 10 mil habitantes",
        "f0_4_pmmb_medicos_por_10k": "F0.4: médicos ativos do PMMB por 10 mil habitantes",
    }
    for k in CICLOS:
        desc_u[f"f0_1_tem_celula_c{k}"] = (f"F0.1: município tem ≥1 célula no quadro do ciclo {k}"
                                           + (" (1a ou 2a chamada)" if k == 2 else " (1a chamada)"))
        desc_u[f"n_celulas_c{k}"] = f"células no quadro da 1a chamada do ciclo {k} (0 fora do quadro)"
        desc_u[f"vagas_imediatas_c{k}"] = f"vagas imediatas no quadro da 1a chamada do ciclo {k}"
        desc_u[f"vagas_cr_c{k}"] = f"vagas de cadastro reserva no quadro da 1a chamada do ciclo {k}"
        desc_u[f"f0_2_celulas_por_10k_c{k}"] = f"F0.2: células do ciclo {k} por 10 mil habitantes"
        desc_u[f"f0_2_vagas_imediatas_por_10k_c{k}"] = f"F0.2: vagas imediatas do ciclo {k} por 10 mil habitantes"
    for k in CICLOS_PRESENCA:
        desc_u[f"n_ativos_pmme_c{k}"] = f"ativos do PMM-E do ciclo {k} no município (0 fora do quadro)"
        desc_u[f"f2_2_ativos_pmme_por_10k_c{k}"] = f"F2.2: ativos do PMM-E do ciclo {k} por 10 mil habitantes"
    desc_g3 = {
        "co_ibge": "código IBGE (6 dígitos)", "ivs_2010_oficial": "IVS 2010 oficial, só chave",
        "tem_ivs_oficial": "1 se tem IVS 2010 oficial", "populacao_2022": "população do Censo 2022",
        "n_celulas_cardapio": "células CNES × curso do cardápio", "vagas_cardapio": "vagas oferecidas no cardápio",
        "n_linhas_adesao": "linhas do resultado final da adesão", "vagas_pedidas": "priorizadas + não priorizadas",
        "vagas_priorizadas": "PRIORIZADAS (= imediatas + cadastro reserva)",
        "vagas_priorizadas_imediatas": "VAGAS IMEDIATAS priorizadas", "vagas_priorizadas_cr": "CADASTRO DE RESERVA priorizado",
        "vagas_nao_priorizadas": "NÃO PRIORIZADAS",
        "f0_3a_consta_do_resultado_final_adesao": "F0.3a: 1 = consta do resultado final da adesão; 0 = não consta "
                                                  "(não equivale a 'não pediu')",
        "f0_3_vagas_pedidas": "F0.3: vagas pedidas", "f0_3_fracao_priorizada": "F0.3: priorizadas / pedidas (NaN se 0 pedidas)",
        "f0_3_vagas_imediatas_priorizadas": "F0.3: vagas imediatas priorizadas",
        "f0_3s_vagas_pedidas_por_10k": "vagas pedidas por 10 mil habitantes (complementar)",
    }

    col_res_v = [c for c in v_mun.columns if re.match(r"f[124]", c)]
    col_res_u = [c for c in u.columns if re.match(r"f[02]", c)]
    col_res_g = [c for c in g3.columns if c.startswith("f0")]

    versoes = {}
    for nome, q in versoes_c2.items():
        _, dg = casar_com_quadro(q, cand_bruto["c2_ch1"])
        versoes[nome] = {
            "celulas": int(len(q)), "municipios": int(q["co_ibge"].nunique()),
            "vagas_imediatas": float(q["vagas_imediatas"].sum()), "vagas_cr": float(q["vagas_cr"].sum()),
            "linhas_do_resultado_final_casadas": dg["linhas_casadas"],
        }

    n_mun_c1_ch2_novos = len(set(q_c1_ch2["co_ibge"]) - set(quadros[1]["co_ibge"]))
    n_c2_celulas_comuns = len(set.intersection(*[set(zip(q["co_cnes_7d"], q["cod_curso"])) for q in versoes_c2.values()]))
    n_pop_fora_u = len(set(pop["co_ibge_6d"]) - set(u["co_ibge"]))

    dicionario = {
        "natureza_dos_dados": NATUREZA,
        "documento": "Tarefa B do protocolo E6: outcomes F0, F1, F2 e F4 do funil do PMM-E (ciclos 1-3)",
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "protocolo": {"arquivo": rel(PROTOCOLO), "sha256": sha256_arquivo(PROTOCOLO),
                      "texto_canonico": protocolo.get("texto_canonico"),
                      "sha256_texto_canonico_declarado": protocolo.get("sha256_texto_canonico")},
        "cegamento": {
            "regra": "nenhum outcome por lado de corte, por faixa ou contra o IVS; IVS oficial só como coluna de chave",
            "arquivo_proibido_lido": False,
            "resumos": "distribuições globais (n, ausentes, média, mínimo, máximo)",
        },
        "contraste": "nenhum: esta etapa só constrói outcomes; não estima efeito",
        "saidas": {
            "U": bloco_saida(OUT_U, u, ["co_ibge"], "U: municípios com IVS 2010 oficial", "município"),
            "G3": bloco_saida(OUT_G3, g3, ["co_ibge"], "G3: municípios do cardápio de gestores do ciclo 3", "município"),
            "V_municipio": bloco_saida(OUT_V_MUN, v_mun, ["ciclo", "co_ibge"], "V1, V2, V3 empilhados", "município × ciclo"),
            "V_celula": bloco_saida(OUT_V_CEL, v_cel, ["ciclo", "co_cnes_7d", "cod_curso"],
                                    "células do quadro da 1a chamada de cada ciclo", "célula CNES × curso × ciclo"),
            "escolhas_candidatos": bloco_saida(
                OUT_ESCOLHAS, escolhas, ["ciclo", "id_candidato", "opcao_rank", "co_cnes_7d", "cod_curso"],
                "candidatos da 1a chamada de cada ciclo (E9, adendo §12)", "candidato × opção ranqueada"),
            "escolhas_conjunto_principal": bloco_saida(
                OUT_CONJUNTO, conjunto, ["ciclo", "co_cnes_7d", "cod_curso"],
                "E9 principal (§14): todas as células do quadro da 1a chamada, por curso e ciclo, com ou sem "
                "vaga imediata", "célula CNES × curso × ciclo"),
            "escolhas_conjunto_sensibilidade_vaga_imediata": bloco_saida(
                OUT_CONJUNTO_SENS, conjunto_sens, ["ciclo", "co_cnes_7d", "cod_curso"],
                "E9 sensibilidade (§12): só células com vaga imediata", "célula CNES × curso × ciclo"),
        },
        "n_por_populacao": {
            "U": int(len(u)), "G3": int(len(g3)),
            **{f"V{k}": int((v_mun["ciclo"] == k).sum()) for k in CICLOS},
            **{f"celulas_V{k}": int((v_cel["ciclo"] == k).sum()) for k in CICLOS},
            "V3_sem_ivs_oficial": sorted(v_mun.loc[(v_mun["ciclo"] == 3) & (v_mun["tem_ivs_oficial"] == 0), "co_ibge"].tolist()),
            "G3_sem_ivs_oficial": sorted(g3.loc[g3["tem_ivs_oficial"] == 0, "co_ibge"].tolist()),
        },
        # Lista de registros {coluna, descricao}: o nome da coluna não vira chave do JSON.
        "variaveis": {nome: [{"coluna": c, "descricao": d} for c, d in descr.items()] for nome, descr in {
            "U": {c: desc_u.get(c) or DESCRICOES_V.get(c, "") for c in u.columns},
            "G3": {c: desc_g3.get(c) or DESCRICOES_V.get(c, "") for c in g3.columns},
            "V_municipio": {c: DESCRICOES_V.get(c, "") for c in v_mun.columns},
            "V_celula": {c: DESCRICOES_V.get(c, "") for c in colunas_cel},
            "escolhas_candidatos": {c: DESCRICOES_ESCOLHAS.get(c) or DESCRICOES_V.get(c, "") for c in escolhas.columns},
            "escolhas_conjunto_principal": {c: DESCRICOES_ESCOLHAS.get(c) or DESCRICOES_V.get(c, "")
                                            for c in conjunto.columns},
            "escolhas_conjunto_sensibilidade_vaga_imediata": {c: DESCRICOES_ESCOLHAS.get(c) or DESCRICOES_V.get(c, "")
                                                              for c in conjunto_sens.columns},
        }.items()},
        "decisoes_de_construcao": [
            "Célula = CNES (7 dígitos) × código do curso (número inicial do rótulo). Não há identificador "
            "persistente de vaga (auditoria A1/08); por isso todos os outcomes de candidatura e preenchimento são "
            "por célula oferecida, nunca por vaga. Arquivos são casados só pela chave da célula; colunas são "
            "localizadas pelo nome do cabeçalho.",
            "V_k e as células de V_k vêm do quadro da 1a chamada do ciclo k: ciclo 1 = quadro original "
            f"({len(quadros[1])} células, a população do E3/E4); ciclo 2 = retificação de 19/03/2026, a mesma "
            "versão do P2 do E3; ciclo 3 = retificação de 24/07/2026. O protocolo define V2 como a união dos "
            "quadros da 1a e da 2a chamada; o script usa as células da 1a chamada e falha se a 2a chamada "
            f"acrescentar célula ou município (células da 2a fora da 1a: {n_c2_ch2_fora}; municípios: "
            f"{n_mun_c2_ch2_fora}), de modo que a união e o quadro da 1a chamada coincidem.",
            "Ciclo 2: versões do quadro da 1a chamada (células, municípios, vagas imediatas, vagas de reserva): "
            + "; ".join(f"{nome}: {v['celulas']}, {v['municipios']}, {v['vagas_imediatas']:.0f}, {v['vagas_cr']:.0f}"
                        for nome, v in versoes.items())
            + f". Células comuns às três versões: {n_c2_celulas_comuns}. Usa-se a versão de 19/03/2026 (a do E3 "
            "e a vigente na alocação final de 24/03/2026). A escolha só afeta vagas_imediatas, vagas_cr e "
            "com_vagas_imediatas (F0.2 e as sensibilidades por célula imediata).",
            "Denominador de F1.1–F1.4 e F2.1: todas as células do quadro da 1a chamada, inclusive as só de "
            "cadastro reserva, como no E3/E4. A sensibilidade f1_3s_fracao_celulas_imediatas_preenchidas_ch1 "
            "restringe às células com vaga imediata.",
            "F1.1 conta linhas candidato × opção com a célula como 1a opção no resultado da 1a chamada. No "
            "ciclo 1 isso inclui os 'SEM PRÉ-REQUISITO' (não classificados) que o arquivo lista com opção; nos "
            "ciclos 2 e 3 os desclassificados ficam numa aba sem célula e não entram. A sensibilidade "
            "f1_1s_..._com_pre_requisito exclui os 'SEM PRÉ-REQUISITO' do ciclo 1 e é igual ao principal nos "
            "ciclos 2 e 3.",
            "F1.2 conta a célula com ≥1 linha candidato × opção (1a ou 2a opção).",
            "F1.3 do ciclo 1 é o Y1 do E3/E4, lido da fonte canônica do A1 (matriz do funil): confirmação de local "
            "na alocação sub judice ou homologação na lista da 1a chamada. O script falha se não reproduzir "
            "E4_proporcao_municipio.csv. Ciclos 2 e 3: ≥1 linha com SITUAÇÃO 'ALOCADO*' no resultado final da "
            "1a chamada.",
            "Ciclo 2: as duas listas de vagas remanescentes da 1a chamada ('ATENDIDO', "
            f"{len(cand_bruto['c2_ch1_remanescentes'])} linhas; 'ALOCADO' de 05/05/2026, "
            f"{len(cand_bruto['c2_ch1_remanescentes_0505'])} linhas) entram só na sensibilidade "
            "f1_3s_..._com_remanescentes. Ciclo 3: as linhas 'SUB JUDICE' "
            f"({int(cand_bruto['c3_ch1']['sub_judice'].sum())}) entram só em f1_3s_..._com_sub_judice.",
            "F1.4 do ciclo 1 é o Y2 do E4 (Y1 ou homologação nova na 2a chamada). Ciclo 2: F1.3 ou ≥1 alocado no "
            "resultado final da 2a chamada na mesma célula. Ciclo 3: não definido (NaN).",
            "F2 (ativos) só para os ciclos 1 e 2: o protocolo define F2.1 e F2.3 em V1 e V2 e usa do ciclo 3 só "
            "o funil administrativo (§3); o ciclo 3 segue congelado. Ativos = relação nominal do PMM-E, mesma "
            "versão e mesma leitura de co_ibge e ciclo do E3.",
            "F2.1 no município conta todos os ativos do ciclo no município (em qualquer estabelecimento) e divide "
            "pelas células oferecidas; a contagem só em células do quadro fica em n_ativos_em_celula_do_quadro e, "
            "por célula, em f2_1_ativos_na_celula. F2.3 = 1[≥1 ativo do ciclo no município] (D_k do E3).",
            "F2.2 em U: ativos do ciclo k no município por 10 mil habitantes do Censo 2022, com zero onde não há "
            "ativo (inclusive fora do quadro).",
            "F4 usa a pontuação que cada resultado final usa para classificar: ciclo 1 'PONTUAÇÃO NO BAREMA "
            "(GERAL)'; ciclo 2 'PONTUAÇÃO FINAL'; ciclo 3 'PONTUAÇÃO NO BAREMA (GERAL)'. No ciclo 2 a pontuação "
            "final não é o barema do resultado preliminar (ver escala_pontuacao_ciclo2) e, na 2a chamada do "
            "mesmo ciclo, é barema + tempo; a escala dos ciclos não é idêntica e o empilhamento deve usar efeito "
            "fixo de ciclo. 'SEM PRÉ-REQUISITO' (ciclo 1) não tem pontuação e fica fora das médias.",
            "F4.1: média por pessoa da pontuação dos alocados na 1a chamada (ciclo 1: confirmações na alocação "
            "sub judice; homologados sem confirmação não têm pontuação no arquivo). F4.2: média por pessoa dos "
            "candidatos de 1a opção. No município, as médias somam as pessoas de todas as células.",
            "F0.1: ciclo 1 = quadro da 1a chamada (= V1); ciclo 2 = união dos quadros da 1a e 2a chamada (= V2); "
            "ciclo 3 = quadro da 1a chamada (= V3). F0.2 usa células e vagas imediatas do quadro da 1a chamada "
            "de cada ciclo (somar quadros de chamadas diferentes contaria vagas duas vezes, inventário A1). "
            "O diagnóstico f0_1s_tem_celula_c1_ch1_ou_ch2 inclui o quadro de reserva da 2a chamada do ciclo 1, "
            f"que tem {n_mun_c1_ch2_novos} municípios fora do quadro da 1a chamada.",
            "F0.3 (G3 = municípios do cardápio de gestores): F0.3a = f0_3a_consta_do_resultado_final_adesao, "
            "1 se o município consta do resultado final da adesão e 0 se não consta. Não constar NÃO é codificado "
            "como 'não pediu': nenhum documento examinado diz que o resultado final lista todas as propostas "
            "enviadas (ver regra_publicacao_resultado_adesao). Vagas pedidas (priorizadas + não priorizadas), "
            "fração priorizada (priorizadas / pedidas, com priorizadas = imediatas + cadastro reserva, identidade "
            "conferida) e imediatas priorizadas só existem para quem consta; os demais ficam NaN com o motivo "
            "'não consta do resultado final de adesão'. A aba de gestão dupla repete linhas da aba principal e "
            "não é somada.",
            "Zeros e ausentes: zero só onde o arquivo completo observa zero (célula oferecida sem candidatura no "
            "resultado; município fora do quadro; sem ativo na relação nominal nacional). "
            "Valor indefinido ou fora do protocolo fica NaN e a coluna motivos_ausencia diz por quê; o script "
            "falha se algum NaN não tiver motivo registrado. Linhas de candidatura cuja célula não casa com o "
            "quadro não são atribuídas a célula nenhuma e são contadas em casamento_entre_arquivos.",
            "F0.4: PMMB consolidado, nível MUNICIPAL; vagas = total_vagas_ativas; médicos ativos = "
            "total_ocupadas (= soma dos ativos por equipe e por sexo, conferido).",
            "E9 (adendo §12; conjunto fixado no §14): escolhas_candidatos tem uma linha por candidato × opção "
            "ranqueada do resultado da 1a chamada de cada ciclo (ciclo 1: alocação sub judice; ciclo 2: "
            "resultado final de 24/03/2026; ciclo 3: resultado final sub judice), com a célula escolhida e o "
            "município e a faixa impressa vindos do quadro pela célula. Conjunto de escolha PRINCIPAL "
            "(escolhas_conjunto_principal): todas as células do curso e ciclo no quadro da 1a chamada, com ou sem "
            "vaga imediata, com tem_vaga_imediata, log(vagas_imediatas + 1), faixa impressa, co_ibge, população "
            "do Censo 2022, macrorregião (impressa no quadro e conferida com o 1o dígito do IBGE) e estrato "
            "territorial (A2, só a coluna estrato). SENSIBILIDADE (escolhas_conjunto_sensibilidade_vaga_imediata): "
            "só as células com vaga imediata, e só candidatos cuja 1a opção está nelas (celula_com_vaga_imediata "
            "= 1 na linha de 1a opção). O conjunto de cada linha é o do curso da PRÓPRIA opção "
            "(id_conjunto_escolha): a 2a opção pode ser de outro curso que a 1a (contagens em "
            "candidatos_com_1a_e_2a_opcao_em_cursos_diferentes), e então o conjunto do posto 2 é o do curso da "
            "2a opção. O tipo de inscrição (cota) não é lido nem gravado (não é necessário ao E9).",
            f"U = os {len(u)} municípios do IVS 2010 oficial; municípios do Censo 2022 fora de U (criados depois "
            f"de 2010): {n_pop_fora_u}. Municípios de V ou G3 sem IVS 2010 ficam com ivs_2010_oficial NaN e "
            "tem_ivs_oficial = 0 (lista em n_por_populacao).",
        ],
        "casamento_entre_arquivos": {
            "candidaturas_contra_quadro_da_1a_chamada": casamento,
            "versoes_do_quadro_ciclo2_chamada1": versoes,
            "ativos": casamento_ativos,
            "escolhas_E9_celula_escolhida_contra_quadro": diag_escolhas,
            "ativos_fora_de_U": ativos_fora_u,
            "adesao_ciclo3": {**diag_adesao, **diag_g3},
            "pmmb": {"municipios_nivel_municipal": int(len(pmmb)),
                     "identidade_vagas_igual_ocupadas_mais_processo_mais_desocupadas": pmmb.attrs.get("identidade_vagas"),
                     "municipios_de_U_sem_linha_pmmb": int(u["pmmb_vagas_ativas"].isna().sum())},
        },
        "escala_pontuacao_ciclo2": escala_c2,
        "regra_publicacao_resultado_adesao": {
            "pergunta": "o resultado final da adesão de gestores lista todas as propostas enviadas?",
            "resposta": "não há texto que o afirme; F0.3 não codifica 'não consta' como 'não pediu'",
            "texto_examinado": [
                "Edital SGTES/MS nº 2/2025 (adesão de gestores, ciclo 1), itens 2.2.1, 2.3.1, 3.6 e 4.4: a SGTES "
                "publica a lista preliminar e o resultado final 'com base nas informações enviadas' / 'incluídas "
                "no sistema', depois de analisar recursos; nada diz que toda proposta enviada aparece no resultado.",
                "Mesmo edital, item 3.5: a SGTES 'se reserva ao direito de excluir do presente chamamento público o "
                "ente federativo que não atender integralmente aos critérios', isto é, propostas podem não constar.",
                "Ciclo 3 (Edital nº 25/2026): a cópia no repositório "
                "(data/raw/aquisicao/ivs_regra/edital_sgtes_05_2026_adesao_ciclo3.html) é só a página de anexos; "
                "o texto do edital não foi examinado. A cópia da página do Edital 2/2025 no repositório também não "
                "traz os itens acima, que foram lidos num extrato de texto fora do repositório.",
            ],
        },
        "conferencias": {
            "ciclo1_F1_3_e_F1_4_reproduzem_E4": True,
            "ciclo1_celulas_do_quadro_bruto_iguais_a_populacao_canonica": True,
            "relacao_nominal_de_ativos_sha256_do_protocolo": True,
            **conferencia_e3,
            "V2_2a_chamada_nao_acrescenta_celula_nem_municipio": True,
            "macrorregiao_do_quadro_igual_ao_1o_digito_do_ibge": True,
        },
        "ressalvas_dos_arquivos_de_candidatura": [
            "A auditoria do A1 (gate 08) bloqueou 'candidaturas por vaga' porque não há ID persistente de vaga; "
            "aqui a unidade é a célula CNES × curso, que existe em todos os arquivos.",
            "O resultado da 1a chamada lista candidatos classificados e em cadastro reserva por opção; candidatos "
            "desclassificados por pré-requisito (ciclos 2 e 3) ficam numa aba sem célula e não entram em F1.",
            "Algumas pessoas aparecem só com linha de 2a opção (ver pessoas_sem_linha_de_1a_opcao): contam em F1.2, "
            "não em F1.1.",
            "Ciclo 2: o resultado final da 1a chamada não tem IBGE; o município vem do quadro pela célula.",
            "Em todos os arquivos o município vem do quadro pela célula, nunca do IBGE do arquivo de resultado. No "
            "resultado da 2a chamada do ciclo 2, há linhas em que o IBGE impresso difere do IBGE do quadro; nelas o "
            "nome do município impresso no próprio arquivo bate com o IBGE do quadro, não com o do arquivo (ver "
            "linhas_ibge_divergente_nome_bate_com_ibge_do_* em casamento_entre_arquivos).",
            "O ciclo 1 usa a alocação retificada sub judice (versão canônica do A1/E4).",
        ],
        "desvios": [
            {
                "data": DATA_EXECUCAO,
                "item": "resultado final da 1a chamada do ciclo 2",
                "situacao": "ausente do repositório no inventário de 18/10/2026",
                "resolucao": "obtido na página pública do Chamamento SGTES/MS nº 1/2026 e preservado por "
                             "scripts/aquisicao/a11_adquirir_resultado_ciclo2_chamada1.py "
                             "(output/aquisicao/a11_manifesto_ciclo2_chamada1.json)",
            },
            {
                "data": DATA_EXECUCAO,
                "item": "data da relação nominal de ativos",
                "situacao": f"o protocolo chama de 'retrato de 09/10/2026' a versão publicada nessa data; "
                            f"a coluna dt_referencia do arquivo diz {ativos_ref}",
                "resolucao": "mesmo arquivo do E3 (SHA-256 conferido); as duas datas ficam registradas",
            },
            {
                "data": DATA_EXECUCAO,
                "item": "F0.3 (adesão do ciclo 3)",
                "situacao": "a primeira versão codificava como 'não aderiu' (zero pedido) o município do cardápio "
                            "ausente do resultado final, sem documento que dissesse que o resultado lista todos os "
                            "pedidos (auditoria independente de 18/10/2026)",
                "resolucao": "F0.3a = consta (1) / não consta (0) do resultado final; pedidos e fração priorizada "
                             "só para quem consta, NaN com motivo para os demais",
            },
            {
                "data": DATA_EXECUCAO,
                "item": "identificador do candidato na tabela de escolhas do E9",
                "situacao": "o pedido era o CPF mascarado como publicado",
                "resolucao": "gravado pseudônimo determinístico por ciclo (id_candidato), que agrupa as opções da "
                             "mesma pessoa; regra do repositório (08a): nenhum nome, CPF ou assinatura de CPF em output/",
            },
            {
                "data": DATA_EXECUCAO,
                "item": "F2 do ciclo 3",
                "situacao": "a relação nominal tem ativos do ciclo 3",
                "resolucao": "não construído: fora do protocolo (§3 e §5) e ciclo 3 congelado",
            },
        ],
        "resumo_global": {
            "U": resumo_global(u, col_res_u),
            "G3": resumo_global(g3, col_res_g),
            **{f"V{k}": resumo_global(v_mun[v_mun["ciclo"] == k], col_res_v) for k in CICLOS},
        },
        "entradas": entradas,
        "dados_pessoais_gravados": False,
        "linguagem": "construção de outcome descritiva; nenhuma estimativa causal",
    }
    tmp = OUT_DICIONARIO.with_name(OUT_DICIONARIO.name + ".tmp")
    tmp.write_text(json.dumps(dicionario, ensure_ascii=False, indent=2, allow_nan=False, default=_json_default) + "\n",
                   encoding="utf-8")
    tmp.replace(OUT_DICIONARIO)

    print(f"[OK] U {len(u)} | G3 {len(g3)} | " + " | ".join(
        f"V{k} {int((v_mun['ciclo'] == k).sum())} mun / {int((v_cel['ciclo'] == k).sum())} células" for k in CICLOS))
    for nome in ("c1_ch1", "c2_ch1", "c2_ch2", "c3_ch1"):
        d = casamento[nome]
        print(f"[OK] casamento {nome}: {d['linhas_casadas']}/{d['linhas']} linhas")
    print(f"[OK] {rel(OUT_DICIONARIO)}")
    return 0


def _json_default(obj: Any) -> Any:
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return None if np.isnan(obj) else float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    raise TypeError(type(obj))


if __name__ == "__main__":
    raise SystemExit(main())
