"""E4 (adendo): proporção de células preenchidas por município, ciclo 1.

Executa a etapa de outcome do adendo congelado
`output/rdd_bolsa/protocolo_E4_adendo_proporcao.json`:

1. Lê a FONTE CANÔNICA (matriz do funil do A1, filtrada para a população
   primária do A4 como em `scripts/tema_trabalho/05_estimar_atracao.py`) e grava,
   por município, Y1 e Y2 em `output/rdd_bolsa/E4_proporcao_municipio.csv`.
2. Reconstrói Y1 e Y2 célula a célula, de forma independente, a partir das
   planilhas brutas publicadas em `data/raw` (sem importar nem reutilizar o
   código de `scripts/tema_trabalho/02_reconciliar_funil_ciclo1.py`; as colunas
   são localizadas pelo nome do cabeçalho, não pela posição) e compara a
   reconstrução com a fonte canônica em
   `output/rdd_bolsa/E4_validacao_reconstrucao.json`.

Definições (adendo E4 e A4):
- População P1: 1.295 células CNES–curso do quadro original da 1a chamada do
  ciclo 1 (368 municípios).
- Y1 da célula: alguma confirmação de local de atuação (versão sub judice da
  alocação, a canônica) ou alguma homologação na lista da 1a chamada.
- Y2 da célula: Y1 ou alguma homologação NOVA na lista da 2a chamada, isto é,
  de pessoa que não consta da lista de homologados da 1a chamada (pareamento
  por nome normalizado ou pelos dígitos do CPF visíveis nas duas máscaras).

Restrições respeitadas: o outcome NÃO é cruzado com o escore administrativo nem
com o IVS; nenhuma proporção por faixa é calculada aqui (a faixa anunciada é só
um atributo do município carregado da fonte canônica). Nenhum nome, CPF ou
assinatura de CPF é gravado. Os arquivos em `data/` são somente lidos.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import warnings
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import openpyxl
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

ADENDO = ROOT / "output" / "rdd_bolsa" / "protocolo_E4_adendo_proporcao.json"
MATRIZ_FUNIL = ROOT / "output" / "tema_trabalho" / "matriz_funil_ciclo1.parquet"
QUADRO_CANONICO = ROOT / "output" / "aquisicao" / "quadro_vagas_tratamento.parquet"
MANIFESTO_FONTES = ROOT / "output" / "manifesto_fontes_pmme.json"

RAW_VAGAS = ROOT / "data" / "raw" / "aquisicao" / "vagas"
RAW_PMME = ROOT / "data" / "raw" / "pmm_e"
BRUTO_QUADRO = RAW_VAGAS / "2025_ciclo1_chamada1_vagas.xlsx"
BRUTO_ALOC_SUBJUDICE = RAW_VAGAS / "2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx"
BRUTO_ALOC_RETIFICADA = RAW_VAGAS / "2025_ciclo1_chamada1_alocacao_retificada.xlsx"
BRUTO_REALOC = RAW_VAGAS / "2025_ciclo1_chamada1_realocacao_retificado.xlsx"
BRUTO_HOMOLOG_CH1 = RAW_PMME / "2025_ciclo1_chamada1_homologados.xlsx"
BRUTO_HOMOLOG_CH2 = RAW_PMME / "2025_ciclo1_chamada2_homologados.xlsx"
BRUTO_CH2_VAGAS_ALOC = RAW_PMME / "2025_ciclo1_chamada2_vagas_e_alocados.xlsx"
BRUTO_CH2_CLASSIF = RAW_PMME / "2025_ciclo1_chamada2_classificacao_final.xlsx"

OUT_DIR = ROOT / "output" / "rdd_bolsa"
OUT_CSV = OUT_DIR / "E4_proporcao_municipio.csv"
OUT_JSON = OUT_DIR / "E4_validacao_reconstrucao.json"

N_CELULAS_P1 = 1295
N_MUNICIPIOS_P1 = 368
CHAVE = ("co_cnes_7d", "cod_curso")


# --------------------------------------------------------------------------
# Utilitários
# --------------------------------------------------------------------------

def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def rel(caminho: Path) -> str:
    return caminho.relative_to(ROOT).as_posix()


def texto_norm(valor: object) -> str:
    """Maiúsculas, sem acento, só alfanuméricos separados por um espaço."""
    if valor is None:
        return ""
    s = unicodedata.normalize("NFKD", str(valor))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).upper()
    return " ".join(re.findall(r"[A-Z0-9]+", s))


def chave_cnes(valor: object, anomalias: Counter) -> str | None:
    """CNES com 7 dígitos; inteiros perdem zeros à esquerda no Excel."""
    if valor is None:
        return None
    if isinstance(valor, bool):
        anomalias["cnes_tipo_invalido"] += 1
        return None
    if isinstance(valor, float):
        if not valor.is_integer():
            anomalias["cnes_float_nao_inteiro"] += 1
            return None
        valor = int(valor)
    digitos = "".join(ch for ch in str(valor) if ch.isdigit())
    if not digitos:
        return None
    if len(digitos) > 7:
        anomalias["cnes_mais_de_7_digitos"] += 1
        return None
    if len(digitos) < 7:
        anomalias["cnes_completado_com_zeros"] += 1
    return digitos.rjust(7, "0")


def chave_curso(valor: object, anomalias: Counter) -> int | None:
    """Código do curso: número inicial do rótulo ("01 - ...", "01. ...")."""
    if valor is None:
        return None
    m = re.match(r"\s*(\d+)\s*[.\-–]", str(valor))
    if not m:
        anomalias["curso_sem_codigo"] += 1
        return None
    codigo = int(m.group(1))
    if not 1 <= codigo <= 16:
        anomalias["curso_fora_1_16"] += 1
        return None
    return codigo


def chave_ibge(valor: object) -> str | None:
    if valor is None:
        return None
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    digitos = "".join(ch for ch in str(valor) if ch.isdigit())
    if len(digitos) == 7:  # código com dígito verificador
        digitos = digitos[:6]
    return digitos if len(digitos) == 6 else None


def chave_cpf_comum(valor: object) -> str | None:
    """Posições do CPF visíveis nas DUAS listas de homologados.

    Lista Ch1: `999XXX99999` (posições 1-3 e 7-11 visíveis).
    Lista Ch2: `999.XXX.X99-99` (posições 1-3 e 8-11 visíveis).
    A interseção é 1-3 e 8-11. A chave é lida por POSIÇÃO no CPF de 11
    caracteres (com os X), nunca pelos dígitos visíveis, e só é usada entre
    essas duas listas. Nunca é gravada.
    """
    if valor is None:
        return None
    s = re.sub(r"[.\-\s]", "", str(valor)).upper()
    if len(s) != 11:
        return None
    parte = s[0:3] + s[7:11]
    return parte if parte.isdigit() else None


def ler_aba(caminho: Path, aba: str | int = 0) -> tuple[list[str], list[tuple]]:
    """Lê uma aba e devolve (cabeçalho normalizado, linhas de dados).

    O cabeçalho é a primeira linha que contém uma coluna com "CNES" ou, na
    falta, "CPF" junto de "CURSO"/"APRIMORAMENTO".
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wb = openpyxl.load_workbook(caminho, read_only=True, data_only=True)
    try:
        ws = wb[aba] if isinstance(aba, str) else wb.worksheets[aba]
        linhas = [tuple(r) for r in ws.iter_rows(values_only=True)]
    finally:
        wb.close()
    for i, linha in enumerate(linhas[:10]):
        cab = [texto_norm(c) for c in linha]
        tem_curso = any(c == "CURSO" or c == "APRIMORAMENTO" for c in cab)
        tem_id = any("CNES" == c for c in cab) or any(c == "CPF" for c in cab)
        if tem_curso and tem_id:
            dados = [r for r in linhas[i + 1:] if any(v is not None and str(v).strip() for v in r)]
            return cab, dados
    raise ValueError(f"cabeçalho não localizado em {rel(caminho)} / {aba}")


