#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

def generate_comparison_figure():
    data = np.load('timeseries_dataset.npz')
    X_seq = data['X_seq']
    groups = data['groups']
    
    # 0 = Success (sub-HUP070), 157 = Failure (sub-HUP172)
    indices = [0, 157]
    titles = ['(A) 수술 성공군 (sub-HUP070)', '(B) 수술 실패군 (sub-HUP172)']
    
    fig = plt.figure(figsize=(15, 10), dpi=300)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.2, 1.0, 1.0])
    
    for row, idx in enumerate(indices):
        patient_id = groups[idx]
        seq = X_seq[idx]
        
        valid_len = len(seq)
        for i in range(len(seq)):
            if np.all(seq[i] == 0):
                valid_len = i
                break
                
        seq = seq[:valid_len]
        t = np.arange(valid_len) * 0.5
        
        traj_x = seq[:, 0]
        traj_y = seq[:, 1]
        traj_z = seq[:, 2]
        dist_mm = seq[:, 3]
        in_mask = seq[:, 4]
        velocity = seq[:, 5]
        
        dispersion = np.zeros(valid_len)
        for i in range(valid_len):
            start_idx = max(0, i-20)
            dispersion[i] = (np.var(traj_x[start_idx:i+1]) + 
                             np.var(traj_y[start_idx:i+1]) + 
                             np.var(traj_z[start_idx:i+1]))
        
        # 3D Trajectory
        ax3d = fig.add_subplot(gs[row, 0], projection='3d')
        sc = ax3d.scatter(traj_x, traj_y, traj_z, c=t, cmap='viridis', s=30, alpha=0.9)
        ax3d.plot(traj_x, traj_y, traj_z, color='navy', linewidth=1.5, alpha=0.7, linestyle='--')
        ax3d.scatter(traj_x[0], traj_y[0], traj_z[0], color='crimson', s=150, marker='*', label='SOZ 시작점', zorder=10)
        ax3d.scatter(traj_x[-1], traj_y[-1], traj_z[-1], color='gold', s=120, marker='o', label='종료점', zorder=10)
        ax3d.set_title(f'{titles[row]} - MNI 발작 궤적 R(t)', fontweight='bold', pad=10)
        ax3d.set_xlabel('MNI X (mm)')
        ax3d.set_ylabel('MNI Y (mm)')
        ax3d.set_zlabel('MNI Z (mm)')
        ax3d.view_init(elev=20, azim=-55)
        
        cbar = fig.colorbar(sc, ax=ax3d, shrink=0.6, pad=0.15)
        if row == 0:
            cbar.set_label('진행 시간 t (초)', labelpad=10)
        ax3d.legend(loc='upper left', fontsize=8, frameon=True)

        # Velocity
        ax_v = fig.add_subplot(gs[row, 1])
        ax_v.plot(t, velocity, color='crimson', linewidth=1.8, label='전파 속도 v(t)')
        avg_vel = np.mean(velocity)
        ax_v.axhline(avg_vel, color='black', linestyle=':', label=f'평균 속도 ({avg_vel:.2f} mm/s)')
        ax_v.axhline(9.24, color='red', linestyle='--', alpha=0.7, label='위험 기준선 (9.24 mm/s)')
        ax_v.set_title(f'{titles[row]} - 전파 속도', fontweight='bold')
        ax_v.set_ylabel('속도 (mm/s)')
        ax_v.set_xlabel('시간 (초)')
        
        # Determine y-limit max for better comparison or let it auto scale
        ax_v.set_ylim(0, max(25, np.max(velocity) + 5))
        ax_v.grid(True, linestyle=':', alpha=0.6)
        ax_v.legend(fontsize=8)

        # Trajectory Dispersion
        ax_r = fig.add_subplot(gs[row, 2])
        ax_r.plot(t, dispersion, color='purple', linewidth=2.0, label='공간 분산 Var(R)')
        ax_r.set_title(f'{titles[row]} - 3D 공간 궤적 분산도', fontweight='bold')
        ax_r.set_ylabel('공간 분산 (mm²)')
        ax_r.set_xlabel('시간 (초)')
        ax_r.grid(True, linestyle=':', alpha=0.6)
        ax_r.legend(fontsize=8)

    plt.suptitle('수술 성공군 vs 실패군 발작 전파 동역학 비교 분석', fontsize=16, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    output_path = 'compare_patients_trajectory_figure.png'
    svg_path = 'compare_patients_trajectory_figure.svg'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.savefig(svg_path, format='svg', bbox_inches='tight')
    plt.close()
    print(f"Generated {output_path} and {svg_path}")

if __name__ == '__main__':
    generate_comparison_figure()
