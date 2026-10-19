# 51. Plano de análise das perguntas reformuladas (P1–P6)

> **Data:** 19/10/2026.<br>
> **Pedido do autor:** planejar tudo o que deveríamos e poderíamos rodar para
> responder bem às perguntas que saíram da teoria da mudança do programa, e
> organizar a execução com subagentes.<br>
> **Estatuto:** plano. Nada aqui é protocolo congelado: cada bloco só roda
> depois de ter seu protocolo próprio commitado, antes de abrir outcomes. A
> escolha da hipótese central continua sendo do autor (doc 44, §7; doc 46).<br>
> **Diagrama causal:** a teoria da mudança está publicada como página à parte
> (link na conversa de 19/10/2026). A seção 1 resume o diagrama.

## 1. A teoria da mudança, em uma tabela

A cadeia vai das regras até a saúde. Cada passo diz o que o move, onde a
identificação é fraca e qual pergunta o cobre.

| Passo | O que move | Onde a identificação é fraca | Pergunta |
|---|---|---|---|
| 0. Regras | IVS 2010 → faixa da bolsa; outras políticas nos mesmos cortes (auditoria 18) | os cortes juntam um pacote de políticas | todas |
| 1. Abertura de vagas | proposta do gestor (CIB, capacidade no CNES); priorização discricionária da SGTES; teto orçamentário | sem fórmula publicada; porte e capacidade movem a abertura; no ciclo 1 a faixa saiu depois do pedido dos gestores | P5, P2 |
| 2. Escolha do candidato | bolsa, lugar, distância da origem, vínculo prévio | **é o único passo em que a bolsa age diretamente** e que compara vagas já abertas | **P1** |
| 3. Provimento | vagas abertas × escolha × alocação por nota | mistura abertura com atração | P2, P6 |
| 4. Capacidade | vínculos e horas de especialistas, SUS e privado | substituição: 45–51% já estavam no município (X1) | P4 |
| 5. Produção | consultas, exames, cirurgias, OCI; SUS e planos | chegada depende da escolha; tendências paralelas | P3 |
| 6. Acesso e saúde | espera, fila, internações dos residentes | espera não é pública; internação por residência é | P3 (parcial) |

**O que já foi feito em cada passo:**

| Passo | Análises | Resultado |
|---|---|---|
| Abertura | F0, S-c (doc 49) | sem salto robusto |
| Escolha | E9 | sinal robusto no ciclo 2 |
| Provimento | E3, F1.3, N | nulo ou frágil |
| Permanência | X2 | nulo |
| Capacidade | E7 | nulo |
| Produção | K | em execução |

## 2. Regras comuns a todos os blocos

1. **Integridade** (`CLAUDE.md` e regras de 18/10/2026):
   - nada simulado, imputado ou digitado vira observação;
   - o que falta fica faltante, com motivo;
   - número de doc sai de `output/` e é conferido por teste;
   - o arquivo de IVS errado não é lido;
   - toda saída leva `natureza_dos_dados = EMPIRICO`.
2. **Congelar antes de abrir.** Cada bloco tem um protocolo commitado antes de
   ver qualquer outcome por lado de corte, tratamento ou grupo. Desvio forçado
   pelos dados vira adendo datado, com o que já se viu.
3. **Separar portões de viabilidade de estimação.** Um portão (G) só verifica
   se o dado existe, se liga e se reproduz. Ele não calcula contraste.
4. **Cenários contrafactuais** (simulações do P1) ficam em `output/cenarios/`,
   com `natureza_dos_dados = CENARIO_CONTRAFACTUAL`, separados das saídas
   empíricas. O teste de integridade passa a aceitar esse rótulo só nessa
   pasta.
5. **Limites de leitura:**
   - nenhum mês CNES ≥ 202609;
   - SIA e SIH até 202607 (principal até 202605, conforme o adendo §10 do
     protocolo 47);
   - TISS até 202512;
   - o ciclo 3 só entra com dados de seleção, escolha e funil; outcomes CNES do
     ciclo 3 seguem o plano prospectivo.
