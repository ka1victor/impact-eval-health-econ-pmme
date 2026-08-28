# A05R — Saneamento de A01–A05 antes do portão A06

## Pré-requisitos

Trabalhe a partir do commit que contém A01–A05 e a revisão crítica em
`docs/auditorias/aquisicao/revisao_pre_a06.md`. Leia integralmente:

- `AGENTS.md` e `CLAUDE.md`;
- `prompts/aquisicao_dados/README.md`;
- os prompts A01–A05;
- os cinco relatórios em `docs/auditorias/aquisicao/`;
- todos os scripts e manifestos A01–A05;
- `docs/auditorias/01_regra_institucional.md` e
  `docs/auditorias/02_disponibilidade_dados.md`.

## Missão

Sanear proveniência, coerência e linguagem dos produtos A01–A05 para que um
agente posterior possa executar A06 sobre entradas confiáveis. **Não execute A06,
não estime efeitos e não force a liberação do estudo.**

O resultado esperado não é “fazer os dados parecerem completos”. É deixar claro
o que foi realmente adquirido, o que é derivado, o que permanece ausente e quais
conclusões são permitidas.

## Regras gerais

- Use apenas fontes primárias oficiais para afirmações normativas, financeiras e
  administrativas. Em buscas técnicas, registre consultas e URLs exatas.
- Um hash de arquivo criado pelo agente não demonstra proveniência oficial.
- Fonte não localizada deve permanecer ausente; nunca reconstrua “bruto” a partir
  de valores digitados no código.
- Tabela derivada pertence a `output/`, com linhagem até as fontes; não a
  `data/raw/`.
- Não desabilite verificação TLS.
- Preserve bytes oficiais. Configure `.gitattributes` quando arquivos textuais
  brutos rastreados pelo Git não puderem sofrer conversão de fim de linha.
- Não altere os três dados observados originais.
- Não baixe as 23 competências CNES restantes nesta tarefa.
- Não faça push ou merge.

## Etapa 0 — fotografia e testes iniciais

Antes de editar:

1. registre commit, status e hashes dos três dados originais;
2. valide todos os JSONs e compile os scripts;
3. confira os hashes dos manifestos A01–A05, inclusive os três ZIPs CNES;
4. leia o diff dos commits A01–A05 e identifique qualquer mudança posterior de
   bytes ou manifesto.

Documente o ponto de partida em
`docs/auditorias/aquisicao/saneamento_pre_a06.md`.

## Etapa 1 — A01: preservar e limitar a unidade

A01 não deve ser refeito sem evidência de erro nos arquivos oficiais.

- preserve os XLSX e hashes atuais;
- revise relatório e inventário para diferenciar:
  - linha/célula `CNES–curso`;
  - quantidade de vagas imediatas ou de reserva;
  - vaga física individual, ainda sem `id_vaga`;
- onde aparecer “novas vagas” com base apenas em diferença de chaves, substitua
  por “novas células de oferta” e reporte separadamente as quantidades;
- não chame `CNES + curso` de chave estável da vaga.

## Etapa 2 — A02: incorporar A01 e reexecutar

Corrija `scripts/aquisicao/a02_adquirir_trajetoria.py` para:

- reconhecer os arquivos recuperados em `data/raw/aquisicao/vagas/`;
- usar o slug oficial ativo, sem manter o arquivo recuperado como HTTP 404;
- não copiar bruto existente desnecessariamente;
- recalcular a matriz de eventos da primeira chamada de 2025;
- distinguir alocação/classificação publicada de candidatura completa;
- atualizar manifesto, matriz e relatório de forma determinística.

A conclusão sobre spells deve ser reavaliada, mas não presumida alterada. Se
aceite, recusa, afastamento e saída continuarem ausentes, mantenha
`cobertura_90/120/180` como não mensurável.

## Etapa 3 — A03: reparar fontes e inferência

Corrija `scripts/aquisicao/a03_adquirir_ivs_regra.py` e seus produtos:

1. remova `ssl._create_unverified_context()`;
2. para Portarias 7.177/2025, 7.266/2025 e Atlas do Ipea, tente preservar os
   documentos oficiais reais em HTML ou PDF;
3. se uma fonte falhar, registre status/erro; não escreva um resumo local e o
   classifique como `registro_oficial_preservado`;
4. mova resumos analíticos necessários para `output/`, marcados como derivados;
5. garanta que os hashes do relatório coincidam com o manifesto e os bytes
   atuais;
6. preserve brutos textuais sem normalização de fim de linha;
7. torne outputs determinísticos ou separe timestamps voláteis;
8. substitua “42,56% demonstra classificação multicritério” por uma conclusão
   compatível com múltiplas explicações;
