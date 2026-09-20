# Proveniência de figuras e números — banca 1

> **Regra aplicada:** todo número exibido declara fonte, data de referência, cobertura, unidade e reprodutibilidade<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Atualização:** 17 de setembro de 2026

> [!IMPORTANT]
> **A numeração mudou de novo em 17/09/2026.** O deck passou a ter **17 slides em
> 3 seções** (mapa no topo de [02](02_conteudo_slides.md)). Toda referência a
> slide neste arquivo usa a **numeração nova**: 1 capa, 2 sumário, 3 divisória,
> 4 Problema, 5 Política, **6 IVS e suas dimensões**, 7 Efeitos, 8 Pergunta,
> 9 divisória, **10 Literatura teórica usada**, 11 Modelo microeconômico
> conjunto, 12 Custo da localidade, 13 Remuneração da localidade, 14 divisória,
> 15 Implicações, 16 Hipótese, 17 Disponibilidade de dados. O slide de **desafio
> metodológico** foi **removido** do deck; a sua seção continua aqui, marcada
> como fora da tela, pela regra 7 da seção 4. Referências a slides em versões
> anteriores deste arquivo, ou em commits antigos, não são comparáveis.

> [!IMPORTANT]
> **O que conta como "na tela", desde 16/09/2026.** A compressão de
> [02](02_conteudo_slides.md) passou a declarar o que é conteúdo de tela e o que
> não é. Vai à tela **o corpo do slide**: texto, listas, tabelas, figuras,
> equações e os destaques em citação. **Não vão** a linha `**Fontes:**`, que
> desce a nota de rodapé pequena, nem qualquer bloco marcado
> `**Nota de produção.**`, que é instrução para quem monta o deck. Isso fixa o
> alcance da regra 4 da seção 4: **número no corpo de um slide precisa de linha
> na seção 2**. Número que só aparece em nota de produção ou em linha de fontes
> continua registrado aqui, marcado como fora da tela — sai do alcance da regra,
> nunca do rastreio. Na mesma revisão os `###` viraram **builds** — 33 em 16
> slides, e **32** desde o corte de 17/09/2026 —, não slides novos: a numeração
> desta seção continua a de slides.
>
> **Uma consequência do corte de 17/09/2026.** Número que sai do corpo do slide
> e entra **dentro de uma figura** continua **na tela**: a figura é conteúdo de
> tela, e o seu rodapé também. É o caso dos percentuais da dupla prática e da
> ressalva de cobertura do inquérito, e é por isso que a linha da regra 4 vale
> igual para eles.
> Linha cuja saída da tela é de 16/09/2026 leva a marca **"saiu da tela em
> 16/09/2026, mantida por rastreio"**; número que nunca foi exibido é declarado
> como tal. O conteúdo de [02](02_conteudo_slides.md) passou por **mais de uma
> rodada em 16/09/2026** — compressão e revisão —, e este arquivo audita sempre a
> **versão vigente**: linha marcada como fora da tela descreve onde o número está
> agora, não a rodada em que ele se moveu.

---

## 1. Figuras

| Código | Figura | Slide | Arquivo | Origem |
|---|---|:---:|---|---|
| `E1` | Especialistas por 100 mil habitantes: as duas maiores e as duas menores UFs, 2024 | 4 | `output/apresentacao_banca1/especialistas_por_uf_extremos.png` | Demografia Médica 2025; gerada por script desde 17/09/2026 — ver `P6` |
| `E2` | Deslocamento médio para serviços de alta complexidade, por região | 4 | `output/apresentacao_banca1/deslocamento_por_regiao.png` | atribuída à REGIC 2018; gerada por script desde 17/09/2026, **sem fonte primária confirmada** — ver `P7` |
| `E3` | Setor de atuação dos cirurgiões: dupla prática, só privado, só público ou SUS | 4 | `output/apresentacao_banca1/dupla_pratica_cirurgioes.png` | Demografia Médica 2025, cap. 13, Fig. 1, p. 254; gerada por script desde 17/09/2026 |
| `F3` | Bolsa mensal por faixa de atração | 5 | `output/apresentacao_banca1/bolsa_por_faixa.png` | Edital SGTES/MS nº 3/2025, gerada por script |
| `F1` | Especialistas por 100 mil habitantes em jun/2025, por faixa publicada | 5 | `output/apresentacao_banca1/oferta_pre_por_faixa.png` | CNES + Censo 2022, gerada por script |
| `F2` | Colegas da mesma especialidade no município, jun/2025, por faixa publicada | 5 | `output/apresentacao_banca1/retaguarda_por_faixa.png` | CNES, gerada por script |
| `F6` | Preenchimento do ciclo 1 por faixa publicada e por estrato territorial | 7 | `output/apresentacao_banca1/preenchimento_ciclo1.png` | tabelas descritivas do módulo A4, gerada por script |
| `F7` | Especialistas por 100 mil habitantes nos 295 municípios do ciclo 1, série mensal agregada de jun/2024 a jul/2026 | 7 | `output/apresentacao_banca1/oferta_total_mensal.png` | CNES + Censo 2022, gerada por script; **eixo truncado em 14–18** — ver a definição abaixo |

`F4` (curva de custo laboral) e `F5` (vagas por região) saíram do deck no corte
de 16/09/2026 e estão listadas abaixo entre as figuras não usadas.

**As oito são produzidas** por
[`scripts/apresentacao/gerar_figuras_banca1.py`](../../../scripts/apresentacao/gerar_figuras_banca1.py),
que grava `output/apresentacao_banca1/manifesto_figuras.json` com o hash das
entradas, o filtro aplicado e as séries por faixa, região e estrato. Desde
17/09/2026 isso inclui `E1`, `E2` e `E3`, que **não derivam de base do
repositório**: os valores são estatísticas publicadas, declaradas no script como
constantes com fonte, página e cobertura, e repetidas no manifesto sob
`estatisticas_publicadas_slide_4`, cada uma com o campo
`fonte_primaria_confirmada`. **Gerar por script resolve a forma, não a fonte:**
`E1` e `E2` seguem sem fonte primária conferida — `P5`, `P6` e `P7`.

**Definição de `E1`.** Os **quatro** valores por UF que têm fonte registrada —
DF 453, SP 244, PA 70, MA 68 —, não as 27 unidades. A figura equivalente do deck
do grupo mostrava 16 barras e **não era usável**: calibrada pelos dois rótulos
impressos (DF 453,5 e MA 68,2), punha **SP em ≈ 419** e **PA em ≈ 135**, contra
os 244 e 70 da série citada nesta seção. Só os dois extremos rotulados batiam.
Ver `P6`.

**Definição de `E3`.** Barra única de 100% com os três percentuais do cap. 13,
Fig. 1, p. 254. O rodapé da figura — que é **conteúdo de tela** — carrega a
ressalva de cobertura: inquérito por amostra do Colégio Brasileiro de Cirurgiões,
**1.544 respondentes**, não censo, sem recorte equivalente para outras
especialidades.

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
dela só se usam as contagens descritivas e, no slide 7, o contraste ajustado de
estrato, declarado como **associativo**.

**Definição de `F7`** (na tela desde 20/09/2026, no **primeiro build** do slide
7, ao lado de `F6`). A **mesma taxa** de `F1`, mês a mês e **sem quebra por
faixa**: razão dos **totais** — soma de especialistas sobre soma da população —
nos mesmos **295 municípios** com curso de correspondência unívoca, em **26
competências**, de `202406` a `202607`. A série está no `manifesto_figuras.json`
sob **`serie_total_por_100k`**; as entradas são o painel
`output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet` (filtro
`curso_sem_sobreposicao == 1`) e a população do Censo 2022, ambas com hash no
manifesto. Município e denominador são **constantes** nas 26 competências, e o
script aborta se qualquer um dos dois variar. É presença cadastral no CNES, não
participação no PMM-E.

