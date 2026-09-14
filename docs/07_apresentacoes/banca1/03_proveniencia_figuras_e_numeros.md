# Proveniência de figuras e números — banca 1

> **Regra aplicada:** todo número exibido declara fonte, data de referência, cobertura, unidade e reprodutibilidade<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Deck vigente:** `.pptx` montado por script — ver seção 1-A e
> [`deck_pptx/README.md`](deck_pptx/README.md)<br>
> **Atualização:** 14 de setembro de 2026

---

## 1. Figuras

| Código | Figura | Slide | Arquivo | Origem |
|---|---|:---:|---|---|
| `F1` | Especialistas por 100 mil habitantes em jun/2025, por faixa | 4 | `output/apresentacao_banca1/oferta_pre_por_faixa.png` | CNES + Censo 2022, gerada por script |
| `F2` | Colegas da mesma especialidade no município, jun/2025, por faixa | 4 | `output/apresentacao_banca1/retaguarda_por_faixa.png` | CNES, gerada por script |
| `F3` | Bolsa mensal por faixa de atração | 7 | `output/apresentacao_banca1/bolsa_por_faixa.png` | Edital SGTES/MS nº 3/2025, gerada por script |
| `F4` | Custo laboral líquido em função do volume de atendimentos | 15 | `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` | ilustração conceitual do modelo |
| `F5` | Células e vagas imediatas do ciclo 1 por região | 6 | `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` | quadro de vagas do ciclo 1, gerada por script |
| `F6` | Preenchimento do ciclo 1 por faixa anunciada e por estrato territorial | 10 | `output/apresentacao_banca1/preenchimento_ciclo1.png` | tabelas descritivas do módulo A4, gerada por script |

Produzidas por
[`scripts/apresentacao/gerar_figuras_banca1.py`](../../../scripts/apresentacao/gerar_figuras_banca1.py),
que grava `output/apresentacao_banca1/manifesto_figuras.json` com o hash das
entradas, o filtro aplicado e as séries por faixa, região e estrato.

**Definição comum de `F1` e `F2`.** Profissionais distintos com vínculo no CNES
nos CBOs dos **10 cursos com correspondência unívoca curso–CBO** (1, 2, 3, 5, 9,
12, 13, 14, 15 e 16), somados por município — a restrição evita contar a mesma
pessoa em dois cursos. Universo: **295 municípios** com vaga nesses cursos no
ciclo 1. Em `F1`, denominador é a população residente do Censo 2022. É presença
cadastral, não participação no programa. A faixa é a que resulta de aplicar a
grade de 2025 à **categoria de IVS do Ipea**, não a faixa publicada na vaga.

**Definição de `F5`.** Quadro de vagas da chamada 1 do ciclo 1
(`output/aquisicao/quadro_vagas_tratamento.parquet`): 1.295 células
estabelecimento–curso, 460 CNES, 368 municípios; 678 vagas imediatas e 1.145
posições de cadastro de reserva. Regiões pela UF do município.

**Definição de `F6`.** Proporção de células com alguma confirmação ou
homologação, lida de `output/tema_trabalho/A4_tabela_01b_amostra_faixa.csv` (por
faixa **publicada na vaga**) e `A4_tabela_01_amostra_construcao.csv` (por
estrato da tipologia territorial, amostra primária). São proporções brutas; o
módulo A4 é a única saída de estimação do projeto que a apresentação toca, e
dela só se usam as contagens descritivas.

### Figuras geradas e não usadas

