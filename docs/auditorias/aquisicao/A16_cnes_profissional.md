# A16 — Portão G5: CNES profissional mensal (médico × mês, com registro do conselho)

> **Data:** 19/10/2026.<br>
> **Tarefa:** portão G5 do plano
> [`06_execucao/51`](../../06_execucao/51_plano_perguntas_reformuladas.md)
> (T4.0), insumo de P4 (T4.1–T4.3) e dos outcomes CNES do T6.2.<br>
> **Script:** [`scripts/aquisicao/a16_cnes_profissional_mensal.py`](../../../scripts/aquisicao/a16_cnes_profissional_mensal.py).<br>
> **Números:** todos os números deste portão estão no resumo gerado pelo
> script, [`output/aquisicao/cnes_profissional/a16_resumo.md`](../../../output/aquisicao/cnes_profissional/a16_resumo.md),
> em [`a16_cobertura_mensal.csv`](../../../output/aquisicao/cnes_profissional/a16_cobertura_mensal.csv),
> no manifesto [`a16_manifesto_cnes_profissional.json`](../../../output/aquisicao/cnes_profissional/a16_manifesto_cnes_profissional.json)
> e em [`output/rdd_bolsa/G5_resumo.json`](../../../output/rdd_bolsa/G5_resumo.json).
> Este texto não repete contagens à mão; só cita os parâmetros fixados no
> script (competências e limiares).<br>
> **Cegamento:** portão, não estimação. Nada foi calculado antes ou depois da
> entrada no PMM-E, por IVS, corte, faixa, ciclo ou tratamento. O script não
> lê IVS (o teste `test_script_nao_le_ivs_nem_quebra_por_corte` confere o
> código-fonte). Só há diagnósticos de cobertura por mês, com todos os médicos
> ligados juntos.

**Veredito do portão: `VIAVEL_PARCIAL`** (o mesmo de `G5_resumo.json`; o
teste confere). O painel existe para todas as competências planejadas, com
registro do conselho e horas em quase todo vínculo, e a ligação da X1 foi
reproduzida sem diferença. O critério que não passou é o C5: o número do CRM
gravado no vínculo muda ao longo do tempo para uma parte dos médicos ligados.
O código do profissional no CNES não muda. Detalhes na seção 6.

## 1. A pergunta do portão

Dá para montar um painel médico × mês, de 202406 a 202608 (nunca ≥ 202609),
com vínculos, estabelecimentos, municípios, CBO e horas (ambulatoriais,
hospitalares e outras; vínculo SUS e não SUS), para:
- (a) os médicos do PMM-E ligados ao CNES na X1;
- (b) os candidatos que o G1 vier a ligar?

A chave tem de ser pseudônima e permitir juntar o G1 depois, sem novo
download.

## 2. Fonte e tabelas

- **Fonte:** base completa mensal do CNES (DATASUS/MS),
  `BASE_DE_DADOS_CNES_AAAAMM.ZIP`, pelo servlet HTTPS
  `https://cnes.datasus.gov.br/EstatisticasServlet?path=...` com o `Referer`
  da página de downloads. É o caminho do a09 e da X1; o FTP do DATASUS é
  bloqueado pelo proxy deste ambiente.
- **Tabelas lidas de cada ZIP:**

| Tabela | Colunas | Para quê |
|---|---|---|
| `tbCargaHorariaSus` | `CO_UNIDADE`, `CO_PROFISSIONAL_SUS`, `CO_CBO`, `TP_SUS_NAO_SUS`, `IND_VINCULACAO`, `TP_TERCEIRO_SIH`, `TP_PRECEPTOR`, `TP_RESIDENTE`, `QT_CARGA_HORARIA_AMBULATORIAL`, `QT_CARGA_HOR_HOSP_SUS`, `QT_CARGA_HORARIA_OUTROS`, `CO_CONSELHO_CLASSE`, `NU_REGISTRO`, `SG_UF_CRM` | o vínculo (profissional × estabelecimento × CBO), as horas e o registro do conselho |
| `tbEstabelecimento` | `CO_UNIDADE`, `CO_CNES`, `CO_MUNICIPIO_GESTOR`, `TP_GESTAO`, `TP_UNIDADE`, `CO_NATUREZA_JUR` | CNES, município (a chave do a09), gestão, tipo de unidade e natureza jurídica |
| `tbDadosProfissionalSus` | `CO_PROFISSIONAL_SUS`, `NO_PROFISSIONAL` | só nas seis competências da X1 e só dos profissionais cujo registro é um CRM das listas do PMM-E: o nome normalizado, para refazer a ligação da X1 com a mesma regra; fica no cache privado |
| `tbOrgaoEmissor` (202608) | código e descrição | o código do CRM no campo `CO_CONSELHO_CLASSE`, pela regra da X1 |

