# 40. Auditoria do adendo 48d: controles de localização e de médicos na região, e pareamento (PSM principal)

> **Data:** 26/10/2026.<br>
> **Objeto:** adendo [`48d`](../06_execucao/48d_adendo_controles_localizacao_e_medicos.md) (com as §3.1 e §3.2),
> script `scripts/rdd_bolsa/44_controles_localizacao_medicos.py`, saídas `output/rdd_bolsa/CL_*`, doc
> [`57r`](../06_execucao/57r_resultados_controles_localizacao_medicos.md) (25 decisões da seção 0 e notas datadas) e
> `tests/test_controles_localizacao_medicos.py`. Base: branch `claude/vigilant-mccarthy-dd92mc`, commit `e9802ab`.<br>
> **Método:** recálculo próprio em memória (scratch, nada gravado em `output/` além da reexecução do próprio script
> 44), sem importar os scripts 40, 43 e 44 nem a `rdd_lib`. Covariáveis, unidades da H1, ΔB1/ΔB2, escore, pares,
> permutação e RDD com CR1/HC1 escritos do zero. Só a leitura do quadro do ciclo 2 de 13/02/2026 usou a função da
> auditoria 36 (`a36_leitura.ler_quadro`).

## Veredito

**Aprovado com correções.** Toda estimativa recalculada bate com a gravada, nas casas mostradas e, no PSM, com os
mesmos 86 e 88 pares. Nenhuma estimativa mudou. As correções foram de texto e de diagnóstico: o 57r não dizia em
linguagem simples o que o balanço no corte implica para a RDD, e o diagnóstico de separação em 0,400 deixava de fora
o Centro-Oeste. A falta do PSM em 0,400 segue a regra congelada antes das contas (decisão 13). Mudar essa regra é
decisão do autor e exige novo adendo; as opções estão no fim deste documento.

## Achados, por gravidade

### Médios

**A1. Separação em 0,400 descrita pela metade (corrigido).** O 57r dizia que o logit não convergiu por causa das
capitais e do Sul. Na H1 há uma terceira categoria só de um lado: o **Centro-Oeste**, a categoria de referência da
macrorregião, tem 8 unidades na janela, todas abaixo do corte. O diagnóstico do script só olhava as colunas de dummy
e não via a categoria de referência. Conferi que a separação é real e não um defeito numérico:

| Janela de 0,050 em 0,400 | Capitais (abaixo / acima) | Sul | Centro-Oeste | Logit |
|---|---|---|---|---|
| H1 (município × ciclo) | 10 / 0 (4 municípios) | 1 / 0 | 8 / 0 | não converge; coeficiente máximo ≈ 24 |
| H1 sem capitais e Sul | — | — | 8 / 0 | ainda não converge |
| H1 sem capitais, Sul e Centro-Oeste | — | — | — | converge |
| V (protocolo 64) | 4 / 0 | 1 / 0 | dos dois lados | não converge; sem capitais e Sul, converge |

As capitais da janela são Salvador (IVS 0,350), São Luís (0,372), Manaus (0,387) e Maceió (0,393). Nenhuma capital
tem IVS entre 0,400 e 0,450, então é impossível ter capital do lado de cima. Correção: o diagnóstico passou a contar
cada macrorregião, inclusive a de referência, e o número de municípios distintos. O texto gerado do 57r e a figura
`CL_escore.png` mudaram. As estimativas, `CL_estimativas.csv` e `CL_balanco.csv` ficaram iguais byte a byte.

**A2. O 57r não dizia com clareza o que o balanço no corte implica (corrigido).** A resposta curta listava as
variáveis que saltam e mostrava o código `ANDA_JUNTO_COM_LOCALIZACAO_OU_MEDICOS`, sem explicar. Em 0,300, o lado de
bolsa maior tem **menos capitais**, **menos municípios do Nordeste** e **mais especialistas no resto da região de
saúde**. Isso quer dizer que a hipótese da RDD (lados iguais em média, tirando o pacote) falha nessas variáveis, e
que a queda da HI-2 não se separa delas. Acrescentei ao bloco gerado um parágrafo "O que o balanço no corte quer dizer
(limite da RDD)", corte a corte, montado das saídas: direção de cada salto, a HI-2 indo de −1,11 [−2,17; −0,05] para
−0,25 [−1,37; +0,87] com L+M e o aviso de que isso não prova que a localização explica a queda.

