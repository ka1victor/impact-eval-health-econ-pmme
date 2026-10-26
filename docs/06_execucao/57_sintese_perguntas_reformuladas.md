# 57. Síntese das perguntas reformuladas (P1–P6, realocação e T1.6)

> **Data:** 24/10/2026.<br>
> **Plano:** [doc 51](51_plano_perguntas_reformuladas.md), §5 (onda 5). Formato e regra de Holm herdados da síntese anterior ([doc 44](44_sintese_rdd_bolsa_multioutcome.md)).<br>
> **Gerado por** `scripts/rdd_bolsa/33_sintese_perguntas.py`, que lê só de `output/`; não editar à mão. O teste `tests/test_sintese_perguntas.py` confere que este arquivo é igual ao gerado, que todo número volta a um arquivo de `output/` e que o Holm e o BKY batem com os p gravados.<br>
> **Saídas:** `output/rdd_bolsa/S57_resumo.json`, `S57_tabela_perguntas.csv`, `S57_multiplicidade.csv` e `S57_poder.csv`; natureza dos dados `EMPIRICO`.<br>
> **Estatuto:** síntese. Nada é estimado de novo. As únicas contas são o Holm e o BKY refeitos dos p gravados, o MDE como 2,8 × EP onde o bloco não gravou o MDE, a razão de chances por +R$ 5 mil a partir do coeficiente por R$ 1 mil e a passagem de fração para p.p.<br>
> **Hipótese central:** a escolha é do autor. A seção 7 traz uma proposta, rotulada como proposta; nada aqui a adota.

Todo resultado mede, no máximo, o **pacote do corte** (a bolsa anunciada +R$ 5 mil e as outras regras federais que mudam nos mesmos cortes de IVS, [auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)), o incentivo marginal dentro desse pacote (DiRD), a chegada do especialista sob tendências paralelas, o fato de ser alocado perto da nota de corte, ou é descritivo. Nenhum é efeito da participação no PMM-E nem do Agora Tem Especialistas.

## 1. Resposta curta

<!-- S57:resposta_curta:inicio -->
Nenhuma pergunta tem hoje evidência causal limpa de mudança no resultado medido. Nas cinco famílias de primárias com Holm definidas nos protocolos (40, 47, 48, 52 e 58), nenhuma linha rejeita zero; na família do relato do P6, só as 2 linhas do Y1 rejeitam, e o Y1 é quase mecânico (ser alocado cria o vínculo cadastrado no município da vaga).

**Pergunta central do autor: os R$ 5 mil a mais aumentam a atração ou o preenchimento?** Como pacote do corte, não se detecta aumento em nenhuma das duas margens, e os dados só descartam aumentos grandes em parte. Na célula aberta, com ciclos e cortes empilhados, o salto da probabilidade de preenchimento é −4,9 p.p. [−12,9; +3,2]: o maior aumento compatível com os dados é +3,2 p.p., e o desenho só detectaria com 80% de poder um salto de 11,5 p.p. Por corte, o limite superior é +1,7 p.p. em 0,300 e +11,3 p.p. em 0,400. Na atração, a probabilidade de a célula ter candidato de 1ª opção salta −7,1 p.p. [−19,6; +5,4]. Na escolha entre vagas já abertas, o coeficiente principal do P1 (M1) não se distingue de zero (razão de chances por +R$ 5 mil 1,24 [0,99; 1,55]); o sinal que resiste a vários testes continua só no ciclo 2 (E9: 1,95 [1,48; 2,57]), e escolha entre vagas não é preenchimento. A realocação entre concorrentes é inconclusiva, os cenários do T1.6 são simulação (validação de base aprovada na revalidação) e ficam só no documento dos cenários, sem entrar nesta síntese empírica.

Produção, horas e vínculos depois da chegada do especialista (P3 D2, P3x e P4) aparecem como associações sob tendências paralelas, com o pré falhando em parte das linhas; nos cortes (P3 D1), nada se distingue de zero. A abertura de vagas (P5) é descrita, não explicada: o IVS contínuo não se distingue de zero no pedido nem na priorização.
<!-- S57:resposta_curta:fim -->

## 2. Tabela por pergunta

**Como ler.** "Contraste identificado" diz o que a comparação mede no melhor caso. "Força da evidência" usa seis categorias fixas: causal-limpo; ATT sob tendências paralelas com pré falhando; exploratório; descritivo; inconclusivo; cenário (simulação). Nenhuma linha está hoje na primeira. "Inconclusivo" quer dizer que o desenho identifica o contraste, mas o IC contém zero: não é evidência de ausência.

