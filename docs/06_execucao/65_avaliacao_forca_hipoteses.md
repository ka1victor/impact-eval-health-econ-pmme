# 65. Avaliação independente da força das hipóteses H1, H2 e H3 (banca 2)

> **Data:** 26/10/2026.<br>
> **Pedido:** dizer, com ceticismo, o que dá para afirmar em cada hipótese da apresentação, para o autor escolher
> **uma só** na versão final (banca 2, parte empírica, 28/10 e 04/11/2026). Regra do autor: plano A é a H1; se a
> H1 não se sustentar, H2; depois H3.<br>
> **Numeração da apresentação** ([doc 06 da banca 2](../07_apresentacoes/banca2/06_estrutura_obrigatoria_versao_final.md)):
> H1 preenchimento (RDD *sharp* em 0,300 e 0,400); H2 bolsa × origem (logit da 1ª opção; nos docs de análise é o
> "P1h" ou "H3"); H3 oferta (horas do médico e oferta local; nos docs de análise é o "P4", "parte B" ou "H4").<br>
> **Estatuto:** avaliação documental. **Nada foi estimado.** Todo número abaixo é copiado de um documento gerado
> por script a partir de `output/` (e conferido por teste contra `output/`), com doc e seção citados. Onde o número
> vem de auditoria, a auditoria é citada. Esta avaliação é opinião técnica; a escolha da hipótese é do autor.<br>
> **Contraste comum:** todo salto nos cortes de IVS mede o **pacote do corte** (bolsa +R$ 5 mil e outras regras
> federais nos mesmos cortes, [auditoria 18](../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)), nunca a
> participação no PMM-E nem o Agora Tem Especialistas.

> **Decisão do autor (27/10/2026) — vale sobre qualquer recomendação abaixo.** A hipótese única da versão final é
> a **H2** (bolsa × origem), reformulada no [doc 07 da banca 2](../07_apresentacoes/banca2/07_nova_hipotese.md); as
> antigas H1 e H3 vão para um apêndice curto. Análise completa da H2: [doc 66](66_analise_completa_H2.md) (auditoria
> 52). A recomendação da §0 e da §4.4 (H1) fica **superada** e é mantida só como registro do raciocínio; a §4.4
> ganhou uma nota que diz isso. Os três cuidados da nota da auditoria 50 abaixo continuam valendo para a H2.

> **Estado atual (nota da [auditoria 50](../auditorias/50_auditoria_avaliacao_hipoteses.md), 27/10/2026).**
> - **A seção mais recente é a §4.8.** Só ela conhece o 48h e o 52e. A §0 a §4.5 são de 26/10. A §4.6 e a §4.7
>   foram escritas em 27/10, antes desses adendos.
> - **As seções divergem na recomendação:**
>   - a §0 ("Veredito curto") e a §4.4 recomendam a **H1 como hipótese única**, e a §4.4 avisa que trocar para a H2
>     porque a H1 deu nulo é escolher a hipótese depois do resultado;
>   - a §4.7 propõe a **H2 como hipótese, com a H1 como fato que motiva**, que a §4.4 só admitia como plano B;
>   - a §4.8 diz que a H2 "ganha força".
>
>   Nenhuma seção revoga a outra, e a escolha é do autor.
> - **Valha qual valer, três cuidados:**
>   - **A H1 não é fato de nulo.** "Não encheu mais vagas" e "não quantas" (§4.7 e §4.8) contrariam a §1.6. A H1
>     não detecta aumento e, por corte, só detectaria saltos de 25 a 31 p.p. (no 48h, de 24 a 29 p.p.).
>   - **O 52e não testa a H2 como ela está definida aqui.** A H2 é D_UF, e o VL-1 não identifica D_UF. O 52e reforça
>     que o pacote do corte desloca a escolha. Isso fala de β > 0, que é outra afirmação. A primária pré-registrada
>     (P1a, quadro corrigido) continua sem rejeitar zero.
>   - **A queda em 0,300 não ficou "explicada pela UF".** Ela nunca passou no Holm, e capital, L+M e pareamento
>     também a mexem.
> - **A origem dos médicos (PH-5) não é ausência.** Se for citada, em 0,400 ela é inconclusiva, não ausência de
>   médicos de outra UF (auditoria 47, A3).
> - **A §0 e as notas da §4.6 e da §4.7 não incorporam o 48h e o 52e.**

## 0. Tabela-resumo

