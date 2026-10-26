"""Auditoria 38: recálculo independente do adendo 48b (não importa o script 40, a rdd_lib nem scripts do projeto).

Lê só: outcomes_V_celula.parquet (alocados por célula, já reconstruídos dos brutos pela auditoria 36),
a08 (IVS 2010 oficial) e os dois quadros brutos do ciclo 2 (13/02 e 19/03). Nada é gravado: o resultado (JSON) vai
para a saída padrão. Estimador próprio: Frisch–Waugh–Lovell + CR1 por município; IC honesto, TOST, Holm e BKY
reescritos aqui.
Uso (da raiz):
    python3 scripts/auditoria_H1/a38_recalculo.py > /tmp/a38.json
    python3 scripts/auditoria_H1/a38_comparar.py . /tmp/a38.json
"""
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
CEL = ROOT / "output/rdd_bolsa/outcomes/outcomes_V_celula.parquet"
A08 = ROOT / "output/aquisicao/a08_ivs_2010_oficial_municipio.csv"
Q13 = ROOT / "data/raw/aquisicao/vagas/2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx"
Q19 = ROOT / "data/raw/pmm_e/2026_ciclo2_chamada1_vagas_retificadas.xlsx"
H = 50.0


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ler_quadro_bruto(p):
    raw = pd.read_excel(p, header=None, dtype=object)
    # cabeçalho na linha 1; imediatas = col 10 (TOTAL sob VAGAS IMEDIATAS), CR = col 14 (TOTAL sob CADASTRO RESERVA)
    assert str(raw.iloc[0, 10]).strip().upper() == "VAGAS IMEDIATAS", raw.iloc[0, 10]
    assert str(raw.iloc[0, 14]).strip().upper() == "CADASTRO RESERVA", raw.iloc[0, 14]
    assert str(raw.iloc[1, 10]).strip().upper() == "TOTAL" and str(raw.iloc[1, 14]).strip().upper() == "TOTAL"
    b = raw.iloc[2:]
    b = b[b[5].notna() & b[0].notna()]
    cnes = b[5].map(lambda v: str(int(float(v))).zfill(7))
    curso = b[0].astype(str).str.extract(r"^\s*(\d+)")[0].astype(int)
    q = pd.DataFrame({"cnes": cnes.values, "curso": curso.values,
                      "vi": pd.to_numeric(b[10]).astype(float).values, "cr": pd.to_numeric(b[14]).astype(float).values})
    assert not q.duplicated(["cnes", "curso"]).any()
    return q


# ---------------------------------------------------------------- estimador próprio (FWL + CR1)
def kern(x, h):
    return np.where((x > -h) & (x < h), 1.0 - np.abs(x) / h, 0.0)


def ajuste(d, y, cut, grupo, cluster, h=H, fe=None, Z=None, devolver=False):
    """y = sum_g 1[g](a_g + b_g r + d_g T r) + tau T [+ FE] [+ Z]; MQP kernel triangular; CR1 por cluster."""
    s = d["s_mil"].to_numpy(float)
    x = s - cut
    w = kern(x, h)
    y = np.asarray(y, float)
    use = (w > 0) & np.isfinite(y)
    if Z is not None:
        use &= np.isfinite(Z).all(axis=1)
    x, w, y = x[use], w[use], y[use]
    g = np.asarray(grupo)[use]
    cl = np.asarray(cluster).astype(str)[use]
    r = x / 1000.0
    T = (x > 0).astype(float)
    cols = []
    for gg in sorted(set(g)):
        ind = (g == gg).astype(float)
        cols += [ind, ind * r, ind * T * r]
    if fe is not None:
        f = np.asarray(fe)[use]
        for lv in sorted(set(f)):
            cols.append((f == lv).astype(float))
    if Z is not None:
        Zu = Z[use]
        for j in range(Zu.shape[1]):
            cols.append(Zu[:, j])
    N = np.column_stack(cols)
    sw = np.sqrt(w)
    Nw = N * sw[:, None]
    rk = np.linalg.matrix_rank(Nw, tol=1e-9 * np.linalg.norm(Nw, 2))
    def resid(v):
        b = np.linalg.lstsq(Nw, v * sw, rcond=None)[0]
        return v * sw - Nw @ b  # resíduo ponderado (multiplicado por sqrt(w))
    Tt = resid(T)
    yt = resid(y)
    tau = float(Tt @ yt / (Tt @ Tt))
    e_w = yt - tau * Tt          # = sqrt(w) * e
    n, k = len(y), rk + 1
    infl = Tt * e_w / (Tt @ Tt)  # = a_i e_i
    ids, inv = np.unique(cl, return_inverse=True)
    G = len(ids)
    S = np.bincount(inv, weights=infl, minlength=G)
    V = float(np.sum(S ** 2)) * (G / (G - 1)) * ((n - 1) / (n - k))
    ep = math.sqrt(V)
    out = {"tau": tau, "ep": ep, "ic95_inf": tau - 1.959963984540054 * ep, "ic95_sup": tau + 1.959963984540054 * ep,
           "p_valor": math.erfc(abs(tau / ep) / math.sqrt(2)), "n_obs": int(n),
           "n_abaixo": len(set(cl[x <= 0])), "n_acima": len(set(cl[x > 0])),
           "media_abaixo": float(y[x <= 0].mean()), "k": k}
    if devolver:
        a = Tt * sw / (Tt @ Tt)   # pesos a_i do estimador linear: tau = sum a_i y_i
        out.update({"a": a, "r": r, "e": e_w / sw, "inv": inv, "G": G, "n": n})
    return out


