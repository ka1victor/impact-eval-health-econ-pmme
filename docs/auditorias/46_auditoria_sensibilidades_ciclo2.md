# 46. Auditoria do adendo 52d: sensibilidades da escolha no ciclo 2 com o tipo de vaga do quadro de 13/02/2026

> **Data:** 26/10/2026.<br>
> **Objeto:**
> - adendo [`52d`](../06_execucao/52d_adendo_sensibilidades_ciclo2_quadro_1302.md), congelado no commit `c87ed75`;
> - script `scripts/rdd_bolsa/48_sensibilidades_ciclo2_quadro_1302.py`;
> - saídas `output/rdd_bolsa/VD_*`;
> - doc [`57v`](../06_execucao/57v_sensibilidades_ciclo2_quadro_1302.md), com o inventário e as 10 decisões no commit
>   `e90ef4f`, antes das estimativas;
> - testes `tests/test_sensibilidades_ciclo2_quadro_1302.py`.
>
> Base: branch `claude/vigilant-mccarthy-dd92mc`, commit `b80e92d`.<br>
> **Referências:**
> - `CLAUDE.md`;
> - adendo [52c](../06_execucao/52c_adendo_vaga_imediata_ciclo2.md), doc
>   [57p](../06_execucao/57p_escolha_vaga_imediata_c2.md) e [auditoria 41](41_auditoria_escolha_vaga_imediata_c2.md)
>   (achado A1);
> - docs [42](../06_execucao/42_resultados_E9_escolha.md), [44](../06_execucao/44_sintese_rdd_bolsa_multioutcome.md),
>   [57a](../06_execucao/57a_resultados_P1_escolha.md) e [57i](../06_execucao/57i_resultados_P1h_magnitudes.md);
> - [auditoria 36](36_auditoria_dados_H1.md);
> - scripts 12, 16, 25 e 25c, lidos e não importados.
>
> **Método:** recálculo próprio em memória, com scripts no scratch. O recálculo não importa os scripts 48, 42, 25c,
> 25, 16 nem 12. Ele lê direto:
> - o quadro bruto do ciclo 2 de 13/02/2026 (xlsx), com leitor próprio, e a leitura independente da auditoria 36
>   (`a36_celulas.csv`);
> - os parquets de escolhas e do conjunto principal (`outcomes/escolhas_*`) e o IVS oficial (a08);
> - a origem G1 (`G1_candidatos_origem.parquet`, regra `g1_cpf_nome`);
> - a tabela de regiões de saúde do TabNet (`.cnv`) e os centroides do IBGE (JSON), com leitores próprios.
>
> Escrevi do zero o logit condicional (Newton amortecido), o sanduíche CR1 com fator G/(G − 1) por conjunto de
> escolha e por curso, o método delta da DAP, o Wald e o BKY de Anderson (2008).<br>
> **Estatuto do que se audita:** `ADENDO_52D_POS_RESULTADO`. É escolha condicional a se candidatar, dentro das vagas
> abertas. O peso da bolsa mede o pacote do corte; não é participação no PMM-E. A origem é preferência revelada.

## Veredito

**Aprovado com correções.** Tudo o que recalculei bate com o gravado:
- o conjunto "só vaga imediata" do ciclo 2 com o quadro de 13/02: **714 células** e **1.140 candidatos** (eram
  1.015 e 1.798), 1.206 vagas imediatas somadas;
- o VD-1: razão de chances **1,955878 [1,324372; 2,888508]**, igual ao gravado em 6 casas; a antiga, 1,950678
  [1,422564; 2,674850];
- o VD-2, as variantes M4, M5 por ciclo, M6 da nota e M6 do município, o Wald do P1d, a DAP do M4 e as duas
  famílias BKY.

O portão VD-5 passa: as 2.865 quantidades da versão antiga que comparei com `E9_*`, `P1_*`, `P1_dap.csv` e
`P1h_magnitudes.csv` são iguais na precisão gravada (10 algarismos).

**Nenhuma estimativa mudou.** As correções são de texto, nos blocos gerados do 57v (A1, A3 a A6, A11), e no cabeçalho.

