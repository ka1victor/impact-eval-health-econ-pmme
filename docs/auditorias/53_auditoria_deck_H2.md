# 53. Auditoria do deck novo da banca 2 (só a H2: 11 slides no corpo e 2 no apêndice)

> **Data:** 27/10/2026, véspera da banca 2.<br>
> **Objeto:** `output/apresentacao_banca2/deck_banca2_curto.pptx` e `.pdf` no commit `a4b9329` (branch
> `claude/vigilant-mccarthy-dd92mc`). Também as figuras novas `curto_origem_bolsa.png`, `curto_bolsa_mesma_uf.png`,
> `curto_robustez_escolha.png` e `curto_fato.png`, os geradores `scripts/apresentacao/gerar_deck_banca2.py` e
> `gerar_figuras_banca2.py`, o registro `numeros_banca2.json`, os docs 03, 04, 05 (§4.1), 06, README e 08 da banca 2
> e os testes `tests/test_deck_curto_banca2.py` e `tests/test_conteudo_banca2.py`.<br>
> **Referências:** `CLAUDE.md`; [doc 07](../07_apresentacoes/banca2/07_nova_hipotese.md) (fonte da verdade);
> auditorias 49 e 50 (regras de redação); docs 57p, 57i, 57a, 57v, 57x, 57n e 57w; auditorias 31, 41, 46, 47 e 48;
> [doc 66](../06_execucao/66_analise_completa_H2.md) e [auditoria 52](52_auditoria_analise_H2.md), que terminou durante
> esta auditoria. Os achados da 52 que valem para o deck foram incorporados (seção 1, A6 a A9).<br>
> **Método:**
> 1. texto e notas lidos com python-pptx; PDF renderizado em PNG e visto slide a slide;
> 2. cada código da linha `**Números:**` do doc 04 relido da saída de origem com código próprio (filtro, coluna e
>    transformação do seletor, sem importar o gerador): 0 diferenças; os descritivos (`D_C*`, `ESC_*`) foram recalculados das bases;
> 3. exp(θ_UF), exp(10·β) e θ_UF − 10·β recalculados de `VC_estimativas.csv`;
> 4. contagens dos ciclos recalculadas de `outcomes_V_celula.parquet` e `P1_resumo.json`;
> 5. redação lida contra as auditorias 49, 50 e 52;
> 6. testes rodados antes e depois, com o deck do grupo (`PMME_DECK_GRUPO`), o que inclui o teste de determinismo.
>
> Nada foi reestimado. Nada foi gravado em `data/` nem nas saídas de estimação.

## Veredito

**Aprovado com correções.** Todas as correções já foram aplicadas, e o deck foi regerado.

- **Números.** Todos os números dos slides e das notas conferem com a saída de origem (seção 2). Os "×11,0 [9,7;
  12,5]" e "×1,57 [0,96; 2,58]" são exp(θ_UF) e exp(10·β) do M1 corrigido (quadro do ciclo 2 de 13/02/2026),
  linhas `mesma_uf` e `bolsa_mil` de `VC_estimativas.csv` (adendo 52c). Não há número inventado nem vencido.
- **Afirmações.** O problema está em quatro pontos:
  - um rótulo trocado (slide 10);
  - uma amostra diferente sem aviso (slide 12);
  - uma interpretação dita como dado (slide 11);
  - um número fora de `output/` nas notas do slide 12.

  Pela auditoria 52, há ainda mais quatro: o VL-1 descrito como "dentro da região", o M1 pré-registrado em segundo
  plano, a leitura teórica sem "sugere" e o Holm de família de um teste dito como correção.
- **Forma.** A forma está aprovada:
  - as 8 seções estão na ordem;
  - há 11 slides no corpo e 2 no apêndice;
  - cada slide tem no máximo 29 palavras;
  - toda figura tem "Como ler";
  - nenhum texto fica cortado nem passa sobre o logo.
- **Testes.** A proveniência das figuras ficou igual. A lista de frases proibidas, porém, perdeu guardas antigas, que
  foram restauradas.

## 1. Achados, por gravidade

Não há achado grave: nenhum número está errado, e o teste central está bem descrito.

### Médios (corrigidos)

**A1. Slide 12 (apêndice, o fato): a linha "RDD com efeito fixo de UF" usa outra amostra, e a figura não dizia.**

