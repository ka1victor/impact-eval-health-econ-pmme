# Síntese dos achados e novo plano causal — atração de especialistas, bolsa e IVS

> **Atualização em 04/09/2026:** este diagnóstico permanece canônico para a
> inviabilidade pública da RDD da bolsa, mas sua prioridade de execução foi
> substituída pelo
> [`17_plano_causal_publico_cutoff_escore.md`](17_plano_causal_publico_cutoff_escore.md).
> O pedido administrativo foi cancelado. O A8 encontrou, com dados já locais,
> um efeito local condicional de ganhar a primeira opção usando 36 pares sem
> empate e separados por um ponto.

## 1. Decisão executiva — registro anterior e atualização

**Decisão vigente:** o trabalho curto passa a ter o A8 como núcleo causal.
Ganhar marginalmente a primeira opção elevou a homologação no mesmo
curso–CNES em 63,9 p.p. e a presença ativa posterior em 33,3 p.p. O placebo
imediatamente abaixo do cutoff é nulo, as sensibilidades não invertem o sinal e
o ciclo 2 de 2026 replica a direção (+36,4 p.p.), ainda com pouca precisão. A
causalidade é local e condicional à comparabilidade entre candidatos separados
por um ponto; o protocolo é retrospectivo e o grau de rigor é moderado.

O texto abaixo preserva a decisão anterior sobre o IVS para fins de
rastreabilidade. Ela não define mais a fila de execução.

O trabalho não perdeu sua pergunta causal. A pergunta mais alinhada ao tema
continua sendo:

> **Qual é o efeito de oferecer R$ 5 mil adicionais por mês sobre a atração e o
> preenchimento administrativo de vagas de especialistas do PMM-E?**

A descontinuidade da bolsa pelo IVS permanece o desenho preferido, mas está
**bloqueada com o IVS público disponível**, e não refutada em princípio. O
arquivo local de IVS 2010 não reproduz a classificação usada nas vagas e não
gera um primeiro estágio estável no valor anunciado. Isso impede tanto uma RDD
sharp quanto uma RDD fuzzy improvisada com a variável pública.

O desenho pode ser recuperado se o Ministério fornecer o escore administrativo
efetivamente usado, sua vintagem, precisão, arredondamento, cutoffs e exceções.
Com esses campos, o núcleo público de confirmação/homologação já permite uma
primeira análise de preenchimento administrativo. O universo de candidaturas é
desejável para medir atração diretamente, mas não é condição para começar a
RDD da oferta.

Enquanto a regra não for recuperada:

1. A4 é a evidência principal sobre desigualdade territorial de atração, em
   linguagem associativa;
2. A5 é evidência longitudinal secundária sobre estoque cadastrado no CNES,
   também associativa;
3. A7 é a alternativa causal mais promissora, mas responde ao efeito de ganhar
   uma alocação, não ao efeito da bolsa, e depende dos desempates não públicos;
4. a DDD imediata versus reserva está encerrada porque seu portão de relevância
   falhou;
5. produção, fila, internações e custo-benefício continuam fora do trabalho
   curto, cujo foco é atração.

## 2. Regra institucional e estimando correto

O Edital SGTES/MS nº 3/2025 associa a categoria municipal do IVS ao valor
mensal anunciado:

| Categoria em 2025 | Faixa | Bolsa anunciada |
|---|---:|---:|
| média, baixa ou muito baixa | 3 | R$ 10 mil |
| alta | 2 | R$ 15 mil |
| muito alta | 1 | R$ 20 mil |

Fonte: [Edital SGTES/MS nº 3/2025, item 11](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2025/chamamento-publico-sgtes-ms-no-3-2025-projeto-mais-medicos-especialistas/edital-de-chamamento-publico-no-3-2025.pdf).

