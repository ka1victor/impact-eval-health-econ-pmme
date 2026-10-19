# Auditoria independente do P5 (protocolo 55): abertura e priorização de vagas

> **Data:** 19/10/2026.<br>
> **Objeto:** commit `89c0eef` (com `6ac9d69` incorporado):
> `scripts/rdd_bolsa/29_determinantes_abertura.py`,
> `output/rdd_bolsa/P5_estimativas.csv`, `P5_resumo.json`, `P5_figuras/`, o
> [doc 57e](../06_execucao/57e_resultados_P5_abertura.md) e
> `tests/test_P5_abertura.py`, contra o
> [protocolo 55](../06_execucao/55_protocolo_P5_abertura_vagas.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.** Bases, T5.1, T5.2, BKY e T5.3 foram
> reproduzidos com código próprio, com diferença máxima de ~1e-11. Nenhuma
> estimativa mudou. As correções são de relato:
> - um termo da sensibilidade que não compara células do mesmo curso;
> - uma leitura que omitia linhas sem avisar;
> - dois desvios não declarados;
> - frases com verbo de mudança;
> - rótulos de figura cortados.<br>
> **Proveniência dos números:** todo número citado aqui foi lido de
> `output/rdd_bolsa/P5_estimativas.csv` e `P5_resumo.json` depois da correção.
> A conferência independente que fica no repositório é a classe
> `TestRecalculoIndependenteAuditoria23` de `tests/test_P5_abertura.py`.

## 1. Como a auditoria foi feita

O código de conferência foi escrito do zero. Ele não importa os estimadores do
script 29 nem a `rdd_lib`. O logit e o Poisson usam o statsmodels; a RDD usa
MQP ponderado do statsmodels; o BKY e os efeitos marginais têm implementação
própria (método delta com gradiente numérico).

Fontes lidas:
- `output/rdd_bolsa/outcomes/` (G3 e U);
- os leitores brutos do script 12 (`ler_cardapio`, `ler_adesao`). Os atributos
  do estabelecimento foram lidos de novo do xlsx do cardápio, com pandas;
- `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`, para a running
  variable e o IVS contínuo;
- o painel CNES do a09, só de `202406` a `202506`, com filtro na leitura;
- o painel SIA do a12, só da janela pré, com filtro na leitura;
- Censo 2022, REGIC 2018, tabela de regiões de saúde do TabNet e `flag_capital`
  da tipologia, todos só lidos;
- `data/ivs_ipea_2010_municipios.csv` não foi lido.

## 2. Recálculo

| Item | Linhas | Diferença máxima |
|---|---:|---|
| Base por célula: 17.543 células × outcomes E1/E2 e 19 covariáveis | 17.543 | nenhuma (mesmos valores e mesmos ausentes) |
| Base municipal (5.566 municípios × 11 covariáveis) | 5.566 | nenhuma |
| T5.1a/b: coeficientes e EP por cluster (E1, E2, presença) | 67 | 4e-11 |
| T5.1c: efeitos marginais médios | 67 | 8e-12 (EP: 9e-7, gradiente numérico) |
| T5.1c: pseudo-R² e contribuição de cada bloco | 19 | 7e-12 |
| T5.2a e T5.2b: salto, EP e n (célula e município; 0,300, 0,400 e empilhado) | 42 | 4e-12 (EP: 3e-11); n idêntico |
| BKY entre as 30 linhas do protocolo | 30 | 0 |
| T5.3: coeficientes e EP HC1 (4 outcomes) | 68 | 5e-12 |

Também conferido:
- `alvo_pmme` do CNES é exatamente a soma das 17 CBO da ponte, sem dupla
  contagem;
- os atributos do estabelecimento na aba da adesão coincidem com os do
  cardápio em todas as células pedidas;
- a regra tudo ou nada da priorização vale.

## 3. Amostras e ausências

| Regra | Situação |
|---|---|
| Município fora do resultado da adesão: pedido ausente, nunca zero | ok. As 7.470 células desses municípios têm `pedida` ausente; o E1 entra com 10.073 células de 1.163 municípios |
| Presença como linha à parte, no município | ok. Logit em G3, 2.697 de 2.699 |
| Cursos 17–24 sem ponte curso–CBO | ok. 5.019 células com vínculos do curso ausentes (2.906 no E1), fora da principal e contadas; sensibilidade rotulada |
| 2 municípios sem covariável | ok. 110002 sem região de saúde: polo e escassez ausentes, 7 células; 422000 sem IVS nem CNES pré. Saem e são contados |
| Separação | ok. E1 tira o curso 16 (8 células, todas pedidas); E2 tira os cursos 3, 5, 7, 15 e 16 (63 células, todas priorizadas). Notas no CSV |
| E1 = 10.073 − 2.906 − 7 − 8 = 7.152; E2 = 3.538 de 5.288; T5.3 = 5.564 de 5.565 | conferido |
| CNES ≥ 202609; SIA fora da janela pré | nada lido |

## 4. Achados e correções

### C1. Sensibilidade "todos os cursos": o termo CAPS é o curso 17 (corrigido no relato)

No E1 da sensibilidade, a coluna "tipo = 70 Centro de Atenção Psicossocial" é
idêntica ao indicador do curso 17: as 110 células são as mesmas. O efeito
fixo `ef[curso17]` sai por colinearidade, e o termo CAPS leva os dois
contrastes juntos. A tabela 4.4 do doc 57e mostrava esse termo como se
comparasse células do mesmo curso.

O que foi feito:
- `ajustar_glm` registra a coluna mantida que é idêntica a uma descartada;
- a nota da linha diz isso, nas linhas T5.1a e T5.1c;
- a tabela do doc marca o termo com † e explica em nota de rodapé;
- `P5_resumo.json` traz `colunas_identicas_a_descartadas` por modelo. Nos três
  modelos principais, o campo está vazio.

### C2. Leitura: linhas omitidas sem aviso e T5.2b ausente (corrigido)

A regra da leitura listava só as 4 maiores associações de cada sinal com IC
que exclui zero. Ficavam de fora, sem aviso:
- no E1, a escassez regional do curso;
- na presença, a macrorregião Centro-Oeste e o REGIC "centro de zona".

Agora a leitura lista todas.

O salto por célula do E1 (empilhado, T5.2a) exclui zero sem passar no BKY. A
leitura não dizia que, com as covariáveis (T5.2b), ele não se distingue de
zero. Agora diz, e lista as 3 linhas do T5.2 no BKY cujo IC exclui zero, todas
com q ≥ 0,602.

A auditoria conferiu, fora do pipeline, a RDD sem covariáveis na amostra do
T5.2b: o IC continua excluindo zero. A perda de distinção vem do ajuste, não
da troca de amostra. Esse número não é relatado.

### C3. Desvios não declarados (declarados agora)

1. **Células pedidas fora do cardápio no E2.**
   - O §1 define a unidade do E2 como a célula pedida.
   - 246 linhas da adesão não têm célula no cardápio. Delas, 150 foram
     priorizadas e 194 são de estabelecimentos que estão no cardápio em outro
     curso.
   - Essas linhas ficavam fora do E2, com uma justificativa só nas
     `decisoes` ("não há atributo do cardápio"), que vale só em parte.
   - A taxa de priorização delas é maior que a das células do cardápio. O E2
     descreve, portanto, a priorização das células do cardápio.
   - Virou o desvio 6, com as contagens em `P5_resumo.json`.
   - Fora do pipeline, a auditoria reestimou o E2 com essas linhas, usando os
     atributos da aba da adesão. Norte, Centro-Oeste, Nordeste, escassez
     regional do curso e natureza sem fins lucrativos continuam excluindo zero,
     com o mesmo sinal, e o IVS continua sem se distinguir de zero. Esses
     números não são relatados.
2. **Amostra do T5.2b por célula.** As covariáveis do §2 incluem os vínculos
   do curso, e o T5.2b por célula perde os cursos 17–24: no E1 empilhado, a
   amostra passa de 6.115 para 4.364 células. Virou o desvio 7, e as 9
   linhas T5.2b por célula levam nota.
3. **Ariquemes (110002).** O município não está na tabela de regiões de
   saúde; só cabe na faixa "Ignorado" de RO. A região a que ele pertence tem
   o polo e a escassez calculados sem ele. O texto do desvio 4 diz isso agora.
   Não se imputa a região: ela não vem de fonte arquivada.

### C4. Linguagem (corrigido)

As frases "quando a característica sobe um desvio-padrão", "se multiplica
quando" e "o efeito é o de subir" leem uma associação como mudança. Elas
estavam:
- na leitura;
- no "Como ler" das figuras T5.1 e T5.3;
- na prosa das seções 4 e 7.

Agora comparam unidades: "por desvio-padrão a mais", "células com o atributo
contra a referência" e "quantas vezes maior é o número esperado entre
municípios". Um teste impede as frases antigas.

Continuam valendo:
- "associado a" em toda a leitura;
- "o critério oficial de priorização não é publicado";
- "pacote do corte" no T5.2;
- nenhuma afirmação causal sobre a SGTES.

### C5. Figuras (corrigido)

| Figura | Problema | Agora |
|---|---|---|
| `P5_T51_efeitos_marginais.png` | rótulos repetidos nos dois painéis espremiam os pontos; dois rótulos cortados perdiam o "(+1 DP)" | rótulo só à esquerda (os termos são os mesmos), painéis mais largos; o corte nunca tira o "(+1 DP)" |
| `P5_T53_razao_taxas.png` | dois rótulos de contínuas cortados sem "(+1 DP)" | idem |
| `P5_T52_rdd_*.png` | a legenda dizia "salto no corte = efeito estimado", contra o próprio "Como ler" (pacote do corte); havia ponto cinza "fora da janela" sem nenhum ponto assim | "salto no corte (pacote do corte; descritivo)"; o item cinza saiu |
| `P5_T51_contribuicao_blocos.png` | nenhum | inalterada (byte a byte) |

Para as figuras RDD, `desenhar` (script 23) ganhou `legenda_salto` e
`legenda_fora`. Os padrões reproduzem as figuras N, NA e K, que não foram
regeradas.

## 5. Julgamento dos desvios declarados

| Desvio | Julgamento |
|---|---|
| Fração priorizada sobre as células pedidas (principal), e sobre o cardápio como leitura alternativa fora do BKY | **coerente com o §1**, que define a unidade do E2 como a célula pedida. A alternativa está bem rotulada |
| `alvo_pmme` no lugar do curso nos modelos municipais | **coerente.** O município não tem curso, e `alvo_pmme` é exatamente a união das CBO da ponte (conferido) |
| Separação: nível com outcome constante sai e é contado | **aceitável e usual.** Muda a população descrita: o E2 é das células de cursos com variação na priorização. Está nas notas e no §10 do doc |
| Cursos 17–24: casos completos na principal, sensibilidade rotulada | **coerente com "usar a ponte do a09".** Nada é imputado. A sensibilidade tem o problema C1, agora anotado |
| Presença do município no T5.2 e no BKY | **leitura razoável** do §1 ("linha separada"). Aumenta a família do BKY de 24 para 30 linhas, o que deixa o BKY mais conservador; nenhuma linha passa de qualquer forma |
| Resultado no doc 57e, e não no 57 | **ok**, até a síntese da onda 5 |

## 6. Testes e determinismo

- `tests/test_P5_abertura.py` passou de 27 para 36 testes:
  - a classe `TestRecalculoIndependenteAuditoria23` (4 testes: outcomes e
    vínculos refeitos dos brutos, as 42 linhas do T5.2 e o BKY, logit com
    efeitos marginais e blocos, Poisson);
  - testes sintéticos da coluna idêntica e do rótulo;
  - testes dos desvios e notas, da legenda, da leitura completa e da
    linguagem.
- O script 29 rodou duas vezes depois da correção. CSV, JSON, as 5 figuras e
  o doc 57e saíram byte a byte iguais.
- Suíte completa rodada módulo a módulo. O resultado está no registro de
  mudanças.

## 7. Números principais (depois da correção)

Os números de estimativas não mudaram.

**Amostras:**
- 17.543 células do cardápio do ciclo 3, em 2.699 municípios, dos quais
  1.163 constam do resultado da adesão;
- E1: 7.152 células, 1.046 clusters;
- E2: 3.538 células, 919 clusters;
- presença: 2.697 municípios.

**T5.1, descritivo:**
- **E1.** IVS +1 DP: −1,8 p.p. [−5,7; +2,1]. Associações que excluem zero:
  - Sul +16,2 p.p.;
  - Nordeste +13,7 p.p.;
  - vínculos do curso +4,2 p.p./DP;
  - gestão estadual −9,3 p.p.;
  - log da população −8,9 p.p./DP;
  - sem fins lucrativos −5,8 p.p.;
  - todos os médicos −4,9 p.p./DP;
  - escassez regional −3,6 p.p./DP.
- **E2.** IVS +0,1 p.p. [−3,4; +3,5]. Associações que excluem zero:
  - Norte +30,5 p.p.;
  - Centro-Oeste +21,4 p.p.;
  - Nordeste +14,2 p.p.;
  - escassez regional do curso +6,5 p.p./DP;
  - sem fins lucrativos −4,9 p.p.
- **Presença.** IVS −3,4 p.p./DP [−6,7; −0,1]; log da população
  +9,6 p.p./DP.
- **Pseudo-R²:** 0,082, 0,103 e 0,076. O bloco que mais separa é sempre o
  municipal.

**T5.2, pacote do corte:**
- célula, E1, empilhado: +14,7 p.p. [+1,8; +27,6], q BKY 0,602;
- o mesmo no T5.2b: +11,6 p.p. [−2,6; +25,8];
- as demais linhas empilhadas contêm zero;
- nenhuma das 30 linhas tem q < 0,05.

**T5.3, IVS por DP:**
- ciclo 1, células: razão de taxas 0,75 [0,60; 0,95];
- ciclo 1, vagas: 0,78 [0,59; 1,03];
- ciclo 2, células: 1,03 [0,80; 1,33];
- ciclo 2, vagas: 0,97 [0,69; 1,37].

## 8. Recomendações ao autor (sem execução aqui)

1. **Reler o E2 com as células pedidas fora do cardápio.** Se o E2 for usado
   para dizer como a SGTES prioriza pedidos, vale considerar uma
   especificação que inclua as 246 linhas, com os atributos da aba da adesão.
   Ela teria de ser registrada como adendo, porque o §2 tira os atributos do
   cardápio.
2. **Comparar o E1 por célula e por município.** O salto do E1 por célula e o
   da fração por município têm sinais opostos. A célula pesa os municípios
   pelo tamanho do cardápio, e a diferença pode vir de heterogeneidade por
   porte. Não há base aqui para preferir um ao outro.