def coluna(cab: list[str], *nomes: str) -> int:
    for nome in nomes:
        if nome in cab:
            return cab.index(nome)
    raise KeyError(f"nenhuma das colunas {nomes} no cabeçalho {cab}")


def eventos_por_celula(registros: Iterable[tuple[str, int]]) -> Counter:
    return Counter(registros)


# --------------------------------------------------------------------------
# Fonte canônica
# --------------------------------------------------------------------------

def carregar_canonica() -> pd.DataFrame:
    """População primária do A4 com Y1 e Y2 da matriz canônica.

    Reproduz o filtro de `05_estimar_atracao.py`: quadro de tratamento (1.295
    células) unido 1:1 às linhas da chamada 1 da matriz do funil. Y2 soma a
    marcação de homologação nova da chamada 2 na mesma chave CNES–curso.
    """
    quadro = pd.read_parquet(QUADRO_CANONICO)
    funil = pd.read_parquet(MATRIZ_FUNIL)
    f1 = funil.loc[
        funil["chamada"] == 1,
        ["co_cnes_7d", "cod_curso", "outcome_alguma_confirmacao_ou_homologacao",
         "n_confirmacoes_ch1", "n_homologacoes_ch1", "in_quadro_ch1_original"],
    ]
    pop = quadro[["co_cnes_7d", "cod_curso", "co_ibge_6d", "faixa_atracao_anunciada"]].merge(
        f1, on=list(CHAVE), how="left", validate="one_to_one"
    )
    if pop["outcome_alguma_confirmacao_ou_homologacao"].isna().any():
        raise AssertionError("célula do quadro sem outcome na matriz canônica")
    f2 = (
        funil.loc[funil["chamada"] == 2]
        .groupby(list(CHAVE), as_index=False)["n_homologacoes_novas_ch2"].sum()
    )
    pop = pop.merge(f2, on=list(CHAVE), how="left", validate="one_to_one")
    pop["n_homologacoes_novas_ch2"] = pop["n_homologacoes_novas_ch2"].fillna(0).astype(int)
    pop["co_ibge_6d"] = pop["co_ibge_6d"].astype(str).str.replace(r"\D", "", regex=True).str.zfill(6)
    pop["cod_curso"] = pop["cod_curso"].astype(int)
    pop["y1"] = pop["outcome_alguma_confirmacao_ou_homologacao"].astype(int)
    pop["y2"] = ((pop["y1"] == 1) | (pop["n_homologacoes_novas_ch2"] > 0)).astype(int)
    if len(pop) != N_CELULAS_P1 or pop["co_ibge_6d"].nunique() != N_MUNICIPIOS_P1:
        raise AssertionError(
            f"população canônica {len(pop)} células / {pop['co_ibge_6d'].nunique()} municípios"
        )
    if pop.duplicated(list(CHAVE)).any():
        raise AssertionError("chave CNES–curso duplicada na população canônica")
    return pop


