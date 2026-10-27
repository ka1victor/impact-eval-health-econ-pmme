# 49. Auditoria do deck curto da banca 2 e dos documentos de conteúdo

> **Data:** 27/10/2026, véspera da banca 2 (parte empírica).<br>
> **Objeto:** `output/apresentacao_banca2/deck_banca2_curto.pptx` e `.pdf` (14 slides, notas incluídas); os geradores
> `scripts/apresentacao/gerar_deck_banca2.py` e `gerar_figuras_banca2.py`; as figuras `curto_*.png` e as do pipeline
> usadas no deck; os manifestos `manifesto_deck_banca2_curto.json`, `manifesto_figuras.json` e `numeros_banca2.json`;
> os docs da banca 2 [03](../07_apresentacoes/banca2/03_proveniencia_figuras_e_numeros.md),
> [04](../07_apresentacoes/banca2/04_conteudo_deck_curto.md),
> [05](../07_apresentacoes/banca2/05_discussao_historia_empirica.md),
> [06](../07_apresentacoes/banca2/06_estrutura_obrigatoria_versao_final.md) e
> [README](../07_apresentacoes/banca2/README.md); e o
> [doc 63](../06_execucao/63_registro_explicacoes_e_controles_H1.md). Base: branch `claude/vigilant-mccarthy-dd92mc`,
> commit `7e9f881` (igual à `main`).<br>
> **Referências (fonte da verdade):** saídas de `output/rdd_bolsa/`; docs 57n a 57x; doc 65 (§1.4 e §4.8);
> auditorias 31 a 48.<br>
> **Método:**
> - texto e notas lidos do `.pptx` com python-pptx; slides vistos no PDF renderizado em PNG;
> - cada código numérico do deck relido da fonte com leitura própria (pandas e json, sem importar os geradores) e
>   comparado com o valor exibido; as contagens descritivas recalculadas do parquet de células;
> - as 29 linhas numéricas das três figuras novas do deck (`h1_controle.png`, `curto_h1_por_ciclo.png`,
>   `curto_h1_parecidos.png`) conferidas contra a fonte;
> - os números das figuras do pipeline usadas sem redesenho (`HI_scatter_imediatas.png`, `HI_principal.png`)
>   conferidos a olho contra `HI_estimativas.csv` e `HI_resumo.json`;
> - SHA-256 do pacote, do PDF, do doc 04, do registro, das seis figuras e do deck do grupo conferidos contra
>   `manifesto_deck_banca2_curto.json`: todos iguais;
> - afirmações comparadas com o resultado auditado mais recente.<br>
> **Mudança de escopo (27/10/2026, a meio da auditoria):** o coordenador informou que o autor decidiu trocar a
> hipótese e que outro agente vai reconstruir o deck. Por isso esta auditoria é só **relatório** para o deck atual: o
> gerador, as figuras, `output/apresentacao_banca2/` e os docs 03, 04 e 06 **não** foram editados, e o deck não foi
> gerado de novo. Os achados abaixo ficam para o deck novo corrigir. As correções feitas aqui são de erro factual, só
> nos docs 05 e 63.

## Veredito

**Aprovado com correções.**

**Os números conferem com a fonte.** As 190 citações de número do deck (código × slide, no corpo, nas tabelas e nas
notas) batem com a fonte declarada (tabela da seção 4). As 29 linhas das figuras novas também batem. Nada é lido de `data/`, e o
arquivo `data/ivs_ipea_2010_municipios.csv` não aparece nos geradores da banca 2. Os hashes do manifesto conferem. Os
testes passam: 92 de 92 com o deck do grupo e 90 com 2 pulados sem ele.

**O problema está em afirmações vencidas.**
- A **H2** do ciclo 2 ainda usa o quadro de 19/03. As notas dizem "reestimação em curso", e a reestimação já foi
  feita (A2).
- A **explicação do sinal** da H1 não traz o resultado que mais pesa nas auditorias recentes: com a UF controlada,
  a queda em 0,300 deixa de se distinguir de zero (A1).
- Algumas frases tratam ausência de diferença detectada como ausência de efeito (A4).

Nenhum desses pontos fabrica um efeito. Todos, porém, mudam o que a banca ouve. Se o deck atual for apresentado,
A1, A2 e A4 precisam ser corrigidos antes. Como o deck vai ser reconstruído, os achados valem como lista de
correção para o deck novo.

## 1. Achados no deck

### Gravidade alta

**A1. A explicação do sinal negativo está desatualizada: falta a UF.**
- **Onde:** slide 12 ("Por que o sinal sai negativo"), notas dos slides 11 e 14, cabeçalho do doc 04, §6.8 do doc 03.
- **O que o deck diz:**
  - a tela dá quatro explicações: reta, vagas, porte e incentivo;
  - as notas do slide 11 resumem o adendo 48c como "a capital sozinha explica pouco": com a dummy de capital, 73% do
    salto da HI-2 fica.
- **Por que é seletivo:**
  - na mesma tabela do 48c (doc 57o, §4), com efeito fixo de UF a HI-2 em 0,300 vai de −1,13 [−2,15; −0,10] a
    −0,32 [−1,31; +0,66], 29% do ponto;
  - sem as capitais, vai a −0,30 [−1,22; +0,62];
  - a HI-1 muda de sinal (+4,0 e +2,9 p.p.);
  - a leitura pré-registrada do 48c é "anda junto com capitais (ou região)" (auditoria 42).
