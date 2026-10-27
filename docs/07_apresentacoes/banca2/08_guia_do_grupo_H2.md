# Guia do grupo: a H2 em uma página (para acompanhar e montar os slides)

> **Para quem é:** para o grupo começar a acompanhar a parte empírica e montar os slides da banca 2.<br>
> **Data:** 27/10/2026.<br>
> **Estado:** a hipótese está decidida (doc [07](07_nova_hipotese.md)). A **análise completa da H2** já está na
> `main`: [doc 66](../../06_execucao/66_analise_completa_H2.md), com 6 figuras simples em
> `output/rdd_bolsa/H2_figuras/`, auditada na [auditoria 52](../../auditorias/52_auditoria_analise_H2.md)
> (aprovada com correções de redação e de rótulo; os números de estimação são cópia de saídas já auditadas). Atenção:
> o VL-1 compara vagas **da mesma UF** (a de origem ou outra), não "só vagas da UF de origem", e a F2 é descritiva:
> não vale como evidência à parte, porque a versão com inferência (VL-2) é inconclusiva.
> O deck novo está pronto e auditado ([auditoria 53](../../auditorias/53_auditoria_deck_H2.md)): no slide, use as
> figuras **do deck** (coluna "No deck" abaixo).<br>
> **Revisão pela rubrica da banca (27/10/2026, véspera):** o deck foi refeito pela rubrica e para cerca de 7 minutos
> (11 slides no corpo e 2 no apêndice). Mudou: um slide de **dados e amostra** com a unidade de observação e o funil
> por ciclo; o **modelo justificado**; a **leitura dos coeficientes** na tela; a robustez como "mantém / não se
> mantém"; **Conclusão** e **Limitações** no lugar da antiga Discussão. O roteiro de fala, com tempo por slide e as
> perguntas prováveis, está no [doc 09](09_roteiro_fala_7min.md); quem montou outra apresentação a partir do deck
> anterior (`8901dea`) encontra no [doc 10](10_mapa_deck_anterior_para_rubrica.md) o mapa slide a slide, o texto exato
> da tela e o checklist do que acrescentar.<br>
> **Regra do projeto:** todo número dos slides sai de `output/` por script. Os números abaixo servem para o grupo
> entender a história. No slide, use a figura gerada pelo pipeline, nunca um número digitado à mão.

## 1. A hipótese (H2)

**O médico especialista escolhe vagas perto de onde já trabalha. A bolsa maior muda *qual* vaga ele escolhe
dentro da mesma UF, mas pesa menos que a própria origem.** É coerente com não termos detectado aumento do
preenchimento no corte, mas essa ligação é interpretação, não teste.

- Foi formulada **depois** de ver os dados. Isso deve ser dito no slide.
- As outras hipóteses (antigas H1 e H3) saem do corpo e vão para um apêndice rápido (no máximo 2 slides).

## 2. A história em 6 passos (uma ideia por slide)

Na ordem do deck revisto (slides 1, 4, 7, 8, 9 e 10). As figuras "No deck" estão em `output/apresentacao_banca2/`.

| Passo | Mensagem | No deck (auditoria 53) | Doc 66 (auditoria 52) |
|---|---|---|---|
| 1. Motivação | no corte de IVS, não detectamos aumento do preenchimento onde a bolsa é R$ 5 mil maior | uma linha no slide 1; o gráfico vai para o apêndice (`curto_fato.png`, slide 12) | — |
| 2. Onde escolhem | a maioria põe a 1ª opção na mesma UF onde já trabalhava | `exp_escolha_origem.png` (slide 4) | `output/rdd_bolsa/H2_figuras/H2_F1_onde_escolhem.png` |
| 3. A origem pesa mais (o teste central da H2) | estar na UF de origem pesa mais que toda a diferença de bolsa | `curto_origem_bolsa.png` (slide 7) | `H2_F4_origem_contra_bolsa.png` (e `H2_F5_bolsa_em_km.png`) |
| 4. Entre vagas da mesma UF, a bolsa pesa (adendo pós-resultado) | comparando só vagas da mesma UF, a vaga de bolsa maior é mais escolhida | `curto_bolsa_mesma_uf.png` (slide 8) | `H2_F3_razao_chances_bolsa.png` (e o descritivo `H2_F2_mesma_uf_perto_do_corte.png`) |
| 5. Robustez | a origem pesa mais em todos os ciclos; a bolsa pesa com força só no ciclo 2, e perto do corte é inconclusivo | `curto_robustez_escolha.png` (slide 9) | `H2_F6_robustez.png` |
| 6. Teoria | incentivo limitado: a origem pesa mais que toda a bolsa (dado); os dados sugerem que um degrau de R$ 5 mil não compensa sair da própria UF (leitura, sem teste direto), sempre sobre o pacote do corte | texto (slide 10, Conclusão; as limitações no slide 11) | doc 66, seção 10 |

## 3. Os números que contam a história (para entender, não para digitar)

