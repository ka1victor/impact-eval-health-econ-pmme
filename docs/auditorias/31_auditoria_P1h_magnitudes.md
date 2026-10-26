# Auditoria independente do P1h (protocolo 52b): peso da bolsa contra o custo do lugar

> **Data:** 26/10/2026.<br>
> **Objeto:** commits `0f810ad` (protocolo) e `963a01a` (execução):
> `scripts/rdd_bolsa/25c_magnitudes_P1h.py`, `output/rdd_bolsa/P1h_magnitudes.csv`, `P1h_resumo.json`,
> `P1h_figuras/P1h_magnitudes.png`, o [doc 57i](../06_execucao/57i_resultados_P1h_magnitudes.md) e
> `tests/test_P1h_magnitudes.py`, contra o [protocolo 52b](../06_execucao/52b_protocolo_P1h_magnitudes.md)
> e o [protocolo 52](../06_execucao/52_protocolo_P1_escolha_dap.md) (§1–§6).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.**
> - Nenhuma estimativa mudou.
> - O M1 e as seis sensibilidades (M2, M4, M5 por ciclo, M7) foram reestimados com código próprio. Os
>   coeficientes e os três EP reproduzem `P1_estimativas.csv` com diferença relativa máxima de 2e-9.
> - D_UF, K5, K10 (delta e Fieller), os pesos da figura e o BKY reproduzem `P1h_magnitudes.csv` com
>   diferença relativa máxima de 2e-8.
> - As correções são de título, rótulo e texto: duas de gravidade média e quatro baixas (seção 5).
>   Foram feitas no script e regeneradas por ele.<br>
> **Proveniência dos números:** lidos de `output/rdd_bolsa/P1_estimativas.csv` e `output/rdd_bolsa/P1h_*`
> depois da correção. A conferência que fica no repositório é `TestRecalculoIndependenteAuditoria31` em
> `tests/test_P1h_magnitudes.py`. Ela roda M1 e M5 ciclo 1 por padrão e as sete especificações com
> `AUDITORIA31_TODAS=1`.

## 1. Ordem dos commits

- `0f810ad` toca três arquivos:
  - o protocolo 52b;
  - o registro de mudanças;
  - o plano da banca 2.
- `963a01a` é o filho direto. Traz o script, as saídas, o doc 57i e os testes. Não altera o protocolo:
  `git diff 0f810ad 963a01a -- docs/06_execucao/52b_protocolo_P1h_magnitudes.md` vem vazio.
- O protocolo declara o estatuto `PROTOCOLO_52B_POS_RESULTADO`. Ele diz que os coeficientes do M1 já
  estavam publicados e que a conta aproximada já tinha sido feita. Não é teste confirmatório, e o doc
  57i diz isso no topo e nos limites.

## 2. Como a auditoria foi feita

O código foi escrito do zero, sem importar os scripts 16, 17, 19, 25 e 25c nem a `rdd_lib`. Ao
contrário da auditoria 26, os leitores de insumo também são próprios.

**Entradas lidas (as do protocolo 52 §2):**
- `escolhas_conjunto_principal.parquet` e `escolhas_candidatos.parquet`;
- o a08 (`a08_ivs_2010_oficial_municipio.csv`). O arquivo local de IVS da auditoria 16 não foi lido;
- `G1_candidatos_origem.parquet`, com a regra `g1_cpf_nome`;
- a CIR do TabNet, lida por expressão regular;
- os centroides do IBGE (JSON);
- distância haversine com raio de 6.371,0088 km.

**Montagem:**
- Bolsa: Faixa 3 = 10, Faixa 2 = 15, Faixa 1 = 20, conferida contra a regra de dois cortes do IVS.
- Spline linear do IVS por 0,1, com nós em 0,300 e 0,400.
- Base de macrorregião: Sudeste. Base de estrato: `interior_proximo_polo`.
- No M4, efeito fixo de UF da vaga, com base na UF mais frequente.
- No M7, o 2º posto no mesmo curso exclui a célula da 1ª opção.

**Estimação:**
- Logit condicional por Newton, com verossimilhança, escore e informação próprios (somas por grupo com
  `bincount`).
- EP sanduíche: `H⁻¹ (Σ_g s_g s_g') H⁻¹ × G/(G−1)`, com cluster por conjunto (curso × ciclo) e por
  candidato.