6. **Execução:**
   - cada tarefa roda num subagente em worktree isolado, com commit próprio;
   - depois vem uma auditoria independente, em que outro agente recalcula com
     código próprio;
   - a junção usa `--no-ff`, roda a suíte completa e faz push no branch;
   - a main só recebe o trabalho por instrução do autor.
7. **Linguagem.** Descritivo é chamado de descritivo. O D2 e o P3 medem ATT
   sob tendências paralelas. O D1 mede o incentivo marginal num pacote. Toda
   figura tem bloco "Como ler".

## 3. As perguntas e o que rodar em cada uma

### P1 — Quanto o salário move a escolha de onde trabalhar? (candidata a pergunta central)

| Item | Conteúdo |
|---|---|
| Pergunta econômica | elasticidade da escolha de local à remuneração e diferencial compensatório: quanto de bolsa equivale a distância, porte, capital, tipo de estabelecimento e vulnerabilidade |
| Estimando | coeficiente da bolsa na utilidade da vaga, dentro do conjunto de vagas abertas do curso e ciclo; disposição a pagar (DAP) = razão de coeficientes |
| Unidade | candidato × vaga do conjunto de escolha (`escolhas_candidatos`, `escolhas_conjunto_principal`); ciclos 1–3 |
| Identificação | saltos da bolsa nos cortes com o IVS contínuo (spline com nós em 0,300 e 0,400), como no E9 §15 |
| Já existe | E9 (logit condicional, logit explodido, aninhado), X4 (heterogeneidade), X5 (deslocamento) |

**Tarefas:**

- **T1.0 — portão G1: identificar os candidatos.** Verificar se os arquivos
  brutos de classificação e resultado trazem nome, CRM e UF de todos os
  candidatos, não só dos alocados. Se trouxerem, ligar cada candidato ao CNES
  pré-programa pela regra da X1, com taxa de ligação e casos ambíguos fora.
  Saída: o município de origem de cada candidato.
- **T1.1 — DAP por distância e atributos.**
  - logit condicional com bolsa, distância origem–vaga (centroides do IBGE já
    no repositório), mesma UF ou região de saúde da origem, porte, capital,
    tipo de estabelecimento e vaga imediata;
  - DAP em R$ por 100 km, por mesma UF e por capital;
  - IC pelo método delta e por bootstrap por conjunto de escolha.
- **T1.2 — heterogeneidade estrutural.** Logit misto, com coeficiente aleatório
  da bolsa e da distância, por simulação com semente fixa. Interações
  pré-determinadas: nota, curso, origem no próprio município e ciclo.
- **T1.3 — por que só o ciclo 2?** Teste formal de igualdade do coeficiente
  entre ciclos. Leituras candidatas, todas a relatar:
  - informação: a grade de faixas foi publicada com o quadro no ciclo 1;
  - número de opções e composição dos candidatos;
  - proporção de vagas imediatas.
- **T1.4 — ordenação por qualidade.** Os candidatos de nota maior vão para
  células de bolsa maior? RDD da nota média dos alocados e dos candidatos de
  1ª opção (F4) mais logit com interação bolsa × nota, a partir da X4.
- **T1.5 — ponte com o preenchimento (P1 → P2).** O coeficiente do E9 implica
  quantos candidatos a mais por célula no corte. Comparar com a RDD de
  candidatos por célula (F1.1) e com o preenchimento observado. É um teste de
  consistência entre o modelo de escolha e o resultado agregado.
- **T1.6 — cenários contrafactuais** (rótulo de cenário, fora de `output/`
  empírico). Com o modelo estimado e as vagas abertas fixas:
  - (a) bolsa plana;
  - (b) gradiente mais íngreme com o mesmo orçamento;
  - (c) adicional só para IVS > 0,400.

  Saídas: distribuição prevista de candidatos de 1ª opção por estrato de IVS e
  custo por candidato adicional em municípios vulneráveis. Toda simulação
  declara as hipóteses: vagas fixas, sem resposta de entrada no programa e
  alocação por nota.

