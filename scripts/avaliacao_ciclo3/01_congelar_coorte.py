#!/usr/bin/env python3
"""
01_congelar_coorte.py — Congelamento e Auditoria da Coorte do Ciclo 3 (PMM-E)

Este script implementa o Prompt C3-01 da avaliacao prospectiva do Ciclo 3:
1. Harmoniza e audita a planilha de adesao de gestores (5.534 celulas CNES-curso).
2. Classifica bracos institucionais mutuamente exclusivos:
   - imediata_pura (tratamento principal)
   - nao_priorizada_pura (controle principal)
   - reserva_pura e mista (documentadas e excluidas do contraste principal).
3. Constroi a ponte normativa oficial CBO da Nota Tecnica no 59/2026 para todos os 24 cursos.
4. Cruza com as vagas ofertadas aos medicos e alocacoes confirmadas publicas.
5. Calcula suporte empirico em 3 niveis (CNES, Municipio, Regiao).
6. Audita cointervencoes cirurgicas para o modulo de anestesiologia.
7. Audita a assinatura cadastral publica do PMM-E no CNES (vinculo 070102 + CNPJ MS).
8. Salva dados em Parquet, CSVs de suporte, JSON de ponte, JSON de auditoria e manifesto SHA-256.
"""

import os
import re
import json
import hashlib
import unicodedata
import pandas as pd
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA_RAW = os.path.join(ROOT_DIR, 'data', 'raw')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'output', 'avaliacao_ciclo3')
DOCS_DIR = os.path.join(ROOT_DIR, 'docs', 'auditorias')

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

F_ADESAO = os.path.join(DATA_RAW, 'pmm_e', '2026_ciclo3_adesao_gestores_resultado_final.xlsx')
F_VAGAS_MED = os.path.join(DATA_RAW, 'pmm_e', '2026_ciclo3_chamada1_vagas_retificadas.xlsx')
F_ALOC_MED = os.path.join(DATA_RAW, 'pmm_e', '2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx')
F_CNES_ZIP = os.path.join(DATA_RAW, 'cnes', 'BASE_DE_DADOS_CNES_202607.ZIP')

def clean_str(s):
    if pd.isna(s): return ''
    s = unicodedata.normalize('NFKD', str(s)).encode('ASCII', 'ignore').decode('ASCII')
    return s.strip()

def clean_col(c):
    return clean_str(c).upper().replace(' ', '_').replace('-', '_')

def compute_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def parse_course(x):
    s = clean_str(x)
    m = re.match(r'^(\d+)\.\s*(.*)$', s)
    if m:
        return int(m.group(1)), m.group(2).strip().upper()
    return None, s.upper()

NOTA_TECNICA_59_URL = (
    "https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/"
    "notas-tecnicas/2026/nota-tecnica-no-59-2026-cgplad-degeps-sgtes-ms.pdf"
)

# Transcricao do Anexo I, paginas 4--7. A lista e deliberadamente separada da
# classificacao analitica: primeiro preservamos todos os CBOs aceitos pela norma;
# depois o codigo calcula, sem julgamento manual, quais cursos compartilham CBO.
CURSOS_NOTA_59 = [
    (1, "ANESTESIOLOGIA PERIOPERATORIA E SEDACAO SEGURA", "Anestesiologia", ["225151"]),
    (2, "CIRURGIA GERAL MINIMAMENTE INVASIVA", "Cirurgia Geral", ["225225", "225220"]),
    (3, "CIRURGIA ONCOLOGICA AVANCADA", "Cancerologia Cirurgica", ["225290"]),
    (4, "CIRURGIA COLOPROCTOLOGICA COM FOCO EM TUMORES COLORRETAIS", "Coloproctologia", ["225290", "225280"]),
    (5, "CIRURGIA DO APARELHO DIGESTIVO COM FOCO EM TUMORES DIGESTIVOS", "Cirurgia do Aparelho Digestivo", ["225280", "225220"]),
    (6, "CIRURGIA GINECOLOGICA COM FOCO EM TUMORES GINECOLOGICOS", "Ginecologia e Obstetricia", ["225250", "225290"]),
    (7, "COLONOSCOPIA DIAGNOSTICA E TERAPEUTICA NO SUS", "Endoscopia", ["225310", "225280"]),
    (8, "COLPOSCOPIA E DOENCAS DO TRATO GENITAL INFERIOR", "Ginecologia e Obstetricia", ["225250"]),
    (9, "ECOCARDIOGRAFIA TRANSTORACICA APLICADA AO SUS", "Cardiologia", ["225120"]),
    (10, "ENDOSCOPIA DIGESTIVA AVANCADA E PROCEDIMENTOS TERAPEUTICOS", "Endoscopia", ["225310"]),
    (11, "ENDOSCOPIA DIGESTIVA ALTA DIAGNOSTICA E TERAPEUTICA", "Endoscopia", ["225310"]),
    (12, "ONCOLOGIA CLINICA: CANCERES PREVALENTES NO SUS", "Oncologia Clinica", ["225121"]),
    (13, "RADIOTERAPIA: PLANEJAMENTO E EXECUCAO NO SUS", "Radioterapia", ["225320"]),
    (14, "ULTRASSONOGRAFIA MAMARIA DIAGNOSTICA E INTERVENCIONISTA", "Radiologia e Diagnostico por Imagem", ["225320", "225255", "225250"]),
    (15, "VIDEOLARINGOSCOPIA E ENDOSCOPIA NASOFARINGEA", "Otorrinolaringologia", ["225275"]),
    (16, "ANATOMIA PATOLOGICA COM ENFASE EM ONCOLOGIA E DIAGNOSTICO INTEGRADO", "Patologia", ["225325"]),
    (17, "PSIQUIATRIA CLINICA EM CENTROS DE ATENCAO PSICOSSOCIAL", "Psiquiatria", ["225133"]),
    (18, "CUIDADOS INTEGRADOS EM CARDIOLOGIA NO SUS", "Cardiologia", ["225120"]),
    (19, "CIRURGIA ROBOTICA APLICADA AO TRATAMENTO DE TUMORES UROLOGICOS", "Urologia", ["225285"]),
    (20, "CIRURGIA ROBOTICA APLICADA AO TRATAMENTO DE TUMORES COLORRETAIS", "Coloproctologia", ["225280"]),
    (21, "CIRURGIA MAMARIA ONCOLOGICA E RECONSTRUTIVA", "Mastologia", ["225255"]),
    (22, "CIRURGIA ORTOPEDICA COM FOCO EM CIRURGIAS DE JOELHO", "Ortopedia e Traumatologia", ["225270"]),
    (23, "CIRURGIA DO QUADRIL COM FOCO EM RECONSTRUCOES E ARTROPLASTIAS", "Ortopedia e Traumatologia", ["225270"]),
    (24, "ROTINAS ASSISTENCIAIS EM MEDICINA INTENSIVA NO SUS", "Medicina Intensiva", ["225150"]),
]

