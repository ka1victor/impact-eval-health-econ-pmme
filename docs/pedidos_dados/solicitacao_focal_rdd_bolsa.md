# Solicitação focal — regra da faixa de atração, vagas, inscrições e eventos do PMM-E

> **Estado:** `AUTORIZADA PELO AUTOR EM 21/09/2026 — ENVIO PENDENTE DO ATO DO AUTOR`.
> O texto abaixo está pronto para ser colado no canal. A submissão exige
> autenticação pessoal do requerente e é ato do autor: nenhuma sessão de agente
> envia, aceita termos ou faz login. Este texto não aceita termos, não autoriza
> transferência de dados e não contém dados pessoais.

## Prioridade revista em 21/09/2026 — o item indispensável mudou

**A prioridade de 09/09/2026 está superada.** Ela elegia como item indispensável
o escore administrativo de IVS. A leitura do edital em 14/09/2026 mostrou que
pedir só o escore traria, em boa parte, algo que já se tem:

- a cláusula **11.1.4** já publica a regra que liga categoria de IVS a faixa, e
  ela é o **piso** da bolsa, não o critério;
- a cláusula **11.1.3** diz que o valor segue "critérios de **localização** e
  vulnerabilidade definidos de acordo com a faixa de atração definida no
  **Anexo IV** no site do Mais Médicos";
- a divergência entre faixa anunciada e categoria de IVS é estritamente
  unidirecional: nenhum município recebe menos do que a categoria manda e 177
  recebem mais. Não é ruído de vintagem, que erraria nos dois sentidos.

Logo, **o documento operativo é o Anexo IV**, e ele não está no repositório. O
item indispensável deste pacote passa a ser o Anexo IV e os critérios de
localização da cláusula 11.1.3. O escore de IVS continua sendo pedido, porque
fixa vintagem, precisão e arredondamento, mas deixou de ser o gargalo.

Detalhamento em
[`../05_identificacao/14_plano_implementacao_rdd_bolsa.md`](../05_identificacao/14_plano_implementacao_rdd_bolsa.md),
seção "O que o edital de fato diz", e em
[`../05_identificacao/16_sintese_achados_e_novo_plano_causal.md`](../05_identificacao/16_sintese_achados_e_novo_plano_causal.md),
seção 3.5.1.

## Texto principal sugerido

Solicito, para fins de pesquisa e avaliação independente de política pública, os
dados e a documentação necessários para reconstruir a regra do incentivo de
atração do Projeto Mais Médicos Especialistas (PMM-E) e o funil administrativo
de candidaturas. O período solicitado vai de 24/07/2025 até a data desta
solicitação, incluindo versões vigentes e substituídas. Caso esta unidade não
seja a custodiante, solicito encaminhamento interno ao setor competente.

**Itens indispensáveis, em ordem de utilidade.** (1) O **Anexo IV do Edital
SGTES/MS nº 3/2025**, em todas as versões vigentes e substituídas, com a faixa de
atração atribuída a cada município, a data de vigência de cada versão e o
endereço de publicação; este é o documento citado pela cláusula 11.1.3 do próprio
edital e é o que determina o valor efetivamente anunciado. (2) A descrição dos
**critérios de localização** da cláusula 11.1.3: quais são, com que fonte e
vintagem são medidos, como se combinam com a categoria de vulnerabilidade da
cláusula 11.1.4, se a promoção é de uma faixa ou de mais de uma, e se há exceções
ou decisões caso a caso. (3) O **escore de vulnerabilidade efetivamente
aplicado** por município, com vintagem, fonte, precisão, arredondamento, limiar,
categoria e faixa resultante. (4) A **folha de pagamento do incentivo de
atração**, agregada por município e competência, com valor efetivamente pago,
número de beneficiários e vigência, para distinguir valor anunciado de valor
recebido.

**Itens complementares.** (5) Cadastro e histórico versionado das vagas, com
identificador pseudonimizado estável; (6) universo de inscrições, inclusive
inválidas, retiradas e não publicadas, com opções escolhidas e conjunto elegível
quando reconstruível; e (7) log de confirmação, recusa, homologação, entrada,
afastamento, retorno, transferência, saída e reocupação, com chaves
pseudonimizadas estáveis.

Não se solicitam nome, CPF, CNS, CRM, endereço, data de nascimento, conta
bancária ou outro identificador civil. A folha de pagamento é solicitada apenas
em agregado por município e competência, sem qualquer identificação individual.
Para a regra de desempate do cutoff de seleção, solicita-se apenas indicador
derivado de prioridade na mesma UF e distância etária em dias ao cutoff,
calculados pelo controlador, sem revelar localidade pessoal ou data de
nascimento.

