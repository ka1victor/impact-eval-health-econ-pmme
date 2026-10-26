"""Manifesto das normas sobre incentivos ligados à vulnerabilidade (auditoria 35).

Relatório: `docs/auditorias/35_incentivos_ligados_a_vulnerabilidade.md`.
Complementa `a10_normas_mesmos_cortes_ivs.py` (auditoria 18), sem refazê-lo.

O que faz:

1. Para cada fonte capturada na pesquisa documental de 26/10/2026 (cópias em
   `output/aquisicao/normas_incentivos/`), registra URL, data de acesso, ato,
   data de publicação declarada, natureza da fonte, tamanho e SHA-256.
   Com `--baixar`, baixa as cópias que faltarem (nunca sobrescreve).
2. Para as normas já arquivadas em `data/raw/aquisicao/` (adquiridas por a03 e
   a10), só lê: calcula o SHA-256 e confere os trechos citados. Nada é escrito
   em `data/`.
3. Confere, no texto extraído de cada fonte, as âncoras (expressões regulares)
   dos trechos citados na auditoria 35. Âncora ausente: o script para
   (fail closed). Fontes sem texto extraível (PDF digitalizado, texto em
   curvas) ficam marcadas `conferencia = "visual"`, com a página lida.
4. Grava `output/aquisicao/normas_incentivos/a18_manifesto_normas_incentivos.json`.

Não lê nenhum outcome. Não há cálculo por lado de corte.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import html as html_lib
import json
import re
import shutil
import subprocess
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "output" / "aquisicao" / "normas_incentivos"
RAW = ROOT / "data" / "raw" / "aquisicao"
MANIFESTO = OUT_DIR / "a18_manifesto_normas_incentivos.json"
DATA_ACESSO = "2026-10-26"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"

# --------------------------------------------------------------------------
# Fontes novas, copiadas para output/ (capturadas em 26/10/2026)
# --------------------------------------------------------------------------
FONTES_NOVAS = [
    {
        "arquivo": "lei_10260_2001_compilada_planalto.html",
        "url": "https://www.planalto.gov.br/ccivil_03/leis/leis_2001/l10260compilado.htm",
        "ato": "Lei 10.260/2001 (Fies), texto compilado",
        "publicacao": "DOU 13/07/2001; compilação Planalto consultada em 26/10/2026",
        "natureza": "ato oficial (texto compilado do Planalto)",
        "ancoras": [
            r"m[ée]dico integrante de equipe de sa[úu]de da fam[íi]lia oficialmente cadastrada",
            r"definidas como priorit[áa]rias pelo Minist[ée]rio da Sa[úu]de",
            r"contratados at[ée] o segundo semestre de 2017",
            r"at[ée] 50% \(cinquenta por cento\) do valor mensal devido",
            r"contratados a partir do primeiro semestre de 2018",
            r"especialidades priorit[áa]rias definidas em ato do Ministro",
        ],
    },
    {
        "arquivo": "fiesmed_faq_ms.html",
        "url": "https://www.gov.br/saude/pt-br/composicao/sgtes/mais-medicos/medico-e-medica/fiesmed/faq",
        "ato": "FAQ do FIESMED (Ministério da Saúde)",
        "publicacao": "página publicada em 19/11/2025, atualizada em 08/09/2026",
        "natureza": "página oficial do Ministério da Saúde",
        "ancoras": [
            r"Atualizado em 08/09/2026",
            r"Portaria Conjunta SGTES/SAS n[ºo] 3, de 19 de fevereiro de 2013",
            r"equipes da Estrat[ée]gia de Sa[úu]de da Fam[íi]lia \(eSF\)",
            r"20% mais pobres do munic[íi]pio",
            r"Atua[çc][ãa]o nos munic[íi]pios definidos como priorit[áa]rios pelo Minist[ée]rio da Sa[úu]de",
        ],
    },
    {
        "arquivo": "fiesmed_pagina_ms.html",
        "url": "https://www.gov.br/saude/pt-br/composicao/sgtes/mais-medicos/medico-e-medica/fiesmed",
        "ato": "Página do FIESMED (Ministério da Saúde)",
        "publicacao": "sem data na página",
        "natureza": "página oficial do Ministério da Saúde",
        "ancoras": [r"FIESMED"],
    },
    {
        "arquivo": "conass_ci30_2013_portaria_conjunta_3.html",
        "url": "https://www.conass.org.br/ci-n30-publicada-portaria-conj-n3-que-estabelece-criterios-para-definicao-das-areas-e-regioes-prioritarias-com-carencia-e-dificuldade-de-retencao-de-medico-integrante-de-equipe-de-saude-da-familia/",
        "ato": "Portaria Conjunta SGTES/SAS 3/2013 (reprodução do texto pelo CONASS, CI n. 30/2013)",
        "publicacao": "DOU 20/02/2013 (segundo o CONASS)",
        "natureza": "reprodução secundária; o texto na BVS-MS respondeu HTTP 503 em 26/10/2026",
        "ancoras": [
            r"percentual da popula[çc][ãa]o em extrema pobreza",
            r"percentual da popula[çc][ãa]o residente na [áa]rea rural",
            r"20% \(vinte por cento\) mais pobres do Munic[íi]pio",
        ],
    },
    {
        "arquivo": "lei_12871_2013_compilada_planalto.html",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2013/lei/l12871.htm",
        "ato": "Lei 12.871/2013 (Mais Médicos), texto compilado",
        "publicacao": "DOU 23/10/2013; compilação Planalto consultada em 26/10/2026",
        "natureza": "ato oficial (texto compilado do Planalto)",
        "ancoras": [
            r"receber[áa] pontua[çc][ãa]o adicional de 10% \(dez por cento\) na nota de todas as fases",
            r"\(Revogado pela Lei n[ºo] 15\.233, de 2025\)",
            r"poder[ãa]o fazer jus a bolsa-forma[çc][ãa]o e demais benef[íi]cios do Projeto Mais M[ée]dicos para o Brasil",
            r"classifica[çc][ãa]o socioecon[ôo]mica de alta vulnerabilidade far[ãa]o jus a adicional",
            r"Art\. 22-E\. O profissional que tiver conclu[íi]do a Resid[êe]ncia em Medicina de Fam[íi]lia e Comunidade",
            r"Art\. 19-B\. O m[ée]dico participante do Projeto Mais M[ée]dicos para o Brasil que tiver realizado gradua[çc][ãa]o em Medicina financiada",
        ],
    },
    {
        "arquivo": "portaria_mec_446_2026_abmes.pdf",
        "url": "https://abmes.org.br/arquivos/legislacoes/Portaria-mec-446-2026-05-19.pdf",
        "ato": "Portaria MEC 446, de 19/05/2026 (bonificação em seleções de residência médica)",
        "publicacao": "DOU 20/05/2026, Seção 1, p. 27 (recorte do DOU arquivado pela ABMES)",
        "natureza": "recorte do DOU (PDF da ABMES)",
        "ancoras": [
            r"Publicado em: 20/05/2026",
            r"Far[áa] jus [àa] pontua[çc][ãa]o adicional ou bonifica[çc][ãa]o de 10% \(dez por cento\) o candidato que houver conclu[íi]do Programa de Resid[êe]ncia M[ée]dica em Medicina de Fam[íi]lia e Comunidade",
            r"I - participa[çc][ãa]o em programas de provimento",
            r"Esta Portaria se aplica aos processos seletivos cujos editais sejam publicados ap[óo]s",
        ],
    },
    {
        "arquivo": "lei_13958_2019_compilada_planalto.html",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2019/lei/l13958.htm",
        "ato": "Lei 13.958/2019 (Médicos pelo Brasil / AgSUS), texto compilado",
        "publicacao": "DOU 19/12/2019; compilação Planalto consultada em 26/10/2026",
        "natureza": "ato oficial (texto compilado do Planalto)",
        "ancoras": [
            r"acrescida de incentivo financeiro diferenciado e vari[áa]vel",
            r"benef[íi]cio previdenci[áa]rio no valor m[áa]ximo de 2 \(dois\) sal[áa]rios m[íi]nimos",
            r"Munic[íi]pios de pequeno tamanho populacional, baixa densidade demogr[áa]fica",
        ],
    },
    {
        "arquivo": "agsus_resolucao_cda_21_2025_pcs.pdf",
        "url": "https://agenciasus.org.br/wp-content/uploads/2025/05/Resolucao-no-21-de-5-de-maio-de-2025-Aprova-o-Plano-de-Cargos-e-Salarios-dos-medicos-do-programa-de-provimento-da-Agencia-Brasileira-de-Apoio-a-Gestao-do-SUS-AgSUS.pdf",
        "ato": "Resolução CDA/AgSUS 21/2025 (Plano de Cargos e Salários dos médicos do provimento)",
        "publicacao": "assinada em 06/05/2025",
        "natureza": "ato oficial da AgSUS (serviço social autônomo)",
        "ancoras": [
            r"munic[íi]pios classificados como de alta ou muito alta vulnerabilidade pelo IPEA",
            r"vantagem pecuni[áa]ria paga ao Tutor M[ée]dico e ao M[ée]dico de Fam[íi]lia e Comunidade",
            r"Os incentivos por localidade n[ãa]o ser[ãa]o cumulativos",
        ],
    },
    {
        "arquivo": "agsus_resolucao_direx_37_2025.pdf",
        "url": "https://agenciasus.org.br/wp-content/uploads/2025/05/SEI_0018065_Resolucao_DIREX_37.pdf",
        "ato": "Resolução DIREX/AgSUS 37/2025 (valores do PCS, incentivo por localidade)",
        "publicacao": "assinada em 29/05/2025; efeitos retroativos a 06/05/2025",
        "natureza": "ato oficial da AgSUS",
        "ancoras": [
            r"Munic[íi]pios de alta e muito alta vulnerabilidade social \(IVS\) ser[áa] de R\$ 3\.000,00",
            r"classificados como rural remoto \(IBGE\) ser[áa] de R\$ 3\.000,00",
            r"Portaria GM/MS n[ºo] 485, de 14 de abril de 2023",
            r"efeitos retroativos a 6 de maio de 2025",
            r"Medicina de fam[íi]lia e comunidade:\s*a\) N[íi]vel I: R\$ R\$ 15\.750,00|m[ée]dico de fam[íi]lia e comunidade:\s*a\) N[íi]vel I: R\$ R\$ 15\.750,00",
        ],
    },
    {
        "arquivo": "agsus_edital_01_2025_eixo_vinculo.pdf",
        "url": "https://agenciasus.org.br/wp-content/uploads/2025/06/EDITAL-DE-ABERTURA_03_06_25_FINAL.pdf",
        "ato": "Edital de abertura AgSUS 01/2025 (Médico de Família e Comunidade, FCC)",
        "publicacao": "edital de 03/06/2025",
        "natureza": "edital oficial da AgSUS",
        "ancoras": [
            r"Remunera[çc][ãa]o Inicial: R\$ 16\.587,90",
            r"alterada somente para locais de mais alta vulnerabilidade",
        ],
    },
    {
        "arquivo": "agsus_faq_integracao_v2.pdf",
        "url": "https://agenciasus.org.br/wp-content/uploads/2024/11/FAQ_Integracao_v2.pdf",
        "ato": "FAQ AgSUS: integração dos programas de provimento (v2)",
        "publicacao": "carregado em 11/2024 (caminho do arquivo)",
        "natureza": "documento informativo da AgSUS",
        "ancoras": [r"Prioriza [áa]reas de alta e muito alta vulnerabilidade"],
    },
    {
        "arquivo": "edital_sgtes_06_2025_pro_residencia_dou.html",
        "url": "https://www.in.gov.br/en/web/dou/-/edital-sgtes/ms-n-6-de-16-setembro-de-2025-656600096",
        "ato": "Edital SGTES/MS 6/2025 (Pró-Residência, bolsas de residência médica)",
        "publicacao": "DOU 18/09/2025, Seção 3, p. 95",
        "natureza": "ato oficial (DOU)",
        "ancoras": [
            r"Publicado em: 18/09/2025",
            r"Programas de Resid[êe]ncia M[ée]dica localizados em estados da Amaz[ôo]nia Legal",
            r"raz[ãa]o de especialistas por 100 mil habitantes abaixo da m[ée]dia nacional",
            r"m[ée]dia entre o [ÍI]ndice de Vulnerabilidade Social - IVS e o [ÍI]ndice de Desenvolvimento Humano",
            r"IVS do IPEA do munic[íi]pio da institui[çc][ãa]o ofertante",
        ],
    },
    {
        "arquivo": "pmme_ciclo2_edital_03_2026.pdf",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/edital-no-3.2026",
        "ato": "Edital SGTES/MS 3/2026 (PMM-E, ciclo 2, médicos), Chamamento 1/2026",
        "publicacao": "página do chamamento publicada em 03/02/2026; PDF gerado em 03/02/2026",
        "natureza": "edital oficial (PDF do SEI, imagem sem camada de texto)",
        "conferencia": "visual",
        "paginas_lidas": "1, 9, 10, 20 e 21 (itens 1, 5.2 a 5.8 e 11.1 a 11.4)",
        "ancoras": [],
    },
    {
        "arquivo": "pmme_ciclo2_errata.pdf",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/errata",
        "ato": "Errata do Edital SGTES/MS 3/2026",
        "publicacao": "assinada em 12/02/2026",
        "natureza": "documento oficial (SEI)",
        "ancoras": [r"ativos no PMMB e PMM-E"],
    },
    {
        "arquivo": "pmme_ciclo3_gestores_edital_05_2026.pdf",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-5-2026-pmm-e/edital",
        "ato": "Edital SGTES/MS 25/2026 (adesão dos entes ao PMM-E, ciclo 3), Chamamento 5/2026",
        "publicacao": "2026 (data de assinatura no SEI não conferida)",
        "natureza": "edital oficial (PDF do SEI)",
        "ancoras": [
            r"EDITAL N[ºo] 25/2026",
            r"baixa disponibilidade regional e distribui[çc][ãa]o desigual",
            r"identificados com escassez de m[ée]dicos especialistas",
        ],
    },
    {
        "arquivo": "manual_implementacao_execucao_pmme_2025.pdf",
        "url": "https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/guias-e-manuais/2025/manual-de-implementacao-e-execucao-mais-medicos-especialistas.pdf",
        "ato": "Manual de Implementação e Execução do PMM-E (versão preliminar)",
        "publicacao": "PDF criado em 30/12/2025",
        "natureza": "publicação oficial do Ministério da Saúde",
        "conferencia": "parcial: valores da ajuda de custo lidos na imagem da p. 31 (PDF p. 33)",
        "ancoras": [
            r"hospitais integrantes da rede Ebserh, cuja unidade de aloca[çc][ãa]o esteja situada a mais de 50km",
        ],
    },
    {
        "arquivo": "lei_municipal_joao_monlevade_2581_2023.pdf",
        "url": "https://pmjm.mg.gov.br/legislacao/LEI-MUN-2581-2023-AUXILIO-PECUNIARIO-PROJETO-MAIS-MEDICOS-PARA-O-BRASIL.pdf",
        "ato": "Lei 2.581/2023 de João Monlevade (MG), auxílio-moradia e alimentação do PMMB",
        "publicacao": "21/11/2023",
        "natureza": "ato oficial municipal",
        "ancoras": [
            r"R\$ 1\.700,00 \(mil e setecentos reais\) mensais",
            r"Projeto Mais M[ée]dicos para o Brasil",
        ],
    },
]

# --------------------------------------------------------------------------
# Normas já arquivadas em data/raw (só leitura)
# --------------------------------------------------------------------------
FONTES_ARQUIVADAS = [
    {
        "arquivo": "ivs_regra/edital_sgtes_03_2025_dou.pdf",
        "ato": "Edital SGTES/MS 3/2025 (PMM-E, ciclo 1), DOU 24/07/2025",
        "ancoras": [
            r"Tabela 4 - Barema",
            r"mesma UF do seu domic[íi]lio de resid[êe]ncia ou do seu local de nascimento",
            r"categoriza[çc][ãa]o municipal do [ÍI]ndice de Vulnerabilidade Social",
        ],
    },
    {
        "arquivo": "normas_ivs/edital_sgtes_03_2025_retificacao_dou.html",
        "ato": "Retificação do Edital SGTES/MS 3/2025, DOU 28/10/2025",
        "ancoras": [
            r"aux[íi]lio nas despesas relacionadas [àa] participa[çc][ãa]o nas imers[õo]es presenciais|auxiliar nas despesas relacionadas [àa] participa[çc][ãa]o nas imers[õo]es presenciais",
            r"parcela [úu]nica para cada ciclo de imers[ãa]o",
        ],
    },
    {
        "arquivo": "ivs_regra/edital_sgtes_06_2026_edital_28_2026_ciclo3.html",
        "ato": "Edital SGTES/MS 28/2026 (PMM-E, ciclo 3, médicos); o arquivo é PDF",
        "ancoras": [
            r"acrescido um valor vari[áa]vel de R\$ 5\.000,00",
            r"muito alta ou alta vulnerabilidade social ser[ãa]o enquadrados na Faixa 1",
            r"imers[õo]es presenciais",
            r"mesma UF do munic[íi]pio de seu nascimento",
        ],
    },
    {
        "arquivo": "normas_ivs/portaria_gm_ms_7177_2025_dou.html",
        "ato": "Portaria GM/MS 7.177/2025 (institui o PMM-E)",
        "ancoras": [
            r"As bolsas concedidas poder[ãa]o ser cumuladas com outras atividades remuneradas",
            r"disponibilidade para atua[çc][ãa]o em territ[óo]rio priorit[áa]rio",
        ],
    },
    {
        "arquivo": "normas_ivs/portaria_gm_ms_7266_2025_dou.html",
        "ato": "Portaria GM/MS 7.266/2025 (Agora Tem Especialistas)",
        "ancoras": [
            r"estrat[ée]gias de provimento, aprimoramento, forma[çc][ãa]o, fixa[çc][ãa]o, incentivo e aloca[çc][ãa]o",
            r"II - [áa]reas de dif[íi]cil provimento",
        ],
    },
    {
        "arquivo": "normas_ivs/portaria_sgtes_ms_169_2025_dou.html",
        "ato": "Portaria SGTES/MS 169/2025 (indenizações dos arts. 19-A e 19-B da Lei 12.871)",
        "ancoras": [
            r"graduação em medicina financiada pelo Fundo de Financiamento Estudantil - Fies",
            r"IVS maior do que 0,638",
            r"no [âa]mbito do Projeto Mais M[ée]dicos para o Brasil",
        ],
    },
    {
        "arquivo": "normas_ivs/portaria_interm_ms_mec_07_2026_dou.html",
        "ato": "Portaria Interministerial MS/MEC 7/2026 (regulamento do PMMB)",
        "ancoras": [
            r"Faixa 2: munic[íi]pios classificados como de vulnerabilidade social alta",
            r"assegurar o pagamento do aux[íi]lio-moradia e do aux[íi]lio-alimenta[çc][ãa]o",
        ],
    },
    {
        "arquivo": "normas_ivs/portaria_gm_ms_9177_2025_dou.html",
        "ato": "Portaria GM/MS 9.177/2025 (Mais Médicos Eixos Vínculo e Estratégico)",
        "ancoras": [
            r"com incentivos adicionais para especialistas com t[íi]tulo de M[ée]dico de Fam[íi]lia e Comunidade",
            r"munic[íi]pios de alta e muito alta vulnerabilidade social",
        ],
    },
    {
        "arquivo": "normas_ivs/portaria_gm_ms_3352_2021_dou.html.gz",
        "ato": "Portaria GM/MS 3.352/2021 (metodologia do Médicos pelo Brasil)",
        "ancoras": [r"rural remoto", r"percentual da popula[çc][ãa]o vulner[áa]vel socioeconomicamente"],
    },
]


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def texto_de(caminho: Path) -> str | None:
    bruto = caminho.read_bytes()
    if bruto[:2] == b"\x1f\x8b":
        bruto = gzip.decompress(bruto)
    if bruto[:4] == b"%PDF":
        if shutil.which("pdftotext") is None:
            return None
        res = subprocess.run(
            ["pdftotext", "-", "-"], input=bruto, capture_output=True, check=True
        )
        texto = res.stdout.decode("utf-8", "replace")
    else:
        try:
            texto = bruto.decode("utf-8")
        except UnicodeDecodeError:
            texto = bruto.decode("cp1252", "replace")
        texto = re.sub(r"<script.*?</script>|<style.*?</style>", " ", texto, flags=re.S | re.I)
        texto = re.sub(r"<[^>]+>", " ", texto)
        texto = html_lib.unescape(texto)
    texto = unicodedata.normalize("NFKC", texto).replace("­", "")
    return re.sub(r"\s+", " ", texto)


def conferir(fonte: dict, caminho: Path) -> dict:
    ancoras = fonte.get("ancoras", [])
    if not ancoras:
        return {"conferencia": fonte.get("conferencia", "visual"), "ancoras": []}
    texto = texto_de(caminho)
    if texto is None:
        return {"conferencia": "nao_conferido_sem_pdftotext", "ancoras": ancoras}
    faltando = [a for a in ancoras if re.search(a, texto, flags=re.I) is None]
    if faltando:
        raise SystemExit(f"Âncora ausente em {caminho.name}: {faltando}")
    return {
        "conferencia": fonte.get("conferencia", "texto"),
        "ancoras": ancoras,
        "ancoras_encontradas": len(ancoras),
    }


def baixar(url: str, destino: Path) -> None:
    parcial = destino.with_suffix(destino.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as resp, open(parcial, "wb") as f:
        shutil.copyfileobj(resp, f)
    parcial.rename(destino)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--baixar", action="store_true", help="baixa cópias que faltarem")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    registros = []
    for fonte in FONTES_NOVAS:
        caminho = OUT_DIR / fonte["arquivo"]
        if not caminho.exists():
            if not args.baixar:
                raise SystemExit(f"Cópia ausente: {caminho} (use --baixar)")
            baixar(fonte["url"], caminho)
        reg = {k: v for k, v in fonte.items() if k != "ancoras"}
        reg.update(
            {
                "caminho": str(caminho.relative_to(ROOT)),
                "data_acesso": DATA_ACESSO,
                "bytes": caminho.stat().st_size,
                "sha256": sha256(caminho),
            }
        )
        reg.update(conferir(fonte, caminho))
        registros.append(reg)

    arquivadas = []
    for fonte in FONTES_ARQUIVADAS:
        caminho = RAW / fonte["arquivo"]
        if not caminho.exists():
            raise SystemExit(f"Norma arquivada ausente: {caminho}")
        reg = {
            "ato": fonte["ato"],
            "caminho": str(caminho.relative_to(ROOT)),
            "bytes": caminho.stat().st_size,
            "sha256": sha256(caminho),
            "origem": "adquirida por a03/a10; ver manifestos a03 e a10",
        }
        reg.update(conferir(fonte, caminho))
        arquivadas.append(reg)

    manifesto = {
        "script": "scripts/aquisicao/a18_normas_incentivos_vulnerabilidade.py",
        "relatorio": "docs/auditorias/35_incentivos_ligados_a_vulnerabilidade.md",
        "data_acesso": DATA_ACESSO,
        "outcomes_abertos": "nenhum",
        "fontes_copiadas_em_output": registros,
        "normas_ja_arquivadas_em_data_raw": arquivadas,
        "nao_preservados": [
            {
                "url": "https://bvsms.saude.gov.br/bvs/saudelegis/sgtes/2013/poc0003_19_02_2013.html",
                "motivo": "HTTP 503 em 26/10/2026; texto lido na reprodução do CONASS",
            },
            {
                "url": "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2011/prt1377_13_06_2011.html",
                "motivo": "HTTP 503 em 26/10/2026",
            },
            {
                "url": "https://www.gov.br/mec/pt-br/assuntos/noticias/2026/maio/mec-regulamenta-bonificacao-em-selecoes-de-residencia-medica",
                "motivo": "página anti-robô (captcha); a portaria foi lida no recorte do DOU",
            },
            {
                "url": "https://mecnormas.mec.gov.br/pesquisa/detalhar/11313",
                "motivo": "conteúdo carregado por JavaScript; sem texto do ato na resposta",
            },
        ],
    }
    MANIFESTO.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(registros)} fontes novas e {len(arquivadas)} normas arquivadas conferidas -> {MANIFESTO.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
