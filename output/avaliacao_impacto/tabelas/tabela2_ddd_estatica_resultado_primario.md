# Tabela 2 — DDD estática

| Modelo                         | Especificação                                            | Outcome               |    Beta |   Erro-padrão cluster |   IC 95% inferior |   IC 95% superior |   P-valor |     N |   Clusters |   Média pré imediata |   Média pré reserva |
|:-------------------------------|:---------------------------------------------------------|:----------------------|--------:|----------------------:|------------------:|------------------:|----------:|------:|-----------:|---------------------:|--------------------:|
| M1_DDD_Principal_Confirmatoria | DDD do estoque; cursos sem CBO compartilhado             | especialistas_mst     | -0.4459 |                0.2456 |           -0.9338 |            0.0419 |    0.0727 |  7975 |         93 |               7.2464 |             10.8523 |
| M2_DDD_Ampliada                | DDD do estoque; 16 cursos como sensibilidade operacional | especialistas_mst     | -0.2319 |                0.1519 |           -0.5321 |            0.0683 |    0.1290 | 20150 |        151 |              11.1685 |             10.3086 |
| M3_DDD_Cobertura               | DDD da probabilidade de ao menos um especialista         | cobertura_binaria_mst |  0.0073 |                0.0154 |           -0.0233 |            0.0379 |    0.6372 |  7975 |         93 |               0.9070 |              0.9635 |

Erros-padrão agrupados por município, com correção para número finito de clusters.
