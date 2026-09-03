# Hipóteses e Viabilidade Empírica: Transposição do Modelo Teórico

> **Classificação:** sketch da seção empírica e hipóteses econômicas de trabalho<br>
> **Fundamentação microeconômica:** ver [modelo_micro.md](modelo_micro.md)<br>
> **Atualização:** 3 de setembro de 2026

> *[Nota metodológica: Este documento funciona como um esboço preliminar (sketch) de transposição empírica para guiar a econometria aplicada do projeto. Como a estratégia final de identificação causal, o poder estatístico dos estimandos e a disponibilidade de microdados estão sendo investigados e refinados na execução empírica (ver `docs/06_execucao/` e `docs/auditorias/`), as formulações operacionais e as hipóteses abaixo são tratadas como uma agenda de trabalho em aberto, e não como escolhas axiomáticas congeladas.]*

---

## 1. Proposta preliminar de especificação operacional

Para conectar a utilidade teórica aos microdados disponíveis no repositório sem recorrer a regressores não observados, o custo locacional $c$ deixa de ser uma caixa-preta e pode ser parametrizado a partir das variáveis territoriais, estruturais e tecnológicas disponíveis:

```math
V_{ims} = \alpha + \beta_B B_m(IVS_m) - c_{ms} + \varepsilon_{ims},
```

com uma formulação candidata para o custo operacional:

```math
c_{ms} = \theta_0 IVS_m + \sum_{k \ne \text{remoto}} \beta_k \mathbf{1}\{\text{Estrato}_m = k\} + \beta_L \text{EstoqueMédico}_m + \beta_P \ln(\text{Pop}_m) + \gamma_s + \mu_{\text{uf}}.
```

Nessa formulação exploratória:
1. $B_m(IVS_m)$: bolsa federal anunciada no edital (Faixas de R$ 10k, R$ 15k e R$ 20k), atrelada ao IVS 2010 (*running variable* institucional da Lei nº 15.233/2025);
2. $\text{Estrato}_m$: tipologia territorial congelada (REGIC 2018 + RM/RIDE 2022 strict), que categoriza o município em *Capital*, *Metropolitano*, *Interior Polo* ou *Interior Remoto* (referência);
3. $\text{EstoqueMédico}_m$: médicos especialistas por 10 mil habitantes nos 12 meses anteriores (CNES), mensurando a retaguarda de suporte profissional ($L$ de Reinhardt) para atenuar o cansaço clínico ($C$);
4. $\ln(\text{Pop}_m)$: população censitária municipal (Censo IBGE), controlando pela escala de demanda e densidade de serviços urbanos;
5. $\gamma_s$: efeitos fixos de especialidade/curso (16 qualificações no edital), absorvendo as diferenças tecnológicas entre especialidades clínicas e cirúrgicas ($s$ de Moehling);
6. $\mu_{\text{uf}}$: efeitos fixos de UF, que absorvem os diferenciais estaduais de custo de vida ($p_m$) e regulações regionais de saúde.

---

## 2. O mecanismo salarial e o risco de subalocação ($w \mid B \ge B$)

A teoria microeconômica sugere que a atratividade do município depende criticamente da interação entre o valor da bolsa e as oportunidades do mercado privado local:
- **Capitais e polos metropolitanos:** O médico cumpre as 20h da bolsa e complementa sua renda no setor privado local ou regional ($w = B + w^{\text{priv}} > B$).
- **Interior isolado:** Não há demanda privada adjacente; o médico fica subalocado nas 20h e sua remuneração nominal colapsa no piso da bolsa ($w = B$).

Essa hipótese ajuda a explicar por que bolsas nominais maiores no interior vulnerável ($B_{\text{interior}} = \text{R\$} 20\text{k} > B_{\text{capital}} = \text{R\$} 10\text{k}$) podem resultar em uma remuneração real total substancialmente inferior ($w_{\text{interior}} < w_{\text{capital}}$).

---

## 3. Mapeamento de variáveis no repositório e forças opostas do IVS

A tabela abaixo sintetiza como os primitivos teóricos do [modelo microeconômico](modelo_micro.md) são empiricamente mapeados nas bases de dados consolidadas do projeto:

| Dimensão Teórica | Variável Operacional Candidata | Fonte no Repositório | Mecanismo Econômico a Investigar |
|:---|:---|:---|:---|
| **Vulnerabilidade Geral** | `IVS 2010` (IPEA) | Censo Demográfico | Regra da bolsa; sintetiza desamenidade física vs. urgência sanitária. |
| **Isolamento e Mercado Privado** | `estrato` (4 níveis) | REGIC 2018 + RM/RIDE 2022 | Proxy de custos de deslocamento e acesso ao mercado privado ($w^{\text{priv}}$). |
| **Suporte de Equipe ($L$)** | `estoque_pre_por_10k` | CNES (12 meses prévios) | Retaguarda médica que reduz o cansaço clínico ($C(q)$). |
| **Infraestrutura Hospitalar ($K$)** | `leitos_exist` e `equipamentos` | CNES físico | Reduz o esforço e viabiliza a resolutividade do cuidado ($B(q)$). |
| **Escala e Densidade** | `log_pop` e `rdpc_2010` | Censo 2010 | Tamanho de mercado e amenidades urbanas mínimas. |
| **Tecnologia Médica ($s$)** | `cod_curso` (16 FEs) | Edital PMM-E | Diferencia prática clínica leve de cirúrgica pesada. |
| **Custo de Vida Regional ($p_m$)** | `sg_uf` (Efeitos Fixos) | IBGE | Absorve o nível de preços estadual e especificidades regionais. |

### A decomposição do IVS e o risco econométrico de forças opostas:
O repositório armazena os **3 sub-índices do IVS** (`ivs_infra_2010`, `ivs_ch_2010`, `ivs_rt_2010`), permitindo decompor a *running variable*:
1. **Infraestrutura Urbana:** Desamenidade física pura (esgoto, lixo, transporte $> 1$h), elevando o custo locacional ($c \uparrow$).
2. **Capital Humano:** Urgência social e gravidade sanitária (mortalidade infantil, vulnerabilidade), ativando a vocação do médico altruísta ($B'(q) \uparrow \implies c \downarrow$), embora sinalize escassez de insumos ($K \downarrow \implies C \uparrow$).
3. **Renda e Trabalho:** Pobreza extrema, eliminando o mercado privado pagador ($w = B$).

> **Implicação econométrica:** Como as dimensões do IVS operam em sentidos divergentes, **não se pode assumir monotonicidade de que $c_0'(IVS) > 0$ a priori**. Avaliar se esses efeitos se anulam no IVS global é uma das investigações centrais da econometria empírica.

---

## 4. Hipóteses preliminares a serem investigadas

A partir da transposição teórica, quatro hipóteses preliminares orientam a agenda econométrica:

1. **Hipótese 1 (Compensação Financeira da Bolsa):** O preenchimento de vagas na descontinuidade requer que o salto financeiro supere o salto no custo latente: $\frac{\Delta B_m}{p_m} > \Delta c_0$. Vacância persistente na Faixa 1 (R$ 20k) indica que o custo territorial latente excede o diferencial de R$ 5k da política.
2. **Hipótese 2 (Penalidade da Subalocação no Interior):** Controlando pela bolsa e pelo IVS, municípios isolados (onde $w = B$) terão menor taxa de ocupação e menor persistência no CNES aos 6 e 12 meses do que polos metropolitanos com mercado privado ($w > B$).
3. **Hipótese 3 (Heterogeneidade Clínico vs. Cirúrgico):** Especialidades cirúrgicas dependem de capital hospitalar instalado ($K$). A taxa de vacância no alto IVS tende a ser maior para cirurgiões do que para clínicos: $\left.\frac{\partial \Pr}{\partial IVS}\right|_{\text{cirúrgico}} \ll \left.\frac{\partial \Pr}{\partial IVS}\right|_{\text{clínico}}$.
4. **Hipótese 4 (Decomposição do IVS: Desamenidade vs. Urgência Social):** Em modelos com sub-índices desagregados, a Infraestrutura Urbana deve exercer efeito negativo sobre a fixação médica ($c \uparrow$), enquanto o Capital Humano pode apresentar efeito atenuado ou positivo ($B' \uparrow$).

---

## 5. Referências

- Costa, F.; Nunes, J.; Sanches, F. (2024). *Physician Allocation and Health Care Delivery: Evidence from Brazil*. Working Paper.
- IPEA (2015). [*Atlas da Vulnerabilidade Social nos Municípios Brasileiros*](https://ivs.ipea.gov.br). **IPEA**, Brasília.
- Sivey, P.; Scott, A.; Witt, J.; Joyce, C.; Humphreys, J. (2012). [*Junior Doctors' Preferences for Specialty and Location: A Discrete Choice Experiment*](https://doi.org/10.1016/j.jhealeco.2012.06.002). **Journal of Health Economics**, 31(6), 813--823.