<!-- S57:perguntas:inicio -->
| Pergunta | Estimando | Desenho | Unidade | Contraste identificado | Resultado principal [IC 95%] | Força da evidência | Doc e auditoria |
|---|---|---|---|---|---|---|---|
| P1 — quanto a bolsa move a escolha de onde trabalhar | peso da bolsa (por R$ 1 mil/mês) na escolha da 1ª opção entre as vagas abertas do curso e ciclo | logit condicional; IVS em spline contínua com nós em 0,300 e 0,400; distância e origem controladas (M1) | candidato × vaga do conjunto de escolha, ciclos 1–3 | pacote do corte | M1: +0,0424 [−0,0027; +0,0874] por R$ 1 mil (razão de chances por +R$ 5 mil 1,24 [0,99; 1,55]); p de Holm 0,065. Ciclo 2 (E9): 1,95 [1,48; 2,57] | inconclusivo | [57a](57a_resultados_P1_escolha.md); [aud. 26](../auditorias/26_auditoria_P1_escolha.md) |
| P2 — a bolsa maior preenche mais a vaga já aberta | salto, no corte, da probabilidade de a célula aberta ser preenchida na 1ª chamada; número de vagas preenchidas por município dado o número oferecido | RDD sharp local linear nos cortes de IVS; efeitos fixos de curso × ciclo e tipo de vaga (A3); controle pelas vagas oferecidas (N, S-a) | célula aberta (A3); município (N); ciclos 1–3 | pacote do corte | A3, empilhado: −4,9 p.p. [−12,9; +3,2]; N1: −0,76 [−1,44; −0,07] vagas por município, p de Holm 0,124 | inconclusivo | [49](49_resultados_contagem_vagas_preenchidas.md) §3 e §15; [aud. 20](../auditorias/20_auditoria_contagem_vagas_N.md), [aud. 22](../auditorias/22_auditoria_abertura_vagas_NA.md) |
| P3 (D1) — produção especializada nos cortes | salto, no corte, da mudança entre pré e pós da produção SUS (K1), das cirurgias (K2) e das consultas SUS + planos (K3) | DiRD local linear nos cortes (remove só a parte fixa no tempo das outras políticas) | município × mês (médias do pré e do pós), U | incentivo marginal | K1: +7,92 [−27,58; +43,42] por 10 mil hab./mês; K2: +0,42 [−0,58; +1,41]; K3: −1,85 [−22,90; +19,19]; p de Holm 1,000 nas três | inconclusivo | [50](50_resultados_producao_especializada.md); [aud. 21](../auditorias/21_auditoria_producao_K.md) |
| P3 (D2 e P3x) — produção depois da chegada do especialista | diferença média do pós na produção entre municípios (ou pares município × curso) que receberam o especialista e os que ainda não tinham recebido | Callaway–Sant'Anna; controles ainda não tratados; pré testado (Wald) | município × mês; município × curso × mês (12.2) | chegada do especialista | K1 (D2): +32,97 [−3,82; +69,75]; produção típica da especialidade (12.2): +14,34 [+3,08; +25,60], pré com p do Wald 0,040; K2 (D2): pré com p do Wald 0,028 | ATT sob tendências paralelas com pré falhando | [50](50_resultados_producao_especializada.md) §7, [57c](57c_resultados_P3_extensoes.md); [aud. 21](../auditorias/21_auditoria_producao_K.md), [aud. 25](../auditorias/25_auditoria_P3_extensoes.md) |
| P4 — oferta nova ou pagamento a quem já estava | variação das horas e vínculos cadastrados do médico associada à entrada no PMM-E | Callaway–Sant'Anna no médico (coortes de entrada); contabilidade pré × pós sem comparação | médico × mês, ciclos 1 e 2 | chegada do especialista | horas totais, média de θ(0..+6): +6,6 h/sem [+5,4; +7,8] (pré: p 0,310); no município do posto: +8,7 [+7,9; +9,5] (pré: p 0,001); já estavam no município: 51,0% [48,4; 53,7] | ATT sob tendências paralelas com pré falhando | [57d](57d_resultados_P4_trajetoria.md); [aud. 24](../auditorias/24_auditoria_P4_trajetoria.md) |
| P5 — onde o Ministério abre vagas | associação de características pré-determinadas com o pedido do gestor e a priorização da SGTES | logit descritivo com efeito fixo de curso (T5.1); RDD nos cortes do pedido e da priorização (T5.2) | célula do cardápio do ciclo 3; município nos ciclos 1–2 | descritivo | IVS contínuo no pedido: −1,8 p.p. por DP [−5,7; +2,1]; na priorização: +0,1 [−3,4; +3,5]; célula pedida no corte (T5.2a, empilhado): +14,7 p.p. [+1,8; +27,6], q BKY 0,602 | descritivo | [57e](57e_resultados_P5_abertura.md); [aud. 23](../auditorias/23_auditoria_P5_abertura.md) |
| P6 — alocado por pouco contra não alocado por pouco | diferença na trajetória cadastrada no CNES entre candidatos logo acima e logo abaixo da nota de corte da 1ª opção | comparação local na nota de corte com efeito fixo de célula; p por permutação; desempate por regra fixa, não sorteio | candidato de ampla concorrência, ciclos 1 e 2 | ser alocado | Y1 (vínculo no município da vaga, média): +0,405 [+0,210; +0,600], p de Holm 0,010 (quase mecânico); Y3 (horas totais, média): +15,5 [+0,6; +30,4], p de Holm 0,384 | exploratório | [57f](57f_resultados_P6_mecanismo.md); [aud. 27](../auditorias/27_auditoria_P6_mecanismo.md) |
| Realocação — a bolsa das concorrentes desloca candidatos | mudança no preenchimento e nos candidatos de 1ª opção da célula quando a bolsa média das concorrentes do mesmo curso e ciclo na região de saúde sobe | regressão na célula com o IVS próprio e o das concorrentes em spline contínua; cluster por região de saúde | célula aberta, ciclos 1–3 | pacote do corte | R-P1 por +R$ 5 mil: −4,9 p.p. [−14,3; +4,6], p de Holm 0,624, MDE 13,5 p.p.; R-P2: −0,075 [−0,553; +0,404], p de Holm 0,760 | inconclusivo | [57g](57g_resultados_realocacao.md); [aud. 28](../auditorias/28_auditoria_realocacao.md) |
| T1.6 — cenários de bolsa com o modelo de escolha | vagas preenchidas na 1ª chamada sob grades de bolsa alternativas, com candidatos e vagas fixos (cenário, não observação) | simulação com o M1 e o mecanismo de alocação do G2 | candidato × célula, 1ª chamada dos ciclos 1–3 | pacote do corte | validação de base aprovada em todas as linhas (revalidação com o desempate do adendo; a primeira tentativa falhou e está registrada no documento dos cenários); os números dos cenários são simulação e não são copiados para esta síntese | cenário (simulação) | [57b](57b_cenarios_P1_bolsa.md); sem auditoria própria |
<!-- S57:perguntas:fim -->

