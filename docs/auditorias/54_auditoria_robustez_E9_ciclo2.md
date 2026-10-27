# 54. Auditoria do adendo 52f: robustezes do E9 no ciclo 2 com o tipo de vaga do quadro de 13/02/2026

> **Data:** 27/10/2026.<br>
> **Objeto:**
> - adendo [`52f`](../06_execucao/52f_adendo_robustez_E9_ciclo2_quadro_1302.md), congelado no commit `9540a8a`;
> - script `scripts/rdd_bolsa/52_robustez_E9_ciclo2_quadro_1302.py`;
> - saídas `output/rdd_bolsa/RB_*`;
> - doc [`57y`](../06_execucao/57y_robustez_E9_ciclo2_quadro_1302.md), com o inventário e as 11 decisões no commit
>   `2f7deba`, antes das estimativas;
> - testes `tests/test_robustez_E9_ciclo2_quadro_1302.py`.
>
> Base: branch `worktree-agent-a280cd3231245ee7b` (commits `2f7deba` e `01ab673`), juntado sobre
> `claude/vigilant-mccarthy-dd92mc`.<br>
> **Referências:**
> - `CLAUDE.md`;
> - docs [42](../06_execucao/42_resultados_E9_escolha.md) e [44](../06_execucao/44_sintese_rdd_bolsa_multioutcome.md);
> - adendos [52c](../06_execucao/52c_adendo_vaga_imediata_ciclo2.md) e
>   [52d](../06_execucao/52d_adendo_sensibilidades_ciclo2_quadro_1302.md), docs
>   [57p](../06_execucao/57p_escolha_vaga_imediata_c2.md) e [57v](../06_execucao/57v_sensibilidades_ciclo2_quadro_1302.md);
> - auditorias [41](41_auditoria_escolha_vaga_imediata_c2.md) e [46](46_auditoria_sensibilidades_ciclo2.md) (A1, A2 e
>   A10);
> - scripts 12, 16, 42 e 48, lidos e não importados;
> - `output/rdd_bolsa/E9_robustez_pos_auditoria.csv`.
>
> **Método:** recálculo próprio em memória, com scripts no scratch. O recálculo não importa os scripts 52, 48, 42, 16
> nem 12. Ele lê direto:
> - os dois quadros brutos do ciclo 2 (xlsx de 13/02 e de 19/03), com leitor próprio, e a leitura independente da
>   auditoria 36 (`a36_celulas.csv`);
> - os parquets de escolhas e do conjunto principal (`outcomes/escolhas_*`) e o IVS oficial (a08).
>
> Escrevi do zero o logit condicional (Newton amortecido), o CR1 por conjunto e por curso, o CV3, o score bootstrap de
> Kline–Santos (Rademacher por enumeração; Webb com a semente e o tamanho fixados no script 16), a inversão do score,
> os cortes placebo e o BKY de Anderson (2008).<br>
> **Estatuto do que se audita:** `ADENDO_52F_POS_RESULTADO`. É escolha condicional a se candidatar, dentro das vagas
> abertas. O peso da bolsa mede o pacote do corte de IVS, não a participação no PMM-E.

## Veredito

**Aprovado com correções.** Todos os números que recalculei batem com o gravado, e a leitura `MANTEM` segue a regra
fixada antes das contas. Recalculei 134 quantidades de `RB_estimativas.csv`, e a maior diferença relativa é 4,9e−9.
Entre elas:
- **RB-1 no ciclo 2 corrigido:**
  - CR1: 0,1423 [0,0754; 0,2093];
  - CV3: p = 0,0036 e IC [0,0542; 0,2305];
  - score bootstrap: Rademacher p = 6,1e−5 (4 de 65.536 vetores de sinais) e Webb p = 0,0021;
  - inversão do score: [0,0765; 0,2169].
- **RB-2:** |t| real 4,17; os 27 |t| placebo batem um a um (diferença máxima 1,1e−9); nenhum chega ao real; p por
  posto 1/28 = 0,036.
- **As três linhas que perdem o IC que exclui 1:**
  - degrau 0,400 com spline quadrático no conjunto só com vaga imediata: 0,5947 [−0,0255; 1,2149], p = 0,060;
  - janela ±0,025 com spline linear: 0,1338 [−0,0068; 0,2743], p = 0,062;
  - janela ±0,025 com spline cúbico: 0,1279 [−0,0737; 0,3296], p = 0,214.