**O eixo de `F7` é truncado em 14–18**, a pedido do autor, para tornar legível
uma variação pequena em relação ao nível. Isso **amplia a inclinação aparente**:
num eixo a partir de zero a mesma série pareceria quase plana. O truncamento vai
**declarado no rodapé da figura**, que é conteúdo de tela — *"Eixo vertical
truncado: começa em 14, não em zero. Sem grupo de comparação: todos os municípios
receberam vaga. Leitura descritiva."* A banda é fixa em `PISO_Y`/`TETO_Y` no
script, que aborta se a série sair dela, para que uma competência nova não seja
cortada em silêncio. Truncar muda a leitura visual, não os dados: os valores do
manifesto são os mesmos. A ressalva de que **não há grupo de comparação** está na
tela em dois lugares, e é ela que impede ler a subida como efeito do programa: o
**terceiro item da leitura** — *"o estoque sobe desde antes da oferta"*, com a
observação de que nenhum município da série está fora do programa — e o
**destaque do build 2**, que diz que a série não tem grupo de comparação. `F7`
entra como **contexto descritivo**. A versão **por faixa**,
`oferta_antes_depois_por_faixa.png`, continua fora do deck, e com ela a tabela de
inclinações pré/pós do deck do grupo — ver `P8`.

### Figuras geradas e não usadas

| Arquivo | Situação |
|---|---|
| `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` (`F5`) | células e vagas imediatas do ciclo 1 por região. Saiu do slide da Política no corte de 16/09/2026: descrevia sem argumentar. Os totais que ficaram em texto no slide 5 são **1.295 / 460 / 368**; o Nordeste (505 células, 39%) e as 18 capitais saíram da tela junto com a figura. O script continua gerando |
| `docs/02_teoria/figuras/curva_custo_laboral_burnout.png` (`F4`) | ilustração conceitual do custo laboral em U. Saiu do deck em 16/09/2026 com a fusão dos dois slides de custo; o formato em U é descrito em texto no **slide 10**. Permanece como figura canônica de `modelo_micro.md`, §2.2. A ressalva de legibilidade em projeção deixa de afetar a apresentação |
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | série mensal de especialistas por 100 mil habitantes, 2024–2026. Saiu do deck na segunda rodada de revisão: sem grupo de comparação, não se lê como efeito do programa. O script continua gerando; a série está no `manifesto_figuras.json` e é a única parte reprodutível da tabela do deck do grupo — ver `P8` |
| `docs/07_apresentacoes/banca1/figuras/motivacao_manchetes.png` | recortes de imprensa com cabeçalho do deck anterior. As manchetes entraram no slide do Problema como citação textual em 09/09/2026 e saíram no corte de 16/09/2026; a portaria de urgência continua citada em texto no slide 4, e a manchete dos 10% deixou a tela: depois da compressão de 16/09/2026 ela só aparece em **nota de produção**, como advertência a quem monta o deck |

`docs/07_apresentacoes/banca1/figuras/especialistas_por_uf.png` e
`docs/07_apresentacoes/banca1/figuras/deslocamento_por_regiao.png` — os arquivos
do deck do grupo — **voltaram a esta lista em 17/09/2026**, agora em definitivo:
`E1` e `E2` passaram a ser gerados por script e gravados em `output/`. Os dois
PNGs antigos ficam preservados como material do deck anterior. O de UF **não
pode voltar à tela** enquanto suas barras intermediárias contradisserem a série
citada; ver `P6`.

---

## 2. Números exibidos

### Slide 4 — Problema: o retrato nacional e a dupla prática

Fontes externas, conferidas em 09/09/2026 e revistas em 16/09/2026. A revisão de
16/09/2026 corrigiu um erro factual (ver `Correção factual` na seção 3) e
rebaixou a manchete dos 10%. A compressão do mesmo dia tirou do corpo do slide a
manchete e a citação do item 1.2.1 do edital; a revisão seguinte devolveu o
tamanho do inquérito e manteve na tela a portaria de urgência. Também saiu da
tela o total de **597 mil** médicos. As linhas abaixo estão marcadas uma a uma.

> [!IMPORTANT]
> **O corte de 17/09/2026 mudou onde os números estão, não quais são.** O slide
> passou a ser figura e uma frase por build. Saíram do **corpo** do slide, e
> **entraram na figura**, que é conteúdo de tela: os quatro marcadores do
> retrato nacional — hoje `E1` e `E2` — e a tabela dos três percentuais de
> atuação, hoje `E3`. Saíram da tela **inteiramente**, e seguem aqui por
> rastreio: **353 mil** especialistas e **59%** dos médicos; **55,4%** no
> Sudeste e **5,9%** no Norte; **16 cursos, 6 cirúrgicos e 10 ambulatoriais**;
> **6 dos 16** títulos citando câncer, tumores ou oncologia; e as contagens de
> células das três maiores ofertas — 188, 164 e 147 —, cujos **nomes** continuam
> na tela. A ressalva de cobertura do inquérito **não saiu**: migrou para o
> rodapé de `E3`. Nenhum valor foi alterado.

| Número | Fonte | Verificação |
|---|---|---|
| 597 mil médicos em 2024; 353.287 especialistas (59,1%) | Scheffer, M. et al., *Demografia Médica no Brasil 2025*, FMUSP/AMB, dados de dez/2024 | conferido na cobertura da Agência Brasil (abril de 2025) e do portal Afya. Na tela, desde 16/09/2026, só **353 mil** e **59%**, arredondados; **597 mil** saiu da tela em 16/09/2026, mantido por rastreio — é o denominador do percentual exibido |
| Sudeste 55,4% dos especialistas; Sul 16,7%; Nordeste 14,5%; Norte 5,9% | idem | ⚠️ **conferido apenas em cobertura.** Uma leitura do PDF integral **não localizou** esses percentuais. O portal Afya reporta: *"A região Sudeste concentra 55,4% dos especialistas, seguida pelo Sul (16,7%) e Nordeste (14,5%). Já o Norte responde por apenas 5,9%"*. Na tela, só **55,4%** e **5,9%**; Sul e Nordeste nunca foram exibidos e constam por integridade da citação. Ver `P5` |
| 453 especialistas por 100 mil habitantes no DF; 244 em SP; 68 no MA; 70 no PA | idem | Agência Brasil: "Distrito Federal e São Paulo respondem pelas maiores razões de especialistas por 100 mil habitantes (453 e 244, especificamente), enquanto Maranhão e Pará respondem pelas menores taxas no país (68 e 70, respectivamente)". É a série de `E1`. Na tela, só **453** e **68**; 244 e 70 nunca foram exibidos e sustentam a figura |
| **72,4%** dos cirurgiões em **dupla prática** (público **e** privado); **19,9%** exclusivamente no setor privado; **7,7%** exclusivamente no setor público ou no atendimento a pacientes do SUS | Scheffer, M. et al., *Demografia Médica no Brasil 2025*, FMUSP/AMB, **cap. 13, Figura 1, p. 254** | conferido na fonte primária, que diz literalmente: *"predomina a dupla prática (72,4%). Apenas 7,7% dos cirurgiões atuam, exclusivamente, no setor público ou no atendimento a pacientes do SUS; enquanto 19,9% atuam somente no setor privado"*. Somando dupla prática e exclusivos do público, **80,1%** atendem SUS — número que **não vai à tela**, ver a linha do Senado Notícias abaixo. Os três percentuais estão na tela no slide 4; o **slide 11** os retoma por **remissão**, sem repetir os números — é a mesma medição, não número novo (ver a linha do slide 11) |
| Cobertura do recorte setorial: **inquérito por amostra** de associados do **Colégio Brasileiro de Cirurgiões** — **1.544 respondentes** de **6.869 elegíveis** | idem, cap. 13 | **não é censo** dos **42.426** cirurgiões do país. E **não existe o mesmo recorte para outras especialidades** em fonte pública: qualquer generalização de "especialistas" a partir desses três números é extrapolação do leitor, não resultado do estudo. **Na tela**, no segundo build do slide 4: *"Dedicação **exclusiva** ao SUS é rara. Único recorte setorial da Demografia Médica 2025: inquérito com **1.544 cirurgiões**, não censo"*. A compressão de 16/09/2026 chegou a levar a ressalva para a nota de produção; a revisão do mesmo dia a devolveu ao corpo do slide. **6.869 e 42.426 nunca foram exibidos** |
| A bolsa do PMM-E compra **20 horas** dessa fração | Edital SGTES/MS nº 3/2025, **item 11.3.b** | linha acrescentada em 16/09/2026: a carga já estava na tela do slide 4 e só tinha registro nos slides 5 e 11. É o mesmo item, antecipado aqui para amarrar a dupla prática à fração que o programa compra |
| "apenas 10% dos especialistas atendem no SUS. Além disso, há concentração desses profissionais nas capitais e regiões mais ricas do país" | Senado Notícias, **24/09/2025** | 🚫 **não citável em slide.** É **fala do ministro da Saúde em debate de medida provisória**, sem metodologia publicada, e **conflita com a fonte primária**: pela Demografia Médica 2025, **80,1%** dos cirurgiões atendem SUS (72,4% + 7,7%). **Saiu da tela em 16/09/2026, mantida por rastreio:** a frase e os **80,1%** que a contradizem passaram ao bloco `**Nota de produção — o que não dá para dizer**` do slide 4. Nenhum dos dois vai à tela; a advertência virou instrução a quem monta o deck e a quem responde à banca |
| Deslocamento médio para serviços de alta complexidade: Norte **276 km**, Centro-Oeste **256**, Nordeste **179**, Sudeste **107**, Sul **101** | atribuídos à REGIC 2018 (IBGE), deslocamentos para serviços de saúde | 🚫 **fonte primária não confirmada.** Série de `E2`; ver `P7`. Na tela, só **276 km** e **101 km**; os outros três sustentam a figura. A compressão de 16/09/2026 tirou do corpo do slide a ressalva "fonte primária ainda não confirmada", que passou a constar apenas da linha de fontes |
| 16 cursos: 6 cirúrgicos e 10 ambulatoriais | Edital SGTES/MS nº 3/2025, Tabela 3 | conferido em 16/09/2026 também nos códigos 1–16 do quadro de vagas (cursos 7 a 16 são ambulatoriais: colonoscopia, colposcopia, ecocardiografia, duas endoscopias digestivas, oncologia clínica, radioterapia, ultrassonografia mamária, videolaringoscopia, anatomia patológica) |
| Três maiores cursos em oferta no ciclo 1: **endoscopia digestiva alta, 188 células**; **colonoscopia, 164**; **anestesiologia perioperatória, 147** | `output/aquisicao/quadro_vagas_tratamento.parquet` e Tabela 3 do Edital SGTES/MS nº 3/2025 | recontagem em 16/09/2026 sobre as 1.295 células estabelecimento–curso da chamada 1; unidade é **célula**, não vaga. Na tela, desde 16/09/2026, os três aparecem como "maiores ofertas", sem a palavra *célula*, e **anestesiologia** sem o qualificador *perioperatória* |
| **6 dos 16** títulos citam oncologia, tumores ou câncer | idem | cursos 3, 4, 5, 6, 12 e 16 (cirurgia oncológica avançada; coloproctológica com foco em tumores colorretais; aparelho digestivo com foco em tumores digestivos; ginecológica com foco em tumores ginecológicos; oncologia clínica; anatomia patológica com ênfase em oncologia) |
| "na redução do tempo de espera, na ampliação do diagnóstico precoce e no fortalecimento das redes de atenção especializada" | Edital SGTES/MS nº 3/2025, item 1.2.1 | conferido no PDF do DOU preservado em `data/raw/aquisicao/ivs_regra/`. **Saiu da tela em 16/09/2026, mantida por rastreio:** a citação literal deixou o corpo do slide 4; o item 1.2.1 permanece na linha de fontes do slide 5 |
| Situação de urgência em saúde pública por 24 meses, em razão do tempo de espera na atenção especializada | Portaria GM/MS nº 7.061, de 6 de junho de 2025 | conferido em reprodução do DOU. **Está na tela**, no terceiro build do slide 4: *"Em 2025 o Ministério declarou **urgência em saúde pública por 24 meses** pelo tempo de espera, e lançou o **Agora Tem Especialistas**, de que o PMM-E é o braço de provimento"*. O registro anterior, de que estaria fora da tela, foi corrigido em 16/09/2026 |

