# 45. Auditoria do adendo 48g: heterogeneidade do salto pelo porte em que o estrato do IED muda

> **Data:** 26/10/2026.<br>
> **Objeto:**
> - adendo [`48g`](../06_execucao/48g_adendo_heterogeneidade_porte_ied.md), congelado no commit `c87ed75`;
> - script `scripts/rdd_bolsa/47_heterogeneidade_porte_ied.py`;
> - saídas `output/rdd_bolsa/PO_*`;
> - doc [`57u`](../06_execucao/57u_resultados_heterogeneidade_porte.md), com as 19 decisões da seção 0 (commit
>   `808db3a`);
> - testes `tests/test_heterogeneidade_porte_ied.py`.
>
> Base: branch `claude/vigilant-mccarthy-dd92mc`, commit `bb1b7e3`.<br>
> **Referências:**
> - `CLAUDE.md`;
> - [auditoria 18](18_politicas_nos_mesmos_cortes_ivs.md), §2.5 e recomendação 5;
> - `output/aquisicao/a10_ied_aps_2024_municipio.csv` e `a10_diagnostico_cortes_normas.json`;
> - adendo 48b, doc 57n e [auditoria 38](38_auditoria_h1_vagas_imediatas.md);
> - protocolo 64, doc 57q e [auditoria 39](39_auditoria_oferta_local_corte.md);
> - `rdd_lib.py`, lida e não importada.
>
> **Método:** recálculo próprio em memória, com scripts no scratch. Nada foi gravado em `output/` além da reexecução
> do próprio 47. O recálculo não importa os scripts 47, 40, 43 e 44 nem a `rdd_lib`. Ele lê direto:
> - o JSON e o CSV do a10, e refaz a regra de G a partir das faixas de código e da tabela código × porte → estrato;
> - o IVS oficial (a08);
> - as bases de células e de municípios (`outcomes_V_*`);
> - o quadro bruto do ciclo 2 de 13/02/2026, com leitor próprio;
> - a lista nominal, a população de 2022 e o painel a09, para refazer V e os ΔB.
>
> Escrevi do zero o MQP ponderado pelo kernel triangular com descarte de colunas colineares, o CR1 e o HC1, a
> diferença em descontinuidades com retas por grupo × lado e o Holm.
> **Estatuto do que se audita:** `ADENDO_48G_POS_RESULTADO`, heterogeneidade descritiva pós-resultado. O contraste é
> o pacote do corte, não a participação no PMM-E nem o incentivo de R$ 5 mil isolado.

## Veredito

**Aprovado com correções.** O que recalculei bate com o gravado:
- a regra de G: portes 2 e 3 em 0,300 e portes 1, 2 e 4 em 0,400, iguais à auditoria 18 e ao texto do adendo;
- o portão: HI-1 e HI-2 do 48b e ΔB1, ΔB2 e ΔB5 do protocolo 64, sem a divisão por grupo, **nos dois cortes**;
- as 30 linhas de `PO_estimativas.csv` (τ₁, τ₀ e τ₀ + τ₁ dos 5 outcomes nos 2 cortes), até 2,3e−13 no salto e
  1,1e−13 no EP;
- as contagens por grupo, lado e corte, os p de Holm, os q de BKY e o balanço de capital e região.

O script é fiel ao adendo. Nenhuma das 19 decisões muda o que o adendo fixava (detalhe abaixo).

**Nenhuma estimativa mudou.** `PO_estimativas.csv`, `PO_contagens.csv` e `PO_salto_por_grupo.png` ficaram iguais
byte a byte ao commit `c0e78be`, antes e depois das correções. `HI_*`, `OC_*`, `CL_*` e `PM_*` não foram regravados.

As correções foram de texto, nos blocos gerados do 57u (A1 a A4), e de proveniência (A5). Mudaram o 57u e
`PO_resumo.json` (só `entradas`).

O ponto de mérito é o A1. O doc destacava um achado da PO-4: na HI-2 em 0,300, o salto é −1,88 [−3,50; −0,26] onde o
estrato não muda e −0,22 onde muda. Esse número confere. Mas o texto não dava o peso dele, e a leitura "o sinal da H1
vem de onde o IED não muda, logo da bolsa" ficava aberta. O grupo "não muda" de 0,300 é sobretudo de municípios com
mais de 100 mil habitantes e reúne as capitais da janela.