- A PH-4 (adendo 48h) só usa municípios com a medida de especialistas a 100 km (o "raio"). O 57w §6 mostra que,
  nessa amostra, sem controle, a HI-1 já é −0,4 p.p. em 0,300 (contra −3,7 na amostra toda) e +1,8 em 0,400 (contra
  −2,3).
- Parte do movimento de −3,7 para +5,4 vem, portanto, da amostra, e não da UF.
- O rótulo também omitia o raio.

**Correção:**
- no gerador de figuras, os códigos novos `PL_H4{1,2}_{300,400}_SC` lêem `tau_sem_controle` do `PL_estimativas.csv`;
- o rótulo passou a "RDD com UF e raio", com "sem controle nela: −0,4" e "+1,8" ao lado;
- o "Como ler" passou a dizer que é amostra menor;
- as notas ganharam os mesmos números.

**A2. Pendência conhecida, notas do slide 12: "só com a UF, o ponto cai à metade".**

- O sentido está certo (auditoria 47, observações: −1,15 → −0,55 só com a UF).
- Mas é uma quantidade ("metade") cujo número (−0,55) só existe na auditoria 47, não em `output/`. Pela regra do
  `CLAUDE.md`, isso não vai ao deck. Sem o número, a frase ficava honesta no sentido, mas não verificável.

**Correção:** a frase saiu. As notas agora dizem: "na mesma amostra, sem controle, −1,15; com efeito fixo de UF e os
especialistas no entorno, −0,62 [...]; o que move o ponto é a UF, não o raio (auditoria 47)". O −1,15 vem do registro
(`PL_H42_300_SC`); a atribuição à UF é qualitativa e auditada. O teste proíbe "cai à metade" e "−0,55".

**A3. Slide 10: a cautela "Quadro da inscrição, log e região: mesma leitura" trocava o rótulo.**

O quadro da inscrição (13/02/2026) é a **base**. A variante mostrada, em cinza, é o quadro **refeito depois do
resultado** (19/03/2026; 57p).

**Correção:** a cautela foi reescrita junto com A7 (abaixo).

**A4. Slide 11: em "Dados", a frase "o custo que domina é sair da própria região" é interpretação.**

- O dado é D_UF > 0: a vaga na UF de origem pesa mais que toda a diferença de bolsa.
- "Custo" é leitura pelo modelo. θ_UF é preferência revelada e mistura família, rede, registro e o emprego atual
  (auditoria 50, A13; doc 66 §5).
- A evidência é no nível da UF, não da "região".

**Correção:** Teoria / Dados / Leitura = "aceita se a bolsa compensa o custo do lugar" / "a origem pesa mais que toda
a bolsa" / "os dados sugerem incentivo limitado (pacote do corte)". As notas separam o dado da leitura, dizem
"sugerem, sem teste direto" e trocam "vagas próximas" por "vagas da mesma UF".

**A5. Notas do slide 10: faltava dizer que o peso da bolsa sozinho depende da especificação.**

- Com o logit explodido (M7; doc 57v), o IC contém 1.
- Com o spline cúbico do IVS (E9; doc 42 §5.2), também.
- O D_UF fica acima de zero em todas as variantes.

**Correção:** uma frase nas notas, sem número novo.

### Médios, da auditoria 52 (corrigidos)

**A6. O VL-1 compara vagas da mesma UF, a de origem ou outra.** As notas do slide 1 diziam "dentro da sua região".
Agora dizem "entre vagas da mesma UF". O "Como ler" do slide 9 e as notas dos slides 6 e 9 agora trazem "a de origem
ou outra". O teste proíbe "dentro da região", "dentro da sua região" e "só vagas da UF de origem".

**A7. O M1 pré-registrado tem de vir na frente do adendo.**

- No slide 9, a linha cinza chamava-se "Modelo base". Passou a "Pré-registrado (M1)", e o "Como ler" diz que a
  linha verde é adendo pós-resultado.
- No slide 10, o M1 dos ciclos 1–3, 1,25 [0,98; 1,61], não aparecia. Agora abre a figura ("Pré-registrado (M1)").
- A cautela do slide 10 passou a "Pré-registrado: IC contém 1; variantes do adendo: mesma leitura".
- As notas do slide 10 abrem pelo M1.

**A8. A teoria passou a ser dita como "sugere", sempre sobre o pacote do corte** (slide 11; ver A4).

