# Auditoria 36: os dados da H1 foram lidos certo? Reconstrução independente a partir dos arquivos brutos

> **Data:** 26/10/2026.<br>
> **Pergunta do autor:** "A gente não entendeu errado ou fez alguma besteira com os dados?"<br>
> **Objeto:** a queda estimada em 0,300 na H1. São três medidas, todas sobre a 1ª chamada:
> - célula aberta preenchida (A3, doc 49 §15);
> - vagas preenchidas por município, com controle das vagas oferecidas (N1, S-a);
> - taxa por vaga oferecida (S-e, que no doc 57l se chama Q2).
>
> **Documentos lidos:** 41a, protocolo 48, 49 (§2, §3, §15), 49b, 57l, auditoria 33 e A01.<br>
> **Método:** código próprio em `scripts/auditoria_H1/`, com três arquivos:
> - `a36_leitura.py`, o leitor dos brutos;
> - `a36_estimador.py`, o local linear com CR1;
> - `a36_reconstruir_H1.py`, que monta as bases, compara com o pipeline e estima.
>
> O código não importa os scripts 12, 23, 24 e 38, nem a `rdd_lib` ou qualquer script de `aquisicao/`.<br>
> **Entradas:**
> - os quadros e resultados em `data/raw/aquisicao/vagas/` e `data/raw/pmm_e/`, só lidos;
> - o IVS 2010 oficial (`output/aquisicao/a08_ivs_2010_oficial_municipio.csv`).
>
> Os SHA-256 estão em `output/auditoria_H1/a36_resumo.json` (`entradas`).<br>
> **Saídas:** `output/auditoria_H1/a36_*.csv` e `a36_resumo.json`. Toda linha leva `natureza_dos_dados = EMPIRICO`
> e `rotulo = AUDITORIA_36_RECONSTRUCAO`. As saídas só têm contagens por célula e por município, sem nome, CPF ou CRM.
> Nada em `output/rdd_bolsa/` foi alterado.<br>
> **Estatuto:** auditoria pós-resultado. As variantes da seção 5 são diagnósticos e não substituem a especificação
> principal do protocolo 48. O contraste é sempre o **pacote do corte**
> ([auditoria 18](18_politicas_nos_mesmos_cortes_ivs.md)): não é o efeito da participação no PMM-E nem do Agora Tem
> Especialistas.

## 1. Resposta curta

**Erro de dados: não.** A reconstrução a partir dos brutos reproduz as bases do pipeline uma a uma.

- **Células:** as 5.135 células (1.295 / 1.547 / 2.293 por ciclo) estão nas duas bases. Batem vagas imediatas,
  cadastro reserva (CR), candidatos de 1ª opção, alocados, faixa, IVS e código IBGE.
- **Municípios:** as 1.570 linhas município × ciclo também batem.
- **Estimativas:** as 32 linhas gravadas (A3, N1 S-a, N1 S-b e taxa S-e, por ciclo e corte) saem iguais. A maior
  diferença é 1,8e−13.
- **Divergência:** há só uma, e ela é de definição, já documentada. Em 6 municípios do ciclo 1, a contagem de
  células preenchidas usada no N2 (`n_celulas_preenchidas_ch1`) aceita confirmação **ou** homologação. Isso não
  entra no A3, no N1 nem na taxa.
- **Chaves:** não há erro de chave.
- **Arquivos:** nenhum arquivo errado é lido. O IVS do caminho da H1 é o oficial, e a faixa impressa bate com a
  regra em 100% dos municípios.
- **Sinal:** o sinal está certo. O salto é o lado de bolsa maior menos o de bolsa menor.

**Erro de entendimento: sim, um. Ele não cria o sinal negativo.**

O quadro do ciclo 2 que o pipeline usa é o retificado de 19/03/2026, e esse quadro foi refeito **depois** do
resultado preliminar (10/03). A ordem dos fatos:

- **Conversão:** a SGTES passou 630 vagas de CR para imediatas em 301 células.
- **Preenchimento:** 297 dessas 301 células receberam alocado. As 532 células que continuaram só de CR não
  receberam nenhum.
- **Alocados em reserva:** pelo quadro vigente na inscrição (13/02), 442 dos 1.057 alocados do ciclo 2 (42%)
  ficaram em células que eram só de cadastro reserva.

Por isso estão erradas duas coisas. A frase "no ciclo 2, vaga de reserva não podia ser preenchida na 1ª chamada"
(doc 57l e nota do doc 49 §2) não descreve o que aconteceu. E o "tipo de vaga" do ciclo 2 não é atributo
pré-tratamento: em boa parte, ele é o próprio resultado.

O que a correção muda:

| Medida | Corte 0,300 | Corte 0,400 |
|---|---|---|
| A3, ciclo 2 | de −10,2 p.p. para −25,6 p.p. | — |
| A3, ciclos empilhados | de −8,4 para −10,1 p.p. | de −1,3 para −4,1 p.p. |
| N1 e taxa por vaga | não mudam | não mudam |

N1 e taxa não mudam porque usam imediatas + CR, e esse total não muda entre as versões. A correção **aumenta** a
queda; não a explica.

**O que de fato acompanha a queda em 0,300 (diagnóstico pós-resultado, sem estatuto causal).** Os municípios logo
abaixo de 0,300 são, em boa parte, capitais. Na janela de 0,050 há 13 capitais abaixo do corte e 6 acima. A até
0,010 do corte, há 4 capitais abaixo e nenhuma acima:

| Capital | IVS |
|---|---|
| São Paulo | 0,291 |
| Goiânia | 0,291 |
| Natal | 0,292 |
| Brasília | 0,294 |

As capitais têm muitas células e preenchem mais. No corte, a parte das células que fica em capital cai 50 p.p.
(IC [−82; −18]), e a parte dos municípios que são capitais cai 17,8 p.p. (IC [−34,1; −1,5]). Com uma dummy de
capital, todos os intervalos passam a conter zero:

| Medida em 0,300 | Pipeline | Com dummy de capital |
|---|---|---|
| A3 | −8,4 p.p. | −2,6 p.p. [−11,8; +6,6] |
| Taxa por vaga | −16,0 p.p. | −10,9 p.p. [−22,6; +0,8] |
| N1 com controle | −1,45 | −0,92 [−1,98; +0,14] |

O ciclo 2 continua negativo na taxa: −23,4 p.p. (IC [−45,8; −0,9]). Em 0,400 nada muda de leitura.

## 2. O que foi reconstruído

