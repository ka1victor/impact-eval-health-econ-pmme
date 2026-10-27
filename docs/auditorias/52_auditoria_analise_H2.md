# 52. Auditoria da análise completa da H2 (doc 66, script 51)

> **Data:** 27/10/2026, véspera da banca 2.<br>
> **Objeto:** [`06_execucao/66_analise_completa_H2.md`](../06_execucao/66_analise_completa_H2.md),
> `scripts/rdd_bolsa/51_sintese_H2.py`, `output/rdd_bolsa/H2_sintese.csv`, `H2_resumo.json`, as 6 figuras em
> `output/rdd_bolsa/H2_figuras/` e `tests/test_sintese_H2.py`, no commit `d5b6f3a` (branch
> `claude/vigilant-mccarthy-dd92mc`).<br>
> **Referências lidas:** `CLAUDE.md`; docs 07 e 08 da banca 2; doc 65 e [auditoria 50](50_auditoria_avaliacao_hipoteses.md)
> (regras de redação); docs 42 (§5.2), 57p, 57v, 57w (PH-5) e 57x; auditorias 41, 46, 47 e 48; G1.<br>
> **Método:** (1) cada número copiado foi relido da saída de origem (`VL_`, `VC_`, `VD_`, `E9_estimativas.csv`,
> `P1h_magnitudes.csv`, `G1_resumo.json`, `P1_resumo.json`, `numeros_banca2.json`), com o filtro e a descrição
> conferidos; (2) os descritivos novos foram refeitos com código próprio, sem importar o 51, a partir das mesmas
> bases (`escolhas_candidatos`, `escolhas_conjunto_principal`, `G1_candidatos_origem`, `G1_distancias_opcoes`, malha
> de regiões e IVS 2010 oficial do a08), em memória; (3) as 6 figuras foram vistas uma a uma; (4) o texto foi lido
> contra as regras da auditoria 50; (5) o 51 foi rodado duas vezes e as saídas comparadas byte a byte. Nada foi
> reestimado; nada foi gravado em `data/` nem nas saídas de origem.

## Veredito

**Aprovado com correções.** Nenhuma estimativa mudou.

- **Números.** Todos os números de estimação conferem com a saída auditada nas casas mostradas. Os descritivos novos
  foram reproduzidos exatamente por código independente.
- **Correções.** Os problemas estavam na **descrição** e no **peso** dados a alguns números:
  - o VL-1 era descrito como "só vagas da UF de origem" (A1);
  - a F6 e a tabela de robustez destacavam como "linha principal" o adendo pós-resultado (A2);
  - o descritivo F2 aparecia com peso de evidência (A3);
  - a comparação crua da bolsa média vinha com uma explicação não testada dita como fato (A4);
  - a §10 trazia frases mais fortes que os dados (A5).

  Tudo foi corrigido no script 51 (texto gerado, rótulos e figuras) e no texto à mão do doc 66. O CSV mudou só no
  rótulo e na coluna `principal` de duas linhas e ganhou o p unilateral de três D_UF que já estava na origem.

## 1. Achados, por gravidade

### Graves (mudam o que se diz na banca)

**A1. O VL-1 estava descrito como "só vagas da UF de origem". Não é o que ele estima.**

- **O que o VL-1 faz** (57x, decisão 1): o efeito fixo do par (UF de origem, UF da vaga) vira, para cada UF de
  origem, um indicador de UF da vaga. O peso da bolsa vem de vagas **da mesma UF** comparadas entre si, vistas por
  médicos **da mesma UF de origem**. Isso vale **em qualquer UF da vaga**, não só na de origem: 281 pares com
  escolha, de 27 UFs de origem (57x §3).
- **Onde estava errado:**
  - o título da 4ª linha da resposta curta: "Dentro da UF de origem, a bolsa maior é mais escolhida";
  - a legenda da F3: "VL-1: só vagas da UF de origem";
  - a linha de km da §6: "VL-1: só vagas da UF de origem".
- **Por que importa:** a banca pode perguntar "é dentro da UF de origem?" e a resposta certa é não. Só o descritivo
  F2 é, de fato, restrito à UF de origem, e por isso ele não é a "versão descritiva" do VL-1 nem do VL-2.

