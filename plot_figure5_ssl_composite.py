#!/usr/bin/env python3
"""
Figure 5. SSL Multimodal Composite Model Threshold Analysis & Performance
--------------------------------------------------------------------------
학술대회 최우수 포스터 발표용 프리미엄 고선명 버전 (Premium Academic Visuals):
1) 폰트 크기 및 위계 최적화 (Title: 17pt, Label: 14.5pt, Annotation: 13.5pt)
2) Nature/Lancet 메디컬 저널 표준 컬러 팔레트 (Emerald Green & Crimson Red & Gold)
3) P=0.61 임계점 Callout 배지 및 가독성 극대화
4) 초고해상도 PNG (300 DPI) 및 100% 무손실 SVG 동시 출력
"""

import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Apple SD Gothic Neo', 'Malgun Gothic', 'NanumGothic', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.edgecolor'] = '#1e293b'
plt.rcParams['axes.linewidth'] = 1.6
plt.rcParams['font.size'] = 13.5

fig, axes = plt.subplots(1, 2, figsize=(14.2, 5.8), dpi=300)
plt.subplots_adjust(wspace=0.26, bottom=0.18, top=0.88)

# ==============================================================================
# Panel (A): ROC 곡선
# ==============================================================================
axA = axes[0]

fpr_base = np.array([0.0, 0.01, 0.01, 0.03, 0.03, 0.06, 0.06, 0.09, 0.09, 0.12, 0.12,
                     0.18, 0.18, 0.21, 0.21, 0.25, 0.25, 0.29, 0.29, 0.33, 0.33, 0.35, 0.35,
                     0.39, 0.39, 0.41, 0.41, 0.43, 0.43, 0.45, 0.45, 0.49, 0.49, 0.54, 0.54,
                     0.59, 0.59, 0.64, 0.64, 0.67, 0.67, 0.71, 0.71, 0.75, 0.75, 0.80, 0.80,
                     0.86, 0.86, 0.93, 0.93, 0.97, 0.97, 1.0])
tpr_base = np.array([0.0, 0.02, 0.05, 0.05, 0.12, 0.12, 0.16, 0.16, 0.22, 0.22, 0.23,
                     0.23, 0.28, 0.28, 0.33, 0.33, 0.35, 0.35, 0.40, 0.40, 0.46, 0.46, 0.47,
                     0.47, 0.50, 0.50, 0.53, 0.53, 0.58, 0.58, 0.60, 0.60, 0.64, 0.64, 0.67,
                     0.67, 0.68, 0.68, 0.76, 0.76, 0.84, 0.84, 0.88, 0.88, 0.89, 0.89, 0.94,
                     0.94, 0.97, 0.97, 0.99, 0.99, 1.0, 1.0])

fpr_ssl = np.array([0.0, 0.0, 0.015, 0.015, 0.03, 0.03, 0.045, 0.045, 0.07, 0.07, 0.09, 0.09,
                    0.105, 0.105, 0.135, 0.135, 0.16, 0.16, 0.191, 0.191, 0.21, 0.21, 0.24, 0.24,
                    0.26, 0.26, 0.29, 0.29, 0.31, 0.31, 0.36, 0.36, 0.42, 0.42, 0.56, 0.56,
                    0.77, 0.77, 1.0])
tpr_ssl = np.array([0.0, 0.40, 0.40, 0.48, 0.48, 0.56, 0.56, 0.61, 0.61, 0.64, 0.64, 0.77,
                    0.77, 0.79, 0.79, 0.81, 0.81, 0.85, 0.85, 0.881, 0.881, 0.89, 0.89, 0.92,
                    0.92, 0.93, 0.93, 0.94, 0.94, 0.96, 0.96, 0.97, 0.97, 0.99, 0.99, 1.0,
                    1.0, 1.0, 1.0])

# Plot ROC curves
axA.plot(fpr_base, tpr_base, color='#ef4444', linestyle='--', linewidth=3.0,
         label='기존 속도 단독 지표 (AUC = 0.595)')
axA.plot(fpr_ssl, tpr_ssl, color='#059669', linewidth=4.0,
         label='23개 SSL 멀티모달 복합 (AUC = 0.921)')

# Diagonal Chance
axA.plot([0, 1], [0, 1], color='#94a3b8', linestyle=':', linewidth=1.8, label='무작위 추측 (Chance)')

axA.set_title('(A) ROC 곡선 비교 (전파 속도 vs 제안 SSL 복합 모델)', fontweight='bold', fontsize=16, pad=12)
axA.set_xlabel('위양성률 (1 - 특이도)', fontweight='bold', fontsize=14)
axA.set_ylabel('진양성률 (민감도)', fontweight='bold', fontsize=14)
axA.tick_params(axis='both', which='major', labelsize=12.5)
axA.set_xlim(-0.02, 1.02)
axA.set_ylim(-0.02, 1.02)
axA.grid(True, linestyle=':', alpha=0.55, linewidth=1.1)
axA.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.96, edgecolor='#cbd5e1', fontsize=12.5)

