# 52. Protocolo P1: quanto o salário move a escolha de onde trabalhar

> **Data de congelamento:** 19/10/2026, antes de estimar qualquer linha abaixo.
> O portão G1 (`docs/auditorias/G1_viabilidade_candidatos.md`) foi juntado sem
> contrastes.<br>
> **Origem:** plano do doc 51 (P1, tarefas T1.1–T1.5). Os cenários do T1.6 ficam
> para depois da auditoria deste bloco.<br>
> **Estatuto:** `PROTOCOLO_52_POS_RESULTADO`. O E9 (doc 42) e a X4 e a X5 (doc
> 46) já foram vistos. Este protocolo não muda o E9 nem o Holm do protocolo 40.
> Toda saída leva `natureza_dos_dados = EMPIRICO`.

## 1. Pergunta e estimandos

**Pergunta econômica.** Quanto a remuneração anunciada move a escolha de onde
trabalhar, em relação a distância, porte, capital, tipo de vaga e
vulnerabilidade? Isto é, qual o diferencial compensatório?

| Id | Estimando | Papel |
|---|---|---|
| P1a | coeficiente da bolsa (por R$ 1 mil/mês) na utilidade da 1ª opção, ciclos 1–3 empilhados, com distância | **primária** |
| P1b | disposição a pagar (DAP) por 100 km a menos de distância origem–vaga = −β_dist / β_bolsa, em R$ mil/mês | primária descritiva (IC, sem teste de zero) |
| P1c | DAP por ficar na mesma UF da origem, por capital, por vaga imediata | secundárias |
| P1d | β_bolsa por ciclo e teste de igualdade entre ciclos (T1.3) | secundária |
| P1e | heterogeneidade: bolsa × tercil da nota, bolsa × origem no próprio município, bolsa × curso (T1.2, T1.4) | secundárias |
| P1f | logit misto: média e desvio do coeficiente da bolsa e da distância | secundária |
| P1g | ponte P1 → P2: salto previsto pelo modelo em candidatos de 1ª opção por célula no corte, contra a RDD por célula (T1.5) | secundária |

## 2. Dados

| Item | Fonte |
|---|---|
| Escolhas | `output/rdd_bolsa/outcomes/escolhas_candidatos.parquet` (1ª opção como escolha; a 2ª opção entra no logit explodido) |
| Conjunto de escolha | `escolhas_conjunto_principal.parquet` (curso × ciclo, todas as células do quadro, como no E9 §14) |
| Bolsa | `faixa_anunciada` → R$ 10, 15 ou 20 mil |
| IVS | oficial, via os arquivos de outcome; spline contínua com nós em 0,300 e 0,400, como no E9 §15 |
| Distância | `G1_distancias_opcoes.parquet`, a distância da origem principal; `dist_km_origem_mais_proxima` como sensibilidade |
| Mesma UF, mesma região de saúde, mesmo município | `G1_candidatos_origem.parquet` com a tabela de regiões de saúde do TabNet |
| Capital e porte | log da população de 2022 |
| Hierarquia urbana | REGIC 2018 (`data/raw/aquisicao/territorio/`), só leitura |

**Amostra principal:** candidatos com origem ligada (G1). Sensibilidade: o E9
reestimado na mesma amostra sem distância, e na amostra completa do E9, para
mostrar o efeito da seleção pela ligação.

## 3. Especificações

Base comum, igual ao E9 §15:
- logit condicional;
- bolsa linear em R$ mil;
- IVS como spline;
- EP sanduíche com cluster por conjunto de escolha (curso × ciclo);
- EP de máxima verossimilhança e cluster por candidato relatados também.

