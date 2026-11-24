#!/usr/bin/env python3
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Set Korean Font
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

def generate_real_patient_figure():
    # 1. Load real data
    data = np.load('timeseries_dataset.npz')
    X_seq = data['X_seq']
    groups = data['groups']
    
    # Pick the first patient as an example
    patient_idx = 0
    patient_id = groups[patient_idx]
    seq = X_seq[patient_idx]
    
    # Filter out zero-padding
    # A valid step has non-zero velocity or position (since origin is extremely rare in MNI)
    valid_len = len(seq)
    for i in range(len(seq)):
        if np.all(seq[i] == 0):
            valid_len = i
            break
            
    seq = seq[:valid_len]
    t = np.arange(valid_len) * 0.5  # 0.5s per step
    
    traj_x = seq[:, 0]
    traj_y = seq[:, 1]
    traj_z = seq[:, 2]
    dist_mm = seq[:, 3]
    in_mask = seq[:, 4]
    velocity = seq[:, 5]
    
    # Calculate Residence Ratio (%)
    cum_residence = np.cumsum(in_mask) / (np.arange(valid_len) + 1) * 100.0
    
    # Calculate Spatial Dispersion (Var(R)) over a window
    dispersion = np.zeros(valid_len)
    for i in range(valid_len):
        start_idx = max(0, i-20)
        dispersion[i] = (np.var(traj_x[start_idx:i+1]) + 
                         np.var(traj_y[start_idx:i+1]) + 
                         np.var(traj_z[start_idx:i+1]))

    # --------------------------------------------------------------------------
    # Layout Setup
    # --------------------------------------------------------------------------
    fig = plt.figure(figsize=(15, 10), dpi=300)
    gs = fig.add_gridspec(2, 3, width_ratios=[1.4, 1.0, 1.0], height_ratios=[1.0, 1.0])

    # Subplot A: 3D Trajectory in MNI Space
    ax3d = fig.add_subplot(gs[:, 0], projection='3d')
    
    sc = ax3d.scatter(traj_x, traj_y, traj_z, c=t, cmap='viridis', s=30, alpha=0.9)
    ax3d.plot(traj_x, traj_y, traj_z, color='navy', linewidth=1.5, alpha=0.7, linestyle='--')

    ax3d.scatter(traj_x[0], traj_y[0], traj_z[0], color='crimson', s=150, marker='*', label='SOZ 발작 시작점 (t=0초)', zorder=10)
    ax3d.scatter(traj_x[-1], traj_y[-1], traj_z[-1], color='gold', s=120, marker='o', label=f'전파 종료점 (t={t[-1]:.1f}초)', zorder=10)

    ax3d.set_title(f'(A) 실제 환자({patient_id}) MNI 3D 발작 궤적 R(t)', fontweight='bold', pad=15)
    ax3d.set_xlabel('MNI X 좌표 (mm)')
    ax3d.set_ylabel('MNI Y 좌표 (mm)')
    ax3d.set_zlabel('MNI Z 좌표 (mm)')
    
    # Adjust view angle based on coordinates to see it well
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
    avg_vel = np.mean(velocity)
    ax_c.axhline(avg_vel, color='black', linestyle=':', label=f'평균 속도 ({avg_vel:.2f} mm/s)')
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
    ax_d.set_ylim(-5, 105)
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

    plt.suptitle(f'실제 환자({patient_id}) 데이터 기반 3D 발작 전파 궤적 및 정량 피처', fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    output_path = 'real_patient_3d_trajectory_figure.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f"=== Real Patient Figure Successfully Generated ===")
    print(f"File Saved: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == '__main__':
    generate_real_patient_figure()