O ponto de mérito é o A1. A resposta curta mantém a frase do doc 44 sobre a robustez do ciclo 2. A regra do §3 manda
isso, e o VD-1 confere. Mas a parte "robusto a placebos" do doc 44 vem do conjunto **principal**, e os placebos, o
spline cúbico e as janelas desse conjunto ainda usam o quadro de 19/03. O texto dizia só que eles "não foram refeitos
no conjunto de sensibilidade", onde eles nunca existiram. O autor podia ler que a frase inteira do doc 44 ficou
conferida.

## Achados, por gravidade

### Médios

**A1. A resposta curta não deixava claro o que da robustez do doc 44 ainda usa o quadro de 19/03 (corrigido no
texto).**

O doc 44 diz que o ciclo 2 é "robusto a poucos clusters e a placebos". As peças por trás disso estão em
`E9_robustez_pos_auditoria.csv` e são todas do conjunto principal: score bootstrap, CV3, inversão do score, placebos
de corte, spline cúbico, nós a cada 0,05 e janelas. O adendo 52c corrigiu o E9 principal desse conjunto, mas nenhuma
dessas robustezes. A auditoria 41 refez só o score bootstrap de Rademacher, no scratch (p = 6,1e−5).

O 57v dizia: "Os placebos de corte, o score bootstrap e o spline cúbico do doc 42 não foram refeitos no conjunto de
sensibilidade (decisão 2)." A frase é verdadeira, mas aponta para o lugar errado. A lacuna real é o conjunto
principal corrigido.

O adendo 52d não pedia esses placebos. O §1 lista o conjunto de sensibilidade, o M2 a M9 e a DAP. O §2 fala em
"score bootstrap onde o original usou", e nas linhas VD o original não usou. Então não é desvio de execução. É
clareza: "mantêm a frase do doc 44 nesta peça" precisa dizer qual parte da frase ficou conferida.

**Correção** (texto fixo do gerador do 48; o 57v foi regravado com `--atualizar-doc`):
- a resposta curta do VD-1 agora diz que, no conjunto principal corrigido, placebos, spline cúbico, janelas e cluster
  por curso continuam com o quadro de 19/03, e que a parte "robusto a placebos" do doc 44 não foi conferida com o
  quadro de 13/02;
- o item "Só o tipo de vaga do ciclo 2 muda", nos limites, diz o mesmo.

**A2. A decisão 2 reduz o §2 ("exatamente as mesmas especificações") e devia ter ido para o autor como pendência
(sem correção nos números; registrado).**

No conjunto de sensibilidade, o doc 42 estimou quatro especificações por ciclo: spline linear ou quadrático, com a
bolsa linear ou em degraus. Ele estimou também o CR1 por curso no empilhado. A decisão 2 refez só a especificação
principal. O §3 lê o VD-1 pela razão de chances por +R$ 5 mil do E9 principal, então a leitura do adendo não muda.
Mas o §2 diz "exatamente as mesmas especificações", e a variante quadrática também dá razão de chances por +R$ 5 mil.

Refiz as que faltavam no scratch. Meu código reproduz as linhas antigas de `E9_estimativas.csv` (por exemplo, a
quadrática do ciclo 2, coef. 0,143734, p = 1,4e−11). Estes números são da auditoria e não entram no 57v:

| Conjunto só vaga imediata | Antiga (19/03) | Corrigida (13/02) |
|---|---|---|
| Ciclo 2, spline quadrático, bolsa linear: razão de chances [IC 95%] | 2,05 [1,67; 2,53] | 2,01 [1,53; 2,63] |
| Ciclo 2, spline linear, degraus: 0,300 / 0,400 (coef.; p) | 0,564 (< 0,001) / 0,769 (< 0,001) | 0,576 (0,005) / 0,734 (0,003) |
| Ciclo 2, spline quadrático, degraus: 0,300 / 0,400 (coef.; p) | 0,774 (< 0,001) / 0,685 (< 0,001) | 0,914 (0,041) / 0,595 (0,060) |
| Ciclos 1–3, spline quadrático, bolsa linear: razão de chances [IC 95%] | 1,92 [1,62; 2,28] | 1,86 [1,53; 2,24] |
| Ciclos 1–3, spline linear, bolsa linear, CR1 por curso (G = 24): p | 8,3e−6 | 1,2e−5 |

