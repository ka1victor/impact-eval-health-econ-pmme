# 01 — Diagrama causal (teoria da mudança) e nova ordem dos slides de teoria

> **Pedido do grupo (26/10/2026):** incluir diagrama causal/teoria da mudança
> para explicar melhor a teoria econômica, e deixar o slide de equações como
> apêndice.<br>
> **Estatuto:** conteúdo canônico da proposta. O `.pptx` é derivado: divergência
> entre deck e este documento é erro do deck (`CLAUDE.md`).<br>
> **Natureza:** teoria e hipótese. Nenhum número de resultado. Os únicos
> números exibidos são a regra da bolsa (cortes do IVS e valores em R$), os
> anos das citações e a numeração dos passos.<br>
> **Fontes de conteúdo:** [`02_teoria/modelo_micro.md`](../../02_teoria/modelo_micro.md);
> [`06_execucao/51`](../../06_execucao/51_plano_perguntas_reformuladas.md), §1;
> [`banca2/04_plano_entrega_empirica.md`](../banca2/04_plano_entrega_empirica.md), §3–§4;
> [`auditorias/16`](../../auditorias/16_ivs_2010_oficial_e_arquivo_local.md) (regra aplicada);
> [`auditorias/18`](../../auditorias/18_politicas_nos_mesmos_cortes_ivs.md) (outras políticas nos cortes).

## 1. Como ler o diagrama

São dois slides.

- **Slide A (seção Literatura): a cadeia.** Da regra à saúde, em três blocos:
  1. **Regra.** O IVS 2010 oficial define a faixa da bolsa: até 0,300, R$ 10 mil;
     de 0,301 a 0,400, R$ 15 mil; acima de 0,400, R$ 20 mil.
  2. **Escolha do médico.** A bolsa eleva o salário esperado, E(w | B). O custo
     de viver ali (geográfico) e o custo de trabalhar ali (laboral) puxam contra.
     O saldo é o valor da vaga.
  3. **Da vaga à saúde.** O valor da vaga define a parcela de médicos que a
     escolhe (π). A agregação leva à chance de a vaga ser preenchida. Depois vêm
     os elos da política: capacidade, produção e acesso, saúde.
- **Slide B (seção Hipótese): a hipótese e os pontos fracos.** A mesma cadeia em
  sete passos (0 a 6, como no doc 51, §1). O passo 2 é o **único em que a bolsa
  age diretamente**. Três marcas dizem onde a leitura é frágil:
  - **A**, outras políticas nos mesmos cortes de IVS;
  - **B**, abertura de vagas decidida antes da escolha;
  - **C**, substituição.

A faixa verde do topo do slide B repete a hipótese que o deck do grupo já
exibia no slide "Da condição de aceitação, sai nossa hipótese econômica", que
vai para o apêndice. Sem o slide B, a seção Hipótese ficaria sem a hipótese.

> [!NOTE]
> A escolha da hipótese central (manter H1 ou adotar H3, com H2 e H1 na cadeia)
> continua sendo do autor ([`banca2/04`](../banca2/04_plano_entrega_empirica.md),
> §3 e §8). O slide B mostra a hipótese **como o grupo a escreveu**. Se o autor
> adotar outra, só a faixa do topo e o colchete dos passos 2 e 3 mudam; a cadeia
> e os avisos não.

## 2. Caixas e setas (bloco gerado)

O texto exibido em cada caixa vem das constantes do script. Este bloco é
regravado com `--atualizar-doc` e conferido por `tests/test_diagrama_banca_final.py`.

<!-- banca_final:caixas:inicio -->
<!-- Bloco gerado por scripts/apresentacao/gerar_diagrama_banca_final.py --atualizar-doc. Não editar à mão. -->

#### Slide A — Da regra da bolsa à saúde: teoria da mudança

