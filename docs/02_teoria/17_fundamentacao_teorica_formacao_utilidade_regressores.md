# 17. Fundamentação teórica microeconômica da escolha e retenção locacional médica

> **Classificação:** literatura teórica e modelo microeconômico autoral<br>
> **Status:** documento teórico canônico<br>
> **Atualização:** 2 de setembro de 2026

## 1. Regra de demarcação

Este documento contém somente referências usadas por sua contribuição teórica, equações dos modelos teóricos consultados e extensões autorais explicitamente identificadas.

Artigos que estimam regressões ou modelos estruturais com dados — ainda que tragam uma função de utilidade — pertencem exclusivamente à [literatura empírica](../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md) e não fundamentam as equações abaixo.

Probit, logit, Cox, diferenças em diferenças e RDD são especificações de estimação ou identificação. Não são primitivas do modelo microeconômico.

## 2. Decisão sobre as referências anteriores

| Referência anterior | Decisão | Base adotada | Razão |
|---|---|---|---|
| Roback (1982) | manter apenas como antecedente genealógico | Redding e Rossi-Hansberg (2017) | A síntese moderna explicita consumo, solo residencial, mobilidade, heterogeneidade locacional, amenidades e fricções espaciais. |
| Reinhardt (1975) | retirar da derivação canônica | Choné e Ma (2011); Barigozzi e Burani (2016) | A primeira referência formaliza agência médica; a segunda formaliza esforço, missão, salário e seleção de profissionais de saúde. |

Não existe substituto recente único que reproduza honestamente todos os elementos antes atribuídos a Reinhardt. A substituição correta é modular. A leitura do original também mostra que $D$ representa a percepção do consumo de serviços médicos na comunidade e que $L$ inclui o custo psíquico de administrar auxiliares. Portanto, não é rigoroso traduzi-los diretamente como “impacto assistencial” e “equipe que reduz sobrecarga”.

## 3. Bloco espacial: Redding e Rossi-Hansberg (2017)

Redding e Rossi-Hansberg organizam a teoria espacial quantitativa em torno de consumo, solo residencial, mobilidade, amenidades e fricções entre residência e trabalho. Uma especialização para o PMM-E é:

$$
U^{S}_{imt}=A_{mt}C_{imt}^{\alpha}h_{imt}^{1-\alpha},
\qquad 0<\alpha<1,
$$

$$
P_{mt}C_{imt}+R_{mt}h_{imt}\leq Y_{imt},
\qquad Y_{imt}=y^{0}_{imt}+B_{mt},
$$

onde $C$ é o composto de consumo, $h$ é moradia, $P$ é o índice local de preços, $R$ é o aluguel, $A$ reúne amenidades, $y^0$ é a renda esperada fora da bolsa e $B$ é a bolsa-formação.

Após maximizar em $C$ e $h$, a utilidade indireta espacial, a menos de uma constante, é:

$$
v^{S}_{imt}
=\log A_{mt}+\log Y_{imt}
-\alpha\log P_{mt}-(1-\alpha)\log R_{mt}.
$$

Maior renda real e melhores amenidades elevam a atratividade; preços e aluguel a reduzem. A inclusão multiplicativa de $A_{mt}$ é uma **especialização autoral** coerente com o bloco de amenidades discutido pelos autores, não uma transcrição literal de uma equação numerada do artigo.

## 4. Bloco da prática médica: Choné e Ma (2011)

Choné e Ma constroem um modelo teórico de agência no qual o médico pondera retorno próprio e benefício do paciente. Adaptando a notação ao PMM-E:

$$
u^{P}_{imt}
=b_{mt}q_{imt}
-C(q_{imt},H_{imt};K_{mt},L_{mt},\Omega_{mt})
+\beta_iG(q_{imt},D_{mt}),
$$

