"""Testes do adendo 48h (script 49): H1 pareada pela localização da unidade (exato na UF e em capital) e dos médicos
(especialistas do curso num raio de 100 km).

- Esquema, `natureza_dos_dados = EMPIRICO` e estatuto `ADENDO_48H_POS_RESULTADO` em todas as saídas `PL_*`.
- IVS oficial (a08); o arquivo local de IVS não é lido; nenhuma competência >= 202609; SHA-256 do adendo; saídas
  `HI_*`, `CL_*`, `PM_*`, `PO_*` e `X1_*` iguais às registradas; o script importa o 44 e o 45 sem reescrevê-los.
- Portão: PM-1 do 48e em 0,300 reproduzido (<= 1e-8, mesmos pares); centroides iguais ao manifesto do 17.
- Exato: todo par da PH-1 e da PH-2 na mesma UF, mesma condição de capital e mesmo ciclo.
- Regra literal refeita de forma independente, a partir do escore gravado e do estrato exato: mesmos pares.
- Regra 2: quem saiu bate com as categorias de um lado só (UF e capital).
- Origem (X1) só como outcome: fora do escore; PH-5 com os pares da PH-1.
- Holm (4) e BKY (16) recalculados; leitura do §3 refeita.
- Doc 57w: blocos idênticos aos gerados; decisões antes dos resultados; nenhum número fora dos blocos.
- Casos SINTÉTICOS em memória (rotulados "sintético"; nada vai para `output/`): média ponderada do raio e regra 2 na UF.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "rdd_bolsa"
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "49_pareamento_localizacao.py"
DOC = ROOT / "docs" / "06_execucao" / "57w_resultados_pareamento_localizacao.md"
ADENDO = ROOT / "docs" / "06_execucao" / "48h_adendo_pareamento_localizacao_unidade_e_medicos.md"


def _mod(nome: str, caminho: Path):
    if nome in sys.modules:
        return sys.modules[nome]
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


PL = _mod("pl49_teste", SCRIPT)
CL, PM, L = PL.CL, PL.PM, PL.L
EST, BAL, EXC, RES = PL.ler_saidas()
PM_EST, CL_EST, HI = PL.referencias()
PL._carregar_siglas()
CAPITAIS = set(CL.T41.A36.CAPITAIS)


class TestEsquemaENatureza(unittest.TestCase):
    def test_colunas(self):
        self.assertEqual(list(EST.columns), PL.COLUNAS)
        self.assertEqual(list(BAL.columns), PL.COLUNAS_BAL)
        self.assertEqual(list(EXC.columns), PL.COLUNAS_EXC)

    def test_natureza_e_estatuto(self):
        for df in (EST, BAL, EXC):
            self.assertEqual(set(df["natureza_dos_dados"]), {"EMPIRICO"})
            self.assertEqual(set(df["estatuto"]), {"ADENDO_48H_POS_RESULTADO"})
        self.assertEqual(RES["natureza_dos_dados"], "EMPIRICO")
        self.assertEqual(RES["estatuto"], "ADENDO_48H_POS_RESULTADO")

    def test_linhas_do_adendo(self):
        self.assertEqual(EST["bloco"].value_counts().to_dict(),
                         {"PH-1": 4, "PH-2": 8, "PH-3": 4, "PH-4": 4, "PH-5": 4})
        self.assertFalse(EST["id_linha"].duplicated().any())
        self.assertTrue(set(EST["status"]) <= {"EXECUTADO", "SEM_ESTIMATIVA"})
        self.assertEqual(set(EST.loc[EST["bloco"] == "PH-2", "raio_km"].astype(int)), {50, 200})
        self.assertEqual(set(EST.loc[EST["bloco"] != "PH-2", "raio_km"].astype(int)), {100})
        self.assertTrue(EST.loc[EST["bloco"] == "PH-3", "exato"].str.startswith("regiao_saude").all())
        self.assertTrue(EST.loc[EST["bloco"].isin(["PH-1", "PH-2", "PH-5"]), "exato"].str.startswith("cd_uf").all())
        self.assertTrue(EST.loc[EST["bloco"] != "PH-4", "regra2"].all())

    def test_figuras_com_como_ler(self):
        nomes = {Path(f["arquivo"]).name for f in RES["figuras"]}
        self.assertEqual(nomes, {"PL_principal.png", "PL_balanco.png", "PL_origem.png"})
        for f in RES["figuras"]:
            self.assertTrue((ROOT / f["arquivo"]).exists(), f["arquivo"])
            self.assertTrue(f["como_ler"].startswith("Como ler"))


class TestIntegridade(unittest.TestCase):
    def setUp(self):
        self.src = SCRIPT.read_text(encoding="utf-8")

    def test_ivs_oficial(self):
        self.assertNotIn("ivs_ipea_2010_municipios", self.src)
        self.assertNotIn("malha_municipios_regioes_saude", self.src)
        for x in RES["entradas"]:
            self.assertNotIn("ivs_ipea_2010_municipios", x["arquivo"])

    def test_sem_competencia_202609(self):
        self.assertTrue(all(c < "202609" for c in RES["parametros"]["competencias_pre"]))

    def test_importa_44_e_45_sem_reescrever(self):
        self.assertIn("44_controles_localizacao_medicos.py", self.src)
        self.assertIn("45_pareamento_regra_literal.py", self.src)
        for f in ("def escore_propensao", "def parear_psm", "def inferencia_pareada", "def pareamentos",
                  "def regra_literal", "def regra2", "def haversine_km", "def ler_listas_pmme"):
            self.assertNotIn(f, self.src)
        self.assertIs(PM.CL, CL)

    def test_trocas_desfeitas(self):
        self.assertEqual(CL.CONJUNTOS["L+M"], ("capital", "regiao", "log_pop", "med", "esp", "esp_resto"))
        self.assertEqual(PM.categorias.__module__, PM.__name__)
        self.assertEqual(CL._col_bal.__module__, CL.__name__)

    def test_nao_escreve_em_data(self):
        self.assertNotRegex(self.src, r"ROOT\s*/\s*\"data\"[^\n]*write")
        for v in RES["saidas"].values():
            self.assertTrue(v.startswith("output/") or v.startswith("docs/"), v)

    def test_adendo_congelado(self):
        self.assertEqual(PL.sha256(ADENDO), PL.SHA_ADENDO)
        self.assertEqual(RES["adendo"]["sha256"], PL.SHA_ADENDO)

    def test_saidas_de_outros_adendos_intactas(self):
        prot = RES["saidas_protegidas_sha256"]
        for pref in ("HI_", "CL_", "PM_", "PO_", "X1_"):
            self.assertTrue(any(k.startswith("output/rdd_bolsa/" + pref) for k in prot), pref)
        self.assertEqual(PL.hashes_protegidos(), prot)

    def test_sem_identificador_de_medico(self):
        for df in (EST, BAL, EXC):
            for c in df.columns:
                self.assertFalse(df[c].astype(str).str.contains("x1m_").any(), c)
        self.assertNotIn("x1m_", (OUT / PL.NOME_RESUMO).read_text(encoding="utf-8"))


class TestPortao(unittest.TestCase):
    def test_pm1_reproduzido(self):
        p = RES["portao"]
        self.assertTrue(p["aprovado"])
        self.assertLessEqual(p["max_abs_dif"], 1e-8)
        self.assertEqual(len(p["linhas"]), 2)
        for x in p["linhas"]:
            self.assertTrue(x["mesmos_pares"])
            r = CL._uma(PM_EST, bloco="PM-1", outcome=x["outcome"], corte="0.300")
            self.assertAlmostEqual(float(r["tau"]), x["tau_48e"], places=12)
            self.assertEqual(int(r["n_pares"]), x["n_pares_refeito"])

    def test_centroides(self):
        c = RES["portao"]["centroides"]
        self.assertEqual(PL.sha256(PL.COORD), c["sha256"])
        self.assertEqual(c["sha256"], c["sha256_manifesto_17"])
        self.assertEqual(c["sha256"], c["sha256_x1_ligacao_resumo"])
        self.assertEqual(PL.sha256(PL.X1_MED), c["x1_medicos"]["sha256"])


def _regs(blocos=("PH-1", "PH-2", "PH-3")):
    return [r for r in RES["pareamento"] if r["bloco"] in blocos]


class TestExatoERegraLiteral(unittest.TestCase):
    def test_pares_na_mesma_uf_capital_e_ciclo(self):
        n = 0
        for rg in _regs(("PH-1", "PH-2")):
            for p in rg["PSM"]["pares"]:
                a, b = p["acima"], p["abaixo"]
                self.assertEqual(a[:2], b[:2])
                self.assertEqual(a.split("|")[1], b.split("|")[1])
                self.assertEqual(a[:6] in CAPITAIS, b[:6] in CAPITAIS)
                n += 1
        self.assertGreater(n, 0)

    def test_regra_literal_refeita(self):
        for rg in _regs(("PH-1", "PH-2")):
            e = rg["escore_por_unidade"]
            ids, acima = e["id"], [bool(a) for a in e["acima"]]
            p = np.array(e["escore"], float)
            lp = np.log(p / (1 - p))
            lo, hi = rg["PSM"]["suporte_comum"]
            cal = rg["PSM"]["caliper_logit"]
            sup = (p >= lo - 1e-9) & (p <= hi + 1e-9)
            ciclo = [i.split("|c")[1] for i in ids]
            estr = [f"{i[:2]}|{int(i[:6] in CAPITAIS)}|{c}" for i, c in zip(ids, ciclo)]
            n: dict[str, list[int]] = {}
            for g, a in zip(ciclo, acima):
                n.setdefault(g, [0, 0])[0 if a else 1] += 1
            busca = sorted((k for k in range(len(ids)) if acima[k] == (n[ciclo[k]][0] <= n[ciclo[k]][1])),
                           key=lambda k: (-p[k], ids[k]))
            usados, pares = set(), set()
            for k in busca:
                if not sup[k]:
                    continue
                cand = [(abs(lp[k] - lp[j]), ids[j]) for j in range(len(ids))
                        if acima[j] != acima[k] and estr[j] == estr[k] and sup[j] and ids[j] not in usados
                        and abs(lp[k] - lp[j]) <= cal + 1e-12]
                if not cand:
                    continue
                _, par = min(cand)
                usados.update((ids[k], par))
                pares.add((ids[k], par) if acima[k] else (par, ids[k]))
            gravados = {(x["acima"], x["abaixo"]) for x in rg["PSM"]["pares"]}
            self.assertEqual(pares, gravados, f"{rg['bloco']} {rg['raio_km']} {rg['corte']}")

    def test_escore_sem_origem_nem_localizacao(self):
        self.assertEqual(RES["parametros"]["escore"], ["log_pop", "med", "esp", "raio"])
        for rg in _regs():
            self.assertEqual(set(rg["escore"]["colunas"]) - {"const"}, {"log_pop", "med", "esp", "raio"})

    def test_ph3_no_mesmo_ciclo_e_pares_unicos(self):
        for rg in _regs():
            pares = rg["PSM"]["pares"]
            self.assertEqual(len({x["acima"] for x in pares}), len(pares))
            self.assertEqual(len({x["abaixo"] for x in pares}), len(pares))
            for x in pares:
                self.assertEqual(x["acima"].split("|")[1], x["abaixo"].split("|")[1])
                self.assertEqual(x["acima"][:2], x["abaixo"][:2])     # CIR dentro da UF


class TestRegra2(unittest.TestCase):
    def test_excluidos_batem_com_as_categorias(self):
        for rg in _regs(("PH-1", "PH-2")):
            am = rg["amostra_48h"]
            sub = EXC[(EXC["bloco"] == rg["bloco"]) & (EXC["corte"] == am["corte"])
                      & (EXC["raio_km"].astype(int) == int(rg["raio_km"]))]
            self.assertEqual(len(sub), am["saiu_regra2"]["abaixo"] + am["saiu_regra2"]["acima"])
            cats = {c["categoria"]: c for c in am["categorias_um_lado"]}
            self.assertTrue(all(c == "capital" or c == "nao capital" or c.startswith("uf[") for c in cats))
            for _, r in sub.iterrows():
                for c in r["categorias"].split(";"):
                    self.assertIn(c, cats)
                    self.assertEqual(r["lado"], cats[c]["lado"])
                    if c.startswith("uf["):
                        self.assertEqual(str(r["co_ibge"])[:2], c[3:5])
            self.assertEqual(am["amostra_pareamento"]["abaixo"],
                             am["apos_covariavel"]["abaixo"] - am["saiu_regra2"]["abaixo"])
            self.assertEqual(am["amostra_pareamento"]["acima"],
                             am["apos_covariavel"]["acima"] - am["saiu_regra2"]["acima"])

    def test_uf_de_um_lado_so_nao_entra_em_par(self):
        for rg in _regs(("PH-1",)):
            fora = {c["categoria"][3:5] for c in rg["amostra_48h"]["categorias_um_lado"] if c["categoria"][:3] == "uf["}
            for p in rg["PSM"]["pares"]:
                self.assertNotIn(p["acima"][:2], fora)


class TestOrigemComoOutcome(unittest.TestCase):
    def test_ph5_usa_os_pares_da_ph1(self):
        for c in ("0.300", "0.400"):
            r1 = CL._uma(EST, bloco="PH-1", outcome="H1M-FRAC", corte=c)
            for oid in PL.OUT_PH5:
                r5 = CL._uma(EST, bloco="PH-5", outcome=oid, corte=c)
                self.assertEqual(int(r5["n_pares"]) + int(r5["pares_sem_outcome"]), int(r1["n_pares"]))
                self.assertEqual(r5["max_abs_dp_depois"], r1["max_abs_dp_depois"])
            m = next(x for x in RES["ph5_medias"] if x["corte"] == c)
            self.assertEqual(m["pares_ciclos_1_2"], int(CL._uma(EST, bloco="PH-5", outcome="H1M-OUTRA-UF",
                                                               corte=c)["n_pares"]))

    def test_x1_conferida(self):
        x = RES["x1"]
        self.assertEqual(x["regra_ligacao"], "d1_pos_hoc")
        self.assertEqual(x["conferencia_listas"], {"ciclo": 0, "co_ibge": 0, "fonte_lista": 0})
        o = x["origem_em_celula_com_vaga_imediata"]
        self.assertEqual(sum(o.values()), x["em_celula_com_vaga_imediata"])
        self.assertEqual(x["em_celula_com_vaga_imediata"] + x["em_celula_so_cadastro_reserva"]
                         + x["sem_celula_no_quadro"], x["registros"])

    def test_sinais_e_p_minimo(self):
        for m in RES["ph5_medias"]:
            for g in m["sinais"].values():
                self.assertEqual(g["acima_maior"] + g["abaixo_maior"], g["diferentes_de_zero"])
                self.assertAlmostEqual(g["p_minimo_permutacao"], 2.0 ** (1 - g["diferentes_de_zero"]))


class TestMultiplicidade(unittest.TestCase):
    def _fam(self, blocos, col, fn, n):
        m = EST["bloco"].isin(blocos)
        self.assertEqual(int(m.sum()), n)
        exe = (EST.loc[m, "status"] == "EXECUTADO").to_numpy()
        p = np.where(exe, EST.loc[m, "p_valor"].astype(float), 1.0)
        np.testing.assert_allclose(fn(p)[exe], EST.loc[m, col].astype(float).to_numpy()[exe], atol=1e-12)
        self.assertTrue(EST.loc[m, col][~exe].isna().all())

    def test_holm(self):
        self._fam(("PH-1",), "p_holm", L.holm, 4)
        self.assertFalse(EST.loc[EST["bloco"] != "PH-1", "entra_holm"].any())

    def test_bky(self):
        self._fam(("PH-2", "PH-3", "PH-5"), "q_bky", L.qvalores_bky, 16)
        self.assertFalse(EST.loc[EST["bloco"].isin(["PH-1", "PH-4"]), "entra_bky"].any())


class TestCoerencia(unittest.TestCase):
    def test_ic_e_limpa(self):
        par = EST[(EST["metodo"] == "pareamento_psm") & (EST["status"] == "EXECUTADO")]
        for _, r in par.iterrows():
            self.assertGreaterEqual(int(r["n_pares"]), 2)
            self.assertLessEqual(float(r["ic95_inf"]), float(r["tau"]))
            self.assertGreaterEqual(float(r["ic95_sup"]), float(r["tau"]))
            self.assertEqual(r["comparacao_limpa"], "SIM" if float(r["max_abs_dp_depois"]) <= 0.25 else "NAO")

    def test_uf_e_capital_balanceadas_depois(self):
        sub = BAL[BAL["bloco"].isin(["PH-1", "PH-2", "PH-3"])
                  & (BAL["variavel"].str.startswith("uf_") | (BAL["variavel"] == "capital"))]
        dep = sub["dp_depois"].dropna().abs()
        self.assertTrue((dep < 1e-12).all())

    def test_leitura(self):
        le = RES["leitura"]
        princ = EST[EST["bloco"] == "PH-1"]
        todas = all(r["status"] == "EXECUTADO" and float(r["ic95_inf"]) <= 0 <= float(r["ic95_sup"])
                    and r["comparacao_limpa"] == "SIM" for _, r in princ.iterrows())
        rejeita = bool((princ["p_holm"].astype(float) < 0.05).any())
        self.assertEqual(le["geral"], "REJEITA_ZERO_DEPOIS_DO_HOLM" if rejeita else
                         "NAO_SE_DETECTA_DIFERENCA" if todas else "PRIMEIRA_LEITURA_NAO_SE_APLICA")
        for x in le["ph5"]:
            r = CL._uma(EST, bloco="PH-5", outcome="H1M-OUTRA-UF", corte=x["corte"])
            ind = float(r["tau"]) > 0 and not (float(r["ic95_inf"]) <= 0 <= float(r["ic95_sup"]))
            self.assertEqual(x["codigo"], "INDICIO_ATRAI_DE_LONGE" if ind else "SEM_INDICIO_DE_ATRAIR_DE_LONGE")
        for x in le["parte_comparavel"]:
            self.assertTrue(any(v > 0.25 for v in x["fracao"].values()))


class TestDoc(unittest.TestCase):
    def test_blocos_iguais_ao_gerado(self):
        txt = DOC.read_text(encoding="utf-8")
        achados = {m.group("nome"): m.group("corpo") for m in PL.MARCA.finditer(txt)}
        gerados = PL.gerar_blocos(EST, BAL, EXC, RES, PM_EST, CL_EST, HI)
        self.assertEqual(set(gerados), set(achados))
        for nome, corpo in gerados.items():
            self.assertEqual(achados[nome].rstrip(), corpo.rstrip(), nome)

    def test_cabecalho_decisoes_e_linguagem(self):
        txt = DOC.read_text(encoding="utf-8")
        self.assertIn("ADENDO_48H_POS_RESULTADO", txt)
        self.assertIn("**Auditoria:** pendente", txt)
        self.assertIn("## 0. Decisões de implementação", txt)
        self.assertLess(txt.index("## 0. Decisões"), txt.index("## 1. Resposta curta"))
        for proibido in ("a bolsa reduz", "a bolsa aumenta", "a bolsa causa", "efeito da bolsa sobre"):
            self.assertNotIn(proibido, txt.lower())

    def test_sem_numeros_fora_dos_blocos(self):
        txt = DOC.read_text(encoding="utf-8")
        resto = PL.MARCA.sub("", txt[txt.index("## 1. Resposta curta"):])
        parametros = {"0,300", "0,400", "0,050", "0,10", "0,25"}
        self.assertEqual(set(re.findall(r"\d+,\d{2,}", resto)) - parametros, set())


class TestSintetico(unittest.TestCase):
    """sintético: dados construídos aqui, só em memória."""

    def test_media_ponderada_do_raio(self):
        # sintético: município 100001 com duas células com vaga imediata (cursos 1 e 2, pesos 3 e 1) e uma de curso
        # 17 (fora da ponte, sai da média); município 100002 só com curso 18 (raio ausente).
        ck = pd.DataFrame({"co_ibge": ["100001"] * 4 + ["100002"], "cod_curso": [1, 2, 17, 3, 18],
                           "tipo_celula": ["so_imed", "mista", "so_imed", "so_cr", "so_imed"],
                           "vagas_imediatas": [3.0, 1.0, 2.0, 0.0, 1.0]})
        mk = pd.DataFrame({"co_ibge": ["100001", "100002"], "vi_imed": [6.0, 1.0]})
        b = {"CK": {k: ck for k in PL.CICLOS}, "MK": {k: mk for k in PL.CICLOS}}
        tab = pd.DataFrame({"co_ibge": ["100001"] * 3, "cod_curso": [1, 2, 3],
                            **{f"raio_{R}": [10.0, 30.0, 99.0] for R in PL.RAIOS}})
        un, _, info = PL.raio_unidades(b, tab)
        u1 = un[(un["co_ibge"] == "100001") & (un["ciclo"] == 1)].iloc[0]
        self.assertAlmostEqual(u1["raio_100"], (3 * 10 + 1 * 30) / 4)
        u2 = un[(un["co_ibge"] == "100002") & (un["ciclo"] == 1)].iloc[0]
        self.assertTrue(np.isnan(u2["raio_100"]))
        self.assertEqual(info["ciclo_1"]["so_cursos_fora_da_ponte"], 1)

    def test_regra2_na_uf(self):
        # sintético: UF 12 só acima e capital só abaixo saem; UF 29 dos dois lados fica.
        d = pd.DataFrame({"id": list("abcde"), "co_ibge": ["120001", "290001", "290002", "290003", "130001"],
                          "acima": [True, False, True, False, True], "capital": [0, 1, 0, 0, 0],
                          "cd_uf": ["12", "29", "29", "29", "13"]})
        orig = PM.categorias
        PM.categorias = PL.categorias_uf
        try:
            fica, cats, por_id = PM.regra2(d)
        finally:
            PM.categorias = orig
        self.assertEqual({c["categoria"] for c in cats}, {"capital", "uf[12]", "uf[13]"})
        self.assertEqual(list(d.loc[fica, "id"]), ["c", "d"])
        self.assertEqual(por_id["b"], ["capital"])


if __name__ == "__main__":
    unittest.main()
