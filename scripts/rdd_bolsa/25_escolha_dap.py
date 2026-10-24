"""P1 (protocolo 52): quanto a remuneração anunciada move a escolha de onde trabalhar (T1.1–T1.5).

Protocolo congelado: `docs/06_execucao/52_protocolo_P1_escolha_dap.md` (19/10/2026, antes de estimar), com
estatuto `PROTOCOLO_52_POS_RESULTADO` (o E9 e a X4/X5 já tinham sido vistos). Plano: doc 51, §3 (P1). Portão
de viabilidade: `docs/auditorias/G1_viabilidade_candidatos.md`. Os cenários do T1.6 NÃO são rodados aqui.

Estimando
---------
P1a: coeficiente da bolsa anunciada (por R$ 1 mil/mês) na utilidade da 1ª opção do candidato, entre as
células (estabelecimento × curso) do seu curso e ciclo no quadro da 1ª chamada, ciclos 1–3 empilhados, com
distância origem–vaga e atributos de origem. A bolsa é identificada pelos degraus em 0,300 e 0,400, porque o
IVS 2010 oficial entra como spline contínuo (nós nos cortes, sem salto de nível), como no E9 §15. O contraste
mede o pacote do corte (bolsa +R$ 5 mil e outras regras federais nos mesmos cortes, auditoria 18) e o
incentivo marginal da bolsa, não a participação no PMM-E. É uma escolha DENTRO do conjunto de vagas abertas e
condicional a candidatar-se: não diz nada sobre quem não se candidatou.

Especificações (protocolo §3), todas relatadas
---------------------------------------------
Logit condicional, bolsa linear em R$ mil, spline linear do IVS com nós em 0,300 e 0,400, EP sanduíche com
cluster por conjunto de escolha (curso × ciclo; principal), mais EP de máxima verossimilhança e por candidato.
- M0: E9 principal na amostra G1 (sem distância).
- M1 (principal de P1a–P1c): M0 + distância/100 km + mesma UF + mesma região de saúde + mesmo município de
  origem + log da população (já no E9) + capital + vaga imediata (já no E9).
- M2: M1 com log(1 + distância em km) no lugar da distância linear.
- M3: M1 com a distância da origem mais próxima (ver "Faltantes").
- M4: M1 com efeito fixo de UF da vaga.
- M5: M1 por ciclo; Wald da igualdade do coeficiente da bolsa entre ciclos.
- M6: M1 + bolsa × tercil da nota no ciclo; M1 + bolsa × origem no município; M1 + bolsa × curso (cursos com
  ≥ 100 candidatos de 1ª opção; demais juntos). Um modelo por dimensão, como na X4.
- M7: logit explodido (1ª e 2ª opção) com M1.
- M8: logit misto, coeficientes normais na bolsa e na distância, 500 sorteios Halton embaralhados (semente
  20261019), demais coeficientes fixos; máxima verossimilhança simulada com gradiente analítico.
- M9: logit aninhado, ninhos = região de saúde (CIR) da célula dentro do conjunto do candidato, um lambda
  comum (como a X5), com M1; máxima verossimilhança com gradiente analítico.
DAP (P1b, P1c) = razão de coeficientes, em R$ mil por mês, IC pelo método delta e por bootstrap de conjuntos
de escolha (999 réplicas, semente fixa). P1g: ponte P1 → P2 (salto previsto por M1 em candidatos de 1ª opção
por célula, mudando só a bolsa, contra a RDD por célula com efeito fixo de curso × ciclo e cluster por
município, convenção do A3). Holm só em P1a; BKY nas secundárias com p-valor (P1d, P1e, P1f).

Amostra
-------
Candidatos com município de origem ligado no G1 (regra principal `g1_cpf_nome`, vínculo médico na competência
de referência). Os candidatos sem origem ficam fora com o motivo (seleção pela ligação, ameaça declarada).
A região de saúde vem da tabela oficial do TabNet (a mesma da X5); célula ou origem em município sem região
oficial fica fora (contada), sem imputação, como na X5. A distância é o círculo máximo entre os centroides do
IBGE do município de origem principal e do município da célula (mesma função e mesmos centroides do G1;
conferida contra `G1_distancias_opcoes.parquet` nas células escolhidas). O E9 é reestimado na amostra completa
dele (sensibilidade) e o script para se não reproduzir `E9_estimativas.csv`.

Faltantes
---------
M3 (distância da origem mais próxima) precisa do conjunto completo de municípios de origem de cada candidato.
O G1 guardou só a origem principal e a distância mais próxima das células ranqueadas; o cache com os vínculos
(`output/rdd_bolsa/G1_cache/` e `X1_cache/`, fora do Git) não está neste checkout. M3 fica `NAO_EXECUTADO`, com
o motivo; nada é aproximado.

Integridade
-----------
Só lê `output/` e, sem alterar, a tabela de CIR e os centroides do IBGE em `data/raw/aquisicao/territorio/`.
O IVS 2010 oficial vem do a08 (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`) pela mesma função do E9;
o arquivo local de IVS da auditoria 16 não é lido. Nenhum mês do CNES é lido. Nada é simulado, imputado ou
digitado como observação; toda saída leva `natureza_dos_dados = EMPIRICO`; sem nome nem CPF em `output/` (o
candidato é o pseudônimo `id_candidato`, que não é gravado).

Uso
---
    python3 scripts/rdd_bolsa/25_escolha_dap.py
    python3 scripts/rdd_bolsa/25_escolha_dap.py --atualizar-doc   # só regrava o doc 57a a partir das saídas
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
from typing import Any

import numpy as np
import pandas as pd
from scipy import optimize, stats

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


E9 = _importar(DIR_RDD / "16_estimar_E9_escolha.py", "e9_escolha_para_p1")
X45 = _importar(DIR_RDD / "19_escolha_heterogeneidade.py", "x4x5_escolha_para_p1")
X1 = _importar(DIR_RDD / "17_ponte_pmme_cnes.py", "x1_ponte_para_p1")
L = _importar(DIR_RDD / "rdd_lib.py", "rdd_lib_para_p1")

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------

PROTOCOLO_MD = ROOT / "docs" / "06_execucao" / "52_protocolo_P1_escolha_dap.md"
DOC = ROOT / "docs" / "06_execucao" / "57a_resultados_P1_escolha.md"
OUT = ROOT / "output" / "rdd_bolsa"
G1_ORIGEM = OUT / "G1_candidatos_origem.parquet"
G1_DIST = OUT / "G1_distancias_opcoes.parquet"
G1_RESUMO = OUT / "G1_resumo.json"
E9_ESTIMATIVAS = OUT / "E9_estimativas.csv"
V_CELULA = OUT / "outcomes" / "outcomes_V_celula.parquet"
NA_ESTIMATIVAS = OUT / "NA_estimativas.csv"
OUT_EST = OUT / "P1_estimativas.csv"
OUT_DAP = OUT / "P1_dap.csv"
OUT_RESUMO = OUT / "P1_resumo.json"
DIR_FIG = OUT / "P1_figuras"
FIG_DAP = DIR_FIG / "P1_dap.png"
FIG_CICLO = DIR_FIG / "P1_beta_por_ciclo.png"
FIG_PONTE = DIR_FIG / "P1_ponte_P1g.png"

# ---------------------------------------------------------------------------
# Parâmetros (protocolo 52 e parametrização; nenhum é dado)
# ---------------------------------------------------------------------------

DATA_EXECUCAO = "2026-10-23"
NATUREZA = "EMPIRICO"
ESTATUTO = "PROTOCOLO_52_POS_RESULTADO"
REGRA_G1 = "g1_cpf_nome"
CICLOS = (1, 2, 3)
EMPILHADO = "empilhado"
ESCALA_DIST_KM = 100.0          # distância por 100 km (P1b)
PASSO_BOLSA = 5.0               # um degrau de faixa = +R$ 5 mil
N_BOOT = 999                    # §3: bootstrap por conjunto de escolha
SEMENTE_BOOT = 20261019
N_HALTON = 500                  # §3, M8
SEMENTE_HALTON = 20261019
MAX_AVAL_M8 = 300               # teto determinístico de avaliações da verossimilhança do M8 (≈ 30 min; ver resumo)
MAX_AVAL_M9 = 400
POLIMENTO_NEWTON = 6            # passos de Newton depois do L-BFGS-B (M8, M9), como na X5
TOL_GRAD_POLIMENTO = 1e-4       # gradiente máximo da log-verossimilhança para declarar convergência
N_THREADS_M8 = 4                # conjuntos em paralelo no M8 (não muda o resultado)
LAMBDA_LIMITES = X45.LAMBDA_LIMITES
MIN_CAND_CURSO = 100            # §3, M6
H_RDD = L.H_PRINCIPAL_MIL       # 50 = 0,050 (convenção do A3)
CORTES = L.CORTES_MIL
ESTRATO_BASE_M1 = "interior_proximo_polo"   # base do estrato em M1, para que 'capital' seja um termo próprio
TOL_DEC = 1e-14
TOL_PASSO = 1e-10
MAX_ITER = 200
Z95 = float(stats.norm.ppf(0.975))

TERMO_BOLSA = "bolsa_mil"
TERMO_DIST = "distancia_100km"
TERMO_LOGDIST = "log1p_distancia_km"
TERMOS_ORIGEM = ["mesma_uf", "mesma_regiao_saude", "mesmo_municipio"]

ROTULO_MODELO = {
    "E9_amostra_completa": "E9 principal reestimado na amostra completa do E9 (sensibilidade da seleção pela ligação)",
    "M0": "E9 principal na amostra G1, sem distância",
    "M1": "M0 + distância/100 km + mesma UF + mesma região de saúde + mesmo município + capital (principal)",
    "M2": "M1 com log(1 + distância em km)",
    "M3": "M1 com distância da origem mais próxima",
    "M4": "M1 com efeito fixo de UF da vaga (no lugar da macrorregião)",
    "M5": "M1 por ciclo",
    "M6_nota": "M1 + bolsa × tercil da nota no ciclo",
    "M6_municipio": "M1 + bolsa × origem no próprio município",
    "M6_curso": "M1 + bolsa × curso (≥ 100 candidatos de 1ª opção; demais juntos)",
    "M7": "logit explodido (1ª e 2ª opção) com M1",
    "M8": "logit misto (bolsa e distância normais; 500 sorteios Halton)",
    "M9": "logit aninhado por região de saúde (CIR) dentro do conjunto, com M1",
}

MOTIVO_M3 = ("a distância da origem mais próxima exige o conjunto completo de municípios de origem de cada "
             "candidato; o G1 gravou só a origem principal e a distância mais próxima das células ranqueadas "
             "(G1_distancias_opcoes.parquet), não das demais células do conjunto de escolha; o cache dos vínculos "
             "(output/rdd_bolsa/G1_cache/ e X1_cache/, fora do Git) não está neste checkout; refazê-lo exige baixar "
             "de novo a tbDadosProfissionalSus e os vínculos do CNES; nada é aproximado")

COMO_LER = {
    "P1_dap.png": ("Cada ponto é quanto de bolsa mensal (em R$ mil) equivale a um atributo da vaga no modelo "
                   "principal; a barra mais grossa é o intervalo pelo método delta e a mais fina, o do bootstrap. "
                   "Ponto à direita do zero: o atributo vale como bolsa a mais. Intervalo que cruza o zero ou é muito "
                   "largo não permite ler o ponto como preço."),
    "P1_beta_por_ciclo.png": ("Cada ponto é o peso da bolsa (por R$ 1 mil) na escolha, em cada ciclo e nos três "
                              "juntos, com intervalo de 95%. Ponto acima do zero: vagas com bolsa maior foram "
                              "mais escolhidas como 1ª opção."),
    "P1_ponte_P1g.png": ("Cada par compara, no corte, quantos candidatos de 1ª opção a mais por célula o "
                         "modelo de escolha prevê (só mudando a bolsa) com o salto observado nos dados. É leitura de "
                         "consistência, não teste: sinais opostos com intervalos que se sobrepõem não mostram que o "
                         "modelo acerta nem que erra."),
}


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

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


def _juntar(*notas) -> str:
    return "; ".join(n for n in notas if n)


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


def bloco_entrada(caminho: Path, papel: str, fonte: str, data_ref: str, cobertura: str, unidade: str, chaves: str,
                  filtros: str) -> dict:
    return {"caminho": rel(caminho), "sha256": sha256(caminho), "bytes": caminho.stat().st_size, "papel": papel,
            "fonte": fonte, "data_referencia": data_ref, "cobertura": cobertura, "unidade": unidade, "chaves": chaves,
            "filtros": filtros}


# ---------------------------------------------------------------------------
# Insumos
# ---------------------------------------------------------------------------

def carregar() -> dict:
    """Lê e confere os insumos; monta células, candidatos de 1ª e 2ª opção e as exclusões com motivo."""
    dic = json.loads(E9.DICIONARIO.read_text(encoding="utf-8"))
    conferencias = E9.conferir_insumos(dic)
    mapa, _ = E9.mapa_bolsa_por_faixa()
    ivs = E9.carregar_ivs()
    cand = pd.read_parquet(E9.ESCOLHAS)
    if not (cand["natureza_dos_dados"] == NATUREZA).all():
        raise FalhaValidacao("escolhas com natureza diferente de EMPIRICO")
    conj, diag_conj = E9.preparar_conjunto(pd.read_parquet(E9.CONJ_PRINCIPAL), ivs, mapa)
    for d in diag_conj["alternativas_retiradas_sem_ivs"]:
        hit = cand[(cand.ciclo == d["ciclo"]) & (cand.co_cnes_7d == d["co_cnes_7d"]) & (cand.cod_curso == d["cod_curso"])]
        if len(hit):
            raise FalhaValidacao(f"célula sem IVS escolhida por candidato: {d}")
    macros = sorted(conj["macrorregiao"].unique())
    estratos = sorted(conj["estrato_territorial"].unique())
    if ESTRATO_BASE_M1 not in estratos or E9.BASE_ESTRATO not in estratos:
        raise FalhaValidacao(f"estratos inesperados: {estratos}")

    # Região de saúde (CIR oficial do TabNet; manifesto conferido pela função da X5) e centroides do IBGE.
    manifesto_cir = X45.adquirir_cir(False)
    cir, diag_cir = X45.ler_cir()
    mapa_cir = cir.set_index("co_ibge")["co_cir"]
    coord, diag_coord = X1.ler_coordenadas()
    if diag_coord.get("status") != "OBTIDO":
        raise FalhaValidacao("centroides do IBGE indisponíveis")
    xy = coord.set_index("co_ibge")
    conj["co_cir"] = conj["co_ibge"].map(mapa_cir)
    falta_xy = sorted(set(conj["co_ibge"]) - set(xy.index))
    if falta_xy:
        raise FalhaValidacao(f"municípios do conjunto sem centroide: {falta_xy}")

    # Origem dos candidatos (G1, regra principal).
    org = pd.read_parquet(G1_ORIGEM)
    if not (org["natureza_dos_dados"] == NATUREZA).all():
        raise FalhaValidacao("G1 com natureza diferente de EMPIRICO")
    org = org[org["regra_ligacao"] == REGRA_G1].copy()
    if org.duplicated(["ciclo", "id_candidato"]).any():
        raise FalhaValidacao("G1: candidato repetido na regra principal")
    ids_cand = set(zip(cand["ciclo"], cand["id_candidato"]))
    ids_org = set(zip(org["ciclo"], org["id_candidato"]))
    if ids_cand != ids_org:
        raise FalhaValidacao("universo do G1 difere do de escolhas_candidatos")
    org["co_ibge_origem"] = org["co_ibge_origem"].astype(object).where(org["co_ibge_origem"].notna(), None)

    r1_todos = cand[cand["opcao_rank"] == 1].copy()
    r1 = r1_todos.merge(org[["ciclo", "id_candidato", "co_ibge_origem", "motivo_origem_ausente", "motivo",
                             "n_municipios_origem"]], on=["ciclo", "id_candidato"], how="left", validate="one_to_one")
    cel_sem_cir = conj[conj["co_cir"].isna()]
    chaves_sem_cir = set(zip(cel_sem_cir["ciclo"], cel_sem_cir["co_cnes_7d"], cel_sem_cir["cod_curso"]))
    motivo = np.full(len(r1), "", dtype=object)
    sem_org = r1["co_ibge_origem"].isna().to_numpy()
    motivo[sem_org] = [f"sem município de origem no G1 ({m})" if isinstance(m, str) and m else
                       "sem município de origem no G1" for m in r1.loc[sem_org, "motivo_origem_ausente"]]
    org_sem_cir = (~sem_org) & ~r1["co_ibge_origem"].isin(mapa_cir.index).to_numpy()
    motivo[org_sem_cir & (motivo == "")] = "município de origem sem região de saúde na tabela oficial (TabNet)"
    esc_sem_cir = np.array([k in chaves_sem_cir for k in zip(r1["ciclo"], r1["co_cnes_7d"], r1["cod_curso"])])
    motivo[esc_sem_cir & (motivo == "")] = "1ª opção em célula de município sem região de saúde na tabela oficial"
    org_sem_xy = (~sem_org) & ~r1["co_ibge_origem"].isin(xy.index).to_numpy()
    if (org_sem_xy & (motivo == "")).any():
        raise FalhaValidacao("município de origem sem centroide")
    r1["motivo_exclusao_p1"] = motivo
    excl = (r1[r1["motivo_exclusao_p1"] != ""].groupby(["motivo_exclusao_p1", "ciclo"]).size()
            .rename("candidatos").reset_index())
    r1_p1 = r1[r1["motivo_exclusao_p1"] == ""].copy()
    sem_r1 = sorted(set(cand["id_candidato"]) - set(r1_todos["id_candidato"]))

    # 2ª opção (M7) dos candidatos da amostra P1.
    r2 = cand[(cand["opcao_rank"] == 2) & cand["id_candidato"].isin(set(r1_p1["id_candidato"]))].copy()
    r2_sem_cir = np.array([k in chaves_sem_cir for k in zip(r2["ciclo"], r2["co_cnes_7d"], r2["cod_curso"])])
    r2_fora = int(r2_sem_cir.sum())
    r2 = r2[~r2_sem_cir].copy()
    conj_p1 = conj[conj["co_cir"].notna()].reset_index(drop=True)

    g1_resumo = json.loads(G1_RESUMO.read_text(encoding="utf-8"))
    return {"conferencias": conferencias, "mapa": mapa, "ivs": ivs, "cand": cand, "conj": conj,
            "conj_p1": conj_p1, "diag_conj": diag_conj, "macros": macros, "estratos": estratos,
            "mapa_cir": mapa_cir, "diag_cir": diag_cir, "manifesto_cir": manifesto_cir, "xy": xy,
            "diag_coord": diag_coord, "org": org, "r1_todos": r1_todos, "r1": r1, "r1_p1": r1_p1,
            "r2_p1": r2, "r2_fora_sem_cir": r2_fora, "exclusoes": excl, "sem_r1": len(sem_r1),
            "celulas_sem_cir": cel_sem_cir[["ciclo", "co_cnes_7d", "cod_curso", "co_ibge"]].to_dict("records"),
            "g1_resumo": g1_resumo}


# ---------------------------------------------------------------------------
# Desenho longo: um grupo por candidato × posto; uma linha por célula do conjunto do grupo
# ---------------------------------------------------------------------------

def montar_desenho(conj: pd.DataFrame, r1: pd.DataFrame, r2: pd.DataFrame | None, dados: dict,
                   com_origem: bool = True) -> dict:
    """Linhas contíguas por grupo. `conj` indexado 0..n−1; escolhas fora do conjunto fazem o script parar."""
    pos = pd.Series(np.arange(len(conj)), index=pd.MultiIndex.from_frame(conj[["ciclo", "co_cnes_7d", "cod_curso"]]))

    def localizar(df: pd.DataFrame) -> np.ndarray:
        idx = pos.reindex(pd.MultiIndex.from_frame(df[["ciclo", "co_cnes_7d", "cod_curso"]]))
        if idx.isna().any():
            raise FalhaValidacao(f"{int(idx.isna().sum())} escolhas fora do conjunto de escolha")
        return idx.to_numpy(dtype=int)

    cols = ["ciclo", "id_candidato", "id_conjunto_escolha", "cod_curso", "pontuacao"]
    if com_origem:
        cols.append("co_ibge_origem")
    g1 = r1[cols].copy()
    g1["posto"] = 1
    g1["idx_escolhida"] = localizar(r1)
    g1["idx_excluida"] = -1
    grupos = [g1]
    if r2 is not None and len(r2):
        g2 = r2[["ciclo", "id_candidato", "id_conjunto_escolha", "cod_curso"]].copy()
        info1 = g1.set_index("id_candidato")
        g2["pontuacao"] = g2["id_candidato"].map(info1["pontuacao"])
        if com_origem:
            g2["co_ibge_origem"] = g2["id_candidato"].map(info1["co_ibge_origem"])
        g2["posto"] = 2
        g2["idx_escolhida"] = localizar(r2)
        mesmo = g2["id_conjunto_escolha"].to_numpy() == g2["id_candidato"].map(info1["id_conjunto_escolha"]).to_numpy()
        g2["idx_excluida"] = np.where(mesmo, g2["id_candidato"].map(info1["idx_escolhida"]).to_numpy(), -1)
        if (g2["idx_excluida"] == g2["idx_escolhida"]).any():
            raise FalhaValidacao("2ª opção igual à 1ª")
        grupos.append(g2)
    G = pd.concat(grupos, ignore_index=True)
    G = G.sort_values(["ciclo", "id_conjunto_escolha", "id_candidato", "posto"], kind="stable").reset_index(drop=True)
    cel_por_conj = {s: np.flatnonzero(conj["id_conjunto_escolha"].to_numpy() == s)
                    for s in conj["id_conjunto_escolha"].unique()}
    blocos, starts, esc = [], [], []
    p = 0
    for s, j, x in zip(G["id_conjunto_escolha"], G["idx_escolhida"], G["idx_excluida"]):
        C = cel_por_conj[s]
        if x >= 0:
            C = C[C != x]
        k = np.flatnonzero(C == j)
        if len(k) != 1:
            raise FalhaValidacao("célula escolhida fora do conjunto do grupo")
        starts.append(p)
        esc.append(p + int(k[0]))
        blocos.append(C)
        p += len(C)
    cel = np.concatenate(blocos)
    starts = np.array(starts, dtype=np.int64)
    tam = np.diff(np.append(starts, len(cel)))
    grp = np.repeat(np.arange(len(G)), tam)
    G["cluster_conjunto"] = G["id_conjunto_escolha"]
    G["cluster_candidato"] = G["id_candidato"]
    G["cluster_curso"] = [f"curso{int(k):02d}" for k in G["cod_curso"]]
    D = {"cel": cel, "grp": grp, "starts": starts, "esc": np.array(esc, dtype=np.int64), "grupos": G,
         "tam": tam, "conj": conj}
    if com_origem:
        xy = dados["xy"]
        o = G["co_ibge_origem"].to_numpy(dtype=object)[grp]
        c = conj["co_ibge"].to_numpy(dtype=object)[cel]
        lon_o, lat_o = xy.loc[o, "lon"].to_numpy(), xy.loc[o, "lat"].to_numpy()
        lon_c, lat_c = xy.loc[c, "lon"].to_numpy(), xy.loc[c, "lat"].to_numpy()
        D["dist_km"] = X1.haversine_km(lon_o, lat_o, lon_c, lat_c)
        D["mesmo_municipio"] = (o == c).astype(float)
        D["mesma_uf"] = (np.array([x[:2] for x in o]) == np.array([x[:2] for x in c])).astype(float)
        cir = dados["mapa_cir"]
        D["mesma_regiao_saude"] = (cir.reindex(o).to_numpy() == cir.reindex(c).to_numpy()).astype(float)
    return D


def conferir_distancias(D: dict) -> dict:
    """Distância das células escolhidas (posto 1 e 2) igual à do G1 (origem principal)."""
    g1 = pd.read_parquet(G1_DIST)
    g1 = g1[g1["regra_ligacao"] == REGRA_G1]
    G = D["grupos"]
    conj = D["conj"]
    esc_cel = D["cel"][D["esc"]]
    chave = pd.DataFrame({"ciclo": G["ciclo"].to_numpy(), "id_candidato": G["id_candidato"].to_numpy(),
                          "opcao_rank": G["posto"].to_numpy(), "co_cnes_7d": conj["co_cnes_7d"].to_numpy()[esc_cel],
                          "cod_curso": conj["cod_curso"].to_numpy()[esc_cel], "dist": D["dist_km"][D["esc"]]})
    m = chave.merge(g1, on=["ciclo", "id_candidato", "opcao_rank", "co_cnes_7d", "cod_curso"], how="left",
                    validate="one_to_one")
    if m["dist_km_origem_principal"].isna().any():
        raise FalhaValidacao("escolha sem distância no G1")
    dif = float(np.max(np.abs(m["dist"] - m["dist_km_origem_principal"])))
    if dif > 1e-6:
        raise FalhaValidacao(f"distância difere da do G1 em até {dif} km")
    return {"escolhas_conferidas": int(len(m)), "diferenca_maxima_km": dif}


# ---------------------------------------------------------------------------
# Matrizes de atributos
# ---------------------------------------------------------------------------

def atributos_celula(conj: pd.DataFrame, dados: dict, estrato_base: str) -> pd.DataFrame:
    """Atributos do E9 principal (spline linear, bolsa linear, vaga imediata, log vagas, log pop, macro, estrato)."""
    X = E9.matriz_atributos(conj, 1, "linear", dados["macros"], dados["estratos"])
    if estrato_base != E9.BASE_ESTRATO:
        X = X.drop(columns=[c for c in X.columns if c.startswith("estrato_")])
        for e in dados["estratos"]:
            if e != estrato_base:
                X["capital" if e == "capital" else f"estrato_{e}"] = (conj["estrato_territorial"] == e).astype(float)
    return X.reset_index(drop=True)


def matriz_modelo(D: dict, dados: dict, modelo: str, extra: dict[str, np.ndarray] | None = None) -> pd.DataFrame:
    conj = D["conj"]
    if modelo in ("E9_amostra_completa", "M0"):
        Xc = atributos_celula(conj, dados, E9.BASE_ESTRATO)
        X = Xc.iloc[D["cel"]].reset_index(drop=True)
    else:
        Xc = atributos_celula(conj, dados, ESTRATO_BASE_M1)
        if modelo == "M4":
            Xc = Xc.drop(columns=[c for c in Xc.columns if c.startswith("macro_")])
            uf = conj["co_ibge"].str[:2]
            base = uf.value_counts().sort_index().idxmax()
            for u in sorted(uf.unique()):
                if u != base:
                    Xc[f"uf_{u}"] = (uf == u).astype(float).to_numpy()
        X = Xc.iloc[D["cel"]].reset_index(drop=True)
        if modelo == "M2":
            X[TERMO_LOGDIST] = np.log1p(D["dist_km"])
        else:
            X[TERMO_DIST] = D["dist_km"] / ESCALA_DIST_KM
        for t in TERMOS_ORIGEM:
            X[t] = D[t]
    for k, v in (extra or {}).items():
        X[k] = v
    return X


# ---------------------------------------------------------------------------
# Logit condicional (e explodido) por máxima verossimilhança, formato longo
# ---------------------------------------------------------------------------

def _indicadora(D: dict):
    """Matriz esparsa grupo × linha (soma por grupo como produto; mais rápida que reduceat em 2D)."""
    if "_S" not in D:
        from scipy import sparse
        n = len(D["grp"])
        D["_S"] = sparse.csr_matrix((np.ones(n), (D["grp"], np.arange(n))), shape=(len(D["starts"]), n))
    return D["_S"]


def _estat(theta: np.ndarray, X: np.ndarray, D: dict, w: np.ndarray | None = None, com_info: bool = True) -> dict:
    st, grp, esc = D["starts"], D["grp"], D["esc"]
    v = X @ theta
    vmax = np.maximum.reduceat(v, st)
    e = np.exp(v - vmax[grp])
    S = np.add.reduceat(e, st)
    p = e / S[grp]
    ll_g = v[esc] - vmax - np.log(S)
    mbar = _indicadora(D) @ (p[:, None] * X)
    scores = X[esc] - mbar
    wg = np.ones(len(st)) if w is None else w
    out = {"ll": float(wg @ ll_g), "grad": wg @ scores, "scores": scores, "p": p}
    if com_info:
        out["info"] = X.T @ (X * (p * wg[grp])[:, None]) - mbar.T @ (mbar * wg[:, None])
    return out


def _estat_tipos(theta: np.ndarray, X: np.ndarray, D: dict, w: np.ndarray | None = None,
                 com_info: bool = True) -> dict:
    """Mesma verossimilhança no desenho comprimido: um 'tipo' = conjunto × município de origem (linhas
    idênticas); n_linha = candidatos do tipo que escolheram a célula; N = candidatos do tipo."""
    st, grp, n_l, N = D["starts"], D["grp"], D["n_linha"], D["N"]
    v = X @ theta
    vmax = np.maximum.reduceat(v, st)
    e = np.exp(v - vmax[grp])
    S = np.add.reduceat(e, st)
    p = e / S[grp]
    wt = (np.ones(len(st)) if w is None else w)
    ll = float(wt @ (np.add.reduceat(n_l * v, st) - N * (vmax + np.log(S))))
    mbar = _indicadora(D) @ (p[:, None] * X)
    if "_nX" not in D:
        D["_nX"] = _indicadora(D) @ (n_l[:, None] * X)
    sc = D["_nX"] - N[:, None] * mbar
    out = {"ll": ll, "grad": wt @ sc, "scores": sc, "p": p}
    if com_info:
        wn = wt * N
        out["info"] = X.T @ (X * (p * wn[grp])[:, None]) - mbar.T @ (mbar * wn[:, None])
    return out


def comprimir(A: np.ndarray, D: dict) -> tuple[np.ndarray, dict]:
    """Desenho comprimido por tipo (conjunto × município de origem), só para a 1ª opção. Confere que as linhas de
    todos os candidatos do tipo são idênticas."""
    G = D["grupos"]
    if (G["idx_excluida"] >= 0).any():
        raise FalhaValidacao("compressão só para o desenho da 1ª opção")
    chave = G["cluster_conjunto"].astype(str) + "|" + G["co_ibge_origem"].astype(str)
    cod, _ = pd.factorize(chave)
    primeiro = np.unique(cod, return_index=True)[1]
    blocos, n_l, starts, tipo_conj = [], [], [], []
    p = 0
    for t, g in enumerate(primeiro):
        a, m = D["starts"][g], D["tam"][g]
        blocos.append(np.arange(a, a + m))
        cnt = np.zeros(m)
        membros = np.flatnonzero(cod == t)
        for h in membros:
            b = D["starts"][h]
            if D["tam"][h] != m or not np.array_equal(A[b:b + m], A[a:a + m]):
                raise FalhaValidacao("compressão: candidatos do mesmo tipo com linhas diferentes")
            cnt[D["esc"][h] - b] += 1
        n_l.append(cnt)
        starts.append(p)
        p += m
        tipo_conj.append(G["cluster_conjunto"].iat[g])
    linhas = np.concatenate(blocos)
    starts = np.array(starts, dtype=np.int64)
    tam = np.diff(np.append(starts, len(linhas)))
    n_l = np.concatenate(n_l)
    Dt = {"starts": starts, "grp": np.repeat(np.arange(len(starts)), tam), "n_linha": n_l,
          "N": np.add.reduceat(n_l, starts), "tam": tam, "conjunto_do_tipo": np.array(tipo_conj, dtype=object)}
    return A[linhas], Dt


def ajustar_cl(X: np.ndarray, D: dict, w: np.ndarray | None = None, theta0: np.ndarray | None = None,
               estat=None) -> dict:
    """Newton–Raphson com meio-passo (critério de parada do E9: decremento de Newton)."""
    _estat_ = _estat if estat is None else estat
    theta = np.zeros(X.shape[1]) if theta0 is None else theta0.astype(float).copy()
    est = _estat_(theta, X, D, w)
    convergiu, it = False, 0
    for it in range(1, MAX_ITER + 1):
        passo = np.linalg.solve(est["info"], est["grad"])
        dec = float(est["grad"] @ passo)
        if dec < TOL_DEC:
            convergiu = True
            break
        tol = 1e-12 * max(1.0, abs(est["ll"]))
        t = 1.0
        while True:
            novo = _estat_(theta + t * passo, X, D, w)
            if novo["ll"] >= est["ll"] - tol or t < 1e-8:
                break
            t /= 2.0
        theta = theta + t * passo
        est = novo
        if np.max(np.abs(t * passo)) < TOL_PASSO:
            convergiu = True
            break
    est = _estat_(theta, X, D, w)
    dec = float(est["grad"] @ np.linalg.solve(est["info"], est["grad"]))
    return {"theta": theta, "ll": est["ll"], "info": est["info"], "scores": est["scores"], "grad": est["grad"],
            "iteracoes": it, "decremento_final": dec,
            "convergiu": bool(convergiu and dec < 1e-8 and np.all(np.isfinite(theta)))}


def colunas_sem_variacao(X: pd.DataFrame, D: dict) -> list[str]:
    A = X.to_numpy(dtype=float)
    amp = np.maximum.reduceat(A, D["starts"], axis=0) - np.minimum.reduceat(A, D["starts"], axis=0)
    return [c for c, m in zip(X.columns, amp.max(axis=0)) if m == 0.0]


def estimar(X: pd.DataFrame, D: dict, *, modelo: str, ciclo: str, amostra: str) -> dict:
    """Ajuste, covariâncias (MV, cluster por conjunto e por candidato) e diagnósticos."""
    omit = colunas_sem_variacao(X, D)
    X = X.drop(columns=omit)
    A = X.to_numpy(dtype=float)
    G = D["grupos"]
    base = {"modelo": modelo, "ciclo": ciclo, "amostra": amostra, "termos": list(X.columns), "omitidas": omit,
            "n_candidatos": int(G.loc[G["posto"] == 1, "id_candidato"].nunique()), "n_grupos": int(len(G)),
            "n_linhas": int(len(A)), "n_conjuntos": int(G["cluster_conjunto"].nunique())}
    media = np.add.reduceat(A, D["starts"], axis=0) / D["tam"][:, None]
    posto = int(np.linalg.matrix_rank(A - media[D["grp"]]))
    if posto < A.shape[1]:
        return {**base, "ok": False, "status": "NAO_CONVERGIU", "nota": f"X sem posto completo ({posto} < {A.shape[1]})"}
    try:
        fit = ajustar_cl(A, D)
    except (np.linalg.LinAlgError, FloatingPointError) as erro:
        return {**base, "ok": False, "status": "NAO_CONVERGIU", "nota": f"estimação falhou ({type(erro).__name__})"}
    if not fit["convergiu"]:
        return {**base, "ok": False, "status": "NAO_CONVERGIU", "nota": "Newton–Raphson não convergiu",
                "iteracoes": fit["iteracoes"]}
    info_inv = np.linalg.inv(fit["info"])
    Vc, Gc = E9.covariancia_cluster(info_inv, fit["scores"], G["cluster_conjunto"].to_numpy())
    Vk, Gk = E9.covariancia_cluster(info_inv, fit["scores"], G["cluster_candidato"].to_numpy())
    nota = _juntar("omitidas por não variarem dentro de nenhum grupo: " + ", ".join(omit) if omit else "")
    return {**base, "ok": True, "status": "EXECUTADO", "nota": nota, "theta": fit["theta"], "ll": fit["ll"],
            "iteracoes": fit["iteracoes"], "V_mle": info_inv, "V_conj": Vc, "V_cand": Vk, "G_conj": Gc, "G_cand": Gk,
            "_A": A, "_D": D, "_scores": fit["scores"], "_info": fit["info"]}


# ---------------------------------------------------------------------------
# Logit misto (M8): máxima verossimilhança simulada, gradiente analítico
# ---------------------------------------------------------------------------

def sorteios_halton(n_grupos: int, n_sorteios: int, semente: int) -> tuple[np.ndarray, np.ndarray]:
    """Normais padrão de Halton embaralhado (2 dimensões), um bloco de `n_sorteios` por grupo."""
    from scipy.stats import qmc
    h = qmc.Halton(d=2, scramble=True, seed=semente)
    u = h.random(n_grupos * n_sorteios)
    u = np.clip(u, 1e-12, 1 - 1e-12)
    z = stats.norm.ppf(u).reshape(n_grupos, n_sorteios, 2)
    return z[:, :, 0].copy(), z[:, :, 1].copy()


def blocos_por_conjunto(D: dict) -> list[tuple[int, int, int, int]]:
    """(grupo inicial, grupo final, linha inicial, nº de células) de cada conjunto; exige que todos os grupos do
    conjunto tenham as mesmas células na mesma ordem (só 1ª opção, sem célula excluída)."""
    G = D["grupos"]
    if (G["idx_excluida"] >= 0).any():
        raise FalhaValidacao("logit misto: desenho com célula excluída (posto 2) não é suportado")
    out = []
    s = G["cluster_conjunto"].to_numpy()
    ini = np.flatnonzero(np.r_[True, s[1:] != s[:-1]])
    fim = np.r_[ini[1:], len(s)]
    for a, b in zip(ini, fim):
        m = int(D["tam"][a])
        if not (D["tam"][a:b] == m).all():
            raise FalhaValidacao("logit misto: grupos do mesmo conjunto com tamanhos diferentes")
        bloco = D["cel"][D["starts"][a]:D["starts"][a] + (b - a) * m].reshape(b - a, m)
        if not (bloco == bloco[0]).all():
            raise FalhaValidacao("logit misto: grupos do mesmo conjunto com células em ordem diferente")
        out.append((int(a), int(b), int(D["starts"][a]), m))
    return out


def misto_ll_grad(params: np.ndarray, Xf: np.ndarray, xb: np.ndarray, xd: np.ndarray, D: dict,
                  eta_b: np.ndarray, eta_d: np.ndarray, blocos: list | None = None,
                  max_elem: int = 400_000) -> tuple[float, np.ndarray, np.ndarray]:
    """Log-verossimilhança simulada, gradiente e scores por grupo. params = [theta_fixos, mu_b, s_b, mu_d, s_d].

    Conjunto a conjunto: utilidades num arranjo (candidatos × sorteios × células), sem índices por linha.
    P_g = média dos sorteios de P(escolhida | sorteio); w_gd = P_gd / (R·P_g);
    d log P_g / d theta = x_esc − Σ_j Q_j x_j com Q_j = Σ_d w_gd P_jd (e análogos para os desvios).
    """
    st, esc = D["starts"], D["esc"]
    blocos = blocos_por_conjunto(D) if blocos is None else blocos
    Kf = Xf.shape[1]
    th = params[:Kf]
    mb, sb, md, sd = params[Kf:]
    vf = Xf @ th + mb * xb + md * xd
    G, R = eta_b.shape
    Q = np.zeros(len(vf))
    Qb = np.zeros(len(vf))
    Qd = np.zeros(len(vf))
    Pg = np.empty(G)
    Wb = np.empty(G)
    Wd = np.empty(G)
    tarefas = []
    for g0, g1, l0, m in blocos:
        nb = max(1, max_elem // (R * m))
        for a in range(g0, g1, nb):
            tarefas.append((a, min(g1, a + nb), l0 + (a - g0) * m, m))

    def lote(t: tuple[int, int, int, int]) -> None:
        """Um lote de candidatos do mesmo conjunto: arranjo (candidatos × sorteios × células) pequeno o
        bastante para caber no cache."""
        g0, g1, l0, m = t
        n = g1 - g0
        sl = slice(l0, l0 + n * m)
        Vf, B, Dd = vf[sl].reshape(n, m), xb[sl].reshape(n, m), xd[sl].reshape(n, m)
        el = esc[g0:g1] - st[g0:g1]
        eb, ed = eta_b[g0:g1], eta_d[g0:g1]
        P = (sb * eb)[:, :, None] * B[:, None, :]
        P += (sd * ed)[:, :, None] * Dd[:, None, :]
        P += Vf[:, None, :]
        P -= P.max(axis=2, keepdims=True)
        np.exp(P, out=P)
        P /= P.sum(axis=2, keepdims=True)
        Pc = P[np.arange(n), :, el]                                  # n × R
        pg = Pc.mean(axis=1)
        W = Pc / (R * pg[:, None])
        Pg[g0:g1] = pg
        Wb[g0:g1] = (W * eb).sum(axis=1)
        Wd[g0:g1] = (W * ed).sum(axis=1)
        Q3 = np.matmul(np.stack([W, W * eb, W * ed], axis=1), P)      # n × 3 × m
        Q[sl] = Q3[:, 0, :].ravel()
        Qb[sl] = Q3[:, 1, :].ravel()
        Qd[sl] = Q3[:, 2, :].ravel()

    # Lotes independentes, cada um grava só as suas fatias: o resultado não depende da ordem das threads.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=N_THREADS_M8) as ex:
        list(ex.map(lote, tarefas))
    ll = float(np.log(Pg).sum())
    Xall = np.column_stack([Xf, xb, xd])
    sc_lin = Xall[esc] - np.add.reduceat(Q[:, None] * Xall, st, axis=0)
    sc_sb = xb[esc] * Wb - np.add.reduceat(Qb * xb, st)
    sc_sd = xd[esc] * Wd - np.add.reduceat(Qd * xd, st)
    scores = np.column_stack([sc_lin[:, :Kf], sc_lin[:, Kf], sc_sb, sc_lin[:, Kf + 1], sc_sd])
    return ll, scores.sum(axis=0), scores


def hessiana_numerica(grad, p: np.ndarray, passo_rel: float) -> np.ndarray:
    """Hessiana da log-verossimilhança por diferença central do gradiente analítico (simetrizada)."""
    K = len(p)
    H = np.zeros((K, K))
    for k in range(K):
        h = passo_rel * max(1.0, abs(p[k]))
        pp, pm = p.copy(), p.copy()
        pp[k] += h
        pm[k] -= h
        H[:, k] = (grad(pp) - grad(pm)) / (2 * h)
    return 0.5 * (H + H.T)


def polir_newton(llgrad, p: np.ndarray, passo_rel: float, max_passos: int = POLIMENTO_NEWTON,
                 tol: float = TOL_GRAD_POLIMENTO, limites: tuple[int, tuple[float, float]] | None = None) -> dict:
    """Polimento por Newton depois do quase-Newton (como na X5): hessiana numérica do gradiente analítico,
    meio-passo se a log-verossimilhança cair; para com gradiente máximo < tol, hessiana não definida negativa,
    parâmetro limitado fora do intervalo ou `max_passos`. Devolve o ponto, a hessiana e o diagnóstico."""
    ll, g, _ = llgrad(p)
    passos = 0
    H = hessiana_numerica(lambda q: llgrad(q)[1], p, passo_rel)
    while np.max(np.abs(g)) >= tol and passos < max_passos:
        if not np.all(np.linalg.eigvalsh(-H) > 0):
            break
        d = np.linalg.solve(-H, g)
        t = 1.0
        while t > 1e-6:
            q = p + t * d
            fora = limites is not None and not (limites[1][0] < q[limites[0]] < limites[1][1])
            if not fora:
                lq, gq, _ = llgrad(q)
                if lq >= ll - 1e-9 * abs(ll):
                    break
            t /= 2
        if t <= 1e-6:
            break
        p, ll, g = q, lq, gq
        passos += 1
        H = hessiana_numerica(lambda q_: llgrad(q_)[1], p, passo_rel)
    _, _, sc = llgrad(p)
    return {"p": p, "ll": ll, "g": g, "scores": sc, "H": H, "passos_newton": passos}


def estimar_misto(r1: dict, nomes: list[str]) -> dict:
    """M8 sobre a amostra e a matriz do M1 (1ª opção); partida no M1 com desvios 0,1."""
    A, D = r1["_A"], r1["_D"]
    kb, kd = nomes.index(TERMO_BOLSA), nomes.index(TERMO_DIST)
    fixos = [j for j in range(A.shape[1]) if j not in (kb, kd)]
    Xf, xb, xd = A[:, fixos], A[:, kb], A[:, kd]
    eta_b, eta_d = sorteios_halton(len(D["starts"]), N_HALTON, SEMENTE_HALTON)
    blocos = blocos_por_conjunto(D)
    p0 = np.concatenate([r1["theta"][fixos], [r1["theta"][kb], 0.1, r1["theta"][kd], 0.1]])
    contador = {"n": 0}
    t0 = time.time()

    def f(p):
        contador["n"] += 1
        if contador["n"] > MAX_AVAL_M8:
            raise TimeoutError
        ll, g, _ = misto_ll_grad(p, Xf, xb, xd, D, eta_b, eta_d, blocos)
        return -ll, -g

    nomes_p = [nomes[j] for j in fixos] + [f"media_{TERMO_BOLSA}", f"desvio_{TERMO_BOLSA}", f"media_{TERMO_DIST}",
                                           f"desvio_{TERMO_DIST}"]
    base = {"modelo": "M8", "termos": nomes_p, "n_sorteios": N_HALTON, "semente": SEMENTE_HALTON,
            "max_avaliacoes": MAX_AVAL_M8}
    try:
        res = optimize.minimize(f, p0, jac=True, method="L-BFGS-B",
                                options={"maxiter": MAX_AVAL_M8, "gtol": 1e-6, "ftol": 1e-13, "maxfun": MAX_AVAL_M8})
    except TimeoutError:
        return {**base, "ok": False, "status": "NAO_CONVERGIU", "avaliacoes": contador["n"] - 1,
                "segundos": round(time.time() - t0),
                "nota": (f"logit misto sem convergência dentro do teto de {MAX_AVAL_M8} avaliações da "
                         f"verossimilhança simulada (≈ 30 min, protocolo do agente); não forçado")}
    pol = polir_newton(lambda q: misto_ll_grad(q, Xf, xb, xd, D, eta_b, eta_d, blocos), res.x, 1e-5)
    p, ll, g, scores, H = pol["p"], pol["ll"], pol["g"], pol["scores"], pol["H"]
    ev = np.linalg.eigvalsh(-H)
    if not (np.max(np.abs(g)) < TOL_GRAD_POLIMENTO) or not np.all(ev > 0):
        return {**base, "ok": False, "status": "NAO_CONVERGIU", "avaliacoes": contador["n"],
                "segundos": round(time.time() - t0), "grad_max": float(np.max(np.abs(g))),
                "passos_newton": pol["passos_newton"],
                "nota": (f"logit misto sem convergência limpa depois do quase-Newton ({res.message}) e de "
                         f"{pol['passos_newton']} passos de Newton: gradiente máximo {np.max(np.abs(g)):.2e}"
                         + ("" if np.all(ev > 0) else ", hessiana não definida negativa") + "; não forçado")}
    info_inv = np.linalg.inv(-H)
    G = D["grupos"]
    Vc, Gc = E9.covariancia_cluster(info_inv, scores, G["cluster_conjunto"].to_numpy())
    Vk, Gk = E9.covariancia_cluster(info_inv, scores, G["cluster_candidato"].to_numpy())
    return {**base, "ok": True, "status": "EXECUTADO", "theta": p, "ll": ll, "V_mle": info_inv, "V_conj": Vc,
            "V_cand": Vk, "G_conj": Gc, "G_cand": Gk, "avaliacoes": contador["n"], "segundos": round(time.time() - t0),
            "grad_max": float(np.max(np.abs(g))), "otimizador": str(res.message),
            "passos_newton": pol["passos_newton"],
            "autovalor_min_informacao": float(ev.min()), "iteracoes": int(res.nit),
            "nota": ("máxima verossimilhança simulada (Halton embaralhado, um bloco de sorteios por candidato); "
                     "desvios relatados em valor absoluto (o sinal não é identificado); H0 desvio = 0 fica na "
                     "fronteira e o p normal é conservador")}


# ---------------------------------------------------------------------------
# Logit aninhado (M9): um lambda comum, ninhos = CIR dentro do conjunto do candidato, gradiente analítico
# ---------------------------------------------------------------------------

def aninhado_ll_grad(params: np.ndarray, X: np.ndarray, D: dict, ninho: np.ndarray, ninho_grp: np.ndarray,
                     ninho_st: np.ndarray, grp_ninho_st: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    """Linhas ordenadas por grupo e, dentro do grupo, por ninho. Devolve LL, gradiente e scores por grupo.

    log P_j = V_j/λ + (λ − 1) IV_n − log Σ_m exp(λ IV_m), IV_n = log Σ_{k∈n} exp(V_k/λ).
    """
    K = X.shape[1]
    beta, lam = params[:K], params[K]
    esc = D["esc"]
    V = X @ beta
    a = V / lam
    amax = np.maximum.reduceat(a, ninho_st)
    ea = np.exp(a - amax[ninho])
    Sn = np.add.reduceat(ea, ninho_st)
    IV = amax + np.log(Sn)
    pcond = ea / Sn[ninho]                          # P(k | n)
    b = lam * IV
    bmax = np.maximum.reduceat(b, grp_ninho_st)
    eb = np.exp(b - bmax[ninho_grp])
    Sg = np.add.reduceat(eb, grp_ninho_st)
    Pn = eb / Sg[ninho_grp]                         # P(n)
    nj = ninho[esc]
    ll_g = a[esc] + (lam - 1.0) * IV[nj] - (bmax + np.log(Sg))
    xbar_n = np.add.reduceat(pcond[:, None] * X, ninho_st, axis=0)
    Vbar_n = np.add.reduceat(pcond * V, ninho_st)
    soma_x = np.add.reduceat(Pn[:, None] * xbar_n, grp_ninho_st, axis=0)
    sc_beta = X[esc] / lam + (lam - 1.0) / lam * xbar_n[nj] - soma_x
    termo_m = IV - Vbar_n / lam
    soma_m = np.add.reduceat(Pn * termo_m, grp_ninho_st)
    sc_lam = -V[esc] / lam ** 2 + IV[nj] - (lam - 1.0) * Vbar_n[nj] / lam ** 2 - soma_m
    scores = np.column_stack([sc_beta, sc_lam])
    return float(ll_g.sum()), scores.sum(axis=0), scores


def preparar_ninhos(D: dict, cir_linha: np.ndarray) -> tuple[dict, np.ndarray, dict]:
    """Reordena as linhas por (grupo, CIR) e devolve o desenho reordenado e os índices dos ninhos."""
    ordem = np.lexsort((cir_linha, D["grp"]))
    grp = D["grp"][ordem]
    inv = np.empty_like(ordem)
    inv[ordem] = np.arange(len(ordem))
    D2 = {**D, "grp": grp, "esc": inv[D["esc"]], "cel": D["cel"][ordem]}
    chave = np.column_stack([grp, cir_linha[ordem]])
    novo = np.r_[True, np.any(chave[1:] != chave[:-1], axis=1)]
    ninho = np.cumsum(novo) - 1
    ninho_st = np.flatnonzero(novo)
    ninho_grp = grp[ninho_st]
    grp_ninho_st = np.flatnonzero(np.r_[True, ninho_grp[1:] != ninho_grp[:-1]])
    tam = np.diff(np.append(ninho_st, len(grp)))
    return D2, ordem, {"ninho": ninho, "ninho_st": ninho_st, "ninho_grp": ninho_grp, "grp_ninho_st": grp_ninho_st,
                       "n_ninhos": int(len(ninho_st)), "n_ninhos_unitarios": int((tam == 1).sum()),
                       "celulas_por_ninho_media": float(tam.mean())}


def estimar_aninhado(r1: dict, cir_linha: np.ndarray) -> dict:
    A, D = r1["_A"], r1["_D"]
    D2, ordem, nin = preparar_ninhos(D, cir_linha)
    X = A[ordem]
    args = (X, D2, nin["ninho"], nin["ninho_grp"], nin["ninho_st"], nin["grp_ninho_st"])
    contador = {"n": 0}
    t0 = time.time()

    def f(p):
        contador["n"] += 1
        ll, g, _ = aninhado_ll_grad(p, *args)
        return -ll, -g

    p0 = np.concatenate([r1["theta"], [1.0]])
    K = X.shape[1]
    res = optimize.minimize(f, p0, jac=True, method="L-BFGS-B", bounds=[(None, None)] * K + [LAMBDA_LIMITES],
                            options={"maxiter": MAX_AVAL_M9, "maxfun": MAX_AVAL_M9, "gtol": 1e-8, "ftol": 1e-15})
    p = res.x
    termos = r1["termos"] + ["lambda"]
    base = {"modelo": "M9", "termos": termos, "avaliacoes": contador["n"], "segundos": round(time.time() - t0),
            "otimizador": str(res.message), **{k: v for k, v in nin.items() if not isinstance(v, np.ndarray)}}
    pol = polir_newton(lambda q: aninhado_ll_grad(q, *args), p, 1e-6, limites=(K, LAMBDA_LIMITES))
    p, ll, g, scores, H = pol["p"], pol["ll"], pol["g"], pol["scores"], pol["H"]
    base["passos_newton"] = pol["passos_newton"]
    no_limite = bool(min(abs(p[K] - LAMBDA_LIMITES[0]), abs(p[K] - LAMBDA_LIMITES[1])) < 1e-6)
    ev = np.linalg.eigvalsh(-H)
    def_pos = bool(np.all(ev > 0))
    conv = bool(def_pos and not no_limite and np.max(np.abs(g)) < TOL_GRAD_POLIMENTO and np.all(np.isfinite(p)))
    base.update({"theta": p, "ll": ll, "grad_max": float(np.max(np.abs(g))), "lambda_no_limite": no_limite,
                 "hessiana_definida": def_pos, "autovalor_min_informacao": float(ev.min()), "iteracoes": int(res.nit)})
    if not conv:
        return {**base, "ok": False, "status": "NAO_CONVERGIU",
                "nota": _juntar("lambda no limite da otimização" if no_limite else "",
                                "" if def_pos else "hessiana não definida negativa",
                                f"gradiente máximo {np.max(np.abs(g)):.2e}" if np.max(np.abs(g)) >= TOL_GRAD_POLIMENTO else "")}
    info_inv = np.linalg.inv(-H)
    G = D["grupos"]
    Vc, Gc = E9.covariancia_cluster(info_inv, scores, G["cluster_conjunto"].to_numpy())
    Vk, Gk = E9.covariancia_cluster(info_inv, scores, G["cluster_candidato"].to_numpy())
    return {**base, "ok": True, "status": "EXECUTADO", "V_mle": info_inv, "V_conj": Vc, "V_cand": Vk, "G_conj": Gc,
            "G_cand": Gk, "lr_contra_M1": float(2 * (ll - r1["ll"])),
            "nota": (f"{nin['n_ninhos']} ninhos (CIR × candidato), {nin['n_ninhos_unitarios']} com uma só célula; "
                     "lambda = 1 é o logit condicional; utilidade na escala do logit (V = x'b)")}


# ---------------------------------------------------------------------------
# Linhas de saída
# ---------------------------------------------------------------------------

COLUNAS_EST = ["natureza_dos_dados", "estatuto", "estimando", "modelo", "descricao_modelo", "ciclo", "amostra",
               "tipo_linha", "termo", "coef", "ep_cluster_conjunto", "ep_mle", "ep_cluster_candidato", "ic95_inf",
               "ic95_sup", "p", "p_t_g_menos_1", "p_mle", "estatistica_wald", "gl", "g_conjuntos", "g_candidatos",
               "n_candidatos", "n_grupos_escolha", "n_linhas_candidato_celula", "n_conjuntos", "log_verossimilhanca",
               "iteracoes", "status", "inferencia_cluster_degenerada", "entra_holm", "p_holm", "entra_bky", "q_bky",
               "unidade", "nota"]


def _linha(**kw) -> dict:
    base = {c: np.nan for c in COLUNAS_EST}
    base.update({"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "inferencia_cluster_degenerada": False,
                 "entra_holm": False, "entra_bky": False, "status": "EXECUTADO", "nota": ""})
    base.update(kw)
    return base


def _comuns(r: dict, estimando: str) -> dict:
    return {"estimando": estimando, "modelo": r["modelo"], "descricao_modelo": ROTULO_MODELO.get(r["modelo"], ""),
            "ciclo": r["ciclo"], "amostra": r["amostra"], "n_candidatos": r.get("n_candidatos"),
            "n_grupos_escolha": r.get("n_grupos"), "n_linhas_candidato_celula": r.get("n_linhas"),
            "n_conjuntos": r.get("n_conjuntos"), "status": r["status"]}


def combinacao(r: dict, a: np.ndarray) -> dict:
    b = float(a @ r["theta"])
    ep = math.sqrt(max(float(a @ r["V_conj"] @ a), 0.0))
    ep_m = math.sqrt(max(float(a @ r["V_mle"] @ a), 0.0))
    ep_k = math.sqrt(max(float(a @ r["V_cand"] @ a), 0.0))
    z = b / ep if ep > 0 else float("nan")
    return {"coef": b, "ep_cluster_conjunto": ep, "ep_mle": ep_m, "ep_cluster_candidato": ep_k,
            "ic95_inf": b - Z95 * ep, "ic95_sup": b + Z95 * ep,
            "p": float(2 * stats.norm.sf(abs(z))) if math.isfinite(z) else float("nan"),
            "p_t_g_menos_1": float(2 * stats.t.sf(abs(z), r["G_conj"] - 1)) if math.isfinite(z) else float("nan"),
            "p_mle": float(2 * stats.norm.sf(abs(b / ep_m))) if ep_m > 0 else float("nan"),
            "g_conjuntos": r["G_conj"], "g_candidatos": r["G_cand"]}


def vetor(r: dict, termo: str) -> np.ndarray:
    a = np.zeros(len(r["termos"]))
    a[r["termos"].index(termo)] = 1.0
    return a


def linhas_modelo(r: dict, estimando: str, *, termos: list[str] | None = None, nota_extra: str = "") -> list[dict]:
    c = _comuns(r, estimando)
    if not r["ok"]:
        return [_linha(**c, tipo_linha="coeficiente", termo=t, nota=_juntar(r["nota"], nota_extra))
                for t in (termos or r["termos"])]
    out = []
    for t in (termos or r["termos"]):
        k = r["termos"].index(t)
        out.append(_linha(**c, tipo_linha="coeficiente", termo=t, **combinacao(r, vetor(r, t)),
                          log_verossimilhanca=r["ll"], iteracoes=r.get("iteracoes"), nota=_juntar(r["nota"], nota_extra),
                          unidade="coeficiente da utilidade (logit)" if t != TERMO_BOLSA else
                          "coeficiente da utilidade por R$ 1 mil/mês de bolsa"))
        del k
    return out


def wald(r: dict, R: np.ndarray, chave: str = "V_conj") -> tuple[float, int, float]:
    d = R @ r["theta"]
    M = R @ r[chave] @ R.T
    W = float(d @ np.linalg.solve(M, d))
    return W, int(R.shape[0]), float(stats.chi2.sf(W, R.shape[0]))


# ---------------------------------------------------------------------------
# DAP: razão de coeficientes, delta e bootstrap por conjunto
# ---------------------------------------------------------------------------

DAP_DEF = {
    "distancia_100km_a_menos": ("−β(distância/100 km) / β(bolsa)", "quanto vale, em R$ mil/mês, ter 100 km a menos entre o "
                                "município de origem e o da vaga, mantidos os demais atributos"),
    "mesma_uf": ("β(mesma UF) / β(bolsa)", "quanto vale, em R$ mil/mês, a vaga ficar na UF de origem (além da distância, "
                 "da região de saúde e do município)"),
    "capital": ("β(capital) / β(bolsa)", "quanto vale, em R$ mil/mês, a vaga ficar numa capital de UF em vez de num "
                "município do interior próximo de polo (estrato A2 de referência), mantidos porte e macrorregião"),
    "vaga_imediata": ("[β(tem vaga imediata) + ln 2 · β(log(vagas imediatas + 1))] / β(bolsa)",
                      "quanto vale, em R$ mil/mês, a célula ter 1 vaga imediata em vez de só cadastro reserva"),
}


def dap_vetor(termos: list[str], theta: np.ndarray, atributo: str) -> tuple[float, np.ndarray]:
    """Valor e gradiente da DAP em relação a theta."""
    kb = termos.index(TERMO_BOLSA)
    b = theta[kb]
    g = np.zeros(len(theta))
    if atributo == "distancia_100km_a_menos":
        kd = termos.index(TERMO_DIST)
        num = -theta[kd]
        g[kd] = -1.0 / b
    elif atributo == "vaga_imediata":
        k1, k2 = termos.index("tem_vaga_imediata"), termos.index("log_vagas_imediatas_mais_1")
        num = theta[k1] + math.log(2.0) * theta[k2]
        g[k1], g[k2] = 1.0 / b, math.log(2.0) / b
    else:
        ka = termos.index(atributo)
        num = theta[ka]
        g[ka] = 1.0 / b
    g[kb] = -num / b ** 2
    return float(num / b), g


def bootstrap_dap(r: dict, atributos: list[str], log=print) -> dict:
    """Bootstrap de pares por conjunto de escolha: reamostra os conjuntos com reposição; partida no estimado."""
    At, Dt = comprimir(r["_A"], r["_D"])
    cheio = ajustar_cl(At, Dt, estat=_estat_tipos)          # partida em zero, como o M1
    dif = float(np.max(np.abs(cheio["theta"] - r["theta"])))
    if not cheio["convergiu"] or dif > 1e-7 or abs(cheio["ll"] - r["ll"]) > 1e-6:
        raise FalhaValidacao(f"desenho comprimido não reproduz o M1 (diferença {dif})")
    codigos = sorted(set(r["_D"]["grupos"]["cluster_conjunto"]))
    conj_g = pd.Index(codigos).get_indexer(Dt["conjunto_do_tipo"])
    Gc = len(codigos)
    rng = np.random.default_rng(SEMENTE_BOOT)
    # Todos os sorteios antes, em sequência: as réplicas podem rodar em paralelo sem mudar o resultado.
    mults = np.stack([np.bincount(rng.integers(0, Gc, Gc), minlength=Gc).astype(float) for _ in range(N_BOOT)])
    reps = np.full((N_BOOT, len(atributos)), np.nan)
    beta_b = np.full(N_BOOT, np.nan)
    motivo = np.full(N_BOOT, "", dtype=object)
    kb = r["termos"].index(TERMO_BOLSA)

    def replica(i: int) -> None:
        try:
            fit = ajustar_cl(At, Dt, w=mults[i][conj_g], theta0=r["theta"], estat=_estat_tipos)
        except (np.linalg.LinAlgError, FloatingPointError) as erro:
            motivo[i] = type(erro).__name__
            return
        if not fit["convergiu"]:
            motivo[i] = "nao_convergiu"
            return
        beta_b[i] = fit["theta"][kb]
        for j, a in enumerate(atributos):
            reps[i, j] = dap_vetor(r["termos"], fit["theta"], a)[0]

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=N_THREADS_M8) as ex:
        list(ex.map(replica, range(N_BOOT)))
    log(f"  bootstrap: {N_BOOT} réplicas")
    falhas = {k: int(v) for k, v in pd.Series(motivo[motivo != ""]).value_counts().sort_index().items()}
    ok = np.isfinite(beta_b)
    out = {"n_boot": N_BOOT, "n_validos": int(ok.sum()), "falhas": falhas, "semente": SEMENTE_BOOT,
           "desenho_comprimido": {"tipos": int(len(Dt["starts"])), "linhas": int(len(At)),
                                  "diferenca_maxima_theta_contra_M1": dif,
                                  "regra": "tipo = conjunto × município de origem (linhas idênticas); mesma "
                                           "verossimilhança do desenho por candidato (conferido)"},
           "fracao_beta_bolsa_nao_positivo": float(np.mean(beta_b[ok] <= 0)) if ok.any() else float("nan"),
           "beta_bolsa_percentis_2_5_97_5": [float(np.percentile(beta_b[ok], 2.5)), float(np.percentile(beta_b[ok], 97.5))]
           if ok.any() else [float("nan")] * 2, "por_atributo": {}}
    for j, a in enumerate(atributos):
        v = reps[ok, j]
        out["por_atributo"][a] = {"ic95_inf": float(np.percentile(v, 2.5)), "ic95_sup": float(np.percentile(v, 97.5)),
                                  "mediana": float(np.median(v))}
    return out


def linhas_dap(r: dict, atributos: list[str], boot: dict | None, estimando: dict[str, str]) -> list[dict]:
    out = []
    for a in atributos:
        base = {"natureza_dos_dados": NATUREZA, "estatuto": ESTATUTO, "estimando": estimando[a], "modelo": r["modelo"],
                "ciclo": r["ciclo"], "amostra": r["amostra"], "atributo": a, "formula": DAP_DEF[a][0],
                "definicao": DAP_DEF[a][1], "unidade": "R$ mil por mês", "n_candidatos": r.get("n_candidatos"),
                "g_conjuntos": r.get("G_conj")}
        if not r["ok"]:
            out.append({**base, "status": r["status"], "dap": np.nan, "ep_delta": np.nan, "ic95_delta_inf": np.nan,
                        "ic95_delta_sup": np.nan, "ic95_boot_inf": np.nan, "ic95_boot_sup": np.nan,
                        "n_boot": np.nan, "n_boot_validos": np.nan, "fracao_boot_beta_bolsa_nao_positivo": np.nan,
                        "nota": r["nota"]})
            continue
        d, g = dap_vetor(r["termos"], r["theta"], a)
        ep = math.sqrt(max(float(g @ r["V_conj"] @ g), 0.0))
        linha = {**base, "status": "EXECUTADO", "dap": d, "ep_delta": ep, "ic95_delta_inf": d - Z95 * ep,
                 "ic95_delta_sup": d + Z95 * ep, "ic95_boot_inf": np.nan, "ic95_boot_sup": np.nan, "n_boot": np.nan,
                 "n_boot_validos": np.nan, "fracao_boot_beta_bolsa_nao_positivo": np.nan,
                 "nota": "delta com a matriz de cluster por conjunto; sem teste de zero (P1b, P1c)"}
        if boot is not None:
            pa = boot["por_atributo"][a]
            linha.update({"ic95_boot_inf": pa["ic95_inf"], "ic95_boot_sup": pa["ic95_sup"], "n_boot": boot["n_boot"],
                          "n_boot_validos": boot["n_validos"],
                          "fracao_boot_beta_bolsa_nao_positivo": boot["fracao_beta_bolsa_nao_positivo"],
                          "nota": _juntar(linha["nota"], f"bootstrap de pares por conjunto de escolha ({boot['n_boot']} "
                                                         f"réplicas, semente {boot['semente']}), IC percentil")})
        else:
            linha["nota"] = _juntar(linha["nota"], "bootstrap só no modelo principal (M1)")
        out.append(linha)
    return out


# ---------------------------------------------------------------------------
# P1g: ponte P1 → P2
# ---------------------------------------------------------------------------

def saltos_previstos(theta: np.ndarray, r: dict, janelas: list[dict]) -> np.ndarray:
    """Para cada janela: média (peso de kernel triangular) sobre as células da janela de E[N_j | bolsa do lado de
    cima] − E[N_j | bolsa do lado de baixo], mantidas as demais células (logit: P_ij' = e'/(S − e + e'))."""
    A, D = r["_A"], r["_D"]
    kb = r["termos"].index(TERMO_BOLSA)
    st, grp = D["starts"], D["grp"]
    v = A @ theta
    vmax = np.maximum.reduceat(v, st)
    e = np.exp(v - vmax[grp])
    S = np.add.reduceat(e, st)[grp]
    out = np.empty(len(janelas))
    for i, janela in enumerate(janelas):
        linhas = janela["linhas"]
        bolsa = A[linhas, kb]
        e0 = e[linhas]
        eh = e0 * np.exp(theta[kb] * (janela["bolsa_alta"] - bolsa))
        el = e0 * np.exp(theta[kb] * (janela["bolsa_baixa"] - bolsa))
        S0 = S[linhas]
        dP = eh / (S0 - e0 + eh) - el / (S0 - e0 + el)
        dN = np.bincount(janela["pos_celula"], weights=dP, minlength=len(janela["peso"]))
        out[i] = float((janela["peso"] * dN).sum() / janela["peso"].sum())
    return out


def jacobiano_numerico(f, theta: np.ndarray) -> np.ndarray:
    """Diferença central, passo como o do E9 (`gradiente_numerico`), para uma função vetorial."""
    cols = []
    for k in range(len(theta)):
        h = 1e-5 * max(1.0, abs(theta[k]))
        tp, tm = theta.copy(), theta.copy()
        tp[k] += h
        tm[k] -= h
        cols.append((f(tp) - f(tm)) / (2 * h))
    return np.column_stack(cols)


def janelas_p1g(r: dict, dados: dict) -> dict[tuple[str, str], dict]:
    """Células com |IVS − corte| ≤ h, por ciclo e corte; bolsas dos dois lados do corte pelo mapa das faixas."""
    D = r["_D"]
    conj = D["conj"]
    mapa = dados["mapa"]
    lados = {300: (mapa["FAIXA 3"], mapa["FAIXA 2"]), 400: (mapa["FAIXA 2"], mapa["FAIXA 1"])}
    out = {}
    for ciclos in [(1,), (2,), (3,), CICLOS]:
        rot_c = "+".join(map(str, ciclos))
        partes = {}
        for c in CORTES:
            x = conj["s_mil"].to_numpy() - c
            peso_cel = np.where((np.abs(x) <= H_RDD) & conj["ciclo"].isin(ciclos).to_numpy(),
                                1.0 - np.abs(x) / H_RDD, 0.0)
            partes[c] = peso_cel
        for corte in [300, 400, EMPILHADO]:
            cs = CORTES if corte == EMPILHADO else (corte,)
            linhas, pos_cel, pesos, ba, bb = [], [], [], [], []
            n = 0
            for c in cs:
                cel_j = np.flatnonzero(partes[c] > 0)
                mapa_pos = {j: n + i for i, j in enumerate(cel_j)}
                m = np.isin(D["cel"], cel_j)
                lin = np.flatnonzero(m)
                linhas.append(lin)
                pos_cel.append(np.array([mapa_pos[j] for j in D["cel"][lin]], dtype=int))
                pesos.append(partes[c][cel_j])
                ba.append(np.full(len(lin), lados[c][1]))
                bb.append(np.full(len(lin), lados[c][0]))
                n += len(cel_j)
            out[(rot_c, str(corte))] = {"linhas": np.concatenate(linhas), "pos_celula": np.concatenate(pos_cel),
                                        "peso": np.concatenate(pesos), "bolsa_alta": np.concatenate(ba),
                                        "bolsa_baixa": np.concatenate(bb), "n_celulas": int(n)}
    return out


def rdd_celulas(celulas: pd.DataFrame, y: str, ciclos: tuple[int, ...], corte) -> dict:
    """RDD por célula como no A3 (variante só curso × ciclo): grupo = ciclo × corte, salto comum, efeito fixo de
    curso × ciclo, CR1 por município, h = 0,050, kernel triangular."""
    cs = CORTES if corte == EMPILHADO else (corte,)
    blocos = []
    for k in ciclos:
        d = celulas[celulas["ciclo"] == k]
        for c in cs:
            b = d.copy()
            b["corte_mil"] = c
            b["grupo"] = f"c{k}_{c}"
            blocos.append(b)
    a = pd.concat(blocos, ignore_index=True)
    return L.rd_empilhado(a["s_mil"].to_numpy(), a[y].to_numpy(dtype=float), a["corte_mil"].to_numpy(),
                          grupo=a["grupo"].to_numpy(), h_mil=H_RDD, cluster=a["co_ibge"].to_numpy(),
                          ids_unidade=a["co_ibge"].to_numpy(), efeitos_fixos=a["fe_curso_ciclo"].to_numpy())


def p1g(r1: dict, dados: dict) -> tuple[list[dict], dict]:
    """Salto previsto por M1 (delta, cluster por conjunto) e saltos observados (RDD por célula)."""
    conj = r1["_D"]["conj"]
    D = r1["_D"]
    janelas = janelas_p1g(r1, dados)
    # Contagens observadas por célula.
    v = pd.read_parquet(V_CELULA)
    if not (v["natureza_dos_dados"] == NATUREZA).all():
        raise FalhaValidacao("outcomes_V_celula com natureza diferente de EMPIRICO")
    cel_all = dados["conj"][["ciclo", "co_cnes_7d", "cod_curso", "co_ibge", "s_mil"]].merge(
        v[["ciclo", "co_cnes_7d", "cod_curso", "n_cand_1a_opcao"]], on=["ciclo", "co_cnes_7d", "cod_curso"],
        how="left", validate="one_to_one")
    if cel_all["n_cand_1a_opcao"].isna().any():
        raise FalhaValidacao("célula do conjunto sem contagem em outcomes_V_celula")
    cel_all["fe_curso_ciclo"] = [f"c{k}_curso{int(c):02d}" for k, c in zip(cel_all["ciclo"], cel_all["cod_curso"])]
    G = D["grupos"]
    esc_cel = D["cel"][D["esc"][G["posto"].to_numpy() == 1]]
    cont = np.bincount(esc_cel, minlength=len(conj))
    cel_p1 = conj[["ciclo", "co_cnes_7d", "cod_curso", "co_ibge", "s_mil"]].copy()
    cel_p1["n_cand_1a_opcao_amostra_p1"] = cont.astype(float)
    cel_p1["fe_curso_ciclo"] = [f"c{k}_curso{int(c):02d}" for k, c in zip(cel_p1["ciclo"], cel_p1["cod_curso"])]
    # Conferência: a RDD de todos os candidatos reproduz o A3 (variante só curso × ciclo) gravado em NA.
    na = pd.read_csv(NA_ESTIMATIVAS, dtype={"ciclo": str, "corte": str})
    conf = {}
    linhas = []
    chaves = list(janelas)
    lista = [janelas[k] for k in chaves]
    f = lambda th: saltos_previstos(th, r1, lista)  # noqa: E731
    s_all = f(r1["theta"])
    J = jacobiano_numerico(f, r1["theta"])
    for i, ((rot_c, corte), jan) in enumerate(janelas.items()):
        ciclos = tuple(int(x) for x in rot_c.split("+"))
        corte_v = EMPILHADO if corte == EMPILHADO else int(corte)
        s = float(s_all[i])
        g = J[i]
        ep = math.sqrt(max(float(g @ r1["V_conj"] @ g), 0.0))
        comum = {"estimando": "P1g", "ciclo": rot_c, "amostra": "P1 (G1 com origem)", "termo": f"corte_{corte}",
                 "unidade": "candidatos de 1ª opção por célula (salto no corte)"}
        linhas.append(_linha(**comum, modelo="M1_previsto", descricao_modelo="salto previsto por M1 mudando só a bolsa "
                             "das células da janela (demais células fixas)", tipo_linha="salto_previsto_modelo",
                             coef=s, ep_cluster_conjunto=ep, ic95_inf=s - Z95 * ep, ic95_sup=s + Z95 * ep,
                             n_conjuntos=r1["n_conjuntos"], n_candidatos=r1["n_candidatos"],
                             nota=(f"{jan['n_celulas']} células na janela h = {H_RDD / 1000:.3f}, peso de kernel "
                                   "triangular; candidatos fixos (sem resposta de entrada); IC delta com a matriz de "
                                   "cluster por conjunto do M1")))
        for y, amostra, conjunto in (("n_cand_1a_opcao", "todos os candidatos (outcomes_V_celula)", cel_all),
                                     ("n_cand_1a_opcao_amostra_p1", "candidatos da amostra P1", cel_p1)):
            rr = rdd_celulas(conjunto, y, ciclos, corte_v)
            linhas.append(_linha(**{**comum, "amostra": amostra}, modelo="RDD_celula",
                                 descricao_modelo="RDD por célula (A3, só curso × ciclo): salto comum, efeito fixo de "
                                                  "curso × ciclo, CR1 por município, h = 0,050",
                                 tipo_linha="salto_rdd_observado", coef=rr.get("tau"), ep_cluster_conjunto=np.nan,
                                 ic95_inf=rr.get("ic95_inf"), ic95_sup=rr.get("ic95_sup"), p=rr.get("p_valor"),
                                 n_linhas_candidato_celula=rr.get("n_obs"),
                                 nota=_juntar(rr.get("nota", ""), f"EP {rr.get('ep'):.6g} (cluster por município, "
                                              f"{rr.get('n_clusters')} municípios); a coluna ep_cluster_conjunto não "
                                              "se aplica" if rr.get("ep") is not None else "")))
            if y == "n_cand_1a_opcao":
                alvo = na[(na["outcome_id"] == "A3_CAND_1A_OPCAO") & (na["variante"] == "so_curso_x_ciclo") &
                          (na["ciclo"] == rot_c) & (na["corte"] == ("empilhado" if corte == EMPILHADO else
                                                                     f"{int(corte) / 1000:.3f}".replace(".", ",")))]
                if len(alvo) == 1:
                    conf[f"{rot_c}|{corte}"] = {"tau": rr.get("tau"), "tau_A3": float(alvo.iloc[0]["tau"]),
                                                "igual": bool(abs(rr.get("tau") - float(alvo.iloc[0]["tau"])) < 1e-8)}
    return linhas, {"conferencia_A3": conf, "celulas_amostra_p1": int(len(cel_p1)), "celulas_todas": int(len(cel_all))}


# ---------------------------------------------------------------------------
# Descritivos do T1.3 (estrutura dos conjuntos por ciclo; não usa a escolha)
# ---------------------------------------------------------------------------

def descritivos_ciclo(D: dict) -> dict:
    conj, G = D["conj"], D["grupos"]
    g1 = G[G["posto"] == 1]
    out = {}
    for k in CICLOS:
        c = conj[conj["ciclo"] == k]
        gk = g1[g1["ciclo"] == k]
        tam = D["tam"][(G["posto"] == 1).to_numpy() & (G["ciclo"] == k).to_numpy()]
        out[str(k)] = {"candidatos": int(len(gk)), "conjuntos": int(c["id_conjunto_escolha"].nunique()),
                       "celulas": int(len(c)), "alternativas_por_candidato_media": float(tam.mean()),
                       "fracao_celulas_com_vaga_imediata": float(c["tem_vaga_imediata"].mean()),
                       "fracao_celulas_por_faixa": {f: float((c["faixa_anunciada"] == f).mean())
                                                    for f in ("FAIXA 3", "FAIXA 2", "FAIXA 1")},
                       "fracao_candidatos_sem_pontuacao": float(gk["pontuacao"].isna().mean())}
    return out


# ---------------------------------------------------------------------------
# Figuras (sem texto embutido além de eixos e legenda; o "Como ler" vai no doc e no resumo)
# ---------------------------------------------------------------------------

ROTULO_DAP = {"distancia_100km_a_menos": "100 km a menos", "mesma_uf": "mesma UF da origem",
              "capital": "capital (vs. interior próximo de polo)", "vaga_imediata": "1 vaga imediata"}


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "p1"})
    return plt