**A3. Decisão 13: separação ou não convergência deixa a linha sem estimativa.** O adendo não fixava o que fazer
nesse caso, mas a §3.2 previa contar e relatar quem ficasse fora do suporte, "com quem são: capitais, região". A
leitura mais próxima disso seria tirar essas unidades, não abandonar o corte. A decisão foi registrada antes de
qualquer estimativa (commit `05830ac`, anterior a `362e830`) e é conservadora, então fica como está. O efeito é que
o principal do adendo só informa 0,300. O 57r agora diz isso. O remédio fica para o autor (ver o fim do documento).

**A4. Decisão 11: guloso global em vez de "o lado com menos unidades procura par".** A §3.1 do adendo fixa que o
lado menor procura par. A decisão 11 usou o guloso global (o par mais próximo primeiro), antes das contas. A §3.2
(PSM) não fixa ordem. Refiz o PSM em 0,300 com o lado menor (o de cima) procurando, em ordem de código:

| Linha | Guloso global (gravado) | Lado menor procura (auditoria) |
|---|---|---|
| PS-1 fração preenchida | −0,6 p.p. [−13,1; +11,8], 86 pares | +2,8 p.p. [−8,9; +14,4], 89 pares |
| PS-1 alocados por vaga imediata | +0,04 [−0,08; +0,17], 86 pares | +0,07 [−0,05; +0,19], 89 pares |
| PS-2 ΔB1 | −0,09 [−0,96; +0,78], 88 pares | +0,22 [−0,65; +1,09], 89 pares |
| PS-2 ΔB2 | −0,71 [−9,32; +8,01], 87 pares | +3,41 [−5,27; +12,12], 88 pares |

Em todas as linhas o IC contém zero nas duas versões. A conclusão não muda; a estimativa pontual depende da ordem do
pareamento. O 57r registra isso na §7.1, sem os números (que ficam aqui, por não serem saída do pipeline).

### Menores

**A5. Troca da malha pela CIR: histórico não prova o "antes".** A revisão da decisão 5 entrou no mesmo commit dos
resultados (`362e830`), e o Git não mostra se ela veio antes das contas. No mérito, a troca é necessária e está
correta. Conferi:

- a coluna `no_regiao_saude` da malha está vazia em **5.034 dos 5.565** municípios (531 com valor);
- a CIR vem de `data/raw/aquisicao/territorio/datasus_tabnet_br_regsaud.cnv`, versionada no commit `ce37a14`
  (19/10/2026, script 19), com manifesto `X5_manifesto_regioes_saude_cir.json`; o SHA-256 `df0f635a…` do arquivo é
  igual ao do manifesto;
- a tabela tem 5.606 municípios e 446 CIR (439 nos municípios do a08), e falta um município do a08;
- meu parser próprio dá as mesmas contagens: 3 municípios sem o "resto da região", 1 deles sem CIR.

Ressalvas: o download foi por HTTP e não por HTTPS, de modo que a integridade vale a partir do hash gravado no
download. A tabela é a versão vigente em 2026, não uma medida do pré. A composição das CIR é geografia
administrativa quase fixa, então a regra "pré-determinada ou fixa" do adendo §1 fica atendida. O adendo diz que nada
é adquirido, e a CIR já estava no repositório. A nota da decisão 21 (ΔB pelas funções do 43) está no mesmo commit, é
inócua e o portão OC-A1 a confere.

**A6. Holm e BKY contam só as linhas executadas.** A decisão 19 define a família do Holm com 8 linhas (PS-1 e PS-2,
dois outcomes × dois cortes). O código usa só as 4 executadas. O BKY usa 76 linhas. Nada muda: todos os p de Holm e
todos os q de BKY já são 1,000, e contar as linhas sem estimativa com p = 1 só aumentaria os ajustados.

**A7. Regra "anda junto" com uma condição a mais.** O código só marca `ANDA_JUNTO_…` quando o IC da CL-4 exclui zero.
A decisão 23 não tem essa condição. Não tem efeito: nas linhas em que ela pesaria (HI-1), "perto de zero" já é falso.

**A8. Dependência do script 41 (adendo 48c, WIP sem auditoria).** O 44 importa do 41 só `carregar_referencias`, que
lê `output/aquisicao/ibge_capitais_uf_regiao.csv` e confere o SHA-256 com o manifesto, e a lista `A36.CAPITAIS`. A
referência foi baixada pelo 41 (`--baixar-referencias`, IBGE Localidades 2022 e SIDRA 4709), que não está no
`run_all.py`. Conferi o conteúdo: as 27 capitais são iguais às da auditoria 36 (o 44 também confere), e a região de
cada UF é igual à dada pelo primeiro dígito do código da UF. Importar o 41 carrega o `a36_reconstruir_H1.py`, que
define o caminho do IVS errado mas não o lê; o rastreio de arquivos abertos confirma. Recomendação: quando o 48c for
auditado, ou antes, mover a aquisição da referência do IBGE para uma etapa de aquisição do pipeline.

