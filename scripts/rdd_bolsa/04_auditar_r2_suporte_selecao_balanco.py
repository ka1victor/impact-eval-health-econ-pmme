"""Portao R2 do RDD da bolsa: suporte, selecao na oferta, balanco e cointervencoes.

Este script **nao abre nenhum outcome**. Le a matriz municipal do R1 com o IVS
administrativo, covariaveis municipais anteriores ao programa, a composicao das
ofertas publicadas e a situacao do PMMB 2026. Nenhuma confirmacao, alocacao,
homologacao, presenca ou estoque posterior entra aqui.

O tratamento e o salto de R$ 5 mil no valor anunciado da bolsa:

    0,300 -> 0,301: R$ 10 mil para R$ 15 mil
    0,400 -> 0,401: R$ 15 mil para R$ 20 mil

Os cortes 0,200 e 0,500 mudam a categoria de IVS mas nao mudam a bolsa; entram
como placebos e calibram quantos desequilibrios aparecem por acaso. O IVS
administrativo tem tres casas decimais, entao janelas e bandas sao contadas em
pontos da grade: (c - h, c] a esquerda e (c, c + h] a direita.

O balanco e julgado por tres criterios, todos sem outcome:

1. randomizacao local, regra de Cattaneo, Titiunik e Vazquez-Bare (2016): a
   maior janela em que cada covariavel tem p >= 0,15, nela e nas menores;
2. randomizacao local com teste conjunto: permutacao do maximo |t| entre as
   covariaveis padronizadas, que respeita a correlacao entre elas;
3. continuidade local-linear (inclinacoes separadas, kernel triangular, HC1),
   com ajuste de Holm entre covariaveis. Covariavel ligada ao IVS tem inclinacao
   no running variable; so a especificacao local-linear separa inclinacao de salto.

O MDE e calculado pelo proprio desenho: a variancia do salto local-linear sob
variancia constante p(1 - p) depende so das posicoes no running variable, nao
do outcome.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm


ROOT = Path(__file__).resolve().parents[2]
MATRIZ = ROOT / "output" / "rdd_bolsa" / "matriz_municipio_ivs_administrativo.csv"
R1 = ROOT / "output" / "rdd_bolsa" / "a01c_regra_ivs_administrativo.json"
TIPOLOGIA = ROOT / "output" / "tema_trabalho" / "matriz_tipologia_territorial.parquet"
POPULACAO = ROOT / "output" / "aquisicao" / "populacao_censo2022_municipios.csv"
QUADRO = ROOT / "output" / "aquisicao" / "quadro_vagas_consolidado.parquet"
OUT_SUPORTE = ROOT / "output" / "rdd_bolsa" / "r2_suporte.csv"
OUT_TESTES = ROOT / "output" / "rdd_bolsa" / "r2_testes_continuidade.csv"
OUT_JSON = ROOT / "output" / "rdd_bolsa" / "r2_portao.json"

CORTES = {0.300: "tratamento", 0.400: "tratamento", 0.200: "placebo", 0.500: "placebo"}
SALTO_BOLSA = {0.300: 5_000, 0.400: 5_000, 0.200: 0, 0.500: 0}
JANELAS = (0.005, 0.010, 0.015, 0.020, 0.025, 0.030, 0.040, 0.050)
BANDAS_LL = (0.030, 0.050, 0.075, 0.100)
BANDA_REFERENCIA = 0.050
ONDAS = ("2025_c1_ch1", "2025_c1_ch2", "2026_c2_ch1", "2026_c2_ch2", "2026_c3_ch1")
VERSAO_CANONICA = {
    (1, 1): "original",
    (1, 2): "oficial",
    (2, 1): "retificada_final",
    (2, 2): "oficial",
    (3, 1): "retificada",
}
N_PERM = 5_000
SEMENTE = 20261005
LIMIAR_BALANCO = 0.15
ALFA = 0.05
MIN_MUNICIPIOS_LADO = 20
MIN_PONTOS_MASSA_LADO = 5
LINHAS_BASE_MDE = (0.2, 0.3, 0.4)
Z_ALFA, Z_PODER = 1.959964, 0.841621

COVARIAVEIS = {
    "ivs_2010": "IVS 2010 do Atlas",
    "ivs_infra_2010": "IVS infraestrutura urbana 2010",
    "ivs_ch_2010": "IVS capital humano 2010",
    "ivs_rt_2010": "IVS renda e trabalho 2010",
    "idhm_2010": "IDHM 2010",
    "log_rdpc_2010": "log da renda per capita 2010",
    "log_pop_2022": "log da populacao 2022",
    "capital": "capital estadual",
    "rm_ride_2022": "em RM ou RIDE (2022)",
    "interior_remoto": "interior remoto (tipologia A2)",
    "amazonia_legal": "Amazonia Legal",
    "faixa_fronteira": "faixa de fronteira",
    "norte_nordeste": "regiao Norte ou Nordeste",
}
COMPOSICAO = {
    "n_ondas_ofertado": "ondas em que o municipio foi ofertado",
    "n_celulas": "celulas CNES-curso ofertadas, soma das ondas",
    "n_vagas": "vagas publicadas (imediatas e reserva), soma das ondas",
    "n_cursos": "cursos distintos ofertados",
}
COINTERVENCAO = {
    "pmmb_elegivel": "municipio elegivel ao PMMB 2026 (eSF)",
    "pmmb_com_vagas": "municipio com vaga de eSF a confirmar no PMMB 2026",
    "pmmb_vagas_esf": "vagas de eSF no PMMB 2026",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def carregar() -> pd.DataFrame:
    matriz = pd.read_csv(MATRIZ, dtype={"co_ibge_6d": str}).set_index("co_ibge_6d")
    tipologia = pd.read_parquet(TIPOLOGIA).assign(co_ibge_6d=lambda f: f.co_ibge_6d.astype(str)).set_index("co_ibge_6d")
    populacao = pd.read_csv(POPULACAO, dtype={"co_ibge_6d": str}).set_index("co_ibge_6d")

    base = matriz.join(
        tipologia[["ivs_infra_2010", "ivs_ch_2010", "ivs_rt_2010", "idhm_2010", "rdpc_2010", "estrato", "flag_capital", "flag_rm_ride_2022"]]
    ).join(populacao[["populacao_2022"]])
    base["x"] = (base.ivs_adm * 1000).round().astype(int)
    base["log_rdpc_2010"] = np.log(base.rdpc_2010)
    base["log_pop_2022"] = np.log(pd.to_numeric(base.populacao_2022))
    base["capital"] = base.flag_capital.astype(float)
    base["rm_ride_2022"] = base.flag_rm_ride_2022.astype(float)
    base["interior_remoto"] = base.estrato.eq("interior_remoto").astype(float).where(base.estrato.notna())
    base["amazonia_legal"] = base.amazonia_legal.astype(float)
    base["faixa_fronteira"] = base.faixa_fronteira.astype(float)
    base["norte_nordeste"] = base.index.str[0].isin(["1", "2"]).astype(float)
    base["pmmb_elegivel"] = base.pmmb_situacao_esf.ne("NÃO ELEGIVEL").astype(float)
    base["pmmb_com_vagas"] = base.pmmb_vagas_esf.gt(0).astype(float)
    base["n_ondas_ofertado"] = base[[f"ofertado_{o}" for o in ONDAS]].sum(axis=1).astype(float)

    # Composicao da oferta publicada, so com linhas que trazem a faixa (as do
    # quadro de vagas); a lista de alocados da segunda chamada de 2025 fica de fora
    # porque so existe para vaga ja preenchida.
    quadro = pd.read_parquet(QUADRO)
    quadro = quadro[quadro.faixa_atracao_anunciada.isin(["FAIXA 1", "FAIXA 2", "FAIXA 3"])]
    quadro = quadro[quadro.tipo_documento.isin(["OFERTA_VAGAS", "OFERTA_E_ALOCADOS"])]
    canonica = quadro.apply(lambda r: VERSAO_CANONICA.get((r.ciclo, r.chamada)) == r.versao_edital, axis=1)
    quadro = quadro[canonica].assign(co_ibge_6d=lambda f: f.co_ibge_6d.astype(str).str[:6])
    composicao = quadro.groupby("co_ibge_6d").agg(
        n_celulas=("cod_curso", "size"),
        n_vagas=("qt_vagas_total", "sum"),
        n_cursos=("cod_curso", "nunique"),
    )
    return base.join(composicao.astype(float))


def janela(base: pd.DataFrame, corte: float, h: float) -> pd.DataFrame:
    c, w = round(corte * 1000), round(h * 1000)
    dentro = base[(base.x > c - w) & (base.x <= c + w)].copy()
    dentro["direita"] = dentro.x > c
    return dentro


def permutacoes(n: int, n_direita: int, rng: np.random.Generator) -> np.ndarray:
    rotulos = np.zeros(n, dtype=bool)
    rotulos[:n_direita] = True
    return rng.permuted(np.tile(rotulos, (N_PERM, 1)), axis=1)


def testar_lr(dados: pd.DataFrame, variavel: str, rng: np.random.Generator) -> dict:
    valido = dados[[variavel, "direita"]].dropna()
    y = valido[variavel].to_numpy(dtype=float)
    d = valido.direita.to_numpy()
    n_dir, n_esq = int(d.sum()), int((~d).sum())
    vazio = {"n_esq": n_esq, "n_dir": n_dir, "media_esq": np.nan, "media_dir": np.nan, "diferenca": np.nan, "erro_padrao": np.nan, "p": np.nan}
    if n_dir < 2 or n_esq < 2:
        return vazio
    observada = y[d].mean() - y[~d].mean()
    soma_dir = permutacoes(len(y), n_dir, rng).astype(float) @ y
    nulas = soma_dir / n_dir - (y.sum() - soma_dir) / n_esq
    p = (1 + np.sum(np.abs(nulas) >= abs(observada) - 1e-12)) / (1 + N_PERM)
    return {**vazio, "media_esq": float(y[~d].mean()), "media_dir": float(y[d].mean()), "diferenca": float(observada), "p": float(p)}


def teste_conjunto_lr(dados: pd.DataFrame, rng: np.random.Generator) -> float:
    """Permutacao do maximo |diferenca padronizada| entre covariaveis."""
    z = dados[list(COVARIAVEIS)].astype(float)
    z = z.fillna(z.mean())
    dp = z.std(ddof=0)
    z = z.loc[:, dp > 0]
    z = ((z - z.mean()) / dp[dp > 0]).to_numpy()
    d = dados.direita.to_numpy()
    n_dir, n_esq = int(d.sum()), int((~d).sum())

    def estatistica(rotulos: np.ndarray) -> np.ndarray:
        r = rotulos.astype(float)
        return np.abs(r @ z / n_dir - (1 - r) @ z / n_esq).max(axis=-1)

    observada = estatistica(d)
    nulas = estatistica(permutacoes(len(d), n_dir, rng))
    return float((1 + np.sum(nulas >= observada - 1e-12)) / (1 + N_PERM))


def desenho_ll(dados: pd.DataFrame, corte: float, h: float) -> tuple[pd.DataFrame, pd.Series]:
    xi = dados.x - round(corte * 1000)
    hi = round(h * 1000)
    dentro = xi.abs() < hi
    xi = xi[dentro]
    d = (xi > 0).astype(float)
    x = xi / 1000
    regressores = sm.add_constant(pd.DataFrame({"D": d, "x": x, "Dx": d * x}))
    return regressores, 1 - xi.abs() / hi


def testar_ll(dados: pd.DataFrame, variavel: str, corte: float, h: float) -> dict:
    regressores, pesos = desenho_ll(dados, corte, h)
    y = dados.loc[regressores.index, variavel].astype(float)
    valido = y.notna()
    regressores, pesos, y = regressores[valido], pesos[valido], y[valido]
    n_esq, n_dir = int((regressores.D == 0).sum()), int((regressores.D == 1).sum())
    if y.nunique() < 2 or n_esq < 5 or n_dir < 5:
        return {"n_esq": n_esq, "n_dir": n_dir, "media_esq": np.nan, "media_dir": np.nan, "diferenca": np.nan, "erro_padrao": np.nan, "p": np.nan}
    ajuste = sm.WLS(y, regressores, weights=pesos).fit(cov_type="HC1")
    return {
        "n_esq": n_esq,
        "n_dir": n_dir,
        "media_esq": np.nan,
        "media_dir": np.nan,
        "diferenca": float(ajuste.params["D"]),
        "erro_padrao": float(ajuste.bse["D"]),
        "p": float(ajuste.pvalues["D"]),
    }


def variancia_desenho_ll(dados: pd.DataFrame, corte: float, h: float) -> float:
    """Var(salto)/sigma^2 do estimador local-linear, sem outcome."""
    regressores, pesos = desenho_ll(dados, corte, h)
    x = regressores.to_numpy()
    w = pesos.to_numpy()
    pao = np.linalg.inv(x.T @ (w[:, None] * x))
    recheio = x.T @ ((w**2)[:, None] * x)
    return float((pao @ recheio @ pao)[1, 1])


def mde(variancia_por_sigma2: float, p: float) -> float:
    return float((Z_ALFA + Z_PODER) * np.sqrt(p * (1 - p) * variancia_por_sigma2))


def holm(ps: list[float]) -> float:
    ordenados = np.sort(np.asarray([p for p in ps if np.isfinite(p)]))
    m = len(ordenados)
    ajustados = np.maximum.accumulate(np.minimum(1, (m - np.arange(m)) * ordenados))
    return float(ajustados[0]) if m else np.nan


def main() -> None:
    r1 = json.loads(R1.read_text(encoding="utf-8"))
    if r1["decisao_r1"] != "APROVADO_SHARP":
        raise SystemExit("R2 bloqueado: o R1 com IVS administrativo nao esta aprovado.")
    base = carregar()
    ofertados = base[base.ofertado_alguma_onda]
    rng = np.random.default_rng(SEMENTE)

    suporte, testes, conjunto = [], [], []
    for corte, tipo in CORTES.items():
        for h in JANELAS:
            todos = janela(base, corte, h)
            of = todos[todos.ofertado_alguma_onda]
            linha = {"corte": corte, "tipo": tipo, "janela": h}
            for rotulo, recorte in [("alguma_onda", of)] + [(o, todos[todos[f"ofertado_{o}"]]) for o in ONDAS]:
                linha[f"n_esq_{rotulo}"] = int((~recorte.direita).sum())
                linha[f"n_dir_{rotulo}"] = int(recorte.direita.sum())
            linha["pontos_massa_esq"] = int(of.loc[~of.direita, "x"].nunique())
            linha["pontos_massa_dir"] = int(of.loc[of.direita, "x"].nunique())
            linha["universo_esq"] = int((~todos.direita).sum())
            linha["universo_dir"] = int(todos.direita.sum())
            suporte.append(linha)
            conjunto.append({"corte": corte, "janela": h, "p_conjunto": teste_conjunto_lr(of, rng)})

            blocos = (
                [("selecao", "todos", "ofertado_alguma_onda", todos)]
                + [("selecao", "todos", f"ofertado_{o}", todos) for o in ONDAS]
                + [("balanco", "ofertados", v, of) for v in COVARIAVEIS]
                + [("composicao", "ofertados", v, of) for v in COMPOSICAO]
                + [("cointervencao", "todos", v, todos) for v in COINTERVENCAO]
            )
            for grupo, populacao, variavel, dados in blocos:
                dados = dados.assign(**{variavel: dados[variavel].astype(float)})
                testes.append({"metodo": "randomizacao_local", "corte": corte, "tipo": tipo, "janela": h, "grupo": grupo, "populacao": populacao, "variavel": variavel, **testar_lr(dados, variavel, rng)})

        for h in BANDAS_LL:
            blocos = (
                [("selecao", "todos", "ofertado_alguma_onda", base)]
                + [("balanco", "ofertados", v, ofertados) for v in COVARIAVEIS]
                + [("composicao", "ofertados", v, ofertados) for v in COMPOSICAO]
                + [("cointervencao", "todos", v, base) for v in COINTERVENCAO]
            )
            for grupo, populacao, variavel, dados in blocos:
                testes.append({"metodo": "local_linear", "corte": corte, "tipo": tipo, "janela": h, "grupo": grupo, "populacao": populacao, "variavel": variavel, **testar_ll(dados, variavel, corte, h)})

    suporte = pd.DataFrame(suporte)
    testes = pd.DataFrame(testes)
    conjunto = pd.DataFrame(conjunto)
    OUT_SUPORTE.parent.mkdir(parents=True, exist_ok=True)
    suporte.to_csv(OUT_SUPORTE, index=False)
    testes.to_csv(OUT_TESTES, index=False, float_format="%.6g")

    def maior_janela_continua(passa: pd.Series) -> float | None:
        escolhida = None
        for h in JANELAS:
            if not passa.loc[h]:
                break
            escolhida = h
        return escolhida

    variancias = {}
    cortes = {}
    for corte, tipo in CORTES.items():
        lr = testes[(testes.metodo == "randomizacao_local") & (testes.corte == corte)]
        ll = testes[(testes.metodo == "local_linear") & (testes.corte == corte)]
        min_p_cov = lr[lr.grupo == "balanco"].groupby("janela").p.min()
        p_conj = conjunto[conjunto.corte == corte].set_index("janela").p_conjunto
        janela_estrita = maior_janela_continua(min_p_cov >= LIMIAR_BALANCO)
        janela_conjunta = maior_janela_continua(p_conj >= LIMIAR_BALANCO)
        sup_ref = suporte[(suporte.corte == corte) & (suporte.janela == BANDA_REFERENCIA)].iloc[0]

        ll_ref = ll[ll.janela == BANDA_REFERENCIA].set_index("variavel")
        holm_por_banda = {
            f"{h:.3f}": round(holm(ll[(ll.janela == h) & (ll.grupo == "balanco")].p.tolist()), 4)
            for h in BANDAS_LL
        }
        sinalizadas = sorted(ll_ref[(ll_ref.grupo == "balanco") & (ll_ref.p < ALFA)].index)
        variancias[corte] = {h: variancia_desenho_ll(ofertados, corte, h) for h in BANDAS_LL}
        bloco = {
            "tipo": tipo,
            "salto_da_bolsa_anunciada": SALTO_BOLSA[corte],
            "suporte_banda_referencia": {
                "banda": BANDA_REFERENCIA,
                "ofertados_esq": int(sup_ref.n_esq_alguma_onda),
                "ofertados_dir": int(sup_ref.n_dir_alguma_onda),
                "pontos_massa_esq": int(sup_ref.pontos_massa_esq),
                "pontos_massa_dir": int(sup_ref.pontos_massa_dir),
            },
            "randomizacao_local": {
                "min_p_por_covariavel": {f"{h:.3f}": round(float(p), 4) for h, p in min_p_cov.items()},
                "janela_regra_estrita": janela_estrita,
                "p_teste_conjunto": {f"{h:.3f}": round(float(p), 4) for h, p in p_conj.items()},
                "janela_teste_conjunto": janela_conjunta,
            },
            "local_linear": {
                "holm_min_p_covariaveis": holm_por_banda,
                "covariaveis_com_p_menor_que_5pct_na_banda_referencia": sinalizadas,
                "p_selecao_na_oferta": round(float(ll_ref.loc["ofertado_alguma_onda", "p"]), 4),
                "p_composicao": {v: round(float(ll_ref.loc[v, "p"]), 4) for v in COMPOSICAO},
                "p_cointervencao_pmmb": {v: round(float(ll_ref.loc[v, "p"]), 4) for v in COINTERVENCAO},
                "mde_proporcao_municipal_pp": {
                    f"{h:.3f}": {f"{p:.1f}": round(100 * mde(variancias[corte][h], p), 1) for p in LINHAS_BASE_MDE}
                    for h in BANDAS_LL
                },
            },
        }
        if tipo == "tratamento":
            criterios = {
                "suporte": bool(
                    sup_ref.n_esq_alguma_onda >= MIN_MUNICIPIOS_LADO
                    and sup_ref.n_dir_alguma_onda >= MIN_MUNICIPIOS_LADO
                    and sup_ref.pontos_massa_esq >= MIN_PONTOS_MASSA_LADO
                    and sup_ref.pontos_massa_dir >= MIN_PONTOS_MASSA_LADO
                ),
                "selecao_na_oferta": bool(ll_ref.loc["ofertado_alguma_onda", "p"] >= ALFA),
                "cointervencao_pmmb": bool(all(ll_ref.loc[v, "p"] >= ALFA for v in COINTERVENCAO)),
                "balanco_local_linear_holm": bool(holm_por_banda[f"{BANDA_REFERENCIA:.3f}"] >= ALFA),
                "composicao_da_oferta": bool(all(ll_ref.loc[v, "p"] >= ALFA for v in COMPOSICAO)),
                "randomizacao_local_viavel": bool(
                    janela_conjunta is not None
                    and suporte[(suporte.corte == corte) & (suporte.janela == janela_conjunta)].iloc[0][["n_esq_alguma_onda", "n_dir_alguma_onda"]].min() >= MIN_MUNICIPIOS_LADO
                ),
            }
            essenciais = ("suporte", "selecao_na_oferta", "cointervencao_pmmb", "balanco_local_linear_holm")
            bloco["criterios"] = criterios
            bloco["status"] = "VIAVEL_CONTINUIDADE" if all(criterios[k] for k in essenciais) else "REPROVADO"
        cortes[f"{corte:.3f}"] = bloco

    tratados = {k: v for k, v in cortes.items() if v["tipo"] == "tratamento"}
    viaveis = [k for k, v in tratados.items() if v["status"] == "VIAVEL_CONTINUIDADE"]
    # Os dois cortes tem a mesma dose (R$ 5 mil); a combinacao por inverso da
    # variancia e a referencia de potencia de uma estimativa conjunta.
    mde_conjunto = {
        f"{h:.3f}": {
            f"{p:.1f}": round(100 * mde(1 / sum(1 / variancias[float(k)][h] for k in viaveis), p), 1)
            for p in LINHAS_BASE_MDE
        }
        for h in BANDAS_LL
    } if viaveis else None
    ressalvas = []
    for k, v in tratados.items():
        if not v["criterios"]["randomizacao_local_viavel"]:
            ressalvas.append(f"{k}: randomizacao local so balanceia em janela com menos de {MIN_MUNICIPIOS_LADO} municipios por lado; nao serve de estimador principal")
        if not v["criterios"]["composicao_da_oferta"]:
            ressalvas.append(f"{k}: a composicao da oferta muda no corte; o efeito por celula pode carregar o numero de celulas")
        for cov in v["local_linear"]["covariaveis_com_p_menor_que_5pct_na_banda_referencia"]:
            ressalvas.append(f"{k}: {cov} com p < 0,05 isoladamente; ajustar ou estratificar no R3")
    placebos_sinalizados = {
        k: v["local_linear"]["covariaveis_com_p_menor_que_5pct_na_banda_referencia"]
        for k, v in cortes.items() if v["tipo"] == "placebo"
    }
    decisao = (
        "VIAVEL_CONTINUIDADE_COM_RESSALVAS" if len(viaveis) == len(tratados) and ressalvas
        else "VIAVEL_CONTINUIDADE" if len(viaveis) == len(tratados)
        else "VIAVEL_PARCIAL" if viaveis
        else "REPROVADO"
    )
    relatorio = {
        "portao": "R2",
        "data_execucao": date.today().isoformat(),
        "outcomes_abertos": False,
        "decisao_r2": decisao,
        "cortes_viaveis": viaveis,
        "primeiro_estagio": {
            "tipo": "sharp por construcao",
            "leitura": (
                "o valor anunciado salta exatamente R$ 5 mil em 0,300/0,301 e em "
                "0,400/0,401 para 100% dos municipios ofertados (R1: 4.103 de 4.103 "
                "municipio-onda-versao), e nao salta em 0,200 e 0,500"
            ),
            "estimando": "intencao de tratar da oferta anunciada; valor recebido nao e observado",
        },
        "regras_pre_especificadas": {
            "unidade": "municipio",
            "populacao_balanco_e_composicao": "municipios ofertados em ao menos uma onda de 2025 ou 2026",
            "populacao_selecao_e_cointervencao": "todos os municipios com IVS administrativo",
            "janelas_randomizacao_local": list(JANELAS),
            "bandas_local_linear": list(BANDAS_LL),
            "banda_referencia_do_portao": BANDA_REFERENCIA,
            "permutacoes": N_PERM,
            "semente": SEMENTE,
            "limiar_balanco_randomizacao_local": LIMIAR_BALANCO,
            "alfa": ALFA,
            "criterios_essenciais": ["suporte", "selecao_na_oferta", "cointervencao_pmmb", "balanco_local_linear_holm"],
            "suporte_minimo": {"municipios_por_lado": MIN_MUNICIPIOS_LADO, "pontos_de_massa_por_lado": MIN_PONTOS_MASSA_LADO},
            "mde": "proporcao municipal, alfa 5% bilateral, poder 80%, variancia p(1-p) com p hipotetico 0,2/0,3/0,4",
        },
        "covariaveis": COVARIAVEIS,
        "cortes": cortes,
        "placebos_covariaveis_sinalizadas": placebos_sinalizados,
        "mde_conjunto_dois_cortes_pp": mde_conjunto,
        "ressalvas": ressalvas,
        "limites": [
            "A regra estrita de randomizacao local, primeira a ser executada, reprova os dois cortes; o registro fica no artefato e o estimador principal passa a ser local-linear, decisao tomada sem outcome.",
            "Estoque previo de especialistas no CNES nao entrou no balanco: o bruto do CNES nao esta neste ambiente e precisa ser readquirido antes do R3.",
            "A safra do IVS administrativo nao e publicada; a regra e reproduzida, mas sua origem precisa ser documentada.",
            "Ser ofertado em 2026 e decisao posterior a 2025; a continuidade da probabilidade de oferta testa selecao, nao a exclui em outras margens.",
        ],
        "fontes": {
            str(p.relative_to(ROOT)).replace("\\", "/"): sha256(p)
            for p in (MATRIZ, R1, TIPOLOGIA, POPULACAO, QUADRO)
        },
        "o_que_nao_autoriza": "Nao abre outcomes. A estimacao (R4) depende de protocolo R3 congelado e autorizacao do autor.",
    }
    OUT_JSON.write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[R2] {decisao}: " + "; ".join(f"{k} {v.get('status', 'placebo')}" for k, v in cortes.items()))


if __name__ == "__main__":
    main()
