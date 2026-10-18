# Construção dos outcomes do funil da bolsa (tarefa B do protocolo 40)

> **Execução:** 18/10/2026, antes de qualquer estimação do E6 e do E9.<br>
> **Protocolo:** [`40_protocolo_multioutcome_rdd_bolsa.md`](40_protocolo_multioutcome_rdd_bolsa.md)
> (famílias F0, F1, F2 e F4; E9 no §12, com o conjunto de escolha fixado no §14).<br>
> **Script:** `scripts/rdd_bolsa/12_construir_outcomes_funil.py`. Aquisição do
> resultado da 1ª chamada do ciclo 2: `scripts/aquisicao/a11_adquirir_resultado_ciclo2_chamada1.py`.<br>
> **Saídas:** `output/rdd_bolsa/outcomes/`.<br>
> **Testes:** `tests/test_outcomes_funil.py`.<br>
> **Natureza:** construção descritiva de outcomes. Não há contraste, nem
> estimativa, nem quebra por lado de corte, faixa ou IVS.

Este documento não traz contagens digitadas. Todo número (linhas, municípios,
taxas de casamento, versões, distribuições globais) é calculado pelo script e
lido de `output/rdd_bolsa/outcomes/dicionario_outcomes_funil.json`. As chaves
do JSON estão citadas abaixo.

## 1. Cegamento

- Nenhum outcome é quebrado por lado de corte, por faixa da bolsa ou contra o
  IVS. Também não há gráfico nem correlação com o IVS.
