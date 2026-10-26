# 57s. Pareamento pela regra literal do 48d e PSM em 0,400 sem as categorias de um lado só (adendo 48e)

> **Data:** 26/10/2026.<br>
> **Adendo:** [`48e_adendo_pareamento_regra_literal_e_0400.md`](48e_adendo_pareamento_regra_literal_e_0400.md),
> congelado antes destas contas (commit `f97e1ca`). SHA-256 do adendo em `adendo` de `PM_resumo.json`, conferido pelo
> script.<br>
> **Estatuto:** `ADENDO_48E_POS_RESULTADO`. Os resultados do 48d (doc
> [57r](57r_resultados_controles_localizacao_medicos.md)) e a
> [auditoria 40](../auditorias/40_auditoria_controles_localizacao_medicos.md) já tinham sido vistos, inclusive o PSM em
> 0,300 refeito pela auditoria com o lado menor procurando par. Toda linha de `PM_estimativas.csv`, `PM_balanco.csv` e
> `PM_excluidos.csv` tem `natureza_dos_dados = EMPIRICO`.<br>
> **Auditoria:** pendente.<br>
> **Script:** `scripts/rdd_bolsa/45_pareamento_regra_literal.py` (importa o script 44; não o reescreve). **Saídas:**
> `output/rdd_bolsa/PM_estimativas.csv`, `PM_balanco.csv`, `PM_excluidos.csv`, `PM_resumo.json`, `PM_figuras/`.
> **Testes:** `tests/test_pareamento_regra_literal.py`.<br>
> **Números:** nenhum é digitado. Os blocos entre marcadores `<!-- PM:... -->` são regravados das saídas por
> `45_pareamento_regra_literal.py --atualizar-doc`; o teste confere que cada bloco é idêntico ao gerado.

**Contraste.** Em toda linha, o lado com bolsa maior (IVS acima do corte) é comparado com o lado com bolsa menor; o
próprio corte fica no lado de baixo. Em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil e em 0,400 de
R$ 15 mil para R$ 20 mil, mas outras regras federais mudam nos mesmos cortes
([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)). O que se mede é o **pacote do corte**, não o
incentivo de R$ 5 mil isolado, nem a participação no PMM-E, nem o Agora Tem Especialistas. Este adendo é robustez do
48d: o principal da H1 continua o 48b, e o da oferta local continua o protocolo 64 sem controle.

## 0. Decisões de implementação (26/10/2026, registradas antes de qualquer estimativa deste adendo)

O adendo segue o 48d (§3.1 e §3.2) e as 25 decisões da seção 0 do doc 57r, salvo onde o 48e muda. Nos pontos que o
48e deixa abertos, ficou a leitura mais próxima do script 44. Estas decisões foram escritas antes de rodar qualquer
conta nova do adendo. A composição das janelas por região e capital já era conhecida (`CL_resumo.json` e auditoria
40); nenhum outcome foi olhado para escrevê-las.

**Base e regra 2 (categorias de um lado só)**

1. **Bases.** As mesmas do 48d, montadas pelas funções do script 44, importadas: unidades município × ciclo da H1
   (`bases_h1`, com os outcomes da decisão 10 do 57r) e a amostra V do protocolo 64 com ΔB1–ΔB5 (`base_v` e
   `construir_delta_b`). Janela |IVS − corte| ≤ w pela função `_janela` do 44. Quem não tem alguma covariável de
   L+M sai primeiro, contado, como no 44; a regra 2 vem depois.
2. **Categorias da regra 2.** Capital (as duas categorias: capital e não capital) e cada uma das cinco
   macrorregiões, inclusive o Centro-Oeste (categoria de referência). Uma categoria é "de um lado só" quando tem pelo
   menos uma unidade na amostra e todas do mesmo lado do corte. A conferência é feita por corte, janela e amostra (H1
   ou oferta local). Na H1, com os três ciclos juntos, porque o logit junta os três ciclos (decisão 13 do 57r); não
   ciclo a ciclo. É o mesmo critério do diagnóstico de separação do 44 (`categorias_so_de_um_lado`).
