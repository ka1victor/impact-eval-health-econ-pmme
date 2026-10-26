# 57r. H1 e oferta local no corte com controles de localização e de médicos na região, e pareamento (adendo 48d)

> **Data:** 26/10/2026.<br>
> **Adendo:** [`48d_adendo_controles_localizacao_e_medicos.md`](48d_adendo_controles_localizacao_e_medicos.md),
> congelado antes destas contas (commit `148479c`), com a nota §3.2 (commit `ff62365`: o pareamento por escore de
> propensão passa a ser o principal). SHA-256 do adendo em `adendo` de `CL_resumo.json`, conferido pelo script.<br>
> **Estatuto:** `ADENDO_48D_POS_RESULTADO` para a H1 (os saltos da H1 já tinham sido vistos, inclusive com capital e
> UF, no adendo 48c). Para a oferta local (protocolo 64) é pré-resultado. Toda linha de `CL_estimativas.csv` e
> `CL_balanco.csv` tem `natureza_dos_dados = EMPIRICO`.<br>
> **Auditoria:** pendente.<br>
> **Script:** `scripts/rdd_bolsa/44_controles_localizacao_medicos.py` (estimadores de `rdd_lib.py` e funções dos
> scripts 23, 37 e 40, importadas). **Saídas:** `output/rdd_bolsa/CL_estimativas.csv`, `CL_balanco.csv`,
> `CL_resumo.json`, `CL_figuras/`. **Testes:** `tests/test_controles_localizacao_medicos.py`.<br>
> **Números:** nenhum é digitado. Os blocos entre marcadores `<!-- CL:... -->` são regravados das saídas por
> `44_controles_localizacao_medicos.py --atualizar-doc`; o teste confere que cada bloco é idêntico ao gerado.

**Contraste.** Em toda linha, o lado com bolsa maior (IVS acima do corte) é comparado com o lado com bolsa menor; o
próprio corte fica no lado de baixo. Em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil e em 0,400 de
R$ 15 mil para R$ 20 mil, mas outras regras federais mudam nos mesmos cortes
([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)). O que se mede é o **pacote do corte**, não o
incentivo de R$ 5 mil isolado, nem a participação no PMM-E, nem o Agora Tem Especialistas. Este adendo é robustez:
o principal da H1 continua o 48b, e o da oferta local continua o protocolo 64 sem controle.

## 0. Decisões de implementação (26/10/2026, registradas antes de qualquer estimativa deste adendo)

O adendo deixa alguns pontos abertos. Em cada um, ficou a leitura mais próxima dos scripts 40 (H1) e 37 (oferta
local). Estas decisões foram escritas antes de rodar qualquer conta nova do adendo. Nenhuma depende de resultado.

**Variáveis**

1. **"Médicos" é número de vínculos.** O a09 conta vínculos (`n_vinculos`) e profissionais distintos. Os outcomes B1
   do script 37 e F3.1 do E7 usam vínculos. Aqui também. Profissionais distintos não podem ser somados entre grupos
   de CBO (a mesma pessoa conta duas vezes).
2. **Médicos (todos) = CBO 2251, 2252 e 2253.** O grupo `todos_medicos` do a09 inclui a família 2231 (residentes e
   códigos antigos), que o adendo não pede. Por isso, médicos = soma dos grupos `alvo_pmme`, `generalistas` e
   `especialistas_nao_alvo`, que são disjuntos e cobrem exatamente 2251, 2252 e 2253 (definição do manifesto a09). O
   script confere que essa soma não passa de `todos_medicos` em nenhum município e mês.
3. **Média do pré.** Média mensal de 2024-06 a 2025-06 (13 competências), dividida pela população do Censo 2022 e
   multiplicada por 10 mil. Município sem alguma das 13 competências, ou sem população > 0, fica ausente naquela
   variável (contado), como em `diferenca_pos_pre` do E7.