**Correção:** "comparando vagas da mesma UF (a da origem ou outra), vistas por médicos da mesma UF de origem" na
resposta curta, na §4 (item 5) e na §6 (leitura 3); legenda da F3 e linha de km: "vagas da mesma UF (par de UFs)".

**A2. A F6 e a tabela de robustez destacavam o VL-1 como "linha principal".**

- O VL-1 é a principal do **adendo pós-resultado 52e** (`ADENDO_52E_POS_RESULTADO`), não da H2.
- A especificação **pré-registrada** do peso da bolsa é o M1 dos ciclos 1–3 (P1a). Ele tem IC que contém 1 e
  p 0,072.
- Destacar o VL-1 em azul, com losango, ao lado de "linha principal", repetia o problema que a auditoria 50 (A4)
  apontou no doc 65: usar a significância do adendo para reforçar a conclusão, quando a primária pré-registrada não
  rejeita.
- O painel do D_UF estava certo: o D_UF do M1 (P1h-1) é o teste central.

**Correção:**
- `principal` passou do VL-1 para o M1 dos ciclos 1–3 (rótulo "M1 (base, pré-registrado), ciclos 1–3");
- o M1 abre a tabela e o painel;
- o cabeçalho da tabela diz que o VL-1 é a principal do adendo, não da H2;
- o "Como ler" da F6 diz: "losango azul: especificação pré-registrada (M1; D_UF do P1h-1) [...] o VL-1 é adendo
  pós-resultado".

O teste agora exige `principal` = {M1 dos ciclos 1–3, D_UF do M1}.

### Médios

**A3. A F2 (52,5% × 60,8%) aparecia com peso de evidência.**

- **Os números estão certos** (seção 2). As definições também:
  - **"Disponível"** é a média, entre candidatos, da parte das vagas (células CNES × curso) do mesmo conjunto
    (curso × ciclo), da UF de origem e da mesma janela que fica do lado de bolsa maior;
  - **"Escolhida"** é a parte das 1ªs opções desse lado;
  - **a janela** é |s − corte| ≤ 50, com s = IVS oficial × 1000 arredondado, e s ≤ 350 vai para o corte 0,300,
    como no VL-2 (57x, decisão 6);
  - **a UF de origem** é a do município de origem principal do G1 (prefixo do código IBGE, igual à coluna
    `uf_origem`);
  - **só contam candidatos que veem os dois lados do corte na sua UF.**
- **Por que é só descritivo:**
  - não controla distância, porte, capital nem a própria origem: um terço desses candidatos escolhe o próprio
    município;
  - é ponderado por célula, não por vaga;
  - condiciona a 1ª opção estar na UF de origem e perto do corte;
  - está concentrado: 1.568 candidatos em 50 conjuntos, e duas UFs (CE e MG) somam 44% deles.
- **A versão com inferência e distância (VL-2) é inconclusiva**: 1,28 [0,95; 1,72]. O VL-2 também não é a mesma
  amostra: usa todos os pares de UF, não só a de origem.
- **O texto dava peso demais:**
  - a §3 tinha o título "Perto do corte, a bolsa aparece";
  - a resposta curta dava ao descritivo uma linha própria, no mesmo nível das linhas com teste;
  - o guia do grupo (doc 08) põe a F2 ao lado da F3.

**Leitura do auditor.** A F2 é um bom **retrato** de que, perto do corte, a escolha pende para o lado de bolsa
maior. Ela resiste a definições alternativas (seção 2). Mas **não é evidência à parte** e não deve sustentar
sozinha nenhum slide.

**Correção:**
- título da F2 começa por "Descritivo:";
- o "Como ler" diz "sem teste e sem controlar a distância; com inferência (VL-2), inconclusivo";
- a linha da resposta curta termina com "Não é evidência à parte: a versão com inferência e distância (VL-2) é
  inconclusiva";
- a §3 passou a "Perto do corte (descritivo)", com as limitações acima em palavras.

**A4. A comparação crua da bolsa média (14,14 × 14,23) vinha com uma explicação não testada dita como fato.**

O texto dizia: "as vagas de bolsa maior ficam em municípios mais vulneráveis, que por outros motivos atraem menos".
Nada no doc testa isso. O recálculo do auditor (seção 2, descritivo, em memória) aponta um canal mais direto, a
própria origem:

