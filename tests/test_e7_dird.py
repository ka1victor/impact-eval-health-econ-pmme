"""Testes do E7 (`scripts/rdd_bolsa/14_estimar_E7_dird_cnes.py`), DiRD no CNES (família F3).

Duas partes:

1. `TestE7Sintetico*`: a cola do pipeline com DADOS SINTÉTICOS gerados em
   memória (semente fixa). Nada é gravado em `output/` nem em `data/`; os dados
   sintéticos só servem para conferir que o código recupera saltos conhecidos
   (DiRD, níveis, placebo, estudo de evento), que horas ausentes nunca viram
   zero, que as validações falham fechado e que as tabelas do doc são geradas.
2. `TestE7SaidasReais`: invariantes das saídas versionadas em
   `output/rdd_bolsa/E7_*` (pulados enquanto as saídas não existem). Todo alvo
   é lido de arquivos de `output/` ou recalculado; nenhum número é digitado.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rdd_bolsa" / "14_estimar_E7_dird_cnes.py"
_bytecode = sys.dont_write_bytecode
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("e7_dird_14", SCRIPT)
E7 = importlib.util.module_from_spec(_spec)
sys.modules["e7_dird_14"] = E7
_spec.loader.exec_module(E7)
sys.dont_write_bytecode = _bytecode

OUT = ROOT / "output" / "rdd_bolsa"
EST = OUT / "E7_estimativas.csv"
EVENTO = OUT / "E7_estudo_evento.csv"
RESUMO = OUT / "E7_resumo.json"
DOC = ROOT / "docs" / "06_execucao" / "43_resultados_E7_dird_cnes.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# --------------------------------------------------------------------------
# Dados sintéticos (só em memória)
# --------------------------------------------------------------------------

SALTO_FIXO_SINTETICO = 1.0     # descontinuidade constante no tempo (co-política fixa)
SALTO_POS_SINTETICO = 2.0      # salto adicional só no pós (o que a DiRD deve recuperar)
POP_SINTETICA = 1_000_000.0    # população constante: vínculos por 10 mil = n / 100


def painel_sintetico(semente: int = 11, n: int = 3000, horas_ausentes: int = 0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Painel sintético no formato do a09 e tabela de municípios (s_mil, população).

    alvo_pmme: taxa = 5 + 10 s + a_i + (salto fixo + salto no pós) x degraus + ruído, com
    degraus = 1[s > 0,3] + 1[s > 0,4] e a_i efeito fixo persistente do município. Generalistas e demais
    grupos: só o salto fixo (placebo sem salto no pós).
    """
    rng = np.random.default_rng(semente)
    s = rng.integers(200, 501, n).astype(float)
    cod = [f"9{i:05d}" for i in range(n)]
    degraus = (s > 300).astype(float) + (s > 400).astype(float)   # um degrau em cada corte, como a bolsa
    pop = pd.DataFrame({"co_ibge": cod, "s_mil": s, "populacao_2022": POP_SINTETICA})
    linhas = []
    comps = list(E7.COMP_EVENTO)
    for g in E7.GRUPOS_USADOS:
        a_i = rng.normal(0, 1.5, n)
        for comp in comps:
            pos = comp in E7.COMP_POS
            taxa = 5 + 10 * s / 1000 + a_i + SALTO_FIXO_SINTETICO * degraus
            if g == "alvo_pmme" and pos:
                taxa = taxa + SALTO_POS_SINTETICO * degraus
            taxa = taxa + rng.normal(0, 0.2, n)
            nv = np.maximum(np.round(taxa * POP_SINTETICA / E7.ESCALA_HAB), 0).astype(int)
            linhas.append(pd.DataFrame({
                "co_ibge": cod, "competencia": comp, "grupo": g, "n_vinculos": nv, "n_profissionais_distintos": nv,
                E7.COL_HORAS_SUS: pd.array(nv * 20, dtype="Int32"),
                E7.COL_HORAS_SEM_FILTRO: pd.array(nv * 25, dtype="Int32"),
                E7.COL_HORAS_PARCIAL: pd.array(nv * 20, dtype="Int32"), "n_vinculos_horas_ausentes": 0,
                "tem_profissional": (nv > 0).astype("int8"), "natureza_dos_dados": "EMPIRICO"}))
    painel = pd.concat(linhas, ignore_index=True)
    if horas_ausentes:
        alvo = (painel["grupo"] == "alvo_pmme") & painel["co_ibge"].isin(cod[:horas_ausentes]) & \
               (painel["competencia"] == E7.COMP_PRE[0])
        painel.loc[alvo, E7.COL_HORAS_SUS] = pd.NA
        painel.loc[alvo, E7.COL_HORAS_SEM_FILTRO] = pd.NA
        painel.loc[alvo, E7.COL_HORAS_PARCIAL] = painel.loc[alvo, "n_vinculos"].to_numpy() * 10   # soma parcial
        painel.loc[alvo, "n_vinculos_horas_ausentes"] = 1
    return painel, pop


