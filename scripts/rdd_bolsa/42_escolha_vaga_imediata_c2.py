"""Adendo 52c: tipo de vaga do ciclo 2 medido antes da alocação (E9, P1 M1 e M5, P1h-1).

Adendo congelado: `docs/06_execucao/52c_adendo_vaga_imediata_ciclo2.md` (26/10/2026, antes de reestimar), com
estatuto `ADENDO_52C_CORRECAO_COVARIAVEL`. Toda saída leva `natureza_dos_dados = EMPIRICO`.

Motivo (auditoria 36, seção 3, item 3, e seção 10a)
--------------------------------------------------
No ciclo 2, as covariáveis "tem vaga imediata" e "log(vagas imediatas + 1)" do conjunto de escolha vieram do
quadro retificado de 19/03/2026, refeito depois do resultado preliminar (10/03): 630 vagas de reserva viraram
imediatas em 301 células, e 297 delas tinham recebido alocado. Esses atributos são, em parte, a própria escolha.
O quadro vigente na inscrição é o retificado de 13/02/2026
(`data/raw/aquisicao/vagas/2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx`), com as mesmas 1.547 células.

O que o script faz
------------------
1. **Portão de reprodução (versão antiga).** Reestima, com as funções dos scripts originais importadas sem
   alteração (16 para o E9, 25 para o P1 e 25c para o D_UF):
   - E9 principal (logit condicional da 1ª opção, conjunto principal, spline linear, bolsa linear), ciclo 2 e
     empilhado, contra `E9_estimativas.csv` (todos os termos) e `E9_efeitos_marginais.csv` (razão de chances);
   - P1 M1 (empilhado) e M5 (ciclos 1, 2, 3), contra `P1_estimativas.csv` (todos os termos e o Wald do P1d);
   - P1h-1 (D_UF no M1) e D_UF no M5 por ciclo, contra `P1h_magnitudes.csv`.
   Diferença máxima ≤ 1e−8 em tudo. Se falhar, a execução para (`FALHA_REPRODUCAO_<linha>`) e nada é corrigido.
2. **Correção.** Só no ciclo 2, `vagas_imediatas`, `tem_vaga_imediata` e `log_vagas_imediatas_mais_1` do conjunto
   passam a vir do quadro de 13/02/2026, lido com a função `ler_quadro` do script 12 (a mesma que montou o
   conjunto), e conferido célula a célula contra a leitura independente da auditoria 36 (`a36_celulas.csv`). A
   amostra de candidatos, as células do conjunto e todas as outras colunas ficam iguais (conferido). Célula do
   conjunto sem linha (ou sem número de vagas) no quadro de 13/02 é contada e faz a execução parar
   (`FALHA_CELULA_AUSENTE_1302`): nada é imputado.
3. **Relato.** Versão antiga e corrigida lado a lado: coeficiente da bolsa, IC e p; razão de chances por +R$ 5 mil;
   D_UF com IC e p unilateral; Holm como nos protocolos (P1a: família de um teste, bilateral; P1h-1: família de um
   teste, unilateral; o E9 é secundário e exploratório, sem Holm, protocolo 40 §12).

Contraste: pacote do corte e incentivo marginal da bolsa na escolha condicional a candidatar-se, dentro das vagas
abertas. Não é efeito da participação no PMM-E nem do Agora Tem Especialistas.

Integridade
-----------
Só lê `data/` (o quadro de 13/02 e, pelas funções do 25, a CIR e os centroides) e `output/`; não escreve em
`data/`. O IVS 2010 oficial vem do a08; o arquivo local de IVS da auditoria 16 não é lido. Nada simulado nem
imputado. Sem nome, CPF, CRM ou pseudônimo de candidato em `output/` (só agregados). As saídas `E9_*`, `P1_*` e
`P1h_*` não são regravadas.

Uso
---
    python3 scripts/rdd_bolsa/42_escolha_vaga_imediata_c2.py
    python3 scripts/rdd_bolsa/42_escolha_vaga_imediata_c2.py --atualizar-doc   # só regrava o doc 57p
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


P1H = _importar(DIR_RDD / "25c_magnitudes_P1h.py", "p1h_para_vc")
P1 = P1H.P1
E9 = P1.E9
L = P1.L
B12 = _importar(DIR_RDD / "12_construir_outcomes_funil.py", "outcomes_funil_para_vc")

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

SCRIPT_16 = DIR_RDD / "16_estimar_E9_escolha.py"
SCRIPT_25 = DIR_RDD / "25_escolha_dap.py"
SCRIPT_25C = DIR_RDD / "25c_magnitudes_P1h.py"
SCRIPT_12 = DIR_RDD / "12_construir_outcomes_funil.py"
ADENDO_MD = ROOT / "docs" / "06_execucao" / "52c_adendo_vaga_imediata_ciclo2.md"
PROTOCOLO_52 = ROOT / "docs" / "06_execucao" / "52_protocolo_P1_escolha_dap.md"
PROTOCOLO_52B = ROOT / "docs" / "06_execucao" / "52b_protocolo_P1h_magnitudes.md"
DOC = ROOT / "docs" / "06_execucao" / "57p_escolha_vaga_imediata_c2.md"
OUT = ROOT / "output" / "rdd_bolsa"
E9_EST = E9.OUT_ESTIMATIVAS
E9_EFE = E9.OUT_EFEITOS
P1_EST = P1.OUT_EST
P1H_CSV = P1H.OUT_CSV
QUADRO_1302 = B12.QUADROS_C2_VERSOES["retificado_servicos"]
QUADRO_1903 = B12.QUADRO_C2
A36_CELULAS = ROOT / "output" / "auditoria_H1" / "a36_celulas.csv"
A36_RESUMO = ROOT / "output" / "auditoria_H1" / "a36_resumo.json"
OUT_CSV = OUT / "VC_estimativas.csv"
OUT_RESUMO = OUT / "VC_resumo.json"
DIR_FIG = OUT / "VC_figuras"
FIG = DIR_FIG / "VC_antigo_corrigido.png"

# ---------------------------------------------------------------------------
# Parâmetros (adendo 52c e protocolos 52 e 52b; nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-26"
NATUREZA = "EMPIRICO"
ESTATUTO = "ADENDO_52C_CORRECAO_COVARIAVEL"
TOL_REPRODUCAO = 1e-8
ALFA = 0.05
Z95 = float(stats.norm.ppf(0.975))
Z95_UNI = float(stats.norm.ppf(0.95))
PASSO_BOLSA = 5.0
CICLO_CORRIGIDO = 2
COVARIAVEIS = ["tem_vaga_imediata", "log_vagas_imediatas_mais_1"]
ANTIGA = "antiga_19mar"
CORRIGIDA = "corrigida_13fev"
VERSOES = (ANTIGA, CORRIGIDA)
ROTULO_VERSAO = {ANTIGA: "antiga (quadro de 19/03/2026)", CORRIGIDA: "corrigida (quadro de 13/02/2026)"}
EMPILHADO = P1.EMPILHADO
B = P1.TERMO_BOLSA
ESPEC_E9 = E9.ESPEC_PRINCIPAL
MOD_E9 = E9.MODELO_COND

# Modelos reestimados: (chave, bloco, modelo no CSV de origem, ciclo)
MODELOS = [("E9_2", "E9", "E9 principal", "2"), ("E9_emp", "E9", "E9 principal", EMPILHADO),
           ("M1", "P1", "M1", EMPILHADO), ("M5_1", "P1", "M5", "1"), ("M5_2", "P1", "M5", "2"),
           ("M5_3", "P1", "M5", "3")]
ROTULO_MODELO = {
    "E9_2": "E9 principal, ciclo 2 (sem distância, amostra completa do E9)",
    "E9_emp": "E9 principal, ciclos 1–3 (sem distância, amostra completa do E9)",
    "M1": "P1 M1, ciclos 1–3 (distância e origem; principal do P1a)",
    "M5_1": "P1 M5, ciclo 1 (M1 por ciclo)",
    "M5_2": "P1 M5, ciclo 2 (M1 por ciclo)",
    "M5_3": "P1 M5, ciclo 3 (M1 por ciclo)",
}
ROTULO_CURTO = {"E9_2": "E9, ciclo 2", "E9_emp": "E9, ciclos 1–3", "M1": "P1 M1, ciclos 1–3",
                "M5_1": "P1 M5, ciclo 1", "M5_2": "P1 M5, ciclo 2", "M5_3": "P1 M5, ciclo 3"}

COLUNAS = ["natureza_dos_dados", "estatuto", "versao", "versao_quadro_ciclo2", "bloco", "chave_modelo", "modelo",
           "ciclo", "tipo_linha", "termo", "estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato",
           "ic95_inf", "ic95_sup", "p", "p_t_g_menos_1", "li95_unilateral", "p_unilateral", "estatistica_wald", "gl",
           "entra_holm", "familia_holm", "p_holm", "rejeita_h0_5pct", "g_conjuntos", "g_candidatos", "n_candidatos",
           "n_alternativas_ou_linhas", "n_conjuntos", "nota"]

COMO_LER = ("Cada linha é uma especificação; o círculo vazado cinza é a versão antiga (tipo de vaga do ciclo 2 pelo "
            "quadro de 19/03/2026, refeito depois do resultado preliminar) e o ponto azul é a versão corrigida (quadro "
            "de 13/02/2026, vigente na inscrição). As barras são o IC 95% com cluster por conjunto de escolha (curso × "
            "ciclo). À esquerda, a razão de chances por +R$ 5 mil de bolsa anunciada, em escala log: acima de 1, a bolsa "
            "maior desloca a 1ª opção para a vaga; a linha vertical marca 1 (nenhum efeito). À direita, D_UF = θ_UF − "
            "10·β, o peso de a vaga ficar na UF de origem menos o de toda a amplitude da bolsa (R$ 10 → 20 mil), em "
            "log-chance; acima de 0, a origem pesa mais. Os ciclos 1 e 3 não mudam por construção (só o ciclo 2 é "
            "corrigido). Tudo é escolha condicional a se candidatar, dentro das vagas abertas; a bolsa mede o pacote do "
            "corte, e a origem é preferência revelada, não efeito causal.")


class FalhaValidacao(RuntimeError):
    pass


rel = P1.rel
sha256 = P1.sha256
gravar_json = P1.gravar_json
_n, _p, _peq, _ic, _tab = P1._n, P1._p, P1._peq, P1._ic, P1._tab


# ---------------------------------------------------------------------------
# Covariável corrigida
# ---------------------------------------------------------------------------

def ler_quadros_c2() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Quadros de 13/02 e 19/03 do ciclo 2 pela função `ler_quadro` do script 12 (só leitura)."""
    if QUADRO_1302.name != "2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx":
        raise FalhaValidacao(f"quadro de 13/02 inesperado: {rel(QUADRO_1302)}")
    return B12.ler_quadro(QUADRO_1302), B12.ler_quadro(QUADRO_1903)


