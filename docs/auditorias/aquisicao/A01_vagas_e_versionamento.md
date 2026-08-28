# Relatório de Auditoria A01 — Universo de Vagas e Versionamento Público do PMM-E

> **Data da auditoria:** 27 de agosto de 2026  
> **Agente responsável:** Agente A01 — Universo de Vagas e Versionamento Público  
> **Status:** Concluído com sucesso (todas as fontes recuperadas byte a byte e auditadas)  
> **Não contém:** estimação de efeitos causais ou imputação de identificadores sintéticos.

---

## 1. Resumo Executivo e Principais Conclusões

1. **Recuperação Integral das Fontes de 2025 (Resolução de Links Quebrados):**
   - Os dois arquivos da 1ª chamada de 2025 cujos links haviam falhado na Auditoria 02 (`2025_ciclo1_chamada1_vagas.xlsx` e `2025_ciclo1_chamada1_alocacao_retificada.xlsx`) foram **recuperados byte a byte com sucesso** diretamente dos endpoints oficiais do Ministério da Saúde.
   - **Diagnóstico da falha anterior:** A URL histórica catalogada utilizava o slug longo `chamamento-publico-sgtes-ms-no-3-2025-projeto-mais-medicos-especialistas/`, enquanto o endpoint canônico ativo do portal do MS adota `chamamento-publico-sgtes-ms-no-3-2025-pmm-e/`. A correção da rota permitiu o download íntegro dos 129.157 bytes do quadro de vagas original e dos 165.047 bytes da alocação retificada.
   - Foram adicionalmente localizados e preservados outros 6 arquivos públicos oficiais inéditos, totalizando **19 planilhas auditadas** (8 novas em `data/raw/aquisicao/vagas/` e 11 preservadas em `data/raw/pmm_e/`).

2. **Inexistência de `id_vaga` Administrativo e Limitação da Unidade:**
   - **Nenhum dos 19 documentos públicos auditados contém um identificador administrativo unívoco e estável de vaga (`id_vaga`).**
   - Não se deve inventar códigos artificiais rotulados como dados primários. Para auditoria técnica entre versões, adota-se a formulação explícita de `chave_candidata = CNES_7digitos + "_" + CURSO_NORMALIZADO`.
   - A `chave_candidata` identifica uma **célula agregada de oferta** (par estabelecimento de saúde e especialidade/curso), e não uma vaga física individual. Nos quadros de vagas ofertadas, atinge-se 100% de unicidade entre as linhas (zero colisões internas de linhas no quadro). Quando uma célula oferta múltiplas vagas (ex.: 2 ou 3 vagas no mesmo hospital e especialidade), a chave não separa cada vaga nem permite acompanhar sua ocupação de forma desagregada.
   - Nas listas de candidatos e homologados, ocorrem colisões esperadas decorrentes de múltiplos candidatos disputando a mesma célula/especialidade e concorrência por cotas.

3. **Denominador de Vagas e Proibição de Soma Ingênua de Publicações:**
   - **Não existe um denominador público cumulativo obtido pela soma linear de planilhas.**
   - Cada publicação reflete uma fotografia fechada de um momento específico do chamamento. Somar chamadas subsequentes gera dupla-contagem severa: a 2ª chamada do Ciclo 1 e a 2ª chamada do Ciclo 2 ofertaram exclusivamente **vagas em cadastro de reserva** (muitas reapresentadas de chamadas anteriores).
   - O denominador confiável de vagas ofertadas deve ser fixado **estritamente por ciclo e por versão de quadro**, conforme inventariado abaixo.

---

## 2. Inventário de Documentos e Recuperação de Fontes