> **Nota de 26/10/2026.** A fonte bruta foi arquivada por uma etapa de aquisição própria,
> `scripts/aquisicao/a19_arquivar_ibge_capitais_uf.py`, em `data/raw/aquisicao/ibge_capitais_uf/`, com os 7 SHA-256
> iguais aos do manifesto do 41. O modo `--verificar` (padrão, sem rede) reconstrói a cópia byte a byte. Ver a nota
> no veredito da [auditoria 42](42_auditoria_capitais_uf.md), achado A1. O a19 não entrou no `run_all.py`: o 41 continua
> lendo a cópia e conferindo o hash, como antes.

**A9. Doc 63 com direção ambígua (corrigido).** "saltam … a capital, o Nordeste e os especialistas no resto da região
(mais do lado de bolsa maior)" dava a entender "mais capitais" do lado de cima, e é o contrário. O texto foi
corrigido, com o Centro-Oeste acrescentado à separação.

**A10. Mahalanobis quase sem pares: leitura correta, não erro de escala.** A decisão 12 usa como *caliper*
0,25 × o desvio-padrão das distâncias de todos os pares admissíveis. Recalculei por corte e ciclo (H1, janela de
0,050):

| Corte | Ciclo | DP das distâncias | *Caliper* | Vizinho mais próximo (mín. / mediana) | Unidades de cima com vizinho dentro do *caliper* |
|---|---|---|---|---|---|
| 0,300 | 1 | 1,01 | 0,25 | 0,39 / 0,93 | 0 de 33 |
| 0,300 | 2 | 1,24 | 0,31 | 0,35 / 0,89 | 0 de 42 |
| 0,300 | 3 | 1,15 | 0,29 | 0,33 / 0,89 | 0 de 43 |
| 0,400 | 1 | 0,98 | 0,25 | 0,53 / 1,20 | 0 de 25 |
| 0,400 | 2 | 1,44 | 0,36 | 0,29 / 0,80 | 2 de 38 |
| 0,400 | 3 | 1,29 | 0,32 | 0,24 / 0,74 | 3 de 35 |

A distância de Mahalanobis já está em desvios-padrão, e o desvio-padrão das distâncias fica perto de 1. Por isso a
outra leitura possível do adendo ("0,25 desvio-padrão" direto na distância) dá quase o mesmo limite e também quase
nenhum par. O motivo é o *caliper* congelado ser apertado demais para quatro variáveis contínuas com pareamento exato
em região, capital e ciclo. A leitura de Rosenbaum e Rubin (*caliper* no escore de propensão) não cabe na §3.1, que
não define escore.

## O que foi recalculado

Todos os valores são do recálculo próprio. "Gravado" é o valor de `CL_*` e do 57r.

