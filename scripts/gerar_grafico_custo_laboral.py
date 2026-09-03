# -*- coding: utf-8 -*-
"""
Gera o gráfico didático do trade-off de volume clínico (q) sobre a utilidade médica.
Ilustra:
- Painel A: Cansaço C(q) com C'' > 0 vs. Realização moral alpha*B(q) com B'' < 0
- Painel B: Custo clínico líquido c(q) = C(q) - alpha*B(q) em formato de U, com c'' > 0
"""
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.8), dpi=300)

q = np.linspace(0, 50, 500)

# C(q): Cansaço convexo (C' > 0, C'' > 0)
C = 0.4 * q + 0.035 * (q ** 2)
dC = 0.4 + 0.07 * q

# alpha*B(q): Realização côncava (B' > 0, B'' < 0)
alpha_B = 3.0 * (1 - np.exp(-0.06 * q)) * 30
d_alpha_B = 3.0 * 0.06 * np.exp(-0.06 * q) * 30

# Custo clínico líquido: c(q) = C(q) - alpha*B(q)
c_net = C - alpha_B
dc_net = dC - d_alpha_B

idx_opt = np.argmin(c_net)
q_opt = q[idx_opt]
c_min = c_net[idx_opt]

# --- Painel 1: Decomposição ---
ax1.plot(q, C, label=r"Cansaço físico e mental $C(q)$ [$C''(q) > 0$]", color='#C0392B', lw=2.8)
ax1.plot(q, alpha_B, label=r"Realização / Dever cumprido $\alpha B(q)$ [$B''(q) < 0$]", color='#27AE60', lw=2.8)
ax1.axvline(q_opt, color='#7F8C8D', linestyle='--', lw=1.5, label=f'Volume ótimo ($q^* \\approx {q_opt:.1f}$)')
ax1.scatter([q_opt], [C[idx_opt]], color='#C0392B', s=60, zorder=5)
ax1.scatter([q_opt], [alpha_B[idx_opt]], color='#27AE60', s=60, zorder=5)

ax1.set_title('A. Decomposição do Esforço Médico: Cansaço vs. Realização', fontsize=12, fontweight='bold', pad=12)
ax1.set_xlabel('Volume de Atendimentos / Intensidade da Prática ($q$)', fontsize=11)
ax1.set_ylabel('Utilidade / Desutilidade de Esforço', fontsize=11)
ax1.legend(loc='upper left', frameon=True, fontsize=10)
ax1.grid(True, linestyle=':', alpha=0.6)

# --- Painel 2: Custo Clínico Líquido c(q) ---
ax2.plot(q, c_net, label=r'Custo clínico líquido $c(q) = C(q) - \alpha B(q)$', color='#1F4E79', lw=3.0)
ax2.axhline(0, color='black', linestyle='-', lw=1.0, alpha=0.7)
ax2.axvline(q_opt, color='#7F8C8D', linestyle='--', lw=1.5)
ax2.scatter([q_opt], [c_min], color='#E67E22', s=90, zorder=5, label=f'Custo mínimo ($q^* \\approx {q_opt:.1f}$)')

# Áreas sombreadas
ax2.axvspan(0, q_opt, alpha=0.12, color='#2ECC71', label='Zona Vocacional (Realização > Cansaço)')
ax2.axvspan(q_opt, 50, alpha=0.12, color='#E74C3C', label='Zona de Sobrecarga e Burnout (Cansaço > Realização)')

# Ajuste de limites no painel B para acomodar perfeitamente anotações e legendas
ax2.set_ylim(-48, 28)

# Anotações didáticas
ax2.annotate("$c'(q) < 0$\n(Dever cumprido domina)", 
             xy=(q_opt*0.5, c_min*0.55), xytext=(2, -35),
             arrowprops=dict(arrowstyle='->', color='#27AE60', lw=1.5),
             fontsize=10, color='#1E8449', fontweight='bold')

ax2.annotate("$c'(q) > 0$\n(Exaustão / Burnout)", 
             xy=(44, 8), xytext=(35, -5),
             arrowprops=dict(arrowstyle='->', color='#C0392B', lw=1.5),
             fontsize=10, color='#922B21', fontweight='bold', ha='center')

ax2.set_title(r"B. Custo Laboral Líquido em Formato de U [$c''(q) > 0$]", fontsize=12, fontweight='bold', pad=12)
ax2.set_xlabel('Volume de Atendimentos / Intensidade da Prática ($q$)', fontsize=11)
ax2.set_ylabel(r'Custo Não Pecuniário Líquido $c(q)$', fontsize=11)
ax2.legend(loc='upper left', frameon=True, fontsize=9.5, framealpha=0.9)
ax2.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
outpath = 'docs/02_teoria/figuras/curva_custo_laboral_burnout.png'
plt.savefig(outpath, bbox_inches='tight')
plt.close()
print(f'Grafico salvo com sucesso em: {outpath}')