3. **Uma passada só.** Saem de uma vez as unidades de todas as categorias de um lado só. A conferência não é
   repetida. Se, depois da saída, outra categoria ficar de um lado só, isso é registrado no resumo, o logit roda
   assim mesmo e, se não convergir ou separar, a linha fica sem estimativa (48e §1, item 2; decisão 13 do 57r).
4. **A regra 2 vale para toda a amostra do pareamento** de cada corte, janela e amostra: PSM, IPW e Mahalanobis
   (PM-1 a PM-7). No Mahalanobis, o pareamento exato em macrorregião e capital já deixava essas unidades sem par;
   tirá-las muda só a matriz de covariância da janela.
5. **Quem sai é listado** em `PM_excluidos.csv`, uma linha por unidade que saiu (município × ciclo na H1; município
   na oferta local), por amostra, corte e janela: código IBGE, nome do município (coluna `nome_municipio_uf` do a08),
   UF, ciclo, lado, categorias que o tiraram e IVS.
6. **"Mais de 25% de um lado"** (leitura do §3): o denominador é o número de unidades daquele lado na janela depois
   da saída por covariável ausente (a amostra em que a regra 2 se aplica), por amostra e corte, na janela de 0,050.
   A fração da janela de 0,020 é relatada, mas não entra na leitura.

**Regra literal de pareamento (regra 1)**

7. **Quem procura par.** Em cada corte e janela (e, na H1, em cada ciclo), contam-se as unidades de cada lado na
   amostra depois da saída por covariável ausente e da regra 2, antes do suporte comum (onde o 44 conta o
   `lado_com_menos_unidades`). O lado com menos unidades procura par. Empate: procura o lado de bolsa maior (acima).
8. **Ordem.** PSM: em ordem decrescente do escore (chance estimada de estar acima do corte); empate no escore pela
   ordem crescente do identificador (código IBGE e, na H1, ciclo). Mahalanobis: em ordem crescente do identificador
   (código IBGE e, na H1, ciclo; como os pares são formados dentro do ciclo, a ordem entre ciclos não muda nada).
9. **Escolha do par.** Cada unidade que procura fica com a unidade do outro lado mais próxima entre as ainda livres e
   admissíveis, sem reposição. Admissível é o que o 44 já define: no PSM, as duas no suporte comum, no mesmo ciclo
   na H1 e com |diferença no logit do escore| ≤ *caliper*; no Mahalanobis, mesmo estrato exato (macrorregião,
   capital e, na H1, ciclo) e distância ≤ *caliper*. Empate na distância: a de menor identificador. Sem candidata
   livre, fica sem par (contada). Não há segunda passada.
10. **Implementação.** Distâncias, *caliper* e suporte vêm das funções `parear_psm` e `parear_mahalanobis` do 44, sem
    mudança. O script 45 troca só o último passo (`guloso_global`) pela regra literal durante a chamada e o devolve
    depois. Inferência, balanço, IPW e montagem das linhas são as do `pareamentos` do 44. A regra gulosa (PM-3) é o
    44 sem troca nenhuma.
11. **Escore, *caliper* e suporte** como nas decisões 13 e 14 do 57r, aplicados depois da regra 2: logit de
    P(acima | L+M) na amostra da regra 2; *caliper* = 0,2 × desvio-padrão do logit do escore nessa amostra; suporte
    mínimo–máximo nessa amostra.

**Linhas**

12. **PM-1:** fração de células com vaga imediata preenchidas e alocados por vaga imediata (município × ciclo,
    decisão 10 do 57r), por corte, janela 0,050. **PM-2:** ΔB1 e ΔB2, por corte, janela 0,050. São as oito linhas
    principais.
13. **Sensibilidades e secundária.** PM-3: as mesmas oito com a regra gulosa global (decisão 11 do 57r), com a
    regra 2. PM-4: as mesmas oito na janela de 0,020, regra literal, com a regra 2 refeita nessa janela. PM-5: IPW
    (decisão 17 do 57r) na amostra da regra 2, janela 0,050, os mesmos quatro outcomes × dois cortes. PM-6:
    Mahalanobis (decisão 12 do 57r) com a regra literal e a regra 2, janela 0,050, os mesmos quatro outcomes × dois
    cortes. PM-7: ΔB3, ΔB4 e ΔB5 por PSM, regra literal, regra 2, janela 0,050, por corte (seis linhas).
