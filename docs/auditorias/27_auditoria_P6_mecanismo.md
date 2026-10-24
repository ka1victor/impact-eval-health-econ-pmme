# Auditoria independente do P6 (protocolo 56): alocado por pouco contra não alocado por pouco

> **Data:** 24/10/2026.<br>
> **Objeto:** commit `df7df26`: `scripts/rdd_bolsa/30_mecanismo_alocacao.py`,
> `31_rd_mecanismo.py`, `output/rdd_bolsa/P6_*`, o
> [doc 57f](../06_execucao/57f_resultados_P6_mecanismo.md) e
> `tests/test_mecanismo_alocacao.py`, contra o
> [protocolo 56](../06_execucao/56_protocolo_P6_mecanismo_alocacao.md).<br>
> **Veredito:** **APROVADO COM CORREÇÕES.** Amostra, primeiro estágio, R1, Holm,
> BKY e balanço foram reproduzidos com código próprio. Nenhuma estimativa
> mudou. As correções são de relato:
> - o Y3 com p = 0,048 não dizia, no texto, que não é efeito;
> - os avisos (Y1 mecânico, desequilíbrio de distância e ligação) ficavam só na
>   leitura, longe da tabela dos resultados;
> - o "Como ler" do gráfico de outcomes sugeria efeito;
> - o gráfico de balanço usava nomes de variável como rótulo de eixo.<br>
> **Proveniência:** todo número aqui foi lido de `output/rdd_bolsa/P6_*`. A
> conferência que fica no repositório é a classe
> `TestRecalculoIndependenteAuditoria27` de `tests/test_mecanismo_alocacao.py`.

## 1. Método

Código novo em pandas e numpy, sem importar os scripts 30 e 31, a partir de
`P6_amostra.parquet` (agregado pseudônimo versionado). Efeito fixo de célula por
centragem dentro da célula, só células com os dois lados. Permutação dentro da
célula com semente própria. O cache privado existe no worktree e está no
`.gitignore`; o recálculo não precisou dele.

## 2. Recálculo

| Item | Script | Auditoria |
|---|---|---|
| Universo: candidatos e células (regra principal) | 320 em 62 | 320 em 62 |
| Janela R1, ligados: acima e abaixo | 64 e 70 | 64 e 70 |
| Células com os dois lados; acima e abaixo efetivos | 27; 30 e 68 | 27; 30 e 68 |
| Primeiro estágio D (ligados) | +1,000 | +1,000 |
| Primeiro estágio D' (ligados; todos) | +0,918; +0,926 | +0,918; +0,926 |
| R1 Y1, 202608 | +0,420 | +0,4197 |
| R1 Y1, média | +0,405 | +0,4048 |
| R1 Y3, média | +15,5 | +15,53 |
| p de permutação Y1 (último; média) | 0,001; 0,001 | < 0,001 (piso do script: 0,001) |
| p de permutação Y3, média | 0,048 | 0,048 (2.999 permutações) |
| Holm e BKY da família de 10, a partir dos p do script | 10 valores | idênticos (3 casas) |
| Balanço: distância | +328,9 km, p = 0,052 | +328,9 km, p = 0,052 |
| Balanço: taxa de ligação | +0,091; 100,0% e 93,3% | +0,0913; 100,0% e 93,2% |

Os outros 7 testes da família (Y2, Y4, Y5, Y3 no último mês) também batem nas
estimativas e nos p, dentro da variação de Monte Carlo (até 0,02). A taxa de ligação abaixo é 93,2% na amostra das células com os dois lados e 93,3% no script (que usa todos da janela abaixo).

## 3. Conferência contra o protocolo

| Ponto | Situação |
|---|---|
| Unidade do corte "célula × ampla concorrência" | **Justificada.** Não é desvio do §1: o protocolo manda usar "célula × modalidade de concorrência, se a modalidade estiver no dado", e ela está. A escolha de olhar só a ampla concorrência foi fixada depois de ver contagens do G2 por r e antes de qualquer outcome; o doc diz isso e que, sem ela, não sobraria candidato com r > 0. Ressalva: a ordem não é verificável pelo Git (um só commit) |
| Candidatos de reserva | Excluídos e contados: 0 no ciclo 1, 5 no ciclo 2 (na célula elegível) |
| Exclusão por motivo, por célula | `P6_celulas.csv`; cada uma com motivo |
| R6 e T6.3 `NAO_EXECUTADO` | Justificados. R6 coincide com o R1 neste desenho (escore 0 abaixo, 1 acima, indefinido no empate), condição do §4 ("se estável") não satisfeita. T6.3 o próprio protocolo manda não rodar |
| Ciclo 3 fora; r = 0 fora do principal | ok |
| Nenhum CNES ≥ 202609 | ok: máximo lido 202608 em `P6_cobertura_mensal.csv`; o script aborta se houver outra |
| Arquivo local de IVS | não lido |