A bolsa linear continua com IC sem 1 em todas as variantes. A única linha que passa de p < 0,05 para p ≥ 0,05 é o
degrau de 0,400 com spline quadrático no ciclo 2 (0,060). É a especificação mais exigente do E9, com 16 conjuntos.
Os placebos e o spline cúbico seguem sem refazer nos dois conjuntos (A1).

O limite do 57v agora cita as variantes quadrática e de degraus do conjunto só com vaga imediata como não refeitas.
A decisão 2 não foi editada, porque é registro pré-estimativa.

### Baixos

**A3. A mudança de significância de `bolsa_x_sem_pontuacao` no M6 da nota é efeito da família BKY, não da linha
(corrigido no texto).**

Refiz o M6 da nota e confere:
- antiga: −0,104239 [−0,200389; −0,008088], p = 0,033600, q = 0,047;
- corrigida: −0,105493 [−0,201975; −0,009010], p = 0,032113, q = 0,051.

O p da própria interação **cai**. O q sobe porque outros membros da família ficam com p maior: M5 do ciclo 2
(0,0015 → 0,0048), interação do mesmo município (0,0031 → 0,0164) e média da bolsa no M8 (0,019 → 0,024). Com menos
rejeições na 1ª etapa do BKY, o limiar fica mais baixo. A linha passa de 0,047 para 0,051, na borda.

O 57v listava a linha como "sim → não" sem dizer isso. O leitor podia entender que a interação enfraqueceu.

**Correção:** a resposta curta agora mostra o p e o q da linha nas duas versões. A seção 5.7 ganhou uma nota: nas
famílias BKY, o q depende dos p de todos os membros.

**A4. A mudança de sinal do M6 do curso é de uma inclinação nula (corrigido no texto).**

A inclinação do curso 18 vai de −0,0038 (p MV 0,881) para +0,0003 (p MV 0,990). A regra da decisão 8 conta isso como
mudança de sinal, e por isso o M6 do curso sai da lista "base da H2". O 57v não dizia o tamanho.

**Correção:** a resposta curta agora mostra a linha que muda de sinal, com a estimativa antiga e a corrigida. A
seção 5.7 lembra que uma estimativa perto de zero pode trocar de sinal sem mudar a leitura.

**A5. A DAP do capital no M4 "muda de significância", mas a DAP é descritiva (corrigido no texto).**

Refiz e confere: −5,2401 [−10,1071; −0,3730] → −4,5473 [−9,8340; +0,7394]. Pelas decisões 4 e 5 e pelo P1, a DAP é
descritiva, sem teste de zero. A decisão 8 usa o IC delta como critério de "significância". A tabela 5.7 está certa
pela regra, mas a palavra pede um aviso.

**Correção:** nota na seção 5.7: na DAP e nos km, "significância" é só o IC delta excluir zero; continuam
descritivos.

**A6. Lista ambígua no VD-3 (corrigido no texto).**

"a leitura da H2 se apoia nas que não mudam: M2 (log da distância), M4 (efeito fixo de UF), M6, nota, M6, município
de origem, M7…" Os rótulos têm vírgula, e a lista também. Agora as listas usam ponto e vírgula.

**A7. Entradas sem hash (sem correção; recomendação).** `entradas`, em `VD_resumo.json`, tem 26 arquivos com
SHA-256, e todos conferem. Mas faltam:
- o script 12, cujo `ler_quadro` lê os dois quadros do ciclo 2 (pelo 42);
- os scripts 17 e 19, que leem os centroides e a CIR;
- a `rdd_lib`.

Os dados lidos por eles têm hash, e o meu leitor próprio dá os mesmos números. Não corrigi, porque isso exige
regravar `VD_resumo.json` pelo script. Fica para a próxima execução do 48.

**A8. O teste das decisões compara o doc com as constantes do script, não com o commit `e90ef4f` (sem correção).**
`test_decisoes_iguais_as_do_pre_registro` passaria mesmo se as constantes tivessem mudado depois das estimativas.
Conferi à mão: os blocos `decisoes` e `inventario` do 57v são iguais, byte a byte, entre `e90ef4f` e `b80e92d`.

