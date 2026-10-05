# 20. Evidência empírica sobre a hipótese: remuneração oferecida e preenchimento de vagas

> **Classificação:** literatura empírica<br>
> **Hipótese em exame:** *"municípios com maior remuneração oferecida pelo PMM-E
> têm maior preenchimento de vagas"* — slide 15 da
> [versão apresentada](../07_apresentacoes/banca1/04_versao_apresentada.md);
> forma canônica **H1**, $\partial\Pr(\text{aceitar})/\partial B_m > 0$, em
> [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../02_teoria/hipoteses_e_viabilidade_empirica.md), §4<br>
> **Modelo de referência:** $\max_m \sum_t \delta^t \left[\mathbb{E}(w_{mt}\mid B)/p_{mt} - c_{im}\right]$,
> com $c$ = custo geográfico + custo laboral ([`modelo_micro.md`](../02_teoria/modelo_micro.md))<br>
> **Complementa:** [`19_literatura_empirica_escolha_locacional_medicos.md`](19_literatura_empirica_escolha_locacional_medicos.md),
> sem substituí-lo<br>
> **Atualização:** 5 de outubro de 2026

## 1. Regra de uso

Vale a regra do [catálogo 19](19_literatura_empirica_escolha_locacional_medicos.md#1-regra-de-uso):
os estudos daqui calibram expectativa, sugerem heterogeneidades pré-tratamento
e situam a contribuição. **Não impõem sinal nem magnitude** ao coeficiente do
desenho brasileiro, **não autorizam** linguagem causal sobre o PMM-E e **não
justificam** reescolher amostra, outcome ou janela depois de observar
resultados. O que este documento sugere para o protocolo — seção 9 — só pode
entrar **antes** do congelamento, pela fila de
[`05_identificacao/14`](../05_identificacao/14_plano_implementacao_rdd_bolsa.md).

**Grau de verificação.** Cada estudo leva uma marca:

- **A** — referência e números conferidos na fonte oficial: texto completo,
  página do periódico, resumo em NBER, IZA, RePEc, PubMed ou Europe PMC;
- **B** — referência confirmada, mas o número vem de resumo secundário, de
  versão de working paper diferente da publicada, ou só existe em forma
  qualitativa;
- **C** — não confirmado; listado apenas na seção 10, como pendência.

Número marcado **B** não vai a slide nem a texto do artigo sem conferência.
O levantamento foi feito em 05/10/2026.

## 2. A resposta curta

A literatura empírica **sustenta a direção** da hipótese e **qualifica fortemente
sua forma**. Cinco achados organizam o resto do documento.

1. **Quando a remuneração varia por sorteio ou por regra, a aceitação e o
   recrutamento sobem.** Salário anunciado 33% maior elevou a aceitação em 15,1
   p.p. no México, com elasticidade da oferta perto de 2 (Dal Bó, Finan & Rossi,
   2013); um prêmio de cerca de 10% por regra de escassez deu elasticidade de 1,0
   a 1,9 na Noruega (Falch, 2010); prêmios de 30–40% mudaram a alocação de
   professores qualificados na Gâmbia (Pugatch & Schroeder, 2014). **Embasa o
   termo $\mathbb{E}(w \mid B)$.**
2. **O efeito depende do custo do lugar, e o prêmio compensa parte dele.** No
   México, a distância derruba a aceitação só com salário baixo; acima de 200 km,
   a aceitação vai de 25% a cerca de 80% com a oferta alta. Na Austrália, quem se
   mudaria exige de 37% a 130% da renda anual conforme o posto, e 65% não se
   mudam por nenhum pacote (Scott et al., 2013). **Embasa $c$ e o slide 13: "é a
   soma dos três que decide".**
3. **No RDD mais parecido com o PMM-E, o preenchimento não se moveu; a
   composição, sim.** No Peru, um adicional fixado por regra num cutoff
   censitário de população elevou o salário em cerca de 13%; o efeito sobre a
   probabilidade de a vaga ser preenchida foi 0,063 (EP 0,048), não
   significativo, mas a vaga passou a ser escolhida mais cedo e por professor
   mais bem avaliado, +0,42σ (Bobba et al., NBER WP 29068). **Desafia a margem
   escolhida, não a direção.**
4. **Médicos são menos elásticos que outros profissionais.** No Brasil, a
   elasticidade-salário da escolha locacional de generalistas fica em torno de
   0,4 nas metrópoles e 0,7 no interior, e o incentivo financeiro é a alavanca
   menos custo-efetiva (Costa, Nunes & Sanches, 2024); nos EUA, modelos
   estruturais acham baixa resposta à compensação e forte apego ao local de
   formação (Kulka & McWeeny; Falcettoni). Em 2013, a primeira chamada do
   Mais Médicos, com bolsa de R$ 10 mil, confirmou cerca de 6% das vagas com
   médicos brasileiros — número de imprensa, sem fonte primária localizada.
   **Qualifica a magnitude.**
5. **Atrair não é reter, e vínculo não é acesso.** Os incentivos movem sobretudo
   a entrada de recém-formados, não o estoque de médicos estabelecidos (Yong et
   al., 2018); a retenção pós-obrigação é baixa (Pathman et al., 1992); mais
   médicos não reduziram a espera de pacientes já vinculados (Swami & Scott,
   2021); e no Mais Médicos parte da oferta substituiu a preexistente (Hone et
   al., 2020). **Delimita o que o preenchimento pode e não pode afirmar.**

A leitura que a banca pode levar é a do título da apresentação: **remuneração é
incentivo, e é limitado**. A evidência diz que pagar mais move a escolha, que o
quanto move depende do lugar e da pessoa, e que a margem binária "preencheu ou
não" pode ser a menos sensível delas.

## 3. Evidência por termo do modelo

| Termo do modelo | O que a evidência diz | Estudos principais | Sinal para H1 |
|---|---|---|---|
| $\mathbb{E}(w \mid B)$ — remuneração esperada, deslocada pela bolsa | remuneração anunciada exógena eleva aceitação, recrutamento e qualidade do pool; elasticidade de 1 a 2 fora da medicina, menor entre médicos | Dal Bó et al. (2013); Falch (2010, 2011); Pugatch & Schroeder (2014); Steele et al. (2010); Bobba et al.; Costa et al. (2024) | **reforça a direção**, qualifica a magnitude |
| $\mathbb{E}(w \mid B)$ contra a renda alternativa | o que conta é o salário **relativo** à opção externa local; onde o mercado local paga mais, um salário público uniforme recruta pior | Propper & Van Reenen (2010); Elliott et al. (2007); Britton & Propper (2016) | **reforça H3**: a bolsa pesa mais onde a renda alternativa é menor |
| $p_m$ — nível de preços | salário nominal não é utilidade; uma regra nominal uniforme distorce a alocação espacial | Moretti (2013); Albouy (2009, 2016); Almeida & Azzoni (2016) para o Brasil | **qualifica**: o mesmo R$ 5 mil vale mais onde os preços são menores |
| $c^{geo}$ — distância, família, amenidades | origem e local de formação são os preditores mais robustos da prática em área carente; cônjuge e filhos pesam e variam com o ciclo de vida | Rabinowitz et al. (2001); Costa et al. (2024); McGrail et al. (2017); Kulka & McWeeny; Falcettoni | **qualifica**: compete com a bolsa e é grande |
| $c^{lab}$ — esforço, equipe $L$, capital $K$ | atributos não pecuniários do posto pesam mais que renda; plantão, apoio e equipe mudam o prêmio exigido | Scott et al. (2013); Holte et al. (2015); Chomitz et al. (1998) | **qualifica**: "salário igual em estruturas diferentes não é oferta igual" |
| $\alpha$ — altruísmo e motivação | salário maior não piorou a motivação dos candidatos no México; no Peru, os mais sensíveis a salário eram menos eficazes | Dal Bó et al. (2013); Bobba et al. | **neutro** sobre a direção; muda **quem** vem |
| $\sum_t \delta^t$ — horizonte | o incentivo atrai mais do que retém; programas com obrigação retêm menos no local original | Pathman et al. (1992, 2004); Bärnighausen & Bloom (2009); Steele et al. (2010) | **delimita**: preenchimento não é permanência |

## 4. Prêmios fixados por regra para postos difíceis de prover

É o bloco mais próximo do objeto do PMM-E: **um valor fixado por regra
administrativa, sem negociação individual, que muda num critério territorial**.
A maior parte vem da economia da educação, porque é lá que há regras com cutoff.

| Estudo | País e população | Desenho | Contraste | Achado principal | Verif. |
|---|---|---|---|---|:---:|
| **Bobba, Ederer, León-Ciliotta, Neilson & Nieddu**, *Teacher Compensation and Structural Inequality: Evidence from Centralized Teacher School Choice in Perú*, NBER WP 29068 (2021; revisão consultada de 2026) | Peru, professores contratados da rede pública, escolha centralizada de vagas | **RDD** no cutoff de 500 habitantes do Censo 2007, que define o adicional de escola "extremamente rural" | S/ 500 = 25–36% do salário-base; no cutoff, +S/ 244, cerca de **+13%** | preenchimento **0,063 (EP 0,048)**, não significativo; posição da vaga na ordem de escolha **+0,108 (EP 0,031)**; nota do professor recrutado **+0,42σ (EP 0,106)** (Tab. 2, p. 16); alunos +0,27σ em matemática e +0,21σ em linguagem. Para compensar as amenidades, as escolas mais remotas precisariam de prêmios 2 a 4 vezes maiores. O cutoff de população, censitário, não foi manipulado; o de tempo de viagem foi | A |
| **Dal Bó, Finan & Rossi** (2013), *QJE* 128(3), 1169–1218 | México, agentes de desenvolvimento municipal | **RCT**: salário anunciado sorteado entre locais de recrutamento; oferta de vaga sorteada | 5.000 vs 3.750 pesos/mês, **+33%** | aceitação **+15,1 p.p.** sobre base de 42,9%; elasticidade de oferta **≈ 2,15** (WP; a versão publicada diz "perto de 2"); com oferta baixa, +10 km reduzem a aceitação em 2,7 p.p., com oferta alta a distância quase não pesa; acima de 200 km, **25% contra cerca de 80%**. Sem seleção adversa em motivação | A |
| **Falch** (2010), *Journal of Labor Economics* 28(2), 237–266, doi:10.1086/649905 | Noruega, professores dos três condados do norte, 1993–2003 | efeitos fixos de escola; o prêmio liga e desliga por regra parlamentar de escassez (≥ 30% de docentes sem qualificação) | cerca de **10%** | elasticidade da oferta no nível da escola **≈ 1,4** (faixa de 1,0 a 1,9) | A |
| **Falch** (2011), *American Economic Review* 101(3), 460–465 | idem | escolas que mudam de status | cerca de 10% | saídas **−6 p.p.**; elasticidade de curto prazo **≈ 1¼**; recrutamento +4 a +7 p.p. no WP | A/B |
| **Pugatch & Schroeder** (2014), *Economics of Education Review* 41, 120–136 (IZA DP 7723) | Gâmbia, professores primários | **descontinuidade geográfica** num limiar de distância da estrada principal, com teste de tendências comuns | adicional de **30–40%** do salário | parcela de professores qualificados **+10 p.p.**; alunos por professor qualificado **−27** (61% da média) perto do limiar; o ganho não é só remanejamento entre lados | A |
| **Pugatch & Schroeder** (2018), *Journal of Development Effectiveness* 10(2), 249–276 (IZA DP 8621) | idem | RDD geográfico | 30–40% | desempenho médio dos alunos **nulo**; ganhos no topo, perdas na base | A/B |
| **Cowan & Goldhaber** (2018), *Economics of Education Review* 65, 138–152 | Washington, professores certificados NBPTS | **RDD** no limiar de alunos com almoço subsidiado | **US$ 5.000/ano** | proporção de certificados **+0,7 a 1,6 p.p.** ao ano; nada nas notas | B |
| **Elacqua, Hincapie, Hincapie & Montalva** (2022), *JPAM* 41(2), 603–631, doi:10.1002/pam.22375 | Chile, professores de alto desempenho | **RDD** | cerca de **16%** do salário anual | retenção em escolas desfavorecidas **+17 a 21 p.p.**; não atrai de escolas favorecidas | A |
| **Steele, Murnane & Willett** (2010), *JPAM* 29(3), 451–478, doi:10.1002/pam.20505 | Califórnia, professores novatos | variável instrumental, experimento natural | **US$ 20.000** | **+28 p.p.** na probabilidade de começar em escola de baixo desempenho; retenção de 4 anos de 75% nos **dois** grupos | A |
| **Clotfelter, Glennie, Ladd & Vigdor** (2008), *Journal of Public Economics* 92(5–6), 1352–1370 | Carolina do Norte, professores de matemática, ciências e educação especial | modelos de duração, elegíveis contra não elegíveis | **US$ 1.800/ano** | rotatividade **−17%** (a versão NBER w12285 diz −12%) | A |
| **Glazerman et al.** (2013), NCEE 2014-4003, *Talent Transfer Initiative* | EUA, 10 distritos em 7 estados | **RCT** multissítio | US$ 20.000 em dois anos | notas no fundamental I +4 a +10 percentis; nada no fundamental II. A taxa de preenchimento das vagas-alvo (≈ 90%) só aparece em fonte secundária | A/B |

**O que este bloco ensina sobre o PMM-E.**

- **A direção é robusta e a elasticidade é alta fora da medicina**: 1 a 2. Os
  saltos do PMM-E são grandes em termos relativos — de R$ 10 mil para R$ 15 mil
  é +50%; de R$ 15 mil para R$ 20 mil, +33% —, maiores que os 13% do cutoff
  peruano e próximos dos 33% do México.
- **O preenchimento binário pode ser a margem menos sensível.** No Peru, com
  preenchimento alto dos dois lados, o prêmio agiu sobre **quem** ocupa a vaga e
  **quando**, não sobre **se** ela é ocupada. No PMM-E o preenchimento é baixo —
  30,3% das células na primeira chamada —, o que deixa espaço para a margem
  extensiva; ainda assim, o caso peruano é o argumento para declarar desfechos
  de composição e de rapidez **antes** de olhar os dados.
- **O RDD em regra territorial tem precedente direto.** Peru, Gâmbia, Washington
  e Chile identificam o incentivo marginal num limiar, o mesmo estimando do RDD
  da bolsa. O precedente peruano mostra também o risco: o cutoff censitário,
  fixado antes do programa, não foi manipulado; o administrativo, sim. O IVS
  2010 tem a vantagem do censo; o risco do PMM-E está na **faixa publicada**, que
  fica acima da categoria de IVS em 177 de 368 municípios
  ([`auditorias/07`](../auditorias/07_portao_rdd_bolsa.md)).
- **Spillover entre lados do limiar é testado.** Pugatch & Schroeder e Bobba et
  al. verificam se o ganho de um lado vem de esvaziar o outro. É o papel do
  painel município–mês no plano vigente.

## 5. Médicos: incentivos por área, escolha declarada e modelos estruturais

| Estudo | País e população | Desenho | Achado principal | Verif. |
|---|---|---|---|:---:|
| **Yong, Scott, Gravelle, Sivey & McGrail** (2018), *Soc Sci Med* 214, 197–205, doi:10.1016/j.socscimed.2018.08.014 | Austrália, médicos de família, 2008–2014 | **DiD**: 755 locais que se tornam elegíveis e 787 sempre elegíveis contra 2.249 nunca elegíveis | incentivo de +1,4% da renda no 1º ano a +6,6% após 5 anos; entrada de **recém-formados +0,068 a 0,080** sobre média de 0,15, cerca de +50%; outras entradas caíram; **estoque total e saídas sem efeito** | A |
| **Swami & Scott** (2021), *Soc Sci Med* 281, 114045 | Austrália, mesmo programa | DiD | mais médicos nos locais recém-elegíveis; **nada** na espera dos pacientes já vinculados; evidência fraca de −16% na espera de pacientes novos | A |
| **Khoury, Leganza & Masucci** (2025), *American Journal of Health Economics* 11(3), 487–527, doi:10.1086/729117 | EUA, médicos de atenção primária | DiD pareado na designação de área com escassez (HPSA) | aumento de médicos **em início de carreira**; médicos estabelecidos não se mudam. Identifica o **pacote** — bônus Medicare de 10%, NHSC e outros —, não o bônus isolado | A (sem magnitude) |
| **Bolduc, Fortin & Fournier** (1996), *Journal of Labor Economics* 14(4), 703–732, doi:10.1086/209828 | Quebec, local da primeira prática de médicos de família, 18 regiões | probit multinomial antes e depois da tabela de honorários diferenciada por região | efeito **significativo** dos honorários diferenciados sobre a escolha de local | B (sem magnitude) |
| **Holmes** (2005), *Labour Economics* 12(5), 697–725 | EUA, National Health Service Corps | escolha estrutural com heterogeneidade não observada | sem o NHSC, a oferta em áreas carentes cairia **cerca de 10%** | B |
| **Chan, Donnelly, Sullivan, Pope & Gambhir** (2025), *BJGP Open* 9(3), doi:10.3399/BJGPO.2024.0289 | Escócia, residência em medicina de família, bônus TERS de **£ 20.000** | antes e depois, elegíveis contra não elegíveis; **observacional** | recrutamento de **57,3% para 87,6%**; OR 4,81 (IC 3,87–5,99); só 36% concluíram a formação | A |
| **Chomitz, Setiadi, Azwar, Ismail & Widiyarti** (1998), World Bank PRWP 1888 | Indonésia, médicos em contrato temporário (PTT) | mudança de regra + preferência declarada | dinheiro modesto funciona em áreas moderadamente remotas, **não** nas extremamente remotas; formação especializada compensa melhor; origem pesa | A (sem números) |
| **Scott, Witt, Humphreys, Joyce, Kalb, Jeon & McGrail** (2013), *Soc Sci Med* 96, 33–44, doi:10.1016/j.socscimed.2013.07.002 | Austrália, 3.727 médicos de família | experimento de escolha discreta com opção de ficar | **65%** ficaram em todas as escolhas; quem se mudaria exige **37%** da renda anual para cidade de 5–20 mil hab., **64%** para menos de 5 mil, **≥ 130%** para o pior pacote; o valor depende de plantão, equipe e apoio | A |
| **Holte, Kjær, Abelsen & Olsen** (2015), *Soc Sci Med* 128, 1–9, doi:10.1016/j.socscimed.2014.12.022 | Noruega, 831 estudantes de último ano e internos | escolha discreta + simulações | renda pesa **menos** que atributos não pecuniários; pacotes combinados são necessários | A (qualitativo) |
| **Kulka & McWeeny** (2019), *Rural Physician Shortages and Policy Intervention*, SSRN 3481777 | EUA, condados rurais | DiD no perdão de dívida + modelo de localização | perdão de dívida → **+3 médicos por condado rural**; médicos *"unresponsive to differences in compensation"*, com preferência pelo estado de origem | B (WP) |
| **Falcettoni** (2018), *The Determinants of Physicians' Location Choice: Understanding the Rural Shortage*, job market paper | EUA, residentes no primeiro emprego | equilíbrio espacial estrutural com instrumento | forte preferência por ficar perto da residência médica; redirecionar o gasto de perdão de dívida para salário multiplicaria por 6 os médicos rurais de atenção primária, mas o efeito agregado dos incentivos é pequeno | B (WP, sem publicação localizada) |

**O que este bloco ensina sobre o PMM-E.** Entre médicos, a resposta existe e é
concentrada em **início de carreira** (Yong; Khoury; Steele, no caso dos
professores); o estoque de profissionais estabelecidos responde pouco. O PMM-E
exige RQE, ou seja, especialista já formado, mas a bolsa de 20 h sem vínculo é
compatível com quem mantém a prática principal noutro lugar. Nenhum estudo
deste bloco tem esse regime de dedicação parcial — é o principal limite de
transportabilidade, e é também o motivo de a renda alternativa
(seção 7) importar tanto.

## 6. Brasil e países de renda média

### 6.1 Brasil

| Estudo | Contexto | Desenho | Achado principal | Verif. |
|---|---|---|---|:---:|
| **Costa, Nunes & Sanches** (2024), *REStat* 106(1), 36–52, doi:10.1162/rest_a_01155 | 60.563 generalistas formados entre 2001 e 2013, primeiro emprego | escolha discreta estrutural com coeficientes aleatórios, oferta e demanda | elasticidade-salário **≈ 0,4** nas metrópoles e **≈ 0,7** no interior; salário público **+50%** no interior do N/NE atrai **cerca de 25%** mais médicos e reduz o desequilíbrio em **12,4%**, a US$ 15,7 mi por ponto; cotas por naturalidade, **63,8%**; novas vagas em escolas médicas, 65,9%; infraestrutura +50%, 14% mais médicos e 6,4% do desequilíbrio, a opção menos eficaz e mais cara. Naturalidade e local de formação pesam *"much more … than wages or quality of health infrastructure"* | A (resumo); números no preprint de 2021 |
| **1ª chamada do Programa Mais Médicos**, agosto de 2013 | bolsa de **R$ 10 mil** por 40 h | dado administrativo | **938** médicos confirmados para **15.460** vagas demandadas, **6%**, em 404 municípios; 815 dos 1.753 inscritos recusaram o local alocado | **B** — só imprensa (Estadão, via IHU, com dados do MS de 06/08/2013); falta a fonte primária |
| **Oliveira et al.** (2015), *Interface* 19(54), 623–634 | PMM, PROVAB e PITS | descritivo | em 2014, 14.462 médicos em 3.785 municípios: **1.846 brasileiros** e 12.616 estrangeiros, 11.429 cubanos. PROVAB de **350 para 3.550** médicos entre 2011 e 2013, depois de aumento de bolsa **e** bônus de 10% na prova de residência — sem como isolar a bolsa | A |
| **Girardi et al.** (2016), *Ciência & Saúde Coletiva* 21(9), 2675–2684 | municípios, 03/2013 contra 09/2015 | descritivo com índice de escassez | municípios em escassez de **1.200 para 777** (21,6% → 14%); a oferta municipal regular caiu — substituição | A |
| **Hone et al.** (2020), *BMC HSR* 20, 873, doi:10.1186/s12913-020-05716-2 | 5.565 municípios, 2008–2017 | DiD | **+15,1** médicos do programa por 100 mil (IC 14,9–15,5), **−9,4** dos demais, líquido **+5,7**; mortalidade evitável −1,06 por 100 mil ao ano; 81% dos municípios receberam médicos, contra 46,5% que cumpriam os critérios de prioridade | A |
| **Carrillo & Feres** (2019), *AEJ: Economic Policy* 11(3), 156–196 | PMM | quase-experimental | mais consultas; médicos substituem enfermeiros no pré-natal; **nenhum** ganho em peso ao nascer ou mortalidade infantil | A |
| **Fontes, Conceição & Jacinto** (2018), *Health Economics* 27(8), 1284–1299 | municípios, 2010–2016 | DiD com pareamento | queda de internações por condições sensíveis à atenção primária, maior no 2º ano | A (sem magnitude) |
| **Mattos & Mazetto** (2019), *World Development* 123, 104617 | 2010–2015 | DiD | consultas +9,4%, encaminhamentos +12,3%, hospitalização −4,6%; nada em mortalidade | A |
| **Thomas, Millett, Sousa Soares & Hone** (2024), *Soc Sci Med* 358, 117222 | PMM | controle sintético generalizado | nenhum efeito significativo em internações ou mortalidade; aponta substituição e má alocação na região | A |
| **Scheffer et al.**, *Demografia Médica no Brasil 2025* | médicos | censo e inquérito | 635.706 médicos, 2,98 por mil; no Norte, 3,78 por mil nas capitais contra 0,75 no interior; dupla prática de **72,4%** dos cirurgiões, e só **4,8%** exclusivamente públicos no Norte | A (PDF consultado pelo levantamento; ainda fora de `data/raw/`) |

**Sobre o próprio PMM-E, não há estudo empírico publicado** nem dado oficial de
preenchimento por faixa de IVS, até onde a busca alcançou em 05/10/2026. Os
números de preenchimento do projeto — 30,3% na primeira chamada e 35,6% no ciclo
1 inteiro — são, até onde se sabe, os únicos. A regra da bolsa por IVS foi
conferida no edital publicado no DOU de 24/07/2025, seção 3, p. 145, item
11.1.4; um portal secundário diz que a bolsa varia "por especialidade", o que o
edital desmente.

**O que o Brasil ensina.** O precedente mais próximo é desconfortável para a
hipótese **e** útil para ela. Em 2013, uma bolsa de R$ 10 mil por 40 h — alta
para a época — preencheu cerca de 6% das vagas na primeira chamada com médicos
brasileiros (número só de imprensa), e o programa só se viabilizou com médicos
estrangeiros. Isso é o slide 13 da apresentação em dado: a remuneração entra
com sinal positivo, mas o custo do lugar pode ser maior que ela. E a
substituição documentada por Hone, Girardi e Thomas é o motivo de o plano
vigente exigir o teste de oferta líquida no painel município–mês.

### 6.2 Países de renda baixa e média

| Estudo | País e população | Desenho | Achado principal | Verif. |
|---|---|---|---|:---:|
| **Deserranno** (2019), *AEJ: Applied* 11(1), 277–317, doi:10.1257/app.20170670 | Uganda, agentes de saúde de ONG | **RCT** na remuneração anunciada | pagar mais atrai **mais candidatos** e **aumenta o preenchimento**, mas sinaliza menor retorno social e afasta os pró-sociais, que ficam mais e rendem mais | A (resumo); magnitudes só secundárias |
| **Ashraf, Bandiera, Davenport & Lee** (2020), *AER* 110(5), 1355–1394, doi:10.1257/aer.20180326 | Zâmbia, agentes comunitários de saúde | **RCT** no destaque a benefícios de carreira | atrai mais talento **sem** perda de pró-socialidade na margem; desnutrição infantil −25% | A |
| **Miranda et al.** (2012), *PLoS ONE* 7(12), e50567, doi:10.1371/journal.pone.0050567 | Peru, 102 médicos | escolha discreta rotulada | preferência urbana OR 4,97; +50% de salário com pontos para especialização: adesão rural de **21% para 52%**; +75% com contrato permanente: **77%** | A |
| **Kurniati et al.** (2024), *PLoS ONE* 19(8), e0308225, doi:10.1371/journal.pone.0308225 | Indonésia, **341 especialistas** em hospitais distritais | escolha discreta | segurança **OR 6,11**; formação continuada financiada OR 2,84; instalações avançadas OR 2,35; incentivo financeiro "também recomendado" — **a população mais próxima do PMM-E** que a busca encontrou | A |
| **Kruk et al.** (2010), *Bull WHO* 88(5), 333–341, doi:10.2471/BLT.09.072892 | Gana, 302 estudantes de medicina | escolha discreta, *mixed logit* | equipamento β = 1,42; gestão de apoio β = 1,17; retirar moradia β = −1,59; salário pesa, abaixo das condições de trabalho | A |
| **Kolstad** (2011), *Health Economics* 20(2), 196–211 | Tanzânia, *clinical officers* formandos | escolha discreta | educação continuada é o instrumento mais forte; salário e adicional de dificuldade pesam muito; mulheres menos responsivas a dinheiro | A (sem magnitudes) |
| **Hanson & Jack** (2010), *Health Affairs* 29(8), 1452–1460 | Etiópia, médicos e enfermeiros | escolha discreta | para médicos, salário e moradia; para enfermeiros, equipamento e insumos | A (sem magnitudes) |
| **Serneels et al.** (2010), *Bull WHO* 88(5), 342–349, doi:10.2471/BLT.09.072728 | Ruanda e Etiópia | salário de reserva para o posto rural | motivação intrínseca, origem rural e vínculo religioso **reduzem** o salário exigido | A (sem magnitudes) |
| **Mandeville et al.** (2016), *Soc Sci Med* 169, 109–118 | Malawi, 148 médicos jovens | escolha discreta | exigem quase 2 vezes o salário mensal para aceitar formação só no país, e mais de 6 vezes para oftalmologia | A |
| **Lagarde & Blaauw** (2009), *Human Resources for Health* 7, 62 | revisão de 10 DCEs | revisão | incentivos não pecuniários *"sometimes more powerful than financial ones"* | A |
| **Mandeville, Lagarde & Hanson** (2014), *BMC Health Services Research* 14, 367, doi:10.1186/1472-6963-14-367 | revisão de 27 DCEs | revisão sistemática | bônus e formação pós-graduada importam; só um terço dos estudos tinha opção de não aceitar nenhum posto — o que **superestima** a resposta | A |
| **Grobler, Marais & Mabunda** (2015), Cochrane CD005314.pub3 | revisão | revisão sistemática com critérios Cochrane | **um** estudo elegível; certeza muito baixa; *"limited reliable evidence"* | A |
| **OMS** (2010; 2021), recomendações para áreas rurais e remotas | global | diretrizes | incentivo financeiro recomendado **em pacote**, com qualidade de evidência baixa | A |

**O que este bloco ensina.** Fora do Brasil, a resposta positiva à remuneração
é a regra, mas raramente a maior: equipamento, gestão, segurança, formação e
carreira competem com o salário e muitas vezes o superam. O único estudo com
**especialistas em exercício** (Kurniati et al., Indonésia) põe segurança e
instalações à frente da renda — o que dá conteúdo empírico ao custo laboral de
Choné & Ma, $C(q; L, K)$. E a revisão de Mandeville et al. lembra que boa parte
dessa evidência é de preferência declarada **sem opção de recusa**, que
superestima a resposta ao preço — exatamente o contrário do que a margem de
preenchimento do PMM-E mede.

## 7. Salário real, regulação uniforme e renda alternativa

| Estudo | Contexto | Desenho | Achado principal | Verif. |
|---|---|---|---|:---:|
| **Propper & Van Reenen** (2010), *Journal of Political Economy* 118(2), 222–273 | Inglaterra, 209 hospitais, salário de enfermagem regulado e quase uniforme | painel; salário regulado contra salário externo local | **+10%** no salário externo local → **+4% a 8%** na mortalidade por infarto em 30 dias; o canal passa por recrutamento e retenção, com substituição por temporários; placebo em setores sem regulação dá nulo | A |
| **Elliott, Ma, Scott, Bell & Roberts** (2007), *Journal of Health Economics* 26(1), 190–212, doi:10.1016/j.jhealeco.2006.05.002 | Grã-Bretanha, enfermeiros do NHS | regressão com mudança de regime | quanto menor a competitividade do salário regulado frente ao mercado local, **maior a vacância de longo prazo** | B (sem coeficientes) |
| **Britton & Propper** (2016), *Journal of Public Economics* 133, 75–89 | Inglaterra, mais de 3.000 escolas | regulação salarial centralizada contra salário local | choque de 10% no hiato salário local–salário docente → perda média de cerca de **2%** no desempenho | A |
| **Moretti** (2013), *AEJ: Applied* 5(1), 65–103, doi:10.1257/app.5.1.65 | EUA, 1980–2000 | deflatores locais de custo de vida | o prêmio **real** de escolaridade cresceu bem menos que o nominal, porque os qualificados se concentraram em cidades caras | A (direção) |
| **Albouy** (2009), *JPE* 117(4), 635–667 | EUA | equilíbrio espacial com imposto federal nominal | uma regra nominal uniforme pesa mais onde salários nominais são altos e reduz o emprego de longo prazo ali | B |
| **Albouy** (2016), *REStat* 98(3), 477–487, doi:10.1162/REST_a_00550 | EUA, áreas metropolitanas | salários e moradia → produtividade, qualidade de vida | diferenciais de salário e moradia refletem mais produtividade que amenidades | B |
| **Almeida & Azzoni** (2016), *Estudos Econômicos* 46(1), 253–276, doi:10.1590/0101-416146128aaa | Brasil, 11 regiões metropolitanas, POFs de 1996, 2003 e 2009 | *Country Product Dummy* | custo de vida mais alto em Brasília, São Paulo e Rio; hierarquia estável no período | A (qualitativo) |
| **Socha & Bech** (2011), *Health Policy* 102(1), 1–7, doi:10.1016/j.healthpol.2010.10.017 | revisão, 23 trabalhos | revisão | dupla prática motivada sobretudo por renda; evidência empírica escassa e sem magnitudes | A |
| **McGrail, Russell & O'Sullivan** (2017), *Human Resources for Health* 15, 75, doi:10.1186/s12960-017-0250-z | Austrália, 4.377 médicos de família, 2008–2014 | painel | filho no ensino médio reduz a chance de prática rural dos médicos (OR 0,83–0,90); cônjuge empregado reduz a das médicas (OR 0,89) | A |

**A implicação do deflator para o PMM-E.** A bolsa é **nominal e uniforme por
faixa**; o valor real é $B_k/p_m$. Três consequências.

1. **O gradiente real é mais íngreme que o nominal, se os preços caem com a
   vulnerabilidade.** Dentro da mesma faixa, municípios mais baratos recebem
   bolsa real maior; entre faixas, os R$ 5 mil somam-se a um $p_m$ menor. Mas
   num contraste local na fronteira de faixa, $p_m$ é **contínuo**: o deflator
   não cria nem destrói a descontinuidade, muda a leitura da magnitude.
2. **A cesta do especialista não é a cesta média.** Escola dos filhos, moradia
   de padrão aceitável num mercado de aluguel raso e o deslocamento de quem
   mantém residência na capital e cumpre as 20 h no interior podem ser **mais
   caros** no município vulnerável. O sinal efetivo de $p_m$ para o médico é
   empírico.
3. **Preço e renda alternativa são canais diferentes.** Em Propper & Van Reenen
   o que pesa é o salário externo local. Para o especialista em dupla prática,
   $\mathbb{E}(w \mid B) = B + w^{priv}_m$: onde o mercado privado é pequeno, a
   bolsa pesa mais **em proporção**, e a renda total é menor. Os dois efeitos
   têm sinais opostos sobre a atratividade; é a leitura territorial de H3.

**Não há índice de preços municipal oficial** que cubra os municípios pequenos
onde estão as vagas. A POF citada no apêndice da apresentação dá, no máximo,
diferenças por UF ou região metropolitana. Qualquer $p_m$ construído — aluguel
do Censo, por exemplo — é **construção do autor**, e entra com fonte, hash e
rótulo, como manda o `CLAUDE.md`.

## 8. Atração, permanência e acesso

| Estudo | Achado | Verif. |
|---|---|:---:|
| **Pathman, Konrad & Ricketts** (1992), *JAMA* 268(12), 1552–1558 | após oito anos, **12%** dos médicos do NHSC seguiam na prática original, contra **39%** dos demais; 29% contra 52% em prática não metropolitana | A |
| **Pathman, Konrad, Dann & Koch** (2004), *AJPH* 94(10), 1723–1729, doi:10.2105/ajph.94.10.1723 | retenção em áreas com escassez semelhante à de fora delas (HR 1,28; IC95% 0,97–1,69): o gargalo seria **recrutar**, não reter | A |
| **Bärnighausen & Bloom** (2009), *BMC HSR* 9, 86 | 43 estudos; **71%** cumpriram a obrigação; em 6 de 7 estudos os participantes ficaram **menos** no mesmo local e, em 11 de 13, **mais** em alguma área carente; sem inferência causal | A |
| **Rabinowitz, Diamond, Markham & Paynter** (2001), *JAMA* 286(9), 1041–1048 | ter crescido em área rural prediz prática rural, **OR 4,0** (IC95% 2,1–7,6), na coorte 1978–1982; para retenção, o preditor é o programa de admissão seletiva, **OR 4,7** (2,0–11,2) | A |
| **Steele, Murnane & Willett** (2010) | +28 p.p. na entrada, **nenhum** efeito na retenção de 4 anos | A |
| **Yong et al.** (2018); **Swami & Scott** (2021) | entrada de recém-formados sobe; estoque e espera dos pacientes vinculados não mudam | A |

Para o projeto, isto confirma duas regras do `CLAUDE.md` com evidência externa:
**oferta persistente no CNES não é retenção individual**, e **vínculo,
produção, acesso e espera não são sinônimos**. A hipótese apresentada fala de
preenchimento — o primeiro elo —, e a literatura diz que é nele que o incentivo
tem mais chance de aparecer.

## 9. O que a literatura sugere para o protocolo, antes do congelamento

Sugestões, não decisões. Entram pela fila RDD
([`05_identificacao/14`](../05_identificacao/14_plano_implementacao_rdd_bolsa.md))
**antes** de qualquer consulta a outcome, ou não entram.

1. **Desfechos secundários de composição e rapidez**, ao lado do preenchimento:
   tempo até a homologação, número de candidatos por célula, chamada em que a
   célula foi preenchida, e perfil do médico homologado (tempo de formado,
   distância entre o município e o local de formação ou de residência, quando
   houver dado). É a lição de Bobba et al.
2. **Heterogeneidade pré-tratamento pela distância** entre o município da vaga e
   a capital ou o polo — o análogo dos 200 km de Dal Bó et al. —, fixada com
   dados anteriores ao programa.
3. **Teste de deslocamento entre lados do limiar**, no painel município–mês,
   como em Pugatch & Schroeder e Bobba et al.
4. **Expectativa de magnitude.** Com elasticidades de 0,4–0,7 para médicos no
   Brasil e um degrau de +33% a +50%, uma resposta de **algumas** dezenas por
   cento sobre a base, e não de dobrar o preenchimento, é o que a literatura
   torna plausível. Serve para calcular poder, não para julgar resultado.

## 10. Pendências de verificação

| Item | O que falta |
|---|---|
| Dal Bó et al. (2013) | conferir 15,1 p.p. e 2,15 nas tabelas da versão publicada (conferidos no NBER WP 18156) |
| Falch (2011) | resolver o DOI e conferir o +4 a +7 p.p. de recrutamento na versão publicada |
| Pugatch & Schroeder (2014, 2018) | DOI e tabelas no periódico |
| Cowan & Goldhaber (2018) | abrir o artigo; números vistos só no resumo |
| Glazerman et al. (2013) | a taxa de preenchimento de ≈ 90% só em fonte secundária |
| Bolduc et al. (1996); Khoury et al. (2025) | magnitudes |
| Holmes (2005) | o ≈ 10% só em resumo secundário |
| Elliott et al. (2007) | coeficientes |
| Scott et al. (2013); Holte et al. (2015) | coeficientes por atributo — plantão, cônjuge, escola dos filhos |
| Falcettoni; Kulka & McWeeny | versões publicadas |
| Bônus Medicare HPSA isolado; adicionais de difícil acesso para saúde em Gana, Zâmbia e Quênia | nenhum estudo quase-experimental localizado |
| 1ª chamada do PMM, 2013 (938 de 15.460) | fonte primária do MS, TCU ou OPAS; hoje só imprensa |
| Costa, Nunes & Sanches (2024) | conferir na versão publicada os números do preprint de 2021 (≈ 25% mais médicos; 65,9%; US$ 94,2 mi) |
| Deserranno (2019) | magnitudes (36% mais candidatos; +13 p.p. de permanência) só em fonte secundária |
| Hone et al. (2020) | números por subgrupo prioritário/não prioritário: reler a tabela original |
| PITS (2001) | números de adesão |
| Chan et al. (2025); Khoury et al. (2025); Kurniati et al. (2024); Thomas et al. (2024); Miranda et al. (2012) | títulos exatos; as referências estão identificadas pelo DOI |
| *Demografia Médica* | percentuais de dupla prática na fonte primária, e o PDF de 2025 em `data/raw/` (pendência `P5` da banca 1) |

## 11. Referências

As referências do [catálogo 19](19_literatura_empirica_escolha_locacional_medicos.md#9-referências)
não são repetidas. Novas neste documento:

- Albouy, D. (2009). *The Unequal Geographic Burden of Federal Taxation*. **Journal of Political Economy**, 117(4), 635–667.
- Albouy, D. (2016). [*What Are Cities Worth? Land Rents, Local Productivity, and the Total Value of Amenities*](https://doi.org/10.1162/REST_a_00550). **The Review of Economics and Statistics**, 98(3), 477–487.
- Almeida, A. N.; Azzoni, C. R. (2016). [*Custo de vida comparativo das regiões metropolitanas brasileiras: 1996-2014*](https://doi.org/10.1590/0101-416146128aaa). **Estudos Econômicos**, 46(1), 253–276.
- Ashraf, N.; Bandiera, O.; Davenport, E.; Lee, S. S. (2020). [*Losing Prosociality in the Quest for Talent? Sorting, Selection, and Productivity in the Delivery of Public Services*](https://doi.org/10.1257/aer.20180326). **American Economic Review**, 110(5), 1355–1394.
- Bobba, M.; Ederer, T.; León-Ciliotta, G.; Neilson, C.; Nieddu, M. G. (2021). [*Teacher Compensation and Structural Inequality: Evidence from Centralized Teacher School Choice in Perú*](https://www.nber.org/papers/w29068). **NBER Working Paper** 29068.
- Bolduc, D.; Fortin, B.; Fournier, M.-A. (1996). [*The Effect of Incentive Policies on the Practice Location of Doctors: A Multinomial Probit Analysis*](https://doi.org/10.1086/209828). **Journal of Labor Economics**, 14(4), 703–732.
- Britton, J.; Propper, C. (2016). [*Teacher Pay and School Productivity: Exploiting Wage Regulation*](https://ideas.repec.org/a/eee/pubeco/v133y2016icp75-89.html). **Journal of Public Economics**, 133, 75–89.
- Chan, K.; Donnelly, C.; Sullivan, F.; Pope, L.; Gambhir, M. (2025). Avaliação do *Targeted Enhanced Recruitment Scheme* na Escócia (título a conferir). **BJGP Open**, 9(3). [doi:10.3399/BJGPO.2024.0289](https://doi.org/10.3399/BJGPO.2024.0289).
- Chomitz, K. M.; Setiadi, G.; Azwar, A.; Ismail, N.; Widiyarti (1998). [*What Do Doctors Want? Developing Incentives for Doctors to Serve in Indonesia's Rural and Remote Areas*](https://ideas.repec.org/p/wbk/wbrwps/1888.html). **World Bank Policy Research Working Paper** 1888.
- Clotfelter, C.; Glennie, E.; Ladd, H.; Vigdor, J. (2008). [*Would Higher Salaries Keep Teachers in High-Poverty Schools? Evidence from a Policy Intervention in North Carolina*](https://ideas.repec.org/a/eee/pubeco/v92y2008i5-6p1352-1370.html). **Journal of Public Economics**, 92(5–6), 1352–1370.
- Cowan, J.; Goldhaber, D. (2018). [*Do Bonuses Affect Teacher Staffing and Student Achievement in High-Poverty Schools? Evidence from an Incentive for National Board Certified Teachers in Washington State*](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6088508/). **Economics of Education Review**, 65, 138–152.
- Elacqua, G.; Hincapie, D.; Hincapie, I.; Montalva, V. (2022). [*Can Financial Incentives Help Disadvantaged Schools to Attract and Retain High-Performing Teachers? Evidence from Chile*](https://doi.org/10.1002/pam.22375). **Journal of Policy Analysis and Management**, 41(2), 603–631.
- Elliott, R. F.; Ma, A. H. Y.; Scott, A.; Bell, D.; Roberts, E. (2007). [*Geographically Differentiated Pay in the Labour Market for Nurses*](https://doi.org/10.1016/j.jhealeco.2006.05.002). **Journal of Health Economics**, 26(1), 190–212.
- Falch, T. (2010). [*The Elasticity of Labor Supply at the Establishment Level*](https://doi.org/10.1086/649905). **Journal of Labor Economics**, 28(2), 237–266.
- Falch, T. (2011). *Teacher Mobility Responses to Wage Changes: Evidence from a Quasi-Natural Experiment*. **American Economic Review: Papers & Proceedings**, 101(3), 460–465.
- Falcettoni, E. (2018). *The Determinants of Physicians' Location Choice: Understanding the Rural Shortage*. Job market paper, University of Minnesota.
- Glazerman, S.; Protik, A.; Teh, B.; Bruch, J.; Max, J. (2013). [*Transfer Incentives for High-Performing Teachers: Final Results from a Multisite Randomized Experiment*](https://ies.ed.gov/use-work/resource-library/report/evaluation-report/transfer-incentives-high-performing-teachers-final-results-multisite-randomized-experiment). NCEE 2014-4003, Institute of Education Sciences.
- Holmes, G. M. (2005). [*Increasing Physician Supply in Medically Underserved Areas*](https://ideas.repec.org/a/eee/labeco/v12y2005i5p697-725.html). **Labour Economics**, 12(5), 697–725.
- Holte, J. H.; Kjær, T.; Abelsen, B.; Olsen, J. A. (2015). [*The Impact of Pecuniary and Non-Pecuniary Incentives for Attracting Young Doctors to Rural General Practice*](https://doi.org/10.1016/j.socscimed.2014.12.022). **Social Science & Medicine**, 128, 1–9.
- Khoury, S.; Leganza, J. M.; Masucci, A. (2025). Designação de HPSA e localização de médicos (título a conferir). **American Journal of Health Economics**, 11(3), 487–527. [doi:10.1086/729117](https://doi.org/10.1086/729117).
- Kulka, A.; McWeeny, D. (2019). [*Rural Physician Shortages and Policy Intervention*](https://papers.ssrn.com/abstract=3481777). SSRN Working Paper 3481777.
- McGrail, M. R.; Russell, D. J.; O'Sullivan, B. G. (2017). [*Family Effects on the Rurality of GP's Work Location: A Longitudinal Panel Study*](https://doi.org/10.1186/s12960-017-0250-z). **Human Resources for Health**, 15, 75.
- Moretti, E. (2013). [*Real Wage Inequality*](https://doi.org/10.1257/app.5.1.65). **American Economic Journal: Applied Economics**, 5(1), 65–103.
- Pathman, D. E.; Konrad, T. R.; Dann, R.; Koch, G. (2004). [*Retention of Primary Care Physicians in Rural Health Professional Shortage Areas*](https://doi.org/10.2105/ajph.94.10.1723). **American Journal of Public Health**, 94(10), 1723–1729.
- Propper, C.; Van Reenen, J. (2010). [*Can Pay Regulation Kill? Panel Data Evidence on the Effect of Labor Markets on Hospital Performance*](https://www.nber.org/papers/w13776). **Journal of Political Economy**, 118(2), 222–273.
- Pugatch, T.; Schroeder, E. (2014). [*Incentives for Teacher Relocation: Evidence from the Gambian Hardship Allowance*](https://www.iza.org/en/publications/dp/7723/incentives-for-teacher-relocation-evidence-from-the-gambian-hardship-allowance). **Economics of Education Review**, 41, 120–136.
- Pugatch, T.; Schroeder, E. (2018). [*Teacher Pay and Student Performance: Evidence from the Gambian Hardship Allowance*](https://www.iza.org/publications/dp/8621). **Journal of Development Effectiveness**, 10(2), 249–276.
- Rabinowitz, H. K.; Diamond, J. J.; Markham, F. W.; Paynter, N. P. (2001). [*Critical Factors for Designing Programs to Increase the Supply and Retention of Rural Primary Care Physicians*](https://doi.org/10.1001/jama.286.9.1041). **JAMA**, 286(9), 1041–1048.
- Socha, K. Z.; Bech, M. (2011). [*Physician Dual Practice: A Review of Literature*](https://doi.org/10.1016/j.healthpol.2010.10.017). **Health Policy**, 102(1), 1–7.
- Steele, J. L.; Murnane, R. J.; Willett, J. B. (2010). [*Do Financial Incentives Help Low-Performing Schools Attract and Keep Academically Talented Teachers? Evidence from California*](https://doi.org/10.1002/pam.20505). **Journal of Policy Analysis and Management**, 29(3), 451–478.
- Carrillo, B.; Feres, J. (2019). [*Provider Supply, Utilization, and Infant Health: Evidence from a Physician Distribution Policy*](https://ideas.repec.org/a/aea/aejpol/v11y2019i3p156-96.html). **American Economic Journal: Economic Policy**, 11(3), 156–196.
- Deserranno, E. (2019). [*Financial Incentives as Signals: Experimental Evidence from the Recruitment of Village Promoters in Uganda*](https://doi.org/10.1257/app.20170670). **American Economic Journal: Applied Economics**, 11(1), 277–317.
- Fontes, L. F. C.; Conceição, O. C.; Jacinto, P. A. (2018). [*Evaluating the Impact of Physicians' Provision on Primary Healthcare: Evidence from Brazil's More Doctors Program*](https://ideas.repec.org/a/wly/hlthec/v27y2018i8p1284-1299.html). **Health Economics**, 27(8), 1284–1299.
- Girardi, S. N. et al. (2016). [*Impacto do Programa Mais Médicos na redução da escassez de médicos em Atenção Primária à Saúde*](https://www.redalyc.org/pdf/630/63047411007.pdf). **Ciência & Saúde Coletiva**, 21(9), 2675–2684.
- Grobler, L.; Marais, B. J.; Mabunda, S. (2015). [*Interventions for increasing the proportion of health professionals practising in rural and other underserved areas*](https://doi.org/10.1002/14651858.CD005314.pub3). **Cochrane Database of Systematic Reviews**, CD005314.
- Hanson, K.; Jack, W. (2010). *Incentives Could Induce Ethiopian Doctors and Nurses to Work in Rural Settings*. **Health Affairs**, 29(8), 1452–1460.
- Kolstad, J. R. (2011). *How to Make Rural Jobs More Attractive to Health Workers: Findings from a Discrete Choice Experiment in Tanzania*. **Health Economics**, 20(2), 196–211.
- Kruk, M. E. et al. (2010). [*Rural practice preferences among medical students in Ghana: a discrete choice experiment*](https://doi.org/10.2471/BLT.09.072892). **Bulletin of the World Health Organization**, 88(5), 333–341.
- Kurniati, A. et al. (2024). Experimento de escolha discreta com especialistas de hospitais distritais na Indonésia (título a conferir). **PLoS ONE**, 19(8), e0308225. [doi:10.1371/journal.pone.0308225](https://doi.org/10.1371/journal.pone.0308225).
- Lagarde, M.; Blaauw, D. (2009). [*A review of the application and contribution of discrete choice experiments to inform human resources policy interventions*](https://doi.org/10.1186/1478-4491-7-62). **Human Resources for Health**, 7, 62.
- Mandeville, K. L.; Lagarde, M.; Hanson, K. (2014). [*The use of discrete choice experiments to inform health workforce policy: a systematic review*](https://doi.org/10.1186/1472-6963-14-367). **BMC Health Services Research**, 14, 367.
- Mandeville, K. L. et al. (2016). *Can policymakers influence the career choices of young doctors? A discrete choice experiment in Malawi*. **Social Science & Medicine**, 169, 109–118.
- Mattos, E.; Mazetto, D. (2019). [*Assessing the impact of more doctors' program on healthcare indicators in Brazil*](https://ideas.repec.org/a/eee/wdevel/v123y2019ic6.html). **World Development**, 123, 104617.
- Miranda, J. J. et al. (2012). Experimento de escolha discreta rotulado sobre preferências rurais de médicos no Peru (título a conferir). **PLoS ONE**, 7(12), e50567. [doi:10.1371/journal.pone.0050567](https://doi.org/10.1371/journal.pone.0050567).
- Oliveira, F. P. et al. (2015). [*Mais Médicos: um programa brasileiro em uma perspectiva internacional*](https://www.redalyc.org/pdf/1801/180141076018.pdf). **Interface — Comunicação, Saúde, Educação**, 19(54), 623–634.
- Serneels, P. et al. (2010). [*Who wants to work in a rural health post? The role of intrinsic motivation, rural background and faith-based institutions in Ethiopia and Rwanda*](https://doi.org/10.2471/BLT.09.072728). **Bulletin of the World Health Organization**, 88(5), 342–349.
- Swami, M.; Scott, A. (2021). [*Impact of rural workforce incentives on access to GP services*](https://doi.org/10.1016/j.socscimed.2021.114045). **Social Science & Medicine**, 281, 114045.
- Thomas, T.; Millett, C.; Sousa Soares, R.; Hone, T. (2024). Avaliação do Programa Mais Médicos por controle sintético generalizado (título a conferir). **Social Science & Medicine**, 358, 117222.
- World Health Organization (2021). *WHO guideline on health workforce development, attraction, recruitment and retention in rural and remote areas*. WHO, Geneva.
