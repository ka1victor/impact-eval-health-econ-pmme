"""Normas federais que usam faixas de IVS nos cortes da bolsa do PMM-E (tarefa D).

Protocolo: `docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`, seção 4.
Relatório: `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md`.

Aquisição com cache e conferência (como a07/a08). Cada ato tem URL oficial e
dois SHA-256 esperados, registrados na captura de 18/10/2026:

- `sha256_bruto`: bytes da página como baixada (no cache, `.gz` guarda os
  mesmos bytes comprimidos; o hash é sempre do conteúdo descomprimido);
- `sha256_texto`: texto normativo extraído da página (corpo do ato no DOU,
  parágrafos no Planalto), uma linha por parágrafo.

Cache presente: o `sha256_bruto` tem de bater, senão o script para sem tocar
no arquivo. Cache ausente: o ato é baixado para `.part`; como as páginas do
DOU trazem marcas de tempo no cabeçalho, o que se confere no download é o
`sha256_texto` (texto do ato idêntico ao capturado). Só depois de conferido o
arquivo recebe o nome final. PDF não tem texto conferível: exige
`sha256_bruto`. Fontes do repositório adquiridas por outro script (a03) são
só conferidas pelo hash, nunca baixadas aqui.

Depois:

1. grava o manifesto das fontes (URL, data de captura, data de publicação no
   DOU lida da própria página, hashes) com os trechos de cláusula citados no
   relatório. Cada trecho é localizado no texto por uma expressão regular; se
   não for encontrado, o script para (fail closed). Ausências afirmadas no
   relatório (por exemplo, "o ato não cita a Portaria 485") são contadas;
2. extrai o Anexo VI da Portaria GM/MS 3.493/2024 (código de IVS, porte e
   estrato do IED por município) para `a10_ied_aps_2024_municipio.csv`;
3. confere a convenção de fronteira das classes administrativas contra o IVS
   2010 oficial (a08): Anexo VI da 3.493/2024, categoria do consolidado PMMB
   (a07) e Quadro 2 da Portaria 5.721/2024;
4. descreve o esquema do consolidado PMMB (retrato de 09/10/2026) para uso
   como outcome de co-intervenção (F0.4), sem cruzar nenhum valor com o IVS.

Só lê variáveis de atribuição (IVS, classes, estratos, porte). Nenhum outcome
do PMM-E ou do PMMB é aberto, e nada é computado por lado de corte além da
contagem de municípios exatamente sobre os limites (variável de atribuição).
"""

from __future__ import annotations

import gzip
import hashlib
import html as html_lib
import io
import json
import re
import shutil
import subprocess
import unicodedata
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "aquisicao" / "normas_ivs"
OUT = ROOT / "output" / "aquisicao"
A08 = OUT / "a08_ivs_2010_oficial_municipio.csv"
A07_CAT = OUT / "a07_categoria_ivs_pmmb_municipio.csv"
PMMB_ZIP = ROOT / "data" / "raw" / "aquisicao" / "ivs_administrativo" / "ppf_mais_medicos_csv.zip"

DATA_CAPTURA = "2026-10-18"
DOU = "https://www.in.gov.br/web/dou/-/"
IVS_REGRA = ROOT / "data" / "raw" / "aquisicao" / "ivs_regra"

# Registro das buscas feitas no DOU (https://www.in.gov.br/consulta) em
# 18/10/2026. É metadado de procedimento, não dado: diz o que foi procurado
# e em que anos, para delimitar o que "não encontrado" quer dizer.
BUSCAS_DOU = [
    {"termos": ['"Vulnerabilidade Social - IVS"', '"Índice de Vulnerabilidade Social"'],
     "anos": "2013 a 2022, um ano por consulta",
     "resultado": "atos do Ministério da Saúde encontrados: Portarias GM/MS 377/2022 e 1.054/2022 (IVS como "
                  "um dos indicadores de um índice de perfil municipal); os demais resultados são de outros órgãos"},
    {"termos": ['"Vulnerabilidade Social - IVS"', '"Índice de Vulnerabilidade Social" saúde'],
     "anos": "2023 a 18/10/2026", "resultado": "atos listados no manifesto e na auditoria 18, §2"},
    {"termos": ['"maior que 0,3"', '"vulnerabilidade social" "maior que 0,3"'],
     "anos": "2021 a 18/10/2026", "resultado": "primeira ocorrência na saúde: Portaria GM/MS 3.283/2024"},
    {"termos": ['"difícil fixação"'], "anos": "2023 a 18/10/2026", "resultado": "editais do PMMB e atos de indenização"},
    {"termos": ['"Equidade e Dimensionamento"'], "anos": "04/2024 a 18/10/2026",
     "resultado": "Portarias 3.493/2024, 4.350/2024 e 7.799/2025"},
    {"termos": ['"752, de 15 de junho de 2023"'], "anos": "07/2023 a 18/10/2026",
     "resultado": "editais 3/2024 e 2/2025 e Portaria 4.853/2024; nenhum ato de revogação"},
]

# Parâmetros do protocolo (limites de classe do IVS, em milésimos).
LIMITES_MIL = (200, 300, 400, 500)
CORTES_BOLSA_MIL = (300, 400)