| Item | Recalculado | Gravado | Diferença |
|---|---|---|---|
| Portão HI-1 (0,300 / 0,400) | −0,036784 / −0,023120 | −0,036784 / −0,023120 | < 1e−6 |
| Portão HI-2 (0,300 / 0,400) | −1,126326 / −0,156707 | −1,126326 / −0,156707 | < 1e−6 |
| Portão OC-A1 (V, 0,300); V | −0,229095; 1.037 municípios | −0,229095; 1.037 | < 1e−6 |
| CL-0, HI-2, 0,300: capital | −29,9 p.p. [−57,1; −2,8], p 0,031 | igual | 0 nas casas mostradas |
| CL-0, HI-2, 0,300: Nordeste | −47,7 p.p. [−82,6; −12,8], p 0,0075 | −47,7 [−82,6; −12,8], p 0,007 | 0 (arredondamento) |
| CL-0, HI-2, 0,300: especialistas no resto da região | +10,54 [+3,54; +17,54], p 0,003 | igual | 0 |
| CL-0, V: capital em 0,300; resto da região em 0,400 | −11,6 p.p.; +6,56 [+0,42; +12,70] | igual | 0 |
| CL-4 HI-2, 0,300 (amostra L+M) | −1,106 [−2,166; −0,047], p 0,041 | −1,11 [−2,17; −0,05], p 0,041 | 0 |
| CL-1 HI-2, 0,300 (L+M) | −0,250 [−1,372; +0,872], p 0,662 | −0,25 [−1,37; +0,87], p 0,662 | 0 |
| CL-4 / CL-1 HI-2, 0,400 | −0,157 / −0,382 | −0,16 / −0,38 | 0 |
| PS-1, 0,300: pares | 86, mesmo conjunto de pares | 86 | idêntico |
| PS-1, 0,300: fração preenchida | −0,61 p.p. [−13,09; +11,79], p 0,922 | −0,6 [−13,1; +11,8], p 0,922 | 0 |
| PS-1, 0,300: alocados por vaga imediata | +0,044 [−0,085; +0,170], p 0,492 | +0,04 [−0,08; +0,17], p 0,492 | 0 |
| PS-1, 0,300: maior DP antes / depois | 0,25 / 0,15; 5 de cima fora do suporte | 0,25 / 0,15; 0 / 5 | 0 |
| PS-3 H1, 0,300 (janela 0,020) | 23 pares; DP depois 0,30; fora do suporte 6 / 12 | igual | 0 |
| PS-2, 0,300: ΔB1 | −0,089 [−0,965; +0,784], p 0,840, 88 pares | igual | 0 |
| PS-2, 0,300: ΔB2 | −0,711 [−9,316; +8,009], p 0,878, 87 pares | igual | 0 |
| PS-2, 0,300: maior DP depois | 0,11 | 0,11 | 0 |
| PS-1 e PS-2, 0,400 | logit não converge (separação, ver A1) | `SEM_ESTIMATIVA` | coincide |
| Holm (PS) e BKY | todos 1,000 | todos 1,000 | 0 |

A IC de permutação foi refeita com os mesmos 9.999 sorteios (semente 20261026) e com uma inversão por bisseção
própria.

## Fidelidade ao adendo

- **Conjuntos L, M e L+M**: são os do §2 (capital; quatro dummies de macrorregião com o Centro-Oeste de referência;
  log da população de 2022; médicos 2251/2252/2253, especialistas nas CBO-alvo no município e no resto da região de
  saúde, por 10 mil hab., média de 2024-06 a 2025-06). L-UF entra só na sensibilidade CL-2.
- **"Médicos" em vínculos** (decisão 1): o adendo não fixava vínculo ou pessoa. A escolha segue o B1 e o F3.1 e é
  relatada nos limites. Não mudou o adendo. A soma dos grupos `alvo_pmme`, `generalistas` e
  `especialistas_nao_alvo` cobre exatamente as três famílias, sem a 2231, como o adendo pede.
- **Especificação à CCFT**: a covariável é linear, com o mesmo coeficiente dos dois lados e dos ciclos. O controle
  das vagas imediatas da HI-2 tem um coeficiente por ciclo, como no 48b. Conferido na minha regressão.
- **Logit com os três ciclos juntos** (decisão 13): as covariáveis são fixas por município, então juntar os ciclos
  só pesa cada município pelo número de ciclos em que aparece. O pareamento é exato no ciclo, como manda a §3.2. Não
  mudou o adendo.
- **Suporte mínimo–máximo** (decisão 14): a §3.2 pede relatar a fração descartada e não fixa a regra. A regra
  usada é padrão. Não mudou o adendo.
- **Não convergência ou separação** (decisão 13): ver A3. Preenche uma lacuna e foi feita antes das contas, mas vai
  contra o espírito da §3.2.
- **Guloso global** (decisão 11): ver A4. Desvia da letra da §3.1, mas a conclusão não muda.
- **Malha → CIR** (decisão 5 revista): ver A5. Troca de fonte necessária; o conceito ("região de saúde") é o mesmo.
- **Holm nas PS e BKY nas secundárias, leitura pré-registrada**: as famílias estão certas (A6). Os códigos da
  leitura seguem as regras 22 a 25 (A7).
- **Ordem no Git**: adendo `148479c` (16:08) → nota §3.2 `ff62365` (16:10) → decisões `05830ac` (16:14) →
  protocolo 64 executado `93c76c7` (16:20, outro worktree) → 48d executado `362e830` (16:36). As 25 decisões são
  anteriores às estimativas que afetam. As revisões das decisões 5 e 21 não têm data verificável (A5).

## Portões

- **HI-1 e HI-2 do 48b** nos dois cortes: reproduzidos pelo script (≤ 1e−16) e por mim (ver tabela).
- **OC-A1 do protocolo 64** em V, 0,300: reproduzido pelo script e por mim. A amostra V (1.037 municípios, 2
  excluídos) também bate.