| Ciclo | Quadro usado (e por quê) | Resultado da 1ª chamada | "Alocado" |
|---|---|---|---|
| 1 | `2025_ciclo1_chamada1_vagas.xlsx`, original de 24/07/2025 (único quadro da 1ª chamada) | `2025_ciclo1_chamada1_alocacao_retificada_subjudice.xlsx` (igual à retificada, salvo uma marca "Sub judice" numa linha não classificada) | "LOCAL DE ATUAÇÃO CONFIRMADO" (468) |
| 2 | Células e total do retificado de 19/03/2026 (igual ao pipeline). Tipo de vaga **pré-alocação**: retificado de 13/02/2026 (seção 3, item 3) | `resultado-final-pmme-2o-ciclo-25-05.xlsx` (sem coluna IBGE) | "ALOCADO - AC/ER/PCD" (1.057) |
| 3 | Retificado de 24/07/2026, anterior ao resultado de 25/08 (muda 4 vagas imediatas em relação a 16/07) | `2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx` | "ALOCADO - *" (704); "SUB JUDICE" (2) em variante |

**Chave da célula.** A chave é o CNES com 7 dígitos mais o código do curso (o número inicial do rótulo). Município
e faixa vêm do quadro.

**Variáveis por célula** (`a36_celulas.csv`):
- vagas imediatas e de CR nas versões relevantes;
- candidatos de 1ª opção e alocados;
- no ciclo 1: desconsiderados, realocados do Quadro 2 e homologados;
- no ciclo 2: alocados no resultado preliminar e nos dois arquivos de remanescentes;
- no ciclo 3: SUB JUDICE;
- faixa impressa, IVS oficial e faixa pela regra.

`a36_municipios.csv` agrega as células por município × ciclo.

## 3. Checklist

### 1. Definição de "preenchida" entre ciclos

**Veredito: não há inconsistência no A3, no N1 nem na taxa.**

- **O que o pipeline usa.** A3, N1 e a taxa usam a mesma regra nos três ciclos: ≥ 1 alocado. No ciclo 1, o alocado
  é o confirmado (`n_alocados_ch1` = confirmações). A outra definição, "confirmação ou homologação", vale só para o
  F1.3 do E3/E6 e para o N2. Ela muda 6 linhas (tabela de divergências).
- **Diferença de nível entre ciclos.** Ela existe: as células preenchidas são 29,9% no ciclo 1, 47,1% no ciclo 2 e
  21,7% no ciclo 3. Mas é absorvida, porque o A3 tem efeito fixo de curso × ciclo e todas as linhas têm reta e
  intercepto por ciclo.
- **Mistura de ciclos perto do corte.** Ela difere entre os lados. A até 0,010 de 0,300, os ciclos 1/2/3 somam
  14% / 31% / 55% das células abaixo e 26% / 33% / 40% acima. Por isso a média crua da janela, sem efeito de ciclo,
  não é comparável à estimativa.
- **Definições alternativas.** Mudam pouco o salto em 0,300 (seção 5):
  - F1.3 no ciclo 1: −7,9 p.p.;
  - ciclo 1 com "classificado", isto é, confirmado mais desconsiderado na célula original: −7,8 p.p.;
  - ciclo 1 com os realocados do Quadro 2: −8,1 p.p.;
  - ciclo 3 com SUB JUDICE: −8,5 p.p.;
  - o pipeline: −8,4 p.p.

### 2. Células só de cadastro reserva no denominador

**Veredito: os editais permitem preencher reserva na 1ª chamada, e isso aconteceu nos três ciclos. Pôr essas
células no denominador não é erro de regra. Mas elas se preenchem por outro mecanismo, e a queda em 0,300 vem
sobretudo delas.**

**Ciclo 1 (Edital SGTES/MS nº 3/2025):**
- item 4.1.3.3: "O candidato poderá escolher, dentre suas opções, município com vaga para preenchimento imediato e
  município que esteja em cadastro de reserva";
- item 4.1.3.4: o município em reserva "poderá recebê-la por remanejamento, caso outro município com vaga
  disponível não tenha lista de espera";
- item 5.7: as vagas imediatas não preenchidas "poderão ser redistribuídas para municípios com cadastro de reserva
  e que tenham candidatos na lista de espera, respeitando a priorização de localidades inseridas em regiões de saúde
  com maior dificuldade de acesso [...] e com comprovada escassez de médicos especialistas".

**Ciclo 3 (Edital SGTES/MS nº 28/2026):** os itens 4.1.3.3, 4.1.3.4 e 5.7 têm o mesmo teor.

**Ciclo 2:** o repositório não tem o texto do Edital nº 3/2026. O quadro original de 03/02 diz que o cadastro
reserva "poderá ter vagas ofertadas em chamadas futuras". Na prática, a reserva foi preenchida na 1ª chamada pela
conversão de 19/03 (item 3).

**Alocados em células só de CR, pela versão anterior à alocação:**

| Ciclo | Alocados em células só de CR | Total de alocados | Células só de CR preenchidas | Células só de CR | % preenchidas, só de CR | % preenchidas, com imediata |
|---|---|---|---|---|---|---|
| 1 | 211 | 468 | 175 | 782 | 22,4% | 41,3% |
| 2 | 442 | 1.057 | 297 | 833 | 35,7% | 60,4% |
| 3 | 131 | 704 | 96 | 1.599 | 6,0% | 57,8% |

O preenchimento de uma célula só de CR depende de dois fatores administrativos: sobrar vaga imediata do curso e a
priorização da SGTES (item 5.7). Não depende só de o lugar atrair candidatos.

**Só células com vaga imediata (versão pré-alocação), em 0,300:**
- A3: de −8,4 para −3,7 p.p. (IC [−21,3; +13,9]);
- taxa: de −16,0 para −13,2 p.p. (IC [−29,0; +2,7]);
- por ciclo, o A3 fica em +0,8 / −21,0 / +7,2 p.p.

Ou seja, fora do ciclo 2 a queda do A3 depende das células só de reserva. Em 0,400, o A3 vai a −2,3 p.p.

### 3. Versão do quadro

**Veredito: há um erro de entendimento no ciclo 2. Os ciclos 1 e 3 estão certos. Não há dupla contagem entre
chamadas.**

**Ciclo 2: cronologia** (página do Chamamento nº 1/2026 e manifesto a11):

| Data | Evento |
|---|---|
| 03/02 | Quadro original: 899 imediatas e 1.998 de CR |
| 13/02 | Retificado: 1.206 e 1.686 |
| — | Inscrições |
| 10/03 | Resultado preliminar |
| 12–13/03 | Recursos |
| 19/03 | Retificado ("pmm-e-vagas-edital-2o-ciclo-19-de-marco-de-2026.xlsx"): 1.836 e 1.053 |
| 24/03 | Resultado final |

As células de 13/02 e de 19/03 são as mesmas (1.547). O total por célula só muda em 2.

