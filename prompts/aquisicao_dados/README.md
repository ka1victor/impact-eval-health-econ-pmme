# Sprint extraordinário de aquisição de dados

Esta pasta transforma os bloqueios encontrados em
[`docs/auditorias/02_disponibilidade_dados.md`](../../docs/auditorias/02_disponibilidade_dados.md)
em tarefas independentes de aquisição. O sprint ocorre **depois dos prompts 01 e
02 e antes do prompt 03**. Seu objetivo é descobrir e preservar dados; nenhum
prompt desta pasta estima efeitos.

## Por que interromper a sequência original

O outcome primário exige spells de cobertura por vaga e a análise de capacidade
líquida exige vínculos mensais. Hoje faltam identificador estável da vaga, log de
eventos, ponte pseudonimizada PMM-E–CNES, regra administrativa exata do IVS e
pagamentos mensais. Congelar agora um protocolo incondicional daria falsa
precisão: a unidade, o tratamento e até a possibilidade de medir o outcome ainda
dependem dessas aquisições.

## Ordem e paralelismo

```text
Auditorias 01 e 02 incorporadas
             |
             +--> A01 vagas e versões públicas ---------+
             +--> A02 seleção e trajetória pública -----+
             +--> A03 IVS/regra administrativa ---------+--> A05R saneamento
             +--> A04 pagamentos públicos --------------+          |
             +--> A05 CNES mensal -----------------------+          v
                                                           A06 integração e portão
                                                                    |
                                                                    v
                                                           A07 pedidos administrativos
                                                                        |
                                                                        v
                                                               Prompt 03, se liberado
```

A01–A05 podem rodar simultaneamente **somente em worktrees ou tarefas com
worktrees isolados**, todos partindo do mesmo commit que contém as auditorias 01
e 02. Subagentes que compartilham o mesmo diretório não devem ser disparados em
paralelo: embora os arquivos de saída sejam separados, commits e mudanças de
estado do Git continuam compartilhados.

A05R começa depois que os cinco commits tiverem sido incorporados e corrige as
falhas documentadas na revisão pré-A06. A06 só começa depois que A05R declarar
suas entradas aptas. A07 começa depois de A06, porque deve pedir somente as
lacunas que restarem. O prompt 03 só começa se o portão de A06 disser que o
tratamento e o outcome são mensuráveis; caso contrário, aguarda-se a resposta
administrativa.

## Responsabilidade exclusiva de cada agente

| Prompt | Objeto | Diretório bruto exclusivo | Manifesto exclusivo |
|---|---|---|---|
| A01 | vagas e versões | `data/raw/aquisicao/vagas/` | `output/aquisicao/a01_manifesto_vagas.json` |
| A02 | seleção e trajetória | `data/raw/aquisicao/trajetoria/` | `output/aquisicao/a02_manifesto_trajetoria.json` |
| A03 | IVS e regra aplicada | `data/raw/aquisicao/ivs_regra/` | `output/aquisicao/a03_manifesto_ivs_regra.json` |
| A04 | regras e pagamentos | `data/raw/aquisicao/pagamentos/` | `output/aquisicao/a04_manifesto_pagamentos.json` |
| A05 | CNES mensal | `data/raw/cnes/` | `output/aquisicao/a05_manifesto_cnes.json` |
| A05R | saneamento | corrige apenas falsos brutos e proveniência | revisa A01–A05 |
| A06 | integração | não adquire brutos | `output/aquisicao/portao_integrado.json` |
| A07 | pedidos administrativos | não adquire nem envia | não se aplica |

Os agentes A01–A05 não alteram `README.md`, `run_all.py`, os relatórios das
auditorias 01–02 nem manifestos de outro agente. Fontes já preservadas podem ser
referenciadas por hash, sem serem copiadas ou regravadas. Somente A06 atualiza a
documentação compartilhada, exceto A05R, que pode corrigir os produtos A01–A05 e
registrar o saneamento.

## Contrato comum de aquisição

Cada agente de aquisição deve:

1. ler `AGENTS.md`, `CLAUDE.md`, o relatório da auditoria 02, este README e seu
   prompt integralmente;
2. usar apenas fontes oficiais ou repositórios arquivísticos cuja proveniência e
   URL original possam ser demonstradas;
3. preservar os bytes obtidos sem alterar arquivos brutos existentes;
4. registrar URL original, URL de recuperação, data/hora, cobertura, unidade,
   tamanho, MIME, SHA-256, licença/restrição e resultado da validação;
5. versionar o script de aquisição e fazê-lo idempotente: não sobrescrever um
   arquivo cujo conteúdo remoto mudou;
6. diferenciar `não publicado`, `link quebrado`, `acesso negado`, `não aplicável`
   e `zero observado`;
7. produzir um relatório de cobertura e esquema, sem imputar campos ausentes;
8. evitar nomes e documentos pessoais em outputs processados quando bastar uma
   chave pseudonimizada;
9. não fazer vinculação probabilística como se fosse uma chave administrativa;
10. validar os arquivos, fazer commit próprio e não fazer push ou merge.

Download concluído não é critério de sucesso. Uma frente só resolve um bloqueio
se a fonte tiver unidade, período, chaves, estados e definições compatíveis com o
estimando. Resultado negativo bem documentado também é uma entrega válida.

## Como coordenar

1. Crie cinco worktrees a partir do mesmo commit e entregue A01–A05, um por
   agente.
2. Incorpore os cinco commits; como os caminhos são exclusivos, a ordem não
   importa.
3. Os ZIPs grandes do A05 não entram no Git. Antes de remover sua worktree,
   preserve `data/raw/cnes/` na worktree principal ou execute ali novamente o
   script idempotente; aceite os arquivos somente se os hashes coincidirem com o
   manifesto A05.
4. Rode `run_all.py` e confira que os três dados observados originais mantiveram
   seus hashes.
5. Entregue A05R a um agente revisor no estado combinado e incorpore seu commit
   somente se a revisão ficar apta.
6. Entregue A06 a um agente integrador no estado saneado e com o bruto A05
   disponível.
7. Se houver lacunas administrativas, entregue A07 no commit de A06.
8. Só então decida entre executar o prompt 03 ou aguardar os pedidos.
