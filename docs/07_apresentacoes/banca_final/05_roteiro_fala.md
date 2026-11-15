# 05. Roteiro de fala da banca final, em bullets

> **Para quê:** o que falar em cada slide da versão conciliada
> (`output/apresentacao_banca_final/deck_banca_final_grupo_conciliado.pptx`, 35 slides), a que junta a nossa versão
> com as ideias do colega. A última seção diz o que muda na nossa versão (`deck_banca_final_grupo.pptx`, 32 slides).
> Conteúdo dos slides no [doc 03](03_deck_banca_final_grupo.md). É a versão curta das notas do apresentador; as notas
> continuam com o detalhe e as respostas de reserva, e as perguntas prováveis estão no
> [doc 04](04_perguntas_provaveis_logit.md).<br>
> **Em Word:** `output/apresentacao_banca_final/roteiro_fala_banca_final.docx`, gerado deste arquivo por
> `scripts/apresentacao/gerar_roteiro_docx.py` (editar aqui e gerar de novo).<br>
> **Tempo:** o tempo da banca ainda não foi informado. Os tempos abaixo somam cerca de 13 min 30 s. Se faltar tempo,
> encurtar primeiro os slides marcados **(encurtável)**.<br>
> **Regra de fala:** é a escolha da 1ª opção de quem se inscreveu, não a chegada do médico ao município; o efeito é o
> do conjunto de regras que muda no corte do IVS, não só do dinheiro. Resultado descritivo é chamado de descritivo.

## Abertura e motivação (≈ 3 min)

**1. Capa** (10 s)
- Grupo 2; tema: a bolsa do PMM-E como incentivo para o médico escolher uma vaga.

**2. Sumário** (5 s): passar.

**3. Escassez de especialistas já é tratada como urgência sanitária** (40 s)
- Faltam especialistas no Brasil, e eles se concentram no Sul e no Sudeste.
- Quem mora longe se desloca muito para chegar a serviço especializado: é um problema de equidade do SUS.

**4–6. Vulnerabilidade social define o valor da bolsa do PMM-E** (60 s, os três juntos)
- O PMM-E leva especialistas a regiões prioritárias: bolsa mensal do Ministério da Saúde, 20 h por semana, até 12
  meses.
- O IVS (Ipea, 2010) resume a vulnerabilidade do município: infraestrutura, capital humano, renda e trabalho.
- A bolsa é fixada por regra pela faixa de IVS: R$ 10 mil (até 0,300), R$ 15 mil (0,301 a 0,400), R$ 20 mil (acima
  de 0,400). É o instrumento da política.

**7. Política direciona incentivos aos territórios mais vulneráveis** (40 s)
- O programa alocou mais especialistas onde havia menos e paga mais nas regiões mais vulneráveis.
- Pergunta natural: essa bolsa maior de fato atrai os médicos?

## Pergunta, teoria e hipótese (≈ 2 min)

**8. Sumário** (5 s): passar.

**9. Pergunta** (20 s)
- "Uma bolsa maior aumenta a chance de uma vaga ser a 1ª opção do médico?"

**10. Sumário** (5 s): passar.

**11–12. Cadeia causal: da bolsa aos desfechos na saúde** (60 s, os dois juntos)
- Regra: IVS do município → bolsa.
- A bolsa aumenta o valor da vaga (Moehling et al.); o custo de viver ali (Redding e Rossi-Hansberg) e o de trabalhar
  ali (Choné e Ma) reduzem. Não vemos esse valor; vemos só a 1ª opção.
- O que estimamos: o peso da remuneração na chance de a vaga ser a 1ª opção.
- (12) Da vaga à saúde fica fora do que estimamos: quantos médicos escolhem a vaga, se ela é ocupada, vínculos e
  horas no CNES, consultas e exames, e por fim espera e internações.

**13. Sumário** (5 s): passar.

**14. Maior remuneração, maior chance de ser escolhida** (40 s)
- Hipótese: entre vagas do mesmo curso, na mesma UF e iguais no resto, a que paga mais tem mais chance de ser a 1ª
  opção.
- Exemplo real (MG, ciclo 2): Araçuaí e Itamarandiba têm IVS e distância quase iguais, mas a segunda paga R$ 5 mil a
  mais. A hipótese diz: chance de Itamarandiba > chance de Araçuaí.
