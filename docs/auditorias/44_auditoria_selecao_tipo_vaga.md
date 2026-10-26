# 44. Auditoria do adendo 48f: seleção pelo tipo de vaga na H1 (tipo como outcome, balanço e limites de Lee)

> **Data:** 26/10/2026.<br>
> **Objeto:**
> - adendo [`48f`](../06_execucao/48f_adendo_selecao_tipo_de_vaga.md), congelado no commit `f97e1ca`;
> - script `scripts/rdd_bolsa/46_selecao_tipo_vaga.py`;
> - saídas `output/rdd_bolsa/SV_*`;
> - doc [`57t`](../06_execucao/57t_resultados_selecao_tipo_vaga.md), com as 30 decisões da seção 0 (commit `efdeece`);
> - testes `tests/test_selecao_tipo_vaga.py`.
>
> Base: branch `claude/vigilant-mccarthy-dd92mc`, commit `4633904`.<br>
> **Referências:**
> - `CLAUDE.md`;
> - adendo 48b (§7), doc 57n e [auditoria 38](38_auditoria_h1_vagas_imediatas.md);
> - adendo 48d, doc 57r e [auditoria 40](40_auditoria_controles_localizacao_medicos.md);
> - doc 57l, parte D-b;
> - banca 2, doc 05, §2.12;
> - `rdd_lib.py` (`_multiplicador_aparo`), lida e não importada.
>
> **Método:** recálculo próprio em memória, com scripts no scratch. Nada foi gravado em `output/` além da reexecução
> do próprio 46. O recálculo não importa os scripts 46, 44, 40 e 24 nem a `rdd_lib`. Ele lê direto:
> - a base de células e a de municípios (`outcomes_V_*`);
> - o IVS oficial (a08);
> - o quadro bruto do ciclo 2 de 13/02/2026, com leitor próprio;
> - população, painel a09 (só de 202406 a 202506), capitais do IBGE e a CIR.
>
> Escrevi do zero a RDD empilhada com CR1, a aparagem de Lee, o bootstrap, o IC de Imbens–Manski e as covariáveis.
> **Estatuto do que se audita:** `ADENDO_48F_POS_RESULTADO`, robustez pós-resultado da H1. O contraste é o pacote do
> corte, não a participação no PMM-E nem o incentivo de R$ 5 mil isolado.

## Veredito

**Aprovado com correções.** O que recalculei bate com o gravado até 5e−13:
- o portão inteiro;
- o SV-1, o SV-2 (40 linhas) e as taxas de seleção por ciclo;
- os 12 pares de limites de Lee (SV-3 a SV-5);
- os 12 IC de Imbens–Manski, com o mesmo esquema de sorteio.

O script é fiel ao adendo. As 30 decisões não mudam o que o adendo fixava. Elas foram registradas antes das
estimativas (`efdeece`, 20:55, antes de `f38429e`, 21:07).

**Nenhuma estimativa mudou.** `SV_estimativas.csv`, `SV_balanco.csv` e `SV_limites_lee.png` ficaram iguais byte a
byte depois de rodar o 46 de novo. `HI_*`, `CL_*` e `DQ_*` não foram regravados.

Fiz correções de texto nos blocos gerados pelo 46 (achados 1 a 6) e uma de proveniência (achado 9). Por isso mudaram
o 57t, o "Como ler" e a figura `SV_taxa_selecao.png`, e `SV_resumo.json`.

Um ponto de mérito fica para o autor (achado 1). Em 0,300, o código `SELECAO_PEQUENA` sai do q dos ciclos juntos. É a
leitura pré-registrada, mas ela não basta para dizer que o 48b fica livre da seleção. O que sustenta a H1 nesse corte
são os limites de Lee por ciclo.

## Achados, por gravidade

### Médios

**A1. Em 0,300, "seleção pequena" vem do q dos ciclos juntos (corrigido no texto; a regra fica).**

