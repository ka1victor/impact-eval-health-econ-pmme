# Erratas de artefatos congelados

> **Criado em:** 2026-09-14, na sessão 5 da fila de
> [`36_backlog_pos_auditoria.md`](../06_execucao/36_backlog_pos_auditoria.md).
> **Finalidade:** registrar defeito de rótulo, fórmula ou nota em artefato cuja
> reexecução não é autorizada ou não é barata, quando corrigir o artefato
> custaria mais do que corrigir a afirmação.
> **Regra:** a errata **não** altera o artefato. O valor publicado continua onde
> está; o que muda é o que se pode afirmar sobre ele. Cada entrada diz o que o
> artefato publica, o que está errado, qual é o valor ou a leitura correta, e
> por que a reexecução não foi feita.

Esta não é uma lista de resultados novos. Nenhuma entrada aqui muda estimativa,
amostra, desfecho ou estimador.

---

## E-1 · Intervalo convencional fora do espaço de parâmetros em A8

**Item de origem:** C-3.
**Artefato:** `output/tema_trabalho/A8_tabela_02_estimativas_escore_estrito.csv`.

**O que o artefato publica.** Duas linhas de `2025_C1_CH2`, amostra `gap_1_ac`,
trazem `ic95_convencional_superior = 1,2618`:

| ciclo_chamada | desfecho | n_pares | diferença | IC95% convencional |
|---|---|---:|---:|---|
| `2025_C1_CH2` | `homologacao_mesma_celula` | 6 | +0,8333 | 0,4049 a **1,2618** |
| `2025_C1_CH2` | `homologacao_qualquer_local` | 6 | +0,8333 | 0,4049 a **1,2618** |

**O que está errado.** A diferença de duas proporções vive em `[-1, 1]`. Um
limite superior de 1,2618 está fora do espaço de parâmetros e não é
interpretável como probabilidade. A coluna já se chama "convencional" e a seção
5 do `A8_relatorio_cutoff_escore.md` já diz que os intervalos `t` não resolvem a
discretização da running variable, mas nenhuma ressalva sinalizava **estas**
linhas, e nenhum intervalo alternativo era oferecido ao lado.

**A leitura correta.** Com seis pares, cinco discordantes favoráveis e nenhum
contrário, a aproximação normal é inadequada nas duas pontas. O intervalo exato
condicional — Clopper–Pearson sobre os pares discordantes, o análogo exato do
teste de McNemar que a própria tabela já usa em `p_exato_pareado_bicaudal` — é:

| desfecho | IC95% convencional | IC95% exato |
|---|---|---|
| `homologacao_mesma_celula` | 0,4049 a 1,2618 | **−0,0364 a 0,8333** |
| `homologacao_qualquer_local` | 0,4049 a 1,2618 | **−0,0364 a 0,8333** |

Além de caber no espaço de parâmetros, o intervalo exato **cobre o zero**,
enquanto o convencional não. Isso é coerente com o `p` exato já publicado para
essas linhas, `0,0625`, que não rejeita a 5%: o convencional era otimista, não
apenas mal delimitado. A leitura correta dessas duas linhas é de **efeito
direcional impreciso**, sustentado por seis pares, e não de efeito estabelecido.

**O que foi feito em vez de reexecutar A8.** O intervalo exato passa a ser
publicado ao lado, em artefato próprio, sem tocar nas tabelas de A8:

- gerador: [`scripts/tema_trabalho/09b_intervalos_exatos_escore.py`](../../scripts/tema_trabalho/09b_intervalos_exatos_escore.py)
- artefato: `output/tema_trabalho/A8_tabela_06_intervalos_exatos.csv`

Ele lê `A8_tabela_02` e `A8_tabela_03` já publicadas, recalcula nada do
estimador e acrescenta três colunas: `ic95_convencional_fora_do_espaco`,
`ic95_exato_inferior` e `ic95_exato_superior`. Das 22 linhas cobertas, duas têm
intervalo convencional fora de `[-1, 1]` — exatamente as duas acima.

**Por que não reexecutar A8.** Duas razões independentes. A fila proíbe alterar
amostra, desfecho ou estimador de A8. E, verificado nesta sessão, os artefatos de
A8 versionados **não reproduzem byte a byte** sob o ambiente documentado: ver a
seção "Achado de reprodutibilidade" abaixo.

---

## E-2 · MDE por estrato do A3 usa fórmula de proporção única

**Item de origem:** C-5.
**Artefato:** `output/tema_trabalho/potencia_atracao.json`, bloco `por_estrato`.
**Gerador:** `scripts/tema_trabalho/04_congelar_pre_analise.py`.

**O que o artefato publica.** Cada estrato traz `mde_80_pp_p50` e
`mde_80_pp_p30` — por exemplo, capital `0,176` e `0,1613` — sem nenhum rótulo
sobre o que esses números são.

**O que está errado.** Três coisas, todas confirmadas por leitura do código:

1. **Não são MDE de diferença.** São calculados por `mde_proporcao`, cujo
   erro-padrão é `sqrt(p(1-p)/n)·sqrt(DEFF)`, o de **uma** proporção. O MDE de
   um contraste soma a variância dos dois lados, como faz
   `mde_diferenca_dois_grupos`. O bloco `mde_global` já carrega o rótulo
   `"benchmark de precisão de uma proporção; não é o MDE dos coeficientes
   territoriais"`; o bloco `por_estrato` publica números da mesma fórmula **sem**
   rótulo equivalente.