- dos 4.295 candidatos que escolhem na UF de origem, 45% escolhem o **próprio município**;
- a bolsa média do município de origem, pela regra do IVS, é 13,11, abaixo da média disponível (14,14);
- entre os que escolhem **fora** do próprio município, a bolsa escolhida é 15,27 contra 14,33 disponível.

Isso também é descritivo e não deve virar número do doc sem passar pelo script. Mostra só que a explicação do texto
não era a única nem estava demonstrada.

O texto também não dizia o que é "disponível" (média por célula, não por vaga) nem que só entram os candidatos cuja
1ª opção está na UF.

**Correção:** o item passou a "A comparação crua não isola a bolsa", com as definições e a frase "Que as vagas mais
vulneráveis atraiam menos por outros motivos é uma leitura possível, não testada aqui". Cita a origem (ficar no
próprio município) como mistura evidente e remete ao modelo de escolha.

**A5. A §10 (teoria) e a §1 diziam mais do que os dados.**

- **"O termo que domina a escolha não é o custo ligado ao IVS [...] e sim o componente individual ligado à origem".**
  É o "mostra" que a auditoria 50 (A13) pediu para trocar por "sugere". A origem é preferência revelada; os canais
  (família, registro, renda alternativa) não se separam.
- **"O degrau alcança a margem 'qual vaga perto de casa', mas não a margem 'sair da região'".**
  - Não foi testado. No logit condicional, a bolsa aumenta a chance de **qualquer** vaga, perto ou longe.
  - D_UF > 0 diz só que toda a diferença de bolsa pesa menos que ter a vaga na UF de origem.
  - Também não se testou nada no nível da "região": a evidência é no nível da UF.
- **§1, "A bolsa desloca a escolha entre vagas parecidas da mesma região, mas não compensa sair dela".** Mesma
  questão. Faltava o "pacote do corte".

**Correção:**
- §10:
  - "Os pesos estimados **sugerem**";
  - "a origem é preferência revelada";
  - "vagas parecidas da mesma UF";
  - o 3º item foi reescrito: a bolsa compensa só uma parte do peso da origem, e isso não quer dizer que o degrau não
    mova ninguém para fora da UF;
  - "a resposta sugerida, não testada".
- §1: "O pacote do corte desloca a escolha entre vagas parecidas da mesma UF, mas toda a diferença de bolsa pesa
  menos que ter a vaga na UF de origem". Também ganhou uma nota: "dentro da sua região" é medido no nível da UF.

A frase da hipótese é do autor (doc 07) e **não foi alterada**.

### Menores

**A6. "p de Holm 0,072" do β pré-registrado sem dizer que a família tem um teste.** Confere com `VC_estimativas.csv`
(M1, `bolsa_mil`: p 0,0724, `p_holm` 0,0724, família "P1a: família de um teste, bilateral"). Holm numa família de um
teste é o próprio p, e a leitura "não passa no Holm" está certa. Mas a frase sugere uma correção que não houve. O
número é do quadro do ciclo 2 de 13/02 (52c). Com o quadro antigo eram 0,065 (57a; auditoria 50, tabela, linha 32).
**Correção:** "(família de um teste: Holm = p)" na resposta curta.

**A7. O BKY dá q abaixo do p em duas secundárias, e o doc não explicava.**

- **As duas linhas:**
  - VL-3 perto do corte, ciclos 1–3: p 0,101, q 0,043, IC [0,95; 1,71];
  - VL-2 do ciclo 2: p 0,042, q 0,022.
- **É legítimo.** O BKY de dois estágios estima o número de nulas verdadeiras e, quando quase toda a família
  rejeita, o q pode ficar abaixo do p. O auditor refez a conta do q do VL-3 perto do corte: com nível 0,043, o 1º
  estágio rejeita 5 das 7, e o 2º estágio, com m₀ = 2, rejeita todas.
- **Mas o doc lê o VL-3 perto do corte como "não se distingue de zero"**, e um leitor vê q < 0,05 na mesma linha.

**Correção:** uma frase gerada no bloco de robustez explica o q < p e diz que a leitura é pelo IC: inconclusivo, como
o VL-2.

**A8. O título da F5 começava pelo número cujo IC contém zero.** "+R$ 5 mil pesam como 119 km a menos" é o M1, com
IC [−12; 250]. **Correção:** "Na mesma UF, +R$ 5 mil pesam como 75 km a menos; no M1, 119 km (IC contém zero)". A
linha de km da resposta curta foi reordenada do mesmo jeito.

