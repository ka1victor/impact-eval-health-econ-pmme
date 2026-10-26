# 59. Protocolo P3/P4: sensibilidade de Rambachan–Roth e grupo de comparação alternativo

> **Data de congelamento:** 25/10/2026, antes de calcular qualquer estimativa nova
> (nenhum coeficiente HonestDiD, nenhum ATT com o grupo alternativo, nenhum
> pré-teste com o grupo alternativo).<br>
> **Origem:** doc 57, §6, linhas "P3 e P4 com pré-tendências falhando" e "P3 e
> P4: outro grupo de comparação". Pedido da tarefa de 25/10/2026.<br>
> **Estatuto:** `PROTOCOLO_59_POS_RESULTADO`. Já vistos: doc 57c (P3, adendo §12
> do protocolo 47), doc 57d (P4, protocolo 54), doc 57f (P6) e doc 57e (P5).
> Nada aqui muda estimativa, Holm ou BKY já gravados. Toda saída leva
> `natureza_dos_dados = EMPIRICO`.<br>
> **Scripts:** `scripts/rdd_bolsa/34_sensibilidade_honestdid.py` (parte A) e
> `35_comparacao_alternativa_P3P4.py` (parte B).<br>
> **Saídas:** `output/rdd_bolsa/H_*` e `output/rdd_bolsa/CA_*`.<br>
> **Resultados:** `docs/06_execucao/57h_resultados_P3P4_sensibilidade.md`.<br>
> **Testes:** `tests/test_honestdid.py` e
> `tests/test_comparacao_alternativa_P3P4.py`.

## 1. Por que e o que não muda

Nos estudos de evento do P3 (12.2, 12.5 e K2 do D2) e do P4 (T4.1b), o teste
conjunto dos pré rejeita zero em parte dos outcomes. A leitura ficou
associativa. Este protocolo faz duas coisas, nas duas fixadas antes de
estimar:

- **A. Sensibilidade (Rambachan e Roth, 2023).** Quanto da diferença do pós
  aguenta violações de tendências paralelas do tamanho das vistas no pré.
  Rótulo `SENSIBILIDADE`. Não muda estimativa pontual; não cria identificação.
- **B. Comparação alternativa.** Outro grupo de controle, escolhido pelo
  desenho (priorização e nota de corte), não pelo resultado.

Escolher grupo ou janela depois de ver o pré seria seleção retrospectiva. Por
isso a regra de cada grupo, a janela, o estimador e a leitura ficam fixados
aqui, e a viabilidade foi conferida só com variáveis de desenho e pré-tratamento
(§5).

## 2. Parte A: sensibilidade de Rambachan–Roth

### 2.1 Estudos de evento cobertos (lista fechada)

| Id | Origem | Outcome | Pré usado | Pós | Leitura principal |
|---|---|---|---|---|---|
| H-P3-K_esp | 57c, 12.2, todos os cursos | produção típica da especialidade no par município × curso | e = −12..−2 | e = 0..9 | **principal do P3** |
| H-P3-K2r | 57c, 12.4, D2 | internações cirúrgicas de residentes | −12..−2 | 0..9 | secundária |
| H-P3-K2r_tot | 57c, 12.4, D2 | todas as internações de residentes | −12..−2 | 0..9 | secundária |
| H-P3-K1_reg | 57c, 12.5, D2 | K1 nos outros municípios da região | −12..−2 | 0..9 | secundária |
| H-P3-K2_reg | 57c, 12.5, D2 | K2 nos outros municípios da região | −12..−2 | 0..9 | secundária |
| H-P4-* | 57d, T4.1b, regra D1, janela principal | os 14 outcomes do §2 do protocolo 54 | e = −6..−2 | e = 0..6 | **principais do P4:** horas totais, horas no município do posto, horas fora do município do posto; as outras 11, secundárias |
| H-CA-* | parte B deste protocolo | as 4 primárias do §4 | ver §3 e §4 | ver §3 e §4 | secundária |

Regra da lista: as linhas D2 do BKY do adendo §12 (P3) e a família do BKY do
T4.1b (P4). Entram todas, com ou sem rejeição no pré. A janela do pré do P3 é
curta (−12..−2, não −24..−2) por custo: o conjunto de magnitude relativa é
uma união de 2 × (nº de diferenças do pré) poliedros. A janela de 12 meses é a
mesma que o doc 50 usa para o θ médio do pré. Se algum θ(e) do pré faltar, usa-se
o bloco contíguo mais próximo de e = −1.

