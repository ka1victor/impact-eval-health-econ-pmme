# Auditoria independente do P3x (adendo §12 do protocolo 47): extensões da produção especializada

> **Data:** 23/10/2026.<br>
> **Objeto:** commit `b358283`: `scripts/rdd_bolsa/27_producao_extensoes.py`,
> `output/rdd_bolsa/K_X_*`, o
> [doc 57c](../06_execucao/57c_resultados_P3_extensoes.md) e
> `tests/test_producao_extensoes.py`, contra o adendo §12 (e os limites do §10)
> do [protocolo 47](../06_execucao/47_protocolo_producao_especializada.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.** As linhas principais foram
> reproduzidas com código próprio: o ponto bate até a última casa e o erro-padrão
> analítico fica a 0,96–1,01 do bootstrap do script. Nenhuma estimativa mudou. As
> correções são de relato:
> - uma leitura do 12.5 que concluía "atendimento de referência, não
>   deslocamento" com pré que rejeita;
> - o pré dos ATT que excluem zero, que não era destacado;
> - a convenção do doc 50 (θ médio do pré parecido ou oposto), que faltava;
> - eixos cortados sem aviso e dois limites não declarados.<br>
> **Proveniência dos números:** todo número citado aqui foi lido de
> `output/rdd_bolsa/K_X_estimativas.csv` e `K_X_resumo.json` depois da correção. A
> conferência independente que fica no repositório é a classe
> `TestRecalculoIndependenteAuditoria25` de `tests/test_producao_extensoes.py`.

## 1. Como a auditoria foi feita

O código de conferência foi escrito do zero (pandas e numpy). Ele não importa
funções dos scripts 21, 22 e 27. Só o teste de plausibilidade do DiD sintético
chama o `sdid` do script 27, porque os pesos só existem lá.

- **Leitura própria** de: IVS e população (universo U), amostra do D2, lista
  nominal (só `co_ibge`, `curso`, `dt_inicio_atividade`), SIH da safra v1 e v2,
  SIH por residência, SIA K1 (`alvo_pmme`, 4 tipos, com a regra do zero só quando
  nenhum subgrupo do tipo veio como coluna), SIA por forma × curso (a17) com as
  formas típicas do G4, tabela de regiões de saúde do TabNet, células dos cursos
  nos ciclos 1–2.
- **Estimador próprio:** Callaway–Sant'Anna com base g−1, controles ainda não
  tratados ou só nunca tratados, grupo (curso), θ(e) com peso pela fração de
  unidades de cada célula grupo × coorte, ATT do pós = média de θ(e), e ≥ 0. EP
  analítico com cluster no município, incluindo o termo dos pesos.
- **BKY** de Anderson (2008) próprio.

Não foram lidos: `data/ivs_ipea_2010_municipios.csv`, o CNES, o TISS nem colunas
de nome da lista nominal.

## 2. Recálculo

| Linha | Meu ATT | ATT do script | Diferença | EP meu (analítico) | EP do script (bootstrap) |
|---|---:|---:|---:|---:|---:|
| 12.2, todos os cursos | 14,339496 | 14,339496 | 0 | 5,49 | 5,74 |
| 12.2, curso 14 | 39,786318 | 39,786318 | 0 | 17,96 | 18,72 |
| 12.2, curso 15 | 5,084831 | 5,084831 | 0 | 2,14 | 2,18 |
| 12.4, K2r_tot (D2) | 2,119173 | 2,119173 | 0 | 0,91 | 0,93 |
| 12.5, K1_reg | 16,234283 | 16,234283 | 0 | 7,72 | 7,87 |
| 12.3a, só nunca tratados | 43,419474 | 43,419474 | 0 | 20,58 | 20,30 |
| 12.3, D2 do doc 50 (K1) | 32,969287 | 32,969287 | 0 | 18,52 | 18,77 |
| 12.1, K2 v1 | 0,722801 | 0,722801 | 0 | 0,88 | 0,89 |
| 12.1, K2 v2 | 0,713379 | 0,713379 | 0 | 0,88 | 0,89 |

Também conferido:
- os θ(e) de todos os meses do estudo de evento do 12.2 agregado (diferença
  máxima abaixo de 1e-8);
- as contagens do 12.2: 1.017 pares, 298 tratados até 2026-05 e 719 não tratados;
- as 20 chegadas depois de 2026-05 retiradas no 12.3a e os 283 nunca tratados;
- BKY das 8 linhas, diferença 0 contra `q_bky`;
- **DiD sintético (plausibilidade):** na coorte 202604, os pesos de unidade e de
  tempo somam 1 e não são negativos, e o ponto bate com a fórmula
  τ = (tratados pós − Σλ pré) − Σω (controles pós − Σλ pré). O ponto da coorte
  é +36,24, igual ao do CSV.

## 3. Protocolo

| Regra | Situação |
|---|---|
| SIA/SIH ≤ 202607 (principal ≤ 202605); CNES < 202609; TISS ≤ 202512 | ok. As séries terminam em 202605; 202607 só nas sensibilidades do D1. Nenhum CNES nem TISS é lido; a lista nominal falha se houver início ≥ 202609 |
| 12.2: cursos ESPECÍFICO do G4, formas típicas, D2 por par, cluster no município | ok. Peso "pelo número de pares" lido como peso pela fração de pares tratados de cada curso × coorte; está nos desvios |
| 12.3a: controles que ficaram vazios | ok no município (nunca tratados; as 20 chegadas tardias saem); o pareamento por curso é o 12.2 |
| 12.3c: heterogeneidade "já presente" só com condição pré-tratamento | ok com limite novo (C4): a ligação do médico ao CNES usa competências posteriores ao início |
| BKY do adendo | ok. 8 linhas; nenhuma com q < 0,05 (mínimo 0,101). 12.1 e 12.3a/b ficam fora e isso está declarado |
| 12.1: K1 reestimado só se o SIA v2 tiver revisão | `NAO_EXECUTADO` justificado: `a12b` compara 14.250.618 células de 202509 a 202607, nenhuma difere, nenhuma ausente e a soma das quantidades é igual nas duas safras |
| Desvios datados | ok: todas as linhas têm data. Duas entradas novas, também datadas |

Pontos que não saíram do adendo e foram aceitos:
- **K2r, K2r_tot e K2_reg** usam o mesmo painel de ausência do a13 e do a15: UF
  e mês sem arquivo ficam ausentes e propagam, nunca viram zero.
- **Zero em forma do a17 omitida:** só vale quando o TabNet não trouxe a coluna.
  A auditoria contou os cursos × meses em que nenhuma forma típica veio: zero de
  53 meses nos 8 cursos, então a regra de zero em bloco nunca é acionada no 12.2.

## 4. Integridade

| Item | Situação |
|---|---|
| `natureza_dos_dados = EMPIRICO` e `estatuto` do adendo | ok nas três tabelas, no resumo e em toda saída lida |
| Ausente não vira zero | ok. Não há `fillna(0)` em série: os `fillna` são de rótulo e da máscara booleana de atípico; o `nan_to_num` só entra no cálculo do IF, com as colunas sem estimativa devolvidas a NaN, e no total regional, onde o mês com qualquer outro município ausente volta a NaN |
| Arquivo de IVS errado | não lido (o teste do script e a auditoria conferiram; a running variable é o a08) |
| `data/` | intacto: o commit não toca `data/`; o script só lê a lista nominal, nas colunas `co_ibge`, `curso`, `dt_inicio_atividade`, `ciclo` e `dt_referencia` (nenhum nome) |
| Manifesto do A6 | regerado pelo gerador (`07_red_team_sintese.py`) nesta auditoria: saída idêntica à do commit, incluindo a linha do script 27 |

## 5. Achados e correções

### C1. Leitura do 12.5 concluía mais do que os dados sustentam (corrigido)

A leitura dizia que, com K1 sobre nos vizinhos, "o padrão é compatível com
atendimento de referência, não com deslocamento". O pré de K1_reg não é plano
(Wald p = 0,005), o K1 do município inclui zero e o desenho não separa expansão
líquida de deslocamento. Além disso, a seção 1 dizia que o 12.5 "separa" os dois.

Agora:
- a leitura diz que expansão líquida e deslocamento **não ficam separados** e
  trata a leitura do protocolo (negativo = deslocamento, positivo = referência)
  como hipótese;
- cita o pré não plano e que pacientes que migram não aparecem na produção por
  município de execução;
- a seção 1, o "Como ler" da figura 12.5 e a leitura do resumo foram trocados no
  mesmo sentido.

### C2. Pré dos ATT que excluem zero não era destacado (corrigido)

A tabela mostrava o pré, mas a leitura só marcava o 12.2 agregado e o 12.5.
Agora a leitura lista todo ATT principal com IC fora de zero (7 de 20) com o
pré de cada um:

| Linha | ATT | Pré |
|---|---:|---|
| 12.2, todos os cursos | +14,34 | Wald p = 0,040 (não plano); sup-t p = 0,595 |
| 12.2, curso 14 | +39,79 | Wald p = 0,003 (não plano); sup-t p = 0,632 |
| 12.5, K1_reg | +16,23 | Wald p = 0,005 (não plano); sup-t p = 0,745 |
| 12.4, K2r_tot (D2) | +2,12 | Wald p = 0,477, mas θ médio do pré +1,18, mesmo sinal e mais da metade do ATT |
| 12.3c, tercil 2 | +70,71 | Wald p = 0,193, mas θ médio do pré +51,94 |
| 12.3a, só nunca tratados | +43,42 | Wald p = 0,597; θ médio do pré −24,61, sinal oposto: o ATT depende do mês-base |
| 12.2, curso 15 | +5,08 | Wald p = 0,930; sem ressalva do pré, ainda ATT sob tendências paralelas |

O texto não chama nenhuma delas de efeito. O sup-t não rejeita em nenhuma das
três com Wald < 0,05; vale o Wald, que é a regra do doc 50.

### C3. Convenção do doc 50 ausente (corrigido)

O doc 50 e a auditoria 21 acrescentam, além do Wald, a leitura do θ médio do pré
(inteiro ou nos 12 meses antes do mês-base), de mesmo sinal ou oposto e com pelo
menos metade do ATT do pós. O script 27 não aplicava essa regra, e K2r_tot e o
tercil 2 apareciam como "compatível com plano". Agora a tabela traz a coluna
"θ médio do pré (−24 a −2 / −13 a −2)", e as funções `theta_pre` e `classe_pre`
aplicam a mesma regra. O teste `test_classe_pre_regra_do_doc50` fixa o limiar.

### C4. Limites não declarados (declarados agora, datados)

1. **12.3c, ligação do médico.** A ligação da lista nominal ao CNES (X1, regra
   D1) usa seis competências, entre elas 202510, 202602 e 202608, posteriores ao
   início de muitos médicos. O valor de cada médico usa só a última competência
   anterior ao início, mas quem entra na fração pode depender de informação
   posterior à chegada. O mesmo desvio traz que os tercis têm tamanhos desiguais
   (122, 68 e 95 municípios), porque o corte inferior, 0,000, agrupa todos os
   municípios sem incumbente. A diferença entre tercis continua descritiva.
2. **Leitura do pré e do 12.5**, nova entrada de desvios, com a convenção do
   doc 50.

### C5. Figuras (corrigido)

As figuras não têm título, legenda nem anotação: só rótulos de eixo. O "Como
ler" é curto (uma ou duas frases, sem número). Faltava avisar, como o D2 do doc
50 faz, quando o eixo vertical é limitado: na figura 12.5, dois meses de K1_reg
têm intervalo cortado na borda. O "Como ler" agora diz isso (campo
`eixo_cortado` no resumo) e as demais figuras só o dizem se o eixo for limitado.
Os PNG não mudaram byte a byte.

## 6. Testes e determinismo

- `TestRecalculoIndependenteAuditoria25`, 7 testes: 12.1, 12.2, 12.3a e K1 do
  doc 50, 12.4, 12.5, BKY próprio e pesos do DiD sintético.
- Três testes novos de relato, em `TestSaidas`: leitura com pré destacado e sem
  separar deslocamento de expansão líquida, regra de `classe_pre` e figuras.
- `tests/test_producao_extensoes.py` passou de 24 para 34 testes.
- O script 27 rodou uma vez depois da correção (4 min 17 s). Os hashes antes e
  depois:
  - iguais: `K_X_estimativas.csv`, `K_X_estudo_evento.csv`, `K_X_att_gt.csv` e os
    6 PNG;
  - diferentes, como esperado: `K_X_resumo.json` (desvios, leitura e "Como ler")
    e o doc 57c.
- `tests/test_producao_extensoes.py`, `tests/test_producao_K.py` e
  `tests/test_pipeline_rdd_bolsa.py`: 89 testes, todos passaram. `run_all.py` e a
  suíte completa não foram rodados.

## 7. Números principais (depois da correção)

Os números de estimativas não mudaram.

- **12.2, todos os cursos:** +14,34 (IC 95% [+3,08; +25,60]), pré não plano.
- **12.4, K2r_tot (D2):** +2,12 (IC [+0,30; +3,94]), pré parecido; K2r: +0,15,
  inclui zero. Em D1, empilhado, K2r_tot −1,48 (IC [−3,21; +0,25]).
- **12.1, K2:** v1 +0,72 e v2 +0,71; K1 não reestimado (SIA sem revisão).
- **12.3:** só nunca tratados +43,42; DiD sintético agregado +31,58 (IC
  [−15,41; +78,56]); tercil 3 − tercil 1 +37,50 (IC [−26,02; +101,02]).
- **12.5:** K1_reg +16,23, pré não plano; K2_reg −0,41, inclui zero.
- **BKY do adendo:** 0 de 8 linhas com q < 0,05; o menor q é 0,101.

## 8. Observações ao autor (sem execução aqui)

1. O 12.2 agregado e o curso 14 têm pré que rejeita pelo Wald. O resultado do
   12.2 só pode ser lido como associação até haver uma fonte de exogeneidade
   para a chegada por curso.
2. O 12.3a (só nunca tratados) tem pré de sinal oposto ao ATT. Se esse for o
   controle preferido, vale registrar um adendo que fixe o mês-base ou a média do
   pré como base.
3. Os cursos 10 e 11 têm o mesmo outcome por construção. O agregado do 12.2 conta
   a mesma produção duas vezes, com peso pelo número de pares de cada curso. O
   cluster no município protege o EP, mas não o peso.