**A9. Faltavam duas ressalvas da auditoria 50 (A4) sobre o VL-1.**

- **O VL-1 não foi estimado nos ciclos 1 e 3**, e o resultado dos ciclos 1–3 juntos não vale para cada ciclo. A F3
  dizia isso; o texto não.
- **O t com cluster por conjunto e spline linear superestima a precisão nos cortes placebo do E9** (doc 42 §5.2). O
  VL-1 usa o mesmo spline e a mesma inferência.

**Correção:** frase na resposta curta, na §4 (item 5) e na §6 (leitura 3); linha "Precisão calibrada" na tabela de
premissas da §5.

**A10. A diferença pareada VL-1 − M1 foi lida sem dizer o estatuto nem o ciclo 2.** Os números conferem:
- ciclos 1–3: 0,159 [0,089; 0,229], igual a ln(1,470) − ln(1,254);
- ciclo 2: 0,063 [−0,061; 0,187].

A diferença é descritiva, fora do Holm (57x, decisão 10); no ciclo 2 contém zero. **Correção:** dito na §6
(leitura 3).

**A11. Médico de outra UF em 0,400.** O texto já dizia "inconclusivo", mas omitia que os poucos pares com diferença
apontam todos para mais médicos de fora do lado de bolsa maior (57w §7; auditoria 47, A3). **Correção:** acrescentado
na §8. A ausência não é dita como fato.

**A12. Três D_UF de sensibilidade sem o p unilateral.** As linhas do M2, M4 e M7 mostravam "—" no p unilateral,
que está em `VD_estimativas.csv`. **Correção:** o script passou a copiar a coluna `p_unilateral`. O q BKY (0,001) já
estava.

**A13. Títulos cortados.** As versões corrigidas dos títulos da F2 e da F5 saíam da borda da figura. **Correção:**
títulos mais curtos e uma trava no script, que para se o título passar de cerca de 8,5 caracteres por polegada.

**A14. Cabeçalho "auditoria pendente".** Trocado pelo link desta auditoria. No doc 08 da banca 2, as duas menções
"auditoria em curso" também foram trocadas, com um aviso sobre A1 e A3. O teste agora confere o cabeçalho.

### Observações (sem correção)

- **Doc 07 da banca 2 (decisão do autor).** Tem frases com o mesmo problema da A5:
  - "a bolsa maior aumenta a chance";
  - "Um degrau de R$ 5 mil desloca a escolha entre vagas próximas, mas não alcança esse custo";
  - "dentro da região".

  Não foram alteradas: o doc registra a decisão do autor. Recomenda-se que o deck use a redação corrigida do doc 66
  (§1 e §10).
- **D_UF por ciclo.** O D_UF do M1 só do ciclo 1, 2 ou 3 tem q BKY 0,001 em `VD_estimativas.csv`, mas o 51 copia
  essas linhas do `VC_estimativas.csv`, que não tem o q. A tabela mostra "—" no p ajustado, o que é conservador.
- **Score bootstrap.** Do M1 pré-registrado: p 0,122 (57x §4.1). Do VL-1, com Holm: 0,023 e 0,011. O doc mostra os p
  brutos do score, e isso está certo.
- **Determinismo e PNG.** As figuras saem idênticas byte a byte entre execuções no mesmo ambiente. Uma versão
  diferente do matplotlib pode mudar os bytes sem mudar o conteúdo.

## 2. O que foi recalculado

### 2.1 Números copiados (conferidos contra a origem)