# Cada fonte: arquivo preservado, URL, ato e trechos citados no relatório.
# `trechos`: rótulo -> expressão regular que deve casar uma linha do texto.
# `ausencia`: expressões que o relatório afirma NÃO aparecerem no ato.
FONTES = [
    {
        "id": "portaria_gm_ms_485_2023",
        "arquivo": "portaria_gm_ms_485_2023_dou.html",
        "url": DOU + "portaria-gm/ms-n-485-de-14-de-abril-de-2023-477636719",
        "ato": "Portaria GM/MS nº 485, de 14/04/2023 (dimensionamento e priorização de vagas de provimento)",
        "trechos": {
            "art2_I": r"^I - programas de provimento: o Programa Mais Médicos",
            "art5_caput": r"^Art\. 5º Para a priorização das vagas em municípios",
            "art5_I": r"^I - vulnerabilidade social muito alta",
            "art5_II": r"^II - vulnerabilidade social alta",
            "art5_III": r"^III - vulnerabilidade social média",
            "art5_IV": r"^IV - vulnerabilidade social baixa",
            "art3": r"^Art\. 3º Incumbe à Secretaria de Atenção Primária à Saúde realizar o dimensionamento",
            "art6_pu": r"^Parágrafo único\. Para efeitos do caput, são incluídas no formato de equipes de atenção primária",
            "art8_I": r"^I - definirá o enquadramento em áreas de vulnerabilidade",
        },
    },
    {
        "id": "portaria_gm_ms_752_2023",
        "arquivo": "portaria_gm_ms_752_2023_dou.html",
        "url": DOU + "portaria-gm/ms-n-752-de-15-de-junho-de-2023-490729168",
        "ato": "Portaria GM/MS nº 752, de 15/06/2023 (expansão de vagas do PMMB na modalidade coparticipação)",
        "trechos": {
            "ementa": r"^Dispõe sobre a expansão de novas vagas",
            "art3": r"^Art\. 3º A coparticipação no financiamento",
            "art5_caput": r"^Art\. 5º Os critérios estabelecidos para delimitação de vagas",
            "art5_I": r"^I - municípios com IVS maior ou igual a 0,4",
            "art5_II": r"^II - municípios com IVS maior ou igual a 0,3",
            "art5_III": r"^III - municípios com IVS menor do que 0,3",
            "art5_p1": r"^§ 1º Serão equiparados aos municípios do inciso I",
            "art5_p1_I": r"^I - o valor do teto de remuneração do chefe do poder executivo",
            "art5_p1_II": r"^II - os municípios do G100",
            "art5_p2": r"^§ 2º O limite de vagas não se aplica",
            "art5_p2_I": r"^I - expansão da cobertura da estratégia da saúde da família",
            "art5_p2_II": r"^II - equipes de consultório na rua e equipes de saúde prisional",
            "art7": r"^Art\. 7º Esta Portaria entra em vigor",
        },
    },
    {
        "id": "portaria_gm_ms_752_2023_ses_sp",
        "arquivo": "portaria_gm_ms_752_2023_ses_sp.pdf",
        "tipo": "pdf",
        "url": "https://ses.sp.bvs.br/wp-content/uploads/2023/06/U_PT-MS-GM-752_150623.pdf",
        "ato": "Cópia em PDF da Portaria GM/MS nº 752/2023 (DOU nº 114-A, 19/06/2023, Seção 1, Ed. Extra, p. 5), hospedada pela SES-SP",
        "trechos": {},
    },
    {
        "id": "edital_saps_11_2023",
        "arquivo": "edital_saps_11_2023_dou.html",
        "url": DOU + "edital-n-11-de-16-de-junho-de-2023-490577086",
        "ato": "Edital SAPS/MS nº 11, de 16/06/2023 (adesão de municípios a vagas do PMMB na modalidade coparticipação)",
        "trechos": {
            "item_2_2": r"^2\.2 As solicitações de novas vagas a este edital estão limitadas",
            "item_2_7": r"^2\.7 A autorização para preenchimento das vagas deste edital",
            "termo_b": r"^b\) manter, durante a execução do Projeto, o quantitativo de equipes",
            "termo_vigencia": r"^O presente Termo de Renovação e/ou Adesão e Compromisso terá vigência",
        },
    },
    {
        "id": "portaria_interm_ms_mec_604_2023",
        "arquivo": "portaria_interm_ms_mec_604_2023_dou.html",
        "url": DOU + "portaria-interministerial-ms/mec-n-604-de-16-de-maio-de-2023-483958798",
        "ato": "Portaria Interministerial MS/MEC nº 604, de 16/05/2023 (execução do PMMB)",
        "trechos": {
            "art24_caput": r"^Art\. 24\. O Ministério da Saúde concederá ajuda de custo",
            "art24_p1_I": r"^I - Faixa 1 - municípios situados na região da Amazônia Legal",
            "art24_p1_II": r"^II - Faixa 2 - municípios classificados como \"vulnerabilidade social alta\"",
            "art24_p1_III": r"^III - Faixa 3 - municípios classificados como \"vulnerabilidade social média\"",
            "art25_pu": r"^Parágrafo único\. A definição das áreas de difícil fixação",
        },
    },
    {
        "id": "portaria_interm_ms_mec_07_2026",
        "arquivo": "portaria_interm_ms_mec_07_2026_dou.html",
        "url": DOU + "portaria-interministerial-ms/mec-n-7-de-2-de-outubro-de-2026-737206420",
        "ato": "Portaria Interministerial MS/MEC nº 7, de 02/10/2026 (nova execução do PMMB; revoga a 604/2023)",
        "trechos": {
            "art7_p2": r"^§ 2º O valor da ajuda de custo corresponderá a uma, duas ou três bolsas",
            "art7_p3_I": r"^I - Faixa 1: municípios situados na região da Amazônia Legal",
            "art7_p3_II": r"^II - Faixa 2: municípios classificados como de vulnerabilidade social alta",
            "art7_p3_III": r"^III - Faixa 3: demais municípios participantes do PMMB",
            "art52": r"^Art\. 52\. Fica revogada a Portaria Interministerial MS/MEC nº 604",
        },
    },
    {
        "id": "portaria_interm_ms_mec_10032_2025",
        "arquivo": "portaria_interm_ms_mec_10032_2025_dou.html",
        "url": DOU + "portaria-interministerial-ms/mec-n-10.032-de-30-de-dezembro-de-2025-679001777",
        "ato": "Portaria Interministerial MS/MEC nº 10.032, de 30/12/2025 (altera a 604/2023)",
        "trechos": {
            "art25_pu": r"^Parágrafo único\. As áreas de difícil fixação e de vulnerabilidade",
        },
    },
    {
        "id": "lei_14621_2023",
        "arquivo": "lei_14621_2023_planalto.html",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14621.htm",
        "ato": "Lei nº 14.621, de 14/07/2023 (conversão da MP 1.165/2023; arts. 19-A e 19-B da Lei 12.871/2013)",
        "trechos": {
            "art19A_caput": r"Art\. 19-A \. O médico participante que atuar",
            "art19A_I": r"^I - 20% \(vinte por cento\) do valor total das bolsas",
            "art19A_II": r"^II - 10% \(dez por cento\) do valor total das bolsas",
        },
    },
    {
        "id": "portaria_sgtes_ms_169_2025",
        "arquivo": "portaria_sgtes_ms_169_2025_dou.html",
        "url": DOU + "portaria-sgtes/ms-n-169-de-30-de-dezembro-de-2025-678998263",
        "ato": "Portaria SGTES/MS nº 169, de 30/12/2025 (indenizações dos arts. 19-A e 19-B)",
        "trechos": {
            "art4_I": r"^I - 20% \(vinte por cento\) do valor total das bolsas",
            "art4_II": r"^II - 10% \(dez por cento\) do valor total das bolsas",
            "art6_I": r"^I - 80% \(oitenta por cento\) da quantia",
            "art6_II": r"^II - 40% \(quarenta por cento\) da quantia",
        },
    },
    {
        "id": "edital_saps_05_2023_medicos",
        "arquivo": "edital_saps_05_2023_medicos_dou.html",
        "url": DOU + "edital-n-5-de-19-de-maio-de-2023-484801096",
        "ato": "Edital SAPS/MS nº 5, de 19/05/2023 (adesão de médicos ao PMMB)",
        "trechos": {
            "item_4_2_1": r"^4\.2\.1 A relação de municípios referida no subitem 4\.2 possuirá as indicações",
            "item_4_3": r"^4\.3\. Para fins de escolha, os locais de atuação",
            "tabela1_amazonia_perfil1": r"^Amazônia Legal \(42,6% dos municípios\)",
            "tabela1_amazonia_perfil2": r"^Amazônia Legal \(21,5% dos municípios\)",
            "tabela1_amazonia_perfil3": r"^Amazônia Legal \(35% dos municípios\)",
            "item_4_3_1": r"^4\.3\.1 A numeração dos Perfis descrita na Tabela 1",
            "item_4_3_2_a": r"^a\) o médico que integrar eSF situada em município de determinado Perfil",
        },
    },
    {
        "id": "edital_saps_13_2023_medicos",
        "arquivo": "edital_saps_13_2023_medicos_dou.html",
        "url": DOU + "edital-n-13-de-11-de-julho-de-2023-496279927",
        "ato": "Edital SAPS/MS nº 13, de 11/07/2023 (adesão de médicos ao PMMB)",
        "trechos": {
            "item_4_3": r"^4\.3\. Para fins de escolha, os locais de atuação disponibilizados neste Edital estão distribuídos nos perfis",
            "item_10_9": r"^10\.9 Somente no caso do médico comprovar necessidade de mudança de domicílio",
            "item_10_10": r"^10\.10 O direito à indenização por atuação em área de difícil fixação",
        },
    },
    {
        "id": "edital_saps_04_2024_medicos",
        "arquivo": "edital_saps_04_2024_medicos_dou.html",
        "url": DOU + "edital-de-chamamento-publico-n-4/2024-569054926",
        "ato": "Edital de Chamamento Público SAPS/MS nº 4/2024 (adesão de médicos ao PMMB, 38º ciclo)",
        "trechos": {
            "item_5_7": r"^5\.7 Para fins de escolha, os locais de atuação",
        },
    },
    {
        "id": "edital_conjunto_saps_sgtes_07_2025",
        "arquivo": "edital_conjunto_saps_sgtes_07_2025_dou.html",
        "url": DOU + "edital-conjunto-saps/sgtes/ms-n-7/2025-626985263",
        "ato": "Edital Conjunto SAPS/SGTES/MS nº 7/2025 (adesão de médicos ao PMMB)",
        "trechos": {
            "item_6_7": r"^6\.7 Para fins de escolha, os locais de atuação",
            "item_6_8_a": r"^a\) o médico que integrar eSF situada em município de determinado Perfil",
        },
    },
    {
        "id": "edital_saps_03_2024_municipios",
        "arquivo": "edital_saps_03_2024_municipios_dou.html",
        "url": DOU + "edital-n-3/2024-559732562",
        "ato": "Edital SAPS/MS nº 3/2024 (adesão/renovação de municípios ao PMMB, 38º ciclo)",
        "trechos": {
            "preambulo": r"Portaria GM/MS nº 752, de 15 de junho de 2023, e considerando",
            "item_1_1": r"sejam de financiamento federal ou de coparticipação",
        },
    },
    {
        "id": "edital_saps_02_2025_municipios",
        "arquivo": "edital_saps_02_2025_municipios_dou.html",
        "url": DOU + "edital-saps/ms-n-2/2025-618393420",
        "ato": "Edital SAPS/MS nº 2/2025 (adesão/renovação de municípios ao PMMB, 41º ciclo)",
        "trechos": {
            "preambulo": r"Portaria GM/MS nº 752, de 15 de junho de 2023, e considerando",
            "item_2_5_e": r"^e\) vagas novas em equipe de Saúde da Família - eSF implantadas, sem médico, nos municípios com maior vulnerabilidade",
        },
    },
    {
        "id": "portaria_gm_ms_4853_2024",
        "arquivo": "portaria_gm_ms_4853_2024_dou.html",
        "url": DOU + "portaria-gm/ms-n-4.853-de-10-de-julho-de-2024-574023155",
        "ato": "Portaria GM/MS nº 4.853, de 10/07/2024 (apoio ao RS)",
        "trechos": {
            "art2_I_c": r"^c\) não-aplicação do desconto preconizado na Portaria GM/MS nº 752",
        },
    },
    {
        "id": "portaria_gm_ms_5422_2024",
        "arquivo": "portaria_gm_ms_5422_2024_dou.html",
        "url": DOU + "portaria-gm/ms-n-5.422-de-2-de-outubro-de-2024-590809552",
        "ato": "Portaria GM/MS nº 5.422, de 02/10/2024 (altera a 485/2023)",
        "trechos": {
            "art2_p1_III": r"^III - os municípios de perfil de muito alta vulnerabilidade",
            "art5_caput": r"^\"Art\. 5º Para priorização das vagas em municípios",
        },
    },
    {
        "id": "portaria_gm_ms_3493_2024",
        "arquivo": "portaria_gm_ms_3493_2024_dou.html.gz",
        "url": DOU + "portaria-gm/ms-n-3.493-de-10-de-abril-de-2024-553573811",
        "ato": "Portaria GM/MS nº 3.493, de 10/04/2024 (nova metodologia de cofinanciamento federal da APS)",
        "trechos": {
            "art9_p2": r"^§ 2º Os recursos de que tratam os componentes dos incisos II e III",
            "art12T": r"^\"Art\. 12-T\. A alteração do modelo de financiamento da APS",
            "art9_p3": r"^§ 3º Para transferência dos recursos dos componentes previstos nos incisos I, II e III",
            "art9B_caput": r"^\"Art\. 9º-B\. O cálculo do componente fixo",
            "art9B_esf_e1": r"^a\) estrato 1: R",
            "art9B_esf_e2": r"^b\) estrato 2: R\$ 16\.000,00",
            "art9B_esf_e3": r"^c\) estrato 3: R\$ 14\.000,00",
            "art9B_esf_e4": r"^d\) estrato 4: R\$ 12\.000,00",
            "art8": r"^Art\. 8º Esta Portaria entra em vigor",
            "anexo_VI_titulo": r"^MUNICÍPIOS E DISTRITO FEDERAL CONFORME CLASSIFICAÇÃO NO ÍNDICE",
        },
    },
    {
        "id": "portaria_gm_ms_7799_2025",
        "arquivo": "portaria_gm_ms_7799_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-7.799-de-20-de-agosto-de-2025-649872356",
        "ato": "Portaria GM/MS nº 7.799, de 20/08/2025 (altera o cofinanciamento da APS)",
        "trechos": {
            "art9B": r"^\"Art\. 9º-B\. O cálculo do componente de equidade",
        },
    },
    {
        "id": "portaria_gm_ms_5721_2024",
        "arquivo": "portaria_gm_ms_5721_2024_dou.html",
        "url": DOU + "portaria-gm/ms-n-5.721-de-11-de-novembro-de-2024-596289126",
        "ato": "Portaria GM/MS nº 5.721, de 11/11/2024 (incentivo de equidade em alimentação e nutrição na APS)",
        "trechos": {
            "art633_II_b": r"^b\) o Índice de Vulnerabilidade Social \(IVS\) vigente",
            "art634": r"^\"Art\. 634\. O incentivo será transferido",
            "quadro2": r"^Quadro 2 - Valor Adicional 1",
        },
    },
    {
        "id": "portaria_gm_ms_635_2023",
        "arquivo": "portaria_gm_ms_635_2023_dou.html",
        "url": DOU + "portaria-gm/ms-n-635-de-22-de-maio-de-2023-484773799",
        "ato": "Portaria GM/MS nº 635, de 22/05/2023 (equipes Multiprofissionais na APS - eMulti)",
        "trechos": {
            "art9_I": r"^I - o Índice de Vulnerabilidade Social - IVS do requerente",
            "art9_I_c": r"^c\) vulnerabilidade social média",
            "art9_I_d": r"^d\) vulnerabilidade social alta",
        },
    },
    {
        "id": "portaria_gm_ms_7954_2025",
        "arquivo": "portaria_gm_ms_7954_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-7.954-de-21-de-agosto-de-2025-650486579",
        "ato": "Portaria GM/MS nº 7.954, de 21/08/2025 (Unidades Odontológicas Móveis)",
        "trechos": {
            "art80C_caput": r"^Art\. 80-C\. São critérios para a priorização das doações das UOM",
            "criterio_ivs": r"^III - Índice de Vulnerabilidade Social - IVS, do Instituto de Pesquisa Econômica Aplicada - IPEA, alta ou muito alta",
        },
    },
    {
        "id": "portaria_gm_ms_9177_2025",
        "arquivo": "portaria_gm_ms_9177_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-9.177-de-8-de-dezembro-de-2025-673878058",
        "ato": "Portaria GM/MS nº 9.177, de 08/12/2025 (Programa Médicos pelo Brasil / Mais Médicos Eixo Vínculo)",
        "trechos": {
            "art4_p1": r"^§ 1º O Programa Mais Médicos Eixo Vínculo é composto por médicos especialistas em MFC ou clínica médica",
            "art5_p1_I_a": r"^a\) municípios de alta e muito alta vulnerabilidade social",
        },
    },
    {
        "id": "portaria_gm_ms_449_2023",
        "arquivo": "portaria_gm_ms_449_2023_dou.html",
        "url": DOU + "portaria-gm/ms-n-449-de-5-de-abril-de-2023-475784517",
        "ato": "Portaria GM/MS nº 449, de 05/04/2023 (emendas parlamentares ao SUS em 2023)",
        "trechos": {},
        "ausencia": [r"IVS", r"[Vv]ulnerabilidade [Ss]ocial"],
    },
    {
        "id": "portaria_gm_ms_3283_2024",
        "arquivo": "portaria_gm_ms_3283_2024_dou.html",
        "url": DOU + "portaria-gm/ms-n-3.283-de-7-de-marco-de-2024-547028906",
        "ato": "Portaria GM/MS nº 3.283, de 07/03/2024 (emendas parlamentares ao SUS em 2024)",
        "trechos": {
            "art6_caput": r"^Art\. 6º A aplicação das emendas parlamentares para incremento temporário",
            "art6_pu": r"^Parágrafo único\. Os Municípios que possuem indicador de vulnerabilidade social \(IVS\) maior que 0,3",
            "art11_I_c": r"^c\) os Estados e Municípios que possuem indicador de vulnerabilidade social \(IVS\) maior que 0,3",
        },
    },
    {
        "id": "portaria_gm_ms_6870_2025",
        "arquivo": "portaria_gm_ms_6870_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-6.870-de-15-de-abril-de-2025-624302164",
        "ato": "Portaria GM/MS nº 6.870, de 15/04/2025 (emendas parlamentares ao SUS em 2025)",
        "trechos": {
            "pu_pap": r"^Parágrafo único\. Os municípios que possuem indicador de vulnerabilidade social - IVS maior que 0,3",
            "mac_c": r"^c\) os Estados e Municípios que possuem indicador de vulnerabilidade social - IVS maior que 0,3",
        },
    },
    {
        "id": "portaria_gm_ms_6904_2025",
        "arquivo": "portaria_gm_ms_6904_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-6.904-de-28-de-abril-de-2025-626437097",
        "ato": "Portaria GM/MS nº 6.904, de 28/04/2025 (emendas individuais ao SUS em 2025)",
        "trechos": {
            "pu_pap": r"^Parágrafo único\. Os municípios que possuem indicador de vulnerabilidade social - IVS maior que 0,3",
            "mac_c": r"^c\) os Estados e Municípios que possuem indicador de vulnerabilidade social - IVS maior que 0,3",
        },
    },
    {
        "id": "portaria_gm_ms_6916_2025",
        "arquivo": "portaria_gm_ms_6916_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-6.916-de-6-de-maio-de-2025-627663968",
        "ato": "Portaria GM/MS nº 6.916, de 06/05/2025 (parcelas únicas de custeio da APS e da Atenção Especializada)",
        "trechos": {
            "art6_V": r"^V - habilitação de Serviço da Atenção Especializada",
            "art7_caput": r"^Art\. 7º Os recursos destinados às ações previstas no art\. 6º",
            "art7_III": r"^III - os Estados e Municípios que possuem indicador de vulnerabilidade social - IVS maior que 0,3",
        },
    },
    {
        "id": "portaria_gm_ms_8283_2025",
        "arquivo": "portaria_gm_ms_8283_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-8.283-de-30-de-setembro-de-2025-659599892",
        "ato": "Portaria GM/MS nº 8.283, de 30/09/2025 (emendas de bancada e comissão ao SUS em 2026)",
        "trechos": {
            "III": r"^III - os Estados e Municípios que possuem Indicador de Vulnerabilidade Social - IVS maior que 0,3",
        },
    },
    {
        "id": "portaria_gm_ms_10169_2026",
        "arquivo": "portaria_gm_ms_10169_2026_dou.html",
        "url": DOU + "portaria-gm/ms-n-10.169-de-19-de-janeiro-de-2026-682018763",
        "ato": "Portaria GM/MS nº 10.169, de 19/01/2026 (parcelas suplementares de custeio da APS e da MAC)",
        "trechos": {
            "art10_I": r"^I - ações do Programa Agora tem Especialistas - Componente Ambulatorial",
            "art10_II": r"^II - ações do Programa Agora tem Especialistas - Componente Cirúrgico",
            "art11_caput": r"^Art\. 11\. Os recursos destinados às ações previstas no art\. 10",
            "art11_III": r"^III - os Estados e Municípios que possuem indicador de vulnerabilidade social - IVS maior que 0,3",
        },
    },
    {
        "id": "portaria_gm_ms_10297_2026",
        "arquivo": "portaria_gm_ms_10297_2026_dou.html",
        "url": DOU + "portaria-gm/ms-n-10.297-de-27-de-fevereiro-de-2026-689565520",
        "ato": "Portaria GM/MS nº 10.297, de 27/02/2026 (emendas individuais ao SUS em 2026)",
        "trechos": {
            "pu_pap": r"^Parágrafo único\. Os Municípios que apresentarem Indicador de Vulnerabilidade Social - IVS superior a 0,3",
            "mac_c": r"^c\) os Estados e Municípios que apresentaram Indicador de Vulnerabilidade Social - IVS superior a 0,3",
        },
    },
    {
        "id": "portaria_gm_ms_12252_2026",
        "arquivo": "portaria_gm_ms_12252_2026_dou.html",
        "url": DOU + "portaria-gm/ms-n-12.252-de-29-de-setembro-de-2026-735410971",
        "ato": "Portaria GM/MS nº 12.252, de 29/09/2026 (emendas ao SUS em 2027)",
        "trechos": {
            "pu_pap": r"^Parágrafo único\. Os Municípios que apresentarem Indicador de Vulnerabilidade Social - IVS superior a 0,3",
            "mac_c": r"^c\) os Estados e Municípios que apresentaram Indicador de Vulnerabilidade Social - IVS superior a 0,3",
        },
    },
    {
        "id": "portaria_gm_ms_7266_2025",
        "arquivo": "portaria_gm_ms_7266_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-7.266-de-18-de-junho-de-2025-637187199",
        "ato": "Portaria GM/MS nº 7.266, de 18/06/2025 (Programa Agora Tem Especialistas)",
        "trechos": {},
        "ausencia": [r"IVS", r"[Vv]ulnerabilidade [Ss]ocial", r"\b485\b"],
    },
    {
        "id": "portaria_gm_ms_7177_2025",
        "arquivo": "portaria_gm_ms_7177_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-7.177-de-10-de-junho-de-2025-635330489",
        "ato": "Portaria GM/MS nº 7.177, de 10/06/2025 (Projeto Mais Médicos Especialistas)",
        "trechos": {
            "ementa": r"^Dispõe sobre o Projeto Mais Médicos Especialistas, instituído no âmbito do Programa Mais Médicos",
            "especialidades_pu": r"^Parágrafo único\. As especialidades médicas abrangidas neste Projeto observarão",
        },
        "ausencia": [r"IVS", r"[Vv]ulnerabilidade [Ss]ocial", r"\b485\b"],
    },
    {
        "id": "edital_sgtes_03_2025_retificacao",
        "arquivo": "edital_sgtes_03_2025_retificacao_dou.html",
        "url": DOU + "edital-665051514",
        "ato": "Retificação do Edital SGTES/MS nº 3/2025 (PMM-E, ciclo 1), DOU de 28/10/2025",
        "trechos": {
            "item_11_1_4": r"^11\.1\.4\. Para fins de alocação dos médicos especialistas no âmbito do PMM-E",
            "item_11_1_leia_se": r"Os médicos também farão jus ao recebimento de ajuda de custo",
        },
        "ausencia": [r"\b485\b"],
    },
    {
        "id": "edital_sgtes_03_2024_pro_residencia",
        "arquivo": "edital_sgtes_03_2024_pro_residencia_dou.html",
        "url": DOU + "edital-n-3-de-6-de-novembro-de-2024-594734463",
        "ato": "Edital SGTES/MS nº 3, de 06/11/2024 (Pró-Residência)",
        "trechos": {
            "criterio_uf": r"^b\) A média entre o Índice de Vulnerabilidade Social - IVS e o Índice de Desenvolvimento Humano - IDH, por UF",
            "desempate": r"^4\.5\.2\. Persistindo o empate, será considerado o Índice de Vulnerabilidade Social",
        },
    },
    {
        "id": "lei_15233_2025",
        "arquivo": "lei_15233_2025_planalto.html",
        "url": "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15233.htm",
        "ato": "Lei nº 15.233/2025 (institui o PMM-E no art. 22-D da Lei 12.871/2013; altera a Lei 13.958/2019)",
        "trechos": {
            "art22D_caput": r"22-D \. Fica instituído, no âmbito do Programa Mais Médicos, o Projeto Mais Médicos Especialistas",
            "art22D_p2": r"^§ 2º Os participantes do Projeto Mais Médicos Especialistas poderão fazer jus",
            "art22D_p4": r"^§ 4º Os profissionais que optarem por atuar em Municípios situados na Amazônia Legal",
            "lei13958_art2_III": r"locais de alta vulnerabilidade: localidades com alta proporção",
        },
        "ausencia": [r"\b485\b", r"IVS"],
    },
    {
        "id": "edital_sgtes_02_2025_gestores",
        "arquivo": "edital_sgtes_02_2025_gestores_dou.html",
        "url": DOU + "edital-n-2-de-10-de-junho-de-2025-635833557",
        "ato": "Edital SGTES/MS nº 2, de 10/06/2025 (adesão de gestores ao PMM-E)",
        "trechos": {
            "item_3_1": r"^3\.1\. Os municípios, estados e o Distrito Federal, por meio de suas respectivas Secretarias",
            "item_3_8": r"^3\.8\. Para a distribuição de médicos especialistas",
            "item_3_8_1": r"^3\.8\.1\. A baixa disponibilidade regional",
            "item_3_8_2": r"^3\.8\.2\. Fluxo dos usuários",
            "item_3_8_3": r"^3\.8\.3\. Capacidade de escala e escopo",
        },
        "ausencia": [r"\b485\b", r"IVS", r"[Vv]ulnerabilidade [Ss]ocial"],
    },
    {
        "id": "edital_sgtes_03_2025_ciclo1",
        "arquivo": "edital_sgtes_03_2025_ciclo1_dou.html",
        "url": DOU + "edital-de-chamamento-publico-n-3/2025-644135890",
        "ato": "Edital de Chamamento Público SGTES/MS nº 3/2025 (PMM-E, ciclo 1)",
        "trechos": {
            "item_4_1_4": r"^4\.1\.4\. Compete à SGTES/MS definir o quadro com as vagas priorizadas",
            "item_5_7": r"^5\.7\. O edital contemplará vagas para oferta imediata",
            "item_11_1_4": r"^11\.1\.4\. Para fins de alocação dos médicos especialistas",
            "item_11_1_4_a": r"^a\) Municípios classificados como de muito alta vulnerabilidade social",
            "item_11_1_4_b": r"^b\) Municípios classificados como de alta vulnerabilidade social",
            "item_11_1_4_c": r"^c\) Municípios classificados com média, baixa ou muito baixa",
        },
        "ausencia": [r"\b485\b"],
    },
    {
        "id": "edital_sgtes_28_2026_ciclo3",
        "arquivo": "edital_sgtes_06_2026_edital_28_2026_ciclo3.html",
        "tipo": "pdf_repositorio",
        "url": "https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e/edital",
        "ato": "Edital SGTES/MS nº 28/2026 (PMM-E, ciclo 3); PDF preservado por a03 com extensão .html",
        "ancoras_pdf": {
            "item_5_7": "redistribuídas para municípios com cadastro de reserva",
            "item_5_7_fim": "comprovada escassez de médicos especialistas",
            "item_11_2": "categorização municipal do índice de Vulnerabilidade Social",
            "item_11_1_1": "Os médicos também farão jus ao recebimento de ajuda de custo",
        },
        "ausencia": [r"\b485\b"],
    },
    {
        "id": "portaria_gm_ms_377_2022",
        "arquivo": "portaria_gm_ms_377_2022_dou.html.gz",
        "url": DOU + "portaria-gm/ms-n-377-de-22-de-fevereiro-de-2022-382238160",
        "ato": "Portaria GM/MS nº 377, de 22/02/2022 (incentivo temporário pós-covid na APS)",
        "trechos": {
            "art4": r"^Art\. 4º Para fins de transferência do incentivo financeiro de que trata esta Portaria, os municípios foram classificados",
            "art4_II": r"^II - índice de Vulnerabilidade Social \(IVS\)",
            "art5": r"^Art\. 5º O detalhamento metodológico",
        },
    },
    {
        "id": "portaria_gm_ms_1054_2022",
        "arquivo": "portaria_gm_ms_1054_2022_dou.html",
        "url": DOU + "portaria-gm/ms-n-1.054-de-9-de-maio-de-2022-400449596",
        "ato": "Portaria GM/MS nº 1.054, de 09/05/2022 (incentivo da Estratégia de Saúde Cardiovascular na APS)",
        "trechos": {
            "art4_IV": r"^IV - índice de Vulnerabilidade Social \(IVS\)",
            "art4_p2": r"^§ 2º A metodologia para a criação do índice de perfil municipal",
        },
    },
    {
        "id": "portaria_gm_ms_2979_2019",
        "arquivo": "portaria_gm_ms_2979_2019_dou.html",
        "url": DOU + "portaria-n-2.979-de-12-de-novembro-de-2019-227652180",
        "ato": "Portaria nº 2.979, de 12/11/2019 (Previne Brasil; dispositivos revogados pela 3.493/2024)",
        "trechos": {
            "vulnerabilidade": r"^II - a vulnerabilidade socioeconômica da população cadastrada",
            "classificacao_geografica": r"^§4º O critério de classificação geográfica",
        },
        "ausencia": [r"IVS", r"[ÍI]ndice de [Vv]ulnerabilidade"],
    },
    {
        "id": "portaria_gm_ms_3352_2021",
        "arquivo": "portaria_gm_ms_3352_2021_dou.html.gz",
        "url": DOU + "portaria-gm/ms-n-3.352-de-2-de-dezembro-de-2021-*-365060101",
        "ato": "Portaria GM/MS nº 3.352, de 02/12/2021, republicada (priorização e vagas do Médicos pelo Brasil; revogada pela 485/2023)",
        "trechos": {
            "criterio_vulneravel": r"^b\) percentual da população vulnerável socioeconomicamente",
            "definicao": r"^1\.1\. Para efeitos desta metodologia entende-se por população vulnerável",
        },
        "ausencia": [r"IVS", r"[ÍI]ndice de [Vv]ulnerabilidade"],
    },
]


