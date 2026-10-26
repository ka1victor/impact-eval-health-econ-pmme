"""Auditoria 42: recálculo independente do adendo 48c (capitais e UF no corte 0,300).

Não importa o script 41, a `rdd_lib` nem a reconstrução da auditoria 36. Lê só arquivos:
- `output/auditoria_H1/a36_celulas.csv` (base de células já auditada na auditoria 36): ciclo, chave, curso, município,
  vagas imediatas do quadro pré-alocação (c2 = 13/02/2026), vagas imediatas e de reserva do pipeline, alocados;
- o quadro bruto do ciclo 2 de 13/02/2026 (`data/raw/aquisicao/vagas/`, só leitura), lido aqui com um leitor próprio,
  para conferir as vagas imediatas pré-alocação do ciclo 2;
- o IVS 2010 oficial (a08), única running variable;
- a referência de capitais e regiões do IBGE (`output/aquisicao/ibge_capitais_uf_regiao.csv`) e, para conferir a
  região de cada UF sem rede, a REGIC 2018 do IBGE arquivada em `data/raw/aquisicao/territorio/` e a coluna
  "Região" do mesmo quadro bruto do ciclo 2 (MS);
- `output/rdd_bolsa/HC_estimativas.csv`, `HC_resumo.json` e `HI_estimativas.csv`, só para comparar no fim.

Estimador escrito do zero: mínimos quadrados ponderados com kernel triangular (h = 0,050, |IVS − corte| < h),
intercepto, inclinação e inclinação × lado por ciclo, salto comum; efeitos fixos por dummies; colunas colineares
descartadas por posto; EP CR1 por município com fator G/(G−1)·(n−1)/(n−k); IC e p pela normal.

Grava `output/auditoria_H1/a42_recalculo.csv` e `a42_resumo.json` (natureza EMPIRICO; rótulo AUDITORIA_42_RECALCULO).
Não grava nada em `output/rdd_bolsa/` nem em `data/`.

Uso: python3 scripts/auditoria_H1/a42_auditoria_capitais_uf.py
"""

from __future__ import annotations

import builtins
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
CEL = RAIZ / "output" / "auditoria_H1" / "a36_celulas.csv"
IVS = RAIZ / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
REF = RAIZ / "output" / "aquisicao" / "ibge_capitais_uf_regiao.csv"
REF_MAN = RAIZ / "output" / "aquisicao" / "manifesto_ibge_capitais_uf_regiao.json"
REGIC = RAIZ / "data" / "raw" / "aquisicao" / "territorio" / "REGIC2018_Municipios_Hierarquia_e_regiao.xlsx"
Q_C2_13FEV = RAIZ / "data" / "raw" / "aquisicao" / "vagas" / "2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx"
HC_EST = RAIZ / "output" / "rdd_bolsa" / "HC_estimativas.csv"
HC_RES = RAIZ / "output" / "rdd_bolsa" / "HC_resumo.json"
HI_EST = RAIZ / "output" / "rdd_bolsa" / "HI_estimativas.csv"
SAIDA = RAIZ / "output" / "auditoria_H1"
ARQUIVO_PROIBIDO = "ivs_ipea_2010_municipios.csv"
H = 50          # 0,050 em milésimos
ROTULO = "AUDITORIA_42_RECALCULO"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------------------------------------------
# Rastreio de arquivos abertos: o arquivo de IVS errado não pode ser aberto por nada que este script rode.
# ---------------------------------------------------------------------------------------------------------------
ABERTOS: list[str] = []
_open = builtins.open


def _open_rastreado(arquivo, *a, **k):
    ABERTOS.append(str(arquivo))
    if ARQUIVO_PROIBIDO in str(arquivo):
        raise RuntimeError("arquivo de IVS errado aberto")
    return _open(arquivo, *a, **k)


builtins.open = _open_rastreado


# ---------------------------------------------------------------------------------------------------------------
# 1. Referência de capitais e regiões
# ---------------------------------------------------------------------------------------------------------------