| Alocados do resultado final contra o quadro | 03/02 | 13/02 | 19/03 |
|---|---|---|---|
| alocados em célula só de CR | 604 | 442 | **0** |
| células só de CR com alocado | 427 | 297 | **0** |
| alocados acima das imediatas da célula | 607 | 442 | **0** |

Contra o quadro de 13/02, o preliminar já tinha 286 alocados em células só de CR. Contra o de 19/03, sobram 2.

**Conversão de 13/02 para 19/03:**
- 301 das 833 células só de CR viraram imediatas, e 297 delas tiveram alocado;
- nenhuma das 532 que continuaram só de CR teve alocado;
- em todas as células, as imediatas de 19/03 são ≥ os alocados.

O quadro de 19/03 registra, portanto, o remanejamento feito depois das escolhas.

**Consequências da versão de 19/03:**
- o efeito fixo de "tipo de vaga" do A3 e o "célula só de CR" do D-b (57l) são, no ciclo 2, em parte o próprio
  outcome;
- o "Q2 sem as células só de CR" do ciclo 2 condiciona no resultado;
- a sensibilidade "só imediatas" do N1 também usa a versão pós-alocação.

**Ciclos 1 e 3:** cada um tem um só quadro da 1ª chamada antes do resultado. No ciclo 3, a retificação de 24/07
(4 vagas) precede o resultado de 25/08.

**Remanescentes e realocação:**
- **N1 e A3:** nenhum dos dois soma remanescentes, a 2ª chamada ou o Quadro 2 do ciclo 1. O N1 do ciclo 2 é
  exatamente 1.057, o "ALOCADO" do resultado final.
- **Quadro 2 do ciclo 1:** os 59 realocados são os 59 "desconsiderados" da alocação. Desses, 20 foram para células
  fora do quadro original e 21 para células só de CR. No pipeline, eles não contam nem na célula original nem na
  nova. Contá-los muda o salto em 0,3 p.p.
- **Sensibilidade com remanescentes** (`f1_3s_*_com_remanescentes`, fora da H1): ela soma dois arquivos diferentes,
  de 9 e de 81 linhas, com uma pessoa em comum. Quatro das 81 pessoas também estão entre os alocados do resultado
  final. Por ser indicador de célula, isso não infla contagens.

### 4. Chaves

**Veredito: não há problema de chave no caminho da H1** (`chaves` em `a36_resumo.json`).

| Verificação | Contagem |
|---|---|
| Linhas de quadro com IBGE de 7 dígitos | 0 (todos os quadros têm 6 dígitos) |
| Linhas de resultado com IBGE de 7 dígitos | 1.053, todas no resultado da 2ª chamada do ciclo 2 (fora da H1); 87 delas têm IBGE diferente do quadro, e por isso o município vem do quadro |
| Resultado da 1ª chamada do ciclo 2 | sem coluna IBGE; município pelo quadro |
| CNES em mais de um município, no mesmo quadro ou entre quadros | 0 |
| Município com mais de uma faixa | 0 |
| Código de curso com nomes diferentes entre quadro e resultado | 0 (comparação por nome normalizado, sem o prefixo numérico) |
| Linhas de resultado da 1ª chamada fora do quadro (c1 / c2 / c3) | 0 / 0 / 0 |
| Alocados ou confirmados fora do quadro | 0 nos três ciclos |
| Células do quadro sem nenhuma linha de resultado (c1 / c2 / c3) | 659 / 579 / 938: células sem candidato, zero verdadeiro |
| Realocados do Quadro 2 em células fora do quadro (ciclo 1) | 20 linhas, 19 células |
| Homologados do ciclo 1 em células fora do quadro | 20 linhas, 18 células |

### 5. Faixa e IVS

**Veredito: está correto.**

- **Faixa:** a faixa impressa é igual à regra do IVS oficial em 100% dos municípios × ciclo com IVS. A regra é
  IVS ≤ 0,300 → faixa 3; ≤ 0,400 → faixa 2; > 0,400 → faixa 1.
- **Corte:** os dois municípios com IVS exatamente 0,300 (Pederneiras e Quissamã) têm faixa 3 impressa. O corte
  fica do lado de baixo, como no pipeline.
- **IVS errado:** nenhum script do caminho da H1 lê `data/ivs_ipea_2010_municipios.csv` (12, 13, 23, 24, 38 e
  `rdd_lib`; conferência em `ivs_errado_no_caminho_H1`). Esta auditoria também não lê esse arquivo.
- **Município criado depois de 2010:** só Balneário Rincão (SC, 422000), no ciclo 3, sem IVS e fora da RDD.
- **Texto do edital:** o item 11.1.4 do Edital 3/2025 descreve as faixas pelas classes de vulnerabilidade. Os
  cortes efetivos, 0,300 e 0,400, são os que reproduzem 100% das faixas impressas. Isso confirma o portão R1.

### 6. Sinal

**Veredito: o sinal está certo.** O salto é a média do lado de cima (IVS > corte, bolsa maior: faixa 2 em 0,300) menos
a do lado de baixo.

**Reprodução das linhas gravadas.** Com o estimador próprio, as 32 linhas saem iguais
(`a36_gravado_contra_refeito.csv`):

| Medida | Ciclo 1 | Ciclo 2 | Ciclo 3 | Empilhado |
|---|---|---|---|---|
| A3 em 0,300 | +0,9 p.p. | −10,2 p.p. | −7,1 p.p. | −8,4 p.p. |
| Taxa em 0,300 | −12,5 p.p. | −27,8 p.p. | −10,7 p.p. | −16,0 p.p. |
| N1 S-a em 0,300 | −0,67 | −2,09 | −1,33 | −1,45 |

As janelas usam −h < x < h, como o pipeline. A tabela 5.3 traz as médias cruas por janela.

**O que as médias cruas mostram em 0,300, nos ciclos empilhados:**

| Janela | Células preenchidas, abaixo → acima | Diferença | IC 95% |
|---|---|---|---|
| ±0,050 | 33,3% → 33,5% | +0,2 p.p. | [−6,1; +6,4] |
| ±0,020 | 38,3% → 31,8% | −6,5 p.p. | [−17,2; +4,1] |
| ±0,010 | 45,4% → 31,1% | −14,3 p.p. | [−28,8; +0,2] |

O local constante com kernel triangular (h = 0,050) dá +0,7 p.p. A queda do local linear vem de inclinações
opostas dos dois lados, levadas até o corte, e de uma faixa estreita perto dele.

### 7. Municípios que puxam o resultado

**Veredito:** não há dado incompleto nem município com vaga e sem resultado publicado. A estimativa se apoia em
poucos municípios grandes, e o principal desequilíbrio é o de capitais.

