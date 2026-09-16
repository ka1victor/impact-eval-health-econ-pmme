# -*- coding: utf-8 -*-
"""Guardas do deck .pptx da banca 1.

O deck é artefato derivado, montado por
`scripts/apresentacao/montar_deck_banca1_pptx.py` sobre o template do autor.
Estes testes travam o que já deu errado uma vez: gabarito não preenchido,
gráfico com dado embutido no próprio arquivo, e manifesto fora de sincronia.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DECK = RAIZ / "output" / "apresentacao_banca1" / "deck_banca1_modelo_economico.pptx"
MANIFESTO = RAIZ / "output" / "apresentacao_banca1" / "manifesto_deck_banca1.json"

pytestmark = pytest.mark.skipif(
    not DECK.exists(), reason="deck ainda não montado nesta árvore"
)


@pytest.fixture(scope="module")
def pacote():
    with zipfile.ZipFile(DECK) as zf:
        yield {
            nome: zf.read(nome).decode("utf8")
            for nome in zf.namelist()
            if nome.startswith("ppt/slides/slide") and nome.endswith(".xml")
        }


@pytest.fixture(scope="module")
def manifesto():
    return json.loads(MANIFESTO.read_text(encoding="utf8"))


def test_o_deck_tem_os_21_slides_do_roteiro(pacote, manifesto):
    assert len(pacote) == 21
    assert manifesto["saida"]["slides"] == 21
    assert len(manifesto["roteiro"]) == 21


def test_o_manifesto_registra_o_hash_do_deck_gravado(manifesto):
    atual = hashlib.sha256(DECK.read_bytes()).hexdigest()
    assert manifesto["saida"]["sha256"] == atual, (
        "manifesto e deck divergem: remonte com "
        "scripts/apresentacao/montar_deck_banca1_pptx.py"
    )


def test_nenhum_grafico_tem_dado_embutido_no_arquivo(pacote):
    """Nenhum slide referencia objeto de gráfico do PowerPoint.

    Os gráficos nativos do template carregavam a série dentro do .pptx; a de
    especialistas por UF chegava a contradizer a fonte registrada na
    proveniência. Todo gráfico do deck é figura gerada por script versionado.
    """
    com_grafico = sorted(nome for nome, xml in pacote.items() if "c:chart" in xml)
    assert com_grafico == []


def test_nenhum_marcador_do_gabarito_sobrou(pacote):
    """Os gabaritos de modelo vinham preenchidos com `X`."""
    sobras = []
    for nome, xml in sorted(pacote.items()):
        for marcador in ("<a:t>X</a:t>", "<a:t>X.</a:t>", "<m:t>𝑋</m:t>"):
            if marcador in xml:
                sobras.append((nome, marcador))
    assert sobras == []


def test_o_enunciado_da_hipotese_esta_no_deck(pacote):
    junto = "".join(pacote.values())
    assert "Ceteris paribus" in junto
    assert "conseguem atrair mais " in junto


def test_a_leitura_da_serie_de_oferta_e_declarada_descritiva(pacote):
    """Sem município fora do programa, a figura não identifica efeito."""
    junto = "".join(pacote.values())
    assert "Leitura descritiva" in junto


def test_os_erros_de_digitacao_do_sumario_foram_corrigidos(pacote):
    junto = "".join(pacote.values())
    assert "porposto" not in junto
    assert "Téorica" not in junto
