# 57u. O salto no corte muda conforme o estrato do IED da atenção primária muda ou não? (adendo 48g)

> **Data:** 26/10/2026.<br>
> **Adendo:** [`48g_adendo_heterogeneidade_porte_ied.md`](48g_adendo_heterogeneidade_porte_ied.md), congelado antes destas
> contas (commit `c87ed75`). SHA-256 do adendo em `adendo` de `PO_resumo.json`, conferido pelo script.<br>
> **Estatuto:** `ADENDO_48G_POS_RESULTADO`. A H1 só com vagas imediatas (48b, doc 57n), a oferta local no corte
> (protocolo 64, doc 57q) e os controles e pareamentos (48d, 48e) já tinham sido vistos; a divisão por porte, não.
> Toda linha de `PO_estimativas.csv` e `PO_contagens.csv` tem `natureza_dos_dados = EMPIRICO`.<br>
> **Auditoria:** pendente.<br>
> **Script:** `scripts/rdd_bolsa/47_heterogeneidade_porte_ied.py` (construtores dos scripts 40 e 43 e estimadores de
> `rdd_lib.py`, importados; a leitura de capitais e regiões vem do script 44). **Saídas:**
> `output/rdd_bolsa/PO_estimativas.csv`, `PO_contagens.csv`, `PO_resumo.json`, `PO_figuras/`. **Testes:**
> `tests/test_heterogeneidade_porte_ied.py`.<br>
> **Números:** nenhum é digitado. Os blocos entre marcadores `<!-- PO:... -->` são regravados das saídas por
> `47_heterogeneidade_porte_ied.py --atualizar-doc`; o teste confere que cada bloco é idêntico ao gerado.

**Contraste.** Em toda linha, o lado com bolsa maior (IVS acima do corte) é comparado com o lado com bolsa menor; o
próprio corte fica no lado de baixo. Em 0,300 a bolsa anunciada sobe de R$ 10 mil para R$ 15 mil e em 0,400 de
R$ 15 mil para R$ 20 mil, mas outras regras federais mudam nos mesmos cortes
([auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)). O que se mede é o **pacote do corte**, não o
incentivo de R$ 5 mil isolado, nem a participação no PMM-E, nem o Agora Tem Especialistas.

**A pergunta, em linguagem simples.** Uma das regras que mudam no corte é o estrato do IED, que define quanto o
Ministério repassa por equipe de saúde da família (R$ 2.000 por equipe por mês a cada degrau). Só que o estrato não muda
em todo município: depende também do porte (tamanho da população). A bolsa do PMM-E muda em todos. Então dá para
comparar o salto no corte entre os municípios em que o estrato muda e aqueles em que não muda. Se o salto só aparece
onde o estrato muda, o IED é um candidato a explicar o sinal; se aparece igual nos dois grupos, o IED não explica. Os
grupos diferem também em tamanho, capital e região, então a diferença entre eles é **descritiva**, não um efeito
causal do IED.

## 0. Decisões de implementação (26/10/2026, registradas antes de qualquer estimativa deste adendo)

O adendo deixa alguns pontos abertos. Em cada um, ficou a leitura mais próxima dos scripts 40 (H1 só com vagas
imediatas) e 43 (oferta local no corte). Estas decisões foram escritas e registradas em commit antes de rodar qualquer
conta do adendo, inclusive o portão. Antes de escrevê-las, foi olhada só uma contagem de desenho, sem outcome: quantos
municípios com célula no quadro ficam em cada porte, lado e ciclo na janela de 0,050, para saber se cada grupo × ciclo
tem suporte para ter retas próprias. Nenhuma decisão depende de resultado.

**Grupo G (o estrato do IED muda ou não no corte)**

1. **Regra lida, não digitada.** Para cada corte, o script lê `output/aquisicao/a10_diagnostico_cortes_normas.json`:
   - o **código de IVS de baixo** é o código cuja faixa do IVS oficial (`faixa_ivs_oficial_por_codigo`, mínimo e
     máximo) contém o corte (o corte fica no lado de baixo, como na `rdd_lib`);
   - o **código de IVS de cima** é o código cuja faixa começa no menor mínimo acima do corte;
   - o estrato de cada código × porte vem de `estrato_ied_por_codigo_ivs_e_porte` (o script exige um só estrato
     observado em cada combinação e `regra_deterministica = true`);
   - **G = 1** no porte em que o estrato do código de baixo difere do estrato do código de cima; **G = 0** no porte em
     que é igual.
   O conjunto de portes com G = 1 não é digitado no script; o teste confere que ele bate com o texto do adendo.
2. **Conferência com a tabela do a10.** O script confere, para cada município de `a10_ied_aps_2024_municipio.csv`, que o
   estrato gravado é o da regra código × porte do JSON, e que o SHA-256 do CSV é o registrado em `saidas` do JSON.
   Para cada município na janela de cada corte, confere ainda que o código de IVS do Anexo VI é o código de baixo
   quando o IVS oficial (a08) é menor ou igual ao corte e o de cima quando é maior. Qualquer diferença para o script
   sem gravar nada.