- **Spline cúbico no ciclo 2:** 0,0583 [−0,0272; 0,1438], p = 0,181.

O portão RB-6 passa. Com o quadro de 19/03, o meu código reproduz `E9_estimativas.csv` e `E9_robustez_pos_auditoria.csv`
nas peças acima, inclusive os p de bootstrap gravados:
- ciclo 2: Rademacher 9,16e−5, Webb 0,00221 e CV3 0,0010;
- empilhado, cluster por conjunto: 0,0101 e 0,0104;
- empilhado, cluster por curso: 0,0424 e 0,0467.

**Nenhuma estimativa mudou.** As correções são de texto, feitas no gerador do 57y e regravadas com `--atualizar-doc`
(A1 a A4), mais o cabeçalho.

O ponto de mérito está na força do `MANTEM`, não na regra. A regra pede só que nenhum corte falso alcance o |t| real.
Isso continua valendo, mas por pouco:
- o maior |t| placebo sobe de 3,68 para 4,08, contra um |t| real que cai de 4,71 para 4,17;
- os cortes falsos com |t| > 1,96 dobram, de 4 para 8 de 27.

O p por posto (0,036) não mostra essa folga, porque já é o piso da grade. O texto dizia que o piso era o mínimo
possível, e isso estava certo. Mas a linguagem simples dizia que "os testes dão o mesmo recado", sem a folga. Com o
spline cúbico, nenhuma das quatro especificações do ciclo 2 exclui zero na versão corrigida. Isso já era a ressalva do
doc 44, e o texto agora diz as duas coisas.

## Achados, por gravidade

### Médios

**A1. A família BKY deixa q < 0,05 em linhas com p ≥ 0,05, inclusive no placebo do empilhado (corrigido no texto).**

A decisão 9 põe na família todas as inferências secundárias sobre o peso da bolsa. Entram, por exemplo, o score
bootstrap Rademacher, o Webb, o CV3 e o CR1 por curso do mesmo coeficiente. Esses membros rejeitam juntos. O BKY
adaptativo estima, a partir da própria família, quantas nulas são verdadeiras. Aqui ele estima poucas e afrouxa o
limiar. Refiz o BKY com código próprio, e os 148 q batem com os gravados (diferença 0).

O resultado:

| Quadro do ciclo 2 | Membros | q < p | p ≥ 0,05 e q < 0,05 |
|---|---|---|---|
| 19/03 | 74 | 35 | 3 |
| 13/02 | 74 | 32 | 4 |

Na versão corrigida, as quatro linhas são:
- o p por posto do empilhado (p = 0,107; q = 0,041);
- o degrau 0,400 do RB-4 (p = 0,060; q = 0,027);
- a janela ±0,025 com spline linear no ciclo 2 (p = 0,062; q = 0,028) e no empilhado (p = 0,086; q = 0,033).

Por isso a tabela da seção 5.6 marca o RB-2 como "2 de 2" com q < 0,05. Mas o próprio 57y e o doc 44 dizem que o
empilhado não resiste aos placebos. E duas das três linhas que "perdem o IC" teriam q < 0,05.

A conta está certa. A decisão 9 é uma leitura possível de "BKY entre as secundárias" e foi gravada antes das
estimativas. Não mexi na família. O problema é de leitura: a contagem "65 → 63 com q < 0,05" parece uma contagem de
achados, e não é.

**Correção** (texto do gerador, seção 5.6): um parágrafo "Como ler o q". Ele diz por que o q fica abaixo do p e lista,
por versão, as linhas com p ≥ 0,05 e q < 0,05. Diz também que a contagem não é de achados independentes e que a
leitura do §3 não usa o q.

**Recomendação ao autor:** numa próxima família, pôr um membro por hipótese, e não várias inferências do mesmo
coeficiente; ou usar BH sem o passo adaptativo.

**A2. A resposta curta não mostrava que a folga do corte verdadeiro sobre os placebos encolheu (corrigido no texto).**