### Slide 5 — Política: o que é o PMM-E e o que fixa a bolsa

> [!IMPORTANT]
> **O corte de 17/09/2026.** O slide passou de **cinco** builds para **três**.
> **Entrou na tela**, correção D1 do PR de ajuste estrutural: o rótulo **célula**
> no lugar de *vaga* — "1.295 **células** estabelecimento–curso" — e as **678**
> vagas imediatas, que estavam fora da tela desde 16/09/2026. **Entrou na tela**,
> correção F2 do mesmo PR: o pacote formativo dito como o que **não** varia —
> bolsa-formação sem vínculo, 12 meses, 20 horas, RQE e supervisão de instituição
> formadora. **Saíram da tela, mantidas por rastreio:** a contribuição
> previdenciária do item 11.2; o adicional do art. 22-D, §4º, e o registro de que
> não foi regulamentado no ciclo 1; a afirmação de que nenhuma célula
> município–curso aparece com mais de uma faixa; os **48%** promovidos, que eram
> a forma proporcional dos mesmos 177/368, hoje só em contagem; e os **31%**
> contra **12%** de médicos sozinhos ou com um único colega. **Mudou de slide:**
> a teoria da mudança, que é hoje o primeiro build do slide 7 — a linha
> correspondente desta seção está lá. Nenhum valor foi alterado.

| Número ou afirmação | Fonte |
|---|---|
| finalidade: provimento para reduzir o tempo de espera em regiões prioritárias; exclusivo a médicos com diploma brasileiro ou revalidado e certificação de especialista; bolsa-formação | Lei nº 15.233/2025, art. 21, que acrescenta o art. 22-D à Lei nº 12.871/2013 — `data/raw/aquisicao/ivs_regra/lei_15233_2025.html` |
| aprimoramento em serviço por integração ensino-serviço; objetivos de equilíbrio regional e redução de desigualdades | Portaria GM/MS nº 7.177/2025, arts. 1 e 2 — conferida em reprodução do Conass |
| objeto (item 1.1); até 12 meses (1.1.4); itinerários formativos com imersões, EAD e supervisão/mentoria (1.2.3, 1.2.7); não é concurso, sem vínculo (1.2.8, 11.1.2); diploma e RQE (3.1); até dois locais (4.1.3); vedada substituição de profissional já vinculado (4.1.6); barema de titulação e tempo de formação, 10 pontos (5.2, Tabela 4); 16 cursos, 6 cirúrgicos e 10 ambulatoriais, 20 horas semanais (Tabela 3, 11.3); bolsa por faixa (11.1.3) | Edital SGTES/MS nº 3/2025, DOU de 24/07/2025 — `data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_dou.pdf`, SHA-256 `417c82d903ab6cf26ca17a5b50705175de40ccc539f0fd2f1e66a3ad9daf6fb2` |
| 1.295 células, 460 estabelecimentos, 368 municípios, 27 UFs; Nordeste 505 células (39%) | `output/aquisicao/quadro_vagas_tratamento.parquet` e `manifesto_figuras.json`. Na tela: 1.295, 460, 368 e "todas as UFs". Saíram da tela em 16/09/2026, mantidos por rastreio: **Nordeste 505 células (39%)**, 678 imediatas, 1.145 reserva e MG 252 |
| dois terços dos municípios com menos de 100 mil habitantes (66,0%); 18 capitais | quadro de vagas × Censo 2022; tipologia A2 (`docs/auditorias/09_tipologia_territorial.md`) — em texto de apoio, fora da tela desde 16/09/2026 |
| **incidência de contribuição previdenciária**: o participante é segurado obrigatório do RGPS, como **contribuinte individual**, e o valor devido é descontado da bolsa-formação | Edital SGTES/MS nº 3/2025, **item 11.2**, conferido no PDF do DOU em 16/09/2026 |
| **adicional** para Amazônia Legal, territórios indígenas e áreas de alta vulnerabilidade, *"conforme regulamentação do Ministério da Saúde e disponibilidade orçamentária"* | Lei nº 15.233/2025, **art. 22-D, §4º** — conferido no HTML preservado |
| o adicional do §4º **não foi regulamentado no ciclo 1** | verificado no PDF do edital em 16/09/2026: a palavra **"adicional"** aparece **uma única vez** no edital, e no **barema de titulação** (Tabela 4, item 5.2 — "ano adicional" de residência), nunca como acréscimo à bolsa. O quadro de vagas tem um único campo de remuneração, a faixa de atração |
| **nenhum município e nenhuma célula município–curso** do ciclo 1 aparece com mais de uma faixa | `output/aquisicao/quadro_vagas_tratamento.parquet`, verificado em 16/09/2026: 0 municípios com mais de uma `faixa_atracao_anunciada` e 0 células município–curso com mais de uma. É o que sustenta a afirmação de que o valor depende **só do município** |
| 16 indicadores, 3 dimensões do IVS 2010 | Ipea, *Atlas da Vulnerabilidade Social nos Municípios Brasileiros* (2015). Na tela **no slide 6** desde 17/09/2026, e antes disso no slide 13 — *"o IVS 2010 do Ipea resume, de 0 a 1, dezesseis indicadores do Censo 2010 em três dimensões"* —, não mais no slide 5: desde 16/09/2026 a cláusula 11.1.4 do slide 5 diz só "categoria de **IVS 2010** do Ipea" |
| Cortes 0,200 / 0,300 / 0,400 / 0,500 | mesma fonte; reproduzidos em `docs/auditorias/01_regra_institucional.md`, §6.3. Na tela aparecem só **0,400** e **0,500**, no **slide 6**, como as fronteiras das categorias do item 11.1.4; até 17/09/2026 apareciam no slide do desafio metodológico, como cortes candidatos. A grade completa nunca foi exibida |
| R$ 20.000 / R$ 15.000 / R$ 10.000 | Edital SGTES/MS nº 3/2025, item 11.1.3, e retificação; auditoria, §6.1 — é a série de `F3` |
| Cláusulas 11.1.3 (localização + Anexo IV) e 11.1.4 (categorias de IVS) | Edital SGTES/MS nº 3/2025, PDF do DOU preservado em `data/raw/aquisicao/ivs_regra/`, com SHA-256 registrado acima |
| Anexo IV não reproduzido no edital (constam I a III) | mesmo PDF, índice de anexos |
| 177 dos 368 municípios com faixa publicada diferente da recalculada; 0 abaixo do piso de IVS, 177 acima; 48% promovidos | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py`; portão R1, `docs/05_identificacao/16_sintese_achados_e_novo_plano_causal.md`, §3.5. Os três estão na tela, no terceiro build do slide 5. **48% é o mesmo 177/368 dito como proporção** (48,1%), não um segundo achado: é a forma que a tela usa em *"o critério de localização promove **48%** dos municípios acima dele"* |
| 102 / 107 / 159 municípios por faixa publicada | quadro de vagas do ciclo 1 — em texto de apoio, fora da tela desde 16/09/2026 |
| Grade mudou em 2026: *alta* passou à Faixa 1 | Chamamento SGTES/MS nº 1/2026; auditoria §6.4 — fora da tela, escopo do ciclo 1 |
| Regra de 2026 aplicada ao ciclo 1 acerta 224/368; união das duas regras, 237/368 | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json` — fora da tela, mantido como registro do portão R1 |
| 18,3 / 14,4 / 15,0 especialistas por 100 mil hab. (Faixas 1, 2 e 3 publicadas), jun/2025 | `F1`, agrupado pela faixa publicada no quadro de vagas |
| Mediana de 2,5 colegas na Faixa 1, 5,0 na Faixa 2 e 6,5 na Faixa 3; 31% contra 12% sozinho ou com um único colega | `F2`, agrupado pela faixa publicada. Faixa 1 tem 150 pares município–especialidade em 85 municípios |
| Agrupamento por faixa publicada, e não por categoria de IVS recalculada | corrigido em 14/09/2026 em `scripts/apresentacao/gerar_figuras_banca1.py`; a versão anterior rotulava errado 177 dos 368 municípios e invertia o sinal de `F1` — ver `P4` |

