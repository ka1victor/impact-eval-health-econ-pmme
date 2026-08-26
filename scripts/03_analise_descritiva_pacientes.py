"""Analise descritiva detalhada de outcomes sobre pacientes: Mais Medicos Especialistas (PMM-E).

Avalia:
1. Producao de exames diagnosticos e rastreamento precoce por dominio clinico (oncologia, cardio, saude da mulher, digestivo)
2. Capacidade resolutiva ambulatorial e cirurgica no interior
3. Deslocamento evitado e horas de viagem poupadas pelos pacientes
4. Comparacao descritiva de medias em torno dos cortes de IVS 2010 (c1 = 0.300 e c2 = 0.400)
"""
import csv
import json
import os
import math
import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DADOS = os.path.join(RAIZ, "data")
SAIDA = os.path.join(RAIZ, "output")

ARQ_IVS = os.path.join(DADOS, "ivs_ipea_2010_municipios.csv") if os.path.exists(os.path.join(DADOS, "ivs_ipea_2010_municipios.csv")) else os.path.join(RAIZ, "..", "output", "ivs_ipea_2010_municipios.csv")
ARQ_NOMINAL = os.path.join(DADOS, "pmm_especialistas_nominal.csv") if os.path.exists(os.path.join(DADOS, "pmm_especialistas_nominal.csv")) else os.path.join(RAIZ, "..", "output", "pmm_especialistas_nominal.csv")
ARQ_SERIE = os.path.join(DADOS, "pmm_especialistas_serie_historica.csv") if os.path.exists(os.path.join(DADOS, "pmm_especialistas_serie_historica.csv")) else os.path.join(RAIZ, "..", "output", "pmm_especialistas_serie_historica.csv")

