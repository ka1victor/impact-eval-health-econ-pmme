# Plano causal público executado — cutoff de escore e atração realizada

> **Documento canônico de decisão em 04/09/2026.** O núcleo do trabalho curto
> passa a ser o efeito local de ganhar a vaga de primeira opção. O desenho usa
> apenas publicações já disponíveis, não depende de pedido administrativo e já
> foi estimado no módulo A8. A RDD da bolsa pelo IVS fica arquivada como uma
> pergunta distinta, bloqueada pela ausência de primeiro estágio público.

## 1. Resposta executiva

O trabalho **não perdeu a causalidade**. Há um resultado causal local
condicional, substantivamente próximo do tema de atração e suficientemente
compacto para organizar um trabalho pequeno:

> **Entre candidatos de ampla concorrência que disputaram a mesma primeira
> opção e ficaram separados por exatamente um ponto no cutoff, qual foi o
> efeito de ganhar a vaga sobre homologar e estar posteriormente ativo naquele
> curso–CNES?**

Em 2025, a amostra principal contém 36 pares. Ganhar marginalmente a vaga
elevou:

- a homologação no mesmo curso–CNES em **63,9 pontos percentuais**;
- a presença ativa no mesmo curso–CNES em 12/08/2026 em **33,3 pontos
  percentuais**.

O primeiro efeito tem IC95% convencional de 47,4 a 80,4 p.p. e teste exato
pareado `p<0,000001`. O segundo tem IC95% convencional de 13,5 a 53,1 p.p. e
teste exato `p=0,0042`.

Esses números são relevantes porque medem se uma oportunidade marginal de
alocação se converte em adesão e presença posterior do especialista no local
pretendido. Eles não medem produção assistencial e não dependem do estoque
agregado do CNES.

## 2. O que foi estimado — e o que não foi

### Tratamento

Ganhar a alocação da primeira opção no cutoff específico de uma célula
curso–CNES.

### Contrafactual

O primeiro candidato não selecionado, também em primeira opção e ampla
concorrência, na mesma célula e chamada, com pontuação exatamente um ponto
menor que a do último selecionado.

### Outcomes

1. **Processo/adesão:** homologação no mesmo curso–CNES. É a conversão
   administrativa imediata, mas está próxima da própria elegibilidade criada
   pela seleção; seu grande efeito não é a principal novidade substantiva.
2. **Resultado substantivo principal:** presença ativa no mesmo curso–CNES em
   12/08/2026. É posterior e incondicional à homologação, portanto preserva o
   efeito total da alocação sem selecionar apenas quem entrou.
3. **Sensibilidades:** homologação e atividade em qualquer local do programa,
   úteis para verificar eventual realocação.

O desenho **não identifica**:

- o efeito da bolsa adicional ou do IVS;
- o efeito total do PMM-E sobre todos os especialistas do município;
- o efeito sobre a decisão de se inscrever, pois todos já são candidatos;
- duração individual, saída ou retenção contínua;
- produção, consultas, exames, internações ou saúde.

Por isso, a formulação substantiva mais precisa é **atração realizada ou
conversão da alocação em ingresso e presença**, não atração ex ante de novos
candidatos.

## 3. Isto é regressão descontínua?

É um **desenho de descontinuidade no cutoff de seleção**, mas não deve ser
vendido como a RDD contínua convencional nem como a RDD da bolsa pelo IVS. A
pontuação é discreta e a amostra principal observa apenas um valor de score de
cada lado de cada cutoff. A interpretação mais honesta é:

> comparação pareada no limite de seleção, sob uma hipótese de randomização
> local ou comparabilidade local entre candidatos separados por um ponto.

O cutoff é específico de cada vaga. O tratamento muda entre a última posição
selecionada e a primeira não selecionada. Empates foram excluídos; assim, os
critérios não publicados de desempate por mesma UF e maior idade não decidem a
atribuição nos pares principais.

Isso resolve a maior ameaça do A7, que misturava empates e diferenças maiores
de pontuação. Não resolve automaticamente todas as ameaças: um ponto no barema
pode refletir experiência ou qualificação também associada à adesão. Com
running variable discreta, não há como fazer a diferença tender arbitrariamente
a zero. A causalidade, portanto, depende da hipótese substantiva de que essa
diferença residual de um ponto não provoca por outro canal um salto grande no
outcome.

## 4. Grau de rigor

O grau correto é **moderado**, e não alto.

### O que fortalece o desenho

- tratamento determinado por um cutoff administrativo dentro da mesma vaga;
- curso, estabelecimento, chamada, primeira preferência e modalidade de
  concorrência mantidos constantes em cada par;
