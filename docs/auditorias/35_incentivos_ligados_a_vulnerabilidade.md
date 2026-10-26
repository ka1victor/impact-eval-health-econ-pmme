# Incentivos educacionais e financeiros ligados à vulnerabilidade do município

> **Execução:** 2026-10-26. É uma pesquisa documental: nada foi estimado. Ela
> complementa a auditoria [`18`](18_politicas_nos_mesmos_cortes_ivs.md) sem
> refazê-la e alimenta o item G-f do protocolo
> [`62`](../06_execucao/62_protocolo_gradiente_dentro_das_faixas.md) e o D-g do
> [`61`](../06_execucao/61_protocolo_diagnostico_queda_0300.md).<br>
> **Pergunta do autor:** existe algum incentivo educacional ou financeiro ligado
> à vulnerabilidade do município (IVS ou critério parecido) que mude a escolha
> ou o preenchimento das vagas de médicos especialistas? Ele poderia explicar a
> queda do preenchimento no corte 0,300 ou a subida do preenchimento ao longo do
> IVS dentro das faixas da bolsa?<br>
> **Resposta curta:** nos atos lidos, **nenhum** incentivo individual além da
> bolsa alcança o especialista do PMM-E por faixa de IVS. Também não há nenhum
> que mude em 0,300 nem nenhum que varie de forma contínua com o IVS.
> - Os incentivos territoriais ativos em 2025–2026 com corte de IVS mudam em
>   **0,400** (incentivo por localidade da AgSUS, de R$ 3 mil por mês, e ajuda
>   de custo do PMMB) ou em **0,512 e 0,638** (indenizações do PMMB, inclusive a
>   do Fies). Todos pagam médicos da atenção primária.
> - O abatimento do Fies usa uma lista de municípios definida por extrema
>   pobreza e população rural, e não o IVS. Ele vale só para médicos de eSF.
> - O bônus de 10% na residência deixou de existir para participantes de
>   programas de provimento.
> - O único benefício do PMM-E além da bolsa que varia com o território é a
>   **ajuda de custo das imersões** (R$ 5 mil ou R$ 2,5 mil por imersão), que
>   depende da **distância até a instituição formadora**, e não do IVS.
>
> No nível municipal, o pacote de 0,300 da auditoria 18 continua sendo o único
> candidato documental para esse corte.<br>
> **Fontes:** as cópias estão em
> [`output/aquisicao/normas_incentivos/`](../../output/aquisicao/normas_incentivos/).
> O manifesto
> [`a18_manifesto_normas_incentivos.json`](../../output/aquisicao/normas_incentivos/a18_manifesto_normas_incentivos.json)
> registra URL, data de acesso, data de publicação, SHA-256 e as âncoras de
> texto conferidas. As normas já arquivadas em `data/raw/aquisicao/` só foram
> lidas e entram no mesmo manifesto pelo hash. Script:
> [`scripts/aquisicao/a18_normas_incentivos_vulnerabilidade.py`](../../scripts/aquisicao/a18_normas_incentivos_vulnerabilidade.py).
> Se uma âncora citada aqui não estiver no texto, o script para.<br>
> **Outcomes abertos:** nenhum. A única leitura de dado do PMM-E foi o
> cabeçalho dos quadros de vagas (coluna `FAIXA DE ATRAÇÃO`, variável de
> atribuição).

Convenção, a mesma da auditoria 18:

- **[V]**: verificado no texto do ato preservado. O trecho tem âncora conferida
  pelo a18, ou, nos PDFs sem camada de texto, foi lido na página indicada
  (`conferencia = "visual"`).
- **[INFERÊNCIA]**: conclusão que combina dois ou mais textos verificados.
- **[NÃO VERIFICADO]**: fonte secundária, documento não preservado ou ponto que
  não foi possível conferir.

Classes de IVS citadas abaixo: a Portaria GM/MS 485/2023 define "média" como
IVS ≥ 0,3 e < 0,4, "alta" como ≥ 0,4 e < 0,5 e "muito alta" como ≥ 0,5. O
texto [V] está na auditoria 18, §2.2. A bolsa aplica os limites 0,300 e 0,400
com o valor do limite na classe de baixo (auditoria 18, §1).

## 1. Tabela-resumo

