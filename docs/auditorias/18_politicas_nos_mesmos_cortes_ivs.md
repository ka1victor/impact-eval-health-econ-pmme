# Políticas federais nos mesmos cortes de IVS da bolsa do PMM-E

> **Execução:** 2026-10-18 (tarefa D do protocolo
> [`06_execucao/40`](../06_execucao/40_protocolo_multioutcome_rdd_bolsa.md), §4),
> revista no mesmo dia depois de auditoria independente.<br>
> **Pergunta:** além da bolsa do PMM-E (+R$ 5 mil em `s > 0,300` e em
> `s > 0,400`, IVS 2010 oficial do Ipea), alguma outra regra federal muda nos
> mesmos cortes?<br>
> **Resposta:** sim, várias, e não só a Portaria GM/MS 752/2023. A mais
> próxima da atenção especializada é o **acréscimo de 20% no teto de emendas e
> de parcelas de custeio da MAC para estados e municípios com "IVS maior que
> 0,3" e "capacidade instalada na média e alta complexidade"** (2024–2027), que
> em 2026 cobre explicitamente os componentes ambulatorial e cirúrgico do
> Agora Tem Especialistas. Na APS, o **cofinanciamento federal de 2024 (IED)**
> muda o valor por equipe em 0,300 e em 0,400, conforme o porte. Uma RDD em
> nível nesses cortes mede um **pacote**, não a bolsa pura.<br>
> **Fontes:** os atos listados no manifesto
> [`output/aquisicao/a10_manifesto_normas_ivs.json`](../../output/aquisicao/a10_manifesto_normas_ivs.json)
> (`totais.fontes_no_manifesto` no diagnóstico), com URL, data de captura, data
> de publicação no DOU, SHA-256 dos bytes e do texto do ato e os trechos
> citados. O cache fica em
> [`data/raw/aquisicao/normas_ivs/`](../../data/raw/aquisicao/normas_ivs/); o
> script baixa o que faltar e para se o texto do ato não for o capturado.
> Diagnósticos em
> [`output/aquisicao/a10_diagnostico_cortes_normas.json`](../../output/aquisicao/a10_diagnostico_cortes_normas.json).
> Script: [`scripts/aquisicao/a10_normas_mesmos_cortes_ivs.py`](../../scripts/aquisicao/a10_normas_mesmos_cortes_ivs.py).<br>
> **Outcomes abertos:** nenhum. O script lê variáveis de atribuição (IVS,
> classes, estratos, porte). Do consolidado do PMMB lê o esquema e, para cada
> uma das colunas, só o número de valores distintos no arquivo inteiro, sem
> cruzar nenhuma delas com o IVS.

Convenção do texto: **[V]** = verificado no texto preservado do ato (o trecho
está no manifesto e o script para se não o encontrar); **[V-dados]** =
verificado por cálculo do script a10 sobre arquivos do repositório;
**[INFERÊNCIA]** = conclusão tirada de dois ou mais textos verificados, que
nenhum deles diz sozinho; **[NÃO VERIFICADO]** = vem de fonte secundária, de
documento não arquivado ou não foi possível conferir.

## 1. Referência: a regra da bolsa

A bolsa do PMM-E usa o IVS 2010 oficial com o limite na classe de baixo:
até 0,300 → R$ 10 mil; 0,301–0,400 → R$ 15 mil; acima de 0,400 → R$ 20 mil
([`16`](16_ivs_2010_oficial_e_arquivo_local.md), §2). Ciclo 1: quadro de vagas
publicado com o Edital SGTES/MS 3/2025 (DOU de 24/07/2025). Janelas do
protocolo 40 para o CNES: pré 2024-06 a 2025-06; pós 2025-10 a 2026-08;
estudo de evento desde 2022-01.

Duas convenções de fronteira aparecem nos atos abaixo, e elas só divergem nos
municípios com IVS **exatamente** igual ao limite (o IVS oficial tem três
casas decimais: `ivs_a08_max_casas_decimais`):

| Convenção | Onde | 0,300 cai em | 0,400 cai em |
|---|---|---|---|
| fechada à direita (`≤`) / estrita (`> 0,3`) | bolsa do PMM-E; categoria do consolidado PMMB; Anexo VI da 3.493/2024; emendas (`IVS maior que 0,3`) | classe de baixo | classe de baixo |
| fechada à esquerda (`≥`) | **texto** das Portarias 485/2023, 752/2023 e 635/2023; Quadro 2 da 5.721/2024 | classe de cima | classe de cima |

**[V-dados]** No IVS oficial (a08), as contagens de municípios exatamente
sobre cada limite estão em `municipios_sobre_os_limites`; sobre os dois cortes
da bolsa são `totais.sobre_os_cortes_da_bolsa` municípios. A categoria do
consolidado PMMB e o código de IVS do Anexo VI da 3.493/2024 põem **todos**
eles na classe de baixo, como a bolsa. As duas bases administrativas
reproduzem o IVS oficial na convenção fechada à direita em todos os municípios
comparados (`categoria_pmmb_a07.igual_classe_fechada_a_direita` e
`ied_aps_3493_2024.codigo_igual_classe_fechada_a_direita`). Na convenção do
texto da 485/2023 a concordância cai, e a diferença
(`totais.diferenca_convencoes_ied` e `totais.diferenca_convencoes_pmmb`) é
igual ao total de municípios sobre os quatro limites
(`totais.sobre_os_quatro_limites`); o script para se não for.

Ou seja: **onde há lista administrativa publicada, o MS aplica o limite como a
bolsa**, mesmo quando o texto da portaria diz "maior ou igual". Para a 752/2023
não há lista arquivada; como ela foi aplicada aos municípios sobre os cortes é
**[NÃO VERIFICADO]**.

## 2. Política por política

### 2.1 Portaria GM/MS 752/2023 — teto de vagas do PMMB em coparticipação

**[V]** DOU de 19/06/2023, Seção 1, Edição Extra A, nº 114-A (cópia em PDF da
SES-SP também arquivada). Trechos:

> Art. 5º Os critérios estabelecidos para delimitação de vagas e promoção da
> equidade entre municípios utilizarão como referência o Índice de
> Vulnerabilidade Social - IVS do Instituto de Pesquisa Econômica Aplicada -
> IPEA (2015), previsto na Portaria GM/MS Nº 485, de 14 de abril de 2023:<br>
> I - municípios com IVS maior ou igual a 0,4 e menor ou igual a 1: até 100% do
> total de equipes de ESF;<br>
> II - municípios com IVS maior ou igual a 0,3 e menor do que 0,4: até 40% do
> total de equipes de ESF; e<br>
> III - municípios com IVS menor do que 0,3: até 10% do total de equipes de ESF.

> § 1º Serão equiparados aos municípios do inciso I deste artigo, os municípios
> onde: I - o valor do teto de remuneração do chefe do poder executivo
> municipal seja abaixo do valor da bolsa do programa; e II - os municípios do
> G100, conforme definição da Frente Nacional de Prefeitos.

> § 2º O limite de vagas não se aplica nas hipóteses em que as novas vagas
> destinarem-se a: I - expansão da cobertura da estratégia da saúde da família
> dentro dos limites previstos na PNAB; e II - equipes de consultório na rua e
> equipes de saúde prisional.

> Art. 3º A coparticipação no financiamento consistirá no desconto do valor de
> custeio mensal da bolsa do profissional do repasse fundo a fundo, limitado ao
> teto federal do Piso de Atenção Primária do referido ente, ficando a cargo do
> Ministério da Saúde o custeio das demais despesas do programa, exceto o
> auxílio moradia e alimentação.

| Item | Achado |
|---|---|
| Mesmos cortes? | **Sim** nos números (0,3 e 0,4). [V] |
| Mesma versão do IVS? | O texto diz "IPEA (2015), previsto na Portaria 485" — a 485 diz "publicado no Atlas da Vulnerabilidade Social (2015)". Que os valores do Atlas 2015 sejam os da Plataforma IVS usados em a08 é **[NÃO VERIFICADO]** para a 752; para a categoria administrativa do PMMB a coincidência é [V-dados] (§1). |
| Fronteira | Texto: `≥ 0,4` e `≥ 0,3` (classe de cima) [V]. Aplicação aos municípios sobre o corte: **[NÃO VERIFICADO]** (quadro de vagas por município em maismedicos.gov.br não arquivado). |
| O que muda | Teto de **novas vagas do PMMB na modalidade coparticipação**, como % das equipes de ESF: 10% → 40% em 0,3; 40% → 100% em 0,4 [V]. Do repasse do PAP do município é descontado **só o custeio mensal da bolsa**; o MS paga as demais despesas do programa, salvo auxílio moradia e alimentação, que ficam com o município (art. 3º e § 3º) [V]. O teto limita o que o município *pode* contratar nessa modalidade; não é transferência. Exceções que quebram a nitidez: equiparação ao inciso I (prefeito com teto abaixo da bolsa; G100) e vagas fora do limite (expansão dentro da PNAB, eCR, eAPP) [V]. |
| Vigência | Em vigor na publicação (19/06/2023) [V]; Edital SAPS 11/2023 (DOU 19/06/2023) abre a adesão "limitadas aos critérios da Portaria GM/MS nº 752" e o termo de adesão vale 96 meses [V]. |
| Ainda aplicada? | Os editais de municípios 3/2024 (DOU 15/05/2024) e 2/2025 (DOU 18/03/2025) citam a 752/2023 no preâmbulo e oferecem vagas "de financiamento federal ou de coparticipação" (3/2024, item 1.1) e "com financiamento federal e de coparticipação" (2/2025, preâmbulo) [V]. A Portaria 4.853/2024 suspende o desconto da 752 no RS nas parcelas 05 e 06/2024 [V], o que mostra a coparticipação em curso em 2024. Se o teto 10/40/100% ainda limita vagas **novas** em 2024–2026 é **[NÃO VERIFICADO]**: os editais não repetem os percentuais e os quadros não foram arquivados. Nenhum ato de revogação foi encontrado na busca do DOU por "752, de 15 de junho de 2023" (registro em `buscas_dou` no manifesto), o que não prova a vigência. |
| Timing | 2023-06: antes do pré-período do CNES e ~2 anos antes do ciclo 1. |
| Outcomes que pode mover | Médicos do PMMB em eSF (generalistas: CBO 225142, 225125, 225170), número de eSF, vagas de coparticipação. Especialistas: só indiretamente. Candidaturas ao PMM-E: não há canal direto; no máximo pela demanda municipal. |

### 2.2 Portaria GM/MS 485/2023 e 5.422/2024 — classes de IVS para priorizar vagas de provimento

**[V]** 485/2023, DOU 18/04/2023, art. 5º: "Para a priorização das vagas em
municípios será adotado como parâmetro o Índice de Vulnerabilidade Social -
IVS [...] publicado no Atlas da Vulnerabilidade Social (2015)", com classes
"alta: IVS maior ou igual a 0,4 e menor do que 0,5", "média: IVS maior ou
igual a 0,3 e menor do que 0,4", "baixa: IVS maior ou igual a 0,2 e menor do
que 0,3". O art. 2º, I, define "programas de provimento" como "o Programa
Mais Médicos, instituído e regulado pela Lei nº 12.871 [...] e respectiva
legislação superveniente e o Programa Médicos pelo Brasil". O art. 6º,
parágrafo único, diz quais equipes são válidas para o provimento: eSF de 40
horas e "outros arranjos prioritários" de atenção primária (eAP, eCR, eAPP,
equipes específicas) [V]. A 5.422/2024 (DOU 17/10/2024) muda o art. 5º para
"Atlas de Vulnerabilidade Social (2015) e suas eventuais atualizações" e
acrescenta como área prioritária "os municípios de perfil de muito alta
vulnerabilidade" [V].

- **Mesmos cortes:** sim (0,3 e 0,4, além de 0,2 e 0,5). Fronteira do texto:
  classe de cima.
- **O que muda:** a ordem de priorização das vagas de provimento. Como a
  priorização entra no dimensionamento é remetido a manual técnico e a
  publicações em maismedicos.gov.br — **[NÃO VERIFICADO]** (não arquivados).
- **Alcance sobre o PMM-E:** ver §2.8.
- **Timing:** desde 04/2023; a alteração de 10/2024 cai dentro do pré-período,
  mas mexe em 0,5 (muito alta), não em 0,3 ou 0,4.

