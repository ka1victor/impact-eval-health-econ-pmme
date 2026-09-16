# Proveniência de figuras e números — banca 1

> **Regra aplicada:** todo número exibido declara fonte, data de referência, cobertura, unidade e reprodutibilidade<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Atualização:** 16 de setembro de 2026

> [!IMPORTANT]
> **A numeração mudou em 16/09/2026.** O deck passou a ter **16 slides em 3
> seções** (mapa no topo de [02](02_conteudo_slides.md)). Toda referência a
> slide neste arquivo usa a **numeração nova**: 1 capa, 2 sumário, 3 divisória,
> 4 Problema, 5 Política, 6 Efeitos, 7 Pergunta, 8 divisória, 9 Visão geral,
> 10 Custo da localidade, 11 Remuneração da localidade, 12 divisória,
> 13 Implicações, 14 Hipótese, 15 Disponibilidade de dados, 16 Desafio
> metodológico. Referências a slides em versões anteriores deste arquivo, ou em
> commits antigos, não são comparáveis.

---

## 1. Figuras

| Código | Figura | Slide | Arquivo | Origem |
|---|---|:---:|---|---|
| `E1` | Especialistas por 100 mil habitantes, por UF, 2024 | 4 | `docs/07_apresentacoes/banca1/figuras/especialistas_por_uf.png` | Demografia Médica 2025; **externa, montada à mão** — ver `P6` |
| `E2` | Deslocamento médio para serviços de alta complexidade, por região | 4 | `docs/07_apresentacoes/banca1/figuras/deslocamento_por_regiao.png` | atribuída à REGIC 2018; **externa e sem fonte primária confirmada** — ver `P6` e `P7` |
| `F3` | Bolsa mensal por faixa de atração | 5 | `output/apresentacao_banca1/bolsa_por_faixa.png` | Edital SGTES/MS nº 3/2025, gerada por script |
| `F1` | Especialistas por 100 mil habitantes em jun/2025, por faixa publicada | 5 | `output/apresentacao_banca1/oferta_pre_por_faixa.png` | CNES + Censo 2022, gerada por script |
| `F2` | Colegas da mesma especialidade no município, jun/2025, por faixa publicada | 5 | `output/apresentacao_banca1/retaguarda_por_faixa.png` | CNES, gerada por script |
| `F6` | Preenchimento do ciclo 1 por faixa publicada e por estrato territorial | 6 | `output/apresentacao_banca1/preenchimento_ciclo1.png` | tabelas descritivas do módulo A4, gerada por script |

`F4` (curva de custo laboral) e `F5` (vagas por região) saíram do deck no corte
de 16/09/2026 e estão listadas abaixo entre as figuras não usadas.

`F1`, `F2`, `F3` e `F6` são produzidas por
[`scripts/apresentacao/gerar_figuras_banca1.py`](../../../scripts/apresentacao/gerar_figuras_banca1.py),
que grava `output/apresentacao_banca1/manifesto_figuras.json` com o hash das
entradas, o filtro aplicado e as séries por faixa, região e estrato. **`E1` e
`E2` não são**: vêm do deck do grupo e violam a regra de proveniência do
projeto enquanto não forem geradas por script — é a pendência `P6`.

**Definição comum de `F1` e `F2`.** Profissionais distintos com vínculo no CNES
nos CBOs dos **10 cursos com correspondência unívoca curso–CBO** (1, 2, 3, 5, 9,
12, 13, 14, 15 e 16), somados por município — a restrição evita contar a mesma
pessoa em dois cursos. Universo: **295 municípios** com vaga nesses cursos no
ciclo 1. Em `F1`, denominador é a população residente do Censo 2022. É presença
cadastral, não participação no programa. Desde 14/09/2026 a faixa é a
**publicada na vaga** do quadro do ciclo 1, não a que resultaria de aplicar a
grade de 2025 à categoria de IVS do Ipea — as duas divergem em 177 dos 368
municípios, e agrupar pela categoria rotulava errado quase metade deles.

**Definição de `F5`** (gerada, não usada). Quadro de vagas da chamada 1 do
ciclo 1 (`output/aquisicao/quadro_vagas_tratamento.parquet`): 1.295 células
estabelecimento–curso, 460 CNES, 368 municípios; 678 vagas imediatas e 1.145
posições de cadastro de reserva. Regiões pela UF do município. Os totais
continuam citados em texto no slide 5.

**Definição de `F6`.** Proporção de células com alguma confirmação ou
homologação, lida de `output/tema_trabalho/A4_tabela_01b_amostra_faixa.csv` (por
faixa **publicada na vaga**) e `A4_tabela_01_amostra_construcao.csv` (por
estrato da tipologia territorial, amostra primária). São proporções brutas; o
módulo A4 é a única saída de estimação do projeto que a apresentação toca, e
dela só se usam as contagens descritivas e, no slide 6, o contraste ajustado de
estrato, declarado como **associativo**.

### Figuras geradas e não usadas

