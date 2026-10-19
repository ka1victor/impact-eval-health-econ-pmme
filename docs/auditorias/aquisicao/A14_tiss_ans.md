# A14 — TISS/ANS: produção paga por planos, município do prestador × mês × tipo × CBO

> **Data:** 19/10/2026.<br>
> **Tarefa:** aquisição TISS do protocolo de produção especializada
> ([`06_execucao/47`](../../06_execucao/47_protocolo_producao_especializada.md),
> §2, §3, §6 e §9), insumo de K3, K3a, K3b e K5.<br>
> **Script:** [`scripts/aquisicao/a14_adquirir_tiss_ans.py`](../../../scripts/aquisicao/a14_adquirir_tiss_ans.py).<br>
> **Números:** todos os números desta aquisição estão no resumo gerado pelo
> script, [`output/aquisicao/tiss/a14_resumo.md`](../../../output/aquisicao/tiss/a14_resumo.md),
> em [`validacao_tiss.json`](../../../output/aquisicao/tiss/validacao_tiss.json),
> em [`cobertura_tiss_uf_mes.csv`](../../../output/aquisicao/tiss/cobertura_tiss_uf_mes.csv)
> e no manifesto [`manifesto_tiss.json`](../../../output/aquisicao/tiss/manifesto_tiss.json).
> Este texto não repete contagens à mão; `tests/test_aquisicao_tiss.py` confere
> o resumo contra os painéis.<br>
> **Cegamento:** só aquisição. Nada foi calculado por faixa de IVS, lado de
> corte, bolsa ou tratamento; o script não lê IVS (o teste
> `test_nao_le_ivs` verifica o código-fonte). Nenhum contraste foi estimado.

## 1. O que foi construído

| Saída | Conteúdo | Git |
|---|---|---|
| `output/aquisicao/tiss/painel_tiss_municipio_mes_tipo_cbo.parquet` | ambulatorial, painel balanceado: município (`co_ibge`, 6 dígitos) × mês de realização × tipo × grupo de CBO | sim |
| `output/aquisicao/tiss/painel_tiss_hospitalar_municipio_mes_tipo.parquet` | hospitalar, mesmo esquema, só com `grupo_cbo = todos_cbo` (a fonte não tem CBO) | sim |
| `output/aquisicao/tiss/painel_tiss_nao_atribuido_uf_mes.parquet` | eventos sem município atribuível, por UF × mês × motivo × tipo × grupo | sim |
| `output/aquisicao/tiss/tiss_itens_por_categoria_uf_mes.parquet` | as 9 categorias finas de item (e eventos sem item), por UF × mês × escopo (atribuído, não atribuído, operadora odontológica) | sim |
| `output/aquisicao/tiss/cobertura_tiss_uf_mes.csv` | status de cada UF × mês × base, linhas, junção, datas de publicação de CONS e DET | sim |
| `output/aquisicao/tiss/validacao_tiss.json` | portões, junção, status de município, quantidades, tabelas TUSS, capítulos, CBO, alertas de queda, comparação com o SIP | sim |
| `output/aquisicao/tiss/a14_resumo.md` | tabelas geradas (cobertura, validações, totais mensais nacionais, SIP, alertas) | sim |
| `output/aquisicao/tiss/manifesto_tiss.json` | fonte, dicionários, TUSS, regras, entradas locais com hash e, por arquivo baixado, URL, bytes, SHA-256, data do download, `Last-Modified`, linhas | sim |
| `output/aquisicao/tiss/cache_pacote/` | agregado e metadado por UF × mês × base, listagem do FTP, referências | não (`.gitignore`) |
| `output/aquisicao/tiss/cache_bruto/` | ZIPs, apagados logo depois da agregação; dicionários, TUSS e SIP | não (`.gitignore`) |

Nada é gravado em `data/`.

Colunas dos painéis:

| Coluna | Definição |
|---|---|
| `co_ibge`, `uf` | município do prestador executante (6 dígitos) e sua UF |
| `competencia_realizacao` | mês de realização, `AAAAMM` |
| `tipo_procedimento` | ver §5 |
| `grupo_cbo` | ver §4 |
| `n_eventos` | eventos (`ID_EVENTO_ATENCAO_SAUDE`) distintos com pelo menos um item do tipo; um evento conta uma vez em cada tipo que tiver, por isso tipos não se somam |
| `qt_itens` | soma de `QT_ITEM_EVENTO_INFORMADO` dos itens do tipo (vírgula decimal convertida) |
| `n_linhas_det` | linhas DET do tipo |
| `n_linhas_qt_vazia` | linhas DET do tipo com quantidade vazia (fora da soma; nunca viram zero) |
| `status_cobertura` | ver §6 |
| `natureza_dos_dados` | sempre `"EMPIRICO"` |