**Ameaças:**
- composição do conjunto de escolha (§14 do protocolo 40);
- quem não se candidatou não aparece (universo de inscrições, pedido externo);
- a distância só existe para quem tem vínculo prévio no CNES; isso entra como
  limite e como sensibilidade.

**Saídas:** script `scripts/rdd_bolsa/25_escolha_dap.py`; protocolo 52;
resultados 57.

### P2 — A bolsa maior preenche mais a vaga já aberta?

| Item | Conteúdo |
|---|---|
| Estimando | efeito da faixa sobre a probabilidade de a vaga aberta ser preenchida, condicional à abertura |
| Unidade | célula e vaga, ciclos 1–3, com o **ciclo 1 como principal** (faixa publicada depois do pedido dos gestores) |
| Já existe | E3, F1.3, N (doc 49), A1–A4 em execução (adendo §7 do protocolo 48) |

**Tarefas:**
- **T2.1** Juntar e auditar A1–A4. Depois, corrigir nos docs 48 e 49 a frase
  sobre o momento em que a faixa foi publicada (já pedida ao agente do A1–A4).
- **T2.2** Linha principal nova: RDD por célula no ciclo 1, com efeitos fixos de
  curso e de tipo de vaga, mais limites de Lee para a abertura. Relatar o
  efeito mínimo detectável e comparar com o T1.5.
- **T2.3** Poder: quantos ciclos seriam precisos para detectar +10 p.p. com
  essa variância. É só cálculo, a partir do X6.

**Ameaças:**
- poucas células por lado;
- outras políticas nos cortes podem ter movido a abertura;
- realocação de vagas imediatas não preenchidas para municípios de cadastro
  reserva (Edital 3/2025, item 5.7).

**Saídas:** script `24_*` (A1–A4) e, para T2.2, `26_preenchimento_celula_c1.py`;
protocolo 53; resultados 57.

### P3 — A chegada do especialista aumenta consultas, exames e cirurgias? (KPI da política)

