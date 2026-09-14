"""Verificação do ambiente de execução exigido pelo repositório.

Motivo: o `requirements.txt` fixa `numpy==2.5.2` e `pandas==3.0.5`, que exigem
Python 3.12 ou superior. Rodar o pipeline sob um interpretador com versões
diferentes não levanta erro: os scripts terminam com sucesso e a suíte passa,
mas as saídas divergem a partir da 14ª casa decimal. Como a proveniência do
projeto é ancorada em SHA-256 de arquivo, essa divergência silenciosa reescreve
artefatos e quebra a cadeia de hashes sem que nada avise.

Verificado em 14/09/2026: sob o ambiente documentado, `05_estimar_atracao.py`
reexecuta sem alterar um único byte. Sob Python 3.11 com numpy 2.4.6, reescreve
doze arquivos. As conclusões não mudam, mas os artefatos sim.

Uso:

- `verificar_ambiente(estrito=True)` em etapa que **grava** artefato: aborta.
- `verificar_ambiente(estrito=False)` em etapa que apenas **lê**: avisa.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = ROOT / "requirements.txt"

PYTHON_MINIMO = (3, 12)

# Pacotes cuja versão altera o resultado numérico gravado em disco.
PACOTES_CRITICOS = ("numpy", "pandas", "statsmodels", "scipy")


def _versoes_fixadas() -> dict[str, str]:
    """Lê do requirements.txt as versões fixadas com `==`."""
    fixadas: dict[str, str] = {}
    if not REQUIREMENTS.exists():
        return fixadas
    for linha in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        casamento = re.match(r"^([A-Za-z0-9_.\-]+)==([^\s;]+)", linha)
        if casamento:
            fixadas[casamento.group(1).lower()] = casamento.group(2)
    return fixadas


def _versao_instalada(pacote: str) -> str | None:
    try:
        from importlib.metadata import PackageNotFoundError, version
    except ImportError:  # pragma: no cover
        return None
    try:
        return version(pacote)
    except PackageNotFoundError:
        return None


def divergencias() -> list[str]:
    """Lista, em português, cada divergência entre o ambiente e o exigido."""
    problemas: list[str] = []

    if sys.version_info < PYTHON_MINIMO:
        exigido = ".".join(str(n) for n in PYTHON_MINIMO)
        atual = ".".join(str(n) for n in sys.version_info[:3])
        problemas.append(
            f"Python {atual} é anterior ao mínimo exigido ({exigido} ou superior)"
        )

    fixadas = _versoes_fixadas()
    for pacote in PACOTES_CRITICOS:
        esperada = fixadas.get(pacote)
        if esperada is None:
            continue
        instalada = _versao_instalada(pacote)
        if instalada is None:
            problemas.append(f"{pacote} não está instalado; requirements fixa {esperada}")
        elif instalada != esperada:
            problemas.append(
                f"{pacote} {instalada} instalado, mas requirements fixa {esperada}"
            )

    return problemas


def _mensagem(problemas: list[str], estrito: bool) -> str:
    cabecalho = (
        "AMBIENTE INCOMPATÍVEL — a execução foi interrompida."
        if estrito
        else "AMBIENTE INCOMPATÍVEL — apenas aviso, a execução segue."
    )
    linhas = [
        "=" * 70,
        cabecalho,
        "=" * 70,
        "",
        "Divergências encontradas:",
    ]
    linhas += [f"  - {p}" for p in problemas]
    linhas += [
        "",
        "Por que isso importa: versões diferentes das fixadas produzem saídas",
        "que divergem a partir da 14ª casa decimal. Como a proveniência do",
        "projeto é ancorada em SHA-256 de arquivo, gravar artefato sob outro",
        "ambiente reescreve arquivos e quebra a cadeia de hashes em silêncio.",
        "",
        "Como montar o ambiente documentado, a partir da raiz do repositório:",
        "",
        "    python3.13 -m venv .venv",
        "    .venv/bin/pip install -r requirements.txt",
        "    .venv/bin/python <comando>",
        "",
        "Detalhe na seção 'Ambiente' do README.md.",
        "=" * 70,
    ]
    return "\n".join(linhas)


def verificar_ambiente(estrito: bool = True) -> list[str]:
    """Confere o ambiente.

    Com `estrito=True`, aborta o processo quando há divergência. Com
    `estrito=False`, imprime aviso em stderr e devolve a lista de problemas.
    """
    problemas = divergencias()
    if not problemas:
        return problemas

    print(_mensagem(problemas, estrito), file=sys.stderr)
    if estrito:
        raise SystemExit(1)
    return problemas


__all__ = ["verificar_ambiente", "divergencias", "PYTHON_MINIMO", "PACOTES_CRITICOS"]
