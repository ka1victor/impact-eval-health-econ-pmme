# 18. Protocolo R3 da RDD da bolsa pelo IVS administrativo — RASCUNHO

> **Estado em 05/10/2026: rascunho, não congelado.** Nada aqui foi estimado e
> nenhum outcome foi aberto por faixa ou por IVS administrativo. O congelamento é
> decisão do autor e se materializa em `output/rdd_bolsa/registro_pre_analise.json`,
> gravado por script versionado, com hashes de todas as entradas, em commit
> anterior a qualquer leitura de desfecho. O controlador
> `02_controlar_execucao_plano_causal.py` recusa resultado R4 sem esse registro.
>
> Base: [`../auditorias/15_portao_r1_r2_ivs_administrativo.md`](../auditorias/15_portao_r1_r2_ivs_administrativo.md).

## 1. Pergunta e estimando

> Próximo aos cortes administrativos de IVS, qual é o efeito de **anunciar R$ 5 mil
> mensais a mais** de bolsa sobre a procura e o preenchimento das vagas do PMM-E?

- **Tratamento:** salto do valor anunciado. Em 0,300/0,301, de R$ 10 mil para
  R$ 15 mil; em 0,400/0,401, de R$ 15 mil para R$ 20 mil. Primeiro estágio sharp:
  4.103 de 4.103 município–onda–versão seguem a regra.
- **Estimando:** intenção de tratar da oferta anunciada, local a cada corte. Não é
  efeito do valor recebido (não observado), da participação no PMM-E, do IVS nem
  do Agora Tem Especialistas.
- **População:** células CNES–curso publicadas nas ondas de oferta com resultado
  disponível, em municípios dentro da banda.
- **Running variable:** IVS administrativo do quadro do PMMB 2026, três casas
  decimais; o valor igual ao corte fica à esquerda.

## 2. Decisões que o autor precisa tomar antes do congelamento

| # | Decisão | Proposta deste rascunho | Por quê |
|---|---|---|---|
| 0 | Running variable | trocar o IVS 2010 do Atlas pelo IVS administrativo da SGTES | o `CLAUDE.md` fixa o IVS 2010 como canônico e exige justificativa e autorização do autor para trocá-lo; a justificativa é o R1: o IVS administrativo reproduz 100% da atribuição e o IVS 2010 erra 48% |
| 1 | Outcome primário | célula com ao menos um candidato **alocado** na onda | existe em todas as ondas e mede a margem de entrada da pergunta |
| 2 | Outcomes secundários | candidaturas de 1ª opção por célula; célula com alguma candidatura; confirmação ou homologação (só 2025, outcome aprovado em A1) | procura é o desfecho preferido do plano 16 e as listas publicam as candidaturas |
| 3 | Unidade | município–onda, proporção de células com alocação, peso igual por município–onda; célula com agrupamento municipal em robustez | o tratamento é municipal (plano 14, seção 6) |
| 4 | Ondas | 2025 c1 ch1, 2025 c1 ch2, 2026 c2 ch1 e 2026 c2 ch2 no principal; 2026 c3 ch1 só com autorização expressa | todas seguem a mesma regra e nenhuma faixa muda entre elas; o ciclo 3 está congelado no `CLAUDE.md` e o resultado dele é *sub judice*. O protocolo do ciclo 3 usa o CNES e não a alocação, mas a inclusão é decisão do autor |
| 5 | Estimador principal | local-linear, inclinações separadas, kernel triangular, banda fixa 0,050 | a randomização local não balanceia com suporte útil (R2) |
| 6 | Robustez de banda | 0,030; 0,075; 0,100 | grade do R2, sem escolha pelo resultado |
| 7 | Estimativa conjunta | cortes empilhados, intercepto e inclinações por corte, salto comum de R$ 5 mil | mesma dose; é o que dá potência |
| 8 | Hipótese principal | uma: o salto comum. Os dois cortes separados ficam com Holm | evita duas manchetes com MDE de 30 p.p. |
| 9 | Covariadas | nenhuma no principal; `capital`, IVS capital humano 2010 e log da população 2022 em robustez; capitais excluídas em robustez | covariadas sinalizadas no R2 |
| 10 | Inferência | erro-padrão agrupado por município; intervalo robusto a viés como complemento | município é a unidade de atribuição |
| 11 | Placebos | o mesmo estimador em 0,200 e 0,500 | a categoria muda e a bolsa não |
| 12 | Linguagem | a do plano 14, seção 9, com "local" e "anunciado"; nulo com MDE alto é "não detectado", não "sem efeito" | potência limitada |

