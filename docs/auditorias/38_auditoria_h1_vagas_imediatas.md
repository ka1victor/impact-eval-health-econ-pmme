# Auditoria 38: adendo 48b (H1 só com vagas imediatas), execução e doc 57n

> **Data:** 26/10/2026.<br>
> **Objeto:**
> - adendo [`48b_adendo_H1_vagas_imediatas.md`](../06_execucao/48b_adendo_H1_vagas_imediatas.md), inclusive a §7;
> - script `scripts/rdd_bolsa/40_h1_vagas_imediatas.py`;
> - saídas `output/rdd_bolsa/HI_estimativas.csv`, `HI_resumo.json` e `HI_figuras/`;
> - doc [`57n_resultados_H1_vagas_imediatas.md`](../06_execucao/57n_resultados_H1_vagas_imediatas.md);
> - testes `tests/test_h1_vagas_imediatas.py`.
>
> **Referências:** `CLAUDE.md`; protocolo 48; docs 49 e 49b; protocolo 60 (margens do TOST);
> [auditoria 36](36_auditoria_dados_H1.md) e `scripts/auditoria_H1/`; `scripts/rdd_bolsa/rdd_lib.py` (lida, não
> importada).<br>
> **Método:** código próprio, que não importa o script 40, a `rdd_lib` nem scripts do pipeline:
> - `scripts/auditoria_H1/a38_recalculo.py` lê `outcomes_V_celula.parquet`, o IVS oficial (a08) e os dois quadros
>   brutos do ciclo 2 (13/02 e 19/03), com leitor próprio das planilhas;
> - o estimador é próprio: Frisch–Waugh–Lovell com kernel triangular e CR1 por município; IC honesto (regra de
>   bolso, classe de Taylor), TOST, Holm e BKY também foram reescritos;
> - `scripts/auditoria_H1/a38_comparar.py` compara linha a linha com `HI_estimativas.csv`.
>
> Os dois só leem e imprimem; nada foi gravado em `output/`.<br>
> **Estatuto:** auditoria pós-resultado. O contraste é o **pacote do corte**
> ([auditoria 18](18_politicas_nos_mesmos_cortes_ivs.md)), não a participação no PMM-E nem o Agora Tem Especialistas.

## 1. Veredito

**Aprovado com correções.**

- **Números.** As 50 linhas de estimativa e as 8 de TOST refeitas (58 das 68 de `HI_estimativas.csv`) batem com o
  arquivo:
  - salto, EP, IC e p, com diferença máxima de 1,2e−12;
  - contagens idênticas;
  - Holm e BKY idênticos;
  - leituras do TOST idênticas;
  - não refeitas: o IC honesto com M ×0,5 e ×2, que é o de M ×1 com M escalado, e a forma literal da HI-s2, que é
    idêntica à HI-1 célula a célula.
- **Ciclo 2.** O tipo de vaga sai do quadro de 13/02/2026, como manda a §7, e as contagens conferem.
- **Integridade e determinismo.** Estão ok.
- **Correções.** São só de texto no 57n (achados 1, 2 e 4). Foram feitas no gerador do doc (`gerar_doc` do script
  40), e o doc foi regerado. **Nenhum número mudou**: CSV, JSON e figuras saíram idênticos byte a byte.

## 2. Achados, por gravidade

Nenhum achado grave: não há erro de dado, de estimador ou de amostra.

### Moderados

1. **A justificativa "pela regra de uso da reserva" não sobrevive à auditoria 36 (corrigido no 57n).**
   - O §1 do adendo justifica olhar só vagas imediatas com a frase "no ciclo 2, nenhuma célula só de reserva teve
     alocado na 1ª chamada". A §7 já diz que essa frase descreve o quadro pós-resultado.
   - O 57n (§6, "Pós-resultado") ainda chamava o adendo de "correção de definição justificada pela regra de uso da
     reserva".
   - Pela auditoria 36 (seção 3, item 2), os editais **permitem** preencher a reserva na 1ª chamada, e pôr essas
     células no denominador "não é erro de regra". O que resta como justificativa é o mecanismo diferente:
     remanejamento e priorização da SGTES.
   - **Correção:** o item "Pós-resultado" do §6 passou a dizer isso. A nota "Regra da reserva nos editais" já estava
     certa.