def agregar_municipio(pop: pd.DataFrame) -> pd.DataFrame:
    faixas = pop.groupby("co_ibge_6d")["faixa_atracao_anunciada"].nunique()
    if (faixas != 1).any():
        raise AssertionError("município com mais de uma faixa anunciada no quadro")
    mun = (
        pop.groupby("co_ibge_6d", as_index=False)
        .agg(
            faixa_anunciada=("faixa_atracao_anunciada", "first"),
            n_celulas=("y1", "size"),
            n_celulas_y1=("y1", "sum"),
            n_celulas_y2=("y2", "sum"),
        )
        .rename(columns={"co_ibge_6d": "co_ibge"})
        .sort_values("co_ibge")
        .reset_index(drop=True)
    )
    mun["y1"] = mun["n_celulas_y1"] / mun["n_celulas"]
    mun["y2"] = mun["n_celulas_y2"] / mun["n_celulas"]
    return mun[["co_ibge", "faixa_anunciada", "n_celulas", "n_celulas_y1", "n_celulas_y2", "y1", "y2"]]


# --------------------------------------------------------------------------
# Reconstrução independente a partir dos brutos
# --------------------------------------------------------------------------

def reconstruir_quadro(anomalias: Counter) -> pd.DataFrame:
    cab, linhas = ler_aba(BRUTO_QUADRO)
    i_curso = coluna(cab, "CURSO")
    i_cnes = coluna(cab, "CNES")
    i_ibge = coluna(cab, "IBGE")
    i_faixa = coluna(cab, "FAIXA DE ATRACAO")
    registros = []
    for r in linhas:
        cnes = chave_cnes(r[i_cnes], anomalias)
        curso = chave_curso(r[i_curso], anomalias)
        if cnes is None or curso is None:
            anomalias["quadro_linha_sem_chave"] += 1
            continue
        registros.append(
            {
                "co_cnes_7d": cnes,
                "cod_curso": curso,
                "co_ibge_6d": chave_ibge(r[i_ibge]),
                "faixa_atracao_anunciada": texto_norm(r[i_faixa]),
            }
        )
    quadro = pd.DataFrame(registros)
    if quadro.duplicated(list(CHAVE)).any():
        raise AssertionError("quadro bruto com chave CNES–curso duplicada")
    return quadro


def ler_alocacao(caminho: Path, anomalias: Counter) -> dict[str, Any]:
    cab, linhas = ler_aba(caminho)
    i_curso = coluna(cab, "CURSO")
    i_cnes = coluna(cab, "CNES")
    i_nome = coluna(cab, "NOME CANDIDATO A")
    i_aloc = coluna(cab, "ALOCACAO")
    # Coluna extra sem cabeçalho só existe na versão sub judice.
    extras = [i for i, c in enumerate(cab) if c == "" and i > i_aloc]
    confirmados, desconsiderados, status, sub_judice = [], [], Counter(), []
    for r in linhas:
        if r[i_nome] is None or not texto_norm(r[i_nome]):
            anomalias["alocacao_linha_sem_nome"] += 1
            continue
        cnes = chave_cnes(r[i_cnes], anomalias)
        curso = chave_curso(r[i_curso], anomalias)
        if cnes is None or curso is None:
            anomalias["alocacao_linha_sem_chave"] += 1
            continue
        st = texto_norm(r[i_aloc])
        status[st[:40] or "VAZIO"] += 1
        if st.startswith("LOCAL DE ATUACAO CONFIRMADO"):
            confirmados.append((cnes, curso))
        elif st.startswith("LOCAL DE ATUACAO DESCONSIDERADO"):
            desconsiderados.append((cnes, curso))
        marca = " ".join(texto_norm(r[i]) for i in extras if i < len(r))
        if "JUDICE" in marca:
            sub_judice.append({"co_cnes_7d": cnes, "cod_curso": curso, "status_alocacao": st[:60]})
    return {
        "confirmados": eventos_por_celula(confirmados),
        "desconsiderados": eventos_por_celula(desconsiderados),
        "status": dict(sorted(status.items())),
        "registros": len(linhas),
        "sub_judice": sub_judice,
    }


def ler_realocacao(anomalias: Counter) -> Counter:
    cab, linhas = ler_aba(BRUTO_REALOC)
    i_curso, i_cnes = coluna(cab, "CURSO"), coluna(cab, "CNES")
    eventos = []
    for r in linhas:
        cnes, curso = chave_cnes(r[i_cnes], anomalias), chave_curso(r[i_curso], anomalias)
        if cnes is not None and curso is not None:
            eventos.append((cnes, curso))
    return eventos_por_celula(eventos)


