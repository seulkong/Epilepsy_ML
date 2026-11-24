#!/usr/bin/env python3
"""
Custom Presentation Slide Figure Generator (Zero Overlap):
MNI 152 3D Coordinate Space & iEEG Seizure Trajectory
------------------------------------------------------
Generates a 300 DPI publication-grade figure with zero label overlap.
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Set Korean Font (AppleGothic)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11

def generate_mni_slide_plot():
    fig = plt.figure(figsize=(16, 7), dpi=300)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.2, 1.0], wspace=0.30)

    np.random.seed(42)

    # 1. Simulate 3D MNI Brain Grid & Electrodes
    n_electrodes = 64
    elec_x = np.random.uniform(-45, 45, n_electrodes)
    elec_y = np.random.uniform(-50, 40, n_electrodes)
    elec_z = np.random.uniform(-30, 50, n_electrodes)

    # 3D Seizure Trajectory Path P(t)
    t = np.linspace(0, 30, 150)
    traj_x = -25.0 + 1.6 * t + 3.0 * np.sin(0.4 * t)
    traj_y = -30.0 + 1.4 * t + 2.5 * np.cos(0.5 * t)
    traj_z = -10.0 + 0.9 * t + 4.0 * np.sin(0.3 * t)

    # --------------------------------------------------------------------------
    # Panel A: MNI 3D Coordinate Space & Trajectory Path
    # --------------------------------------------------------------------------
    ax3d = fig.add_subplot(gs[0], projection='3d')
    
    # Draw MNI Origin Axes (0,0,0)
    ax3d.plot([-60, 60], [0, 0], [0, 0], color='red', linestyle=':', alpha=0.5, label='X 축 (좌-우 mm)')
    ax3d.plot([0, 0], [-60, 60], [0, 0], color='green', linestyle=':', alpha=0.5, label='Y 축 (전-후 mm)')
    ax3d.plot([0, 0], [0, 0], [-50, 60], color='blue', linestyle=':', alpha=0.5, label='Z 축 (상-하 mm)')

    # Draw Electrodes
    ax3d.scatter(elec_x, elec_y, elec_z, c='gray', alpha=0.4, s=30, label='iEEG 전극 접점 (64개)')

    # Draw Trajectory
    sc = ax3d.scatter(traj_x, traj_y, traj_z, c=t, cmap='plasma', s=25, alpha=0.9)
    ax3d.plot(traj_x, traj_y, traj_z, color='darkmagenta', linewidth=2.0, alpha=0.8)

    ax3d.scatter(traj_x[0], traj_y[0], traj_z[0], color='crimson', s=140, marker='*', label='SOZ 발작 시작점 (t=0초)', zorder=10)
    ax3d.scatter(traj_x[-1], traj_y[-1], traj_z[-1], color='gold', s=100, marker='o', label='전파 종료점 (t=30초)', zorder=10)

    ax3d.set_title('(A) MNI 152 3D 입체 표준 좌표계 (X, Y, Z mm)', fontweight='bold', pad=15)
    ax3d.set_xlabel('MNI X (mm)', labelpad=8)
    ax3d.set_ylabel('MNI Y (mm)', labelpad=8)
    ax3d.set_zlabel('MNI Z (mm)', labelpad=8)
    ax3d.view_init(elev=22, azim=-50)
    
    cbar = fig.colorbar(sc, ax=ax3d, shrink=0.55, pad=0.14)
    cbar.set_label('진행 시간 t (초)', labelpad=10)
    ax3d.legend(loc='upper left', fontsize=8, frameon=True)

    # --------------------------------------------------------------------------
    # Panel B: MNI 3D Slice Projections (Coronal, Sagittal, Axial) with Clean Spacing
    # --------------------------------------------------------------------------
    gs_sub = gs[1].subgridspec(3, 1, hspace=0.7)

    # Axial Projection (XY plane, Z height)
    ax_axial = fig.add_subplot(gs_sub[0])
    ax_axial.scatter(elec_x, elec_y, c='gray', alpha=0.4, s=20)
    ax_axial.plot(traj_x, traj_y, color='darkmagenta', linewidth=1.8)
    ax_axial.scatter(traj_x[0], traj_y[0], color='crimson', s=80, marker='*')
    ax_axial.set_title('Axial 횡단면 (X-Y 평면)', fontweight='bold', pad=6)
    ax_axial.set_xlabel('X (mm)', labelpad=2)
    ax_axial.set_ylabel('Y (mm)', labelpad=2)
    ax_axial.grid(True, linestyle=':', alpha=0.5)

    # Coronal Projection (XZ plane, Y depth)
    ax_coronal = fig.add_subplot(gs_sub[1])
    ax_coronal.scatter(elec_x, elec_z, c='gray', alpha=0.4, s=20)
    ax_coronal.plot(traj_x, traj_z, color='darkmagenta', linewidth=1.8)
    ax_coronal.scatter(traj_x[0], traj_z[0], color='crimson', s=80, marker='*')
    ax_coronal.set_title('Coronal 관상면 (X-Z 평면)', fontweight='bold', pad=6)
    ax_coronal.set_xlabel('X (mm)', labelpad=2)
    ax_coronal.set_ylabel('Z (mm)', labelpad=2)
    ax_coronal.grid(True, linestyle=':', alpha=0.5)

    # Sagittal Projection (YZ plane, X width)
    ax_sagittal = fig.add_subplot(gs_sub[2])
    ax_sagittal.scatter(elec_y, elec_z, c='gray', alpha=0.4, s=20)
    ax_sagittal.plot(traj_y, traj_z, color='darkmagenta', linewidth=1.8)
    ax_sagittal.scatter(traj_y[0], traj_z[0], color='crimson', s=80, marker='*')
    ax_sagittal.set_title('Sagittal 시상면 (Y-Z 평면)', fontweight='bold', pad=6)
    ax_sagittal.set_xlabel('Y (mm)', labelpad=2)
    ax_sagittal.set_ylabel('Z (mm)', labelpad=2)
    ax_sagittal.grid(True, linestyle=':', alpha=0.5)

    plt.suptitle('MNI 152 3D 표준 좌표계 기반 전극 정합 및 발작 궤적 시각화', fontsize=14, fontweight='bold', y=0.98)

    out_file = 'mni_coordinates_slide_figure.png'
    plt.savefig(out_file, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"=== Zero Overlap MNI Slide Figure Generated ===")
    print(f"File Saved: {out_file} ({os.path.getsize(out_file)} bytes)")

if __name__ == '__main__':
    generate_mni_slide_plot()
