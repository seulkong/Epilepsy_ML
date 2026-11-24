#!/usr/bin/env python3
"""
Option 1: Real Data Visualization of the 0% Residence Ratio Paradox (n = 203 seizures)
Matches the exact academic style of cutoff_visualization.png (Navy, Brick Red, inward ticks).
"""

import os
os.environ['MPLCONFIGDIR'] = '/tmp/mplconfig'
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
    'xtick.labelsize': 9.2,
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


def generate_real_residence_figure():
    df = pd.read_csv('preprocessed_features.csv')
    succ = df[df['outcome'] == 1]
    fail = df[df['outcome'] == 0]

    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.3), dpi=300)
    plt.subplots_adjust(wspace=0.28)

    # ------------------------------------------------------------------
    # Panel (a): Binned Proportion of Residence Ratio (Success vs Failure)
    # ------------------------------------------------------------------
    axA = axes[0]
    axA.grid(True, linestyle=':', linewidth=0.55, color='#cccccc', alpha=0.85, zorder=0)

    def bin_props(s):
        n = len(s)
        c0 = (s == 0).sum() / n * 100
        c1 = ((s > 0) & (s <= 25)).sum() / n * 100
        c2 = ((s > 25) & (s <= 50)).sum() / n * 100
        c3 = ((s > 50) & (s <= 75)).sum() / n * 100
        c4 = (s > 75).sum() / n * 100
        return [c0, c1, c2, c3, c4]

    labels = ['0%\n(Exact zero)', '1–25%', '26–50%', '51–75%', '76–100%']
    p_succ = bin_props(succ['residence_ratio'])
    p_fail = bin_props(fail['residence_ratio'])

    x = np.arange(len(labels))
    w = 0.36
    b1 = axA.bar(x - w/2, p_succ, width=w, color=NAVY, alpha=0.88, edgecolor=NAVY,
                 label=f'Surgical success (n = {len(succ)})', zorder=3)
    b2 = axA.bar(x + w/2, p_fail, width=w, color=RED, alpha=0.85, edgecolor=RED,
                 label=f'Surgical failure (n = {len(fail)})', zorder=3)

    # Annotate the striking 0% bar
    axA.text(b1[0].get_x() + b1[0].get_width()/2, p_succ[0] + 1.8,
             f'{p_succ[0]:.1f}%\n(Median 0%)', ha='center', va='bottom',
             fontsize=8.2, fontweight='bold', color=NAVY)
    axA.text(b2[0].get_x() + b2[0].get_width()/2, p_fail[0] + 1.8,
             f'{p_fail[0]:.1f}%', ha='center', va='bottom',
             fontsize=8.2, fontweight='bold', color=RED)

    axA.set_xticks(x)
    axA.set_xticklabels(labels)
    axA.set_ylim(0, 82)
    axA.set_xlabel('Resection Residence Ratio (%)')
    axA.set_ylabel('Proportion of Seizures (%)')
    axA.set_title('(a) Residence Ratio Distribution (Real Data)', fontweight='bold', pad=10)
    axA.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#cccccc', framealpha=0.95)

    # ------------------------------------------------------------------
    # Panel (b): Residence Ratio vs. Min Distance to Resection (n = 203)
    # ------------------------------------------------------------------
    axB = axes[1]
    axB.grid(True, linestyle=':', linewidth=0.55, color='#cccccc', alpha=0.85, zorder=0)

    # Add tiny x-jitter only at x=0 so overlapping points are visible
    rng = np.random.default_rng(42)
    sx = succ['residence_ratio'].values.copy()
    fx = fail['residence_ratio'].values.copy()
    sx_plot = np.where(sx == 0, rng.uniform(-1.5, 1.5, size=len(sx)), sx)
    fx_plot = np.where(fx == 0, rng.uniform(-1.5, 1.5, size=len(fx)), fx)

    axB.scatter(fx_plot, fail['min_dist_to_resect'], color=RED, alpha=0.65, s=28,
                edgecolor='white', linewidth=0.4, label='Surgical failure (Engel II–IV)', zorder=3)
    axB.scatter(sx_plot, succ['min_dist_to_resect'], color=NAVY, alpha=0.65, s=28,
                edgecolor='white', linewidth=0.4, label='Surgical success (Engel I)', zorder=4)

    axB.axvline(0, color=CHARCOAL, linestyle='--', linewidth=1.0, alpha=0.6, zorder=2)
    axB.text(4.0, axB.get_ylim()[1] * 0.72,
             '90/135 success seizures\nsit at 0% residence\n(sparse sEEG coverage)',
             fontsize=8.3, fontweight='bold', color=NAVY,
             bbox=dict(boxstyle='round,pad=0.35', facecolor='white', edgecolor='#cccccc', alpha=0.92),
             zorder=5)

    axB.set_xlim(-5, 105)
    axB.set_xlabel('Resection Residence Ratio (%)')
    axB.set_ylabel('Min Distance to Resection Center (mm)')
    axB.set_title('(b) Residence Ratio vs. Minimum Distance', fontweight='bold', pad=10)
    axB.legend(loc='upper right', frameon=True, facecolor='white', edgecolor='#cccccc', framealpha=0.95)

    plt.tight_layout()
    out_file = 'residence_ratio_real_data.png'
    plt.savefig(out_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Saved: {out_file}')


if __name__ == '__main__':
    generate_real_residence_figure()