## Achados, por gravidade

### Médios

**A1. O destaque da HI-2 em 0,300 por grupo pedia mais peso contrário (corrigido no texto).**

O 57u dizia, na resposta curta, que na HI-2 em 0,300 o IC 95% exclui zero onde o estrato não muda. Depois vinha só
"Descritivo: a PO-4 fica fora do Holm". O número confere: −1,8827 [−3,5043; −0,2610], p = 0,023. Onde o estrato muda,
o salto é −0,2175 [−1,2783; +0,8432]. Mas faltavam quatro coisas:
- **A diferença entre os grupos não se distingue de zero.** τ₁ = +1,67 [−0,27; +3,60], p = 0,091, p de Holm 0,366.
  Que um grupo tenha IC sem zero e o outro não, não mostra que os saltos sejam diferentes.
- **Multiplicidade.** A PO-4 tem 20 intervalos (5 outcomes × 2 cortes × 2 grupos), e só esse exclui zero. A 5%,
  um em vinte é o que o acaso daria, mesmo sem salto nenhum.
- **Seleção da linha.** A linha é destacada porque já tinha IC sem zero no 57n. É a mesma informação, fatiada.
- **Composição.** Em 0,300, o grupo "não muda" reúne os portes 1 e 4. Na população H1 da janela, 62 dos 92
  municípios são do porte 4 e 18 são capitais (24 % abaixo e 14 % acima do corte). O grupo "muda" não tem capital
  nenhuma. A comparação mistura o canal do IED com porte, capital e região.

Um cálculo exploratório meu indica que a composição pesa: tirando as 18 capitais do grupo "não muda", o salto da HI-2
em 0,300 cai para −0,65 [−2,36; +1,07]. É um cálculo da auditoria, fora do adendo e de qualquer família, para
calibrar o peso do texto. Não entra no 57u. Só no porte 4, o salto é −1,92 [−3,85; +0,02]; só no porte 1, −0,60
[−1,51; +0,30].

**Risco de leitura causal.** O 57u não usa linguagem causal. Mas a frase isolada convida a ler que "o sinal da H1
vem de onde o IED não muda, logo da bolsa". Isso não se sustenta, por três razões:
- τ₁ não rejeita zero;
- o grupo "não muda" de 0,300 é sobretudo de cidades grandes e capitais, onde o adendo 48c já tinha localizado parte do sinal da H1 (o doc 57o diz que a queda em 0,300 anda junto com capitais logo abaixo do
  corte);
- mesmo onde o estrato não muda, o salto é de um pacote, não da bolsa isolada.

Em 0,400, o grupo "não muda" é só o porte 3, com 78 % e 93 % dos municípios no Nordeste. Os dois cortes comparam
tipos de município diferentes.

**Correção** (no gerador do 47; os números vêm das saídas). A resposta curta agora:
- diz que o achado não mostra que o salto da H1 venha de um grupo e não do outro;
- dá o p e o p de Holm de τ₁ dessa linha;
- descreve a composição dos grupos (portes, capitais e Nordeste, lidos do balanço da seção 7);
- conta quantos dos intervalos da PO-4 excluem zero (1 de 20), com a frase sobre o acaso.

Os limites ganharam um item: os grupos não são os mesmos nos dois cortes. A composição de cada corte vem do balanço.
A figura destaca em azul só essa barra, pela regra do "Como ler". Não mudei a figura: a regra vale para todas as
barras, e o texto agora dá o peso.

**A2. "O IED não explica" é a frase do adendo, mas os IC de τ₁ são largos demais para descartar o canal (corrigido
no texto).**

A leitura `TAU1_TODOS_CONTEM_ZERO` copia a frase do §4: "o IED não explica o sinal da H1, com pouca potência". Os IC
de τ₁ incluem diferenças maiores, em valor absoluto, que o próprio salto da H1 sem divisão. Exemplos:
- HI-1 em 0,400: [−71,8; +9,7] p.p., para um salto da H1 de −2,3 p.p.;
- HI-2 em 0,300: [−0,27; +3,60], para −1,13.

A regra fica, porque é a do adendo. Acrescentei uma frase: "não explica" quer dizer que os dados não mostram que o IED
explique o salto, não que o canal esteja descartado.

### Menores

