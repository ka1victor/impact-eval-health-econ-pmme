# Saneamento pré-A06 (A05R)

> **Data de referência:** 28 de agosto de 2026
> **Escopo:** revisão de proveniência, unidades, versionamento e limites das
> aquisições A01–A05.
> **Não contém:** estimação causal, construção do painel integral do CNES ou
> imputação de dados administrativos ausentes.

## Decisão

```text
ENTRADAS APTAS PARA A06, COM RESTRIÇÕES EXPLÍCITAS
```

A decisão libera somente a **integração e o portão de viabilidade** previstos no
A06. Ela não significa que RDD, DiD, estudo de evento, permanência individual ou
dose financeira efetiva estejam identificados. Os dados abertos atuais permitem
construir denominadores por publicação, descrever resultados administrativos
publicados, verificar regras normativas e testar a existência cadastral de CNES
em três competências piloto.

A revisão crítica que motivou este saneamento está em
[`revisao_pre_a06.md`](revisao_pre_a06.md).

## Resultado por frente

### A01 — vagas e versionamento

Arquivos: [`A01_vagas_e_versionamento.md`](A01_vagas_e_versionamento.md),
[`a01_inventario_versoes.json`](../../../output/aquisicao/a01_inventario_versoes.json)
e [`a01_manifesto_vagas.json`](../../../output/aquisicao/a01_manifesto_vagas.json).

- Foram auditadas 19 planilhas oficiais: 11 em `data/raw/pmm_e/` e oito em
  `data/raw/aquisicao/vagas/`.
- Uma linha de quadro de vagas é uma **célula agregada CNES–curso**. A soma dos
  campos de quantidade mede vagas daquela publicação, não vagas físicas com
  identificador administrativo individual.
- Não existe denominador cumulativo obtido pela soma de chamadas: células e
  vagas podem ser reapresentadas.
- A transição entre a primeira e a segunda chamada de 2025 usa explicitamente a
  aba `VAGAS - CADASTRO RESERVA`: 1.762 células, 2.896 vagas em reserva, 929
  células reapresentadas, 833 novas e 366 da primeira chamada ausentes na
  segunda.
- Os diagnósticos textuais são gerados das mesmas métricas estruturadas, evitando
  divergência futura entre narrativa e inventário.

### A02 — seleção e trajetória pública

Arquivos: [`A02_selecao_e_trajetoria.md`](A02_selecao_e_trajetoria.md),
[`a02_matriz_eventos_publicos.json`](../../../output/aquisicao/a02_matriz_eventos_publicos.json)
e [`a02_manifesto_trajetoria.json`](../../../output/aquisicao/a02_manifesto_trajetoria.json).

- A02 lê diretamente as três fontes de 2025 recuperadas por A01 e confere seus
  hashes contra o manifesto de A01.
- A versão retificada *sub judice* de 19/09/2025 substitui a versão de 10/09 nas
  contagens; as duas não são somadas.
- A versão canônica contém 1.671 **registros publicados** e 993 chaves distintas
  `CPF mascarado + nome`: são resultados de preferência, classificação e
  alocação, não prova do universo completo de inscrições.
- Nessa publicação há 993 registros de primeira opção, 678 de segunda opção, 527
  classificados, 468 locais confirmados e 59 locais desconsiderados. O quadro
  complementar de 59 propostas de realocação é contabilizado separadamente.
- Aceite, recusa, início efetivo, saída, motivo de saída e *spells* de 90/120/180
  dias continuam não observados.

### A03 — IVS e regra normativa

Arquivos: [`A03_ivs_e_regra.md`](A03_ivs_e_regra.md),
[`a03_matriz_regra_tratamento.json`](../../../output/aquisicao/a03_matriz_regra_tratamento.json)
e [`a03_manifesto_ivs_regra.json`](../../../output/aquisicao/a03_manifesto_ivs_regra.json).

- Três JSONs sintéticos foram retirados de `data/raw/`; normas não adquiridas
  permanecem catalogadas como indisponíveis, sem bytes oficiais simulados.
- O IVS 2010 do IPEA permanece a running variable canônica do projeto.
- A divergência de 42,56% entre faixa declarada e classificação estrita pelo IVS
  é um diagnóstico descritivo. Ela não identifica uma causa única nem valida um
  RDD.

### A04 — regra financeira

