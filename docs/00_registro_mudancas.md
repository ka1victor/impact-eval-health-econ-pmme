# 00. Registro de mudanças da documentação

> **Finalidade:** rastrear alterações **estruturais** da documentação — arquivo
> criado, fundido, removido, renomeado ou movido — e o motivo de cada uma.<br>
> **Não registra:** correção de texto, atualização de número ou acréscimo de
> seção dentro de um documento que permaneceu no mesmo lugar.<br>
> **Regra:** quem move informação de lugar abre entrada aqui no mesmo commit.

---

## 09/09/2026 — Seção de apresentações, absorção do documento 18 e limpeza de referências

Motivo: preparar a entrega da banca 1 e eliminar as três duplicações de conteúdo
teórico que o projeto vinha carregando.

### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| [`00_registro_mudancas.md`](00_registro_mudancas.md) | este registro | a documentação já tinha sido reorganizada antes sem deixar rastro do que foi para onde |
| [`07_apresentacoes/README.md`](07_apresentacoes/README.md) | regra da seção de apresentações | entregas de banca não tinham lugar próprio e vinham sendo tratadas como documento de teoria |
| [`07_apresentacoes/banca1/README.md`](07_apresentacoes/banca1/README.md) | escopo, estado por bloco e pendências bloqueantes | declarar que a banca 1 termina na viabilidade empírica |
| [`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md) | arco, regras de composição, rastreio do feedback e defeitos do deck anterior | feedback de banca sem ajuste rastreável não é feedback incorporado |
| [`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md) | conteúdo dos 15 slides, com título, corpo, visual, fonte e nota | fonte de verdade do deck; o `.pptx` passa a ser artefato derivado |
| [`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md) | origem e reprodutibilidade de cada número exibido | a regra de proveniência do projeto valia para `output/`, mas não estava sendo aplicada a slide |

### O que foi removido

| Arquivo removido | Para onde o conteúdo foi | Motivo |
|---|---|---|
| `02_teoria/18_modelo_teorico_slides_apresentacao.md` | [`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md), seções 3 e 3.2 | mantinha uma segunda versão da mesma teoria, com a adaptação ao PMM-E e as equações dos complementos que faltavam no documento canônico. Com o conteúdo de slides em `07_apresentacoes/`, o documento 18 deixou de ter função |

### O que mudou de lugar dentro da documentação

| Conteúdo | Antes | Agora | Motivo |
|---|---|---|---|
| Adaptação da equação de Moehling ao PMM-E, com $B_m(IVS_m)$ | documento 18 | `modelo_micro.md`, seção 3 | o modelo canônico parava no custo integrado e nunca chegava à bolsa |
| Equações originais de Redding & Rossi-Hansberg e de Choné & Ma | documento 18 | `modelo_micro.md`, seção 3.2 | mesma razão |
| Composição do IVS e correspondência com os blocos de custo | documento 18 **e** `hipoteses_e_viabilidade_empirica.md`, seção 3 | `modelo_micro.md`, seção 3.1 (única cópia) | estava duplicado em dois documentos com redações divergentes |
| Consequência econométrica da não monotonicidade de $c_0'(IVS)$ | `hipoteses_e_viabilidade_empirica.md`, seção 3 | permanece lá, agora sem repetir a teoria | teoria e consequência para estimação são coisas distintas |
| Hipótese de heterogeneidade clínico versus cirúrgico | `hipoteses_e_viabilidade_empirica.md`, hipótese 3 | mesma seção, agora como 4.1, rebaixada a heterogeneidade pré-declarada | não é hipótese principal e concorria com as três centrais |

### O que foi acrescentado a documentos existentes