| Ciclo 2 | Antiga (19/03) | Corrigida (13/02) |
|---|---|---|
| \|t\| real | 4,71 | 4,17 |
| maior \|t\| placebo (corte) | 3,68 (0,230) | 4,08 (0,230) |
| segundo maior | 2,23 (0,450) | 4,03 (0,450) |
| \|t\| placebo > 1,96 | 4 de 27 | 8 de 27 |
| média; dp do t placebo | −0,30; 1,52 | −0,81; 1,75 |

A regra da decisão 7 dá `MANTEM` nas duas versões, e eu confirmo. O p por posto, 0,036, é o mínimo possível com 27
placebos, e o 57y dizia isso duas vezes (na resposta curta e nos limites). Mas o p por posto fica igual mesmo quando o
corte verdadeiro passa a vencer o falso de 0,230 por 0,08 de |t|. Com o quadro de 13/02, a cauda dos placebos engrossa,
e a frase "os testes dão o mesmo recado" ficava forte demais.

**Correção** (resposta curta e linguagem simples): os números da folga entram na resposta, com a frase "ainda fica à
frente de todos os falsos, mas por pouco". A linguagem simples ganha a ressalva da folga.

**A3. O spline cúbico estava dito, mas sem o peso todo (corrigido no texto).**

A frase sobre o spline cúbico estava certa no conteúdo: p de 0,083 para 0,181, com IC que contém zero. Mas a
pontuação era confusa ("vai de X; p = 0,083 para Y; p = 0,181"). Faltava também dizer que, das quatro especificações
cúbicas do ciclo 2 (sem janela e nas janelas de ±0,10, ±0,05 e ±0,025), o IC exclui zero:
- em 1 com o quadro de 19/03 (janela ±0,025, p = 0,035);
- em 0 com o quadro de 13/02.

O coeficiente cúbico (0,058) é menos da metade do linear (0,142). A frase do doc 44 fala de robustez a poucos clusters
e a placebos, e o `MANTEM` vale para ela. Mas o leitor da linguagem simples não ficava sabendo que a forma funcional
continua sendo o ponto fraco.

**Correção:** frase reescrita, com a contagem das quatro cúbicas e a observação de que a regra do §3 não confere
robustez a uma forma mais flexível do IVS. A linguagem simples ganha a ressalva.

### Baixos

**A4. "Exclui 1" e "exclui 0" para a mesma coisa (corrigido no texto).** A resposta curta e o §3 falam do IC da razão
de chances que exclui 1. A tabela da seção 5.7 fala do IC do coeficiente que exclui 0. São equivalentes, mas o texto não
dizia isso. A nota "Como ler" da 5.7 agora diz.

**A5. O título da figura afirma a robustez sem a ressalva (sem correção; fica para o autor).** O título é "Com o tipo de
vaga da inscrição, o ciclo 2 continua robusto a poucos clusters e a placebos". Ele segue a regra, e o painel da direita
mostra a folga pequena. Mudar o título exige regravar a figura e o `RB_resumo.json` pela execução inteira, o que está
fora de uma correção de texto com `--atualizar-doc`. Sugestão para a próxima execução: "... continua à frente dos
placebos, por pouco".

### Sem achado (fidelidade ao adendo)