# Highlight Area under SSL curve
axA.fill_between(fpr_ssl, tpr_ssl, color='#059669', alpha=0.10)

# ==============================================================================
# Panel (B): 민감도/특이도 분석
# ==============================================================================
axB = axes[1]

prob_thresh = np.array([
    0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30, 0.32, 0.34, 0.36, 0.38,
    0.40, 0.42, 0.44, 0.46, 0.48, 0.50, 0.52, 0.54, 0.56, 0.58, 0.60, 0.61, 0.62, 0.64, 0.66,
    0.68, 0.70, 0.72, 0.74, 0.76, 0.78, 0.80, 0.82, 0.84, 0.86, 0.88, 0.90
])

sens_curve = np.array([
    1.00, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 0.98, 0.97, 0.97, 0.97, 0.97, 0.97, 0.97,
    0.97, 0.97, 0.96, 0.96, 0.94, 0.93, 0.92, 0.92, 0.90, 0.89, 0.89, 0.881, 0.87, 0.86, 0.85,
    0.84, 0.84, 0.82, 0.79, 0.74, 0.71, 0.69, 0.66, 0.61, 0.57, 0.52, 0.47
])

spec_curve = np.array([
    0.28, 0.32, 0.34, 0.34, 0.37, 0.39, 0.41, 0.43, 0.44, 0.47, 0.49, 0.53, 0.56, 0.56, 0.59,
    0.59, 0.61, 0.63, 0.63, 0.66, 0.69, 0.70, 0.72, 0.74, 0.76, 0.79, 0.809, 0.82, 0.84, 0.85,
    0.85, 0.85, 0.87, 0.90, 0.91, 0.91, 0.92, 0.94, 0.95, 0.95, 0.97, 0.98
])

line_sens, = axB.plot(prob_thresh, sens_curve, color='#059669', linewidth=3.8, label='민감도 (Sensitivity)')
line_spec, = axB.plot(prob_thresh, spec_curve, color='#b91c1c', linewidth=3.8, label='특이도 (Specificity)')

# Optimal threshold vertical line
axB.axvline(x=0.61, ymin=0.0, ymax=0.96, color='#dc2626', linestyle='--', linewidth=2.6, label='최적 임계값 (P = 0.61)')

# Markers at P = 0.61
axB.scatter([0.61], [0.881], color='#f59e0b', s=220, edgecolor='#1e293b', linewidth=2.2, zorder=5)
axB.scatter([0.61], [0.809], color='#f59e0b', s=220, edgecolor='#1e293b', linewidth=2.2, zorder=5)

# Callout annotation boxes with clean badges
axB.annotate('민감도: 88.1%', xy=(0.61, 0.881), xytext=(0.66, 0.895),
             arrowprops=dict(arrowstyle='->', color='#059669', lw=1.8),
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#ecfdf5', edgecolor='#059669', lw=1.5),
             color='#065f46', fontweight='bold', fontsize=13)

axB.annotate('특이도: 80.9%', xy=(0.61, 0.809), xytext=(0.66, 0.775),
             arrowprops=dict(arrowstyle='->', color='#b91c1c', lw=1.8),
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#fef2f2', edgecolor='#b91c1c', lw=1.5),
             color='#991b1b', fontweight='bold', fontsize=13)

axB.set_title('(B) 임계값별 민감도 / 특이도 동역학 (최적점 P = 0.61)', fontweight='bold', fontsize=16, pad=12)
axB.set_xlabel('수술 성공 예측 확률 임계값 (P)', fontweight='bold', fontsize=14)
axB.set_ylabel('성능 비율 (Ratio)', fontweight='bold', fontsize=14)
axB.tick_params(axis='both', which='major', labelsize=12.5)
axB.set_xlim(0.08, 0.92)
axB.set_ylim(0.20, 1.05)
axB.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
axB.grid(True, linestyle=':', alpha=0.55, linewidth=1.1)

axB.legend(loc='lower center', bbox_to_anchor=(0.5, -0.25), ncol=3, frameon=True,
           facecolor='white', framealpha=0.96, edgecolor='#cbd5e1', fontsize=12.5,
           handlelength=2.0, columnspacing=1.5)

png_path = 'upgraded_ssl_composite_threshold_analysis.png'
svg_path = 'upgraded_ssl_composite_threshold_analysis.svg'
plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white', transparent=False)
plt.savefig(svg_path, format='svg', bbox_inches='tight')
plt.close()
print(f"Successfully generated refined Figure 5: {png_path} and {svg_path}")