A decisão 16 aplica a regra "q < 0,05" do §4 ao q dos ciclos juntos. Para isso, combina as taxas de cada ciclo pelo
número de unidades com S = 1. O §4 não diz qual q usar. A decisão foi fixada antes das contas e o código a segue.

Em 0,300, porém, o lado com mais vaga imediata muda de ciclo para ciclo:

| Ciclo | p_abaixo | p_acima | q | Lado aparado | RDD de S só nesse ciclo (auditoria, descritivo) |
|---|---|---|---|---|---|
| 1 | 47,6% | 60,7% | 0,216 | de cima | +19,6 p.p. [−23,4; +62,5] |
| 2 | 72,9% | 64,8% | 0,111 | de baixo | −15,1 p.p. [−50,1; +19,8] |
| 3 | 48,3% | 55,4% | 0,128 | de cima | +22,4 p.p. [−8,1; +52,9] |
| juntos | 57,9% | 60,4% | 0,042 | de cima | +8,8 p.p. [−14,7; +32,3] (SV-1) |

O 48b empilha os ciclos com intercepto e inclinações por ciclo, ou seja, compara dentro do ciclo. Uma seleção num
sentido no ciclo 1 e no outro no ciclo 2 não se anula necessariamente na H1. A frase "o 48b não é muito afetado por
ela" segue a letra do §4, mas sozinha diz mais do que os dados mostram.

Com o q máximo por ciclo, que é a outra leitura possível, 0,300 cairia em `IC_CONTEM_ZERO_MAS_TAXAS_DIFEREM`, como
0,400. Os limites de Lee não mudam em nenhuma das duas leituras, porque já aparam com o q de cada ciclo.

Trocar a regra agora seria escolher retrospectivamente, por isso ela fica. O que corrigi foi o texto:
- a resposta curta diz que o "pequena" vale só com os ciclos juntos e dá o q máximo por ciclo;
- o parágrafo "Por ciclo" diz que o código vem da regra e que, nesse corte, quem protege a H1 são os limites de Lee;
- a seção 7 leva a mesma ressalva.

Nenhuma RDD de S por ciclo exclui zero. A troca de sentido pode ser acaso, e o texto diz isso na seção 9.

**A2. A linha do SV-5 de um lado do zero precisava de peso explícito (corrigido).**

A linha é Y2 em 0,300, com a reta. Os limites conferem: [−0,1947; −0,0133], IC de Imbens–Manski [−0,391; +0,193].

O texto antigo listava a linha como "leitura diferente" sem dizer o peso dela. Agora o bloco gerado diz:
- pela decisão 29 (fixada antes), ela não muda a leitura do SV-3;
- o limite superior fica em −0,01, colado no zero;
- com o IC de Imbens–Manski contendo zero, o sinal não se distingue do acaso;
- o SV-5 é a versão com a reta, como a HI-1 e a HI-2 do 48b;
- a diferença sem aparo vai de +0,04 (SV-3) para −0,10 (SV-5);
- o sentido é o da HI-2 do 48b em 0,300 (−1,13, p Holm 0,126), em outra escala.

O ponto de fundo é que o "não se detecta" do SV-3 depende da hipótese de randomização local na janela de 0,050. A
seção 9 já dizia isso, e agora a resposta curta também diz.

**A3. O 57t não explicava por que o D-b mostrava salto no tipo de vaga e o SV-1 não (corrigido).**

As 16 linhas do D-b com o quadro de 19/03 reproduzem o 57l. O 57t explicava a diferença de definição, mas não
reconciliava os números. Na célula, ter vaga imediata é 1 menos ser só de CR. Com os ciclos juntos, a parte só de CR
salta assim:

| Corte | 19/03, sem EF (57l) | 13/02, sem EF | 13/02, com EF de curso × ciclo (= −SV-1 célula) |
|---|---|---|---|
| 0,300 | +15,4 p.p. [+2,1; +28,6] | +14,0 p.p. [−0,2; +28,3] | +4,3 p.p. [−7,5; +16,1] |
| 0,400 | +11,3 p.p. [−1,5; +24,1] | +7,2 p.p. [−12,8; +27,2] | +2,3 p.p. [−18,9; +23,5] |