### Slide 6 — IVS e suas dimensões

Slide novo em 17/09/2026. **Nenhum número é novo:** é o build "Por que o IVS
organiza o custo", que estava no slide das implicações, mais a definição do
índice, que já estava registrada na seção do slide 5.

| Número ou afirmação | Fonte |
|---|---|
| **16 indicadores** do **Censo 2010**, resumidos de **0 a 1** em **três** sub-índices, para todos os municípios | Ipea, *Atlas da Vulnerabilidade Social nos Municípios Brasileiros* (2015) — mesma linha registrada no slide 5 |
| **muito alta** acima de `0,500`, **alta** entre `0,400` e `0,500`, **demais** abaixo | mesma fonte, faixas de classificação do Atlas, reproduzidas em `docs/auditorias/01_regra_institucional.md`, §6.3 (alta de 0,401 a 0,500; muito alta de 0,501 a 1); o item 11.1.4 do Edital SGTES/MS nº 3/2025 usa essas categorias |
| os indicadores de cada dimensão — saneamento, lixo e tempo de deslocamento; mortalidade infantil, analfabetismo e mães adolescentes; extrema pobreza, desemprego e informalidade | Ipea (2015). Estão na tela desde 16/09/2026, antes no slide 13 |
| o IVS como **parte pública** da regra do valor | Edital SGTES/MS nº 3/2025: o item 11.1.4 é público e o Anexo IV do item 11.1.3 não consta do edital — as duas linhas estão na seção do slide 5 |
| a coluna *"o que significa para quem vai atender ali"* | **leitura do projeto**, não classificação do Ipea: é a tradução, em linguagem comum, do mapeamento dimensão → bloco do custo de [`modelo_micro.md`](../../02_teoria/modelo_micro.md), §3.1 |
| *"as três apontam para o mesmo lado"* | **decisão do autor, 17/09/2026.** O documento canônico afirma o contrário para a dimensão de capital humano. Ver `P11` |

### Slide 7 — Efeitos: o ciclo 1 e a literatura

> **Classificação de rigor:** todos os números do ciclo 1 neste slide são
> **associativos/descritivos**. Nenhum é efeito causal do PMM-E. O destaque em
> citação do slide declara isso na tela — *"Isto é descrição, não efeito"* —, e
> desde 17/09/2026 ele **se basta**: o slide que explicava por quê saiu do deck.
> Desde 16/09/2026 esse bloco deixou de ser um `CAUTION` e passou a **citação de
> tela**, com as duas palavras permitidas, **gradiente** e **associação**.

> [!IMPORTANT]
> **O corte de 17/09/2026.** **Saíram da tela dois números que são saída de
> estimação**, e a banca 1 não apresenta resultado de estimação: o **+20,9 p.p.**
> do estrato metropolitano no modelo ajustado e o **+0,50** especialista
> cadastrado do módulo A5, com o erro padrão **0,234** e a expressão "sem
> pré-tendência detectável". O gradiente **bruto** por território — 44,9% a
> 20,5% — continua na tela, na figura e na leitura. **Saíram da tela, e ficam de
> reserva para pergunta da banca**, duas das quatro células do lado "não basta":
> Costa, Nunes & Sanches (2024), com os 12,4% a US$ 15,7 mi por ponto e os 63,8%
> por US$ 2,2 a 5,1 mi — o autor pediu dois a favor e dois contra —, e Pathman,
> Konrad & Ricketts (1992), com os 12% contra 39% após oito anos. Costa et al.
> continua na tela **no slide 10**. **Mudou de rótulo:** "1.295 vagas" virou
> "1.295 **células**", correção D1. Nenhum valor foi alterado.