### 2.3 Ajuda de custo e perfis de escolha do PMMB (PI MS/MEC 604/2023 e 7/2026)

**[V]** PI 604/2023 (DOU 18/05/2023), art. 24, caput: a ajuda de custo é
"destinada a compensar as despesas de instalação do médico participante que
não residir na localidade para o qual foi selecionado, desde que comprove a
mudança de domicílio". § 1º:

> I - Faixa 1 - municípios situados na região da Amazônia Legal, em região de
> fronteira ou em áreas indígenas e aqueles classificados como "vulnerabilidade
> social muito alta" [...]: concessão de ajuda de custo no valor de três
> bolsas-formação [...];<br>
> II - Faixa 2 - municípios classificados como "vulnerabilidade social alta"
> [...]: concessão de ajuda de custo no valor de duas bolsas-formação [...]; e<br>
> III - Faixa 3 - municípios classificados como "vulnerabilidade social média",
> "baixa vulnerabilidade social" e "muito baixa vulnerabilidade social" [...]:
> concessão de ajuda de custo no valor de uma bolsa-formação [...].

A PI 7/2026 (DOU 07/10/2026, Edição Extra B) revoga a 604/2023 (art. 52) e
mantém as três faixas (art. 7º, § 3º), agora "de acordo com o Índice de
Vulnerabilidade Social - IVS do [...] Ipea", sem citar o Atlas 2015, e com
"Faixa 3: demais municípios participantes do PMMB" [V].

**A 604 não dá número para "alta".** Ela nomeia classes ("vulnerabilidade
social alta", "muito alta") sem limites numéricos. Que "alta" comece em 0,4 é
**[INFERÊNCIA]** a partir das classes da 485/2023, que a 604 não cita.

**Perfis de escolha.** Os editais de médicos do PMMB 13/2023 (item 4.3),
4/2024 (item 5.7) e Conjunto SAPS/SGTES 7/2025 (item 6.7) distribuem os
locais "nos perfis de municípios, conforme Faixas estabelecidas no art. 24 da
Portaria Interministerial MS/MEC nº 604" [V]. O **Edital 5/2023 é diferente**:
o item 4.3 usa perfis "conforme Portaria GM/MS nº 485", e a Tabela 1 reparte a
Amazônia Legal entre os três perfis ("Amazônia Legal (42,6% dos municípios)"
no Perfil 1, "(21,5% ...)" no Perfil 2 e "(35% ...)" no Perfil 3), sem dizer
o critério [V]. Os editais de médicos (por exemplo, 5/2023, item 4.3.2, a, e
7/2025, regra para quem está em eSF, alínea a) restringem quem já está em eSF a
escolher municípios mais vulneráveis [V]:

> a) o médico que integrar eSF situada em município de determinado Perfil
> somente poderá indicar como municípios de alocação [...] opções de
> municípios classificados com maior grau de vulnerabilidade que o município
> da eSF a qual está vinculado;

| Item | Achado |
|---|---|
| Mesmos cortes? | **Só 0,400**, por inferência (média → alta: 1 → 2 bolsas-formação de ajuda de custo; perfil 3 → 2 nos editais que seguem a 604). **Não em 0,300**: média, baixa e muito baixa são todas Faixa 3 [V]. |
| Quem recebe | Só o médico que não reside no município e comprova mudança de domicílio [V]: o salto não alcança quem já mora lá. |
| Exceção | Para a **ajuda de custo**, Amazônia Legal, faixa de fronteira e áreas indígenas são Faixa 1 em qualquer IVS [V]. Para os **perfis de escolha**, isso só vale nos editais que seguem a 604; no Edital 5/2023 a Amazônia Legal está nos três perfis [V]. |
| Versão do IVS e fronteira | 604: "IVS do Ipea, publicado no Atlas da Vulnerabilidade Social, 2015"; limites numéricos e fronteira não definidos no ato. Como os quadros de vagas classificaram os municípios em 0,400 é **[NÃO VERIFICADO]**. |
| Valor da bolsa-formação do PMMB | **[NÃO VERIFICADO]** (ato da SAPS não arquivado). |
| Timing | 05/2023 em diante, sem mudança de regra até 10/2026: constante nas janelas pré e pós do CNES. |
| Outcomes | Atração e alocação de médicos do PMMB (generalistas) e fluxo de médicos de eSF entre municípios abaixo e acima de 0,400. Se alcança o PMM-E: ver §2.8. |

### 2.4 Indenização por área de difícil fixação (Lei 14.621/2023; SGTES 169/2025)

**[V]** Lei 14.621/2023, art. 19-A da Lei 12.871/2013: indenização de "20%
[...] se atuar em área de vulnerabilidade indicada em ato do Ministério da
Saúde" e "10% [...] se atuar nas demais áreas de difícil fixação". A 485/2023
(art. 8º, I) remete o enquadramento a ato da SAPS; a PI 10.032/2025 (DOU
31/12/2025) diz que as áreas "serão indicadas nos editais de chamamento
público de médicos" [V].

**[V]** Portaria SGTES/MS 169/2025 (DOU 31/12/2025), art. 4º, I: 20% "se atuar
em municípios classificados como muito alta vulnerabilidade com índice a partir
de 0,512 (quinhentos e doze milésimos)" e DSEI do Nordeste, Centro-Oeste e
Norte; art. 6º: 80% com "IVS maior do que 0,638" e 40% com IVS "de 0,512 [...]
a 0,638".

- **Mesmos cortes:** **não**. Os limites da 169/2025 são 0,512 e 0,638.
- **Quais áreas valeram de 2023 a 2025** (antes da 169/2025): indicadas nos
  quadros de vagas e em maismedicos.gov.br, segundo os editais 5/2023 (item
  4.2.1) e 13/2023 (item 10.10) [V]; a regra numérica desses quadros é **[NÃO
  VERIFICADO]**.

### 2.5 Cofinanciamento federal da APS: IED (Portaria GM/MS 3.493/2024; 7.799/2025)