**A3. A decisão 7 (controle de vagas da HI-2 com coeficiente por ciclo) é a leitura literal da base e não muda nada
(sem correção).**

Na base (`est_municipio` → `T23.ajustar`), o controle tem um coeficiente por grupo, e o grupo é o ciclo. O 47 mantém
um coeficiente por ciclo, com as retas por ciclo × G. Como os interceptos já são por ciclo × G, a centragem do
controle não afeta τ.

Refiz com coeficiente por ciclo × G, que é a outra leitura possível:
- 0,300: τ₁ = +1,40 [−0,44; +3,25]; não muda −1,79 [−3,42; −0,15]; muda −0,38 [−1,24; +0,47];
- 0,400: τ₁ = −0,79 [−2,22; +0,64].

A leitura não muda. Regressões separadas por grupo dão os mesmos saltos que a versão por ciclo × G.

Há uma redação ambígua na decisão 7: "um coeficiente por ciclo (não por ciclo × G, como na base)". O certo é "por
ciclo, como na base, e não por ciclo × G". Não editei, porque a seção 0 é o registro pré-estimativa.

**A4. A regra de "< 10" é aplicada a grupo × lado, mas as retas são por ciclo × grupo × lado (sem correção; o
texto já avisa).**

A decisão 11 conta municípios distintos por G × lado, a unidade do cluster. É a leitura mais conservadora do adendo
(contar células daria números maiores), e nenhum G × lado fica abaixo de 10 (mínimo 15). Mas a HI-1 e a HI-2 estimam
retas por ciclo × G × lado, e há células finas. Em 0,400, no grupo "não muda", acima do corte, são 10, 9 e 6
municípios nos ciclos 1 a 3 (HI-2). O adendo pede "grupo × lado", e a decisão o segue. O item "Retas por ciclo ×
grupo" dos limites já diz que essas retas são imprecisas. Registro aqui as contagens por ciclo (tabela abaixo).

**A5. Cinco entradas lidas não tinham hash (corrigido).** Rastreei os arquivos abertos na execução do 47. Os
construtores importados leem cinco arquivos que `entradas`, em `PO_resumo.json`, não listava:
- `outcomes_U_municipio.parquet` e `outcomes_G3_municipio.parquet`, lidos por `E6.chaves_populacoes`, o mesmo ponto
  do A9 da auditoria 44;
- `data/pmm_especialistas_nominal.csv` e o ZIP da lista de ativos, que definem V no 43;
- o manifesto da referência do IBGE.

Os cinco foram acrescentados com SHA-256. Nenhum número mudou.

**A6. A ordem "decisões antes das estimativas" só é verificável pela ordem dos commits (sem correção).**

Os commits:
- adendo congelado em `c87ed75` (22:25);
- decisões em `808db3a` (22:30);
- script, saídas e blocos em `c0e78be` (22:39).

O cabeçalho e a seção 0 do 57u estão iguais, byte a byte, entre `808db3a` e `bb1b7e3`. Fora dos blocos `PO:`, nada
mudou. O adendo não mudou desde o congelamento; o SHA-256 confere.

Nove minutos entre as decisões e um script de 1.163 linhas indicam que o código foi escrito em paralelo. Pelo Git, não
dá para provar nem negar que nenhuma conta rodou antes de `808db3a`. Nada nos resultados sugere escolha
retrospectiva:
- as decisões seguem os scripts 40 e 43;
- a única que podia mexer em número (A3) não muda a leitura.

**A7. A contagem de desenho olhada antes das decisões é aceitável (sem correção).** O 57u diz que, antes de escrever
as decisões, foi olhada uma contagem de municípios com célula por porte, lado e ciclo na janela, sem outcome. Essa
contagem:
- usa só a running variable e o porte, ambos anteriores ao tratamento;
- não foi gravada, então não é reproduzível pelo histórico;
- serviu para checar suporte às retas por ciclo × G, e as retas ficaram como o adendo pede.

Não houve desvio do adendo motivado por ela. Para a próxima vez, vale gravar essa contagem no próprio commit das
decisões.

### Sem achado (fidelidade ao adendo)

