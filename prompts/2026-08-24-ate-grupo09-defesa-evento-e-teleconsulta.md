# ATE em três frentes: a defesa do painel (migração ao Grupo 09), o evento (entrada OCI) e o teste do modelo (teleconsulta)

> Escrito em 24/08/2026, depois de o autor mandar converter as implicações da nota
> `02-saude/66` em plano: *"devemos fazer o q exatamente? pensa sobre e documenta bem"*.
> A fila marcável está no `TODO.md` (itens Q-ATE nos blocos do T2 e do T4); este arquivo é
> o texto integral do que se cola, com o critério de parada de cada item dentro.
>
> **A ordem dos itens é de dependência e de risco, não de interesse: o item 1 é DEFESA do
> ativo central e bloqueia qualquer estimação com competência de 2025 em diante; os
> demais são oportunidade.** Nada aqui muda a ordem T2, T4, T6 do `VEREDITO.md` §T.0c-3.
>
> **Pré-requisitos de infraestrutura, os mesmos de sempre:** contêiner novo vem sem
> git-lfs (`apt-get install -y git-lfs`, depois `git lfs pull --include=` só do
> necessário) e sem numpy (`pip install --break-system-packages numpy scipy duckdb`).
> `git fetch --all --prune` e merge do `main` ANTES de reconstruir fila.
>
> **Hosts:** o espelho `dfdu08vi8wsus.cloudfront.net/sia-pa` (o mesmo do A4; cortesia de
> 1 req/s), o FTP do DATASUS só se o item 1b precisar do zip do SIGTAP, e gov.br/bvsms
> para o item 0. Nenhum item toca o e-SAJ.
>
> **Trava de replicação obrigatória antes de qualquer estimação sobre painel OD:**
> SP 0301, 12 competências de 2024, β = **−1,4043**. Carregador com `--anos` explícito e
> janela impressa (armadilha do `glob`, `INVENTARIO` Parte 3).
>
> **Os três controles da extração do Grupo 09 já estão medidos** (nota `66 §66.2`) e são a
> régua de sanidade de qualquer download novo: positivo, AC 2025-06 tem **433** linhas de
> Grupo 09 com residência 100%; negativo, competência de 2024 tem **zero**; temporal, AC
> 2026-01 tem **856**. Extração que não reproduzir os três está lendo o arquivo errado.

---

## Item 0 · As normas, com hosts que falham (custo: minutos, tolera ❓)

Tentar o texto oficial de: Portaria GM/MS 7.266/2025 (linhas de ação do ATE), Portarias
SAES 1.821, 1.823 e 1.824/2024 (criação do Grupo 09), SAES 1.640/2024 (habilitação 38.01)
e SAES 2.326/2024 (telessaúde no Grupo 08). O bvsms devolveu **503** em 24/08; alternar
com `in.gov.br` e os espelhos do CONASS e COSEMS. **Objetivo: promover as datas e regras
de habilitação de ⚠️ a ✅.** Se os hosts falharem, seguir: a datação dos itens abaixo vem
da PRODUÇÃO, não da norma, e fechar com ❓ declarado é fechar.

## Item 1 · Q-ATE2, a DEFESA: quanto volume os subgrupos do gradiente perdem para o Grupo 09 (custo: uma tarde)

**Por que primeiro:** a OCI é migração de registro (APAC única do Grupo 09 no lugar de
consultas e exames dos subgrupos 02 e 03). O A4 já tem 2025 em disco para SP e PE, e
**qualquer sessão que estime 2025 sem esta medida está estimando com o desfecho vazando
para outro código.**

1a. **Nacional, de graça, do SIGTAP em disco:** série mensal da quantidade aprovada do
    Grupo 09 contra a dos dez subgrupos do gradiente (`output/sigtap_sia_2025*.csv`).
    Reportar a razão 09/(09+subgrupo) por mês.
1b. **O mapa OCI → procedimentos componentes:** a tabela de compatibilidade
    APAC-principal × secundário do SIGTAP (zip mensal ❓, host FTP). Dela sai DE QUAIS
    subgrupos o volume migra (a OCI de ortopedia com TC tira volume do 0206, a de
    oncologia do 0304, e assim por diante).
1c. **Por UF do painel (SP, PE, MG, CE):** extrair o Grupo 09 do espelho, 2025-01 até a
    última competência disponível, e computar a razão de migração por subgrupo-UF-mês.

**Regra de saída, escrita antes de rodar:** competência em que a migração passar de
**1% do volume de qualquer subgrupo usado** não entra em estimação sem correção (somar a
OCI mapeada de volta ou declarar o viés com sinal). Abaixo de 1%, registra-se a fração e
segue-se. O resultado vira bloco no `INVENTARIO` Parte 3, ao lado da armadilha já aberta.

## Item 2 · Q-ATE1, o EVENTO: a entrada OCI por estabelecimento, com as métricas do portão 1 (custo: horas)

> ⚠️ **Este item não reabre o T7.** O `CLAUDE.md` manda não reabri-lo *sem fonte de evento nova*,
> e a entrada de OCI **é** a fonte nova: outro registro, outra data (o repasse), outro fenômeno
> (entrada de linha de cuidado, não abertura ou fechamento de unidade). Se o teste zero abaixo
> reprovar, ela morre como as três rotas do T7 morreram, e isso fecha o item.