## 3. Construção dos desfechos — antes de abrir

Cada onda tem uma planilha de resultado com candidato × opção (1ª ou 2ª) e
situação. A construção precisa ser escrita e testada só com a estrutura das
planilhas, sem cruzar com faixa ou IVS:

| Onda | Arquivo | Linhas | Situações publicadas |
|---|---|---:|---|
| 2025 c1 ch1 | `2025_ciclo1_chamada1_alocacao_retificada.xlsx` | 1.671 | classificado ou não; local confirmado, desconsiderado ou nenhum |
| 2025 c1 ch2 | `2025_ciclo1_chamada2_classificacao_final.xlsx` | 757 | alocado ou não alocado |
| 2026 c2 ch1 | **ausente do repositório** (só 9 remanescentes) | — | adquirir `resultado-final-pmme-2o-ciclo-25-05.xlsx` |
| 2026 c2 ch2 | `2026_ciclo2_chamada2_resultado_final.xlsx` | 1.053 | alocado ou cadastro reserva |
| 2026 c3 ch1 | `2026_ciclo3_chamada1_resultado_final_sub_judice.xlsx` | 4.532 | alocado, cadastro reserva ou sub judice |

Pendências de construção:

1. definir se células só de cadastro reserva entram no denominador de alocação;
2. tratar o resultado sub judice do ciclo 3 (proposta: versão publicada, com
   reestimação obrigatória se a versão final mudar);
3. registrar se as listas contêm todas as candidaturas válidas ou só as
   classificadas — a da chamada 1 de 2025 inclui não classificados;
4. readquirir o CNES se o estoque prévio de especialistas for entrar como
   covariada.

## 4. Potência declarada antes

Do R2, com município como unidade e linha de base hipotética de 30%: MDE de
31,5 p.p. (0,300) e 32,9 p.p. (0,400) na banda 0,050; 22,8 p.p. no salto comum
na banda 0,050 e 16,5 p.p. na 0,100. O registro R3 deve recalcular o MDE para a
unidade escolhida (município–onda), com a correlação entre ondas do mesmo
município tratada de forma conservadora, **antes** de abrir o desfecho. Se o MDE
do salto comum ficar acima de 15 p.p., a manchete é rebaixada a exploratória e o
texto diz que efeitos menores não seriam detectados.

## 5. Ameaças que o protocolo precisa nomear

- **Conhecimento prévio.** Comparações brutas e ajustadas de preenchimento por
  faixa já foram vistas (A4 e conversas de 21/09 a 05/10/2026). São comparações
  entre faixas inteiras, não perto dos cortes, mas o registro deve declará-las,
  como manda o plano 14, seção 5.
- **Origem do IVS administrativo.** A regra é reproduzida; a safra não. Se ela
  vier a ser documentada como posterior à publicação de 2025, o desenho de 2025
  precisa ser reavaliado.
- **Cointervenções nos mesmos cortes.** O PMMB 2026 não salta; outros programas
  que usem a categoria de IVS não foram verificados. Os placebos 0,200 e 0,500
  testam efeito de categoria sem bolsa.
- **Composição.** Em 0,400, a oferta tende a ter menos células à direita (local-
  linear p = 0,14). O resultado por célula pode carregar o número de células.
- **Mesmo município em várias ondas.** Agrupar por município; nunca tratar
  ondas como atribuições independentes.

## 6. Ordem após a autorização

O prompt operacional é
[`prompts/avaliacao_rdd_bolsa/02_congelar_protocolo_r3.md`](../../prompts/avaliacao_rdd_bolsa/02_congelar_protocolo_r3.md),
precedido da revisão de
[`prompts/integracao_rodadas_outubro_2026/`](../../prompts/integracao_rodadas_outubro_2026/README.md).


1. adquirir o resultado da 1ª chamada do ciclo 2 e preservar com hash;
2. escrever o construtor de desfechos e testá-lo só na estrutura;
3. fixar as decisões da seção 2 e calcular o MDE da unidade escolhida;
4. gravar `registro_pre_analise.json` e commitar;
5. só então estimar R4, em script separado, e publicar inclusive se nulo.
