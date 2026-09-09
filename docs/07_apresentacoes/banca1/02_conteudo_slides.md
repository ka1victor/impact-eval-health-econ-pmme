# 02. Conteúdo dos slides — banca 1

> **Classificação:** fonte de verdade do deck. O arquivo `.tex` ou `.pptx` é derivado deste documento.<br>
> **Regras de composição:** [01_roteiro_narrativo.md](01_roteiro_narrativo.md)<br>
> **Proveniência de cada número:** [03_proveniencia_figuras_e_numeros.md](03_proveniencia_figuras_e_numeros.md)<br>
> **Atualização:** 9 de setembro de 2026

---

## Convenções deste documento

- **Título** é o takeaway exibido no slide, em frase completa. Nunca contém o nome do bloco.
- **Tracking** é o rótulo de seção exibido fora do título, em faixa própria.
- **Corpo** é o texto que vai ao slide, já enxugado. Frase longa aqui é frase longa no slide.
- **Visual** identifica a figura pelo código de proveniência (`F1`…`F6`).
- **Nota** não vai ao slide: é fala do apresentador e defesa antecipada de arguição.

---

## Slide 1 — Capa

- **Tracking:** ausente.
- **Título:** Bolsa maior compensa município pior?
- **Subtítulo:** Um modelo de escolha locacional para o preenchimento e a permanência de vagas no Mais Médicos Especialistas
- **Rodapé:** autoria, instituição, data da banca.
- **Nota:** o título antigo — *"Bolsa-formação como diferencial compensatório: um modelo de escolha racional…"* — nomeava o mecanismo antes de a banca saber qual é o problema. A capa passa a fazer a pergunta; o mecanismo aparece no bloco teórico.

---

## Slide 2 — Roteiro

- **Tracking:** ausente.
- **Título:** O argumento em seis passos
- **Corpo:**

  | | Bloco | Em uma linha |
  |---|---|---|
  | 1 | Motivação | há uma dor territorial, há uma política e o efeito dela está em aberto |
  | 2 | Pergunta | bolsa maior compensa município pior? |
  | 3 | Literatura | o arcabouço existe; o preço fixado por regra ainda não foi testado |
  | 4 | Modelo | o médico aceita quando o ganho supera o custo de estar ali |
  | 5 | Hipóteses | entrar, ficar, e para quem o incentivo pesa mais |
  | 6 | Viabilidade | onde estão os dados e o que ainda falta |

- **Nota:** este slide também estabelece o contrato de escopo — a apresentação termina na viabilidade, sem resultados.

---

# Bloco I — Motivação

## Slide 3 — (i) A dor, como ela já é reconhecida

- **Tracking:** `Motivação · 1 de 4`
- **Título:** A escassez de especialistas já é tratada como urgência sanitária pelo próprio governo
- **Visual:** `F1` — três recortes de imprensa e comunicação oficial.
- **Corpo:**
  - Ministério da Saúde decreta **situação de urgência em saúde pública por dois anos** para reduzir tempo de espera por consultas, exames e cirurgias (07/05/2025).
  - Dados do Ministério da Saúde citados no Senado: **apenas 10% dos especialistas atendem no SUS**, concentrados em capitais e regiões mais ricas (25/09/2025).
  - A permanência dos especialistas do programa é **prorrogada até fevereiro de 2027**; 52% atuam no interior (26/08/2026).
- **Fonte:** Correio do Povo (07/05/2025); Senado Notícias (25/09/2025); gov.br — Agora Tem Especialistas (26/08/2026).
- **Nota:** o slide estabelece que o problema é reconhecido pelo formulador, não apenas pela literatura. A prorrogação de agosto de 2026 é dado relevante para o desenho: o ciclo 1 ainda estava em curso quando a política foi estendida, o que afeta o horizonte de permanência observável.

## Slide 4 — (i) A dor, medida

