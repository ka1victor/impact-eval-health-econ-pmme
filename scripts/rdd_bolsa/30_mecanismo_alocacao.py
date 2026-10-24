"""P6 (protocolo 56): amostra do desenho do mecanismo de alocação e passo 0 (painel CNES dos candidatos).

Protocolo: `docs/06_execucao/56_protocolo_P6_mecanismo_alocacao.md`, congelado em 19/10/2026 antes de ligar os
candidatos ao painel CNES mensal e de abrir qualquer outcome. Estatuto de toda saída: `EXPLORATORIO_P6`;
`natureza_dos_dados = EMPIRICO`. O contraste do P6 é ser ALOCADO perto da nota de corte da 1ª opção, não a bolsa.

Este script NÃO estima nada: monta a amostra (células elegíveis, candidatos, variável de seleção r, tratamento D e
D'), liga os candidatos ao CNES pela regra do G1 e calcula, por candidato, as covariáveis pré e os outcomes Y1–Y5 do
§3. Nenhuma tabela por r, por lado do corte ou por tratamento é calculada aqui; a estimação é do script 31.

Passo 0 (§3 do protocolo)
-------------------------
1. Arquivo de chaves dos candidatos ligados no G1, só no cache privado ignorado pelo Git
   (`output/aquisicao/cnes_profissional/cache_privado/chaves_extra_P6.parquet`, com o código do profissional).
2. O protocolo pede consolidar o a16 com `--chaves-extra`. Isso renumeraria o `id_prof` das saídas versionadas do
   a16, que o P4 usa. Por isso o painel dos candidatos é montado em memória, a partir do mesmo cache privado do a16
   e com a mesma agregação (`agregar_medico_mes` do a16 confere horas e municípios), e o a16 versionado fica
   intocado (adendo datado no resumo e no doc 57f).
3. Cobertura por mês (`P6_cobertura_mensal.csv`), sem quebra por r ou tratamento.

O cache privado do a16 (27 competências, 202406–202608) e o dicionário do G1 (202602) não estavam no ambiente:
foram refeitos pelos próprios scripts (a16 `--etapa baixar`; `--etapa aquisicao` deste script chama a aquisição do
G1 com o conjunto de busca lido do cache do a16, porque o cache da X1 também não existia). Antes de usar o cache,
o script confere que ele reproduz, linha a linha, o painel versionado do a16 (X1) e a ligação versionada do G1
(`G1_candidatos_origem.parquet`, as duas regras, os três ciclos). Se não reproduzir, para sem gravar.

Dados pessoais: nome e CPF mascarado dos candidatos ficam só em memória (funções do G1); o código do profissional
fica só em memória e no cache privado. `P6_amostra.parquet` traz o pseudônimo `id_candidato` (o do script 12, já
publicado pelo G1 e pelo G2) e nenhuma coluna com nome, CPF, CNS, CRM ou código do profissional.

Uso
---
    python3 scripts/rdd_bolsa/30_mecanismo_alocacao.py --etapa aquisicao   # dicionário do G1 (rede, uma vez)
    python3 scripts/rdd_bolsa/30_mecanismo_alocacao.py --etapa construir   # amostra e passo 0 (cache privado)
    python3 scripts/rdd_bolsa/30_mecanismo_alocacao.py                     # verificar (padrão; sem rede, sem gravar)
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    if nome in sys.modules:
        return sys.modules[nome]
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


# ---------------------------------------------------------------------------
# Caminhos e parâmetros (fixados pelo protocolo 56 e pelo adendo de 23/10/2026, antes de abrir outcomes)
# ---------------------------------------------------------------------------

OUT = ROOT / "output" / "rdd_bolsa"
ARQ_AMOSTRA = OUT / "P6_amostra.parquet"
ARQ_CELULAS = OUT / "P6_celulas.csv"
ARQ_COBERTURA = OUT / "P6_cobertura_mensal.csv"
ARQ_PASSO0 = OUT / "P6_passo0_resumo.json"
PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "56_protocolo_P6_mecanismo_alocacao.md"
G2_ALOC = OUT / "G2_alocacao_reconstruida.parquet"
G2_CORTES = OUT / "G2_cortes_celula.csv"
G2_RESUMO = OUT / "G2_resumo.json"
G1_CAND = OUT / "G1_candidatos_origem.parquet"
G1_DIST = OUT / "G1_distancias_opcoes.parquet"
ESCOLHAS = OUT / "outcomes" / "escolhas_candidatos.parquet"
DIR_A16 = ROOT / "output" / "aquisicao" / "cnes_profissional"
A16_PAINEL_MEDICO = DIR_A16 / "painel_medico_mes.parquet"
A16_CHAVES = DIR_A16 / "chaves_origem.parquet"
A16_MANIFESTO = DIR_A16 / "a16_manifesto_cnes_profissional.json"
CACHE_PRIVADO = DIR_A16 / "cache_privado"
CHAVES_EXTRA = CACHE_PRIVADO / "chaves_extra_P6.parquet"
GITIGNORE = ROOT / ".gitignore"
LINHAS_GITIGNORE = ("output/aquisicao/cnes_profissional/cache_privado/", "output/rdd_bolsa/G1_cache/")

DATA_EXECUCAO = "2026-10-23"
ESTATUTO = "EXPLORATORIO_P6"
NATUREZA = "EMPIRICO"
LIMITE_EXCLUSIVO = "202609"
CICLOS = (1, 2)
CHAMADA = 1
SEGUIMENTO = {1: ("202510", "202608"), 2: ("202604", "202608")}
ULTIMO_MES = "202608"
PRE_HORAS = ("202406", "202506")
REGRAS = ("g1_cpf_nome", "g1_so_nome")          # principal e sensibilidade (R5)
ROTULO_REGRA = {"g1_cpf_nome": "G1 (CPF + nome), principal", "g1_so_nome": "só nome (R5, sensibilidade)"}

OUTCOMES = [
    ("y1_vinculo_mun_1a_opcao", "Y1", "tem vínculo cadastrado no município da 1ª opção", "fração"),
    ("y2_horas_sus", "Y2", "horas SUS semanais totais", "h/sem"),
    ("y3_horas_totais", "Y3", "horas totais", "h/sem"),
    ("y4_vinculo_fora_origem", "Y4", "tem vínculo fora do município de origem pré-programa", "fração"),
    ("y5_n_municipios", "Y5", "número de municípios com vínculo", "municípios"),
]
COVARIAVEIS = [
    ("cov_vinculo_medico_pre", "vínculo médico na competência de referência (G1)", "fração"),
    ("cov_horas_pre", "horas totais no CNES, média de 202406 a 202506", "h/sem"),
    ("cov_mesma_uf", "origem na mesma UF da 1ª opção", "fração"),
    ("cov_dist_km", "distância origem–1ª opção (km)", "km"),
]
COLUNAS_PROIBIDAS = ("nome", "_nome", "nome_norm", "cpf", "_cpf", "co_cpf", "cns", "co_cns", "crm", "nu_registro",
                     "sg_uf_crm", "co_profissional_sus", "co_unidade", "_chave", "_padrao")


class FalhaValidacao(RuntimeError):
    """Conferência de integridade que falhou: o script para sem gravar."""


def rotulo(p: Path) -> str:
    return Path(p).resolve().relative_to(ROOT).as_posix()


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 22), b""):
            h.update(bloco)
    return h.hexdigest()


def _nan_none(o):
    if isinstance(o, dict):
        return {str(k): _nan_none(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_nan_none(v) for v in o]
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def gravar_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(_nan_none(obj), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bloco_entrada(path: Path, papel: str, fonte: str, data_ref: str, cobertura: str, unidade: str, chaves: str,
                  filtros: str) -> dict:
    return {"caminho": rotulo(path), "sha256": sha256(path), "bytes": Path(path).stat().st_size, "papel": papel,
            "fonte": fonte, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade,
            "chaves": chaves, "filtros": filtros}


def competencias() -> list[str]:
    comps = [c for c in pd.period_range("2024-06", "2026-08", freq="M").strftime("%Y%m")]
    if any(c >= LIMITE_EXCLUSIVO for c in comps) or len(comps) != 27:
        raise FalhaValidacao("plano de competências fora de 202406–202608")
    return comps


def modulos():
    a16 = _importar(ROOT / "scripts" / "aquisicao" / "a16_cnes_profissional_mensal.py", "a16_para_p6")
    g1 = _importar(DIR_RDD / "G1_identificar_candidatos.py", "g1_para_p6")
    return a16, g1


def conferir_gitignore() -> dict:
    texto = GITIGNORE.read_text(encoding="utf-8").splitlines()
    falta = [l for l in LINHAS_GITIGNORE if l not in texto]
    if falta:
        raise FalhaValidacao(f".gitignore sem {falta}: o cache privado não pode ficar fora do Git")
    return {"linhas_conferidas": list(LINHAS_GITIGNORE), "presentes": True}


# ---------------------------------------------------------------------------
# 1. Cache privado do a16: completo e reprodutor do a16 versionado
# ---------------------------------------------------------------------------

def conferir_cache_a16(a16) -> dict:
    regs = a16.ler_registros()
    comps = competencias()
    faltam = [c for c in comps if regs.get(c, {}).get("status") != "extraido_zip_apagado"
              or not a16.caminho_cache(c).exists()]
    if faltam:
        raise SystemExit(f"cache privado do a16 incompleto ({faltam}); rode o a16 com --etapa baixar (fail closed)")
    sem_a09 = [c for c in comps if not regs[c].get("validacao_contra_a09", {}).get("sha256_igual_ao_a09")]
    if sem_a09:
        raise FalhaValidacao(f"ZIP do cache com SHA-256 diferente do manifesto do a09: {sem_a09}")
    man = json.loads(A16_MANIFESTO.read_text(encoding="utf-8"))["por_competencia"]
    dif = [c for c in comps if regs[c].get("sha256_zip") != man.get(c, {}).get("sha256_zip")
           or regs[c].get("linhas_vinculos_medicos") != man.get(c, {}).get("linhas_vinculos_medicos")]
    if dif:
        raise FalhaValidacao(f"cache refeito difere do manifesto versionado do a16 (ZIP ou linhas): {dif}")
    return {"competencias": [comps[0], comps[-1]], "n_competencias": len(comps),
            "sha256_zip_igual_ao_a09_e_ao_manifesto_a16": True,
            "linhas_vinculos_medicos_iguais_ao_manifesto_a16": True,
            "datas_de_processamento": sorted({str(regs[c].get("data_processamento")) for c in comps})}


def reproduzir_a16(a16) -> dict:
    """Refaz a ligação da X1 e o painel médico × mês do a16 a partir do cache e compara com o versionado."""
    X = a16.x1()
    listas, _ = X.ler_listas_pmme()
    alvo = X.crms_alvo(listas)
    conselho, _ = a16.codigo_conselho_crm()
    ligs, _ = a16.refazer_ligacao_x1(listas, conselho)
    rep = a16.comparar_com_x1(ligs)
    if not rep["reproduz_100pct"]:
        raise FalhaValidacao(f"cache refeito não reproduz a ligação da X1: {rep['por_regra']}")
    partes = []
    for regra, lig in ligs.items():
        ll = lig.dropna(subset=["co_profissional_sus"])
        partes.append(pd.DataFrame({"origem": "X1", "id_externo": ll["id_medico"].astype("string"),
                                    "regra_ligacao": regra,
                                    "co_profissional_sus": ll["co_profissional_sus"].astype("string")}))
    chaves = pd.concat(partes, ignore_index=True).astype("string")
    ids = a16.atribuir_ids(chaves)
    chaves["id_prof"] = chaves["co_profissional_sus"].map(ids)
    profs = sorted(ids)
    comps = competencias()
    cols_v = [c for c in a16.COLS_CACHE if c != "co_unidade"]
    vincs = []
    for c in comps:
        t = a16._ler_cache(c, cols_v, [("co_profissional_sus", "in", profs)])
        vincs.append(t)
    vinc = pd.concat(vincs, ignore_index=True)
    vinc["id_prof"] = vinc["co_profissional_sus"].map(ids).astype("string")
    for h in a16.HORAS:
        vinc[h] = vinc[h].astype("Int32")
    vinc["natureza_dos_dados"] = NATUREZA
    pv = vinc[a16.COLS_VINCULO].sort_values(["id_prof", "competencia", "co_cnes", "co_cbo", "tp_sus_nao_sus"],
                                           kind="mergesort", na_position="last").reset_index(drop=True)
    pm = a16.agregar_medico_mes(pv, sorted(ids.values()), comps)
    ref = pd.read_parquet(A16_PAINEL_MEDICO)
    ref_ch = pd.read_parquet(A16_CHAVES)
    ch = chaves.assign(natureza_dos_dados=NATUREZA)[a16.COLS_CHAVES].sort_values(
        ["origem", "regra_ligacao", "id_externo"], kind="mergesort").reset_index(drop=True)
    iguais_painel = (len(pm) == len(ref) and all(
        np.array_equal(pm[c].astype(str).to_numpy(), ref[c].astype(str).to_numpy()) for c in a16.COLS_MEDICO))
    iguais_chaves = (len(ch) == len(ref_ch) and all(
        np.array_equal(ch[c].astype(str).to_numpy(), ref_ch[c].astype(str).to_numpy()) for c in a16.COLS_CHAVES))
    if not (iguais_painel and iguais_chaves):
        raise FalhaValidacao(f"cache refeito não reproduz o a16 versionado (painel {iguais_painel}, "
                             f"chaves {iguais_chaves})")
    del alvo
    return {"ligacao_x1_reproduzida_100pct": True,
            "painel_medico_mes_identico": True, "linhas_painel_medico_mes": int(len(pm)),
            "chaves_origem_identicas": True, "linhas_chaves": int(len(ch)),
            "nota": "ligação da X1 refeita do cache com a função do a16 e painel agregado com agregar_medico_mes; "
                    "comparação coluna a coluna com as saídas versionadas do a16"}


# ---------------------------------------------------------------------------
# 2. Ligação dos candidatos (regra do G1), conferida contra o G1 versionado
# ---------------------------------------------------------------------------

def vinc_x1_do_cache(a16, g1) -> pd.DataFrame:
    """Vínculos médicos das seis competências da X1, lidos do cache do a16 (colunas usadas pelo G1)."""
    partes = []
    for c in g1.COMPETENCIAS_X1:
        if c >= LIMITE_EXCLUSIVO:
            raise FalhaValidacao("competência >= 202609")
        t = a16._ler_cache(c, ["competencia", "co_profissional_sus", "co_municipio", "co_cnes"])
        partes.append(t)
    return pd.concat(partes, ignore_index=True)


def ligar_candidatos(a16, g1) -> tuple[dict[str, pd.DataFrame], pd.DataFrame, dict]:
    """Refaz a ligação do G1 (duas regras) e a origem; confere contra G1_candidatos_origem.parquet."""
    cands, _ = g1.ler_candidatos()
    meta_p = g1.caminho_meta(g1.COMPETENCIA_DICIONARIO)
    if not (meta_p.exists() and g1.caminho_dicionario(g1.COMPETENCIA_DICIONARIO).exists()):
        raise SystemExit("dicionário do G1 ausente; rode --etapa aquisicao (fail closed)")
    dic_meta = json.loads(meta_p.read_text(encoding="utf-8"))
    cands = g1.chaves_candidatos(cands, dic_meta["padrao_co_cpf_dominante"])
    if dic_meta.get("assinatura_alvo") != g1.assinatura_alvo(cands) or dic_meta.get("versao_cache") != g1.VERSAO_CACHE:
        raise FalhaValidacao("candidatos mudaram desde a extração do dicionário do G1")
    dic = pd.read_parquet(g1.caminho_dicionario(g1.COMPETENCIA_DICIONARIO))
    vinc = vinc_x1_do_cache(a16, g1)
    no_dic = set(dic["co_profissional_sus"])
    pool = {}
    for k in g1.CICLOS:
        comps = [c for c in g1.COMPETENCIAS_X1 if c <= g1.REFERENCIA[k]]
        pool[k] = set(vinc.loc[vinc["competencia"].isin(comps), "co_profissional_sus"].dropna()) & no_dic
    ref = pd.read_parquet(G1_CAND)
    campos = ["ligado", "etapa_ligacao", "motivo", "competencia_referencia", "vinculo_medico_na_referencia",
              "n_vinculos_referencia", "n_municipios_origem", "co_ibge_origem", "origem_principal_empatada",
              "motivo_origem_ausente"]
    ligs, conf = {}, {}
    for regra in REGRAS:
        lig = g1.ligar(cands, dic, pool, usar_cpf=(regra == "g1_cpf_nome"))
        org = g1.origem(lig, vinc)
        m = lig.merge(org, on=["ciclo", "id_candidato"], how="left", validate="one_to_one")
        r = ref[ref["regra_ligacao"] == regra].merge(m, on=["ciclo", "id_candidato"], how="outer",
                                                     suffixes=("_g1", "_p6"), validate="one_to_one", indicator=True)
        if (r["_merge"] != "both").any():
            raise FalhaValidacao(f"{regra}: candidatos diferentes do G1 versionado")
        dif = {}
        for c in campos:
            a = r[f"{c}_g1"].astype("string").fillna("<NA>").str.replace(r"\.0$", "", regex=True)
            b = r[f"{c}_p6"].astype("string").fillna("<NA>").str.replace(r"\.0$", "", regex=True)
            dif[c] = int((a != b).sum())
        if any(dif.values()):
            raise FalhaValidacao(f"{regra}: a ligação refeita difere do G1 versionado: {dif}")
        conf[regra] = {"candidatos": int(len(r)), "ligados": int(m["ligado"].sum()), "diferencas_por_campo": dif}
        ligs[regra] = m
    meta = {k: dic_meta.get(k) for k in ("competencia", "sha256_zip", "sha256_igual_ao_a09", "data_download",
                                         "data_processamento", "padrao_co_cpf_dominante", "linhas_guardadas_no_cache")}
    return ligs, cands[["ciclo", "id_candidato"]], {"reproducao_g1": conf, "dicionario_g1": meta,
                                                    "conjunto_de_busca": "profissionais com vínculo médico nas "
                                                    "competências da X1 até a referência, lidos do cache do a16"}


# ---------------------------------------------------------------------------
# 3. Células e candidatos do P6 (G2): unidade do corte = célula × ampla concorrência
# ---------------------------------------------------------------------------

CHAVE_CEL = ["ciclo", "co_cnes_7d", "cod_curso"]


def celulas_e_candidatos() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    aloc = pd.read_parquet(G2_ALOC)
    cortes = pd.read_csv(G2_CORTES, dtype={"co_cnes_7d": str})
    aloc = aloc[(aloc["chamada"] == CHAMADA) & aloc["ciclo"].isin(CICLOS)].copy()
    cortes = cortes[(cortes["chamada"] == CHAMADA) & cortes["ciclo"].isin(CICLOS)].copy()
    cortes["co_cnes_7d"] = cortes["co_cnes_7d"].str.zfill(7)
    cortes["cod_curso"] = cortes["cod_curso"].astype("Int64")
    a = aloc.rename(columns={"co_cnes_7d_1a_opcao": "co_cnes_7d"})
    a["cod_curso"] = a["cod_curso_1a_opcao"].astype("Int64")
    ac = a[(a["elegivel"] == 1) & (a["inscricao_em_reserva"] == 0)]
    mx = ac.groupby(CHAVE_CEL)["pontuacao"].max().rename("maior_nota_ac_1a_opcao").reset_index()
    n_ac = ac.groupby(CHAVE_CEL).size().rename("n_ac_1a_opcao").reset_index()
    n_res = a[(a["elegivel"] == 1) & (a["inscricao_em_reserva"] == 1)].groupby(CHAVE_CEL).size().rename(
        "n_reserva_1a_opcao").reset_index()
    c = cortes.merge(mx, on=CHAVE_CEL, how="left").merge(n_ac, on=CHAVE_CEL, how="left").merge(
        n_res, on=CHAVE_CEL, how="left")
    c[["n_ac_1a_opcao", "n_reserva_1a_opcao"]] = c[["n_ac_1a_opcao", "n_reserva_1a_opcao"]].fillna(0).astype(int)
    motivo = np.select(
        [c["vagas_total"] == 0,
         c["vagas_total"] != c["vagas_imediatas_quadro"],
         c["corte_ativo"] != 1,
         c["corte_opcao"].isna(),
         c["corte_opcao"] == 2,
         ~(c["corte_pontuacao"] < c["maior_nota_ac_1a_opcao"])],
        ["sem vaga efetiva",
         "capacidade efetiva diferente das vagas imediatas do quadro (item 5.7)",
         "sem corte ativo (nenhum proponente recusado)",
         "corte geral indefinido (só reserva admitida)",
         "corte entre candidatos de 2ª opção",
         "corte não efetivo: a nota de corte é a maior nota de ampla concorrência de 1ª opção"],
        default="elegivel")
    c["motivo_celula"] = motivo
    c["celula_elegivel"] = (c["motivo_celula"] == "elegivel").astype(int)
    c["celula"] = ("c" + c["ciclo"].astype(str) + "_" + c["co_cnes_7d"] + "_" + c["cod_curso"].map("{:02d}".format))
    c["natureza_dos_dados"] = NATUREZA
    c["estatuto"] = ESTATUTO
    cols = ["natureza_dos_dados", "estatuto", "ciclo", "celula", "co_cnes_7d", "cod_curso", "vagas_ac",
            "vagas_reserva", "vagas_total", "vagas_imediatas_quadro", "corte_ativo", "corte_opcao", "corte_pontuacao",
            "maior_nota_ac_1a_opcao", "n_ac_1a_opcao", "n_reserva_1a_opcao", "celula_elegivel", "motivo_celula"]
    cel = c[cols].sort_values(["ciclo", "co_cnes_7d", "cod_curso"]).reset_index(drop=True)

    # Candidatos: 1ª opção numa célula elegível; motivos de exclusão contados.
    a = a.merge(cel[CHAVE_CEL + ["celula", "celula_elegivel", "corte_pontuacao", "vagas_total"]], on=CHAVE_CEL,
                how="left", validate="many_to_one")
    excl = {}
    for k in CICLOS:
        d = a[a["ciclo"] == k]
        excl[str(k)] = {
            "candidatos_1a_chamada": int(len(d)),
            "nao_elegiveis_sem_pontuacao": int((d["elegivel"] != 1).sum()),
            "1a_opcao_fora_das_celulas_elegiveis": int(((d["elegivel"] == 1) & (d["celula_elegivel"] != 1)).sum()),
            "inscritos_em_reserva_na_celula_elegivel": int(((d["elegivel"] == 1) & (d["celula_elegivel"] == 1)
                                                           & (d["inscricao_em_reserva"] == 1)).sum()),
            "sub_judice_na_celula_elegivel": int(((d["elegivel"] == 1) & (d["celula_elegivel"] == 1)
                                                  & (d["sub_judice"] == 1)).sum()),
        }
    s = a[(a["elegivel"] == 1) & (a["celula_elegivel"] == 1) & (a["inscricao_em_reserva"] == 0)
          & (a["sub_judice"] == 0)].copy()
    if s["margem_1a_opcao"].isna().any():
        raise FalhaValidacao("candidato de célula elegível sem margem da 1ª opção")
    s["r"] = s["margem_1a_opcao"].astype(int)
    if not np.allclose(s["r"], s["pontuacao"] - s["corte_pontuacao"]):
        raise FalhaValidacao("margem do G2 diferente de nota − corte")
    s["empatado_no_corte"] = (s["r"] == 0).astype(int)
    rec_1a = ((s["alocado_reconstruido"] == 1) & (s["co_cnes_7d_reconstruido"] == s["co_cnes_7d"])
              & (s["cod_curso_reconstruido"] == s["cod_curso"])).astype(int)
    s["ganhou_desempate"] = np.where(s["r"] == 0, rec_1a, np.nan)
    pub_1a = ((s["alocado_publicado"] == 1) & (s["co_cnes_7d_publicado"] == s["co_cnes_7d"])
              & (s["cod_curso_publicado"] == s["cod_curso"])).astype(int)
    s["d_alocado_1a_opcao"] = pub_1a
    s["d_alocado_pmme"] = s["alocado_publicado"].astype(int)
    s["alocado_reconstruido_1a_opcao"] = rec_1a
    esc = pd.read_parquet(ESCOLHAS, columns=["ciclo", "id_candidato", "opcao_rank", "co_cnes_7d", "cod_curso",
                                             "co_ibge"])
    esc = esc[esc["opcao_rank"] == 1].drop(columns="opcao_rank")
    esc["cod_curso"] = esc["cod_curso"].astype("Int64")
    s = s.merge(esc.rename(columns={"co_ibge": "co_ibge_1a_opcao"}), on=["ciclo", "id_candidato", "co_cnes_7d",
                                                                         "cod_curso"], how="left",
                validate="one_to_one")
    if s["co_ibge_1a_opcao"].isna().any():
        raise FalhaValidacao("1ª opção sem município em escolhas_candidatos")
    for k in CICLOS:
        excl[str(k)]["no_universo_p6"] = int((s["ciclo"] == k).sum())
    cont = {"celulas_por_motivo": {str(k): {m: int(n) for m, n in g["motivo_celula"].value_counts().sort_index().items()}
                                   for k, g in cel.groupby("ciclo")},
            "celulas_elegiveis": {str(k): int(g["celula_elegivel"].sum()) for k, g in cel.groupby("ciclo")},
            "celulas_elegiveis_com_vaga_reservada": int(((cel["celula_elegivel"] == 1)
                                                         & (cel["vagas_reserva"] > 0)).sum()),
            "candidatos": excl}
    cols_s = ["ciclo", "id_candidato", "celula", "co_cnes_7d", "cod_curso", "co_ibge_1a_opcao", "vagas_total",
              "corte_pontuacao", "pontuacao", "r", "empatado_no_corte", "ganhou_desempate",
              "alocado_reconstruido_1a_opcao", "d_alocado_1a_opcao", "d_alocado_pmme", "n_opcoes"]
    return cel, s[cols_s].sort_values(["ciclo", "id_candidato"]).reset_index(drop=True), cont


# ---------------------------------------------------------------------------
# 4. Painel dos candidatos (em memória) e outcomes por candidato
# ---------------------------------------------------------------------------

def ler_vinculos_candidatos(a16, profs: list[str]) -> pd.DataFrame:
    comps = competencias()
    cols = ["competencia", "co_profissional_sus", "co_cnes", "co_municipio", "co_cbo", "tp_sus_nao_sus",
            "qt_ch_ambulatorial", "qt_ch_hosp_sus", "qt_ch_outros"]
    partes = [a16._ler_cache(c, cols, [("co_profissional_sus", "in", profs)]) for c in comps]
    v = pd.concat(partes, ignore_index=True)
    if (v["competencia"] >= LIMITE_EXCLUSIVO).any():
        raise FalhaValidacao("vínculo com competência >= 202609")
    return v


def painel_candidato_mes(v: pd.DataFrame, cmap: pd.DataFrame, origem: pd.DataFrame, comps: list[str]) -> pd.DataFrame:
    """Outcomes por candidato (`chave`) × competência. Mês sem vínculo médico (competência lida) = zero, com
    `tem_vinculo_medico = 0`; hora vazia em algum vínculo deixa as horas do mês ausentes (regra do a16 e do P4).
    `origem`: pares (chave, co_municipio) do município de origem; quem não tem origem fica com Y4 ausente."""
    vc = v.merge(cmap[["chave", "co_profissional_sus", "co_ibge_1a_opcao"]], on="co_profissional_sus", how="inner")
    h = sum(vc[c].astype("Float64") for c in ("qt_ch_ambulatorial", "qt_ch_hosp_sus", "qt_ch_outros"))
    vc["h"] = h.astype(float)
    vc["h_aus"] = vc["h"].isna()
    vc["h_sus"] = np.where(vc["tp_sus_nao_sus"] == "S", vc["h"], 0.0)
    vc["no_mun_1a"] = (vc["co_municipio"] == vc["co_ibge_1a_opcao"]).fillna(False).astype(bool)
    om = origem.assign(_orig=True)
    vc = vc.merge(om, on=["chave", "co_municipio"], how="left")
    vc["fora_origem"] = vc["_orig"].isna() & vc["co_municipio"].notna()
    g = vc.groupby(["chave", "competencia"], sort=True)
    agg = pd.DataFrame({
        "n_vinculos": g.size(),
        "y3_horas_totais": g["h"].sum(min_count=1),
        "y2_horas_sus": g["h_sus"].sum(min_count=1),
        "_aus": g["h_aus"].any(),
        "y1_vinculo_mun_1a_opcao": g["no_mun_1a"].any().astype(float),
        "y4_vinculo_fora_origem": g["fora_origem"].any().astype(float),
        "y5_n_municipios": g["co_municipio"].nunique().astype(float),
    })
    agg.loc[agg["_aus"], ["y3_horas_totais", "y2_horas_sus"]] = np.nan
    grade = pd.MultiIndex.from_product([sorted(cmap["chave"].unique()), comps], names=["chave", "competencia"])
    p = agg.reindex(grade)
    p["tem_vinculo_medico"] = p["n_vinculos"].notna().astype(float)
    aus = p["_aus"].fillna(False).astype(bool)
    for c in ("n_vinculos", "y3_horas_totais", "y2_horas_sus", "y1_vinculo_mun_1a_opcao", "y4_vinculo_fora_origem",
              "y5_n_municipios"):
        p[c] = p[c].where(p["tem_vinculo_medico"] == 1, 0.0)
    p.loc[aus, ["y3_horas_totais", "y2_horas_sus"]] = np.nan
    sem_origem = set(cmap.loc[~cmap["tem_origem"], "chave"])
    p = p.drop(columns="_aus").reset_index()
    p.loc[p["chave"].isin(sem_origem), "y4_vinculo_fora_origem"] = np.nan
    return p


def conferir_agregacao_a16(a16, v: pd.DataFrame, cmap: pd.DataFrame, p: pd.DataFrame, comps: list[str]) -> dict:
    """Horas totais, número de municípios e presença iguais aos da agregação do a16 (agregar_medico_mes)."""
    pares = cmap[["chave", "co_profissional_sus"]].drop_duplicates()
    vv = v.merge(pares, on="co_profissional_sus").rename(columns={"chave": "id_prof"})
    vv["id_prof"] = vv["id_prof"].astype(str)
    for hcol in a16.HORAS:
        vv[hcol] = vv[hcol].astype("Int32")
    pm = a16.agregar_medico_mes(vv, sorted(pares["chave"].astype(str).unique()), comps)
    q = p.set_index(["chave", "competencia"]).sort_index()
    pm = pm.set_index(["id_prof", "competencia"]).sort_index()
    pm.index.names = ["chave", "competencia"]
    q = q.loc[pm.index]
    sus = pm[["horas_amb_vinc_sus", "horas_hosp_vinc_sus", "horas_outros_vinc_sus"]].astype(float).sum(
        axis=1, min_count=3).to_numpy()
    tem_y2 = q["y2_horas_sus"].notna().to_numpy()
    dif = {
        "horas_totais": int((~np.isclose(q["y3_horas_totais"].to_numpy(float),
                                         pm["horas_totais"].astype(float).to_numpy(), equal_nan=True)).sum()),
        "n_municipios": int((q["y5_n_municipios"].to_numpy(float) != pm["n_municipios"].to_numpy(float)).sum()),
        "tem_vinculo_medico": int((q["tem_vinculo_medico"].to_numpy(float)
                                   != pm["tem_vinculo_medico"].to_numpy(float)).sum()),
        "horas_sus": int((~np.isclose(q["y2_horas_sus"].to_numpy(float)[tem_y2], sus[tem_y2])).sum()),
    }
    if any(dif.values()):
        raise FalhaValidacao(f"painel dos candidatos difere da agregação do a16: {dif}")
    return {"linhas_conferidas": int(len(q)), "diferencas": dif}


def resumir(p: pd.DataFrame, base: pd.DataFrame) -> pd.DataFrame:
    """Por candidato: Y no último mês (202608) e média nos meses de seguimento do ciclo; covariável de horas pré."""
    linhas = []
    pp = p.set_index("chave")
    for r in base.itertuples(index=False):
        o = {"chave": r.chave}
        if r.chave not in pp.index:
            linhas.append(o)
            continue
        d = pp.loc[[r.chave]]
        ini, fim = SEGUIMENTO[r.ciclo]
        seg = d[(d["competencia"] >= ini) & (d["competencia"] <= fim)]
        ult = d[d["competencia"] == ULTIMO_MES]
        pre = d[(d["competencia"] >= PRE_HORAS[0]) & (d["competencia"] <= PRE_HORAS[1])]
        for col, _, _, _ in OUTCOMES:
            o[f"{col}_ultimo"] = float(ult[col].iloc[0]) if len(ult) else np.nan
            x = seg[col].to_numpy(float)
            o[f"{col}_media"] = float(np.nanmean(x)) if np.isfinite(x).any() else np.nan
        o["n_meses_seguimento"] = int(len(seg))
        o["n_meses_seguimento_horas_ausentes"] = int(seg["y3_horas_totais"].isna().sum())
        xp = pre["y3_horas_totais"].to_numpy(float)
        o["cov_horas_pre"] = float(np.nanmean(xp)) if np.isfinite(xp).any() else np.nan
        o["cov_n_meses_pre"] = int(np.isfinite(xp).sum())
        linhas.append(o)
    return pd.DataFrame(linhas)


def cobertura(p: pd.DataFrame, base: pd.DataFrame, comps: list[str]) -> pd.DataFrame:
    """Candidatos ligados com vínculo médico por mês, por regra × ciclo × grupo (sem quebra por r ou tratamento)."""
    linhas = []
    pv = p.pivot(index="chave", columns="competencia", values="tem_vinculo_medico")
    for (regra, ciclo, grupo), g in base.groupby(["regra_ligacao", "ciclo", "grupo"], sort=True):
        ch = g.loc[g["ligado"] == 1, "chave"]
        sub = pv.reindex(ch)
        for c in comps:
            n = int(len(ch))
            k = int(sub[c].sum()) if n else 0
            linhas.append({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "regra_ligacao": regra,
                           "ciclo": int(ciclo), "grupo": grupo, "competencia": c, "candidatos": int(len(g)),
                           "candidatos_ligados": n, "ligados_com_vinculo_medico": k,
                           "fracao_com_vinculo_medico": (k / n) if n else np.nan})
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 5. Etapas
# ---------------------------------------------------------------------------

ADENDO = [
    {"data": "2026-10-23", "item": "Unidade do corte: célula × ampla concorrência (§1 do protocolo)",
     "descricao": "A modalidade está no dado (indicador de inscrição em reserva e tipo de vaga publicada, do G2). O "
                  "corte da célula é o do G2: a nota do último admitido em vaga de ampla concorrência (inclusive "
                  "remanescente de cota). Entram os candidatos de ampla concorrência; os inscritos em reserva (ER, "
                  "PCD) ficam fora e são contados, porque o corte das vagas reservadas não é reconstruído. A regra "
                  "foi fixada antes de ler qualquer outcome, depois de ver só as contagens de candidatos por r no G2 "
                  "(todas as células elegíveis têm vaga reservada; sem esta leitura do §1 não sobraria nenhum "
                  "candidato com r > 0)."},
    {"data": "2026-10-23", "item": "Corte efetivo (§2)",
     "descricao": "Célula elegível: capacidade efetiva igual às vagas imediatas do quadro, corte ativo, corte entre "
                  "candidatos de 1ª opção e nota de corte abaixo da maior nota de ampla concorrência entre os que "
                  "puseram a célula em 1º lugar. Motivos de exclusão por célula em P6_celulas.csv."},
    {"data": "2026-10-23", "item": "Passo 0: painel em memória em vez de reconsolidar o a16",
     "descricao": "O cache privado do a16 e o dicionário do G1 não existiam neste ambiente e foram refeitos pelos "
                  "próprios scripts (mesmos ZIPs do a09, SHA-256 conferido). As chaves dos candidatos foram gravadas "
                  "só no cache privado (chaves_extra_P6.parquet). Consolidar o a16 com --chaves-extra renumeraria o "
                  "id_prof das saídas versionadas que o P4 usa; o painel dos candidatos foi montado em memória, do "
                  "mesmo cache, e conferido contra agregar_medico_mes do a16. O cache refeito reproduz o painel "
                  "versionado do a16 e a ligação versionada do G1."},
    {"data": "2026-10-23", "item": "Y4 e o município de origem",
     "descricao": "Origem = todos os municípios com vínculo médico do candidato na competência de referência do "
                  "ciclo (G1: 202506 no ciclo 1, 202510 no ciclo 2). Y4 = algum vínculo num município fora desse "
                  "conjunto; candidato ligado sem vínculo na referência fica com Y4 ausente (motivo no resumo)."},
    {"data": "2026-10-23", "item": "D, D' e desempate",
     "descricao": "D = alocado na 1ª opção no resultado publicado da 1ª chamada (alvo do G2); D' = alocado em "
                  "qualquer célula. Ganhou o desempate (r = 0, R4) = admitido na 1ª opção pela reconstrução "
                  "principal do G2, que usa a classificação publicada como desempate."},
    {"data": "2026-10-23", "item": "Distância só na regra principal",
     "descricao": "A distância origem–1ª opção vem de G1_distancias_opcoes.parquet, que só tem a regra principal; "
                  "na regra só por nome (R5) ela fica ausente."},
]


def etapa_aquisicao() -> int:
    """Dicionário do G1 (202602) com o conjunto de busca lido do cache do a16 (o cache da X1 não existe aqui)."""
    a16, g1 = modulos()
    conferir_gitignore()
    conferir_cache_a16(a16)

    def profissionais_medicos_do_a16() -> dict[str, set[str]]:
        return {c: set(a16._ler_cache(c, ["co_profissional_sus"])["co_profissional_sus"].dropna())
                for c in g1.COMPETENCIAS_X1}

    g1.profissionais_medicos_x1 = profissionais_medicos_do_a16
    g1.adquirir(g1.COMPETENCIA_DICIONARIO)
    return 0


def etapa_construir() -> int:
    a16, g1 = modulos()
    comps = competencias()
    git = conferir_gitignore()
    info_cache = conferir_cache_a16(a16)
    rep_a16 = reproduzir_a16(a16)
    ligs, _, info_g1 = ligar_candidatos(a16, g1)
    cel, s, cont = celulas_e_candidatos()

    # Base candidato × regra (universo P6) + todos os candidatos ligados dos ciclos 1 e 2 (cobertura)
    partes, chaves_extra, origem_pares = [], [], []
    for regra in REGRAS:
        m = ligs[regra]
        m = m[m["ciclo"].isin(CICLOS)].copy()
        m["regra_ligacao"] = regra
        m["chave"] = regra + "|" + m["ciclo"].astype(str) + "|" + m["id_candidato"]
        partes.append(m)
        ll = m[m["ligado"] == 1]
        chaves_extra.append(pd.DataFrame({"origem": "G1_P6", "id_externo": ll["id_candidato"].astype("string"),
                                          "regra_ligacao": regra,
                                          "co_profissional_sus": ll["co_profissional_sus"].astype("string")}))
        for ch, munis in zip(ll["chave"], ll["_munis"]):
            if isinstance(munis, tuple):
                origem_pares.extend((ch, mun) for mun in munis)
    todos = pd.concat(partes, ignore_index=True)
    # _munis (tupla) fica só em memória
    origem = pd.DataFrame(origem_pares, columns=["chave", "co_municipio"]).astype("string").drop_duplicates()
    ex = pd.concat(chaves_extra, ignore_index=True).astype("string")
    CACHE_PRIVADO.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(ex, preserve_index=False), CHAVES_EXTRA, compression="zstd")

    todos = todos.merge(s[["ciclo", "id_candidato", "co_ibge_1a_opcao"]], on=["ciclo", "id_candidato"], how="left")
    todos["grupo"] = np.where(todos["co_ibge_1a_opcao"].notna(), "universo_P6", "fora_do_universo_P6")
    cmap = todos[todos["ligado"] == 1][["chave", "co_profissional_sus", "co_ibge_1a_opcao",
                                        "vinculo_medico_na_referencia"]].copy()
    cmap["co_ibge_1a_opcao"] = cmap["co_ibge_1a_opcao"].astype("string")
    cmap["tem_origem"] = cmap["vinculo_medico_na_referencia"].fillna(0).astype(int) == 1
    profs = sorted(set(cmap["co_profissional_sus"].dropna()))
    v = ler_vinculos_candidatos(a16, profs)
    p = painel_candidato_mes(v, cmap, origem, comps)
    conf_ag = conferir_agregacao_a16(a16, v, cmap, p, comps)
    cob = cobertura(p, todos, comps)

    # Amostra: universo P6 × regra
    base = todos[todos["grupo"] == "universo_P6"].drop(columns=["co_ibge_1a_opcao"]).merge(
        s, on=["ciclo", "id_candidato"], how="inner", validate="many_to_one")
    res = resumir(p, base[base["ligado"] == 1][["chave", "ciclo"]])
    am = base.merge(res, on="chave", how="left", validate="one_to_one")
    dist = pd.read_parquet(G1_DIST)
    dist = dist[(dist["opcao_rank"] == 1)][["regra_ligacao", "ciclo", "id_candidato", "dist_km_origem_principal"]]
    am = am.merge(dist, on=["regra_ligacao", "ciclo", "id_candidato"], how="left", validate="one_to_one")
    am["cov_vinculo_medico_pre"] = pd.to_numeric(am["vinculo_medico_na_referencia"], errors="coerce")
    am["cov_mesma_uf"] = np.where(am["co_ibge_origem"].notna(),
                                  (am["co_ibge_origem"].astype("string").str[:2]
                                   == am["co_ibge_1a_opcao"].astype("string").str[:2]).astype(float), np.nan)
    am["cov_dist_km"] = am["dist_km_origem_principal"]
    motivos = []
    for r in am.itertuples(index=False):
        mt = []
        if r.ligado != 1:
            mt.append(f"não ligado ao CNES ({r.motivo}): outcomes e covariáveis ausentes")
        else:
            if pd.isna(r.co_ibge_origem):
                mt.append("sem vínculo médico na competência de referência: Y4, mesma UF e distância ausentes")
            elif pd.isna(r.cov_dist_km):
                mt.append("distância ausente (" + ("regra só por nome: G1 só traz a distância da regra principal"
                                                    if r.regra_ligacao == "g1_so_nome" else "sem centroide") + ")")
            if r.n_meses_seguimento_horas_ausentes > 0:
                mt.append("algum mês de seguimento com hora ausente na fonte: horas desse mês ausentes")
        motivos.append("; ".join(mt))
    am["motivo_ausencia"] = motivos
    am["natureza_dos_dados"] = NATUREZA
    am["estatuto"] = ESTATUTO
    am = am.rename(columns={"motivo": "motivo_ligacao"})
    cols_y = [f"{c}_{k}" for c, _, _, _ in OUTCOMES for k in ("ultimo", "media")]
    cols = (["natureza_dos_dados", "estatuto", "regra_ligacao", "ciclo", "id_candidato", "celula", "co_cnes_7d",
             "cod_curso", "co_ibge_1a_opcao", "vagas_total", "corte_pontuacao", "pontuacao", "r",
             "empatado_no_corte", "ganhou_desempate", "alocado_reconstruido_1a_opcao", "d_alocado_1a_opcao",
             "d_alocado_pmme", "n_opcoes", "ligado", "etapa_ligacao", "motivo_ligacao"]
            + [c for c, _, _ in COVARIAVEIS] + ["cov_n_meses_pre"] + cols_y
            + ["n_meses_seguimento", "n_meses_seguimento_horas_ausentes", "motivo_ausencia"])
    am = am[cols].sort_values(["regra_ligacao", "ciclo", "id_candidato"]).reset_index(drop=True)
    for c in ("ligado", "n_meses_seguimento", "n_meses_seguimento_horas_ausentes", "cov_n_meses_pre"):
        am[c] = pd.to_numeric(am[c], errors="coerce").astype("Int64")
    for c in ("etapa_ligacao", "motivo_ligacao", "co_ibge_1a_opcao", "celula", "co_cnes_7d", "motivo_ausencia"):
        am[c] = am[c].astype("string")
    am["co_ibge_1a_opcao"] = am["co_ibge_1a_opcao"].astype("string")
    if any(c.lower() in COLUNAS_PROIBIDAS for c in am.columns):
        raise FalhaValidacao("coluna proibida na amostra")
    if not ((am["natureza_dos_dados"] == NATUREZA).all() and (am["estatuto"] == ESTATUTO).all()):
        raise FalhaValidacao("rótulo ausente")

    OUT.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pandas(am, preserve_index=False), ARQ_AMOSTRA, compression="zstd")
    cel.to_csv(ARQ_CELULAS, index=False)
    cob.to_csv(ARQ_COBERTURA, index=False, float_format="%.10g")

    principal = am[am["regra_ligacao"] == REGRAS[0]]
    lig_univ = {regra: {"candidatos": int((am["regra_ligacao"] == regra).sum()),
                        "ligados": int(am.loc[am["regra_ligacao"] == regra, "ligado"].sum())} for regra in REGRAS}
    cob_univ = cob[(cob["grupo"] == "universo_P6")]
    resumo = {
        "etapa": "P6_passo0_amostra",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rotulo(Path(__file__)),
        "protocolo": {"arquivo": rotulo(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD)},
        "parametros": {"ciclos": list(CICLOS), "chamada": CHAMADA, "seguimento": {str(k): list(v) for k, v in
                                                                                  SEGUIMENTO.items()},
                       "ultimo_mes": ULTIMO_MES, "pre_horas": list(PRE_HORAS), "regras": list(REGRAS),
                       "limite_exclusivo": LIMITE_EXCLUSIVO, "competencias": [comps[0], comps[-1]]},
        "outcomes": {c: {"id": i, "rotulo": r, "unidade": u} for c, i, r, u in OUTCOMES},
        "covariaveis": {c: {"rotulo": r, "unidade": u} for c, r, u in COVARIAVEIS},
        "cache_privado": {"cache_a16": rotulo(CACHE_PRIVADO), "dicionario_g1": rotulo(g1.CACHE_DIR),
                          "chaves_extra": rotulo(CHAVES_EXTRA), "gitignore": git, **info_cache},
        "reproducao_a16": rep_a16,
        "ligacao": info_g1,
        "conferencia_agregacao_a16": conf_ag,
        "contagens": cont,
        "ligacao_no_universo": lig_univ,
        "universo_principal": {"candidatos": int(len(principal)),
                               "celulas": int(principal["celula"].nunique()),
                               "por_ciclo": {str(k): int(n) for k, n in principal["ciclo"].value_counts().sort_index()
                                             .items()}},
        "cobertura_universo": {f"{regra}|{ciclo}": {"min": float(g["fracao_com_vinculo_medico"].min()),
                                                     "max": float(g["fracao_com_vinculo_medico"].max()),
                                                     "candidatos_ligados": int(g["candidatos_ligados"].iloc[0])}
                               for (regra, ciclo), g in cob_univ.groupby(["regra_ligacao", "ciclo"])},
        "candidatos_ligados_sem_origem": {regra: int(((am["regra_ligacao"] == regra) & (am["ligado"] == 1)
                                                      & am["cov_vinculo_medico_pre"].eq(0)).sum()) for regra in REGRAS},
        "adendo": ADENDO,
        "entradas": [
            bloco_entrada(PROTOCOLO_MD, "protocolo 56 (somente lido)", "repositório", "2026-10-19", "§1–§7",
                          "documento", "-", "-"),
            bloco_entrada(G2_ALOC, "candidatos, nota, margem da 1ª opção, alocação publicada e reconstruída", "G2",
                          "2026-10-19", "ciclos 1–3, 1ª e 2ª chamadas", "candidato × chamada",
                          "ciclo, chamada, id_candidato", "ciclos 1 e 2, 1ª chamada"),
            bloco_entrada(G2_CORTES, "corte de ampla concorrência e capacidade por célula", "G2", "2026-10-19",
                          "células", "célula × chamada", "ciclo, chamada, co_cnes_7d, cod_curso",
                          "ciclos 1 e 2, 1ª chamada"),
            bloco_entrada(G1_CAND, "ligação versionada do G1 (conferência fail closed)", "G1", "2026-10-19",
                          "ciclos 1–3, duas regras", "candidato × regra", "regra_ligacao, ciclo, id_candidato",
                          "nenhum"),
            bloco_entrada(G1_DIST, "distância origem–opção (regra principal)", "G1", "2026-10-19", "ciclos 1–3",
                          "candidato × opção", "ciclo, id_candidato, opcao_rank", "opcao_rank = 1"),
            bloco_entrada(ESCOLHAS, "município da 1ª opção", "script 12", "2026-10-18", "ciclos 1–3",
                          "candidato × opção", "ciclo, id_candidato, opcao_rank", "opcao_rank = 1"),
            bloco_entrada(A16_PAINEL_MEDICO, "conferência do cache refeito (painel médico × mês da X1)", "a16",
                          "2026-10-19", "202406–202608", "médico × competência", "id_prof, competencia", "nenhum"),
            bloco_entrada(A16_CHAVES, "conferência do cache refeito (chaves da X1)", "a16", "2026-10-19", "X1",
                          "registro × regra", "id_prof, id_externo, regra_ligacao", "nenhum"),
            bloco_entrada(A16_MANIFESTO, "SHA-256 e linhas dos ZIPs por competência (conferência do cache)", "a16",
                          "2026-10-19", "27 competências", "competência", "competencia", "por_competencia"),
        ],
        "integridade": "nada simulado ou imputado; mês sem vínculo numa competência lida = zero, com rótulo; hora "
                       "vazia = ausente; não ligado fica na amostra com outcomes ausentes e motivo; nenhuma "
                       "competência >= 202609; o arquivo local de IVS não é lido; sem nome, CPF, CNS, CRM ou código "
                       "do profissional nas saídas",
    }
    resumo["saidas"] = {}
    for p_ in (ARQ_AMOSTRA, ARQ_CELULAS, ARQ_COBERTURA):
        resumo["saidas"][p_.name] = {"arquivo": rotulo(p_), "sha256": sha256(p_)}
    resumo["saidas"][ARQ_AMOSTRA.name].update({"linhas": int(len(am)), "colunas": list(am.columns)})
    gravar_json(ARQ_PASSO0, resumo)
    print(json.dumps(_nan_none({"universo_principal": resumo["universo_principal"], "ligacao": lig_univ}),
                     ensure_ascii=False, indent=1))
    return 0


def etapa_verificar() -> int:
    """Confere as saídas versionadas contra o resumo do passo 0, sem rede e sem gravar (fail closed)."""
    if not ARQ_PASSO0.exists():
        raise SystemExit(f"{rotulo(ARQ_PASSO0)} ausente; rode --etapa construir")
    r = json.loads(ARQ_PASSO0.read_text(encoding="utf-8"))
    erros = []
    for nome, reg in r["saidas"].items():
        p = ROOT / reg["arquivo"]
        if not p.exists():
            erros.append(f"saída ausente: {reg['arquivo']}")
        elif sha256(p) != reg["sha256"]:
            erros.append(f"SHA-256 de {reg['arquivo']} difere do resumo do passo 0")
    for e in r["entradas"]:
        p = ROOT / e["caminho"]
        if not p.exists() or sha256(p) != e["sha256"]:
            erros.append(f"entrada mudou desde a construção: {e['caminho']}")
    if ARQ_AMOSTRA.exists():
        nomes = pq.read_metadata(ARQ_AMOSTRA).schema.to_arrow_schema().names
        if any(c.lower() in COLUNAS_PROIBIDAS for c in nomes):
            erros.append("coluna com dado pessoal na amostra")
    if r.get("natureza_dos_dados") != NATUREZA or r.get("estatuto") != ESTATUTO:
        erros.append("rótulos do resumo")
    if r["parametros"]["competencias"][1] >= LIMITE_EXCLUSIVO:
        erros.append("competência >= 202609")
    conferir_gitignore()
    if erros:
        for e in erros:
            print(f"VERIFICAÇÃO REPROVADA: {e}")
        raise SystemExit("verificar: saídas do P6 (passo 0) não conferem; refaça com --etapa construir")
    print(f"P6 passo 0 conferido sem rede: {r['saidas'][ARQ_AMOSTRA.name]['linhas']} linhas na amostra; nada gravado")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--etapa", choices=("verificar", "aquisicao", "construir"), default="verificar")
    args = ap.parse_args(argv)
    if args.etapa == "aquisicao":
        return etapa_aquisicao()
    if args.etapa == "construir":
        return etapa_construir()
    return etapa_verificar()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