**A9. A ordem "decisões antes das estimativas" só é verificável pela ordem dos commits (sem correção).**

Os commits:
- adendo congelado em `c87ed75` (22:25);
- decisões, inventário e o script inteiro (1.797 linhas, sem rodar) em `e90ef4f` (22:41);
- saídas e blocos em `39f129c` (23:39).

Entre `e90ef4f` e `39f129c`, o script mudou em 31 linhas. Nenhuma toca a estimação:
- `fillna` numa comparação de colunas;
- a regra do VD-1 extraída para uma função (mesma lógica);
- a família filtrada na tabela BKY;
- layout da figura;
- concordância de número numa frase.

Pelo Git, não dá para provar que nenhuma conta rodou antes de `e90ef4f`. Nada nos resultados sugere escolha
retrospectiva: as decisões seguem os scripts 12, 16, 25 e 42.

**A10. O inventário de "fora do adendo" está certo pela letra (sem correção).**

O 57v lista como fora do §1:
- o logit explodido e as variantes quadrática e de degraus do E9 no conjunto principal;
- o M0;
- a ponte P1g;
- os pesos da figura do P1h.

Pela letra do §1, nenhum deles precisava entrar. O §1 lista três grupos: o conjunto só com vaga imediata, o M2, M4 e
M6 a M9, e a DAP que depende deles. O M0 é a especificação do E9 na amostra P1. A P1g e os pesos da figura vêm do M1,
corrigido pelo 52c, e não são DAP.

Pelo espírito do §1, que fala das "sensibilidades que sustentam a robustez do ciclo 2 (doc 44)", duas coisas pesam
mais que essa lista e não estão no inventário: as robustezes pós-auditoria do conjunto principal (A1) e as variantes
do conjunto de sensibilidade (A2). Não editei o inventário, porque é registro pré-estimativa. As correções de A1 e A2
põem isso nos limites.

**A11. A variação da probabilidade em p.p. quase dobra no VD-1 por causa do conjunto menor (corrigido no texto).**

A variação vai de 0,680 para 0,974 p.p., com a mesma razão de chances. O conjunto corrigido tem menos células por
curso (714 contra 1.015 em 16 conjuntos), e a probabilidade-base de cada célula sobe na mesma proporção, cerca de 1,4.
Não é efeito maior.

**Correção:** frase no bloco do E9 (seção 5.1).

### Sem achado (fidelidade ao adendo)

| Ponto do adendo ou das decisões | Verificação |
|---|---|
| §2: só o ciclo 2 muda, com o quadro de 13/02 | li o xlsx bruto com leitor próprio: 1.547 células, 0 sem número, 714 com vaga imediata. O resultado é igual à `a36_celulas.csv` em 1.547 de 1.547. 301 células passam de reserva (13/02) a imediata (19/03); nenhuma no sentido contrário |
| Decisão 1: conjunto pela regra do script 12 | a regra `tem_vaga_imediata == 1` sobre o conjunto principal reproduz as 2.222 células gravadas. A marca da 1ª opção com o quadro de 19/03 reproduz as 3.646 linhas do ciclo 2. Com o de 13/02: 714 células e 1.140 de 2.140 primeiras opções. É a regra do 12 (`conjunto_escolha`, `tabela_escolhas`) e do 16 (`montar_grupos`: só candidatos com 1ª opção em célula com vaga imediata); não muda o que o adendo fixava |
| Decisão 2: score bootstrap e placebos | `E9_robustez_pos_auditoria.csv`: score bootstrap, CV3 e placebos só no conjunto principal. No de sensibilidade, o doc 42 tem só o CR1 por curso (empilhado), que a decisão não cita; refeito no A2. Não muda a leitura do §3 |
| Decisão 6: tolerância relativa acima de 1 | os CSV de origem têm 10 algarismos significativos, e 1e−8 absoluto em DAP de dezenas ou em Wald de centenas fica abaixo da precisão gravada. A regra relativa é a leitura mínima possível do §4 e não afrouxa nada abaixo de 1. Na minha comparação, a diferença é 0 em todas as 2.865 quantidades |
| Decisão 5: famílias BKY | refiz as duas: 12 membros no P1 e 6 no P1h-3, iguais aos originais. Os q batem nas duas versões |
| Decisões 3, 4, 7, 9 e 10 | seguem os scripts 25 e 42; não mudam amostra, conjunto nem especificação |
| §3: leitura do VD-1 | mesmo sinal e IC corrigido sem 1 → `MANTEM`. Confere |
| Portão VD-5 (28 linhas) | ver abaixo |