| Item | Conteúdo |
|---|---|
| Estimandos | D1: efeito do incentivo marginal (DiRD); D2: ATT da chegada (Callaway–Sant'Anna) |
| Unidade | município × mês |
| Já existe | protocolo 47 com adendos §10–§11; aquisições A12, A13, A14; D1 e D2 em execução |

**Tarefas:**
- **T3.1** Auditar e juntar D1 e D2 (doc 50).
- **T3.2 — produção por especialidade.** Mapear curso → procedimentos SIGTAP
  típicos (por exemplo, oftalmologia → exames 0211.06 e cirurgias 0405;
  anestesiologia → cirurgias 04). Medir a produção da especialidade que chegou,
  no município que a recebeu. É mais específico e tem mais poder do que o
  total.
  - Portão G4: o mapeamento é feito a partir do SIGTAP e da ponte curso–CBO,
    antes de abrir outcomes.
  - Se o TabNet não filtrar por procedimento junto com o CBO, a lacuna é
    registrada.
- **T3.3 — controles alternativos no D2:**
  - (a) células oferecidas que ficaram vazias contra preenchidas, dentro do
    mesmo curso e ciclo;
  - (b) diferenças em diferenças sintéticas (Arkhangelsky et al., 2021) como
    robustez;
  - (c) evento com efeito heterogêneo pela origem do médico: já estava no
    município ou não (X1).
- **T3.4 — acesso dos residentes.** Portão G3: adquirir a SIH por local de
  residência (TabNet `sih/cnv/qrbr.def`), com as mesmas regras do A13. Medir
  internações cirúrgicas de residentes por 10 mil. Isso aproxima o acesso, não
  a oferta local.
- **T3.5 — transbordamento regional.** Produção na região de saúde fora do
  município tratado: pacientes atendidos no polo podem vir de fora, e médicos
  podem sair de municípios vizinhos.

**Ameaças:**
- seleção da chegada (escolha do candidato);
- meses imaturos;
- OCI mudando a forma de registro;
- subnotificação do TISS no fim de 2025.

**Saídas:** scripts `21_*`, `22_*` e `27_producao_especialidade.py`; resultados
50 e 57.

### P4 — O programa cria oferta nova ou só passa a pagar quem já estava lá?

| Item | Conteúdo |
|---|---|
| Estimando | variação líquida de horas e vínculos de especialistas, no município de destino e no de origem, ao redor da entrada no PMM-E |
| Unidade | médico (ponte por CRM, X1) e município |
| Já existe | X1 (origem e incumbência, competências pontuais), K4 (capacidade não SUS) |

**Tarefas:**
- **T4.0 — portão G5: painel individual mensal.** Verificar se o cache do a09
  ou um novo download do CNES público por competência (202406–202608, nunca
  ≥ 202609) traz o registro do conselho por vínculo. Se trouxer, montar o
  painel médico × mês: vínculos, horas SUS e não SUS, municípios. Pseudônimo
  determinístico, sem nome.
- **T4.1 — trajetória individual (evento por médico).** Horas totais, SUS e não
  SUS, e número de municípios, de −12 a +10 meses da entrada. A pergunta é se
  o médico soma horas, troca privado por SUS ou só muda de rótulo. É
  descritivo, com comparação entre coortes de entrada.
- **T4.2 — perdas na origem.** Municípios de origem dos que mudaram: variação
  de horas de especialistas da mesma CBO depois da saída (deslocamento).
- **T4.3 — contabilidade líquida.** Ganho no destino menos perda na origem,
  por curso e por estrato de IVS. É descritivo e ligado ao P3.

**Ameaças:**
- vínculo cadastrado não é presença real;
- a ligação falha para parte dos médicos (taxas da X1);
- seleção de quem entra.

**Saídas:** script `28_trajetoria_medicos.py`; protocolo 54; resultados 57.

### P5 — Como o Ministério escolhe onde abrir vagas?

| Item | Conteúdo |
|---|---|
| Pergunta | quais atributos pré-determinados explicam a abertura e a priorização; o IVS ou a faixa entram? |
| Unidade | célula do cardápio do ciclo 3 (cardápio → pedido → priorização tudo ou nada → quadro); município nos ciclos 1–2 (só o quadro publicado) |
| Já existe | `outcomes_G3_municipio`, F0.3 (sem salto) |

**Tarefas:**
- **T5.1** Modelo descritivo da priorização: logit da célula priorizada com
  - tipo e gestão do estabelecimento, natureza jurídica;
  - capacidade no CNES pré;
  - produção SIA e SIH pré (2024–2025);
  - escassez regional de especialistas da CBO;
  - porte, região de saúde, polo regional e IVS contínuo.

  É explicitamente descritivo.
- **T5.2** RDD nos cortes do pedido (gestor) e da priorização (SGTES), por
  célula e por município, com cardápio fixo. Mede se a faixa, já inferível no
  ciclo 3, mudou a demanda do gestor.
- **T5.3** Ciclos 1–2: determinantes do número de vagas no quadro (mesmo modelo,
  só com o resultado final), para dar base ao A4 do P2.

**Ameaças:** é descritivo; nenhuma leitura causal da decisão do Ministério.

**Saídas:** script `29_determinantes_abertura.py`; protocolo 55; resultados 57.

### P6 — Vaga preenchida por pouco contra vaga vazia por pouco (desenho do mecanismo de alocação)

| Item | Conteúdo |
|---|---|
| Ideia | a alocação segue a ordem de nota entre quem escolheu cada célula, com até 2 opções. Perto da nota de corte de cada célula, ser alocado é quase aleatório (Abdulkadiroğlu, Angrist, Narita e Pathak, 2017, "Research Design Meets Market Design") |
| Dois estimandos | (a) candidato: efeito de ser alocado no PMM-E sobre a trajetória do médico no CNES (estar no município da vaga, horas SUS, permanência); (b) célula: efeito de a vaga ser preenchida sobre a oferta e a produção do município, com a variação vinda do mecanismo |
| Dados | `escolhas_candidatos` (ordem das opções, nota, classificado, alocado), quadros de vagas, ponte com o CNES (G1) |

**Tarefas:**
- **T6.0 — portão G2: replicar o mecanismo.** Reconstruir a alocação a partir
  das escolhas, das notas e das vagas. Meta: ≥ 99% de concordância com o
  alocado publicado, por ciclo e chamada. Registrar as regras de desempate e
  os casos *sub judice*. **Sem isso, P6 não roda.**
- **T6.1** Notas de corte por célula e escore de propensão do mecanismo (a
  probabilidade de alocação dada a nota e as opções).
- **T6.2** RDD do candidato em torno da nota de corte da sua 1ª opção.
  - Outcomes CNES do G1 e G5, até 202608.
  - Só ciclos 1 e 2.
  - Relatar o primeiro estágio: alocação e homologação.
- **T6.3** Na célula, a variação no preenchimento induzida pelo mecanismo, como
  instrumento para os outcomes municipais de P3. Só roda se o primeiro estágio
  for forte.

**Ameaças:**
- poucas células com disputa;
- a alocação na 2ª opção contamina o contraste;
- a homologação depende de documentos, não só da nota.

**Saídas:** scripts `30_mecanismo_alocacao.py` e `31_rd_mecanismo.py`;
protocolo 56; resultados 57.

## 4. Fora do alcance (e por quê)

| Pergunta | Por que não roda | Caminho |
|---|---|---|
| Espera e fila | regulação não é pública | pedido externo (`docs/pedidos_dados/`) |
| Gasto do bolso | sem fonte municipal | relatar como limite |
| Total de inscritos e quem não se candidatou | só vemos quem tem opção listada | pedido externo |
| Saúde da população | horizonte curto | agenda de longo prazo |
| Ciclo 3 no CNES | competência 202703 madura | plano prospectivo do ciclo 3 |

## 5. Execução em ondas

### Onda 0 — em curso

| Tarefa | Estado | Depois |
|---|---|---|
| K: D1 e D2 (protocolo 47) | estimando | auditoria e junção (T3.1) |
| A1–A4 (protocolo 48, adendo §7) | estimando | auditoria e junção (T2.1); correção dos docs 48 e 49 |

### Onda 1 — portões de viabilidade (sem abrir outcomes; até 4 agentes em paralelo)

| Portão | Tarefa | Entrada | Saída | Bloqueia |
|---|---|---|---|---|
| G1 | identificar e ligar todos os candidatos ao CNES pré | brutos de classificação e resultado; CNES pré | `output/rdd_bolsa/G1_*`, taxa de ligação | T1.1, T6.2 |
| G2 | replicar o mecanismo de alocação | `escolhas_candidatos`, quadros | `G2_*`, concordância | P6 inteiro |
| G3 | SIH por residência no TabNet | `sih/cnv/qrbr.def` | `output/aquisicao/sih_residencia/` (a15) | T3.4 |
| G4 | mapa curso → procedimentos SIGTAP; viabilidade do filtro no TabNet | SIGTAP, ponte curso–CBO | `G4_*` | T3.2 |
| G5 | painel CNES médico × mês com registro do conselho | cache do a09 ou download novo | `output/aquisicao/cnes_profissional/` (a16) | P4, T6.2 |

Cada portão termina com um relatório de viabilidade e um veredito: `VIAVEL`,
`VIAVEL_PARCIAL` ou `INVIAVEL`. O protocolo da onda 2 se ajusta ao veredito.

### Onda 2 — protocolos congelados (eu escrevo; um commit por protocolo, antes de abrir)

| Doc | Bloco | Depende |
|---|---|---|
| 52 | P1 (T1.1–T1.6) | G1 |
| 53 | P2 (T2.2–T2.3) | onda 0 |
| 54 | P4 | G5 |
| 55 | P5 | — |
| 56 | P6 | G2 (e G1, G5 para o T6.2) |

Para P3, os itens T3.2–T3.5 entram como adendo §12 do protocolo 47, depois de
G3 e G4.

### Onda 3 — estimação (até 5 agentes em paralelo, em worktrees)

| Agente | Bloco | Script | Saídas |
|---|---|---|---|
| E-P1 | DAP, logit misto, ciclos, ordenação por qualidade, ponte P1→P2 | `25_*` | `output/rdd_bolsa/P1_*` |
| E-P1c | cenários contrafactuais (separados) | `25b_cenarios_bolsa.py` | `output/cenarios/P1_*` |
| E-P3x | especialidade, controles alternativos, residência, região | `27_*` | `output/rdd_bolsa/K_X_*` |
| E-P4 | trajetória individual, origem, contabilidade líquida | `28_*` | `P4_*` |
| E-P5 | determinantes da abertura e priorização | `29_*` | `P5_*` |
| E-P6 | mecanismo e RD do candidato | `30_*`, `31_*` | `P6_*` |
| E-P2 | célula no ciclo 1 e poder | `26_*` | `P2_*` |

### Onda 4 — auditorias independentes

Para cada agente da onda 3, um auditor:
- recalcula com código próprio as linhas principais;
- confere rótulos, ausências, textos e figuras ("Como ler" legível);
- roda a suíte;
- escreve `docs/auditorias/2x_*.md`.

Só depois disso vem a junção.

### Onda 5 — síntese

- Doc 57, síntese das perguntas reformuladas:
  - tabela por pergunta: estimando, desenho, resultado, força da evidência;
  - Holm dentro de cada família de primárias;
  - BKY nas secundárias.
- Atualizar:
  - o relatório lean (`gerar_figuras_validacao_professores.py`);
  - o relatório de validação;
  - o doc 38;
  - o bullet do `CLAUDE.md`;
  - o registro de mudanças.
- Conteúdo da banca 2 (`docs/07_apresentacoes/banca2/`) só depois da decisão
  do autor sobre a hipótese central.

## 6. Bloco comum dos prompts dos subagentes

Todo prompt de agente começa com estes pontos:
1. A regra de sincronizar o worktree com o branch de trabalho
   (`git merge --ff-only`).
2. A leitura obrigatória: `CLAUDE.md`, o protocolo do bloco e os scripts e
   docs que ele reutiliza.
3. As regras de integridade da seção 2, por extenso.
4. A lista de saídas e testes: esquema, rótulos, números do doc contra
   `output/`, verificação sintética em memória rotulada "sintético", figuras
   com "Como ler".
5. O pipeline:
   - `run_all.py`;
   - `tests/test_pipeline_rdd_bolsa.py`;
   - o manifesto do A6, regenerado pelo gerador e nunca à mão.
6. A documentação: `tests/README.md` e `docs/00_registro_mudancas.md`.
7. As restrições: commit sem push e sem merge; relatório final com números
   principais, desvios e motivos.

## 7. Ordem de prioridade

Se for preciso cortar, esta é a ordem:
1. Fechar a onda 0: K e A1–A4.
2. P1, com G1 → T1.1, T1.3, T1.4, T1.5. É a candidata a pergunta central, com o
   desenho mais limpo.
3. P3, com T3.2 e T3.4. É o KPI da política.
4. P4. Responde à pergunta sobre substituição, que a X1 já sugere ser central.
5. P5. Barata e dá base ao P2.
6. P2, com T2.2–T2.3.
7. P6. É a mais cara e incerta e depende de G2.
8. T1.6, os cenários. Só depois de o modelo do P1 ser auditado.