| Ponto do adendo ou das decisões | Verificação |
|---|---|
| Inventário RB-1 a RB-5 | cobre os sete itens do A1 da auditoria 46: score bootstrap, CV3, inversão, placebos, cúbico, nós a cada 0,05 e janelas. Cobre o A2 (quadrática, degraus e cluster por curso do conjunto só com vaga imediata) e o que ficou "fora do 52d" (explodido, quadrática e degraus no conjunto principal). Os cinco itens de `robustez_pos_auditoria` do 16 estão todos classificados: o item 5 vai como apoio, e o 1+3 como sem mudança. Contei 16 linhas no RB-3, 16 no RB-4, 33 no RB-5, 7 no RB-1 empilhado e 2 no RB-2, que somam os 74 membros do BKY e as 65 linhas lidas do RB-3 ao RB-5 |
| Decisão 7: score bootstrap com Rademacher e Webb | o §3 diz "score bootstrap"; a decisão exige os dois pesos, o que é mais estrito. O CV3 usa a t com G − 1 gl, como no 16 |
| Decisão 7: regra do RB-2 | "nenhum \|t\| placebo ≥ \|t\| real" é a leitura literal de "corte verdadeiro fora da distribuição dos placebos, como no original" (no doc 42, 0 de 27). O caso `PLACEBO_NAO_CONFIRMA` acrescenta um desfecho que o §3 não previa e só o relata; não afrouxa nada |
| Decisão 3: empilhado como secundária | o §2 nomeia o ciclo 2 como principal. O empilhado entra como secundário, como no doc 42; isso amplia o relato e não muda a principal. A principal é única (teste `test_principal_unica`) |
| Decisão 9: família BKY nova | o §2 pede "BKY entre as secundárias"; a família fixada é uma leitura possível. A forma dela tem efeito na leitura do q: ver A1 |
| Decisões 1, 2, 4, 5, 6, 8, 10 e 11 | seguem os scripts 16, 42 e 48; não mudam amostra, conjunto de escolha nem especificação. Sementes e grades são as do 16 (o meu Webb, com `default_rng([20261018, G, 6])` e 199.999 sorteios, reproduz o p gravado) |
| Ordem dos commits | o bloco de decisões do 57y em `2f7deba` (15:22) é idêntico ao de `01ab673` (15:36), conferido por `diff` e pelo teste. `RB_*` só aparecem em `01ab673`. Entre os dois commits, o script muda só em texto e figura (rótulos, `_quantos`, frase "o menor possível", veredito da linguagem simples, limites do eixo) e num `.copy()` em `_sel`, que não muda número. As funções `regra_rb`, `entra_bky`, `criterio`, `leitura` e `DECISOES` não mudaram. A execução inteira leva 181 s, compatível com os 14 minutos entre os commits. O `--pre-registro` se recusa a rodar se `RB_resumo.json` existe. O Git não prova que nada rodou antes, mas nada indica que rodou |
| Correção do tipo de vaga | com leitor próprio, o quadro de 13/02 tem 1.547 células e nenhuma sem número; 714 têm vaga imediata, com 1.206 vagas. Bate com a `a36_celulas.csv` em 1.547 de 1.547. O quadro de 19/03 reproduz as covariáveis gravadas. O conjunto só com vaga imediata tem 714 células e 1.140 candidatos (eram 1.015 e 1.798) |

## Integridade

| Item | Resultado |
|---|---|
| IVS errado | nem o 52 nem a cadeia importada (48, 42, 25c, 25, 16, 17, 19, 12, `rdd_lib`) cita `data/ivs_ipea_2010_municipios.csv`; o IVS vem do a08. O meu recálculo também usa o a08 |
| `EMPIRICO` | nas 1.816 linhas de `RB_estimativas.csv` e no resumo; estatuto `ADENDO_52F_POS_RESULTADO` em todas |
| Imputação | nada imputado. `corrigir` (42) e `marca_vaga_imediata` (48) param se faltar célula ou número; nenhum falta |
| `E9_*`, `VC_*`, `VD_*`, `VL_*` | em `output/rdd_bolsa/`, só `RB_*` mudam entre `a94ef67` e `01ab673`. Os SHA-256 de `E9_*`, `VC_*`, `VD_*` e `VL_*` ficam iguais depois da reexecução |
| Determinismo | reexecutei o 52 inteiro (181 s) antes das correções de texto. `RB_estimativas.csv`, `RB_resumo.json`, `RB_antigo_corrigido.png` e o 57y saíram iguais, byte a byte, aos de `01ab673`. Depois das correções, só o 57y muda, regravado com `--atualizar-doc` |
| Testes | `tests/test_robustez_E9_ciclo2_quadro_1302.py` (28) e `tests/test_pipeline_rdd_bolsa.py` (15): 43 passam. O teste do cabeçalho agora espera o link desta auditoria, e o da linguagem confere as frases novas (folga, cúbicas e leitura do q) |

## Texto do 57y

- **Linguagem simples.** Clara, com a frase do doc 44 entre aspas e a regra explicada. Faltavam a folga dos placebos
  (A2) e o peso do spline cúbico (A3).
- **Linguagem causal.** "Efeito da bolsa sobre a 1ª opção" é o estimando do E9 (doc 42). Vem sempre com o pacote do
  corte, condicional a se candidatar e dentro das vagas abertas. A origem aparece como preferência revelada. Sem
  achado.
