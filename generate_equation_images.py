#!/usr/bin/env python3
"""
Generate publication-quality, high-resolution large equation images for equations (1)-(14).
Font size increased to 24pt with 400 DPI for crystal clear, large display.
"""
import os
import matplotlib.pyplot as plt

plt.rcParams['mathtext.fontset'] = 'cm'

EQUATIONS = {
    1: r'$C_{SOZ} = \frac{1}{|K_{soz}|} \sum_{i \in K_{soz}} \mathbf{p}_i$',
    2: r'$C_{res} = \frac{1}{|K_{res}|} \sum_{j \in K_{res}} \mathbf{p}_j$',
    3: r'$d_0 = \| C_{SOZ} - C_{res} \|_2$',
    4: r'$R_{res} = \max_{j \in K_{res}} \| \mathbf{p}_j - C_{res} \|_2$',
    5: r'$w_k(t) = \frac{P_k(t)^2}{\sum_{m=1}^{N} P_m(t)^2}$',
    6: r'$\mathbf{R}(t) = \sum_{k=1}^{N} w_k(t) \, \mathbf{p}_k$',
    7: r'$v(t) = \frac{\| \mathbf{R}(t+\Delta t) - \mathbf{R}(t) \|_2}{\Delta t}$',
    8: r'$v_{mean} = \frac{1}{T-1} \sum_{t=1}^{T-1} v(t)$',
    9: r'$v_{max} = \max_{t} v(t)$',
    10: r'$R_{residence} = \frac{1}{T} \sum_{t=1}^{T} \mathbf{I}(\| \mathbf{R}(t) - C_{res} \|_2 \leq R_{res}) \times 100 \; (\%)$',
    11: r'$D_{disp} = \max_{t} \| \mathbf{R}(t) - C_{SOZ} \|_2$',
    12: r'$d_{min} = \min_{t} \| \mathbf{R}(t) - C_{res} \|_2$',
    13: r'$d_{mean} = \frac{1}{T} \sum_{t=1}^{T} \| \mathbf{R}(t) - C_{res} \|_2$',
    14: r'$\mathcal{L}_{i,j} = -\log \frac{\exp(\mathrm{sim}(\mathbf{z}_i, \mathbf{z}_j) / \tau)}{\sum_{k=1}^{2N} \mathbf{I}_{[k \neq i]} \exp(\mathrm{sim}(\mathbf{z}_i, \mathbf{z}_k) / \tau)}$'
}

os.makedirs('equations_img', exist_ok=True)

for eq_num, eq_tex in EQUATIONS.items():
    fig = plt.figure(figsize=(9, 1.6), dpi=300)
    plt.axis('off')
    plt.text(0.5, 0.5, eq_tex, fontsize=24, ha='center', va='center')
    out_file = f'equations_img/eq_{eq_num}.png'
    plt.savefig(out_file, bbox_inches='tight', transparent=True, dpi=300, pad_inches=0.08)
    plt.close(fig)
    print(f"Generated (Large): {out_file}")

print("All 14 equation images generated with 24pt large size successfully!")
