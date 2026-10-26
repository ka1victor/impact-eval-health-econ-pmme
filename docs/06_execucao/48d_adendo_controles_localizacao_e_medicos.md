# 48d. Adendo: H1 e oferta local no corte com controles de localização e de presença de médicos na região

> **Data de congelamento:** 26/10/2026, antes de rodar as contas deste adendo.<br>
> **Pedido do autor (26/10/2026):** "adicionar controle de localização, ou
> presença de médicos da região". Antes, no mesmo dia: "deveríamos pensar em
> vários controles que já sabemos que influenciam a propensão do médico a atuar
> no município, por exemplo presença de médicos na região".<br>
> **Estatuto:** `ADENDO_48D_POS_RESULTADO` para a H1 (os saltos da H1 já foram
> vistos, inclusive com capital e UF, no adendo 48c, ainda sem auditoria).
> Para o protocolo 64 (oferta local no corte), é **pré-resultado**: nenhuma
> estimativa do 64 existia quando este adendo foi congelado.<br>
> **Fonte das variáveis candidatas:** registro
> [`63_registro_explicacoes_e_controles_H1.md`](63_registro_explicacoes_e_controles_H1.md),
> §1 e §3. Toda saída leva `natureza_dos_dados = EMPIRICO`.

## 1. Regra para entrar como controle

Só variáveis **pré-determinadas**, medidas antes do programa (até 2025-06) ou
fixas (geografia). O controle entra como na RDD com covariáveis de Calonico,
Cattaneo, Farrell e Titiunik (2019): linear, **mesmo coeficiente dos dois
lados** do corte. Com covariáveis pré-determinadas e balanceadas, o salto
estimado é o mesmo em esperança e o IC tende a encolher. Se uma covariável
**salta** no corte, ela muda o salto, e isso é lido como "a queda anda junto com
essa variável", não como efeito da bolsa.

O tipo de vaga, a concorrência, os candidatos e as vagas oferecidas **não**
entram: podem responder ao corte (doc 63, itens 7, 8, 9 e 14).

## 2. Conjuntos de controles (fixados aqui)

| Conjunto | Variáveis | Fonte no repositório |
|---|---|---|
| **L — localização** | dummy de capital; efeito fixo de macrorregião (5); log(população do Censo 2022) | `output/aquisicao/ibge_capitais_uf_regiao.csv` (48c); população já usada nos denominadores do E7 |
| L-UF (sensibilidade) | L com efeito fixo de UF no lugar da macrorregião | idem |
| **M — médicos na região** | médicos (CBO 2251*, 2252*, 2253*, todos) por 10 mil hab. no município; especialistas nas CBO-alvo do curso por 10 mil hab. no município; especialistas nas CBO-alvo por 10 mil hab. no **resto da região de saúde** (sem o próprio município) | CNES nacional a09, média de 2024-06 a 2025-06; `output/aquisicao/malha_municipios_regioes_saude.parquet` |
| **L+M** | as duas juntas | — |

- Na unidade célula (HI-1), "CBO-alvo do curso" é a da célula; na unidade
  município (HI-2 e protocolo 64), é a soma das CBO-alvo de todos os cursos do
  PMM-E (o B1 do doc 57k no pré).
- Se uma variável não puder ser construída com o que está no repositório, ela
  fica fora, o motivo é relatado e o conjunto roda sem ela. **Nada é
  adquirido nem imputado neste adendo.**
- Variável com valor ausente num município: o município sai das linhas que a
  usam, contado; as linhas sem controle rodam na amostra comum, para
  comparação.

## 3. O que se estima

**Especificação base:** a do 48b para a H1 (HI-1 célula, efeitos fixos de
curso × ciclo; HI-2 município, controle das vagas imediatas por ciclo; RDD
local linear, kernel triangular, h = 0,050, **cada corte separado**, ciclos
empilhados com parâmetros por ciclo, CR1 por município; ciclo 2 com o tipo de
vaga do quadro de 13/02/2026) e a do protocolo 64 para a oferta local (OC-A1 e
OC-A2, ΔY por município em V, HC1).