- **O que o 48h acrescenta** (doc 57w; auditoria 47, achado do PH-4), na mesma amostra:
  - sem controle: −1,15;
  - só o raio de especialistas: −1,19;
  - só a UF: −0,55 [−1,61; +0,50];
  - os dois: −0,62 [−1,67; +0,43].
- **Leitura do doc 65, §4.8:** "de onde vinha a queda em 0,300: da UF".
- **O que o deck novo deve dizer:** o sinal some com UF (48c, 48d e 48h). É robustez pós-resultado e limite da RDD
  em 0,300, não prova de mecanismo.
- **Também a corrigir:** a frase do slide 14 ("puxada por poucos municípios") e a das notas do slide 11.

**A2. A H2 do ciclo 2 usa o quadro de 19/03, e as notas dizem que a reestimação está em curso.**
- **Onde:** slide 13.
- **O que o deck diz:** a tela mostra "2,34 · 1,31 · 2,37 (ciclos 1–3)", e as notas dizem: "Reestimação em curso
  (52c): o ciclo 2 será refeito com o tipo de vaga do quadro de 13/02/2026; até lá, valem estes números."
- **Por que está errado:** o adendo 52c rodou em 26/10 (doc 57p, auditoria 41), e o 57p diz que a versão corrigida é
  a de referência. Os números a trocar (`VC_estimativas.csv`, versão `corrigida_13fev`):

  | Número | No deck (19/03) | Corrigido (13/02) |
  |---|---|---|
  | D_UF do M5 no ciclo 2 | 1,31 | 1,19 [0,51; 1,86] |
  | D_UF com os ciclos juntos | 1,98 [1,56; 2,40] | 1,94 [1,48; 2,40] |
  | peso de toda a bolsa | 0,42 | 0,45 (10 × 0,0453) |
  | mesma UF | 2,40 | 2,40 |
  | ciclos 1 e 3 | — | não mudam |

- **O que não muda:** a leitura (D_UF > 0 nos três ciclos).
- **Onde mais está:** o texto vencido também está no doc 04 (cabeçalho, linhas 57–58, e notas da H2) e é exigido por
  dois testes: `test_h2_reestimacao_52c_so_nas_notas` e `test_planos_b` (que lê `H3_S_M5C*` de
  `P1h_magnitudes.csv`).
- **Viola** a regra "quadro do ciclo 2 de 13/02".

### Gravidade média

**A3. O slide 10 tira a conclusão "a queda em 0,300 vem do ciclo 2" das medidas antigas, não da principal.**
- **O que o slide usa:** A3, com o tipo de vaga do quadro de 19/03, e a taxa por vaga oferecida. A cautela da tela
  avisa disso.
- **O que diz a especificação principal** (HI-s1, quadro de 13/02, doc 57n, §4; `HI_figuras/HI_por_ciclo.png`):

  | Linha em 0,300 | Ciclo 1 | Ciclo 2 | Ciclo 3 |
  |---|---|---|---|
  | HI-1 (p.p.) | +0,8 | −21,0 | +7,2 |
  | HI-2 (médicos) | −1,07 | −0,97 | −1,33 |

  Todos os IC contêm zero. A queda da HI-1 vem do ciclo 2. A da HI-2, a única com IC sem zero no empilhado, não vem:
  ela aparece nos três ciclos.
- **Recomendação:** usar a HI-s1 no deck novo e reescrever o título.

**A4. Algumas frases tratam "não detectado" como "não muda" (inconclusivo não é efeito zero).**
- **Slide 9:** "0,300: a oferta não muda; cai o preenchimento por vaga".
  - "Não muda" vem de um salto de +0,39 [−6,69; +7,46].
  - "Cai" vem do N1 com controle, −1,45 [−2,67; −0,22]: medida antiga, sem correção múltipla. Com efeito fixo de UF,
    ele vai a −0,46 [−1,34; +0,42] (doc 57o, C-5).
- **Slide 13:** "oferta igual" e "outros ficam".
  - O protocolo 64 não detecta diferença.
  - Para os outros especialistas, B3 em 0,300 é −4,75 [−19,26; +9,76], que não descarta saída relevante.
- **Slide 14:** o título "por que não sobe?" e as notas ("o preenchimento não sobe no corte") afirmam ausência de
  efeito.
  - O TOST só descarta aumento ≥ 25% na HI-2 em 0,300, com IC convencional.
  - A HI-1 é inconclusiva nos dois cortes.
  - O doc 65 classifica a H1 como inconclusiva, não como nulo.
- **Doc 04:** o cabeçalho diz "a oferta local muda igual dos dois lados".
- **Sugestão de redação:** "não se detecta diferença" ou "não detectamos aumento".

**A5. O slide 7 resume o balanço como "passam, salvo capitais", o que é menos do que os adendos mostram.**
- **Em 0,300**, na amostra da HI-2, saltam no corte:
  - a parte de capitais, −29,9 p.p.;
  - a do Nordeste, −47,7 p.p.;
  - os especialistas no resto da região, +10,54 por 10 mil hab. (48d).
- **Em 0,400:** os especialistas no resto da região, +6,21.
- **Só com vagas imediatas:** 3 covariáveis saltam, contra 1 na amostra toda (48f).
- **Onde está dito:** as notas dizem tudo isso; a tela, não.
- **Sugestão:** "passam, salvo localização e médicos na região em 0,300".

**A6. O rótulo "Vagas" do slide 12 se apoia no quadro de 19/03.**
- **O que o deck diz:** "diferentes do lado de cima"; nas notas, "do lado de cima há mais vagas de cadastro reserva".
- **O que mudou** (doc 57t; auditoria 44): o +15,4 p.p. [+2,1; +28,6] da parte só de reserva é do quadro de 19/03.
  - Com o de 13/02, é +14,0 [−0,2; +28,3].
  - Com efeitos fixos de curso × ciclo, +4,3 [−7,5; +16,1].
