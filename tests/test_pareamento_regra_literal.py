"""Testes do adendo 48e (script 45): pareamento pela regra literal do 48d e PSM em 0,400 sem as categorias de um
lado só.

- Esquema, `natureza_dos_dados = EMPIRICO` e estatuto `ADENDO_48E_POS_RESULTADO` em todas as saídas `PM_*`.
- Running variable só o IVS 2010 oficial (a08); o arquivo local de IVS não é lido; nenhuma competência >= 202609;
  SHA-256 do adendo congelado; saídas `CL_*`, `HI_*` e `OC_*` iguais às registradas no resumo.
- Portão: PS-1 e PS-2 do 48d em 0,300 reproduzidos (<= 1e-8; 86 pares na H1 e 88 no ΔB1).
- Regra 2: quem saiu é exatamente quem pertence às categorias de um lado só; nenhuma categoria de um lado só sobra.
- Regra literal refeita aqui, de forma independente, a partir do escore gravado: mesmos pares de PM-1 e PM-2.
- Holm (8 linhas) e BKY (38 linhas) recalculados, com p = 1 nas linhas sem estimativa.
- Doc 57s: blocos idênticos aos gerados; decisões antes dos resultados; nenhum número fora dos blocos.
- Casos SINTÉTICOS em memória (rotulados "sintético"; nada vai para `output/`): regra literal e regra 2.
"""

from __future__ import annotations

import importlib.util
import math
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "rdd_bolsa"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "45_pareamento_regra_literal.py"
DOC = ROOT / "docs" / "06_execucao" / "57s_resultados_pareamento_regra_literal.md"
ADENDO = ROOT / "docs" / "06_execucao" / "48e_adendo_pareamento_regra_literal_e_0400.md"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


PM = _mod("pm45_teste", SCRIPT)
CL = PM.CL
L = PM.L
EST, BAL, EXC, RES = PM.ler_saidas()
CL_EST, CL_RES = PM.ler_cl()