**Portão.** Comparei as linhas `antiga_19mar` de `VD_estimativas.csv` com os CSV de origem, com código próprio:
- E9 no conjunto de sensibilidade, ciclo 2 e empilhado: 13 + 13 coeficientes, com os três EP, o IC, o p, o p de
  t(G − 1) e as razões de chances e as variações de probabilidade de `E9_efeitos_marginais.csv`;
- P1: M1, M2, M4, M5 por ciclo, M6 (nota, município e curso), M7, M8, M9 e o Wald do P1d, com coef., EP, IC, p, p de
  MV, Wald e q BKY;
- DAP do M1 (delta e bootstrap), M4, M7 e M5 do ciclo 2;
- D_UF e K5/K10 do P1h, com LI, p unilateral, q e Fieller.

São 2.865 valores, e todos são iguais. As 28 linhas da tabela do portão no 57v estão cobertas. As linhas antigas do
VD também saem do meu código: o VD-1 e o VD-2 antigos, o M4, o M6 e a DAP do M4 batem em todas as casas mostradas.

## Integridade

| Item | Resultado |
|---|---|
| IVS errado | nem o 48 nem a cadeia importada (42, 25c, 25, 16, 19, 17, 12) cita `data/ivs_ipea_2010_municipios.csv`; o IVS vem do a08 |
| `EMPIRICO` | em todas as 674 linhas de `VD_estimativas.csv` e no resumo; estatuto `ADENDO_52D_POS_RESULTADO` em todas; status `EXECUTADO` em todas |
| Imputação | nada imputado. A correção para se faltar célula ou número no quadro de 13/02, e nenhum falta. As 6 linhas sem `estimativa` são de Wald, com o valor em `estatistica_wald` |
| `E9_*`, `P1_*`, `P1h_*`, `VC_*` | `git diff c87ed75 b80e92d` vazio nesses arquivos e em `outcomes/`; os hashes de `entradas` conferem |
| `data/` | nada escrito pelo 48 (os 7 arquivos novos em `data/` no intervalo são do a19, outro commit) |
| Determinismo | reexecutei o 48 inteiro (2.133 s), antes das correções de texto. `VD_estimativas.csv`, `VD_resumo.json`, `VD_antigo_corrigido.png` e o 57v saíram iguais, byte a byte, aos de `b80e92d` (`git status` limpo). Depois das correções, só o 57v muda, regravado com `--atualizar-doc` |
| Testes | `tests/test_sensibilidades_ciclo2_quadro_1302.py` (32) e `tests/test_pipeline_rdd_bolsa.py` (15): 47 passam. O teste do cabeçalho agora espera o link desta auditoria |

## Texto do 57v

- **Linguagem causal.** A origem aparece sempre como preferência revelada, e a bolsa como pacote do corte, condicional
  a se candidatar. O título da figura ("a bolsa continua deslocando a 1ª opção") usa o verbo do doc 44 e vem com a
  nota de rodapé do pacote; não mudei.
- **Números fora dos blocos.** Só datas e o commit do adendo. O teste confere, e continua passando depois das
  correções.
- **Clareza para o autor.** As tabelas lado a lado e a seção 5.7 são claras. As lacunas eram:
  - o que da frase do doc 44 ficou conferido (A1);
  - por que as três "mudanças" da 5.7 não mudam a leitura (A3 a A5);
  - a lista ambígua (A6);
  - o salto da variação em p.p. (A11).

## O que foi recalculado

"Gravado" é o valor de `VD_estimativas.csv`. As diferenças são na escala da saída.

