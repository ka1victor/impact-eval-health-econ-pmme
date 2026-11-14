# 04. Perguntas prováveis da banca sobre o logit condicional, com respostas

> **Para quê:** preparar a defesa do método (slides 17 e 20–22 e anexo 1 do deck de [03](03_deck_banca_final_grupo.md)).
> Pedido do autor de 14/11/2026: explicar melhor como o logit condicional foi feito.<br>
> **Estatuto:** apresentação. Nenhuma estimativa nova. Cada número vem de `output/rdd_bolsa/VL_estimativas.csv`,
> `VL_resumo.json`, `P1_estimativas.csv`, `portao_r1_ivs_oficial.json` ou dos docs citados; o deck lê os mesmos
> arquivos.<br>
> **Regra de fala:** é escolha da 1ª opção, condicional a se candidatar; não é ida ao município, nem preenchimento,
> nem efeito da participação no PMM-E. O contraste é o pacote do corte de IVS (bolsa e outras regras nos mesmos
> cortes), não o dinheiro isolado.

## Modelo

**1. Por que logit condicional, e não uma regressão linear?**
Cada médico escolhe **uma** vaga entre as que podia escolher (≈ 107 em média; mediana 82). O logit condicional
(McFadden, 1974) modela exatamente isso: dá uma chance a cada vaga, as chances das vagas de cada candidato somam 1, e tudo o que é do
médico (nota, idade, de onde vem) é igual em todas as vagas dele e sai da conta. Uma regressão linear por vaga não
respeita a soma 1 nem compara vagas do mesmo médico. É o desenho usado na literatura de escolha de vaga com bônus
que salta em cortes (Bobba et al., 2026) e de escolha de local por médicos no Brasil (Costa, Nunes & Sanches, 2024),
que usam versões mais ricas da mesma família. Na tela fica só o exemplo de saúde (Costa, Nunes e Sanches).

**2. Vocês estão estimando a utilidade?**
Só os pesos da parte observável do valor (V), numa escala normalizada. O nível do valor e a unidade não são
identificados: só diferenças entre vagas do mesmo candidato importam. Por isso lemos cada coeficiente pela razão de
chances entre duas vagas: P(A) ÷ P(B) = exp(V_A − V_B), em que o denominador se cancela.

**3. O que é o 1,47?**
β = 0,077 por R$ 1 mil. Entre duas vagas iguais no resto, a que paga R$ 5 mil a mais tem chance e^(5 × 0,077) =
e^0,385 = **1,47** vez maior de ser a 1ª opção (IC 95%: 1,15 a 1,89). Exemplo real dos slides 14 e 21: Araçuaí 2,53% e
Itamarandiba 3,62%; a razão 1,43 = ×1,47 (bolsa) × 0,97 (6 km a mais) × 1,00 (o resto).

**4. E os 75 km?**
É a razão entre dois coeficientes: 5β ÷ |γ| × 100 = 0,385 ÷ 0,514 × 100 = 75 km (IC delta 28 a 122 km; doc 57x,
VL-4). Mais R$ 5 mil compensam, na escolha, uma vaga 75 km mais longe do local de trabalho anterior.

## Identificação

**5. De onde vem a variação que identifica o β?**
Três coisas juntas (anexo 1):
1. a bolsa é função em degraus do IVS 2010: salta em 0,300 e 0,400 (a regra reproduz 368 de 368 municípios no
   ciclo 1 e 454 de 454 no ciclo 2);
2. o IVS entra como reta com dobras nesses cortes, **sem salto**; o que muda de repente no corte é só a bolsa, e é esse
   salto que informa o β (a mesma lógica da nota 13 de Bobba et al.);
3. a comparação é dentro do par UF de trabalho × UF da vaga: 260 pares com bolsas diferentes, 5.345 candidatos.

**6. Por que não um efeito fixo de município ou de vaga?**
A bolsa é a mesma no município inteiro: um efeito fixo de município absorveria a bolsa, e o β não existiria. O que
fica fixo é o candidato (implícito no logit condicional) e o par de UFs (254 colunas 0/1).

