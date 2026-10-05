# 02. Resolver as pendências abertas pela sessão remota de 01/10/2026

## Papel e limites

Você fecha o que a rodada remota deixou aberto. Parta do branch
`claude/admiring-tesla-bduu1t`, a partir de `355e868` ou do commit mais recente
do branch, depois que a revisão do
[`01_revisar_trabalho_sessao_remota.md`](01_revisar_trabalho_sessao_remota.md) não
tiver deixado nada `BLOQUEADO`.

Leia antes [`CLAUDE.md`](../../CLAUDE.md), [`AGENTS.md`](../../AGENTS.md), [`TODO.md`](../../TODO.md),
[`docs/06_execucao/05_roadmap_execucao.md`](../../docs/06_execucao/05_roadmap_execucao.md), o backlog
[`36`](../../docs/06_execucao/36_backlog_pos_auditoria.md) e o [`README.md`](README.md) desta pasta.

Regras que valem sobre tudo o que está abaixo:

- Não altere `data/`.
- Toda transformação sai de script versionado e vai para `output/`.
- Antes de qualquer código que mude número publicado, commite uma emenda.
- Toda mudança estrutural na documentação ganha entrada em
  [`docs/00_registro_mudancas.md`](../../docs/00_registro_mudancas.md) no mesmo
  commit.
- Fora do A8, nada de linguagem causal.
- Não escolha variante depois de ver qual favorece a narrativa.
- Push e merge só com autorização explícita.

**Ambiente:** `.venv` com Python >= 3.12 e as versões de `requirements.txt`.
Rode `python run_tests.py` no início; o esperado são 189 testes verdes.

## Seção A — decisões do autor

Pergunte tudo de uma vez, com opções curtas, e execute só o que for
autorizado. Se não houver autor para responder, pule a seção e registre as
perguntas no relatório final.

### A1. A5/A6 sob o ambiente fixado

Os artefatos foram gravados sob Python 3.11.15, numpy 2.4.6 e pandas 3.0.6.
Sob o ambiente fixado, `A5_tabela_13` e o bloco `pretendencia_por_curso` de
`A5_ameacas_c7.json` mudam:

- `pre_F_gl_fe`, em até 3,5e-4, nos cursos 3 e 13, que têm posto baixo;
- `q_fdr_bh_pre`, em até 2,5e-4.

Nenhuma rejeição muda e nenhuma cifra dos artigos muda.

Opções:

- **(a) Regravar**, como no A8 em 16/09: registro no backlog 36 e em
  `docs/auditorias/14_erratas_artefatos_congelados.md`, hashes de A6
  reemitidos e os dois conferidores aprovando.
- **(b) Errata nova**, sem regravar.

### A2. O `run_all.py` reescreve `docs/`

`scripts/rdd_bolsa/02_controlar_execucao_plano_causal.py` reescreve o
[doc 33](../../docs/06_execucao/33_status_execucao_plano_causal.md) a partir de
um modelo de 04/09, com estado vencido, e apaga as subseções curadas. Outros
scripts carimbam data ou hash nestes documentos:

- `docs/auditorias/07_portao_rdd_bolsa.md`;
- `docs/auditorias/09_matriz_afirmacao_evidencia_limite.md`;
- `docs/auditorias/09_red_team_atracao_provimento.md`;
- `docs/06_execucao/32_sintese_A6_resumo_intro_metodos_conclusao.md`.

Proposta: os scripts gravam o relatório gerado em `output/` e não escrevem em
`docs/`. Um teste falha se o `run_all.py` deixar `docs/` modificado.

### A3. O `run_all.py` sem os microdados do CNES (D-4)

Hoje ele aborta na etapa 8 de 25 (`05_integrar_painel_analitico.py`).

Opções:

- **(a)** Manter o aborto.
- **(b)** Criar um modo "a partir de artefatos congelados" que pule as etapas
  8 e 9 com hash conferido, como o A5 já faz.

