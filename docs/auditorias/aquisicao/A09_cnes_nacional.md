# A09 — CNES nacional: painel município × grupo de CBO × mês

> **Data:** 18/10/2026.<br>
> **Tarefa:** C do protocolo multi-outcome da bolsa
> ([`06_execucao/40`](../../06_execucao/40_protocolo_multioutcome_rdd_bolsa.md)),
> insumo da família F3 (DiRD no CNES, tarefa E7).<br>
> **Script:** [`scripts/aquisicao/a09_adquirir_cnes_nacional.py`](../../../scripts/aquisicao/a09_adquirir_cnes_nacional.py).<br>
> **Números:** todos os números desta aquisição estão no resumo gerado pelo
> script, [`output/aquisicao/cnes_nacional/a09_resumo.md`](../../../output/aquisicao/cnes_nacional/a09_resumo.md),
> e no manifesto [`output/aquisicao/a09_manifesto_cnes_nacional.json`](../../../output/aquisicao/a09_manifesto_cnes_nacional.json).
> Este texto não repete contagens à mão.<br>
> **Cegamento:** nenhum outcome foi olhado por faixa, por lado de corte ou
> contra o IVS. Do a08 só se lê a lista `co_ibge`. Nenhuma RDD foi estimada.

## 1. O que foi construído

| Saída | Conteúdo | Git |
|---|---|---|
| `output/aquisicao/cnes_nacional/painel_municipio_cbo_mes.parquet` | painel balanceado: município (`co_ibge`, 6 dígitos) × competência × grupo | sim |
| `output/aquisicao/a09_manifesto_cnes_nacional.json` | por competência: URL, data, SHA-256 e tamanho do ZIP, tabelas e colunas lidas, linhas, municípios, profissionais, diagnóstico da chave municipal; entradas locais com hash; filtros; diferenças de esquema | sim |
| `output/aquisicao/cnes_nacional/a09_validacao_painel_ciclo1.json` | reprodução do painel municipal do ciclo 1 | sim |
| `output/aquisicao/cnes_nacional/a09_rotulos_cbo_medicos.csv` | rótulos de CBO médicos lidos de `tbAtividadeProfissional` | sim |
| `output/aquisicao/cnes_nacional/a09_resumo.md` | tabelas geradas (competências, totais nacionais por grupo, validação, rótulos) | sim |
| `output/aquisicao/cnes_nacional/mensal/` | cache por competência dos vínculos médicos (Parquet) e metadados | não (`.gitignore`) |
| `data/raw/cnes/BASE_DE_DADOS_CNES_AAAAMM.ZIP` | ZIP bruto, apagado depois da extração validada | não |

Colunas do painel (horas pelo §16 do protocolo 40):

| Coluna | Definição | Papel |
|---|---|---|
| `n_vinculos` | linhas de `tbCargaHorariaSus` na célula | |
| `n_vinculos_sus` | vínculos com `TP_SUS_NAO_SUS = 'S'` | |
| `n_profissionais_distintos` | `CO_PROFISSIONAL_SUS` distintos | |
| `horas_sus_semanais` | ambulatorial + hospitalar dos vínculos com `TP_SUS_NAO_SUS = 'S'`; nulo se algum deles tem um desses campos em branco | **principal (F3.3)** |
| `horas_sus_semanais_parcial` | a mesma soma, só com as horas observadas | sensibilidade rotulada |
| `horas_totais_amb_hosp` | ambulatorial + hospitalar de todos os vínculos, sem filtro SUS; nulo se algum vínculo tem um desses campos em branco | sensibilidade rotulada |
| `horas_totais` | ambulatorial + hospitalar + outros de todos os vínculos; nulo se algum vínculo tem qualquer dos três em branco | sensibilidade rotulada |
| `horas_totais_parcial` | `horas_totais` só com as horas observadas | sensibilidade rotulada |
| `n_vinculos_horas_ausentes` | vínculos da célula (SUS ou não) com algum dos três campos em branco ou não numérico; ler ao lado das parciais | |
| `tem_profissional` | `n_profissionais_distintos ≥ 1` | |
| `natureza_dos_dados` | sempre `"EMPIRICO"` | |

Na primeira versão do painel, `horas_sus_semanais` somava ambulatorial e
hospitalar de todos os vínculos, SUS ou não; essa soma agora se chama
`horas_totais_amb_hosp`.

Grupos:
- `cbo_XXXXXX`: cada CBO-alvo da ponte
  (`cbos_elegiveis` dos cursos, `output/aquisicao/ponte_curso_cbo_oficial.json`);
- `alvo_pmme`: união das CBO-alvo (a pessoa conta uma vez);
- `generalistas`: 225125 (médico clínico), 225142 (médico da estratégia de
  saúde da família), 225170 (médico generalista). Os rótulos foram conferidos
  em `tbAtividadeProfissional` e estão no manifesto;
- `mfc_225130`: médico de família e comunidade, em grupo próprio pelo adendo
  §13 do protocolo 40 (especificação S6). Não entra em `generalistas`;
- `especialistas_nao_alvo`: CBO 2251/2252/2253 fora das CBO-alvo e dos
  generalistas (contém a 225130);