onde $q$ é atividade/qualidade assistencial, $b$ é eventual remuneração marginal por produção, $H$ é tempo de trabalho, $K$ é capital clínico, $L$ é equipe, $\Omega$ é a organização da rede, $G$ é o benefício do paciente e $\beta_i\geq0$ mede a preocupação do médico com esse benefício.

Para uma solução interior:

$$
b_{mt}+\beta_iG_q(q_{imt},D_{mt})
=C_q(q_{imt},H_{imt};K_{mt},L_{mt},\Omega_{mt}).
$$

Choné e Ma autorizam a presença de retorno próprio, custo e benefício do paciente. As derivadas abaixo são **hipóteses estruturais do modelo autoral**, e não resultados atribuídos ao artigo:

$$
C_H>0,\qquad C_{qK}<0,\qquad C_{qL}<0,\qquad C_{q\Omega}<0.
$$

Elas dizem que jornadas maiores geram custo e que equipamentos, equipe e organização podem reduzir o custo marginal de produzir cuidado. A evidência empírica poderá apoiar ou rejeitar essas hipóteses; não deve transformá-las em teoremas.

## 5. Bloco de missão: Barigozzi e Burani (2016)

Barigozzi e Burani desenvolvem um modelo teórico no qual hospitais com e sem finalidade lucrativa competem por profissionais de saúde que conhecem sua própria habilidade e motivação. O contrato combina tarefa/esforço e remuneração não linear. Profissionais motivados obtêm benefício não pecuniário ao contribuir para a missão social do hospital.

Uma representação reduzida do mecanismo teórico é:

$$
u^{BB}_{ij}
=w_j(e_{ij})-c(e_{ij};a_i)
+\mathbf 1\{j=M\}\gamma_i e_{ij},
$$

em que $e$ é esforço/quantidade de cuidado, $a_i$ é habilidade, $\gamma_i$ é motivação intrínseca e $M$ identifica a organização orientada por missão. No artigo, a missão diferencia hospitais sem fins lucrativos.

No PMM-E, o prêmio não pecuniário é generalizado para $\gamma_i\mu_m(e_{im})$, permitindo que a missão varie entre postos. Essa é uma **adaptação autoral**. Como renda e custo de esforço já aparecem nos blocos anteriores, o modelo unificado importa apenas esse prêmio de missão, evitando dupla contagem.

O resultado qualitativo relevante é seleção: profissionais mais motivados podem aceitar salários menores e fornecer mais cuidado em organizações orientadas por missão. O canal varia entre pessoas e organizações. “Propósito” não deve receber sinal homogêneo diretamente a partir do IVS.

## 6. Modelo microeconômico autoral do PMM-E

O fluxo de utilidade do médico $i$ no município $m$ e período $t$ é:

$$
u_{imt}=v^{S}_{imt}+u^{P}_{imt}+\gamma_i\mu_m(e_{imt})
-\tau_{im}+\varepsilon_{imt},
$$

onde $\tau_{im}$ reúne distância, dupla residência, afastamento familiar e instalação. Para separar atração de retenção:

$$
V_{imt}=u_{imt}
+\delta\,\mathbb{E}_t\left[
\max_{n\in\mathcal I\cup\{0\}}
\{V_{in,t+1}-\kappa_{imn,t+1}\}
\right],
$$

em que $0$ é a alternativa externa e $\kappa_{imn}$ é o custo de trocar de localidade. Esta equação de Bellman é uma **extensão autoral** dos três blocos teóricos.

A escolha inicial é:

$$
m^*_{it}\in\arg\max_{m\in\mathcal I\cup\{0\}}V_{imt}.
$$

Depois da entrada, há permanência em $m$ quando:

$$
V_{imt}\geq
\max_{n\neq m}\{V_{int}-\kappa_{imn,t}\}.
$$

Atração e retenção são decisões relacionadas, mas distintas: a primeira compara a vaga com a alternativa externa; a segunda compara continuar com sair, já incorporando custos de troca e informação adquirida no posto.

## 7. Compensação monetária e previsões

