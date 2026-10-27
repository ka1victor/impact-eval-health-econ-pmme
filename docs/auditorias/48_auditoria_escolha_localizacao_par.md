# 48. Auditoria do adendo 52e: H2 com efeito fixo de UF de origem × UF da vaga e comparação local no corte

> **Data:** 27/10/2026.<br>
> **Objeto:** adendo [`52e`](../06_execucao/52e_adendo_escolha_localizacao_par.md) (congelado em `243160d`), script
> `scripts/rdd_bolsa/50_escolha_localizacao_par.py`, saídas `output/rdd_bolsa/VL_*`, doc
> [`57x`](../06_execucao/57x_resultados_escolha_localizacao_par.md) (13 decisões gravadas em `4f8ca82`, antes das
> estimativas, e duas notas de execução na §7.1) e `tests/test_escolha_localizacao_par.py`. Base: branch
> `claude/vigilant-mccarthy-dd92mc`, commit `92e7f70`.<br>
> **Referências:** protocolos [52](../06_execucao/52_protocolo_P1_escolha_dap.md) e
> [52b](../06_execucao/52b_protocolo_P1h_magnitudes.md); adendos
> [52c](../06_execucao/52c_adendo_vaga_imediata_ciclo2.md) e
> [52d](../06_execucao/52d_adendo_sensibilidades_ciclo2_quadro_1302.md); docs 42, 57a, 57i, 57p e 57v; auditorias 31,
> 41 e 46; scripts 12, 16, 25, 25c, 42 e 48.<br>
> **Método:** recálculo próprio, em memória e no scratch, sem importar os scripts 12, 16, 25, 25c, 42, 48 e 50.
> Escrevi do zero:
>
> - a leitura das entradas: escolhas e conjunto de escolha do funil, a08, grade de faixas (a04), CIR do TabNet,
>   centroides do IBGE e origem G1 (regra `g1_cpf_nome`);
> - a amostra do P1 (exclusões por origem ausente e por região de saúde ausente);
> - a troca do tipo de vaga do ciclo 2 pelo quadro de 13/02/2026, lida de `output/auditoria_H1/a36_celulas.csv`
>   (auditoria 36), e não do script 12;
> - o desenho do logit condicional e a matriz do M1;
> - o efeito fixo do par: retirada de pares sem escolha, detecção de separação, componentes e bases. A base é o par
>   **mais escolhido** de cada componente, e não o par da própria UF, como no 50, para conferir que o β não depende da
>   normalização;
> - Newton com informação em blocos (β denso, efeitos fixos por somas esparsas), com passo limitado, partindo de zero;
> - sanduíche CR1 por conjunto de escolha;
> - score bootstrap de Kline–Santos (ajuste restrito próprio, partindo de zero), com enumeração no ciclo 2 e 400 mil
>   sorteios com semente minha nos ciclos 1–3;
> - Holm, diferença pareada contra o M1 e km equivalentes pelo método delta.

## Veredito

**Aprovado com correções de texto.** O recálculo próprio reproduz todas as linhas:

- as 14 especificações de `VL_estimativas.csv`: todos os coeficientes fora dos efeitos fixos batem a ≤ 3,1e−10, os EP
  com cluster a ≤ 2,4e−10 e os p a ≤ 3e−11, com os mesmos candidatos. A exceção é uma segunda passada do M1 do ciclo
  2, com passo limitado, que ficou a 3,6e−9;
- as contagens de pares, alternativas e candidatos da seção 3 do 57x, idênticas nas 10 linhas com efeito fixo;
- Holm, diferença pareada e km equivalentes;
- o score bootstrap, idêntico onde há enumeração e dentro do erro de Monte Carlo nos sorteios.

O portão VL-5 confere. As decisões de implementação são as do commit `4f8ca82`, idênticas byte a byte no 57x final.
A troca do ponto de partida do Newton (§7.1) não muda o máximo.

O problema está na leitura. Pela regra fixada, o VL-1 dos ciclos 1–3 fica "parecido" com o M1, mas a diferença pareada
mostra que ele é **maior** (A1). Além disso, a redação da resposta curta foi escrita depois dos números sem que isso
estivesse dito (A2). Corrigi os dois pontos nos blocos gerados pelo script e no cabeçalho do 57x, e acrescentei à
resposta curta a linha com a distância em log (A3). Nenhum número mudou. A reexecução completa do 50 deu `VL_*`
idênticos byte a byte, figura incluída.

