# 19. Literatura empírica sobre escolha locacional e provimento médico

> **Classificação:** literatura empírica<br>
> **Status:** catálogo canônico para motivação empírica e comparação de resultados<br>
> **Atualização:** 9 de setembro de 2026

## 1. Regra de uso

Os estudos deste documento podem documentar fatos estilizados, sugerir heterogeneidades e variáveis observáveis, orientar comparações e informar a discussão dos resultados.

Resultados estimados, calibrações e sinais encontrados nesses estudos pertencem à literatura empírica. Quando um artigo empírico oferece uma equação de escolha útil, sua formulação teórica pode ser reproduzida separadamente no [modelo microeconômico](../02_teoria/modelo_micro.md), com a adaptação e os limites explicitados.

## 2. Estudos centrais e uso permitido

| Estudo | Natureza empírica | Contribuição para o PMM-E | Uso vedado |
|---|---|---|---|
| Diamond (2016) | equilíbrio espacial estimado com dados de cidades dos EUA | mostrar como uma aplicação empírica trata renda, moradia, amenidades e heterogeneidade | fundamentar a função de utilidade ou os sinais teóricos |
| Moehling et al. (2020) | estudo histórico sobre educação médica e escassez rural, com modelo simples de escolha | motivar formação, origem e infraestrutura produtiva; a equação de escolha fundamenta o [modelo microeconômico](../02_teoria/modelo_micro.md) | transportar suas magnitudes históricas para o PMM-E |
| Costa, Nunes e Sanches (2019/2024) | escolha discreta com coeficientes aleatórios estimada para médicos generalistas formados no Brasil | motivar vínculos de nascimento/formação, salários reais, amenidades e infraestrutura | fornecer primitivas teóricas ou ser extrapolado automaticamente para especialistas |
| Sivey et al. (2012) | experimento de escolha discreta com médicos em formação na Austrália | mostrar que a disposição a aceitar posto remoto responde a incentivo monetário e quantificar a ordem de grandeza do trade-off | tratar preferência declarada como comportamento observado, ou transportar valores australianos para o Brasil |

## 3. Costa, Nunes e Sanches

O trabalho circulou como working paper em 2019 e foi publicado em 2024. A versão publicada deve ser a citação principal:

