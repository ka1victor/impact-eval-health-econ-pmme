# Auditoria do Piloto SIH Pré-Tratamento — Anestesiologia (PMM-E)

> **Data de Execução:** 2026-08-30  
> **Status:** Piloto técnico concluído; validação substantiva pendente
> **Painéis Gerados:** `output/avaliacao_ciclo3/sih_pre/painel_sih_cnes_pre.parquet` e `painel_sih_muni_pre.parquet`

---

## 1. Benchmark de Descompressão e Armazenamento

A aquisição processou um arquivo por vez e descartou intermediários. Isso
comprovou a viabilidade de leitura, mas o pico de disco não foi instrumentado e
não pode ser inferido apenas do tamanho do DBC.

| Métrica | Resultado Observado (GO 2025-01) |
|---|---:|
| Tamanho Comprimido (.dbc) | 2.68 MB |
| Tempo de Download | 1.71 s |
| Tempo de Descompressão & Parser | 0.39 s |
| Linhas Processadas | 38,096 linhas |
| Pico de Disco Temporário | não instrumentado nesta versão |
| **Volume Total Transferido no Pré-Painel** | **2139.66 MB** |

---

## 2. Estrutura do Painel Pré-Tratamento Construído

O painel cobre **25 competências mensais (202406 a 202606 (25 competencias))** para os 612 estabelecimentos e 456 municípios da coorte de Anestesiologia do Ciclo 3.

### 2.1 Definição operacional candidata
- **Grupo 04:** códigos de `PROC_REA` iniciados por `04`. O CSV produzido só
  lista subgrupos; ele não historiciza mensalmente o SIGTAP. Portanto, essa
  ainda não é uma família clínica definitiva ligada à anestesiologia.
- **AIH Inicial (`IDENT = '1'`):** Garante a contagem de internações únicas, descartando AIHs de continuidade (`IDENT = '5'`).
- **Caráter Eletivo (`CAR_INT = '01'`):** Separa cirurgias programadas de atendimentos de urgência (`CAR_INT = '02'`).

### 2.2 Estatísticas Descritivas do Pré-Período
- **Total de Cirurgias Eletivas no Painel Pré:** 1,535,731 cirurgias
- **Média Mensal por CNES Imediato Puro (Tratamento):** 89.14 cirurgias/mês
- **Média Mensal por CNES Não Priorizado Puro (Controle):** 109.49 cirurgias/mês

---

## 3. Revisão independente e portão corretivo

O piloto processou 600 arquivos (24 UFs × 25 competências), transferiu 2,14 GiB
e gerou painéis balanceados. Isso responde à dúvida de infraestrutura: SIH é
público e operacionalmente manejável neste escopo.

Ainda assim, a revisão encontrou quatro bloqueios antes do C3-03:

1. os 600 manifestos individuais foram montados em memória, mas não persistidos;
   o JSON resume arquivos concluídos sem demonstrar que todos tiveram sucesso;
2. fluxos por residência exigem ler as 27 UFs, pois um residente pode ser
   internado fora das 24 UFs que têm tratados/controles;
3. um município com oferta imediata e reserva foi classificado pela primeira
   linha, em vez de ser marcado como contaminado e excluído;
4. a lista de subgrupos não é a historicização mensal do SIGTAP exigida pelo
   plano.

Assim, os painéis atuais provam viabilidade, cobertura mensal aparente e ordem
de grandeza. Eles **não autorizam ainda** testes de pré-tendência, MDE ou o
congelamento do protocolo. O próximo passo é o prompt corretivo C3-02B; só depois
se executa o C3-03.
