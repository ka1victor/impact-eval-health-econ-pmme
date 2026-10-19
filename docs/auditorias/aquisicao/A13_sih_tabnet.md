# A13 — SIH/SUS no TabNet: AIH por município de internação × mês × grupo

> **Data:** 19/10/2026.<br>
> **Tarefa:** aquisição SIH do protocolo de produção especializada
> ([`06_execucao/47`](../../06_execucao/47_protocolo_producao_especializada.md), §2, §6 e §9),
> insumo da primária K2 (cirurgias SUS hospitalares, AIH do grupo 04).<br>
> **Script:** [`scripts/aquisicao/a13_adquirir_sih_tabnet.py`](../../../scripts/aquisicao/a13_adquirir_sih_tabnet.py).<br>
> **Números:** contagens, totais nacionais, validações por mês e status estão no
> resumo gerado pelo script,
> [`output/aquisicao/sih/a13_resumo.md`](../../../output/aquisicao/sih/a13_resumo.md),
> em [`a13_validacoes.json`](../../../output/aquisicao/sih/a13_validacoes.json) e no
> manifesto [`manifesto_sih.json`](../../../output/aquisicao/sih/manifesto_sih.json).
> Este texto não repete contagens à mão; as listas de UF-mês da seção 5 são
> conferidas contra o manifesto por `tests/test_aquisicao_sih.py`.<br>
> **Cegamento:** só aquisição. Nada foi calculado por IVS, faixa da bolsa, lado de
> corte ou tratamento; o script não lê IVS. O universo de municípios é a lista do
> próprio formulário do TabNet.

## 1. O que foi construído

| Saída | Conteúdo | Git |
|---|---|---|
| `output/aquisicao/sih/painel_sih_municipio_mes_grupo.parquet` | painel balanceado: município (`co_ibge`, 6 dígitos) × competência de processamento × grupo do procedimento principal | sim |
| `output/aquisicao/sih/painel_sih_municipio_mes_carater_g04.parquet` | grupo 04 (cirúrgico) por caráter do atendimento: eletivo, urgência e as três categorias de causa externa | sim |
| `output/aquisicao/sih/ignorados_sih_uf_mes_grupo.parquet` | "MUNICIPIO IGNORADO - UF" de cada UF e "000000 Ignorado ou exterior", separados do painel | sim |
| `output/aquisicao/sih/a13_validacoes.json` | validações v1–v7 por mês, totais nacionais e por UF, UF-mês sem dado e atípicos | sim |
| `output/aquisicao/sih/a13_resumo.md` | tabelas geradas do manifesto e das validações | sim |
| `output/aquisicao/sih/manifesto_sih.json` | fonte, formulário (SHA-256), opções usadas, conceito de tempo e lugar, chaves, filtros, regras, status e, por consulta × mês, URL, corpo do POST, data e hora, SHA-256 e tamanho da resposta | sim |
| `output/aquisicao/sih/cache_tabnet/` | formulário e respostas brutas (um `.html` e um `.json` de metadado por consulta × mês) | não (`.gitignore`) |

Colunas do painel principal:

| Coluna | Definição |
|---|---|
| `co_ibge` | código IBGE de 6 dígitos do município de internação (rótulo da linha do TabNet) |
| `uf` | dois primeiros dígitos de `co_ibge` |
| `competencia` | mês de processamento, `AAAAMM` (arquivo `qibrAAMM.dbf`) |
| `grupo` | grupo SIGTAP do procedimento principal, 2 dígitos (`04` = cirúrgico) |
| `aih_aprovadas` | incremento "AIH aprovadas" (inteiro; ausente onde a UF-mês não tem dado) |
| `internacoes` | incremento "Internações" (exclui AIH de continuação) |
| `valor_total` | incremento "Valor total", R$ correntes |
| `status` | ver a seção 4 |
| `uf_mes_atipico` | alerta da seção 5.2; não altera o valor |
| `natureza_dos_dados` | sempre `EMPIRICO` |

## 2. Fonte

- **Formulário:** `http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sih/cnv/qibr.def`,
  "Procedimentos hospitalares do SUS - por local de internação - Brasil". Só HTTP.
- **Consulta:** POST `application/x-www-form-urlencoded` em latin-1 para
  `http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sih/cnv/qibr.def`, com
  `formato=prn`, `zeradas=exibirlz` e `mostre=Mostra`.