4. **Especialistas do curso, na célula (HI-1).** CBO do curso pela ponte do manifesto a09 (`cbo_para_cursos`), soma
   dos grupos `cbo_XXXXXX` dessas CBO. Os cursos 17 a 20 do ciclo 3 não estão na ponte: nessas células as duas
   variáveis do curso ficam ausentes e a célula sai das linhas que usam M (contada), como no doc 57e. No município
   (HI-2, pareamento e protocolo 64), especialistas = grupo `alvo_pmme` (todas as CBO-alvo), como manda o adendo.
5. **Resto da região de saúde.** Região = UF + nome da região de saúde da malha (`sg_uf|no_regiao_saude`, como nos
   scripts 19 e das figuras da banca 2). Taxa = vínculos dos outros municípios da região ÷ população deles × 10 mil.
   Região com um município só: o resto não existe, a variável fica ausente (contada). Se algum outro município da
   região não tiver a média do pré, a variável do resto fica ausente. Da malha só se leem código, UF e região de
   saúde; as colunas de IVS, IDHM e renda que ela traz não são lidas.
6. **Capital e macrorregião.** Da referência do IBGE gravada pelo 48c (`ibge_capitais_uf_regiao.csv`), com a
   conferência de SHA-256 e de 27 capitais da função `carregar_referencias` do script 41, importada. Macrorregião
   entra como quatro dummies (referência: Centro-Oeste). UF, na sensibilidade L-UF, como 26 dummies.
7. **Um coeficiente por covariável.** Cada covariável entra linear, com o mesmo coeficiente dos dois lados e em
   todos os ciclos empilhados, como a dummy de capital do script 41. O controle das vagas imediatas da HI-2 continua
   com um coeficiente por ciclo, como no 48b. Coluna sem variação na janela é descartada pela `rdd_lib` e registrada.
8. **Amostra comum.** As linhas com covariável usam só as unidades com todas as variáveis daquela linha. A
   "variação em relação ao sem controle" de cada linha compara com a mesma especificação sem covariável **na mesma
   amostra** daquela linha. A CL-4 é a sem controle na amostra de L+M.
9. **CL-0 (balanço).** Salto de cada variável no corte, sem controle: (a) na amostra da HI-2 (município × ciclo,
   ciclos empilhados, CR1 por município); (b) em V do protocolo 64 (um município por linha, HC1); (c) as duas do
   curso, na amostra da HI-1 (célula, CR1). Macrorregião: uma dummy por região. UF (27 níveis) não entra no balanço.

**Pareamento (CL-7 a CL-9, Mahalanobis; PS-1 a PS-4, escore de propensão)**

10. **Outcomes da H1 pareada,** por município × ciclo com pelo menos uma célula com vaga imediata (ciclo 2 pelo
    quadro de 13/02/2026): fração das células com vaga imediata preenchidas na 1ª chamada (média de `preenchida` do
    48b) e médicos alocados nessas células por vaga imediata (`aloc_imed / vi_imed`).
11. **Algoritmo 1:1 sem reposição:** guloso global, o par de menor distância primeiro; empates pela ordem do código
    IBGE (e do ciclo). Com essa regra, os pares não dependem de qual lado "procura"; o lado com menos unidades é
    registrado.
12. **Mahalanobis:** matriz de covariância das quatro variáveis contínuas (log da população e as três de M) na
    amostra da janela, os dois lados juntos, por corte (e por ciclo na H1). *Caliper* = 0,25 × desvio-padrão das
    distâncias de todos os pares admissíveis (mesmo estrato exato: macrorregião, capital e, na H1, ciclo).
13. **Escore de propensão:** logit por máxima verossimilhança (statsmodels) na amostra da janela de cada corte, com
    L+M; na H1, ajustado nas linhas município × ciclo dos três ciclos juntos e pareado dentro do ciclo. Coluna sem
    variação ou colinear é tirada antes do ajuste e registrada; separação perfeita ou falta de convergência é
    registrada e a linha fica sem estimativa. *Caliper* = 0,2 × desvio-padrão do logit do escore na amostra da
    janela (os dois lados).