| O quê | Valor | Fonte (doc auditado) |
|---|---|---|
| 1ª opção na mesma UF de origem (descritivo) | 79% (mesma região de saúde: 46%; mesmo município: 36%; distância mediana 51 km) | `output/apresentacao_banca2/numeros_banca2.json` (`ESC_UF`) e figura `exp_escolha_origem.png` (bases `G1_*`) |
| Bolsa +R$ 5 mil, vagas da mesma UF, ciclos 1–3 (adendo pós-resultado) | razão de chances 1,47 [1,15; 1,89] | [57x](../../06_execucao/57x_resultados_escolha_localizacao_par.md), auditoria 48 |
| Idem, ciclo 2 | 1,90 [1,30; 2,78] | 57x |
| Sem fixar a UF (base, pré-registrada), ciclos 1–3 | 1,25 [0,98; 1,61]: não passa no Holm | [57p](../../06_execucao/57p_escolha_vaga_imediata_c2.md), auditoria 41 |
| +R$ 5 mil pesa como… | 75 km a menos de distância, dentro da mesma UF | 57x |
| Origem × toda a bolsa (D_UF) | 1,94 [1,48; 2,40] (em log-chance; > 0 = a origem pesa mais) | 57p |
| Só vagas perto do corte | 1,28 [0,95; 1,72]: inconclusivo | 57x |
| Ciclos 1 e 3 separados | perto de 1, IC largos: a bolsa desloca a escolha com força só no ciclo 2 | [57a](../../06_execucao/57a_resultados_P1_escolha.md), 57p |

**Como ler a razão de chances:** acima de 1, a vaga de bolsa maior é preferida a uma vaga parecida. Ela compara
duas vagas iguais no resto: o ×11,0 da origem quer dizer que, à mesma distância, a vaga na UF de origem tem 11,0
vezes a chance de ser a 1ª opção que uma vaga de outra UF (auditoria 55).

## 4. O que dizer e o que não dizer

| Dizer | Não dizer |
|---|---|
| "entre quem se candidatou, a vaga de bolsa maior é preferida a uma vaga parecida da mesma UF" | "a bolsa traz mais médicos" |
| "a origem pesa mais que toda a diferença de bolsa na escolha" | "a origem causa a escolha" (é preferência revelada) |
| "no corte, não detectamos aumento do preenchimento" | "a bolsa não encheu mais vagas", "a bolsa não tem efeito nenhum" ou "a bolsa reduz o preenchimento" |
| "em 0,400, se a bolsa traz médico de outra UF é inconclusivo" | "a bolsa não traz médico de longe" |
| "o contraste da bolsa é o pacote de regras que muda no corte" | "o efeito do PMM-E" |

**Ressalvas obrigatórias:** (1) a hipótese veio depois dos dados; (2) a origem é preferência, não causa (e é medida
pelo vínculo anterior no CNES); (3) a bolsa desloca a escolha com força só no ciclo 2; (4) a comparação só perto do
corte é inconclusiva; (5) tudo é condicional a se candidatar; (6) a bolsa é o pacote de regras do corte.

## 5. Estrutura obrigatória do deck (8 seções, até 14 slides + apêndice)

Hipótese → Dados → Análise descritiva → Metodologia → Identificação → Resultados → Robustez → Discussão
([doc 06](06_estrutura_obrigatoria_versao_final.md)). No máximo ~30 palavras por slide; o detalhe vai nas notas.

## 6. Onde está cada coisa

| Para | Arquivo |
|---|---|
| a hipótese e o roteiro | [07_nova_hipotese.md](07_nova_hipotese.md) |
| a avaliação das hipóteses (por que H2) | [`docs/06_execucao/65_avaliacao_forca_hipoteses.md`](../../06_execucao/65_avaliacao_forca_hipoteses.md) §4.6–4.8 |
| os resultados da escolha | docs 57a, 57i, 57p, 57v, 57x em `docs/06_execucao/` |
| a análise completa da H2 | [`docs/06_execucao/66_analise_completa_H2.md`](../../06_execucao/66_analise_completa_H2.md) ([auditoria 52](../../auditorias/52_auditoria_analise_H2.md)) |
| o deck | `output/apresentacao_banca2/deck_banca2_curto.pdf` (versão revista pela rubrica, 27/10/2026: 11 slides no corpo e 2 no apêndice; conteúdo em [04](04_conteudo_deck_curto.md)); a versão anterior, auditada na [auditoria 53](../../auditorias/53_auditoria_deck_H2.md), em `output/apresentacao_banca2/versoes/deck_banca2_curto_8901dea.pdf` |
| o roteiro de 7 minutos | [09_roteiro_fala_7min.md](09_roteiro_fala_7min.md) |
| o mapa do deck anterior para o novo | [10_mapa_deck_anterior_para_rubrica.md](10_mapa_deck_anterior_para_rubrica.md) |
| decisões e pendências | [05_discussao_historia_empirica.md](05_discussao_historia_empirica.md) §2.16 e §4.1 |