## 3. Holm nas primárias e BKY nas secundárias

Cada família é a que o protocolo do bloco definiu. Os p são os gravados nas saídas de cada bloco; o Holm e o BKY (Benjamini, Krieger e Yekutieli, grade de 0,001 de Anderson, 2008) foram refeitos aqui com código próprio e comparados com o que o bloco gravou. Fora destas famílias, nada tem correção: o D2 da família K, as leituras por ciclo da realocação e as linhas do adendo NA são relatados sem ajuste, como nos docs de origem.

### 3.1 Holm

O protocolo 56 (P6) pede BKY; o Holm do P6 foi pedido no relato e aparece como família à parte.

<!-- S57:holm:inicio -->
| Família (protocolo) | Linha | p gravado | p de Holm gravado | p de Holm recalculado | Diferença | Rejeita a 5%? |
|---|---|---|---|---|---|---|
| H40 (40): rodada multi-outcome: P1 (E6) e P2 (E7) | P1 índice de atração-presença (E6) | 0,426 | 0,851 | 0,851 | 0,000000 | não |
| H40 (40): rodada multi-outcome: P1 (E6) e P2 (E7) | P2 vínculos nas CBO-alvo por DiRD (E7) | 0,677 | 0,851 | 0,851 | 0,000000 | não |
| H47 (47): família K (D1): K1, K2 e K3, U, cortes empilhados | K1 | 0,662 | 1,000 | 1,000 | 0,000000 | não |
| H47 (47): família K (D1): K1, K2 e K3, U, cortes empilhados | K2 | 0,415 | 1,000 | 1,000 | 0,000000 | não |
| H47 (47): família K (D1): K1, K2 e K3, U, cortes empilhados | K3 | 0,863 | 1,000 | 1,000 | 0,000000 | não |
| H48 (48): família N: N1–N4 com controle das vagas oferecidas (S-a), empilhados | N1 | 0,031 | 0,124 | 0,124 | 0,000000 | não |
| H48 (48): família N: N1–N4 com controle das vagas oferecidas (S-a), empilhados | N2 | 0,078 | 0,235 | 0,235 | 0,000000 | não |
| H48 (48): família N: N1–N4 com controle das vagas oferecidas (S-a), empilhados | N3 | 0,188 | 0,376 | 0,376 | 0,000000 | não |
| H48 (48): família N: N1–N4 com controle das vagas oferecidas (S-a), empilhados | N4 | 0,717 | 0,717 | 0,717 | 0,000000 | não |
| H52 (52): P1a: coeficiente da bolsa no M1 (família de um teste) | M1 · bolsa_mil | 0,065 | 0,065 | 0,065 | 0,000000 | não |
| H58 (58): realocação: R-P1 e R-P2 na principal | R_P1 | 0,312 | 0,624 | 0,624 | 0,000000 | não |
| H58 (58): realocação: R-P1 e R-P2 na principal | R_P2 | 0,760 | 0,760 | 0,760 | 0,000000 | não |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y1_vinculo_mun_1a_opcao · ultimo | 0,001 | 0,010 | 0,010 | 0,000000 | sim |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y1_vinculo_mun_1a_opcao · media | 0,001 | 0,010 | 0,010 | 0,000000 | sim |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y2_horas_sus · ultimo | 0,293 | 0,855 | 0,855 | 0,000000 | não |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y2_horas_sus · media | 0,191 | 0,764 | 0,764 | 0,000000 | não |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y3_horas_totais · ultimo | 0,113 | 0,678 | 0,678 | 0,000000 | não |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y3_horas_totais · media | 0,048 | 0,384 | 0,384 | 0,000000 | não |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y4_vinculo_fora_origem · ultimo | 0,124 | 0,678 | 0,678 | 0,000000 | não |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y4_vinculo_fora_origem · media | 0,073 | 0,511 | 0,511 | 0,000000 | não |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y5_n_municipios · ultimo | 0,299 | 0,855 | 0,855 | 0,000000 | não |
| H56 (56, relato): P6: Y1–Y5 × último mês e média no R1 (Holm pedido no relato; o protocolo pede BKY) | y5_n_municipios · media | 0,285 | 0,855 | 0,855 | 0,000000 | não |
<!-- S57:holm:fim -->