def conferir_referencia() -> tuple[pd.DataFrame, dict]:
    man = json.loads(REF_MAN.read_text(encoding="utf-8"))
    ref = pd.read_csv(REF, dtype=str)
    out = {"sha256_csv": sha(REF), "sha256_manifesto_saida": man["saida"]["sha256"],
           "csv_igual_ao_manifesto": sha(REF) == man["saida"]["sha256"], "ufs": int(ref["cd_uf"].nunique()),
           "capitais": int(ref["capital_co_ibge_6d"].nunique())}
    # Região de cada UF pela REGIC 2018 (IBGE, arquivada): uma linha por município, com coduf e Grande Região.
    regic = pd.read_excel(REGIC, sheet_name=0, dtype={"coduf": str, "codmun": str})
    por_uf = regic.groupby("coduf")["Grande Região"].agg(lambda s: sorted(set(s)))
    reg_regic = {uf: v[0] for uf, v in por_uf.items() if len(v) == 1}
    out["regic_ufs_com_uma_regiao"] = len(reg_regic)
    out["regiao_igual_regic"] = int(sum(reg_regic.get(r.cd_uf) == r.nome_regiao for r in ref.itertuples()))
    # Capital: a REGIC tem o código de município da capital? Ela não marca capital; conferimos só que existe.
    out["capitais_existem_na_regic"] = int(ref["capital_co_ibge_7d"].isin(set(regic["codmun"].astype(str))).sum())
    # Região de cada UF pela coluna "Região" do quadro bruto do ciclo 2 (MS), em maiúsculas e sem acento.
    q = pd.read_excel(Q_C2_13FEV, header=None, skiprows=2, dtype=str)
    q = q[q[2].notna() & q[3].notna()]
    norm = {"NORTE": "Norte", "NORDESTE": "Nordeste", "SUDESTE": "Sudeste", "SUL": "Sul", "CENTRO-OESTE": "Centro-Oeste",
            "CENTRO OESTE": "Centro-Oeste"}
    q["cd_uf"] = q[3].str.strip().str[:2]
    q["reg"] = q[1].str.strip().str.upper().map(norm)
    pq = q.groupby("cd_uf")["reg"].agg(lambda s: sorted(set(s.dropna())))
    ufs_q = {uf: v[0] for uf, v in pq.items() if len(v) == 1}
    out["ufs_no_quadro_c2"] = len(ufs_q)
    out["regiao_igual_quadro_c2_nas_ufs_do_quadro"] = int(sum(ufs_q.get(r.cd_uf) == r.nome_regiao
                                                            for r in ref.itertuples() if r.cd_uf in ufs_q))
    # Primeiro dígito do código da UF (convenção do IBGE) — terceira conferência, só aritmética.
    dig = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}
    out["regiao_igual_primeiro_digito"] = int(sum(dig[r.cd_uf[0]] == r.nome_regiao for r in ref.itertuples()))
    return ref, out


# ---------------------------------------------------------------------------------------------------------------
# 2. Base de células e municípios × ciclo
# ---------------------------------------------------------------------------------------------------------------

def ler_quadro_c2_13fev() -> pd.DataFrame:
    """Leitor próprio: curso (2 dígitos do início), CNES e o 1º TOTAL (vagas imediatas) do cabeçalho de 2 linhas."""
    q = pd.read_excel(Q_C2_13FEV, header=None, dtype=str)
    cab0, cab1 = q.iloc[0].fillna(""), q.iloc[1].fillna("")
    i_imed = next(j for j in range(len(cab0)) if "IMEDIATAS" in cab0[j].upper())
    assert cab1[i_imed].strip().upper() == "TOTAL"
    i_cnes = next(j for j in range(len(cab1)) if cab1[j].strip().upper() == "CNES")
    d = q.iloc[2:].copy()
    d = d[d[0].notna() & d[i_cnes].notna()]
    d["curso"] = d[0].str.strip().str[:2]
    d["cnes"] = d[i_cnes].str.strip().str.zfill(7)
    d["vi"] = pd.to_numeric(d[i_imed], errors="raise")
    d["chave"] = d["cnes"] + "_" + d["curso"]
    return d.groupby("chave", as_index=False)["vi"].sum()