- O IVS 2010 oficial (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`)
  entra só como coluna de chave (`ivs_2010_oficial`). O arquivo local de IVS da
  [auditoria 16](../auditorias/16_ivs_2010_oficial_e_arquivo_local.md) não é
  lido, e o teste confere isso.
- A faixa impressa no quadro é atributo da célula. Só se confere que ela é
  única por município.
- Os resumos gravados (`resumo_global`) são distribuições globais: n,
  ausentes, média, mínimo e máximo.

## 2. Saídas

| Arquivo | População | Unidade e chave |
|---|---|---|
| `outcomes_U_municipio.parquet` | U: municípios com IVS 2010 oficial | município (`co_ibge`) |
| `outcomes_G3_municipio.parquet` | G3: cardápio de gestores do ciclo 3 | município (`co_ibge`) |
| `outcomes_V_municipio.parquet` | V1, V2 e V3 empilhados | município × ciclo |
| `outcomes_V_celula.parquet` | células do quadro da 1ª chamada de cada ciclo | célula CNES × curso × ciclo |
| `escolhas_candidatos.parquet` | E9: candidatos da 1ª chamada de cada ciclo | candidato × opção ranqueada |
| `escolhas_conjunto_principal.parquet` | E9 principal (§14): todas as células do curso e ciclo no quadro da 1ª chamada | célula CNES × curso × ciclo |
| `escolhas_conjunto_sensibilidade_vaga_imediata.parquet` | E9 sensibilidade (§12): só células com vaga imediata | célula CNES × curso × ciclo |
| `dicionario_outcomes_funil.json` | fontes, colunas, decisões, casamento, conferências, desvios | — |

O número de linhas por população está em `n_por_populacao`. Toda saída tem
`natureza_dos_dados = "EMPIRICO"` e a coluna `motivos_ausencia`.

`motivos_ausencia` é um objeto JSON `{coluna: motivo}` com as colunas NaN da
linha, ou `{}` se não há nenhuma. JSON evita ambiguidade de separador, porque
um motivo pode conter qualquer caractere. O script para se algum NaN não tiver
motivo registrado ou aparecer fora de onde o motivo se aplica (ciclo ou
condição).

Os hashes das saídas estão em `saidas`. Os das entradas, com data de
referência, cobertura, unidade, chaves e filtros, estão em `entradas`.

## 3. A célula como unidade

Nenhum arquivo público tem identificador persistente de vaga
(`output/aquisicao/a01_inventario_versoes.json`). Por isso o gate do A1
(auditoria 08) bloqueou "candidaturas por vaga". O protocolo define os outcomes
**por célula oferecida**. A célula é CNES (7 dígitos) × código do curso
(número inicial do rótulo), e essa chave existe em todos os arquivos.

Regras de casamento:
- as colunas são localizadas pelo nome do cabeçalho, não pela posição;
- linhas de candidatura e alocação são casadas com o quadro da 1ª chamada do
  ciclo só pela célula;
- o município sempre vem do quadro, pela célula, e nunca do IBGE impresso no
  arquivo de resultado;
- linha cuja célula não está no quadro não é atribuída a nenhuma célula e é
  contada à parte.

As taxas estão em `casamento_entre_arquivos.candidaturas_contra_quadro_da_1a_chamada`:
linhas, linhas casadas, taxa, linhas fora do quadro, pessoas distintas, linhas
por opção, pessoas sem linha de 1ª opção e situações publicadas. Os outros
blocos são:
- `escolhas_E9_celula_escolhida_contra_quadro`, para o E9;
- `ativos`, para a relação nominal;
- `adesao_ciclo3`;
- `pmmb`.

No resultado da 2ª chamada do ciclo 2, o IBGE impresso diverge do IBGE do quadro
em algumas linhas. Nelas, o nome do município impresso no próprio arquivo bate
com o IBGE do quadro (`linhas_ibge_divergente_nome_bate_com_ibge_do_*`). É mais
uma razão para tirar o município do quadro.

## 4. Fontes e versões

- **V1:** quadro original da 1ª chamada do ciclo 1, a mesma população de
  células do E3/E4. A conferência contra `quadro_vagas_tratamento.parquet`
  falha fechada.
- **V2:** o protocolo define V2 como a união dos quadros da 1ª e da 2ª
  chamada. O script usa as células do quadro retificado de 19/03/2026 (a versão
  do P2 do E3 e a vigente na alocação final). Ele **para** se o quadro da 2ª
  chamada acrescentar célula ou município (conferência
  `V2_2a_chamada_nao_acrescenta_celula_nem_municipio`). Como não acrescenta, a
  união coincide com a 1ª chamada.
  - As três versões do quadro da 1ª chamada têm as mesmas células e diferem
    nas vagas imediatas e de reserva (`versoes_do_quadro_ciclo2_chamada1`).
  - A escolha de versão só afeta `vagas_imediatas`, `vagas_cr` e
    `com_vagas_imediatas`.
- **V3:** quadro retificado de 24/07/2026.
- **Candidaturas:**
  - ciclo 1: alocação retificada sub judice, a versão canônica do A1/E4;
  - ciclo 2: resultado final da 1ª chamada, obtido nesta tarefa (seção 7);
  - ciclo 3: resultado final sub judice.
- **Ativos:** relação nominal do PMM-E, o mesmo arquivo do E3 (o SHA-256 é
  conferido) e a mesma leitura de `co_ibge` e `ciclo`.
- **PMMB:** consolidado, nível MUNICIPAL.
- **População:** Censo 2022.
- **Estrato territorial:** tipologia A2, só a coluna `estrato`.
- **G3:** cardápio de gestores do ciclo 3 e resultado final da adesão.

**Conferências que o script faz e que o fazem parar** (bloco `conferencias`):
- F1.3 e F1.4 do ciclo 1 iguais a Y1 e Y2 do E4;
- V1 e V2 iguais às populações P1 e P2 do E3;
- F2.3 igual a D_k, calculado pelas próprias funções do E3;
- as células do ciclo 1 iguais à população canônica;
- a 2ª chamada do ciclo 2 não acrescenta célula nem município;
- a macrorregião impressa no quadro igual ao 1º dígito do IBGE.

Os testes repetem as conferências com o E3 e o E4, lendo os alvos de `output/`.

## 5. Definições

Os denominadores de F1 e F2.1 são todas as células do quadro da 1ª chamada,
inclusive as que só têm cadastro reserva, como no E3/E4.

| Id | Definição | Colunas |
|---|---|---|
| F0.1 | ciclo 1: célula no quadro da 1ª chamada; ciclo 2: na 1ª ou na 2ª; ciclo 3: na 1ª | `f0_1_tem_celula_c{k}`; diagnóstico com a reserva da 2ª chamada do ciclo 1: `f0_1s_tem_celula_c1_ch1_ou_ch2` |
| F0.2 | células e vagas imediatas do quadro da 1ª chamada por 10 mil habitantes (somar chamadas contaria vagas duas vezes) | `f0_2_*_c{k}` |
| F0.3a | 1 se o município **consta** do resultado final da adesão, 0 se **não consta**. Não constar não é "não pediu" (ver abaixo) | `f0_3a_consta_do_resultado_final_adesao` |
| F0.3 | só para quem consta: vagas pedidas = priorizadas + não priorizadas; fração priorizada = priorizadas / pedidas; imediatas priorizadas. Quem não consta fica NaN, com o motivo "não consta do resultado final de adesão" | `f0_3_*` |
| F0.4 | PMMB: `total_vagas_ativas` e `total_ocupadas` por 10 mil habitantes | `f0_4_*` |
| F1.1 | linhas candidato × opção com a célula como 1ª opção, por célula | `f1_1_*`; sensibilidade sem "SEM PRÉ-REQUISITO" (só existe no ciclo 1): `f1_1s_*` |
| F1.2 | célula com ≥ 1 candidatura em qualquer opção | `f1_2_*` |
| F1.3 | ciclo 1: Y1 do E3/E4, da fonte canônica do A1. Ciclos 2 e 3: ≥ 1 linha "ALOCADO*" no resultado da 1ª chamada | `f1_3_*`; sensibilidades: só células imediatas, remanescentes (ciclo 2), "SUB JUDICE" (ciclo 3) |
| F1.4 | ciclo 1: Y2 do E4. Ciclo 2: F1.3 ou ≥ 1 alocado na 2ª chamada na mesma célula. Ciclo 3: não definido | `f1_4_*` |
| F2.1 | ativos do ciclo no município (qualquer estabelecimento) / células; na célula, ativos na própria célula | `f2_1_*` |
| F2.2 | ativos do ciclo por 10 mil habitantes, em U, com zero onde não há ativo | `f2_2_*_c{k}` |
| F2.3 | D_k do E3: ≥ 1 ativo do ciclo no município | `f2_3_d_k_algum_ativo_do_ciclo` |
| F4.1 | média, por pessoa, da pontuação dos alocados na 1ª chamada | `f4_1_*` |
| F4.2 | média, por pessoa, da pontuação dos candidatos de 1ª opção | `f4_2_*` |

**Regra de publicação do resultado da adesão** (`regra_publicacao_resultado_adesao`).
- No Edital SGTES/MS nº 2/2025 (adesão de gestores):
  - os itens 2.2.1, 2.3.1, 3.6 e 4.4 dizem que a lista preliminar e o
    resultado final são publicados "com base nas informações enviadas";
  - o item 3.5 permite à SGTES excluir o ente que não atender aos critérios;
  - nenhum item diz que toda proposta enviada aparece no resultado.
- Do ciclo 3 (Edital nº 25/2026), o repositório só tem a página de anexos; o
  texto do edital não foi examinado.
- Por isso a ausência no resultado não é codificada como pedido zero.

**Pontuação (F4).** Cada ciclo usa a pontuação com que o seu resultado final
classifica:
- ciclos 1 e 3: "PONTUAÇÃO NO BAREMA (GERAL)";
- ciclo 2: "PONTUAÇÃO FINAL".

No ciclo 2 a pontuação final não é o barema do resultado preliminar. Na 2ª
chamada do mesmo ciclo ela é barema mais tempo (`escala_pontuacao_ciclo2`).
Como as escalas não são idênticas, o empilhamento usa efeito fixo de ciclo.

**Zeros e ausentes.**
- Zero aparece só onde o arquivo completo observa zero:
  - célula oferecida sem candidatura;
  - município fora do quadro;
  - município sem ativo na relação nominal nacional.
- Fica NaN, com motivo, o que é indefinido, não observado ou está fora do
  protocolo:
  - F1.4 e F2 do ciclo 3;
  - média de pontuação sem ninguém para pontuar;
  - pedidos de adesão de município que não consta do resultado;
  - IVS de município criado depois de 2010.

**E9 (§12 e §14).**
- `escolhas_candidatos`: uma linha por candidato × opção ranqueada, com:
  - curso, posto da opção e célula escolhida;
  - município e faixa impressa, ambos do quadro;
  - classificado, alocado, situação publicada e pontuação.
- O tipo de inscrição (cota) não é lido nem gravado, porque o E9 não precisa
  dele.
- **Conjunto principal (§14):** todas as células do curso e ciclo no quadro da
  1ª chamada, com ou sem vaga imediata. Os atributos são:
  - `tem_vaga_imediata` e `log_vagas_imediatas_mais_1`;
  - faixa impressa e município;
  - população do Censo 2022;
  - macrorregião (impressa no quadro e conferida com o IBGE);
  - estrato territorial.
- **Sensibilidade (§12):** só as células com vaga imediata, e só os candidatos
  cuja 1ª opção está nelas (`celula_com_vaga_imediata = 1` na linha de 1ª
  opção).
- **Conjunto por posto:** o conjunto de cada linha é o do curso da **própria
  opção** (`id_conjunto_escolha`). Alguns candidatos escolhem a 1ª e a 2ª
  opção em cursos diferentes. Para eles, o conjunto do posto 2 é o do curso da
  2ª opção. As contagens por ciclo estão em
  `candidatos_com_1a_e_2a_opcao_em_cursos_diferentes`.

## 6. Ressalvas dos arquivos de candidatura

- Nos ciclos 2 e 3, os desclassificados por pré-requisito ficam numa aba sem
  célula e não entram em F1. No ciclo 1, os "SEM PRÉ-REQUISITO" aparecem com
  opção, e daí vem a sensibilidade `f1_1s_*`.
- Há pessoas listadas só com a linha de 2ª opção
  (`pessoas_sem_linha_de_1a_opcao`). Elas contam em F1.2, não em F1.1.
- No ciclo 1, F4.1 usa as confirmações de local. Homologado sem confirmação não
  tem pontuação no arquivo de alocação.
- Alocações em células só de cadastro reserva existem e estão contadas
  (`linhas_alocadas_em_celula_so_cadastro_reserva`). Ficam no numerador de F1.3,
  porque o denominador inclui essas células.

## 7. Desvios (registrados também em `desvios` no JSON)

1. **Resultado da 1ª chamada do ciclo 2.**
   - *Situação:* faltava no repositório.
   - *Resolução:* foi obtido da página pública do Chamamento Público SGTES/MS
     nº 1/2026, bloco "1ª chamada", "Resultado final PMME - 2º Ciclo", e
     preservado com URL, data de captura e SHA-256 em
     `output/aquisicao/a11_manifesto_ciclo2_chamada1.json`.
   - *Metadados da planilha:* o manifesto também registra as datas de criação e
     de última modificação gravadas na planilha (`metadados_da_planilha`). A
     criação coincide com a data do comunicado oficial do resultado. O sufixo
     "25-05" do nome do arquivo corresponde à última modificação.
   - *Conferência cruzada:* o arquivo de remanescentes da mesma página tem o
     mesmo SHA-256 do que já estava no repositório.
2. **Data dos ativos.** O protocolo chama de "retrato de 09/10/2026" a versão
   publicada nessa data. A coluna `dt_referencia` do arquivo traz outra data.
   As duas ficam registradas, e o arquivo é o mesmo do E3.
3. **F2 do ciclo 3.** A relação nominal tem ativos do ciclo 3, mas F2 do ciclo
   3 não é construído. Ele está fora do protocolo (§3 e §5), e o ciclo 3 segue
   congelado.
4. **F0.3.**
   - *Primeira versão:* codificava como "não aderiu", com pedido zero, o
     município do cardápio ausente do resultado final.
   - *Auditoria:* a auditoria independente de 18/10/2026 apontou que nenhum
     documento sustenta isso.
   - *Versão atual:* F0.3a registra só se o município consta ou não consta do
     resultado; os pedidos ficam NaN para quem não consta.
5. **Identificador do candidato (E9).**
   - *Pedido:* o CPF mascarado como publicado.
   - *O que foi gravado:* um pseudônimo determinístico por ciclo
     (`id_candidato`), que agrupa as opções da mesma pessoa.
   - *Motivo:* regra do repositório (08a): nome, CPF e assinatura de CPF não
     vão para `output/`.
6. **Numeração.** O script de aquisição e o manifesto passaram de `a10` para
   `a11`, para não colidir com outra tarefa.
