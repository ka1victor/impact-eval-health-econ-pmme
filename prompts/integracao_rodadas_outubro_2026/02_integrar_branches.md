# S2 — Integrar os branches das rodadas de 01/10 e 05/10/2026

## Pré-condições

1. S1a (`prompts/fechamento_sessao_remota/01_revisar_trabalho_sessao_remota.md`)
   e S1b ([`01_revisar_rdd_ivs_administrativo.md`](01_revisar_rdd_ivs_administrativo.md))
   terminaram sem `BLOQUEADO`, ou os bloqueios foram resolvidos.
2. O autor disse onde integrar: só num branch de integração, ou também na `main`.

Ambiente fixado: Python ≥ 3.12 com `requirements.txt`. **Não rode o
`run_all.py`**: ele aborta na etapa 8 sem os microdados do CNES e reescreve
`docs/` (item A2 da rodada remota). Rode só os scripts listados abaixo.

## Passo 1 — merge

Parta de `claude/compassionate-feynman-d70ipe` (o RDD e estes planos), ou do
branch designado da sessão criado a partir dele, mais os commits de correção de
S1a e S1b. Faça
`git merge --no-ff origin/claude/admiring-tesla-bduu1t`.

Em 05/10/2026, um merge de teste num worktree descartável deu **exatamente dois
conflitos**. Se aparecer qualquer outro, pare e reporte.

1. **`docs/00_registro_mudancas.md`.** Os dois lados acrescentam entradas no
   topo. Mantenha todas, da mais recente para a mais antiga: primeiro as de
   05/10, depois as de 01/10.
2. **`docs/06_execucao/33_status_execucao_plano_causal.md`.** Esse arquivo é
   **gerado** pelo `scripts/rdd_bolsa/02_controlar_execucao_plano_causal.py`.
   O lado de 01/10 acrescentou à mão a seção "Reprodutibilidade do estado
   validado — verificação de 01/10/2026", que a próxima execução do controlador
   apagaria. Resolva assim:
   - fique com a versão gerada, do lado de 05/10;
   - mova a seção curada, **sem alterar o texto**, para um documento novo,
     `docs/06_execucao/38_verificacoes_reprodutibilidade.md` (o 37 já foi usado
     por `37_proposta_ajuste_estrutural.md`, de um PR que não entrou na `main`), com um cabeçalho
     que diga de onde ela veio (commit `6fd3a82`) e que hoje o `run_all.py` tem
     27 etapas;
   - acrescente ao modelo de markdown do controlador uma linha com link para o
     doc 38, para que a regeneração preserve o ponteiro;
   - abra a entrada do doc 38 no registro de mudanças.

## Passo 2 — alinhar o que não conflita, mas ficou errado

Estes arquivos entram no merge sem conflito textual e contradizem o R1 de 05/10:

| Arquivo | O que diz hoje | O que passa a dizer |
|---|---|---|
| `README.md` (de `e40c6b1`) | "RDD do IVS fora do plano: arquivada porque o escore administrativo que gera a faixa não é observado" | RDD do IVS reaberta em 05/10/2026: o IVS administrativo da SGTES reproduz a faixa (R1 sharp); R2 viável sem outcomes; R3 aguarda o autor |
| `TODO.md` | RDD-IVS `ARQUIVADO_SEM_PRIMEIRO_ESTAGIO`; D-3 "é o único caminho para o efeito da bolsa" | trilha RDD reaberta, com os itens R3 (S4), R4 (S5), safra do IVS administrativo, estoque prévio do CNES e artigos/banca (decisão do autor); D-3 não enviado e não mais pré-condição |
| `docs/06_execucao/36_backlog_pos_auditoria.md` | seções "D-3 · Pedido do escore administrativo de IVS" e "Por que o D-3 é o único caminho para o efeito da bolsa", que leem o IVS como piso da bolsa | nota datada no topo das duas seções, apontando para a auditoria 15, sem reescrever o histórico |
| `prompts/README.md` | só a pasta `fechamento_sessao_remota/` como novidade | as pastas `fechamento_sessao_remota/` e `integracao_rodadas_outubro_2026/`, com uma linha cada |
| `prompts/fechamento_sessao_remota/README.md` | prompt 02 sem ressalva | nota no topo: antes do 02, ler `../integracao_rodadas_outubro_2026/03_adendo_pendencias_fechamento.md` |

Não edite `CLAUDE.md` nem `AGENTS.md` aqui: isso é decisão do autor, na S3.

## Passo 3 — regerar o que depende dos dois lados

No ambiente fixado:

1. `scripts/rdd_bolsa/02_controlar_execucao_plano_causal.py`, com o modelo já
   apontando para o doc 38;
2. `scripts/tema_trabalho/07_red_team_sintese.py`, para que o manifesto A6
   registre a lista de etapas e os hashes do repositório integrado;
3. `python run_tests.py`. O esperado é **204 testes**: 188 da base, 1 da rodada
   remota e 15 do RDD;
4. os conferidores `10_` e `11_`.

Reverta qualquer mudança em `docs/` ou `output/` que não seja das etapas acima.

## Passo 4 — commits e relatório

- um commit de merge, com os dois conflitos resolvidos;
- um commit "Alinhamento pós-integração", com o passo 2 e o passo 3;
- push só para o branch de integração; `main` só com autorização do autor;
- relatório final: conflitos encontrados, arquivos alinhados, hashes, testes e
  o que ficou para S3 e S4.