### 3.2 BKY

<!-- S57:bky:inicio -->
| Família (protocolo) | Linhas | q < 0,05 gravado | q < 0,05 recalculado | Maior diferença de q |
|---|---|---|---|---|
| B40-F0 (40): E6, família F0 (implementação e seleção) | 42 | 0 | 0 | 0,0000 |
| B40-F1 (40): E6, família F1 (atração) | 45 | 0 | 0 | 0,0000 |
| B40-F2 (40): E6, família F2 (presença) | 24 | 0 | 0 | 0,0000 |
| B40-F4 (40): E6, família F4 (seleção de quem chega) | 24 | 0 | 0 | 0,0000 |
| B40-F3 (40): E7, família F3 (oferta no CNES) | 18 | 0 | 0 | 0,0000 |
| B47-K (47): K D1, secundárias | 13 | 0 | 0 | 0,0000 |
| B47-12 (47 §12): P3x, linhas principais do adendo | 8 | 0 | 0 | 0,0000 |
| B52 (52): P1, secundárias P1d–P1f | 12 | 6 | 6 | 0,0000 |
| B54-T41b (54): P4, T4.1b (regra D1) | 98 | 91 | 91 | 0,0000 |
| B54-T41c (54): P4, T4.1c (regra D1) | 196 | 172 | 172 | 0,0000 |
| B54-T41b-lit (54): P4, T4.1b (regra literal, sensibilidade) | 98 | 88 | 88 | 0,0000 |
| B54-T41c-lit (54): P4, T4.1c (regra literal, sensibilidade) | 196 | 172 | 172 | 0,0000 |
| B55 (55): P5, T5.2 (cortes, com e sem covariáveis) | 30 | 0 | 0 | 0,0000 |
| B56 (56): P6, Y1–Y5 no R1 | 10 | 2 | 2 | 0,0000 |
<!-- S57:bky:fim -->

### 3.3 Divergências

<!-- S57:divergencias:inicio -->
Nenhuma divergência: em todas as famílias, o Holm recalculado bate com o gravado dentro da tolerância e o BKY recalculado bate com o gravado dentro de um passo da grade, com a mesma decisão a 5% em toda linha.
<!-- S57:divergencias:fim -->

## 4. Poder e efeito mínimo detectável

**Como ler.** O limite superior do IC 95% é o maior valor que os dados ainda admitem, com o IC convencional e a aproximação local linear; quando a estimativa pontual é negativa, esse limite fica perto de zero mesmo com pouca precisão. O MDE de 80% é o menor salto que o desenho detectaria com 80% de poder num teste bilateral a 5% (cerca de 2,8 × EP): diz quanto o desenho enxerga, independentemente do sinal observado. Os dois números juntos dizem o que fica descartado e o que ainda passaria despercebido.

### 4.1 Primárias

