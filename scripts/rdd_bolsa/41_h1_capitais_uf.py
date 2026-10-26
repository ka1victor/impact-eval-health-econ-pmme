"""Adendo 48c: capitais e UF no corte 0,300 (H1). Robustez pós-resultado, descritiva quanto ao mecanismo.

Especificação: `docs/06_execucao/48c_adendo_capitais_e_UF.md`, congelada em 26/10/2026 antes destas contas (commit
4326241; SHA-256 em `HC_resumo.json`). Estatuto de toda saída: `ADENDO_48C_POS_RESULTADO`; `natureza_dos_dados =
EMPIRICO`. Não muda a especificação principal da H1 (adendo 48b).

Pergunta: a queda do preenchimento em 0,300 anda junto com a presença de capitais (ou com a região) logo abaixo do
corte?

O que faz, na ordem
-------------------
1. Referência de capitais e regiões (IBGE), sem nada digitado:
   - capitais: base "Localidades do Brasil 2022" do IBGE (geoftp; categoria `CT_LOCALID = Cidade` com
     `SCT_LOCALI` = "Capital Estadual" ou "Capital Federal"), 27 municípios;
   - macrorregião de cada UF: SIDRA/IBGE, tabela 4709 consultada por UF dentro de cada Grande Região (`n3/in n2 r`).
   A cópia fica em `output/aquisicao/ibge_capitais_uf_regiao.csv`, com o manifesto (URLs, datas, SHA-256 dos
   arquivos baixados e da cópia) em `output/aquisicao/manifesto_ibge_capitais_uf_regiao.json`. Só
   `--baixar-referencias` acessa a rede; a execução normal lê a cópia e confere o SHA-256.
2. Base de células e de municípios: a reconstrução da auditoria 36 (`scripts/auditoria_H1/a36_reconstruir_H1.py`,
   funções `montar_ciclo1/2/3` e `ler_ivs`), importada sem alteração. No ciclo 2 o tipo de vaga vem do quadro de
   13/02/2026 (48b, §7). A base montada aqui é conferida, célula a célula e município a município, contra
   `output/auditoria_H1/a36_celulas.csv` e `a36_municipios.csv`.
3. Linhas do adendo 48c, todas com local linear, kernel triangular, h = 0,050, cada corte separado, ciclos 1–3
   empilhados com intercepto e inclinações por ciclo, CR1 por município (`rdd_lib.rd_empilhado`):
   - C-1: balanço no corte — salto de "é capital", "é do Nordeste" e "é do Norte", por município × ciclo e por
     célula, nas amostras da H1 (48b) e no quadro inteiro (medidas antigas);
   - base: HI-1 e HI-2 do 48b sem controle extra (para comparar);
   - C-2: HI-1 e HI-2 com dummy de capital; C-3: com efeito fixo de UF; C-4: sem as capitais;
   - C-5: A3 (tipo de vaga do pipeline e de 13/02), N1 com controle (S-a) e taxa por vaga oferecida (S-e), sem
     ajuste e com C-2, C-3 e C-4;
   - BKY entre as linhas C-2 a C-4.
4. Conferências: as linhas sem ajuste e com dummy de capital/sem capitais que a auditoria 36 já tinha calculado,
   e A3, N1 S-a e taxa S-e gravados pelo pipeline (`NA_estimativas.csv`, `N_estimativas.csv`); se algo não bater, o
   script para sem gravar. HI-1 e HI-2 sem ajuste contra `HI_estimativas.csv` (script 40) quando ele existir; se
   não existir, a conferência fica registrada como pendente.
5. Leitura pré-registrada (48c, §2), figuras com "Como ler" e o doc 57o (gerado entre marcadores).

Integridade: nada imputado nem simulado; célula fora da amostra é contada; o arquivo local de IVS da auditoria 16
não é lido (running variable = IVS 2010 oficial, a08); `data/` só é lido; nenhuma saída tem identificador de pessoa
(só contagens por célula e município). Linguagem descritiva e pós-resultado: "anda junto com", nunca "causa".

Uso
---
    python3 scripts/rdd_bolsa/41_h1_capitais_uf.py                        # calcula e grava as saídas e o doc 57o
    python3 scripts/rdd_bolsa/41_h1_capitais_uf.py --atualizar-doc        # só regrava o doc 57o das saídas
    python3 scripts/rdd_bolsa/41_h1_capitais_uf.py --baixar-referencias   # baixa de novo a referência do IBGE
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import io
import json
import math
import sys
import tempfile
import textwrap
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"
DIR_A36 = ROOT / "scripts" / "auditoria_H1"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location(nome, caminho)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[nome] = mod
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = bytecode
    return mod


L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_para_hc")
A36 = _importar(DIR_A36 / "a36_reconstruir_H1.py", "a36_reconstruir_para_hc")


class FalhaValidacao(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Caminhos e parâmetros do adendo 48c
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
NOME_EST = "HC_estimativas.csv"
NOME_RESUMO = "HC_resumo.json"
DIR_FIG = "HC_figuras"
DOC = ROOT / "docs" / "06_execucao" / "57o_h1_capitais_uf.md"
ADENDO_48C = ROOT / "docs" / "06_execucao" / "48c_adendo_capitais_e_UF.md"
ADENDO_48B = ROOT / "docs" / "06_execucao" / "48b_adendo_H1_vagas_imediatas.md"
AUDITORIA_36 = ROOT / "docs" / "auditorias" / "36_auditoria_dados_H1.md"
A36_CEL = ROOT / "output" / "auditoria_H1" / "a36_celulas.csv"
A36_MUN = ROOT / "output" / "auditoria_H1" / "a36_municipios.csv"
A36_EST = ROOT / "output" / "auditoria_H1" / "a36_estimativas.csv"
N_EST = OUT / "N_estimativas.csv"
NA_EST = OUT / "NA_estimativas.csv"
HI_EST = OUT / "HI_estimativas.csv"
IVS_OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
REF_CSV = ROOT / "output" / "aquisicao" / "ibge_capitais_uf_regiao.csv"
REF_MANIFESTO = ROOT / "output" / "aquisicao" / "manifesto_ibge_capitais_uf_regiao.json"

# Fontes oficiais do IBGE (só acessadas com --baixar-referencias).
URL_LOCALIDADES = ("https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/localidades/"
                   "Localidades_do_Brasil/2022/Localidades_Brasil_shp.zip")
DBF_LOCALIDADES = "BR_localidades_2022.dbf"
CATEGORIA_CIDADE = "Cidade"
SUBCATEGORIAS_CAPITAL = ("Capital Estadual", "Capital Federal")
URL_SIDRA_REGIOES = "https://apisidra.ibge.gov.br/values/t/4709/n2/all/v/93/p/2022/h/n"
URL_SIDRA_UFS_NA_REGIAO = "https://apisidra.ibge.gov.br/values/t/4709/n3/in%20n2%20{r}/v/93/p/2022/h/n"

DATA_EXECUCAO = "2026-10-26"
ESTATUTO = "ADENDO_48C_POS_RESULTADO"
NATUREZA = "EMPIRICO"
CORTES = (300, 400)
H_MIL = L.H_PRINCIPAL_MIL      # 50 (0,050), como no 48b
CICLOS = (1, 2, 3)
AJUSTES = ("sem_ajuste", "capital", "uf", "sem_capitais")
ROT_AJ = {"sem_ajuste": "sem ajuste", "capital": "com dummy de capital (C-2)", "uf": "com efeito fixo de UF (C-3)",
          "sem_capitais": "sem as capitais (C-4)"}
ROT_AJ_CURTO = {"sem_ajuste": "sem ajuste", "capital": "+ dummy de capital", "uf": "+ efeito fixo de UF",
                "sem_capitais": "sem as capitais"}
BLOCO_AJ = {"capital": "C-2", "uf": "C-3", "sem_capitais": "C-4"}
REGIOES_BALANCO = ("Nordeste", "Norte")

MEDIDAS = {
    "HI-1": {"rotulo": "HI-1: célula com vaga imediata preenchida na 1ª chamada", "unidade_analise": "celula",
             "amostra": "H1", "papel": "H1 principal (48b)", "unidade": "fracao (x100 = p.p.)",
             "y": "preenchida", "fe": "fe_cc", "z_ciclo": None, "z": (), "peso": None,
             "especificacao": "celulas com >= 1 vaga imediata (c2: quadro de 13/02/2026); EF curso x ciclo"},
    "HI-2": {"rotulo": "HI-2: médicos alocados em células com vaga imediata, por município",
             "unidade_analise": "municipio", "amostra": "H1", "papel": "H1 principal (48b)",
             "unidade": "medicos alocados por municipio", "y": "n_aloc_imed_pre", "fe": None, "z_ciclo": "vi_pre",
             "z": (), "peso": None,
             "especificacao": "municipio x ciclo com >= 1 celula com vaga imediata (c2: 13/02/2026); controle = "
                              "vagas imediatas dessas celulas, um coeficiente por ciclo (como o S-a)"},
    "A3": {"rotulo": "A3: célula aberta preenchida (tipo de vaga do pipeline)", "unidade_analise": "celula",
           "amostra": "quadro", "papel": "medida antiga (C-5)", "unidade": "fracao (x100 = p.p.)",
           "y": "preenchida", "fe": "fe_cc", "z_ciclo": None, "z": ("com_imediata_pipe",), "peso": None,
           "especificacao": "todas as celulas; EF curso x ciclo + tipo de vaga do pipeline (c2: quadro de 19/03/2026, "
                            "pos-resultado), como no adendo §7 do protocolo 48"},
    "A3-pre": {"rotulo": "A3 com tipo de vaga de 13/02/2026", "unidade_analise": "celula", "amostra": "quadro",
               "papel": "medida antiga (C-5), tipo de vaga pre-alocacao", "unidade": "fracao (x100 = p.p.)",
               "y": "preenchida", "fe": "fe_cc", "z_ciclo": None, "z": ("com_imediata_pre",), "peso": None,
               "especificacao": "todas as celulas; EF curso x ciclo + tipo de vaga pre-alocacao (c2: 13/02/2026, 48b "
                                "§7)"},
    "N1": {"rotulo": "N1 com controle (S-a): vagas preenchidas por município", "unidade_analise": "municipio",
           "amostra": "quadro", "papel": "medida antiga (C-5)", "unidade": "medicos alocados por municipio",
           "y": "n_alocados", "fe": None, "z_ciclo": "vic", "z": (), "peso": None,
           "especificacao": "municipio x ciclo do quadro; controle = vagas oferecidas (imediatas + CR), um "
                            "coeficiente por ciclo (S-a do protocolo 48)"},
    "taxa": {"rotulo": "Taxa por vaga oferecida (S-e)", "unidade_analise": "municipio", "amostra": "quadro",
             "papel": "medida antiga (C-5)", "unidade": "fracao (x100 = p.p.)", "y": "taxa", "fe": None,
             "z_ciclo": None, "z": (), "peso": "vic",
             "especificacao": "municipio x ciclo do quadro; alocados / vagas oferecidas, ponderado pelas vagas (S-e)"},
}
MEDIDAS_H1 = ("HI-1", "HI-2")
MEDIDAS_ANTIGAS = ("A3", "A3-pre", "N1", "taxa")
VARIAVEIS_BALANCO = {"capital": "é capital", "nordeste": "é do Nordeste", "norte": "é do Norte"}
AMOSTRAS = {"H1": "amostra da H1 (48b): células com vaga imediata / municípios com essas células",
            "quadro": "quadro inteiro (amostra das medidas antigas)"}


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def rotulo(caminho: Path) -> str:
    p = Path(caminho).resolve()
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def _nan_none(o):
    if isinstance(o, dict):
        return {str(k): _nan_none(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_nan_none(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not math.isfinite(float(o)) else float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def gravar_json(caminho: Path, obj: dict) -> None:
    caminho.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Referência do IBGE: capitais e macrorregião de cada UF
# ---------------------------------------------------------------------------

def _baixar(url: str, timeout: int = 300) -> tuple[bytes, dict]:
    with urllib.request.urlopen(url, timeout=timeout) as r:  # noqa: S310 (URL fixa do IBGE)
        corpo = r.read()
        cab = {k: r.headers.get(k) for k in ("Last-Modified", "Content-Length", "Content-Type")}
    return corpo, cab


def baixar_referencias() -> dict:
    """Baixa as duas fontes do IBGE, monta a tabela das 27 UFs e grava a cópia e o manifesto em output/aquisicao/."""
    from dbfread import DBF  # só aqui: a execução normal não precisa

    acesso = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    zbytes, zcab = _baixar(URL_LOCALIDADES)
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(io.BytesIO(zbytes)) as z:
            nomes = z.namelist()
            if DBF_LOCALIDADES not in nomes:
                raise FalhaValidacao(f"{DBF_LOCALIDADES} ausente do ZIP do IBGE ({nomes})")
            dbf_bytes = z.read(DBF_LOCALIDADES)
            cpg = DBF_LOCALIDADES.replace(".dbf", ".cpg")
            codificacao = z.read(cpg).decode("ascii").strip() if cpg in nomes else "utf-8"
        caminho_dbf = Path(tmp) / DBF_LOCALIDADES
        caminho_dbf.write_bytes(dbf_bytes)
        linhas = [dict(r) for r in DBF(str(caminho_dbf), encoding=codificacao)
                  if r["CT_LOCALID"] == CATEGORIA_CIDADE and r["SCT_LOCALI"] in SUBCATEGORIAS_CAPITAL]
    cap = pd.DataFrame(linhas)
    if len(cap) != 27 or cap["CD_UF"].nunique() != 27:
        raise FalhaValidacao(f"esperadas 27 capitais, uma por UF; achadas {len(cap)} em {cap['CD_UF'].nunique()} UFs")
    if not (cap["CD_MUN"].str[:2] == cap["CD_UF"]).all():
        raise FalhaValidacao("capital com código de município fora da própria UF")
    rbytes, rcab = _baixar(URL_SIDRA_REGIOES, timeout=60)
    regioes = [(x["D1C"], x["D1N"]) for x in json.loads(rbytes)]
    sidra = {"regioes": {"url": URL_SIDRA_REGIOES, "sha256_resposta": sha256_bytes(rbytes)}, "ufs_por_regiao": []}
    uf_reg = []
    for cod, nome in regioes:
        url = URL_SIDRA_UFS_NA_REGIAO.format(r=cod)
        b, _ = _baixar(url, timeout=60)
        sidra["ufs_por_regiao"].append({"regiao": cod, "url": url, "sha256_resposta": sha256_bytes(b)})
        uf_reg += [{"cd_uf": x["D1C"], "nome_uf_sidra": x["D1N"], "cd_regiao": cod, "nome_regiao": nome}
                   for x in json.loads(b)]
    ur = pd.DataFrame(uf_reg)
    if len(ur) != 27 or ur["cd_uf"].nunique() != 27:
        raise FalhaValidacao("SIDRA não devolveu 27 UFs em 5 regiões")
    ref = cap.rename(columns={"CD_UF": "cd_uf", "SIGLA_UF": "sigla_uf", "NM_UF": "nome_uf",
                              "CD_MUN": "capital_co_ibge_7d", "NM_MUN": "capital_nome",
                              "SCT_LOCALI": "categoria_ibge"})[
        ["cd_uf", "sigla_uf", "nome_uf", "capital_co_ibge_7d", "capital_nome", "categoria_ibge"]]
    ref = ref.merge(ur, on="cd_uf", how="outer", validate="1:1", indicator=True)
    if (ref["_merge"] != "both").any():
        raise FalhaValidacao("UF sem capital ou sem região")
    if (ref["nome_uf"] != ref["nome_uf_sidra"]).any():
        raise FalhaValidacao("nome da UF difere entre Localidades 2022 e SIDRA")
    ref["capital_co_ibge_6d"] = ref["capital_co_ibge_7d"].str[:6]
    ref = ref[["cd_uf", "sigla_uf", "nome_uf", "cd_regiao", "nome_regiao", "capital_co_ibge_7d", "capital_co_ibge_6d",
               "capital_nome", "categoria_ibge"]].sort_values("cd_uf").reset_index(drop=True)
    ref["natureza_dos_dados"] = NATUREZA
    REF_CSV.parent.mkdir(parents=True, exist_ok=True)
    ref.to_csv(REF_CSV, index=False)
    manifesto = {
        "natureza_dos_dados": NATUREZA,
        "etapa": "referencia_ibge_capitais_uf_regiao (scripts/rdd_bolsa/41_h1_capitais_uf.py --baixar-referencias)",
        "data_acesso_utc": acesso,
        "fontes": {
            "capitais": {"fonte": "IBGE, Localidades do Brasil 2022 (estrutura territorial, geoftp)",
                         "url": URL_LOCALIDADES, "last_modified": zcab["Last-Modified"],
                         "sha256_zip": sha256_bytes(zbytes), "arquivo_lido": DBF_LOCALIDADES,
                         "sha256_dbf": sha256_bytes(dbf_bytes), "codificacao": codificacao,
                         "filtro": f"CT_LOCALID == '{CATEGORIA_CIDADE}' e SCT_LOCALI em {list(SUBCATEGORIAS_CAPITAL)}",
                         "data_referencia": "2022", "cobertura": "Brasil", "unidade": "localidade (sede municipal)",
                         "chaves": "CD_UF; CD_MUN (7 dígitos)"},
            "regioes": {"fonte": "IBGE, SIDRA, tabela 4709 (Censo 2022), níveis n2 (Grande Região) e n3 (UF)",
                        **sidra, "data_referencia": "2022", "cobertura": "27 UFs", "unidade": "UF",
                        "chaves": "D1C (código da UF ou da Grande Região)",
                        "uso": "só a pertença territorial UF -> Grande Região; o valor da variável 93 não é usado"},
        },
        "saida": {"arquivo": rotulo(REF_CSV), "sha256": sha256(REF_CSV), "linhas": int(len(ref)),
                  "unidade": "UF (uma capital por UF)",
                  "chaves": "cd_uf; capital_co_ibge_6d (6 dígitos, como o IVS a08 e os quadros)"},
    }
    gravar_json(REF_MANIFESTO, manifesto)
    return manifesto


def carregar_referencias() -> tuple[pd.DataFrame, dict]:
    if not REF_CSV.exists() or not REF_MANIFESTO.exists():
        raise FalhaValidacao("referência do IBGE ausente: rode com --baixar-referencias")
    man = json.loads(REF_MANIFESTO.read_text(encoding="utf-8"))
    if sha256(REF_CSV) != man["saida"]["sha256"]:
        raise FalhaValidacao("SHA-256 da cópia da referência do IBGE difere do manifesto")
    ref = pd.read_csv(REF_CSV, dtype=str)
    if len(ref) != 27 or ref["cd_uf"].nunique() != 27 or ref["capital_co_ibge_6d"].nunique() != 27:
        raise FalhaValidacao("referência do IBGE não tem 27 UFs com uma capital cada")
    if not (ref["capital_co_ibge_6d"].str[:2] == ref["cd_uf"]).all():
        raise FalhaValidacao("capital fora da própria UF na referência")
    if set(ref["nome_regiao"]) != {"Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"}:
        raise FalhaValidacao("regiões da referência não são as 5 Grandes Regiões")
    return ref, man


# ---------------------------------------------------------------------------
# 2. Base de células e de municípios (reconstrução da auditoria 36, importada)
# ---------------------------------------------------------------------------

def montar_base(ref: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    reg: dict = {}
    c1 = A36.montar_ciclo1(reg)[0]
    c2 = A36.montar_ciclo2(reg)[0]
    c3 = A36.montar_ciclo3(reg)[0]
    ivs = A36.ler_ivs().set_index("co_ibge")
    cel = pd.concat([c1, c2, c3], ignore_index=True, sort=False)
    cel["co_ibge"] = cel["ibge_impresso"].astype(str)
    cel["ivs"] = cel["co_ibge"].map(ivs["ivs"])
    cel["nome_municipio_uf"] = cel["co_ibge"].map(ivs["nome_municipio_uf"])
    cel["vic"] = cel["vagas_imediatas"] + cel["vagas_cr"]
    cel["com_imediata_pre"] = (cel["vagas_imediatas_pre"] > 0).astype(int)
    cel["com_imediata_pipe"] = (cel["vagas_imediatas_pipe_versao"] > 0).astype(int)
    cel["preenchida"] = (cel["n_alocados"] >= 1).astype(int)
    cel["n_aloc_imed_pre"] = np.where(cel["com_imediata_pre"] == 1, cel["n_alocados"], 0)
    cel["fe_cc"] = cel["ciclo"].astype(str) + "_" + cel["cod_curso"].astype(str)
    # Capital, UF e região só pela referência do IBGE.
    caps = set(ref["capital_co_ibge_6d"])
    cel["capital"] = cel["co_ibge"].isin(caps).astype(int)
    cel["cd_uf"] = cel["co_ibge"].str[:2]
    por_uf = ref.set_index("cd_uf")
    if not cel["cd_uf"].isin(por_uf.index).all():
        raise FalhaValidacao("célula com código de UF fora da referência do IBGE")
    sigla_quadro = cel["uf"].astype(str).str.upper()
    if (sigla_quadro != cel["cd_uf"].map(por_uf["sigla_uf"])).any():
        raise FalhaValidacao("sigla da UF do quadro difere da UF do código IBGE")
    cel["regiao"] = cel["cd_uf"].map(por_uf["nome_regiao"])
    cel["nordeste"] = (cel["regiao"] == "Nordeste").astype(int)
    cel["norte"] = (cel["regiao"] == "Norte").astype(int)
    # Conferência célula a célula contra a saída versionada da auditoria 36.
    a = pd.read_csv(A36_CEL, dtype={"co_ibge": str, "chave": str})
    m = cel.merge(a, on=["ciclo", "chave"], how="outer", suffixes=("", "_a36"), indicator=True)
    if (m["_merge"] != "both").any():
        raise FalhaValidacao("células diferentes das da auditoria 36")
    for meu, dele in (("co_ibge", "co_ibge_a36"), ("ivs", "ivs_a36"), ("vagas_imediatas_pre", "vagas_imediatas_pre_a36"),
                      ("vagas_imediatas_pipe_versao", "vagas_imediatas_pipe_versao_a36"), ("vagas_cr", "vagas_cr_a36"),
                      ("n_alocados", "n_alocados_a36"), ("preenchida", "preenchida_a36"),
                      ("com_imediata_pre", "com_imediata_pre_a36"), ("com_imediata_pipe", "com_imediata_versao_pipe")):
        x, y = m[meu], m[dele]
        if meu == "co_ibge":
            dif = x.astype(str) != y.astype(str)
        else:
            dif = ~np.isclose(x.astype(float), y.astype(float), equal_nan=True)
        if dif.any():
            raise FalhaValidacao(f"{int(dif.sum())} células com {meu} diferente da auditoria 36")
    capitais_c3 = set(cel.loc[cel["tipo_municipio"].astype(str) == "CAPITAL", "co_ibge"])
    if not capitais_c3 <= caps:
        raise FalhaValidacao("município marcado CAPITAL no quadro do ciclo 3 fora da lista do IBGE")
    # Município × ciclo.
    mun = cel.groupby(["ciclo", "co_ibge"]).agg(
        n_celulas=("chave", "size"), n_cel_imediata_pre=("com_imediata_pre", "sum"), n_alocados=("n_alocados", "sum"),
        n_aloc_imed_pre=("n_aloc_imed_pre", "sum"), vic=("vic", "sum"), vi_pre=("vagas_imediatas_pre", "sum"),
        ivs=("ivs", "first"), capital=("capital", "first"), cd_uf=("cd_uf", "first"), regiao=("regiao", "first"),
        nordeste=("nordeste", "first"), norte=("norte", "first"),
        nome_municipio_uf=("nome_municipio_uf", "first")).reset_index()
    mun["taxa"] = mun["n_alocados"] / mun["vic"]
    am = pd.read_csv(A36_MUN, dtype={"co_ibge": str})
    mm = mun.merge(am, on=["ciclo", "co_ibge"], how="outer", suffixes=("", "_a36"), indicator=True)
    if (mm["_merge"] != "both").any():
        raise FalhaValidacao("municípios × ciclo diferentes dos da auditoria 36")
    for meu, dele in (("n_alocados", "n_alocados_a36"), ("vic", "vic_a36"), ("vi_pre", "vi_pre_a36"),
                      ("n_aloc_imed_pre", "n_alocados_em_imediata_pre"), ("capital", "capital_a36"),
                      ("n_cel_imediata_pre", "n_cel_imediata_pre_a36")):
        if not np.allclose(mm[meu].astype(float), mm[dele].astype(float), equal_nan=True):
            raise FalhaValidacao(f"município × ciclo com {meu} diferente da auditoria 36")
    for d in (cel, mun):
        d["s"] = np.where(d["ivs"].notna(), np.round(d["ivs"].astype(float) * 1000), np.nan)
    info = {
        "celulas_por_ciclo": {str(k): int(v) for k, v in cel.groupby("ciclo").size().items()},
        "celulas_sem_ivs": {str(k): int(v) for k, v in cel[cel["ivs"].isna()].groupby("ciclo").size().items()},
        "municipios_sem_ivs": sorted(cel.loc[cel["ivs"].isna(), "co_ibge"].unique().tolist()),
        "celulas_so_cr_pre_fora_da_H1": {str(k): int(v) for k, v in
                                         cel[cel["com_imediata_pre"] == 0].groupby("ciclo").size().items()},
        "celulas_com_imediata_pre": {str(k): int(v) for k, v in
                                     cel[cel["com_imediata_pre"] == 1].groupby("ciclo").size().items()},
        "municipios_ciclo": {str(k): int(v) for k, v in mun.groupby("ciclo").size().items()},
        "municipios_ciclo_sem_celula_com_imediata_fora_da_HI2": {
            str(k): int(v) for k, v in mun[mun["n_cel_imediata_pre"] == 0].groupby("ciclo").size().items()},
        "capitais_em_algum_quadro": int(mun.loc[mun["capital"] == 1, "co_ibge"].nunique()),
        "capitais_marcadas_CAPITAL_no_quadro_c3": int(len(capitais_c3)),
        "marcadas_no_quadro_c3_estao_na_lista_ibge": True,
        "lista_ibge_igual_a_da_auditoria_36": bool(caps == set(A36.CAPITAIS)),
        "base_igual_a_auditoria_36": {"celulas": True, "municipios_ciclo": True},
    }
    return cel[cel["ivs"].notna()].copy(), mun[mun["ivs"].notna()].copy(), info


def amostra(cel: pd.DataFrame, mun: pd.DataFrame, nome_amostra: str, unidade: str) -> pd.DataFrame:
    if unidade == "celula":
        return cel[cel["com_imediata_pre"] == 1] if nome_amostra == "H1" else cel
    return mun[mun["n_cel_imediata_pre"] > 0] if nome_amostra == "H1" else mun


# ---------------------------------------------------------------------------
# 3. Estimação
# ---------------------------------------------------------------------------

def _dummies(v: pd.Series, prefixo: str) -> tuple[list[np.ndarray], list[str]]:
    niveis = sorted(v.astype(str).unique().tolist())[1:]
    return [(v.astype(str) == n).to_numpy(float) for n in niveis], [f"{prefixo}[{n}]" for n in niveis]


def estimar(d: pd.DataFrame, y: str, corte: int, *, ajuste: str, fe: str | None = None, z: tuple = (),
            z_ciclo: str | None = None, peso: str | None = None) -> dict:
    """Uma linha do 48c: local linear h = 0,050, ciclos empilhados com parâmetros por ciclo, CR1 por município."""
    if ajuste == "sem_capitais":
        d = d[d["capital"] == 0]
    cols, nomes = [], []
    if z_ciclo is not None:
        for k in sorted(d["ciclo"].unique()):
            cols.append(((d["ciclo"] == k).to_numpy(float) * d[z_ciclo].to_numpy(float)))
            nomes.append(f"{z_ciclo}_c{k}")
    for c in z:
        cols.append(d[c].to_numpy(float))
        nomes.append(c)
    if ajuste == "capital":
        cols.append(d["capital"].to_numpy(float))
        nomes.append("capital")
    elif ajuste == "uf":
        cu, nu = _dummies(d["cd_uf"], "uf")
        cols += cu
        nomes += nu
    elif ajuste not in ("sem_ajuste", "sem_capitais"):
        raise ValueError(ajuste)
    Z = np.column_stack(cols) if cols else None
    r = L.rd_empilhado(d["s"].to_numpy(float), d[y].to_numpy(float), corte, grupo=d["ciclo"].astype(str).to_numpy(),
                       h_mil=H_MIL, cluster=d["co_ibge"].astype(str).to_numpy(),
                       efeitos_fixos=d[fe].astype(str).to_numpy() if fe else None, Z=Z, nomes_z=nomes or None,
                       peso=d[peso].to_numpy(float) if peso else None, detalhes=True)
    det = r.pop("_detalhes", None)
    r["coef_capital"] = float(det["fit"]["coef"].get("capital", np.nan)) if det and ajuste == "capital" else np.nan
    dentro = (d["s"] - corte).abs() < H_MIL
    caps = d[dentro & (d["capital"] == 1)]
    r["capitais_abaixo"] = int(caps.loc[caps["s"] <= corte, "co_ibge"].nunique())
    r["capitais_acima"] = int(caps.loc[caps["s"] > corte, "co_ibge"].nunique())
    r["ufs_na_janela"] = int(d.loc[dentro, "cd_uf"].nunique())
    return r


def _linha(bloco: str, medida: str, unidade_analise: str, amostra_: str, corte: int, ajuste: str, r: dict,
           papel: str, unidade: str, especificacao: str, efeitos_fixos: str, controle: str) -> dict:
    tau, lo, hi = r.get("tau", np.nan), r.get("ic95_inf", np.nan), r.get("ic95_sup", np.nan)
    ok = all(np.isfinite([tau, lo, hi]))
    return {
        "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO,
        "id_linha": f"{bloco}|{medida}|{unidade_analise}|{amostra_}|{corte / 1000:.3f}|{ajuste}",
        "bloco": bloco, "medida": medida, "papel": papel, "unidade_analise": unidade_analise, "amostra": amostra_,
        "corte": f"{corte / 1000:.3f}", "ajuste": ajuste, "rotulo_ajuste": ROT_AJ[ajuste],
        "especificacao": especificacao, "efeitos_fixos": efeitos_fixos, "controle": controle,
        "estimador": "local linear, kernel triangular, h = 0,050; ciclos 1-3 empilhados com intercepto e inclinacoes "
                     "por ciclo x lado e salto comum; CR1 por municipio (rdd_lib.rd_empilhado)",
        "h": H_MIL / 1000, "status": "EXECUTADO" if ok else "SEM_ESTIMATIVA",
        "tau": tau, "ep": r.get("ep", np.nan), "ic95_inf": lo, "ic95_sup": hi, "p_valor": r.get("p_valor", np.nan),
        "ic_contem_zero": (bool(lo <= 0 <= hi) if ok else None),
        "n_abaixo": r.get("n_abaixo"), "n_acima": r.get("n_acima"), "n_obs": r.get("n_obs"),
        "n_clusters": r.get("n_clusters"), "capitais_abaixo": r.get("capitais_abaixo"),
        "capitais_acima": r.get("capitais_acima"), "ufs_na_janela": r.get("ufs_na_janela"),
        "coef_capital": r.get("coef_capital", np.nan),
        "entra_bky": False, "q_bky": np.nan, "unidade": unidade,
        "covariaveis_descartadas": r.get("covariaveis_descartadas", ""),
        "nota": r.get("nota", "") or "",
    }


def estimar_linhas(cel: pd.DataFrame, mun: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for corte in CORTES:
        # C-1: balanço no corte (sem efeito fixo nem controle).
        for nome_am in ("H1", "quadro"):
            for un in ("municipio", "celula"):
                d = amostra(cel, mun, nome_am, un)
                for var, rot in VARIAVEIS_BALANCO.items():
                    r = estimar(d, var, corte, ajuste="sem_ajuste")
                    linhas.append(_linha("C-1", var, un, nome_am, corte, "sem_ajuste", r, "balanço no corte",
                                         "fracao (x100 = p.p.)", f"{rot}; {AMOSTRAS[nome_am]}", "", ""))
        # H1 (base e C-2 a C-4) e medidas antigas (C-5).
        for med in MEDIDAS_H1 + MEDIDAS_ANTIGAS:
            spec = MEDIDAS[med]
            d = amostra(cel, mun, spec["amostra"], spec["unidade_analise"])
            for aj in AJUSTES:
                r = estimar(d, spec["y"], corte, ajuste=aj, fe=spec["fe"], z=spec["z"], z_ciclo=spec["z_ciclo"],
                            peso=spec["peso"])
                if med in MEDIDAS_H1:
                    bloco = "base" if aj == "sem_ajuste" else BLOCO_AJ[aj]
                else:
                    bloco = "C-5"
                fe = ("curso x ciclo" if spec["fe"] else "") + (" + UF" if aj == "uf" else "")
                ctrl = ";".join(([f"{spec['z_ciclo']} por ciclo"] if spec["z_ciclo"] else []) + list(spec["z"])
                                + (["capital"] if aj == "capital" else []))
                linhas.append(_linha(bloco, med, spec["unidade_analise"], spec["amostra"], corte, aj, r, spec["papel"],
                                     spec["unidade"], spec["especificacao"], fe.strip(" +"), ctrl))
    est = pd.DataFrame(linhas)
    # BKY entre as linhas C-2 a C-4 (H1 com ajuste).
    m = est["bloco"].isin(["C-2", "C-3", "C-4"]) & (est["status"] == "EXECUTADO")
    est.loc[m, "entra_bky"] = True
    est.loc[m, "q_bky"] = L.qvalores_bky(est.loc[m, "p_valor"].to_numpy(float))
    if int(m.sum()) != 12:
        raise FalhaValidacao(f"esperadas 12 linhas no BKY (HI-1/HI-2 x 3 ajustes x 2 cortes), achadas {int(m.sum())}")
    return est


# ---------------------------------------------------------------------------
# 4. Conferências
# ---------------------------------------------------------------------------

TOL = 1e-8


def _um(est: pd.DataFrame, **f) -> pd.Series:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        m &= (est[k].astype(str) == str(v)).to_numpy()
    s = est[m]
    if len(s) != 1:
        raise FalhaValidacao(f"esperada 1 linha para {f}, achadas {len(s)}")
    return s.iloc[0]


def conferir_a36(est: pd.DataFrame) -> list[dict]:
    """Linhas que a auditoria 36 já calculou com o estimador próprio (a36_estimador.rd) no empilhado."""
    a = pd.read_csv(A36_EST, dtype={"ciclo": str})
    a = a[a["ciclo"] == "1+2+3"]
    A3o = "A3_pipeline (>=1 alocado; c1 = confirmado)"
    pares = [
        ("HI-1", "sem_ajuste", "celula", A3o, "só células com vaga imediata pré-alocação (c2 = 13/02); FE curso x ciclo"),
        ("A3", "sem_ajuste", "celula", A3o, "FE curso x ciclo + tipo de vaga (versão do pipeline: c2 = 19/03)"),
        ("A3-pre", "sem_ajuste", "celula", A3o, "FE curso x ciclo + tipo de vaga pré-alocação (c2 = 13/02)"),
        ("A3", "capital", "celula", A3o, "FE do pipeline + dummy de capital"),
        ("A3", "sem_capitais", "celula", A3o, "sem capitais; FE do pipeline"),
        ("N1", "sem_ajuste", "municipio", "N1 com controle VIC (S-a/Q1)", "pipeline"),
        ("N1", "capital", "municipio", "N1 com controle VIC (S-a/Q1)", "com dummy de capital"),
        ("N1", "sem_capitais", "municipio", "N1 com controle VIC (S-a/Q1)", "sem capitais"),
        ("taxa", "sem_ajuste", "municipio", "taxa N1/VIC ponderada (Q2)", "pipeline"),
        ("taxa", "capital", "municipio", "taxa N1/VIC ponderada (Q2)", "com dummy de capital"),
        ("taxa", "sem_capitais", "municipio", "taxa N1/VIC ponderada (Q2)", "sem capitais"),
    ]
    out = []
    for corte in CORTES:
        for med, aj, un, oc, var in pares:
            meu = _um(est, medida=med, ajuste=aj, corte=f"{corte / 1000:.3f}", bloco="base" if med == "HI-1" else "C-5")
            dele = a[(a["unidade"] == un) & (a["outcome"] == oc) & (a["variante"] == var) & (a["corte"] == corte)]
            if len(dele) != 1:
                continue      # a auditoria 36 não calculou essa linha nesse corte
            out.append({"linha": f"{med} {ROT_AJ[aj]}", "corte": f"{corte / 1000:.3f}",
                        "aqui": float(meu["tau"]), "auditoria_36": float(dele["salto"].iloc[0]),
                        "dif_tau": abs(float(meu["tau"]) - float(dele["salto"].iloc[0])),
                        "dif_ep": abs(float(meu["ep"]) - float(dele["ep"].iloc[0]))})
        for un, var in (("municipio", "município é capital"), ("celula", "célula em capital")):
            meu = _um(est, bloco="C-1", medida="capital", unidade_analise=un, amostra="quadro",
                      corte=f"{corte / 1000:.3f}")
            dele = a[(a["unidade"] == un) & (a["outcome"] == "composicao") & (a["variante"] == var)
                     & (a["corte"] == corte)]
            out.append({"linha": f"C-1 capital por {un} (quadro inteiro)", "corte": f"{corte / 1000:.3f}",
                        "aqui": float(meu["tau"]), "auditoria_36": float(dele["salto"].iloc[0]),
                        "dif_tau": abs(float(meu["tau"]) - float(dele["salto"].iloc[0])),
                        "dif_ep": abs(float(meu["ep"]) - float(dele["ep"].iloc[0]))})
    ruins = [x for x in out if x["dif_tau"] > TOL or x["dif_ep"] > TOL]
    if ruins:
        raise FalhaValidacao(f"linhas diferentes da auditoria 36: {ruins}")
    return out


def conferir_pipeline(est: pd.DataFrame) -> list[dict]:
    """A3 (NA_, script 24), N1 S-a e taxa S-e (N_, script 23), ciclos 1-3 empilhados, sem ajuste."""
    na = pd.read_csv(NA_EST, dtype=str)
    n = pd.read_csv(N_EST, dtype=str)
    out = []
    for corte in CORTES:
        cs = f"{corte / 1000:.3f}"
        alvos = [
            ("A3", na[(na["outcome_id"] == "A3_PREENCHIDA") & (na["variante"] == "principal")
                      & (na["populacao"] == "V1+V2+V3 (celulas)") & (na["corte"] == cs)], "NA_estimativas.csv"),
            ("N1", n[(n["especificacao"] == "S-a") & (n["outcome_id"] == "N1") & (n["variante"] == "principal")
                     & (n["populacao"] == "V1+V2+V3") & (n["corte"] == cs)], "N_estimativas.csv (S-a)"),
            ("taxa", n[(n["especificacao"] == "S-e") & (n["outcome_id"] == "N1") & (n["populacao"] == "V1+V2+V3")
                       & (n["corte"] == cs)], "N_estimativas.csv (S-e)"),
        ]
        for med, g, arq in alvos:
            if len(g) != 1:
                raise FalhaValidacao(f"linha gravada do pipeline não encontrada: {med} {cs}")
            meu = _um(est, bloco="C-5", medida=med, ajuste="sem_ajuste", corte=cs)
            d_tau = abs(float(meu["tau"]) - float(g["tau"].iloc[0]))
            d_ep = abs(float(meu["ep"]) - float(g["ep"].iloc[0]))
            if d_tau > TOL or d_ep > TOL:
                raise FalhaValidacao(f"{med} {cs} difere do pipeline ({arq}): {d_tau}, {d_ep}")
            out.append({"linha": MEDIDAS[med]["rotulo"], "corte": cs, "arquivo": arq, "aqui": float(meu["tau"]),
                        "gravado": float(g["tau"].iloc[0]), "dif_tau": d_tau, "dif_ep": d_ep})
    return out


def conferir_hi(est: pd.DataFrame) -> dict:
    """HI-1 e HI-2 sem ajuste contra HI_estimativas.csv (script 40, adendo 48b), se ele já existir no branch."""
    if not HI_EST.exists():
        return {"status": "PENDENTE", "arquivo": rotulo(HI_EST),
                "motivo": "HI_estimativas.csv (script 40) não estava no branch nesta execução"}
    hi = pd.read_csv(HI_EST, dtype=str)
    precisa = {"linha", "outcome", "ciclo", "corte", "variante", "versao_quadro_c2", "tau", "ep", "h"}
    if not precisa <= set(hi.columns):
        return {"status": "PENDENTE", "arquivo": rotulo(HI_EST), "sha256": sha256(HI_EST),
                "motivo": f"colunas esperadas ausentes: {sorted(precisa - set(hi.columns))}"}
    linhas = []
    for corte in CORTES:
        cs = f"{corte / 1000:.3f}"
        for med in MEDIDAS_H1:
            g = hi[(hi["linha"] == med) & (hi["outcome"] == med) & (hi["ciclo"] == "1+2+3") & (hi["corte"] == cs)
                   & (hi["variante"] == "principal") & (hi["versao_quadro_c2"] == "13fev")
                   & (pd.to_numeric(hi["h"]) == H_MIL / 1000)]
            if len(g) != 1:
                return {"status": "PENDENTE", "arquivo": rotulo(HI_EST), "sha256": sha256(HI_EST),
                        "motivo": f"linha principal de {med} em {cs} não identificada ({len(g)} candidatas)"}
            meu = _um(est, bloco="base", medida=med, corte=cs)
            linhas.append({"medida": med, "corte": cs, "aqui_tau": float(meu["tau"]), "HI_tau": float(g["tau"].iloc[0]),
                           "aqui_ep": float(meu["ep"]), "HI_ep": float(g["ep"].iloc[0]),
                           "HI_p_holm": float(g["p_holm"].iloc[0]) if "p_holm" in g.columns else float("nan"),
                           "dif_tau": abs(float(meu["tau"]) - float(g["tau"].iloc[0])),
                           "dif_ep": abs(float(meu["ep"]) - float(g["ep"].iloc[0]))})
    if any(x["dif_tau"] > TOL or x["dif_ep"] > TOL for x in linhas):
        raise FalhaValidacao(f"HI-1/HI-2 sem ajuste diferem de HI_estimativas.csv: {linhas}")
    return {"status": "CONFERIDO", "arquivo": rotulo(HI_EST), "sha256": sha256(HI_EST), "tolerancia": TOL,
            "linhas": linhas}


# ---------------------------------------------------------------------------
# 5. Leitura pré-registrada (48c, §2) e descritivos da janela
# ---------------------------------------------------------------------------

LEITURA_SIM = ("a queda em 0,300 anda junto com a presença de capitais (ou região) logo abaixo do corte, que é "
               "desbalanceamento de poucos municípios grandes, e não com a bolsa")
LEITURA_NAO = "relatar como está"


def leitura_preregistrada(est: pd.DataFrame) -> dict:
    """Regra do 48c, §2, aplicada a cada corte.

    - "C-1 mostra salto em capital ou região": alguma linha de balanço do C-1 na amostra da H1 (capital, Nordeste ou
      Norte; por município ou por célula) com IC 95% que exclui zero.
    - "C-2 a C-4 levam o salto da H1 a um IC que contém zero": entre HI-1 e HI-2, as linhas cujo IC sem ajuste exclui
      zero (a queda a explicar) passam a ter IC que contém zero nos três ajustes. Sem nenhuma linha com IC que exclui
      zero sem ajuste, não há salto a levar e vale "caso contrário".
    """
    out = {}
    for corte in CORTES:
        cs = f"{corte / 1000:.3f}"
        bal = est[(est["bloco"] == "C-1") & (est["amostra"] == "H1") & (est["corte"] == cs)]
        com_salto = bal[bal["ic_contem_zero"] == False]  # noqa: E712
        c1 = bool(len(com_salto))
        por_medida = {}
        for med in MEDIDAS_H1:
            b = _um(est, bloco="base", medida=med, corte=cs)
            ajs = {aj: bool(_um(est, bloco=BLOCO_AJ[aj], medida=med, corte=cs)["ic_contem_zero"])
                   for aj in ("capital", "uf", "sem_capitais")}
            por_medida[med] = {"tau_sem_ajuste": float(b["tau"]), "ic_sem_ajuste_exclui_zero": not bool(b["ic_contem_zero"]),
                               "ic_contem_zero_por_ajuste": ajs, "ajustes_que_levam_a_zero": [a for a, v in ajs.items() if v],
                               "levam_nos_tres": all(ajs.values())}
        a_levar = [m for m, v in por_medida.items() if v["ic_sem_ajuste_exclui_zero"]]
        c2 = bool(a_levar) and all(por_medida[m]["levam_nos_tres"] for m in a_levar)
        if c1 and c2:
            leitura, motivo = "ANDA_JUNTO_COM_CAPITAIS_OU_REGIAO", "as duas condições do §2 valem"
        else:
            motivos = []
            if not c1:
                motivos.append("C-1 não mostra salto em capital nem em região na amostra da H1")
            if not a_levar:
                motivos.append("nenhuma linha da H1 (HI-1, HI-2) tem IC que exclui zero sem ajuste: não há salto a levar")
            elif not c2:
                motivos.append("algum ajuste mantém o IC da H1 sem conter zero")
            leitura, motivo = "RELATAR_COMO_ESTA", "; ".join(motivos)
        out[cs] = {"c1_salto_em_capital_ou_regiao": c1,
                   "c1_linhas_com_salto": [f"{VARIAVEIS_BALANCO[r['medida']]} "
                                           f"({'município' if r['unidade_analise'] == 'municipio' else 'célula'})"
                                           for _, r in com_salto.iterrows()],
                   "linhas_H1_com_queda_a_levar": a_levar, "c2_ajustes_levam_a_ic_com_zero": c2,
                   "por_medida": por_medida, "leitura": leitura, "motivo": motivo,
                   "texto": LEITURA_SIM if leitura == "ANDA_JUNTO_COM_CAPITAIS_OU_REGIAO" else LEITURA_NAO}
    return out


def comparacao_antigas(est: pd.DataFrame) -> dict:
    """C-5, só para comparação (fora da leitura e do BKY): o IC sem ajuste exclui zero? E com cada ajuste?"""
    out = {}
    for corte in CORTES:
        cs = f"{corte / 1000:.3f}"
        out[cs] = {}
        for med in MEDIDAS_ANTIGAS:
            out[cs][med] = {aj: {"tau": float(_um(est, bloco="C-5", medida=med, ajuste=aj, corte=cs)["tau"]),
                                 "ic_contem_zero": bool(_um(est, bloco="C-5", medida=med, ajuste=aj, corte=cs)[
                                     "ic_contem_zero"])} for aj in AJUSTES}
    return out


def capitais_na_janela(mun: pd.DataFrame, cel: pd.DataFrame) -> list[dict]:
    """Capitais com IVS a menos de 0,050 de cada corte (quadro inteiro), com células totais e com vaga imediata."""
    out = []
    for corte in CORTES:
        m = mun[((mun["s"] - corte).abs() < H_MIL) & (mun["capital"] == 1)]
        for ib, g in m.groupby("co_ibge"):
            s = float(g["s"].iloc[0])
            out.append({"corte": f"{corte / 1000:.3f}", "co_ibge": ib, "municipio": g["nome_municipio_uf"].iloc[0],
                        "regiao": g["regiao"].iloc[0], "ivs": s / 1000, "distancia_ao_corte": (s - corte) / 1000,
                        "distancia_mil": int(s - corte),
                        "a_menos_de_0010": bool(abs(s - corte) < 10),
                        "lado": "abaixo (bolsa menor)" if s <= corte else "acima (bolsa maior)",
                        "ciclos": ",".join(str(int(k)) for k in sorted(g["ciclo"])),
                        "celulas": int(g["n_celulas"].sum()), "celulas_com_vaga_imediata": int(g["n_cel_imediata_pre"].sum()),
                        "peso_kernel": 1 - abs(s - corte) / H_MIL})
    return sorted(out, key=lambda x: (x["corte"], x["ivs"]))


JANELA_ESTREITA_MIL = 10   # 0,010, como as janelas do pipeline; só para ler o C-1 (auditoria 42, achado 3)


def composicao_janela(cel: pd.DataFrame, mun: pd.DataFrame) -> list[dict]:
    """Médias cruas por lado (sem reta), na janela de 0,050 e na de 0,010: só descritivo, para ler o C-1."""
    out = []
    for jan in (H_MIL, JANELA_ESTREITA_MIL):
        for corte in CORTES:
            for nome_am in ("H1", "quadro"):
                for un in ("municipio", "celula"):
                    d = amostra(cel, mun, nome_am, un)
                    d = d[(d["s"] - corte).abs() < jan]
                    for lado, dd in (("abaixo", d[d["s"] <= corte]), ("acima", d[d["s"] > corte])):
                        out.append({"janela_mil": int(jan), "corte": f"{corte / 1000:.3f}", "amostra": nome_am,
                                    "unidade_analise": un, "lado": lado,
                                    "linhas": int(len(dd)), "municipios": int(dd["co_ibge"].nunique()),
                                    "frac_capital": float(dd["capital"].mean()),
                                    "frac_nordeste": float(dd["nordeste"].mean()),
                                    "frac_norte": float(dd["norte"].mean()),
                                    "nordeste_capital": int(((dd["nordeste"] == 1) & (dd["capital"] == 1)).sum()),
                                    "nordeste_total": int((dd["nordeste"] == 1).sum())})
    return out


def estimar_tudo() -> tuple[pd.DataFrame, dict]:
    ref, man = carregar_referencias()
    cel, mun, info = montar_base(ref)
    est = estimar_linhas(cel, mun)
    extras = {
        "info_dados": info,
        "referencia_ibge": {"arquivo": rotulo(REF_CSV), "sha256": sha256(REF_CSV), "manifesto": rotulo(REF_MANIFESTO),
                            "sha256_manifesto": sha256(REF_MANIFESTO), "fontes": man["fontes"],
                            "capitais": ref[["capital_co_ibge_6d", "capital_nome", "sigla_uf", "nome_regiao"]]
                            .to_dict(orient="records")},
        "conferencia_auditoria_36": conferir_a36(est),
        "conferencia_pipeline": conferir_pipeline(est),
        "conferencia_HI": conferir_hi(est),
        "leitura": leitura_preregistrada(est),
        "comparacao_medidas_antigas": comparacao_antigas(est),
        "capitais_na_janela": capitais_na_janela(mun, cel),
        "composicao_janela": composicao_janela(cel, mun),
    }
    return est, extras


# ---------------------------------------------------------------------------
# 6. Formatação
# ---------------------------------------------------------------------------

def _num(v, casas=1, sinal=True) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if not math.isfinite(v):
        return "—"
    s = f"{v:+.{casas}f}" if sinal else f"{v:.{casas}f}"
    if sinal and float(s) == 0:
        s = f"{0:.{casas}f}"
    return s.replace(".", ",").replace("-", "−")


def _escala(r) -> float:
    return 100.0 if str(r["unidade"]).startswith("fracao") else 1.0


def _casas(r) -> int:
    return 1 if _escala(r) == 100.0 else 2


def _v(r, col="tau") -> str:
    return _num(float(r[col]) * _escala(r), _casas(r))


def _ic(r) -> str:
    return f"[{_v(r, 'ic95_inf')}; {_v(r, 'ic95_sup')}]"


def _p(v) -> str:
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "—"
    if not math.isfinite(v):
        return "—"
    return "< 0,001" if v < 0.001 else f"{v:.3f}".replace(".", ",")


def _un(r) -> str:
    return "p.p." if _escala(r) == 100.0 else "médicos"


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    return "\n".join(["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
                     + ["| " + " | ".join(str(c) for c in ln) + " |" for ln in linhas])


def _bloco(nome: str, corpo: str) -> str:
    return f"<!-- HC:{nome}:inicio -->\n{corpo.strip()}\n<!-- HC:{nome}:fim -->"


def _corte_txt(cs: str) -> str:
    return cs.replace(".", ",")


# ---------------------------------------------------------------------------
# 7. Figuras (legíveis em slide; "Como ler" vai na imagem, no doc e no resumo)
# ---------------------------------------------------------------------------

COR_BASE = "#eb6834"
COR_AJ = {"capital": "#2a78d6", "uf": "#1f9e74", "sem_capitais": "#8a5cc2"}
CINZA = "#a3a29c"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
SUPERF = "#fcfcfb"
COMO_LER = {
    "HC_capitais_no_corte.png": "Cada ponto é uma capital com IVS a menos de 0,050 do corte (todas as que têm célula no "
                                "quadro de algum ciclo). À esquerda da linha tracejada a bolsa é menor; à direita, maior. "
                                "O tamanho do ponto é o número de células da capital nos três ciclos. Quanto mais perto "
                                "da linha, mais a capital pesa na estimativa do salto.",
    "HC_balanco_corte.png": "Cada ponto é o salto, no corte, da fração de municípios (ou de células) que são capital, "
                            "do Nordeste ou do Norte, na amostra da H1. Traço = IC 95%. Num corte bem balanceado esses "
                            "saltos ficam perto de zero; um ponto à esquerda de zero quer dizer que logo acima do corte "
                            "(bolsa maior) há menos daquele grupo do que logo abaixo.",
    "HC_salto_H1_ajustes.png": "Cada ponto é o salto da H1 no corte: o lado de bolsa maior menos o de bolsa menor. "
                               "Laranja: sem ajuste (48b). Azul: comparando só municípios iguais em ser ou não capital. "
                               "Verde: comparando só municípios da mesma UF. Roxo: tirando as capitais. Traço = IC 95%; "
                               "traço cruzando o zero quer dizer que a diferença não se distingue de zero.",
    "HC_salto_medidas_antigas.png": "Igual à figura anterior, para as medidas antigas (que misturam vaga imediata e "
                                    "cadastro reserva), só para comparação: A3 (célula aberta preenchida), N1 com "
                                    "controle (médicos por município) e taxa por vaga oferecida.",
}
DETALHE_FIG = {
    "HC_capitais_no_corte.png": "Municípios × ciclo do quadro (a36), capitais pela lista do IBGE (Localidades 2022); "
                                "IVS 2010 oficial (a08). Peso do kernel triangular = 1 − |IVS − corte| / 0,050.",
    "HC_balanco_corte.png": "Linhas C-1 com amostra = H1 de HC_estimativas.csv (local linear, h = 0,050, ciclos "
                            "empilhados, CR1 por município); em p.p.",
    "HC_salto_H1_ajustes.png": "Linhas base, C-2, C-3 e C-4 de HC_estimativas.csv; HI-1 em p.p., HI-2 em médicos "
                               "alocados por município.",
    "HC_salto_medidas_antigas.png": "Linhas C-5 de HC_estimativas.csv (A3 com o tipo de vaga do pipeline, N1 S-a e "
                                    "taxa S-e); fora do BKY e da leitura pré-registrada.",
}


def _rodape(fig, nome: str, largura: int) -> None:
    fig.text(0.012, 0.012, "\n".join(textwrap.wrap("Como ler: " + COMO_LER[nome], largura)), fontsize=13,
             color=TINTA, va="bottom", ha="left")


def _painel_saltos(ax, est, med, cs, bloco_base, mostrar_rotulos):
    from matplotlib.ticker import FuncFormatter
    ys = np.arange(len(AJUSTES))[::-1].astype(float)
    ax.axvline(0, color=TINTA_2, lw=1)
    for y, aj in zip(ys, AJUSTES):
        bloco = bloco_base if bloco_base == "C-5" else ("base" if aj == "sem_ajuste" else BLOCO_AJ[aj])
        r = _um(est, bloco=bloco, medida=med, ajuste=aj, corte=cs)
        k = _escala(r)
        t, lo, hi = float(r["tau"]) * k, float(r["ic95_inf"]) * k, float(r["ic95_sup"]) * k
        cor = COR_BASE if aj == "sem_ajuste" else COR_AJ[aj]
        ax.plot([lo, hi], [y, y], color=cor, lw=3, solid_capstyle="butt")
        ax.plot(t, y, "o", color=cor, markersize=11, markeredgecolor=SUPERF, markeredgewidth=1.2)
        ax.text(hi, y + 0.22, f" {_num(t, _casas(r))}", color=TINTA, fontsize=12, va="bottom", ha="right")
    ax.set_yticks(ys)
    ax.set_yticklabels([ROT_AJ_CURTO[a] for a in AJUSTES] if mostrar_rotulos else [])
    ax.set_ylim(-0.6, len(AJUSTES) - 0.3)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−")))
    ax.spines[["top", "right"]].set_visible(False)


def gerar_figuras(est: pd.DataFrame, extras: dict, dir_fig: Path) -> list[dict]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FuncFormatter
    dir_fig.mkdir(parents=True, exist_ok=True)
    for antigo in dir_fig.glob("*.png"):
        antigo.unlink()
    plt.rcParams.update({"font.size": 14, "axes.titlesize": 16, "axes.labelsize": 14, "xtick.labelsize": 13,
                         "ytick.labelsize": 13, "axes.edgecolor": TINTA_2, "axes.labelcolor": TINTA,
                         "text.color": TINTA, "xtick.color": TINTA_2, "ytick.color": TINTA_2,
                         "figure.facecolor": SUPERF, "axes.facecolor": SUPERF, "savefig.facecolor": SUPERF,
                         "svg.hashsalt": "hc", "path.simplify": False})
    virgula = FuncFormatter(lambda v, _: f"{v:.2f}".replace(".", ","))
    feitas = []
    cortes_s = [f"{c / 1000:.3f}" for c in CORTES]
    # (1) capitais perto de cada corte
    nome = "HC_capitais_no_corte.png"
    fig, eixos = plt.subplots(1, 2, figsize=(18, 7.6))
    caps = pd.DataFrame(extras["capitais_na_janela"])
    for ax, cs in zip(eixos, cortes_s):
        c = float(cs)
        g = caps[caps["corte"] == cs].sort_values("ivs").reset_index(drop=True)
        ax.axvline(c, color=TINTA_2, lw=1.4, ls="--")
        ax.axvspan(c - H_MIL / 1000, c, color="#f4efe9", zorder=0)
        niveis = [0.0, 1.0, 2.0, 3.0]
        for i, r in g.iterrows():
            y = niveis[i % len(niveis)]
            cor = COR_BASE if r["distancia_mil"] <= 0 else COR_AJ["capital"]
            ax.scatter(r["ivs"], y, s=40 + 6 * r["celulas"], color=cor, alpha=0.85, edgecolors=SUPERF, lw=1, zorder=3)
            ax.text(r["ivs"], y + 0.32, str(r["municipio"]).rsplit(" (", 1)[0], ha="center", va="bottom", fontsize=12)
        ab = int((g["distancia_mil"] <= 0).sum())
        ac = int((g["distancia_mil"] > 0).sum())
        ax.set_title(f"Corte {_corte_txt(cs)}: {ab} capitais abaixo, {ac} acima (janela de 0,050)")
        ax.set_xlim(c - H_MIL / 1000 - 0.002, c + H_MIL / 1000 + 0.002)
        ax.set_ylim(-0.8, 4.4)
        ax.set_yticks([])
        ax.xaxis.set_major_formatter(virgula)
        ax.set_xlabel("IVS 2010")
        ax.text(c - 0.001, 4.25, "bolsa menor ←", ha="right", va="top", fontsize=13, color=TINTA_2)
        ax.text(c + 0.001, 4.25, "→ bolsa maior", ha="left", va="top", fontsize=13, color=TINTA_2)
        ax.spines[["top", "right", "left"]].set_visible(False)
    fig.suptitle("Onde estão as capitais perto dos cortes da bolsa", fontsize=19, y=0.99)
    fig.tight_layout(rect=(0, 0.11, 1, 0.95))
    _rodape(fig, nome, 170)
    fig.savefig(dir_fig / nome, dpi=150)
    plt.close(fig)
    feitas.append(nome)
    # (2) balanço no corte (amostra da H1)
    nome = "HC_balanco_corte.png"
    fig, eixos = plt.subplots(1, 2, figsize=(18, 7.8), sharey=True)
    linhas_bal = [(v, un) for v in VARIAVEIS_BALANCO for un in ("municipio", "celula")]
    rot_bal = [f"{VARIAVEIS_BALANCO[v]} ({'município' if un == 'municipio' else 'célula'})" for v, un in linhas_bal]
    ys = np.arange(len(linhas_bal))[::-1].astype(float)
    for ax, cs in zip(eixos, cortes_s):
        ax.axvline(0, color=TINTA_2, lw=1)
        for y, (v, un) in zip(ys, linhas_bal):
            r = _um(est, bloco="C-1", medida=v, unidade_analise=un, amostra="H1", corte=cs)
            t, lo, hi = float(r["tau"]) * 100, float(r["ic95_inf"]) * 100, float(r["ic95_sup"]) * 100
            cor = COR_BASE if not r["ic_contem_zero"] else CINZA
            ax.plot([lo, hi], [y, y], color=cor, lw=3, solid_capstyle="butt")
            ax.plot(t, y, "o", color=cor, markersize=11, markeredgecolor=SUPERF)
            ax.text(t, y + 0.2, f"{_num(t, 1)}", ha="center", va="bottom", fontsize=12)
        ax.set_yticks(ys)
        ax.set_yticklabels(rot_bal)
        ax.set_title(f"Corte {_corte_txt(cs)}")
        ax.set_xlabel("salto no corte (p.p.): lado de bolsa maior − lado de bolsa menor")
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−")))
        ax.spines[["top", "right"]].set_visible(False)
    leg = [Line2D([], [], color=COR_BASE, lw=3, marker="o", label="IC 95% exclui zero"),
           Line2D([], [], color=CINZA, lw=3, marker="o", label="IC 95% contém zero")]
    fig.legend(handles=leg, loc="upper center", ncol=2, frameon=False, fontsize=13, bbox_to_anchor=(0.5, 0.94))
    fig.suptitle("Balanço no corte: capitais e região dos dois lados (amostra da H1)", fontsize=19, y=0.99)
    fig.tight_layout(rect=(0, 0.1, 1, 0.9))
    _rodape(fig, nome, 170)
    fig.savefig(dir_fig / nome, dpi=150)
    plt.close(fig)
    feitas.append(nome)
    # (3) e (4) saltos sem e com ajuste
    for nome, meds, bloco, titulo, tam in (
            ("HC_salto_H1_ajustes.png", MEDIDAS_H1, "base",
             "H1 (vagas imediatas, 48b): o salto sem e com cada ajuste", (18, 9.4)),
            ("HC_salto_medidas_antigas.png", ("A3", "N1", "taxa"), "C-5",
             "Medidas antigas: o salto sem e com cada ajuste (só comparação)", (18, 12.4))):
        fig, eixos = plt.subplots(len(meds), 2, figsize=tam, squeeze=False)
        for i, med in enumerate(meds):
            for j, cs in enumerate(cortes_s):
                ax = eixos[i][j]
                _painel_saltos(ax, est, med, cs, bloco, j == 0)
                r0 = _um(est, bloco="base" if bloco == "base" else "C-5", medida=med, ajuste="sem_ajuste", corte=cs)
                ax.set_title(f"{MEDIDAS[med]['rotulo'].split(':')[0]} — corte {_corte_txt(cs)}", fontsize=15)
                ax.set_xlabel("salto (p.p.)" if _escala(r0) == 100.0 else "salto (médicos alocados por município)")
        fig.suptitle(titulo, fontsize=19, y=0.995)
        fig.tight_layout(rect=(0, 0.08, 1, 0.96))
        _rodape(fig, nome, 175)
        fig.savefig(dir_fig / nome, dpi=150)
        plt.close(fig)
        feitas.append(nome)
    return [{"arquivo": rotulo(dir_fig / f), "como_ler": COMO_LER[f], "detalhe_tecnico": DETALHE_FIG[f]}
            for f in feitas]


# ---------------------------------------------------------------------------
# 8. Documento 57o (gerado inteiro a partir das saídas)
# ---------------------------------------------------------------------------

def _perto(resumo: dict, cs: str) -> list[dict]:
    """Capitais a menos de 0,010 do corte (−0,010 < IVS − corte < 0,010, como as janelas do pipeline)."""
    return [c for c in resumo["capitais_na_janela"] if c["corte"] == cs and c["a_menos_de_0010"]]


def _nome(c: dict) -> str:
    return c["municipio"].rsplit(" (", 1)[0]


def _diferenca_txt(r, grupo: str) -> str:
    """Salto de um indicador de balanço em palavras: 'X p.p. menor/maior logo acima do corte (IC ...)'."""
    t = float(r["tau"]) * 100
    sentido = "menor" if t < 0 else "maior"
    return (f"a fração de {grupo} é {_num(abs(t), 1, False)} p.p. {sentido} logo acima do corte (bolsa maior) do que "
            f"logo abaixo (IC {_ic(r)})")


def resposta_curta(est: pd.DataFrame, resumo: dict) -> str:
    le = resumo["leitura"]
    l3, l4 = le["0.300"], le["0.400"]
    b = {(m, aj): _um(est, bloco=("base" if aj == "sem_ajuste" else BLOCO_AJ[aj]), medida=m, corte="0.300")
         for m in MEDIDAS_H1 for aj in AJUSTES}
    c1 = {(v, un): _um(est, bloco="C-1", medida=v, unidade_analise=un, amostra="H1", corte="0.300")
          for v in VARIAVEIS_BALANCO for un in ("municipio", "celula")}
    perto = _perto(resumo, "0.300")
    ab = [c for c in resumo["capitais_na_janela"] if c["corte"] == "0.300" and c["distancia_mil"] <= 0]
    ac = [c for c in resumo["capitais_na_janela"] if c["corte"] == "0.300" and c["distancia_mil"] > 0]
    nomes_perto = ", ".join(f"{_nome(c)} ({_num(c['ivs'], 3, False)})" for c in perto)
    lado_perto = ("todas abaixo" if perto and all(c["distancia_mil"] <= 0 for c in perto) else
                  ("todas acima" if perto and all(c["distancia_mil"] > 0 for c in perto) else "dos dois lados"))
    comp = pd.DataFrame(resumo["composicao_janela"])
    cj = comp[(comp["corte"] == "0.300") & (comp["amostra"] == "H1") & (comp["unidade_analise"] == "municipio")
              & (comp["janela_mil"] == H_MIL)]
    cj_ab, cj_ac = cj[cj["lado"] == "abaixo"].iloc[0], cj[cj["lado"] == "acima"].iloc[0]
    ce = comp[(comp["corte"] == "0.300") & (comp["amostra"] == "H1") & (comp["unidade_analise"] == "municipio")
              & (comp["janela_mil"] == JANELA_ESTREITA_MIL)]
    ce_ab, ce_ac = ce[ce["lado"] == "abaixo"].iloc[0], ce[ce["lado"] == "acima"].iloc[0]
    linhas = []
    if l3["leitura"] == "ANDA_JUNTO_COM_CAPITAIS_OU_REGIAO":
        linhas.append(f"**Sim, pela leitura pré-registrada:** {LEITURA_SIM}. É robustez pós-resultado, com poucos "
                      "municípios perto do corte. Na regra, \"e não com a bolsa\" quer dizer que o corte não separa a "
                      "bolsa da composição de capitais; não quer dizer que a bolsa não tenha efeito.")
    else:
        linhas.append(f"**Pela leitura pré-registrada, em 0,300: {LEITURA_NAO}** ({l3['motivo']}).")
    linhas.append("")
    linhas.append(
        f"- **Capitais no corte.** Na janela de 0,050 em torno de 0,300 há {len(ab)} capitais abaixo (bolsa menor) e "
        f"{len(ac)} acima. A menos de 0,010 do corte: {nomes_perto or 'nenhuma'}"
        f"{', ' + lado_perto if perto else ''}. Na amostra da H1, "
        f"{_diferenca_txt(c1[('capital', 'municipio')], 'municípios que são capital')}; por célula, "
        f"{_diferenca_txt(c1[('capital', 'celula')], 'células em capital')}. Ser capital é anterior à bolsa: o corte "
        "não é balanceado em capital.")
    reg = []
    for v, nome in (("nordeste", "Nordeste"), ("norte", "Norte")):
        rm = c1[(v, "municipio")]
        if rm["ic_contem_zero"]:
            reg.append(f"{nome}: o salto no corte tem IC que contém zero ({_v(rm)} p.p. por município, IC {_ic(rm)})")
        else:
            txt = (f"{nome}: {_diferenca_txt(rm, 'municípios do ' + nome)}, embora na janela inteira de 0,050 "
                   f"sejam {_num(cj_ab['frac_' + v] * 100, 0, False)}% abaixo e "
                   f"{_num(cj_ac['frac_' + v] * 100, 0, False)}% acima (sem reta). A reta local pesa os municípios "
                   f"colados no corte: a menos de 0,010, são {_num(ce_ab['frac_' + v] * 100, 0, False)}% abaixo "
                   f"({int(ce_ab['linhas'])} municípios × ciclo) e {_num(ce_ac['frac_' + v] * 100, 0, False)}% acima "
                   f"({int(ce_ac['linhas'])})")
            if v == "nordeste":
                txt += (f"; dos {int(ce_ab['nordeste_total'])} municípios × ciclo do Nordeste logo abaixo, "
                        f"{int(ce_ab['nordeste_capital'])} são capital, então o desbalanceamento de região não se "
                        "resume às capitais")
            reg.append(txt)
    linhas.append("- **Região.** " + "; ".join(reg) + ".")
    for m in MEDIDAS_H1:
        r0 = b[(m, "sem_ajuste")]
        partes = "; ".join(f"{ROT_AJ_CURTO[aj]} {_v(b[(m, aj)])} {_ic(b[(m, aj)])}" for aj in AJUSTES[1:])
        linhas.append(f"- **{MEDIDAS[m]['rotulo']}** (salto em {_un(r0)}): sem ajuste {_v(r0)} {_ic(r0)}; {partes}.")
    linhas.append(f"- **0,400:** {l4['texto']} ({l4['motivo']}).")
    linhas.append("")
    linhas.append("**Para dizer na banca:** " + frase_banca(est, resumo))
    return "\n".join(linhas)


def _holm_48b(resumo: dict, medidas: list[str], cs: str) -> str:
    """p de Holm das primárias do 48b (gravado em HI_estimativas.csv), quando a conferência contra o HI_ foi feita."""
    hi = resumo.get("conferencias", {}).get("HI", {})
    if hi.get("status") != "CONFERIDO":
        return ""
    ps = [x.get("HI_p_holm") for x in hi["linhas"] if x["medida"] in medidas and x["corte"] == cs]
    if not ps or any(p is None or not math.isfinite(float(p)) for p in ps):
        return ""
    return ", ".join(_p(p) for p in ps)


def frase_banca(est: pd.DataFrame, resumo: dict) -> str:
    l3 = resumo["leitura"]["0.300"]
    perto = _perto(resumo, "0.300")
    abaixo = [c for c in perto if c["distancia_mil"] <= 0]
    acima = [c for c in perto if c["distancia_mil"] > 0]
    base = (f"Logo abaixo de 0,300 (a menos de 0,010) estão {len(abaixo)} capitais ("
            + ", ".join(_nome(c) for c in abaixo) + f") e {len(acima) or 'nenhuma'} logo acima; o corte não é "
            "balanceado em capital. ")
    a_levar = l3["linhas_H1_com_queda_a_levar"]
    if l3["leitura"] == "ANDA_JUNTO_COM_CAPITAIS_OU_REGIAO":
        quedas = "; ".join(
            f"{m}, {_num(l3['por_medida'][m]['tau_sem_ajuste'] * (100 if m == 'HI-1' else 1), 1 if m == 'HI-1' else 2)}"
            f" {'p.p.' if m == 'HI-1' else 'médico por município'}" for m in a_levar)
        sem_queda = [m for m in MEDIDAS_H1 if m not in a_levar]
        holm = _holm_48b(resumo, a_levar, "0.300")
        return (base + f"A única queda das vagas imediatas que se distinguia de zero sem correção ({quedas}"
                + (f"; no 48b, depois do Holm, ela já não rejeitava zero: p de Holm {holm}" if holm else "")
                + ") deixa de se distinguir quando se compara capital com capital, municípios da mesma UF, ou quando "
                "se tiram as capitais"
                + (f"; a {' e a '.join(sem_queda)} já não se distinguia de zero" if sem_queda else "")
                + ". A queda anda junto com essas poucas capitais grandes: o corte não separa a bolsa delas. Isso não "
                "mostra que a bolsa não tenha efeito. É robustez pós-resultado, com poucos municípios perto do corte.")
    if not a_levar:
        return (base + "Comparando vagas do mesmo tipo, já não se detecta queda em 0,300, com ou sem esses ajustes; "
                "o desbalanceamento de capitais fica registrado como limite da RDD nesse corte.")
    fica = [m for m in a_levar if not l3["por_medida"][m]["levam_nos_tres"]]
    return (base + f"Com os ajustes, a queda da {' e da '.join(fica)} nem sempre deixa de se distinguir de zero; pela "
            "regra pré-registrada o resultado é relatado como está, com o desbalanceamento de capitais como limite da "
            "RDD em 0,300. É robustez pós-resultado, com poucos municípios perto do corte.")


def tabela_balanco(est: pd.DataFrame) -> str:
    linhas = []
    for cs in ("0.300", "0.400"):
        for am in ("H1", "quadro"):
            for v in VARIAVEIS_BALANCO:
                for un in ("municipio", "celula"):
                    r = _um(est, bloco="C-1", medida=v, unidade_analise=un, amostra=am, corte=cs)
                    linhas.append([_corte_txt(cs), "H1 (vagas imediatas)" if am == "H1" else "quadro inteiro",
                                   VARIAVEIS_BALANCO[v], "município × ciclo" if un == "municipio" else "célula",
                                   _v(r), _ic(r), _p(r["p_valor"]), f"{int(r['n_abaixo'])} / {int(r['n_acima'])}"])
    return _tab(["Corte", "Amostra", "Variável", "Unidade", "Salto (p.p.)", "IC 95%", "p", "Municípios abaixo / acima"],
                linhas)


def tabela_capitais(resumo: dict) -> str:
    linhas = [[_corte_txt(c["corte"]), c["municipio"], c["regiao"], _num(c["ivs"], 3, False),
               _num(c["distancia_ao_corte"], 3), c["lado"], c["ciclos"], str(c["celulas"]),
               str(c["celulas_com_vaga_imediata"]), _num(c["peso_kernel"], 2, False)]
              for c in resumo["capitais_na_janela"]]
    return _tab(["Corte", "Capital", "Região", "IVS", "Distância ao corte", "Lado", "Ciclos no quadro",
                 "Células (3 ciclos)", "Células com vaga imediata", "Peso do kernel"], linhas)


def tabela_composicao(resumo: dict, jan: int = H_MIL) -> str:
    comp = pd.DataFrame(resumo["composicao_janela"])
    comp = comp[comp["janela_mil"] == jan]
    linhas = []
    for cs in ("0.300", "0.400"):
        for am in ("H1", "quadro"):
            for un in ("municipio", "celula"):
                g = comp[(comp["corte"] == cs) & (comp["amostra"] == am) & (comp["unidade_analise"] == un)]
                a = g[g["lado"] == "abaixo"].iloc[0]
                c = g[g["lado"] == "acima"].iloc[0]
                f = lambda col: f"{_num(a[col] * 100, 0, False)}% → {_num(c[col] * 100, 0, False)}%"  # noqa: E731
                linhas.append([_corte_txt(cs), "H1" if am == "H1" else "quadro inteiro",
                               "município × ciclo" if un == "municipio" else "célula",
                               f"{int(a['linhas'])} / {int(c['linhas'])}", f("frac_capital"), f("frac_nordeste"),
                               f("frac_norte")])
    return _tab(["Corte", "Amostra", "Unidade", "Linhas abaixo / acima", "Capital (abaixo → acima)",
                 "Nordeste", "Norte"], linhas)


def tabela_h1(est: pd.DataFrame) -> str:
    linhas = []
    for cs in ("0.300", "0.400"):
        for m in MEDIDAS_H1:
            for aj in AJUSTES:
                bloco = "base" if aj == "sem_ajuste" else BLOCO_AJ[aj]
                r = _um(est, bloco=bloco, medida=m, corte=cs)
                q = _p(r["q_bky"]) if bool(r["entra_bky"]) else "—"
                cc = (f"{_num(float(r['coef_capital']) * _escala(r), _casas(r))}" if aj == "capital" else "—")
                linhas.append([_corte_txt(cs), m, bloco, ROT_AJ[aj], f"{_v(r)} {_un(r)}", _ic(r), _p(r["p_valor"]), q,
                               f"{int(r['n_abaixo'])} / {int(r['n_acima'])}",
                               f"{int(r['capitais_abaixo'])} / {int(r['capitais_acima'])}", cc])
    return _tab(["Corte", "Medida", "Linha", "Ajuste", "Salto", "IC 95%", "p", "q BKY (C-2 a C-4)",
                 "Municípios abaixo / acima", "Capitais abaixo / acima", "Coef. de capital"], linhas)


def tabela_antigas(est: pd.DataFrame) -> str:
    linhas = []
    for cs in ("0.300", "0.400"):
        for m in MEDIDAS_ANTIGAS:
            for aj in AJUSTES:
                r = _um(est, bloco="C-5", medida=m, ajuste=aj, corte=cs)
                linhas.append([_corte_txt(cs), MEDIDAS[m]["rotulo"], ROT_AJ[aj], f"{_v(r)} {_un(r)}", _ic(r),
                               _p(r["p_valor"]), f"{int(r['n_abaixo'])} / {int(r['n_acima'])}"])
    return _tab(["Corte", "Medida", "Ajuste", "Salto", "IC 95%", "p", "Municípios abaixo / acima"], linhas)


def tabela_leitura(resumo: dict) -> str:
    linhas = []
    for cs, l in resumo["leitura"].items():
        por = "; ".join(f"{m}: {'IC exclui zero' if v['ic_sem_ajuste_exclui_zero'] else 'IC contém zero'} sem ajuste; "
                        f"contém zero com {', '.join(ROT_AJ_CURTO[a] for a in v['ajustes_que_levam_a_zero']) or 'nenhum ajuste'}"
                        for m, v in l["por_medida"].items())
        linhas.append([_corte_txt(cs), "sim" if l["c1_salto_em_capital_ou_regiao"] else "não",
                       ", ".join(l["c1_linhas_com_salto"]) or "—", por,
                       "sim" if l["c2_ajustes_levam_a_ic_com_zero"] else "não", f"**{l['texto']}**", l["motivo"]])
    return _tab(["Corte", "C-1 mostra salto (amostra da H1)?", "Linhas de balanço com IC sem zero",
                 "H1 sem e com ajuste", "C-2 a C-4 levam a H1 a IC com zero?", "Leitura", "Por quê"], linhas)


def tabela_conferencias(resumo: dict) -> str:
    c = resumo["conferencias"]
    max_a36 = max(max(x["dif_tau"], x["dif_ep"]) for x in c["auditoria_36"])
    max_pipe = max(max(x["dif_tau"], x["dif_ep"]) for x in c["pipeline"])
    hi = c["HI"]
    if hi["status"] == "CONFERIDO":
        hi_txt = (f"conferido: {len(hi['linhas'])} linhas (HI-1 e HI-2 × 2 cortes) iguais a `{hi['arquivo']}`; maior "
                  f"diferença {max(max(x['dif_tau'], x['dif_ep']) for x in hi['linhas']):.1e}")
    else:
        hi_txt = f"**pendente**: {hi['motivo']}"
    info = resumo["info_dados"]
    linhas = [
        ["base de células e de municípios × ciclo igual à da auditoria 36 (`a36_celulas.csv`, `a36_municipios.csv`)",
         "sim (o script para se não for)"],
        ["linhas já calculadas pela auditoria 36 (estimador próprio)",
         f"{len(c['auditoria_36'])} linhas iguais; maior diferença {max_a36:.1e}"],
        ["A3, N1 S-a e taxa S-e sem ajuste contra o pipeline (`NA_estimativas.csv`, `N_estimativas.csv`)",
         f"{len(c['pipeline'])} linhas iguais; maior diferença {max_pipe:.1e}"],
        ["HI-1 e HI-2 sem ajuste contra `HI_estimativas.csv` (script 40)", hi_txt],
        ["lista de capitais do IBGE igual à digitada na auditoria 36", "sim" if info["lista_ibge_igual_a_da_auditoria_36"]
         else "não"],
        ["municípios marcados CAPITAL no quadro do ciclo 3 estão na lista do IBGE",
         f"sim ({info['capitais_marcadas_CAPITAL_no_quadro_c3']} marcados)"],
        ["capitais com célula em algum quadro", str(info["capitais_em_algum_quadro"])],
        ["sigla da UF do quadro = UF do código IBGE", "sim (o script para se não for)"],
        ["células por ciclo", ", ".join(f"ciclo {k}: {v}" for k, v in info["celulas_por_ciclo"].items())],
        ["células só de cadastro reserva (13/02 no ciclo 2), fora da H1",
         ", ".join(f"ciclo {k}: {v}" for k, v in info["celulas_so_cr_pre_fora_da_H1"].items())],
        ["municípios × ciclo sem célula com vaga imediata, fora da HI-2",
         ", ".join(f"ciclo {k}: {v}" for k, v in info["municipios_ciclo_sem_celula_com_imediata_fora_da_HI2"].items())],
        ["células sem IVS 2010 (município criado depois de 2010), fora da RDD",
         ", ".join(f"ciclo {k}: {v}" for k, v in info["celulas_sem_ivs"].items()) or "0"],
        ["linhas em `HC_estimativas.csv` / sem estimativa",
         f"{resumo['validacoes']['linhas']} / {resumo['validacoes']['sem_estimativa']}"],
    ]
    return _tab(["Conferência", "Resultado"], linhas)


LIMITES = [
    "- **Pós-resultado.** O adendo foi escrito depois de a auditoria 36 ver o desbalanceamento de capitais e o efeito da "
    "dummy de capital nas medidas antigas. Estas linhas são robustez; não substituem a especificação principal (48b) "
    "nem autorizam escolher, depois de ver, a variante que mais agrada.",
    "- **Poucos municípios.** Na janela de 0,050 há poucas capitais de cada lado; a estimativa no corte se apoia nos "
    "municípios mais próximos, e cada capital tem muitas células. Um município a mais ou a menos muda o número.",
    "- **Capital e região não são a explicação de mecanismo.** Ser capital junta porte, rede de serviços, residência "
    "médica e atratividade. \"Anda junto com capitais\" não diz qual desses atributos importa, nem que a bolsa não "
    "tenha efeito: diz que o corte não separa a bolsa da composição de capitais.",
    "- **Indicador binário com reta local.** O salto de \"é capital\" ou \"é do Nordeste\" é uma reta levada até o "
    "corte em cada lado; com poucos municípios grandes colados no corte, ele pode ter sinal oposto ao das médias cruas "
    "da janela inteira (tabela da seção 3) e passar de ±100 p.p. O sinal e o tamanho relativo informam mais que o "
    "número exato.",
    "- **Efeito fixo de UF.** Compara só municípios da mesma UF dos dois lados do corte; nas UFs sem município dos "
    "dois lados, a UF não informa o salto e o IC fica mais largo.",
    "- **Pacote do corte.** Em 0,300 e 0,400 mudam também outras regras federais (auditoria 18). O contraste é o "
    "pacote do corte, nunca a participação no PMM-E nem o Agora Tem Especialistas.",
    "- **Tipo de vaga.** No ciclo 2 o tipo de vaga é o do quadro de 13/02/2026 (48b, §7). A3 com o tipo de vaga do "
    "pipeline (19/03/2026, pós-resultado) só aparece como medida antiga, para comparar.",
]


def gerar_doc(est: pd.DataFrame, resumo: dict) -> str:
    d = DATA_EXECUCAO
    figs = resumo["saidas"]["figuras"]
    limite_balanco = []
    for cs in ("0.300", "0.400"):
        ruins = est[(est["bloco"] == "C-1") & (est["medida"] == "capital") & (est["corte"] == cs)
                    & (est["ic_contem_zero"] == False)]  # noqa: E712
        if len(ruins):
            limite_balanco.append(f"- **Balanço de capital em {_corte_txt(cs)}: violado.** A fração de capitais salta "
                                  f"no corte ({len(ruins)} das 4 linhas de capital do C-1 com IC que exclui zero). "
                                  f"Pelo 48c, isso é registrado como **limite da RDD em {_corte_txt(cs)}**.")
    # Auditoria 42, achado 2: a regra do §2 é binária no IC; dizer quanto do ponto cada ajuste leva.
    for cs, l in resumo["leitura"].items():
        for m in l["linhas_H1_com_queda_a_levar"]:
            b = _um(est, bloco="base", medida=m, corte=cs)
            pb = float(b["p_valor"])
            partes_aj, fica = [], []
            for aj in ("capital", "uf", "sem_capitais"):
                r = _um(est, bloco=BLOCO_AJ[aj], medida=m, corte=cs)
                frac = float(r["tau"]) / float(b["tau"])
                partes_aj.append(f"{ROT_AJ_CURTO[aj]} {_v(r)} {_ic(r)}, "
                                 f"{_num(100 * frac, 0, False)}% do ponto sem ajuste")
                if frac > 0.5:
                    fica.append({"capital": "a dummy de capital", "uf": "o efeito fixo de UF",
                                 "sem_capitais": "a amostra sem capitais"}[aj])
            limite_balanco.append(
                f"- **A regra do §2 olha só o IC.** Em {_corte_txt(cs)}, a {m} sem ajuste é {_v(b)} {_ic(b)}, com "
                f"p = {_p(pb)}: um IC que exclui zero por pouco passa a conter zero com qualquer perda de precisão "
                f"ou recuo do ponto. Com os ajustes: " + "; ".join(partes_aj) + ". Perder a significância não é o "
                "mesmo que o salto ir a zero"
                + (f"; com {' e com '.join(fica)}, mais da metade do ponto continua lá." if fica else "."))
    partes = [f"""# 57o. H1 com capitais e UF no corte 0,300 (adendo 48c, robustez pós-resultado)