## 2. Fonte e dicionário

- **Fonte:** Portal de Dados Abertos da ANS,
  `https://dadosabertos.ans.gov.br/FTP/PDA/TISS/`, conjuntos "Procedimentos
  Ambulatoriais por UF" (`AMBULATORIAL/<ano>/<UF>/<UF>_<AAAAMM>_AMB_{CONS,DET,REM}.zip`)
  e "Procedimentos Hospitalares por UF" (`HOSPITALAR/.../<UF>_<AAAAMM>_HOSP_*.zip`).
  Cada ZIP tem um CSV separado por `;`, entre aspas, UTF-8 com BOM, vírgula
  decimal. O REM (modelo de remuneração) só é listado. A listagem do FTP de
  19/10/2026 vai de 2015 a 2025; a última realização publicada é 202512.
- **Dicionários** (ANS, `TISS/DICIONARIO/`, URL e SHA-256 no manifesto):
  `Dicionario_de_variaveis_a_partir_de_2023.ods` e
  `Dicionario_de_variaveis_ate_2022.ods`. Definições usadas:
  - `ID_EVENTO_ATENCAO_SAUDE`: "identificador único do evento"; a
    planilha de informações gerais manda cruzar CONS e DET por ele. Um evento
    ambulatorial é uma guia de consulta ou de SP/SADT não vinculada a
    internação (até 2022, também guia odontológica, GTO);
  - `CD_MUNICIPIO_PRESTADOR`: "código IBGE do município do prestador
    executante". No hospitalar, "para os municípios com atendimento por um
    único prestador hospitalar durante o ano foi omitida a informação do
    município, permanecendo apenas a UF do prestador";
  - `DT_REALIZACAO` (ambulatorial) e `ANO_MES_EVENTO` (hospitalar): "ano e mês
    de ocorrência do evento", `aaaa-mm`;
  - `CBO` (só no CONS ambulatorial): CBO "preenchida conforme a tabela TUSS 24";
  - `CD_MODALIDADE`: modalidade da operadora; 23 = cooperativa odontológica,
    26 = odontologia de grupo;
  - `CD_TABELA_REFERENCIA` e `CD_PROCEDIMENTO`: item conforme as tabelas TUSS
    19 (materiais e OPME), 20 (medicamentos) ou 22 (procedimentos e eventos em
    saúde), ou grupo da TUSS 63; tabelas 90 e 98 são pacotes criados pela
    operadora;
  - `QT_ITEM_EVENTO_INFORMADO`: "quantidade do procedimento/item assistencial
    informada pelo prestador executante". Em pacote (`IND_PACOTE = 1`), a
    quantidade e o valor ficam na linha do pacote e os itens que o compõem vêm
    sem quantidade;
  - `IND_TABELA_PROPRIA = 1`: código criado pela operadora, sem TUSS;
  - `LG_VALOR_PREESTABELECIDO = 1`: contrato por valor preestabelecido; os
    eventos entram nos dados com valor zero ou só o complemento. Este painel
    conta eventos e quantidades, não valores.
- **Datas de publicação** (`Last-Modified` de cada arquivo, no manifesto e em
  `cobertura_tiss_uf_mes.csv`, colunas `data_publicacao_cons` e
  `data_publicacao_det`): os arquivos de 2022 são de 30/07/2025 (CONS e DET);
  de 2023 a 2025, os CONS foram republicados em 20/08/2026 e os DET são de
  18 ou 19/06/2026. Como CONS e DET têm datas diferentes, a junção DET → CONS
  é conferida em todo par (§7).
- **TUSS:** `terminologia_unificada_saude_suplementar_TUSS-049/pda-049-tuss.zip`
  (ANS, versão de 26/06/2026; URL e SHA-256 no manifesto), usada para
  documentar a estrutura dos capítulos da tabela 22 e os grupos da tabela 63
  (`classificacao.estrutura_tuss22` no manifesto).

## 3. Unidade, chaves e filtros