- exclusão de empates e de linhas explicitamente rotuladas como sub judice nas
  publicações que trazem esse marcador;
- nenhuma violação do sentido do gap nos pares principais;
- outcomes definidos no mesmo curso–CNES e em qualquer local;
- placebos, janelas alternativas, leave-one-out e replicação externa;
- ausência de nomes, CPFs ou pares reidentificáveis nos artefatos persistidos;
- hashes das seis fontes de entrada congelados no protocolo.

### O que impede rigor alto

- score discreto, com apenas um ponto de cada lado;
- comparabilidade local não integralmente testável;
- poucas covariáveis individuais prévias disponíveis para balanceamento;
- apenas 36 pares em 2025;
- ligação pública entre listas por nome normalizado exato e curso–CNES;
- homologação muito próxima da própria etapa de seleção, tornando a presença
  posterior o resultado substantivamente mais informativo;
- protocolo retrospectivo: o A7 já havia aberto os outcomes antes do recorte
  estrito ser congelado.

O teste exato pareado é mais transparente que depender somente de aproximações
assintóticas, mas ele também é condicional à hipótese de comparabilidade local.
Os intervalos t são reportados como **convencionais**, não como solução para os
problemas de running variable discreta.

## 5. Diagnósticos que já foram executados

### Placebo imediatamente abaixo do cutoff

Entre 30 pares de não selecionados separados por um ponto, onde a alocação não
muda, as diferenças foram:

- homologação no mesmo local: **−3,3 p.p.** (`p=1,000`);
- presença ativa no mesmo local: **0,0 p.p.** (`p=1,000`).

O salto principal não reaparece fora do ponto em que o tratamento muda. Esse é
um teste favorável, embora não prove sozinho a hipótese identificadora.

O placebo imediatamente acima tem apenas cinco pares e não é informativo para
precisão; ele é mantido como transparência, não como teste decisivo.

### Janelas e outcomes alternativos

| Recorte de 2025 | Pares | Homologação no local | Ativo no local |
|---|---:|---:|---:|
| gap exato de 1 ponto — principal | 36 | +63,9 p.p. | +33,3 p.p. |
| gap positivo de até 2 pontos | 74 | +58,1 p.p. | +35,1 p.p. |
| qualquer gap positivo | 100 | +58,0 p.p. | +36,0 p.p. |

O sinal e a ordem de magnitude não dependem da janela. Os 76 pares empatados
continuam apenas descritivos, pois voltam a depender dos desempates não
observados.

### Influência de curso e UF

Ao excluir sucessivamente cada curso ou cada UF:

- homologação permanece entre +58,1 e +71,0 p.p.;
- presença ativa permanece entre +27,3 e +38,7 p.p.

Nenhum curso ou UF isolado cria ou inverte o resultado.

### Replicação pública em 2026

Na segunda chamada do ciclo 2 de 2026, há 11 pares no mesmo recorte. O efeito
sobre estar ativo no mesmo curso–CNES é **+36,4 p.p.**, direção muito próxima à
de 2025. O IC95% convencional é 2,5 a 70,3 p.p., mas o teste exato é
`p=0,125`, pois há somente quatro pares discordantes. A classificação correta é
**replicação direcional consistente, porém imprecisa**.

## 6. Relevância para atração e retenção

O resultado responde a uma margem relevante de desenho do programa: quando
dois candidatos marginais querem a mesma vaga, oferecer efetivamente a vaga ao
primeiro aumenta muito a probabilidade de adesão e de presença posterior
naquele local. Isso mostra que o mecanismo de seleção e matching tem efeitos
reais, e não apenas formais, sobre onde o especialista aparece.

Para um trabalho curto, essa pergunta é mais defensável do que usar produção ou
estoque municipal como proxy. Ela também é mais simples do que tentar explicar
toda a oferta de especialistas, pois compara pessoas no limite da mesma
oportunidade.

Há, contudo, duas palavras que precisam ser usadas com cuidado:

- **atração:** aqui significa ingresso/homologação realizada após a candidatura,
  não geração de novas inscrições;
- **retenção:** o snapshot mostra presença numa data posterior, não tempo até a
  saída nem permanência contínua.

Uma formulação enxuta para o artigo é:

> “Estimamos o efeito local da alocação de primeira opção sobre a adesão e a
> presença posterior de especialistas no estabelecimento escolhido.”

## 7. Relação com os resultados anteriores