2. **Exposição prévia ao resultado (declarada no 57n; agora também no cabeçalho).**
   - A §7 do adendo diz que a mudança vale "antes de qualquer resultado dele ter sido visto". Isso é verdade para quem
     escreveu a nota, não para quem executou o script.
   - O `HI_resumo.json` (`exposicao_previa_deste_script`) e o 57n (§6, "Tipo de vaga do ciclo 2") registram que o
     script rodou uma vez com o quadro de 19/03 antes da nota, e que o executor viu HI-1 e HI-2 dessa versão.
   - **No Git não há rastro dessa rodada.** Há um único commit de execução (`232e81a`, 15:44), feito 9 minutos depois
     do commit da §7 (`4326241`, 15:35:26) e depois da auditoria 36 (`1756209`). A rodada com 19/03 só existe como
     declaração.
   - **A direção da troca não favorece uma leitura nula.** Com 19/03, as quatro primárias têm IC que contém zero (a
     HI-2 em 0,300 fica em −1,00 [−2,16; +0,16]). Com 13/02, a HI-2 em 0,300 passa a excluir zero no IC
     convencional (−1,13 [−2,15; −0,10]).
   - **Correção:** a declaração estava só no §6. Foi acrescentada uma frase ao bloco "Estatuto" do cabeçalho do 57n.