- `todos_medicos`: CBO 2251/2252/2253 e a família 2231 (ver §4), **inclusive
  médicos residentes** (2231F9);
- `todos_medicos_sem_residentes`: `todos_medicos` sem a CBO 2231F9 (médico
  residente), pelo §16 do protocolo 40. Nenhuma das duas é outcome primário.

## 2. Fonte e competências

- **Fonte:** base completa mensal do CNES (DATASUS/MS),
  `BASE_DE_DADOS_CNES_AAAAMM.ZIP`, pelo servlet HTTPS
  `https://cnes.datasus.gov.br/EstatisticasServlet?path=...` com o
  `Referer` da página de downloads. O FTP do DATASUS é bloqueado pelo proxy
  deste ambiente. O servlet não envia `Content-Length`; a integridade é
  verificada com `ZipFile.testzip()` (CRC de todos os membros).
- **Competências planejadas:** mensais de 202406 a 202608 e trimestrais
  202201, 202204, 202207, 202210, 202301, 202304, 202307, 202310, 202401 e
  202404 (pré-período que atravessa a Portaria GM/MS 752, de junho de 2023),
  mais 202302 e 202303 pelo adendo §13 (S5): a janela 2022-01..2023-03
  antecede todas as políticas nos mesmos cortes (Portaria 752, de 06/2023, e
  Portaria 3.493/2024, a partir de 05/2024).
  Nenhuma competência a partir de 202609 é baixada ou lida: o script recusa
  (`checar_limite`) e o teste verifica.
- **Competência que falha** (download, integridade ou extração) fica **sem
  linhas** no painel e com o motivo no manifesto. Nada é interpolado nem
  copiado de outro mês. Os zeros do painel balanceado só existem em
  competências lidas com sucesso, para município sem nenhum registro no grupo.
- **ZIPs:** o SHA-256 e o tamanho são gravados no metadado da competência
  antes de o ZIP ser apagado.

## 3. Chave municipal

`tbEstabelecimento` tem um único código de município, `CO_MUNICIPIO_GESTOR`
(6 dígitos), além de `CO_ESTADO_GESTOR`. Apesar do nome, ele é o município de
localização do estabelecimento: os estabelecimentos sob gestão estadual
(`TP_GESTAO = E`) e dupla (`D`) aparecem espalhados por milhares de municípios,
e não concentrados nas capitais, e a UF do código coincide com
`CO_ESTADO_GESTOR` em todos os estabelecimentos (diagnóstico por competência no
manifesto, campo `diagnostico_chave_municipal`). É também a chave do painel do
ciclo 1 (`03_adquirir_cnes_mensal.py` e `05_integrar_painel_analitico.py`), o
que permite a validação da §5.

**Distrito Federal.** O universo tem um único código para o DF, 530010. O
script falha (fail-closed) se algum vínculo médico cair num código 53xxxx
diferente (regiões administrativas). Em nenhuma competência isso ocorreu
(`painel.portao_df` no manifesto).

O universo é a lista de municípios do IVS 2010 oficial
(`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`). Municípios do CNES
fora dele (instalados depois de 2010) são registrados no manifesto
(`painel.municipios_cnes_fora_do_universo`) e ficam fora do painel.

## 4. Esquema e mudanças entre competências

- As tabelas lidas têm o mesmo nome em todas as competências
  (`tbCargaHorariaSusAAAAMM.csv`, `tbEstabelecimentoAAAAMM.csv`,
  `tbAtividadeProfissionalAAAAMM.csv`). As colunas usadas existem em todas; o
  script mapeia nomes alternativos e grava, por competência, o cabeçalho lido e
  as diferenças em relação à competência mais recente
  (`diferencas_de_esquema`). O número de membros do ZIP muda ao longo do tempo
  (campo `n_membros_zip`).
- **Família 2231.** As bases trazem códigos de ocupação médica próprios do
  CNES, alfanuméricos, na família 2231 (por exemplo 2231F9, médico residente;
  2231G1, cardiologista intervencionista). Eles entram em `todos_medicos`, como
  pede a tarefa, e em nenhum outro grupo. A contagem por família e competência
  está no resumo; quem usar `todos_medicos` como série deve conferir se a
  família 2231 muda de tamanho no período.
- **Horas vazias ou não numéricas.** Nenhuma documentação do CNES no
  repositório, nem a consultada nesta tarefa, define campo de carga horária
  vazio como zero. Por isso o extrator (versão 2) lê o texto bruto
  (`keep_default_na=False`), conta por campo e competência os valores vazios,
  não numéricos, não inteiros e negativos, e guarda o vazio como **ausente**,
  nunca zero. Regra do painel: `horas_sus_semanais` é ausente se algum vínculo
  da célula tem `QT_CARGA_HORARIA_AMBULATORIAL` ou `QT_CARGA_HOR_HOSP_SUS`
  ausente; `horas_totais` é ausente se algum vínculo tem qualquer dos três
  campos ausente; `n_vinculos_horas_ausentes` conta esses vínculos. Contagem e
  presença de profissional não são afetadas. Célula sem vínculo tem horas 0
  (observado). Pelo §16, a regra do nulo vale para as colunas principais, e as
  colunas `*_parcial` dão a soma das horas observadas como sensibilidade
  rotulada, com `n_vinculos_horas_ausentes` ao lado. A versão 1 do extrator, usada na primeira rodada de 18/10/2026,
  convertia vazio em 0 sem contar; todo o cache foi refeito com novo download
  e o SHA-256 de cada ZIP foi comparado com o da rodada anterior
  (`extracao_anterior` no metadado de cada competência).
