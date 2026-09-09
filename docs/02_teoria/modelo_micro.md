# Modelo Microeconômico da Escolha Locacional Médica

> **Classificação:** fundamentação teórica canônica — primitivos, derivações, adaptação ao PMM-E e derivação das hipóteses<br>
> **Transposição empírica:** [hipoteses_e_viabilidade_empirica.md](hipoteses_e_viabilidade_empirica.md)<br>
> **Versão apresentada:** [`docs/07_apresentacoes/banca1/02_conteudo_slides.md`](../07_apresentacoes/banca1/02_conteudo_slides.md), slides 12 a 17<br>
> **Atualização:** 9 de setembro de 2026

> [!NOTE]
> Este documento absorveu, em 09/09/2026, o antigo `18_modelo_teorico_slides_apresentacao.md`.
> A adaptação ao PMM-E e as equações originais dos complementos estão na seção 3;
> a derivação das hipóteses, na seção 4. O documento 18 foi removido para não
> manter duas versões concorrentes da mesma teoria.

---

## 1. Modelo principal: escolha locacional em Moehling et al. (2020)

Moehling et al. (2020, eq. 1, p. 184) formulam a distribuição espacial de médicos pela maximização intertemporal dos retornos líquidos esperados entre localidades:

```math
\arg\max_{i \in I}\;U(\omega_i)
=
\arg\max_{i \in I}
\left\{
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{it}^{(s)}\right)}{p_{it}}
- c_{it}^{(s)}
\right]
\right\},
```

em que:
- $i \in I$: localidade de atuação (município ou condado);
- $t$: períodos de tempo futuros e $\delta \in (0,1)$ é o fator subjetivo de desconto intertemporal;
- $s$: grupo de qualificação ou especialidade médica;
- $w_{it}^{(s)}$: rendimento nominal auferido na localidade;
- $p_{it}$: nível de preços local (deflator do custo de vida);
- $c_{it}^{(s)}$: custo locacional líquido não pecuniário.

