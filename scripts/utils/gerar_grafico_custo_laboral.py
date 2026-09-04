# -*- coding: utf-8 -*-
"""
Gera o gráfico didático em painel único do trade-off de volume clínico (q) sobre o custo laboral médico.
Decomposição teórica:
- Cansaço físico e mental C(q) (C' > 0, C'' > 0) [Vermelho]
- Satisfação moral e sensação de dever cumprido alpha*B(q) (B' > 0, B'' < 0) [Azul]
- Custo laboral líquido c(q) = C(q) - alpha*B(q) em formato de U [Roxo]

Pontos notáveis:
- q_{c_max}: ponto de satisfação líquida máxima / custo laboral mínimo (c' = 0)
- q_{c=0}: ponto onde cansaço e satisfação se igualam e o custo líquido se anula (c = 0, C = alpha*B)

Ilustração puramente conceitual e hipotética sem escala cardinal numérica.
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

fig, ax = plt.subplots(figsize=(11.8, 7.2), dpi=300)

q = np.linspace(0, 58, 600)

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

# Ponto notável q_zero onde c(q) = 0 (cruzamento C = alpha*B)
q_zero = float(np.interp(0, c_net[idx_opt:], q[idx_opt:]))
C_zero = float(np.interp(q_zero, q, C))

# Paleta semântica:
color_C = '#D32F2F'       # Cansaço: Vermelho
color_B = '#1976D2'       # Satisfação: Azul
color_c = '#7B1FA2'       # Custo líquido: Roxo
color_green = '#4CAF50'   # Zona 1: Verde clarinho
color_amber = '#FB8C00'   # Zona 2: Âmbar

# Áreas sombreadas das 3 zonas (Verde suave -> Âmbar suave -> Vermelho suave)
ax.axvspan(0, q_opt, alpha=0.08, color=color_green, zorder=0)
ax.axvspan(q_opt, q_zero, alpha=0.05, color=color_amber, zorder=0)
ax.axvspan(q_zero, 58, alpha=0.06, color=color_C, zorder=0)

# Linha neutra de referência (custo zero)
ax.axhline(0, color='#546E7A', linestyle='-', lw=1.2, alpha=0.6, zorder=1)

# Curvas principais
ax.plot(q, C, label=r"Cansaço: $C(q)$",
        color=color_C, lw=3.2, zorder=3)
ax.plot(q, alpha_B, label=r"Satisfação: $\alpha B(q)$",
        color=color_B, lw=3.2, zorder=3)
ax.plot(q, c_net, label=r"Custo líquido: $c^{\mathrm{laboral}}(q) = C(q) - \alpha B(q)$",
        color=color_c, lw=3.6, zorder=4)

# 1. Linhas e pontos de destaque em q_{c_max}
ax.plot([q_opt, q_opt], [c_min, alpha_B[idx_opt]], color='#616161', linestyle='--', lw=1.5, alpha=0.75, zorder=2)
ax.plot([q_opt, q_opt], [-48, c_min], color='#616161', linestyle=':', lw=1.2, alpha=0.6, zorder=2)

ax.scatter([q_opt], [C[idx_opt]], color=color_C, s=70, zorder=5)
ax.scatter([q_opt], [alpha_B[idx_opt]], color=color_B, s=70, zorder=5)
ax.scatter([q_opt], [c_min], color=color_c, s=120, zorder=6, edgecolors='white', linewidth=1.5)

# 2. Linhas e pontos de destaque em q_zero (c = 0, C = alpha*B)
ax.plot([q_zero, q_zero], [0, C_zero], color='#616161', linestyle='--', lw=1.5, alpha=0.75, zorder=2)
ax.plot([q_zero, q_zero], [-48, 0], color='#616161', linestyle=':', lw=1.2, alpha=0.6, zorder=2)

ax.scatter([q_zero], [C_zero], color=color_c, s=90, zorder=5, edgecolors='white', linewidth=1.5)
ax.scatter([q_zero], [0], color=color_c, s=110, zorder=6, edgecolors='white', linewidth=1.5)

# Rotulagem direta no final das curvas (direita) sem parênteses
ax.text(58.4, C[-1], 'Cansaço', color=color_C, fontsize=10.5, fontweight='bold', va='center')
ax.text(58.4, alpha_B[-1], 'Satisfação', color=color_B, fontsize=10.5, fontweight='bold', va='center')
ax.text(58.4, c_net[-1], 'Custo líquido', color=color_c, fontsize=10.5, fontweight='bold', va='center')

# Índices para anotação das caixas
q_mid1 = q_opt / 2.0
q_mid2 = (q_opt + q_zero) / 2.0
q_mid3 = (q_zero + 58) / 2.0

# --- Caixas didáticas sem setas ---

# 1. Região 1 (0 < q < q_{c_max})
ax.annotate(
    r"$\mathbf{c' < 0}$" + "\n" +
    "Utilidade laboral crescente",
    xy=(q_mid1, -11),
    ha='center',
    va='center',
    fontsize=8.8,
    color='#1B5E20',
    bbox=dict(boxstyle='round,pad=0.45', facecolor='#FFFFFF', edgecolor='#81C784', lw=1.4, alpha=0.98),
    zorder=7
)

# 2. Ponto Ótimo q_{c_max}
ax.annotate(
    r"$\mathbf{c' = 0}$" + "\n" +
    "Satisfação líquida máxima",
    xy=(q_opt, -18),
    ha='center',
    va='center',
    fontsize=8.8,
    color='#4A148C',
    fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.45', facecolor='#FFFFFF', edgecolor='#BA68C8', lw=1.5, alpha=0.98),
    zorder=7
)

# 3. Região 2 (q_{c_max} < q < q_zero)
ax.annotate(
    r"$\mathbf{c' > 0}$" + "\n" +
    "Utilidade laboral decrescente",
    xy=(q_mid2, -11),
    ha='center',
    va='center',
    fontsize=8.8,
    color='#E65100',
    bbox=dict(boxstyle='round,pad=0.45', facecolor='#FFFFFF', edgecolor='#FFB74D', lw=1.4, alpha=0.98),
    zorder=7
)

# 4. Região 3 (q > q_zero: c > 0)
ax.annotate(
    r"$\mathbf{c > 0}$" + "\n" +
    "Cansaço > Satisfação",
    xy=(q_mid3, -11),
    ha='center',
    va='center',
    fontsize=8.8,
    color='#B71C1C',
    bbox=dict(boxstyle='round,pad=0.45', facecolor='#FFEBEE', edgecolor='#EF9A9A', lw=1.4, alpha=0.98),
    zorder=7
)

# Configuração dos eixos SEM NÚMEROS (apenas q_{c_max}, q_{c=0} e 0)
ax.set_xticks([q_opt, q_zero])
ax.set_xticklabels([r'$\mathbf{q_{c_{max}}}$', r'$\mathbf{q_{c=0}}$'], fontsize=12.5, fontweight='bold')
ax.set_yticks([0])
ax.set_yticklabels(['0'], fontsize=12, fontweight='bold')

ax.set_xlim(0, 63)
ax.set_ylim(-48, 150)

ax.set_xlabel('Volume de Atendimentos: $q$',
              fontsize=13.5, fontweight='bold', labelpad=4)
ax.set_ylabel(r'Custo Laboral Líquido: $c^{\mathrm{laboral}}$',
              fontsize=13.5, fontweight='bold', labelpad=3)

# Título
ax.set_title('Ilustração do Modelo de Custo Laboral (Choné & Ma, 2011)',
             fontsize=14.0, fontweight='bold', pad=14)

# Legenda customizada com as 3 zonas
patch_reg1 = mpatches.Patch(facecolor=color_green, alpha=0.20,
                            label=r'Zona 1: Utilidade laboral crescente')
patch_reg2 = mpatches.Patch(facecolor=color_amber, alpha=0.15,
                            label=r'Zona 2: Utilidade laboral decrescente')
patch_reg3 = mpatches.Patch(facecolor=color_C, alpha=0.15,
                            label=r'Zona 3: Cansaço > Satisfação')

handles, labels = ax.get_legend_handles_labels()
all_handles = [handles[0], handles[1], handles[2], patch_reg1, patch_reg2, patch_reg3]
all_labels = [labels[0], labels[1], labels[2], patch_reg1.get_label(), patch_reg2.get_label(), patch_reg3.get_label()]

ax.legend(handles=all_handles, labels=all_labels, loc='upper left',
          frameon=True, framealpha=0.95, facecolor='#FFFFFF', edgecolor='#CFD8DC', fontsize=9.2)
ax.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()

ROOT = Path(__file__).resolve().parents[2]
outpath = ROOT / "docs" / "02_teoria" / "figuras" / "curva_custo_laboral_burnout.png"
outpath.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(str(outpath), bbox_inches='tight')
plt.close()
print(f'Grafico salvo com sucesso em: {outpath}')
