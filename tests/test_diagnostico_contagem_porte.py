"""Testes do diagnóstico ND (fora do protocolo 48): `scripts/rdd_bolsa/23b_diagnostico_contagem_porte.py`.

Três partes:

1. `TestSintetico`: DADOS SINTÉTICOS gerados em memória (semente fixa), rotulados `SINTETICO_TESTE` e nunca
   gravados em `output/` nem em `data/`. Conferem que o local linear com ciclos juntos recupera um salto conhecido,
   que o local constante é a diferença de médias, que salto empilhado = soma omega x salto do grupo, que a
   decomposição log-aditiva fecha e que taxa com denominador zero e log de zero ficam ausentes (nunca zero).
2. `TestSaidas`: esquema, rótulos, lista fixa de diagnósticos, hashes e números de `ND_estimativas.csv` refeitos de
   forma independente a partir do parquet da tarefa B e do a08 (MQP e CR1 escritos aqui, sem a rdd_lib).
3. `TestDoc49b`: o doc 49b é idêntico ao gerado das saídas, cada número dele tem origem em `output/`, a lista fixa
   aparece antes dos resultados e cada figura traz o "Como ler" abaixo da imagem.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import struct
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "23b_diagnostico_contagem_porte.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("diagnostico_contagem_porte_23b", SCRIPT)
ND = importlib.util.module_from_spec(_spec)
sys.modules["diagnostico_contagem_porte_23b"] = ND
_spec.loader.exec_module(ND)
sys.dont_write_bytecode = _bytecode
L, T23 = ND.L, ND.T23

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "ND_estimativas.csv"
RESUMO = OUT / "ND_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "49b_diagnostico_contagem_porte.md"
DOC49 = ROOT / "docs" / "06_execucao" / "49_resultados_contagem_vagas_preenchidas.md"
VM = ROOT / "output" / "rdd_bolsa" / "outcomes" / "outcomes_V_municipio.parquet"
A08 = ROOT / "output" / "aquisicao" / "a08_ivs_2010_oficial_municipio.csv"
NATUREZA_SINTETICA = "SINTETICO_TESTE"   # rótulo dos dados gerados aqui; nunca gravados


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# 1. Sintético (só em memória)
# --------------------------------------------------------------------------

SALTO_SINTETICO = 1.2


def painel_sintetico(semente: int = 7, n: int = 900) -> dict[int, pd.DataFrame]:
    """SINTÉTICO: três ciclos com níveis diferentes, salto conhecido em 0,300 e em 0,400."""
    rng = np.random.default_rng(semente)
    V = {}
    for k in (1, 2, 3):
        s = rng.integers(200, 501, n).astype(float)
        t = ((s > 300) & (s <= 350)) | (s > 400)
        vi = rng.poisson(2.0, n).astype(float)
        vcr = rng.poisson(3.0, n).astype(float) + 1
        y = np.maximum(0, np.round(0.5 * k + 0.3 * (vi + vcr) + 3 * (s / 1000 - 0.3) + SALTO_SINTETICO * t
                                   + rng.normal(0, 0.4, n)))
        V[k] = pd.DataFrame({"co_ibge": [f"9{i:05d}" for i in range(n)], "s_mil": s, "ciclo": k,
                             "natureza_dos_dados": NATUREZA_SINTETICA, "populacao_2022": rng.integers(3000, 900000, n),
                             "vagas_imediatas": vi, "vagas_cr": vcr, "vagas_imediatas_mais_cr": vi + vcr,
                             "n_alocados_ch1": y, "n_celulas": np.maximum(1, np.round((vi + vcr) / 2))})
    nomes = pd.Series({f"9{i:05d}": f"municipio sintetico {i}" for i in range(n)})
    return ND.preparar(V, nomes)


class TestSintetico(unittest.TestCase):
    """Dados SINTÉTICOS em memória: conferem os estimadores, nunca viram resultado."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.V = painel_sintetico()

    def test_rotulo_sintetico(self) -> None:
        for d in self.V.values():
            self.assertEqual(set(d["natureza_dos_dados"]), {NATUREZA_SINTETICA})

    def test_local_linear_ciclos_juntos_recupera_salto(self) -> None:
        for c in ND.CORTES:
            a = ND.amostra_corte(self.V, c)
            r = ND.ajustar(a, a.col("n_alocados_ch1"), ND.H, (("v", a.col("vagas_imediatas_mais_cr")),))
            self.assertLess(abs(r["tau"] - SALTO_SINTETICO), 3 * r["ep"] + 0.05, c)

    def test_local_constante_e_diferenca_de_medias(self) -> None:
        a = ND.amostra_ciclo(self.V, 1, 300)
        y = a.col("n_alocados_ch1")
        r = ND.local_constante(a, y, 20)
        x = L.normalizar_s_mil(a.s) - 300
        dif = y[(x > 0) & (x <= 20)].mean() - y[(x <= 0) & (x >= -20)].mean()
        self.assertAlmostEqual(r["tau"], dif, places=10)
        v = a.col("vagas_imediatas_mais_cr")
        rp = ND.local_constante(a, a.col("taxa_vic"), 20, peso=v)
        ac, ab = (x > 0) & (x <= 20), (x <= 0) & (x >= -20)
        difp = y[ac].sum() / v[ac].sum() - y[ab].sum() / v[ab].sum()
        self.assertAlmostEqual(rp["tau"], difp, places=10)

    def test_identidade_omega(self) -> None:
        ex = {"residuos_omega": []}
        linhas = ND.d5(self.V, ex)
        self.assertTrue(ex["residuos_omega"])
        self.assertLess(max(abs(x) for x in ex["residuos_omega"]), 1e-8)
        idt = [ln for ln in linhas if ln["tipo_linha"] == "identidade"]
        for ln in idt:
            self.assertAlmostEqual(ln["tau"], ln["contribuicao"], places=8)

    def test_decomposicao_log_fecha(self) -> None:
        ex = {"residuos_log": []}
        a = ND.amostra_corte(self.V, 300)
        ND.d1(ND.POR_CORTE, a, ND._ctx(ND.POR_CORTE, a, c=300), ex)
        self.assertLess(abs(ex["residuos_log"][0]), 1e-9)

    def test_ausencias_nunca_viram_zero(self) -> None:
        for d in self.V.values():
            sem_vi = d["vagas_imediatas"] == 0
            self.assertTrue(sem_vi.any())
            self.assertTrue(d.loc[sem_vi, "taxa_vi"].isna().all())
            n1z = d["n_alocados_ch1"] == 0
            if n1z.any():
                self.assertTrue(d.loc[n1z, ["log_n1", "log_vic", "log_taxa_vic"]].isna().all().all())
            self.assertFalse(d.loc[~sem_vi, "taxa_vi"].isna().any())