def ler_homologados(caminho: Path, anomalias: Counter, exigir_resultado: bool) -> list[dict]:
    cab, linhas = ler_aba(caminho)
    i_curso = coluna(cab, "CURSO")
    i_cnes = coluna(cab, "CNES")
    i_nome = coluna(cab, "NOME CANDIDATO A")
    i_cpf = coluna(cab, "CPF")
    i_res = coluna(cab, "RESULTADO") if exigir_resultado else None
    pessoas = []
    for r in linhas:
        nome = texto_norm(r[i_nome])
        if not nome:
            anomalias[f"{caminho.stem}_sem_nome"] += 1
            continue
        if i_res is not None and texto_norm(r[i_res]) != "HOMOLOGADO":
            anomalias[f"{caminho.stem}_resultado_nao_homologado"] += 1
            continue
        cnes, curso = chave_cnes(r[i_cnes], anomalias), chave_curso(r[i_curso], anomalias)
        if cnes is None or curso is None:
            anomalias[f"{caminho.stem}_sem_chave"] += 1
            continue
        pessoas.append({"nome": nome, "cpf": chave_cpf_comum(r[i_cpf]), "celula": (cnes, curso)})
    return pessoas


def ler_ch2_auxiliares(anomalias: Counter) -> dict[str, Counter]:
    """Eventos da 2a chamada que NÃO entram no Y2; servem só a diagnósticos."""
    cab, linhas = ler_aba(BRUTO_CH2_CLASSIF, "ALOCADOS")
    i_curso, i_cnes, i_sit = coluna(cab, "CURSO"), coluna(cab, "CNES"), coluna(cab, "SITUACAO")
    alocados_finais = []
    for r in linhas:
        if texto_norm(r[i_sit]).startswith("ALOCADO"):
            cnes, curso = chave_cnes(r[i_cnes], anomalias), chave_curso(r[i_curso], anomalias)
            if cnes is not None and curso is not None:
                alocados_finais.append((cnes, curso))
    cab, linhas = ler_aba(BRUTO_CH2_VAGAS_ALOC, "VAGAS - CADASTRO RESERVA")
    i_curso, i_cnes = coluna(cab, "CURSO"), coluna(cab, "CNES")
    reserva = []
    for r in linhas:
        cnes, curso = chave_cnes(r[i_cnes], anomalias), chave_curso(r[i_curso], anomalias)
        if cnes is not None and curso is not None:
            reserva.append((cnes, curso))
    return {
        "alocados_finais_ch2": eventos_por_celula(alocados_finais),
        "quadro_reserva_ch2": eventos_por_celula(reserva),
    }


def reconstruir(anomalias: Counter) -> tuple[pd.DataFrame, dict[str, Any]]:
    quadro = reconstruir_quadro(anomalias)
    aloc = ler_alocacao(BRUTO_ALOC_SUBJUDICE, anomalias)
    aloc_ant = ler_alocacao(BRUTO_ALOC_RETIFICADA, Counter())
    realoc = ler_realocacao(anomalias)
    h1 = ler_homologados(BRUTO_HOMOLOG_CH1, anomalias, exigir_resultado=True)
    h2 = ler_homologados(BRUTO_HOMOLOG_CH2, anomalias, exigir_resultado=False)
    aux = ler_ch2_auxiliares(anomalias)

    # Pessoa da lista Ch2 é "nova" se não aparece na lista Ch1 nem pelo nome
    # nem pela chave de CPF comum às duas máscaras.
    nomes_h1 = {p["nome"] for p in h1}
    cpfs_h1 = {p["cpf"] for p in h1 if p["cpf"]}
    celulas_h1_por_nome: dict[str, set] = {}
    for p in h1:
        celulas_h1_por_nome.setdefault(p["nome"], set()).add(p["celula"])
    pareamento = Counter()
    novos, repetidos_mudaram_celula = [], []
    for p in h2:
        por_nome = p["nome"] in nomes_h1
        por_cpf = bool(p["cpf"]) and p["cpf"] in cpfs_h1
        pareamento[
            "nome_e_cpf" if por_nome and por_cpf else
            "so_nome" if por_nome else
            "so_cpf" if por_cpf else "nenhum"
        ] += 1
        if por_nome or por_cpf:
            antigas = celulas_h1_por_nome.get(p["nome"], set())
            if por_nome and p["celula"] not in antigas:
                repetidos_mudaram_celula.append(p["celula"])
        else:
            novos.append(p["celula"])

    conf = aloc["confirmados"]
    hom1 = eventos_por_celula(p["celula"] for p in h1)
    hom2_novas = eventos_por_celula(novos)
    hom2_todas = eventos_por_celula(p["celula"] for p in h2)
    conf_ant = aloc_ant["confirmados"]
    mudaram = eventos_por_celula(repetidos_mudaram_celula)

    chaves = list(zip(quadro["co_cnes_7d"], quadro["cod_curso"]))
    quadro["r_n_confirmacoes_ch1"] = [conf.get(k, 0) for k in chaves]
    quadro["r_n_homologacoes_ch1"] = [hom1.get(k, 0) for k in chaves]
    quadro["r_n_homologacoes_novas_ch2"] = [hom2_novas.get(k, 0) for k in chaves]
    quadro["r_y1"] = ((quadro["r_n_confirmacoes_ch1"] + quadro["r_n_homologacoes_ch1"]) > 0).astype(int)
    quadro["r_y2"] = ((quadro["r_y1"] == 1) | (quadro["r_n_homologacoes_novas_ch2"] > 0)).astype(int)
    # Sensibilidades (não substituem Y1/Y2).
    quadro["s_y1_alocacao_retificada_anterior"] = (
        (pd.Series([conf_ant.get(k, 0) for k in chaves]) + quadro["r_n_homologacoes_ch1"]) > 0
    ).astype(int)
    quadro["s_y2_qualquer_homologacao_ch2"] = (
        (quadro["r_y1"] == 1) | (pd.Series([hom2_todas.get(k, 0) for k in chaves]) > 0)
    ).astype(int)
    quadro["s_realocacao_ch1"] = [realoc.get(k, 0) for k in chaves]
    quadro["s_alocado_final_ch2"] = [aux["alocados_finais_ch2"].get(k, 0) for k in chaves]

    set_quadro = set(chaves)

    def fora(contador: Counter) -> dict[str, int]:
        return {
            "eventos": int(sum(v for k, v in contador.items() if k not in set_quadro)),
            "celulas": int(sum(1 for k in contador if k not in set_quadro)),
        }

    detalhes: dict[str, Any] = {
        "quadro_bruto": {"celulas": int(len(quadro)), "municipios": int(quadro["co_ibge_6d"].nunique())},
        "alocacao_subjudice_canonica": {
            "registros": aloc["registros"],
            "confirmacoes": int(sum(conf.values())),
            "locais_desconsiderados": int(sum(aloc["desconsiderados"].values())),
            "status_alocacao": aloc["status"],
            "registros_marcados_sub_judice": aloc["sub_judice"],
            "confirmacoes_fora_do_quadro": fora(conf),
        },
        "alocacao_retificada_anterior": {
            "registros": aloc_ant["registros"],
            "confirmacoes": int(sum(conf_ant.values())),
            "celulas_com_contagem_de_confirmacoes_diferente_da_subjudice": int(
                sum(1 for k in set(conf) | set(conf_ant) if conf.get(k, 0) != conf_ant.get(k, 0))
            ),
            "papel": "comparação; nunca somada à versão sub judice",
        },
        "homologados_ch1": {
            "registros_validos": len(h1),
            "fora_do_quadro": fora(hom1),
        },
        "homologados_ch2": {
            "registros_validos": len(h2),
            "pareamento_com_ch1": dict(sorted(pareamento.items())),
            "novos": len(novos),
            "repetidos": len(h2) - len(novos),
            "repetidos_em_celula_diferente_da_ch1": len(repetidos_mudaram_celula),
            "novos_fora_do_quadro_ch1": fora(hom2_novas),
            "regra_novo": (
                "pessoa da lista Ch2 sem correspondência na lista Ch1 pelo nome normalizado "
                "nem pela chave de CPF nas posições 1-3 e 8-11 (comuns às duas máscaras)"
            ),
        },
        "realocacao_ch1": {
            "propostas": int(sum(realoc.values())),
            "papel": "diagnóstico; proposta de realocação não é confirmação nem homologação e não entra em Y1",
        },
        "ch2_auxiliares": {
            "alocados_finais_ch2": int(sum(aux["alocados_finais_ch2"].values())),
            "celulas_quadro_reserva_ch2": int(len(aux["quadro_reserva_ch2"])),
            "papel": "diagnóstico; o adendo define Y2 só por homologação nova na 2a chamada",
        },
        "celulas_ch1_que_receberam_homologado_repetido_de_outra_celula": int(
            sum(1 for k in mudaram if k in set_quadro)
        ),
    }
    return quadro, detalhes


