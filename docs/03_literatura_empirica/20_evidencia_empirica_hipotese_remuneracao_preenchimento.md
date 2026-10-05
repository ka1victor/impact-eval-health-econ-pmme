# 20. Evidência empírica sobre a hipótese: remuneração oferecida e preenchimento de vagas

> **Classificação:** literatura empírica — fichamento<br>
> **Hipótese em exame:** *"municípios com maior remuneração oferecida pelo PMM-E
> têm maior preenchimento de vagas"* — slide 15 da
> [versão apresentada](../07_apresentacoes/banca1/04_versao_apresentada.md);
> forma canônica **H1**, $\partial\Pr(\text{aceitar})/\partial B_m > 0$, em
> [`02_teoria/hipoteses_e_viabilidade_empirica.md`](../02_teoria/hipoteses_e_viabilidade_empirica.md), §4<br>
> **Modelo de referência:** $\max_m \sum_t \delta^t \left[\mathbb{E}(w_{mt}\mid B)/p_{mt} - c_{im}\right]$,
> com $c$ = custo geográfico + custo laboral ([`modelo_micro.md`](../02_teoria/modelo_micro.md))<br>
> **Complementa:** [`19_literatura_empirica_escolha_locacional_medicos.md`](19_literatura_empirica_escolha_locacional_medicos.md)<br>
> **Atualização:** 5 de outubro de 2026 — 60 estudos com método e conclusão
> conferidos na fonte

## 1. Como ler este documento