- Medimos a escolha de quem se inscreveu, não a chegada de médicos ao município.

## Dados e descritiva (≈ 2 min 30 s)

**15. Sumário** (5 s): passar.

**16. Dados ligam os editais do PMM-E ao CNES** (40 s)
- Editais e quadros de vagas (1ª opção, bolsa), CNES (onde o médico trabalhava antes), Ipea (IVS) e IBGE (distância,
  porte, capital).
- Três ciclos; 5.417 candidatos no modelo principal.

**17. Cada candidato vira uma linha por vaga possível** (50 s)
- Para cada candidato, uma linha por vaga que ele podia escolher; y = 1 só na vaga posta em 1º.
- Exemplo: o médico de MG tinha 222 vagas; escolheu Brasília de Minas.
- 5.417 candidatos × ≈ 107 vagas = 578.998 linhas.

**18. Candidatos escolhem perto de onde trabalham** (50 s)
- Como montamos: 5.425 candidatos; distância do município onde trabalhavam até o da vaga posta em 1º.
- Metade escolhe a até 51 km; 79% ficam na mesma UF; 36% no próprio município.
- É descritivo: mostra onde escolhem, não por quê. Por isso o modelo compara vagas da mesma UF.

## Metodologia e identificação (≈ 4 min)

**19. Sumário** (5 s): passar.

**20. Cada médico escolhe a vaga que mais vale a pena** (45 s)
- Não vemos o que o médico pensa, só a vaga que ele pôs em 1º lugar.
- Cada médico tem uma lista de vagas, cada vaga tem prós e contras, e há coisas que não vemos (família, gosto); por
  isso o modelo dá a chance de cada vaga: A 29%, B 42%, C 29%.
- B paga mais e fica perto; C paga como B, mas fica 75 km mais longe, e isso anula a bolsa extra.
- Nossa pergunta: quanto a bolsa pesa? Se vagas iguais com bolsas diferentes fossem escolhidas meio a meio, ela não
  pesaria nada.

**21. Modelo: logit condicional da 1ª opção** (60 s)
- É a mesma ideia do slide anterior, em fórmula. Cada vaga tem uma utilidade para o médico: bolsa, distância, IVS,
  controles e o par de UFs, mais um erro ε (o que não vemos).
- Vemos só qual vaga tem a maior utilidade: a 1ª opção. Com ε de valor extremo, a chance de cada vaga é a fórmula ①.
- O coeficiente testado é o da bolsa; o resto são controles. O par de UFs faz comparar vagas dentro da mesma UF, e a
  bolsa vem de regra com o IVS no modelo (detalhe no anexo 1, se perguntarem).
- Por que este modelo: logit condicional de McFadden (1974), que lhe rendeu o Nobel de Economia de 2000. Compara as
  vagas do mesmo médico, então o que é dele sai da conta. Referência de uso em economia da saúde: Costa, Nunes e
  Sanches (2024), sobre onde os médicos escolhem trabalhar no Brasil.

**22. Método passo a passo: da escolha à razão de chances** (60 s)
- 1–2: monta a base (uma linha por vaga; y = 1 na escolhida). 3–5: estima os pesos que melhor explicam as escolhas.
  6: lê o resultado como razão de chances.
- Passo 4: a chance de cada vaga é exp(U sem ε) dela dividido pela soma disso em todas as vagas do médico.
- Passo 6: a métrica é a chance da vaga que paga mais dividida pela chance da outra; as outras vagas se cancelam.
- No exemplo: Itamarandiba 3,62% ÷ Araçuaí 2,53% = 1,43, e quase tudo vem da bolsa (×1,47).

**23. Identificação: as premissas do logit condicional** (60 s)
- Escolha sincera e conjunto de escolha conhecido: suposições.
- Exogeneidade da bolsa: vale em parte; a bolsa segue a regra, mas outras regras federais mudam nos mesmos cortes.
- IIA: testada; com um logit aninhado, o peso da bolsa quase não muda.

## Resultados e discussão (≈ 2 min 30 s)

**24. Sumário** (5 s): passar.

