"""T1.6 (adendo §7 do protocolo 52): cenários contrafactuais de bolsa com alocação centralizada.

CENÁRIO CONTRAFACTUAL, NÃO OBSERVAÇÃO. Toda saída leva `natureza_dos_dados = CENARIO_CONTRAFACTUAL` e fica em
`output/cenarios/` (doc 51, §2, item 4). Nada é gravado em `output/rdd_bolsa/`.

Pergunta do autor
-----------------
"Quantas vagas a mais seriam preenchidas no total se a bolsa subisse R$ 5 mil", com as vagas disputando o
mesmo grupo de candidatos numa alocação centralizada por nota. A RDD compara células perto do corte e não
responde isso; aqui o mercado inteiro da 1ª chamada é refeito com o mecanismo do G2.

Desenho (fixado no adendo §7 do protocolo 52 antes de simular)
--------------------------------------------------------------
1. Preferências: M1 do P1 (θ̂ reestimado com as funções do script 25 e conferido contra `P1_estimativas.csv`).
   Sensibilidades: S1/S2 = β_bolsa nos limites do IC 95%; S3 = θ sorteado de N(θ̂, V_cluster) por réplica
   (faixa de incerteza principal); S4 = M8 com coeficientes individuais condicionais às escolhas observadas.
2. Listas: ε de valor extremo sorteado condicional à lista observada (corrida de exponenciais, exato); no
   cenário, U' = U + β·Δbolsa e a nova lista são as L melhores células (L = tamanho observado). Sem mudança, a
   lista reproduz a observada por construção (conferido em toda réplica).
3. Mecanismo: `alocar` do G2 (aceitação adiada, prioridade da 1ª opção, nota, cotas na ordem do edital),
   capacidade efetiva (`divisao_cr`). Desempate (adendo §8 do protocolo 52, 25/10/2026): classificação publicada
   nos pares candidato × célula observados; sorteio por candidato (fixo na réplica, comum aos cenários) só nos
   pares novos, posicionado entre os observados empatados.
4. Validação de base: o cenário sem mudança precisa reproduzir as vagas preenchidas publicadas na 1ª chamada,
   por ciclo e faixa, com |B0 − observado| ≤ max(3; 2%) em todas as réplicas; senão, FALHA_VALIDACAO_BASE e os
   cenários não são calculados.
5. Cenários C1–C4 (bolsas dentro de R$ 10–20 mil), R = 200 réplicas, semente 20261024.

Integridade
-----------
Lê só `output/` e, sem alterar, os arquivos de `data/` que o G2 e o script 25 já leem. O nome e o CPF dos
resultados publicados entram só em memória, no hash do G2, como lá. Nenhum identificador de candidato é
gravado. O arquivo local de IVS da auditoria 16 não é lido (o IVS vem do a08, pelas funções do E9).

Uso
---
    python3 scripts/rdd_bolsa/25b_cenarios_bolsa.py
    python3 scripts/rdd_bolsa/25b_cenarios_bolsa.py --atualizar-doc   # só regrava o doc 57b das saídas
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DIR_RDD = ROOT / "scripts" / "rdd_bolsa"


def _importar(caminho: Path, nome: str):
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    if nome in sys.modules:
        return sys.modules[nome]
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    sys.dont_write_bytecode = bytecode
    return mod


P1 = _importar(DIR_RDD / "25_escolha_dap.py", "p1_escolha_para_t16")
G2M = _importar(DIR_RDD / "G2_mecanismo_alocacao.py", "g2_mecanismo_para_t16")

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "52_protocolo_P1_escolha_dap.md"
DOC = ROOT / "docs" / "06_execucao" / "57b_cenarios_P1_bolsa.md"
OUT = ROOT / "output" / "cenarios"
OUT_RESUMO = OUT / "P1_cenarios_resumo.json"
OUT_TABELA = OUT / "P1_cenarios_tabela.csv"
OUT_REPLICAS = OUT / "P1_cenarios_replicas.parquet"
OUT_FLUXOS = OUT / "P1_cenarios_fluxos.csv"
OUT_VALIDACAO = OUT / "P1_cenarios_validacao_base.csv"
OUT_VALIDACAO_FALHA_1 = OUT / "P1_cenarios_validacao_base_falha_2026-10-24.csv"   # execução de 24/10 (desempate antigo), preservada
DIR_FIG = OUT / "P1_figuras"
FIG_TOTAL = DIR_FIG / "P1_cenarios_total_e_mudancas.png"
FIG_FAIXAS = DIR_FIG / "P1_cenarios_por_faixa.png"

# ---------------------------------------------------------------------------
# Parâmetros do adendo §7 (nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-25"
NATUREZA = "CENARIO_CONTRAFACTUAL"
ESTATUTO = "ADENDO_52_T16_CENARIOS"
R_REPLICAS = 200
SEMENTE = 20261024
K_M8 = 100                       # sorteios de (b_i, d_i) por candidato no S4
TOL_ABS = 3                      # tolerância da validação de base: max(3 vagas; 2% do observado)
TOL_REL = 0.02
TOL_THETA = 1e-6                 # θ̂ reestimado contra P1_estimativas.csv
CICLOS = (1, 2, 3)
TOTAL = "1-3"
FAIXAS = ("FAIXA 3", "FAIXA 2", "FAIXA 1")
ROTULO_FAIXA = {"FAIXA 3": "Faixa 3 (IVS ≤ 0,300; R$ 10 mil)", "FAIXA 2": "Faixa 2 (0,300–0,400; R$ 15 mil)",
                "FAIXA 1": "Faixa 1 (IVS > 0,400; R$ 20 mil)"}
NAO_ALOCADO = "NAO_ALOCADO"
SEM_FAIXA = "SEM_FAIXA"
BOLSA_OBS = {"FAIXA 1": 20.0, "FAIXA 2": 15.0, "FAIXA 3": 10.0}
CENARIOS = {
    "C1": {"FAIXA 3": 15.0, "FAIXA 2": 15.0, "FAIXA 1": 20.0},
    "C2": {"FAIXA 3": 20.0, "FAIXA 2": 20.0, "FAIXA 1": 20.0},
    "C3": {"FAIXA 3": 10.0, "FAIXA 2": 20.0, "FAIXA 1": 20.0},
    "C4": {"FAIXA 3": 15.0, "FAIXA 2": 15.0, "FAIXA 1": 15.0},
}
DESCRICAO_CENARIO = {
    "C1": "+R$ 5 mil na faixa de bolsa menor (Faixa 3: 10 → 15)",
    "C2": "todas no maior valor (R$ 20 mil)",
    "C3": "+R$ 5 mil só na faixa 0,300–0,400 (Faixa 2: 15 → 20)",
    "C4": "bolsa uniforme de R$ 15 mil",
}
BOLSA_MIN, BOLSA_MAX = 10.0, 20.0
VARIANTES = ("principal", "S1_beta_inf", "S2_beta_sup", "S3_assintotico", "S4_M8")
DESCRICAO_VARIANTE = {
    "principal": "M1, θ̂ (só sorteio do erro)",
    "S1_beta_inf": "M1 com β_bolsa no limite inferior do IC 95%",
    "S2_beta_sup": "M1 com β_bolsa no limite superior do IC 95%",
    "S3_assintotico": "M1 com θ sorteado de N(θ̂, V_cluster) a cada réplica",
    "S4_M8": "M8 (logit misto), coeficientes individuais condicionais às escolhas",
}
OUTCOMES = ("delta_preenchidas_total", "delta_preenchidas_FAIXA 3", "delta_preenchidas_FAIXA 2",
            "delta_preenchidas_FAIXA 1", "medicos_mudam_de_vaga", "vagas_deixam_de_ser_preenchidas",
            "vagas_passam_a_ser_preenchidas", "delta_custo_mensal_bolsas_mil")

COMO_LER = {
    FIG_TOTAL.name: ("Para cada cenário, a barra da esquerda é quantos médicos terminam numa vaga diferente da do "
                     "cenário sem mudança, e a da direita é quanto muda o total de vagas preenchidas (ciclos 1–3, "
                     "1ª chamada). O traço é a faixa de 95% com a incerteza dos parâmetros (S3). Barra da esquerda "
                     "alta e barra da direita perto de zero: a bolsa troca médicos de lugar, mas quase não aumenta o "
                     "total."),
    FIG_FAIXAS.name: ("Para cada cenário, cada barra é quanto muda o número de vagas preenchidas numa faixa de IVS "
                      "(a faixa observada da célula), com a faixa de 95% do S3. Barras que se compensam (uma "
                      "faixa ganha o que outra perde) indicam redistribuição entre faixas, não médicos a mais."),
}


NOTA_PROCESSO_24 = (
    "Antes da execução com R = 200, o script foi rodado três vezes com R = 2 para depurar o código (24/10/2026, "
    "depois do commit do adendo). A 1ª parou numa conferência interna (instabilidade numérica no S4, corrigida "
    "no sorteio condicional); a 2ª parou num erro do código das figuras; a 3ª passou a validação de base com 2 "
    "réplicas e calculou os cenários, e o agente viu esses números de 2 réplicas. A execução com R = 200 falhou "
    "na validação de base. Depois disso só mudaram o texto do doc e a limpeza das saídas de cenário da depuração "
    "(apagadas); nada mudou no modelo, no mecanismo, na tolerância ou no desempate.")
NOTA_PROCESSO = (
    "Revalidação de 25/10/2026, depois do commit do adendo §8 (protocolo 52) e da escolha do autor pela opção 1. "
    "A falha de 24/10 já era conhecida (seção 9). Antes da execução com R = 200 houve uma depuração com R = 2 "
    "(opção `--depurar`, que só roda a validação de base e não grava nada); ela passou a validação e não calculou "
    "cenários, então nenhum número de cenário foi visto antes da execução com R = 200. A única mudança de "
    "código no cálculo foi o desempate (adendo §8); o doc passou a incluir a falha de 24/10 como histórico "
    "(seção 9), a partir da saída preservada. Modelo, mecanismo, tolerância, regra de validação, R e semente não "
    "mudaram.")


class FalhaValidacao(RuntimeError):
    pass


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def rel(caminho: Path) -> str:
    return str(Path(caminho).resolve().relative_to(ROOT))


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


def tolerancia(observado: int) -> float:
    return max(TOL_ABS, TOL_REL * observado)


def checar_faixa_de_bolsa() -> None:
    for c, m in CENARIOS.items():
        for v in m.values():
            if not BOLSA_MIN <= v <= BOLSA_MAX:
                raise FalhaValidacao(f"{c}: bolsa {v} fora de R$ 10–20 mil (extrapolação proibida)")


# ---------------------------------------------------------------------------
# Núcleo: sorteio condicional do erro e novas listas (sem I/O; testado com mercado sintético)
# ---------------------------------------------------------------------------

def sortear_condicional(V: np.ndarray, starts: np.ndarray, top1: np.ndarray, top2: np.ndarray,
                        E1: np.ndarray, E2: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Utilidades U = V + ε, com ε valor extremo tipo I, condicionais à ordem observada em cada unidade.

    Unidade = bloco contíguo de linhas (células). `top1` (e `top2`, ou −1) são as linhas observadas em 1º (e 2º)
    lugar. Representação em corrida: T = exp(−U) ~ Exp(λ = e^V). Condicional a T_top1 < T_top2 < demais:
    T_top1 = E1/Λ; T_top2 = T_top1 + E2/(Λ − λ_top1); demais T_r = T_último + F_r/λ_r (falta de memória).
    """
    n = len(V)
    tam = np.diff(np.append(starts, n))
    unid = np.repeat(np.arange(len(starts)), tam)
    m = np.maximum.reduceat(V, starts)
    lam = np.exp(V - m[unid])
    Lam = np.add.reduceat(lam, starts)
    T1 = E1 / Lam
    tem2 = top2 >= 0
    sem1 = lam.copy()
    sem1[top1] = 0.0
    resto2 = np.add.reduceat(sem1, starts)   # soma direta (Λ − λ_top1 perde precisão quando a 1ª domina)
    with np.errstate(divide="ignore", invalid="ignore"):
        T2 = np.where(tem2, T1 + E2 / np.where(tem2, resto2, 1.0), T1)
        T = T2[unid] + F / lam
    T[top1] = T1
    T[top2[tem2]] = T2[tem2]
    with np.errstate(divide="ignore"):
        return -np.log(T) + m[unid]