> Costa, F.; Nunes, L.; Sanches, F. M. (2024). [*How to Attract Physicians to Underserved Areas? Policy Recommendations from a Structural Model*](https://doi.org/10.1162/rest_a_01155). **The Review of Economics and Statistics**, 106(1), 36–52.

Os autores usam escolhas locacionais de médicos generalistas graduados entre 2001 e 2013 e estimam preferências por localidade com coeficientes aleatórios. O resultado especialmente pertinente é a relevância da proximidade do local de nascimento ou formação. Salário e infraestrutura importam, mas os contrafactuais favorecem políticas de formação e origem em áreas desassistidas em relação a incentivos financeiros.

Para o PMM-E, há três limites de transportabilidade: a amostra é de generalistas recém-formados; o PMM-E se dirige a especialistas; e a política atual combina bolsa-formação com uma regra administrativa baseada no IVS 2010. O artigo é central para a revisão empírica nacional, mas não é base da teoria econômica.

## 4. Diamond

> Diamond, R. (2016). [*The Determinants and Welfare Implications of US Workers' Diverging Location Choices by Skill: 1980–2000*](https://doi.org/10.1257/aer.20131706). **American Economic Review**, 106(3), 479–524.

Diamond estima um modelo de equilíbrio espacial com salários, aluguéis, amenidades, oferta de habitação e composição por escolaridade. É uma referência empírica estrutural de alta qualidade e uma aplicação moderna da tradição Rosen–Roback. Justamente por estimar o modelo com dados, não substitui Roback na seção teórica sob a regra do projeto.

## 5. Moehling et al.

> Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020). [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14(2), 181–225.

O estudo histórico-empírico motiva mecanismos de formação, origem, infraestrutura produtiva e escassez rural. Sua equação de escolha é reproduzida, separadamente de seus resultados, como núcleo do [modelo microeconômico](../02_teoria/modelo_micro.md).

## 6. Ponte permitida para o desenho empírico

| Dimensão sugerida pela evidência | Uso possível | Cuidado |
|---|---|---|
| local de nascimento e formação | heterogeneidade prévia | requer microdados individuais e proteção de dados |
| remuneração real | construção do tratamento e mecanismo | distinguir valor anunciado, devido e recebido |
| amenidades | covariáveis ou heterogeneidades prévias | não usar IVS como sinônimo |
| infraestrutura clínica | heterogeneidade por especialidade | congelar no pré-tratamento quando necessário |
| proximidade e custo de deslocamento | mecanismo locacional | definir rede e tempo de viagem antes de observar resultados |

O uso empírico requer correspondência com um primitivo do [modelo microeconômico](../02_teoria/modelo_micro.md), temporalidade adequada e compatibilidade com a estratégia causal. Achados de outras políticas não impõem sinais aos coeficientes do RDD do PMM-E.

## 7. Incentivos financeiros para provimento em áreas desassistidas

Levantamento de 09/09/2026, para a motivação da banca 1. Todos os números
abaixo foram conferidos na fonte primária, exceto onde indicado.

### 7.1 Evidência de que o incentivo monetário move a alocação

| Estudo | País | Desenho | Achado |
|---|---|---|---|
| Dal Bó, Finan & Rossi (2013), *QJE* 128(3) | México | **RCT**: salário anunciado sorteado entre 106 postos de um concurso público; oferta de vaga também sorteada | Salário 33% maior (3.750 → 5.000 pesos) eleva a aceitação em **15,1 p.p.** sobre base de 42,9%; elasticidade de oferta ≈ 2,15. Em postos a mais de 200 km, a aceitação vai de **25% para cerca de 80%**, e o aumento anula o desconto de ir do município de maior para o de menor IDH. Sem seleção adversa sobre motivação |
| Yong, Scott, Gravelle, Sivey & McGrail (2018), *Soc Sci Med* 214 | Austrália | DiD sobre mudança de elegibilidade geográfica (GPRIP 2010) | O incentivo aumentou a **entrada de recém-formados** nas localidades recém-elegíveis; **nenhum efeito** sobre entrada ou saída dos demais clínicos |
| Miranda et al. (2012), *PLoS ONE* 7(12) | Peru | Escolha discreta rotulada, 102 médicos | Salário +50% com pontos para especialização eleva a adesão rural de 21% para 52%; pacote com +75% e contrato permanente eleva a 77% |

### 7.2 A ordem de grandeza do prêmio exigido

| Estudo | País | Prêmio compensatório estimado |
|---|---|---|
| Scott et al. (2013), *Soc Sci Med* 96 | Austrália | Escolha discreta com 3.727 clínicos. **65% não se moveriam por nenhum pacote.** Quem se moveria exige **37%** da renda anual para cidade de 5 a 20 mil habitantes, **64%** para menos de 5 mil, e **130%** para o pior pacote |
| Costa, Nunes & Sanches (2024), *REStat* 106(1) | Brasil | Oferta inelástica: elasticidade-salário em torno de **0,4** nas metrópoles e **0,7** no interior |

A síntese defensável é um prêmio da ordem de **35% a 65% da remuneração**,
chegando acima de 100% nos postos mais penosos. O degrau do PMM-E — R$ 5 mil
sobre R$ 10 mil, ou +50% — cai dentro dessa faixa. **Ressalva de
comparabilidade:** os prêmios acima são sobre a renda total do médico, enquanto
a bolsa remunera 20 horas semanais; traduzir R$ 5 mil em "+50%" e comparar com
a régua australiana pressupõe que a bolsa seja a fração dominante do
rendimento, o que é hipótese sobre a composição de vínculos, não dado.

### 7.3 Evidência de que o incentivo é caro, ou insuficiente

| Estudo | País | Achado |
|---|---|---|
| Costa, Nunes & Sanches (2024), *REStat* 106(1) | Brasil | Elevar em 50% o salário público no interior do N/NE corrige **12,4%** do desequilíbrio geográfico, a **US$ 15,7 milhões por ponto percentual**. Cotas em escolas médicas para nascidos em áreas desassistidas corrigem **63,8%** a **US$ 2,2 a 5,1 milhões por ponto**. Os autores escrevem que "as baixas elasticidades-salário podem explicar por que incentivos financeiros no Brasil não foram suficientes para atrair mais médicos para áreas desassistidas" |
| Hone et al. (2020), *BMC Health Serv Res* 20:873 | Brasil (PMMB) | DiD em 5.565 municípios, 2008–2017: **+15,1 médicos do programa por 100 mil habitantes**, mas aumento líquido de apenas **+5,7**, por substituição de médicos preexistentes; ganhos menores nos municípios prioritários |
| Swami & Scott (2021), *Soc Sci Med* 281 | Austrália | O número de clínicos subiu nas áreas recém-elegíveis, mas **sem redução do tempo de espera** para pacientes já cadastrados |
| Holte, Kjær, Abelsen & Olsen (2015), *Soc Sci Med* 128 | Noruega | Renda tem **menos** impacto que atributos não pecuniários; exige pacotes conjuntos |
| Rabinowitz et al. (2001), *JAMA* 286(9) | EUA | Crescer em área rural prediz prática rural (OR 4,0); o componente de **admissão**, não o financeiro, explica o sucesso do programa |

### 7.4 A permanência não acompanha a atração

| Estudo | País | Achado |
|---|---|---|
| Pathman, Konrad & Ricketts (1992), *JAMA* 268(12) | EUA | Coorte de 9 anos, 412 médicos: após oito anos, **12%** dos que tinham bolsa com obrigação de serviço seguiam na prática original, contra **39%** dos sem obrigação |
| Matsumoto, Inoue & Kajii (2010), *Soc Sci Med* 71(4) | Japão | Egressos da Jichi Medical University: a proporção atuando no quintil mais rural cai de **30,8% (2000) para 8,7% (2006)** ao fim da obrigação |
| Bärnighausen & Bloom (2009), *BMC Health Serv Res* 9:86 | Multipaís | Revisão de 43 estudos: recrutamento cumprido de **71%**, retenção pós-obrigação entre **12% e 90%**; em 5 de 7 comparações os participantes tinham **menor** probabilidade de permanecer. Os autores concluem que a evidência não permite inferir efeito causal |
| OMS (2010), *Global policy recommendations* | Global | A recomendação sobre incentivos financeiros é **condicional**, com qualidade da evidência classificada como **baixa** |

### 7.5 Uso permitido no projeto

Nada nesta seção fundamenta equação teórica. Os números servem para calibrar
expectativa sobre magnitude e para situar a contribuição, nunca para impor
sinal a coeficiente do desenho brasileiro. Em particular, **nenhum dos estudos
acima usa RDD**: a evidência causal disponível é RCT de oferta salarial, DiD
sobre mudança de elegibilidade geográfica ou coorte observacional. Um desenho
de descontinuidade no adicional de bolsa, se os portões passarem, seria novo
nessa literatura.

## 8. A lacuna que este trabalho ocupa

Os três estudos centrais observam variação salarial de mercado, escolha
declarada em experimento ou contexto histórico. Nenhum deles observa o objeto
do PMM-E: **um valor de remuneração fixado por regra pública, uniforme dentro
da faixa e descontínuo em um escore territorial publicado**.

| Fonte de variação | Estudos | O que ela não permite |
|---|---|---|
| salário de mercado observado | Costa, Nunes e Sanches; Diamond | separar preço do lugar de preço da política; o salário é endógeno às condições locais |
| preferência declarada | Sivey et al. | garantir que a escolha hipotética se realize sob restrição orçamentária e oferta efetiva |
| choque histórico de formação | Moehling et al. | transportar magnitudes para um sistema de saúde e um mercado de trabalho distintos |
| **regra administrativa com degrau** | **PMM-E** | — |

Essa é a contribuição empírica pretendida, e também o motivo de o estimando
candidato ser o **incentivo marginal na fronteira de faixa**, e não a
participação no programa. Ver
[`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md).

## 9. Referências

- Bärnighausen, T.; Bloom, D. E. (2009). [*Financial incentives for return of service in underserved areas: a systematic review*](https://doi.org/10.1186/1472-6963-9-86). **BMC Health Services Research**, 9, 86.
- Costa, F.; Nunes, L.; Miessi Sanches, F. (2024). [*How to Attract Physicians to Underserved Areas? Policy Recommendations from a Structural Model*](https://doi.org/10.1162/rest_a_01166). **The Review of Economics and Statistics**, 106(1), 36--52.
- Dal Bó, E.; Finan, F.; Rossi, M. A. (2013). [*Strengthening State Capabilities: The Role of Financial Incentives in the Call to Public Service*](https://doi.org/10.1093/qje/qjt008). **The Quarterly Journal of Economics**, 128(3), 1169--1218.
- Hone, T.; Powell-Jackson, T.; Santos, L. M. P. et al. (2020). [*Impact of the Programa Mais Médicos on primary care doctor supply and health outcomes*](https://doi.org/10.1186/s12913-020-05716-2). **BMC Health Services Research**, 20, 873.
- Matsumoto, M.; Inoue, K.; Kajii, E. (2010). [*Long-term effect of the home prefecture return program on the geographic distribution of physicians*](https://doi.org/10.1016/j.socscimed.2010.05.006). **Social Science & Medicine**, 71(4), 667--671.
- Pathman, D. E.; Konrad, T. R.; Ricketts, T. C. (1992). [*The comparative retention of National Health Service Corps and other rural physicians*](https://doi.org/10.1001/jama.1992.03490120066030). **JAMA**, 268(12), 1552--1558.
- Scott, A.; Witt, J.; Humphreys, J. et al. (2013). [*Getting doctors into the bush: general practitioners' preferences for rural location*](https://doi.org/10.1016/j.socscimed.2013.07.002). **Social Science & Medicine**, 96, 33--44.
- Swami, M.; Scott, A. (2021). [*Impact of rural workforce incentives on access to GP services*](https://doi.org/10.1016/j.socscimed.2021.114045). **Social Science & Medicine**, 281, 114045.
- World Health Organization (2010). [*Increasing access to health workers in remote and rural areas through improved retention*](https://www.ncbi.nlm.nih.gov/books/NBK138626/). WHO, Geneva.
- Yong, J.; Scott, A.; Gravelle, H.; Sivey, P.; McGrail, M. (2018). [*Do rural incentives payments affect entries and exits of general practitioners?*](https://doi.org/10.1016/j.socscimed.2018.08.014). **Social Science & Medicine**, 214, 197--205.
- Diamond, R. (2016). [*The Determinants and Welfare Implications of US Workers' Diverging Location Choices by Skill: 1980–2000*](https://doi.org/10.1257/aer.20131706). **American Economic Review**, 106(3), 479–524.
- Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020). [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14, 181–225.
- Sivey, P.; Scott, A.; Witt, J.; Joyce, C.; Humphreys, J. (2012). [*Junior Doctors' Preferences for Specialty and Location: A Discrete Choice Experiment*](https://doi.org/10.1016/j.jhealeco.2012.06.002). **Journal of Health Economics**, 31(6), 813–823.