3. **Porte.** `porte_codigo` do Anexo VI (IBGE 2022, pré-tratamento), pela chave `co_ibge` de 6 dígitos. Município da
   amostra sem linha ou sem porte no a10 sai, contado por outcome e corte.

**Amostras e outcomes (os mesmos das especificações de base)**

4. **HI-1 e HI-2.** As amostras do 48b montadas por `carregar()` do script 40, versão `13fev` (no ciclo 2, tipo de vaga
   pelo quadro de 13/02/2026, adendo 48b §7): HI-1 nas células com vaga imediata (só imediatas e mistas), ciclos 1–3;
   HI-2 nos municípios × ciclo com pelo menos uma dessas células. Outcomes `preenchida` e `aloc_imed`; controle de
   HI-2 `vi_imed`.
5. **ΔB1, ΔB2 e ΔB5.** A amostra V e os outcomes do protocolo 64 montados por `carregar()`, `taxa()` e `deltas()` do
   script 43 (por 10 mil hab., média do pós 2025-10 a 2026-08 menos a do pré 2024-06 a 2025-06). Município sem todos os
   meses de uma janela sai daquele outcome, contado, como no 43. Nenhuma competência do CNES ≥ 2026-09 é lida; o
   script confere a maior competência do painel usado.

**Especificação**

6. **HI-1 (PO-1).** `rdd_lib.rd_empilhado` com `grupo` = ciclo × G: intercepto, inclinação e inclinação acima do corte
   próprios em cada ciclo × G (a especificação de base já tem retas por ciclo; o adendo acrescenta retas por grupo).
   Salto comum T, que é o salto onde G = 0 (τ₀), mais a coluna T × G, cujo coeficiente é τ₁. Efeitos fixos de curso ×
   ciclo; EP agrupado por município (CR1); local linear, kernel triangular, h = 0,050; cada corte separado.
7. **HI-2 (PO-1).** O mesmo, com o controle do S-a do script 40: vagas imediatas das células com vaga imediata, linear,
   igual dos dois lados, **um coeficiente por ciclo** (não por ciclo × G, como na base), centrado como em
   `colunas_controle` do script 23. Uma linha por município × ciclo; CR1 por município.
8. **ΔB1, ΔB2, ΔB5 (PO-2 e PO-3).** `rd_empilhado` sobre ΔY com `grupo` = G (retas próprias por G e lado), T comum
   (τ₀) e T × G (τ₁); um município por linha, EP HC1, como o `rd_dird_delta` da base.
9. **Inferência.** τ₀ é o coeficiente de T, τ₁ o de T × G, e o salto onde o estrato muda é τ₀ + τ₁, com variância
   V(T) + V(T × G) + 2 Cov, da mesma matriz sanduíche. IC 95% e p pela normal, como na biblioteca.
10. **Sem estimativa.** Se a biblioteca descartar a coluna T × G por colinearidade, ou devolver NaN (menos de 2 mass
    points de algum lado em algum grupo), a linha fica `SEM_ESTIMATIVA`, com o motivo, contada. Não há especificação
    de reserva.
11. **Menos de 10 unidades.** A unidade é o **município distinto** (a unidade do cluster; é o que `n_abaixo` e
    `n_acima` contam no 48b e no 64), com peso de kernel positivo (−0,050 < IVS − corte < 0,050) e outcome (e
    controle) observados. Se algum G × lado tiver menos de 10, as linhas PO-1 a PO-4 desse outcome e corte ficam
    `SEM_ESTIMATIVA_MENOS_DE_10`, contadas. Na HI-1 as células também são contadas.

**Testes múltiplos**

12. **Holm** entre as 4 linhas τ₁ da PO-1 (HI-1 e HI-2 × dois cortes), com `rdd_lib.holm`. **BKY** entre as 6 linhas τ₁
    secundárias: PO-2 (ΔB1 e ΔB2 × dois cortes) e PO-3 (ΔB5 × dois cortes), com `rdd_lib.qvalores_bky`. O tamanho de
    cada família fica fixo: linha sem estimativa entra com p = 1 só no cálculo, e seu p ajustado fica vazio. A PO-4
    (τ₀ e τ₀ + τ₁) é descritiva, fora das duas famílias.

**Portão (antes de qualquer conta nova; falha fechada)**

13. Das amostras refeitas (decisões 4 e 5), o script reestima, com as funções de base (`est_celula` e `est_municipio`
    do script 40; `rd_dird_delta`), HI-1 e HI-2 em 0,300 e OC-A1 (ΔB1 em V) em 0,300, e compara com
    `HI_estimativas.csv` (variante `principal`) e `OC_estimativas.csv` (parte A, V, `principal`): |diferença| ≤ 1e−8 no
    salto e no EP, contagens iguais. Depois roda o estimador desta análise **sem a divisão por grupo** (grupo = ciclo,
    sem T × G; no OC, um grupo só) e exige o mesmo resultado. Junto vêm as conferências de G das decisões 1 e 2. Se algo
    não bater, o script para sem gravar.