def sup_sintetico(cod: list[str]) -> dict:
    """Atributos S3/S4 sintéticos: porte e Amazônia Legal alternados por município."""
    rng = np.random.default_rng(3)
    porte = pd.Series(rng.integers(1, 5, len(cod)), index=cod)
    am = pd.Series(rng.integers(0, 2, len(cod)).astype(float), index=cod)
    return {"S3": {"tabela": porte, "portes_muda": {300: {2, 3}, 400: {1, 2, 4}}},
            "S4": {"tabela": am, "definicao": "sintetico"}}


SPEC_F31 = next(c for c in E7.CATALOGO if c["id"] == "F3.1")
SPEC_F33 = next(c for c in E7.CATALOGO if c["id"] == "F3.3")
SPEC_F33_PARCIAL = next(c for c in E7.CATALOGO if c["id"] == "F3.3.soma_parcial")
SPEC_F33_SEM_FILTRO = next(c for c in E7.CATALOGO if c["id"] == "F3.3.sem_filtro_sus")
SPEC_P1 = next(c for c in E7.CATALOGO if c["id"] == "F3.P1")


class TestE7SinteticoRecuperaSaltos(unittest.TestCase):
    """Dados sintéticos: a DiRD recupera o salto do pós; o nível mostra o pacote; placebo e pré ficam em zero."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.painel, cls.pop = painel_sintetico()
        cls.serie = E7.serie_outcome(cls.painel, SPEC_F31, cls.pop)
        lr = {("U", 300): 10, ("U", 400): 10}
        cls.linhas, cls.info, cls.base = E7.estimar_outcome(SPEC_F31, "U", cls.serie,
                                                            sup=sup_sintetico(list(cls.pop["co_ibge"])), lr=lr)
        cls.est = E7.aplicar_bky(pd.DataFrame(cls.linhas)[E7.COLUNAS_SAIDA])
        cls.ev = pd.DataFrame(E7.estudo_evento(SPEC_F31, "U", cls.serie))[E7.COLUNAS_EVENTO]

    def _linha(self, esp: str, corte: str, h: float | None = None) -> pd.Series:
        m = (self.est["especificacao"] == esp) & (self.est["corte"] == corte)
        if h is not None:
            m &= np.isclose(self.est["h"].astype(float), h)
        g = self.est[m]
        self.assertEqual(len(g), 1, f"{esp} {corte}")
        return g.iloc[0]

    def test_dird_principal_recupera_salto_do_pos(self) -> None:
        for corte in ("0.300", "0.400", E7.EMPILHADO):
            r = self._linha("principal", corte)
            self.assertEqual(r["status"], "EXECUTADO")
            self.assertAlmostEqual(r["tau"], SALTO_POS_SINTETICO, delta=0.25, msg=corte)
            self.assertLess(r["ic95_inf"], SALTO_POS_SINTETICO)
            self.assertGreater(r["ic95_sup"], SALTO_POS_SINTETICO)

    def test_nivel_mostra_pacote(self) -> None:
        for corte in ("0.300", "0.400", E7.EMPILHADO):
            # Em nível o efeito fixo a_i não se cancela: tolerância de 4 erros-padrão em torno do valor verdadeiro.
            for esp, alvo in (("nivel_pre", SALTO_FIXO_SINTETICO), ("nivel_pre_extra", SALTO_FIXO_SINTETICO),
                              ("nivel_pos", SALTO_FIXO_SINTETICO + SALTO_POS_SINTETICO)):
                r = self._linha(esp, corte)
                self.assertLess(abs(r["tau"] - alvo), 4 * r["ep"], f"{esp} {corte}")
            self.assertIn("pacote", self._linha("nivel_pos", corte)["contraste"])

    def test_placebo_e_s5_em_zero(self) -> None:
        for corte in ("0.300", "0.400", E7.EMPILHADO):
            self.assertAlmostEqual(self._linha("placebo_pre", corte)["tau"], 0.0, delta=0.25)
            self.assertAlmostEqual(self._linha("S5_pre_menos_pre_extra", corte)["tau"], 0.0, delta=0.25)
            self.assertAlmostEqual(self._linha("S5_dird_pre_extra", corte)["tau"], SALTO_POS_SINTETICO, delta=0.25)

    def test_covariavel_sensibilidade_e_donut(self) -> None:
        for corte in ("0.300", "0.400", E7.EMPILHADO):
            for h in (0.030, 0.080):
                self.assertAlmostEqual(self._linha("sensibilidade_h", corte, h)["tau"], SALTO_POS_SINTETICO, delta=0.4)
            self.assertAlmostEqual(self._linha("pos_com_pre_covariavel", corte)["tau"], SALTO_POS_SINTETICO,
                                   delta=0.3)
            self.assertAlmostEqual(self._linha("S2_donut", corte)["tau"], SALTO_POS_SINTETICO, delta=0.3)

    def test_honesto_tres_fatores_e_h_otimo_rotulado(self) -> None:
        for corte in ("0.300", "0.400", E7.EMPILHADO):
            hon = self.est[(self.est["especificacao"] == "ic_honesto") & (self.est["corte"] == corte)]
            self.assertEqual(sorted(hon["fator_M"].astype(float)), list(E7.FATORES_M))
            self.assertTrue(hon["no_protocolo"].all())
        ot = self.est[self.est["especificacao"] == "ic_honesto_h_otimo"]
        self.assertTrue(len(ot) > 0)
        self.assertFalse(ot["no_protocolo"].any())
        self.assertTrue(ot["rotulo"].str.contains("ESPECIFICACAO_ADICIONAL").all())
        p = self._linha("principal", E7.EMPILHADO)
        self.assertEqual(float(p["fator_M"]), 1.0)

    def test_painel_identico_e_lr(self) -> None:
        for corte in ("0.300", "0.400"):
            pn = self._linha("dird_painel", corte)
            self.assertAlmostEqual(pn["tau"], self._linha("principal", corte)["tau"], places=9)
            self.assertFalse(bool(pn["no_protocolo"]))
            lr = self._linha("local_randomization", corte)
            self.assertEqual(lr["status"], "EXECUTADO")
            self.assertAlmostEqual(float(lr["w_lr"]), 0.010)

    def test_suplementares_s3_s4(self) -> None:
        for corte in ("0.300", "0.400"):
            for e in ("S3_porte_muda", "S3_porte_nao_muda", "S3_diferenca"):
                self.assertEqual(self._linha(e, corte)["status"], "EXECUTADO")
            self.assertAlmostEqual(self._linha("S3_diferenca", corte)["tau"], 0.0, delta=0.5)
        for e in ("S4_dentro", "S4_fora", "S4_diferenca"):
            self.assertEqual(len(self.est[(self.est["especificacao"] == e) & (self.est["corte"] == "0.300")]), 0)
            self.assertEqual(self._linha(e, "0.400")["status"], "EXECUTADO")

    def test_rotulos_e_bky(self) -> None:
        self.assertEqual(set(self.est["natureza_dos_dados"]), {"EMPIRICO"})
        bky = self.est[self.est["entra_bky"].astype(bool)]
        self.assertEqual(sorted(bky["corte"]), sorted(["0.300", "0.400", E7.EMPILHADO]))
        self.assertTrue((bky["especificacao"] == "principal").all())
        self.assertTrue(self.est.loc[~self.est["entra_bky"].astype(bool), "q_bky"].isna().all())
        p2 = E7.p2_de(self.est)
        self.assertAlmostEqual(p2["tau"], self._linha("principal", E7.EMPILHADO)["tau"])
        for esp in self.est["especificacao"].unique():
            self.assertIn(esp, E7.ESPECIFICACOES)

    def test_estudo_de_evento(self) -> None:
        ev = self.ev
        ref = ev[ev["referencia"].astype(bool)]
        self.assertEqual(set(ref["competencia"]), {E7.COMP_REF})
        self.assertEqual(len(ref), 3)
        for corte in ("0.300", "0.400", E7.EMPILHADO):
            e = ev[(ev["corte"] == corte) & ~ev["referencia"].astype(bool)]
            self.assertEqual(set(e["competencia"]) | {E7.COMP_REF}, set(E7.COMP_EVENTO))
            pre = e[e["janela"].isin(["pre", "pre_extra", "entre_pre_extra_e_pre", "transicao"])]
            pos = e[e["janela"] == "pos"]
            self.assertLess(pre["tau"].abs().max(), 0.4)
            self.assertAlmostEqual(pos["tau"].mean(), SALTO_POS_SINTETICO, delta=0.2)
        self.assertTrue((ev["competencia"] < E7.LIMITE_CICLO3).all())

    def test_tabelas_do_doc(self) -> None:
        resumo = {"p2_para_holm": E7.p2_de(self.est), "entradas": [], "validacoes": {}, "contagens": {},
                  "desvios": E7.DESVIOS}
        tabs = E7.gerar_tabelas_doc(self.est, self.ev, resumo)
        modelo = "\n\n".join(f"<!-- E7:{k}:inicio -->\nX\n<!-- E7:{k}:fim -->" for k in tabs)
        novo = E7.aplicar_tabelas_doc(modelo, tabs)
        self.assertEqual(E7.tabelas_no_doc(novo), tabs)
        self.assertIn("P2", tabs["p2"])

    def test_figuras_em_pasta_temporaria(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            feitas = E7.gerar_figuras({("F3.1", "U"): (SPEC_F31, self.base)}, self.ev, Path(tmp))
            self.assertEqual(len(feitas), 3)
            for f in feitas:
                self.assertTrue((Path(tmp) / f).stat().st_size > 0)


class TestE7SinteticoHorasAusentes(unittest.TestCase):
    """Dados sintéticos: horas ausentes ficam ausentes (nunca zero) e saem do outcome com nota."""

    def test_horas_ausentes_nao_viram_zero(self) -> None:
        painel, pop = painel_sintetico(n=600, horas_ausentes=5)
        serie = E7.serie_outcome(painel, SPEC_F33, pop)
        self.assertEqual(int(serie["y"].isna().sum()), 5)
        base, notas = E7.janelas(serie)
        afetados = set(pop["co_ibge"].iloc[:5])
        self.assertTrue(base.loc[base["co_ibge"].isin(afetados), "delta_principal"].isna().all())
        self.assertTrue(base.loc[~base["co_ibge"].isin(afetados), "delta_principal"].notna().all())
        # Placebo usa 202406 também; S5 (pós - pré extra) não usa: afetados continuam ali.
        self.assertTrue(base.loc[base["co_ibge"].isin(afetados), "delta_s5_dird"].notna().all())
        self.assertIn("5 unidades sem todos os periodos de pre", notas["principal"])
        self.assertEqual(notas["municipios_y_ausente_em_algum_mes_do_evento"], 5)

    def test_sensibilidades_do_paragrafo_16(self) -> None:
        painel, pop = painel_sintetico(n=600, horas_ausentes=5)
        afetados = set(pop["co_ibge"].iloc[:5])
        # Sem filtro: mesma regra de ausência do principal.
        base_sf, _ = E7.janelas(E7.serie_outcome(painel, SPEC_F33_SEM_FILTRO, pop))
        self.assertTrue(base_sf.loc[base_sf["co_ibge"].isin(afetados), "delta_principal"].isna().all())
        # Soma parcial: nunca ausente; os afetados ficam na amostra.
        serie = E7.serie_outcome(painel, SPEC_F33_PARCIAL, pop)
        self.assertFalse(serie["y"].isna().any())
        br = E7.contar_horas_em_branco(painel, "alvo_pmme", pop["co_ibge"])
        self.assertEqual(br, {"celulas_municipio_mes": 5, "vinculos_em_branco_soma_nos_meses": 5, "municipios": 5})
        linhas, _, base = E7.estimar_outcome(SPEC_F33_PARCIAL, "U", serie, sup={}, lr={}, nota_extra="X_BRANCO")
        self.assertTrue(base.loc[base["co_ibge"].isin(afetados), "delta_principal"].notna().all())
        est = pd.DataFrame(linhas)
        self.assertTrue(est["rotulo"].str.contains(E7.ROTULO_SENS_HORAS).all())
        self.assertFalse(est["entra_bky"].astype(bool).any())
        princ = est[est["especificacao"] == "principal"]
        self.assertTrue(princ["nota"].str.contains("soma parcial").all())
        self.assertTrue(princ["nota"].str.contains("X_BRANCO").all())
        self.assertFalse(SPEC_F33_PARCIAL["bky"] or SPEC_F33_SEM_FILTRO["bky"])
        self.assertTrue(SPEC_F33["bky"])

    def test_taxa_sem_populacao_fica_ausente(self) -> None:
        painel, pop = painel_sintetico(n=50)
        pop.loc[0, "populacao_2022"] = np.nan
        serie = E7.serie_outcome(painel, SPEC_P1, pop)
        self.assertTrue(serie.loc[serie["co_ibge"] == pop.loc[0, "co_ibge"], "y"].isna().all())
        self.assertTrue(serie.loc[serie["co_ibge"] != pop.loc[0, "co_ibge"], "y"].notna().all())


class TestE7SinteticoValidacoes(unittest.TestCase):
    """Dados sintéticos: a validação de esquema falha fechado."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.painel, cls.pop = painel_sintetico(n=40)
        cls.universo = set(cls.pop["co_ibge"])

    def test_painel_valido_passa(self) -> None:
        v = E7.validar_painel(self.painel, self.universo)
        self.assertTrue(v["balanceado"])

    def test_chave_repetida(self) -> None:
        p = pd.concat([self.painel, self.painel.iloc[:1]], ignore_index=True)
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_painel(p, self.universo)

    def test_competencia_do_ciclo3_recusada(self) -> None:
        extra = self.painel[self.painel["competencia"] == "202608"].assign(competencia="202609")
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_painel(pd.concat([self.painel, extra], ignore_index=True), self.universo)

    def test_competencia_ausente(self) -> None:
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_painel(self.painel[self.painel["competencia"] != E7.COMP_REF], self.universo)

    def test_desbalanceado(self) -> None:
        p = self.painel.drop(index=self.painel.index[5])
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_painel(p, self.universo)

    def test_natureza_nao_empirica(self) -> None:
        p = self.painel.copy()
        p.loc[0, "natureza_dos_dados"] = "OUTRA"
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_painel(p, self.universo)

    def test_horas_nulas_sem_vinculo_ausente(self) -> None:
        p = self.painel.copy()
        p[E7.COL_HORAS_SUS] = p[E7.COL_HORAS_SUS].astype("Int32")
        p.loc[0, E7.COL_HORAS_SUS] = pd.NA
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_painel(p, self.universo)

    def test_sensibilidade_de_horas_ausente_ou_incoerente(self) -> None:
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_painel(self.painel.drop(columns=[E7.COL_HORAS_PARCIAL]), self.universo)
        p = self.painel.copy()
        p.loc[p["n_vinculos"] > 0, E7.COL_HORAS_PARCIAL] = p.loc[p["n_vinculos"] > 0, E7.COL_HORAS_PARCIAL] + 1
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_painel(p, self.universo)
        p = self.painel.copy()
        p[E7.COL_HORAS_PARCIAL] = p[E7.COL_HORAS_PARCIAL].astype("Int32")
        p.loc[0, E7.COL_HORAS_PARCIAL] = pd.NA
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_painel(p, self.universo)

    def test_manifesto(self) -> None:
        defs_ok = {E7.COL_HORAS_SUS: "soma das horas dos vinculos com TP_SUS_NAO_SUS == 'S'"}
        base = {"painel": {"sha256": "a"}, "natureza_dos_dados": "EMPIRICO", "definicoes": defs_ok}
        self.assertTrue(E7.validar_manifesto(base, "a")["sha256_painel_igual_manifesto"])
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_manifesto(base, "b")
        # Definição antiga (sem o filtro do §16) é recusada.
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_manifesto({**base, "definicoes": {E7.COL_HORAS_SUS: "ambulatorial + hospitalar SUS"}}, "a")
        with self.assertRaises(E7.FalhaValidacao):
            E7.validar_manifesto({**base, "competencias_nao_obtidas": ["202501"]}, "a")

    def test_s3_portes_conferidos(self) -> None:
        # Tabela sintética que segue a regra do Anexo VI (estrato por código de IVS x porte).
        regra = {(1, 1): 1, (2, 1): 2, (3, 1): 3, (4, 1): 3, (5, 1): 4, (1, 2): 1, (2, 2): 2, (3, 2): 3, (4, 2): 4,
                 (5, 2): 4, (1, 3): 2, (2, 3): 3, (3, 3): 3, (4, 3): 4, (5, 3): 4, (1, 4): 3, (2, 4): 3, (3, 4): 4,
                 (4, 4): 4, (5, 4): 4}
        a10 = pd.DataFrame([{"co_ibge": f"8{i:05d}", "ivs_codigo_portaria": c, "porte_codigo": p, "estrato_ied": e}
                            for i, ((c, p), e) in enumerate(regra.items())])
        s3 = E7.s3_de_tabela(a10)
        self.assertEqual(s3["portes_muda"], E7.PORTES_MUDA_PROTOCOLO)
        a10.loc[a10["porte_codigo"] == 1, "estrato_ied"] = 4
        with self.assertRaises(E7.FalhaValidacao):
            E7.s3_de_tabela(a10)

    def test_s4_valor_fora_do_dicionario(self) -> None:
        df = pd.DataFrame({"co_ibge": ["100001", "100002"], "amazonia_legal": ["Amazonia Legal", "X"],
                           "faixa_fronteira": ["Fora da Faixa de Fronteira", "Faixa de Fronteira"]})
        with self.assertRaises(E7.FalhaValidacao):
            E7.s4_de_tabela(df)

    def test_janelas_do_protocolo(self) -> None:
        self.assertEqual(len(E7.COMP_PRE), 13)
        self.assertEqual((E7.COMP_PRE[0], E7.COMP_PRE[-1]), ("202406", "202506"))
        self.assertEqual((E7.COMP_POS[0], E7.COMP_POS[-1]), ("202510", "202608"))
        self.assertEqual(E7.COMP_PLACEBO_A + E7.COMP_PLACEBO_B, E7.COMP_PRE[:-1])
        self.assertTrue(all(c < E7.LIMITE_CICLO3 for c in E7.COMP_EVENTO))
        self.assertEqual(len(set(E7.COMP_EVENTO)), len(E7.COMP_EVENTO))