def montar(ref: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    c = pd.read_csv(CEL, dtype={"co_ibge": str, "chave": str})
    ivs = pd.read_csv(IVS, dtype={"co_ibge": str})
    ivs["co_ibge"] = ivs["co_ibge"].str[:6]
    c = c[["ciclo", "chave", "cod_curso", "co_ibge", "uf", "vagas_imediatas", "vagas_cr", "vagas_imediatas_pre",
           "n_alocados"]].copy()
    c["co_ibge"] = c["co_ibge"].str[:6]
    c = c.merge(ivs[["co_ibge", "ivs"]], on="co_ibge", how="left", validate="m:1")
    info = {"celulas": {int(k): int(v) for k, v in c.groupby("ciclo").size().items()},
            "celulas_sem_ivs": int(c["ivs"].isna().sum())}
    # Conferência do tipo de vaga do ciclo 2 contra o quadro bruto de 13/02/2026.
    q = ler_quadro_c2_13fev()
    c2 = c[c["ciclo"] == 2].merge(q, on="chave", how="left")
    info["c2_celulas_no_quadro_13fev"] = int(c2["vi"].notna().sum())
    info["c2_vi_pre_diferente_do_bruto_13fev"] = int((c2["vi"].fillna(-1) != c2["vagas_imediatas_pre"]).sum())
    caps = set(ref["capital_co_ibge_6d"])
    reg = ref.set_index("cd_uf")["nome_regiao"]
    sig = ref.set_index("cd_uf")["sigla_uf"]
    c["cd_uf"] = c["co_ibge"].str[:2]
    info["uf_do_quadro_diferente_do_codigo"] = int((c["uf"].str.upper() != c["cd_uf"].map(sig)).sum())
    c["capital"] = c["co_ibge"].isin(caps).astype(float)
    c["nordeste"] = (c["cd_uf"].map(reg) == "Nordeste").astype(float)
    c["norte"] = (c["cd_uf"].map(reg) == "Norte").astype(float)
    c["imed"] = (c["vagas_imediatas_pre"] > 0).astype(float)
    c["preench"] = (c["n_alocados"] >= 1).astype(float)
    c["aloc_imed"] = c["n_alocados"] * c["imed"]
    c["vic"] = c["vagas_imediatas"] + c["vagas_cr"]
    c["fe"] = c["ciclo"].astype(str) + "|" + c["cod_curso"].astype(str)
    c = c[c["ivs"].notna()].copy()
    c["s"] = np.round(c["ivs"] * 1000)
    m = c.groupby(["ciclo", "co_ibge"]).agg(s=("s", "first"), cd_uf=("cd_uf", "first"), capital=("capital", "first"),
                                            nordeste=("nordeste", "first"), norte=("norte", "first"),
                                            n_imed=("imed", "sum"), aloc_imed=("aloc_imed", "sum"),
                                            vi_pre=("vagas_imediatas_pre", "sum"), n_aloc=("n_alocados", "sum"),
                                            vic=("vic", "sum")).reset_index()
    m["taxa"] = m["n_aloc"] / m["vic"]
    info["municipios_ciclo"] = {int(k): int(v) for k, v in m.groupby("ciclo").size().items()}
    return c, m, info


# ---------------------------------------------------------------------------------------------------------------
# 3. Estimador próprio
# ---------------------------------------------------------------------------------------------------------------

def rd(d: pd.DataFrame, y: str, corte: int, *, fe: str | None = None, extra: list[np.ndarray] | None = None,
       peso: str | None = None, uf: bool = False) -> dict:
    x_mil = d["s"].to_numpy(float) - corte
    k = np.where(np.abs(x_mil) < H, 1 - np.abs(x_mil) / H, 0.0)
    w = k * (d[peso].to_numpy(float) if peso else 1.0)
    usa = w > 0
    d = d[usa]
    x, w = x_mil[usa] / 1000, w[usa]
    t = (x > 0).astype(float)
    cols = []
    for g in sorted(d["ciclo"].unique()):
        ig = (d["ciclo"] == g).to_numpy(float)
        cols += [ig, ig * x, ig * t * x]
    cols.append(t)
    i_t = len(cols) - 1
    if fe:
        for v in sorted(d[fe].unique())[1:]:
            cols.append((d[fe] == v).to_numpy(float))
    if uf:
        for v in sorted(d["cd_uf"].unique())[1:]:
            cols.append((d["cd_uf"] == v).to_numpy(float))
    for e in extra or []:
        cols.append(e[usa])
    X = np.column_stack(cols)
    # Descarta colunas colineares (depois das protegidas), uma a uma, por posto.
    keep = list(range(i_t + 1))
    for j in range(i_t + 1, X.shape[1]):
        cand = keep + [j]
        if np.linalg.matrix_rank(X[:, cand] * np.sqrt(w)[:, None]) == len(cand):
            keep = cand
    X = X[:, keep]
    yv = d[y].to_numpy(float)
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], yv * sw, rcond=None)
    e = yv - X @ beta
    bread = np.linalg.inv(X.T @ (X * w[:, None]))
    cl = d["co_ibge"].to_numpy()
    _, idx = np.unique(cl, return_inverse=True)
    G = idx.max() + 1
    S = np.zeros((G, X.shape[1]))
    np.add.at(S, idx, X * (w * e)[:, None])
    n, kk = X.shape
    V = bread @ (S.T @ S) @ bread * (G / (G - 1)) * ((n - 1) / (n - kk))
    tau, ep = float(beta[i_t]), float(math.sqrt(V[i_t, i_t]))
    z = tau / ep
    p = math.erfc(abs(z) / math.sqrt(2))
    ab = d.loc[x <= 0, "co_ibge"].nunique()
    ac = d.loc[x > 0, "co_ibge"].nunique()
    capd = d[d["capital"] == 1]
    return {"tau": tau, "ep": ep, "ic95_inf": tau - 1.959963984540054 * ep, "ic95_sup": tau + 1.959963984540054 * ep,
            "p_valor": p, "n_obs": int(n), "n_clusters": int(G), "n_abaixo": int(ab), "n_acima": int(ac),
            "capitais_abaixo": int(capd.loc[capd["s"] <= corte, "co_ibge"].nunique()),
            "capitais_acima": int(capd.loc[capd["s"] > corte, "co_ibge"].nunique()),
            "ufs_na_janela": int(d["cd_uf"].nunique()),
            "ufs_com_os_dois_lados": int(sum(1 for _, g in d.groupby("cd_uf") if (g["s"] <= corte).any()
                                             and (g["s"] > corte).any()))}


