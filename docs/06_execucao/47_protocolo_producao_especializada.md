# Protocolo de produção especializada (SUS e saúde suplementar)

> **Data de congelamento:** 19/10/2026, antes de baixar ou abrir qualquer
> outcome de produção.<br>
> **Pedido do autor (19/10/2026):** medir, como KPI central da política, a
> produção de consultas, exames e cirurgias que exigem médico especialista, no
> SUS e, se possível, no conjunto SUS + privado do município. A ideia do autor:
> se a oferta privada do município aumenta, isso também ajuda a resolver o
> problema central da política (acesso a especialista).<br>
> **Estatuto:** pré-especificado antes de abrir os dados, mas **posterior à
> síntese E8** (doc 44) e à rodada X (doc 46). A família K abaixo tem Holm
> próprio e não altera o Holm das primárias P1 e P2 do protocolo 40. Toda saída
> leva `estatuto = PROTOCOLO_47_POS_SINTESE` e `natureza_dos_dados = EMPIRICO`.

## 1. Por que agora e o portão do `CLAUDE.md`

O `CLAUDE.md` guarda SIH e SIA até os portões R1–R5 do plano da RDD
(`docs/05_identificacao/14_plano_implementacao_rdd_bolsa.md`), para não usar
produção clínica na busca de um resultado antes de validar a fonte de
exogeneidade. Estado dos portões:

- **R1:** aprovado (regra sharp com o IVS 2010 oficial);
- **R2:** suporte e densidade validados; os cortes coincidem com outras
  políticas (auditoria 18), o que torna a RDD em nível um pacote. Esse é o
  motivo do desenho em diferenças (DiRD);
- **R3:** congelamento do protocolo 40;
- **R4:** estimado no E3/E6/E9;
- **R5:** estimado no E7.

Os portões foram executados. O autor autorizou expressamente a produção
clínica em 19/10/2026. Os resultados de R4 (sem salto robusto em
preenchimento) e R5 (sem salto no CNES) já são conhecidos. Por isso a família
K é relatada como teste posterior à síntese, e não como confirmação
independente.

## 2. O que se mede e o que não se mede

| Margem | Fonte pública | Cobre | Não cobre |
|---|---|---|---|
| SUS ambulatorial | SIA/SUS, TabNet `sia/cnv/qabr.def`, por local de atendimento, mês de processamento | produção aprovada pelo SUS, inclusive de prestador privado contratado, com o **CBO do profissional executante** | produção paga fora do SUS |
| SUS hospitalar | SIH/SUS, TabNet `sih/cnv/qibr.def`, por local de internação | AIH aprovadas por grupo do procedimento principal (04 = cirúrgico) | CBO do executante (o TabNet não filtra) |
| Saúde suplementar | ANS, dados abertos TISS (`dadosabertos.ans.gov.br/FTP/PDA/TISS`), por município do prestador e mês de realização | eventos pagos por planos de saúde, com CBO do executante no evento | pagamento direto do bolso, que não tem fonte pública por município |
| Capacidade privada | painel CNES nacional (tarefa C) | vínculos e horas **não SUS** por CBO | produção |

**Limites conhecidos antes de abrir os dados:**
- TISS publicado até a realização 202512. O pós-período do conjunto
  SUS + planos tem 3 meses (202510–202512) e só alcança o ciclo 1.
- O SIA no TabNet vai até o processamento 202607.
- Espera e fila (regulação) não são públicas e continuam fora.
- O conjunto "SUS + privado" é **SUS + planos**: o desembolso direto fica fora.
  Isso é relatado como limite e não é imputado.

## 3. Definições

### 3.1 "Exige médico especialista"

No SIA e no TISS, um procedimento conta quando o **CBO do profissional
executante** é médico especialista. Os grupos de CBO são os mesmos do painel
CNES nacional (`scripts/aquisicao/a09_adquirir_cnes_nacional.py`):

| Grupo | Uso |
|---|---|
| `alvo_pmme` | CBO-alvo dos cursos do PMM-E; **principal** |
| `especialistas_nao_alvo` | outros especialistas médicos; secundário e placebo de especialidade |
| `generalistas` (225125, 225142, 225170) | placebo e confundidor |
| `mfc_225130` | relatado à parte |

A classificação é importada do script a09, e não redigitada.

Exame de laboratório executado por biomédico, por exemplo, não conta, porque o
CBO não é médico especialista.

### 3.2 Tipos de produção

| Tipo | SIA (SIGTAP) | TISS (TUSS) |
|---|---|---|
| consultas | subgrupo 0301 (consultas, atendimentos, acompanhamentos) | consultas (10101012 e família 1.01) |
| exames | grupo 02 (finalidade diagnóstica) | SADT diagnóstico (família 4) |
| cirurgias | grupo 04 ambulatorial; SIH grupo 04 (AIH) | procedimentos cirúrgicos (famílias 3) |

**Unidade e medida:**
- unidade: município × mês;
- medida principal: quantidade aprovada (SIA), AIH aprovadas (SIH),
  quantidade informada (TISS);