def regra_m(s, y, cut, sup):
    lo, hi = sup
    r = (s - cut) / 1000.0
    ok = np.isfinite(y) & (s >= lo) & (s <= hi)
    ms = []
    for lado in (r <= 0, r > 0):
        m = ok & lado
        rr, yy = r[m], y[m]
        P = np.column_stack([rr ** p for p in range(5)])
        b = np.linalg.lstsq(P, yy, rcond=None)[0]
        f2 = lambda u: abs(2 * b[2] + 6 * b[3] * u + 12 * b[4] * u ** 2)
        c = [f2(rr.min()), f2(rr.max())]
        if abs(b[4]) > 1e-10:
            ex = -b[3] / (4 * b[4])
            if rr.min() < ex < rr.max():
                c.append(f2(ex))
        ms.append(max(c))
    return max(ms)


def cv(t):
    f = lambda c: stats.norm.cdf(c - t) - stats.norm.cdf(-c - t) - 0.95
    return optimize.brentq(f, 0, t + 10, xtol=1e-14)


def honesto(d, y, cut, grupo, cluster, fe=None, fator=1.0):
    sup = (-np.inf, 350.0) if cut == 300 else (350.0, np.inf)
    s = d["s_mil"].to_numpy(float)
    M = max(regra_m(s[np.asarray(grupo) == g], np.asarray(y, float)[np.asarray(grupo) == g], cut, sup)
            for g in sorted(set(grupo))) * fator
    r = ajuste(d, y, cut, grupo, cluster, fe=fe, devolver=True)
    a, rr, e, inv, G, n, k = r["a"], r["r"], r["e"], r["inv"], r["G"], r["n"], r["k"]
    S = np.bincount(inv, weights=a * e, minlength=G)
    ep = math.sqrt(float(np.sum(S ** 2)) * (G / (G - 1)) * ((n - 1) / (n - k)))
    B = 0.5 * M * float(np.sum(np.abs(a) * rr ** 2))
    c = cv(B / ep)
    return {"tau": r["tau"], "ep": ep, "M": M, "vies_max": B, "ic95_inf": r["tau"] - c * ep,
            "ic95_sup": r["tau"] + c * ep}


def tost(tau, ep, m, B=0.0):
    z = stats.norm.ppf(0.95)
    pa = stats.norm.cdf((tau - m + B) / ep)
    pq = stats.norm.cdf((-m - tau + B) / ep)
    lo, hi = tau - (B + z * ep), tau + (B + z * ep)
    lei = ("EQUIVALENTE" if pa < .05 and pq < .05 else "SO_AUMENTO" if pa < .05 else "SO_QUEDA" if pq < .05
           else "INCONCLUSIVO")
    return {"ic90_inf": lo, "ic90_sup": hi, "p_aumento": pa, "p_queda": pq, "leitura": lei}