## Achados, por gravidade

Não há achado grave.

### Médios (corrigidos no texto)

**A1. Nos ciclos 1–3, o VL-1 é maior que o M1, e não "parecido".** A regra da decisão 11 (registrada antes das
estimativas) chama de `PARECIDA_COM_M1` quando cada razão de chances cai dentro do IC da outra. É o que acontece:
1,47 [1,15; 1,89] contra 1,25 [0,98; 1,61]. A regra foi aplicada como estava escrita, e o código não deve mudar
depois de ver o número.

O critério de IC lado a lado, porém, ignora que os dois β vêm dos mesmos candidatos. A correlação entre eles é 0,96,
calculada pelas influências por conjunto da decisão 10. A diferença pareada, que o próprio executor calculou "para
ajudar a ler o §3", dá 0,159 [0,089; 0,229] em log, ou seja, cerca de 17% a mais na razão de chances. Exclui zero
com folga.

| Linha | Contra | Diferença de log RC [IC 95%] | Correlação dos β | Regra (decisão 11) | Leitura que o dado sustenta |
|---|---|---|---|---|---|
| VL-1, ciclos 1–3 | M1, ciclos 1–3 | 0,159 [0,089; 0,229] | 0,96 | `PARECIDA_COM_M1` | maior que no M1 |
| VL-1, ciclo 2 | M1, ciclo 2 | 0,063 [−0,061; 0,187] | 0,95 | `PARECIDA_COM_M1` | parecida |
| VL-2, ciclos 1–3 | M1, ciclos 1–3 | 0,020 [−0,227; 0,267] | 0,60 | `PARECIDA_COM_M1` | parecida, com IC largo |

O §3 do adendo não define "parecida". A intenção dele é saber se o peso da bolsa **cai** quando o par de UFs é
fixado. Um VL-1 maior responde a essa pergunta com mais força ("a localização não explica"), mas não é "a bolsa pesa
o mesmo". O texto gerado dizia "parecida com a do M1" e, na mesma frase, "a bolsa pesa mais que no M1", o que confunde
o leitor.

O texto agora:

- mantém o rótulo da regra, apresentado como "pela regra fixada";
- diz que a leitura mais exata é "maior que no M1";
- explica por que os IC se sobrepõem e a diferença ainda assim exclui zero;
- repete isso na frase de abertura.

Acrescentei também uma frase gerada sobre de onde vem a subida. O M4, que só troca a macrorregião por efeito fixo de
UF da vaga, já dá 1,48 [1,14; 1,91] nos ciclos 1–3 e 2,04 [1,37; 3,03] no ciclo 2, perto do VL-1. O que sobe o peso
da bolsa é comparar vagas dentro da mesma UF; fixar a UF de origem muda pouco. O M4 já estava na figura e na tabela
4.2, e a frase é descritiva.

**A2. A redação da resposta curta e o título da figura foram escritos depois dos números.** O diff `4f8ca82` →
`28f16fb` mostra que as regras (`regra_linha`, `leitura`) não mudaram. Mudaram, porém:

- a frase geral, que antes dizia "a bolsa maior pesa o mesmo que no modelo base" e passou a "fica parecida […],
  continua pesando";
- a frase sobre a diferença contra o M1, que foi acrescentada;
- a explicação dos km, que foi acrescentada;
- o título da figura, que passou a depender de as três principais não ficarem abaixo da referência ("não diminui").

São mudanças de redação, e a nova é mais fiel ao dado que a antiga. O 57x, porém, só registrava as mudanças "antes de
ler qualquer estimativa da bolsa" (§7.1). O cabeçalho do 57x agora diz que a redação da resposta e o título da figura
são posteriores às estimativas, e que as regras do §3 são as do commit das decisões.

Pelo Git não dá para conferir que as duas notas da §7.1 vieram antes de ler o β: elas entraram no mesmo commit dos
números, e não há commit intermediário. A questão perde peso porque o máximo não depende da partida, como mostro na
seção de fidelidade.

### Menores

**A3. Distância: o parêntese do §2 fala em log, e o VL-1 usa a distância linear.** Isso não é desvio de fato. O
adendo se contradiz:

- chama o VL-1 de "M1 (…, log da distância, …)", mas o M1 do protocolo 52 tem a distância linear por 100 km (o log é
  o M2);
- pede os km equivalentes "como no P1h", que só existem com o termo linear;
- compara com o M1 no §3, e o contraste limpo só acrescenta o efeito fixo.

A decisão 4 resolveu a ambiguidade antes de estimar, pela leitura que o adendo sustenta (VL-1 = M1 + par), e pôs a
versão em log como secundária, no BKY. As duas versões contam a mesma história:

| | Distância linear (principal) | log(1 + km) (secundária) |
|---|---|---|
| VL-1, ciclos 1–3 | 1,47 [1,15; 1,89], p = 0,0025 | 1,45 [1,15; 1,83], p = 0,0015 |
| VL-1, ciclo 2 | 1,90 [1,30; 2,78], p = 0,0009 | 1,75 [1,23; 2,49], p = 0,0017 |
| Regra do §3 | `PARECIDA_COM_M1` nas duas | `PARECIDA_COM_M1` nas duas |

Com o log no lugar do linear na família de Holm, os p ajustados seriam 0,0045, 0,0045 e 0,103: a mesma decisão. A
resposta curta não mostrava a versão em log. Ela entrou numa frase gerada, que diz se a regra do §3 dá o mesmo rótulo.

**A4. A docstring do script dizia que tudo usa `estimar` do 25 "sem alteração".** Isso deixou de valer com a nota 1
da §7.1, porque as linhas com par usam `estimar_ef`. Corrigi a docstring (item 2).

### Observações (sem correção)

- **As regras de retirada não enviesam o β.** A decisão 2 retira:
  - (a) as alternativas de pares sem escolha;
  - (b) as alternativas fora de um conjunto separado;
  - (c) os candidatos que ficam com uma só alternativa.

  (a) e (b) são o limite exato da verossimilhança quando o efeito fixo vai a ±∞. (c) contribui log 1 = 0. O β
  estimado é o da mesma verossimilhança, e o que muda é o conjunto de escolha descrito, como diz a seção 8 do 57x.

  Implementei a separação de outro jeito, com o fecho de cada par e a interseção dos fechos com vazamento. Ela
  retira as mesmas alternativas: 0 no VL-1 dos ciclos 1–3, 297 no ciclo 2, 980 e 229 no VL-2, e 1.619, 914, 1.766 e
  627 no VL-3. A base de cada componente também não importa: a minha (o par mais escolhido) dá o mesmo β que a do 50
  (o par da própria UF).
- **Parâmetros incidentais.** O VL-1 tem 254 efeitos fixos para 5.417 candidatos, e alguns pares têm uma ou duas
  escolhas. Não há sinal de viés. O M4, com só 26 colunas de UF, dá 1,48, praticamente o VL-1 (1,47), e o diagnóstico
  abaixo, com muito mais efeitos fixos, sobe em vez de cair.
- **"O peso da bolsa passa a vir só de vagas da mesma UF" é quase exato.** O efeito fixo do par é comum a todos os
  candidatos da mesma UF de origem. Como as vagas de uma UF mudam de curso para curso e de ciclo para ciclo, parte da
  variação ainda vem de diferenças, entre conjuntos de escolha, na composição de faixas de cada UF. Como diagnóstico
  meu, fora do adendo e sem teste, estimei com efeito fixo de UF de origem × UF da vaga × conjunto de escolha. Esse
  efeito fixo isola por completo a comparação dentro da UF:
  - ciclos 1–3: 1,61 [1,23; 2,10], com 5.105 candidatos e 651 efeitos fixos;
  - ciclo 2: 2,02 [1,35; 3,03], com 1.939 candidatos e 228 efeitos fixos;
  - peso da distância: −0,62 por 100 km nos dois.

  A frase do 57x é conservadora, e não a mudei.
- **Empate em 0,350 no VL-2.** Há 23 células com IVS exatamente 0,350 na janela, com 27 primeiras opções. A decisão 6
  as põe na janela do corte 0,300 (`s > 350` para o intercepto). Com `s ≥ 350`, o VL-2 dá 1,24 [0,92; 1,69], p =
  0,159, contra 1,28 [0,95; 1,72] gravado. A regra do §3 continua `PARECIDA_COM_M1`.
