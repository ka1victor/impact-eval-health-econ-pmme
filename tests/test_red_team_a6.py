"""Invariantes A6 — red team e síntese (associativo, RDD encerrado)."""

from __future__ import annotations

import json
import hashlib
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DOCS_REDTEAM = ROOT / "docs" / "auditorias" / "09_red_team_atracao_provimento.md"
DOCS_MATRIZ_CSV = ROOT / "docs" / "auditorias" / "09_matriz_afirmacao_evidencia_limite.csv"
OUT_MATRIZ_CSV = ROOT / "output" / "tema_trabalho" / "A6_matriz_afirmacao_evidencia_limite.csv"
DOCS_SINTESE = ROOT / "docs" / "06_execucao" / "32_sintese_A6_resumo_intro_metodos_conclusao.md"
MANIFESTO = ROOT / "output" / "tema_trabalho" / "A6_manifesto_reproducao.json"
MATRIZ_MD = ROOT / "docs" / "auditorias" / "09_matriz_afirmacao_evidencia_limite.md"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()


class RedTeamA6Test(unittest.TestCase):
    def test_entregaveis_existem(self):
        for p in [DOCS_REDTEAM, DOCS_MATRIZ_CSV, OUT_MATRIZ_CSV, DOCS_SINTESE, MANIFESTO, MATRIZ_MD]:
            self.assertTrue(p.exists(), f"missing {p}")
            self.assertGreater(p.stat().st_size, 200, f"empty {p}")

    def test_checklist_9_itens(self):
        txt = DOCS_REDTEAM.read_text(encoding="utf-8").lower()
        for kw in [
            "denominador",
            "população territorial",
            "municípios",
            "inferência municipal",
            "confirmação",
            "homologação",
            "ivs",
            "faixa",
            "cnes",
            "retenção individual",
            "rdd",
            "r1",
            "sih",
        ]:
            self.assertIn(kw.lower(), txt, f"checklist missing {kw}")
        man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        self.assertEqual(len(man["checklist_A6_passou"]), 9)
        # case-insensitive check for rdd
        checklist_low = [x.lower() for x in man["checklist_A6_passou"]]
        for item in ["denominador_versionamento","populacao_territorial_previa","inferencia_municipal_concentracao","rdd_encerrado_r1","sem_sih_sia_fila"]:
            self.assertIn(item.lower(), checklist_low)

    def test_matriz_afirmacao_evidencia_limite(self):
        df = pd.read_csv(OUT_MATRIZ_CSV)
        self.assertEqual(len(df), 11)
        for col in ["afirmacao","evidencia","limite","linguagem_maxima"]:
            self.assertIn(col, df.columns)
            self.assertFalse(df[col].isna().any(), f"NA in {col}")
        # must contain associativa language and not causal claim
        txt = " ".join(df["linguagem_maxima"].tolist()).lower()
        self.assertIn("associado", txt)
        # docs copy must match out
        df2 = pd.read_csv(DOCS_MATRIZ_CSV)
        pd.testing.assert_frame_equal(df, df2)

    def test_sintese_coerente_nivel_associativo(self):
        txt = DOCS_SINTESE.read_text(encoding="utf-8")
        low = txt.lower()
        for sec in ["resumo","introdução","métodos","conclusão"]:
            # accept without accent
            self.assertTrue(sec in low or sec.replace("ç","c") in low or sec.replace("ã","a") in low, f"missing section {sec}")
        self.assertIn("associativo", low)
        self.assertIn("atração", low)
        # must not claim positive causal effect; allow negated "sem base para efeito causal"
        self.assertNotIn("efeito causal do adicional da bolsa foi estimado", low)
        self.assertNotIn("efeito causal do adicional da bolsa é", low)
        self.assertIn("sem base para efeito causal", low)
        # must mention rdd encerrado
        self.assertTrue("rdd" in low and "r1" in low)
        # hashes mentioned
        self.assertIn("hash", low)

    def test_manifesto_reproducao_completo(self):
        man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
        self.assertIn("comandos_reproducao", man)
        cmds = " ".join(man["comandos_reproducao"])
        for cmd in ["02_reconciliar_funil", "03_construir_tipologia", "04_congelar_pre_analise", "05_estimar_atracao", "06_avaliar_provimento", "07_red_team"]:
            self.assertIn(cmd, cmds)
        self.assertIn("hashes_entradas_e_artefatos", man)
        # check hashes conferem for at least quadro
        for rel, meta in man["hashes_entradas_e_artefatos"].items():
            p = ROOT / rel
            if p.exists():
                self.assertEqual(sha(p), meta["sha256"], f"hash diverge {rel}")
        self.assertIn("versoes", man)
        self.assertIn("python", man["versoes"])
        self.assertIn("limites_reafirmados", man)
        self.assertIn("portoes", man)
        self.assertIn("R1_RDD_ENCERRADO", " ".join(man["portoes"].keys()))

    def test_red_team_tenta_refutar(self):
        txt = DOCS_REDTEAM.read_text(encoding="utf-8")
        # must contain attempts to refute
        self.assertIn("Refutação tentada", txt)
        self.assertIn("Veredito", txt)
        # must mention winsor and loo as attempts (case-insensitive)
        low = txt.lower()
        self.assertIn("winsorizar", low)
        self.assertTrue("leave-one" in low or "loo" in low)
        # must not declare causal
        self.assertIn("não há base para reivindicar efeito causal", low)

    def test_sem_sih_sia_fila(self):
        for p in [DOCS_REDTEAM, DOCS_SINTESE, OUT_MATRIZ_CSV]:
            txt = p.read_text(encoding="utf-8", errors="ignore").lower()
            # must not claim estimated cost-benefit without gate
            self.assertNotIn("custo-benefício logístico estimado", txt)
            # if sih appears, must be in blocked/negative context
            if "sih" in txt:
                self.assertTrue("sem sih" in txt or "nenhuma" in txt or "não" in txt or "fora do núcleo" in txt or "sem portão" in txt)


if __name__ == "__main__":
    unittest.main()
