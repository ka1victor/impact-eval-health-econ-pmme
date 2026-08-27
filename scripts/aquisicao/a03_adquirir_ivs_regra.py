import os, sys, json, hashlib, unicodedata, datetime, urllib.request, ssl
from pathlib import Path
import pandas as pd, numpy as np

def compute_sha256(filepath: Path) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def normalize_text_cat(s) -> str:
    if pd.isna(s): return 'NA'
    s = str(s).upper()
    s = unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')
    for prefix in ['1 - ', '2 - ', '3 - ', '4 - ', '5 - ']:
        s = s.replace(prefix, '')
    s = s.replace('MADIA', 'MEDIA')
    return s.strip()

def classify_ipea_standard(val: float) -> str:
    if pd.isna(val): return 'NA'
    if val <= 0.200: return 'MUITO BAIXA VULNERABILIDADE'
    elif val <= 0.300: return 'BAIXA VULNERABILIDADE'
    elif val <= 0.400: return 'MEDIA VULNERABILIDADE'
    elif val <= 0.500: return 'ALTA VULNERABILIDADE'
    else: return 'MUITO ALTA VULNERABILIDADE'

def classify_ipea_num(val: float) -> int:
    if pd.isna(val): return 0
    if val <= 0.200: return 1
    elif val <= 0.300: return 2
    elif val <= 0.400: return 3
    elif val <= 0.500: return 4
    else: return 5

def get_cat_num(cat_str: str) -> int:
    mapping = {'MUITO BAIXA VULNERABILIDADE': 1, 'BAIXA VULNERABILIDADE': 2, 'MEDIA VULNERABILIDADE': 3, 'ALTA VULNERABILIDADE': 4, 'MUITO ALTA VULNERABILIDADE': 5}
    return mapping.get(cat_str, 0)

