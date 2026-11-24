#!/usr/bin/env python3
"""
Publication-Quality Model Architecture Diagram Generator (Refined & Polished)
------------------------------------------------------------------------------
Generates a perfectly proportioned, beautiful, horizontal 2x2 layout diagram
with clear typography (Apple SD Gothic Neo), balanced spacing, and clean arrows.
Output: model_architecture.png (15x8.5 inches, 300 DPI)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# Configure fonts
plt.rcParams['font.family'] = 'Apple SD Gothic Neo'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 1.0

fig, ax = plt.subplots(figsize=(15, 8.5), dpi=300)
ax.set_xlim(0, 15)
ax.set_ylim(0, 8.5)
ax.axis('off')

# Color Palette (Pastel with High-Contrast Text)
c_bg_data = '#f0f7fd'
c_bd_data = '#1976d2'

c_bg_feat = '#fffbf0'
c_bd_feat = '#f57c00'

c_bg_mod = '#fbf2fb'
c_bd_mod = '#7b1fa2'

c_bg_out = '#f1f8f3'
c_bd_out = '#2e7d32'
c_node_succ = '#e8f5e9'
c_bd_succ = '#2e7d32'
c_node_warn = '#ffebee'
c_bd_warn = '#c62828'

def draw_subgraph_box(x, y, w, h, bg_color, bd_color, title_text):
    """Draws a rounded outer container box with a clear header title."""
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.25",
                         facecolor=bg_color, edgecolor=bd_color, linewidth=1.6, zorder=1)
    ax.add_patch(box)
    # Header title
    ax.text(x + w/2, y + h - 0.35, title_text,
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#1a1a1a', zorder=3)
    # Divider line
    ax.plot([x + 0.3, x + w - 0.3], [y + h - 0.68, y + h - 0.68],
            color=bd_color, linewidth=1.0, linestyle=':', alpha=0.6, zorder=2)

def draw_node(x, y, w, h, text, subtext="", bg_color='#ffffff', bd_color='#90caf9',
              txt_color='#1565c0', fontsize=10.5, sub_fontsize=9.0, zorder=4):
    """Draws an inner node with title and descriptive subtext."""
    node = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle="round,pad=0.06,rounding_size=0.16",
                          facecolor=bg_color, edgecolor=bd_color, linewidth=1.3, zorder=zorder)
    ax.add_patch(node)
    if subtext:
        ax.text(x, y + 0.18, text, ha='center', va='center', fontsize=fontsize,
                fontweight='bold', color=txt_color, zorder=zorder+1)
        ax.text(x, y - 0.18, subtext, ha='center', va='center', fontsize=sub_fontsize,
                color='#424242', zorder=zorder+1, multialignment='center')
    else:
        ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
                fontweight='bold', color=txt_color, zorder=zorder+1)

def draw_arrow(x1, y1, x2, y2, color='#455a64', style='->', rad=0.0, zorder=5, lw=1.6):
    """Draws a connection arrow."""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                            connectionstyle=f"arc3,rad={rad}",
                            arrowstyle=style, mutation_scale=13,
                            color=color, linewidth=lw, zorder=zorder)
    ax.add_patch(arrow)


# ==============================================================================
# 1. Box 1: 다중 코호트 데이터 입력 & 초기 30초 윈도우 분할 (Top-Left)
# ==============================================================================
draw_subgraph_box(0.5, 4.4, 6.7, 3.7, c_bg_data, c_bd_data,
                  "1. 다중 코호트 데이터 입력 및 초기 30초 윈도우 분할")

draw_node(2.05, 7.05, 2.7, 0.75, "HUP iEEG 코호트", "ds004100 (55명 / 203개 발작)",
          bg_color='#ffffff', bd_color='#64b5f6', txt_color='#0d47a1')

draw_node(5.45, 7.05, 3.1, 0.75, "발작 초기 30초 (0–30s) 분할", "MNI 152 3D 전극 좌표 정합",
          bg_color='#e3f2fd', bd_color='#1976d2', txt_color='#0d47a1')

draw_arrow(3.4, 7.05, 3.9, 7.05, color='#1976d2')

draw_node(2.05, 5.25, 2.7, 0.75, "외부 코호트 (SWEC-ETHZ)", "16명 환자 / 100개 발작",
          bg_color='#ffffff', bd_color='#64b5f6', txt_color='#0d47a1')

draw_node(5.45, 5.25, 3.1, 0.75, "대조학습 (SimCLR 1D-CNN)", "생체신호 5대 증강 사전학습",
          bg_color='#e3f2fd', bd_color='#1976d2', txt_color='#0d47a1')

draw_arrow(3.4, 5.25, 3.9, 5.25, color='#1976d2')


# ==============================================================================
# 2. Box 2: 23차원 멀티모달 피처 추출 (Top-Right)
# ==============================================================================
draw_subgraph_box(7.8, 4.4, 6.7, 3.7, c_bg_feat, c_bd_feat,
                  "2. 23차원 멀티모달 피처 추출 및 표현 학습")

draw_node(11.15, 7.15, 6.1, 0.72, "Group A: 3차원 공간 궤적 동역학 (6종)",
          "초기 30초 평균/최고속도, 절제구역 체류비율, 궤적 분산도, 최소/평균거리",
          bg_color='#ffffff', bd_color='#ffb74d', txt_color='#e65100')

draw_node(11.15, 6.15, 6.1, 0.72, "Group B: 환자 임상 및 인구학적 메타데이터 (9종)",
          "연령, 발병 연령, 유병기간, 성별, 치료법, 병변 유무, SOZ 및 절제 전극수",
          bg_color='#ffffff', bd_color='#ffb74d', txt_color='#e65100')

draw_node(11.15, 5.15, 6.1, 0.72, "Group C: 외부 사전학습 SSL 잠재 표상 (8종)",
          "128차원 대조학습 인코더 임베딩 → PCA 주성분 분석 8차원 압축",
          bg_color='#ffffff', bd_color='#ffb74d', txt_color='#e65100')


# ==============================================================================
# 3. Box 3: 제안 멀티모달 복합 모델 & 환자 단위 검증 (Bottom-Left)
# ==============================================================================
draw_subgraph_box(0.5, 0.4, 6.7, 3.6, c_bg_mod, c_bd_mod,
                  "3. 제안 멀티모달 복합 모델 구축 및 엄격 검증")

draw_node(1.8, 2.2, 2.2, 0.85, "23개 피처 융합", "멀티모달 통합 벡터\n(Group A + B + C)",
          bg_color='#f3e5f5', bd_color='#ba68c8', txt_color='#4a148c')

draw_node(3.9, 2.2, 2.3, 0.85, "환자 단위 교차검증", "10회 반복 5-Fold 계층화\n(StratifiedGroupKFold, 50회)",
          bg_color='#ffffff', bd_color='#ab47bc', txt_color='#4a148c')

draw_arrow(2.9, 2.2, 3.25, 2.2, color='#7b1fa2')

draw_node(5.95, 2.2, 2.1, 1.1, "최적 임계값 도출", "전파속도 ≤ 9.24 mm/s\n성공확률 P ≥ 0.61\n(특이도 80.9% 달성)",
          bg_color='#ffffff', bd_color='#8e24aa', txt_color='#4a148c', fontsize=10.0, sub_fontsize=8.5)

draw_arrow(4.55, 2.2, 4.9, 2.2, color='#7b1fa2')


# ==============================================================================
# 4. Box 4: 임상 의사결정 지원 & 맞춤형 치료법 추천 (CDSS) (Bottom-Right)
# ==============================================================================
draw_subgraph_box(7.8, 0.4, 6.7, 3.6, c_bg_out, c_bd_out,
                  "4. 임상 의사결정 지원 (CDSS) 및 개인화 치료법 추천")

draw_node(9.1, 2.2, 2.2, 1.05, "초기 30초\n복합 위험도 평가", "속도 & 모델 점수 판별\n(Youden Cutoff 최적화)",
          bg_color='#ffffff', bd_color='#66bb6a', txt_color='#1b5e20')

draw_node(12.7, 2.9, 4.3, 0.85, "개두 절제술 (Open Resection) 강력 권고",
          "저속 국소형 (v ≤ 9.24 mm/s & P ≥ 0.61) → 발작 소실(Engel I) 최적군",
          bg_color=c_node_succ, bd_color=c_bd_succ, txt_color='#1b5e20')

draw_node(12.7, 1.45, 4.3, 0.85, "신경자극술 (RNS/DBS) 또는 소작술 (LITT) 권고",
          "초고속 원격형 (v > 9.24 mm/s & P < 0.61) → 과도 절제 방지 및 대안치료",
          bg_color=c_node_warn, bd_color=c_bd_warn, txt_color='#b71c1c')

draw_arrow(10.2, 2.5, 10.55, 2.9, color='#2e7d32', rad=-0.08)
draw_arrow(10.2, 1.9, 10.55, 1.45, color='#c62828', rad=0.08)


# ==============================================================================
# Inter-Subgraph Connectors (Major Flow 1 -> 2 -> 3 -> 4)
# ==============================================================================
# Step 1 -> Step 2
draw_arrow(7.0, 7.05, 8.1, 7.15, color='#e65100', style='-|>', rad=0.06, lw=2.2)
draw_arrow(7.0, 5.25, 8.1, 5.15, color='#e65100', style='-|>', rad=-0.06, lw=2.2)

# Step 2 -> Step 3 (Graceful arc from Step 2 left edge to Step 3 top edge)
arrow_p23 = FancyArrowPatch((7.8, 4.6), (2.8, 4.0),
                            connectionstyle="arc3,rad=-0.14",
                            arrowstyle='-|>', mutation_scale=14,
                            color='#7b1fa2', linewidth=2.2, zorder=5)
ax.add_patch(arrow_p23)

# Step 3 -> Step 4
draw_arrow(7.2, 2.2, 7.8, 2.2, color='#2e7d32', style='-|>', rad=0.0, lw=2.2)

# Flow Badges
ax.text(7.45, 6.15, '①→②', ha='center', va='center', fontsize=10, fontweight='bold',
        color='#b74d00', bbox=dict(boxstyle='round,pad=0.25', facecolor='#fff3e0', edgecolor='#ffb74d', alpha=0.95))
ax.text(5.3, 4.45, '②→③', ha='center', va='center', fontsize=10, fontweight='bold',
        color='#4a148c', bbox=dict(boxstyle='round,pad=0.25', facecolor='#f3e5f5', edgecolor='#ba68c8', alpha=0.95))
ax.text(7.5, 2.45, '③→④', ha='center', va='center', fontsize=10, fontweight='bold',
        color='#1b5e20', bbox=dict(boxstyle='round,pad=0.25', facecolor='#e8f5e9', edgecolor='#81c784', alpha=0.95))

plt.tight_layout()
output_path = 'model_architecture.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', transparent=False)
plt.savefig('model_architecture.svg', format='svg', bbox_inches='tight')
plt.close(fig)
print(f"Refined model_architecture.png and model_architecture.svg generated successfully.")
