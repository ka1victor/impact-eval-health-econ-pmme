# Revisão crítica de A01–A05 antes do portão A06

> **Data da revisão:** 28 de agosto de 2026  
> **Estado inspecionado:** `dbc7986`  
> **Escopo:** qualidade, proveniência, coerência substantiva e prontidão dos
> entregáveis A01–A05.  
> **Não contém:** execução do A06, estimação causal ou correção silenciosa dos
> produtos revisados.

## 1. Decisão

Os produtos A01–A05 **não devem ser entregues ao A06 como se estivessem
validados**. A01 pode ser aceita com uma ressalva terminológica. A02 deve ser
reexecutada depois de incorporar as fontes recuperadas por A01. A03 precisa de
correção de proveniência e linguagem. A04 deve ser refeita. A05 é um bom piloto
de esquema, mas não é a aquisição do painel integral e contém conclusões que não
decorrem do código executado.

| Frente | Qualidade observada | Decisão pré-A06 |
|---|---|---|
| A01 — vagas e versões | fontes oficiais recuperadas, hashes e inventário úteis | aceitar com ressalva |
| A02 — trajetória | conclusão central correta, mas fontes e matriz ficaram obsoletas após A01 | corrigir e reexecutar |
| A03 — IVS/regra | bloqueio do RDD é plausível; parte dos “brutos” é resumo local | corrigir proveniência e inferência |
| A04 — pagamentos | tabelas escritas no código foram rotuladas como brutos oficiais | refazer |
| A05 — CNES | três ZIPs oficiais íntegros e esquema útil; universo e conclusões mal rotulados | corrigir e assumir como piloto |

O saneamento está especificado em
[`prompts/aquisicao_dados/A05R_saneamento_pre_a06.md`](../../../prompts/aquisicao_dados/A05R_saneamento_pre_a06.md).

## 2. Validações técnicas que passaram

- o branch estava limpo e alinhado com `origin/main`;
- `run_all.py` concluiu sem erro;
- todos os JSONs em `output/aquisicao/` são sintaticamente válidos;
- os scripts Python compilam;
- 32 arquivos referenciados nos manifestos A01–A04 existem e conferem com os
  hashes atualmente registrados;
- os três ZIPs CNES locais — 202406, 202506 e 202607 — são íntegros e seus
  SHA-256 conferem com o manifesto A05;
- os três dados observados originais mantiveram seus hashes.

Esses testes demonstram consistência interna dos bytes atuais. Eles **não
demonstram proveniência oficial**, correção do conteúdo escrito pelo agente nem
validade de uma conclusão causal.

## 3. Achados por frente

### 3.1 A01 — aceitar com ressalva

A01 recuperou oito planilhas oficiais adicionais, inclusive os dois endpoints de
2025 anteriormente classificados como quebrados. Os arquivos são XLSX válidos,
os hashes conferem e a separação entre versões evita a soma ingênua de chamadas.

A ressalva é de unidade: `CNES + curso` identifica uma **célula agregada de
oferta**, não uma vaga física. Quando uma linha anuncia quantidade maior que um,
a chave não separa cada vaga nem permite seguir sua ocupação individual. Logo,
“100% de unicidade” significa unicidade das linhas/células dentro do quadro, não
existência de `id_vaga` estável. Expressões como “833 novas vagas” devem ser
substituídas por “833 novas células CNES–curso”, salvo se a quantidade de vagas
for somada separadamente.

### 3.2 A02 — reexecutar depois de A01

O relatório A02 ainda diz que o quadro e a alocação da primeira chamada de 2025
estão quebrados e que seus registros são inacessíveis. A01 recuperou ambos pelo
slug oficial ativo. O script A02 procura o slug histórico quebrado e não consulta
`data/raw/aquisicao/vagas/`, portanto uma nova execução sem correção reproduziria
o erro.

A matriz da primeira chamada deve ser recalculada usando as fontes A01. Isso pode
melhorar candidatura, preferência, classificação, alocação e realocação
publicadas. Não altera o bloqueio central: aceite, recusa, afastamento, saída e
spells completos continuam ausentes, de modo que `cobertura_90/120/180` ainda
não é mensurável.

### 3.3 A03 — resultado negativo útil, proveniência inadequada

Seis páginas oficiais foram preservadas como HTML. Entretanto, as duas portarias
e o Atlas do Ipea foram representados por JSONs cujo conteúdo foi escrito no
próprio script. Esses resumos foram classificados como
`registro_oficial_preservado`, embora não sejam os bytes do documento oficial.
Se o original não puder ser obtido, o correto é registrar a falha e manter o
resumo em `output/`, explicitamente derivado.