- taxa: por 10 mil habitantes, com a população do Censo 2022 do arquivo usado
  no E7.

## 4. Outcomes

### Família K — primárias (Holm entre as três)

| Id | Outcome | Fonte | Pré | Pós |
|---|---|---|---|---|
| K1 | produção SUS ambulatorial por CBO `alvo_pmme` (consultas + exames + cirurgias), por 10 mil | SIA | 202406–202506 | 202510–202607 |
| K2 | cirurgias SUS hospitalares (AIH grupo 04), por 10 mil | SIH | 202406–202506 | 202510–202607 |
| K3 | consultas especializadas SUS + planos por CBO `alvo_pmme`, por 10 mil | SIA + TISS | 202406–202506 | 202510–202512 |

Sinal: **+ = mais produção especializada no município.**

### Secundárias

| Id | Outcome |
|---|---|
| K1a, K1b, K1c | componentes de K1: consultas, exames e cirurgias |
| K1d | mesmo que K1 com todos os especialistas (`alvo_pmme` + `especialistas_nao_alvo`) |
| K3a | consultas, exames e cirurgias nos planos (TISS), separados, por CBO `alvo_pmme` |
| K3b | K3 com SIA no mesmo pós 202510–202512, para separar janela de fonte |
| K4 | capacidade privada: vínculos e horas **não SUS** das CBO `alvo_pmme` por 10 mil (CNES; não SUS = total − SUS) |
| K5 | composição SUS/privado: participação do SUS em K3 |

### Placebos

| Id | Outcome | Leitura |
|---|---|---|
| KP1 | produção SIA por `generalistas` | não deve saltar por causa da bolsa de especialista; salto indica cointervenção (PMMB/APS nos mesmos cortes) |
| KP2 | produção SIA por `especialistas_nao_alvo` | substituição entre especialidades se negativo |
| KP3 | placebo dentro do pré (202406–202411 contra 202412–202505) | igual ao E7 |

## 5. Desenhos

### D1 — DiRD nos cortes (efeito do incentivo marginal de R$ 5 mil)

- Igual ao E7 (protocolo 40, §5–§6 e §13):
  - ΔY_m = média(pós) − média(pré);
  - RDD local linear sobre ΔY_m, kernel triangular, h = 0,050, HC1;
  - cortes 0,300 e 0,400 empilhados (principal) e separados;
  - população U (todos os municípios) principal; V1 secundária;
  - funções de `scripts/rdd_bolsa/rdd_lib.py`.
- **Estudo de evento:**
  - RDD mês a mês relativo a 202506, desde 202201, com datas das políticas S1–S6;
  - pré extra 202201–202303 (S5).
- **Robustez:**
  - Poisson local nas contagens com exposição populacional;
  - IC honesto (Armstrong–Kolesár) para as primárias;
  - h = 0,035 e 0,075;
  - média do pós em vez da média de meses com dado.

### D2 — chegada do especialista do PMM-E (participação; exploratório)

O D1 mede o efeito marginal da bolsa. O KPI da política também pede o efeito
da **chegada** do especialista.

| Elemento | Especificação |
|---|---|
| Amostra | municípios que ofereceram células nos ciclos 1 ou 2 (`outcomes_V_municipio`) |
| Tratado | município com ≥ 1 especialista ativo |
| Mês de chegada | menor `dt_inicio_atividade` da lista nominal (`data/pmm_especialistas_nominal.csv`) |
| Controles | não tratados até 202607 (nunca tratados) e ainda não tratados |
| Estimador | Callaway–Sant'Anna (2021), ATT(g, t) com coortes trimestrais de chegada e comparação com ainda-não-tratados; agregação por tempo de evento de −24 a +9 meses; teste conjunto dos pré; erros por bootstrap multiplicador com cluster no município |
| Outcomes | K1, K1a–K1d, K2, KP1, KP2 e K4; K3 só onde o TISS cobre (coorte de chegada ≤ 202512) |
| Rótulo | `EXPLORATORIO_PARTICIPACAO` |

**Limites declarados antes de abrir:**
- a lista nominal só traz quem estava ativo no retrato, então quem saiu antes
  some e seu município pode ser contado como não tratado. Sensibilidade:
  excluir municípios com alocado na 1ª chamada (X2) e sem ativo;
- a chegada depende da escolha do candidato, então D2 é ATT sob tendências
  paralelas, não um efeito com fonte de exogeneidade validada;
- linguagem associativa se o pré não for plano.

**Dose:** ATT por especialista que chega (efeito ÷ número de chegadas), só
descritivo.

### Leitura de substituição (D1 e D2)

| Padrão | Leitura |
|---|---|
| SUS sobe e privado (K4, TISS) cai na mesma especialidade | migração de horas do privado para o SUS sem ganho líquido |
| total sobe | ganho líquido |
| alvo sobe e não alvo cai | remanejamento entre especialidades |

A X1 mostrou que 45–51% dos especialistas já estavam no município antes do
início, por isso essa leitura é central.

## 6. Regras de integridade

