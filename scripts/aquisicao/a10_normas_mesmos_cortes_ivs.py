"""Normas federais que usam faixas de IVS nos cortes da bolsa do PMM-E (tarefa D).

Protocolo: `docs/06_execucao/40_protocolo_multioutcome_rdd_bolsa.md`, seção 4.
Relatório: `docs/auditorias/18_politicas_nos_mesmos_cortes_ivs.md`.

O script não baixa nada. Ele lê os atos preservados em
`data/raw/aquisicao/normas_ivs/` (baixados em 18/10/2026 do DOU, do Planalto e
da SES-SP) e:

1. grava o manifesto das fontes (URL, data de captura, data de publicação no
   DOU lida da própria página, tamanho e SHA-256) com os trechos de cláusula
   citados no relatório. Cada trecho é localizado no texto preservado por uma
   expressão regular; se não for encontrado, o script para (fail closed);
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

import hashlib
import html as html_lib
import io
import json
import re
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
        "arquivo": "portaria_gm_ms_3493_2024_dou.html",
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
        },
    },
    {
        "id": "portaria_gm_ms_12252_2026",
        "arquivo": "portaria_gm_ms_12252_2026_dou.html",
        "url": DOU + "portaria-gm/ms-n-12.252-de-29-de-setembro-de-2026-735410971",
        "ato": "Portaria GM/MS nº 12.252, de 29/09/2026 (emendas ao SUS em 2027)",
        "trechos": {
            "pu_pap": r"^Parágrafo único\. Os Municípios que apresentarem Indicador de Vulnerabilidade Social - IVS superior a 0,3",
        },
    },
    {
        "id": "portaria_gm_ms_7266_2025",
        "arquivo": "portaria_gm_ms_7266_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-7.266-de-18-de-junho-de-2025-637187199",
        "ato": "Portaria GM/MS nº 7.266, de 18/06/2025 (Programa Agora Tem Especialistas)",
        "trechos": {},
        "ausencia": [r"IVS", r"[Vv]ulnerabilidade [Ss]ocial"],
    },
    {
        "id": "portaria_gm_ms_7177_2025",
        "arquivo": "portaria_gm_ms_7177_2025_dou.html",
        "url": DOU + "portaria-gm/ms-n-7.177-de-10-de-junho-de-2025-635330489",
        "ato": "Portaria GM/MS nº 7.177, de 10/06/2025 (Projeto Mais Médicos Especialistas)",
        "trechos": {},
        "ausencia": [r"IVS", r"[Vv]ulnerabilidade [Ss]ocial"],
    },
    {
        "id": "edital_sgtes_03_2025_retificacao",
        "arquivo": "edital_sgtes_03_2025_retificacao_dou.html",
        "url": DOU + "edital-665051514",
        "ato": "Retificação do Edital SGTES/MS nº 3/2025 (PMM-E, ciclo 1), DOU de 28/10/2025",
        "trechos": {
            "item_11_1_4": r"^11\.1\.4\. Para fins de alocação dos médicos especialistas no âmbito do PMM-E",
        },
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
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while bloco := f.read(1 << 20):
            h.update(bloco)
    return h.hexdigest()


def ler_html(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252")


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
    path = RAW / fonte["arquivo"]
    if not path.exists():
        raise FileNotFoundError(f"fonte preservada ausente: {path.relative_to(ROOT)}")
    reg = {
        "id": fonte["id"],
        "ato": fonte["ato"],
        "url": fonte["url"],
        "caminho": str(path.relative_to(ROOT)),
        "data_captura": DATA_CAPTURA,
        "tamanho_bytes": path.stat().st_size,
        "sha256": sha256(path),
    }
    if path.suffix == ".pdf":
        reg["nota"] = "PDF preservado como cópia secundária; os trechos citados vêm da página do DOU"
        return reg, None
    html = ler_html(path)
    reg.update(metadados_dou(html))
    linhas = texto_planalto(html) if "planalto" in fonte["url"] else texto_linhas(html)
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

    diagnostico = {
        "data_execucao": DATA_CAPTURA,
        "outcomes_abertos": False,
        "natureza_dos_dados": "EMPIRICO",
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
            "descricao": "atos normativos preservados para a auditoria 18 (políticas nos mesmos cortes de IVS)",
            "diretorio": str(RAW.relative_to(ROOT)),
            "fontes": manifesto,
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