def bky(p: np.ndarray) -> np.ndarray:
    """q-valores aguçados de BKY (2006) pela grade de Anderson (2008), escritos de novo."""
    m = len(p)
    o = np.argsort(p, kind="stable")
    ps = p[o]
    r = np.arange(1, m + 1)
    q = np.ones(m)
    for kq in range(1000, 0, -1):
        qq = kq / 1000
        q1 = qq / (1 + qq)
        r1 = r[ps <= q1 * r / m].max() if (ps <= q1 * r / m).any() else 0
        if r1 == m:
            r2 = m
        else:
            q2 = q1 * m / (m - r1)
            r2 = r[ps <= q2 * r / m].max() if (ps <= q2 * r / m).any() else 0
        q[:r2] = qq
    out = np.empty(m)
    out[o] = q
    return out


# ---------------------------------------------------------------------------------------------------------------
# 4. Linhas
# ---------------------------------------------------------------------------------------------------------------

def linhas(c: pd.DataFrame, m: pd.DataFrame) -> pd.DataFrame:
    res = []
    h1c = c[c["imed"] == 1]
    h1m = m[m["n_imed"] > 0]
    for corte in (300, 400):
        cs = f"{corte / 1000:.3f}"
        for am, dc, dm in (("H1", h1c, h1m), ("quadro", c, m)):
            for un, d in (("municipio", dm), ("celula", dc)):
                for v in ("capital", "nordeste", "norte"):
                    res.append({"bloco": "C-1", "medida": v, "unidade_analise": un, "amostra": am, "corte": cs,
                                "ajuste": "sem_ajuste", **rd(d, v, corte)})
        for aj, bloco in (("sem_ajuste", "base"), ("capital", "C-2"), ("uf", "C-3"), ("sem_capitais", "C-4")):
            dc = h1c[h1c["capital"] == 0] if aj == "sem_capitais" else h1c
            dm = h1m[h1m["capital"] == 0] if aj == "sem_capitais" else h1m
            ex_c = [dc["capital"].to_numpy(float)] if aj == "capital" else []
            ex_m = [((dm["ciclo"] == g).to_numpy(float) * dm["vi_pre"].to_numpy(float)) for g in (1, 2, 3)]
            ex_m += [dm["capital"].to_numpy(float)] if aj == "capital" else []
            res.append({"bloco": bloco, "medida": "HI-1", "unidade_analise": "celula", "amostra": "H1", "corte": cs,
                        "ajuste": aj, **rd(dc, "preench", corte, fe="fe", extra=ex_c, uf=aj == "uf")})
            res.append({"bloco": bloco, "medida": "HI-2", "unidade_analise": "municipio", "amostra": "H1", "corte": cs,
                        "ajuste": aj, **rd(dm, "aloc_imed", corte, extra=ex_m, uf=aj == "uf")})
    # Uma linha do C-5: taxa por vaga oferecida (S-e), sem ajuste e com efeito fixo de UF, em 0,300.
    for aj in ("sem_ajuste", "uf"):
        res.append({"bloco": "C-5", "medida": "taxa", "unidade_analise": "municipio", "amostra": "quadro",
                    "corte": "0.300", "ajuste": aj, **rd(m, "taxa", 300, peso="vic", uf=aj == "uf")})
    est = pd.DataFrame(res)
    mb = est["bloco"].isin(["C-2", "C-3", "C-4"])
    est["q_bky"] = np.nan
    est.loc[mb, "q_bky"] = bky(est.loc[mb, "p_valor"].to_numpy(float))
    est["ic_contem_zero"] = (est["ic95_inf"] <= 0) & (est["ic95_sup"] >= 0)
    return est