### 2.2 Coeficientes e covariância

- θ(e) e as funções de influência são **recalculados** com as funções dos
  scripts 22, 27 e 28, deterministicamente. As saídas versionadas não guardam a
  covariância.
- Antes de usar, o script confere que os θ(e) recalculados batem com
  `K_X_estudo_evento.csv` e `P4_estimativas.csv` (diferença máxima ≤ 1e−8);
  se não baterem, para sem gravar.
- Σ = covariância analítica das funções de influência (V = IF′IF/N², com
  cluster no município no P3 e no médico no P4). É a mesma do Wald do pré já
  relatado. O EP bootstrap dos docs 57c e 57d não entra.

### 2.3 Restrições e alvos

Notação de Rambachan e Roth (2023): β = τ + δ; δ(−1) = 0; δ_pré = β_pré.

| Restrição | Definição | Grade |
|---|---|---|
| Magnitude relativa, Δ^RM(M̄) | toda variação de δ entre meses consecutivos do pós (inclusive de −1 a 0) ≤ M̄ × a maior variação entre meses consecutivos do pré, em valor absoluto | M̄ ∈ {0; 0,25; 0,5; 0,75; 1; 1,5; 2} |
| Suavidade, Δ^SD(M) | toda segunda diferença de δ (pré, referência e pós) ≤ M em valor absoluto | M = k × u, k ∈ {0; 0,05; 0,1; 0,25; 0,5; 1}, u = EP analítico de θ(0) |

Alvos: (a) **média de θ(e) no pós** (principal); (b) θ(0).

### 2.4 Inferência e implementação

Não há R nem o pacote `HonestDiD` no ambiente. A implementação é própria, em
numpy e scipy (`linprog`/HiGHS e `minimize`), no módulo
`scripts/rdd_bolsa/honestdid_lib.py`:

- **Δ^SD: FLCI** (intervalo de comprimento fixo; Armstrong e Kolesár, 2018;
  Rambachan e Roth, 2023, seção 4). Estimador afim v′β̂ com v_pós = l. O viés
  máximo em Δ^SD(M) é M × min‖w‖₁ com D′w = v (dual do PL; D = matriz das
  segundas diferenças). O meio-comprimento é σ_v × cv_α(viés/σ_v), cv_α(b) =
  quantil 1 − α de |N(b, 1)|. v é escolhido para minimizar o meio-comprimento
  (PQ em w para cada ‖w‖₁ e busca unidimensional).
- **Δ^RM: teste condicional de Andrews, Roth e Pakes (ARP)**, aplicado a cada
  poliedro da união (diferença do pré s e sinal ±). O IC é o conjunto de θ̄ não
  rejeitado em pelo menos um poliedro; relata-se o envelope [mín, máx]. A
  truncagem condicional (v_lo, v_up) sai de dois PL lineares-fracionários
  (transformação de Charnes–Cooper). Usa-se o teste condicional puro, não o
  híbrido C-LF do pacote; isso está declarado no resultado.
- **Conjunto identificado** em β̂ (PL), por restrição e M̄/M; "vazio" quando o
  pré estimado já viola a restrição.
- α = 0,05.
- **Ponto de ruptura:** o maior M̄ (Δ^RM) e o maior M (Δ^SD, também em
  múltiplos de u) com IC que exclui zero. Busca por bisseção em [0; 4] (M̄) e
  [0; 4u] (M), tolerância 0,01 e 0,01u. Zero quando o IC já inclui zero em
  M̄ = 0 ou M = 0. Referência descritiva: a maior |segunda diferença| de β̂_pré,
  em múltiplos de u.
- **Validação:** `tests/test_honestdid.py` confere a implementação em casos
  sintéticos que se resolvem à mão (um pré e um pós: conjunto identificado de
  Δ^RM = β_pós ± M̄|β_pré|; Δ^SD com M = 0 extrapola a reta; FLCI com M = 0
  igual a v′β̂ ± 1,96 σ_v; teste condicional com uma desigualdade igual ao teste
  z unilateral; com uma igualdade, igual ao bilateral) e por Monte Carlo
  pequeno (cobertura ≥ 0,93 com 400 réplicas). Os casos sintéticos ficam só no
  teste, rotulados como sintéticos, nunca em `output/`.

### 2.5 Leitura

- "Robusto até M̄ = x": o IC exclui zero enquanto a variação do pós entre meses
  consecutivos não passa de x vezes a maior vista no pré.