# --------------------------------------------------------------------------
# Validação
# --------------------------------------------------------------------------

def motivo_divergencia(linha: pd.Series) -> str:
    motivos = []
    if linha["_merge"] == "left_only":
        return "célula da população canônica ausente do quadro bruto reconstruído (chave CNES–curso)"
    if linha["_merge"] == "right_only":
        return "célula do quadro bruto reconstruído ausente da população canônica (chave CNES–curso)"
    if linha["n_confirmacoes_ch1"] != linha["r_n_confirmacoes_ch1"]:
        motivos.append("contagem de confirmações Ch1 difere (versão da alocação ou regra de status)")
    if linha["n_homologacoes_ch1"] != linha["r_n_homologacoes_ch1"]:
        motivos.append("contagem de homologações Ch1 difere (filtro de RESULTADO ou chave)")
    if linha["n_homologacoes_novas_ch2"] != linha["r_n_homologacoes_novas_ch2"]:
        motivos.append("homologação nova Ch2 difere (regra de pareamento nome/CPF entre listas)")
    if linha["co_ibge_6d"] != linha["r_co_ibge_6d"]:
        motivos.append("código IBGE difere")
    if linha["faixa_atracao_anunciada"] != linha["r_faixa"]:
        motivos.append("faixa anunciada difere")
    return "; ".join(motivos) or "sem motivo identificado"