<!-- S57:poder:inicio -->
| Primária | Contraste | Estimativa | IC 95% | Maior valor compatível (limite superior) | MDE 80% | Unidade | MDE |
|---|---|---|---|---|---|---|---|
| P1 índice de atração-presença (protocolo 40) | pacote do corte | −0,13 | [−0,44; +0,19] | +0,19 | 0,45 | desvios-padrão | 2,8 × EP (aqui) |
| P2 vínculos nas CBO-alvo, DiRD (protocolo 40) | incentivo marginal | +0,083 | [−0,309; +0,476] | +0,476 | 0,561 | vínculos por 10 mil hab. | 2,8 × EP (aqui) |
| K1 produção SUS das CBO-alvo (protocolo 47) | incentivo marginal | +7,92 | [−27,58; +43,42] | +43,42 | 50,72 | por 10 mil hab./mês | gravado pelo bloco |
| K2 cirurgias SUS (protocolo 47) | incentivo marginal | +0,42 | [−0,58; +1,41] | +1,41 | 1,43 | por 10 mil hab./mês | gravado pelo bloco |
| K3 consultas SUS + planos (protocolo 47) | incentivo marginal | −1,85 | [−22,90; +19,19] | +19,19 | 30,07 | por 10 mil hab./mês | gravado pelo bloco |
| N1 vagas preenchidas (protocolo 48) | pacote do corte | −0,76 | [−1,44; −0,07] | −0,07 | 0,98 | por município | gravado pelo bloco |
| N2 células com alocado (protocolo 48) | pacote do corte | −0,31 | [−0,66; +0,04] | +0,04 | 0,50 | por município | gravado pelo bloco |
| N3 células com alocado até a 2ª chamada (protocolo 48) | pacote do corte | −0,35 | [−0,87; +0,17] | +0,17 | 0,75 | por município | gravado pelo bloco |
| N4 especialistas ativos (protocolo 48) | pacote do corte | −0,21 | [−1,34; +0,92] | +0,92 | 1,61 | por município | gravado pelo bloco |
| P1a coeficiente da bolsa, M1 (protocolo 52) | pacote do corte | +0,0424 | [−0,0027; +0,0874] | +0,0874 | 0,0644 | log-chance por R$ 1 mil | 2,8 × EP (aqui) |
| P1a em razão de chances (protocolo 52) | pacote do corte | 1,24 | [0,99; 1,55] | 1,55 | 1,38 | razão de chances por +R$ 5 mil | exp(5 × 2,8 × EP) (aqui) |
| R-P1 célula preenchida (protocolo 58) | pacote do corte | −4,9 | [−14,3; +4,6] | +4,6 | 13,5 | p.p. por +R$ 5 mil das concorrentes | gravado pelo bloco |
| R-P2 candidatos de 1ª opção (protocolo 58) | pacote do corte | −0,075 | [−0,553; +0,404] | +0,404 | 0,684 | candidatos por +R$ 5 mil das concorrentes | gravado pelo bloco |
| Y1 vínculo no município da vaga, 202608 (protocolo 56) | ser alocado | +0,420 | [+0,215; +0,624] | +0,624 | 0,292 | fração | 2,8 × EP (aqui) |
| Y1 vínculo no município da vaga, média do seguimento (protocolo 56) | ser alocado | +0,405 | [+0,210; +0,600] | +0,600 | 0,279 | fração | 2,8 × EP (aqui) |
| Y2 horas SUS, 202608 (protocolo 56) | ser alocado | +8,6 | [−6,6; +23,7] | +23,7 | 21,6 | h/sem | 2,8 × EP (aqui) |
| Y2 horas SUS, média do seguimento (protocolo 56) | ser alocado | +10,5 | [−4,4; +25,3] | +25,3 | 21,2 | h/sem | 2,8 × EP (aqui) |
| Y3 horas totais, 202608 (protocolo 56) | ser alocado | +13,2 | [−3,1; +29,5] | +29,5 | 23,3 | h/sem | 2,8 × EP (aqui) |
| Y3 horas totais, média do seguimento (protocolo 56) | ser alocado | +15,5 | [+0,6; +30,4] | +30,4 | 21,3 | h/sem | 2,8 × EP (aqui) |
| Y4 vínculo fora da origem, 202608 (protocolo 56) | ser alocado | +0,202 | [−0,053; +0,457] | +0,457 | 0,364 | fração | 2,8 × EP (aqui) |
| Y4 vínculo fora da origem, média do seguimento (protocolo 56) | ser alocado | +0,207 | [−0,036; +0,450] | +0,450 | 0,347 | fração | 2,8 × EP (aqui) |
| Y5 número de municípios, 202608 (protocolo 56) | ser alocado | +0,446 | [−0,371; +1,264] | +1,264 | 1,168 | municípios | 2,8 × EP (aqui) |
| Y5 número de municípios, média do seguimento (protocolo 56) | ser alocado | +0,432 | [−0,350; +1,215] | +1,215 | 1,118 | municípios | 2,8 × EP (aqui) |
<!-- S57:poder:fim -->

### 4.2 A pergunta central: os R$ 5 mil a mais aumentam a atração ou o preenchimento?

Tudo abaixo é o **pacote do corte**: a bolsa anunciada maior junto com as outras regras federais nos mesmos cortes. O ciclo 1 aparece à parte porque nele a faixa saiu depois do pedido dos gestores.

<!-- S57:pergunta_central:inicio -->
**Preenchimento: probabilidade de a célula aberta ser preenchida na 1ª chamada (A3, p.p.)**

| Amostra e corte | Média abaixo do corte | Salto [IC 95%] | Maior aumento compatível | MDE 80% |
|---|---|---|---|---|
| ciclos 1–3, corte 0,300 | 33,3% | −8,4 [−18,5; +1,7] | +1,7 | 14,5 |
| ciclos 1–3, corte 0,400 | 36,8% | −1,3 [−14,0; +11,3] | +11,3 | 18,1 |
| ciclos 1–3, cortes empilhados | 34,7% | −4,9 [−12,9; +3,2] | +3,2 | 11,5 |
| ciclo 1, corte 0,300 | 26,0% | +0,9 [−23,5; +25,3] | +25,3 | 34,9 |
| ciclo 1, corte 0,400 | 37,2% | −12,4 [−37,5; +12,6] | +12,6 | 35,8 |
| ciclo 1, cortes empilhados | 31,2% | −3,3 [−20,9; +14,2] | +14,2 | 25,1 |

**Atração: probabilidade de a célula aberta ter candidato de 1ª opção (A3, p.p.)**

| Amostra e corte | Média abaixo do corte | Salto [IC 95%] | Maior aumento compatível | MDE 80% |
|---|---|---|---|---|
| ciclos 1–3, corte 0,300 | 48,3% | −10,8 [−28,2; +6,7] | +6,7 | 24,9 |
| ciclos 1–3, corte 0,400 | 49,6% | −2,7 [−19,7; +14,3] | +14,3 | 24,2 |
| ciclos 1–3, cortes empilhados | 48,8% | −7,1 [−19,6; +5,4] | +5,4 | 17,9 |
| ciclo 1, corte 0,300 | 36,5% | −10,6 [−31,6; +10,5] | +10,5 | 30,0 |
| ciclo 1, corte 0,400 | 38,5% | −6,5 [−32,4; +19,4] | +19,4 | 37,0 |
| ciclo 1, cortes empilhados | 37,4% | −6,5 [−22,7; +9,7] | +9,7 | 23,1 |

Candidatos de 1ª opção por célula (E6, F1.1, ciclos e cortes empilhados): +0,063 [−0,511; +0,636]; maior aumento compatível +0,636 candidato; MDE 80% 0,819 (2,8 × EP, aqui).