| Bloco | Papel no trabalho curto | Leitura correta |
|---|---|---|
| A4 — gradiente territorial | motivação descritiva | localidades remotas têm menor atração realizada; não é causal |
| A5 — dinâmica CNES | apêndice ou evidência contextual | trajetória associada; não identifica o participante nem causalidade |
| A7 — pares adjacentes amplos | diagnóstico que levou ao A8 | diferenças grandes, mas mistura empates e gaps |
| **A8 — gap de um ponto sem empate** | **núcleo causal** | efeito local condicional de ganhar a primeira opção |
| RDD da bolsa pelo IVS | pergunta arquivada | IVS público não reproduz a faixa nem gera primeiro estágio estável |
| DDD imediata versus reserva | diagnóstico histórico | falhou o portão de relevância |

O A4 ajuda a explicar por que alocação territorial importa. O A8 responde à
pergunta causal viável. O A5 não deve ser usado para “confirmar” o A8, pois mede
outro objeto e continua associativo.

## 8. Outros resultados possíveis sem pedir dados

Com as fontes públicas já locais, os resultados adicionais defensáveis são
limitados e quase todos já foram incorporados ao A8:

1. **Substituição para outro local:** os outcomes “em qualquer local” mostram
   se o não selecionado entrou em outra vaga. Em 2025, o efeito foi +58,3 p.p.
   em homologação em qualquer local e +33,3 p.p. em atividade em qualquer
   local. Isso sugere que a alocação afeta ingresso no programa, não apenas o
   endereço observado.
2. **Replicação por chamada/ciclo:** a primeira e a segunda chamadas de 2025
   são reportadas separadamente; 2026 fornece uma replicação independente,
   ainda pequena.
3. **Heterogeneidade territorial:** pode ser mostrada apenas como exploratória.
   Com 36 pares, dividir por remoticidade, IVS, curso ou região produziria
   células muito pequenas e risco alto de resultados acidentais. Não deve virar
   a conclusão principal.
4. **Retenção contínua:** não é possível com o snapshot atual. Não se deve
   inferir uma curva de sobrevivência a partir da data de início apenas entre
   quem segue ativo, pois isso seleciona sobreviventes.

Portanto, a decisão não é abrir muitas regressões. É preservar um resultado
principal simples, dois outcomes hierarquizados, placebos claros e uma
replicação transparente.

## 9. Plano executado e próximos passos internos

Sem solicitações externas ou espera administrativa:

1. **Concluído:** protocolo retrospectivo com pergunta, amostra, treatment,
   outcomes, inferência, placebos e linguagem proibida.
2. **Concluído:** amostra estrita de 2025, com 36 pares sem empate e gap de um
   ponto.
3. **Concluído:** estimativas principais, sensibilidades de gap, outcomes em
   qualquer local e placebos.
4. **Concluído:** leave-one-course, leave-one-UF e replicação do ciclo 2 de
   2026.
5. **Concluído:** proteção de dados, hashes, relatório, figura e testes
   automatizados.
6. **Próximo passo de redação:** organizar introdução, método, resultados e
   conclusão em torno do A8; manter A4 como motivação e A5 no apêndice.

Não há pedido administrativo pendente e nenhum efeito fica condicionado a uma
resposta do Ministério.

## 10. Artefatos reproduzíveis

- protocolo: [`A8_protocolo_cutoff_escore.json`](../../output/tema_trabalho/A8_protocolo_cutoff_escore.json);
- estimativas principais: [`A8_tabela_02_estimativas_escore_estrito.csv`](../../output/tema_trabalho/A8_tabela_02_estimativas_escore_estrito.csv);
- placebos: [`A8_tabela_03_placebos_escore_estrito.csv`](../../output/tema_trabalho/A8_tabela_03_placebos_escore_estrito.csv);
- sensibilidades: [`A8_tabela_04_sensibilidade_gap.csv`](../../output/tema_trabalho/A8_tabela_04_sensibilidade_gap.csv);
- leave-one-out: [`A8_tabela_05_leave_one_out.csv`](../../output/tema_trabalho/A8_tabela_05_leave_one_out.csv);
- síntese estruturada: [`A8_estimativas_cutoff_escore.json`](../../output/tema_trabalho/A8_estimativas_cutoff_escore.json);
- relatório: [`A8_relatorio_cutoff_escore.md`](../../output/tema_trabalho/A8_relatorio_cutoff_escore.md);
- figura: [`A8_figura_01_efeitos_cutoff_escore.png`](../../output/tema_trabalho/A8_figura_01_efeitos_cutoff_escore.png).

O script canônico é
[`09_estimar_cutoff_escore_estrito.py`](../../scripts/tema_trabalho/09_estimar_cutoff_escore_estrito.py)
e está integrado ao `run_all.py`.