| Arquivo | Situação |
|---|---|
| `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` (`F5`) | células e vagas imediatas do ciclo 1 por região. Saiu do slide da Política no corte de 16/09/2026: descrevia sem argumentar, e os totais que importam (1.295 / 460 / 368 / 39% / 18 capitais) ficaram em texto no slide 5. O script continua gerando |
| `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` (`F4`) | ilustração conceitual do custo laboral em U. Saiu do deck em 16/09/2026 com a fusão dos dois slides de custo; o formato em U é descrito em texto no **slide 10**. Permanece como figura canônica de `modelo_micro.md`, §2.2. A ressalva de legibilidade em projeção deixa de afetar a apresentação |
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | série mensal de especialistas por 100 mil habitantes, 2024–2026. Saiu do deck na segunda rodada de revisão: sem grupo de comparação, não se lê como efeito do programa. O script continua gerando; a série está no `manifesto_figuras.json` e é a única parte reprodutível da tabela do deck do grupo — ver `P8` |
| `docs/07_apresentacoes/banca1/figuras/motivacao_manchetes.png` | recortes de imprensa com cabeçalho do deck anterior. As manchetes entraram no slide do Problema como citação textual em 09/09/2026 e saíram no corte de 16/09/2026; a portaria de urgência continua citada em texto e a manchete dos 10% passou a **advertência** no slide 4 |

`especialistas_por_uf.png` e `deslocamento_por_regiao.png` saíram desta lista em
16/09/2026: a reescrita do slide 4 as **recolocou na tela** e elas passaram a
`E1` e `E2`, com as pendências `P6` e `P7` abertas.

---

## 2. Números exibidos

### Slide 4 — Problema: o retrato nacional e a dupla prática

Fontes externas, conferidas em 09/09/2026 e revistas em 16/09/2026. A revisão de
16/09/2026 corrigiu um erro factual (ver `Correção factual` na seção 3) e
rebaixou a manchete dos 10%.

| Número | Fonte | Verificação |
|---|---|---|
| 597 mil médicos em 2024; 353.287 especialistas (59,1%) | Scheffer, M. et al., *Demografia Médica no Brasil 2025*, FMUSP/AMB, dados de dez/2024 | conferido na cobertura da Agência Brasil (abril de 2025) e do portal Afya |
| Sudeste 55,4% dos especialistas; Sul 16,7%; Nordeste 14,5%; Norte 5,9% | idem | ⚠️ **conferido apenas em cobertura.** Uma leitura do PDF integral **não localizou** esses percentuais. O portal Afya reporta: *"A região Sudeste concentra 55,4% dos especialistas, seguida pelo Sul (16,7%) e Nordeste (14,5%). Já o Norte responde por apenas 5,9%"*. Ver `P5` |
| 453 especialistas por 100 mil habitantes no DF; 244 em SP; 68 no MA; 70 no PA | idem | Agência Brasil: "Distrito Federal e São Paulo respondem pelas maiores razões de especialistas por 100 mil habitantes (453 e 244, especificamente), enquanto Maranhão e Pará respondem pelas menores taxas no país (68 e 70, respectivamente)". É a série de `E1` |
| **72,4%** dos cirurgiões em **dupla prática** (público **e** privado); **19,9%** exclusivamente no setor privado; **7,7%** exclusivamente no setor público ou no atendimento a pacientes do SUS | Scheffer, M. et al., *Demografia Médica no Brasil 2025*, FMUSP/AMB, **cap. 13, Figura 1, p. 254** | conferido na fonte primária, que diz literalmente: *"predomina a dupla prática (72,4%). Apenas 7,7% dos cirurgiões atuam, exclusivamente, no setor público ou no atendimento a pacientes do SUS; enquanto 19,9% atuam somente no setor privado"*. Somando dupla prática e exclusivos do público, **80,1%** atendem SUS |
| Cobertura do recorte setorial: **inquérito por amostra** de associados do **Colégio Brasileiro de Cirurgiões** — **1.544 respondentes** de **6.869 elegíveis** | idem, cap. 13 | **não é censo** dos **42.426** cirurgiões do país. E **não existe o mesmo recorte para outras especialidades** em fonte pública: qualquer generalização de "especialistas" a partir desses três números é extrapolação do leitor, não resultado do estudo |
| "apenas 10% dos especialistas atendem no SUS. Além disso, há concentração desses profissionais nas capitais e regiões mais ricas do país" | Senado Notícias, **24/09/2025** | 🚫 **não citável em slide.** É **fala do ministro da Saúde em debate de medida provisória**, sem metodologia publicada, e **conflita com a fonte primária**: pela Demografia Médica 2025, **80,1%** dos cirurgiões atendem SUS (72,4% + 7,7%). O slide 4 a exibe **como advertência do que não se pode dizer**, não como estatística |
| Deslocamento médio para serviços de alta complexidade: Norte **276 km**, Centro-Oeste **256**, Nordeste **179**, Sudeste **107**, Sul **101** | atribuídos à REGIC 2018 (IBGE), deslocamentos para serviços de saúde | 🚫 **fonte primária não confirmada.** Série de `E2`; ver `P7` |
| 16 cursos: 6 cirúrgicos e 10 ambulatoriais | Edital SGTES/MS nº 3/2025, Tabela 3 | conferido em 16/09/2026 também nos códigos 1–16 do quadro de vagas (cursos 7 a 16 são ambulatoriais: colonoscopia, colposcopia, ecocardiografia, duas endoscopias digestivas, oncologia clínica, radioterapia, ultrassonografia mamária, videolaringoscopia, anatomia patológica) |
| Três maiores cursos em oferta no ciclo 1: **endoscopia digestiva alta, 188 células**; **colonoscopia, 164**; **anestesiologia perioperatória, 147** | `output/aquisicao/quadro_vagas_tratamento.parquet` e Tabela 3 do Edital SGTES/MS nº 3/2025 | recontagem em 16/09/2026 sobre as 1.295 células estabelecimento–curso da chamada 1; unidade é **célula**, não vaga |
| **6 dos 16** títulos citam oncologia, tumores ou câncer | idem | cursos 3, 4, 5, 6, 12 e 16 (cirurgia oncológica avançada; coloproctológica com foco em tumores colorretais; aparelho digestivo com foco em tumores digestivos; ginecológica com foco em tumores ginecológicos; oncologia clínica; anatomia patológica com ênfase em oncologia) |
| "na redução do tempo de espera, na ampliação do diagnóstico precoce e no fortalecimento das redes de atenção especializada" | Edital SGTES/MS nº 3/2025, item 1.2.1 | conferido no PDF do DOU preservado em `data/raw/aquisicao/ivs_regra/` |
| Situação de urgência em saúde pública por 24 meses, em razão do tempo de espera na atenção especializada | Portaria GM/MS nº 7.061, de 6 de junho de 2025 | conferido em reprodução do DOU; **fora da tela** desde 16/09/2026, mantido aqui por continuar na documentação de origem |