- M̄ = 1 é a referência de Rambachan e Roth: violações do pós do mesmo tamanho
  das do pré. Ruptura < 1 = conclusão frágil.
- A sensibilidade não transforma associação em efeito. Uma ruptura alta diz só
  que a diferença não se explica por uma tendência do tamanho da vista no pré;
  continua ATT sob a hipótese restrita, sem fonte de exogeneidade.

## 3. Parte B, P3: chegada contra células pedidas e não priorizadas (P3-CA)

### 3.1 Desenho

| Item | Definição |
|---|---|
| Estimando | ATT da chegada do 1º especialista do PMM-E no par município × curso sobre a produção típica do curso (K_esp do 12.2), em relação a pares que pediram o curso e não foram priorizados |
| Tratados | pares do 12.2 (célula do curso nos ciclos 1–2, em U) com 1ª chegada até 202605 |
| Controles (principal) | pares município × curso em U com linha na adesão do ciclo 3 (resultado final, P5) para o curso, **nenhuma** linha priorizada do curso no município, e nenhuma chegada da lista nominal no par, em qualquer data |
| Fora | pares tratados com 1ª chegada depois de 202605; pares sem nenhum dos dois status |
| Cursos | os 8 ESPECÍFICO do G4; entram só os que têm ≥ 1 tratado e ≥ 2 controles com a regra principal (pela contagem do §5: 10, 11, 12, 13 e 14; 7, 15 e 16 ficam fora e são contados) |
| Janela | 202201–202605; e = −24..+9; coorte = trimestre da chegada; base universal g − 1 |
| Estimador | Callaway–Sant'Anna como no 12.2 (`att_gt_geral`), controles só do mesmo curso, **só o grupo alternativo como controle** (`controles = "nunca"`), agregação por e com peso = pares tratados |
| Inferência | cluster no município; bootstrap multiplicador de Mammen, B = 9.999, semente 20261019; EP = IQR/(z₀,₇₅ − z₀,₂₅); IC 95% normal |
| Primária | média de θ(0..9) de K_esp, todos os cursos que entram |
| Secundárias | (S1) controles = todos os pares pedidos no ciclo 3 sem chegada, priorizados ou não (os 8 cursos); (S2) por curso, regra principal |
| Pré-tendência | Wald conjunto de θ(e) = 0, e = −24..−2, covariância analítica com cluster (regra do doc 50); passa se p ≥ 0,05. Ressalva do doc 50 também relatada (θ médio do pré de mesmo sinal ou oposto e ≥ metade do ATT) |
| MDE | 2,8 × EP, relatado ex post. Ex ante não há variância do outcome no grupo alternativo sem abri-lo; ordem de grandeza: MDE por curso do 12.2 (6,4 a 52,4) |

### 3.2 O que identifica

- A diferença entre pares que receberam o especialista e pares cuja demanda
  (pedido do gestor no ciclo 3) não foi priorizada pela SGTES, sob tendências
  paralelas entre os dois grupos. É **priorização entre quem pediu**, não
  efeito da participação no PMM-E nem da bolsa.
- O pedido e a priorização do ciclo 3 são de 2026; a série termina em 202605,
  antes do início do ciclo 3 (202608). Nenhum outcome do ciclo 3 é lido. O
  ciclo 3 continua prospectivo.
- A priorização não é sorteio: o P5 mostra associação com macrorregião e
  escassez regional (doc 57e). O pré-teste é o diagnóstico; sem ele, a leitura
  é associativa.
- Controles do 12.2 e do P3-CA se sobrepõem (pares com célula vazia nos ciclos
  1–2 que pediram de novo no ciclo 3).

## 4. Parte B, P4: alocado contra não alocado perto da nota de corte (P4-CA)

### 4.1 Desenho