**A9. O "Holm 0,072" é de uma família com um único teste (P1a), em que Holm = p.**

- A cautela do slide 9 dizia "sem fixar a UF, Holm 0,072", como se fosse correção múltipla. Passou a
  "pré-registrado, sem fixar a UF: p 0,072".
- As notas dos slides 7 e 9 dizem "p 0,072; família de um teste, Holm = p".
- O D_UF já dizia "família de um teste".

Os km estão na ordem certa. A tela do slide 9 cita 75 km (IC [28; 122], sem zero). Os 119 km [−12; 250] do M1 só
aparecem nas notas, depois dos 75 km.

### Menores (corrigidos)

**A10. O título do slide 9, "a vaga de bolsa maior atrai", pode ser ouvido como "atrai médicos".** Isso o doc 07 §3
não permite afirmar. O título passou a "Dentro da mesma UF, a vaga de bolsa maior é preferida", na frase do doc 07.

**A11. Os testes perderam guardas antigas na reescrita de 27/10.**

- Foram restaurados:
  - a lista da auditoria 36 (`PROIBIDAS_A36`);
  - "SOCR";
  - "em auditoria" no deck;
  - "52c", "fuzzy", "candidato de 1ª opção" e "escolhidas em 1º lugar" na tela;
  - "EM AUDITORIA" nas descrições dos códigos.
- Foram acrescentadas as frases das seções A1 a A10, e um teste novo (`test_fato_mesma_amostra`).
- O teste de proveniência das figuras é idêntico ao anterior. Não enfraqueceu.

**A12. Docs desatualizados.**

| Doc | O que estava | Correção |
|---|---|---|
| README | o doc 66 "em preparação" | o doc 66 está na `main`, auditado na 52 |
| doc 05, item 23 | idem | idem; item 24 novo (esta auditoria) |
| guia 08 | o deck "sendo reconstruído"; a tabela apontava as figuras do doc 66, então sob auditoria, em ordem diferente da do deck | conflito com a versão da auditoria 52 resolvido; agora aponta as figuras **do deck** por slide, com as do doc 66 ao lado |
| doc 06 §3 | Discussão e apêndice | descritos como ficaram |
| doc 03 | G29 (título) e G31 (rótulo) | atualizados |

**A13. A docstring de `figura_fato` dizia "não enche mais vagas; o negativo era localização".** Não ia à tela, mas é
redação proibida. Foi reescrita.

**A14. As notas do slide 7 citavam só o doc 57a para a IIA.** Esse M9 usa o quadro do ciclo 2 de 19/03. Foi
acrescentado o doc 57v, com o quadro de 13/02.

### Observações (sem correção)

- **Dois N diferentes, ambos corretos.** O 5.425 do slide 5 (descritivo G1) e o 5.421 dos slides 3 e 6 (amostra
  P1) diferem em 4 candidatos: são as exclusões do P1 por falta de região de saúde (3 no ciclo 1 e 1 no ciclo 2;
  `P1_resumo.json`).
- **"A origem pesa mais em todos os ciclos" (título do slide 10) confere.**
  - Ciclo 1: D_UF 2,34 [1,45; 3,24].
  - Ciclo 2: 1,19 [0,51; 1,86].
  - Ciclo 3: 2,37 [1,75; 3,00].
  - Os três IC excluem zero; o p unilateral mais alto é 2,8e−4.
  - São secundárias, sem Holm (o M5 entra no BKY da família secundária do P1, não refeito; 57p). O ciclo 2 tem o
    menor D_UF porque a bolsa pesa mais nele.
- **"Forte só no ciclo 2"** repete o doc 07 §4 ("com força só no ciclo 2"). O IC do ciclo 2, 1,19 a 2,68, exclui 1.
- **"Anda junto com a UF"** está no texto. "Some" não aparece em lugar nenhum.
- **"Médico de outra UF em 0,400"** é chamado de inconclusivo, com poucos pares (notas do slide 12).
- **"Não detectamos aumento"** está no slide 1 e nas notas do slide 11; "sem aumento detectado", no título do
  slide 12.
- **O VL-1 é tratado como pós-resultado** na cautela e nas notas, e como "não testa a comparação com a origem".
- **Pacote do corte, preferência revelada e "condicional a se candidatar"** estão nas notas dos slides 1, 7, 8, 9,
  10 e 11.