### Propriedades estruturais do modelo:
- **Horizonte intertemporal ($\sum_t \delta^t$):** Modela escolhas dinâmicas de carreira ao longo de períodos indefinidos, capturando a decisão entre fixar-se no município ou migrar após o término de vínculos temporários.
- **Custo não pecuniário ($c_{it}^{(s)}$):** Na definição original dos autores ([p. 184](https://doi.org/10.1007/s11698-019-00187-w)), inclui *"preferences over rural or urban living, or other location-specific attributes, such as proximity to family"*.
- **Heterogeneidade por especialidade ($s$):** Generalistas praticam em postos simples; especialistas cirúrgicos ou de alta densidade diagnóstica exigem centro cirúrgico e leitos de UTI, sofrendo severa desutilidade em postos precários e abrindo mão de altos rendimentos privados em grandes centros.

---

## 2. Microfundamentação dos componentes de custo

### 2.1. Custo geográfico: distância e amenidades

O custo de vida entra diretamente no deflator $p_{it}$. O custo geográfico não pecuniário é expresso por:

```math
c^{\text{geo}}_{im} = \phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}},
```

em que:
- $\text{dist}_{im} = d(\text{família}_i, m)$: distância física à cidade onde os familiares de fato residem (não onde o médico cursou a formação);
- $A_m$: amenidades urbanas locais (qualidade urbana, saneamento e segurança);
- $\theta_i^{\text{rural}}$: gosto pessoal por ambiente rural vs. urbano (sem derivada monotônica universal).

**Derivadas parciais:**
```math
\frac{\partial c^{\text{geo}}}{\partial \text{dist}_{im}} = \phi' > 0,
\qquad
\frac{\partial c^{\text{geo}}}{\partial A_m} = -\gamma < 0.
```

*Fundamentação:* Moehling et al. (2020, p. 184) e Redding & Rossi-Hansberg (2017, p. 28, eq. 24). Afastar-se da família impõe custos logísticos e afetivos crescentes ($\phi' > 0$); amenidades urbanas superiores tornam o município mais atraente ($-\gamma < 0$).
*(Limitação de commuting:* Os dados do CNES/edital não informam a residência do profissional por sigilo fiscal, fixando o município do estabelecimento como unidade de análise).*

---

### 2.2. Custo laboral: cansaço, satisfação e volume de atendimentos ($q$)

Com base em Choné e Ma (2011, p. 232, eq. 1), a desutilidade clínica líquida de atender $q$ pacientes é expressa pelo custo laboral não pecuniário líquido:

```math
c^{\text{laboral}}(q) = C(q) - \alpha B(q),
```

em que:
- $C(q)$: **cansaço e exaustão física/mental** ($C' > 0$, com $C'' > 0$ por desgaste biológico e cognitivo crescente);
- $B(q)$: **benefício efetivo de saúde gerado** ($B' > 0$, com $B'' < 0$ pela priorização de casos mais urgentes na triagem);
- $\alpha \ge 0$: **satisfação moral e sensação de dever cumprido** (satisfação intrínseca pela melhora do paciente).

#### Trade-off de $q$ e convexidade estrita:
O custo marginal $c'(q) = C'(q) - \alpha B'(q)$ tem sinal incerto *a priori*, mas a derivada segunda é inequivocamente positiva:

```math
c''(q) = C''(q) - \alpha B''(q) \gg 0.
```

Essa convexidade garante uma curva de custo não pecuniário em **formato de U**, com ponto de satisfação líquida máxima em $q_{c_{\max}}$ ($C'(q_{c_{\max}}) = \alpha B'(q_{c_{\max}})$) e cruzamento de custo neutro em $q_{c=0}$ ($C(q_{c=0}) = \alpha B(q_{c=0})$):

![Curva de Custo Laboral Líquido](figuras/curva_custo_laboral_burnout.png)

1. **Zona 1: Utilidade Laboral Crescente ($q < q_{c_{\max}}$):** A satisfação marginal supera o cansaço marginal ($\alpha B' > C' \implies c'(q) < 0$). Atender pacientes adicionais reduz o custo laboral líquido, gerando utilidade líquida crescente.
2. **Ponto Ótimo ($q = q_{c_{\max}}$):** O cansaço marginal equilibra exatamente a satisfação adicional ($c'(q_{c_{\max}}) = 0 \iff C' = \alpha B'$), atingindo a **satisfação líquida máxima** (ponto de custo laboral mínimo).
3. **Zona 2: Utilidade Laboral Decrescente ($q_{c_{\max}} < q < q_{c=0}$):** O cansaço marginal passa a superar a satisfação marginal ($c'(q) > 0 \implies C' > \alpha B'$), tornando a utilidade marginal decrescente. No entanto, o custo acumulado ainda é negativo ($c < 0$), significando que a satisfação total acumulada ainda excede o cansaço ($\alpha B > C$).
4. **Ponto Notável de Custo Neutro ($q = q_{c=0}$):** O cansaço total acumulado iguala a satisfação total ($C = \alpha B \iff c = 0$).
5. **Zona 3: Cansaço Supera a Satisfação ($q > q_{c=0}$):** O custo laboral líquido torna-se estritamente positivo ($c > 0 \iff C > \alpha B$), impondo desutilidade líquida pela sobrecarga e exaustão clínica.

---

### 2.3. Infraestrutura, insumos e pessoal de saúde ($L$ e $K$)

A infraestrutura hospitalar instalada ($K$) e a equipe de apoio/enfermagem ($L$) exercem um **efeito duplo**. O primeiro canal está em Choné e Ma (2011), que já escrevem o custo de atender como $C(q; L, K)$. O segundo é **extensão deste projeto**, motivada pela função de produção médica de Reinhardt (1972, 1975), na qual o produto do consultório depende de insumos não médicos: escrevemos o benefício como $B(q; L, K)$, e não $B(q)$.
1. **Reduzem o cansaço:** $\frac{\partial C}{\partial K} < 0$ e $\frac{\partial C}{\partial L} < 0$ (apoio técnico e retaguarda para segunda opinião diminuem a penosidade do trabalho).
2. **Multiplicam o benefício de saúde:** $\frac{\partial B}{\partial K} > 0$ e $\frac{\partial B}{\partial L} > 0$. A falta de medicamentos essenciais, insumos cirúrgicos ou maquinário quebrado esvaziam a resolutividade curativa do atendimento.

**Derivadas parciais totais:**
```math
\frac{\partial c^{\text{laboral}}}{\partial K} = \frac{\partial C}{\partial K} - \alpha \frac{\partial B}{\partial K} < 0,
\qquad
\frac{\partial c^{\text{laboral}}}{\partial L} = \frac{\partial C}{\partial L} - \alpha \frac{\partial B}{\partial L} < 0.
```

---

### 2.4. O modelo teórico integrado completo

Consolidando os blocos desenvolvidos, a decisão locacional intertemporal do médico especialista $s$ é expressa em harmonia direta com a formulação de Moehling et al. (2020):

```math
\arg\max_{m \in M}\;U_i(\omega_m)
=
\arg\max_{m \in M}
\left\{
\sum_t \delta^t
\left[
\frac{\mathbb{E}\!\left(w_{mt}^{(s)}\right)}{p_{mt}}
- c_{im}^{(s)}
\right]
\right\},
```

em que o custo locacional não pecuniário $c_{im}^{(s)}$ é formalmente aberto em seus componentes microfundamentados:

```math
c_{im}^{(s)} = \underbrace{\phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}}_{\text{Custo Geográfico e Amenidades}} + \underbrace{C(q_{im}; L_m, K_m, s) - \alpha_i B(q_{im}; L_m, K_m)}_{\text{Custo Laboral Líquido de Realização}}.
```

---

## 3. Adaptação ao PMM-E: a bolsa fixada por regra

O programa introduz no modelo um elemento que a literatura de escolha locacional
raramente observa: **um componente da remuneração fixado por regra pública e
descontínuo em um escore territorial**. A bolsa-formação $B_m$ não é negociada
com o médico nem determinada pelo mercado local; é atribuída ao município por
faixa de vulnerabilidade.

Escrevendo a decisão do médico $i$ sobre o município $m$, com a alternativa
$m=0$ representando ficar fora do programa:

```math
V_{im}^{(s)}
=
\sum_t\delta^t
\left[
\frac{\mathbb{E}\!\left(w_{imt}^{(s)}\mid B_m(IVS_m)\right)}{p_{mt}}
- c_{im}^{(s)}
\right]
+\varepsilon_{im},
\qquad
m_i^{\ast} \in \arg\max_{m \in \mathcal{M} \cup \{0\}} V_{im}^{(s)}.
```

Duas restrições de observabilidade obrigam a uma forma reduzida. Não se observa
distância à cidade da família, preço local de aluguel nem esforço clínico
individual $q$. Observa-se, para 100% dos municípios, a bolsa $B_m$ e o IVS 2010
do IPEA. O custo locacional é então escrito como função do escore territorial
mais um desvio individual:

```math
c_{im}^{(s)} = c_0^{(s)}(IVS_m) + \eta_i .
```

### 3.1 Por que o IVS é a variável que organiza o custo latente

O IVS do IPEA agrega 16 indicadores censitários em três sub-índices, e cada um
deles corresponde a um bloco distinto do custo microfundamentado na seção 2:

| Sub-índice do IVS | Indicadores | Bloco teórico correspondente | Efeito esperado sobre $c$ |
|---|---|---|:---:|
| Infraestrutura urbana | saneamento, coleta de lixo, tempo de deslocamento | amenidades $A_m$ e custo espacial (Redding & Rossi-Hansberg) | $\uparrow$ |
| Capital humano | mortalidade infantil, mães adolescentes, analfabetismo | gravidade do caso $B'(q)$ e escassez de capital $K$ (Choné & Ma; Reinhardt) | ambíguo |
| Renda e trabalho | extrema pobreza, desemprego, informalidade | ausência de mercado privado pagador, logo $w \to B$ | $\uparrow$ |

O sub-índice de capital humano é o que impede assumir monotonicidade: carência
sanitária eleva o benefício marginal de atender ($B'(q)\uparrow$, o que **reduz**
o custo laboral líquido de um médico altruísta) ao mesmo tempo em que sinaliza
falta de insumos ($K\downarrow$, o que **eleva** o cansaço). Portanto

```math
c_0'(IVS) \; \gtrless \; 0 ,
```

e o sinal é questão empírica, não postulado. Essa é a razão teórica para
estudar o **degrau** da bolsa na fronteira de faixa, e não o gradiente do IVS.

### 3.2 Equações originais dos complementos

Redding e Rossi-Hansberg (2017, eq. 24, p. 28), de onde vem o componente
espacial do custo:

```math
u_{nio} = \frac{z_{nio}B_n w_i}{\kappa_{ni}Q_n^{\,1-\beta}}
\implies
c^{\text{espacial}}_m = (1-\beta)\ln Q_m - \ln A_m .
```

Choné e Ma (2011, eq. 1, p. 232), com Reinhardt (1975), de onde vem o
componente clínico:

```math
U = R - C(q; L, K) + \alpha B(q)
\implies
c^{\text{laboral}}_{im} = C(q; L, K) - \alpha B(q).
```

---

## 4. Da condição de aceitação às hipóteses

O modelo só é útil ao trabalho empírico se produzir hipóteses por derivação, e
não por analogia. Esta seção faz essa passagem.

### 4.1 Condição de aceitação

O médico aceita a vaga no município $m$ quando o valor da vaga supera sua
melhor alternativa. Normalizando a alternativa em $\bar{v}_i$ e usando a forma
reduzida da seção 3:

```math
\frac{B_m}{p_m} - c_0(IVS_m) \;\geq\; \bar{v}_i .
```

Comparando dois municípios contíguos separados pela fronteira administrativa
entre faixas de bolsa, o preenchimento do lado mais vulnerável exige que o
degrau monetário supere o degrau de custo latente:

```math
\boxed{\;\frac{\Delta B_m}{p_m} \;>\; \Delta c_0\;}
\qquad\text{com}\qquad
\Delta B_m = \text{R\$ }5.000 .
```

Essa desigualdade é o objeto do trabalho. Ela não pergunta se o PMM-E funciona;
pergunta se **o preço que o programa colocou sobre a vulnerabilidade é
suficiente** para vencer a desvantagem que ele pretende compensar.

### 4.2 Estática comparativa e hipóteses derivadas

| # | Derivada | Origem no modelo | Hipótese |
|:---:|---|---|---|
| **H1** | $\dfrac{\partial \Pr(\text{aceitar})}{\partial B_m} > 0$ | $B_m$ entra aditivamente na remuneração real esperada | quanto maior a bolsa, maior a probabilidade de preenchimento |
| **H2** | $\dfrac{\partial \Pr(\text{permanecer em } t{+}k)}{\partial B_m} > 0$ | a bolsa entra em **todo** período do somatório $\sum_t\delta^t$, não apenas no primeiro | quanto maior a bolsa, maior a persistência da oferta local após o período inicial |
| **H3** | $\dfrac{\partial^2 \Pr(\text{aceitar})}{\partial B_m \, \partial w^{\text{alt}}} < 0$ | a bolsa concorre com a renda alternativa dentro do mesmo termo $\mathbb{E}(w\mid B)$ | o efeito da bolsa é maior onde e para quem a renda alternativa é menor |
| **H4** | $\text{sinal}\left(c_0'(IVS)\right)$ indefinido | sub-índices do IVS operam em sentidos opostos (seção 3.1) | decompondo o IVS, infraestrutura urbana eleva o custo e capital humano pode atenuá-lo |

H2 merece nota: ela não é uma hipótese sobre retenção individual. O modelo
prevê persistência da **decisão locacional**, e o dado disponível observa
oferta cadastrada no município, não o mesmo profissional na mesma vaga. A
distinção é mantida em toda a transposição empírica.

H3 tem duas leituras, ambas derivadas da mesma cruzada. A leitura individual
compara médicos por renda alternativa e exige microdado de renda. A leitura
territorial compara municípios pela existência de mercado privado local: onde
não há demanda privada adjacente, a remuneração colapsa no piso da bolsa,
$w = B$, e a bolsa é a totalidade do incentivo.

A transposição dessas hipóteses para especificações, variáveis e bases está em
[hipoteses_e_viabilidade_empirica.md](hipoteses_e_viabilidade_empirica.md).

---

## 5. Referências teóricas

- Choné, P.; Ma, C.-T. A. (2011). [*Optimal Health Care Contract under Physician Agency*](https://people.bu.edu/ma/CHONE-MA_Annals2011.pdf). **Annals of Economics and Statistics**, 101/102, 229--256. [p. 232, eq. 1].
- Moehling, C. M.; Niemesh, G. T.; Thomasson, M. A.; Treber, J. (2020). [*Medical Education Reforms and the Origins of the Rural Physician Shortage*](https://doi.org/10.1007/s11698-019-00187-w). **Cliometrica**, 14, 181--225. [p. 184, eq. 1].
- Redding, S. J.; Rossi-Hansberg, E. (2017). [*Quantitative Spatial Economics*](https://doi.org/10.1146/annurev-economics-063016-103713). **Annual Review of Economics**, 9, 21--58. [p. 28, eq. 24].
- Reinhardt, U. E. (1972). [*A Production Function for Physician Services*](https://doi.org/10.2307/1927495). **The Review of Economics and Statistics**, 54(1), 55--66. [forma geral $Q = f(H, X_1, \ldots, X_n)$].
- Reinhardt, U. E. (1975). *Physician Productivity and the Demand for Health Manpower: An Economic Analysis*. Ballinger Publishing Company. [caps. 3 e 4]. Referência secundária: a especificação estimada não está transcrita neste repositório.
