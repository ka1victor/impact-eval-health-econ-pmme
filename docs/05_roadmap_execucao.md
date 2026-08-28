# 05. Roadmap de execução do estudo prioritário

> Este é o roadmap operacional canônico. O encadeamento completo de outcomes em `03_plano_avaliacao_outcomes.md` é uma agenda de pesquisa de longo prazo, não a fila de execução atual.

## 1. Produto que será executado agora

Pergunta:

> Quando o incentivo adicional do PMM-E transforma vagas ofertadas em capacidade médica sustentada e líquida, e quando resulta apenas em ocupação transitória, substituição ou remanejamento?

O estudo avalia eficácia operacional do provimento. Seu outcome primário pretendido é a proporção da janela comum de acompanhamento em que a vaga permaneceu coberta. A janela-alvo é 180 dias, condicionada à disponibilidade de seguimento definida antes de observar efeitos.

## 2. Quais WPs entram agora

| WP | Uso no estudo prioritário | Situação |
|---|---|---|
| WP0 — regra e exposição | Auditar tratamento, cutoff, vagas e contraste causal | Executar integralmente |
| WP1 — força de trabalho | Construir cobertura, entrada, permanência, rotatividade e FTE | Executar integralmente |
| WP2 — capacidade e produção | Usar somente infraestrutura prévia como moderador | Executar parcialmente |
| WP3 — acesso e fila | Nenhuma estimação nesta etapa | Guardado |
| WP4 — clínica | Nenhuma estimação nesta etapa | Guardado |
| WP5 — custos e bem-estar | Nenhuma estimação nesta etapa | Guardado |
| WP6 — síntese e spillovers | Heterogeneidade confirmatória, decomposição contábil de remanejamento e síntese | Executar parcialmente |

O que fica guardado em WP3–WP5 está especificado em [`06_backlog_wp3_wp4_wp5.md`](06_backlog_wp3_wp4_wp5.md).

## 3. Bloqueio atual

As três bases preservadas permitem inventariar participantes, municípios e IVS. Elas não contêm:

- universo e denominador de vagas;
- trajetória individual completa de entrada e saída;
- identificador individual na série histórica;
- CNES mensal e carga horária;
- informação suficiente para cobertura sustentada, retenção individual ou FTE líquido.

Portanto, nenhum agente deve iniciar estimação antes dos portões de viabilidade institucional e de dados.

## 4. Sequência operacional

```text
FASE 1 — VIABILIDADE

01 Auditoria institucional ─┐
                            ├─→ sprint de aquisição A01–A05
02 Auditoria de dados ──────┘              ↓
                                  A05R saneamento pré-A06
                                           ↓
                                  A06 portão integrado
                                           ↓
                              A07 pedidos, se necessários
                                           ↓
                              03 Protocolo empírico congelado
                                      ↓
                               PORTÃO: prosseguir?
                                      ↓
FASE 2 — CONSTRUÇÃO E ESTIMAÇÃO

04 Painel de vagas ─────────┐
                            ├─→ 06 Identificação e estimação
05 CNES/FTE/infraestrutura ─┘
                                      ↓
FASE 3 — AUDITORIA E ENTREGA

07 Red team e reprodução ─────→ 08 Síntese final
```

Os pares 01–02 e 04–05 podem rodar em paralelo apenas em worktrees ou branches isolados. O agente 03 depende das auditorias, do sprint de aquisição saneado e do portão A06. O agente 06 depende dos painéis validados. O agente 08 depende do red team.

Após a execução das auditorias 01–02, o primeiro portão classificou o estudo como
`aguardando dados`. Por isso, a dependência efetiva do prompt 03 inclui agora o
sprint extraordinário descrito em
[`prompts/aquisicao_dados/README.md`](../prompts/aquisicao_dados/README.md).
A01–A05 podem rodar em paralelo em worktrees isolados; A05R corrige e valida os
produtos combinados; A06 os integra; A07 prepara pedidos administrativos para as
lacunas remanescentes, sem enviá-los.

## 5. Portão depois da Fase 1

O protocolo deve responder, antes de qualquer estimação:

1. O contraste identifica participação, incentivo marginal ou pacote?
2. A regra usa efetivamente o IVS 2010 e qual é o cutoff?
3. Existe universo de vagas e denominador confiável?
4. Existe trajetória temporal suficiente para cobertura sustentada?
5. Qual é a maior janela comum possível sem olhar os efeitos?
6. Há chave para vincular vaga, participante e CNES?
7. FTE e infraestrutura podem ser medidos com informação pré-tratamento?
8. A amostra tem potência para o efeito principal e para uma interação?

Saídas permitidas:

- **prosseguir:** pergunta, tratamento, dados e contraste estão definidos;
- **prosseguir parcialmente:** estimar apenas o que os dados identificam e reduzir a linguagem;
- **parar:** não há contraste ou mensuração defensável;
- **aguardar dados:** pergunta permanece, mas exige fonte ainda indisponível.

Não redefinir o outcome silenciosamente apenas para aproveitar as bases existentes.

## 6. Entregáveis por fase

### Fase 1

- `docs/auditorias/01_regra_institucional.md`;
- `docs/auditorias/02_disponibilidade_dados.md`;
- manifestos e hashes de novas fontes;
- `docs/07_protocolo_empirico_congelado.md`.

### Fase 2

- painel vaga–especialidade–chamamento;
- spells de ocupação e fluxo de exclusões;
- painel profissional–vínculo–mês;
- FTE, infraestrutura prévia e remanejamento contábil;
- scripts determinísticos integrados ao `run_all.py`;
- tabelas, figuras e resultados estruturados.

### Fase 3

- `docs/auditorias/03_red_team_e_reprodutibilidade.md`;
- correções ou limitações classificadas;
- relatório final e README atualizados;
- reprodução ponta a ponta a partir das fontes documentadas.

## 7. Regras de coordenação dos agentes

- Cada agente lê `AGENTS.md`, `CLAUDE.md`, este roadmap e seu prompt integralmente.
- Cada agente respeita os pré-requisitos e não avança para a fase seguinte.
- Dados brutos existentes nunca são modificados.
- Dados não observados nunca são preenchidos com simulação ou premissas.
- Cada agente entrega commit próprio; não faz push nem merge.
- Trabalho paralelo exige worktrees isolados.
- O integrador revisa os commits na ordem deste roadmap.
- Um resultado antigo no histórico do Git não vale como evidência vigente.

## 8. Definição de conclusão

O estudo estará pronto quando puder sustentar, com dados observados:

> Próximo ao contraste institucional analisado, determinada condição de incentivo alterou em X a cobertura das vagas durante Y dias. O resultado ocorreu principalmente por entrada/permanência, correspondeu a Z de capacidade líquida e foi ou não condicionado pela infraestrutura anterior.

A conclusão deve também declarar que o estudo não mede diretamente produção, espera, saúde, custos ou eficácia global do PMM-E.