- **Forma do VL-2.** Pela decisão 6, o *spline* é o do M1 restrito à janela, mais o intercepto acima de 0,350. A
  inclinação de 0,300 a 0,350 fica, portanto, igual à de 0,350 a 0,400. Não é uma RDD local-linear com inclinações
  livres em cada lado de cada corte. Isso segue o adendo ("mesmo efeito fixo", "intercepto por corte") e está descrito
  na decisão 6.
- **Janela fechada.** \|IVS − corte\| ≤ 0,050 inclui 0,250, 0,350 e 0,450, como no "≤" do adendo e na robustez de
  janelas do E9 (script 16).
- **O IC do VL-2 não é "muito largo" pela regra.** Em log, a largura é 0,59, contra 0,49 no M1 (1,2 vez; a regra
  pede 2). O IC contém 1 e o da referência também.
- **Por que os km caem.** O 57x diz que é porque a distância pesa mais dentro da UF (−0,51 contra −0,19 por 100 km),
  e não porque a bolsa pese menos (β de 0,045 para 0,077). Isso confere: K5 = 100 · 5β / (−γ), com β 1,7 vez maior e
  γ 2,7 vezes maior. Os km do VL-1 são "km dentro da UF" e não se comparam um a um com os do M1. O texto já diz isso
  à sua maneira.

## Fidelidade ao adendo e às decisões

| Ponto | Conferência |
|---|---|
| Efeito fixo do par (§1, §2) | Indicadores por (UF de origem, UF da vaga), menos uma base por componente conexa de pares de cada origem; `mesma_uf` e macrorregiões saem. No VL-1 dos ciclos 1–3: 27 componentes (uma por origem) e 254 colunas, iguais ao gravado |
| Pares sem escolha e separação (decisão 2) | Limite exato da verossimilhança (observações acima). Contagens idênticas nas 10 linhas: VL-1 dos ciclos 1–3 com 353.575 + 0 de 932.577 alternativas e 4 candidatos fora; ciclo 2 com 206.094 + 297 de 380.022 e 20 fora |
| Distância (decisão 4) | Leitura sustentada pelo adendo (A3); log como secundária |
| Janela do VL-2 (decisão 6) | Fechada, \|s − 300\| ≤ 50 ou \|s − 400\| ≤ 50, e 1ª opção na janela: 4.329 de 5.421 candidatos (ciclos 1–3) e 1.645 de 2.032 (ciclo 2), iguais ao gravado. Intercepto `s > 350` (empate: observações) |
| Score bootstrap (decisão 8) | Kline–Santos: ajuste restrito sem a coluna da bolsa, score e informação no ponto restrito com todos os efeitos fixos, score da bolsa projetado fora dos demais, somado por conjunto. Enumeração dos 2^16 sinais no ciclo 2. Ver a tabela de recálculo |
| Famílias (decisão 9) | Holm nas três principais: 0,004939, 0,002627 e 0,1030, iguais ao gravado. Holm do score: 0,022, 0,011 e 0,183, a mesma decisão |
| Ponto de partida (§7.1) | Ver abaixo |
| Leitura do §3 (decisão 11) | Regra reaplicada por mim: `PARECIDA_COM_M1` nas três principais, `LOCALIZACAO_NAO_EXPLICA`. A1 trata do texto |

**Ponto de partida do Newton.** A log-verossimilhança do logit condicional é côncava, e com a matriz de posto
completo o máximo é único. Conferi isso no VL-1 dos ciclos 1–3, partindo de três pontos, todos com a minha base de
normalização:

- zero, com passo limitado;
- um vetor N(0, 1);
- β = 0 com todos os efeitos fixos = +3.

As três partidas chegam à mesma log-verossimilhança (−12.500,78076770), com |Δβ| ≤ 1,6e−13. O β coincide com o
gravado a 5e−11. O ajuste restrito do score bootstrap, que o 50 faz partindo da estimativa irrestrita, eu fiz partindo
de zero, e o p sai igual.

Também reproduzi o problema que motivou a nota 1. No VL-1 do ciclo 2, o Newton puro partindo de zero leva um efeito
fixo a −266 e para numa log-verossimilhança de −5.001,8. O máximo é −4.492,15. O que falha é a trajetória numérica,
não o modelo, e a correção do executor (só o ponto de partida) é adequada.