class TestEsquemaENatureza(unittest.TestCase):
    def test_colunas(self):
        self.assertEqual(list(EST.columns), PM.COLUNAS)
        self.assertEqual(list(BAL.columns), PM.COLUNAS_BAL)
        self.assertEqual(list(EXC.columns), PM.COLUNAS_EXC)

    def test_natureza_e_estatuto(self):
        for df in (EST, BAL, EXC):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"ADENDO_48E_POS_RESULTADO"})
        self.assertEqual(RES["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(RES["estatuto"], "ADENDO_48E_POS_RESULTADO")

    def test_blocos_do_adendo(self):
        esperados = {"PM-1": 4, "PM-2": 4, "PM-3": 8, "PM-4": 8, "PM-5": 8, "PM-6": 8, "PM-7": 6, "PM-F": 8}
        self.assertEqual(EST["bloco"].value_counts().to_dict(), esperados)
        self.assertFalse(EST["id_linha"].duplicated().any())
        self.assertTrue(set(EST["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA"})
        self.assertTrue(EST.loc[EST["bloco"] != "PM-F", "regra2"].all())
        self.assertFalse(EST.loc[EST["bloco"] == "PM-F", "regra2"].any())
        self.assertEqual(set(EST.loc[EST["bloco"] == "PM-3", "regra_pareamento"]), {"gulosa"})
        self.assertEqual(set(EST.loc[EST["bloco"].isin(["PM-1", "PM-2", "PM-4", "PM-6", "PM-7", "PM-F"]),
                                     "regra_pareamento"]), {"literal"})

    def test_figuras_com_como_ler(self):
        nomes = {Path(f["arquivo"]).name for f in RES["figuras"]}
        self.assertEqual(nomes, {"PM_principal.png", "PM_escore_0400.png"})
        for f in RES["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists(), f["arquivo"])
            self.assertTrue(f["como_ler"].startswith("Como ler"))


class TestIntegridade(unittest.TestCase):
    def setUp(self):
        self.src = SCRIPT.read_text(encoding="utf-8")

    def test_ivs_oficial(self):
        self.assertNotIn("ivs_ipea_2010_municipios", self.src)
        self.assertNotIn("malha_municipios_regioes_saude", self.src)
        self.assertEqual(CL.A08.name, "a08_ivs_2010_oficial_municipio.csv")
        for x in RES["entradas"]:
            self.assertNotIn("ivs_ipea_2010_municipios", x["arquivo"])

    def test_sem_competencia_202609(self):
        comp = RES["parametros"]["competencias_pre"] + RES["parametros"]["competencias_pos_oferta_local"]
        self.assertTrue(all(c < "202609" for c in comp))

    def test_importa_o_44_sem_reescrever(self):
        self.assertIn("44_controles_localizacao_medicos.py", self.src)
        for f in ("def escore_propensao", "def parear_psm", "def inferencia_pareada", "def pareamentos"):
            self.assertNotIn(f, self.src)

    def test_nao_escreve_em_data(self):
        self.assertNotRegex(self.src, r"ROOT\s*/\s*\"data\"[^\n]*write")
        for v in RES["saidas"].values():
            self.assertTrue(v.startswith("output/") or v.startswith("docs/"), v)

    def test_adendo_congelado(self):
        self.assertEqual(PM.sha256(ADENDO), PM.SHA_ADENDO)
        self.assertEqual(RES["adendo"]["sha256"], PM.SHA_ADENDO)

    def test_saidas_de_outros_adendos_intactas(self):
        prot = RES["saidas_protegidas_sha256"]
        self.assertTrue(any(k.startswith("output/rdd_bolsa/CL_") for k in prot))
        self.assertTrue(any(k.startswith("output/rdd_bolsa/HI_") for k in prot))
        self.assertTrue(any(k.startswith("output/rdd_bolsa/OC_") for k in prot))
        self.assertEqual(PM.hashes_protegidos(), prot)


class TestPortao(unittest.TestCase):
    def test_portao(self):
        p = RES["portao"]
        self.assertTrue(p["aprovado"])
        self.assertLessEqual(p["max_abs_dif"], 1e-8)
        self.assertEqual(len(p["linhas"]), 4)
        for x in p["linhas"]:
            self.assertTrue(x["mesmos_pares"])
            r = CL._uma(CL_EST, bloco=x["linha"], outcome=x["outcome"], corte="0.300")
            self.assertAlmostEqual(float(r["tau"]), x["tau_48d"], places=12)
            self.assertEqual(int(r["n_pares"]), x["n_pares_refeito"])
        n = {x["outcome"]: x["n_pares_refeito"] for x in p["linhas"]}
        self.assertEqual(n["H1M-FRAC"], 86)
        self.assertEqual(n["dB1"], 88)

    def test_pm3_em_0300_igual_ao_48d(self):
        """Em 0,300 a regra 2 não tira ninguém: a PM-3 (gulosa com a regra 2) é o PS-1/PS-2 do 48d."""
        for parte in ("H1", "oferta_local"):
            am = PM._am(RES, parte, "0.300", 0.05)
            self.assertEqual(am["saiu_regra2"], {"abaixo": 0, "acima": 0})
        for _, r in EST[(EST["bloco"] == "PM-3") & (EST["corte"] == "0.300")].iterrows():
            ref = CL._uma(CL_EST, bloco="PS-1" if r["parte"] == "H1" else "PS-2", outcome=r["outcome"], corte="0.300")
            for k in ("tau", "ic95_inf", "ic95_sup", "p_valor", "n_pares"):
                self.assertAlmostEqual(float(r[k]), float(ref[k]), places=10, msg=k)


class TestRegra2(unittest.TestCase):
    def test_excluidos_batem_com_as_categorias(self):
        for am in RES["amostras"]:
            if not am["regra2"]:
                continue
            sub = EXC[(EXC["parte"] == am["parte"]) & (EXC["corte"] == am["corte"])
                      & (np.abs(EXC["janela"] - am["janela"]) < 1e-12)]
            n = am["saiu_regra2"]["abaixo"] + am["saiu_regra2"]["acima"]
            self.assertEqual(len(sub), n)
            self.assertEqual(am["categorias_um_lado_depois"], [])
            cats = {c["categoria"]: c for c in am["categorias_um_lado"]}
            for _, r in sub.iterrows():
                for c in r["categorias"].split(";"):
                    self.assertIn(c, cats)
                    self.assertEqual(r["lado"], cats[c]["lado"])
            soma = sum(c["unidades"] for c in cats.values())
            self.assertGreaterEqual(soma, len(sub))
            self.assertEqual(am["amostra_pareamento"]["abaixo"],
                             am["apos_covariavel"]["abaixo"] - am["saiu_regra2"]["abaixo"])
            self.assertEqual(am["amostra_pareamento"]["acima"],
                             am["apos_covariavel"]["acima"] - am["saiu_regra2"]["acima"])

    def test_0400_tira_capitais_e_regioes_de_um_lado(self):
        h1 = PM._am(RES, "H1", "0.400", 0.05)
        self.assertEqual({c["categoria"] for c in h1["categorias_um_lado"]},
                         {"capital", "regiao[Centro-Oeste]", "regiao[Sul]"})
        diag = next(x for x in CL_RES["amostra"]["pareamento"] if x["parte"] == "H1" and x["corte"] == "0.400"
                    and abs(x["janela"] - 0.05) < 1e-12)
        self.assertEqual({c["unidades"] for c in diag["escore"]["categorias_so_de_um_lado"]},
                         {c["unidades"] for c in h1["categorias_um_lado"]})
        self.assertTrue(set(EXC.loc[EXC["categorias"] == "capital", "capital"]) == {1})

    def test_principais_estimadas_em_0400(self):
        sub = EST[EST["bloco"].isin(["PM-1", "PM-2"]) & (EST["corte"] == "0.400")]
        self.assertEqual(set(sub["status"]), {"EXECUTADO"})
        sem = EST[(EST["bloco"] == "PM-F") & (EST["corte"] == "0.400")]
        self.assertEqual(set(sem["status"]), {"SEM_ESTIMATIVA"})


def _literal_independente(reg: dict, por_ciclo: bool) -> set[tuple[str, str]]:
    """Regra literal refeita do zero a partir do escore gravado (ordem decrescente do escore; empate pelo id)."""
    e = reg["escore_por_unidade"]
    ids, acima = e["id"], [bool(a) for a in e["acima"]]
    p = np.array(e["escore"], float)
    lp = np.log(p / (1 - p))
    lo, hi = reg["PSM"]["suporte_comum"]
    cal = reg["PSM"]["caliper_logit"]
    sup = (p >= lo - 1e-9) & (p <= hi + 1e-9)
    grupo = [i.split("|c")[1] if por_ciclo else "" for i in ids]
    n: dict[str, list[int]] = {}
    for g, a in zip(grupo, acima):
        n.setdefault(g, [0, 0])[0 if a else 1] += 1
    busca = sorted((k for k in range(len(ids)) if acima[k] == (n[grupo[k]][0] <= n[grupo[k]][1])),
                   key=lambda k: (-p[k], ids[k]))
    usados, pares = set(), set()
    for k in busca:
        if not sup[k]:
            continue
        cand = [(abs(lp[k] - lp[j]), ids[j]) for j in range(len(ids))
                if acima[j] != acima[k] and grupo[j] == grupo[k] and sup[j] and ids[j] not in usados
                and abs(lp[k] - lp[j]) <= cal + 1e-12]
        if not cand:
            continue
        _, par = min(cand)
        usados.update((ids[k], par))
        pares.add((ids[k], par) if acima[k] else (par, ids[k]))
    return pares


class TestRegraLiteralRefeita(unittest.TestCase):
    def test_pares_de_pm1_e_pm2(self):
        n = 0
        for reg in RES["pareamento"]:
            if reg["bloco"] not in ("PM-1", "PM-2", "PM-4", "PM-7") or not reg.get("escore_por_unidade"):
                continue
            gravados = {(x["acima"], x["abaixo"]) for x in reg["PSM"]["pares"]}
            self.assertEqual(_literal_independente(reg, reg["parte"] == "H1"), gravados,
                             f"{reg['bloco']} {reg['parte']} {reg['corte']}")
            n += 1
        self.assertEqual(n, 10)

    def test_pares_unicos(self):
        for reg in RES["pareamento"]:
            for met in ("PSM", "MAH"):
                pares = (reg.get(met) or {}).get("pares")
                if pares:
                    self.assertEqual(len({x["acima"] for x in pares}), len(pares))
                    self.assertEqual(len({x["abaixo"] for x in pares}), len(pares))


class TestMultiplicidade(unittest.TestCase):
    def _fam(self, blocos, col, fn, n):
        m = EST["bloco"].isin(blocos)
        self.assertEqual(int(m.sum()), n)
        self.assertTrue(EST.loc[m, "entra_holm" if col == "p_holm" else "entra_bky"].all())
        exe = EST.loc[m, "status"] == "EXECUTADO"
        p = np.where(exe, EST.loc[m, "p_valor"].astype(float), 1.0)
        adj = fn(p)
        np.testing.assert_allclose(adj[exe.to_numpy()], EST.loc[m, col].astype(float).to_numpy()[exe.to_numpy()],
                                   atol=1e-12)
        self.assertTrue(EST.loc[m, col][~exe].isna().all())

    def test_holm(self):
        self._fam(("PM-1", "PM-2"), "p_holm", L.holm, 8)
        self.assertFalse(EST.loc[~EST["bloco"].isin(["PM-1", "PM-2"]), "entra_holm"].any())

    def test_bky(self):
        self._fam(("PM-3", "PM-4", "PM-5", "PM-6", "PM-7"), "q_bky", L.qvalores_bky, 38)
        self.assertFalse(EST.loc[EST["bloco"].isin(["PM-1", "PM-2", "PM-F"]), "entra_bky"].any())


class TestCoerencia(unittest.TestCase):
    def test_ic_e_limpa(self):
        par = EST[EST["metodo"].isin(["pareamento_psm", "pareamento_mahalanobis"]) & (EST["status"] == "EXECUTADO")]
        for _, r in par.iterrows():
            self.assertGreaterEqual(int(r["n_pares"]), 2)
            self.assertLessEqual(float(r["ic95_inf"]), float(r["tau"]))
            self.assertGreaterEqual(float(r["ic95_sup"]), float(r["tau"]))
            limpa = "SIM" if float(r["max_abs_dp_depois"]) <= CL.LIMIAR_DP_LIMPA else "NAO"
            self.assertEqual(r["comparacao_limpa"], limpa)

    def test_leitura_pelas_regras(self):
        le = RES["leitura"]
        princ = EST[EST["bloco"].isin(["PM-1", "PM-2"])]
        todas = all(r["status"] == "EXECUTADO" and float(r["ic95_inf"]) <= 0 <= float(r["ic95_sup"])
                    and r["comparacao_limpa"] == "SIM" for _, r in princ.iterrows())
        rejeita = bool((princ["p_holm"].astype(float) < 0.05).any())
        esperado = ("REJEITA_ZERO_DEPOIS_DO_HOLM" if rejeita else
                    "NAO_SE_DETECTA_DIFERENCA" if todas else "PRIMEIRA_LEITURA_NAO_SE_APLICA")
        self.assertEqual(le["geral"], esperado)
        dep = set()
        for _, r in princ.iterrows():
            g = CL._uma(EST, bloco="PM-3", outcome=r["outcome"], corte=r["corte"])
            if (float(r["tau"]) * float(g["tau"]) < 0 and float(r["ic95_inf"]) <= 0 <= float(r["ic95_sup"])
                    and float(g["ic95_inf"]) <= 0 <= float(g["ic95_sup"])):
                dep.add((r["outcome"], r["corte"]))
        self.assertEqual({(x["outcome"], x["corte"]) for x in le["depende_da_regra"]}, dep)
        for x in le["parte_comparavel"]:
            self.assertTrue(any(v > 0.25 for v in x["fracao"].values()))


class TestDoc(unittest.TestCase):
    def test_blocos_iguais_ao_gerado(self):
        txt = DOC.read_text(encoding="utf-8")
        achados = {m.group("nome"): m.group("corpo") for m in PM.MARCA.finditer(txt)}
        gerados = PM.gerar_blocos(EST, BAL, EXC, RES, CL_EST)
        self.assertEqual(set(gerados), set(achados))
        for nome, corpo in gerados.items():
            self.assertEqual(achados[nome].rstrip(), corpo.rstrip(), nome)

    def test_cabecalho_decisoes_e_linguagem(self):
        txt = DOC.read_text(encoding="utf-8")
        self.assertIn("ADENDO_48E_POS_RESULTADO", txt)
        self.assertIn("**Auditoria:** [auditoria 43]", txt)
        self.assertIn("## 0. Decisões de implementação", txt)
        self.assertLess(txt.index("## 0. Decisões"), txt.index("## 1. Resposta curta"))
        for proibido in ("a bolsa reduz", "a bolsa aumenta", "a bolsa causa", "efeito da bolsa sobre"):
            self.assertNotIn(proibido, txt.lower())

    def test_sem_numeros_fora_dos_blocos(self):
        txt = DOC.read_text(encoding="utf-8")
        resto = PM.MARCA.sub("", txt[txt.index("## 1. Resposta curta"):])
        parametros = {"0,300", "0,400", "0,050", "0,020", "0,10", "0,25"}
        self.assertEqual(set(re.findall(r"\d+,\d{2,}", resto)) - parametros, set())


class TestSintetico(unittest.TestCase):
    """sintético: dados construídos aqui, só em memória."""

    def test_regra_literal_difere_da_gulosa(self):
        # sintético: a1 procura primeiro (lado de cima tem menos) e fica com b1; a gulosa daria a2-b1 primeiro.
        cand = [(0.3, "a1", "b1"), (0.1, "a2", "b1"), (0.5, "a2", "b2")]
        acima = {"a1": True, "a2": True, "b1": False, "b2": False, "b3": False}
        grupo = {k: None for k in acima}
        chave = {"a1": (-0.9, "a1"), "a2": (-0.8, "a2"), "b1": (0, "b1"), "b2": (0, "b2"), "b3": (0, "b3")}
        self.assertEqual(PM.regra_literal(cand, acima, grupo, chave), [("a1", "b1", 0.3), ("a2", "b2", 0.5)])
        self.assertEqual(CL.guloso_global(cand), [("a2", "b1", 0.1)])

    def test_lado_menor_procura_e_empate(self):
        # sintético: em empate (2 × 2), procura o lado de cima.
        cand = [(0.2, "a1", "b1"), (0.1, "a2", "b1")]
        acima = {"a1": True, "a2": True, "b1": False, "b2": False}
        grupo = {k: None for k in acima}
        chave = {"a1": (-0.9, "a1"), "a2": (-0.1, "a2"), "b1": (0, "b1"), "b2": (0, "b2")}
        self.assertEqual(PM.regra_literal(cand, acima, grupo, chave), [("a1", "b1", 0.2)])
        # sintético: com 3 abaixo e 1 acima no grupo "x", o de cima procura; no grupo "y", com 1 abaixo, procura b9.
        acima2 = {"a1": True, "b1": False, "b2": False, "b3": False, "a8": True, "a9": True, "b9": False}
        grupo2 = {"a1": "x", "b1": "x", "b2": "x", "b3": "x", "a8": "y", "a9": "y", "b9": "y"}
        chave2 = {k: (k,) for k in acima2}
        cand2 = [(0.4, "a1", "b2"), (0.3, "a1", "b3"), (0.2, "a8", "b9"), (0.1, "a9", "b9")]
        self.assertEqual(PM.regra_literal(cand2, acima2, grupo2, chave2), [("a1", "b3", 0.3), ("a9", "b9", 0.1)])

    def test_regra2_uma_passada(self):
        # sintético: capital só abaixo e Sul só abaixo saem; o resto fica.
        d = pd.DataFrame({"id": list("abcdef"), "co_ibge": list("abcdef"),
                          "acima": [False, False, True, True, False, True],
                          "capital": [1, 0, 0, 0, 0, 0],
                          "regiao": ["Norte", "Sul", "Norte", "Nordeste", "Nordeste", "Norte"]})
        fica, cats, por_id = PM.regra2(d)
        self.assertEqual({c["categoria"] for c in cats}, {"capital", "regiao[Sul]"})
        self.assertEqual(list(d.loc[fica, "id"]), ["c", "d", "e", "f"])
        self.assertEqual(por_id, {"a": ["capital"], "b": ["regiao[Sul]"]})


if __name__ == "__main__":
    unittest.main()