- **Tracking:** `Motivação · 2 de 4`
- **Título:** Onde há menos especialista, o paciente percorre mais quilômetros
- **Visual:** `F2` (esquerda) — especialistas por 100 mil habitantes, por UF, 2024; `F3` (direita) — deslocamento médio da população para serviços de alta complexidade, por região, em km.
- **Corpo:**
  - Densidade de especialistas: **453,5 por 100 mil habitantes no DF** contra **68,2 no Maranhão** — razão de **6,6 vezes**.
  - Deslocamento médio até alta complexidade: **276 km no Norte** e **256 km no Centro-Oeste**, contra **101 km no Sul**.
  - As duas medidas descrevem a mesma falha: a oferta é nacional no agregado e ausente no território.
- **Fonte:** Scheffer, M. (coord.), *Demografia Médica no Brasil 2025*; IBGE, *Regiões de Influência das Cidades — REGIC 2018*.
- **Nota:** dois gráficos no mesmo slide porque sustentam **uma** afirmação. Se a banca perguntar por que não usar leitos ou produção: ambas as medidas são pré-programa e independentes do desfecho que se pretende estudar.

## Slide 5 — (ii) A política

- **Tracking:** `Motivação · 3 de 4`
- **Título:** O programa responde com um preço explícito pela vulnerabilidade do município
- **Visual:** `F4` — valor mensal da bolsa-formação por faixa de atração.
- **Corpo:**
  - O Mais Médicos Especialistas (Lei nº 15.233/2025) oferece **bolsa-formação mensal** por vaga de especialista, com carga de 20 horas semanais em estabelecimento do SUS.
  - O valor **não é uniforme**: é fixado por faixa de atração, definida pela vulnerabilidade do município.

    | Faixa | Vulnerabilidade declarada | Bolsa mensal |
    |---|---|---:|
    | Faixa 1 | muito alta | R$ 20.000 |
    | Faixa 2 | alta | R$ 15.000 |
    | Faixa 3 | média, baixa ou muito baixa | R$ 10.000 |

  - A Faixa 1 paga **o dobro** da Faixa 3. Entre faixas contíguas, o degrau é de **R$ 5.000**.
- **Fonte:** Lei nº 15.233/2025 e edital do PMM-E; faixas registradas em [`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md).
- **Nota:** este é o slide que torna o trabalho possível. A política não apenas aloca médicos: ela **coloca um preço em reais sobre a vulnerabilidade territorial**, e o faz por regra publicada. O degrau de R$ 5.000 é o objeto de interesse — não a participação no programa.

## Slide 6 — (iii) Os efeitos, até onde se pode afirmar

- **Tracking:** `Motivação · 4 de 4`
- **Título:** As vagas foram de fato para as regiões desassistidas — o que não diz que foram preenchidas nem mantidas
- **Visual:** `F5` — participação regional: especialistas existentes (2024) versus profissionais do PMM-E ativos (ciclo 1).
- **Corpo:**
  - O Nordeste concentra **14,5%** dos especialistas do país e **60,3%** dos profissionais ativos no ciclo 1 do programa.
  - O Sudeste faz o caminho inverso: **55,3%** do estoque nacional e parcela minoritária do programa.
  - A alocação, portanto, foi redistributiva. Três coisas que este gráfico **não** mostra:
    1. se as vagas ofertadas foram preenchidas — o gráfico conta quem está ativo, não a razão sobre vagas;
    2. se quem entrou permaneceu;
    3. se a bolsa maior é a causa da alocação, ou se ela apenas acompanha onde o programa decidiu ofertar.
- **Fonte:** `data/pmm_especialistas_nominal.csv` (ciclo 1, referência 12/08/2026); Scheffer, M. (coord.), *Demografia Médica no Brasil 2025*. **Ver pendência `P1`.**
- **Nota:** o terceiro item é a transição para a pergunta. Este é o slide onde a linguagem precisa ser mais disciplinada: descrição de alocação administrativa, nunca efeito.

---

# Bloco II — Pergunta

## Slide 7 — A pergunta

- **Tracking:** `Pergunta`
- **Título:** Bolsa maior compensa município pior?
- **Corpo:**
  - Em uma linha: **um degrau de R$ 5.000 na bolsa é suficiente para vencer a desvantagem territorial de um município mais vulnerável?**
  - Ela se decompõe em duas margens observáveis:

    | | Margem | Pergunta operacional |
    |---|---|---|
    | a | **Entrar** | a vaga com bolsa maior é preenchida? |
    | b | **Ficar** | a oferta médica local persiste depois da entrada? |

  - **O que a pergunta não é:**
    - não é o efeito de participar do PMM-E;
    - não é o efeito total do programa Agora Tem Especialistas;
    - não é o efeito causal do IVS — vulnerabilidade não é tratamento manipulável.
- **Fonte:** [`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), seção 1.
- **Nota:** o bloco "o que a pergunta não é" existe para evitar a arguição mais provável — a de que o trabalho estaria reivindicando avaliar o programa inteiro. O estimando candidato é o incentivo marginal, próximo a uma fronteira administrativa.