| Número | Fonte |
|---|---|
| **393 de 1.295** células com confirmação ou homologação — **30,3%** | `output/tema_trabalho/A4_relatorio_diagnostico.md`, §1 |
| 23,6% / 37,4% / 31,6% por faixa publicada (n = 539 / 465 / 291) | `F6`, `A4_tabela_01b_amostra_faixa.csv` |
| 35,6% / 44,9% / 26,9% / 20,5% por estrato (n = 73 / 265 / 811 / 146) | `F6`, `A4_tabela_01_amostra_construcao.csv`, amostra primária |
| **14,5** em jun/2024 e **17,7** em jul/2026 especialistas por 100 mil habitantes nos **295 municípios** — na tela no **build 1**, no corpo do slide e dentro de `F7` | `F7`; `manifesto_figuras.json`, chave `serie_total_por_100k`, 26 competências de `202406` a `202607`. Valores cheios **14,45** e **17,71**, arredondados na tela. É a razão dos totais: **6.068** e **7.436** especialistas sobre população do Censo 2022 **constante** de **41.991.553** — os três **nunca foram exibidos** e sustentam a série. Presença cadastral no CNES, não participação no PMM-E; **sem grupo de comparação**, ver a definição de `F7` e `P8` |
| **Alta de 22,5%** no estoque entre jun/2024 e jul/2026, *"desde antes da oferta"* — na tela no **build 2**, terceiro item da leitura | `F7`, mesma chave `serie_total_por_100k`. Vem da **razão dos totais**, 7.436 / 6.068 = 1,2254; com os dois valores arredondados do manifesto (17,71 / 14,45) daria 22,6%, e é por isso que o percentual é dos totais, não da série arredondada. **Descritivo:** a subida começa mais de um ano antes da publicação das vagas e **nenhum município da série está fora do programa** |
| **Metropolitano +20,9 p.p.** sobre interior remoto no **modelo ajustado** | `output/tema_trabalho/A4_tabela_03b_ajuste_completo.csv`, termo `estrato_metropolitano` = 0,2085 (EP cluster 0,078; p = 0,008), especificação `LPM_full_estrato_ivs_logpop_estoque_faixa_FE`, n = 1.295, 368 clusters. Na especificação mínima o mesmo contraste é 0,279 — o slide cita o **ajustado**, que é o menor |
| **A5: +0,500** especialista cadastrado em **mar/2026** contra **jun/2025**, **erro padrão 0,234** | `output/tema_trabalho/A5_relatorio_diagnostico.md`, módulo A5. O EP 0,234 é o da convenção anterior (p = 0,033); na convenção `reghdfe`/`fixest`, que conta os efeitos fixos absorvidos, o EP é 0,2469 e p = 0,044. O slide arredonda para "+0,50". **O erro padrão está na tela**: a compressão de 16/09/2026 chegou a retirá-lo e a revisão do mesmo dia devolveu o "(erro padrão **0,234**)" ao corpo do slide — é o EP da convenção anterior, não o da `reghdfe`/`fixest` |
| **Pré-tendências: F = 1,031, p = 0,420** (teste conjunto pré-referência) | idem — é ausência de pré-tendência **detectável**, não prova de paralelismo. O teste nunca foi à tela: sustenta a expressão "sem pré-tendência detectável" |
| Salário +33% eleva aceitação em 15,1 p.p.; 106 postos; a >200 km, de ~25% a ~80%; sem seleção adversa | Dal Bó, Finan & Rossi (2013), *QJE* 128(3) — RCT com salário sorteado |
| **+15,1 médicos do programa** por 100 mil habitantes, contra expansão **líquida** de apenas **+5,7** | Hone, T.; Powell-Jackson, T.; Santos, L. M. P. et al. (2020), *BMC Health Services Research* **20:873**. DiD em 5.565 municípios, 2008–2017; o restante substituiu profissionais preexistentes. Catalogado em [`03_literatura_empirica/19_...md`](../../03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md), §7 |
| 3.727 clínicos; 65% não mudariam por nenhum pacote; 37% da renda anual para cidade de 5 a 20 mil hab.; 64% para menos de 5 mil; 130% para o pior pacote | Scott et al. (2013), *Soc Sci Med* 96 — **conferido no resumo** (Europe PMC, PMID 24034949) |
| Elasticidade-salário ~0,4 nas metrópoles e ~0,7 no interior | Costa, Nunes & Sanches (2024), *REStat* 106(1) — **conferido no PDF**. Na tela, só o **0,7** do interior; o 0,4 nunca foi exibido |
| +50% no salário público corrige 12,4% do desequilíbrio a US$ 15,7 mi/p.p.; cotas corrigem 63,8% a US$ 2,2–5,1 mi/p.p. | idem — **conferido na Tabela 6 do PDF** |
| 12% contra 39% de permanência após oito anos | Pathman, Konrad & Ricketts (1992), *JAMA* 268(12) — coorte de 9 anos, 412 médicos |
| Degrau de +50% "cai dentro da faixa" de 37% a 64% | leitura do projeto sobre Scott et al. (2013); é comparação do projeto, não número de um paper — ver `P1` e `P2` |
| Ressalva na tela: os percentuais da literatura são sobre a **renda total**; a bolsa remunera **20 horas semanais** | `P2` |
| Degrau de **R$ 5 mil** no fecho do slide — *"a evidência não decide se um degrau de R$ 5 mil basta"* | Edital SGTES/MS nº 3/2025, item 11.1.3. Retomada do mesmo degrau dos slides 7, 11 e 14; linha acrescentada em 16/09/2026 para cobrir a frase de fecho |

### Slide 8 — Pergunta de pesquisa

O diagrama de teoria da mudança veio do slide 5 em 17/09/2026; a linha abaixo
veio com ele, sem alteração de conteúdo.

| Número | Fonte |
|---|---|
| Teoria da mudança: regra de valor (11.1.3 e 11.1.4), provimento como finalidade (art. 22-D e item 1.1.2), redução da espera como objetivo (art. 22-D e itens 1.2.1 e 1.2.5.V) | Lei nº 15.233/2025 e Edital SGTES/MS nº 3/2025. O que está em **laranja e tracejado** no diagrama — assim nomeado na tela desde 16/09/2026 — é o que **nenhum ato afirma**: é leitura do projeto sobre o que os atos deixam de dizer, não citação. A ressalva de **oferta líquida** que fecha o slide — 20 horas, sem vínculo, e o edital apenas **vedando substituição** de quem já está lá — apoia-se no item **4.1.6**, registrado na linha do edital acima |
| Degrau de **R$ 5 mil** entre faixas | Edital SGTES/MS nº 3/2025, item 11.1.3 (R$ 10 / 15 / 20 mil) |
| "maiores bolsas do PMM-E para municípios mais vulneráveis compensam suas desvantagens territoriais na atração de médicos especialistas?" | [`01_pergunta_escopo/15`](../../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md) — formulação canônica. **Saiu da tela em 16/09/2026, mantida por rastreio:** a citação literal passou à nota de produção do slide 7. Na tela está a versão de manchete do deck, *"O incentivo financeiro oferecido pelo PMM-E funciona para atrair especialistas para regiões mais vulneráveis?"*, que é a mesma pergunta em linguagem de tela |

### Slide 10 — Literatura teórica usada: as equações originais

Slide novo em 17/09/2026. Restaura a tabela das três tradições que saíra do
slide 9 em 16/09/2026, com a coluna **"Equações originais"** no lugar de
"Primitiva que fornece".

| Número | Fonte |
|---|---|
| Moehling et al. (2020), eq. 1, p. 184, como no original | `docs/02_teoria/modelo_micro.md`, §1 |
| Redding & Rossi-Hansberg (2017), eq. 24, p. 28, como no original | idem, §3.2, que a transcreve |
| Choné & Ma (2011), eq. 1, p. 232, com Reinhardt (1972, 1975) | idem, §3.2 e §2.3. **Correção de referência, 17/09/2026:** a linha de fontes do deck citava *IJHCFE* 11; o periódico correto, conforme §5 do documento canônico, é *Annals of Economics and Statistics* 101/102, 229–256, que contém a p. 232 |
| a leitura do numerador e do denominador de R&RH — o que atrai e o que repele | idem, §2.1. Estava no slide do custo até 16/09/2026 |
| a advertência sobre o símbolo $B$ — amenidade, benefício ao paciente, bolsa | convenção de notação do próprio deck; os três usos vêm de `modelo_micro.md`, §2.1 e §2.2, e do item 11.1.3 do edital |
| Redding & Rossi-Hansberg (2017) e Choné & Ma (2011) como as duas primitivas do custo | `modelo_micro.md`, §2.1 e §2.2. **Voltou à tela em 17/09/2026:** a tabela "Três tradições sustentam uma equação" saíra do slide 9 em 16/09/2026 por redundância e é hoje este slide, com as equações originais na terceira coluna. Os três nomes aparecem juntos de novo no **slide 15** |

### Slide 11 — Modelo microeconômico conjunto

| Número | Fonte |
|---|---|
| a equação de escolha na **notação do projeto**, com $m \in M$ e $c^{(s)}_{im}$, e a definição de $c$ | `docs/02_teoria/modelo_micro.md`, §2.4 e §1. É a forma integrada; a original está no slide 10 |
| a troca de índice — $i$ é localidade no original, e passa a ser o médico, com $m$ o município | idem, §2.4 e §3; convenção do deck desde 16/09/2026, dita na tela |
| "preferences over rural or urban living, or other location-specific attributes, such as proximity to family" | Moehling et al. (2020), *Cliometrica* 14, p. 184 — transcrita em `modelo_micro.md`, §1. Na tela, desde 16/09/2026, a citação aparece **elidida**: *"preferences over rural or urban living … such as proximity to family"*. A elisão é de tela; a transcrição íntegra fica no `modelo_micro.md` |

### Slide 12 — Custo da localidade: o lugar e o trabalho