| Número no doc 66 | Valor | Origem | Descrição | Confere? |
|---|---|---|---|---|
| D_UF M1, ciclos 1–3 | 1,94 [1,48; 2,40], p unil. < 0,001, Holm = p | `VC_estimativas.csv`, `corrigida_13fev`, M1, D_UF (1,9421; p 6,4e−17; família de um teste) | P1h-1, quadro de 13/02 | sim |
| D_UF M1, ciclo 2 | 1,19 [0,51; 1,86] | VC, M5_2 (1,1869) | M1 só do ciclo 2 | sim |
| θ_UF e 10·β | 2,40 [2,27; 2,52]; 0,45 [−0,04; 0,95] | VC, M1 (2,3950; 10 × 0,045292) | quadro de 13/02 | sim |
| β pré-registrado | 0,0453 [−0,0041; 0,0947], p de Holm 0,072 | VC, M1, `bolsa_mil` (p = `p_holm` = 0,07238) | família de um teste (A6) | sim |
| VL-1, ciclos 1–3 | 1,47 [1,15; 1,89], p 0,002, Holm 0,005 | `VL_estimativas.csv`, VL1_emp (1,4702; 0,00247; 0,00494) | era "só UF de origem" (A1) | número sim; descrição corrigida |
| VL-1, ciclo 2 | 1,90 [1,30; 2,78], Holm 0,003 | VL1_c2 (1,9045; 0,00263) | idem | número sim; descrição corrigida |
| VL-2 | 1,28 [0,95; 1,72], Holm 0,103 | VL2_emp (1,2798) | inconclusivo | sim |
| M1 RC, ciclos 1–3 e ciclo 2 | 1,25 [0,98; 1,61]; 1,79 [1,19; 2,68] | VL, M1_emp e M1_c2 (iguais ao VC) | — | sim |
| M1 RC, ciclos 1 e 3 | 1,07 [0,69; 1,65]; 1,00 [0,72; 1,39] | VC, M5_1 e M5_3 | — | sim |
| Diferença pareada | 0,159 [0,089; 0,229]; 0,063 [−0,061; 0,187]; 0,020 [−0,227; 0,267] | VL, `diferenca_log_rc_contra_referencia` | descritiva, fora do Holm (A10) | sim |
| km | 119 [−12; 250]; 302 [88; 516]; 75 [28; 122]; 117 [56; 178] | VL, `km_equivalentes` K5 (118,81; 302,43; 74,91; 116,57) | IC delta | sim |
| γ e β no VL-1 | −0,51 contra −0,19; 0,077 contra 0,045 | VL e VC, coeficientes | — | sim |
| Robustez (24 RC, 8 D_UF) | tabela da §7 | VL, VC, VD, E9 (spline cúbico: exp(5·coef), quadro de 19/03), P1h | rótulos, ajuste, família e quadro | sim |
| M2/M4/M7 D_UF | 1,16; 1,70; 2,03; q BKY 0,001 | VD, `corrigida_13fev` | família P1h-3 (6) | sim; faltava o p unilateral (A12) |
| Amostra G1/P1 | 5.776 / 5.573 / 5.484; 5.714; 5.421; 56 conjuntos, 5.125 vagas, 932.577 pares | `G1_resumo.json`, `P1_resumo.json` | — | sim |
| Identificação do VL-1 | 260 de 281 pares; 27 UFs; 5.345 de 5.417; 3.937 | `VL_resumo.json` | — | sim |
| ESC_* | 79%, 46%, 36%, 51 km, 189 km, 5.425 | `numeros_banca2.json` | descritivo | sim |

As contagens "IC acima de zero em 8 de 8" e "acima de 1 em 16 de 24", bem como as listas "o que se mantém" e "o que
muda" da §7, conferem linha a linha.

### 2.2 Descritivos novos (código próprio, sem importar o 51)

Base: 1ª opção (`opcao_rank` = 1, única por candidato) com origem do G1 (`g1_cpf_nome`, `co_ibge_origem`
preenchido) e distância à origem principal preenchida. UF = 2 primeiros dígitos do IBGE, conferido contra a coluna
`uf_origem` do G1. Região = `sg_uf` + `no_regiao_saude` da malha. IVS só do a08; a coluna `ivs_2010` da malha não é
usada. Faixa da célula conferida contra a regra de dois cortes do IVS oficial: 0 discordâncias em 5.134 células; 1
célula sem IVS fica fora, como no 51.