3. **A leitura pré-registrada (§4) não cobre o resultado obtido (sem correção; transparente).**
   - O §4 tem dois casos: (a) as quatro primárias com IC que contém zero; (b) alguma rejeita zero depois do Holm.
   - O resultado fica entre os dois: a HI-2 em 0,300 tem p = 0,032 e p de Holm = 0,126.
   - O script cria um terceiro código, `IC_CONVENCIONAL_EXCLUI_ZERO_SEM_HOLM`, com o texto de leitura escrito no
     código, e não no adendo. O 57n diz isso com clareza ("fica entre os dois"; "não é a frase 'não se detecta
     diferença' … nem um efeito confirmado").
   - Do mesmo modo, a regra que decide se a HI-s6 mostra a diferença "concentrada nas células só de reserva" (IC da
     HI-s6 sem zero, salto negativo, e HI-1 com IC que contém zero) é uma operacionalização do código, não do adendo.
     O 57n a chama de "regra fixa no código".
   - **Recomendação:** na banca, apresentar essas duas leituras como decisões de implementação, não como leitura
     pré-registrada.

4. **A seleção da amostra pelo tipo de vaga não estava dita no 57n (corrigido).**
   - O §6 discutia só o *controle* de HI-2, que pode ter respondido ao corte. A *amostra* (células com vaga imediata)
     depende da mesma decisão da SGTES.
   - **Correção:** acrescentada uma frase que remete ao adendo 48f, congelado depois destas contas, que mede essa
     seleção.

### Menores

5. **Itens de edital do ciclo 3.**
   - O texto da nota sobre a reserva cita "itens 4.1.3.3, 4.1.3.4 e 5.7" para os ciclos 1 e 3, e a tabela do 57n
     mostra o 4.1.3.3 só do ciclo 1. É a tabela arquivada em `N_resumo.json`.
   - A auditoria 36 afirma que o ciclo 3 tem os três itens com o mesmo teor; não há erro de conteúdo.
   - Não corrigido: o texto está em `HI_resumo.json`. Fica como sugestão para a próxima rodada.

6. **A HI-s6, descritiva, entra na família BKY (34 linhas).**
   - O adendo pede "BKY entre as secundárias", e a HI-s6 é uma delas. Está conforme.
   - Os q-valores ficam todos em 0,819 ou 1,000, e a inclusão não muda nenhuma leitura.

7. **A legenda de `HI_antiga_vs_imediatas.png` simplifica.**
   - A legenda diz que a figura "mostra quanto do sinal antigo vinha de comparar vagas de tipos diferentes".
   - Mas a medida antiga (A3) usa o efeito fixo de tipo pelo quadro de 19/03, e a HI-1 usa o tipo de 13/02: a
     diferença mistura a restrição da amostra com a troca de quadro.
   - Na contagem por município, o sinal antigo persiste em boa parte: N1 S-a −1,45; HI-2 −1,13.
   - Não corrigido: exigiria regerar a figura. Sugestão de redação: "mostra como o salto muda ao comparar só vagas
     imediatas".

8. **Interpretação da HI-s2 (registrada e razoável).**
   - Na base, a definição do A3 já é "≥ 1 alocado" nos três ciclos. Por isso a forma literal da HI-s2 repete HI-1, e
     o script relata, além dela, a F1.3.
   - A decisão está em `HI_resumo.json` (`decisoes.definicao_preenchida`) e no 57n. Conferi célula a célula que a
     forma literal é idêntica a HI-1.

## 3. Fidelidade ao adendo

| Item do adendo | Conferência | Situação |
|---|---|---|
| Amostra: células com ≥ 1 vaga imediata; as só de reserva ficam fora e são contadas | Recontado: ciclo 1 com 513 dentro e 782 fora; ciclo 2 (13/02) com 714 e 833; ciclo 3 com 694 e 1.598, mais 1 célula sem IVS oficial, fora e contada. Municípios na HI-2: 215 / 328 / 307 | conforme |
| "Preenchida" por ciclo = A3 | `n_alocados_ch1 >= 1`; a fonte do "alocado" muda por ciclo (achado 8) | conforme |
| HI-1: efeitos fixos de curso × ciclo | Refeito com EF próprios: dummies de nível ausente ou colinear não mudam o salto | conforme |
| HI-2: controle = vagas imediatas, coeficiente por ciclo | Refeito com uma coluna por ciclo, sem centrar (o centro não muda o salto nem o EP) | conforme |
| Estimação e inferência | h = 0,050, kernel triangular, cortes separados, ciclos empilhados com intercepto e inclinações por ciclo × lado e salto comum, CR1 por município | conforme |
| Holm entre as 4 primárias | p de Holm refeitos: 1,000; 0,126; 1,000; 1,000 | conforme |
| BKY nas HI-s1 a HI-s8 | 34 linhas: HI-s1 (12), HI-s2 F1.3 (2), HI-s3 (2), HI-s4 (4), HI-s5 (2), HI-s6 (4), h da HI-s8 (8). Ficam fora: a forma literal da HI-s2, o IC honesto, o TOST e a SENS-19MAR. q refeitos com dif. 0 | conforme |
| Leitura do §4 | Ver achado 3 | caso não previsto, tratado com transparência |
| TOST (HI-s7) com as margens do protocolo 60 | ±10 p.p.; ±25% da média abaixo do corte na mesma amostra | conforme |
| IC honesto (HI-s8) como no protocolo 48 | Regra do E6, com suporte até 0,350 | conforme |

## 4. Ciclo 2: tipo de vaga pelo quadro de 13/02/2026

**Arquivos e hashes conferidos:**
- `data/raw/aquisicao/vagas/2026_ciclo2_chamada1_vagas_e_servicos_retificado.xlsx`, SHA-256
  `3393473c…697f8`, é o retificado de 13/02/2026 (A01, linha `vagas_2026_c2_ch1_retificado_servicos`);
- o de 19/03/2026 é `data/raw/pmm_e/2026_ciclo2_chamada1_vagas_retificadas.xlsx` (`a47b0b02…425b`);
- o pipeline usa o de 19/03: as vagas imediatas do ciclo 2 em `outcomes_V_celula.parquet` são iguais às desse
  quadro, célula a célula.

**Origem dos números.** Na amostra e no controle de HI-1 e HI-2, o tipo de vaga e as vagas imediatas do ciclo 2 vêm
do quadro de 13/02, e nos ciclos 1 e 3 vêm do pipeline. As duas coisas foram conferidas no código e no recálculo.

**Contagens refeitas com leitor próprio:**
- as 1.547 células são as mesmas nos dois quadros; só 2 têm total de vagas diferente;
- 1.206 imediatas e 1.686 de reserva em 13/02, contra 1.836 e 1.053 em 19/03;
- 630 vagas foram convertidas de reserva em imediatas;
- **das 833 células só de reserva em 13/02, 301 ganharam vaga imediata, e 297 delas tinham alocado**;
- 442 dos 1.057 alocados estavam em células só de reserva pelo quadro de 13/02; pelo de 19/03, nenhum.

Tudo igual ao 57n e à auditoria 36.

**Git.** A §7 só acrescentou texto ao adendo: o diff `666aee1..4326241` não remove nenhuma linha. Os hashes batem com
os do script: o original é `383768d2…`, e o atual, com a §7, é `0dc4a673…`. A rodada com 19/03 está tratada no
achado 2.

## 5. Recálculo independente e diferenças

| Bloco | Linhas | Máx. diferença |
|---|---|---|
| HI-1 e HI-2 principais, nos dois cortes | 4 | salto 3,4e−14; EP 5,6e−14; p 2,4e−13; contagens iguais |
| HI-s1 (por ciclo) | 12 | 1,6e−13 (p) |
| HI-s2 (F1.3), HI-s3 (sem controle), HI-s4 (puras), HI-s5 (F1.4), HI-s6 (só reserva) | 14 | 7,0e−13 (p) |
| HI-s8: h = 0,030 e 0,080 | 8 | 1,2e−12 (p) |
| HI-s8: IC honesto M ×1 (HI-1 e HI-2, nos dois cortes) | 4 | M relativo 2,9e−15; viés máx. 2,0e−13; limites do IC 2,4e−13 |
| HI-s7: TOST convencional e honesto | 8 | 2,3e−13; as 8 leituras são iguais |
| SENS-19MAR (empilhada e ciclo 2) | 8 | 2,2e−13 |
| Holm (4) e BKY (34) | — | 6e−14 e 0 |

**Valores conferidos** (os do 57n):
- **HI-1:** −3,7 p.p. [−21,3; +13,9] em 0,300 e −2,3 p.p. [−24,0; +19,4] em 0,400;
- **HI-2:** −1,13 [−2,15; −0,10] em 0,300 (p = 0,032; p de Holm = 0,126) e −0,16 [−0,99; +0,68] em 0,400;
- **HI-s3 em 0,300:** −2,76 [−5,00; −0,51];
- **HI-s6 por célula em 0,300:** −9,9 p.p. [−20,7; +0,9];
- **TOST da HI-2 em 0,300, convencional:** descarta aumento ≥ 0,69, mas não queda;
- **IC honesto M ×1 da HI-2 em 0,300:** [−39,02; +36,76].

## 6. Integridade

- **Arquivo de IVS errado: não é lido.** Rodei o script com um *audit hook* do Python que registra cada arquivo
  aberto. Leituras em `data/`: só o quadro de 13/02. Em `output/`: a08, outcomes, `N_`/`NA_`/`ND_` (só leitura),
  dicionário. Fora isso: o adendo, a auditoria 36 e os scripts importados.
- **CNES: nenhum arquivo lido.** As colunas das bases de outcomes não têm competência; `co_cnes_7d` é só chave de
  estabelecimento. Não há competência ≥ 202609.
- **`EMPIRICO`:** nas 68 linhas do CSV e no JSON. O estatuto `ADENDO_48B_POS_RESULTADO` também está em todas.
- **Nada imputado:**
  - célula sem vaga ou com vaga ausente para o script;
  - `n_alocados_ch1` e F1.3 não têm ausência na amostra;
  - a F1.4 só é ausente no ciclo 3, que fica fora da HI-s5;
  - o município sem IVS oficial fica fora e é contado.
- **Saídas dos protocolos 48 e 61 intactas.** Depois de quatro rodadas do script, `git diff --quiet HEAD -- output/`
  não acusa diferença: os 35 arquivos `N_*`, `NA_*`, `ND_*`, `DQ_*` e `HI_*` versionados, figuras incluídas, têm
  conteúdo idêntico ao commit. No Git, nenhum `N_*`, `NA_*`, `ND_*` ou `DQ_*` mudou desde antes do `666aee1`, e o
  script só abre esses arquivos para leitura (*audit hook*).
- **Determinismo.** Quatro rodadas: uma com o *hook*, uma com `--atualizar-doc` antes das correções e duas depois.
  CSV, JSON e as 4 PNG saíram idênticos byte a byte ao commit nas quatro. O 57n saiu idêntico na rodada anterior às
  correções.
- **Testes.** `tests/test_h1_vagas_imediatas.py`: 23 passam, antes e depois das correções.

## 7. Texto do 57n

- **Linguagem causal.** Não há linguagem causal indevida:
  - "pacote do corte" em todo o texto;
  - "não se detecta" não vira "zero";
  - "efeito total" só como rótulo do adendo para a HI-s3;
  - a frase para a banca é descritiva ("do lado de bolsa maior há menos médicos alocados por município"), e o sinal
    não sobrevive ao Holm.
- **Números.** Nenhum número digitado: o doc é gerado inteiro pelo script, e o teste confere a igualdade. Fora dos
  blocos `HI:` só aparecem parâmetros fixos (h, margens, cortes, valores da bolsa), commits e hashes.
- **Estatuto pós-resultado.** Está claro no cabeçalho e no §6. A exposição à versão com 19/03 agora também está no
  cabeçalho (achado 2).
- **Regra da reserva nos editais.** A nota está certa à luz da auditoria 36: editais dos ciclos 1 e 3; ciclo 2 sem o
  texto do edital, com a reserva preenchida pela conversão de 19/03; mecanismo diferente. O que faltava foi
  corrigido (achado 1). O item 5.7 é a "priorização" citada.

## 8. O que foi alterado nesta auditoria

- `scripts/rdd_bolsa/40_h1_vagas_imediatas.py`: só texto em `gerar_doc`.
  - Cabeçalho "Estatuto": exposição à versão com 19/03.
  - §6, "Pós-resultado": justificativa à luz da auditoria 36.
  - §6, "Controle de HI-2": seleção da amostra pelo tipo de vaga e remissão ao 48f.
- `docs/06_execucao/57n_resultados_H1_vagas_imediatas.md`: regerado com `--atualizar-doc`; só esses três trechos
  mudam.
- Criados: este relatório e `scripts/auditoria_H1/a38_recalculo.py` e `a38_comparar.py`, que só leem.
- Nenhuma saída em `output/` mudou.

## 9. Reprodução

```
python3 scripts/auditoria_H1/a38_recalculo.py > /tmp/a38.json
python3 scripts/auditoria_H1/a38_comparar.py . /tmp/a38.json
python3 -m pytest -q tests/test_h1_vagas_imediatas.py
```