- Fieller resolvido como a quadrática de `(100·passo·β + K·γ)² ≤ z²·Var(100·passo·β + K·γ)`. O limite
  unilateral sai do conjunto de 90%.
- BKY pelo algoritmo de Anderson (2008), escrito de novo.

**Amostra reconstruída:** igual à do P1.
- 5.714 candidatos de 1ª opção, dos quais 5.421 ficam na amostra P1.
- 1 célula sem IVS oficial.
- 932.577 linhas no M1 e 1.630.577 no M7.
- G = 56 conjuntos no empilhado; no M5, G = 16, 16 e 24 por ciclo.
- As distâncias das células escolhidas são iguais às do G1 (diferença máxima de 0 km).

## 3. Recálculo

### 3.1 Reprodução do P1 (portão do §2)

Diferenças contra `P1_estimativas.csv`, em todos os termos de cada especificação. A coluna "EP" traz o
maior desvio relativo entre os três EP.

| Especificação | Termos | Linhas | Dif. máx. coef. (absoluta) | Dif. máx. EP (relativa) | Log-verossimilhança |
|---|---:|---:|---|---|---|
| M1 | 18 | 932.577 | 2,9e-10 | 3,5e-10 | −13.658,16 (igual) |
| M2 | 18 | 932.577 | 2,6e-9 | 8,8e-10 | −12.777,11 (igual) |
| M4 | 40 | 932.577 | 5,0e-10 | 3,6e-10 | −13.499,09 (igual) |
| M5 ciclo 1 | 18 | 80.522 | 4,6e-10 | 3,0e-10 | −2.027,54 (igual) |
| M5 ciclo 2 | 18 | 380.022 | 2,4e-9 | 1,5e-9 | −4.987,33 (igual) |
| M5 ciclo 3 | 18 | 472.033 | 2,8e-10 | 4,1e-10 | −6.485,99 (igual) |
| M7 | 18 | 1.630.577 | 4,8e-10 | 2,8e-10 | −24.714,12 (igual) |

As diferenças de 2e-9 no M2 e no M5 ciclo 2 vêm do critério de parada do meu Newton. O portão do
próprio script (1e-8 contra o CSV com 10 algarismos significativos) também passou, e eu o reproduzi.

**Convenção do cluster.** O EP gravado é o CR1 com fator G/(G−1) e sem (N−1)/(N−K):
- com G/(G−1), a diferença relativa é de 3e-10;
- sem fator nenhum, os EP ficariam 0,9% menores no empilhado (G = 56) e 2,1% a 3,2% menores no M5
  (G = 24 e 16);
- com o fator completo, à moda do Stata, G/(G−1)·(N−1)/(N−K), a diferença seria de 0,1% a 0,9%.

Não há diferença de convenção a explicar: o script usa G/(G−1), como o E9 e o P1.

### 3.2 Linhas do P1h

| Linha | Modelo | Recálculo | Gravado (CSV) | Dif. rel. máx. |
|---|---|---|---|---|
| P1h-1: D_UF = θ_UF − 10·β | M1 | 1,97842; EP 0,21330; IC [1,5604; 2,3965]; LI 1,6276; p = 8,86e-21 | idem | 3e-10 |
| P1h-2a: K5 (delta) | M1 | 111,98 km; EP 61,756; IC [−9,06; 233,02]; LI 10,40; p = 0,03490 | idem | 2e-10 |
| P1h-2a: K5 (Fieller) | M1 | IC [−6,93; 237,14]; LI (90%) 12,01; conjunto limitado | idem | 2e-10 |
| P1h-2b: K10 (delta) | M1 | 223,96 km; EP 123,51; IC [−18,12; 466,04]; LI 20,80; p = 0,03490 | idem | 2e-10 |
| P1h-2b: K10 (Fieller) | M1 | IC [−13,85; 474,29]; LI 24,01 | idem | 2e-10 |
| P1h-3: D_UF | M2 | 1,17627; EP 0,18693; p = 1,56e-10; q BKY 0,001 | idem | 2e-8 (p) |
| P1h-3: D_UF | M4 | 1,73234; EP 0,22943; p = 2,17e-14; q 0,001 | idem | 3e-10 |
| P1h-3: D_UF | M5 ciclo 1 | 2,34302; EP 0,45723; p = 1,49e-7; q 0,001 | idem | 3e-10 |
| P1h-3: D_UF | M5 ciclo 2 | 1,31025; EP 0,27908; p = 1,33e-6; q 0,001 | idem | 5e-10 |
| P1h-3: D_UF | M5 ciclo 3 | 2,37251; EP 0,31764; p = 4,04e-14; q 0,001 | idem | 2e-10 |
| P1h-3: D_UF | M7 | 2,06716; EP 0,22149; p = 5,15e-21; q 0,001 | idem | 2e-10 |
| FIG: 5β; 10β | M1 | 0,21198 [−0,0132; 0,4372]; 0,42396 [−0,0265; 0,8744] | idem | 3e-10 |
| FIG: −γ | M1 | 0,18930 [0,1657; 0,2129] | idem | 3e-10 |
| FIG: θ_UF | M1 | 2,40238 [2,278; 2,527] | idem | 7e-11 |
| FIG: θ_UF + θ_reg | M1 | 4,04759 [3,665; 4,430] | idem | 2e-10 |
| FIG: θ_UF + θ_reg + θ_mun | M1 | 4,83503 [4,553; 5,117] | idem | 3e-10 |

