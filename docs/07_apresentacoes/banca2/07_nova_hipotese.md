# A nova hipótese da banca 2: o médico escolhe perto da origem; a bolsa muda **qual** vaga ele escolhe, mas pesa menos que a origem

> **Decisão do autor, 27/10/2026.** A versão final da banca 2 usa como hipótese única a antiga H2 (bolsa ×
> origem), reformulada abaixo. O resultado da antiga H1 (preenchimento no corte) entra como o **fato** que motiva a
> hipótese. A antiga H3 (oferta) sai do corpo e fica só nas notas.<br>
> **Atualização da decisão (27/10/2026):** "pode tirar todas as hipóteses além da H2, que agora é nosso foco.
> Deixa no apêndice, se quiser, mas bem rápido. Agora precisamos de uma análise clara e completa da hipótese 2."
> O corpo do deck tem **só a H2**. O fato da antiga H1 vira no máximo uma linha de motivação e vai para o apêndice,
> com a antiga H3, em no máximo 2 slides.<br>
> **Revisão de texto de 27/10/2026 (auditoria 50):** "não encheu" virou "não detectamos aumento"; o sinal negativo "encolhe com a UF", não "some"; o teste central da H2 é origem × bolsa.<br>
> **Revisão de redação (auditoria 52):** "dentro da região" virou "entre vagas da mesma UF" (o VL-1 compara vagas da mesma UF, vistas por médicos da mesma UF de origem); a leitura pela teoria passou a "sugere". A decisão do autor não muda.<br>
> **Base da decisão:** [doc 65](../../06_execucao/65_avaliacao_forca_hipoteses.md), seções 4.6 a 4.8 (avaliação por
> critérios, foco em interpretação simples e resultados com a localização controlada).<br>
> **Estatuto:** a hipótese foi formulada **depois** de ver os resultados da H1 e dos coeficientes do modelo de
> escolha. Isso é dito na apresentação. Nenhum número deste documento é novo: todos vêm de docs gerados por script
> e auditados, citados ao lado.

## 1. A hipótese, numa frase

**O médico especialista escolhe vagas perto de onde já trabalha. A bolsa maior muda qual vaga ele escolhe entre
vagas da mesma UF, mas pesa menos que a própria origem.** Isso é coerente com não termos detectado aumento do
preenchimento no corte, mas essa ligação é interpretação, não teste (auditoria 50).

## 2. A história, na ordem da apresentação

1. **O fato (antiga H1).** Onde a bolsa é R$ 5 mil maior, **não detectamos aumento** do preenchimento (o desenho
   só pegaria saltos grandes). O sinal negativo em 0,300 nunca passou no Holm e anda junto com a localização: com
   efeito fixo de UF o ponto cai à metade e deixa de se distinguir de zero; comparando municípios da mesma UF, fica
   positivo, também sem se distinguir de zero
   ([57n](../../06_execucao/57n_resultados_H1_vagas_imediatas.md); [57w](../../06_execucao/57w_resultados_pareamento_localizacao.md);
   auditorias 38 e 47).
2. **A pergunta.** Por que não detectamos efeito de um incentivo de R$ 5 mil por mês no preenchimento?
3. **A hipótese.** Porque o médico escolhe perto de onde já trabalha, e a bolsa pesa menos que a origem: ela
   reordena a escolha entre vagas da mesma UF (leitura sugerida pelos dados, não teste da ligação com o
   preenchimento).
4. **A evidência.**
   - **Descritiva:** a maioria dos candidatos põe a 1ª opção na mesma UF de onde já trabalhava, e a distância
     mediana é pequena (`exp_escolha_origem.png`, a partir de `G1_*`).
   - **A bolsa pesa entre vagas da mesma UF:** comparando só vagas da mesma UF, vistas por médicos da mesma UF de origem,
     a bolsa maior aumenta a chance de a vaga ser a 1ª opção, nos ciclos 1–3 e no ciclo 2. É um adendo
     pós-resultado; na especificação pré-registrada (sem fixar a UF), o peso da bolsa sozinho não passa no Holm
     ([57x](../../06_execucao/57x_resultados_escolha_localizacao_par.md); auditoria 48).
   - **Mas pesa menos que a origem:** ter a vaga na UF de origem pesa na escolha muito mais que toda a diferença
     de bolsa entre a menor e a maior faixa ([57i](../../06_execucao/57i_resultados_P1h_magnitudes.md);
     [57p](../../06_execucao/57p_escolha_vaga_imediata_c2.md); auditorias 31 e 41).
   - **Médico de longe:** em 0,300 não se detecta mais médico de outra UF do lado de bolsa maior; em 0,400 é
     **inconclusivo** (poucos pares, todos apontando para mais médicos de fora). Não dizer "não traz médico de longe"
     ([57w](../../06_execucao/57w_resultados_pareamento_localizacao.md), PH-5; auditoria 47).
5. **A teoria (modelo da banca 1).** O médico aceita a vaga se a bolsa compensa o custo do lugar. O custo que
   domina não é o do município (que a bolsa compensa), e sim o de sair da própria região. Um degrau de R$ 5 mil
   desloca a escolha entre vagas da mesma UF; os dados **sugerem** que ele não compensa esse custo (não testado diretamente). A leitura é a de um **incentivo limitado**, sempre sobre o pacote do corte.
   O **teste central da H2** é a comparação origem × toda a bolsa (D_UF > 0); o peso da bolsa dentro da mesma UF
   (52e) reforça que a escolha responde à bolsa, mas não testa a comparação com a origem (auditoria 50).

## 3. O que dá e o que não dá para afirmar

| Dá para afirmar | Não dá para afirmar |
|---|---|
| Entre quem se candidatou, a vaga de bolsa maior é preferida a uma vaga parecida da mesma UF | que a bolsa **causa** mais médicos no município |
| A origem pesa mais que toda a diferença de bolsa na escolha | que a origem **causa** a escolha: é preferência revelada |
| No corte, não se detecta aumento do preenchimento | que o efeito no preenchimento é zero: o desenho só pegaria efeitos grandes |
| O sinal negativo no corte nunca passou no Holm e anda junto com a localização | que a bolsa **reduz** o preenchimento |

O contraste da bolsa é sempre o **pacote do corte**: a bolsa mais as outras regras federais que mudam nos mesmos
cortes de IVS ([auditoria 18](../../auditorias/18_politicas_nos_mesmos_cortes_ivs.md)).

## 4. Ressalvas obrigatórias na fala

1. A hipótese foi formulada depois de ver os dados.
2. A origem é preferência revelada, não causa.
3. A bolsa desloca a escolha com força só no ciclo 2. Nos ciclos 1 e 3, os intervalos são largos.
4. A comparação só com vagas perto do corte é inconclusiva.

## 5. Os gráficos (simples)

| # | Gráfico | Mensagem |
|---|---|---|
| G-A | o fato: salto do preenchimento no corte, sem controle e comparando municípios da mesma UF | "não detectamos aumento; o negativo anda junto com a localização" |
| G-B | onde os candidatos escolhem (mesma UF, mesma região, mesmo município; distância) | "o médico escolhe perto de casa" |
| G-C | razão de chances da 1ª opção por +R$ 5 mil, comparando vagas da mesma UF, ciclos 1–3 e ciclo 2 | "entre vagas da mesma UF, a bolsa pesa" |
| G-D | peso da origem × peso de toda a bolsa | "mas a origem pesa mais" |

Todos gerados por `scripts/apresentacao/gerar_figuras_banca2.py`, a partir de `output/`.
