#!/usr/bin/env python3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import os

# Set publication style
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0

# -------------------------------------------------------------
# Generate Figure 4: Lobe Stratification (IT vs ET)
# -------------------------------------------------------------
fig4, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300)
fig4.subplots_adjust(wspace=0.3)

# Load data
df_part = pd.read_csv('.cache_ds004100/ds004100_participants.tsv', sep='\t')
df_feat = pd.read_csv('preprocessed_features.csv')

def categorize_lobe(target):
    if pd.isna(target):
        return 'Unknown'
    t = str(target).upper()
    if 'TEMPORAL' in t or 'MTL' in t:
        return 'Temporal (TL)'
    else:
        return 'Extra-temporal (ETL)'

df_part['lobe_group'] = df_part['target'].apply(categorize_lobe)
df_merged = pd.merge(df_feat, df_part[['participant_id', 'target', 'lobe_group']], on='participant_id', how='left')

# Panel A: Baseline Velocity Comparison (IT vs ET)
axA = axes[0]
sns.boxplot(data=df_merged, x='lobe_group', y='velocity_mean', palette=['#3498db', '#e74c3c'], ax=axA, width=0.4)
axA.set_title('(A) Baseline Propagation Velocity by Lobe', fontweight='bold', fontsize=11)
axA.set_xlabel('Anatomical Lobe Cohort', fontweight='bold')
axA.set_ylabel('Mean Velocity (mm/s)', fontweight='bold')
axA.grid(True, linestyle=':', alpha=0.5)
axA.text(0.5, 0.9, 'ETL Mean: 7.22 mm/s\nTL Mean: 4.27 mm/s', transform=axA.transAxes, fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Panel B: Outcome Separation in Temporal Lobe (IT)
axB = axes[1]
df_it = df_merged[df_merged['lobe_group'] == 'Temporal (TL)'].copy()
df_it['Outcome_Label'] = df_it['outcome'].map({1: 'Success (S)', 0: 'Failure (F)'})
sns.boxplot(data=df_it, x='Outcome_Label', y='velocity_mean', palette=['#2ecc71', '#e74c3c'], ax=axB, width=0.4, order=['Success (S)', 'Failure (F)'])
axB.axhline(9.24, color='crimson', linestyle='--', linewidth=1.5, label='Threshold (9.24 mm/s)')
axB.set_title('(B) Temporal Lobe Cohort (TL, n=40)', fontweight='bold', fontsize=11)
axB.set_xlabel('Surgical Outcome', fontweight='bold')
axB.set_ylabel('Mean Velocity (mm/s)', fontweight='bold')
axB.grid(True, linestyle=':', alpha=0.5)
axB.legend(loc='upper right', fontsize=8)

# Panel C: Outcome Separation in Extra-Temporal Lobe (ET)
axC = axes[2]
df_et = df_merged[df_merged['lobe_group'] == 'Extra-temporal (ETL)'].copy()
df_et['Outcome_Label'] = df_et['outcome'].map({1: 'Success (S)', 0: 'Failure (F)'})
sns.boxplot(data=df_et, x='Outcome_Label', y='velocity_mean', palette=['#2ecc71', '#e74c3c'], ax=axC, width=0.4, order=['Success (S)', 'Failure (F)'])
axC.axhline(9.24, color='crimson', linestyle='--', linewidth=1.5, label='Threshold (9.24 mm/s)')
axC.set_title('(C) Extra-Temporal Lobe Cohort (ETL, n=15)', fontweight='bold', fontsize=11)
axC.set_xlabel('Surgical Outcome', fontweight='bold')
axC.set_ylabel('Mean Velocity (mm/s)', fontweight='bold')
axC.grid(True, linestyle=':', alpha=0.5)
axC.legend(loc='upper left', fontsize=8)

fig4.suptitle('Figure 4. Anatomical Lobe Stratification Analysis', fontsize=14, fontweight='bold', y=1.02)
fig4.savefig('figure4_lobe_stratification.png', bbox_inches='tight', dpi=300, facecolor='white', transparent=False)
plt.close(fig4)
print("Generated figure4_lobe_stratification.png successfully.")

# -------------------------------------------------------------
# Generate Figure 5: Model Benchmark & 30s Sensitivity
# -------------------------------------------------------------
fig5, axes5 = plt.subplots(1, 3, figsize=(15, 4.5), dpi=300)

# Data for Panel A: Feature Ablation
axA5 = axes5[0]
models_ablation = ['Group B\n(Clinical)', 'Group A\n(Trajectory)', 'Group A+B\n(Combined)']
auc_ablation = [0.5487, 0.6543, 0.5596]
f1_ablation = [0.6617, 0.7723, 0.6985]
x = np.arange(len(models_ablation))
width = 0.35
axA5.bar(x - width/2, auc_ablation, width, label='ROC-AUC', color='#34495e')
axA5.bar(x + width/2, f1_ablation, width, label='F1-Score', color='#2980b9')
axA5.set_title('(A) Feature Group Ablation', fontweight='bold', fontsize=10)
axA5.set_xticks(x)
axA5.set_xticklabels(models_ablation, fontsize=9)
axA5.set_ylim(0, 1.0)
axA5.set_ylabel('Score', fontweight='bold')
axA5.legend(loc='lower right', fontsize=8)
axA5.grid(True, linestyle=':', alpha=0.5)

# Data for Panel B: Early 30s Window Sensitivity
axB5 = axes5[1]
windows = ['Early (0-30s)', 'Late (30-60s)', 'Full Window']
f1_win = [0.7051, 0.6525, 0.6544]
bars = axB5.bar(windows, f1_win, color=['#e67e22', '#f39c12', '#d35400'], width=0.45)
axB5.set_title('(B) Window Sensitivity (F1-Score, GBM)', fontweight='bold', fontsize=10)
axB5.set_ylim(0, 1.0)
axB5.set_ylabel('F1-Score', fontweight='bold')
axB5.grid(True, linestyle=':', alpha=0.5)
for bar in bars:
    yval = bar.get_height()
    axB5.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f'{yval:.4f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')

# Data for Panel C: Benchmark Comparison (Baseline vs Final Model vs TS-DL)
axC5 = axes5[2]
bench_models = ['Baseline\n(Clinical)', '3D Trajectory\n(Group A)', 'Conv1D-LSTM\n(DL)', 'GRU-Attention\n(DL)', 'Final Model\n(SSL + Lobe)']
acc_bench = [0.5567, 0.6567, 0.6154, 0.6538, 0.8056]
f1_bench = [0.6617, 0.7723, 0.6923, 0.7059, 0.8679]
x5 = np.arange(len(bench_models))
axC5.plot(bench_models, acc_bench, marker='o', linewidth=2, color='#16a085', label='Accuracy')
axC5.plot(bench_models, f1_bench, marker='s', linewidth=2, color='#8e44ad', label='F1-Score')
axC5.set_title('(C) Overall Model Benchmarking', fontweight='bold', fontsize=10)
axC5.set_ylim(0.4, 1.0)
axC5.set_ylabel('Performance Score', fontweight='bold')
axC5.set_xticklabels(bench_models, rotation=20, ha='right', fontsize=8)
axC5.legend(loc='lower right', fontsize=8)
axC5.grid(True, linestyle=':', alpha=0.5)

fig5.suptitle('Figure 5. Benchmark Models & 30s Early Prediction Sensitivity', fontsize=14, fontweight='bold', y=1.05)
fig5.savefig('figure5_model_benchmark.png', bbox_inches='tight', dpi=300, facecolor='white', transparent=False)
plt.close(fig5)
print("Generated figure5_model_benchmark.png successfully.")