| # | Incentivo | Ato e data | Critério territorial | Quem recebe | Alcança especialista do PMM-E? | Vigente em 2025–2026 | Muda em 0,300? | Muda em 0,400? | Contínuo no IVS? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Abatimento do Fies (1% do saldo ou até 50% da parcela) | Lei 10.260/2001, arts. 6º-B, II, e 6º-F; Portaria Conjunta SGTES/SAS 3/2013 | **lista de municípios** (extrema pobreza e população rural) e setores 20% mais pobres; **não usa IVS** | médico de eSF (ou militar) com Fies | **não**: exige eSF de 40 h [V] | sim (FAQ do MS atualizado em 08/09/2026) [V] | não | não | não |
| 1b | Carência estendida do Fies | Lei 10.260, art. 6º-B, § 3º | **nenhum**: depende da especialidade | residente em especialidade prioritária | não: é para quem ainda está na residência | sim [V] | não | não | não |
| 2 | Indenização do PMMB e indenização diferenciada para quem tem Fies | Lei 12.871, arts. 19-A e 19-B; Portaria SGTES 169/2025 (DOU 31/12/2025) | IVS ≥ 0,512 e > 0,638, DSEI e região | médico do **PMMB** com 12 a 48 meses | **não**: a portaria vale "no âmbito do PMMB" [V] | sim, 90 dias após a publicação [V] | não | não | não (degraus em 0,512 e 0,638) |
| 3 | Bônus de 10% na prova de residência | Lei 12.871, art. 22, § 2º (revogado pela Lei 15.233/2025); art. 22-E; Portaria MEC 446/2026 | **nenhum** | só quem concluiu residência em MFC | **não**: o bônus por programa de provimento é vedado [V] | o bônus do PMM/Provab acabou em 10/2025 [V] | não | não | não |
| 4 | Incentivo por localidade da AgSUS (Eixo Vínculo e Estratégico) | Lei 13.958, art. 25, § 2º; Resoluções CDA 21/2025 e DIREX 37/2025 | IVS **"alta e muito alta"**, pelas classes da Portaria 485/2023; rural remoto (IBGE); DSEI | MFC e tutor contratados (CLT) pela AgSUS, na APS | **não** [V] | desde 06/05/2025 [V] | não | **sim**: R$ 0 → R$ 3.000 por mês [INFERÊNCIA: a DIREX remete à 485] | não |
| 5 | Ajuda de custo das imersões do PMM-E | Retificação do Edital 3/2025 (DOU 28/10/2025); Editais 3/2026 e 28/2026, item 11.1; Manual do PMM-E (12/2025) | **distância** até a instituição formadora: só formadora da rede Ebserh, com o serviço a mais de 50 km; níveis de R$ 5.000 e R$ 2.500 por imersão | especialista do PMM-E | **sim** | sim [V] | não | não | não pelo IVS; muda com a distância |
| 6 | Outros itens dos editais do PMM-E (barema, desempate, cotas, cumulação) | Editais 3/2025, 3/2026 e 28/2026; Portaria 7.177/2025 | desempate pela **UF** de domicílio ou de nascimento; sem IVS | candidatos | sim | sim [V] | não | não | não |
| 7 | Ajuda de custo e perfis de escolha do PMMB (já na auditoria 18) | PI 604/2023 e PI 7/2026 | classes de IVS; Amazônia Legal, fronteira e áreas indígenas | médico do PMMB | não: a PI 7/2026 não cita o PMM-E [V] | sim | não | sim (auditoria 18) | não |
| 8 | Pró-Residência (bolsas de residência) | Edital SGTES 6/2025 (DOU 18/09/2025) | Amazônia Legal; NE e CO; UF com poucos especialistas; IVS+IDH **por UF** e IVS do município da instituição só no desempate | programa de residência (bolsa do residente) | **não**: forma especialistas, não os aloca | sim [V] | não | não | só no desempate (ordenação) |
| 9 | Auxílio-moradia e auxílio-alimentação pagos pelo município | PI 7/2026; leis municipais (ex.: João Monlevade 2.581/2023) | **nenhum**: valor fixado por cada município | médico do PMMB | **não**: o termo de adesão do PMM-E não traz essa obrigação [V] | sim | não | não | não |
| 10 | Complemento estadual ou municipal para especialistas com base no IVS | — | — | — | **nada encontrado** | — | — | — | — |
| 11 | Compra de serviços especializados do Agora Tem Especialistas (modalidades 2 e 3) | Portaria 7.266/2025, art. 16 | "áreas de difícil provimento" (unidades móveis); sem IVS | empresas e prestadores credenciados | concorre pelas horas do especialista | sim [V] | não | não | não |
| 12 | Teto de emendas e parcelas MAC e PAP (+20%) (auditoria 18) | Portarias 3.283/2024 a 12.252/2026 | "IVS maior que 0,3" | estado e município (não o médico) | indireto | sim | **sim** (auditoria 18) | não | não |

