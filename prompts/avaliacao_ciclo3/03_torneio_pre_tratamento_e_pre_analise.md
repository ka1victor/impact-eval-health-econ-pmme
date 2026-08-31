# C3-03 — Torneio pré-tratamento e congelamento do plano

## Objetivo

Usar somente exposição e outcomes anteriores a `T0` para verificar a viabilidade
do estudo principal de anestesiologia e da generalização para outros cursos.
O portão da força de trabalho depende do CNES pré; o portão clínico depende
separadamente do SIH pré completo. Congelar um plano antes da primeira
atualização pós-tratamento. O torneio classifica credibilidade; ele não escolhe
a menor estatística `p`.

## Entradas obrigatórias

- C3-01 incorporado e aprovado;
- coorte, ponte e CNES pré validados para força de trabalho;
- C3-02B e SIH pré completos somente para liberar o submódulo clínico;
- `docs/12_estrategia_causal_prospectiva_ciclo3.md`;
- auditoria do pipeline agregado do ciclo 1, para não repetir seleção
  retrospectiva.

## Regras invioláveis

- rejeite qualquer arquivo ou competência `>=T0`;
- não estime “efeitos” com datas reais pós-tratamento;
- não mude braços pelo preenchimento observado;
- não escolha outcome, janela ou estimador por menor p-valor;
- synthetic DiD é robustez, não reparo de pré-tendências.
- não aceite como válida uma saída anterior que mencione sete cursos unívocos:
  a ponte normativa corrigida admite apenas os cursos 1, 12 e 24 no núcleo
  integral sem sobreposição;
- não interprete `p>0,05` em um placebo isolado como comprovação de tendências
  paralelas.

## Trabalho

1. Congele a hierarquia substantiva antes dos diagnósticos:
   - **principal direto:** oferta imediata de anestesiologia sobre o estoque no
     CNES ofertante no mês 6, com atualização no mês 12;
   - **secundário-chave:** estoque municipal nos mesmos horizontes, necessário
     para separar expansão local de remanejamento entre estabelecimentos;
   - **mecanismos:** primeiro vínculo PMM-E, entradas, saídas, churn e número de
     entrantes/participantes ainda presentes, sem usar taxa condicionada a
     entrantes como outcome causal primário;
   - **secundário clínico-chave:** AIHs cirúrgicas eletivas no CNES e no
     município, somente se a família de procedimentos estiver validada;
   - **generalização:** cursos 12 e 24 em estimativas separadas e resumo
     empilhado predefinido; curso 2/CBO 225225 apenas como sensibilidade.
2. Defina a menor mudança relevante antes da MDE, em unidade natural e relativa
   ao baseline: um anestesiologista adicional e uma variação cirúrgica com
   justificativa de política.
3. Avalie suporte, distribuição de propensão, níveis e trajetórias prévias.
   Registre separadamente estoque total, vínculo que satisfaz a assinatura
   completa da Nota 59 e `070102` genérico.
4. Faça vários placebos temporais no pré-período, teste conjunto de leads e
   teste de
   equivalência contra limites derivados da mudança relevante.
5. Calcule MDE com cluster no município e simulação coerente com a estrutura do
   painel.
6. Compare, por rubrica pré-definida:
   - anestesiologia/força de trabalho municipal;
   - anestesia total/SIH no CNES e município;
   - anestesia isolada de outros cursos cirúrgicos;
   - oncologia clínica e medicina intensiva como generalização separada;
   - ecocardiografia/SIA apenas com metadados e pré-CNES, sem baixar SIA.
7. Estime a propensão somente com variáveis e trajetórias pré-tratamento,
   congele pesos de sobreposição e reporte a perda de suporte. Não use o
   preenchimento posterior para redefinir tratamento.
8. Avalie sensibilidade a pesos de sobreposição, suporte dentro de município e
   CNES, leave-one-region-out e placebos de CBO/procedimento.
9. Classifique cada módulo como `confirmatorio_condicional`, `associacao_ajustada`
   ou `inviavel`. A priorização não foi aleatória; nenhum diagnóstico permite
   chamá-la de experimento natural.
10. Só acione C3-04 se ecocardiografia puder substituir o módulo cirúrgico por critério
   substantivo e quantitativo pré-especificado.
11. Escreva o plano final com estimando, população, tratamento, controle, `T0`,
   outcomes, horizontes, equação, inferência, multiplicidade, contaminação,
   missing, winsorização e regras de linguagem.
12. Defina como primeiro estágio a proporção de células imediatas com vínculo
    PMM-E completo e o número desses vínculos. Se a assinatura não for
    implementada de forma confiável, preserve o estoque total como outcome e
    rebaixe retenção individual.
13. Pré-especifique DiD/event study com data comum e inferência agrupada no
    município; use wild cluster bootstrap. Synthetic DiD será apenas robustez.
14. Faça uma auditoria independente das rotinas de estimação, da construção dos
    clusters e do bootstrap antes de selar hashes.
15. Gere hashes do protocolo e das listas de unidades/códigos congeladas.

## Entregáveis

- `scripts/avaliacao_ciclo3/03_auditar_pre_e_potencia.py`;
- `output/avaliacao_ciclo3/diagnosticos_pre.csv`;
- `output/avaliacao_ciclo3/potencia_pre.json`;
- `output/avaliacao_ciclo3/decisao_torneio_pre.json`;
- `docs/13_plano_pre_analise_ciclo3.md`;
- `output/avaliacao_ciclo3/registro_pre_analise.json`.

## Portão

O JSON deve conter decisão única por módulo e nível, razões, números usados e hashes.
Resultados narrativos, CSVs de diagnóstico, MDE e JSON de decisão precisam
concordar exatamente. Se anestesiologia falhar equivalência de pré-tendência ou
suporte, a análise futura será associação ajustada. Se o módulo SIH falhar
potência ou ponte clínica, ele será exploratório e não será substituído
automaticamente por outro outcome. A generalização não pode esconder que
anestesiologia domina numericamente o núcleo de três cursos.

Incompletude do SIH não impede congelar o protocolo de força de trabalho e não
autoriza usar painéis clínicos preliminares. Registre os dois portões
separadamente.

Valide determinismo, referências locais, sintaxe JSON, testes e
`git diff --check`. Não modifique brutos. Crie commit próprio e não faça push.
