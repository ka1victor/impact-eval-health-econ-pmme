# 56. Revisão do deck da banca 2 na versão de 28/10/2026 (bolsa → 1ª opção, mesma UF; 11 slides)

> **Data:** 09/11/2026.<br>
> **Objeto:** `output/apresentacao_banca2/deck_banca2_curto.pptx` e `.pdf` no commit `2fe85cd` (SHA-256 do PDF
> começa por `49cfa1a07fcbca39`, igual ao manifesto); o doc 04 (fonte da verdade), o roteiro 09, o mapa 10 (§6) e o
> README da banca 2; as saídas `output/rdd_bolsa/VL_*`, `VG_*` e `VK_*`.<br>
> **Por que esta revisão:** a auditoria 55 aprovou a versão de 27/10 (hipótese bolsa × origem, com apêndice). A versão
> de 28/10, reescrita no dia da banca pela decisão do autor ("a hipótese é simplesmente sobre o efeito bolsa → 1ª
> opção", tudo dentro da mesma UF), e as figuras com os adendos 52g e 52h não tinham revisão.<br>
> **Método:** PDF renderizado em PNG (100 dpi) e lido slide a slide; texto comparado com o doc 04; números da tela
> conferidos contra `VL_estimativas.csv`, `VG_estimativas.csv` e `VK_estimativas.csv`; funil do slide 2 somado à mão;
> hashes do `.pptx` e do `.pdf` conferidos contra o manifesto; `python3 -m unittest tests.test_conteudo_banca2
> tests.test_deck_curto_banca2` rodado (98 testes, OK, 2 pulados por falta do deck do grupo, `PMME_DECK_GRUPO`).<br>
> **Estatuto:** revisão, não auditoria independente dos adendos 52g e 52h. Nada foi reestimado, nada foi gravado em
> `data/` nem em `output/`, e o deck **não** foi alterado: o gerador precisa do deck do grupo como template, que não
> está no repositório, e as mudanças de texto propostas abaixo dependem do autor.

## Veredito

**Números corretos; três pontos de substância e três de redação para o autor decidir.** Nenhum número da tela
diverge da saída de origem. O deck está em sincronia com o doc 04 (testes) e o PDF corresponde ao `.pptx` do
manifesto. Os problemas são de enquadramento: o slide de identificação não diz como a bolsa é separada do IVS; a
conclusão diz "Sim" sem a qualificação que o próprio deck dá nas limitações; e a robustez mostra resultados ainda
sem auditoria, com uma linha ("por degrau") que o score bootstrap não sustenta inteira.

Se esta é a versão apresentada em 28/10 (e em 04/11), qualquer correção vai para uma versão nova; antes de regerar,
copiar o PDF atual para `output/apresentacao_banca2/versoes/deck_banca2_curto_2fe85cd.pdf`, como foi feito com o
`8901dea`.

## 1. O que confere

| Item | Conferência |
|---|---|
| Slide 2, funil | 993 + 2.140 + 2.581 = 5.714; cada etapa = anterior − saídas (55, 77, 69; 20, 30, 38; 3, 1, 0); 5.421 no modelo |
| Slide 5 | 52,5% das vagas e 60,8% das 1ªs opções; 1.568 candidatos; rótulo "descritivo, sem teste" na tela |
| Slide 8 | VL-1 ciclos 1–3: 1,470 [1,146; 1,887], p 0,0025; ciclo 2: 1,904 [1,303; 2,783] |
| Slide 9 | log da distância 1,455 [1,154; 1,834]; região × UF 1,488 [1,152; 1,921]; VL-2 1,280 [0,951; 1,721]; VL-3 sobre VL-2 1,278 [0,953; 1,713]; degraus 1,412 [1,032; 1,932] e 1,519 [1,158; 1,993]; ciclos 1 e 3: 1,148 [0,656; 2,009] e 1,248 [0,900; 1,729] |
| Score bootstrap citado na fala | VL-1 ciclos 1–3, p Rademacher 0,01125 (fala: 0,011); ciclo 2, 0,0035 |
| Regra | slide 3 e 7: 368/368 e 454/454 (ciclos 1 e 2); 404/404 do escore do MS nas notas |
| Cautelas | "formulada após ver os dados", "pós-resultado", "pré-registrado, sem fixar a UF: IC contém 1", "pacote do corte", "y = opção marcada, não ida ao município" estão na tela |

## 2. Achados

### Substância

| # | Slide | Achado | Proposta (texto da tela) |
|---|---|---|---|
| S1 | 7 (Identificação) | A bolsa é função exata do IVS; o que a separa do IVS no VL-1 é a **spline contínua do IVS**, com o peso da bolsa vindo só dos saltos nos cortes (doc 57x, §7; nota do slide 6). A tela diz "Mantido fixo: candidato, par de UFs, distância" e não menciona o IVS. É a primeira pergunta provável da banca ("se a bolsa é função do IVS, como vocês separam um do outro?"). Além disso, o VL-1 usa todas as vagas da UF, não só as perto do corte: a identificação depende da forma funcional global do IVS. | linha "Mantido fixo" → `IVS (curva contínua), par de UFs, distância` (o candidato já está no slide 6: "candidato consigo mesmo"); na fala: "a curva do IVS é contínua; só o salto da bolsa nos cortes identifica o peso dela" |
| S2 | 9 e 10 | No adendo 52e, o VL-2 (só vagas perto do corte, a versão "RDD dentro da escolha") era **principal**, na família de Holm com o VL-1. No deck ele aparece na Robustez, e é inconclusivo: 1,28 [0,95; 1,72], Holm 0,103. A Conclusão (slide 10) responde "Sim" no título e "sim, comparando vagas da mesma UF" na primeira linha, enquanto o slide 11 diz "Pós-resultado → exploratório" e a comparação local não detecta efeito. O "aumenta" do título também é linguagem causal para um contraste que mede o pacote do corte. | Resposta → `sim, mas exploratório: ×1,47 na mesma UF; perto do corte, inconclusivo`; se o título continuar "Sim", ao menos a primeira linha precisa trazer "exploratório" |
| S3 | 9 | Os resultados por ciclo (adendo 52g) e por degrau (adendo 52h) estão na tela com "auditoria pendente". E a linha "Mantém: … por degrau; score bootstrap" junta duas coisas que não se mantêm juntas: no degrau 0,300 (ciclos 1–3) o score bootstrap dá p 0,064 (`VK_estimativas.csv`), o que as notas dizem, mas a tela não. | auditar 52g e 52h antes de reusar o slide na banca final; na tela, `Mantém: log da distância; região × UF; score bootstrap.` e `Por degrau: os dois acima de 1; em 0,300, o score não confirma.` |

### Redação

| # | Slide | Achado | Proposta |
|---|---|---|---|
| R1 | 8 | "por +R$ 5 mil, o médico **aceita** vaga 75 km mais longe" contradiz a cautela do slide 2 ("y = opção marcada, não ida ao município") e o ajuste de 28/10 (doc 10, §6.7): o modelo mede a ordem das opções na inscrição, não aceitação. | `Leitura: +R$ 5 mil pesam como 75 km a menos na escolha.` (a mesma frase das notas). O teste `tests/test_deck_curto_banca2.py` fixa a frase atual e muda junto. |
| R2 | 6 | "Teste: β > zero", mas o p relatado (57x, §4.1) é bilateral, de H0: β = 0. | `Teste: H0 β = 0; cluster por conjunto` |
| R3 | 6 | A equação está em texto corrido: "P(j) = e^Uj/Σe^U". | `P(j) = exp(U_j) / Σ_k exp(U_k)` |

### Documentação

| # | Onde | Achado | Estado |
|---|---|---|---|
| D1 | README da banca 2 e `docs/07_apresentacoes/README.md` | Os quadros do topo ainda descreviam a hipótese bolsa × origem, o "teste central" e um apêndice de 2 slides, todos retirados em 28/10. | **corrigido neste commit** (quadro de estado no topo; quadros antigos ficam como registro) |
| D2 | `manifesto_deck_banca2_curto.json` | Os campos `pedido`, `regra` e `numeracao_das_hipoteses` (constantes do gerador) ainda falam de "corpo com só a H2" e "apêndice curto". | corrigir no gerador na próxima regeração |
| D3 | Notas do slide 10 (doc 04) | "Próximos passos: a auditoria do adendo 52g" omite o 52h. | corrigir junto com S1–S3 e R1–R3, para doc 04 e deck não divergirem |
| D4 | Deck | Sem capa (decisão: sem slides do grupo). Se o PDF circular sozinho, não tem título, autores nem data. | decisão do autor |

## 3. O que não muda

A hipótese, a escolha do VL-1 como resultado principal, a retirada do preenchimento e da origem são decisões do
autor de 28/10 e não foram tocadas. As propostas acima mantêm o limite de 30 palavras por slide e de 58 caracteres no
título, mas a contagem final é do gerador.

## 4. Para aplicar

1. Autor decide S1–S3 e R1–R3.
2. Copiar o PDF atual para `versoes/deck_banca2_curto_2fe85cd.pdf`.
3. Editar o doc 04 (tela, roteiro e notas), o doc 09 e o doc 10 (§6), e as frases fixadas em
   `tests/test_deck_curto_banca2.py`.
4. `PMME_DECK_GRUPO="<deck do grupo>" python3 scripts/apresentacao/gerar_deck_banca2.py` e os testes.