- **Números fora dos blocos.** Só datas, o commit do adendo e o número desta auditoria no cabeçalho. O teste confere, e
  continua passando depois das correções.
- **"O menor possível com essa grade".** Está dito na resposta curta e nos limites ("Placebos têm piso").

## O que foi recalculado

"Gravado" é o valor de `RB_estimativas.csv`. As diferenças são relativas, com piso 1.

| Item | Recalculado (antiga → corrigida) | Gravado | Diferença máxima |
|---|---|---|---|
| Quadro de 13/02, ciclo 2 | 1.547 células; 714 com vaga imediata; 1.206 vagas (eram 1.015 e 1.836) | igual | 0 |
| RB-1 CR1, ciclo 2 | 0,13310 [0,07776; 0,18844] → 0,14234 [0,07538; 0,20929] | igual | < 5e−9 |
| RB-1 score bootstrap, ciclo 2 | Rademacher 9,155e−5 → 6,104e−5; Webb 0,002210 → 0,002055 | igual | < 5e−9 |
| RB-1 CV3, ciclo 2 | p 0,00100 [0,06345; 0,20275] → p 0,00363 [0,05419; 0,23048] | igual | < 5e−9 |
| RB-1 inversão, ciclo 2 | [0,06824; 0,18816] → [0,07648; 0,21686] | igual | < 5e−9 |
| RB-1 empilhado | CR1 p 0,0029 → 0,0037; score por conjunto 0,0101/0,0104 → 0,0101/0,0108; por curso 0,0424/0,0467 → 0,0353/0,0405 | igual | < 5e−9 |
| RB-2, ciclo 2 | t real 4,714 → 4,166; 27 t placebo; máx. 3,684 → 4,082; 0 → 0 ≥ real; p por posto 0,036 → 0,036 | igual | < 2e−9 |
| RB-2, empilhado | t real 2,983 → 2,902; 2 → 2 ≥ real; p por posto 0,107 → 0,107 | igual | < 5e−9 |
| RB-3, ciclo 2 | cúbico, nós a cada 0,05 e as seis janelas (coef., IC, p) | igual | < 5e−9 |
| RB-4, ciclo 2 | quadrática com bolsa linear; degraus com spline quadrático (0,300 e 0,400); candidatos 1.798 → 1.140 | igual | < 5e−9 |
| BKY | os 148 q (74 por versão), com código próprio | igual | 0 |
| Portão RB-6 | as peças acima, versão antiga, contra `E9_estimativas.csv` e `E9_robustez_pos_auditoria.csv` | igual | < 5e−9 |

Não refiz o explodido, as variantes de degraus com spline linear, os efeitos marginais em p.p. nem a inversão por
curso. Eles saem das mesmas funções e foram conferidos pelo portão (versão antiga) e pela reexecução byte a byte.

## O que mudou nesta auditoria

- `scripts/rdd_bolsa/52_robustez_E9_ciclo2_quadro_1302.py`: só texto gerado:
  - resposta curta: folga dos placebos (A2), frase do spline cúbico e contagem das quatro cúbicas (A3), e as duas
    ressalvas na linguagem simples;
  - seção 5.6: parágrafo "Como ler o q" (A1);
  - nota da seção 5.7 (A4);
  - cabeçalho com o link desta auditoria.

  Nenhuma conta mudou. Decisões, inventário, regra e família BKY ficam intactos.
- `docs/06_execucao/57y_robustez_E9_ciclo2_quadro_1302.md`: regravado com `--atualizar-doc`.
- `tests/test_robustez_E9_ciclo2_quadro_1302.py`: o cabeçalho esperado passa de "pendente" para o link desta
  auditoria. O teste de linguagem confere as frases novas.
- `RB_estimativas.csv`, `RB_resumo.json` e a figura: sem mudança.

## O que fica para o autor

1. A frase do doc 44 "o ciclo 2 é robusto a poucos clusters e a placebos" continua valendo pela regra pré-registrada,
   agora com o quadro da inscrição. Decidir se o doc 44 ganha a nuance da folga menor contra os placebos (A2). Editar o
   doc 44 é decisão do autor.
2. Decidir se a família BKY da decisão 9 continua como está em relatos futuros, ou se passa a um membro por hipótese
   (A1).
3. Na próxima execução do 52, considerar um título da figura com a ressalva da folga (A5).