# --------------------------------------------------------------------------
# 2. Saídas reais
# --------------------------------------------------------------------------

def _dados_independentes() -> dict[int, pd.DataFrame]:
    """Parquet da tarefa B + IVS do a08, lidos aqui sem o script."""
    vm = pd.read_parquet(VM)
    a08 = pd.read_csv(A08, dtype={"co_ibge": str}, usecols=["co_ibge", "ivs"])
    a08["co_ibge"] = a08["co_ibge"].str.zfill(6)
    vm = vm.merge(a08, on="co_ibge", how="inner")
    vm["s"] = np.round(vm["ivs"] * 1000)
    vm["vic"] = vm["vagas_imediatas"] + vm["vagas_cr"]
    return {int(k): d.reset_index(drop=True) for k, d in vm.groupby("ciclo")}


def _mqp_cr1(V: dict, corte: int, y_col: str, peso_col: str | None = None, h: int = 50) -> tuple[float, float]:
    """Local linear com ciclos juntos: const, x, T x por ciclo e T comum; MQP e CR1 por município, escritos aqui."""
    linhas = []
    for k, d in V.items():
        x = d["s"] - corte
        w = np.clip(1 - np.abs(x) / h, 0, None) * (np.abs(x) < h)
        if peso_col:
            w = w * d[peso_col]
        y = d[y_col] if y_col != "taxa" else d["n_alocados_ch1"] / d["vic"]
        linhas.append(pd.DataFrame({"k": k, "x": x / 1000, "t": (x > 0).astype(float), "w": w, "y": y,
                                    "cl": d["co_ibge"]}))
    df = pd.concat(linhas, ignore_index=True)
    df = df[df["w"] > 0]
    cols = []
    for k in sorted(df["k"].unique()):
        ind = (df["k"] == k).astype(float)
        cols += [ind, ind * df["x"], ind * df["t"] * df["x"]]
    cols.append(df["t"])
    X = np.column_stack(cols)
    w, y = df["w"].to_numpy(), df["y"].to_numpy()
    XtW = X.T * w
    B = np.linalg.inv(XtW @ X)
    b = B @ (XtW @ y)
    e = y - X @ b
    sc = X * (w * e)[:, None]
    g = pd.factorize(df["cl"])[0]
    S = np.zeros((g.max() + 1, X.shape[1]))
    np.add.at(S, g, sc)
    G, n, kk = g.max() + 1, len(y), X.shape[1]
    Vb = B @ (S.T @ S) @ B * (G / (G - 1)) * ((n - 1) / (n - kk))
    return float(b[-1]), float(np.sqrt(Vb[-1, -1]))


