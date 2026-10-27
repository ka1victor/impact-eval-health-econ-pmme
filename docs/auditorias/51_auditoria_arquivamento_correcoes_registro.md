# 51. Auditoria de cinco peças que entraram na `main` sem auditoria: arquivamento do IBGE, formato *fuzzy* do OC, correção da reserva no ciclo 2, registro de mudanças e worktrees

> **Data:** 27/10/2026.<br>
> **Objeto:**
> 1. arquivamento da fonte do IBGE de capitais, UF e região (commit `9d77c2d`, merge `fcd4aeb`): script
>    `scripts/aquisicao/a19_arquivar_ibge_capitais_uf.py`, brutos em `data/raw/aquisicao/ibge_capitais_uf/`, manifesto
>    `output/aquisicao/a19_manifesto_arquivamento_ibge_capitais_uf.json` e `tests/test_arquivamento_ibge_capitais.py`;
> 2. formato da razão *fuzzy* do protocolo 64 (commit `515a559`, merge `0dd0c1f`): script 43,
>    `output/rdd_bolsa/OC_estimativas.csv`, doc 57q e teste;
> 3. correção do erro "reserva no ciclo 2" (commit `515a559`; nota do doc 49 reescrita em `7e9f881`): docs 49 §2,
>    49b e 57l e scripts 23b e 38;
> 4. `docs/00_registro_mudancas.md`, desde 24/10/2026;
> 5. worktrees que sobraram em `.claude/worktrees/` (só leitura).<br>
> **Base:** branch `claude/vigilant-mccarthy-dd92mc`. As peças 1 a 3 foram conferidas em `7e9f881`, como pedido. Durante
> a auditoria, a `main` (`origin/main`) e o branch andaram para `a6236fc` (docs 07 e 08 da banca 2, auditorias 49 e 50),
> sem tocar nas peças 1 a 3. O worktree foi avançado para `a6236fc` (fast-forward) antes das correções, para que
> registro e doc 05 não fiquem atrás da `main`. A referência local `main` está parada em `40a8c98`, 355 commits atrás;
> nesta auditoria, "main" é `origin/main`.<br>
> **Método:** leitor próprio do DBF (struct puro, sem `dbfread` nem pandas) e do SIDRA; comparação célula a célula do
> CSV antigo e do novo; diff das saídas no Git; busca em `docs/` com quebra de linha normalizada; para os worktrees,
> hash de blob de cada arquivo comparado com a árvore do HEAD, sem rodar git dentro deles. Nada foi reestimado.

## Veredito

| Peça | Veredito |
|---|---|
| 1. Arquivamento do IBGE | **Aprovado.** Hashes conferem; o CSV se reconstrói byte a byte com leitor próprio; `data/` só ganhou arquivos novos. |
| 2. Formato *fuzzy* do OC | **Aprovado.** As 132 linhas não *fuzzy* estão idênticas; `ar_p_beta0` = `p_valor` antigo nas 30 linhas; Holm e BKY idênticos. |
| 3. Reserva no ciclo 2 | **Aprovado com ressalvas.** O texto novo está certo e nenhuma estimativa mudou. Restam a frase congelada do adendo 48b §1 (presa por hash) e a falta de aviso de que o "sem as células só de CR" do ciclo 2 condiciona no resultado. |
| 4. Registro de mudanças | **Aprovado com correções de registro.** Corrigidos: a entrada duplicada (na verdade, três fragmentos de um retrato WIP), um arquivo sem entrada e sete entradas "pendente"/WIP já auditadas. |
| 5. Worktrees | **Inventário feito, nada apagado.** Não há trabalho útil abandonado fora da `main`, exceto o trabalho em curso de um agente ativo (`agent-ac0541a3256f2f9af`). |

## 1. Arquivamento da fonte do IBGE (capitais, UF, região)

**Hashes.** Os sete brutos de `data/raw/aquisicao/ibge_capitais_uf/` têm o SHA-256 dos dois manifestos:

| Bruto | Bytes | SHA-256 (início) | a19 | 41 |
|---|---|---|---|---|
| `Localidades_Brasil_shp.zip` | 4.511.488 | `1c0bec392891` | confere | `sha256_zip` confere |
| `sidra_4709_n2_all_v93_p2022.json` | 1.258 | `1f8a223cbb80` | confere | confere |
| `sidra_4709_n3_in_n2_{1..5}_v93_p2022.json` | 799 a 2.349 | `ddd8eb8d…`, `8d3d2d84…`, `a4fbebc8…`, `098fa2f1…`, `2bfedd4f…` | confere | confere |

O DBF extraído do ZIP tem o `sha256_dbf` do manifesto do 41 (`6c2a8dda7de6…`), com codificação UTF-8. O hash do
manifesto do 41 gravado no a19 (`d1b75dc54078…`) é o do arquivo atual.

**Reconstrução com leitor próprio.** Um leitor do DBF escrito do zero (cabeçalho e campos por `struct`, sem `dbfread`
nem pandas) lê as 96.163 localidades, sem registro apagado. O filtro `CT_LOCALID = Cidade` e `SCT_LOCALI` em Capital
Estadual / Capital Federal dá 26 + 1 = 27 capitais, uma por UF, cada uma com código de município dentro da própria
UF. As respostas do SIDRA dão as 5 Grandes Regiões e as 27 UFs, sem UF repetida, e o nome da UF no SIDRA é igual ao
do DBF nas 27. O CSV montado por esse leitor, sem pandas, é **igual byte a byte** a
`output/aquisicao/ibge_capitais_uf_regiao.csv` (SHA-256 `e4c9ffb63c0e…`, o do manifesto do 41). O
`--verificar` do a19, rodado de novo, também dá idêntico.

**Onde o script escreve.** Pela leitura do código, o a19 só grava em `data/raw/aquisicao/ibge_capitais_uf/` (brutos e
`.part` temporário, com substituição atômica) e em `output/aquisicao/` (manifesto). Arquivo existente com outros bytes
nunca é substituído; bruto com hash divergente vai para nome datado. O `--verificar`, que é o padrão, não grava nada.

**`data/` no Git.** De `c87ed75` (pai do commit do a19) até `a6236fc`, a única mudança em `data/` são os sete
arquivos **adicionados** (`A`) em `9d77c2d`. Nenhum arquivo preexistente de `data/` foi modificado ou removido desde
24/10/2026. As duas alterações em `data/` mais antigas no histórico (`628d788`, 19/10, manifesto de malhas do IBGE;
`1934626`, 18/10, remoção de uma portaria duplicada) estão fora do escopo desta peça.

**Achados**

- **A1 (baixo).** `capitais_do_zip` extrai o DBF (58 MB) para um `TemporaryDirectory` do sistema, fora dos dois
  diretórios permitidos. É escrita transitória, apagada ao sair, e não toca em `data/`. O teste "só escreve no bruto e
  em `output/aquisicao/`" olha só a pasta redirecionada e não vê essa extração. Sem correção necessária; se o autor
  quiser, o DBF pode ser lido em memória.
- **A2 (observação).** O `--baixar-referencias` do script 41 continua baixando em memória, sem arquivar. O caminho de
  arquivamento é o a19; uma nova rodada do 41 com rede não atualiza o bruto. O a19 fica fora do `run_all.py`, como os
  outros scripts de aquisição (a18).

Testes: `tests/test_arquivamento_ibge_capitais.py`, 9 de 9 passam.

## 2. Formato da razão *fuzzy* no protocolo 64

Comparei `git show 515a559^:output/rdd_bolsa/OC_estimativas.csv` com o atual (o arquivo não mudou depois de
`515a559`). As duas versões têm 162 linhas, na mesma ordem e com a mesma chave. O esquema novo só acrescenta
`ar_ilimitado` e `ar_p_beta0`.