O script também desabilita a verificação TLS e produz timestamps variáveis. Os
HTMLs rastreados como texto podem sofrer conversão de fim de linha no checkout:
os hashes abreviados do relatório A03 não coincidem com o manifesto atual após a
integração. Brutos textuais precisam ser preservados como bytes, inclusive com
regra `.gitattributes` apropriada.

A divergência de 42,56% entre categoria textual e recálculo com IVS 2010 é um
diagnóstico relevante, mas não “demonstra classificação multicritério”. Também é
compatível com vintagem diferente, precisão, arredondamento, recodificação,
historicização defeituosa ou erro cadastral. A conclusão máxima é que a regra
administrativa não foi reconstruída e o RDD permanece bloqueado.

### 3.4 A04 — rejeitar e refazer

A04 não executa uma aquisição de dados orçamentários. O script contém listas
hard-coded de valores normativos e de execução financeira, grava essas listas em
`data/raw/aquisicao/pagamentos/` e calcula hashes dos arquivos recém-criados. O
manifesto aponta domínios gerais como “SIOP e Portal da Transparência”, sem URL de
recurso, consulta, parâmetros, identificador de relatório ou resposta oficial
preservada.

O problema independe de os números parecerem plausíveis: não há como reproduzir
sua origem. Esses arquivos locais não podem ser chamados de brutos oficiais. A04
deve preservar respostas oficiais reais ou retirar os valores exatos e registrar
honestamente que a extração não foi obtida.

Há ainda sobrealcance econométrico. Observar a faixa anunciada mede uma versão do
tratamento; não identifica, por si só, um ITT causal. O efeito continua dependente
do desenho de atribuição, do outcome, do denominador e das hipóteses que A06 e o
protocolo ainda avaliarão.

### 3.5 A05 — aceitar somente como piloto de esquema

Foram baixadas três das 26 competências planejadas: 202406, 202506 e 202607. Os
ZIPs somam aproximadamente 1,97 GB, são oficiais, estão íntegros e permitem
demonstrar que CNES mensal contém estabelecimento, vínculo/carga horária e
infraestrutura. Isso é suficiente para um piloto de viabilidade de esquema, não
para construir tendências mensais ou FTE longitudinal.

O relatório afirma validar 518 estabelecimentos “ofertados”, mas o código forma
esse conjunto somente a partir do snapshot nominal de participantes ativos. As
planilhas de vagas são listadas como fontes, mas não são lidas para formar o
universo. A conclusão correta é que os 518 CNES do snapshot ativo foram
localizados; o universo de estabelecimentos ofertados ainda precisa ser
recalculado a partir dos quadros A01.

A frase de que três unidades ausentes em 202406 foram inauguradas posteriormente
é inserida diretamente no relatório sem auditoria de data de abertura. Deve ser
removida ou demonstrada. A recomendação de DiD/event study também deve ser
retirada: disponibilidade de painel não garante tratamento definido, tendências
paralelas ou desenho causal válido.

Não é necessário baixar agora as outras 23 competências. Sem ponte
PMM-E–CNES e sem log administrativo de trajetória, o painel integral não abre o
portão causal. O A06 deve receber A05 como `piloto público disponível; aquisição
integral adiada até a ponte ser obtida`.

## 4. Correções transversais obrigatórias

1. separar fonte oficial bruta de tabela derivada ou resumo escrito pelo agente;
2. registrar URL de recurso/consulta, parâmetros, data, MIME, tamanho e hash;
3. preservar bytes oficiais sem conversão de fim de linha;
4. remover timestamps voláteis de outputs determinísticos ou isolá-los como
   metadado não comparado;
5. não declarar efeito identificado só porque tratamento ou painel existem;
6. reconciliar explicitamente conclusões conflitantes produzidas em paralelo;
7. diferenciar célula CNES–curso, quantidade de vagas e vaga física;
8. distinguir piloto de esquema, aquisição completa e painel analítico pronto.

## 5. Critério para liberar A06

A06 só deve começar quando:

- A02 reconhecer e processar as fontes recuperadas em A01;
- A03 contiver fontes oficiais reais ou falhas honestamente registradas, com
  relatório e manifesto consistentes;
- A04 não contiver números escritos à mão apresentados como aquisição oficial;
- A05 separar snapshot ativo de universo de vagas e retirar inferências não
  demonstradas;
- os relatórios não declararem RDD, ITT, DiD ou event study identificado antes do
  portão;
- hashes, schemas, `run_all.py` e worktree forem validados novamente.

Até lá, o estado correto é: **aquisições executadas, revisão reprovada, saneamento
pré-A06 pendente**.

