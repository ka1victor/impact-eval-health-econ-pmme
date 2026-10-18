# Construção dos outcomes do funil da bolsa (tarefa B do protocolo 40)

> **Execução:** 18/10/2026, antes de qualquer estimação do E6 e do E9.<br>
> **Protocolo:** [`40_protocolo_multioutcome_rdd_bolsa.md`](40_protocolo_multioutcome_rdd_bolsa.md)
> (famílias F0, F1, F2 e F4; adendo §12, E9).<br>
> **Script:** `scripts/rdd_bolsa/12_construir_outcomes_funil.py`. Aquisição do
> resultado da 1ª chamada do ciclo 2: `scripts/aquisicao/a10_adquirir_resultado_ciclo2_chamada1.py`.<br>
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
| `escolhas_conjunto_celulas.parquet` | E9: células com vaga imediata, por curso e ciclo | célula CNES × curso × ciclo |
| `dicionario_outcomes_funil.json` | fontes, colunas, decisões, casamento, desvios | — |

O número de linhas por população está em `n_por_populacao`. Cada saída tem
`natureza_dos_dados = "EMPIRICO"` e uma coluna `motivos_ausencia`. Essa coluna
diz, para cada valor ausente da linha, por que ele está ausente. O script para
se algum NaN não tiver motivo registrado. Os hashes das saídas estão em
`saidas`, e os das entradas, com data de referência, cobertura, unidade, chaves
e filtros, em `entradas`.

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
- **V2:** quadro retificado de 19/03/2026, a versão do P2 do E3 e a vigente na
  alocação final, mais o quadro da 2ª chamada (união, como no protocolo). As
  três versões do quadro da 1ª chamada têm as mesmas células e diferem nas
  vagas imediatas e de reserva (`versoes_do_quadro_ciclo2_chamada1`). A
  escolha só afeta `vagas_imediatas`, `vagas_cr` e `com_vagas_imediatas`.
- **V3:** quadro retificado de 24/07/2026.
- **Candidaturas:**
  - ciclo 1: alocação retificada sub judice, a versão canônica do A1/E4;
  - ciclo 2: resultado final da 1ª chamada, obtido nesta tarefa (seção 7);
  - ciclo 3: resultado final sub judice.
- **Ativos:** relação nominal do PMM-E, o mesmo arquivo do E3 (o SHA-256 é
  conferido) e a mesma leitura de `co_ibge` e `ciclo`.
- **PMMB:** consolidado, nível MUNICIPAL.
- **População:** Censo 2022.
- **G3:** cardápio de gestores do ciclo 3 e resultado final da adesão.

## 5. Definições

Os denominadores de F1 e F2.1 são todas as células do quadro da 1ª chamada,
inclusive as que só têm cadastro reserva, como no E3/E4.

| Id | Definição | Colunas |
|---|---|---|
| F0.1 | ciclo 1: célula no quadro da 1ª chamada; ciclo 2: na 1ª ou na 2ª; ciclo 3: na 1ª | `f0_1_tem_celula_c{k}`; diagnóstico com a reserva da 2ª chamada do ciclo 1: `f0_1s_tem_celula_c1_ch1_ou_ch2` |
| F0.2 | células e vagas imediatas do quadro da 1ª chamada por 10 mil habitantes (somar chamadas contaria vagas duas vezes) | `f0_2_*_c{k}` |
| F0.3 | aderiu = pediu ≥ 1 vaga; pedidas = priorizadas + não priorizadas; fração priorizada = priorizadas / pedidas; imediatas priorizadas | `f0_3_*` |
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
  - município sem ativo na relação nominal nacional;
  - município do cardápio sem linha na adesão, porque o resultado final é a
    lista completa de pedidos.
- Fica NaN, com motivo, o que é indefinido ou está fora do protocolo:
  - F1.4 e F2 do ciclo 3;
  - média de pontuação sem ninguém para pontuar;
  - fração priorizada sem vaga pedida;
  - IVS de município criado depois de 2010.

**E9 (adendo §12).**
- `escolhas_candidatos`: uma linha por candidato × opção, com:
  - curso, posto da opção, célula escolhida;
  - município e faixa impressa, ambos do quadro;
  - classificado, alocado, situação publicada, tipo de inscrição e pontuação.
- `escolhas_conjunto_celulas`: as células do quadro da 1ª chamada com vaga
  imediata, por curso e ciclo.
- Opção em célula que só tem cadastro reserva fica marcada
  (`celula_com_vaga_imediata = 0`) e não é descartada aqui. As contagens estão
  em `escolhas_E9_celula_escolhida_contra_quadro`.

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
     `output/aquisicao/a10_manifesto_ciclo2_chamada1.json`.
   - *Conferência cruzada:* o arquivo de remanescentes da mesma página tem o
     mesmo SHA-256 do que já estava no repositório.
   - *Consequência:* F1.1–F1.3 e F4 do ciclo 2 vêm do arquivo oficial, sem
     proxy.
2. **Data dos ativos.** O protocolo chama de "retrato de 09/10/2026" a versão
   publicada nessa data. A coluna `dt_referencia` do arquivo traz outra data.
   As duas ficam registradas, e o arquivo é o mesmo do E3.
3. **F2 do ciclo 3.** A relação nominal tem ativos do ciclo 3, mas F2 do ciclo
   3 não é construído. Ele está fora do protocolo (§3 e §5), e o ciclo 3 segue
   congelado.
4. **Identificador do candidato (E9).**
   - *Pedido:* o CPF mascarado como publicado.
   - *O que foi gravado:* um pseudônimo determinístico por ciclo
     (`id_candidato`), que agrupa as opções da mesma pessoa.
   - *Motivo:* regra do repositório (08a): nome, CPF e assinatura de CPF não
     vão para `output/`.
