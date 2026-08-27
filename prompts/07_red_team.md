# Prompt 07 — Red team e reprodução independente

Execute somente depois que dados processados e estimações estiverem concluídos. Comece em modo somente leitura.

Leia todo o protocolo, auditorias, código, outputs e documentação de resultados.

## Missão

Executar o pipeline a partir de um ambiente limpo e tentar derrubar as conclusões.

Audite:

- tratamento e cutoff;
- continuidade da oferta e composição;
- seleção de municípios e vagas;
- ausência versus zero;
- censura;
- vazamento de informação posterior;
- vinculação de profissionais;
- múltiplos vínculos;
- medição de FTE;
- infraestrutura pós-tratamento;
- remanejamento;
- inferência e clusterização;
- bandwidth;
- placebos;
- múltiplos testes;
- estabilidade entre execuções;
- generalização além da vizinhança do corte;
- diferença entre efeito do incentivo e efeito do programa.

Classifique cada problema como:

- resolvido;
- limitação administrável;
- ameaça séria;
- fatal para a identificação.

## Entregável

- `docs/auditorias/03_red_team_e_reprodutibilidade.md`;
- registro dos comandos de reprodução;
- reconciliação de outputs;
- lista priorizada de correções;
- parecer sobre a linguagem máxima sustentada.

Não escolha uma especificação “melhor” com base no resultado. Faça apenas correções técnicas inequívocas; mudanças substantivas devem ser recomendações separadas.

Não inicie WP3, WP4 ou WP5. Faça commit próprio e não faça push ou merge.