| ID do Documento | Arquivo | Ciclo / Chamada | Data Publicação | Tamanho (Bytes) | SHA-256 | Status de Aquisição |
|---|---|---|---|---:|---|---|
| `vagas_2025_c1_ch1_original` | `2025_ciclo1_chamada1_vagas.xlsx` | Ciclo 1, Ch 1 | 24/07/2025 | 129.157 | `51c6807f6bc2efa252b5236d89c5384ae484c4d47c8b65d4161c3facbfebe304` | Recuperado byte a byte oficial (corrigido link) |
| `alocacao_2025_c1_ch1_retificada` | `2025_ciclo1_chamada1_alocacao_retificada.xlsx` | Ciclo 1, Ch 1 | 10/09/2025 | 165.047 | `0acfba2a89e0c269b754c0ca0fd5a2426be511f88a3c1a934a41345f8c9ffd0c` | Recuperado byte a byte oficial (corrigido link) |
| `alocacao_2025_c1_ch1_retificada_subjudice` | `2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx` | Ciclo 1, Ch 1 | 19/09/2025 | 165.250 | `bffd60b79b1ad1352d8bb636192311eecab484818da01fce8b821dde58793bec` | Recuperado byte a byte oficial |
| `realocacao_2025_c1_ch1_retificado` | `2025_ciclo1_chamada1_realocacao_retificado.xlsx` | Ciclo 1, Ch 1 | 10/09/2025 | 15.559 | `7c31cb441b8668eca0c06a6c6a648c731e26d1f14162fe071fd9695ebfe89b86` | Recuperado byte a byte oficial |
| `homologados_2025_c1` | `2025_ciclo1_chamada1_homologados.xlsx` | Ciclo 1, Ch 1 | 29/09/2025 | 40.259 | `4f4d0d3c621c0c540002aae8b6f453665dcad33be5856516ce299ad9b2484d9b` | Preservado em `data/raw/pmm_e/` |
| `vagas_alocados_2025_c1_ch2` | `2025_ciclo1_chamada2_vagas_e_alocados.xlsx` | Ciclo 1, Ch 2 | 29/09/2025 | 155.827 | `f1b8f7533cb13d8aba21d1100ab957e6accac52532fb8235e1b4231343a0588c` | Preservado em `data/raw/pmm_e/` |
| `classificacao_2025_c1_ch2` | `2025_ciclo1_chamada2_classificacao_final.xlsx` | Ciclo 1, Ch 2 | 14/11/2025 | 86.076 | `5c73a99847708b2749019c634f661771b28c88cb5421e9672e44704e62103e85` | Preservado em `data/raw/pmm_e/` |
| `homologados_2025_c1_ch2` | `2025_ciclo1_chamada2_homologados.xlsx` | Ciclo 1, Ch 2 | 24/11/2025 | 55.034 | `4e85cfe45b2e5e1f7ebef78aa5dc90ba61b7adc5f7046f43a5066803f603e147` | Preservado em `data/raw/pmm_e/` |
| `vagas_2026_c2_ch1_original` | `2026_ciclo2_chamada1_vagas_e_servicos_original.xlsx` | Ciclo 2, Ch 1 | 03/02/2026 | 337.149 | `cddad12d958963e29d3b9912814990c90a9220ba724f4657d9181cc1b9e3e049` | Recuperado byte a byte oficial |
| `vagas_2026_c2_ch1_retificado_servicos` | `2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx` | Ciclo 2, Ch 1 | 13/02/2026 | 157.862 | `3393473cfe5c3163056a0314c3cad4779e8c9c957ba9ea714c29d6a2c77697f8` | Recuperado byte a byte oficial |
| `vagas_2026_c2_ch1_retificada` | `2026_ciclo2_chamada1_vagas_retificadas.xlsx` | Ciclo 2, Ch 1 | 19/03/2026 | 153.185 | `a47b0b0204fe80bdd15249bcb8e4b6686d8bc9b981c277a6c240f4d2ea97425b` | Preservado em `data/raw/pmm_e/` |
| `resultado_2026_c2_ch1_remanescentes` | `2026_ciclo2_chamada1_resultado_final_remanescentes.xlsx` | Ciclo 2, Ch 1 | 05/05/2026 | 17.548 | `db39d51f9163fd8deedc8727ced37bf3fcdf19b4a6966d91a396e09f5f2a26e6` | Preservado em `data/raw/pmm_e/` |
| `vagas_2026_c2_ch2` | `2026_ciclo2_chamada2_vagas.xlsx` | Ciclo 2, Ch 2 | 16/04/2026 | 111.673 | `4815e1558b515d4cdabf245b45e24062ab2e9531abd657b4f24f68bb45b3d3a4` | Preservado em `data/raw/pmm_e/` |
| `resultado_2026_c2_ch2` | `2026_ciclo2_chamada2_resultado_final.xlsx` | Ciclo 2, Ch 2 | 28/05/2026 | 111.857 | `8690d6fc381692fc20c59ae077ac8b80ca1ce27dd03d27fd8e1ef17c75abc85f` | Preservado em `data/raw/pmm_e/` |
| `vagas_2026_c3_gestores_original` | `2026_ciclo3_gestores_quadro_vagas_original.xlsx` | Ciclo 3, Gestores | 15/05/2026 | 986.492 | `3c77f7dc86f02267b9db0df0ccb97ffe84fcdc756c300f95b355e73d65cbe6f1` | Recuperado byte a byte oficial |
| `adesao_gestores_2026_c3_final` | `2026_ciclo3_adesao_gestores_resultado_final.xlsx` | Ciclo 3, Gestores | 15/07/2026 | 495.019 | `0c07d4c972d14bac8ae9b8c99d5edac32f9ea76996ec82e92198065ac63b1f74` | Preservado em `data/raw/pmm_e/` |
| `vagas_2026_c3_medicos_original` | `2026_ciclo3_chamada1_vagas_original.xlsx` | Ciclo 3, Médicos | 16/07/2026 | 236.751 | `417eb9a459df88e4600992237c4b2dae5e9315e933eeaada7d8d6eb3faf96dda` | Recuperado byte a byte oficial |
| `vagas_2026_c3_retificada` | `2026_ciclo3_chamada1_vagas_retificadas.xlsx` | Ciclo 3, Médicos | 24/07/2026 | 244.948 | `6bc07f48d0eaac37936fc827ebdefd12fb7bf2be86dc26f64a08e1f5b57f5371` | Preservado em `data/raw/pmm_e/` |
| `resultado_2026_c3_sub_judice` | `2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx` | Ciclo 3, Médicos | 25/08/2026 | 393.041 | `d74f268bb7192c80a02c94e54eb4407e60a0923ad7d0310c2c6b432b3dbbb6ee` | Preservado em `data/raw/pmm_e/` |

