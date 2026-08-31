# C3-03 — Torneio pré-tratamento e congelamento do plano

## Objetivo

Usar somente exposição e outcomes anteriores a `T0` para decidir se o núcleo
geral e o módulo anestesia/SIH têm suporte causal e potência, e congelar um plano
de análise antes da primeira atualização pós-tratamento.

## Entradas obrigatórias

- C3-01 e C3-02 incorporados;
- coorte, ponte, CNES pré e SIH pré validados;
- `docs/12_estrategia_causal_prospectiva_ciclo3.md`;
- auditoria do pipeline agregado do ciclo 1, para não repetir seleção
  retrospectiva.

## Regras invioláveis

- rejeite qualquer arquivo ou competência `>=T0`;
- não estime “efeitos” com datas reais pós-tratamento;
- não mude braços pelo preenchimento observado;
- não escolha outcome, janela ou estimador por menor p-valor;
- synthetic DiD é robustez, não reparo de pré-tendências.

## Trabalho

1. Defina a menor mudança relevante antes da MDE, com justificativa de política:
   especialista adicional no núcleo e variação cirúrgica no módulo SIH.
2. Avalie suporte, distribuição de propensão, níveis e trajetórias prévias.
   Registre separadamente estoque total, vínculo que satisfaz a assinatura
   completa da Nota 59 e `070102` genérico.
3. Faça placebos temporais no pré-período, testes conjuntos de leads e testes de
   equivalência contra limites derivados da mudança relevante.
4. Calcule MDE com cluster no município e simulação coerente com a estrutura do
   painel.
5. Compare, por rubrica pré-definida:
   - seis cursos/força de trabalho;
   - anestesia total/SIH;
   - anestesia isolada de outros cursos cirúrgicos;
   - ecocardiografia/SIA apenas com metadados e pré-CNES, sem baixar SIA.
6. Avalie sensibilidade a pesos de sobreposição, suporte dentro de município e
   CNES, leave-one-region-out e placebos de CBO/procedimento.
7. Classifique cada módulo como `confirmatorio`, `exploratorio` ou `inviavel`.
8. Só acione C3-04 se ecocardiografia puder substituir anestesia por critério
   substantivo e quantitativo pré-especificado.
9. Escreva o plano final com estimando, população, tratamento, controle, `T0`,
   outcomes, horizontes, equação, inferência, multiplicidade, contaminação,
   missing, winsorização e regras de linguagem.
10. Defina como primeiro estágio a proporção de células imediatas com vínculo
    PMM-E completo e o número desses vínculos. Se a assinatura não for
    implementada de forma confiável, preserve o estoque total como outcome e
    rebaixe retenção individual.
11. Gere hashes do protocolo e das listas de unidades/códigos congeladas.

## Entregáveis

- `scripts/avaliacao_ciclo3/03_auditar_pre_e_potencia.py`;
- `output/avaliacao_ciclo3/diagnosticos_pre.csv`;
- `output/avaliacao_ciclo3/potencia_pre.json`;
- `output/avaliacao_ciclo3/decisao_torneio_pre.json`;
- `docs/13_plano_pre_analise_ciclo3.md`;
- `output/avaliacao_ciclo3/registro_pre_analise.json`.

## Portão

O JSON deve conter decisão única por módulo, razões e hashes. Se o núcleo geral
falhar pré-tendência ou suporte, a análise futura será associação ajustada, não
causal. Se anestesia falhar potência ou ponte, ela será exploratória; não será
substituída automaticamente por outro outcome.

Valide determinismo, referências locais, sintaxe JSON, testes e
`git diff --check`. Não modifique brutos. Crie commit próprio e não faça push.