| Conferência | Resultado |
|---|---|
| Linhas não *fuzzy* (132), colunas antigas | **0 células diferentes**; `ar_ilimitado` e `ar_p_beta0` vazios |
| Linhas `fuzzy_*` | 30, todas com F robusto < 10 (máximo 0,75) |
| `tau`, `ep`, `ic95_inf`, `ic95_sup`, `p_valor` nas 30 | vazios (`ep` e IC convencional já eram vazios antes) |
| `nota` nas 30 | começa com `instrumento_fraco_F<10` |
| `ar_ilimitado` | `True` nas 30; `ar_ic_inf`/`ar_ic_sup` vazios (antes: ±`ar_grade_L`, a borda da grade) |
| `ar_p_beta0` contra o `p_valor` antigo | **igual, como texto, nas 30** (diferença numérica 0) |
| `p_holm` e `q_bky` nas 162 linhas | **idênticos**; as 10 *fuzzy* do BKY usam `ar_p_beta0` por `p_familia()` |

Mudaram, nas linhas *fuzzy*, só `tau`, `p_valor`, `ar_ic_inf`, `ar_ic_sup` e `nota`, como o commit diz. As primárias
(família Holm, OC-A1 e OC-A2) e os primeiros estágios OC-B0 não mudaram. A mudança de hash de
`OC_estimativas.csv` está propagada: `OC_resumo.json`, `CL_resumo.json` e `PM_resumo.json` (os scripts 44 e 45 foram
rodados de novo em `8dfeb25`, estimativas idênticas), `PO_resumo.json`, `PL_resumo.json` e
`output/apresentacao_banca2/manifesto_figuras.json` citam o hash novo; nenhum arquivo cita o antigo. Os scripts 44 e 47
e o gerador de figuras da banca 2 só leem linhas `principal` e `primeiro_estagio`, que não mudaram.

O texto do 57q (§5.4, nota da tabela, cabeçalho e nota datada da §8) descreve a mudança corretamente. É a sugestão do
achado B1 da auditoria 39 ("`tau` vazio quando F < 10"), feita a pedido do autor. Sem achado.

Testes: `tests/test_oferta_local_corte.py`, 27 de 27 passam.

## 3. Correção do erro "reserva no ciclo 2"

**Texto novo contra a auditoria 36 e o adendo 48b §7.** A auditoria 36 (§1 e §3) mostra que:
- o quadro do ciclo 2 usado no pipeline (19/03/2026) foi refeito depois do resultado preliminar (10/03);
- a SGTES converteu 630 vagas de reserva em imediatas em 301 células, e 297 delas tiveram alocado;
- pelo quadro de 13/02/2026, 442 dos 1.057 alocados (42%) estavam em células só de reserva
  (`output/auditoria_H1/a36_resumo.json`, `ciclo2_versoes.final_contra_13fev`, conferido);
- os editais permitem preencher a reserva na 1ª chamada.

O 48b §7 diz o mesmo. As correções dizem isto, e nada além:
- doc 49 §2: nota datada; o zero vale só para o quadro de 19/03, e a linha do ciclo 2 não se lê como "a reserva não
  podia ser / não foi preenchida". A versão de `7e9f881` troca "442 dos 1.057 (42%)" por "uma parte grande", com
  a fonte; continua correta;
- 49b (resposta curta, pelo script 23b): o "0 alocados" fica restrito ao quadro de 19/03, com a correção;
- 57l (resposta curta, frase da banca, nota e §8, pelo script 38): idem, e a frase da banca perdeu a afirmação
  errada.

Nenhuma correção afirma o contrário do que a auditoria 36 sustenta.

**Estimativas.** De `515a559^` até `a6236fc`, `DQ_*`, `ND_*` (saídas do 23b), `N_*`, `NA_*` e `GF_estimativas.csv`
não mudaram. A última mudança deles é anterior a `515a559`. O único arquivo dessas famílias que mudou é
`GF_resumo.json`: duas linhas, o hash e o tamanho do script 38 que o 39 registra como entrada. O hash novo
(`04a19714a779…`, 154.450 bytes) é o do script 38 atual. Nenhum outro resumo cita o hash antigo do 38 ou do 23b.