Solicitam-se arquivos CSV UTF-8, dicionário, data de corte, histórico de
revisões, versão do esquema, manifesto e SHA-256. Documentos normativos podem ser
fornecidos em PDF, desde que acompanhados da data de vigência. Vazio/`NULL`, zero
e não aplicável devem ser distinguíveis. Se o nível de vaga individual ou os
microdados não puderem ser fornecidos, peço que seja adotada a alternativa
hierarquizada descrita nos anexos e que toda supressão seja quantificada por
tabela, período e motivo.

A finalidade imediata é reconstruir a regra de atribuição da faixa de atração, de
modo a testar se o adicional anunciado pode ser identificado por um desenho
quase-experimental. O critério publicado sobre vulnerabilidade, sozinho,
reproduz 191 das 368 faixas municipais observadas, o que impede a reconstrução da
regra a partir de fontes públicas. O segundo desenho, condicionado à
reconstrução integral dos desempates, avalia o efeito local de ganhar a primeira
opção sobre início e presença posterior. Não se solicita que o órgão produza
estimativas causais.

## Anexos técnicos que acompanham a solicitação

1. [`vagas_e_regra_ivs.md`](vagas_e_regra_ivs.md) — três tabelas, chaves,
   versões e teste objetivo de completude;
2. [`eventos_e_ponte_cnes.md`](eventos_e_ponte_cnes.md) — universo de
   inscrições, escolhas, eventos e ligação minimizada;
3. [`cutoff_selecao_causal.md`](cutoff_selecao_causal.md) — subconjunto focal
   de desempates e outcomes administrativos;
4. [`layouts_requisitados.md`](layouts_requisitados.md) — contrato técnico
   comum de grãos, chaves, domínios e integridade.

## Roteiro de envio

Passos do ato, que é do autor:

1. Acessar o [Fala.BR](https://falabr.cgu.gov.br/) e autenticar-se pelo gov.br.
2. Abrir manifestação na modalidade **Acesso à Informação**, órgão destinatário
   `Ministério da Saúde`.
3. Colar a seção "Texto principal sugerido" no campo de detalhamento. Se o campo
   truncar, manter os itens de 1 a 4 no corpo e anexar o restante.
4. Anexar os quatro anexos técnicos acima.
5. Não aceitar termo que restrinja publicação de resultados agregados sem antes
   registrar a restrição neste documento.
6. Registrar abaixo a data e o protocolo, e então acionar
   `scripts/rdd_bolsa/` conforme a triagem, quando a resposta chegar.

## Campos a preencher no momento do envio

- canal: [Fala.BR](https://falabr.cgu.gov.br/), modalidade **Acesso à
  Informação**; envio `AUTORIZADO PELO AUTOR EM 21/09/2026`, `PENDENTE DE
  EXECUÇÃO PELO AUTOR`;
- órgão destinatário: `Ministério da Saúde`; unidade custodiante interna ainda
  deve ser confirmada pelo SIC;
- data de envio: `PENDENTE`;
- protocolo: `PENDENTE`;
- prazo legal: 20 dias corridos a partir do protocolo, prorrogável por mais 10
  mediante justificativa;
- restrições ou termos apresentados pelo canal: `PENDENTE DE REVISÃO`.

O [serviço oficial do SIC/MS](https://www.gov.br/pt-br/servicos/solicitar-acesso-a-informacao-no-servico-de-informacao-ao-cidadao-do-ministerio-da-saude-sic-ms?id=11966&origem=servico)
indica o Fala.BR como canal eletrônico, exige autenticação do requerente e
informa o acompanhamento pelo protocolo. Se o sistema estiver indisponível, a
própria página informa `sic@saude.gov.br` como contato de contingência. Esta
confirmação do canal não autoriza login, aceite de termos ou envio pelo projeto.

O protocolo e a resposta devem ser registrados sem inserir credenciais ou
dados pessoais no repositório público.

## O que fazer quando a resposta chegar

A triagem é automática e já está escrita. Depositar os arquivos recebidos em
`data/raw/administrativo_rdd_bolsa/` e executar:

```bash
.venv/bin/python scripts/rdd_bolsa/03_triagem_resposta_administrativa.py
```

A triagem grava o estado em
`output/rdd_bolsa/triagem_resposta_administrativa.json`, hoje em
`AGUARDANDO_RECEBIMENTO`, e decide se o R1 pode ser reexecutado. Ela **não**
imputa ausência como zero e **não** libera estimação por conta própria: o
controlador `02_controlar_execucao_plano_causal.py` mantém R2 a R5 bloqueados
enquanto o R1 não for aprovado. O R1 hoje está reprovado e pendente de
reconstrução, com 191 de 368 faixas reproduzidas. Resposta parcial, negativa ou
omissa é resultado a registrar, não motivo para relaxar o portão.