**Os 5 mais próximos de 0,300 de cada lado**, com uma linha por ciclo em que há célula. "Imediatas pré" é a versão
de 13/02 no ciclo 2.

| Lado | Município | IVS | Faixa | Ciclo | Células (só CR pré) | Imediatas pré / imediatas + CR | Cand. 1ª opção | Alocados | Células preenchidas | Taxa |
|---|---|---|---|---|---|---|---|---|---|---|
| abaixo | Pederneiras (SP) | 0,300 | 3 | 3 | 2 (2) | 0 / 2 | 0 | 0 | 0 | 0% |
| abaixo | Quissamã (RJ) | 0,300 | 3 | 2 | 2 (2) | 0 / 2 | 0 | 1 | 1 | 50% |
| abaixo | Quissamã (RJ) | 0,300 | 3 | 3 | 1 (1) | 0 / 3 | 0 | 0 | 0 | 0% |
| abaixo | Lajinha (MG) | 0,299 | 3 | 2 | 1 (0) | 1 / 1 | 1 | 1 | 1 | 100% |
| abaixo | Goiás (GO) | 0,299 | 3 | 2 | 1 (0) | 2 / 2 | 2 | 2 | 1 | 100% |
| abaixo | Barueri (SP) | 0,298 | 3 | 2 | 1 (1) | 0 / 2 | 0 | 0 | 0 | 0% |
| abaixo | Barueri (SP) | 0,298 | 3 | 3 | 2 (2) | 0 / 4 | 1 | 0 | 0 | 0% |
| acima | Morro Agudo (SP) | 0,301 | 2 | 2 | 1 (1) | 0 / 1 | 0 | 0 | 0 | 0% |
| acima | Limoeiro do Norte (CE) | 0,302 | 2 | 2 | 1 (1) | 0 / 1 | 2 | 1 | 1 | 100% |
| acima | Limoeiro do Norte (CE) | 0,302 | 2 | 3 | 4 (3) | 1 / 8 | 3 | 1 | 1 | 12% |
| acima | Poá (SP) | 0,302 | 2 | 3 | 2 (2) | 0 / 2 | 0 | 0 | 0 | 0% |
| acima | Teófilo Otoni (MG) | 0,302 | 2 | 1 | 17 (13) | 4 / 25 | 7 | 5 | 5 | 20% |
| acima | Teófilo Otoni (MG) | 0,302 | 2 | 2 | 10 (7) | 8 / 24 | 3 | 3 | 2 | 12% |
| acima | Teófilo Otoni (MG) | 0,302 | 2 | 3 | 12 (10) | 3 / 31 | 3 | 1 | 1 | 3% |
| acima | Campos dos Goytacazes (RJ) | 0,303 | 2 | 2 | 12 (9) | 6 / 26 | 27 | 12 | 6 | 46% |
| acima | Campos dos Goytacazes (RJ) | 0,303 | 2 | 3 | 13 (6) | 15 / 39 | 17 | 7 | 5 | 18% |

**Leitura da tabela:**
- Os municípios a 0,001–0,002 do corte são pequenos e quase só de CR, com poucas células.
- Logo acima, Teófilo Otoni e Campos dos Goytacazes somam 64 células, quase todas só de CR, com preenchimento baixo.
- Nada indica dado faltante. As células sem alocado não tiveram candidato de 1ª opção, ou são só de CR num curso
  sem sobra de vaga imediata.
- Os números de 0,400 estão em `a36_vizinhos_0300_0400.csv`.

**Influência de cada município (A3 e taxa, 0,300, ciclos empilhados).** Refiz o salto tirando um município por vez
(linhas `unidade = influencia`). Nenhum município muda o sinal. As maiores mudanças:

| Município tirado | A3 | Taxa |
|---|---|---|
| Natal (0,292, 34 células) | −6,0 p.p. | −13,3 p.p. |
| Teresina (0,288, 67 células) | −6,2 p.p. | −13,5 p.p. |
| Teófilo Otoni | −7,0 p.p. | −13,4 p.p. |
| Campos dos Goytacazes | −10,5 p.p. | −18,2 p.p. |

**Capitais.** Na janela de 0,050 em torno de 0,300:

| Lado | Grupo | Municípios | Células | Células preenchidas | Taxa por vaga |
|---|---|---|---|---|---|
| abaixo | capitais | 13 | 392 | 43,4% | 27,8% |
| abaixo | demais | 132 | 788 | 28,3% | 19,9% |
| acima | capitais | 6 | 277 | 36,1% | 25,4% |
| acima | demais | 114 | 658 | 32,4% | 22,9% |

As 13 capitais abaixo são Curitiba, Boa Vista, Cuiabá, Campo Grande, Belo Horizonte, João Pessoa, Aracaju,
Teresina, Rio de Janeiro, Goiânia, São Paulo, Natal e Brasília. As 6 acima são Belém, Recife, Porto Velho,
Fortaleza, Macapá e Rio Branco.

Ser capital é pré-determinado e salta no corte:

| Medida no corte | Salto | IC 95% |
|---|---|---|
| Município × ciclo é capital | −17,8 p.p. | [−34,1; −1,5] |
| Célula em capital | −50,3 p.p. | [−82,4; −18,2] |

O D-e do doc 57l testou o nível REGIC, que não salta, mas não testou a condição de capital.

### 8. Alocados em 2ª opção

**Veredito: estão na célula certa.**

- Cada linha do resultado é candidato × opção, com a célula da opção. A linha marcada ALOCADO ou CONFIRMADO é a da
  célula onde a pessoa ficou.
- Ninguém tem mais de uma linha alocada em nenhum ciclo.
- Alocados em 2ª opção: 64 no ciclo 1, 134 no ciclo 2 e 76 no ciclo 3. Todos contam na célula da 2ª opção, como no
  pipeline.

### 9. Ciclo 3 *sub judice*

**Veredito: o resultado está completo.**

- **UFs:** as 26 UFs do quadro aparecem no resultado. O Acre não tem célula no quadro do ciclo 3.
- **Cursos:** os 24 cursos aparecem.
- **Situações:** 3.826 CADASTRO RESERVA, 704 ALOCADO e 2 SUB JUDICE.
- **Efeito no salto:** contar os 2 SUB JUDICE muda o salto em 0,300 de −8,4 para −8,5 p.p.

### 10. Outros achados

**a. O erro do ciclo 2 também atinge o E9 (fora da H1).** No conjunto de escolha do E9, ciclo 2, `tem_vaga_imediata`
e `log_vagas_imediatas_mais_1` vêm da versão de 19/03: 100% de concordância com ela e 80,5% com a de 13/02. O
conjunto de sensibilidade "só células com vaga imediata" também vem dela.