Recalculei as três colunas. Duas coisas mudam do 57l para cá:
- a troca do quadro do ciclo 2 leva o IC de 0,300 a encostar no zero;
- os efeitos fixos de curso × ciclo tiram cerca de dois terços do salto.

A mistura de cursos não é a mesma dos dois lados, e a parte só de CR varia por curso (descritivo). O S do município é
outra margem: ter alguma vaga imediata.

Acrescentei esse parágrafo ao bloco do portão, gerado das saídas. **Recomendação ao autor:** a §2.12 da banca 2
(canal 1) cita +15,4 p.p. [+2,1; +28,6], com o quadro de 19/03. Vale atualizar com as colunas acima. Não editei a
§2.12: é conteúdo de apresentação.

### Menores

**A4. A referência à H1 do 48b não dava o Holm (corrigido).** A resposta curta mostrava a HI-2 de 0,300 com IC que
exclui zero e não dizia que ela não passa no Holm do 48b (p Holm 0,126). Agora os quatro p de Holm aparecem, lidos de
`HI_estimativas.csv`, com a frase "Nenhuma das quatro rejeita zero depois do Holm do 48b", que só aparece se for
verdade.

**A5. O texto não dizia para quem vale o intervalo de Lee (corrigido).** O intervalo vale para os "sempre
selecionados": municípios × ciclo que teriam vaga imediata dos dois lados do corte. Não vale para todo município com
vaga imediata. Isso foi acrescentado à premissa, na seção 9.

**A6. O "Como ler" da figura de taxas tinha linguagem forte (corrigido).** Dizia "o tipo de vaga muda no corte"
quando as barras diferem, e "q é a parte que os limites aparam", inclusive para "juntos", cujo q não apara nada.
Agora diz que a chance difere entre os lados na janela (pode ser acaso) e que o q de "juntos" só entra na regra do
§4. A figura foi regerada; os números dela não mudaram.

**A7. A monotonicidade é tratada por ciclo, corretamente, e o texto agora explica por quê.** Os limites aparam dentro
de cada ciclo, com o lado e o q de cada ciclo, e combinam pelo número de unidades com S = 1. Por isso a premissa de Lee
só precisa valer dentro de cada ciclo. Juntar os ciclos com um q só exigiria o mesmo sentido em todos, o que 0,300 não
mostra. A seção 9 já dizia que a premissa vale dentro do ciclo. Acrescentei:
- por que não se pode juntar os ciclos com um q só;
- que a troca de sentido é compatível com acaso;
- que o lado aparado de cada ciclo é o da taxa estimada.

**A8. O bootstrap estratificado pelo lado é detalhe, não desvio (sem correção).** O adendo pede blocos de município. A
decisão 17 sorteia municípios dentro de cada lado, com o lado fixado pelo IVS. Refiz com um bootstrap meu, não
estratificado, com outra semente e 1.999 reamostras. Os IC de Imbens–Manski mudam no máximo 0,01 na escala de cada
outcome:
- SV-3, 0,300, Y1: [−19,0; +22,0] p.p., contra [−19,0; +22,2] gravado;
- SV-5, 0,300, Y2: [−0,387; +0,191], contra [−0,391; +0,193] gravado.

Nenhuma leitura muda. Repetindo o esquema do script (mesma semente, municípios em ordem, um gerador por corte ×
janela), as 12 linhas batem até 1e−16, com as 1.999 reamostras válidas.

**A9. Duas entradas lidas não tinham hash (corrigido).** `E6.chaves_populacoes` lê `outcomes_U_municipio.parquet` e
`outcomes_G3_municipio.parquet`, mas `entradas` em `SV_resumo.json` não os listava. Foram acrescentados com SHA-256.

