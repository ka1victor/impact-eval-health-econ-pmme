# A12 — SIA/SUS pelo TabNet: município × mês de processamento × subgrupo × conjunto de CBO

> **Data:** 19/10/2026.<br>
> **Tarefa:** aquisição SIA do protocolo de produção especializada
> ([`06_execucao/47`](../../06_execucao/47_protocolo_producao_especializada.md),
> §2–§4, §6 e §9), insumo de K1, K1a–K1d, K3b, KP1 e KP2.<br>
> **Script:** [`scripts/aquisicao/a12_adquirir_sia_tabnet.py`](../../../scripts/aquisicao/a12_adquirir_sia_tabnet.py).<br>
> **Números:** as contagens e totais estão no resumo gerado pelo script,
> [`output/aquisicao/sia/a12_resumo.md`](../../../output/aquisicao/sia/a12_resumo.md),
> e no manifesto [`output/aquisicao/sia/manifesto_sia.json`](../../../output/aquisicao/sia/manifesto_sia.json).
> Os poucos números deste texto vêm marcados (`<!--n:...-->`) e
> `tests/test_aquisicao_sia.py` confere cada um contra o manifesto.<br>
> **Cegamento:** só aquisição e validação. Nenhum IVS foi lido, nada foi
> tabulado por faixa, lado de corte, bolsa ou tratamento, e nada foi estimado.

## 1. O que foi construído

| Saída | Conteúdo | Git |
|---|---|---|
| `output/aquisicao/sia/painel_sia_municipio_mes_subgrupo_cbo.parquet` | painel longo: `co_ibge` × `competencia_processamento` × `subgrupo` × `conjunto_cbo`, com `qtd_aprovada`, `status` e `natureza_dos_dados` | sim |
| `output/aquisicao/sia/sia_municipio_ignorado_mes_subgrupo_cbo.parquet` | linhas "MUNICIPIO IGNORADO - UF" e "000000 Ignorado ou exterior", nunca atribuídas a município | sim |
| `output/aquisicao/sia/sia_uf_mes_subgrupo_todos.parquet` | consulta Linha = UF, sem filtro de CBO (validação) | sim |
| `output/aquisicao/sia/sia_nacional_cbo_mes_subgrupo.parquet` | consulta Linha = Profissional - CBO, nacional, sem filtro (validação e completude do CBO) | sim |
| `output/aquisicao/sia/sia_subgrupos_por_consulta.csv` | por mês × conjunto × subgrupo: se o subgrupo é coluna da resposta, total do TabNet, total da consulta por UF e soma das CBO do conjunto | sim |
| `output/aquisicao/sia/sia_cobertura_mes.csv` | por mês × conjunto: municípios com produção, totais e sinal de queda | sim |
| `output/aquisicao/sia/sia_conjuntos_cbo.csv` | CBO de cada conjunto com o índice da opção no formulário, mais as opções médicas do formulário | sim |
| `output/aquisicao/sia/sia_municipios_tabnet.csv` | lista de municípios do formulário (código, nome, UF) | sim |
| `output/aquisicao/sia/manifesto_sia.json` | fonte, filtros, conjuntos, regras de status, validações e, para cada consulta, URL, corpo do POST, data e hora, SHA-256 e tamanho da resposta, tentativas | sim |
| `output/aquisicao/sia/a12_resumo.md` | tabelas geradas: validações, conjuntos, cobertura, completude do CBO e subgrupos ao longo do tempo | sim |
| `output/aquisicao/sia/brutos/` | resposta bruta de cada consulta (`.html.gz`) e metadado (`.json`) | não (`.gitignore`) |

Colunas do painel:

| Coluna | Definição |
|---|---|
| `co_ibge` | município do **local de atendimento** (estabelecimento), 6 dígitos do TabNet |
| `competencia_processamento` | mês de **processamento** (arquivo `qabrAAMM.dbf`), `AAAAMM` |
| `subgrupo` | subgrupo SIGTAP do procedimento, 4 dígitos (`0301` consultas; `02xx` grupo 02, exames; `04xx` grupo 04, cirurgias) |
| `conjunto_cbo` | `alvo_pmme`, `especialistas_nao_alvo`, `generalistas`, `mfc_225130` ou `todos_profissionais` |
| `qtd_aprovada` | quantidade aprovada (`Qtd.aprovada`); nula quando `status = municipio_ausente_da_resposta` |
| `status` | `valor_tabnet` (> 0), `zero_tabnet` (`-` no TabNet) ou `municipio_ausente_da_resposta` |
| `natureza_dos_dados` | sempre `EMPIRICO` |

## 2. Fonte, consultas e proveniência