| Número | Fonte |
|---|---|
| $c^{\text{geo}}_{im} = \phi(\text{dist}) - \gamma A_m + \theta^{\text{rural}}_i$, a equação **inferida** de Redding & Rossi-Hansberg | `docs/02_teoria/modelo_micro.md`, §2.1 e §3.2. **A equação original saiu deste slide em 17/09/2026** e está no slide 10; aqui ficou só a inferida e a definição dos seus termos |
| $c^{\text{laboral}}_{im} = C(q; L, K) - \alpha_i B(q; L, K)$, a equação **inferida** de Choné & Ma; formato em U | idem, §2.2 e §3.2. Mesma observação: a original está no slide 10. As **três zonas** da curva saíram da tela em 16/09/2026; o formato em U continua descrito em texto |
| $\partial B/\partial K > 0$ como **extensão do projeto**, motivada por Reinhardt (1972, 1975) | idem, §2.3 — ver a nota sobre Reinhardt na seção 3. Reinhardt aparece na tela em dois lugares desde 17/09/2026: aqui, como motivação da extensão, e na tabela do slide 10, ao lado de Choné & Ma. Em nenhum dos dois é fonte de número |
| Tabela das **três desvantagens do médico** (retaguarda em $L$, infraestrutura em $K$, distância da família em $\phi$) e o porquê de cada uma | idem, §2.1 a §2.3; a coluna "Medimos?" segue o inventário de dados do slide 17. Movida do slide do problema para cá em 16/09/2026. **Eram quatro até 17/09/2026:** a quarta, *mercado privado ausente*, passou ao **slide 13**, por ser de remuneração e não de custo |
| proximidade do lugar de nascimento ou formação é o principal fator; salário e infraestrutura importam em escala menor; ~50 mil generalistas formados de 2001 a 2013 | Costa, Nunes & Sanches (2024), *REStat* 106(1) — conferido no PDF e na cobertura do estudo (Gazeta do Povo, 2019, sobre a versão *working paper* do Ieps, 49.989 médicos) |
| Limitação de commuting: CNES e edital não informam residência | `modelo_micro.md`, §2.1 |

### Slide 13 — Remuneração da localidade