**A10. A regra de empates não muda nenhum limite (sem correção).** A decisão 12 usa empates proporcionais
(auditoria 22). Refiz a aparagem por ordem das linhas, com o código IBGE em ordem crescente e em ordem decrescente. Os
quatro pares do SV-3 ficam iguais até a 4ª casa. Há uma razão matemática: dentro de um bloco de valores iguais de Y,
tirar peso de uma unidade ou de outra deixa a média igual. A decisão é inócua para estes limites.

### Sem achado (fidelidade ao adendo)

| Ponto do adendo | Verificação |
|---|---|
| S = 1 se o município × ciclo tem ≥ 1 célula com vaga imediata | refeito de `outcomes_V_celula`; 215, 328 e 307 com S = 1 nos ciclos 1 a 3 (de 368, 454 e 747) |
| Y1 e Y2 ausentes quando S = 0 | conferido: observados exatamente quando S = 1, nunca zero |
| Ciclo 2 pelo quadro de 13/02 | leitor próprio do xlsx bruto (colunas TOTAL de "VAGAS IMEDIATAS" e "CADASTRO RESERVA"); as 1.547 células casam uma a uma |
| RDD: local linear, triangular, h = 0,050, ciclos empilhados, CR1 por município | SV-1 (S e célula com EF de curso × ciclo) e SV-2 iguais |
| Lee §3: taxas por ciclo, q no lado de taxa maior, direção | lado de cima aparado: no inferior saem os maiores Y; lado de baixo aparado: no inferior saem os menores. Conferido também nos casos sintéticos do teste |
| Combinação com o peso de cada ciclo no número de unidades com S = 1 | igual ao §3, passo 1 |
| IC de Imbens–Manski, bootstrap em blocos de município, 1.999, semente 20261026, aparagem refeita | igual |
| Leitura do §4 | refeita das saídas; mesmos códigos |
| Novo código `IC_CONTEM_ZERO_MAS_TAXAS_DIFEREM` (0,400: q = 0,204) | o §4 não cobria o caso "IC de S com zero e q ≥ 0,05". A decisão 27 o fixou em `efdeece`, antes das estimativas, e lhe deu a mesma consequência da linha "IC exclui zero" (dar peso aos limites). É a escolha conservadora e razoável |
| SV-4 (janela 0,020) e SV-5 (reta por ciclo × lado, aparo nos resíduos) | leitura literal do adendo; refeitos |
| SV-2: regra "desbalanço maior entre S = 1" | contagem de IC sem zero (decisão 24); 3 contra 1 em 0,300 e 1 contra 1 em 0,400, refeitos |

**Portões.**
- HI-1 e HI-2 do 48b: refeitos nos dois cortes; diferença ≤ 1e−13 no salto e no EP.
- D-b do 57l: as 16 linhas refeitas com o quadro de 19/03 (salto, EP, médias e n por lado); diferença ≤ 2e−14.
- A diferença de definição está bem descrita no 57t. A reconciliação dos números foi acrescentada (A3).

## Integridade

| Item | Resultado |
|---|---|
| IVS errado e malha de regiões | rastreio de arquivos abertos na execução do 46: nenhum dos dois é lido; a região de saúde vem da CIR oficial (`.cnv`) |
| CNES | painel a09 só de 202406 a 202506; nenhuma competência ≥ 202609 |
| `EMPIRICO` | em todas as linhas de `SV_estimativas.csv` (68) e `SV_balanco.csv` (40) e no resumo |
| Imputação | nada imputado; Y ausente quando S = 0; covariável ausente fica ausente |
| `HI_*`, `CL_*`, `DQ_*` | só lidos (rastreio); hashes iguais antes e depois |
| Determinismo | duas execuções seguidas do 46 dão saídas iguais byte a byte, antes e depois das correções |
| `data/` | nada escrito |
| Testes | `tests/test_selecao_tipo_vaga.py`: 27 passam (o teste do cabeçalho agora espera o link desta auditoria); `tests/test_pipeline_rdd_bolsa.py`: 15 passam |

## Texto do 57t