def validar(canon: pd.DataFrame, rec: pd.DataFrame) -> dict[str, Any]:
    rec = rec.rename(columns={"co_ibge_6d": "r_co_ibge_6d", "faixa_atracao_anunciada": "r_faixa"})
    comp = canon.merge(rec, on=list(CHAVE), how="outer", indicator=True)
    ambos = comp["_merge"] == "both"
    contagens = [
        ("n_confirmacoes_ch1", "r_n_confirmacoes_ch1"),
        ("n_homologacoes_ch1", "r_n_homologacoes_ch1"),
        ("n_homologacoes_novas_ch2", "r_n_homologacoes_novas_ch2"),
    ]
    comp["diverge_y1"] = ~ambos | (comp["y1"] != comp["r_y1"])
    comp["diverge_y2"] = ~ambos | (comp["y2"] != comp["r_y2"])
    comp["diverge_contagem"] = ~ambos | pd.concat(
        [comp[a] != comp[b] for a, b in contagens], axis=1
    ).any(axis=1)
    comp["diverge_atributo"] = ~ambos | (comp["co_ibge_6d"] != comp["r_co_ibge_6d"]) | (
        comp["faixa_atracao_anunciada"] != comp["r_faixa"]
    )
    comp["diverge"] = comp[["diverge_y1", "diverge_y2", "diverge_contagem", "diverge_atributo"]].any(axis=1)

    lista = []
    for _, linha in comp.loc[comp["diverge"]].sort_values(list(CHAVE)).iterrows():
        def inteiro(v):
            return None if pd.isna(v) else int(v)
        lista.append(
            {
                "co_cnes_7d": linha["co_cnes_7d"],
                "cod_curso": int(linha["cod_curso"]),
                "co_ibge_6d": linha["co_ibge_6d"] if isinstance(linha["co_ibge_6d"], str) else linha["r_co_ibge_6d"],
                "y1_canonica": inteiro(linha["y1"]),
                "y1_reconstruida": inteiro(linha["r_y1"]),
                "y2_canonica": inteiro(linha["y2"]),
                "y2_reconstruida": inteiro(linha["r_y2"]),
                "contagens_canonica": [inteiro(linha[a]) for a, _ in contagens],
                "contagens_reconstruida": [inteiro(linha[b]) for _, b in contagens],
                "motivo_provavel": motivo_divergencia(linha),
            }
        )

    so_ambos = comp.loc[ambos]
    return {
        "celulas_canonicas": int((comp["_merge"] != "right_only").sum()),
        "celulas_reconstruidas": int((comp["_merge"] != "left_only").sum()),
        "celulas_em_ambas": int(ambos.sum()),
        "celulas_batidas_y1": int((~comp["diverge_y1"]).sum()),
        "celulas_batidas_y2": int((~comp["diverge_y2"]).sum()),
        "celulas_batidas_y1_y2_contagens_e_atributos": int((~comp["diverge"]).sum()),
        "celulas_divergentes_y1": int(comp["diverge_y1"].sum()),
        "celulas_divergentes_y2": int(comp["diverge_y2"].sum()),
        "celulas_divergentes_contagens": int(comp["diverge_contagem"].sum()),
        "celulas_divergentes_atributos": int(comp["diverge_atributo"].sum()),
        "ordem_contagens": [a for a, _ in contagens],
        "divergencias": lista,
        "_so_ambos": so_ambos,
    }


# --------------------------------------------------------------------------
# Proveniência
# --------------------------------------------------------------------------

def metadados_manifesto() -> dict[str, dict]:
    if not MANIFESTO_FONTES.exists():
        return {}
    manifesto = json.loads(MANIFESTO_FONTES.read_text(encoding="utf-8"))
    por_arquivo: dict[str, dict] = {}
    for f in manifesto.get("fontes", []):
        nome = f.get("arquivo")
        if not nome:
            continue
        if nome not in por_arquivo or (f.get("caminho") and not por_arquivo[nome].get("caminho")):
            por_arquivo[nome] = f
    return por_arquivo


def bloco_entrada(caminho: Path, papel: str, unidade: str, chaves: str, filtros: str,
                  data_referencia: str, manifesto: dict[str, dict]) -> dict[str, Any]:
    m = manifesto.get(caminho.name, {})
    sha = sha256_arquivo(caminho)
    bloco: dict[str, Any] = {
        "caminho": rel(caminho),
        "sha256": sha,
        "bytes": caminho.stat().st_size,
        "papel": papel,
        "fonte": m.get("fonte", "Ministério da Saúde (publicação do PMM-E)" if "raw" in caminho.parts else "pipeline do repositório"),
        "data_referencia": data_referencia,
        "cobertura": m.get("cobertura", "ciclo 1 do PMM-E"),
        "unidade": unidade,
        "chaves": chaves,
        "filtros": filtros,
    }
    if m:
        bloco["manifesto"] = {
            "url": m.get("url"),
            "data_extracao": m.get("data_extracao"),
            "sha256_no_manifesto": m.get("sha256"),
            "sha256_confere": (m.get("sha256") == sha) if m.get("sha256") else None,
        }
    return bloco


# --------------------------------------------------------------------------
# Execução
# --------------------------------------------------------------------------