- **Unidade:** município do prestador executante × mês de realização × tipo de
  procedimento × grupo de CBO do evento. É o lugar onde o serviço foi prestado,
  não a residência do beneficiário.
- **Chave de junção:** `ID_EVENTO_ATENCAO_SAUDE`, do DET para o CONS do mesmo
  par UF × mês. O CONS tem de ter ID único e numérico (até 18 dígitos); senão o
  par falha.
- **Meses:** realização 202201 a 202512 (48 meses). Nenhum arquivo de mês
  ≥ 202601 é baixado ou lido (`checar_limite`). A aquisição seguiu a ordem
  pedida: primeiro 202406–202506 e 202510–202512 (pré e pós do protocolo 47),
  depois o resto.
- **Município válido:** 6 dígitos, presente na lista do IBGE usada no
  repositório (`output/aquisicao/populacao_censo2022_municipios.csv`, só a
  coluna `co_ibge_6d` e a UF; a população não é lida) e com o prefixo da UF do
  arquivo. Os demais nunca são atribuídos (§6).
- **Odontologia, fora das contagens médicas:** eventos de operadoras com
  `CD_MODALIDADE` 23 ou 26 e itens da TUSS 22 do capítulo 8 (odontologia). Os
  totais excluídos ficam no manifesto, na validação e na tabela de categorias
  finas (escopo `operadora_odontologica`, categoria `odontologia_tuss22`).

## 4. Grupos de CBO

A regra é a do painel CNES nacional (protocolo 47, §3.1) e é **importada** do
a09, não redigitada. O a14 carrega `a09_adquirir_cnes_nacional.py`, lê dele a
ponte (`carregar_ponte`), `PREFIXOS_MEDICOS`, `GENERALISTAS`, `MFC` e
`GRUPO_MFC`, e classifica cada código distinto de CBO passando-o pela própria
função `agregar_mes` do a09 (um vínculo fictício por código, sem dado
observado), depois do filtro de extração do a09 (CBO médico = começa por um
dos `PREFIXOS_MEDICOS`). O teste `test_igual_ao_a09_em_todos_os_cbo_medicos_da_ponte`
confere a equivalência.

Partição exclusiva do evento, e grupos de saída:

| Grupo de saída | Partição | Observação |
|---|---|---|
| `alvo_pmme` | CBO-alvo da ponte (`cbos_elegiveis` dos cursos) | principal do K3 |
| `especialistas_nao_alvo` | 2251/2252/2253 fora do alvo e dos generalistas | **contém a MFC**, como no a09 |
| `mfc_225130` | 225130 | subconjunto de `especialistas_nao_alvo` |
| `generalistas` | 225125, 225142, 225170 | |
| `outros_medicos` | médico pelo filtro do a09 sem outro grupo (família 2231) | |
| `nao_medicos` | CBO preenchido não médico (enfermagem, fisioterapia, odontologia etc.) | |
| `cbo_ausente` | CBO vazio no CONS | ver §9 |
| `todos_cbo` | soma das partições | total para validação |

No hospitalar o CONS não tem CBO: só existe `todos_cbo`.

## 5. Tipos de procedimento (TUSS)

Cada linha DET recebe uma categoria fina, e cada evento conta em cada tipo em
que tiver pelo menos um item.

**Estrutura usada.** A tabela 22 da TUSS (procedimentos e eventos em saúde)
usa códigos de 8 dígitos herdados da Classificação Brasileira Hierarquizada de
Procedimentos Médicos (CBHPM, AMB), cujo primeiro dígito é o capítulo:
1 = procedimentos gerais (1.01 = consultas; 1.01.02 = visita hospitalar),
2 = procedimentos clínicos, 3 = procedimentos cirúrgicos e invasivos,
4 = procedimentos diagnósticos e terapêuticos (SADT). A TUSS acrescenta o
capítulo 5 (procedimentos de outros profissionais, por exemplo sessões de
terapias) e o 8 (odontologia). A estrutura foi conferida na própria tabela 22
publicada pela ANS (número de códigos e exemplos de cada capítulo, e a
família 101, no manifesto em `classificacao.estrutura_tuss22`).