---

# Bloco III — Literatura

## Slide 8 — Literatura

- **Tracking:** `Literatura`
- **Título:** A literatura modela a escolha locacional do médico, mas não testa um preço fixado por regra
- **Corpo:** duas colunas.

  **Teórica — de onde vêm as primitivas**

  | Trabalho | O que fornece |
  |---|---|
  | Moehling, Niemesh, Thomasson & Treber (2020) | escolha locacional intertemporal: o médico maximiza o valor presente de rendimento real menos custo locacional não pecuniário |
  | Choné & Ma (2011); Reinhardt (1975) | utilidade do médico com altruísmo: atender pacientes gera cansaço e satisfação, mediados por equipe e capital instalado |
  | Redding & Rossi-Hansberg (2017) | equilíbrio espacial: amenidades e custo de moradia entram como componentes do custo de estar ali |

  **Empírica — de onde vêm os fatos**

  | Trabalho | O que fornece |
  |---|---|
  | Costa, Nunes & Sanches (2024) | escolha discreta estimada para médicos formados no Brasil: salário real, vínculo de origem e infraestrutura pesam na localização |
  | Diamond (2016) | como uma aplicação empírica trata conjuntamente renda, moradia, amenidades e heterogeneidade |
  | Sivey, Scott, Witt, Joyce & Humphreys (2012) | experimento de escolha discreta: disposição a aceitar posto remoto responde a incentivo monetário |

  **A lacuna:** essas evidências vêm de escolha declarada, de variação salarial de mercado ou de contexto histórico. Nenhuma observa um **valor de bolsa fixado por regra pública, descontínuo em um escore territorial**, como o do PMM-E.