def conferir_contra_a36(q1302: pd.DataFrame) -> dict:
    """Vagas imediatas de 13/02 iguais às da leitura independente da auditoria 36, célula a célula."""
    a = pd.read_csv(A36_CELULAS, dtype={"cnes": str, "chave": str})
    a = a[a["ciclo"] == CICLO_CORRIGIDO]
    a["co_cnes_7d"] = a["cnes"].str.zfill(7)
    m = q1302.merge(a[["co_cnes_7d", "cod_curso", "vagas_imediatas_13fev"]], on=["co_cnes_7d", "cod_curso"],
                    how="outer", indicator=True, validate="one_to_one")
    so_um = int((m["_merge"] != "both").sum())
    dif = int((m.loc[m["_merge"] == "both", "vagas_imediatas"] !=
               m.loc[m["_merge"] == "both", "vagas_imediatas_13fev"]).sum())
    if so_um or dif:
        raise FalhaValidacao(f"quadro de 13/02 difere da leitura da auditoria 36: {so_um} células em só uma das "
                             f"leituras, {dif} com vagas imediatas diferentes")
    return {"celulas_comparadas": int(len(m)), "celulas_em_so_uma_leitura": so_um,
            "celulas_com_vagas_imediatas_diferentes": dif}


def corrigir(conj: pd.DataFrame, q1302: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Troca, só no ciclo 2, vagas imediatas, tem vaga imediata e log(vagas + 1) pelas do quadro de 13/02.

    Mesma fórmula do script 12 (`conjunto_escolha`). Célula sem linha ou sem número no quadro de 13/02 é contada e faz
    parar: não se imputa nem se retira célula (a amostra tem de ser a mesma).
    """
    c = conj.copy()
    c["vagas_imediatas"] = c["vagas_imediatas"].astype(float)
    c["log_vagas_imediatas_mais_1"] = c["log_vagas_imediatas_mais_1"].astype(float)
    m2 = (c["ciclo"] == CICLO_CORRIGIDO).to_numpy()
    idx = pd.MultiIndex.from_frame(c.loc[m2, ["co_cnes_7d", "cod_curso"]])
    q = q1302.set_index(["co_cnes_7d", "cod_curso"])
    vi = q["vagas_imediatas"].reindex(idx).to_numpy(dtype=float)
    sem_linha = int((~idx.isin(q.index)).sum())
    sem_numero = int(np.isnan(vi).sum()) - sem_linha
    diag = {"celulas_ciclo2_no_conjunto": int(m2.sum()), "celulas_sem_linha_no_quadro_1302": sem_linha,
            "celulas_sem_numero_de_vagas_imediatas_no_quadro_1302": sem_numero, "imputadas": 0}
    if sem_linha or sem_numero:
        raise FalhaValidacao(f"FALHA_CELULA_AUSENTE_1302: {sem_linha} células sem linha e {sem_numero} sem número "
                             "no quadro de 13/02 (nada é imputado)")
    ibge_q = q["co_ibge"].reindex(idx).to_numpy(dtype=object)
    faixa_q = q["faixa_anunciada"].reindex(idx).to_numpy(dtype=object)
    diag["celulas_com_municipio_diferente_19mar_13fev"] = int((ibge_q != c.loc[m2, "co_ibge"].to_numpy()).sum())
    diag["celulas_com_faixa_diferente_19mar_13fev"] = int((faixa_q != c.loc[m2, "faixa_anunciada"].to_numpy()).sum())
    antigo_tem = c.loc[m2, "tem_vaga_imediata"].to_numpy()
    antigo_vi = c.loc[m2, "vagas_imediatas"].to_numpy(dtype=float)
    novo_tem = (vi > 0).astype(int)
    c.loc[m2, "vagas_imediatas"] = vi
    c.loc[m2, "tem_vaga_imediata"] = novo_tem
    c.loc[m2, "log_vagas_imediatas_mais_1"] = np.log(vi + 1.0)
    diag.update({
        "vagas_imediatas_total_19mar": float(antigo_vi.sum()), "vagas_imediatas_total_13fev": float(vi.sum()),
        "celulas_com_vaga_imediata_19mar": int(antigo_tem.sum()), "celulas_com_vaga_imediata_13fev": int(novo_tem.sum()),
        "celulas_de_reserva_em_13fev_com_imediata_em_19mar": int(((antigo_tem == 1) & (novo_tem == 0)).sum()),
        "celulas_com_imediata_em_13fev_e_reserva_em_19mar": int(((antigo_tem == 0) & (novo_tem == 1)).sum()),
        "celulas_com_vagas_imediatas_diferentes": int((antigo_vi != vi).sum()),
        "concordancia_tem_vaga_imediata": float((antigo_tem == novo_tem).mean()),
    })
    return c, diag


def conferir_versao_antiga(conj: pd.DataFrame, q1903: pd.DataFrame) -> dict:
    """A covariável gravada no conjunto do ciclo 2 é a do quadro de 19/03 (auditoria 36, seção 10a)."""
    c2 = conj[conj["ciclo"] == CICLO_CORRIGIDO]
    m = c2.merge(q1903[["co_cnes_7d", "cod_curso", "vagas_imediatas"]], on=["co_cnes_7d", "cod_curso"], how="left",
                 suffixes=("", "_19mar"), validate="one_to_one")
    igual = (m["vagas_imediatas"] == m["vagas_imediatas_19mar"])
    if not igual.all():
        raise FalhaValidacao(f"conjunto do ciclo 2 difere do quadro de 19/03 em {int((~igual).sum())} células")
    return {"celulas": int(len(m)), "iguais_ao_quadro_19mar": int(igual.sum())}


def escolhas_c2(cand: pd.DataFrame, conj_antigo: pd.DataFrame, conj_novo: pd.DataFrame) -> dict:
    """Parte das 1ªs opções do ciclo 2 (amostra do E9) em célula com vaga imediata, nas duas versões (descritivo)."""
    r1 = cand[(cand["ciclo"] == CICLO_CORRIGIDO) & (cand["opcao_rank"] == 1)][["ciclo", "co_cnes_7d", "cod_curso"]]
    out = {"candidatos_1a_opcao_ciclo2": int(len(r1))}
    for nome, cj in ((ANTIGA, conj_antigo), (CORRIGIDA, conj_novo)):
        m = r1.merge(cj[["ciclo", "co_cnes_7d", "cod_curso", "tem_vaga_imediata"]], how="left",
                     on=["ciclo", "co_cnes_7d", "cod_curso"], validate="many_to_one")
        if m["tem_vaga_imediata"].isna().any():
            raise FalhaValidacao("1ª opção do ciclo 2 fora do conjunto")
        out[f"em_celula_com_vaga_imediata_{nome}"] = int(m["tem_vaga_imediata"].sum())
        out[f"fracao_em_celula_com_vaga_imediata_{nome}"] = float(m["tem_vaga_imediata"].mean())
    return out


# ---------------------------------------------------------------------------
# Estimação (funções dos scripts 16, 25 e 25c, sem alteração)
# ---------------------------------------------------------------------------

def _enxugar(r: dict) -> dict:
    for k in ("_A", "_D", "_scores", "_info"):
        r.pop(k, None)
    return r


def estimar_versao(dados: dict, conj_e9: pd.DataFrame, conj_p1: pd.DataFrame, log=print) -> dict[str, dict]:
    """E9 (ciclo 2 e empilhado), M1 e M5 (ciclos 1–3) num conjunto de escolha. Devolve os ajustes e as linhas de
    efeito do E9 (razão de chances) calculadas pela função do script 16."""
    res: dict[str, dict] = {}
    cand = dados["cand"]
    for chave, ciclo in (("E9_2", "2"), ("E9_emp", EMPILHADO)):
        ci = [1, 2, 3] if ciclo == EMPILHADO else [int(ciclo)]
        cj = conj_e9[conj_e9["ciclo"].isin(ci)].reset_index(drop=True)
        r = E9.estimar(cj, cand[cand["ciclo"].isin(ci)], MOD_E9, "principal", ESPEC_E9, dados["macros"],
                       dados["estratos"])
        if not r["ok"]:
            raise FalhaValidacao(f"{chave} não convergiu")
        r["_efeitos"] = E9.linhas_efeitos(ciclo, r)
        for k in ("_X", "_conj", "_esc_r1", "_esc", "_exc", "_grupos", "_scores", "_info_inv"):
            r.pop(k, None)
        res[chave] = r
        log(f"{chave}: ok, it={r['iteracoes']}")
    dados_v = {**dados, "conj_p1": conj_p1}
    D = P1.montar_desenho(conj_p1, dados["r1_p1"], None, dados_v)
    res["_conf_dist"] = P1.conferir_distancias(D)
    res["M1"] = _enxugar(P1.estimar(P1.matriz_modelo(D, dados_v, "M1"), D, modelo="M1", ciclo=EMPILHADO,
                                    amostra="P1 (G1 com origem)"))
    log(f"M1: ok={res['M1']['ok']} it={res['M1'].get('iteracoes')}")
    del D
    for k in P1.CICLOS:
        Dk = P1.montar_desenho(conj_p1[conj_p1["ciclo"] == k].reset_index(drop=True),
                               dados["r1_p1"][dados["r1_p1"]["ciclo"] == k], None, dados_v)
        res[f"M5_{k}"] = _enxugar(P1.estimar(P1.matriz_modelo(Dk, dados_v, "M1"), Dk, modelo="M5", ciclo=str(k),
                                             amostra="P1 (G1 com origem)"))
        log(f"M5 ciclo {k}: ok={res[f'M5_{k}']['ok']}")
    for chave in ("M1", "M5_1", "M5_2", "M5_3"):
        if not res[chave]["ok"]:
            raise FalhaValidacao(f"{chave} não convergiu")
    return res


def wald_ciclos(res: dict) -> tuple[float, float]:
    """Wald da igualdade de β entre ciclos (P1d), como no script 25: ciclos como amostras independentes."""
    bs, vs = [], []
    for k in P1.CICLOS:
        r = res[f"M5_{k}"]
        kb = r["termos"].index(B)
        bs.append(r["theta"][kb])
        vs.append(r["V_conj"][kb, kb])
    Rw = np.array([[1.0, -1.0, 0.0], [0.0, 1.0, -1.0]])
    d = Rw @ np.array(bs)
    W = float(d @ np.linalg.solve(Rw @ np.diag(vs) @ Rw.T, d))
    return W, float(stats.chi2.sf(W, 2))


def d_uf(chave: str, r: dict) -> dict:
    """D_UF = θ_UF − 10·β pela função do script 25c (linha P1h-1 no M1; sensibilidade P1h-3 no M5)."""
    papel = ("P1h-1", "primaria") if chave == "M1" else ("P1h-3", "sensibilidade")
    return P1H.linha_dif_uf(chave, r, *papel)


# ---------------------------------------------------------------------------
# Portão de reprodução (versão antiga)
# ---------------------------------------------------------------------------

def _dif(a, b) -> float:
    return float(np.max(np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))))


def portao(res: dict, e9_est: pd.DataFrame, e9_efe: pd.DataFrame, p1_est: pd.DataFrame,
           p1h: pd.DataFrame, tol: float = TOL_REPRODUCAO) -> dict:
    """Compara a versão antiga com os CSV gravados. Cada linha do portão é uma especificação."""
    linhas, falha = [], None

    def registrar(nome: str, ok_termos: bool, difs: dict[str, float], n_termos: int, n_gravados: int) -> None:
        nonlocal falha
        passou = bool(ok_termos and all(v <= tol for v in difs.values()))
        linhas.append({"linha": nome, "termos_reestimados": n_termos, "termos_gravados": n_gravados,
                       "mesmos_termos_na_mesma_ordem": bool(ok_termos), **{f"dif_max_{k}": v for k, v in difs.items()},
                       "passou": passou})
        if not passou and falha is None:
            falha = f"FALHA_REPRODUCAO_{nome}"

    ep = lambda V: np.sqrt(np.diag(V))  # noqa: E731
    for chave, ciclo in (("E9_2", "2"), ("E9_emp", EMPILHADO)):
        r = res[chave]
        g = e9_est[(e9_est["ciclo"] == ciclo) & (e9_est["modelo"] == MOD_E9) & (e9_est["conjunto"] == "principal") &
                   (e9_est["especificacao"] == ESPEC_E9)].set_index("termo")
        ok = list(g.index) == list(r["termos"])
        difs = {}
        if ok:
            difs = {"coef": _dif(r["theta"], g["coef"]), "ep_cluster_conjunto": _dif(ep(r["V_conj"]),
                                                                                     g["ep_cluster_conjunto"]),
                    "ep_mle": _dif(ep(r["V_mle"]), g["ep_mle"]),
                    "ep_cluster_candidato": _dif(ep(r["V_cand"]), g["ep_cluster_candidato"])}
            f = e9_efe[(e9_efe["ciclo"] == ciclo) & (e9_efe["modelo"] == MOD_E9) &
                       (e9_efe["conjunto"] == "principal") & (e9_efe["especificacao"] == ESPEC_E9) &
                       (e9_efe["termo"] == B)].set_index("quantidade")
            novo = pd.DataFrame(r["_efeitos"]).set_index("quantidade")
            q = ["razao_chances_por_5mil", "log_razao_chances_por_5mil", "variacao_prob_media_pp"]
            difs["efeitos_razao_chances_e_prob"] = _dif(novo.loc[q, ["estimativa", "ic95_inf", "ic95_sup"]].to_numpy(),
                                                       f.loc[q, ["estimativa", "ic95_inf", "ic95_sup"]].to_numpy())
        registrar(chave, ok, difs, len(r["termos"]), len(g))
    for chave, modelo, ciclo in (("M1", "M1", EMPILHADO), ("M5_1", "M5", "1"), ("M5_2", "M5", "2"),
                                 ("M5_3", "M5", "3")):
        r = res[chave]
        g = p1_est[(p1_est["modelo"] == modelo) & (p1_est["ciclo"] == ciclo) &
                   (p1_est["tipo_linha"] == "coeficiente")].set_index("termo")
        ok = list(g.index) == list(r["termos"])
        difs = {}
        if ok:
            difs = {"coef": _dif(r["theta"], g["coef"]),
                    "ep_cluster_conjunto": _dif(ep(r["V_conj"]), g["ep_cluster_conjunto"]),
                    "ep_mle": _dif(ep(r["V_mle"]), g["ep_mle"]),
                    "ep_cluster_candidato": _dif(ep(r["V_cand"]), g["ep_cluster_candidato"])}
        registrar(chave, ok, difs, len(r["termos"]), len(g))
    W, pw = wald_ciclos(res)
    gw = p1_est[(p1_est["modelo"] == "M5") & (p1_est["tipo_linha"] == "wald_igualdade_ciclos")].iloc[0]
    registrar("P1d_wald", True, {"estatistica_wald": abs(W - gw["estatistica_wald"]), "p": abs(pw - gw["p"])}, 1, 1)
    for chave, id_linha, modelo, ciclo in (("M1", "P1h-1", "M1", EMPILHADO), ("M5_1", "P1h-3", "M5", "1"),
                                           ("M5_2", "P1h-3", "M5", "2"), ("M5_3", "P1h-3", "M5", "3")):
        d = d_uf(chave, res[chave])
        g = p1h[(p1h["id_linha"] == id_linha) & (p1h["modelo"] == modelo) & (p1h["ciclo"] == ciclo)]
        ok = len(g) == 1
        difs = {}
        if ok:
            g = g.iloc[0]
            difs = {k: abs(d[k] - g[k]) for k in ("estimativa", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato",
                                                 "ic95_inf", "ic95_sup", "p_unilateral")}
        registrar(f"D_UF_{chave}", ok, difs, 1, int(len(g)) if not ok else 1)
    return {"status": "PASSOU" if falha is None else falha, "tolerancia": tol,
            "regra": ("versão antiga reestimada com as funções dos scripts 16, 25 e 25c contra E9_estimativas.csv e "
                      "E9_efeitos_marginais.csv (E9 principal, ciclo 2 e empilhado), P1_estimativas.csv (M1, M5 por "
                      "ciclo, todos os termos, e o Wald do P1d) e P1h_magnitudes.csv (D_UF no M1 e no M5 por ciclo); "
                      "coeficientes, os três EP, IC e p; diferença máxima ≤ 1e−8 (os CSV têm 10 algarismos "
                      "significativos)"),
            "linhas": linhas}


# ---------------------------------------------------------------------------
# Linhas de saída
# ---------------------------------------------------------------------------

def _linha(**kw) -> dict:
    base = {c: np.nan for c in COLUNAS}
    base.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "entra_holm": False, "familia_holm": "",
                 "rejeita_h0_5pct": None, "nota": ""})
    base.update(kw)
    return base


def _comuns(versao: str, chave: str, r: dict) -> dict:
    bloco, modelo, ciclo = next((b, m, c) for k, b, m, c in MODELOS if k == chave)
    n_alt = r.get("n_alternativas", r.get("n_linhas"))
    return {"versao": versao, "versao_quadro_ciclo2": "19/03/2026" if versao == ANTIGA else "13/02/2026",
            "bloco": bloco, "chave_modelo": chave, "modelo": modelo, "ciclo": ciclo, "g_conjuntos": r["G_conj"],
            "g_candidatos": r["G_cand"], "n_candidatos": r["n_candidatos"], "n_alternativas_ou_linhas": n_alt,
            "n_conjuntos": r["n_conjuntos"]}


def linhas_versao(versao: str, res: dict) -> list[dict]:
    out = []
    for chave, *_ in MODELOS:
        r = res[chave]
        c = _comuns(versao, chave, r)
        for k, t in enumerate(r["termos"]):
            b = float(r["theta"][k])
            e = math.sqrt(r["V_conj"][k, k])
            z = b / e
            linha = _linha(**c, tipo_linha="coeficiente", termo=t, estimativa=b, ep_cluster_conjunto=e,
                           ep_mle=math.sqrt(r["V_mle"][k, k]), ep_cluster_candidato=math.sqrt(r["V_cand"][k, k]),
                           ic95_inf=b - Z95 * e, ic95_sup=b + Z95 * e, p=float(2 * stats.norm.sf(abs(z))),
                           p_t_g_menos_1=float(2 * stats.t.sf(abs(z), r["G_conj"] - 1)),
                           nota=("coeficiente da utilidade por R$ 1 mil/mês" if t == B else "coeficiente da utilidade"))
            if chave == "M1" and t == B:
                linha.update(entra_holm=True, familia_holm="P1a (protocolo 52, §4): família de um teste, bilateral",
                             p_holm=float(L.holm(np.array([linha["p"]]))[0]))
                linha["rejeita_h0_5pct"] = bool(linha["p_holm"] < ALFA)
            elif t == B and chave.startswith("E9"):
                linha["nota"] += "; E9 secundário e exploratório (protocolo 40, §12): sem Holm"
            out.append(linha)
        kb = r["termos"].index(B)
        b = float(r["theta"][kb])
        e = math.sqrt(r["V_conj"][kb, kb])
        e_m = math.sqrt(r["V_mle"][kb, kb])
        e_k = math.sqrt(r["V_cand"][kb, kb])
        if chave.startswith("E9"):
            f = pd.DataFrame(r["_efeitos"]).set_index("quantidade")
            orr = f.loc["razao_chances_por_5mil"]
            vp = f.loc["variacao_prob_media_pp"]
            out.append(_linha(**c, tipo_linha="razao_chances_por_5mil", termo=B, estimativa=orr["estimativa"],
                              ep_cluster_conjunto=orr["ep_cluster_conjunto"], ep_mle=orr["ep_mle"],
                              ic95_inf=orr["ic95_inf"], ic95_sup=orr["ic95_sup"],
                              p=float(2 * stats.norm.sf(abs(b / e))),
                              nota="exp(5·coef.), IC = exp do IC do log (função linhas_efeitos do script 16); p = o do "
                                   "coeficiente da bolsa"))
            out.append(_linha(**c, tipo_linha="variacao_prob_media_pp", termo=B, estimativa=vp["estimativa"],
                              ep_cluster_conjunto=vp["ep_cluster_conjunto"], ep_mle=vp["ep_mle"],
                              ic95_inf=vp["ic95_inf"], ic95_sup=vp["ic95_sup"],
                              nota="variação média da probabilidade de escolha (p.p.) por +R$ 5 mil, delta (script 16)"))
        else:
            orr = math.exp(PASSO_BOLSA * b)
            out.append(_linha(**c, tipo_linha="razao_chances_por_5mil", termo=B, estimativa=orr,
                              ep_cluster_conjunto=orr * PASSO_BOLSA * e, ep_mle=orr * PASSO_BOLSA * e_m,
                              ep_cluster_candidato=orr * PASSO_BOLSA * e_k,
                              ic95_inf=math.exp(PASSO_BOLSA * (b - Z95 * e)),
                              ic95_sup=math.exp(PASSO_BOLSA * (b + Z95 * e)),
                              p=float(2 * stats.norm.sf(abs(b / e))),
                              nota="exp(5·coef.), IC = exp do IC do log, EP pelo delta (como na síntese 57); p = o do "
                                   "coeficiente da bolsa"))
            d = d_uf(chave, r)
            linha = _linha(**c, tipo_linha="D_UF", termo="D_UF = θ_UF − 10·β", estimativa=d["estimativa"],
                           ep_cluster_conjunto=d["ep_cluster_conjunto"], ep_mle=d["ep_mle"],
                           ep_cluster_candidato=d["ep_cluster_candidato"], ic95_inf=d["ic95_inf"],
                           ic95_sup=d["ic95_sup"], li95_unilateral=d["li95_unilateral"],
                           p_unilateral=d["p_unilateral"], p_t_g_menos_1=d["p_unilateral_t_g_menos_1"],
                           nota="H0: D_UF ≤ 0 contra H1: D_UF > 0; função linha_dif_uf do script 25c; "
                                "p_t_g_menos_1 aqui é o unilateral pela t")
            if chave == "M1":
                linha.update(entra_holm=True, familia_holm="P1h-1 (protocolo 52b, §3): família de um teste, unilateral",
                             p_holm=float(L.holm(np.array([d["p_unilateral"]]))[0]))
                linha["rejeita_h0_5pct"] = bool(linha["p_holm"] < ALFA)
            else:
                linha["nota"] += ("; sensibilidade P1h-3 (só o M5; o BKY da família P1h-3 não é refeito porque M2, M4 "
                                  "e M7 não fazem parte do adendo)")
            out.append(linha)
    W, pw = wald_ciclos(res)
    out.append(_linha(versao=versao, versao_quadro_ciclo2="19/03/2026" if versao == ANTIGA else "13/02/2026",
                      bloco="P1", chave_modelo="M5", modelo="M5", ciclo="1,2,3", tipo_linha="wald_igualdade_ciclos",
                      termo="wald_bolsa_igual_entre_ciclos", estatistica_wald=W, gl=2, p=pw, g_conjuntos=np.nan,
                      nota="P1d: EP cluster por conjunto de cada ciclo; ciclos como amostras independentes (script 25); "
                           "o q BKY da família secundária do P1 não é refeito (o M6 e o M8 também usam o ciclo 2 e "
                           "não fazem parte do adendo)"))
    return out


def montar(res_a: dict, res_c: dict) -> pd.DataFrame:
    est = pd.DataFrame(linhas_versao(ANTIGA, res_a) + linhas_versao(CORRIGIDA, res_c))[COLUNAS]
    est["entra_holm"] = est["entra_holm"].astype(bool)
    return est


def conferir_mesma_amostra(res_a: dict, res_c: dict) -> dict:
    """Mesma amostra, mesmos conjuntos, mesmos termos; ciclos 1 e 3 do M5 idênticos (só o ciclo 2 muda)."""
    out = {}
    for chave, *_ in MODELOS:
        a, c = res_a[chave], res_c[chave]
        chaves = ("n_candidatos", "n_conjuntos", "n_grupos_escolha", "n_alternativas", "n_grupos", "n_linhas")
        iguais = all(a.get(k) == c.get(k) for k in chaves) and a["termos"] == c["termos"]
        if not iguais:
            raise FalhaValidacao(f"{chave}: amostra, conjunto ou termos diferentes entre as versões")
        out[chave] = {k: a.get(k) for k in chaves if a.get(k) is not None}
    for chave in ("M5_1", "M5_3"):
        d = _dif(res_a[chave]["theta"], res_c[chave]["theta"])
        if d > 0:
            raise FalhaValidacao(f"{chave} mudou com a correção do ciclo 2 (dif. {d})")
        out[chave]["dif_max_coef_antiga_corrigida"] = d
    return out


# ---------------------------------------------------------------------------
# Leitura (regras fixadas antes de rodar a versão corrigida)
# ---------------------------------------------------------------------------

def _sel(est: pd.DataFrame, versao: str, chave: str, tipo: str, termo: str | None = None) -> pd.Series:
    s = est[(est["versao"] == versao) & (est["chave_modelo"] == chave) & (est["tipo_linha"] == tipo)]
    if termo is not None:
        s = s[s["termo"] == termo]
    if len(s) != 1:
        raise FalhaValidacao(f"esperava 1 linha {versao} {chave} {tipo} {termo}, achei {len(s)}")
    return s.iloc[0]


def _verdadeiro(v) -> bool:
    return str(v).strip().lower() in ("true", "1")


def leitura(est: pd.DataFrame) -> dict:
    """Decisões nas duas versões, pelas regras dos protocolos: P1h-1 e P1a por Holm a 5%; o 'sinal do ciclo 2' do E9
    pelo IC 95% da razão de chances excluir 1 (doc 44, doc 57)."""
    out = {}
    for v in VERSOES:
        h2 = _sel(est, v, "M1", "D_UF")
        p1a = _sel(est, v, "M1", "coeficiente", B)
        e9 = _sel(est, v, "E9_2", "razao_chances_por_5mil")
        e9e = _sel(est, v, "E9_emp", "razao_chances_por_5mil")
        m52 = _sel(est, v, "M5_2", "razao_chances_por_5mil")
        out[v] = {"H2_P1h1_rejeita": _verdadeiro(h2["rejeita_h0_5pct"]),
                  "P1a_rejeita": _verdadeiro(p1a["rejeita_h0_5pct"]),
                  "E9_ciclo2_ic_exclui_1": bool(e9["ic95_inf"] > 1 or e9["ic95_sup"] < 1),
                  "E9_empilhado_ic_exclui_1": bool(e9e["ic95_inf"] > 1 or e9e["ic95_sup"] < 1),
                  "M5_ciclo2_ic_exclui_1": bool(m52["ic95_inf"] > 1 or m52["ic95_sup"] < 1)}
    a, c = out[ANTIGA], out[CORRIGIDA]
    out["muda"] = {k: a[k] != c[k] for k in a}
    out["muda_H2"] = out["muda"]["H2_P1h1_rejeita"]
    out["muda_sinal_ciclo2"] = out["muda"]["E9_ciclo2_ic_exclui_1"]
    out["muda_alguma_leitura"] = any(out["muda"].values())
    return out


# ---------------------------------------------------------------------------
# Figura
# ---------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 12})
    return plt


COR = {ANTIGA: "#8a8984", CORRIGIDA: "#2a78d6"}


def titulo_figura(lei: dict) -> str:
    if not lei["muda_alguma_leitura"]:
        return "Corrigir o tipo de vaga do ciclo 2 para o quadro da inscrição não muda a leitura"
    return "Corrigir o tipo de vaga do ciclo 2 para o quadro da inscrição muda parte da leitura"


def figura(est: pd.DataFrame, lei: dict) -> dict:
    plt = _plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.4), gridspec_kw={"width_ratios": [1.25, 1.0]})
    paineis = [(ax1, ["E9_2", "E9_emp", "M1", "M5_1", "M5_2", "M5_3"], "razao_chances_por_5mil",
                "razão de chances por +R$ 5 mil (escala log), IC 95%", 1.0, True),
               (ax2, ["M1", "M5_1", "M5_2", "M5_3"], "D_UF", "D_UF = θ_UF − 10·β (log-chance), IC 95%", 0.0, False)]
    for ax, chaves, tipo, xlab, ref, logx in paineis:
        y0 = np.arange(len(chaves))[::-1].astype(float)
        for yi, chave in zip(y0, chaves):
            for v, dy in ((ANTIGA, 0.17), (CORRIGIDA, -0.17)):
                r = _sel(est, v, chave, tipo)
                ax.plot([r["ic95_inf"], r["ic95_sup"]], [yi + dy] * 2, color=COR[v], lw=2.4, solid_capstyle="round")
                ax.plot([r["estimativa"]], [yi + dy], "o", ms=9, zorder=3,
                        mfc="white" if v == ANTIGA else COR[v], mec=COR[v], mew=2.0)
                ax.text(r["ic95_sup"] * (1.04 if logx else 1.0) + (0 if logx else 0.06), yi + dy,
                        _n(r["estimativa"], 2), va="center", ha="left", fontsize=10.5, color="#2b2b29")
        ax.axvline(ref, color="#52514e", lw=1.0)
        ax.set_yticks(y0)
        ax.set_yticklabels([ROTULO_CURTO[k] for k in chaves], fontsize=12)
        ax.set_xlabel(xlab, fontsize=11.5)
        if logx:
            ax.set_xscale("log")
            ticks = [0.6, 0.8, 1.0, 1.5, 2.0, 3.0]
            ax.set_xticks(ticks)
            ax.set_xticklabels([_n(t, 1) for t in ticks])
            ax.minorticks_off()
            lo = min(0.55, float(est.loc[est["tipo_linha"] == tipo, "ic95_inf"].min()) * 0.95)
            hi = float(est.loc[est["tipo_linha"] == tipo, "ic95_sup"].max()) * 1.35
            ax.set_xlim(lo, hi)
        else:
            sub = est[est["tipo_linha"] == tipo]
            ax.set_xlim(min(-0.2, float(sub["ic95_inf"].min()) - 0.2), float(sub["ic95_sup"].max()) + 0.7)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.grid(axis="x", color="#e6e5e0", lw=0.6)
        ax.set_axisbelow(True)
    from matplotlib.lines import Line2D
    leg = [Line2D([0], [0], marker="o", color=COR[ANTIGA], mfc="white", mec=COR[ANTIGA], mew=2, lw=2.4,
                  label="antiga: tipo de vaga do ciclo 2 pelo quadro de 19/03/2026 (pós-resultado)"),
           Line2D([0], [0], marker="o", color=COR[CORRIGIDA], mfc=COR[CORRIGIDA], mec=COR[CORRIGIDA], lw=2.4,
                  label="corrigida: quadro de 13/02/2026 (vigente na inscrição)")]
    fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.012, 0.905), ncol=2, frameon=False, fontsize=10.5)
    fig.text(0.012, 0.975, titulo_figura(lei), fontsize=15, ha="left", va="top", color="#1f1f1d")
    fig.text(0.012, 0.02, "Escolha da 1ª opção, condicional a se candidatar; IC 95% com cluster por conjunto de escolha "
             "(curso × ciclo). Bolsa: pacote do corte; origem: preferência revelada, não efeito causal.",
             fontsize=9.5, color="#52514e", ha="left", va="bottom")
    fig.subplots_adjust(left=0.13, right=0.985, top=0.80, bottom=0.17, wspace=0.42)
    fig.savefig(FIG, dpi=150, metadata={"Software": None})
    plt.close(fig)
    return {"arquivo": rel(FIG), "sha256": sha256(FIG), "titulo": titulo_figura(lei), "como_ler": COMO_LER}


# ---------------------------------------------------------------------------
# Documento 57p
# ---------------------------------------------------------------------------

def bloco(nome: str, corpo: str) -> list[str]:
    return [f"<!-- VC:{nome}:inicio -->", corpo, f"<!-- VC:{nome}:fim -->"]


def _sci(v) -> str:
    return "—" if v is None else f"{v:.1e}".replace(".", ",").replace("-", "−")


def texto_resposta(est: pd.DataFrame, resumo: dict) -> str:
    lei = resumo["leitura"]
    a, c = ANTIGA, CORRIGIDA
    h2a, h2c = _sel(est, a, "M1", "D_UF"), _sel(est, c, "M1", "D_UF")
    e9a, e9c = _sel(est, a, "E9_2", "razao_chances_por_5mil"), _sel(est, c, "E9_2", "razao_chances_por_5mil")
    eea, eec = _sel(est, a, "E9_emp", "razao_chances_por_5mil"), _sel(est, c, "E9_emp", "razao_chances_por_5mil")
    m1a, m1c = _sel(est, a, "M1", "coeficiente", B), _sel(est, c, "M1", "coeficiente", B)
    o1a, o1c = _sel(est, a, "M1", "razao_chances_por_5mil"), _sel(est, c, "M1", "razao_chances_por_5mil")
    m5a, m5c = _sel(est, a, "M5_2", "razao_chances_por_5mil"), _sel(est, c, "M5_2", "razao_chances_por_5mil")
    t = []
    # H2
    dec = {True: "rejeita H0 (D_UF ≤ 0) depois do Holm", False: "não rejeita H0 depois do Holm"}
    if not lei["muda_H2"]:
        t.append(f"**H2 (bolsa × origem): a leitura não muda.** No M1, D_UF = θ_UF − 10·β passa de "
                 f"{_n(h2a['estimativa'], 2)} (IC 95% {_ic(h2a['ic95_inf'], h2a['ic95_sup'], 2)}; "
                 f"{_peq(h2a['p_unilateral'])}, unilateral) para {_n(h2c['estimativa'], 2)} "
                 f"(IC {_ic(h2c['ic95_inf'], h2c['ic95_sup'], 2)}; {_peq(h2c['p_unilateral'])}); nas duas versões o "
                 f"P1h-1 {dec[lei[c]['H2_P1h1_rejeita']]} (família de um teste, p de Holm = p). No modelo de escolha, "
                 + ("a amplitude inteira da bolsa (R$ 10 → 20 mil) continua pesando menos que a vaga ficar na UF de "
                    "origem." if lei[c]["H2_P1h1_rejeita"] else
                    "os dados continuam sem separar o peso da UF de origem do de toda a amplitude da bolsa."))
    else:
        t.append(f"**H2 (bolsa × origem): a leitura muda.** No M1, D_UF passa de {_n(h2a['estimativa'], 2)} "
                 f"(IC {_ic(h2a['ic95_inf'], h2a['ic95_sup'], 2)}; {_peq(h2a['p_unilateral'])}) para "
                 f"{_n(h2c['estimativa'], 2)} (IC {_ic(h2c['ic95_inf'], h2c['ic95_sup'], 2)}; "
                 f"{_peq(h2c['p_unilateral'])}): na versão antiga o P1h-1 {dec[lei[a]['H2_P1h1_rejeita']]}; na "
                 f"corrigida, {dec[lei[c]['H2_P1h1_rejeita']]}. Pelo adendo 52c, §2, vale a corrigida.")
    # Sinal do ciclo 2
    exc = {True: "exclui 1", False: "contém 1"}
    frase_e9 = (f"No E9 do ciclo 2, a razão de chances por +R$ 5 mil passa de {_n(e9a['estimativa'], 2)} "
                f"(IC {_ic(e9a['ic95_inf'], e9a['ic95_sup'], 2)}) para {_n(e9c['estimativa'], 2)} "
                f"(IC {_ic(e9c['ic95_inf'], e9c['ic95_sup'], 2)})")
    if not lei["muda_sinal_ciclo2"]:
        t.append(f"**\"Sinal do ciclo 2\" (E9): a leitura não muda.** {frase_e9}; o IC {exc[lei[c]['E9_ciclo2_ic_exclui_1']]} "
                 f"nas duas versões. Com distância e origem (P1 M5, ciclo 2): de {_n(m5a['estimativa'], 2)} "
                 f"{_ic(m5a['ic95_inf'], m5a['ic95_sup'], 2)} para {_n(m5c['estimativa'], 2)} "
                 f"{_ic(m5c['ic95_inf'], m5c['ic95_sup'], 2)}. O E9 continua secundário e exploratório, sem Holm, e as "
                 "fragilidades do doc 42 (só o ciclo 2; spline cúbico) não são reavaliadas aqui.")
    else:
        t.append(f"**\"Sinal do ciclo 2\" (E9): a leitura muda.** {frase_e9}: o IC {exc[lei[a]['E9_ciclo2_ic_exclui_1']]} "
                 f"na versão antiga e {exc[lei[c]['E9_ciclo2_ic_exclui_1']]} na corrigida. Pelo adendo 52c, §2, vale a "
                 "corrigida; a síntese (doc 57) precisa registrar isso numa nota datada, por adendo ao script 33.")
    # P1a e empilhado
    t.append(f"**P1a (M1, ciclos 1–3) e E9 empilhado.** O coeficiente da bolsa no M1 passa de {_n(m1a['estimativa'], 4)} "
             f"(IC {_ic(m1a['ic95_inf'], m1a['ic95_sup'], 4)}; p de Holm {_p(m1a['p_holm'])}; razão de chances "
             f"{_n(o1a['estimativa'], 2)}) para {_n(m1c['estimativa'], 4)} (IC {_ic(m1c['ic95_inf'], m1c['ic95_sup'], 4)}; "
             f"p de Holm {_p(m1c['p_holm'])}; razão de chances {_n(o1c['estimativa'], 2)}): "
             + ("a decisão do P1a não muda" if not lei["muda"]["P1a_rejeita"] else "a decisão do P1a muda")
             + f" ({'rejeita' if lei[c]['P1a_rejeita'] else 'não rejeita'} zero na corrigida). No E9 empilhado, a razão "
             f"de chances vai de {_n(eea['estimativa'], 2)} {_ic(eea['ic95_inf'], eea['ic95_sup'], 2)} para "
             f"{_n(eec['estimativa'], 2)} {_ic(eec['ic95_inf'], eec['ic95_sup'], 2)}.")
    cv = resumo["correcao"]
    t.append(f"**O que a correção mexe.** No ciclo 2, {cv['celulas_de_reserva_em_13fev_com_imediata_em_19mar']} das "
             f"{cv['celulas_ciclo2_no_conjunto']} células do conjunto eram só de reserva na inscrição e aparecem com vaga "
             f"imediata no quadro de 19/03; a concordância de \"tem vaga imediata\" entre os dois quadros é "
             f"{_n(100 * cv['concordancia_tem_vaga_imediata'], 1)}%. Das {resumo['escolhas_ciclo2']['candidatos_1a_opcao_ciclo2']} "
             f"1ªs opções do ciclo 2, {_n(100 * resumo['escolhas_ciclo2'][f'fracao_em_celula_com_vaga_imediata_{a}'], 1)}% "
             f"estão em célula com vaga imediata pelo quadro de 19/03 e "
             f"{_n(100 * resumo['escolhas_ciclo2'][f'fracao_em_celula_com_vaga_imediata_{c}'], 1)}% pelo de 13/02. "
             "A versão corrigida é a de referência (adendo 52c, §2).")
    t.append("Tudo acima é escolha condicional a se candidatar, dentro das vagas abertas. O contraste da bolsa é o pacote "
             "do corte (bolsa e outras regras federais nos mesmos cortes, auditoria 18) e o incentivo marginal; não é "
             "efeito da participação no PMM-E nem do Agora Tem Especialistas.")
    return "\n\n".join(t)


def texto_portao(resumo: dict) -> str:
    p = resumo["portao"]
    linhas = []
    for e in p["linhas"]:
        difs = {k[len("dif_max_"):]: v for k, v in e.items() if k.startswith("dif_max_")}
        linhas.append([e["linha"], f"{e['termos_reestimados']} / {e['termos_gravados']}",
                       _sci(max(difs.values())) if difs else "—", ", ".join(sorted(difs)) or "—",
                       "passou" if e["passou"] else "**falhou**"])
    t = [f"**Portão de reprodução: {p['status']}.** Com a covariável antiga, as funções originais (scripts 16, 25 e "
         "25c, importadas sem alteração) reproduzem os números gravados em `E9_estimativas.csv`, "
         "`E9_efeitos_marginais.csv`, `P1_estimativas.csv` e `P1h_magnitudes.csv`. Tolerância 1e−8 na diferença "
         "máxima absoluta de cada quantidade comparada.", "",
         _tab(["Linha", "Termos (reestimados / gravados)", "Dif. máx.", "Quantidades comparadas", "Portão"], linhas)]
    if p["status"] != "PASSOU":
        t += ["", f"A execução parou em `{p['status']}`: a covariável não foi trocada (adendo 52c)."]
    return "\n".join(t)


def texto_correcao(resumo: dict) -> str:
    cv = resumo["correcao"]
    ec = resumo["escolhas_ciclo2"]
    linhas = [
        ["células do ciclo 2 no conjunto de escolha", _n(cv["celulas_ciclo2_no_conjunto"], 0), "—"],
        ["células sem linha (ou sem número) no quadro de 13/02", "—",
         _n(cv["celulas_sem_linha_no_quadro_1302"] + cv["celulas_sem_numero_de_vagas_imediatas_no_quadro_1302"], 0)],
        ["células com vaga imediata", _n(cv["celulas_com_vaga_imediata_19mar"], 0),
         _n(cv["celulas_com_vaga_imediata_13fev"], 0)],
        ["vagas imediatas somadas nas células", _n(cv["vagas_imediatas_total_19mar"], 0),
         _n(cv["vagas_imediatas_total_13fev"], 0)],
        ["1ªs opções do ciclo 2 (E9) em célula com vaga imediata",
         f"{ec[f'em_celula_com_vaga_imediata_{ANTIGA}']} de {ec['candidatos_1a_opcao_ciclo2']}",
         f"{ec[f'em_celula_com_vaga_imediata_{CORRIGIDA}']} de {ec['candidatos_1a_opcao_ciclo2']}"],
    ]
    t = [_tab(["Item", "Antiga (19/03/2026)", "Corrigida (13/02/2026)"], linhas), "",
         f"- Células que eram só de reserva em 13/02 e têm vaga imediata em 19/03: "
         f"{cv['celulas_de_reserva_em_13fev_com_imediata_em_19mar']}; o inverso: "
         f"{cv['celulas_com_imediata_em_13fev_e_reserva_em_19mar']}. Células com número de vagas imediatas diferente: "
         f"{cv['celulas_com_vagas_imediatas_diferentes']}. Concordância de \"tem vaga imediata\": "
         f"{_n(100 * cv['concordancia_tem_vaga_imediata'], 1)}%.",
         f"- Município e faixa das células iguais nos dois quadros (diferenças: "
         f"{cv['celulas_com_municipio_diferente_19mar_13fev']} e {cv['celulas_com_faixa_diferente_19mar_13fev']}). "
         "Nada imputado; nenhuma célula retirada.",
         f"- Conferências: a covariável antiga do conjunto é a do quadro de 19/03 em "
         f"{resumo['conferencia_versao_antiga']['iguais_ao_quadro_19mar']} de "
         f"{resumo['conferencia_versao_antiga']['celulas']} células; o quadro de 13/02 lido pela função do script 12 "
         f"bate com a leitura independente da auditoria 36 em {resumo['conferencia_a36']['celulas_comparadas']} células "
         f"({resumo['conferencia_a36']['celulas_com_vagas_imediatas_diferentes']} diferenças).",
         "- Ciclos 1 e 3: covariáveis sem mudança; o M5 desses ciclos sai idêntico nas duas versões (conferido)."]
    return "\n".join(t)


def tabela_bolsa(est: pd.DataFrame) -> str:
    linhas = []
    for chave, *_ in MODELOS:
        ca, cc = _sel(est, ANTIGA, chave, "coeficiente", B), _sel(est, CORRIGIDA, chave, "coeficiente", B)
        oa, oc = _sel(est, ANTIGA, chave, "razao_chances_por_5mil"), _sel(est, CORRIGIDA, chave, "razao_chances_por_5mil")
        holm = (f"{_p(ca['p_holm'])} → {_p(cc['p_holm'])}" if bool(ca["entra_holm"]) else
                ("sem Holm (exploratório)" if chave.startswith("E9") else "—"))
        linhas.append([ROTULO_CURTO[chave], _int(cc["n_candidatos"]),
                       f"{_n(ca['estimativa'], 4)} {_ic(ca['ic95_inf'], ca['ic95_sup'], 4)}; {_peq(ca['p'])}",
                       f"{_n(cc['estimativa'], 4)} {_ic(cc['ic95_inf'], cc['ic95_sup'], 4)}; {_peq(cc['p'])}",
                       f"{_n(oa['estimativa'], 2)} {_ic(oa['ic95_inf'], oa['ic95_sup'], 2)}",
                       f"{_n(oc['estimativa'], 2)} {_ic(oc['ic95_inf'], oc['ic95_sup'], 2)}", holm])
    wa = est[(est["versao"] == ANTIGA) & (est["tipo_linha"] == "wald_igualdade_ciclos")].iloc[0]
    wc = est[(est["versao"] == CORRIGIDA) & (est["tipo_linha"] == "wald_igualdade_ciclos")].iloc[0]
    return "\n".join([
        "Coeficiente da bolsa por R$ 1 mil/mês (IC 95% e p bilateral com cluster por conjunto de escolha) e razão de "
        "chances por +R$ 5 mil (exp de 5 × coef.; IC transformado). Holm como nos protocolos: só o P1a (M1), família de "
        "um teste (p de Holm = p); o E9 é secundário e exploratório (protocolo 40, §12), sem Holm; o M5 entra no BKY "
        "da família secundária do P1, que não é refeito aqui.", "",
        _tab(["Especificação", "Candidatos", "Coef. antigo [IC]; p", "Coef. corrigido [IC]; p",
              "Razão de chances antiga [IC]", "Razão de chances corrigida [IC]", "p de Holm (antigo → corrigido)"],
             linhas), "",
        f"P1d, Wald da igualdade de β entre ciclos (M5, χ² com 2 gl): {_n(wa['estatistica_wald'], 2)} "
        f"({_peq(wa['p'])}) na antiga; {_n(wc['estatistica_wald'], 2)} ({_peq(wc['p'])}) na corrigida."])


def _int(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{int(v)}"


def tabela_duf(est: pd.DataFrame) -> str:
    linhas = []
    for chave in ("M1", "M5_1", "M5_2", "M5_3"):
        a, c = _sel(est, ANTIGA, chave, "D_UF"), _sel(est, CORRIGIDA, chave, "D_UF")
        linha_id = "P1h-1" if chave == "M1" else "P1h-3 (sensib.)"
        holm = f"{_p(a['p_holm'])} → {_p(c['p_holm'])}" if bool(a["entra_holm"]) else "—"
        rej = (f"{'sim' if _verdadeiro(a['rejeita_h0_5pct']) else 'não'} → "
               f"{'sim' if _verdadeiro(c['rejeita_h0_5pct']) else 'não'}") if bool(a["entra_holm"]) else "—"
        linhas.append([linha_id, ROTULO_CURTO[chave],
                       f"{_n(a['estimativa'], 3)} {_ic(a['ic95_inf'], a['ic95_sup'], 3)}; LI {_n(a['li95_unilateral'], 3)}; "
                       f"{_peq(a['p_unilateral'])}",
                       f"{_n(c['estimativa'], 3)} {_ic(c['ic95_inf'], c['ic95_sup'], 3)}; LI {_n(c['li95_unilateral'], 3)}; "
                       f"{_peq(c['p_unilateral'])}", holm, rej])
    return "\n".join([
        "D_UF = θ_UF − 10·β (peso de a vaga ficar na UF de origem menos o de toda a amplitude da bolsa), em log-chance; "
        "IC 95% bilateral, limite inferior (LI) unilateral de 95% e p unilateral de H0: D_UF ≤ 0, com cluster por "
        "conjunto. Holm só no P1h-1 (família de um teste, p de Holm = p). As linhas do M5 são as sensibilidades P1h-3 "
        "desse modelo, sem o BKY da família (M2, M4 e M7 não fazem parte do adendo).", "",
        _tab(["Linha", "Especificação", "Antigo: D_UF [IC]; LI; p", "Corrigido: D_UF [IC]; LI; p",
              "p de Holm (antigo → corrigido)", "Rejeita H0 a 5% (antigo → corrigido)"], linhas)])


def tabela_covariaveis(est: pd.DataFrame) -> str:
    linhas = []
    for chave in ("E9_2", "E9_emp", "M1", "M5_2"):
        for t in COVARIAVEIS + ["mesma_uf"]:
            s = est[(est["chave_modelo"] == chave) & (est["termo"] == t) & (est["tipo_linha"] == "coeficiente")]
            if s.empty:
                continue
            a, c = s[s["versao"] == ANTIGA].iloc[0], s[s["versao"] == CORRIGIDA].iloc[0]
            linhas.append([ROTULO_CURTO[chave], f"`{t}`", f"{_n(a['estimativa'], 3)} {_ic(a['ic95_inf'], a['ic95_sup'], 3)}",
                           f"{_n(c['estimativa'], 3)} {_ic(c['ic95_inf'], c['ic95_sup'], 3)}"])
    return "\n".join([
        "Coeficientes das covariáveis corrigidas (e de mesma UF, que entra no D_UF) nas duas versões, IC 95% com cluster "
        "por conjunto. Todos os termos de todas as especificações estão em `output/rdd_bolsa/VC_estimativas.csv`.", "",
        _tab(["Especificação", "Termo", "Antigo [IC]", "Corrigido [IC]"], linhas)])


def texto_figura(resumo: dict) -> str:
    f = resumo["figura"]
    return "\n".join([f"![{f['titulo']}](../../{f['arquivo']})", "",
                      f"Arquivo: `{f['arquivo']}`. Título: \"{f['titulo']}\".", "",
                      f"**Como ler.** {f['como_ler']}"])


DESVIOS = [
    {"data": "2026-10-26", "item": "Célula ausente no quadro de 13/02",
     "situacao": "O pedido do autor manda registrar e contar; o adendo não diz o que fazer com ela.",
     "resolucao": "A execução para (FALHA_CELULA_AUSENTE_1302) se alguma célula do conjunto do ciclo 2 não tiver linha "
                  "ou número de vagas imediatas no quadro de 13/02: não se imputa e não se retira célula, porque a "
                  "amostra e o conjunto têm de ser os mesmos. A contagem foi zero."},
    {"data": "2026-10-26", "item": "D_UF no M5",
     "situacao": "O adendo pede P1h-1 (M1) e o M5 do P1; o D_UF do M5 é sensibilidade P1h-3.",
     "resolucao": "O D_UF do M5 por ciclo é relatado como sensibilidade, com portão próprio contra P1h_magnitudes.csv, "
                  "sem o BKY da família P1h-3 (M2, M4 e M7 não são reestimados)."},
    {"data": "2026-10-26", "item": "Razão de chances do P1",
     "situacao": "O P1 não gravou razão de chances; o E9 gravou (script 16).",
     "resolucao": "E9: a função linhas_efeitos do script 16 (reproduzida no portão). P1: exp(5·coef.) com o IC "
                  "transformado do IC do coeficiente, a mesma conta da síntese 57."},
    {"data": "2026-10-26", "item": "BKY das secundárias do P1",
     "situacao": "O P1d (Wald entre ciclos) entra no BKY da família secundária do P1, com o M6 e o M8, que também usam o "
                 "ciclo 2 e não fazem parte do adendo.",
     "resolucao": "O Wald do P1d é relatado nas duas versões, sem q BKY refeito."},
]


def texto_desvios(resumo: dict) -> str:
    def data_br(iso: str) -> str:
        a, m, d = iso.split("-")
        return f"{d}/{m}/{a}"
    t = ["Decisões de implementação onde o adendo não fixava o detalhe. Elas estão no mesmo commit dos números. Nenhuma "
         "muda a amostra, o conjunto de escolha ou a especificação dos modelos.", ""]
    for i, d in enumerate(resumo["desvios"], 1):
        t.append(f"{i}. **{d['item']}** ({data_br(d['data'])}). {d['situacao']} *Resolução:* {d['resolucao']}")
    return "\n".join(t)


def gerar_doc(est: pd.DataFrame | None, resumo: dict) -> str:
    ok = resumo["portao"]["status"] == "PASSOU" and est is not None
    Lh = [
        "# 57p. Escolha com o tipo de vaga do ciclo 2 medido antes da alocação (adendo 52c)",
        "",
        "> **Gerado por** `scripts/rdd_bolsa/42_escolha_vaga_imediata_c2.py` a partir de `output/rdd_bolsa/VC_*`; não "
        "editar à mão (o teste `tests/test_escolha_vaga_imediata_c2.py` confere que este arquivo é igual ao gerado; "
        "`--atualizar-doc` o regrava das saídas).<br>",
        "> **Adendo:** [`52c_adendo_vaga_imediata_ciclo2.md`](52c_adendo_vaga_imediata_ciclo2.md), congelado em "
        "26/10/2026 antes de reestimar; estatuto `ADENDO_52C_CORRECAO_COVARIAVEL`. Protocolos de origem: "
        "[40](40_protocolo_multioutcome_rdd_bolsa.md) (E9, §12), [52](52_protocolo_P1_escolha_dap.md) (P1) e "
        "[52b](52b_protocolo_P1h_magnitudes.md) (P1h).<br>",
        "> **Motivo:** [auditoria 36](../auditorias/36_auditoria_dados_H1.md), seção 3, item 3, e seção 10a: no ciclo 2, "
        "\"tem vaga imediata\" e \"log(vagas imediatas + 1)\" vinham do quadro retificado de 19/03/2026, refeito depois do "
        "resultado preliminar (10/03). A correção usa o quadro de 13/02/2026, vigente na inscrição.<br>",
        "> **Saídas:** `output/rdd_bolsa/VC_estimativas.csv`, `VC_resumo.json` e `VC_figuras/VC_antigo_corrigido.png`; "
        "toda linha tem `natureza_dos_dados = EMPIRICO`. As saídas do E9, do P1 e do P1h (`E9_*`, `P1_*`, `P1h_*`) não "
        "são regravadas, e os docs 42, 57a, 57i e 57 não são editados.",
        "",
        "## 1. Resposta curta",
        "",
    ]
    if ok:
        Lh += [*bloco("resposta", texto_resposta(est, resumo)), ""]
    else:
        Lh += [*bloco("resposta", f"Nada corrigido: `{resumo['portao']['status']}`."), ""]
    Lh += ["## 2. Portão de reprodução (versão antiga)", "", *bloco("portao", texto_portao(resumo)), ""]
    if ok:
        Lh += [
            "## 3. A correção da covariável",
            "",
            *bloco("correcao", texto_correcao(resumo)),
            "",
            "## 4. Tabelas: antigo e corrigido lado a lado",
            "",
            "### 4.1 Peso da bolsa (E9, P1a e P1d)",
            "",
            *bloco("bolsa", tabela_bolsa(est)),
            "",
            "### 4.2 Bolsa contra origem (H2: P1h-1, D_UF)",
            "",
            *bloco("duf", tabela_duf(est)),
            "",
            "### 4.3 Covariáveis corrigidas",
            "",
            *bloco("covariaveis", tabela_covariaveis(est)),
            "",
            "## 5. Figura",
            "",
            *bloco("figura", texto_figura(resumo)),
            "",
        ]
    Lh += [
        "## 6. Decisões de implementação",
        "",
        *bloco("desvios", texto_desvios(resumo)),
        "",
        "## 7. Limites",
        "",
        "- **Pós-resultado.** O E9, o P1 e o P1h já eram conhecidos, e a auditoria 36 apontou o problema depois deles. O "
        "adendo foi congelado antes de reestimar, mas a correção não é teste confirmatório novo.",
        "- **Só o tipo de vaga do ciclo 2 muda.** O conjunto de sensibilidade \"só células com vaga imediata\" do E9, o "
        "M2, o M4, o M6, o M7, o M8 e o M9 do P1, a DAP e as sensibilidades P1h-3 fora do M5 continuam com o quadro de "
        "19/03 e não foram reestimados. O BKY das famílias secundárias não é refeito.",
        "- **O quadro de 13/02 também é anúncio.** Ele mede o que estava publicado na inscrição, não a vaga que de fato "
        "seria preenchida: o remanejamento posterior (item 5.7 dos editais) fica fora do atributo, como deve ficar num "
        "controle pré-tratamento.",
        "- **Escolha condicional.** Tudo vale para quem se candidatou, dentro das vagas abertas do seu curso e ciclo; "
        "o conjunto de escolha supõe que o candidato viu todas as células do curso; IIA do logit condicional.",
        "- **Pacote do corte.** O peso da bolsa é identificado pelos saltos nos cortes de IVS (0,300 e 0,400), com o IVS "
        "em spline contínua; em 0,300 e 0,400 mudam também outras regras federais (auditoria 18) e há desequilíbrio de "
        "capitais em 0,300 (auditoria 36, seção 7). Não é efeito da participação no PMM-E.",
        "- **Origem não é causal.** θ_UF é preferência revelada condicional ao modelo; a origem é o município do vínculo "
        "médico no CNES, não a residência.",
        "- **Poucos conjuntos.** 16 a 24 conjuntos (curso × ciclo) por ciclo e 56 nos ciclos empilhados; o EP com "
        "cluster por conjunto é impreciso, e o p pela t com G − 1 gl está no CSV.",
    ]
    return "\n".join(Lh) + "\n"


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def entradas(dados: dict) -> list[dict]:
    be = P1.bloco_entrada
    return [
        be(ADENDO_MD, "adendo 52c (especificação, somente lido)", "repositório", "2026-10-26", "§1–§3", "documento",
           "-", "-"),
        be(PROTOCOLO_52, "protocolo 52 (P1; somente lido)", "repositório", "2026-10-19", "§1–§6", "documento", "-", "-"),
        be(PROTOCOLO_52B, "protocolo 52b (P1h; somente lido)", "repositório", "2026-10-26", "§1–§6", "documento", "-",
           "-"),
        be(QUADRO_1302, "quadro da 1ª chamada do ciclo 2, retificado de 13/02/2026 (vigente na inscrição): fonte da "
           "covariável corrigida", "Chamamento SGTES/MS nº 1/2026 (página oficial)", "2026-02-13",
           "1547 células CNES × curso", "célula", "CNES (7 dígitos) × código do curso", "coluna TOTAL de vagas imediatas"),
        be(QUADRO_1903, "quadro do ciclo 2, retificado de 19/03/2026: conferência da versão antiga", "idem", "2026-03-19",
           "1547 células", "célula", "CNES × curso", "coluna TOTAL de vagas imediatas"),
        be(A36_CELULAS, "leitura independente da auditoria 36 (vagas_imediatas_13fev): conferência", "auditoria 36",
           "2026-10-26", "células dos ciclos 1–3", "célula", "cnes, cod_curso", "ciclo = 2"),
        be(A36_RESUMO, "datas das versões do quadro do ciclo 2 (auditoria 36)", "auditoria 36", "2026-10-26", "-",
           "documento", "-", "ciclo2_versoes"),
        be(E9_EST, "alvo do portão (E9 principal, ciclo 2 e empilhado)", "script 16", "2026-10-18", "todos os termos",
           "especificação × termo", "ciclo, modelo, conjunto, especificacao, termo", "principal, spline linear, bolsa linear"),
        be(E9_EFE, "alvo do portão (razão de chances do E9)", "script 16", "2026-10-18", "bolsa_mil",
           "especificação × quantidade", "ciclo, modelo, conjunto, especificacao, termo, quantidade", "idem"),
        be(P1_EST, "alvo do portão (M1, M5, Wald do P1d)", "script 25", "2026-10-23", "todos os termos",
           "especificação × termo", "modelo, ciclo, tipo_linha, termo", "M1, M5"),
        be(P1H_CSV, "alvo do portão (D_UF no M1 e no M5)", "script 25c", "2026-10-26", "P1h-1 e P1h-3 do M5",
           "linha", "id_linha, modelo, ciclo", "-"),
        be(SCRIPT_16, "funções do E9 (importadas sem alteração)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_25, "funções do P1 (importadas sem alteração)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_25C, "função do D_UF (importada sem alteração)", "repositório", "-", "-", "código", "-", "-"),
        be(SCRIPT_12, "função ler_quadro (importada sem alteração)", "repositório", "-", "-", "código", "-", "-"),
        be(E9.ESCOLHAS, "escolhas dos candidatos (1ª opção)", "tarefa B (script 12)", "resultados da 1ª chamada",
           f"{len(dados['cand'])} linhas", "candidato × opção", "ciclo, id_candidato, opcao_rank", "posto 1"),
        be(E9.CONJ_PRINCIPAL, "conjunto de escolha principal (E9 §14); ciclo 2 com a covariável de 19/03",
           "tarefa B (script 12)", "quadros da 1ª chamada", f"{len(dados['conj'])} células com IVS",
           "célula CNES × curso × ciclo", "ciclo, co_cnes_7d, cod_curso", "como no E9 e no P1"),
        be(E9.IVS_OFICIAL, "IVS 2010 oficial (a08)", "Ipea (a08)", "Censo 2010", f"{len(dados['ivs'])} municípios",
           "município", "co_ibge", "co_ibge, ivs"),
        be(P1.G1_ORIGEM, "município de origem (G1)", "portão G1", "referências 202506, 202510, 202602",
           f"{len(dados['org'])} candidatos", "candidato", "ciclo, id_candidato", f"regra_ligacao = {P1.REGRA_G1}"),
        be(P1.G1_DIST, "conferência das distâncias", "portão G1", "idem", "candidato × opção", "candidato × opção",
           "ciclo, id_candidato, opcao_rank", f"regra_ligacao = {P1.REGRA_G1}"),
        be(P1.X45.CIR_BRUTO, "região de saúde (CIR), só lido", "DATASUS/TabNet", dados["manifesto_cir"]["data_download_utc"],
           f"{dados['diag_cir']['municipios']} municípios", "município", "co_ibge → co_cir", "-"),
        be(P1.X1.COORD_JSON, "centroides municipais do IBGE, só lido", "IBGE, API de malhas v3",
           str(dados["diag_coord"].get("data_download", "")), f"{dados['diag_coord'].get('municipios')} municípios",
           "município", "id", "centroide"),
    ]


def remover_saidas_calculadas() -> None:
    for p in (OUT_CSV, FIG):
        if p.exists():
            p.unlink()
    if DIR_FIG.exists() and not any(DIR_FIG.iterdir()):
        DIR_FIG.rmdir()


def covariancias(res: dict) -> dict:
    """θ e blocos da covariância de bolsa e mesma UF, para recálculo nos testes."""
    out = {}
    for chave, *_ in MODELOS:
        r = res[chave]
        termos = [t for t in (B, "mesma_uf") if t in r["termos"]]
        k = [r["termos"].index(t) for t in termos]
        out[chave] = {"termos": termos, "theta": r["theta"][k].tolist(),
                      "V_cluster_conjunto": r["V_conj"][np.ix_(k, k)].tolist(), "g_conjuntos": r["G_conj"]}
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57p a partir das saídas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    t0 = time.time()

    def log(m: str) -> None:
        print(f"[{time.time() - t0:7.0f}s] {m}", flush=True)

    dados = P1.carregar()
    log("insumos do P1 carregados")
    q1302, q1903 = ler_quadros_c2()
    conf_antiga = conferir_versao_antiga(dados["conj"], q1903)
    conf_a36 = conferir_contra_a36(q1302)
    conj_e9_c, corr = corrigir(dados["conj"], q1302)
    conj_p1_c, corr_p1 = corrigir(dados["conj_p1"], q1302)
    esc_c2 = escolhas_c2(dados["cand"], dados["conj"], conj_e9_c)
    log("covariável de 13/02 montada")

    res_a = estimar_versao(dados, dados["conj"], dados["conj_p1"], log)
    port = portao(res_a, pd.read_csv(E9_EST, dtype={"ciclo": str}), pd.read_csv(E9_EFE, dtype={"ciclo": str}),
                  pd.read_csv(P1_EST, dtype={"ciclo": str}), pd.read_csv(P1H_CSV, dtype={"ciclo": str}))
    log(f"portão: {port['status']}")
    resumo = {
        "etapa": "VC_escolha_vaga_imediata_c2",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "adendo": {"arquivo": rel(ADENDO_MD), "sha256": sha256(ADENDO_MD)},
        "protocolos": {rel(p): sha256(p) for p in (PROTOCOLO_52, PROTOCOLO_52B)},
        "portao": port,
        "conferencia_versao_antiga": conf_antiga,
        "conferencia_a36": conf_a36,
        "correcao": {**corr, "conjunto_P1": {k: corr_p1[k] for k in ("celulas_ciclo2_no_conjunto",
                                                                       "celulas_sem_linha_no_quadro_1302",
                                                                       "celulas_com_vagas_imediatas_diferentes")},
                     "quadro_antigo": rel(QUADRO_1903), "quadro_corrigido": rel(QUADRO_1302),
                     "datas": json.loads(A36_RESUMO.read_text(encoding="utf-8"))["ciclo2_versoes"]["datas"],
                     "formula": "tem_vaga_imediata = 1[vagas imediatas > 0]; log_vagas_imediatas_mais_1 = "
                                "log(vagas imediatas + 1) (script 12, conjunto_escolha)"},
        "escolhas_ciclo2": esc_c2,
        "desvios": DESVIOS,
        "entradas": entradas(dados),
        "integridade": ("nada simulado nem imputado; data/ só lido; IVS do a08 (o arquivo local de IVS da auditoria 16 "
                        "não é lido); só agregados em output/ (sem nome, CPF, CRM nem pseudônimo de candidato); saídas "
                        "E9_*, P1_* e P1h_* não regravadas"),
        "linguagem": ("escolha condicional a se candidatar, dentro das vagas abertas; a bolsa mede o pacote do corte e o "
                      "incentivo marginal; θ_UF é preferência revelada, não efeito causal; não é efeito da participação "
                      "no PMM-E"),
        "tempo_execucao_nao_registrado": "fora do resumo para que duas execuções deem o mesmo hash",
    }
    if port["status"] != "PASSOU":
        remover_saidas_calculadas()
        resumo["saidas"] = {}
        gravar_json(OUT_RESUMO, resumo)
        atualizar_doc()
        print(f"{port['status']}: nada corrigido (adendo 52c)", file=sys.stderr)
        return 3

    res_c = estimar_versao(dados, conj_e9_c, conj_p1_c, log)
    resumo["mesma_amostra"] = conferir_mesma_amostra(res_a, res_c)
    resumo["conferencia_distancia"] = res_a["_conf_dist"]
    est = montar(res_a, res_c)
    sem = est[est["estimativa"].isna() & (est["tipo_linha"] != "wald_igualdade_ciclos")]
    if len(sem):
        raise FalhaValidacao(f"{len(sem)} linhas sem estimativa")
    est.to_csv(OUT_CSV, index=False, float_format="%.10g")
    est = ler_est()
    resumo["leitura"] = leitura(est)
    resumo["covariancias"] = {ANTIGA: covariancias(res_a), CORRIGIDA: covariancias(res_c)}
    resumo["inferencia"] = {"principal": "sanduíche com cluster por conjunto de escolha (curso × ciclo), fator G/(G−1)",
                            "holm": {"P1a": "M1, bolsa_mil, bilateral, família de um teste",
                                     "P1h-1": "M1, D_UF, unilateral, família de um teste",
                                     "E9": "sem Holm (secundário e exploratório, protocolo 40 §12)"},
                            "z_bilateral_95": Z95, "z_unilateral_95": Z95_UNI}
    resumo["figura"] = figura(est, resumo["leitura"])
    resumo["como_ler"] = {FIG.name: COMO_LER}
    resumo["saidas"] = {rel(OUT_CSV): sha256(OUT_CSV), rel(FIG): resumo["figura"]["sha256"]}
    gravar_json(OUT_RESUMO, resumo)
    atualizar_doc()
    log(f"gravado: {rel(OUT_CSV)}, {rel(OUT_RESUMO)}, {rel(FIG)}, {rel(DOC)}")
    return 0


def ler_est() -> pd.DataFrame:
    return pd.read_csv(OUT_CSV, dtype={"ciclo": str})


def ler_resumo() -> dict:
    return json.loads(OUT_RESUMO.read_text(encoding="utf-8"))


def atualizar_doc() -> None:
    resumo = ler_resumo()
    est = ler_est() if resumo["portao"]["status"] == "PASSOU" else None
    DOC.write_text(gerar_doc(est, resumo), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