**25. Ficar perto de onde trabalha pesa mais que a bolsa** (60 s)
- O gráfico mostra quanto cada fator multiplica a chance da vaga: mesma região de saúde ×3,01; mesmo município ×1,80;
  +R$ 5 mil de bolsa ×1,47; população em dobro ×1,10; capital ×0,73 (o intervalo inclui 1); +100 km ×0,60.
- As três contas: 5 × 0,077 = 0,385; exp(0,385) = ×1,47, ou seja, 47% mais chance (IC 1,15 a 1,89); 0,385 ÷ 0,514 ×
  100 = 75 km.
- Leitura: a bolsa conta, mas estar na mesma região de saúde de onde já trabalha pesa mais. Por isso, incentivo
  limitado.

**26. Robustez: ×1,47 se mantém com mais dados** (20 s) **(encurtável)**
- Uma frase: com outras medidas, o ×1,47 se mantém (×1,45 a ×1,49); com só parte dos dados fica inconclusivo, e o
  ciclo 2 é o mais forte (×1,90).

**27. Limitações** (30 s, passar rápido)
- Medimos a escolha, não a chegada; no corte mudam outras regras; o local anterior é o do CNES, não a residência.
- Fixar a UF foi decidido depois de ver os dados: o resultado é exploratório; confirmar exige dados novos (o ciclo 3
  maduro). **Falar isso antes de a banca perguntar.**
- Significativo só no ciclo 2; a escolha sincera não dá para testar.

**28. Conclusão: bolsa pesa na escolha, mas pouco** (50 s)
- Fecha a apresentação. Resposta: sim, a vaga de bolsa maior é mais escolhida (×1,47; ≈ 75 km).
- Descritivo: 51% de quem ocupa a vaga já tinha vínculo no município; o cadastro sobe +6,6 h/sem num programa de 20 h.
- Não dá para afirmar que leva mais médicos ao município, que o efeito é só da bolsa, nem que vale em todo ciclo.
- Para a política: pagar mais muda a escolha entre vagas próximas; não mostramos que atraia médicos de longe.

**29. Q&A**: abrir para perguntas (respostas no [doc 04](04_perguntas_provaveis_logit.md)).

## Anexos (só se perguntarem; do mais ao menos provável de ser cobrado)

O rodapé de cada anexo marca a seção a que ele se refere.

- **30. Anexo 1, estimação (Metodologia):** a bolsa é fixada por regra e o IVS está no modelo; comparamos vagas do
  mesmo candidato, na mesma UF (260 pares de UFs, 5.345 candidatos); dentro do município não dá, porque a bolsa é
  igual no município inteiro.
- **31. Anexo 2, por que este modelo e não outro (Metodologia):** comparar vagas dos dois lados do corte foi feito e
  deu inconclusivo; a regressão linear 0/1 prevê chances fora de 0 a 100%; a contagem Poisson dá o mesmo β; versões
  mais ricas (misto, aninhado) ficaram como teste extra.
- **32. Anexo 3, o modelo formal (Metodologia):** U = β·x + ε; y = 1 na vaga de maior U; a chance usa só β·x; a razão
  de chances é exp(5β) = 1,47. "y é o resultado, U é o mecanismo."
- **33. Anexo 4, a regra da bolsa (Identificação):** o IVS reproduz a faixa de 368 de 368 municípios no ciclo 1 e de
  454 de 454 no ciclo 2; o município não escolhe a bolsa.
- **34. Anexo 5, a equação da teoria (Literatura):** de onde vem cada termo (salário, custo de trabalhar, custo de
  viver).
- **35. Anexo 6, literatura (Literatura):** Moehling et al. dão a escolha do local (rendimento menos custo de estar
  ali); Choné e Ma, Reinhardt e Redding e Rossi-Hansberg dão os dois custos, de trabalhar e de viver ali.

## Nossa versão (32 slides): o que muda

- Não tem o slide 20 (as vagas A, B e C): do 20 em diante, os números caem um.
- O resultado (slide 24) é "Resultados: +R$ 5 mil multiplicam a chance por 1,47": três cartões (×1,47; ≈ 75 km;
  ×1,90 só no ciclo 2), a figura dos quatro fatores e a leitura "a bolsa pesa, mas a proximidade pesa mais".
- Os anexos são quatro (slides 29 a 32): estimação, regra da bolsa, equação da teoria e literatura.