**Escolha entre vagas abertas (razão de chances por +R$ 5 mil)**

| Modelo | Razão de chances [IC 95%] | Maior valor compatível | Leitura |
|---|---|---|---|
| P1, M1 (ciclos 1–3, com distância; primária) | 1,24 [0,99; 1,55] | 1,55 | IC contém 1; MDE 80% em razão de chances 1,38 |
| P1, M5 (só o ciclo 2) | 1,70 [1,22; 2,37] | 2,37 | IC exclui 1; secundária |
| E9 (ciclo 2, sem distância) | 1,95 [1,48; 2,57] | 2,57 | IC exclui 1; exploratório |

**Realocação entre concorrentes (por +R$ 5 mil na bolsa média das concorrentes)**

- R-P1, célula preenchida: −4,9 p.p. [−14,3; +4,6]; MDE 13,5 p.p., acima do limiar do protocolo: inconclusivo.
- R-P2, candidatos de 1ª opção: −0,075 [−0,553; +0,404]; MDE 0,684, acima do limiar do protocolo: inconclusivo.

**T1.6 (cenários)**

- A primeira validação de base falhou (desempate por sorteio); depois do adendo datado com o desempate pela classificação publicada nos pares observados, a reconstrução sem mudança de bolsa reproduziu as vagas publicadas dentro da tolerância em todas as réplicas. Os cenários foram simulados e estão no documento dos cenários, rotulados como simulação; nenhum número simulado entra nesta síntese empírica.
- O modelo de escolha não responderia à margem extensiva: no logit condicional só diferenças de utilidade entre vagas contam, então somar o mesmo valor à bolsa de todas as vagas não muda nenhuma escolha com o grupo de candidatos fixo. Um aumento uniforme só poderia mover quem entra no programa, e isso o modelo não vê.
<!-- S57:pergunta_central:fim -->

## 5. Leitura em linguagem simples, pela cadeia

A ordem é a do `CLAUDE.md`: implementação → força de trabalho → capacidade → acesso → saúde → custos e bem-estar → equidade e spillovers. Em cada elo: o que se sabe, com que força e o que falta.

<!-- S57:cadeia:inicio -->
**Implementação (abertura de vagas).** O pedido do gestor e a priorização da SGTES andam junto com macrorregião, porte e capacidade instalada; o IVS contínuo não se distingue de zero no pedido (−1,8 p.p. por DP [−5,7; +2,1]) nem na priorização (+0,1 [−3,4; +3,5]). No corte, a célula pedida salta +14,7 p.p. [+1,8; +27,6], sem passar no BKY (q 0,602); a priorizada, −0,3 p.p. [−12,4; +11,8]. *Força:* descritivo, inconclusivo. *O que falta:* o critério oficial de priorização não é publicado; a abertura dos ciclos 1–2 só se vê no quadro final.

**Força de trabalho (escolha, alocação e entrada).** Na escolha entre vagas abertas, o M1 dá razão de chances por +R$ 5 mil de 1,24 [0,99; 1,55]; só o ciclo 2 tem IC que exclui 1 (E9: 1,95 [1,48; 2,57]). Ser alocado por pouco cria o vínculo cadastrado no município da vaga (+0,405 [+0,210; +0,600], quase mecânico); horas e permanência não se distinguem entre os lados. Dos médicos que entraram, 51,0% [48,4; 53,7] já tinham vínculo no município do posto antes do início (descritivo). *Força:* inconclusivo, exploratório. *O que falta:* o universo de inscritos e quem não se candidatou (margem extensiva, pedido externo); a remuneração paga; a replicação da escolha no ciclo 3.

**Capacidade (vínculos e horas).** Nos cortes, a DiRD dos vínculos nas CBO-alvo dá +0,083 [−0,309; +0,476] por 10 mil hab. (p de Holm 0,851). Entre médicos que entram em meses diferentes, as horas totais cadastradas sobem +6,6 h/sem [+5,4; +7,8] associadas à entrada (pré com p 0,310); as horas no município do posto, +8,7 [+7,9; +9,5], com o pré falhando (p 0,001); as horas fora dele, −2,1 [−3,2; −1,0]. Na contabilidade sem comparação, 26,3% [17,4; 35,4] do ganho no município do posto é compensado por perda fora dele (descritivo). Horas cadastradas não são horas trabalhadas. *Força:* inconclusivo, ATT sob tendências paralelas com pré falhando. *O que falta:* o CNES do ciclo 3 em 202703 (município–mês como teste de oferta líquida local); a presença real (folha de pagamento, pedido externo).

**Acesso (produção).** Nos cortes, K1 dá +7,92 [−27,58; +43,42] por 10 mil hab./mês, com MDE de 50,72 sobre uma média do pré de 288,29; K2 e K3 também têm IC que contém zero (p de Holm 1,000). Depois da chegada, K1 difere +32,97 [−3,82; +69,75]; a produção típica da especialidade que chegou, +14,34 [+3,08; +25,60], mas com o pré falhando (p 0,040); todas as internações dos residentes, +2,12 [+0,30; +3,94], com boa parte da diferença já presente antes da chegada (doc 57c). *Força:* inconclusivo, ATT sob tendências paralelas com pré falhando. *O que falta:* espera e fila (a regulação não é pública, pedido externo); meses maduros do SIA e do SIH; o ciclo 3.