- **Linguagem causal:** nenhuma frase atribui efeito à bolsa. O texto fala sempre do pacote do corte, e "não se
  detecta" vem com "não é mostrar que é zero". As exceções eram "o tipo de vaga muda no corte" no "Como ler" (A6) e o
  "não é muito afetado" sem ressalva (A1), ambas corrigidas.
- **Números fora dos blocos:** só parâmetros do adendo. O teste confere isso.
- **Premissa:** dita com clareza na seção 9. Agora diz também para quem vale o intervalo (A5) e por que basta valer
  por ciclo (A7).
- **Clareza para o autor:** a seção "A pergunta, em linguagem simples" e as tabelas por ciclo são boas. A principal
  lacuna era a reconciliação com o D-b (A3).

## O que foi recalculado

"Gravado" é o valor de `SV_*`. As diferenças são absolutas, na escala da saída.

| Item | Recalculado | Gravado | Diferença máxima |
|---|---|---|---|
| Amostra (município × ciclo; S = 1) | 368/215, 454/328, 747/307 | igual | 0 |
| SV-1, S, 0,300 | +8,82 p.p., EP 12,00 p.p.; 145/120 municípios; 441 linhas | igual | 1e−16 |
| SV-1, S, 0,400 | −12,51 p.p., EP 8,49 p.p.; 122/145; 415 | igual | 1e−15 |
| SV-1, célula (EF curso × ciclo), 0,300 / 0,400 | −4,30 / −2,32 p.p.; 2.115 / 1.243 células | igual | 2e−14 |
| Taxas por ciclo e juntas, janelas 0,050 e 0,020 | p_acima, p_abaixo, q e lado dos 3 ciclos, nos 2 cortes | igual | 6e−17 |
| q juntos, 0,300 / 0,400 | 0,0420 / 0,2039 | igual | 3e−17 |
| SV-3, 0,300: Y1 / Y2 | [−7,36; +9,59] p.p. / [−0,054; +0,119] | igual | 1e−16 |
| SV-3, 0,400: Y1 / Y2 | [−12,97; +16,24] p.p. / [−0,149; +0,159] | igual | 1e−16 |
| SV-4 e SV-5, 8 pares de limites e "sem aparo" | todos | igual | 1e−16 |
| SV-5, 0,300, Y2 | [−0,1947; −0,0133]; sem aparo −0,1006 | igual | 1e−16 |
| IC de Imbens–Manski, mesmo esquema, 12 linhas | ex.: SV-3 0,300 Y1 [−19,01; +22,20] p.p.; SV-5 0,300 Y2 [−0,391; +0,193] | igual | 1e−16 |
| IC de Imbens–Manski, bootstrap próprio não estratificado (semente 12345) | ver A8 | — | ≤ 0,01 na escala do outcome |
| SV-2, 10 covariáveis × 2 amostras × 2 cortes | salto, EP, salto padronizado | igual | 5e−13 |
| Portão HI-1 / HI-2 | −0,036784 / −1,126326 (0,300); −0,023120 / −0,156707 (0,400) | igual | 1e−13 |
| Portão D-b, 16 linhas, quadro de 19/03 | salto, EP, médias, n | igual | 2e−14 |
| Célula sem EF, quadro de 13/02 (A3) | −14,0 p.p. [−28,3; +0,2] em 0,300; −7,2 [−27,2; +12,8] em 0,400 | = −D-b de 13/02 no 57t | 0 nas casas mostradas |

## O que mudou nesta auditoria

- `scripts/rdd_bolsa/46_selecao_tipo_vaga.py`: só texto gerado (A1 a A7) e duas entradas com hash (A9). Nenhuma conta
  mudou.
- `docs/06_execucao/57t_resultados_selecao_tipo_vaga.md`: blocos regerados pelo script e cabeçalho com o link desta
  auditoria.
- `output/rdd_bolsa/SV_resumo.json` (entradas e "Como ler") e `SV_figuras/SV_taxa_selecao.png` (rodapé "Como ler").
- `tests/test_selecao_tipo_vaga.py`: o cabeçalho esperado passa de "pendente" para o link desta auditoria.