# SHA-256 registrados na captura de 18/10/2026 (bytes da página e texto do ato).
HASHES: dict[str, dict[str, str | None]] = {
    "portaria_gm_ms_485_2023": {"sha256_bruto": "aed9712e20d902a49deb3bf3289a4f3c674584cd82532864dab90952d0b29786",
        "sha256_texto": "c5a13a2bf0172c729b399e6af8b884575f1124c96905b68b03e3bd06b28976fd"},
    "portaria_gm_ms_752_2023": {"sha256_bruto": "d364fa6bb4053b16788160a04c5bc54ff60a693176d0cad2abb5523992a4c8cb",
        "sha256_texto": "abf42607c1fb96dcb81ba685e2550e3a2b6245d7ef2ba55a9a5401565b576a77"},
    "portaria_gm_ms_752_2023_ses_sp": {"sha256_bruto": "ac29ccb10ad2df16e15794ac83eb4b6f2185a48c16de3b7b5504d6ab870d87bf",
        "sha256_texto": None},
    "edital_saps_11_2023": {"sha256_bruto": "1c1f8d8e442d587edf9f640b509c8dfa8bb9fe310242a5d373c1cca143a68a2c",
        "sha256_texto": "ce7cc4fb0345aa30b4760fe34b55b54eccbaf7aa4f633e916bc218f7cc47d06b"},
    "portaria_interm_ms_mec_604_2023": {"sha256_bruto": "42884aa67cab540afacc6410d7954134f14e7cecae0af2f0a1380f5ce5fea36c",
        "sha256_texto": "799c61fc16b6e05357fa5c68949378645a0565dbc234d9e87194c5db0474d814"},
    "portaria_interm_ms_mec_07_2026": {"sha256_bruto": "5436be051dbc04189b1a7be3bbc856046d0435dfbb3f0346d638988064a18869",
        "sha256_texto": "873a70d8b4dda37375b42673f3f172033fd0bff13cd7a8303b1aebc4efa15ee3"},
    "portaria_interm_ms_mec_10032_2025": {"sha256_bruto": "0583d283b2eaa7497a55a2748675a5dca10e86342ab091169d1623b644938b39",
        "sha256_texto": "fc1683b64514e829fff57ec722cebb01d0339e3552a08c9e05ebe8b6f1ee3496"},
    "lei_14621_2023": {"sha256_bruto": "4a731149c9e1b7814bd5518773b83cd8f2c9a02d3c5475fdc2672b1c1f625b8d",
        "sha256_texto": "017d4f4b26564bc9593464c0caa2fb718e77cfe6c3d26c45aed9823a0795002e"},
    "portaria_sgtes_ms_169_2025": {"sha256_bruto": "dc38cd9e18aec8f81aaa836fdad0592a60ed97ed41e6924588062cfed10c5d29",
        "sha256_texto": "d2f46180f3799bbb33af80be20f2110db5a82d57278b9d9641622d2960b41951"},
    "edital_saps_05_2023_medicos": {"sha256_bruto": "c59d428f54535f3f3308281c20934db8eeb5b8fab91de06287cf939296e09509",
        "sha256_texto": "e73b876c434ecefb1c58f20ddaede7e63664599cb9a86b19fb4d21ff45457bec"},
    "edital_saps_13_2023_medicos": {"sha256_bruto": "7314c5289e100fbf5af6951b0215cb2aae8b194416643a5e09308bf2ecdf100e",
        "sha256_texto": "fe17e31230526e366aabe18b8dfddfb0c4a3cceeda91f41390ac12b09d96b095"},
    "edital_saps_04_2024_medicos": {"sha256_bruto": "992893ea16490f3cffd8a4688b7b1ef6f93990788bdd39ea51b04813a3ea5442",
        "sha256_texto": "cbb8ffbfb035718f2954a56ed2acb42d9a1a792bb1ab55181ba0003ead90700a"},
    "edital_conjunto_saps_sgtes_07_2025": {"sha256_bruto": "c9db05db469491c5dd74f4eb3ca8779ce965c64f5e13228a14a0972aec140ba4",
        "sha256_texto": "bb834244d2edb816ff7fd425567fb83d8747d8f06f9299273b7955a07cd4e801"},
    "edital_saps_03_2024_municipios": {"sha256_bruto": "f7d0ddfd3b36c85529449689a78a418c4ba4226484bccb49c94d6a8178e223fe",
        "sha256_texto": "30dce2d13dc5c287936259594b6b5f874847b6e16311f518d96fb737095995c7"},
    "edital_saps_02_2025_municipios": {"sha256_bruto": "a7d14f17a80bf782dd8892776009725d6ace4073b6b305f782fa33d3905f69f9",
        "sha256_texto": "2f328ad6f9632782555fcc7e850d677f86de0d210d168697ebf986daec489edc"},
    "portaria_gm_ms_4853_2024": {"sha256_bruto": "f2bfa1fcdabee5a1d24fa9ac71301c1a1529a6e543da58fb6e30ba571777517b",
        "sha256_texto": "1ecd9bb348435df809256f595bf6bf04d1b6772b1da172b744a4083d377ef821"},
    "portaria_gm_ms_5422_2024": {"sha256_bruto": "a5d569cb5942da23d947b1b74ea7601e0db5136c0133243c9fdaaea8e62f1211",
        "sha256_texto": "3ad9d645bf54dad966316db33671e19f601d8ce1abe38c1db2b7b8fa846e6b54"},
    "portaria_gm_ms_3493_2024": {"sha256_bruto": "9af9828420aae6dff060d7efe8e9a5cc47ccac7245150c6e43495cdd79874f91",
        "sha256_texto": "0efec39029bdd8adddca95977d4f469e6b176f6e37dc91c449d8929ae44da5d3"},
    "portaria_gm_ms_7799_2025": {"sha256_bruto": "284830fae3255317678a98b44e68910492fe6a17bfd0d9b7f25183d1d09afc81",
        "sha256_texto": "5ba23fe0b18d1f0f29b9c681405f40ba296db8385297b616fc9852aa00d2e425"},
    "portaria_gm_ms_5721_2024": {"sha256_bruto": "6ede41820f931b030fc6c89916dc8995417f96ab4a830d14b75fca2490f5f7ba",
        "sha256_texto": "e8a73b9b6acf24af7b0c6899fc3be42a3c38942971a3f4486aa0cf59bdfb61fc"},
    "portaria_gm_ms_635_2023": {"sha256_bruto": "e45532b4f82d65d3787a4253fd850edd5ddfdbf7ac82a96b7440760114c65ba8",
        "sha256_texto": "ea2bb8545a8301059394b006740dc98e506a19eed4996a72cd3dcb2c0a0e6581"},
    "portaria_gm_ms_7954_2025": {"sha256_bruto": "e6c77ef7de865c95d495339dd399307ba44c61dcad01dbd0f2d372e40d5fe66f",
        "sha256_texto": "e82a92fe492be73ebe5ed495093753406948ceba83258735da001280ed733143"},
    "portaria_gm_ms_9177_2025": {"sha256_bruto": "38ed660e78d67f92128e1fb526c734b04d55b4fddd10f94122e0ed75dcb17f3c",
        "sha256_texto": "22b317955aa4ec372ba5692933dcaecc38c0ca859cd9eaee8f3c99482232a806"},
    "portaria_gm_ms_449_2023": {"sha256_bruto": "a51c2878cbb4120408dc922a75908f65a9015fd7e93798eb150087b60b65f07e",
        "sha256_texto": "ce59f6c6678f308159352d26c3dc903f0544fa107b91bcf251f7f355454e6a06"},
    "portaria_gm_ms_3283_2024": {"sha256_bruto": "330ac893c050fa1e9c3173b92e12ab3074193aadfe98ea792ca0cb4a988fc823",
        "sha256_texto": "78ffa9684e42427633d6d5b808b6f11dcc2561f74af92aea778ac72149128687"},
    "portaria_gm_ms_6870_2025": {"sha256_bruto": "d4bd08d1684318514318074050ae57385f274e0941c7844e92919507fdc20a3f",
        "sha256_texto": "28b2940108176088cf099805e7114243ed2391e604e2e9126b3a60444bc02d6d"},
    "portaria_gm_ms_6904_2025": {"sha256_bruto": "4bdeacc988bec9ccf4678cb40b9e8d33e21e6b4466489eeaada80478624acf5f",
        "sha256_texto": "29abdeca847b9d1d00cec2220291b49d082ff4a373940ca73d139dc2672be7f2"},
    "portaria_gm_ms_6916_2025": {"sha256_bruto": "8857c805d4e155cca16e80e49170e9af015dab5cfb5fc24e0294f024f9f46e54",
        "sha256_texto": "ad191395da1d84aa7683e538cfae2585a632ac52bf8292838f8a188d2f635400"},
    "portaria_gm_ms_8283_2025": {"sha256_bruto": "a4a9f840a8a4bd50fabc9361f2176319cf71c3943c9d637c6f6e7c2a5267ccec",
        "sha256_texto": "4e26396d9b0ed319a74891c74d8deebd7dc6fb5ecacf1abec84051de6d84ffff"},
    "portaria_gm_ms_10169_2026": {"sha256_bruto": "6c202039993cd6f369bf3d9d3c271f101f9913fa0f65bb72d4ebebc22576eeb2",
        "sha256_texto": "d020907f62a6cfab82e676a6790d3bf87db08aa9698fd61c6236a7f1dd42dcdd"},
    "portaria_gm_ms_10297_2026": {"sha256_bruto": "c69c0bd64685f5ccba4eee066af8482da4ad88f916de4698050e5b5e997b1a2d",
        "sha256_texto": "0fb600140f238a018eba3ffa930ced476a73c21502c093be40f52d6de1c1f536"},
    "portaria_gm_ms_12252_2026": {"sha256_bruto": "7053d8cfe80f264e2be6dfbcad696766c716653f5dcf1a8f741d33026d8e5338",
        "sha256_texto": "66504385fc23581aaffcc618f09ead014562f3044edc96866a74568c9b82b299"},
    "portaria_gm_ms_7266_2025": {"sha256_bruto": "327cd5a4a023dfa17bfb2f806ec15c38b78748019cedf6ef99309380414d05fb",
        "sha256_texto": "487a7fd010c5d335da1fd09ed50cb01c09a8b262569fe97cfabee7fee3ef5438"},
    "portaria_gm_ms_7177_2025": {"sha256_bruto": "df646c6b057935dbcaf1948365de4b729d593b7a9e80d6b765d268976f949ddf",
        "sha256_texto": "19372ef2cc6e6679c55013f119c02411e659af9dca6500c77721179ed0cfa8ea"},
    "edital_sgtes_03_2025_retificacao": {"sha256_bruto": "c5f8a3979f7f82a91676915f2d9ad3db8ebc9f92d6c1ffcf0c38683c57bb67ba",
        "sha256_texto": "ec1fc01c08df049c1768f722281dee2e8cdfe93f4e62bd76203c1c27c00d70c0"},
    "edital_sgtes_03_2024_pro_residencia": {"sha256_bruto": "9241607257feae927d0c67ca3092bf734114511a827faec4b4ca444990ab5a3b",
        "sha256_texto": "e7c967099b5fa4be7167b81981bab2ec80d7e77bc0858a91611d5ca47535d266"},
    "lei_15233_2025": {"sha256_bruto": "ea4ebdbe706cc675aaa5b1d9d9c0afdfceac9e65e4d285ec8a94485f026ca609",
        "sha256_texto": "bdc0b244683c76fc0c6a81aafa9f8883b2ec685680bcb9e9ab4923eee8289672"},
    "edital_sgtes_02_2025_gestores": {"sha256_bruto": "be82c8159f585a0d167a408146116a884a3e19179dff012ec602b9b09d69b268",
        "sha256_texto": "cf50b72e851b1a853b7fdfccb434fecc0ace6a2a2e6e94b1e52a2c1c08379e1e"},
    "edital_sgtes_03_2025_ciclo1": {"sha256_bruto": "523025ca92b6ae04d8187828e0514b488b0d933b0cdba579c513aa18278f0d39",
        "sha256_texto": "9e0bed2145e228c98566680fc23fac0802c2c3002b15334056a03ed8876ff482"},
    "edital_sgtes_28_2026_ciclo3": {"sha256_bruto": "eb1e07b44465edc8226efe0743ed1fd8fca97de0f88d5886e249478052c84306",
        "sha256_texto": None},
    "portaria_gm_ms_377_2022": {"sha256_bruto": "df3ed7197c04f6d7383686fb0746d7395b9c939a2c8f5cabe567c26252306a94",
        "sha256_texto": "f88c8cc985c893e551192a534045908973614cd0dc7e9f7153aad53b98e8acbf"},
    "portaria_gm_ms_1054_2022": {"sha256_bruto": "b8144e86dc25131e58f26fa19f879ae02091f0ab807dcdf47076bab6ec818f32",
        "sha256_texto": "0cdaa39b568d047dc55d58b0623ba943bc70fee057377d00750e030e584b5715"},
    "portaria_gm_ms_2979_2019": {"sha256_bruto": "0b7e1354dc713ded6b909b1279e46f407f99db99ef97ecf37910a522c56e94c2",
        "sha256_texto": "79892bea2099a4eab9748db34087bcfd46c2b5083dc1295d0aa3114b4f2354fb"},
    "portaria_gm_ms_3352_2021": {"sha256_bruto": "f322cf934a573cb26f8af50d2b1da232c241017b5d8c51ab346eb01d481cb8db",
        "sha256_texto": "c5b88c9eeb7028224b75168e1698e74cefb10c2619d271a7b66738dfa47e36d5"},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(1 << 20):
            h.update(bloco)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def decodificar(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252")  # páginas do Planalto


def ler_cache(path: Path) -> bytes:
    raw = path.read_bytes()
    return gzip.decompress(raw) if path.suffix == ".gz" else raw


def gravar_cache(path: Path, conteudo: bytes) -> None:
    parcial = path.with_name(path.name + ".part")
    dados = gzip.compress(conteudo, compresslevel=9, mtime=0) if path.suffix == ".gz" else conteudo
    parcial.write_bytes(dados)
    parcial.replace(path)


def baixar(url: str) -> bytes:
    # O firewall do in.gov.br recusa (403) cabeçalhos mínimos; estes são aceitos.
    req = urllib.request.Request(url, headers={
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120 Safari/537.36"),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "pt-BR,pt;q=0.9",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def linhas_do_ato(fonte: dict, raw: bytes) -> list[str]:
    html = decodificar(raw)
    return texto_planalto(html) if "planalto" in fonte["url"] else texto_linhas(html)


def hash_texto(linhas: list[str]) -> str:
    return sha256_bytes("\n".join(linhas).encode("utf-8"))


def obter(fonte: dict) -> tuple[bytes, str]:
    """Bytes conferidos da fonte e o status da aquisição (fail closed)."""
    esperado = HASHES[fonte["id"]]
    tipo = fonte.get("tipo", "html")
    path = (IVS_REGRA if tipo == "pdf_repositorio" else RAW) / fonte["arquivo"]
    if path.exists():
        raw = ler_cache(path)
        if sha256_bytes(raw) == esperado["sha256_bruto"]:
            return raw, "cache_conferido_bytes"
        # Página do DOU baixada de novo: cabeçalho muda, o texto do ato não pode mudar.
        if tipo == "html" and hash_texto(linhas_do_ato(fonte, raw)) == esperado["sha256_texto"]:
            return raw, "cache_conferido_texto"
        raise ValueError(f"{path.relative_to(ROOT)}: SHA-256 diferente do registrado; "
                         "arquivo substituído ou corrompido (apague-o para baixar de novo)")
    if tipo == "pdf_repositorio":
        raise FileNotFoundError(f"{path.relative_to(ROOT)} ausente: é adquirido por a03, não por a10")
    raw = baixar(fonte["url"])
    if tipo == "pdf":
        if sha256_bytes(raw) != esperado["sha256_bruto"]:
            raise ValueError(f"{fonte['id']}: PDF baixado com SHA-256 diferente do registrado")
    elif hash_texto(linhas_do_ato(fonte, raw)) != esperado["sha256_texto"]:
        raise ValueError(f"{fonte['id']}: texto do ato baixado difere do capturado em {DATA_CAPTURA}")
    RAW.mkdir(parents=True, exist_ok=True)
    gravar_cache(path, raw)
    return raw, "baixado_agora_texto_conferido"


def texto_pdf(path: Path) -> str | None:
    """Texto do PDF via `pdftotext`, se instalado; None se não houver."""
    if shutil.which("pdftotext") is None:
        return None
    out = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, check=True).stdout
    return unicodedata.normalize("NFKC", out.decode("utf-8", errors="replace"))


def texto_linhas(html: str) -> list[str]:
    """Texto do corpo do ato, uma linha por parágrafo ou célula."""
    m = re.search(r'<div class="texto-dou">(.*?)</div>\s*</div>', html, re.S)
    corpo = m.group(1) if m else html
    corpo = re.sub(r"<script.*?</script>|<style.*?</style>", " ", corpo, flags=re.S | re.I)
    corpo = re.sub(r"<(p|br|tr|td|li|h\d)[^>]*>", "\n", corpo, flags=re.I)
    corpo = re.sub(r"<[^>]+>", " ", corpo)
    corpo = html_lib.unescape(corpo)
    corpo = re.sub(r"[ \t\xa0\r]+", " ", corpo)
    linhas = [ln.strip() for ln in corpo.split("\n")]
    return [ln for ln in linhas if ln]


def texto_planalto(html: str) -> list[str]:
    """No Planalto, um parágrafo vem quebrado em várias linhas; junta por <p>."""
    corpo = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S | re.I)
    corpo = re.sub(r"<strike>.*?</strike>", " ", corpo, flags=re.S | re.I)
    corpo = re.sub(r"\s+", " ", corpo)  # quebras do código-fonte não são parágrafos
    corpo = re.sub(r"<p[^>]*>", "\n", corpo, flags=re.I)
    corpo = re.sub(r"<[^>]+>", " ", corpo)
    corpo = html_lib.unescape(corpo)
    corpo = re.sub(r"[ \t\xa0]+", " ", corpo)
    return [ln.strip() for ln in corpo.split("\n") if ln.strip()]


def metadados_dou(html: str) -> dict:
    out = {}
    for chave, padrao in {
        "data_publicacao_dou": r'publicado-dou-data">([^<]+)',
        "edicao_dou": r'edicao-dou-data">([^<]+)',
        "secao_dou": r'class="secao-dou">(Seção:[^<]+)',
    }.items():
        m = re.search(padrao, html)
        if m:
            out[chave] = m.group(1).strip()
    return out


def processar_fonte(fonte: dict) -> tuple[dict, list[str] | None]:
    tipo = fonte.get("tipo", "html")
    path = (IVS_REGRA if tipo == "pdf_repositorio" else RAW) / fonte["arquivo"]
    raw, status = obter(fonte)
    reg = {
        "id": fonte["id"],
        "ato": fonte["ato"],
        "url": fonte["url"],
        "caminho": str(path.relative_to(ROOT)),
        "comprimido_gzip": path.suffix == ".gz",
        "data_captura": DATA_CAPTURA,
        "status": status,
        "tamanho_bytes": len(raw),
        "sha256_bruto": sha256_bytes(raw),
    }
    if tipo == "pdf":
        reg["nota"] = "PDF preservado como cópia secundária; os trechos citados vêm da página do DOU"
        return reg, None
    if tipo == "pdf_repositorio":
        texto = texto_pdf(path)
        reg["nota"] = ("PDF adquirido por a03; trechos conferidos por âncoras via pdftotext, "
                       "quando disponível (sem pdftotext, o relatório usa transcrição manual)")
        if texto is None:
            reg["ancoras_conferidas"] = None
            return reg, None
        plano = re.sub(r"\s+", " ", texto)
        faltando = [r for r, a in fonte["ancoras_pdf"].items() if a not in plano]
        if faltando:
            raise ValueError(f"{fonte['id']}: âncoras não encontradas no PDF: {faltando}")
        reg["ancoras_conferidas"] = fonte["ancoras_pdf"]
        reg["termos_ausentes_conferidos"] = {p: len(re.findall(p, plano)) for p in fonte.get("ausencia", [])}
        return reg, None
    html = decodificar(raw)
    reg.update(metadados_dou(html))
    linhas = linhas_do_ato(fonte, raw)
    reg["sha256_texto"] = hash_texto(linhas)
    trechos = {}
    for rotulo, padrao in fonte["trechos"].items():
        achados = [ln for ln in linhas if re.search(padrao, ln)]
        if not achados:
            raise ValueError(f"{fonte['id']}: trecho '{rotulo}' não encontrado no texto preservado")
        trechos[rotulo] = achados[0][:1500]
    reg["trechos"] = trechos
    if "ausencia" in fonte:
        texto = "\n".join(linhas)
        reg["termos_ausentes_conferidos"] = {
            p: len(re.findall(p, texto)) for p in fonte["ausencia"]
        }
    return reg, linhas


def extrair_anexo_vi(linhas: list[str]) -> pd.DataFrame:
    """Anexo VI da 3.493/2024: UF, IBGE, nome, código IVS, habitantes, porte, IED."""
    i0 = next(i for i, ln in enumerate(linhas) if ln.startswith("MUNICÍPIOS E DISTRITO FEDERAL CONFORME CLASSIFICAÇÃO"))
    corpo = linhas[i0 + 1:]
    regs = []
    i = 0
    while i + 6 < len(corpo):
        bloco = corpo[i:i + 7]
        if (re.fullmatch(r"[A-Z]{2}", bloco[0]) and re.fullmatch(r"\d{6}", bloco[1])
                and re.fullmatch(r"[1-5]", bloco[3]) and re.fullmatch(r"[1-4]-.*", bloco[5])
                and re.fullmatch(r"[1-4]", bloco[6])):
            regs.append(bloco)
            i += 7
        else:
            i += 1
    df = pd.DataFrame(regs, columns=["uf", "co_ibge", "nome_municipio", "ivs_codigo_portaria",
                                     "populacao_ibge_2022_portaria", "porte_populacional", "estrato_ied"])
    df["populacao_ibge_2022_portaria"] = df["populacao_ibge_2022_portaria"].str.replace(".", "", regex=False).astype(int)
    df["ivs_codigo_portaria"] = df["ivs_codigo_portaria"].astype(int)
    df["estrato_ied"] = df["estrato_ied"].astype(int)
    df["porte_codigo"] = df["porte_populacional"].str[0].astype(int)
    total = next((ln for ln in reversed(linhas) if re.fullmatch(r"[\d.]+ municípios", ln)), None)
    if total is None or int(total.split()[0].replace(".", "")) != len(df):
        raise ValueError(f"Anexo VI: {len(df)} linhas extraídas; total declarado no ato: {total}")
    if df["co_ibge"].duplicated().any():
        raise ValueError("Anexo VI: município repetido")
    df["fonte"] = "Portaria GM/MS 3.493/2024, Anexo VI"
    df["natureza_dos_dados"] = "EMPIRICO"
    return df.sort_values("co_ibge").reset_index(drop=True)


def classe_fechada_direita(s_mil: int) -> int:
    """Código 1 = muito alta ... 5 = muito baixa; limite pertence à classe de baixo (≤)."""
    if s_mil > 500:
        return 1
    if s_mil > 400:
        return 2
    if s_mil > 300:
        return 3
    if s_mil > 200:
        return 4
    return 5


def classe_fechada_esquerda(s_mil: int) -> int:
    """Mesma escala; limite pertence à classe de cima (≥), como no texto da 485/2023."""
    if s_mil >= 500:
        return 1
    if s_mil >= 400:
        return 2
    if s_mil >= 300:
        return 3
    if s_mil >= 200:
        return 4
    return 5


ROTULO_CODIGO = {1: "MUITO ALTA VULNERABILIDADE", 2: "ALTA VULNERABILIDADE", 3: "MEDIA VULNERABILIDADE",
                 4: "BAIXA VULNERABILIDADE", 5: "MUITO BAIXA VULNERABILIDADE"}


def quadro2_5721(linhas: list[str]) -> dict:
    """Quadro 2 da 5.721/2024: categoria, intervalo e número de municípios."""
    i0 = next(i for i, ln in enumerate(linhas) if ln.startswith("Quadro 2 - Valor Adicional 1"))
    out = {}
    for j in range(i0, i0 + 40):
        if linhas[j] in ("Muito Baixa", "Baixa", "Média", "Alta", "Muito Alta"):
            out[linhas[j]] = {"intervalo": linhas[j + 1], "valor_adicional_1": linhas[j + 2],
                              "n_municipios": int(linhas[j + 3])}
    if len(out) != 5:
        raise ValueError(f"Quadro 2 da 5.721/2024 incompleto: {out}")
    return out


def esquema_pmmb() -> dict:
    with zipfile.ZipFile(PMMB_ZIP) as z:
        nome = z.namelist()[0]
        bruto = z.read(nome)
    df = pd.read_csv(io.BytesIO(bruto), sep=";", dtype=str, encoding="latin1")
    mun = df[df["nivel"] == "MUNICIPAL"]
    of = pd.read_csv(A08, dtype={"co_ibge": str})
    return {
        "arquivo": str(PMMB_ZIP.relative_to(ROOT)),
        "sha256_zip": sha256(PMMB_ZIP),
        "arquivo_interno": nome,
        "colunas": list(df.columns),
        "n_colunas": int(df.shape[1]),
        # Só o número de valores distintos por coluna (todas as linhas, sem
        # cruzar com IVS): serve para achar colunas constantes ou mal rotuladas.
        "valores_distintos_por_coluna": {c: int(df[c].nunique()) for c in df.columns},
        "linhas_por_nivel": {k: int(v) for k, v in df["nivel"].value_counts().sort_index().items()},
        "dt_referencia": sorted(df["dt_referencia"].unique().tolist()),
        "dt_geracao": sorted(df["dt_geracao"].unique().tolist()),
        "municipal_co_ibge_unicos": int(mun["co_ibge"].nunique()),
        "municipal_com_ivs_oficial_a08": int(mun["co_ibge"].isin(of["co_ibge"]).sum()),
        "a08_sem_linha_municipal_pmmb": int((~of["co_ibge"].isin(mun["co_ibge"])).sum()),
        "nota": "esquema e cobertura apenas; nenhum valor de vaga ou médico foi cruzado com o IVS",
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifesto, textos = [], {}
    for fonte in FONTES:
        reg, linhas = processar_fonte(fonte)
        manifesto.append(reg)
        textos[fonte["id"]] = linhas

    ied = extrair_anexo_vi(textos["portaria_gm_ms_3493_2024"])
    saida_ied = OUT / "a10_ied_aps_2024_municipio.csv"
    ied.to_csv(saida_ied, index=False)

    of = pd.read_csv(A08, dtype={"co_ibge": str})
    of = of[of["ivs"].notna()].copy()
    casas = of["ivs"].map(lambda v: len(repr(float(v)).split(".")[1].rstrip("0")))
    of["s_mil"] = (of["ivs"] * 1000).round().astype(int)
    of["classe_dir"] = of["s_mil"].map(classe_fechada_direita)
    of["classe_esq"] = of["s_mil"].map(classe_fechada_esquerda)
    cat = pd.read_csv(A07_CAT, dtype={"co_ibge": str})

    # 1. Anexo VI da 3.493/2024 contra o IVS oficial.
    k = ied.merge(of, on="co_ibge", how="inner")
    regra_ied = (ied.groupby(["ivs_codigo_portaria", "porte_codigo"])["estrato_ied"]
                 .agg(lambda s: sorted(set(int(x) for x in s))).reset_index())
    diag_ied = {
        "municipios_anexo_vi": int(len(ied)),
        "com_ivs_oficial_a08": int(len(k)),
        "sem_ivs_oficial_a08": sorted(set(ied["co_ibge"]) - set(of["co_ibge"])),
        "codigo_igual_classe_fechada_a_direita": int((k["ivs_codigo_portaria"] == k["classe_dir"]).sum()),
        "codigo_igual_classe_fechada_a_esquerda": int((k["ivs_codigo_portaria"] == k["classe_esq"]).sum()),
        "faixa_ivs_oficial_por_codigo": {
            str(c): {"min": float(g["ivs"].min()), "max": float(g["ivs"].max()), "n": int(len(g))}
            for c, g in k.groupby("ivs_codigo_portaria")
        },
        "estrato_ied_por_codigo_ivs_e_porte": [
            {"ivs_codigo": int(r.ivs_codigo_portaria), "porte_codigo": int(r.porte_codigo),
             "estratos_observados": r.estrato_ied} for r in regra_ied.itertuples()
        ],
        "regra_deterministica": bool(regra_ied["estrato_ied"].map(len).eq(1).all()),
        "porte_codigo_rotulos": dict(sorted({int(a): b for a, b in zip(ied["porte_codigo"], ied["porte_populacional"])}.items())),
    }

    # 2. Categoria do consolidado PMMB (a07) contra o IVS oficial.
    kc = cat.merge(of, on="co_ibge", how="inner")
    diag_pmmb_cat = {
        "comparados": int(len(kc)),
        "igual_classe_fechada_a_direita": int((kc["categoria_ivs_admin"] == kc["classe_dir"].map(ROTULO_CODIGO)).sum()),
        "igual_classe_fechada_a_esquerda": int((kc["categoria_ivs_admin"] == kc["classe_esq"].map(ROTULO_CODIGO)).sum()),
    }

    # 3. Municípios exatamente sobre os limites (variável de atribuição).
    sobre = {}
    for lim in LIMITES_MIL:
        sub = of[of["s_mil"] == lim]
        s_cat = sub.merge(cat, on="co_ibge", how="left")["categoria_ivs_admin"]
        s_ied = sub.merge(ied, on="co_ibge", how="left")["ivs_codigo_portaria"]
        sobre[f"{lim / 1000:.3f}"] = {
            "n_municipios": int(len(sub)),
            "corte_da_bolsa": lim in CORTES_BOLSA_MIL,
            "categoria_pmmb_a07": {str(a): int(b) for a, b in s_cat.value_counts(dropna=False).items()},
            "codigo_ivs_anexo_vi_3493": {str(a): int(b) for a, b in s_ied.value_counts(dropna=False).items()},
        }

    # 4. Quadro 2 da 5.721/2024 contra as duas convenções.
    q2 = quadro2_5721(textos["portaria_gm_ms_5721_2024"])
    ordem = {"Muito Alta": 1, "Alta": 2, "Média": 3, "Baixa": 4, "Muito Baixa": 5}
    diag_5721 = {
        "quadro_2": q2,
        "total_quadro_2": int(sum(v["n_municipios"] for v in q2.values())),
        "a08_municipios_com_ivs": int(len(of)),
        "contagem_a08_fechada_a_esquerda": {c: int((of["classe_esq"] == n).sum()) for c, n in ordem.items()},
        "contagem_a08_fechada_a_direita": {c: int((of["classe_dir"] == n).sum()) for c, n in ordem.items()},
        "nota": ("o Quadro 2 cobre municípios criados depois de 2010 que não estão em a08; "
                 "a comparação é indicativa da convenção, não uma reprodução exata"),
    }

    # 5. Totais usados no relatório, calculados aqui (nada digitado à mão).
    totais = {
        "sobre_os_cortes_da_bolsa": int(sum(v["n_municipios"] for v in sobre.values() if v["corte_da_bolsa"])),
        "sobre_os_quatro_limites": int(sum(v["n_municipios"] for v in sobre.values())),
        "diferenca_convencoes_ied": int(diag_ied["codigo_igual_classe_fechada_a_direita"]
                                        - diag_ied["codigo_igual_classe_fechada_a_esquerda"]),
        "diferenca_convencoes_pmmb": int(diag_pmmb_cat["igual_classe_fechada_a_direita"]
                                         - diag_pmmb_cat["igual_classe_fechada_a_esquerda"]),
        "fontes_no_manifesto": int(len(manifesto)),
        "fontes_em_normas_ivs": int(sum(1 for f in FONTES if f.get("tipo") != "pdf_repositorio")),
    }
    if not (totais["diferenca_convencoes_ied"] == totais["diferenca_convencoes_pmmb"]
            == totais["sobre_os_quatro_limites"]):
        raise ValueError(f"as convenções deveriam divergir só nos pontos de massa: {totais}")

    diagnostico = {
        "data_execucao": DATA_CAPTURA,
        "outcomes_abertos": False,
        "natureza_dos_dados": "EMPIRICO",
        "totais": totais,
        "entradas": {
            str(A08.relative_to(ROOT)): sha256(A08),
            str(A07_CAT.relative_to(ROOT)): sha256(A07_CAT),
            str(PMMB_ZIP.relative_to(ROOT)): sha256(PMMB_ZIP),
        },
        "ied_aps_3493_2024": diag_ied,
        "categoria_pmmb_a07": diag_pmmb_cat,
        "ivs_a08_max_casas_decimais": int(casas.max()),
        "municipios_sobre_os_limites": sobre,
        "portaria_5721_2024_quadro_2": diag_5721,
        "esquema_consolidado_pmmb": esquema_pmmb(),
        "saidas": {str(saida_ied.relative_to(ROOT)): {"linhas": int(len(ied)), "sha256": sha256(saida_ied)}},
    }
    (OUT / "a10_diagnostico_cortes_normas.json").write_text(
        json.dumps(diagnostico, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (OUT / "a10_manifesto_normas_ivs.json").write_text(
        json.dumps({
            "data_execucao": DATA_CAPTURA,
            "natureza_dos_dados": "EMPIRICO",
            "descricao": "atos normativos preservados para a auditoria 18 (políticas nos mesmos cortes de IVS)",
            "diretorio": str(RAW.relative_to(ROOT)),
            "fontes": manifesto,
            "buscas_dou": BUSCAS_DOU,
            "nao_preservados": [
                {"url": "https://bvsms.saude.gov.br/bvs/saudelegis/gm/2023/prt0752_19_06_2023.html",
                 "motivo": "HTTP 403 do servidor (F5) em 18/10/2026; usada a página do DOU"},
                {"url": "https://www.saude.mt.gov.br/storage/old/files/485-[28953-170523-SES-MT].pdf",
                 "motivo": "conexão encerrada pelo servidor em 18/10/2026; usada a página do DOU"},
            ],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"fontes": len(manifesto), "ied_linhas": len(ied),
                      "ied_dir": diag_ied["codigo_igual_classe_fechada_a_direita"],
                      "ied_esq": diag_ied["codigo_igual_classe_fechada_a_esquerda"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