- **Fonte:** [`docs/03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md); [`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 3.
- **Nota:** a separação em duas colunas não é estética, é regra do projeto: trabalho empírico não fundamenta equação teórica, e magnitude estimada em outro contexto não vira primitiva. Moehling é a única exceção declarada — sua **equação de escolha** fundamenta a teoria; suas magnitudes históricas, não.

---

# Bloco IV — Modelo teórico

## Slide 9 — A condição de aceitação

- **Tracking:** `Modelo · 1 de 3`
- **Título:** O médico aceita a vaga quando o ganho monetário supera o custo de estar ali
- **Corpo:**
  - O médico $i$ escolhe o município $m$ que maximiza o valor presente líquido da carreira (Moehling et al., 2020, eq. 1, adaptada):

    $$V_{im} = \sum_t \delta^t\left[\frac{\mathbb{E}\left(w_{imt}\mid B_m\right)}{p_{mt}} - c_{im}\right] + \varepsilon_{im},
    \qquad m_i^\ast \in \arg\max_{m\,\in\,\mathcal{M}\cup\{0\}} V_{im}.$$

  - Três leituras que o modelo impõe:

    | Termo | Leitura |
    |---|---|
    | $\mathbb{E}(w_{imt}\mid B_m)$ | a bolsa **entra na remuneração esperada**; ela é fixada pela regra, não negociada |
    | $p_{mt}$ | o que importa é a bolsa **real**, deflacionada pelo custo de vida local |
    | $c_{im}$ | tudo o que torna estar naquele município custoso e não é pago em dinheiro |

  - A alternativa $m=0$ é ficar fora do programa. Aceitar a vaga exige $V_{im} \geq V_{i0}$.
- **Fonte:** [`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 1.
- **Nota:** o horizonte $\sum_t\delta^t$ não é ornamento: é o que permite tratar **entrar** e **ficar** como duas margens do mesmo problema, e não como dois modelos.

## Slide 10 — O custo de estar ali

- **Tracking:** `Modelo · 2 de 3`
- **Título:** O custo de estar ali tem duas partes, e a infraestrutura entra nas duas
- **Corpo:**
  - Abrindo $c_{im}$:

    $$c_{im} = \underbrace{\phi(\text{dist}_{im}) - \gamma A_m + \theta_i^{\text{rural}}}_{\text{geográfico}} \; + \; \underbrace{C(q; L_m, K_m) - \alpha_i B(q; L_m, K_m)}_{\text{laboral líquido}}$$

    | Componente | Sinal | Significado |
    |---|:---:|---|
    | $\phi'(\text{dist})$ | $>0$ | afastar-se da família custa, e custa mais a cada quilômetro |
    | $-\gamma A_m$ | $<0$ | amenidade urbana compensa |
    | $C(q)$ | $C'>0,\;C''>0$ | atender cansa, e cansa de forma crescente |
    | $\alpha_i B(q)$ | $B'>0,\;B''<0$ | curar dá satisfação, ponderada pelo altruísmo $\alpha_i$ |

  - **Equipe ($L$) e capital instalado ($K$) atuam duas vezes**: reduzem o cansaço ($\partial C/\partial K<0$) e ampliam o benefício de saúde produzido ($\partial B/\partial K>0$). Logo $\partial c/\partial K<0$ por dois caminhos.
  - Consequência incômoda: no município vulnerável, $K$ e $L$ são baixos — o mesmo lugar que paga mais é o que impõe maior custo laboral.
- **Fonte:** [`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seções 2.1–2.4.
- **Nota:** se houver tempo, mencionar a forma em U do custo laboral líquido e o ponto $q_{c_{\max}}$ (figura em `docs/02_teoria/figuras/curva_custo_laboral_burnout.png`). Não é necessário para as hipóteses e pode ser sacrificado.

## Slide 11 — Da condição às hipóteses

- **Tracking:** `Modelo · 3 de 3`
- **Título:** Da condição de aceitação saem três hipóteses testáveis
- **Visual:** `F6` — reta de indiferença no plano (custo latente $c_0$, bolsa $B$), com a região de aceitação acima da reta e o degrau de R$ 5.000 deslocando a fronteira. **Figura a produzir.**
- **Corpo:**
  - Escrevendo o custo latente como função da vulnerabilidade, $c_{im} = c_0(IVS_m) + \eta_i$, o médico aceita $m$ quando

    $$\frac{B_m}{p_m} - c_0(IVS_m) \;\geq\; \bar{v}_i,$$

    e, comparando dois municípios separados pela fronteira de faixa, o preenchimento da faixa mais vulnerável exige

    $$\boxed{\;\frac{\Delta B_m}{p_m} \;>\; \Delta c_0\;}\qquad \text{com } \Delta B_m = \text{R\$ }5.000.$$

  - Cada derivada gera uma hipótese:

    | Derivada | Leitura | Gera |
    |---|---|:---:|
    | $\dfrac{\partial \Pr(\text{aceitar})}{\partial B_m} > 0$ | mais bolsa, mais chance de a vaga ser ocupada | **H1** |
    | $\dfrac{\partial \Pr(\text{permanecer em } t{+}k)}{\partial B_m} > 0$ | a bolsa entra em **todo** período descontado, não só no primeiro | **H2** |
    | $\dfrac{\partial^2 \Pr(\text{aceitar})}{\partial B_m\,\partial w^{\text{alt}}_i} < 0$ | o mesmo real de bolsa pesa mais para quem tem menor renda alternativa | **H3** |

  - E uma implicação de sinal ambíguo, que o desenho precisa enfrentar: $c_0'(IVS)$ **não é monotônico**. Infraestrutura urbana precária eleva o custo; carência sanitária eleva $B'(q)$ e pode reduzi-lo via altruísmo.
- **Fonte:** [`docs/02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seções 1 e 4.
- **Nota:** este é o slide que responde ao pedido de derivar as hipóteses diretamente. A ambiguidade de $c_0'(IVS)$ é declarada aqui de propósito: é honestidade teórica e, ao mesmo tempo, a justificativa para estudar o **degrau** e não o gradiente.

---

# Bloco V — Hipóteses

## Slide 12 — As três hipóteses

- **Tracking:** `Hipóteses`
- **Título:** As três hipóteses distinguem entrar, ficar e para quem o incentivo pesa mais
- **Corpo:**

  | | Hipótese | Forma testável | Margem |
  |---|---|---|---|
  | **H1** | Quanto maior a bolsa, maior a probabilidade de preenchimento da vaga | salto no preenchimento administrativo da célula CNES–curso na fronteira de faixa | entrar |
  | **H2** | Quanto maior a bolsa, maior a persistência da oferta médica local após o período inicial | salto no estoque/cobertura municipal do CBO em horizonte fixo de 6 e 12 meses | ficar |
  | **H3** | O efeito da bolsa é maior onde a renda alternativa é menor | interação entre faixa e ausência de mercado privado local: no interior isolado a remuneração colapsa no piso da bolsa, $w = B$ | heterogeneidade |

  - **H3 tem uma versão territorial e uma individual.** A territorial é testável com dados públicos (tipologia REGIC + RM/RIDE). A individual exige microdado de renda que o projeto não possui.
  - **Extensão registrada, fora do slide se faltar tempo (H4):** decompondo o IVS, a dimensão de infraestrutura urbana deve elevar o custo, enquanto a de capital humano pode atenuá-lo.
- **Fonte:** [`docs/02_teoria/hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), seção 4.
- **Nota — correspondência com as hipóteses canônicas:** o documento canônico lista quatro hipóteses e a apresentação leva três. O mapeamento é: H1 do slide $=$ H1 canônica (compensação financeira); H2 do slide é margem nova, derivada do horizonte intertemporal; H3 do slide $=$ H2 canônica (subalocação, $w=B$) na leitura territorial; H3 canônica (clínico versus cirúrgico) e H4 canônica (decomposição do IVS) ficam como extensões. Se arguida, esta é a resposta.
- **Nota — linguagem:** H2 fala em **persistência da oferta local**, não em retenção do bolsista. Retenção individual exigiria identificador longitudinal que não existe nas bases públicas; dizer "retenção" em slide seria afirmar mais do que o dado permite.

---

# Bloco VI — Viabilidade empírica

## Slide 13 — O que já existe

- **Tracking:** `Viabilidade · 1 de 2`
- **Título:** Temos o cadastro de quem está ativo e a regra da bolsa
- **Corpo:**

  | Base | Conteúdo | Cobertura |
  |---|---|---|
  | `ivs_ipea_2010_municipios.csv` | IVS 2010 e seus três sub-índices, IDHM, população e renda | 5.565 municípios; IVS de 0,066 a 0,752 |
  | `pmm_especialistas_nominal.csv` | profissionais ativos, com município, estabelecimento, curso e faixa de atração | 1.480 registros; 325 municípios; 518 CNES; 16 cursos; referência 12/08/2026 |
  | `pmm_especialistas_serie_historica.csv` | ativos agregados por município e curso | 7.276 registros; 9 competências, de dez/2025 a ago/2026 |
  | Painel CNES mensal | estoque de profissionais por município e especialidade | base do outcome de persistência da oferta |
  | Lei nº 15.233/2025 e editais | faixa de atração e valor da bolsa por município | regra completa, publicada |

  - **A variação de interesse existe e é pública:** o valor da bolsa muda em degrau na fronteira de faixa, e a faixa é função de um escore territorial.
- **Fonte:** [`docs/04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md), seção 1.
- **Nota:** dizer explicitamente que nenhuma dessas bases foi construída para avaliação — todas são subprodutos administrativos de transparência. Isso condiciona tudo o que vem no slide seguinte.

## Slide 14 — O que falta

- **Tracking:** `Viabilidade · 2 de 2`
- **Título:** Falta o denominador: sem universo de vagas, descrevemos, não testamos
- **Corpo:**
  - O quadro original do ciclo 1 publica **678 vagas imediatas** e **1.145 posições de reserva**, mas:
    - não existe identificador persistente de vaga que a acompanhe entre oferta, realocação e homologação;
    - a segunda chamada não publica capacidade imediata por célula;
    - há células com mais confirmações do que a capacidade publicada.
  - **Decisão de portão (01/09/2026):** a unidade **célula CNES–curso** foi aprovada como denominador; a **vaga física individual** foi reprovada.

    | Outcome | Situação |
    |---|---|
    | Preenchimento administrativo da célula | ✅ viável |
    | Persistência da oferta local em 6 e 12 meses | ✅ viável, com data-base explícita |
    | Taxa de preenchimento por vaga | ❌ bloqueado, sem `id_vaga` |
    | Retenção individual do bolsista | ❌ bloqueado, sem identificador longitudinal |
    | Salário efetivamente recebido | ❌ não observado |

  - **Próximo passo declarado:** reconstruir a regra de atribuição de faixa e o escore administrativo, e só então abrir os outcomes. Nenhum resultado será usado para escolher fronteira, janela ou especificação.
- **Fonte:** [`docs/auditorias/08_portao_denominador_atracao.md`](../../auditorias/08_portao_denominador_atracao.md); [`docs/01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), seção 4.
- **Nota:** este slide é o encerramento do escopo da banca 1 e deve ser apresentado como força, não como fraqueza — o projeto sabe o que pode e o que não pode afirmar, e registrou isso antes de olhar qualquer resultado.

---

## Slide 15 — Encerramento

- **Tracking:** ausente.
- **Título:** Perguntas
- **Corpo:** repetir, em uma linha, a pergunta da capa e as duas margens (entrar, ficar).
- **Nota:** manter os slides de apoio à mão — decomposição do IVS, curva de custo laboral em U, hipóteses canônicas H3 e H4, e a tabela de linguagem permitida por outcome.

---

## Anexo — slides de apoio (não apresentados)

| # | Conteúdo | Quando usar |
|---|---|---|
| A1 | Curva de custo laboral líquido em U, com $q_{c_{\max}}$ e $q_{c=0}$ | arguição sobre altruísmo ou sobre por que atender pode não ser custoso |
| A2 | Decomposição do IVS em três sub-índices e as forças opostas | arguição sobre o IVS como running variable |
| A3 | Hipóteses canônicas H3 (clínico versus cirúrgico) e H4 (decomposição do IVS) | arguição sobre heterogeneidade por especialidade |
| A4 | Tabela de linguagem máxima permitida por outcome | arguição sobre o que o trabalho poderá afirmar |
| A5 | Tipologia territorial capital / metropolitano / interior polo / interior remoto | arguição sobre "fora das capitais" |