**Ordem no Git:**

1. adendo `243160d`, às 03:04;
2. decisões e script sem estimativas `4f8ca82`, às 03:31;
3. execução `28f16fb`, às 04:10.

O bloco de decisões do 57x é idêntico entre `4f8ca82` e `92e7f70`, e as funções `regra_linha` e `leitura` também. O
SHA-256 do adendo (`3023f3ff…`) é o gravado em `VL_resumo.json` e o do arquivo em `243160d`.

## Portão (VL-5)

Confirmado com o meu código:

- **M1 antigo** (tipo de vaga do ciclo 2 de 19/03) contra `P1_estimativas.csv`: coeficientes a 1,6e−10 e EP a
  4,6e−11;
- **M1 corrigido** dos ciclos 1–3 e do ciclo 2 contra `VC_estimativas.csv`: 1,254151 [0,979638; 1,605587] e
  1,788723 [1,193827; 2,680064], coeficientes a ≤ 3,6e−9;
- **M4 corrigido** contra `VD_estimativas.csv`: razão de chances 1,4756. O maior desvio é 1,2e−7, num coeficiente de
  UF, e vem do critério de parada mais frouxo dessa passada do meu Newton. Com critério mais estrito, os termos do M4
  fora das UF batem com `VL_estimativas.csv` a 2,9e−10 nos ciclos 1–3 e a 1,4e−10 no ciclo 2: 1,475607 [1,139500;
  1,910852] e 2,036975 [1,369331; 3,030144];
- **km do M1:** 118,8 [−12,3; 250,0] e 302,4 [88,4; 516,5].

O portão do 50 (máx. 4,5e−10) é coerente com isso.

## O que foi recalculado

Valores do meu recálculo; "Gravado" vem de `VL_estimativas.csv`.

| Linha | Candidatos | G | RC [IC 95%] (auditoria) | p | Gravado |
|---|---|---|---|---|---|
| M1, ciclos 1–3 | 5.421 | 56 | 1,2542 [0,9796; 1,6056] | 0,0724 | 1,254151 [0,979638; 1,605587] |
| M1, ciclo 2 | 2.032 | 16 | 1,7887 [1,1938; 2,6801] | 0,0048 | 1,788723 [1,193827; 2,680064] |
| **VL-1, ciclos 1–3** | 5.417 | 55 | **1,4702 [1,1455; 1,8869]** | 0,0025 | 1,470207 [1,145523; 1,886919] |
| **VL-1, ciclo 2** | 2.012 | 16 | **1,9045 [1,3031; 2,7833]** | 0,0009 | 1,904474 [1,303144; 2,783283] |
| **VL-2, ciclos 1–3** | 4.288 | 55 | **1,2798 [0,9514; 1,7215]** | 0,1030 | 1,279775 [0,951403; 1,721483] |
| VL-2, ciclo 2 | 1.596 | 16 | 1,4725 [1,0136; 2,1392] | 0,0423 | 1,472538 [1,013621; 2,139229] |
| VL-3 (VL-1), ciclos 1–3 / ciclo 2 | 5.360 / 2.001 | 55 / 16 | 1,4878 [1,1521; 1,9213] / 1,9113 [1,3320; 2,7428] | 0,0023 / 0,0004 | iguais |
| VL-3 (VL-2), ciclos 1–3 / ciclo 2 | 4.216 / 1.575 | 55 / 16 | 1,2779 [0,9531; 1,7135] / 1,4899 [1,0413; 2,1318] | 0,101 / 0,029 | iguais |
| VL-1 com log, ciclos 1–3 / ciclo 2 | 5.417 / 2.012 | 55 / 16 | 1,4546 [1,1540; 1,8336] / 1,7517 [1,2338; 2,4869] | 0,0015 / 0,0017 | iguais |

**VL-4 (km equivalentes de +R$ 5 mil, delta).**

| Modelo | Auditoria | Gravado |
|---|---|---|
| VL-1, ciclos 1–3 | 74,91 km [27,72; 122,10] | 74,910958 [27,72323; 122,098686] |
| VL-1, ciclo 2 | 116,57 km [55,54; 177,61] | 116,573395 [55,535729; 177,611061] |