### Slide 5 — Política: o que é o PMM-E e o que fixa a bolsa

| Número ou afirmação | Fonte |
|---|---|
| finalidade: provimento para reduzir o tempo de espera em regiões prioritárias; exclusivo a médicos com diploma brasileiro ou revalidado e certificação de especialista; bolsa-formação | Lei nº 15.233/2025, art. 21, que acrescenta o art. 22-D à Lei nº 12.871/2013 — `data/raw/aquisicao/ivs_regra/lei_15233_2025.html` |
| aprimoramento em serviço por integração ensino-serviço; objetivos de equilíbrio regional e redução de desigualdades | Portaria GM/MS nº 7.177/2025, arts. 1 e 2 — conferida em reprodução do Conass |
| objeto (item 1.1); até 12 meses (1.1.4); itinerários formativos com imersões, EAD e supervisão/mentoria (1.2.3, 1.2.7); não é concurso, sem vínculo (1.2.8, 11.1.2); diploma e RQE (3.1); até dois locais (4.1.3); vedada substituição de profissional já vinculado (4.1.6); barema de titulação e tempo de formação, 10 pontos (5.2, Tabela 4); 16 cursos, 6 cirúrgicos e 10 ambulatoriais, 20 horas semanais (Tabela 3, 11.3); bolsa por faixa (11.1.3) | Edital SGTES/MS nº 3/2025, DOU de 24/07/2025 — `data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_dou.pdf`, SHA-256 `417c82d903ab6cf26ca17a5b50705175de40ccc539f0fd2f1e66a3ad9daf6fb2` |
| 1.295 células, 460 estabelecimentos, 368 municípios, 27 UFs; Nordeste 505 células (39%) | `output/aquisicao/quadro_vagas_tratamento.parquet` e `manifesto_figuras.json`; 678 imediatas, 1.145 reserva e MG 252 saíram do slide em 16/09/2026 |
| dois terços dos municípios com menos de 100 mil habitantes (66,0%); 18 capitais | quadro de vagas × Censo 2022; tipologia A2 (`docs/auditorias/09_tipologia_territorial.md`) — em texto de apoio, fora da tela desde 16/09/2026 |
| **incidência de contribuição previdenciária**: o participante é segurado obrigatório do RGPS, como **contribuinte individual**, e o valor devido é descontado da bolsa-formação | Edital SGTES/MS nº 3/2025, **item 11.2**, conferido no PDF do DOU em 16/09/2026 |
| **adicional** para Amazônia Legal, territórios indígenas e áreas de alta vulnerabilidade, *"conforme regulamentação do Ministério da Saúde e disponibilidade orçamentária"* | Lei nº 15.233/2025, **art. 22-D, §4º** — conferido no HTML preservado |
| o adicional do §4º **não foi regulamentado no ciclo 1** | verificado no PDF do edital em 16/09/2026: a palavra **"adicional"** aparece **uma única vez** no edital, e no **barema de titulação** (Tabela 4, item 5.2 — "ano adicional" de residência), nunca como acréscimo à bolsa. O quadro de vagas tem um único campo de remuneração, a faixa de atração |
| **nenhum município e nenhuma célula município–curso** do ciclo 1 aparece com mais de uma faixa | `output/aquisicao/quadro_vagas_tratamento.parquet`, verificado em 16/09/2026: 0 municípios com mais de uma `faixa_atracao_anunciada` e 0 células município–curso com mais de uma. É o que sustenta a afirmação de que o valor depende **só do município** |
| 16 indicadores, 3 dimensões do IVS 2010 | Ipea, *Atlas da Vulnerabilidade Social nos Municípios Brasileiros* (2015) |
| Cortes 0,200 / 0,300 / 0,400 / 0,500 | mesma fonte; reproduzidos em `docs/auditorias/01_regra_institucional.md`, §6.3 |
| R$ 20.000 / R$ 15.000 / R$ 10.000 | Edital SGTES/MS nº 3/2025, item 11.1.3, e retificação; auditoria, §6.1 — é a série de `F3` |
| Cláusulas 11.1.3 (localização + Anexo IV) e 11.1.4 (categorias de IVS) | Edital SGTES/MS nº 3/2025, PDF do DOU preservado em `data/raw/aquisicao/ivs_regra/`, com SHA-256 registrado acima |
| Anexo IV não reproduzido no edital (constam I a III) | mesmo PDF, índice de anexos |
| 177 dos 368 municípios com faixa publicada diferente da recalculada; 0 abaixo do piso de IVS, 177 acima; 48% promovidos | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py`; portão R1, `docs/05_identificacao/16_sintese_achados_e_novo_plano_causal.md`, §3.5 |
| 102 / 107 / 159 municípios por faixa publicada | quadro de vagas do ciclo 1 — em texto de apoio, fora da tela desde 16/09/2026 |
| Grade mudou em 2026: *alta* passou à Faixa 1 | Chamamento SGTES/MS nº 1/2026; auditoria §6.4 — fora da tela, escopo do ciclo 1 |
| Regra de 2026 aplicada ao ciclo 1 acerta 224/368; união das duas regras, 237/368 | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json` — fora da tela, mantido como registro do portão R1 |
| 18,3 / 14,4 / 15,0 especialistas por 100 mil hab. (Faixas 1, 2 e 3 publicadas), jun/2025 | `F1`, agrupado pela faixa publicada no quadro de vagas |
| Mediana de 2,5 colegas na Faixa 1, 5,0 na Faixa 2 e 6,5 na Faixa 3; 31% contra 12% sozinho ou com um único colega | `F2`, agrupado pela faixa publicada. Faixa 1 tem 150 pares município–especialidade em 85 municípios |
| Agrupamento por faixa publicada, e não por categoria de IVS recalculada | corrigido em 14/09/2026 em `scripts/apresentacao/gerar_figuras_banca1.py`; a versão anterior rotulava errado 177 dos 368 municípios e invertia o sinal de `F1` — ver `P4` |
| Teoria da mudança: regra de valor (11.1.3 e 11.1.4), provimento como finalidade (art. 22-D e item 1.1.2), redução da espera como objetivo (art. 22-D e itens 1.2.1 e 1.2.5.V) | Lei nº 15.233/2025 e Edital SGTES/MS nº 3/2025. O que está em **amarelo** no diagrama é o que **nenhum ato afirma** — é leitura do projeto sobre o que os atos deixam de dizer, não citação |

