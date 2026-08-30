# 04. Auditoria e resultado do pipeline agregado

> **Data de corte:** 30/08/2026
> **Escopo:** ciclo 1, chamada 1; painel mensal do CNES de 2024-06 a
> 2026-07
> **Status da evidência:** **comparação ajustada, não impacto causal**

## 1. Decisão em uma frase

O painel público permite medir estoque, entradas, saídas e presença posterior
de especialistas nos municípios do quadro do PMM-E. Ele não permite, com o
contraste imediato versus reserva atualmente observado, identificar o efeito
causal do programa: a modalidade inicial não prediz alocação na mesma amostra
município–curso que identifica a DDD.

Isso é diferente de concluir que o PMM-E não teve efeito. O que falhou foi o
primeiro estágio do desenho escolhido, não necessariamente a política.

## 2. O que foi auditado e corrigido

A implementação anterior produzia números, mas não sustentava a interpretação
proposta. Os problemas abaixo eram materiais, não apenas de apresentação.

| Problema encontrado | Por que invalidava a leitura | Correção vigente |
|---|---|---|
| Uso somente dos CNES ofertantes | Confundia mudança de estabelecimento com expansão municipal | Uso de todos os CNES dos 368 municípios do quadro |
| Soma de contagens distintas por CNES | O mesmo profissional podia ser contado mais de uma vez no município | Deduplicação de `CO_PROFISSIONAL_SUS` em município–curso–mês |
| Soma da lista nominal do PMM-E ao CNES | CRM/nome e chave CNES não formam ponte determinística; havia risco de dupla contagem | Lista nominal excluída dos outcomes |
| Imputação de 40 horas aos nomes do programa | Criava FTE não observado | FTE removido desta versão; nenhuma hora é presumida |
| Reutilização do último mês quando faltava uma competência | Transformava arquivo ausente em permanência artificial | As 26 competências são obrigatórias; ausência interrompe o pipeline |
| Entrada e saída definidas pela diferença contra um único mês | Ruído cadastral mensal virava rotatividade | Entrada exige seis meses anteriores de ausência; saída exige três meses posteriores de ausência |
| Retenção calculada sem maturidade comum | Observações censuradas eram comparadas como se tivessem seguimento | Coorte de seis meses limitada a entradas de 2025-08 a 2026-01; doze meses permanece censurada |
| Ponte curso–CBO chamada de oficial | As fontes oficiais não publicam uma crosswalk pronta | Artefato marcado como ponte operacional; cursos com CBO compartilhado saem da amostra confirmatória |
| Absorção de efeitos fixos por 15 iterações sem teste | Não havia garantia de convergência numérica | Projeções alternadas até tolerância `1e-10`, com diagnóstico de médias residuais e posto |
| Portão aprovado com resultado do universo CNES–curso | O teste não correspondia ao grão e à amostra da regressão | Decisão tomada na amostra município–curso que identifica a DDD |
| Linguagem causal automática | Tendências prévias e placebo não compensam um primeiro estágio irrelevante | Nota final rebaixada para comparação ajustada |

## 3. Dados e unidades válidos

### 3.1 Oferta administrativa

O quadro inicial contém 1.295 células CNES–curso: 503 apenas imediatas, 782
apenas em reserva e 10 mistas. Depois da agregação, existem 1.184 células
município–curso em 368 municípios. Esses totais não são intercambiáveis.

A amostra confirmatória de outcomes tem 587 células município–curso. A DDD é
identificada pelos 93 municípios que possuem, simultaneamente, cursos apenas
imediatos e cursos apenas em reserva entre os cursos sem CBO compartilhado. O
portão administrativo correspondente usa 319 células município–curso desses
municípios.

### 3.2 CNES

O painel cobre exatamente 26 competências, de 2024-06 a 2026-07. Cada arquivo
mensal é exigido e lido separadamente. O outcome principal é:

```text
especialistas_mst = número de CO_PROFISSIONAL_SUS distintos
                    em qualquer CNES do município m,
                    nos CBOs operacionais do curso s,
                    na competência t
```

Zero significa que a competência existe, mas nenhum profissional elegível foi
observado na célula. Ausência nas margens de entradas, saídas e presença futura
significa censura, não zero. A continuidade mensal da chave é quantificada no
artefato de auditoria: a mediana da fração de pessoas–municípios–cursos que
permanece no mês seguinte é 99,16%, e o mínimo entre pares adjacentes é 98,65%.
Essa continuidade é compatível com chave estável, mas não elimina mudanças
cadastrais nem substitui documentação externa do identificador.

### 3.3 Ponte curso–CBO

