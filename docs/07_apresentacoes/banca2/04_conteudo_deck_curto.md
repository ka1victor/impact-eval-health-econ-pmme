---
documento: Conteúdo do deck curto — banca 2 (parte empírica)
papel: fonte de verdade do deck curto, o único usado na versão final; o deck é derivado
escopo: estrutura obrigatória da versão final (doc 06) — Hipótese, Dados, Análise descritiva, Metodologia, Identificação, Resultados, Robustez e Discussão — com uma hipótese só, o efeito da bolsa na 1ª opção comparando vagas da mesma UF (decisão do autor de 28/10/2026); sem apêndice (decisão do autor de 28/10/2026: nada de preenchimento, só a escolha da 1ª opção); sem os slides do grupo, sem divisórias e sem o diagrama da teoria
slides: 11
estado: em produção; versão de 28/10/2026 (dia da banca), ajustada à decisão do autor "a hipótese é simplesmente sobre o efeito bolsa → 1ª opção", com "só comparação entre municípios da mesma UF", e ao reforço "pode deixar TUDO na mesma UF. UF, origem etc. é tudo controle/pareamento"; corpo: pergunta e hipótese; dados e amostra; regra sharp; onde escolhem (motivação para comparar dentro da UF); a descritiva da hipótese (F2 do doc 66); modelo (logit condicional com efeito fixo do par de UFs; teste β > zero); identificação (o que mantemos fixo; especificação pós-resultado); resultado principal (VL-1); robustez só dentro da mesma UF; conclusão; limitações; sem apêndice; versão anterior (33d15d9, 27/10/2026) no histórico do Git e mapa no doc 10, §6
atualizacao: 28 de outubro de 2026
---