| Descritivo | Doc 66 | Recálculo | Confere? |
|---|---|---|---|
| N por ciclo | 918 / 2.033 / 2.474 (5.425) | 918 / 2.033 / 2.474 | sim |
| Mesma UF / região / município, ciclos 1–3 | 79% / 46% / 36% | 0,7917 / 0,4579 / 0,3583 | sim |
| Idem por ciclo | 72/24/16; 81/49/40; 80/51/40 | 0,7233/0,2386/0,1612; 0,8136/0,4943/0,3999; 0,7991/0,5093/0,3973 | sim |
| Mediana e 3º quartil (km) | 51 / 189; 126/271; 37/153; 34/164 | 51,4/188,5; 126,5/270,7; 36,9/152,9; 34,3/163,9 | sim |
| Mesma UF por bolsa escolhida | 77% (2.017), 82% (2.231), 77% (1.177) | 0,7744; 0,8207; 0,7664 (mesmos n) | sim |
| Bolsa média disponível × escolhida na UF | 14,14 × 14,23 (4.295); 14,31 × 14,28; 13,89 × 14,20; 14,29 × 14,24 | 14,140 × 14,232; 14,314 × 14,277; 13,887 × 14,199; 14,293 × 14,244 | sim |
| Perto do corte, ciclos 1–3 | 52,5% × 60,8% (1.568) | 0,5254 × 0,6084 (1.568) | sim |
| Idem por ciclo | 49,6/55,6 (234); 53,0/64,1 (691); 53,1/59,3 (643) | 0,4955/0,5556; 0,5302/0,6411; 0,5312/0,5925 | sim |
| Por corte | 0,300: 52,3/60,6 (791); 0,400: 52,8/61,1 (777) | 0,5230/0,6056 (791); 0,5280/0,6113 (777) | sim |

### 2.3 Sensibilidades da F2 e da comparação crua (só nesta auditoria; descritivas; não entram no doc)

| Variante | Disponível | Escolhida | n |
|---|---|---|---|
| Como no doc 66 | 52,5% | 60,8% | 1.568 |
| IVS sem arredondar a milésimos | 52,5% | 60,8% | 1.568 |
| Sem quem escolhe o próprio município de origem | 54,5% | 66,8% | 1.040 |
| Só quem escolhe o próprio município | 48,6% | 49,1% | 528 |
| Sem exigir ver os dois lados do corte | 46,9% | 50,7% | 3.464 |
| Vagas ponderadas por vagas imediatas + 1 | 52,0% | 60,8% | 1.568 |
| Sem CE (a UF com mais candidatos) | 47,4% | 55,4% | 1.172 |
| Sem MG | 52,7% | 60,1% | 1.281 |
| Sem RJ | 53,5% | 61,1% | 1.482 |

16 das 21 UFs têm a escolhida acima da disponível, e as três maiores contribuições respondem por 69% da diferença
total (8,3 p.p.). A direção resiste a todas as variantes; a diferença some entre quem escolhe o próprio município,
como esperado. Comparação crua: dos 4.295, 45% escolhem o próprio município; a bolsa do município de origem é 13,11
em média; fora do próprio município, a escolhida é 15,27 contra 14,33 disponível (A4). Scripts do auditor fora do
repositório; leitura só em memória.

## 3. Figuras

| Figura | Uma mensagem? | "Como ler" e fonte | Problema | Situação |
|---|---|---|---|---|
| F1 (onde escolhem) | sim | sim | nenhum; eixo 0–100, histograma com cauda agrupada em 1.500+ rotulada | sem mudança |
| F2 (perto do corte) | sim | sim | peso de evidência; não dizia "vagas = células" nem a falta de controle de distância (A3) | título "Descritivo:"; "Como ler" com VL-2 inconclusivo |
| F3 (razão de chances) | sim | sim | legenda "só vagas da UF de origem" (A1). Diz, sim, que o VL-1 não foi estimado nos ciclos 1 e 3; escala log com 1 marcado | legenda corrigida |
| F4 (origem × bolsa) | sim | sim | nenhum; mesma escala, IC, caixa com D_UF | sem mudança |
| F5 (km) | sim | sim | título abria pelo número com IC que contém zero (A8) | título reordenado |
| F6 (robustez) | sim | sim | destacava o VL-1 (adendo) como principal (A2); o D_UF estava certo | M1 pré-registrado destacado e no topo; "Como ler" reescrito |

Nenhum eixo engana: as razões de chances estão em escala log com a linha em 1; os pesos e o D_UF, em escala linear
com a linha em 0; os percentuais vão de 0 a 100.

## 4. Texto, pelas regras da auditoria 50