## 2. Incentivo por incentivo

### 2.1 Fies: abatimento por atuação em área prioritária (FIESMED)

**[V]** Lei 10.260/2001, art. 6º-B, texto compilado do Planalto:

> II - médico integrante de equipe de saúde da família oficialmente cadastrada
> ou médico militar das Forças Armadas, com atuação em áreas e regiões com
> carência e dificuldade de retenção desse profissional, definidas como
> prioritárias pelo Ministério da Saúde, na forma do regulamento.

> § 7º Somente farão jus ao abatimento mensal referido no caput deste artigo os
> financiamentos contratados até o segundo semestre de 2017.

Para contratos a partir de 2018, o art. 6º-F prevê abater "até 50% (cinquenta
por cento) do valor mensal devido" pelos financiados do inciso II [V]. O § 3º do
art. 6º-B estende a carência por toda a residência "em especialidades
prioritárias definidas em ato do Ministro de Estado da Saúde" [V].

**[V]** FAQ do FIESMED (gov.br/saude, publicado em 19/11/2025 e atualizado em
08/09/2026). A base legal citada é a Portaria GM/MS 1.377/2011, a Portaria
203/2013, a Portaria Conjunta SGTES/SAS nº 3/2013 e a Portaria Normativa MEC
7/2013. Elegibilidade:

> atuou ininterruptamente por um período de 12 meses em equipes da Estratégia
> de Saúde da Família (eSF) e equipes para populações específicas

O cálculo usa "Código Brasileiro de Ocupação (CBO) para médicos", "Vínculo com
o SUS em equipes da Estratégia Saúde da Família", carga mínima de 40 h e
"Atuação nos municípios definidos como prioritários pelo Ministério da Saúde".

**[NÃO VERIFICADO no ato]** Portaria Conjunta SGTES/SAS 3/2013 (DOU
20/02/2013). A BVS-MS respondeu HTTP 503, e o texto foi lido na reprodução
integral do CONASS (CI n. 30/2013), arquivada:

> § 1º A definição das áreas e regiões prioritárias de que trata o "caput" foi
> realizada considerando-se os seguintes critérios: I – percentual da população
> em extrema pobreza; e II – percentual da população residente na área rural.

O § 2º admite ainda eSF de populações específicas e eSF em setores censitários
"que compõem os 20% (vinte por cento) mais pobres do Município". A lista está
no Anexo I, que não foi arquivado.

| Item | Achado |
|---|---|
| Critério territorial | lista de municípios de 2013 (extrema pobreza e ruralidade), mais exceções intramunicipais. **Não usa IVS** [V no FAQ; texto da Portaria Conjunta NÃO VERIFICADO no DOU]. |
| Alcança especialistas? | **Não** para o especialista do PMM-E: exige vínculo em eSF de 40 h [V]. A carência estendida beneficia quem ainda está na residência, não quem vai para a atenção especializada. |
| 0,300 / 0,400 / contínuo | não, não, não. A lista é binária e definida por outros indicadores. Se os municípios da lista se concentram acima de algum corte de IVS é **[NÃO VERIFICADO]**, porque o Anexo I não foi arquivado. |
| Vigência | em vigor (FAQ de 09/2026) [V]. |

### 2.2 Indenizações do PMMB, inclusive a do Fies (Lei 12.871, arts. 19-A e 19-B)

A auditoria 18 (§2.4) registrou os limites 0,512 e 0,638. O que este documento
acrescenta: a faixa de 80% / 40% do art. 6º da Portaria SGTES 169/2025 é a
**indenização diferenciada para quem tem Fies** (art. 19-B). Ela substitui a
indenização comum e é paga em parcelas a partir de 12 meses [V]:

> II - por atuação do médico no PMMB por atuação em área de difícil fixação que
> tiver realizado graduação em medicina financiada pelo Fundo de Financiamento
> Estudantil - Fies [...] em substituição à indenização prevista no art. 19-A

- **Limites:** "IVS maior do que 0,638" (80%) e "de 0,512 [...] a 0,638" (40%),
  mais DSEI [V]. Nenhum limite em 0,300 ou 0,400.