> [!IMPORTANT]
> **Decisão do autor de 28/10/2026 (dia da banca).** "A hipótese é simplesmente sobre o efeito bolsa → 1ª opção",
> com "só comparação entre municípios da mesma UF". Reforço do mesmo dia: "pode deixar TUDO na mesma UF. UF, origem
> etc. é tudo controle/pareamento". Nesta versão:
> - **Hipótese** (slide 1): uma frase só, sobre o efeito da bolsa na escolha, comparando vagas da mesma UF; continua
>   dita como formulada após ver os dados. Saiu "pesa menos que a origem".
> - **Nenhum resultado sobre a origem.** O teste origem × toda a bolsa (D_UF) e o slide "Teste central" saíram do
>   corpo e do apêndice; o D_UF fica numa linha das notas do slide de Limitações, só para pergunta da banca. A UF de
>   origem × UF da vaga (efeito fixo do par), a região de saúde, o município e a distância aparecem só como controle e
>   pareamento, no Modelo e na Identificação.
> - **Descritiva:** os 79% na própria UF são a motivação para comparar dentro da UF; a F2 do doc 66 (perto do corte,
>   na UF de origem, o lado de bolsa maior tem 52,5% das vagas e 60,8% das 1ªs opções) é a descritiva da hipótese.
> - **Resultado principal:** o VL-1 (adendo 52e), sem a linha do modelo base na figura; a especificação pré-registrada,
>   sem fixar a UF, fica nas limitações e nas notas.
> - **Robustez:** só variantes dentro da mesma UF (distância em log, região de saúde de origem × UF da vaga, só vagas
>   perto do corte) e o VL-1 por ciclo, com os ciclos 1 e 3 do adendo 52g (`VG_estimativas.csv`, doc 57z, auditoria
>   pendente): forte só no ciclo 2; nos ciclos 1 e 3 o IC contém 1 (leitura fixada no adendo, `FORTE_SO_NO_CICLO_2`).
> - **Sem preenchimento** (decisão do autor de 28/10/2026, "não é pra ter nada de preenchimento, só escolha na
>   primeira opção"): saíram a motivação pelo preenchimento no corte, a limitação "escolha ≠ preenchimento" e o
>   apêndice com o fato da antiga H1. O deck não tem apêndice.
> - Continuam: 11 slides no corpo (o apêndice, se voltar, tem no máximo 2); até 30 palavras por slide; as oito seções; roteiro de
>   cerca de 7 minutos (doc 09); a regra dos números; as frases proibidas das auditorias 49, 50, 52, 53 e 55, mais
>   "origem pesa", "×11" e "D_UF" na tela.
>
> As versões de 27/10/2026 (hipótese bolsa × origem, revista pela rubrica e pela auditoria 55) ficam no histórico do
> Git (`git show 33d15d9:docs/07_apresentacoes/banca2/04_conteudo_deck_curto.md`); o que mudou slide a slide está no
> [doc 10](10_mapa_deck_anterior_para_rubrica.md), §6.
>
> **Formato.** Cada `#` é uma seção da estrutura obrigatória (e, no fim, o `# Apêndice`); cada `##` é um slide:
> título-afirmação (no máximo 58 caracteres), a figura (ou a tabela) grande e poucas linhas curtas. As linhas são os
> marcadores `- `; a cautela é a citação em negrito. Layouts: `curto_figura`, `curto_tabela`, `curto_texto`,
> `curto_capa` (frase grande, com cautela opcional), `curto_hipotese` (a hipótese em destaque; a motivação em cinza)
> e `curto_espec` (a 1ª linha, sem rótulo, é a equação). O bloco `> **Roteiro (N s).**` é a fala do slide, com o
> tempo-alvo em segundos; vai para as notas antes do detalhe, só no corpo. O gerador
> (`scripts/apresentacao/gerar_deck_banca2.py`, modo padrão) para se as seções fugirem da estrutura, se o corpo passar
> de 14 slides ou o apêndice de 2, se um slide passar de 30 palavras, se uma linha não couber ou se o roteiro sair de
> 6:30 a 7:30.
>
> **Regra dos números.** Todo número de um slide, notas incluídas, é o valor de um código listado na linha
> `**Números:**` ou um parâmetro do protocolo
> ([03, §3](03_proveniencia_figuras_e_numeros.md#3-parâmetros-que-podem-aparecer-sem-código)).
> `tests/test_deck_curto_banca2.py` confere a estrutura, a contagem de palavras, os números, as cautelas e o pacote
> gerado.

<!-- deck:inicio -->

# Hipótese

## Pergunta e hipótese: a bolsa maior muda a 1ª opção?

`Hipótese`

<!-- layout: curto_hipotese -->

- **Hipótese** comparando vagas da mesma UF, a de bolsa maior tem mais chance de ser a 1ª opção
- **Motivação** a bolsa sobe com o IVS

> **Formulada após ver os dados.**

**Fontes:** doc 07 da banca 2 (decisão do autor de 28/10/2026); adendos 52e e 52g; doc 57x; auditoria 48.

**Números:** nenhum

> **Roteiro (35 s).** Nossa pergunta é simples: quando o médico especialista escolhe uma vaga do PMM-E, a bolsa maior
> muda qual vaga ele põe em 1ª opção? A hipótese: comparando vagas da mesma UF, a vaga de bolsa maior tem mais chance
> de ser a 1ª opção. A motivação: o programa paga bolsa maior onde o IVS do município é maior; queremos saber se
> isso muda a vaga que o médico escolhe. Um aviso honesto, que está na tela: formulamos esta
> hipótese depois de ver os dados.

> **Notas do apresentador.** Hipótese única desta versão (decisão do autor de 28/10/2026; doc 07 da banca 2): "a
> hipótese é simplesmente sobre o efeito bolsa → 1ª opção", com "só comparação entre municípios da mesma UF". A UF de
> origem, a UF da vaga, a região de saúde, o município e a distância entram só como controle e pareamento, nunca como
> resultado. Foi formulada depois de ver outros resultados do projeto no corte e os coeficientes do modelo de
> escolha: é pós-resultado, e isso é dito aqui. A leitura pela teoria da banca 1 é interpretação, não teste
> (auditoria 50). O contraste da bolsa é o pacote do corte (a bolsa e as outras regras federais que mudam
> nos mesmos cortes de IVS, auditoria 18), não a participação no PMM-E nem o Agora Tem Especialistas. Tudo é
> condicional a se candidatar.

---

# Dados

## Dados e amostra: de onde vêm e quem entra no modelo

`Dados · fontes, unidade e funil`

<!-- layout: curto_figura -->
<!-- linhas: 3 -->

![Variáveis e fontes, à esquerda; à direita, o funil da amostra da escolha por ciclo, de quem tem 1ª opção no quadro até quem entra no modelo, com quem sai em cada etapa](../../../output/apresentacao_banca2/curto_dados_amostra.png)

- **Unidade:** candidato × vaga do seu curso e ciclo; y = 1 na 1ª opção.
- **No modelo:** 5.421 candidatos e 932.577 pares candidato × vaga.

> **y = opção marcada, não ida ao município.**

**Fontes:** `output/rdd_bolsa/P1_resumo.json` (protocolo 52; doc 57a); portão G1; `output/apresentacao_banca2/tabela_fontes.csv`; `curto_dados_amostra.png`; auditorias 16, 36 e 41.

**Números:** `M1_N`, `AM_PARES`, `AM_CONJ`, `AM_VAGAS`, `AM_TOT_R1`, `AM_TOT_LIG`, `AM_TOT_ORI`

> **Roteiro (45 s).** A 1ª opção de cada candidato vem dos editais do Ministério da Saúde, ciclos 1 a 3; a origem
> vem do CNES: o município onde ele tinha vínculo médico antes da inscrição; bolsa e vagas, dos quadros de vagas; o
> IVS, do Ipea; distância e UF, do IBGE. A unidade de observação é o par candidato × vaga: cada candidato aparece
> uma vez para cada vaga aberta do seu curso e ciclo, e a variável dependente vale 1 na sua 1ª opção. Atenção: é a vaga que ele marcou na inscrição; não
> medimos se ele foi alocado nem se entrou no município. O funil, à
> direita, mostra quem sai em cada etapa: dos 5.714 candidatos com 1ª opção, 5.421 entram no modelo.

> **Notas do apresentador.** 1ª opção: listas de classificação dos editais do PMM-E (SGTES/MS), ciclos 1–3, uma
> linha por candidato e opção. Cada ciclo é um chamamento com quadro de vagas próprio: o ciclo 1 com quadro de
> 24/07/2025; o ciclo 2 com quadro de 03/02/2026, retificado em 13/02/2026 (o vigente na inscrição, de onde vem o
> tipo de vaga usado aqui; auditoria 36) e de novo em 19/03/2026; o ciclo 3 com quadro de 16/07/2026. Origem: o
> município do estabelecimento onde o candidato tinha vínculo médico no CNES antes das inscrições, ligado pelo
> portão G1 (CPF e nome); não é a residência. Vagas e bolsa: quadros de vagas da 1ª chamada, por célula
> (estabelecimento × curso), com a faixa da bolsa anunciada (adendo 52c, auditoria 41). IVS 2010 oficial: Plataforma
> IVS do Ipea; é a variável dos cortes. Distância entre os centroides dos municípios (malha do IBGE); UF e região de
> saúde (tabela oficial do TabNet). Secundárias, em cinza: porte e capital, controles do modelo. Funil (P1_resumo.json,
> sem recálculo): 5.714 candidatos com 1ª opção numa vaga do quadro; 5.513 ligados ao CNES; 5.425 com município de
> origem (vínculo médico na competência anterior à inscrição); 5.421 no modelo, depois de tirar quem tem a origem ou
> a 1ª opção num município sem região de saúde na tabela oficial. Unidade do modelo: 932.577 pares candidato × vaga,
> em 56 conjuntos de escolha (curso × ciclo), com 5.125 vagas (estabelecimento × curso). A taxa de ligação é
> parecida entre alocados e não alocados (G1). Dados pessoais só em memória ou em cache fora do Git.

---

# Análise descritiva

## A bolsa é função exata do IVS: a regra é sharp

`Análise descritiva · IVS × faixa`

<!-- layout: curto_figura -->

![Bolsa anunciada contra o IVS 2010 oficial, ciclo 1, um ponto por município](../../../output/apresentacao_banca2/regra_bolsa_ivs_oficial.png)

- **Como ler:** um ponto por município do ciclo 1; a bolsa salta nos cortes.
- **Ciclos 1 e 2:** reproduz 368/368 e 454/454 municípios.

**Fontes:** `output/rdd_bolsa/portao_r1_ivs_oficial.json`; `output/aquisicao/a08_ivs_2010_oficial_municipio.csv`; auditoria 16.

**Números:** `R_C1_REPR`, `R_C1_MUN`, `R_C2_REPR`, `R_C2_MUN`, `R_ESCORE_IGUAIS`, `R_C3_REPR`, `R_C3_MUN`

> **Roteiro (25 s).** De onde vem a variação da bolsa? De uma regra. Até IVS 0,300, R$ 10 mil; até 0,400, R$ 15 mil;
> acima, R$ 20 mil. Cada ponto é um município, e a regra reproduz a faixa de todos os municípios dos ciclos 1 e 2.
> O município não escolhe a bolsa: é a regra que dá.

> **Notas do apresentador.** Como ler: cada ponto é um município com vaga no quadro da 1ª chamada do ciclo 1; o
> eixo horizontal é o IVS 2010 oficial, a cor também; o vertical, a bolsa anunciada. Até 0,300, R$ 10 mil; até
> 0,400, R$ 15 mil; acima, R$ 20 mil. O escore da relação nominal do MS é o IVS 2010 oficial em 404/404 municípios.
> No ciclo 3, 747 de 748: o que falta foi criado depois de 2010. É daqui que vem a variação da bolsa no modelo de
> escolha: vagas parecidas, de lados diferentes de um corte, pagam bolsas diferentes. Em 0,300 e 0,400 mudam também
> outras regras federais: pacote do corte.

---

## Onde escolhem: a maioria fica na própria UF

`Análise descritiva · motivação do desenho`

<!-- layout: curto_figura -->

![1ª opção em relação à origem do candidato (mesma UF, mesma região de saúde, mesmo município) e distância da origem à 1ª opção](../../../output/apresentacao_banca2/exp_escolha_origem.png)

- **79%** põem a 1ª opção na UF de origem; mediana: 51 km (descritivo).
- **Por isso:** comparamos só vagas da mesma UF.

**Fontes:** `output/rdd_bolsa/G1_distancias_opcoes.parquet` e `G1_candidatos_origem.parquet` (portão G1); `output/apresentacao_banca2/exp_escolha_origem.png`.

**Números:** `ESC_N`, `ESC_UF`, `ESC_REG`, `ESC_MUN`, `ESC_DIST_P50`, `ESC_DIST_P75`

> **Roteiro (30 s).** Antes do modelo, os dados crus. Dos 5.425 candidatos com origem, 79% põem a 1ª opção na
> própria UF, e a distância mediana é de 51 km. Isso é descritivo, e não é o nosso resultado: é o motivo do desenho.
> Como a maioria escolhe dentro da própria UF, comparamos só vagas da mesma UF, e a UF entra como controle.

> **Notas do apresentador.** Descritivo. Dos 5.425 candidatos com 1ª opção e município de origem, 79% põem a 1ª
> opção na UF onde já trabalhavam, 46% na mesma região de saúde e 36% no próprio município; a distância mediana até
> a 1ª opção é 51 km, e três em cada quatro ficam a até 189 km. A origem é o município do vínculo médico anterior
> no CNES, não a residência. É preferência revelada: diz onde escolhem, não por quê. Aqui ela não é resultado: é a
> razão para controlar e parear pela UF (decisão do autor de 28/10/2026). Como a comparação crua mistura a bolsa com o
> IVS, a distância e a UF (doc 66, §3), o modelo compara cada candidato consigo mesmo, só entre vagas da mesma UF.

---

## Descritivo: perto do corte, a bolsa maior é mais escolhida

`Análise descritiva · a hipótese nos dados`

<!-- layout: curto_figura -->
<!-- linhas: 3 -->

![Descritivo: na UF de origem, a até 0,050 de um corte de IVS, a parte do lado de bolsa maior nas vagas disponíveis e nas 1ªs opções, ciclos 1–3 e por ciclo](../../../output/rdd_bolsa/H2_figuras/H2_F2_mesma_uf_perto_do_corte.png)

- **Bolsa maior:** 52,5% das vagas, 60,8% das 1ªs opções.
- **Quem:** na UF de origem, a até 0,050 de um corte; 1.568 candidatos.

> **Descritivo: sem teste e sem controlar a distância.**

**Fontes:** `output/rdd_bolsa/H2_sintese.csv` e `H2_figuras/H2_F2_mesma_uf_perto_do_corte.png` (`scripts/rdd_bolsa/51_sintese_H2.py`; doc 66, §3; auditoria 52).

**Números:** `H2D_DISP`, `H2D_ESC`, `H2D_N`

> **Roteiro (35 s).** Agora, a descritiva da hipótese. Pegamos só as 1ªs opções na UF de origem, a até 0,050 de um
> corte de IVS, onde as vagas dos dois lados são parecidas. O lado de bolsa maior tem 52,5% das vagas, mas recebe
> 60,8% das 1ªs opções: é mais escolhido do que oferecido, e nos três ciclos. Cuidado: é descritivo, sem teste e sem
> controlar a distância; quem testa é o modelo.

> **Notas do apresentador.** Descritivo (doc 66, §3; figura F2 do doc 66, usada sem redesenho; auditoria 52). Só
> 1ªs opções na UF de origem a até 0,050 de um corte; para cada candidato, a parte das vagas (estabelecimento ×
> curso) do mesmo curso e UF que fica no lado de bolsa maior, contra a parte das 1ªs opções que fica nele: 52,5% das
> vagas e 60,8% das 1ªs opções, com 1.568 candidatos nos ciclos 1–3. Em cada ciclo, as 1ªs opções ficam acima das
> vagas. Não é evidência à parte: sem teste e sem controlar a distância; a versão com inferência, distância e o par de
> UFs fixado (VL-2, só vagas perto do corte) é inconclusiva (Robustez). Pacote do corte; condicional a se candidatar.

---

# Metodologia

## Modelo: logit condicional da 1ª opção

`Metodologia · escolha`

<!-- layout: curto_espec -->

- U = β·bolsa + γ·distância + EF(UF origem × UF vaga) + …; P(j) = e^Uj/Σe^U
- **Por quê** candidato consigo mesmo, vagas da mesma UF
- **Bolsa** regra do IVS (sharp)
- **Teste** β > zero; cluster por conjunto

**Fontes:** protocolo 52; adendos 52c e 52e (`docs/06_execucao/`); docs 57a, 57x e 66 (§4).

**Números:** `M1_N`

> **Roteiro (35 s).** Usamos um logit condicional. A escolha é discreta: o candidato escolhe uma entre as vagas
> abertas do seu curso. Cada candidato é comparado consigo mesmo, e o efeito fixo do par de UFs faz a comparação só
> entre vagas da mesma UF, vistas por médicos da mesma UF de origem. A distância, a região e o município entram como
> controle. A bolsa varia pela regra do IVS. O teste é β maior que zero, com erro-padrão agrupado por conjunto de
> escolha.

> **Notas do apresentador.** Logit condicional (McFadden): cada um dos 5.421 candidatos escolhe, entre as vagas
> abertas do seu curso e ciclo, a de maior utilidade; o candidato é comparado consigo mesmo entre as vagas que podia
> escolher, e o que não varia entre vagas (dele) sai da verossimilhança. Utilidade (VL-1, adendo 52e): bolsa (linear,
> por R$ 1 mil) + curva contínua do IVS (spline com dobras nos cortes, sem salto) + distância + mesma região de saúde e
> mesmo município da origem + efeito fixo do par (UF de origem, UF da vaga) + porte, capital, estrato e vagas
> imediatas da vaga. Com o efeito fixo do par, o peso da bolsa vem só de vagas da mesma UF (a de origem ou outra),
> vistas por médicos da mesma UF de origem. Só o salto da bolsa nos cortes de IVS identifica o peso dela. UF,
> região, município e distância são controle e pareamento: os coeficientes deles não são interpretados. Teste: β > zero;
> p de H0: β = zero com erro-padrão agrupado por conjunto de escolha (curso × ciclo), Holm nas três principais do adendo
> e, com poucos grupos, score bootstrap de Rademacher. Tipo de vaga do ciclo 2 pelo quadro de 13/02/2026 (adendo 52c).
> Especificação pós-resultado: o adendo 52e foi congelado antes de rodar, mas depois de ver o modelo base.

---

# Identificação

## Identificação: as premissas e o nosso caso

`Identificação · escolha`

<!-- layout: curto_tabela -->

| Premissa | Aderência |
|---|---|
| Bolsa por regra | sharp: 368/368, 454/454 |
| Mantido fixo | candidato, par de UFs, distância |
| Só a bolsa? | não: pacote do corte |
| Especificação | pós-resultado (adendo 52e) |
| Conjunto | suposto: todas vistas |

**Fontes:** auditorias 16, 18 e 48; adendo 52e; docs 57a, 57v e 57x; `output/rdd_bolsa/portao_r1_ivs_oficial.json`; `VL_estimativas.csv`.

**Números:** `R_C1_REPR`, `R_C1_MUN`, `R_C2_REPR`, `R_C2_MUN`, `VLB_EMP_RC`, `VLB_EMP_RCI`, `VLB_EMP_RCS`, `VC_B_HOLM`

> **Roteiro (45 s).** Cinco premissas. Primeiro, a bolsa segue a regra do IVS, sem exceção nos ciclos 1 e 2. Segundo,
> o que mantemos fixo: o próprio candidato, o par de UFs e a distância; a região de saúde e o município também entram
> como controle. Terceiro, nos mesmos cortes mudam outras regras federais: medimos o pacote do corte. Quarto, e
> precisamos ser claros: esta especificação foi escolhida depois de ver o resultado; a pré-registrada, sem fixar a
> UF, tem intervalo que contém 1. Quinto, supomos que o candidato viu todas as vagas do seu curso.

> **Notas do apresentador.** Bolsa por regra: o IVS 2010 oficial reproduz a faixa de todos os municípios dos ciclos
> 1 e 2 (368/368 e 454/454); o município não escolhe a bolsa. Mantido fixo: o candidato (logit condicional), o par
> (UF de origem, UF da vaga) por efeito fixo e a distância, com a mesma região de saúde e o mesmo município da origem
> como controles; nenhum deles é resultado. Pacote do corte: em 0,300 e 0,400 mudam também outras regras federais
> (auditoria 18); o peso da bolsa é o do pacote, não o da bolsa sozinha nem o da participação no PMM-E.
> Especificação pós-resultado (adendo 52e; auditoria 48): congelada antes de rodar, depois de ver o modelo base. A
> especificação pré-registrada (P1a, sem fixar a UF) dá 1,25 [0,98; 1,61], IC que contém 1 (p 0,072; família de um
> teste, Holm = p). IIA (independência de alternativas irrelevantes): no modelo base, o logit aninhado por região de
> saúde a rejeita em parte e o peso da bolsa fica perto do mesmo valor (doc 57a; doc 57v); não foi refeito com o par
> de UFs. Conjunto de escolha: supõe que o candidato viu todas as vagas do seu curso e listou sem estratégia (a
> alocação é por nota). A origem é medida pelo vínculo anterior no CNES, não pela residência. Tudo é condicional a se
> candidatar.

---

# Resultados

## Dentro da mesma UF, a vaga de bolsa maior é preferida

`Resultados · bolsa → 1ª opção`

<!-- layout: curto_figura -->
<!-- linhas: 3 -->

![Razão de chances da 1ª opção por +R$ 5 mil comparando vagas da mesma UF (efeito fixo do par de UFs), ciclos 1–3 e ciclo 2, com IC 95% e os km equivalentes](../../../output/apresentacao_banca2/curto_bolsa_mesma_uf.png)

- **+R$ 5 mil:** chance ×1,47 [1,15; 1,89].
- **Leitura:** por +R$ 5 mil, o médico aceita vaga 75 km mais longe.

> **Adendo pós-resultado; pré-registrado, sem fixar a UF: IC contém 1.**

**Fontes:** `output/rdd_bolsa/VL_estimativas.csv` (adendo 52e; doc 57x; auditoria 48); `output/apresentacao_banca2/curto_bolsa_mesma_uf.png`.

**Números:** `VL1_EMP_RC`, `VL1_EMP_RCI`, `VL1_EMP_RCS`, `VL1_EMP_HOLM`, `VL1_C2_RC`, `VL1_C2_RCI`, `VL1_C2_RCS`, `VL1_C2_HOLM`, `VL1_EMP_K5`, `VL1_EMP_K5I`, `VL1_EMP_K5S`, `VL1_C2_K5`, `VL1_C2_K5I`, `VL1_C2_K5S`, `VLB_EMP_RC`, `VLB_EMP_RCI`, `VLB_EMP_RCS`, `VLB_C2_RC`, `VLB_C2_RCI`, `VLB_C2_RCS`, `VC_B_HOLM`

> **Roteiro (50 s).** Este é o resultado principal. Comparando só vagas da mesma UF, a de origem ou outra, vistas por
> médicos da mesma UF de origem, a vaga com bolsa R$ 5 mil maior tem 1,47 vez a chance de ser a 1ª opção, nos ciclos
> 1 a 3 juntos; o intervalo vai de 1,15 a 1,89. No ciclo 2, 1,90. Em palavras: entre duas vagas parecidas da mesma UF,
> a de bolsa maior tem cerca de uma vez e meia a chance de ser a escolhida; ou, por R$ 5 mil a mais, o médico aceita
> uma vaga 75 km mais longe. Duas ressalvas, na tela: é uma especificação escolhida depois do resultado; e a
> pré-registrada, sem fixar a UF, tem intervalo que contém 1.

> **Notas do apresentador.** VL-1 (adendo 52e; doc 57x; auditoria 48; pós-resultado): comparando só vagas da mesma
> UF (a de origem ou outra), vistas por médicos da mesma UF de origem (efeito fixo do par de UFs), a razão de chances
> da 1ª opção por +R$ 5 mil é 1,47 [1,15; 1,89] nos ciclos 1–3 (p de Holm 0,005) e 1,90 [1,30; 2,78] no ciclo 2 (p
> de Holm 0,003). Como ler: entre duas vagas parecidas da mesma UF, a de bolsa R$ 5 mil maior tem 1,47 vez a chance
> de ser a 1ª opção; no logit condicional, é a razão entre as probabilidades de escolher uma e a outra. Em km: dentro
> da mesma UF, +R$ 5 mil pesam como 75 km [28; 122] a menos de distância nos ciclos 1–3 e 117 km [56; 178] no ciclo
> 2. Sem fixar a UF (modelo base; a especificação pré-registrada é a dos ciclos 1–3): 1,25 [0,98; 1,61], IC que
> contém 1 (p 0,072; família de um teste, Holm = p), e 1,79 [1,19; 2,68] no ciclo 2. Com o score bootstrap para
> poucos grupos, o VL-1 se mantém (doc 57x). Escolha não é expansão: o que uma vaga ganha, outra do mesmo curso perde.
> Pacote do corte; condicional a se candidatar.

---

# Robustez

## Robustez: sempre comparando vagas da mesma UF

`Robustez · mesma UF`

<!-- layout: curto_figura -->
<!-- linhas: 3 -->

![Robustez dentro da mesma UF: razão de chances da 1ª opção por +R$ 5 mil no VL-1, com a distância em log, com a região de saúde de origem × UF da vaga e só com vagas perto do corte (ciclos 1–3); à direita, o VL-1 em cada ciclo](../../../output/apresentacao_banca2/curto_robustez_escolha.png)

- **Mantém:** log da distância; região × UF; score bootstrap (p 0,011).
- **Por ciclo:** forte só no ciclo 2; nos ciclos 1 e 3 o IC contém 1.
- **Perto do corte:** inconclusivo.

**Fontes:** `output/rdd_bolsa/VL_estimativas.csv` (adendo 52e; doc 57x; auditoria 48); `output/rdd_bolsa/VG_estimativas.csv` (adendo 52g; doc 57z; auditoria pendente); `output/apresentacao_banca2/curto_robustez_escolha.png`.

**Números:** `VL1_EMP_RC`, `VL1_EMP_RCI`, `VL1_EMP_RCS`, `VL1_C2_RC`, `VL1_C2_RCI`, `VL1_C2_RCS`, `VLLOG_EMP_RC`, `VLLOG_EMP_RCI`, `VLLOG_EMP_RCS`, `VLLOG_C2_RC`, `VLLOG_C2_RCI`, `VLLOG_C2_RCS`, `VL3_EMP_RC`, `VL3_EMP_RCI`, `VL3_EMP_RCS`, `VL3_C2_RC`, `VL3_C2_RCI`, `VL3_C2_RCS`, `VL2_EMP_RC`, `VL2_EMP_RCI`, `VL2_EMP_RCS`, `VL2_EMP_HOLM`, `VG1_RC`, `VG1_RCI`, `VG1_RCS`, `VG1_NCONJ`, `VG3_RC`, `VG3_RCI`, `VG3_RCS`, `VG3_NCONJ`, `VL1_EMP_PSR`, `VL1_C2_PSR`

> **Roteiro (40 s).** A robustez fica sempre dentro da mesma UF. À esquerda, o peso da bolsa se mantém com a
> distância em log e com a região de saúde de origem no lugar da UF de origem. Com poucos grupos, o p do score
> bootstrap continua 0,011. Só com vagas perto do corte, o
> intervalo contém 1: inconclusivo. À direita, ciclo a ciclo: o efeito é forte só no ciclo 2; nos ciclos 1 e 3, o
> intervalo contém 1. Por que o ciclo 2? Não sabemos.

> **Notas do apresentador.** Todas as variantes comparam vagas da mesma UF. Ciclos 1–3 (adendo 52e; doc 57x;
> auditoria 48): VL-1, 1,47 [1,15; 1,89]; com a distância em log, 1,45 [1,15; 1,83] (ciclo 2: 1,75 [1,23; 2,49]); com
> o efeito fixo de região de saúde de origem × UF da vaga (VL-3), 1,49 [1,15; 1,92] (ciclo 2: 1,91 [1,33; 2,74]); só
> com vagas a até 0,050 de um corte (VL-2), 1,28 [0,95; 1,72], p de Holm 0,103: inconclusivo, a comparação local tem
> pouca informação. Inferência com poucos *clusters* (conjuntos de escolha): p do score bootstrap de Rademacher
> 0,011 nos ciclos 1–3 e 0,004 no ciclo 2, sem ajuste (doc 57x). Por ciclo, com o par de UFs fixado (adendo 52g; doc 57z; pós-resultado; auditoria pendente):
> ciclo 1, 1,15 [0,66; 2,01], com 16 conjuntos de escolha; ciclo 2, 1,90 [1,30; 2,78]; ciclo 3, 1,25 [0,90; 1,73], com
> 23 conjuntos. A leitura fixada no adendo antes de rodar: forte só no ciclo 2, como na especificação base. Os km dos
> ciclos 1 e 3 têm IC que contém zero e não são usados. Por que o ciclo 2, não sabemos (leituras candidatas, sem
> teste: informação sobre a grade, vagas por curso, parte de vagas imediatas; doc 57a). Tudo pós-resultado e
> condicional a se candidatar; pacote do corte.

---

# Discussão

## Conclusão: a bolsa maior aumenta a 1ª opção? Sim

`Discussão · Conclusão`

<!-- layout: curto_texto -->

- **Resposta** sim, comparando vagas da mesma UF: chance ×1,47
- **Força** forte só no ciclo 2 (×1,90)
- **Teoria** os dados sugerem: bolsa compensa parte do custo do lugar

**Fontes:** modelo da banca 1; doc 07 da banca 2; docs 57x e 57z; doc 66 (§9 e §10); auditorias 18, 48, 50 e 52.

**Números:** `VL1_EMP_RC`, `VL1_C2_RC`, `VL1_EMP_K5`

> **Roteiro (35 s).** Voltando à pergunta: a bolsa maior aumenta a chance de a vaga ser a 1ª opção, comparando vagas
> da mesma UF? Sim: 1,47 vez a chance nos três ciclos juntos, e forte só no ciclo 2. Pela teoria da banca 1, o médico
> aceita a vaga se a bolsa compensa o custo do lugar; os dados sugerem que R$ 5 mil compensam parte desse custo,
> cerca de 75 km a menos. Isso vale para a vaga que quem se candidatou marcou como 1ª opção, não para a
> entrada no município.

> **Notas do apresentador.** No modelo da banca 1, o médico aceita a vaga se a bolsa compensa o custo do lugar. O
> dado: comparando vagas da mesma UF, a vaga de bolsa maior tem mais chance de ser a 1ª opção. A leitura que os dados
> sugerem, sem teste direto: a bolsa compensa parte do custo do lugar, e R$ 5 mil valem cerca de 75 km a menos de
> distância na escolha. É interpretação, não teste (auditoria 50). Dá para afirmar: entre quem se
> candidatou, a vaga de bolsa maior é preferida a uma vaga parecida da mesma UF, com força só no ciclo 2 (nos ciclos 1 e 3, separados, o IC contém 1). Não dá para
> afirmar: que a bolsa causa mais médicos no município; nada sobre quem não se candidatou; que o efeito vale fora
> do pacote do corte. O contraste é o pacote do corte, não a participação no
> PMM-E. Próximos passos: a auditoria do adendo 52g, o ciclo 3 com a competência 202703 madura e
> o universo de inscritos.

---

## Limitações e o que cada uma implica

`Discussão · Limitações`

<!-- layout: curto_tabela -->

| Limitação | Implicação |
|---|---|
| Pós-resultado | exploratório |
| Sem fixar UF | IC contém 1 |
| Só inscrição | ≠ ida ao município |
| Pacote do corte | bolsa não isolada |
| Só ciclo 2 | não generalizar |
| Origem = CNES | ≠ residência |

**Fontes:** doc 66 (§0, §5 e §8); doc 07 da banca 2 (§3 e §4); docs 57p, 57x e 57z; auditorias 18, 48, 50 e 52.

**Números:** `VL1_EMP_RC`, `VL1_EMP_RCI`, `VL1_EMP_RCS`, `VL1_EMP_HOLM`, `VLB_EMP_RC`, `VLB_EMP_RCI`, `VLB_EMP_RCS`, `VC_B_HOLM`, `VG1_RC`, `VG1_RCI`, `VG1_RCS`, `VG3_RC`, `VG3_RCI`, `VG3_RCS`, `VC_DUF_EST`, `VC_DUF_INF`, `VC_DUF_SUP`

> **Roteiro (45 s).** Seis limitações e o que cada uma implica. A especificação é pós-resultado: o resultado é
> exploratório e pede dados novos. Sem fixar a UF, como no pré-registrado, o intervalo contém 1. Só vemos a
> inscrição: quem se candidatou e o que marcou, não quem entrou no município. O contraste é o pacote do corte: vale para o pacote, não
> para os R$ 5 mil sozinhos. O efeito é forte só no ciclo 2: não dá para generalizar. E a origem é o vínculo no CNES,
> não a residência. Obrigado.

> **Notas do apresentador.** Implicações, com mais detalhe. Pós-resultado: a hipótese e a especificação com o par de
> UFs vieram depois dos coeficientes do modelo base; o resultado é exploratório e só vira confirmatório com um
> protocolo congelado aplicado a dados novos (o universo de inscritos, novos ciclos). Sem fixar a UF: a especificação
> pré-registrada (P1a) dá 1,25 [0,98; 1,61], IC que contém 1 (p 0,072; família de um teste, Holm = p). Condicional a
> se candidatar: sem a margem extensiva, nada aqui diz quantos especialistas a mais se inscreveriam com bolsa maior;
> e o que uma vaga ganha na escolha, outra do mesmo curso perde. Pacote do corte: nos mesmos cortes
> mudam outras regras federais (auditoria 18); a implicação de política vale para o pacote, não para os R$ 5 mil
> sozinhos. Só inscrição: a 1ª opção é a vaga marcada na inscrição; não medimos alocação, posse nem trabalho no
> município. Só ciclo 2: comparando vagas da mesma UF, ciclo a ciclo (adendo 52g), 1,15 [0,66; 2,01] no
> ciclo 1 e 1,25 [0,90; 1,73] no ciclo 3, IC que contêm 1; não generalizar para o programa. Origem = vínculo no CNES: quem trabalha longe de casa aparece com a origem do trabalho; ela só define o
> par de UFs que fica fixo. Perguntas prováveis da banca (doc 66, §8). P1, "Vocês formularam a hipótese depois de ver
> os resultados?" Sim, e está na tela do slide 1; a especificação com o par de UFs foi congelada antes de rodar (52e;
> auditoria 48), mas depois de ver o modelo base. P2, "Se o pré-registrado tem IC que contém 1, por que acreditar?"
> Porque, comparando vagas da mesma UF, o efeito é 1,47 [1,15; 1,89], p de Holm 0,005, e se mantém com o score
> bootstrap; mas é exploratório. P3, "Isso é a bolsa ou o pacote?" O pacote do corte: nos mesmos cortes mudam outras
> regras federais (auditoria 18); em 0,300 nenhum outro incentivo individual ao especialista do PMM-E muda
> (auditoria 35); em 0,400 fica aberta a ajuda de custo do PMMB; nos dois cortes, o serviço do município pode mudar. P4, "E a
> origem?" Não é a pergunta desta hipótese: a UF de origem é controle. Se insistirem: no modelo base, sem fixar a UF,
> o teste origem × toda a bolsa (D_UF) dá 1,94 [1,48; 2,40] em log-chance (doc 57p); não é interpretado aqui.

<!-- deck:fim -->

<!-- apendice:fim -->