### A4. Hash vencido

`output/rdd_bolsa/portao_regra_ivs.json` e
`output/rdd_bolsa/diagnostico_viabilidade_salario_ivs.json` registram
`41e1d3af…` para `quadro_vagas_tratamento.parquet`. O hash atual é
`96281c14…`, e a diferença é só `cod_curso` int32 contra int64.
`status_execucao_plano_causal.json` tem hashes vencidos de dois arquivos de
`docs/pedidos_dados/`.

Correção: regenerar pelos scripts de origem, nunca editar à mão.

### A5. Estado do D-3 e da RDD-IVS

As fontes divergem:

| Fonte | D-3 | RDD-IVS |
|---|---|---|
| `status_execucao_plano_causal.json` | `PRONTO_NAO_ENVIADO` / `AGUARDANDO_RECEBIMENTO` | — |
| Doc 33 | `CANCELADO_NAO_ENVIADO` | `ARQUIVADO_ESCORE_NAO_OBSERVADO` |
| Backlog 36 | "DECIDIDA: NÃO ENVIAR", mas listado como pendente | — |
| `TODO.md` | — | `ARQUIVADO_SEM_PRIMEIRO_ESTAGIO` |

Pergunte qual é o estado vigente e alinhe todas as fontes a ele.

### A6. `CLAUDE.md` e `AGENTS.md`

Só edite com autorização. Redação a propor:

- **`CLAUDE.md`:**
  - O núcleo causal vigente é o A8
    ([`17`](../../docs/05_identificacao/17_plano_causal_publico_cutoff_escore.md)).
    A4 é descritivo e A5 é associativo.
  - A RDD da bolsa pelo IVS está arquivada, porque o escore administrativo não
    é observado. O plano `14` é registro e só volta com o D-3.
  - A fila vigente é o backlog 36, com ordem normativa. Hoje não há sessão
    aberta.
  - A regra "SIH/SIA só depois de R1–R5" passa a ser: o módulo clínico do
    ciclo 3 só entra com C3-02B em 675/675 e `202703` madura.
  - Dizer a que diretório pertencem os pares de prompts 01–02 e 04–05.
  - Acrescentar a regra de ambiente: Python >= 3.12 com as versões fixadas.
  - Acrescentar a linguagem do A8: efeito causal local, condicional à
    comparabilidade dos pares, com protocolo retrospectivo. Heterogeneidade
    com 36 pares é exploratória.
- **`AGENTS.md` §2:**
  - O escopo vigente é o A8. Saúde e custos são agenda condicionada (WP3–WP5).
  - O IVS é canônico para RDD territorial, mas a RDD-IVS atual está arquivada
    (teto de 78,0%).
- **`AGENTS.md` §3, novo:** ponteiros para `CLAUDE.md`, roadmap e backlog 36.

### A7. Hook `SessionStart`

Para sessões na web. Na sessão remota foi bloqueado pelo sistema de
permissões. O que precisa ter:

- `.claude/hooks/session-start.sh`, idempotente. Escolhe python3.12 ou 3.13
  (ou `uv`), cria o `.venv` e instala o `requirements.txt` só quando o hash do
  arquivo mudar.
- Exporta `PATH` via `$CLAUDE_ENV_FILE`.
- Fica registrado em `.claude/settings.json`.
- Ganha entrada no registro de mudanças.

## Seção B — executável sem decisão nova

1. **Beamer.**
   - Compile com LuaLaTeX: `scripts/apresentacao/build_deck_beamer.sh` e
     `build_exemplos_tema.sh`.
   - O PDF versionado não traz a frase nova do slide A4.
   - Confira: nenhum Overfull, 40 páginas e o rodapé parando em `17 / 17`.