class TestE7SinteticoSequencia(unittest.TestCase):
    """Dados sintéticos: a maior sequência de meses com p < 0,05 é achada na ordem do estudo de evento."""

    def test_maior_sequencia(self) -> None:
        comps = ["202508", "202509", "202510", "202511", "202512", "202601", "202602"]
        ps = [0.01, 0.2, 0.01, 0.02, 0.03, 0.5, 0.01]
        e = pd.DataFrame({"competencia": comps, "janela": "pos", "referencia": False, "p_valor": ps})
        self.assertEqual(E7.maior_sequencia_significativa(e), ["202510", "202511", "202512"])
        e["p_valor"] = 0.5
        self.assertEqual(E7.maior_sequencia_significativa(e), [])


class TestE7CodigoSemArquivoProibido(unittest.TestCase):
    def test_arquivo_local_errado_nao_e_lido(self) -> None:
        texto = SCRIPT.read_text(encoding="utf-8")
        # Nem lido nem citado pelo nome (a guarda de test_fonte_ivs_oficial conta ocorrências por script).
        self.assertNotIn("ipea_2010_municipios", texto.lower())
        self.assertIn("a08_ivs_2010_oficial_municipio.csv", texto)


# --------------------------------------------------------------------------
# Saídas reais
# --------------------------------------------------------------------------