**[V]** 3.493/2024 (DOU 11/04/2024), art. 9º, § 3º: "será utilizado o
Indicador de Equidade e Dimensionamento - IED, classificado nos estratos de 1 a
4, considerando a classificação dos municípios [...] de acordo com o Índice de
Vulnerabilidade Social - IVS, definido e calculado pelo [...] Ipea e o porte
populacional [...]". Art. 9º-B: componente fixo mensal por eSF de "RS
18.000,00" (estrato 1), "R$ 16.000,00" (2), "R$ 14.000,00" (3) e "R$ 12.000,00"
(4). Art. 8º: "efeitos financeiros a partir da parcela maio de 2024". O § 2º do
art. 9º diz que os componentes de vínculo e de qualidade "terão um valor mínimo
e máximo mensal que considera os estratos". A 7.799/2025 (DOU 21/08/2025)
rebatiza o componente fixo como "componente de equidade" e mantém o IED [V].

**[V-dados]** O Anexo VI da 3.493/2024 lista os municípios com código de
IVS (1 = muito alta … 5 = muito baixa), porte e estrato
(`output/aquisicao/a10_ied_aps_2024_municipio.csv`;
`ied_aps_3493_2024.municipios_anexo_vi`). Contra o IVS oficial:

- o código reproduz a classe do IVS 2010 oficial na convenção fechada à
  direita em todos os municípios com IVS oficial; 0,300 é "baixa" e 0,400 é
  "média", como na bolsa (`faixa_ivs_oficial_por_codigo`: código 3 vai de
  0,301 a 0,400; código 4, de 0,201 a 0,300);
- o estrato é função determinística de código de IVS × porte
  (`regra_deterministica = true`):

| Porte (IBGE 2022) | muito alta | alta | média | baixa | muito baixa |
|---|---:|---:|---:|---:|---:|
| 1 — até 20 mil | 1 | 2 | 3 | 3 | 4 |
| 2 — 20 a 50 mil | 1 | 2 | 3 | 4 | 4 |
| 3 — 50 a 100 mil | 2 | 3 | 3 | 4 | 4 |
| 4 — acima de 100 mil | 3 | 3 | 4 | 4 | 4 |

(estratos lidos de `estrato_ied_por_codigo_ivs_e_porte`).

| Item | Achado |
|---|---|
| Mesmos cortes, mesma versão, mesma fronteira? | **Sim nos três** [V-dados]. |
| Onde o estrato muda | Em **0,300** (baixa → média): porte 2 e 3 (estrato 4 → 3); **não** muda no porte 1 nem no 4. Em **0,400** (média → alta): porte 1 e 2 (3 → 2) e porte 4 (4 → 3); **não** muda no porte 3. Cada degrau de estrato vale R$ 2.000 por eSF por mês no componente fixo (diferença entre os valores do art. 9º-B). |
| Timing | Parcela de maio de 2024: **um mês antes do início do pré-período do CNES** (2024-06). |
| Outcomes | Equipes de eSF/eAP, médicos e enfermeiros da APS (generalistas). Especialistas: indireto. |
| Atenuante | Art. 12-T: compensação para quem perder recursos frente às últimas doze parcelas anteriores [V]; o efeito líquido no corte depende disso. |

### 2.6 Teto de emendas e de parcelas de custeio: "IVS maior que 0,3"