| Documento | Acréscimo | Motivo |
|---|---|---|
| [`01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md`](01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md) | seção "Formulação curta canônica": a pergunta em uma linha, as duas margens e o bloco "o que a pergunta não é" | feedback da banca pedia simplificação da pergunta; a versão curta precisa ser canônica, não só de slide |
| [`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md) | seção 4 — condição de aceitação, condição de degrau $\Delta B/p > \Delta c_0$ e estática comparativa que gera H1 a H4 | feedback da banca pedia derivar as hipóteses diretamente da teoria; antes elas apareciam apenas listadas em outro documento |
| [`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md) | seção 4 reescrita como leitura empírica das derivadas, com 4.2 mapeando as hipóteses canônicas nas três apresentadas e 4.3 fixando linguagem permitida | as hipóteses eram postuladas no documento empírico, sem ligação formal com o modelo |
| [`03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md`](03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md) | Sivey et al. (2012) na tabela de estudos centrais; seção 7 declarando a lacuna que o trabalho ocupa; seção 8 de referências | Sivey era citado em outro documento sem estar catalogado; a lacuna estava implícita |
| [`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md) | seção 4.1 — números publicados que não reproduzem nas bases | achado da conferência da banca 1, detalhado abaixo |
| [`06_execucao/05_roadmap_execucao.md`](06_execucao/05_roadmap_execucao.md) | bloco "Entrega de banca 1", com estado item a item | a entrega existia e não aparecia em nenhum roadmap |
| [`README.md`](README.md) | seção 1.1 apontando este registro; seção 07 na navegação; regra de precedência ampliada | — |

### Correções de referência

| Problema | Onde | Correção |
|---|---|---|
| Link para `04_dados/20_dossie_bases_dados_saude_brasil_pmme.md`, arquivo inexistente | `README.md` | referência removida |
| Links para `02_teoria/17_fundamentacao_teorica_formacao_utilidade_regressores.md`, arquivo inexistente | três documentos de `90_arquivo_historico/` | redirecionados para `02_teoria/modelo_micro.md` |
| Referências por número — "documento 17", "documento 19", "documentos 12–14" — a arquivos que já haviam sido renomeados | `README.md`, seções 3 e 6, e documento 19 | substituídas por nome e link do arquivo vigente |

### Achado de proveniência registrado

A figura de distribuição regional do PMM-E usada no material anterior **não é
reprodutível** a partir de `data/`. Apenas o Nordeste, 60,3%, coincide com o
ciclo 1 de `pmm_especialistas_nominal.csv`. Na mesma base, o Sudeste é 23,0% e
não 10,6% — diferença de 12,4 pontos percentuais, no sentido de exagerar a
redistributividade do programa. Recortes alternativos testados, ciclos 1+2,
série histórica de dez/2025 e contagem de municípios distintos, também não
reproduzem o conjunto.

Registrado em [`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md),
seção 4.1, e detalhado em
[`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md).

### Conteúdo do deck anterior que foi descartado

O arquivo `PEE__Modelo_econômico.pptx` trazia, no slide de literatura, seis
referências de economia do crime — Becker (1968), Ehrlich (1973), Fella &
Gallipoli (2014), Bennett & Ouazad (2020), Dix-Carneiro et al. (2018),
Deshpande & Mueller-Smith (2022) — sem relação com escolha locacional médica.
Nenhuma delas entrou na documentação. O slide foi refeito com a literatura
canônica do projeto.

---

## 09/09/2026 — Quarta revisão da banca 1: seis seções, 18 slides e edital no repositório

Motivo: o sumário do conteúdo usava "Parte I/II/III", que não é a estrutura da
banca 1. A estrutura correta tem seis seções — motivação, pergunta, literatura
teórica, modelo microeconômico, hipóteses, viabilidade empírica — e cada uma
pode ocupar quantos slides o argumento pedir. O conteúdo foi reescrito para
essa estrutura e aprofundado onde estava raso.

### O que mudou em [`07_apresentacoes/banca1/02_conteudo_slides.md`](07_apresentacoes/banca1/02_conteudo_slides.md)

| Seção | Antes | Agora |
|---|---|---|
| 1. Motivação | 3 slides | 8 slides, em três blocos: **problema** (retrato nacional da Demografia Médica 2025 e manchetes; nossos dados por faixa; as desvantagens na visão do médico), **política** (o que é o PMM-E — lei, quem participa, aprimoramento em serviço, 16 cursos, como a vaga chega, ciclo 1 por região; e a regra IVS → faixa → bolsa) e **efeito incerto** (evidência a favor; evidência contra; o preenchimento do ciclo 1 por faixa e por estrato) |
| 2. Pergunta | 1 slide | 1 slide, com a leitura em dois objetos — preço e desvantagem |
| 3. Literatura teórica | tabela | tabela com parágrafo dizendo o que cada tradição resolve |
| 4. Modelo | 2 slides | 4 slides: decisão; **o que a bolsa paga e o que não paga** (novo — bolsa e mercado local); custo; **o IVS organiza o custo** (novo — as três dimensões do índice e o sinal ambíguo de $c_0'$) |
| 5. Hipóteses | 1 slide | 1 slide, derivação em quatro passos |
| 6. Viabilidade | 1 slide | 1 slide, com custo de vida e distância da família na tabela |

### O que foi criado

| Arquivo | Conteúdo | Por que existe |
|---|---|---|
| `data/raw/aquisicao/ivs_regra/edital_sgtes_03_2025_dou.pdf` | texto integral do Edital SGTES/MS nº 3/2025 (DOU, 24/07/2025), SHA-256 `417c82d9…d9afb2` | o repositório tinha só o FAQ da bolsa; o slide "O que é o PMM-E" cita itens do edital (objeto, requisitos, cursos, escolha de locais, barema, bolsa) que precisavam de fonte primária local |
| `output/apresentacao_banca1/vagas_ciclo1_por_regiao.png` | células e vagas imediatas do ciclo 1 por região | figura do slide 6, gerada por script |
| `output/apresentacao_banca1/preenchimento_ciclo1.png` | proporção de células preenchidas por faixa anunciada e por estrato territorial | figura do slide 10, gerada por script a partir das tabelas descritivas do módulo A4 |

### O que foi acrescentado a documentos existentes

| Documento | Acréscimo |
|---|---|
| [`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md) | arco reescrito nas seis seções; títulos dos 18 slides; quarta rodada de ajustes; tempo estimado |
| [`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md) | figuras F5 e F6; números dos slides 3, 5, 6 e 10; fontes documentais externas conferidas em 09/09/2026 |
| [`07_apresentacoes/banca1/README.md`](07_apresentacoes/banca1/README.md) | estrutura em seis seções; estado por seção |
| `scripts/apresentacao/gerar_figuras_banca1.py` | funções `figura_vagas_por_regiao` e `figura_preenchimento_ciclo1`; manifesto com as novas entradas |

### Fontes externas conferidas para o slide 3

Demografia Médica no Brasil 2025 (Scheffer et al., FMUSP/AMB): 597 mil
médicos em 2024, 353.287 especialistas (59,1%); Sudeste com 55,4% dos
especialistas e Norte com 5,9%; 453 especialistas por 100 mil habitantes no
Distrito Federal, 68 no Maranhão e 70 no Pará — conferidos na cobertura da
Agência Brasil (abril de 2025). Portaria GM/MS nº 7.061/2025 reconheceu
situação de urgência em saúde pública por 24 meses em razão do tempo de espera
na atenção especializada. A manchete do Senado Notícias de 25/09/2025 foi
conferida na página original.

---

## 09/09/2026 — Terceira revisão da banca 1: escopo teórico e saída de Reinhardt

Motivo: terceira rodada de revisão do autor, fixando o escopo da banca.

### Regra de escopo

**A banca 1 é teórica.** Fora da motivação, nenhum slide traz literatura
empírica, econometria ou estimação. A motivação é a exceção declarada: ali,
antes da pergunta, entra evidência sobre o que se pode esperar da política,
inclusive de trabalhos empíricos, porque é o que justifica perguntar. A regra
está em
[`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md),
seção 2.4.