2. **Artigos.**
   - Compile `paper_pmme_submission.tex` e `paper_pmme_curto.tex`.
   - Confira as páginas afirmadas na documentação (13 e 7). Se mudaram,
     corrija `TODO.md`, `README.md` e roadmap.
   - Os conferidores `10_` e `11_` têm de aprovar 214 e 199 cifras.
3. **Ponteiros vencidos.**
   - Doc 33: data de 04/09, "Próxima ação interna: redigir o trabalho curto"
     (já feito), sem menção à fila pós-auditoria.
   - Roadmap, seção 9: "reaberta somente pelos portões R1–R3" contradiz o topo
     do próprio roadmap.
   - `docs/07_apresentacoes/banca1/03_proveniencia_figuras_e_numeros.md`:
     - na P7, os 276 km e 101 km já não estão "no texto do slide 4", só na
       figura;
     - `curva_custo_laboral` está no slide 12, não no 10.
4. **D-4 mais estreito do que o registrado.**
   - Corrija o `TODO.md` e o backlog 36: o painel mensal existe, falta o
     microdado.
   - Avalie se, com esse painel, o teste de deslocamento região–curso fica
     viável com **todos** os municípios da região de saúde, ou se o painel só
     cobre os municípios do quadro.
   - Se ficar viável, escreva e commite um protocolo antes de rodar qualquer
     coisa.
5. **`TODO.md`.**
   - Marque como concluído o diagnóstico dos cursos 2 e 16 (protocolo
     `b57eb4e`, execução `e5a1872`), com a leitura descritiva "compatível com
     oferta" nos dois.
   - Registre a ressalva: a pré-tendência fica nos CNES ofertantes e é
     compensada pelo resto do município (−0,84 e −0,79). Os agregados não
     separam transferência de reatribuição cadastral.
   - Abra o item "classificar transições profissional × CNES × CBO com
     microdados (D-4)".

## Seção C — só com acesso ao FTP do DATASUS

Teste `ftp.datasus.gov.br` antes de qualquer coisa. Da nuvem ele estava
inacessível.

- **D-2.**
  - Se `RDAC2606.dbc` e `RDRR2606.dbc` estiverem publicados, refaça o C3-02B
    conforme
    [`prompts/avaliacao_ciclo3/02b_corrigir_e_validar_sih_pre.md`](../avaliacao_ciclo3/02b_corrigir_e_validar_sih_pre.md),
    até 675/675.
  - Não impute zeros. Não consulte outcome pós-tratamento.
  - C3-05 e C3-06 seguem congelados até a competência `202703` existir.
- **Microdados do CNES (D-4).**
  - Estime volume e espaço em disco antes de baixar.
  - Registre fonte, data, cobertura e hash de cada arquivo.
  - Rode o desenho já registrado no backlog 36 para os cursos 2 e 16, sem
    reescolher amostra, outcome ou regra de exclusão.

## Seção D — depende de material do autor (não invente)

- **Pendência 1:** tabela por UF da *Demografia Médica 2025* em `data/raw/`,
  com hash, e a figura das 27 UFs no lugar da dos 4 extremos.
- **Pendências 2 e P7:** fonte primária do deslocamento por região (REGIC
  2018). Sem confirmação, os valores saem da tela.
- **Pendências 3 e 5:** PDF da *Demografia Médica 2025* com hash, e o "Sudeste
  55,4%" conferido nele.
- **Pendência 8:** limitação da retaguarda regional — uma linha no slide 5, ou
  um argumento próprio.
- **Pendência 9:** sinal do custo em relação ao IVS — fixado na teoria, ou a
  ressalva volta à tela.
- **Capa:** título neutro, como pede a nota de produção do documento de
  conteúdo.

## Encerramento

- Um commit por item, com mensagem em português.
- Suíte verde e os dois conferidores aprovando são portão.
- Atualize o ponteiro de estado em `TODO.md`, no roadmap e no backlog 36.
- Relatório final com:
  - o que foi feito, com hashes;
  - o que ficou e por quê;
  - o que continua com o autor.