@unittest.skipUnless(EST.exists() and EVENTO.exists() and RESUMO.exists(), "saidas do E7 ainda nao geradas")
class TestE7SaidasReais(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.est = pd.read_csv(EST, dtype={"corte": str})
        cls.ev = pd.read_csv(EVENTO, dtype={"corte": str, "competencia": str})
        cls.resumo = json.loads(RESUMO.read_text(encoding="utf-8"))

    def test_rotulos_e_colunas(self) -> None:
        self.assertEqual(list(self.est.columns), E7.COLUNAS_SAIDA)
        self.assertEqual(list(self.ev.columns), E7.COLUNAS_EVENTO)
        self.assertEqual(set(self.est["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(set(self.ev["natureza_dos_dados"]), {"EMPIRICO"})
        self.assertEqual(self.resumo["natureza_dos_dados"], "EMPIRICO")

    def test_entradas_com_hash_atual(self) -> None:
        for b in self.resumo["entradas"]:
            self.assertEqual(sha256(ROOT / b["caminho"]), b["sha256"], b["caminho"])
        man = json.loads(E7.MANIFESTO_A09.read_text(encoding="utf-8"))
        painel = next(b for b in self.resumo["entradas"] if b["caminho"].endswith("painel_municipio_cbo_mes.parquet"))
        self.assertEqual(painel["sha256"], man["painel"]["sha256"])

    def test_p2_bate_com_csv(self) -> None:
        p2 = self.resumo["p2_para_holm"]
        r = self.est[(self.est["outcome_id"] == "F3.1") & (self.est["populacao"] == "U")
                     & (self.est["corte"] == E7.EMPILHADO) & (self.est["especificacao"] == "principal")]
        self.assertEqual(len(r), 1)
        self.assertAlmostEqual(p2["p_valor"], float(r["p_valor"].iloc[0]), places=12)
        self.assertAlmostEqual(p2["tau"], float(r["tau"].iloc[0]), places=12)

    def test_bky_recalculado(self) -> None:
        m = self.est["entra_bky"].astype(bool)
        q = E7.L.qvalores_bky(self.est.loc[m, "p_valor"].to_numpy(dtype=float))
        np.testing.assert_allclose(self.est.loc[m, "q_bky"].to_numpy(dtype=float), q)
        self.assertTrue(self.est.loc[~m, "q_bky"].isna().all())
        self.assertFalse(self.est.loc[m, "outcome_id"].eq("S6").any())
        self.assertTrue((self.est.loc[m, "especificacao"] == "principal").all())

    def test_todas_as_especificacoes_por_outcome(self) -> None:
        for spec in E7.CATALOGO:
            for pop in spec["pops"]:
                sub = self.est[(self.est["outcome_id"] == spec["id"]) & (self.est["populacao"] == pop)]
                for corte in ("0.300", "0.400", E7.EMPILHADO):
                    s = sub[sub["corte"] == corte]
                    for esp in ("principal", "sensibilidade_h", "ic_honesto", "pos_com_pre_covariavel",
                                "placebo_pre", "nivel_pre", "nivel_pos", "nivel_pre_extra", "S5_pre_menos_pre_extra",
                                "S5_dird_pre_extra", "S2_donut"):
                        self.assertTrue((s["especificacao"] == esp).any(), f"{spec['id']} {pop} {corte} {esp}")

    def test_estudo_de_evento_sem_ciclo3(self) -> None:
        self.assertTrue((self.ev["competencia"] < E7.LIMITE_CICLO3).all())
        self.assertEqual(set(self.ev["competencia"]), set(E7.COMP_EVENTO))
        ref = self.ev[self.ev["referencia"].astype(bool)]
        self.assertEqual(set(ref["competencia"]), {E7.COMP_REF})
        self.assertTrue(ref["tau"].isna().all())

    def test_resumo_sem_nome_do_arquivo_errado(self) -> None:
        self.assertNotIn("ipea_2010_municipios", RESUMO.read_text(encoding="utf-8").lower())

    def test_sequencia_do_evento_recalculada(self) -> None:
        """Recalcula, com código independente, a sequência de p < 0,05 de F3.1 (U, 0,300) citada no doc."""
        e = self.ev[(self.ev["outcome_id"] == "F3.1") & (self.ev["populacao"] == "U") & (self.ev["corte"] == "0.300")
                    & self.ev["janela"].isin(["transicao", "pos"])].sort_values("competencia")
        sig = (e["p_valor"].astype(float) < 0.05).to_numpy()
        melhor, ini = (0, 0), None
        for i, s in enumerate(list(sig) + [False]):
            if s and ini is None:
                ini = i
            if not s and ini is not None:
                if i - ini > melhor[1] - melhor[0]:
                    melhor = (ini, i)
                ini = None
        seq = e["competencia"].iloc[melhor[0]:melhor[1]].tolist()
        self.assertEqual(seq, E7.maior_sequencia_significativa(
            self.ev[(self.ev["outcome_id"] == "F3.1") & (self.ev["populacao"] == "U") & (self.ev["corte"] == "0.300")]))
        if seq:
            texto = DOC.read_text(encoding="utf-8")
            self.assertIn(f"de {seq[0][:4]}-{seq[0][4:]} a {seq[-1][:4]}-{seq[-1][4:]} têm", texto)

    def test_figuras_existem(self) -> None:
        for f in self.resumo["figuras"]:
            self.assertTrue((ROOT / f).exists(), f)

    @unittest.skipUnless(DOC.exists(), "doc 43 ausente")
    def test_doc_bate_com_as_saidas(self) -> None:
        texto = DOC.read_text(encoding="utf-8")
        no_doc = E7.tabelas_no_doc(texto)
        geradas = E7.gerar_tabelas_doc(self.est, self.ev, self.resumo)
        self.assertEqual(set(no_doc), set(geradas))
        for k, v in geradas.items():
            self.assertEqual(no_doc[k], v, f"tabela {k} do doc 43 difere das saidas")

    @unittest.skipUnless(DOC.exists(), "doc 43 ausente")
    def test_doc_sem_numero_digitado_fora_das_tabelas(self) -> None:
        """Fora dos blocos gerados, o doc só tem parâmetros do protocolo (cortes, h, fatores, R$, datas, seções)."""
        texto = E7.MARCA.sub("", DOC.read_text(encoding="utf-8"))
        permitidos = {"0,300", "0,400", "0,050", "0,030", "0,080", "0,5", "0,3", "0,4", "0,2", "0,5M",
                      "0,05"}   # parâmetros do protocolo e o nível de significância convencional
        decimais = set(re.findall(r"(?<![\w/.-])\d+,\d+(?![\w/])", texto))
        self.assertEqual(decimais - permitidos, set(), "numero decimal fora das tabelas geradas")


if __name__ == "__main__":
    unittest.main()
