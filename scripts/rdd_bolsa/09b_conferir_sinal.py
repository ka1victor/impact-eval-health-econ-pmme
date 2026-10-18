"""Confere o sinal do salto da RDD da bolsa (E3): bolsa maior menos bolsa menor.

Pergunta do autor (18/10/2026): no corte 0,300, a media bruta do preenchimento
na janela e maior acima do corte do que abaixo, mas o salto do E3 e negativo.
O E3 esta mesmo estimando o efeito de passar da bolsa MENOR para a MAIOR?

O script nao estima nada novo para a analise. Refaz, por outro caminho, as
contas do E3 e grava o que conferiu em `output/rdd_bolsa/E3_conferencia_sinal.json`.
O relatorio (`09_gerar_relatorio_pdf.py`) le esse JSON.

Conferencias
------------
C1 Regra e lado, sem outcome. No quadro de vagas, todo municipio com IVS 2010
   oficial s > c oferece a faixa de bolsa maior e todo municipio com s <= c a
   menor, na populacao inteira e na janela principal. Os valores por faixa sao
   os do edital (clausula 11.1.4, transcrita em `a01b_reconstrucao_regra_faixa.json`).
   A populacao e a faixa da matriz conferem com a leitura dos quadros brutos
   (xlsx) feita pelas funcoes do proprio E3.
C2 Convencao no codigo do E3: localiza em `07_estimar_E3_rdd_completa.py` as
   linhas que definem T = 1[s > c] e tau = coeficiente de T (registro para
   conferencia manual; o teste e funcional, em C3).
C3 Reestimacao independente: duas regressoes lineares ponderadas, uma de cada
   lado do corte, por formula fechada (sem a matriz do E3), com o mesmo kernel
   triangular e a mesma janela. Salto = intercepto do lado da bolsa maior menos
   intercepto do lado da bolsa menor. Tem de igualar o tau do E3 em todas as
   especificacoes de `E3_estimativas.csv`.
C4 Tratamento lido do quadro: no modelo empilhado, trocar T por
   (bolsa anunciada no quadro - bolsa do lado menor) / R$ 5 mil da o mesmo
   coeficiente. O salto e, portanto, "por +R$ 5 mil", com o sinal da bolsa maior.
C5 Erro-padrao HC1 recalculado (lstsq + sanduiche explicito) igual ao do E3.
C6 Medias brutas x salto: decomposicao exata, lado a lado,
   dif. de medias brutas = salto + inclinacao + residuo, em que
   inclinacao = b_maior * xbar_maior - b_menor * xbar_menor (x = s - c, medias
   simples do lado) e residuo = media simples dos residuos da reta ponderada
   de cada lado (maior - menor). Mostra por que o salto pode ter sinal oposto
   ao da diferenca de medias brutas.

Nenhuma escolha de amostra, janela ou estimador e refeita: tudo segue o E3.
Os outcomes sao lidos como no relatorio (`09_*`): fracao preenchida de
`E4_proporcao_municipio.csv` (reconstrucao independente dos brutos) e D_k da
relacao nominal com o leitor do E3 (so `co_ibge` e `ciclo`).

Entradas: lista ENTRADAS (SHA-256 gravado no JSON).
Saida: output/rdd_bolsa/E3_conferencia_sinal.json
"""

from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "output" / "rdd_bolsa"

MATRIZ = OUT_DIR / "matriz_municipio_escore_administrativo.csv"
IVS_OFICIAL = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
ESCORE = OUT_DIR / "escore_completo_ivs2010_oficial.csv"
E3_EST = OUT_DIR / "E3_estimativas.csv"
E3_STATUS = OUT_DIR / "E3_status.json"
E4_PROP = OUT_DIR / "E4_proporcao_municipio.csv"
A01B = OUT_DIR / "a01b_reconstrucao_regra_faixa.json"
ATIVOS_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
E3_SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "07_estimar_E3_rdd_completa.py"
SAIDA = OUT_DIR / "E3_conferencia_sinal.json"