> **Data:** {d[8:]}/{d[5:7]}/{d[:4]}.<br>
> **Adendo:** [`48c_adendo_capitais_e_UF.md`](48c_adendo_capitais_e_UF.md), congelado antes destas contas (SHA-256 em
> `adendo` de `HC_resumo.json`). Especificação principal da H1: [`48b`](48b_adendo_H1_vagas_imediatas.md) (com a §7:
> no ciclo 2, tipo de vaga do quadro de 13/02/2026).<br>
> **Origem:** a [auditoria 36](../auditorias/36_auditoria_dados_H1.md) viu capitais concentradas logo abaixo de 0,300.<br>
> **Auditoria:** [42](../auditorias/42_auditoria_capitais_uf.md) (recálculo independente; correções só de texto).<br>
> **Estatuto:** `{ESTATUTO}`. Robustez **pós-resultado**; não muda a especificação principal. O contraste é o pacote
> do corte (incentivo marginal anunciado e outras regras no mesmo corte), nunca a participação no PMM-E nem o Agora
> Tem Especialistas. Toda linha de `HC_estimativas.csv` tem `natureza_dos_dados = EMPIRICO`.<br>
> **Script:** `scripts/rdd_bolsa/41_h1_capitais_uf.py`. **Saídas:** `output/rdd_bolsa/HC_estimativas.csv`,
> `HC_resumo.json`, `HC_figuras/`. **Testes:** `tests/test_h1_capitais_uf.py`.<br>
> **Números:** nenhum é digitado. Os blocos entre marcadores `<!-- HC:... -->` são regravados das saídas por
> `41_h1_capitais_uf.py --atualizar-doc`; o teste confere que o documento é idêntico ao gerado."""]
    partes.append("## 1. Resposta curta\n\n" + _bloco("resposta_curta", resposta_curta(est, resumo)))
    partes.append(
        "## 2. O que se estima\n\n"
        "Todas as linhas: RDD *sharp* local linear, kernel triangular, h = 0,050, cada corte separado (0,300 e 0,400), "
        "ciclos 1–3 empilhados com intercepto e inclinações por ciclo e salto comum, erro-padrão agrupado por "
        "município (CR1). O salto é o lado de bolsa maior menos o de bolsa menor.\n\n"
        + _bloco("especificacao", _tab(["Id", "Linha", "Como"], [
            ["C-1", "balanço no corte", "salto de \"é capital\", \"é do Nordeste\" e \"é do Norte\", por município × "
             "ciclo e por célula, na amostra da H1 e no quadro inteiro; sem controle"],
            ["base", "HI-1 e HI-2 do 48b", "HI-1: células com ≥ 1 vaga imediata, preenchida = ≥ 1 alocado na 1ª chamada, "
             "efeito fixo de curso × ciclo; HI-2: médicos alocados nessas células por município, controle = vagas "
             "imediatas delas com coeficiente por ciclo"],
            ["C-2", "H1 com dummy de capital", "acrescenta 1[capital] ao modelo"],
            ["C-3", "H1 com efeito fixo de UF", "acrescenta uma dummy por UF"],
            ["C-4", "H1 sem as capitais", "tira as 27 capitais da amostra"],
            ["C-5", "medidas antigas", "A3 (tipo de vaga do pipeline; e de 13/02), N1 com controle (S-a) e taxa por "
             "vaga oferecida (S-e), sem ajuste e com C-2, C-3 e C-4; só comparação"],
            ["BKY", "q-valores", "entre as 12 linhas C-2 a C-4 (HI-1 e HI-2 × 3 ajustes × 2 cortes)"],
        ]) + "\n\nCapital = um dos 27 municípios da lista do IBGE (Localidades do Brasil 2022, categoria \"Capital "
            "Estadual\" ou \"Capital Federal\"); região = Grande Região da UF pelo SIDRA/IBGE. A cópia e o manifesto "
            f"ficam em `{resumo['referencia_ibge']['arquivo']}` e `{resumo['referencia_ibge']['manifesto']}`."))
    partes.append("## 3. C-1 — balanço de capital e de região no corte\n\n"
                  "Capitais a menos de 0,050 de cada corte (quadro inteiro, três ciclos):\n\n"
                  + _bloco("capitais", tabela_capitais(resumo))
                  + "\n\nSalto no corte (local linear, sem controle):\n\n" + _bloco("balanco", tabela_balanco(est))
                  + "\n\nMédias cruas na janela de 0,050, sem reta (só para ler o salto):\n\n"
                  + _bloco("composicao", tabela_composicao(resumo))
                  + "\n\nMédias cruas na janela de 0,010, sem reta (os municípios que mais pesam na reta local; "
                    "acrescentada pela auditoria 42):\n\n"
                  + _bloco("composicao_estreita", tabela_composicao(resumo, JANELA_ESTREITA_MIL)))
    partes.append("## 4. C-2 a C-4 — H1 com dummy de capital, efeito fixo de UF e sem capitais\n\n"
                  "\"Base\" é a H1 do 48b sem controle extra, refeita aqui com a mesma base e o mesmo estimador. HI-1 em "
                  "p.p.; HI-2 em médicos alocados por município. O coeficiente de capital é a diferença média entre "
                  "capital e não capital, dos dois lados, na mesma unidade da medida.\n\n" + _bloco("h1", tabela_h1(est)))
    partes.append("## 5. C-5 — medidas antigas, para comparação\n\n"
                  "Fora do BKY e da leitura pré-registrada. As linhas sem ajuste são as do pipeline (conferidas na "
                  "seção 7).\n\n" + _bloco("antigas", tabela_antigas(est)))
    partes.append("## 6. Leitura pré-registrada (48c, §2)\n\n"
                  "Regra aplicada a cada corte. \"C-1 mostra salto\": alguma linha de balanço na amostra da H1 com IC 95% "
                  "que exclui zero. \"C-2 a C-4 levam o salto da H1 a um IC que contém zero\": as linhas da H1 com IC "
                  "que exclui zero sem ajuste passam a ter IC com zero nos três ajustes. Se as duas valem: "
                  f"\"{LEITURA_SIM}\"; senão, \"{LEITURA_NAO}\".\n\n" + _bloco("leitura", tabela_leitura(resumo)))
    partes.append("## 7. Conferências\n\n" + _bloco("conferencias", tabela_conferencias(resumo)))
    figtxt = [f"![{Path(f['arquivo']).name}](../../{f['arquivo']})\n\n**Como ler:** {f['como_ler']}\n\n"
              f"*Detalhe técnico:* {f['detalhe_tecnico']}" for f in figs]
    partes.append("## 8. Figuras\n\n" + _bloco("figuras", "\n\n".join(figtxt)))
    partes.append("## 9. Limites\n\n" + _bloco("limites", "\n".join(limite_balanco + LIMITES)))
    partes.append("## 10. Decisões\n\n" + _bloco("decisoes", "\n".join(f"- {x}" for x in resumo["decisoes"])))
    return "\n\n".join(partes) + "\n"


# ---------------------------------------------------------------------------
# 9. Main
# ---------------------------------------------------------------------------

DECISOES = [
    "Capital e região vêm de fontes do IBGE gravadas em `output/aquisicao/` com SHA-256 (nada digitado); a lista coincide "
    "com a que a auditoria 36 tinha digitado.",
    "HI-1 e HI-2 seguem o 48b com a §7: amostra e controle pelo tipo de vaga do quadro de 13/02/2026 no ciclo 2.",
    "C-1 é estimado na amostra da H1 (a que a leitura usa) e no quadro inteiro (a das medidas antigas); por município "
    "× ciclo e por célula, sem controle, com a mesma reta por ciclo e o mesmo kernel das outras linhas.",
    "\"C-2 a C-4 levam o salto a um IC que contém zero\" foi lido como: nos três ajustes, para toda linha da H1 cujo IC "
    "sem ajuste exclui zero. Sem nenhuma linha assim, não há salto a levar e vale \"relatar como está\".",
    "Efeito fixo de UF entra como uma dummy por UF (referência = a primeira em ordem de código); dummy sem variação ou "
    "colinear na janela é descartada e registrada em `covariaveis_descartadas`.",
    "C-5 traz o A3 com o tipo de vaga do pipeline (19/03/2026, a medida antiga como foi gravada) e com o de 13/02/2026; "
    "N1 S-a e taxa S-e não dependem do tipo de vaga. C-5 fica fora do BKY e da leitura.",
    "BKY entre as 12 linhas C-2 a C-4, como manda o adendo; sem Holm (o 48c não pede).",
]


def ler_saidas() -> tuple[pd.DataFrame, dict]:
    est = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "id_linha": str})
    for c in ("efeitos_fixos", "controle", "covariaveis_descartadas", "nota"):
        est[c] = est[c].fillna("")
    resumo = json.loads((OUT / NOME_RESUMO).read_text(encoding="utf-8"))
    return est, resumo


def atualizar_doc() -> None:
    est, resumo = ler_saidas()
    DOC.write_text(gerar_doc(est, resumo), encoding="utf-8")


def entradas() -> list[dict]:
    def b(p: Path, papel: str, fonte: str, data_ref: str, cobertura: str, unidade: str, chaves: str, filtros: str):
        return {"caminho": rotulo(p), "sha256": sha256(p), "bytes": p.stat().st_size, "papel": papel, "fonte": fonte,
                "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade, "chaves": chaves,
                "filtros": filtros}
    arq = A36.ARQ
    out = [
        b(ADENDO_48C, "adendo 48c (especificacao, congelado antes)", "docs/06_execucao", "2026-10-26", "-", "texto", "-",
          "-"),
        b(ADENDO_48B, "adendo 48b (definicao de HI-1 e HI-2, §7)", "docs/06_execucao", "2026-10-26", "-", "texto", "-",
          "-"),
        b(DIR_A36 / "a36_reconstruir_H1.py", "reconstrucao da auditoria 36 (importada, nao alterada)",
          "scripts/auditoria_H1", "2026-10-26", "-", "codigo", "-", "-"),
        b(DIR_A36 / "a36_leitura.py", "leitor dos brutos da auditoria 36 (importado)", "scripts/auditoria_H1",
          "2026-10-26", "-", "codigo", "-", "-"),
        b(IVS_OFICIAL, "running variable (IVS 2010 oficial)", "Ipea (a08)", "Censo 2010", "Brasil", "municipio",
          "co_ibge (6 digitos)", "ivs"),
        b(REF_CSV, "capitais e macrorregiao das UFs", "IBGE (Localidades 2022; SIDRA 4709)", "2022", "27 UFs", "UF",
          "cd_uf; capital_co_ibge_6d", "-"),
        b(REF_MANIFESTO, "manifesto da referencia do IBGE (URLs e SHA-256 dos arquivos baixados)", "IBGE", "2022",
          "27 UFs", "-", "-", "-"),
        b(A36_CEL, "conferencia da base de celulas", "auditoria 36", "ciclos 1-3", "5135 celulas", "celula x ciclo",
          "ciclo, chave", "-"),
        b(A36_MUN, "conferencia da base de municipios", "auditoria 36", "ciclos 1-3", "municipios do quadro",
          "municipio x ciclo", "ciclo, co_ibge", "-"),
        b(A36_EST, "conferencia das linhas ja estimadas pela auditoria 36", "auditoria 36", "ciclos 1-3", "-",
          "estimativa", "-", "ciclo = 1+2+3"),
        b(NA_EST, "conferencia do A3 gravado (script 24)", "pipeline", "ciclos 1-3", "-", "estimativa", "-",
          "A3_PREENCHIDA principal, V1+V2+V3"),
        b(N_EST, "conferencia do N1 S-a e da taxa S-e gravados (script 23)", "pipeline", "ciclos 1-3", "-", "estimativa",
          "-", "N1 S-a principal e S-e, V1+V2+V3"),
    ]
    # Todos os arquivos que montar_ciclo1/2/3 da auditoria 36 leem (os não usados nas contas entram nas conferências
    # internas dela).
    papeis = {"c1_quadro": "quadro da 1a chamada, ciclo 1", "c1_aloc_sj": "alocacao do ciclo 1 (sub judice)",
              "c1_aloc": "alocacao retificada do ciclo 1 (conferencia da a36)",
              "c1_realoc": "realocacao do Quadro 2 do ciclo 1 (conferencia da a36)",
              "c1_homol": "homologados do ciclo 1 (conferencia da a36)",
              "c2_quadro_orig": "quadro original do ciclo 2 de 03/02/2026 (conferencia da a36)",
              "c2_quadro_ret1": "quadro do ciclo 2 de 13/02/2026 (tipo de vaga pre-alocacao)",
              "c2_quadro_ret2": "quadro do ciclo 2 de 19/03/2026 (celulas e total)",
              "c2_final": "resultado final do ciclo 2", "c2_prelim": "resultado preliminar do ciclo 2 (conferencia)",
              "c2_reman9": "remanescentes do ciclo 2 (conferencia)", "c2_reman81": "remanescentes do ciclo 2 (conferencia)",
              "c3_quadro_orig": "quadro original do ciclo 3 de 16/07/2026 (conferencia)",
              "c3_quadro_ret": "quadro do ciclo 3 (24/07/2026)", "c3_result_sj": "resultado do ciclo 3 (sub judice)"}
    for k, papel in papeis.items():
        out.append(b(arq[k], papel + " (lido pela auditoria 36)", "MS/SGTES (data/raw, so leitura)", "-", "-",
                     "linha do quadro/resultado", "CNES x curso", "sem colunas pessoais"))
    if HI_EST.exists():
        out.append(b(HI_EST, "conferencia de HI-1 e HI-2 (script 40)", "pipeline", "ciclos 1-3", "-", "estimativa", "-",
                     "principal, c2 = 13fev"))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="so regrava o doc 57o a partir das saidas")
    ap.add_argument("--baixar-referencias", action="store_true",
                    help="baixa de novo a lista de capitais e regioes do IBGE para output/aquisicao/")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    if args.baixar_referencias:
        man = baixar_referencias()
        print(f"referencia IBGE gravada: {man['saida']['arquivo']} ({man['saida']['sha256']})")
    est, extras = estimar_tudo()
    if {"cpf", "nome", "id_candidato", "co_profissional_sus"} & {c.lower() for c in est.columns}:
        raise FalhaValidacao("coluna de identificador pessoal na saida")
    OUT.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT / NOME_EST, index=False)
    est_lido = pd.read_csv(OUT / NOME_EST, dtype={"corte": str, "id_linha": str})
    figs = gerar_figuras(est_lido, extras, OUT / DIR_FIG)
    resumo = {
        "etapa": "HC_h1_capitais_uf",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "adendo": {"texto": rotulo(ADENDO_48C), "sha256": sha256(ADENDO_48C)},
        "pergunta": "a queda do preenchimento em 0,300 anda junto com a presenca de capitais (ou com a regiao) logo "
                    "abaixo do corte?",
        "contraste": "pacote do corte (incentivo marginal anunciado de R$ 5 mil e outras regras federais no mesmo corte, "
                     "auditoria 18); nao identifica participacao no PMM-E nem o Agora Tem Especialistas",
        "estimando": "salto no corte (lado de bolsa maior menos lado de bolsa menor) de HI-1 e HI-2 (48b) sem e com "
                     "ajuste de capital, de UF e sem capitais; balanco de capital e regiao no corte",
        "populacao": "celulas (CNES x curso) e municipios x ciclo do quadro da 1a chamada, ciclos 1-3, com IVS 2010",
        "parametros": {"cortes_mil": list(CORTES), "h_mil": H_MIL, "kernel": "triangular", "ciclos": list(CICLOS),
                       "ajustes": list(AJUSTES), "tolerancia_conferencias": TOL},
        "medidas": MEDIDAS,
        "leitura": extras["leitura"],
        "comparacao_medidas_antigas": extras["comparacao_medidas_antigas"],
        "capitais_na_janela": extras["capitais_na_janela"],
        "composicao_janela": extras["composicao_janela"],
        "referencia_ibge": extras["referencia_ibge"],
        "info_dados": extras["info_dados"],
        "conferencias": {"auditoria_36": extras["conferencia_auditoria_36"],
                         "pipeline": extras["conferencia_pipeline"], "HI": extras["conferencia_HI"]},
        "decisoes": DECISOES,
        "entradas": entradas(),
        "validacoes": {"linhas": int(len(est)), "sem_estimativa": int((est["status"] != "EXECUTADO").sum()),
                       "linhas_bky": int(est["entra_bky"].sum())},
        "saidas": {NOME_EST: {"arquivo": rotulo(OUT / NOME_EST), "sha256": sha256(OUT / NOME_EST)},
                   "figuras": [dict(f, sha256=sha256(ROOT / f["arquivo"])) for f in figs]},
        "linguagem": "descritivo e pos-resultado: diz com o que a queda anda junto, nao o que a causa",
    }
    if resumo["validacoes"]["sem_estimativa"]:
        raise FalhaValidacao("linha sem estimativa")
    gravar_json(OUT / NOME_RESUMO, resumo)
    atualizar_doc()
    print(f"HC: {len(est)} linhas; leitura "
          f"{json.dumps({k: v['leitura'] for k, v in extras['leitura'].items()})}; HI {extras['conferencia_HI']['status']}; "
          f"doc {rotulo(DOC)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