14. **Suporte comum** (só no PSM): regra mínimo–máximo, escore entre o maior dos mínimos e o menor dos máximos dos
    dois lados. Quem fica fora é contado, com capitais e região.
15. **Balanço:** diferença padronizada = diferença de médias (acima − abaixo) ÷ desvio-padrão combinado
    √((s²_acima + s²_abaixo)/2) calculado **antes** do pareamento; o mesmo denominador é usado depois.
16. **Inferência pareada:** média das diferenças (acima − abaixo). Permutação de sinais dentro dos pares, 9.999
    sorteios, semente 20261026, p bicaudal = (1 + nº de |média*| ≥ |média|) ÷ 10.000; IC 95% por inversão desse
    teste (os mesmos sorteios, busca por bisseção). IC t pareado também relatado. O p usado no Holm e no BKY é o da
    permutação. Na H1, o mesmo município pode estar em pares de ciclos diferentes (limite registrado).
17. **IPW (PS-4):** pesos do ATT (1 acima; e/(1 − e) abaixo), escore aparado: unidades com escore fora de
    [0,05; 0,95] saem (contadas). Estimativa = diferença de médias ponderadas, por MQP de y em 1 e no lado, EP
    sanduíche (HC1 por município no protocolo 64; CR1 por município na H1), escore tratado como fixo.
18. **Mínimo de pares:** com menos de 2 pares, a linha fica `SEM_ESTIMATIVA`.

**Testes múltiplos e linhas pendentes**

19. **Holm** só nas principais da nota §3.2: PS-1 (dois outcomes × dois cortes) e PS-2 (ΔB1, ΔB2 × dois cortes).
    **BKY** nas secundárias: CL-1, CL-2, CL-3, CL-5, CL-6, CL-7 e CL-8. Fora das duas famílias: CL-0 (diagnóstico),
    CL-4 (referência), CL-9, PS-3 e PS-4 (sensibilidades).
20. **Oferta local pendente.** CL-5, CL-6, CL-8, a parte de oferta local do CL-9, PS-2 e a oferta local de PS-3 e
    PS-4 só rodam com as saídas `OC_*` do protocolo 64 presentes (flag `--so-oferta-local`), depois de reproduzir
    OC-A1 em 0,300 (≤ 1e−8). Sem elas, essas linhas ficam `PENDENTE_OC`, sem número, contadas. Enquanto houver
    linha pendente, o Holm das PS-1 e o BKY são **provisórios**: calculados com o tamanho da família completa, com
    as linhas pendentes contadas como p = 1; a flag `--so-oferta-local` refaz os dois com os p de verdade.
21. **ΔB da oferta local:** construção do script 37 importada (`ler_painel`, `contagem`, `horas_ligados`), em V
    (a amostra do doc 57k), ΔY = média de 2025-10 a 2026-08 − média de 2024-06 a 2025-06, com todas as competências
    de cada janela (`diferenca_pos_pre` com `exigir_completo`), como o E7.

**Regras de leitura fixadas no código (antes de ver resultado)**

22. **CL-0 com salto:** IC 95% da variável no corte não contém zero.
23. **Salto "parecido" ao sem controle:** a estimativa com L+M (CL-1) fica dentro do IC 95% da CL-4 e tem o mesmo
    sinal. **"IC menor":** IC da CL-1 mais estreito que o da CL-4. **"Leva para perto de zero":** IC da CL-1 contém
    zero e |CL-1| ≤ metade de |CL-4|.
24. **Pareado limpo:** todas as diferenças padronizadas depois do pareamento com |DP| ≤ 0,25.
25. **Pareado concorda com a RDD:** as duas com IC que contém zero, ou as duas com IC sem zero e o mesmo sinal.
    Compara-se PS-1 (e CL-7) com a HI-1/HI-2 sem controle (CL-4) e com L+M (CL-1), corte a corte.
