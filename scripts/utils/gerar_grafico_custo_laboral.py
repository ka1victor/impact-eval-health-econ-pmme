# -*- coding: utf-8 -*-
"""
Gera o gráfico didático em painel único do trade-off de volume clínico (q) sobre o custo laboral médico.
Decomposição teórica:
- Exaustão física e mental C(q) (C' > 0, C'' > 0) [Vermelho]
- Sensação de dever cumprido alpha*B(q) (B' > 0, B'' < 0) [Azul]
- Custo laboral líquido c(q) = C(q) - alpha*B(q) em formato de U [Roxo]

Ilustração puramente conceitual e hipotética sem escala cardinal numérica.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

fig, ax = plt.subplots(figsize=(11.5, 7.2), dpi=300)

q = np.linspace(0, 50, 500)

# C(q): Exaustão convexa (C' > 0, C'' > 0)
C = 0.4 * q + 0.035 * (q ** 2)
dC = 0.4 + 0.07 * q

# alpha*B(q): Sensação de dever cumprido côncava (B' > 0, B'' < 0)
alpha_B = 3.0 * (1 - np.exp(-0.06 * q)) * 30
d_alpha_B = 3.0 * 0.06 * np.exp(-0.06 * q) * 30

# Custo laboral líquido: c(q) = C(q) - alpha*B(q)
c_net = C - alpha_B
dc_net = dC - d_alpha_B

idx_opt = np.argmin(c_net)
q_opt = q[idx_opt]
c_min = c_net[idx_opt]

# Paleta semântica:
color_C = '#D32F2F'       # Exaustão: Vermelho
color_B = '#1976D2'       # Sensação de dever cumprido: Azul
color_c = '#7B1FA2'       # Custo laboral líquido: Roxo

# Linha neutra de referência (custo zero)
ax.axhline(0, color='#546E7A', linestyle='-', lw=1.2, alpha=0.6, zorder=1)
ax.text(1.2, 3.2, 'Linha de base neutra (custo líquido zero)',
        fontsize=9.5, color='#455A64', fontstyle='italic')

# Áreas sombreadas qualitativas
ax.axvspan(0, q_opt, alpha=0.06, color=color_B, zorder=0)
ax.axvspan(q_opt, 50, alpha=0.06, color=color_C, zorder=0)

# Curvas principais
ax.plot(q, C, label=r"Exaustão física e mental $C(q)$  [$C' > 0,\, C'' > 0$]",
        color=color_C, lw=3.2, zorder=3)
ax.plot(q, alpha_B, label=r"Sensação de dever cumprido $\alpha B(q)$  [$B' > 0,\, B'' < 0$]",
        color=color_B, lw=3.2, zorder=3)
ax.plot(q, c_net, label=r"Custo laboral líquido $c^{\mathrm{laboral}}(q) = C(q) - \alpha B(q)$  [$c'' > 0$]",
        color=color_c, lw=3.6, zorder=4)

# Linha vertical tracejada no volume ótimo q*
ax.axvline(q_opt, color='#616161', linestyle='--', lw=1.5, alpha=0.75, zorder=2)

# Pontos de destaque em q*
ax.scatter([q_opt], [C[idx_opt]], color=color_C, s=70, zorder=5)
ax.scatter([q_opt], [alpha_B[idx_opt]], color=color_B, s=70, zorder=5)
ax.scatter([q_opt], [c_min], color=color_c, s=120, zorder=6, edgecolors='white', linewidth=1.5)

# Rotulagem direta no final das curvas (direita)
ax.text(49.8, C[-1], r'  $C(q)$', color=color_C, fontsize=11, fontweight='bold', va='center')
ax.text(49.8, alpha_B[-1], r'  $\alpha B(q)$', color=color_B, fontsize=11, fontweight='bold', va='center')
ax.text(49.8, c_net[-1], r'  $c^{\mathrm{laboral}}(q)$', color=color_c, fontsize=11, fontweight='bold', va='center')

# --- Caixas didáticas perfeitamente posicionadas dentro do vão côncavo ---

# 1. Região de Dever Cumprido (Esquerda)
ax.annotate(
    r"$\mathbf{c'(q) < 0}$" + "\n" +
    "Sensação de dever cumprido supera\n" +
    "o cansaço inicial, reduzindo a desutilidade",
    xy=(q_opt * 0.45, -20),
    xytext=(q_opt * 0.45, -9),
    ha='center',
    fontsize=9.2,
    color='#0D47A1',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#E3F2FD', edgecolor='#90CAF9', alpha=0.95),
    arrowprops=dict(arrowstyle='->', color='#1976D2', lw=1.5),
    zorder=7
)

# 2. Ponto Ótimo q* (Centro)
ax.annotate(
    r"$\mathbf{q^*}$ (Mínimo Custo Laboral)" + "\n" +
    r"$C'(q^*) = \alpha B'(q^*)$" + "\n" +
    r"Equilíbrio marginal perfeito",
    xy=(q_opt, c_min),
    xytext=(q_opt, -25),
    ha='center',
    fontsize=9.5,
    color='#4A148C',
    fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#F3E5F5', edgecolor='#BA68C8', alpha=0.95),
    arrowprops=dict(arrowstyle='->', color='#7B1FA2', lw=1.8),
    zorder=7
)

# 3. Região de Exaustão (Direita)
ax.annotate(
    r"$\mathbf{c'(q) > 0}$" + "\n" +
    "Exaustão física e mental cresce rápido\n" +
    "e sobrecarrega a prática clínica",
    xy=(35, -20),
    xytext=(35, -9),
    ha='center',
    fontsize=9.2,
    color='#B71C1C',
    bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFEBEE', edgecolor='#EF9A9A', alpha=0.95),
    arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5),
    zorder=7
)

# Configuração dos eixos SEM NÚMEROS (ilustração teórica conceitual)
ax.set_xticks([q_opt])
ax.set_xticklabels([r'$\mathbf{q^*}$' + '\n(Volume com menor custo)'], fontsize=12)
ax.set_yticks([])  # Nenhum número no eixo Y

ax.set_xlim(0, 52)
ax.set_ylim(-48, 120)

ax.set_xlabel('Volume de Atendimentos / Intensidade da Prática Médica ($q$)',
              fontsize=12, fontweight='semibold', labelpad=8)
ax.set_ylabel('Impacto no Bem-Estar / Custo Não Pecuniário',
              fontsize=12, fontweight='semibold', labelpad=10)

# Título e subtítulo
ax.set_title('Modelo Teórico de Custo Laboral do Médico (Choné & Ma, 2011)',
             fontsize=14, fontweight='bold', pad=22)
ax.text(0.5, 1.018, 'Ilustração Teórica Hipotética — Sem Escala Cardinal Numérica',
        transform=ax.transAxes, ha='center', fontsize=10.5, color='#555555', fontstyle='italic')

# Legenda customizada
patch_reg1 = mpatches.Patch(facecolor=color_B, alpha=0.15,
                            label=r'Zona 1: Sensação de dever cumprido domina ($c\'(q) < 0$)')
patch_reg2 = mpatches.Patch(facecolor=color_C, alpha=0.15,
                            label=r'Zona 2: Exaustão domina ($c\'(q) > 0$)')

handles, labels = ax.get_legend_handles_labels()
all_handles = [handles[0], handles[1], handles[2], patch_reg1, patch_reg2]
all_labels = [labels[0], labels[1], labels[2], patch_reg1.get_label(), patch_reg2.get_label()]

ax.legend(handles=all_handles, labels=all_labels, loc='upper left',
          frameon=True, framealpha=0.93, fontsize=9.8)
ax.grid(True, linestyle=':', alpha=0.5)

# Nota de rodapé explicativa
fig.text(0.5, 0.015,
         r"* Nota teórica: $C(q)$ [vermelho] denota a exaustão acumulada estritamente convexa; $\alpha B(q)$ [azul] reflete o dever cumprido côncavo;" + "\n" +
         r"o custo laboral líquido $c(q)$ [roxo] assume formato em U com mínimo estrito em $q^*$, onde o dever cumprido marginal equilibra a exaustão marginal.",
         ha='center', fontsize=8.8, color='#555555')

plt.tight_layout(rect=[0, 0.045, 1, 0.96])

ROOT = Path(__file__).resolve().parents[2]
outpath = ROOT / "docs" / "02_teoria" / "figuras" / "curva_custo_laboral_burnout.png"
outpath.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(str(outpath), bbox_inches='tight')
plt.close()
print(f'Grafico salvo com sucesso em: {outpath}')