def main() -> None:
    entradas_obrigatorias = [
        ADENDO, MATRIZ_FUNIL, QUADRO_CANONICO, BRUTO_QUADRO, BRUTO_ALOC_SUBJUDICE,
        BRUTO_ALOC_RETIFICADA, BRUTO_REALOC, BRUTO_HOMOLOG_CH1, BRUTO_HOMOLOG_CH2,
        BRUTO_CH2_VAGAS_ALOC, BRUTO_CH2_CLASSIF,
    ]
    for caminho in entradas_obrigatorias:
        if not caminho.exists():
            raise FileNotFoundError(caminho)

    adendo = json.loads(ADENDO.read_text(encoding="utf-8"))

    # 1. Fonte canônica -> CSV por município.
    canon = carregar_canonica()
    mun = agregar_municipio(canon)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUT_CSV.with_suffix(".csv.tmp")
    mun.to_csv(tmp, index=False, float_format="%.10f", lineterminator="\n")
    tmp.replace(OUT_CSV)

    # 2. Reconstrução independente e validação célula a célula.
    pendencias: list[str] = []
    anomalias: Counter = Counter()
    try:
        rec, detalhes = reconstruir(anomalias)
        val = validar(canon, rec)
        so_ambos = val.pop("_so_ambos")
        reconstrucao_completa = True
    except Exception as erro:  # registra a pendência sem perder o CSV canônico
        rec, detalhes, so_ambos = None, {}, None
        val = {}
        reconstrucao_completa = False
        pendencias.append(f"reconstrução falhou: {type(erro).__name__}: {erro}")

    totais = {
        "y1_canonica": int(canon["y1"].sum()),
        "y2_canonica": int(canon["y2"].sum()),
        "celulas": int(len(canon)),
        "municipios": int(canon["co_ibge_6d"].nunique()),
        "esperado_adendo": {"y1": 393, "y2": 461, "celulas": N_CELULAS_P1, "municipios": N_MUNICIPIOS_P1},
    }
    if rec is not None:
        totais.update(
            {
                "y1_reconstruida": int(rec["r_y1"].sum()),
                "y2_reconstruida": int(rec["r_y2"].sum()),
                "celulas_reconstruidas": int(len(rec)),
                "municipios_reconstruidos": int(rec["co_ibge_6d"].nunique()),
            }
        )
    totais["confere_esperado"] = bool(
        totais["y1_canonica"] == 393 and totais["y2_canonica"] == 461
        and totais.get("y1_reconstruida") == 393 and totais.get("y2_reconstruida") == 461
    )

    sensibilidades: dict[str, Any] = {}
    if rec is not None:
        sensibilidades = {
            "nota": "diagnósticos de definição; não alteram Y1/Y2 do adendo, que seguem a fonte canônica",
            "y1_com_alocacao_retificada_anterior_no_lugar_da_subjudice": int(
                rec["s_y1_alocacao_retificada_anterior"].sum()
            ),
            "y2_contando_qualquer_homologacao_ch2_na_celula_mesmo_repetida": int(
                rec["s_y2_qualquer_homologacao_ch2"].sum()
            ),
            "celulas_com_proposta_de_realocacao_ch1_e_y1_zero": int(
                ((rec["s_realocacao_ch1"] > 0) & (rec["r_y1"] == 0)).sum()
            ),
            "celulas_com_alocado_final_ch2_e_y2_zero": int(
                ((rec["s_alocado_final_ch2"] > 0) & (rec["r_y2"] == 0)).sum()
            ),
        }

    manifesto = metadados_manifesto()
    entradas = [
        bloco_entrada(ADENDO, "protocolo congelado do E4 (somente lido)", "documento", "-", "-",
                      adendo.get("data_congelamento", ""), manifesto),
        bloco_entrada(MATRIZ_FUNIL, "fonte canônica de Y1 e Y2 (A1)", "célula CNES–curso × chamada",
                      "co_cnes_7d, cod_curso, chamada",
                      "chamada 1 (Y1); chamada 2, n_homologacoes_novas_ch2 > 0 (componente de Y2)",
                      "2026-09-01 (data de referência do A1)", manifesto),
        bloco_entrada(QUADRO_CANONICO, "população primária do A4 (1.295 células)", "célula CNES–curso",
                      "co_cnes_7d, cod_curso", "nenhum (quadro completo da 1a chamada)",
                      "quadro original publicado em 24/07/2025", manifesto),
        bloco_entrada(BRUTO_QUADRO, "reconstrução: quadro de vagas da 1a chamada", "célula CNES–curso",
                      "CNES (7 dígitos), código do curso", "linhas com CNES e curso válidos",
                      "quadro original publicado em 24/07/2025", manifesto),
        bloco_entrada(BRUTO_ALOC_SUBJUDICE, "reconstrução: confirmações Ch1 (versão canônica)",
                      "registro candidato–local", "CNES, curso",
                      "ALOCAÇÃO começa com 'LOCAL DE ATUAÇÃO CONFIRMADO'",
                      "não declarada no arquivo; versão sub judice da alocação retificada", manifesto),
        bloco_entrada(BRUTO_ALOC_RETIFICADA, "reconstrução: versão anterior da alocação (só comparação)",
                      "registro candidato–local", "CNES, curso",
                      "ALOCAÇÃO começa com 'LOCAL DE ATUAÇÃO CONFIRMADO'; nunca somada",
                      "não declarada no arquivo", manifesto),
        bloco_entrada(BRUTO_REALOC, "diagnóstico: propostas de realocação Ch1", "registro candidato–local",
                      "CNES, curso", "nenhum; não entra em Y1", "não declarada no arquivo", manifesto),
        bloco_entrada(BRUTO_HOMOLOG_CH1, "reconstrução: homologados Ch1", "registro pessoa–local",
                      "CNES, curso; pessoa por nome e CPF (posições 1-3, 8-11) só para parear com Ch2",
                      "RESULTADO = HOMOLOGADO", "não declarada no arquivo", manifesto),
        bloco_entrada(BRUTO_HOMOLOG_CH2, "reconstrução: homologados Ch2 (novos entram em Y2)",
                      "registro pessoa–local", "CNES, curso; pessoa por nome e CPF (posições 1-3, 8-11)",
                      "novo = sem correspondência na lista Ch1", "não declarada no arquivo", manifesto),
        bloco_entrada(BRUTO_CH2_VAGAS_ALOC, "diagnóstico: quadro de reserva da 2a chamada",
                      "célula CNES–curso", "CNES, curso", "aba 'VAGAS - CADASTRO RESERVA'; não entra em Y2",
                      "cadastro de reserva oficial de 29/09/2025", manifesto),
        bloco_entrada(BRUTO_CH2_CLASSIF, "diagnóstico: alocados finais da 2a chamada",
                      "registro candidato–local", "CNES, curso", "SITUAÇÃO começa com 'ALOCADO'; não entra em Y2",
                      "não declarada no arquivo", manifesto),
    ]

    relatorio: dict[str, Any] = {
        "documento": "E4 (adendo): validação célula a célula da reconstrução independente de Y1 e Y2",
        "data_execucao": "2026-10-14",
        "script": rel(Path(__file__).resolve()),
        "protocolo": {"arquivo": rel(ADENDO), "sha256": sha256_arquivo(ADENDO)},
        "escopo": {
            "populacao": adendo.get("populacao"),
            "unidade": "célula CNES–curso (validação) e município (CSV gravado)",
            "Y1": adendo.get("outcomes", {}).get("Y1_principal"),
            "Y2": adendo.get("outcomes", {}).get("Y2_secundario"),
            "contraste": "nenhum: esta etapa só constrói o outcome; não estima efeito",
            "nao_feito": [
                "cruzamento do outcome com o escore administrativo",
                "cruzamento do outcome com o IVS",
                "proporções por faixa além das já relatadas no A4",
            ],
        },
        "saida_municipio": {
            "arquivo": rel(OUT_CSV),
            "fonte_dos_valores": "fonte canônica (matriz do funil filtrada como no A4)",
            "linhas": int(len(mun)),
            "colunas": list(mun.columns),
            "soma_n_celulas": int(mun["n_celulas"].sum()),
            "soma_n_celulas_y1": int(mun["n_celulas_y1"].sum()),
            "soma_n_celulas_y2": int(mun["n_celulas_y2"].sum()),
            "sha256": sha256_arquivo(OUT_CSV),
        },
        "reconstrucao_completa": reconstrucao_completa,
        "pendencias": pendencias,
        "totais": totais,
        "validacao_celula_a_celula": val,
        "regras_da_reconstrucao": [
            "colunas localizadas pelo nome normalizado do cabeçalho, não pela posição",
            "CNES: dígitos do valor (inteiro do Excel ou texto) completados com zeros à esquerda até 7; mais de 7 dígitos é rejeitado",
            "curso: número inicial do rótulo ('01 - ...' ou '01. ...'), válido de 1 a 16",
            "população: as 1.295 linhas do quadro bruto da 1a chamada; eventos fora do quadro não contam",
            "confirmação Ch1: versão sub judice da alocação retificada, status 'LOCAL DE ATUAÇÃO CONFIRMADO'; a versão retificada anterior só é comparada",
            "homologação Ch1: lista da 1a chamada com RESULTADO = HOMOLOGADO",
            "homologação nova Ch2: registro da lista da 2a chamada cuja pessoa não está na lista Ch1 (nome normalizado ou CPF nas posições 1-3 e 8-11)",
            "proposta de realocação, desconsideração de local, alocação final e quadro de reserva da 2a chamada não entram em Y1/Y2",
            "Y1 = confirmação Ch1 ou homologação Ch1 > 0; Y2 = Y1 ou homologação nova Ch2 > 0",
        ],
        "detalhes_reconstrucao": detalhes,
        "anomalias_de_leitura": dict(sorted(anomalias.items())),
        "sensibilidades_de_definicao": sensibilidades,
        "entradas": entradas,
        "dados_pessoais_gravados": False,
        "linguagem": "construção de outcome descritiva; nenhuma estimativa causal",
    }
    if so_ambos is not None and val.get("celulas_divergentes_y1", 1) == 0 and val.get("celulas_divergentes_y2", 1) == 0:
        relatorio["conclusao"] = (
            "a reconstrução independente reproduz a fonte canônica em todas as células para Y1 e Y2"
        )
    elif val:
        relatorio["conclusao"] = (
            f"{val['celulas_divergentes_y1']} células divergem em Y1 e {val['celulas_divergentes_y2']} em Y2; "
            "a fonte canônica prevalece, conforme o adendo"
        )
    else:
        relatorio["conclusao"] = "reconstrução pendente; CSV gravado a partir da fonte canônica"

    tmp = OUT_JSON.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(OUT_JSON)

    print(f"[OK] {rel(OUT_CSV)}: {len(mun)} municípios; Y1 {totais['y1_canonica']}/{totais['celulas']}, "
          f"Y2 {totais['y2_canonica']}/{totais['celulas']} (canônica)")
    if rec is not None:
        print(f"[OK] reconstrução: Y1 {totais['y1_reconstruida']}, Y2 {totais['y2_reconstruida']}; "
              f"divergências Y1 {val['celulas_divergentes_y1']}, Y2 {val['celulas_divergentes_y2']}, "
              f"contagens {val['celulas_divergentes_contagens']}, atributos {val['celulas_divergentes_atributos']}")
    else:
        print("[PENDENTE] reconstrução:", pendencias)
    print(f"[OK] {rel(OUT_JSON)}")


if __name__ == "__main__":
    main()
