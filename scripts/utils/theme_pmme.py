"""theme_pmme.py — Sistema de Design Visual Editorial para o PMM-E (Lei 15.233/2025).

Este módulo padroniza a paleta de cores corporativa, a tipografia, os espaçamentos
em pontos físicos e as anotações editoriais em todas as figuras do projeto de
avaliação de impacto do Programa Mais Médicos Especialistas.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import FancyBboxPatch, Rectangle


class PMMEPalette:
    """Paleta editorial elegante para Economia da Saúde e Recursos Humanos em Saúde."""
    # Neutros e Tipografia
    PRIMARY_NAVY = '#0F172A'      # Slate 900 — Títulos principais e eixos
    TEXT_DARK = '#1E293B'         # Slate 800 — Corpo e anotações
    SUBTITLE_SLATE = '#334155'    # Slate 700 — Subtítulos (10.2pt)
    MUTED_GRAY = '#64748B'        # Slate 500 — Textos auxiliares e placebos
    LIGHT_GRAY = '#E2E8F0'        # Slate 200 — Linhas divisórias e bordas
    BG_LIGHT = '#F8FAFC'          # Slate 50 — Fundos de cards e painéis
    GRID_COLOR = '#F1F5F9'        # Slate 100 — Linhas de grade sutis
    
    # Cores Semânticas de Política Pública e Tratamento
    ACCENT_BLUE = '#2563EB'       # Blue 600 — Modalidade Imediata / Tratamento Principal
    ACCENT_CRIMSON = '#E11D48'    # Rose 600 — Cadastro de Reserva / Choque / Alertas
    ACCENT_TEAL = '#0D9488'       # Teal 600 — Estabelecimento Ofertante / Saneamento
    ACCENT_EMERALD = '#059669'    # Emerald 600 — Retenção / Ganhos de Fixação
    ACCENT_PURPLE = '#7C3AED'     # Purple 600 — Especialidades / Retorno Social
    ACCENT_AMBER = '#D97706'      # Amber 600 — Transição / Atenção
    PLACEBO = '#94A3B8'           # Slate 400 — Placebos e Controles


def pt_to_y(pt: float, fig_h: float) -> float:
    """Converte pontos tipográficos (pt) em fração da altura da figura."""
    return pt / (72.0 * fig_h)


def setup_editorial_theme() -> None:
    """Aplica configurações globais de estilo limpo e editorial ao Matplotlib."""
    plt.rcParams.update({
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif'],
        'font.family': 'sans-serif',
        'text.color': PMMEPalette.TEXT_DARK,
        'axes.labelcolor': PMMEPalette.TEXT_DARK,
        'xtick.color': PMMEPalette.MUTED_GRAY,
        'ytick.color': PMMEPalette.MUTED_GRAY,
        'axes.edgecolor': PMMEPalette.LIGHT_GRAY,
        'axes.linewidth': 0.85,
        'axes.facecolor': '#FFFFFF',
        'figure.facecolor': '#FFFFFF',
        'grid.color': PMMEPalette.GRID_COLOR,
        'grid.linestyle': '-',
        'grid.linewidth': 0.75,
        'grid.alpha': 0.9,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'xtick.major.size': 3.5,
        'ytick.major.size': 3.5,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'figure.autolayout': False,
    })


def add_editorial_header(
    fig: plt.Figure,
    title: str,
    subtitle: str | None = None,
    kicker: str | None = None,
    x: float = 0.06,
    y_top: float = 0.97
) -> None:
    """Adiciona cabeçalho com espaçamento físico milimétrico e hierarquia tipográfica.
    
    - Kicker: 8.2pt negrito em Rose/Crimson
    - Título: 12.8pt a 13.8pt negrito em Slate 900
    - Subtítulo: 10.2pt em Slate 700 (#334155) com espaçamento exato de 18pt
    """
    fig_h = fig.get_size_inches()[1]
    curr_y = y_top
    
    if kicker:
        fig.text(
            x, curr_y,
            kicker.upper(),
            fontsize=8.2,
            fontweight='bold',
            color=PMMEPalette.ACCENT_CRIMSON,
            ha='left',
            va='top'
        )
        curr_y -= pt_to_y(15.0, fig_h)
        
    fig.text(
        x, curr_y,
        title,
        fontsize=13.0,
        fontweight='bold',
        color=PMMEPalette.PRIMARY_NAVY,
        ha='left',
        va='top'
    )
    
    if subtitle:
        curr_y -= pt_to_y(18.0, fig_h)
        fig.text(
            x, curr_y,
            subtitle,
            fontsize=10.2,
            fontweight='normal',
            color=PMMEPalette.SUBTITLE_SLATE,
            ha='left',
            va='top'
        )


def add_editorial_footer(
    fig: plt.Figure,
    source: str,
    notes: str | None = None,
    x: float = 0.06,
    y_bottom: float = 0.022
) -> None:
    """Adiciona rodapé editorial padronizado com fonte oficial e notas metodológicas."""
    footer_text = f"Fonte: {source}"
    if notes:
        footer_text += f" | Notas: {notes}"
        
    fig.text(
        x, y_bottom,
        footer_text,
        fontsize=7.8,
        color=PMMEPalette.MUTED_GRAY,
        ha='left',
        va='bottom'
    )