**7. Por que fixar o par de UFs? Isso não foi escolhido depois de ver o resultado?**
Foi, e dizemos isso na tela, em Limitações (slide 26). O plano original saiu da apresentação; esta é a resposta se
perguntarem. O plano pré-registrado, sem o par, dá ×1,25 (IC 0,98 a 1,61): o IC
contém 1. O par tira tudo o que é comum à UF (salário de mercado, conselho regional, família, distância média entre
UFs). Dentro da UF, a distância pesa mais (×0,60 contra ×0,83 por 100 km) e a bolsa também. Por isso chamamos o
resultado de exploratório: o desenho é o mesmo, mas não foi o teste planejado; não quer dizer "não causal".
Confirmar exigiria repetir o teste em dados novos (o ciclo 3 maduro).

**8. E perto do corte, que seria a comparação mais limpa?**
Só com vagas a ±0,050 de um corte: ×1,28 (IC 0,95 a 1,72). Mesma direção, mas com menos dados o IC contém 1:
inconclusivo, não contrário.

**9. Isso é efeito causal da bolsa?**
É o efeito do **pacote do corte** sobre a escolha de quem se candidatou. Outras políticas federais usam os mesmos
cortes de IVS (auditoria 18), então o dinheiro não sai isolado. E escolher não é ir: não medimos a chegada.

**10. A premissa de alternativas independentes (IIA) vale?**
Não por inteiro. No logit aninhado por região de saúde, λ = 0,45 (λ = 1 seria o logit condicional): vagas da mesma
região se substituem mais. Mas o peso da bolsa quase não muda (0,043 contra 0,042). **Atenção:** o aninhado foi
rodado no modelo base (sem o par de UFs), não no principal. O logit misto (M8) mostra que o peso da bolsa varia entre
candidatos: o β é uma média.

**11. E a escolha sincera? O médico não evita vaga concorrida?**
É premissa (SUPOSIÇÃO no slide 22): supomos que ninguém deixa de pôr em 1º a vaga preferida por medo de não passar na
nota. Não dá para testar com estes dados.

## Estimação e incerteza

**12. Como foi estimado?**
Máxima verossimilhança por Newton–Raphson, em código próprio (`scripts/rdd_bolsa/25_escolha_dap.py` e
`50_escolha_localizacao_par.py`). Antes de estimar algo novo, o script reproduz as estimativas já gravadas
(diferença ≤ 10⁻⁸) e para se não reproduzir.

**13. Como foi calculado o erro-padrão?**
Agrupado por conjunto de escolha (curso × ciclo, 55 grupos), porque escolhas do mesmo edital não são independentes.
O EP do β agrupado é 0,025, o dobro do ingênuo (0,013).

**14. 55 grupos não é pouco?**
É, por isso há um teste que não depende da aproximação normal: score bootstrap de Kline e Santos (2012), p = 0,011.
E, como há três testes principais (todos os ciclos, só o ciclo 2, perto do corte), corrigimos por Holm: p = 0,005.

**15. Vale para os três ciclos?**
Não com a mesma força. Ciclo 2: ×1,90 (IC 1,30 a 2,78). Ciclos 1 e 3: ×1,15 e ×1,25, com IC que contém 1. Não dá
para generalizar para outros ciclos.

## Dados

**16. De onde sai a distância?**
Do local de trabalho anterior: o município do vínculo médico no CNES antes da inscrição, não a residência. De 5.714
candidatos com 1ª opção, 5.425 têm esse local; 5.421 têm região de saúde; 5.417 entram no modelo principal.

**17. Por que 578.998 linhas?**
Uma linha por candidato × vaga que ele podia escolher. O desenho tinha 932.577; saem as vagas de pares de UFs que nenhum médico
daquela UF escolheu (não informam o peso da bolsa: o efeito fixo do par iria a menos infinito) e 4 candidatos que
ficaram com uma só vaga possível.