- **O doc 07 era a fonte da verdade.** A auditoria 52 trocou "dentro da sua região" por "entre vagas da mesma UF".
  O deck acompanha.

## 2. Tabela de conferência

Fonte: `rdd/` = `output/rdd_bolsa/`. O "Código" é o do registro `numeros_banca2.json`. A coluna "Confere" diz se o
valor bate com a saída de origem, relida por código próprio.

| Slide | Número(s) | Código | Fonte (arquivo; filtro) | Confere |
|---|---|---|---|---|
| 3 | células 1.295 / 1.547 / 2.293 | `D_C*_CEL` | `outcomes_V_celula.parquet`, linhas por ciclo | sim |
| 3 | candidatos 993 / 2.140 / 2.581 | `D_C*_CAND1` | idem, soma de `n_cand_1a_opcao` | sim |
| 3 | com origem 915 / 2.032 / 2.474; 5.421 | `D_C*_P1`, `M1_N` | `P1_resumo.json` `amostra.p1_por_ciclo`; `P1_estimativas.csv` M1 | sim (soma = 5.421) |
| 4, 7 | 368/368, 454/454; 404/404; 747/748 | `R_*` | `portao_r1_ivs_oficial.json` | sim |
| 5 | 79%, 46%, 36%; 51 km e 189 km; 5.425 | `ESC_*` | `G1_distancias_opcoes.parquet` + `G1_candidatos_origem` | sim (0,7917; 0,4579; 0,3583; 51,4; 188,5) |
| 7, 9 | p 0,072 (P1a, família de um teste) | `VC_B_HOLM` | `VC_estimativas.csv`, corrigida_13fev, M1, `bolsa_mil`, `p_holm` | sim (0,07238 = p) |
| 8 | D_UF 1,94 [1,48; 2,40]; p < 0,001 | `VC_DUF_*` | `VC_estimativas.csv`, M1, `D_UF` | sim (1,9421 = 2,3950 − 10 × 0,04529) |
| 8 | θ_UF 2,40 [2,27; 2,52]; ×11,0 [9,7; 12,5] | `VC_THETA*`, `VC_THETAX*` | idem, `mesma_uf`; exp | sim (exp 2,3950 = 10,97) |
| 8 | 10·β 0,45 [−0,04; 0,95]; ×1,57 [0,96; 2,58] | `VC_B10*`, `VC_B10X*` | idem, `bolsa_mil` × 10; exp | sim (exp 0,4529 = 1,573) |
| 9 | VL-1 1,47 [1,15; 1,89], Holm 0,005; ciclo 2 1,90 [1,30; 2,78], Holm 0,003 | `VL1_*` | `VL_estimativas.csv`, VL1_emp / VL1_c2 | sim |
| 9, 10 | M1 1,25 [0,98; 1,61]; ciclo 2 1,79 [1,19; 2,68] | `VLB_*` | `VL_estimativas.csv`, M1_emp / M1_c2 | sim (= exp(5β) do VC) |
| 9 | 75 km [28; 122]; 117 [56; 178]; 119 [−12; 250]; 302 [88; 516] | `VL1_*_K5*`, `VLB_*_K5*` | `VL_estimativas.csv`, `km_equivalentes` K5 | sim |
| 10 | ciclos 1,07 [0,69; 1,65], 1,79, 1,00 [0,72; 1,39] | `VC_M5C*` | `VC_estimativas.csv`, M5_1/2/3 | sim |
| 10 | quadro refeito 1,70 [1,22; 2,37] | `VC_M5C2A_*` | `VC_estimativas.csv`, antiga_19mar, M5_2 | sim (57p §1) |
| 10 | log 1,45 [1,15; 1,83] (c2 1,75 [1,23; 2,49]); região 1,49 [1,15; 1,92] (c2 1,91 [1,33; 2,74]) | `VLLOG_*`, `VL3_*` | `VL_estimativas.csv` | sim |
| 10 | perto do corte 1,28 [0,95; 1,72], Holm 0,103 | `VL2_EMP_*` | idem | sim |
| 10 | D_UF por ciclo 2,34 [1,45; 3,24]; 1,19 [0,51; 1,86]; 2,37 [1,75; 3,00] | `VC_DUF_C*` | `VC_estimativas.csv`, M5_k, `D_UF` | sim; os três IC excluem 0 |
| 12 | HI-1 −3,7 [−21,3; +13,9] e −2,3 [−24,0; +19,4]; Holm 1,000; MDE 25,1 e 31,0 | `HI1_*` | `HI_estimativas.csv`, HI-1 principal | sim (Holm 1,0 nos dois cortes) |
| 12 | UF e raio +5,4 [−11,0; +21,8] e −4,2 [−21,1; +12,6]; sem controle nela −0,4 e +1,8 | `PL_H41_*` | `PL_estimativas.csv`, PH-4 HI-1 | sim (código `_SC` novo) |
| 12 | pareados +16,4 [−3,8; +36,6] (25 pares) e −6,0 [−23,2; +11,5] (29) | `PL_FRAC_*` | `PL_estimativas.csv`, PH-1 | sim |
| 12 | HI-2 −1,13 [−2,15; −0,10], Holm 0,126; mesma amostra −1,15; UF e raio −0,62 [−1,67; +0,43] | `HI2_300_*`, `PL_H42_300_*` | `HI_estimativas.csv`; `PL_estimativas.csv` PH-4 HI-2 | sim |
| 12 | por ciclo −1,07 [−2,88; +0,74], −0,97 [−2,48; +0,55], −1,33 [−3,59; +0,93] | `HI2_C*` | `HI_estimativas.csv`, HI-s1 | sim |
| 12 | balanço −29,9; −47,7; +10,54 | `CL_BAL_*` | `CL_balanco.csv`, CL-0, 0,300 | sim |
| 12 | outra UF +0,02 [−0,01; +0,06]; +0,16 [+0,00; +0,35] | `PL_OUT_*` | `PL_estimativas.csv`, PH-5 | sim (limite −5e−11 mostrado +0,00) |
| 13 | +6,6 h/sem [+5,4; +7,8]; 51,0% [48,4; 53,7]; Holm 1,000 | `P4_*`, `OC_B1_*` | `S57_resumo.json`; `OC_estimativas.csv` | sim |