Consequências: o slide 11 foi reescrito sem vocabulário econométrico — passa a
perguntar se há como medir cada peça do modelo e declara as duas que ficam de
fora, a renda no mercado privado local e a distância até a família. O slide 5
descreve o desenho de cada estudo em palavras comuns.

### Reinhardt retirado do slide 7

Choné e Ma (2011) já escrevem o custo de atender como $C(q; L, K)$: equipe e
capital instalado já entram no modelo por essa via. O que Reinhardt
acrescentaria é que esses insumos também elevam o benefício produzido — mas
escrever $B(q; L, K)$ em vez de $B(q)$ é **extensão deste projeto**, não dele. A
citação saiu do slide e a extensão passou a ser creditada ao projeto.

Reinhardt permanece como referência secundária em
[`02_teoria/modelo_micro.md`](02_teoria/modelo_micro.md), seção 2.3, agora com a
distinção correta entre os dois canais e com a referência de **1972**, cuja
forma geral $Q = f(H, X_1, \ldots, X_n)$ é verificável, ao lado do livro de 1975
que o projeto citava sem transcrever.

### Slide 5 reescrito como narrativa

No lugar da tabela de quatro estudos, três movimentos: **funciona** — o
experimento mexicano que sorteou o salário anunciado; **é caro** — a régua
australiana e o custo-efetividade brasileiro; **não segura** — a retenção
americana após o fim da obrigação. Fecha com o degrau do PMM-E dentro da faixa
que a literatura estima ser necessária, e com o fato de que no primeiro ciclo a
bolsa maior não trouxe mais gente.

### Títulos simplificados

"Três primitivas teóricas" virou **"De onde vem o modelo"**; "A decisão
locacional do médico" virou **"Como o médico escolhe onde trabalhar"**.

---

## 09/09/2026 — Segunda revisão da banca 1: evidência internacional, retaguarda profissional e estrutura em três partes