| Caixa | Papel | Pílula | Título exibido | Texto exibido | Fonte exibida na caixa | Equações no apêndice (título do slide) |
|:---:|---|---|---|---|---|---|
| A1 | regra | — | IVS 2010 oficial | Vulnerabilidade social do município. | IPEA, ATLAS IVS | — (regra; sem equação) |
| A2 | regra | — | Faixa da bolsa | Cortes do IVS em 0,300 e 0,400. | — | — (regra; sem equação) |
| A3 | forca_a_favor | ELEVA O VALOR | A bolsa eleva o salário esperado | E(w \| B) sobe com a faixa. Rende mais onde a vida é barata. | MOEHLING et al. (2020) | A escolha locacional maximiza a utilidade; A escolha locacional maximiza a renda real líquida |
| A4 | forca_contra | REDUZ O VALOR | Custo de viver ali (geográfico) | Moradia, deslocamento, amenidades e distância da origem. | REDDING & ROSSI-HANSBERG (2017) | Literatura divide o custo em dois tipos: geográfico e laboral |
| A5 | forca_contra | REDUZ O VALOR | Custo de trabalhar ali (laboral) | Equipe, capital, esforço e altruísmo do médico. | CHONÉ & MA (2011) | Literatura divide o custo em dois tipos: geográfico e laboral |
| A6 | valor | — | Valor da vaga para o médico | Valor presente da renda real menos o custo do lugar. | MOEHLING et al. (2020) | A escolha locacional maximiza a utilidade; Da condição de aceitação, sai nossa hipótese econômica |
| A7 | agregacao | — | Parcela de médicos que a escolhe (π) | Médicos diferem em curso, vínculos e preferências. | BURDETT, SHI & WRIGHT (2001) | Da escolha individual ao preenchimento agregado |
| A8 | agregacao | — | Vaga preenchida | Chance de a vaga receber ao menos um médico. | BURDETT, SHI & WRIGHT (2001) | Da escolha individual ao preenchimento agregado |
| A9 | politica | — | Capacidade | Vínculos e horas de especialistas. | — | — (elo da política; sem equação do modelo) |
| A10 | politica | — | Produção e acesso | Consultas, exames e cirurgias. | — | — (elo da política; sem equação do modelo) |
| A11 | politica | — | Saúde | Espera e internações dos moradores. | — | — (elo da política; sem equação do modelo) |

Chips da faixa (dentro de A2): até 0,300 → R$ 10 mil; 0,301 a 0,400 → R$ 15 mil; acima de 0,400 → R$ 20 mil.

Rótulos de faixa: 1 REGRA; 2 ESCOLHA DO MÉDICO; 3 DA VAGA À SAÚDE. Rótulos de grupo: AGREGAÇÃO · BURDETT, SHI & WRIGHT (2001); ELOS DA POLÍTICA: DO PROVIMENTO À SAÚDE.

| Seta | O que ela diz | Literatura |
|:---:|---|---|
| A1 → A2 | o IVS decide a faixa | regra aplicada (auditoria 16) |
| A2 → A3 | a faixa soma R$ à remuneração esperada | Moehling et al. (2020) |
| A3 → A6 | mais renda real eleva o valor da vaga | Moehling et al. (2020) |
| A4 → A6 | custo de viver ali reduz o valor da vaga | Redding & Rossi-Hansberg (2017) |
| A5 → A6 | custo de trabalhar ali reduz o valor da vaga | Choné & Ma (2011) |
| A6 → A7 | quanto maior o valor, maior a parcela de médicos que escolhe a vaga | Moehling et al. (2020); Burdett, Shi & Wright (2001) |
| A7 → A8 | quanto maior a parcela, maior a chance de a vaga ser preenchida | Burdett, Shi & Wright (2001) |
| A8 → A9 | vaga preenchida vira médico no serviço (provimento) | teoria da mudança do programa (doc 51, §1) |
| A9 → A10 | mais capacidade permite mais produção e acesso | teoria da mudança do programa (doc 51, §1) |
| A10 → A11 | mais acesso, melhor a saúde dos moradores | teoria da mudança do programa (doc 51, §1) |

