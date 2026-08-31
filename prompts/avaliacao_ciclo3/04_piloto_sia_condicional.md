# C3-04 — Piloto SIA condicional para ecocardiografia

## Condição de execução

Execute este prompt **somente** se
`output/avaliacao_ciclo3/decisao_torneio_pre.json` ordenar explicitamente o
piloto de ecocardiografia/SIA. Caso contrário, registre “não acionado” e pare sem
baixar dados.

## Objetivo

Testar se produção ambulatorial de ecocardiografia pode substituir o módulo
assistencial de anestesia, usando somente competências anteriores a `T0` e uma
aquisição seletiva que reconheça o peso do SIA/PA.

## Trabalho

1. Leia integralmente `AGENTS.md`, `CLAUDE.md`, a estratégia C3, o plano de
   pré-análise, a decisão do torneio e a documentação oficial do SIA/SIGTAP.
2. Faça primeiro um piloto de uma UF–competência. Registre transferência, pico
   de disco, tempo, linhas e tamanho filtrado.
3. Diferencie BPA-C, BPA-I, APAC e demais instrumentos; não suponha identificação
   individual onde ela não existe.
4. Historicize códigos e regras no SIGTAP.
5. Construa apenas pré-outcomes por CNES e município para os procedimentos
   predefinidos de ecocardiografia.
6. Interrompa a expansão se a cobertura ou o esquema não sustentarem o outcome,
   ou se a projeção de transferência exceder o limite operacional registrado no
   torneio.
7. Se viável, adquira somente UFs da coorte e processe um arquivo de cada vez.

## Entregáveis

- `scripts/avaliacao_ciclo3/04_adquirir_sia_pre.py`;
- testes de esquema e agregação;
- `output/avaliacao_ciclo3/manifesto_sia_pre.json`;
- `output/avaliacao_ciclo3/dicionario_procedimentos_ecocardiografia.csv`;
- `docs/auditorias/07_piloto_sia_ecocardiografia.md`;
- atualização do registro pré-análise, com novo hash e trilha explícita de
  versão, sem sobrescrever silenciosamente a decisão anterior.

Não baixe o Brasil inteiro “por segurança”, não consulte `>=T0`, não estime
efeitos e não persista identificadores pessoais. Valide testes, JSON,
`git diff --check` e integridade dos brutos. Crie commit próprio e não faça push.
