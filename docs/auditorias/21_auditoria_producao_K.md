# Auditoria independente da família K (protocolo 47, doc 50)

> **Data:** 19/10/2026.<br>
> **Objeto:** commit `1c35900`, com `scripts/rdd_bolsa/21_producao_dird.py` (D1),
> `22_chegada_pmme_evento.py` (D2), as saídas `output/rdd_bolsa/K_D1_*` e `K_D2_*`,
> [`06_execucao/50`](../06_execucao/50_resultados_producao_especializada.md) e
> `tests/test_producao_K.py`. Referência: o protocolo congelado
> [`06_execucao/47`](../06_execucao/47_protocolo_producao_especializada.md), com
> os adendos §10 e §11, e as aquisições
> [`A12`](aquisicao/A12_sia_tabnet.md), [`A13`](aquisicao/A13_sih_tabnet.md) e
> [`A14`](aquisicao/A14_tiss_ans.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.**
> - O D1 foi reproduzido de forma independente, até a precisão de máquina, e
>   não muda.
> - O D2 também foi reproduzido. Ele foi corrigido num ponto de codificação: 20
>   municípios cuja 1ª chegada é posterior ao fim da série estavam contados
>   como tratados. A correção muda pouco os números e nenhuma conclusão.
> - As figuras foram refeitas, para leitura por não especialistas.
> - O teste de integridade que estourava a memória foi corrigido, sem mudar o
>   que ele confere.
>
> **Proveniência dos números:** os valores citados aqui foram lidos de
> `output/rdd_bolsa/K_D1_estimativas.csv` e `K_D2_estimativas.csv`, antes da
> correção (commit `1c35900`) e depois dela. A conferência independente está
> versionada em `tests/test_producao_K.py`, na classe
> `TestRecalculoIndependenteAuditoria21` e no teste
> `test_chegada_depois_do_fim_da_serie_fica_ainda_nao_tratada`.

## 1. Como a auditoria foi feita

O código de conferência foi escrito do zero. Ele não importa o 21, o 22 nem a
`rdd_lib`.

**Leitura dos dados:**
- só os painéis de aquisição: SIA, SIH, TISS ambulatorial e CNES nacional;
- o painel SIA (64 milhões de linhas) foi lido com filtros do pyarrow, um
  conjunto de CBO por vez;
- população: Censo 2022;
- running variable: `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`,
  arredondado a milésimos;
- `data/ivs_ipea_2010_municipios.csv` não foi lido;
- a lista nominal foi lida só nas colunas `co_ibge` e `dt_inicio_atividade`.

**Estimação:**
- D1: MQP ponderado escrito à mão, kernel triangular, h = 0,050;
  - EP HC1 por corte;
  - empilhado com intercepto, inclinação e inclinação × lado por corte, salto
    comum e EP CR1 por município (a convenção do E7);
  - Holm entre K1–K3, MDE = 2,8 × EP e efeito relativo, todos refeitos.
- D2: Callaway–Sant'Anna implementado do zero:
  - ATT(g, t) com base g − 1;
  - controles nunca tratados e ainda não tratados (G > max(t, g − 1));
  - θ(e) ponderado pelo tamanho das coortes;
  - ATT médio do pós;
  - Wald do pré com funções de influência derivadas à parte;
  - inferência independente por **bootstrap não paramétrico de municípios**
    (499 reamostragens), em vez do bootstrap multiplicador do script.

## 2. Construção dos outcomes

| Conferência | Resultado |
|---|---|
| Universo U = a08 com população 2022 > 0 | 5.565 municípios; os 5 municípios do Censo sem IVS oficial e o 510183 (sem população) ficam fora, como declarado |
| SIA: `-` do TabNet = zero | todo `zero_tabnet` tem quantidade 0 e todo `valor_tabnet` > 0; nenhum `municipio_ausente_da_resposta` |
| SIA: subgrupo omitido da resposta = zero daquela consulta | em cada mês × subgrupo presente aparecem os 5.571 municípios do formulário; a soma por tipo trata o subgrupo omitido como zero (regra V4 do a12) |
| SIA: soma dos municípios de U contra o total do TabNet (alvo_pmme, 0301 + 02 + 04 + 09) | 99,988% a 99,999% do total em todos os meses; a diferença são os 6 municípios fora de U |
| SIH: UF-mês sem dado = ausente | 37 células ausentes: AC (22) e RR (15) em 202607; nenhuma outra |
| TISS: `ausente_*` = ausente; `arquivo_presente_municipio_sem_evento` = zero | não há UF-mês ausente no período; zeros só em pacote aprovado |
| Janelas | pré 202406–202506; pós 202510–202605 (K1, K2, K4); pós 202510–202512 (K3); média dos meses com dado |
| ΔY por município (5 municípios: 355030, 292740, 150140, 260410, 172100) | a leitura direta do parquet, município a município, e as matrizes agregadas dão o mesmo ΔY de K1, K2 e K3 até a 6ª casa |

## 3. D1: recálculo independente

As diferenças absolutas entre o código da auditoria e o CSV são no máximo
2 × 10⁻¹³, no salto e no EP de todas as linhas abaixo.

| Outcome | Corte | Salto (auditoria = CSV) | EP | p | n abaixo / acima |
|---|---|---|---|---|---|
| K1 | 0,300 | −3,9612 | 25,8760 | 0,8783 | 859 / 654 |
| K1 | 0,400 | +23,1643 | 24,6896 | 0,3481 | 587 / 603 |
| K1 | empilhado | +7,9196 | 18,1140 | 0,6620 | 1.446 / 1.257 |
| K2 | 0,300 | +0,4181 | 0,5424 | 0,4408 | 859 / 654 |
| K2 | 0,400 | +0,4114 | 0,9311 | 0,6586 | 587 / 603 |
| K2 | empilhado | +0,4152 | 0,5090 | 0,4147 | 1.446 / 1.257 |
| K3 | 0,300 | −19,4505 | 14,0576 | 0,1665 | 859 / 654 |
| K3 | 0,400 | +20,7282 | 16,5527 | 0,2105 | 587 / 603 |
| K3 | empilhado | −1,8525 | 10,7385 | 0,8630 | 1.446 / 1.257 |
| KP1 | empilhado | −42,0515 | 101,4093 | 0,6784 | 1.446 / 1.257 |
| KP2 | empilhado | −11,7312 | 25,1220 | 0,6405 | 1.446 / 1.257 |
| K1d | empilhado | −3,8116 | 33,4270 | 0,9092 | 1.446 / 1.257 |
| K4.vinculos | empilhado | +0,0789 | 0,0456 | 0,0837 | 1.446 / 1.257 |
| KP3 de K1 | empilhado | +5,9334 | 13,4882 | 0,6600 | — |
| KP3 de K2 | empilhado | +0,5099 | 0,7275 | 0,4834 | — |
| KP3 de K3 | empilhado | +0,7946 | 6,4678 | 0,9022 | — |

- **Holm (K1–K3):** p ajustado = 1,000 nas três, igual ao CSV.
- **MDE e efeito relativo:** batem em todas as linhas:
  - MDE de K1, K2 e K3 = 50,72; 1,43; 30,07;
  - média do pré abaixo do corte = 288,29; 10,81; 141,89;
  - efeito relativo = +2,7%; +3,8%; −1,3%.
- **Estudo de evento** (empilhado, U, 41 meses de 202201 a 202505), meses com
  p < 0,05, refeitos mês a mês:

  | Outcome | Meses com p < 0,05 |
  |---|---|
  | K1 | 0 |
  | K2 | 4 |
  | K3 | 1 |
  | KP1 | 23 |
  | KP2 | 0 |

  São os números do doc 50. Diferença máxima de salto contra o CSV: 7 × 10⁻¹³.

## 4. D2: recálculo independente

**Amostra.**
- 598 municípios com célula nos ciclos 1 ou 2 e em U.
- 315 com especialista ativo.
- Coortes trimestrais:
  - 2025-07: 130;
  - 2025-10: 34;
  - 2026-01: 47;
  - 2026-04: 104.
- 10 municípios da lista nominal ficam fora da amostra.

**Antes da correção, o código da auditoria reproduz exatamente o CSV:**

| Outcome | ATT médio do pós | EP (IF) | Wald do pré (gl), p | EP bootstrap do script | EP bootstrap não paramétrico (auditoria) |
|---|---|---|---|---|---|
| K1 | +31,3705 | 18,4445 | 23,111 (23), 0,4543 | 18,63 | 18,90 |
| K1d | +65,0273 | 32,0911 | 26,543 (23), 0,2759 | 32,30 | 32,38 |
| K4.vinculos | −0,1308 | 0,0614 | 26,037 (22), 0,2501 | — | — |
| K2 | +0,7729 | 0,8837 | 38,929 (23), 0,0202 | — | — |

- **Bootstrap não paramétrico:** dá EP 1–2% maior que o do script.
- **Wald do pré com a covariância do bootstrap:**
  - K1: p = 0,38;
  - K1d: p = 0,23.

  A conclusão sobre o pré não muda.

## 5. Achados e correções

### A1 (corrigido). D2: chegadas posteriores ao fim da série contadas como tratadas

O 22 data a coorte pelo 1º mês do trimestre da chegada. O teste "chega depois
do fim da série → ainda não tratado" era feito sobre o início do trimestre, e
não sobre o mês da chegada.

- 20 municípios têm a 1ª chegada em 202606.
- Por esse teste, eles caíam na coorte 2026-04 e contavam como tratados em
  202604 e 202605.
- Na série, que acaba em 202605, eles não têm nenhum mês de exposição.

Isso contradiz o §5 D2, que manda tratar esses municípios como ainda não
tratados, e a própria regra que o script declarava.

**Correção:** o teste passa a usar o mês da chegada (`indices_coorte`). A
tabela da amostra do doc 50 mostra os municípios afetados:
- 20 nas séries de SIA, SIH e CNES;
- 151 em K3, que já eram ainda não tratados no horizonte de K3.

Um teste novo cobre o caso, e a correção entrou como linha datada na tabela de
desvios do D2.

| Outcome | Antes: ATT [IC 95%], p; Wald p | Depois: ATT [IC 95%], p; Wald p |
|---|---|---|
| K1 | +31,37 [−5,14; +67,88], 0,092; 0,454 | +32,97 [−3,82; +69,75], 0,079; 0,538 |
| K1d | +65,03 [+1,72; +128,33], 0,044; 0,276 | +66,14 [+1,93; +130,35], 0,043; 0,372 |
| K2 | +0,77 [−0,97; +2,52], 0,385; 0,020 | +0,72 [−1,03; +2,47], 0,418; 0,028 |
| K4.vinculos | −0,13 [−0,25; −0,01], 0,035; 0,250 | −0,13 [−0,26; −0,01], 0,031; 0,141 |
| KP1 | −110,66, 0,496; 0,115 | −103,15, 0,520; **0,021** |
| K3 | +32,32 [−23,46; +88,11], 0,256; 0,307 | igual (coortes ≤ 202512) |

- Tratados / nunca tratados: de 315 / 283 para 295 / 303 nos outcomes de SIA,
  SIH e CNES.
- O código da auditoria, com a mesma regra, dá os mesmos números do script
  corrigido. Exemplos: K1 +32,9693 e K1d +66,1418.
- Nenhuma conclusão muda.
- O pré de KP1 passa a rejeitar a 5%, e o doc 50 o relata como "não plano".

### A2 (corrigido). D2: leitura da pré-tendência de K4.vinculos e de K1

A regra de ressalva do 22 marcava como "diferença já presente antes da
chegada" o outcome cujo θ médio do pré (−24 a −2) tem o mesmo sinal do ATT do
pós e pelo menos metade do tamanho. Ela tinha dois problemas.

**K4.vinculos.** Depois de A1, o θ médio do pré de K4.vinculos passou a −0,06,
contra ATT −0,13. A ressalva sumia. Mas a figura mostra θ em torno de −0,1 nos
12 meses antes do mês-base.

- **Correção:** a regra também considera a média dos 12 meses antes do
  mês-base (−13 a −2). Para K4.vinculos ela é −0,09.
- O acréscimo só põe ressalva, nunca a tira.
- A ressalva também aparece na leitura de substituição do D2, onde K4.vinculos
  era "cai" sem ressalva.

**K1.** O pré de K1 fica em média do lado oposto: θ médio do pré −27,28,
contra ATT +32,97.

- Isso indica que o ATT depende do mês-base.
- Uma subida que começou antes da chegada não é descartada pelo Wald.
- Foi acrescentada uma frase gerada para esse caso.

### A3 (corrigido). D2 sem correção para múltiplos testes

O D2 tem 11 outcomes. 2 deles têm p < 0,05 (K1d e K4.vinculos), contra cerca
de 0,6 esperados por acaso. O doc 50 não dizia isso. A frase agora é gerada, e
o limite está na seção 10 do doc.

### A4 (corrigido). Figuras

As 14 figuras do D1 e as 11 do D2 foram abertas uma a uma. Foram encontrados
quatro problemas.

1. **Estudo de evento do D1.** Os rótulos verticais dos atos ficavam dentro do
   primeiro painel e cobriam pontos e barras.
   - Agora são números no alto do painel, com a chave no "COMO LER".
   - O texto explica os meses em branco de transição (jul–set/2025) e a
     falta de pontos do CNES antes de jun/2024 (só competências trimestrais).
   - A legenda só mostra "meses só da sensibilidade" quando eles existem: em
     K3 não existem.
2. **DiRD do D1.**
   - O texto "salto" ao lado da seta cobria o ponto vizinho ao corte. Saiu, e
     a legenda e o título continuam explicando a seta. A opção
     `rotulo_salto=False` é nova em `23_estimar_contagem_vagas.desenhar`; o
     padrão mantém as figuras da família N.
   - O "COMO LER" de K4 falava em "produção". Agora usa o substantivo do
     outcome.
   - O "COMO LER" avisa que um único município pode puxar a média de uma
     faixa.
3. **D2.** O fundo azul do pós e a banda uniforme azul eram quase iguais, e a
   banda sumia no pós. O fundo agora é bege e só cobre os tempos de evento
   estimados.
4. **Escala do D2.** Um único mês com IC enorme achatava todos os outros: em
   K1, e = −12 levava o eixo a ±1.500.
   - O eixo agora cobre todos os θ e os IC dos meses típicos.
   - O IC cortado ganha um triângulo, e o corte vem dito na legenda e no
     "COMO LER".
   - Os meses 0 e 1 podem ser anteriores à chegada, e o "COMO LER" agora diz
     isso.

### A5 (corrigido, prosa). KP2 e K1d incluem a CBO 225130

Pela regra do a09, `especialistas_nao_alvo` contém a 225130 (medicina de
família e comunidade). O doc 50 não dizia isso. Uma frase de prosa, sem número,
foi acrescentada na seção 1.

### A6 (corrigido, texto gerado). Estudo de evento de KP1

KP1 tem 23 de 41 meses do pré com p < 0,05, e o doc só dava a contagem. A
frase gerada nova:
- marca os outcomes com mais de 3 vezes os 5% esperados;
- mostra que 89% dos saltos mensais de KP1 têm o mesmo sinal, antes e depois
  de jun/2025.

Esse é o padrão de um mês de referência atípico, e não de uma tendência. A
DiRD, que compara médias de janelas, não depende desse mês.

### A7 (corrigido). Teste de integridade sem estouro de memória

`tests/test_integridade_dados.py::test_csv_e_parquet_rotulados_sao_empiricos`
lia com `pd.read_parquet` a coluna `natureza_dos_dados` inteira dos 64 milhões
de linhas do painel SIA e era morto por falta de memória.

**Correção:** o ramo parquet passa a fazer três coisas:
- confere o esquema;
- lê só a coluna com o pyarrow, como dicionário (`read_dictionary`);
- tira os valores distintos.

A semântica é a mesma:
- arquivo sem a coluna ou ilegível é pulado;
- nulos não contam;
- os rótulos são comparados em maiúsculas.

Os 23 parquets com a coluna foram conferidos contra a leitura antiga, nos que
cabem em memória, e deram o mesmo conjunto de rótulos.

### Observações sem correção (para o autor)

- **IC honesto inútil na prática.** No D1, a regra de bolso dá M da ordem de
  10⁶ (por 10 mil hab. por unidade de IVS²). Em K1, por exemplo, o IC honesto
  é [−929; +945], contra um IC convencional [−28; +43].
  - Isso é a `rdd_lib` aplicada como no E7, e o doc 50 o declara.
  - Esse IC não informa nada sobre a hipótese.
- **K4.vinculos em 0,400 (p = 0,040) depende em parte de um município.** O
  240790 tem 2.276 habitantes e seus vínculos não SUS por 10 mil hab. passam
  de 283 para 474.
  - Sem ele, o salto em 0,400 vai a +0,113 (p = 0,057) e o empilhado vai de
    p = 0,084 a p = 0,114.
  - Não foi reespecificado, porque seria escolha posterior ao resultado.
  - Fica como sensibilidade a propor ao autor.
- **K3 no D2.** O EP do bootstrap multiplicador, por intervalo interquartil,
  é 28,46 e o analítico é 20,89. Com 2 coortes e no máximo 6 meses de pós, a
  distribuição bootstrap tem caudas pesadas. O doc usa o EP maior, que é o
  conservador.
- **Dose do D2.** O denominador conta todos os especialistas da lista nominal
  do município, inclusive os que chegam depois da janela. A linha é rotulada
  DESCRITIVO.
- **Eventos de tempo 0 e 1 do D2.** A coorte trimestral (§5 D2) com tratamento
  a partir do 1º mês do trimestre dilui o ATT do pós. Na coorte 2025-07, todos
  chegam em 202509. Isso já estava declarado e agora está explícito no doc e
  nas figuras.

## 6. Rótulos, especificações e desvios declarados

**Rótulos.** Todas as 1.758 linhas do D1 e as 3.387 do estudo de evento
levam `EMPIRICO` e `PROTOCOLO_47_POS_SINTESE`. Todas as linhas do D2 levam
`EMPIRICO` e `EXPLORATORIO_PARTICIPACAO`.

**Linhas sem estimativa.**
- Não há linha `NAO_EXECUTADO`.
- As 6 linhas `SEM_ESTIMATIVA` são Poisson de K1f e de KP1.mfc em 0,400 e no
  empilhado, por falta de eventos num lado. Todas têm motivo na nota.
- As especificações fora do protocolo (`nivel_*` e `ic_honesto_h_otimo`) estão
  rotuladas `ESPECIFICACAO_ADICIONAL_AO_PROTOCOLO`.

**Cobertura do protocolo.**
- Primárias, secundárias e placebos do §4.
- Variantes do §10 (até 202607, sem o grupo 09, K1f, sem UF-mês atípico da
  SIH).
- Variantes do §11 (com TUSS 63, pós até 202511, sem UF-mês sinalizado,
  K3c).
- Robustez do §5 D1: média completa, h = 0,035 e 0,075, Poisson, IC honesto,
  estudo de evento desde 202201 e pré extra.

Todos estão presentes e são conferidos por `test_todas_as_especificacoes`.

| Desvio declarado | Julgamento |
|---|---|
| K1e ausente | correto: o protocolo (§4, §10, §11) define K1a–K1d e K1f; não há K1e |
| leitura de K3b | aceitável. O texto do §4 é ambíguo; a leitura escolhida (parte SIA de K3 no pós de 3 meses) é a única que separa janela (K1a × K3b) e fonte (K3 × K3b) |
| janela pós de K4 | aceitável. O protocolo não a dá; a mesma janela de K1 foi fixada antes de estimar, e a do E7 é sensibilidade. Nenhum mês ≥ 202609 é lido |
| medida de K3c (qt_itens) e de K4.horas | correto: segue o §3.2 e o §16 do protocolo 40; n_eventos é variante |
| S1 e randomização local não estimados | correto. O S1 não depende do outcome e está no E6 (linhas `S1` de `E6_estimativas.csv`). A randomização local não está no protocolo 47 |
| datação da coorte | aceitável como aproximação conservadora da coorte trimestral do §5 D2, mas com o erro A1, agora corrigido |

**Linguagem.** O doc 50 está adequado nos três pontos:
- O D1 é chamado de incentivo marginal num pacote: "somado ao que outras
  políticas com o mesmo corte mudaram".
- O D2 é chamado de ATT sob tendências paralelas: "comparação, não a prova de
  um efeito".
- "IC que inclui zero não prova que a bolsa não tem efeito".

Não há linguagem causal no D2. Os números do doc 50 vêm todos de blocos
gerados pelos scripts, e os testes `test_doc_bate_com_as_saidas` e
`test_sem_numero_digitado_fora_dos_blocos` passam.

## 7. Testes e determinismo

- `21_producao_dird.py` e `22_chegada_pmme_evento.py` rodados duas vezes em
  seguida: os 33 arquivos de saída (CSV, JSON, PNG e o doc 50) são idênticos
  byte a byte.
- O D1 corrigido não muda nenhum CSV nem o `K_D1_resumo.json`: mudam só as
  figuras e a frase gerada do estudo de evento.
- `tests/test_producao_K.py`: 40 testes passam. São 3 novos: o caso de A1 e os
  dois recálculos independentes, do D1 com Holm e do D2 em K1 e K1d.
- Suíte completa (`python -m pytest -q`): 920 testes coletados.
  - Rodada única com as correções de código: todos passaram, 2 pulados, sem
    estouro de memória, já com o teste de integridade corrigido.
  - Os módulos tocados depois, de K, integridade, N, pipeline e documentação,
    foram rodados de novo e passaram.

## 8. Números principais (depois da auditoria)

| Desenho | Outcome | Estimativa [IC 95%] | p | Leitura |
|---|---|---|---|---|
| D1 (U, empilhado) | K1 | +7,92 [−27,58; +43,42] por 10 mil hab./mês | 0,662 (Holm 1,000) | +2,7% da média do pré; MDE 50,72 (17,6%) |
| D1 | K2 | +0,42 [−0,58; +1,41] | 0,415 (Holm 1,000) | +3,8%; MDE 1,43 (13,2%) |
| D1 | K3 | −1,85 [−22,90; +19,19] | 0,863 (Holm 1,000) | −1,3%; MDE 30,07 (21,2%) |
| D2 (exploratório) | K1 | +32,97 [−3,82; +69,75] | 0,079 | pré: Wald p = 0,538, θ médio do pré de sinal oposto |
| D2 | K1d | +66,14 [+1,93; +130,35] | 0,043 | sem correção para múltiplos testes |
| D2 | K4.vinculos | −0,13 [−0,26; −0,01] | 0,031 | o pré dos 12 meses antes da base já está perto do pós |

Nenhuma primária do D1 rejeita zero depois do Holm. Isso não mostra efeito
zero: efeitos menores que o MDE não seriam detectados. O D1 mede, no máximo, o
incentivo marginal de R$ 5 mil dentro do pacote dos cortes. O D2 é ATT sob
tendências paralelas, sem fonte de exogeneidade validada.
