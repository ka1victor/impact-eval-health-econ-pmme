# Auditoria independente do P4 (protocolo 54): trajetória individual dos médicos

> **Data:** 23/10/2026.<br>
> **Objeto:** commit `a922e66`: `scripts/rdd_bolsa/28_trajetoria_medicos.py`,
> `output/rdd_bolsa/P4_estimativas.csv`, `P4_resumo.json`, `P4_figuras/`, o
> [doc 57d](../06_execucao/57d_resultados_P4_trajetoria.md) e
> `tests/test_trajetoria_medicos.py`, contra o
> [protocolo 54](../06_execucao/54_protocolo_P4_oferta_substituicao.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.** Amostra, origem, T4.1b nas horas
> totais, no município do posto e fora dele, BKY e T4.3 foram reproduzidos com
> código próprio. Nenhuma estimativa mudou. As correções são de relato:
> - falhas de pré-tendência sem destaque onde os outcomes afetados são citados;
> - o doc não dizia, no texto, que o resultado é exploratório;
> - `p = < 0,001` na leitura;
> - um rótulo do T4.2 que sugeria retenção forte onde o critério é frouxo.<br>
> **Proveniência dos números:** todo número citado aqui foi lido de
> `output/rdd_bolsa/P4_estimativas.csv` e `P4_resumo.json`. A conferência que
> fica no repositório é a classe `TestRecalculoIndependenteAuditoria24` de
> `tests/test_trajetoria_medicos.py`.

## 1. Como a auditoria foi feita

O código de conferência foi escrito do zero, em pandas e numpy. Ele não importa
nenhuma função do script 28 nem a `rdd_lib`. Só a leitura das listas nominais
vem da função da X1 (script 17), porque ela dá o `id_medico`; nome, CRM e UF não
são gravados.

Fontes lidas:
- `output/aquisicao/cnes_profissional/painel_vinculo_mes.parquet` e
  `chaves_origem.parquet`;
- `output/rdd_bolsa/X1_medicos.parquet`;
- `data/` só pela leitura da X1, sem escrita; `git status` limpo em `data/`;
- `data/ivs_ipea_2010_municipios.csv` não foi lido.

## 2. Recálculo

O painel médico × mês foi refeito dos vínculos: horas = ambulatorial +
hospitalar SUS + outras; mês lido sem vínculo = zero; município do posto =
`co_ibge` da lista.

| Item | Linhas | Diferença |
|---|---:|---|
| Amostra: 1.865 médicos (D1) e 1.887 (literal), 1.397 e 1.419 tratados, 468 do ciclo 3 | 2 regras | idêntica |
| Fração já no município (X1 b) e fração de novos: total, ciclos 1 e 2, faixas 1 a 3, nas duas regras | 24 | 0 (n idêntico) |
| T4.1b, θ(e) de e = −6 a +6: horas totais, no município do posto e fora; D1 e literal | 72 | 4e-9 (arredondamento do CSV em 10 dígitos) |
| T4.1b, média de θ(0..+6) nesses 3 outcomes e 2 regras | 6 | 4e-9 |
| T4.3: Σ Δ município, Σ Δ fora, Σ saldo e fração compensada (ciclos 1 e 2, D1 e literal) | 8 | 3e-6 nas somas (CSV arredondado); 5e-11 na fração |
| BKY de T4.1b (98 linhas) e T4.1c (196), D1 | 294 | 9e-16; mesmas 91 e 173 linhas com q ≤ 0,05 |

Inferência. O script usa bootstrap multiplicador de Mammen; a auditoria usou
bootstrap não paramétrico por médico (B = 400), então só se espera acordo dentro
da variação de Monte Carlo:

| Outcome | IC 95% de θ(0..+6), auditoria | IC 95%, script | p do pré, auditoria | p do pré, script |
|---|---|---|---:|---:|
| horas totais | [+5,36; +7,84] | [+5,37; +7,84] | 0,276 | 0,310 |
| horas no município do posto | [+7,91; +9,50] | [+7,95; +9,46] | 0,0004 | 0,001 |
| horas fora do município do posto | [−3,15; −1,05] | [−3,16; −1,04] | 0,903 | 0,927 |

As conclusões dos testes dos pré coincidem: horas totais e fora do município
não rejeitam; horas no município do posto rejeitam.

Não foi recalculado de forma independente: T4.1c, a ligação com o painel
nacional do T4.2 (a09), a subamostra balanceada, os 11 outcomes restantes do
T4.1b e os ICs de Wilson. Esses pontos ficam cobertos só pelos testes do próprio
script (que usam o mesmo código) e por consistência interna (partes que somam o
total, `test_t43_saldo_e_soma`).

## 3. Conferência contra o protocolo

| Regra do protocolo 54 | Situação |
|---|---|
| Unidade médico × mês, D1 principal e literal como sensibilidade | ok |
| Janela principal [−6, +6], longa [−12, +10], balanceada 202412–202602 | ok; n por e no CSV |
| Nenhum CNES ≥ 202609 | ok. Máximo lido: 202608; o script aborta se houver outra |
| T4.1b: Callaway–Sant'Anna, controles ainda não iniciados (inclusive ciclo 3), base g − 1, semente 20261019 | ok; reproduzido nos pontos |
| BKY dentro do T4.1b e do T4.1c; o protocolo não pede Holm | ok. 14 outcomes × 7 meses por família |
| Mês sem o médico = zero vínculos, com rótulo; mês ausente da fonte não vira zero | ok. Nenhuma competência falta; 0 médico-mês com hora ausente |
| Linguagem "associado à entrada", "horas cadastradas" | ok (ver C1) |
| Figuras com "Como ler" | ok; 5 figuras, no máximo 3 frases cada |

Desvios datados (13 itens, todos de 23/10/2026): um registro por médico, ciclo 3
só controle, mínimo de 30 controles, inferência, controles do T4.1c, família do
BKY, natureza jurídica, sinal do T4.3, janelas do T4.2/T4.3, definição de
mudança no T4.2, cache privado e local do doc. Todos são coerentes com o
protocolo e estão justificados.

Ressalva, sem correção possível: o doc afirma que a regra de deduplicação e o
mínimo de controles foram "fixados antes de abrir os dados por tempo de evento".
O repositório tem um só commit do P4, então a auditoria não consegue verificar a
ordem. A auditoria conferiu apenas que as duas regras não dependem de nenhum
resultado do T4.1 (a deduplicação usa fonte da lista e data; o mínimo de 30 é
uma constante).

## 4. Integridade

- Nenhum nome, CPF, CNS, CRM, `id_prof` ou `id_medico` em `output/`. Varredura
  do CSV e do JSON: nenhum `g5p_`, `x1m_`, número de 11 ou 15 dígitos fora de
  casas decimais, nenhuma sequência de nomes em caixa alta. As palavras "CRM",
  "CPF" e "CNS" que aparecem no JSON são texto de integridade e de desvio.
- Todas as 7.170 linhas têm `natureza_dos_dados = EMPIRICO` e
  `estatuto = EXPLORATORIO_P4`.
- O arquivo local de IVS não é lido: o nome não aparece no script nem entre as
  entradas do resumo.
- `data/` não mudou no commit; os hashes das entradas e das figuras conferem.

## 5. Achados e correções

### C1. Falhas de pré-tendência sem destaque (corrigido)

O teste conjunto dos pré rejeita zero (p < 0,05) em 5 dos 14 outcomes do T4.1b
(vínculos, estabelecimentos, municípios, horas no estabelecimento do posto e
horas no município do posto) e em 7 combinações de outcome e origem do T4.1c.
Isso aparecia só num ponto da leitura. A frase "Onde estão as horas" citava o
resultado das horas no município do posto sem avisar que o teste rejeita, e as
tabelas mostravam o p sem marca.

O que foi feito, no script, e o doc foi regerado:
- os p < 0,05 do pré aparecem em negrito, com "(rejeita)", nas tabelas do T4.1b,
  do T4.1c e das sensibilidades;
- cada tabela ganha um aviso curto; as figuras do T4.1b (horas) e do T4.1c
  também;
- a frase "Onde estão as horas" diz, ao lado de cada outcome, se o teste dos
  pré rejeita;
- a leitura dos pré, agora chamada "Falha de pré-tendência", lista também as 7
  linhas do T4.1c;
- a seção do BKY e a leitura dizem que o q corrige o número de testes, não a
  falha de pré-tendência: as 264 linhas com q ≤ 0,05 incluem outcomes cujo pré
  rejeita.

### C2. O doc não dizia "exploratório" no texto (corrigido)

O estatuto aparecia só no cabeçalho, como `EXPLORATORIO_P4`. A seção 1 agora tem
o item "Resultado exploratório": sem exogeneidade validada para a data de
entrada, os números descrevem associação. A frase "horas cadastradas não são
horas trabalhadas" já estava.

### C3. `p = < 0,001` (corrigido)

A leitura escrevia "p = < 0,001". Agora "p < 0,001".

### C4. Rótulo do T4.2 sugeria retenção (corrigido)

"Fração que mantém horas na origem no pós" vale 98,6%. O critério é média de 0
a +6 maior que zero, ou seja, horas na origem em pelo menos um desses meses, um
critério que o início do período quase garante. O rótulo agora é "fração com
horas na origem em algum mês de 0 a +6 (critério frouxo)". Não é retenção
individual. O número não mudou.

### Observações, sem correção

- O T4.2 traz +209,4 h/sem de variação da mesma CBO no município de origem. A
  média por par pesa os municípios grandes e inclui a tendência local; o doc já
  avisa. Sem grupo de comparação, esse número não mostra deslocamento.
- O ponto de T4.1b em horas no município do posto antes do início fica cerca de
  0,8 h abaixo de zero; isso, e não a magnitude pós, é o que o teste dos pré
  detecta. Ver C1.

## 6. Saídas e testes

Nenhuma estimativa, figura ou JSON mudou: só o doc foi regerado por
`28_trajetoria_medicos.py --atualizar-doc`. `tests/test_trajetoria_medicos.py`
passou de 20 para 26 testes, com a classe `TestRecalculoIndependenteAuditoria24`
(amostra, origem por faixa, T4.1b em 3 outcomes e 2 regras, pré-tendência com
bootstrap próprio, T4.3 e destaque das falhas no doc). Com
`tests/test_pipeline_rdd_bolsa.py`: 41 testes, todos passam (a soma é 26 mais 15).