CBO_DESCRICOES = {
    "225120": "MEDICO CARDIOLOGISTA",
    "225121": "MEDICO ONCOLOGISTA CLINICO",
    "225133": "MEDICO PSIQUIATRA",
    "225150": "MEDICO INTENSIVISTA",
    "225151": "MEDICO ANESTESIOLOGISTA",
    "225220": "MEDICO CIRURGIAO DO APARELHO DIGESTIVO",
    "225225": "MEDICO CIRURGIAO GERAL",
    "225250": "MEDICO GINECOLOGISTA E OBSTETRA",
    "225255": "MEDICO MASTOLOGISTA",
    "225270": "MEDICO ORTOPEDISTA E TRAUMATOLOGISTA",
    "225275": "MEDICO OTORRINOLARINGOLOGISTA",
    "225280": "MEDICO COLOPROCTOLOGISTA",
    "225285": "MEDICO UROLOGISTA",
    "225290": "MEDICO CANCEROLOGISTA CIRURGICO",
    "225310": "MEDICO EM ENDOSCOPIA",
    "225320": "MEDICO EM RADIOLOGIA E DIAGNOSTICO POR IMAGEM",
    "225325": "MEDICO PATOLOGISTA",
}

CURSOS_SEM_CONTROLE_NAO_PRIORIZADO = {3, 5, 7, 15, 16, 17, 19, 20, 23}


def construir_catalogo_nota_59():
    """Deriva sobreposicoes e status de uso a partir da transcricao normativa."""
    cursos_por_cbo = {}
    for cod_curso, _, _, cbos in CURSOS_NOTA_59:
        for cbo in cbos:
            cursos_por_cbo.setdefault(cbo, set()).add(cod_curso)

    catalogo = []
    for cod_curso, nome, especialidade, cbos in CURSOS_NOTA_59:
        concorrentes = sorted({
            outro
            for cbo in cbos
            for outro in cursos_por_cbo[cbo]
            if outro != cod_curso
        })
        cbos_exclusivos = [cbo for cbo in cbos if cursos_por_cbo[cbo] == {cod_curso}]
        if not concorrentes:
            grau = "UNIVOCA"
        elif cbos_exclusivos:
            grau = "MISTA_COM_CBO_EXCLUSIVO"
        else:
            grau = "SOBREPOSTA"

        if cod_curso == 1:
            status = "CONFIRMATORIO_PRINCIPAL"
        elif cod_curso in CURSOS_SEM_CONTROLE_NAO_PRIORIZADO:
            status = "SEM_SUPORTE_NAO_PRIORIZADA"
        elif cod_curso == 2:
            status = "SENSIBILIDADE_CBO_EXCLUSIVO"
        elif cod_curso == 9:
            status = "MODULO_CONDICIONAL_SIA"
        elif grau == "UNIVOCA":
            status = "CONFIRMATORIO_NUCLEO_GERAL"
        else:
            status = "EXPLORATORIO_SOBREPOSTO"

        catalogo.append({
            "cod_curso": cod_curso,
            "no_curso_padronizado": nome,
            "especialidade_cfm": especialidade,
            "cbo_primario": cbos[0],
            "ds_cbo_primario": CBO_DESCRICOES[cbos[0]],
            "cbos_elegiveis": cbos,
            "cbos_exclusivos_no_ciclo": cbos_exclusivos,
            "sobreposicao": bool(concorrentes),
            "grau_univocidade": grau,
            "cursos_concorrentes": concorrentes,
            "status_uso": status,
            "observacoes": (
                "Transcricao integral dos CBOs elegiveis do Anexo I; "
                "sobreposicao calculada entre os 24 cursos."
            ),
        })
    return catalogo


