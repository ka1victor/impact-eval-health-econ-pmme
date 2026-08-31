# Auditoria do Piloto SIH Pré-Tratamento — Anestesiologia (PMM-E)

> **Data de Execução:** 2026-08-30  
> **Status:** Piloto SIH Pré-Tratamento Concluído com Sucesso (Prompt C3-02)  
> **Painéis Gerados:** `output/avaliacao_ciclo3/sih_pre/painel_sih_cnes_pre.parquet` e `painel_sih_muni_pre.parquet`

---

## 1. Benchmark de Descompressão e Armazenamento

A aquisição foi estruturada em modo estrito de streaming local (processando arquivo por arquivo e descartando imediatamente os intermediários), comprovando a viabilidade técnica e economia de disco:

| Métrica | Resultado Observado (GO 2025-01) |
|---|---:|
| Tamanho Comprimido (.dbc) | 2.68 MB |
| Tempo de Download | 1.71 s |
| Tempo de Descompressão & Parser | 0.39 s |
| Linhas Processadas | 38,096 linhas |
| **Pico de Disco Temporário** | **< 150 MB** |
| **Volume Total Transferido no Pré-Painel** | **2139.66 MB** |

---

## 2. Estrutura do Painel Pré-Tratamento Construído

O painel cobre **25 competências mensais (202406 a 202606 (25 competencias))** para os 612 estabelecimentos e 456 municípios da coorte de Anestesiologia do Ciclo 3.

### 2.1 Critérios de Definição das Cirurgias Eletivas
- **Grupo 04 do SIGTAP:** Códigos de procedimentos iniciados por `04` (Procedimentos Cirúrgicos).
- **AIH Inicial (`IDENT = '1'`):** Garante a contagem de internações únicas, descartando AIHs de continuidade (`IDENT = '5'`).
- **Caráter Eletivo (`CAR_INT = '01'`):** Separa cirurgias programadas de atendimentos de urgência (`CAR_INT = '02'`).

### 2.2 Estatísticas Descritivas do Pré-Período
- **Total de Cirurgias Eletivas no Painel Pré:** 1,535,731 cirurgias
- **Média Mensal por CNES Imediato Puro (Tratamento):** 89.14 cirurgias/mês
- **Média Mensal por CNES Não Priorizado Puro (Controle):** 109.49 cirurgias/mês

---

## 3. Próximo Portão: C3-03 (Torneio Pré-Tratamento)

Com o painel do SIH construído exclusivamente sobre dados anteriores a $T_0$, o próximo passo é executar o **Prompt C3-03**:
1. Testar pré-tendências paralelas e placebos temporais para cirurgias eletivas.
2. Calcular o Efeito Mínimo Detectável (MDE) para o módulo de cirurgias.
3. Arbitrar por critérios objetivos se o módulo assistencial de anestesiologia será confirmatório ou exploratório, congelando o **Plano de Pré-Análise** oficial.
