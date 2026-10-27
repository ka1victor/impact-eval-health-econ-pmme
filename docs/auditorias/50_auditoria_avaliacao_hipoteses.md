# 50. Auditoria do doc 65: avaliação da força das hipóteses H1, H2 e H3 (banca 2)

> **Data:** 27/10/2026.<br>
> **Objeto:** [`06_execucao/65_avaliacao_forca_hipoteses.md`](../06_execucao/65_avaliacao_forca_hipoteses.md) no
> commit `7e9f881` (branch `claude/vigilant-mccarthy-dd92mc`). Ordem no Git: §0–§5 em `568d8e4` (26/10, 23:48),
> §4.6 em `12c5211` (27/10, 02:05), §4.7 em `3156b3d` (27/10, 02:24) e §4.8 em `a6a2c30` (27/10, 04:29). Os adendos
> 48h e 52e rodaram entre 03:27 e 04:10 de 27/10. Portanto, só a §4.8 conhece os resultados deles.<br>
> **Uso declarado:** o autor vai escolher por este doc **uma** hipótese para a apresentação de 28/10/2026.<br>
> **Referências lidas:** `CLAUDE.md`; docs 57a, 57d, 57i, 57j, 57k, 57l, 57n, 57o, 57p, 57q, 57r, 57s, 57t, 57u, 57v,
> 57w e 57x; docs 37, 42, 44, 49 e 63; protocolo 52b; [modelo micro](../02_teoria/modelo_micro.md) §4; doc 15 §1;
> auditorias 18 e 31 a 48; docs 02, 04 e 05 da banca 2.<br>
> **Método:** cada número do doc 65 foi conferido contra o doc citado e, nas linhas principais, contra o CSV ou JSON em
> `output/` (`HI_estimativas.csv`, `PL_estimativas.csv`, `VL_estimativas.csv`, `P1h_magnitudes.csv`,
> `VC_estimativas.csv`, `P4_estimativas.csv` e `output/apresentacao_banca2/numeros_banca2.json`), com leitura em
> memória. Nada foi estimado e nada foi gravado em `output/`.

## Veredito

**Aprovado com correções.**

- **Números.** Os números conferem com a fonte citada (tabela da seção 3). Não há número inventado nem trocado. Há
  quatro números **desatualizados**, superados por versões corrigidas e já auditadas: os 112 km, o β de 0,0424
  com p 0,065 no resumo, e a marca "auditoria pendente" do 57v em três lugares. Há também **um número sem fonte**, os
  79% da §4.7. Esses pontos foram corrigidos no doc 65 com nota datada.
- **Texto.** O problema está na leitura, não nos números. O doc traz **duas recomendações sem dizer qual vale**:
  - a §0 e a §4.4 recomendam a H1 como hipótese única;
  - a §4.7 propõe a H2 como hipótese, com a H1 como fato que a motiva;
  - a §4.8 diz que a H2 "ganha força".

  O resumo da §0 e as notas das §4.6 e §4.7 não incorporam os adendos 48h e 52e. A §4.7 e a §4.8 também transformam a
  **não detecção** da H1 em fato ("não quantas vagas são preenchidas"), o que a própria §1.6 proíbe. Isso não foi
  reescrito, porque é opinião. Foi acrescentada no topo do doc 65 uma nota de "estado atual" que aponta a seção mais
  recente e onde as seções divergem.

## 1. Achados, por gravidade

### Graves (afetam a escolha de amanhã)

**A1. O doc dá duas recomendações incompatíveis e não diz qual prevalece.**

- A §0 ("Veredito curto") e a §4.4 recomendam a **H1 como hipótese única**. A §4.4 avisa: "passar à H2 porque a H1
  deu nulo seria escolher a hipótese depois do resultado".