| Categoria fina | Regra (ordem de precedência de baixo para cima) |
|---|---|
| `consultas` | tabela 22, código de 8 dígitos começando por `101` |
| `exames` | tabela 22, capítulo 4 |
| `cirurgicos` | tabela 22, capítulo 3 |
| `outros_tuss22` | tabela 22, demais capítulos (1 exceto 101, 2, 5 e outros) |
| `odontologia_tuss22` | tabela 22, capítulo 8 (fora das contagens médicas) |
| `agrupados_tuss63` | tabela 63 (grupos de procedimentos) |
| `materiais_medicamentos_taxas` | tabelas 18, 19 e 20 |
| `pacote_ou_tabela_propria` | tabelas 90 e 98, ou `IND_TABELA_PROPRIA = 1` (vence a tabela informada) |
| `outra_tabela_ou_invalido` | qualquer outra tabela (inclusive a 00 sem tabela própria) ou código da 22 fora do formato |

O código da tabela é normalizado com zeros à esquerda: os arquivos de 2022
escrevem a tabela 00 como "0" e grupos da 63 sem zeros.

Tipos do painel:

| `tipo_procedimento` | Categorias |
|---|---|
| `consultas` | `consultas` |
| `exames` | `exames` |
| `cirurgicos` | `cirurgicos` |
| `outros` | `outros_tuss22`, `agrupados_tuss63`, `materiais_medicamentos_taxas`, `pacote_ou_tabela_propria`, `outra_tabela_ou_invalido` |
| `agrupados_tuss63` | `agrupados_tuss63` (subconjunto de `outros`, para eventual adendo) |
| `todos_nao_odonto` | todas menos `odontologia_tuss22` |

As regras de consultas, exames e cirurgias são as do protocolo 47 (§3.2). Os
itens agrupados da TUSS 63 (por exemplo "009 medicina laboratorial") são
exames em parte, mas o protocolo congelou "exames = família 4"; por isso
ficam em `outros`, separados em `agrupados_tuss63` (§9).

## 6. Cobertura, zero e ausente

A unidade de aquisição é o par CONS/DET de uma UF × mês × base (pacote).

| `status_cobertura` | Significado | Valores |
|---|---|---|
| `observado_municipio_com_evento` | pacote aprovado e município com pelo menos um evento atribuído no mês | contagens observadas; zero numa célula = nenhum evento daquele tipo × grupo |
| `arquivo_presente_municipio_sem_evento` | pacote aprovado e município sem nenhum evento de plano reportado no mês | **zero de eventos reportados**, não zero de produção |
| `ausente_arquivo_nao_publicado` | CONS ou DET não listado no FTP | NA |
| `ausente_falha_download` | download falhou depois das tentativas | NA |
| `ausente_reprovado_*` | pacote reprovado num portão (§7) | NA |
| `ausente_falha_leitura_ou_validacao` | esquema, ID ou leitura inválidos | NA |
| `ausente_nao_processado` | pacote não processado | NA |

Ausente nunca vira zero, e zero só existe em pacote aprovado. Eventos de um
pacote aprovado sem município atribuível vão para
`painel_tiss_nao_atribuido_uf_mes.parquet`, com o motivo:
`municipio_ausente` (ambulatorial, código vazio), `municipio_omitido_pela_ans`
(hospitalar, código vazio pela regra do prestador único),
`municipio_invalido` (fora da lista do IBGE), `municipio_de_outra_uf` e
`mes_divergente` (mês de realização diferente do arquivo). Por isso um
município com `arquivo_presente_municipio_sem_evento` pode ter tido eventos que
a ANS publicou sem código; quem usar o painel deve ler a tabela de não
atribuídos da UF ao lado.

## 7. Validações

**Portões por pacote** (fixados antes de agregar qualquer arquivo completo; o
pacote reprovado fica ausente com o motivo):
- esquema: as colunas usadas existem no cabeçalho;
- CONS com ID numérico e único;
- junção DET → CONS ≥ 99,5% das linhas DET (`taxa_juncao_det` por pacote em
  `cobertura_tiss_uf_mes.csv`); as linhas não juntadas são contadas e não são
  atribuídas;
- eventos com mês de realização diferente do arquivo ≤ 1%;
- CONS e DET não vazios (arquivo vazio é ausente, não zero).

**Conferências gravadas** (em `validacao_tiss.json` e no resumo):
- linhas por arquivo (manifesto, `arquivos[].linhas`);
- eventos por status de município, eventos de operadora odontológica,
  eventos CONS sem item DET;
- quantidades vazias (dentro e fora de pacote), não numéricas, negativas e
  não inteiras;