### Slide 6 — Efeitos: o ciclo 1 e a literatura

> **Classificação de rigor:** todos os números do ciclo 1 neste slide são
> **associativos/descritivos**. Nenhum é efeito causal do PMM-E; a `CAUTION` do
> slide declara isso na tela e o slide 16 explica por quê.

| Número | Fonte |
|---|---|
| **393 de 1.295** células com confirmação ou homologação — **30,3%** | `output/tema_trabalho/A4_relatorio_diagnostico.md`, §1 |
| 23,6% / 37,4% / 31,6% por faixa publicada (n = 539 / 465 / 291) | `F6`, `A4_tabela_01b_amostra_faixa.csv` |
| 35,6% / 44,9% / 26,9% / 20,5% por estrato (n = 73 / 265 / 811 / 146) | `F6`, `A4_tabela_01_amostra_construcao.csv`, amostra primária |
| **Metropolitano +20,9 p.p.** sobre interior remoto no **modelo ajustado** | `output/tema_trabalho/A4_tabela_03b_ajuste_completo.csv`, termo `estrato_metropolitano` = 0,2085 (EP cluster 0,078; p = 0,008), especificação `LPM_full_estrato_ivs_logpop_estoque_faixa_FE`, n = 1.295, 368 clusters. Na especificação mínima o mesmo contraste é 0,279 — o slide cita o **ajustado**, que é o menor |
| **A5: +0,500** especialista cadastrado em **mar/2026** contra **jun/2025**, **erro padrão 0,234** | `output/tema_trabalho/A5_relatorio_diagnostico.md`, módulo A5. O EP 0,234 é o da convenção anterior (p = 0,033); na convenção `reghdfe`/`fixest`, que conta os efeitos fixos absorvidos, o EP é 0,2469 e p = 0,044. O slide arredonda para "+0,50" |
| **Pré-tendências: F = 1,031, p = 0,420** (teste conjunto pré-referência) | idem — é ausência de pré-tendência **detectável**, não prova de paralelismo |
| Salário +33% eleva aceitação em 15,1 p.p.; 106 postos; a >200 km, de ~25% a ~80%; sem seleção adversa | Dal Bó, Finan & Rossi (2013), *QJE* 128(3) — RCT com salário sorteado |
| **+15,1 médicos do programa** por 100 mil habitantes, contra expansão **líquida** de apenas **+5,7** | Hone, T.; Powell-Jackson, T.; Santos, L. M. P. et al. (2020), *BMC Health Services Research* **20:873**. DiD em 5.565 municípios, 2008–2017; o restante substituiu profissionais preexistentes. Catalogado em [`03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md), §7 |
| 3.727 clínicos; 65% não mudariam por nenhum pacote; 37% da renda anual para cidade de 5 a 20 mil hab.; 64% para menos de 5 mil; 130% para o pior pacote | Scott et al. (2013), *Soc Sci Med* 96 — **conferido no resumo** (Europe PMC, PMID 24034949) |
| Elasticidade-salário ~0,4 nas metrópoles e ~0,7 no interior | Costa, Nunes & Sanches (2024), *REStat* 106(1) — **conferido no PDF** |
| +50% no salário público corrige 12,4% do desequilíbrio a US$ 15,7 mi/p.p.; cotas corrigem 63,8% a US$ 2,2–5,1 mi/p.p. | idem — **conferido na Tabela 6 do PDF** |
| 12% contra 39% de permanência após oito anos | Pathman, Konrad & Ricketts (1992), *JAMA* 268(12) — coorte de 9 anos, 412 médicos |
| Degrau de +50% "cai dentro da faixa" de 37% a 64% | leitura do projeto sobre Scott et al. (2013); é comparação do projeto, não número de um paper — ver `P1` e `P2` |
| Ressalva na tela: os percentuais da literatura são sobre a **renda total**; a bolsa remunera **20 horas semanais** | `P2` |

### Slide 7 — Pergunta de pesquisa

| Número | Fonte |
|---|---|
| Degrau de **R$ 5 mil** entre faixas | Edital SGTES/MS nº 3/2025, item 11.1.3 (R$ 10 / 15 / 20 mil) |
| "maiores bolsas do PMM-E para municípios mais vulneráveis compensam suas desvantagens territoriais na atração de médicos especialistas?" | [`01_pergunta_escopo/15`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md) — formulação canônica, citada textualmente |

### Slide 9 — Visão geral: a equação de escolha

| Número | Fonte |
|---|---|
| Moehling, Niemesh, Thomasson & Treber (2020), eq. 1, p. 184, e a definição de $c$ | `docs/02_teoria/modelo_micro.md`, §1 |
| "preferences over rural or urban living, or other location-specific attributes, such as proximity to family" | Moehling et al. (2020), *Cliometrica* 14, p. 184 — transcrita em `modelo_micro.md`, §1 |
| Redding & Rossi-Hansberg (2017) e Choné & Ma (2011) como as duas primitivas do custo | idem, §2.1 e §2.2 |

### Slide 10 — Custo da localidade: o lugar e o trabalho

| Número | Fonte |
|---|---|
| Redding & Rossi-Hansberg (2017), eq. 24, p. 28, e a redução a $c^{\text{geo}}$ | `docs/02_teoria/modelo_micro.md`, §2.1 e §3.2 |
| Choné & Ma (2011), eq. 1, p. 232; formato em U e as três zonas | idem, §2.2 |
| $\partial B/\partial K > 0$ como **extensão do projeto**, motivada por Reinhardt (1972, 1975) | idem, §2.3 — ver a nota sobre Reinhardt na seção 3 |
| Tabela das **quatro desvantagens do médico** (retaguarda, infraestrutura, distância da família, mercado privado ausente) e o bloco do custo de cada uma | idem, §2.1 a §2.3; a coluna "Medimos?" segue o inventário de dados do slide 15. Movida do slide de teoria para o **slide 10** em 16/09/2026 |
| proximidade do lugar de nascimento ou formação é o principal fator; salário e infraestrutura importam em escala menor; ~50 mil generalistas formados de 2001 a 2013 | Costa, Nunes & Sanches (2024), *REStat* 106(1) — conferido no PDF e na cobertura do estudo (Gazeta do Povo, 2019, sobre a versão *working paper* do Ieps, 49.989 médicos) |
| Limitação de commuting: CNES e edital não informam residência | `modelo_micro.md`, §2.1 |

### Slide 11 — Remuneração da localidade

| Número | Fonte |
|---|---|
| $w = B + w^{\text{priv}}$, o deflator e a correspondência dimensão do IVS – bloco do custo | `docs/02_teoria/modelo_micro.md`, §3 e §3.1 |
| R$ 10 mil (Faixa 3) e R$ 20 mil (Faixa 1) na tabela de contraste | Edital SGTES/MS nº 3/2025, item 11.1.3 |
| **20 horas semanais** | Edital SGTES/MS nº 3/2025, item 11.3.b |
| Retomada de **7,7%** exclusivos do setor público e **72,4%** em dupla prática | mesma linha do slide 4 — Scheffer et al. (2025), cap. 13, Figura 1, p. 254. Vale aqui a mesma ressalva de cobertura: é **amostra de cirurgiões**, não o conjunto dos especialistas |

### Slide 13 — Implicações para o PMM-E

| Número | Fonte |
|---|---|
| $V_{im}$ integrado e a abertura de $c_{im}$ em dois blocos | `docs/02_teoria/modelo_micro.md`, §2.4 |
| Nenhuma das três tradições trata de remuneração fixada por regra sobre índice territorial | idem, §3 |
| Tabela de derivadas ($\partial V/\partial B_m > 0$; $\partial^2 V/\partial B_m \partial w^{\text{priv}} < 0$; $\partial V/\partial p_m < 0$; $c_0'(IVS) \gtrless 0$) | idem, §3 e §3.1 |
| As três dimensões do IVS 2010 e seus indicadores, mapeadas nos blocos do custo | Ipea, *Atlas da Vulnerabilidade Social* (2015); mapeamento em `modelo_micro.md`, §3.1 — o mapeamento é **leitura do projeto**, não classificação do Ipea |

### Slide 14 — Hipótese do trabalho

| Número | Fonte |
|---|---|
| Condição de aceitação $V_{im} \geq \bar{v}_i$ e a passagem do médico à vaga | `docs/02_teoria/modelo_micro.md`, §4.1 e §4.2 |
| H1 e $\partial \Pr(\text{preenchimento})/\partial (B_m/p_m) > 0$ | [`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §4.2 |
| $\Delta B_m = \text{R\$ } 5.000$ | Edital SGTES/MS nº 3/2025, item 11.1.3 |

### Slide 15 — Disponibilidade de dados

| Número | Fonte |
|---|---|
| 1.295 células estabelecimento–curso, 368 municípios (desfecho) | quadro de vagas do ciclo 1, chamada 1 |
| **2.815 municípios**, ciclos 1 a 3 (cobertura do instrumento) | `output/aquisicao/quadro_vagas_consolidado.parquet`, 47.475 linhas, `ciclo` ∈ {1, 2, 3}; contagem verificada em 16/09/2026 |
| CNES mensal, jun/2024 a jul/2026 | `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet`; competências `202406` a `202607` no `manifesto_figuras.json` |
| RAIS nunca adquirida; CNES sem carga horária nem renda; residência do profissional é sigilo fiscal; sem fonte municipal de custo de moradia | [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md) |
| Tipologia territorial em 4 estratos; REGIC 2018 e RMs/RIDEs 2022 (IBGE) | `docs/auditorias/09_tipologia_territorial.md` |
| CNES físico (leitos e equipamentos) mapeado, competências não baixadas; SIH bloqueado | inventário de dados, e `docs/06_execucao/06_backlog_wp3_wp4_wp5.md` |

### Slide 16 — Desafio metodológico

| Número | Fonte |
|---|---|
| 177 dos 368 municípios com faixa publicada diferente da recalculada | portão R1, `docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md`, §"Correção de 14/09/2026", e `a01b_reconstrucao_regra_faixa.json` |
| 37 municípios com IVS ≤ 0,400 na Faixa 1; 94 na Faixa 2; os intervalos das três faixas se sobrepõem | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py` |
| Em ±0,050 de **0,500**, os dois lados são **100% Faixa 1** (20 municípios de um lado, 11 do outro) | idem; `14_plano_implementacao_rdd_bolsa.md`, tabela de janelas |
| Maior IVS da Faixa 3 é **0,372**; em ±0,010 de **0,400** não há Faixa 3 de nenhum lado | idem |
| 83 municípios fora da melhor regra de limiar; **41 promovidos** com mediana de população **7.933** contra **32.179** dos **42 rebaixados**, e muito mais interior remoto | idem, §"a variação que sobra não é exógena" |
| Faixa 1 começa em IVS 0,303 | idem — em texto de apoio, fora da tela desde 16/09/2026 |
| Remoticidade como previsor mais forte do desfecho | `A4_tabela_02_modelo_principal_LPM.csv` e `A4_tabela_02b_logit_AME.csv` |
| Anexo IV e critérios de localização como o que destrava o efeito da bolsa; desenho do escore do candidato responde a outra pergunta | `docs/06_execucao/36_backlog_pos_auditoria.md`, item D-3, e `docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md` — citados sem número, por escopo da banca 1 |

---

## 3. Pendências e ressalvas

### Correção factual de 16/09/2026 — os "10% no SUS"

Até 16/09/2026 este arquivo registrava, na linha do Senado Notícias, que *"a
Demografia Médica 2025 reporta, para cirurgiões, 10% atuando **exclusivamente**
no SUS"*. **Era erro.** A fonte primária — Scheffer, M. et al., *Demografia
Médica no Brasil 2025*, FMUSP/AMB, **capítulo 13, Figura 1, p. 254** — diz, na
letra:

> "predomina a dupla prática (72,4%). Apenas 7,7% dos cirurgiões atuam,
> exclusivamente, no setor público ou no atendimento a pacientes do SUS;
> enquanto 19,9% atuam somente no setor privado"

São **três** números, e nenhum deles é 10%: **72,4%** dupla prática, **19,9%**
exclusivamente privado, **7,7%** exclusivamente público ou SUS. Os três estão
registrados na seção 2, slide 4.

Duas restrições de cobertura, que valem para toda citação desses percentuais:

1. **É amostra, não censo.** O recorte vem de um inquérito com associados do
   **Colégio Brasileiro de Cirurgiões**: **1.544 respondentes** de **6.869
   elegíveis**, e não os **42.426** cirurgiões do país. Taxa de resposta e
   autosseleção do respondente não estão controladas.
2. **Não há o mesmo recorte para outras especialidades** em fonte pública. O
   estudo reporta a divisão público/privado **só para cirurgiões**. Estender
   "7,7%" a "especialistas" é extrapolação do leitor.

**Efeito sobre a manchete.** A frase "apenas 10% dos especialistas atendem no
SUS" está **rebaixada a não citável em slide**: é fala do **ministro da Saúde em
debate de medida provisória**, noticiada pelo Senado Notícias em **24/09/2025**
(não 25/09, como este arquivo registrava), sem metodologia publicada, e
**conflita com a fonte primária** — somando dupla prática e exclusivos do setor
público, **80,1%** dos cirurgiões atendem SUS. O slide 4 a exibe apenas como
**advertência** do que não se pode afirmar. O defensável é o inverso: o que é
raro é a **exclusividade** ao SUS.

### Reinhardt: retirado do slide

O projeto citava Reinhardt (1975), *Physician Productivity and the Demand for
Health Manpower*, e o livro não tem sua especificação transcrita no
repositório; a única forma verificável é a geral do artigo de **1972**,
$Q = f(H, X_1, \ldots, X_n)$, no *Review of Economics and Statistics* 54(1).

Avaliado o que a citação acrescenta: Choné e Ma (2011) já escrevem o custo de
atender como $C(q; L, K)$, de modo que equipe e capital já estão no modelo por
essa via. O que Reinhardt acrescentaria é que esses insumos também **elevam o
benefício produzido** — mas escrever $B(q; L, K)$ em vez de $B(q)$ é extensão
deste projeto, não dele. A citação foi retirada do slide de literatura e a
extensão passou a ser creditada ao projeto no **slide 10**. Reinhardt permanece
como referência secundária em
[`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 2.3.

### `P1` — a comparação do degrau com a régua australiana é do projeto

Nenhum artigo compara o PMM-E a nada. Dizer que +50% "cai dentro da faixa" de
37% a 64% é leitura do projeto sobre Scott et al. (2013). Apresentar como tal.

### `P2` — comparabilidade do prêmio com a bolsa

Os prêmios compensatórios da literatura são sobre a **renda total** do médico. A
bolsa do PMM-E remunera **20 horas semanais**. Traduzir R$ 5 mil em "+50%" e
comparar com a régua australiana pressupõe que a bolsa seja a fração dominante
do rendimento — hipótese sobre composição de vínculos, não dado. O **slide 6**
declara essa ressalva na tela, e o slide 11 mostra por que a hipótese é frágil.

### `P3` — `populacao_2010` não é população residente

A coluna do arquivo do IVS soma 41.852.890 contra 190.755.799 do Censo 2010, com
razão variando de 0,10 a 0,42 entre municípios. Não é usada como denominador
aqui; o denominador é o Censo 2022, adquirido por
[`scripts/aquisicao/06_adquirir_populacao_censo2022.py`](../../../scripts/aquisicao/06_adquirir_populacao_censo2022.py).
Registro completo em
[`docs/04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md),
seção 4.0.

### `P4` — faixa recalculada e faixa publicada

Até 14/09/2026, `F1` e `F2` agrupavam municípios pela categoria de IVS do Ipea
traduzida na grade de 2025, enquanto `F6` usava a faixa publicada na vaga, e o
texto do slide falava em "municípios com bolsa de R$ 10 mil" — 48% dos rótulos
estavam errados e o sinal de `F1` invertia. Desde então as três figuras usam a
**faixa publicada**. A categoria recalculada só aparece no
`manifesto_figuras.json`, como detalhe descritivo, e no slide 5, para mostrar
que é piso e não critério. Não comparar valores das figuras atuais com os da
versão anterior.

### `P5` — Demografia Médica 2025: o que está conferido no original e o que não está

Situação em 16/09/2026, por número:

| Número | Estado |
|---|---|
| **72,4% / 19,9% / 7,7%** de atuação dos cirurgiões | ✅ **conferido na fonte primária**, cap. 13, Figura 1, p. 254, com a frase transcrita acima |
| 597 mil médicos; 353.287 especialistas (59,1%); 453 no DF, 244 em SP, 68 no MA, 70 no PA | conferido em **cobertura** (Agência Brasil, abril de 2025; portal Afya) |
| **Sudeste 55,4%**, Sul 16,7%, Nordeste 14,5%, Norte 5,9% | ⚠️ **ressalva de fonte.** Uma leitura do **PDF integral não localizou** esses percentuais. Estão conferidos **apenas em cobertura**, no portal Afya: *"A região Sudeste concentra 55,4% dos especialistas, seguida pelo Sul (16,7%) e Nordeste (14,5%). Já o Norte responde por apenas 5,9%"*. Os números **não são removidos** do slide; a citação é atribuída ao estudo e a checagem no original fica pendente |

Pendência residual, **não bloqueante**: o PDF da *Demografia Médica no Brasil
2025* ainda não está preservado em `data/raw/` com hash, como manda a regra 5 da
seção 4. Ao registrá-lo, conferir no original a distribuição regional de
especialistas.

### `P6` — as duas figuras do slide 4 não são geradas por script versionado

`E1` (especialistas por 100 mil habitantes por UF) e `E2` (deslocamento médio
para serviços de alta complexidade por região) vêm do **deck do grupo**, montadas
fora do pipeline. Isso **contraria a regra de proveniência do `CLAUDE.md`**:
figura derivada de base do repositório é gerada por script versionado e lida de
`output/`; gráfico produzido fora do pipeline não entra em apresentação.

As duas estão na tela porque carregam o argumento do slide 4, e a alternativa —
tirá-las — deixaria o slide sem a evidência territorial. A pendência é de
**forma, não de conteúdo** no caso de `E1`, cuja série está conferida em
cobertura (453 no DF, 68 no MA); em `E2` é de forma **e** de fonte, ver `P7`.

**O que fecha:** acrescentar as duas séries a
`scripts/apresentacao/gerar_figuras_banca1.py`, lendo de `output/`, com a fonte
registrada no `manifesto_figuras.json`. Enquanto isso não acontecer, as duas
figuras são exceção declarada, não prática aceita.

### `P7` — os valores do gráfico de deslocamento não têm fonte primária confirmada

A série de `E2` — **Norte 276 km, Centro-Oeste 256, Nordeste 179, Sudeste 107,
Sul 101** — **não teve fonte primária confirmada**. A origem provável é a
pesquisa **REGIC 2018 do IBGE**, na parte sobre deslocamentos da população para
serviços de saúde, mas a página da pesquisa **retornou HTTP 403** na tentativa de
verificação, e nenhuma tabela publicada foi localizada com esses cinco valores.

Consequência prática: **276 km** e **101 km** aparecem no texto do slide 4 e no
gráfico, e são hoje os dois únicos números da apresentação sem rastreio até uma
fonte checada. Enquanto a checagem não se fizer, tratá-los como **ilustrativos**
e não como estatística do trabalho.

**O que fecha:** localizar a tabela da REGIC 2018 sobre deslocamentos para
serviços de saúde, registrar o arquivo em `data/raw/` com hash e gerar `E2` por
script (fecha `P6` e `P7` juntos). Se a fonte não for localizada, os valores
saem da tela.

### `P8` — a tabela de inclinações pré/pós por faixa do deck do grupo não é reproduzível

O deck do grupo trazia uma tabela de inclinações da série de especialistas por
100 mil habitantes, antes e depois do programa, por faixa: **Faixa 1
0,012/0,271; Faixa 2 0,033/0,136; Faixa 3 0,024/0,269**. Ela **não pode ser
usada**.

**O que é reprodutível.** A **série mensal por faixa** é. Está em
`output/apresentacao_banca1/manifesto_figuras.json`, chave `serie_por_100k`, 26
competências de `202406` a `202607`, gerada por
`scripts/apresentacao/gerar_figuras_banca1.py`. O último ponto, `202607`, é
**Faixa 1 = 21,96**, **Faixa 3 = 17,97** e **Faixa 2 = 16,18** — exatamente os
**22,0 / 18,0 / 16,2** arredondados que o deck exibia. A série, portanto, é a
mesma; o problema está nos coeficientes.

**O que não é.** Os coeficientes pré/pós **não têm origem rastreável em
`output/`**: nenhum artefato do repositório os produz, e nenhum script os grava.
E eles **não se reproduzem**. Recalculando por MQO sobre a própria série do
manifesto, com os marcos registrados nela (`ultima_pre = 202506`,
`primeira_pos = 202510`), obtém-se:

| Faixa | Alegado no deck (pré/pós) | Recalculado da série (pré/pós) |
|---|---|---|
| Faixa 1 | 0,012 / 0,271 | **0,0525 / 0,2535** |
| Faixa 2 | 0,033 / 0,136 | **0,0442 / 0,1167** |
| Faixa 3 | 0,024 / 0,269 | **0,0357 / 0,2653** |

Não é questão de janela: varrendo **todas** as janelas contíguas da série com ao
menos 3 pontos, e exigindo que as **três faixas** batam simultaneamente,
**nenhuma janela pré e nenhuma janela pós** reproduz o trio alegado a uma
tolerância de 0,01. O trio não vem desta série sob nenhum recorte.

**Impedimento de uso.** A tabela fica **fora do slide 6** e fora de qualquer
slide. Números sem origem em `output/` e que não se reproduzem não entram em
apresentação — e, ainda que se reproduzissem, seriam inclinações **sem grupo de
comparação**, que não se leem como efeito do programa (é a mesma razão que tirou
`oferta_antes_depois_por_faixa.png` do deck). A **série mensal por faixa** pode
entrar como contexto descritivo, pelo caminho normal: gerada por script e lida
de `output/`.

---

### `P9` — o slide 16 pede uma figura que ainda não existe

O slide do desafio metodológico sustenta-se num achado visual que **nenhuma
figura do repositório mostra**: a ausência de descontinuidade nos dois cortes da
regra. A figura pedida é a dispersão do **IVS 2010** contra a **faixa
publicada** de cada município, com `0,400` e `0,500` marcados, tornando visíveis
a sobreposição das três faixas e o salto nulo de tratamento em torno dos cortes.

**Insumo disponível.** `output/rdd_bolsa/matriz_municipio_regra_ivs.csv`, que já
tem IVS, categoria recalculada e `valor_anunciado_mensal_brl` por município.

**Fechamento.** Acrescentar a figura a `scripts/apresentacao/gerar_figuras_banca1.py`,
lendo de `output/`, e registrá-la na seção 1 deste documento. Enquanto não
existir, o slide 16 fica só em texto — o que é aceitável, mas desperdiça o
argumento mais forte da seção.

## 4. Regra permanente

1. Figura derivada de base do repositório é gerada por script e lida de
   `output/`.
2. Figura de fonte externa é preservada em `figuras/`, com a fonte na legenda e
   uma linha na seção 1.
3. Figura conceitual recebe rótulo de ilustração do modelo.
4. Número exibido sem linha na seção 2 é erro, não detalhe editorial.
5. Documento oficial citado em slide tem cópia em `data/raw/aquisicao/`, com
   hash registrado aqui.
6. Número que não se reproduz a partir de `output/` não vai à tela, ainda que
   venha de material do grupo.