| Regra | Situação no doc 66 |
|---|---|
| "não detectamos aumento", nunca "não encheu" | cumprida (§1, §9, frase de 10 s; o teste proíbe as formas erradas) |
| o teste central é D_UF | cumprida (resposta curta, §4, §6, F4, F6); reforçada na §8 |
| o VL-1 é pós-resultado | cumprida, mas a F6 o destacava como principal (A2, corrigido) |
| médico de outra UF em 0,400 é inconclusivo | cumprida; acrescentada a direção dos pares (A11) |
| o contraste é o pacote do corte | cumprida nas ressalvas; acrescentada na §1 e na §10 |
| a origem é preferência revelada | cumprida; a §10 dizia "o termo que domina" sem "sugere" (A5, corrigido) |
| tudo é condicional a se candidatar | cumprida (ressalva 1, §5, §9) |

- **Seção 8 (perguntas da banca).** Correta e simples. Ajustes: a resposta sobre "como ela muda qual vaga" agora diz
  "Holm do adendo pós-resultado" e lembra que o teste central é o D_UF; médico de longe com a direção dos pares.
- **Seção 10 (teoria).** Coerente com o modelo micro. Estava forte demais em dois pontos (A5), já corrigidos.

## 5. Integridade

- **IVS.** O 51 só lê o IVS de `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`. O arquivo local errado não é
  citado nem aberto: o teste com *audit hook* confere os arquivos abertos. A coluna de IVS da malha não é lida.
- **`data/`.** Nenhuma leitura nem escrita. O script grava só nos seus alvos (`H2_*` e doc 66), e o teste tenta
  gravar nas saídas de origem e falha, como deve.
- **`EMPIRICO`.** Todas as 137 linhas do CSV, o resumo e cada base lida estão marcados `EMPIRICO`. Nada é sintético,
  imputado ou cenário. O doc 57b é citado só em palavras, como simulação.
- **Saídas de origem intactas.** O commit `50f221d` não tocou `G1_*`, `E9_*`, `P1_*`, `P1h_*`, `VC_*`, `VD_*` nem
  `VL_*`. Os SHA-256 registrados em `H2_resumo.json` conferem.
- **Determinismo.**
  - Antes das correções, o 51 rodado de novo reproduziu byte a byte o CSV, o resumo, as 6 PNG e o doc 66.
  - Depois das correções, duas execuções seguidas também saíram idênticas.
  - Os SHA-256 (12) novos são:
    - `H2_sintese.csv`: `42308e104e2a`;
    - `H2_resumo.json`: `c137a184b205`;
    - F2: `19196d2405bd`;
    - F3: `7cd9bb2ddd7a`;
    - F5: `e51e10c4b7b5`;
    - F6: `b805b316f917`.
  - F1 e F4 não mudaram.
- **Testes.** `tests/test_sintese_H2.py` passa. Foi acrescentado `test_correcoes_da_auditoria_52`, que confere:
  - o cabeçalho;
  - a ausência de "só vagas da UF de origem" e "a bolsa aparece";
  - a linha principal pré-registrada;
  - o título descritivo da F2;
  - o "Como ler" da F6.

## 6. O que mudou nesta auditoria

- **`scripts/rdd_bolsa/51_sintese_H2.py`:**
  - texto gerado da resposta curta (A1, A3, A6, A8, A9);
  - legenda da F3 (A1);
  - título e "Como ler" da F2 (A3);
  - título da F5 (A8);
  - linha principal e ordem da robustez, "Como ler" da F6 (A2);
  - frase do BKY (A7);
  - p unilateral de três D_UF (A12);
  - trava de largura do título (A13).
- **Saídas regeneradas:** `output/rdd_bolsa/H2_sintese.csv`, `H2_resumo.json`, F2, F3, F5 e F6. Nenhuma estimativa
  mudou.
- **`docs/06_execucao/66_analise_completa_H2.md`:**
  - blocos regravados com `--atualizar-doc`;
  - texto à mão: cabeçalho; §1 (nota da UF e resposta proposta); §3 (leitura da comparação crua e de perto do
    corte); §4 (item 5); §5 (linha de precisão); §6 (leitura 3); §8 (duas respostas); §10.
- **`docs/07_apresentacoes/banca2/08_guia_do_grupo_H2.md`:** "auditoria em curso" → link desta auditoria, com o
  aviso sobre A1 e A3.
- **`tests/test_sintese_H2.py`:** teste novo (seção 5).
- **`docs/00_registro_mudancas.md`:** entrada desta auditoria.
