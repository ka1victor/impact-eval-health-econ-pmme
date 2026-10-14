# Guia de conferência manual do IVS

> **Para quê:** conferir sem código, só com navegador e planilha, três
> afirmações da [auditoria 16](16_ivs_2010_oficial_e_arquivo_local.md).<br>
> **Tempo:** cerca de 30 minutos, a maior parte esperando downloads.<br>
> **Valores esperados:** conferidos em 14/10/2026 nos próprios arquivos.

1. **(A)** O IVS que o Ministério da Saúde publica para o PMM-E é o IVS 2010
   oficial do Ipea.
2. **(B)** O arquivo do repositório `data/ivs_ipea_2010_municipios.csv` não é o
   IVS do município. Em cada município ele traz a **última linha de subgrupo
   com IVS preenchido** da mesma base do Ipea:
   - em 4.362 municípios (78%), a de **mulheres negras em área urbana**;
   - quando essa linha vem vazia ou não existe, a linha preenchida anterior:
     mulheres negras (576), mulheres urbanas (484) ou mulheres (142).
3. **(C)** A bolsa segue: IVS até 0,300 → Faixa 3 (R$ 10 mil); de 0,301 a 0,400
   → Faixa 2 (R$ 15 mil); acima de 0,400 → Faixa 1 (R$ 20 mil).

## 1. Ministério da Saúde — o número que define a bolsa

