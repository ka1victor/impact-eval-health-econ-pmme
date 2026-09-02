# Prompt 02 — Auditoria e aquisição dos dados

Você está trabalhando no repositório `impact-eval-health-econ-pmme`.

Leia integralmente `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/04_dados/02_inventario_dados_por_outcome.md`, `docs/01_pergunta_escopo/04_escopo_eficacia_operacional.md` e `docs/06_execucao/05_roadmap_execucao.md`.

## Missão

Descobrir se o estudo prioritário pode ser executado e obter, quando públicos e acessíveis, os insumos necessários. Não estime efeitos.

Comece auditando as três bases existentes sem alterá-las. Depois procure fontes oficiais para:

### Base A — vagas e trajetória administrativa

- universo de vagas ofertadas;
- vaga, CNES, município, especialidade e chamamento;
- faixa e valor do incentivo;
- candidaturas, convocação, aceite e recusa;
- entrada, afastamento, transferência e saída;
- identificador estável da vaga;
- identificador pseudonimizado do profissional;
- datas dos eventos.

### Base B — CNES mensal

- vínculos e CBO;
- carga horária;
- estabelecimento e município;
- vínculos anteriores e simultâneos;
- infraestrutura existente antes do PMM-E.

Para cada campo, classifique:

- disponível localmente;
- disponível publicamente;
- acessível somente por pedido administrativo/LAI;
- não localizado;
- inadequado para o estimando.

Quando houver download oficial seguro e de tamanho razoável, crie etapa reproduzível e preserve o arquivo bruto sem modificá-lo. Para arquivos grandes, prefira script de aquisição, manifesto e checksums em vez de versionar o bruto. Nunca gere dados sintéticos para preencher lacunas.

## Entregáveis

- `docs/auditorias/02_disponibilidade_dados.md`;
- manifesto de fontes, URLs, datas, cobertura, unidades e hashes;
- matriz `variável × fonte × disponibilidade`;
- diagnóstico sobre janelas possíveis de 90, 120 e 180 dias;
- viabilidade de vincular cadastro nominal, vagas e CNES;
- lista precisa de pedidos administrativos ainda necessários;
- conclusão: executável agora, executável parcialmente, aguardando dados ou bloqueado.

## Limites

- Não estimar efeitos.
- Não reinterpretar ausência como zero sem documentação da fonte.
- Não alterar os três arquivos observados existentes.
- Não baixar bases de WP3, WP4 ou WP5.
- Não fazer push ou merge.

Ao final, valide tudo, faça commit próprio e informe hash, arquivos alterados e bloqueios.