- **Consequência:** a parte de "mais reserva" deixa de se distinguir de zero com o quadro anterior à alocação.

**A7. Resultados auditados que o deck não traz** (pendência, não erro; o deck foi feito antes deles):
- **48g** (estrato do IED; doc 57u; auditoria 45).
  - Não se detecta que o salto dependa de o estrato mudar: diferença τ₁ na HI-2 em 0,300 de +1,67
    [−0,27; +3,60], Holm 0,366.
  - O IED não explica o sinal, com pouca potência.
  - O canal **não** fica descartado (auditoria 45).
  - O grupo "não muda" de 0,300 junta as capitais.
- **48h** (UF e raio; doc 57w; auditoria 47).
  - Pareado: nenhuma diferença nos dois cortes, com 25 e 29 pares.
  - Com a reta: a HI-2 em 0,300 vai a −0,62 [−1,67; +0,43].
  - Ver A1.
- **52d** (sensibilidades do ciclo 2 com 13/02; doc 57v; auditoria 46). A robustez do ciclo 2 se mantém no conjunto só
  com vaga imediata.
- **52e** (H2 com efeito fixo do par de UFs; doc 57x; auditoria 48).
  - Comparando vagas da mesma UF, a razão de chances por +R$ 5 mil é 1,47 [1,15; 1,89], p de Holm 0,005, maior que a
    do M1 (diferença pareada que exclui zero).
  - No ciclo 2, 1,90.
  - Perto do corte, 1,28 [0,95; 1,72].
  - Isso mexe no enunciado da H2 ("a bolsa pesa pouco"); a decisão é do autor (seção 3).
- **Janelas e IC honesto** (doc 57n, HI-s8; doc 65, §1.4).
  - A única linha com IC sem zero (HI-2 em 0,300) passa a conter zero com h = 0,030 e com h = 0,080.
  - O IC honesto dela é [−39,0; +36,8].
  - O deck menciona só o IC convencional, e só nas notas.

### Gravidade baixa

**A8. A figura do slide 4 (regra *sharp*) não tem "Como ler".** A regra do autor pede "Como ler" em toda figura.
Também não diz quais municípios são os pontos.

**A9. O "descarta aumento ≥ 25%" do slide 8 vale só com IC convencional.** Com o IC honesto, o TOST é inconclusivo
(`HI_estimativas.csv`, `TOST_honesto`). As notas dizem "no IC convencional"; a tela, não.

**A10. A cronologia omite a retificação de 13/02 do quadro do ciclo 2.** A cronologia (`cronologia_ciclos.csv`; notas
do slide 3) dá "03/02/2026 (retificado em 19/03/2026)". O quadro que a H1 e a H2 corrigida usam é o de 13/02
(auditoria 36).

**A11. "Preenchidas" no slide 3 tem definição diferente da H1 no ciclo 1.**
- No slide 3, o ciclo 1 conta confirmação ou homologação: 30,3%.
- Na H1, conta ≥ 1 alocado: 29,9% (recalculado do parquet).
- A diferença está explicada só nas notas.

**A12. Forma.**
- **Slides:** 14, nas oito seções e na ordem certa. O rodapé marca a seção ativa.
- **Palavras:** pela regra do doc 06 (só trechos com letra ou algarismo), todos os slides ficam em até 30 palavras.
  Contando também `=`, `+` e `×`, o slide 6 chega a 37; vale a regra do doc 06.
- **Cinza dos planos B:** rótulos `A3A39E` e caixas `F2F2F0`, nos slides 1, 6 e 13.
- **Efeitos:** sempre por corte; nada empilha os cortes no corpo.
- **Logo:** nenhum título passa por baixo dele.
- **Texto cortado:** nenhum no PDF.
- **Fora da área do slide:** o número de página e a caixa de navegação passam um pouco da borda (0,02 cm e 0,08 cm).
  Vem do *template* e não é visível.

**A13. Lugar do slide 12 na Discussão.**
- O slide 12 é diagnóstico pós-resultado e fica na Discussão. O doc 06 reserva a Discussão para a "explicação simples
  em termos da teoria".
- O doc 65, §1.5, avisa do risco de explicar um sinal que não passa no Holm e muda de sinal na robustez.
- Recomendação: levar o slide para a Robustez, ou reduzi-lo a "o sinal some com UF".

## 2. Achados nos documentos

**D1. Doc 05: corrigido nesta auditoria (erros factuais).**

*Cabeçalho*
- Dizia que o doc não traz número de resultado; as seções 2.11 a 2.14 trazem. Todos foram conferidos (ver D8).
- O retrato "estado do branch em 26/10" estava vencido.

*Seções 2.1 e 2.3*
- A frase errada "nenhuma célula só de reserva foi preenchida na 1ª chamada", corrigida no 49b em 26/10, continuava
  no corpo, só com um aviso no topo.
- A §2.3 ligava o ciclo 2 ao cadastro reserva. Agora diz que, na HI-s1, a HI-2 cai nos três ciclos.

*Seção 2.9*
- Acrescentado o resultado do 52e: o peso da bolsa na escolha deixa de "encostar no zero" quando se compara dentro da
  mesma UF.

*Seções 2.11 e 2.12*
- "Falta a seleção pelo tipo de vaga" e o estado "aberto" do canal 2 estavam vencidos: o 48f foi feito.

