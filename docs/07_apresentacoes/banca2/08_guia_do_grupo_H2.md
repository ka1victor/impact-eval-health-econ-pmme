# Guia do grupo: a H2 em uma página (para acompanhar e montar os slides)

> **Para quem é:** para o grupo começar a acompanhar a parte empírica e montar os slides da banca 2.<br>
> **Data:** 27/10/2026.<br>
> **Estado:** a hipótese está decidida (doc [07](07_nova_hipotese.md)). Um agente está reconstruindo o deck e
> outro está escrevendo a análise completa da H2 (doc 66, em `docs/06_execucao/`). Os dois entram na `main` quando
> forem auditados. Até lá, use este guia e as figuras listadas abaixo, que já estão prontas e auditadas.<br>
> **Regra do projeto:** todo número dos slides sai de `output/` por script. Os números abaixo servem para o grupo
> entender a história. No slide, use a figura gerada pelo pipeline, nunca um número digitado à mão.

## 1. A hipótese (H2)

**O médico especialista escolhe vagas perto de onde já trabalha. A bolsa maior muda *qual* vaga ele escolhe
dentro da sua região, mas pesa menos que a própria origem. Por isso não aumenta o número de vagas preenchidas.**

- Foi formulada **depois** de ver os dados. Isso deve ser dito no slide.
- As outras hipóteses (antigas H1 e H3) saem do corpo e vão para um apêndice rápido (no máximo 2 slides).

## 2. A história em 6 passos (uma ideia por slide)

| Passo | Mensagem | Figura pronta |
|---|---|---|
| 1. Motivação | no corte de IVS, a bolsa R$ 5 mil maior não encheu mais vagas | só uma linha de texto; o gráfico vai para o apêndice |
| 2. Onde escolhem | a maioria põe a 1ª opção na mesma UF onde já trabalhava | `output/apresentacao_banca2/exp_escolha_origem.png` |
| 3. A bolsa pesa dentro da região | comparando só vagas da mesma UF, a vaga de bolsa maior é mais escolhida | `output/rdd_bolsa/VL_figuras/VL_razao_chances_e_km.png` |
| 4. Mas a origem pesa mais | estar na UF de origem pesa mais que toda a diferença de bolsa | `output/rdd_bolsa/P1h_figuras/P1h_magnitudes.png` |
| 5. Robustez | a leitura não muda com o quadro corrigido do ciclo 2 nem com outras variantes | `output/rdd_bolsa/VC_figuras/VC_antigo_corrigido.png`, `output/rdd_bolsa/VD_figuras/VD_antigo_corrigido.png` |
| 6. Teoria | incentivo limitado: o custo de sair da própria região pesa mais que o degrau da bolsa | texto |

## 3. Os números que contam a história (para entender, não para digitar)

| O quê | Valor | Fonte (doc auditado) |
|---|---|---|
| 1ª opção na mesma UF de origem | 79% (mesma região de saúde: 46%; mesmo município: 36%; distância mediana 51 km) | figura `exp_escolha_origem.png` (bases `G1_*`) |
| Bolsa +R$ 5 mil, vagas da mesma UF, ciclos 1–3 | razão de chances 1,47 [1,15; 1,89] | [57x](../../06_execucao/57x_resultados_escolha_localizacao_par.md), auditoria 48 |
| Idem, ciclo 2 | 1,90 [1,30; 2,78] | 57x |
| Sem fixar a UF (base), ciclos 1–3 | 1,25 [0,98; 1,61] | [57p](../../06_execucao/57p_escolha_vaga_imediata_c2.md), auditoria 41 |
| +R$ 5 mil pesa como… | 75 km a menos de distância, dentro da mesma UF | 57x |
| Origem × toda a bolsa (D_UF) | 1,94 [1,48; 2,40] (em log-chance; > 0 = a origem pesa mais) | 57p |
| Só vagas perto do corte | 1,28 [0,95; 1,72]: inconclusivo | 57x |
| Ciclos 1 e 3 separados | perto de 1, IC largos: a bolsa desloca a escolha com força só no ciclo 2 | [57a](../../06_execucao/57a_resultados_P1_escolha.md), 57p |

**Como ler a razão de chances:** acima de 1, a vaga de bolsa maior é preferida a uma vaga parecida.

## 4. O que dizer e o que não dizer

| Dizer | Não dizer |
|---|---|
| "entre quem se candidatou, a vaga de bolsa maior é preferida a uma vaga parecida da mesma UF" | "a bolsa traz mais médicos" |
| "a origem pesa mais que toda a diferença de bolsa na escolha" | "a origem causa a escolha" (é preferência revelada) |
| "no corte, não detectamos aumento do preenchimento" | "a bolsa não tem efeito nenhum" ou "a bolsa reduz o preenchimento" |
| "o contraste da bolsa é o pacote de regras que muda no corte" | "o efeito do PMM-E" |

**Ressalvas obrigatórias:** (1) a hipótese veio depois dos dados; (2) a origem é preferência, não causa; (3) a bolsa
desloca a escolha com força só no ciclo 2; (4) a comparação só perto do corte é inconclusiva.

## 5. Estrutura obrigatória do deck (8 seções, até 14 slides + apêndice)

Hipótese → Dados → Análise descritiva → Metodologia → Identificação → Resultados → Robustez → Discussão
([doc 06](06_estrutura_obrigatoria_versao_final.md)). No máximo ~30 palavras por slide; o detalhe vai nas notas.

## 6. Onde está cada coisa

| Para | Arquivo |
|---|---|
| a hipótese e o roteiro | [07_nova_hipotese.md](07_nova_hipotese.md) |
| a avaliação das hipóteses (por que H2) | [`docs/06_execucao/65_avaliacao_forca_hipoteses.md`](../../06_execucao/65_avaliacao_forca_hipoteses.md) §4.6–4.8 |
| os resultados da escolha | docs 57a, 57i, 57p, 57v, 57x em `docs/06_execucao/` |
| a análise completa da H2 | doc 66 (em preparação) |
| o deck | `output/apresentacao_banca2/deck_banca2_curto.pdf` (a versão com a H2 está sendo gerada; a atual ainda é a antiga) |
| decisões e pendências | [05_discussao_historia_empirica.md](05_discussao_historia_empirica.md) §2.16 e §4.1 |