| Id | Linha | Papel |
|---|---|---|
| CL-0 | **balanço**: salto de cada variável de L e M no corte, por município, em 0,300 e 0,400 | diagnóstico; relatar todas |
| **CL-1** | HI-1 e HI-2 com **L+M**, por corte | **principal deste adendo** (4 linhas; Holm entre elas) |
| CL-2 | HI-1 e HI-2 com L só; com M só; com L-UF + M | secundária (BKY) |
| CL-3 | HI-1 e HI-2 com cada variável isolada | secundária (BKY) |
| CL-4 | HI-1 e HI-2 sem controle, na amostra comum das linhas com L+M | referência |
| **CL-5** | OC-A1 e OC-A2 (protocolo 64) com **L+M**, por corte | **principal deste adendo para a oferta local** (4 linhas; Holm entre elas) |
| CL-6 | OC-A1 a OC-A5 com L só e M só | secundária (BKY) |

Para cada linha: salto, IC 95%, p, n por lado, e a **variação do salto em
relação à linha sem controle na mesma amostra**, em p.p. e em % do salto sem
controle.

### 3.1 Pareamento perto do corte (acrescentado em 26/10/2026, antes de rodar; pedido do autor: "fazer pareamento também é uma boa")

Ideia: perto do corte, parear cada município do lado de bolsa maior com um do
lado de bolsa menor parecido em localização e em médicos na região, e comparar
os pares. É o desenho de RDD com pareamento de Keele, Titiunik e Zubizarreta
(2015). Supõe que, dentro da janela e dados os controles, o lado do corte é
como sorteado (randomização local condicional); não usa a reta.

**Regras fixadas:**
- **Janelas:** |IVS − corte| ≤ 0,050 (principal) e ≤ 0,020 (sensibilidade),
  cada corte separado. O próprio IVS não entra no pareamento (separa os lados
  por construção); a distância ao corte é relatada nos pares.
- **Unidade:** município × ciclo para a H1; município para o protocolo 64.
- **Pareamento:** exato em macrorregião e em capital; vizinho mais próximo por
  distância de Mahalanobis em log(população) e nas três variáveis de M;
  1:1, sem reposição, o lado com menos municípios é o que procura par; *caliper*
  de 0,25 desvio-padrão do escore de distância; quem fica sem par é contado e
  relatado. Na H1, os pares são formados dentro do mesmo ciclo.
- **Balanço:** diferença padronizada de cada variável antes e depois do
  pareamento; meta |DP| < 0,10. Se alguma variável ficar acima de 0,25 depois
  do pareamento, relatar e **não** ler a linha como comparação limpa.
- **Outcomes:**
  - H1: por município × ciclo, a fração das células com vaga imediata que
    foram preenchidas (versão municipal de HI-1) e os médicos alocados em
    células com vaga imediata por vaga imediata (versão de HI-2 sem regressão);
  - oferta local: ΔB1 e ΔB2 (e, como secundárias, ΔB3–ΔB5) do protocolo 64.
- **Estimador e inferência:** média das diferenças dentro dos pares; IC por
  teste de permutação dentro dos pares (troca de sinal, 9.999 sorteios, semente
  20261026) e IC t pareado, os dois relatados.

| Id | Linha | Papel |
|---|---|---|
| CL-7 | H1 pareada, por corte, janela 0,050 | secundária (BKY) |
| CL-8 | oferta local pareada (ΔB1, ΔB2), por corte, janela 0,050 | secundária (BKY) |
| CL-9 | CL-7 e CL-8 na janela 0,020 | sensibilidade |

### 3.2 Nota datada de 26/10/2026: pareamento por escore de propensão (PSM) passa a ser o principal deste adendo

Decisão do autor, **antes de qualquer resultado deste adendo ou do protocolo 64
existir** (nenhuma saída `CL_*` ou `OC_*` em nenhum worktree no momento desta
nota): "PSM, parear, em vez de colocar controle direto na regressão como soma".

**O que muda:**
- o **principal** deste adendo passa a ser o **pareamento por escore de
  propensão** (linhas PS-1 e PS-2 abaixo), no lugar de CL-1 e CL-5;
- os controles somados na regressão (CL-1 a CL-6) e o pareamento por
  Mahalanobis (CL-7 a CL-9) continuam **relatados**, como secundários (BKY),
  para comparação. O Holm passa para as linhas PS.

**Especificação do PSM:**
- **"Tratamento":** estar acima do corte (lado de bolsa maior), dentro da
  janela |IVS − corte| ≤ 0,050, cada corte separado; 0,020 como sensibilidade.
- **Escore:** logit de P(acima do corte | X) dentro da janela, com X = L+M
  (capital, macrorregião, log da população, médicos por 10 mil, especialistas
  do curso por 10 mil no município, especialistas no resto da região de
  saúde). O IVS **não** entra no escore (separa os lados por construção).