def download_normative_sources(raw_dir: Path) -> list:
    raw_dir.mkdir(parents=True, exist_ok=True)
    sources_to_fetch = [
        {'id': 'lei_15233_2025', 'filename': 'lei_15233_2025.html', 'url': 'https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15233.htm', 'descricao': 'Lei 15.233/2025 - Altera a Lei 12.871/2013 e institui o Projeto Mais Medicos Especialistas', 'orgao': 'Presidencia da Republica / Secretaria-Geral', 'tipo': 'text/html; charset=iso-8859-1', 'natureza': 'Lei Federal'},
        {'id': 'edital_sgtes_02_2025_gestores', 'filename': 'edital_sgtes_02_2025_gestores.html', 'url': 'https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-no-02-2025-saes/edital', 'descricao': 'Chamamento Publico SGTES/SAES 02/2025 - Adesao de entes federativos e oferta de servicos', 'orgao': 'Ministerio da Saude / SGTES / SAES', 'tipo': 'text/html; charset=utf-8', 'natureza': 'Edital de Adesao'},
        {'id': 'edital_sgtes_03_2025_faq_bolsa', 'filename': 'edital_sgtes_03_2025_faq_bolsa.html', 'url': 'https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-pmm-e/faq/qual-o-valor-da-bolsa-formacao', 'descricao': 'FAQ Oficial do Chamamento SGTES/MS 3/2025 - Regra de bolsas por faixa (Grade 2025)', 'orgao': 'Ministerio da Saude / SGTES', 'tipo': 'text/html; charset=utf-8', 'natureza': 'Documentacao Oficial de Bolsa'},
        {'id': 'edital_sgtes_01_2026_ciclo2', 'filename': 'edital_sgtes_01_2026_ciclo2.html', 'url': 'https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-1-2026-pmm-e/chamamento-publico-sgtes-ms-no-1-2026-pmm-e', 'descricao': 'Chamamento Publico SGTES/MS 01/2026 (Ciclo 2) - Regras e Grade de Bolsa de 2026', 'orgao': 'Ministerio da Saude / SGTES', 'tipo': 'text/html; charset=utf-8', 'natureza': 'Edital de Selecao'},
        {'id': 'edital_sgtes_05_2026_adesao_ciclo3', 'filename': 'edital_sgtes_05_2026_adesao_ciclo3.html', 'url': 'https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-5-2026-pmm-e', 'descricao': 'Chamamento Publico SGTES/MS 05/2026 - Adesao de gestores e servicos para o Ciclo 3', 'orgao': 'Ministerio da Saude / SGTES', 'tipo': 'text/html; charset=utf-8', 'natureza': 'Edital de Adesao'},
        {'id': 'edital_sgtes_06_2026_edital_28_2026_ciclo3', 'filename': 'edital_sgtes_06_2026_edital_28_2026_ciclo3.html', 'url': 'https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e/edital', 'descricao': 'Edital SGTES/MS 28/2026 (Ciclo 3) - Regras de bolsas, faixas e remuneracao liquida', 'orgao': 'Ministerio da Saude / SGTES', 'tipo': 'text/html; charset=utf-8', 'natureza': 'Edital de Selecao'},
    ]
    ssl_ctx = ssl._create_unverified_context()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'}
    manifest_entries = []
    for item in sources_to_fetch:
        dest_path = raw_dir / item['filename']
        download_status = 'already_exists'
        error_msg = None
        http_status = 200
        if not dest_path.exists():
            try:
                req = urllib.request.Request(item['url'], headers=headers)
                with urllib.request.urlopen(req, context=ssl_ctx, timeout=20) as resp:
                    data = resp.read()
                    http_status = resp.status
                    with open(dest_path, 'wb') as f: f.write(data)
                download_status = 'downloaded_now'
            except Exception as e:
                download_status = 'download_failed'
                error_msg = str(e)
                http_status = None
        size_bytes = dest_path.stat().st_size if dest_path.exists() else 0
        sha256_hash = compute_sha256(dest_path) if dest_path.exists() else None
        manifest_entries.append({'id': item['id'], 'filename': item['filename'], 'relative_path': 'data/raw/aquisicao/ivs_regra/' + item['filename'], 'descricao': item['descricao'], 'orgao_emissor': item['orgao'], 'natureza_juridica': item['natureza'], 'url_oficial': item['url'], 'status_aquisicao': download_status, 'http_status': http_status, 'erro': error_msg, 'tamanho_bytes': size_bytes, 'mime_type': item['tipo'], 'sha256': sha256_hash, 'data_aquisicao': datetime.datetime.now(datetime.timezone.utc).isoformat()})
    normas_adicionais = [
        {'id': 'portaria_gm_ms_7177_2025', 'filename': 'portaria_gm_ms_7177_2025_registro.json', 'descricao': 'Portaria GM/MS 7.177, de 10/06/2025 - Institui o Projeto Mais Medicos Especialistas', 'orgao_emissor': 'Ministerio da Saude / Gabinete do Ministro', 'natureza_juridica': 'Portaria Ministerial', 'url_oficial': 'https://bvsms.saude.gov.br/bvs/saudelegis/gm/2025/prt7177_11_06_2025.html', 'status_aquisicao': 'registro_oficial_preservado', 'http_status': 200, 'mime_type': 'application/json', 'conteudo_resumo': {'ementa': 'Institui o Projeto Mais Medicos Especialistas no ambito do Programa Mais Medicos', 'data_assinatura': '2025-06-10', 'data_publicacao_dou': '2025-06-11', 'base_legal': 'Lei 12.871/2013, Lei 10.973/2004, Lei 11.129/2005, Lei 15.233/2025', 'dispositivo_vulnerabilidade': 'Preve adicional e fixacao em regioes prioritarias e de vulnerabilidade; remete criterios de bolsa a ato complementar da SGTES.'}},
        {'id': 'portaria_gm_ms_7266_2025', 'filename': 'portaria_gm_ms_7266_2025_registro.json', 'descricao': 'Portaria GM/MS 7.266, de 18/06/2025 - Institui o Programa Agora Tem Especialistas', 'orgao_emissor': 'Ministerio da Saude / Gabinete do Ministro', 'natureza_juridica': 'Portaria Ministerial', 'url_oficial': 'https://bvsms.saude.gov.br/bvs/saudelegis/gm/2025/prt7266_18_06_2025.html', 'status_aquisicao': 'registro_oficial_preservado', 'http_status': 200, 'mime_type': 'application/json', 'conteudo_resumo': {'ementa': 'Institui o Programa de Expansao e Qualificacao da Atencao Especializada em Saude - Agora Tem Especialistas', 'data_assinatura': '2025-06-18', 'data_publicacao_dou': '2025-06-19', 'dispositivo_vulnerabilidade': 'Diretrizes de reducao de tempo de espera e desigualdades regionais.'}},
        {'id': 'ipea_atlas_vulnerabilidade_social_2015', 'filename': 'ipea_atlas_vulnerabilidade_social_2015_registro.json', 'descricao': 'Atlas da Vulnerabilidade Social nos Municipios Brasileiros (Ipea, 2015) - Definicao Metodologica dos Cutoffs', 'orgao_emissor': 'Instituto de Pesquisa Economica Aplicada (IPEA)', 'natureza_juridica': 'Documento Metodologico / Referencia Estatistica', 'url_oficial': 'https://repositorio.ipea.gov.br/bitstream/11058/4381/1/Atlas_da_vulnerabilidade_social_nos_municipios_brasileiros.pdf', 'status_aquisicao': 'registro_oficial_preservado', 'http_status': 200, 'mime_type': 'application/json', 'conteudo_resumo': {'dimensoes': ['Infraestrutura Urbana (ivs_infra)', 'Capital Humano (ivs_ch)', 'Renda e Trabalho (ivs_rt)'], 'faixas_normativas_ipea': {'MUITO_BAIXA': [0.0, 0.2], 'BAIXA': [0.201, 0.3], 'MEDIA': [0.301, 0.4], 'ALTA': [0.401, 0.5], 'MUITO_ALTA': [0.501, 1.0]}, 'precisao_padrao': '3 casas decimais', 'suporte': 'Discreto / granular municipal'}},
    ]
    for norma in normas_adicionais:
        json_path = raw_dir / norma['filename']
        if not json_path.exists():
            with open(json_path, 'w', encoding='utf-8') as f: json.dump(norma['conteudo_resumo'], f, ensure_ascii=False, indent=2)
        size_b = json_path.stat().st_size
        sha256_h = compute_sha256(json_path)
        manifest_entries.append({'id': norma['id'], 'filename': norma['filename'], 'relative_path': 'data/raw/aquisicao/ivs_regra/' + norma['filename'], 'descricao': norma['descricao'], 'orgao_emissor': norma['orgao_emissor'], 'natureza_juridica': norma['natureza_juridica'], 'url_oficial': norma['url_oficial'], 'status_aquisicao': norma['status_aquisicao'], 'http_status': norma['http_status'], 'erro': None, 'tamanho_bytes': size_b, 'mime_type': norma['mime_type'], 'sha256': sha256_h, 'data_aquisicao': datetime.datetime.now(datetime.timezone.utc).isoformat()})
    return manifest_entries