- linhas DET por tabela TUSS, por capítulo da 22 e por grupo da 63;
- eventos ambulatoriais por código de CBO;
- cobertura de meses por UF;
- **quedas e saltos anormais**, só sinalizados: mês de uma UF abaixo de metade
  ou acima do dobro da mediana da UF, ou queda de mais de 40% contra o mês
  anterior. Nada é corrigido;
- códigos de município válidos contra a lista do IBGE, por construção e por
  teste.

**Totais publicados pela ANS.** O D-TISS (painel dos dados do TISS) só existe
como painéis Power BI, sem arquivo de totais para download reprodutível, e não
foi usado. O agregado publicado usado é o **SIP** (mapa assistencial
trimestral, `FTP/PDA/SIP/`), comparado por trimestre com o TISS nacional
(todos os municípios, inclusive não atribuídos, sem operadoras
odontológicas): consultas médicas (SIP `A`) contra eventos e quantidades de
consultas; internações (SIP `E`) contra eventos hospitalares; internações
cirúrgicas (SIP `E1.02`) contra eventos hospitalares com item cirúrgico. São
sistemas diferentes (o SIP é declarado por operadora e beneficiário), então a
comparação é descritiva, com faixa de alerta 0,67–1,5 fixada antes de rodar, e
não é portão.

## 8. Resultado da execução de 19/10/2026

A aquisição terminou em 19/10/2026, em cinco rodadas da mesma etapa
retomável (histórico em `manifesto_tiss.json`, campo `execucao_aquisicao`):
duas interrompidas à mão para mudar o código antes de qualquer pacote ser
usado (classificação de CBO pela função do a09; fila separada para os pacotes
grandes), uma morta por falta de memória do cgroup (14,3 GB) e uma interrompida
para reduzir a memória do agregador. Pacote interrompido não deixa cache: é
refeito do zero. A equivalência do agregador revisto foi conferida
reagregando um pacote já aprovado (mesmo SHA-256 dos ZIPs, mesma tabela e
mesmo diagnóstico). Dois downloads truncados de SP foram detectados pelo
`Content-Length` e baixados de novo. Contagens, bytes e tempos estão no
manifesto e no resumo; aqui só o que eles mostram (cada afirmação abaixo é
conferida por `tests/test_aquisicao_tiss.py`, classe `TestAfirmacoesDoDoc`).

- **Cobertura completa:** todos os pacotes planejados (27 UFs × 48 meses ×
  2 bases) foram baixados, passaram nos portões e estão no painel. Não há
  nenhuma célula `ausente_*`; os zeros são todos
  `arquivo_presente_municipio_sem_evento`.
- **Junção:** em todos os pacotes, todas as linhas DET têm evento no CONS,
  apesar das datas de publicação diferentes; nenhum evento CONS ficou sem item
  DET; nenhum mês de realização diverge do arquivo, nem no CONS nem no DET.
- **Município:** no ambulatorial não há código vazio e quase nenhum código
  inválido; no hospitalar, as internações com município omitido pela ANS são
  uma fração mínima. Os eventos não atribuídos estão em
  `painel_tiss_nao_atribuido_uf_mes.parquet`.
- **Quantidade:** toda quantidade vazia é de item de pacote (como diz o
  dicionário); não há quantidade vazia fora de pacote, não numérica nem
  negativa. Há quantidades decimais, somadas como estão.
- **CBO:** a maior parte dos eventos de exames, cirurgias e "outros" não tem
  CBO, enquanto nas consultas a fração sem CBO é pequena (tabela de
  participação no resumo). A família 2231 (`outros_medicos`) praticamente não
  aparece no TISS.
- **Hospitalar:** a maioria dos municípios-mês não tem internação de plano
  reportada (`arquivo_presente_municipio_sem_evento`), como esperado para
  oferta hospitalar concentrada.
- **SIP:** em nenhum trimestre a razão TISS/SIP sai da faixa de alerta; o
  TISS fica abaixo do SIP em todos os trimestres e itens comparados, e a menor
  razão de internações e de consultas é a do último trimestre (202510–202512),
  o que é compatível com envio ainda incompleto dos meses mais recentes.
- **Quedas e saltos sinalizados** (lista no resumo): entre eles, o Acre a
  partir de 202509 no ambulatorial e no hospitalar, Roraima em 202511–202512 e
  picos isolados do Piauí em 2022–2023. Nada foi corrigido.

## 9. Limites

- **Só eventos pagos por planos.** O TISS cobre o que as operadoras enviam à
  ANS. O pagamento direto do bolso não tem fonte pública por município e não
  é imputado: "SUS + planos" não é "SUS + privado".
