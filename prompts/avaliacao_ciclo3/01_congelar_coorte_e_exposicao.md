# C3-01 — Congelar coorte, exposição e suporte

## Objetivo

Construir e auditar, sem usar outcomes pós-tratamento, a coorte prospectiva do
terceiro ciclo para o contraste oferta imediata pura versus proposta não
priorizada pura.

## Leia integralmente antes de agir

- `AGENTS.md` e `CLAUDE.md`;
- `docs/12_estrategia_causal_prospectiva_ciclo3.md`;
- `docs/auditorias/01_regra_institucional.md`;
- `docs/auditorias/02_disponibilidade_dados.md`;
- `docs/auditorias/aquisicao/A01_vagas_e_versionamento.md`;
- `docs/auditorias/aquisicao/A03_ivs_e_regra.md`;
- `docs/auditorias/aquisicao/A04_pagamentos.md`;
- `docs/auditorias/aquisicao/A05_cnes_mensal.md`;
- [Nota Técnica nº 59/2026-CGPLAD/DEGEPS/SGTES/MS](https://www.gov.br/saude/pt-br/centrais-de-conteudo/publicacoes/notas-tecnicas/2026/nota-tecnica-no-59-2026-cgplad-degeps-sgtes-ms.pdf/view),
  inclusive Anexo I;
- `output/aquisicao/ponte_curso_cbo_oficial.json`;
- arquivos públicos locais do ciclo 3 em `data/raw/pmm_e/` e
  `data/raw/aquisicao/vagas/`.

## Trabalho

1. Verifique Git, worktree e hashes dos arquivos de entrada; não altere `data/`.
2. Reconstrua, por CNES–curso, as propostas do resultado final de gestores e as
   versões de vagas e alocações do chamamento médico.
3. Classifique braços mutuamente exclusivos: `imediata_pura`, `reserva_pura`,
   `nao_priorizada_pura`, `mista` e `inconsistente`.
4. Defina tratamento principal como `imediata_pura`; controle principal como
   `nao_priorizada_pura`; exclua reserva e mistas da análise confirmatória.
5. Preserve quantidades de vagas e alocações como mecanismos, sem redefinir o
   tratamento pelo preenchimento observado.
6. Fixe o primeiro mês em que um vínculo do ciclo poderia aparecer no CNES
   (`T0`) usando cronogramas e regras oficiais. Diferencie publicação, alocação,
   homologação e início.
7. Reconstrua a ponte normativa dos 24 cursos a partir do Anexo I da Nota
   Técnica nº 59/2026. Compare-a com a ponte local histórica, documente
   divergências e sobreposições e produza uma nova ponte C3; não sobrescreva a
   ponte histórica.
8. Audite a assinatura pública do PMM-E no `tbCargaHorariaSus`:
   `IND_VINCULACAO=070102`,
   `NU_CNPJ_DETALHAMENTO_VINCULO=00394544012787`, CBO do Anexo I e cargas
   horárias esperadas. Atualize a aquisição futura para preservar o CNPJ de
   detalhamento, sem persistir CPF/CNS/nome. Demonstre primeiro que o campo está
   presente na disseminação e reconcilie vínculos com alocações; não presuma
   completude.
9. Congele a família geral com CBO oficial não sobreposto e suporte em ambos os
   braços. Os seis cursos já auditados são um limite inferior, não uma restrição
   arbitrária.
10. Produza suporte em três níveis: CNES–curso, município–curso e região–curso;
   identifique suporte dentro do mesmo CNES e município.
11. Marque cointervenções: outros cursos imediatos, especialmente cursos
   cirúrgicos no módulo de anestesia.
12. Registre conversões ou novas chamadas futuras como contaminação temporal,
    sem consultar outcomes.

## Entregáveis

- `scripts/avaliacao_ciclo3/01_congelar_coorte.py`;
- `output/avaliacao_ciclo3/coorte_c3_congelada.parquet`;
- `output/avaliacao_ciclo3/suporte_c3.csv`;
- `output/avaliacao_ciclo3/ponte_curso_cbo_c3_nota59.json`;
- `output/avaliacao_ciclo3/auditoria_assinatura_pmme_cnes.json`;
- `output/avaliacao_ciclo3/manifesto_coorte_c3.json`;
- `docs/auditorias/05_coorte_c3_e_exposicao.md`.

O manifesto deve conter hashes, datas de corte, versões, regras de inclusão,
contagens esperadas e `T0`. O relatório deve explicar por que priorização não é
aleatória e por que o estimando é ITT.

## Validações e parada

- chaves CNES com sete dígitos e IBGE com seis;
- uma única classificação por CNES–curso na versão final;
- reconciliação das 5.534 células e dos totais publicados;
- reconciliação entre vagas e alocações sem confundi-las;
- cobertura da ponte oficial e lista explícita de sobreposições;
- presença e completude da assinatura da Nota 59, sem tratar `070102` isolado
  como identificador do PMM-E;
- testes determinísticos e `git diff --check`.

Pare sem criar protocolo se `T0`, a versão de exposição ou os braços não forem
reproduzíveis. Não baixe SIH/SIA, não estime efeitos e não execute o prompt 03
histórico.

Ao final, crie commit próprio e não faça push.