- **Filtro:** só vínculos com CBO médica, pelos prefixos do a09 (2251, 2252,
  2253 e a família 2231 do CNES). Sem filtro de `TP_SUS_NAO_SUS`, vinculação
  ou tipo de unidade.
- **Por que baixar de novo.** O cache do a09 guarda as horas, mas não o
  registro do conselho. O cache da X1 guarda o registro, mas só em seis
  competências e sem horas. Nenhum dos dois serve sozinho, e os dois ficam
  fora do controle de versão, em worktrees de outros agentes. O a16 baixa as 27
  competências mensais e guarda, num cache privado, os vínculos médicos com
  registro e horas. Com isso, chaves novas (G1) entram sem baixar nada.
- **Conferência com o a09.** Para cada competência, o SHA-256 do ZIP é
  comparado com o do manifesto do a09. Quando é o mesmo arquivo, a contagem
  de vínculos médicos tem de ser idêntica (fail closed). Quando o DATASUS
  republicou o arquivo, a diferença fica registrada.
- **Competência que falha** (download, integridade ou extração) fica sem
  linhas, com o motivo no manifesto. Nada é interpolado nem copiado de outro
  mês.

## 3. Chave pseudônima e como juntar o G1

- `id_prof` = `g5p_` + a ordem do SHA-256 de `CO_PROFISSIONAL_SUS` dentro da
  união das chaves de uma consolidação, calculada só em memória. É a convenção
  do `id_medico` da X1.
- Nome, CPF, CNS, CRM, UF do CRM, `CO_PROFISSIONAL_SUS` e `CO_UNIDADE` não
  saem de `output/aquisicao/cnes_profissional/cache_privado/`, que fica fora
  do controle de versão.
- `chaves_origem.parquet` liga `id_prof` ao pseudônimo de origem:
  `id_medico` da X1, uma linha por regra de ligação (`literal_doc45` e
  `d1_pos_hoc`). Um mesmo médico ligado nas duas regras tem o mesmo `id_prof`.
- **G1.** O G1 grava, no seu próprio cache fora do controle de versão, um
  parquet com `origem`, `id_externo` (o pseudônimo do candidato) e
  `co_profissional_sus`. Basta rodar:

  ```bash
  python3 scripts/aquisicao/a16_cnes_profissional_mensal.py --etapa consolidar --chaves-extra <arquivo>
  ```

  O painel ganha as chaves do G1 sem novo download.
- O `id_prof` é renumerado a cada consolidação. Painel, chaves e cobertura
  saem juntos e só se juntam entre si; não junte saídas de consolidações
  diferentes pelo `id_prof`.
- **O pseudônimo é fraco.** CNES, CBO e município de cada vínculo, cruzados
  com o CNES público, reidentificam o médico. O painel serve à análise dentro
  do projeto, não à publicação de microdado.

## 4. Saídas

| Saída | Conteúdo | Git |
|---|---|---|
| `output/aquisicao/cnes_profissional/painel_vinculo_mes.parquet` | uma linha por vínculo médico do profissional na competência: `co_cnes`, `co_municipio`, `co_cbo`, `tp_sus_nao_sus`, vinculação, preceptor, residente, as três cargas horárias, gestão, tipo de unidade, natureza jurídica | sim |
| `output/aquisicao/cnes_profissional/painel_medico_mes.parquet` | `id_prof` × competência obtida, balanceado: vínculos (SUS, não SUS, outro), estabelecimentos, municípios, CBO, horas por campo e tipo de vínculo, horas totais, vínculos com hora ausente | sim |
| `output/aquisicao/cnes_profissional/chaves_origem.parquet` | `id_prof` ↔ pseudônimo de origem e regra de ligação | sim |
| `output/aquisicao/cnes_profissional/a16_cobertura_mensal.csv` | por origem, regra e competência: profissionais com vínculo médico e estabilidade da chave | sim |
| `output/aquisicao/cnes_profissional/a16_resumo.md` | tabelas geradas: critérios, competências, cobertura | sim |
| `output/aquisicao/cnes_profissional/a16_manifesto_cnes_profissional.json` | fonte, tabelas, por competência URL, data, SHA-256, tamanho, tempo de download e de extração, colunas, contagens, conferência com o a09; entradas com hash; saídas com hash; reprodução da X1; critérios e veredito | sim |
| `output/rdd_bolsa/G5_resumo.json` | veredito do portão, status por critério, volume baixado, cobertura por mês | sim |
| `output/aquisicao/cnes_profissional/cache_privado/` | vínculos médicos com registro e código do profissional por competência, nomes do alvo, `tbOrgaoEmissor`, metadados; ZIPs transitórios | não |