São atributos formados em parte pelas próprias escolhas. Isso é relevante porque o ciclo 2 é "o único sinal robusto"
do E9 (doc 44). Não reestimei o E9.

**b. Ciclo 1: confirmados e homologados.**
- 189 dos 468 confirmados não foram homologados.
- 16 homologados estão em célula diferente da confirmada e da realocada.
- Na alocação há 59 "desconsiderados a pedido da gestão local ou por capacidade", e 22 deles estavam em células só
  de CR.

Nada disso entra no A3 nem no N1. Só o F1.3 e o N2 usam a homologação.

**c. Frase do doc 41a.** A frase "as três versões do quadro da 1ª chamada têm as mesmas células" não é exata. O
original de 03/02 tem 1.550 células, e os retificados têm 1.547. O próprio dicionário de outcomes registra isso.

**d. Remanejamento como regra de alocação.** Pelo item 5.7, a vaga de reserva é preenchida com prioridade para
"regiões de saúde com maior dificuldade de acesso" e "escassez". Se essa priorização acompanha o IVS, ela é mais uma
regra administrativa no mesmo corte. Neste caso a regra não muda a faixa da bolsa: ela atua sobre que célula de
reserva recebe a vaga. O efeito dela não se separa do incentivo com os dados públicos.

## 4. Tabela de divergências (pipeline × reconstrução)

Os campos comparados por célula foram:
- presença;
- código IBGE, faixa e IVS;
- vagas imediatas e de CR (na versão do pipeline);
- candidatos de 1ª opção e alocados;
- preenchida (A3) e preenchida (F1.3);
- tipo de vaga.

Por município, foram comparados: número de células, vagas, alocados, células preenchidas, candidatos, faixa e IVS.

| Nível | Ciclo | Município | Campo | Auditoria | Pipeline | Motivo |
|---|---|---|---|---|---|---|
| município | 1 | 220770 Parnaíba (PI) | células preenchidas | 7 | 8 | o pipeline (N2/F1.3) conta homologação sem confirmação |
| município | 1 | 241220 São José de Mipibu (RN) | células preenchidas | 5 | 6 | idem |
| município | 1 | 290070 Alagoinhas (BA) | células preenchidas | 1 | 2 | idem |
| município | 1 | 313520 Januária (MG) | células preenchidas | 2 | 3 | idem |
| município | 1 | 316860 Teófilo Otoni (MG) | células preenchidas | 5 | 6 | idem |
| município | 1 | 350210 Andradina (SP) | células preenchidas | 1 | 2 | idem |

Em todos os outros campos e linhas não há divergência (`a36_divergencias_pipeline.csv`). Na célula, o
`f1_3_preenchida_ch1` do pipeline bate com a minha definição de confirmação ou homologação. O indicador ≥ 1 alocado
do A3 bate com o meu `preenchida`.

## 5. Saltos refeitos

Local linear, kernel triangular, h = 0,050, uma reta de cada lado por ciclo e salto comum. EP CR1 por município, IC
normal de 95%. A3 e taxa estão em p.p., e N1 em vagas por município. A fonte é `a36_estimativas.csv`.

### 5.1 Corte 0,300

| Especificação | Ciclos 1–3 | Ciclo 1 | Ciclo 2 | Ciclo 3 |
|---|---|---|---|---|
| A3 como no pipeline (FE curso×ciclo + tipo de vaga; c2 = 19/03) | −8,4 [−18,5; +1,7] p=0,104 | +0,9 [−23,5; +25,3] p=0,942 | −10,2 [−23,4; +2,9] p=0,128 | −7,1 [−18,6; +4,3] p=0,223 |
| A3, tipo de vaga pré-alocação (c2 = 13/02) | −10,1 [−22,4; +2,1] p=0,105 | +0,9 [−23,5; +25,3] p=0,942 | −25,6 [−43,3; −7,8] p=0,005 | −7,1 [−18,6; +4,3] p=0,223 |
| A3, só FE curso×ciclo | −11,4 [−23,9; +1,2] p=0,076 | +1,1 [−23,3; +25,4] p=0,931 | −26,8 [−44,3; −9,2] p=0,003 | −6,9 [−23,7; +9,8] p=0,418 |
| A3, definição do F1.3 no c1 (confirmado ou homologado) | −7,9 [−17,9; +2,0] p=0,119 | +3,1 [−21,0; +27,2] p=0,802 | −10,2 [−23,4; +2,9] p=0,128 | −7,1 [−18,6; +4,3] p=0,223 |
| A3, c1 = classificado (confirmado + desconsiderado) | −7,8 [−17,9; +2,3] p=0,129 | +2,8 [−20,2; +25,8] p=0,812 | −10,2 [−23,4; +2,9] p=0,128 | −7,1 [−18,6; +4,3] p=0,223 |
| A3, c1 com realocados do Quadro 2 | −8,1 [−18,2; +1,9] p=0,112 | +2,3 [−22,6; +27,2] p=0,856 | −10,2 [−23,4; +2,9] p=0,128 | −7,1 [−18,6; +4,3] p=0,223 |
| A3, c3 com SUB JUDICE | −8,5 [−18,6; +1,7] p=0,101 | +0,9 [−23,5; +25,3] p=0,942 | −10,2 [−23,4; +2,9] p=0,128 | −7,3 [−18,7; +4,2] p=0,214 |
| A3, só células com vaga imediata pré-alocação | −3,7 [−21,3; +13,9] p=0,682 | +0,8 [−38,1; +39,7] p=0,969 | −21,0 [−44,4; +2,4] p=0,078 | +7,2 [−17,3; +31,6] p=0,564 |
| A3, só células com vaga imediata (versão do pipeline) | −3,4 [−20,3; +13,6] p=0,698 | +0,8 [−38,1; +39,7] p=0,969 | −12,7 [−33,8; +8,4] p=0,237 | +7,2 [−17,3; +31,6] p=0,564 |
| A3, FE do pipeline + dummy de capital | −2,6 [−11,8; +6,6] p=0,579 | +1,2 [−23,0; +25,5] p=0,921 | −0,5 [−12,5; +11,5] p=0,933 | −0,5 [−11,8; +10,8] p=0,927 |
| A3, sem capitais | −1,7 [−11,9; +8,5] p=0,741 | +2,5 [−22,8; +27,8] p=0,847 | −4,0 [−18,4; +10,5] p=0,592 | +6,8 [−3,2; +16,8] p=0,183 |
| Taxa por vaga (Q2/S-e) como no pipeline | −16,0 [−27,9; −4,1] p=0,008 | −12,5 [−34,4; +9,4] p=0,263 | −27,8 [−49,0; −6,7] p=0,010 | −10,7 [−24,1; +2,6] p=0,115 |
| Taxa, c1 = classificado | −15,6 [−27,7; −3,4] p=0,012 | −9,7 [−31,6; +12,3] p=0,388 | −27,8 [−49,0; −6,7] p=0,010 | −10,7 [−24,1; +2,6] p=0,115 |
| Taxa, só células com imediata pré-alocação | −13,2 [−29,0; +2,7] p=0,104 | −12,2 [−50,2; +25,8] p=0,531 | −21,9 [−62,7; +18,9] p=0,293 | −8,9 [−29,7; +11,9] p=0,403 |
| Taxa, com dummy de capital | −10,9 [−22,6; +0,8] p=0,067 | −12,6 [−34,8; +9,6] p=0,265 | −23,4 [−45,8; −0,9] p=0,041 | −2,6 [−15,1; +9,9] p=0,682 |
| Taxa, sem capitais | −9,7 [−21,8; +2,4] p=0,116 | −12,3 [−35,6; +11,0] p=0,301 | −24,3 [−49,2; +0,6] p=0,055 | +1,6 [−7,9; +11,1] p=0,740 |
| N1 com controle (Q1/S-a) como no pipeline | −1,45 [−2,67; −0,22] p=0,021 | −0,67 [−2,07; +0,72] p=0,346 | −2,09 [−3,93; −0,24] p=0,027 | −1,33 [−3,14; +0,48] p=0,151 |
| N1, c1 = classificado | −1,40 [−2,65; −0,16] p=0,027 | −0,46 [−1,84; +0,92] p=0,512 | −2,09 [−3,93; −0,24] p=0,027 | −1,33 [−3,14; +0,48] p=0,151 |
| N1, controle = só imediatas pré-alocação | −0,84 [−2,15; +0,47] p=0,208 | +0,02 [−1,47; +1,51] p=0,983 | −1,03 [−3,76; +1,69] p=0,457 | −1,12 [−2,37; +0,13] p=0,080 |
| N1, com dummy de capital | −0,92 [−1,98; +0,14] p=0,088 | −0,64 [−2,08; +0,81] p=0,386 | −1,61 [−3,30; +0,09] p=0,063 | −0,15 [−1,62; +1,33] p=0,845 |
| N1, sem capitais | −0,50 [−1,39; +0,38] p=0,264 | −0,62 [−2,14; +0,90] p=0,424 | −1,42 [−3,07; +0,24] p=0,094 | +0,28 [−0,51; +1,08] p=0,482 |