Motivo: segunda rodada de revisão do autor, ponto a ponto, sobre a versão em
markdown.

### Estrutura

A apresentação passou de 12 para **11 slides**, organizados em **Parte I —
Introdução** (motivação, pergunta), **Parte II — Teoria** (literatura teórica,
modelo microeconômico, hipóteses) e **Parte III — Empiria** (viabilidade
empírica). O slide de perguntas foi eliminado: a apresentação termina na
viabilidade.

### Mudanças de conteúdo

| Slide | Mudança |
|---|---|
| 3 | passou a explicar as desvantagens territoriais **na perspectiva do médico**. Nova figura de retaguarda profissional. Saíram as manchetes e o gráfico de deslocamento por região |
| 4 | explicação em três passos de como o IVS vira valor de bolsa |
| 5 | refeito: deixa de mostrar a evolução da oferta e passa a trazer **evidência externa** sobre se incentivo financeiro atrai médico para área desassistida |
| 7 | equações corrigidas para renderizar em tabela; Choné & Ma e Reinhardt em linhas separadas, cada um com sua equação original |
| 10 → 11 | a tabela de como cada objeto aparece nos dados saiu das hipóteses e entrou na viabilidade empírica |

### Por que o gráfico de deslocamento saiu

Verificação no edital: a Portaria GM/MS nº 7.177/2025 declara quatro objetivos —
**provimento, fixação, equilíbrio territorial e formação**. Reduzir deslocamento
de paciente **não é objetivo declarado**; fluxo de usuários aparece apenas como
um entre vários critérios de priorização de vagas (Edital SGTES/MS nº 2/2025,
itens 3.8–3.10). Além disso a figura media custo do paciente, quando o slide
trata do custo do médico.

### Acrescentado à literatura empírica

[`03_literatura_empirica/19_...md`](03_literatura_empirica/19_literatura_empirica_escolha_locacional_medicos.md)
ganhou a seção 7, com evidência sobre incentivos financeiros para provimento em
áreas desassistidas, em quatro blocos: o que move a alocação, a ordem de
grandeza do prêmio exigido, a evidência de que é caro ou insuficiente, e a
permanência que não acompanha a atração. Dez referências novas. Os números de
Costa, Nunes e Sanches (2024) foram conferidos no PDF do working paper —
elasticidade de 0,4 e 0,7, redução de 12,4% do desequilíbrio a US$ 15,7 milhões
por ponto percentual contra US$ 2,2 a 5,1 milhões das cotas.

Registro relevante para o desenho: **nenhum estudo dessa literatura usa RDD**. A
evidência causal disponível é RCT de oferta salarial, DiD sobre elegibilidade
geográfica ou coorte observacional.

### Figuras

| Arquivo | Situação |
|---|---|
| `output/apresentacao_banca1/retaguarda_por_faixa.png` | **nova**: colegas da mesma especialidade por município, por faixa |
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | continua sendo gerada, mas **saiu do deck** |
| `figuras/motivacao_manchetes.png`, `figuras/deslocamento_por_regiao.png`, `figuras/especialistas_por_uf.png` | preservadas, **não usadas** |

Nenhuma figura de fonte externa entra mais no deck: as três em uso são geradas
por script e a quarta é ilustração conceitual do modelo.

### Ressalva de citação

A equação de Reinhardt exibida no slide 7 é a forma geral do artigo de **1972**
no *Review of Economics and Statistics*, não do livro de 1975 que o projeto
cita. Registrado em
[`07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`](07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md),
seção 3.

---

## 09/09/2026 — Revisão de conteúdo da banca 1, população do Censo 2022 e achado sobre `populacao_2010`

Motivo: revisão ponto a ponto do autor sobre a primeira versão em markdown, e
a descoberta de que o repositório não tinha denominador populacional válido.

### Conteúdo

A apresentação passou de 15 para **12 slides**, na margem de **preenchimento**
apenas. Mudanças por slide em
[`07_apresentacoes/banca1/01_roteiro_narrativo.md`](07_apresentacoes/banca1/01_roteiro_narrativo.md),
seção 4. As hipóteses foram reduzidas a duas — remuneração real com sinal
positivo e custo locacional com sinal negativo sobre a probabilidade de
preenchimento — e o slide passou a declarar como cada objeto aparece nos dados
e o limite de identificação.

### Criado

