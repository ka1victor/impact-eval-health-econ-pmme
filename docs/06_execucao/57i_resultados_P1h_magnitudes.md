# 57i. Resultados do P1h: o peso da bolsa contra o custo do lugar na escolha (H3)

> **Gerado por** `scripts/rdd_bolsa/25c_magnitudes_P1h.py` a partir de `output/rdd_bolsa/P1h_*`; não editar à mão (o teste `tests/test_P1h_magnitudes.py` confere que este arquivo é igual ao gerado).<br>
> **Protocolo:** [`52b_protocolo_P1h_magnitudes.md`](52b_protocolo_P1h_magnitudes.md), congelado em 26/10/2026 antes de calcular; estatuto `PROTOCOLO_52B_POS_RESULTADO`.<br>
> **O que já tinha sido visto:** os coeficientes do M1 e os seus IC (doc 57a, protocolo 52, auditoria 26) e a conta aproximada da linha primária (conversa de 26/10/2026). Este bloco acrescenta a inferência formal da diferença, com a covariância conjunta, e a bolsa em km com IC. Não é teste confirmatório novo.<br>
> **Saídas:** `output/rdd_bolsa/P1h_magnitudes.csv`, `P1h_resumo.json` e `P1h_figuras/P1h_magnitudes.png`; toda saída tem `natureza_dos_dados = EMPIRICO`. As saídas do P1 (`P1_*`) não são regravadas.

## 1. O que se mede e o que não se pode dizer

- **Pergunta (H3, incentivo limitado).** No modelo de escolha do P1 (M1), o peso de toda a amplitude da bolsa que a política oferece (de R$ 10 mil para R$ 20 mil por mês, 10·β) é menor que o peso de a vaga ficar na UF de origem do candidato (θ_UF)?
- **É uma comparação de pesos na utilidade da escolha**, não de efeitos causais do lugar. Os dois pesos estão na mesma escala (log-chance) e saem do mesmo modelo, por isso podem ser subtraídos.
- **A bolsa (β)** é identificada pelos saltos da bolsa nos cortes de IVS (0,300 e 0,400), com o IVS em spline contínua: mede o pacote do corte (a bolsa e outras regras federais que mudam no mesmo IVS, auditoria 18) e o incentivo marginal, não a participação no PMM-E.
- **A origem (θ)** é preferência revelada condicional ao modelo. Mistura família, rede, registro profissional e outros motivos ligados à origem. Não é efeito causal da geografia nem de mudar alguém de lugar.
- **Escolha condicional.** Tudo vale para quem se candidatou, dentro do conjunto de vagas abertas do seu curso e ciclo. Nada sobre quem não se candidatou.
- **O que não se pode dizer.** Nada aqui diz se a bolsa "funciona" ou "não funciona". Um peso menor que o da UF de origem não é efeito nulo da bolsa, e um peso grande da UF não diz que a geografia causa a escolha.

Notação: β = `bolsa_mil` (por R$ 1 mil/mês); γ = `distancia_100km` (negativo); θ_UF = `mesma_uf`; θ_reg = `mesma_regiao_saude` (incremento sobre a mesma UF); θ_mun = `mesmo_municipio` (incremento sobre a mesma região). Assim, θ_UF é o peso de uma vaga na UF de origem, fora da região de saúde de origem, contra uma vaga em outra UF à mesma distância.

## 2. Amostra e portão de reprodução

<!-- P1h:portao:inicio -->
- Amostra: a do P1 (candidatos de 1ª opção com município de origem ligado no G1 e com região de saúde), 5421 candidatos, 56 conjuntos de escolha (curso × ciclo), 932577 linhas candidato × célula no M1; no M7, 1630577 linhas (1ª e 2ª opção). Por ciclo (M5): 915, 2032 e 2474 candidatos.
- Distâncias das células escolhidas iguais às do G1: 5421 escolhas, diferença máxima 0,000000000 km.
- **Portão de reprodução: PASSOU.** Tolerância 1e−8 na diferença máxima dos coeficientes e dos EP com cluster por conjunto, em todos os termos de cada especificação, contra `output/rdd_bolsa/P1_estimativas.csv` (gravado com 10 algarismos significativos). Os EP de máxima verossimilhança e por candidato vão ao lado, só como registro.