*Seção 2.16*
- Razão *fuzzy*, item C: constava "a fazer"; foi feita no commit `515a559` (o doc 03, §6.9, já dizia isso, e o
  `OC_estimativas.csv` tem `tau` vazio com F < 10).
- Seleção pelo tipo de vaga, item D: constava "a fazer"; foi feita (48f).
- Heterogeneidade por porte: constava "aguardando decisão"; foi feita (48g). A redação é "não explica", não
  "descartado".
- Acrescentadas as linhas do 48h e do 52e.
- Na hipótese única, registrado que o coordenador informou a decisão do autor de trocar a hipótese. O conteúdo da
  decisão não está nos docs.

*Seção 4*
- Parte B (constava "estimando"), 48c e 52c (constavam "congelados") e "slides da história".

*Seção 4.1*
- Cabeçalho WIP vencido.
- Item 2: a fonte do IBGE já está arquivada (a19).
- Item 5: as covariáveis pré-determinadas foram em parte feitas (48c, 48d, 48h).
- Item 7: o 48g foi feito.

**D2. Doc 63: corrigido nesta auditoria.**
- A coluna "Estado" das explicações 1, 2, 3, 8, 11 e 14 dizia "em teste formal", "a incluir", "proposto" ou
  "aberto". Os adendos 48c, 48d, 48f, 48g e 48h já rodaram e foram auditados.
- Na explicação 14, o +15,4 p.p. ganhou a ressalva do quadro de 19/03.
- Nota datada no fim: pelo doc 65, §4.8, a explicação com mais apoio é a UF.

**D3. Doc 04, não editado (fora do escopo depois da mudança).** Correções para o deck novo:
- **Cabeçalho, linhas 36–40:** "A queda em 0,300 é explicada pela reta levada até o corte, puxada por poucos
  municípios". Falta a UF, e "é explicada" é forte demais.
- **Linhas 47–48:** "73% do salto da HI-2 fica", sem a linha da UF (A1).
- **Linhas 53–56:** "a oferta local muda igual dos dois lados" (A4).
- **Linhas 57–58 e notas da H2:** "reestimação em curso (52c)" (A2).
- **Campo `atualizacao`:** ainda é 26/10.

**D4. Doc 03, não editado.**
- **§6.8:** repete o "73% fica" sem a UF.
- **§6:** não registra como pendência que a H2 do ciclo 2 usa o quadro de 19/03, nem os adendos 48g, 48h, 52d e 52e.
- **Bloco gerado:** está igual ao JSON (teste `test_bloco_do_doc03_igual_ao_json`).

**D5. Doc 06, não editado.**
- **§3:** a linha da Identificação fala só da "ressalva das capitais"; deveria ser localização e médicos (A5).
- **§3, Discussão:** inclui o slide de diagnóstico (A13).
- **Estado:** a §3 é "versão de 26/10, a validar" e muda com a hipótese nova.
- **§1 e §2 (as regras):** o deck atual cumpre.

**D6. README da banca 2, não editado.** Pontos vencidos:
- "o slide está marcado 'aguardando 48b'";
- "A queda em 0,300 é explicada pelas capitais", forte demais e sem a UF;
- "doc 57m, em auditoria" (foi auditado: auditoria 37);
- "Em aberto com o autor: a hipótese central (H3 ou H1)";
- a lista das figuras do curto: `curto_dispersao_a3`, `curto_reta_0300` e `curto_tost` não entram mais; entram
  `h1_controle`, `curto_h1_por_ciclo`, `curto_h1_parecidos`, a regra e `HI_*`;
- a §6 com a numeração antiga (H3 e H4).

**D7. Coerência entre os docs.**
- Antes desta auditoria, o doc 03 (§6.9: razão *fuzzy* vazia) e o doc 05 (§2.16: "a fazer") se contradiziam.
  Corrigido no 05.
- O doc 63 e o doc 05, §4.1, discordavam do estado real dos adendos 48c a 48h. Corrigido nos dois.
- Fica a divergência entre o doc 04 e o doc 65, §4.8, sobre de onde vem o sinal (A1). Só o deck novo a resolve.

**D8. Números soltos que os testes não pegam.** Os testes conferem os números do deck (doc 04, dentro dos marcadores),
do doc 02, do 03, do README e do roteiro. Os docs 05, 06 e 63 ficam fora. Conferi um a um os números de resultado do
05 e do 63, e todos batem:

| Doc | Números | Fonte |
|---|---|---|
| 05, §2.11 | 630 vagas, 42% dos alocados | auditoria 36 |
| 05, §2.12 | +15,4 [+2,1; +28,6] e +11,3 | doc 57l |
| 05, §2.12 | +14,0 [−0,2; +28,3], +4,3, 66% e 53% | doc 57t (65,9% e 52,5%) |
| 05, §2.12 | 630, 301 e 297 | auditoria 36 |
| 05, §2.12 | −8,4 e −3,7 | docs 57n e 49 |
| 05, §2.13 | 1.397, +6,6, +8,7, −2,1 e 51,0% | doc 57d e `S57_resumo.json` |
| 05, §2.13 | 1.037 e 315 | doc 57k |
| 05, §2.14 | F 0,2 e 0,0 | `OC_estimativas.csv` |
| 63 | +15,4, +11,3, −8,4 → −3,7, 40% e 44% | docs 57l, 57n, 57m e auditoria 37 |

O doc 06 só traz parâmetros. O cabeçalho do 04, fora dos marcadores, traz "73%", que confere com
`HC_HI2_300_CAP_PCT`.

## 3. Recomendações que não são desta auditoria (conteúdo e hipótese: decisão do autor)

