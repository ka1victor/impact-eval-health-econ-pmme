"""Intervalos exatos ao lado dos intervalos convencionais de A8 (item C-3).

Motivo. `A8_tabela_02` publica `ic95_convencional_superior = 1,2618` na linha
`2025_C1_CH2` de homologação. A diferença de duas proporções vive em `[-1, 1]`,
então esse limite está fora do espaço de parâmetros. A coluna já se chama
"convencional" e a seção 5 do relatório já diz que intervalos `t` não resolvem a
discretização da running variable, mas nada sinaliza **este** valor.

O que este script faz. Lê os artefatos de A8 já publicados e grava, num arquivo
próprio, o intervalo exato condicional ao lado do convencional, mais uma marca
explícita para cada linha cujo intervalo convencional saia de `[-1, 1]`.

O que este script **não** faz. Não reexecuta A8, não regrava nenhuma tabela de
A8 e não altera amostra, desfecho nem estimador. O intervalo convencional segue
publicado como está; o exato entra ao lado, não no lugar.

Método. Para dados binários pareados com `n` pares, `b` discordantes favoráveis
e `c` discordantes contrários, a diferença é `δ = (b - c) / n`. Condicionando
nos `m = b + c` pares discordantes, `b ~ Binomial(m, π)`. Com o intervalo exato
de Clopper–Pearson `[πL, πU]` para `π`, o intervalo para `δ` é
`[(2πL - 1)·m/n, (2πU - 1)·m/n]`, que por construção cabe em `[-m/n, m/n]` e
portanto nunca sai do espaço de parâmetros. É o análogo exato do teste de
McNemar já usado em `p_exato_pareado_bicaudal`, então as duas peças concordam
por construção.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from scipy import stats


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "tema_trabalho"

ESTIMATIVAS = OUT / "A8_tabela_02_estimativas_escore_estrito.csv"
PLACEBOS = OUT / "A8_tabela_03_placebos_escore_estrito.csv"
DESTINO = OUT / "A8_tabela_06_intervalos_exatos.csv"

ALFA = 0.05


def clopper_pearson(sucessos: int, tentativas: int, alfa: float = ALFA) -> tuple[float, float]:
    """Intervalo exato de Clopper–Pearson para uma proporção binomial."""
    if tentativas == 0:
        return (float("nan"), float("nan"))
    inferior = (
        0.0
        if sucessos == 0
        else float(stats.beta.ppf(alfa / 2, sucessos, tentativas - sucessos + 1))
    )
    superior = (
        1.0
        if sucessos == tentativas
        else float(stats.beta.ppf(1 - alfa / 2, sucessos + 1, tentativas - sucessos))
    )
    return (inferior, superior)


def intervalo_exato_pareado(
    n_pares: int, favoraveis: int, contrarios: int, alfa: float = ALFA
) -> tuple[float, float]:
    """Intervalo exato condicional para a diferença de proporções pareadas."""
    discordantes = favoraveis + contrarios
    if n_pares == 0:
        return (float("nan"), float("nan"))
    if discordantes == 0:
        # Sem par discordante não há informação sobre o sinal: a diferença é
        # exatamente zero e o intervalo condicional degenera nesse ponto.
        return (0.0, 0.0)
    pi_inferior, pi_superior = clopper_pearson(favoraveis, discordantes, alfa)
    escala = discordantes / n_pares
    return ((2 * pi_inferior - 1) * escala, (2 * pi_superior - 1) * escala)


def anotar(frame: pd.DataFrame, origem: str) -> pd.DataFrame:
    linhas = []
    for linha in frame.itertuples(index=False):
        inferior, superior = intervalo_exato_pareado(
            int(linha.n_pares),
            int(linha.discordantes_favoraveis),
            int(linha.discordantes_contrarios),
        )
        fora = bool(
            linha.ic95_convencional_superior > 1.0 or linha.ic95_convencional_inferior < -1.0
        )
        linhas.append(
            {
                "origem": origem,
                "ciclo_chamada": linha.ciclo_chamada,
                "amostra": linha.amostra,
                "desfecho": linha.desfecho,
                "n_pares": int(linha.n_pares),
                "diferenca": float(linha.diferenca),
                "discordantes_favoraveis": int(linha.discordantes_favoraveis),
                "discordantes_contrarios": int(linha.discordantes_contrarios),
                "ic95_convencional_inferior": float(linha.ic95_convencional_inferior),
                "ic95_convencional_superior": float(linha.ic95_convencional_superior),
                "ic95_convencional_fora_do_espaco": fora,
                "ic95_exato_inferior": inferior,
                "ic95_exato_superior": superior,
                "p_exato_pareado_bicaudal": float(linha.p_exato_pareado_bicaudal),
            }
        )
    return pd.DataFrame(linhas)


def main() -> None:
    partes = [
        anotar(pd.read_csv(ESTIMATIVAS), "A8_tabela_02"),
        anotar(pd.read_csv(PLACEBOS), "A8_tabela_03"),
    ]
    tabela = pd.concat(partes, ignore_index=True)

    fora = tabela["ic95_convencional_fora_do_espaco"]
    # O intervalo exato é o que respeita o espaço de parâmetros; se algum sair
    # de [-1, 1], é erro de implementação, não resultado.
    assert not tabela["ic95_exato_superior"].gt(1.0).any()
    assert not tabela["ic95_exato_inferior"].lt(-1.0).any()

    tmp = DESTINO.with_suffix(DESTINO.suffix + ".tmp")
    tabela.to_csv(tmp, index=False)
    tmp.replace(DESTINO)

    print(
        f"[OK] A8 intervalos exatos: {len(tabela)} linhas; "
        f"{int(fora.sum())} com intervalo convencional fora de [-1, 1]."
    )
    for linha in tabela[fora].itertuples(index=False):
        print(
            f"     {linha.ciclo_chamada} / {linha.desfecho}: "
            f"convencional ate {linha.ic95_convencional_superior:.4f}; "
            f"exato [{linha.ic95_exato_inferior:.4f}, {linha.ic95_exato_superior:.4f}]"
        )


if __name__ == "__main__":
    main()
