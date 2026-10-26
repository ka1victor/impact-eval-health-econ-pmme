# Banca final — conteúdo canônico

> **Estado:** rascunho de proposta, pedido do grupo de 26/10/2026. A banca final
> ainda não tem roteiro; este diretório guarda só o que já foi pedido: o
> diagrama causal e a reorganização dos slides de teoria.<br>
> **Pedido do grupo:** "incluir diagrama causal/teoria da mudança pra explicar
> melhor a teoria econômica (deixar slide de equações como apêndice)".<br>
> **Não é a banca 2.** A banca 2 (28/10 e 04/11/2026) tem o seu próprio
> conteúdo em [`../banca2/`](../banca2/README.md).

## Índice

| Documento | Função |
|---|---|
| [`01_diagrama_teoria_mudanca.md`](01_diagrama_teoria_mudanca.md) | **fonte de verdade**: cada caixa e seta do diagrama, a literatura de cada elo, a ligação com as equações do apêndice e a nova ordem dos slides de teoria |

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

O diagrama é teoria e hipótese. Não traz número de resultado nem diz que a bolsa
"funciona" ou "não funciona".

Para regerar (o deck do grupo fica fora do repositório):

```bash
python3 scripts/apresentacao/gerar_diagrama_banca_final.py --deck "<caminho do deck do grupo>"
python3 scripts/apresentacao/gerar_diagrama_banca_final.py --atualizar-doc   # bloco gerado do doc 01
python3 -m pytest -q tests/test_diagrama_banca_final.py
```