**Regra de uso.** Vale a do [catálogo 19](19_literatura_empirica_escolha_locacional_medicos.md#1-regra-de-uso).
Os estudos daqui calibram expectativa, sugerem heterogeneidades pré-tratamento
e situam a contribuição. Eles **não impõem sinal nem magnitude** ao coeficiente
do desenho brasileiro, **não autorizam** linguagem causal sobre o PMM-E e **não
justificam** reescolher amostra, outcome ou janela depois de observar
resultados.

**Organização.** A seção 2 é o **quadro-resumo**: uma linha por estudo, com
método e conclusão. A seção 3 traz as **fichas**, agrupadas em sete blocos, com
o mesmo roteiro em todas:

| Campo | O que traz |
|---|---|
| **Referência** | periódico, volume, páginas e DOI |
| **Pergunta** | o que o estudo quer saber, em uma frase |
| **Dados** | fonte, país, período, unidade e tamanho |
| **Método** | a variação usada, o grupo de comparação, a hipótese de identificação e o que é estimado |
| **Resultado** | os números centrais, com erro-padrão ou intervalo quando há |
| **Conclusão dos autores** | paráfrase e uma citação literal do resumo |
| **Limitações** | as que os autores apontam ou que o desenho impõe |
| **Para a hipótese** | ✅ reforça · ⚠️ qualifica · ➖ delimita — o que o estudo diz sobre H1 |
| **Verificação** | **A**: conferido na fonte oficial (periódico, NBER, IZA, RePEc, PubMed, Europe PMC ou texto integral); **B**: só em fonte secundária, ou número de versão diferente da publicada |

As seções 4 a 6 trazem a síntese para a hipótese, as sugestões para o protocolo
e as pendências de verificação. **Número marcado B não vai a slide nem a texto
do artigo sem conferência.**

**Classificação dos métodos.** Do mais forte para o mais fraco, para a
pergunta "a remuneração causa preenchimento?":

| Classe | Métodos | Estudos |
|---|---|---|
| **Experimento** | salário ou anúncio sorteado | A2, A11, D1, D2 |
| **Descontinuidade** | RDD na regra que fixa o adicional | A1, A5, A6, A7, A8 |
| **Quase-experimento** | DiD, efeitos fixos sobre mudança de regra, variável instrumental, controle sintético | A3, A4, A9, A10, B1, B2, B3, C2, C6, C7, C8, C9, E1, E3 |
| **Modelo estrutural** | escolha discreta estimada com dados reais e contrafactuais | B4, B5, B9, B10, C1, E5, E6, G1 |
| **Preferência declarada** | experimento de escolha discreta, valoração contingente | B7, B8, B11, D3–D10 |
| **Observacional e descritivo** | coorte, antes e depois, estudo de caso, medição | B6, C3, C4, C5, D14, E2, E4, E7, E9, F1, F2, F4, G2 |
| **Revisão** | narrativa ou sistemática | D11, D12, D13, E8, F3 |

## 2. Quadro-resumo

| # | Estudo | País | Método | Conclusão | H1 |
|:---:|---|---|---|---|:---:|
| | **A. Prêmios por regra e salário anunciado** | | | | |
| A1 | Bobba et al. (NBER 2021, rev. 2026) | Peru | RDD no corte censitário de 500 hab. que define adicional de +13% | o adicional **não** mudou o preenchimento (0,063, EP 0,048), mas trouxe professor melhor (+0,42 dp) e mais aprendizagem | ⚠️ |
| A2 | Dal Bó, Finan & Rossi (2013), *QJE* | México | salário anunciado sorteado (+33%) | aceitação +15,1 p.p.; elasticidade ≈ 2; salário alto anula o efeito da distância; sem perda de motivação | ✅ |
| A3 | Falch (2010), *JOLE* | Noruega | efeitos fixos sobre prêmio de ~10% que liga e desliga por regra | elasticidade da oferta à escola ≈ 1,4 | ✅ |
| A4 | Falch (2011), *AER P&P* | Noruega | idem, sobre saídas | saída voluntária −6 p.p.; elasticidade ≈ 1¼ | ✅ |
| A5 | Pugatch & Schroeder (2014), *EER* | Gâmbia | DiD e RD *fuzzy* no corte de 3 km da estrada; adicional de 30–40% | professores qualificados +10 p.p.; ganho menor nas escolas mais remotas | ✅ |
| A6 | Pugatch & Schroeder (2018), *JDE* | Gâmbia | RD *fuzzy*, mesmo corte | desempenho médio dos alunos nulo | ➖ |
| A7 | Cowan & Goldhaber (2018), *EER* | EUA | RD *fuzzy* no % de alunos pobres; bônus de US$ 5 mil | certificados +1,2 p.p. ao ano; nada nas notas | ✅ |
| A8 | Elacqua et al. (2022), *JPAM* | Chile | RD na nota do portfólio; prêmio de ~16% | retém quem já está (+17 a 21 p.p.), não atrai de fora | ⚠️ |
| A9 | Steele, Murnane & Willett (2010), *JPAM* | EUA | variável instrumental; bolsa de US$ 20 mil | entrada +28 p.p.; retenção igual (75%) | ✅ |
| A10 | Clotfelter et al. (2008), *JPubE* | EUA | modelos de risco com variação tripla; bônus de US$ 1.800 | rotatividade −17% | ✅ |
| A11 | Glazerman et al. (2013), NCEE | EUA | experimento; US$ 20 mil para transferir | 88% das vagas preenchidas; retenção só enquanto paga | ✅ |
| | **B. Médicos em países de alta renda** | | | | |
| B1 | Yong et al. (2018), *SSM* | Austrália | DiD na mudança de elegibilidade de 2010 | recém-formados +50%; outras entradas caem; estoque não muda | ⚠️ |
| B2 | Swami & Scott (2021), *SSM* | Austrália | DiD, mesma reforma | mais médicos, espera igual para quem já era paciente | ➖ |
| B3 | Khoury, Leganza & Masucci (2025), *AJHE* | EUA | DiD pareado na designação de área de escassez (pacote) | mais médicos em início de carreira; experientes não se mudam | ⚠️ |
| B4 | Bolduc, Fortin & Fournier (1996), *JOLE* | Canadá | probit multinomial espacial, antes e depois | remuneração diferenciada por região afetou a escolha de local | ✅ |
| B5 | Holmes (2005), *Labour Econ* | EUA | logit multinomial com seleção | sem o NHSC, −10% de médicos em áreas carentes | ✅ |
| B6 | Chan et al. (2025), *BJGP Open* | Escócia | antes e depois, elegíveis contra não elegíveis; bolsa de £ 20 mil | preenchimento de 57% para 88% (associação) | ✅ |
| B7 | Scott et al. (2013), *SSM* | Austrália | experimento de escolha com opção de ficar | 65% não se mudam; os demais pedem de 37% a 130% da renda | ⚠️ |
| B8 | Holte et al. (2015), *SSM* | Noruega | experimento de escolha | renda pesa menos que atributos não pecuniários | ⚠️ |
| B9 | Kulka & McWeeny (2019), SSRN | EUA | DiD + modelo estrutural | médicos pouco sensíveis a salário; preferem o estado de origem | ⚠️ |
| B10 | Falcettoni (2018), JMP | EUA | equilíbrio espacial estrutural com instrumento | salário é melhor que perdão de dívida, mas o efeito agregado é pequeno | ⚠️ |
| B11 | Sivey et al. (2012), *JHE* | Austrália | experimento de escolha (especialidade) | elasticidade-renda da escolha de especialidade 0,95 | — |
| | **C. Brasil** | | | | |
| C1 | Costa, Nunes & Sanches (2024), *REStat* | Brasil | logit estrutural de coeficientes aleatórios com instrumento | elasticidade 0,4–0,7; salário é a alavanca menos custo-efetiva; origem pesa mais | ⚠️ |
| C2 | Hone et al. (2020), *BMC HSR* | Brasil | DiD com estudo de evento | +15,1 médicos do programa, mas só +5,7 líquido | ➖ |
| C3 | Girardi et al. (2016), *C&SC* | Brasil | antes e depois, índice de escassez | escassez caiu, com substituição da oferta municipal | ➖ |
| C4 | Oliveira et al. (2015), *Interface* | Brasil | análise comparativa | em 2014, 1.846 brasileiros e 12.616 estrangeiros no PMM | ⚠️ |
| C5 | Santos, Costa & Girardi (2015), *C&SC* | Brasil | ensaio descritivo | escassez −53,5% até 2014 | — |
| C6 | Carrillo & Feres (2019), *AEJ: Policy* | Brasil | DiD | mais consultas; nada na saúde infantil | ➖ |
| C7 | Fontes, Conceição & Jacinto (2018), *Health Econ* | Brasil | DiD com pareamento | menos internações sensíveis à atenção primária | — |
| C8 | Mattos & Mazetto (2019), *World Dev* | Brasil | DiD | mais atendimentos, menos internações; mortalidade igual | — |
| C9 | Thomas et al. (2024), *SSM* | Brasil | controle sintético generalizado | nenhum efeito em internações ou mortalidade | ➖ |
| | **D. Países de renda baixa e média** | | | | |
| D1 | Deserranno (2019), *AEJ: Applied* | Uganda | experimento no ganho anunciado | +36% de candidatos, mas afasta os pró-sociais | ✅ ⚠️ |
| D2 | Ashraf et al. (2020), *AER* | Zâmbia | experimento na saliência da carreira | atrai mais talento sem perder pró-socialidade | ✅ |
| D3 | Miranda et al. (2012), *PLoS ONE* | Peru | experimento de escolha rotulado | +50% de salário com pontos para residência: rural de 21% para 52% | ✅ |
| D4 | Kurniati et al. (2024), *PLoS ONE* | Indonésia | experimento de escolha com **especialistas** | segurança (OR 6,1) e formação pesam mais que renda | ⚠️ |
| D5 | Kruk et al. (2010), *Bull WHO* | Gana | experimento de escolha | equipamento e gestão pesam tanto quanto dobrar o salário | ⚠️ |
| D6 | Kolstad (2011), *Health Econ* | Tanzânia | experimento de escolha | salário move; educação continuada move mais | ✅ ⚠️ |
| D7 | Hanson & Jack (2010), *Health Aff* | Etiópia | experimento de escolha | dobrar o salário: médicos dispostos de 7% para mais de 50% | ✅ |
| D8 | Serneels et al. (2010), *Bull WHO* | Ruanda, Etiópia | valoração contingente | motivação intrínseca reduz o salário exigido em ~25% | — |
| D9 | Mandeville et al. (2016), *SSM* | Malawi | experimento de escolha | treinamento no país exige quase 2× o salário | — |
| D10 | Chomitz et al. (1998), Banco Mundial | Indonésia | preferência revelada e declarada | dinheiro modesto basta no remoto moderado, não no extremo | ⚠️ |
| D11 | Lagarde & Blaauw (2009), *HRH* | revisão | revisão narrativa | não pecuniário às vezes supera o financeiro | ⚠️ |
| D12 | Mandeville, Lagarde & Hanson (2014), *BMC HSR* | revisão | revisão sistemática | só 1/3 dos experimentos de escolha tinha opção de recusa | — |
| D13 | Grobler et al. (2015), Cochrane | revisão | revisão sistemática Cochrane | evidência causal confiável quase inexistente | — |
| D14 | Wibulpolprasert & Pengpaibon (2003), *HRH* | Tailândia | estudo de caso | só estratégias integradas funcionaram | — |
| | **E. Salário real, regulação, família e dupla prática** | | | | |
| E1 | Propper & Van Reenen (2010), *JPE* | Inglaterra | painel com GMM; salário regulado contra salário externo | +10% no salário externo → +7% de mortes por infarto | ✅ |
| E2 | Elliott et al. (2007), *JHE* | Grã-Bretanha | *switching regression* | salário menos competitivo → mais vagas abertas de longa duração | ✅ |
| E3 | Britton & Propper (2016), *JPubE* | Inglaterra | efeitos fixos de escola | +10% na diferença salarial → −2% no desempenho | ✅ |
| E4 | Moretti (2013), *AEJ: Applied* | EUA | deflatores locais de preço | custo de vida explica 25–30% do aumento do prêmio nominal | — |
| E5 | Albouy (2009), *JPE* | EUA | equilíbrio espacial calibrado | imposto nominal uniforme distorce a localização | — |
| E6 | Albouy (2016), *REStat* | EUA | equilíbrio espacial calibrado | diferenças de salário e moradia refletem mais produtividade | — |
| E7 | Almeida & Azzoni (2016), *Est. Econ.* | Brasil | Country Product Dummy nas POFs | DF, SP e RJ mais caros; só regiões metropolitanas | — |
| E8 | Socha & Bech (2011), *Health Policy* | revisão | revisão sistemática | dupla prática tem pouca evidência | — |
| E9 | McGrail et al. (2017), *HRH* | Austrália | painel, GEE | filhos no ensino médio e cônjuge empregado afastam do rural | ⚠️ |
| | **F. Atração, permanência e origem** | | | | |
| F1 | Pathman et al. (1992), *JAMA* | EUA | coorte de 9 anos | com obrigação, 12% ficam; sem, 39% | ➖ |
| F2 | Pathman et al. (2004), *AJPH* | EUA | coorte | retenção semelhante; o gargalo é recrutar | ✅ |
| F3 | Bärnighausen & Bloom (2009), *BMC HSR* | revisão | revisão sistemática com meta-análise | 71% cumprem a obrigação; nenhuma inferência causal possível | — |
| F4 | Rabinowitz et al. (2001), *JAMA* | EUA | coorte retrospectiva | origem rural (OR 4,0) e admissão seletiva (OR 4,7) | ⚠️ |
| | **G. Equilíbrio espacial e origem da escassez** | | | | |
| G1 | Diamond (2016), *AER* | EUA | equilíbrio espacial estrutural | demanda local causou a segregação por qualificação | — |
| G2 | Moehling et al. (2020), *Cliometrica* | EUA | histórico-econométrico | reformas da formação médica reduziram em 40% a ida ao rural | — |

**Legenda:** ✅ reforça a direção da hipótese · ⚠️ qualifica — magnitude,
condição ou margem · ➖ delimita — o que o preenchimento não garante · — não se
aplica diretamente.

## 3. Fichas

### A. Prêmios fixados por regra e salário anunciado

O bloco mais próximo do objeto do PMM-E: um valor definido por regra ou por
sorteio, sem negociação individual. Quase tudo vem da economia da educação,
porque é lá que há regras com cutoff.

#### A1. Bobba, Ederer, León-Ciliotta, Neilson & Nieddu (2021, rev. 2026) — *Teacher Compensation and Structural Inequality: Evidence from Centralized Teacher School Choice in Perú*

- **Referência:** NBER Working Paper 29068, jul. 2021, revisado em set. 2026. [doi:10.3386/w29068](https://doi.org/10.3386/w29068). Sem versão em periódico localizada.
- **Pergunta:** salário maior em escola rural e pouco desejada atrai professor mais qualificado e melhora a aprendizagem?
- **Dados:** Peru, escolas primárias públicas. Concurso centralizado de professores contratados de 2016 e 2018, prova nacional de competência docente e provas de alunos. São 22.743 vagas; a amostra RD tem 3.068 vagas preenchidas em 1.388 escolas.
- **Método:** **RDD nítido** no corte de 500 habitantes da localidade, medido no Censo de 2007. Abaixo do corte, o adicional é de S/ 500; acima, de S/ 100. O salto médio é de S/ 244, cerca de **+13%** do salário. A hipótese de identificação é a continuidade dos resultados potenciais no corte. A estimação é local linear com correção de viés (Calonico et al., 2014). Os autores **descartaram** os cortes de tempo de viagem porque há salto de densidade em 120 min, sinal de manipulação. Depois estimam um modelo estrutural de *sorting* e simulam contrafactuais salariais.
- **Resultado:** Tabela 2, sobre a vaga:
  - probabilidade de ser preenchida: **0,063 (EP 0,048)**, não significativo;
  - nota de competência do professor recrutado: **+0,418 dp (EP 0,106)**.

  Tabela 3, sobre os alunos dos professores novos:
  - matemática: **+0,543 dp (0,221)**;
  - espanhol: **+0,340 dp (0,174)**.

  Nas escolas sem vaga aberta não há efeito, ou seja, não há canal de esforço dos professores já em exercício.
- **Conclusão dos autores:** o ganho vem da **seleção** de recrutas melhores, não de mais esforço. Atrair candidatos mais eficazes é mais custo-efetivo que realocar os professores existentes. Nas palavras deles: *"increasing salaries in less desirable locations attracts qualified teachers and improves student learning"*.
- **Limitações:** o efeito é local ao corte de 500 habitantes. Não está descartada violação de SUTVA por *sorting* entre escolas vizinhas. A qualidade só é observada nas vagas preenchidas, o que os autores tratam com *bounds*.
- **Para a hipótese:** ⚠️ **qualifica.** É o desenho mais parecido com o RDD da bolsa. O prêmio mudou **quem** ocupa a vaga, não **se** ela foi ocupada.
- **Verificação:** A — PDF de set./2026 e página do NBER. O resumo de 2021 trazia +0,45 dp; a versão atual traz 0,42.

#### A2. Dal Bó, Finan & Rossi (2013) — *Strengthening State Capabilities: The Role of Financial Incentives in the Call to Public Service*

- **Referência:** *Quarterly Journal of Economics*, 128(3), 1169–1218. [doi:10.1093/qje/qjt008](https://doi.org/10.1093/qje/qjt008). Versão anterior: NBER WP 18156.
- **Pergunta:** salário maior atrai candidatos mais capazes e mais motivados ao serviço público, e ajuda a preencher vagas em municípios menos atrativos?
- **Dados:** México, 2011. São 350 vagas de agente de desenvolvimento em 167 municípios marginalizados e 106 locais de recrutamento. Houve 1.920 candidatos, com testes de QI, personalidade e motivação.
- **Método:** **experimento em dois níveis.** Primeiro, o salário anunciado foi sorteado entre os locais: 5.000 pesos/mês em 65 locais e 3.750 em 41, diferença de **33%**. Depois, as ofertas foram sorteadas entre os elegíveis. A identificação vem da aleatorização. Os estimandos são o efeito do salário sobre o tamanho e a qualidade do pool de candidatos e sobre a aceitação, e a elasticidade-arco da oferta.
- **Resultado:**
  - aceitação de **42,9%** com o salário baixo;
  - o salário alto eleva a aceitação em **15,1 p.p.**, cerca de +35%; com controles, 0,160 (EP 0,054);
  - candidaturas **+26%**;
  - elasticidade **≈ 2,15** no working paper e *"around 2"* no artigo publicado;
  - distância e piores características do município reduzem a aceitação, e o salário alto **atenua** esse efeito (Tabela 9).
- **Conclusão dos autores:** salário mais alto atraiu candidatos mais capazes **sem perda de motivação pública**, elevou a aceitação e ajudou a fechar o hiato de recrutamento nos municípios piores. Nas palavras deles: *"higher wages attract more able applicants as measured by their IQ, personality, and proclivity toward public sector work"*.
- **Limitações:** é um único recrutamento, de curto prazo, para uma ocupação específica. Não mede desempenho nem retenção.
- **Para a hipótese:** ✅ **reforça.** É a evidência mais limpa de que remuneração anunciada eleva o preenchimento e compensa a distância.
- **Verificação:** A — números do NBER WP 18156; resumo publicado conferido no Crossref.

#### A3. Falch (2010) — *The Elasticity of Labor Supply at the Establishment Level*

- **Referência:** *Journal of Labor Economics*, 28(2), 237–266. [doi:10.1086/649905](https://doi.org/10.1086/649905).
- **Pergunta:** qual é a elasticidade da oferta de trabalho que cada escola enfrenta? Em outras palavras, há monopsônio?
- **Dados:** Noruega, escolas de ensino fundamental dos três condados do norte, de 1995–96 a 2000–01. São 81 escolas "experimentais" e 1.680 observações escola-ano.
- **Método:** o salário é fixado centralmente, com uma exceção. Escolas com escassez passada de professores certificados (mais de 20% ou 30%) pagavam **prêmio de cerca de 10%**, que liga e desliga por regra. A identificação vem da variação **dentro da escola** no status do prêmio, com efeitos fixos de escola e de ano e com primeiras diferenças. A hipótese é que, dados os efeitos fixos, a mudança de status seja exógena à oferta. O estimando é a elasticidade de curto prazo.
- **Resultado:** Tabela 5, elasticidade:
  - **1,024 (0,271)** sem tendência;
  - **1,449 (0,387)** com tendência específica da escola;
  - **1,436 (0,277)** em primeiras diferenças.
- **Conclusão dos autores:** a oferta dirigida a cada escola tem inclinação positiva e está longe de ser infinitamente elástica. Nas palavras deles: *"the supply elasticity faced by individual schools is estimated to about 1.4"*.
- **Limitações:** a oferta só é observada quando há excesso de demanda, o que gera censura. O critério de escassez passada cria risco de reversão à média. O prêmio era temporário.
- **Para a hipótese:** ✅ **reforça.** Um prêmio fixado por regra administrativa move a oferta, com elasticidade perto de 1,4.
- **Verificação:** A — PDF publicado e Crossref.

#### A4. Falch (2011) — *Teacher Mobility Responses to Wage Changes: Evidence from a Quasi-Natural Experiment*

- **Referência:** *American Economic Review: Papers & Proceedings*, 101(3), 460–465. [doi:10.1257/aer.101.3.460](https://doi.org/10.1257/aer.101.3.460).
- **Pergunta:** o prêmio salarial reduz a saída voluntária de professores?
- **Dados:** Noruega, mesmos condados de A3. Todos os professores certificados em cargo permanente em 161 escolas, de 1992–93 a 1999–2000: 1.810 professores e 7.867 observações professor-ano.
- **Método:** modelo de probabilidade linear da saída sobre o indicador de prêmio, com efeitos fixos de escola e de ano e, em variantes, efeitos fixos individuais. A identificação vem das escolas que **mudaram de status**.
- **Resultado:** efeito sobre a saída de **−0,048 (0,013)** no modelo simples a **−0,071 (0,024)** com efeitos fixos individuais. O resumo publicado diz *"six percentage points"*. A elasticidade de oferta de curto prazo é **≈ 1¼**.
- **Conclusão dos autores:** o prêmio reduz a saída de forma significativa, mas não maciça. Nas palavras dele: *"the wage premium reduces the probability of voluntary quits by six percentage points"*.
- **Limitações:** efeito de curto prazo, porque os prêmios duravam pouco. Pode haver *spillover* entre escolas do mesmo mercado.
- **Para a hipótese:** ✅ **reforça,** pela margem de **permanência**. Aqui o prêmio também retém.
- **Verificação:** A para o resumo publicado; os coeficientes vêm da versão de conferência da AEA.

#### A5. Pugatch & Schroeder (2014) — *Incentives for Teacher Relocation: Evidence from the Gambian Hardship Allowance*

- **Referência:** *Economics of Education Review*, 41, 120–136. [doi:10.1016/j.econedurev.2014.04.003](https://doi.org/10.1016/j.econedurev.2014.04.003). Versão anterior: IZA DP 7723.
- **Pergunta:** um adicional de 30–40% do salário para escolas remotas muda a distribuição e a qualificação dos professores?
- **Dados:** Gâmbia, dados administrativos de escolas públicas das regiões 3 a 6. O DiD usa 2001–2003 e 2010–2012; o RD usa 244 escolas em 2012.
- **Método:** dois desenhos.
  - **DiD:** escolas com adicional contra escolas sem adicional, com efeitos fixos de escola e hipótese de tendências paralelas.
  - **RD *fuzzy*:** o corte é a distância de **3 km da estrada principal**. Passar do corte eleva em 48 p.p. a chance de receber o adicional, com F de 14,5 no primeiro estágio. O IV dá o LATE. Há teste de McCrary e testes de covariáveis.
- **Resultado:**
  - DiD (Tabela 4): parcela de professores qualificados **+0,10 (EP 0,03)** sobre média de 0,49;
  - RD-IV (Tabela 7): alunos por professor qualificado **−27,4 (EP 12,7)** sobre média de 45;
  - RD-IV, parcela de qualificados: 0,16 (0,11), não significativo.
- **Conclusão dos autores:** o adicional aumentou a presença de professores qualificados. O ganho se concentra perto do corte, e a política foi menos eficaz nas escolas **mais** remotas. Nas palavras deles: *"the hardship allowance increased the share of qualified (certified) teachers by 10 percentage points"*.
- **Limitações:** não separa atração líquida de realocação entre escolas. O resultado some quando se excluem estagiários e professores corânicos. O RD tem amostra pequena.
- **Para a hipótese:** ✅ **reforça.** É precedente de RD num adicional por critério territorial. O ganho cai nos lugares mais difíceis.
- **Verificação:** A — PDF do IZA DP 7723 e Crossref.

#### A6. Pugatch & Schroeder (2018) — *Teacher Pay and Student Performance: Evidence from the Gambian Hardship Allowance*

- **Referência:** *Journal of Development Effectiveness*, 10(2), 249–276. [doi:10.1080/19439342.2018.1452778](https://doi.org/10.1080/19439342.2018.1452778). Versão anterior: IZA DP 8621.
- **Pergunta:** o adicional de A5 melhora o desempenho dos alunos?
- **Dados:** Gâmbia, prova nacional de 2012, do 3º e do 5º ano. São 244 escolas, 148 delas com adicional.
- **Método:** **RD *fuzzy*** no mesmo corte de 3 km. A forma reduzida dá o ITT e o IV dá o LATE. Há também efeitos quantílicos. A hipótese é a continuidade no corte.
- **Resultado:** efeitos médios **nulos** em todas as disciplinas e séries; por exemplo, inglês no 3º ano: +0,15 dp no IV, não significativo. A única exceção é inglês das meninas no 5º ano, +0,25 dp com p < 0,10.
- **Conclusão dos autores:** um aumento salarial grande e incondicional teve efeito médio nulo, com sinais de ganho no topo da distribuição e de perda na base. Nas palavras deles: *"We find no effects of the hardship allowance on average test scores."*
- **Limitações:** só um ano após o tratamento, sem linha de base de provas. Os erros-padrão são grandes.
- **Para a hipótese:** ➖ **delimita.** Mais profissional qualificado não garante resultado final. É o elo força de trabalho → resultado da cadeia do projeto.
- **Verificação:** A — PDF do IZA DP 8621 e Crossref.

#### A7. Cowan & Goldhaber (2018) — *Do Bonuses Affect Teacher Staffing and Student Achievement in High Poverty Schools? Evidence from an Incentive for National Board Certified Teachers in Washington State*

- **Referência:** *Economics of Education Review*, 65, 138–152. [doi:10.1016/j.econedurev.2018.06.010](https://doi.org/10.1016/j.econedurev.2018.06.010). Manuscrito em PMC6088508.
- **Pergunta:** um bônus anual de **US$ 5.000** para professores certificados pelo NBPTS em escolas pobres muda o quadro docente e o desempenho dos alunos?
- **Dados:** estado de Washington, 2008–2013, com 6.877 observações escola-ano.
- **Método:** **RD *fuzzy*** na proporção de alunos com almoço subsidiado. O corte é 70%, 60% ou 50% conforme o nível de ensino. É *fuzzy* porque escolas que deixam de ser elegíveis mantêm o bônus. A estimação é por 2SLS, com DiD como complemento. O estimando é o LATE perto do corte.
- **Resultado:** parcela de professores certificados **+0,0115 (EP 0,0039)** por ano de elegibilidade, ou +4 a 8 p.p. em cinco anos. Esse ganho vem de contratação, certificação de quem já estava e menor rotatividade. Nas notas dos alunos não há efeito.
- **Conclusão dos autores:** o bônus aumentou a presença de professores certificados, mas não teve efeito detectável no desempenho. Nas palavras deles: *"we do not find evidence that the bonus resulted in detectible effects on student test achievement"*.
- **Limitações:** há descontinuidade **antes** do tratamento na proporção de certificados, o que segundo os autores *"may cast some doubt"* sobre o RDD.
- **Para a hipótese:** ✅ **reforça,** com efeito pequeno. É um bônus de valor nominal parecido com o degrau do PMM-E.
- **Verificação:** A — manuscrito em PMC e Crossref.

#### A8. Elacqua, Hincapié, Hincapié & Montalva (2022) — *Can Financial Incentives Help Disadvantaged Schools to Attract and Retain High-Performing Teachers? Evidence from Chile*

- **Referência:** *Journal of Policy Analysis and Management*, 41(2), 603–631. [doi:10.1002/pam.22375](https://doi.org/10.1002/pam.22375). Versão anterior: IDB WP 1080.
- **Pergunta:** um prêmio a professores de alto desempenho, 40% maior em escolas desfavorecidas, os retém ou atrai para essas escolas?
- **Dados:** Chile, programa AEP, 2012–2015, com painel de professores públicos de 2011 a 2017.
- **Método:** **RD nítido** pelo método de fronteira: a nota do portfólio é a *running variable*, condicionada à categoria na prova escrita. A estimação segue Calonico, Cattaneo e Titiunik. Só uma das duas fronteiras passou nos testes de validade.
- **Resultado:** o bônus vale cerca de **16%** do salário anual. A retenção em escolas desfavorecidas dos professores que já estavam nelas sobe **17 a 21 p.p.** (o working paper reporta 22 a 29 p.p.).
- **Conclusão dos autores:** o programa reteve quem já estava, mas **não atraiu** professores de escolas favorecidas, para os quais o prêmio funcionou como sinal de qualidade. Nas palavras deles: *"it did not achieve the objective of attracting better teachers from more advantaged schools"*.
- **Limitações:** efeito local a uma fronteira, numa subamostra. O efeito monetário se confunde com o efeito do sinal de qualidade.
- **Para a hipótese:** ⚠️ **qualifica.** O prêmio retém mais do que atrai de fora.
- **Verificação:** A — resumo publicado; método conferido no IDB WP 1080.

#### A9. Steele, Murnane & Willett (2010) — *Do Financial Incentives Help Low-Performing Schools Attract and Keep Academically Talented Teachers? Evidence from California*

- **Referência:** *Journal of Policy Analysis and Management*, 29(3), 451–478. [doi:10.1002/pam.20505](https://doi.org/10.1002/pam.20505). Versão anterior: NBER WP 14780.
- **Pergunta:** a bolsa de **US$ 20.000** levou professores novatos talentosos a escolas de baixo desempenho, e os manteve lá?
- **Dados:** Califórnia, 27.106 candidatos a licença entre 1998–99 e 2002–03, dos quais 718 receberam a bolsa.
- **Método:** **variável instrumental.** O instrumento é a matrícula em licenciatura nos dois únicos anos em que a bolsa existiu, interagida com traços acadêmicos. A exclusão supõe que a matrícula naqueles anos não foi motivada pela bolsa, que foi pouco divulgada. O F do primeiro estágio é 396,6. O estimando é o LATE.
- **Resultado:** **+28 p.p.** na probabilidade de lecionar em escola de baixo desempenho em até dois anos: 0,281 (EP 0,071) no IV, contra 0,136 no MQO. Na retenção por quatro anos, **75%** nos dois grupos.
- **Conclusão dos autores:** a bolsa aumentou em 28 p.p. a entrada em escolas de baixo desempenho. Nas palavras deles: *"acquiring a GTF increased their probability of doing so by 28 percentage points"*.
- **Limitações:** a validade externa se restringe a um grupo auto-selecionado. A comparação de retenção é só descritiva.
- **Para a hipótese:** ✅ **reforça** a atração; ➖ não mostra efeito na permanência.
- **Verificação:** A — NBER WP 14780 e Crossref.

#### A10. Clotfelter, Glennie, Ladd & Vigdor (2008) — *Would Higher Salaries Keep Teachers in High-Poverty Schools? Evidence from a Policy Intervention in North Carolina*

- **Referência:** *Journal of Public Economics*, 92(5–6), 1352–1370. [doi:10.1016/j.jpubeco.2007.07.003](https://doi.org/10.1016/j.jpubeco.2007.07.003). Versão anterior: NBER WP 12285.
- **Pergunta:** um bônus anual de **US$ 1.800** reduz a rotatividade de professores de matemática, ciências e educação especial em escolas pobres?
- **Dados:** Carolina do Norte, de 1999–2000 a 2003–04. O programa vigorou de 2001 a 2004.
- **Método:** **modelos de risco de saída** com variação tripla: antes e depois do programa, disciplinas elegíveis contra não elegíveis, e escolas elegíveis contra escolas que por pouco não foram. A hipótese é de tendências comuns. O estimando é a razão de riscos de saída.
- **Resultado:** rotatividade **−17%** no artigo publicado, contra −12% no working paper. A regra de bolso é cerca de 1% de redução a cada US$ 100. Com a elegibilidade imputada, em vez do recebimento efetivo do bônus, o efeito não é significativo.
- **Conclusão dos autores:** o bônus reduziu a saída, mais entre professores experientes, e o efeito foi minado por má comunicação das regras. Nas palavras deles: *"was sufficient to reduce mean turnover rates of the targeted teachers by 17%"*.
- **Limitações:** programa curto e mal compreendido pelos professores. O resultado depende de usar o recebimento efetivo do bônus.
- **Para a hipótese:** ✅ **reforça,** pela permanência. Mostra também que a **informação** sobre o incentivo importa.
- **Verificação:** A — RePEc, NBER WP e Crossref.

#### A11. Glazerman, Protik, Teh, Bruch & Max (2013) — *Transfer Incentives for High-Performing Teachers: Final Results from a Multisite Randomized Experiment*

- **Referência:** NCEE 2014-4003, Institute of Education Sciences, nov. 2013. [PDF](https://ies.ed.gov/ncee/pubs/20144003/pdf/20144003.pdf).
- **Pergunta:** **US$ 20.000** para professores de alto valor agregado se transferirem a escolas de baixo desempenho preenche vagas, retém esses professores e melhora o desempenho?
- **Dados:** EUA, 10 distritos em 7 estados, coortes de 2009 e 2010, 114 escolas. Foram identificados 1.514 candidatos e preenchidas 81 vagas.
- **Método:** **experimento aleatorizado.** Equipes com vaga em escola de baixo desempenho foram sorteadas, dentro de blocos pareados, entre o tratamento (vaga oferecida pelo programa) e o controle (contratação normal). O estimando é o ITT por equipe.
- **Resultado:**
  - **88%** das vagas de tratamento preenchidas por candidatos do programa;
  - no ensino fundamental I: +0,08 dp em matemática e +0,07 dp em leitura;
  - no fundamental II: nada;
  - retenção durante o pagamento: **93% contra 70%**;
  - retenção depois do pagamento: **60% contra 51%**, diferença não significativa.
- **Conclusão dos autores:** o incentivo atraiu e reteve professores de alto desempenho **enquanto pagou**. Nas palavras deles: *"The transfer incentive successfully attracted high-performing teachers to lower-performing schools and retained them in these schools during the two years."*
- **Limitações:** os distritos não são amostra aleatória. Foi preciso um pool grande para poucas vagas.
- **Para a hipótese:** ✅ **reforça** o preenchimento; ⚠️ a retenção dura enquanto dura o pagamento, o que é relevante para uma bolsa de 12 meses.
- **Verificação:** A — relatório NCEE integral.

### B. Incentivos a médicos em países de alta renda

Programas e experimentos de escolha com médicos na Austrália, nos EUA, no
Canadá, na Noruega e na Escócia.

#### B1. Yong, Scott, Gravelle, Sivey & McGrail (2018) — *Do Rural Incentives Payments Affect Entries and Exits of General Practitioners?*

- **Referência:** *Social Science & Medicine*, 214, 197–205. [doi:10.1016/j.socscimed.2018.08.014](https://doi.org/10.1016/j.socscimed.2018.08.014).
- **Pergunta:** a reforma de 2010 do incentivo rural australiano (GPRIP), que tornou elegíveis novas localidades, mudou a entrada e a saída de médicos de família (GPs)?
- **Dados:** cadastro AMPCo, que cobre todos os médicos de família da Austrália, 2008–2014. A unidade é a localidade: 755 passaram a ser elegíveis, 787 já eram e 2.249 nunca foram, num total de 17.587 localidade-ano.
- **Método:** **diferenças em diferenças.** A troca da classificação de remoticidade em 2010 tornou elegíveis áreas que antes não eram. A comparação é com as localidades nunca elegíveis, que são as metropolitanas. As estimativas usam MQO e efeitos fixos de localidade, sobre o estoque e sobre cada tipo de entrada e saída. A hipótese é de tendências paralelas, testada com apenas dois anos antes da reforma. O incentivo equivale a +1,4% a +6,6% da renda.
- **Resultado:**
  - entrada de **recém-formados**: **+0,068 (EP 0,020)** a **+0,080 (EP 0,022)** por localidade-ano, cerca de **+50%** sobre a média de 0,15;
  - outras entradas: **−0,071 a −0,080**;
  - **estoque total sem efeito**.
- **Conclusão dos autores:** o programa atraiu recém-formados e não mexeu com os demais médicos; o incentivo deveria focar quem está no início da carreira. Nas palavras deles: *"The policy change increased the entry of newly-qualified GPs to newly eligible locations but had no effect on the entry and exit of other GPs."*
- **Limitações:** período pré-tratamento curto. O incentivo é pequeno e gradual.
- **Para a hipótese:** ⚠️ **qualifica.** Há resposta na entrada, mas o estoque não muda, porque parte da entrada substitui outras.
- **Verificação:** A — Europe PMC e manuscrito aceito (White Rose).

#### B2. Swami & Scott (2021) — *Impact of Rural Workforce Incentives on Access to GP Services in Underserved Areas: Evidence from a Natural Experiment*

- **Referência:** *Social Science & Medicine*, 281, 114045. [doi:10.1016/j.socscimed.2021.114045](https://doi.org/10.1016/j.socscimed.2021.114045).
- **Pergunta:** a mesma reforma de B1 reduziu o tempo de espera por consulta não urgente?
- **Dados:** Austrália, painel de 2008–2014 com 2.058 médicos de família.
- **Método:** **diferenças em diferenças** sobre a mudança de elegibilidade de 2010, tratada como experimento natural. Os desfechos são o número de médicos na clínica e o tempo de espera de pacientes já vinculados e de pacientes novos.
- **Resultado:** o número de médicos aumentou nas áreas que passaram a ser elegíveis. **Nenhum efeito** na espera dos pacientes já vinculados. Para pacientes novos, evidência fraca de queda de cerca de **16%**.
- **Conclusão dos autores:** o incentivo financeiro tem papel limitado na melhora do acesso. Nas palavras deles: *"financial incentives may only play a limited role in improving access to primary care"*.
- **Limitações:** o tempo de espera é relatado pelo próprio médico. Há um único desfecho de acesso.
- **Para a hipótese:** ➖ **delimita.** Mais médicos não é o mesmo que mais acesso.
- **Verificação:** A apenas para o resumo; o texto integral é fechado.

#### B3. Khoury, Leganza & Masucci (2025) — *Health Professional Shortage Areas and Physician Location Decisions*

- **Referência:** *American Journal of Health Economics*, 11(3), 487–527. [doi:10.1086/729117](https://doi.org/10.1086/729117).
- **Pergunta:** ser designado área de escassez (HPSA) — o que dá direito ao bônus de 10% do Medicare e a outros programas — muda onde os médicos se instalam?
- **Dados:** EUA, dados do Medicare por condado.
- **Método:** **diferenças em diferenças com pareamento:** condados designados contra condados pareados não designados, sob tendências paralelas condicionais. O efeito é desagregado por estágio de carreira. O tratamento é um **pacote** de incentivos, não o bônus isolado.
- **Resultado:** aumento de médicos de atenção primária **em início de carreira**, sobretudo formados em escolas ranqueadas. **Nenhum efeito** em médicos experientes. As magnitudes não foram conferidas.
- **Conclusão dos autores:** a designação atrai quem está começando e não faz médicos estabelecidos se mudarem. Nas palavras deles: *"designated counties experience an increase in the number of early-career primary care physicians"*.
- **Limitações:** identifica um pacote. Só capta médicos que atendem Medicare.
- **Para a hipótese:** ⚠️ **qualifica.** A resposta se concentra no início de carreira; o PMM-E, que exige RQE, recruta especialistas já formados.
- **Verificação:** A para referência e resumo; números não conferidos.

#### B4. Bolduc, Fortin & Fournier (1996) — *The Effect of Incentive Policies on the Practice Location of Doctors: A Multinomial Probit Analysis*

- **Referência:** *Journal of Labor Economics*, 14(4), 703–732. [doi:10.1086/209828](https://doi.org/10.1086/209828).
- **Pergunta:** os incentivos de Quebec, entre eles a remuneração diferenciada por região, influenciaram onde os médicos de família abrem a primeira prática?
- **Dados:** Quebec, 18 regiões, médicos no momento da primeira escolha, antes e depois das medidas.
- **Método:** **modelo estrutural de escolha discreta:** um probit multinomial espacial, que permite correlação entre locais próximos. As políticas entram como efeito preço e efeito renda na utilidade. A identificação vem da comparação antes e depois, condicionada à forma funcional.
- **Resultado:** efeito **significativo** dos incentivos sobre a escolha. As magnitudes não foram conferidas.
- **Conclusão dos autores:** nas palavras deles, *"Our results provide evidence that these measures had a significant effect on location choices."*
- **Limitações:** depende da forma funcional e da estrutura espacial imposta. Cobre só a primeira prática.
- **Para a hipótese:** ✅ **reforça.** É o caso mais antigo de remuneração médica diferenciada por região, por regra, com efeito sobre a localização.
- **Verificação:** A para o resumo; números não conferidos.

#### B5. Holmes (2005) — *Increasing Physician Supply in Medically Underserved Areas*

- **Referência:** *Labour Economics*, 12(5), 697–725. [doi:10.1016/j.labeco.2004.02.003](https://doi.org/10.1016/j.labeco.2004.02.003).
- **Pergunta:** quanto o National Health Service Corps (NHSC) aumenta a oferta de médicos em áreas carentes dos EUA?
- **Dados:** localização de médicos em intervalos de cinco anos, participantes contra não participantes do NHSC.
- **Método:** **logit multinomial** do tipo de local escolhido, com heterogeneidade não observada para tratar a seleção para o programa. O contrafactual simula o fim do programa.
- **Resultado:** sem o programa, a oferta em áreas carentes cairia **cerca de 10%**.
- **Conclusão do autor:** o NHSC aumenta de forma relevante a oferta em áreas carentes.
- **Limitações:** a correção de seleção é paramétrica. Estima o efeito de **participação** num programa, não de um incentivo marginal.
- **Para a hipótese:** ✅ **reforça**, com a ressalva do estimando.
- **Verificação:** **B** — referência conferida; o resumo vem de indexador secundário.

#### B6. Chan, Donnelly, Sullivan, Pope & Gambhir (2025) — *Incentivising General Practice: A Review of the Scottish Targeted Enhanced Recruitment Scheme (TERS) through Recruitment and Training Data*

- **Referência:** *BJGP Open*, 9(3), BJGPO.2024.0289. [doi:10.3399/BJGPO.2024.0289](https://doi.org/10.3399/BJGPO.2024.0289).
- **Pergunta:** uma bolsa única de **£ 20.000** aumentou o recrutamento para programas de residência em medicina de família historicamente pouco procurados na Escócia?
- **Dados:** NHS Education for Scotland, 2015–2023, com unidade programa-ano. O esquema recrutou 734 residentes; os programas não elegíveis, 1.522.
- **Método:** **observacional.** Compara razões de chances de vaga preenchida antes e depois, em programas elegíveis e não elegíveis. Não há modelo formal de DiD nem teste de tendências. A elegibilidade foi definida pelo **baixo preenchimento passado**, o que abre espaço para reversão à média.
- **Resultado:**
  - preenchimento de **57,3% para 87,6%**;
  - OR **4,81 (IC95% 3,87–5,99)**, ou **2,33 (1,74–3,12)** dentro dos programas elegíveis.
- **Conclusão dos autores:** a bolsa esteve associada a cerca do dobro da chance de recrutamento; a retenção ainda está em aberto. Nas palavras deles: *"a one-off £20 000 conditional grant was associated with a doubling of the odds of recruitment"*.
- **Limitações:** desenho associativo. Não mede retenção.
- **Para a hipótese:** ✅ **reforça**, sem identificação causal. É o caso com o desfecho mais parecido com o nosso: **preenchimento de vaga**.
- **Verificação:** A — Europe PMC, texto integral.

#### B7. Scott, Witt, Humphreys, Joyce, Kalb, Jeon & McGrail (2013) — *Getting Doctors into the Bush: General Practitioners' Preferences for Rural Location*

- **Referência:** *Social Science & Medicine*, 96, 33–44. [doi:10.1016/j.socscimed.2013.07.002](https://doi.org/10.1016/j.socscimed.2013.07.002).
- **Pergunta:** que incentivo financeiro os médicos de família australianos exigiriam para se mudar para áreas rurais?
- **Dados:** 3.727 médicos de família do painel MABEL.
- **Método:** **experimento de escolha discreta (DCE)** com **opção de ficar no emprego atual**. Em cada tarefa, o médico escolhe entre dois empregos hipotéticos, descritos por localidade e atributos do trabalho, ou fica onde está. Do modelo sai a compensação exigida. A hipótese é que a escolha declarada reflita a escolha real.
- **Resultado:**
  - **65%** ficariam no emprego atual em todas as escolhas;
  - cidade de 5 a 20 mil habitantes: **≥ 37%** da renda anual;
  - cidade com menos de 5 mil: **64%**;
  - pior pacote rural: **≥ 130%**.
- **Conclusão dos autores:** os incentivos necessários são grandes e dependem do lugar e do emprego. Nas palavras deles: *"It is important to begin to tailor incentive packages to the characteristics of jobs and of rural areas."*
- **Limitações:** preferência declarada. Alta proporção de quem não se mudaria.
- **Para a hipótese:** ⚠️ **qualifica.** O dinheiro precisa ser grande e o custo do lugar decide.
- **Verificação:** A — Europe PMC.

#### B8. Holte, Kjær, Abelsen & Olsen (2015) — *The Impact of Pecuniary and Non-Pecuniary Incentives for Attracting Young Doctors to Rural General Practice*

- **Referência:** *Social Science & Medicine*, 128, 1–9. [doi:10.1016/j.socscimed.2014.12.022](https://doi.org/10.1016/j.socscimed.2014.12.022).
- **Pergunta:** quanto pesam a renda e os atributos não pecuniários na disposição de médicos jovens noruegueses de trabalhar em medicina de família rural?
- **Dados:** todos os estudantes de último ano e internos da Noruega (1.562); 831 responderam (53%), em 2010.
- **Método:** **DCE** com atributos de emprego, entre eles localização e renda, seguido de simulações de pacotes de política.
- **Resultado:** renda maior tem **menos** impacto que melhorias não pecuniárias. Um número de fonte secundária, não conferido, diz que +20% de renda elevaria em 12 p.p. a escolha rural.
- **Conclusão dos autores:** são necessários pacotes combinados. Nas palavras deles: *"increased income seem to have less impact as compared to improvements in the non-pecuniary attributes"*.
- **Limitações:** preferência declarada. Taxa de resposta de 53%.
- **Para a hipótese:** ⚠️ **qualifica.** O custo laboral pesa mais que a renda.
- **Verificação:** A para o resumo.

#### B9. Kulka & McWeeny (2019) — *Rural Physician Shortages and Policy Intervention*

- **Referência:** SSRN Working Paper 3481777. [SSRN](https://papers.ssrn.com/abstract=3481777). Sem versão em periódico.
- **Pergunta:** programas de perdão de dívida estudantil reduzem a escassez de médicos rurais nos EUA?
- **Dados:** EUA, nível de condado.
- **Método:** **diferenças em diferenças** para o perdão de dívida, seguida de um **modelo estrutural** de localização que estima a resposta à remuneração e a preferência pelo estado de origem.
- **Resultado:** perdão de dívida → **+3 médicos por condado rural**. Resposta à remuneração **baixa**; preferência forte pelo estado de origem.
- **Conclusão dos autores:** os programas atuais são pequenos demais para eliminar a escassez. Nas palavras deles: *"current programs are too small to eliminate shortages"*.
- **Limitações:** working paper; desenho e robustez não conferidos.
- **Para a hipótese:** ⚠️ **qualifica a magnitude.**
- **Verificação:** **B** — só resumo indexado.

#### B10. Falcettoni (2018) — *The Determinants of Physicians' Location Choice: Understanding the Rural Shortage*

- **Referência:** job market paper, University of Minnesota; versão apresentada na AEA 2021 ([PDF](https://www.aeaweb.org/conference/2021/preliminary/paper/NrRK4A2i)). Sem versão em periódico localizada.
- **Pergunta:** o que determina a escolha do primeiro emprego depois da residência, e qual o efeito do perdão de dívida e de incentivos salariais sobre a oferta rural?
- **Dados:** Medicare Part B 2012–2016 ligado a diretórios médicos: 9.691 residentes de atenção primária e 22.068 especialistas, em 305 localidades.
- **Método:** **modelo estrutural de equilíbrio espacial** com médicos heterogêneos, estimado à moda BLP. A renda é endógena e instrumentada por um instrumento do tipo Bartik, com F ≈ 68. Os contrafactuais simulam a retirada e a realocação de políticas.
- **Resultado:**
  - perdão de dívida e incentivos salariais juntos levam **+1,2%** de médicos a áreas rurais;
  - realocar o gasto do perdão de dívida para salário traria **cerca de 6 vezes** mais médicos de atenção primária;
  - médicos de atenção primária têm **cerca de 3,8 vezes** mais chance de ficar no estado onde fizeram a residência.
- **Conclusão da autora:** a persistência geográfica é forte, e salário é instrumento mais eficaz que perdão de dívida. Nas palavras dela: *"residents strongly prefer remaining close to their residency location."*
- **Limitações:** depende das suposições estruturais e do instrumento. Os dados cobrem só Medicare.
- **Para a hipótese:** ✅ entre os instrumentos, o salário é o melhor; ⚠️ o efeito agregado é pequeno.
- **Verificação:** A — PDF no site da AEA.

#### B11. Sivey, Scott, Witt, Joyce & Humphreys (2012) — *Junior Doctors' Preferences for Specialty Choice*

- **Referência:** *Journal of Health Economics*, 31(6), 813–823. [doi:10.1016/j.jhealeco.2012.07.001](https://doi.org/10.1016/j.jhealeco.2012.07.001).
- **Pergunta:** quanto pesam os ganhos esperados e os atributos não pecuniários na escolha de especialidade?
- **Dados:** médicos juniores do painel MABEL, Austrália; o working paper informa 532 médicos em 2008.
- **Método:** **DCE** com especialidades hipotéticas descritas por ganhos, horas, trabalho procedimental e acadêmico e continuidade do cuidado, seguido de simulações.
- **Resultado:** +US$ 50 mil na renda do médico de família elevam de **8 a 13 p.p.** a escolha da especialidade; elasticidade-renda de **0,95**.
- **Conclusão dos autores:** renda e atributos não pecuniários afetam a escolha. Nas palavras deles: *"The simulation implies an earnings elasticity of specialty choice of 0.95."*
- **Limitações:** trata de **especialidade**, não de **local**. Preferência declarada.
- **Para a hipótese:** evidência indireta.
- **Verificação:** A para o resumo. **Correção:** o catálogo 19 citava este artigo com outro título e outro DOI; o correto é o desta ficha.

### C. Brasil

#### C1. Costa, Nunes & Sanches (2024) — *How to Attract Physicians to Underserved Areas? Policy Recommendations from a Structural Model*

- **Referência:** *The Review of Economics and Statistics*, 106(1), 36–52. [doi:10.1162/rest_a_01155](https://doi.org/10.1162/rest_a_01155). Versões anteriores: IEPS TD nº 1 (2019) e SocArXiv.
- **Pergunta:** que políticas — cotas, novas vagas de medicina, salário, infraestrutura — melhoram a distribuição geográfica de médicos generalistas no Brasil, e a que custo?
- **Dados:** cadastro do CFM ligado à RAIS (2001–2015) e ao CNES (2005–2016). São 46.989 generalistas formados entre 2001 e 2013, observados nos três primeiros anos de carreira, com 52 alternativas de local: a região metropolitana ou o interior de cada UF.
- **Método:** **modelo estrutural de oferta e demanda.** A oferta é um logit de coeficientes aleatórios para a escolha de local; a demanda vem de estabelecimentos privados que competem com os públicos. O salário é endógeno, tratado por função de controle e instrumentado pelos atributos médios de outros locais da mesma macrorregião. A hipótese de exclusão é que esses atributos afetem a utilidade só pelo salário. Os contrafactuais medem o desequilíbrio entre a distribuição de médicos e a da população, e o custo por ponto reduzido.
- **Resultado:** conferido no manuscrito final aceito:
  - elasticidade-salário **≈ 0,4** nas metrópoles e **≈ 0,7** no interior;
  - salário público **+50%** no interior do N/NE: **cerca de 25%** mais médicos e **−12,4%** de desequilíbrio, a **US$ 15,7 mi por ponto** ao ano;
  - cotas para nascidos em áreas carentes: **−63,8%**;
  - novas vagas de medicina: **−65,9%**, a US$ 2,2–5,1 mi por ponto;
  - infraestrutura ×1,5: −6,4%, a US$ 94,2 mi por ponto.
- **Conclusão dos autores:** cotas e novas vagas em áreas carentes custam menos que incentivos financeiros, porque os médicos valorizam muito trabalhar perto de onde nasceram e se formaram. Nas palavras deles: *"quotas in medical schools for students born in underserved areas and the opening of vacancies in medical schools in deprived areas are more cost-effective than financial incentives"*.
- **Limitações:** os contrafactuais dependem da forma funcional e dos instrumentos. Mede o primeiro emprego de recém-formados generalistas, não especialistas nem retenção.
- **Para a hipótese:** ✅ o salário entra com sinal positivo; ⚠️ a oferta é **inelástica** e o salário é a alavanca menos custo-efetiva.
- **Verificação:** A — manuscrito final aceito e Crossref. O WP de 2019 trazia outros números (0,41/0,70; −13,4%; cotas −51,5%).

#### C2. Hone, Powell-Jackson, Santos et al. (2020) — *Impact of the Programa Mais Médicos (More Doctors Programme) on Primary Care Doctor Supply and Amenable Mortality: Quasi-Experimental Study of 5565 Brazilian Municipalities*

- **Referência:** *BMC Health Services Research*, 20, 873. [doi:10.1186/s12913-020-05716-2](https://doi.org/10.1186/s12913-020-05716-2).
- **Pergunta:** a alocação de médicos do PMM seguiu os critérios do programa, e qual o efeito sobre a densidade de médicos de atenção primária e a mortalidade evitável?
- **Dados:** painel trimestral de 5.565 municípios, 2008–2017, com médicos em tempo integral pelo CNES e mortalidade evitável.
- **Método:** **diferenças em diferenças** com múltiplos períodos, efeitos fixos de município e de estado×trimestre e covariáveis. A hipótese é de tendências paralelas, testada por estudo de evento e checada com ponderação por escore de propensão (IPTW).
- **Resultado:**
  - **+15,1** médicos do programa por 100 mil habitantes, mas **líquido de só +5,7**, por substituição;
  - mortalidade evitável **−1,06 por 100 mil** ao ano (IC95% −1,78 a −0,34), cerca de 1,4%;
  - efeito maior em municípios prioritários e de baixa densidade prévia.
- **Conclusão dos autores:** os ganhos foram limitados pela alocação a áreas não prioritárias e pela substituição local. Nas palavras deles: *"PMM potential health benefits were undermined due to widespread allocation of doctors to non-priority areas and local substitution effects."*
- **Limitações:** desenho ecológico. A adesão não é aleatória.
- **Para a hipótese:** ➖ **delimita.** Médico do programa não é expansão líquida — é o motivo do teste município–mês do plano vigente.
- **Verificação:** A — PMC.

#### C3. Girardi, van Stralen, Cella, Wan Der Maas, Carvalho & Faria (2016) — *Impacto do Programa Mais Médicos na redução da escassez de médicos em Atenção Primária à Saúde*

- **Referência:** *Ciência & Saúde Coletiva*, 21(9), 2675–2684. [doi:10.1590/1413-81232015219.16032016](https://doi.org/10.1590/1413-81232015219.16032016).
- **Pergunta:** quanto o PMM reduziu a escassez de médicos de atenção primária nos municípios?
- **Dados:** CNES de março de 2013 e de setembro de 2015, cadastro de médicos do programa (14.256 em 3.755 municípios) e Censo 2010; 5.562 municípios.
- **Método:** **descritivo, antes e depois, sem grupo de comparação.** Aplica um índice de escassez em quatro dimensões e compara com um cenário mecânico de 2015 sem os médicos do programa.
- **Resultado:** municípios em escassez caem de **1.200 (21,6%)** para **777 (14,0%)**. Sem os médicos do programa, seriam **2.021 (35,4%)**, o que indica queda da oferta regular — **substituição**.
- **Conclusão dos autores:** a escassez caiu, mas os municípios ficaram dependentes do provimento federal. Nas palavras deles: *"permaneceu um quadro de insegurança assistencial em função da dependência dos municípios em relação ao provimento federal"*.
- **Limitações:** sem contrafactual causal.
- **Para a hipótese:** ➖ **delimita**, pela substituição.
- **Verificação:** A — PDF no Redalyc e Crossref.

#### C4. Oliveira, Vanni, Pinto, Santos, Figueiredo, Araújo, Matos & Cyrino (2015) — *Mais Médicos: um programa brasileiro em uma perspectiva internacional*

- **Referência:** *Interface — Comunicação, Saúde, Educação*, 19(54), 623–634. [doi:10.1590/1807-57622014.1142](https://doi.org/10.1590/1807-57622014.1142).
- **Pergunta:** como o PMM se compara às políticas de provimento da Austrália e dos EUA?
- **Dados:** revisão bibliográfica, documentos de um seminário internacional de 2014 e dados administrativos do programa.
- **Método:** **análise comparativa descritiva**, sem identificação causal. Os autores são gestores do Ministério da Saúde.
- **Resultado:** em menos de um ano, 14.462 médicos em 3.785 municípios — **1.846 brasileiros** e 12.616 estrangeiros, 11.429 deles cubanos. O PROVAB passou de 350 para 3.550 médicos entre 2011 e 2013, depois de aumento de bolsa e bônus de 10% na prova de residência.
- **Conclusão dos autores:** iniciativas anteriores tiveram sucesso parcial; só o PMM teve escala e tempo de resposta. Nas palavras deles: *"foi apenas com o Programa Mais Médicos que a provisão de médicos em áreas vulneráveis teve a magnitude e a resposta em tempo adequado"*.
- **Limitações:** ensaio de debate, de autoria do órgão gestor.
- **Para a hipótese:** ⚠️ **qualifica.** Com bolsa alta, o programa dependeu de médicos estrangeiros; no PROVAB não dá para isolar a bolsa do bônus de carreira.
- **Verificação:** A — SciELO.

#### C5. Santos, Costa & Girardi (2015) — *Programa Mais Médicos: uma ação efetiva para reduzir iniquidades em saúde*

- **Referência:** *Ciência & Saúde Coletiva*, 20(11), 3547–3552. [doi:10.1590/1413-812320152011.07252015](https://doi.org/10.1590/1413-812320152011.07252015).
- **Pergunta:** o PMM reduz iniquidades na oferta de médicos?
- **Dados:** números do programa até julho de 2014 e relatório de escassez da UFMG.
- **Método:** **ensaio descritivo**, sem grupo de comparação.
- **Resultado:** municípios em escassez de 1.200 para **558** em setembro de 2014, −53,5%.
- **Conclusão dos autores:** o programa chegou aos municípios mais necessitados. Nas palavras deles: *"Evidências indicam redução em 53% no número de municípios com escassez de médicos"*.
- **Limitações:** sem contrafactual; não trata da substituição. Os números diferem de C3 (558 em 2014 contra 777 em 2015).
- **Para a hipótese:** contexto.
- **Verificação:** A — Redalyc e Crossref.

#### C6. Carrillo & Feres (2019) — *Provider Supply, Utilization, and Infant Health: Evidence from a Physician Distribution Policy*

- **Referência:** *American Economic Journal: Economic Policy*, 11(3), 156–196. [doi:10.1257/pol.20170619](https://doi.org/10.1257/pol.20170619).
- **Pergunta:** mais médicos de atenção primária aumentam o uso de serviços e melhoram a saúde infantil?
- **Dados:** painel municipal 2008–2016: CNES, SIA, SINASC e SIM.
- **Método:** **diferenças em diferenças** entre municípios que receberam e que não receberam médicos do PMM, antes e depois de 2013, sob tendências paralelas.
- **Resultado:** números do working paper de 2017, não conferidos na versão publicada: médicos **+17%**, consultas **+4,3%**, pré-natal com médico **+10%** — este último em substituição ao feito por enfermeiros. **Nenhum efeito** em peso ao nascer, duração da gestação ou mortalidade infantil.
- **Conclusão dos autores:** o uso de médicos subiu, a saúde infantil não mudou. Nas palavras deles: *"We find no evidence of gains in widely used metrics of infant health, including birth weight, gestation, and infant mortality."*
- **Limitações:** a adesão se correlaciona com características municipais; horizonte curto.
- **Para a hipótese:** ➖ **delimita.** Mais oferta não chega automaticamente à saúde.
- **Verificação:** A para o resumo; **B** para os números.

#### C7. Fontes, Conceição & Jacinto (2018) — *Evaluating the Impact of Physicians' Provision on Primary Healthcare: Evidence from Brazil's More Doctors Program*

- **Referência:** *Health Economics*, 27(8), 1284–1299. [doi:10.1002/hec.3775](https://doi.org/10.1002/hec.3775).
- **Pergunta:** o PMM reduziu as internações por condições sensíveis à atenção primária (ICSAP)?
- **Dados:** painel municipal 2010–2016.
- **Método:** **diferenças em diferenças com pareamento por escore de propensão**, em três especificações, com teste de falsificação.
- **Resultado:** redução significativa de ICSAP, crescente e perceptível a partir do segundo ano. As magnitudes não foram conferidas.
- **Conclusão dos autores:** nas palavras deles, *"The results show a significant reduction in hospital admissions in treated municipalities with an increasing and perceptible effect in the second year of the program."*
- **Limitações:** pareamento só em observáveis; o tratamento é definido pela intensidade relativa.
- **Para a hipótese:** desfecho, não preenchimento.
- **Verificação:** A para o resumo.

#### C8. Mattos & Mazetto (2019) — *Assessing the Impact of More Doctors' Program on Healthcare Indicators in Brazil*

- **Referência:** *World Development*, 123, 104617. [doi:10.1016/j.worlddev.2019.104617](https://doi.org/10.1016/j.worlddev.2019.104617).
- **Pergunta:** quais os efeitos de curto prazo do PMM sobre uso de serviços, internações e mortalidade?
- **Dados:** municípios, 2010–2015.
- **Método:** **diferenças em diferenças**, sob tendências paralelas.
- **Resultado:** atendimentos **+5,9%**, consultas **+9,4%**, encaminhamentos **+12,3%**, visitas domiciliares **+29,7%**, internações **−4,6%**; **nenhum efeito** na mortalidade.
- **Conclusão dos autores:** nas palavras deles, *"it does not seem to have been able to reduce mortality in the municipalities"*.
- **Limitações:** horizonte curto.
- **Para a hipótese:** desfecho, não preenchimento.
- **Verificação:** A para o resumo.

#### C9. Thomas, Millett, Sousa Soares & Hone (2024) — *More Doctors, Better Health? A Generalised Synthetic Control Approach to Estimating Impacts of Increasing Doctors under Brazil's Mais Medicos Programme*

- **Referência:** *Social Science & Medicine*, 358, 117222. [doi:10.1016/j.socscimed.2024.117222](https://doi.org/10.1016/j.socscimed.2024.117222).
- **Pergunta:** qual o efeito de mais médicos por 100 mil habitantes sobre internações e mortalidade?
- **Dados:** painel mensal de 558 microrregiões, 2008–2017.
- **Método:** **controle sintético generalizado com tratamento contínuo**, com doadores da mesma UF. Os autores argumentam que as tendências paralelas fortes do DiD contínuo são implausíveis nesse contexto. Placebo com antecipação de seis meses.
- **Resultado:** **nenhum efeito significativo** de médicos do programa sobre internações ou mortalidade.
- **Conclusão dos autores:** nas palavras deles, *"We find limited effects of an increase in primary care physicians impacting health outcomes - with no significant impact of the Programa Mais Médicos on hospitalisations or mortality rates."*
- **Limitações:** a agregação por microrregião dilui a alocação dentro delas.
- **Para a hipótese:** ➖ **delimita** a cadeia oferta → saúde.
- **Verificação:** A — Europe PMC.

#### Nota — a 1ª chamada do Mais Médicos, agosto de 2013

O número que circula — **938 médicos confirmados para 15.460 vagas, 6%**, em
404 municípios, com bolsa de R$ 10 mil — vem de **imprensa** (*O Estado de S.
Paulo*, 07/08/2013, reproduzido pelo IHU), relatando anúncio do Ministério de
06/08/2013. **Não foi localizada fonte primária.** E há uma ressalva: Oliveira,
Sanchez & Santos (2016), *Ciência & Saúde Coletiva* 21(9), 2719–2727, atribuem
os 15.460 aos municípios que aderiram entre agosto de 2013 e julho de 2014,
não à 1ª chamada. O denominador talvez não seja o da chamada. **Verificação:**
B. Não usar em slide ou texto sem a fonte primária.

### D. Países de renda baixa e média: experimentos, escolha declarada e revisões

#### D1. Deserranno (2019) — *Financial Incentives as Signals: Experimental Evidence from the Recruitment of Village Promoters in Uganda*

- **Referência:** *American Economic Journal: Applied Economics*, 11(1), 277–317. [doi:10.1257/app.20170670](https://doi.org/10.1257/app.20170670).
- **Pergunta:** num cargo novo, cujas características os candidatos desconhecem, anunciar um pagamento esperado maior muda o tamanho e a composição do pool?
- **Dados:** Uganda, 2012, expansão do programa de agentes de saúde da ONG BRAC em 315 grupos comunitários, com cerca de 4.900 potenciais candidatas.
- **Método:** **experimento aleatorizado.** Três folhetos de recrutamento mostravam pontos diferentes da distribuição real de ganhos: baixo, médio e alto. O grupo de comparação é o braço baixo. A aleatorização é por grupo comunitário, e há um segundo experimento de informação, individual. O estimando é o ITT.
- **Resultado:** números da versão de tese, não conferidos no artigo:
  - candidatos por vaga **2,2 → 3,0** do braço baixo ao alto, cerca de **+36%**;
  - no braço alto, a chance de ver o cargo como de objetivo privado é 17% maior;
  - abandono 14 p.p. maior no braço alto.
- **Conclusão da autora:** pagar mais sinaliza menor valor social da função; atrai mais candidatos, mas afasta os mais pró-sociais, que ficam mais e rendem mais. Nas palavras dela: *"the signal they convey reduces the ability to recruit the most socially motivated agents, who are found to stay longer on the job and to perform better."*
- **Limitações:** cargo comunitário de baixa renda, pago por vendas. O efeito de sinal depende de o cargo ser desconhecido, o que não é o caso de uma vaga médica.
- **Para a hipótese:** ✅ mais candidatos, e portanto mais preenchimento; ⚠️ o pagamento seleciona contra o altruísmo, o termo $\alpha$ de Choné & Ma.
- **Verificação:** A para o resumo; **B** para os números.

#### D2. Ashraf, Bandiera, Davenport & Lee (2020) — *Losing Prosociality in the Quest for Talent? Sorting, Selection, and Productivity in the Delivery of Public Services*

- **Referência:** *American Economic Review*, 110(5), 1355–1394. [doi:10.1257/aer.20180326](https://doi.org/10.1257/aer.20180326).
- **Pergunta:** destacar benefícios de carreira no recrutamento atrai talento à custa da motivação pró-social, e qual o efeito sobre o desempenho e a saúde?
- **Dados:** Zâmbia, 2010, primeiro recrutamento nacional de agentes comunitários de saúde: 167 comunidades em 48 distritos, 2.457 candidaturas e 307 contratados.
- **Método:** **experimento aleatorizado por distrito**, 24 contra 24. O cartaz do tratamento destacava a carreira; o do controle, o benefício à comunidade. Depois da contratação, todos recebem a mesma informação, o que isola o canal de **seleção**. O estimando é o ITT.
- **Resultado:** visitas domiciliares **+29%**; partos na unidade **+30%**; crianças com baixo peso **−5 p.p.** sobre média de 21%, cerca de −25%.
- **Conclusão dos autores:** a carreira atrai candidatos mais talentosos, e a perda de pró-socialidade fica só entre os de baixo talento. Nas palavras deles: *"the marginal applicants in treatment are more talented and equally prosocial."*
- **Limitações:** o contraste é a saliência da carreira, não salário. Poder estatístico de 48 clusters.
- **Para a hipótese:** ✅ incentivos de carreira atraem sem custo de motivação na margem; contrabalança D1.
- **Verificação:** A — AEA e manuscrito aceito.

#### D3. Miranda et al. (2012) — *Stated Preferences of Doctors for Choosing a Job in Rural Areas of Peru: A Discrete Choice Experiment*

- **Referência:** *PLoS ONE*, 7(12), e50567. [doi:10.1371/journal.pone.0050567](https://doi.org/10.1371/journal.pone.0050567).
- **Pergunta:** que atributos do emprego levam médicos a escolher postos rurais no Peru?
- **Dados:** 102 médicos com contrato temporário do Ministério da Saúde em Ayacucho, 2010.
- **Método:** **DCE rotulado**: comunidade rural, cidade de Ayacucho ou outra capital provincial. Os atributos são renda, tempo até vaga permanente, pontos para residência médica, moradia, jornada e educação continuada. Havia opção de recusa, mas a análise usou só as escolhas forçadas, porque 7,4% recusaram. Logit condicional, seguido de simulações.
- **Resultado:**
  - preferência urbana com **OR 4,97 (IC95% 1,2–20,54)**;
  - +50% de salário com pontos para especialização: adesão rural de **21% para 52%**;
  - +75% com contrato permanente: **77%**.
- **Conclusão dos autores:** nas palavras deles, *"Doctors are five times more likely to favour a job in urban areas over rural settings."*
- **Limitações:** amostra pequena; preferência declarada.
- **Para a hipótese:** ✅ a remuneração pesa; ⚠️ só em pacote com carreira.
- **Verificação:** A — Europe PMC.

#### D4. Kurniati et al. (2024) — *What Medical Specialists Want to Stay in Remote Areas of Indonesia: Discrete Choice Experiments*

- **Referência:** *PLoS ONE*, 19(8), e0308225. [doi:10.1371/journal.pone.0308225](https://doi.org/10.1371/journal.pone.0308225).
- **Pergunta:** que características de um programa de retenção fazem **especialistas** permanecerem em áreas remotas da Indonésia?
- **Dados:** 341 especialistas de hospitais distritais em 10 províncias, amostra intencional, novembro de 2022.
- **Método:** **DCE** de escolha forçada entre duas alternativas, com oito atributos: local, instalações, renda, desenvolvimento profissional, segurança, duração do compromisso, fonte do incentivo e volume de casos. Logit condicional, com disposição a aceitar.
- **Resultado:** segurança garantida pelo governo local, **OR 6,11**; desenvolvimento profissional financiado, **OR 2,84**; instalações acima do padrão, **OR 2,35**; área remota com coeficiente negativo.
- **Conclusão dos autores:** é preciso um pacote, com ênfase em segurança; incentivos financeiros também são recomendados. Nas palavras deles: *"a comprehensive intervention package, with a particular emphasis on security provisions, is necessary to retain medical specialists in remote areas."*
- **Limitações:** amostra intencional; escolha forçada.
- **Para a hipótese:** ⚠️ **qualifica.** É a **única população de especialistas em exercício** encontrada, e nela o custo laboral e o de segurança pesam mais que a renda.
- **Verificação:** A — Europe PMC.

#### D5. Kruk et al. (2010) — *Rural Practice Preferences among Medical Students in Ghana: A Discrete Choice Experiment*

- **Referência:** *Bulletin of the World Health Organization*, 88(5), 333–341. [doi:10.2471/BLT.09.072892](https://doi.org/10.2471/BLT.09.072892).
- **Pergunta:** como atributos do emprego afetam a preferência de estudantes de medicina por postos rurais?
- **Dados:** 302 de 310 estudantes do 4º ano em Gana, 2009.
- **Método:** **DCE** com dois postos, ambos rurais, sem opção urbana nem de recusa. Os atributos incluem salário (+30%, +50%, 2×), equipamento, gestão, moradia e carro. Logit misto.
- **Resultado:** equipamento **β 1,42**; gestão de apoio **β 1,17**; retirar moradia **β −1,59**. Nas simulações, dobrar o salário equivale aproximadamente a melhorar equipamento ou gestão.
- **Conclusão dos autores:** nas palavras deles, *"Better working conditions were strongly associated with the stated choice of hypothetical rural postings."*
- **Limitações:** só opções rurais; estudantes, não médicos em exercício.
- **Para a hipótese:** ⚠️ **qualifica.** Capital e equipe, o $K$ e o $L$ do modelo, competem com o salário.
- **Verificação:** A — PMC.

#### D6. Kolstad (2011) — *How to Make Rural Jobs More Attractive to Health Workers. Findings from a Discrete Choice Experiment in Tanzania*

- **Referência:** *Health Economics*, 20(2), 196–211. [doi:10.1002/hec.1581](https://doi.org/10.1002/hec.1581).
- **Pergunta:** que incentivos tornam postos remotos atraentes para *clinical officers* recém-formados?
- **Dados:** cerca de 300 formandos de 10 escolas sorteadas na Tanzânia, 2007.
- **Método:** **DCE** binário forçado, com sete atributos, entre eles salário e adicional, educação continuada, moradia e infraestrutura. Logit, com disposição a pagar e simulações.
- **Resultado:** números do working paper: elevar o salário a 500 mil xelins por mês aumenta em **47 p.p.** a probabilidade de aceitar posto remoto; a 350 mil, em **26 p.p.**
- **Conclusão do autor:** nas palavras dele, *"offering continuing education after a certain period of service is one of the most powerful recruitment instruments the authorities have available."* Salário e adicional também pesam muito; mulheres respondem menos a dinheiro.
- **Limitações:** formandos; escolha forçada superestima a adesão.
- **Para a hipótese:** ✅ o salário move a escolha; ⚠️ a carreira compete.
- **Verificação:** A para o resumo; **B** para os números.

#### D7. Hanson & Jack (2010) — *Incentives Could Induce Ethiopian Doctors and Nurses to Work in Rural Settings*

- **Referência:** *Health Affairs*, 29(8), 1452–1460. [doi:10.1377/hlthaff.2009.0164](https://doi.org/10.1377/hlthaff.2009.0164).
- **Pergunta:** que combinação de salário, condições, moradia e formação levaria médicos e enfermeiros a áreas rurais da Etiópia?
- **Dados:** 861 profissionais (219 médicos) em 97 unidades.
- **Método:** **DCE** binário forçado com seis atributos, salário em 1×, 1,5× ou 2×. Probit de efeitos aleatórios e simulações.
- **Resultado:** dobrar o salário fora da capital eleva os médicos dispostos de **cerca de 7% para mais de 50%**. Moradia de qualidade, cerca de 27%, equivale a +46% de salário.
- **Conclusão dos autores:** para médicos, salário e moradia pesam mais; para enfermeiros, equipamento. Nas palavras deles: *"Choosing the right incentive package requires a consideration of both the effects of different packages on health workers' choices and the cost of those packages."*
- **Limitações:** escolha forçada; para médicos, o local não incluía a área rural propriamente dita.
- **Para a hipótese:** ✅ **reforça** para médicos.
- **Verificação:** A para o resumo; **B** para os números.

#### D8. Serneels et al. (2010) — *Who Wants to Work in a Rural Health Post? The Role of Intrinsic Motivation, Rural Background and Faith-Based Institutions in Ethiopia and Rwanda*

- **Referência:** *Bulletin of the World Health Organization*, 88(5), 342–349. [doi:10.2471/BLT.09.072728](https://doi.org/10.2471/BLT.09.072728).
- **Pergunta:** o que explica a disposição de futuros profissionais de saúde a trabalhar em área rural?
- **Dados:** 412 estudantes de enfermagem e medicina em Ruanda (2008) e 270 na Etiópia (2005).
- **Método:** **valoração contingente:** o salário mínimo exigido para o posto rural, regredido por regressão intervalar em características. Associação, sem desenho causal.
- **Resultado:** motivação intrínseca reduz o salário exigido em cerca de **23–31%** (coeficiente em log, −0,230 a −0,306).
- **Conclusão dos autores:** nas palavras deles, *"Intrinsic motivation and rural origin play an important role in health workers' decisions to work in a rural area, in addition to economic incentives."*
- **Limitações:** medida hipotética; associação.
- **Para a hipótese:** dá conteúdo ao $\alpha$ do modelo. O altruísmo **reduz** o custo do lugar.
- **Verificação:** A — PMC.

#### D9. Mandeville et al. (2016) — *The Use of Specialty Training to Retain Doctors in Malawi: A Discrete Choice Experiment*

- **Referência:** *Social Science & Medicine*, 169, 109–118. [doi:10.1016/j.socscimed.2016.09.034](https://doi.org/10.1016/j.socscimed.2016.09.034).
- **Pergunta:** que treinamento de especialidade os médicos jovens do Malawi valorizam, e ele serve para retê-los?
- **Dados:** 148 de 153 médicos elegíveis, 2012–2013.
- **Método:** **DCE** em duas etapas, primeiro **com opção de recusa** e depois forçado. Logit de classes latentes e disposição a pagar.
- **Resultado:** a maioria exigiria **quase o dobro** do salário para fazer o treinamento todo no país, e **mais de 6 vezes** para fazer oftalmologia.
- **Conclusão dos autores:** nas palavras deles, *"indiscriminate expansion of postgraduate training to slow emigration of doctors from sub-Saharan African countries may not be effective unless doctors' preferences are taken into account."*
- **Limitações:** amostra pequena; preferência declarada.
- **Para a hipótese:** contexto sobre carreira contra salário.
- **Verificação:** A — Europe PMC.

#### D10. Chomitz, Setiadi, Azwar, Ismail & Widiyarti (1998) — *What Do Doctors Want? Developing Incentives for Doctors to Serve in Indonesia's Rural and Remote Areas*

- **Referência:** World Bank Policy Research Working Paper 1888. [RePEc](https://ideas.repec.org/p/wbk/wbrwps/1888.html).
- **Pergunta:** que incentivos atrairiam médicos recém-formados para áreas remotas e muito remotas da Indonésia?
- **Dados:** escolhas reais de alocação no serviço compulsório, antes e depois de uma mudança de regra, mais 585 formandos de 14 escolas, 1997.
- **Método:** **preferência revelada** — logit multinomial antes e depois da mudança de regra, sem grupo de controle — e **preferência declarada** — 18 escolhas binárias, sem opção de recusa, por probit. Estima equivalentes monetários dos atributos.
- **Resultado:** para um formando homem de Java, o treinamento de especialista vale cerca de **Rp 4,2 milhões por mês**. Para mulheres, posto muito remoto custa **mais de Rp 3 milhões por mês**. Médicos das ilhas externas são muito mais propensos a aceitar posto muito remoto.
- **Conclusão dos autores:** nas palavras deles, *"Moderately (but not extremely) remote areas can be staffed using modest cash incentives."*
- **Limitações:** amostra de conveniência; antes e depois sem controle.
- **Para a hipótese:** ⚠️ **qualifica.** O custo do lugar é **não linear**: o dinheiro funciona no meio, não no extremo. É um argumento para heterogeneidade por remoticidade.
- **Verificação:** A — texto integral do Banco Mundial.

#### D11. Lagarde & Blaauw (2009) — *A Review of the Application and Contribution of Discrete Choice Experiments to Inform Human Resources Policy Interventions*

- **Referência:** *Human Resources for Health*, 7, 62. [doi:10.1186/1478-4491-7-62](https://doi.org/10.1186/1478-4491-7-62).
- **Pergunta:** como os DCEs têm sido usados para estudar escolhas de emprego de profissionais de saúde, e o que mostram?
- **Dados:** 9 ou 10 estudos — o resumo e o texto divergem —, em países de alta e de baixa renda.
- **Método:** **revisão narrativa**, não sistemática, sem meta-análise.
- **Resultado:** não há estimativa agregada.
- **Conclusão dos autores:** nas palavras deles, *"non-pecuniary incentives are significant determinants, sometimes more powerful than financial ones."*
- **Limitações:** poucos estudos; só preferência declarada.
- **Para a hipótese:** ⚠️ **qualifica.**
- **Verificação:** A — Europe PMC.

#### D12. Mandeville, Lagarde & Hanson (2014) — *The Use of Discrete Choice Experiments to Inform Health Workforce Policy: A Systematic Review*

- **Referência:** *BMC Health Services Research*, 14, 367. [doi:10.1186/1472-6963-14-367](https://doi.org/10.1186/1472-6963-14-367).
- **Pergunta:** como os DCEs sobre força de trabalho em saúde foram feitos, comparados às boas práticas, e o que mostram?
- **Dados:** 27 estudos, mais da metade em países de renda baixa e média.
- **Método:** **revisão sistemática** com avaliação de risco de viés por 13 critérios, sem meta-análise.
- **Resultado:** só **um terço** dos estudos tinha opção de recusa; bônus e pós-graduação pesam; compromissos de tempo são impopulares.
- **Conclusão dos autores:** nas palavras deles, *"Only one third of studies included an opt-out option, despite all health workers having the option to exit the labour market."*
- **Limitações:** heterogeneidade impede síntese quantitativa.
- **Para a hipótese:** **alerta de método.** Sem opção de recusa, o DCE **superestima** a resposta ao preço; a margem de preenchimento do PMM-E mede justamente a recusa.
- **Verificação:** A — Europe PMC.

#### D13. Grobler, Marais & Mabunda (2015) — *Interventions for Increasing the Proportion of Health Professionals Practising in Rural and Other Underserved Areas*

- **Referência:** *Cochrane Database of Systematic Reviews*, CD005314. [doi:10.1002/14651858.CD005314.pub3](https://doi.org/10.1002/14651858.CD005314.pub3).
- **Pergunta:** qual a efetividade de intervenções educacionais, financeiras, regulatórias ou de apoio para levar profissionais a áreas carentes?
- **Dados:** 8.945 registros triados até 2014; **um** estudo incluído, uma série temporal interrompida em Taiwan.
- **Método:** **revisão sistemática Cochrane**, que só aceita ensaios, antes e depois controlado e série temporal interrompida, com GRADE.
- **Resultado:** o seguro nacional de Taiwan associou-se a melhor equidade geográfica, com **certeza muito baixa**.
- **Conclusão dos autores:** nas palavras deles, *"There is currently limited reliable evidence regarding the effects of interventions aimed at addressing the inequitable distribution of health professionals."*
- **Limitações:** os critérios excluem quase toda a literatura.
- **Para a hipótese:** mostra a **lacuna**. Por critérios Cochrane, não há evidência causal sobre incentivo financeiro a profissionais de saúde — o espaço que o RDD da bolsa ocuparia.
- **Verificação:** A — Europe PMC.

#### D14. Wibulpolprasert & Pengpaibon (2003) — *Integrated Strategies to Tackle the Inequitable Distribution of Doctors in Thailand: Four Decades of Experience*

- **Referência:** *Human Resources for Health*, 1, 12. [doi:10.1186/1478-4491-1-12](https://doi.org/10.1186/1478-4491-1-12).
- **Pergunta:** que estratégias a Tailândia usou em quatro décadas para reduzir a desigualdade urbano-rural de médicos, e com que resultado?
- **Dados:** séries administrativas do Ministério da Saúde Pública, 1960–2002.
- **Método:** **estudo de caso descritivo**, sem grupo de comparação. As estratégias são serviço compulsório, infraestrutura, adicionais de difícil acesso — até US$ 500 por mês em 1997 — e recrutamento e formação rurais.
- **Resultado:** a razão de habitantes por médico entre o Nordeste e Bangkok caiu de **21 vezes (1979)** para **8,6 (1986)** e voltou a **13,8 (1996)**.
- **Conclusão dos autores:** as estratégias precisam ser integradas. Nas palavras deles: *"Financial incentives should be more flexible yet focused."*
- **Limitações:** descritivo; escrito por gestores do próprio sistema.
- **Para a hipótese:** contexto; pacote acima de instrumento isolado.
- **Verificação:** A — Europe PMC.

### E. Salário real, regulação salarial, família e dupla prática

Os termos $p_m$, renda alternativa e $c^{geo}$ do modelo.

#### E1. Propper & Van Reenen (2010) — *Can Pay Regulation Kill? Panel Data Evidence on the Effect of Labor Markets on Hospital Performance*

- **Referência:** *Journal of Political Economy*, 118(2), 222–273. [doi:10.1086/653137](https://doi.org/10.1086/653137). Versão anterior: NBER WP 13776.
- **Pergunta:** a regulação nacional do salário de enfermagem — praticamente igual em mercados locais diferentes — piora a qualidade hospitalar onde o salário externo é alto?
- **Dados:** todos os hospitais agudos do NHS inglês. A mortalidade em 30 dias por infarto é o desfecho; o salário externo é o de mulheres em ocupações não manuais num raio de 20 km.
- **Método:** usa a variação geográfica e temporal do **salário externo** contra um salário interno regulado quase constante. Efeitos fixos de hospital e de ano, GMM com defasagens como instrumentos, placebos em 42 setores não regulados e teste do canal de pessoal temporário.
- **Resultado:** **+10%** no salário externo → **+7%** na mortalidade, segundo o resumo do JPE; o working paper dá +4% a +8%.
- **Conclusão dos autores:** nas palavras deles, *"Higher outside wages significantly worsen hospital quality as measured by hospital deaths for emergency heart attacks."* A regulação aumenta a mortalidade agregada.
- **Limitações:** fatores locais não observados podem se correlacionar com o salário externo; há um único desfecho.
- **Para a hipótese:** ✅ **reforça a lógica do modelo.** O que atrai é o salário **relativo** à opção externa local. Uma bolsa uniforme compete pior onde o mercado privado paga mais.
- **Verificação:** A — RePEc e Crossref; detalhes de método no working paper.

#### E2. Elliott, Ma, Scott, Bell & Roberts (2007) — *Geographically Differentiated Pay in the Labour Market for Nurses*

- **Referência:** *Journal of Health Economics*, 26(1), 190–212. [doi:10.1016/j.jhealeco.2006.05.002](https://doi.org/10.1016/j.jhealeco.2006.05.002).
- **Pergunta:** quão competitivo é o salário de enfermeiros do NHS em cada mercado local, e isso afeta as vagas?
- **Dados:** mercados de trabalho locais da Grã-Bretanha.
- **Método:** *switching regression* para obter diferenciais salariais espaciais padronizados de enfermeiros e de ocupações de comparação; a diferença entre eles é relacionada à **taxa de vagas de longa duração**.
- **Resultado:** quanto menos competitivo o salário local, **maior a vacância** de longa duração. A magnitude não foi conferida.
- **Conclusão dos autores:** nas palavras deles, *"The competitiveness of nursing pay is shown to have a strong effect on the ability of the NHS to attract and retain nurses."*
- **Limitações:** identificação e magnitude não conferidas.
- **Para a hipótese:** ✅ **reforça.** É o único estudo do conjunto com **vacância** como desfecho, a mesma margem da hipótese.
- **Verificação:** A apenas para o resumo.

#### E3. Britton & Propper (2016) — *Teacher Pay and School Productivity: Exploiting Wage Regulation*

- **Referência:** *Journal of Public Economics*, 133, 75–89. [doi:10.1016/j.jpubeco.2015.12.004](https://doi.org/10.1016/j.jpubeco.2015.12.004).
- **Pergunta:** a diferença entre o salário docente nacional e o salário do mercado local afeta o desempenho das escolas?
- **Dados:** Inglaterra, mais de 3.000 escolas secundárias, cerca de 200 mil professores.
- **Método:** o salário docente é plano entre mercados heterogêneos. A regressão é do desempenho no salário externo defasado, com efeitos fixos de escola e duas observações por escola, análoga a uma diferença em diferenças. Há placebo com salários posteriores.
- **Resultado:** choque de **10%** na diferença → **−2%** no desempenho médio.
- **Conclusão dos autores:** nas palavras deles, *"We find that teachers respond to pay."*
- **Limitações:** apenas duas observações por escola.
- **Para a hipótese:** ✅ **reforça,** pelo mesmo mecanismo de E1.
- **Verificação:** A — resumo; desenho conferido no working paper.

#### E4. Moretti (2013) — *Real Wage Inequality*

- **Referência:** *American Economic Journal: Applied Economics*, 5(1), 65–103. [doi:10.1257/app.5.1.65](https://doi.org/10.1257/app.5.1.65).
- **Pergunta:** quanto do aumento do prêmio de escolaridade desde 1980 desaparece quando se deflaciona pelo custo de vida local?
- **Dados:** EUA, 1980–2000, microdados censitários por área metropolitana.
- **Método:** constrói índices de preço por cidade, dominados pela habitação, e compara os prêmios nominal e real. Usa instrumento *shift-share* para separar oferta de demanda.
- **Resultado:** o custo de vida explica **25% a 30%** do aumento do prêmio — de 20 p.p. nominais para 14–15 p.p. reais, segundo o working paper.
- **Conclusão do autor:** nas palavras dele, *"real wage differences between college and high school graduates have grown significantly less than nominal differences."*
- **Limitações:** o deflator ignora amenidades, que vão no sentido oposto (Diamond, 2016).
- **Para a hipótese:** fundamenta o deflator $p_m$. **Salário nominal não é utilidade.**
- **Verificação:** A — resumo; números do working paper.

#### E5. Albouy (2009) — *The Unequal Geographic Burden of Federal Taxation*

- **Referência:** *Journal of Political Economy*, 117(4), 635–667. [doi:10.1086/605309](https://doi.org/10.1086/605309).
- **Pergunta:** um imposto federal sobre a renda **nominal**, sem indexar ao custo de vida, cria cargas desiguais e distorce a localização?
- **Dados:** EUA, amostra de 5% do Censo 2000.
- **Método:** **equilíbrio espacial do tipo Rosen–Roback calibrado**, com impostos federais.
- **Resultado:** quem trabalha em cidade de salário acima da média paga **27%** mais imposto federal; o emprego nessas áreas cai **13%** na simulação.
- **Conclusão do autor:** nas palavras dele, *"Tax deductions index taxes partially to local cost of living, improving locational efficiency."*
- **Limitações:** são simulações calibradas, não estimativas causais.
- **Para a hipótese:** o espelho do PMM-E. Uma regra **nominal uniforme** distorce a alocação espacial; a bolsa uniforme por faixa vale mais em termos reais onde os preços são menores.
- **Verificação:** A — Crossref e RePEc.

#### E6. Albouy (2016) — *What Are Cities Worth? Land Rents, Local Productivity, and the Total Value of Amenities*

- **Referência:** *The Review of Economics and Statistics*, 98(3), 477–487. [doi:10.1162/REST_a_00550](https://doi.org/10.1162/REST_a_00550).
- **Pergunta:** como inferir produtividade, qualidade de vida e valor das amenidades a partir de salários e custo de moradia?
- **Dados:** EUA, Censo 2000, 325 áreas.
- **Método:** **equilíbrio espacial calibrado**, seguido de regressões dos índices em amenidades observáveis, que são associações.
- **Resultado:** as diferenças de salário e moradia refletem mais **produtividade** que qualidade de vida.
- **Conclusão do autor:** nas palavras dele, *"the most productive and valuable cities are typically coastal, sunny, mild, educated, and large."*
- **Limitações:** parâmetros calibrados.
- **Para a hipótese:** fundamenta $c^{geo}$, as amenidades.
- **Verificação:** A — resumo.

#### E7. Almeida & Azzoni (2016) — *Custo de vida comparativo das regiões metropolitanas brasileiras: 1996-2014*

- **Referência:** *Estudos Econômicos*, 46(1), 253–276. [doi:10.1590/0101-416146128aaa](https://doi.org/10.1590/0101-416146128aaa).
- **Pergunta:** quais os níveis relativos de custo de vida das regiões metropolitanas brasileiras e como evoluíram?
- **Dados:** 11 regiões metropolitanas e as POFs de 1996, 2003 e 2009.
- **Método:** **Country Product Dummy** aplicado às POFs, com interpolação nos anos intermediários. Medição, não causalidade.
- **Resultado:** os maiores custos estão em DF, São Paulo e Rio; Goiânia subiu para a terceira posição.
- **Conclusão dos autores:** nas palavras deles, *"não se encontraram indícios de que tenha havido mudanças significativas ao longo do período."*
- **Limitações:** só regiões metropolitanas, **sem o interior**, onde estão as vagas do PMM-E.
- **Para a hipótese:** a única medida brasileira de $p_m$ encontrada, e ela não cobre os municípios que importam.
- **Verificação:** A — revista da USP. O resumo em português diz "1996 a 2012".

#### E8. Socha & Bech (2011) — *Physician Dual Practice: A Review of Literature*

- **Referência:** *Health Policy*, 102(1), 1–7. [doi:10.1016/j.healthpol.2010.10.017](https://doi.org/10.1016/j.healthpol.2010.10.017).
- **Pergunta:** o que a literatura mostra sobre os efeitos da dupla prática pública e privada?
- **Dados:** 23 trabalhos.
- **Método:** **revisão sistemática** com discussão crítica, sem meta-análise.
- **Resultado:** evidência escassa; os modelos teóricos apontam efeitos nos dois sentidos.
- **Conclusão dos autores:** nas palavras deles, *"The subject is short on evidence."*
- **Limitações:** base pequena, predominantemente teórica.
- **Para a hipótese:** o termo $w^{priv}_m$ de H3 tem pouca base empírica direta.
- **Verificação:** A — resumo.

#### E9. McGrail, Russell & O'Sullivan (2017) — *Family Effects on the Rurality of GP's Work Location: A Longitudinal Panel Study*

- **Referência:** *Human Resources for Health*, 15, 75. [doi:10.1186/s12960-017-0250-z](https://doi.org/10.1186/s12960-017-0250-z).
- **Pergunta:** o local de trabalho rural do médico de família se associa à fase escolar dos filhos e ao trabalho do cônjuge?
- **Dados:** painel MABEL, Austrália, 2008–2014, com 4.377 médicos.
- **Método:** **equações de estimação generalizadas (GEE)**, estratificadas por sexo. Associação.
- **Resultado:**
  - homens com filho de 12 a 18 anos: **OR 0,83 (0,75–0,92)** de trabalhar em área rural;
  - mulheres com cônjuge empregado: **OR 0,89 (0,79–0,99)**.
- **Conclusão dos autores:** nas palavras deles, *"GP work location is related to key family needs which differ according to GP gender and educational stages of children."*
- **Limitações:** associação; poucos médicos mudam de local.
- **Para a hipótese:** fundamenta $c^{geo}$: o custo familiar varia com o ciclo de vida e o sexo.
- **Verificação:** A — PMC.

### F. Atração, permanência e origem

#### F1. Pathman, Konrad & Ricketts (1992) — *The Comparative Retention of National Health Service Corps and Other Rural Physicians: Results of a 9-Year Follow-up Study*

- **Referência:** *JAMA*, 268(12), 1552–1558. [doi:10.1001/jama.1992.03490120066030](https://doi.org/10.1001/jama.1992.03490120066030).
- **Pergunta:** médicos com obrigação de serviço do NHSC permanecem menos que os sem obrigação?
- **Dados:** 412 médicos em 178 clínicas rurais (36% do NHSC), 1981, reentrevistados em 1990.
- **Método:** **coorte** com análise de sobrevivência na prática original, com ajuste por características do médico, da prática e da comunidade.
- **Resultado:** após oito anos, **12%** dos médicos do NHSC contra **39%** dos demais seguiam na prática original; em prática não metropolitana, 29% contra 52%.
- **Conclusão dos autores:** nas palavras deles, *"the retention of rural NHSC physicians is seen to be poor and only partially explained by fixed physician, practice, or community variables."*
- **Limitações:** seleção para o programa; dados retrospectivos.
- **Para a hipótese:** ➖ **delimita.** Atrair com obrigação não é reter.
- **Verificação:** A — resumo.

#### F2. Pathman, Konrad, Dann & Koch (2004) — *Retention of Primary Care Physicians in Rural Health Professional Shortage Areas*

- **Referência:** *American Journal of Public Health*, 94(10), 1723–1729. [doi:10.2105/ajph.94.10.1723](https://doi.org/10.2105/ajph.94.10.1723).
- **Pergunta:** a retenção é menor em áreas rurais com escassez (HPSA) do que fora delas?
- **Dados:** amostra nacional de médicos recém-chegados, sem obrigação, entrevistados em 1991 e em 1996–97: 308 em HPSA e 197 fora.
- **Método:** **coorte prospectiva** com análise de sobrevivência.
- **Resultado:** **HR 1,28 (IC95% 0,97–1,69)**, não significativo.
- **Conclusão dos autores:** nas palavras deles, *"Poor recruitment is likely to be the principal dynamic underlying local rural shortages."*
- **Limitações:** exclui médicos com obrigação de serviço.
- **Para a hipótese:** ✅ o gargalo é **recrutar**, que é justamente a margem de preenchimento.
- **Verificação:** A — resumo.

#### F3. Bärnighausen & Bloom (2009) — *Financial Incentives for Return of Service in Underserved Areas: A Systematic Review*

- **Referência:** *BMC Health Services Research*, 9, 86. [doi:10.1186/1472-6963-9-86](https://doi.org/10.1186/1472-6963-9-86).
- **Pergunta:** programas de incentivo financeiro com contrapartida de serviço funcionam para recrutar e reter?
- **Dados:** 43 estudos de 10.495 triados — 34 dos EUA e um único de país em desenvolvimento.
- **Método:** **revisão sistemática**, com meta-análise de efeitos aleatórios para o cumprimento da obrigação e contagem de estudos para o resto.
- **Resultado:**
  - **71% (IC95% 60–80%)** cumpriram a obrigação;
  - em 6 de 7 estudos, os participantes ficaram **menos** no local original;
  - em 11 de 13, ficaram **mais** em alguma área carente.
- **Conclusão dos autores:** nas palavras deles, *"the evidence to date does not allow the inference that the programs have caused increases in the supply of health workers to underserved areas."*
- **Limitações:** todos os estudos são observacionais.
- **Para a hipótese:** a lacuna causal é antiga e reconhecida.
- **Verificação:** A — resumo.

#### F4. Rabinowitz, Diamond, Markham & Paynter (2001) — *Critical Factors for Designing Programs to Increase the Supply and Retention of Rural Primary Care Physicians*

- **Referência:** *JAMA*, 286(9), 1041–1048. [doi:10.1001/jama.286.9.1041](https://doi.org/10.1001/jama.286.9.1041).
- **Pergunta:** que fatores predizem a oferta e a retenção de médicos de atenção primária rural?
- **Dados:** 3.414 graduados do Jefferson Medical College, 1978–1993; 220 deles no programa de admissão seletiva (PSAP).
- **Método:** **coorte retrospectiva** com regressão logística de 19 preditores.
- **Resultado:** ter crescido em área rural, **OR 4,0 (IC95% 2,1–7,6)**; o PSAP é o único preditor de retenção, **OR 4,7 (2,0–11,2)**.
- **Conclusão dos autores:** nas palavras deles, *"the admissions component of the PSAP is the most important reason for its success."*
- **Limitações:** uma única escola; autosseleção.
- **Para a hipótese:** ⚠️ **qualifica.** Seleção por origem pesa mais que incentivo. É a mesma mensagem de C1.
- **Verificação:** A — resumo.

### G. Equilíbrio espacial e origem histórica da escassez

Já fichados de forma resumida no [catálogo 19](19_literatura_empirica_escolha_locacional_medicos.md); aqui com método e conclusão conferidos.

#### G1. Diamond (2016) — *The Determinants and Welfare Implications of US Workers' Diverging Location Choices by Skill: 1980–2000*

- **Referência:** *American Economic Review*, 106(3), 479–524. [doi:10.1257/aer.20131706](https://doi.org/10.1257/aer.20131706).
- **Pergunta:** por que os graduados se concentraram em cidades de salário e aluguel altos, e com que consequência para o bem-estar?
- **Dados:** EUA, áreas metropolitanas, 1980–2000.
- **Método:** **modelo estrutural de equilíbrio espacial** com demanda de trabalho, oferta de habitação, escolha discreta de local e amenidades endógenas à composição. Choques de demanda do tipo Bartik — detalhe de identificação não conferido no texto.
- **Resultado:** os choques de demanda local causaram a maior parte da segregação por qualificação, amplificada por amenidades endógenas.
- **Conclusão da autora:** nas palavras dela, *"local labor demand changes fundamentally caused the increased skill sorting."*
- **Limitações:** forma funcional; validade dos instrumentos.
- **Para a hipótese:** fundamenta a leitura de $c^{geo}$ e das amenidades; não é sobre médicos.
- **Verificação:** A para o resumo; **B** para o detalhe de identificação.

#### G2. Moehling, Niemesh, Thomasson & Treber (2020) — *Medical Education Reforms and the Origins of the Rural Physician Shortage*

- **Referência:** *Cliometrica*, 14(2), 181–225. [doi:10.1007/s11698-019-00187-w](https://doi.org/10.1007/s11698-019-00187-w).
- **Pergunta:** as reformas da educação médica do início do século XX contribuíram para a escassez de médicos rurais?
- **Dados:** EUA, duas primeiras décadas do século XX, diretórios médicos da AMA.
- **Método:** relaciona o rigor da escola de formação à probabilidade de o novo médico se instalar em área rural. A especificação econométrica não foi conferida, porque o texto integral é fechado. A equação de escolha do artigo (eq. 1, p. 184) é a base teórica do [modelo do projeto](../02_teoria/modelo_micro.md).
- **Resultado:** a probabilidade de um recém-formado se instalar em área rural **caiu 40%** no período; os formados em escolas mais rigorosas foram menos propensos a ir.
- **Conclusão dos autores:** nas palavras deles, *"the medical education reforms of the early twentieth century contributed to the urban–rural disparity in access to physician care."*
- **Limitações:** seleção de estudantes entre escolas; contexto histórico.
- **Para a hipótese:** origem da equação de escolha; evidência sobre formação, não sobre remuneração.
- **Verificação:** A para o resumo.

## 4. Síntese para a hipótese

A literatura **sustenta a direção** da hipótese e **qualifica fortemente sua
forma**. São cinco achados.

1. **Quando a remuneração varia por sorteio ou por regra, a aceitação e o
   recrutamento sobem.** México, elasticidade perto de 2 (A2). Noruega, 1,0 a
   1,9 (A3, A4). Gâmbia, Califórnia e Carolina do Norte (A5, A9, A10). Escócia,
   preenchimento de 57% para 88%, sem desenho causal (B6). **Embasa
   $\mathbb{E}(w \mid B)$.**
2. **O efeito depende do custo do lugar.** No México, a distância só derruba a
   aceitação quando o salário é baixo (A2). Na Indonésia, o dinheiro funciona no
   remoto moderado e não no extremo (D10). Na Gâmbia, o ganho cai nas escolas
   mais remotas (A5). Na Austrália, 65% não se mudam por nenhum pacote e os
   demais pedem de 37% a 130% da renda (B7). Equipamento, gestão, segurança e
   formação competem com o salário (D4, D5, B8, D11). **Embasa $c$ e o slide 13:
   "é a soma dos três que decide".**
3. **No RDD mais parecido com o PMM-E, o preenchimento não se moveu; a
   composição, sim** (A1). A mesma regra territorial com cutoff censitário,
   +13% de salário: efeito no preenchimento de 0,063 (EP 0,048), mas professor
   recrutado +0,42 dp. **Desafia a margem, não a direção.**
4. **Médicos são menos elásticos que outros profissionais.** No Brasil, de 0,4 a
   0,7, e o salário é a alavanca menos custo-efetiva diante de cotas e vagas
   para nascidos em áreas carentes (C1). Nos EUA, baixa resposta à compensação e
   forte apego ao local de formação (B9, B10). A resposta se concentra em
   **início de carreira** (B1, B3), e o PMM-E recruta especialistas já formados.
   **Qualifica a magnitude.**
5. **Atrair não é reter, e vínculo não é acesso.** Retenção só enquanto o
   pagamento dura (A11); com obrigação, retenção menor (F1, F3). Mais médicos
   sem menos espera (B2), sem melhora em saúde infantil (C6) ou mortalidade (C9),
   e com substituição da oferta existente (C2, C3). **Delimita o que o
   preenchimento pode afirmar.**

E dois achados sobre a **forma** da remuneração.

- **O que atrai é o salário relativo à opção local.** Uma escala nacional
  uniforme recruta pior onde o mercado local paga mais (E1, E2, E3). Para o
  especialista em dupla prática, $\mathbb{E}(w \mid B) = B + w^{priv}_m$: a bolsa
  pesa mais, em proporção, onde o mercado privado é menor. É a leitura
  territorial de H3.
- **Uma regra nominal uniforme distorce a alocação espacial** (E4, E5). A bolsa
  por faixa vale mais em termos reais onde os preços são menores. Num contraste
  local na fronteira de faixa, porém, $p_m$ é contínuo: o deflator muda a
  leitura da magnitude, não cria descontinuidade. **Não há índice de preços
  municipal oficial** que cubra os municípios das vagas (E7); qualquer $p_m$
  construído é construção do autor, com fonte, hash e rótulo.

A leitura que a banca pode levar é a do título da apresentação: **remuneração é
incentivo, e é limitado.** Pagar mais move a escolha; quanto move depende do
lugar e da pessoa; e a margem binária "preencheu ou não" pode ser a menos
sensível delas.

**A lacuna.** Pelos critérios Cochrane, não há evidência causal confiável sobre
incentivo financeiro a profissionais de saúde (D13, F3). Os RDDs em regra de
remuneração territorial são todos de **professores** (A1, A5–A8). Um RDD no
adicional da bolsa do PMM-E, se passar pelos portões, seria o primeiro com
**médicos especialistas**.

## 5. O que a literatura sugere para o protocolo, antes do congelamento

Sugestões, não decisões. Entram pela fila RDD
([`05_identificacao/14`](../05_identificacao/14_plano_implementacao_rdd_bolsa.md))
**antes** de qualquer consulta a outcome, ou não entram.

1. **Desfechos de composição e rapidez** ao lado do preenchimento: tempo até a
   homologação, chamada em que a célula foi preenchida, número de candidatos e
   perfil do homologado. É a lição de A1.
2. **Heterogeneidade pré-tratamento pela distância** até a capital ou o polo, o
   análogo dos 200 km de A2 e da não linearidade de D10, fixada com dados
   anteriores ao programa.
3. **Teste de deslocamento entre lados do limiar**, no painel município–mês,
   como em A1 e A5.
4. **Densidade da *running variable*.** Em A1, o cutoff censitário não foi
   manipulado e o administrativo foi. O IVS 2010 é censitário; o risco do PMM-E
   está na faixa publicada acima da categoria de IVS em 177 de 368 municípios
   ([`auditorias/07`](../auditorias/07_portao_rdd_bolsa.md)).
5. **Expectativa de magnitude**, para cálculo de poder e não para julgar
   resultado: com elasticidades de 0,4 a 0,7 para médicos no Brasil e um degrau
   de +33% a +50%, a literatura torna plausível uma resposta de algumas dezenas
   por cento sobre a base, e não dobrar o preenchimento.

## 6. Pendências de verificação

| Estudo | O que falta |
|---|---|
| A1 | o número de 2021 (+0,45 dp) e o de 2026 (+0,42) diferem; citar a versão e a data |
| A2 | conferir 15,1 p.p. e 2,15 nas tabelas da versão publicada (vêm do NBER WP 18156) |
| A4, A5, A6, A10 | conferir as tabelas publicadas; os números vêm das versões de working paper |
| A8 | o working paper dá 22–29 p.p.; o artigo, 17–21 p.p. — usar o do artigo |
| B2, B3, B4 | magnitudes; só o resumo foi acessível |
| B5, B9 | resumo só em fonte secundária |
| B8 | o "+20% de renda → +12 p.p." é de fonte secundária |
| C6 | magnitudes da versão publicada |
| D1, D6, D7 | números das versões de tese ou working paper |
| Nota da seção C | fonte primária da 1ª chamada do Mais Médicos (938 de 15.460) |
| E2 | coeficientes |
| G1 | estratégia de identificação no texto |
| Catálogo 19 | o artigo de Sivey et al. (B11) estava com título e DOI errados — corrigido |
