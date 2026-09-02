# 19. Literatura empírica sobre escolha locacional e provimento médico

> **Classificação:** literatura empírica<br>
> **Status:** catálogo canônico para motivação empírica e comparação de resultados<br>
> **Atualização:** 2 de setembro de 2026

## 1. Regra de uso

Os estudos deste documento podem documentar fatos estilizados, sugerir heterogeneidades e variáveis observáveis, orientar comparações e informar a discussão dos resultados.

Resultados estimados, calibrações e sinais encontrados nesses estudos pertencem à literatura empírica. Quando um artigo empírico oferece uma equação de escolha útil, sua formulação teórica pode ser reproduzida separadamente no documento 17, com a adaptação e os limites explicitados.

## 2. Estudos centrais e uso permitido

| Estudo | Natureza empírica | Contribuição para o PMM-E | Uso vedado |
|---|---|---|---|
| Diamond (2016) | equilíbrio espacial estimado com dados de cidades dos EUA | mostrar como uma aplicação empírica trata renda, moradia, amenidades e heterogeneidade | fundamentar a função de utilidade ou os sinais teóricos |
| Moehling et al. (2020) | estudo histórico sobre educação médica e escassez rural, com modelo simples de escolha | motivar formação, origem e infraestrutura produtiva; a equação de escolha fundamenta o documento 17 | transportar suas magnitudes históricas para o PMM-E |
| Costa, Nunes e Sanches (2019/2024) | escolha discreta com coeficientes aleatórios estimada para médicos generalistas formados no Brasil | motivar vínculos de nascimento/formação, salários reais, amenidades e infraestrutura | fornecer primitivas teóricas ou ser extrapolado automaticamente para especialistas |

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

O estudo histórico-empírico motiva mecanismos de formação, origem, infraestrutura produtiva e escassez rural. Sua equação de escolha é reproduzida, separadamente de seus resultados, como núcleo do [modelo teórico](../02_teoria/17_fundamentacao_teorica_formacao_utilidade_regressores.md).

## 6. Ponte permitida para o desenho empírico

| Dimensão sugerida pela evidência | Uso possível | Cuidado |
|---|---|---|
| local de nascimento e formação | heterogeneidade prévia | requer microdados individuais e proteção de dados |
| remuneração real | construção do tratamento e mecanismo | distinguir valor anunciado, devido e recebido |
| amenidades | covariáveis ou heterogeneidades prévias | não usar IVS como sinônimo |
| infraestrutura clínica | heterogeneidade por especialidade | congelar no pré-tratamento quando necessário |
| proximidade e custo de deslocamento | mecanismo locacional | definir rede e tempo de viagem antes de observar resultados |

O uso empírico requer correspondência com um primitivo do [modelo teórico](../02_teoria/17_fundamentacao_teorica_formacao_utilidade_regressores.md), temporalidade adequada e compatibilidade com a estratégia causal. Achados de outras políticas não impõem sinais aos coeficientes do RDD do PMM-E.
