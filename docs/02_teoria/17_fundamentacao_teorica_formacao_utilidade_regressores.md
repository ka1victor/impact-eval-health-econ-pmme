# 17. Fundamentação teórica da escolha locacional médica

> **Classificação:** literatura teórica e modelo microeconômico autoral<br>
> **Status:** documento teórico canônico<br>
> **Atualização:** 2 de setembro de 2026

---

## 1. Modelo principal: escolha locacional em Moehling et al. (2020)

Moehling et al. (2020, eq. 1, p. 184) formulam a distribuição espacial de médicos a partir da maximização intertemporal dos retornos líquidos esperados de cada localidade:

```math
\arg\max_{j \in J}\;U(\omega_j)
=
\arg\max_{j \in J}
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{jt}^{(s)}\right)}{p_{jt}}
- c_{jt}^{(s)}
\right].
```

- $j \in J$: localidade de atuação (município ou condado);
- $t$ e $\delta \in (0,1)$: períodos de exercício profissional e fator de desconto intertemporal;
- $s$: especialidade ou grupo de qualificação médica;
- $w_{jt}^{(s)}$: rendimento nominal auferido na localidade;
- $p_{jt}$: nível de preços local (custo de vida);
- $c_{jt}^{(s)}$: custo locacional líquido não pecuniário, que agrega preferências pessoais, amenidades, moradia, condições de trabalho e proximidade da família ([Moehling et al., 2020, p. 184](https://doi.org/10.1007/s11698-019-00187-w)).

### Adaptação ao PMM-E e convenção de notação

No artigo original de Moehling, o índice $i$ foi utilizado para representar localidades ($i \in I$). Na notação microeconômica usual de economia espacial e mobilidade de trabalho, adota-se uma convenção mais intuitiva e livre de ambiguidades:
- Indexa-se o **médico** por $i$ (indivíduo);
- Indexa-se o **município de atuação (destino)** por $m \in \mathcal{M}$ (ou a opção externa de não adesão por $0$);
- Indexa-se o **município de origem/família do médico** por $o(i)$;
- Indexa-se a especialidade médica por $s$.

A decisão ótima de candidatura e ocupação da vaga é dada por:

```math
m_i^* \in \arg\max_{m \in \mathcal{M} \cup \{0\}} V_{im}^{(s)}.
```

No PMM-E (Lei nº 15.233/2025), o médico bolsista não recebe pagamento por produção marginal, mas uma bolsa pré-fixada como função da vulnerabilidade do município, $B_m(IVS_m)$. A bolsa entra diretamente na remuneração esperada $w_{imt}^{(s)}$. 

Na especificação basal mínima (antes da abertura dos componentes com microdados), a utilidade esperada é expressa em forma reduzida:

```math
V_{im}^{(s,0)}
=
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{imt}^{(s)}\mid B_m(IVS_m)\right)}{p_{mt}}
- c_0^{(s)}(IVS_m)
\right]
+\varepsilon_{im}.
```

- $c_0^{(s)}(IVS_m)$ é o custo locacional líquido latente associado ao município, resumindo todas as desvantagens e amenidades não observadas.
- $\varepsilon_{im}$ é o choque idiossincrático de preferência do médico $i$ pelo município $m$.
- Não se impõe *a priori* que $c_0'(IVS) > 0$: desvantagens de infraestrutura competem com oportunidades de maior impacto social para médicos vocacionados.

---

## 2. Microfundamentação dos componentes do custo locacional

Para compreender os canais econômicos que constituem $c$, a teoria microeconômica decompõe estruturalmente esse custo. Cada bloco abaixo apresenta o artigo teórico de referência, sua equação exata e a derivada parcial do custo locacional.

### 2.1. Distância geográfica da origem: Moehling et al. (2020)

Moehling et al. (2020, p. 184) destacam explicitamente que o custo locacional não pecuniário inclui a proximidade da rede de apoio familiar (*"proximity to family"*). 

Sendo $o(i)$ o município de origem/família do médico $i$ e $m$ o município do posto de trabalho, a distância física ou tempo de viagem é $\text{dist}_{im} = d(o(i), m)$. O componente de distanciamento do custo é expresso como:

```math
c^{\text{dist}}_{im} = \phi(\text{dist}_{im}).
```

**Derivada parcial do custo:**
```math
\frac{\partial c^{\text{dist}}_{im}}{\partial \text{dist}_{im}} = \phi'(\text{dist}_{im}) > 0.
```

*Fundamentação na literatura:* Moehling et al. (2020, p. 184, eq. 1; [manuscrito, p. 6](https://niemesgt.github.io/files/MoehlingNiemeshThomassonTreber2019.pdf)). Como a proximidade familiar gera utilidade direta e amenidade de convivência, afastar-se da origem impõe custos logísticos e psicológicos crescentes, elevando estritamente o custo locacional ($\frac{\partial c}{\partial \text{dist}} > 0$).

### 2.2. Preço de moradia e amenidades: Redding e Rossi-Hansberg (2017)

Redding e Rossi-Hansberg (2017, p. 28, eq. 24) modelam a utilidade indireta de um indivíduo $o$, residente no local $n$ e empregado no local $i$:

```math
u_{nio} = \frac{z_{nio}B_n w_i}{\kappa_{ni}Q_n^{\,1-\beta}}.
```

**Significado de cada termo:**
- $u_{nio}$: utilidade indireta do trabalhador individual;
- $w_i$: **salário nominal auferido no local de trabalho** $i$;
- $B_n$: **amenidades residenciais no local de moradia** $n$ (qualidade de vida, segurança, infraestrutura urbana);
- $Q_n$: **preço do espaço residencial (custo de moradia/aluguel)** na localidade $n$;
- $\kappa_{ni} \ge 1$: **custo iceberg de deslocamento pendular** (*commuting*) entre residência $n$ e trabalho $i$ ($\kappa_{ii} = 1$);
- $z_{nio}$: choque de preferência idiossincrática com distribuição de Fréchet;
- $1-\beta \in (0,1)$: **parcela da renda despendida em habitação** (sendo $\beta$ a fração gasta em bens comercializáveis).

**Derivação da função custo:**
No modelo de Moehling et al. (2020), a utilidade intertemporal compara o logaritmo da renda real contra o custo locacional ($\ln w - c$). Tomando o logaritmo natural de $u_{nio}$:
$$\ln u_{nio} = \ln w_i - \left[ (1-\beta)\ln Q_n - \ln B_n + \ln \kappa_{ni} - \ln z_{nio} \right].$$
Para um médico que reside e trabalha no mesmo município ($n = i = m$, de modo que $\kappa_{mm} = 1$ e $\ln\kappa_{mm} = 0$), comparando diretamente com $\ln w_m - c_m^{\text{espacial}}$, a função de custo espacial líquido é:

```math
c^{\text{espacial}}_m = (1-\beta)\ln Q_m - \ln B_m.
```

**Derivadas parciais do custo:**
```math
\frac{\partial c^{\text{espacial}}_m}{\partial Q_m} = \frac{1-\beta}{Q_m} > 0,
\qquad
\frac{\partial c^{\text{espacial}}_m}{\partial B_m} = -\frac{1}{B_m} < 0.
```

*Fundamentação na literatura:* Redding e Rossi-Hansberg (2017, p. 28, eq. 24; [manuscrito, p. 28](https://rossihansberg.economics.uchicago.edu/QSE.pdf)). Moradias mais caras ($Q_m$) aumentam o custo locacional de forma proporcional à participação do aluguel no orçamento ($1-\beta$), enquanto melhores amenidades urbanas locais ($B_m$) reduzem a desutilidade de viver no município.

### 2.3. Custo da prática, tecnologia clínica e altruísmo: Choné & Ma (2011) e Reinhardt (1975)

Choné e Ma (2011, p. 232, eq. 1) formulam a função de utilidade exata do médico sob agência:

```math
U = R - C(q) + \alpha B(q),
```

em que:
- $R$ é a remuneração/transferência financeira total recebida pelo médico;
- $q$ é a quantidade ou intensidade de cuidados e tratamentos clínicos prestados;
- $C(q)$ é o custo de esforço clínico do médico para produzir $q$, com $C'(q) > 0$ e $C''(q) > 0$;
- $B(q)$ é o benefício de saúde auferido pelo paciente, com $B'(q) > 0$ e $B''(q) \le 0$;
- $\alpha \ge 0$ é o coeficiente de altruísmo do médico em relação à melhora clínica do paciente.

Pela teoria da tecnologia de produção médica de Reinhardt (1975, caps. 3 e 4), a quantidade de consultas e procedimentos $q$ é produzida via:

```math
q = f(L_D, L_A, K),
```

em que $L_D$ é o tempo/esforço de trabalho médico, $L_A$ é a mão de obra de suporte/enfermagem (*auxiliary labor*) e $K$ é o capital físico instalado (consultórios, leitos e equipamentos diagnósticos). Invertendo a função para explicitar a demanda de esforço do médico:

```math
C(q) = C(q; L_A, K), \qquad \text{com } \frac{\partial C}{\partial K} < 0, \quad \frac{\partial C}{\partial L_A} < 0.
```

#### A questão central: quando o efeito de $q$ sobre a utilidade é positivo?

Como a bolsa federal do PMM-E é pré-fixada no edital ($\frac{\partial R}{\partial q} = 0$), o efeito marginal de atender mais pacientes sobre a utilidade do médico é:

```math
\frac{\partial U}{\partial q} = \alpha B'(q) - \frac{\partial C(q; L_A, K)}{\partial q}.
```

O atendimento de pacientes incute **positivamente** na utilidade pelo canal do altruísmo ($\alpha B'(q) > 0$), mas **negativamente** pelo canal da desutilidade de esforço ($- \frac{\partial C}{\partial q} < 0$).

Portanto, o atendimento adicional gera ganho líquido de utilidade ($\frac{\partial U}{\partial q} > 0$) se e somente se:

```math
\alpha B'(q) > \frac{\partial C(q; L_A, K)}{\partial q}.
```

Essa condição estabelece os limiares das variáveis para os quais atender pacientes é gratificante:
1. **Grau de altruísmo ($\alpha$ elevado):** médicos com forte vocação social derivam utilidade moral que supera o cansaço clínico;
2. **Gravidade do paciente / benefício marginal ($B'(q)$ elevado):** em comunidades de alta vulnerabilidade onde a assistência médica é escassa, cada atendimento evita sequelas graves ou mortalidade, maximizando $B'(q)$;
3. **Infraestrutura hospitalar e equipe ($K$ e $L_A$ elevados):** como $\frac{\partial^2 C}{\partial q \partial K} < 0$ e $\frac{\partial^2 C}{\partial q \partial L_A} < 0$, postos bem equipados reduzem o esforço marginal do médico por paciente, viabilizando $\frac{\partial U}{\partial q} > 0$.

Inversamente, em postos precários desprovidos de capital e equipe ($K \to 0$, $L_A \to 0$), o custo marginal de esforço $\frac{\partial C}{\partial q}$ explode, tornando $\frac{\partial U}{\partial q} < 0$ para qualquer $q$, o que resulta em sobrecarga clínica severa e esgotamento profissional (*burnout*).

Isolando a parcela não remuneratória como o custo clínico líquido, $c^{\text{clínico}} = C(q; L_A, K) - \alpha B(q)$:

**Derivadas parciais do custo:**
```math
\frac{\partial c^{\text{clínico}}}{\partial K} = \frac{\partial C}{\partial K} < 0,
\qquad
\frac{\partial c^{\text{clínico}}}{\partial L_A} = \frac{\partial C}{\partial L_A} < 0,
\qquad
\frac{\partial c^{\text{clínico}}}{\partial \alpha} = -B(q) < 0.
```

*Fundamentação na literatura:* Choné e Ma (2011, p. 232, eq. 1; [manuscrito, p. 4](https://people.bu.edu/ma/CHONE-MA_Annals2011.pdf)); Reinhardt (1975). Mais capital ($K$) e mais equipe de enfermagem ($L_A$) reduzem o esforço médico, e maior altruísmo ($\alpha$) valoriza o resultado do paciente, reduzindo o custo subjetivo da prática médica.

---

## 3. Disponibilidade de dados, o IVS do IPEA e o modelo canônico operacional

### Confronto com os dados: quais variáveis realmente observamos?

Na execução concreta da pesquisa empírica do PMM-E, avalia-se a disponibilidade dos dados:
- **Distância da origem do médico ($d_{im}$):** não observada nos editais públicos (exigiria cruzamentos restritos de dados de naturalidade/graduação);
- **Preços municipais de habitação ($Q_m$) e amenidades ($B_m$):** inexiste índice de preços ou de aluguel residencial para os 5.570 municípios do país;
- **Volume e esforço clínico individual ($q$ e $C(q)$):** prontuários e produtividade ambulatorial individualizada por médico no momento da escolha do edital não estão disponíveis.

O que a política pública e as bases administrativas **efetivamente disponibilizam** para todos os municípios é:
1. O valor da **bolsa federal anunciada** por vaga, $B_m(IVS_m)$;
2. O **Índice de Vulnerabilidade Social (IVS 2010 do IPEA)**, running variable canônica da Lei nº 15.233/2025.

### Composição do IVS do IPEA: a justificativa das variáveis

O IVS do IPEA não é um índice arbitrário. Ele é composto por **3 sub-índices de igual peso (1/3 cada) e 16 indicadores censitários** que mapeiam diretamente os canais teóricos deduzidos acima:

1. **Sub-índice de Infraestrutura Urbana (peso 1/3 — 3 indicadores):**
   - % de pessoas em domicílios sem abastecimento de água tratada e esgotamento sanitário adequado;
   - % de pessoas em domicílios sem coleta de lixo regular;
   - % da população que gasta mais de 1 hora no deslocamento residência-trabalho.
   *Conexão teórica:* Mapeia diretamente a ausência de amenidades urbanas ($B_m$ baixo) e custos de transporte/isolamento espacial de Redding e Rossi-Hansberg (2017).

2. **Sub-índice de Capital Humano (peso 1/3 — 7 indicadores):**
   - Taxa de mortalidade infantil (até 1 ano de idade);
   - % de mães adolescentes (10 a 17 anos);
   - % de mães chefes de família sem ensino fundamental completo e com filhos menores de 15 anos;
   - Taxa de analfabetismo da população de 15 anos ou mais;
   - % de crianças em domicílios onde ninguém completou o ensino fundamental;
   - % de crianças de 0 a 5 anos que não frequentam a escola;
   - % de jovens de 15 a 24 anos que não estudam nem trabalham ("nem-nem").
   *Conexão teórica:* A mortalidade infantil e a privação humana refletem carência severa de saúde, gerando elevado retorno marginal ao tratamento ($B'(q)$ alto em Choné e Ma), mas também indicam carência de infraestrutura física ($K$ baixo em Reinhardt).

3. **Sub-índice de Renda e Trabalho (peso 1/3 — 6 indicadores):**
   - Proporção de pessoas com renda domiciliar per capita vulnerável à pobreza extrema ou pobreza;
   - Taxa de desocupação da população de 18 anos ou mais;
   - Taxa de ocupados informais sem ensino fundamental completo;
   - Razão de dependência de renda (idosos e crianças sobre população potencialmente ativa);
   - Taxa de trabalho infantil (10 a 14 anos).
   *Conexão teórica:* Municípios com baixa capacidade contributiva e dependência social dependem exclusivamente da atenção do SUS, exigindo maior esforço assistencial local.

### O modelo canônico operacional

Por estrita parcimônia e aderência aos dados existentes, **adota-se o modelo simples em forma reduzida**:

```math
c_m = c_0(IVS_m).
```

A função de utilidade operacional do médico no PMM-E é expressa como:

```math
V_{im}^{(s)}
=
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{imt}^{(s)}\mid B_m(IVS_m)\right)}{p_{mt}}
- c_0^{(s)}(IVS_m)
\right]
+\varepsilon_{im},
```

com a regra de alocação:

```math
m_i^* \in \arg\max_{m \in \mathcal{M} \cup \{0\}} V_{im}^{(s)}.
```

Os complementos teóricos de Redding & Rossi-Hansberg e Choné & Ma / Reinhardt não prometem regressores que não possuímos; eles atuam como a **fundamentação estrutural de por que e através de quais canais o IVS sintetiza o custo de viver e exercer a medicina no município**.

---

## 4. Referências

- Choné, P.; Ma, C.-T. A. (2011). [*Optimal Health Care Contract under Physician Agency*](https://people.bu.edu/ma/CHONE-MA_Annals2011.pdf). **Annals of Economics and Statistics**, 101/102, 229--256. [p. 232, eq. 1].
- IPEA (2015). [*Atlas da Vulnerabilidade Social nos Municípios Brasileiros*](https://ivs.ipea.gov.br). **Instituto de Pesquisa Econômica Aplicada**, Brasília.
- Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020). [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14, 181--225. [p. 184, eq. 1; manuscrito p. 6].
- Redding, S. J.; Rossi-Hansberg, E. (2017). [*Quantitative Spatial Economics*](https://doi.org/10.1146/annurev-economics-063016-103713). **Annual Review of Economics**, 9, 21--58. [p. 28, eq. 24; manuscrito p. 28].
- Reinhardt, U. E. (1975). *Physician Productivity and the Demand for Health Manpower: An Economic Analysis*. Ballinger Publishing Company. [caps. 3 e 4].