#### Slide B — A hipótese e onde a identificação é fraca

Faixa da hipótese (HIPÓTESE): Municípios com maior remuneração oferecida pelo PMM-E têm maior probabilidade de preenchimento de vagas.

| Passo | Caixa | Título exibido | Texto exibido | Aviso |
|:---:|:---:|---|---|:---:|
| 0 | B1 | Regra | IVS 2010 define a faixa da bolsa. | A |
| 1 | B2 | Abertura de vagas | Gestor propõe, SGTES decide. | B |
| 2 | B3 | Escolha do médico (destaque: A BOLSA AGE AQUI) | Valor da vaga define quem a escolhe. | — |
| 3 | B4 | Vaga preenchida | Ao menos um médico a escolhe. | — |
| 4 | B5 | Capacidade | Vínculos e horas de especialistas. | C |
| 5 | B6 | Produção e acesso | Consultas, exames e cirurgias. | — |
| 6 | B7 | Saúde | Espera e internações dos moradores. | — |

Colchete sob os passos 2 e 3: HIPÓTESE: BOLSA → PREENCHIMENTO. Etiqueta sobre o passo 2: A BOLSA AGE AQUI.

Cabeçalho dos avisos: ONDE A LEITURA É FRÁGIL.

| Aviso | Caixa marcada | Título exibido | Texto exibido | Base |
|:---:|:---:|---|---|---|
| A | B1 | Outras políticas nos mesmos cortes | Em 0,300 e 0,400 mudam também outras regras federais. O salto mede um pacote, não só a bolsa. | auditoria 18 |
| B | B2 | A vaga abre antes da escolha | O gestor propõe e a SGTES prioriza, sem fórmula publicada. Contar vagas preenchidas mistura abrir com atrair. | doc 51, §1 |
| C | B5 | Substituição | Parte dos médicos já estava no município. Chegada pode ser troca de vínculo, não oferta nova. | doc 51, §1 (passo 4) |

Faixa final: O que o corte identifica: o incentivo marginal de R$ 5 mil, dentro de um pacote de regras. Não é participação no PMM-E nem o efeito do Agora Tem Especialistas.

Nota do slide A: Diagrama teórico: as setas dizem o que o modelo prevê, não o que foi estimado.

<!-- banca_final:caixas:fim -->

## 3. Literatura de cada elo

| Elo | O que a literatura fornece | Referência | Onde está no repositório |
|---|---|---|---|
| A3, A6: bolsa → salário esperado → valor da vaga | escolha locacional intertemporal: o médico maximiza o valor presente do rendimento real menos um custo locacional não pecuniário; a bolsa entra em E(w \| B) | Moehling, Niemesh, Thomasson & Treber (2020), eq. 1, p. 184 | [`modelo_micro.md`](../../02_teoria/modelo_micro.md), §1 e §3 |
| A4: custo de viver ali (geográfico) | custo espacial: moradia, deslocamento, amenidades; distância da cidade da família | Redding & Rossi-Hansberg (2017), eq. 24, p. 28; Moehling et al. (2020), p. 184 | `modelo_micro.md`, §2.1 e §3.2 |
| A5: custo de trabalhar ali (laboral) | desutilidade líquida de atender: esforço que cai com equipe (L) e capital (K), compensado pelo altruísmo (α) | Choné & Ma (2011), eq. 1, p. 232; Reinhardt (1972, 1975) | `modelo_micro.md`, §2.2, §2.3 e §3.2 |
| A6 → A7: valor da vaga → parcela que a escolhe | cada médico escolhe a oferta de maior valor; médicos diferem, e π é a parcela que prefere a vaga | Moehling et al. (2020) para a escolha; Burdett, Shi & Wright (2001) para a agregação | deck do grupo (slides de agregação); [`banca2/04`](../banca2/04_plano_entrega_empirica.md), §3–§4 |
| A7 → A8: parcela → vaga preenchida | a vaga é preenchida se ao menos um médico a escolhe; simplificação binomial (escolhas independentes), não equação estimada | Burdett, Shi & Wright (2001) | idem |
| A8 → A9 → A10 → A11: capacidade, produção e acesso, saúde | elos da teoria da mudança do programa, não do modelo de escolha; cada elo tem desenho e fonte próprios | doc 51, §1 | [`06_execucao/51`](../../06_execucao/51_plano_perguntas_reformuladas.md), §1 |
| A1 → A2: IVS → faixa | regra aplicada, com cortes em 0,300 e 0,400 (limite na classe de baixo) | auditoria 16, §2 | [`auditorias/16`](../../auditorias/16_ivs_2010_oficial_e_arquivo_local.md) |