def figuras(dap: pd.DataFrame, est: pd.DataFrame) -> list[dict]:
    plt = _plt()
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    figs = []
    # DAP do M1.
    d = dap[(dap["modelo"] == "M1") & (dap["status"] == "EXECUTADO")].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    y = np.arange(len(d))[::-1]
    for yi, r in zip(y, d.itertuples()):
        if np.isfinite(r.ic95_boot_inf):
            ax.plot([r.ic95_boot_inf, r.ic95_boot_sup], [yi, yi], color="#8fb4e3", lw=1.2)
        ax.plot([r.ic95_delta_inf, r.ic95_delta_sup], [yi, yi], color="#2a78d6", lw=3.2)
        ax.plot([r.dap], [yi], "o", color="#1b3f73", ms=6)
    ax.axvline(0, color="#52514e", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([ROTULO_DAP[a] for a in d["atributo"]])
    ax.set_xlabel("R$ mil por mês de bolsa equivalentes (M1, ciclos 1–3)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", color="#e6e5e0", lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG_DAP, dpi=150, metadata={"Software": None})
    plt.close(fig)
    figs.append({"arquivo": rel(FIG_DAP), "como_ler": COMO_LER[FIG_DAP.name],
                 "descricao": "DAP do M1 (P1b, P1c) com IC delta e bootstrap"})
    # Beta por ciclo (M5) e empilhado (M1).
    sel = est[(est["termo"] == TERMO_BOLSA) & (((est["modelo"] == "M5") & (est["tipo_linha"] == "coeficiente")) |
                                                ((est["modelo"] == "M1") & (est["ciclo"] == EMPILHADO)))]
    ordem = ["1", "2", "3", EMPILHADO]
    sel = sel.set_index("ciclo").loc[ordem].reset_index()
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    x = np.arange(len(sel))
    for xi, r in zip(x, sel.itertuples()):
        cor = "#1b3f73" if r.ciclo == EMPILHADO else "#2a78d6"
        ax.plot([xi, xi], [r.ic95_inf, r.ic95_sup], color=cor, lw=2.4)
        ax.plot([xi], [r.coef], "o", color=cor, ms=6)
    ax.axhline(0, color="#52514e", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(["ciclo 1", "ciclo 2", "ciclo 3", "ciclos 1–3"])
    ax.set_ylabel("coeficiente da bolsa por R$ 1 mil")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e6e5e0", lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG_CICLO, dpi=150, metadata={"Software": None})
    plt.close(fig)
    figs.append({"arquivo": rel(FIG_CICLO), "como_ler": COMO_LER[FIG_CICLO.name],
                 "descricao": "coeficiente da bolsa por ciclo (M5) e empilhado (M1), IC 95% cluster por conjunto"})
    # Ponte P1g, ciclos 1+2+3: 0,300, 0,400 e empilhado.
    p = est[(est["estimando"] == "P1g") & (est["ciclo"] == "1+2+3")]
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    cortes = ["corte_300", "corte_400", f"corte_{EMPILHADO}"]
    series = [("M1_previsto", None, "#2a78d6", "previsto pelo modelo (M1, só a bolsa)", -0.2),
              ("RDD_celula", "candidatos da amostra P1", "#eb6834", "observado: amostra P1 (RDD)", 0.0),
              ("RDD_celula", "todos os candidatos (outcomes_V_celula)", "#1baf7a", "observado: todos os candidatos (RDD)", 0.2)]
    for modelo, amostra, cor, rotulo, dx in series:
        s = p[p["modelo"] == modelo]
        if amostra is not None:
            s = s[s["amostra"] == amostra]
        s = s.set_index("termo").loc[cortes]
        xs = np.arange(len(cortes)) + dx
        ax.errorbar(xs, s["coef"], yerr=[s["coef"] - s["ic95_inf"], s["ic95_sup"] - s["coef"]], fmt="o", color=cor,
                    capsize=3, lw=1.6, label=rotulo)
    ax.axhline(0, color="#52514e", lw=0.8)
    ax.set_xticks(np.arange(len(cortes)))
    ax.set_xticklabels(["0,300", "0,400", "cortes empilhados"])
    ax.set_ylabel("candidatos de 1ª opção por célula")
    ax.legend(frameon=False, fontsize=8, loc="best")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e6e5e0", lw=0.5)
    fig.tight_layout()
    fig.savefig(FIG_PONTE, dpi=150, metadata={"Software": None})
    plt.close(fig)
    figs.append({"arquivo": rel(FIG_PONTE), "como_ler": COMO_LER[FIG_PONTE.name],
                 "descricao": "P1g: salto previsto por M1 contra a RDD por célula, ciclos 1–3"})
    return figs


# ---------------------------------------------------------------------------
# Documento 57a (gerado inteiro pelo script a partir das saídas)
# ---------------------------------------------------------------------------

def _n(v, casas: int = 3, sinal: bool = False) -> str:
    if v is None or (isinstance(v, float) and not math.isfinite(v)) or pd.isna(v):
        return "—"
    t = f"{float(v):+.{casas}f}" if sinal else f"{float(v):.{casas}f}"
    return t.replace("-", "−").replace(".", ",")


def _p(v) -> str:
    if v is None or pd.isna(v):
        return "—"
    return "< 0,001" if v < 0.001 else _n(v, 3)


def _peq(v) -> str:
    """'p < 0,001' ou 'p = 0,xxx' (para frases)."""
    t = _p(v)
    return f"p {t}" if t.startswith("<") else f"p = {t}"


def _ic(lo, hi, casas: int = 3) -> str:
    return f"[{_n(lo, casas)}; {_n(hi, casas)}]"


def _int(v) -> str:
    return "—" if v is None or pd.isna(v) else f"{int(v)}"


def _tab(cab: list[str], linhas: list[list[str]]) -> str:
    out = ["| " + " | ".join(cab) + " |", "|" + "|".join("---" for _ in cab) + "|"]
    out += ["| " + " | ".join(x) + " |" for x in linhas]
    return "\n".join(out)


def _sel(est: pd.DataFrame, **f) -> pd.DataFrame:
    m = np.ones(len(est), dtype=bool)
    for k, v in f.items():
        m &= est[k].astype(str).to_numpy() == str(v)
    return est[m]


def _um(est: pd.DataFrame, **f) -> pd.Series:
    s = _sel(est, **f)
    if len(s) != 1:
        raise FalhaValidacao(f"esperava 1 linha para {f}, achei {len(s)}")
    return s.iloc[0]


def gerar_doc(est: pd.DataFrame, dap: pd.DataFrame, resumo: dict) -> str:
    a = resumo["amostra"]
    L_ = [
        "# 57a. Resultados do P1: quanto a bolsa anunciada move a escolha de onde trabalhar",
        "",
        "> **Gerado por** `scripts/rdd_bolsa/25_escolha_dap.py` a partir de `output/rdd_bolsa/P1_*`; não editar à "
        "mão (o teste `tests/test_escolha_dap.py` confere que este arquivo é igual ao gerado).<br>",
        "> **Protocolo:** [`52_protocolo_P1_escolha_dap.md`](52_protocolo_P1_escolha_dap.md), congelado em "
        "19/10/2026 antes de estimar; estatuto `PROTOCOLO_52_POS_RESULTADO` (o E9, a X4 e a X5 já tinham sido "
        "vistos).<br>",
        "> **Saídas:** `output/rdd_bolsa/P1_estimativas.csv`, `P1_dap.csv`, `P1_resumo.json` e `P1_figuras/`; toda "
        "linha tem `natureza_dos_dados = EMPIRICO`.<br>",
        "> **Fora deste bloco:** os cenários contrafactuais do T1.6 (doc 51, §3), que só rodam depois da auditoria.<br>",
        "> **Para a síntese:** este documento é a seção P1 que o protocolo manda pôr no doc 57 (ver desvios).",
        "",
        "## 1. O que se mede e o que não se pode dizer",
        "",
        "- **Estimando principal (P1a).** O peso da bolsa anunciada (por R$ 1 mil por mês) na escolha da 1ª opção "
        "do candidato **dentro do conjunto de vagas abertas** do seu curso e ciclo, com a distância e os atributos "
        "de origem controlados.",
        "- **Identificação.** A bolsa muda só nos cortes do IVS 2010 oficial (0,300 e 0,400); o IVS entra como uma "
        "curva contínua com dobras nos cortes e sem salto. O peso da bolsa sai, portanto, dos saltos da bolsa nos "
        "cortes, com a vulnerabilidade contínua controlada.",
        "- **O que o contraste mede.** O pacote do corte (bolsa +R$ 5 mil e outras regras federais que mudam no "
        "mesmo IVS, auditoria 18) e o incentivo marginal da bolsa. Não mede a participação no PMM-E nem o efeito "
        "total do Agora Tem Especialistas.",
        "- **O que não diz.** Nada sobre quem não se candidatou, nem sobre o número total de candidatos: é uma "
        "realocação entre vagas já abertas.",
        "- **DAP (P1b, P1c).** Razão de coeficientes: quanto de bolsa mensal equivale a um atributo da vaga. É uma "
        "estimativa com intervalo, sem teste de zero.",
        "",
        "**Ameaças declaradas (protocolo, §4):**",
        "- seleção pela ligação: os candidatos sem município de origem no G1 ficam fora (seção 2);",
        "- a origem é o município do estabelecimento em que o candidato tinha vínculo médico, não a residência;",
        "- o conjunto de escolha supõe que o candidato viu todas as células do curso;",
        "- outras políticas nos mesmos cortes podem mudar atributos não observados da vaga (pacote).",
        "",
        "## 2. Amostra",
        "",
        "<!-- P1:amostra:inicio -->",
        tabela_amostra(resumo),
        "<!-- P1:amostra:fim -->",
        "",
        "## 3. Leitura em linguagem simples",
        "",
        "<!-- P1:leitura:inicio -->",
        leitura(est, dap, resumo),
        "<!-- P1:leitura:fim -->",
        "",
        "## 4. P1a: coeficiente da bolsa em todas as especificações",
        "",
        "Coeficiente por R$ 1 mil por mês de bolsa, IC 95% e p com o EP de cluster por conjunto de escolha (curso × "
        "ciclo); ao lado, o p pela t com G − 1 graus de liberdade e os EPs de máxima verossimilhança e por "
        "candidato. Holm só na linha principal (M1, ciclos empilhados), família de um teste: o p de Holm é o próprio p.",
        "",
        "<!-- P1:bolsa:inicio -->",
        tabela_bolsa(est),
        "<!-- P1:bolsa:fim -->",
        "",
        "## 5. P1b e P1c: disposição a pagar",
        "",
        "<!-- P1:dap:inicio -->",
        tabela_dap(dap),
        "<!-- P1:dap:fim -->",
        "",
        "## 6. Atributos do modelo principal (M1)",
        "",
        "<!-- P1:m1:inicio -->",
        tabela_m1(est),
        "<!-- P1:m1:fim -->",
        "",
        "## 7. P1d: por que só o ciclo 2? (T1.3)",
        "",
        "<!-- P1:ciclos:inicio -->",
        tabela_ciclos(est, resumo),
        "<!-- P1:ciclos:fim -->",
        "",
        "Leituras candidatas, todas a relatar (doc 51, T1.3): (i) informação, porque a grade de faixas foi "
        "publicada com o quadro no ciclo 1; (ii) número de opções e composição dos candidatos; (iii) proporção de "
        "vagas imediatas. A tabela de estrutura acima descreve (ii) e (iii) sem usar a escolha; nenhuma das "
        "leituras é testada aqui.",
        "",
        "## 8. P1e e P1f: heterogeneidade",
        "",
        "<!-- P1:heterogeneidade:inicio -->",
        tabela_heterogeneidade(est),
        "<!-- P1:heterogeneidade:fim -->",
        "",
        "## 9. P1g: ponte com o preenchimento (T1.5)",
        "",
        "O modelo prevê, para as células perto do corte, quantos candidatos de 1ª opção a mais a célula teria se só "
        "a sua bolsa subisse um degrau, com os candidatos e as outras células fixos. A RDD por célula mede o salto "
        "observado. A leitura é de consistência, não um teste novo; o salto observado inclui também quem passou a "
        "se candidatar ou deixou de se candidatar, e o previsto não.",
        "",
        "<!-- P1:p1g:inicio -->",
        tabela_p1g(est),
        "<!-- P1:p1g:fim -->",
        "",
        "## 10. Figuras",
        "",
        "Nenhuma figura traz texto de leitura dentro da imagem; o \"Como ler\" fica aqui e no campo `como_ler` de "
        "`P1_resumo.json`.",
        "",
        "<!-- P1:figuras:inicio -->",
        tabela_figuras(resumo),
        "<!-- P1:figuras:fim -->",
        "",
        "## 11. Desvios e decisões de implementação",
        "",
        "<!-- P1:desvios:inicio -->",
        tabela_desvios(resumo),
        "<!-- P1:desvios:fim -->",
        "",
        "## 12. Limites",
        "",
        "- **Escolha condicional.** O coeficiente descreve como quem se candidatou ordena as vagas abertas; não "
        "mede entrada no programa nem oferta líquida de especialistas.",
        "- **Poucos conjuntos.** Há 56 conjuntos de escolha (curso × ciclo); o EP com cluster por conjunto é "
        "impreciso, e por isso o p pela t com G − 1 graus de liberdade vai ao lado.",
        "- **IIA.** O logit condicional supõe independência de alternativas irrelevantes; o aninhado (M9) e o "
        "misto (M8) relaxam isso em parte.",
        "- **Origem não é residência.** A distância vai do município do estabelecimento de origem no CNES ao da vaga.",
        "- **DAP com bolsa fraca.** Quando o coeficiente da bolsa é pequeno perto do seu erro, a razão fica "
        "instável: o IC delta é simétrico por construção e o do bootstrap mostra a assimetria.",
        "",
    ]
    del a
    return "\n".join(L_)


def tabela_amostra(resumo: dict) -> str:
    a = resumo["amostra"]
    linhas = [["candidatos com linha de 1ª opção (E9)", *[_int(a["r1_por_ciclo"][str(k)]) for k in CICLOS],
               _int(sum(a["r1_por_ciclo"].values()))]]
    for m, por in a["exclusoes"].items():
        linhas.append([f"fora: {m}", *[_int(por.get(str(k), 0)) for k in CICLOS], _int(sum(por.values()))])
    linhas.append(["**amostra P1 (1ª opção)**", *[_int(a["p1_por_ciclo"][str(k)]) for k in CICLOS],
                   _int(sum(a["p1_por_ciclo"].values()))])
    linhas.append(["2ª opção na amostra P1 (M7)", *[_int(a["r2_por_ciclo"].get(str(k), 0)) for k in CICLOS],
                   _int(sum(a["r2_por_ciclo"].values()))])
    t = _tab(["Item", "Ciclo 1", "Ciclo 2", "Ciclo 3", "Total"], linhas)
    extra = [
        "",
        f"- Células do conjunto de escolha: {a['celulas_e9']} no E9; {a['celulas_p1']} na amostra P1 (fora "
        f"{a['celulas_sem_cir']} células de município sem região de saúde na tabela oficial: "
        f"{', '.join(a['municipios_sem_cir'])}).",
        f"- Linhas candidato × célula no M1: {a['linhas_m1']}; conjuntos de escolha: {a['conjuntos_m1']}.",
        f"- 2ª opção fora por cair em célula sem região de saúde: {a['r2_fora_sem_cir']}.",
        f"- Distância das células escolhidas igual à do G1: {a['conferencia_distancia']['escolhas_conferidas']} "
        f"escolhas, diferença máxima {_n(a['conferencia_distancia']['diferenca_maxima_km'], 9)} km.",
        f"- Reprodução do E9 (amostra completa, ciclos empilhados): coeficiente {_n(a['reproducao_E9']['coef'], 6)} "
        f"contra {_n(a['reproducao_E9']['coef_E9'], 6)} gravado; EP {_n(a['reproducao_E9']['ep'], 6)} contra "
        f"{_n(a['reproducao_E9']['ep_E9'], 6)}.",
    ]
    return t + "\n" + "\n".join(extra)


def tabela_bolsa(est: pd.DataFrame) -> str:
    s = est[(est["termo"].isin([TERMO_BOLSA, f"media_{TERMO_BOLSA}"])) & (est["tipo_linha"] == "coeficiente")]
    ordem = ["E9_amostra_completa", "M0", "M1", "M2", "M3", "M4", "M5", "M6_nota", "M6_municipio", "M6_curso", "M7",
             "M8", "M9"]
    linhas = []
    for m in ordem:
        for r in s[s["modelo"] == m].itertuples():
            if m.startswith("M6") and r.termo != TERMO_BOLSA:
                continue
            nota = r.status if r.status != "EXECUTADO" else ""
            linhas.append([m, str(r.ciclo), r.descricao_modelo if m != "M8" else ROTULO_MODELO["M8"] + " (média)",
                           _int(r.n_candidatos), _n(r.coef, 4), _ic(r.ic95_inf, r.ic95_sup, 4), _p(r.p),
                           _p(r.p_t_g_menos_1), _n(r.ep_mle, 4), _n(r.ep_cluster_candidato, 4),
                           _p(r.p_holm) if bool(r.entra_holm) else "—", nota])
    t = _tab(["Modelo", "Ciclo", "Especificação", "Candidatos", "Coef.", "IC 95%", "p", "p (t, G−1)", "EP MV",
              "EP candidato", "p Holm", "Situação"], linhas)
    m3 = _sel(est, modelo="M3")
    if len(m3):
        t += f"\n\nM3 não executado: {m3.iloc[0]['nota']}."
    return t + "\n\nAs inclinações por grupo do M6 estão na seção 8."


def tabela_dap(dap: pd.DataFrame) -> str:
    linhas = []
    for r in dap.itertuples():
        linhas.append([r.modelo, str(r.ciclo), ROTULO_DAP[r.atributo], _n(r.dap, 2), _ic(r.ic95_delta_inf, r.ic95_delta_sup, 2),
                       _ic(r.ic95_boot_inf, r.ic95_boot_sup, 2) if pd.notna(r.ic95_boot_inf) else "—",
                       r.status if r.status != "EXECUTADO" else ""])
    t = _tab(["Modelo", "Ciclo", "Atributo", "DAP (R$ mil/mês)", "IC 95% delta", "IC 95% bootstrap", "Situação"], linhas)
    m1 = dap[(dap["modelo"] == "M1")].iloc[0]
    defs = "\n".join(f"- **{ROTULO_DAP[a]}:** {DAP_DEF[a][1]} (`{DAP_DEF[a][0]}`)." for a in DAP_DEF)
    boot = (f"\n\nBootstrap de pares por conjunto de escolha: {_int(m1['n_boot_validos'])} réplicas válidas de "
            f"{_int(m1['n_boot'])}; fração das réplicas com coeficiente da bolsa ≤ 0: "
            f"{_n(m1['fracao_boot_beta_bolsa_nao_positivo'], 3)}.")
    aviso = ("Leitura: os intervalos acima são largos, e a maioria contém zero no M1. Por ciclo (M5), onde o coeficiente "
             "da bolsa é próximo de zero, a razão explode e não tem leitura econômica; a DAP não é um preço de mercado.")
    return t + boot + "\n\n" + aviso + "\n\n" + defs


def tabela_m1(est: pd.DataFrame) -> str:
    s = _sel(est, modelo="M1", ciclo=EMPILHADO, tipo_linha="coeficiente")
    linhas = [[r.termo, _n(r.coef, 4), _ic(r.ic95_inf, r.ic95_sup, 4), _p(r.p), _n(r.ep_mle, 4)] for r in s.itertuples()]
    return (_tab(["Termo", "Coef.", "IC 95% (cluster por conjunto)", "p", "EP MV"], linhas) +
            "\n\nSpline do IVS em unidades de 0,1 de IVS a partir de 0,300; estrato de referência: interior próximo "
            "de polo; macrorregião de referência: Sudeste; distância por 100 km.")


def tabela_ciclos(est: pd.DataFrame, resumo: dict) -> str:
    linhas = []
    for k in ("1", "2", "3"):
        r = _um(est, modelo="M5", ciclo=k, termo=TERMO_BOLSA, tipo_linha="coeficiente")
        linhas.append([f"ciclo {k}", _int(r["n_candidatos"]), _n(r["coef"], 4), _ic(r["ic95_inf"], r["ic95_sup"], 4),
                       _p(r["p"]), _n(r["q_bky"], 3)])
    w = _um(est, modelo="M5", tipo_linha="wald_igualdade_ciclos")
    t = _tab(["Ciclo", "Candidatos", "Coef. da bolsa", "IC 95%", "p", "q BKY"], linhas)
    t += (f"\n\nWald da igualdade do coeficiente da bolsa nos três ciclos (χ², {_int(w['gl'])} gl, ciclos tratados "
          f"como amostras independentes): {_n(w['estatistica_wald'], 2)}, {_peq(w['p'])}, q BKY = {_n(w['q_bky'], 3)}.")
    d = resumo["descritivos_ciclo"]
    lin = [[f"ciclo {k}", _int(d[k]["candidatos"]), _int(d[k]["conjuntos"]), _int(d[k]["celulas"]),
            _n(d[k]["alternativas_por_candidato_media"], 1), _n(d[k]["fracao_celulas_com_vaga_imediata"], 3),
            " / ".join(_n(d[k]["fracao_celulas_por_faixa"][f], 3) for f in ("FAIXA 3", "FAIXA 2", "FAIXA 1")),
            _n(d[k]["fracao_candidatos_sem_pontuacao"], 3)] for k in ("1", "2", "3")]
    t += "\n\nEstrutura dos conjuntos por ciclo (amostra P1; descritivo, sem usar a escolha):\n\n" + _tab(
        ["Ciclo", "Candidatos", "Conjuntos", "Células", "Alternativas por candidato (média)",
         "Fração de células com vaga imediata", "Fração de células nas faixas 3 / 2 / 1",
         "Fração de candidatos sem pontuação"], lin)
    return t


def tabela_heterogeneidade(est: pd.DataFrame) -> str:
    linhas = []
    for m in ("M6_nota", "M6_municipio", "M6_curso"):
        for r in _sel(est, modelo=m).itertuples():
            if r.tipo_linha not in ("inclinacao_do_grupo", "interacao", "wald_igualdade"):
                continue
            deg = bool(r.inferencia_cluster_degenerada)
            if r.tipo_linha == "wald_igualdade":
                termo = f"Wald (χ², {_int(r.gl)} gl) = {_n(r.estatistica_wald, 2)}"
                linhas.append([m, termo, "—", "—", _p(r.p_mle if deg else r.p), _n(r.q_bky, 3) if bool(r.entra_bky) else "—",
                               "MV (cluster degenerado)" if deg else "cluster por conjunto"])
                continue
            lo, hi, p_ = (r.coef - Z95 * r.ep_mle, r.coef + Z95 * r.ep_mle, r.p_mle) if deg else (r.ic95_inf, r.ic95_sup, r.p)
            linhas.append([m, r.termo, _n(r.coef, 4), _ic(lo, hi, 4), _p(p_), _n(r.q_bky, 3) if bool(r.entra_bky) else "—",
                           "MV (cluster degenerado)" if deg else "cluster por conjunto"])
    t = _tab(["Modelo", "Termo", "Coef.", "IC 95%", "p", "q BKY", "Inferência"], linhas)
    t += ("\n\n`bolsa_mil|grupo` é a inclinação da bolsa no grupo; `bolsa_x_grupo` é a diferença para o grupo de "
          "base. Na dimensão curso, o termo de cada curso só varia nos conjuntos do curso (no máximo 3 clusters): o "
          "EP por cluster é degenerado, a linha usa o EP de máxima verossimilhança e fica fora do BKY, como na X4.")
    linhas = []
    for r in _sel(est, modelo="M8").itertuples():
        linhas.append([r.termo, _n(abs(r.coef) if str(r.termo).startswith("desvio_") else r.coef, 4),
                       _ic(r.ic95_inf, r.ic95_sup, 4) if not str(r.termo).startswith("desvio_") else "—",
                       _n(r.ep_cluster_conjunto, 4), _p(r.p), _n(r.q_bky, 3) if bool(r.entra_bky) else "—", r.status])
    linhas = [x for x in linhas if x[0].startswith(("media_", "desvio_"))] or [["—", "—", "—", "—", "—", "—", "—"]]
    t += "\n\n**P1f, logit misto (M8).**\n\n" + _tab(["Parâmetro", "Estimativa", "IC 95%", "EP (cluster por conjunto)",
                                                     "p", "q BKY", "Situação"], linhas)
    m8 = _sel(est, modelo="M8")
    if len(m8) and m8.iloc[0]["status"] != "EXECUTADO":
        t += f"\n\nM8: {m8.iloc[0]['nota']}."
    elif len(m8):
        t += "\n\nDesvios em valor absoluto; o IC do desvio não é relatado porque H0: desvio = 0 fica na fronteira."
    m9 = _sel(est, modelo="M9")
    lam = m9[m9["termo"] == "lambda"]
    if len(lam):
        r = lam.iloc[0]
        t += (f"\n\n**M9, logit aninhado por região de saúde.** lambda = {_n(r['coef'], 3)} "
              f"(IC 95% {_ic(r['ic95_inf'], r['ic95_sup'], 3)}; situação {r['status']}); 1 = logit condicional, menos "
              "de 1 = mais substituição entre vagas da mesma região de saúde.")
        t1 = m9[m9["tipo_linha"] == "teste_lambda_igual_1"]
        if len(t1):
            t += f" Wald de lambda = 1: {_peq(t1.iloc[0]['p'])}."
    return t


def tabela_p1g(est: pd.DataFrame) -> str:
    s = _sel(est, estimando="P1g")
    linhas = []
    for rot_c in ("1+2+3", "1", "2", "3"):
        for corte in ("300", "400", EMPILHADO):
            sub = s[(s["ciclo"].astype(str) == rot_c) & (s["termo"] == f"corte_{corte}")]
            prev = sub[sub["modelo"] == "M1_previsto"].iloc[0]
            obs_p1 = sub[(sub["modelo"] == "RDD_celula") & (sub["amostra"] == "candidatos da amostra P1")].iloc[0]
            obs_all = sub[(sub["modelo"] == "RDD_celula") & (sub["amostra"] != "candidatos da amostra P1")].iloc[0]
            rc = {"300": "0,300", "400": "0,400", EMPILHADO: "empilhado"}[corte]
            linhas.append([rot_c, rc, _n(prev["coef"], 3, True), _ic(prev["ic95_inf"], prev["ic95_sup"], 3),
                           _n(obs_p1["coef"], 3, True), _ic(obs_p1["ic95_inf"], obs_p1["ic95_sup"], 3),
                           _n(obs_all["coef"], 3, True), _ic(obs_all["ic95_inf"], obs_all["ic95_sup"], 3)])
    return _tab(["Ciclos", "Corte", "Previsto por M1", "IC 95% (delta)", "Observado, amostra P1", "IC 95%",
                 "Observado, todos os candidatos", "IC 95%"], linhas)


def tabela_figuras(resumo: dict) -> str:
    return _tab(["Arquivo", "O que mostra", "Como ler"],
                [[f"`{Path(f['arquivo']).name}`", f["descricao"], f["como_ler"]] for f in resumo["figuras"]])


def tabela_desvios(resumo: dict) -> str:
    def data_br(iso: str) -> str:
        a, m, d = iso.split("-")
        return f"{d}/{m}/{a}"
    return "\n".join(f"{i}. **{d['item']}** ({data_br(d['data'])}). {d['situacao']} *Resolução:* {d['resolucao']}"
                     for i, d in enumerate(resumo["desvios"], start=1))


def leitura(est: pd.DataFrame, dap: pd.DataFrame, resumo: dict) -> str:
    m1 = _um(est, modelo="M1", ciclo=EMPILHADO, termo=TERMO_BOLSA, tipo_linha="coeficiente")
    m0 = _um(est, modelo="M0", ciclo=EMPILHADO, termo=TERMO_BOLSA, tipo_linha="coeficiente")
    e9 = _um(est, modelo="E9_amostra_completa", ciclo=EMPILHADO, termo=TERMO_BOLSA, tipo_linha="coeficiente")

    def frase_ic(lo, hi) -> str:
        return ("o intervalo de 95% exclui zero" if (lo > 0 or hi < 0) else
                "o intervalo de 95% contém zero: os dados não distinguem o efeito de zero com a precisão relatada")
    txt = [
        f"**P1a.** No modelo principal (M1, ciclos 1–3, {_int(m1['n_candidatos'])} candidatos), cada R$ 1 mil por mês "
        f"de bolsa anunciada muda a utilidade da vaga em {_n(m1['coef'], 4, True)} (IC 95% {_ic(m1['ic95_inf'], m1['ic95_sup'], 4)}; "
        f"{_peq(m1['p'])}; {_peq(m1['p_t_g_menos_1'])} pela t com G − 1 gl); {frase_ic(m1['ic95_inf'], m1['ic95_sup'])}. "
        f"Sem a distância, na mesma amostra (M0): {_n(m0['coef'], 4, True)} (IC {_ic(m0['ic95_inf'], m0['ic95_sup'], 4)}); "
        f"na amostra completa do E9: {_n(e9['coef'], 4, True)} (IC {_ic(e9['ic95_inf'], e9['ic95_sup'], 4)}).",
    ]
    outras = []
    for mod, termo in (("M2", TERMO_BOLSA), ("M4", TERMO_BOLSA), ("M7", TERMO_BOLSA), ("M8", f"media_{TERMO_BOLSA}"),
                       ("M9", TERMO_BOLSA)):
        sub = est[(est["modelo"] == mod) & (est["ciclo"] == EMPILHADO) & (est["termo"] == termo) &
                  (est["status"] == "EXECUTADO")]
        if len(sub):
            outras.append((mod, float(sub.iloc[0]["coef"]), float(sub.iloc[0]["ic95_inf"]), float(sub.iloc[0]["ic95_sup"])))
    if outras:
        exclui = [m for m, _, lo, hi in outras if lo > 0 or hi < 0]
        contem = [m for m, _, lo, hi in outras if not (lo > 0 or hi < 0)]
        coefs = [m1["coef"]] + [c for _, c, _, _ in outras]
        txt[0] += (f" Nas outras especificações do empilhado, o IC de 95% exclui zero em {', '.join(exclui) or 'nenhuma'} "
                   f"e contém zero em {', '.join(contem) or 'nenhuma'}; o coeficiente varia de {_n(min(coefs), 4, True)} a "
                   f"{_n(max(coefs), 4, True)}. A leitura de P1a é sensível à especificação: só o M1 é a principal e o "
                   f"único com Holm, e as demais são relatadas, não escolhidas.")
    d = dap[dap["modelo"] == "M1"].set_index("atributo")
    partes = []
    for a in DAP_DEF:
        r = d.loc[a]
        partes.append(f"{ROTULO_DAP[a]}: {_n(r['dap'], 2, True)} (delta {_ic(r['ic95_delta_inf'], r['ic95_delta_sup'], 2)}; "
                      f"bootstrap {_ic(r['ic95_boot_inf'], r['ic95_boot_sup'], 2)})")
    n_zero_delta = sum(1 for a in DAP_DEF if d.loc[a, "ic95_delta_inf"] <= 0 <= d.loc[a, "ic95_delta_sup"])
    n_zero_boot = sum(1 for a in DAP_DEF if d.loc[a, "ic95_boot_inf"] <= 0 <= d.loc[a, "ic95_boot_sup"])
    txt.append("**P1b e P1c (R$ mil por mês de bolsa equivalentes, M1).** " + "; ".join(partes) + ". **Os intervalos "
               f"são largos: o IC contém zero em {n_zero_delta} dos {len(DAP_DEF)} atributos pelo delta e em "
               f"{n_zero_boot} pelo bootstrap.** A DAP é uma razão: com o coeficiente da bolsa perto de zero (o IC do "
               "M1 contém zero), o intervalo fica largo e assimétrico, e o ponto não é um preço. A bolsa só varia entre "
               "R$ 10 e R$ 20 mil nos dados, então valores muito maiores que isso são extrapolação da razão, não algo "
               "que a escolha observada mostre.")
    w = _um(est, modelo="M5", tipo_linha="wald_igualdade_ciclos")
    cic = []
    for k in ("1", "2", "3"):
        r = _um(est, modelo="M5", ciclo=k, termo=TERMO_BOLSA, tipo_linha="coeficiente")
        cic.append(f"ciclo {k}: {_n(r['coef'], 4, True)} (IC {_ic(r['ic95_inf'], r['ic95_sup'], 4)})")
    txt.append("**P1d.** Por ciclo (M5): " + "; ".join(cic) + f". Wald da igualdade: {_peq(w['p'])} "
               f"(q BKY = {_n(w['q_bky'], 3)}).")
    het = []
    for r in est[(est["entra_bky"].astype(bool)) & (est["estimando"] == "P1e")].itertuples():
        het.append(f"{r.modelo} {r.termo}: {_n(r.coef, 4, True) if pd.notna(r.coef) else 'Wald'} "
                   f"({_peq(r.p)}, q BKY = {_n(r.q_bky, 3)})")
    txt.append("**P1e.** " + "; ".join(het) + ". Diferença com q BKY ≥ 0,05 não é evidência de heterogeneidade.")
    m8 = _sel(est, modelo="M8")
    if len(m8) and m8.iloc[0]["status"] == "EXECUTADO":
        sb = _um(est, modelo="M8", termo=f"desvio_{TERMO_BOLSA}")
        mb = _um(est, modelo="M8", termo=f"media_{TERMO_BOLSA}")
        txt.append(f"**P1f.** No logit misto (M8), a média do coeficiente da bolsa é {_n(mb['coef'], 4, True)} "
                   f"(IC {_ic(mb['ic95_inf'], mb['ic95_sup'], 4)}) e o desvio entre candidatos, {_n(abs(sb['coef']), 4)} "
                   f"({_peq(sb['p'])}, q BKY = {_n(sb['q_bky'], 3)}).")
    elif len(m8):
        txt.append(f"**P1f.** O logit misto (M8) ficou {m8.iloc[0]['status']}: {m8.iloc[0]['nota']}.")
    g = _sel(est, estimando="P1g", ciclo="1+2+3", termo=f"corte_{EMPILHADO}")
    prev = g[g["modelo"] == "M1_previsto"].iloc[0]
    obs = g[(g["modelo"] == "RDD_celula") & (g["amostra"] == "candidatos da amostra P1")].iloc[0]
    txt.append(f"**P1g.** Nos cortes empilhados (ciclos 1–3), o modelo prevê {_n(prev['coef'], 3, True)} candidato de "
               f"1ª opção por célula (IC {_ic(prev['ic95_inf'], prev['ic95_sup'], 3)}) quando só a bolsa sobe um degrau; "
               f"a RDD por célula, na mesma amostra de candidatos, observa {_n(obs['coef'], 3, True)} "
               f"(IC {_ic(obs['ic95_inf'], obs['ic95_sup'], 3)}). É leitura de consistência, não teste.")
    if prev["coef"] * obs["coef"] < 0:
        sobrepoe = max(prev["ic95_inf"], obs["ic95_inf"]) <= min(prev["ic95_sup"], obs["ic95_sup"])
        ambos_zero = all(x["ic95_inf"] <= 0 <= x["ic95_sup"] for x in (prev, obs))
        txt[-1] += (" Os sinais são opostos"
                    + (", mas os dois intervalos se sobrepõem" if sobrepoe else "")
                    + (" e ambos contêm zero" if ambos_zero else "")
                    + ": o salto observado não confirma nem refuta o modelo, e o P1g não é usado para validar nem para "
                      "rejeitar o M1. O observado inclui quem passou a se candidatar ou deixou de se candidatar; o "
                      "previsto não.")
    txt.append("Tudo acima é escolha condicional a candidatar-se, dentro das vagas abertas; o contraste no corte mede o "
               "pacote do corte e o incentivo marginal da bolsa, não a participação no PMM-E.")
    return "\n\n".join(txt)


# ---------------------------------------------------------------------------
# Desvios e decisões
# ---------------------------------------------------------------------------

DESVIOS = [
    {"data": "2026-10-23", "item": "Local do resultado",
     "situacao": "O §5 do protocolo diz 'doc 57, seção P1'; o doc 57 é a síntese da onda 5 (doc 51, §5), e outros "
                 "blocos escrevem em paralelo.",
     "resolucao": "Resultados em docs/06_execucao/57a_resultados_P1_escolha.md, gerado inteiro pelo script, para "
                  "entrar na síntese 57 (mesma solução do P5, doc 57e)."},
    {"data": "2026-10-23", "item": "M3 não executado",
     "situacao": MOTIVO_M3 + ".",
     "resolucao": "Linhas do M3 com status NAO_EXECUTADO e o motivo; nenhuma distância aproximada."},
    {"data": "2026-10-23", "item": "Células e origens sem região de saúde",
     "situacao": "A 'mesma região de saúde' de M1 exige a CIR da origem e da célula; um município do quadro "
                 "(células nos três ciclos) e um município de origem não estão na tabela oficial do TabNet.",
     "resolucao": "Como na X5: as células desse município saem do conjunto de escolha de todos os modelos da "
                  "amostra P1 (M0 incluído), e saem os candidatos cuja 1ª opção estava nelas ou cuja origem não tem "
                  "região; a 2ª opção nessas células sai do M7. Contagens na seção 2; nada imputado."},
    {"data": "2026-10-23", "item": "Capital em M1",
     "situacao": "O E9 já tem o estrato A2 com base na capital; acrescentar um indicador de capital seria colinear.",
     "resolucao": "Em M1 a base do estrato passa a ser o interior próximo de polo; o termo 'capital' é capital contra "
                  "essa base, mantidos porte (log da população) e macrorregião. É reparametrização: o coeficiente da "
                  "bolsa não muda por isso."},
    {"data": "2026-10-23", "item": "Vaga imediata na DAP",
     "situacao": "O E9 tem 'tem vaga imediata' e log(vagas imediatas + 1); mudar o indicador sem mudar o log é "
                 "impossível.",
     "resolucao": "DAP da vaga imediata = célula com 1 vaga imediata contra só cadastro reserva: "
                  "[β(tem) + ln 2 · β(log)] / β(bolsa)."},
    {"data": "2026-10-23", "item": "M4",
     "situacao": "A macrorregião é função da UF.",
     "resolucao": "Em M4 o efeito fixo de UF da vaga substitui a macrorregião (UF de base: a de mais células)."},
    {"data": "2026-10-23", "item": "M6",
     "situacao": "O §3 lista três interações sem dizer se entram juntas.",
     "resolucao": "Um modelo por dimensão (como na X4). Tercis da nota dentro do ciclo, sobre os candidatos de 1ª "
                  "opção da amostra P1 com pontuação, empate no corte para baixo, sem pontuação = grupo próprio. "
                  "Curso: cursos com ≥ 100 candidatos de 1ª opção na amostra empilhada, base = o de mais candidatos; "
                  "inferência por cluster degenerada (o termo do curso só varia nos conjuntos dele), EP de máxima "
                  "verossimilhança relatado e linhas fora do BKY, como na X4."},
    {"data": "2026-10-23", "item": "BKY",
     "situacao": "O §4 manda BKY nas secundárias com p-valor sem listar as linhas.",
     "resolucao": "Família única: β da bolsa por ciclo e Wald entre ciclos (P1d); termos de interação da nota e do "
                  "município de origem e Wald da nota (P1e); média da bolsa e desvios da bolsa e da distância no "
                  "logit misto, se convergir (P1f). p com cluster por conjunto."},
    {"data": "2026-10-23", "item": "M8 (logit misto)",
     "situacao": "500 sorteios por candidato em cerca de um milhão de linhas candidato × célula; o prompt do agente "
                 "pede não forçar além de 30 min.",
     "resolucao": f"Gradiente analítico, teto determinístico de {MAX_AVAL_M8} avaliações da verossimilhança (≈ 30 min "
                  "nesta máquina) para que duas execuções deem o mesmo resultado; sem convergência, status "
                  "NAO_CONVERGIU com o motivo."},
    {"data": "2026-10-23", "item": "Polimento por Newton no M8 e no M9",
     "situacao": "Na primeira execução completa o L-BFGS-B parou pelo critério de redução relativa da função com "
                 "gradiente máximo de 1,2e-3 (M8) e 3,6e-4 (M9), acima da tolerância de 1e-4; as duas linhas saíram "
                 "NAO_CONVERGIU. Nenhum coeficiente dessas execuções foi lido para decidir a mudança.",
     "resolucao": f"Até {POLIMENTO_NEWTON} passos de Newton com a hessiana numérica do gradiente analítico depois do "
                  "L-BFGS-B, como o polimento da X5; mesma tolerância (1e-4), mesma amostra, mesma especificação. Se "
                  "ainda assim não convergir, a linha fica NAO_CONVERGIU."},
    {"data": "2026-10-23", "item": "M9 (logit aninhado)",
     "situacao": "A X5 usou gradiente numérico; aqui as linhas são do candidato (distância e origem variam por "
                 "candidato).",
     "resolucao": "Ninhos = CIR da célula dentro do conjunto de cada candidato; gradiente analítico (conferido contra "
                  "o numérico no teste sintético); lambda limitado a [0,001; 50] como na X5."},
    {"data": "2026-10-23", "item": "P1g",
     "situacao": "O §3 manda comparar com a RDD por célula de n_cand_1a_opcao, mas o modelo só prevê os candidatos "
                 "da amostra P1.",
     "resolucao": "Relatadas as duas RDDs (todos os candidatos, conferida contra o A3 gravado, e só a amostra P1); o "
                  "salto previsto é a média, com peso de kernel triangular nas células da janela, da diferença de "
                  "candidatos esperados com a bolsa do lado de cima e do lado de baixo do corte."},
    {"data": "2026-10-23", "item": "T1.4 (RDD da nota média)",
     "situacao": "O doc 51 lista a RDD da nota média dos alocados e dos candidatos (F4) no T1.4; o protocolo 52 não a "
                 "inclui.",
     "resolucao": "Não reestimada aqui (o F4 está no E6); o T1.4 entra pela interação bolsa × tercil da nota (M6)."},
]


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def conferir_E9(dados: dict) -> dict:
    """E9 principal na amostra completa (todos os candidatos de 1ª opção, conjunto com as células sem CIR)."""
    conj = dados["conj"].reset_index(drop=True)
    r1 = dados["r1_todos"]
    D = montar_desenho(conj, r1, None, dados, com_origem=False)
    X = matriz_modelo(D, dados, "E9_amostra_completa")
    r = estimar(X, D, modelo="E9_amostra_completa", ciclo=EMPILHADO, amostra="E9 completa")
    e9 = pd.read_csv(E9_ESTIMATIVAS, dtype={"ciclo": str})
    alvo = e9[(e9.ciclo == EMPILHADO) & (e9.modelo == E9.MODELO_COND) & (e9.conjunto == "principal") &
              (e9.especificacao == E9.ESPEC_PRINCIPAL) & (e9.termo == TERMO_BOLSA)].iloc[0]
    k = r["termos"].index(TERMO_BOLSA)
    b, ep = float(r["theta"][k]), math.sqrt(r["V_conj"][k, k])
    ok = bool(np.isclose(b, alvo.coef, rtol=1e-6, atol=1e-9) and np.isclose(ep, alvo.ep_cluster_conjunto, rtol=1e-6))
    if not ok:
        raise FalhaValidacao(f"E9 não reproduzido: {b} {ep} contra {alvo.coef} {alvo.ep_cluster_conjunto}")
    return r, {"coef": b, "ep": ep, "coef_E9": float(alvo.coef), "ep_E9": float(alvo.ep_cluster_conjunto), "igual": ok}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--atualizar-doc", action="store_true", help="só regrava o doc 57a a partir das saídas")
    args = ap.parse_args(argv)
    if args.atualizar_doc:
        atualizar_doc()
        return 0
    t0 = time.time()

    def log(m: str) -> None:
        print(f"[{time.time() - t0:7.0f}s] {m}", flush=True)

    dados = carregar()
    r_e9, rep_e9 = conferir_E9(dados)
    log("E9 reproduzido")
    conj = dados["conj_p1"]
    D = montar_desenho(conj, dados["r1_p1"], None, dados)
    conf_dist = conferir_distancias(D)
    De = montar_desenho(conj, dados["r1_p1"], dados["r2_p1"], dados)
    conferir_distancias(De)
    log(f"desenho: {len(D['cel'])} linhas, {len(D['starts'])} candidatos; explodido: {len(De['cel'])} linhas")

    est: list[dict] = []
    res: dict[str, dict] = {}
    est += linhas_modelo(r_e9, "sensibilidade", termos=[TERMO_BOLSA],
                         nota_extra="reproduz E9_estimativas.csv (principal, empilhado)")
    for m in ("M0", "M1", "M2", "M4"):
        X = matriz_modelo(D, dados, m)
        r = estimar(X, D, modelo=m, ciclo=EMPILHADO, amostra="P1 (G1 com origem)")
        res[m] = r
        papel = {"M0": "sensibilidade", "M1": "P1a", "M2": "sensibilidade", "M4": "sensibilidade"}[m]
        est += linhas_modelo(r, papel)
        log(f"{m}: ok={r['ok']} it={r.get('iteracoes')}")
    r1 = res["M1"]
    if not r1["ok"]:
        raise FalhaValidacao("M1 não convergiu")
    # M3 não executado.
    for t in r1["termos"]:
        est.append(_linha(estimando="sensibilidade", modelo="M3", descricao_modelo=ROTULO_MODELO["M3"],
                          ciclo=EMPILHADO, amostra="P1 (G1 com origem)", tipo_linha="coeficiente",
                          termo=t if t != TERMO_DIST else "distancia_origem_mais_proxima_100km", status="NAO_EXECUTADO",
                          nota=MOTIVO_M3))
    # M5 por ciclo.
    bs, vs = [], []
    for k in CICLOS:
        Dk = montar_desenho(conj[conj["ciclo"] == k].reset_index(drop=True),
                            dados["r1_p1"][dados["r1_p1"]["ciclo"] == k], None, dados)
        rk = estimar(matriz_modelo(Dk, dados, "M1"), Dk, modelo="M5", ciclo=str(k), amostra="P1 (G1 com origem)")
        res[f"M5_{k}"] = rk
        est += linhas_modelo(rk, "P1d")
        kb = rk["termos"].index(TERMO_BOLSA)
        bs.append(rk["theta"][kb])
        vs.append(rk["V_conj"][kb, kb])
        log(f"M5 ciclo {k}: ok={rk['ok']}")
    for ln in est:
        if ln["modelo"] == "M5" and ln["termo"] == TERMO_BOLSA:
            ln["entra_bky"] = True
    Rw = np.array([[1.0, -1.0, 0.0], [0.0, 1.0, -1.0]])
    d = Rw @ np.array(bs)
    Wm = float(d @ np.linalg.solve(Rw @ np.diag(vs) @ Rw.T, d))
    est.append(_linha(estimando="P1d", modelo="M5", descricao_modelo="Wald: β da bolsa igual nos ciclos 1, 2 e 3",
                      ciclo="1,2,3", amostra="P1 (G1 com origem)", tipo_linha="wald_igualdade_ciclos",
                      termo="wald_bolsa_igual_entre_ciclos", estatistica_wald=Wm, gl=2, p=float(stats.chi2.sf(Wm, 2)),
                      entra_bky=True, nota="EP cluster por conjunto de cada ciclo; ciclos tratados como amostras "
                                           "independentes (candidatos distintos; a mesma célula pode se repetir)"))
    # M6.
    G1g = D["grupos"]
    rot = pd.Series("sem_pontuacao", index=G1g.index, dtype=object)
    cortes_tercil = {}
    for k in CICLOS:
        m = (G1g["ciclo"] == k) & G1g["pontuacao"].notna()
        t, q = X45.tercis(G1g.loc[m, "pontuacao"])
        rot.loc[m] = [f"tercil{int(v)}" for v in t]
        cortes_tercil[str(k)] = q
    rot_linha_nota = rot.to_numpy()[D["grp"]]
    ncurso = G1g.groupby("cod_curso").size()
    grandes = sorted(int(c) for c, n in ncurso.items() if n >= MIN_CAND_CURSO)
    rot_curso = np.array([f"curso{int(c):02d}" if int(c) in grandes else "demais_cursos" for c in G1g["cod_curso"]],
                         dtype=object)
    cont_curso = pd.Series(rot_curso).value_counts()
    base_curso = sorted(cont_curso.index, key=lambda g: (-int(cont_curso[g]), g))[0]
    dims = {
        "M6_nota": ("tercil1", rot_linha_nota, ["tercil1", "tercil2", "tercil3", "sem_pontuacao"], False),
        "M6_municipio": ("fora_do_municipio", np.where(D["mesmo_municipio"] == 1, "mesmo_municipio", "fora_do_municipio"),
                         ["fora_do_municipio", "mesmo_municipio"], False),
        "M6_curso": (base_curso, rot_curso[D["grp"]], [f"curso{k:02d}" for k in grandes] + ["demais_cursos"], True),
    }
    for nome, (base, rot_l, ordem, degenerada) in dims.items():
        X = matriz_modelo(D, dados, "M1")
        bolsa = X[TERMO_BOLSA].to_numpy()
        presentes = [g for g in ordem if g in set(rot_l)]
        outros = [g for g in presentes if g != base]
        for g in outros:
            X[f"bolsa_x_{g}"] = bolsa * (rot_l == g)
        r = estimar(X, D, modelo=nome, ciclo=EMPILHADO, amostra="P1 (G1 com origem)")
        res[nome] = r
        c = _comuns(r, "P1e")
        cont_g = pd.Series(rot_l[D["esc"]]).value_counts()
        nota_deg = ("dimensão curso: o termo de cada curso só varia nos conjuntos do curso; EP e p por cluster não "
                    "são confiáveis; usar o EP de máxima verossimilhança; fora do BKY" if degenerada else "")
        for g in presentes:
            a = vetor(r, TERMO_BOLSA)
            if g != base:
                a = a + vetor(r, f"bolsa_x_{g}")
            est.append(_linha(**c, tipo_linha="inclinacao_do_grupo", termo=f"bolsa_mil|{g}", **combinacao(r, a),
                              log_verossimilhanca=r["ll"], iteracoes=r["iteracoes"], inferencia_cluster_degenerada=degenerada,
                              unidade="coeficiente por R$ 1 mil/mês",
                              nota=_juntar(f"inclinação da bolsa no grupo {g} ({int(cont_g.get(g, 0))} escolhas)", nota_deg)))
        R = []
        for g in outros:
            a = vetor(r, f"bolsa_x_{g}")
            R.append(a)
            est.append(_linha(**c, tipo_linha="interacao", termo=f"bolsa_x_{g}", **combinacao(r, a),
                              log_verossimilhanca=r["ll"], iteracoes=r["iteracoes"], inferencia_cluster_degenerada=degenerada,
                              entra_bky=not degenerada, unidade="diferença de inclinação por R$ 1 mil/mês",
                              nota=_juntar(f"diferença da inclinação do grupo {g} para a do grupo {base}", nota_deg)))
        if len(R) > 1:
            W, gl, pw = wald(r, np.array(R))
            Wm_, _, pm_ = wald(r, np.array(R), "V_mle")
            est.append(_linha(**c, tipo_linha="wald_igualdade", termo="wald_inclinacoes_iguais", estatistica_wald=W, gl=gl,
                              p=pw, p_mle=pm_, inferencia_cluster_degenerada=degenerada, entra_bky=not degenerada,
                              nota=_juntar(f"Wald de H0: inclinações iguais nos {len(presentes)} grupos; χ² com "
                                           f"cluster por conjunto (MV: {Wm_:.4g})", nota_deg)))
        for t in r["termos"]:
            if t == TERMO_BOLSA or t.startswith("bolsa_x_"):
                continue
            est.append(_linha(**c, tipo_linha="coeficiente_controle", termo=t, **combinacao(r, vetor(r, t)),
                              log_verossimilhanca=r["ll"], iteracoes=r["iteracoes"], nota="controle do modelo"))
        log(f"{nome}: ok={r['ok']} grupos={presentes}")
    # M7.
    X = matriz_modelo(De, dados, "M1")
    r7 = estimar(X, De, modelo="M7", ciclo=EMPILHADO, amostra="P1 (G1 com origem), 1ª e 2ª opção")
    res["M7"] = r7
    est += linhas_modelo(r7, "sensibilidade", nota_extra="logit explodido: conjunto do posto 2 = curso da 2ª opção, "
                                                       "sem a célula da 1ª quando os cursos coincidem")
    log(f"M7: ok={r7['ok']}")
    # Holm em P1a.
    for ln in est:
        if ln["modelo"] == "M1" and ln["termo"] == TERMO_BOLSA and ln["ciclo"] == EMPILHADO:
            ln["entra_holm"] = True
    # DAP e bootstrap.
    atributos = list(DAP_DEF)
    estim_dap = {"distancia_100km_a_menos": "P1b", "mesma_uf": "P1c", "capital": "P1c", "vaga_imediata": "P1c"}
    boot = bootstrap_dap(r1, atributos, log=log)
    dap = linhas_dap(r1, atributos, boot, estim_dap)
    for m in ("M4", "M7"):
        dap += linhas_dap(res[m], atributos, None, estim_dap)
    for k in CICLOS:
        dap += linhas_dap(res[f"M5_{k}"], atributos, None, estim_dap)
    log("DAP e bootstrap prontos")
    # M9.
    cir = dados["mapa_cir"]
    cir_linha = pd.factorize(cir.reindex(D["conj"]["co_ibge"].to_numpy()[D["cel"]]).to_numpy())[0]
    r9 = estimar_aninhado(r1, cir_linha)
    r9.update({"ciclo": EMPILHADO, "amostra": "P1 (G1 com origem)", "n_candidatos": r1["n_candidatos"],
               "n_grupos": r1["n_grupos"], "n_linhas": r1["n_linhas"], "n_conjuntos": r1["n_conjuntos"]})
    res["M9"] = r9
    c9 = _comuns(r9, "sensibilidade")
    for t in r9["termos"]:
        if r9["ok"]:
            cb = combinacao(r9, vetor(r9, t))
            if t == "lambda":
                cb.update({"p": np.nan, "p_t_g_menos_1": np.nan, "p_mle": np.nan})
            est.append(_linha(**c9, tipo_linha="coeficiente", termo=t, **cb, log_verossimilhanca=r9["ll"],
                              iteracoes=r9["iteracoes"], nota=_juntar(r9["nota"], "p de H0: lambda = 0 não relatado"
                                                                      if t == "lambda" else "")))
        else:
            est.append(_linha(**c9, tipo_linha="coeficiente", termo=t, coef=float(r9["theta"][r9["termos"].index(t)]),
                              log_verossimilhanca=r9["ll"], nota=r9["nota"]))
    if r9["ok"]:
        k = r9["termos"].index("lambda")
        lam = float(r9["theta"][k])
        ep = math.sqrt(r9["V_conj"][k, k])
        est.append(_linha(**c9, tipo_linha="teste_lambda_igual_1", termo="lambda_menos_1", coef=lam - 1,
                          ep_cluster_conjunto=ep, ep_mle=math.sqrt(r9["V_mle"][k, k]),
                          ep_cluster_candidato=math.sqrt(r9["V_cand"][k, k]), ic95_inf=lam - 1 - Z95 * ep,
                          ic95_sup=lam - 1 + Z95 * ep, p=float(2 * stats.norm.sf(abs((lam - 1) / ep))),
                          estatistica_wald=r9["lr_contra_M1"], gl=1,
                          g_conjuntos=r9["G_conj"], g_candidatos=r9["G_cand"],
                          nota=f"Wald de H0: lambda = 1 (cluster por conjunto); estatistica_wald guarda a razão de "
                               f"verossimilhança contra M1 (p LR = {stats.chi2.sf(max(r9['lr_contra_M1'], 0), 1):.4g})"))
    log(f"M9: ok={r9['ok']} ({r9.get('segundos')} s)")
    # M8.
    r8 = estimar_misto(r1, r1["termos"])
    r8.update({"ciclo": EMPILHADO, "amostra": "P1 (G1 com origem)", "n_candidatos": r1["n_candidatos"],
               "n_grupos": r1["n_grupos"], "n_linhas": r1["n_linhas"], "n_conjuntos": r1["n_conjuntos"]})
    res["M8"] = r8
    c8 = _comuns(r8, "P1f")
    for t in r8["termos"]:
        if r8["ok"]:
            cb = combinacao(r8, vetor(r8, t))
            alvo = t in (f"media_{TERMO_BOLSA}", f"desvio_{TERMO_BOLSA}", f"desvio_{TERMO_DIST}")
            if t.startswith("desvio_"):
                cb["coef"] = abs(cb["coef"])
                cb["ic95_inf"], cb["ic95_sup"] = np.nan, np.nan
            est.append(_linha(**c8, tipo_linha="coeficiente", termo=t, **cb, log_verossimilhanca=r8["ll"],
                              iteracoes=r8.get("iteracoes"), entra_bky=alvo, nota=r8["nota"]))
        else:
            est.append(_linha(**c8, tipo_linha="coeficiente", termo=t, nota=r8["nota"]))
    log(f"M8: ok={r8['ok']} ({r8.get('segundos')} s, {r8.get('avaliacoes')} avaliações)")
    # P1g.
    lin_g, info_g = p1g(r1, dados)
    est += lin_g
    log("P1g pronto")

    est = pd.DataFrame(est)[COLUNAS_EST]
    est["p_holm"] = np.nan
    mh = est["entra_holm"].astype(bool)
    est.loc[mh, "p_holm"] = L.holm(est.loc[mh, "p"].to_numpy())
    mb = est["entra_bky"].astype(bool) & est["p"].notna()
    est["q_bky"] = np.nan
    est.loc[mb, "q_bky"] = L.qvalores_bky(est.loc[mb, "p"].to_numpy())
    sem_nota = est[est["coef"].isna() & ~est["tipo_linha"].str.startswith("wald") & (est["nota"].fillna("") == "")]
    if len(sem_nota):
        raise FalhaValidacao(f"{len(sem_nota)} linhas sem coeficiente e sem nota")
    dap = pd.DataFrame(dap)
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    est.to_csv(OUT_EST, index=False, float_format="%.10g")
    dap.to_csv(OUT_DAP, index=False, float_format="%.10g")
    est = ler_est()
    dap = ler_dap()
    figs = figuras(dap, est)
    for f in figs:
        f["sha256"] = sha256(ROOT / f["arquivo"])

    r1g = dados["r1"]
    excl = {}
    for x in dados["exclusoes"].itertuples():
        excl.setdefault(x.motivo_exclusao_p1, {})[str(int(x.ciclo))] = int(x.candidatos)
    amostra = {
        "r1_por_ciclo": {str(k): int((dados["r1_todos"]["ciclo"] == k).sum()) for k in CICLOS},
        "exclusoes": excl,
        "p1_por_ciclo": {str(k): int((dados["r1_p1"]["ciclo"] == k).sum()) for k in CICLOS},
        "r2_por_ciclo": {str(k): int((dados["r2_p1"]["ciclo"] == k).sum()) for k in CICLOS},
        "r2_fora_sem_cir": dados["r2_fora_sem_cir"],
        "candidatos_sem_linha_de_1a_opcao": dados["sem_r1"],
        "celulas_e9": int(len(dados["conj"])), "celulas_p1": int(len(conj)),
        "celulas_sem_cir": int(len(dados["celulas_sem_cir"])),
        "municipios_sem_cir": sorted({c["co_ibge"] for c in dados["celulas_sem_cir"]}),
        "linhas_m1": r1["n_linhas"], "conjuntos_m1": r1["n_conjuntos"], "linhas_m7": r7["n_linhas"],
        "conferencia_distancia": conf_dist, "reproducao_E9": rep_e9,
        "taxa_ligacao_g1_com_origem": {k: v.get("com_municipio_de_origem") if isinstance(v, dict) else None
                                       for k, v in (dados["g1_resumo"].get("taxas", {}).get(REGRA_G1, {}) or {}).items()},
    }
    del r1g
    m1row = est[(est["modelo"] == "M1") & (est["termo"] == TERMO_BOLSA)].iloc[0]
    resumo = {
        "etapa": "P1_escolha_dap",
        "natureza_dos_dados": NATUREZA,
        "estatuto": ESTATUTO,
        "data_execucao": DATA_EXECUCAO,
        "script": rel(Path(__file__)),
        "protocolo": {"arquivo": rel(PROTOCOLO_MD), "sha256": sha256(PROTOCOLO_MD), "tarefas": "T1.1–T1.5 (T1.6 fora)"},
        "estimando": ("P1a: coeficiente da bolsa anunciada (por R$ 1 mil/mês) na utilidade da 1ª opção, dentro do "
                      "conjunto de vagas abertas do curso e ciclo, ciclos 1–3 empilhados, com distância e atributos de "
                      "origem; identificado pelos saltos da bolsa nos cortes 0,300 e 0,400 com o IVS contínuo "
                      "controlado; mede o pacote do corte e o incentivo marginal, não a participação no PMM-E; nada diz "
                      "sobre quem não se candidatou"),
        "ameacas": ["seleção pela ligação (candidatos sem município de origem no G1 ficam fora)",
                    "origem = município do estabelecimento de vínculo médico na referência, não residência",
                    "o conjunto de escolha supõe que o candidato viu todas as células do curso",
                    "outras políticas nos mesmos cortes podem mudar atributos não observados da vaga (pacote)"],
        "resultado_principal": {"modelo": "M1", "coef_bolsa_por_mil": m1row["coef"],
                                "ic95": [m1row["ic95_inf"], m1row["ic95_sup"]], "p": m1row["p"],
                                "p_holm": m1row["p_holm"], "n_candidatos": m1row["n_candidatos"]},
        "inferencia": {"principal": "sanduíche com cluster por conjunto de escolha (curso × ciclo), fator G/(G−1)",
                       "adicionais": ["máxima verossimilhança", "cluster por candidato", "p pela t com G − 1 gl"],
                       "holm": "só em P1a (M1 empilhado, bolsa): família de um teste",
                       "bky": "família única: P1d (β por ciclo, Wald), P1e (interações da nota e do município, Wald da "
                              "nota), P1f (média da bolsa e desvios no M8, se convergir)",
                       "dap": "delta (cluster por conjunto) e bootstrap de pares por conjunto (percentil)"},
        "amostra": amostra,
        "tercis_nota": {"cortes": cortes_tercil, "regra": "dentro do ciclo, candidatos de 1ª opção da amostra P1 com "
                                                          "pontuação; empate no corte vai para baixo"},
        "cursos_m6": {"cursos_com_100": grandes, "base": base_curso,
                      "candidatos_por_curso": {str(int(k)): int(v) for k, v in ncurso.items()}},
        "bootstrap": boot,
        "m8": {k: v for k, v in r8.items() if not k.startswith(("V_", "_")) and k not in ("theta",)},
        "m9": {k: v for k, v in r9.items() if not k.startswith(("V_", "_")) and k not in ("theta",)},
        "p1g": info_g,
        "descritivos_ciclo": descritivos_ciclo(D),
        "convergencia": {m: {"ok": r["ok"], "status": r["status"], "iteracoes": r.get("iteracoes"),
                             "omitidas": r.get("omitidas", [])} for m, r in res.items()},
        "figuras": figs,
        "como_ler": {Path(f["arquivo"]).name: f["como_ler"] for f in figs},
        "desvios": DESVIOS,
        "entradas": [
            bloco_entrada(PROTOCOLO_MD, "protocolo 52 (somente lido)", "repositório", "2026-10-19", "§1–§6",
                          "documento", "-", "-"),
            bloco_entrada(E9.ESCOLHAS, "escolhas dos candidatos (1ª e 2ª opção) e pontuação",
                          "tarefa B (script 12)", "resultados da 1ª chamada dos ciclos 1–3",
                          f"{len(dados['cand'])} linhas", "candidato × opção", "ciclo, id_candidato, opcao_rank",
                          "postos 1 e 2"),
            bloco_entrada(E9.CONJ_PRINCIPAL, "conjunto de escolha principal (E9 §14)", "tarefa B (script 12)",
                          "quadros da 1ª chamada", f"{len(dados['conj']) + len(dados['diag_conj']['alternativas_retiradas_sem_ivs'])} "
                          "células", "célula CNES × curso × ciclo", "ciclo, co_cnes_7d, cod_curso",
                          "sem IVS oficial e sem CIR fora (listados)"),
            bloco_entrada(E9.IVS_OFICIAL, "IVS 2010 oficial (a08): spline e regra das faixas", "Ipea (a08)", "Censo 2010",
                          f"{len(dados['ivs'])} municípios", "município", "co_ibge", "co_ibge, ivs"),
            bloco_entrada(E9.GRADES_EDITAIS, "mapa faixa → bolsa (como no E9)", "editais (a03)", "2025–2026",
                          "3 faixas", "faixa", "faixa", "mapeamento_regras_por_edital"),
            bloco_entrada(E9.GRADE_2025, "conferência do mapa faixa → bolsa (como no E9)", "FAQ 3/2025 (a04)", "2025",
                          "3 faixas", "faixa", "faixa_atracao", "-"),
            bloco_entrada(E9.DICIONARIO, "dicionário da tarefa B (SHA-256 das tabelas de escolha conferido)",
                          "pipeline", "2026-10-18", "-", "documento", "-", "-"),
            bloco_entrada(G1_ORIGEM, "município de origem dos candidatos (G1)", "portão G1", "referências 202506, "
                          "202510, 202602", f"{len(dados['org'])} candidatos (regra principal)", "candidato",
                          "ciclo, id_candidato", f"regra_ligacao = {REGRA_G1}"),
            bloco_entrada(G1_DIST, "conferência das distâncias das células escolhidas", "portão G1", "idem",
                          "linhas candidato × opção", "candidato × opção", "ciclo, id_candidato, opcao_rank",
                          f"regra_ligacao = {REGRA_G1}"),
            bloco_entrada(G1_RESUMO, "taxas de ligação do G1", "portão G1", "2026-10-19", "-", "documento", "-", "-"),
            bloco_entrada(X45.CIR_BRUTO, "região de saúde (CIR) por município (só lido)", "DATASUS/TabNet (manifesto "
                          "da X5)", dados["manifesto_cir"]["data_download_utc"],
                          f"{dados['diag_cir']['municipios']} municípios", "município", "co_ibge → co_cir",
                          "linhas 'Ignorado' fora"),
            bloco_entrada(X1.COORD_JSON, "centroides municipais do IBGE (distância, só lido)", "IBGE, API de malhas v3",
                          str(dados["diag_coord"].get("data_download", "")), f"{dados['diag_coord'].get('municipios')} "
                          "municípios", "município", "id (7 dígitos)", "centroide"),
            bloco_entrada(E9_ESTIMATIVAS, "alvo da conferência de reprodução do E9", "E9 (script 16)", "2026-10-19",
                          "linha principal empilhada", "especificação × termo", "ciclo, modelo, conjunto, "
                          "especificacao, termo", "condicional, principal, spline_linear__bolsa_linear, bolsa_mil"),
            bloco_entrada(V_CELULA, "candidatos de 1ª opção por célula (P1g)", "tarefa B (script 12)",
                          "ciclos 1–3", "células do quadro", "célula", "ciclo, co_cnes_7d, cod_curso", "n_cand_1a_opcao"),
            bloco_entrada(NA_ESTIMATIVAS, "conferência da RDD por célula contra o A3 (só curso × ciclo)",
                          "script 24", "2026-10-19", "linhas A3_CAND_1A_OPCAO", "linha", "outcome_id, variante, "
                          "ciclo, corte", "variante so_curso_x_ciclo"),
        ],
        "saidas": {rel(p): sha256(p) for p in (OUT_EST, OUT_DAP)},
        "integridade": ("nada simulado, imputado ou digitado como observação; faltante fica faltante com motivo; IVS do "
                        "a08 (o arquivo local de IVS da auditoria 16 não é lido); nenhum mês do CNES é lido; sem nome "
                        "nem CPF em output/; data/ só lido"),
        "linguagem": ("P1a é efeito da remuneração anunciada na escolha DENTRO do conjunto de vagas abertas, "
                      "identificado pelos saltos nos cortes com o IVS contínuo controlado; mede o pacote do corte e o "
                      "incentivo marginal, não a participação no PMM-E; não diz nada sobre quem não se candidatou"),
        "tempo_execucao_nao_registrado": "o tempo de execução fica fora do resumo para que duas execuções deem o mesmo hash",
    }
    for chave in ("m8", "m9"):
        resumo[chave].pop("segundos", None)
    gravar_json(OUT_RESUMO, resumo)
    atualizar_doc()
    log(f"gravado: {rel(OUT_EST)}, {rel(OUT_DAP)}, {rel(OUT_RESUMO)}, {rel(DIR_FIG)}, {rel(DOC)}")
    return 0


def ler_est() -> pd.DataFrame:
    return pd.read_csv(OUT_EST, dtype={"ciclo": str})


def ler_dap() -> pd.DataFrame:
    return pd.read_csv(OUT_DAP, dtype={"ciclo": str})


def atualizar_doc() -> None:
    est, dap = ler_est(), ler_dap()
    resumo = json.loads(OUT_RESUMO.read_text(encoding="utf-8"))
    DOC.write_text(gerar_doc(est, dap, resumo), encoding="utf-8")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except FalhaValidacao as erro:
        print(f"FALHA DE VALIDACAO: {erro}", file=sys.stderr)
        sys.exit(2)