| Id | Especificação |
|---|---|
| M0 | E9 principal na amostra G1 (sem distância) |
| **M1** | **M0 + distância/100 km + mesma UF + mesma região de saúde + mesmo município de origem + log pop + capital + vaga imediata** (principal de P1a–P1c) |
| M2 | M1 com log(1 + distância) no lugar da distância linear |
| M3 | M1 com distância da origem mais próxima |
| M4 | M1 com efeito fixo de UF da vaga |
| M5 | M1 por ciclo; teste de Wald de igualdade de β_bolsa entre ciclos |
| M6 | M1 + bolsa × (tercil da nota no ciclo); bolsa × origem no município; bolsa × curso (≥ 100 candidatos) |
| M7 | logit explodido (1ª e 2ª opção) com M1 |
| M8 | logit misto: coeficientes normais na bolsa e na distância; 500 sorteios Halton (semente 20261019); demais fixos |
| M9 | logit aninhado por região de saúde (como a X5), com M1 |

**DAP:** razão de coeficientes, IC pelo método delta e por bootstrap por
conjunto de escolha (999 réplicas, semente fixa). Unidades: R$ mil por mês.

**P1g:** usar M1 para prever, em cada célula, a esperança de candidatos de 1ª
opção. Depois:
- calcular o salto no corte que o modelo implica, mudando só a bolsa;
- comparar com a RDD por célula de `n_cand_1a_opcao`, com efeito fixo de curso
  × ciclo e cluster por município (convenção do A3).

A leitura é de consistência, não um teste novo.

## 4. Inferência e relato

- Holm só em P1a. P1b e P1c são estimativas com IC.
- BKY nas secundárias com p-valor (P1d, P1e, P1f).
- Toda especificação é relatada.
- Linguagem: P1a é um efeito da remuneração na escolha **dentro do conjunto de
  vagas abertas**, identificado pelos saltos da bolsa nos cortes, com a
  vulnerabilidade contínua controlada. Não diz nada sobre quem não se
  candidatou.

**Ameaças declaradas:**
- seleção pela ligação (5% sem origem);
- origem = município do estabelecimento, não residência;
- o conjunto de escolha supõe que o candidato viu todas as células do curso;
- outras políticas nos cortes podem mudar atributos não observados da vaga
  (pacote).