> [!WARNING]
> Burdett, Shi & Wright (2001) está no deck do grupo e no doc `banca2/04`, mas
> **não consta na seção 5 (referências) de `modelo_micro.md`**. A referência
> completa precisa entrar lá antes da banca final.

## 4. Onde cada equação do apêndice se liga ao diagrama

As equações saem do corpo da apresentação e ficam nos slides do apêndice. A
tabela diz qual caixa cada slide de equação explica.

| Slide do apêndice (título no deck do grupo) | Equação | Caixas do diagrama que ela explica |
|---|---|---|
| O modelo combina três elementos da teoria | quadro das três literaturas; Pr(Y = 1) = 1 − (1 − π)^N | A3 a A8 (resumo de quem fornece o quê) |
| A escolha locacional maximiza a utilidade | escolha m* = argmax do valor presente de E(w \| B)/p − c (Moehling et al., 2020, eq. 1) | A3 (E(w \| B)), A4 (p e amenidades), A5 (c laboral), A6 (valor da vaga) |
| A escolha locacional maximiza a renda real líquida | a mesma equação, com a leitura em palavras (versão que o grupo tinha ocultado) | A3 e A6 |
| Literatura divide o custo em dois tipos: geográfico e laboral | u = z·B·w / (κ·Q^(1−β)) (Redding & Rossi-Hansberg); U = R − C(q; L, K) + αB(q) (Choné & Ma) | A4 e A5 |
| Da escolha individual ao preenchimento agregado (duas versões, uma delas oculta) | m*, π = Pr(m* = m), Pr(Y = 1) = 1 − (1 − π)^N | A6 → A7 → A8 |
| Da condição de aceitação, sai nossa hipótese econômica | derivadas do valor em relação a E(w), p e c; texto da hipótese | A3, A4, A5 e a hipótese do slide B |

Cada caixa remete ao apêndice pela coluna "Equações no apêndice" do bloco da
seção 2. As caixas A1, A2 e A9 a A11 não têm equação do modelo.

## 5. O que o diagrama marca como frágil ou como outra força

| Marca | Onde | Por que está no diagrama | Base |
|:---:|---|---|---|
| A | passo 0, regra | Em 0,300 e 0,400 mudam também outras regras federais (acréscimo de 20% no teto de emendas e de parcelas de custeio da MAC para IVS acima de 0,3; cofinanciamento da APS). Uma RDD em nível nesses cortes mede um **pacote**, não a bolsa pura | [`auditorias/18`](../../auditorias/18_politicas_nos_mesmos_cortes_ivs.md) |
| B | passo 1, abertura de vagas | O gestor propõe (CIB, capacidade no CNES) e a SGTES prioriza, antes da escolha, sem fórmula publicada. Contar vagas preenchidas mistura abrir com atrair. A bolsa só age no passo 2 | doc 51, §1 (passos 1 e 2) |
| C | passo 4, capacidade | Parte dos médicos já estava no município. Chegada pode ser troca de vínculo, não oferta nova. Expansão líquida se separa de substituição | doc 51, §1 (passo 4); `CLAUDE.md` |

