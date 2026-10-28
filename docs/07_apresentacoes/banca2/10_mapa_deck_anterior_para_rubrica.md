# 10. Mapa do deck anterior (8901dea) para o deck revisto pela rubrica

> **Data:** 27/10/2026, véspera da banca 2.<br>
> **Mudança de 28/10/2026 (dia da banca):** a hipótese passou a ser só bolsa → 1ª opção, comparando vagas da mesma UF, e nada da origem é resultado. **O deck vigente está na [seção 6](#6-mudança-de-28102026-dia-da-banca-a-hipótese-é-só-bolsa--1ª-opção-dentro-da-mesma-uf)**; as seções 0 a 5 descrevem a passagem de `8901dea` para o deck de 27/10/2026 (`33d15d9`) e ficam como registro.<br>
> **Para quem é:** o grupo, que está montando outra apresentação a partir do deck que estava na `main` (commit
> `8901dea`, 11 slides no corpo e 2 no apêndice, auditado na [auditoria 53](../../auditorias/53_auditoria_deck_H2.md))
> e vai adaptá-la ao deck novo.<br>
> **Pedido do autor:** facilitar a adaptação: correspondência slide a slide, o texto exato da tela dos slides novos
> ou alterados, os números que mudaram de lugar ou de redação e um checklist do que acrescentar.<br>
> **Regra:** nenhum número aparece só aqui. Todos vêm de `output/apresentacao_banca2/numeros_banca2.json` (código
> entre parênteses) ou de `output/`; o texto da tela é copiado do [doc 04](04_conteudo_deck_curto.md), que é a fonte
> da verdade, e `tests/test_deck_curto_banca2.py` confere que cada linha da tela está aqui.<br>
> **Estatuto:** regra de apresentação. Nada foi reestimado; nenhuma conclusão mudou.<br>
> **Revisão da [auditoria 55](../../auditorias/55_auditoria_deck_rubrica.md) (27/10/2026, noite):** seis linhas da
> tela e o roteiro de cinco slides mudaram de redação, sem número novo; o que mudou desde a primeira versão deste mapa
> está na seção 5. Quem já copiou o texto da tela deve conferir essa seção.

## 0. Onde estão os dois decks

| Versão | Arquivo | SHA-256 |
|---|---|---|
| anterior (`8901dea`, auditoria 53) | `output/apresentacao_banca2/versoes/deck_banca2_curto_8901dea.pdf`, cópia extraída do commit com `git show`, sem regerar | `66fa8369fbc68eb23456a103a9585d90c3935a2fb913e423f8cb9053a20c66df` |
| nova (rubrica e 7 minutos) | `output/apresentacao_banca2/deck_banca2_curto.pdf` e `.pptx` | ver `manifesto_deck_banca2_curto.json` |

O hash da cópia anterior também fica no manifesto do deck curto (`versao_anterior`). O conteúdo anterior continua no
histórico do Git (`git show 8901dea:docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md`).

## 1. Correspondência slide a slide

O número da coluna "Critério" é o da rubrica da banca: 1 slides e narrativa; 2 apresentador; 3 base de dados; 4
análise descritiva; 5 modelo econométrico; 6 interpretação; 7 robustez; 8 conclusões; 9 limitações.

| Anterior | Título anterior | Novo | Título novo | O que aconteceu | Critério e motivo |
|---|---|---|---|---|---|
| 1 | Hipótese: a origem pesa mais que a bolsa na escolha | 1 | Pergunta e hipótese: origem ou bolsa na escolha? | alterado: o título vira a pergunta | 8 (conclusões: a Conclusão retoma a mesma pergunta) e 1 (narrativa: a história abre pela pergunta) |
| 2 | Dados: as variáveis e de onde vêm | 2 | Dados e amostra: de onde vêm e quem entra no modelo | fundido com o 3 | 3 (base de dados): fontes, variáveis, **unidade de observação** e **construção da amostra** num slide só |
| 3 | Os três ciclos em números | 2 | Dados e amostra: de onde vêm e quem entra no modelo | fundido no 2 (o funil por ciclo substitui a tabela de contagens) | 3 (base de dados): o funil mostra quem sai em cada etapa e por quê |
| 4 | A bolsa é função exata do IVS: a regra é sharp | 3 | A bolsa é função exata do IVS: a regra é sharp | mantido (só o roteiro de fala nas notas) | 4 (descritiva): a regra que gera a variação da bolsa |
| 5 | Onde escolhem: perto de onde já trabalham | 4 | Onde escolhem: perto de onde já trabalham | alterado: ganha a linha "Para a pergunta" | 4 (descritiva): o gráfico interpretado e ligado à pergunta |
| 6 | Metodologia: logit condicional da 1ª opção | 5 | Modelo: logit condicional da 1ª opção | alterado: "Por quê", "Bolsa" e "Teste" no lugar de "Comparação" e "Teste" | 5 (modelo): apresenta e **justifica** o logit condicional e diz qual é o teste |
| 7 | Identificação: as premissas e o nosso caso | 6 | Identificação: as premissas e o nosso caso | alterado: enxuto (5 linhas); origem e pós-resultado vão para Limitações; entra o conjunto de escolha, como suposto | 5 (modelo) e 9 (limitações): premissas aqui, limitações com implicação no slide 11 |
| 8 | Teste central: a origem pesa mais que toda a bolsa | 7 | Teste central: a origem pesa mais que toda a bolsa | alterado: ganha a leitura do coeficiente em linguagem simples | 6 (interpretação): o que 11,0 e 1,57 querem dizer |
| 9 | Dentro da mesma UF, a vaga de bolsa maior é preferida | 8 | Dentro da mesma UF, a vaga de bolsa maior é preferida | alterado: a linha de km vira a leitura do coeficiente (1,47 vez e 75 km) | 6 (interpretação) |
| 10 | Robustez: a origem pesa mais em todos os ciclos | 9 | Robustez: o que se mantém e o que não se mantém | alterado: título e linhas "Mantém" / "Não se mantém"; cautela encurtada | 7 (robustez): o que se mantém e o que não se mantém em especificações alternativas |
| 11 | Discussão: um incentivo limitado | 10 | Conclusão: a origem pesa mais que toda a bolsa? Sim | alterado: "Discussão" vira "Conclusão"; a teoria fica no 3º ponto | 8 (conclusões): retoma a pergunta e sintetiza em três pontos |
| — | — | 11 | Limitações e o que cada uma implica | novo | 9 (limitações): cada limitação seguida da sua implicação |
| 12 | Apêndice · O fato: sem aumento detectado no corte | 12 | Apêndice · O fato: sem aumento detectado no corte | mantido (apêndice, não apresentado) | — |
| 13 | Apêndice · H3: oferta, numa frase | 13 | Apêndice · H3: oferta, numa frase | mantido (apêndice, não apresentado) | — |

Em todos os slides do corpo, as notas do apresentador passaram a abrir pelo **roteiro de fala** com o tempo-alvo
(critério 2); o roteiro inteiro está no [doc 09](09_roteiro_fala_7min.md). O apêndice não é apresentado.

## 2. Texto exato da tela dos slides novos ou alterados

Copie daqui. "Linha" é uma linha curta da tela; "Cautela" é a caixa verde-clara. As figuras estão em `output/` e são
geradas por `scripts/apresentacao/gerar_figuras_banca2.py`; não as redesenhe. O slide 3 (regra *sharp*) e o
apêndice não mudaram na tela; estão aqui para o deck ficar completo.

### Slide 1. Pergunta e hipótese: origem ou bolsa na escolha?

Seção: Hipótese. Tempo de fala: 35 s.

- **Linha:** Hipótese médico escolhe perto de onde trabalha; bolsa muda qual vaga, mas pesa menos que a origem
- **Linha:** Motivação no corte, preenchimento sem aumento detectado
- **Cautela (caixa verde-clara):** Formulada após ver os dados.
- **Formato:** cada linha é uma caixa, com o rótulo em negrito à esquerda.

### Slide 2. Dados e amostra: de onde vêm e quem entra no modelo

Seção: Dados. Tempo de fala: 50 s.

- **Figura:** `output/apresentacao_banca2/curto_dados_amostra.png`
- **Linha:** Unidade: candidato × vaga do seu curso e ciclo; y = 1 na 1ª opção.
- **Linha:** No modelo: 5.421 candidatos e 932.577 pares candidato × vaga.

### Slide 3. A bolsa é função exata do IVS: a regra é sharp

Seção: Análise descritiva. Tempo de fala: 25 s.

- **Figura:** `output/apresentacao_banca2/regra_bolsa_ivs_oficial.png`
- **Linha:** Como ler: um ponto por município do ciclo 1; a bolsa salta nos cortes.
- **Linha:** Ciclos 1 e 2: reproduz 368/368 e 454/454 municípios.

### Slide 4. Onde escolhem: perto de onde já trabalham

Seção: Análise descritiva. Tempo de fala: 35 s.

- **Figura:** `output/apresentacao_banca2/exp_escolha_origem.png`
- **Linha:** 79% põem a 1ª opção na UF de origem; mediana: 51 km (descritivo).
- **Linha:** Para a pergunta: a maioria fica perto; quanto pesa a bolsa?

### Slide 5. Modelo: logit condicional da 1ª opção

Seção: Metodologia. Tempo de fala: 45 s.

- **Linha:** U = β·bolsa + γ·distância + θ·origem; P(j) = e^Uj/Σe^U (equação formal na tela desde 27/10/2026, para o critério "Modelo" da rubrica)
- **Linha:** Por quê escolha entre vagas; candidato comparado consigo mesmo
- **Linha:** Bolsa muda pela regra do IVS
- **Linha:** Teste D_UF = θ − 10β > zero; cluster por conjunto
- **Formato:** a 1ª linha é a equação em palavras, numa faixa verde-escura; as outras, com rótulo à esquerda.

### Slide 6. Identificação: as premissas e o nosso caso

Seção: Identificação. Tempo de fala: 30 s.

- **Tabela:**

  | Premissa | Aderência |
  |---|---|
  | Bolsa por regra | sharp: 368/368, 454/454 |
  | Só a bolsa? | não: pacote do corte |
  | IIA | em parte; bolsa estável |
  | Localização | par de UFs fixado |
  | Conjunto | suposto: todas vistas |


### Slide 7. Teste central: a origem pesa mais que toda a bolsa

Seção: Resultados. Tempo de fala: 50 s.

- **Figura:** `output/apresentacao_banca2/curto_origem_bolsa.png`
- **Linha:** Origem − bolsa: 1,94 [1,48; 2,40] em log-chance; p < 0,001.
- **Linha:** UF de origem vs. outra UF: chance ×11,0; toda a bolsa: ×1,57 (IC contém 1).
- **Cautela (caixa verde-clara):** Origem é preferência revelada, não causa.

### Slide 8. Dentro da mesma UF, a vaga de bolsa maior é preferida

Seção: Resultados. Tempo de fala: 40 s.

- **Figura:** `output/apresentacao_banca2/curto_bolsa_mesma_uf.png`
- **Linha:** Na mesma UF, +R$ 5 mil: chance ×1,47; vale 75 km a menos.
- **Cautela (caixa verde-clara):** Adendo pós-resultado; pré-registrado, sem fixar a UF: p 0,072.

### Slide 9. Robustez: o que se mantém e o que não se mantém

Seção: Robustez. Tempo de fala: 40 s.

- **Figura:** `output/apresentacao_banca2/curto_robustez_escolha.png`
- **Linha:** Mantém: origem pesa mais que toda a bolsa nos três ciclos.
- **Linha:** Não se mantém: peso da bolsa, forte só no ciclo 2; perto do corte, inconclusivo.
- **Cautela (caixa verde-clara):** Pré-registrado: IC contém 1.

### Slide 10. Conclusão: a origem pesa mais que toda a bolsa? Sim

Seção: Discussão. Tempo de fala: 30 s.

- **Linha:** Origem pesa mais que toda a bolsa, nos três ciclos
- **Linha:** Bolsa muda qual vaga, na mesma UF (adendo)
- **Linha:** Teoria os dados sugerem incentivo limitado (pacote do corte)
- **Formato:** cada linha é uma caixa, com o rótulo em negrito à esquerda.

### Slide 11. Limitações e o que cada uma implica

Seção: Discussão. Tempo de fala: 40 s.

- **Tabela:**

  | Limitação | Implicação |
  |---|---|
  | Pós-resultado | exploratório |
  | Preferência revelada | não é causa |
  | Só candidatos | sem margem extensiva |
  | Pacote do corte | bolsa não isolada |
  | Só ciclo 2 | não generalizar |
  | Origem = CNES | não é residência |


### Slide 12. Apêndice · O fato: sem aumento detectado no corte

Seção: Apêndice.

- **Figura:** `output/apresentacao_banca2/curto_fato.png`
- **Linha:** O negativo em 0,300 nunca passou no Holm; anda junto com a UF.
- **Cautela (caixa verde-clara):** Pacote do corte; só detectaria saltos grandes.

### Slide 13. Apêndice · H3: oferta, numa frase

Seção: Apêndice.

- **Linha:** O médico que chega cadastra +6,6 h/sem; metade já estava lá
- **Cautela (caixa verde-clara):** Associação; vínculo cadastrado não é presença.

## 3. Números que mudaram de lugar ou de redação

Nenhum número novo de estimação. Os números novos na tela são contagens da amostra, lidas do
`output/rdd_bolsa/P1_resumo.json` (códigos `AM_*`).

| Número | Código | Antes (8901dea) | Agora |
|---|---|---|---|
| 1.295 · 1.547 · 2.293 células | `D_C*_CEL` | tela do slide 3 ("Células") | saíram da tela; o modelo usa 5.125 vagas nos conjuntos de escolha (`AM_VAGAS`), dito na figura do slide 2 |
| 993 · 2.140 · 2.581 | `D_C*_CAND1` = `AM_C*_R1` | slide 3, "Candidatos, 1ª opção" | 1ª linha do funil (slide 2), com total 5.714 (`AM_TOT_R1`) |
| 915 · 2.032 · 2.474 | `D_C*_P1` | slide 3, rotulado "Com origem" | rotulado **"No modelo"** (total 5.421, `M1_N`); "Com município de origem" agora é 918 · 2.033 · 2.474 (`AM_C*_ORI`, total 5.425 = `ESC_N`): a diferença são 3 · 1 · 0 candidatos sem região de saúde na tabela oficial |
| 938 · 2.063 · 2.512 ligados ao CNES | `AM_C*_LIG` | — | funil do slide 2 (exclusões: 55 · 77 · 69 sem ligação, `AM_C*_NLIG`; 20 · 30 · 38 sem vínculo médico antes da inscrição, `AM_C*_SVIN`) |
| 932.577 pares candidato × vaga; 56 conjuntos | `AM_PARES`, `AM_CONJ` | só no doc 66 | tela do slide 2 (pares) e figura (conjuntos): é a unidade de observação |
| ×11,0 e ×1,57 | `VC_THETAX_EST`, `VC_B10X_EST` | só na figura e nas notas do slide 8 | também na linha de leitura do slide 7: "UF de origem vs. outra UF: chance ×11,0; toda a bolsa: ×1,57 (IC contém 1)" |
| 1,47 | `VL1_EMP_RC` | só na figura do slide 9 | também na linha do slide 8: "chance ×1,47; vale 75 km a menos" |
| 75 km | `VL1_EMP_K5` | "pesam como 75 km a menos de distância" | "vale 75 km a menos" (os 119 km do M1 continuam só nas notas) |
| p 0,072 | `VC_B_HOLM` | cautela do slide 9 (tela) e notas do slide 7, na linha "Hipótese: pós-resultado" | cautela do slide 8 (igual) e notas do slide 6; "pós-resultado" passou para a tabela de Limitações |
| 1,19 e 2,37 | `VC_DUF_C2_EST`, `VC_DUF_C3_EST` | figura e notas da robustez | também no roteiro de fala do slide 9 |

Redação que mudou na tela, sem número: a equação em palavras perdeu o "(UF, região, município)" depois de "origem"
(as três dummies continuam no modelo e nas notas); "não: pacote" virou "não: pacote do corte"; a cautela da robustez
"Pré-registrado: IC contém 1; variantes do adendo: mesma leitura" virou "Pré-registrado: IC contém 1." (a segunda
metade foi para a fala); a linha "Comparação: o candidato consigo mesmo, entre vagas do seu curso" virou "Por quê:
escolha entre vagas; candidato comparado consigo mesmo"; o "Teste: origem pesa mais que toda a bolsa" virou "D_UF =
origem − bolsa > zero; cluster por conjunto". As frases obrigatórias das auditorias 50, 52 e 53 continuam: "não
detectamos aumento", o teste central é o D_UF, o VL-1 compara vagas da mesma UF (a de origem ou outra) e é
pós-resultado, o pré-registrado tem IC que contém 1, "os dados sugerem", pacote do corte, preferência revelada,
condicional a se candidatar, e na tela os 75 km, não os 119.

## 4. Checklist: o que o grupo precisa acrescentar para cobrir a rubrica

- [ ] **Narrativa** (critério 1): o slide 1 abre com a pergunta no título ("origem ou bolsa na escolha?"), e a
  Conclusão (slide 10) a retoma com a resposta; o rodapé com as oito seções; até 30 palavras por slide.
- [ ] **Unidade de observação** (critério 3): "candidato × vaga do seu curso e ciclo; y = 1 na 1ª opção", na tela.
- [ ] **Funil da amostra por ciclo** (critério 3): a figura `output/apresentacao_banca2/curto_dados_amostra.png`, com
  fontes e variáveis à esquerda; no lugar dos antigos slides "Dados" e "Os três ciclos em números".
- [ ] **Descritiva ligada à pergunta** (critério 4): "Como ler" na regra *sharp* (slide 3) e a linha "Para a
  pergunta" no slide 4; dizer que é descritivo.
- [ ] **Justificativa do modelo** (critério 5): escolha discreta entre vagas; cada candidato comparado consigo mesmo
  (o que é dele sai da conta); a bolsa varia entre vagas pela regra do IVS; teste D_UF > zero, unilateral, com
  erro-padrão agrupado por conjunto de escolha.
- [ ] **Interpretação dos coeficientes** (critério 6): a linha de leitura do slide 7 ("UF de origem vs. outra UF:
  chance ×11,0; toda a bolsa: ×1,57 (IC contém 1)") e a do slide 8 ("chance ×1,47; vale 75 km a menos"). Na fala,
  sempre com o termo de comparação: "entre duas vagas iguais no resto, inclusive na distância". 11,0 é razão de
  chances entre duas vagas, não "a probabilidade de uma vaga multiplicada por 11".
- [ ] **Robustez dita como "mantém / não se mantém"** (critério 7).
- [ ] **Conclusão** (critério 8): slide próprio que retoma a pergunta do slide 1 e a responde em três pontos.
- [ ] **Limitações com implicações** (critério 9): a tabela do slide 11, com a implicação de cada uma dita na fala.
- [ ] **Roteiro de 7 minutos** (critério 2): o [doc 09](09_roteiro_fala_7min.md), com tempo por slide; ensaiar com
  cronômetro; o apêndice não é apresentado.
- [ ] **Perguntas prováveis** (critério 2): as três respostas curtas do doc 09.
- [ ] **Ressalvas na fala** (critérios 6 e 9): pós-resultado, preferência revelada, pacote do corte, condicional a
  se candidatar; "não detectamos aumento"; o teste central é o D_UF; o VL-1 compara vagas da mesma UF (a de origem
  ou outra) e é adendo; o pré-registrado tem IC que contém 1; na tela, 75 km, não os 119.
- [ ] **Não mexer** nos números nem redesenhar figuras: tudo sai de `output/` por script.

## 5. O que mudou na auditoria 55 (27/10/2026, noite)

Só redação; nenhum número, figura ou conclusão mudou. Quem já copiou a seção 2 troca:

| Slide | Antes (primeira versão deste mapa) | Agora | Por quê |
|---|---|---|---|
| 6 | Conjunto: "todas as vagas vistas" | "suposto: todas vistas" | é premissa que não se testa (doc 66, §5), não aderência verificada |
| 7 | "Na UF de origem, chance 11,0 vezes maior; toda a bolsa: 1,57 (IC contém 1)." | "UF de origem vs. outra UF: chance ×11,0; toda a bolsa: ×1,57 (IC contém 1)." | a razão de chances compara duas vagas; faltava contra o quê |
| 8 | "chance 1,47 vez maior" | "chance ×1,47" | mesma notação das figuras; "1,47 vez maior" é ambíguo (multiplica ou soma?) |
| 9 | "Mantém: a origem pesa mais que a bolsa…"; "Não se mantém: peso da bolsa: forte…" | "Mantém: origem pesa mais que toda a bolsa…"; "Não se mantém: peso da bolsa, forte…" | "toda a bolsa" é o que o D_UF testa; dois-pontos repetidos |
| 10 | título "Conclusão: a origem pesa mais que a bolsa? Sim" | "Conclusão: a origem pesa mais que toda a bolsa? Sim" | idem |
| 11 | Só ciclo 2: "bolsa instável" | "não generalizar" | é a implicação, não a descrição |
| roteiro 2, 3, 4, 7, 11 | mais números falados | menos números falados (ficam na tela); slide 7 com "entre duas vagas iguais no resto, inclusive na distância"; slide 11 com a implicação de cada limitação | caber nos 7 minutos; o número dito em voz alta vale várias palavras |
| roteiro 5 | "como idade, nota ou família" | "como idade ou nota" | a família tem lugar: a distância até ela varia entre vagas e não sai da conta |

## 6. Mudança de 28/10/2026 (dia da banca): a hipótese é só bolsa → 1ª opção, dentro da mesma UF

> **Decisão do autor (28/10/2026):** "a hipótese é simplesmente sobre o efeito bolsa → 1ª opção", com "só comparação
> entre municípios da mesma UF". Reforço do mesmo dia: "pode deixar TUDO na mesma UF. UF, origem etc. é tudo
> controle/pareamento".<br>
> **Para o grupo:** as seções 1 a 5 acima descrevem o deck de 27/10/2026 (commit `33d15d9`) e ficam só como registro.
> **O deck vigente é o desta seção.** Quem copiou o texto da tela do deck de 27/10 troca tudo pelo que está aqui.
> Nada foi reestimado para esta versão além do adendo 52g (ciclos 1 e 3 separados, doc 57z, auditoria pendente);
> os outros números são os mesmos, só mudaram de lugar.

### 6.1 O que muda, em uma frase

Antes, a hipótese comparava a origem com a bolsa ("a bolsa pesa menos que a origem"). Agora ela é só sobre a bolsa:
**comparando vagas da mesma UF, a vaga de bolsa maior tem mais chance de ser a 1ª opção**. A UF de origem, a UF da
vaga, a região de saúde, o município e a distância entram **só como controle e pareamento**. Nenhum slide, nem do
apêndice, interpreta o coeficiente da origem: saem o ×11,0, o D_UF e "a origem pesa mais".

### 6.2 Correspondência slide a slide (deck de 27/10 → deck de 28/10)

| 27/10 | Título em 27/10 | 28/10 | Título em 28/10 | O que aconteceu |
|---|---|---|---|---|
| 1 | Pergunta e hipótese: origem ou bolsa na escolha? | 1 | Pergunta e hipótese: a bolsa maior muda a 1ª opção? | alterado: a hipótese é só sobre a bolsa, dentro da mesma UF; "formulada após ver os dados" continua |
| 2 | Dados e amostra: de onde vêm e quem entra no modelo | 2 | Dados e amostra: de onde vêm e quem entra no modelo | mantido (fala um pouco mais curta) |
| 3 | A bolsa é função exata do IVS: a regra é sharp | 3 | A bolsa é função exata do IVS: a regra é sharp | mantido |
| 4 | Onde escolhem: perto de onde já trabalham | 4 | Onde escolhem: a maioria fica na própria UF | alterado: os 79% viram a **motivação para comparar dentro da UF**, não resultado |
| — | — | 5 | Descritivo: perto do corte, a bolsa maior é mais escolhida | novo: a F2 do doc 66, descritiva da hipótese |
| 5 | Modelo: logit condicional da 1ª opção | 6 | Modelo: logit condicional da 1ª opção | alterado: equação com o efeito fixo do par de UFs; teste β > zero |
| 6 | Identificação: as premissas e o nosso caso | 7 | Identificação: as premissas e o nosso caso | alterado: "Mantido fixo" e "Especificação: pós-resultado" no lugar de IIA e Localização |
| 7 | Teste central: a origem pesa mais que toda a bolsa | — | — | **saiu** (corpo e apêndice); o D_UF fica numa linha das notas do slide 11, para pergunta da banca |
| 8 | Dentro da mesma UF, a vaga de bolsa maior é preferida | 8 | Dentro da mesma UF, a vaga de bolsa maior é preferida | alterado: é o **resultado principal**; figura sem a linha do modelo base |
| 9 | Robustez: o que se mantém e o que não se mantém | 9 | Robustez: sempre comparando vagas da mesma UF | alterado: só variantes dentro da mesma UF, com o VL-1 por ciclo (adendo 52g) |
| 10 | Conclusão: a origem pesa mais que toda a bolsa? Sim | 10 | Conclusão: a bolsa maior aumenta a 1ª opção? Sim | alterado: responde a nova pergunta |
| 11 | Limitações e o que cada uma implica | 11 | Limitações e o que cada uma implica | alterado: entram "sem fixar UF" e "escolha ≠ preenchimento"; sai "preferência revelada" |
| 12 | Apêndice · O fato: sem aumento detectado no corte | 12 | Apêndice · O fato: pareando municípios da mesma UF | alterado: só a comparação de municípios pareados na mesma UF; sai a RDD sem controle |
| 13 | Apêndice · H3: oferta, numa frase | — | — | **saiu** |

### 6.3 Texto exato da tela (deck de 28/10)

Copie daqui. As figuras estão em `output/` e são geradas por script; não as redesenhe.

**Slide 1. Pergunta e hipótese: a bolsa maior muda a 1ª opção?** Seção: Hipótese. Tempo de fala: 35 s.
- Linha: Hipótese comparando vagas da mesma UF, a de bolsa maior tem mais chance de ser a 1ª opção
- Linha (cinza): Motivação no corte, preenchimento sem aumento detectado
- Cautela: Formulada após ver os dados.

**Slide 2. Dados e amostra: de onde vêm e quem entra no modelo** Seção: Dados. Tempo de fala: 45 s.
- Figura: `output/apresentacao_banca2/curto_dados_amostra.png`
- Linha: Unidade: candidato × vaga do seu curso e ciclo; y = 1 na 1ª opção.
- Linha: No modelo: 5.421 candidatos e 932.577 pares candidato × vaga.

**Slide 3. A bolsa é função exata do IVS: a regra é sharp** Seção: Análise descritiva. Tempo de fala: 25 s.
- Figura: `output/apresentacao_banca2/regra_bolsa_ivs_oficial.png`
- Linha: Como ler: um ponto por município do ciclo 1; a bolsa salta nos cortes.
- Linha: Ciclos 1 e 2: reproduz 368/368 e 454/454 municípios.

**Slide 4. Onde escolhem: a maioria fica na própria UF** Seção: Análise descritiva. Tempo de fala: 30 s.
- Figura: `output/apresentacao_banca2/exp_escolha_origem.png`
- Linha: 79% põem a 1ª opção na UF de origem; mediana: 51 km (descritivo).
- Linha: Por isso: comparamos só vagas da mesma UF.

**Slide 5. Descritivo: perto do corte, a bolsa maior é mais escolhida** Seção: Análise descritiva. Tempo de fala: 35 s.
- Figura: `output/rdd_bolsa/H2_figuras/H2_F2_mesma_uf_perto_do_corte.png` (F2 do doc 66)
- Linha: Bolsa maior: 52,5% das vagas, 60,8% das 1ªs opções.
- Linha: Quem: na UF de origem, a até 0,050 de um corte; 1.568 candidatos.
- Cautela: Descritivo: sem teste e sem controlar a distância.

**Slide 6. Modelo: logit condicional da 1ª opção** Seção: Metodologia. Tempo de fala: 35 s.
- Equação: U = β·bolsa + γ·distância + EF(UF origem × UF vaga) + …; P(j) = e^Uj/Σe^U
- Linha: Por quê candidato consigo mesmo, vagas da mesma UF
- Linha: Bolsa regra do IVS (sharp)
- Linha: Teste β > zero; cluster por conjunto

**Slide 7. Identificação: as premissas e o nosso caso** Seção: Identificação. Tempo de fala: 45 s.

| Premissa | Aderência |
|---|---|
| Bolsa por regra | sharp: 368/368, 454/454 |
| Mantido fixo | candidato, par de UFs, distância |
| Só a bolsa? | não: pacote do corte |
| Especificação | pós-resultado (adendo 52e) |
| Conjunto | suposto: todas vistas |

**Slide 8. Dentro da mesma UF, a vaga de bolsa maior é preferida** Seção: Resultados. Tempo de fala: 50 s.
- Figura: `output/apresentacao_banca2/curto_bolsa_mesma_uf.png` (só o VL-1, sem o modelo base)
- Linha: +R$ 5 mil: chance ×1,47 [1,15; 1,89].
- Linha: Leitura: por +R$ 5 mil, o médico aceita vaga 75 km mais longe.
- Cautela: Adendo pós-resultado; pré-registrado, sem fixar a UF: IC contém 1.
- O ×1,90 do ciclo 2 fica na figura (pedido do autor, 28/10: interpretação simples na tela, dentro de 30 palavras).

**Slide 9. Robustez: sempre comparando vagas da mesma UF** Seção: Robustez. Tempo de fala: 40 s.
- Figura: `output/apresentacao_banca2/curto_robustez_escolha.png`
- Linha: Mantém: distância em log; região de saúde × UF.
- Linha: Por ciclo: forte só no ciclo 2; nos ciclos 1 e 3 o IC contém 1.
- Linha: Perto do corte: inconclusivo.

**Slide 10. Conclusão: a bolsa maior aumenta a 1ª opção? Sim** Seção: Discussão. Tempo de fala: 35 s.
- Linha: Resposta sim, comparando vagas da mesma UF: chance ×1,47
- Linha: Força forte só no ciclo 2 (×1,90)
- Linha: Teoria os dados sugerem: bolsa compensa parte do custo do lugar

**Slide 11. Limitações e o que cada uma implica** Seção: Discussão. Tempo de fala: 45 s.

| Limitação | Implicação |
|---|---|
| Pós-resultado | exploratório |
| Sem fixar UF | IC contém 1 |
| Só candidatos | escolha ≠ preenchimento |
| Pacote do corte | bolsa não isolada |
| Só ciclo 2 | não generalizar |
| Origem = CNES | não é residência |

**Slide 12. Apêndice · O fato: pareando municípios da mesma UF** (não apresentado)
- Figura: `output/apresentacao_banca2/curto_fato_pareado.png`
- Linha: Sem aumento detectado do preenchimento nos dois cortes.
- Cautela: Pacote do corte; poucos pares.

### 6.4 Números que entram, saem ou mudam de lugar

| Número | Código | Em 27/10 | Em 28/10 |
|---|---|---|---|
| 1,47 [1,15; 1,89] e 1,90 [1,30; 2,78] | `VL1_EMP_*`, `VL1_C2_*` (`VL_estimativas.csv`) | slide 8, adendo | slide 8, **resultado principal**; também na Conclusão |
| 75 km | `VL1_EMP_K5` | slide 8 | slide 8 e fala da Conclusão |
| 52,5% e 60,8%; 1.568 candidatos | `H2D_DISP`, `H2D_ESC`, `H2D_N` (`H2_sintese.csv`, doc 66) | só no doc 66 | slide 5 (novo) |
| 1,15 [0,66; 2,01] e 1,25 [0,90; 1,73] | `VG1_*`, `VG3_*` (`VG_estimativas.csv`, adendo 52g) | não existiam | slide 9 (figura) e notas; os km desses ciclos têm IC com zero e ficam fora |
| 1,45; 1,49; 1,28 | `VLLOG_EMP_RC`, `VL3_EMP_RC`, `VL2_EMP_RC` | slide 9 | slide 9 (figura, só variantes dentro da mesma UF) |
| 1,25 [0,98; 1,61], p 0,072 | `VLB_EMP_*`, `VC_B_HOLM` | figura do slide 8 (cinza) e cautela | fora das figuras; na cautela do slide 8 ("sem fixar a UF: IC contém 1"), na Identificação, nas Limitações e nas notas |
| ×11,0; ×1,57; 1,94 | `VC_THETAX_EST`, `VC_B10X_EST`, `VC_DUF_EST` | slide 7 (teste central) | **fora da tela**; o D_UF só numa linha das notas do slide 11 (pergunta P4) |
| 1,07 e 1,00 por ciclo (modelo base) | `VC_M5C1_RC`, `VC_M5C3_RC` | figura da robustez | fora: o por ciclo agora é o VL-1 (adendo 52g) |
| +16,4 e −6,0 (pareados) | `PL_FRAC_300_TAU`, `PL_FRAC_400_TAU` | figura do apêndice, junto com a RDD | figura do apêndice, sozinhos |

### 6.5 Checklist para o grupo

- [ ] Trocar a hipótese do slide 1 pela frase nova; manter "formulada após ver os dados" na tela.
- [ ] Tirar o slide "Teste central" e qualquer menção a ×11,0, D_UF ou "a origem pesa mais" da tela e da fala.
- [ ] No slide 4, dizer que os 79% são o motivo de comparar dentro da UF, não o resultado.
- [ ] Pôr a F2 do doc 66 como slide 5, com "Descritivo" na tela.
- [ ] No Modelo, a equação com o efeito fixo do par de UFs e o teste β > zero, com cluster por conjunto de escolha.
- [ ] Na Identificação, "Mantido fixo" e "Especificação: pós-resultado (adendo 52e)".
- [ ] O resultado principal é o VL-1 (slide 8), com a figura sem o modelo base.
- [ ] Na robustez, "forte só no ciclo 2; nos ciclos 1 e 3 o IC contém 1"; os km dos ciclos 1 e 3 não vão à tela.
- [ ] Conclusão e Limitações como na seção 6.3; o roteiro de fala novo está no [doc 09](09_roteiro_fala_7min.md).
- [ ] Ressalvas na fala: pós-resultado; sem fixar a UF, o IC contém 1; escolha não é preenchimento; pacote do corte;
  forte só no ciclo 2; origem = vínculo no CNES.