O peso da distância é −0,514 nos ciclos 1–3 e −0,553 no ciclo 2, contra −0,191 e −0,192 no M1. O Fieller não foi
refeito.

**Score bootstrap (Rademacher), p.**

| Linha | Auditoria | Gravado |
|---|---|---|
| VL-1, ciclos 1–3 | 0,0112 (400 mil sorteios, semente 48) | 0,0113 (199.999, semente 20261018) |
| VL-1, ciclo 2 | 0,0035 (enumeração) | 0,0035 |
| VL-2, ciclos 1–3 | 0,1835 | 0,1830 |
| M1, ciclos 1–3 | 0,1222 | 0,1215 |
| M1, ciclo 2 | 0,0074 (enumeração) | 0,0074 |

**Identificação (seção 3 do 57x).** Todas as contagens são idênticas:

- ciclos 1–3: 281 pares com escolha (de 729), 260 com variação de bolsa, de 27 das 27 UFs de origem; 5.345 dos 5.417
  candidatos veem variação dentro de alguma UF, e 3.937 escolheram a 1ª opção numa UF assim;
- ciclo 2: 169 pares, 151 com variação, 1.956 de 2.012 candidatos;
- VL-2 e VL-3: as 4 + 4 linhas da tabela, iguais.

Um par conta como "com variação" quando algum candidato vê, dentro dele, vagas de bolsas diferentes.

## Integridade

| Item | Conferência |
|---|---|
| IVS errado | Rodei a carga do 50 (funções de leitura do P1 e do 52c) sob um *audit hook* de `open`. Nenhum `ivs_ipea_2010_municipios` foi aberto; o único IVS lido é `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`. Nenhum dos scripts importados cita o arquivo errado |
| `data/` | Só leitura: CIR, centroides (e manifesto) e os dois quadros do ciclo 2. Nenhuma escrita |
| `EMPIRICO` | 225 de 225 linhas de `VL_estimativas.csv` e o resumo |
| Nada imputado | `imputadas = 0`. Na minha troca do ciclo 2, nenhuma das 1.545 células ficou sem número no quadro de 13/02 (301 têm vagas imediatas diferentes das de 19/03) |
| Saídas antigas | `E9_*`, `P1_*`, `P1h_*`, `VC_*` e `VD_*` sem mudança desde `4f8ca82` (diff vazio), e os docs 57a, 57i, 57p e 57v também |
| Identificadores | Nenhum CPF, nome, CRM ou `id_candidato` nas saídas (teste do 50) |
| Determinismo | Reexecução completa do 50 (cerca de 7 min nesta máquina): `VL_estimativas.csv`, `VL_resumo.json`, a figura e o 57x idênticos byte a byte aos de `92e7f70` |

## Texto do 57x

- **Linguagem.** É simples. A seção "Em linguagem simples" diz a pergunta, o que se compara e o que a bolsa mede.
- **Leitura causal.** Não há leitura causal indevida. A bolsa é o "pacote do corte", a origem é "preferência
  revelada, não efeito causal", e não se trata de participação no PMM-E. A frase de abertura ("não vem da
  localização") vale para a localização no nível da UF; os limites dizem o que o par não controla.
- **Números.** Todos os números estão em blocos gerados (teste `test_nenhum_numero_de_resultado_fora_dos_blocos`).
- **Por que os km caem.** O texto explica, com os dois pesos da distância (observações).
- **Correções desta auditoria** (A1 a A4), feitas no gerador do script 50 e aplicadas com `--atualizar-doc`:
  - a frase de abertura e a linha do VL-1 dos ciclos 1–3, com a leitura da diferença pareada;
  - a frase do M4;
  - a frase da distância em log;
  - o cabeçalho, que aponta para esta auditoria e registra que a redação da resposta é posterior às estimativas;
  - a docstring.

  O teste do 57x passou a conferir o novo cabeçalho e a presença das três frases.

## O que fica para o autor

- O rótulo `PARECIDA_COM_M1` nos ciclos 1–3 segue a regra pré-registrada e não foi mudado. Se o autor quiser que
  "parecida" passe a ser julgada pela diferença pareada, isso é decisão nova e vale para os próximos adendos, não
  para este.
- O diagnóstico com efeito fixo de UF de origem × UF da vaga × conjunto (1,61 e 2,02) é da auditoria, fora do
  adendo e sem teste. Não entra no 57x.
