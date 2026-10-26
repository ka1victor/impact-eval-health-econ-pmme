# Roteiro narrativo da banca 2

> **Classificação:** decisão de comunicação, não de método<br>
> **Conteúdo dos slides:** [02_conteudo_slides.md](02_conteudo_slides.md)<br>
> **Plano que este roteiro executa:** [04_plano_entrega_empirica.md](04_plano_entrega_empirica.md), §3 a §5 e §9<br>
> **Estado:** pronto para 28/10, com a H3 PENDENTE (protocolo 52b em estimação e auditoria)<br>
> **Atualização:** 26 de outubro de 2026

---

## 1. Arco da apresentação

A banca 2 cobra, nesta ordem: hipótese econômica; base de dados e
descritivas; metodologia econométrica e hipóteses de identificação;
resultados, robustez e discussão. O deck do grupo já cobre motivação,
pergunta, literatura e o modelo; os slides novos entram na seção de hipótese
e nos três marcadores "X" (Base de Dados, Metodologia, Resultados).

Fio condutor: **o modelo da banca 1 tem uma cadeia — bolsa maior, vaga que
vale mais, mais médicos que a escolhem, vaga preenchida — e nós testamos cada
seta, não só a última.** Com isso, o nulo no preenchimento deixa de ser o fim
da história e ganha explicação dentro do modelo.

| Bloco da banca | Pergunta que responde | Slides novos |
|---|---|---|
| Hipótese econômica | que setas do modelo testamos, e com que equação? | cadeia H1–H4; ponte modelo → equação |
| Base de dados e descritivas | de onde vêm os dados e como são os três ciclos? | tabela de fontes; tabela descritiva por ciclo |
| Metodologia econométrica | que estimador para cada hipótese, e o que precisa valer? | um estimador por hipótese; hipóteses de identificação |
| Resultados | o que se move e o que não se move? | regra sharp; H1; H2; H3 (PENDENTE); H4; cadeia-resumo |
| Robustez e discussão | as leituras aguentam? o que o contraste não mede? | robustez; limites; magnitude e próximos passos |

## 2. Hipóteses pela cadeia do modelo (decisão de 26/10/2026)

| Hipótese | Seta | Leitura hoje |
|---|---|---|
| **H1** preenchimento | B → Pr(Y = 1) | inconclusiva: não se detecta aumento; o IC da célula aberta descarta ganhos grandes com os cortes empilhados |
| **H2** escolha | B → V → π | inconclusiva na primária; o sinal robusto está só no ciclo 2 |
| **H3** incentivo limitado | a bolsa contra o custo do lugar, dentro de V | **pendente** (protocolo 52b) |
| **H4** capacidade líquida | chegada → capacidade | associação: o médico soma horas cadastradas, mas metade já estava no município |

A recomendação do plano (§3), delegada pelo autor e revisável por ele, é a H3
como hipótese central, com a H2 como o parâmetro que ela usa e a H1 como teste
de consistência. A variável de efeito da H1 que o grupo pediu é o número de
vagas preenchidas controlando o número de vagas oferecidas (N1); ela vem
junto com a probabilidade de a célula aberta ser preenchida (A3) e com o que
o IC descarta.

## 3. A lógica de cada bloco

### 3.1 Hipótese

Dois slides depois do slide do grupo "Da condição de aceitação, sai nossa
hipótese econômica". O primeiro desenha a cadeia e põe H1–H4 sobre as setas.
O segundo mostra o modelo virando equação: β é o 1/p do modelo; distância e
mesma UF são o custo geográfico; o IVS entra contínuo e absorve o custo
laboral e as amenidades; o salto no corte mede o pacote do corte.

### 3.2 Base de dados

Uma tabela de fontes (base, fonte oficial, período, unidade e chaves,
cobertura, uso) e uma tabela descritiva por ciclo. A unidade do quadro é a
**célula** (estabelecimento × curso), não a vaga; "preenchida" é alguma
confirmação ou homologação. A faixa da bolsa é contada pela grade aplicada.

### 3.3 Metodologia econométrica

Dois slides de tabela: um estimador por hipótese (RDD sharp local linear;
logit condicional; estudo de evento escalonado e comparação na nota de corte)
e as hipóteses de identificação com o teste de cada uma e a situação. A
ameaça comum é o pacote do corte.

### 3.4 Resultados

A regra sharp abre o bloco, porque é ela que torna a descontinuidade
possível. Depois, uma hipótese por slide, sempre com a mesma estrutura:
título-afirmação, figura com "Como ler" dentro, duas linhas de leitura e a
frase de cautela. A cadeia-resumo fecha o bloco com as linhas do doc 57 e a
força da evidência de cada uma.

As figuras foram refeitas para o grupo: cada linha diz em português o que
compara, o nulo é uma linha preta, a referência do protocolo é tracejada, e
o bloco "Como ler" explica ponto, barra e cor. A lição veio da banca anterior:
gráficos de descontinuidade com faixas e pontos sem explicação ficaram
incompreensíveis.

### 3.5 Robustez e discussão

Um slide de tabela com as leituras que resistem e as duas ressalvas
declaradas (o Holm de N1 depende do coeficiente do controle; o IC honesto não
informa). Dois slides de discussão: os limites (pacote do corte, margem
extensiva ausente, vínculo não é presença, não é participação no PMM-E) e a
magnitude da literatura com os próximos passos (ciclo 3 em 202703; pedidos
externos; H3 depois da auditoria).

## 4. Frases que não podem mudar

1. **Inconclusivo não é "a bolsa não funciona":** é ausência de efeito
   detectável, e IC que contém zero não é efeito zero.
2. **ATT com pré falhando é associação.** H4 é lida como associação sob
   tendências paralelas; horas cadastradas não são presença.
3. **Tudo nos cortes é "pacote do corte":** a bolsa anunciada e as outras
   regras federais que mudam nos mesmos cortes de IVS.
4. **Não é efeito da participação no PMM-E** nem do Agora Tem Especialistas:
   o efeito candidato é o incentivo marginal de R$ 5 mil.
5. **Escolha não é expansão:** o que uma vaga ganha, outra do mesmo curso
   perde.

## 5. Regras de composição

- **Título = afirmação**, curto o bastante para não encostar no logotipo.
- **Número no corpo tem código.** Cada slide lista, na linha `**Números:**`,
  os códigos do bloco gerado de [03](03_proveniencia_figuras_e_numeros.md).
- **Figura só do pipeline**, com "Como ler" na própria imagem.
- **Tabela nativa** no deck, com o texto do doc 02.
- **Frase de cautela** em todo slide de resultado.
- **O que não vai à tela:** as linhas `**Números:**`, as notas de produção e as
  notas do apresentador (que vão para as notas do slide).

## 6. Correções no deck do grupo

O quadro de correções está no doc 02 e é aplicado pelo gerador do deck: a
grade da bolsa aplicada; a retirada do "IVS como piso"; os gráficos de
crescimento por faixa sem proveniência; células, não vagas; SGTES e curso; o
IVS como running variable. O deck original não é alterado.

## 7. Histórico

| Data | O que mudou |
|---|---|
| 19/10/2026 | primeira versão, a partir do doc 44 e das saídas E3–E9; rascunho pendente das decisões do autor |
| 26/10/2026 | reescrita no arco do plano da entrega empírica (H1–H4 pela cadeia do modelo; metodologia econométrica), com a síntese do doc 57; H3 pendente |