Definições do painel médico × mês:

| Coluna | Definição |
|---|---|
| `tem_vinculo_medico` | 1 se o profissional tem ao menos um vínculo com CBO médica na competência |
| `n_vinculos`, `n_vinculos_sus`, `n_vinculos_nao_sus`, `n_vinculos_tp_sus_outro` | linhas de `tbCargaHorariaSus`; por `TP_SUS_NAO_SUS` = `S`, `N` ou outro valor |
| `n_estabelecimentos`, `n_municipios`, `n_cbo` | distintos entre os vínculos médicos |
| `horas_amb_vinc_sus`, `horas_hosp_vinc_sus`, `horas_outros_vinc_sus` | soma de `QT_CARGA_HORARIA_AMBULATORIAL`, `QT_CARGA_HOR_HOSP_SUS` e `QT_CARGA_HORARIA_OUTROS` nos vínculos SUS; ausente se algum deles tem o campo vazio |
| `horas_*_vinc_nao_sus` | o mesmo nos vínculos não SUS |
| `horas_totais` | os três campos em todos os vínculos; ausente se algum vínculo tem algum campo vazio |
| `n_vinculos_horas_ausentes` | vínculos com algum dos três campos vazio |

Regras:
- hora vazia é ausente, nunca zero (regra do a09);
- zero só existe numa competência lida com sucesso, para quem não tem vínculo
  médico nela;
- "sem vínculo médico" quer dizer sem vínculo com CBO médica no cadastro. Não
  quer dizer que o médico parou de trabalhar: vínculos em CBO não médica (por
  exemplo, gestão) ficam fora.

## 5. Critérios do veredito (fixados no script antes da consolidação)

| Critério | ok | parcial | falha |
|---|---|---|---|
| C1 competências | 27 de 27 obtidas | ≥ 24, com 202406 e 202608 | menos |
| C2 registro por vínculo | colunas do registro em toda competência e fração de vínculos médicos com `NU_REGISTRO` ≥ 0,99 em cada uma | colunas presentes, fração menor | coluna ausente |
| C3 horas | três cargas e `TP_SUS_NAO_SUS` em toda competência e fração de vínculos com hora ausente ≤ 0,001 em cada uma | colunas presentes, fração maior | coluna ausente |
| C4 reprodução da X1 | a ligação refeita do cache reproduz `X1_medicos.parquet` (ligado, etapa e motivo) em 100% dos registros, nas duas regras | diferenças | — |
| C5 estabilidade da chave | em toda competência, entre os ligados pela regra D1 com vínculo médico, fração com vínculo que traz o CRM da lista ≥ 0,95, e fração de registros CRM+UF que aparecem em outro código de profissional ≤ 0,01 | senão | — |

Veredito: `VIAVEL` se todos ok; `INVIAVEL` se C1, C2 ou C3 em falha;
`VIAVEL_PARCIAL` nos demais casos. O teste recalcula o veredito a partir do
manifesto e da cobertura.

## 6. Resultado da execução de 19/10/2026

Contagens, frações e hashes estão no resumo gerado e no manifesto. Aqui fica
só o que eles mostram.

- **Teste de viabilidade.** Antes do download completo, 202406 e 202608 foram
  baixadas e extraídas. Os dois ZIPs tinham o mesmo SHA-256 do a09, e a
  extração reproduziu a contagem de vínculos médicos do a09. As duas
  competências entraram no painel com o ZIP do teste: o tempo de download
  delas não está no manifesto (`segundos_download` nulo, com nota).
- **C1, competências: ok.** Todas as 27 competências mensais foram obtidas.
  Em todas, o ZIP é o mesmo do a09 (SHA-256 igual) e a contagem de vínculos
  médicos é idêntica. Nenhum ZIP ficou em disco. O volume total e a soma dos
  tempos de download por conexão estão em `G5_resumo.json`, campo `volume`.
  Os downloads correram em paralelo; o servidor derrubou algumas conexões, e
  a nova tentativa automática completou todas.
- **C2, registro por vínculo: ok.** `CO_CONSELHO_CLASSE`, `NU_REGISTRO` e
  `SG_UF_CRM` existem em todas as competências. Quase todo vínculo médico tem
  número de registro; o código do CRM, lido da `tbOrgaoEmissor`, é o mesmo da
  X1.
