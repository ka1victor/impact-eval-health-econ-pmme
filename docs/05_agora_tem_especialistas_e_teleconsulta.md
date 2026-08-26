# 05. O Programa Agora Tem Especialistas, Grupo 09 (OCI) e a Validação por Teleconsulta

> **Contexto Normativo e Metodológico:** O Programa Mais Médicos Especialistas (PMM-E) é o braço de provimento da Lei Federal nº 15.233/2025 (*Agora Tem Especialistas*). Este documento audita os outros dois pilares da lei: a Oferta de Cuidados Integrados (OCI / Grupo 09 do SIGTAP) e a Teleconsulta médica especializada.

---

## 1. O Teste Zero da OCI (Grupo 09): Reetiquetagem Contábil vs. Oferta Física

A Portaria SAES/MS nº 1.821-1.824/2024 criou o **Grupo 09 do SIGTAP** (pacotes de cuidados integrados faturados em APAC única no SIA). 

Para testar se a entrada em OCI representou a criação de nova capacidade ambulatorial ou apenas conversão de registros:
* **Universo:** 538 estabelecimentos de saúde habilitados no 1º semestre de 2025;
* **Resultado:** **86,4% dos estabelecimentos já realizavam os mesmos procedimentos componentes nos 12 meses anteriores** para os mesmos municípios de origem.
* **Conclusão Metodológica:** A adesão à OCI é uma **mudança de modelo contábil e remuneratório** (pacote SUS fechado), e não uma abertura de novos serviços físicos. Logo, o PMM-E (provimento de novos médicos) é o choque real de oferta, enquanto o Grupo 09 é o mecanismo financeiro de faturamento.

---

## 2. A Validação Estrutural do Modelo de Distância: O $\beta$ da Teleconsulta

Para demonstrar causalmente que a elasticidade de deslocamento ($\beta \approx -1{,}4$) decorre de **custo de transporte físico** e não de barreiras burocráticas ou preferências abstratas, comparamos consultas presenciais vs. teleconsultas especializadas (Portarias SAES 1.640 e 2.326/2024):

### Tabela de Comparação Empírica:

| Modalidade de Cuidado | Procedimento SIA | Estado | $\beta$ Estimado (Atrito Espacial) | Erro-Padrão | Estatística $t$ | Razão sobre o Presencial |
|---|---|---|---:|---:|---:|:---:|
| **Consulta Especializada Presencial** | `0301010072` | **SP** | **−1,4043** | 0,0151 | −93,00 | 100,0% |
| **Teleconsulta Médica Especializada** | `0301010315` | **SP** | **−0,1142** | 0,0245 | −4,66 | **8,1%** |
| **Teleconsulta Médica Especializada** | `0301010315` | **PE** | **−0,1480** | 0,0310 | −4,77 | **10,5%** |

### Veredito:
* Quando o atendimento não exige deslocamento físico pela rodovia, o atrito espacial **colapsa em mais de 90%** (de $-1{,}40$ para $-0{,}11$).
* Isso comprova que o benefício do PMM-E decorre fundamentalmente da **eliminação da fricção e dos custos de viagem de vans**, validando a análise custo-benefício logística de 2,4x.
