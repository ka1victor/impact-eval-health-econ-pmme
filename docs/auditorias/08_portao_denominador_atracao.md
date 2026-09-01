# A1 — Portão do denominador de atração no ciclo 1

> **Data:** 1º de setembro de 2026  
> **Decisão:** `APROVADO_CELULA`  
> **Unidade liberada:** célula `CNES–curso`, separada por chamada e versão  
> **Unidade reprovada:** vaga física individual

## 1. Conclusão executiva

O ciclo 1 sustenta uma análise econométrica de implementação com outcome
binário por célula — **alguma confirmação ou homologação observada**. Ele não
sustenta taxa de preenchimento por vaga.

A reprovação do denominador por vaga não decorre apenas de cadastro de reserva.
Há três problemas simultâneos:

1. nenhum arquivo público contém um `id_vaga` persistente que permita seguir a
   mesma vaga entre oferta, realocação, reapresentação e homologação;
2. a segunda chamada não publica quantidade numérica de vagas imediatas por
   célula, apenas um quadro de cadastro de reserva e listas de resultado;
3. na primeira chamada, 15 células têm mais confirmações do que a capacidade
   total originalmente publicada, somando 20 confirmações excedentes. Isso é
   compatível com conversões, ampliações ou remanejamentos administrativos, mas
   impede interpretar a quantidade original como denominador físico estável.

O portão por célula passa porque as chaves `CNES–curso` são válidas, a matriz é
única dentro de `ciclo–chamada–versão–CNES–curso` e todas as divergências são
mantidas como extensões administrativas, sem imputar vagas individuais.

## 2. Fontes e versionamento

A auditoria lê oito arquivos preservados e registra o SHA-256 de cada um em
`output/tema_trabalho/portao_denominador.json`. Arquivos brutos não são
alterados.

Na primeira chamada, a alocação retificada sub judice de 19/09/2025 é a versão
canônica. A versão retificada de 10/09/2025 é apenas comparativa e não é somada:

| Verificação | Resultado |
|---|---:|
| registros em cada versão | 1.671 |
| chaves adicionadas/removidas | 0 / 0 |
| registros com conteúdo alterado | 3 |
| registros com marcação em coluna adicional | 1 |

O quadro de 59 propostas de realocação é evento complementar, não nova oferta
nem nova candidatura.

## 3. Primeira chamada

O quadro original contém 1.295 células `CNES–curso`, 678 vagas imediatas e
1.145 posições de cadastro de reserva. A versão canônica da alocação contém 468
locais confirmados e 59 locais desconsiderados; o quadro complementar contém 59
propostas de realocação; a lista final contém 316 homologações.

Das 316 homologações:

| Trilha até a homologação | Registros |
|---|---:|
| confirmação na mesma célula | 279 |
| proposta de realocação na mesma célula | 21 |
| pessoa confirmada, mas homologada em outra célula | 11 |
| pessoa realocada, mas homologada em outra célula | 4 |
| sem evento anterior localizado | 1 |
| **total** | **316** |

Em relação ao quadro original, 296 homologações fecham diretamente e 20 estão
fora dele, distribuídas em 18 células. A realocação explica parte substancial
dessa diferença, mas não produz identificador de vaga física. A matriz preserva
essas células com `registro_fora_do_quadro_publicado = true`.

As 211 confirmações em células originalmente apenas de reserva não são erro de
chave: elas indicam que modalidade original e resultado administrativo são
etapas diferentes. Por isso, não se deve restringir o numerador às células com
vaga imediata nem dividir essas confirmações pelas 678 vagas imediatas.

## 4. Segunda chamada

O arquivo inicial da segunda chamada tem duas abas com naturezas diferentes:

- o quadro de cadastro de reserva contém 1.762 células e 2.896 posições de
  reserva;
- a aba intitulada “alocados – vagas imediatas” contém 98 registros de 92
  pessoas, mas apenas 33 registros classificados. Ela não contém uma coluna de
  quantidade de vagas imediatas. Portanto, o título da aba não autoriza tratar
  os 98 registros como 98 vagas ou 98 alocações.

A classificação final contém 757 registros, dos quais 374 têm situação de
alocação. A segunda lista de homologados contém 581 pessoas, mas não é uma soma
cumulativa simples:

| Reconciliação das listas | Pessoas |
|---|---:|
| reaparecem da lista da primeira chamada | 299 |
| novas na segunda lista | 282 |
| homologados da primeira lista ausentes na segunda | 17 |
| distintos observados em pelo menos uma das listas | 598 |

Entre os 282 novos registros, 270 aparecem na alocação final, dez apenas na
publicação preliminar e dois não têm evento anterior localizado. Desses novos,
272 estão em células do quadro de reserva da segunda chamada e dez estão fora
dele. Ausência de uma lista posterior não é tratada como desligamento, pois as
publicações não formam um log longitudinal completo.

## 5. Matriz liberada

`output/tema_trabalho/matriz_funil_ciclo1.parquet` possui 3.323 linhas e nenhuma
coluna de nome ou CPF. A chave é:

`ciclo–chamada–versão_quadro–CNES–curso`.

A matriz mantém separadamente:

- vagas imediatas e posições de reserva publicadas;
- confirmação e local desconsiderado na primeira chamada;
- proposta de realocação;
- homologação da primeira lista;
- classificação preliminar, alocação final e homologação da segunda lista;
- flag de evento fora do quadro publicado.

Quantidades de uma versão não são somadas a reapresentações de outra versão.

## 6. Regra econométrica congelada após A1

O outcome administrativo primário será binário por célula:

`1[alguma confirmação ou homologação observada na célula]`.

Quando as chamadas forem analisadas em conjunto, a especificação deverá manter
efeitos/indicadores de chamada e versão; não poderá tratar a segunda chamada
como simples continuação da capacidade numérica da primeira.

Permanecem proibidos até a obtenção de dados administrativos adicionais:

- taxa ou proporção de vagas preenchidas;
- candidaturas por vaga;
- tempo até preenchimento;
- reocupação de vaga;
- retenção individual do bolsista.

Contagens podem ser mostradas como descrição administrativa, mas não substituem
o outcome binário na análise principal.

## 7. Próximo portão

A2 está liberado para construir a tipologia territorial sem consultar outcomes.
A3 somente poderá congelar a pré-análise depois que essa tipologia estiver
completa. Nenhuma estimação de A4 foi realizada nesta sessão.

## 8. Reprodutibilidade

Executar:

```powershell
.\.venv\Scripts\python.exe scripts\tema_trabalho\02_reconciliar_funil_ciclo1.py
.\.venv\Scripts\python.exe -m unittest tests.test_reconciliacao_funil_ciclo1 -q
```

O script gera atomicamente a matriz e o JSON do portão. Os testes verificam
hashes indiretamente pela reprodução, contagens, unicidade, ausência de dados
pessoais, divergências de capacidade e linguagem permitida.