| Ponto do adendo | Verificação |
|---|---|
| G lido do a10, não digitado | refeito do JSON: código de baixo pela faixa que contém o corte; código de cima pela faixa que começa em corte + 0,001; G = 1 onde o estrato difere. Em 0,300, 4 → 3, com estratos 3→3, 4→3, 4→3 e 4→4 nos portes 1 a 4. Em 0,400, 3 → 2, com 3→2, 3→2, 3→3 e 4→3. No script, os portes só aparecem no teste, contra o texto do adendo |
| Código do Anexo VI do lado certo do corte | conferi **todos** os municípios do a08 na janela, não só os da amostra: 1.513 em 0,300 e 1.190 em 0,400, 0 divergentes |
| Porte do Anexo VI | todos os municípios das amostras têm porte; 0 fora |
| Diferença em descontinuidades: retas por grupo e por lado, mais a base | H1: intercepto e inclinações por ciclo × G × lado, T e T × G, EF de curso × ciclo (HI-1), controle de vagas imediatas (HI-2), CR1 por município. ΔB: retas por G × lado, HC1. Refeito, igual |
| τ₀ + τ₁ com V(T) + V(T × G) + 2 Cov | refeito da mesma matriz sanduíche |
| Holm nas 4 primárias | p = 0,438 / 0,135 / 0,092 / 0,459; Holm = 0,876 / 0,405 / 0,366 / 0,876 (HI-1 e HI-2 × 0,300 e 0,400) |
| BKY nas 6 secundárias | menor p = 0,2246. Para rejeitar na 1ª etapa seria preciso q > 1, logo todos os q valem 1,000. Confere |
| Leitura do §4 | `TAU1_TODOS_CONTEM_ZERO`; PO-3 `SEM_INDICIO` nos dois cortes; nenhum G × lado < 10. Refeito |
| Código intermediário `TAU1_IC_EXCLUI_ZERO_SEM_HOLM` (decisão 16) | o §4 não cobria esse caso. A decisão o fixou antes, como sinal sem correção, e ele não foi acionado |
| CNES | maior competência lida 202608; pré 202406–202506 (13 meses), pós 202510–202608 (11), exigindo meses completos (ΔB2: 3 municípios fora em 0,300) |
| V | 1.039 municípios de U com célula, menos 2 com chegada na lista nominal sem célula nos ciclos 1–2 (261110 e 520870) = 1.037, como no 43 |

**Portão.** Refiz as linhas de base sem a divisão por grupo nos **dois** cortes. O 47 só confere 0,300, como o
adendo pede.
- HI-1: −0,036784 em 0,300 e −0,023120 em 0,400;
- HI-2: −1,126326 e −0,156707;
- ΔB1: −0,229095 e −0,455828;
- ΔB2: −6,146960 e −6,090510;
- ΔB5: +0,214916 e −1,094201.

Os n por lado são iguais aos de `HI_estimativas.csv` e `OC_estimativas.csv`, nas casas mostradas.

## Integridade

| Item | Resultado |
|---|---|
| IVS errado | rastreio de arquivos abertos na execução do 47: `data/ivs_ipea_2010_municipios.csv` não é lido; nenhum script da cadeia importada o cita |
| CNES | painel a09 com competências até 202608; nenhuma ≥ 202609 |
| `EMPIRICO` | em todas as 30 linhas de `PO_estimativas.csv`, nas 56 de `PO_contagens.csv` e no resumo |
| Imputação | nada imputado; município sem todos os meses fica fora do ΔY daquele outcome, contado |
| `HI_*`, `OC_*`, `CL_*`, `PM_*` | só lidos (rastreio: o 47 só abre para escrita `PO_*` e o 57u); `git status` limpo neles |
| Determinismo | duas execuções seguidas do 47 dão saídas iguais byte a byte, antes e depois das correções; estimativas, contagens e figura iguais às de `c0e78be` |
| `data/` | nada escrito |
| Testes | `tests/test_heterogeneidade_porte_ied.py`: 31 passam (o teste do cabeçalho agora espera o link desta auditoria); `tests/test_pipeline_rdd_bolsa.py`: 15 passam |

## Texto do 57u

- **Linguagem causal.** Nenhuma frase atribui efeito ao IED ou à bolsa. O texto fala do pacote do corte e de
  heterogeneidade descritiva, e "não se detecta" vem com "não é mostrar que é zero". Os riscos estavam no peso do
  destaque da PO-4 (A1) e no "o IED não explica" (A2). Os dois foram corrigidos.
