# Prompt 03 — Congelamento do protocolo empírico

Execute somente depois que os resultados dos prompts 01 e 02 estiverem incorporados ao branch.

Leia `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/01_pergunta_escopo/04_escopo_eficacia_operacional.md`, `docs/06_execucao/05_roadmap_execucao.md` e os dois relatórios em `docs/auditorias/`.

## Missão

Transformar as auditorias em um protocolo empírico executável. Não estime resultados.

Defina e justifique:

- pergunta causal exata;
- tratamento e contraste;
- população;
- unidade de observação;
- cutoff e running variable, se aplicável;
- janela comum de acompanhamento;
- outcome primário;
- decomposições secundárias;
- definição de censura;
- regras de exclusão;
- menor efeito substantivamente relevante;
- infraestrutura prévia como única heterogeneidade confirmatória;
- análises exploratórias;
- estratégia de inferência e potência;
- linguagem máxima permitida;
- condições que invalidariam o desenho.

O protocolo deve distinguir efeito do programa, efeito do incentivo marginal, efeito de pacote e descrição de implantação.

Se os dados não permitirem `cobertura_180`, selecione a maior janela comum antes de observar efeitos. Se nem cobertura sustentada for mensurável, documente o bloqueio; não redefina silenciosamente o outcome para aproveitar a base disponível.

## Entregáveis

- `docs/07_protocolo_empirico_congelado.md`;
- tabela de estimandos e fórmulas;
- DAG ou cadeia causal mínima;
- portões de validade e regras de parada;
- decisão final: prosseguir, prosseguir parcialmente, aguardar dados ou parar;
- ajustes em README/TODO apenas se necessários para refletir a decisão.

## Limites

- Não estimar resultados.
- Não escolher janela, bandwidth ou outcome pela aparência dos efeitos.
- Não ampliar o escopo para WP3, WP4 ou WP5.
- Não fazer push ou merge.

Ao final, valide tudo, faça commit próprio e informe o hash e a decisão do portão.