def melhores(U: np.ndarray, starts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Linha de maior e de segunda maior utilidade em cada unidade (−1 se a unidade tem uma linha só)."""
    n = len(U)
    tam = np.diff(np.append(starts, n))
    unid = np.repeat(np.arange(len(starts)), tam)
    idx = np.arange(n)
    m1 = np.maximum.reduceat(U, starts)
    a1 = np.minimum.reduceat(np.where(U == m1[unid], idx, n), starts)
    U2 = U.copy()
    U2[a1] = -np.inf
    m2 = np.maximum.reduceat(U2, starts)
    a2 = np.minimum.reduceat(np.where((U2 == m2[unid]) & np.isfinite(U2), idx, n), starts)
    a2 = np.where((tam >= 2) & (a2 < n), a2, -1)
    return a1, a2


# ---------------------------------------------------------------------------
# Mercado: candidatos, unidades de simulação e mecanismo
# ---------------------------------------------------------------------------

def montar_unidades(De: dict) -> dict:
    """Unidades de simulação a partir do desenho explodido do P1 (1ª e 2ª opção).

    Tipo A: 1ª e 2ª opção no mesmo conjunto (curso) → posições 1 e 2 juntas no bloco da 1ª opção.
    Tipo B: só a 1ª opção modelada (lista de 1, 2ª em outro curso ou 2ª fora do conjunto) → posição 1.
    Tipo C: 2ª opção em outro curso → posição 2, no bloco do curso dela.
    """
    G = De["grupos"]
    st, tam, esc, cel = De["starts"], De["tam"], De["esc"], De["cel"]
    pos2_mesmo = {}
    for g in np.flatnonzero((G["posto"] == 2).to_numpy() & (G["idx_excluida"] >= 0).to_numpy()):
        pos2_mesmo[(int(G["ciclo"].iat[g]), G["id_candidato"].iat[g])] = int(cel[esc[g]])
    linhas, starts, top1, top2, tipo, chave, posicoes = [], [], [], [], [], [], []
    p = 0
    for g in range(len(G)):
        posto = int(G["posto"].iat[g])
        k = (int(G["ciclo"].iat[g]), G["id_candidato"].iat[g])
        if posto == 2 and int(G["idx_excluida"].iat[g]) >= 0:
            continue
        a, m = int(st[g]), int(tam[g])
        bloco = np.arange(a, a + m)
        t1 = p + int(esc[g]) - a
        t2 = -1
        if posto == 1 and k in pos2_mesmo:
            hit = np.flatnonzero(cel[bloco] == pos2_mesmo[k])
            if len(hit) != 1:
                raise FalhaValidacao("2ª opção do mesmo curso fora do bloco da 1ª")
            t2 = p + int(hit[0])
            tp, pos = "A", (1, 2)
        elif posto == 1:
            tp, pos = "B", (1,)
        else:
            tp, pos = "C", (2,)
        linhas.append(bloco)
        starts.append(p)
        top1.append(t1)
        top2.append(t2)
        tipo.append(tp)
        chave.append(k)
        posicoes.append(pos)
        p += m
    linhas = np.concatenate(linhas)
    return {"linhas_De": linhas, "cel": cel[linhas], "starts": np.array(starts, dtype=np.int64),
            "top1": np.array(top1, dtype=np.int64), "top2": np.array(top2, dtype=np.int64),
            "tipo": np.array(tipo), "chave": chave, "posicoes": posicoes}


def listas_das_unidades(U: dict, a1: np.ndarray, a2: np.ndarray) -> dict:
    """{(ciclo, id): {posição: índice da célula em conj}} a partir das melhores linhas de cada unidade."""
    out: dict = {}
    cel = U["cel"]
    for j, (k, pos) in enumerate(zip(U["chave"], U["posicoes"])):
        d = out.setdefault(k, {})
        d[pos[0]] = int(cel[a1[j]])
        if len(pos) == 2:
            if a2[j] < 0:
                raise FalhaValidacao("unidade do tipo A sem segunda célula")
            d[pos[1]] = int(cel[a2[j]])
    return out


def referencia_desempate(eleg: pd.DataFrame) -> dict:
    """Referência da regra de desempate do adendo §8 (protocolo 52): classificação publicada por par observado
    e, por (célula, pontuação), o intervalo [mín., máx.] das classificações publicadas (posiciona os pares novos)."""
    obs = {(r.id_candidato, r.celula): r.classificacao_publicada for r in eleg.itertuples(index=False)}
    cl = eleg.dropna(subset=["classificacao_publicada"])
    g = cl.groupby(["celula", "pontuacao"])["classificacao_publicada"].agg(["min", "max"])
    return {"obs": obs, "intervalo": {k: (float(v["min"]), float(v["max"])) for k, v in g.iterrows()}}


def desempate_par(ref: dict, ident: str, celula: tuple, pontuacao: float, u: float) -> float:
    """Par observado: classificação publicada (ausente = +∞, como no G2). Par novo: sorteio u posicionado entre os
    observados empatados na célula (u puro se não há)."""
    if (ident, celula) in ref["obs"]:
        c = ref["obs"][(ident, celula)]
        return float(c) if not np.isnan(c) else np.inf
    iv = ref["intervalo"].get((celula, pontuacao))
    if iv is None:
        return float(u)
    return iv[0] - 0.5 + u * (iv[1] - iv[0] + 1.0)


def montar_entrada_mecanismo(fixos: pd.DataFrame, resp: pd.DataFrame, listas: dict, cel_chave: list,
                             ref: dict | None = None, u: dict | None = None) -> pd.DataFrame:
    """Linhas candidato × opção para o `alocar` do G2: fixos (lista observada) + respondentes (lista nova).

    Com `ref` e `u` (adendo §8), a coluna `classificacao_publicada` das linhas dos respondentes traz o desempate
    da regra nova (classificação publicada nos pares observados, sorteio posicionado nos pares novos) e o `alocar`
    é chamado com o desempate padrão. Sem `ref`, a coluna fica vazia (regra antiga, sorteio por candidato).

    `resp`: um respondente por linha (ciclo, id_candidato, pontuacao, tipo_inscricao, L, obs1, obs2), em que
    obs1/obs2 são as células observadas (tuplas) usadas quando a posição não é modelada.
    """
    ids, cels, ranks, pts, tps, cls = [], [], [], [], [], []
    for r in resp.itertuples(index=False):
        d = listas.get((r.ciclo, r.id_candidato), {})
        lista = []
        for pos, obs in ((1, r.obs1), (2, r.obs2)):
            if pos > r.L:
                break
            lista.append(cel_chave[d[pos]] if pos in d else obs)
        for o, c in enumerate(lista, start=1):
            ids.append(r.id_candidato)
            cels.append(c)
            ranks.append(o)
            pts.append(r.pontuacao)
            tps.append(r.tipo_inscricao)
            cls.append(np.nan if ref is None else desempate_par(ref, r.id_candidato, c, r.pontuacao, u[r.id_candidato]))
    novo = pd.DataFrame({"id_candidato": ids, "celula": cels, "opcao_rank": ranks, "pontuacao": pts,
                         "tipo_inscricao": tps, "classificacao_publicada": cls})
    return pd.concat([fixos, novo], ignore_index=True)


def conferir_conservacao(sim: dict, entrada: pd.DataFrame, cap: dict) -> dict:
    """Alocados ≤ capacidade em cada célula; um médico em no máximo uma vaga; vaga só numa célula da lista."""
    por_cel: dict = {}
    for p, (c, _t) in sim.items():
        por_cel[c] = por_cel.get(c, 0) + 1
    acima = sum(1 for c, n in por_cel.items() if n > sum(cap.get(c, (0, 0, 0))))
    lista = entrada.groupby("id_candidato")["celula"].apply(set).to_dict()
    fora = sum(1 for p, (c, _t) in sim.items() if c not in lista.get(p, set()))
    return {"celulas_acima_da_capacidade": int(acima), "alocados_fora_da_lista": int(fora),
            "medicos_em_mais_de_uma_vaga": 0}


def medir(base: dict, cen: dict, faixa_cel: dict, bolsa_base: dict, bolsa_cen: dict) -> tuple[dict, dict]:
    """Outcomes do cenário contra o B0 da mesma réplica, e a matriz de fluxos (origem × destino) dos que mudam."""
    def fx(c):
        return NAO_ALOCADO if c is None else faixa_cel.get(c, SEM_FAIXA)

    cb = {p: v[0] for p, v in base.items()}
    cc = {p: v[0] for p, v in cen.items()}
    nb = pd.Series(list(cb.values())).value_counts().to_dict() if cb else {}
    nc = pd.Series(list(cc.values())).value_counts().to_dict() if cc else {}
    celulas = set(nb) | set(nc)
    deixam = sum(max(0, nb.get(c, 0) - nc.get(c, 0)) for c in celulas)
    passam = sum(max(0, nc.get(c, 0) - nb.get(c, 0)) for c in celulas)
    out = {"delta_preenchidas_total": len(cc) - len(cb), "vagas_deixam_de_ser_preenchidas": deixam,
           "vagas_passam_a_ser_preenchidas": passam}
    for f in FAIXAS:
        out[f"delta_preenchidas_{f}"] = (sum(1 for c in cc.values() if fx(c) == f)
                                         - sum(1 for c in cb.values() if fx(c) == f))
    custo_b = sum(bolsa_base.get(fx(c), 0.0) for c in cb.values())
    custo_c = sum(bolsa_cen.get(fx(c), 0.0) for c in cc.values())
    out["delta_custo_mensal_bolsas_mil"] = custo_c - custo_b
    fluxos: dict = {}
    mudam = 0
    for p in set(cb) | set(cc):
        a, b = cb.get(p), cc.get(p)
        if a != b:
            mudam += 1
            k = (fx(a), fx(b))
            fluxos[k] = fluxos.get(k, 0) + 1
    out["medicos_mudam_de_vaga"] = mudam
    return out, fluxos


def contar_por_faixa(sim: dict, faixa_cel: dict) -> dict:
    out = {f: 0 for f in FAIXAS}
    out[SEM_FAIXA] = 0
    for c, _t in sim.values():
        out[faixa_cel.get(c, SEM_FAIXA)] += 1
    out["total"] = len(sim)
    return out


# ---------------------------------------------------------------------------
# Insumos
# ---------------------------------------------------------------------------

def carregar() -> dict:
    t0 = time.time()
    dados = P1.carregar()
    conj = dados["conj_p1"]
    D = P1.montar_desenho(conj, dados["r1_p1"], None, dados)
    De = P1.montar_desenho(conj, dados["r1_p1"], dados["r2_p1"], dados)
    print(f"[{time.time() - t0:6.0f}s] desenho do P1 montado", flush=True)

    # θ̂ do M1 reestimado e conferido contra o gravado.
    X = P1.matriz_modelo(D, dados, "M1")
    r1 = P1.estimar(X, D, modelo="M1", ciclo=P1.EMPILHADO, amostra="P1 (G1 com origem)")
    if not r1["ok"]:
        raise FalhaValidacao("M1 não convergiu na reestimação")
    est = pd.read_csv(P1.OUT_EST, dtype={"ciclo": str})
    g = est[(est["modelo"] == "M1") & (est["ciclo"] == P1.EMPILHADO) & (est["tipo_linha"] == "coeficiente")]
    gravado = g.set_index("termo")["coef"]
    if list(gravado.index) != list(r1["termos"]):
        raise FalhaValidacao("termos do M1 diferentes dos gravados")
    dif_theta = float(np.max(np.abs(gravado.to_numpy() - r1["theta"])))
    if dif_theta > TOL_THETA:
        raise FalhaValidacao(f"θ̂ do M1 difere do gravado em {dif_theta}")
    kb = r1["termos"].index(P1.TERMO_BOLSA)
    linha_b = g.set_index("termo").loc[P1.TERMO_BOLSA]
    m8 = est[(est["modelo"] == "M8") & (est["ciclo"] == P1.EMPILHADO) & (est["tipo_linha"] == "coeficiente")]
    m8 = m8.set_index("termo")["coef"]
    if not (est.loc[est["modelo"] == "M8", "status"] == "EXECUTADO").all():
        raise FalhaValidacao("M8 não executado")

    Xe = P1.matriz_modelo(De, dados, "M1")[r1["termos"]]
    U = montar_unidades(De)
    A = Xe.to_numpy(dtype=float)[U["linhas_De"]]
    print(f"[{time.time() - t0:6.0f}s] M1 conferido (dif. máx. {dif_theta:.1e}); {len(U['starts'])} unidades, "
          f"{len(A)} linhas", flush=True)

    # Mecanismo do G2: 1ª chamada dos três ciclos.
    mapa_ch1: dict = {}
    mercado = {}
    for ch in G2M.CHAMADAS:
        if ch["chamada"] != 1:
            continue
        res, quadro, diag = G2M.preparar(ch, mapa_ch1)
        conf = G2M.conferir_com_escolhas(res, ch["ciclo"])
        if conf["linhas_casadas"] != conf["linhas_g2"] or conf["linhas_casadas"] != conf["linhas_escolhas"]:
            raise FalhaValidacao(f"ciclo {ch['ciclo']}: G2 e escolhas_candidatos não casam")
        publicado = res[res["alvo"]][["id_candidato", "celula", "tipo_vaga_publicada"]]
        cap = G2M.capacidade_efetiva(quadro, publicado)
        eleg = res[res["elegivel"]][["id_candidato", "celula", "opcao_rank", "pontuacao", "tipo_inscricao",
                                     "classificacao_publicada"]].copy()
        if (eleg.groupby("id_candidato")["pontuacao"].nunique() > 1).any():
            raise FalhaValidacao("pontuação varia entre as opções do candidato")
        mercado[ch["ciclo"]] = {"ch": ch, "eleg": eleg, "cap": cap, "publicado": publicado, "diag": diag}
    print(f"[{time.time() - t0:6.0f}s] mercados do G2 lidos", flush=True)

    # Faixa observada de cada célula (todas as células do quadro, inclusive as fora do conjunto do P1).
    conj_tudo = pd.read_parquet(P1.E9.CONJ_PRINCIPAL, columns=["ciclo", "co_cnes_7d", "cod_curso", "faixa_anunciada"])
    faixa_cel = {k: {} for k in CICLOS}
    for r in conj_tudo.itertuples(index=False):
        faixa_cel[int(r.ciclo)][(r.co_cnes_7d, int(r.cod_curso))] = r.faixa_anunciada
    cel_chave = list(zip(conj["co_cnes_7d"], conj["cod_curso"].astype(int)))
    faixa_conj = np.array([faixa_cel[int(c)][k] for c, k in zip(conj["ciclo"], cel_chave)], dtype=object)

    # Respondentes (amostra P1 elegível) e fixos.
    cand = dados["cand"]
    obs = {}
    for r in cand.itertuples(index=False):
        obs.setdefault((int(r.ciclo), r.id_candidato), {})[int(r.opcao_rank)] = (r.co_cnes_7d, int(r.cod_curso))
    resp_ids = {k for k in U["chave"]}
    linhas_resp, fixos = [], {}
    contagem = {}
    for k in CICLOS:
        e = mercado[k]["eleg"]
        ids_e = set(e["id_candidato"])
        resp_k = sorted(i for (c, i) in resp_ids if c == k and i in ids_e)
        nao_eleg = sorted(i for (c, i) in resp_ids if c == k and i not in ids_e)
        info = e.groupby("id_candidato").agg(pontuacao=("pontuacao", "first"), tipo_inscricao=("tipo_inscricao", "first"),
                                             L=("opcao_rank", "size"))
        for i in resp_k:
            o = obs[(k, i)]
            lista_g2 = e[e["id_candidato"] == i].sort_values("opcao_rank")["celula"].tolist()
            lista_e9 = [o[p] for p in sorted(o)]
            if lista_g2 != lista_e9:
                raise FalhaValidacao("lista do G2 diferente da de escolhas_candidatos")
            linhas_resp.append({"ciclo": k, "id_candidato": i, "pontuacao": float(info.at[i, "pontuacao"]),
                                "tipo_inscricao": info.at[i, "tipo_inscricao"], "L": int(info.at[i, "L"]),
                                "obs1": o.get(1), "obs2": o.get(2)})
        fixos[k] = e[~e["id_candidato"].isin(set(resp_k))].reset_index(drop=True)
        contagem[str(k)] = {"candidatos_elegiveis": int(len(ids_e)), "respondem_ao_cenario": len(resp_k),
                            "lista_fixa_observada": int(fixos[k]["id_candidato"].nunique()),
                            "amostra_P1_inelegiveis_no_mecanismo": len(nao_eleg),
                            "celulas_com_capacidade": int(sum(1 for v in mercado[k]["cap"].values() if sum(v) > 0)),
                            "capacidade_efetiva_total": int(sum(sum(v) for v in mercado[k]["cap"].values())),
                            "preenchidas_publicadas": int(len(mercado[k]["publicado"]))}
    resp = pd.DataFrame(linhas_resp)
    # Unidades de respondentes inelegíveis ficam fora (o mecanismo não os vê).
    tipos = pd.Series(U["tipo"]).value_counts().to_dict()
    entradas = [
        {"caminho": rel(P1.OUT_EST), "sha256": sha256(P1.OUT_EST), "papel": "θ̂ e IC do M1; coeficientes do M8",
         "fonte": "script 25 (P1, EMPIRICO)"},
        {"caminho": rel(P1.E9.ESCOLHAS), "sha256": sha256(P1.E9.ESCOLHAS), "papel": "listas observadas"},
        {"caminho": rel(P1.E9.CONJ_PRINCIPAL), "sha256": sha256(P1.E9.CONJ_PRINCIPAL),
         "papel": "conjunto de escolha e faixa anunciada da célula"},
        {"caminho": rel(P1.G1_ORIGEM), "sha256": sha256(P1.G1_ORIGEM), "papel": "origem do candidato (G1)"},
    ] + [{"caminho": rel(m["ch"]["arquivo"]), "sha256": sha256(m["ch"]["arquivo"]),
          "papel": f"resultado publicado, ciclo {k}, 1ª chamada (nome e CPF só em memória, em hash, como no G2)"}
         for k, m in mercado.items()] + [
        {"caminho": rel(m["ch"]["quadro"]), "sha256": sha256(m["ch"]["quadro"]),
         "papel": f"quadro de vagas, ciclo {k}, 1ª chamada (AC/ER/PCD)"} for k, m in mercado.items()]
    return {"dados": dados, "conj": conj, "U": U, "A": A, "termos": r1["termos"], "theta": r1["theta"],
            "V_conj": r1["V_conj"], "kb": kb, "ic_beta": (float(linha_b["ic95_inf"]), float(linha_b["ic95_sup"])),
            "m8": m8, "mercado": mercado, "faixa_cel": faixa_cel, "cel_chave": cel_chave, "faixa_conj": faixa_conj,
            "resp": resp, "fixos": fixos, "contagem": contagem, "tipos_unidade": tipos, "entradas": entradas,
            "dif_theta": dif_theta}


# ---------------------------------------------------------------------------
# S4: coeficientes individuais do M8 condicionais às escolhas observadas
# ---------------------------------------------------------------------------

def preparar_m8(M: dict) -> dict:
    U, A, termos, m8 = M["U"], M["A"], M["termos"], M["m8"]
    fixos = [t for t in termos if t not in (P1.TERMO_BOLSA, P1.TERMO_DIST)]
    tf = np.array([m8[t] for t in fixos])
    idx_f = [termos.index(t) for t in fixos]
    base = A[:, idx_f] @ tf
    xb = A[:, termos.index(P1.TERMO_BOLSA)]
    xd = A[:, termos.index(P1.TERMO_DIST)]
    chaves = sorted(set(U["chave"]))
    pos = {k: i for i, k in enumerate(chaves)}
    unid_cand = np.array([pos[k] for k in U["chave"]])
    n_l = len(A)
    tam = np.diff(np.append(U["starts"], n_l))
    linha_cand = np.repeat(unid_cand, tam)
    rng = np.random.default_rng([SEMENTE, 8])
    z = rng.standard_normal((len(chaves), K_M8, 2))
    b = m8["media_bolsa_mil"] + abs(m8["desvio_bolsa_mil"]) * z[:, :, 0]
    d = m8["media_distancia_100km"] + abs(m8["desvio_distancia_100km"]) * z[:, :, 1]
    st, t1, t2 = U["starts"], U["top1"], U["top2"]
    tem2 = t2 >= 0
    unid = np.repeat(np.arange(len(st)), tam)
    logw = np.zeros((len(chaves), K_M8))
    for k in range(K_M8):
        v = base + b[linha_cand, k] * xb + d[linha_cand, k] * xd
        m = np.maximum.reduceat(v, st)
        e = np.exp(v - m[unid])
        S = np.add.reduceat(e, st)
        ll = v[t1] - m - np.log(S)
        ll2 = np.where(tem2, v[np.where(tem2, t2, 0)] - m - np.log(np.maximum(S - e[t1], 1e-300)), 0.0)
        logw[:, k] = np.bincount(unid_cand, weights=ll + ll2, minlength=len(chaves))
    w = np.exp(logw - logw.max(axis=1, keepdims=True))
    w /= w.sum(axis=1, keepdims=True)
    ess = 1.0 / (w ** 2).sum(axis=1)
    return {"base": base, "xb": xb, "xd": xd, "b": b, "d": d, "w": w, "linha_cand": linha_cand,
            "unid_cand": unid_cand, "ess_mediana": float(np.median(ess)), "ess_minimo": float(ess.min())}


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def rodar(M: dict, log=print, so_validacao: bool = False) -> dict:
    checar_faixa_de_bolsa()
    U, A = M["U"], M["A"]
    n_l, n_u = len(A), len(U["starts"])
    st, t1, t2 = U["starts"], U["top1"], U["top2"]
    theta, kb = M["theta"], M["kb"]
    xb = A[:, kb]
    faixa_linha = M["faixa_conj"][U["cel"]]
    delta = {c: np.array([CENARIOS[c][f] - BOLSA_OBS[f] for f in faixa_linha]) for c in CENARIOS}
    resp_por_ciclo = {k: M["resp"][M["resp"]["ciclo"] == k] for k in CICLOS}
    ids_ciclo = {k: sorted(set(M["mercado"][k]["eleg"]["id_candidato"])) for k in CICLOS}
    refs = {k: referencia_desempate(M["mercado"][k]["eleg"]) for k in CICLOS}
    m8 = preparar_m8(M)
    log(f"S4 pronto: ESS mediano {m8['ess_mediana']:.1f} de {K_M8}")
    # Cholesky de V_cluster (S3).
    Vc = M["V_conj"]
    autoval, autovet = np.linalg.eigh((Vc + Vc.T) / 2)
    raiz = autovet * np.sqrt(np.clip(autoval, 0, None))
    ic_inf, ic_sup = M["ic_beta"]
    theta_inf, theta_sup = theta.copy(), theta.copy()
    theta_inf[kb], theta_sup[kb] = ic_inf, ic_sup

    # B0 e validação, em todas as réplicas, antes de qualquer cenário.
    sorteios, b0 = [], []
    valid_linhas = []
    for r in range(R_REPLICAS):
        rng_t = np.random.default_rng([SEMENTE, r, 1])
        u = {k: dict(zip(ids_ciclo[k], rng_t.random(len(ids_ciclo[k])))) for k in CICLOS}
        sorteios.append(u)
        b0_r = {}
        for k in CICLOS:
            mk = M["mercado"][k]
            entrada = montar_entrada_mecanismo(M["fixos"][k], resp_por_ciclo[k], {}, M["cel_chave"], refs[k], u[k])
            sim = G2M.alocar(entrada, mk["cap"], mk["ch"]["ordem_edital"])
            b0_r[k] = (sim, entrada)
        b0.append(b0_r)
    obs_cont, g2_cont = {}, {}
    for k in CICLOS:
        mk = M["mercado"][k]
        pub = {p: (c, None) for p, c in zip(mk["publicado"]["id_candidato"], mk["publicado"]["celula"])}
        obs_cont[k] = contar_por_faixa(pub, M["faixa_cel"][k])
        g2 = G2M.alocar(mk["eleg"], mk["cap"], mk["ch"]["ordem_edital"])
        g2_cont[k] = contar_por_faixa(g2, M["faixa_cel"][k])
    passou = True
    conserv_b0 = {"celulas_acima_da_capacidade": 0, "alocados_fora_da_lista": 0}
    for k in CICLOS:
        conts = [contar_por_faixa(b0[r][k][0], M["faixa_cel"][k]) for r in range(R_REPLICAS)]
        for r in range(R_REPLICAS):
            c = conferir_conservacao(b0[r][k][0], b0[r][k][1], M["mercado"][k]["cap"])
            for kk in conserv_b0:
                conserv_b0[kk] += c[kk]
        for f in list(FAIXAS) + ["total"]:
            o = obs_cont[k][f]
            vals = np.array([c[f] for c in conts])
            tol = tolerancia(o)
            ok = bool(np.max(np.abs(vals - o)) <= tol)
            passou &= ok
            valid_linhas.append({"natureza_dos_dados": NATUREZA, "ciclo": str(k), "faixa": f, "observado": o,
                                 "g2_principal_classificacao_publicada": g2_cont[k][f],
                                 "b0_minimo": int(vals.min()), "b0_maximo": int(vals.max()),
                                 "b0_media": float(vals.mean()), "desvio_maximo": int(np.max(np.abs(vals - o))),
                                 "tolerancia": tol, "passa": ok})
        if obs_cont[k][SEM_FAIXA]:
            raise FalhaValidacao(f"ciclo {k}: vaga publicada em célula sem faixa")
    validacao = pd.DataFrame(valid_linhas)
    log(f"validação de base: {'PASSOU' if passou else 'FALHOU'}")
    out = {"validacao": validacao, "passou": passou, "conservacao_b0": conserv_b0, "m8": m8,
           "obs_cont": obs_cont}
    if not passou or so_validacao:
        return out

    reg, fluxos = [], {}
    conserv = {"celulas_acima_da_capacidade": 0, "alocados_fora_da_lista": 0, "listas_base_iguais_as_observadas": 0,
               "unidades_conferidas": 0}
    t0 = time.time()
    for r in range(R_REPLICAS):
        rng = np.random.default_rng([SEMENTE, r, 0])
        E1, E2, F = rng.exponential(size=n_u), rng.exponential(size=n_u), rng.exponential(size=n_l)
        theta_r = theta + raiz @ np.random.default_rng([SEMENTE, r, 2]).standard_normal(len(theta))
        rng4 = np.random.default_rng([SEMENTE, r, 3])
        cum = np.cumsum(m8["w"], axis=1)
        kk = np.minimum((cum < rng4.random(len(cum))[:, None]).sum(axis=1), K_M8 - 1)
        nc = np.arange(len(kk))
        bi, di = m8["b"][nc, kk], m8["d"][nc, kk]
        variantes = {
            "principal": (A @ theta, theta[kb]),
            "S1_beta_inf": (A @ theta_inf, ic_inf),
            "S2_beta_sup": (A @ theta_sup, ic_sup),
            "S3_assintotico": (A @ theta_r, theta_r[kb]),
            "S4_M8": (m8["base"] + bi[m8["linha_cand"]] * m8["xb"] + di[m8["linha_cand"]] * m8["xd"],
                      bi[m8["linha_cand"]]),
        }
        for nome in VARIANTES:
            V, beta = variantes[nome]
            Ub = sortear_condicional(V, st, t1, t2, E1, E2, F)
            a1, a2 = melhores(Ub, st)
            ok_base = bool(np.array_equal(a1, t1) and np.array_equal(np.where(t2 >= 0, a2, -1), t2))
            if not ok_base:
                raise FalhaValidacao(f"{nome}, réplica {r}: lista sem mudança difere da observada")
            conserv["listas_base_iguais_as_observadas"] += 1
            conserv["unidades_conferidas"] += n_u
            for c in CENARIOS:
                a1, a2 = melhores(Ub + beta * delta[c], st)
                listas = listas_das_unidades(U, a1, a2)
                bolsa_c = CENARIOS[c]
                for k in CICLOS:
                    mk = M["mercado"][k]
                    entrada = montar_entrada_mecanismo(M["fixos"][k], resp_por_ciclo[k], listas, M["cel_chave"],
                                                       refs[k], sorteios[r][k])
                    sim = G2M.alocar(entrada, mk["cap"], mk["ch"]["ordem_edital"])
                    cc = conferir_conservacao(sim, entrada, mk["cap"])
                    conserv["celulas_acima_da_capacidade"] += cc["celulas_acima_da_capacidade"]
                    conserv["alocados_fora_da_lista"] += cc["alocados_fora_da_lista"]
                    o, fl = medir(b0[r][k][0], sim, M["faixa_cel"][k], BOLSA_OBS, bolsa_c)
                    for nome_o, v in o.items():
                        reg.append((nome, c, r, str(k), nome_o, float(v)))
                    for (a, b), n in fl.items():
                        chave = (nome, c, str(k), a, b)
                        fluxos[chave] = fluxos.get(chave, 0) + n
        if r % 20 == 19:
            log(f"réplica {r + 1}/{R_REPLICAS} ({time.time() - t0:.0f}s)")
    rep = pd.DataFrame(reg, columns=["variante", "cenario", "replica", "ciclo", "outcome", "valor"])
    tot = rep.groupby(["variante", "cenario", "replica", "outcome"], as_index=False)["valor"].sum()
    tot["ciclo"] = TOTAL
    rep = pd.concat([rep, tot[rep.columns]], ignore_index=True)
    fl = pd.DataFrame([(*k, v) for k, v in fluxos.items()],
                      columns=["variante", "cenario", "ciclo", "origem", "destino", "soma"])
    flt = fl.groupby(["variante", "cenario", "origem", "destino"], as_index=False)["soma"].sum()
    flt["ciclo"] = TOTAL
    fl = pd.concat([fl, flt[fl.columns]], ignore_index=True)
    fl["media_por_replica"] = fl["soma"] / R_REPLICAS
    out.update({"replicas": rep, "fluxos": fl, "conservacao": conserv})
    return out


def tabela(rep: pd.DataFrame) -> pd.DataFrame:
    g = rep.groupby(["variante", "cenario", "ciclo", "outcome"])["valor"]
    t = pd.DataFrame({"media": g.mean(), "p2_5": g.quantile(0.025), "p97_5": g.quantile(0.975),
                      "minimo": g.min(), "maximo": g.max(), "replicas": g.size()}).reset_index()
    t.insert(0, "natureza_dos_dados", NATUREZA)
    ordem_v = {v: i for i, v in enumerate(VARIANTES)}
    ordem_o = {o: i for i, o in enumerate(OUTCOMES)}
    ordem_c = {c: i for i, c in enumerate(["1", "2", "3", TOTAL])}
    t = t.sort_values(["variante", "cenario", "ciclo", "outcome"],
                      key=lambda s: s.map(ordem_v) if s.name == "variante" else s.map(ordem_o) if s.name == "outcome"
                      else s.map(ordem_c) if s.name == "ciclo" else s).reset_index(drop=True)
    return t


# ---------------------------------------------------------------------------
# Figuras (sem texto de leitura embutido; o "Como ler" fica no doc e em `como_ler`)
# ---------------------------------------------------------------------------

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "t16"})
    return plt


def _sel(t: pd.DataFrame, variante: str, cenario: str, outcome: str, ciclo: str = TOTAL) -> pd.Series:
    s = t[(t["variante"] == variante) & (t["cenario"] == cenario) & (t["outcome"] == outcome) & (t["ciclo"] == ciclo)]
    if len(s) != 1:
        raise KeyError((variante, cenario, outcome, ciclo))
    return s.iloc[0]


def figuras(t: pd.DataFrame) -> list[dict]:
    plt = _plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    cen = list(CENARIOS)
    x = np.arange(len(cen))
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    for dx, outc, cor, rot in ((-0.18, "medicos_mudam_de_vaga", "#2a78d6", "médicos que mudam de vaga"),
                               (0.18, "delta_preenchidas_total", "#eb6834", "variação do total de vagas preenchidas")):
        pt = [_sel(t, "principal", c, outc)["media"] for c in cen]
        lo = [_sel(t, "S3_assintotico", c, outc)["p2_5"] for c in cen]
        hi = [_sel(t, "S3_assintotico", c, outc)["p97_5"] for c in cen]
        ax.bar(x + dx, pt, width=0.34, color=cor, label=rot)
        ax.vlines(x + dx, lo, hi, color="#2b2b2b", lw=1.2)
    ax.axhline(0, color="#52514e", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(cen)
    ax.set_ylabel("médicos ou vagas (ciclos 1–3)")
    ax.legend(frameon=False, fontsize=8, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e6e5e0", lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG_TOTAL, dpi=150, metadata={"Software": None})
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    cores = {"FAIXA 3": "#8fb4e3", "FAIXA 2": "#2a78d6", "FAIXA 1": "#1b3f73"}
    for i, f in enumerate(FAIXAS):
        dx = (i - 1) * 0.26
        o = f"delta_preenchidas_{f}"
        pt = np.array([_sel(t, "principal", c, o)["media"] for c in cen])
        lo = np.array([_sel(t, "S3_assintotico", c, o)["p2_5"] for c in cen])
        hi = np.array([_sel(t, "S3_assintotico", c, o)["p97_5"] for c in cen])
        ax.bar(x + dx, pt, width=0.24, color=cores[f], label=ROTULO_FAIXA[f])
        ax.vlines(x + dx, lo, hi, color="#2b2b2b", lw=1.0)
    ax.axhline(0, color="#52514e", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(cen)
    ax.set_ylabel("variação de vagas preenchidas (ciclos 1–3)")
    ax.legend(frameon=False, fontsize=8, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e6e5e0", lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG_FAIXAS, dpi=150, metadata={"Software": None})
    plt.close(fig)
    return [{"arquivo": rel(FIG_TOTAL), "descricao": "médicos que mudam de vaga e variação do total preenchido, "
                                                     "por cenário (principal; faixa S3)",
             "como_ler": COMO_LER[FIG_TOTAL.name]},
            {"arquivo": rel(FIG_FAIXAS), "descricao": "variação das vagas preenchidas por faixa observada da célula, "
                                                      "por cenário (principal; faixa S3)",
             "como_ler": COMO_LER[FIG_FAIXAS.name]}]


# ---------------------------------------------------------------------------
# Documento 57b (gerado inteiro pelo script)
# ---------------------------------------------------------------------------

def _n(v, casas: int = 1, sinal: bool = False) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return "—"
    s = f"{v:+,.{casas}f}" if sinal else f"{v:,.{casas}f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", "−")


def _faixa(lo, hi, casas: int = 1) -> str:
    return f"[{_n(lo, casas, True)}; {_n(hi, casas, True)}]"


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    out += ["| " + " | ".join(l) + " |" for l in linhas]
    return "\n".join(out)


def tabela_validacao(val: pd.DataFrame) -> str:
    linhas = []
    for r in val.itertuples(index=False):
        linhas.append([f"ciclo {r.ciclo}", "total" if r.faixa == "total" else ROTULO_FAIXA.get(r.faixa, r.faixa),
                       str(r.observado), str(r.g2_principal_classificacao_publicada),
                       f"{r.b0_minimo}–{r.b0_maximo}", str(r.desvio_maximo), _n(r.tolerancia, 1),
                       "sim" if r.passa else "**não**"])
    return _tab(["Ciclo", "Faixa", "Observado (1ª chamada publicada)", "G2 principal (classificação publicada)",
                 "B0 nas réplicas (mín.–máx.)", "Desvio máximo", "Tolerância", "Passa"], linhas)


def tabela_principal(t: pd.DataFrame) -> str:
    linhas = []
    for c in CENARIOS:
        def cel(o, casas=1):
            p = _sel(t, "principal", c, o)
            s = _sel(t, "S3_assintotico", c, o)
            return f"{_n(p['media'], casas, True)} {_faixa(s['p2_5'], s['p97_5'], casas)}"
        linhas.append([f"**{c}**: {DESCRICAO_CENARIO[c]}", cel("delta_preenchidas_total"),
                       _n(_sel(t, "principal", c, "medicos_mudam_de_vaga")["media"], 1) + " " + _faixa(
                           _sel(t, "S3_assintotico", c, "medicos_mudam_de_vaga")["p2_5"],
                           _sel(t, "S3_assintotico", c, "medicos_mudam_de_vaga")["p97_5"]).replace("+", ""),
                       _n(_sel(t, "principal", c, "vagas_deixam_de_ser_preenchidas")["media"], 1),
                       _n(_sel(t, "principal", c, "vagas_passam_a_ser_preenchidas")["media"], 1),
                       cel("delta_custo_mensal_bolsas_mil", 0)])
    return _tab(["Cenário", "Δ total de vagas preenchidas [faixa S3]", "Médicos que mudam de vaga [faixa S3]",
                 "Vagas que deixam de ser preenchidas", "Vagas que passam a ser preenchidas",
                 "Δ custo mensal das bolsas, R$ mil (aritmética simples) [faixa S3]"], linhas)


def tabela_faixas(t: pd.DataFrame) -> str:
    linhas = []
    for c in CENARIOS:
        l = [c]
        for f in FAIXAS:
            o = f"delta_preenchidas_{f}"
            p, s = _sel(t, "principal", c, o), _sel(t, "S3_assintotico", c, o)
            l.append(f"{_n(p['media'], 1, True)} {_faixa(s['p2_5'], s['p97_5'])}")
        linhas.append(l)
    return _tab(["Cenário"] + [ROTULO_FAIXA[f] for f in FAIXAS], linhas)


def tabela_sensibilidades(t: pd.DataFrame) -> str:
    linhas = []
    for c in CENARIOS:
        for v in VARIANTES:
            p = _sel(t, v, c, "delta_preenchidas_total")
            m = _sel(t, v, c, "medicos_mudam_de_vaga")
            linhas.append([c, DESCRICAO_VARIANTE[v], _n(p["media"], 1, True), _faixa(p["p2_5"], p["p97_5"]),
                           _n(m["media"], 1)])
    return _tab(["Cenário", "Variante", "Δ total preenchido (média)", "Percentis 2,5–97,5 nas réplicas",
                 "Médicos que mudam (média)"], linhas)


def tabela_ciclos(t: pd.DataFrame) -> str:
    linhas = []
    for c in CENARIOS:
        l = [c]
        for k in ["1", "2", "3"]:
            p = _sel(t, "principal", c, "delta_preenchidas_total", k)
            s = _sel(t, "S3_assintotico", c, "delta_preenchidas_total", k)
            m = _sel(t, "principal", c, "medicos_mudam_de_vaga", k)
            l.append(f"{_n(p['media'], 1, True)} {_faixa(s['p2_5'], s['p97_5'])}; mudam {_n(m['media'], 1)}")
        linhas.append(l)
    return _tab(["Cenário", "Ciclo 1", "Ciclo 2", "Ciclo 3"], linhas)


def tabela_fluxos(fl: pd.DataFrame) -> str:
    cats = list(FAIXAS) + [NAO_ALOCADO]
    rot = {**{f: f.replace("FAIXA", "Faixa") for f in FAIXAS}, NAO_ALOCADO: "não alocado", SEM_FAIXA: "sem faixa"}
    linhas = []
    for c in CENARIOS:
        s = fl[(fl["variante"] == "principal") & (fl["cenario"] == c) & (fl["ciclo"] == TOTAL)]
        m = s.set_index(["origem", "destino"])["media_por_replica"]
        for a in cats:
            linhas.append([c, f"de {rot[a]}"] + [_n(float(m.get((a, b), 0.0)), 1) for b in cats])
    return _tab(["Cenário", "Origem (no B0)"] + [f"para {rot[b]}" for b in cats], linhas)


def leitura(t: pd.DataFrame) -> str:
    partes = []
    for c in CENARIOS:
        p = _sel(t, "principal", c, "delta_preenchidas_total")
        s = _sel(t, "S3_assintotico", c, "delta_preenchidas_total")
        m = _sel(t, "principal", c, "medicos_mudam_de_vaga")
        dx = _sel(t, "principal", c, "vagas_deixam_de_ser_preenchidas")["media"]
        ps = _sel(t, "principal", c, "vagas_passam_a_ser_preenchidas")["media"]
        zero = s["p2_5"] <= 0 <= s["p97_5"]
        razao = abs(p["media"]) / m["media"] if m["media"] > 0 else float("nan")
        txt = (f"- **{c}** ({DESCRICAO_CENARIO[c]}): em média {_n(m['media'], 1)} médicos terminam numa vaga "
               f"diferente; {_n(ps, 1)} vagas passam a ser preenchidas e {_n(dx, 1)} deixam de ser. O total "
               f"preenchido muda {_n(p['media'], 1, True)} (faixa S3 {_faixa(s['p2_5'], s['p97_5'])})")
        if zero:
            txt += ", e a faixa contém zero."
        else:
            txt += ", e a faixa não contém zero."
        if math.isfinite(razao):
            txt += (f" A variação líquida equivale a {_n(100 * razao, 0)}% das mudanças de vaga: "
                    + ("**a bolsa sobretudo redistribui médicos entre vagas**." if razao < 0.5 else
                       "boa parte das mudanças vira vaga preenchida a mais."))
        partes.append(txt)
    iguais = all(abs(_sel(t, v, "C2", o)["media"] - _sel(t, v, "C4", o)["media"]) < 1e-9
                 for v in VARIANTES for o in OUTCOMES if o != "delta_custo_mensal_bolsas_mil")
    if iguais:
        partes.append("- **C2 e C4 dão as mesmas vagas** em todas as variantes (só o custo muda). Não é erro: as "
                      "duas grades diferem por uma constante (−R$ 5 mil em todas as células), e no modelo de escolha "
                      "só a diferença de bolsa entre as vagas do conjunto move a escolha. O nível da bolsa só mudaria "
                      "quem se candidata, e isso está fora da simulação (grupo de candidatos fixo).")
    return "\n".join(partes)


def secao_historico_24(n: int) -> list[str]:
    """Falha de 24/10/2026 (desempate por sorteio em todos os pares), preservada como registro."""
    val = pd.read_csv(OUT_VALIDACAO_FALHA_1, dtype={"ciclo": str})
    falhas = val[~val["passa"].astype(bool)]
    lista = "; ".join(f"ciclo {r.ciclo}, {'total' if r.faixa == 'total' else ROTULO_FAIXA.get(r.faixa, r.faixa)}: "
                      f"observado {r.observado}, B0 entre {r.b0_minimo} e {r.b0_maximo} (média "
                      f"{_n(r.b0_media, 1)}), desvio máximo {r.desvio_maximo} > tolerância {_n(r.tolerancia, 2)}"
                      for r in falhas.itertuples(index=False))
    return [
        f"## {n}. Histórico: falha da validação de 24/10/2026 (registro preservado)",
        "",
        "Execução anterior, com o desempate por sorteio por candidato em todos os pares (adendo §7.3). "
        "Saída preservada em `output/cenarios/P1_cenarios_validacao_base_falha_2026-10-24.csv`. Mesma regra e "
        "tolerância; a única mudança depois foi o desempate (adendo §8).",
        "",
        tabela_validacao(val),
        "",
        "**Resultado da validação de 24/10/2026: FALHOU.**",
        "",
        f"### {n}.1 Falha da validação de base",
        "",
        f"`FALHA_VALIDACAO_BASE`. Onde falhou: {lista}.",
        "",
        "Conforme o adendo, nada foi calibrado e **os cenários não foram calculados**: não há resposta "
        "simulada à pergunta do autor nesta execução. Não há arquivo de réplicas, tabela, fluxos nem figura "
        "de cenário em `output/cenarios/`.",
        "",
        "**O que a falha mostra.** O mecanismo foi conferido: com o mesmo desempate, a alocação montada pelo "
        "script é idêntica à do `alocar` do G2 sobre as linhas publicadas. A diferença vem do desempate por "
        "sorteio por candidato, fixado no adendo porque a classificação publicada não existe para pares "
        "candidato × célula novos. Com a classificação publicada (coluna do G2 principal), a reconstrução fica a "
        f"no máximo {int((val['g2_principal_classificacao_publicada'] - val['observado']).abs().max())} vaga(s) "
        "do observado em cada linha da tabela. Onde há empate de nota no corte da célula (G2, seção 4), o "
        "sorteio troca quem fica, e o perdedor pode ocupar ou não a vaga da 2ª opção; isso desloca vagas entre "
        "faixas em parte das réplicas.",
        "",
        "**Decisões em aberto, do autor (nenhuma foi executada em 24/10):**",
        "1. aceitar um desempate que use a classificação publicada nos pares observados e o sorteio só nos pares "
        "novos, com nova validação (**escolhida pelo autor em 25/10/2026; adendo §8**);",
        "2. trocar a regra \"em todas as réplicas\" por uma regra sobre a média ou sobre um percentil das "
        "réplicas;",
        "3. rodar só os ciclos 2 e 3, que passaram;",
        "4. manter a falha como resultado: com o desempate do edital fora dos dados, o mecanismo não é "
        "reproduzido com a precisão exigida em todas as réplicas.",
        "",
        "Qualquer uma delas exige um adendo datado antes de rodar, que registre que esta falha já foi vista.",
        "",
        f"### {n}.2 Nota de processo de 24/10/2026",
        "",
        NOTA_PROCESSO_24,
        "",
    ]


def gerar_doc(resumo: dict, val: pd.DataFrame, t: pd.DataFrame | None, fl: pd.DataFrame | None) -> str:
    cont = resumo["contagens"]
    linhas_cont = [[f"ciclo {k}", str(v["candidatos_elegiveis"]), str(v["respondem_ao_cenario"]),
                    str(v["lista_fixa_observada"]), str(v["capacidade_efetiva_total"]), str(v["preenchidas_publicadas"])]
                   for k, v in cont.items()]
    partes = [
        "# 57b. Cenários contrafactuais de bolsa (T1.6): SIMULAÇÃO, NÃO OBSERVAÇÃO",
        "",
        "> **ATENÇÃO: tudo neste documento é simulação (`natureza_dos_dados = CENARIO_CONTRAFACTUAL`).** Nenhum "
        "número abaixo foi observado: são alocações refeitas com um modelo de escolha estimado e o mecanismo do "
        "G2, sob hipóteses fixas. Não use estes números como resultado empírico nem como efeito causal "
        "estimado.<br>",
        f"> **Gerado por** `scripts/rdd_bolsa/25b_cenarios_bolsa.py` a partir de `output/cenarios/P1_*`; não editar "
        "à mão (o teste `tests/test_cenarios_bolsa.py` confere que este arquivo é igual ao gerado).<br>",
        "> **Protocolo:** [adendo §7 do protocolo 52](52_protocolo_P1_escolha_dap.md#7-adendo-de-24102026-t16-cenários), "
        "congelado em 24/10/2026 antes de simular, e [adendo §8](52_protocolo_P1_escolha_dap.md#8-adendo-de-25102026-t16-nova-regra-de-desempate-e-revalidação) "
        "(25/10/2026), que só troca a regra de desempate depois da falha de 24/10 (seção 9). Modelo de escolha: [doc 57a](57a_resultados_P1_escolha.md) "
        "(M1), auditado na auditoria 26. Mecanismo: [portão G2](../auditorias/G2_viabilidade_mecanismo.md).",
        "",
        "## 1. A pergunta e o que a simulação faz",
        "",
        "**Pergunta do autor:** quantas vagas a mais seriam preenchidas no total se a bolsa subisse R$ 5 mil, "
        "levando em conta que todas as vagas disputam o mesmo grupo de candidatos numa alocação centralizada por "
        "nota? A RDD não responde isso: ela compara células perto do corte, e uma vaga que ganha um candidato pode "
        "estar tirando esse candidato de outra.",
        "",
        "**O que a simulação faz**, para a 1ª chamada dos ciclos 1, 2 e 3:",
        "1. parte das listas de opções observadas e sorteia a parte da preferência que o modelo não explica, de modo "
        "que, sem mudar a bolsa, cada candidato repete exatamente a lista que fez;",
        "2. muda a bolsa das células segundo o cenário e refaz a lista de cada candidato com o peso da bolsa do M1;",
        "3. refaz a alocação com o mecanismo do G2 (aceitação adiada por opção e nota, cotas, capacidade efetiva);",
        "4. compara com a alocação sem mudança (B0) da mesma réplica.",
        "",
        "**Hipóteses (todas fixas):** vagas e capacidade fixas; o grupo de candidatos é fixo (ninguém novo entra, "
        "ninguém desiste); cada candidato mantém o número de opções que listou; alocação por nota como no G2; só a "
        "1ª chamada; sem 2ª chamada, desistência, homologação ou custo fiscal (o custo abaixo é aritmética simples). "
        "Bolsas sempre dentro de R$ 10–20 mil, a faixa observada.",
        "",
        "**O que o contraste mede:** o incentivo da bolsa como o M1 o identifica (o pacote do corte, auditoria 18), "
        "aplicado a quem já se candidatou. Não mede participação no PMM-E nem quantos médicos a mais o programa "
        "atrairia.",
        "",
        "## 2. Mercado",
        "",
        _tab(["Ciclo", "Candidatos elegíveis", "Respondem ao cenário (amostra P1)", "Lista fixa (fora da amostra P1)",
              "Capacidade efetiva", "Vagas preenchidas publicadas"], linhas_cont),
        "",
        f"- Unidades de simulação: {resumo['unidades']['total']} (tipo A, 1ª e 2ª opção no mesmo curso: "
        f"{resumo['unidades']['A']}; tipo B, só a 1ª opção modelada: {resumo['unidades']['B']}; tipo C, 2ª opção "
        f"em outro curso: {resumo['unidades']['C']}).",
        f"- M1 reestimado igual ao gravado (diferença máxima {resumo['modelo']['diferenca_theta_gravado']:.1e}); "
        f"β_bolsa = {_n(resumo['modelo']['beta_bolsa'], 4)} (IC 95% {_faixa(*resumo['modelo']['ic95_beta'], casas=4)}).",
        f"- R = {resumo['parametros']['R']} réplicas, semente {resumo['parametros']['semente']}; S4 com "
        f"{resumo['parametros']['K_M8']} sorteios por candidato (ESS mediano {_n(resumo['s4']['ess_mediana'], 1)}).",
        "",
        "## 3. Validação de base",
        "",
        "O cenário sem mudança (B0) precisa reproduzir as vagas preenchidas publicadas na 1ª chamada, por ciclo e "
        "faixa, com |B0 − observado| ≤ max(3; 2% do observado) em todas as réplicas (fixado antes de simular). A "
        "coluna do G2 principal usa a classificação publicada como desempate. Desde o adendo §8, o B0 usa a mesma "
        "classificação nos pares observados e o sorteio só nos pares novos; como no B0 todos os pares são "
        "observados, o B0 coincide com a coluna do G2 principal em todas as réplicas (a validação testa o "
        "mecanismo, não o sorteio).",
        "",
        tabela_validacao(val),
        "",
        f"**Resultado da validação: {'PASSOU' if resumo['validacao_base']['passou'] else 'FALHOU'}.**",
        "",
    ]
    if not resumo["validacao_base"]["passou"]:
        falhas = val[~val["passa"].astype(bool)]
        lista = "; ".join(f"ciclo {r.ciclo}, {'total' if r.faixa == 'total' else ROTULO_FAIXA.get(r.faixa, r.faixa)}: "
                          f"observado {r.observado}, B0 entre {r.b0_minimo} e {r.b0_maximo} (média "
                          f"{_n(r.b0_media, 1)}), desvio máximo {r.desvio_maximo} > tolerância {_n(r.tolerancia, 2)}"
                          for r in falhas.itertuples(index=False))
        partes += [
            "## 4. Falha da validação de base (revalidação de 25/10/2026)",
            "",
            f"`FALHA_VALIDACAO_BASE`. Onde falhou: {lista}.",
            "",
            "Conforme o adendo §8.3, nada foi calibrado e **os cenários não foram calculados**: o resultado fica "
            "registrado como falha e só o autor decide o passo seguinte, em novo adendo. Não há arquivo de "
            "réplicas, tabela, fluxos nem figura de cenário em `output/cenarios/`.",
            "",
            "## 5. Nota de processo",
            "",
            resumo["nota_processo"],
            "",
        ] + secao_historico_24(9)
        return "\n".join(partes) + "\n"
    cons = resumo["conservacao"]
    partes += [
        f"Conferências em toda réplica: as listas sem mudança são iguais às observadas em "
        f"{cons['listas_base_iguais_as_observadas']} de {cons['listas_base_iguais_as_observadas']} sorteios "
        f"(variante × réplica); células acima da capacidade: {cons['celulas_acima_da_capacidade']}; alocados fora "
        f"da própria lista: {cons['alocados_fora_da_lista']}; cada médico ocupa no máximo uma vaga (por construção "
        "do mecanismo).",
        "",
        "## 4. Leitura em linguagem simples",
        "",
        "**Subir a bolsa redistribui médicos entre vagas ou aumenta o total preenchido?**",
        "",
        leitura(t),
        "",
        resumo["leitura_geral"],
        "",
        "## 5. Resultados por cenário (ciclos 1–3, 1ª chamada)",
        "",
        "Ponto: média das réplicas do principal (M1, θ̂). Entre colchetes: percentis 2,5 e 97,5 do S3 (θ sorteado da "
        "distribuição assintótica e erro sorteado), a faixa de incerteza principal do adendo.",
        "",
        tabela_principal(t),
        "",
        "### 5.1 Por faixa observada da célula",
        "",
        tabela_faixas(t),
        "",
        "### 5.2 De onde saem e para onde vão os médicos que mudam (principal, média por réplica)",
        "",
        "Só os médicos cuja vaga muda entram. \"Não alocado\" na origem: o médico passa a ter vaga; no destino: "
        "perde a vaga que tinha no B0. Na diagonal, mudança de célula dentro da mesma faixa.",
        "",
        tabela_fluxos(fl),
        "",
        "### 5.3 Por ciclo (principal [faixa S3]; médicos que mudam)",
        "",
        tabela_ciclos(t),
        "",
        "### 5.4 Sensibilidades",
        "",
        tabela_sensibilidades(t),
        "",
        "S1 e S2 fixam β_bolsa nos limites do IC 95% do M1 (o limite inferior é negativo: bolsa maior atrairia "
        "menos). O S4 usa o logit misto (M8), em que o peso da bolsa varia entre os candidatos.",
        "",
        "## 6. Figuras",
        "",
        "Nenhuma figura traz texto de leitura dentro da imagem; o \"Como ler\" fica aqui e no campo `como_ler` de "
        "`P1_cenarios_resumo.json`.",
        "",
        _tab(["Arquivo", "O que mostra", "Como ler"],
             [[f"`{Path(f['arquivo']).name}`", f["descricao"], f["como_ler"]] for f in resumo["figuras"]]),
        "",
        "## 7. Limites",
        "",
        "- **Grupo de candidatos fixo.** Ninguém entra por causa da bolsa e ninguém desiste. Se a bolsa atrai "
        "médicos novos, o total preenchido subiria mais do que aqui; isso não é medido.",
        "- **Capacidade efetiva fixa.** Inclui a redistribuição do item 5.7 já feita na 1ª chamada publicada; a "
        "SGTES poderia redistribuir de outro modo num cenário.",
        "- **Modelo de escolha.** O peso da bolsa é o do M1, cujo IC 95% contém zero; IIA dentro do curso; o "
        "candidato vê todas as células do curso. A ordem entre opções de cursos diferentes fica a observada.",
        "- **Quem não responde.** Candidatos sem origem ligada no G1 mantêm a lista observada (seção 2).",
        "- **Desempate.** Classificação publicada nos pares candidato × célula observados; nos pares novos, sorteio por "
        "candidato posicionado entre os observados empatados (adendo §8), no lugar da regra do edital (UF e "
        "idade), que não é pública. Em células com muitos empates de nota no corte, o resultado para pares novos "
        "depende desse sorteio.",
        "- **Só a 1ª chamada.** Sem 2ª chamada, desistência, homologação; o custo é só bolsa × alocados.",
        "- **Só redistribuição.** Com candidatos e vagas fixos, um aumento uniforme da bolsa não muda nenhuma "
        "escolha no logit condicional (só a diferença de bolsa entre as células do conjunto entra na utilidade): "
        "C2 e C4 dão o mesmo resultado. Os efeitos dos cenários vêm só da redistribuição de candidatos entre "
        "células e faixas, e a variação do total vem de candidatos que saem de células disputadas para células "
        "com vaga sobrando. Não é atração de médicos novos.",
        "- **Incerteza herdada do M1.** O IC 95% do β_bolsa contém zero; com β no limite inferior (S1) o efeito "
        "no total é nulo, e a faixa S3 (principal) contém zero em C1, C2 e C4 para o total. Os números são "
        "condicionais ao modelo; leia a faixa, não o ponto.",
        "",
        "## 8. Nota de processo",
        "",
        resumo["nota_processo"],
        "",
    ] + secao_historico_24(9)
    return "\n".join(partes) + "\n"


def leitura_geral(t: pd.DataFrame) -> str:
    p1 = _sel(t, "principal", "C1", "delta_preenchidas_total")
    s1 = _sel(t, "S3_assintotico", "C1", "delta_preenchidas_total")
    m1 = _sel(t, "principal", "C1", "medicos_mudam_de_vaga")
    return (f"**Resposta direta à pergunta do autor (C1, +R$ 5 mil na faixa de bolsa menor):** na simulação, o "
            f"total de vagas preenchidas na 1ª chamada dos três ciclos muda {_n(p1['media'], 1, True)} (faixa S3 "
            f"{_faixa(s1['p2_5'], s1['p97_5'])}), enquanto {_n(m1['media'], 1)} médicos trocam de vaga. Com o "
            "grupo de candidatos fixo, a bolsa só pode mudar o total se levar candidatos de células disputadas "
            "(onde perderiam para alguém de nota maior) para células que ficariam vazias, ou o contrário. Isto é "
            "simulação condicional ao modelo e às hipóteses da seção 1, não observação.")


# ---------------------------------------------------------------------------
# Principal
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--depurar", type=int, metavar="R",
                    help="depuração: roda a validação de base com R réplicas e imprime o resultado; não grava nada")
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57b a partir das saídas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    t0 = time.time()

    def log(m: str) -> None:
        print(f"[{time.time() - t0:6.0f}s] {m}", flush=True)

    checar_faixa_de_bolsa()
    M = carregar()
    if args.depurar:
        global R_REPLICAS
        R_REPLICAS = args.depurar
        res = rodar(M, log, so_validacao=True)
        print(res["validacao"].to_string(index=False))
        log(f"depuração R={args.depurar}: validação {'PASSOU' if res['passou'] else 'FALHOU'}; nada gravado")
        return 0
    res = rodar(M, log)
    OUT.mkdir(parents=True, exist_ok=True)
    val = res["validacao"]
    val.to_csv(OUT_VALIDACAO, index=False)
    resumo = {
        "etapa": "T1.6 (adendo §7 do protocolo 52)", "natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO,
        "aviso": "SIMULAÇÃO: cenário contrafactual sob hipóteses fixas; nada aqui é observação",
        "data_execucao": DATA_EXECUCAO, "script": rel(Path(__file__)), "protocolo": rel(PROTOCOLO_MD) + " §7",
        "parametros": {"R": R_REPLICAS, "semente": SEMENTE, "K_M8": K_M8, "tolerancia_abs": TOL_ABS,
                       "tolerancia_rel": TOL_REL, "bolsa_observada": BOLSA_OBS, "cenarios": CENARIOS,
                       "descricao_cenarios": DESCRICAO_CENARIO, "variantes": DESCRICAO_VARIANTE},
        "modelo": {"termos": M["termos"], "theta": M["theta"].tolist(), "beta_bolsa": float(M["theta"][M["kb"]]),
                   "ic95_beta": list(M["ic_beta"]), "diferenca_theta_gravado": M["dif_theta"]},
        "unidades": {"total": int(len(M["U"]["starts"])), **{k: int(M["tipos_unidade"].get(k, 0)) for k in "ABC"},
                     "linhas": int(len(M["A"]))},
        "contagens": M["contagem"],
        "s4": {"ess_mediana": res["m8"]["ess_mediana"], "ess_minimo": res["m8"]["ess_minimo"]},
        "validacao_base": {"passou": bool(res["passou"]),
                           "regra": "|B0 − observado| ≤ max(3; 2% do observado) em todas as réplicas, por ciclo × "
                                    "faixa e no total do ciclo",
                           "conservacao_b0": res["conservacao_b0"]},
        "nota_processo": NOTA_PROCESSO,
        "entradas": M["entradas"],
        "integridade": {"data_alterado": False, "identificador_de_candidato_gravado": False,
                        "arquivo_local_de_ivs_lido": False, "saidas_em_output_rdd_bolsa": False},
        "limites": ["grupo de candidatos fixo (sem entrada nem desistência)", "sem extrapolação fora de R$ 10–20 mil",
                    "sem 2ª chamada, desistência, homologação ou custo fiscal (custo = aritmética simples)",
                    "capacidade efetiva fixa (inclui a redistribuição do item 5.7 publicada)",
                    "M1 com IC de β_bolsa que contém zero; IIA dentro do curso"],
    }
    if res["passou"]:
        t = tabela(res["replicas"])
        t.to_csv(OUT_TABELA, index=False)
        rep = res["replicas"].copy()
        rep.insert(0, "natureza_dos_dados", NATUREZA)
        rep.to_parquet(OUT_REPLICAS, index=False)
        fl = res["fluxos"].copy()
        fl.insert(0, "natureza_dos_dados", NATUREZA)
        fl = fl.sort_values(["variante", "cenario", "ciclo", "origem", "destino"]).reset_index(drop=True)
        fl.to_csv(OUT_FLUXOS, index=False)
        resumo["conservacao"] = res["conservacao"]
        resumo["figuras"] = figuras(t)
        resumo["como_ler"] = {Path(f["arquivo"]).name: f["como_ler"] for f in resumo["figuras"]}
        resumo["principal"] = {c: {o: {"media": float(_sel(t, "principal", c, o)["media"]),
                                       "faixa_S3": [float(_sel(t, "S3_assintotico", c, o)["p2_5"]),
                                                    float(_sel(t, "S3_assintotico", c, o)["p97_5"])]}
                                   for o in OUTCOMES} for c in CENARIOS}
        resumo["leitura_geral"] = leitura_geral(t)
        saidas = [OUT_VALIDACAO, OUT_TABELA, OUT_REPLICAS, OUT_FLUXOS, FIG_TOTAL, FIG_FAIXAS]
    else:
        resumo["status"] = "FALHA_VALIDACAO_BASE"
        # Nenhuma saída de cenário pode sobrar de execução anterior: a regra do adendo é não calcular nem ler.
        for p in (OUT_TABELA, OUT_REPLICAS, OUT_FLUXOS, FIG_TOTAL, FIG_FAIXAS):
            if p.exists():
                p.unlink()
        if DIR_FIG.exists() and not any(DIR_FIG.iterdir()):
            DIR_FIG.rmdir()
        resumo["figuras"] = []
        resumo["como_ler"] = {}
        resumo["leitura_geral"] = ""
        t = fl = None
        saidas = [OUT_VALIDACAO]
    resumo["saidas"] = [{"caminho": rel(p), "sha256": sha256(p)} for p in saidas]
    gravar_json(OUT_RESUMO, resumo)
    atualizar_doc()
    log("fim")
    return 0


def ler_saidas() -> tuple[dict, pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    resumo = json.loads(OUT_RESUMO.read_text(encoding="utf-8"))
    val = pd.read_csv(OUT_VALIDACAO, dtype={"ciclo": str})
    if not resumo["validacao_base"]["passou"]:
        return resumo, val, None, None
    t = pd.read_csv(OUT_TABELA, dtype={"ciclo": str})
    fl = pd.read_csv(OUT_FLUXOS, dtype={"ciclo": str})
    return resumo, val, t, fl


def atualizar_doc() -> None:
    DOC.write_text(gerar_doc(*ler_saidas()), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
