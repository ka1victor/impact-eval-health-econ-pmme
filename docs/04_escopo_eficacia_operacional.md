# 04. Quando o incentivo é eficaz?

> **Status:** desenho anterior preservado, mas congelado. A análise individual de
> cobertura e retenção continua dependendo de dados administrativos e não será
> executada na primeira versão. O plano vigente é o painel público agregado de
> estoque municipal, fluxos e presença posterior em
> [`05_roadmap_execucao.md`](05_roadmap_execucao.md).
>
> Registro do escopo empírico individual anterior. Este documento define o que
> seria chamado de eficácia nesse desenho, seus modos de falha e os limites das
> conclusões.

## 1. Pergunta de pesquisa

> Quando o incentivo adicional do PMM-E transforma vagas ofertadas em capacidade médica sustentada e líquida, e quando resulta apenas em ocupação transitória, substituição ou remanejamento?

Essa formulação é deliberadamente mais estreita que “quando o programa é eficaz”. O estudo avalia o mecanismo de provimento. Não avalia diretamente produção assistencial, fila, saúde ou bem-estar.

## 2. Três níveis distintos de eficácia

| Nível | Pergunta | Situação no desenho individual histórico |
|---|---|---|
| Operacional | O incentivo produz cobertura sustentada e oferta médica adicional? | Objeto central |
| Assistencial | A capacidade adicional produz atendimento e reduz espera? | Fora do escopo atual |
| Social | Há melhora de saúde, equidade e bem-estar superior aos custos? | Fora do escopo atual |

Um resultado favorável no primeiro nível não autoriza inferir os dois seguintes. A conclusão correta será “o incentivo foi eficaz para produzir capacidade médica”, não “o PMM-E foi eficaz” sem qualificação.

## 3. Tratamento e contraste causal

A auditoria institucional deve decidir qual pergunta os dados permitem responder:

| Regra observada | Estimando possível |
|---|---|
| O corte define participação no PMM-E | Efeito local da elegibilidade ao programa |
| Ambos os lados participam, mas o valor do incentivo muda | Efeito marginal do incentivo adicional |
| O corte altera simultaneamente incentivo, oferta e composição das vagas | Efeito do pacote de mudanças, sem isolar remuneração |
| Não existe mudança descontínua ou contraste exógeno | Análise descritiva; sem afirmação causal |

Não nomear como “efeito do programa” uma estimativa que compare apenas duas faixas de incentivo dentro dele.

## 4. Outcome primário

No desenho individual histórico, a unidade preferencial é a
vaga-especialidade-chamamento. Para vagas com seguimento comum, o outcome
primário seria:

```text
cobertura_180 = dias com profissional em exercício nos 180 dias após a oferta / 180
```

Se houver carga horária comparável, será construída também a medida `FTE-dias/180`. A janela poderá ser reduzida antes da estimação se os chamamentos não tiverem 180 dias completos, mas não será escolhida com base nos resultados.

### Decomposição do outcome

- preenchimento em 30, 60 e 90 dias;
- tempo até a primeira entrada;
- saída em até 180 dias;
- dias vagos após o primeiro preenchimento;
- número de profissionais que ocuparam a vaga;
- FTE líquido municipal;
- origem dos vínculos anteriores e simultâneos.

Nesse desenho histórico, cobertura é o outcome primário. Os demais descrevem
mecanismos e não concorrem retrospectivamente para se tornar “o resultado
principal”.

## 5. Perfis de resultado

| Cobertura sustentada | FTE líquido | Perda na origem | Interpretação máxima |
|---|---|---|---|
| Aumenta | Aumenta | Pequena | Expansão operacional sustentada |
| Aumenta | Não aumenta | — | Substituição ou recomposição de vínculos |
| Aumenta localmente | Aumenta localmente | Semelhante | Redistribuição territorial |
| Não aumenta | — | — | Sem resposta operacional detectável |
| Aumenta apenas com infraestrutura prévia | Aumenta nesses locais | Pequena | Eficácia condicionada a complementaridades |
| Efeito impreciso | Incerto | Incerto | Evidência insuficiente, não “efeito nulo” |

Redistribuição não será classificada automaticamente como fracasso: pode melhorar equidade e proximidade. Também não será chamada de expansão líquida.

