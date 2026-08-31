# Plano de pré-análise do ciclo 3

> Congelado em 31/08/2026, antes de qualquer outcome pós-tratamento. Este
> documento não apresenta efeito do PMM-E. A primeira estimação só poderá
> ocorrer quando houver seis meses comuns maduros.

## 1. Decisão executiva

A pergunta principal permanece simples e relevante:

> Qual é o efeito de oferecer vagas imediatas de anestesiologia do PMM-E, em
> comparação com propostas de anestesiologia do mesmo ciclo que não foram
> priorizadas, sobre a presença e a permanência de anestesiologistas?

O efeito direto será medido no CNES ofertante. O efeito líquido local será
medido no município. Um ganho no CNES sem ganho municipal será interpretado
como compatível com remanejamento, não como aumento da oferta local. Essa
hierarquia é mais informativa do que escolher apenas um nível:

1. **principal direto:** estoque de anestesiologistas no CNES ofertante, seis
   meses depois de `T0`;
2. **secundário-chave:** estoque municipal de anestesiologistas no mesmo
   horizonte;
3. **mecanismos:** entradas, saídas, churn e número de entrantes ainda presentes
   seis meses depois;
4. **atualização predefinida:** os mesmos outcomes doze meses depois;
5. **clínico condicionado:** cirurgias no SIH, somente depois de completar o
   portão C3-02B.

O torneio pré-tratamento não encontrou base para chamar a priorização de
experimento natural. A classificação congelada para anestesiologia é
`associacao_ajustada`: há suporte e não há rejeição convencional das
pré-tendências, mas os intervalos são largos demais para demonstrar
equivalência e a potência para um único especialista é baixa. O estimando é
causal, mas sua interpretação depende de tendências paralelas condicionais que
os dados prévios não conseguem comprovar.

## 2. População, tratamento e controle

### 2.1 Unidade direta

- população: células CNES--curso do resultado final de adesão do ciclo 3;
- tratamento: todas as observações da célula são `imediata_pura`;
- controle: todas são `nao_priorizada_pura`;
- exclusão: qualquer reserva, célula mista ou combinação inconsistente;
- anestesiologia: 119 CNES tratados e 305 controles;
- CBO: `225151`, conforme a ponte normativa congelada.

### 2.2 Unidade municipal

O braço é agregado sem usar preenchimento. Um município é tratado somente se
todas as suas células daquele curso forem `imediata_pura`; é controle somente se
todas forem `nao_priorizada_pura`. Qualquer outra combinação é excluída.
Anestesiologia tem 77 municípios tratados e 247 controles.

Cadastro de reserva não é ausência de programa e não será controle. Alocação
publicada, preenchimento posterior e presença no CNES não redefinem o braço.
O contraste é intenção de tratar pela oferta imediata, não efeito de receber
um bolsista.

## 3. Calendário e maturidade

- `T0` calendário congelado: competência `202609`;
- pré usado no torneio: `202406`--`202607`, 26 competências;
- `202608`, quando publicado e validado, só completa o baseline; não pode
  alterar outcomes, amostra, estimador ou decisão do torneio;
- horizonte de seis meses: `T0+6`, competência `202703`;
- horizonte de doze meses: `T0+12`, competência `202709`.

Uma competência só é madura depois de publicada e estabilizada no CNES. A data
do tratamento não será deslocada para o primeiro aumento observado do outcome.
Se a documentação administrativa mostrar que o início comum não foi setembro,
a correção deve ocorrer antes de abrir os outcomes pós e ficar registrada como
emenda externa; nunca será inferida da trajetória de médicos.

## 4. Outcomes

### 4.1 Família principal de força de trabalho

Outcome primário: número de profissionais distintos com CBO `225151` no CNES
ofertante em `T0+6`. O outcome secundário-chave soma profissionais distintos no
município, deduplicando o mesmo profissional entre estabelecimentos.

Serão reportados, sem trocar a hierarquia pelo resultado que parecer melhor:

- estoque no mês 6;
- média do estoque nos seis primeiros meses, como estabilidade operacional;
- presença de pelo menos um anestesiologista;
- entradas após seis meses anteriores de ausência observada;
- saídas apenas após três meses posteriores de ausência observada;
- churn: entradas mais saídas quando ambos forem observáveis;
- número, não taxa, de entrantes pós-`T0` ainda presentes em `T0+6`;
- repetição predefinida em `T0+12`.

Uma taxa de retenção condicionada aos entrantes não será outcome causal
primário, pois a entrada ocorre depois do tratamento. Horas cadastrais, se
reconstruídas, serão exploratórias e não equivalem a atendimento realizado.

### 4.2 O que não é mensurável ainda

Os Parquets mensais preservam `IND_VINCULACAO`, mas não
`NU_CNPJ_DETALHAMENTO_VINCULO`. Logo, `070102` sozinho mistura outras bolsas,
APS e ciclos anteriores. Ele é apenas diagnóstico. O primeiro estágio PMM-E e
a permanência individual de participantes exigem a assinatura completa da Nota
59 ou vinculação pelo controlador. Não se solicitarão identificadores civis
quando a vinculação pseudonimizada pelo controlador bastar.

## 5. Estimando e especificação

O estimando principal é o efeito médio da oferta imediata na população de
sobreposição (`ATO`) de CNES comparáveis. Pesos de sobreposição foram
estimados apenas com nível, variabilidade, zeros e tendência do outcome no pré,
IVS 2010, população, região e quantidade de CNES propostos. Os pesos e o
suporte estão congelados em `output/avaliacao_ciclo3/pesos_sobreposicao_pre.csv`.
O efeito não ponderado na coorte administrativa completa será robustez.

A especificação de evento é:

\[
Y_{it}=\alpha_i+\lambda_t+
\sum_{k\ne-1}\beta_k\,Imediata_i\,1[t-T_0=k]+\varepsilon_{it}.
\]

No nível direto, `i` é CNES e o erro é agrupado no município. No nível
local, `i` e o cluster são o município. Como a data é comum, não se usarão
estimadores de adoção escalonada. A inferência principal usará wild cluster
bootstrap-t restrito, reestudantizado, com 9.999 repetições e semente fixa;
o sandwich municipal convencional será mostrado para auditoria.

Synthetic DiD, leave-one-região-out e tendências lineares específicas serão
robustez. Nenhum deles transforma uma regra endógena em sorteio nem repara uma
pré-tendência incompatível. Não haverá inferência por randomização.

## 6. Diagnósticos pré-tratamento

| Módulo e nível | Tratados | Controles | Suporte retido T/C | MDE 80% | Decisão |
|---|---:|---:|---:|---:|---|
| Anestesiologia, CNES | 119 | 305 | 83,2% / 97,7% | 2,22 | associação ajustada |
| Anestesiologia, município | 77 | 247 | 90,9% / 91,1% | 4,44 | associação ajustada |
| Oncologia, CNES | 12 | 39 | ver CSV | 1,22 | inviável confirmatoriamente |
| Intensiva, CNES | 6 | 83 | ver CSV | não estimável | inviável confirmatoriamente |
| Cirurgia geral/CBO exclusivo, CNES | 33 | 337 | ver CSV | 1,70 | sensibilidade ajustada |

Para anestesiologia no CNES, a diferença de tendência mensal ponderada foi
`-0,0028` (EP municipal `0,0698`; IC90% `[-0,1179; 0,1123]`) e o teste conjunto
dos leads teve `p=0,8593`. No município, a tendência foi `-0,0344` (EP `0,1205`;
IC90% `[-0,2332; 0,1645]`) e o teste conjunto teve `p=0,4966`.

Esses p-valores não comprovam paralelismo. A equivalência falhou porque os
intervalos não ficaram integralmente dentro dos limites congelados. A potência
para detectar um anestesiologista foi 22,8% no CNES e 9,0% no município; a MDE
direta de 2,22 é próxima das 2,44 vagas oferecidas por CNES tratado, mas maior
que as 1,12 alocações publicadas por CNES. Isso permite detectar uma resposta
forte do pacote ofertado, não garante precisão para um acréscimo unitário.

Foram usados três placebos temporais, teste conjunto de 13 leads e equivalência
contra limites substantivos. Os resultados integrais, sem seleção pelo menor
`p`, estão em `output/avaliacao_ciclo3/diagnosticos_pre.csv`.

## 7. Generalização, multiplicidade e cointervenção

Oncologia (`225121`) e medicina intensiva (`225150`) têm poucos tratados e não
serão apresentadas como confirmação. Serão descritas separadamente. Qualquer
resumo dos cursos 1, 12 e 24 mostrará os efeitos específicos e usará peso igual
por curso; não esconderá a dominância numérica da anestesiologia. Curso 2 no
CBO exclusivo `225225` é apenas sensibilidade.

Dentro da família de mecanismos, valores `p` serão ajustados por Holm. O
outcome primário e o secundário-chave terão intervalos individuais, com a
hierarquia explicitada. Outras ofertas imediatas no município serão marcadas;
a variante sem cointervenção cirúrgica é robustez congelada, não nova amostra
escolhida pelo resultado.

Conversão futura de reserva ou nova política será contaminação. O ITT original
permanece; uma análise de censura na primeira contaminação será secundária.

## 8. Missing, zeros e valores extremos

- arquivo/competência ausente é censura, nunca zero;
- arquivo presente, unidade coberta e nenhum especialista elegível significa
  zero observado;
- identificador profissional vazio é descartado e contabilizado na auditoria;
- nenhuma imputação de profissional ou de vínculo;
- resultado primário em contagem natural, sem winsorização;
- winsorização simétrica de mudanças a 1% será apenas diagnóstico de quebras
  cadastrais, sempre junto do resultado integral.

## 9. Módulo clínico e próximos portões

O SIH não bloqueia a força de trabalho. Ele bloqueia apenas cirurgias e
resolutividade: C3-02B possui 673 de 675 arquivos, pois `RDAC2606.dbc` e
`RDRR2606.dbc` não estavam no FTP oficial. Os painéis preliminares não são
insumo autorizado, e as ausências não viraram zeros.

C3-04/SIA não foi acionado: ecocardiografia não substitui automaticamente um
módulo SIH incompleto. Quando os dois arquivos aparecerem, C3-02B poderá ser
reexecutado e o subprotocolo clínico congelado sem alterar a família principal.

A próxima ação analítica é somente atualizar o CNES até `202703`, validar seis
meses comuns e executar o protocolo sem redesenho. Até lá, qualquer estimativa
de efeito do ciclo 3 permanece proibida.

## 10. Reprodutibilidade e linguagem

O script `scripts/avaliacao_ciclo3/03_auditar_pre_e_potencia.py` reconstrói
painéis balanceados, pesos, placebos, equivalência e MDE. A rotina within foi
comparada a uma regressão independente de dummies com diferença inferior a
`1e-10`; clusters e bootstrap são determinísticos sob semente fixa. Hashes de
entradas e artefatos estão em
`output/avaliacao_ciclo3/registro_pre_analise.json`.

Linguagem autorizada no futuro: “diferença-em-diferenças ajustada”, “estimando
causal sob tendências paralelas condicionais” e “resultado compatível com”.
Linguagem vedada: “sorteio”, “experimento natural”, “efeito de participar”,
“retenção de bolsistas” sem assinatura completa, ou causalidade definitiva
baseada apenas em `p>0,05` no pré.