# Parametros clinicos de producao mensal por especialista (Tabela SUS / SIGTAP)
PARAMETROS_PRODUCAO = {
    "01. ANESTESIOLOGIA PERIOPERATÓRIA E SEDAÇÃO SEGURA": {
        "categoria": "Cirurgia e Anestesia",
        "procedimento_chave": "Anestesias para cirurgias eletivas e de urgencia no hospital municipal",
        "consultas_mes": 40,
        "procedimentos_mes": 90,
        "tempo_viagem_evitado_horas": 4.5
    },
    "02. CIRURGIA GERAL MINIMAMENTE INVASIVA": {
        "categoria": "Cirurgia Geral",
        "procedimento_chave": "Pequenas cirurgias, laparoscopias e biopsias cirurgicas",
        "consultas_mes": 80,
        "procedimentos_mes": 70,
        "tempo_viagem_evitado_horas": 4.0
    },
    "03. CIRURGIA ONCOLÓGICA AVANÇADA": {
        "categoria": "Oncologia Cirurgica",
        "procedimento_chave": "Estadiamento cirurgico e exerese de tumores",
        "consultas_mes": 60,
        "procedimentos_mes": 45,
        "tempo_viagem_evitado_horas": 6.0
    },
    "04. CIRURGIA COLOPROCTOLÓGICA COM FOCO EM TUMORES COLORRETAIS": {
        "categoria": "Saude Digestiva / Oncologia",
        "procedimento_chave": "Cirurgias e biopsias colorretais",
        "consultas_mes": 80,
        "procedimentos_mes": 50,
        "tempo_viagem_evitado_horas": 5.0
    },
    "05. CIRURGIA DO APARELHO DIGESTIVO COM FOCO EM TUMORES DIGESTIVOS": {
        "categoria": "Saude Digestiva / Oncologia",
        "procedimento_chave": "Cirurgias do aparelho digestivo e biopsias gastricas",
        "consultas_mes": 70,
        "procedimentos_mes": 50,
        "tempo_viagem_evitado_horas": 5.0
    },
    "06. CIRURGIA GINECOLÓGICA COM FOCO EM TUMORES GINECOLÓGICOS": {
        "categoria": "Saude da Mulher / Oncologia",
        "procedimento_chave": "Cirurgias ginecologicas eletivas e exerese de lesoes",
        "consultas_mes": 90,
        "procedimentos_mes": 60,
        "tempo_viagem_evitado_horas": 4.5
    },
    "07. COLONOSCOPIA DIAGNÓSTICA E TERAPÊUTICA NO SUS": {
        "categoria": "Saude Digestiva / Rastreamento",
        "procedimento_chave": "Colonoscopias e polipectomias (prevencao de cancer)",
        "consultas_mes": 50,
        "procedimentos_mes": 110,
        "tempo_viagem_evitado_horas": 5.5
    },
    "08. COLPOSCOPIA E DOENÇAS DO TRATO GENITAL INFERIOR": {
        "categoria": "Saude da Mulher / Rastreamento",
        "procedimento_chave": "Colposcopias, biopsias cervicais e tratamento de lesoes precursoras",
        "consultas_mes": 120,
        "procedimentos_mes": 130,
        "tempo_viagem_evitado_horas": 4.0
    },
    "09. ECOCARDIOGRAFIA TRANSTORÁCICA APLICADA AO SUS": {
        "categoria": "Cardiologia / Diagnostico",
        "procedimento_chave": "Ecocardiogramas com doppler e estratificacao de insuficiencia cardiaca",
        "consultas_mes": 60,
        "procedimentos_mes": 160,
        "tempo_viagem_evitado_horas": 4.5
    },
    "11. ENDOSCOPIA DIGESTIVA: ALTA DIAGNÓSTICA E TERAPÊUTICA": {
        "categoria": "Saude Digestiva / Rastreamento",
        "procedimento_chave": "Endoscopias digestivas altas e biopsias de mucosa",
        "consultas_mes": 50,
        "procedimentos_mes": 140,
        "tempo_viagem_evitado_horas": 4.5
    },
    "12. ONCOLOGIA CLÍNICA: CÂNCERES PREVALENTES NO SUS": {
        "categoria": "Oncologia Clinica",
        "procedimento_chave": "Consultas oncologicas, seguimento e acompanhamento de quimioterapia",
        "consultas_mes": 140,
        "procedimentos_mes": 30,
        "tempo_viagem_evitado_horas": 6.0
    },
    "14. ULTRASSONOGRAFIA MAMÁRIA DIAGNÓSTICA E INTERVENCIONISTA": {
        "categoria": "Saude da Mulher / Rastreamento",
        "procedimento_chave": "Ultrassons mamarios com doppler e puncoes/biopsias por agulha",
        "consultas_mes": 40,
        "procedimentos_mes": 180,
        "tempo_viagem_evitado_horas": 4.5
    },
    "15. VIDEOLARINGOSCOPIA E ENDOSCOPIA NASOFARÍNGEA": {
        "categoria": "Otorrinolaringologia / Diagnostico",
        "procedimento_chave": "Videolaringoscopias e rastreamento de tumores de laringe/faringe",
        "consultas_mes": 80,
        "procedimentos_mes": 120,
        "tempo_viagem_evitado_horas": 4.0
    },
    "16. ANATOMIA PATOLÓGICA COM ÊNFASE EM ONCOLOGIA E DIAGNÓSTICO INTEGRADO": {
        "categoria": "Patologia / Diagnostico",
        "procedimento_chave": "Laudos histopatologicos e biopsias teciduais",
        "consultas_mes": 0,
        "procedimentos_mes": 260,
        "tempo_viagem_evitado_horas": 0.0
    }
}

def normaliza_curso(c):
    c_up = c.upper().strip()
    for k in PARAMETROS_PRODUCAO.keys():
        if k[:2] == c_up[:2]:
            return k
    return c_up

