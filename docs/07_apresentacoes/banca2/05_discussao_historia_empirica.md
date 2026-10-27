# Discussão da história empírica (perguntas do autor de 26/10/2026)

> **Finalidade:** registrar as perguntas do autor sobre a parte empírica, as
> respostas dadas e as decisões de apresentação. Isto alimenta a sequência de
> slides da "história" da banca 2.<br>
> **Números:** cada resposta aponta a seção do documento gerado onde o número
> está (docs 49, 49b, 57, 57a, 57d, 57e, 57i, 57j, 57k), conferido por teste
> contra `output/`. Fora disso aparecem parâmetros (cortes, valores da bolsa,
> margens e datas) e, nas seções 2.11 a 2.14, números de resultado copiados dos
> docs auditados (57d, 57k, 57l, 57q, 57t e auditoria 36). **Esses números não
> são conferidos por teste**; a auditoria 49 conferiu um a um contra a fonte em
> 27/10/2026 (todos batem). Correção da auditoria 49: a versão anterior dizia
> que este documento não trazia número de resultado.<br>
> **Estatuto:** registro de discussão. Não muda protocolo nem resultado.

> [!NOTE]
> **Numeração da apresentação a partir de 26/10/2026:** H1 preenchimento; H2
> bolsa × origem (antes H3); H3 oferta (antes H4). Os nomes dos documentos de
> análise (P1h, P4, protocolos) não mudam. Abaixo, as seções escritas antes da troca usam a numeração antiga.
> O deck usado é o curto
> ([04](04_conteudo_deck_curto.md)), na estrutura do
> [06](06_estrutura_obrigatoria_versao_final.md).

> **Estado do branch em 26/10/2026 (retrato de trabalho em andamento).** O
> branch `claude/vigilant-mccarthy-dd92mc` contém commits marcados "WIP":
> - o deck em produção (`deck_banca2.pptx` e `deck_banca2_curto.*`), ainda não
>   revisado;
> - o diagnóstico 61 (`57l`, `DQ_*`), ainda não auditado;
> - a oferta local, protocolo 60 parte B (`57k`, `OL_*`), ainda não auditada.
>
> Servem para continuar o trabalho, não como resultado final: números e textos
> podem mudar até a auditoria. A `main` só recebe essas partes depois de
> revisadas.
>
> **Atualização de 27/10/2026 (auditoria 49).** O retrato acima está vencido: o
> diagnóstico 61 foi auditado (auditoria 33), a oferta local da parte B também
> (auditoria 34), e o deck curto foi auditado pela auditoria 49. A `main` está
> no commit `7e9f881`, igual ao branch.

## 1. Decisões de apresentação tomadas pelo autor

| Data | Decisão |
|---|---|
| 26/10/2026 | "Metodologia" na banca é a metodologia econométrica |
| 26/10/2026 | focar na parte empírica; reutilizar os slides prévios do grupo, corrigindo só o necessário |
| 26/10/2026 | o importante mas não central vai para o apêndice |
| 26/10/2026 | um único arquivo de deck (`output/apresentacao_banca2/deck_banca2.pptx`) |
| 26/10/2026 | menos espaço em branco; cada slide explica o que o número quer dizer |
| 26/10/2026 | **não mostrar o empilhado; mostrar o efeito de cada corte (0,300 e 0,400) separado** |
| 26/10/2026 | diagrama causal e equações no apêndice ficam para a banca final (`../banca_final/`) |
| 26/10/2026 | a história completa entra nos slides só depois de refinada e validada (protocolo 60 auditado) |
| 26/10/2026 | cada estimador ganha nos slides a sua especificação explicada (outcome, amostra, equação em palavras, o que é por ciclo, erro-padrão, leitura, cuidado, sensibilidades); a equação formal fica no apêndice |
| 26/10/2026 | a explicação da queda no corte 0,300 entra num slide próprio, logo depois do H1, com o diagnóstico do protocolo 61 |
| 26/10/2026 | **estrutura obrigatória da versão final:** Hipótese (uma só depois da validação; planos B em cinza), Dados, Análise descritiva, Metodologia, Identificação, Resultados, Robustez, Discussão ([`06`](06_estrutura_obrigatoria_versao_final.md)) |
| 26/10/2026 | **só as versões curtas são usadas**; as longas não precisam mais ser geradas (o deck completo fica como registro, sem atualização) |
| 26/10/2026 | **numeração da apresentação:** H1 preenchimento; H2 bolsa × origem (antes H3); H3 oferta (antes H4); a H2 antiga (escolha por ciclo) vira robustez da H2 |
| 26/10/2026 | **a candidata central é a H1 (preenchimento); H2 e H3 são plano B, em cinza** (correção do autor: a proposta anterior, com a H2 central, estava errada). Cada seção começa pela H1 e dá a ela o maior espaço; os slides da mesma hipótese ficam juntos, em sequência; H2 e H3 vão cortados ao mínimo, com "plano B" no título |
| 26/10/2026 | **auditoria 36:** sai a explicação "no ciclo 2, a vaga de reserva não podia ser preenchida na 1ª chamada" (errada: o quadro do ciclo 2 foi refeito depois do resultado); a queda em 0,300 passa a ser explicada em três ideias: dados crus iguais; a reta levada até o corte, puxada por capitais e Nordeste logo abaixo; controlando a capital, ou só com vagas imediatas, a queda encolhe |
| 26/10/2026 | **"texto demais":** no máximo cerca de 30 palavras visíveis por slide; especificação em até 4 linhas, com a equação em palavras no centro; o resto nas notas |
| 26/10/2026 | explicação da queda em 0,300 passo a passo, em Robustez: antes e depois do controle; a estimativa no corte; as vagas do lado de cima eram diferentes; o que dá para afirmar. Na Discussão, uma linha simples |
| 26/10/2026 | scatter IVS × preenchimento com as retas, em Análise descritiva; H1 por ciclo, em Robustez |
| 26/10/2026 | **H1 principal = adendo 48b** (só vagas imediatas: HI-1 e HI-2 por corte, com Holm); medidas antigas viram especificações secundárias |
| 26/10/2026 | **no máximo 14 slides** ("esses últimos decks tão muito grandes. pode deixar mais curtos mesmo, só com os principais slides, idealmente <15 slides"); o passo a passo da queda em 0,300 e o TOST em slide próprio saem, e o essencial vai para as notas ([06](06_estrutura_obrigatoria_versao_final.md), §2) |