Dez cursos entram na especificação confirmatória: 1, 2, 3, 5, 9, 12, 13,
14, 15 e 16. Seis cursos ficam apenas na sensibilidade ampliada por
compartilharem CBO com outro curso: 4, 6, 7, 8, 10 e 11.

O nome histórico do arquivo
`output/aquisicao/ponte_curso_cbo_oficial.json` é mantido por compatibilidade.
Seu conteúdo declara explicitamente
`OPERACIONAL_NAO_PUBLICADA_COMO_CROSSWALK_OFICIAL`.

## 4. Estratégia econométrica executada

A especificação é:

```text
Y_mst = alpha_ms + gamma_mt + delta_st
      + beta (Immediate_ms x Post_t) + epsilon_mst
```

com efeitos fixos município–curso, município–mês e curso–mês e inferência
agrupada por município. A janela pré vai de 2024-06 a 2025-06, julho de 2025
é transição e a janela pós vai de 2025-08 a 2026-07.

O estimando pretendido seria a intenção de tratar administrativa de tornar a
vaga imediatamente disponível, relativamente a mantê-la inicialmente em
reserva. Ele não é PMM-E versus ausência do programa, não identifica o efeito
de receber um bolsista e não identifica o efeito das faixas de bolsa.

## 5. Portão de relevância

No universo CNES–curso, a diferença bruta de alocação foi +19,17 p.p. e a
associação ajustada foi +5,97 p.p. (`p=0,0806`). Esse resultado descreve o
processo amplo, mas não identifica a regressão municipal.

Na amostra município–curso que identifica a DDD:

- diferença bruta de alocação: −3,14 p.p.;
- associação ajustada: +2,79 p.p.;
- erro-padrão: 6,89 p.p.;
- `p=0,6871`;
- IC 95%: −10,91 a +16,48 p.p.

Logo, o portão é **não aprovado**. Aprovar com o universo amplo seria uma
troca de unidade de análise depois de conhecer o resultado.

## 6. Resultados que podem ser reportados

| Resultado | Estimativa | IC 95% | Leitura permitida |
|---|---:|---:|---|
| Estoque, amostra confirmatória | −0,446 | [−0,934; 0,042] | Diferença ajustada; não efeito causal |
| Estoque, 16 cursos | −0,232 | [−0,532; 0,068] | Sensibilidade operacional |
| Cobertura de ao menos um especialista | +0,73 p.p. | [−2,33; 3,79] p.p. | Diferença ajustada |
| Entradas após seis meses de ausência | −0,073 | [−0,156; 0,011] | Mecanismo ajustado |
| Saídas após três meses de ausência | −0,018 | [−0,119; 0,082] | Mecanismo ajustado |
| Presença seis meses depois entre entrantes | 86,9% imediata; 79,7% reserva | não causal | Descritivo, condicionado à entrada |

O teste conjunto dos coeficientes pré produziu `F=1,262`, `p=0,2546`. O
placebo com falso início em 2025-01 produziu −0,031, `p=0,8684`. Esses
diagnósticos não rejeitam o desenho, mas também não recuperam a identificação
perdida no portão administrativo.

## 7. O que não pode ser concluído

- não se demonstrou que o PMM-E reduziu o número de especialistas;
- não se demonstrou que o PMM-E não funciona;
- não se estimou participação individual, FTE, horas realizadas ou produção;
- não se estimou efeito sobre espera, acesso, saúde ou custos;
- não se identificou retenção causal entre os entrantes;
- não se identificou efeito causal das faixas de bolsa;
- não se validou RDD pelo IVS;
- três competências piloto não foram tratadas como painel completo;
- presença cadastral no CNES não foi tratada como participação no PMM-E.

## 8. Decisão operacional

Esta versão agregada está concluída como diagnóstico empírico. Reestimar o
mesmo contraste com métodos sintéticos, novas janelas ou filtros escolhidos pelo
resultado não corrige a ausência de primeiro estágio.

As próximas opções substantivamente defensáveis são:

1. atualizar o CNES até 2027-01 para completar a descrição de presença em 12
   meses, sem promover essa atualização a causal;
2. obter exposição administrativa observada e vinculável, por exemplo a ponte
   pseudonimizada e o log de ocupação preparados no A07, e então formular um
   novo protocolo;
3. procurar variação institucional em ciclos posteriores somente depois de
   auditar datas, ativação de reservas e comparabilidade, sem tratar adoção
   escalonada como exógena por construção.

O prompt 03 do desenho individual permanece bloqueado. Os pedidos A07 estão
preparados e não enviados; nenhuma submissão ou contato com órgãos foi feito.