## 5. Saídas

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/25_escolha_dap.py` |
| estimativas | `output/rdd_bolsa/P1_estimativas.csv`, `P1_dap.csv` |
| resumo | `P1_resumo.json` |
| figuras | `P1_figuras/` (DAP com IC; β por ciclo; ponte P1g), cada uma com "Como ler" |
| resultados | `docs/06_execucao/57_resultados_perguntas_reformuladas.md`, seção P1, gerada pelo script |

## 6. Integridade

Valem as regras de sempre:
- nada imputado;
- o que falta fica faltante, com motivo;
- sem nome nem CPF em `output/`;
- números do doc gerados ou testados;
- o arquivo de IVS errado não é lido;
- nenhum CNES ≥ 202609.

## 7. Adendo de 24/10/2026: T1.6, cenários

> **Data de congelamento:** 24/10/2026, antes de qualquer simulação. Nenhum
> cenário foi rodado antes deste commit. O P1 foi auditado (auditoria 26) e
> juntado.<br>
> **Pedido do autor:** "quantas vagas a mais seriam preenchidas no total se a
> bolsa subisse R$ 5 mil", levando em conta que as vagas disputam o mesmo
> grupo de candidatos numa alocação centralizada por nota. A RDD não responde
> isso: ela compara células perto do corte, não o mercado inteiro.<br>
> **Estatuto:** `CENARIO_CONTRAFACTUAL`. Nada aqui é observação. As saídas ficam
> em `output/cenarios/P1_*`, com `natureza_dos_dados = CENARIO_CONTRAFACTUAL`
> (doc 51, §2, item 4), e nada vai para `output/rdd_bolsa/`.<br>
> **Este adendo substitui** a lista de cenários do doc 51 (T1.6, itens a–c) pela
> lista fixa da seção 7.5, que responde à pergunta do autor. O item (a) "bolsa
> plana" equivale ao C4.

### 7.1 Modelo de preferências

| Papel | Modelo | Como entra |
|---|---|---|
| **principal** | M1 (seção 3), ciclos empilhados | θ̂ do M1, reestimado no script com as funções do script 25. O script para se algum coeficiente diferir de `P1_estimativas.csv` em mais de 1e-6 |
| sensibilidade S1 | M1 com β_bolsa no limite inferior do IC 95% (cluster por conjunto), −0,002651 | demais coeficientes em θ̂ |
| sensibilidade S2 | M1 com β_bolsa no limite superior do IC 95%, +0,087443 | demais coeficientes em θ̂ |
| sensibilidade S3 | M1 com θ sorteado da distribuição assintótica N(θ̂, V_cluster por conjunto), um sorteio do vetor inteiro por réplica | propaga a incerteza dos parâmetros |
| sensibilidade S4 | M8 (logit misto): coeficientes fixos do M8; bolsa e distância individuais | para cada candidato, 100 sorteios de (b_i, d_i) da normal estimada (semente fixa); em cada réplica, um deles é reamostrado com peso igual à verossimilhança das opções observadas (distribuição condicional às escolhas, Train, cap. 11) |

**Faixa de incerteza principal:** percentis 2,5 e 97,5, nas R réplicas do S3,
de cada outcome (incerteza dos parâmetros e dos sorteios). O ponto é a média
das R réplicas do principal. Também são relatados os percentis do principal
(só sorteio de erro), S1, S2 e S4.

### 7.2 Listas de preferência simuladas

- **Ancoragem: as opções observadas são mantidas como ponto de partida.** A
  utilidade de cada célula é U_ij = V_ij + ε_ij, com ε de valor extremo tipo
  I. O ε é sorteado **condicional à lista observada**: a 1ª opção tem a maior
  utilidade do conjunto e a 2ª, a segunda maior. O sorteio é exato, pela
  representação em corrida de exponenciais: exp(−U) ~ Exp(e^V), sem rejeição.
  No cenário, U'_ij = U_ij + β·Δbolsa_j, e a nova lista é formada pelas L
  células de maior U', em que L é o tamanho da lista observada (1 ou 2).
- **Por que ancorar e não simular a lista inteira:**
  - o cenário sem mudança reproduz a lista observada de cada candidato por
    construção (o script confere isso). Assim, toda diferença entre cenário e
    base vem só da mudança da bolsa;
  - a parte da preferência que o M1 não explica (o pseudo-R² é baixo) fica no
    ε condicional e não vira ruído. Simular a lista inteira do zero redistribuiria
    os candidatos mesmo sem mudar nada, e a base não reproduziria o observado.
- **Quem responde:** os candidatos da amostra P1 (5421, com origem ligada no G1).
  Para eles, cada posição da lista é simulada dentro do conjunto de escolha do
  curso daquela opção:
  - 1ª e 2ª opção no mesmo curso: as duas juntas, no conjunto do curso;
  - 2ª opção em outro curso: cada uma no conjunto do seu curso, condicional a
    ser a melhor dele. A ordem entre os dois cursos fica a observada;
  - opção em célula fora do conjunto da amostra P1 (célula sem região de
    saúde): fica fixa.
- **Quem fica com a lista observada:** quem está fora da amostra P1 (sem
  origem ligada; sem 1ª opção na base do E9). A contagem sai no doc. Nada é
  imputado para eles.
- **Sorteios:** R = 200 réplicas e semente 20261024. Os números aleatórios de
  cada réplica são os mesmos em todos os cenários e em todas as sensibilidades
  (números aleatórios comuns).

### 7.3 Mecanismo

- O do G2 (`alocar` de `scripts/rdd_bolsa/G2_mecanismo_alocacao.py`), sem
  reescrever. É aceitação adiada com até 2 opções, e a célula ordena por:
  1. ordem da opção;
  2. pontuação observada, decrescente;
  3. desempate.
- As vagas reservadas (ER, PCD) seguem a ordem do item 5.6 de cada edital, e a
  reserva vazia vai à ampla concorrência.
- Elegibilidade como no G2.
- **Capacidade:** a efetiva de cada célula, com a regra `divisao_cr` do G2:
  vagas imediatas do quadro mais o que a 1ª chamada publicada alocou acima
  delas. Ela fica fixa em todos os cenários.
- **Desempate por regra fixa:** a classificação publicada da célula só existe
  para os pares candidato × célula observados. Por isso o desempate é um
  sorteio por candidato, fixo na réplica e igual em todas as células e em
  todos os cenários. Ele imita o critério de "maior idade" do edital (item
  5.2.5), que é atributo do candidato. A especificação principal do G2, com a
  classificação publicada, é relatada ao lado na validação.
- Só a 1ª chamada dos ciclos 1, 2 e 3.

### 7.4 Validação de base

- O cenário sem mudança (B0) é rodado em cada réplica.
- Ele é comparado com o número observado de vagas preenchidas na 1ª chamada
  publicada (o alvo do G2), por ciclo e por faixa observada da célula.
- **Tolerância fixada agora:** em todas as R réplicas, |B0 − observado| ≤
  max(3 vagas; 2% do observado) em cada combinação de ciclo × faixa e no total
  de cada ciclo.
- **Se falhar:** o resultado é relatado como `FALHA_VALIDACAO_BASE`, sem
  calibrar nada, e os cenários não são calculados nem lidos.

### 7.5 Cenários fixos

Faixa observada → bolsa (R$ mil/mês): Faixa 3 (IVS ≤ 0,300) = 10; Faixa 2 (0,300
< IVS ≤ 0,400) = 15; Faixa 1 (IVS > 0,400) = 20.

| Cenário | Mudança | Faixa 3 | Faixa 2 | Faixa 1 |
|---|---|---|---|---|
| C1 | +R$ 5 mil em todas as vagas da faixa de bolsa menor | 15 | 15 | 20 |
| C2 | igualar todas no maior valor | 20 | 20 | 20 |
| C3 | +R$ 5 mil só na faixa 0,300–0,400 | 10 | 20 | 20 |
| C4 | bolsa uniforme de R$ 15 mil | 15 | 15 | 15 |

Todos os valores ficam dentro de R$ 10–20 mil.

### 7.6 Outcomes

Por cenário, por ciclo e nos ciclos 1–3 somados, como diferença contra o B0 da
mesma réplica:

1. **total de vagas preenchidas** (o outcome da pergunta do autor);
2. preenchidas por faixa observada da célula;
3. médicos que mudam de vaga: a célula final difere da do B0, incluindo os que
   passam de não alocado a alocado e o inverso;
4. de quais faixas saem e para quais vão: a matriz origem × destino, com "não
   alocado" como categoria;
5. vagas que deixam de ser preenchidas: soma, por célula, de max(0, B0 −
   cenário). Também é relatada a soma das que passam a ser preenchidas.

Também é relatado o custo mensal das bolsas das vagas preenchidas (soma de
bolsa × alocados). É **aritmética simples**, rotulada assim, sem modelo fiscal.

### 7.7 Limites declarados

- O grupo de candidatos é fixo: não entra médico novo, e ninguém deixa de se
  candidatar. A pergunta "quantos médicos a mais o programa atrairia" não é
  respondida.
- A extrapolação fora de R$ 10–20 mil não é permitida.
- Não modela a 2ª chamada, a desistência, a homologação, a redistribuição do
  item 5.7, que fica embutida na capacidade efetiva, nem o custo fiscal (além
  da aritmética simples).
- A preferência é a do M1, com IIA dentro do curso, e o conjunto de escolha
  supõe que o candidato viu todas as células do curso.
- O β_bolsa do M1 tem IC que contém zero: o cenário herda essa incerteza.
- Mede o incentivo da bolsa como o M1 o identifica (pacote do corte). Não mede
  participação no PMM-E.

### 7.8 Saídas e testes

| Item | Onde |
|---|---|
| script | `scripts/rdd_bolsa/25b_cenarios_bolsa.py` |
| saídas | `output/cenarios/P1_*` (resumo JSON, réplicas, fluxos, figuras) |
| doc gerado | `docs/06_execucao/57b_cenarios_P1_bolsa.md` |
| testes | `tests/test_cenarios_bolsa.py` |

O doc 57b diz no topo que é simulação. Os testes cobrem:
- rótulo só em `output/cenarios/`;
- base dentro da tolerância;
- determinismo;
- conservação: alocados ≤ capacidade, e um médico ocupa no máximo uma vaga;
- doc igual ao gerado;
- mercado sintético em memória com resultado conhecido.

Fica fora do `run_all.py`.

## 8. Adendo de 25/10/2026: T1.6, nova regra de desempate e revalidação

> **Data:** 25/10/2026, antes de qualquer nova execução do script 25b.<br>
> **O que já foi visto.** A execução com R = 200 de 24/10/2026 falhou na
> validação de base (`FALHA_VALIDACAO_BASE`: ciclo 1, Faixa 3, desvio máximo 5
> > tolerância 3,66; doc 57b, seção 4). Os cenários não foram calculados nessa
> execução, mas as saídas de 2 réplicas de depuração foram vistas (doc 57b,
> seção 5). Esta revalidação não é uma primeira tentativa.<br>
> **Escolha do autor (25/10/2026):** opção 1 da seção 4 do doc 57b.

### 8.1 Única mudança: o desempate

Substitui o último parágrafo de "Desempate por regra fixa" da seção 7.3. O
desempate de cada célula passa a ser:

1. **par candidato × célula observado** (o candidato está na lista de opções
   publicada daquela célula, em qualquer posição): usa a `classificacao_publicada`
   dessa célula, como no G2 principal. Classificação ausente vale +∞, como no G2;
2. **par novo** (a célula entrou na lista simulada e não está nas observadas do
   candidato): sorteio por candidato u ~ U(0,1), fixo na réplica, comum a todas as
   células, cenários e sensibilidades (mesmos números aleatórios da seção 7.2).
   Para ficar na mesma escala da classificação, o sorteio é posicionado entre os
   observados empatados: seja T o conjunto de candidatos com classificação
   publicada naquela célula e a mesma pontuação do entrante; se T é vazio, o
   desempate é u; senão, é (mín. T − 0,5) + u · (máx. T − mín. T + 1), em que
   mín. e máx. são as classificações em T.

A ordem na célula continua: ordem da opção, pontuação decrescente, desempate.
A regra antiga (sorteio em todos os pares) deixa de ser usada.

### 8.2 O que não muda

Tolerância (max(3 vagas; 2% do observado)), regra de validação ("em todas as R
réplicas", por ciclo × faixa e no total de cada ciclo), R = 200, semente
20261024, modelos (M1 principal; S1 a S4), cenários C1 a C4, mecanismo do G2,
capacidade efetiva, outcomes e limites declarados (seção 7.7).

Consequência esperada, que não é calibração: no B0 todos os pares são
observados, então o B0 tende a coincidir com a coluna do G2 principal em toda
réplica. A validação passa a testar o mecanismo, não o desempate.

### 8.3 Se falhar de novo

O resultado é registrado como `FALHA_VALIDACAO_BASE`, os cenários não são
calculados nem lidos, e nada mais é ajustado (nem tolerância, nem regra de
validação, nem desempate, nem amostra). Só o autor decide o passo seguinte, em
novo adendo. Execuções de depuração com R pequeno ficam registradas no doc 57b
e só podem parar na validação de base.