**Saúde.** Nada foi medido. As internações dos residentes aproximam o uso, não o estado de saúde. *Força:* não medido. *O que falta:* horizonte longo; desfechos de saúde por residência depois da maturidade do ciclo 3.

**Custos e bem-estar.** Nada foi estimado de forma empírica. O custo da bolsa por vaga preenchida no T1.6 é aritmética simples sobre uma simulação, e não é custo observado. *Força:* não estimado (o custo do T1.6 é aritmética sobre simulação). *O que falta:* folha de pagamento (pedido externo); gasto do bolso não tem fonte municipal.

**Equidade e spillovers.** Nos outros municípios da região de saúde, a produção K1 difere +16,23 [+0,81; +31,66] depois da chegada, com o pré falhando (p 0,005): não separa atendimento de referência de deslocamento. A realocação entre concorrentes é inconclusiva (−4,9 p.p. [−14,3; +4,6]). Entre os médicos que mudaram, as horas cadastradas na origem variam −4,1 h/sem [−5,4; −2,7] (descritivo, sem comparação). *Força:* ATT sob tendências paralelas com pré falhando, inconclusivo, descritivo. *O que falta:* o universo de inscritos (para ver quem deixa de se candidatar onde); o ciclo 3 para replicar fora da amostra que gerou a hipótese.
<!-- S57:cadeia:fim -->

## 6. Lacunas e próximos passos

Nenhum item abaixo tinha sido executado em 24/10/2026. Custo e valor são juízos qualitativos desta síntese, para o autor decidir.

**Atualização de 25/10/2026.** Os dois itens do P3 e do P4 (sensibilidade de Rambachan e Roth e outro grupo de
comparação) rodaram sob o [protocolo 59](59_protocolo_P3P4_sensibilidade_comparacao.md), congelado antes de
estimar; resultados no [doc 57h](57h_resultados_P3P4_sensibilidade.md). As tabelas e o Holm desta síntese não
mudam.

| Item | O que resolveria | Custo | Valor | Quem decide |
|---|---|---|---|---|
| Pedido do universo de inscritos e do conjunto de escolha efetivo (pedido 2 em [`pedidos_dados/`](../pedidos_dados/README.md)) | a margem extensiva: se a bolsa traz candidatos novos ou só reordena quem já se candidatou; é a única forma de responder à atração no sentido de Dal Bó, Finan e Rossi | baixo para o projeto (ofício já redigido), alto em prazo (depende do Ministério) | alto: a pergunta central fica sem resposta sem ele | autor (envio do pedido) |
| Ciclo 3 em 202703 (seis meses só com a competência publicada, completa e madura) | replicação fora da amostra do sinal de escolha do ciclo 2; oferta líquida município–mês; mais células para o preenchimento | baixo (plano prospectivo congelado) | alto: é o único teste novo sem pedido externo | calendário (maturidade dos dados) |
| Auditoria independente dos cenários do T1.6 (revalidados em 25/10/2026, [doc 57b](57b_cenarios_P1_bolsa.md)) | se os cenários, agora com a validação de base aprovada, foram calculados como o protocolo diz | baixo a médio | médio: o modelo só redistribui entre células (candidatos e vagas fixos), não vê a margem extensiva e herda o IC largo do M1 | autor (pendente) |
| P3 e P4 com pré-tendências falhando: sensibilidade de Rambachan e Roth (HonestDiD) | quanto da diferença do pós sobrevive a violações de tendências paralelas do tamanho das vistas no pré (magnitude relativa M̄ ou suavidade) | baixo a médio (pós-resultado, rotulado como sensibilidade) | médio: diz se as associações de horas e produção são frágeis, sem criar identificação | autor (protocolo antes de rodar) |
| P3 e P4: outro grupo de comparação | células pedidas e não priorizadas (P5) ou candidatos não alocados por pouco (P6) como comparação da chegada e da trajetória; coortes do ciclo 3 como ainda não tratadas depois de 202703 | médio (protocolo novo, congelado antes de abrir) | médio a alto: a comparação pela priorização ou pela nota é menos dependente da escolha do candidato | autor (protocolo antes de rodar) |
| Folha de pagamento mensal (pedido 3) | se o anunciado é o recebido; presença efetiva em vez de vínculo cadastrado | baixo para o projeto, alto em prazo | médio | autor (envio do pedido) |
| Espera e fila (regulação) | o elo do acesso que a produção não mede | alto (fonte não pública) | alto para a política, baixo no curto prazo | autor (pedido externo) |

Sobre o P3 e o P4, as duas propostas acima são só propostas: escolher outro grupo de comparação ou outra
janela depois de ver o pré seria seleção retrospectiva, a menos que o protocolo fixe a regra antes de abrir os
outcomes. A sensibilidade de Rambachan e Roth não muda a estimativa; ela diz até onde a conclusão aguenta
uma tendência que o pré já mostrou.

## 7. Proposta ao autor sobre a hipótese central (PROPOSTA, não decisão)

> **Estatuto.** Nada aqui foi adotado. A escolha da hipótese central é do autor (doc 44, §7; doc 46; doc 51).

