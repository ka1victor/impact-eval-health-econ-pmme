# 63. Registro: possíveis explicações para o sinal da H1 e controles candidatos

> **Pedido do autor (26/10/2026):** "vai vendo tudo que temos de possível
> explicação para a H1 e anotando para colocar como controle, por exemplo
> UF".<br>
> **Estatuto:** registro vivo. **Não é protocolo.** Lista as explicações já
> levantadas, a evidência de cada uma e como ela entraria como controle. Para
> rodar a H1 com um conjunto de controles, é preciso antes congelar um adendo
> que fixe o conjunto (RDD com covariáveis à CCFT 2019, que exige covariáveis
> pré-determinadas). Este registro é a lista de onde o adendo vai escolher.<br>
> **Regra para entrar como controle:** a variável tem de ser **anterior ao
> tratamento e à escolha** (pré-determinada). Variável que pode responder ao
> corte ou ao resultado entra só como diagnóstico, nunca como controle da
> principal.

## 1. Tabela

| # | Explicação | Evidência até agora | Variável de controle | Pré-determinada? | Estado |
|---|---|---|---|---|---|
| 1 | **Capitais logo abaixo de 0,300** (São Paulo, Goiânia, Natal, Brasília a menos de 0,010; nenhuma acima) | com uma dummy de capital, a queda encolhe e o IC contém zero (auditoria 36) | dummy de capital | sim | em teste formal (adendo 48c) |
| 2 | **Região e UF**: o Nordeste se concentra nos últimos 0,050 antes de 0,300 e preenche mais | dentro da mesma UF, a subida da faixa de R$ 10 mil quase some; na janela sai 40% (auditoria 37) | efeito fixo de UF; ou de macrorregião | sim | em teste formal (48c, efeito fixo de UF) |
| 3 | **Porte do município** (cidades grandes abrem e preenchem mais; em 0,400, três grandes logo abaixo do corte) | em 0,400, com o controle das vagas oferecidas, a queda some (doc 49b) | log(população 2022) | sim | a incluir |
| 4 | **Hierarquia urbana** (REGIC) | no diagnóstico 61 não saltou no corte nem reduziu a queda (doc 57l) | categorias do REGIC 2018 | sim | testado; fraco |
| 5 | **Tipo de vaga** (imediata, mista, só de reserva) | comparando só vagas imediatas, a célula preenchida em 0,300 vai de −8,4 a −3,7 p.p. (57n) | tipo de célula do **quadro de 13/02** no ciclo 2 (48b, §7) | anterior à alocação só com o quadro de 13/02 no ciclo 2; **mas pode responder ao corte** (ver 14) | já é a principal (48b) |
| 6 | **Curso** (cursos que preenchem pouco em qualquer lugar) | o índice de curso salta no corte em 0,300 (57l) | efeito fixo de curso × ciclo | sim | já no A3 e no HI-1; a incluir no HI-2 (por município, a parte de cada curso nas vagas) |
| 7 | **Concorrência** (mais células do mesmo curso na mesma UF) | entre os fatores que mais reduzem a queda (57l) | nº de células do mesmo curso e ciclo na UF ou região de saúde | **depende**: o quadro é decidido pelo Ministério e pode responder ao corte | só diagnóstico |
| 8 | **Candidatos por perto** (oferta de médicos da região) | tira 44% da subida na janela antes de 0,300 (auditoria 37); não salta no corte (57l) | candidatos do curso com origem na UF ou região, ou especialistas pré no CNES por 10 mil hab. (202406–202506) | os especialistas pré no CNES, sim; candidatos, **não** (é escolha) | especialistas pré: a incluir; candidatos: só diagnóstico |
| 9 | **Vagas oferecidas** (o controle do S-a) | em 0,400 explica a queda (49b) | vagas imediatas pré-alocação | **duvidosa**: o quadro pode responder ao corte (protocolo 48, §2) | já na HI-2; manter com a ressalva |
| 10 | **Ciclo** (o sinal varia por ciclo) | a taxa por vaga em 0,300 cai mais no ciclo 2 | efeito fixo de ciclo e parâmetros por ciclo | sim | já incluído |
| 11 | **Outras políticas no mesmo corte** (estrato da atenção primária, emendas +20%, PMMB) | sem teste causal; o estrato da atenção primária só muda para portes 2 e 3 em 0,300 (auditoria 18) | porte × lado (heterogeneidade: onde o estrato muda e onde não) | sim | proposto ao autor; sem protocolo |
| 12 | **Definição de "preenchida" diferente no ciclo 1** (confirmação ou homologação) | HI-1 usa ≥ 1 alocado; a F1.3 entra como sensibilidade (57n) | definição única | — | resolvido no 48b |
| 13 | **Acaso / poucos municípios** | cortes placebo e randomização local não descartam (57l) | — | — | relatar |
| 14 | **Seleção pelo tipo de vaga** (26/10/2026, pergunta do autor): a SGTES decide qual município recebe vaga imediata e qual fica na reserva, com critério que não está nos dados; se o tipo responde ao corte, restringir às vagas imediatas (48b) compara grupos selecionados de forma diferente | o tipo salta no corte: parte de células só de reserva +15,4 p.p. [+2,1; +28,6] em 0,300 e +11,3 p.p. em 0,400 (57l, descritivo) | nenhuma: o tipo **não** é pré-determinado em relação ao corte, logo não entra como controle | **não** (decidido pelo Ministério, possivelmente olhando a faixa) | aberto: limites de Lee, "ter vaga imediata" como outcome e balanço dentro da amostra imediata (`docs/07_apresentacoes/banca2/05_discussao_historia_empirica.md`, §2.12); precisa de adendo congelado |

