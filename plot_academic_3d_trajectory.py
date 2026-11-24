#!/usr/bin/env python3
"""
Academic Paper Figure Generator (Korean Version):
3D Seizure Trajectory & Quantitative Feature Calculation Framework
------------------------------------------------------------------
Generates a 300 DPI publication-grade figure with Korean typography:
  Figure 1A: (A) MNI 3D 좌표 공간 발작 궤적 R(t)
  Figure 1B: (B) 수술 절제 영역과의 3D 최소 거리 d(t) [mm]
  Figure 1C: (C) 뇌파 발작 전파 속도 v(t) [mm/s]
  Figure 1D: (D) 절제 구역 체류 비율 [%]
  Figure 1E: (E) 3D 공간 궤적 분산도 [mm^2]
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Set Korean Font for Mac (AppleGothic)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

def generate_korean_academic_figure():
    np.random.seed(42)

    # 1. 3D MNI Brain Grid & Electrodes Simulation
    n_electrodes = 64
    elec_x = np.random.uniform(-45, 45, n_electrodes)
    elec_y = np.random.uniform(-50, 40, n_electrodes)
    elec_z = np.random.uniform(-30, 50, n_electrodes)

    # 2. 3D Resection Volume Ellipsoid
    center_resect = np.array([20.0, 10.0, 15.0])
    rx, ry, rz = 18.0, 15.0, 20.0

    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    mesh_x = center_resect[0] + rx * np.outer(np.cos(u), np.sin(v))
    mesh_y = center_resect[1] + ry * np.outer(np.sin(u), np.sin(v))
    mesh_z = center_resect[2] + rz * np.outer(np.ones(np.size(u)), np.cos(v))

    # 3. 3D Seizure Trajectory R(t) over Time (0 ~ 30s)
    t = np.linspace(0, 30, 200)
    traj_x = -30.0 + 1.8 * t + 4.0 * np.sin(0.4 * t)
    traj_y = -35.0 + 1.5 * t + 3.0 * np.cos(0.5 * t)
    traj_z = -15.0 + 1.0 * t + 5.0 * np.sin(0.3 * t)

    # Calculate 4 Quantitative Features
    distances = np.sqrt(((traj_x - center_resect[0])/rx)**2 + 
                        ((traj_y - center_resect[1])/ry)**2 + 
                        ((traj_z - center_resect[2])/rz)**2)
    dist_mm = np.maximum(0, (distances - 1.0) * 15.0)

    inside_mask = distances <= 1.0
    cum_residence = np.cumsum(inside_mask) / (np.arange(len(t)) + 1) * 100.0

    dx = np.diff(traj_x, prepend=traj_x[0])
    dy = np.diff(traj_y, prepend=traj_y[0])
    dz = np.diff(traj_z, prepend=traj_z[0])
    dt = t[1] - t[0]
    velocity = np.sqrt(dx**2 + dy**2 + dz**2) / dt
    velocity[0] = velocity[1]

    dispersion = np.array([np.var(traj_x[max(0, i-20):i+1]) + 
                           np.var(traj_y[max(0, i-20):i+1]) + 
                           np.var(traj_z[max(0, i-20):i+1]) for i in range(len(t))])

    # --------------------------------------------------------------------------
    # Layout Setup
    # --------------------------------------------------------------------------
    fig = plt.figure(figsize=(15, 10), dpi=300)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.4, 1.0, 1.0], height_ratios=[1.0, 1.0])

    # Subplot A: 3D Trajectory in MNI Space
    ax3d = fig.add_subplot(gs[:, 0], projection='3d')
    ax3d.scatter(elec_x, elec_y, elec_z, c='gray', alpha=0.4, s=25, label='iEEG 전극 접점 (64개)')
    ax3d.plot_surface(mesh_x, mesh_y, mesh_z, color='limegreen', alpha=0.25, edgecolor='green', linewidth=0.3)

    sc = ax3d.scatter(traj_x, traj_y, traj_z, c=t, cmap='viridis', s=20, alpha=0.9)
    ax3d.plot(traj_x, traj_y, traj_z, color='navy', linewidth=1.5, alpha=0.7, linestyle='--')

    ax3d.scatter(traj_x[0], traj_y[0], traj_z[0], color='crimson', s=120, marker='*', label='SOZ 발작 시작점 (t=0초)', zorder=10)
    ax3d.scatter(traj_x[-1], traj_y[-1], traj_z[-1], color='gold', s=100, marker='o', label='전파 종료점 (t=30초)', zorder=10)

    ax3d.set_title('(A) MNI 3D 좌표 공간 발작 궤적 R(t)', fontweight='bold', pad=15)
    ax3d.set_xlabel('MNI X 좌표 (mm)')
    ax3d.set_ylabel('MNI Y 좌표 (mm)')
    ax3d.set_zlabel('MNI Z 좌표 (mm)')
    ax3d.view_init(elev=20, azim=-55)
    cbar = fig.colorbar(sc, ax=ax3d, shrink=0.55, pad=0.15)
    cbar.set_label('진행 시간 t (초)', labelpad=15)
    ax3d.legend(loc='upper left', fontsize=8, frameon=True)

    # Subplot B: Distance to Resection
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.plot(t, dist_mm, color='darkblue', linewidth=2.0, label='최소 거리 d(t)')
    ax_b.axhline(0, color='limegreen', linestyle='--', label='수술 절제 영역 경계')
    ax_b.set_title('(B) 수술 절제 영역과의 3D 최소 거리', fontweight='bold')
    ax_b.set_ylabel('거리 (mm)')
    ax_b.set_xlabel('시간 (초)')
    ax_b.grid(True, linestyle=':', alpha=0.6)
    ax_b.legend(fontsize=8)

    # Subplot C: Propagation Velocity
    ax_c = fig.add_subplot(gs[0, 2])
    ax_c.plot(t, velocity, color='crimson', linewidth=1.8, label='전파 속도 v(t)')
    ax_c.axhline(np.mean(velocity), color='black', linestyle=':', label=f'평균 속도 ({np.mean(velocity):.2f} mm/s)')
    ax_c.set_title('(C) 뇌파 발작 전파 속도', fontweight='bold')
    ax_c.set_ylabel('전파 속도 (mm/s)')
    ax_c.set_xlabel('시간 (초)')
    ax_c.grid(True, linestyle=':', alpha=0.6)
    ax_c.legend(fontsize=8)

    # Subplot D: Residence Ratio
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.plot(t, cum_residence, color='forestgreen', linewidth=2.0, label='누적 체류 비율 (%)')
    ax_d.axhline(50.0, color='darkorange', linestyle='--', label='50% 임상 임계값')
    ax_d.set_title('(D) 절제 구역 체류 비율', fontweight='bold')
    ax_d.set_ylabel('체류 비율 (%)')
    ax_d.set_xlabel('시간 (초)')
    ax_d.set_ylim(0, 105)
    ax_d.grid(True, linestyle=':', alpha=0.6)
    ax_d.legend(fontsize=8)

    # Subplot E: Trajectory Dispersion
    ax_e = fig.add_subplot(gs[1, 2])
    ax_e.plot(t, dispersion, color='purple', linewidth=1.8, label='공간 분산 Var(R)')
    ax_e.set_title('(E) 3D 공간 궤적 분산도', fontweight='bold')
    ax_e.set_ylabel('공간 분산 (mm²)')
    ax_e.set_xlabel('시간 (초)')
    ax_e.grid(True, linestyle=':', alpha=0.6)
    ax_e.legend(fontsize=8)

    plt.suptitle('iEEG 3D 발작 전파 궤적 및 4대 정량 피처 산출 프레임워크', fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    output_path = 'korean_academic_3d_trajectory_figure.png'
    svg_path = 'korean_academic_3d_trajectory_figure.svg'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.savefig(svg_path, format='svg', bbox_inches='tight')
    plt.close()

    print(f"=== Korean Academic Figure Successfully Generated ===")
    print(f"File Saved: {output_path} and {svg_path}")

if __name__ == '__main__':
    generate_korean_academic_figure()