A compensação mínima para aceitar $m$ é definida implicitamente por:

$$
V_{im0}(B^{WTA}_{im})=V_{i00}.
$$

Sob monotonicidade da utilidade na renda, $\partial V_{im}/\partial B_m>0$. O modelo prevê:

1. bolsa maior tende a elevar a atração;
2. aluguel, custo de vida, distância e instalação elevam o $WTA$;
3. amenidades, infraestrutura, equipe e organização podem reduzir o $WTA$;
4. congruência de missão reduz o $WTA$ apenas para médicos que valorizam aquela missão.

O IVS 2010 é a running variable administrativa canônica, não uma medida estrutural suficiente de todas essas dimensões. Seu efeito sobre $V_{im}$ é ambíguo porque pode estar associado à faixa da bolsa, a desamenidades, à necessidade assistencial e à missão. IDHM ou PIB per capita não substituem o IVS 2010.

## 8. Ponte autorizada para regressores

| Primitivo | Sinal estrutural | Proxy candidata | Status |
|---|---:|---|---|
| Bolsa $B$ | $\partial V/\partial B>0$ | valor devido e recebido | tratamento; requer dados administrativos |
| Preços $P$ e aluguel $R$ | negativo | custo de vida/moradia | validar |
| Amenidades $A$ | positivo | acesso, segurança e serviços | não substituir pelo IVS |
| Capital $K$ | reduz custo marginal sob hipótese | equipamentos, leitos, habilitações | medir no pré-tratamento |
| Equipe $L$ | reduz custo marginal sob hipótese | FTE de enfermagem/apoio | evitar variável pós-tratamento |
| Organização $\Omega$ | reduz custo marginal sob hipótese | rede de referência/complexidade | validar |
| Distância $\tau$ | negativo | tempo até polo/capital | validar |
| Benefício $G$ e altruísmo $\beta_i$ | heterogêneo | necessidade × características prévias | não observados diretamente |
| Missão $\gamma_i\mu_m(e)$ | heterogêneo | vínculo territorial/trajetória | requer microdados individuais |

O mapeamento não converte proxies em fundamentos teóricos. Apenas indica como operacionalizar primitivos, sujeito à temporalidade, observabilidade e estratégia causal.

## 9. Fora do escopo teórico

- resultados de qualquer estudo empírico;
- equações de Cox, Kaplan–Meier, logit/probit, DiD, DDD ou RDD;
- sinais impostos a coeficientes econométricos;
- percentuais de retenção ou magnitudes retirados de outras políticas.

Esses itens pertencem à literatura empírica ou à metodologia econométrica.

## 10. Referências teóricas

- Barigozzi, F.; Burani, N. (2016). [*Competition and Screening with Motivated Health Professionals*](https://doi.org/10.1016/j.jhealeco.2016.06.003). **Journal of Health Economics**, 50, 358–371.
- Choné, P.; Ma, C.-T. A. (2011). [*Optimal Health Care Contract under Physician Agency*](https://people.bu.edu/ma/CHONE-MA_Annals2011.pdf). **Annals of Economics and Statistics**, 101/102, 229–256.
- Redding, S. J.; Rossi-Hansberg, E. (2017). [*Quantitative Spatial Economics*](https://doi.org/10.1146/annurev-economics-063016-103713). **Annual Review of Economics**, 9, 21–58.

### Antecedentes mantidos apenas para genealogia

- Reinhardt, U. E. (1975). *Health Manpower Planning in a Market Context: The Case of Physician Manpower*. Em *Systems Aspects of Health Planning*, pp. 131–162.
- Roback, J. (1982). [*Wages, Rents, and the Quality of Life*](https://doi.org/10.1086/261120). **Journal of Political Economy**, 90(6), 1257–1278.
- Besley, T.; Ghatak, M. (2005). [*Competition and Incentives with Motivated Agents*](https://doi.org/10.1257/0002828054201413). **American Economic Review**, 95(3), 616–636.