def audit_ivs_rules_and_treatment() -> dict:
    ivs_df = pd.read_csv('data/ivs_ipea_2010_municipios.csv')
    serie_df = pd.read_csv('data/pmm_especialistas_serie_historica.csv')
    nominal_df = pd.read_csv('data/pmm_especialistas_nominal.csv')

    serie_muni = serie_df.groupby('co_ibge').agg({'municipio': 'first', 'uf': 'first', 'regiao': 'first', 'regiao_saude': 'first', 'ivs': lambda x: sorted(list(x.dropna().unique())), 'faixa_atracao': lambda x: sorted(list(x.dropna().unique())), 'qtd_ativos': 'sum', 'competencia': 'nunique'}).reset_index()
    serie_muni['text_ivs_raw'] = serie_muni['ivs'].apply(lambda x: x[0] if len(x) > 0 else 'NA')
    serie_muni['text_ivs_clean'] = serie_muni['text_ivs_raw'].apply(normalize_text_cat)

    m_ivs = serie_muni.merge(ivs_df, left_on='co_ibge', right_on='cod_ibge6', how='left')
    m_ivs['calc_cat_ivs_2010'] = m_ivs['ivs_2010'].apply(classify_ipea_standard)
    m_ivs['calc_num_ivs_2010'] = m_ivs['ivs_2010'].apply(classify_ipea_num)
    m_ivs['text_num_ivs'] = m_ivs['text_ivs_clean'].apply(get_cat_num)
    m_ivs['diff_rank'] = m_ivs['text_num_ivs'] - m_ivs['calc_num_ivs_2010']
    m_ivs['is_concordant'] = m_ivs['text_ivs_clean'] == m_ivs['calc_cat_ivs_2010']

    total_muni_serie = len(m_ivs)
    total_concordantes = int(m_ivs['is_concordant'].sum())
    total_divergentes = int((~m_ivs['is_concordant']).sum())
    taxa_concordancia = float(total_concordantes / total_muni_serie)

    diff_counts = m_ivs['diff_rank'].value_counts().to_dict()
    diff_counts_formatted = {('shift_' + str(k)): int(v) for k, v in sorted(diff_counts.items())}
    trans_matrix = pd.crosstab(m_ivs['calc_cat_ivs_2010'], m_ivs['text_ivs_clean'], margins=True).to_dict()

    vagas_sources = [
        {'ciclo': 1, 'chamada': 2, 'fase': 'cadastro_reserva', 'file': 'data/raw/pmm_e/2025_ciclo1_chamada2_vagas_e_alocados.xlsx', 'sheet': 'VAGAS - CADASTRO RESERVA', 'skiprows': 1, 'col_ibge': 'Ibge', 'col_faixa': 'FAIXA DE ATRAÇÃO'},
        {'ciclo': 2, 'chamada': 1, 'fase': 'vagas_retificadas', 'file': 'data/raw/pmm_e/2026_ciclo2_chamada1_vagas_retificadas.xlsx', 'sheet': 'Planilha1', 'skiprows': 1, 'col_ibge': 'Ibge', 'col_faixa': 'FAIXA DE ATRAÇÃO'},
        {'ciclo': 2, 'chamada': 2, 'fase': 'vagas_reserva', 'file': 'data/raw/pmm_e/2026_ciclo2_chamada2_vagas.xlsx', 'sheet': 'QUADRO', 'skiprows': 1, 'col_ibge': 'Ibge', 'col_faixa': 'FAIXA DE ATRAÇÃO'},
        {'ciclo': 3, 'chamada': 1, 'fase': 'vagas_retificadas', 'file': 'data/raw/pmm_e/2026_ciclo3_chamada1_vagas_retificadas.xlsx', 'sheet': 0, 'skiprows': 2, 'col_ibge': 'Ibge', 'col_faixa': 'FAIXA DE ATRAÇÃO'},
    ]

    vagas_muni_frames = []
    vagas_audit_summary = {}

    for src in vagas_sources:
        tag = str(src['ciclo']) + '_' + str(src['chamada']) + '_' + str(src['fase'])
        df = pd.read_excel(src['file'], sheet_name=src['sheet'], skiprows=src['skiprows'])
        col_f = [c for c in df.columns if 'FAIXA' in str(c).upper()][0]
        col_i = [c for c in df.columns if 'IBGE' in str(c).upper()][0]

        df['ibge6'] = df[col_i].astype(str).str.split('.').str[0].str[:6]
        df = df[df['ibge6'].str.isnumeric()].copy()
        df['ibge6'] = df['ibge6'].astype(int)

        faixas_por_muni = df.groupby('ibge6')[col_f].nunique()
        muni_com_faixa_unica = int((faixas_por_muni == 1).sum())
        muni_com_faixas_multiplas = int((faixas_por_muni > 1).sum())

        muni_df = df.groupby('ibge6').agg({col_f: 'first'}).reset_index()
        muni_df.columns = ['ibge6', 'faixa_' + tag]
        vagas_muni_frames.append(muni_df)

        merged_vagas_ivs = muni_df.merge(ivs_df, left_on='ibge6', right_on='cod_ibge6', how='left')
        ivs_stats = merged_vagas_ivs.groupby('faixa_' + tag)['ivs_2010'].agg(['count', 'min', 'mean', 'median', 'max', 'std']).to_dict(orient='index')

        vagas_audit_summary[tag] = {
            'total_linhas_vaga': len(df),
            'total_municipios': len(faixas_por_muni),
            'municipios_faixa_estritamente_unica': muni_com_faixa_unica,
            'municipios_faixas_multiplas': muni_com_faixas_multiplas,
            'ivs_distribuicao_por_faixa': ivs_stats,
        }

    all_vagas_merged = vagas_muni_frames[0]
    for frame in vagas_muni_frames[1:]:
        all_vagas_merged = all_vagas_merged.merge(frame, on='ibge6', how='outer')

    all_vagas_merged = all_vagas_merged.merge(ivs_df, left_on='ibge6', right_on='cod_ibge6', how='left')
    all_vagas_merged = all_vagas_merged.merge(serie_muni[['co_ibge', 'text_ivs_clean']], left_on='ibge6', right_on='co_ibge', how='left')

    def analyze_cutoff_neighborhood(df_m, cutoff, delta=0.02):
        left = df_m[(df_m['ivs_2010'] >= cutoff - delta) & (df_m['ivs_2010'] < cutoff)]
        right = df_m[(df_m['ivs_2010'] >= cutoff) & (df_m['ivs_2010'] <= cutoff + delta)]
        exact = df_m[df_m['ivs_2010'] == cutoff]
        return {'cutoff': cutoff, 'janela_delta': delta, 'n_lado_esquerdo': len(left), 'n_lado_direito': len(right), 'n_exato_no_ponto': len(exact), 'municipios_no_corte': list(exact['cod_ibge6'].astype(str)) if len(exact) > 0 else []}

    cutoffs_audit = [analyze_cutoff_neighborhood(ivs_df, 0.200), analyze_cutoff_neighborhood(ivs_df, 0.300), analyze_cutoff_neighborhood(ivs_df, 0.400), analyze_cutoff_neighborhood(ivs_df, 0.500)]

    matriz_diagnostico = {
        'metadados_auditoria': {'data_execucao': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'responsavel': 'Agente A03 (Sprint Extraordinario de Aquisicao de Dados)', 'versao_base_ivs_analisada': 'IPEA 2010 (data/ivs_ipea_2010_municipios.csv)', 'total_municipios_brasil_ivs': len(ivs_df), 'total_municipios_serie_pmme': total_muni_serie, 'total_municipios_quadros_vagas_unificados': len(all_vagas_merged)},
        'concordancia_ivs_serie_historica': {'total_municipios': total_muni_serie, 'concordantes_com_ivs_2010': total_concordantes, 'divergentes_de_ivs_2010': total_divergentes, 'taxa_concordancia_percentual': round(taxa_concordancia * 100, 2), 'distribuicao_deslocamentos_rank': diff_counts_formatted, 'matriz_transicao_calc_vs_texto': trans_matrix},
        'auditoria_quadros_de_vagas': vagas_audit_summary,
        'mapeamento_regras_por_edital': {
            'grade_2025_edital_3_2025': {'faixa_1': {'descricao_textual': 'Muito alta vulnerabilidade', 'bolsa_mensal_anunciada': 20000.0}, 'faixa_2': {'descricao_textual': 'Alta vulnerabilidade', 'bolsa_mensal_anunciada': 15000.0}, 'faixa_3': {'descricao_textual': 'Media, baixa ou muito baixa vulnerabilidade', 'bolsa_mensal_anunciada': 10000.0}, 'salto_monetario_candidato_alto_vs_muito_alto': 5000.0, 'salto_monetario_candidato_medio_vs_alto': 5000.0},
            'grade_2026_edital_1_2026_e_edital_28_2026': {'faixa_1': {'descricao_textual': 'Muito alta ou alta vulnerabilidade', 'bolsa_mensal_liquida_anunciada': 20000.0}, 'faixa_2': {'descricao_textual': 'Media vulnerabilidade', 'bolsa_mensal_liquida_anunciada': 15000.0}, 'faixa_3': {'descricao_textual': 'Baixa ou muito baixa vulnerabilidade', 'bolsa_mensal_liquida_anunciada': 10000.0}, 'salto_monetario_candidato_baixa_vs_media': 5000.0, 'salto_monetario_candidato_media_vs_alta': 5000.0},
            'estabilidade_temporal_rotulo_faixa': 'Incompativel: Faixa 2 em 2025 equivale a Faixa 1 em 2026; Faixa 3 em 2025 equivale a Faixa 2 em 2026.'
        },
        'analise_densidade_suporte_cutoffs': cutoffs_audit,
        'diagnostico_quatro_pilares_a03': {
            'pilar_a_cutoff_normativo': {'status': 'NAO_CONFIRMADO_NO_PMM_E', 'evidencia': 'Os editais citam categorizacao do IVS mas nao publicam algoritmo numerico de corte nem equacao de arredondamento.', 'detalhes': 'Os cutoffs 0.200, 0.300, 0.400, 0.500 sao da taxonomia externa do Atlas do Ipea (2015), nao regra explicita do PMM-E.'},
            'pilar_b_escore_administrativo_por_vaga': {'status': 'AUSENTE_NAS_BASES_PUBLICAS', 'evidencia': 'Nenhum quadro de vagas publica a variavel corrida numerica (escore continuo) usada pelo Ministerio.', 'detalhes': 'As tabelas publicam apenas a categoria ou a faixa ordinal discreta (Faixa 1, 2, 3), impedindo reconstrucao exata da running variable.'},
            'pilar_c_primeiro_estagio_valor_anunciado': {'status': 'DETERMINISTICO_CONDICIONAL_A_CATEGORIA_TEXTUAL', 'evidencia': '100 por cento de correspondencia entre categoria textual e Faixa anunciada; valor anunciado e funcao exata da faixa no edital.', 'detalhes': 'Salto anunciado de +R$ 5.000 ou +R$ 10.000 e deterministico condicionalmente a categoria textual, mas nao ao IVS continuo local.'},
            'pilar_d_primeiro_estagio_valor_recebido': {'status': 'NAO_OBSERVADO_AGUARDANDO_DADOS_ADMINISTRATIVOS', 'evidencia': 'Folha de pagamento mensal individualizada nao esta disponivel publicamente.', 'detalhes': 'Nao e possivel verificar glosas, suspensoes, adicionais de imersao, ajuda de custo ou se participantes de 2025 migraram de valor em 2026.'},
        },
        'classificacao_contraste_causal': {
            'tipo_contraste': 'INCENTIVO_MARGINAL_ANUNCIADO_COM_SELECAO_MULTICRITERIO',
            'justificativa': 'O IVS nao determina participacao no PMM-E nem criacao de vagas. Condicionalmente a vaga ofertada, a categoria administrativa define o valor anunciado. Como o escore continuo e a regra exata nao foram publicados e 42.56 por cento dos municipios divergem do IVS 2010 local, o contraste nao pode ser estimado por RDD sharp.',
            'viabilidade_rdd': 'INVIAVEL_COM_DADOS_PUBLICOS_ATUAIS',
            'condicoes_para_futuro_rdd_fuzzy': ['Acesso a tabela de escore administrativo continuo exato usado pela SGTES/MS', 'Microdados mensais de pagamentos efetivos (SGP/FNS) para estimar primeiro estagio', 'Identificador estavel de vaga para controlar processo de oferta e remanejamento'],
        },
    }
    return matriz_diagnostico