A taxonomia do Atlas do Ipea classifica `0,301–0,400` como média,
`0,401–0,500` como alta e `0,501–1` como muito alta. Se o PMM-E tiver aplicado
exatamente esse arquivo e essa precisão, os saltos candidatos de 2025 seriam:

- `0,400/0,401`: R$ 10 mil para R$ 15 mil;
- `0,500/0,501`: R$ 15 mil para R$ 20 mil.

Fonte: [Atlas da Vulnerabilidade Social nos Municípios Brasileiros, Ipea](https://repositorio.ipea.gov.br/bitstream/11058/4381/1/Atlas_da_vulnerabilidade_social_nos_municipios_brasileiros.pdf).

O IVS não atribui mecanicamente municípios ao PMM-E nem determina o número de
vagas. Adesão, capacidade instalada, pactuação e priorização ocorrem antes da
publicação. Assim, o estimando não é o efeito do IVS, da vulnerabilidade ou da
participação no programa. É o efeito local do **adicional anunciado**,
condicionalmente ao universo de ofertas publicadas próximo ao cutoff.

Para o outcome `Y`, a versão sharp candidata é:

\[
\tau_{\text{oferta}}(c)=
\lim_{r\downarrow c}E[Y\mid R=r]-
\lim_{r\uparrow c}E[Y\mid R=r],
\]

em que `R` deve ser o escore administrativo exato. Se existirem exceções e o
corte apenas elevar a probabilidade ou o valor da bolsa, a versão fuzzy é:

\[
\tau_{\text{fuzzy}}(c)=
\frac{\text{salto em }Y}{\text{salto no valor anunciado ou recebido}}.
\]

O denominador deve corresponder ao tratamento declarado. Pagamentos mensais só
são necessários para estimar dose recebida; não são necessários para o efeito
da oferta anunciada sobre a escolha do candidato.

## 3. Achados empíricos já produzidos

### 3.1 A4 — atração administrativa e território

População primária: 1.295 células CNES–curso da primeira chamada de 2025, em
368 municípios. Alguma confirmação ou homologação foi observada em 393 células
— **30,3%**.

| Estrato | Proporção bruta com atração | Diferença ajustada vs. interior remoto, modelo mínimo |
|---|---:|---:|
| interior remoto | 20,5% | referência |
| interior próximo de polo | 26,9% | +12,7 p.p. (EP 4,3) |
| capital | 35,6% | +23,2 p.p. (EP 8,6) |
| metropolitano | 44,9% | +29,4 p.p. (EP 6,1) |

No modelo completo, o contraste metropolitano cai para +19,8 p.p.
(`p=0,0199`; `q=0,0596`). O padrão metropolitano versus remoto permanece ao
separar confirmação (+28,5 p.p.), homologação (+25,0 p.p.) e ao colapsar a
unidade para município–curso (+33,1 p.p.). Leave-one-UF, leave-one-curso e
leave-one-município não invertem o sinal metropolitano.

**Interpretação permitida:** há um gradiente territorial robusto de atração
administrativa. **Interpretação proibida:** municípios metropolitanos atraíram
mais por causa do PMM-E, da bolsa ou do IVS. A alocação territorial das vagas e
as escolhas dos candidatos não foram aleatórias.

Fonte reproduzível: [A4_relatorio_diagnostico.md](../../output/tema_trabalho/A4_relatorio_diagnostico.md).

### 3.2 A5 — evolução posterior do estoque cadastrado

A amostra confirmatória contém 587 células município–curso, 295 municípios e
dez cursos com ponte curso–CBO sem sobreposição. O estudo de evento usa junho
de 2025 como referência limpa, efeitos fixos de célula, curso–mês e UF–mês e
inferência agrupada por município.

- teste conjunto das diferenças prévias: `F=1,031`, `p=0,420`;
- março de 2026 versus junho de 2025: **+0,500 especialista cadastrado** nas
  células com atração, relativamente às sem atração (EP 0,234; `p=0,033`);
- a distribuição é assimétrica: entre células com atração, média 2,29,
  mediana 1 e máximo 211 na variação junho/2025–março/2026.

A não rejeição das pré-tendências não prova tendências paralelas. Atração é um
resultado realizado, não um tratamento exógeno, e o CNES não identifica o
bolsista. O coeficiente descreve uma trajetória diferencial associada à
atração; não é efeito causal nem retenção individual.

Fonte: [A5_relatorio_diagnostico.md](../../output/tema_trabalho/A5_relatorio_diagnostico.md).

### 3.3 DDD histórica — vaga imediata versus cadastro de reserva

No universo CNES–curso, a diferença bruta de alocação foi +19,17 p.p., mas ela
não se transportou para o grão e a amostra que identificavam a DDD. Nas 319
células município–curso de 93 municípios:

- alocação confirmada: +2,79 p.p., EP 6,89 p.p., `p=0,687`;
- homologação: -2,45 p.p., EP 6,54 p.p., `p=0,709`.

Como a modalidade imediata não criou uma primeira etapa relevante na amostra
identificadora, a DDD foi corretamente encerrada como comparação ajustada. Nem
pré-tendências nem placebos consertam a ausência de relevância.

Fonte: [01_relatorio_portao_relevancia.json](../../output/avaliacao_impacto/relatorios/01_relatorio_portao_relevancia.json).

### 3.4 A7 — cutoff do último selecionado

As publicações permitem comparar, na mesma célula curso–CNES, o último
selecionado em primeira opção com o primeiro não selecionado:

- 423 pares adjacentes em quatro publicações;
- 193 pares com outcomes observáveis em 2025;
- 81 pares de 2025 com o mesmo escore publicado.

Na primeira chamada, as diferenças selecionado menos não selecionado foram
+46,3 p.p. em homologação e +27,2 p.p. em presença ativa no snapshot. Na
segunda chamada, foram +77,2 p.p. e +56,1 p.p.

O padrão é grande e se repete, mas ainda não é causal. O edital desempata por
mesma UF de domicílio ou nascimento e depois por maior idade; esses campos não
estão nas planilhas públicas e também podem explicar início e permanência. O
snapshot não reconstrói spells individuais.

Fonte: [A7_relatorio_cutoff_selecao.md](../../output/tema_trabalho/A7_relatorio_cutoff_selecao.md).

### 3.5 RDD da bolsa — reprodução da faixa

No ciclo 1, apenas 191 dos 368 municípios caem na faixa que seria prevista ao
aplicar a taxonomia externa ao IVS 2010 local. Os outros **177 municípios
(48,1%)** divergem:

| Faixa anunciada | Recalculada 1 | Recalculada 2 | Recalculada 3 |
|---|---:|---:|---:|
| Faixa 1 | 19 | 46 | 37 |
| Faixa 2 | 0 | 13 | 94 |
| Faixa 3 | 0 | 0 | 159 |

A divergência pode decorrer de vintagem, arquivo, precisão, arredondamento,
recodificação, exceções ou erro. Enquanto sua origem não for documentada, ela
não constitui variação exógena e o IVS público não é a running variable
administrativa comprovada.

### 3.6 RDD fuzzy pública — auditoria do primeiro estágio

Foi testado se o IVS público ao menos provoca um salto probabilístico no valor
anunciado. As regressões usam uma observação por município, inclinações locais
separadas, pesos triangulares e erros HC1. Por ser um diagnóstico de tratamento,
nenhum outcome de atração foi utilizado.

| Corte | Janela | Municípios abaixo/acima | Diferença bruta da bolsa | Salto local-linear | `p` |
|---:|---:|---:|---:|---:|---:|
| 0,400 | 0,010 | 12 / 8 | -R$ 625 | +R$ 4.065 | 0,018 |
| 0,400 | 0,020 | 30 / 18 | +R$ 56 | +R$ 202 | 0,920 |
| 0,400 | 0,030 | 42 / 26 | +R$ 696 | -R$ 329 | 0,831 |
| 0,400 | 0,050 | 77 / 39 | +R$ 1.710 | -R$ 711 | 0,518 |
| 0,500 | 0,010 | 5 / 5 | R$ 0 | R$ 0 | — |
| 0,500 | 0,020 | 8 / 6 | R$ 0 | R$ 0 | — |
| 0,500 | 0,030 | 11 / 7 | R$ 0 | R$ 0 | — |
| 0,500 | 0,050 | 20 / 11 | R$ 0 | R$ 0 | — |

A única especificação aparentemente favorável — local-linear em `0,400` com
janela 0,010 — usa vinte municípios, contradiz a diferença bruta negativa e
desaparece nas janelas seguintes. Selecioná-la pelo p-valor seria escolha
retrospectiva. Em `0,500`, todos os municípios próximos dos dois lados já têm
R$ 20 mil. Logo, não existe primeiro estágio público estável e a fuzzy RDD
também é reprovada.

Fontes: [tabela do primeiro estágio](../../output/rdd_bolsa/a01_primeiro_estagio_publico.csv) e [relatório estruturado](../../output/rdd_bolsa/a01_primeiro_estagio_publico.json).

## 4. Classificação do rigor atual

| Resultado | O que os dados sustentam | Nível máximo hoje | Principal ameaça |
|---|---|---|---|
| A4 território–atração | associação robusta e replicada entre especificações | associativo | seleção de municípios, vagas e candidatos |
| A5 atração–CNES | trajetória cadastral diferencial posterior | associativo longitudinal | atração endógena e CNES sem identidade PMM-E |
| DDD imediata–reserva | comparação histórica ajustada | não causal; desenho encerrado | primeiro estágio administrativo falhou |
| A7 corte de seleção | grande descontinuidade observável | preliminar | desempates por território e idade não observados |
| RDD sharp com IVS público | faixa não reproduzida | inválido | running variable errada ou incompleta |
| RDD fuzzy com IVS público | bolsa não salta de forma estável | inválido | instrumento sem relevância |
| RDD com escore administrativo | ainda não estimada | causal potencial | depende de dados e portões R1–R3 |

Os resultados existentes são rigorosos para as afirmações limitadas acima:
amostra e unidade foram auditadas, erros respeitam agrupamento municipal,
especificações de robustez foram executadas e resultados instáveis não foram
promovidos. Rigor de execução, contudo, não transforma uma associação em
causalidade.

## 5. Novo plano principal — recuperar a RDD da bolsa

### 5.1 Escopo mínimo

- ciclo principal: primeira chamada de 2025;
- tratamento: oferta de R$ 5 mil mensais adicionais;
- cutoff principal candidato: `0,400/0,401`;
- cutoff `0,500/0,501`: somente replicação, caso o escore correto mostre
  suporte e primeiro estágio;
- unidade de atribuição e inferência: município;
- nenhuma combinação automática com 2026, pois a grade mudou.

### 5.2 Outcomes focados em atração

Ordem de preferência:

1. candidaturas válidas por oferta e indicador de ao menos uma candidatura;
2. aceite ou confirmação administrativa;
3. homologação;
4. início efetivo em prazo fixo.

Com dados exclusivamente públicos, o outcome mínimo será a proporção de
células município–curso publicadas que tiveram alguma
confirmação/homologação, dando o mesmo peso a cada município. O indicador de
alguma atração no município e o modelo no nível da célula, com agrupamento
municipal, serão secundários. Não será calculada taxa por vaga sem identificador
e capacidade versionada.

### 5.3 Dados mínimos e dados ideais

**Mínimo para tentar a RDD com outcomes públicos:**

- município e identificador estável da oferta;
- escore IVS administrativo em sua precisão original;
- vintagem e arquivo de origem;
- regra de arredondamento e inclusão nos cutoffs;
- categoria, faixa e valor anunciados na data da escolha;
- histórico de versões e exceções.

**Ideal para medir atração diretamente:**

- universo de inscrições, inclusive inválidas, retiradas e não publicadas;
- opções escolhidas e conjunto de vagas visível/elegível;
- aceite, recusa, confirmação, homologação e início com datas;
- chaves pseudonimizadas estáveis de vaga, inscrição e profissional.

**Extensão de retenção, fora do núcleo curto:**

- entrada, afastamento, retorno, saída e reocupação;
- ativo em 90 e 180 dias calculado a partir do log;
- ponte segura com o CNES, se necessária.

Folha mensal é dispensável para o efeito da oferta anunciada. Ela só entra se
o estimando mudar para valor efetivamente recebido.

As especificações de pedido estão prontas em
[vagas_e_regra_ivs.md](../pedidos_dados/vagas_e_regra_ivs.md) e
[eventos_e_ponte_cnes.md](../pedidos_dados/eventos_e_ponte_cnes.md).

### 5.4 Portões de identificação

| Portão | Teste | Aprovação | Falha |
|---|---|---|---|
| R1 — regra | reproduzir escore, cutoff, faixa e valor por vigência | 100% ou exceções normativas prévias | encerrar RDD |
| R2 — primeiro estágio | salto estável no valor anunciado/recebido | magnitude relevante em janelas predefinidas | não estimar fuzzy |
| R2 — suporte | municípios e mass points dos dois lados | potência e influência aceitáveis | rebaixar a exploratório |
| R2 — continuidade | vagas, cursos, infraestrutura e covariáveis prévias | ausência de salto material não explicado | interpretar pacote ou encerrar |
| R3 — congelamento | amostra, cutoff, janela, outcomes, inferência e hashes | registro fechado antes de abrir `Y` | não estimar |
| R4 — atração | efeito local sobre procura/aceite/homologação | estimativa e incerteza reportadas | concluir efeito nulo/impreciso sem redesenho |
| R5 — presença | eventos/CNES após R4 | horizonte e identidade válidos | manter fora do artigo curto |

### 5.5 Estimação e inferência

O IVS observado possui três casas decimais. Não há observações arbitrariamente
próximas do cutoff, portanto:

- randomização local municipal será o estimador principal candidato;
- a janela será escolhida por suporte e balanceamento pré-outcome, nunca por
  significância do resultado;
- permutações respeitarão mass points e a atribuição municipal;
- RDD local-linear com inclinações separadas e pesos triangulares será
  robustez;
- haverá `leave-one-mass-point-out`, cutoffs placebo e análise de influência;
- múltiplos cursos do mesmo município não serão tratados como atribuições
  independentes;
- efeitos em `0,400` e `0,500` não serão automaticamente agrupados.

### 5.6 Cointervenções e interpretação

Antes dos outcomes, será testado se o cutoff também altera:

- probabilidade e quantidade de vagas publicadas;
- composição de cursos e CNES;
- prioridade, remanejamento ou ajuda de custo;
- infraestrutura e outras ações do Agora Tem Especialistas.

Se outro componente saltar no mesmo ponto, a conclusão será “efeito do pacote
no limiar”, e não efeito isolado da bolsa.

## 6. Alternativas causais e quando acioná-las

### Alternativa A — cutoff da seleção dos candidatos

**Pergunta:** ganhar marginalmente a primeira opção aumenta início e presença
posterior?

**Vantagem:** a descontinuidade já é grande e aparece em duas chamadas.

**Necessidade:** barema final, indicador de prioridade por UF, distância etária
ao cutoff, capacidade por modalidade, recursos e eventos pseudonimizados.

**Limite temático:** identifica o efeito de receber uma alocação, não o efeito
da bolsa sobre a decisão de se candidatar. É a primeira alternativa se a RDD do
IVS morrer e os dados de desempate forem obtidos.

Plano específico: [15_cutoff_selecao_atracao_retencao.md](15_cutoff_selecao_atracao_retencao.md).

### Alternativa B — mudança da grade entre 2025 e 2026

Em 2026, alta e muito alta passaram a R$ 20 mil, média a R$ 15 mil e baixa ou
muito baixa permaneceram em R$ 10 mil. Assim, o salto em `0,300/0,301` aparece
e o salto em `0,500/0,501` desaparece, enquanto `0,400/0,401` permanece.

Fonte: [Edital nº 28/2026, item 11.2](https://www.gov.br/saude/pt-br/acesso-a-informacao/participacao-social/chamamentos-publicos/2026/chamamento-publico-sgtes-ms-no-6-2026-pmm-e/edital).

Duas versões são possíveis:

1. diferença-em-diferenças por categoria, comparando a mudança em grupos que
   receberam aumento com grupos cujo valor permaneceu;
2. diferença-em-descontinuidades, comparando o salto em `0,300` ou `0,500`
   antes e depois da mudança da grade.

A segunda é mais convincente contra descontinuidades fixas preexistentes, mas
continua exigindo o escore administrativo. Ambas requerem ofertas e outcomes
comparáveis entre ciclos e a hipótese de que outras mudanças não afetaram
diferencialmente os grupos. Por isso são complemento, não atalho automático.

### Alternativa C — DiD município–especialidade com CNES

**Pergunta:** a oferta de uma vaga foi acompanhada por aumento do estoque da
especialidade relativamente a células comparáveis sem oferta?

É possível construir controles e testar tendências prévias usando o painel
CNES. Entretanto, a escolha de municípios e especialidades foi baseada em
necessidade, capacidade e priorização. Mesmo com matching e estudo de evento, a
causalidade depende de tendências paralelas não testáveis. Esta rota é
evidência complementar e condicional, não substituto de igual força para a
RDD.

### Alternativa D — experimento prospectivo de atração

Com parceria institucional, poderiam ser aleatorizados:

- contato ativo e lembretes sobre vagas;
- saliência ou ordenação das vagas na plataforma;
- informação personalizada sobre bolsa e condições locais;
- idealmente, um adicional financeiro entre vagas comparáveis.

O experimento produziria identificação forte, mas o estimando seria o efeito da
intervenção sorteada. Mensagens e saliência não identificam o efeito monetário
da bolsa. É a alternativa metodologicamente mais limpa, mas depende de nova
implementação e parceria.

## 7. Sequência operacional atualizada

```text
P0  Documentar decisão e preservar diagnóstico público                CONCLUÍDO
 ↓
P1  Solicitar escore/regra IVS e histórico de vagas                   PENDENTE
 ↓
R1  Reproduzir 100% da regra administrativa
 ├─ falhou  → encerrar RDD da bolsa e avaliar cutoff de seleção
 └─ passou
      ↓
R2  Primeiro estágio, suporte, potência e cointervenções sem outcomes
 ├─ falhou  → relatório de inviabilidade; sem busca de cutoff alternativo
 └─ passou
      ↓
R3  Congelar protocolo, hashes, janela e outcomes
      ↓
R4  Estimar atração; artigo curto pode terminar aqui
      ↓
R5  Início/presença/retenção somente com eventos válidos
```

### Tarefas imediatas

1. Submeter o pacote focal de vagas e regra do IVS ao canal administrativo
   escolhido pelo autor.
2. Solicitar conjuntamente o universo de inscrições e eventos, porque ele
   melhora o outcome de atração e também permite a alternativa A7.
3. Ao receber resposta, executar a triagem sem incorporar os arquivos brutos
   ao controle de versão e sem converter ausência em zero.
4. Rodar R1 antes de qualquer outcome e publicar o portão, inclusive se falhar.
5. Somente após R1/R2, registrar uma pré-análise curta e estimar R4.

Nenhum pedido foi enviado por esta documentação; os arquivos atuais são
minutas técnicas.

### Estado executado em 04/09/2026

- o portão R1 público foi materializado em uma matriz de 368 municípios e
  reprovado por 177 divergências, sem abrir outcomes;
- o controlador fail-closed confirma que R2–R4 permanecem bloqueados e que não
  existem artefatos prematuros de pré-análise ou efeito RDD;
- a solicitação focal conjunta está pronta para submissão, mas segue não
  enviada porque canal, credenciais, termos e protocolo dependem de autorização
  do autor;
- a triagem automática de eventual resposta está pronta e registra
  `AGUARDANDO_RECEBIMENTO`; ausência de arquivo não é convertida em zero;
- dados administrativos recebidos serão preservados em diretório bruto
  ignorado pelo Git, e somente metadados, hashes e diagnósticos sem linhas
  individuais poderão ser versionados.

O ledger reproduzível de execução está em
[33_status_execucao_plano_causal.md](../06_execucao/33_status_execucao_plano_causal.md).
Este estado é execução correta do plano sob o portão atual: estimar R4 apesar da
falha de R1 violaria, em vez de executar, a estratégia causal.

## 8. Linguagem máxima por cenário

| Cenário | Formulação permitida |
|---|---|
| dados atuais | “território está associado à atração administrativa” |
| A5 atual | “células com atração tiveram trajetória cadastral diferencial” |
| RDD com regra, suporte e continuidade aprovados | “próximo ao cutoff, oferecer R$ 5 mil adicionais alterou o outcome em X” |
| fuzzy com primeiro estágio aprovado | “o aumento induzido da bolsa alterou o outcome para os municípios compliers no limiar” |
| cointervenções no cutoff | “o pacote associado ao limiar alterou o outcome” |
| A7 com desempates reconstruídos | “ganhar marginalmente a alocação alterou início/presença em X” |
| sem score/regra | nenhuma alegação causal da bolsa ou do IVS |

Nunca usar, com os dados atuais: efeito causal do IVS; efeito total do PMM-E;
retenção individual do bolsista; produtividade; redução de fila; melhora de
saúde; custo-benefício.

## 9. Arquivos de referência

- plano operacional detalhado da RDD:
  [14_plano_implementacao_rdd_bolsa.md](14_plano_implementacao_rdd_bolsa.md);
- alternativa pelo cutoff de seleção:
  [15_cutoff_selecao_atracao_retencao.md](15_cutoff_selecao_atracao_retencao.md);
- regra institucional:
  [01_regra_institucional.md](../auditorias/01_regra_institucional.md);
- auditoria IVS e regra:
  [A03_ivs_e_regra.md](../auditorias/aquisicao/A03_ivs_e_regra.md);
- pedido mínimo de vaga e escore:
  [vagas_e_regra_ivs.md](../pedidos_dados/vagas_e_regra_ivs.md);
- pedido de candidaturas e eventos:
  [eventos_e_ponte_cnes.md](../pedidos_dados/eventos_e_ponte_cnes.md);
- script do primeiro estágio:
  [01_auditar_primeiro_estagio_publico.py](../../scripts/rdd_bolsa/01_auditar_primeiro_estagio_publico.py).

## 10. Conclusão fixada

O resultado público não autoriza uma descontinuidade causal da bolsa pelo IVS
2010 disponível. A sharp RDD falha porque a faixa não é reproduzida; a fuzzy
RDD falha porque o IVS público não produz salto estável no valor anunciado.
Isso não elimina o desenho institucional. Elimina somente sua execução com a
variável errada.

O próximo passo não é trocar de cutoff, janela ou outcome. É recuperar o escore
administrativo e testar a regra de modo fail-closed. Se esse portão passar, o
trabalho curto deve terminar no efeito local do adicional sobre atração ou
preenchimento administrativo. Se falhar, a alternativa mais promissora é o
cutoff de seleção, reconhecendo que ele responde a outra pergunta.