### 5.2 Corte 0,400

| Especificação | Ciclos 1–3 | Ciclo 1 | Ciclo 2 | Ciclo 3 |
|---|---|---|---|---|
| A3 como no pipeline (FE curso×ciclo + tipo de vaga; c2 = 19/03) | −1,3 [−14,0; +11,3] p=0,838 | −12,4 [−37,5; +12,6] p=0,330 | +2,2 [−24,7; +29,2] p=0,870 | −4,3 [−12,8; +4,2] p=0,317 |
| A3, tipo de vaga pré-alocação (c2 = 13/02) | −4,1 [−17,8; +9,6] p=0,556 | −12,4 [−37,5; +12,6] p=0,330 | +0,3 [−27,6; +28,1] p=0,984 | −4,3 [−12,8; +4,2] p=0,317 |
| A3, só FE curso×ciclo | −4,7 [−17,7; +8,4] p=0,482 | −10,3 [−36,0; +15,4] p=0,431 | +1,1 [−26,0; +28,1] p=0,937 | −5,5 [−22,7; +11,8] p=0,534 |
| A3, definição do F1.3 no c1 | −1,3 [−14,0; +11,4] p=0,841 | −12,6 [−37,6; +12,5] p=0,324 | +2,2 [−24,7; +29,2] p=0,870 | −4,3 [−12,8; +4,2] p=0,317 |
| A3, c1 = classificado | −1,0 [−13,9; +11,8] p=0,874 | −10,7 [−36,0; +14,7] p=0,410 | +2,2 [−24,7; +29,2] p=0,870 | −4,3 [−12,8; +4,2] p=0,317 |
| A3, só células com vaga imediata pré-alocação | −2,3 [−24,0; +19,4] p=0,835 | −22,4 [−65,4; +20,6] p=0,307 | +15,2 [−14,7; +45,1] p=0,319 | −24,5 [−56,4; +7,4] p=0,132 |
| A3, FE do pipeline + dummy de capital | +1,6 [−11,7; +15,0] p=0,810 | −12,0 [−37,3; +13,3] p=0,351 | +14,3 [−11,6; +40,1] p=0,278 | −3,9 [−13,3; +5,5] p=0,417 |
| Taxa por vaga como no pipeline | +2,5 [−9,9; +15,0] p=0,689 | +3,6 [−22,9; +30,1] p=0,789 | +9,5 [−15,8; +34,8] p=0,462 | −1,9 [−15,6; +11,8] p=0,784 |
| Taxa, só células com imediata pré-alocação | −4,1 [−26,3; +18,1] p=0,718 | +2,1 [−36,3; +40,5] p=0,915 | +8,4 [−22,6; +39,4] p=0,596 | −23,4 [−56,8; +9,9] p=0,169 |
| Taxa, com dummy de capital | +1,9 [−11,6; +15,4] p=0,783 | +2,0 [−25,2; +29,2] p=0,884 | +2,1 [−27,0; +31,1] p=0,889 | +1,1 [−13,1; +15,3] p=0,879 |
| N1 com controle como no pipeline | −0,14 [−0,82; +0,54] p=0,682 | −0,09 [−1,11; +0,92] p=0,855 | −0,29 [−2,00; +1,43] p=0,744 | −0,09 [−0,80; +0,62] p=0,798 |
| N1, com dummy de capital | −0,11 [−0,79; +0,58] p=0,761 | −0,13 [−1,16; +0,90] p=0,805 | −0,26 [−1,99; +1,48] p=0,773 | +0,01 [−0,70; +0,72] p=0,979 |

### 5.3 Médias cruas nas janelas (sem reta)

Cada célula traz a média abaixo → acima, a diferença (acima − abaixo) e o IC 95% CR1. A3 e taxa estão em %, e N1 em
vagas por município. O "n" é o número de municípios abaixo/acima no empilhado.