## 6. Modos de falha definidos antes dos resultados

1. **Falha de atração:** não há aumento em candidatura, aceite ou preenchimento.
2. **Falha de conversão:** há aceite, mas não entrada efetiva.
3. **Falha de durabilidade:** a entrada acelera, mas saída e vacância posterior eliminam o ganho de cobertura.
4. **Falha de adicionalidade:** a vaga é coberta, mas não há aumento líquido de FTE.
5. **Remanejamento:** o ganho local corresponde a perda em outros municípios ou vínculos.
6. **Gargalo complementar:** o efeito aparece apenas onde havia infraestrutura utilizável antes do programa.
7. **Evidência insuficiente:** estimativas são pouco precisas para distinguir efeito relevante de ausência de efeito.

Os modos podem coexistir. Eles serão diagnosticados pela sequência de estimandos, não por histórias escolhidas depois de observar casos extremos.

## 7. Como responder “quando” sem viés pós-tratamento

Não comparar simplesmente vagas que deram certo com vagas que deram errado. Sucesso, permanência e cobertura são resultados posteriores ao tratamento; condicionar a análise a eles gera seleção e viés de sobrevivência.

A heterogeneidade causal será definida somente por condições observadas antes do tratamento, como:

- infraestrutura do CNES no período pré-programa;
- especialidade ou necessidade de ativos complementares;
- oferta médica e dificuldade histórica de preenchimento;
- distância de centros regionais;
- IVS 2010 e características geográficas predefinidas.

Para preservar potência e evitar mineração de resultados, o estudo terá uma heterogeneidade confirmatória: infraestrutura prévia. As demais serão exploratórias e apresentadas como tal.

Casos extremos poderão ser usados para auditoria de processo ou ilustração qualitativa, nunca para identificar por que o incentivo funcionou.

## 8. Adicionalidade e remanejamento

O estudo separará três margens:

1. vínculo nominal do PMM-E;
2. aumento líquido de horas/FTE no município tratado;
3. aumento líquido na região após considerar municípios de origem.

O rastreamento de vínculos anteriores e simultâneos pode descrever de onde vieram os profissionais. Atribuir causalmente perdas a municípios de origem é mais difícil por causa de spillovers e interferência; essa etapa começará como decomposição contábil e terá linguagem própria.

## 9. Critérios de interpretação

- Reportar efeitos, intervalos de confiança e magnitudes substantivas; não classificar pelo p-valor isolado.
- Definir antes da análise a menor mudança de cobertura considerada relevante para a política.
- Não traduzir estimativa imprecisa como ausência de efeito.
- Não criar um índice arbitrário de “sucesso” somando outcomes heterogêneos.
- Não promover heterogeneidade exploratória a conclusão confirmatória.
- Não inferir produção, redução de espera ou saúde a partir de vínculo ou FTE.

## 10. Dados mínimos e portões

### Base A — vagas e trajetória administrativa

- universo de vagas, editais, CNES, especialidade, faixa e valor;
- candidaturas, convocações, aceite, entrada, afastamento e saída;
- identificador pseudonimizado do profissional;
- datas suficientes para reconstruir spells e censura.

### Base B — CNES mensal pré e pós

- vínculos, CBO e carga horária;
- demais vínculos dos participantes;
- infraestrutura anterior ao tratamento;
- município, estabelecimento e região de saúde.

### Portões de decisão

1. Sem universo de vagas: não estimar preenchimento.
2. Sem regra institucional auditável: não usar RDD.
3. Sem seguimento comum: não comparar retenção bruta entre coortes.
4. Sem CNES longitudinal: limitar a conclusão a cobertura administrativa, sem adicionalidade.
5. Sem potência para interação: não concluir que infraestrutura explica a diferença.

## 11. Conclusão que o desenho pode sustentar

O produto final deverá responder:

1. O incentivo alterou a cobertura sustentada das vagas?
2. O efeito veio de atração, velocidade de entrada ou permanência?
3. Houve capacidade médica líquida ou apenas substituição/remanejamento?
4. O efeito dependeu de infraestrutura existente antes do programa?
5. Qual é a população local à qual o efeito pode ser generalizado?

Esse perfil é a definição de eficácia operacional do estudo. Outcomes assistenciais e sociais permanecem como etapas futuras e independentes da cadeia causal.