| Item | Definição |
|---|---|
| Estimando | efeito de ser alocado na 1ª opção sobre a trajetória **cadastrada** do candidato no CNES, em diferenças (mês do evento − mês de referência), para candidatos perto da nota de corte |
| População | universo do P6 (`P6_amostra.parquet`): ciclos 1 e 2, 1ª chamada, ampla concorrência, 1ª opção em célula elegível, ligado ao CNES pela regra principal do G1 |
| Amostra principal | r ∈ {−2, −1, +1, +2}, só células com os dois lados (a do R1 do P6) |
| Tratamento | D = alocado na 1ª opção (`d_alocado_1a_opcao`) |
| Tempo | candidato × mês, 202406–202608; e = mês − t₀; t₀ = 1º mês de início da lista nominal no ciclo (202509 no ciclo 1, 202603 no ciclo 2); referência e = −1 |
| Janela | e = −12..+5 |
| Estimador | para cada e: MQO de ΔY = Y(t₀+e) − Y(t₀−1) em D com efeito fixo de célula (centragem na célula; o R1 do P6 aplicado à variação) |
| Inferência | IC 95% com EP agrupado por célula (funções de influência somadas por célula, fator G/(G − 1)); p da primária por permutação de D dentro da célula (999, semente 20261019), como no R1 |
| Primárias (3) | média de θ(0..5) de: horas totais; horas no município da 1ª opção; horas fora do município da 1ª opção (horas semanais cadastradas) |
| Secundárias | (a) outcomes, amostra principal: horas SUS, número de municípios com vínculo, tem vínculo no município da 1ª opção (quase mecânico), número de vínculos; BKY entre essas 4; (b) amostra r ∈ [−4, +5] sem 0; (c) com os empatados (r = 0), indicador de empate como covariável; (d) ligação só por nome |
| Pré-tendência | Wald conjunto de θ(e) = 0, e = −12..−2, com a covariância agrupada; p por permutação do Wald dentro da célula (999, mesma semente); passa se p ≥ 0,05; p qui-quadrado também relatado |
| MDE ex ante | sem outcome: 2,8 × DP das horas pré (202406–202506, `cov_horas_pre`) × √(1/30 + 1/68) ≈ 18,8 h/sem em nível; a variação tem DP menor, então é cota superior; ex post, 2,8 × EP |

### 4.2 O que identifica

- O efeito de **ser alocado perto do corte**, entre candidatos que se
  inscreveram, sob tendências paralelas locais (desempate por regra fixa, nota
  inteira; principal sem empatados). Não é o efeito da bolsa (a mesma para os
  alocados da célula) nem do PMM-E sobre o município.
- Em relação ao P4 (coortes de entrada), troca a hipótese de tendências
  paralelas entre médicos que entram em meses diferentes pela de tendências
  paralelas entre quem passou e quem não passou por 1 ou 2 pontos.
- Horas no município da 1ª opção: para o alocado é o município do posto; para o
  não alocado é o município que ele pediu. Vínculo cadastrado não é presença.
- Desequilíbrios já vistos no P6 (distância origem–vaga, taxa de ligação) valem
  aqui. Só os ligados têm outcome.

### 4.3 Viabilidade e cache

O painel mensal dos candidatos não está versionado (só os agregados do P6).
O script 35 o refaz em memória a partir do cache privado do a16 e do
dicionário do G1, com as funções do script 30 e as mesmas conferências (o
cache reproduz o a16 e o G1 versionados; se não reproduzir, para). Cache só em
`output/aquisicao/cnes_profissional/cache_privado/` e
`output/rdd_bolsa/G1_cache/` (no `.gitignore`). Nada com código do
profissional, nome, CPF, CNS ou CRM sai do cache; as saídas `CA_*` têm só
estatísticas por e e por grupo. Se o cache não puder ser refeito (fonte fora do
ar ou SHA-256 diferente do manifesto do a16), o P4-CA fica `NAO_EXECUTADO` com o
motivo; o P3-CA e a parte A não dependem dele.

## 5. Conferência de viabilidade feita antes do congelamento (só desenho)

Contagens com a adesão do ciclo 3, as células dos ciclos 1–2, a lista nominal
(só município, curso e data de início) e `P6_amostra.parquet` (r, D, célula,
ligação, horas pré). Nenhum outcome pós e nenhuma série por grupo alternativo.

| Item | Valor |
|---|---|
| P3-CA: pares pedidos no ciclo 3 (8 cursos) | 1.238 (396 com alguma célula priorizada; 842 sem) |
| P3-CA: pedidos, não priorizados e sem chegada (controles principais, antes do filtro U) | 761 em 579 municípios: curso 10: 112; 11: 99; 12: 31; 13: 14; 14: 505; 7, 15, 16: 0 |
| P3-CA: pedidos e priorizados sem chegada (entram só em S1) | 359 |
| P3-CA: tratados do 12.2 nos cursos 10–14 | 178 (15 + 64 + 15 + 8 + 76) |
| P4-CA principal: células com os dois lados; acima / abaixo | 27; 30 / 68 (96 do ciclo 2, 2 do ciclo 1) |
| P4-CA S(b): r ≠ 0 | 30 células; 36 / 93 |
| P4-CA S(c): com empatados | 46 células; 108 / 162 |
| t₀ (1º início na lista nominal) | ciclo 1: 202509 (274 inícios); ciclo 2: 202603 (309) |