## 2. Perguntas e respostas

### 2.1 Por que o sinal do preenchimento é negativo?

> [!WARNING]
> **Corrigido pela auditoria 36 (26/10/2026).** A explicação pelo cadastro
> reserva do ciclo 2, abaixo e na seção 2.11, está errada: o quadro do ciclo 2
> usado foi refeito depois do resultado preliminar, e a SGTES converteu vagas
> de reserva em imediatas onde houve alocado. O que acompanha a queda em 0,300
> (diagnóstico pós-resultado) são as capitais logo abaixo do corte; com uma
> dummy de capital, os intervalos passam a conter zero. Ver a auditoria 36 e o
> doc 04.

**Não é "a bolsa reduz o preenchimento".** Depois da correção por múltiplos
testes, nada se distingue de zero (doc 49, §3; doc 57, §3). O sinal vem de
coisas diferentes em cada corte (doc 49b, §3):

- **Corte 0,400: porte e oferta.**
  - Logo abaixo do corte, do lado de bolsa menor, estão alguns municípios
    grandes, que abrem e preenchem mais vagas.
  - Do lado de bolsa maior há, em média, menos vagas oferecidas, mas o salto
    das vagas oferecidas no corte não se distingue de zero.
  - Com o controle das vagas oferecidas, o salto do número de vagas preenchidas
    quase some. A taxa por vaga não salta.
- **Corte 0,300: a taxa por vaga oferecida cai.**
  - O porte não explica essa queda.
  - Cerca de metade dela vem do ciclo 2 (doc 49b, §14). Nesse ciclo, o lado de
    bolsa maior teve mais vagas de cadastro reserva. ~~E nenhuma célula só de
    reserva foi preenchida na 1ª chamada.~~ **Errado** (auditoria 36; corrigido
    no doc 49b em 26/10/2026): o zero de alocados nas células só de reserva vem
    do quadro de 19/03/2026, refeito depois do resultado preliminar; pelo quadro
    de 13/02/2026, vigente na inscrição, havia alocados do ciclo 2 em células só
    de reserva. Com esse quadro, mais reserva no denominador baixa a taxa por
    vaga oferecida, mas não explica a queda inteira.
  - O resultado depende da medida: contando só as vagas imediatas, ou dando o
    mesmo peso a cada município, o intervalo inclui zero (doc 49b, §6).
- **"A reta extrapola uma subida"** (doc 49b, §5 e §7):
  - A RDD ajusta uma reta de cada lado do corte e compara as duas retas no
    ponto do corte.
  - Do lado de bolsa menor, perto do corte, o preenchimento sobe à medida que o
    IVS se aproxima do corte, porque ali estão as cidades grandes. A reta desse
    lado segue essa subida e chega alta no corte.
  - Do lado de bolsa maior, a reta começa num nível normal.
  - O salto é a reta da direita menos a da esquerda, medidas no corte. Ele sai
    negativo mesmo quando a média bruta do lado de bolsa maior é igual ou
    maior. É uma propriedade da comparação local, não um erro, mas faz o
    resultado depender de poucas cidades perto do corte.
- **Empilhar os dois cortes** mistura dois fenômenos diferentes, porte em 0,400
  e taxa em 0,300. Por isso o autor decidiu mostrar cada corte separado.

### 2.2 Logo abaixo dos cortes há muito mais vagas abertas? O Ministério evitaria pagar R$ 5 mil a mais?

A hipótese do autor é que a direção do programa abriria mais vagas logo abaixo
do corte para pagar menos por municípios parecidos. Ela é plausível, mas os
dados só a apoiam em parte:

| Evidência | O que diz | Onde |
|---|---|---|
| Vagas oferecidas no corte 0,400 | menos vagas do lado de bolsa maior, em média; salto no corte com IC que inclui zero; a diferença vem sobretudo de três municípios grandes logo abaixo | doc 49b, §3 e §5 |
| Vagas oferecidas no corte 0,300 | sem diferença entre os lados | doc 49b, §3 |
| Vagas imediatas do ciclo 1 por habitante em 0,400 | menos do lado de bolsa maior, com IC que exclui zero, mas sem passar no BKY da família | doc 44, §5.4 |
| Cronologia do ciclo 1 | a adesão dos gestores (DOU de 12/06/2025) precedeu o anúncio da grade por faixa (DOU de 24/07/2025). O gestor não podia responder à bolsa; a SGTES, ao montar o quadro, podia | protocolo 48, §8 |
| Ciclo 3, onde pedido e priorização são observados | a priorização da SGTES não salta no corte; o IVS contínuo não se associa à priorização | doc 57e, T5.1 e T5.2 |
| Quadro dos ciclos 1 e 2, IVS contínuo | no ciclo 1, IVS maior anda junto com menos células, mantidas as outras características; no ciclo 2, não | doc 57e, T5.3 (descritivo) |

**Leitura.** Em 0,400 há menos vagas do lado de bolsa maior, mas isso se
explica sobretudo pelo porte de poucas cidades, e não aparece em 0,300. No
ciclo 3, o único em que se vê a decisão da SGTES, não há sinal de que ela
evite o lado de bolsa maior. A hipótese não foi testada formalmente nos ciclos
1 e 2, porque neles só se observa o quadro final.

**Como testar.** Uma RDD do número de vagas oferecidas por município, por ciclo
e por corte, com protocolo próprio congelado antes, e a leitura da priorização
do ciclo 3 por corte. É um item da fila (seção 4).

### 2.3 Que "ponto do ciclo 2" é esse? Só temos preenchimento do ciclo 1?

Temos preenchimento dos **três ciclos**:
- **1ª chamada:** ciclos 1, 2 e 3;
- **até a 2ª chamada:** ciclos 1 e 2.

O funil dos ciclos 2 e 3 foi reconstruído às cegas e entrou no E6 (doc 41a;
doc 38, D2). A tabela "os três ciclos em números" do deck mostra as contagens.