- A §4.7 propõe juntar as duas "numa só hipótese (H2)", com o resultado da H1 como "fato que motiva a pergunta". É
  exatamente o caminho que a §4.4 só admitia como plano B ("se o autor ler a regra como 'a H1 precisa mostrar o
  efeito'"). A §4.7 não repete o custo que a §4.4 aponta.
- A §4.8 diz que "a H2 ganha força" e fecha com a síntese "qual vaga, não quantas", sem retomar a recomendação.
- A tabela-resumo da §0 continua sem o 48h e o 52e. O [doc 05 da banca 2](../07_apresentacoes/banca2/05_discussao_historia_empirica.md)
  (§2.16, última linha) cita o doc 65 com a recomendação da H1.

Quem ler só o topo escolhe a H1; quem ler só o fim escolhe a H2. As duas opções são defensáveis, mas o doc precisa
dizer que a §4.4 e a §4.7 divergem e que a escolha é do autor. **Correção:** nota de estado atual no topo do doc 65.
A opinião não foi reescrita.

**A2. A §4.7 e a §4.8 tratam a não detecção da H1 como fato.**

- A §4.7 propõe dizer: "no corte, a bolsa maior não encheu mais vagas".
- A §4.8 sintetiza: "a bolsa muda qual vaga [...], mas não quantas vagas são preenchidas".

Os dados não sustentam um nulo:

- por corte, a HI-1 só detectaria saltos de 25 a 31 p.p. (57n §3);
- o TOST é inconclusivo em 3 das 4 primárias (57n §4, HI-s7);
- com o IC honesto, nada fica descartado;
- no 48h, a diferença mínima detectável é de 24 a 29 p.p., com 25 e 29 pares (57w; auditoria 47, A1).

A própria §1.6 lista como "não dá para afirmar" que a bolsa não funciona ou que o efeito é zero. O doc 44 §7.3, de
onde vem a leitura "realocação entre vagas", diz "sem expansão líquida **detectável**". Esse doc é uma **proposta**
ao autor (`CLAUDE.md`: "a revisão da hipótese é proposta, não decisão").

A forma defensável é "não detectamos mais vagas preenchidas; os dados só descartam aumentos grandes, e em parte das
medidas". Vale também para o "fato que motiva" da §4.7. **Correção:** registrado na nota de estado atual. A frase de
opinião não foi reescrita.

### Médios

**A3. A §4.8 exagera "de onde vinha a queda em 0,300: da UF [...] Com efeito fixo de UF, a queda some" e "explicação
do sinal resolvida".**

- **Números da auditoria 47 (observações), na mesma amostra:**
  - sem controle: −1,15 [−2,21; −0,08];
  - só a UF: −0,55 [−1,61; +0,50];
  - só o raio: −1,19 [−2,24; −0,13];
  - os dois: −0,62 [−1,67; +0,43].

  Com a UF, o ponto **cai à metade** e o IC passa a conter zero. A queda não "some". No 57o (C-3), o EF de UF leva a
  HI-2 a −0,32 [−1,31; +0,66].
- **Outros controles também mexem na queda:**
  - a dummy de capital: −0,83 [−1,87; +0,21] (57o);
  - L+M: −0,25 [−1,37; +0,87] (57r);
  - o pareamento: +0,10 e +0,13 por vaga imediata (57s, 57w).

  O 57r diz que a queda "não se separa" da localização e dos médicos na região. A auditoria 42 corrigiu o 57o por
  concluir "e não com a bolsa".
- **A queda nunca passou no Holm** (HI-2 em 0,300, p Holm 0,126; 57n §3). A §4.4 (item 4) do próprio doc recomenda
  trocar o slide "Por que o sinal sai negativo" porque o sinal "não passa no Holm e vira positivo no pareamento". Dar
  a explicação como "resolvida" contradiz essa recomendação.
- **O ponto pareado muda de sinal.** No 48h, em 0,300, o ponto da fração preenchida é **+16,4 p.p.** [−3,8; +36,6],
  com sinal oposto ao da RDD e só 1 par em comum com os 92 do 48e (auditoria 47, A5).

**Correção:** a frase factual "a queda some" foi trocada pelos números da auditoria 47, com nota datada. A leitura
"vinha da UF" é opinião e ficou, com a ressalva na nota de estado atual.

**A4. A §4.8 diz que "a H2 ganha força", mas o 52e testa outro estimando.**

- **A H2 do doc é D_UF** = θ_UF − 10·β: "a bolsa pesa pouco perto da origem" (§0, §2). No VL-1, o efeito fixo do par
  de UFs absorve θ_UF, e o D_UF **não é identificado** (57x, decisão 1). O 52e testa só se o **β** da bolsa vem da
  localização.
- **Um β maior não reforça a H2.** Com a comparação dentro da UF, o β sobe (0,045 → 0,077 por R$ 1 mil; 57x §4.4).
  Isso, se tanto, **aproxima** os dois lados da desigualdade. No análogo mais próximo, o M4 corrigido (β 0,078), o
  D_UF continua 1,70 [1,21; 2,19] (57v §5.6). A desigualdade sobrevive, mas não "ganha força".
- **O que o 52e reforça é outra frase:** "a bolsa desloca a escolha" (P1a/E9), que o doc 44 §7.3 chama de
  realocação. Essa frase fala de **β > 0**, o contrário de "a bolsa pesa pouco". A §4.8 troca o conteúdo da H2 sem
  dizer.
- **A significância vem de um adendo pós-resultado.** A frase "passa a se distinguir de zero depois do Holm" usa o
  Holm da família do 52e (`ADENDO_52E_POS_RESULTADO`). A primária pré-registrada, P1a (M1, quadro corrigido), segue
  sem rejeitar zero: 0,0453 [−0,0041; 0,0947], p de Holm 0,072 (57p §1).
- **A precisão pode estar superestimada.** O doc 42 §5.2 mostra que, no empilhado, o t com cluster por conjunto e
  *spline* linear superestima a precisão nos placebos. O VL-1 usa o mesmo *spline* e a mesma inferência.
- **O empilhado não vale para cada ciclo.** O 52e não estimou o VL-1 nos ciclos 1 e 3. A §4.7 diz que "a bolsa só
  deslocou a escolha no ciclo 2", e essa leitura por ciclo continua a mais sustentada (57a §7). Ler o VL-1 empilhado
  como generalização para os ciclos 1 e 3 repetiria o problema do E9 empilhado.
- **Duas expressões exageram.** "Deixa de depender de onde as vagas ficam" vale só no nível da UF; o par não
  controla diferenças dentro da UF (57x §8). "Dentro da sua região" deveria ser "dentro da mesma UF".

**Correção:** nota de estado atual. É opinião e não foi reescrita.

**A5. As notas da §4.7 contam as ressalvas de forma assimétrica, e a §4.6 e a §4.7 se contradizem sobre o gráfico
da H2.**

- **Contagem das ressalvas.** Na §4.7, a H1 "precisa de cinco ressalvas", entre elas o pacote do corte. Na H2,
  "três ressalvas". Faltam pelo menos três que a §2 do próprio doc exige:
  - o β é pacote do corte;
  - escolha não é preenchimento e vale condicional a se candidatar;
  - a origem é o vínculo no CNES, não a residência.

  Com a mesma régua, a H2 teria cinco ou seis. A nota "poucas ressalvas" (3 contra 1) favorece a H2 por construção.
- **Gráfico da H2.** A §4.6 dá 3 à H2 em clareza porque "logit e log-chance são abstratos". Vinte minutos depois, a
  §4.7 dá 5 à H2 em "o gráfico principal fala sozinho". A frase de 10 segundos da §4.7 se apoia nos 79% na mesma UF,
  que são **descritivos** (doc 02 da banca 2) e não testam D_UF. Se o "gráfico principal" é esse descritivo, a nota
  mede a clareza de um dado que não é a hipótese.

**Correção:** nenhuma no doc 65 (julgamento). Registrado aqui e na nota de estado atual.

**A6. A §0, as §4.6 e §4.7 e o resto do corpo estão desatualizados em relação ao 48h e ao 52e.**

- **§0, linha da H1.** Não traz o 48h: pareamento na UF, MDE de 24 a 29 p.p., ponto de +16,4 p.p. em 0,300.
- **§0, linha da H2.** Traz o β pré-correção (0,0424; p 0,065) como "peso da bolsa sozinho".
- **§4.6.** Diz que "o peso da bolsa sozinho não se distingue de zero". É verdade na primária, mas a §4.8 diz o
  contrário para o VL-1.

**Correção:** o β corrigido foi acrescentado ao lado do antigo na §0, com nota. O resto ficou na nota de estado atual.

**A7. Números superados por versões corrigidas e auditadas (corrigidos).**

- **"auditoria pendente" do 57v**, na tabela 2.2, na tabela 2.4 e na §5. O 57v foi auditado na
  [auditoria 46](46_auditoria_sensibilidades_ciclo2.md) (27/10, 00:27, depois do texto da §2). Ela aprovou com
  correções, e nenhuma estimativa mudou.
- **"112 km [−9; 233]"**, na tabela 2.3 e na §4.5. É o número do quadro de 19/03. O corrigido, de referência, é
  **119 km [−12; 250]** (57v §5.6; `VL_estimativas.csv`, VL-5). Comparando dentro da UF (VL-1), são 75 km [28; 122]
  (57x §4.3). Esses km não se comparam um a um com os do M1 (auditoria 48, observações).

### Menores

**A8. Os 79% da §4.7 não tinham fonte.** O número vem de `output/apresentacao_banca2/numeros_banca2.json` (`ESC_UF`
= 0,7917; G1, 5.425 candidatos; gerado por `scripts/apresentacao/gerar_figuras_banca2.py`; doc 02 da banca 2). A
fonte foi acrescentada com nota. É descritivo e não é o resultado da H2.

**A9. A §4.8 descreve mal o pareamento do 48h.** "Cada município do lado de bolsa maior pareado com um da mesma UF"
não é o que o 48h faz:

- em cada ciclo, quem procura par é o lado com **menos** unidades (em 0,300, no ciclo 1, é o de baixo; 57w, decisão
  10);
- a maioria fica sem par: 92/71 em 0,300 e 72/55 em 0,400;
- os pares são sobretudo do ciclo 2: 15 de 25 e 15 de 29.

"Resultado: nenhuma diferença" deveria ser "não se detecta diferença" (57w §1). **Correção:** as duas frases foram
ajustadas, com nota datada.

**A10. A §4.8 omite a origem dos médicos (PH-5).** A frase "não aparece mais médico vindo de outra UF" não está no
doc 65 nem nos docs da banca 2. Se for usada, precisa da ressalva da auditoria 47 (A3): em 0,400, os 5 pares com
diferença vão **todos** para o lado de bolsa maior, e o menor p possível com 5 pares é 0,0625. É **inconclusivo** por
falta de pares informativos, não evidência de ausência. A forma fiel é "pela regra fixada, não há indício; o teste
não tem pares suficientes para concluir". Registrado na nota de estado atual.

**A11. A §4.2 usa verbos de nulo.** "O índice de atração não se move", "a oferta no corte não se move" e "o corte nem
muda quem recebe médico" deveriam ser "não se distingue de zero". No primeiro estágio, o salto é +5,0 p.p.
[−20,1; +30,1], com F 0,2 (57q §4). Não foi corrigido: é redação dentro de uma seção de opinião, e a §1.6 já dá a
regra.

**A12. Há um deslize na §1.3.** "O que descarta aumento grande: só as medidas antigas empilhadas" contradiz a tabela
logo acima, em que a HI-2 em 0,300, por corte, descarta aumento ≥ 0,69. No contexto, a frase fala da HI-1 (+10 p.p.),
e a §1.6 diz as duas coisas certas. Não foi corrigido.

**A13. A §4.6 diz que a H2 "mostra" que o custo individual domina.** θ_UF é preferência revelada que mistura
família, rede, registro e renda alternativa (57i §1). A §4.5 do mesmo doc usa "sugere". "Mostra" é forte demais.

**A14. Há escolhas implícitas na soma da §4.6.**

- **Precisão da H2.** A H2 recebe "4 na desigualdade, 2 no peso da bolsa", e a soma usa o 4. Com o 2, a soma da H2
  cai de 26 para 24, contra 28 da H1. A leitura "H1 e H2 ficam próximas" depende dessa escolha, e o doc não a
  declara.
- **Força da conclusão da H2.** A H2 tem 4 por uma comparação cuja resposta era "previsível" pelos IC publicados
  (52b, cabeçalho; 57i, limites). A nota mede precisão, não informação nova.

**A15. O doc 65 não tem teste automático.** Os números foram copiados à mão de docs gerados; não há teste que confira
o doc 65 contra `output/`, como há nos 57*. Esta auditoria faz essa conferência uma vez (seção 3). Toda mudança futura
de número no doc 65 deveria repetir a conferência.

## 2. As notas por critério (§4.6 e §4.7)

São julgamento. Avaliei se cada nota é defensável pelos dados e se é coerente com o texto.

| Seção | Critério | Notas H1 / H2 / H3 | Defensável? | Observação |
|---|---|---|---|---|
| 4.6 | Limpeza do desenho | 3 / 2 / 1 | sim | coerente com §1.2, §2.2 e §3.2 |
| 4.6 | Formulada antes dos dados | 4 / 2 / 3 | sim | H1 do modelo micro §4.2 (`5cf4ed8`, 16/09), principal 48b pós-resultado; H2 pós-resultado (52b; auditoria 31 §1); H3: pergunta de oferta líquida no `CLAUDE.md` |
| 4.6 | Força da conclusão | 2 / 4 / 2 | em parte | o 4 da H2 é de uma comparação "previsível" (A14) |
| 4.6 | Robustez | 3 / 4 / 2 | sim | o 4 da H2 é anterior ao 52e; segue válido para D_UF |
| 4.6 | Precisão | 2 / 4 (ou 2) / 3 | em parte | a soma usa o 4 (A14) |
| 4.6 | Clareza | 4 / 3 / 3 | sim, isolada | contradiz a §4.7 sobre o gráfico (A5) |
| 4.6 | Ligação com a teoria | 5 / 4 / 2 | em parte | "mostra" exagera (A13); a H3 do deck não é a H3 do modelo micro, e a nota 2 é coerente com isso |
| 4.6 | Relevância | 5 / 3 / 3 | sim | — |
| 4.7 | Mensagem numa frase | 2 / 5 / 3 | sim | — |
| 4.7 | Gráfico fala sozinho | 3 / 5 / 3 | não está demonstrado | se o gráfico é o descritivo dos 79%, ele não é a H2 (A5) |
| 4.7 | Diz algo que acontece | 1 / 4 / 3 | em parte | H3 com 3 e "conclusão central inconclusiva" na frase de 10 s é tenso |
| 4.7 | Poucas ressalvas | 1 / 3 / 2 | não | contagem assimétrica (A5) |
| 4.7 | Método para leigo | 4 / 3 / 3 | sim | — |
| 4.7 | Resposta firme à pergunta dura | 2 / 4 / 2 | em parte | a resposta firme da H2 é uma concessão ("não é causal"; "foi depois dos dados") |

As somas estão certas: 28, 26 e 19 na §4.6 e 13, 24 e 16 na §4.7. A ordem H2 > H1 da §4.7 se mantém mesmo corrigindo
a contagem de ressalvas (H2 cairia de 24 para 22). Ela é, portanto, uma leitura possível, desde que dita como
critério de clareza e não como força de evidência.

## 3. Tabela de conferência

"Confere" quer dizer igual à fonte nas casas mostradas. "Desatualizado" quer dizer igual à fonte citada, mas
superado por versão corrigida e auditada.

| # | Afirmação no doc 65 | Número | Fonte | Confere? |
|---|---|---|---|---|
| 1 | HI-1 em 0,300 (§0, §1.3) | −3,7 p.p. [−21,3; +13,9]; p 0,682; Holm 1,000; média 56,1% | 57n §3; `HI_estimativas.csv` (−0,0368 [−0,2126; +0,1390]) | sim |
| 2 | HI-1 em 0,400 | −2,3 p.p. [−24,0; +19,4]; p 0,835; Holm 1,000; 59,0% | 57n §3; CSV | sim |
| 3 | HI-2 em 0,300 | −1,13 [−2,15; −0,10]; p 0,032; Holm 0,126; média 2,77 | 57n §3; CSV (p 0,0316; Holm 0,1265) | sim |
| 4 | HI-2 em 0,400 | −0,16 [−0,99; +0,68]; p 0,713; Holm 1,000; 2,01 | 57n §3; CSV | sim |
| 5 | MDE da HI-1 | 25,1 e 31,0 p.p. ("25 a 31") | 57n §3; CSV `mde` 0,251 e 0,310 | sim |
| 6 | MDE da HI-2 | 1,47 e 1,19 | 57n §3 | sim |
| 7 | TOST inconclusivo em 3 de 4; HI-1 em 0,300 IC 90% [−18,4; +11,1] | — | 57n §4, HI-s7; CSV `leitura_tost` (só a HI-2 em 0,300 dá `SO_AUMENTO`) | sim |
| 8 | HI-2 em 0,300 descarta aumento ≥ 0,69 | IC 90% [−1,99; −0,26] | 57n §4, HI-s7 | sim |
| 9 | IC honesto "centenas de p.p." | [−930,0; +922,6] | 57n §4, HI-s8 | sim |
| 10 | Regra *sharp* | 368/368; 454/454; 404/404 | 37 §2; `CLAUDE.md`; auditoria 16 | sim |
| 11 | Densidade | 0,93 [0,40; 2,16]; 0,61 [0,29; 1,30] | 37 §2; 44 §5.4 | sim |
| 12 | Balanço em 0,300 | capital −29,9 p.p. [−57,1; −2,8]; Nordeste −47,7 [−82,6; −12,8]; especialistas no resto da região +10,54 [+3,54; +17,54] | 57r §3; 57o §3 | sim |
| 13 | Balanço em 0,400 | +6,21 [+0,71; +11,70] | 57r §3 | sim |
| 14 | Lee | 0,300: Y1 [−7,4; +9,6], Y2 [−0,05; +0,12]; 0,400: Y1 [−13,0; +16,2], Y2 [−0,15; +0,16]; com a reta, [−0,19; −0,01] | 57t §1 | sim |
| 15 | Placebo S-b | −5,64 [−9,92; −1,37] | 49 §9 | sim |
| 16 | Subida antes de 0,300 | +36,1 p.p. por 0,100 [+7,4; +64,7] | 57m §1 | sim |
| 17 | Empilhado (TOST) | A3 IC 90% [−11,6; +1,9]; N1 [−1,33; −0,18] contra ±0,54 | 57j §2.1 | sim |
| 18 | Referência da literatura | +10 p.p. (protocolo); Dal Bó et al. +15 p.p. | 57j §1; 44 §6 | sim |
| 19 | Medidas antigas | A3 −8,4 [−18,5; +1,7] e −1,3 [−14,0; +11,3]; N1 −1,45 [−2,67; −0,22] e −0,14 [−0,82; +0,54] | 57n §2.1 | sim |
| 20 | Por ciclo (HI-1 em 0,300) | +0,8 / −21,0 / +7,2 p.p. | 57n §4, HI-s1 | sim |
| 21 | Janelas (HI-2 em 0,300) | −0,50 [−1,67; +0,68]; −0,74 [−1,67; +0,20] | 57n §4, HI-s8 | sim |
| 22 | HI-s3 | −2,76 [−5,00; −0,51]; q 0,819 | 57n §4 | sim |
| 23 | Capital, UF, sem capitais | HI-2 −0,83 / −0,32 / −0,30; HI-1 +2,6 / +4,0 / +2,9 | 57o §1 e §4 | sim |
| 24 | L+M | HI-2 −1,11 → −0,25; HI-1 −4,1 → +3,6 | 57r §1 e §4.1 | sim |
| 25 | PM-1 | +4,7 [−6,5; +16,0]; +5,5 [−9,7; +20,7]; +0,10 [−0,01; +0,22], Holm 0,636; +0,07; gulosa −0,6 | 57s §1; 57r §2.1 | sim |
| 26 | Porte (τ₁) | +1,67 [−0,27; +3,60]; Holm 0,366 | 57u §1 | sim |
| 27 | Acaso | 33,3% e 33,5%; placebo com p ≥ 0,250 | 57l §1 | sim |
| 28 | Funil | −10,8 p.p. [−28,2; +6,7] | 57l §1 | sim |
| 29 | D_UF | 1,98 [1,56; 2,40]; p < 0,001 | 57i §3 e §4; `P1h_magnitudes.csv` (1,978) | sim |
| 30 | D_UF corrigido | 1,94 [1,48; 2,40] | 57p §1; `VC_estimativas.csv` (1,942) | sim |
| 31 | 10·β e θ_UF | 0,42 [−0,03; 0,87]; 2,40 [2,28; 2,53] | 57i §4; CSV (0,424; 2,402) | sim, mas pré-correção (corrigidos: θ_UF 2,395, 57p §4.3; β 0,0453) |
| 32 | β da bolsa (§0, §2.3) | 0,0424 [−0,0027; 0,0874]; p 0,065 | 57a §4 | **desatualizado**: o de referência é 0,0453 [−0,0041; 0,0947], p 0,072 (57p §1). Corrigido na §0 |
| 33 | β corrigido (§2.2) | 0,0424 → 0,0453; Holm 0,065 → 0,072 | 57p §1 | sim |
| 34 | K5 (§2.3, §4.5) | 112 km [−9; 233] | 57i §3 e §4 | **desatualizado**: o corrigido é 119 km [−12; 250] (57v §5.6; `VL_estimativas.csv`, VL-5, 118,8). Corrigido |
| 35 | D_UF M2 / M4 / M7; M5 por ciclo | 1,18 / 1,73 / 2,07; 2,34 / 1,31 / 2,37 | 57i §3 | sim |
| 36 | M5 do ciclo 2 com 13/02 | 1,19 [0,51; 1,86] | 57p §4.2 | sim |
| 37 | M2 / M4 / M7 com 13/02 | 1,16 / 1,70 / 2,03 | 57v §5.6 | sim; "auditoria pendente" desatualizado (auditoria 46). Corrigido |
| 38 | IIA (M9) | λ 0,449 [0,341; 0,556]; β 0,0434 | 57a §8 e §4 | sim |
| 39 | β por ciclo; Wald | +0,0132; +0,1064 [+0,0405; +0,1722]; −0,0004; p 0,058 | 57a §7 | sim |
| 40 | Ligação ao G1 | 5.421 de 5.714; β 0,0662 | 57a §2 e §4 | sim |
| 41 | P1g | +0,218 [−0,015; +0,451]; −0,457 [−1,031; +0,117] | 57a §9 | sim |
| 42 | Horas do médico | +6,6 [+5,4; +7,8]; posto +8,7 [+7,9; +9,5]; fora −2,1 [−3,2; −1,0] | 57d §5; `P4_estimativas.csv` (6,604; 8,703; −2,099) | sim |
| 43 | Já tinham vínculo no município | 51,0% [48,4%; 53,7%] | 57d §3; CSV (0,5104) | sim |
| 44 | Compensado fora | 26,3% [17,4%; 35,4%] | 57d §9 | sim |
| 45 | Já presentes: horas no posto | +6,2 [+5,0; +7,4] | 57d §6 | sim |
| 46 | Sensibilidades do médico | +6,1 e +7,5 | 57d §10 | sim |
| 47 | Pré e ruptura (médico) | p 0,310; M̄ 1,30; posto p 0,001, M̄ 1,90; fora M̄ 0,78 | 57d §5; 57h §2.2 | sim |
| 48 | Nota de corte (P4-CA) | +7,91 [−0,63; +16,45]; Holm 0,162; 98 e 30 | 57h §3.2 | sim |
| 49 | Município pela chegada | B1/B2/B3/B5 +0,40 / +7,00 / +1,88 / −0,13; θ(−6) −0,28 [−0,52; −0,04]; M̄ = 0 | 57k §4 e §5 | sim |
| 50 | Município no corte | B1 −0,23 [−1,51; +1,05] e −0,46 [−1,86; +0,94]; Holm 1,000; B3 −4,75 [−19,26; +9,76] | 57q §4 e §5.1 | sim |
| 51 | Primeiro estágio no corte | +5,0 p.p. [−20,1; +30,1]; F 0,2 e 0,0; pré p de 0,063 a 0,707 | 57q §4 | sim |
| 52 | DiRD (P2) | +0,083 [−0,309; +0,476]; Holm 0,851 | 44 §4 | sim |
| 53 | PM-2 ΔB1 | +0,06 | 57s §1 | sim |
| 54 | 48h: pares (§4.8) | 25 e 29 | 57w §1 e §4; `PL_estimativas.csv` | sim |
| 55 | 48h: diferença mínima detectável | "cerca de 24 a 29 p.p." | 57w §1 ("O preço"); auditoria 47, A1 (29 e 24 p.p.); CSV EP 0,0987 e 0,0834 | sim |
| 56 | 48h: HI-2 em 0,300 com UF e raio | −1,15 → −0,62 (não está no doc 65) | 57w §6; CSV (−1,145 → −0,620 [−1,671; +0,432]) | número correto na fonte; no doc 65 só a frase "a queda some", **exagerada** (A3) |
| 57 | 52e (não estão no doc 65, que só descreve em palavras) | 1,47 [1,15; 1,89]; 1,90 [1,30; 2,78]; 1,28 [0,95; 1,72]; 75 km [28; 122] | 57x §4.1 e §4.3; `VL_estimativas.csv` (1,4702; 1,9045; 1,2798; 74,9) | números corretos na fonte; as frases da §4.8 ("pesa mais", "pesa o mesmo", "IC contém 1") são fiéis à auditoria 48 (A1) |
| 58 | 52e: Holm | "passa a se distinguir de zero depois do Holm" | 57x §4.1 (Holm 0,005) | sim, mas é Holm do adendo pós-resultado (A4) |
| 59 | 79% na mesma UF (§4.7) | 79% | `numeros_banca2.json`, `ESC_UF` 0,7917 (G1, 5.425); doc 02 da banca 2 | o número confere; **sem fonte no doc 65**. Corrigido |
| 60 | Somas das notas | 28 / 26 / 19; 13 / 24 / 16 | aritmética das §4.6 e §4.7 | sim |

## 4. Afirmações qualitativas

| Afirmação | Se sustenta? | Base |
|---|---|---|
| "A H2 foi formulada depois de ver os coeficientes" | **sim** | 52b, cabeçalho ("a resposta da linha primária é previsível"); 57i, cabeçalho; auditoria 31 §1 |
| "A H1 vem do modelo da banca 1" | **sim**, como hipótese; a especificação principal (48b) é pós-resultado, e o doc 65 diz isso | modelo micro §4.2 (H1: ∂Pr(aceitar)/∂B > 0), commit de 16/09; 57n, cabeçalho |
| "O sinal negativo vinha da UF" (§4.8) | **exagerada** | A3: com só a UF, o ponto cai à metade; capital, L+M e pareamento também mexem; a queda nunca passou no Holm |
| "A bolsa muda qual vaga, não quantas" (§4.8) | **"não quantas" não se sustenta**; "qual vaga" vale como deslocamento da escolha pelo **pacote do corte**, condicional a se candidatar, com a primária pré-registrada sem rejeitar zero | A2, A4; 44 §7.3 (proposta, "sem expansão líquida detectável") |
| "Não aparece mais médico vindo de outra UF" | **não está no doc 65**; se for dita, em 0,400 é inconclusivo, não ausência | auditoria 47, A3; 57w §7 |
| "A H2 ganha força" (§4.8) | **não**, para D_UF | A4 |
| "Nos ciclos 1–3 a bolsa pesa mais do que na base; no ciclo 2, o mesmo; no local, IC contém 1" (§4.8) | **sim** | 57x §1; auditoria 48, A1 |
| "Nenhuma estimativa mudou nas auditorias 47 e 48" (§4.8) | **sim** | auditorias 47 e 48, veredito |
| "Em 0,300 não muda nenhum outro incentivo individual" (§1.1, §1.5) | **sim** | auditoria 35, resposta curta |
| "Em 0,300 mudam emendas e custeio da APS e da MAC (+20%)" (§1.1) | **sim** (PAP e MAC) | auditoria 18, tabela de 0,300 |
| "O deck ainda diz 'reestimação em curso'" (§4.4, item 6) | **sim**, ainda vale | doc 04 da banca 2, notas da H2 |
| "Balanço: passam, salvo capitais subestima" (§4.4, item 5) | **sim**, ainda vale | doc 04 da banca 2, tabela de Identificação; 57r §3 |

## 5. Linguagem causal

- **Pacote do corte.** O cabeçalho e as §1 a §3 do doc 65 usam bem "pacote do corte". A §4.7 e a §4.8 o deixam cair:
  - "a bolsa maior faz a vaga ser escolhida mais vezes" (§4.8);
  - "a bolsa muda qual vaga" (§4.8);
  - "onde a bolsa é R$ 5 mil maior" (§4.7). Esta tem o pacote na lista de ressalvas.

  A forma fiel é "a vaga do lado de bolsa maior (pacote do corte) é mais escolhida como 1ª opção".
- **Preferência revelada.** Usada corretamente nas §2 e §4.3. A §4.6 diz "mostra que o custo individual domina"
  (A13).
- **Associação.** A H3 está toda como associação ou descrição. Correto.
- **Pós-resultado.** Há dois problemas:
  - o 48h e o 52e são pós-resultado (`ADENDO_48H_POS_RESULTADO`, `ADENDO_52E_POS_RESULTADO`), e a §4.8 não diz isso;
  - a §4.8 usa a significância do VL-1 para reforçar uma conclusão, quando a primária pré-registrada (P1a) não
    rejeita (A4).
- **Nulo.** A §4.2 ("não se move"), a §4.7 ("não encheu") e a §4.8 ("nenhuma diferença"; "não quantas") escrevem
  como nulo o que é não detecção (A2, A9, A11).

## 6. Regra do `CLAUDE.md` sobre números

- Todo número de resultado do doc 65 remete a doc gerado por script a partir de `output/`, e os conferidos contra o
  CSV batem.
- A única exceção era o **79%**, sem fonte no doc. Ele vem de `output/` por script, e a fonte foi acrescentada.
- As notas por critério e as somas são **julgamento**, não dado, e o doc diz isso ("julgamento técnico").
- O doc 65 é escrito à mão e não tem teste que o confira contra `output/` (A15). Para uso em slide, os números devem
  vir de `numeros_banca2.json` ou dos docs 57* gerados, nunca do doc 65.

## 7. O que mudou nesta auditoria

- **`docs/06_execucao/65_avaliacao_forca_hipoteses.md`**, com nota datada "auditoria 50, 27/10/2026" em cada ponto:
  - nota de **estado atual** no topo, com a seção mais recente, as divergências e o que não se pode dizer;
  - na §0, o β corrigido ao lado do antigo;
  - nas tabelas 2.2 e 2.4 e na §5, "auditoria pendente" → auditoria 46;
  - na tabela 2.3 e na §4.5, os km corrigidos (119 [−12; 250]);
  - na §4.7, a fonte dos 79%;
  - na §4.8, a descrição do pareamento do 48h, "não se detecta diferença" e os números da UF no lugar de "a queda
    some".

  A opinião das §0, §4.4, §4.6, §4.7 e §4.8 **não foi reescrita**.
- **`docs/00_registro_mudancas.md`:** entrada desta auditoria.
- **Fora de escopo, mas registrado:** o doc 05 da banca 2 (§2.16, última linha) resume o doc 65 só com a
  recomendação da H1. Quando o autor escolher, essa linha deve ser atualizada.