## 4. Privacidade

- Varredura de todo `output/` do diff (P6_amostra, celulas, cobertura,
  estimativas, resumos, figuras): nenhum nome, CPF (inclusive mascarado), CNS ou
  CRM. As ocorrências de "CPF", "CRM", "CNS" e "id_prof" nos JSON são texto de
  integridade e nome de coluna do esquema; nenhum `id_prof` ligável a candidato
  está em coluna de dados. Os números longos achados são decimais e hashes.
- `P6_amostra.parquet` só tem `id_candidato` (posição pseudônima, a mesma já
  versionada no G1 e no G2), célula, CNES do posto, município da 1ª opção, nota e
  outcomes agregados por candidato. Não há `id_prof`. Observação, sem correção: com
  as listas públicas do edital, quem conhece a célula e a nota pode localizar um
  candidato; o padrão é o do G1 e do G2.
- O cache privado (`cache_privado/chaves_extra_P6.parquet`, `G1_cache/`) está no
  `.gitignore` (`git check-ignore` confirma) e `git show --stat df7df26` não o
  lista.
- Os painéis do a16 (`output/aquisicao/cnes_profissional/`) não aparecem no diff do
  commit contra o commit base: o `id_prof` do P4 não foi renumerado.

## 5. Achados e correções

### C1. Y3 com p = 0,048 sem aviso (corrigido)

O doc dizia "3 têm p < 0,05" sem dizer quais nem que o Y3 não sobrevive. Agora a
leitura tem o item "Y3, média do seguimento, não é efeito": q de BKY 0,147, p de
Holm 0,384, p = 0,113 no último mês e R3 de +0,6. Diz também que os ICs do R4
que excluem zero em Y2 a Y4 não são evidência (sem permutação nem correção, com
desempate por regra fixa), e que os dois que rejeitam depois do Holm são os do
Y1.

### C2. Avisos longe da tabela dos resultados (corrigido)

Logo abaixo da tabela do R1 há agora "Leia com três avisos": Y1 quase mecânico;
distância origem–1ª opção (+329 km, p = 0,052) e taxa de ligação (100,0% contra
93,3%) desequilibradas, com outcomes só para ligados; Y3 não sobrevive à correção.
Os números do aviso saem de `output/`.

### C3. "Como ler" (corrigido)

O dos outcomes dizia que um degrau "sugere efeito de ser alocado". Agora diz que o
degrau do Y1 é quase mecânico e que nos demais os intervalos se sobrepõem. O do
balanço aponta o desequilíbrio. Os quatro têm no máximo 3 frases (teste existente).
As figuras não têm título nem legenda embutida; os rótulos dos eixos do balanço
(`vinculo_medico_pre`, `dist_km`) viraram texto legível.

### Observações, sem correção

- Os IC do gráfico de médias por r são normais e saem de [0, 1] no Y1 e em
  frações com poucos casos; é aparência, o texto não se apoia neles.
- Em r = −1 a taxa de ligação é 89,1%, a menor da janela; combinada com 100% acima,
  é o que produz o desequilíbrio. Nenhum limite de Manski foi calculado (fora do
  protocolo).
- A estimativa do Y1 e de todo outcome é efeito de ser alocado na 1ª opção, não da
  bolsa, para ampla concorrência nas 27 células com os dois lados.

## 6. Saídas e testes

Nenhuma estimativa, tabela de CSV ou contagem mudou. Foram regerados, pelo script
31: o doc 57f, `P6_balanco.png` e `P6_resumo.json` (textos e hash da figura).
`tests/test_mecanismo_alocacao.py` ganhou `TestRecalculoIndependenteAuditoria27` (5
testes). Com `test_trajetoria_medicos.py` e `test_pipeline_rdd_bolsa.py`: 73 testes,
todos passam.