| Arquivo | Situação |
|---|---|
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | série mensal de especialistas por 100 mil habitantes, 2024–2026. Saiu do deck na segunda rodada de revisão: sem grupo de comparação, não se lê como efeito do programa. **Voltou ao deck `.pptx` vigente** no slide "O efeito", com rodapé declarando a leitura como descritiva e registrando que não há município fora do programa para comparar — ver `F8` na seção 1-A |
| `docs/07_apresentacoes/banca1/figuras/especialistas_por_uf.png` | Demografia Médica 2025, 16 UFs, montada à mão no deck anterior. Substituída pelos dois extremos citados em texto no slide 3, com fonte, e por `F1` |
| `docs/07_apresentacoes/banca1/figuras/deslocamento_por_regiao.png` | REGIC 2018. Retirada: mede custo do paciente, e reduzir deslocamento não é objetivo declarado do edital |
| `docs/07_apresentacoes/banca1/figuras/motivacao_manchetes.png` | recortes de imprensa com cabeçalho do deck anterior. As manchetes voltaram ao slide 3 como citação textual, com veículo e data, conferidas nas páginas originais |

---

## 1-A. Deck `.pptx` — figuras, equações e o arquivo montado

O deck vigente da banca 1 é o `.pptx` montado sobre o template desenhado pelo
autor. As entradas abaixo seguem a mesma regra das figuras da seção 1: entrada
declarada, script versionado, saída em `output/` e hash no manifesto.

