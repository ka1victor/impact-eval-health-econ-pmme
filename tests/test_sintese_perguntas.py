"""Testes da síntese das perguntas reformuladas (doc 57; script 33).

Conferem:
- que o doc 57 é igual ao que o script gera a partir de `output/rdd_bolsa/S57_resumo.json`;
- que todo número exibido nos blocos volta a um arquivo de `output/` (o valor é refeito da fonte, com
  leitor próprio, e o texto é reformatado) e que a prosa fora dos blocos não traz número de resultado;
- que o Holm e o BKY de cada família, refeitos aqui com código próprio a partir dos p gravados, batem
  com o que cada bloco gravou e com o que o resumo registra;
- que o script não lê `data/` e que todas as entradas estão em `output/`;
- a linguagem: nenhuma frase causal proibida para a força da evidência de cada trecho.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "33_sintese_perguntas.py"
DOC = ROOT / "docs" / "06_execucao" / "57_sintese_perguntas_reformuladas.md"
OUT = ROOT / "output" / "rdd_bolsa"
RESUMO = OUT / "S57_resumo.json"

FORCAS = {"causal-limpo", "ATT sob tendências paralelas com pré falhando", "exploratório", "descritivo",
          "inconclusivo", "cenário (simulação)"}
CONTRASTES = {"incentivo marginal", "pacote do corte", "ser alocado", "chegada do especialista", "descritivo"}

# Números estruturais aceitos sem rastreio (parâmetros e rótulos, não resultados).
PERMITIDOS_FORA = {"0,300", "0,400", "2,8", "0,05", "0,001"}
PERMITIDOS_BLOCOS = PERMITIDOS_FORA

# Frases proibidas por força da evidência (minúsculas; busca por substring).
PROIBIDAS_COMUNS = ["efeito causal", "causou", "comprova", "prova que", "a bolsa aumenta", "a bolsa aumentou",
                    "a bolsa reduz", "a bolsa reduziu", "a bolsa funciona", "a bolsa não funciona", "efeito nulo",
                    "efeito zero", "não tem efeito", "sem efeito", "impacto"]
PROIBIDAS = {
    "descritivo": ["efeito", "por causa d", "determina a", "determinam a"],
    "ATT sob tendências paralelas com pré falhando": ["efeito", "causad", "a chegada aumenta", "a chegada aumentou",
                                                      "a chegada reduz"],
    "exploratório": ["efeito", "causad"],
    "inconclusivo": ["efeito", "aumenta o preenchimento", "reduz o preenchimento", "descarta qualquer",
                     "ineficaz"],
    "cenário (simulação)": ["efeito", "vagas a mais seriam", "o cenário mostra", "a simulação mostra",
                            "simulação indica"],
}

TOKEN = re.compile(r"[+−]?\d+(?:,\d+)?")
MARCA = re.compile(r"<!-- S57:(?P<nome>[a-z_]+):inicio -->\n(?P<corpo>.*?)\n<!-- S57:(?P=nome):fim -->", re.S)


def _importar():
    spec = importlib.util.spec_from_file_location("sintese57", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sintese57"] = mod
    spec.loader.exec_module(mod)
    return mod


def _resumo() -> dict:
    return json.loads(RESUMO.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Leitor e contas próprios (não importam o script)
# ---------------------------------------------------------------------------

_CACHE: dict[str, object] = {}


def _ler(rel: str):
    if rel not in _CACHE:
        p = ROOT / rel
        _CACHE[rel] = (pd.read_csv(p, dtype=str, low_memory=False) if rel.endswith(".csv")
                       else json.loads(p.read_text(encoding="utf-8")))
    return _CACHE[rel]


def _resolver(fonte: dict) -> float:
    obj = _ler(fonte["arquivo"])
    if "caminho" in fonte:
        for k in fonte["caminho"]:
            obj = obj[k]
        x = float(obj)
    else:
        sel = fonte["sel"]
        if "__linha__" in sel:
            row = obj.iloc[int(sel["__linha__"])]
        else:
            m = pd.Series(True, index=obj.index)
            for k, v in sel.items():
                m &= obj[k] == v
            sub = obj[m]
            assert len(sub) == 1, (fonte, len(sub))
            row = sub.iloc[0]
        x = float(row[fonte["col"]])
    for op in fonte["transf"]:
        x = x * float(op[1]) if op[0] == "mul" else math.exp(x)
    return x


def _holm(p):
    p = list(map(float, p))
    m = len(p)
    ordem = sorted(range(m), key=lambda i: (p[i], i))
    out, acc = [0.0] * m, 0.0
    for k, i in enumerate(ordem):
        acc = max(acc, min(1.0, (m - k) * p[i]))
        out[i] = acc
    return out


def _bky(p):
    p = np.asarray(p, dtype=float)
    m = len(p)
    srt = np.sort(p)

    def bh(q):
        ok = [k for k in range(m) if srt[k] <= q * (k + 1) / m]
        return max(ok) + 1 if ok else 0

    out = np.ones(m)
    for i in range(1000, 0, -1):
        q = i / 1000
        q1 = q / (1 + q)
        r1 = bh(q1)
        if r1 == 0:
            continue
        r2 = m if r1 == m else bh(q1 * m / (m - r1))
        if r2:
            out[p <= srt[r2 - 1]] = q
    return out


def _fmt(x: float, casas: int, sinal: bool) -> str:
    t = f"{abs(x):.{casas}f}"
    if float(t) == 0:
        return t.replace(".", ",")
    t = t.replace(".", ",")
    return ("−" + t) if x < 0 else (("+" if sinal else "") + t)


def _fmt_p(x: float) -> str:
    return "< 0,001" if x < 0.001 else f"{x:.3f}".replace(".", ",")


# Famílias definidas aqui, a partir dos protocolos (independente do script).
HOLM_FAMILIAS = {
    "H47": ("output/rdd_bolsa/K_D1_estimativas.csv", {"entra_holm": "True"}, "p_valor", "p_holm"),
    "H48": ("output/rdd_bolsa/N_estimativas.csv", {"entra_holm": "True"}, "p_valor", "p_holm"),
    "H52": ("output/rdd_bolsa/P1_estimativas.csv", {"entra_holm": "True"}, "p", "p_holm"),
    "H58": ("output/rdd_bolsa/R_estimativas.csv", {"especificacao": "PRINCIPAL"}, "p", "p_holm"),
    "H56": ("output/rdd_bolsa/P6_estimativas.csv", {"entra_familia": "True"}, "p_valor", "p_holm"),
}
BKY_FAMILIAS = {
    "B40-F0": ("output/rdd_bolsa/E6_estimativas.csv", {"familia": "F0", "entra_bky": "True"}, "p_valor"),
    "B40-F1": ("output/rdd_bolsa/E6_estimativas.csv", {"familia": "F1", "entra_bky": "True"}, "p_valor"),
    "B40-F2": ("output/rdd_bolsa/E6_estimativas.csv", {"familia": "F2", "entra_bky": "True"}, "p_valor"),
    "B40-F4": ("output/rdd_bolsa/E6_estimativas.csv", {"familia": "F4", "entra_bky": "True"}, "p_valor"),
    "B40-F3": ("output/rdd_bolsa/E7_estimativas.csv", {"familia": "F3", "entra_bky": "True"}, "p_valor"),
    "B47-K": ("output/rdd_bolsa/K_D1_estimativas.csv", {"entra_bky": "True"}, "p_valor"),
    "B47-12": ("output/rdd_bolsa/K_X_estimativas.csv", {"entra_bky": "True"}, "p_valor"),
    "B52": ("output/rdd_bolsa/P1_estimativas.csv", {"entra_bky": "True"}, "p"),
    "B54-T41b": ("output/rdd_bolsa/P4_estimativas.csv",
                 {"entra_bky": "True", "especificacao": "T4.1b", "regra_ligacao": "d1_pos_hoc"}, "p_valor"),
    "B54-T41c": ("output/rdd_bolsa/P4_estimativas.csv",
                 {"entra_bky": "True", "especificacao": "T4.1c", "regra_ligacao": "d1_pos_hoc"}, "p_valor"),
    "B54-T41b-lit": ("output/rdd_bolsa/P4_estimativas.csv",
                     {"entra_bky": "True", "especificacao": "T4.1b", "regra_ligacao": "literal_doc45"}, "p_valor"),
    "B54-T41c-lit": ("output/rdd_bolsa/P4_estimativas.csv",
                     {"entra_bky": "True", "especificacao": "T4.1c", "regra_ligacao": "literal_doc45"}, "p_valor"),
    "B55": ("output/rdd_bolsa/P5_estimativas.csv", {"entra_bky": "True"}, "p_valor"),
    "B56": ("output/rdd_bolsa/P6_estimativas.csv", {"entra_familia": "True"}, "p_valor"),
}


def _filtrar(rel: str, filtro: dict) -> pd.DataFrame:
    d = _ler(rel)
    m = pd.Series(True, index=d.index)
    for k, v in filtro.items():
        m &= d[k] == v
    return d[m]


def _holm_recalculado_por_familia() -> dict[str, list[float]]:
    out = {}
    e6 = _filtrar("output/rdd_bolsa/E6_estimativas.csv", {"outcome_id": "P1", "populacao": "V1+V2+V3", "ciclo": "1+2+3",
                                                         "corte": "empilhado", "especificacao": "principal"})
    e7 = _filtrar("output/rdd_bolsa/E7_estimativas.csv", {"outcome_id": "F3.1", "populacao": "U", "corte": "empilhado",
                                                         "especificacao": "principal"})
    out["H40"] = _holm([float(e6.iloc[0]["p_valor"]), float(e7.iloc[0]["p_valor"])])
    for fid, (rel, filtro, pcol, _) in HOLM_FAMILIAS.items():
        sub = _filtrar(rel, filtro)
        if fid == "H58":
            sub = sub[sub["outcome_id"].isin(["R_P1", "R_P2"])]
        out[fid] = _holm(sub[pcol].astype(float))
    return out


class TestSinteseDoc(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _importar()
        cls.r = _resumo()
        cls.doc = DOC.read_text(encoding="utf-8")

    def test_doc_igual_ao_gerado(self) -> None:
        r = dict(self.r)
        rastreio = r.pop("rastreio")
        segs = r.pop("segmentos_linguagem")
        texto, rast2, segs2, _ = self.mod.gerar_doc(r)
        self.assertEqual(texto, self.doc, "doc 57 diferente do gerado: rode o script 33")
        self.assertEqual(json.loads(json.dumps(rast2)), rastreio)
        self.assertEqual(json.loads(json.dumps(segs2)), segs)

    def test_saidas_rotuladas_empirico(self) -> None:
        self.assertEqual(self.r["natureza_dos_dados"], "EMPIRICO")
        for nome in ("S57_multiplicidade.csv", "S57_poder.csv"):
            d = pd.read_csv(OUT / nome)
            self.assertEqual(set(d["natureza_dos_dados"]), {"EMPIRICO"}, nome)
            self.assertGreater(len(d), 0)
        d = pd.read_csv(OUT / "S57_tabela_perguntas.csv")
        t16 = d["pergunta"].str.startswith("T1.6")
        self.assertEqual(set(d.loc[t16, "natureza_dos_dados"]), {"STATUS_DE_CENARIO_SEM_NUMERO_SIMULADO"})
        self.assertEqual(set(d.loc[~t16, "natureza_dos_dados"]), {"EMPIRICO"})
        self.assertNotIn("CENARIO_CONTRAFACTUAL", RESUMO.read_text(encoding="utf-8"))

    def test_entradas_em_output_e_hash(self) -> None:
        for e in self.r["entradas"]:
            self.assertTrue(e["caminho"].startswith("output/"), e["caminho"])
            h = hashlib.sha256((ROOT / e["caminho"]).read_bytes()).hexdigest()
            self.assertEqual(h, e["sha256"], f"{e['caminho']} mudou: rode o script 33")

    def test_nenhuma_leitura_de_data(self) -> None:
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"[\"']data/", src), "o script cita um caminho em data/")
        self.assertNotIn('ROOT / "data"', src)
        self.assertNotIn("ivs_ipea_2010_municipios", src)
        for item in self.r["rastreio"]:
            f = item["fonte"]
            if "arquivo" in f:
                self.assertTrue(f["arquivo"].startswith("output/"), f)

    def test_tabela_por_pergunta_com_categorias_fixas(self) -> None:
        d = pd.read_csv(OUT / "S57_tabela_perguntas.csv")
        self.assertTrue(set(d["forca"]) <= FORCAS, set(d["forca"]) - FORCAS)
        self.assertTrue(set(d["contraste"]) <= CONTRASTES, set(d["contraste"]) - CONTRASTES)
        self.assertNotIn("causal-limpo", set(d["forca"]))
        perguntas = " ".join(d["pergunta"])
        for chave in ("P1", "P2", "P3 (D1)", "P3 (D2", "P4", "P5", "P6", "Realocação", "T1.6"):
            self.assertIn(chave, perguntas)
        t16 = d[d["pergunta"].str.startswith("T1.6")].iloc[0]
        self.assertEqual(t16["forca"], "cenário (simulação)")
        self.assertTrue(_ler("output/cenarios/P1_cenarios_resumo.json")["validacao_base"]["passou"])


class TestRastreioNumeros(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r = _resumo()
        cls.doc = DOC.read_text(encoding="utf-8")
        cls.holm = _holm_recalculado_por_familia()

    def test_cada_numero_volta_a_fonte(self) -> None:
        fh = {f["id"]: f for f in self.r["holm"]}
        fb = {f["id"]: f for f in self.r["bky"]}
        self.assertGreater(len(self.r["rastreio"]), 100)
        for item in self.r["rastreio"]:
            f = item["fonte"]
            if "derivado" in f:
                tipo = f["derivado"]
                if tipo == "holm":
                    x = self.holm[f["familia"]][f["indice"]]
                elif tipo == "dif_holm":
                    g = fh[f["familia"]]["membros"][f["indice"]]["gravado"]
                    x = abs(self.holm[f["familia"]][f["indice"]] - _resolver(g))
                elif tipo == "bky_max_dif":
                    rel, filtro, pcol = BKY_FAMILIAS[f["familia"]]
                    sub = _filtrar(rel, filtro)
                    x = float(np.max(np.abs(_bky(sub[pcol].astype(float)) - sub["q_bky"].astype(float).to_numpy())))
                    self.assertEqual(fb[f["familia"]]["n"], len(sub))
                else:
                    self.fail(f"derivado desconhecido: {tipo}")
            else:
                x = _resolver(f)
            self.assertTrue(math.isclose(x, f["v"], rel_tol=1e-9, abs_tol=1e-12), (item["texto"], f))
            texto = _fmt_p(x) if item["modo"] == "p" else _fmt(x, item["casas"], item["sinal"])
            self.assertEqual(texto, item["texto"], f)

    def test_numeros_dos_blocos_sao_rastreados(self) -> None:
        registrados = set()
        for item in self.r["rastreio"]:
            registrados.update(TOKEN.findall(item["texto"]))
        blocos = list(MARCA.finditer(self.doc))
        self.assertGreaterEqual(len(blocos), 8)
        for m in blocos:
            corpo = m.group("corpo")
            if m.group("nome") == "entradas":
                corpo = re.sub(r"`[^`]*`", "", corpo)
            corpo = re.sub(r"θ\([^)]*\)", "", corpo)  # rótulo da janela de evento, não resultado
            for tok in TOKEN.findall(corpo):
                if "," in tok or tok[0] in "+−":
                    self.assertIn(tok, registrados | PERMITIDOS_BLOCOS, f"bloco {m.group('nome')}: {tok} sem fonte")

    def test_prosa_fora_dos_blocos_sem_numero_de_resultado(self) -> None:
        fora = MARCA.sub("", self.doc)
        fora = re.sub(r"`[^`]*`", "", fora)
        for tok in TOKEN.findall(fora):
            if "," in tok or tok[0] in "+−":
                self.assertIn(tok, PERMITIDOS_FORA, f"número fora dos blocos: {tok}")


class TestHolmBky(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r = _resumo()
        cls.holm = _holm_recalculado_por_familia()

    def test_holm_recalculado_bate_com_gravado_e_resumo(self) -> None:
        for f in self.r["holm"]:
            rec = self.holm[f["id"]]
            self.assertEqual(len(rec), len(f["membros"]), f["id"])
            for k, m in enumerate(f["membros"]):
                self.assertAlmostEqual(rec[k], _resolver(m["gravado"]), places=8, msg=f"{f['id']} {m['rotulo']}")
                self.assertAlmostEqual(rec[k], m["recalculado"]["v"], places=12)
                self.assertEqual(rec[k] < 0.05, m["rejeita_recalculado"])

    def test_holm_do_protocolo_40_bate_com_e8(self) -> None:
        e8 = _ler("output/rdd_bolsa/E8_resumo.json")
        self.assertAlmostEqual(self.holm["H40"][0], e8["holm"]["P1"]["p_holm"], places=12)
        self.assertAlmostEqual(self.holm["H40"][1], e8["holm"]["P2"]["p_holm"], places=12)

    def test_bky_recalculado_bate_com_gravado(self) -> None:
        ids = {f["id"]: f for f in self.r["bky"]}
        self.assertEqual(set(ids), set(BKY_FAMILIAS))
        for fid, (rel, filtro, pcol) in BKY_FAMILIAS.items():
            sub = _filtrar(rel, filtro)
            q = _bky(sub[pcol].astype(float))
            qg = sub["q_bky"].astype(float).to_numpy()
            self.assertLessEqual(float(np.max(np.abs(q - qg))), 0.0011, fid)
            self.assertEqual(int((q < 0.05).sum()), ids[fid]["n_q_recalculado_menor_005"], fid)
            self.assertEqual(int((qg < 0.05).sum()), ids[fid]["n_q_gravado_menor_005"], fid)
            np.testing.assert_allclose(q, ids[fid]["q_recalculado"], atol=1e-12)

    def test_divergencias_coerentes(self) -> None:
        esperado = []
        for f in self.r["holm"]:
            for k, m in enumerate(f["membros"]):
                if abs(self.holm[f["id"]][k] - _resolver(m["gravado"])) > 1e-6:
                    esperado.append(f["id"])
        for f in self.r["bky"]:
            if f["max_dif"]["v"] > 0.0011 or f["n_q_gravado_menor_005"] != f["n_q_recalculado_menor_005"]:
                esperado.append(f["id"])
        self.assertEqual(len(esperado), len(self.r["divergencias"]))

    def test_holm_e_bky_sinteticos(self) -> None:
        # Sintético (só em memória): exemplos de resultado conhecido.
        np.testing.assert_allclose(_holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])
        np.testing.assert_allclose(_holm([0.5]), [0.5])
        mod = _importar()
        rng = np.random.default_rng(20261024)
        for _ in range(20):
            p = rng.uniform(0, 0.2, size=int(rng.integers(2, 30)))
            np.testing.assert_allclose(mod.holm(p), _holm(p), atol=1e-15)
            np.testing.assert_allclose(mod.bky(p), _bky(p), atol=1e-15)
        q = _bky([0.001, 0.002, 0.9])
        self.assertTrue(q[0] <= q[1] <= q[2])


class TestLinguagem(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.r = _resumo()
        cls.doc = DOC.read_text(encoding="utf-8").lower()

    def test_frases_proibidas_por_forca(self) -> None:
        self.assertGreater(len(self.r["segmentos_linguagem"]), 10)
        for s in self.r["segmentos_linguagem"]:
            texto = s["texto"].lower()
            for forca in s["forcas"]:
                self.assertIn(forca, FORCAS)
                self.assertNotEqual(forca, "causal-limpo")
                for frase in PROIBIDAS_COMUNS + PROIBIDAS[forca]:
                    self.assertNotIn(frase, texto, f"'{frase}' em trecho de força '{forca}': {s['texto'][:120]}")

    def test_frases_proibidas_no_doc_inteiro(self) -> None:
        for frase in PROIBIDAS_COMUNS:
            self.assertNotIn(frase, self.doc, frase)

    def test_avisos_obrigatorios(self) -> None:
        for frase in ("pacote do corte", "não é evidência de ausência", "proposta, não decisão",
                      "participação no pmm-e", "agora tem especialistas", "202703"):
            self.assertIn(frase, self.doc, frase)


if __name__ == "__main__":
    unittest.main()