**Busca em `docs/`.** A busca normaliza as quebras de linha, para pegar frase partida entre linhas. Fora de
`auditorias/`:
- em `7e9f881`, ainda havia a afirmação como fato no doc `07_apresentacoes/banca2/05_discussao_historia_empirica.md`
  (§2.1, "e nenhuma célula só de reserva foi preenchida na 1ª chamada", partida em duas linhas), que a busca por linha
  não acha. A auditoria 49 (`a6236fc`) a riscou e corrigiu;
- em `a6236fc`, toda ocorrência restante é citação da frase errada para dizer que está errada, frase restrita ao
  quadro de 19/03, ou riscada. **Única exceção:** o adendo congelado 48b, §1 e cabeçalho (achado C1).

**Achados**

- **C1 (baixo).** O 48b §1 ainda diz, como fato, "no ciclo 2, nenhuma célula só de reserva teve alocado na 1ª
  chamada", e o cabeçalho, "justificada pela regra de uso da reserva". A §7 do mesmo adendo corrige isso, mas o §1
  não aponta para a §7. O arquivo está preso por hash em `HI_resumo.json`, `HC_resumo.json` e
  `tests/test_h1_vagas_imediatas.py`: uma nota no §1 quebraria a conferência do adendo congelado. Por isso **não
  editei**. Recomendo que o autor decida entre (a) deixar como está, com a §7 e a auditoria 38 (achado 1) como
  registro, ou (b) acrescentar uma nota e rodar de novo os scripts 40 e 41 para regravar o hash.