| Número | Fonte |
|---|---|
| $\mathbb{E}(w \mid B_m) = B_m + w^{\text{priv}}_m \geq B_m$, com $w^{\text{priv}}_m \geq 0$ | [`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §2, cujo título é literalmente $w \mid B \ge B$, e `modelo_micro.md`, §3. **A desigualdade entrou na tela em 17/09/2026**, a pedido do autor: a lei fixa a bolsa, não a remuneração |
| mercado privado do interior isolado **menor, não nulo** | mesma §2, que descreve o interior isolado como sem demanda privada **adjacente**. **Mudança de 17/09/2026:** a tela dizia *ausente* e passou a dizer *menor*; o dado que sustenta a afirmação é o de dupla prática do slide 4, e ele não sustenta zero |
| deflator do interior **suposto menor**, com a ressalva do custo logístico | `modelo_micro.md`, §3, trata $p_m$ como nível de preços local, sem afirmar ordenação entre territórios. **Mudança de 17/09/2026:** a tela dizia *custo de vida baixo* e passou a declarar a suposição e o seu limite. O projeto não tem fonte municipal de nível de preços — ver a linha de custo de moradia no slide 17 |
| *"esta é a quarta desvantagem do lugar"* | a quarta linha da tabela de desvantagens do slide 12 até 17/09/2026, movida para cá no mesmo dia |
| R$ 10 mil (Faixa 3) e R$ 20 mil (Faixa 1) na tabela de contraste | Edital SGTES/MS nº 3/2025, item 11.1.3. Desde 16/09/2026 a tela mostra os dois valores **sem os rótulos de faixa**: o contraste é "Capital ou metrópole" contra "Interior isolado" |
| **20 horas semanais** | Edital SGTES/MS nº 3/2025, item 11.3.b |
| Retomada de **7,7%** exclusivos do setor público e **72,4%** em dupla prática | mesma linha do slide 4 — Scheffer et al. (2025), cap. 13, Figura 1, p. 254. **É retomada da mesma medição, não número novo:** há uma fonte, uma linha de proveniência e uma única medição por trás, e o slide 11 a usa como razão de $w^{\text{priv}} > 0$. **Os dois percentuais saíram da tela do slide 11 em 16/09/2026, mantidos por rastreio:** a compressão os repetiu no destaque em citação e a revisão do mesmo dia trocou a repetição por **remissão** — *"Pela dupla prática do slide 4, $w^{\text{priv}} > 0$ é a regra, não a exceção"*. Repetidos ou não, vale a mesma ressalva de cobertura: é **amostra de cirurgiões**, não o conjunto dos especialistas |
| Degrau de **R$ 5 mil** — *"a política aposta que R$ 5 mil compensam o lugar"* | Edital SGTES/MS nº 3/2025, item 11.1.3. Retomada do mesmo degrau dos slides 7, 8 e 15; linha acrescentada em 16/09/2026 |

### Slide 15 — Implicações para o PMM-E

| Número | Fonte |
|---|---|
| $V_{im}$ integrado, **sem termo de erro**, e a abertura de $c_{im}$ em dois blocos | `docs/02_teoria/modelo_micro.md`, §2.4 e §3. **Mudança de 17/09/2026:** o documento canônico escreve $V_{im}$ com $+\,\varepsilon_{im}$; a tela não o exibe, por pedido do autor — esta banca é estritamente teórica. A supressão é de tela, não de teoria |
| $\mathbf{B}_m$ e $\mathbf{w}^{\text{priv}}_m$ em negrito | decisão de composição de 17/09/2026, a pedido do autor; não altera nenhum valor |
| $c_{im} = c_0(IVS_m) + \eta_i$, a forma reduzida do custo | idem, §3 |
| condição de aceitação $\frac{B_m + w^{\text{priv}}_m}{p_m} - c_0(IVS_m) \geq \bar{v}_i$, e a vaga preenchida com ao menos um candidato | idem, §4.1. **Veio do slide da hipótese em 17/09/2026** |
| $\Delta B_m / p_m > \Delta c_0$, com $\Delta B_m = \text{R\$ } 5.000$ | idem, §4.1, e Edital SGTES/MS nº 3/2025, item 11.1.3. **Veio do slide da hipótese em 17/09/2026** |
| *"O que **Moehling, Redding & Rossi-Hansberg e Choné & Ma** não têm: remuneração fixada por **regra pública sobre um índice territorial**"* | idem, §3. Desde 16/09/2026 a frase **nomeia os três** na tela, no lugar de "nenhuma das três tradições": a mudança é de enunciado, não de conteúdo, e recupera os nomes que saíram do slide 9 com a tabela das três tradições |
| Tabela de derivadas ($\partial V/\partial B_m > 0$; $\partial^2 V/\partial B_m \partial w^{\text{priv}} < 0$; $\partial V/\partial p_m < 0$) | idem, §3 e §3.1 |
| $c_0'(IVS) > 0$ — *"o custo cresce com o índice"* | **divergência declarada com o documento canônico**, que escreve $c_0'(IVS) \gtrless 0$ em `modelo_micro.md`, §3.1. Decisão do autor de 17/09/2026; ver `P11` |
| As três dimensões do IVS 2010 e seus indicadores | **Saíram deste slide em 17/09/2026 e estão no slide 6**, com a linha de proveniência lá. Aqui restou a remissão "IVS e suas dimensões, do slide 6" |

### Slide 16 — Hipótese do trabalho

| Número | Fonte |
|---|---|
| H1 e $\partial \Pr(\text{preenchimento})/\partial (\mathbf{B}_m/p_m) > 0$ | [`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §4.2, e `modelo_micro.md`, §4.2 |
| a margem é o **preenchimento**, não a permanência | mesma §4.2, que registra a redução a uma hipótese como decisão da banca, de 14/09/2026 |
| Condição de aceitação, leitura do lado esquerdo e $\Delta B_m = \text{R\$ } 5.000$ | **Saíram deste slide em 17/09/2026 e estão no slide 15**, a pedido do autor: aqui ficou só a enunciação da hipótese |

### Slide 17 — Disponibilidade de dados

| Número | Fonte |
|---|---|
| 1.295 células estabelecimento–curso, 368 municípios (desfecho) | quadro de vagas do ciclo 1, chamada 1. **Saíram da tela deste slide em 16/09/2026, mantidos por rastreio:** a linha de preenchimento passou a dizer só "quadros do edital", com a coluna **Grau** no lugar das contagens. Os dois números seguem na tela nos slides 5 e 7 |
| **2.815 municípios**, ciclos 1 a 3 (cobertura do instrumento) | `output/aquisicao/quadro_vagas_consolidado.parquet`, 47.475 linhas, `ciclo` ∈ {1, 2, 3}; contagem verificada em 16/09/2026. **Os 2.815 municípios saíram da tela em 16/09/2026, mantidos por rastreio:** a tabela deste slide diz só "edital e quadro de vagas, ciclos 1 a 3". A contagem segue sendo a cobertura do instrumento |
| CNES mensal, jun/2024 a jul/2026 | `output/avaliacao_impacto/dados/painel_municipio_curso_mes.parquet`; competências `202406` a `202607` no `manifesto_figuras.json`. A janela de **12 meses prévios** que a tela exibe na linha de equipe $L$ é a do estoque `estoque_pre_por_10k`, definido em [`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §3; as competências do painel nunca foram à tela |
| RAIS nunca adquirida; CNES sem carga horária nem renda; residência do profissional é sigilo fiscal; sem fonte municipal de custo de moradia | [`04_dados/02_inventario_dados_por_outcome.md`](../../04_dados/02_inventario_dados_por_outcome.md) |
| Tipologia territorial em 4 estratos; REGIC 2018 e RMs/RIDEs 2022 (IBGE) | `docs/auditorias/09_tipologia_territorial.md`. **Saiu da tela em 17/09/2026, mantida por rastreio:** a linha de custos geográficos deixou de ser proxy própria na tabela, porque o autor pediu que todo o custo do lugar entrasse pelo IVS. A tipologia continua no repositório e no inventário |
| **IVS 2010** como proxy do custo do lugar, e a coluna *"por onde entra"* de cada ausência | [`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md), §3, e `modelo_micro.md`, §3 e §3.1 — a correspondência ausência → dimensão do IVS é a mesma do mapeamento canônico. **Entrou na tela em 17/09/2026.** A distância da família não entra pelo índice: fica em $\eta_i$, o desvio individual da forma reduzida |
| *"quanto maior o índice, maior o custo"* | **divergência declarada com o documento canônico** — ver `P11` |
| CNES físico (leitos e equipamentos) mapeado, competências não baixadas; SIH bloqueado | inventário de dados, e `docs/06_execucao/06_backlog_wp3_wp4_wp5.md` |

### Slide 16 da estrutura anterior — Desafio metodológico

> [!IMPORTANT]
> **Slide removido do deck em 17/09/2026, seção mantida por rastreio.** A pedido
> do autor, a apresentação deixou de tratar a separação entre efeito da bolsa e
> efeito da vulnerabilidade. **Todos** os números abaixo saíram da tela na mesma
> data; nenhum foi alterado ou desmentido, e todos continuam registrados em
> [`05_identificacao/16`](../../05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
> §3.5. A seção fica aqui pela regra 7 da seção 4 — número que já foi exibido à
> banca continua rastreável.

| Número | Fonte |
|---|---|
| 177 dos 368 municípios com faixa publicada diferente da recalculada | portão R1, `docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md`, §"Correção de 14/09/2026", e `a01b_reconstrucao_regra_faixa.json` |
| 37 municípios com IVS ≤ 0,400 na Faixa 1; 94 na Faixa 2; os intervalos das três faixas se sobrepõem | `output/rdd_bolsa/a01b_reconstrucao_regra_faixa.json`, gerado por `scripts/rdd_bolsa/01b_reconstruir_regra_faixa.py` |
| Em ±0,050 de **0,500**, os dois lados são **100% Faixa 1** (20 municípios de um lado, 11 do outro) | idem; `14_plano_implementacao_rdd_bolsa.md`, tabela de janelas |
| Maior IVS da Faixa 3 é **0,372**; em ±0,010 de **0,400** não há Faixa 3 de nenhum lado | idem. Na tela, só o **0,372**; a janela de ±0,010 sustenta a frase e nunca foi exibida |
| 83 municípios fora da melhor regra de limiar; **41 promovidos** com mediana de população **7.933** contra **32.179** dos **42 rebaixados**, e muito mais interior remoto | idem, §"a variação que sobra não é exógena". Os cinco números e o "muito mais interior remoto" estão na tela, no terceiro achado do slide 16 |
| **R$ 10 mil a mais** entre Faixa 1 e Faixa 3 | diferença entre os R$ 20 mil e os R$ 10 mil do item 11.1.3 do Edital SGTES/MS nº 3/2025 — é o contraste entre extremos, não o degrau de **R$ 5 mil** entre faixas vizinhas dos slides 7, 8, 13 e 15. Linha acrescentada em 16/09/2026 |
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
público, **80,1%** dos cirurgiões atendem SUS. Desde a compressão de 16/09/2026 a
frase **não vai à tela**: ela e os 80,1% que a contradizem ficaram no bloco
`**Nota de produção — o que não dá para dizer**` do slide 4, como advertência a
quem monta o deck e a quem responde à banca. O defensável é o inverso: o que é
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
extensão passou a ser creditada ao projeto no **slide 12**. Reinhardt permanece
como referência secundária em
[`docs/02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md), seção 2.3.

### `P1` — a comparação do degrau com a régua australiana é do projeto

Nenhum artigo compara o PMM-E a nada. Dizer que +50% "cai dentro da faixa" de
37% a 64% é leitura do projeto sobre Scott et al. (2013). Apresentar como tal.

### `P2` — comparabilidade do prêmio com a bolsa

Os prêmios compensatórios da literatura são sobre a **renda total** do médico. A
bolsa do PMM-E remunera **20 horas semanais**. Traduzir R$ 5 mil em "+50%" e
comparar com a régua australiana pressupõe que a bolsa seja a fração dominante
do rendimento — hipótese sobre composição de vínculos, não dado. O **slide 7**
declara essa ressalva na tela, e o slide 13 mostra por que a hipótese é frágil.

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
estavam errados (os mesmos 177 de 368 da seção 2) e o sinal de `F1` invertia. Desde então as três figuras usam a
**faixa publicada**. A categoria recalculada só aparece no
`manifesto_figuras.json`, como detalhe descritivo, e no slide 5, para mostrar
que é piso e não critério. Não comparar valores das figuras atuais com os da
versão anterior.

### `P5` — Demografia Médica 2025: o que está conferido no original e o que não está

Situação em 16/09/2026, por número:

| Número | Estado |
|---|---|
| **72,4% / 19,9% / 7,7%** de atuação dos cirurgiões — na tela no slide 4; o slide 13 os retoma por remissão | ✅ **conferido na fonte primária**, cap. 13, Figura 1, p. 254, com a frase transcrita acima |
| 597 mil médicos; 353.287 especialistas (59,1%); 453 no DF, 244 em SP, 68 no MA, 70 no PA | conferido em **cobertura** (Agência Brasil, abril de 2025; portal Afya) |
| **Sudeste 55,4%**, Sul 16,7%, Nordeste 14,5%, Norte 5,9% | ⚠️ **ressalva de fonte.** Uma leitura do **PDF integral não localizou** esses percentuais. Estão conferidos **apenas em cobertura**, no portal Afya: *"A região Sudeste concentra 55,4% dos especialistas, seguida pelo Sul (16,7%) e Nordeste (14,5%). Já o Norte responde por apenas 5,9%"*. Os números **não são removidos** do slide; a citação é atribuída ao estudo e a checagem no original fica pendente |

Pendência residual, **não bloqueante**: o PDF da *Demografia Médica no Brasil
2025* ainda não está preservado em `data/raw/` com hash, como manda a regra 5 da
seção 4. Ao registrá-lo, conferir no original a distribuição regional de
especialistas.

### `P6` — as figuras do slide 4 fora do pipeline, e o que a medição encontrou

**Estado em 17/09/2026: a parte de forma está fechada; a de cobertura, não.**

Até 16/09/2026, `E1` (especialistas por 100 mil habitantes por UF) e `E2`
(deslocamento médio para alta complexidade por região) vinham do **deck do
grupo**, montadas fora do pipeline — o que **contraria a regra de proveniência do
`CLAUDE.md`**: gráfico produzido fora do pipeline não entra em apresentação. Com
o pedido de "gráfico > texto" para o slide 4, a exceção deixou de ser
sustentável: pôr **mais** peso numa figura fora do pipeline agrava a violação em
vez de tolerá-la.

As três figuras do slide 4 passaram então a ser geradas por
`scripts/apresentacao/gerar_figuras_banca1.py`, com os valores declarados como
constantes com fonte, página e cobertura, e repetidos no manifesto.

**A figura de UF do grupo não era usável, e isso foi medido.** Calibrando a
imagem pelos dois únicos rótulos impressos — DF 453,5 e MA 68,2 —, as dezesseis
barras dão a série abaixo, contra os quatro valores que esta seção registra:

| UF | Barra da figura do grupo | Série citada nesta seção |
|---|---:|---:|
| DF | 453,5 | 453 |
| SP | ≈ 419 | **244** |
| PA | ≈ 135 | **70** |
| MA | 68,2 | 68 |

Só os dois extremos rotulados batem; as outras catorze barras não correspondem à
fonte declarada, e a série que elas desenham **não tem origem conhecida**. Por
isso `E1` passou a ser a figura dos **quatro** valores com fonte registrada, e
não das 27 unidades: a tela perde o panorama completo, e não ganha uma série que
ninguém consegue rastrear.

**O que fecha:** registrar em `data/raw/` a tabela por UF da *Demografia Médica
2025*, com hash — o mesmo PDF que `P5` já pede —, e trocar `E1` pela figura das
27 unidades. Enquanto isso não acontecer, o panorama completo por UF **não vai à
tela**, em nenhuma versão.

### `P7` — os valores do gráfico de deslocamento não têm fonte primária confirmada

A série de `E2` — **Norte 276 km, Centro-Oeste 256, Nordeste 179, Sudeste 107,
Sul 101** — **não teve fonte primária confirmada**. A origem provável é a
pesquisa **REGIC 2018 do IBGE**, na parte sobre deslocamentos da população para
serviços de saúde, mas a página da pesquisa **retornou HTTP 403** na tentativa de
verificação, e nenhuma tabela publicada foi localizada com esses cinco valores.

Consequência prática: **276 km** e **101 km** aparecem no texto do slide 4 e no
gráfico, e são hoje os dois únicos números da apresentação sem rastreio até uma
fonte checada. Desde 16/09/2026 eles aparecem **sem ressalva na tela**: o corpo
do slide perdeu a frase "fonte primária ainda não confirmada", e o "a confirmar"
ficou só na linha de fontes, que desce a nota de rodapé. Enquanto a checagem não
se fizer, tratá-los como **ilustrativos** e não como estatística do trabalho.

**O que mudou em 17/09/2026.** `E2` passou a ser gerada por script, e o rodapé
da figura — que é **conteúdo de tela** — diz *"atribuído à REGIC 2018 (IBGE);
fonte primária a confirmar"*. A ressalva voltou à tela, agora dentro da figura.
**Gerar não confirma fonte:** a pendência continua aberta, e o manifesto marca a
série com `fonte_primaria_confirmada: false`.

**O que fecha:** localizar a tabela da REGIC 2018 sobre deslocamentos para
serviços de saúde e registrar o arquivo em `data/raw/` com hash. Se a fonte não
for localizada, os valores saem da tela.

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

**Impedimento de uso.** A tabela fica **fora do slide 7** e fora de qualquer
slide. Números sem origem em `output/` e que não se reproduzem não entram em
apresentação — e, ainda que se reproduzissem, seriam inclinações **sem grupo de
comparação**, que não se leem como efeito do programa (é a mesma razão que tirou
`oferta_antes_depois_por_faixa.png` do deck). A **série mensal por faixa** pode
entrar como contexto descritivo, pelo caminho normal: gerada por script e lida
de `output/`.

---

### `P9` — a figura que faltava ao desafio metodológico · **fechada em 17/09/2026**

**Fechada por remoção do slide, não por produção da figura.** O slide do desafio
metodológico saiu do deck a pedido do autor, e com ele a necessidade da figura
que lhe faltava: a dispersão do **IVS 2010** contra a **faixa publicada**, com
`0,400` e `0,500` marcados.

O insumo continua disponível —
`output/rdd_bolsa/matriz_municipio_regra_ivs.csv`, com IVS, categoria recalculada
e `valor_anunciado_mensal_brl` por município —, e a receita de produção continua
valendo: acrescentar a figura a `scripts/apresentacao/gerar_figuras_banca1.py`,
lendo de `output/`, e registrá-la na seção 1 deste documento. **A pendência
reabre** se a apresentação voltar a tratar da identificação.

### `P10` — a retaguarda é municipal, e o serviço é em parte regional

Aberta em 17/09/2026 a partir do item **F5** do PR de ajuste estrutural. `F2`
mede colegas da mesma especialidade **no município**, e é dela que sai a
afirmação de tela *"a Faixa 1 compensa isolamento, não cobertura"*. O quadro de
vagas do ciclo 1 mostra que boa parte do serviço é regional: **552 de 1.295
células (42,6%)** estão em estabelecimento de gestão estadual, e **93 dos 460**
CNES têm "REGIONAL" no nome, com 339 células (26,2%). Para um hospital regional,
a retaguarda relevante é a do estabelecimento e da região, não a do município.

A medida **não é falsa** — é mais estreita que a frase. E o descasamento tem
interesse próprio: o incentivo é fixado pelo IVS do **município-sede**, e a
clientela é a da **região**. Isso é propriedade do desenho da política, não
defeito da medição.

**O que fecha:** decisão do autor, que o próprio PR registra como tal — ou uma
linha de limitação no terceiro build do slide 5, ou o descasamento como argumento
próprio da motivação. O teste de deslocamento intrarregional que verificaria o
ponto depende da malha territorial versionada, item F4 do mesmo PR, e está
bloqueado. Nada entrou na tela sem essa decisão.

### `P11` — a tela diz que o custo cresce com o IVS; o documento canônico diz que o sinal é ambíguo

Aberta em 17/09/2026, por decisão do autor. O pedido foi *"deixa os custos todos
dentro do IVS, e remove nuances de ambiguidade, p dizer diretamente que o custo é
crescente no IVS"*. Foi aplicado nos slides **6**, **15** e **17**.

**O que o documento canônico diz.** Em
[`modelo_micro.md`](../../02_teoria/modelo_micro.md), §3.1, o sub-índice de
**capital humano** opera nos dois sentidos: carência sanitária eleva o benefício
marginal de atender — o que **reduz** o custo laboral líquido de um médico
altruísta — e ao mesmo tempo sinaliza falta de insumo, o que **eleva** o cansaço.
Daí $c_0'(IVS) \gtrless 0$, com o sinal declarado como questão empírica. A
hipótese **H4** de
[`hipoteses_e_viabilidade_empirica.md`](../../02_teoria/hipoteses_e_viabilidade_empirica.md),
§4, é exatamente o teste desse sinal, e a §3 do mesmo documento diz, na letra,
que **não se pode assumir $c_0'(IVS) > 0$ a priori**.

**O que está na tela.** Que as três dimensões apontam para o mesmo lado, e que o
custo cresce com o índice. É simplificação de exposição, declarada nas notas de
produção dos três slides e registrada como **pendência 9** no documento de
conteúdo.

**O que fecha.** Decisão do autor, em uma de duas direções: (a) fixar o sinal no
documento canônico, com justificativa econométrica, o que muda a teoria do
projeto e a hipótese H4; ou (b) devolver à tela uma ressalva de uma linha. Nada
foi mudado na teoria por conta da tela.

## 4. Regra permanente

1. Figura derivada de base do repositório é gerada por script e lida de
   `output/`.
2. Figura de fonte externa é preservada em `figuras/`, com a fonte na legenda e
   uma linha na seção 1.
3. Figura conceitual recebe rótulo de ilustração do modelo.
4. Número exibido sem linha na seção 2 é erro, não detalhe editorial. "Exibido"
   é o **corpo do slide**: desde 16/09/2026 a linha `**Fontes:**` e o bloco
   `**Nota de produção.**` não vão à tela, e o que só aparece neles fica
   registrado aqui como fora da tela (ver a nota no topo).
5. Documento oficial citado em slide tem cópia em `data/raw/aquisicao/`, com
   hash registrado aqui.
6. Número que não se reproduz a partir de `output/` não vai à tela, ainda que
   venha de material do grupo.
7. Número que sai da tela não é apagado daqui. A linha fica, com a data da saída
   e a marca **"mantida por rastreio"**: deck e documento mudam de versão, e o
   que já foi exibido à banca precisa continuar rastreável.