- **Município do prestador**, não do beneficiário: mede oferta realizada no
  município, inclusive para pacientes de fora.
- **Completude do envio varia por operadora e por mês.** Quedas e saltos de
  uma UF podem ser mudança de envio, não de produção; estão sinalizados, não
  corrigidos.
- **CBO ausente.** Uma parte grande dos eventos ambulatoriais não tem CBO,
  sobretudo SP/SADT de exames; esses eventos ficam em `cbo_ausente` e não
  entram em `alvo_pmme`. K3 por CBO `alvo_pmme` é, portanto, um piso.
- **CBO do evento:** o CONS traz um CBO por evento; o dicionário não diz se é
  o do executante em todas as guias de SP/SADT.
- **Hospitalar sem CBO** e com município omitido onde há um único prestador
  hospitalar no ano: as internações desses municípios ficam como não
  atribuídas, o que torna o hospitalar por município incompleto justamente nos
  municípios pequenos.
- **Exames agrupados:** os itens enviados pela TUSS 63 não entram em `exames`
  (regra congelada do protocolo); ficam em `agrupados_tuss63`.
- **Pós-período só até 202512**: três meses depois de 202510, como o
  protocolo 47 já registra.
- **Republicação:** a ANS republica arquivos (os CONS de 2025 em 20/08/2026).
  O SHA-256 de cada arquivo no manifesto identifica a versão lida.

## 10. Pressupostos do protocolo que se mostraram falsos ou incompletos

- **"Exames = família 4" não cobre todos os exames.** Uma parte grande dos
  itens chega agrupada pela TUSS 63, e o grupo mais frequente é o 009
  (medicina laboratorial); a tabela 64 vigente diz que tudo é enviado
  individualizado, mas os arquivos de 2022 a 2025 ainda trazem grupos. Esses
  itens ficam em `agrupados_tuss63` (dentro de `outros`). Reclassificar exige
  adendo datado ao protocolo.
- **"Consultas = família 1.01" inclui mais que consulta em consultório:** a
  família 101 da TUSS 22 tem também consulta em domicílio e em pronto-socorro,
  visita hospitalar e atendimento ao recém-nascido (lista em `classificacao.estrutura_tuss22.familia_101_consultas`
  no manifesto). No hospitalar, `consultas` é, na prática, visita hospitalar.
- **Produção "que exige especialista" pelo CBO** só é medida bem nas
  consultas: em exames e cirurgias a maior parte dos eventos não tem CBO, e o
  K3a de exames e cirurgias por `alvo_pmme` é um piso, não um total.
- **O TISS hospitalar não tem CBO:** cirurgias de planos por CBO
  `alvo_pmme` não existem na fonte; só o total por município.
- **Pós-período até 202512:** confirmado (a listagem não tem 2026), mas os
  últimos meses parecem incompletos frente ao SIP (§8); o pós de três meses do
  K3 tende a subestimar o nível. Como é igual dos dois lados do corte, afeta
  mais o nível que o contraste, mas isso não foi verificado aqui (verificar
  exigiria olhar por lado do corte, o que a aquisição não faz).
- **Data de publicação diferente entre CONS e DET** (2023–2025) não quebrou
  a chave: a junção é completa.

## 11. Reprodução

```bash
python3 scripts/aquisicao/a14_adquirir_tiss_ans.py                       # padrão: verificar (sem rede, não grava)
python3 scripts/aquisicao/a14_adquirir_tiss_ans.py --etapa aquisicao     # lista o FTP, baixa, agrega e apaga os ZIPs (cache)
python3 scripts/aquisicao/a14_adquirir_tiss_ans.py --etapa painel        # monta as saídas versionadas do cache
python3 scripts/aquisicao/a14_adquirir_tiss_ans.py --etapa tudo
python3 -m pytest -q tests/test_aquisicao_tiss.py
```

O `run_all.py` roda o a14 só em `--etapa verificar`: confere as saídas
versionadas (SHA-256, linhas e colunas), o plano de meses e os SHA-256 das
entradas locais contra o manifesto, sem rede e sem gravar. A aquisição é
retomável: pacote aprovado (com cache) ou reprovado não é refeito; ausência e
falhas são tentadas de novo. Os ZIPs de cada pacote são apagados assim que a
agregação termina; o SHA-256 fica no manifesto.