---

## 3. Tabela Comparativa de Denominador de Vagas por Ciclo e Versão

A tabela a seguir consolida a auditoria das vagas em cada documento oficial, distinguindo **vagas de preenchimento imediato** e **vagas em cadastro de reserva**, além da amplitude territorial e cobertura por faixas.

| Ciclo e Chamada | Documento e Versão | Data | Linhas Dados | Vagas Imediatas | Vagas Reserva | Total Vagas | Municípios Únicos | CNES Únicos | Cursos | Distribuição de Faixas |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Ciclo 1, Chamada 1** | Quadro Original | 24/07/2025 | 1.295 | **678** | **1.145** | **1.823** | 368 | 460 | 16 | F1: 291, F2: 465, F3: 539 |
| **Ciclo 1, Chamada 1** | Alocação Retificada | 10/09/2025 | 1.671 | — | — | — | 267 | 336 | 16 | — |
| **Ciclo 1, Chamada 1** | Homologados Retificados | 29/09/2025 | 316 | — | — | — | 149 | 178 | 16 | F1: 88, F2: 139, F3: 89 |
| **Ciclo 1, Chamada 2** | Quadro Vagas Reserva | 29/09/2025 | 1.762 | **0** | **2.896** | **2.896** | 507 | 638 | 14 | F1: 281, F2: 551, F3: 930 |
| **Ciclo 1, Chamada 2** | Classificação Final | 14/11/2025 | 757 | — | — | — | — | 226 | 14 | — |
| **Ciclo 1, Chamada 2** | Homologados Final | 24/11/2025 | 581 | — | — | — | — | 253 | 16 | — |
| **Ciclo 2, Chamada 1** | Quadro Original | 03/02/2026 | 1.550 | **899** | **1.998** | **2.897** | 455 | 686 | 16 | F1: 259, F2: 478, F3: 813 |
| **Ciclo 2, Chamada 1** | Quadro Retificado (Serviços) | 13/02/2026 | 1.547 | **1.206** | **1.686** | **2.892** | 454 | 685 | 16 | F1: 258, F2: 478, F3: 811 |
| **Ciclo 2, Chamada 1** | Quadro Retificado Final | 19/03/2026 | 1.547 | **1.836** | **1.053** | **2.889** | 454 | 685 | 16 | F1: 258, F2: 478, F3: 811 |
| **Ciclo 2, Chamada 1** | Remanescentes Final | 05/05/2026 | 9 | — | — | — | 7 | 7 | 3 | — |
| **Ciclo 2, Chamada 2** | Quadro 2ª Chamada | 16/04/2026 | 1.039 | **0** | **1.992** | **1.992** | 369 | 532 | 16 | F1: 140, F2: 282, F3: 617 |
| **Ciclo 2, Chamada 2** | Resultado Final | 28/05/2026 | 1.053 | — | — | — | 193 | 285 | 15 | — |
| **Ciclo 3, Gestores** | Proposta Preliminar | 15/05/2026 | 17.543 | — | — | **52.265** | 2.699 | 5.623 | 24 | — |
| **Ciclo 3, Gestores** | Resultado Adesão Final | 15/07/2026 | 5.534 | **1.136** | **3.995** | **5.131** | 1.179 | 2.218 | 24 | (Priorizadas CIB/MS) |
| **Ciclo 3, Médicos** | Quadro Original | 16/07/2026 | 2.293 | **1.136** | **3.995** | **5.131** | 748 | 1.262 | 24 | F1: 463, F2: 787, F3: 1.043 |
| **Ciclo 3, Médicos** | Quadro Retificado | 24/07/2026 | 2.293 | **1.132** | **3.999** | **5.131** | 748 | 1.262 | 24 | F1: 463, F2: 787, F3: 1.043 |
| **Ciclo 3, Médicos** | Resultado Sub Judice | 25/08/2026 | 4.532 | — | — | — | 499 | 774 | 24 | — |