- **C2 (baixo).** Pela auditoria 36 (§3, "Consequências da versão de 19/03"), o "Q2 sem as células só de CR" do ciclo
  2 e a sensibilidade "só vagas imediatas" condicionam no resultado. As frases corrigidas do 57l ("a queda vai de
  −27,8 p.p. para −12,9 p.p. sem as células só de CR do quadro de 19/03/2026") e do 49b ("com esse quadro, mais reserva
  no denominador baixa a taxa") dizem de que quadro vêm, mas não dizem que, por isso, o −12,9 não é decomposição
  pré-tratamento. Os blocos são gerados pelos scripts 38 e 23b; a mudança não é só de registro. Fica como
  recomendação: uma oração nos dois geradores ("no ciclo 2, tirar as células só de CR do quadro de 19/03 condiciona
  no resultado; a versão com o quadro de 13/02 está no adendo 48b").
- **C3 (corrigido).** A fila do doc `07_apresentacoes/banca2/05_discussao_historia_empirica.md`, item 13 ("Documentos
  com texto errado a corrigir"), não registrava que a correção foi feita. Acrescentei "**Feito** (26/10/2026, commit
  `515a559`)…".

Testes: `test_contagem_vagas.py` (34), `test_diagnostico_queda_0300.py` (26), `test_gradiente_faixas.py` (24) e
`test_diagnostico_contagem_porte.py` (28, o teste do 49b) passam.

## 4. Registro de mudanças

**Arquivos criados, movidos ou removidos em `docs/` desde 24/10/2026.** O `git log --diff-filter=ADRC` lista 73
arquivos, todos **criados**: nenhum foi movido, renomeado ou removido em `docs/`. Cada um foi procurado no registro,
numa linha de tabela ou numa frase da entrada:

- 72 têm entrada;
- **R1 (corrigido):** `07_apresentacoes/banca2/04_conteudo_deck_curto.md`, criado no WIP `57683ad` (26/10/2026), não
  tinha entrada. A entrada "Retrato WIP" fala do deck curto, mas não do arquivo. Registro retroativo na entrada desta
  auditoria.

**R2 (corrigido). A entrada duplicada "Execução do protocolo 60, parte B".** As duas não descrevem o mesmo arquivo.
O `git blame` mostra que o texto da entrada do retrato WIP `886ac00` (parte B, doc 57k) entrou no registro em **três**
lugares, por junção malfeita com o WIP `8ba0c35` (protocolo 61) e com a entrada da parte A:

| Lugar | O que tem | Situação |
|---|---|---|
| entrada própria "Execução do protocolo 60, parte B" | título, motivo, tabela com o 57k, "Também criados" | válida |
| dentro da entrada "Protocolo 61 executado" | título e motivo da parte B, colados entre o motivo do 61 e a tabela do 61 (57l, script 38, `DQ_*`) | fragmento: o título duplicado fazia a tabela do 57l parecer da parte B |
| dentro da entrada "Protocolo 60, parte A" | linha do 57k na tabela, "Também criados" e o parágrafo do manifesto A6 | fragmento: a parte A parecia ter criado o 57k |

Correção sem apagar nada. No segundo lugar, o título e o motivo duplicados ficaram riscados, numa citação com nota
datada: foram **substituídos** pela entrada da parte B, e a tabela pertence ao protocolo 61. No terceiro, uma nota
datada depois do bloco diz que a linha do 57k e os dois parágrafos são da parte B e foram substituídos por aquela
entrada. Não há outro título repetido no registro. Os arquivos que aparecem em duas tabelas desde 24/10 são casos
legítimos (por exemplo, o 48b, criado numa entrada e alterado em outra), fora o 57k, tratado acima.

**R3 (corrigido). Entradas "pendente" ou WIP já auditadas.** Ganharam nota curta datada, sem reescrever a entrada:

| Entrada | Dizia | Auditado em |
|---|---|---|
| Doc 57w (adendo 48h) | "Auditoria pendente" | auditoria 47 |
| Doc 57v (adendo 52d) | "auditoria pendente" | auditoria 46 |
| Doc 57u (adendo 48g) | "Auditoria pendente" | auditoria 45 |
| Doc 57t (adendo 48f) | "auditoria pendente" | auditoria 44 |
| Doc 57s (adendo 48e) | "auditoria pendente" | auditoria 43 |
| Protocolo 64 executado (57q) | "auditoria pendente" | auditoria 39 (e o formato *fuzzy*, nesta) |
| Retrato WIP: adendo 48c e deck curto | "WIP, sem auditoria" | auditoria 42 (48c); auditoria 49 (deck curto) |

As entradas do 57k e do 57l vieram de commits WIP, mas não dizem "WIP" nem "sem auditoria"; as auditorias 34 e 33
já estão registradas. Não há `tests/test_registro_mudancas*`. Os testes que leem o registro
(`test_conteudo_banca2.py`, `test_diagrama_banca_final.py`) só exigem a presença de caminhos, que continuam lá.

**Observação.** O commit `78f9c57` e os seguintes, já na `main`, acrescentam entradas no topo do registro. Esta
auditoria foi aplicada sobre `a6236fc` e não conflita com eles.

## 5. Worktrees em `.claude/worktrees/`

Inventário em 27/10/2026, por volta das 14h15 UTC, só leitura. São 21 worktrees, contando este
(`agent-a975e7b8f013a4d02`, a auditoria 51). "Fora da main" = `git log origin/main..<branch>`, com `origin/main` em
`a6236fc`.

O equivalente a `git status --short` foi calculado sem rodar git dentro dos worktrees, porque o isolamento deste
agente bloqueia `git -C`. Para cada arquivo, comparei o hash de blob em disco com a árvore do HEAD do worktree e
filtrei os não rastreados pelo `.gitignore`. Cada arquivo alterado ou novo foi comparado com a `main`: "na main" quer
dizer que o conteúdo é igual ao da `main` ou a uma versão que já esteve nela.

| Worktree | Branch | HEAD | Commits fora da main | Não commitado | Leitura |
|---|---|---|---|---|---|
| `agent-a12b338193439241c` | `worktree-agent-a12b338193439241c` | `39f129c` | 0 | limpo | nada a recuperar |
| `agent-a20c7726f13d92050` | `worktree-agent-a20c7726f13d92050` | `f47624f` | 0 | 5 M, 9 novos: execução da parte B do protocolo 60 (script 37, `OL_*`, 57k, teste) | rascunho; todas as versões estão ou estiveram na main (retrato `886ac00`, auditoria 34) |
| `agent-a23f0187c7139eed8` | `worktree-agent-a23f0187c7139eed8` | `2cad1d2` | 0 | 10 M, 16 novos (+2 ignorados: brutos do IVS oficial, também no checkout principal): P4 (script 28, `P4_*`, `test_P4_trajetoria.py`, 57d) | rascunho de 19/10, diferente da main; a versão final do P4 está na main (`test_trajetoria_medicos.py`, 57d, auditoria 24) |
| `agent-a35c59d5224eae61d` | `worktree-agent-a35c59d5224eae61d` | `7e9f881` | 0 | limpo | travado (*locked*); nada a recuperar |
| `agent-a383665ec53e8c07d` | `worktree-agent-a383665ec53e8c07d` | `568d8e4` | 0 | limpo | nada a recuperar |
| `agent-a4f0535ef496294e6` | `worktree-agent-a4f0535ef496294e6` | `843141a` | 0 | limpo | nada a recuperar |
| `agent-a4f6b45a7d07db646` | `worktree-agent-a4f6b45a7d07db646` | `8e95d8b` | 0 | 4 M, 9 novos: P1 (script `25_escolha_dap.py`, `P1_*`, `test_P1_escolha.py`, 57a) | rascunho de 19/10; a versão final do P1 está na main (`test_escolha_dap.py`, 57a, auditoria 26) |
| `agent-a554ee4c7666f75cf` | `worktree-agent-a554ee4c7666f75cf` | `7e9f881` | 0 | 2 M, 1 novo: registro, doc 65, auditoria 50 | travado; agente da auditoria 50; doc 65 e auditoria 50 iguais à main (`5211e01`) |
| `agent-a57df57513f68ca4b` | `worktree-agent-a57df57513f68ca4b` | `4281cca` | **1**: `4281cca` "Prévia do deck curto… (WIP)" (`gerar_previa_curto_banca2.py`, PDF/PPTX de prévia) | limpo | prévia superada pelo deck curto da main (auditoria 49) |
| `agent-a5b79bcd2e3fd9996` | `worktree-agent-a5b79bcd2e3fd9996` | `daca437` | 0 | 5 M, 8 novos: execução do protocolo 61 (script 38, `DQ_*`, 57l, teste) | rascunho; todas as versões estão ou estiveram na main (WIP `8ba0c35`, auditoria 33) |
| `agent-a709c2842c641fa64` | `worktree-agent-a709c2842c641fa64` | `5d205f2` | 0 | limpo | nada a recuperar |
| `agent-aa01c7fc0132c6840` | `worktree-agent-aa01c7fc0132c6840` | `32a1cde` | 0 | 14 M, 10 novos: deck da banca 2 e deck curto (docs 01–04, gerador, figuras, PPTX/PDF) | rascunho; todas as versões estão ou estiveram na main (WIP `57683ad`) |
| `agent-abc87096856a11dbe` | `worktree-agent-abc87096856a11dbe` | `28f16fb` | 0 | limpo | nada a recuperar |
| `agent-ac0541a3256f2f9af` | `worktree-agent-ac0541a3256f2f9af` | `78f9c57` | 0 (o `78f9c57` já está na main) | 8 M, 6 novos: doc 03 da banca 2, registro, `gerar_figuras_banca2.py`, `numeros_banca2.json`, `manifesto_figuras.json` diferentes da main; 4 figuras novas `curto_*.png` ausentes da main; docs 07, 08 e auditoria 50 iguais à main | **travado e ativo** (mexido às 13h58): trabalho em curso do deck novo; **não é abandono** |
| `agent-acc86249d53a99f50` | `worktree-agent-acc86249d53a99f50` | `71a6645` | 0 | limpo | nada a recuperar |
| `agent-acfd89e49780b38be` | `audit-P6` | `05ebf18` | **2**: `113e8bd` (P6, passo 0) e o merge `05ebf18` | 9 caches novos `output/rdd_bolsa/P6_cache/` (+63 caches ignorados, inclusive `cache_privado` do CNES) | P6 superado pela versão da main (`df7df26`, scripts 30 e 31, 57f, auditoria 27); caches intermediários |
| `agent-adb5a8a86e18d10f9` | `worktree-agent-adb5a8a86e18d10f9` | `077146c` | **3**: `4281cca`, merge `750a0ae`, `077146c` "prévia 2 do deck curto" (`gerar_previa2_curto_banca2.py`, PDF/PPTX) | limpo | prévia superada pelo deck curto da main |
| `agent-aed36c096e586ab64` | `worktree-agent-aed36c096e586ab64` | `e09dd99` | 0 | limpo | nada a recuperar |
| `agent-aed663ff562b49688` | `worktree-agent-aed663ff562b49688` | `113e8bd` | **1**: `113e8bd` (P6, passo 0) | os mesmos caches do `audit-P6` | superado (`df7df26`) |
| `agent-af8cf0881bcd7c18f` | `worktree-agent-af8cf0881bcd7c18f` | `eec3290` | 0 | limpo | nada a recuperar |

**Há trabalho útil que nunca entrou na `main`?** Não há trabalho abandonado que valha recuperar. Em detalhe:
- **Agente ativo.** O `agent-ac0541a3256f2f9af` tem trabalho em curso: quatro figuras `curto_*.png` e mudanças no
  gerador de figuras, nos números e no doc 03 da banca 2. Esse agente está em atividade e deve terminar ou commitar
  por conta própria.
- **Commits fora da main.** Os commits fora da main são as duas prévias do deck curto (`4281cca`, `077146c`), com
  geradores próprios de prévia, e o passo 0 do P6 (`113e8bd`). Todos foram superados por versões na main que já
  foram auditadas.
- **Alterações não commitadas.** As alterações não commitadas dos worktrees antigos são rascunhos de execuções que
  depois entraram na main. Em quatro deles (60B, 61, deck WIP e auditoria 50), cada arquivo é igual à main ou a uma
  versão que já esteve nela. Em dois (P1 e P4, 19/10), são versões anteriores às finais da main, com nomes de teste e
  de figura diferentes.
- **Caches.** Os caches do P6 (inclusive dados identificados em `cache_privado/`) são intermediários e não devem ir
  para o Git.

Nada foi apagado. Antes de limpar, o autor pode querer guardar só as prévias, pelo histórico do deck.

## 6. Correções feitas nesta auditoria (só texto e registro)

- `docs/00_registro_mudancas.md`:
  - entrada desta auditoria no topo, com o registro retroativo do `04_conteudo_deck_curto.md`;
  - fragmentos da parte B do protocolo 60 marcados como substituídos, nas entradas do protocolo 61 e da parte A;
  - sete notas datadas em entradas "pendente"/WIP já auditadas.
- `docs/07_apresentacoes/banca2/05_discussao_historia_empirica.md`, item 13 da fila: "**Feito**".

Nenhum script, nenhuma saída de `output/` e nenhum arquivo de `data/` foi alterado. O adendo 48b não foi tocado
(achado C1).

## 7. Testes rodados

`python3 -m pytest tests/test_arquivamento_ibge_capitais.py tests/test_oferta_local_corte.py
tests/test_contagem_vagas.py tests/test_diagnostico_queda_0300.py tests/test_gradiente_faixas.py
tests/test_diagnostico_contagem_porte.py`: **148 passam** (9 + 27 + 34 + 26 + 24 + 28), nenhum pulado. Não existe
`test_registro_mudancas`. Depois das correções, rodei também `tests/test_conteudo_banca2.py` e
`tests/test_diagrama_banca_final.py`, que leem o registro: 84 passam e 2 são pulados, porque a variável
`PMME_DECK_GRUPO` (deck do grupo) não está definida.

## 8. Reprodução

Os scripts de conferência ficaram no scratch da sessão, fora do repositório:
- leitor do DBF e do SIDRA;
- comparação do OC antes e depois;
- busca normalizada;
- estado dos worktrees.

O essencial se refaz com:

```bash
python3 scripts/aquisicao/a19_arquivar_ibge_capitais_uf.py --verificar
git diff --stat 515a559^ HEAD -- 'output/rdd_bolsa/DQ_*' 'output/rdd_bolsa/ND_*' 'output/rdd_bolsa/N_*' \
    'output/rdd_bolsa/NA_*' 'output/rdd_bolsa/GF_*'
git log --since=2026-10-24 --diff-filter=ADRC --name-status -- docs/
git worktree list
```