A faixa final do slide B diz o que o contraste identifica, como pede o
`CLAUDE.md`: o incentivo marginal de R$ 5 mil, dentro de um pacote de regras;
não é participação no PMM-E nem o efeito total do Agora Tem Especialistas.

Vocabulário fixo: "curso" (não "especialidade") para as vagas; SGTES. A grade do
FAQ (R$ 20 mil só acima de 0,500) e a frase "IVS é o piso" vêm do arquivo de
IVS errado e **não** aparecem.

## 6. Nova ordem dos slides de teoria

Posições no deck do grupo recebido em 26/10/2026 (36 slides). Na proposta, o
deck passa a ter 38.

| Antes (posição, título) | Depois | Observação |
|---|---|---|
| 15, Sumário (Literatura) | 15 | igual |
| 16, O modelo combina três elementos da teoria | apêndice | equação Pr(Y = 1) |
| 17, A escolha locacional maximiza a utilidade | apêndice | equação de Moehling |
| 18, Da escolha individual ao preenchimento agregado | apêndice | equações de agregação |
| 19, A escolha locacional maximiza a renda real líquida (oculto) | apêndice, **visível** | o grupo o tinha ocultado; no apêndice passa a aparecer |
| 20, Literatura divide o custo em dois tipos (oculto) | apêndice, **visível** | idem; traz as equações de Redding & Rossi-Hansberg e de Choné & Ma |
| 21, Da escolha individual ao preenchimento agregado (oculto) | apêndice, **oculto** | versão anterior de 18, com "O que faz / Chega a"; fica oculta como estava |
| (novo) | **16, novo A:** Da regra da bolsa à saúde: teoria da mudança | seção Literatura |
| 22, Sumário (Hipótese) | 17 | igual |
| (novo) | **18, novo B:** A hipótese e onde a identificação é fraca | seção Hipótese; leva a hipótese do slide 23 |
| 23, Da condição de aceitação, sai nossa hipótese econômica | apêndice | equações das derivadas |
| 24 a 30, seções seguintes e Q&A | 19 a 25 | iguais |
| 31, Apêndice | 26 | divisor |
| (movidos) | 27 a 33: os sete slides de equações acima, na ordem original (16, 17, 18, 19, 20, 21, 23) | nenhum conteúdo perdido |
| 32 a 36 | 34 a 38 | exemplos e slides que já estavam depois do divisor |

Nenhum slide foi apagado nem editado; só mudaram de lugar, e dois deixaram de
estar ocultos. O número da página dos slides novos é campo automático. Os
números impressos à mão nos slides antigos do grupo (por exemplo "10", "13")
continuam como estavam e **não** batem com a nova posição: corrigir no deck, se
quiserem.

**Slides ocultos.** Os slides 19 e 20 estavam ocultos no deck do grupo (versões
anteriores, com rodapé antigo) e são os únicos com as equações de Redding &
Rossi-Hansberg e de Choné & Ma. No apêndice passam a aparecer. É escolha desta
proposta, não do grupo: para voltar, basta ocultá-los de novo.

## 7. Limites desta proposta

- **Equações do deck não conferidas aqui.** Os slides de equações foram só
  movidos. A conferência delas contra `modelo_micro.md` é do grupo.
- **Erros do deck que continuam**, listados em
  [`banca2/04`](../banca2/04_plano_entrega_empirica.md), §2: grade do FAQ nos
  slides 5 a 8, "177 dos 368", "SGETS", "especialidade", "proporção de vagas
  preenchidas". A proposta não os corrige: a tarefa era o diagrama e a ordem.
- **Montserrat.** O deck usa Montserrat. As imagens de conferência foram
  geradas com a fonte instalada na máquina de QA; o PowerPoint do grupo usa a
  fonte do próprio deck.
- **Sem ensaio.** O diagrama não passou por apresentação de ensaio.