1. **Explicação do sinal da H1:** pôr a UF como explicação principal da queda em 0,300 (48c, C-3; 48h, PH-4), com o
   48g ("o IED não explica, com pouca potência"). Decidir se o slide "Por que o sinal sai negativo" fica.
2. **H2:** trocar os números pelos do quadro de 13/02 (52c). Decidir como o 52e entra: comparando dentro da mesma UF,
   a bolsa pesa mais e passa no Holm. Isso pede rever o enunciado "a bolsa pesa pouco perto da origem", ou deixar
   claro que D_UF > 0 continua (origem pesa mais que toda a bolsa) enquanto o peso da bolsa deixa de "encostar no
   zero".
3. **Por ciclo:** usar a HI-s1 (`HI_por_ciclo.png`) no lugar das medidas antigas.
4. **Robustez da HI-2 em 0,300:** mostrar que ela não aguenta a troca de janela (HI-s8) nem o IC honesto, além de
   não passar no Holm.
5. **Testes:** atualizar os testes que travam o texto vencido:
   - `test_h2_reestimacao_52c_so_nas_notas`;
   - `test_planos_b`, que exige `H3_S_M5C*` do P1h;
   - `test_discussao`, que exige "capitais e Nordeste logo abaixo do corte";
   - `LINHA_POR_CICLO` em `tests/test_deck_curto_banca2.py`.
6. **Hipótese:** registrar a decisão nova do autor no doc 05, §1 e §2.16, e no doc 06, antes de gerar o deck novo.

## 4. Tabela de conferência: slide × número × fonte

Leitura própria da fonte declarada em `numeros_banca2.json`. A coluna "Onde" diz se o valor aparece no corpo (tela e
tabelas) ou nas notas do `.pptx`. Os números das figuras novas estão na seção 5. Os slides 1, 2 e 14 não têm número
de resultado. "Desatualizado" quer dizer que o valor confere com a fonte citada, mas há versão corrigida auditada
(achado A2).