## Integridade

- **IVS errado:** o script 44 roda sob um *audit hook* que registra cada arquivo aberto. `data/ivs_ipea_2010_municipios.csv`
  não é aberto, nem a malha de regiões. A running variable é o a08.
- **Competências:** o a09 do pré vai de 202406 a 202506 e o do pós de 202510 a 202608. O script falha se aparecer
  competência ≥ 202609; o meu recálculo também conferiu.
- **`natureza_dos_dados = EMPIRICO`** em todas as linhas de `CL_estimativas.csv` (120) e `CL_balanco.csv`, e no
  resumo.
- **Nada imputado:** variável ausente fica ausente (3 municípios sem o resto da região; 192 células dos cursos 17 a 20
  sem M), e a unidade sai das linhas que usam a variável, com contagem.
- **`HI_*`, `HC_*` e `OC_*` intactos:** SHA-256 iguais antes e depois das duas reexecuções.
- **Determinismo:** a reexecução do script na base auditada deu saídas, figuras e doc 57r iguais byte a byte (árvore
  limpa no Git). Depois das correções, duas execuções seguidas deram saídas idênticas.

## Texto do 57r

- **Linguagem causal:** não há. O texto fala em "pacote do corte", "não se detecta diferença" e "anda junto".
- **Números fora de bloco:** não há números com decimais fora dos blocos gerados (o teste confere). A nota da §7.1
  acrescentada pela auditoria também não tem números.
- **Limite da RDD em 0,300:** antes não estava explícito. Agora está, no bloco gerado (A2).
- **PSM em 0,400:** dizia que não há estimativa, mas o motivo estava incompleto. Agora o texto diz o motivo completo
  (A1), que o principal só informa 0,300 e que mudar a regra exige novo adendo.
- **Clareza:** os códigos (`ANDA_JUNTO_…`, `RELATAR_COMO_ESTA`) agora vêm acompanhados da explicação em linguagem
  simples. "Randomização local condicional" aparece explicada como "como sorteado".

## Correções feitas nesta auditoria

| Arquivo | Mudança | Número mudou? |
|---|---|---|
| `scripts/rdd_bolsa/44_controles_localizacao_medicos.py` | diagnóstico de separação passa a contar todas as macrorregiões (inclusive a de referência) e os municípios distintos; frase da separação; parágrafo gerado "limite da RDD"; frase sobre o que falta em 0,400; figura do escore com uma categoria por linha | não (estimativas e balanço iguais byte a byte) |
| `output/rdd_bolsa/CL_resumo.json`, `CL_figuras/CL_escore.png` | regravados pelo script com o diagnóstico completo | não |
| `docs/06_execucao/57r_…md` | blocos regravados; cabeçalho da auditoria; §7.1 com as notas da auditoria | não |
| `docs/06_execucao/63_registro_explicacoes_e_controles_H1.md` | direção dos saltos e separação em 0,400 | não |
| `tests/test_controles_localizacao_medicos.py` | o cabeçalho do 57r passa a apontar a auditoria 40 | — |

Testes rodados: `test_controles_localizacao_medicos.py`, `test_pipeline_rdd_bolsa.py`, `test_h1_vagas_imediatas.py`
e `test_oferta_local_corte.py`, com 88 testes, todos OK.

## Proposta para o PSM em 0,400 (decisão do autor; exige novo adendo antes de olhar outcome)

Em 0,400 não há capital do lado de cima, e o mesmo vale para o Sul e, na H1, para o Centro-Oeste. Opções:

1. **Restringir antes do logit às categorias presentes dos dois lados** (tirar capitais, Sul e, na H1,
   Centro-Oeste), relatando quem saiu. O estimando passa a ser "municípios não capitais do Norte, Nordeste e
   Sudeste perto de 0,400". Testei só a convergência, sem olhar outcome: o logit converge assim na H1 e em V.
2. **Pareamento exato em macrorregião e capital (como na §3.1) e logit só nas variáveis contínuas** dentro dos
   estratos com os dois lados. Fica coerente com o Mahalanobis.
3. **Logit penalizado (Firth)** com as mesmas variáveis. Tem estimativa finita, mas as unidades sem par do outro
   lado continuam sem comparação, e o ganho sobre a opção 1 é pequeno.

Seja qual for a escolha, ela deve ser congelada em adendo antes de qualquer outcome. A opção 1 é a mais próxima do
que a §3.2 já previa ("fora do suporte comum … com quem são: capitais, região").
