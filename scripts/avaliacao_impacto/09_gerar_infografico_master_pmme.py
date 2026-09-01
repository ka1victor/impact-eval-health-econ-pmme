"""09_gerar_infografico_master_pmme.py — Painel de diagnóstico do PMM-E.

Gera a figura infográfica master (figura_master_infografico_pmme.png) que sintetiza
em um único dashboard de padrão editorial os 4 KPIs executivos e as 4 dimensões
analíticas da comparação ajustada do Programa Mais Médicos Especialistas:
1. Dinâmica Temporal do Estudo de Evento DDD
2. Diagnóstico de Redistribuição (Município vs. Estabelecimento)
3. Trajetória Temporal Bruta por Modalidade
4. Fluxos cadastrados e presença posterior entre entrantes
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[2] / ".matplotlib-cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT / "scripts" / "utils"))
from theme_pmme import PMMEPalette, setup_editorial_theme, add_editorial_header, add_editorial_footer
from model_utils import atomic_savefig


OUT = ROOT / "output" / "avaliacao_impacto"
MODELS = OUT / "modelos"
TABLES = OUT / "tabelas"
FIGURES = OUT / "figuras"
PANEL = OUT / "dados" / "painel_municipio_curso_mes.parquet"


def main() -> None:
    setup_editorial_theme()
    FIGURES.mkdir(parents=True, exist_ok=True)

    # 1. Carregar Dados de Modelos e Painel
    with open(MODELS / "resultados_ddd_estatica.json", "r", encoding="utf-8") as f:
        ddd_res = json.load(f)
    with open(MODELS / "resultados_estudo_evento.json", "r", encoding="utf-8") as f:
        event_res = json.load(f)
    with open(MODELS / "resultados_robustez_e_redistribuicao.json", "r", encoding="utf-8") as f:
        robust_res = json.load(f)

    df_event = pd.read_csv(TABLES / "tabela_estudo_evento_dinamico.csv")
    df = pd.read_parquet(PANEL)
    df_conf = df[df["amostra_confirmatoria"] & df["within_muni_var_confirmatoria"]].copy()
    n_cells = int(df_conf[["co_ibge_6d", "cod_curso"]].drop_duplicates().shape[0])
    n_municipalities = int(df_conf["co_ibge_6d"].nunique())

    # 2. Configurar Canvas Master
    fig = plt.figure(figsize=(14.2, 10.5), dpi=300)
    gs = fig.add_gridspec(3, 2, height_ratios=[0.75, 1.25, 1.25], hspace=0.38, wspace=0.22)

    # Kicker, Título e Subtítulo
    add_editorial_header(
        fig,
        title="DIAGNÓSTICO DE IMPLEMENTAÇÃO DO MAIS MÉDICOS ESPECIALISTAS (PMM-E)",
        subtitle="Comparações ajustadas e descritivas do ciclo 1; não constituem efeito causal do programa",
        kicker="ECONOMIA DA SAÚDE & EVIDÊNCIA EM CONSTRUÇÃO",
        x=0.06,
        y_top=0.980
    )

    # 3. 4 Cards de KPI Executivo no Topo
    kpis = [
        ("–0,446 Médico", "Diferença DDD Ajustada", f"IC 95%: [–0,934; +0,042]\n(p = 0,0727; {n_cells} células)", '#EFF6FF', '#1E40AF', '#93C5FD'),
        ("+2,79 p.p.", "Alocação Confirmada", "Primeiro estágio impreciso\n(p = 0,687; F = 0,16)", '#FFF1F2', '#9F1239', '#FDA4AF'),
        ("86,9% vs 79,7%", "Presença aos 6 Meses", "Entre entrantes; estatística descritiva\n(Imediata | Reserva)", '#ECFDF5', '#065F46', '#6EE7B7'),
        (f"{n_cells} Células", "Amostra da DDD", f"26 competências mensais\n{n_municipalities} municípios", '#FAF5FF', '#6B21A8', '#D8B4FE')
    ]

    gs_top = gs[0, :].subgridspec(1, 4, wspace=0.15)
    for col, (val, title, desc, bg, txt_c, brd) in enumerate(kpis):
        ax_kpi = fig.add_subplot(gs_top[0, col])
        ax_kpi.set_axis_off()
        rect = Rectangle((0.02, 0.04), 0.96, 0.92, facecolor=bg, edgecolor=brd, linewidth=1.1, transform=ax_kpi.transAxes)
        ax_kpi.add_patch(rect)
        ax_kpi.text(0.5, 0.70, val, fontsize=17.0, fontweight='bold', color=txt_c, ha='center', va='center', transform=ax_kpi.transAxes)
        ax_kpi.text(0.5, 0.40, title, fontsize=8.6, fontweight='bold', color=PMMEPalette.PRIMARY_NAVY, ha='center', va='center', transform=ax_kpi.transAxes)
        ax_kpi.text(0.5, 0.18, desc, fontsize=7.4, color='#475569', ha='center', va='center', transform=ax_kpi.transAxes)

    # --- SUBPLOT 1 (TOP-LEFT): ESTUDO DE EVENTO DDD ---
    ax1 = fig.add_subplot(gs[1, 0])
    x_ev = np.arange(len(df_event))
    trans_idx = int(df_event.index[df_event["competencia"] == 202507][0])
    ax1.axvspan(trans_idx - 0.5, len(df_event) - 0.5, color='#F0F7FF', alpha=0.75, zorder=0)
    ax1.axhline(0, color=PMMEPalette.PRIMARY_NAVY, linewidth=0.8, alpha=0.7, zorder=2)
    ax1.axvline(trans_idx, color=PMMEPalette.ACCENT_CRIMSON, linestyle='--', linewidth=1.2, zorder=2)

    ax1.errorbar(
        x_ev, df_event["beta"],
        yerr=[df_event["beta"] - df_event["ci_95_inferior"], df_event["ci_95_superior"] - df_event["beta"]],
        fmt="o", color=PMMEPalette.ACCENT_BLUE, ecolor='#3B82F6', elinewidth=1.1, capsize=3.0, capthick=1.0,
        markersize=4.2, markeredgecolor='white', markeredgewidth=0.7, zorder=4
    )
    ax1.set_title("1. Diferença Ajustada Dinâmica: Estudo de Evento DDD", fontsize=9.8, fontweight='bold', pad=8)
    ax1.set_ylabel("Diferença no Estoque", fontsize=8.8)
    ax1.set_xticks(x_ev[::3])
    labs_ev = [f"{str(m)[:4]}-{str(m)[4:]}" for m in df_event["competencia"][::3]]
    ax1.set_xticklabels(labs_ev, fontsize=7.8, fontweight='bold')
    ax1.set_ylim(-2.35, 1.10)
    ax1.grid(True, axis='y')
    ax1.text(3.5, 0.75, "Coeficientes pré:\nF = 1,262 (p = 0,2546)\nNão prova paralelismo", fontsize=7.3, color='#334155', ha='center', va='top',
             bbox=dict(boxstyle='square,pad=0.25', facecolor='#F8FAFC', edgecolor='#CBD5E1', lw=0.8), zorder=5)

    # --- SUBPLOT 2 (TOP-RIGHT): DIAGNÓSTICO DE REDISTRIBUIÇÃO ---
    ax2 = fig.add_subplot(gs[1, 1])
    geo = [r for r in robust_res["modelos"] if r["grupo_analise"] == "Escala geográfica"]
    y_geo = np.arange(len(geo))
    b_geo = np.array([r["beta"] for r in geo])
    l_geo = np.array([r["ci_95"][0] for r in geo])
    h_geo = np.array([r["ci_95"][1] for r in geo])

    ax2.axhspan(-0.5, 0.5, color='#EFF6FF', alpha=0.6, zorder=0)
    ax2.axhspan(0.5, 1.5, color='#F0FDFA', alpha=0.6, zorder=0)
    ax2.axvline(0, color=PMMEPalette.PRIMARY_NAVY, linewidth=0.8, alpha=0.7, zorder=2)

    c_geo = [PMMEPalette.ACCENT_BLUE, PMMEPalette.ACCENT_TEAL]
    for i in range(len(geo)):
        ax2.errorbar(
            b_geo[i], y_geo[i], xerr=[[b_geo[i] - l_geo[i]], [h_geo[i] - b_geo[i]]],
            fmt="o", color=c_geo[i], ecolor=c_geo[i], elinewidth=1.4, capsize=3.8, capthick=1.1,
            markersize=5.8, markeredgecolor='white', markeredgewidth=0.8, zorder=4
        )
        txt = f"{b_geo[i]:+.3f}  [IC: {l_geo[i]:.2f}; {h_geo[i]:.2f}]".replace('.', ',')
        pos_x = max(h_geo[i] + 0.08, 0.08)
        ax2.text(pos_x, y_geo[i], txt, ha='left', va='center', fontsize=7.8, fontweight='bold', color=c_geo[i],
                 bbox=dict(boxstyle='square,pad=0.18', facecolor='white', edgecolor='none', alpha=0.92), zorder=5)

    ax2.set_title("2. Diagnóstico de Escala: Estabelecimento vs. Município", fontsize=9.8, fontweight='bold', pad=8)
    ax2.set_yticks(y_geo)
    ax2.set_yticklabels(["Município\nCompleto (DDD)", "Estabelecimento\nOfertante"], fontsize=8.0, fontweight='bold')
    ax2.set_xlabel("Diferença Estimada no Estoque", fontsize=8.8)
    ax2.set_xlim(-1.60, 1.15)
    ax2.set_ylim(-0.6, 1.6)
    ax2.grid(True, axis='x')

    # --- SUBPLOT 3 (BOTTOM-LEFT): TRAJETÓRIAS BRUTAS POR MODALIDADE ---
    ax3 = fig.add_subplot(gs[2, 0])
    trajectory = df_conf.groupby(["competencia", "modalidade_ms"])["especialistas_mst"].mean().unstack()
    x_tr = np.arange(len(trajectory))
    trans_tr = list(trajectory.index).index("202507")
    ax3.axvspan(trans_tr - 0.5, len(trajectory) - 0.5, color='#F0F7FF', alpha=0.75, zorder=0)
    ax3.axvline(trans_tr, color=PMMEPalette.ACCENT_CRIMSON, linestyle='--', linewidth=1.2, zorder=2)

    ax3.plot(x_tr, trajectory["IMEDIATA"], marker="o", color=PMMEPalette.ACCENT_BLUE, linewidth=1.8,
             markersize=4.2, markeredgecolor='white', markeredgewidth=0.7, label="Vagas Imediatas", zorder=4)
    ax3.plot(x_tr, trajectory["RESERVA"], marker="s", color=PMMEPalette.ACCENT_CRIMSON, linestyle="--", linewidth=1.6,
             markersize=4.2, markeredgecolor='white', markeredgewidth=0.7, label="Cadastro Reserva", zorder=4)
    ax3.set_title("3. Trajetória Temporal Bruta por Modalidade de Oferta", fontsize=9.8, fontweight='bold', pad=8)
    ax3.set_ylabel("Média de Médicos por Célula", fontsize=8.8)
    ax3.set_xticks(x_tr[::3])
    labs_tr = [f"{m[:4]}-{m[4:]}" for m in trajectory.index[::3]]
    ax3.set_xticklabels(labs_tr, fontsize=7.8, fontweight='bold')
    ax3.set_ylim(6.2, 13.5)
    ax3.grid(True, axis='y')
    ax3.legend(loc='lower left', fontsize=7.8, framealpha=0.95, edgecolor=PMMEPalette.LIGHT_GRAY)

    # --- SUBPLOT 4 (BOTTOM-RIGHT): DECOMPOSIÇÃO DE FLUXOS E RETENÇÃO ---
    ax4 = fig.add_subplot(gs[2, 1])
    means_fl = (
        df_conf.groupby(["competencia", "modalidade_ms"], as_index=False)
        .agg(entradas=("n_entradas_6m", "mean"), saidas=("n_saidas_confirmadas_3m", "mean"))
    )
    part_im = means_fl[means_fl["modalidade_ms"] == "IMEDIATA"].sort_values("competencia")
    part_re = means_fl[means_fl["modalidade_ms"] == "RESERVA"].sort_values("competencia")

    ax4.plot(x_tr, part_im["entradas"], color=PMMEPalette.ACCENT_EMERALD, linewidth=1.8, label="Entradas (Imediata)", zorder=4)
    ax4.plot(x_tr, part_im["saidas"], color=PMMEPalette.ACCENT_CRIMSON, linestyle="--", linewidth=1.6, label="Saídas (Imediata)", zorder=4)
    ax4.plot(x_tr, part_re["entradas"], color='#94A3B8', linestyle=':', linewidth=1.4, label="Entradas (Reserva)", zorder=3)
    ax4.plot(x_tr, part_re["saidas"], color='#CBD5E1', linestyle='-.', linewidth=1.4, label="Saídas (Reserva)", zorder=3)

    ax4.set_title("4. Fluxos Cadastrados e Presença Posterior", fontsize=9.8, fontweight='bold', pad=8)
    ax4.set_ylabel("Média de Fluxos por Célula", fontsize=8.8)
    ax4.set_xticks(x_tr[::3])
    ax4.set_xticklabels(labs_tr, fontsize=7.8, fontweight='bold')
    ax4.set_ylim(-0.02, 0.46)
    ax4.grid(True, axis='y')
    ax4.legend(loc='upper left', fontsize=7.5, framealpha=0.95, edgecolor=PMMEPalette.LIGHT_GRAY, ncol=2)

    ax4.text(0.70, 0.76, "Presença aos 6m\nentre entrantes:\n86,9% | 79,7%",
             ha='center', va='center', transform=ax4.transAxes, fontsize=7.8, fontweight='bold', color='#065F46',
             bbox=dict(boxstyle='square,pad=0.25', facecolor='#ECFDF5', edgecolor='#6EE7B7', lw=0.8), zorder=5)

    # Rodapé Editorial
    add_editorial_footer(
        fig,
        source="CNES / DATASUS, Ministério da Saúde (SGTES / PMM-E) e IPEA (IVS 2010)",
        notes=f"Amostra DDD: {n_cells} células em {n_municipalities} municípios. Prioridade imediata não aleatória; resultados não identificam o efeito causal do PMM-E.",
        x=0.06, y_bottom=0.015
    )

    fig.subplots_adjust(top=0.91, bottom=0.07, left=0.06, right=0.96)
    out_path = FIGURES / "figura_master_infografico_pmme.png"
    atomic_savefig(fig, out_path, dpi=300)
    plt.close(fig)
    print(f"[OK] Infográfico Master PMME gerado com sucesso: {out_path}")


if __name__ == "__main__":
    main()
