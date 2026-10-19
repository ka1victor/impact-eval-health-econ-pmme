"""E2 do protocolo congelado: limites parciais com escore administrativo ausente.

Executa a especificacao `E2_limites` de
`output/rdd_bolsa/protocolo_escore_administrativo.json` (congelado em
14/10/2026) sem altera-la: cortes, janelas, populacoes, outcome e cenarios sao
lidos do protocolo e conferidos contra as constantes deste script; qualquer
divergencia interrompe a execucao.

Estimando (por ciclo k, corte c, janela h):

    Delta(c,k,h) = P(D_k = 1 | s em (c, c+h]) - P(D_k = 1 | s em (c-h, c])

entre os municipios de P_k, com s = escore administrativo de IVS (a07).

Identificacao parcial. O escore so e publicado para municipios com especialista
ativo; todo municipio com D_k = 1 tem escore, e municipios sem escore tem
D_k = 0 e posicao desconhecida. A posicao possivel de cada municipio sem escore
e o intervalo da faixa anunciada (cenario `pior_caso`). O cenario `informado`
do protocolo, que estreitava esse intervalo com o arquivo de IVS errado, saiu
em 18/10/2026 (auditoria 19; ver CENARIO_RETIRADO). Em cada lado, um municipio sem escore esta
"certamente dentro" se todo o conjunto possivel cai na janela e "possivelmente
dentro" se o conjunto apenas cruza a janela.

Extremos de Delta. Os limites marginais sao Delta_min = P_sup_min - P_inf_max e
Delta_max = P_sup_max - P_inf_min. Um mesmo municipio que cruzasse as duas
janelas so poderia estar em uma delas; por isso os extremos sao recalculados
por enumeracao exata de todas as alocacoes admissiveis (contagens por grupo,
pois todos os municipios sem escore tem D = 0) e comparados aos marginais. A
faixa anunciada fixa o lado de cada corte (a regra de dois cortes reproduz 100%
das faixas no R1), de modo que nenhum municipio sem escore pode cruzar as duas
janelas do mesmo corte; a enumeracao confirma isso em cada especificacao.

A estimativa so com municipios com escore e reportada como
`delta_ingenuo_viesado`: condiciona na cobertura, que e funcao do desfecho, e
serve apenas de referencia.

Linguagem: exploratorio, limites parciais, descritivo. O contraste e o
incentivo marginal anunciado de R$ 5 mil (possivelmente pacote, se outra regra
mudar no mesmo corte); nao e efeito do PMM-E nem do Agora Tem Especialistas.
D_k e presenca de especialista do ciclo k na relacao nominal de 09/10/2026, nao
preenchimento de vaga nem retencao individual.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROTOCOLO = ROOT / "output" / "rdd_bolsa" / "protocolo_escore_administrativo.json"
ESCORE = ROOT / "output" / "aquisicao" / "a07_ivs_administrativo_municipio.csv"
ATIVOS_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "tb_profissionais_ativos_pmme_csv.zip"
ATIVOS_MEMBRO = "tb_profissionais_ativos_pmme.csv"
OUT_CSV = ROOT / "output" / "rdd_bolsa" / "E2_limites.csv"
OUT_JSON = ROOT / "output" / "rdd_bolsa" / "E2_limites_resumo.json"

DATA_EXECUCAO = "2026-10-14"

# Populacoes do protocolo: ciclo k -> (rotulo, quadros de vagas cuja uniao define P_k).
POPULACOES = {
    1: ("P1", [("c1_ch1", "data/raw/aquisicao/vagas/2025_ciclo1_chamada1_vagas.xlsx")]),
    2: ("P2", [
        ("c2_ch1", "data/raw/pmm_e/2026_ciclo2_chamada1_vagas_retificadas.xlsx"),
        ("c2_ch2", "data/raw/pmm_e/2026_ciclo2_chamada2_vagas.xlsx"),
    ]),
}
# Tudo em milesimos inteiros do escore (3 casas decimais) para evitar erro de ponto flutuante.
CORTES_MIL = (300, 400)
JANELAS_MIL = (50, 30, 80)  # 0,050 principal; 0,030 e 0,080 sensibilidade (ordem do protocolo)
INTERVALO_FAIXA_MIL = {"FAIXA 3": (0, 300), "FAIXA 2": (301, 400), "FAIXA 1": (401, 1000)}
# Desvio de 18/10/2026: o cenario `informado` do protocolo usava como banda o
# arquivo data/ivs_ipea_2010_municipios.csv, que e uma linha de subgrupo
# populacional e nao o IVS do municipio (auditorias 16 e 19). Por regra do autor,
# numeros desse arquivo nao entram em saida ativa: o cenario saiu do E2. As linhas
# antigas ficam so no historico do repositorio e na auditoria 19, como failure mode.
CENARIOS = ("pior_caso",)
CENARIO_RETIRADO = {
    "cenario": "informado",
    "data": "2026-10-18",
    "motivo": (
        "a banda [ivs_2010 + dmin, ivs_2010 + dmax] usava data/ivs_ipea_2010_municipios.csv, linha de subgrupo "
        "populacional e nao o IVS do municipio; numeros desse arquivo so valem como failure mode"
    ),
    "efeito_no_pior_caso": "nenhum: o pior caso nunca leu o arquivo",
    "registro": "docs/auditorias/19_reestimacao_base_oficial_failure_mode.md",
}

COLUNAS = [
    "ciclo", "corte", "h", "cenario",
    "n_conhecidos_inf", "n_conhecidos_sup", "nD_inf", "nD_sup",
    "n_sem_escore_certos_inf", "n_sem_escore_possiveis_inf",
    "n_sem_escore_certos_sup", "n_sem_escore_possiveis_sup",
    "p_inf_min", "p_inf_max", "p_sup_min", "p_sup_max",
    "delta_min", "delta_max", "delta_ingenuo_viesado",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(65536):
            h.update(bloco)
    return h.hexdigest()


def mil(x: float) -> int:
    v = round(float(x) * 1000)
    if abs(float(x) * 1000 - v) > 1e-6:
        raise ValueError(f"valor fora da grade de 0,001: {x}")
    return int(v)


def conferir_protocolo(p: dict) -> None:
    """Falha fechada se o protocolo divergir das constantes executadas aqui."""
    cortes = sorted(mil(float(c)) for c in p["running_variable"]["cortes"])
    assert tuple(cortes) == CORTES_MIL, cortes
    assert "s > c" in p["running_variable"]["lado"], "lado do corte mudou no protocolo"
    intervalos = {f: (mil(a), mil(b)) for f, (a, b) in p["running_variable"]["intervalos_por_faixa"].items()}
    assert intervalos == INTERVALO_FAIXA_MIL, intervalos
    janelas = tuple(mil(float(re.search(r"h = (\d,\d+)", j).group(1).replace(",", ".")))
                    for j in p["E2_limites"]["janelas"])
    assert janelas == JANELAS_MIL, janelas
    assert "principal" in p["E2_limites"]["janelas"][0]
    assert "ciclo == k" in p["outcome"]["D_k"].replace("`", "")
    for rot, quadros in POPULACOES.values():
        for _, caminho in quadros:
            nome = Path(caminho).name
            assert nome in p["populacoes"][rot], (rot, nome)


def ler_quadro(caminho: str) -> pd.DataFrame:
    """Faixa anunciada por municipio (mesma leitura do 04_portao_r1)."""
    bruto = pd.read_excel(ROOT / caminho, header=None)
    linha = next(
        i for i in range(10) if bruto.iloc[i].astype(str).str.upper().str.contains("FAIXA").any()
    )
    df = pd.read_excel(ROOT / caminho, header=linha)
    df.columns = [str(c).strip().upper() for c in df.columns]
    col_ibge = next(c for c in df.columns if c.startswith("IBGE"))
    col_faixa = next(c for c in df.columns if "FAIXA" in c)
    m = df[[col_ibge, col_faixa]].dropna()
    m.columns = ["co_ibge", "faixa_anunciada"]
    m["co_ibge"] = m["co_ibge"].astype(str).str.split(".").str[0].str[:6]
    m = m[m["co_ibge"].str.isnumeric()]
    m["faixa_anunciada"] = m["faixa_anunciada"].astype(str).str.strip().str.upper()
    return m.drop_duplicates()


def ler_ativos() -> pd.DataFrame:
    """Le apenas co_ibge e ciclo da relacao nominal de ativos (protocolo)."""
    with zipfile.ZipFile(ATIVOS_ZIP) as z, z.open(ATIVOS_MEMBRO) as f:
        d = pd.read_csv(f, sep=";", encoding="latin1", dtype=str, usecols=["co_ibge", "ciclo"])
    d["co_ibge"] = d["co_ibge"].str.strip()
    d["ciclo"] = d["ciclo"].str.strip()
    assert d["co_ibge"].str.fullmatch(r"\d{6}").all(), "co_ibge fora do formato de 6 digitos"
    assert set(d["ciclo"].dropna()) <= {"1", "2", "3"}, sorted(d["ciclo"].unique())
    assert d["ciclo"].notna().all(), "ciclo ausente em alguma linha"
    return d


def faixa_por_escore_mil(s: int) -> str:
    for f, (a, b) in INTERVALO_FAIXA_MIL.items():
        if a <= s <= b:
            return f
    raise ValueError(s)


def proporcao(nd: int, den: int) -> float:
    return nd / den if den > 0 else float("nan")


def limites_marginais(nd: int, k_fixo: int, n_poss: int) -> tuple[float, float]:
    """P minima (todos os possiveis dentro) e maxima (nenhum dentro) de um lado.

    Se a janela pudesse ficar vazia (k_fixo = 0), entao nd = 0 (D = 1 exige escore)
    e P = 0 em qualquer configuracao nao vazia; o maximo vira 0 se houver possiveis.
    """
    p_min = proporcao(nd, k_fixo + n_poss)
    if k_fixo > 0:
        p_max = nd / k_fixo
    else:
        assert nd == 0
        p_max = 0.0 if n_poss > 0 else float("nan")
    return p_min, p_max


def extremos_exatos(nd_l, k_l, nd_u, k_u, n_a, n_b, n_c, n_c_fora) -> tuple[float, float]:
    """Min e max de Delta sobre todas as alocacoes admissiveis.

    Grupos de municipios sem escore (todos com D = 0): A = possiveis so no lado
    inferior; B = possiveis so no superior; C = possiveis nos dois (exclusivos:
    cada um vai para L, U ou, se o conjunto nao couber em L uniao U, para fora).
    Configuracoes com janela vazia sao descartadas (P indefinida).
    """
    a = np.arange(n_a + 1)[:, None]
    b = np.arange(n_b + 1)[None, :]
    dmin, dmax = np.inf, -np.inf
    for cl in range(n_c + 1):
        for cu in range(n_c + 1 - cl):
            if n_c - cl - cu > n_c_fora:
                continue
            den_l = k_l + a + cl
            den_u = k_u + b + cu
            with np.errstate(divide="ignore", invalid="ignore"):
                delta = nd_u / den_u - nd_l / den_l
            ok = (den_l > 0) & (den_u > 0)
            if ok.any():
                dmin = min(dmin, float(delta[ok].min()))
                dmax = max(dmax, float(delta[ok].max()))
    if not np.isfinite(dmin):
        return float("nan"), float("nan")
    return dmin, dmax


def limites_janela(s: np.ndarray, dk: np.ndarray, lo: np.ndarray, hi: np.ndarray, c: int, h: int) -> dict:
    """Limites de Delta numa especificacao (corte c, janela h, em milesimos).

    `s` e `dk`: escore e D_k dos municipios com escore. `lo` e `hi`: conjunto
    possivel do escore de cada municipio sem escore (todos com D_k = 0).
    Devolve as colunas de COLUNAS a partir de `n_conhecidos_inf` e a comparacao
    entre os extremos marginais e os exatos.
    """
    l0, l1 = c - h + 1, c      # (c-h, c]
    u0, u1 = c + 1, c + h      # (c, c+h]
    in_l = (s >= l0) & (s <= l1)
    in_u = (s >= u0) & (s <= u1)
    n_kl, n_ku = int(in_l.sum()), int(in_u.sum())
    nd_l, nd_u = int(dk[in_l].sum()), int(dk[in_u].sum())

    cert_l = (lo >= l0) & (hi <= l1)
    cert_u = (lo >= u0) & (hi <= u1)
    cruza_l = (lo <= l1) & (hi >= l0)
    cruza_u = (lo <= u1) & (hi >= u0)
    poss_l = cruza_l & ~cert_l
    poss_u = cruza_u & ~cert_u
    assert not (cert_l & cruza_u).any() and not (cert_u & cruza_l).any()
    grupo_c = poss_l & poss_u
    grupo_a = poss_l & ~poss_u
    grupo_b = poss_u & ~poss_l
    # C pode ficar fora das duas janelas se o conjunto nao couber em [l0, u1].
    c_fora = grupo_c & ~((lo >= l0) & (hi <= u1))

    k_l = n_kl + int(cert_l.sum())
    k_u = n_ku + int(cert_u.sum())
    np_l, np_u = int(poss_l.sum()), int(poss_u.sum())
    p_inf_min, p_inf_max = limites_marginais(nd_l, k_l, np_l)
    p_sup_min, p_sup_max = limites_marginais(nd_u, k_u, np_u)
    dmin_marg = p_sup_min - p_inf_max
    dmax_marg = p_sup_max - p_inf_min
    dmin_ex, dmax_ex = extremos_exatos(
        nd_l, k_l, nd_u, k_u,
        int(grupo_a.sum()), int(grupo_b.sum()), int(grupo_c.sum()), int(c_fora.sum()),
    )
    restringe = not (np.isclose(dmin_ex, dmin_marg, rtol=0, atol=1e-12, equal_nan=True)
                     and np.isclose(dmax_ex, dmax_marg, rtol=0, atol=1e-12, equal_nan=True))
    return {
        "n_conhecidos_inf": n_kl, "n_conhecidos_sup": n_ku,
        "nD_inf": nd_l, "nD_sup": nd_u,
        "n_sem_escore_certos_inf": int(cert_l.sum()), "n_sem_escore_possiveis_inf": np_l,
        "n_sem_escore_certos_sup": int(cert_u.sum()), "n_sem_escore_possiveis_sup": np_u,
        "p_inf_min": p_inf_min, "p_inf_max": p_inf_max,
        "p_sup_min": p_sup_min, "p_sup_max": p_sup_max,
        "delta_min": dmin_ex, "delta_max": dmax_ex,
        "delta_ingenuo_viesado": proporcao(nd_u, n_ku) - proporcao(nd_l, n_kl),
        "n_sem_escore_cruzam_ambas_janelas": int(grupo_c.sum()),
        "delta_min_marginal": dmin_marg,
        "delta_max_marginal": dmax_marg,
        "exclusividade_restringe_extremos": bool(restringe),
    }


def montar_populacao(k: int, escore: pd.DataFrame, ativos: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rotulo, quadros = POPULACOES[k]
    q = pd.concat([ler_quadro(c) for _, c in quadros], ignore_index=True).drop_duplicates()
    conflitos = int((q.groupby("co_ibge")["faixa_anunciada"].nunique() > 1).sum())
    assert conflitos == 0, f"{rotulo}: {conflitos} municipios com mais de uma faixa anunciada"
    q = q.drop_duplicates("co_ibge")
    assert q["faixa_anunciada"].isin(list(INTERVALO_FAIXA_MIL)).all(), q["faixa_anunciada"].unique()

    d_k = set(ativos.loc[ativos["ciclo"] == str(k), "co_ibge"])
    q = q.merge(escore[["co_ibge", "s_mil"]], on="co_ibge", how="left")
    q["tem_escore"] = q["s_mil"].notna()
    q["D"] = q["co_ibge"].isin(d_k).astype(int)

    # Propriedades do protocolo: D_k = 1 implica escore; escore reproduz a faixa anunciada.
    assert not ((q["D"] == 1) & ~q["tem_escore"]).any(), "municipio com D_k = 1 sem escore"
    com = q[q["tem_escore"]]
    assert (com["s_mil"].astype(int).map(faixa_por_escore_mil) == com["faixa_anunciada"]).all(), \
        "escore nao reproduz a faixa anunciada"

    q["faixa_lo"] = q["faixa_anunciada"].map(lambda f: INTERVALO_FAIXA_MIL[f][0])
    q["faixa_hi"] = q["faixa_anunciada"].map(lambda f: INTERVALO_FAIXA_MIL[f][1])
    meta = {
        "rotulo": rotulo,
        "quadros": [c for _, c in quadros],
        "municipios": int(len(q)),
        "com_escore": int(q["tem_escore"].sum()),
        "sem_escore": int((~q["tem_escore"]).sum()),
        "com_D_igual_1": int(q["D"].sum()),
        "por_faixa_anunciada": {
            f: {"municipios": int(len(g)), "com_escore": int(g["tem_escore"].sum()), "com_D_igual_1": int(g["D"].sum())}
            for f, g in q.groupby("faixa_anunciada")
        },
    }
    return q, meta


def conjuntos_possiveis(sem: pd.DataFrame, cenario: str) -> tuple[np.ndarray, np.ndarray, int]:
    """Conjunto possivel do escore de cada municipio sem escore: o intervalo da faixa."""
    if cenario != "pior_caso":
        raise ValueError(f"cenario {cenario!r} fora do E2 (o `informado` saiu em 18/10/2026; auditoria 19)")
    lo = sem["faixa_lo"].to_numpy(dtype=int)
    hi = sem["faixa_hi"].to_numpy(dtype=int)
    return lo, hi, 0


def main() -> None:
    protocolo = json.loads(PROTOCOLO.read_text(encoding="utf-8"))
    conferir_protocolo(protocolo)

    escore = pd.read_csv(ESCORE, dtype={"co_ibge": str})
    assert escore["co_ibge"].is_unique
    escore["s_mil"] = escore["ivs_admin"].map(mil)
    ativos = ler_ativos()

    # A relacao nominal e a fonte do escore: mesmos municipios.
    assert set(ativos["co_ibge"]) == set(escore["co_ibge"]), "municipios da relacao nominal != a07"
    assert len(escore) == 404, len(escore)

    linhas, detalhes, populacoes = [], [], {}
    for k in sorted(POPULACOES):
        q, meta = montar_populacao(k, escore, ativos)
        populacoes[f"ciclo_{k}"] = meta
        com = q[q["tem_escore"]]
        sem = q[~q["tem_escore"]]
        s = com["s_mil"].to_numpy(dtype=int)
        dk = com["D"].to_numpy(dtype=int)
        assert (sem["D"] == 0).all()

        conjuntos = {cen: conjuntos_possiveis(sem, cen) for cen in CENARIOS}
        meta["largura_media_conjunto_possivel_milesimos"] = {
            cen: round(float((hi_c - lo_c + 1).mean()), 1) if len(lo_c) else None
            for cen, (lo_c, hi_c, _) in conjuntos.items()
        }
        for c in CORTES_MIL:
            for h in JANELAS_MIL:
                for cenario in CENARIOS:
                    lo, hi, _ = conjuntos[cenario]
                    r = limites_janela(s, dk, lo, hi, c, h)
                    espec = {"ciclo": k, "corte": f"{c / 1000:.3f}", "h": f"{h / 1000:.3f}", "cenario": cenario}
                    linhas.append({**espec, **{col: r[col] for col in COLUNAS[4:]}})
                    detalhes.append({
                        **espec,
                        "n_sem_escore_cruzam_ambas_janelas": r["n_sem_escore_cruzam_ambas_janelas"],
                        "delta_min_marginal": round(r["delta_min_marginal"], 6),
                        "delta_max_marginal": round(r["delta_max_marginal"], 6),
                        "exclusividade_restringe_extremos": r["exclusividade_restringe_extremos"],
                    })

    # Ordem das linhas: ciclo, corte, janela na ordem do protocolo (principal primeiro), cenario.
    tabela = pd.DataFrame(linhas, columns=COLUNAS)
    for col in ["p_inf_min", "p_inf_max", "p_sup_min", "p_sup_max", "delta_min", "delta_max", "delta_ingenuo_viesado"]:
        tabela[col] = tabela[col].round(6)
    tabela.to_csv(OUT_CSV, index=False, float_format="%.6f")

    algum_restringe = any(d["exclusividade_restringe_extremos"] for d in detalhes)
    fontes = {
        str(PROTOCOLO.relative_to(ROOT)): sha256(PROTOCOLO),
        str(ESCORE.relative_to(ROOT)): sha256(ESCORE),
        str(ATIVOS_ZIP.relative_to(ROOT)): sha256(ATIVOS_ZIP),
    }
    for _, quadros in POPULACOES.values():
        for _, caminho in quadros:
            fontes[caminho] = sha256(ROOT / caminho)

    resumo = {
        "status": "ESTIMACAO_EXPLORATORIA_E2",
        "natureza_dos_dados": "EMPIRICO",
        "desvio_do_protocolo": CENARIO_RETIRADO,
        "data_execucao": DATA_EXECUCAO,
        "script": str(Path(__file__).resolve().relative_to(ROOT)),
        "protocolo": {
            "arquivo": str(PROTOCOLO.relative_to(ROOT)),
            "sha256": sha256(PROTOCOLO),
            "data_congelamento": protocolo["data_congelamento"],
            "secao": "E2_limites",
            "estimando": protocolo["E2_limites"]["estimando"],
            "conferido_contra_constantes_do_script": True,
            "alterado": False,
        },
        "saida": str(OUT_CSV.relative_to(ROOT)),
        "linguagem": (
            "Exploratorio e descritivo: limites parciais de uma diferenca de proporcoes nas janelas "
            "adjacentes aos cortes, sob ausencia do escore para municipios sem especialista ativo. Nao e "
            "efeito causal estabelecido. O contraste e o incentivo marginal anunciado de R$ 5 mil "
            "(possivelmente pacote se outra regra mudar no mesmo corte), nao o efeito do PMM-E nem do "
            "Agora Tem Especialistas. D_k e presenca de especialista do ciclo k na relacao nominal de "
            "09/10/2026, nao preenchimento de vaga nem retencao individual."
        ),
        "outcome": {
            "D_k": "1 se ha ao menos um especialista ativo com ciclo == k no municipio (relacao nominal 09/10/2026)",
            "colunas_lidas_da_relacao_nominal": ["co_ibge", "ciclo"],
            "valores_de_ciclo_linhas": {c: int(n) for c, n in ativos["ciclo"].value_counts().sort_index().items()},
            "municipios_na_relacao_nominal": int(ativos["co_ibge"].nunique()),
            "municipios_por_ciclo": {c: int(g["co_ibge"].nunique()) for c, g in ativos.groupby("ciclo")},
        },
        "running_variable": {
            "fonte": str(ESCORE.relative_to(ROOT)) + ", coluna ivs_admin",
            "unidade_interna": "milesimos inteiros",
            "cortes": [c / 1000 for c in CORTES_MIL],
            "janela_inferior": "(c - h, c]",
            "janela_superior": "(c, c + h]",
            "intervalos_por_faixa": {f: [a / 1000, b / 1000] for f, (a, b) in INTERVALO_FAIXA_MIL.items()},
        },
        "cenarios": {
            "pior_caso": "municipio sem escore em qualquer ponto do intervalo da faixa anunciada",
            "informado": "retirado em 18/10/2026 (ver desvio_do_protocolo)",
        },
        "metodo_extremos": {
            "marginal": "p_lado_min = nD/(conhecidos + certos + possiveis); p_lado_max = nD/(conhecidos + certos); "
                        "com conhecidos + certos = 0, nD = 0 e p_lado_max = 0 se houver possiveis; janela "
                        "necessariamente vazia -> NaN",
            "exato": "delta_min/delta_max do CSV vem de enumeracao de todas as alocacoes admissiveis dos "
                     "municipios sem escore (exclusividade entre janelas respeitada; janelas vazias descartadas)",
            "exclusividade_restringe_algum_extremo": algum_restringe,
            "por_que": (
                "todo conjunto possivel esta contido no intervalo de uma unica faixa e cada corte separa faixas "
                "adjacentes; logo nenhum municipio sem escore pode cruzar as duas janelas do mesmo corte e os "
                "extremos marginais sao atingiveis. A enumeracao confirma em todas as especificacoes."
            ),
            "detalhe_por_especificacao": detalhes,
        },
        "referencia_viesada": (
            "delta_ingenuo_viesado usa so municipios com escore; a cobertura do escore e funcao do desfecho "
            "(selecao), entao serve apenas de referencia e nao de estimativa"
        ),
        "populacoes": populacoes,
        "fontes_sha256": fontes,
        "regra_de_relato": protocolo["regra_de_relato"],
    }
    OUT_JSON.write_text(json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with pd.option_context("display.width", 250, "display.max_columns", 30):
        print(tabela.to_string(index=False))
    print(json.dumps({"exclusividade_restringe_algum_extremo": algum_restringe,
                      "populacoes": populacoes}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