## 2. Próximo passo proposto

Quando o adendo 48c (capitais e UF) e a auditoria 38 (48b) saírem, congelar um
adendo "H1 com covariáveis pré-determinadas", com o conjunto fixado antes de
rodar:
- capital;
- efeito fixo de UF;
- log(população);
- especialistas pré por 10 mil hab.;
- composição de curso.

Ele roda HI-1 e HI-2 por corte e relata cada covariável isolada e todas juntas.
Concorrência, candidatos e vagas oferecidas ficam fora do conjunto, porque não
são pré-determinados, e aparecem só como diagnóstico.

## 3. Controles que a literatura e o problema sugerem (atualização de 26/10/2026)

Pedido do autor: pensar em controles que **já se sabe** que afetam a propensão
do médico a atuar no município, como a presença de médicos na região. Todos
precisam ser medidos **antes do programa** (até 202506). Situação dos dados:
- **no repo:** já adquirido e auditado;
- **adquirir:** fonte pública ainda não baixada.

| Grupo | Controle | Por que importa | Fonte | Situação |
|---|---|---|---|---|
| Mercado de médicos | médicos por 10 mil hab. no município (todos) | densidade médica atrai e retém (rede, cobertura) | CNES nacional (a09), 202406–202506 | no repo |
| | especialistas das CBO do curso por 10 mil hab. no município e na região de saúde | concorrência e rede da especialidade; também "médicos por perto" | a09 + ponte curso–CBO | no repo |
| | generalistas do PMMB e da atenção primária no município | outra política no mesmo corte; carga e rede da atenção primária | a09 (CBO de eSF) | no repo |
| Estrutura de trabalho | estabelecimentos com leitos, centro cirúrgico, UTI; leitos por 10 mil hab. | o especialista precisa de estrutura (custo laboral do modelo, Choné e Ma) | CNES (tabelas de estabelecimento e leito) | verificar se o a05/a09 trouxe essas tabelas; senão, adquirir |
| | produção especializada pré (SIA e SIH) por 10 mil hab. | demanda e estrutura já existentes | SIA e SIH (a12–a13), 202406–202506 | no repo |
| Formação | escola médica e programa de residência na região de saúde ou na UF | onde o médico se forma e faz residência explica onde ele fica | e-MEC e CNRM | adquirir |
| Mercado privado | beneficiários de plano de saúde por habitante | renda privada complementar (as 20 h da bolsa são cumuláveis) | ANS (beneficiários por município) | adquirir; a TISS (a14) dá só um proxy de produção |
| Lugar | porte (log pop. 2022), capital, metrópole, REGIC, distância à capital | amenidades, carreira e família (custo geográfico do modelo) | Censo 2022; IBGE território; REGIC 2018 | no repo |
| | UF e região de saúde | diferenças regionais estáveis (Nordeste preenche mais) | malha de regiões de saúde | no repo |
| Renda e fisco | PIB per capita; receita corrente municipal per capita | capacidade de complementar salário e pagar estrutura | IBGE PIB municipal; SICONFI | adquirir. Atenção: correlacionados com o IVS; só como controle, nunca no lugar da running variable (`CLAUDE.md`) |
| Violência | taxa de homicídios | amenidade negativa forte | SIM/DATASUS | adquirir |

**Regras:**
- Esses controles entram no adendo "H1 com covariáveis pré-determinadas"
  (seção 2) **só depois de congelados**, com o conjunto fixado antes de rodar.
- Cada controle é relatado isolado e todos juntos.
- Antes de usar como controle, cada um passa por um teste de balanço no corte:
  se saltar no corte, também é explicação candidata.
- Os itens "adquirir" precisam de script de aquisição com manifesto e hash,
  como os a0x.

**26/10/2026:** o conjunto de localização (capital, macrorregião, log da população) e de médicos na região (médicos e especialistas por 10 mil hab. no município e no resto da região de saúde) foi congelado no adendo [`48d`](48d_adendo_controles_localizacao_e_medicos.md), com pareamento perto do corte. Escola médica, ANS, PIB e receita, homicídios e leitos continuam fora até serem adquiridos.

**26/10/2026, resultados do 48d (doc 57r; auditoria 40, aprovado com correções):** no balanço do corte, em 0,300
o lado de bolsa maior tem menos capitais, menos municípios do Nordeste e mais especialistas no resto da região de
saúde; em 0,400, só os especialistas no resto da região diferem (mais do lado de bolsa maior). Com localização e
médicos na regressão, o HI-2 em 0,300 deixa de excluir zero, e o código aplica a leitura "anda junto com localização
ou médicos": é limite da RDD nesse corte, não prova de que a localização explica a queda. O PSM em 0,300 não detecta
diferença na H1 nem na oferta local; em 0,400 não tem estimativa (capitais, Sul e, na H1, Centro-Oeste só do lado
de baixo; o logit não converge). Números no doc 57r.
Explicações 1, 2 e 8 da tabela ganham apoio; "especialistas no resto da região" entra como explicação nova.

Este registro é atualizado a cada explicação nova, com data.