| Especificação | Termos (reestimados / gravados) | Dif. máx. coef. | Dif. máx. EP cluster | Dif. máx. EP MV | Dif. máx. EP candidato | Portão |
|---|---|---|---|---|---|---|
| M1 (principal): ciclos 1–3, distância/100 km, mesma UF, mesma região, mesmo município, capital | 18 / 18 | 2,9e−10 | 4,6e−11 | 3,3e−11 | 4,9e−11 | passou |
| M2: M1 com log(1 + distância em km) | 18 / 18 | 4,2e−10 | 4,3e−11 | 4,2e−11 | 3,4e−11 | passou |
| M4: M1 com efeito fixo de UF da vaga | 40 / 40 | 5,0e−10 | 4,8e−11 | 4,6e−11 | 4,6e−11 | passou |
| M5: M1 só no ciclo 1 | 18 / 18 | 4,6e−10 | 4,7e−11 | 4,7e−11 | 4,7e−11 | passou |
| M5: M1 só no ciclo 2 | 18 / 18 | 4,6e−10 | 3,8e−11 | 4,6e−11 | 5,0e−11 | passou |
| M5: M1 só no ciclo 3 | 18 / 18 | 2,8e−10 | 4,9e−11 | 4,2e−11 | 4,4e−11 | passou |
| M7: logit explodido (1ª e 2ª opção) com M1 | 18 / 18 | 4,8e−10 | 3,3e−11 | 8,5e−12 | 4,2e−11 | passou |
<!-- P1h:portao:fim -->

## 3. Leitura em linguagem simples

Segue a leitura pré-registrada do §4 do protocolo 52b.

<!-- P1h:leitura:inicio -->
**P1h-1: rejeita H0 depois do Holm.** No M1, toda a amplitude da bolsa (de R$ 10 mil para R$ 20 mil por mês, 10·β) pesa 0,42 na utilidade da escolha (IC 95% [−0,03; 0,87]); a vaga ficar na UF de origem pesa 2,40 (IC [2,28; 2,53]). A diferença D_UF = θ_UF − 10·β é 1,98 (EP 0,213; IC 95% [1,56; 2,40]; limite inferior unilateral de 95% 1,63; p < 0,001, unilateral; família de um teste, p de Holm = p). No modelo de escolha, a amplitude inteira da bolsa pesa menos que a vaga ficar na UF de origem. Isso vale condicional a se candidatar e dentro das vagas abertas. Não diz que a bolsa não tem efeito nem que a geografia causa a escolha: o peso da UF é preferência revelada condicional ao modelo, e o da bolsa é o do pacote do corte.

**P1h-2 (km equivalentes, descritivo).** Um degrau da bolsa (R$ 5 mil por mês) pesa na escolha o mesmo que a vaga ficar 112 km mais perto da origem (IC 95% delta [−9; 233]; Fieller [−7; 237]); toda a amplitude (R$ 10 mil), 224 km (delta [−18; 466]; Fieller [−14; 474]). O IC 95% de β contém zero ([−0,0027; 0,0874]), e por isso o IC de K5 e o de K10 também contêm zero: os dados não descartam que a bolsa não valha nenhum km, nem que um degrau valha até cerca de 237 km. Pelo lado unilateral (H0: K ≤ 0), o limite inferior de 95% de K5 é 10 km pelo delta e 12 km pelo Fieller (p = 0,035, delta). Essas linhas são descritivas: o P1a foi pré-registrado como teste bilateral de β (protocolo 52, Holm; p = 0,065), e o lado unilateral das linhas de km não o substitui.

**P1h-3 (sensibilidade, BKY entre as 6 linhas).** D_UF em M2: 1,18 (IC [0,81; 1,54]; p < 0,001; q BKY = 0,001); M4: 1,73 (IC [1,28; 2,18]; p < 0,001; q BKY = 0,001); M5 ciclo 1: 2,34 (IC [1,45; 3,24]; p < 0,001; q BKY = 0,001); M5 ciclo 2: 1,31 (IC [0,76; 1,86]; p < 0,001; q BKY = 0,001); M5 ciclo 3: 2,37 (IC [1,75; 3,00]; p < 0,001; q BKY = 0,001); M7: 2,07 (IC [1,63; 2,50]; p < 0,001; q BKY = 0,001). Com q BKY < 0,05, 6 de 6 especificações rejeitam H0: D_UF ≤ 0. O M2 mede a distância em log, então o seu θ_UF fica condicional a outra forma da distância; no M5, cada ciclo tem o seu β, e nos ciclos em que β é perto de zero a diferença é quase só θ_UF.