Valem todas as regras de integridade:
- nada simulado, imputado ou digitado vira observação;
- mês ou UF ausente na fonte fica ausente com motivo, nunca zero. Exemplos:
  - os arquivos SIH de AC e RR de 2026-06 que faltavam no FTP em 31/08/2026;
  - célula que o TabNet não retorna;
- números de docs saem de `output/` e são conferidos por teste;
- o arquivo de IVS errado não é lido.

**Proveniência:** cada consulta ao TabNet registra:
- a URL;
- o corpo do POST;
- a data;
- o SHA-256 da resposta bruta.

Cada arquivo TISS registra a URL, o tamanho, o SHA-256 e a data.

**Brutos:**
- em `data/` não se escreve;
- respostas brutas ficam fora do Git, no cache da aquisição;
- só os agregados e manifestos entram em `output/aquisicao/`.

**Validações de aquisição, antes de qualquer contraste:**
- totais nacionais por mês contra o total "Brasil" do próprio TabNet;
- cobertura de municípios por mês;
- meses sem processamento;
- conferência de uma UF pequena célula a célula.

**Sem olhar por lado do corte:** a aquisição não calcula nada por faixa de IVS
nem por tratamento. A estimação só começa depois que a aquisição for validada
e commitada.

**Limites de leitura:**
- nenhum mês CNES ≥ 202609 é lido;
- SIA e SIH são lidos até 202607;
- TISS até 202512.

## 7. Inferência e relato

- Holm na família K (K1–K3). BKY nas secundárias, dentro de K.
- Todo resultado é relatado, qualquer que seja o sinal. Para cada primária
  também são relatados:
  - o efeito mínimo detectável (2,8 × EP);
  - o efeito relativo à média abaixo do corte no pré.
- Nada é reescolhido depois de ver resultados. Desvio forçado pelos dados (por
  exemplo, uma variável que o TabNet não oferece) vira adendo datado, com o que
  já se viu.

## 8. Exposição prévia aos dados (honestidade)

Antes deste congelamento, foram vistos:

- os formulários do TabNet SIA e SIH: só nomes de dimensões e filtros, sem dado;
- a listagem de arquivos do FTP da ANS;
- o cabeçalho e 8 linhas brutas de `AC_202510_AMB_CONS` e
  `AC_202510_AMB_DET`, para conhecer o esquema. Nada foi agregado nem
  cruzado com IVS.

Nenhum outcome da família K foi visto por município nem por lado de corte.

## 9. Saídas

| Etapa | Script | Saídas | Doc |
|---|---|---|---|
| aquisição SIA | `scripts/aquisicao/a12_adquirir_sia_tabnet.py` | `output/aquisicao/sia/` | `docs/auditorias/aquisicao/A12_sia_tabnet.md` |
| aquisição SIH | `scripts/aquisicao/a13_adquirir_sih_tabnet.py` | `output/aquisicao/sih/` | `A13_sih_tabnet.md` |
| aquisição TISS | `scripts/aquisicao/a14_adquirir_tiss_ans.py` | `output/aquisicao/tiss/` | `A14_tiss_ans.md` |
| D1 | `scripts/rdd_bolsa/21_producao_dird.py` | `output/rdd_bolsa/K_D1_*` | `50_resultados_producao_especializada.md` |
| D2 | `scripts/rdd_bolsa/22_chegada_pmme_evento.py` | `output/rdd_bolsa/K_D2_*` | idem |

## 10. Adendo de 19/10/2026 (depois da aquisição de SIA e SIH, antes de estimar)

A aquisição (A12 e A13) mostrou três fatos da fonte. Eles foram vistos só em
totais nacionais e por UF, nunca por IVS ou lado de corte. As decisões abaixo
são tomadas antes de qualquer contraste:

1. **Meses imaturos.** O número de municípios com produção no SIA cai nos dois
   últimos meses de processamento:
   - todos os profissionais: de cerca de 5.450 para 4.884 em 202606 e para
     3.973 em 202607;
   - na SIH, AC e RR não têm o arquivo de 202607;
   - o TabNet avisa que os últimos seis meses estão sujeitos a revisão.

   **Decisão:** o pós principal de K1 e K2 passa a 202510–202605. As linhas até
   202607 viram sensibilidade.
2. **Grupo 09 do SIGTAP (OCI, Ofertas de Cuidados Integrados).** O grupo 09
   começa em 202501. São pacotes de cuidado especializado do Agora Tem
   Especialistas, que substituem procedimentos antes cobrados um a um. Se
   ficassem fora, K1 poderia cair sem queda real da produção.

   **Decisão:**
   - K1 principal inclui o grupo 09 executado pelas CBO `alvo_pmme`;
   - K1 sem o grupo 09, na definição original, vira sensibilidade;
   - OCI sozinho entra como secundária K1f.
3. **SIH, meses atípicos e município sem população.**
   - Meses atípicos de RR (`uf_mes_atipico`): ficam na amostra principal; uma
     sensibilidade exclui as UF-meses marcadas.
   - O município 510183, criado depois do Censo 2022, não tem população e fica
     fora das taxas, com registro.