- O script baixa o formulário e lê dele os nomes dos campos e os `VALUE` das
  opções de `Linha`, `Coluna`, `Incremento`, `Arquivos` e dos filtros `S*`. Nada
  é digitado: o script procura o rótulo (por exemplo, "04 Procedimentos
  cirurgicos") e usa o valor que o formulário traz. Todos os filtros não usados
  vão com o padrão do formulário, "Todas as categorias".
- O formulário oferece "Caráter atendimento" como coluna e filtro, mas **não**
  oferece especialidade do leito nem CBO do profissional. O painel opcional por
  especialidade cirúrgica não foi feito porque a dimensão não existe nesta fonte.

Consultas, uma por arquivo mensal:

| Consulta | Linha | Coluna | Incremento | Filtro | Uso |
|---|---|---|---|---|---|
| `mun_grupo_aih` | Município | Grupo procedimento | AIH aprovadas | — | painel |
| `mun_grupo_internacoes` | Município | Grupo procedimento | Internações | — | painel |
| `mun_grupo_valor` | Município | Grupo procedimento | Valor total | — | painel |
| `uf_grupo_aih` | UF | Grupo procedimento | AIH aprovadas | — | conferência; UF-mês sem dado |
| `procmes_grupo_aih` | Ano/mês processamento | Grupo procedimento | AIH aprovadas | — | conceito de tempo; total nacional |
| `mun_carater_g04_aih` | Município | Caráter atendimento | AIH aprovadas | Grupo procedimento = 04 | painel de caráter |
| `mun_grupo_aih_uf_AC` | Município | Grupo procedimento | AIH aprovadas | UF = 12 Acre | conferência célula a célula |
| `mun_grupo_aih_uf_RR` | Município | Grupo procedimento | AIH aprovadas | UF = 14 Roraima | conferência célula a célula |

## 3. Tempo, lugar e unidade

- **Tempo:** o campo "Arquivos" do TabNet seleciona `qibrAAMM.dbf`, que é o
  **mês de processamento** da AIH. A validação v4 confere, em cada arquivo, que a
  única linha não nula de "Ano/mês processamento" é o próprio mês. Não é o mês
  da internação nem o da alta: AIH reapresentadas ou processadas com atraso caem
  no mês em que foram processadas. É o mesmo conceito do SIA no TabNet.
- **Período:** 202201 a 202607, 55 meses. Nenhum mês ≥ 202609 é pedido; o
  protocolo 47 lê o SIH até 202607, embora o formulário já liste arquivos até o
  último publicado.
- **Lugar:** município do **estabelecimento de internação**, não o de residência
  do paciente. Internação de residente de outro município conta onde ocorreu.
- **Unidade:** município × mês de processamento × grupo do procedimento
  principal (SIGTAP). Chave `(co_ibge, competencia, grupo)`; no painel de caráter,
  `(co_ibge, competencia, carater)`.
- **Grupos:** só aparecem como colunas os grupos com AIH no mês (o TabNet omite
  coluna com total nacional zero). O painel tem a união dos grupos devolvidos em
  algum mês (lista em `a13_validacoes.json`, `grupos_painel`).

## 4. Zeros, ausências e status

| `status` | Valor | Quando |
|---|---|---|
| `observado` | positivo | célula numérica devolvida pelo TabNet |
| `zero_tabnet` | 0 | o TabNet devolveu `-`, que a legenda da página define como "dado numérico igual a 0 não resultante de arredondamento" |
| `zero_coluna_omitida` | 0 | o grupo não veio como coluna no mês; aceito como zero só porque o Total de cada linha confere com a soma das colunas devolvidas |
| `ausente_uf_mes_sem_dado` | NaN | a UF inteira tem total zero no mês (seção 5.1) |

- Nenhum município da lista do formulário faltou em nenhuma resposta (v7); se
  faltasse, a consolidação pararia, em vez de preencher.
- A lista do formulário tem um código além dos municípios do Censo 2022:
  `510183` (Boa Esperança do Norte, MT), instalado depois do Censo. Fica no
  painel como o TabNet o devolve; quem cruzar com a população do Censo 2022 terá
  de tratá-lo explicitamente.
- O município ignorado de cada UF e o "Ignorado ou exterior" ficam em
  `ignorados_sih_uf_mes_grupo.parquet`, com a mesma regra de ausência. O DF não
  tem linha de município ignorado no TabNet.
- Os status valem para `aih_aprovadas`; `internacoes` e `valor_total` seguem a
  mesma regra de ausência por UF-mês.

## 5. UF-mês sem dado e UF-mês atípico

### 5.1 Sem dado na fonte (NaN, nunca zero)

Regra: UF com total de AIH aprovadas igual a zero no mês, na consulta UF × grupo.
Uma UF inteira sem nenhuma AIH processada no mês não é produção zero: é o
arquivo da UF ausente do processamento publicado. Os municípios e o ignorado da
UF ficam NaN com `status = ausente_uf_mes_sem_dado`. Lista gerada pela execução
de 19/10/2026 (conferida contra o manifesto pelo teste):

<!-- uf_meses_sem_dado -->
- 202607 — AC
- 202607 — RR
<!-- /uf_meses_sem_dado -->

### 5.2 Atípico (alerta; valor mantido)

Regra: total de AIH da UF no mês maior que zero e menor que 0,5 × a mediana
mensal da UF em 202201–202607. A coluna `uf_mes_atipico` marca esses UF-meses;
o valor fica como o TabNet devolveu, porque não há como saber se o arquivo está
parcial ou se a produção caiu. O limiar foi fixado depois de ver a tabela
nacional UF × mês da própria fonte, sem nenhum dado por IVS ou lado de corte.
Cabe à estimação decidir, antes de olhar resultados, se exclui esses UF-meses.

<!-- uf_meses_atipicos -->
- 202206 — RR
- 202309 — RR
- 202606 — RR

Totais da UF, mediana e fração de cada um estão no resumo gerado.
<!-- /uf_meses_atipicos -->

### 5.3 O que mudou em relação ao registro de 31/08/2026

O `CLAUDE.md` registra que `RDAC2606.dbc` e `RDRR2606.dbc` (arquivos reduzidos
do SIH no FTP) faltavam em 31/08/2026. No TabNet consultado em 19/10/2026:

- AC e RR em 202606 **têm** dado;
- RR em 202606 aparece como atípico (5.2), o que é compatível com um arquivo
  parcial ou tardio, mas a fonte não permite confirmar;
- a falta passou para 202607, onde AC e RR estão sem dado (5.1).

O FTP e o TabNet são publicações diferentes, e a página avisa que os "dados
referentes aos últimos seis meses" estão "sujeitos a atualização". Uma nova
consulta pode mudar 2026-02 a 2026-07; por isso cada resposta tem SHA-256 e data
no manifesto.

## 6. Validações (fail closed)

Todas por mês; qualquer falha impede a gravação das saídas canônicas.

| Id | Validação |
|---|---|
| leitor | período da resposta igual ao mês pedido; filtro ecoado na página; cabeçalho esperado; toda célula numérica ou `-`; Total de cada linha = soma das colunas; linha Total = soma das linhas; subtotais de ano = soma dos 12 meses |
| v1 | soma de todas as linhas (municípios + ignorados) = Total do TabNet, por grupo, nos três incrementos |
| v2 | Total da consulta municipal = Total da consulta por UF = linha do mês na consulta por processamento |
| v3 | por UF × grupo: municípios da UF + ignorado da UF = linha da UF na consulta por UF |
| v4 | o arquivo do mês só tem AIH no próprio mês de processamento |
| v5 | por município: soma das AIH do grupo 04 por caráter = AIH do grupo 04 |
| v6 | AC e RR célula a célula: consulta filtrada pela UF = linhas da UF na consulta nacional; linhas de fora da UF zeradas |
| v7 | municípios de cada resposta = lista do formulário |

O resultado por mês está na tabela do resumo gerado. O teste também refaz, a
partir do painel versionado, a soma municipal + ignorados contra o Total de cada
mês e grupo, e a soma por caráter contra o grupo 04.

## 7. Limites

- **Sem CBO:** o TabNet do SIH não filtra pelo CBO do profissional. K2 conta
  toda AIH cirúrgica do município, feita ou não por especialista do PMM-E.
- **Local de internação:** mede a produção dos hospitais do município, não o
  acesso dos residentes. Deslocamento de pacientes entre municípios entra como
  mudança de produção local.
- **Mês de processamento:** atrasos de faturamento, reapresentações e mudanças
  de rotina de processamento deslocam AIH entre meses e podem criar picos
  administrativos sem mudança na assistência.
- **AIH aprovadas inclui continuação:** internações longas geram mais de uma AIH;
  a coluna `internacoes` é a contagem sem as de continuação.
- **Revisão da fonte:** os últimos seis meses podem ser revistos pelo DATASUS.
- **UF-mês atípico:** o alerta não corrige nada; um arquivo parcial passaria como
  dado observado.
- **Caráter:** é o campo da AIH; "eletivo" e "urgência" seguem a classificação do
  faturamento, não uma auditoria clínica.

## 8. Reprodução

```bash
python3 scripts/aquisicao/a13_adquirir_sih_tabnet.py                     # padrão: verificar (sem rede, não grava)
python3 scripts/aquisicao/a13_adquirir_sih_tabnet.py --etapa tudo        # baixa para o cache e consolida
python3 scripts/aquisicao/a13_adquirir_sih_tabnet.py --etapa consolidar  # só refaz as saídas do cache
```

O `run_all.py` roda só `--etapa verificar`. Como as respostas recentes podem ser
revistas pela fonte, uma nova execução de `--etapa tudo` pode não reproduzir os
mesmos SHA-256; a comparação deve ser feita contra o manifesto versionado.