Arquivos: [`A04_pagamentos.md`](A04_pagamentos.md),
[`a04_grade_anunciada_2025.csv`](../../../output/aquisicao/a04_grade_anunciada_2025.csv),
[`a04_matriz_dose_financeira.json`](../../../output/aquisicao/a04_matriz_dose_financeira.json)
e [`a04_manifesto_pagamentos.json`](../../../output/aquisicao/a04_manifesto_pagamentos.json).

- A tabela orçamentária digitada no código e os artefatos derivados sem
  proveniência foram removidos.
- A única grade monetária publicada agora é a de 2025, extraída do FAQ oficial
  preservado. Cada linha registra documento, URL, arquivo local, SHA-256 e
  localizador da evidência.
- As páginas locais de 2026 não sustentam uma grade monetária verificável; por
  isso nenhum valor exato de 2026 é publicado.
- Valor anunciado, devido, empenhado, liquidado e pago são estados distintos.
  Com as fontes atuais, somente o anunciado de 2025 é parcialmente observável.
- Dose recebida e primeiro estágio financeiro continuam bloqueados; nenhum
  efeito causal financeiro é declarado.

### A05 — CNES mensal

Arquivos: [`A05_cnes_mensal.md`](A05_cnes_mensal.md),
[`a05_auditoria_universos_cnes.json`](../../../output/aquisicao/a05_auditoria_universos_cnes.json),
[`a05_dicionario_tabelas_cnes.json`](../../../output/aquisicao/a05_dicionario_tabelas_cnes.json)
e [`a05_manifesto_cnes.json`](../../../output/aquisicao/a05_manifesto_cnes.json).

A05 é um **piloto de esquema e aquisição pública parcial: 3 de 26 competências**.
O download integral permanece adiado.

Os dois universos são construídos e auditados separadamente:

| Universo | Unidade | Tamanho |
|---|---|---:|
| Snapshot nominal de ativos | registro de participante / CNES | 1.480 registros; 518 CNES |
| Quadros finais A01 | célula CNES–curso / estabelecimento | cinco versões; união de 1.930 CNES |

As cinco versões de oferta usadas são C1/Ch1, C1/Ch2, C2/Ch1 retificada,
C2/Ch2 e C3/Ch1 retificada. A união de CNES é adequada para validação cadastral;
as quantidades de vagas dessas versões não são somadas entre chamadas.

| Competência | Snapshot ativo | União dos quadros A01 |
|---|---:|---:|
| 202406 | 515/518 (99,42%) | 1.904/1.930 (98,65%) |
| 202506 | 517/518 (99,81%) | 1.927/1.930 (99,84%) |
| 202607 | 518/518 (100,00%) | 1.930/1.930 (100,00%) |

Cobertura significa apenas que o código aparece em `tbEstabelecimento` naquela
competência. Não demonstra inauguração, início de atividade, presença de médico
do PMM-E ou efeito do programa.

## Bloqueios que seguem válidos

| Informação ausente | Consequência |
|---|---|
| Ponte determinística PMM-E–CNES/profissional | Não permite atribuir vínculo individual do CNES ao programa |
| Universo completo de inscrições e eventos administrativos | Não permite estimar aceite, recusa, reocupação ou permanência individual |
| Folha mensal individualizada | Não permite medir valor devido/recebido ou primeiro estágio financeiro |
| Regra administrativa completa que gerou a faixa declarada | A divergência com o IVS 2010 não pode ser explicada por uma causa única |
| 23 competências CNES ainda não adquiridas | O piloto não constitui painel mensal completo |

## Portão para A06

A06 deve:

1. integrar cada quadro de oferta preservando ciclo, chamada e versão;
2. manter separadas célula CNES–curso, quantidade publicada, estabelecimento e
   registro de participante;
3. tratar resultados publicados como estágios administrativos parciais, não como
   universo de inscrições;
4. usar a grade anunciada somente onde a fonte normativa correspondente estiver
   preservada;
5. produzir um mapa explícito de observabilidade antes de propor qualquer
   estimando causal;
6. interromper a construção de um desenho causal se as chaves ou os períodos
   mínimos não estiverem disponíveis.

O A06 pode, portanto, executar a integração e concluir que determinados
estimandos permanecem bloqueados. A liberação deste portão não antecipa o
resultado dessa decisão.
