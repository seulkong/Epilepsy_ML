#!/usr/bin/env python3
"""
Detailed Model Architecture Diagram Generator (Flawless Typography & Spacing)
-----------------------------------------------------------------------------
Publication-grade 16:9 diagram:
1. 3 Feature Extraction Branches (1D-CNN SSL Encoder, 3D CoM Trajectory, Clinical Meta)
2. 23-Dimensional Multimodal Feature Fusion Layer (Leakage-Free Patient-Stratified CV)
3. Multi-Model Benchmark (Logistic Regression, Bi-LSTM, Ensemble)
4. Clinical Decision Support System (CDSS) Output (P >= 0.61 Cutoff & Patient Guidance)
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# Configure fonts & styles
plt.rcParams['font.sans-serif'] = ['Apple SD Gothic Neo', 'Malgun Gothic', 'NanumGothic', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# Canvas: 16.5 x 9.2 inches (1.79:1 ratio, matching PowerPoint 355x196mm slot)
fig, ax = plt.subplots(figsize=(16.5, 9.2), dpi=300)
ax.set_xlim(0, 16.5)
ax.set_ylim(0, 9.2)
ax.axis('off')

# Color Tokens
c_dark = '#0f172a'
c_slate = '#334155'
c_muted = '#64748b'

# Branch 1: Blue Palette (iEEG & 1D-CNN SSL)
c_blue_bg = '#f0f9ff'
c_blue_bd = '#0284c7'
c_blue_box = '#e0f2fe'
c_blue_txt = '#0369a1'

# Branch 2: Orange Palette (3D Trajectory Dynamics)
c_orange_bg = '#fffbeb'
c_orange_bd = '#d97706'
c_orange_box = '#fef3c7'
c_orange_txt = '#b45309'

# Branch 3: Teal Palette (Clinical Meta)
c_teal_bg = '#f0fdfa'
c_teal_bd = '#0d9488'
c_teal_box = '#ccfbf1'
c_teal_txt = '#0f766e'

# Column 2 & 3: Purple Palette (Fusion & Classifiers)
c_purple_bg = '#f5f3ff'
c_purple_bd = '#7c3aed'
c_purple_box = '#ede9fe'
c_purple_txt = '#6d28d9'

# Stage 4: Green & Rose Palette (CDSS Outcomes)
c_green_bg = '#ecfdf5'
c_green_bd = '#059669'
c_green_txt = '#047857'
c_rose_bg = '#fff1f2'
c_rose_bd = '#e11d48'
c_rose_txt = '#be123c'

# Helper: Container Card
def draw_card(x, y, w, h, bg_color, bd_color, title, subtitle=None):
    card = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.18",
                          facecolor=bg_color, edgecolor=bd_color, linewidth=1.5, zorder=1)
    ax.add_patch(card)
    
    # Title Banner Line
    ax.text(x + 0.22, y + h - 0.30, title, fontsize=11.8, fontweight='bold',
            color=bd_color, va='center', zorder=2)
    if subtitle:
        ax.text(x + w - 0.22, y + h - 0.30, subtitle, fontsize=9.2,
                color=c_muted, ha='right', va='center', zorder=2)
    
    # Divider line
    ax.plot([x + 0.18, x + w - 0.18], [y + h - 0.52, y + h - 0.52],
            color=bd_color, linewidth=0.8, alpha=0.35, zorder=2)

# Helper: Layer Block with perfect internal spacing (No overlapping!)
def draw_block(x, y, w, h, title, body_lines=None, bg_col='#ffffff', bd_col='#cbd5e1', txt_col=c_dark,
               title_size=10.0, body_size=8.5, title_weight='bold'):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.03,rounding_size=0.1",
                         facecolor=bg_col, edgecolor=bd_col, linewidth=1.2, zorder=3)
    ax.add_patch(box)
    
    if body_lines:
        # Title positioned in upper half
        ax.text(x, y + h*0.22, title, ha='center', va='center', fontsize=title_size,
                fontweight=title_weight, color=txt_col, zorder=4)
        # Body text positioned in lower half
        if isinstance(body_lines, list):
            body_str = "\n".join(body_lines)
        else:
            body_str = body_lines
        ax.text(x, y - h*0.20, body_str, ha='center', va='center', fontsize=body_size,
                color=c_dark, zorder=4, linespacing=1.2)
    else:
        ax.text(x, y, title, ha='center', va='center', fontsize=title_size,
                fontweight=title_weight, color=txt_col, zorder=4)

# Helper: Curved or Straight Arrow
def draw_arrow(x1, y1, x2, y2, color=c_slate, rad=0.0, lw=1.4):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                            connectionstyle=f"arc3,rad={rad}",
                            arrowstyle='-|>', mutation_scale=13,
                            color=color, linewidth=lw, zorder=10)
    ax.add_patch(arrow)

# ==============================================================================
# Header Section
# ==============================================================================
ax.text(8.25, 8.88, "다각적 피처 추출·자가지도학습(SSL) 인코더 및 23개 복합 예후 예측 모델 아키텍처",
        ha='center', va='center', fontsize=14.5, fontweight='bold', color=c_dark)
ax.text(8.25, 8.52, "Multimodal Fusion Architecture: 1D-CNN Self-Supervised Learning (8-d) + 3D Trajectory Dynamics (6-d) + Clinical Meta (9-d)",
        ha='center', va='center', fontsize=9.6, color=c_muted)

# ==============================================================================
# Column 1 (Left): Feature Extraction & Encoders (x: 0.5 ~ 6.8)
# ==============================================================================

# ------------------------------------------------------------------------------
# Branch 1 (Top): 1D-CNN Self-Supervised Learning (SSL) Encoder
# ------------------------------------------------------------------------------
draw_card(0.5, 4.85, 6.4, 3.40, c_blue_bg, c_blue_bd,
          "Group C: 자가지도학습(SSL) 생체 신호 인코더", "SWEC-ETHZ 16명 사전학습 $\\rightarrow$ ds004100")

# Input Waveform Node
draw_block(1.50, 7.35, 1.65, 0.65, "iEEG 원신호 입력", "4초(1,024 샘플), 256Hz",
           '#ffffff', c_blue_bd, c_blue_txt)

# Data Augmentation Node
draw_block(1.50, 6.00, 1.65, 1.30, "생체 신호 5대 증강",
           ["• 시간 원형 이동 (±0.5s)", "• 가우시안 잡음 (σ=0.1)", "• 주파수 밴드스톱 (4-12Hz)", "• 시간 마스킹 & 스케일링"],
           c_blue_box, c_blue_bd, c_blue_txt, title_size=9.5, body_size=8.0)
draw_arrow(1.50, 7.02, 1.50, 6.66, color=c_blue_bd)

# 5-Layer 1D-CNN Pipeline
conv_blocks = [
    ("Conv1D Block 1", "k=9, s=2, 1→32 채널"),
    ("Conv1D Block 2", "k=7, s=2, 32→64 채널"),
    ("Conv1D Block 3", "k=7, s=2, 64→128 채널"),
    ("Conv1D Block 4-5", "k=5/3, s=2, 128→128")
]
for i, (b_title, b_desc) in enumerate(conv_blocks):
    cy = 7.35 - i * 0.60
    draw_block(3.50, cy, 1.85, 0.48, b_title, b_desc,
               '#ffffff', '#38bdf8', '#0369a1', title_size=9.2, body_size=8.0)
    if i > 0:
        draw_arrow(3.50, cy + 0.48, 3.50, cy + 0.24, color='#0284c7')

# Connect Augmentation to Conv1D Block 1
draw_arrow(2.33, 6.00, 2.57, 7.35, rad=-0.15, color=c_blue_bd)

# GAP & Embedding Vector
draw_block(5.65, 7.20, 1.85, 0.78, "전역 풀링 & 잠재표상",
           ["GAP $\\rightarrow$ 128차원 벡터 (z)", "(양성쌍 검색정확도 87.9%)"],
           c_blue_box, c_blue_bd, c_blue_txt, title_size=9.5, body_size=8.0)
draw_arrow(4.43, 5.55, 5.65, 6.81, rad=-0.12, color=c_blue_bd)

# PCA Compression Node
draw_block(5.65, 5.85, 1.85, 0.88, "SOZ 풀링 & PCA 압축",
           ["SOZ 및 전체 전극 풀링", "PCA(k=8) 압축 차원 축소", "▶ SSL 표상 8개 피처"],
           '#ffffff', c_blue_bd, c_blue_txt, title_size=9.5, body_size=8.0)
draw_arrow(5.65, 6.81, 5.65, 6.29, color=c_blue_bd)

# ------------------------------------------------------------------------------
# Branch 2 (Middle): 3D Spatiotemporal Trajectory CoM Engine
# ------------------------------------------------------------------------------
draw_card(0.5, 2.65, 6.4, 2.00, c_orange_bg, c_orange_bd,
          "Group A: 3차원 시공간 질량 중심(CoM) 동역학 엔진", "발작 초기 30초 (0–30s)")

draw_block(1.50, 3.50, 1.65, 0.85, "3D 전극 & 전력 입력",
           ["MNI 152 공간 좌표 (p_k)", "힐베르트 전력 P_k(t)"],
           '#ffffff', c_orange_bd, c_orange_txt, title_size=9.5, body_size=8.2)

draw_block(3.50, 3.50, 1.85, 0.85, "3차원 전력 질량 중심",
           ["R(t) = Σ w_k(t) · p_k", "v(t) = ||ΔR|| / Δt (0.5s)"],
           c_orange_box, c_orange_bd, c_orange_txt, title_size=9.5, body_size=8.2)
draw_arrow(2.33, 3.50, 2.57, 3.50, color=c_orange_bd)

draw_block(5.65, 3.50, 1.85, 0.85, "6대 궤적 동역학 피처",
           ["v_mean, v_max, R_res", "D_disp, d_min, d_mean"],
           '#ffffff', c_orange_bd, c_orange_txt, title_size=9.5, body_size=8.2)
draw_arrow(4.43, 3.50, 4.72, 3.50, color=c_orange_bd)

# ------------------------------------------------------------------------------
# Branch 3 (Bottom): Clinical & Demographic Metadata
# ------------------------------------------------------------------------------
draw_card(0.5, 0.60, 6.4, 1.85, c_teal_bg, c_teal_bd,
          "Group B: 임상 및 인구학적 메타데이터", "환자 코호트 (ds004100, 55명)")

draw_block(1.50, 1.38, 1.65, 0.75, "환자 임상 기록", "55명 수술 환자 메타데이터",
           '#ffffff', c_teal_bd, c_teal_txt, title_size=9.5, body_size=8.2)

draw_block(3.50, 1.38, 1.85, 0.75, "원-핫 인코딩 & 정규화", "표준 스케일러 (StandardScaler)",
           c_teal_box, c_teal_bd, c_teal_txt, title_size=9.5, body_size=8.2)
draw_arrow(2.33, 1.38, 2.57, 1.38, color=c_teal_bd)

draw_block(5.65, 1.38, 1.85, 0.75, "9대 임상 피처",
           ["나이, 성별, 유병기간", "절제마진, 병변타입 등"],
           '#ffffff', c_teal_bd, c_teal_txt, title_size=9.5, body_size=8.2)
draw_arrow(4.43, 1.38, 4.72, 1.38, color=c_teal_bd)


# ==============================================================================
# Column 2 (Center): Multimodal Feature Fusion Layer (x: 7.2 ~ 10.4)
# ==============================================================================
draw_card(7.2, 0.60, 3.2, 7.65, c_purple_bg, c_purple_bd,
          "23개 멀티모달 피처 융합", "Fusion & Validation")

# Connect 3 Feature Branches to Fusion Layer
draw_arrow(6.58, 5.85, 7.20, 6.20, color=c_blue_bd, lw=1.8)
draw_arrow(6.58, 3.50, 7.20, 3.90, color=c_orange_bd, lw=1.8)
draw_arrow(6.58, 1.38, 7.20, 2.10, color=c_teal_bd, lw=1.8)

# Concatenation Box
draw_block(8.80, 6.85, 2.65, 0.85, "이종 피처 결합 (Concatenation)",
           ["[Group A(6) ∥ Group B(9) ∥ Group C(8)]", "총 23개 멀티모달 피처 벡터"],
           '#ffffff', c_purple_bd, c_purple_txt, title_size=9.6, body_size=8.2)

# Feature Badges
f_badges = [
    ("Group A: 3D 동역학 피처 (6종)", c_orange_txt, c_orange_box, c_orange_bd),
    ("Group B: 임상/인구학 피처 (9종)", c_teal_txt, c_teal_box, c_teal_bd),
    ("Group C: SSL 신호 표상 (8종)", c_blue_txt, c_blue_box, c_blue_bd),
]
for idx, (b_title, b_txt, b_bg, b_bd) in enumerate(f_badges):
    by = 5.75 - idx * 0.58
    b_patch = FancyBboxPatch((7.50, by - 0.20), 2.60, 0.40, boxstyle="round,pad=0.02,rounding_size=0.08",
                            facecolor=b_bg, edgecolor=b_bd, linewidth=1.1, zorder=3)
    ax.add_patch(b_patch)
    ax.text(8.80, by, b_title, ha='center', va='center', fontsize=9.0, fontweight='bold',
            color=b_txt, zorder=4)

draw_arrow(8.80, 6.42, 8.80, 6.00, color=c_purple_bd)

# Patient-Stratified GroupKFold Box
draw_block(8.80, 2.95, 2.65, 1.55, "엄격한 환자 단위 교차검증",
           ["• StratifiedGroupKFold (5-Fold)",
            "• 10회 반복 교차검증 (총 50회)",
            "• Train Fold 독립 StandardScaler",
            "• 환자간 데이터 누출 원천 차단"],
           '#ffffff', c_purple_bd, c_purple_txt, title_size=9.8, body_size=8.2)
draw_arrow(8.80, 4.30, 8.80, 3.73, color=c_purple_bd)

# Golden Window Validation Box
draw_block(8.80, 1.25, 2.65, 0.95, "초기 30초 검증 완료",
           ["골든 윈도우(0–30s) 검증 완료",
            "전체 구간 대비 동등 이상 민감도",
            "▶ F1 0.7192, 100% 승률 달성"],
           c_purple_box, c_purple_bd, c_purple_txt, title_size=9.8, body_size=8.2)
draw_arrow(8.80, 2.17, 8.80, 1.73, color=c_purple_bd)


# ==============================================================================
# Column 3 (Right): Multi-Model Benchmark & CDSS Output (x: 10.8 ~ 16.0)
# ==============================================================================
draw_card(10.8, 4.85, 5.2, 3.40, c_purple_bg, c_purple_bd,
          "다중 예측 모델 벤치마크 평가", "Multi-Model Benchmark")

# Connect Fusion to Benchmark
draw_arrow(10.40, 4.80, 10.80, 6.45, color=c_purple_bd, lw=1.8)

# Model Benchmark Cards
benchmark_models = [
    ("로지스틱 회귀 (LR) [최적 복합 모델]", "ROC-AUC 0.921, PR-AUC 0.9108, 특이도 80.9%", '#ffffff', '#7c3aed', '#6d28d9', True),
    ("시계열 딥러닝 (Bi-LSTM / GRU)", "양방향 장단기 메모리 기반 시계열 전파 학습", '#ffffff', '#a855f7', '#7e22ce', False),
    ("앙상블 기법 (Random Forest / XGBoost)", "비선형 결정 트리 기반 피처 중요도 분석", '#ffffff', '#a855f7', '#7e22ce', False)
]
for k, (m_title, m_desc, m_bg, m_bd, m_txt, is_best) in enumerate(benchmark_models):
    my = 7.35 - k * 0.78
    mw = 4.60
    m_patch = FancyBboxPatch((13.40 - mw/2, my - 0.28), mw, 0.58, boxstyle="round,pad=0.03,rounding_size=0.1",
                            facecolor=m_bg, edgecolor=m_bd, linewidth=1.8 if is_best else 1.1, zorder=3)
    ax.add_patch(m_patch)
    ax.text(13.40, my + 0.10, m_title, ha='center', va='center', fontsize=9.8,
            fontweight='bold', color=m_txt, zorder=4)
    ax.text(13.40, my - 0.12, m_desc, ha='center', va='center', fontsize=8.4,
            color=c_dark if not is_best else '#b91c1c', fontweight='bold' if is_best else 'normal', zorder=4)

# ------------------------------------------------------------------------------
# Stage 5 (Bottom-Right): Clinical Decision Support System (CDSS)
# ------------------------------------------------------------------------------
draw_card(10.8, 0.60, 5.2, 4.05, '#f8fafc', '#475569',
          "임상 의사결정 지원 시스템 (CDSS) 출력", "치료 가이드라인")

# Connect Models to CDSS
draw_arrow(13.40, 4.85, 13.40, 4.35, color=c_slate, lw=1.8)

# Optimal Cutoff Pill
cutoff_pill = FancyBboxPatch((11.10, 3.52), 4.60, 0.60, boxstyle="round,pad=0.04,rounding_size=0.12",
                             facecolor='#fef08a', edgecolor='#ca8a04', linewidth=1.5, zorder=4)
ax.add_patch(cutoff_pill)
ax.text(13.40, 3.73, "최적 예후 판정 기준선: 수술 성공 확률 P ≥ 0.61 (61점 이상)",
        ha='center', va='center', fontsize=9.8, fontweight='bold', color='#854d0e', zorder=5)
ax.text(13.40, 3.53, "(단일 속도 9.24 mm/s 특이도 29.4% 한계 ▶ 23개 복합 모델 특이도 80.9% 극복)",
        ha='center', va='center', fontsize=8.2, color='#713f12', zorder=5)

# Dual Outcome Action Cards
# Success Card
succ_patch = FancyBboxPatch((11.10, 1.05), 2.22, 2.15, boxstyle="round,pad=0.04,rounding_size=0.12",
                           facecolor=c_green_bg, edgecolor=c_green_bd, linewidth=1.5, zorder=4)
ax.add_patch(succ_patch)
ax.text(12.21, 2.95, "수술 성공군 (P ≥ 0.61)", ha='center', va='center',
        fontsize=10.0, fontweight='bold', color=c_green_txt, zorder=5)
ax.text(12.21, 2.50, "• 민감도: 88.1%\n• 특이도: 80.9%\n• ROC-AUC: 0.921",
        ha='center', va='center', fontsize=8.6, color=c_dark, zorder=5, linespacing=1.2)
ax.text(12.21, 1.50, "[치료 권고안]\n개두 절제술 적극 권고\n(SOZ 완전 절제 목표)",
        ha='center', va='center', fontsize=8.8, fontweight='bold', color=c_green_txt, zorder=5, linespacing=1.2)

# Failure Card
fail_patch = FancyBboxPatch((13.48, 1.05), 2.22, 2.15, boxstyle="round,pad=0.04,rounding_size=0.12",
                           facecolor=c_rose_bg, edgecolor=c_rose_bd, linewidth=1.5, zorder=4)
ax.add_patch(fail_patch)
ax.text(14.59, 2.95, "수술 실패 위험군 (P < 0.61)", ha='center', va='center',
        fontsize=10.0, fontweight='bold', color=c_rose_txt, zorder=5)
ax.text(14.59, 2.50, "• 급속 전파 위험군\n• 속도 > 9.24 mm/s\n• 실패 위험 3.82배 급증",
        ha='center', va='center', fontsize=8.6, color=c_dark, zorder=5, linespacing=1.2)
ax.text(14.59, 1.50, "[대안 치료 권고안]\n과도 절제 지양 및\nRNS / DBS / LITT 권고",
        ha='center', va='center', fontsize=8.8, fontweight='bold', color=c_rose_txt, zorder=5, linespacing=1.2)

# Connect Cutoff to Outcome Cards
draw_arrow(12.21, 3.52, 12.21, 3.20, color=c_green_bd, lw=1.5)
draw_arrow(14.59, 3.52, 14.59, 3.20, color=c_rose_bd, lw=1.5)

plt.tight_layout()

# Save Files
png_out = 'model_architecture_detailed.png'
svg_out = 'model_architecture_detailed.svg'
plt.savefig(png_out, dpi=300, bbox_inches='tight', facecolor='white', transparent=False)
plt.savefig(svg_out, format='svg', bbox_inches='tight')
plt.close(fig)

print(f"[완료] 오버랩이 완벽히 해결된 상세 모델 아키텍처 다이어그램이 생성되었습니다:")
print(f"  - PNG: {png_out}")
print(f"  - SVG: {svg_out}")