- **Fonte:** TabNet do DATASUS, "Produção Ambulatorial do SUS - Brasil - por
  local de atendimento", `sia/cnv/qabr.def`. Formulário em
  `http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sia/cnv/qabr.def`; consultas por
  POST em `http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sia/cnv/qabr.def`, corpo
  `application/x-www-form-urlencoded` em latin-1. Só HTTP: o HTTPS do TabNet falha
  neste ambiente.
- **Formulário primeiro.** O script baixa o formulário, guarda o SHA-256 e lê
  dele os valores das opções:
  - dimensões: `Linha=Município`, `UF` ou `Profissional_-_CBO`;
    `Coluna=Subgrupo_proced.`; `Incremento=Qtd.aprovada`;
  - arquivos mensais: `Arquivos=qabrAAMM.dbf`;
  - índices das opções de CBO (`SProfissional_-_CBO`) e de UF (`SUF`).

  Os filtros do TabNet usam **índices posicionais** (`1`, `2`, ...), não o
  código da CBO. Por isso cada resposta é conferida pelo eco que o próprio
  TabNet imprime no cabeçalho ("Profissional - CBO: 225120 Medico
  cardiologista, ..." e "Período: Jun/2025"). Se o eco não for exatamente o
  pedido, a resposta é recusada e a consulta é refeita.
- **Formato:** `formato=prn` (texto com ponto e vírgula entre `<PRE>`),
  `zeradas=exibirlz` e `mostre=Mostra`.
- **Consultas:** <!--n:consultas-->395 consultas, todas com status `ok`, em
  <!--n:meses-->55 meses de processamento (202201 a 202607). Para cada mês:
  - cinco consultas Linha = Município, Coluna = Subgrupo: uma por conjunto de
    CBO e uma sem filtro;
  - uma consulta Linha = UF, sem filtro;
  - uma consulta Linha = Profissional - CBO, sem filtro.

  Em 202506 há ainda dez consultas filtradas por UF (RR e AC × cinco
  conjuntos). As consultas são sequenciais, com pausa de 1,5 s, até cinco
  tentativas e espera crescente. Nenhuma precisou ser dividida por UF. Para cada
  consulta o manifesto registra:
  - URL e corpo do POST;
  - data e hora (UTC);
  - SHA-256 e tamanho da resposta bruta;
  - status HTTP, tentativas e falhas anteriores;
  - eco do período.
- **Limite do ciclo 3:** nenhum mês ≥ 202609 é pedido ou lido; o SIA vai até
  202607 (protocolo 47, §6). O script recusa e o teste confere.

## 3. Conjuntos de CBO do profissional executante

A regra é a do painel CNES nacional e **não foi redigitada**. O script importa
`scripts/aquisicao/a09_adquirir_cnes_nacional.py` e:
- lê as CBO-alvo da ponte com `a09.carregar_ponte()`;
- monta um quadro de classificação com uma linha por CBO do formulário do TabNet;
- passa o quadro pela própria `a09.agregar_mes`;
- o grupo em que cada CBO cai é o seu conjunto.

| Conjunto | Regra (a09) | CBO |
|---|---|---|
| `alvo_pmme` | CBO-alvo da ponte (`cbos_elegiveis` dos cursos) | <!--n:alvo_cbo-->17 |
| `especialistas_nao_alvo` | CBO 2251/2252/2253 fora do alvo e dos generalistas; **contém 225130** | <!--n:nao_alvo_cbo-->45 |
| `generalistas` | 225125, 225142, 225170 | 3 |
| `mfc_225130` | 225130 (médico de família e comunidade), relatado à parte | 1 |
| `todos_profissionais` | sem filtro de CBO: todos os profissionais, inclusive produção sem CBO na tabela do TabNet | — |

A lista de cada conjunto, com o rótulo e o índice da opção no formulário, está em
`sia_conjuntos_cbo.csv` e no manifesto. A família 2231 (CBO antigas do CNES,
inclusive 2231F9, médico residente) é médica, mas fica fora dos quatro
conjuntos, como no a09. `--etapa verificar` reaplica a regra atual do a09 às
opções médicas guardadas e para se os conjuntos mudarem.

## 4. Zeros, ausências e "município ignorado"

- **`-` é zero.** A legenda do TabNet diz: "Dado numérico igual a 0 não
  resultante de arredondamento". Vira `qtd_aprovada = 0` com
  `status = zero_tabnet`. Um `0` impresso (zero por arredondamento) é impossível
  numa contagem; se aparecer, a leitura falha.
- **Município ausente da resposta.** Com `exibirlz`, todos os municípios da
  lista do formulário (<!--n:municipios-->5571 códigos de 6 dígitos) vêm na
  resposta. Um município da lista que não viesse ganharia linhas com
  `qtd_aprovada` nula e `status = municipio_ausente_da_resposta`, nunca zero.
  Não houve nenhum (`validacoes.V6_cobertura.municipios_ausentes_da_resposta`
  vazio no manifesto).
- **Subgrupo que não é coluna.** O `exibirlz` mostra linhas zeradas, mas não
  colunas: o TabNet omite o subgrupo sem nenhum registro sob o filtro. Esse
  subgrupo não tem linhas no painel daquele mês e conjunto. A presença de cada
  subgrupo em cada consulta está em `sia_subgrupos_por_consulta.csv`
  (`presente_na_resposta`). A validação V4 confere, pela consulta nacional por
  CBO, que a soma das CBO do conjunto é zero em todo subgrupo ausente. Quem
  agregar por grupo (02, 04) pode tratar o subgrupo ausente como zero
  **daquela consulta**. Isso não vale para um mês ausente: nenhum mês faltou.
- **Consulta que falha** não gera linhas. A consolidação exige todas as
  consultas do plano em cache e íntegras (SHA-256) e, senão, para sem gravar
  nada.
- **"Município ignorado".** As linhas "MUNICIPIO IGNORADO - UF" (o DF não tem)
  e "000000 Ignorado ou exterior" ficam em
  `sia_municipio_ignorado_mes_subgrupo_cbo.parquet` e nunca são atribuídas a
  município. Entram nas somas de validação (Total = municípios + ignorados).

## 5. Validações (todas antes de gravar; fail closed)

O painel é escrito num arquivo temporário dentro do cache. Só é movido para
`output/` se todas as validações obrigatórias passam; se uma falha, nada é
gravado e o diagnóstico fica em `brutos/` (fora do Git). O resultado de cada uma
está em `validacoes` no manifesto e na tabela do resumo.

| Id | O que confere | Resultado |
|---|---|---|
| V1 | em cada resposta, linha Total = soma das linhas (municípios + ignorados) por subgrupo, e coluna Total = soma das células por linha | aprovado |
| V2 | `alvo_pmme + especialistas_nao_alvo + generalistas ≤ todos_profissionais` e `mfc_225130 ≤ especialistas_nao_alvo`, **em cada célula** município × subgrupo × mês | aprovado |
| V3 | todos os profissionais: total nacional por subgrupo e mês igual ao da consulta Linha = UF; e, em cada UF, soma dos municípios + ignorado da UF igual à linha da UF | aprovado |
| V4 | cada conjunto: total nacional por subgrupo e mês igual à soma das suas CBO na consulta Linha = Profissional - CBO; subgrupo ausente da resposta do conjunto tem soma zero nas suas CBO | aprovado |
| V5 | RR e AC em 202506 (mês fixado antes de ver os dados), cada conjunto: consulta filtrada por UF igual à nacional célula a célula; mesmos municípios; municípios de outras UF zerados; subgrupo ausente na filtrada é zero na nacional | aprovado |
| V6 | cobertura (só relato): meses com municípios com produção < 90% da mediana do conjunto, ou quantidade < 80% da mediana | <!--n:meses_sinalizados-->38 meses × conjunto sinalizados |
| V7 | eco de período e filtros igual ao pedido em toda resposta; nenhum mês ≥ 202609 nem > 202607 | aprovado |

Os limiares da V6 foram fixados no script antes da execução completa. A V6 não
corrige nada.

## 6. Resultado da execução de 19/10/2026

Contagens e totais estão no resumo gerado; aqui só o que eles mostram.

- **Todos os meses obtidos**, 202201 a 202607, com as cinco consultas por
  município, a consulta por UF e a por CBO. Todas as consultas responderam na
  primeira tentativa (`consultas.com_mais_de_uma_tentativa` vazio).
- **Todas as validações obrigatórias aprovadas** (V1–V5, V7).
- **Nenhum município ausente** da resposta e nenhum código fora da lista do
  formulário: não há `status = municipio_ausente_da_resposta` no painel.
- **"Município ignorado"** veio zerado em todos os meses e conjuntos; o arquivo
  próprio existe e guarda esses zeros.
- **Queda de cobertura nos meses mais recentes (V6).** O número de municípios
  com produção cai nos últimos meses de processamento, em todos os conjuntos.
  `todos_profissionais` é sinalizado em 202606 e 202607; `alvo_pmme`,
  `especialistas_nao_alvo` e `generalistas` em 202607 (tabela de cobertura no
  resumo). O padrão é o esperado se a produção de muitos municípios desses
  meses ainda não foi processada ou aprovada. O próprio TabNet avisa que os
  últimos seis meses estão sujeitos a atualização. **Não foi corrigido.** O
  pós-período de K1 (202510–202607) inclui esses meses. Quem estimar precisa
  decidir, por adendo datado (protocolo 47, §7), entre:
  - uma nova extração depois de maturar;
  - uma sensibilidade sem os meses sinalizados.

  A aquisição não escolhe.
- **Outros sinais da V6.** No início da série (2022) a quantidade fica abaixo de
  80% da mediana em alguns meses e conjuntos, porque a produção cresce ao longo
  do período. `mfc_225130` é sinalizado em muitos meses por ser pequeno e
  instável (próximo item). A lista completa está no manifesto.
- **Completude do CBO.** A diferença entre o total sem filtro e a soma das linhas
  da consulta por CBO é a produção cujo CBO não está na tabela do TabNet (BPA-C
  sem CBO informado, por exemplo). É pequena em todos os meses, com a fração por
  mês no resumo. Ela entra só em `todos_profissionais`: nenhum dos quatro
  conjuntos a recebe.
- **`mfc_225130`** tem produção em poucos municípios. A CBO 225130 é pouco usada
  no SIA, e a produção da atenção primária aparece sobretudo em 225142
  (`generalistas`). O conjunto é relatado à parte, como pede o protocolo.
- **Grupo 09 (OCI).** Os subgrupos 09xx ("Atenção em Oncologia",
  "Cardiologia", "Ortopedia", ...) são as Ofertas de Cuidados Integrados. Eles
  aparecem só nos meses mais recentes (primeiro mês no resumo, seção
  "Subgrupos ao longo do tempo"). Pela definição do protocolo 47, ficam fora de
  consultas (0301), exames (02) e cirurgias (04). Se parte da produção
  especializada passou a ser registrada como OCI, K1 por grupo pode cair sem
  queda real de produção. Esse é um limite de leitura para o D1/D2. A aquisição
  não muda a definição.

## 7. Limites

- **Mês de processamento, não de atendimento.** O arquivo `qabrAAMM` reúne o
  que foi processado no mês. Produção de meses anteriores (apresentação tardia,
  reapresentação) entra no mês em que é processada. O TabNet avisa que os
  últimos seis meses estão sujeitos a atualização: a série recente pode mudar
  numa nova extração (datas e hashes no manifesto).
- **Local de atendimento, não residência** do paciente: a produção é do
  município do estabelecimento. Deslocamento de pacientes não é observado aqui.
- **Quantidade aprovada pelo SUS**, inclusive de prestador privado contratado.
  Não cobre produção paga fora do SUS. A quantidade apresentada não foi
  adquirida: o TabNet recusa dois incrementos com coluna ativa ("Múltiplos
  conteúdos exigem coluna não ativa"), o que dobraria as consultas, e ela era
  opcional.
- **CBO do executante.** Vale o que o prestador informa no BPA, na APAC e no
  RAAS. A produção sem CBO na tabela do TabNet só entra em
  `todos_profissionais`. Não há filtro por documento (BPA-C, BPA-I, APAC, RAAS),
  financiamento ou complexidade.
- **Quantidade não é paciente nem consulta única.** Um exame de laboratório
  conta cada procedimento. O conjunto de CBO médico limita a contagem ao que o
  médico executa, como pede o protocolo (§3.1).
- **Lista de municípios do TabNet.** É a do formulário; não foi cruzada com o
  universo do a08 (o IVS não é lido nesta tarefa). O cruzamento fica para a
  estimação.

## 8. Reprodução

```bash
python3 scripts/aquisicao/a12_adquirir_sia_tabnet.py                       # padrão: verificar (sem rede, não grava)
python3 scripts/aquisicao/a12_adquirir_sia_tabnet.py --etapa baixar        # respostas brutas para o cache (fora do Git)
python3 scripts/aquisicao/a12_adquirir_sia_tabnet.py --etapa consolidar    # valida o cache e grava as saídas
python3 scripts/aquisicao/a12_adquirir_sia_tabnet.py --etapa tudo          # baixar + consolidar
python3 -m unittest tests.test_aquisicao_sia
```

O `run_all.py` roda o a12 em `--etapa verificar`, depois do a09. Esse modo
confere, sem rede e sem gravar:
- os SHA-256 de todas as saídas tabulares contra o manifesto;
- o esquema e as linhas do painel;
- o plano de meses;
- as validações aprovadas;
- as entradas locais (ponte e script a09);
- a regra dos conjuntos, reaplicada.

O download é retomável: consulta com resposta íntegra no cache não é refeita
(`--refazer` força).