def holm(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p, kind="stable")
    adj = np.minimum(1, (m - np.arange(m)) * p[o]); out = np.empty(m); out[o] = np.maximum.accumulate(adj)
    return out


def bky(p):
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


# ---------------------------------------------------------------- dados
def montar():
    cel = pd.read_parquet(CEL)
    a08 = pd.read_csv(A08, dtype={"co_ibge": str})
    a08["co_ibge"] = a08["co_ibge"].str[:6].str.zfill(6)
    mil = a08["ivs"].astype(float) * 1000
    assert (np.abs(mil - mil.round()) < 1e-6).all()
    a08["s_mil"] = mil.round()
    cel["co_ibge"] = cel["co_ibge"].astype(str).str.zfill(6)
    cel = cel.merge(a08[["co_ibge", "s_mil"]], on="co_ibge", how="left")
    q13, q19 = ler_quadro_bruto(Q13), ler_quadro_bruto(Q19)
    c2 = cel["ciclo"] == 2
    key = cel["co_cnes_7d"].astype(str).str.zfill(7) + "_" + cel["cod_curso"].astype(int).astype(str)
    k13 = q13["cnes"] + "_" + q13["curso"].astype(str)
    k19 = q19["cnes"] + "_" + q19["curso"].astype(str)
    assert set(k13) == set(key[c2]) == set(k19), "células de 13/02, 19/03 e pipeline diferentes"
    cel["vi19"], cel["cr19"] = cel["vagas_imediatas"].astype(float), cel["vagas_cr"].astype(float)
    # o pipeline do ciclo 2 tem de ser o quadro de 19/03
    m19 = key[c2].map(dict(zip(k19, q19["vi"])))
    assert (m19.values == cel.loc[c2, "vagas_imediatas"].values).all(), "pipeline c2 != 19/03"
    cel["vi13"], cel["cr13"] = cel["vi19"], cel["cr19"]
    cel.loc[c2, "vi13"] = key[c2].map(dict(zip(k13, q13["vi"]))).values
    cel.loc[c2, "cr13"] = key[c2].map(dict(zip(k13, q13["cr"]))).values
    return cel, q13, q19


def amostras(cel, versao):
    vi, cr = cel[f"vi{versao}"], cel[f"cr{versao}"]
    c = cel.copy()
    c["vi"], c["cr"] = vi, cr
    c["tipo"] = np.where((vi > 0) & (cr > 0), "mista", np.where(vi > 0, "so_imed", "so_cr"))
    c["y1"] = (c["n_alocados_ch1"] >= 1).astype(float)
    c["fe"] = "c" + c["ciclo"].astype(str) + "_" + c["cod_curso"].astype(str)
    c["grupo"] = "c" + c["ciclo"].astype(str)
    c = c[c["s_mil"].notna()]
    return c


def municipios(c, tipos, ycol="n_alocados_ch1", vcol="vi"):
    m = c[c["tipo"].isin(tipos)]
    g = m.groupby(["ciclo", "co_ibge"]).agg(y=(ycol, "sum"), v=(vcol, "sum"), s_mil=("s_mil", "first")).reset_index()
    g["grupo"] = "c" + g["ciclo"].astype(str)
    return g


def Zciclo(g, ks=(1, 2, 3)):
    return np.column_stack([np.where(g["ciclo"] == k, g["v"].astype(float), 0.0) for k in ks if (g["ciclo"] == k).any()])