## 3. O que mudou no deck

| Slide | Antes | Depois |
|---|---|---|
| 1 (notas) | "dentro da sua região" | "entre vagas da mesma UF" |
| 6, 7 (notas) | — | "a de origem ou outra"; "p 0,072; família de um teste, Holm = p"; 57v para a IIA |
| 9 | título "… atrai"; cautela "Holm 0,072"; linha cinza "Modelo base" | "… é preferida"; "pré-registrado, sem fixar a UF: p 0,072"; "Pré-registrado (M1)"; "Como ler" com o adendo e "a de origem ou outra" |
| 10 | sem o M1 dos ciclos 1–3; cautela "Quadro da inscrição, log e região: mesma leitura" | o M1 abre a figura; "Pré-registrado: IC contém 1; variantes do adendo: mesma leitura"; notas com o M1 e a dependência da especificação |
| 11 | Dados "o custo que domina é sair da própria região"; Leitura "a bolsa reordena vagas próximas" | Dados "a origem pesa mais que toda a bolsa"; Leitura "os dados sugerem incentivo limitado (pacote do corte)"; notas separando dado e leitura |
| 12 | "RDD com efeito fixo de UF"; notas com "cai à metade" | "RDD com UF e raio", com o ponto sem controle na mesma amostra; notas com −1,15 → −0,62 |

As figuras foram regeradas por `gerar_figuras_banca2.py`. Mudaram `curto_fato.png`, `curto_bolsa_mesma_uf.png` e
`curto_robustez_escolha.png`; as outras saíram idênticas. O deck foi regerado por `gerar_deck_banca2.py --curto`
com o deck do grupo, o PDF renderizado em `qa_render/` (`curto_slide01` a `13` e `grade_curto.png`) e os testes
rodados: `test_deck_curto_banca2`, `test_conteudo_banca2` e `test_sintese_H2` passam, sem pulos.

## 4. Para o autor

1. **A hipótese no doc 07.** A auditoria 52 já trocou "dentro da sua região" por "entre vagas da mesma UF". O slide
   1 não usa nenhuma das duas formas.
2. **O que a banca pode perguntar sobre o slide 12.** Em 0,300, cerca de um terço do salto de −3,7 para +5,4 (3,3 de 9,1 p.p.) é amostra. A
   leitura "anda junto com a UF" fica apoiada sobretudo na HI-2 (−1,15 → −0,62 na mesma amostra) e no pareamento.
