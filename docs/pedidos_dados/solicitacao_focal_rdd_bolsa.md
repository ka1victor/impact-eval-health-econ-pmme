# Solicitação focal — regra do IVS, vagas, inscrições e eventos do PMM-E

> **Estado:** `PRONTO PARA SUBMISSÃO — NÃO ENVIADO`.
> O envio depende da escolha e autorização do canal pelo autor. Este texto não
> aceita termos, não autoriza transferência de dados e não contém dados pessoais.

## Texto principal sugerido

Solicito, para fins de pesquisa e avaliação independente de política pública,
os dados e a documentação necessários para reconstruir a regra do incentivo de
atração do Projeto Mais Médicos Especialistas (PMM-E) e o funil administrativo
de candidaturas. O período solicitado é de 24/07/2025 a 29/08/2026, incluindo
versões vigentes e substituídas. Caso esta unidade não seja a custodiante,
solicito encaminhamento interno ao setor competente.

O núcleo mínimo contém: (1) cadastro e histórico versionado das vagas, com
identificador pseudonimizado estável; (2) escore IVS efetivamente aplicado,
vintagem, precisão, arredondamento, cutoff, categoria, faixa, valor anunciado,
vigência, exceções e fonte da regra; (3) universo de inscrições, inclusive
inválidas, retiradas e não publicadas, com opções escolhidas e conjunto elegível
quando reconstruível; e (4) log de confirmação, recusa, homologação, entrada,
afastamento, retorno, transferência, saída e reocupação, com chaves
pseudonimizadas estáveis.

Não se solicitam nome, CPF, CNS, CRM, endereço, data de nascimento, conta
bancária ou outro identificador civil. Para a regra de desempate do cutoff de
seleção, solicita-se apenas indicador derivado de prioridade na mesma UF e
distância etária em dias ao cutoff, calculados pelo controlador, sem revelar
localidade pessoal ou data de nascimento.

Solicitam-se arquivos CSV UTF-8, dicionário, data de corte, histórico de
revisões, versão do esquema, manifesto e SHA-256. Vazio/`NULL`, zero e não
aplicável devem ser distinguíveis. Se o nível de vaga individual ou os
microdados não puderem ser fornecidos, peço que seja adotada a alternativa
hierarquizada descrita nos anexos e que toda supressão seja quantificada por
tabela, período e motivo.

A finalidade imediata é testar, antes de consultar outcomes, se o adicional de
R$ 5 mil anunciado nos limiares administrativos pode ser identificado por uma
regressão descontínua. O segundo desenho, condicionado à reconstrução integral
dos desempates, avalia o efeito local de ganhar a primeira opção sobre início e
presença posterior. Não se solicita que o órgão produza estimativas causais.

## Anexos técnicos que acompanham a solicitação

1. [`vagas_e_regra_ivs.md`](vagas_e_regra_ivs.md) — três tabelas, chaves,
   versões e teste objetivo de completude;
2. [`eventos_e_ponte_cnes.md`](eventos_e_ponte_cnes.md) — universo de
   inscrições, escolhas, eventos e ligação minimizada;
3. [`cutoff_selecao_causal.md`](cutoff_selecao_causal.md) — subconjunto focal
   de desempates e outcomes administrativos;
4. [`layouts_requisitados.md`](layouts_requisitados.md) — contrato técnico
   comum de grãos, chaves, domínios e integridade.

## Campos a preencher no momento do envio

- canal recomendado: [Fala.BR](https://falabr.cgu.gov.br/), na modalidade
  **Acesso à Informação**; envio `PENDENTE DE AUTORIZAÇÃO DO AUTOR`;
- órgão destinatário: `Ministério da Saúde`; unidade custodiante interna ainda
  deve ser confirmada pelo SIC;
- data de envio: `PENDENTE`;
- protocolo: `PENDENTE`;
- restrições ou termos apresentados pelo canal: `PENDENTE DE REVISÃO`.

O [serviço oficial do SIC/MS](https://www.gov.br/pt-br/servicos/solicitar-acesso-a-informacao-no-servico-de-informacao-ao-cidadao-do-ministerio-da-saude-sic-ms?id=11966&origem=servico)
indica o Fala.BR como canal eletrônico, exige autenticação do requerente e
informa o acompanhamento pelo protocolo. Se o sistema estiver indisponível, a
própria página informa `sic@saude.gov.br` como contato de contingência. Esta
confirmação do canal não autoriza login, aceite de termos ou envio pelo projeto.

O protocolo e a resposta devem ser registrados sem inserir credenciais ou
dados pessoais no repositório público.