def main():
    cel, q13, q19 = montar()
    res = {"entradas": {str(p.relative_to(ROOT)): sha(p) for p in (CEL, A08, Q13, Q19)}}
    # contagens do ciclo 2
    c2 = cel[cel["ciclo"] == 2]
    so_cr13 = c2["vi13"] == 0
    res["c2"] = {"celulas": int(len(c2)), "vi13": c2["vi13"].sum(), "cr13": c2["cr13"].sum(),
                 "vi19": c2["vi19"].sum(), "cr19": c2["cr19"].sum(),
                 "so_cr_13": int(so_cr13.sum()), "so_cr13_com_vi19": int((so_cr13 & (c2["vi19"] > 0)).sum()),
                 "dessas_com_alocado": int((so_cr13 & (c2["vi19"] > 0) & (c2["n_alocados_ch1"] > 0)).sum()),
                 "convertidas": float((c2["vi19"] - c2["vi13"]).clip(lower=0).sum()),
                 "aloc_so_cr_13": float(c2.loc[so_cr13, "n_alocados_ch1"].sum()),
                 "aloc_total": float(c2["n_alocados_ch1"].sum()),
                 "so_cr_19": int((c2["vi19"] == 0).sum()),
                 "so_cr19_com_alocado": int(((c2["vi19"] == 0) & (c2["n_alocados_ch1"] > 0)).sum()),
                 "total_dif": int(((c2["vi13"] + c2["cr13"]) != (c2["vi19"] + c2["cr19"])).sum())}
    out = []
    for versao in ("13", "19"):
        c = amostras(cel, versao)
        for cut in (300, 400):
            imed = c[c["tipo"].isin(["so_imed", "mista"])]
            r = ajuste(imed, imed["y1"], cut, imed["grupo"], imed["co_ibge"], fe=imed["fe"])
            out.append(("HI-1", versao, cut, "1+2+3", "principal", r))
            g = municipios(c, ["so_imed", "mista"])
            r = ajuste(g, g["y"], cut, g["grupo"], g["co_ibge"], Z=Zciclo(g))
            out.append(("HI-2", versao, cut, "1+2+3", "principal", r))
            for k in (1, 2, 3):
                ik = imed[imed["ciclo"] == k]
                out.append(("HI-1", versao, cut, str(k), "por_ciclo",
                            ajuste(ik, ik["y1"], cut, np.full(len(ik), "u"), ik["co_ibge"], fe=ik["fe"])))
                gk = g[g["ciclo"] == k]
                out.append(("HI-2", versao, cut, str(k), "por_ciclo",
                            ajuste(gk, gk["y"], cut, np.full(len(gk), "u"), gk["co_ibge"], Z=gk[["v"]].to_numpy(float))))
            if versao == "19":
                continue
            out.append(("HI-s3", versao, cut, "1+2+3", "sem_controle", ajuste(g, g["y"], cut, g["grupo"], g["co_ibge"])))
            cr = c[c["tipo"] == "so_cr"]
            out.append(("HI-s6_cel", versao, cut, "1+2+3", "so_cr",
                        ajuste(cr, cr["y1"], cut, cr["grupo"], cr["co_ibge"], fe=cr["fe"])))
            gc = municipios(c, ["so_cr"], vcol="cr")
            out.append(("HI-s6_mun", versao, cut, "1+2+3", "so_cr",
                        ajuste(gc, gc["y"], cut, gc["grupo"], gc["co_ibge"], Z=Zciclo(gc))))
            pu = c[c["tipo"] == "so_imed"]
            out.append(("HI-s4_cel", versao, cut, "1+2+3", "pura",
                        ajuste(pu, pu["y1"], cut, pu["grupo"], pu["co_ibge"], fe=pu["fe"])))
            gp = municipios(c, ["so_imed"])
            out.append(("HI-s4_mun", versao, cut, "1+2+3", "pura",
                        ajuste(gp, gp["y"], cut, gp["grupo"], gp["co_ibge"], Z=Zciclo(gp))))
            f13 = imed["f1_3_preenchida_ch1"].astype(float)
            out.append(("HI-s2_F13", versao, cut, "1+2+3", "F1.3",
                        ajuste(imed, f13, cut, imed["grupo"], imed["co_ibge"], fe=imed["fe"])))
            c12 = c[c["ciclo"].isin([1, 2])]
            out.append(("HI-s5", versao, cut, "1+2", "F1.4",
                        ajuste(c12, c12["f1_4_preenchida_ate_ch2"].astype(float), cut, c12["grupo"], c12["co_ibge"],
                               fe=c12["fe"])))
            for h in (30.0, 80.0):
                out.append(("HI-1", versao, cut, "1+2+3", f"h={h/1000:.3f}",
                            ajuste(imed, imed["y1"], cut, imed["grupo"], imed["co_ibge"], h=h, fe=imed["fe"])))
                out.append(("HI-2", versao, cut, "1+2+3", f"h={h/1000:.3f}",
                            ajuste(g, g["y"], cut, g["grupo"], g["co_ibge"], h=h, Z=Zciclo(g))))
            # honesto (M x1) e TOST
            hon1 = honesto(imed, imed["y1"].to_numpy(), cut, imed["grupo"].to_numpy(), imed["co_ibge"],
                           fe=imed["fe"])
            # HI-2: y residualizado pelo gamma da regressão principal (constante por grupo não importa)
            rr = ajuste(g, g["y"], cut, g["grupo"], g["co_ibge"], Z=Zciclo(g))
            # gamma: refaz por MQP direta para obter os coeficientes do controle
            s = g["s_mil"].to_numpy(float); x = s - cut; w = kern(x, H); u = w > 0
            gr = g["grupo"].to_numpy(); T = (x > 0).astype(float); rv = x / 1000
            cols = []
            for gg in sorted(set(gr)):
                ind = (gr == gg).astype(float); cols += [ind, ind * rv, ind * T * rv]
            cols.append(T)
            Zc = Zciclo(g)
            X = np.column_stack(cols + [Zc[:, j] for j in range(Zc.shape[1])])
            b = np.linalg.lstsq(X[u] * np.sqrt(w[u])[:, None], g["y"].to_numpy(float)[u] * np.sqrt(w[u]), rcond=None)[0]
            gam = b[-Zc.shape[1]:]
            assert abs(b[len(cols) - 1] - rr["tau"]) < 1e-9
            ytil = g["y"].to_numpy(float) - Zc @ gam
            hon2 = honesto(g, ytil, cut, gr, g["co_ibge"])
            for nome, hon in (("HI-1", hon1), ("HI-2", hon2)):
                out.append((nome, versao, cut, "1+2+3", "ic_honesto_M_x1", hon))
            prim1 = [o for o in out if o[0] == "HI-1" and o[1] == versao and o[2] == cut and o[4] == "principal"][0][5]
            prim2 = [o for o in out if o[0] == "HI-2" and o[1] == versao and o[2] == cut and o[4] == "principal"][0][5]
            out.append(("TOST HI-1 conv", versao, cut, "1+2+3", "tost", tost(prim1["tau"], prim1["ep"], 0.10)))
            out.append(("TOST HI-1 hon", versao, cut, "1+2+3", "tost", tost(hon1["tau"], hon1["ep"], 0.10, hon1["vies_max"])))
            m2 = 0.25 * prim2["media_abaixo"]
            out.append(("TOST HI-2 conv", versao, cut, "1+2+3", "tost", tost(prim2["tau"], prim2["ep"], m2)))
            out.append(("TOST HI-2 hon", versao, cut, "1+2+3", "tost", tost(hon2["tau"], hon2["ep"], m2, hon2["vies_max"])))
            # contagens da amostra
            res.setdefault("amostra", {})
    # contagens por ciclo (13/02)
    c = amostras(cel, "13")
    cc = {}
    for k in (1, 2, 3):
        ck = cel[cel["ciclo"] == k]
        x = c[c["ciclo"] == k]
        g = x.groupby("co_ibge")["tipo"].agg(lambda t: (t != "so_cr").any())
        cc[k] = {"celulas": int(len(ck)), "sem_ivs": int(ck["s_mil"].isna().sum()),
                 "so_imed": int((x["tipo"] == "so_imed").sum()), "mista": int((x["tipo"] == "mista").sum()),
                 "so_cr": int((x["tipo"] == "so_cr").sum()),
                 "aloc_so_cr": float(x.loc[x["tipo"] == "so_cr", "n_alocados_ch1"].sum()),
                 "mun": int(x["co_ibge"].nunique()), "mun_hi2": int(g.sum()), "mun_so_cr": int((~g).sum())}
    res["contagens_13"] = cc
    res["linhas"] = [{"id": o[0], "c2": o[1], "corte": o[2], "ciclo": o[3], "variante": o[4],
                      **{k: v for k, v in o[5].items() if not isinstance(v, np.ndarray)}} for o in out]
    # Holm e BKY
    p = [o[5]["p_valor"] for o in out if o[1] == "13" and o[4] == "principal" and o[3] == "1+2+3"]
    res["holm"] = holm(p).tolist()
    res["holm_p"] = p
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