14. **Linha só para a figura (PM-F).** A figura principal pede, ao lado do 48d e do PM-1/PM-2, o PSM pela regra
    literal **sem** a regra 2. Ela é calculada com os mesmos quatro outcomes × dois cortes, janela 0,050, gravada em
    `PM_estimativas.csv` com papel `figura` e fica fora do Holm, do BKY e da leitura. Em 0,400, sem a regra 2, o
    logit separa como no 48d e a linha fica sem estimativa.

**Portão**

15. Antes de qualquer conta nova, o script refaz com as funções do 44, sem troca nenhuma, o PS-1 (dois outcomes) e o
    PS-2 (ΔB1 e ΔB2) em 0,300, janela 0,050, regra gulosa, sem a regra 2, e compara com `CL_estimativas.csv`:
    estimativa, p, IC de permutação e IC t com diferença ≤ 1e−8, e o número de pares igual (86 na H1; 88 no ΔB1 da
    oferta local; no ΔB2, 87, porque um par não tem o outcome). Confere também que os pares formados são os mesmos
    de `CL_resumo.json`. Se falhar, para sem gravar nada.
16. **Saídas de outros adendos.** O script grava o SHA-256 de cada arquivo `CL_*`, `HI_*` e `OC_*` antes de começar
    e confere de novo antes de gravar; se algum mudar, para sem gravar.

**Inferência e testes múltiplos**

17. **Inferência pareada** como na decisão 16 do 57r (permutação de sinais, 9.999 sorteios, semente 20261026; IC por
    inversão; IC t ao lado; o p do Holm e do BKY é o da permutação). IPW como na decisão 17. Menos de 2 pares: sem
    estimativa (decisão 18).
18. **Holm** nas oito linhas de PM-1 e PM-2, família de tamanho fixo: linha sem estimativa entra com p = 1 e fica
    sem p ajustado (resolve o achado 6 da auditoria 40). **BKY** nas 38 linhas de PM-3 a PM-7, do mesmo jeito. PM-F
    fica fora das duas famílias.
19. **Balanço** como na decisão 15 do 57r, na amostra que entrou no pareamento (depois da regra 2): diferença
    padronizada com o desvio-padrão combinado antes do pareamento. Variável sem variação na amostra (por exemplo,
    capital depois de tirar as capitais) tem diferença zero. **Comparação limpa:** todas as |DP| depois do
    pareamento ≤ 0,25 (decisão 24).

**Leitura do §3, fixada no código**

20. **`NAO_SE_DETECTA_DIFERENCA`** (1ª linha do §3): as oito linhas de PM-1 e PM-2 com estimativa, IC de permutação
    contendo zero e comparação limpa.
21. **`REJEITA_ZERO_DEPOIS_DO_HOLM`** (2ª linha), por linha principal com p de Holm < 0,05: relatar sinal e tamanho,
    o pacote do corte e quem saiu pela regra 2 naquele corte.
22. **`VALE_SO_PARA_PARTE_COMPARAVEL`** (3ª linha), por amostra e corte: a regra 2 tira mais de 25% de um lado na
    janela de 0,050 (decisão 6); o texto diz quais categorias saíram.
23. **`PONTO_DEPENDE_DA_REGRA`** (4ª linha), por linha principal: PM-3 e a linha correspondente de PM-1 ou PM-2 com
    estimativa, sinais opostos (os dois diferentes de zero) e os dois IC contendo zero.
24. Quando a 1ª linha não vale, o código diz por quê, linha a linha: `SEM_ESTIMATIVA`, `BALANCO_NAO_LIMPO` ou
    `IC_EXCLUI_ZERO_SEM_HOLM` (IC de permutação sem zero e p de Holm ≥ 0,05).
25. **Saídas.** Estatuto `ADENDO_48E_POS_RESULTADO` e `natureza_dos_dados = EMPIRICO` em toda saída; o script
    confere o SHA-256 do adendo 48e; nada é escrito em `data/`; o arquivo de IVS errado não é lido; nenhuma
    competência do CNES ≥ 202609 (conferências herdadas das funções do 44 e do 43).