- Sem filtro de `TP_SUS_NAO_SUS`, vinculação ou tipo de unidade, como no painel
  do ciclo 1. `n_vinculos` conta linhas de `tbCargaHorariaSus`; vínculos sem
  `CO_PROFISSIONAL_SUS` entram em vínculos e horas, não em distintos.

## 5. Validação contra o painel do ciclo 1

Para os municípios do painel do ciclo 1 e as competências comuns (202406–202607), o
script recalcula o estoque por município × curso × mês com a mesma definição de
`05_integrar_painel_analitico.py` (profissionais distintos nas CBO do curso) e
compara com `especialistas_mst` de
`output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet`. Do painel
antigo só são lidas as chaves e essa coluna. O portão, fixado antes de ver o
resultado, exige ≥ 99% de células idênticas e diferença relativa da soma
≤ 0,5%. O portão roda antes de qualquer gravação: o painel é montado em
memória e, se a validação reprova, o script termina com erro sem gravar nada
em `output/` (o diagnóstico vai só para o log). A etapa `--etapa aquisicao`
só atualiza o cache, que fica fora do controle de versão. O resultado, inclusive se o
SHA-256 de cada ZIP coincide com o do manifesto do ciclo 1, está em
`a09_validacao_painel_ciclo1.json` e no resumo.

## 6. Resultado da execução de 18/10/2026

Contagens e hashes estão no resumo gerado e no manifesto; aqui só o que eles
mostram.
- **Todas as competências planejadas foram obtidas**, inclusive 202608 e os
  meses extras do adendo §13. `competencias_nao_obtidas` está vazio, o painel é
  balanceado (universo × competências × grupos) e nenhum ZIP ficou em disco.
- **Esquema:** as colunas usadas existem em todas as competências. As antigas
  não têm `CO_TIPO_ABRANGENCIA` nem `ST_COWORKING` em `tbEstabelecimento`,
  colunas que o painel não usa.
- **Chave municipal:** em todas as competências, a UF do município coincide
  com `CO_ESTADO_GESTOR` e os estabelecimentos sob gestão estadual se espalham
  por milhares de municípios (§3). Nenhum vínculo médico ficou sem
  estabelecimento nem sem `CO_PROFISSIONAL_SUS`.
- **Fora do universo:** os códigos de município do CNES ausentes do a08, todos instalados
  depois de 2010, ficam fora do painel (lista e tamanho no manifesto). Um deles
  aparece só em parte do período; o estoque do município de origem pode ter um
  degrau quando ele é instalado.
- **Horas ausentes:** poucos vínculos médicos por competência têm algum campo
  de horas vazio, quase todos no hospitalar SUS, e nenhum valor é não
  numérico, não inteiro ou negativo (tabela no resumo e
  `horas_ausentes_por_competencia` no manifesto). São os mesmos vínculos em
  todas as competências (mesmo estabelecimento, profissional e CBO), o que
  sugere registros antigos não atualizados. No painel, só as células que os
  contêm ficam com horas ausentes. A reextração encontrou o mesmo SHA-256 da
  rodada anterior em todas as competências.
- **Família 2231:** presente em todas as competências, dominada pelo médico
  residente (2231F9); entra só em `todos_medicos`.
- **Validação:** o portão foi **aprovado**. Nas competências em que o ZIP é
  o mesmo do ciclo 1 (SHA-256 igual), as células são idênticas. As competências
  mais recentes do ciclo 1 foram republicadas pelo DATASUS depois de 30/08/2026
  (SHA-256 diferente); nelas restam diferenças de uma unidade em poucas células,
  compatíveis com atualização retroativa do cadastro.

## 7. Limites

- CNES é cadastro: vínculo e carga horária declarados, não presença nem horas
  realizadas.
- `n_profissionais_distintos` é distinto dentro do município; quem atua em dois
  municípios conta nos dois.
- A ponte curso–CBO é operacional, não crosswalk oficial (ver a própria ponte).
- O painel é insumo do E7. Nenhum contraste por corte foi feito aqui.

## 8. Reprodução

```bash
python3 scripts/aquisicao/a09_adquirir_cnes_nacional.py            # aquisição + painel
python3 scripts/aquisicao/a09_adquirir_cnes_nacional.py --etapa painel  # só refaz o painel do cache
python3 -m unittest tests.test_cnes_nacional
```

A aquisição é idempotente e retomável: competência com cache e metadado não é
baixada de novo; ZIP local íntegro é reaproveitado. Quatro a seis downloads
correm em paralelo (cerca de 1 MB/s por conexão).
