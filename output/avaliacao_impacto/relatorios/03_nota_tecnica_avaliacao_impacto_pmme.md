# Nota técnica — vagas viram médicos e eles permanecem?

> Data da execução: 2026-09-03
> Status: **COMPARAÇÃO AJUSTADA**
> Unidade principal: município–curso–mês
> Janela: 2024-06 a 2026-07

## Pergunta e estimando

A análise pergunta se disponibilizar inicialmente uma vaga do primeiro ciclo do
PMM-E para preenchimento imediato, em vez de mantê-la apenas em cadastro de
reserva, alterou o estoque cadastral de especialistas no município. O contraste
é uma intenção de tratar administrativa dentro do mesmo quadro de vagas; não
é PMM-E versus ausência do programa e não identifica individualmente bolsistas.

## Dados corrigidos

O painel usa exclusivamente os 26 arquivos mensais do CNES e todos os
estabelecimentos dos 368 municípios da
amostra. `CO_PROFISSIONAL_SUS` é deduplicado no município–curso–mês. A lista
nominal do PMM-E não é somada ao CNES, nenhuma carga horária é presumida e
competências ausentes interrompem o pipeline.

O universo confirmatório possui
587 células
município–curso. A especificação com variação dentro do município usa
319 células em
93 municípios com cursos nas
duas modalidades. Ela exclui cursos cujos CBOs são compartilhados com outro
curso do ciclo. A ponte é operacional e auditável, mas não é uma crosswalk
publicada pelo Ministério da Saúde.

## Relevância administrativa

O portão foi **NAO_APROVADO** no mesmo grão e amostra da DDD. A
associação ajustada entre modalidade imediata e alocação confirmada foi
2.79 p.p. (EP 6.89;
p=0.6871). A modalidade imediata não separou a alocação na amostra identificadora; por isso, as regressões abaixo não identificam o impacto causal do programa. A diferença observada no universo
CNES–curso não substitui esse teste no grão da análise. Homologação mede uma
candidatura homologada, não entrada em exercício no CNES.

## Resultado principal

A especificação DDD confirmatória, com efeitos fixos município–curso,
município–mês e curso–mês, produziu uma diferença ajustada de
**-0.446 especialista** por célula
(EP 0.246; IC 95% [-0.934,
0.042]; p=0.0727). O intervalo deve ser
usado para avaliar tanto aumentos relevantes quanto reduções compatíveis com
os dados. Como o portão administrativo falhou na amostra identificadora, esse
número não deve ser chamado de efeito causal.

Na amostra ampliada dos 16 cursos, a estimativa foi -0.232
(IC 95% [-0.532, 0.068]). Para a
probabilidade de haver ao menos um especialista, a estimativa confirmatória foi
0.73 p.p. (IC 95% [-2.33,
3.79] p.p.).

## Dinâmica, entradas e presença posterior

Entradas exigem seis meses anteriores de ausência observada; saídas exigem três
meses posteriores consecutivos de ausência. As bordas sem seguimento são
censuradas, não preenchidas com zero.

Entre entrantes de 2025-08 a 2026-01, a presença no mesmo
município–curso seis meses depois foi
86.9% na modalidade imediata e
79.7% na reserva. Essa comparação
é descritiva porque condiciona em entrada, que pode ser afetada pelo tratamento.
A presença em doze meses permanece censurada até haver CNES até 2027-01.

## Diagnósticos de identificação

O teste conjunto dos coeficientes pré-tratamento produziu F=1.262
(p=0.2546); o maior coeficiente pré em valor absoluto foi
0.246. Não rejeitar a hipótese nula não prova tendências
paralelas. O placebo com falso início em 2025-01 estimou -0.031
(p=0.8684).

O painel regional é mantido apenas como diagnóstico descritivo. Como a exposição
é municipal e pode gerar interferência, ele não é apresentado como estimativa
causal de spillovers.

## Interpretação máxima

Esta execução não sustenta uma afirmação causal sobre o PMM-E. Ela mostra que,
na comparação ajustada escolhida, não apareceu aumento do estoque de
especialistas em municípios–cursos classificados como imediatos relativamente
aos mantidos em reserva. Isso não equivale a demonstrar que o programa não teve
efeito: o contraste perdeu relevância justamente na amostra que identifica a
DDD. O CNES mede presença cadastral total, não confirma que o profissional seja
bolsista, que cumpra horas efetivas, que produza procedimentos ou que melhore
desfechos de pacientes.

## Artefatos

- `tabelas/tabela1_estatisticas_descritivas_baseline.csv`
- `tabelas/tabela2_ddd_estatica_resultado_primario.csv`
- `tabelas/tabela3_mecanismos_fluxos_e_retencao.csv`
- `tabelas/tabela4_diagnosticos_robustez_e_redistribuicao.csv`
- `figuras/figura1_estudo_evento_ddd_dinamico.png`
- `figuras/figura2_diagnostico_redistribuicao.png`
- `figuras/figura3_trajetoria_estoque_por_modalidade.png`
- `figuras/figura4_decomposicao_mecanismos_fluxos.png`