def leitura(est: pd.DataFrame) -> dict:
    out = {}
    for cs in ("0.300", "0.400"):
        b1 = est[(est["bloco"] == "C-1") & (est["amostra"] == "H1") & (est["corte"] == cs)]
        c1 = bool((~b1["ic_contem_zero"]).any())
        a_levar = [md for md in ("HI-1", "HI-2")
                   if not bool(est[(est["bloco"] == "base") & (est["medida"] == md) & (est["corte"] == cs)]
                               ["ic_contem_zero"].iloc[0])]
        c2 = bool(a_levar) and all(bool(est[(est["bloco"] == b) & (est["medida"] == md) & (est["corte"] == cs)]
                                        ["ic_contem_zero"].iloc[0]) for md in a_levar for b in ("C-2", "C-3", "C-4"))
        out[cs] = {"c1": c1, "a_levar": a_levar, "c2": c2,
                   "leitura": "ANDA_JUNTO_COM_CAPITAIS_OU_REGIAO" if c1 and c2 else "RELATAR_COMO_ESTA"}
    return out


def comparar(est: pd.DataFrame) -> pd.DataFrame:
    hc = pd.read_csv(HC_EST, dtype={"corte": str})
    chave = ["bloco", "medida", "unidade_analise", "amostra", "corte", "ajuste"]
    x = est.merge(hc[chave + ["tau", "ep", "p_valor", "q_bky", "n_abaixo", "n_acima", "capitais_abaixo",
                              "capitais_acima"]], on=chave, how="left", suffixes=("", "_hc"), validate="1:1")
    for col in ("tau", "ep", "p_valor", "q_bky"):
        x[f"dif_{col}"] = (x[col] - x[f"{col}_hc"]).abs()
    for col in ("n_abaixo", "n_acima", "capitais_abaixo", "capitais_acima"):
        x[f"igual_{col}"] = x[col] == x[f"{col}_hc"]
    return x


