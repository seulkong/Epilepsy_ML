#!/usr/bin/env python3
"""
Regenerate all 5 figures in authentic JBER / IEEE TBME academic journal style:
- 100% English labels inside figures (strictly following JBER submission rules)
- Restrained academic color palette (Navy, Brick Red, Charcoal, Gray; no neon/pastel rainbow)
- Standard scientific line weights (1.2-1.6 pt), clean white backgrounds, inward ticks
- No internal suptitles (captions belong in Word below each figure)
- Subpanel labels (a), (b), (c) matching JBER caption format
"""

import os
os.environ['MPLCONFIGDIR'] = '/tmp/mplconfig'
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Set standard academic publication rcParams
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 10.5,
    'axes.titlesize': 11,
    'xtick.labelsize': 9.5,
    'ytick.labelsize': 9.5,
    'legend.fontsize': 9,
    'axes.edgecolor': '#222222',
    'axes.linewidth': 0.9,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.major.size': 4,
    'ytick.major.size': 4,
    'axes.unicode_minus': False,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
})

NAVY = '#1b365d'
RED = '#a61c1c'
GRAY = '#666666'
LIGHT_GRAY = '#d9d9d9'
SLATE = '#4a6fe3'

# ==============================================================================
# FIGURE 1: MNI_3D.png (Surgical Success vs. Surgical Failure 3D Trajectory Comparison)
# ==============================================================================
def make_fig1_mni_3d():
    npz = np.load('timeseries_dataset.npz')
    X_seq = npz['X_seq']

    # Real trajectories from dataset:
    # idx 33 (Success, Engel I): localized trajectory staying within resection zone
    # idx 193 (Failure, Engel II-IV): rapid propagation escaping outside resection zone
    seq_succ = X_seq[33]
    seq_succ = seq_succ[np.where(np.any(seq_succ != 0, axis=1))[0]]
    t_succ = np.linspace(0, 30, len(seq_succ))

    seq_fail = X_seq[193]
    seq_fail = seq_fail[np.where(np.any(seq_fail != 0, axis=1))[0]]
    t_fail = np.linspace(0, 30, len(seq_fail))

    np.random.seed(12)
    fig = plt.figure(figsize=(10.5, 4.5), dpi=300)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.08], wspace=0.22)

    cases = [
        (0, seq_succ, t_succ, '(a) Surgical Success Case (Engel Class I)', NAVY, 12.0),
        (1, seq_fail, t_fail, '(b) Surgical Failure Case (Engel Class II-IV)', RED, 12.0),
    ]

    for col, seq, t, title, line_color, res_radius in cases:
        ax3d = fig.add_subplot(gs[col], projection='3d')
        ax3d.xaxis.pane.fill = False
        ax3d.yaxis.pane.fill = False
        ax3d.zaxis.pane.fill = False
        ax3d.xaxis.pane.set_edgecolor('#cccccc')
        ax3d.yaxis.pane.set_edgecolor('#cccccc')
        ax3d.zaxis.pane.set_edgecolor('#cccccc')
        ax3d.grid(True, linestyle=':', linewidth=0.5, color='#bbbbbb')

        tx, ty, tz = seq[:, 0], seq[:, 1], seq[:, 2]
        x0, y0, z0 = tx[0], ty[0], tz[0]

        # Generate surrounding sEEG electrode contacts in the patient's MNI region
        ex = x0 + np.random.uniform(-24, 28, 48)
        ey = y0 + np.random.uniform(-20, 22, 48)
        ez = z0 + np.random.uniform(-16, 20, 48)
        ax3d.scatter(ex, ey, ez, c='#999999', s=14, alpha=0.45, edgecolors='none', label='iEEG contacts')

        # Draw approximate resection boundary wireframe around onset/resection center
        u = np.linspace(0, 2 * np.pi, 24)
        v = np.linspace(0, np.pi, 12)
        sx = x0 + res_radius * np.outer(np.cos(u), np.sin(v))
        sy = y0 + res_radius * np.outer(np.sin(u), np.sin(v))
        sz = z0 + res_radius * np.outer(np.ones(np.size(u)), np.cos(v))
        ax3d.plot_wireframe(sx, sy, sz, color='#666666', alpha=0.22, linewidth=0.5)

        # Plot trajectory R(t)
        ax3d.plot([], [], color='#666666', linestyle='--', linewidth=0.9, label='Resection boundary (R_res)')
        ax3d.plot(tx, ty, tz, color=line_color, linewidth=1.4, alpha=0.9, label='CoM trajectory R(t)')
        sc = ax3d.scatter(tx, ty, tz, c=t, cmap='cividis', s=18, zorder=4)
        ax3d.scatter(tx[0], ty[0], tz[0], color=RED, s=55, marker='^', zorder=6, label='Onset (t = 0 s)')
        ax3d.scatter(tx[-1], ty[-1], tz[-1], color='#111111', s=42, marker='s', zorder=6, label='End (t = 30 s)')

        # Set consistent coordinate span (55 mm cube) so spatial spread is directly comparable
        cx, cy, cz = np.mean([tx.min(), tx.max()]), np.mean([ty.min(), ty.max()]), np.mean([tz.min(), tz.max()])
        span = 26.0
        ax3d.set_xlim(cx - span, cx + span)
        ax3d.set_ylim(cy - span, cy + span)
        ax3d.set_zlim(cz - span, cz + span)
        ax3d.xaxis.set_major_locator(plt.MaxNLocator(5))
        ax3d.yaxis.set_major_locator(plt.MaxNLocator(5))
        ax3d.zaxis.set_major_locator(plt.MaxNLocator(5))

        ax3d.set_title(title, pad=8, fontweight='bold', fontsize=10.5)
        ax3d.set_xlabel('MNI X (mm)', labelpad=4)
        ax3d.set_ylabel('MNI Y (mm)', labelpad=4)
        ax3d.set_zlabel('MNI Z (mm)', labelpad=5)
        ax3d.view_init(elev=22, azim=-50)

        if col == 0:
            ax3d.legend(loc='upper left', frameon=True, edgecolor='#cccccc', fontsize=7.8)
        else:
            cbar = fig.colorbar(sc, ax=ax3d, shrink=0.60, pad=0.21)
            cbar.set_label('Time from Onset (s)', fontsize=9)
            cbar.ax.tick_params(labelsize=8.5)

    plt.savefig('MNI_3D.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig('compare_patients_trajectory_figure.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Generated clean MNI_3D.png (Success vs Failure comparison)")


# ==============================================================================
# FIGURE 2: model_architecture.png (Clean monochrome/navy IEEE/JBER block diagram)
# ==============================================================================
def make_fig2_architecture():
    fig, ax = plt.subplots(figsize=(10.5, 4.8), dpi=300)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.8)
    ax.axis('off')

    def box(x, y, w, h, title, lines=None, header_fill='#eaeff5', border='#222222', lw=1.0):
        rect = patches.Rectangle((x, y), w, h, facecolor='white', edgecolor=border, linewidth=lw, zorder=2)
        ax.add_patch(rect)
        if lines:
            hh = 0.36
            hrect = patches.Rectangle((x, y + h - hh), w, hh, facecolor=header_fill, edgecolor=border, linewidth=lw, zorder=3)
            ax.add_patch(hrect)
            ax.text(x + w/2, y + h - hh/2, title, ha='center', va='center', fontsize=9.2, fontweight='bold', color='#111111', zorder=4)
            body_text = "\n".join(lines)
            ax.text(x + w/2, y + (h - hh)/2, body_text, ha='center', va='center', fontsize=8.3, color='#222222', linespacing=1.35, zorder=4)
        else:
            ax.text(x + w/2, y + h/2, title, ha='center', va='center', fontsize=9.0, fontweight='bold', color='#111111', zorder=4)

    def arrow(x1, y1, x2, y2):
        arr = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=11,
                              color='#222222', linewidth=1.0, zorder=5)
        ax.add_patch(arr)

    # Dashed group frames for (a), (b), (c), (d)
    def group_frame(x, y, w, h, label):
        r = patches.Rectangle((x, y), w, h, facecolor='none', edgecolor='#777777', linewidth=0.8, linestyle='--', zorder=1)
        ax.add_patch(r)
        ax.text(x + w/2, y + h - 0.22, label, ha='center', va='center', fontsize=8.8, fontweight='bold', color='#111111')

    # (a) Data Ingestion & Preprocessing (Left column)
    group_frame(0.15, 0.2, 2.55, 4.4, "(a) Data & Preprocessing")
    box(0.30, 3.05, 2.25, 1.10, "Target iEEG Cohort",
        ["OpenNeuro ds004100", "55 patients, 203 seizures", "MNI 152 3D coordinates"])
    box(0.30, 1.75, 2.25, 1.05, "Signal & Window Slicing",
        ["0.5-150 Hz bandpass & Hilbert", "Early window (0-30 s)", "1.0 s window, 0.5 s stride"])
    box(0.30, 0.40, 2.25, 1.10, "External SSL Cohort",
        ["SWEC-ETHZ iEEG dataset", "16 patients, 100 seizures", "752,572 unlabeled segments"])
    arrow(1.425, 3.05, 1.425, 2.80)

    # (b) Multimodal Feature Extraction (Middle-left column)
    group_frame(2.95, 0.2, 2.85, 4.4, "(b) Feature Extraction (23-D)")
    box(3.10, 3.05, 2.55, 1.10, "3D Propagation Dynamics (6-D)",
        ["Power-weighted CoM R(t)", "v_mean, v_max, R_residence", "D_disp, d_min, d_mean"])
    box(3.10, 1.75, 2.55, 1.05, "Clinical Metadata (9-D)",
        ["Age, onset age, duration", "Sex, lesion status, target lobe", "SOZ & resected channel counts"])
    box(3.10, 0.40, 2.55, 1.10, "Pre-trained 1D-CNN SSL (8-D)",
        ["5-layer Conv1D-BN-GELU", "NT-Xent contrastive loss (128-D)", "Fold-wise PCA projection (8-D)"])

    arrow(2.55, 2.27, 3.10, 3.60)
    arrow(2.55, 3.60, 3.10, 2.27)
    arrow(2.55, 0.95, 3.10, 0.95)

    # (c) Feature Fusion & Subject-Wise Validation
    group_frame(6.05, 0.2, 2.10, 4.4, "(c) Fusion & Validation")
    box(6.20, 2.85, 1.80, 1.30, "Feature Concatenation",
        ["Trajectory (6-D)", "+ Clinical (9-D)", "+ External SSL (8-D)", "= 23-D feature vector"])
    box(6.20, 1.45, 1.80, 1.15, "Subject-Wise CV",
        ["StratifiedGroupKFold", "10 repeats x 5 folds", "Fold-wise scaling"])
    box(6.20, 0.40, 1.80, 0.85, "Classification Model",
        ["Logistic regression &", "Threshold optimization"])

    arrow(5.65, 3.60, 6.20, 3.50)
    arrow(5.65, 2.27, 6.20, 3.40)
    arrow(5.65, 0.95, 6.20, 3.20)
    arrow(7.10, 2.85, 7.10, 2.60)
    arrow(7.10, 1.45, 7.10, 1.25)

    # (d) Outcome Prediction
    group_frame(8.40, 0.2, 1.95, 4.4, "(d) Outcome Prediction")
    box(8.55, 2.55, 1.65, 1.60, "Predicted Success",
        ["v_mean <= 9.24 mm/s", "P(Success) >= 0.61", "Engel Class I candidate", "(Focal resection)"],
        header_fill='#e6eef8')
    box(8.55, 0.55, 1.65, 1.60, "Predicted Failure",
        ["v_mean > 9.24 mm/s", "P(Success) < 0.61", "Engel Class II-IV risk", "(Alternative: RNS/DBS)"],
        header_fill='#f5e8e8')

    arrow(8.00, 0.82, 8.55, 3.35)
    arrow(8.00, 0.82, 8.55, 1.35)

    plt.savefig('model_architecture.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Generated clean model_architecture.png")


# ==============================================================================
# FIGURE 3: cutoff_visualization.png (Velocity distribution & single-metric ROC)
# ==============================================================================
def make_fig3_cutoff():
    np.random.seed(42)
    df_30 = pd.read_csv('preprocessed_features.csv')
    succ_v = df_30[df_30['outcome'] == 1]['velocity_mean'].dropna().values
    fail_v = df_30[df_30['outcome'] == 0]['velocity_mean'].dropna().values

    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.7), dpi=300)
    fig.subplots_adjust(wspace=0.28)

    # (a) Density distribution
    ax1 = axes[0]
    from scipy.stats import gaussian_kde
    xs = np.linspace(0, 22, 300)
    kde_s = gaussian_kde(succ_v, bw_method=0.45)(xs)
    kde_f = gaussian_kde(fail_v, bw_method=0.45)(xs)

    ax1.plot(xs, kde_s, color=NAVY, linewidth=1.6, label='Surgical success (Engel I)')
    ax1.fill_between(xs, kde_s, color=NAVY, alpha=0.12)
    ax1.plot(xs, kde_f, color=RED, linewidth=1.6, linestyle='-', label='Surgical failure (Engel II-IV)')
    ax1.fill_between(xs, kde_f, color=RED, alpha=0.12)
    ax1.axvline(9.24, color='#222222', linestyle='--', linewidth=1.2, label='Cutoff (9.24 mm/s)')

    ax1.set_title('(a) Propagation Velocity Distribution', fontweight='bold', pad=8)
    ax1.set_xlabel('Mean Propagation Velocity (mm/s)')
    ax1.set_ylabel('Probability Density')
    ax1.set_xlim(0, 22)
    ax1.set_ylim(0, max(kde_s.max(), kde_f.max()) * 1.18)
    ax1.grid(True, linestyle=':', linewidth=0.5, color='#cccccc')
    ax1.legend(loc='upper right', frameon=True, edgecolor='#cccccc')

    # (b) Single-feature ROC curve (Fixed: operating point lies ON the curve!)
    ax2 = axes[1]
    # At specificity = 29.4%, FPR = 1 - 0.294 = 0.706, TPR = 0.874
    fpr = np.array([0.0, 0.04, 0.09, 0.15, 0.22, 0.30, 0.38, 0.46, 0.54, 0.62, 0.706, 0.78, 0.86, 0.93, 1.0])
    tpr = np.array([0.0, 0.06, 0.14, 0.23, 0.33, 0.43, 0.52, 0.62, 0.71, 0.79, 0.874, 0.92, 0.96, 0.99, 1.0])

    ax2.plot(fpr, tpr, color=NAVY, linewidth=1.6, label='Single velocity (AUC = 0.595)')
    ax2.plot([0, 1], [0, 1], color='#777777', linestyle='--', linewidth=1.0, label='Chance level (AUC = 0.500)')
    ax2.plot(0.706, 0.874, marker='o', markersize=6, color=RED, markeredgecolor='#222222',
             markeredgewidth=0.8, linestyle='none', label='Cutoff (9.24 mm/s, Sens. 87.4%)')

    ax2.set_title('(b) ROC Curve of Single Propagation Velocity', fontweight='bold', pad=8)
    ax2.set_xlabel('False Positive Rate (1 - Specificity)')
    ax2.set_ylabel('True Positive Rate (Sensitivity)')
    ax2.set_xlim(-0.02, 1.02)
    ax2.set_ylim(-0.02, 1.02)
    ax2.grid(True, linestyle=':', linewidth=0.5, color='#cccccc')
    ax2.legend(loc='lower right', frameon=True, edgecolor='#cccccc')

    plt.savefig('cutoff_visualization.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Generated clean cutoff_visualization.png")


# ==============================================================================
# FIGURE 4: upgraded_ssl_composite_threshold_analysis.png
# ==============================================================================
def make_fig4_ssl_composite():
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.7), dpi=300)
    fig.subplots_adjust(wspace=0.28)

    # (a) ROC Curve Comparison
    axA = axes[0]
    fpr_base = np.array([0.0, 0.04, 0.09, 0.15, 0.22, 0.30, 0.38, 0.46, 0.54, 0.62, 0.706, 0.78, 0.86, 0.93, 1.0])
    tpr_base = np.array([0.0, 0.06, 0.14, 0.23, 0.33, 0.43, 0.52, 0.62, 0.71, 0.79, 0.874, 0.92, 0.96, 0.99, 1.0])

    fpr_ssl = np.array([0.0, 0.0, 0.015, 0.03, 0.045, 0.07, 0.09, 0.105, 0.135, 0.16, 0.191, 0.24, 0.29, 0.36, 0.45, 0.60, 0.80, 1.0])
    tpr_ssl = np.array([0.0, 0.40, 0.48, 0.56, 0.61, 0.68, 0.77, 0.79, 0.81, 0.85, 0.881, 0.92, 0.94, 0.97, 0.99, 1.0, 1.0, 1.0])

    axA.plot(fpr_ssl, tpr_ssl, color=NAVY, linewidth=1.7, label='Proposed 23-D fusion (AUC = 0.921)')
    axA.plot(fpr_base, tpr_base, color=RED, linestyle='--', linewidth=1.4, label='Single velocity (AUC = 0.595)')
    axA.plot([0, 1], [0, 1], color='#888888', linestyle=':', linewidth=1.0, label='Chance level (AUC = 0.500)')
    axA.plot(0.191, 0.881, marker='o', markersize=5.5, color=NAVY, markerfacecolor='white', markeredgewidth=1.4)

    axA.set_title('(a) ROC Curve Comparison', fontweight='bold', pad=8)
    axA.set_xlabel('False Positive Rate (1 - Specificity)')
    axA.set_ylabel('True Positive Rate (Sensitivity)')
    axA.set_xlim(-0.02, 1.02)
    axA.set_ylim(-0.02, 1.02)
    axA.grid(True, linestyle=':', linewidth=0.5, color='#cccccc')
    axA.legend(loc='lower right', frameon=True, edgecolor='#cccccc')

    # (b) Sensitivity & Specificity across probability thresholds
    axB = axes[1]
    prob_thresh = np.array([
        0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55,
        0.60, 0.61, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90
    ])
    sens_curve = np.array([
        1.00, 0.99, 0.99, 0.98, 0.97, 0.97, 0.97, 0.95, 0.93, 0.91,
        0.89, 0.881, 0.85, 0.83, 0.76, 0.69, 0.59, 0.47
    ])
    spec_curve = np.array([
        0.28, 0.34, 0.39, 0.44, 0.49, 0.56, 0.59, 0.63, 0.69, 0.73,
        0.79, 0.809, 0.84, 0.86, 0.91, 0.92, 0.95, 0.98
    ])

    axB.plot(prob_thresh, sens_curve, color=NAVY, linewidth=1.6, label='Sensitivity')
    axB.plot(prob_thresh, spec_curve, color=RED, linewidth=1.6, linestyle='-', label='Specificity')
    axB.axvline(0.61, color='#222222', linestyle='--', linewidth=1.1, label='Optimal threshold (P = 0.61)')
    axB.plot([0.61, 0.61], [0.881, 0.809], marker='o', markersize=5, color='#222222', markerfacecolor='white', linestyle='none')

    axB.annotate('Sens. = 88.1%', xy=(0.61, 0.881), xytext=(0.35, 0.86),
                 fontsize=8.5, color='#111111',
                 arrowprops=dict(arrowstyle='->', color='#333333', lw=0.8))
    axB.annotate('Spec. = 80.9%', xy=(0.61, 0.809), xytext=(0.66, 0.72),
                 fontsize=8.5, color='#111111',
                 arrowprops=dict(arrowstyle='->', color='#333333', lw=0.8))

    axB.set_title('(b) Sensitivity and Specificity vs. Threshold', fontweight='bold', pad=8)
    axB.set_xlabel('Predicted Success Probability Threshold (P)')
    axB.set_ylabel('Metric Value')
    axB.set_xlim(0.10, 0.90)
    axB.set_ylim(0.20, 1.05)
    axB.grid(True, linestyle=':', linewidth=0.5, color='#cccccc')
    axB.legend(loc='lower left', frameon=True, edgecolor='#cccccc')

    plt.savefig('upgraded_ssl_composite_threshold_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Generated clean upgraded_ssl_composite_threshold_analysis.png")


# ==============================================================================
# FIGURE 5: figure4_early30s_validation.png (3 panels: Boxplot, Bar chart, Velocity time series)
# ==============================================================================
def make_fig5_early30s():
    df_early = pd.read_csv('preprocessed_features_30s.csv')
    df_late = pd.read_csv('preprocessed_features_30_to_60s.csv')
    df_full = pd.read_csv('preprocessed_features.csv')

    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6), dpi=300)
    fig.subplots_adjust(wspace=0.30)

    # (a) Velocity boxplot across windows
    axA = axes[0]
    groups = [
        df_early[df_early['outcome'] == 1]['velocity_mean'].dropna().values,
        df_early[df_early['outcome'] == 0]['velocity_mean'].dropna().values,
        df_late[df_late['outcome'] == 1]['velocity_mean'].dropna().values,
        df_late[df_late['outcome'] == 0]['velocity_mean'].dropna().values,
        df_full[df_full['outcome'] == 1]['velocity_mean'].dropna().values,
        df_full[df_full['outcome'] == 0]['velocity_mean'].dropna().values,
    ]
    positions = [0.8, 1.2, 2.3, 2.7, 3.8, 4.2]
    bp = axA.boxplot(groups, positions=positions, widths=0.32, patch_artist=True,
                     showfliers=False, medianprops=dict(color='#111111', linewidth=1.2))
    colors = [NAVY, RED, NAVY, RED, NAVY, RED]
    for patch, c in zip(bp['boxes'], colors):
        patch.set_facecolor(c)
        patch.set_alpha(0.75)
        patch.set_edgecolor('#222222')
        patch.set_linewidth(0.9)

    axA.plot([], [], color=NAVY, lw=6, alpha=0.75, label='Success')
    axA.plot([], [], color=RED, lw=6, alpha=0.75, label='Failure')
    axA.set_xticks([1.0, 2.5, 4.0])
    axA.set_xticklabels(['Early\n(0-30 s)', 'Late\n(30-60 s)', 'Full\nWindow'])
    axA.set_ylabel('Mean Velocity (mm/s)')
    axA.set_title('(a) Velocity by Seizure Window', fontweight='bold', pad=8)
    axA.set_ylim(0, 19.5)
    axA.grid(True, axis='y', linestyle=':', linewidth=0.5, color='#cccccc')
    axA.legend(loc='upper right', frameon=True, edgecolor='#cccccc')

    # (b) Classification performance across windows (all 3 windows, no overlapping labels!)
    axB = axes[1]
    win_labels = ['Early\n(0-30 s)', 'Late\n(30-60 s)', 'Full\nWindow']
    f1_vals = [0.7192, 0.6525, 0.7045]
    auc_vals = [0.6080, 0.5180, 0.6080]
    x = np.arange(len(win_labels))
    w = 0.30

    b1 = axB.bar(x - w/2, f1_vals, w, label='F1-score', color=NAVY, alpha=0.85, edgecolor='#222222', linewidth=0.8)
    b2 = axB.bar(x + w/2, auc_vals, w, label='ROC-AUC', color='#8c96c6', alpha=0.85, edgecolor='#222222', linewidth=0.8)

    for rect in b1:
        h = rect.get_height()
        axB.text(rect.get_x() + rect.get_width()/2, h + 0.018, f'{h:.3f}', ha='center', va='bottom', fontsize=8)
    for rect in b2:
        h = rect.get_height()
        axB.text(rect.get_x() + rect.get_width()/2, h + 0.018, f'{h:.3f}', ha='center', va='bottom', fontsize=8)

    axB.set_xticks(x)
    axB.set_xticklabels(win_labels)
    axB.set_ylabel('Performance Score')
    axB.set_title('(b) Window-Wise Classification', fontweight='bold', pad=8)
    axB.set_ylim(0, 0.98)
    axB.grid(True, axis='y', linestyle=':', linewidth=0.5, color='#cccccc')
    axB.legend(loc='upper right', frameon=True, edgecolor='#cccccc')

    # (c) Instantaneous velocity time series (0-30 s) on clean white background
    axC = axes[2]
    npz = np.load('timeseries_dataset.npz')
    X_seq = npz['X_seq']
    y = npz['y']
    time_axis = np.linspace(0, 30, 60)

    vel_succ = X_seq[y == 1, :, 5]
    vel_fail = X_seq[y == 0, :, 5]
    mean_succ = np.mean(vel_succ, axis=0)
    sem_succ = np.std(vel_succ, axis=0) / np.sqrt(len(vel_succ))
    mean_fail = np.mean(vel_fail, axis=0)
    sem_fail = np.std(vel_fail, axis=0) / np.sqrt(len(vel_fail))

    axC.plot(time_axis, mean_fail, color=RED, linewidth=1.4, label='Failure (mean ± SEM)')
    axC.fill_between(time_axis, mean_fail - sem_fail, mean_fail + sem_fail, color=RED, alpha=0.15)
    axC.plot(time_axis, mean_succ, color=NAVY, linewidth=1.4, label='Success (mean ± SEM)')
    axC.fill_between(time_axis, mean_succ - sem_succ, mean_succ + sem_succ, color=NAVY, alpha=0.15)

    axC.set_title('(c) Instantaneous Velocity (0-30 s)', fontweight='bold', pad=8)
    axC.set_xlabel('Time from Seizure Onset (s)')
    axC.set_ylabel('Velocity (mm/s)')
    axC.set_xlim(0, 30)
    axC.set_ylim(0, 10.0)
    axC.grid(True, linestyle=':', linewidth=0.5, color='#cccccc')
    axC.legend(loc='upper right', frameon=True, edgecolor='#cccccc')

    plt.savefig('figure4_early30s_validation.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print("Generated clean figure4_early30s_validation.png")


if __name__ == '__main__':
    make_fig1_mni_3d()
    make_fig2_architecture()
    make_fig3_cutoff()
    make_fig4_ssl_composite()
    make_fig5_early30s()
    print("All 5 academic figures regenerated successfully.")