@unittest.skipUnless(EST.exists() and RESUMO.exists(), "saidas ND ausentes")
class TestSaidas(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est, cls.resumo = ND.ler_saidas()

    def test_esquema_e_rotulos(self) -> None:
        self.assertEqual(list(self.est.columns), ND.COLUNAS)
        self.assertEqual(set(self.est["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(self.est["estatuto"]), {"DIAGNOSTICO_FORA_PROTOCOLO_48"})
        self.assertEqual(self.resumo["estatuto"], "DIAGNOSTICO_FORA_PROTOCOLO_48")
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")
        self.assertFalse(self.est["id_linha"].duplicated().any())
        self.assertLessEqual(set(self.est["amostra"]), {ND.POR_CORTE, ND.APENDICE, ND.EMP})
        emp = self.est[self.est["amostra"] == ND.EMP]
        self.assertEqual(set(emp["corte"]), {"empilhado"})
        self.assertEqual(set(self.est.loc[self.est["amostra"] == ND.POR_CORTE, "corte"]), {"0.300", "0.400"})

    def test_lista_fixa_relatada_por_corte(self) -> None:
        ids = [d["id"] for d in self.resumo["diagnosticos"]]
        self.assertEqual(ids, ["D1", "D2", "D3", "D4", "D5"])
        pc = self.est[self.est["amostra"] == ND.POR_CORTE]
        for corte in ("0.300", "0.400"):
            presentes = set(pc.loc[pc["corte"] == corte, "diagnostico"])
            self.assertEqual(presentes, {"D1", "D2", "D3", "D4", "D5"}, corte)
            d3 = pc[(pc["corte"] == corte) & (pc["diagnostico"] == "D3")]
            for h in ND.H_D3:
                self.assertEqual(len(d3[(d3["especificacao"] == "poisson_offset") & (d3["variante"] == f"h={h / 1000:.3f}")]), 1)
            for w in ND.JANELAS_LC:
                self.assertEqual(len(d3[(d3["especificacao"] == "local_constante")
                                        & d3["variante"].str.startswith(f"janela_{w / 1000:.3f}")]), 4)
            sm = pc[(pc["corte"] == corte) & (pc["tipo_linha"] == "sem_maiores")]
            self.assertEqual(len(sm), len(ND.KS) * 3 * 4)
            inf = pc[(pc["corte"] == corte) & (pc["tipo_linha"] == "influencia")]
            n_mun = self.resumo["contagens"]["influencia"][corte]["n_municipios"]
            self.assertEqual(len(inf), 2 * n_mun)
        # apêndice por ciclo: D1 e D4 em todo ciclo x corte
        ap = self.est[self.est["amostra"] == ND.APENDICE]
        self.assertEqual(len(ap.groupby(["populacao", "corte"])), 6)

    def test_adendo_e_nao_executado_rotulados(self) -> None:
        ad = self.est[self.est["especificacao"] == "local_constante_adendo_AD1"]
        self.assertTrue(len(ad))
        self.assertTrue(ad["nota"].str.contains("ADENDO AD1").all())
        self.assertEqual([a["id"] for a in self.resumo["adendos"]], ["AD1"])
        for a in self.resumo["adendos"]:
            self.assertTrue(a["ja_visto"] and a["por_que"] and a["data"])
        ne = self.est[self.est["status"] == "NAO_EXECUTADO"]
        self.assertTrue((ne["especificacao"] == "rdrobust_h_otimo").all())
        self.assertTrue(ne["nota"].str.len().gt(20).all())
        nucleo = self.est[self.est["tipo_linha"] == "estimativa"]
        sem = nucleo[nucleo["tau"].isna() & (nucleo["nota"] == "")]
        self.assertEqual(len(sem), 0)

    def test_hashes(self) -> None:
        for e in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / e["caminho"]), e["sha256"], e["caminho"])
            self.assertNotIn("ivs_ipea", e["caminho"])
        self.assertEqual(sha256(EST), self.resumo["saidas"]["ND_estimativas.csv"]["sha256"])
        for f in self.resumo["saidas"]["figuras"]:
            self.assertEqual(sha256(ROOT / f["arquivo"]), f["sha256"], f["arquivo"])

    def test_reproduz_doc49(self) -> None:
        self.assertEqual(len(self.resumo["validacoes"]["doc49"]["linhas_conferidas"]), 12)
        self.assertLess(self.resumo["validacoes"]["doc49"]["max_abs_dif"], 1e-9)
        n = pd.read_csv(OUT / "N_estimativas.csv", dtype={"corte": str})
        for corte in ("0.300", "0.400"):
            alvo = n[(n["outcome_id"] == "N1") & (n["populacao"] == "V1+V2+V3") & (n["corte"] == corte)
                     & (n["especificacao"] == "S-b") & (n["variante"] == "principal")].iloc[0]
            r = ND._um(self.est, diagnostico="D1", tipo_linha="estimativa", amostra=ND.POR_CORTE, corte=corte,
                       outcome="N1", especificacao="sem_controle")
            self.assertAlmostEqual(float(r["tau"]), float(alvo["tau"]), places=9)

    def test_saltos_refeitos_independentemente(self) -> None:
        V = _dados_independentes()
        for c in (300, 400):
            corte = f"0.{c}"
            for oid, ycol, peso in (("N1", "n_alocados_ch1", None), ("VIC", "vic", None), ("TAXA_VIC", "taxa", "vic")):
                esp = "taxa_ponderada" if peso else "sem_controle"
                r = ND._um(self.est, diagnostico="D1", tipo_linha="estimativa", amostra=ND.POR_CORTE, corte=corte,
                           outcome=oid, especificacao=esp)
                tau, ep = _mqp_cr1(V, c, ycol, peso)
                self.assertAlmostEqual(float(r["tau"]), tau, places=8, msg=(corte, oid))
                self.assertAlmostEqual(float(r["ep"]), ep, places=8, msg=(corte, oid))

    def test_faixas_refeitas(self) -> None:
        V = _dados_independentes()
        d = pd.concat(V.values(), ignore_index=True)
        for c in (300, 400):
            x = d["s"] - c
            jan = d[np.abs(x) < 50].assign(x=x[np.abs(x) < 50])
            jan["f"] = np.where(jan["x"] <= 0, -(np.floor(-jan["x"] / 10) + 1), np.floor(jan["x"] / 10)).astype(int)
            fx = ND._sel(self.est, tipo_linha="faixa", amostra=ND.POR_CORTE, corte=f"0.{c}")
            self.assertEqual(len(fx), 10)
            for _, r in fx.iterrows():
                g = jan[jan["f"] == int(r["faixa"])]
                self.assertEqual(int(r["n_linhas"]), len(g))
                self.assertAlmostEqual(float(r["n1_media"]), g["n_alocados_ch1"].mean(), places=10)
                self.assertAlmostEqual(float(r["pop_media"]), g["populacao_2022"].mean(), places=6)
                self.assertAlmostEqual(float(r["taxa_vic_ponderada"]), g["n_alocados_ch1"].sum() / g["vic"].sum(),
                                       places=10)

    def test_identidades_gravadas(self) -> None:
        for _, r in self.est[(self.est["diagnostico"] == "D5") & (self.est["tipo_linha"] == "identidade")].iterrows():
            parte = self.est[(self.est["diagnostico"] == "D5") & (self.est["tipo_linha"] == "contribuicao")
                             & (self.est["amostra"] == r["amostra"]) & (self.est["corte"] == r["corte"])
                             & (self.est["especificacao"] == r["especificacao"])]
            self.assertAlmostEqual(parte["peso_omega"].astype(float).sum(), 1.0, places=9)
            self.assertAlmostEqual(parte["contribuicao"].astype(float).sum(), float(r["tau"]), places=8)
        for _, r in self.est[(self.est["diagnostico"] == "D1") & (self.est["tipo_linha"] == "identidade")].iterrows():
            self.assertAlmostEqual(float(r["tau"]), float(r["contribuicao"]) + float(r["tau_grupo"]), places=9)

    def test_figuras_16x9_e_como_ler_simples(self) -> None:
        figs = self.resumo["saidas"]["figuras"]
        self.assertEqual(len(figs), 8)
        proibidas = ("kernel", "cr1", "hc1", "gamma", "omega", "poisson", "offset", "ccft", "leave-one-out")
        for f in figs:
            with open(ROOT / f["arquivo"], "rb") as fh:
                cab = fh.read(24)
            w, h = struct.unpack(">II", cab[16:24])
            self.assertAlmostEqual(w / h, 16 / 9, places=2, msg=f["arquivo"])
            txt = f["como_ler"]
            frases = [s for s in re.split(r"(?<=[.!?])\s+", txt.strip()) if s]
            self.assertTrue(1 <= len(frases) <= 2, f["arquivo"])
            for p in proibidas:
                self.assertNotIn(p, txt.lower(), (f["arquivo"], p))

    def test_script_nao_le_ivs_errado_nem_grava_data(self) -> None:
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("ivs_ipea", src)
        self.assertNotRegex(src, r"ROOT\s*/\s*\"data\"")


# --------------------------------------------------------------------------
# 3. Doc 49b
# --------------------------------------------------------------------------

def _candidatos(est: pd.DataFrame, resumo: dict) -> set[str]:
    """Todo número formatável a partir de output/ (CSV e JSON), sem sinal, com 0 a 3 casas e escalas 1, 100, 1/1000."""
    vals: list[float] = []
    textos: list[str] = []
    for c in est.columns:
        s = pd.to_numeric(est[c], errors="coerce")
        vals += s.dropna().tolist()
        if s.isna().all():
            textos += est[c].dropna().astype(str).tolist()

    def andar(o):
        if isinstance(o, dict):
            for v in o.values():
                andar(v)
        elif isinstance(o, list):
            for v in o:
                andar(v)
        elif isinstance(o, bool):
            return
        elif isinstance(o, (int, float)):
            vals.append(float(o))
        elif isinstance(o, str):
            textos.append(o)
    andar(resumo)
    cand = set()
    for v in vals:
        for esc in (1, 100, 1 / 1000):
            x = abs(v * esc)
            for casas in range(4):
                cand.add(f"{x:.{casas}f}".replace(".", ","))
    for t in textos:
        cand |= {m.replace(".", ",") for m in re.findall(r"\d+(?:[.,]\d+)?", t)}
    # Somas de grupos (D5 por corte) e contagens derivadas do CSV.
    d5 = est[(est["diagnostico"] == "D5") & (est["tipo_linha"] == "contribuicao") & (est["amostra"] == ND.EMP)]
    for esp, g in d5.groupby("especificacao"):
        for c in ("300", "400"):
            s = g[g["variante"].str.endswith(c)]
            for col in ("peso_omega", "contribuicao"):
                tot = abs(s[col].astype(float).sum())
                cand |= {f"{tot:.{k}f}".replace(".", ",") for k in range(4)}
    for n in range(0, 60):
        cand.add(str(n))
    return cand


@unittest.skipUnless(DOC.exists() and EST.exists(), "doc 49b ou saidas ausentes")
class TestDoc49b(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est, cls.resumo = ND.ler_saidas()
        cls.doc = DOC.read_text(encoding="utf-8")

    def test_doc_igual_ao_gerado(self) -> None:
        self.assertEqual(self.doc, ND.gerar_doc(self.est, self.resumo))

    def test_numeros_do_doc_tem_origem_em_output(self) -> None:
        txt = self.doc
        txt = re.sub(r"`[^`]*`", "", txt)
        txt = re.sub(r"\]\([^)]*\)", "]", txt)
        txt = re.sub(r"!\[[^\]]*\]", "", txt)
        txt = re.sub(r"\b\d{2}/\d{2}/\d{4}\b", "", txt)
        txt = re.sub(r"(?m)^#+ .*$", "", txt)
        txt = re.sub(r"\b[A-Za-z_][A-Za-z_\-]*\d+[a-z]?(?:\.\d+)*\b", "", txt)   # D1, N1, F1.3, k=, AD1...
        txt = re.sub(r"\d+ª", "", txt)
        txt = re.sub(r"\d\.\de[-+]\d+", "", txt)                                 # resíduos em notação científica
        txt = re.sub(r"\b(?:docs?|protocolo|seção|seções|auditoria|Censo|IVS de|Edital)\s+\d+", "", txt)
        for fixo in ("SHA-256", "IC 95%", "16:9", "R$ 5 mil", "1–3", "x100"):
            txt = txt.replace(fixo, "")
        tokens = re.findall(r"(?<![\w,])[−+-]?\d+(?:,\d+)?", txt)
        cand = _candidatos(self.est, self.resumo)
        parametros = {"0,300", "0,400", "0,050", "0,010", "0,020", "0,030", "0,080", "0,040", "0", "1", "2", "3", "5",
                      "10", "2010", "2022"}
        fora = sorted({t.lstrip("−+-") for t in tokens} - cand - parametros)
        self.assertEqual(fora, [], f"numeros do doc sem origem em output/: {fora[:20]}")

    def test_gerador_do_doc_sem_numero_digitado(self) -> None:
        """Nos literais de texto das funções que escrevem o doc só há parâmetros e referências, nunca resultado.

        Os valores entram só por campos formatados lidos das saídas (as especificações de formato, como '.2f',
        não contam). Permitidos: cortes, janelas, h, k, ano do IVS, números de seção, de documento, de script e de
        auditoria, 'IC 95%', '16:9', 'SHA-256', 'R$ 5 mil' e 'ciclos 1–3'.
        """
        import ast
        arvore = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        prefixos = ("gerar_doc", "leitura", "tabela_", "lista_retirados", "_sentido")
        achados: set[str] = set()

        def andar(no):
            if isinstance(no, ast.FormattedValue):
                andar(no.value)
                return
            if isinstance(no, ast.Constant) and isinstance(no.value, str):
                achados.update(re.findall(r"(?<![\w.])[−+-]?\d+(?:[.,]\d+)?", no.value))
            for filho in ast.iter_child_nodes(no):
                andar(filho)

        for f in arvore.body:
            if isinstance(f, ast.FunctionDef) and f.name.startswith(prefixos):
                andar(f)
        parametros = {"0,300", "0,400", "0,050", "0.050", "0,010", "0,020", "0,080", "−0,010", "−0,040", "−0,050",
                      "2010", "95", "16", "9", "256", "5", "1", "2", "3", "0"}
        referencias = {str(n) for n in range(4, 14)} | {"18", "23", "48", "49"}
        self.assertEqual(achados - parametros - referencias, set())
        self.assertTrue(achados)

    def test_lista_fixa_antes_dos_resultados(self) -> None:
        i_lista = self.doc.index("## 2. Conjunto fixo de diagnósticos")
        i_res = self.doc.index("## 3. Resposta curta")
        for d in self.resumo["diagnosticos"]:
            pos = self.doc.index(f"**{d['id']}, {d['nome']}:**")
            self.assertTrue(i_lista < pos < i_res, d["id"])
        self.assertIn("Como evitar confusão", self.doc)

    def test_como_ler_abaixo_de_cada_figura(self) -> None:
        for f in self.resumo["saidas"]["figuras"]:
            img = f"](../../{f['arquivo']})"
            i = self.doc.index(img)
            self.assertEqual(self.doc.index("**Como ler:**", i), self.doc.index("\n\n", i) + 2)
            self.assertIn(f["como_ler"], self.doc[i:i + 2000])

    def test_sem_linguagem_causal_indevida(self) -> None:
        baixo = self.doc.lower()
        for termo in ("efeito da bolsa", "a bolsa reduz", "a bolsa aumenta", "efeito causal"):
            self.assertNotIn(termo, baixo)
        self.assertIn("pacote do corte", baixo)
        self.assertIn("fora do protocolo 48", baixo)

    def test_doc49_aponta_para_49b(self) -> None:
        txt = DOC49.read_text(encoding="utf-8")
        self.assertEqual(txt.count("49b_diagnostico_contagem_porte.md"), 2)  # texto do link e destino


if __name__ == "__main__":
    unittest.main()