Também foram conferidos, com a mesma diferença:
- o EP de MV;
- o EP por candidato;
- o p unilateral pela t com G − 1 graus de liberdade.

A diferença de 2e-8 no p do M2 é relativa, num p de 1,6e-10, e vem do coeficiente do M2 (2,6e-9).

**β do M1.**
- β = 0,042396, com EP 0,022983 e IC [−0,00265; 0,08744].
- p bilateral = 0,0651. É o P1a do protocolo 52 e bate com o `beta_M1` do resumo.

## 4. Fidelidade ao protocolo 52b

| Regra | Situação |
|---|---|
| §1: comparação de pesos na utilidade, não de efeitos causais do lugar | ok, no §1 do doc, na leitura, na figura e nos limites |
| §2: M1 exatamente como no P1 (amostra, conjunto, covariáveis) | ok; reproduzido do zero (3.1) |
| §2: portão ≤ 1e-8 nos coeficientes e nos EP com cluster por conjunto; para se falhar | ok; passou nas 7 especificações |
| §2: EP de MV e por candidato relatados | ok |
| §3: P1h-1 primária, unilateral a 5%, Holm numa família de um teste | ok: p de Holm = p = 8,9e-21; rejeita |
| §3: K5 e K10 com IC delta e Fieller | ok; os dois conjuntos de Fieller são limitados (γ bem determinado) |
| §3: P1h-3 em M2, M4, M5 por ciclo e M7, cada um com portão; BKY entre essas linhas | ok; 6 linhas e q de 0,001 em todas |
| §3: cada linha com estimativa, EP, IC bilateral, LI unilateral e p unilateral | ok, inclusive nas linhas de km |
| §3: DAP em R$, M8 e M3 fora | ok |
| §4: leitura pré-registrada, se rejeitar | ok; o texto do doc reproduz as três frases do §4 (e o teste confere) |
| §4: km com IC em todos os casos; IC de β com zero, então IC de K com zero, "dito assim" | ok ("o IC de K5 e o de K10 também contêm zero") |
| §5: saídas, doc gerado entre marcadores, testes com caso sintético rotulado | ok |
| §6: integridade | ok (seção 7) |

### 4.1 As quatro decisões de implementação do doc 57i

| # | Decisão | Muda resultado? | Excede o protocolo? |
|---|---|---|---|
| 1 | Pesos da figura no CSV com `id_linha = FIG`, sem teste | Não: são combinações do mesmo θ e V. O 5β tem p unilateral 0,033 no CSV, mas a coluna `rejeita_h0_5pct` fica vazia e o doc não o relata como teste | Não: é exigência da regra de proveniência (figura lida de `output/`) |
| 2 | p unilateral de K pelo delta | Não: nenhuma decisão depende dele. O p equivalente pelo Fieller é o p unilateral de β, 0,0325 (metade do 0,065 do P1a). O delta dá 0,0349, um pouco mais conservador | Não: o §3 pede p unilateral em toda linha e não fixa o método |
| 3 | Portão em todos os termos das 7 especificações; qualquer falha para tudo | Não: passou | É mais estrito que o texto (o §2 só manda parar no M1), mas na direção segura |
| 4 | q BKY < 0,05 marca "rejeita" nas sensibilidades, como leitura de robustez | Não: a única decisão é a do P1h-1 | Não: o §3 não fixa o nível; 5% é o da primária |