2. **O docstring errava duas vezes.** Dizia *"MDE bilateral para diferença de
   proporções vs baseline (aprox. 2*SE)"*. Não é EP de diferença, como acima; e
   o multiplicador não é 2, e sim `Z_ALPHA + Z_POWER = 1,9600 + 0,8416 =
   **2,8016**` para alfa bilateral de 5% e poder de 80%. Conferido reproduzindo
   capital à mão: `sqrt(0,25/73)·sqrt(1,153)·2,8016 = 0,176`, exatamente o valor
   publicado.
3. **`mde_diferenca_vs_resto_p50` usa o DEFF errado de um lado.** A chamada passa
   `deff2=deff`, o DEFF da **amostra inteira** (1,126), onde o correto seria o
   DEFF do próprio complemento do estrato. Conferido: capital com
   `n1=73, deff1=1,153, n2=1.222, deff2=1,126` devolve `0,1811`, o valor
   publicado.

**Consequência substantiva: nenhuma para o artigo.** O artigo usa apenas os
contrastes versus interior remoto, do bloco `contrastes_vs_interior_remoto`, que
são calculados por `mde_diferenca_dois_grupos` com o DEFF de cada lado e estão
corretos. O `interpretacao.regra` do próprio artefato já manda usar esses, e não
o benchmark global.

**Leitura correta do bloco `por_estrato`.** `mde_80_pp_p50` e `mde_80_pp_p30`
devem ser lidos como **precisão de uma proporção dentro do estrato**, não como
potência de um contraste, e `mde_diferenca_vs_resto_p50` como aproximação com o
DEFF do complemento substituído pelo da amostra inteira.

**Por que errata e não reexecução.** A3 é protocolo congelado e o próprio item
recomenda errata. Reexecutar regravaria `potencia_atracao.json` e
`registro_pre_analise_atracao.json`, cujos hashes entram no manifesto A6 e na
cadeia a jusante, para trocar rótulo de números que o artigo não usa. O
docstring e um comentário no ponto exato do código foram corrigidos, porque não
alteram nenhuma saída; os artefatos seguem intactos, com hashes
`91fa9055…` e `eb2bf812…`.

---

## Achado de reprodutibilidade — A8 não reproduz byte a byte

Registrado aqui porque condiciona a escolha da E-1, e não como resultado.

Verificado em 14/09/2026, no ambiente documentado (Python 3.13.12, numpy 2.5.2,
pandas 3.0.5, scipy 1.18.1, matplotlib 3.11.1, todos iguais ao
`requirements.txt`): reexecutar `scripts/tema_trabalho/09_estimar_cutoff_escore_estrito.py`
**altera seis artefatos de A8** em relação ao que está versionado.

O que muda é pequeno e não é resultado:

- `A8_tabela_02`, `A8_tabela_03`, `A8_tabela_04`, `A8_estimativas_cutoff_escore.json`
  e `A8_protocolo_cutoff_escore.json` diferem **apenas** nas colunas de intervalo
  de confiança, e apenas a partir do 15º dígito significativo — por exemplo,
  `0,41394184915555393` contra `0,413941849155554`. Diferenças, erros-padrão,
  contagens de pares, discordantes e `p` exatos são idênticos dígito a dígito.
- `A8_figura_01_efeitos_cutoff_escore.png` muda de 63.929 para 75.121 bytes, o
  que é assinatura de outra versão de renderização.

**Duas execuções consecutivas agora são byte a byte idênticas entre si**,
incluindo o PNG. Ou seja, o script é determinístico neste ambiente; o que não
bate é o artefato versionado, que foi gravado sob outro estado de biblioteca.

**O que isso significa e o que não significa.** Não invalida nenhum número
publicado: toda cifra de A8 citada no artigo é reportada em precisão muito acima
da divergência, e o conferidor segue aprovando. O que deixa de valer é a
generalização de que *o repositório inteiro* reproduz byte a byte sob o ambiente
documentado — verificada para A4, e **falsa para A8**.

**Não corrigido nesta sessão, de propósito.** Regravar os artefatos de A8 para
fazê-los bater seria ajustar até o resultado fechar, que é o que a fila proíbe.
A decisão de regravar A8 sob o ambiente documentado — e de registrar o novo
conjunto de hashes — é do autor, e está anotada no item C-3 da fila.

### Complemento de 14/09/2026 — há um defeito objetivo junto do juízo

A discussão acima é sobre dígitos, e nela cabe juízo. Junto dela viaja um
defeito que não depende de juízo nenhum: **os artefatos versionados de A8
registram os caminhos dos insumos com barra invertida do Windows**, seis
ocorrências em `A8_protocolo_cutoff_escore.json` e oito em
`A8_estimativas_cutoff_escore.json`, do tipo
`data\raw\pmm_e\2025_ciclo1_chamada1_homologados.xlsx`. O manifesto de
reprodução do próprio repositório declara a plataforma como
`Linux-6.18.44-fc-v24-x86_64-with-glibc2.39`.

Não é divergência de precisão: é registro de proveniência gravado num formato
que não corresponde à plataforma declarada e que não resolve para caminho válido
aqui. Reexecutar `09_estimar_cutoff_escore_estrito.py` no ambiente documentado
corrige isso sozinho, gravando caminhos POSIX relativos à raiz.

Isso muda o peso da decisão do autor. Regravar A8 **não seria apenas** trocar
dígitos irrelevantes para fazer hash bater; seria também consertar um registro
de proveniência que hoje está errado. Os dois efeitos vêm no mesmo ato e não
podem ser separados, porque ambos saem da mesma reexecução.

A recomendação desta errata continua sendo que a decisão é do autor, mas com a
ponderação explícita: **manter os artefatos como estão preserva a cadeia de
hashes e conserva caminhos Windows incorretos; regravá-los conserta os caminhos
e obriga a reemitir os hashes de A8 onde eles estiverem fixados.** Amostra,
desfecho e estimador de A8 não mudam em nenhum dos dois caminhos.
