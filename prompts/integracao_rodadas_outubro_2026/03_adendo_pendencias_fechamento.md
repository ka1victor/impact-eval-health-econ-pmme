# S3 — Adendo ao `02_resolver_pendencias.md` da rodada de 01/10/2026

Use este adendo **junto com**
`prompts/fechamento_sessao_remota/02_resolver_pendencias.md`, depois da
integração (S2). Onde os dois divergirem, vale este adendo: ele incorpora o R1
de 05/10/2026, posterior àquele prompt. O que não aparece aqui vale como está
no 02.

## Seção A — o que mudou em cada decisão

**A1 · A5/A6 sob o ambiente fixado.** Continua de pé para A5. O manifesto A6 já
foi regravado sob Python 3.12.3 em `be12956`, e só o bloco de versões mudou. Se
o autor escolher regravar A5, regere A6 de novo em seguida.

**A2 · O `run_all.py` reescreve `docs/`.** Continua de pé. Os scripts novos do
RDD (`01c` e `04`) gravam só em `output/`. Depois da S2, o registro curado de
01/10 está no doc 38 e deixa de ser apagado, mas a decisão de fundo segue com o
autor: manter os documentos gerados em `docs/`, com ponteiros para os curados,
ou passar os relatórios gerados para `output/` com um teste que falhe se o
`run_all.py` deixar `docs/` modificado.

**A3 · O `run_all.py` sem os microdados do CNES.** Continua de pé. O
`run_all.py` tem agora 27 etapas (`01c` e `04` entraram depois do `01b`) e ainda
aborta na etapa 8.

**A4 · Hash vencido.** A parte de `status_execucao_plano_causal.json` está
resolvida: o controlador recalcula os hashes de `docs/pedidos_dados/` a cada
execução. Continua vencido o hash de `quadro_vagas_tratamento.parquet` em
`portao_regra_ivs.json` e `diagnostico_viabilidade_salario_ivs.json`. Regenere
pelos scripts de origem; `01_auditar_regra_e_suporte.py` regrava também o doc
07, com data nova, o que é esperado.

**A5 · Estado do D-3 e da RDD-IVS.** A pergunta ao autor continua, mas a
resposta proposta mudou:

| Item | Estado a propor |
|---|---|
| RDD-IVS | **reaberta**: R1 `APROVADO_SHARP` com o IVS administrativo da SGTES (05/10/2026), R2 `VIAVEL_CONTINUIDADE_COM_RESSALVAS`, R3 `PENDENTE_AUTORIZACAO_DO_AUTOR` |
| D-3 | não enviado e deixou de ser pré-condição do R1. Um pedido estreito, só sobre a safra e a base de cálculo do IVS administrativo, é opcional |

As fontes a alinhar são o JSON de status e o doc 33 (já alinhados na S2), o
backlog 36, o `TODO.md` e o `README.md`.

**A6 · `CLAUDE.md` e `AGENTS.md`.** **Não aplique a redação proposta no 02.**
Ela declara a RDD "arquivada porque o escore administrativo não é observado", o
que agora é falso, e apagaria o achado de 05/10. Proponha ao autor, para editar
só com autorização:

- **`CLAUDE.md`, fila imediata.** Manter "a fila imediata é o portão de
  viabilidade do RDD", com: "R1 e R2 foram executados em 05/10/2026 com o IVS
  administrativo publicado pela SGTES (`docs/auditorias/15`). A próxima etapa é
  o R3, que depende de decisões do autor (`docs/05_identificacao/18`). R4 só com
  o registro R3 commitado."
- **`CLAUDE.md`, running variable.** No lugar de "O IVS 2010 do IPEA é a running
  variable canônica": "A running variable do RDD da bolsa é o IVS administrativo
  da SGTES (quadro de vagas do PMMB 2026), que reproduz a faixa em 100% dos
  casos. O IVS 2010 do Ipea segue como covariada e referência territorial. Não
  o substitua por IDHM ou PIB per capita sem justificativa econométrica
  explícita e autorização do autor." Só depois de o autor aprovar a decisão 0 do
  R3.
- **`CLAUDE.md`, execução.** No lugar de "A única execução imediata autorizada é
  R1 e, condicionalmente, R2": "R1 e R2 da fila RDD estão concluídos; a execução
  imediata autorizada é o R3, condicionada às decisões do autor."
- **Do 02, manter:**
  - o A8 como núcleo causal executado, com a pergunta própria dele (ganhar a
    alocação);
  - a fila de correções no backlog 36;
  - a regra de ambiente;
  - a linguagem do A8;
  - a regra do módulo clínico do ciclo 3.
- **`AGENTS.md` §2.** No lugar de "a RDD-IVS atual está arquivada (teto de
  78,0%)": "A running variable do RDD territorial da bolsa é o IVS
  administrativo da SGTES; o IVS 2010 não reproduz a regra (teto de 78,0% para
  qualquer regra de dois cortes), e por isso o R1 com ele foi reprovado."

**A7 · Hook `SessionStart`.** Continua de pé. No container da nuvem existem
`python3.12`, `python3.13` e `uv`. O comando testado em 05/10 foi
`uv venv --python 3.12 <dir> && VIRTUAL_ENV=<dir> uv pip install -r requirements.txt`,
que instala Python 3.12.3, numpy 2.5.2, pandas 3.0.5, statsmodels 0.15.0 e scipy
1.18.1.

## Seção B — acréscimos

**B2 · Artigos.** Além de compilar: os dois artigos dizem que a rota da RDD foi
encerrada no R1. Os trechos são `paper_pmme_curto.tex` (em torno das linhas
411–415 e 456–458) e `paper_pmme_submission.tex` (em torno de 64–67 e 805–813).
As cifras citadas (191, 177, 48,1%) continuam corretas para o IVS 2010; o que
ficou errado é a conclusão. Reescreva só com decisão do autor, agora ("reaberta,
sem estimativa") ou depois do R4. Qualquer cifra nova passa pelos conferidores.

**B3 · Ponteiros vencidos.**
- **Doc 33:** a data e a próxima ação já vêm atualizadas pelo controlador.
- **Roadmap, seção 9:** "reaberta somente pelos portões R1–R3" agora está
  coerente com o estado; não a corrija para "arquivada".
- **Banca 1:** o apêndice A1 (diagnóstico da reconstrução da regra) e o que a
  banca diz sobre o RDD ficaram desatualizados. Como R1 e R2 são viabilidade e
  não estimação, cabem na banca. Mudar só com decisão do autor, primeiro no
  documento de conteúdo (`02_conteudo_slides.md`), depois nos decks.

**B4 · D-4.** O painel mensal de `output/avaliacao_impacto/dados/` cobre só os
368 municípios da 1ª chamada de 2025 (verificado em 05/10). Ele não serve para o
balanço do R2 nos 1.144 municípios ofertados. O estoque prévio do CNES para o
R2 e o R3 depende dos microdados (seção C).

**B5 · `TODO.md`.** Inclua os itens do RDD:
- R3, com as decisões do autor;
- R4;
- safra do IVS administrativo;
- estoque prévio do CNES;
- artigos e banca.

## Seção C — acréscimo

Os microdados do CNES (D-4) também destravam duas coisas do RDD: a covariada de
estoque prévio no R2/R3, para todos os municípios ofertados, e, depois do R4, o
R5 (oferta local persistente). Para o R3, baixe só competências anteriores à
oferta; competências posteriores só no R5.