**PO-5 (diagnóstico)**

14. **Contagens** por corte × G × lado na janela, para cada amostra de estimação: HI-1 (municípios e células), HI-2
    (municípios e linhas município × ciclo), ΔB1, ΔB2 e ΔB5 (municípios); e os municípios fora por falta de porte.
15. **Balanço de capital e região.** Na janela de cada corte, por G × lado: número de municípios, fração de capitais e
    fração em cada uma das cinco macrorregiões. Duas populações: "H1" (municípios distintos da amostra da HI-2, em
    qualquer ciclo) e "V" (municípios da amostra de ΔB1). Capital e região vêm da referência do IBGE gravada
    (`output/aquisicao/ibge_capitais_uf_regiao.csv`), lida por `ler_referencia_ibge` do script 44; a UF é o prefixo de
    2 dígitos do `co_ibge`. São médias simples, sem teste: descrevem quem está em cada grupo.

**Leitura (§4 do adendo, regra fixada no código)**

16. **PO-1.** `TAU1_TODOS_CONTEM_ZERO` se as 4 linhas τ₁ têm IC 95% que contém zero; `TAU1_REJEITA_HOLM_CONCENTRADO` se
    alguma τ₁ tem p de Holm < 0,05 e, nessa linha, o IC de τ₀ + τ₁ (estrato muda) exclui zero e o de τ₀ (não muda)
    contém zero; `TAU1_REJEITA_HOLM_SEM_CONCENTRACAO` se rejeita depois do Holm sem essa concentração;
    `TAU1_IC_EXCLUI_ZERO_SEM_HOLM` se algum IC convencional de τ₁ exclui zero, mas nenhum p de Holm fica abaixo de
    0,05 (relatado como sinal sem correção, entre os dois casos do adendo). Linhas sem estimativa são listadas.
17. **PO-3, por corte.** `INDICIO_IED_MOVE_APS` se o IC do salto de generalistas onde o estrato muda (τ₀ + τ₁) exclui
    zero e o IC onde não muda (τ₀) contém zero; senão `SEM_INDICIO`. O τ₁ e seu q BKY vêm junto, para dizer se a
    diferença entre os grupos também se distingue de zero.
18. **Potência.** Todo G × lado com menos de 10 municípios é listado como "sem potência para esse grupo". As contagens
    vêm sempre junto com a leitura.

**Saídas e figura**

19. Sem sensibilidades além do adendo (o adendo não pede outras janelas nem IC honesto). Uma figura,
    `PO_figuras/PO_salto_por_grupo.png`: um painel por outcome, e em cada corte o salto onde o estrato não muda (τ₀),
    onde muda (τ₀ + τ₁) e a diferença (τ₁), com IC 95% e "Como ler". Nenhuma saída `HI_*`, `OC_*`, `CL_*` ou `PM_*` é
    regravada.

## 1. Resposta curta

<!-- PO:resposta_curta:inicio -->
(gerado pelo script)
<!-- PO:resposta_curta:fim -->

### 1.1 Portão

<!-- PO:portao:inicio -->
(gerado pelo script)
<!-- PO:portao:fim -->

## 2. Onde o estrato muda (regra lida do a10)

<!-- PO:regra_g:inicio -->
(gerado pelo script)
<!-- PO:regra_g:fim -->

## 3. Contagens por grupo, lado e corte (PO-5)

<!-- PO:contagens:inicio -->
(gerado pelo script)
<!-- PO:contagens:fim -->

## 4. PO-1 — a H1 depende de o estrato mudar? (primária, Holm)

<!-- PO:po1:inicio -->
(gerado pelo script)
<!-- PO:po1:fim -->

## 5. PO-2 e PO-3 — oferta local de especialistas e de generalistas (secundárias, BKY)

<!-- PO:po2_po3:inicio -->
(gerado pelo script)
<!-- PO:po2_po3:fim -->

## 6. PO-4 — o salto em cada grupo (descritivo)

<!-- PO:po4:inicio -->
(gerado pelo script)
<!-- PO:po4:fim -->

## 7. PO-5 — quem está em cada grupo: capital e região (diagnóstico)

<!-- PO:balanco:inicio -->
(gerado pelo script)
<!-- PO:balanco:fim -->

## 8. Leitura pela regra pré-registrada

<!-- PO:leitura:inicio -->
(gerado pelo script)
<!-- PO:leitura:fim -->

## 9. Figura

<!-- PO:figura:inicio -->
(gerado pelo script)
<!-- PO:figura:fim -->

## 10. Limites

<!-- PO:limites:inicio -->
(gerado pelo script)
<!-- PO:limites:fim -->
