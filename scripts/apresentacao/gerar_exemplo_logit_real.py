"""Exemplo real do logit condicional (VL-1) para o slide do método passo a passo da banca final.

O que faz
---------
1. Monta o desenho do VL-1 dos ciclos 1–3 com as funções do script 50 (sem alteração) e reestima o modelo com
   `estimar_ef`. Portão: o coeficiente de cada termo que não é efeito fixo tem de reproduzir o gravado em
   `output/rdd_bolsa/VL_estimativas.csv` (diferença ≤ 1e−8); se não reproduzir, para.
2. Calcula, para cada candidato, a chance que o modelo dá a cada vaga do seu cardápio:
   P(v) = exp(V_v) / soma de exp(V_k) no cardápio, com V = x'θ (efeitos fixos incluídos).
3. Escolhe o exemplo por regra fixa, sem olhar a escolha do candidato: entre todos os candidatos e todos os pares
   de vagas da UF onde o candidato trabalhava com bolsas que diferem em R$ 5 mil, o par mais parecido em todo o
   resto (soma de |diferença| de IVS × 10, distância em 100 km, vaga imediata, log das vagas imediatas, log da
   população, capital, estratos, mesma região, mesmo município). Empate: ciclo, curso, município de origem, vagas.
4. Grava `output/apresentacao_banca_final/exemplo_logit_real.json`: curso, ciclo, UF de origem (sem município nem
   identificador do candidato), tamanho do cardápio, as duas vagas (município, IVS, bolsa, km, chance), a vaga que
   ele de fato pôs em 1º (lida só depois da escolha do par, para a tabela de dados do slide), a conta da
   razão termo a termo (o efeito fixo do par é o mesmo nas duas vagas e se cancela) e as linhas por candidato.

Natureza: EMPIRICO (pesos estimados; vagas e cardápio observados). Nada simulado. Só lê `data/` pelas funções do
script 50; não escreve em `data/`.

Uso
---
    python3 scripts/apresentacao/gerar_exemplo_logit_real.py
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_VL = ROOT / "scripts/rdd_bolsa/50_escolha_localizacao_par.py"
VL_EST = ROOT / "output/rdd_bolsa/VL_estimativas.csv"
IVS = ROOT / "output/aquisicao/a08_ivs_2010_oficial_municipio.csv"
QUADRO = ROOT / "output/aquisicao/quadro_vagas_consolidado.parquet"
SAIDA = ROOT / "output/apresentacao_banca_final/exemplo_logit_real.json"
CHAVE = "VL1_emp"
TOL = 1e-8
OUTROS = ["tem_vaga_imediata", "log_vagas_imediatas_mais_1", "log_populacao_2022", "capital",
          "estrato_interior_remoto", "estrato_metropolitano", "mesma_regiao_saude", "mesmo_municipio"]
ROTULOS = {"bolsa_mil": "bolsa", "ivs": "curva do IVS", "distancia_100km": "distância",
           "log_populacao_2022": "porte (população)", "outros": "demais controles"}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def importar_vl():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("vl50_exemplo", SCRIPT_VL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["vl50_exemplo"] = mod
    spec.loader.exec_module(mod)
    return mod


def ajustar(VL):
    dados = VL.P1.carregar()
    q1302, _ = VL.VC.ler_quadros_c2()
    conj_c, _ = VL.VC.corrigir(dados["conj_p1"], q1302)
    e = VL.ESPECS[CHAVE]
    dv = {**dados, "conj_p1": conj_c}
    conj, r1 = VL.subconjunto(conj_c, dados["r1_p1"], e["ciclo"])
    D0 = VL.P1.montar_desenho(conj, r1, None, dv)
    tam_m1 = D0["tam"].copy()
    D, ef, diag = VL.desenho_ef(D0, dados, e["ef"])
    del D0
    X = VL.matriz_vl(D, dv, e, ef)
    r = VL.estimar_ef(X, D, ef, modelo=CHAVE, ciclo=e["ciclo"], amostra=VL.AMOSTRA)
    if not r["ok"]:
        raise SystemExit(f"ERRO: VL-1 não convergiu: {r.get('nota')}")
    theta = pd.Series(r["theta"], index=r["termos"])
    gravado = pd.read_csv(VL_EST)
    g = gravado[(gravado.chave_modelo == CHAVE) & (gravado.tipo_linha == "coeficiente")].set_index("termo")
    for t, v in g["estimativa"].items():
        if abs(theta[t] - v) > TOL * max(1.0, abs(v)):
            raise SystemExit(f"ERRO: {t} = {theta[t]} não reproduz o gravado ({v})")
    A = X[r["termos"]].to_numpy(dtype=float)
    V = A @ r["theta"]
    return X, D, ef, theta, V, tam_m1, diag


def probabilidades(V: np.ndarray, starts: np.ndarray) -> np.ndarray:
    tam = np.diff(np.append(starts, len(V)))
    m = np.repeat(np.maximum.reduceat(V, starts), tam)
    e = np.exp(V - m)
    return e / np.repeat(np.add.reduceat(e, starts), tam)


def escolher_par(X: pd.DataFrame, D: dict, ef: dict, ivs: pd.Series):
    conj, cel, grp, G = D["conj"], D["cel"], D["grp"], D["grupos"]
    co = conj["co_ibge"].to_numpy(dtype=object)[cel]
    T = X[["bolsa_mil", "distancia_100km"] + OUTROS].copy()
    T["ivs"] = ivs.reindex(co).to_numpy()
    T["uf"] = [c[:2] for c in co]
    T["par"] = ef["par_lin"]
    T["grp"] = grp
    T["linha"] = np.arange(len(T))
    origem = G["co_ibge_origem"].astype(str).str[:2].to_numpy()
    melhor = None
    for g, sub in T.groupby("grp", sort=True):
        sub = sub[sub["uf"] == origem[g]]
        for _, s2 in sub.groupby("par", sort=True):
            for b in (10.0, 15.0):
                a_, b_ = s2[s2.bolsa_mil == b], s2[s2.bolsa_mil == b + 5]
                if a_.empty or b_.empty:
                    continue
                dif = np.abs(a_["ivs"].to_numpy()[:, None] - b_["ivs"].to_numpy()[None, :]) * 10
                dif += np.abs(a_["distancia_100km"].to_numpy()[:, None] - b_["distancia_100km"].to_numpy()[None, :])
                for c in OUTROS:
                    dif += np.abs(a_[c].to_numpy()[:, None] - b_[c].to_numpy()[None, :])
                i, j = np.unravel_index(np.argmin(dif), dif.shape)
                gi = G.iloc[g]
                chave = (round(float(dif[i, j]), 12), int(gi["ciclo"]), int(gi["cod_curso"]), str(gi["co_ibge_origem"]),
                         int(a_["linha"].iloc[i]), int(b_["linha"].iloc[j]))
                if melhor is None or chave < melhor[0]:
                    melhor = (chave, g)
    return melhor


def main() -> int:
    VL = importar_vl()
    X, D, ef, theta, V, tam_m1, diag = ajustar(VL)
    P = probabilidades(V, D["starts"])
    ivs_tab = pd.read_csv(IVS, dtype={"co_ibge": str}).set_index("co_ibge")
    (dif, ciclo, curso, _origem, la, lb), g = escolher_par(X, D, ef, ivs_tab["ivs"])
    conj, cel, G = D["conj"], D["cel"], D["grupos"]
    co = conj["co_ibge"].to_numpy(dtype=object)
    quadro = pd.read_parquet(QUADRO, columns=["cod_curso", "no_curso"]).dropna().drop_duplicates("cod_curso")
    nome_curso = str(quadro.set_index("cod_curso")["no_curso"].get(float(curso), curso))
    if str(G.iloc[g]["co_ibge_origem"])[:2] != co[cel[la]][:2]:
        raise SystemExit("ERRO: o par do exemplo tem de estar na UF de trabalho anterior")
    sigla = str(ivs_tab.loc[co[cel[la]], "nome_municipio_uf"]).rsplit("(", 1)[1].rstrip(")")

    def vaga(linha: int) -> dict:
        m = co[cel[linha]]
        return {"municipio": ivs_tab.loc[m, "nome_municipio_uf"], "co_ibge": m,
                "ivs": round(float(ivs_tab.loc[m, "ivs"]), 3), "bolsa_mil": float(X.loc[linha, "bolsa_mil"]),
                "km": round(float(X.loc[linha, "distancia_100km"]) * 100, 1),
                "populacao_2022": round(math.exp(float(X.loc[linha, "log_populacao_2022"]))),
                "chance_modelo": float(P[linha])}

    termos = [t for t in theta.index if not t.startswith(VL.PREFIXO_EF)]
    contrib = {t: float(theta[t] * (X.loc[lb, t] - X.loc[la, t])) for t in termos}
    grupos = {"bolsa_mil": contrib["bolsa_mil"], "distancia_100km": contrib["distancia_100km"],
              "ivs": sum(v for t, v in contrib.items() if t.startswith("ivs_")),
              "log_populacao_2022": contrib["log_populacao_2022"]}
    grupos["outros"] = sum(contrib.values()) - sum(grupos.values())
    log_razao = sum(contrib.values())
    if abs(log_razao - math.log(P[lb] / P[la])) > 1e-9:
        raise SystemExit("ERRO: a soma das contribuições não reproduz a razão das chances do modelo")
    starts, tam = D["starts"], D["tam"]
    b = float(theta["bolsa_mil"])
    saida = {
        "etapa": "exemplo_logit_real_banca_final",
        "natureza_dos_dados": "EMPIRICO",
        "script": str(Path(__file__).resolve().relative_to(ROOT)),
        "modelo": "VL-1, ciclos 1–3 (logit condicional da 1ª opção com efeito fixo do par de UFs)",
        "regra_de_escolha_do_exemplo": __doc__.split("3. ")[1].split("4. ")[0].strip().replace("\n   ", " "),
        "portao": f"coeficientes reproduzem VL_estimativas.csv (tolerância {TOL})",
        "candidato": {"ciclo": ciclo, "curso": nome_curso, "uf_de_trabalho_anterior": sigla,
                      "vagas_no_cardapio": int(tam[g]), "nota": "sem município de origem nem identificador"},
        "vaga_a": vaga(la),
        "vaga_b": vaga(lb),
        "vaga_escolhida": vaga(int(D["esc"][g])),
        "dissimilaridade": dif,
        "conta": {
            "beta_bolsa_por_mil": b,
            "log_razao_por_termo": grupos,
            "rotulos": ROTULOS,
            "razao_por_termo": {k: math.exp(v) for k, v in grupos.items()},
            "log_razao_total": log_razao,
            "razao_total": math.exp(log_razao),
            "razao_so_bolsa": math.exp(5 * b),
            "chance_b_entre_as_duas": float(P[lb] / (P[la] + P[lb])),
            "efeito_fixo_do_par": "o mesmo nas duas vagas: se cancela na razão",
        },
        "linhas": {
            "candidatos_modelo": int(len(starts)),
            "linhas_modelo": int(len(V)),
            "linhas_por_candidato": {"media": float(tam.mean()), "mediana": float(np.median(tam)),
                                     "minimo": int(tam.min()), "maximo": int(tam.max())},
            "candidatos_desenho_completo": int(len(tam_m1)),
            "linhas_desenho_completo": int(tam_m1.sum()),
            "linhas_por_candidato_desenho_completo": {"media": float(tam_m1.mean()),
                                                      "mediana": float(np.median(tam_m1)),
                                                      "minimo": int(tam_m1.min()), "maximo": int(tam_m1.max())},
            "alternativas_retiradas_par_sem_escolha": diag["alternativas_retiradas_par_sem_escolha"],
            "candidatos_retirados_uma_so_alternativa": diag["candidatos_retirados_uma_so_alternativa"],
        },
        "entradas": {str(p.relative_to(ROOT)): sha256(p) for p in (VL_EST, IVS, QUADRO, SCRIPT_VL)},
    }
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=2, default=lambda o: o.item()) + "\n", encoding="utf-8")
    print(json.dumps({k: saida[k] for k in ("candidato", "vaga_a", "vaga_b", "conta")}, ensure_ascii=False, indent=1, default=lambda o: o.item()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
