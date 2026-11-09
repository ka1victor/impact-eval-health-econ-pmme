# Banca final — conteúdo canônico

> **Estado (09/11/2026):** deck da banca final, versão 2 (proposta), 23 slides: a
> parte da banca 1 (motivação e teoria) ajustada pelo feedback da banca de 04/11,
> o deck da banca 2 revisto depois dessa banca (doc 12 da banca 2) e o apêndice de
> teoria ([02](02_deck_banca_final.md); `output/apresentacao_banca_final/deck_banca_final.pptx`
> e `.pdf`). Ainda sem roteiro de fala para a parte da banca 1; em aberto no doc 02, §4.<br>
> **Antes (26/10/2026):** rascunho com o diagrama causal e a reorganização dos
> slides de teoria (doc 01), que o deck final usa.<br>
> **Pedido do grupo:** "incluir diagrama causal/teoria da mudança pra explicar
> melhor a teoria econômica (deixar slide de equações como apêndice)".<br>
> **Não é a banca 2.** A banca 2 (28/10 e 04/11/2026) tem o seu próprio
> conteúdo em [`../banca2/`](../banca2/README.md).

## Índice

| Documento | Função |
|---|---|
| [`01_diagrama_teoria_mudanca.md`](01_diagrama_teoria_mudanca.md) | **fonte de verdade**: cada caixa e seta do diagrama, a literatura de cada elo, a ligação com as equações do apêndice e a nova ordem dos slides de teoria |
| [`02_deck_banca_final.md`](02_deck_banca_final.md) | **fonte de verdade do deck final**: ordem dos 23 slides, o feedback de 04/11 aplicado à parte da banca 1, cada texto novo e o que fica para o autor decidir |

## Derivados (o deck é derivado deste conteúdo)

Gerados por
[`scripts/apresentacao/gerar_diagrama_banca_final.py`](../../../scripts/apresentacao/gerar_diagrama_banca_final.py)
em [`output/apresentacao_banca_final/`](../../../output/apresentacao_banca_final/):

| Arquivo | O que é |
|---|---|
| `slides_diagrama_teoria_mudanca.pptx` | os 2 slides novos, no template do deck do grupo, em formas nativas editáveis |
| `deck_proposta_reorganizada.pptx` | o deck do grupo com o diagrama na seção de teoria e os slides de equações no apêndice (**proposta**; o deck original não é alterado) |
| `manifesto_diagrama.json` | SHA-256 do deck de entrada e das saídas, ordem dos slides |
| `qa_render/` | imagens dos 2 slides novos, só para conferência visual |
| `deck_banca_final.pptx` e `.pdf` | **o deck da banca final** (doc 02), gerado por `scripts/apresentacao/gerar_deck_banca_final.py` a partir do `deck_proposta_reorganizada.pptx` e do deck pós-banca da banca 2; manifesto em `manifesto_deck_banca_final.json` |

O diagrama é teoria e hipótese. Não traz número de resultado nem diz que a bolsa
"funciona" ou "não funciona".

Para regerar (o deck do grupo fica fora do repositório):

```bash
python3 scripts/apresentacao/gerar_diagrama_banca_final.py --deck "<caminho do deck do grupo>"
python3 scripts/apresentacao/gerar_diagrama_banca_final.py --atualizar-doc   # bloco gerado do doc 01
python3 -m pytest -q tests/test_diagrama_banca_final.py
```

Deck final (não precisa do deck do grupo; lê só de `output/`):

```bash
python3 scripts/apresentacao/gerar_deck_banca_final.py
python3 -m unittest tests.test_deck_banca_final
```