- **Alcance:** a portaria "define as regras [...] no âmbito do Projeto Mais
  Médicos para o Brasil - PMMB" [V]. O § 2º do art. 22-D da Lei 12.871 diz que
  os participantes do PMM-E "poderão fazer jus a bolsa-formação e demais
  benefícios do Projeto Mais Médicos para o Brasil" [V]. Mesmo assim, nenhum
  ato lido estende as indenizações ao PMM-E, cuja ação formativa dura até 12
  meses [V, item 11.1 dos editais].
- **Vigência:** "entra em vigor em 90 (noventa) dias após a data de sua
  publicação" (DOU de 31/12/2025) [V].

### 2.3 Bônus na prova de residência (Provab, Mais Médicos, Médicos pelo Brasil)

**[V]** Lei 12.871, art. 22, § 2º, no texto compilado: "receberá pontuação
adicional de 10% (dez por cento) na nota de todas as fases [...] dos Programas
de Residência Médica", marcado "(Revogado pela Lei nº 15.233, de 2025)", assim
como os §§ 3º e 4º. A Lei 15.233 (DOU de 08/10/2025) acrescentou o art. 22-E,
que dá o bônus a quem "tiver concluído a Residência em Medicina de Família e
Comunidade", e o art. 22-F, que dá ao MEC a regulamentação das
"bonificações concedidas por programas de provimento" [V].

**[V]** Portaria MEC 446, de 19/05/2026 (DOU 20/05/2026, Seção 1, p. 27):

> Art. 2º Fará jus à pontuação adicional ou bonificação de 10% (dez por cento)
> o candidato que houver concluído Programa de Residência Médica em Medicina de
> Família e Comunidade - PRMFC [...]

> § 1º É vedada a concessão de pontuação adicional fundada exclusivamente em:
> I - participação em programas de provimento; II - participação em projetos,
> ações estratégicas ou políticas públicas governamentais; [...]

O art. 8º aplica a portaria aos processos seletivos com edital publicado depois
de 20/05/2026 [V].

- **Critério territorial:** nenhum.
- **Alcance sobre o PMM-E:** nulo. O participante já é especialista com RQE, e
  a participação em programa de provimento deixou de dar pontos [V].
- **Fora do escopo verificado:** a Resolução CNRM 6/2026, que alinharia a CNRM
  à portaria, e o PL 2689/2024, que devolveria o bônus aos participantes do
  Mais Médicos, só apareceram em fontes secundárias [NÃO VERIFICADO].

### 2.4 Médicos pelo Brasil / AgSUS: incentivo por localidade

**[V]** Lei 13.958/2019, art. 25, § 2º (redação da Lei 14.621/2023): a
remuneração é "acrescida de incentivo financeiro diferenciado e variável, de
modo a incentivar o provimento de médicos nos Municípios e localidades mais
distantes dos centros urbanos ou naqueles com maior vulnerabilidade". O art.
2º, III, na redação da Lei 15.233, define "locais de alta vulnerabilidade" pela
"alta proporção de pessoas cadastradas nas equipes de saúde da família e que
recebem benefício financeiro do Programa Bolsa Família, benefício de prestação
continuada ou benefício previdenciário no valor máximo de 2 (dois) salários
mínimos". **Não usa o IVS.**

**[V]** A Resolução CDA/AgSUS 21/2025 (assinada em 06/05/2025, Plano de Cargos
e Salários) adota outro critério:

> XII - locais de difícil provimento médico e de alta vulnerabilidade:
> municípios classificados como de alta ou muito alta vulnerabilidade pelo
> IPEA; municípios classificados como rurais e remotos pelo IBGE; distritos
> sanitários especiais indígenas; [...]

O art. 24 diz que os incentivos "não serão cumulativos" [V].