| | Estimando e contraste | Resultado principal | Força | Frase defensável |
|---|---|---|---|---|
| **H1** bolsa maior → mais vagas preenchidas | salto no corte (lado de bolsa maior − menor) na chance de a célula com vaga imediata ser preenchida (HI-1) e nos alocados por município (HI-2); **pacote do corte**, condicional a a célula ter vaga imediata | HI-1: −3,7 p.p. [−21,3; +13,9] em 0,300 e −2,3 p.p. [−24,0; +19,4] em 0,400; HI-2: −1,13 [−2,15; −0,10] (p 0,032; **Holm 0,126**) e −0,16 [−0,99; +0,68]. Nenhuma primária passa no Holm (57n §3) | **Inconclusiva.** Não sustenta o efeito positivo proposto. Não é nulo bem estimado: TOST inconclusivo em 3 das 4 primárias; MDE da HI-1 de 25 a 31 p.p. | "No corte de IVS, não detectamos aumento do preenchimento onde a bolsa é maior. Com o IC convencional, os dados descartam só aumentos grandes, e só em parte das medidas." |
| **H2** a bolsa pesa pouco perto da origem | no modelo de escolha da 1ª opção, D_UF = peso da vaga na UF de origem − peso de toda a amplitude da bolsa (R$ 10 → 20 mil); **comparação de pesos na utilidade**, condicional a se candidatar; a bolsa é identificada pelos cortes (pacote) e a origem é preferência revelada | D_UF = 1,98 [1,56; 2,40], p < 0,001, unilateral (57i §3); com o tipo de vaga do ciclo 2 corrigido, 1,94 [1,48; 2,40] (57p §1). O peso da bolsa sozinho não se distingue de zero: β = 0,0424 [−0,0027; 0,0874], p 0,065 (57a §4) [*auditoria 50, 27/10/2026: na versão corrigida, que é a de referência, β = 0,0453 [−0,0041; 0,0947], p de Holm 0,072 (57p §1)*] | **Moderada.** A desigualdade é forte e estável dentro do modelo, mas foi formulada depois de ver os coeficientes, e o lado da origem não é causal | "Entre quem se candidatou, toda a diferença de bolsa pesa na escolha bem menos que a vaga ficar na UF de origem do médico." |
| **H3** a chegada soma oferta ou remaneja | no médico: horas cadastradas associadas à entrada no PMM-E (Callaway–Sant'Anna, coortes de entrada); no município: oferta de especialistas depois da chegada (CS) e comparada no corte (forma reduzida); **associação sob tendências paralelas**, não efeito da bolsa | médico: +6,6 h/sem [+5,4; +7,8] (57d §5); 51,0% já tinham vínculo no município do posto (57d §3). Município, pela chegada: sobe, mas o pré já subia e a ruptura de Rambachan–Roth é 0 (57k §5.1); no corte: nada se distingue de zero, Holm 1,000 (57q §5.1) | **Fraca a moderada.** Moderada no nível do médico (associação); inconclusiva no município, que é onde a pergunta "soma ou remaneja" se responde | "O médico que entra passa a cadastrar mais horas, cerca de metade já estava no município e parte do ganho sai de horas que ele tinha fora; no município, não dá para afirmar aumento da oferta, nem há sinal de saída dos outros especialistas." |

> **Superado em 27/10/2026:** o autor escolheu a H2 (ver o topo do documento). O veredito abaixo é registro.

**Veredito curto (detalhe na seção 4).** Recomendo manter a **H1 como hipótese única**, apresentada como hipótese
testada e **não confirmada**, com o que os dados descartam e o que não descartam. Ela é a única das três derivada
antes dos resultados (modelo da banca 1) e a única com desenho de identificação do incentivo. Um resultado
inconclusivo não faz o desenho "não se sustentar". A H2 entra na Discussão como explicação, rotulada
pós-resultado. Trocar a hipótese central pela H2 *porque* a H1 deu nulo seria escolher a hipótese depois de ver o
resultado. A banca vê isso, e o próprio deck já marca a H2 como pós-resultado.

---

## 1. H1: bolsa maior leva a mais vagas preenchidas (RDD *sharp*)

### 1.1 Estimando e contraste

- **Estimando principal** (adendo [48b](48b_adendo_H1_vagas_imediatas.md) §2; resultados no [57n](57n_resultados_H1_vagas_imediatas.md)):
  - HI-1: salto no corte da chance de uma célula com vaga imediata ser preenchida na 1ª chamada (células, efeitos
    fixos de curso × ciclo);
  - HI-2: médicos alocados nessas células por município, controlando as vagas imediatas;
  - local linear, triangular, h = 0,050, cada corte separado, ciclos 1–3 empilhados, CR1 por município; Holm entre
    as quatro linhas.
- **Contraste:** pacote do corte. Em 0,300 muda também o teto de emendas e o custeio da APS e da MAC (+20%); em
  0,400, a ajuda de custo do PMMB e o incentivo de localidade da AgSUS; o cofinanciamento da APS (IED) muda nos dois
  cortes, conforme o porte (auditoria 18, resumo; [auditoria 35](../auditorias/35_incentivos_ligados_a_vulnerabilidade.md), §1).
  Nenhum outro incentivo **individual** ao especialista do PMM-E muda em 0,300 (auditoria 35, resposta curta). Por
  isso 0,300 é o corte mais próximo de "a bolsa como único incentivo pessoal", mas o pacote municipal continua.
- **Não é** o incentivo marginal isolado, nem participação no PMM-E. **É condicional:** à célula aberta e, na
  especificação principal, a a célula ter vaga imediata, um tipo que o Ministério decide (57n §6, "Controle de HI-2").

### 1.2 Identificação: premissas e aderência

| Premissa | O que foi testado | Resultado | Situação |
|---|---|---|---|
| Regra *sharp* | faixa reproduzida pelo IVS 2010 oficial | 368/368 municípios no ciclo 1 e 454/454 no ciclo 2 ([37](37_resultados_rdd_bolsa_ivs_oficial.md) §2); escore do MS = IVS oficial em 404/404 (`CLAUDE.md`; auditoria 16) | **cumprida** |
| Sem manipulação | IVS medido em 2010; densidade no ciclo 1 | razão de densidades 0,93 [0,40; 2,16] em 0,300 e 0,61 [0,29; 1,30] em 0,400 (37 §2) | **cumprida**; em 0,400, a razão abaixo de 1 com balanço ruim torna V1 suspeita ([44](44_sintese_rdd_bolsa_multioutcome.md) §5.4) |
| Continuidade / balanço pré-determinado | saltos de covariáveis na amostra da H1 | em 0,300, do lado de bolsa maior: capital −29,9 p.p. [−57,1; −2,8]; Nordeste −47,7 p.p. [−82,6; −12,8]; especialistas por 10 mil hab. no resto da região de saúde +10,54 [+3,54; +17,54]. Em 0,400, só os especialistas no resto da região: +6,21 [+0,71; +11,70] ([57r](57r_resultados_controles_localizacao_medicos.md) §3; [57o](57o_h1_capitais_uf.md) §3) | **falha em 0,300**; parcial em 0,400. É a ameaça mais séria da H1 (auditoria 40, A2) |
| Pacote do corte | levantamento normativo | várias regras federais mudam nos mesmos cortes (auditorias 18 e 35) | **não testável** com estes dados; define o estimando |
| Seleção pelo tipo de vaga (amostra só com vagas imediatas) | "ter vaga imediata" como outcome e limites de Lee | salto de S com IC que contém zero nos dois cortes; Lee contém zero: 0,300, Y1 [−7,4; +9,6] p.p., Y2 [−0,05; +0,12]; 0,400, Y1 [−13,0; +16,2], Y2 [−0,15; +0,16] ([57t](57t_resultados_selecao_tipo_vaga.md) §1) | **testada**, com ressalvas: monotonicidade por ciclo; o lado com mais vaga imediata troca de ciclo para ciclo em 0,300 ([auditoria 44](../auditorias/44_auditoria_selecao_tipo_vaga.md), A1); restringir a vagas imediatas piora o balanço em 0,300 (57t §1, SV-2) |
| Controle de HI-2 (vagas imediatas) pré-determinado | — | o quadro é decidido pela SGTES e pode responder ao corte ([48](48_protocolo_contagem_vagas_preenchidas.md) §2 e §8); no ciclo 1 a adesão dos gestores precedeu a faixa | **não testável** por inteiro; HI-s3 sem controle relatada |
| Forma local linear adequada | placebos de corte, IC honesto | no ciclo 2, um corte placebo entre 0,300 e 0,400 acusa salto (S-b −5,64 [−9,92; −1,37]; [49](49_resultados_contagem_vagas_preenchidas.md) §9); dentro da faixa de R$ 10 mil, perto do corte, o preenchimento sobe +36,1 p.p. por 0,100 de IVS [+7,4; +64,7] ([57m](57m_gradiente_faixas.md) §1), e a reta leva essa subida até o corte; o IC honesto é ilimitado na prática (57n §4, HI-s8) | **frágil em 0,300** |

O que **não** se testa: a exclusão do pacote (bolsa sozinha), a regra com que a SGTES monta o quadro e o tipo de
vaga, e se "alocado" é a mesma operação nos três ciclos (57n §6).

### 1.3 Resultado principal

| Linha (57n §3) | Corte | Salto | IC 95% | p | p Holm | Média abaixo | MDE (2,8 × EP) | TOST (57n §4, HI-s7) |
|---|---|---|---|---|---|---|---|---|
| HI-1 célula com vaga imediata preenchida | 0,300 | −3,7 p.p. | [−21,3; +13,9] | 0,682 | 1,000 | 56,1% | 25,1 p.p. | inconclusivo (IC 90% [−18,4; +11,1] contra ±10 p.p.) |
| HI-1 | 0,400 | −2,3 p.p. | [−24,0; +19,4] | 0,835 | 1,000 | 59,0% | 31,0 p.p. | inconclusivo |
| HI-2 alocados em vagas imediatas por município | 0,300 | −1,13 | [−2,15; −0,10] | 0,032 | 0,126 | 2,77 | 1,47 | descarta **aumento** ≥ 0,69; não descarta queda |
| HI-2 | 0,400 | −0,16 | [−0,99; +0,68] | 0,713 | 1,000 | 2,01 | 1,19 | inconclusivo |

- **Estatuto:** é **descrição do pacote do corte com a precisão relatada**, não efeito causal estabelecido. Também
  não é nulo bem estimado: nenhuma linha tem equivalência. Com o IC honesto, todas as linhas ficam inconclusivas,
  e as amplitudes chegam a centenas de p.p. (57n §4, HI-s8).
- **O caso intermediário** (HI-2 em 0,300: IC sem zero, mas sem rejeitar zero depois do Holm) não estava na leitura
  pré-registrada. A leitura veio do código, não do adendo ([auditoria 38](../auditorias/38_auditoria_h1_vagas_imediatas.md), achado 3).
- **Poder.** Por corte, a HI-1 só detectaria com 80% de poder saltos de 25 a 31 p.p. A referência da literatura no
  protocolo é +10 p.p. (doc 57j §1), e Dal Bó, Finan e Rossi acham +15 p.p. de aceitação (44 §6). **A especificação
  principal por corte não tem poder para a pergunta que faz.**
- **O que descarta aumento grande:** só as medidas antigas **empilhadas** (cortes e ciclos), com IC convencional.
  Na célula aberta (A3), IC 90% [−11,6; +1,9]: não houve aumento de 10 p.p. ou mais. Nos alocados (N1), IC 90%
  [−1,33; −0,18] contra ±0,54: o mesmo vale para +25% da média ([57j](57j_resultados_equivalencia_H1.md) §2.1).
  Com o IC honesto, nem isso se sustenta (57j §2.3). O autor decidiu não mostrar o empilhado (doc 05 da banca 2,
  §1). **Esse é o custo dessa decisão:** por corte, a HI-1 não descarta +10 p.p.

### 1.4 Robustez

| Especificação | Resultado (salto em 0,300; 0,400) | Muda a leitura? | Fonte |
|---|---|---|---|
| Medidas antigas (todas as células, A3; alocados com controle de imediatas + reserva, N1 S-a) | A3: −8,4 p.p. [−18,5; +1,7]; −1,3 [−14,0; +11,3]. N1: −1,45 [−2,67; −0,22]; −0,14 [−0,82; +0,54] | não: sinal negativo, nada passa no Holm | 57n §2.1; 49 §3 |
| Por ciclo (HI-s1) | HI-1 em 0,300: +0,8 / −21,0 / +7,2 p.p. nos ciclos 1 / 2 / 3; todos os IC contêm zero | o sinal muda de ciclo para ciclo | 57n §4 |
| Janelas h = 0,030 e 0,080 | HI-2 em 0,300: −0,50 [−1,67; +0,68] e −0,74 [−1,67; +0,20] | **sim:** o único IC sem zero (HI-2 em 0,300) não aguenta a troca de janela | 57n §4, HI-s8 |
| Sem controle (HI-s3) | HI-2: −2,76 [−5,00; −0,51] em 0,300; q BKY 0,819 | não | 57n §4 |
| Dummy de capital / efeito fixo de UF / sem capitais | HI-2 em 0,300: −0,83 [−1,87; +0,21] / −0,32 [−1,31; +0,66] / −0,30 [−1,22; +0,62]; HI-1: +2,6 / +4,0 / +2,9 p.p. | **sim:** o IC da HI-2 passa a conter zero; a HI-1 muda de sinal | 57o §1 |
| Localização e médicos na região na regressão (L+M) | HI-2 em 0,300: de −1,11 [−2,17; −0,05] para −0,25 [−1,37; +0,87]; HI-1: de −4,1 para +3,6 p.p. | **sim** | 57r §1 |
| Pareamento por escore de propensão, regra literal (PM-1) | fração preenchida: +4,7 p.p. [−6,5; +16,0] e +5,5 [−9,7; +20,7]; alocados por vaga imediata: +0,10 [−0,01; +0,22] (Holm 0,636) e +0,07 | **sim no sinal**; IC com zero; o ponto depende da regra de pareamento (gulosa: −0,6 p.p.) | [57s](57s_resultados_pareamento_regra_literal.md) §1; 57r §2.1 |
| Limites de Lee (tipo de vaga) | todos os intervalos contêm zero (tabela 1.2); com a reta, os alocados em 0,300 ficam em [−0,19; −0,01], mas o IC de Imbens–Manski contém zero | não | 57t §1 |
| Heterogeneidade pelo estrato da APS (IED) | diferença τ₁ na HI-2 em 0,300: +1,67 [−0,27; +3,60], Holm 0,366 | não (pouca potência) | [57u](57u_resultados_heterogeneidade_porte.md) §1 |
| Acaso (diagnóstico 61, medidas antigas) | células abertas, médias cruas da janela em 0,300: 33,3% preenchidas abaixo e 33,5% acima; o placebo do protocolo só alcança p ≥ 0,250 por construção | acaso nem descartado, nem confirmado | [57l](57l_diagnostico_queda_0300.md) §1 |

**O que se mantém:** nenhuma especificação mostra salto **positivo** que se distinga de zero. **O que muda:** o
sinal e a significância sem correção da queda em 0,300. Ela some com capital, UF, localização e médicos, ou com o
pareamento.

**Escolhas feitas depois de ver o resultado** (todas registradas como tal nos próprios docs):
1. O outcome mudou três vezes depois de olhar: F1.3 do protocolo 40 → contagem N (protocolo 48, "pós-resultado") →
   só vagas imediatas (48b, `ADENDO_48B_POS_RESULTADO`). A justificativa original do 48b ("a reserva não podia ser
   preenchida") caiu na auditoria 36 (auditoria 38, achado 1).
2. O quadro do ciclo 2 trocou para 13/02 depois de o executor ver a versão com 19/03. A troca **não** favoreceu o
   nulo: com 19/03, a HI-2 em 0,300 tinha IC com zero (auditoria 38, achado 2).
3. A leitura do caso "IC sem zero, Holm não rejeita" e a regra da HI-s6 ficaram fixadas no código, não no adendo
   (auditoria 38, achado 3).
4. Mostrar por corte, sem empilhado, foi decisão de apresentação tomada depois de ver que o empilhado misturava os
   dois cortes (49b §8; doc 05 da banca 2, §1).
5. Os adendos 48c a 48g e as margens do TOST (protocolo 60) vieram todos depois da H1.

O lado positivo é que nenhuma dessas escolhas fabricou um efeito positivo: todas levam a estimativa para perto de
zero ou a deixam negativa. O risco que fica é de **interpretação**: o deck explica um sinal negativo que não passa
no Holm e muda de sinal na robustez.

### 1.5 Ameaças que sobram e perguntas prováveis da banca

- **"Por que vocês trocaram o outcome três vezes?"** Resposta honesta: todas as versões dão a mesma conclusão (nada
  positivo detectado); a principal atual é pós-resultado.
- **"O balanço falha em 0,300. A RDD vale nesse corte?"** Só como comparação local com a ressalva. Capital,
  Nordeste e especialistas na região diferem no corte (57r §3), e a queda não se separa disso.
- **"Com MDE de 25 a 31 p.p., o que esse teste podia mostrar?"** Muito pouco por corte. É por isso que o empilhado
  e o TOST importam.
- **"Por que explicar um sinal que não passa no Holm e vira positivo no pareamento?"** O slide "Por que o sinal sai
  negativo" ([04 da banca 2](../07_apresentacoes/banca2/04_conteudo_deck_curto.md), Discussão) arrisca
  sobreinterpretar ruído.
- **"Isso é a bolsa ou o pacote?"** O pacote. Em 0,300 não muda nenhum outro incentivo individual (auditoria 35),
  mas mudam emendas e custeio MAC e APS (auditoria 18).
- **"O preenchimento é limitado por candidatos ou por vagas?"** No funil, a chance de a célula ter candidato de 1ª
  opção muda −10,8 p.p. [−28,2; +6,7] em 0,300 (57l §1), sem distinção de zero. O universo de inscritos não está
  nos dados (44 §7.3).

### 1.6 Frase honesta

**Dá para afirmar:** "Nos dois cortes de IVS, comparando vagas imediatas, não detectamos aumento do preenchimento do
lado de bolsa maior. Nenhuma das quatro linhas principais passa no Holm. Com o IC convencional, os dados descartam
aumento de 25% ou mais nos alocados em 0,300 (e, com os cortes empilhados, aumento de 10 p.p. na célula aberta).
Tudo isso vale para o pacote do corte."

**Não dá para afirmar:**
- que a bolsa não funciona ou que o efeito é zero (nada tem equivalência; o MDE é grande);
- que a bolsa reduz o preenchimento (Holm; o sinal muda com controles e pareamento);
- que se trata do efeito da bolsa isolada;
- que o desenho é limpo em 0,300 (balanço).

### 1.7 Nota: **inconclusiva**

A H1 é inconclusiva, não um nulo bem estimado. Ela não sustenta o efeito positivo proposto: nenhuma
especificação o mostra. Como nulo, informa só de um lado:
- descarta aumentos grandes em parte das medidas (empilhado; HI-2 em 0,300), com IC convencional;
- não descarta +10 p.p. por corte na especificação principal;
- não informa nada com o IC honesto.

O desenho é o melhor do projeto para a pergunta do incentivo: a regra é *sharp* e não há manipulação. A
identificação em 0,300 fica comprometida pelo balanço.

---

## 2. H2: a bolsa pesa pouco perto da origem do médico (logit condicional da 1ª opção)

### 2.1 Estimando e contraste

- **Estimando** ([52b](52b_protocolo_P1h_magnitudes.md) §3; [57i](57i_resultados_P1h_magnitudes.md) §1): D_UF =
  θ_UF − 10·β, no modelo M1, em log-chance. Teste unilateral de D_UF ≤ 0, família de um teste.
  - β é o peso da bolsa por R$ 1 mil na escolha da 1ª opção entre as vagas abertas do mesmo curso e ciclo.
  - θ_UF é o peso de a vaga ficar na UF de origem, fora da região de saúde de origem.
- **β:** identificado só pelos degraus da bolsa nos cortes, com o IVS em *spline* contínuo. É o pacote do corte
  ([42](42_resultados_E9_escolha.md) §1).
- **θ_UF:** **preferência revelada**, não efeito causal. A origem é o município do vínculo no CNES antes da inscrição,
  não a residência (57i §1; doc 05 da banca 2, §2.5).
- **Tipo de contraste:** comparação de dois pesos na mesma utilidade, condicional a se candidatar. Mede repartição
  de um conjunto dado de candidatos entre vagas, não preenchimento nem expansão (57a §1).

### 2.2 Identificação: premissas e aderência

| Premissa | Teste | Resultado | Situação |
|---|---|---|---|
| Nenhum outro atributo da célula que pese na escolha salta no corte (dado o *spline*) | auditoria 18 (normas); controles de capital, macrorregião e estrato; efeito fixo de UF (M4) | o +20% de MAC e emendas em 0,300 pode mudar o serviço, em sentido desconhecido (42 §1); o desequilíbrio de capitais em 0,300 está controlado por capital e macrorregião | **parcial**: mesma ameaça de pacote da H1 |
| Forma funcional do IVS | *spline* linear, quadrático e cúbico; janelas | no E9 empilhado, com *spline* cúbico, o IC inclui zero; o do ciclo 2 também (42 §5.2) | **frágil para β** |
| IIA | logit aninhado por região de saúde (M9) | λ = 0,449 [0,341; 0,556]; Wald de λ = 1: p < 0,001 (57a §8) | **violada em parte**; β quase não muda (M9: 0,0434) |
| Poucos *clusters* | 56 conjuntos de escolha; t com G − 1; *score bootstrap* | ciclo 2 robusto (42 §5.2; auditoria 41, A2) | ok para o ciclo 2 |
| Homogeneidade entre ciclos | β por ciclo; Wald | ciclo 1 +0,0132; ciclo 2 +0,1064 [+0,0405; +0,1722]; ciclo 3 −0,0004; Wald p 0,058 (57a §7) | o sinal de β vem do ciclo 2 |
| Conjunto de escolha completo; escolha não estratégica | — | não testável (42 §7) | aberto |
| Seleção pela ligação candidato–CNES | E9 na amostra completa | 5.421 de 5.714 candidatos ligados; β na amostra completa 0,0662 (57a §2 e §4) | pouco efeito |
| Tipo de vaga do ciclo 2 pré-alocação | adendos 52c e 52d | D_UF 1,98 → 1,94; β M1 0,0424 → 0,0453 (Holm 0,065 → 0,072) (57p §1) | **resolvido** nas principais; sensibilidades em [57v](57v_sensibilidades_ciclo2_quadro_1302.md), auditada na [auditoria 46](../auditorias/46_auditoria_sensibilidades_ciclo2.md) (*correção da auditoria 50, 27/10/2026; antes dizia "auditoria pendente"*) |

**Não testável:** se θ_UF reflete custo do lugar ou outras coisas que andam com a origem: registro no conselho,
família, rede, ou manter o emprego atual. As 20 h da bolsa são cumuláveis (doc 63 §3), e no doc 57d §5 o médico
perde só −2,1 h/sem fora do município do posto. Ficar perto da origem pode ser, em parte, renda alternativa, não
só "custo do lugar".

### 2.3 Resultado principal

| Linha | Estimativa | IC 95% | Inferência | Fonte |
|---|---|---|---|---|
| P1h-1: D_UF (M1, ciclos 1–3) | 1,98 | [1,56; 2,40] | p < 0,001 unilateral; Holm = p | 57i §3 |
| P1h-1 corrigido (ciclo 2 pelo quadro de 13/02) | 1,94 | [1,48; 2,40] | p < 0,001 | 57p §1 |
| peso de toda a amplitude da bolsa, 10·β | 0,42 | [−0,03; 0,87] | — | 57i §4 |
| peso da mesma UF, θ_UF | 2,40 | [2,28; 2,53] | — | 57i §4 |
| β por R$ 1 mil (P1a, a primária do protocolo 52) | 0,0424 | [−0,0027; 0,0874] | p 0,065, Holm 0,065: **não rejeita zero** | 57a §4 |
| km equivalentes a um degrau de R$ 5 mil (K5) | 112 km | [−9; 233] (delta) | descritivo | 57i §4 [*auditoria 50, 27/10/2026: com o quadro corrigido, 119 km [−12; 250] (57v §5.6)*] |

**Estatuto:** comparação de pesos estruturais dentro de um modelo de escolha. Há preferência revelada de um lado e
um coeficiente identificado pelo pacote do corte do outro. **Não é efeito causal** da origem nem da bolsa sobre o
preenchimento. A conclusão é robusta à imprecisão de β: mesmo o limite superior de 10·β (0,87) fica bem abaixo do
limite inferior de θ_UF (2,28).

### 2.4 Robustez

| Especificação | D_UF | Fonte |
|---|---|---|
| M2 (log da distância) / M4 (efeito fixo de UF) / M7 (explodido) | 1,18 / 1,73 / 2,07; q BKY 0,001 | 57i §3 |
| M5 por ciclo (1, 2, 3) | 2,34 / 1,31 / 2,37; q BKY 0,001 | 57i §3 |
| M5 ciclo 2 com o quadro de 13/02 | 1,19 [0,51; 1,86] | 57p §4.2 |
| M2 / M4 / M7 com o quadro de 13/02 | 1,16 / 1,70 / 2,03 | 57v §5.6 (auditoria 46; *correção da auditoria 50, 27/10/2026: antes "auditoria pendente"*) |

- **O que se mantém:** D_UF > 0 em todas as especificações, ciclos e versões do quadro.
- **O que muda:** a significância do próprio β. Ele passa no ciclo 2 e em M2, M4, M8 e M9, mas não no M1, no M7 nem
  nos ciclos 1 e 3 (57a §4).
- **Pós-resultado:** a hipótese foi formulada depois de ver os coeficientes do M1. O protocolo 52b diz que a
  resposta "é previsível" e que "não é teste confirmatório novo" (52b, cabeçalho; [auditoria 31](../auditorias/31_auditoria_P1h_magnitudes.md) §1).
  O deck traz "H2 é pós-resultado" no slide 1.

### 2.5 Ameaças e perguntas da banca

- **"Vocês formularam a hipótese depois de ver o resultado?"** Sim, e isso está declarado. É um teste formal de uma
  diferença já visível nos IC.
- **"O peso da UF é custo do lugar ou manter o emprego e o registro atuais?"** Não se separa com estes dados.
- **"Se β não se distingue de zero, o que quer dizer 'pesa pouco'?"** Quer dizer que é menor que θ_UF com folga. Não
  diz que β é zero nem que é positivo.
- **"Escolha não é preenchimento."** A ponte P1g prevê +0,218 candidato de 1ª opção por célula [−0,015; +0,451]; a
  RDD observa −0,457 [−1,031; +0,117]. Os dois IC contêm zero (57a §9).
- **"Só o ciclo 2 responde à bolsa. Por quê?"** Sem teste. Há leituras candidatas: informação, número de opções,
  proporção de vagas imediatas (57a §7).

### 2.6 Frase honesta

**Dá para afirmar:** "Entre os candidatos, dentro das vagas abertas do seu curso, toda a diferença de bolsa que o
programa oferece (R$ 10 mil → 20 mil) pesa na escolha bem menos que a vaga ficar na UF de origem. Isso vale em
todas as especificações e em cada ciclo."

**Não dá para afirmar:**
- que a origem *causa* a escolha;
- que a bolsa não tem efeito;
- que a bolsa aumenta candidatos ou preenchimento;
- que a desigualdade foi prevista antes dos dados.

### 2.7 Nota: **moderada**

A desigualdade em si é forte: grande, precisa e estável em seis especificações, três ciclos e duas versões do
quadro. A nota cai para moderada por três motivos:
1. é pós-resultado;
2. o lado forte (θ_UF) não é causal, e o lado da política (β) é inconclusivo;
3. a hipótese responde "por quê", não "se" a bolsa preenche.

---

## 3. H3: a chegada do especialista soma oferta ou só remaneja (horas do médico e oferta local)

### 3.1 Estimando e contraste

- **Nível do médico** ([57d](57d_resultados_P4_trajetoria.md) §1): ATT das horas cadastradas no CNES associadas à
  entrada no PMM-E, comparando coortes que entram em meses diferentes (Callaway–Sant'Anna). É **associação sob
  tendências paralelas**, sem fonte de exogeneidade validada (`EXPLORATORIO_P4`).
- **Nível do município, pela chegada** ([57k](57k_resultados_oferta_local.md) §1): ATT da chegada do 1º médico sobre
  a oferta de especialistas (B1 vínculos, B2 horas SUS), sobre os "outros" (B3) e sobre o placebo (B5).
- **Nível do município, no corte** ([57q](57q_resultados_oferta_local_corte.md) §1): forma reduzida do pacote do
  corte sobre a mudança pré → pós da oferta.
- **Contraste:** a chegada ou entrada, **não** a bolsa. Só a versão no corte toca a bolsa, e ali o primeiro estágio
  é nulo.

### 3.2 Identificação

| Premissa | Teste | Resultado | Situação |
|---|---|---|---|
| Tendências paralelas (médico) | Wald do pré; Rambachan–Roth | horas totais: pré p 0,310, ruptura M̄ 1,30; no município do posto: pré **p 0,001**, ruptura 1,90; fora: ruptura 0,78 (57d §5; [57h](57h_resultados_P3P4_sensibilidade.md) §2.2) | aceitável para as horas totais; **falha** para as horas no posto |
| Tendências paralelas (município) | Wald; θ(e) do pré; Rambachan–Roth | B1 e B2 já subiam antes da chegada (θ(−6) de B1 = −0,28 [−0,52; −0,04]); ruptura M̄ = 0 em B1, B2 e B3 (57k §4 e §5) | **falha** |
| Exclusão no corte (razão *fuzzy*) | primeiro estágio | receber médico salta +5,0 p.p. [−20,1; +30,1] em 0,300, F robusto 0,2; em 0,400, F 0,0 (57q §4) | instrumento **fraco**: sem razão utilizável |
| Pré plano no corte; placebo | estudo de evento; generalistas | pré plano (p de 0,063 a 0,707); placebo zero (57q §4) | ok para a forma reduzida |
| Comparação quase experimental na nota de corte | alocado × não alocado perto da nota | horas totais +7,91 [−0,63; +16,45], Holm 0,162; 98 candidatos, 30 alocados (57h §3.2) | não confirma o total |
| Medida | — | vínculo e horas **cadastrados** não são presença (57d §1) | não testável |

### 3.3 Resultado principal

| Nível | Linha | Estimativa [IC 95%] | Leitura | Fonte |
|---|---|---|---|---|
| médico | horas totais, média de θ(0..+6) | +6,6 h/sem [+5,4; +7,8] | associação | 57d §5 |
| médico | no município do posto / fora dele | +8,7 [+7,9; +9,5] / −2,1 [−3,2; −1,0] | o pré falha no posto | 57d §5 |
| médico | já tinham vínculo no município do posto | 51,0% [48,4%; 53,7%] | descritivo | 57d §3 |
| médico | ganho no posto compensado fora (sem grupo de comparação) | 26,3% [17,4%; 35,4%] | descritivo | 57d §9 |
| município (chegada) | B1 / B2 / B3 / B5 | +0,40 / +7,00 / +1,88 / −0,13; ruptura M̄ = 0 nas três primeiras | sem leitura de aumento (regra pré-registrada); B3 não cai | 57k §5.1 |
| município (corte) | B1 em 0,300 / 0,400 | −0,23 [−1,51; +1,05] / −0,46 [−1,86; +0,94]; Holm 1,000 | inconclusivo | 57q §5.1 |
| município (corte) | B3 (outros especialistas) em 0,300 | −4,75 [−19,26; +9,76] | sem sinal de deslocamento | 57q §5.1 |
| município (DiRD, E7) | P2: vínculos nas CBO-alvo | +0,083 [−0,309; +0,476], Holm 0,851; há descontinuidade pré-existente em 0,300 | inconclusivo | 44 §4 e §5.3 |

### 3.4 Robustez

- **Médico:**
  - a regra literal de ligação e a janela longa mantêm as horas totais: +6,1 e +7,5 (57d §10);
  - Rambachan–Roth mantém as horas totais até M̄ ≈ 1,3 (57h §2.4);
  - a comparação na nota de corte não as confirma depois do Holm (57h §3.2).
- **Município:** o pareamento por escore (PS-2 e PM-2) também não detecta diferença na oferta no corte, por exemplo
  ΔB1 em 0,300 +0,06 (57s §1).
- **Pós-resultado:** o protocolo 60 (parte B) e o protocolo 64 são pós-resultado (57k, 57q, cabeçalhos). As decisões
  do 64 foram fixadas antes dos números ([auditoria 39](../auditorias/39_auditoria_oferta_local_corte.md) §1).

### 3.5 Ameaças e perguntas da banca

- **"Isso tem a ver com a bolsa?"** Não. É a chegada. No corte, a bolsa não muda quem recebe médico (F 0,2).
- **"Quem entra mais cedo é diferente?"** Sim, é possível: a seleção da data de entrada não é aleatória (57d §14), e
  no município o pré já subia.
- **"Horas cadastradas são trabalho?"** Não; o CNES registra vínculo e carga declarada.
- **"Metade já estava lá: isso é pagamento a quem já atendia?"** Em parte. Para quem já tinha vínculo no município,
  as horas no município do posto sobem +6,2 [+5,0; +7,4] (57d §6), associação.

### 3.6 Frase honesta

**Dá para afirmar:** "Depois de entrar no PMM-E, o médico cadastra mais horas, sobretudo no município do posto, e
perde parte delas fora. Metade já trabalhava no município. No município, não detectamos saída dos outros
especialistas, e também não dá para afirmar aumento da oferta local."

**Não dá para afirmar:**
- que o programa ou a bolsa aumentaram a oferta local;
- que os médicos estão presentes;
- que a chegada causou o aumento de B1 e B2.

### 3.7 Nota: **fraca a moderada**

- **Moderada** para a associação no nível do médico: precisa, robusta a violações das tendências paralelas do
  tamanho das do pré nas horas totais, mas cadastral e sem exogeneidade.
- **Inconclusiva** para a pergunta da H3 ("soma ou remaneja"), que se responde no município: pré falhando na
  comparação pela chegada, nulo impreciso no corte.

O contraste não envolve o instrumento da política.

---

## 4. Comparação e recomendação

### 4.1 As três lado a lado

| Dimensão | H1 | H2 | H3 |
|---|---|---|---|
| Derivada antes dos dados? | **sim**: H1 do [modelo micro](../02_teoria/modelo_micro.md), §4.2 (∂Pr(aceitar)/∂B > 0); pergunta canônica do [doc 15](../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md), §1 | **não**: pós-resultado (52b; deck, slide 1) | parcialmente: a pergunta "oferta líquida × substituição" é do plano (`CLAUDE.md`); os protocolos são pós-resultado |
| Contraste envolve a bolsa? | sim (pacote do corte) | sim, no β (pacote); o lado forte é a origem | não (chegada); no corte, F ≈ 0 |
| Desenho | RDD *sharp* | modelo estrutural de escolha + degraus nos cortes | evento escalonado (sem exogeneidade) |
| Precisão | baixa por corte (MDE de 25 a 31 p.p. na HI-1) | alta em D_UF; baixa em β | alta no médico; baixa no corte |
| Causal? | descrição do pacote no corte (o desenho permitiria leitura causal do pacote se o balanço passasse) | não (comparação de pesos) | não (associação) |
| Ameaça principal | balanço em 0,300; pós-resultado; poder | pós-resultado; θ não causal; β só no ciclo 2 | tendências pré; cadastro ≠ presença |
| Nota | inconclusiva | moderada | fraca a moderada |

### 4.2 A H1 "não deu certo"?

- **No sentido do que propõe, sim.** Nenhuma especificação mostra preenchimento maior do lado de bolsa maior.
- **Ela também não sustenta um nulo bem estimado.** Por corte, a especificação principal é inconclusiva, e o TOST
  não dá equivalência em nenhuma linha.
- **Ela sustenta, porém, um "não detectado, com descarte parcial de aumentos grandes".** Esse nulo é informativo
  para a política, sob IC convencional:
  - 0,69 alocado por município na HI-2 em 0,300;
  - 10 p.p. e 25% nas medidas empilhadas (57j).
- **É coerente com o resto da cadeia.** O índice de atração não se move (44 §4). A oferta no corte não se move, e o
  corte nem muda quem recebe médico (57q). A oferta no CNES pela DiRD também não se move (44).
- **Pode continuar como hipótese central** se for dita como hipótese **testada e não confirmada**, com o MDE e o
  TOST na tela. Não pode ser dita como "a bolsa não funciona" nem como "o efeito é zero".

### 4.3 A H2 identifica melhor ou só estima com mais precisão?

**Só estima com mais precisão, e a precisão vem do lado não causal.**
- O β da H2 é identificado pelos mesmos cortes (pacote) que a H1.
- Ele soma hipóteses que a H1 não precisa: IIA, forma do *spline* do IVS em toda a faixa, conjunto de escolha
  completo, escolha não estratégica.
- Ele é inconclusivo na primária do protocolo 52 (p 0,065).
- O que a H2 tem de melhor é comparar vagas dentro do mesmo conjunto de escolha, com distância, origem, capital e
  região controladas. Isso afasta os problemas de composição e de porte que atrapalham a H1 no município.
- A força da H2 está na **desigualdade** θ_UF ≫ 10·β, que vale mesmo no limite superior de β. Mas θ_UF é
  preferência revelada, não efeito identificado.

### 4.4 Recomendação

> **Superada em 27/10/2026 pela decisão do autor** (H2 como hipótese única; ver o topo do documento e o
> [doc 07 da banca 2](../07_apresentacoes/banca2/07_nova_hipotese.md)). O texto abaixo fica como registro do
> raciocínio de 26/10. O cuidado que ele levanta continua válido e está no deck: a H2 é dita como **formulada depois
> de ver os dados**.

**Usar a H1 como hipótese única.** Pela regra do autor, a H1 "se sustenta" como hipótese: o desenho existe, a
regra é *sharp*, não há manipulação, e o teste foi feito e auditado. O que não se sustenta é o efeito positivo, e
isso é o resultado, não um defeito da hipótese. Passar à H2 porque a H1 deu nulo seria escolher a hipótese depois
do resultado, contra o espírito do `CLAUDE.md` ("não reescolher… depois de observar resultados").

A H3 não deve ser a hipótese única: é a mais fraca e não testa a bolsa.

Se o autor ler a regra como "a H1 precisa mostrar o efeito", a segunda opção é a H2, apresentada como pós-resultado
e como preferência revelada. Ela é mais fácil de defender estatisticamente, mas pior como desenho. Nesse caso, a
H1 precisaria aparecer como motivação.

**Para a H1 ser defensável na banca:**
1. Dizer na tela "não confirmada" e "pós-resultado (48b)". A cautela já está no slide de Resultados.
2. Pôr o MDE por corte e o TOST juntos. A frase "descarta aumento ≥ 25% nos alocados em 0,300, não descarta queda"
   é a mais forte e honesta disponível.
3. Considerar devolver o TOST empilhado às notas (A3: IC 90% [−11,6; +1,9]). É a única linha que descarta +10 p.p.
   na célula, e sem ela a H1 por corte não descarta nada na HI-1.
4. Trocar "Por que o sinal sai negativo" por "O que pode confundir o corte". O sinal não passa no Holm e vira
   positivo no pareamento e com L+M (57s; 57r).
5. Corrigir a Identificação: "balanço: passam, salvo capitais" subestima. Em 0,300 também falham Nordeste e
   especialistas no resto da região de saúde (57r §3).
6. Atualizar as notas da H2: o adendo 52c já foi executado (D_UF corrigido 1,94 [1,48; 2,40], 57p). O deck ainda
   diz "reestimação em curso".

### 4.5 Como a teoria da banca 1 acomoda o resultado

No modelo, o médico aceita a vaga se B_m/p − c₀(IVS_m) ≥ v̄_i (modelo micro §4.1), e o lado mais vulnerável
preenche se ΔB/p > Δc₀ (com c_im = c₀(IVS_m) + η_i, §3).

- **Bolsa** (o degrau ΔB que a regra fixa): é o único termo que a política mexe.
- **Custo do lugar:** a H2 sugere que o termo que domina a escolha não é o c₀(IVS) que a bolsa compensa, mas o
  componente individual ligado à origem (η_i e a renda alternativa perto da origem). Um degrau de R$ 5 mil pesa
  na escolha o mesmo que 112 km [−9; 233] a menos de distância (57i §3). [*Auditoria 50, 27/10/2026: com o quadro
  corrigido do ciclo 2, de referência, são 119 km [−12; 250] (57v §5.6). Comparando só vagas da mesma UF (52e,
  VL-1), são 75 km [28; 122] (57x §4.3), que são "km dentro da UF" e não se comparam um a um com os do M1.*]
- **Escolha:** com custos individuais grandes e heterogêneos, poucos médicos estão na margem no corte. O degrau
  reordena candidatos entre vagas, como no ciclo 2 (E9). No logit condicional, porém, o que uma vaga ganha outra do
  mesmo curso perde (42 §1).
- **Preenchimento:** sem mexer no número de candidatos (a margem m = 0 não é observada), o preenchimento no corte
  não sobe de forma detectável. É o "incentivo limitado": ΔB/p não alcança Δc₀ + Δη relevante para o médico
  marginal.

A H1 é o teste dessa desigualdade, e o resultado diz que, com R$ 5 mil, ela não se verifica de forma detectável. A
teoria não exige efeito positivo: exige que o degrau supere o custo, e a pergunta canônica ("bolsa maior compensa
município pior?") admite a resposta "não, com este degrau".

Duas ressalvas para a fala:
- o contraste é o pacote;
- o canal da renda alternativa (hipótese H3 do modelo micro) não foi separado do custo do lugar.

---

## 4.6 Avaliação por critérios (acrescentada em 27/10/2026, a pedido do autor)

Notas de 1 (fraco) a 5 (forte). São julgamento técnico sobre os números das seções 1 a 3; nenhum número novo.

| Critério | H1 preenchimento | H2 bolsa × origem | H3 oferta |
|---|:-:|:-:|:-:|
| **Limpeza do desenho** (a variação é exógena?) | **3**: regra *sharp*, sem manipulação; mas em 0,300 capital, Nordeste e especialistas na região diferem entre os lados, e o corte é um pacote | **2**: a bolsa vem dos mesmos cortes (pacote), com hipóteses a mais (IIA, *spline* do IVS, conjunto de escolha); a origem não tem variação exógena | **1**: evento escalonado sem fonte de exogeneidade; no corte, o instrumento é fraco (F ≈ 0) |
| **Hipótese formulada antes dos dados** | **4**: vem do modelo da banca 1; a especificação principal (48b) é pós-resultado | **2**: formulada depois de ver os coeficientes | **3**: a pergunta "soma ou remaneja" é do plano; os protocolos são pós-resultado |
| **Força da conclusão** | **2**: "não detectado"; descarta só aumentos grandes, em parte das medidas, com IC convencional | **4**: a origem pesa muito mais que toda a bolsa, com IC longe de zero; o peso da bolsa sozinho não se distingue de zero | **2**: no médico é associação; no município, inconclusivo |
| **Robustez** | **3**: o "não detectado" se mantém em todas as variantes (controles, PSM, Lee, porte); o **sinal** não se mantém (vira positivo com controles e pareamento) | **4**: estável entre variantes, ciclos e com o quadro corrigido; a bolsa só desloca a escolha no ciclo 2 | **2**: as horas do médico são estáveis; o município tem pré-tendência e ruptura M̄ abaixo de 1 |
| **Precisão / poder** | **2**: só detectaria saltos de 25 a 31 p.p. por corte | **4** na desigualdade origem × bolsa; **2** no peso da bolsa | **3**: alta no médico; baixa no município |
| **Clareza para explicar** | **4**: o gráfico do salto no corte é intuitivo; o sinal negativo exige explicação | **3**: logit e log-chance são abstratos; "R$ 5 mil = 112 km" ajuda | **3**: os dois níveis (médico e município) confundem |
| **Ligação com a teoria da banca 1** | **5**: é o teste direto de ∂Pr(aceitar)/∂B > 0 | **4**: mostra que o custo individual (origem) domina o custo do lugar que a bolsa compensa | **2**: fala de oferta, não da bolsa |
| **Relevância para a pergunta do artigo** | **5**: "bolsa maior enche mais vagas?" | **3**: explica por que não, mas não responde à pergunta | **3**: oferta líquida é parte da cadeia, sem a bolsa no contraste |
| **Soma (máx. 40)** | **28** | **26** | **19** |

**Leitura.** H1 e H2 ficam próximas; a H3 fica para trás em quase tudo. A H1 ganha em desenho, teoria e relevância;
a H2 ganha em força da conclusão, robustez do que afirma e precisão. A escolha depende do peso que a banca dá a
"desenho limpo testando a pergunta" (H1) contra "resultado firme" (H2). Os critérios têm o mesmo peso nesta soma;
com outros pesos a ordem entre H1 e H2 pode inverter.

**Pergunta mais provável da banca, e a resposta honesta:**
- **H1:** "o resultado é nulo ou falta poder?". Os dois: não se detecta aumento, e o desenho só detectaria saltos
  grandes por corte. Descarta aumento ≥ 25% nos alocados em 0,300, não descarta queda.
- **H2:** "a origem é causal?". Não: é preferência revelada. A comparação diz quanto cada coisa pesa na escolha,
  não o que aconteceria se o médico mudasse de origem. E "por que só no ciclo 2?": não sabemos; os ciclos 1 e 3
  têm IC largo.
- **H3:** "as horas cadastradas são presença?". Não: vínculo cadastrado não é presença, e no município o pré já
  vinha subindo.

## 4.7 Reavaliação com foco em interpretação simples e clara (27/10/2026, a pedido do autor)

Mesmos números; outros critérios. Notas de 1 a 5.

| Critério | H1 | H2 | H3 |
|---|:-:|:-:|:-:|
| A mensagem cabe numa frase, sem "mas" | 2 | 5 | 3 |
| O gráfico principal fala sozinho | 3 | 5 | 3 |
| A conclusão diz algo que acontece (e não só "não detectado") | 1 | 4 | 3 |
| Poucas ressalvas obrigatórias | 1 | 3 | 2 |
| O método se explica para leigo | 4 | 3 | 3 |
| Resposta firme à pergunta mais dura da banca | 2 | 4 | 2 |
| **Soma (máx. 30)** | **13** | **24** | **16** |

**Frase de 10 segundos de cada uma:**
- **H1:** "Onde a bolsa é R$ 5 mil maior, não vimos mais vagas preenchidas; mas o desenho só pegaria efeitos
  grandes, e o corte muda outras regras junto." Precisa de cinco ressalvas: pacote do corte, poder, balanço em
  0,300, sinal negativo e especificação escolhida depois.
- **H2:** "O médico escolhe perto de onde já trabalha: 79% põem a 1ª opção na mesma UF, e ter a vaga na UF de
  origem pesa na escolha muito mais que toda a diferença de bolsa." [*Fonte dos 79%, acrescentada pela auditoria
  50 em 27/10/2026: `output/apresentacao_banca2/numeros_banca2.json`, `ESC_UF`, sobre os 5.425 candidatos do G1, no
  doc 02 da banca 2. É descritivo, não o teste da H2.*] Precisa de três ressalvas: é preferência, não
  efeito causal da origem; a hipótese veio depois dos dados; a bolsa só deslocou a escolha no ciclo 2.
- **H3:** "O médico que entra cadastra mais horas, mas metade já estava no município, e não dá para dizer que a
  oferta local subiu." Precisa de duas ressalvas, mas a conclusão central é inconclusiva.

**Leitura.** Com foco em clareza, a ordem muda: **H2 > H3 > H1**. A H1 continua a de melhor desenho, mas é a mais
difícil de contar: a conclusão é uma ausência e vem cercada de ressalvas. A H2 conta uma história simples,
com gráfico que fala sozinho e um resultado firme.

**Uma forma de juntar as duas numa só hipótese (H2), sem esconder a ordem:** apresentar o resultado da H1 como o
**fato** que motiva a pergunta ("no corte, a bolsa maior não encheu mais vagas") e a H2 como a hipótese que o
explica ("porque a origem pesa mais que a bolsa"). A H2 deve ser dita como formulada depois de ver os dados.

## 4.8 Atualização de 27/10/2026: H1 e H2 com a localização controlada (adendos 48h e 52e)

Pedido do autor: rodar H1 e H2 "com pareamento pela localização da unidade e do médico, o controle mais importante".
Os dois adendos foram executados e auditados, e nenhuma estimativa mudou nas auditorias.

- **H1 ([57w](57w_resultados_pareamento_localizacao.md), [auditoria 47](../auditorias/47_auditoria_pareamento_localizacao.md)).**
  - **Pareamento:** pares formados dentro da **mesma UF** e da mesma condição de capital, parecidos no escore
    (população, médicos, especialistas no município e a até 100 km). Em cada ciclo, quem procura par é o lado com
    menos unidades. A maioria fica sem par, e os pares são sobretudo do ciclo 2 (57w, "O preço" e §4). [*Correção da
    auditoria 50, 27/10/2026: antes dizia "cada município do lado de bolsa maior pareado com um da mesma UF".*]
  - **Resultado:** não se detecta diferença de preenchimento nos dois cortes. Em 0,300, o ponto da fração preenchida
    é +16,4 p.p. [−3,8; +36,6], com sinal oposto ao da RDD, e não deve ser lido como tamanho de efeito (auditoria
    47, A5). [*Correção da auditoria 50, 27/10/2026: antes dizia "nenhuma diferença".*]
  - **Poder:** sobram poucos pares (25 e 29), e só seria detectada uma diferença de cerca de 24 a 29 p.p.
  - **De onde vinha a queda em 0,300:** da **UF**. Na mesma amostra, a HI-2 em 0,300 vai de −1,15 [−2,21; −0,08],
    sem controle, para −0,55 [−1,61; +0,50] só com efeito fixo de UF. O ponto cai à metade, e o IC passa a conter
    zero. Só com o estoque de especialistas no entorno, ela continua: −1,19 [−2,24; −0,13] (auditoria 47,
    observações). [*Correção da auditoria 50, 27/10/2026: antes dizia "com efeito fixo de UF, a queda some". A
    leitura "vinha da UF" é opinião. A queda nunca passou no Holm, e capital, L+M e pareamento também a mexem (ver a
    nota de estado atual no topo).*]
- **H2 ([57x](57x_resultados_escolha_localizacao_par.md), [auditoria 48](../auditorias/48_auditoria_escolha_localizacao_par.md)).**
  - **Comparação:** só vagas da mesma UF, vistas por médicos da mesma UF de origem.
  - **Resultado:** a bolsa maior faz a vaga ser escolhida mais vezes como 1ª opção. Nos ciclos 1–3, a bolsa pesa
    **mais** do que na especificação base, e passa a se distinguir de zero depois do Holm. No ciclo 2, pesa o mesmo.
  - **Perto do corte:** a comparação local tem o ponto parecido e o IC que contém 1 (inconclusiva).

**Efeito sobre a avaliação.** A H2 ganha força: o peso da bolsa na escolha deixa de depender de onde as vagas
ficam. A H1 continua inconclusiva, agora com a explicação do sinal resolvida (UF). As duas juntas dão uma leitura
simples, que é a do "incentivo limitado": a bolsa muda **qual** vaga o médico escolhe dentro da sua região, mas
não **quantas** vagas são preenchidas.

---

## 5. O que foi lido

- **H1:** [48](48_protocolo_contagem_vagas_preenchidas.md), [48b](48b_adendo_H1_vagas_imediatas.md),
  [57n](57n_resultados_H1_vagas_imediatas.md), [49](49_resultados_contagem_vagas_preenchidas.md),
  [49b](49b_diagnostico_contagem_porte.md), [57j](57j_resultados_equivalencia_H1.md),
  [57l](57l_diagnostico_queda_0300.md), [57m](57m_gradiente_faixas.md), [48c](48c_adendo_capitais_e_UF.md),
  [57o](57o_h1_capitais_uf.md), [48d](48d_adendo_controles_localizacao_e_medicos.md),
  [57r](57r_resultados_controles_localizacao_medicos.md), [48e](48e_adendo_pareamento_regra_literal_e_0400.md),
  [57s](57s_resultados_pareamento_regra_literal.md), [48f](48f_adendo_selecao_tipo_de_vaga.md),
  [57t](57t_resultados_selecao_tipo_vaga.md), [48g](48g_adendo_heterogeneidade_porte_ied.md),
  [57u](57u_resultados_heterogeneidade_porte.md), [63](63_registro_explicacoes_e_controles_H1.md),
  [37](37_resultados_rdd_bolsa_ivs_oficial.md); auditorias 36, 38, 40, 42, 43, 44 e 45.
- **H2:** [42](42_resultados_E9_escolha.md), [52](52_protocolo_P1_escolha_dap.md),
  [52b](52b_protocolo_P1h_magnitudes.md), [52c](52c_adendo_vaga_imediata_ciclo2.md),
  [57a](57a_resultados_P1_escolha.md), [57i](57i_resultados_P1h_magnitudes.md),
  [57p](57p_escolha_vaga_imediata_c2.md), [52d](52d_adendo_sensibilidades_ciclo2_quadro_1302.md),
  [57v](57v_sensibilidades_ciclo2_quadro_1302.md) (auditoria 46; *correção da auditoria 50, 27/10/2026: antes
  "auditoria pendente"*), [44](44_sintese_rdd_bolsa_multioutcome.md);
  auditorias 31 e 41.
- **H3:** [57d](57d_resultados_P4_trajetoria.md), [57h](57h_resultados_P3P4_sensibilidade.md),
  [60](60_protocolo_equivalencia_e_oferta_local.md), [57k](57k_resultados_oferta_local.md),
  [64](64_protocolo_oferta_local_no_corte.md), [57q](57q_resultados_oferta_local_corte.md), 43 (pela síntese 44);
  auditorias 34 e 39.
- **Transversais:** auditorias 18 e 35; [doc 15](../01_pergunta_escopo/15_incentivos_ivs_provimento_duradouro.md);
  [modelo micro](../02_teoria/modelo_micro.md); [57](57_sintese_perguntas_reformuladas.md);
  [05](../07_apresentacoes/banca2/05_discussao_historia_empirica.md),
  [04](../07_apresentacoes/banca2/04_conteudo_deck_curto.md) e
  [06](../07_apresentacoes/banca2/06_estrutura_obrigatoria_versao_final.md) da banca 2; texto do
  `output/apresentacao_banca2/deck_banca2_curto.pdf`.