O doc dizia que as decisões foram "tomadas antes de ver os números do P1h". Elas estão no mesmo commit
dos números, e o Git não permite verificar isso. O texto foi trocado (correção B2).

## 5. Achados e correções

| # | Gravidade | Achado | Correção |
|---|---|---|---|
| A1 | média | O título da figura, "Na escolha da vaga, ficar na UF de origem pesa mais que toda a amplitude da bolsa", tem dois problemas: não diz "no modelo" e tem como sujeito implícito o médico ("ficar"). Lido num slide, soa como comportamento ou efeito do lugar. A leitura pré-registrada fala do modelo de escolha e da vaga | Título regerado: "No modelo de escolha, a vaga estar na UF de origem pesa mais que toda a amplitude da bolsa (R$ 10 → 20 mil)". O ramo "não rejeita" também ganhou "No modelo de escolha" |
| A2 | média | Os rótulos "Vaga na mesma UF da origem", "na mesma região de saúde" e "no mesmo município" são ambíguos. θ_UF é o peso de uma vaga na UF de origem **fora** da região de saúde de origem, contra outra UF à mesma distância: é a menor das três categorias de lugar. O D_UF compara a bolsa com essa categoria. Quem lê "mesma UF" como "qualquer vaga na UF" pode achar que 2,40 já inclui os casos de mesma região (4,05) | Rótulos regerados: "Mesma UF, outra região de saúde", "Mesma região de saúde, outro município" e "Mesmo município da origem" (figura, tabela de pesos do doc e coluna `estimando` das linhas FIG do CSV). O "Como ler" diz a base (outra UF, à mesma distância) e que cada linha é uma categoria. A notação do §1 do doc ganhou uma frase com o sentido exato de θ_UF |
| B1 | baixa | "No ciclo em que β é perto de zero" está no singular, mas são dois: ciclo 1 (β = 0,013) e ciclo 3 (β = −0,0004), em `P1_estimativas.csv` | "nos ciclos em que β é perto de zero" |
| B2 | baixa | A frase "decisões ... tomadas antes de ver os números do P1h" não é verificável (mesmo commit) | Texto novo: as decisões estão no mesmo commit dos números, e o Git não mostra a ordem; nenhuma muda estimativa, EP, IC ou a decisão do P1h-1 |
| B3 | baixa | Na tabela, "q BKY = 0,001" nas seis sensibilidades é o piso da grade do algoritmo de Anderson, não um valor exato | Legenda da tabela: "q BKY = 0,001 é o piso da grade do algoritmo (Anderson, 2008), não um valor exato" |
| B4 | baixa | O "Como ler" dizia que comparar a distância de cada ponto ao zero é comparar quanto cada atributo move a escolha. Isso vale para os atributos binários e para os degraus da bolsa, mas o peso da distância depende da unidade escolhida (100 km) | Frase retirada; o "Como ler" diz que o peso da distância depende da unidade |

**Hashes depois da correção:**
- PNG: `12eafcc0…` → `61bcc1b8…`.
- CSV: `dfa77c88…` → `934d3931…`. Só mudou a coluna `estimando` de três linhas FIG; nenhum número mudou.
- `P1h_resumo.json` mudou só no título, no "Como ler" e nos hashes das saídas.
- As covariâncias gravadas não mudaram.

**Mudanças no código e nos testes:**
- Script 25c: só textos (`PESOS_FIGURA`, `COMO_LER`, `titulo_figura`, `texto_leitura`, `texto_tabela`,
  `texto_desvios` e a notação em `gerar_doc`).
- Teste: acréscimo da classe da auditoria.

**Observações sem correção:**
- O §1 do doc diz que β "mede o pacote do corte (...) e o incentivo marginal". É a formulação do doc 57a,
  já auditada (auditoria 26), e vem junto do pacote. Mantida.
- O "Como ler" fica no doc e no resumo, não dentro do PNG. É a convenção das figuras do P1 e da
  realocação (auditoria 28, §5). A figura tem rodapé com a ressalva de linguagem.
- O script 25c importa o script 25. O protocolo 52b §5 permite isso ("reusa as funções do script 25").
  Por isso a reprodução independente desta auditoria não reaproveita nada dele.

