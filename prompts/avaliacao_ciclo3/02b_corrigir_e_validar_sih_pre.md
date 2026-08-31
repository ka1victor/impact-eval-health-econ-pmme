# C3-02B — Corrigir e validar o painel SIH pré-tratamento

## Objetivo

Reexecutar o piloto SIH pré-tratamento de anestesiologia com proveniência
completa e corrigir quatro limitações da primeira execução: arquivos sem
manifesto persistido, cobertura incompleta dos destinos interestaduais,
classificação municipal arbitrária e ausência de historicização do SIGTAP.

Este prompt é corretivo. Não execute o C3-03, não consulte competências
pós-`T0`, não estime efeitos e não congele um plano de análise.

## Antes de agir

1. confirme que `HEAD` contém a correção normativa da ponte da Nota Técnica nº
   59/2026 e que os cursos confirmatórios integrais são exatamente 1, 12 e 24;
2. leia `AGENTS.md`, `CLAUDE.md`,
   `docs/12_estrategia_causal_prospectiva_ciclo3.md`,
   `docs/auditorias/05_coorte_c3_e_exposicao.md`,
   `docs/auditorias/06_piloto_sih_anestesiologia.md` e os prompts C3-02/C3-03;
3. confirme que a última competência solicitada é anterior ao `T0` operacional
   e registre que 2026-07/08 podem ainda não estar disponíveis no SIH;
4. preserve os dados brutos existentes e use somente diretórios temporários
   descartáveis para DBC/DBF.

## Correções obrigatórias

1. Proces­se as 27 UFs em cada uma das 25 competências de 2024-06 a 2026-06.
   Isso é necessário para que o destino de residentes inclua internações em
   qualquer UF. Se optar por não processar as 27, retire o outcome de
   resolutividade e documente que o denominador é truncado.
2. Persista uma linha por arquivo UF--competência, com URL, nome, tamanho,
   SHA-256, data/hora de aquisição, linhas lidas e status. O total esperado é
   675. Qualquer erro deve interromper a construção de zeros estruturais.
3. Classifique a exposição de anestesiologia no município usando o conjunto de
   todas as células locais:
   - tratada: ao menos uma imediata e nenhuma reserva/mista;
   - controle: ao menos uma não priorizada, nenhuma imediata e nenhuma
     reserva/mista;
   - contaminada/excluída: demais combinações.
   A auditoria anterior encontrou 77 municípios tratados puros, 247 controles
   puros e um município com imediata e reserva; reconcilie essas contagens.
4. Não use `drop_duplicates(subset=['ibge'])` para escolher silenciosamente o
   primeiro braço municipal.
5. Historicize a tabela SIGTAP aplicável a cada competência, ou demonstre com
   fonte oficial que a regra por prefixo `04` é temporalmente estável. Até essa
   validação, nomeie o outcome como candidato amplo de AIH cirúrgica eletiva,
   não como cirurgia necessariamente sensível a anestesiologia.
6. Meça o pico real de armazenamento temporário. Não repita estimativa não
   instrumentada.
7. Diferencie AIH inicial/continuidade, caráter eletivo/urgência, competência de
   processamento e datas de internação/alta. Preserve zeros à esquerda.
8. Reconcilie linhas lidas, linhas filtradas, agregados e cobertura mensal.

## Testes mínimos

- 675 arquivos com `status=SUCCESS`, hashes não vazios e nenhuma duplicidade
  UF--competência;
- unicidade em CNES--competência e município--competência;
- exatamente 25 competências em cada unidade elegível;
- município com imediata e reserva nunca marcado como tratamento puro;
- AIH de continuidade nunca contada como nova cirurgia;
- procedimento fora do grupo escolhido nunca contado;
- fluxo de residência soma local + fora no universo nacional processado;
- hashes dos painéis reproduzíveis e `git diff --check` limpo;
- nenhuma alteração em `data/raw/`.

## Entregáveis

- correções em `scripts/avaliacao_ciclo3/02_adquirir_sih_pre.py` e testes;
- `output/avaliacao_ciclo3/manifesto_arquivos_sih_pre.csv`;
- `output/avaliacao_ciclo3/manifesto_sih_pre.json` atualizado;
- painéis pré-tratamento corrigidos em `output/avaliacao_ciclo3/sih_pre/`;
- dicionário/historicização SIGTAP auditável;
- `docs/auditorias/06_piloto_sih_anestesiologia.md` revisado.

Ao final, faça commit próprio e não faça push. Informe tráfego real, pico de
disco, contagens por braço municipal e se o C3-03 foi liberado ou continuou
bloqueado.
