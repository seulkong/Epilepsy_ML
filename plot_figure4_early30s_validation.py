#!/usr/bin/env python3
"""
Figure 4. Validation of Early 30-Second Seizure Window Hypothesis
-----------------------------------------------------------------
A0 포스터 전용 고선명 버전 (Poster-Optimized Ultra Crisp Version):
1) 대형 글자 크기 (Title: 16pt, Label: 14pt, Tick: 13pt, Legend: 13pt)
2) 굵은 선 및 바 두께 (Linewidth: 3.0~3.5pt)
3) PNG (DPI 300) 및 SVG 벡터 파일 동시 생성
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
plt.rcParams['axes.edgecolor'] = '#1e293b'
plt.rcParams['axes.linewidth'] = 1.6
plt.rcParams['font.size'] = 13

fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.8), dpi=300)
plt.subplots_adjust(wspace=0.28, top=0.86, bottom=0.16)

c_succ = '#10b981'   # Emerald Green (Success)
c_fail = '#ef4444'   # Crimson Red (Failure)
c_blue = '#2563eb'   # Blue
c_purple = '#8b5cf6' # Purple

# ==============================================================================
# Panel (A): 공간 전파 속도 분리도 (초기 vs 후기 비교)
# ==============================================================================
axA = axes[0]

df_30 = pd.read_csv('preprocessed_features_30s.csv')
df_late = pd.read_csv('preprocessed_features_30_to_60s.csv')

df_30['Window'] = '초기 (0–30초)'
df_late['Window'] = '후기 (30–60초)'

df_combined = pd.concat([df_30, df_late], ignore_index=True)
df_combined['Outcome_Label'] = df_combined['outcome'].map({1: '수술 성공군', 0: '수술 실패군'})

sns.boxplot(
    data=df_combined,
    x='Window',
    y='velocity_mean',
    hue='Outcome_Label',
    palette=[c_fail, c_succ],
    ax=axA,
    width=0.48,
    fliersize=3.5,
    linewidth=1.8
)

axA.set_title('(A) 구간별 전파 속도 분포', fontweight='bold', fontsize=16, pad=12)
axA.set_xlabel('발작 전파 분석 윈도우', fontweight='bold', fontsize=14)
axA.set_ylabel('평균 전파 속도 (mm/s)', fontweight='bold', fontsize=14)
axA.tick_params(axis='both', which='major', labelsize=12.5)
axA.set_ylim(-0.5, 21)
axA.grid(True, linestyle=':', alpha=0.6, linewidth=1.2)
axA.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cbd5e1', fontsize=12)

# ==============================================================================
# Panel (B): 구간별 조기 진단 성능 비교 (초기 vs 후기)
# ==============================================================================
axB = axes[1]

windows = ['초기 (0–30초)', '후기 (30–60초)']
f1_scores = [0.7192, 0.6525]
auc_scores = [0.6080, 0.5180]

x = np.arange(len(windows))
width = 0.28

rects1 = axB.bar(x - width/2, f1_scores, width, label='F1-Score', color='#3b82f6', edgecolor='#1d4ed8', linewidth=1.8)
rects2 = axB.bar(x + width/2, auc_scores, width, label='ROC-AUC', color='#a855f7', edgecolor='#7e22ce', linewidth=1.8)

axB.set_title('(B) 발작 구간별 진단 성능 비교', fontweight='bold', fontsize=16, pad=12)
axB.set_ylabel('진단 성능 점수 (Score)', fontweight='bold', fontsize=14)
axB.set_xticks(x)
axB.set_xticklabels(windows, fontsize=13, fontweight='bold')
axB.tick_params(axis='y', which='major', labelsize=12.5)
axB.set_xlim(-0.6, 1.6)
axB.set_ylim(0, 0.95)
axB.grid(True, linestyle=':', alpha=0.6, linewidth=1.2)
axB.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cbd5e1', fontsize=12)

for rect in rects1:
    h = rect.get_height()
    axB.text(rect.get_x() + rect.get_width()/2., h + 0.02, f'{h:.4f}', ha='center', va='bottom', fontsize=12, fontweight='bold', color='#1d4ed8')

for rect in rects2:
    h = rect.get_height()
    axB.text(rect.get_x() + rect.get_width()/2., h + 0.02, f'{h:.4f}', ha='center', va='bottom', fontsize=12, fontweight='bold', color='#6b21a8')

# ==============================================================================
# Panel (C): 발작 온셋 직후 순간 전파 속도 시계열 추이 (0~30초)
# ==============================================================================
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

axC.plot(time_axis, mean_fail, color=c_fail, linewidth=3.2, label='수술 실패군')
axC.fill_between(time_axis, mean_fail - sem_fail, mean_fail + sem_fail, color=c_fail, alpha=0.20)

axC.plot(time_axis, mean_succ, color=c_succ, linewidth=3.2, label='수술 성공군')
axC.fill_between(time_axis, mean_succ - sem_succ, mean_succ + sem_succ, color=c_succ, alpha=0.20)

axC.axvspan(0, 30, color='#fef3c7', alpha=0.35, zorder=0)

axC.set_title('(C) 순간 전파 속도 시계열 (0~30초)', fontweight='bold', fontsize=16, pad=12)
axC.set_xlabel('발작 개시 후 시간 (초)', fontweight='bold', fontsize=14)
axC.set_ylabel('순간 전파 속도 (mm/s)', fontweight='bold', fontsize=14)
axC.tick_params(axis='both', which='major', labelsize=12.5)
axC.set_xlim(0, 30)
axC.set_ylim(0, 10.0)
axC.grid(True, linestyle=':', alpha=0.6, linewidth=1.2)
axC.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.95, edgecolor='#cbd5e1', fontsize=12)

png_path = 'figure4_early30s_validation.png'
svg_path = 'figure4_early30s_validation.svg'
plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white', transparent=False)
plt.savefig(svg_path, format='svg', bbox_inches='tight')
plt.close(fig)
print(f"Successfully generated ultra-crisp Figure 4: {png_path} and {svg_path}")