9. declare somente que o score/vintagem/precisão administrativos não foram
   reconstruídos e que o RDD não é liberado com os dados atuais.

Não substitua o IVS 2010 por outro indicador.

## Etapa 4 — A04: refazer a proveniência financeira

Trate A04 como reprovação, não como ajuste cosmético.

- remova de `data/raw/aquisicao/pagamentos/` os arquivos produzidos a partir de
  constantes hard-coded quando não houver resposta oficial correspondente; o
  histórico do Git já preserva a versão anterior;
- elimine tabelas de valores orçamentários digitadas no script;
- procure extratos oficiais somente em fontes primárias, preservando a resposta
  original e registrando endpoint, consulta, filtros, exercício, unidade,
  posição temporal e hash;
- uma página inicial de domínio ou a expressão “SIOP e Portal da Transparência”
  não é URL de proveniência suficiente;
- se a extração oficial não puder ser obtida, não publique valores exatos:
  registre a fonte consultada, a falha e a granularidade disponível;
- grades de bolsa derivadas de editais devem ir para `output/`, com referência
  por linha ao edital/versão correspondente;
- separe valor anunciado, devido, empenhado, liquidado e pago;
- não atribua campos internos ao SGP sem documentação oficial;
- remova afirmações de que um ITT causal foi “identificado”. A conclusão máxima
  desta frente é qual versão do tratamento financeiro pode ser observada.

Atualize script, manifesto, matriz e relatório A04. Nenhum arquivo local criado
pelo script pode ser descrito como bruto oficial.

## Etapa 5 — A05: corrigir universo e limitar ao piloto

Preserve e revalide os três ZIPs CNES atuais. Não faça o download integral.

Corrija `scripts/aquisicao/a05_adquirir_cnes.py` para:

- apresentar separadamente:
  - CNES do snapshot nominal de ativos;
  - CNES do universo de quadros de vagas A01, por versão final escolhida;
- realmente ler os quadros usados para formar o segundo universo;
- reportar denominadores e perdas de normalização;
- remover a inferência de que unidades ausentes em 202406 foram inauguradas,
  salvo se data de abertura for observada e documentada;
- retirar a recomendação de DiD/event study: disponibilidade de painel não
  valida desenho causal;
- declarar explicitamente `3 de 26 competências adquiridas`;
- classificar A05 como `piloto de esquema e aquisição pública parcial`;
- declarar que o painel integral fica adiado até haver ponte PMM-E–CNES ou outra
  decisão explícita do portão.

Atualize o dicionário apenas se a correção mudar seu conteúdo. Não transforme
CNES cadastral em presença ou trabalho efetivamente realizado.

## Etapa 6 — reconciliação transversal

Depois das correções:

- elimine contradições entre A01 e A02;
- reconcilie hashes A03 entre relatório, manifesto e arquivos;
- confirme que A04 distingue fonte bruta de derivação;
- confirme que A05 não chama 518 CNES do snapshot de “universo ofertado”;
- procure nos relatórios linguagem indevida de RDD, ITT, DiD ou event study
  identificado/recomendado;
- atualize `TODO.md` e os READMEs somente para refletir o saneamento concluído;
- não crie `portao_integrado.json` nem
  `docs/auditorias/03_portao_apos_aquisicao.md`: esses pertencem ao A06.

## Entregáveis

- `docs/auditorias/aquisicao/saneamento_pre_a06.md`, com cada achado, correção e
  evidência;
- scripts, manifestos, matrizes e relatórios A01–A05 corrigidos;
- brutos oficiais efetivamente adquiridos e suas regras de preservação;
- remoção dos falsos brutos/artefatos sem proveniência atual;
- checklist final com `passou`, `parcial` ou `falhou` para cada frente;
- decisão binária: `ENTRADAS APTAS PARA A06` ou
  `SANEAMENTO AINDA INCOMPLETO`.

## Critérios de aceite

Antes de declarar as entradas aptas:

1. `run_all.py` passa;
2. todos os scripts compilam e JSONs são válidos;
3. os hashes de cada fonte local coincidem com os manifestos;
4. os três dados observados originais mantêm seus hashes;
5. não há dado hard-coded apresentado como extração oficial;
6. não há resumo local apresentado como byte oficial;
7. A02 usa as fontes recuperadas por A01;
8. A03 não atribui uma causa única à divergência de categorias;
9. A04 não declara efeito causal identificado;
10. A05 distingue piloto, snapshot ativo e universo de vagas;
11. `git diff --check` passa e a worktree fica limpa após o commit.

Se algum item falhar, marque `SANEAMENTO AINDA INCOMPLETO` e não faça A06.

Ao final, faça commit próprio e informe hash, arquivos removidos/adicionados,
fontes que não puderam ser obtidas e decisão. Não faça push ou merge.