- [ ] Abra a página
  [Provimento Federal — Programa Mais Médicos](https://dadosabertos.saude.gov.br/dataset/provimento-federal-programa-mais-medicos)
  e baixe "Programa Mais Médicos Especialistas – Relação Nominal de Ativos" em
  CSV. Link direto:
  `https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/MaisMedicos/csv/tb_profissionais_ativos_pmme_csv.zip`.
- [ ] Descompacte e importe no Excel pelo assistente de importação:
  - Excel: Dados → De Texto/CSV;
  - delimitador **ponto e vírgula**;
  - codificação **Latin-1 / ISO-8859-1 (Europa Ocidental)**, para não quebrar
    acentos.

  O arquivo tem nomes de médicos, que são dado público. Só interessam as
  colunas `co_ibge`, `municipio`, `ivs`, `categoria_ivs` e `faixa_atracao`.
- [ ] **Atenção:** a coluna `ivs` vem **multiplicada por 10.000**. `3190,0`
  significa 0,319.

## 2. Ipea — o IVS 2010 oficial

O caminho garantido é a base completa da Plataforma IVS:
- **Onde:** [ivs.ipea.gov.br](https://ivs.ipea.gov.br/), seção de bases de
  dados, grupo **"IVS Municipal" → "Base Completa"**.
- **Link direto:**
  `https://ivs.ipea.gov.br/api/cockpit/storage/uploads/databases/basecompletamunicipal.zip`
  (201 MB).
- **Conteúdo:** uma planilha `atlasivs_dadosbrutos_pt_v2.xlsx` de 210 MB, com
  cerca de 340 mil linhas.
- **Como abrir:** use Excel desktop ou LibreOffice. O Google Sheets não abre
  esse tamanho.

A plataforma também tem uma consulta em tabela (`ivs.ipea.gov.br/#/consulta-tabela`),
que deve permitir ver o IVS de um município sem baixar a base. Não consegui
operar essa tela daqui; se ela funcionar para você, é o caminho mais rápido.

- [ ] Na planilha, ative o filtro e filtre:
  - `nivel` = `regiao,uf,rm,municipio`;
  - `ano` = `2010`;
  - `municipio_6digt` = o código do município, por exemplo 261160 para Recife.
- [ ] Sobram várias linhas, uma para cada combinação de `label_cor`,
  `label_sexo` e `label_sit_dom`. O **IVS do município** é a linha
  `Total Cor` / `Total Sexo` / `Total Situação de Domicílio`. Anote a coluna
  `ivs`.
- [ ] Na mesma lista, ache a linha `Negro` / `Mulher` / `Urbano`: é ela que o
  arquivo do repositório copiou nos municípios da tabela abaixo. Ela é a
  última do município na planilha. Quando vem vazia, o arquivo traz a anterior
  preenchida.

## 3. Arquivo do repositório

- [ ] Abra `data/ivs_ipea_2010_municipios.csv` no GitHub
  (`ka1victor/impact-eval-health-econ-pmme`). O GitHub mostra o CSV como
  tabela pesquisável. Busque o município pelo `cod_ibge6` e anote `ivs_2010` e
  `populacao_2010`.

## 4. Tabela de conferência

Os municípios abaixo estão na relação nominal do MS. Os seis últimos ficam a
menos de 0,006 de um corte.

| Município | Código | MS: `ivs` (÷ 10.000) | Ipea, linha Total | Ipea, linha Negro / Mulher / Urbano = arquivo do repositório | Faixa no MS | Faixa pela regra (C) com o IVS oficial | Faixa pela regra (C) com o arquivo do repositório |
|---|---|---:|---:|---:|---|---|---|
| Recife (PE) | 261160 | 3190,0 → 0,319 | 0,319 | 0,364 | FAIXA 2 | Faixa 2 | Faixa 2 |
| Natal (RN) | 240810 | 2920,0 → 0,292 | 0,292 | 0,333 | FAIXA 3 | Faixa 3 | **Faixa 2** ✗ |
| Florianópolis (SC) | 420540 | 2010,0 → 0,201 | 0,201 | 0,237 | FAIXA 3 | Faixa 3 | Faixa 3 |
| Cajazeiras (PB) | 250370 | 2960,0 → 0,296 | 0,296 | 0,302 | FAIXA 3 | Faixa 3 | **Faixa 2** ✗ |
| Teófilo Otoni (MG) | 316860 | 3020,0 → 0,302 | 0,302 | 0,324 | FAIXA 2 | Faixa 2 | Faixa 2 |
| Luziânia (GO) | 521250 | 3960,0 → 0,396 | 0,396 | 0,436 | FAIXA 2 | Faixa 2 | **Faixa 1** ✗ |
| Piripiri (PI) | 220840 | 3990,0 → 0,399 | 0,399 | 0,361 | FAIXA 2 | Faixa 2 | Faixa 2 |
| Itamarandiba (MG) | 313250 | 4010,0 → 0,401 | 0,401 | 0,355 | FAIXA 1 | Faixa 1 | **Faixa 2** ✗ |
| Quixadá (CE) | 231130 | 4010,0 → 0,401 | 0,401 | 0,381 | FAIXA 1 | Faixa 1 | **Faixa 2** ✗ |

- [ ] **(A)** A coluna do MS é igual à linha Total do Ipea em todos.
- [ ] **(B)** Nesses nove municípios, o arquivo do repositório é igual à
  linha Negro / Mulher / Urbano, e não à Total. Os nove estão entre os 4.362 em
  que essa linha tem valor.
- [ ] **(C)** Com o IVS oficial, a faixa do MS sai sempre da regra. Com o
  arquivo do repositório, erra em vários casos, marcados com ✗. Foi isso que
  fez a regra parecer impossível de reproduzir.

Para ver o degrau da regra em mais municípios:
- **No quadro de vagas oficial do ciclo 1** (edital SGTES/MS nº 3/2025; cópia
  no repositório em `data/raw/aquisicao/vagas/2025_ciclo1_chamada1_vagas.xlsx`),
  confira a coluna "FAIXA DE ATRAÇÃO" desses municípios. O link do gov.br
  registrado no manifesto devolveu 404 em 14/10/2026.
- **Na planilha do MS do passo 1**, ordene a coluna `ivs`: a faixa muda entre
  2990,0 (Faixa 3) e 3020,0 (Faixa 2), e entre 4000,0 (Faixa 2) e 4010,0
  (Faixa 1).

## 5. Por que a população do arquivo é baixa

| Município | IBGE, Censo 2010 | Ipea, linha Total, `populacao` | Arquivo do repositório (= linha Negro / Mulher / Urbano) |
|---|---:|---:|---:|
| Florianópolis | 421.240 | 421.240 | 29.095 |
| Recife | 1.537.704 | 1.537.704 | 468.300 |

- [ ] **No IBGE:** SIDRA, tabela 1378 (Censo 2010, população residente),
  município, total. É a população do município inteiro.
- [ ] **No arquivo do repositório:** é a população de mulheres negras em área
  urbana. Nos municípios em que essa linha vem vazia, é a do recorte usado no
  lugar.
- [ ] **Opcional:** a coluna `populacao` da linha Total da base do Ipea, somada
  nos 5.565 municípios, dá 190.755.799, que é exatamente o Censo 2010.

## 6. Se der diferente

| O que aparece | O que provavelmente é |
|---|---|
| valor do MS 100 vezes ou 10.000 vezes maior | o campo `ivs` vem ×10.000 |
| vírgula e ponto trocados | importação sem a configuração regional de vírgula decimal |
| valor do Ipea diferente do da tabela | outra linha: ano 2000 em vez de 2010, ou cor, sexo ou situação diferente de "Total" |
| acentos quebrados no CSV do MS | codificação errada; use Latin-1 |
| a linha Total do Ipea não bate com o MS num município da tabela | aí sim haveria algo novo a investigar. Na conferência de 14/10/2026 bateram 404 de 404 |

A conferência automática completa está em
`output/rdd_bolsa/portao_r1_ivs_oficial.json` e
`output/rdd_bolsa/identificacao_arquivo_local_ivs.json`.