---

## 4. Auditoria de Chaves Técnicas e Colisões

### 4.1 Definição da `chave_candidata`
Como não existe `id_vaga` administrativo nos documentos oficiais, a auditoria construiu e testou a seguinte formulação determinística:

$$\text{chave\_candidata} = \text{CNES\_7digitos} + \text{"\_"} + \text{CURSO\_NORMALIZADO}$$
$$\text{chave\_candidata\_ibge} = \text{IBGE\_6digitos} + \text{"\_"} + \text{CNES\_7digitos} + \text{"\_"} + \text{CURSO\_NORMALIZADO}$$

Onde a normalização de curso remove pontuação, acentuação, caixa alta/baixa, prefixos numéricos ordinais (ex: `01.`, `01 -`) e termos padronizados como `APRIMORAMENTO EM`.

### 4.2 Desempenho e Colisões
1. **Quadros de Oferta de Vagas (Universo de Vagas):**
   - **Taxa de unicidade de 100%:** Em todos os quadros de oferta de vagas auditados (Ciclo 1 Ch1, Ciclo 1 Ch2, Ciclo 2 Ch1, Ciclo 2 Ch2, Ciclo 3 Gestores e Ciclo 3 Médicos), o número de linhas de dados é exatamente igual ao número de `chave_candidata` únicas.
   - **Zero colisões internas:** Não existem duas linhas no mesmo quadro de vagas compartilhando o mesmo par (CNES, Curso).
   - O código IBGE municipal é 100% funcionalmente dependente do CNES (não há divergência de município para um mesmo CNES dentro de cada quadro).

2. **Listas de Candidatos, Alocações e Homologações:**
   - Ocorrem colisões esperadas de chave porque múltiplos candidatos disputam a mesma especialidade no mesmo estabelecimento de saúde.
   - Por exemplo, na Alocação Retificada do Ciclo 1 Ch1, há 1.671 inscrições distribuídas em 636 chaves únicas (370 chaves com 2 ou mais candidatos classificados).
   - Na lista de Homologados do Ciclo 1 Ch1, 316 profissionais homologados ocupam 268 chaves únicas (em 39 estabelecimentos houve mais de um especialista homologado no mesmo curso).

---

## 5. Dinâmica de Versionamento e Transições entre Publicações

### 5.1 Ciclo 1 (2025)
- **Chamada 1:** O quadro original de 24/07/2025 ofertou **678 vagas imediatas e 1.145 em cadastro de reserva** (total 1.823 vagas em 1.295 estabelecimentos/cursos).
- **Retificações:** Em 10/09/2025, o Ministério publicou o Quadro 1 (alocação retificada com 1.671 candidatos para 636 chaves) e o Quadro 2 (proposta de realocação para 59 profissionais que haviam selecionado serviços cuja gestão desistiu ou que apresentavam incompatibilidade técnica).
- **Transição Ch1 → Ch2:** A 2ª chamada (29/09/2025) não ofertou novas vagas imediatas, publicando apenas **2.896 vagas em cadastro de reserva** em 1.762 células de oferta CNES–curso.
  - Das 1.762 células, **929 eram células de oferta reapresentadas da 1ª chamada** e **833 foram novas células de oferta adicionadas ao cadastro de reserva** (totalizando 2.896 vagas em reserva somadas).