O "ponto do ciclo 2" é o diagnóstico do doc 49b, §14: no corte 0,300, cerca de
metade da queda da taxa por vaga oferecida vem do ciclo 2. A ligação com o
cadastro reserva que esta resposta fazia vinha do quadro de 19/03/2026, refeito
depois do resultado (auditoria 36; seção 2.1, corrigida). Na especificação
principal (adendo 48b, quadro de 13/02), a HI-1 em 0,300 cai sobretudo no ciclo
2, mas a HI-2 cai de tamanho parecido nos três ciclos; por ciclo, todos os IC
contêm zero (doc 57n, HI-s1).

### 2.4 E daí?

- **Para a política:** subir a bolsa em R$ 5 mil não é a alavanca que mais
  enche vaga. Pesam mais onde a vaga está, em relação à origem dos médicos
  (doc 57i), e quantas vagas o município abre.
- **Para o modelo do grupo:** é o "incentivo limitado". A política mexe em uma
  variável; o custo do lugar continua contra.
- **Para o desenho:** contar vagas mistura quem abriu vagas (gestor e SGTES)
  com quem escolheu. A escolha (H2 e H3) é a margem mais limpa.

### 2.5 Que dado é o "da origem do médico"? É causal?

**Fonte:** duas fontes públicas ligadas pelo portão G1
(`docs/auditorias/G1_viabilidade_candidatos.md`):
- as listas de classificação e resultado dos editais, com nome e CPF mascarado
  de todos os candidatos, inclusive os não alocados;
- o cadastro de profissionais do CNES, com CPF também mascarado.

**Ligação:** dígitos visíveis do CPF nas duas máscaras mais o nome, por regra
fixada antes de ligar. Os ambíguos ficam fora.

**Origem:** o município do estabelecimento em que o candidato tinha vínculo
médico no CNES na competência anterior às inscrições. Não é residência nem
naturalidade.

**Não é causal.** O peso da "UF de origem" no modelo de escolha é preferência
revelada: mistura família, rede, registro no conselho e clientela. A bolsa, essa
sim, é identificada pelo salto nos cortes.

### 2.6 Aumentaram as horas, mas não os especialistas no município?

São medidas diferentes:

| Medida | O que diz | Onde |
|---|---|---|
| Horas do próprio médico que entra no PMM-E | sobem depois da entrada (associação); metade já estava no município; parte do ganho no posto é compensada fora dele | doc 57d; doc 57h |
| Degrau da bolsa sobre os especialistas do município, nos cortes (DiRD) | nada detectado; é o efeito do R$ 5 mil, não da chegada | doc 43; doc 57 |
| Chegada do especialista sobre a oferta de especialistas do município, e deslocamento dos outros | protocolo 60, parte B | doc 57k |

### 2.7 Dá para dizer que não mudou nada? Como testar?

O teste é o de **equivalência** (TOST, protocolo 60, parte A; doc 57j;
auditoria 32): verificar se o IC de 90% cabe numa margem fixada antes.
- A3: ±10 p.p.
- N1: ±25% da média abaixo do corte.

**Resultado:**
- não há equivalência em nenhuma linha;
- nas linhas principais, só o teste do aumento rejeita.

**O que dá para dizer:** "não houve aumento do tamanho da margem ou mais", no
IC convencional, sob a aproximação local linear e para o pacote do corte. Uma
queda desse tamanho não fica descartada. Com o IC honesto, nem isso se sustenta.

**Não dá para dizer** "não mudou nada".

### 2.8 Metodologias e especificações

| Pergunta | Método | Especificação principal | Onde |
|---|---|---|---|
| A regra existe? | reprodução da faixa pelo IVS 2010 oficial | todos os municípios dos três ciclos | auditoria 16 |
| H1, preenchimento | RDD *sharp* local linear nos cortes 0,300 e 0,400 | h = 0,050, kernel triangular, reta por ciclo × corte, CR1 por município; Holm nas primárias; IC honesto; TOST | docs 49, 57j |
| Validade da RDD | densidade, balanço, placebos | IVS de 2010, anterior ao programa | docs 37, 41, 49 |
| Sinal negativo | diagnóstico oferta × taxa | por corte, por ciclo, retirada de municípios, troca de medida | doc 49b |
| H2 e H3, escolha | logit condicional da 1ª opção | bolsa linear; IVS em spline com nós nos cortes; distância e origem; cluster por conjunto de escolha; H3 como combinação linear unilateral | docs 57a, 57i |
| Robustez de H2 e H3 | variantes do logit | log da distância, efeito fixo de UF, por ciclo, explodido, misto, aninhado; placebos de corte | docs 57a, 42 |
| H4, horas do médico | Callaway–Sant'Anna no médico | ainda não tratados como controle; pré testado; Rambachan–Roth; comparação na nota de corte | docs 57d, 57h |
| H4, oferta local | Callaway–Sant'Anna no município × mês | vínculos e horas das CBO-alvo; teste de deslocamento | doc 57k |
| Produção | DiRD nos cortes e chegada | SUS e planos | docs 50, 57c |

### 2.9 E a 2ª opção? E a chance de ir de fato depois de ser alocado? Por que mais escolha e menos preenchimento?

- **Opções:** cada candidato lista no máximo duas opções, então não há 3ª. O
  logit "explodido", que usa a 1ª e a 2ª opção (M7), dá um peso da bolsa
  menor e não distinguível de zero (doc 57a, §4).
- **Depois da alocação:** o preenchimento do ciclo 1 já exige confirmação ou
  homologação. A presença do especialista ativo por célula (F2) não se
  distingue de zero nos cortes (doc 44). Não há estimativa direta de "ir de
  fato, dado alocado" por faixa da bolsa; é um ponto a acrescentar ao funil
  num protocolo próprio, depois do diagnóstico 61.