- **C3, horas: ok.** As três cargas horárias e `TP_SUS_NAO_SUS` existem em
  todas as competências. Pouquíssimos vínculos médicos têm algum campo de
  horas vazio, e nenhum deles é de médico do painel.
- **C4, reprodução da X1: ok.** A ligação refeita com a função `ligar` da X1,
  sobre o cache do a16 nas seis competências da X1, é idêntica a
  `X1_medicos.parquet` em todos os registros, nas duas regras (ligado, etapa e
  motivo).
- **C5, estabilidade da chave: parcial.**
  - O registro CRM+UF da lista nunca aparece em outro código de profissional,
    em nenhuma competência. O código do profissional (`CO_PROFISSIONAL_SUS`)
    se mantém: nenhum registro "migra" de pessoa.
  - O que falha é a primeira parte do critério. Nas competências mais
    antigas, uma parte dos médicos ligados que têm vínculo médico só aparece
    com **outro número de CRM**, sob o mesmo código de profissional. Nenhum
    deles está sem registro. A parte com outro número cai mês a mês; a
    fração com o CRM da lista só alcança o limiar de 0,95 no segundo
    semestre de 2025 (tabela no resumo).
  - Leitura provável: o médico se inscreve no CRM da UF do posto e o cadastro
    passa a trazer o número novo. As listas do PMM-E trazem só o número
    atual. É um padrão do calendário, com todos os médicos juntos; não foi
    olhado em relação à data de entrada de cada um.
  - Consequência prática: o **CRM não serve de chave longitudinal**; o
    `CO_PROFISSIONAL_SUS` serve. O painel usa o código do profissional, e a
    ligação da X1 (que procura o CRM em seis competências) continua a porta
    de entrada. O G1 deve seguir a mesma regra: ligar o candidato pelo CRM
    no CNES pré e acompanhar pelo código do profissional.
- **Cobertura.** Quase todos os médicos ligados têm vínculo médico em cada
  competência; a fração sobe ao longo do período. A tabela por competência
  está no resumo e em `a16_cobertura_mensal.csv`, sem quebra por ciclo,
  faixa ou entrada.

## 7. O que P4 e T6.2 podem usar

**P4 (T4.1–T4.3) pode contar com:**
- painel médico × mês balanceado, de 202406 a 202608, para todos os médicos
  ligados na X1, nas duas regras de ligação;
- por médico e mês: vínculos, estabelecimentos, municípios e CBO; horas
  ambulatoriais, hospitalares e outras, separadas em vínculos SUS e não SUS;
- por vínculo: CNES, município, CBO, tipo de vínculo, gestão, tipo de
  unidade e natureza jurídica do estabelecimento, que dão a separação entre
  público e privado;
- a ponte `id_prof` ↔ `id_medico` (X1). O mês de início, o ciclo e o
  município do posto vêm da X1 e das listas, no protocolo 54, não deste
  painel.

**P4 deve tratar como limite:**
- só vínculos com CBO médica (225x e 2231); outras ocupações do mesmo
  médico ficam fora;
- vínculo e carga horária são cadastrados, não presença nem horas
  realizadas;
- os médicos não ligados na X1 não estão no painel;
- o pré-período começa em 202406. Para os médicos do ciclo 1, isso dá poucos
  meses antes da entrada. Doze meses antes da entrada só existem para quem
  entrou a partir de 202506. O protocolo 54 deve fixar a janela com isso em
  mente, antes de abrir os dados.

**T6.2 (RD do candidato) pode contar com:**
- a mesma estrutura e as mesmas variáveis, quando o G1 entregar as chaves dos
  candidatos (`--chaves-extra`, sem novo download).

**T6.2 depende ainda de:**
- G1: ligação dos candidatos não alocados;
- G2: reconstrução do mecanismo de alocação.

Este portão não substitui nenhum dos dois.

## 8. Reprodução

```bash
python3 scripts/aquisicao/a16_cnes_profissional_mensal.py                     # padrão: verificar (sem rede, não grava)
python3 scripts/aquisicao/a16_cnes_profissional_mensal.py --etapa baixar      # ZIPs → cache privado (~17 GB baixados, apagados)
python3 scripts/aquisicao/a16_cnes_profissional_mensal.py --etapa consolidar  # painel a partir do cache
python3 -m pytest tests/test_aquisicao_cnes_profissional.py
```

O `run_all.py` roda o a16 em `--etapa verificar`: confere as saídas
versionadas contra o manifesto (SHA-256, linhas, colunas, competências,
entradas e veredito), sem rede e sem gravar nada. A aquisição é idempotente
e retomável: competência com cache e metadado não é baixada de novo, e ZIP
local íntegro é reaproveitado.