ENTRADAS = [MATRIZ, IVS_OFICIAL, ESCORE, E3_EST, E3_STATUS, E4_PROP, A01B, ATIVOS_ZIP, E3_SCRIPT]

# Mesma definicao de populacao do relatorio e do 04b (conferida contra os quadros brutos em C1).
QUADROS_POP = {"P1": ["c1_ch1"], "P2": ["c2_ch1", "c2_ch2"]}
OUTCOME_D = "D_k_especialista_ativo_do_ciclo"
OUTCOME_FRAC = "fracao_celulas_ch1_com_confirmacao_ou_homologacao"
Z_975 = 1.959963984540054
# Tolerancias: a fracao preenchida de E4_proporcao_municipio.csv tem 10 casas decimais, e o E3 a calcula
# do funil com precisao total; as diferencas de arredondamento ficam abaixo de 1e-10 por municipio.
TOL_TAU = 1e-9  # |tau independente - tau do E3|
TOL_EP = 1e-9  # idem para o EP (relativa ao EP quando ele passa de 1)
TOL_MEDIA = 1e-9

# Trechos do codigo do E3 que fixam a convencao (C2). Conferencia manual; o teste e funcional (C3).
TRECHOS_E3 = {
    "tratamento": r"t\s*=\s*\(x_mil\[usa\]\s*>\s*0\)",
    "desenho": r"X\s*=\s*np\.column_stack\(\[np\.ones_like\(xs\),\s*xs,\s*t,\s*t\s*\*\s*xs\]\)",
    "salto": r"tau\s*=\s*float\(beta\[2\]\)",
    "x_centrado": r"x_mil\s*=\s*s\s*-\s*corte_mil",
}


# ---------------------------------------------------------------------------
# Utilitarios
# ---------------------------------------------------------------------------


def rel(p: Path) -> str:
    try:
        return Path(p).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def importar_e3():
    spec = importlib.util.spec_from_file_location("e3_rdd_completa", E3_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    antes = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


def p_normal(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0)) if math.isfinite(z) else float("nan")


