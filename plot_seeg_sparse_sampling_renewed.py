#!/usr/bin/env python3
"""
Ultra-clean Academic-Style Figure: sEEG Sparse Sampling & 0% Residence Ratio Artifact
Matches the exact typography, color palette, and minimalist style of cutoff_visualization.png.
"""

import os
os.environ['MPLCONFIGDIR'] = '/tmp/mplconfig'
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

NAVY = '#1b365d'
RED = '#a61c1c'
GRAY = '#666666'
CHARCOAL = '#222222'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 10.5,
    'axes.titlesize': 11,
    'xtick.labelsize': 9.5,
    'ytick.labelsize': 9.5,
    'legend.fontsize': 8.5,
    'axes.edgecolor': CHARCOAL,
    'axes.linewidth': 0.9,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    'axes.unicode_minus': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
})


def generate_clean_english_panel():
    fig, ax = plt.subplots(figsize=(5.6, 4.4), dpi=300)

    # Subtle dotted grid matching cutoff_visualization.png
    ax.grid(True, linestyle=':', linewidth=0.55, color='#cccccc', alpha=0.85, zorder=0)

    # Resection Zone
    rect = patches.Rectangle(
        (4.0, 4.2), 3.0, 2.8,
        linewidth=1.4, linestyle='--', edgecolor=NAVY,
        facecolor=NAVY, alpha=0.10, zorder=2,
        label='Resection zone (R_res)'
    )
    ax.add_patch(rect)
    ax.text(5.5, 5.6, 'Resection Zone', ha='center', va='center',
            fontsize=9.5, fontweight='bold', color=NAVY, zorder=3)

    # Sparse sEEG Depth Electrode Path & Contacts
    ax.plot([1.0, 9.0], [2.2, 8.2], color=GRAY, linestyle=':', linewidth=1.2,
            alpha=0.8, zorder=2, label='sEEG electrode trajectory')
    ax.scatter([2.0, 8.0], [2.95, 7.45], color=CHARCOAL, edgecolor='white',
               linewidth=0.7, s=55, zorder=5, label='sEEG contacts (sparse)')
    ax.text(2.0, 3.32, 'Contact A', ha='center', va='bottom', fontsize=8.5, color=CHARCOAL)
    ax.text(8.0, 7.80, 'Contact B', ha='center', va='bottom', fontsize=8.5, color=CHARCOAL)

    # Seizure Propagation Trajectory R(t) passing 1.2 mm outside resection boundary
    traj_x = np.linspace(1.4, 8.6, 200)
    traj_y = 1.8 + 0.15 * traj_x + 0.375 * np.cos(0.8 * (traj_x - 5.5))
    ax.plot(traj_x, traj_y, color=RED, linewidth=2.2, zorder=4,
            label='Seizure trajectory R(t)')

    # 1.2 mm Gap Annotation (clean, no heavy box)
    ax.annotate('', xy=(5.5, 4.2), xytext=(5.5, 3.0),
                arrowprops=dict(arrowstyle='<->', color=NAVY, lw=1.4), zorder=5)
    ax.text(5.68, 3.6, 'Just outside R_res\n(Residence = 0%)', color=NAVY,
            fontsize=8.5, fontweight='bold', va='center')

    ax.set_title('Sparse sEEG Sampling & 0% Residence Artifact',
                 fontweight='bold', color='#111111', pad=10)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 9.5)
    ax.set_xlabel('Spatial X (mm)')
    ax.set_ylabel('Spatial Y (mm)')

    ax.legend(loc='upper left', fontsize=8.3, frameon=True,
              facecolor='white', edgecolor='#cccccc', framealpha=0.95)

    plt.tight_layout()
    out_file = 'seeg_sparse_sampling_A_renewed.png'
    plt.savefig(out_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Saved: {out_file}')


if __name__ == '__main__':
    generate_clean_english_panel()