**[V]** Mesma regra em todos os atos abaixo, para o teto de **incremento
temporário de custeio** da APS (municípios) e da **média e alta complexidade**
(estados e municípios "que tiverem capacidade instalada na média e alta
complexidade"):

| Ato (DOU) | Exercício | Trecho |
|---|---|---|
| 3.283/2024 (08/03/2024) | 2024 | "Os Municípios que possuem indicador de vulnerabilidade social (IVS) maior que 0,3, terão um acréscimo de 20% (vinte por cento) ao limite de que trata o caput." (PAP); idem no art. 11, I, c (MAC) |
| 6.870/2025 (16/04/2025) e 6.904/2025 (29/04/2025) | 2025 | "IVS maior que 0,3, terão um acréscimo de 20%" (PAP e MAC) |
| 6.916/2025 (07/05/2025) | 2025, parcelas únicas | MAC, art. 7º, III; o art. 6º inclui "habilitação de Serviço da Atenção Especializada" |
| 8.283/2025 (01/10/2025) | 2026 (bancada e comissão) | "IVS maior que 0,3 [...] acréscimo de 20% [...] ao teto de que trata o §1º" (MAC) |
| 10.169/2026 (20/01/2026) | 2026, parcelas suplementares | art. 11, III (MAC); o art. 10 lista "ações do Programa Agora tem Especialistas - Componente Ambulatorial" e "- Componente Cirúrgico" |
| 10.297/2026 (02/03/2026) | 2026 (individuais) | "IVS superior a 0,3 farão jus a acréscimo de 20%" (PAP); "IVS superior a 0,3 e que possuírem capacidade instalada na Média e Alta Complexidade" (MAC) |
| 12.252/2026 (30/09/2026) | 2027 | idem (PAP e MAC) |
| 449/2023 (05/04/2023) | 2023 | **sem** a regra: o texto não contém "IVS" nem "vulnerabilidade social" (`termos_ausentes_conferidos`) |

| Item | Achado |
|---|---|
| Mesmos cortes? | **Só 0,300.** Não há regra em 0,400. |
| Fronteira | "maior que" / "superior a": 0,300 fica **fora**, como na bolsa [V]. |
| Versão do IVS | Não citada nos atos: **[NÃO VERIFICADO]**. |
| O que muda | O **teto** (valor máximo) de emendas e de parcelas de custeio, não o repasse. Se o teto é ativo para os municípios perto de 0,300 é **[NÃO VERIFICADO]** — depende dos valores indicados pelos parlamentares e das propostas, que não estão no repositório. Para a MAC, vale só com "capacidade instalada na média e alta complexidade" (critério não definido nos trechos arquivados). |
| Timing | Desde o exercício de 2024 (portaria de 03/2024), em todos os anos seguintes. Cobre o pré-período e o pós-período, com atos e montantes diferentes a cada ano. Em 2026 alcança recursos do Agora Tem Especialistas. |
| Outcomes | **Atenção especializada (MAC), inclusive especialistas e habilitações de serviços** — o mesmo alvo da F3 — e APS. É a ameaça mais direta à leitura da F3 em 0,300. |

### 2.7 Outras regras com faixas de IVS (menor alcance)

| Ato | Corte | Fronteira | O que muda | Timing | Ameaça |
|---|---|---|---|---|---|
| 5.721/2024 (DOU 18/11/2024), incentivo de alimentação e nutrição na APS | 0,3 e 0,4 ("De 0,3 a 0,399"; "De 0,4 a 0,499") [V] | classe de cima: as contagens do Quadro 2 coincidem com a convenção fechada à esquerda em baixa, alta e muito alta (`portaria_5721_2024_quadro_2`) [V-dados] | Valor adicional anual por município (Quadro 2 do ato), em "parcela única anual" [V] | regra publicada em 11/2024; datas de pagamento **[NÃO VERIFICADO]** | baixa: não financia médicos |
| 635/2023 (DOU 22/05/2023), eMulti | 0,2/0,3/0,4/0,5 (`IVS ³ 0,3 e < 0,4` no texto publicado) [V] | classe de cima | ordem de priorização do credenciamento de eMulti [V] | desde 05/2023 | média se a eMulti tiver médicos especialistas no CNES: composição **[NÃO VERIFICADO]** (está no Anexo XXII da PC 2, não arquivado) |
| 7.954/2025 (DOU 22/08/2025), Unidades Odontológicas Móveis | "IVS [...] alta ou muito alta" [V]; limite numérico não dado no ato (0,4 seria **[INFERÊNCIA]** pelas classes da 485) | não definida | um dos "critérios para a priorização das doações das UOM" (art. 80-C) [V] | desde 08/2025 | baixa: odontologia |
| 9.177/2025 (DOU 09/12/2025), Médicos pelo Brasil / Mais Médicos Eixo Vínculo | "municípios de alta e muito alta vulnerabilidade social" [V] | o ato não diz que índice usa. A Lei 13.958/2019, na redação da Lei 15.233/2025, define "locais de alta vulnerabilidade" por proporção de cadastrados com Bolsa Família, BPC ou benefício de até 2 salários mínimos, não pelo IVS [V]. Se a 9.177 usa o IVS (e o corte 0,4) é **[NÃO VERIFICADO]** | áreas de atuação de médicos especialistas em MFC ou clínica médica contratados pela AgSUS [V] | **12/2025, dentro do pós-período** | média para generalistas, **se** o critério for o IVS |
| Editais do Pró-Residência (ex.: SGTES 3/2024) | não há | — | IVS médio **por UF** e IVS do município só no desempate [V] | — | nula nos cortes municipais |
| 7.266/2025 (Agora Tem Especialistas) e 7.177/2025 (PMM-E) | não há | — | nenhum dos dois textos contém "IVS", "vulnerabilidade social" ou "485" (`termos_ausentes_conferidos`) [V] | — | — |

Atos que a busca no DOU mostrou com uso de IVS, mas que **não** foram
arquivados nem lidos por inteiro, e portanto ficam **[NÃO VERIFICADO]**: SUS
Digital (índice ICSD contínuo, sem corte, Portarias 3.233/2024, 4.160/2024 e
5.764/2024), Qualifar-SUS (4.986/2024), Plantas Medicinais (5.619/2024 e
6.837/2025), Programa Saúde na Escola (7.568/2025: "alta" e "muito alta" numa
medida-síntese), doença de Chagas (9.628/2025), Conselhos Locais de Saúde
(11.485/2026) e emendas de bancada de 2025 (6.928/2025).

### 2.8 As classes da 485/2023 valem para o PMM-E?

A pergunta importa porque, se valessem, a priorização das vagas do PMM-E
mudaria em 0,300 e 0,400 com o limite na classe de cima, ao contrário da
bolsa.

O que os textos dizem:

| Fonte | Trecho | Situação |
|---|---|---|
| 485/2023, art. 2º, I | "programas de provimento: o Programa Mais Médicos, instituído e regulado pela Lei nº 12.871 [...] e respectiva legislação superveniente" | [V] |
| Lei 15.233/2025, art. 22-D da Lei 12.871 | "Fica instituído, no âmbito do Programa Mais Médicos, o Projeto Mais Médicos Especialistas" | [V] |
| 7.177/2025, ementa | PMM-E "instituído no âmbito do Programa Mais Médicos" | [V] |
| 485/2023, art. 6º, parágrafo único | as equipes válidas para o provimento são eSF de 40 horas e outros arranjos da atenção primária | [V] |
| 485/2023, art. 3º | "Incumbe à Secretaria de Atenção Primária à Saúde realizar o dimensionamento detalhado com a distribuição do teto de vagas de provimento" | [V] |
| Lei 15.233/2025, art. 22-D, § 4º | adicional sobre a bolsa para quem atuar na Amazônia Legal, em territórios indígenas "ou em áreas com classificação socioeconômica de alta vulnerabilidade" | [V] (base legal do adicional da bolsa; não cita IVS nem a 485) |
| Lei 15.233/2025, art. 22-D, § 2º | os participantes do PMM-E "poderão fazer jus a bolsa-formação e demais benefícios do Projeto Mais Médicos para o Brasil" | [V] |

O que os atos do PMM-E usam para priorizar vagas:

- **Edital SGTES 2/2025 (gestores), item 3.1:** a priorização dos serviços e
  das vagas é deliberada na CIB; **item 3.8:** a distribuição dos especialistas
  observa "a baixa disponibilidade regional e distribuição desigual",
  o "fluxo dos usuários [...] entre os municípios de residência e ocorrência" e
  a "capacidade de escala e escopo" na região de saúde [V]. O texto não contém
  "485", "IVS" nem "vulnerabilidade social" [V].
- **7.177/2025, parágrafo único:** as especialidades seguem "critérios de baixa
  disponibilidade regional, escassez na oferta de serviços e distribuição
  desigual" [V].
- **Edital 3/2025 (ciclo 1), item 4.1.4:** a SGTES define "o quadro com as
  vagas priorizadas [...] de acordo com as pactuações regionais"; **item 5.7:**
  redistribuição de vagas não preenchidas "respeitando a priorização de
  localidades inseridas em regiões de saúde com maior dificuldade de acesso aos
  procedimentos ofertados e com comprovada escassez de médicos especialistas"
  [V]. Não cita a 485 [V]. O IVS aparece só no item 11.1.4, a faixa da bolsa
  [V].
- **Edital 28/2026 (ciclo 3), item 5.7:** mesma redação de priorização na
  redistribuição. Conferido por âncoras de texto no PDF via `pdftotext`, quando
  instalado (`ancoras_conferidas` no manifesto); o PDF não cita "485"
  (`termos_ausentes_conferidos`).

Leitura:

1. **Nenhum ato do PMM-E arquivado cita a Portaria 485/2023 nem usa as classes
   de IVS para priorizar ou distribuir vagas** [V]. Os critérios escritos são
   de escassez de especialistas, fluxo de pacientes, escala regional e
   pactuação em CIB.
2. **A 485 poderia, pelo texto, alcançar o PMM-E** (programas de provimento
   incluem o Mais Médicos "e respectiva legislação superveniente") — é uma
   leitura possível, **[INFERÊNCIA]** —, mas o art. 6º, parágrafo único,
   restringe as vagas a equipes da atenção primária, o que não é o caso do
   PMM-E. Se a SGTES usou as classes da 485 ao montar o quadro de vagas do
   PMM-E é **[NÃO VERIFICADO]**.
3. **A fronteira do PMM-E não é a da 485:** a faixa aplicada da bolsa põe 0,300
   e 0,400 na classe de baixo (§1, [V-dados]), o oposto do texto da 485.
4. **Benefícios do PMMB para o PMM-E.** Pelo § 2º do art. 22-D, os
   participantes do PMM-E "poderão fazer jus" aos benefícios do PMMB. Se isso
   inclui a ajuda de custo por faixa da 604 (salto em 0,400) é **[NÃO
   VERIFICADO]**. Os editais do PMM-E descrevem uma ajuda de custo própria, para
   as imersões nas instituições formadoras (retificação do Edital 3/2025 e
   Edital 28/2026), sem ligação com faixa de IVS no texto.
5. **Teste empírico possível sem abrir outcome de efeito:** a continuidade, em
   U, de "ter vaga no ciclo k" e do número de células nos cortes (F0.1 e F0.2
   do protocolo) é exatamente o diagnóstico de que a alocação de vagas do PMM-E
   não muda nos cortes. É ele que responde à pergunta.

## 3. Implicações para o estimando

| Corte | Muda além da bolsa — **verificado** | Muda além da bolsa — **não verificado ou inferido** | Contraste de uma RDD em nível |
|---|---|---|---|
| 0,300 | teto de emendas e parcelas PAP e MAC +20% (2024 em diante, mesma fronteira) [V]; estrato IED da APS nos portes 2 e 3 (05/2024 em diante, mesma fronteira) [V-dados]; texto da 752 (10% → 40% de teto de coparticipação, fronteira oposta) [V]; incentivo de nutrição (11/2024, fronteira oposta) [V-dados] | se e como a 752 foi aplicada no corte; ordem de priorização de eMulti (classe de cima no texto; efeito sobre médicos não verificado); uso das classes da 485 no quadro do PMM-E | **pacote**: bolsa + financiamento de MAC/APS + PMMB |
| 0,400 | estrato IED nos portes 1, 2 e 4 [V-dados]; texto da 752 (40% → 100%) [V]; incentivo de nutrição [V-dados] | ajuda de custo e perfis de escolha do PMMB (limite 0,4 inferido da 485); Eixo Vínculo (12/2025; índice não dito no ato); priorização de UOM (classe "alta" sem número); eMulti; aplicação da 752; ajuda de custo do PMMB a participantes do PMM-E | **pacote**: bolsa + APS + PMMB |

1. **F1 (candidaturas, preenchimento) e F2 (presença do especialista do
   PMM-E).** Nos atos arquivados, nenhuma regra além da bolsa paga ou
   restringe o especialista do PMM-E por faixa de IVS: 7.266/2025 e 7.177/2025
   não usam IVS nem citam a 485, e os editais do PMM-E priorizam vagas por
   escassez e pactuação regional [V]. Duas portas ficam abertas e **não
   verificadas**: a 485 alcançar o quadro do PMM-E (§2.8) e benefícios do PMMB
   (ajuda de custo por faixa) alcançarem o participante do PMM-E pelo § 2º do
   art. 22-D. A ameaça indireta continua: a demanda municipal (adesão, vagas
   pedidas) pode responder a tetos financeiros e a equipes da APS. Leitura:
   "efeito do anúncio de +R$ 5 mil, condicional ao pacote municipal do
   corte"; o diagnóstico F0 de seleção é obrigatório.
2. **F3 (oferta líquida de especialistas no CNES).** Em 0,300, o teto da MAC
   (+20%) mira o mesmo outcome. A RDD em nível em 0,300 **não** isola a bolsa.
3. **Placebo de generalistas (F3.P1).** É o outcome que 752, IED, ajuda de
   custo e, possivelmente, Eixo Vínculo movem. Um salto de generalistas no
   corte confirma o confundidor; a ausência de salto não exclui o canal da MAC,
   que mira especialistas.

### 3.1 A hipótese da DiRD

A DiRD do protocolo remove a parte da descontinuidade **constante** entre
pré (2024-06 a 2025-06) e pós (2025-10 a 2026-08). Pelos atos:

| Política | Constante entre pré e pós? |
|---|---|
| 752/2023 (teto de coparticipação) | regra constante desde 06/2023; o **estoque** de médicos de coparticipação pode continuar crescendo depois do pré (adesões e preenchimentos em ciclos sucessivos) — provavelmente **não** constante em nível |
| ajuda de custo / perfis do PMMB | regra constante de 05/2023 a 10/2026; efeito sobre estoque pode acumular |
| IED da APS | começa em 05/2024, logo antes do pré; efeito sobre equipes tende a crescer com o tempo — **não** constante |
| emendas e parcelas "IVS > 0,3" | regra presente nos dois períodos, mas atos, montantes e alvos mudam por ano; em 2026 inclui o Agora Tem Especialistas — **não** constante |
| Eixo Vínculo (9.177/2025) | só no pós; se o critério for o IVS, **viola** a hipótese em 0,400 para generalistas |
| nutrição (5.721/2024) | começa em 11/2024, dentro do pré |

Conclusão: a DiRD reduz o viés da parte fixa, mas **não** identifica a bolsa
pura em nenhum dos dois cortes. Ela identifica "bolsa + variação, entre pré e
pós, das descontinuidades das outras políticas". O placebo dentro do pré
(2024-06..2024-11 contra 2024-12..2025-05) também não é um nulo limpo: o IED
começou em 05/2024, a nutrição em 11/2024 e as emendas de 2025 em 04–05/2025.

### 3.2 Antes de 2023

Para saber se 2022-01 a 2023-03 é um trecho "limpo", foi feita a busca do DOU
por "Vulnerabilidade Social - IVS" e "Índice de Vulnerabilidade Social", ano a
ano de 2013 a 2022 (registro em `buscas_dou` no manifesto). Resultado:

- **Atos da saúde com IVS:** só as Portarias GM/MS 377/2022 (DOU 23/02/2022,
  incentivo temporário pós-covid) e 1.054/2022 (DOU 17/05/2022, Estratégia de
  Saúde Cardiovascular). Nas duas o IVS é **um dos indicadores** de um "índice
  de perfil municipal", cuja metodologia está em manual não arquivado [V]; o
  texto não traz corte em 0,3 ou 0,4. Se o índice composto salta nos cortes é
  **[NÃO VERIFICADO]**.
- **Sem IVS no texto:** Previne Brasil (Portaria 2.979/2019; vulnerabilidade
  por cadastro em Bolsa Família/BPC e tipologia rural-urbana do IBGE) e
  metodologia do Médicos pelo Brasil (Portaria 3.352/2021, republicada;
  "percentual da população vulnerável socioeconomicamente" e tipologia do
  IBGE) (`termos_ausentes_conferidos`) [V].
- **"maior que 0,3":** nenhuma ocorrência na saúde antes da Portaria
  3.283/2024 (busca de 2021 em diante).
- **Não buscado:** editais do PMM e do PMpB de 2013 a 2022 um a um, normas
  estaduais e municipais e atos que usem o IVS sem os termos buscados.

Leitura: 2022-01 a 2023-03 é anterior a **todas as regras com corte em 0,3 ou
0,4 encontradas**, mas contém dois incentivos que usam o IVS dentro de um
índice composto. Não é "sem nenhuma política ligada ao IVS".

## 4. O retrato do PMMB em a07 (para o outcome F0.4)

**[V-dados]** O arquivo é `data/raw/aquisicao/ivs_administrativo/ppf_mais_medicos_csv.zip`
(SHA-256 no diagnóstico, `esquema_consolidado_pmmb`). Do zip, a07 lê só
`nivel`, `co_ibge` e `categoria_ivs`. O CSV interno tem as colunas listadas em
`esquema_consolidado_pmmb.colunas` (`n_colunas`), um único `dt_referencia`
(2026-10-09) e linhas MUNICIPAL, ESTADUAL e DSEI; todos os municípios de a08
têm linha MUNICIPAL. Nenhum valor de vaga ou médico foi cruzado com o IVS.

Colunas úteis como co-intervenção, com a definição do dicionário de dados do
MS (versão de 13/07/2026, arquivado em
`data/raw/aquisicao/ivs_administrativo/Dicionario_de_dados_PPF_Mais_Medicos.pdf`):

| Coluna | Dicionário | Uso em E6 |
|---|---|---|
| `ativas_ff` | "Número de vagas ativas com financiamento federal exclusivo" | vagas federais |
| `ativas_coparticipacao` | "Número de vagas ativas com cofinanciamento (federal e municipal/estadual)" | **canal direto da 752/2023**: primeiro estágio do confundidor em 0,3 e 0,4 |
| `total_vagas_ativas` | "Vagas aderidas por meio de editais vigentes, confirmadas para ocupação [...]" | F0.4, vagas |
| `total_ocupadas` | "Vagas de provimento federal (PPF) atualmente ocupadas por profissionais em atividade no território (PMMB + Vagas de instituições vinculadas)" | F0.4, médicos ativos |
| `em_processo_ocupacao`, `total_desocupadas` | vagas em ocupação e desocupadas | decomposição |
| `ativos_crm_pmm`, `ativos_intercambista_pmm`, `ativos_bolsistas`, `ativos_celetista_mfc`, `ativos_tutores` | perfis (CRM Brasil, intercambista, bolsista e celetista MFC da AgSUS, tutor) | `ativos_celetista_mfc` ≈ Eixo Vínculo (9.177/2025) |
| `ativos_esf`, `ativos_emsi`, `ativos_eapp`, `ativos_ecr` | profissionais ativos por tipo de equipe | eSF é o alvo da 752 |
| `equipe_esf`, `equipe_emsi`, `ampliacao_ecr`, `ampliacao_eapp` | equipes e vagas de ampliação | contexto |
| `cobertura` | cobertura de equipes de APS "considerando a população estimada e parâmetros da PNAB" | contexto |
| `amazonia_legal`, `faixa_fronteira`, `categoria_ivs` | atribuição | estratificação (Faixa 1 da ajuda de custo) |

Cuidados para E6, antes de olhar valores por corte:
- **Nomes divergem do dicionário.** O CSV tem `co_ibge`, `ampliacao_ecr`,
  `ampliacao_eapp`, `ativos_bolsistas`, `ativos_celetista_mfc` e
  `ativos_tutores`; o dicionário fala em `ibge`, `equipe_ecr`, `equipe_eapp`,
  `ativos_bolsista_vin...`, `ativos_celetista_vin...` e `ativos_tutor_vincul`.
  As identidades (por exemplo, `total_vagas_ativas` = `ativas_ff` +
  `ativas_coparticipacao`; `total_ocupadas` contra a soma dos perfis) devem
  ser conferidas no total nacional, sem quebra por IVS, pelo script de
  construção.
- **Colunas constantes.** `nac_brasileiro`, `nac_cubano`, `nac_boliviano` e
  `nac_venezuelano` têm um único valor distinto em todas as linhas, e
  `nac_outros` tem tantos valores distintos quanto `total_ocupadas`
  (`valores_distintos_por_coluna`, contado no arquivo inteiro). As colunas de
  nacionalidade não devem ser usadas.
- **É um retrato pós-tratamento** (09/10/2026): mede o estoque acumulado de
  todas as políticas desde 2013, não um fluxo do ciclo 1. Serve para F0
  (diagnóstico do confundidor), não para DiRD.
- **Série no tempo.** O mesmo dicionário documenta uma tabela "Serie
  Historica_PMM_APS" (profissionais por município e competência). Ela permitiria
  um estudo de evento do PMMB desde antes de 06/2023, mas não está no
  repositório; URL e cobertura **[NÃO VERIFICADO]**.

## 5. Recomendações para E6 e E7

Todas usam só regras fixadas antes de olhar outcomes; o que não está no
protocolo 40 entra como análise **suplementar rotulada**, sem substituir as
especificações congeladas. O adendo S1–S6 do protocolo 40 já incorpora a
maior parte.

1. **Nomear o contraste.** Em todo resultado em nível: "pacote do corte".
   Na DiRD: "bolsa + variação das outras descontinuidades". Nenhum resultado
   deve ser chamado de efeito da bolsa pura.
2. **F0.4 como primeiro estágio do confundidor (E6).** Rodar a RDD em
   `ativas_coparticipacao`, `total_vagas_ativas` e `total_ocupadas` por 10 mil
   habitantes, em U, nos dois cortes. Salto em `ativas_coparticipacao` = a 752
   operou no corte.
3. **F0.1 e F0.2 respondem à §2.8.** Continuidade de "ter vaga" e de células
   no corte é a evidência de que a alocação de vagas do PMM-E não usa as
   classes de IVS; salto ali muda a leitura de F1 e F2.
4. **Donut nos pontos de massa (E6 e E7).** Sensibilidade excluindo os
   municípios com IVS exatamente igual a 0,300 e a 0,400 (contagens em
   `municipios_sobre_os_limites`): é ali que os atos com fronteira "≥" e os com
   "≤"/"maior que" divergem.
5. **Heterogeneidade pelo porte, que o IED prevê (E7, suplementar).** Em
   0,300, o estrato IED muda só nos portes 2 e 3; em 0,400, nos portes 1, 2 e
   4 (tabela da §2.5, lida do JSON). Se o salto de generalistas aparece só onde
   o estrato muda, o canal é o IED. É uma diferença em descontinuidades entre
   portes, com o porte do próprio Anexo VI (IBGE 2022, pré-tratamento).
6. **Amazônia Legal e fronteira (E6/E7, suplementar).** Nelas a **ajuda de
   custo** do PMMB é Faixa 1 em qualquer IVS: em 0,400 o salto da ajuda de
   custo some ali. Isso não vale com certeza para os **perfis de escolha**: no
   Edital 5/2023 a Amazônia Legal está repartida entre os três perfis. A
   comparação dentro × fora isola só o canal da ajuda de custo dos editais que
   seguem a 604. Atenção: as emendas MAC também dão +30% à Amazônia Legal,
   cumulativo.
7. **Estudo de evento desde 2022-01, com as datas marcadas (E7).** Linhas
   verticais em 2023-04 (485), 2023-05 (604, 635), 2023-06 (752), 2024-03
   (emendas 2024), 2024-05 (IED), 2024-11 (nutrição), 2025-04/05 (emendas e
   parcelas de 2025), 2025-07 (ciclo 1 do PMM-E), 2025-12 (Eixo Vínculo),
   2026-01 (parcelas do Agora Tem Especialistas). A janela 2022-01 a 2023-03 é
   anterior a todas as regras com corte em 0,3 ou 0,4 encontradas na busca do
   DOU de 2013 a 2022 (§3.2), mas contém as Portarias 377/2022 e 1.054/2022,
   que usam o IVS dentro de índice composto. Reportar a DiRD também com pré =
   2022-01 a 2023-03, como sensibilidade suplementar, com essa ressalva.
8. **Placebos de outcome.** Manter F3.P1 (generalistas) e F3.P2; acrescentar,
   como suplementar, contagem de eSF (canal 752/IED) se o painel C trouxer
   equipes. O CBO 225130 (médico de família e comunidade), perfil do Eixo
   Vínculo, não está na lista F3.P1; incluí-lo exige registro como desvio
   antes de abrir o outcome.
9. **Canal da MAC em 0,300.** A ameaça mais séria à F3 não tem outcome no
   protocolo. Recomenda-se adquirir (dado público) os repasses fundo a fundo
   do FNS por município e ano (emendas e parcelas de custeio de MAC e PAP) e
   testar o salto em 0,300 como primeiro estágio do confundidor, antes de
   interpretar a F3 nesse corte. Sem isso, F3 em 0,300 fica rotulada como
   pacote.
10. **Funil do PMM-E (F1).** Registrar como limite que a demanda municipal
    (adesão do ciclo 3, vagas pedidas — F0.3) pode responder aos tetos
    financeiros dos dois cortes.

## 6. Limites e pendências

- Quadros de vagas do PMMB por município (teto da 752, faixas, áreas de
  indenização de 2023–2025) não foram arquivados: a aplicação administrativa
  da 752 e da 604 sobre os municípios exatamente nos cortes
  (`totais.sobre_os_cortes_da_bolsa`) é **[NÃO VERIFICADO]**.
- Se o teto de +20% das emendas e parcelas é ativo perto de 0,300 é **[NÃO
  VERIFICADO]**.
- O Edital 28/2026 é um PDF adquirido por a03: o script confere o hash e, se
  houver `pdftotext`, as âncoras de texto e a ausência de "485"; sem
  `pdftotext`, a afirmação da §2.8 sobre esse edital depende de leitura manual.
- A página da 752/2023 na BVS-MS respondeu HTTP 403 e o PDF da 485/2023 da
  SES-MT teve a conexão encerrada (`nao_preservados` no manifesto); as duas
  normas foram lidas no DOU.
- Reprodutibilidade: as páginas do DOU e do Planalto mudam bytes do cabeçalho
  a cada acesso. O script confere o cache pelo `sha256_bruto` e um download
  novo pelo `sha256_texto` (texto do ato); se o órgão alterar o texto
  publicado, o script para.
- A busca no DOU foi por termos (`buscas_dou`). Atos que usam o IVS sem esses
  termos podem ter ficado de fora; normas estaduais e municipais não foram
  buscadas.