def limpo(v):
    """Valor serializavel em JSON (numpy -> python; NaN -> None)."""
    if isinstance(v, dict):
        return {str(k): limpo(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [limpo(x) for x in v]
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return None if not math.isfinite(float(v)) else float(v)
    return v


def num(x: float, nd: int) -> str:
    """Numero com virgula decimal (texto do JSON em portugues)."""
    s = f"{x:,.{nd}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return "−" + s[1:] if s.startswith("-") else s


def pct(x: float) -> str:
    return num(100 * x, 1) + "%"


def pp(x: float) -> str:
    s = num(100 * x, 1)
    return s if s.startswith("−") else "+" + s


def mil(v: float) -> str:
    return f"R$ {int(round(v / 1000))} mil" if v % 1000 == 0 else f"R$ {num(v, 0)}"


# ---------------------------------------------------------------------------
# Estimador independente (formula fechada por lado; empilhado por lstsq)
# ---------------------------------------------------------------------------


def reta_ponderada(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> tuple[float, float]:
    """MQP de y em (1, x) por formula fechada: devolve (intercepto em x = 0, inclinacao)."""
    sw = w.sum()
    xb = (w * x).sum() / sw
    yb = (w * y).sum() / sw
    b = (w * (x - xb) * (y - yb)).sum() / (w * (x - xb) ** 2).sum()
    return float(yb - b * xb), float(b)


def amostra_janela(s_mil: np.ndarray, y: np.ndarray, corte_mil: int, h_mil: int):
    """Mesma amostra efetiva do E3: |s - c| < h (em c + h o peso triangular e zero) e y finito."""
    x_mil = s_mil - corte_mil
    usa = (np.abs(x_mil) < h_mil) & np.isfinite(y)
    w = 1.0 - np.abs(x_mil) / h_mil
    return usa, x_mil, w


def estimar_independente(s_mil, y, bolsa, corte_mil: int, h_mil: int, passo_brl: float) -> dict:
    """Salto por duas retas separadas e pelo modelo empilhado com a bolsa do quadro."""
    s_mil = np.asarray(s_mil, dtype=int)
    y = np.asarray(y, dtype=float)
    bolsa = np.asarray(bolsa, dtype=float)
    usa, x_mil, w = amostra_janela(s_mil, y, corte_mil, h_mil)
    menor = usa & (x_mil <= 0)
    maior = usa & (x_mil > 0)
    x = x_mil / 1000.0
    a0, b0 = reta_ponderada(x[menor], y[menor], w[menor])
    a1, b1 = reta_ponderada(x[maior], y[maior], w[maior])
    tau = a1 - a0

    # Modelo empilhado com o tratamento lido do quadro: D = (bolsa - bolsa do lado menor) / passo.
    bolsa_menor = float(np.min(bolsa[usa]))
    d = (bolsa[usa] - bolsa_menor) / passo_brl
    xs, ys, ws = x[usa], y[usa], w[usa]
    X = np.column_stack([np.ones_like(xs), xs, d, d * xs])
    raiz = np.sqrt(ws)
    beta = np.linalg.lstsq(X * raiz[:, None], ys * raiz, rcond=None)[0]
    e = ys - X @ beta
    n, k = X.shape
    pao = np.linalg.inv((X * ws[:, None]).T @ X)
    meio = np.einsum("i,ij,ik->jk", (ws * e) ** 2, X, X)
    V = pao @ meio @ pao * (n / (n - k))
    ep = float(math.sqrt(max(V[2, 2], 0.0)))

    # Medias e decomposicao exata da diferenca de medias brutas.
    def lado(sel, a, b):
        res = y[sel] - (a + b * x[sel])
        return {
            "n": int(sel.sum()),
            "media_bruta": float(y[sel].mean()),
            "media_ponderada_kernel": float(np.average(y[sel], weights=w[sel])),
            "x_medio": float(x[sel].mean()),
            "ivs_medio": float((s_mil[sel].mean()) / 1000.0),
            "residuo_medio": float(res.mean()),
            "valor_da_reta_no_corte": float(a),
            "inclinacao_por_0_010_de_ivs": float(b * 0.010),
        }

    L0, L1 = lado(menor, a0, b0), lado(maior, a1, b1)
    dif_bruta = L1["media_bruta"] - L0["media_bruta"]
    inclinacao = b1 * L1["x_medio"] - b0 * L0["x_medio"]
    residuo = L1["residuo_medio"] - L0["residuo_medio"]
    return {
        "tau_duas_retas": float(tau),
        "tau_bolsa_do_quadro": float(beta[2]),
        "ep_hc1": ep,
        "ic95_inf": float(beta[2] - Z_975 * ep),
        "ic95_sup": float(beta[2] + Z_975 * ep),
        "p_valor": p_normal(float(beta[2]) / ep) if ep > 0 else float("nan"),
        "bolsa_lado_menor": sorted(set(bolsa[menor].tolist())),
        "bolsa_lado_maior": sorted(set(bolsa[maior].tolist())),
        "lado_bolsa_menor": L0,
        "lado_bolsa_maior": L1,
        "diferenca_medias_brutas": float(dif_bruta),
        "decomposicao": {
            "salto": float(tau),
            "inclinacao_dentro_da_janela": float(inclinacao),
            "residuo": float(residuo),
            "soma": float(tau + inclinacao + residuo),
        },
    }


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------


def valores_do_edital(a01b: dict) -> dict[str, float]:
    txt = (((a01b.get("regra_do_edital") or {}).get("clausulas_transcritas") or {}).get("11.1.4") or "")
    achados = re.findall(r"Faixa\s+(\d)\s*,\s*R\$\s*([\d.]+)", txt)
    return {f"FAIXA {f}": float(v.replace(".", "")) for f, v in achados}


def carregar_base(e3) -> dict:
    st = json.loads(E3_STATUS.read_text(encoding="utf-8"))
    if st.get("status") != "CONCLUIDO":
        raise SystemExit(f"E3 nao concluido ({st.get('status')}): nada a conferir.")
    if (st.get("escore") or {}).get("sha256") != sha256(ESCORE):
        raise SystemExit("O escore gravado no E3_status nao e o arquivo atual do escore completo.")
    cortes_mil = [int(round(float(c) * 1000)) for c in st["cortes"]]
    h_principal_mil = int(round(float(st["janelas"]["principal"]) * 1000))

    mat = pd.read_csv(MATRIZ, dtype={"co_ibge": str})
    of = pd.read_csv(IVS_OFICIAL, dtype={"co_ibge": str})[["co_ibge", "ivs"]]
    esc = pd.read_csv(ESCORE, dtype={"co_ibge": str})[["co_ibge", "ivs_admin"]]
    j = of.merge(esc, on="co_ibge", how="outer")
    escore_e_ivs_oficial = bool(len(j) == len(of) and np.array_equal(
        np.rint(j["ivs"].to_numpy(float) * 1000), np.rint(j["ivs_admin"].to_numpy(float) * 1000)))

    pops = {}
    for nome, quadros in QUADROS_POP.items():
        g = mat[mat["quadro"].isin(quadros)][["co_ibge", "faixa_anunciada", "valor_anunciado_brl"]].drop_duplicates()
        if g["co_ibge"].duplicated().any():
            raise SystemExit(f"{nome}: municipio com mais de uma faixa na matriz")
        g = g.merge(of, on="co_ibge", how="left")
        if g["ivs"].isna().any():
            raise SystemExit(f"{nome}: municipio sem IVS oficial")
        g["s_mil"] = np.rint(g["ivs"].to_numpy(float) * 1000).astype(int)
        pops[nome] = g.sort_values("co_ibge").reset_index(drop=True)

    # A populacao e a faixa da matriz conferem com a leitura dos quadros brutos pelo E3.
    brutos = e3.carregar_populacoes(ROOT)
    confere_quadros = {}
    for nome, g in pops.items():
        b = brutos[nome][["co_ibge", "faixa_anunciada"]].drop_duplicates()
        confere_quadros[nome] = {
            "municipios_matriz": int(len(g)),
            "municipios_quadros_brutos": int(b["co_ibge"].nunique()),
            "mesmos_pares_municipio_faixa": bool(
                set(map(tuple, g[["co_ibge", "faixa_anunciada"]].to_numpy()))
                == set(map(tuple, b.to_numpy()))),
            "quadros_brutos": list(((st.get("populacoes") or {}).get(nome) or {}).get("quadros", {}).keys()),
        }

    # Outcomes (como no relatorio).
    prop = pd.read_csv(E4_PROP, dtype={"co_ibge": str})
    if set(prop["co_ibge"]) != set(pops["P1"]["co_ibge"]):
        raise SystemExit("E4_proporcao_municipio.csv nao cobre exatamente os municipios de P1")
    ativos = e3.ler_ativos(ATIVOS_ZIP)
    ciclo_de = {k: int((v or {}).get("ciclo_do_outcome")) for k, v in (st.get("populacoes") or {}).items()}
    for nome, g in pops.items():
        d_k = e3.construir_d_k(g["co_ibge"], ativos, ciclo_de[nome])
        g[OUTCOME_D] = g["co_ibge"].map(d_k).astype(float)
    pops["P1"] = pops["P1"].merge(prop[["co_ibge", "y1"]].rename(columns={"y1": OUTCOME_FRAC}), on="co_ibge",
                                  how="left")
    return {
        "st": st, "cortes_mil": cortes_mil, "h_mil": h_principal_mil, "mat": mat, "pops": pops,
        "escore_e_ivs_oficial": escore_e_ivs_oficial, "confere_quadros": confere_quadros,
        "a01b": json.loads(A01B.read_text(encoding="utf-8")), "ciclo_de": ciclo_de,
        "sha_ativos_confere_protocolo": sha256(ATIVOS_ZIP) == getattr(e3, "SHA256_ATIVOS_PROTOCOLO", None),
    }


# ---------------------------------------------------------------------------
# Conferencias
# ---------------------------------------------------------------------------


def conferir_regra(base: dict, valor_faixa: dict[str, float]) -> list[dict]:
    """C1 sem outcome: lado do corte x bolsa do quadro, na populacao e na janela principal."""
    vals = sorted(set(valor_faixa.values()))
    out = []
    h = base["h_mil"]
    for nome, g in base["pops"].items():
        s = g["s_mil"].to_numpy(int)
        v = g["valor_anunciado_brl"].to_numpy(float)
        for i, c in enumerate(base["cortes_mil"]):
            v_menor, v_maior = vals[i], vals[i + 1]
            T = s > c
            janela = np.abs(s - c) < h
            out.append({
                "populacao": nome,
                "corte": c / 1000,
                "bolsa_lado_menor_ivs_ate_o_corte": v_menor,
                "bolsa_lado_maior_ivs_acima_do_corte": v_maior,
                "diferenca_brl": v_maior - v_menor,
                "populacao_inteira": {
                    "municipios_com_s_maior_que_c": int(T.sum()),
                    "todos_com_bolsa_maior_ou_igual_a_do_lado_maior": bool(np.all(v[T] >= v_maior)),
                    "municipios_com_s_ate_c": int((~T).sum()),
                    "todos_com_bolsa_menor_ou_igual_a_do_lado_menor": bool(np.all(v[~T] <= v_menor)),
                },
                "janela_principal": {
                    "h": h / 1000,
                    "n_lado_menor": int((janela & ~T).sum()),
                    "n_lado_maior": int((janela & T).sum()),
                    "bolsas_no_lado_menor": sorted(set(v[janela & ~T].tolist())),
                    "bolsas_no_lado_maior": sorted(set(v[janela & T].tolist())),
                    "municipios_em_c_mais_h_peso_zero": int((s == c + h).sum()),
                },
                "ok": bool(np.all(v[T] >= v_maior) and np.all(v[~T] <= v_menor)
                           and set(v[janela & ~T].tolist()) == {v_menor}
                           and set(v[janela & T].tolist()) == {v_maior}
                           and v_maior - v_menor == 5000),
            })
    return out


def trechos_codigo() -> dict:
    linhas = E3_SCRIPT.read_text(encoding="utf-8").splitlines()
    achados = {}
    for chave, padrao in TRECHOS_E3.items():
        rx = re.compile(padrao)
        hit = next(((i + 1, ln.strip()) for i, ln in enumerate(linhas) if rx.search(ln)), None)
        achados[chave] = {"linha": hit[0], "texto": hit[1]} if hit else {"linha": None, "texto": "nao localizado"}
    return achados


def conferir_estimativas(base: dict, e3, valor_faixa: dict[str, float]) -> list[dict]:
    """C3 a C6 em todas as linhas de E3_estimativas.csv."""
    est = pd.read_csv(E3_EST)
    vals = sorted(set(valor_faixa.values()))
    out = []
    for r in est.itertuples():
        g = base["pops"][r.populacao]
        if r.outcome not in g.columns:
            raise SystemExit(f"Outcome {r.outcome} sem dado para {r.populacao}")
        c_mil = int(round(r.corte * 1000))
        h_mil = int(round(r.h * 1000))
        i = base["cortes_mil"].index(c_mil)
        s = g["s_mil"].to_numpy(int)
        y = g[r.outcome].to_numpy(float)
        ind = estimar_independente(s, y, g["valor_anunciado_brl"].to_numpy(float), c_mil, h_mil,
                                   passo_brl=vals[i + 1] - vals[i])
        e3_mesmo_dado = e3.rdd_local_linear(s, y, c_mil, h_mil)  # o estimador do E3 nos dados lidos aqui
        tol_ep = TOL_EP * max(1.0, abs(r.ep))
        checks = {
            "C3_tau_duas_retas_igual_E3": abs(ind["tau_duas_retas"] - r.tau) <= TOL_TAU,
            "C3_dados_lidos_aqui_reproduzem_E3": abs(e3_mesmo_dado["tau"] - r.tau) <= TOL_TAU,
            "C4_tau_bolsa_do_quadro_igual_E3": abs(ind["tau_bolsa_do_quadro"] - r.tau) <= TOL_TAU,
            "C5_ep_hc1_igual_E3": abs(ind["ep_hc1"] - r.ep) <= tol_ep,
            "C1_n_por_lado_igual_E3": (ind["lado_bolsa_menor"]["n"] == r.n_abaixo
                                       and ind["lado_bolsa_maior"]["n"] == r.n_acima),
            "C1_bolsa_menor_abaixo_maior_acima": (ind["bolsa_lado_menor"] == [vals[i]]
                                                  and ind["bolsa_lado_maior"] == [vals[i + 1]]),
            "C6_medias_brutas_iguais_E3": (abs(ind["lado_bolsa_menor"]["media_bruta"] - r.media_bruta_abaixo) <= TOL_MEDIA
                                           and abs(ind["lado_bolsa_maior"]["media_bruta"] - r.media_bruta_acima)
                                           <= TOL_MEDIA),
            "C6_decomposicao_fecha": abs(ind["decomposicao"]["soma"] - ind["diferenca_medias_brutas"]) <= 1e-12,
        }
        out.append({
            "populacao": r.populacao,
            "outcome": r.outcome,
            "corte": float(r.corte),
            "h": float(r.h),
            "especificacao": r.especificacao,
            "bolsa_lado_menor": vals[i],
            "bolsa_lado_maior": vals[i + 1],
            "E3": {"tau": r.tau, "ep": r.ep, "ic95_inf": r.ic95_inf, "ic95_sup": r.ic95_sup, "p_valor": r.p_valor,
                   "n_abaixo": int(r.n_abaixo), "n_acima": int(r.n_acima),
                   "media_bruta_abaixo": r.media_bruta_abaixo, "media_bruta_acima": r.media_bruta_acima},
            "independente": ind,
            "diferencas": {
                "tau_duas_retas_menos_E3": ind["tau_duas_retas"] - r.tau,
                "tau_bolsa_do_quadro_menos_E3": ind["tau_bolsa_do_quadro"] - r.tau,
                "ep_menos_E3": ind["ep_hc1"] - r.ep,
            },
            "sinal_salto_difere_da_diferenca_bruta": bool(np.sign(ind["tau_duas_retas"])
                                                          != np.sign(ind["diferenca_medias_brutas"])),
            "checks": checks,
            "ok": bool(all(checks.values())),
        })
    return out


def montar() -> dict:
    e3 = importar_e3()
    base = carregar_base(e3)
    valor_edital = valores_do_edital(base["a01b"])
    vm = base["mat"].groupby("faixa_anunciada")["valor_anunciado_brl"].agg(lambda s: sorted(set(s)))
    valor_matriz = {f: float(v[0]) for f, v in vm.items() if len(v) == 1}
    if len(valor_matriz) != len(vm):
        raise SystemExit("Mais de um valor anunciado por faixa na matriz.")
    edital_confere = bool(valor_edital and valor_edital == valor_matriz)

    regra = conferir_regra(base, valor_matriz)
    especs = conferir_estimativas(base, e3, valor_matriz)
    trechos = trechos_codigo()
    quadros_ok = all(v["mesmos_pares_municipio_faixa"] for v in base["confere_quadros"].values())

    conferencias = [
        {"id": "C0_insumos", "ok": bool(base["escore_e_ivs_oficial"] and edital_confere and quadros_ok),
         "descricao": "escore do E3 = IVS 2010 oficial (a08); valores por faixa do edital = matriz; população e "
                      "faixa da matriz = quadros brutos lidos pelo E3",
         "detalhe": {"escore_do_E3_igual_ao_IVS_oficial": base["escore_e_ivs_oficial"],
                     "valor_por_faixa_edital": valor_edital, "valor_por_faixa_matriz": valor_matriz,
                     "edital_igual_matriz": edital_confere, "quadros": base["confere_quadros"],
                     "relacao_nominal_e_a_versao_do_protocolo": bool(base["sha_ativos_confere_protocolo"])}},
        {"id": "C1_regra_e_lado", "ok": all(x["ok"] for x in regra),
         "descricao": "todo município com s > c tem a faixa de bolsa maior no quadro e todo município com s <= c, a "
                      "menor (população inteira e janela principal); a diferença é de R$ 5 mil",
         "detalhe": regra},
        {"id": "C2_convencao_no_codigo", "ok": all(v["linha"] for v in trechos.values()),
         "descricao": "no E3, x = s - c, T = 1[s > c], X = [1, x, T, T*x] e tau = coeficiente de T: o limite pela "
                      "direita (bolsa maior) menos o limite pela esquerda (bolsa menor)",
         "detalhe": {"arquivo": rel(E3_SCRIPT), "trechos": trechos}},
        {"id": "C3_reestimacao_independente", "ok": all(x["checks"]["C3_tau_duas_retas_igual_E3"]
                                                        and x["checks"]["C3_dados_lidos_aqui_reproduzem_E3"]
                                                        for x in especs),
         "descricao": "duas retas ponderadas separadas (fórmula fechada): o intercepto do lado da bolsa maior menos o "
                      "do lado da bolsa menor reproduz o tau do E3 em todas as especificações",
         "detalhe": {"especificacoes": len(especs),
                     "max_abs_diferenca": max(abs(x["diferencas"]["tau_duas_retas_menos_E3"]) for x in especs),
                     "tolerancia": TOL_TAU}},
        {"id": "C4_tratamento_lido_do_quadro", "ok": all(x["checks"]["C4_tau_bolsa_do_quadro_igual_E3"]
                                                         for x in especs),
         "descricao": "com (bolsa do quadro - bolsa do lado menor) / R$ 5 mil no lugar de T, o coeficiente é o "
                      "mesmo: o salto é por +R$ 5 mil, com o sinal da bolsa maior",
         "detalhe": {"max_abs_diferenca": max(abs(x["diferencas"]["tau_bolsa_do_quadro_menos_E3"]) for x in especs),
                     "tolerancia": TOL_TAU}},
        {"id": "C5_erro_padrao", "ok": all(x["checks"]["C5_ep_hc1_igual_E3"] for x in especs),
         "descricao": "EP HC1 recalculado (lstsq e sanduíche explícito) igual ao do E3",
         "detalhe": {"max_abs_diferenca": max(abs(x["diferencas"]["ep_menos_E3"]) for x in especs),
                     "tolerancia": TOL_EP}},
        {"id": "C6_medias_brutas_e_salto", "ok": all(x["checks"]["C6_medias_brutas_iguais_E3"]
                                                     and x["checks"]["C6_decomposicao_fecha"] for x in especs),
         "descricao": "médias brutas iguais às do E3; diferença de médias brutas = salto + inclinação + resíduo "
                      "(identidade exata)",
         "detalhe": {"especificacoes_com_sinal_oposto": [
             {"populacao": x["populacao"], "outcome": x["outcome"], "corte": x["corte"], "h": x["h"],
              "salto": x["independente"]["tau_duas_retas"],
              "diferenca_medias_brutas": x["independente"]["diferenca_medias_brutas"]}
             for x in especs if x["sinal_salto_difere_da_diferenca_bruta"]]}},
    ]
    tudo_ok = all(c["ok"] for c in conferencias) and all(x["ok"] for x in especs)

    # Leitura do caso que motivou a conferencia: P1, preenchimento, corte 0,300, janela principal.
    caso = next((x for x in especs if x["populacao"] == "P1" and x["outcome"] == OUTCOME_FRAC
                 and math.isclose(x["corte"], base["cortes_mil"][0] / 1000)
                 and math.isclose(x["h"], base["h_mil"] / 1000)), None)
    leitura_caso = None
    if caso:
        ind = caso["independente"]
        L0, L1, dec = ind["lado_bolsa_menor"], ind["lado_bolsa_maior"], ind["decomposicao"]
        b0, b1 = mil(caso["bolsa_lado_menor"]), mil(caso["bolsa_lado_maior"])
        leitura_caso = (
            f"Corte {num(caso['corte'], 3)}, preenchimento do ciclo 1: média bruta de {pct(L0['media_bruta'])} do lado "
            f"de {b0} e {pct(L1['media_bruta'])} do lado de {b1} (diferença de {pp(ind['diferenca_medias_brutas'])} "
            f"p.p.). No próprio corte, a reta do lado de {b0} vale {pct(L0['valor_da_reta_no_corte'])} e a do lado de "
            f"{b1}, {pct(L1['valor_da_reta_no_corte'])}: salto de {pp(dec['salto'])} p.p. As médias brutas são tomadas "
            f"no meio de cada lado (IVS médio {num(L0['ivs_medio'], 3)} e {num(L1['ivs_medio'], 3)}); a reta do lado de "
            f"{b0} sobe {num(100 * L0['inclinacao_por_0_010_de_ivs'], 1)} p.p. a cada 0,010 de IVS até o corte. "
            f"Decomposição: {pp(ind['diferenca_medias_brutas'])} = {pp(dec['salto'])} (salto) "
            f"{pp(dec['inclinacao_dentro_da_janela'])} (inclinação dentro da janela) {pp(dec['residuo'])} (resíduo).")

    vals = sorted(set(valor_matriz.values()))
    por_corte = "; ".join(f"{mil(vals[i + 1])} menos {mil(vals[i])} em {num(c / 1000, 3)}"
                          for i, c in enumerate(base["cortes_mil"]))
    return limpo({
        "etapa": "E3_conferencia_sinal",
        "script": rel(Path(__file__)),
        "data_execucao": dt.date.today().isoformat(),
        "natureza_dos_dados": "EMPIRICO",
        "outcomes_abertos": True,
        "nota_outcomes": "lê os mesmos outcomes já abertos pelo E3; não escolhe amostra, janela nem estimador",
        "pergunta": "O salto do E3 é o efeito de passar da bolsa MENOR para a MAIOR?",
        "status": "CONFERIDO" if tudo_ok else "DIVERGENCIA",
        "resposta": (
            "Sim. O salto é o valor no corte do lado com bolsa R$ 5 mil maior (IVS acima do corte) menos o valor do "
            f"lado com bolsa menor (IVS até o corte, inclusive): {por_corte}. Positivo = bolsa maior associada a "
            "mais preenchimento (ou presença)."
            if tudo_ok else "Há divergência: ver as conferências com ok = false."),
        "convencao": {
            "running_variable": "IVS 2010 oficial do Ipea (= escore administrativo do MS), em milésimos",
            "lado_do_corte": base["st"].get("lado_do_corte"),
            "salto": "tau = lim s->c+ E[y|s] - lim s->c- E[y|s] = (lado da bolsa maior) - (lado da bolsa menor)",
            "estimador": "local linear, kernel triangular max(0, 1 - |s - c| / h), EP HC1 por município",
        },
        "leitura_do_caso_0300": leitura_caso,
        "conferencias": conferencias,
        "por_especificacao": especs,
        "entradas": {rel(p): {"sha256": sha256(p)} for p in ENTRADAS},
    })


def main() -> int:
    res = montar()
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": res["status"], "conferencias": {c["id"]: c["ok"] for c in res["conferencias"]}},
                     ensure_ascii=False, indent=2))
    if res.get("leitura_do_caso_0300"):
        print(res["leitura_do_caso_0300"])
    print(f"Gravado: {rel(SAIDA)}")
    return 0 if res["status"] == "CONFERIDO" else 1


if __name__ == "__main__":
    sys.exit(main())