| Item | Recalculado (antiga → corrigida) | Gravado | Diferença máxima |
|---|---|---|---|
| Quadro de 13/02, ciclo 2 | 1.547 células; 714 com vaga imediata; 1.206 vagas | igual | 0 |
| Conjunto só vaga imediata, ciclo 2 | células 1.015 → 714; 1ªs opções com vaga imediata 1.798 → 1.140 de 2.140 | igual | 0 |
| VD-1: coef. da bolsa; EP | 0,133635; 0,032217 → 0,134168; 0,039787 | igual | < 5e−7 |
| VD-1: razão de chances [IC] | 1,950678 [1,422564; 2,674850] → 1,955878 [1,324372; 2,888508] | igual | < 5e−7 |
| VD-1: variação média da prob. (p.p.) | 0,679743 → 0,974039 | igual | < 5e−7 |
| VD-1: log(vagas imediatas + 1) | 0,389 [0,250; 0,528] → 0,674 [0,403; 0,946] | igual | < 5e−4 |
| VD-2: razão de chances [IC]; candidatos | 1,734216 [1,385955; 2,169986] → 1,685389 [1,350807; 2,102843]; 3.365 → 2.707 | igual | < 5e−7 |
| P1: amostra e desenho | 5.421 candidatos, 932.577 linhas, 56 conjuntos | igual | 0 |
| P1 M1 e M5 do ciclo 2 (bolsa) | 0,042396 → 0,045292; 0,106372 → 0,116300 | igual ao `VC_` e ao `P1_` | < 5e−7 |
| VD-3: M4 (bolsa) [IC]; p | 0,075942 [0,028193; 0,123690]; 0,0018 → 0,077814 [0,026118; 0,129510]; 0,0032 | igual | < 5e−7 |
| VD-3: M6 nota, interações (p) | tercil 2: 0,129 → 0,119; tercil 3: 0,328 → 0,330; sem pontuação: 0,0336 → 0,0321; Wald 0,133 → 0,123 | igual | < 5e−7 |
| VD-3: M6 município, interação [IC] | 0,0594 [0,0201; 0,0988] → 0,0537 [0,0098; 0,0976] | igual | < 5e−7 |
| Wald do P1d (χ², 2 gl; p) | 5,690; 0,058 → 5,229; 0,073 | igual | < 5e−7 |
| BKY, família P1 (12) e P1h-3 (6) | os 36 q, nas duas versões (M8 com os p gravados) | igual | 0 |
| VD-4: DAP do capital no M4 [IC delta] | −5,2401 [−10,1071; −0,3730] → −4,5473 [−9,8340; +0,7394] | igual | < 5e−5 |
| Portão VD-5 | 2.865 valores da versão antiga contra `E9_*`, `P1_*`, `P1_dap.csv`, `P1h_magnitudes.csv` | — | 0 |
| Variantes do E9 no conjunto de sensibilidade (A2) | ver A2 | não gravado | — |

Não refiz o M2, o M7, o M8, o M9, o bootstrap da DAP nem os km. Eles saem das mesmas matrizes e foram conferidos só
pelo portão (versão antiga) e pela reexecução.

## O que mudou nesta auditoria

- `scripts/rdd_bolsa/48_sensibilidades_ciclo2_quadro_1302.py`: só texto gerado (A1, A3 a A6, A11: resposta curta,
  bloco do E9, nota da seção 5.7 e limites) e o cabeçalho com o link desta auditoria. Nenhuma conta mudou; decisões e
  inventário intactos.
- `docs/06_execucao/57v_sensibilidades_ciclo2_quadro_1302.md`: regravado com `--atualizar-doc`.
- `tests/test_sensibilidades_ciclo2_quadro_1302.py`: o cabeçalho esperado passa de "pendente" para o link desta
  auditoria.
- `VD_estimativas.csv`, `VD_resumo.json` e a figura: sem mudança.

## O que fica para o autor

1. Decidir se refaz, com o quadro de 13/02, as robustezes pós-auditoria do E9 no conjunto principal: placebos de
   corte, spline cúbico, janelas e cluster por curso (A1). Até lá, a frase "robusto a placebos" do doc 44 se apoia no
   quadro de 19/03.
2. Decidir se as variantes quadrática e de degraus do conjunto só com vaga imediata entram num relato. O degrau de
   0,400 com spline quadrático perde o p < 0,05 (A2).
3. Na próxima execução do 48, acrescentar os hashes dos scripts 12, 17 e 19 e da `rdd_lib` em `entradas` (A7).
