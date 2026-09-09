# Hipóteses e Viabilidade Empírica: Transposição do Modelo Teórico

> **Classificação:** transposição empírica do modelo — especificação candidata, mapeamento de variáveis e hipóteses operacionais<br>
> **Derivação das hipóteses:** [modelo_micro.md](modelo_micro.md), seção 4<br>
> **Versão apresentada:** [`docs/07_apresentacoes/banca1/02_conteudo_slides.md`](../07_apresentacoes/banca1/02_conteudo_slides.md), slide 12<br>
> **Atualização:** 9 de setembro de 2026

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

### Decomposição do IVS e consequência econométrica

A correspondência entre os três sub-índices do IVS e os blocos do custo
teórico está em [modelo_micro.md](modelo_micro.md), seção 3.1, e não é repetida
aqui. O que interessa a este documento é a consequência para a estimação.

O repositório armazena os três sub-índices separadamente
(`ivs_infra_2010`, `ivs_ch_2010`, `ivs_rt_2010`), o que permite decompor a
*running variable*. Como as dimensões operam em sentidos divergentes,
**não se pode assumir $c_0'(IVS) > 0$ a priori**. Três implicações práticas:

1. um coeficiente global do IVS próximo de zero é compatível com dois efeitos
   grandes que se cancelam, e não deve ser lido como ausência de gradiente;
2. a decomposição em sub-índices é diagnóstico, não busca de especificação —
   deve ser declarada antes de observar outcomes;
3. o argumento de identificação repousa sobre o **degrau** da bolsa na fronteira
   de faixa, precisamente porque o gradiente é de sinal ambíguo.

## 4. Hipóteses operacionais

As quatro hipóteses abaixo **não são postuladas aqui**: são a leitura empírica
das derivadas obtidas em [modelo_micro.md](modelo_micro.md), seção 4.2. Esta
seção apenas diz, para cada uma, o que seria observado nos dados do projeto.

| # | Hipótese derivada | Forma testável com as bases do projeto | Margem |
|:---:|---|---|---|
| **H1** | Compensação financeira: $\partial\Pr(\text{aceitar})/\partial B_m > 0$ | salto no preenchimento administrativo da célula CNES–curso na fronteira de faixa. Vacância persistente na Faixa 1 indica $\Delta c_0 > \Delta B/p$ | entrar |
| **H2** | Persistência: $\partial\Pr(\text{permanecer})/\partial B_m > 0$ | salto no estoque e na cobertura municipal do CBO em horizonte fixo de 6 e 12 meses, com data-base explícita | ficar |
| **H3** | Renda alternativa: $\partial^2\Pr/\partial B_m\partial w^{\text{alt}} < 0$ | **leitura territorial** — interação entre faixa e ausência de mercado privado local, onde $w = B$; **leitura individual** — exigiria microdado de renda que o projeto não possui | heterogeneidade |
| **H4** | Decomposição do IVS: sinal de $c_0'(IVS)$ indefinido | infraestrutura urbana com efeito negativo sobre fixação e capital humano com efeito atenuado ou positivo, em modelos com sub-índices desagregados | diagnóstico |

### 4.1 Hipótese complementar de heterogeneidade tecnológica

Especialidades cirúrgicas dependem de capital hospitalar instalado ($K$).
Espera-se, portanto, gradiente mais adverso para cirurgiões do que para
clínicos:

```math
\left.\frac{\partial \Pr}{\partial IVS}\right|_{\text{cirúrgico}}
\;\ll\;
\left.\frac{\partial \Pr}{\partial IVS}\right|_{\text{clínico}} .
```

Ela decorre da mesma estática comparativa, pela via de $\partial c/\partial K < 0$,
e é tratada como heterogeneidade pré-declarada, não como hipótese principal.

### 4.2 Correspondência com as hipóteses apresentadas na banca 1

A banca 1 trata apenas da margem **preenchimento** e leva duas hipóteses, as
derivadas diretas da condição de aceitação:

| Banca 1 | Enunciado | Documento canônico |
|---|---|---|
| H1 | maior remuneração real aumenta a probabilidade de preenchimento — $\partial\Pr/\partial(B_m/p_m) > 0$ | H1 |
| H2 | maior custo locacional reduz a probabilidade de preenchimento — $\partial\Pr/\partial c_m < 0$ | operacionaliza-se por H3 (mercado privado), H4 (sub-índices do IVS) e 4.1 (infraestrutura), todas leituras do mesmo $c_m$ |
| — | persistência da oferta | H2 canônica; fora da banca 1, permanece no escopo do projeto |

A apresentação declara, no mesmo slide, como cada objeto aparece nos dados: o
preenchimento por célula CNES–curso; a bolsa como faixa anunciada, colinear
com a categoria de IVS por construção da regra; o custo como IVS, sub-índices,
tipologia territorial e estoque prévio. E declara o limite: separar H1 de H2
exige a fronteira entre faixas com o escore administrativo, que não está
recuperado — até lá, o que se estima é gradiente.

### 4.3 Linguagem permitida

Nenhuma dessas hipóteses autoriza linguagem causal por si só. O salto na
fronteira só recebe interpretação causal se a regra de atribuição, o suporte e
as demais condições do desenho passarem pelos portões registrados em
[`docs/06_execucao/05_roadmap_execucao.md`](../06_execucao/05_roadmap_execucao.md).
Enquanto isso, "gradiente", "associação" e "preenchimento administrativo" são os
termos corretos.

---

## 5. Referências

- Costa, F.; Nunes, J.; Sanches, F. (2024). *Physician Allocation and Health Care Delivery: Evidence from Brazil*. Working Paper.
- IPEA (2015). [*Atlas da Vulnerabilidade Social nos Municípios Brasileiros*](https://ivs.ipea.gov.br). **IPEA**, Brasília.
- Sivey, P.; Scott, A.; Witt, J.; Joyce, C.; Humphreys, J. (2012). [*Junior Doctors' Preferences for Specialty and Location: A Discrete Choice Experiment*](https://doi.org/10.1016/j.jhealeco.2012.06.002). **Journal of Health Economics**, 31(6), 813--823.