## 6. Linguagem

| Ponto | Situação |
|---|---|
| θ não pode ser lido como efeito causal da geografia | ok: "preferência revelada condicional ao modelo", "não é efeito causal da geografia nem de mudar alguém de lugar" (§1), rodapé da figura, "Como ler" e limites. Com A1 e A2, o título e os rótulos deixaram de convidar a essa leitura |
| Nada diz que a bolsa "funciona" ou "não funciona" | ok: a frase aparece só como negação ("Nada aqui diz se..."), e o teste a confere |
| Limite unilateral positivo de K5 (p = 0,035) não substitui o teste bilateral do P1a (p = 0,065) | ok, ver abaixo |

**Os limites unilaterais de K5 e K10.**
- O doc relata, porque o §3 do 52b exige, o LI unilateral de 95% (10 km pelo delta, 12 km pelo Fieller) e
  o p de 0,035.
- Na mesma frase, diz que "essas linhas são descritivas: o P1a foi pré-registrado como teste bilateral de β
  (protocolo 52, Holm; p = 0,065), e o lado unilateral das linhas de km não o substitui".
- Antes disso, diz que "os dados não descartam que a bolsa não valha nenhum km".
- Na tabela, a coluna "Rejeita H0 a 5%" fica "—" nas linhas de km.
- A figura não mostra K5, K10 nem p.
- O resumo JSON não traz nenhuma marca de rejeição para K.

Não há venda do lado unilateral.

## 7. Integridade

- `data/`: `git diff --stat 98edb96 963a01a -- data/` vem vazio, e esta auditoria não escreve em `data/`.
- **Arquivo de IVS errado.** `ivs_ipea_2010_municipios` não aparece nos scripts 25c, 25, 16, 17 e 19 nem na
  `rdd_lib` (grep). O resumo não o lista entre as entradas, e o IVS vem do a08.
- **Saídas do P1.** `git diff --stat 45a8636 HEAD` em `P1_estimativas.csv`, `P1_dap.csv`, `P1_resumo.json`
  e `P1_figuras/` vem vazio; a última mudança nesses arquivos é a auditoria 26. Depois da nova execução do
  25c nesta auditoria, `git status` não mostra `P1_*`. Os hashes de `P1_resumo.json["saidas"]` batem
  (teste).
- **Hashes de proveniência.** Os de `P1h_resumo.json["entradas"]` (14 entradas, protocolo incluído) e
  `["saidas"]` batem com os arquivos.
- **Dado pessoal.** `P1h_magnitudes.csv` e `P1h_resumo.json` não têm `id_candidato`, nome, CPF nem CRM. A
  varredura por pseudônimo (`c[123]_\d{5}`) vem vazia. As sequências de 11 dígitos encontradas são casas
  decimais de p.
- **CNES.** Nenhum mês é lido.
- **A6.** `scripts/tema_trabalho/07_red_team_sintese.py` foi reexecutado e regravou o manifesto byte a byte
  igual ao commitado.
- **Rótulo.** `natureza_dos_dados = EMPIRICO` em toda linha e no resumo.

## 8. Testes

Cada execução foi gravada em log, e o código de saída foi conferido. A suíte inteira e o `run_all.py` não
foram rodados.

| Comando | Resultado | Código de saída |
|---|---|---|
| `pytest tests/test_P1h_magnitudes.py` (antes das correções) | 28 passam | 0 |
| `pytest tests/test_integridade_dados.py` | 4 passam | 0 |
| `pytest tests/test_escolha_dap.py` (P1) | 36 passam | 0 |
| `AUDITORIA31_TODAS=1 pytest tests/test_P1h_magnitudes.py` (depois das correções; 7 especificações) | 31 passam (3,5 min) | 0 |
| `pytest tests/test_P1h_magnitudes.py` (padrão: M1 e M5 ciclo 1) | 31 passam | 0 |
| `pytest tests/test_integridade_dados.py tests/test_escolha_dap.py tests/test_pipeline_rdd_bolsa.py` | 55 passam | 0 |

A classe `TestRecalculoIndependenteAuditoria31` tem três testes:
- coeficientes e EP contra o P1;
- D_UF, pesos da figura e BKY;
- K5 e K10 pelo delta e por Fieller, com a coerência entre o IC de β e o de K e o P1a bilateral acima de
  0,05.