def main() -> None:
    ref, conf_ref = conferir_referencia()
    c, m, info = montar(ref)
    est = linhas(c, m)
    cmp_ = comparar(est)
    hi = pd.read_csv(HI_EST, dtype={"corte": str, "h": str})
    hi = hi[(hi["ciclo"] == "1+2+3") & (hi["variante"] == "principal") & (hi["versao_quadro_c2"] == "13fev")
            & (hi["linha"].isin(["HI-1", "HI-2"]))]
    portao = []
    for r in hi.itertuples():
        a = est[(est["bloco"] == "base") & (est["medida"] == r.linha) & (est["corte"] == r.corte)].iloc[0]
        portao.append({"medida": r.linha, "corte": r.corte, "dif_tau": abs(a["tau"] - r.tau),
                       "dif_ep": abs(a["ep"] - r.ep), "p_holm_48b": r.p_holm})
    janela = []
    for corte in (300, 400):
        mm = m[((m["s"] - corte).abs() < H) & (m["capital"] == 1)].drop_duplicates("co_ibge")
        janela.append({"corte": corte, "abaixo": int((mm["s"] <= corte).sum()), "acima": int((mm["s"] > corte).sum()),
                       "a_menos_de_0010_abaixo": int(((mm["s"] - corte > -10) & (mm["s"] <= corte)).sum()),
                       "a_menos_de_0010_acima": int(((mm["s"] - corte < 10) & (mm["s"] > corte)).sum())})
    hc_res = json.loads(HC_RES.read_text(encoding="utf-8"))
    le = leitura(est)
    resumo = {
        "natureza_dos_dados": "EMPIRICO", "rotulo": ROTULO, "script": "scripts/auditoria_H1/a42_auditoria_capitais_uf.py",
        "referencia": conf_ref, "base": info, "capitais_na_janela": janela,
        "leitura_refeita": le, "leitura_gravada": {k: v["leitura"] for k, v in hc_res["leitura"].items()},
        "portao_HI": portao,
        "maior_diferenca_contra_HC": {col: float(cmp_[f"dif_{col}"].max()) for col in ("tau", "ep", "p_valor")},
        "maior_diferenca_q_bky": float(cmp_["dif_q_bky"].max()),
        "contagens_iguais": bool(cmp_[[c_ for c_ in cmp_.columns if c_.startswith("igual_")]].all().all()),
        "linhas_recalculadas": int(len(est)),
        "arquivo_ivs_errado_aberto": any(ARQUIVO_PROIBIDO in a for a in ABERTOS),
        "entradas": {str(p.relative_to(RAIZ)): sha(p) for p in (CEL, IVS, REF, REF_MAN, REGIC, Q_C2_13FEV, HC_EST, HI_EST)},
    }
    SAIDA.mkdir(parents=True, exist_ok=True)
    cmp_.insert(0, "natureza_dos_dados", "EMPIRICO")
    cmp_.insert(1, "rotulo", ROTULO)
    cmp_.to_csv(SAIDA / "a42_recalculo.csv", index=False)
    (SAIDA / "a42_resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2, default=float) + "\n",
                                           encoding="utf-8")
    pd.set_option("display.width", 250)
    print(json.dumps({k: resumo[k] for k in ("referencia", "base", "capitais_na_janela", "leitura_refeita",
                                             "leitura_gravada", "portao_HI", "maior_diferenca_contra_HC",
                                             "maior_diferenca_q_bky", "contagens_iguais", "arquivo_ivs_errado_aberto")},
                     ensure_ascii=False, indent=1, default=float))
    print(cmp_[["bloco", "medida", "unidade_analise", "amostra", "corte", "ajuste", "tau", "ep", "ic95_inf", "ic95_sup",
                "p_valor", "q_bky", "n_abaixo", "n_acima", "ufs_na_janela", "ufs_com_os_dois_lados", "dif_tau",
                "dif_ep"]].to_string())


if __name__ == "__main__":
    main()
