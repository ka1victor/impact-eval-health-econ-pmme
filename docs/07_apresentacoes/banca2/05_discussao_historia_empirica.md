# Discussão da história empírica (perguntas do autor de 26/10/2026)

> **Finalidade:** registrar as perguntas do autor sobre a parte empírica, as
> respostas dadas e as decisões de apresentação. Isto alimenta a sequência de
> slides da "história" da banca 2.<br>
> **Números:** este documento não traz número de resultado. Cada resposta
> aponta a seção do documento gerado onde o número está (docs 49, 49b, 57, 57a,
> 57d, 57e, 57i, 57j, 57k), conferido por teste contra `output/`. Fora disso
> aparecem só parâmetros: cortes, valores da bolsa, margens e datas.<br>
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
    bolsa maior teve mais vagas de cadastro reserva, e nenhuma célula só de
    reserva foi preenchida na 1ª chamada. Mais reserva no denominador derruba a
    taxa.
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
metade da queda da taxa por vaga oferecida vem do ciclo 2, ligada ao cadastro
reserva (seção 2.1).

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
| **3. Cadastro reserva no ciclo 2** | no ciclo 2, a vaga de reserva não foi preenchida na 1ª chamada; mais reserva acima do corte derruba a taxa | ciclo 2 com e sem as células só de reserva | citar a regra do edital do ciclo 2; refazer Q1–Q3 só com as células de vaga imediata, por ciclo |
| **4. Porte em 0,400** | municípios grandes logo abaixo do corte abrem e preenchem muitas vagas | doc 49b: retirada dos maiores; controle das vagas oferecidas | o mesmo com log(população) e vagas oferecidas juntas; retirar um por vez |

Todas as linhas são descritivas e pós-resultado: medem o pacote do corte. A
robustez a fazer precisa de adendo datado ao protocolo 61 antes de rodar.

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
| Protocolo 60, parte B (oferta local e deslocamento) | estimando; depois, auditoria |
| Deck curto na estrutura obrigatória (doc 06), H1 central, numeração nova, até 30 palavras por slide | feito em 26/10/2026; falta a H1 principal do adendo 48b (slide "aguardando 48b") e a troca do scatter pela versão só com vagas imediatas |
| Slides da história (seção 3) | depois da parte B auditada |
| RDD das vagas oferecidas por município, por ciclo e corte (seção 2.2) | proposta; precisa de protocolo próprio |
| Diagnóstico da queda em 0,300 (protocolo 61, doc 57l) | auditado (auditoria 33, aprovado com correções de texto); no curto, passo a passo em quatro slides de Robustez |
| Robustez das explicações da queda (seção 2.11) | a fazer; adendo datado ao protocolo 61 antes de rodar |
| Slides de especificação por estimador e da cronologia dos ciclos | feitos: fichas no completo; no curto, até 4 linhas com a equação em palavras no centro e o resto nas notas |
| Subida dentro das faixas (protocolo 62, doc 57m) | auditada (auditoria 37, aprovado com correções de texto) |
| Capitais e UF no corte 0,300 (adendo 48c) e vaga imediata do ciclo 2 no logit (adendo 52c) | congelados; no curto, o diagnóstico da auditoria 36 até as saídas padronizadas; a nota do 52c só nas notas da H2 |
