# 05. Roteiro de fala da banca final, em bullets

> **Para quê:** o que falar em cada slide da nossa versão final
> (`output/apresentacao_banca_final/deck_banca_final_grupo.pptx`, 32 slides; conteúdo no
> [doc 03](03_deck_banca_final_grupo.md)). É a versão curta das notas do apresentador: as notas do deck continuam
> com o detalhe e as respostas de reserva; as perguntas prováveis estão no [doc 04](04_perguntas_provaveis_logit.md).<br>
> **Tempo:** o tempo da banca ainda não foi informado. Os tempos abaixo somam cerca de 15 min. Se faltar tempo,
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

## Pergunta, literatura e hipótese (≈ 2 min 30 s)

**8. Sumário** (5 s): passar.

**9. Pergunta** (20 s)
- "Uma bolsa maior aumenta a chance de uma vaga ser a 1ª opção do médico?"

**10. Sumário** (5 s): passar.

**11. Modelo combina dois elementos da teoria** (40 s) **(encurtável)**
- Moehling et al. (2020): o médico escolhe o local que maximiza o valor do rendimento menos um custo de estar ali.
- Esse custo tem duas partes: trabalhar ali (equipe, equipamento; Choné e Ma) e viver ali (amenidades, distância;
  Redding e Rossi-Hansberg).

**12–13. Cadeia causal: da bolsa aos desfechos na saúde** (50 s, os dois juntos)
- Regra: IVS do município → bolsa.
- A bolsa aumenta o valor da vaga; os custos de viver e de trabalhar ali reduzem. Não vemos esse valor; vemos só a 1ª
  opção.
- O que estimamos: o peso da remuneração na chance de a vaga ser a 1ª opção.
- (13) Da vaga à saúde fica fora do que estimamos: quantos médicos escolhem a vaga, se ela é ocupada, vínculos e
  horas no CNES, consultas e exames, e por fim espera e internações.

**14. Sumário** (5 s): passar.

**15. Maior remuneração, maior chance de ser escolhida** (40 s)
- Hipótese: entre vagas do mesmo curso, na mesma UF e iguais no resto, a que paga mais tem mais chance de ser a 1ª
  opção.
- Exemplo real (MG, ciclo 2): Araçuaí e Itamarandiba têm IVS e distância quase iguais, mas a segunda paga R$ 5 mil a
  mais. A hipótese diz: chance de Itamarandiba > chance de Araçuaí.
- Medimos a escolha de quem se inscreveu, não a chegada de médicos ao município.

## Dados e descritiva (≈ 2 min 30 s)

**16. Sumário** (5 s): passar.

**17. Dados ligam os editais do PMM-E ao CNES** (40 s)
- Editais e quadros de vagas (1ª opção, bolsa), CNES (onde o médico trabalhava antes), Ipea (IVS) e IBGE (distância,
  porte, capital).
- Três ciclos; 5.417 candidatos no modelo principal.

**18. Cada candidato vira uma linha por vaga possível** (50 s)
- Para cada candidato, uma linha por vaga que ele podia escolher; y = 1 só na vaga posta em 1º.
- Exemplo: o médico de MG tinha 222 vagas; escolheu Brasília de Minas.
- 5.417 candidatos × ≈ 107 vagas = 578.998 linhas.

**19. Candidatos escolhem perto de onde trabalham** (50 s)
- Como montamos: 5.425 candidatos; distância do município onde trabalhavam até o da vaga posta em 1º.
- Metade escolhe a até 51 km; 79% ficam na mesma UF; 36% no próprio município.
- É descritivo: mostra onde escolhem, não por quê. Por isso o modelo compara vagas da mesma UF.

## Metodologia e identificação (≈ 4 min)

**20. Sumário** (5 s): passar.

**21. Modelo: logit condicional da 1ª opção** (70 s)
- Cada vaga tem uma utilidade para o médico: bolsa, distância, IVS, controles e o par de UFs, mais um erro ε (o que
  não vemos, como família e gosto).