| Código | Artefato | Arquivo | Origem |
|---|---|---|---|
| `F7` | Custo laboral líquido — versão de projeção | `output/apresentacao_banca1/custo_laboral_deck.png` | **ilustração conceitual do modelo**, gerada por script |
| `F8` | Especialistas por 100 mil habitantes, série mensal por faixa | `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | CNES + Censo 2022, gerada por script (mesma figura da seção 1) |
| `D1` | Deck da banca 1 | `output/apresentacao_banca1/deck_banca1_modelo_economico.pptx` | template do autor, com conteúdo aplicado por script |
| `E1` | Equações do modelo renderizadas em LaTeX | `output/apresentacao_banca1/equacoes/*.png` | expressões de `docs/02_teoria/modelo_micro.md`, geradas pelo script do deck |

**Definição de `F7` — ilustração conceitual, sem dado observado.** Gerada por
[`scripts/apresentacao/gerar_figura_custo_laboral_deck.py`](../../../scripts/apresentacao/gerar_figura_custo_laboral_deck.py).
É a mesma construção conceitual de
[`scripts/utils/gerar_grafico_custo_laboral.py`](../../../scripts/utils/gerar_grafico_custo_laboral.py),
que produz `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` (`F4`, do
documento de teoria, não alterada); muda só o que a projeção exige — proporção
larga e baixa, paleta do deck e tipografia legível do fundo da sala.

A construção teórica é Choné & Ma (2011), eq. 1, p. 232, transcrita em
[`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), §2.2:
$C(q)$ é o cansaço ($C' > 0$, $C'' > 0$), $\alpha B(q)$ a satisfação
($B' > 0$, $B'' < 0$) e $c^{\text{laboral}}(q) = C(q) - \alpha B(q)$ o custo
laboral líquido, em U, com as três zonas.

**Nenhum dado observado entra em `F7`, e a figura não tem escala cardinal.** As
curvas são formas funcionais escolhidas para exibir os sinais das derivadas; os
únicos rótulos de eixo são o $q$ de custo mínimo, o ponto $c = 0$ e o zero da
ordenada. Não é simulação de dados do programa, não é projeção de resultado e
não pode ser lida como magnitude. O slide que a exibe deve rotulá-la como
ilustração do modelo — regra permanente 3, na seção 4 deste documento.

**Definição de `D1` — o deck.** Entrada:
`docs/07_apresentacoes/banca1/deck_pptx/base_modelo_economico.pptx`, o template
desenhado pelo autor (identidade visual, slides de sumário, equações da
literatura e gabaritos de modelo). Script:
[`scripts/apresentacao/montar_deck_banca1_pptx.py`](../../../scripts/apresentacao/montar_deck_banca1_pptx.py),
que preserva o desenho e substitui o conteúdo. Saída:
`output/apresentacao_banca1/deck_banca1_modelo_economico.pptx`. Manifesto:
`output/apresentacao_banca1/manifesto_deck_banca1.json`, gravado pelo mesmo
script, com o SHA-256 da base e da saída, o hash de cada figura e de cada
equação usadas, o roteiro numerado dos slides, as correções de digitação feitas
nos sumários do template e a nota de escopo da banca. **Os hashes não são
transcritos aqui: leia-os no manifesto**, que é gravado a cada execução.

As únicas figuras que o deck insere são `F7` e `F8`, ambas lidas de `output/` e
produzidas por script versionado; nenhuma imagem é desenhada fora do pipeline.
Reprodução: `python3 scripts/apresentacao/montar_deck_banca1_pptx.py`, a partir
da raiz do repositório, depois de gerar as figuras. Detalhe de execução e
dependências em [`deck_pptx/README.md`](deck_pptx/README.md).

**Definição de `E1` — as equações renderizadas.** O mesmo script grava em
`output/apresentacao_banca1/equacoes/` um PNG transparente por equação nova,
renderizado em LaTeX de verdade (`amsmath`, `amssymb`), na cor `#114719` do
template. São sete arquivos:

| Arquivo | Expressão | Origem |
|---|---|---|
| `derivadas_lk.png` | sinais de $\partial C/\partial K$, $\partial B/\partial K$ e do custo líquido | `modelo_micro.md`, §2.2 e §2.3 — a extensão em $B$ é do projeto, não de Choné & Ma nem de Reinhardt |
| `decomposicao_custo.png` | abertura de $c_{im}$ nos blocos de Redding & Rossi-Hansberg e de Choné & Ma | `modelo_micro.md`, §2.4 |
| `remuneracao_total.png` | $\mathbb{E}(w_{imt} \mid B_m) = B_m + w^{\mathrm{priv}}_m$ | `modelo_micro.md`, §3, que escreve a esperança $\mathbb{E}(w_{imt}^{(s)} \mid B_m(IVS_m))$ e o colapso de $w$ no piso da bolsa onde não há mercado privado pagador. **A escrita como soma explícita de dois termos é do deck**, não uma equação transcrita do documento |
| `custo_por_ivs.png` | $c_{im} = c_0(IVS_m) + \eta_i$ | `modelo_micro.md`, §3 (a forma do documento traz o índice de especialidade, $c_{im}^{(s)} = c_0^{(s)}(IVS_m) + \eta_i$) |
| `condicao_aceitacao.png` | condição de aceitação da vaga | `modelo_micro.md`, §4.1, onde ela aparece como $B_m/p_m - c_0(IVS_m) \geq \bar{v}_i$; **o deck acrescenta $w^{\mathrm{priv}}_m$ ao numerador**, coerente com §3 e com o slide da remuneração |
| `derivada_hipotese.png` | derivada do preenchimento em relação a $B_m/p_m$ | `docs/02_teoria/hipoteses_e_viabilidade_empirica.md`, §4 |
| `degrau_fronteira.png` | $\Delta B_m / p_m > \Delta c_0$, com $\Delta B_m = \mathrm{R\$}\,5.000$ | mesma fonte; o degrau de R$ 5 mil é a diferença entre faixas adjacentes do Edital SGTES/MS nº 3/2025, item 11.1.3 (seção 2, slide 6) |

As equações são **imagens**, não OMML editável no PowerPoint. A razão está
registrada no script e em [`deck_pptx/README.md`](deck_pptx/README.md): o OMML
nativo não é verificável neste ambiente, de modo que só o que o script escreve
pode ser conferido no render. Alterar uma equação é alterar o LaTeX no script e
rodá-lo de novo, nunca editar a imagem ou o `.pptx` de saída.

---

## 2. Números exibidos

> **Numeração.** Os títulos desta seção usam a numeração da estrutura
> anterior, de 19 slides, que é a de `02_conteudo_slides.md`, de
> `deck_beamer/` e de `deck_slidev/`. O deck `.pptx` vigente reordena e
> renomeia slides; a correspondência entre os dois está no roteiro
> numerado de `manifesto_deck_banca1.json`. As fontes e as ressalvas
> abaixo valem igual nos dois — o que muda é o número do slide.

### Slide 3 — o retrato nacional

Fontes externas, conferidas em 09/09/2026.

| Número | Fonte | Verificação |
|---|---|---|
| 597 mil médicos em 2024; 353.287 especialistas (59,1%) | Scheffer, M. et al., *Demografia Médica no Brasil 2025*, FMUSP/AMB | conferido na cobertura da Agência Brasil (abril de 2025) e do portal Afya; o PDF integral não foi baixado |
| Sudeste 55,4% dos especialistas; Norte 5,9% | idem | idem |
| 453 especialistas por 100 mil habitantes no DF; 68 no MA; 70 no PA | idem | Agência Brasil: "Distrito Federal e São Paulo respondem pelas maiores razões de especialistas por 100 mil habitantes (453 e 244, especificamente), enquanto Maranhão e Pará respondem pelas menores taxas no país (68 e 70, respectivamente)" |
| "apenas 10% dos especialistas atendem no SUS. Além disso, há concentração desses profissionais nas capitais e regiões mais ricas do país" | Senado Notícias, 25/09/2025, citando dados do Ministério da Saúde | conferido na página original. Nota: a Demografia Médica 2025 reporta, para cirurgiões, 10% atuando **exclusivamente** no SUS; a manchete é citada como manchete, não como estatística do trabalho |
| Situação de urgência em saúde pública por 24 meses, em razão do tempo de espera na atenção especializada | Portaria GM/MS nº 7.061, de 6 de junho de 2025 | conferido em reprodução do DOU. A manchete do Correio do Povo de 07/05/2025 antecede a portaria e é citada como manchete |

### Slide 4 — o que o médico vê

| Afirmação | Fonte | Verificação |
|---|---|---|
| "preferences over rural or urban living, or other location-specific attributes, such as proximity to family" | Moehling et al. (2020), *Cliometrica* 14, p. 184 | transcrita em `docs/02_teoria/modelo_micro.md`, seção 1 |
| proximidade do lugar de nascimento ou formação é o principal fator; salário e infraestrutura importam em escala menor; ~50 mil generalistas formados de 2001 a 2013 | Costa, Nunes & Sanches (2024), *REStat* 106(1) | conferido no PDF e na cobertura do estudo (Gazeta do Povo, 2019, sobre a versão *working paper* do Ieps, 49.989 médicos) |
| 3.727 clínicos; 65% não mudariam; "depends not only on the area but also on the characteristics of the job" | Scott et al. (2013), *Soc Sci Med* 96 | **conferido no resumo** (Europe PMC, PMID 24034949) |

### Slide 5 — o que é o PMM-E

| Número ou afirmação | Fonte |
|---|---|
| finalidade: provimento para reduzir o tempo de espera em regiões prioritárias; exclusivo a médicos com diploma brasileiro ou revalidado e certificação de especialista; bolsa-formação; adicional para Amazônia Legal, territórios indígenas e alta vulnerabilidade | Lei nº 15.233/2025, art. 21, que acrescenta o art. 22-D à Lei nº 12.871/2013 — `data/raw/aquisicao/ivs_regra/lei_15233_2025.html` |
| aprimoramento em serviço por integração ensino-serviço; objetivos de equilíbrio regional e redução de desigualdades | Portaria GM/MS nº 7.177/2025, arts. 1 e 2 — conferida em reprodução do Conass |
| objeto (item 1.1); até 12 meses (1.1.4); itinerários formativos com imersões, EAD e supervisão/mentoria (1.2.3, 1.2.7); não é concurso, sem vínculo (1.2.8, 11.1.2); diploma e RQE (3.1); até dois locais (4.1.3); vedada substituição de profissional já vinculado (4.1.6); barema de titulação e tempo de formação, 10 pontos (5.2, Tabela 4); 16 cursos, 6 cirúrgicos e 10 ambulatoriais, 20 horas semanais (Tabela 3, 11.3); bolsa por faixa (11.1.3) | Edital SGTES/MS nº 3/2025, DOU de 24/07/2025 — `data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_dou.pdf`, SHA-256 `417c82d903ab6cf26ca17a5b50705175de40ccc539f0fd2f1e66a3ad9daf6fb2` |
| 1.295 células, 460 estabelecimentos, 368 municípios, 27 UFs; 678 imediatas, 1.145 reserva; Nordeste 505 células (39%); MG 252 células | `F5` e `output/aquisicao/quadro_vagas_tratamento.parquet` |
| dois terços dos municípios com menos de 100 mil habitantes (66,0%); 18 capitais | quadro de vagas × Censo 2022; tipologia A2 (`docs/auditorias/09_tipologia_territorial.md`) |

### Slide 6 — a regra da bolsa

| Número | Fonte |
|---|---|
| 16 indicadores, 3 dimensões do IVS 2010 | Ipea, *Atlas da Vulnerabilidade Social nos Municípios Brasileiros* (2015) |
| Cortes 0,200 / 0,300 / 0,400 / 0,500 | mesma fonte; reproduzidos em `docs/auditorias/01_regra_institucional.md`, §6.3 |
| R$ 20.000 / R$ 15.000 / R$ 10.000 | Edital SGTES/MS nº 3/2025, item 11.1.3, e retificação; auditoria, §6.1 |
| 102 / 107 / 159 municípios por faixa publicada | quadro de vagas do ciclo 1 |
| 177 dos 368 municípios com faixa publicada diferente da recalculada | portão R1, `docs/05_identificacao/16_sintese_achados_e_novo_plano_causal.md`, §3.5 |
| Grade mudou em 2026: *alta* passou à Faixa 1 | Chamamento SGTES/MS nº 1/2026; auditoria §6.4 |
| Cláusulas 11.1.3 (localização + Anexo IV) e 11.1.4 (categorias de IVS) | Edital SGTES/MS nº 3/2025, PDF do DOU preservado em `data/raw/aquisicao/ivs_regra/`, com SHA-256 registrado no artefato |
| 0 municípios abaixo do piso de IVS, 177 acima | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py` |
| Regra de 2026 aplicada ao ciclo 1 acerta 224/368; união das duas regras, 237/368 | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py` |
| Anexo IV não reproduzido no edital (constam I a III) | mesmo PDF, índice de anexos |

### Slide 7 — o problema nos dados do programa

| Número | Fonte |
|---|---|
| 18,3 / 14,4 / 15,0 especialistas por 100 mil hab. (Faixas 1, 2 e 3 publicadas), jun/2025 | `F1`, agrupado pela faixa publicada no quadro de vagas |
| Mediana de 2,5 colegas na Faixa 1, 5,0 na Faixa 2 e 6,5 na Faixa 3; 31% contra 12% sozinho ou com um único colega | `F2`, agrupado pela faixa publicada. Faixa 1 tem 150 pares município–especialidade em 85 municípios |
| Agrupamento por faixa publicada, e não por categoria de IVS recalculada | corrigido em 14/09/2026 em `scripts/apresentacao/gerar_figuras_banca1.py`; a versão anterior rotulava errado 177 dos 368 municípios e invertia o sinal de `F1` |

### Slides 8 e 9 — a evidência

Todos os números foram conferidos na fonte primária em 09/09/2026. O
catálogo completo, com mais estudos, está em
[`docs/03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md),
seção 7.

| Número | Fonte | Verificação |
|---|---|---|
| Salário +33% eleva aceitação em 15,1 p.p.; postos a >200 km vão de ~25% a ~80%; anula o desconto de IDH; sem seleção adversa | Dal Bó, Finan & Rossi (2013), *QJE* 128(3) | RCT com salário sorteado entre 106 postos |
| 65% não mudariam por nenhum pacote; 37% da renda anual para cidade de 5 a 20 mil hab.; 64% para menos de 5 mil; 130% para o pior pacote | Scott et al. (2013), *Soc Sci Med* 96 | **conferido no resumo** (Europe PMC) |
| Elasticidade-salário ~0,4 nas metrópoles e ~0,7 no interior | Costa, Nunes & Sanches (2024), *REStat* 106(1) | **conferido no PDF** |
| +50% no salário público corrige 12,4% do desequilíbrio a US$ 15,7 mi/p.p.; cotas corrigem 63,8% a US$ 2,2–5,1 mi/p.p. | idem | **conferido na Tabela 6 do PDF** |
| 12% contra 39% de permanência após oito anos | Pathman, Konrad & Ricketts (1992), *JAMA* 268(12) | coorte de 9 anos, 412 médicos |
| Degrau de +50% "cai dentro da faixa" de 37% a 64% | leitura do projeto sobre Scott et al. (2013) | é comparação do projeto, não número de um paper; ver `P1` e `P2` |

### Slide 10 — o preenchimento do ciclo 1

| Número | Fonte |
|---|---|
| 30,3% das 1.295 células com confirmação ou homologação | `output/tema_trabalho/A4_relatorio_diagnostico.md`, §1 |
| 23,6% / 37,4% / 31,6% por faixa publicada (n = 539 / 465 / 291) | `F6`, `A4_tabela_01b_amostra_faixa.csv` |
| 35,6% / 44,9% / 26,9% / 20,5% por estrato (n = 73 / 265 / 811 / 146) | `F6`, `A4_tabela_01_amostra_construcao.csv`, amostra primária |

### Slides 12 a 14 — as três tradições teóricas

| Número | Fonte |
|---|---|
| Moehling, Niemesh, Thomasson & Treber (2020), eq. 1, p. 184, e a definição de $c$ | `docs/02_teoria/modelo_micro.md`, §1 |
| Redding & Rossi-Hansberg (2017), eq. 24, p. 28, e a redução a $c^{\text{espacial}}$ | idem, §2.1 e §3.2 |
| Choné & Ma (2011), eq. 1, p. 232; formato em U e as três zonas | idem, §2.2 |
| $\partial B/\partial K > 0$ como extensão do projeto, motivada por Reinhardt (1972, 1975) | idem, §2.3 |
| Limitação de commuting: CNES e edital não informam residência | idem, §2.1 |

### Slide 15 — a junção das três

| Número | Fonte |
|---|---|
| $V_{im}$ integrado e a abertura de $c_{im}$ em dois blocos | `docs/02_teoria/modelo_micro.md`, §2.4 |
| Condição de aceitação $V_{im} \geq V_{i0}$ | idem, §4.1 |
| Nenhuma das três trata de remuneração fixada por regra sobre índice territorial | idem, §3 |

### Slide 19 — viabilidade empírica

| Número | Fonte |
|---|---|
| 1.295 vagas estabelecimento–curso, 368 municípios | quadro de vagas do ciclo 1, chamada 1 |
| 177 dos 368 municípios com faixa publicada diferente da recalculada | portão R1 |
| 37 municípios com IVS ≤ 0,400 na Faixa 1; 94 na Faixa 2; Faixa 1 começa em IVS 0,303 | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py` |
| Em ±0,050 de 0,500, os dois lados são 100% Faixa 1 | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py` |
| Maior IVS da Faixa 3 é 0,372; em ±0,010 de 0,400 não há Faixa 3 de nenhum lado | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py` |
| 83 municípios fora da melhor regra de limiar; 41 promovidos com mediana de população 7.933 contra 32.179 dos 42 rebaixados | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py` |
| Remoticidade como previsor mais forte do desfecho | `A4_tabela_02_modelo_principal_LPM.csv` e `A4_tabela_02b_logit_AME.csv` |
| CNES mensal, jun/2024 a jul/2026 | `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet` |

### Deck `.pptx` — slide "O efeito"

O slide que exibe `F8` só existe no deck `.pptx`. Os números lidos nele:

| Número | Fonte |
|---|---|
| Faixa 1 vai de 17,4 a 22,0 especialistas por 100 mil habitantes | `F8`; série em `output/apresentacao_banca1/manifesto_figuras.json`, chave `serie_por_100k` — 17,40 na competência 202406 e 21,96 na 202607, arredondado no slide |
| Faixa 1 é a de R$ 20 mil | Edital SGTES/MS nº 3/2025, item 11.1.3; faixa publicada na vaga |
| Não há município fora do programa: todos os 368 receberam vaga | quadro de vagas do ciclo 1, chamada 1 |

Que a distância entre a Faixa 1 e as outras duas aumenta depois da homologação é
**leitura descritiva da própria figura**, e o rodapé do slide declara que, sem
município de comparação, ela não identifica efeito. Não promover a efeito causal.

---

## 3. Pendências e ressalvas

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
extensão passou a ser creditada ao projeto no slide 14. Reinhardt permanece
como referência secundária em
[`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 2.3.

### `P1` — a comparação do degrau com a régua australiana é do projeto

Nenhum artigo compara o PMM-E a nada. Dizer que +50% "cai dentro da faixa" de
37% a 64% é leitura do projeto sobre Scott et al. (2013). Apresentar como tal.

### `P2` — comparabilidade do prêmio com a bolsa

Os prêmios compensatórios da literatura são sobre a **renda total** do médico. A
bolsa do PMM-E remunera **20 horas semanais**. Traduzir R$ 5 mil em "+50%" e
comparar com a régua australiana pressupõe que a bolsa seja a fração dominante
do rendimento — hipótese sobre composição de vínculos, não dado. O slide 8
declara essa ressalva.

### `P3` — `populacao_2010` não é população residente

A coluna do arquivo do IVS soma 41.852.890 contra 190.755.799 do Censo 2010, com
razão variando de 0,10 a 0,42 entre municípios. Não é usada como denominador
aqui; o denominador é o Censo 2022, adquirido por
[`scripts/aquisicao/06_adquirir_populacao_censo2022.py`](../../../scripts/aquisicao/06_adquirir_populacao_censo2022.py).
Registro completo em
[`docs/04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md),
seção 4.0.

### `P4` — faixa recalculada em `F1`/`F2`, faixa publicada em `F6`

`F1` e `F2` agrupam municípios pela categoria de IVS do Ipea traduzida na grade
de 2025; `F6` usa a faixa publicada na vaga. As duas coincidem em 191 dos 368
municípios. A escolha é deliberada — `F1`/`F2` descrevem o território, `F6`
descreve a política como aplicada — e cada figura diz qual usa. Não somar nem
comparar valores entre elas.

### `P5` — Demografia Médica 2025 conferida em cobertura, não no PDF

Os números do slide 3 vêm de reproduções do estudo pela Agência Brasil e pelo
portal Afya. O PDF integral da FMUSP não pôde ser baixado em 09/09/2026. A
conferência no original é pendência não bloqueante.

---

## 4. Regra permanente

1. Figura derivada de base do repositório é gerada por script e lida de
   `output/`.
2. Figura de fonte externa é preservada em `figuras/`, com a fonte na legenda e
   uma linha na seção 1.
3. Figura conceitual recebe rótulo de ilustração do modelo.
4. Número exibido sem linha na seção 2 é erro, não detalhe editorial.
5. Documento oficial citado em slide tem cópia em `data/raw/aquisicao/`, com
   hash registrado aqui.
6. Deck é artefato derivado: template de entrada versionado em `docs/`, saída em
   `output/`, e hash de entrada e saída no manifesto do deck. Conteúdo não se
   corrige editando o `.pptx` de saída.