- **Números fora dos blocos.** Só os parâmetros do adendo; o teste confere.
- **Clareza para o autor.** "A pergunta, em linguagem simples", a tabela da regra de G e o balanço da seção 7 são
  claros. A lacuna era ligar o balanço à leitura dos grupos, e agora a resposta curta e os limites fazem isso.

## O que foi recalculado

"Gravado" é o valor de `PO_*`. As diferenças são absolutas, na escala da saída.

| Item | Recalculado | Gravado | Diferença máxima |
|---|---|---|---|
| Regra de G (a10) | portes G = 1: {2, 3} em 0,300; {1, 2, 4} em 0,400 | igual | — |
| Contagens HI-1 (mun. / células), 0,300: não muda ab/ac, muda ab/ac | 50/330, 42/211, 45/162, 30/100 | igual | 0 |
| Contagens HI-1, 0,400 | 18/85, 15/39, 65/230, 54/131 | igual | 0 |
| Contagens HI-2 (mun. / mun. × ciclo), 0,300 / 0,400 | 50/80, 42/68, 45/61, 30/48 / 18/37, 15/25, 65/93, 54/72 | igual | 0 |
| Contagens ΔB1 e ΔB5, 0,300 / 0,400 | 73, 72, 71, 47 / 22, 22, 100, 123 (ΔB2 em 0,300: 70 abaixo no "não muda") | igual | 0 |
| τ₁ HI-1, 0,300 / 0,400 | +12,54 p.p. [−19,13; +44,20] / −31,06 p.p. [−71,80; +9,68] | igual | ≤ 2,3e−13 |
| τ₁ HI-2, 0,300 / 0,400 | +1,665 [−0,269; +3,599] / −0,611 [−2,230; +1,007] | igual | ≤ 2,3e−13 |
| HI-2 0,300 por grupo | não muda −1,883 [−3,504; −0,261]; muda −0,218 [−1,278; +0,843] | igual | ≤ 2,3e−13 |
| PO-3 (ΔB5) 0,300 | τ₁ +2,80 [−1,72; +7,32]; não muda −0,99; muda +1,81 | igual | ≤ 2,3e−13 |
| PO-3 (ΔB5) 0,400 | τ₁ +0,95 [−1,92; +3,82]; não muda −1,88; muda −0,93 | igual | ≤ 2,3e−13 |
| Demais linhas (ΔB1, ΔB2, HI-1 por grupo) | as 30 linhas | igual | ≤ 2,3e−13 |
| Holm (4) e BKY (6) | ver tabela de fidelidade | igual | 0 nas casas mostradas |
| Balanço H1, capitais e Nordeste por G × lado | 0,300: 24/14 % e 0/0 % de capitais; 0,400: 78/93 % e 52/65 % no Nordeste | igual | 0 nas casas mostradas |
| Sensibilidade da auditoria: controle por ciclo × G (A3) | ver A3 | — | — |
| Exploratório da auditoria: HI-2 0,300 por porte e sem capitais (A1) | ver A1 | — | — |

Contagens de municípios da HI-2 por ciclo na janela (A4):

| Corte | Grupo, lado | Ciclo 1 | Ciclo 2 | Ciclo 3 |
|---|---|---|---|---|
| 0,300 | não muda, abaixo / acima | 18 / 17 | 30 / 23 | 32 / 28 |
| 0,300 | muda, abaixo / acima | 12 / 16 | 31 / 18 | 18 / 14 |
| 0,400 | não muda, abaixo / acima | 13 / 10 | 14 / 9 | 10 / 6 |
| 0,400 | muda, abaixo / acima | 27 / 15 | 29 / 29 | 37 / 28 |

## O que mudou nesta auditoria

- `scripts/rdd_bolsa/47_heterogeneidade_porte_ied.py`: só texto gerado (A1 e A2: resposta curta, leitura e limites)
  e cinco entradas com hash (A5). Nenhuma conta mudou.
- `docs/06_execucao/57u_resultados_heterogeneidade_porte.md`: blocos regerados pelo script e cabeçalho com o link
  desta auditoria.
- `output/rdd_bolsa/PO_resumo.json`: só `entradas`.
- `tests/test_heterogeneidade_porte_ied.py`: o cabeçalho esperado passa de "pendente" para o link desta auditoria.