- Vemos só qual vaga tem a maior utilidade: a 1ª opção. Com ε de valor extremo, a chance de cada vaga é a fórmula ①.
- O coeficiente testado é o da bolsa; o resto são controles. O par de UFs faz comparar vagas dentro da mesma UF.
- Por que este modelo: é o padrão para escolher uma opção entre várias (McFadden, Nobel de 2000). Compara as vagas do
  mesmo médico, então o que é dele sai da conta. Em saúde, Costa, Nunes e Sanches usam a mesma família.

**22. Método passo a passo: da escolha à razão de chances** (60 s)
- 1–2: monta a base (uma linha por vaga; y = 1 na escolhida). 3–5: estima os pesos que melhor explicam as escolhas.
  6: lê o resultado como razão de chances.
- Passo 4: a chance de cada vaga é exp(U sem ε) dela dividido pela soma disso em todas as vagas do médico.
- Passo 6: a métrica é a chance da vaga que paga mais dividida pela chance da outra; as outras vagas se cancelam.
- No exemplo: Itamarandiba 3,62% ÷ Araçuaí 2,53% = 1,43, e quase tudo vem da bolsa (×1,47).

**23. Estimação: de onde vem o β** (50 s) **(encurtável)**
- A bolsa é fixada por regra e o IVS está no modelo: o β não mistura bolsa com vulnerabilidade.
- Comparamos vagas do mesmo candidato, na mesma UF; dentro do município não dá, porque a bolsa é a mesma no município
  inteiro.

**24. Identificação: as premissas do logit condicional** (60 s)
- Escolha sincera e conjunto de escolha conhecido: suposições.
- Exogeneidade da bolsa: vale em parte; a bolsa segue a regra, mas outras regras federais mudam nos mesmos cortes.
- IIA: testada; com um logit aninhado, o peso da bolsa quase não muda.

## Resultados e discussão (≈ 3 min)

**25. Sumário** (5 s): passar.

**26. Resultados: +R$ 5 mil multiplicam a chance por 1,47** (60 s)
- Na mesma UF, +R$ 5 mil multiplicam por 1,47 a chance de a vaga ser a 1ª opção (IC 1,15 a 1,89).
- Em distância: R$ 5 mil valem o mesmo que a vaga ficar ≈ 75 km mais perto.
- Mas a proximidade pesa mais: na mesma região de saúde de onde já trabalhava, ×3,01. Por isso, incentivo limitado.

**27. Robustez: ×1,47 se mantém com mais dados** (40 s)
- Com outras medidas e todos os dados, de ×1,45 a ×1,49.
- Com só parte dos dados (perto do corte; ciclos 1 e 3), o intervalo inclui 1: inconclusivo, não contrário. O ciclo 2
  é o mais forte (×1,90).

**28. Limitações** (30 s, passar rápido)
- Medimos a escolha, não a chegada; no corte mudam outras regras; o local anterior é o do CNES, não a residência.
- Fixar a UF foi decidido depois de ver os dados: o resultado é exploratório; confirmar exige dados novos (o ciclo 3
  maduro). **Falar isso antes de a banca perguntar.**
- Significativo só no ciclo 2; a escolha sincera não dá para testar.

**29. Conclusão: bolsa pesa na escolha, mas pouco** (50 s)
- Fecha a apresentação. Resposta: sim, a vaga de bolsa maior é mais escolhida (×1,47; ≈ 75 km).
- Descritivo: 51% de quem ocupa a vaga já tinha vínculo no município; o cadastro sobe +6,6 h/sem num programa de 20 h.
- Não dá para afirmar que leva mais médicos ao município, que o efeito é só da bolsa, nem que vale em todo ciclo.
- Para a política: pagar mais muda a escolha entre vagas próximas; não mostramos que atraia médicos de longe.

**30. Q&A**: abrir para perguntas (respostas no [doc 04](04_perguntas_provaveis_logit.md)).

## Anexos (só se perguntarem)

- **31. Anexo 1, a equação da teoria:** de onde vem cada termo (salário, custo de trabalhar, custo de viver).
- **32. Anexo 2, a regra da bolsa:** o IVS reproduz a faixa de 368 de 368 municípios no ciclo 1 e de 454 de 454 no
  ciclo 2; o município não escolhe a bolsa.