### 5.2 Ciclo 2 (2026)
- **Quadro Original (03/02/2026):** Ofertou 899 vagas imediatas e 1.998 em reserva (total 2.897 vagas em 1.550 chaves).
- **Quadro Retificado Intermediário (13/02/2026):** Ajustou para 1.206 imediatas e 1.686 reserva (total 2.892 vagas em 1.547 chaves).
- **Quadro Retificado Final (19/03/2026):** Operou uma **conversão massiva de modalidade**: 937 vagas de cadastro de reserva foram promovidas para vagas imediatas, resultando em **1.836 vagas imediatas e 1.053 de reserva** (total 2.889 vagas em 1.547 chaves).
  - Apenas 3 chaves do quadro original foram suprimidas na retificação final.
- **Transição Ch1 → Ch2:** A 2ª chamada do 2º ciclo (16/04/2026) ofertou estritamente **1.992 vagas em cadastro de reserva** em 1.039 chaves (todas as 1.039 chaves eram subconjunto das 1.547 chaves da 1ª chamada).

### 5.3 Ciclo 3 (2026)
- **Adesão de Gestores (Chamamento nº 5/2026):** Os entes federados cadastraram propostas preliminares para 52.265 vagas em 17.543 linhas.
- **Resultado da Adesão dos Gestores (15/07/2026):** Após análise técnica da SGTES e pactuação em CIB, o MS homologou **5.131 vagas priorizadas** (1.136 imediatas e 3.995 reserva), distribuídas em 5.534 linhas de propostas.
- **Oferta aos Médicos (Chamamento nº 28/2026):**
  - O quadro original (16/07/2026) disponibilizou exatamente as **5.131 vagas priorizadas**, agregadas em 2.293 estabelecimentos/cursos.
  - A retificação de 24/07/2026 manteve o total de 5.131 vagas e 2.293 chaves, alterando a modalidade de 4 vagas (de imediatas para reserva): totalizando **1.132 vagas imediatas e 3.999 vagas em cadastro de reserva**.

---

## 6. Diagnóstico Metodológico e Recomendações

1. **Denominador Analítico Válido:**
   - O denominador de vagas ofertadas é determinístico **apenas quando fixado na versão final de cada chamada**.
   - Para o Ciclo 1 Ch1: 678 vagas imediatas (1.295 chaves).
   - Para o Ciclo 2 Ch1 (versão retificada de 19/03/2026): 1.836 vagas imediatas (1.547 chaves).
   - Para o Ciclo 3 Ch1 (versão retificada de 24/07/2026): 1.132 vagas imediatas (2.293 chaves).
   - **Regra de ouro:** Nunca somar chamadas ou versões preliminares e retificadas.

2. **Rastreabilidade sem `id_vaga`:**
   - Na ausência de `id_vaga` gerado pelo sistema SGP/DGEPSS, qualquer vinculação longitudinal entre a publicação da vaga, a escolha do candidato, a homologação e o registro no CNES depende da tripla chave construída `(CNES, CURSO_NORMALIZADO, CICLO_CHAMADA)`.
   - Se houver necessidade de distinguir vagas múltiplas na mesma especialidade e estabelecimento (por exemplo, 3 vagas de Anestesiologia no mesmo hospital), os dados públicos agregam a quantidade em uma única linha e não permitem saber qual vaga específica foi preenchida ou abandonada. Isso confirma a necessidade dos **pedidos administrativos via LAI** descritos na Auditoria 02.

---

## 7. Manifesto de Arquivos e Reprodutibilidade

Todos os scripts e artefatos de saída desta auditoria são determinísticos e idempotentes:
- **Script mestre:** `scripts/aquisicao/a01_adquirir_vagas.py`
- **Manifesto de fontes:** `output/aquisicao/a01_manifesto_vagas.json`
- **Inventário de versões:** `output/aquisicao/a01_inventario_versoes.json`
- **Diretório de brutos adquiridos:** `data/raw/aquisicao/vagas/` (sem alteração nos dados brutos pré-existentes em `data/raw/pmm_e/` ou `data/`).

---