**[V]** A Resolução DIREX/AgSUS 37/2025 (assinada em 29/05/2025, "com efeitos
retroativos a 6 de maio de 2025") fixa o salário-base de MFC em R$ 15.750,00 e
o incentivo por localidade:

> V - o valor do incentivo de localidade destinado aos profissionais alocados
> em Municípios de alta e muito alta vulnerabilidade social (IVS) será de R$
> 3.000,00 (três mil reais).

O mesmo valor de R$ 3.000 vale para "rural remoto (IBGE)", DSEI Padrão e Sede
DSEI; o DSEI Prioritário recebe R$ 6.000 [V]. O parágrafo único remete a
classificação dos municípios à "Portaria GM/MS nº 485, de 14 de abril de 2023"
[V].

| Item | Achado |
|---|---|
| Corte | **0,400** [INFERÊNCIA]: a DIREX remete à 485, e na 485 "alta" começa em IVS ≥ 0,4 [V na auditoria 18]. Não há corte em 0,300 ("média" não recebe). |
| Fronteira e versão | Texto da 485: "maior ou igual" (0,400 na classe de cima) e IVS do Atlas 2015. Se a lista aplicada pela AgSUS põe 0,400 em cima ou embaixo é **[NÃO VERIFICADO]**. |
| Quem recebe | MFC e tutor médico contratados pela AgSUS (Eixos Vínculo e Estratégico), em equipes da APS [V]. O tutor pode ser especialista em clínica médica (Lei 13.958, art. 25, § 1º, II) [V], mas trabalha na APS. |
| Alcance sobre o PMM-E | nenhum direto. A errata do Edital 3/2026 veda a participação no PMM-E de quem está ativo no PMMB e no PMM-E [V]; a vedação a contratados da AgSUS **não** aparece no texto lido. |
| Vigência | desde 06/05/2025, dentro das janelas do PMM-E [V]. A regra de transição (arts. 6º e 7º) mantém o incentivo para quem está em local que deixou de ser prioritário [V]. |
| Nota | A Lei 13.958 define alta vulnerabilidade pelo Bolsa Família e BPC; o regulamento da AgSUS usa as classes de IVS do Ipea. As duas definições divergem [V]. |

O valor do incentivo em 2021–2024 (editais da Adaps) não foi pesquisado.

### 2.5 PMM-E: o que existe além da bolsa

**Ajuda de custo das imersões.** **[V]** A retificação do Edital 3/2025 (DOU
28/10/2025) e o item 11.1.1 dos Editais 3/2026 (ciclo 2, lido na p. 20) e
28/2026 (ciclo 3) dizem:

> Os médicos também farão jus ao recebimento de ajuda de custo, exclusivamente
> durante a participação nas atividades de aprimoramento, para auxiliar nas
> despesas relacionadas à participação nas imersões presenciais das
> instituições formadoras às quais estão vinculados. O pagamento da ajuda de
> custo será realizado em parcela única para cada ciclo de imersão [...]

**[V]** O Manual de Implementação e Execução do PMM-E (versão preliminar, PDF
de 30/12/2025, p. 31; os valores foram lidos na imagem da página porque o texto
extraído os perde) diz:

> O valor da ajuda de custo foi definido conforme critérios de localização e
> distância entre o serviço ao qual o(a) médico(a) especialista está
> alocado(a) e a respectiva instituição formadora, estabelecendo-se dois
> níveis: Nível 1: R$ 5.000,00 (cinco mil reais); Nível 2: R$ 2.500,00 (dois
> mil e quinhentos reais)

> Fará jus à ajuda de custo o(a) médico(a) especialista que têm como
> instituição formadora hospitais integrantes da rede Ebserh, cuja unidade de
> alocação esteja situada a mais de 50km de distância da instituição formadora.

Quem tem formadora do Proadi-SUS não recebe a ajuda de custo, porque o projeto
custeia deslocamento, hospedagem e alimentação [V]. A regra que separa os
níveis 1 e 2 não é dada [NÃO VERIFICADO]. O número de imersões por ciclo também
não foi encontrado [NÃO VERIFICADO].

| Item | Achado |
|---|---|
| Critério | distância até a formadora (> 50 km) e "localização"; só formadoras da Ebserh. **Não usa IVS** [V]. |
| Muda em 0,300 / 0,400? | não. |
| Contínuo no IVS? | não. Varia com a geografia (distância à formadora), que pode estar correlacionada com o IVS **[NÃO VERIFICADO]**. |
| Ordem de grandeza | por imersão, de R$ 2,5 mil a R$ 5 mil, contra uma bolsa de R$ 10 a 20 mil por mês [V]. |
| Timing | instituída pela retificação de 28/10/2025, **depois** da escolha das vagas do ciclo 1 [INFERÊNCIA: o Edital 3/2025 é de 24/07/2025]. Nos ciclos 2 e 3 já constava do edital [V]. |

**Outros itens dos editais** (ciclo 1: Edital 3/2025; ciclo 2: Edital 3/2026,
lido nas pp. 1, 9, 10, 20 e 21; ciclo 3: Edital 28/2026):

- **Barema [V]:** a pontuação vem só de titulação (2 pontos por residência ou
  por título, até 6) e de tempo de formação (até 3). Não há ponto territorial.
- **Desempate [V]:**
  - ciclo 1: "mesma UF do seu domicílio de residência ou do seu local de
    nascimento";
  - ciclos 2 e 3: primeiro a UF de domicílio, depois a UF de nascimento, depois
    a idade.

  É um critério de **UF**, sem IVS.
- **Cotas [V]:** 20% para negros, indígenas e quilombolas e 6% para pessoas com
  deficiência (ciclo 1). Não há critério territorial.
- **Redistribuição [V]:** vagas não preenchidas vão a municípios em cadastro de
  reserva, "respeitando a priorização de localidades inseridas em regiões de
  saúde com maior dificuldade de acesso aos procedimentos ofertados e com
  comprovada escassez de médicos especialistas" (item 5.7 nos três ciclos). Já
  estava na auditoria 18, §2.8.
- **Bolsa nos ciclos 2 e 3 [V]:** o texto passa a dizer que "o valor fixo da
  bolsa é de R$ 10.000,00 [...] acrescido um valor variável de R$ 5.000,00 [...]
  até R$ 10.000,00 [...] a depender da faixa de atratividade". As classes ficam
  "muito alta ou alta" → R$ 20 mil, "média" → R$ 15 mil, "baixa ou muito
  baixa" → R$ 10 mil. É a grade aplicada desde o ciclo 1 (auditoria 16, §2). O
  texto do ciclo 1 descrevia a grade um degrau abaixo.
- **Cumulação [V]:** a Portaria 7.177/2025, art. 3º, § 3º, diz: "As bolsas
  concedidas poderão ser cumuladas com outras atividades remuneradas". A carga
  do projeto é de 20 h semanais (item 11.3, b).
- **Obrigações do ente [V]:** o Termo de Adesão do ciclo 3 (Edital 25/2026,
  cláusula terceira) não prevê auxílio-moradia nem auxílio-alimentação, ao
  contrário do PMMB.
- **Adicional da lei [V]:** o art. 22-D, § 4º, da Lei 12.871 prevê adicional
  para "Amazônia Legal, [...] territórios indígenas ou [...] áreas com
  classificação socioeconômica de alta vulnerabilidade". Os editais
  implementam só a faixa de IVS: nenhum dos três cita Amazônia Legal ou
  território indígena para a bolsa.
- **O que o candidato vê [V]:** os quadros de vagas dos ciclos 1 e 3 trazem a
  coluna `FAIXA DE ATRAÇÃO` (e, no ciclo 3, `TIPO DE MUNICÍPIO`), mas não o
  valor do IVS. No quadro original do ciclo 2 o cabeçalho não está nas
  primeiras linhas, e as colunas não foram conferidas.

**Não foi encontrado** nos editais, no manual nem na Portaria 7.177 nenhum
destes benefícios por faixa ou vulnerabilidade: pontuação em seleção futura,
titulação, prioridade na escolha, auxílio-moradia ou ajuda de custo de
instalação. A ajuda de custo de instalação da PI 604/2023 e da PI 7/2026 é do
PMMB, e a PI 7/2026 não menciona o PMM-E [V].

### 2.6 Pró-Residência (formação, não provimento)

**[V]** Edital SGTES/MS 6/2025 (DOU 18/09/2025). A ordem de concessão de bolsas
de residência é:

1. programas em estados da Amazônia Legal;
2. NE e CO;
3. na quarta etapa, pontuação adicional de 50% para UF "com razão de
   especialistas por 100 mil habitantes abaixo da média nacional" e para NE e
   CO.

Desempate:

> 4.6.1. O Critério de Prioridade Territorial [...] que considera
> conjuntamente a média entre o Índice de Vulnerabilidade Social - IVS e o
> Índice de Desenvolvimento Humano - IDH, por UF [...]<br>
> 4.6.2. Persistindo o empate, será considerado o Índice de Vulnerabilidade
> Social - IVS do IPEA do município da instituição ofertante, do mais
> vulnerável para o menos vulnerável.

Esse é o único uso **contínuo** de IVS municipal encontrado, e só como segundo
critério de desempate. Ele aloca bolsas de residência às instituições, não
especialistas formados aos municípios. Não alcança a escolha de vagas do PMM-E
em 2025–2026. O edital 3/2024 já estava na auditoria 18, §2.7.

### 2.7 Estados e municípios

- **Encontrado [V]:** leis municipais de auxílio-moradia e auxílio-alimentação
  para o **PMMB**. Exemplo: a Lei 2.581/2023 de João Monlevade (MG) paga R$
  1.700,00 de moradia e R$ 550,00 de alimentação, "aos Médicos que atuarem no
  Projeto Mais Médicos para o Brasil". O valor é fixado pelo município, sem
  critério de IVS. A obrigação vem da PI 7/2026, que manda "assegurar o
  pagamento do auxílio-moradia e do auxílio-alimentação" [V].
- **Não encontrado:** nenhum programa estadual ou municipal que complemente a
  remuneração de **especialistas** (do PMM-E ou não) com base no IVS ou em
  critério parecido. Buscas por complemento estadual da bolsa do PMM-E,
  provimento estadual de especialistas no interior e "difícil provimento" com
  especialistas não deram resultado. A busca **não foi exaustiva**: não foram
  lidos os diários oficiais estaduais nem os municipais.

### 2.8 Outros programas federais

- **Agora Tem Especialistas, art. 16 da Portaria 7.266/2025 [V].** A União
  compra consultas, exames e cirurgias de prestadores credenciados
  (modalidades 1 e 2) e de unidades móveis em "comunidades indígenas,
  quilombolas, [...] áreas de difícil provimento" e "áreas com grande demanda e
  tempo de espera" (modalidade 3). Nenhum critério de IVS. Para o especialista,
  é demanda concorrente pelas mesmas horas, porque a bolsa do PMM-E é
  cumulável. Não há corte.
- **Eixo Vínculo e Eixo Estratégico (Portaria 9.177/2025) [V]:** "incentivos
  adicionais para especialistas com título de Médico de Família e Comunidade,
  para atuação em locais de difícil fixação". O valor está no §2.4.
- **Teto de emendas e parcelas MAC e PAP (+20% com IVS > 0,3), IED da APS, teto
  da 752/2023 e incentivo de nutrição:** estão na auditoria 18. São
  transferências e tetos para entes, não pagamentos ao médico.

## 3. O que isso implica para a queda em 0,300 e para a subida do preenchimento ao longo do IVS

Esta seção só levanta hipóteses. Nenhuma foi testada aqui, e nenhuma afirma
efeito.

### 3.1 Queda no corte 0,300

1. **Concorrência de incentivos individuais.** Nos atos lidos, nenhum
   incentivo individual a médico, especialista ou não, muda em 0,300. Os
   degraus territoriais encontrados ficam em 0,400 (AgSUS e PMMB), 0,512 e
   0,638 (indenizações). Os outros incentivos não usam IVS (Fies, ajuda de
   custo das imersões, desempate por UF). Hipótese: a queda em 0,300 **não**
   vem de um benefício concorrente que o especialista perde ou ganha ao cruzar
   o corte. Esta é a leitura mais segura da documentação.
2. **Lado municipal (pacote da auditoria 18).** Em 0,300 mudam o teto de
   emendas e parcelas MAC e PAP (+20%), o estrato do IED nos portes 2 e 3 e,
   no texto, o teto de coparticipação da 752. Se essas regras fizerem os
   municípios logo acima do corte abrir mais serviços ou vagas para o mesmo
   número de candidatos, a taxa de preenchimento cai pelo denominador.
   Hipótese testável sem abrir outcome novo: continuidade, no corte, das
   **vagas oferecidas** e das células por município (F0.1 e F0.2, família N).
3. **Fronteira exatamente em 0,300.** Atos que seguem o texto da 485 põem 0,300
   na classe de cima. A bolsa e as emendas põem na de baixo. O donut (auditoria
   18, §5.4) separa os dois casos.
4. **Informação: hipótese fraca.** O texto do Edital 3/2025 descrevia uma grade
   um degrau menos generosa que a aplicada. Pelo texto, 0,301–0,400 seria
   "média", ou seja, R$ 10 mil. Mas o quadro do ciclo 1 mostrava a faixa de cada
   vaga, e a faixa tem valor fixo no próprio texto (Faixa 2 = R$ 15 mil) [V].
   Um descompasso só pesaria para quem inferisse a faixa pela classe de IVS. Se
   a queda se concentrar no ciclo 1 e sumir nos ciclos 2 e 3 (cujos textos já
   descrevem a grade aplicada), essa hipótese ganha peso. Se persistir, perde.
5. **Ajuda de custo das imersões, a partir do ciclo 2.** Ela depende da
   distância à formadora da Ebserh, não do IVS. Só explicaria um salto em 0,300
   se a distância à formadora saltasse ali, o que não há motivo documental para
   esperar.

### 3.2 Subida do preenchimento ao longo do IVS dentro das faixas

1. **Nenhum incentivo contínuo no IVS** foi encontrado para o especialista do
   PMM-E. Além disso, o candidato não vê o IVS: o quadro mostra a faixa.
   Hipótese: o gradiente dentro da faixa não vem de resposta direta ao IVS. Ele
   viria de características territoriais correlacionadas com o IVS.
2. **Custo de oportunidade das 20 h.** A bolsa é cumulável com outras
   atividades remuneradas e exige 20 h semanais. Onde o mercado privado de
   especialistas é mais denso (em geral, IVS mais baixo), o custo de
   oportunidade das 20 h é maior, e a bolsa constante dentro da faixa vale
   relativamente menos. Hipótese contínua, compatível com a subida. Fatores
   pré-tratamento para o G-f do protocolo 62: densidade de especialistas por
   habitante no município ou na região antes do programa, porte e capital.
3. **Desempate por UF de domicílio e de nascimento.** Favorece candidatos
   locais. Se a oferta de especialistas nascidos ou residentes na UF variar com
   o IVS, o critério pode mudar o preenchimento ao longo do IVS. Só pesa em
   vagas disputadas.
4. **Redistribuição para cadastro de reserva (item 5.7).** A prioridade vai
   para regiões com maior dificuldade de acesso e escassez de especialistas, o
   que tende a estar correlacionado com o IVS [NÃO VERIFICADO]. Se o
   preenchimento medido incluir vagas redistribuídas, isso pode produzir
   gradiente.
5. **Ajuda de custo por distância (ciclos 2 e 3).** Compensa parte do custo das
   imersões para quem está a mais de 50 km da formadora da Ebserh. O valor é
   pequeno perto da bolsa. Correlação com o IVS **[NÃO VERIFICADO]**.
6. **Degraus em 0,400 fora do PMM-E (AgSUS e PMMB).** Afetam generalistas da APS
   e ficam no limite superior da faixa de R$ 15 mil. Não produzem inclinação
   dentro da faixa de R$ 10 mil nem dentro da de R$ 15 mil. Podem afetar a
   oferta local de APS acima de 0,400, o que pesa na leitura do corte 0,400,
   não do gradiente.

Para o G-f do protocolo 62, o que esta auditoria permite registrar é: **não há
fator documental de política, ligado ao IVS, que varie continuamente dentro das
faixas para o especialista**. Os candidatos documentais (2 a 5 acima) são
correlatos territoriais e devem entrar, se entrarem, como fatores
pré-tratamento já previstos no protocolo (região, porte, médicos por perto,
concorrência). Nenhum fator novo deve ser escolhido depois de olhar a
inclinação.

## 4. Limites

- A Portaria Conjunta SGTES/SAS 3/2013 e a Portaria 1.377/2011 não foram lidas
  no DOU nem na BVS (HTTP 503). O texto vem da reprodução do CONASS, e o Anexo I
  (lista de municípios) não foi arquivado.
- Os valores da ajuda de custo das imersões vêm de manual em "versão
  preliminar". A regra que separa os níveis 1 e 2 e o número de imersões não
  foram encontrados.
- O Edital 3/2026 (ciclo 2) é PDF digitalizado. Foram lidas visualmente as pp.
  1, 9, 10, 20 e 21. Itens fora dessas páginas não foram conferidos.
- Na AgSUS, o corte 0,400 é inferido pela remissão à 485. A lista aplicada (e a
  fronteira em 0,400 exato) não foi obtida, nem o valor do incentivo em 2021–2024.
- A busca de incentivos estaduais e municipais foi por termos na web e não
  cobre diários oficiais estaduais nem municipais.
- A Resolução CNRM 6/2026 e o PL 2689/2024 só apareceram em fontes secundárias.
- As páginas do gov.br e do Planalto mudam bytes a cada acesso. O manifesto
  guarda o SHA-256 da cópia capturada, e o script confere as âncoras no texto.