- **Pareamento:** 1:1, vizinho mais próximo no logit do escore, sem reposição,
  *caliper* de 0,2 desvio-padrão do logit do escore (Austin, 2011). Na H1, exato
  no ciclo (município × ciclo). Unidades sem par ou fora do suporte comum são
  contadas e relatadas (com quem são: capitais, região).
- **Suporte comum:** histograma do escore dos dois lados antes do pareamento;
  relatar a fração descartada.
- **Balanço:** diferença padronizada de cada variável de X antes e depois;
  meta |DP| < 0,10; acima de 0,25 depois do pareamento, a linha não é lida como
  comparação limpa.
- **Outcomes:** os mesmos do §3.1 (H1 municipal e ΔB1, ΔB2 do protocolo 64).
- **Estimador e inferência:** média das diferenças dentro dos pares (ATT do
  lado de cima); IC por permutação de sinais dentro dos pares (9.999 sorteios,
  semente 20261026), condicional aos pares, e IC t pareado; os dois relatados.
  O *bootstrap* simples não é usado (inválido para vizinho mais próximo,
  Abadie e Imbens, 2008).
- **Sensibilidade:** ponderação pelo inverso do escore (IPW) na mesma janela,
  com o mesmo escore aparado em [0,05; 0,95].

| Id | Linha | Papel |
|---|---|---|
| **PS-1** | H1 por PSM, por corte, janela 0,050 | **principal deste adendo** (Holm com PS-2) |
| **PS-2** | oferta local por PSM (ΔB1, ΔB2), por corte, janela 0,050 | **principal deste adendo** para a oferta local (Holm com PS-1) |
| PS-3 | PS-1 e PS-2 na janela 0,020 | sensibilidade |
| PS-4 | PS-1 e PS-2 por IPW | sensibilidade |

**O que o PSM supõe, diferente da RDD:** que, perto do corte e com o mesmo X,
estar de um lado ou do outro é como sorteado (randomização local condicional).
A RDD supõe continuidade e usa a reta. O PSM não usa a reta, o que importa
porque parte da queda da H1 vem da reta levada até o corte (doc 05, §2.1).
Nenhum dos dois remove o pacote do corte (auditoria 18).

**Leitura:** se o pareado concordar com a RDD (CL-1 e CL-5), a conclusão não
depende da reta. Se discordar, relatar as duas, com o aviso de que o pareado
supõe randomização local e a RDD supõe continuidade; nenhuma das duas passa a
ser a principal por isso.

## 4. Leitura pré-registrada

| Situação | Leitura |
|---|---|
| CL-0 sem salto relevante (IC contém zero) e CL-1 com salto parecido ao sem controle, IC menor | os controles melhoram a precisão sem mudar a conclusão da H1 |
| CL-0 mostra salto em alguma variável (capital, região, médicos) e CL-1 leva o salto da H1 para perto de zero | a queda em 0,300 anda junto com localização ou presença de médicos dos lados do corte (desbalanceamento de poucos municípios), e não com a bolsa; relatar como **limite da RDD** no corte |
| CL-1 rejeita zero depois do Holm | relatar sinal e tamanho, com as ressalvas do diagnóstico 61 e do pacote do corte |
| CL-5 com IC que contém zero | a conclusão do protocolo 64 sobre a oferta local não depende desses controles |
| CL-5 difere do 64 sem controle | relatar as duas lado a lado; o principal do 64 continua o sem controle, como congelado |

O principal da H1 continua o 48b. Este adendo é robustez.

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/44_controles_localizacao_medicos.py` |
| estimativas | `output/rdd_bolsa/CL_estimativas.csv`, `CL_balanco.csv`, `CL_resumo.json`, `CL_figuras/` |
| resultados | `docs/06_execucao/57r_resultados_controles_localizacao_medicos.md` (blocos gerados pelo script) |
| testes | `tests/test_controles_localizacao_medicos.py` |

**Portão:** antes de qualquer conta nova, o script reproduz HI-1 e HI-2 do 48b
nos dois cortes (diferença ≤ 1e−8); a parte CL-5 só roda depois de existirem as
saídas `OC_*` do protocolo 64 e reproduz OC-A1 em 0,300 (≤ 1e−8).

## 6. Integridade

- Nada imputado; nada adquirido; nada escrito em `data/`.
- O arquivo de IVS errado não é lido; PIB, IDHM e renda não entram (não são
  necessários aqui e não podem substituir o IVS).
- Nenhuma competência do CNES ≥ 2026-09.
- As saídas do 48b, 48c e 64 não são regravadas.