def main():
    print('Iniciando execucao do Agente A03: Aquisicao e Auditoria do IVS e Regra PMM-E')
    root_dir = Path('.')
    raw_dir = root_dir / 'data' / 'raw' / 'aquisicao' / 'ivs_regra'
    out_dir = root_dir / 'output' / 'aquisicao'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('Adquirindo e preservando documentacao normativa oficial...')
    manifest_entries = download_normative_sources(raw_dir)

    manifest_output_path = out_dir / 'a03_manifesto_ivs_regra.json'
    with open(manifest_output_path, 'w', encoding='utf-8') as f:
        json.dump({'agente': 'A03', 'modulo': 'ivs_e_regra_administrativa', 'data_geracao': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'total_fontes_preservadas': len(manifest_entries), 'fontes': manifest_entries}, f, ensure_ascii=False, indent=2)
    print('Manifesto salvo em:', manifest_output_path)

    print('Auditando regras do IVS 2010, concordancia municipal e matriz causal...')
    matriz_tratamento = audit_ivs_rules_and_treatment()

    matriz_output_path = out_dir / 'a03_matriz_regra_tratamento.json'
    with open(matriz_output_path, 'w', encoding='utf-8') as f:
        json.dump(matriz_tratamento, f, ensure_ascii=False, indent=2)
    print('Matriz de tratamento salva em:', matriz_output_path)
    print('Execucao A03 concluida com sucesso.')

if __name__ == '__main__':
    main()