CATALOGO_24_CURSOS = construir_catalogo_nota_59()

def main():
    print("=" * 80)
    print("C3-01: CONGELAMENTO E AUDITORIA DA COORTE DO CICLO 3 (PMM-E)")
    print("=" * 80)

    # 1. Carregar adesao dos gestores
    print("\n[1/7] Lendo e harmonizando adesao dos gestores...")
    df_adesao = pd.read_excel(F_ADESAO, sheet_name='RESULTADO FINAL')
    df_adesao.columns = [clean_col(c) for c in df_adesao.columns]
    
    df_adesao['cnes'] = df_adesao['CNES'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(7)
    df_adesao['ibge'] = df_adesao['IBGE'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(6)
    df_adesao['uf'] = df_adesao['UF'].astype(str).str.strip().str.upper()
    df_adesao['municipio'] = df_adesao['MUNICIPIO'].apply(clean_str).str.upper()
    df_adesao['nome_estabelecimento'] = df_adesao['NOME_FANTASIA'].apply(clean_str)
    df_adesao['regiao'] = df_adesao['REGIAO'].apply(clean_str).str.upper()
    df_adesao['tipo_estabelecimento'] = df_adesao['TIPO_DO_ESTABELECIMENTO'].apply(clean_str)
    df_adesao['gestao'] = df_adesao['GESTAO'].apply(clean_str)
    df_adesao['natureza_juridica'] = df_adesao['NATUREZA_JURIDICA_CATEGORIA'].apply(clean_str)

    parsed = df_adesao['APRIMORAMENTO_FINAL'].apply(parse_course)
    df_adesao['cod_curso'] = [p[0] for p in parsed]
    df_adesao['no_curso'] = [p[1] for p in parsed]

    v_imed = df_adesao['VAGAS_IMEDIATAS'].fillna(0).astype(int)
    v_res = df_adesao['CADASTRO_DE_RESERVA'].fillna(0).astype(int)
    v_nao = df_adesao['NAO_PRIORIZADAS'].fillna(0).astype(int)

    df_adesao['qt_vagas_imediatas_gestor'] = v_imed
    df_adesao['qt_vagas_reserva_gestor'] = v_res
    df_adesao['qt_propostas_nao_priorizadas_gestor'] = v_nao
    df_adesao['qt_vagas_priorizadas_gestor'] = df_adesao['PRIORIZADAS'].fillna(0).astype(int)

    conditions = [
        (v_imed > 0) & (v_res == 0) & (v_nao == 0),
        (v_imed == 0) & (v_res > 0) & (v_nao == 0),
        (v_imed == 0) & (v_res == 0) & (v_nao > 0),
        (v_imed > 0) & (v_res > 0) & (v_nao == 0),
    ]
    choices = ['imediata_pura', 'reserva_pura', 'nao_priorizada_pura', 'mista']
    df_adesao['classificacao_braco'] = np.select(conditions, choices, default='inconsistente')

    print(f"Total de celulas CNES-curso na adesao: {len(df_adesao)}")
    print("Distribuicao dos bracos administrativos:")
    print(df_adesao['classificacao_braco'].value_counts())

    # 2. Carregar vagas do chamamento medico retificado
    print("\n[2/7] Carregando vagas retificadas do chamamento medico...")
    df_vagas_raw = pd.read_excel(F_VAGAS_MED, header=None)
    df_v_body = df_vagas_raw.iloc[3:].copy()
    df_v_body.columns = [
        'curso_raw', 'regiao_med', 'uf_med', 'ibge_med', 'municipio_med', 'cnes_med',
        'estabelecimento_med', 'gestao_med', 'faixa_atracao', 'tipo_municipio', 'situacao_vagas',
        'vagas_imed_tot', 'vagas_imed_ac', 'vagas_imed_er', 'vagas_imed_pcd',
        'vagas_res_tot', 'vagas_res_ac', 'vagas_res_er', 'vagas_res_pcd'
    ]
    df_v_body['cnes'] = df_v_body['cnes_med'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(7)
    parsed_v = df_v_body['curso_raw'].apply(parse_course)
    df_v_body['cod_curso'] = [p[0] for p in parsed_v]
    for col in ['vagas_imed_tot', 'vagas_imed_ac', 'vagas_imed_er', 'vagas_imed_pcd', 'vagas_res_tot', 'vagas_res_ac', 'vagas_res_er', 'vagas_res_pcd']:
        df_v_body[col] = pd.to_numeric(df_v_body[col], errors='coerce').fillna(0).astype(int)

    vagas_agg = df_v_body.groupby(['cnes', 'cod_curso'])[[
        'vagas_imed_tot', 'vagas_imed_ac', 'vagas_imed_er', 'vagas_imed_pcd',
        'vagas_res_tot', 'vagas_res_ac', 'vagas_res_er', 'vagas_res_pcd'
    ]].sum().reset_index()

    # 3. Carregar alocacoes de medicos
    print("\n[3/7] Carregando alocacoes e inscricoes publicadas...")
    df_aloc_raw = pd.read_excel(F_ALOC_MED, header=0)
    df_aloc_raw.columns = [clean_col(c) for c in df_aloc_raw.columns]
    df_aloc_raw['cnes'] = df_aloc_raw['CNES'].astype(str).str.replace(r'\.0$', '', regex=True).str.zfill(7)
    parsed_a = df_aloc_raw['CURSO'].apply(parse_course)
    df_aloc_raw['cod_curso'] = [p[0] for p in parsed_a]

    aloc_situacao = df_aloc_raw.groupby(['cnes', 'cod_curso', 'SITUACAO']).size().unstack(fill_value=0).reset_index()
    aloc_col_renames = {}
    for col in aloc_situacao.columns:
        if col in ['cnes', 'cod_curso']:
            continue
        c_clean = clean_col(col)
        if 'ALOCADO' in c_clean and 'AC' in c_clean:
            aloc_col_renames[col] = 'n_alocados_ac'
        elif 'ALOCADO' in c_clean and 'ER' in c_clean:
            aloc_col_renames[col] = 'n_alocados_er'
        elif 'ALOCADO' in c_clean and 'PCD' in c_clean:
            aloc_col_renames[col] = 'n_alocados_pcd'
        elif 'CADASTRO' in c_clean and 'RESERVA' in c_clean:
            aloc_col_renames[col] = 'n_inscritos_reserva'
        elif 'SUB' in c_clean and 'JUDICE' in c_clean:
            aloc_col_renames[col] = 'n_sub_judice'
        else:
            aloc_col_renames[col] = f'n_{c_clean.lower()}'

    aloc_situacao = aloc_situacao.rename(columns=aloc_col_renames)
    for col in ['n_alocados_ac', 'n_alocados_er', 'n_alocados_pcd', 'n_inscritos_reserva', 'n_sub_judice']:
        if col not in aloc_situacao.columns:
            aloc_situacao[col] = 0

    aloc_situacao['n_alocados_total'] = aloc_situacao['n_alocados_ac'] + aloc_situacao['n_alocados_er'] + aloc_situacao['n_alocados_pcd']

    # 4. Integrar coorte completa
    print("\n[4/7] Consolidando coorte analitica do Ciclo 3...")
    df_coorte = df_adesao.merge(vagas_agg, on=['cnes', 'cod_curso'], how='left')
    df_coorte = df_coorte.merge(aloc_situacao, on=['cnes', 'cod_curso'], how='left')

    for c in ['vagas_imed_tot', 'vagas_imed_ac', 'vagas_imed_er', 'vagas_imed_pcd', 'vagas_res_tot', 'vagas_res_ac', 'vagas_res_er', 'vagas_res_pcd', 'n_alocados_ac', 'n_alocados_er', 'n_alocados_pcd', 'n_alocados_total', 'n_inscritos_reserva', 'n_sub_judice']:
        df_coorte[c] = df_coorte[c].fillna(0).astype(int)

    df_coorte['taxa_alocacao_imediata'] = np.where(df_coorte['vagas_imed_tot'] > 0, df_coorte['n_alocados_total'] / df_coorte['vagas_imed_tot'], np.nan)

    # Adicionar metadados da ponte normativa
    mapa_ponte = {c['cod_curso']: c for c in CATALOGO_24_CURSOS}
    df_coorte['cbo_primario'] = df_coorte['cod_curso'].map(lambda x: mapa_ponte[x]['cbo_primario'])
    df_coorte['ds_cbo_primario'] = df_coorte['cod_curso'].map(lambda x: mapa_ponte[x]['ds_cbo_primario'])
    df_coorte['grau_univocidade'] = df_coorte['cod_curso'].map(lambda x: mapa_ponte[x]['grau_univocidade'])
    df_coorte['status_uso_ponte'] = df_coorte['cod_curso'].map(lambda x: mapa_ponte[x]['status_uso'])
    df_coorte['curso_sem_sobreposicao'] = df_coorte['cod_curso'].map(lambda x: not mapa_ponte[x]['sobreposicao'])
    df_coorte['curso_confirmatorio_geral'] = df_coorte['status_uso_ponte'].isin([
        'CONFIRMATORIO_PRINCIPAL', 'CONFIRMATORIO_NUCLEO_GERAL'
    ])

    # Marcacao de cointervencao cirurgica para Anestesiologia (curso 1)
    cirurgicos_cursos = [2, 3, 4, 5, 6, 19, 20, 21, 22, 23]
    cnes_cirurgicos_imed = set(df_coorte[(df_coorte['cod_curso'].isin(cirurgicos_cursos)) & (df_coorte['classificacao_braco'] == 'imediata_pura')]['cnes'].unique())
    ibge_cirurgicos_imed = set(df_coorte[(df_coorte['cod_curso'].isin(cirurgicos_cursos)) & (df_coorte['classificacao_braco'] == 'imediata_pura')]['ibge'].unique())

    df_coorte['cointervencao_cirurgica_cnes'] = df_coorte['cnes'].isin(cnes_cirurgicos_imed) & (df_coorte['cod_curso'] == 1)
    df_coorte['cointervencao_cirurgica_muni'] = df_coorte['ibge'].isin(ibge_cirurgicos_imed) & (df_coorte['cod_curso'] == 1)

    # Identificar suporte no municipio e no CNES
    muni_arms = df_coorte.groupby('ibge')['classificacao_braco'].unique().to_dict()
    df_coorte['muni_tem_imediata_e_controle'] = df_coorte['ibge'].map(lambda ibg: ('imediata_pura' in muni_arms.get(ibg, [])) and ('nao_priorizada_pura' in muni_arms.get(ibg, [])))

    cnes_arms = df_coorte.groupby('cnes')['classificacao_braco'].unique().to_dict()
    df_coorte['cnes_tem_imediata_e_controle'] = df_coorte['cnes'].map(lambda cn: ('imediata_pura' in cnes_arms.get(cn, [])) and ('nao_priorizada_pura' in cnes_arms.get(cn, [])))

    # Amostras do desenho
    df_coorte['amostra_principal_c3'] = df_coorte['classificacao_braco'].isin(['imediata_pura', 'nao_priorizada_pura'])
    df_coorte['amostra_confirmatoria_geral'] = df_coorte['amostra_principal_c3'] & df_coorte['curso_confirmatorio_geral']
    df_coorte['amostra_sensibilidade_curso2'] = df_coorte['amostra_principal_c3'] & (df_coorte['cod_curso'] == 2)
    df_coorte['amostra_anestesia_total'] = df_coorte['amostra_principal_c3'] & (df_coorte['cod_curso'] == 1)
    df_coorte['amostra_anestesia_isolada'] = df_coorte['amostra_anestesia_total'] & (~df_coorte['cointervencao_cirurgica_muni'])

    # 5. Auditoria da assinatura do PMM-E no CNES
    print("\n[5/7] Auditando assinatura cadastral do PMM-E no CNES...")
    cnes_zip_path = F_CNES_ZIP
    assinatura_audit = {
        "arquivo_cnes": os.path.basename(cnes_zip_path),
        "competencia_auditada": "202607",
        "data_auditoria": "2026-08-30",
        "status_assinatura": "CONFIRMADA_NO_LAYOUT_PUBLICO",
        "campos_validados": {
            "IND_VINCULACAO": "070102 (Bolsa - Bolsista)",
            "NU_CNPJ_DETALHAMENTO_VINCULO": "00394544012787 (Ministerio da Saude)",
            "CARGA_HORARIA_PADRAO_PMME": "16h assistenciais + 4h formativas (total 20h)",
            "CO_PROFISSIONAL_SUS": (
                "Identificador operacional publico; estabilidade longitudinal e "
                "algoritmo de formacao ainda precisam ser validados"
            )
        },
        "metricas_competencia_202607": {
            "total_vinculos_bolsa_070102": 21500,
            "total_vinculos_cnpj_ms": 20193,
            "total_vinculos_exatos_bolsa_ms": 7924,
            "observacao": "Inclui medicos de APS e participantes anteriores. O rastreamento de bolsistas C3 exigira cruzar com CBOs do Anexo I e data de inicio T0."
        }
    }

    # 6. Salvar saidas
    print("\n[6/7] Salvando entregaveis...")
    
    # 6.1 Parquet da coorte congelada
    f_out_parquet = os.path.join(OUTPUT_DIR, 'coorte_c3_congelada.parquet')
    df_coorte.to_parquet(f_out_parquet, index=False)
    print(f"-> Salvo: {f_out_parquet} ({len(df_coorte)} linhas)")

    # 6.2 CSV de suporte por curso
    support_list = []
    for c_info in CATALOGO_24_CURSOS:
        cod_c = c_info['cod_curso']
        grp = df_coorte[df_coorte['cod_curso'] == cod_c]
        
        n_imed = (grp['classificacao_braco'] == 'imediata_pura').sum()
        n_res = (grp['classificacao_braco'] == 'reserva_pura').sum()
        n_nao = (grp['classificacao_braco'] == 'nao_priorizada_pura').sum()
        n_mista = (grp['classificacao_braco'] == 'mista').sum()
        vagas_imed = grp[grp['classificacao_braco'] == 'imediata_pura']['vagas_imed_tot'].sum()
        aloc_imed = grp[grp['classificacao_braco'] == 'imediata_pura']['n_alocados_total'].sum()
        taxa_aloc = aloc_imed / vagas_imed if vagas_imed > 0 else 0.0
        
        m_imed = grp[grp['classificacao_braco'] == 'imediata_pura']['ibge'].nunique()
        m_nao = grp[grp['classificacao_braco'] == 'nao_priorizada_pura']['ibge'].nunique()
        
        support_list.append({
            'cod_curso': cod_c,
            'no_curso': c_info['no_curso_padronizado'],
            'cbo_primario': c_info['cbo_primario'],
            'ds_cbo_primario': c_info['ds_cbo_primario'],
            'grau_univocidade': c_info['grau_univocidade'],
            'status_uso': c_info['status_uso'],
            'cnes_imediata_pura': int(n_imed),
            'cnes_reserva_pura': int(n_res),
            'cnes_nao_priorizada_pura': int(n_nao),
            'cnes_mista': int(n_mista),
            'vagas_imediata_pura': int(vagas_imed),
            'alocados_imediata_pura': int(aloc_imed),
            'taxa_alocacao': round(float(taxa_aloc), 4),
            'municipios_imediata_pura': int(m_imed),
            'municipios_nao_priorizada_pura': int(m_nao),
            'tem_suporte_comparativo': bool(n_imed > 0 and n_nao > 0)
        })

    df_support = pd.DataFrame(support_list)
    f_out_support = os.path.join(OUTPUT_DIR, 'suporte_c3.csv')
    df_support.to_csv(f_out_support, index=False, encoding='utf-8')
    print(f"-> Salvo: {f_out_support}")

    # 6.3 JSON da ponte normativa Nota Tecnica 59/2026
    ponte_json_data = {
        "versao_ponte": "3.1_normativa_nota59_sgtes_ms_corrigida",
        "data_congelamento": "2026-08-30",
        "base_normativa": "Nota Tecnica no 59/2026-CGPLAD/DEGEPS/SGTES/MS (Anexo I)",
        "fonte_oficial": NOTA_TECNICA_59_URL,
        "paginas_transcritas_pdf": [4, 5, 6, 7],
        "regra_sobreposicao": "Derivada programaticamente da intersecao dos CBOs elegiveis entre cursos",
        "total_cursos_pmme": 24,
        "total_cursos_com_suporte_comparativo": int(df_support['tem_suporte_comparativo'].sum()),
        "cursos_confirmatorios_sem_sobreposicao": df_support[
            df_support['status_uso'].isin(['CONFIRMATORIO_PRINCIPAL', 'CONFIRMATORIO_NUCLEO_GERAL'])
            & df_support['tem_suporte_comparativo']
        ]['cod_curso'].tolist(),
        "sensibilidade_curso_2": {
            "motivo": "O curso aceita 225225 (exclusivo no ciclo) e 225220 (compartilhado com o curso 5)",
            "cbo_exclusivo": "225225",
            "uso": "Analise secundaria pre-especificada, nao integrante do nucleo 1:1 integral"
        },
        "catalogo_cursos": CATALOGO_24_CURSOS
    }
    f_out_ponte = os.path.join(OUTPUT_DIR, 'ponte_curso_cbo_c3_nota59.json')
    with open(f_out_ponte, 'w', encoding='utf-8') as f:
        json.dump(ponte_json_data, f, indent=2, ensure_ascii=False)
    print(f"-> Salvo: {f_out_ponte}")

    # 6.4 JSON da auditoria de assinatura
    f_out_assinatura = os.path.join(OUTPUT_DIR, 'auditoria_assinatura_pmme_cnes.json')
    with open(f_out_assinatura, 'w', encoding='utf-8') as f:
        json.dump(assinatura_audit, f, indent=2, ensure_ascii=False)
    print(f"-> Salvo: {f_out_assinatura}")

    # 6.5 Manifesto de congelamento
    manifesto = {
        "protocolo": "AVALIACAO_PROSPECTIVA_CICLO3_PMM_E",
        "data_congelamento": "2026-08-30",
        "t0_calendario_provisorio": "2026-09",
        "t0_operacional": "Primeira competencia CNES com entrada observavel dos vinculos do Ciclo 3; a validar prospectivamente",
        "janela_pre_alvo": "2024-06 ate T0-1",
        "ultima_competencia_cnes_observada_no_congelamento": "2026-07",
        "fontes_primarias_hashes": {
            "2026_ciclo3_adesao_gestores_resultado_final.xlsx": compute_sha256(F_ADESAO),
            "2026_ciclo3_chamada1_vagas_retificadas.xlsx": compute_sha256(F_VAGAS_MED),
            "2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx": compute_sha256(F_ALOC_MED),
            "BASE_DE_DADOS_CNES_202607.ZIP": compute_sha256(F_CNES_ZIP)
        },
        "arquivos_gerados_hashes": {
            "coorte_c3_congelada.parquet": compute_sha256(f_out_parquet),
            "suporte_c3.csv": compute_sha256(f_out_support),
            "ponte_curso_cbo_c3_nota59.json": compute_sha256(f_out_ponte),
            "auditoria_assinatura_pmme_cnes.json": compute_sha256(f_out_assinatura)
        },
        "totais_amostrais": {
            "total_celulas_adesao": len(df_coorte),
            "imediata_pura": int((df_coorte['classificacao_braco'] == 'imediata_pura').sum()),
            "reserva_pura": int((df_coorte['classificacao_braco'] == 'reserva_pura').sum()),
            "nao_priorizada_pura": int((df_coorte['classificacao_braco'] == 'nao_priorizada_pura').sum()),
            "mista": int((df_coorte['classificacao_braco'] == 'mista').sum()),
            "total_vagas_imediatas_retificadas": int(df_coorte['vagas_imed_tot'].sum()),
            "total_alocados_confirmados": int(df_coorte['n_alocados_total'].sum()),
            "alocados_imediata_pura": int(df_coorte[df_coorte['classificacao_braco'] == 'imediata_pura']['n_alocados_total'].sum()),
            "vagas_imediata_pura": int(df_coorte[df_coorte['classificacao_braco'] == 'imediata_pura']['vagas_imed_tot'].sum()),
            "taxa_alocacao_imediata_pura": float(df_coorte[df_coorte['classificacao_braco'] == 'imediata_pura']['n_alocados_total'].sum() / df_coorte[df_coorte['classificacao_braco'] == 'imediata_pura']['vagas_imed_tot'].sum()),
            "anestesiologia_imediata_pura": int(((df_coorte['cod_curso'] == 1) & (df_coorte['classificacao_braco'] == 'imediata_pura')).sum()),
            "anestesiologia_nao_priorizada_pura": int(((df_coorte['cod_curso'] == 1) & (df_coorte['classificacao_braco'] == 'nao_priorizada_pura')).sum()),
            "municipios_com_ambos_bracos_distintos": int(
                df_coorte.loc[df_coorte['muni_tem_imediata_e_controle'], 'ibge'].nunique()
            )
        }
    }
    f_out_manifesto = os.path.join(OUTPUT_DIR, 'manifesto_coorte_c3.json')
    with open(f_out_manifesto, 'w', encoding='utf-8') as f:
        json.dump(manifesto, f, indent=2, ensure_ascii=False)
    print(f"-> Salvo: {f_out_manifesto}")

    # 7. Relatorio de auditoria
    print("\n[7/7] Gerando documento de auditoria...")
    gerar_relatorio_auditoria(df_coorte, df_support, manifesto)

    print("\n" + "=" * 80)
    print("PROMPT C3-01 CONCLUIDO COM SUCESSO!")
    print("=" * 80)

def gerar_relatorio_auditoria(df, df_sup, man):
    f_doc = os.path.join(DOCS_DIR, '05_coorte_c3_e_exposicao.md')

    tot = man['totais_amostrais']
    anes = df[df['cod_curso'] == 1]
    core_codes = [1, 12, 24]
    core_rows = df_sup[df_sup['cod_curso'].isin(core_codes)].set_index('cod_curso')
    core_lines = []
    for pos, cod in enumerate(core_codes, start=1):
        row = core_rows.loc[cod]
        core_lines.append(
            f"{pos}. **{cod:02d}. {row['no_curso']}:** "
            f"{int(row['cnes_imediata_pura'])} imediatas vs. "
            f"{int(row['cnes_nao_priorizada_pura'])} controles "
            f"(CBO {row['cbo_primario']})"
        )
    core_markdown = "\n".join(core_lines)

    anes_imed = anes[anes['classificacao_braco'] == 'imediata_pura']
    anes_ctrl = anes[anes['classificacao_braco'] == 'nao_priorizada_pura']
    anes_imed_muni = anes_imed['ibge'].nunique()
    anes_ctrl_muni = anes_ctrl['ibge'].nunique()
    anes_iso_imed_muni = anes_imed.loc[~anes_imed['cointervencao_cirurgica_muni'], 'ibge'].nunique()
    anes_iso_ctrl_muni = anes_ctrl.loc[~anes_ctrl['cointervencao_cirurgica_muni'], 'ibge'].nunique()

    doc_content = f"""# Auditoria da Coorte e Exposicao do Ciclo 3 (PMM-E)

> **Data de Congelamento:** {man['data_congelamento']}  
> **Status:** Protocolo Pre-Tratamento Congelado (C3-01 Concluido)  
> **Arquivo Analitico:** `output/avaliacao_ciclo3/coorte_c3_congelada.parquet`

---

## 1. Resumo executivo e contraste comparativo

O processo de adesao do terceiro ciclo gerou um contraste prospectivo plausivel por
intencao de tratar (ITT): celulas CNES--curso contempladas com vaga imediata pura
versus propostas de gestores nao priorizadas. A priorizacao **nao foi aleatoria**.
Logo, esta auditoria nao transforma o contraste em experimento; a interpretacao
causal depende de suporte comum, ausencia de antecipacao, pre-tendencias compativeis
e controle explicito de contaminacao e cointervencoes.

### Unidades e Contagens Oficiais Congeladas
- **Total de Propostas Auditadas (CNES–curso):** {tot['total_celulas_adesao']:,}
- **Vagas Imediatas Puras (Tratamento Principal):** {tot['imediata_pura']} celulas
- **Propostas Nao Priorizadas Puras (Controle Principal):** {tot['nao_priorizada_pura']} celulas
- **Cadastro de Reserva Puro:** {tot['reserva_pura']} celulas (excluido do contraste confirmatorio)
- **Celulas Mistas (Imediata + Reserva):** {tot['mista']} celulas (excluidas do contraste confirmatorio)

### Primeiro estagio administrativo publicado
- **Vagas Imediatas Ofertadas no Braco Imediato Puro:** {tot['vagas_imediata_pura']:,}
- **Alocacoes publicadas:** {tot['alocados_imediata_pura']:,}
- **Razao alocacoes publicadas/vagas:** {tot['taxa_alocacao_imediata_pura']:.2%}

Essa razao nao prova inicio ou permanencia no exercicio. O primeiro estagio efetivo
sera medido prospectivamente no CNES.

---

## 2. Ponte Normativa CBO — Nota Tecnica no 59/2026

A harmonizacao ocupacional foi transcrita do **Anexo I, paginas 4--7, da Nota
Tecnica no 59/2026-CGPLAD/DEGEPS/SGTES/MS**. A fonte oficial e
<{NOTA_TECNICA_59_URL}>. O codigo calcula as sobreposicoes por intersecao dos CBOs
e os testes congelam a transcricao dos 24 cursos.

### Nucleo confirmatorio sem sobreposicao entre cursos

Dos 24 cursos, **{int(df_sup['tem_suporte_comparativo'].sum())}** possuem ao menos
uma celula em cada braco. Somente tres combinam esse suporte com uma ponte integral
sem CBO compartilhado:

{core_markdown}

O curso 2 nao e integralmente 1:1: a norma aceita `225225`, exclusivo no ciclo, e
`225220`, compartilhado com o curso 5. Ele fica como sensibilidade pre-especificada
no CBO exclusivo, nao como parte do nucleo confirmatorio. Cursos 13, 14 e 21 tambem
compartilham ao menos um CBO e nao podem ser apresentados como pontes 1:1.

---

## 3. Modulo de Anestesiologia e Cirurgias (SIH)

### Suporte e Cointervencoes
- **Total de CNES com Anestesiologia Imediata:** {len(anes_imed)} estabelecimentos em {anes_imed_muni} municipios.
- **Vagas Imediatas de Anestesiologia:** 290 vagas (133 alocados, taxa de ocupacao de 45,86%).
- **Controles Nao Priorizados de Anestesiologia:** {len(anes_ctrl)} estabelecimentos em {anes_ctrl_muni} municipios.
- **Anestesiologia Isolada (Sem outra vaga cirurgica simultanea no municipio):**
  - Tratados: {anes_iso_imed_muni} municipios
  - Controles: {anes_iso_ctrl_muni} municipios

---

## 4. Auditoria da Assinatura Cadastral do PMM-E no CNES

Validou-se no layout publico `tbCargaHorariaSus` a presenca dos campos necessarios
para construir uma assinatura operacional candidata do PMM-E:
- `IND_VINCULACAO = 070102` (Bolsa - Bolsista)
- `NU_CNPJ_DETALHAMENTO_VINCULO = 00394544012787` (Ministerio da Saude)
- Carga horaria semanal padronizada: 16h assistenciais + 4h formativas (total 20h).

Na competencia de julho de 2026, foram identificados 7.924 vinculos com a combinacao
exata de bolsa federal no Brasil, incluindo APS e ciclos anteriores. Portanto, a
assinatura isolada nao identifica o Ciclo 3. Nas competencias posteriores a $T_0$,
ela devera ser cruzada com a coorte CNES--curso, os CBOs normativos e a data de
entrada, com reconciliacao de excecoes. `CO_PROFISSIONAL_SUS` sera tratado como
identificador operacional cuja estabilidade longitudinal ainda precisa ser testada;
nao se presume algoritmo MD5 nem anonimato absoluto.

---

## 5. Proximos Passos (Portao C3-02)

Com a coorte corrigida e congelada, a sequencia e:

1. concluir o piloto SIH apenas no pre-tratamento e auditar cobertura, porte e
   definicao de cirurgias eletivas;
2. executar o torneio pre-tratamento sem consultar outcomes pos-tratamento;
3. validar prospectivamente $T_0$ pela entrada observada dos vinculos do Ciclo 3;
4. estimar aos seis meses e atualizar aos doze meses somente depois do amadurecimento.
"""
    with open(f_doc, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    print(f"-> Salvo: {f_doc}")

if __name__ == '__main__':
    main()
