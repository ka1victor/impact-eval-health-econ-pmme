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

# Áreas sombreadas qualitativas
ax.axvspan(0, q_opt, alpha=0.06, color=color_B, zorder=0)
ax.axvspan(q_opt, 50, alpha=0.06, color=color_C, zorder=0)

# Linha neutra de referência (custo zero)
ax.axhline(0, color='#546E7A', linestyle='-', lw=1.2, alpha=0.6, zorder=1)

# Curvas principais
ax.plot(q, C, label=r"Cansaço e exaustão física/mental $C(q)$  [$C' > 0,\, C'' > 0$]",
        color=color_C, lw=3.2, zorder=3)
ax.plot(q, alpha_B, label=r"Satisfação e dever cumprido $\alpha B(q)$  [$B' > 0,\, B'' < 0$]",
        color=color_B, lw=3.2, zorder=3)
ax.plot(q, c_net, label=r"Custo laboral líquido $c^{\mathrm{laboral}}(q) = C(q) - \alpha B(q)$  [$c'' > 0$]",
        color=color_c, lw=3.6, zorder=4)

# Linha vertical tracejada no volume ótimo q* conectando pontos
ax.plot([q_opt, q_opt], [c_min, alpha_B[idx_opt]], color='#616161', linestyle='--', lw=1.5, alpha=0.75, zorder=2)
ax.plot([q_opt, q_opt], [-48, c_min], color='#616161', linestyle=':', lw=1.2, alpha=0.6, zorder=2)

# Pontos de destaque em q*
ax.scatter([q_opt], [C[idx_opt]], color=color_C, s=70, zorder=5)
ax.scatter([q_opt], [alpha_B[idx_opt]], color=color_B, s=70, zorder=5)
ax.scatter([q_opt], [c_min], color=color_c, s=120, zorder=6, edgecolors='white', linewidth=1.5)

# Rotulagem direta no final das curvas (direita)
ax.text(50.4, C[-1], r'$C(q)$' + '\n(Cansaço)', color=color_C, fontsize=9.5, fontweight='bold', va='center')
ax.text(50.4, alpha_B[-1], r'$\alpha B(q)$' + '\n(Satisfação)', color=color_B, fontsize=9.5, fontweight='bold', va='center')
ax.text(50.4, c_net[-1], r'$c^{\mathrm{laboral}}(q)$' + '\n(Custo líquido)', color=color_c, fontsize=9.5, fontweight='bold', va='center')

# Índices para anotação nas curvas
idx_q1 = np.argmin(np.abs(q - 8.0))
idx_q2 = np.argmin(np.abs(q - 34.0))

# --- Caixas didáticas posicionadas dentro do vão côncavo (opacas) ---

# 1. Região de Satisfação / Dever Cumprido (Esquerda)
ax.annotate(
    r"$\mathbf{c'(q) < 0}$" + "\n" +
    "Satisfação e dever cumprido\n" +
    "superam o cansaço inicial\n" +
    "(reduz o custo líquido)",
    xy=(q[idx_q1], c_net[idx_q1] + 2.5),
    xytext=(q[idx_q1], -11),
    ha='center',
    fontsize=8.8,
    color='#0D47A1',
    bbox=dict(boxstyle='round,pad=0.45', facecolor='#FFFFFF', edgecolor='#90CAF9', lw=1.4, alpha=0.98),
    arrowprops=dict(arrowstyle='->', color='#1976D2', lw=1.5),
    zorder=7
)

# 2. Ponto Ótimo q* (Centro)
ax.annotate(
    r"$\mathbf{q^*}$ (Mínimo Custo Laboral)" + "\n" +
    r"$C'(q^*) = \alpha B'(q^*)$" + "\n" +
    r"Equilíbrio marginal",
    xy=(q_opt, c_min + 3.0),
    xytext=(q_opt, -20),
    ha='center',
    fontsize=9.0,
    color='#4A148C',
    fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.42', facecolor='#FFFFFF', edgecolor='#BA68C8', lw=1.5, alpha=0.98),
    arrowprops=dict(arrowstyle='->', color='#7B1FA2', lw=1.8),
    zorder=7
)

# 3. Região de Cansaço / Exaustão (Direita)
ax.annotate(
    r"$\mathbf{c'(q) > 0}$" + "\n" +
    "Cansaço e exaustão superam\n" +
    "a satisfação marginal\n" +
    "(eleva o custo líquido)",
    xy=(q[idx_q2], c_net[idx_q2] + 2.5),
    xytext=(q[idx_q2], -11),
    ha='center',
    fontsize=8.8,
    color='#B71C1C',
    bbox=dict(boxstyle='round,pad=0.45', facecolor='#FFFFFF', edgecolor='#EF9A9A', lw=1.4, alpha=0.98),
    arrowprops=dict(arrowstyle='->', color='#D32F2F', lw=1.5),
    zorder=7
)

# Configuração dos eixos SEM NÚMEROS (ilustração puramente conceitual)
ax.set_xticks([q_opt])
ax.set_xticklabels([r'$\mathbf{q^*}$' + '\n(Volume de menor custo)'], fontsize=11.5)
ax.set_yticks([0])
ax.set_yticklabels([r'$c^{\mathrm{laboral}} = 0$' + '\n(Neutro)'], fontsize=9.5, fontweight='medium')

ax.set_xlim(0, 54.5)
ax.set_ylim(-48, 120)

ax.set_xlabel('Volume de Atendimentos / Intensidade da Prática Médica ($q$)',
              fontsize=12, fontweight='semibold', labelpad=8)
ax.set_ylabel(r'Custo Não Pecuniário Líquido $c^{\mathrm{laboral}}(q)$' + '\n' +
              r'(Desutilidade clínica líquida de atender $q$ pacientes: $C - \alpha B$)',
              fontsize=11.5, fontweight='semibold', labelpad=10)

# Título único (sem subtítulo, conforme solicitado)
ax.set_title('Ilustração do Modelo Teórico de Custo Laboral do Médico (Choné & Ma, 2011)',
             fontsize=13.5, fontweight='bold', pad=14)

# Legenda customizada
patch_reg1 = mpatches.Patch(facecolor=color_B, alpha=0.15,
                            label=r'Zona 1: Satisfação e dever cumprido dominam ($c\'(q) < 0$)')
patch_reg2 = mpatches.Patch(facecolor=color_C, alpha=0.15,
                            label=r'Zona 2: Cansaço e exaustão dominam ($c\'(q) > 0$)')

handles, labels = ax.get_legend_handles_labels()
all_handles = [handles[0], handles[1], handles[2], patch_reg1, patch_reg2]
all_labels = [labels[0], labels[1], labels[2], patch_reg1.get_label(), patch_reg2.get_label()]

ax.legend(handles=all_handles, labels=all_labels, loc='upper left',
          frameon=True, framealpha=0.95, facecolor='#FFFFFF', edgecolor='#CFD8DC', fontsize=9.6)
ax.grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()

ROOT = Path(__file__).resolve().parents[2]
outpath = ROOT / "docs" / "02_teoria" / "figuras" / "curva_custo_laboral_burnout.png"
outpath.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(str(outpath), bbox_inches='tight')
plt.close()
print(f'Grafico salvo com sucesso em: {outpath}')