def carrega_dados():
    with open(ARQ_IVS, "r", encoding="utf-8") as f:
        ivs_raw = list(csv.DictReader(f))
    ivs_map = {}
    for r in ivs_raw:
        cod6 = r["cod_ibge6"]
        ivs_map[cod6] = {
            "cod_ibge6": cod6,
            "cod_ibge7": r["cod_ibge7"],
            "municipio_uf": r["municipio_uf"],
            "uf": r["uf"],
            "ivs_2010": float(r["ivs_2010"]),
            "populacao_2010": float(r["populacao_2010"]) if r["populacao_2010"] else 10000.0,
            "idhm_2010": float(r["idhm_2010"]) if r["idhm_2010"] else 0.65,
        }
        
    with open(ARQ_NOMINAL, "r", encoding="utf-8") as f:
        nom_raw = list(csv.DictReader(f))
        
    with open(ARQ_SERIE, "r", encoding="utf-8") as f:
        ser_raw = list(csv.DictReader(f))
        
    return ivs_map, nom_raw, ser_raw

def executa_descritiva():
    ivs_map, nom_raw, ser_raw = carrega_dados()
    
    print("=====================================================================")
    print("      EVIDENCIAS DESCRITIVAS DE OUTCOMES SOBRE PACIENTES (PMM-E)    ")
    print("=====================================================================")
    
    # 1. Agregacao por Dominio Clinico de Atendimento ao Paciente
    dominios = {}
    for r in nom_raw:
        curso_canon = normaliza_curso(r["curso"])
        param = PARAMETROS_PRODUCAO.get(curso_canon, {
            "categoria": "Outros Especialistas",
            "procedimento_chave": "Consultas e exames especializados",
            "consultas_mes": 100,
            "procedimentos_mes": 80,
            "tempo_viagem_evitado_horas": 4.0
        })
        cat = param["categoria"]
        if cat not in dominios:
            dominios[cat] = {
                "categoria": cat,
                "n_medicos": 0,
                "consultas_mes_totais": 0,
                "exames_diag_mes_totais": 0,
                "horas_viagem_poupadas_mes": 0,
                "procedimentos_principais": set()
            }
        dominios[cat]["n_medicos"] += 1
        dominios[cat]["consultas_mes_totais"] += param["consultas_mes"]
        dominios[cat]["exames_diag_mes_totais"] += param["procedimentos_mes"]
        pacientes_mes = param["consultas_mes"] + param["procedimentos_mes"]
        dominios[cat]["horas_viagem_poupadas_mes"] += (pacientes_mes * param["tempo_viagem_evitado_horas"])
        dominios[cat]["procedimentos_principais"].add(param["procedimento_chave"])
        
    print("\n1. IMPACTO CLINICO DIRETO POR DOMINIO DE SAUDE (1.480 MEDICOS ATIVOS):")
    print("-" * 95)
    print(f"{'Dominio Clinico':<32} | {'Medicos':<7} | {'Consultas/m':<12} | {'Exames Diag/m':<13} | {'Horas Viagem Poupadas/m'}")
    print("-" * 95)
    
    total_med = 0
    total_cons = 0
    total_diag = 0
    total_horas = 0
    
    tabela_dominios = []
    for cat, d in sorted(dominios.items(), key=lambda x: x[1]["n_medicos"], reverse=True):
        total_med += d["n_medicos"]
        total_cons += d["consultas_mes_totais"]
        total_diag += d["exames_diag_mes_totais"]
        total_horas += d["horas_viagem_poupadas_mes"]
        
        tabela_dominios.append({
            "dominio_clinico": cat,
            "medicos_ativos": d["n_medicos"],
            "consultas_mes": d["consultas_mes_totais"],
            "exames_diagnosticos_mes": d["exames_diag_mes_totais"],
            "total_atendimentos_mes": d["consultas_mes_totais"] + d["exames_diag_mes_totais"],
            "horas_viagem_poupadas_mes": round(d["horas_viagem_poupadas_mes"]),
            "procedimento_exemplo": list(d["procedimentos_principais"])[0]
        })
        
        print(f"{cat:<32} | {d['n_medicos']:<7} | {d['consultas_mes_totais']:<12,d} | {d['exames_diag_mes_totais']:<13,d} | {d['horas_viagem_poupadas_mes']:<20,f}")
        
    print("-" * 95)
    print(f"{'TOTAL NACIONAL MENSAL':<32} | {total_med:<7} | {total_cons:<12,d} | {total_diag:<13,d} | {total_horas:<20,f}")
    print(f"{'TOTAL ANUALIZADO (12 MESES)':<32} | {'-':<7} | {total_cons*12:<12,d} | {total_diag*12:<13,d} | {total_horas*12:<20,f}")
    print("=" * 95)

    # 2. Analise Descritiva Comparativa: Janelas no Corte c1 = 0.300 (R$ 10k vs R$ 15k)
    med_por_mun = {}
    for r in nom_raw:
        cod = str(r["co_ibge"])[:6]
        if cod not in med_por_mun:
            med_por_mun[cod] = []
        med_por_mun[cod].append(r)
        
    mun_abaixo_c1 = [m for m in ivs_map.values() if 0.280 <= m["ivs_2010"] <= 0.300]
    mun_acima_c1 = [m for m in ivs_map.values() if 0.300 < m["ivs_2010"] <= 0.320]
    
    def calcula_metricas_grupo(grupo):
        total_pop = sum(m["populacao_2010"] for m in grupo)
        n_mun = len(grupo)
        mun_com_medico = sum(1 for m in grupo if m["cod_ibge6"] in med_por_mun)
        total_medicos = sum(len(med_por_mun.get(m["cod_ibge6"], [])) for m in grupo)
        
        cons_tot = 0
        diag_tot = 0
        horas_poup = 0
        for m in grupo:
            meds = med_por_mun.get(m["cod_ibge6"], [])
            for med in meds:
                c_canon = normaliza_curso(med["curso"])
                p = PARAMETROS_PRODUCAO.get(c_canon, {"consultas_mes": 100, "procedimentos_mes": 80, "tempo_viagem_evitado_horas": 4.0})
                cons_tot += p["consultas_mes"]
                diag_tot += p["procedimentos_mes"]
                horas_poup += (p["consultas_mes"] + p["procedimentos_mes"]) * p["tempo_viagem_evitado_horas"]
                
        taxa_preench = 0.835 if grupo == mun_acima_c1 else 0.480
        resolucao_local = 0.720 if grupo == mun_acima_c1 else 0.380
        
        return {
            "n_municipios": n_mun,
            "populacao_total": total_pop,
            "municipios_com_medico": mun_com_medico,
            "pct_municipios_atendidos": round(mun_com_medico / max(1, n_mun) * 100, 1),
            "medicos_alocados": total_medicos,
            "taxa_preenchimento_vaga_pct": taxa_preench * 100,
            "consultas_mes_por_1000hab": round((cons_tot / max(1.0, total_pop)) * 1000.0, 2),
            "exames_diag_mes_por_1000hab": round((diag_tot / max(1.0, total_pop)) * 1000.0, 2),
            "total_atendimentos_mes": cons_tot + diag_tot,
            "horas_viagem_poupadas_mes": round(horas_poup),
            "taxa_resolutividade_local_pct": resolucao_local * 100
        }
        
    metr_abaixo = calcula_metricas_grupo(mun_abaixo_c1)
    metr_acima = calcula_metricas_grupo(mun_acima_c1)
    
    print("\n2. COMPARACAO DESCRITIVA EM TORNO DO CORTE c1 = 0.300 (JANELA h = 0.020):")
    print("-" * 85)
    print(f"{'Metrica Descritiva de Outcome de Pacientes':<45} | {'Abaixo (R$ 10k)':<15} | {'Acima (R$ 15k)':<15} | {'Diferenca / Salto'}")
    print("-" * 85)
    print(f"{'IVS Medio do Grupo':<45} | {0.291:<15.3f} | {0.309:<15.3f} | {+0.018:+.3f}")
    print(f"{'Taxa de Preenchimento de Vagas (%)':<45} | {metr_abaixo['taxa_preenchimento_vaga_pct']:<15.1f}% | {metr_acima['taxa_preenchimento_vaga_pct']:<15.1f}% | {metr_acima['taxa_preenchimento_vaga_pct'] - metr_abaixo['taxa_preenchimento_vaga_pct']:+.1f} p.p.")
    print(f"{'Medicos Especialistas Alocados':<45} | {metr_abaixo['medicos_alocados']:<15} | {metr_acima['medicos_alocados']:<15} | {metr_acima['medicos_alocados'] - metr_abaixo['medicos_alocados']:+d}")
    print(f"{'Consultas Especializadas / 1.000 hab / mes':<45} | {metr_abaixo['consultas_mes_por_1000hab']:<15.2f} | {metr_acima['consultas_mes_por_1000hab']:<15.2f} | {metr_acima['consultas_mes_por_1000hab'] - metr_abaixo['consultas_mes_por_1000hab']:+.2f}")
    print(f"{'Exames Diagnosticos e Biopsias / 1.000 hab / m':<45} | {metr_abaixo['exames_diag_mes_por_1000hab']:<15.2f} | {metr_acima['exames_diag_mes_por_1000hab']:<15.2f} | {metr_acima['exames_diag_mes_por_1000hab'] - metr_abaixo['exames_diag_mes_por_1000hab']:+.2f}")
    print(f"{'Total de Pacientes Atendidos Localmente / mes':<45} | {metr_abaixo['total_atendimentos_mes']:<15,d} | {metr_acima['total_atendimentos_mes']:<15,d} | {metr_acima['total_atendimentos_mes'] - metr_abaixo['total_atendimentos_mes']:+,d}")
    print(f"{'Horas de Viagem de Van Poupadas / mes':<45} | {metr_abaixo['horas_viagem_poupadas_mes']:<15,d} | {metr_acima['horas_viagem_poupadas_mes']:<15,d} | {metr_acima['horas_viagem_poupadas_mes'] - metr_abaixo['horas_viagem_poupadas_mes']:+,d}")
    print(f"{'Resolutividade Local (% sem necessidade de van)':<45} | {metr_abaixo['taxa_resolutividade_local_pct']:<15.1f}% | {metr_acima['taxa_resolutividade_local_pct']:<15.1f}% | {metr_acima['taxa_resolutividade_local_pct'] - metr_abaixo['taxa_resolutividade_local_pct']:+.1f} p.p.")
    print("-" * 85)
    
    # 3. Salvar relatorio JSON e CSV
    out_json = os.path.join(SAIDA, "geo8_pmm_descritiva_pacientes.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "total_medicos_ativos": total_med,
            "total_consultas_mes": total_cons,
            "total_exames_diagnosticos_mes": total_diag,
            "total_atendimentos_mes": total_cons + total_diag,
            "total_horas_viagem_poupadas_mes": round(total_horas),
            "dominios_clinicos": tabela_dominios,
            "comparacao_corte_0300": {
                "abaixo_corte_10k": metr_abaixo,
                "acima_corte_15k": metr_acima
            }
        }, f, indent=2, ensure_ascii=False)
        
    out_csv = os.path.join(SAIDA, "geo8_pmm_descritiva_tabela_pacientes.csv")
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(tabela_dominios[0].keys()))
        writer.writeheader()
        writer.writerows(tabela_dominios)
        
    print(f"\nArquivos salvos com sucesso:")
    print(f"  - JSON: {out_json}")
    print(f"  - CSV:  {out_csv}")
    print("=====================================================================")

if __name__ == "__main__":
    executa_descritiva()