## 6. Multiplicidade e leitura

- **Holm** na família das 4 primárias da parte B: P3-CA (K_esp) e as 3 do
  P4-CA. Nível 5%.
- BKY só nas secundárias de outcome do P4-CA (§4.1 a). Demais secundárias sem
  correção, rotuladas.
- A parte A não entra em teste múltiplo.
- Uma primária só é lida como "diferença que não se explica pelo pré" se: Holm
  < 0,05, pré passa e ruptura de Δ^RM ≥ 1. Mesmo assim, a linguagem é a do §3.2
  ou do §4.2. Em qualquer outro caso, "associação" ou "não se distingue de
  zero", com o MDE.
- Todas as linhas são relatadas, qualquer que seja o resultado.

## 7. Saídas

| Item | Onde |
|---|---|
| biblioteca | `scripts/rdd_bolsa/honestdid_lib.py` |
| parte A | `scripts/rdd_bolsa/34_sensibilidade_honestdid.py` → `H_estimativas.csv`, `H_coeficientes.csv` (θ(e) e Σ por linha), `H_resumo.json`, `H_figuras/` |
| parte B | `scripts/rdd_bolsa/35_comparacao_alternativa_P3P4.py` → `CA_estimativas.csv`, `CA_estudo_evento.csv`, `CA_resumo.json`, `CA_figuras/` |
| resultados | `docs/06_execucao/57h_resultados_P3P4_sensibilidade.md` |

## 8. Integridade

- Nada imputado; ausente não vira zero (regras do a16, do P6 e do 12.2).
- Nenhum CNES ≥ 202609; SIA e SIH até 202605.
- O arquivo local de IVS não é lido; o universo U vem do a08 oficial.
- Sem nome, CPF, CNS, CRM ou `id_prof` em `output/`.
- Desvios: adendo datado no fim deste documento e no doc de resultados.

## Referências

- Rambachan, A.; Roth, J. (2023). A more credible approach to parallel trends.
  *Review of Economic Studies*, 90(5), 2555–2591.
- Andrews, I.; Roth, J.; Pakes, A. (2023). Inference for linear conditional
  moment inequalities. *Review of Economic Studies*, 90(6), 2763–2791.
- Armstrong, T.; Kolesár, M. (2018). Optimal inference in a class of
  regression models. *Econometrica*, 86(2), 655–683.
- Callaway, B.; Sant'Anna, P. (2021). Difference-in-differences with multiple
  time periods. *Journal of Econometrics*, 225(2), 200–230.

## Adendo de 25/10/2026: híbrido condicional–LF na parte A

Escrito depois de calcular a primeira linha da parte A (H-P4, horas totais) e
o P3-CA (rodada de desenvolvimento do script 35), e antes de qualquer
estimativa do P4-CA.

- **Achado.** O teste condicional puro de ARP, congelado no §2.4, fica muito
  conservador quando outro momento está perto de ativo: num caso sintético
  (M̄ = 0, um pré a 5 EP de zero, um pós) aceita θ̄ a quase 5 EP do ponto, e na
  primeira linha real o IC em M̄ = 0 sai mais largo que em M̄ = 0,25. É a
  limitação que Andrews, Roth e Pakes (2023) descrevem e que o híbrido
  condicional–LF corrige; o híbrido é o padrão do pacote HonestDiD para Δ^RM.
- **Decisão.** O condicional puro continua em todas as linhas, como congelado
  (`RM`, `RM_ruptura`). Acrescenta-se o híbrido (`RM_hibrido`,
  `RM_hibrido_ruptura`): κ = α/10, valor crítico LF por 1.000 simulações
  (semente 20261025 + índice do poliedro), v_up truncado no valor crítico,
  nível condicional (α − κ)/(1 − κ). Por custo, o híbrido roda nas linhas
  principais (P3 K_esp; P4 horas totais, no município do posto e fora) e nas
  quatro do CA; as secundárias ficam só com o condicional.
- **Leitura.** O doc 57h mostra as duas rupturas lado a lado. A regra do §6
  ("ruptura de Δ^RM ≥ 1") é aplicada com as duas e o doc diz qual satisfaz.
  Nada muda na parte B.
- **Validação.** `tests/test_honestdid.py` (classe `TestHibrido`): o caso
  sintético acima, o valor crítico LF de uma desigualdade (≈ 2,576) e cobertura
  ≥ 0,93 em Monte Carlo.