Tudo acima é escolha condicional a candidatar-se, dentro do conjunto de vagas abertas. Nada aqui diz se a bolsa "funciona" ou "não funciona": o contraste compara dois pesos dentro do mesmo modelo de escolha.
<!-- P1h:leitura:fim -->

## 4. Tabela

<!-- P1h:tabela:inicio -->
EP cluster = sanduíche com cluster por conjunto de escolha (curso × ciclo), a inferência principal; EP MV = máxima verossimilhança; EP candidato = cluster por candidato. IC, limite inferior (LI) unilateral e p unilateral (H0: estimando ≤ 0) usam o EP cluster pela normal; ao lado, o p unilateral pela t com G − 1 graus de liberdade. Linhas de km: estimativa, EP, IC e p pelo método delta; Fieller ao lado. Holm só no P1h-1 (família de um teste); BKY só entre as linhas P1h-3, e q BKY = 0,001 é o piso da grade do algoritmo (Anderson, 2008), não um valor exato.

| Linha | Modelo | Estimando | Estimativa | EP cluster | EP MV | EP candidato | IC 95% | LI unilateral 95% | p unilateral | p unil. (t, G−1) | Fieller: IC 95%; LI 95% | p Holm / q BKY | Rejeita H0 a 5% |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1h-1 | M1 | D_UF | 1,978 | 0,213 | 0,131 | 0,135 | [1,560; 2,396] | 1,628 | < 0,001 | < 0,001 | — | < 0,001 | sim |
| P1h-2a | M1 | K5 | 112 | 62 | 32 | 33 | [−9; 233] | 10 | 0,035 | 0,038 | [−7; 237]; LI 12 | — | — |
| P1h-2b | M1 | K10 | 224 | 124 | 64 | 66 | [−18; 466] | 21 | 0,035 | 0,038 | [−14; 474]; LI 24 | — | — |
| P1h-3 | M2 | D_UF | 1,176 | 0,187 | 0,135 | 0,139 | [0,810; 1,543] | 0,869 | < 0,001 | < 0,001 | — | 0,001 | sim |
| P1h-3 | M4 | D_UF | 1,732 | 0,229 | 0,139 | 0,144 | [1,283; 2,182] | 1,355 | < 0,001 | < 0,001 | — | 0,001 | sim |
| P1h-3 | M5 ciclo 1 | D_UF | 2,343 | 0,457 | 0,318 | 0,316 | [1,447; 3,239] | 1,591 | < 0,001 | < 0,001 | — | 0,001 | sim |
| P1h-3 | M5 ciclo 2 | D_UF | 1,310 | 0,279 | 0,221 | 0,229 | [0,763; 1,857] | 0,851 | < 0,001 | < 0,001 | — | 0,001 | sim |
| P1h-3 | M5 ciclo 3 | D_UF | 2,373 | 0,318 | 0,194 | 0,201 | [1,750; 2,995] | 1,850 | < 0,001 | < 0,001 | — | 0,001 | sim |
| P1h-3 | M7 | D_UF | 2,067 | 0,221 | 0,098 | 0,112 | [1,633; 2,501] | 1,703 | < 0,001 | < 0,001 | — | 0,001 | sim |

Pesos da figura (M1, descritivos, mesma escala da utilidade):

| Peso (M1) | Combinação | Estimativa | EP cluster | IC 95% |
|---|---|---|---|---|
| Bolsa: um degrau (+R$ 5 mil/mês) | 5β | 0,212 | 0,115 | [−0,013; 0,437] |
| Bolsa: toda a amplitude (R$ 10 → 20 mil) | 10β | 0,424 | 0,230 | [−0,027; 0,874] |
| Vaga 100 km mais perto da origem | −γ | 0,189 | 0,012 | [0,166; 0,213] |
| Mesma UF, outra região de saúde | θ_UF | 2,402 | 0,064 | [2,278; 2,527] |
| Mesma região de saúde, outro município | θ_UF + θ_reg | 4,048 | 0,195 | [3,665; 4,430] |
| Mesmo município da origem | θ_UF + θ_reg + θ_mun | 4,835 | 0,144 | [4,553; 5,117] |
<!-- P1h:tabela:fim -->

## 5. Figura

<!-- P1h:figura:inicio -->
![No modelo de escolha, a vaga estar na UF de origem pesa mais que toda a amplitude da bolsa (R$ 10 → 20 mil)](../../output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png)

Arquivo: `output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png`. Título da figura: "No modelo de escolha, a vaga estar na UF de origem pesa mais que toda a amplitude da bolsa (R$ 10 → 20 mil)".