| Corte | Janela | Medida | n | Ciclos 1–3 | Ciclo 1 | Ciclo 2 | Ciclo 3 |
|---|---|---|---|---|---|---|---|
| 0,300 | ±0,010 | A3 cru | 27/23 | 45,4 → 31,1; −14,3 [−28,8; +0,2] | 57,7 → 37,1; −20,5 [−58,8; +17,7] | 64,3 → 34,1; −30,2 [−52,6; −7,8] | 31,7 → 24,5; −7,2 [−24,9; +10,6] |
| 0,300 | ±0,010 | A3, só imediata pré | 12/13 | 74,3 → 57,5; −16,8 [−31,6; −2,0] | 78,6 → 55,6; −23,0 [−69,8; +23,7] | 90,9 → 58,3; −32,6 [−64,6; −0,5] | 63,2 → 57,9; −5,3 [−22,8; +12,3] |
| 0,300 | ±0,010 | A3, sem capitais | 23/23 | 43,0 → 31,1; −12,0 [−34,6; +10,7] | 54,2 → 37,1; −17,0 [−58,0; +24,0] | 80,8 → 34,1; −46,7 [−67,3; −26,1] | 8,3 → 24,5; +16,2 [+0,1; +32,3] |
| 0,300 | ±0,010 | Taxa por vaga | 27/23 | 34,4 → 22,4; −12,0 [−28,4; +4,3] | 55,6 → 28,0; −27,6 [−68,2; +13,1] | 56,8 → 30,1; −26,7 [−48,9; −4,5] | 22,5 → 14,8; −7,7 [−22,2; +6,8] |
| 0,300 | ±0,010 | N1 | 27/23 | 2,93 → 1,68; −1,25 [−3,64; +1,14] | 2,14 → 2,00; −0,14 [−3,03; +2,74] | 4,15 → 1,92; −2,23 [−6,13; +1,67] | 2,43 → 1,29; −1,14 [−3,82; +1,54] |
| 0,300 | ±0,020 | A3 cru | 54/47 | 38,3 → 31,8; −6,5 [−17,2; +4,1] | 30,4 → 28,1; −2,3 [−18,2; +13,5] | 56,6 → 48,6; −7,9 [−22,4; +6,6] | 29,0 → 23,5; −5,5 [−22,8; +11,9] |
| 0,300 | ±0,020 | A3, só imediata pré | 31/29 | 61,6 → 60,5; −1,0 [−19,7; +17,7] | 45,5 → 40,0; −5,5 [−32,5; +21,6] | 68,2 → 55,2; −13,1 [−36,9; +10,8] | 65,2 → 74,5; +9,4 [−12,6; +31,4] |
| 0,300 | ±0,020 | A3, sem capitais | 46/45 | 31,9 → 27,8; −4,1 [−15,3; +7,0] | 27,1 → 27,5; +0,4 [−16,1; +16,9] | 56,5 → 44,4; −12,1 [−28,9; +4,7] | 10,0 → 16,3; +6,3 [−4,8; +17,4] |
| 0,300 | ±0,020 | Taxa por vaga | 54/47 | 28,9 → 21,5; −7,4 [−17,1; +2,3] | 26,6 → 21,4; −5,2 [−19,1; +8,8] | 45,4 → 35,0; −10,5 [−24,6; +3,7] | 19,6 → 14,6; −5,1 [−18,5; +8,4] |
| 0,300 | ±0,020 | N1 | 54/47 | 3,28 → 2,44; −0,84 [−2,95; +1,28] | 2,10 → 1,42; −0,68 [−2,19; +0,83] | 4,97 → 3,19; −1,78 [−4,98; +1,41] | 2,60 → 2,41; −0,19 [−3,39; +3,00] |
| 0,300 | ±0,050 | A3 cru | 145/120 | 33,3 → 33,5; +0,2 [−6,1; +6,4] | 26,0 → 35,3; +9,3 [−1,0; +19,6] | 48,7 → 54,4; +5,7 [−5,0; +16,4] | 25,7 → 20,7; −5,0 [−14,4; +4,4] |
| 0,300 | ±0,050 | A3, só imediata pré | 95/72 | 56,1 → 60,5; +4,4 [−6,5; +15,2] | 43,0 → 45,7; +2,7 [−15,5; +20,9] | 64,4 → 67,6; +3,3 [−11,4; +18,0] | 56,3 → 64,1; +7,8 [−8,4; +23,9] |
| 0,300 | ±0,050 | A3, sem capitais | 132/114 | 28,3 → 32,4; +4,1 [−2,9; +11,0] | 23,4 → 37,7; +14,3 [+3,4; +25,3] | 45,1 → 50,0; +4,9 [−8,4; +18,3] | 16,3 → 17,9; +1,5 [−6,2; +9,2] |
| 0,300 | ±0,050 | Taxa por vaga | 145/120 | 23,0 → 23,8; +0,7 [−5,1; +6,5] | 21,5 → 29,5; +8,0 [−2,6; +18,5] | 34,2 → 42,5; +8,3 [−4,2; +20,7] | 15,9 → 12,8; −3,0 [−10,4; +4,4] |
| 0,300 | ±0,050 | N1 | 145/120 | 2,32 → 2,33; +0,01 [−1,11; +1,13] | 1,61 → 1,68; +0,07 [−0,79; +0,93] | 3,45 → 3,75; +0,30 [−1,90; +2,51] | 1,84 → 1,70; −0,15 [−1,52; +1,22] |
| 0,400 | ±0,010 | A3 cru | 29/28 | 39,2 → 37,7; −1,5 [−15,6; +12,6] | 32,7 → 37,9; +5,2 [−19,8; +30,2] | 60,8 → 67,6; +6,8 [−16,1; +29,7] | 21,8 → 17,9; −3,9 [−19,1; +11,2] |
| 0,400 | ±0,010 | Taxa por vaga | 29/28 | 31,5 → 30,7; −0,8 [−13,5; +12,0] | 27,9 → 36,4; +8,4 [−16,5; +33,3] | 50,0 → 63,8; +13,8 [−9,3; +36,9] | 12,8 → 13,7; +0,9 [−10,4; +12,3] |
| 0,400 | ±0,020 | A3 cru | 52/53 | 39,9 → 41,1; +1,2 [−8,5; +10,9] | 37,6 → 34,1; −3,5 [−23,1; +16,1] | 60,2 → 73,8; +13,6 [−1,8; +29,0] | 26,3 → 23,2; −3,1 [−15,4; +9,2] |
| 0,400 | ±0,020 | Taxa por vaga | 52/53 | 31,2 → 33,0; +1,7 [−7,7; +11,1] | 30,4 → 31,2; +0,8 [−18,7; +20,4] | 49,4 → 65,6; +16,2 [+0,7; +31,7] | 17,2 → 18,7; +1,5 [−9,3; +12,4] |
| 0,400 | ±0,050 | A3 cru | 122/145 | 36,8 → 38,6; +1,9 [−5,4; +9,1] | 37,2 → 35,3; −2,0 [−14,4; +10,4] | 57,3 → 70,6; +13,3 [+2,1; +24,6] | 22,4 → 23,0; +0,6 [−8,0; +9,2] |
| 0,400 | ±0,050 | Taxa por vaga | 122/145 | 27,7 → 31,3; +3,6 [−3,7; +10,9] | 32,4 → 32,9; +0,5 [−13,1; +14,1] | 45,8 → 63,9; +18,1 [+4,2; +32,0] | 14,3 → 17,4; +3,1 [−3,7; +9,9] |