<!-- tabela gerada pela leitura própria; ver o método no cabeçalho -->
| Slide | Código | Valor no deck | Onde | Fonte | Confere |
|---|---|---|---|---|---|
| 3 | `D_C1_MUN` | 368 | corpo | `rdd_bolsa/outcomes/outcomes_V_celula.parquet` | sim (recalculado do parquet) |
| 3 | `D_C2_MUN` | 454 | corpo | `rdd_bolsa/outcomes/outcomes_V_celula.parquet` | sim (recalculado do parquet) |
| 3 | `D_C3_MUN` | 748 | corpo | `rdd_bolsa/outcomes/outcomes_V_celula.parquet` | sim (recalculado do parquet) |
| 3 | `D_C1_CEL` | 1.295 | corpo | `rdd_bolsa/outcomes/outcomes_V_celula.parquet` | sim (recalculado do parquet) |
| 3 | `D_C2_CEL` | 1.547 | corpo | `rdd_bolsa/outcomes/outcomes_V_celula.parquet` | sim (recalculado do parquet) |
| 3 | `D_C3_CEL` | 2.293 | corpo | `rdd_bolsa/outcomes/outcomes_V_celula.parquet` | sim (recalculado do parquet) |
| 3 | `D_C1_PRE1_PCT` | 30,3 | corpo | `rdd_bolsa/outcomes/outcomes_V_celula.parquet` | sim (recalculado do parquet) |
| 3 | `D_C2_PRE1_PCT` | 47,1 | corpo | `rdd_bolsa/outcomes/outcomes_V_celula.parquet` | sim (recalculado do parquet) |
| 3 | `D_C3_PRE1_PCT` | 21,7 | corpo | `rdd_bolsa/outcomes/outcomes_V_celula.parquet` | sim (recalculado do parquet) |
| 3 | `D_C1_P1` | 915 | notas | `rdd_bolsa/P1_resumo.json` | sim |
| 3 | `D_C2_P1` | 2.032 | notas | `rdd_bolsa/P1_resumo.json` | sim |
| 3 | `D_C3_P1` | 2.474 | notas | `rdd_bolsa/P1_resumo.json` | sim |
| 4 | `R_C1_REPR` | 368 | corpo | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 4 | `R_C1_MUN` | 368 | corpo | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 4 | `R_C2_REPR` | 454 | corpo | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 4 | `R_C2_MUN` | 454 | corpo | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 4 | `R_ESCORE_IGUAIS` | 404/404 | notas | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 4 | `R_C3_REPR` | 747 | notas | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 4 | `R_C3_MUN` | 748 | notas | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 5 | `HI1_300_TAU` | −3,7 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 5 | `HI1_300_INF` | −21,3 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 5 | `HI1_300_SUP` | +13,9 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 5 | `HI1_400_TAU` | −2,3 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 5 | `HI1_300_MEDIA` | 56,1 | notas | `rdd_bolsa/HI_estimativas.csv` | sim (fração × 100) |
| 5 | `GF_10_ORIG` | +11,9 | notas | `rdd_bolsa/GF_estimativas.csv` | sim |
| 5 | `GF_10_ORIG_INF` | +6,0 | notas | `rdd_bolsa/GF_estimativas.csv` | sim |
| 5 | `GF_10_ORIG_SUP` | +17,7 | notas | `rdd_bolsa/GF_estimativas.csv` | sim |
| 5 | `GF_10_UF` | +1,3 | notas | `rdd_bolsa/GF_estimativas.csv` | sim |
| 5 | `GF_10_NE_PRE` | 43 | notas | `rdd_bolsa/GF_estimativas.csv` | sim (fração × 100) |
| 6 | `M1_N` | 5.421 | notas | `rdd_bolsa/P1_estimativas.csv` | sim |
| 7 | `R_C1_REPR` | 368 | corpo | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 7 | `R_C1_MUN` | 368 | corpo | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 7 | `R_C2_REPR` | 454 | corpo | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 7 | `R_C2_MUN` | 454 | corpo | `rdd_bolsa/portao_r1_ivs_oficial.json` | sim |
| 7 | `E1_300_HOLM` | 0,707 | notas | `rdd_bolsa/E1_densidade_estimativas.csv` | sim |
| 7 | `E1_400_HOLM` | 0,658 | notas | `rdd_bolsa/E1_densidade_estimativas.csv` | sim |
| 7 | `A36_CAPMUN_TAU` | −17,8 | notas | `auditoria_H1/a36_estimativas.csv` | sim |
| 7 | `A36_CAPMUN_INF` | −34,1 | notas | `auditoria_H1/a36_estimativas.csv` | sim |
| 7 | `A36_CAPMUN_SUP` | −1,5 | notas | `auditoria_H1/a36_estimativas.csv` | sim |
| 7 | `SV3_Y1_300_LINF` | −7,4 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV3_Y1_300_LSUP` | +9,6 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV3_Y2_300_LINF` | −0,05 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV3_Y2_300_LSUP` | +0,12 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV3_Y1_400_LINF` | −13,0 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV3_Y1_400_LSUP` | +16,2 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV3_Y2_400_LINF` | −0,15 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV3_Y2_400_LSUP` | +0,16 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV5_Y2_300_LINF` | −0,19 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV5_Y2_300_LSUP` | −0,01 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV5_Y2_300_IMI` | −0,39 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV5_Y2_300_IMS` | +0,19 | notas | `rdd_bolsa/SV_estimativas.csv` | sim |
| 7 | `SV2_300_NS1` | 3 | notas | `rdd_bolsa/SV_resumo.json` | sim |
| 7 | `SV2_300_NTODA` | 1 | notas | `rdd_bolsa/SV_resumo.json` | sim |
| 8 | `HI1_300_TAU` | −3,7 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI1_300_INF` | −21,3 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI1_300_SUP` | +13,9 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI1_300_HOLM` | 1,000 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI1_400_TAU` | −2,3 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI1_400_INF` | −24,0 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI1_400_SUP` | +19,4 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI1_400_HOLM` | 1,000 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_300_TAU` | −1,13 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_300_INF` | −2,15 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_300_SUP` | −0,10 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_300_HOLM` | 0,126 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_400_TAU` | −0,16 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_400_INF` | −0,99 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_400_SUP` | +0,68 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_400_HOLM` | 1,000 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_300_MEDIA` | 2,77 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI_EQ1_300_I90I` | −18,4 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI_EQ1_300_I90S` | +11,1 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI_EQ1_400_I90I` | −20,5 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI_EQ1_400_I90S` | +15,9 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI_EQ2_300_I90I` | −1,99 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI_EQ2_300_I90S` | −0,26 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI_EQ2_300_MARG` | 0,69 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI_EQ2_400_MARG` | 0,50 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 8 | `HI2_300_P` | 0,032 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 9 | `VIC_400_TAU` | −3,59 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `N1_400_DTOT` | −1,36 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `N1_400_VIA` | −1,22 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `N1_400_DSA` | −0,14 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `N1_300_DTOT` | −1,56 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `N1_300_VIA` | −0,11 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `N1_300_DSA` | −1,45 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `VIC_300_TAU` | +0,39 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `A3_300_TAU` | −8,4 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 9 | `A3_300_INF` | −18,5 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 9 | `A3_300_SUP` | +1,7 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 9 | `HI1_300_TAU` | −3,7 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 9 | `N1_300_INF` | −2,67 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `N1_300_SUP` | −0,22 | notas | `rdd_bolsa/N_estimativas.csv` | sim |
| 9 | `HI2_300_TAU` | −1,13 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 10 | `PC_TX_2_300_TAU` | −27,8 | notas | `rdd_bolsa/ND_estimativas.csv` | sim |
| 10 | `PC_TX_2_300_INF` | −49,0 | notas | `rdd_bolsa/ND_estimativas.csv` | sim |
| 10 | `PC_TX_2_300_SUP` | −6,7 | notas | `rdd_bolsa/ND_estimativas.csv` | sim |
| 10 | `PC_TX_J_300_TAU` | −16,0 | notas | `rdd_bolsa/ND_estimativas.csv` | sim |
| 10 | `ND_TX300_C2_PCT` | 51 | notas | `razão/diferença de códigos registrados` | sim |
| 10 | `PC_A3_2_300_TAU` | −10,2 | notas | `rdd_bolsa/NA_estimativas.csv` | sim |
| 11 | `CL_HI1_300_SEM_TAU` | −4,1 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_300_SEM_INF` | −23,6 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_300_SEM_SUP` | +15,4 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_400_SEM_TAU` | +2,8 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_400_SEM_INF` | −20,3 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_400_SEM_SUP` | +25,8 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_300_LM_TAU` | +3,6 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_300_LM_INF` | −16,8 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_300_LM_SUP` | +23,9 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_400_LM_TAU` | −1,5 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_400_LM_INF` | −23,9 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI1_400_LM_SUP` | +20,9 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `PM_FRAC_300_TAU` | +4,7 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_FRAC_300_INF` | −6,5 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_FRAC_300_SUP` | +16,0 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_FRAC_300_NPAR` | 92 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_FRAC_400_TAU` | +5,5 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_FRAC_400_INF` | −9,7 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_FRAC_400_SUP` | +20,7 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_FRAC_400_NPAR` | 70 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_FRAC_300_HOLM` | 1,000 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `CL_PS1_300_TAU` | −0,6 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_PS1_300_INF` | −13,1 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_PS1_300_SUP` | +11,8 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_PS1_300_NPAR` | 86 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `HI1_300_TAU` | −3,7 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 11 | `HI1_400_TAU` | −2,3 | notas | `rdd_bolsa/HI_estimativas.csv` | sim |
| 11 | `CL_HI2_300_SEM_TAU` | −1,11 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI2_300_SEM_INF` | −2,17 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI2_300_SEM_SUP` | −0,05 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI2_300_LM_TAU` | −0,25 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI2_300_LM_INF` | −1,37 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `CL_HI2_300_LM_SUP` | +0,87 | notas | `rdd_bolsa/CL_estimativas.csv` | sim |
| 11 | `PM_ALOC_300_TAU` | +0,10 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_ALOC_300_INF` | −0,01 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_ALOC_300_SUP` | +0,22 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `PM_ALOC_300_HOLM` | 0,636 | notas | `rdd_bolsa/PM_estimativas.csv` | sim |
| 11 | `CL_BAL_CAP_300` | −29,9 | notas | `rdd_bolsa/CL_balanco.csv` | sim |
| 11 | `CL_BAL_NE_300` | −47,7 | notas | `rdd_bolsa/CL_balanco.csv` | sim |
| 11 | `CL_BAL_ESP_300` | +10,54 | notas | `rdd_bolsa/CL_balanco.csv` | sim |
| 11 | `CL_BAL_ESP_400` | +6,21 | notas | `rdd_bolsa/CL_balanco.csv` | sim |
| 11 | `HC_HI2_300_BASE` | −1,13 | notas | `rdd_bolsa/HC_estimativas.csv` | sim |
| 11 | `HC_HI2_300_CAP` | −0,83 | notas | `rdd_bolsa/HC_estimativas.csv` | sim |
| 11 | `HC_HI2_300_CAP_PCT` | 73 | notas | `razão/diferença de códigos registrados` | sim |
| 11 | `A36_CAP_ABX` | 13 | notas | `razão/diferença de códigos registrados` | sim |
| 11 | `A36_CAP_ACI` | 6 | notas | `razão/diferença de códigos registrados` | sim |
| 11 | `A36_CAPMUN_TAU` | −17,8 | notas | `auditoria_H1/a36_estimativas.csv` | sim |
| 11 | `A36_CAPMUN_INF` | −34,1 | notas | `auditoria_H1/a36_estimativas.csv` | sim |
| 11 | `A36_CAPMUN_SUP` | −1,5 | notas | `auditoria_H1/a36_estimativas.csv` | sim |
| 12 | `DQ_FUN_PRE_ABX` | 33,3 | notas | `rdd_bolsa/DQ_estimativas.csv` | sim (fração × 100) |
| 12 | `DQ_FUN_PRE_ACI` | 33,5 | notas | `rdd_bolsa/DQ_estimativas.csv` | sim (fração × 100) |
| 12 | `DQ_PPOSTO_Q1` | 0,250 | notas | `rdd_bolsa/DQ_estimativas.csv` | sim |
| 12 | `DQ_PCOMP_Q1` | 0,031 | notas | `rdd_bolsa/DQ_estimativas.csv` | sim |
| 13 | `H3_S_M5C1` | 2,34 | corpo+notas | `rdd_bolsa/P1h_magnitudes.csv` | sim |
| 13 | `H3_S_M5C2` | 1,31 | corpo+notas | `rdd_bolsa/P1h_magnitudes.csv` | sim com a fonte; **desatualizado**: quadro de 19/03 (achado A2) |
| 13 | `H3_S_M5C3` | 2,37 | corpo+notas | `rdd_bolsa/P1h_magnitudes.csv` | sim |
| 13 | `H3_DUF` | 1,98 | notas | `rdd_bolsa/P1h_magnitudes.csv` | sim com a fonte; **desatualizado**: quadro de 19/03 (achado A2) |
| 13 | `H3_DUF_INF` | 1,56 | notas | `rdd_bolsa/P1h_magnitudes.csv` | sim com a fonte; **desatualizado**: quadro de 19/03 (achado A2) |
| 13 | `H3_DUF_SUP` | 2,40 | notas | `rdd_bolsa/P1h_magnitudes.csv` | sim |
| 13 | `H3_10B` | 0,42 | notas | `rdd_bolsa/P1h_magnitudes.csv` | sim com a fonte; **desatualizado**: quadro de 19/03 (achado A2) |
| 13 | `H3_THETA` | 2,40 | notas | `rdd_bolsa/P1h_magnitudes.csv` | sim |
| 13 | `P4_HT_ATT` | +6,6 | corpo+notas | `rdd_bolsa/S57_resumo.json` | sim |
| 13 | `P4_HT_INF` | +5,4 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 13 | `P4_HT_SUP` | +7,8 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 13 | `P4_HM_ATT` | +8,7 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 13 | `P4_HF_ATT` | −2,1 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 13 | `P4_ORIGEM` | 51,0 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 13 | `P4_ORIGEM_INF` | 48,4 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 13 | `P4_ORIGEM_SUP` | 53,7 | notas | `rdd_bolsa/S57_resumo.json` | sim |
| 13 | `CA_HT_EST` | +7,91 | notas | `rdd_bolsa/CA_estimativas.csv` | sim |
| 13 | `CA_HT_INF` | −0,63 | notas | `rdd_bolsa/CA_estimativas.csv` | sim |
| 13 | `CA_HT_SUP` | +16,45 | notas | `rdd_bolsa/CA_estimativas.csv` | sim |
| 13 | `OC_B1_300_HOLM` | 1,000 | corpo+notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B1_400_HOLM` | 1,000 | corpo+notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B2_300_HOLM` | 1,000 | corpo+notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B2_400_HOLM` | 1,000 | corpo+notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B1_300_TAU` | −0,23 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B1_300_INF` | −1,51 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B1_300_SUP` | +1,05 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B1_400_TAU` | −0,46 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B1_400_INF` | −1,86 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B1_400_SUP` | +0,94 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B3_300_TAU` | −4,75 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B3_300_INF` | −19,26 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B3_300_SUP` | +9,76 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B3_400_TAU` | +0,37 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B3_400_INF` | −12,46 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_B3_400_SUP` | +13,20 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_F_300` | 0,2 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |
| 13 | `OC_F_400` | 0,0 | notas | `rdd_bolsa/OC_estimativas.csv` | sim |

## 5. Figuras novas do deck: linhas numéricas conferidas

Cada linha desenhada foi relida da fonte pelos códigos do `manifesto_figuras.json`. As figuras do pipeline usadas
sem redesenho (slides 5 e 8) foram conferidas a olho contra `HI_estimativas.csv` e `HI_resumo.json`:

- HI-1: −3,7 [−21,3; +13,9] e −2,3 [−24,0; +19,4], p de Holm 1,000;
- HI-2: −1,13 [−2,15; −0,10], Holm 0,126, e −0,16 [−0,99; +0,68], Holm 1,000;
- distância crua entre as retas: −15,6 e +11,3 p.p.

Todas conferem.

| Figura (slide) | Linha | Texto na figura | Confere |
|---|---|---|---|
| `h1_controle.png` (9) | Sem controle: efeito total: 0,300 | −1,56 [−3,73; +0,61] | sim |
| `h1_controle.png` (9) | Sem controle: efeito total: 0,400 | −1,36 [−3,30; +0,57] | sim |
| `h1_controle.png` (9) | Com controle: preenchimento: 0,300 | −1,45 [−2,67; −0,22] | sim |
| `h1_controle.png` (9) | Com controle: preenchimento: 0,400 | −0,14 [−0,82; +0,54] | sim |
| `h1_controle.png` (9) | Vagas oferecidas (o controle): 0,300 | +0,39 [−6,69; +7,46] | sim |
| `h1_controle.png` (9) | Vagas oferecidas (o controle): 0,400 | −3,59 [−8,94; +1,77] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,300 · Célula aberta preenchida (A3, p.p.): Ciclo 1 | +0,9 [−23,5; +25,3] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,300 · Célula aberta preenchida (A3, p.p.): Ciclo 2 | −10,2 [−23,4; +2,9] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,300 · Célula aberta preenchida (A3, p.p.): Ciclo 3 | −7,1 [−18,6; +4,3] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,300 · Célula aberta preenchida (A3, p.p.): Juntos | −8,4 [−18,5; +1,7] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,300 · Taxa por vaga oferecida (p.p.): Ciclo 1 | −12,5 [−34,4; +9,4] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,300 · Taxa por vaga oferecida (p.p.): Ciclo 2 | −27,8 [−49,0; −6,7] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,300 · Taxa por vaga oferecida (p.p.): Ciclo 3 | −10,7 [−24,1; +2,6] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,300 · Taxa por vaga oferecida (p.p.): Juntos | −16,0 [−27,9; −4,1] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,400 · Célula aberta preenchida (A3, p.p.): Ciclo 1 | −12,4 [−37,5; +12,6] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,400 · Célula aberta preenchida (A3, p.p.): Ciclo 2 | +2,2 [−24,7; +29,2] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,400 · Célula aberta preenchida (A3, p.p.): Ciclo 3 | −4,3 [−12,8; +4,2] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,400 · Célula aberta preenchida (A3, p.p.): Juntos | −1,3 [−14,0; +11,3] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,400 · Taxa por vaga oferecida (p.p.): Ciclo 1 | +3,6 [−22,9; +30,1] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,400 · Taxa por vaga oferecida (p.p.): Ciclo 2 | +9,5 [−15,8; +34,8] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,400 · Taxa por vaga oferecida (p.p.): Ciclo 3 | −1,9 [−15,6; +11,8] | sim |
| `curto_h1_por_ciclo.png` (10) | 0,400 · Taxa por vaga oferecida (p.p.): Juntos | +2,5 [−9,9; +15,0] | sim |
| `curto_h1_parecidos.png` (11) | 0,300 · Sem controle (RDD) | −4,1 [−23,6; +15,4] | sim |
| `curto_h1_parecidos.png` (11) | 0,300 · + localização e médicos | +3,6 [−16,8; +23,9] | sim |
| `curto_h1_parecidos.png` (11) | 0,300 · Pareados: regra literal | +4,7 [−6,5; +16,0] | sim |
| `curto_h1_parecidos.png` (11) | 0,300 · Pareados: regra do 48d | −0,6 [−13,1; +11,8] | sim |
| `curto_h1_parecidos.png` (11) | 0,400 · Sem controle (RDD) | +2,8 [−20,3; +25,8] | sim |
| `curto_h1_parecidos.png` (11) | 0,400 · + localização e médicos | −1,5 [−23,9; +20,9] | sim |
| `curto_h1_parecidos.png` (11) | 0,400 · Pareados: regra literal | +5,5 [−9,7; +20,7] | sim |
