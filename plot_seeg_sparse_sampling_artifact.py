#!/usr/bin/env python3
"""
Scientific Diagram: SEEG Sparse Sampling Artifact & 0% Residence Ratio Paradox
-------------------------------------------------------------------------------
Generates a 300 DPI publication-quality figure explaining:
  Panel A: Sparse SEEG Electrodes & Small Resection Volume (Trajectory passes 1mm outside)
  Panel B: Binary Residence Ratio Artifact (Calculates 0% Residence Ratio)
  Panel C: 3D Distance Metric Solution d(t) = 1.2mm (Correctly measures high spatial correlation)
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set Korean Font (AppleGothic)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12

def generate_seeg_artifact_figure():
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    # --------------------------------------------------------------------------
    # Panel A: 0% Residence Ratio Computational Artifact
    # --------------------------------------------------------------------------
    ax1 = axes[0]
    ax1.set_title('(A) 단선적 체류 비율(Residence Ratio)의 한계: 0% 착시 현상', fontweight='bold', pad=12)

    # Draw Small Resection Volume (3mm box)
    rect = patches.Rectangle((4, 4), 3, 3, linewidth=2, edgecolor='limegreen', facecolor='limegreen', alpha=0.3, label='작은 수술 절제 영역 (3mm)')
    ax1.add_patch(rect)

    # Draw SEEG Depth Electrodes (Sparse 1D Lines)
    ax1.plot([1, 9], [2, 8], color='gray', linestyle='--', linewidth=1.5, alpha=0.6, label='SEEG 바늘 전극 경로')
    ax1.scatter([2, 8], [2.75, 7.25], color='black', s=80, zorder=5, label='SEEG 전극 센서 접점 (Sparse)')
    ax1.text(2, 2.1, 'SEEG 전극 A', fontsize=9, fontweight='bold')
    ax1.text(8, 6.6, 'SEEG 전극 B', fontsize=9, fontweight='bold')

    # Draw Seizure Trajectory Path (passes strictly outside resection box with 1.2mm gap at Y=2.8)
    traj_x = np.linspace(1.5, 8.5, 100)
    # Peak at X=5.5 is Y=2.8, giving exact 1.2mm gap to bottom of box (Y=4.0)
    traj_y = 1.6 + 0.15 * traj_x + 0.375 * np.cos(0.8 * (traj_x - 5.5))
    ax1.plot(traj_x, traj_y, color='crimson', linewidth=3, label='발작 전파 궤적 P(t)', zorder=4)

    # Draw Distance Gap Arrow (1.2mm gap between box Y=4.0 and curve Y=2.8 at X=5.5)
    ax1.annotate('', xy=(5.5, 4.0), xytext=(5.5, 2.8),
                 arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
    ax1.text(5.7, 3.2, '1.2mm 미세 간격\n(영역 바깥 통과)', color='purple', fontsize=9, fontweight='bold')

    # Result Box for Panel A
    ax1.text(0.8, 8.1, '[오류] 기존 단선적 평가:\n궤적 중심선이 2D/3D 경계 안으로 안 들어옴\n→ 체류 시간 0초 → 체류 비율 0% (잘못된 착시)', 
             bbox=dict(boxstyle='round,pad=0.6', facecolor='mistyrose', edgecolor='red', alpha=0.9),
             fontsize=9.5, color='darkred', fontweight='bold')

    # 3D Depth Note
    ax1.text(0.8, 0.5, '※ Z축 3D 공간 상으로도 1.2mm 이격되어 실제 절제 부위를 스쳐 통과함',
             fontsize=8.5, color='purple', fontweight='bold')

    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 9.5)
    ax1.set_xlabel('공간 X 축 (mm)')
    ax1.set_ylabel('공간 Y 축 (mm)')
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='lower right', fontsize=8, frameon=True)

    # --------------------------------------------------------------------------
    # Panel B: 3D Distance Metric Solution d(t)
    # --------------------------------------------------------------------------
    ax2 = axes[1]
    ax2.set_title('(B) 해결책: 3D 최소 거리 d(t) 피처 적용', fontweight='bold', pad=12)

    # Plot Distance over time
    t = np.linspace(0, 30, 100)
    d_t = 15.0 - 0.7 * t + 0.5 * np.sin(0.5 * t)
    d_t[d_t < 1.2] = 1.2 + 0.1 * np.sin(2 * t[d_t < 1.2])  # Approaches 1.2mm minimum

    ax2.plot(t, d_t, color='darkblue', linewidth=2.5, label='3D 최소 거리 d(t)')
    ax2.axhline(0, color='limegreen', linestyle='--', linewidth=2, label='수술 절제 영역 경계 (0mm)')
    ax2.axhline(1.2, color='purple', linestyle=':', linewidth=1.8, label='최저 근접 거리 (1.2mm)')

    ax2.annotate('체류 비율은 0%이지만\n최소 거리가 1.2mm로\n수술 부위와 밀접함을 포착!', 
                 xy=(20, 1.2), xytext=(12, 7.0),
                 arrowprops=dict(arrowstyle='->', color='purple', lw=2),
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='lavender', edgecolor='purple', alpha=0.9),
                 fontsize=10, color='purple', fontweight='bold')

    # Result Box for Panel B
    ax2.text(1.0, 13.5, '[해결] min_dist_to_resect 피처 적용:\n   SEEG 희소 샘플링 오차 보완', 
             bbox=dict(boxstyle='round,pad=0.6', facecolor='honeydew', edgecolor='green', alpha=0.9),
             fontsize=10, color='darkgreen', fontweight='bold')

    ax2.set_xlim(0, 30)
    ax2.set_ylim(-1, 16)
    ax2.set_xlabel('진행 시간 t (초)')
    ax2.set_ylabel('절제 영역과의 거리 d(t) [mm]')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(loc='upper right', fontsize=8, frameon=True)

    plt.suptitle('SEEG 희소 샘플링 한계와 체류 비율 0% 착시 현상 해명 다이어그램', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])

    out_file = 'seeg_sparse_sampling_figure.png'
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"=== SEEG Sparse Sampling Figure Generated ===")
    print(f"File Saved: {out_file} ({os.path.getsize(out_file)} bytes)")

if __name__ == '__main__':
    generate_seeg_artifact_figure()
