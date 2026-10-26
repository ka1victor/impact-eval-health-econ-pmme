"""Auditoria 38: compara o recálculo independente (a38_recalculo.py) com output/rdd_bolsa/HI_estimativas.csv.

Uso: python3 scripts/auditoria_H1/a38_comparar.py <raiz> <json do a38_recalculo>. Só lê; imprime as diferenças.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1])
meu = json.loads(Path(sys.argv[2]).read_text())
e = pd.read_csv(ROOT / "output/rdd_bolsa/HI_estimativas.csv", dtype={"corte": str, "ciclo": str})
CT = {300: "0.300", 400: "0.400"}


def ref(linha, outcome, corte, ciclo, variante, versao="13fev"):
    m = (e["linha"] == linha) & (e["outcome"] == outcome) & (e["corte"] == CT[corte]) & (e["ciclo"] == ciclo) & \
        (e["variante"] == variante) & (e["versao_quadro_c2"] == versao)
    s = e[m]
    assert len(s) == 1, (linha, outcome, corte, ciclo, variante, versao, len(s))
    return s.iloc[0]


MAP = {
    ("HI-1", "principal"): ("HI-1", "HI-1", "principal"), ("HI-2", "principal"): ("HI-2", "HI-2", "principal"),
    ("HI-1", "por_ciclo"): ("HI-s1", "HI-1", "por_ciclo"), ("HI-2", "por_ciclo"): ("HI-s1", "HI-2", "por_ciclo"),
    ("HI-s3", "sem_controle"): ("HI-s3", "HI-2", "sem_controle"),
    ("HI-s6_cel", "so_cr"): ("HI-s6", "CR_CELULA", "so_cadastro_reserva"),
    ("HI-s6_mun", "so_cr"): ("HI-s6", "CR_MUN", "so_cadastro_reserva"),
    ("HI-s4_cel", "pura"): ("HI-s4", "HI-1_PURA", "so_celulas_puras"),
    ("HI-s4_mun", "pura"): ("HI-s4", "HI-2_PURA", "so_celulas_puras"),
    ("HI-s2_F13", "F1.3"): ("HI-s2", "HI-1_F13", "definicao_F1.3"),
    ("HI-s5", "F1.4"): ("HI-s5", "F14_TODAS", "ate_2a_chamada_todas_as_celulas"),
    ("HI-1", "h=0.030"): ("HI-s8", "HI-1", "h=0.030"), ("HI-2", "h=0.030"): ("HI-s8", "HI-2", "h=0.030"),
    ("HI-1", "h=0.080"): ("HI-s8", "HI-1", "h=0.080"), ("HI-2", "h=0.080"): ("HI-s8", "HI-2", "h=0.080"),
    ("HI-1", "ic_honesto_M_x1"): ("HI-s8", "HI-1", "ic_honesto_M_x1"),
    ("HI-2", "ic_honesto_M_x1"): ("HI-s8", "HI-2", "ic_honesto_M_x1"),
}
rows = []
for x in meu["linhas"]:
    if x["variante"] == "tost":
        nome = x["id"].split()
        tipo = "TOST_convencional" if nome[2] == "conv" else "TOST_honesto"
        r = ref("HI-s7", nome[1], x["corte"], "1+2+3", tipo)
        rows.append({"linha": x["id"], "corte": x["corte"], "ciclo": x["ciclo"],
                     "dif_ic90_inf": abs(x["ic90_inf"] - r["ic90_inf"]), "dif_ic90_sup": abs(x["ic90_sup"] - r["ic90_sup"]),
                     "dif_p_aum": abs(x["p_aumento"] - r["p_aumento"]), "dif_p_que": abs(x["p_queda"] - r["p_queda"]),
                     "leitura_igual": x["leitura"] == r["leitura_tost"]})
        continue
    if x["c2"] == "19":
        if x["variante"] == "por_ciclo" and x["ciclo"] != "2":
            continue
        r = ref("SENS-19MAR", x["id"], x["corte"], x["ciclo"], "tipo_vaga_pos_resultado_19mar", "19mar")
    else:
        lin, oid, var = MAP[(x["id"], x["variante"])]
        r = ref(lin, oid, x["corte"], x["ciclo"], var)
    d = {"linha": f"{x['id']}|{x['variante']}|c2={x['c2']}", "corte": x["corte"], "ciclo": x["ciclo"],
         "meu_tau": x["tau"], "dif_tau": abs(x["tau"] - r["tau"]), "dif_ep": abs(x["ep"] - r["ep"]),
         "dif_ic_inf": abs(x["ic95_inf"] - r["ic95_inf"]), "dif_ic_sup": abs(x["ic95_sup"] - r["ic95_sup"])}
    if "p_valor" in x:
        d["dif_p"] = abs(x["p_valor"] - r["p_valor"])
        d["n_igual"] = (x["n_abaixo"], x["n_acima"], x["n_obs"]) == (int(r["n_abaixo"]), int(r["n_acima"]), int(r["n_obs"]))
        d["dif_media"] = abs(x["media_abaixo"] - r["media_abaixo"])
    else:
        d["dif_M_rel"] = abs(x["M"] / r["M"] - 1)
        d["dif_vies"] = abs(x["vies_max"] - r["vies_max"])
    rows.append(d)
t = pd.DataFrame(rows)
pd.set_option("display.width", 250)
print(t.to_string())
num = t.select_dtypes("number").drop(columns=["corte", "meu_tau"], errors="ignore")
print("max dif por coluna:\n", num.max())
print("n_igual todas:", t["n_igual"].dropna().all(), "leituras TOST iguais:", t["leitura_igual"].dropna().all())
prim = e[e["entra_holm"]]
print("holm meu:", meu["holm"], "\nholm csv (mesma ordem? linhas):", list(zip(prim["linha"], prim["corte"], prim["p_holm"])))
print("p meu:", meu["holm_p"])


def bky(p):
    """q-valores aguçados BKY (Anderson, 2008), reescritos aqui."""
    p = np.asarray(p, float); m = len(p); o = np.argsort(p, kind="stable"); ps = p[o]; rk = np.arange(1, m + 1)
    q = np.ones(m)
    for kk in range(1000, 0, -1):
        qq = kk / 1000; q1 = qq / (1 + qq)
        R1 = rk[ps <= q1 * rk / m].max() if (ps <= q1 * rk / m).any() else 0
        q2 = q1 * m / (m - R1) if R1 < m else np.inf
        R2 = rk[ps <= q2 * rk / m].max() if (ps <= q2 * rk / m).any() else 0
        q[rk <= R2] = qq
    out = np.empty(m); out[o] = q
    return out


b = e[e["entra_bky"]]
print("BKY: linhas", len(b), "max |dif q|", float(np.abs(bky(b["p_valor"].to_numpy(float)) - b["q_bky"].to_numpy(float)).max()))