- **Os sinais opostos não se contradizem:**
  - **amostras diferentes:** o logit compara todas as vagas do mesmo curso e
    ciclo, com o IVS como curva suave; a RDD compara só municípios perto de
    cada corte;
  - **comparações diferentes:** o logit fixa a concorrência e mede a
    atratividade relativa da vaga; a RDD absorve tudo o que muda no corte
    (pacote de regras, composição das vagas, cadastro reserva, número de
    vagas por município);
  - **nenhum dos dois é firme:** o peso da bolsa na escolha encosta no zero, e
    o salto do preenchimento não passa no Holm.
  - **Atualização de 27/10/2026 (auditoria 49):** com a comparação só entre
    vagas da mesma UF, vistas por médicos da mesma UF de origem (adendo 52e,
    doc 57x, auditoria 48), o peso da bolsa na escolha passa a se distinguir de
    zero depois do Holm nos ciclos 1–3; perto do corte, não. No M1 com o quadro
    de 13/02 (doc 57p), continua sem rejeitar zero.

### 2.10 Já existe uma conexão entre H1 e H2/H3?

Existe uma ponte formal, a P1g (doc 57a, §9), que é leitura de consistência e
não teste:
- o modelo de escolha prevê quantos candidatos de 1ª opção a mais uma célula
  teria no corte se só a bolsa subisse um degrau, com o resto fixo;
- a RDD mede quantos a mais ela teve de fato.

O previsto é positivo e pequeno; o observado é negativo. Os dois intervalos
contêm zero e se sobrepõem.

**Leitura:** a escolha implica um efeito pequeno demais para aparecer no
preenchimento. O que se observa no corte é dominado pelo que muda além da
bolsa (seções 2.1 e 2.2). A H3 dá o porquê: a bolsa pesa pouco perto da origem.

A conexão empírica mais direta virá:
- do funil do diagnóstico 61 (D-c): a célula fica vazia por falta de
  candidato ou porque o candidato foi para outra?
- da concorrência (D-d).

### 2.11 Explicações da queda que têm apoio nos dados, e robustez a fazer

Resumo preliminar do diagnóstico 61 (doc 57l, em auditoria). Os números estão no
doc 57l e nas saídas `DQ_*`.

| Explicação | Em uma frase | Robustez já feita (protocolo 61) | Robustez a fazer |
|---|---|---|---|
| **1. É a reta, não os dados** | nos dados crus a fração preenchida é igual dos dois lados; a queda aparece quando a reta é levada até o corte | cortes falsos (grade do protocolo e grade maior, esta fora do protocolo); randomização local em ±0,010 e ±0,020 | janelas h = 0,030 e 0,080 para Q2 e Q3; reta quadrática; retirar um município por vez perto do corte; donut |
| **2. Vagas piores do lado de bolsa maior** | mais vagas só de cadastro reserva e de cursos que preenchem pouco em qualquer lugar | Q3 com efeitos fixos de composição; Q2 sem as células só de reserva | repetir por ciclo; índice de curso medido fora da amostra (outros ciclos); taxa só com as vagas imediatas |
| **3. Cadastro reserva no ciclo 2** | ~~no ciclo 2, a vaga de reserva não foi preenchida na 1ª chamada~~ **errado** (auditoria 36): o quadro do ciclo 2 usado no pipeline (19/03/2026) foi refeito depois do resultado preliminar, convertendo 630 vagas de reserva em imediatas; pelo quadro de 13/02/2026, 42% dos alocados do ciclo 2 estavam em células só de reserva. Ver seção 2.12 | ciclo 2 com e sem as células só de reserva | feito pelo adendo 48b (tipo de vaga do ciclo 2 pelo quadro de 13/02); a seleção pelo tipo de vaga foi testada no adendo 48f (seção 2.12, linha 2a) |
| **4. Porte em 0,400** | municípios grandes logo abaixo do corte abrem e preenchem muitas vagas | doc 49b: retirada dos maiores; controle das vagas oferecidas | o mesmo com log(população) e vagas oferecidas juntas; retirar um por vez |

Todas as linhas são descritivas e pós-resultado: medem o pacote do corte. A
robustez a fazer precisa de adendo datado ao protocolo 61 antes de rodar.

### 2.12 O que decide se a vaga é imediata ou de reserva não pode estar influenciando a H1?

Pergunta do autor, 26/10/2026. **Pode, e hoje está resolvido só pela metade.**
*(Atualização de 27/10/2026, auditoria 49: o canal 2 foi testado no adendo 48f;
ver a linha 2a.)*

**Quem decide o tipo.** A SGTES/MS monta o quadro de vagas. Pelo edital do
ciclo 1 (item 4.1.3.4), "considera-se em cadastro de reserva o município que,
na oferta inicial, não tinha vaga imediata, mas que poderá recebê-la por
remanejamento". **O critério com que o Ministério decide qual município recebe
vaga imediata e qual fica na reserva não está nos dados nem nos editais
arquivados.**

**Três canais pelos quais isso afeta a H1:**

| # | Canal | Evidência | Estado |
|---|---|---|---|
| 1 | **Composição:** o tipo salta no corte | acima de 0,300, a parte das células só de reserva é +15,4 p.p. maior (IC [+2,1; +28,6]); em 0,400, +11,3 p.p. (doc 57l, descritivo). **Atualização (26/10/2026, auditoria 44):** esse +15,4 usa o quadro do ciclo 2 de 19/03, refeito depois do resultado; com o quadro de 13/02 é +14,0 p.p. [−0,2; +28,3], e com efeitos fixos de curso × ciclo, +4,3 p.p. (doc 57t). Comparar todas as células mistura efeito com composição do quadro | tratado: o adendo 48b compara só vagas imediatas; em 0,300 a célula preenchida vai de −8,4 para −3,7 p.p. (IC contém zero) |
| 2 | **Seleção:** restringir às vagas imediatas condiciona numa variável que o Ministério pode ter decidido olhando o lado do corte (por exemplo, mais reserva onde a bolsa custa mais; **hipótese, sem evidência**) | se o tipo responde ao corte, os municípios com vaga imediata acima e abaixo não são comparáveis. A medida antiga mistura tipos; a nova pode comparar grupos selecionados de forma diferente. A verdade provavelmente fica entre as duas | testado (linha 2a) |
| 2a | **Resultado do teste (adendo 48f, doc 57t, auditoria 44)** | a chance de o município × ciclo ter vaga imediata não salta no corte (IC contém zero), mas em 0,400 as taxas diferem (66% abaixo, 53% acima) e em 0,300 o lado com mais vaga imediata troca entre ciclos; os limites de Lee, que não supõem como o Ministério escolheu o tipo (só monotonicidade dentro de cada ciclo), contêm zero nos dois cortes, para fração preenchida e alocados por vaga; com a reta (sensibilidade), os alocados em 0,300 ficam inteiramente abaixo de zero, com IC que contém zero | **feito**: a seleção pelo tipo de vaga não muda a conclusão da H1, com a ressalva de que, em 0,300, restringir a vagas imediatas piora o balanço (capital, Nordeste, especialistas na região) |
| 3 | **Conversão pós-resultado no ciclo 2:** 630 vagas de reserva viraram imediatas em 301 células depois do resultado preliminar (297 com alocado) | auditoria 36 | tratado: tipo do ciclo 2 pelo quadro de 13/02/2026 (adendo 48b, §7; adendo 52c no logit) |