**Local constante, kernel triangular h = 0,050, efeitos fixos do pipeline (A3):**

| Corte | Ciclos 1–3 | Ciclo 1 | Ciclo 2 | Ciclo 3 |
|---|---|---|---|---|
| 0,300 | +0,7 [−5,3; +6,6] | +7,2 [−3,9; +18,3] | +2,3 [−6,0; +10,7] | −3,6 [−10,3; +3,2] |
| 0,400 | +1,8 [−5,4; +8,9] | −7,5 [−20,5; +5,5] | +1,5 [−14,3; +17,3] | +3,3 [−2,4; +8,9] |

### 5.4 Composição no corte (sem efeitos fixos)

| Corte | Medida | Ciclos 1–3 | Ciclo 1 | Ciclo 2 | Ciclo 3 |
|---|---|---|---|---|---|
| 0,300 | célula só de CR, versão pré-alocação (c2 = 13/02) | +14,0 [−0,2; +28,3] | +17,9 [−7,7; +43,4] | +24,1 [−4,7; +52,8] | +5,6 [−16,0; +27,2] |
| 0,300 | célula só de CR, versão do pipeline (c2 = 19/03) | +15,4 [+2,1; +28,6] | +17,9 [−7,7; +43,4] | +28,4 [+8,3; +48,4] | +5,6 [−16,0; +27,2] |
| 0,300 | célula em capital | −50,3 [−82,4; −18,2] | −2,9 [−22,9; +17,1] | −58,2 [−97,3; −19,2] | −67,8 [−105,9; −29,7] |
| 0,300 | município × ciclo é capital | −17,8 [−34,1; −1,5] | −18,5 [−42,3; +5,2] | −22,4 [−41,9; −2,8] | −13,9 [−28,0; +0,2] |
| 0,400 | célula só de CR, versão pré-alocação | +7,2 [−12,8; +27,2] | +32,8 [+14,3; +51,3] | −12,9 [−59,7; +34,0] | +6,0 [−12,0; +23,9] |
| 0,400 | célula só de CR, versão do pipeline | +11,3 [−1,5; +24,1] | +32,8 [+14,3; +51,3] | +0,3 [−21,2; +21,9] | +6,0 [−12,0; +23,9] |
| 0,400 | célula em capital | −32,0 [−69,9; +5,8] | −7,9 [−19,4; +3,5] | −52,1 [−112,3; +8,0] | −32,3 [−70,5; +5,9] |
| 0,400 | município × ciclo é capital | −5,9 [−15,1; +3,3] | −6,8 [−18,0; +4,5] | −8,7 [−22,0; +4,5] | −4,1 [−10,6; +2,4] |

A célula em capital é um indicador binário estimado por reta local. Quando a reta é levada até o corte, a
estimativa pode passar de ±100 p.p., como no ciclo 3 em 0,300. Por isso o sinal e o tamanho relativo informam mais
que o número exato.

## 6. Leitura e recomendações

**O que a auditoria sustenta:**

- **Não houve erro de dados.** Os brutos, lidos de forma independente, geram as mesmas bases e os mesmos números do
  pipeline.
- **Houve um erro de entendimento.** O "tipo de vaga" do ciclo 2 é pós-alocação: ele vem do quadro de 19/03, que
  converteu reserva em imediata depois das escolhas. A correção não muda o sinal da H1 em 0,300. No ciclo 2 a queda
  do A3 até aumenta.
- **A queda em 0,300 é frágil.** Ela aparece só com a reta levada até o corte: as médias da janela de 0,050 são
  iguais, e o local constante dá +0,7 p.p. Ela se concentra nas células só de reserva, cujo preenchimento depende do
  remanejamento administrativo. E ela coincide com um desequilíbrio pré-determinado: abaixo do corte há mais
  capitais, que preenchem mais. Com uma dummy de capital, A3, taxa e N1 em 0,300 passam a ter IC com zero. O ciclo 2
  na taxa é a exceção.
- **Estatuto destas variantes.** Elas são pós-resultado. Não substituem a especificação congelada do protocolo 48 e
  não autorizam dizer que "não há queda". Autorizam dizer que a queda não é robusta à composição de capitais e de
  vagas só de reserva.

**O que recomendo corrigir.** Toda mudança de especificação é decisão do autor.

1. **Docs 49 §2 e 57l.** Corrigir a frase de que, no ciclo 2, "vaga de reserva não podia ser preenchida na 1ª
   chamada". Ela foi preenchida, por conversão do quadro em 19/03. A frase "Para dizer na banca" do 57l repete isso.
   Esta auditoria não edita os docs 57*.
2. **Tipo de vaga do ciclo 2.** Onde ele entra como atributo ou controle (FE do A3, D-b, "Q2 sem só CR", sensibilidade
   "só imediatas" do N1, E9), usar a versão de 13/02 ou tirá-lo no ciclo 2. Relatar as duas formas.
3. **E9 do ciclo 2.** Reestimar com `tem_vaga_imediata` e as vagas imediatas de 13/02, e com o conjunto de
   sensibilidade refeito. É o "único sinal robusto" da rodada multi-outcome, e hoje ele usa um atributo formado em
   parte pelas escolhas.
4. **Capitais.** Incluir a condição de capital no balanço pré-determinado da H1 e do diagnóstico da queda em 0,300.
   Se o autor quiser, pré-registrar a dummy de capital como covariável CCFT numa rodada nova, declarada como
   pós-resultado.
5. **Doc 41a.** Corrigir a frase de que "as três versões têm as mesmas células" (1.550 contra 1.547).

## 7. Reprodução

```bash
python scripts/auditoria_H1/a36_reconstruir_H1.py
```

O script é determinístico, sem sorteio. Ele grava:

| Arquivo | Conteúdo |
|---|---|
| `a36_celulas.csv` | base por célula |
| `a36_municipios.csv` | base por município × ciclo |
| `a36_divergencias_pipeline.csv` | divergências contra o pipeline |
| `a36_gravado_contra_refeito.csv` | linhas gravadas contra as refeitas |
| `a36_estimativas.csv` | todas as estimativas desta auditoria |
| `a36_vizinhos_0300_0400.csv` | municípios mais próximos dos cortes |
| `a36_resumo.json` | entradas, saídas com SHA-256, verificações por ciclo e chaves |

Tudo fica em `output/auditoria_H1/`. O script fica fora do `run_all.py`.