| Arquivo | Conteúdo |
|---|---|
| `scripts/aquisicao/06_adquirir_populacao_censo2022.py` | baixa a população residente municipal do Censo 2022 (IBGE/SIDRA, tabela 4709), com bruto em `data/raw/aquisicao/populacao/` e manifesto com hash |
| `output/aquisicao/populacao_censo2022_municipios.csv` | 5.570 municípios, 203.080.756 habitantes |
| `output/apresentacao_banca1/oferta_pre_por_faixa.png` | especialistas por 100 mil habitantes em jun/2025, por faixa de bolsa |
| `output/apresentacao_banca1/oferta_antes_depois_por_faixa.png` | a mesma taxa, mensal, jun/2024 a jul/2026 |

### Removido

| Arquivo | Motivo |
|---|---|
| `output/apresentacao_banca1/distribuicao_regional.png` | participação no total confunde tamanho do programa com tamanho da população; substituída pelas figuras por habitante |

### Achado registrado

`populacao_2010`, única variável populacional de `data/`, **não é população
residente**: soma 41,85 milhões contra 190,76 milhões do Censo 2010, com razão
variando de 0,10 a 0,42 entre municípios. Afeta `estoque_pre_por_10k`, a
covariável `log_pop` dos módulos A4 e A5 e o rótulo da tabela 1 de estatísticas
descritivas. Registrado em
[`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md),
seção 4.0. As saídas históricas não foram reescritas.

### Acrescentado a documentos existentes

| Documento | Acréscimo |
|---|---|
| [`04_dados/02_inventario_dados_por_outcome.md`](04_dados/02_inventario_dados_por_outcome.md) | base derivada de população do Censo 2022; seção 4.0 |
| [`02_teoria/hipoteses_e_viabilidade_empirica.md`](02_teoria/hipoteses_e_viabilidade_empirica.md) | seção 4.2 refeita para as duas hipóteses da banca |
| [`scripts/README.md`](../scripts/README.md) | `apresentacao/` e o script de população no mapa |

---

## 09/09/2026 — Conteúdo da banca 1 em markdown, figuras versionadas e correção da figura regional

Motivo: a entrega passa a ser lida no GitHub e no Obsidian, não montada como
deck. O conteúdo deixa de ser especificação de slide e vira documento legível de
ponta a ponta, com as figuras dentro do repositório.

### Estrutura da apresentação

Reorganizada nas três partes da banca 1, no lugar dos seis blocos anteriores:

| Parte | Conteúdo | Slides |
|:---:|---|:---:|
| 1 | Motivação e pergunta | 3–7 |
| 2 | Literatura teórica, modelo micro e hipóteses | 8–12 |
| 3 | Viabilidade empírica | 13–14 |

O slide de literatura passou a liderar pela literatura **teórica**, com cada
trabalho declarando qual primitiva fornece e onde ela entra no modelo. A
evidência empírica ficou como bloco de apoio ao argumento da lacuna.

### Figuras

| Arquivo | Origem |
|---|---|
| `docs/07_apresentacoes/banca1/figuras/motivacao_manchetes.png` | externa, preservada do material anterior |
| `docs/07_apresentacoes/banca1/figuras/especialistas_por_uf.png` | externa, Demografia Médica no Brasil 2025 |
| `docs/07_apresentacoes/banca1/figuras/deslocamento_por_regiao.png` | externa, REGIC 2018 |
| `output/apresentacao_banca1/bolsa_por_faixa.png` | gerada por script |
| `output/apresentacao_banca1/distribuicao_regional.png` | gerada por script |

Criado `scripts/apresentacao/gerar_figuras_banca1.py`, que grava as duas figuras
geradas e um `manifesto_figuras.json` com hash SHA-256 da base de entrada,
recorte aplicado, data de referência e as constantes externas usadas.

### Pendência encerrada

A figura de distribuição regional foi regerada a partir de
`data/pmm_especialistas_nominal.csv`, ciclo 1. Os valores corretos são Nordeste
60,3%, Sudeste 23,0%, Norte 12,1%, Centro-Oeste 3,6% e Sul 1,0%. A versão
anterior trazia o Sudeste com 10,6%, doze pontos percentuais abaixo, o que
exagerava a redistributividade afirmada no slide. Permanece aberta apenas a
pendência de manifesto das figuras de fonte externa.

### Removido

A seção de restrições de template e a decisão sobre equações nativas em
PowerPoint saíram do documento de conteúdo. Eram específicas da produção de
`.pptx`, que deixou de ser o formato da entrega.

---

## Antes de 09/09/2026

A reorganização em seções numeradas 01 a 06, com `90_arquivo_historico/`, é
anterior a este registro e está descrita na
[`README.md`](README.md), seções 2 e 4. Os documentos 07 a 11 e as versões 15 e
16 foram arquivados naquela ocasião, sem entrada individual.