**Como testar o canal 2 (proposta; precisa de adendo congelado antes de rodar):**
- **limites de Lee** (Lee, 2009): apara, no lado com mais células de vaga
  imediata, o excesso de células, nas duas pontas da distribuição do
  outcome, e dá um intervalo para o salto sem supor como o Ministério escolheu
  o tipo. Em RDD, a mesma ideia de aparar aparece em Gerard, Rokkanen e Rothe
  (2020), para manipulação do escore; a adaptação à seleção pelo tipo de vaga
  é nossa e precisa ser escrita no adendo (conferir a literatura antes);
- **"ter vaga imediata" como outcome da RDD**, por corte e ciclo, com o tipo do
  quadro anterior à alocação (ciclo 2 de 13/02): é o tamanho da seleção que os
  limites precisam aparar;
- **balanço dos controles pré-determinados dentro da amostra só de vagas
  imediatas** (capital, UF, porte, médicos e especialistas por 10 mil hab.,
  composição de curso; doc 63, §3): se a amostra selecionada estiver
  balanceada no corte, a seleção pesa menos;
- **outcome que não condiciona no tipo:** médicos alocados por município com
  todas as vagas no denominador (N1) continua relatado ao lado.

Registrado também como explicação 14 em
[`../../06_execucao/63_registro_explicacoes_e_controles_H1.md`](../../06_execucao/63_registro_explicacoes_e_controles_H1.md).

### 2.13 Na H3, estamos olhando só para os médicos do município?

Pergunta do autor, 26/10/2026. **Não. A H3 tem dois níveis, e o deck hoje só
mostra o primeiro.**