🔴 **TESTE ZERO, OBRIGATÓRIO, acrescentado no merge com a nota `58`: o entrante é oferta
nova ou reetiquetagem?** A `58` mediu que **91,4%** dos eventos de entrada do SIA são CNES que
**já faturavam outro subgrupo**, e para a OCI a versão da ameaça é pior: o estabelecimento pode
já fazer as consultas e exames componentes para as mesmas origens, e a APAC 09 ser só um
invólucro de faturamento. **Medir, antes de qualquer m1:** a fração dos entrantes de OCI que já
faturava os procedimentos componentes (do mapa do item 1b) para as mesmas origens nos doze meses
anteriores. **Limiar escrito agora: acima de 50%, o evento morre como oferta nova**, a nota o diz
com destaque, e o item para aqui. Abaixo, a fração vai para a nota como erro de medida declarado.

🟢 **E a `58` dá a esta rota a defesa que ela não tinha:** o cadastro **envelopa** a produção, e o
erro troca de sinal entre as pontas (no nascimento antecede 6 meses e chega depois em 3,9% dos
casos; na morte atrasa 13 meses e chega depois em 94,5%). **Entrada é datável, saída não é**, e é
por isso que este item usa entrada. O **CNES-ST mensal está em disco** desde a `58`
(`output/bases_saude_externas/cnes_st_painel/`), então a habilitação **38.01** do PMAE pode ser
lida por estabelecimento-mês e **confrontada** com a data de produção, em vez de substituí-la.

Extrair do espelho, para SP, PE, MG e CE, todas as linhas de Grupo 09 por
estabelecimento-competência (2025-01 até o fim do espelho). A **primeira competência com
APAC 09 do estabelecimento é a data de entrada**, datação pela produção, que é a que a
nota `62` exigiu e o T7 não tinha. Medir:

- **m1** (coortes efetivas) e **m1b** (fração da coorte modal) sobre as primeiras
  competências por estabelecimento;
- **m2**: desvio padrão da dose em km (distância dos municípios num raio de 100 km ao
  estabelecimento entrante), com os centroides já em disco;
- contagem de entrantes por UF e por subgrupo de OCI.

**Critério de parada, escrito antes de rodar:** **m1 < 2 ou m1b > 50%** mata o evento OCI
pelo mesmo número que matou a telessaúde por cadastro (nota `29`), e a nota o diz com
destaque, porque enterrar cedo é o resultado mais valioso. Se passar: **não estimar efeito
nesta sessão.** O entregável é o desenho do m5 (janela pré no fluxo dos vizinhos, com a
seleção do PAR declarada como a ameaça, que é a patologia da fiscalização do T1) e a
m3 escalada pela fração exposta, como a nota `62 §62.5` manda.

## Item 3 · Q-ATE3, a teleconsulta por estabelecimento: rampa, coortes e o ato de 2024 (custo: horas)

Extrair 0301010307 e 0301010315 por estabelecimento-competência (2024-01 até o fim do
espelho) nas quatro UFs. Medir m1 e m1b da primeira competência de produção por
estabelecimento, e a rampa por UF. Pergunta adversarial obrigatória: **que ato explica a
inflexão nacional de meados de 2024** (28,7 mil em janeiro para 64,2 mil em dezembro,
nota `66 §66.2`)? Buscar a portaria; se for um único ato com adoção em bloco, o item 4
morre antes de rodar. **Critério de parada: m1b > 50% numa coorte única.**

## Item 4 · Q-ATE4, o β da teleconsulta: hipótese PRÉ-REGISTRADA aqui (custo: horas, depois do item 3)

**A hipótese, escrita antes de olhar qualquer estimativa, com âncora medida:** a
teleconsulta tem custo de viagem zero, então o modelo de custo de viagem prevê que o
"par origem-destino" dela é geografia de faturamento, não fricção. A previsão formal:

> **|β_teleconsulta| fica na faixa do braço sem paciente do D3** (−0,0865 em SP, nota
> `63 §63.6`), isto é **abaixo de 25% do β presencial do mesmo recorte**, e o IC95 dela
> exclui o β presencial (−1,2 a −1,4).

Estimar com os mesmos efeitos fixos de origem-mês e destino-mês, teleconsulta como
subgrupo extra, SP e PE primeiro. **Publicável nos dois sinais:** β ≈ 0 é a validação
interna mais elegante que o modelo pode ter (o cuidado que não viaja não paga distância);
β grande diz que o registro de residência da teleconsulta carrega a geografia da rede, e
isso vira aviso de dado no `INVENTARIO`. ⚠️ Reportar junto o mesmo recorte para PE com a
ressalva de rede em estrela do D3.

## Item 5 · Q-ATE5, se sobrar sessão: as listas que provavelmente não existem (custo: uma tarde, tolera 🔴)

Credenciados dos chamamentos de 2025 com CNES e data ❓; carretas e mutirões com município
e data ❓; implementação municipal do transporte da Lei 15.233 ❓. Hosts gov.br. Se não
existir em fonte pública, **a nota registra o 🔴 por dado e isso também é resultado**.

---

## O que esta sessão NÃO faz

1. Não estima efeito de OCI sobre fluxo de vizinho (o m5 vem antes, e é de outra sessão).
2. Não usa tempo de espera como desfecho (o programa cria o próprio registro, regra 1).
3. Não usa habilitação do CNES como data de evento (atraso médio de 3,24 anos, nota
   `62 §62.16`): data é a primeira competência de produção, sempre.
4. Não reabre telessaúde por cadastro, sob nenhuma forma (notas `13`, `24`, `29`).
5. Não muda a ordem T2, T4, T6.

**Definição de pronto:** cada item fecha com número e nota escrita (a nota nova é a `67`),
ou com ❓ declarado dizendo qual host respondeu o quê. Fechar com ❓ é fechar, e morrer é
fechar. Commit ao fim de cada item, sem empurrar sem pedir.