**Como ler.** Cada ponto é o peso de um atributo da vaga na utilidade da escolha da 1ª opção, no modelo principal (M1, ciclos 1–3), em log-chance; a barra é o IC 95% com cluster por conjunto de escolha. Todos os pesos estão na mesma escala: um peso de 1 multiplica por e ≈ 2,7 a razão entre a probabilidade de escolher a vaga e a de escolher qualquer outra do conjunto, mantido o resto. As linhas de lugar comparam com uma vaga em outra UF, à mesma distância, e cada uma é uma categoria: mesma UF fora da região de saúde de origem; mesma região fora do município; mesmo município. São preferência revelada condicional ao modelo, não efeito causal da geografia; as da bolsa são identificadas pelos cortes de IVS (pacote do corte). O peso da distância depende da unidade escolhida (100 km).
<!-- P1h:figura:fim -->

## 6. Desvios e decisões de implementação

<!-- P1h:desvios:inicio -->
Nenhum desvio forçado pelos dados: a execução seguiu o protocolo 52b. Abaixo, as decisões de implementação onde o protocolo não fixava o detalhe. Elas estão no mesmo commit dos números, e por isso o Git não mostra se vieram antes deles. Nenhuma muda estimativa, EP, IC ou a decisão do P1h-1 (auditoria 31).

1. **Linhas da figura no CSV** (26/10/2026). O §5 pede a figura dos pesos na mesma escala, mas o §3 só lista P1h-1 a P1h-3. *Resolução:* Os seis pesos da figura (5β, 10β, −γ, θ_UF, θ_UF + θ_reg, θ_UF + θ_reg + θ_mun) vão para o CSV com id_linha = FIG e papel descritivo, sem teste nem correção múltipla, para que a figura seja lida de output/ (regra de proveniência).
2. **p unilateral das linhas de km** (26/10/2026). O §3 pede p unilateral em toda linha; para K5 e K10 o protocolo não diz o método. *Resolução:* p de H0: K ≤ 0 pelo método delta, como o EP e o IC dessas linhas; o Fieller dá o IC 95% e o limite inferior unilateral (conjunto de 90%). Pelo Fieller, H0: K ≤ 0 equivale a H0: β ≤ 0, porque γ < 0. As linhas são descritivas e não substituem o teste bilateral do P1a.
3. **Alcance do portão** (26/10/2026). O §2 manda conferir 'os coeficientes e os EP com cluster por conjunto'; o §3 aplica o mesmo portão às sensibilidades. *Resolução:* Todos os termos de cada especificação (M1, M2, M4, M5 por ciclo, M7) entram no portão; os EP de MV e por candidato são registrados sem entrar nele. Qualquer falha para a execução inteira, com o código da primeira especificação que falhou, e nada é calculado.
4. **Rejeição nas sensibilidades** (26/10/2026). O §3 manda BKY entre as linhas P1h-3 sem dizer o nível. *Resolução:* q BKY e a marca 'rejeita a 5%' (q < 0,05) são registrados como leitura de robustez; a única linha com decisão é o P1h-1.
<!-- P1h:desvios:fim -->

## 7. Limites

- **Pós-resultado.** Os coeficientes do M1 já eram conhecidos; o P1h formaliza uma comparação cuja resposta era previsível pelos IC publicados. Não é teste confirmatório novo.
- **Escolha condicional.** Os pesos descrevem como quem se candidatou ordena as vagas abertas; não medem entrada no programa, oferta líquida de especialistas nem permanência.
- **θ não é causal.** A origem é o município do estabelecimento de vínculo médico no CNES, não a residência, e o peso da UF de origem junta tudo o que a origem carrega (família, rede, registro profissional e outros motivos).
- **β é pacote do corte e é impreciso.** O IC de β no M1 contém zero; as razões em km herdam essa imprecisão. A bolsa entra linear entre R$ 10 e R$ 20 mil: 10·β supõe que os dois degraus pesam o mesmo.
- **Distância linear.** K5 e K10 usam a distância linear do M1; com a distância em log (M2), um km não vale o mesmo em toda distância, e a conversão não se aplica.
- **Poucos conjuntos.** São 56 conjuntos de escolha (curso × ciclo); o EP com cluster por conjunto é impreciso, e o p pela t com G − 1 graus de liberdade vai ao lado.
- **IIA e especificações fora.** O logit condicional supõe independência de alternativas irrelevantes. O logit misto (M8) e o aninhado (M9) ficaram fora do P1h (o M8 é caro de reestimar); o M3 não foi estimado no P1.