| Nível | Unidade e amostra | Comparação | Outcomes | Resultado | Leitura |
|---|---|---|---|---|---|
| **1. Médico** (doc 57d; é o +6,6 h/sem do deck) | o próprio médico do PMM-E ligado ao CNES, ciclos 1 e 2 (1.397 com origem) | quem já começou contra médicos do programa ainda não iniciados (Callaway–Sant'Anna no médico) | horas cadastradas do médico em qualquer lugar; no município do posto; fora dele | +6,6 h/sem total; +8,7 no município do posto; −2,1 fora; 51,0% já tinham vínculo no município do posto | trajetória de quem entrou; associação sob tendências paralelas entre quem entra em meses diferentes; **não diz nada sobre os outros médicos do município**; não é efeito da bolsa nem do PMM-E sobre a oferta |
| **2. Município** (protocolo 60, parte B; doc 57k; auditoria 34) | município × mês, 2024-06 a 2026-08; 1.037 municípios que ofereceram vaga, 315 tratados | municípios com o 1º médico do programa contra os que ainda não receberam (Callaway–Sant'Anna no município) | B1 vínculos de especialistas nas CBO-alvo; B2 horas SUS deles; B3 horas dos **outros** especialistas, sem os do PMM-E; B4 horas totais; B5 generalistas (placebo) | B1–B4 sobem depois da chegada, B5 não; mas o pré já vinha subindo e a ruptura M̄ de Rambachan–Roth fica abaixo de 1 | **não dá para afirmar aumento da oferta local**; dá para dizer que **não aparece saída dos outros especialistas** (B3 não cai) |

**Consequência para o deck:**
- "metade já estava lá" vem do nível 1;
- a pergunta "soma oferta no município?" só o nível 2 responde, e de forma
  inconclusiva;
- falta no deck curto um gráfico do nível 2, com B3 em destaque, na Robustez
  da H3 (e uma linha na Discussão: "não detectamos saída dos outros; não dá
  para afirmar que a oferta local subiu").

### 2.14 E se usarmos o corte para separar quem recebe de quem não recebe, no nível do município?

Pedido do autor, 26/10/2026: "gosto da ideia de olhar para esse desenho,
especialmente se pudermos comparar quem recebeu e quem não recebeu a partir do
corte como controle e tratamento. Roda se não tiver feito isso ainda."

**O que já existia:**
- **E7 (doc 43):** DiRD da bolsa sobre a oferta de especialistas do município
  (mudança pós − pré, comparada nos dois lados do corte), em todos os
  municípios (U) e nos do quadro do ciclo 1 (V1). Nenhuma linha rejeita zero.
  É a forma reduzida do corte, mas sem os outcomes do doc 57k (horas dos
  **outros** especialistas, B3) e sem a amostra dos três ciclos.
- **Doc 57k:** compara pelo **mês da chegada**, não pelo corte; o pré já subia.

**O que faltava e foi congelado no protocolo 64**
([`../../06_execucao/64_protocolo_oferta_local_no_corte.md`](../../06_execucao/64_protocolo_oferta_local_no_corte.md)),
antes de qualquer conta:
- **forma reduzida** por corte nos municípios que ofereceram vaga em algum
  ciclo (V, 1.037), com os outcomes do 57k (B1–B5): primárias B1 e B2, Holm;
- **primeiro estágio:** o corte muda a chance de o município receber médico do
  programa? Se o F robusto for < 10, o instrumento é fraco e só se relata o IC
  de Anderson–Rubin;
- **razão *fuzzy*:** efeito de receber médico para os municípios que recebem
  por causa do corte, **só sob exclusão**, que o pacote do corte pode violar;
  por isso é secundária e lida junto com o placebo de generalistas (B5);
- **estudo de evento no corte**, mês a mês, para ver se o pré é plano;
- **heterogeneidade da chegada por lado do corte** (o ATT do 57k acima e
  abaixo de cada corte);
- **seleção de V:** o corte muda a chance de oferecer vaga?

**Cautelas a levar para a leitura:**
- a H1 não detectou que o corte mude o preenchimento; se o corte quase não
  muda quem recebe médico, o primeiro estágio será fraco e a razão *fuzzy* não
  terá estimativa pontual útil. Isso já está previsto na leitura do protocolo;
- o corte mede o **pacote** (bolsa e outras regras); a DiRD remove só a parte
  constante no tempo das outras regras.

**Estado (26/10/2026):** executado e auditado (doc 57q; auditoria 39, aprovado
com correções de texto, nenhum número mudou). Resultado: o corte não muda a
chance de o município receber médico do programa (F ≈ 0,2 e 0,0; instrumento
fraco, IC de Anderson–Rubin ilimitado, sem razão *fuzzy* utilizável); a mudança
na oferta local de especialistas não se distingue entre os lados (Holm = 1 nas
quatro primárias); os outros especialistas não saem; placebo de generalistas
zero; pré plano. Números no doc 57q. É ausência de efeito detectado, com IC
largos, sobre o pacote do corte; não é prova de efeito zero.

### 2.15 Decisão de 26/10/2026: o deck tem no máximo 14 slides

O autor: "esses últimos decks estão muito grandes. Pode deixar mais curtos
mesmo, só com os principais slides, idealmente menos de 15". O deck curto passa
a ter **no máximo 14 slides**, nas oito seções obrigatórias (doc 06), sem
apêndice no PDF. O que sai do deck continua nos docs. Em execução.

### 2.16 Resultados do adendo 48d (controles e PSM) e decisões pendentes do autor

Executado (doc 57r) e auditado (auditoria 40, aprovado com correções; nenhuma
estimativa mudou). Em resumo:
- **Balanço em 0,300:** do lado de bolsa maior há menos capitais, menos
  Nordeste e mais especialistas no resto da região de saúde. É limite da RDD
  em 0,300.
- **Controles somados (secundário):** o HI-2 em 0,300 deixa de excluir zero;
  a queda não se separa dessas diferenças de localização e médicos.
- **PSM em 0,300 (principal do adendo):** nenhuma diferença na H1 nem na
  oferta local.
- **PSM em 0,400:** sem estimativa. Capitais, Sul e Centro-Oeste só aparecem
  abaixo do corte na janela e o logit não converge (regra fixada antes).

**Decisões que só o autor toma (cada uma vira adendo datado):**

| # | Decisão | Opções | Recomendação |
|---|---|---|---|
| 1 | PSM em 0,400 | tirar antes do logit as categorias que só aparecem de um lado (relatando quem saiu), como a §3.2 previa para o suporte; parear exato em capital e região; deixar sem estimativa | tirar as categorias de um lado só (a auditoria testou só a convergência, sem olhar outcome) |
| 2 | Regra do pareamento (decisão 11 do 57r desvia da §3.1: pareou primeiro o par mais próximo de todos, e não "o lado menor procura par") | voltar à regra literal do adendo como principal e manter a gulosa como sensibilidade; manter como está | voltar à regra literal; os IC contêm zero nas duas (auditoria 40, achado 4) |
| 3 | Coluna da razão *fuzzy* do protocolo 64 quando o instrumento é fraco (auditoria 39, achado 1) | deixar vazia quando F < 10; manter com o aviso | deixar vazia, para não ir parar em slide |
| 4 | Teste de heterogeneidade por porte (estrato da atenção primária) | rodar; não rodar | — |
| 5 | Teste de seleção pelo tipo de vaga (§2.12) | congelar adendo; não | congelar |

**Decisão do autor (26/10/2026): "ok, mas anota para fazer mesmo depois".**
As recomendações dos itens 1, 2, 3 e 5 estão **aprovadas** e ficam **a fazer
depois**, nesta ordem, cada uma com adendo datado congelado antes de rodar e
auditoria independente:

| Ordem | Tarefa aprovada | O que fazer | Estado |
|---|---|---|---|
| A | Item 2: regra do pareamento | adendo 48e: no PSM e no Mahalanobis do 48d, a regra literal da §3.1 ("o lado com menos municípios procura par") passa a ser a principal; a gulosa global (decisão 11 do 57r) vira sensibilidade; refazer PS-1 a PS-4 e CL-7 a CL-9 | feito: adendo 48e, doc 57s, auditoria 43 (aprovado com correções de texto; nenhum número mudou). O CL-9 (Mahalanobis na janela de 0,020) não foi refeito: o 48e não o pede |
| B | Item 1: PSM em 0,400 | no mesmo adendo 48e: antes do logit, tirar as unidades das categorias que só aparecem de um lado do corte na janela (capitais, Sul, Centro-Oeste em 0,400; checar também 0,300), contá-las e relatar quem saiu; depois estimar PS-1 e PS-2 em 0,400 | feito: adendo 48e, doc 57s, auditoria 43. Em 0,400 saíram 19 linhas da H1 e 5 municípios da oferta local; nenhuma linha principal detecta diferença |
| C | Item 3: razão *fuzzy* do protocolo 64 | deixar `tau` e os limites de Anderson–Rubin vazios em `OC_estimativas.csv` quando o F robusto do primeiro estágio for < 10, com a nota "instrumento fraco"; ajustar teste e doc 57q; é mudança de formato de saída, não de especificação | **feito** (commit `515a559`, 26/10/2026): `tau`, EP, IC e p vazios nas linhas *fuzzy* com F < 10; AR ilimitado em `ar_ilimitado`; doc 57q §5.4 e §8 (correção da auditoria 49: constava "a fazer") |
| D | Item 5: seleção pelo tipo de vaga | adendo novo à H1: limites de Lee por corte; "ter vaga imediata" como outcome da RDD; balanço dos controles L e M dentro da amostra só de vagas imediatas (§2.12) | **feito**: adendo 48f, doc 57t, auditoria 44 (§2.12, linha 2a) (correção da auditoria 49: constava "a fazer") |
| — | Item 4: heterogeneidade por porte | adendo 48g (estrato do IED da APS) | **feito**: doc 57u, auditoria 45 (aprovado com correções). Não se detecta que o salto dependa de o estrato mudar; o IED não explica o sinal, com pouca potência, e o canal **não** fica descartado (auditoria 45). Fora do deck curto (correção da auditoria 49: constava "aberto") |
| — | H1 pareada por UF e capital e pelos especialistas num raio de 100 km (pedido do autor de 27/10/2026) | adendo 48h | **feito**: doc 57w, auditoria 47 (aprovado com correções de texto). Nenhuma diferença de preenchimento nos dois cortes, com poucos pares; com efeito fixo de UF, a queda da HI-2 em 0,300 deixa de se distinguir de zero (doc 65, §4.8). Fora do deck curto |
| — | H2 com efeito fixo do par de UFs e comparação local no corte (pedido do autor de 27/10/2026) | adendo 52e | **feito**: doc 57x, auditoria 48 (aprovado com correções de texto). Comparando vagas da mesma UF, a bolsa pesa mais que no M1 e passa no Holm nos ciclos 1–3; perto do corte, IC com 1. Fora do deck curto |
| — | Auditoria 41 (adendo 52c), achado 1: as sensibilidades da escolha no ciclo 2 (conjunto "só células com vaga imediata" do E9, M2, M4, M6–M9 e DAP) ainda usam o quadro de 19/03/2026, refeito depois do resultado | refazer com o quadro de 13/02 exige adendo; recomendação: refazer ao menos o conjunto "só vaga imediata" do E9, que sustenta a robustez do ciclo 2 no doc 44 | **feito**: adendo 52d (doc 57v; auditoria 46, aprovado com correções); VD-1 mantém o sinal e o IC exclui 1 |
| — | Auditoria 46 (adendo 52d), A1 e A2: as robustezes do **conjunto principal** do E9 no ciclo 2 (placebos, *spline* cúbico, janelas, *cluster* por curso) e as variantes quadrática e de degraus do conjunto só com vaga imediata ainda usam o quadro de 19/03 ou ficaram fora do 52d; na conta da auditoria, a bolsa linear se mantém e o degrau de 0,400 com *spline* quadrático vai a p = 0,060 | refazer exige adendo | **aguarda decisão do autor** |
| — | Hipótese única da versão final | doc [65](../../06_execucao/65_avaliacao_forca_hipoteses.md): H1 inconclusiva (testada, não confirmada), H2 moderada (pós-resultado, preferência revelada), H3 fraca a moderada; recomendação: H1 como hipótese única, H2 na Discussão | **aguarda decisão do autor**. Em 27/10/2026 o coordenador informou à auditoria 49 que o autor decidiu trocar a hipótese e que o deck será reconstruído; o conteúdo da decisão ainda não está registrado aqui |

## 3. A história, na ordem dos slides (depois da validação)

1. A regra é limpa: a bolsa salta só nos cortes de IVS.
2. O preenchimento não sobe no corte, por corte. Por que o sinal sai negativo
   em cada corte, e o que o teste de equivalência permite afirmar.
3. A escolha revela o porquê: a bolsa pesa pouco perto da origem do médico
   (incentivo limitado).
4. A oferta: o médico soma horas, mas metade já estava lá, e o que acontece com
   os especialistas do município (protocolo 60, parte B).
5. O que podemos e o que não podemos afirmar.

## 4. Fila aberta

| Item | Estado |
|---|---|
| Protocolo 60, parte B (oferta local e deslocamento) | feito: doc 57k, auditoria 34 (correção da auditoria 49: constava "estimando") |
| Deck curto na estrutura obrigatória (doc 06), H1 central, numeração nova, até 30 palavras por slide | feito em 26/10/2026, com a H1 principal do adendo 48b (em auditoria) e o scatter só com vagas imediatas; reduzido a 14 slides no mesmo dia |
| Slides da história (seção 3) | a parte B foi auditada (auditoria 34); a história entrou no deck curto de 14 slides, auditado pela auditoria 49 |
| RDD das vagas oferecidas por município, por ciclo e corte (seção 2.2) | proposta; precisa de protocolo próprio |
| Diagnóstico da queda em 0,300 (protocolo 61, doc 57l) | auditado (auditoria 33, aprovado com correções de texto); no curto de 14 slides, o slide das capitais em Robustez e uma frase por explicação na Discussão (o passo a passo foi para as notas) |
| Robustez das explicações da queda (seção 2.11) | a fazer; adendo datado ao protocolo 61 antes de rodar |
| Slides de especificação por estimador e da cronologia dos ciclos | feitos: fichas no completo; no curto, até 4 linhas com a equação em palavras no centro e o resto nas notas |
| Subida dentro das faixas (protocolo 62, doc 57m) | auditada (auditoria 37, aprovado com correções de texto) |
| Capitais e UF no corte 0,300 (adendo 48c) e vaga imediata do ciclo 2 no logit (adendo 52c) | executados e auditados: 48c (doc 57o, auditoria 42) e 52c (doc 57p, auditoria 41). O deck curto ainda usa a H2 do ciclo 2 com o quadro de 19/03 e diz "reestimação em curso" nas notas (auditoria 49, achado A2) |

### 4.1 Fila consolidada em 26/10/2026, fim do dia (pedido do autor: "anota absolutamente tudo isso para resolvermos")

Estado do branch `claude/vigilant-mccarthy-dd92mc` neste momento: os agentes do
deck, do adendo 48c e da auditoria 38 foram interrompidos; o trabalho do deck e
do 48c entrou como **WIP** (registro de mudanças, 26/10/2026). A `main` está
parada antes dos retratos WIP.

*Atualização de 27/10/2026 (auditoria 49): o retrato acima venceu. Os WIP foram
auditados e a `main` está no commit `7e9f881`, igual ao branch. Os estados das
linhas abaixo foram corrigidos onde estavam vencidos, com a marca "auditoria
49".*

**H1 (plano A)**

| # | Item | Estado | Próximo passo |
|---|---|---|---|
| 1 | Auditoria 38 do adendo 48b (`HI_*`, doc 57n) | feito: aprovado com correções de texto; nenhum número mudou | **feito** (26/10/2026): "em auditoria" saiu do slide 8 e das linhas de fontes; nas notas, o p sem correção e o p de Holm da HI-2 em 0,300 e a leitura desse caso como decisão de implementação (achado 3) |
| 2 | Adendo 48c (capitais e UF; script 41, `HC_*`, doc 57o) | feito: testes, pipeline e auditoria 42 (aprovado com correções; nenhum número mudou). A fonte bruta do IBGE foi arquivada em 26/10/2026, com autorização do autor (script a19; nota da auditoria 42) | — (auditoria 49: constava "pendente") |
| 3 | Adendo 52c (escolha com tipo de vaga do ciclo 2 de 13/02) | feito: auditoria 41 (aprovado com correções; nenhum número mudou); pendência do achado 1 na §2.16 | — |
| 4 | Seleção pelo tipo de vaga (seção 2.12, canal 2) | feito: adendo 48f, doc 57t, auditoria 44 (seção 2.12, linha 2a) | no deck curto, linha "Tipo de vaga · testado: Lee contém zero" na Identificação, com o detalhe nas notas |
| 5 | H1 com covariáveis pré-determinadas (doc 63, §2 e §3) | em parte feito (auditoria 49: constava "proposto"): capital e efeito fixo de UF no 48c; localização (capital, macrorregião, porte) e médicos na região no 48d; UF e especialistas num raio de 100 km no 48h. Falta a composição de curso na HI-2 e os controles a adquirir (item 6) | congelar adendo com o que falta; relatar cada um isolado e todos juntos |
| 6 | Controles a adquirir (doc 63, §3): escola médica e residência (e-MEC, CNRM), beneficiários ANS, PIB e receita municipal (só controle, nunca running variable), homicídios (SIM), leitos e estrutura se o CNES do repo não tiver | não adquiridos | scripts de aquisição com manifesto e hash, como os a0x |
| 7 | Heterogeneidade por porte (estrato da atenção primária muda em 0,300 só para portes 2 e 3; auditoria 18) | **feito** (auditoria 49: constava "não aprovado"): adendo 48g, doc 57u, auditoria 45. O IED não explica o sinal, com pouca potência; o canal não fica descartado | fora do deck curto |
| 8 | Robustez das explicações da queda (seção 2.11) | a fazer | adendo datado ao protocolo 61 |
| 9 | "Ir de fato depois de alocado" por faixa (seção 2.9) | sem estimativa | protocolo próprio |
| 10 | RDD das vagas oferecidas por município, por ciclo e corte (seção 2.2) | proposta | protocolo próprio |

**H2 e H3 (planos B)**

| # | Item | Estado | Próximo passo |
|---|---|---|---|
| 11 | Nível 2 da H3 (oferta local, doc 57k) fora do deck curto | **frase com número** (26/10/2026): linha "H3 · município" no slide de planos B, pelo protocolo 64 (doc 57q, auditoria 39), com o Holm das primárias na tela; saltos de B1 e B3 nas notas; a razão *fuzzy* fica fora (instrumento fraco) | o gráfico de B1–B5 com B3 em destaque não cabe no teto de 14 slides |
| 12 | Deixar explícito no slide da H3 que o +6,6 h é do próprio médico, não do município | **feito** (26/10/2026): "+6,6 h/sem do próprio médico" no slide de planos B | — |

**Documentos com texto errado a corrigir**

| # | Onde | Erro | Correção |
|---|---|---|---|
| 13 | doc 49, §2; doc 57l (§8 e "Para dizer na banca"), gerado pelo script 38; seção 2.11 deste doc (corrigida acima) | "no ciclo 2, vaga de reserva não podia ser preenchida na 1ª chamada" | é efeito do quadro refeito depois do resultado (auditoria 36); no 57l, corrigir pelo script e rodar de novo, não à mão |
| 14 | doc 06, seção 3 | — | já corrigido pelo agente do deck (H1 central) |
| 15 | doc 04, §3 e §8 | recomendação antiga "H3" (hoje H2) como central | mantida como registro da proposta; a decisão do autor (H1) entra no §9 do doc 04 |

**Deck curto (rascunho de 26 slides reduzido a 14 em 26/10/2026)**

| # | Item | Estado |
|---|---|---|
| 16 | Revisar o WIP inteiro: ~30 palavras por slide, H1 agrupada, H2/H3 renumeradas, efeitos por corte | **feito** (26/10/2026): 14 slides, no máximo 30 palavras cada, H1 agrupada, H2/H3 em cinza, efeitos por corte; PDF renderizado e conferido slide a slide |
| 17 | Slide 11 ("H2 e H3: como estimamos") pouco informativo; slides 2 e 25–26 ainda com espaço vazio | **feito** (26/10/2026): o slide 11 virou duas linhas cinzentas na especificação da H1; capa e secundárias fundidas; as colunas de texto ao lado das figuras e os slides de texto ocupam a área |
| 18 | Incluir a seção 2.12 (tipo de vaga) em uma frase na Identificação ou Robustez da H1 | **feito** (26/10/2026): linha na tabela da Identificação, com o detalhe nas notas; depois da auditoria 44, "Tipo de vaga · testado: Lee contém zero" |
| 19 | Quando sair a auditoria 38 e o 48c, trocar "em auditoria" e atualizar o slide de capitais com `HC_*` | **feito** (26/10/2026): "em auditoria" saiu; o slide "Controlando a capital" virou "Comparando municípios parecidos" (figura nova dos adendos 48d e 48e, por corte); as capitais (auditoria 36) e o `HC_*` (auditoria 42: com a dummy de capital, a maior parte do salto da HI-2 fica) foram para as notas |

**Infraestrutura**

| # | Item |
|---|---|
| 20 | Suíte completa módulo a módulo (a suíte inteira morre por memória); depois, levar à `main` só o que estiver auditado |
| 21 | Doc 63 atualizado a cada explicação nova, com data |