**Proposta.** Tratar como pergunta central a P1 (quanto a bolsa move a escolha entre vagas, relativa à distância
e à origem), com o preenchimento como teste de consistência, e não o contrário. Motivos:
- é a pergunta em que a bolsa age diretamente e em que o desenho compara vagas já abertas (doc 51, §1);
- é a única margem com sinal que resiste a vários testes, ainda que só no ciclo 2;
- o preenchimento, a presença e a oferta no CNES não se distinguem de zero com MDEs grandes, e o ciclo 3 é o
  próximo teste natural para as duas leituras.

**Alternativa.** Manter a hipótese original (H1 do doc 44: mais bolsa, mais preenchimento) e relatar o resultado como
inconclusivo, com os limites superiores e os MDEs da seção 4 por corte. A leitura correta, nos dois casos, é
"não se detecta, e os dados descartam só aumentos grandes", não "a bolsa é ineficaz".

**O que não muda em nenhum caso:** o contraste é o pacote do corte (ou o incentivo marginal na DiRD), não a
participação no PMM-E nem o Agora Tem Especialistas; os protocolos e os resultados dos blocos não são
reescritos; os pedidos externos e o ciclo 3 seguem como estão.

## 8. Proveniência

<!-- S57:entradas:inicio -->
| Entrada | SHA-256 (início) | Papel |
|---|---|---|
| `output/rdd_bolsa/E6_estimativas.csv` | `223b4c77326b8399…` | E6: P1 (primária do protocolo 40), F1.1 e F1.3 empilhados; BKY de F0, F1, F2 e F4 |
| `output/rdd_bolsa/E7_estimativas.csv` | `f6acdd7062cd0dad…` | E7: P2 (primária do protocolo 40), F3.1 por DiRD; BKY de F3 |
| `output/rdd_bolsa/E8_resumo.json` | `2a5a3eb7fc42eaa3…` | E8: p de Holm gravados de P1 e P2 (protocolo 40) |
| `output/rdd_bolsa/E9_efeitos_marginais.csv` | `812ac52a25cb2b86…` | E9: razão de chances por +R$ 5 mil no ciclo 2 |
| `output/rdd_bolsa/P1_estimativas.csv` | `8c4ca2e98b671709…` | P1 (protocolo 52): M1, M5, Holm de P1a e BKY de P1d–P1f |
| `output/rdd_bolsa/P1_resumo.json` | `bddaf9ef03a4374b…` | P1: estatuto |
| `output/rdd_bolsa/NA_estimativas.csv` | `9f737d4c2a2850dd…` | NA (adendo §7 do protocolo 48): A3 por célula aberta, por corte e ciclo |
| `output/rdd_bolsa/N_estimativas.csv` | `3490d69c568ed13e…` | N (protocolo 48): N1–N4 com Holm |
| `output/rdd_bolsa/K_D1_estimativas.csv` | `6d89726c7ad81029…` | K D1 (protocolo 47): K1–K3 com Holm; BKY das secundárias |
| `output/rdd_bolsa/K_D2_estimativas.csv` | `c3b62441a2345e48…` | K D2 (protocolo 47): chegada do especialista, ATT e pré-tendência |
| `output/rdd_bolsa/K_X_estimativas.csv` | `fd2e95f59185e245…` | P3x (adendo §12 do protocolo 47): 12.2, 12.4, 12.5 e BKY do adendo |
| `output/rdd_bolsa/P4_estimativas.csv` | `93f3e35bb21baced…` | P4 (protocolo 54): trajetória, origem, contabilidade líquida e BKY |
| `output/rdd_bolsa/P4_resumo.json` | `035e64a2ddad7e58…` | P4: estatuto |
| `output/rdd_bolsa/P5_estimativas.csv` | `f311e4c3908ef2a4…` | P5 (protocolo 55): associações do IVS, T5.2 e BKY |
| `output/rdd_bolsa/P5_resumo.json` | `36b70d8c8ffe5676…` | P5: estatuto |
| `output/rdd_bolsa/P6_estimativas.csv` | `275735381084d986…` | P6 (protocolo 56): R1, BKY e Holm da família de 10 testes |
| `output/rdd_bolsa/P6_resumo.json` | `87be1e524c9eecdb…` | P6: estatuto |
| `output/rdd_bolsa/R_estimativas.csv` | `9612da8684affe2d…` | realocação (protocolo 58): principal, Holm e MDE |
| `output/rdd_bolsa/R_resumo.json` | `b7bce621da60772c…` | realocação: leitura pré-registrada |
| `output/cenarios/P1_cenarios_resumo.json` | `444a4bf36df2cf07…` | T1.6: status da validação de base (só o status; nenhum número simulado é copiado) |
| `output/cenarios/P1_cenarios_validacao_base.csv` | `ec6e0749dd309da5…` | T1.6: linhas da validação de base (só o veredito por linha; B0 igual ao G2 principal) |
<!-- S57:entradas:fim -->

## 9. Reprodução

```bash
python3 scripts/rdd_bolsa/33_sintese_perguntas.py                  # saídas S57_* e este doc
python3 scripts/rdd_bolsa/33_sintese_perguntas.py --atualizar-doc  # só o doc, a partir do resumo
python3 -m pytest tests/test_sintese_perguntas.py
```
