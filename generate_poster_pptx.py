#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A0 대형 학술 논문 포스터 PPTX 자동 생성 스크립트 (연구 결과 논리적 완결판)
규격: ISO A0 Portrait (841 mm x 1189 mm)
디자인:
  - 연구 결과의 설명 텍스트와 그림이 1:1로 완벽히 매칭되는 논리적 순서:
    1) SSL 복합 모델 성과 서술 -> [그림 3: SSL ROC & 민감도/특이도 피규어]
    2) [표 1] 머신러닝 평가지표 비교표
    3) 초기 30초 조기 진단 유효성 서술 -> [그림 4: 윈도우별 벤치마크 & 시계열 피규어]
    4) 환자별 맞춤 치료 추천 체계 (환자 A 절제술 vs 환자 B 대안치료 카드)
"""

import os
from pptx import Presentation
from pptx.util import Mm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_poster():
    prs = Presentation()
    
    prs.slide_width = Mm(841)
    prs.slide_height = Mm(1189)
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)
    
    # 세련된 컬러 팔레트
    C_NAVY = RGBColor(27, 54, 93)           # #1B365D - 메인 학술 네이비
    C_NAVY_LIGHT = RGBColor(234, 240, 248)  # #EAF0F8 - 연한 블루 하이라이트
    C_WHITE = RGBColor(255, 255, 255)       # #FFFFFF
    C_CARD_BG = RGBColor(255, 255, 255)     # 카드 배경
    C_CARD_BORDER = RGBColor(203, 213, 225) # #CBD5E1 - 카드 테두리
    C_TEXT_MAIN = RGBColor(30, 41, 59)       # #1E293B - 본문 텍스트
    C_TEXT_MUTED = RGBColor(71, 85, 105)    # #475569 - 캡션
    C_EMERALD = RGBColor(5, 150, 105)       # #059669 - 성공/성능 향상 초록
    C_EMERALD_BG = RGBColor(236, 253, 245)  # #ECFDF5 - 연한 초록 배경
    C_CRIMSON = RGBColor(220, 38, 38)       # #DC2626 - 위험/실패군 빨강
    C_CRIMSON_BG = RGBColor(254, 242, 242)  # #FEF2F2 - 연한 빨강 배경
    C_TABLE_HEADER = RGBColor(30, 58, 138)  # #1E3A8A - 테이블 헤더
    C_ROW_ALT = RGBColor(248, 250, 252)      # #F8FAFC - 테이블 교차 행
    
    FONT_NAME = "Malgun Gothic"

    # 슬라이드 전체 배경
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Mm(841), Mm(1189))
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(245, 247, 250)
    bg.line.fill.background()

    # =========================================================================
    # [상단 헤더 영역] Top = 16mm, Height = 102mm, Width = 791mm
    # =========================================================================
    header_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(25), Mm(16), Mm(791), Mm(102))
    header_box.fill.solid()
    header_box.fill.fore_color.rgb = C_WHITE
    header_box.line.color.rgb = C_CARD_BORDER
    header_box.line.width = Pt(2)

    # 헤더 좌측 USW 로고 엠블럼
    logo_badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(38), Mm(26), Mm(62), Mm(82))
    logo_badge.fill.solid()
    logo_badge.fill.fore_color.rgb = C_NAVY
    logo_badge.line.fill.background()
    tf_lb = logo_badge.text_frame
    tf_lb.word_wrap = True
    tf_lb.vertical_anchor = MSO_ANCHOR.MIDDLE
    p_lb1 = tf_lb.paragraphs[0]
    p_lb1.text = "USW"
    p_lb1.font.name = "Arial"
    p_lb1.font.size = Pt(22)
    p_lb1.font.bold = True
    p_lb1.font.color.rgb = C_WHITE
    p_lb1.alignment = PP_ALIGN.CENTER
    p_lb2 = tf_lb.add_paragraph()
    p_lb2.text = "수원대학교\n데이터과학부"
    p_lb2.font.name = FONT_NAME
    p_lb2.font.size = Pt(11)
    p_lb2.font.color.rgb = RGBColor(224, 231, 255)
    p_lb2.alignment = PP_ALIGN.CENTER
    p_lb2.space_before = Pt(4)

    # 헤더 텍스트 박스
    tb_h = slide.shapes.add_textbox(Mm(110), Mm(20), Mm(690), Mm(94))
    tf_header = tb_h.text_frame
    tf_header.word_wrap = True
    tf_header.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_header.margin_left = tf_header.margin_right = tf_header.margin_top = tf_header.margin_bottom = 0

    p_title = tf_header.paragraphs[0]
    p_title.text = "3차원 iEEG 뇌파 궤적 동역학 및 자가지도학습(SSL) 신호 표상 기반\n초기 30초 뇌전증 수술 예후 조기 예측과 맞춤형 치료 추천 AI 모델"
    p_title.font.name = FONT_NAME
    p_title.font.size = Pt(41)
    p_title.font.bold = True
    p_title.font.color.rgb = C_NAVY
    p_title.alignment = PP_ALIGN.CENTER
    p_title.line_spacing = 1.15

    p_author = tf_header.add_paragraph()
    p_author.text = "이슬빈"
    p_author.font.name = FONT_NAME
    p_author.font.size = Pt(27)
    p_author.font.bold = True
    p_author.font.color.rgb = RGBColor(51, 65, 85)
    p_author.alignment = PP_ALIGN.CENTER
    p_author.space_before = Pt(6)

    p_affil = tf_header.add_paragraph()
    p_affil.text = "수원대학교 공과대학 데이터과학부 (Division of Data Science, The University of Suwon)"
    p_affil.font.name = FONT_NAME
    p_affil.font.size = Pt(20)
    p_affil.font.color.rgb = RGBColor(100, 116, 139)
    p_affil.alignment = PP_ALIGN.CENTER
    p_affil.space_before = Pt(3)

    def create_section_card(left_mm, top_mm, width_mm, height_mm, title_text):
        card = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Mm(left_mm), Mm(top_mm), Mm(width_mm), Mm(height_mm)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD_BG
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1.5)

        header_bar_height = 26
        header_bar = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            Mm(left_mm), Mm(top_mm), Mm(width_mm), Mm(header_bar_height)
        )
        header_bar.fill.solid()
        header_bar.fill.fore_color.rgb = C_NAVY
        header_bar.line.fill.background()
        
        tf = header_bar.text_frame
        tf.word_wrap = False
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Mm(12)
        p = tf.paragraphs[0]
        p.text = " ".join(list(title_text))
        p.font.name = FONT_NAME
        p.font.size = Pt(26)
        p.font.bold = True
        p.font.color.rgb = C_WHITE
        p.alignment = PP_ALIGN.LEFT

        return card

    # =========================================================================
    # [좌측 열 (Column 1)] Left = 25mm, Width = 385mm
    # =========================================================================
    c1_left = 25
    c1_width = 385

    # 1. 초록 (Abstract)
    create_section_card(c1_left, 126, c1_width, 126, "초 록")
    tb_abs = slide.shapes.add_textbox(Mm(c1_left + 10), Mm(156), Mm(c1_width - 20), Mm(90))
    tf_abs = tb_abs.text_frame
    tf_abs.word_wrap = True
    tf_abs.margin_left = tf_abs.margin_right = tf_abs.margin_top = tf_abs.margin_bottom = 0
    
    p_abs = tf_abs.paragraphs[0]
    p_abs.text = (
        "본 연구는 약물 난치성 뇌전증(DRE) 환자의 발작 시작 구역(SOZ) 절제술 후 발생하는 "
        "30~40%의 재발 한계를 극복하기 위해, 발작 초기 30초 iEEG 전파 궤적 동역학과 "
        "외부 대규모 자가지도학습(SSL) 신호 표상을 융합한 조기 예후 예측 AI 모델을 제안한다. "
        "OpenNeuro 코호트(55명) 전극을 MNI 152 3차원 공간에 정합하여 질량 중심 궤적을 복원하고, "
        "독립된 외부 코호트(SWEC-ETHZ)로 사전학습된 1D-CNN 대조학습 표상을 결합하여 희소 전극 한계를 극복하였다. "
        "결과적으로 초기 30초 신호만으로 F1-score 0.7192의 민감도를 유지하였으며, "
        "23개 피처 멀티모달 모델을 통해 특이도 80.9%, ROC-AUC 0.921의 압도적인 분류 성능을 달성하였다."
    )
    p_abs.font.name = FONT_NAME
    p_abs.font.size = Pt(17.5)
    p_abs.font.color.rgb = C_TEXT_MAIN
    p_abs.line_spacing = 1.35

    # 2. 서론 (Introduction)
    create_section_card(c1_left, 262, c1_width, 280, "서 론")
    tb_intro = slide.shapes.add_textbox(Mm(c1_left + 10), Mm(292), Mm(c1_width - 20), Mm(80))
    tf_intro = tb_intro.text_frame
    tf_intro.word_wrap = True
    tf_intro.margin_left = tf_intro.margin_right = tf_intro.margin_top = tf_intro.margin_bottom = 0

    p_in1 = tf_intro.paragraphs[0]
    p_in1.text = "• 연구 배경 및 기존 단일 지표의 한계:"
    p_in1.font.name = FONT_NAME
    p_in1.font.size = Pt(19)
    p_in1.font.bold = True
    p_in1.font.color.rgb = C_NAVY

    p_in2 = tf_intro.add_paragraph()
    p_in2.text = (
        "  - 약물 난치성 뇌전증 환자의 절제술 후 30~40%는 재발 한계에 직면함.\n"
        "  - 심부 전극(sEEG)의 공간 희소성과 성공·실패군 간 속도 중첩(2~7 mm/s)으로 "
        "단일 전파 속도 지표는 특이도가 29.4%에 그치는 구조적 한계 노출."
    )
    p_in2.font.name = FONT_NAME
    p_in2.font.size = Pt(16.5)
    p_in2.font.color.rgb = C_TEXT_MAIN
    p_in2.line_spacing = 1.25

    p_in3 = tf_intro.add_paragraph()
    p_in3.text = "• 초기 30초 윈도우의 필요성 및 SSL 융합 제안:"
    p_in3.font.name = FONT_NAME
    p_in3.font.size = Pt(19)
    p_in3.font.bold = True
    p_in3.font.color.rgb = C_NAVY
    p_in3.space_before = Pt(4)

    p_in4 = tf_intro.add_paragraph()
    p_in4.text = (
        "  - 발작 30초 이후에는 대측 전파 및 이차성 전신화 잡음으로 원점 특성이 심각하게 마스킹됨.\n"
        "  - 발작 시작 30초 신호만으로 절제술 적합 여부를 조기 판별하고 대안 치료(RNS/LITT)를 "
        "즉각 가이드하는 3D 궤적+외부 SSL 신호 표상 융합 AI 프레임워크 구축."
    )
    p_in4.font.name = FONT_NAME
    p_in4.font.size = Pt(16.5)
    p_in4.font.color.rgb = C_TEXT_MAIN
    p_in4.line_spacing = 1.25

    img_mni_path = "MNI_3D.png"
    if os.path.exists(img_mni_path):
        slide.shapes.add_picture(
            img_mni_path,
            Mm(c1_left + 15), Mm(392), Mm(c1_width - 30), Mm(128)
        )
    
    tb_c1 = slide.shapes.add_textbox(Mm(c1_left + 10), Mm(522), Mm(c1_width - 20), Mm(16))
    tf_c1 = tb_c1.text_frame
    tf_c1.word_wrap = True
    tf_c1.margin_left = tf_c1.margin_right = tf_c1.margin_top = tf_c1.margin_bottom = 0
    p_c1 = tf_c1.paragraphs[0]
    p_c1.text = "[그림 1] MNI 152 3차원 표준 뇌 좌표계 상의 전극 매핑 및 발작 전파 질량 중심 궤적 복원"
    p_c1.font.name = FONT_NAME
    p_c1.font.size = Pt(14.5)
    p_c1.font.bold = True
    p_c1.font.color.rgb = C_TEXT_MUTED
    p_c1.alignment = PP_ALIGN.CENTER

    # 3. 연구 방법 (Methods)
    create_section_card(c1_left, 552, c1_width, 580, "연 구 방 법")
    tb_m = slide.shapes.add_textbox(Mm(c1_left + 10), Mm(582), Mm(c1_width - 20), Mm(90))
    tf_m = tb_m.text_frame
    tf_m.word_wrap = True
    tf_m.margin_left = tf_m.margin_right = tf_m.margin_top = tf_m.margin_bottom = 0

    p_m1 = tf_m.paragraphs[0]
    p_m1.text = "• 코호트 데이터 및 23차원 멀티모달 피처 세트:"
    p_m1.font.name = FONT_NAME
    p_m1.font.size = Pt(18)
    p_m1.font.bold = True
    p_m1.font.color.rgb = C_NAVY

    p_m2 = tf_m.add_paragraph()
    p_m2.text = (
        "  - 분석 코호트: OpenNeuro ds004100 (환자 55명, 203개 발작 iEEG, MNI 152 정합)\n"
        "  - 외부 사전학습: SWEC-ETHZ (16명 환자, 100개 발작 세그먼트, 75만 개 윈도우)\n"
        "  - 3D 궤적 동역학 (6종): 평균/최대 속도(v_mean, v_max), 체류비율(R_res), 분산도(D_disp)\n"
        "  - 외부 SSL 신호 표상 (8종): 1D-CNN 인코더 128차원 잠재 표현 → PCA(k=8) 축소\n"
        "  - 임상 메타데이터 (9종): 발작 시작 연령, 전극 삽입 수, 수술 절제 영역 부피 등"
    )
    p_m2.font.name = FONT_NAME
    p_m2.font.size = Pt(15.5)
    p_m2.font.color.rgb = C_TEXT_MAIN
    p_m2.line_spacing = 1.25

    table_shape = slide.shapes.add_table(3, 2, Mm(c1_left + 10), Mm(680), Mm(c1_width - 20), Mm(38))
    tbl = table_shape.table
    tbl.columns[0].width = Mm(90)
    tbl.columns[1].width = Mm(c1_width - 20 - 90)

    tbl_data = [
        ("초기 30초 (Early, 0~30s)", "국소 억제 장벽 유지 및 조기 발작 원점 집중 구간 (골든 윈도우)"),
        ("후기 30초 (Late, 30~60s)", "억제 장벽 파탄 및 주변 뇌 조직·대측 반구 광범위 확산 구간"),
        ("전체 구간 (Full Seizure)", "발작 개시부터 임상적 종료 시점까지의 전체 기록 구간")
    ]
    for row_idx, (col1, col2) in enumerate(tbl_data):
        cell1 = tbl.cell(row_idx, 0)
        cell1.text = col1
        cell1.fill.solid()
        cell1.fill.fore_color.rgb = C_NAVY_LIGHT if row_idx == 0 else C_ROW_ALT
        for p in cell1.text_frame.paragraphs:
            p.font.name = FONT_NAME
            p.font.size = Pt(14.5)
            p.font.bold = True
            p.font.color.rgb = C_NAVY if row_idx == 0 else C_TEXT_MAIN
            p.alignment = PP_ALIGN.CENTER

        cell2 = tbl.cell(row_idx, 1)
        cell2.text = col2
        cell2.fill.solid()
        cell2.fill.fore_color.rgb = C_NAVY_LIGHT if row_idx == 0 else C_WHITE
        for p in cell2.text_frame.paragraphs:
            p.font.name = FONT_NAME
            p.font.size = Pt(14)
            p.font.color.rgb = C_TEXT_MAIN

    tb_opt = slide.shapes.add_textbox(Mm(c1_left + 10), Mm(724), Mm(c1_width - 20), Mm(28))
    tf_opt = tb_opt.text_frame
    tf_opt.word_wrap = True
    tf_opt.margin_left = tf_opt.margin_right = tf_opt.margin_top = tf_opt.margin_bottom = 0
    p_opt1 = tf_opt.paragraphs[0]
    p_opt1.text = "• 최적화 및 환자 단위 교차검증 (데이터 누출 완벽 차단):"
    p_opt1.font.name = FONT_NAME
    p_opt1.font.size = Pt(18)
    p_opt1.font.bold = True
    p_opt1.font.color.rgb = C_NAVY

    p_opt2 = tf_opt.add_paragraph()
    p_opt2.text = (
        "  - Adam Optimizer (LR 0.001, Batch 1024, SimCLR NT-Xent 대조 손실함수, 생체 신호 5대 증강)\n"
        "  - 환자 식별자(participant_id) 기준 10회 반복 환자 단위 5-Fold 계층화 교차검증 (총 50회)"
    )
    p_opt2.font.name = FONT_NAME
    p_opt2.font.size = Pt(15.5)
    p_opt2.font.color.rgb = C_TEXT_MAIN
    p_opt2.line_spacing = 1.2

    img_arch_path = "model_architecture.png"
    if os.path.exists(img_arch_path):
        slide.shapes.add_picture(
            img_arch_path,
            Mm(c1_left + 15), Mm(758), Mm(c1_width - 30), Mm(196)
        )

    tb_arch_desc = slide.shapes.add_textbox(Mm(c1_left + 10), Mm(960), Mm(c1_width - 20), Mm(165))
    tf_arch_desc = tb_arch_desc.text_frame
    tf_arch_desc.word_wrap = True
    tf_arch_desc.margin_left = tf_arch_desc.margin_right = tf_arch_desc.margin_top = tf_arch_desc.margin_bottom = 0

    p_a0 = tf_arch_desc.paragraphs[0]
    p_a0.text = "[그림 2] 다각적 피처 추출·자가지도학습(SSL) 결합 및 수술 예후 예측 모델 파이프라인"
    p_a0.font.name = FONT_NAME
    p_a0.font.size = Pt(15.5)
    p_a0.font.bold = True
    p_a0.font.color.rgb = C_NAVY
    p_a0.alignment = PP_ALIGN.CENTER

    layers_info = [
        ("① 데이터 입력 및 증강", "OpenNeuro ds004100 55명 코호트 기반 3D 전파 궤적 및 슬라이딩 윈도우 증강"),
        ("② 다각적 피처 추출·병합", "Group A(3D 궤적 동역학 6종) + Group B(임상/인구학 9종) + 외부 SSL 표상(8종) 결합"),
        ("③ 통합 피처 세트 구축", "다차원 이종 생체 신호(총 23개 피처) 표준화 정규화 및 상호보완적 멀티모달 융합"),
        ("④ 다중 예측 모델 벤치마크", "로지스틱 회귀, 시계열 딥러닝(Bi-LSTM/GRU), 트리 기반 앙상블 기법 비교 평가"),
        ("⑤ 최종 가이드라인 제시", "수술 성공 확률(P ≥ 0.61) 기준 최적 예후 판정 및 절제술 vs 신경자극술(RNS/LITT) 추천")
    ]
    for l_title, l_desc in layers_info:
        p_l = tf_arch_desc.add_paragraph()
        p_l.text = f"{l_title}: {l_desc}"
        p_l.font.name = FONT_NAME
        p_l.font.size = Pt(14.5)
        p_l.font.color.rgb = C_TEXT_MAIN
        p_l.space_before = Pt(3)

    # =========================================================================
    # [우측 열 (Column 2)] Left = 431mm, Width = 385mm
    # ⭐ [개선 핵심]: 설명 텍스트와 그림이 1:1로 완벽히 매칭되는 논리적 순서!
    # =========================================================================
    c2_left = 431
    c2_width = 385

    create_section_card(c2_left, 126, c2_width, 712, "연 구 결 과")

    # -------------------------------------------------------------------------
    # [파트 1: SSL 복합 모델 성과 서술 (핵심 성과)] Top = 156mm ~ 194mm
    # -------------------------------------------------------------------------
    tb_r1 = slide.shapes.add_textbox(Mm(c2_left + 10), Mm(156), Mm(c2_width - 20), Mm(38))
    tf_r1 = tb_r1.text_frame
    tf_r1.word_wrap = True
    tf_r1.margin_left = tf_r1.margin_right = tf_r1.margin_top = tf_r1.margin_bottom = 0

    p_r1_t = tf_r1.paragraphs[0]
    p_r1_t.text = "1. 외부 SSL 표상 결합 23개 피처 모델 성능 혁신 (본 연구의 핵심):"
    p_r1_t.font.name = FONT_NAME
    p_r1_t.font.size = Pt(17.5)
    p_r1_t.font.bold = True
    p_r1_t.font.color.rgb = C_NAVY

    p_r1_b = tf_r1.add_paragraph()
    p_r1_b.text = (
        "  - [속도 중첩 극복]: 기존 단일 속도는 2~7 mm/s 중첩으로 특이도가 29.4%(AUC 0.595)에 불과.\n"
        "  - [23개 피처 멀티모달 융합]: 외부 코호트(SWEC-ETHZ) 사전학습 1D-CNN 표상(8종) 결합 모델은 "
        "최적 임계값(P ≥ 0.61)에서 특이도 80.9%(2.75배↑), ROC-AUC 0.921의 압도적 판별력 달성!"
    )
    p_r1_b.font.name = FONT_NAME
    p_r1_b.font.size = Pt(14.5)
    p_r1_b.font.color.rgb = C_TEXT_MAIN
    p_r1_b.line_spacing = 1.25

    # [그림 3: 그림 5 전면 배치!] Top = 196mm ~ 306mm
    img_ssl_path = "upgraded_ssl_composite_threshold_analysis.png"
    if os.path.exists(img_ssl_path):
        slide.shapes.add_picture(
            img_ssl_path,
            Mm(c2_left + 15), Mm(196), Mm(c2_width - 30), Mm(110)
        )

    tb_c_ssl = slide.shapes.add_textbox(Mm(c2_left + 10), Mm(308), Mm(c2_width - 20), Mm(14))
    tf_c_ssl = tb_c_ssl.text_frame
    tf_c_ssl.word_wrap = True
    tf_c_ssl.margin_left = tf_c_ssl.margin_right = tf_c_ssl.margin_top = tf_c_ssl.margin_bottom = 0
    p_css = tf_c_ssl.paragraphs[0]
    p_css.text = "[그림 3] 23개 SSL 피처 결합 모델의 ROC 곡선(AUC 0.921) 및 임계값(P=0.61) 민감도·특이도 분석"
    p_css.font.name = FONT_NAME
    p_css.font.size = Pt(13.5)
    p_css.font.bold = True
    p_css.font.color.rgb = C_NAVY
    p_css.alignment = PP_ALIGN.CENTER

    # -------------------------------------------------------------------------
    # [파트 2: 표 1 머신러닝 평가지표 비교표] Top = 324mm ~ 386mm
    # -------------------------------------------------------------------------
    tb_tbl_title = slide.shapes.add_textbox(Mm(c2_left + 10), Mm(324), Mm(c2_width - 20), Mm(12))
    tf_tbl_title = tb_tbl_title.text_frame
    tf_tbl_title.margin_left = tf_tbl_title.margin_right = tf_tbl_title.margin_top = tf_tbl_title.margin_bottom = 0
    p_tt = tf_tbl_title.paragraphs[0]
    p_tt.text = "[표 1] 단일 3D 전파 속도 모델과 SSL 멀티모달 복합 모델의 머신러닝 평가지표 비교표"
    p_tt.font.name = FONT_NAME
    p_tt.font.size = Pt(15.5)
    p_tt.font.bold = True
    p_tt.font.color.rgb = C_NAVY

    t1_shape = slide.shapes.add_table(5, 4, Mm(c2_left + 10), Mm(338), Mm(c2_width - 20), Mm(48))
    t1 = t1_shape.table
    t1.columns[0].width = Mm(85)
    t1.columns[1].width = Mm(85)
    t1.columns[2].width = Mm(85)
    t1.columns[3].width = Mm(c2_width - 20 - 255)

    headers = ["평가지표", "단일 속도 (레코드)", "단일 속도 (환자)", "SSL 멀티모달 복합 모델"]
    for c_idx, h in enumerate(headers):
        cell = t1.cell(0, c_idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_TABLE_HEADER
        for p in cell.text_frame.paragraphs:
            p.font.name = FONT_NAME
            p.font.size = Pt(13.5)
            p.font.bold = True
            p.font.color.rgb = C_WHITE
            p.alignment = PP_ALIGN.CENTER

    table1_rows = [
        ("정확도/판별력 (ROC-AUC)", "0.5950", "0.6280", "0.9210 (+0.326)"),
        ("정밀도-재현율 (PR-AUC)", "0.7299", "0.7512", "0.9108"),
        ("민감도 (Sensitivity)", "87.4%", "94.4%", "88.1%"),
        ("특이도 (Specificity)", "29.4%", "36.8%", "80.9% (+51.5%p)"),
    ]
    for r_idx, r_data in enumerate(table1_rows, start=1):
        for c_idx, val in enumerate(r_data):
            cell = t1.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            if c_idx == 3:
                cell.fill.fore_color.rgb = C_NAVY_LIGHT
            elif r_idx % 2 == 1:
                cell.fill.fore_color.rgb = C_ROW_ALT
            else:
                cell.fill.fore_color.rgb = C_WHITE

            for p in cell.text_frame.paragraphs:
                p.font.name = FONT_NAME
                p.font.size = Pt(13)
                if c_idx == 3 or c_idx == 0:
                    p.font.bold = True
                p.font.color.rgb = C_NAVY if c_idx == 3 else C_TEXT_MAIN
                p.alignment = PP_ALIGN.CENTER

    # -------------------------------------------------------------------------
    # [파트 3: 초기 30초 윈도우 조기 진단 유효성 서술] Top = 390mm ~ 428mm
    # -------------------------------------------------------------------------
    tb_r2 = slide.shapes.add_textbox(Mm(c2_left + 10), Mm(390), Mm(c2_width - 20), Mm(38))
    tf_r2 = tb_r2.text_frame
    tf_r2.word_wrap = True
    tf_r2.margin_left = tf_r2.margin_right = tf_r2.margin_top = tf_r2.margin_bottom = 0

    p_r2_t = tf_r2.paragraphs[0]
    p_r2_t.text = "2. 발작 초기 30초 윈도우 조기 진단 유효성 실증 (골든 윈도우 입증):"
    p_r2_t.font.name = FONT_NAME
    p_r2_t.font.size = Pt(17.5)
    p_r2_t.font.bold = True
    p_r2_t.font.color.rgb = C_NAVY

    p_r2_b = tf_r2.add_paragraph()
    p_r2_b.text = (
        "  - [30초 골든 윈도우]: '조기 원점 집중 효과'로 전체 발작을 보지 않고 단 30초만으로 F1 0.7192, AUC 0.6080 유지.\n"
        "  - [후기 30~60초 붕괴]: 이차성 전신화 잡음 개입으로 후기 구간은 F1 0.6525, AUC 0.5180으로 성능이 급격히 무력화됨.\n"
        "  - [10회 반복 교차검증]: 16명 외부 SSL 결합 모델은 베이스라인 대비 100% 승률(10/10회, ΔAUC +0.035)로 우월성 입증."
    )
    p_r2_b.font.name = FONT_NAME
    p_r2_b.font.size = Pt(14.5)
    p_r2_b.font.color.rgb = C_TEXT_MAIN
    p_r2_b.line_spacing = 1.25

    # [그림 4: figure4_early30s... 삽입] Top = 430mm ~ 534mm
    img_early_path = "figure4_early30s_validation.png"
    if os.path.exists(img_early_path):
        slide.shapes.add_picture(
            img_early_path,
            Mm(c2_left + 15), Mm(430), Mm(c2_width - 30), Mm(104)
        )

    tb_c_early = slide.shapes.add_textbox(Mm(c2_left + 10), Mm(536), Mm(c2_width - 20), Mm(14))
    tf_c_early = tb_c_early.text_frame
    tf_c_early.word_wrap = True
    tf_c_early.margin_left = tf_c_early.margin_right = tf_c_early.margin_top = tf_c_early.margin_bottom = 0
    p_ce = tf_c_early.paragraphs[0]
    p_ce.text = "[그림 4] 시간 구간별(초기 30초 vs 후기 vs 전체) 진단 성능(F1/AUC) 유지 및 시계열 프로파일"
    p_ce.font.name = FONT_NAME
    p_ce.font.size = Pt(13.5)
    p_ce.font.bold = True
    p_ce.font.color.rgb = C_TEXT_MUTED
    p_ce.alignment = PP_ALIGN.CENTER

    # -------------------------------------------------------------------------
    # [파트 4: 환자별 맞춤 치료 추천 체계 카드 2종 및 CDSS 결론] Top = 554mm ~ 712mm
    # -------------------------------------------------------------------------
    tb_rec_title = slide.shapes.add_textbox(Mm(c2_left + 10), Mm(554), Mm(c2_width - 20), Mm(12))
    tf_rec_title = tb_rec_title.text_frame
    tf_rec_title.margin_left = tf_rec_title.margin_right = tf_rec_title.margin_top = tf_rec_title.margin_bottom = 0
    p_rt = tf_rec_title.paragraphs[0]
    p_rt.text = "3. 환자별 맞춤형 치료 조기 추천 체계 (임상 CDSS 의사결정 지원):"
    p_rt.font.name = FONT_NAME
    p_rt.font.size = Pt(17.5)
    p_rt.font.bold = True
    p_rt.font.color.rgb = C_NAVY

    card_w = (c2_width - 20 - 8) / 2 # 약 178mm

    # 환자 A 카드
    box_ptA = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(c2_left + 10), Mm(568), Mm(card_w), Mm(56))
    box_ptA.fill.solid()
    box_ptA.fill.fore_color.rgb = C_EMERALD_BG
    box_ptA.line.color.rgb = C_EMERALD
    box_ptA.line.width = Pt(1.5)
    tf_pa = box_ptA.text_frame
    tf_pa.word_wrap = True
    tf_pa.margin_left = tf_pa.margin_right = tf_pa.margin_top = tf_pa.margin_bottom = Mm(3)

    p_pa1 = tf_pa.paragraphs[0]
    p_pa1.text = "🟢 환자 A (개두 절제술 권고 증례)"
    p_pa1.font.name = FONT_NAME
    p_pa1.font.size = Pt(14)
    p_pa1.font.bold = True
    p_pa1.font.color.rgb = C_EMERALD

    p_pa2 = tf_pa.add_paragraph()
    p_pa2.text = (
        "• 30초 전파 속도: 0.55 mm/s (병소 국소 정체)\n"
        "• 모델 성공 예측: 89.4% (P ≥ 0.61 충족)\n"
        "• 임상 결론: 개두 절제술 시행 → 완전 발작 소실 (Engel I)"
    )
    p_pa2.font.name = FONT_NAME
    p_pa2.font.size = Pt(11.5)
    p_pa2.font.color.rgb = C_TEXT_MAIN
    p_pa2.space_before = Pt(2)

    # 환자 B 카드
    box_ptB = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Mm(c2_left + 10 + card_w + 8), Mm(568), Mm(card_w), Mm(56))
    box_ptB.fill.solid()
    box_ptB.fill.fore_color.rgb = C_CRIMSON_BG
    box_ptB.line.color.rgb = C_CRIMSON
    box_ptB.line.width = Pt(1.5)
    tf_pb = box_ptB.text_frame
    tf_pb.word_wrap = True
    tf_pb.margin_left = tf_pb.margin_right = tf_pb.margin_top = tf_pb.margin_bottom = Mm(3)

    p_pb1 = tf_pb.paragraphs[0]
    p_pb1.text = "🔴 환자 B (RNS / LITT 대안 치료 증례)"
    p_pb1.font.name = FONT_NAME
    p_pb1.font.size = Pt(14)
    p_pb1.font.bold = True
    p_pb1.font.color.rgb = C_CRIMSON

    p_pb2 = tf_pb.add_paragraph()
    p_pb2.text = (
        "• 30초 전파 속도: 20.29 mm/s (급속 원격 확산)\n"
        "• 수술 실패 위험: 84.1% (수술 시 재발 고위험)\n"
        "• 임상 결론: 절제 배제 → 반응성 신경자극술(RNS)/소작술(LITT)"
    )
    p_pb2.font.name = FONT_NAME
    p_pb2.font.size = Pt(11.5)
    p_pb2.font.color.rgb = C_TEXT_MAIN
    p_pb2.space_before = Pt(2)

    # CDSS 요약 텍스트
    tb_cdss = slide.shapes.add_textbox(Mm(c2_left + 10), Mm(628), Mm(c2_width - 20), Mm(80))
    tf_cdss = tb_cdss.text_frame
    tf_cdss.word_wrap = True
    tf_cdss.margin_left = tf_cdss.margin_right = tf_cdss.margin_top = tf_cdss.margin_bottom = 0

    p_cd1 = tf_cdss.paragraphs[0]
    p_cd1.text = (
        "  - [임상적 가치]: 발작 시작 단 30초 신호만으로 개두 절제술 적합군(환자 A)과 비절제 신경자극술 대안 치료군(환자 B)을 "
        "80.9%의 높은 특이도로 즉시 정량 판별하여, 불필요한 과도 절제를 막고 환자 맞춤형 치료 전략을 신속히 결정함.\n"
        "  - [10회 반복 계층화 교차검증]: 16명 외부 코호트 SSL 표상 결합 모델은 10/10회 전체(100% 승률, ΔAUC +0.035)에서 "
        "일관된 일반화 성능 향상을 입증하여 임상 의사결정 지원 시스템(CDSS)으로서의 신뢰성을 확보함."
    )
    p_cd1.font.name = FONT_NAME
    p_cd1.font.size = Pt(13.5)
    p_cd1.font.color.rgb = C_TEXT_MAIN
    p_cd1.line_spacing = 1.3

    # 5. 결론 (Conclusion)
    create_section_card(c2_left, 842, c2_width, 144, "결 론")
    tb_con = slide.shapes.add_textbox(Mm(c2_left + 10), Mm(872), Mm(c2_width - 20), Mm(108))
    tf_con = tb_con.text_frame
    tf_con.word_wrap = True
    tf_con.margin_left = tf_con.margin_right = tf_con.margin_top = tf_con.margin_bottom = 0

    p_con = tf_con.paragraphs[0]
    p_con.text = (
        "본 연구에서 구축한 3차원 전파 동역학 및 자가지도학습(SSL) 융합 모델은 발작 시작 불과 30초 "
        "신호만으로 뇌전증 수술 예후를 고정밀도로 조기 예측할 수 있음을 입증하였다.\n\n"
        "도출된 9.24 mm/s 속도 임계값과 23개 피처 복합 모델(AUC 0.921, 특이도 80.9%)은 신경외과 및 신경과 "
        "임상의에게 개두 절제술, 신경자극술(RNS/DBS), 레이저 소작술(LITT) 중 최적의 치료법을 정량적으로 "
        "조기 제시하는 신뢰도 높은 임상 의사결정 지원 시스템(CDSS)으로 즉시 활용될 수 있다.\n\n"
        "향후 발작 개시 30초 실시간 감시 CDSS 소프트웨어 개발과 함께, 9.24 mm/s 초고위험군 환자를 위한 "
        "반응성 신경자극술(RNS) 최적 표적 가상 시뮬레이션 및 다기관 전향적 임상 검증으로 확장할 계획이다."
    )
    p_con.font.name = FONT_NAME
    p_con.font.size = Pt(16)
    p_con.font.color.rgb = C_TEXT_MAIN
    p_con.line_spacing = 1.35

    # 6. 참고문헌 (References)
    create_section_card(c2_left, 992, c2_width, 140, "참 고 문 헌")
    tb_ref = slide.shapes.add_textbox(Mm(c2_left + 10), Mm(1022), Mm(c2_width - 20), Mm(105))
    tf_ref = tb_ref.text_frame
    tf_ref.word_wrap = True
    tf_ref.margin_left = tf_ref.margin_right = tf_ref.margin_top = tf_ref.margin_bottom = 0

    refs = [
        "[1] P. Kwan and M. J. Brodie, \"Early identification of refractory epilepsy,\" N. Engl. J. Med., vol. 342, no. 5, pp. 314-319, 2000.",
        "[2] S. Wiebe et al., \"A randomized, controlled trial of surgery for temporal-lobe epilepsy,\" N. Engl. J. Med., vol. 345, no. 5, pp. 311-318, 2001.",
        "[3] J. M. Diamond et al., \"Mapping the human epileptic network using intracranial EEG high-frequency activity,\" Brain, vol. 144, no. 10, pp. 3075-3087, 2021.",
        "[4] K. A. Davis et al., \"A validated library of human electrocorticographic data and analyses (ds004100),\" Sci. Data, vol. 9, no. 1, pp. 1-10, 2022."
    ]
    for r_idx, ref in enumerate(refs):
        p_r = tf_ref.paragraphs[0] if r_idx == 0 else tf_ref.add_paragraph()
        p_r.text = ref
        p_r.font.name = FONT_NAME
        p_r.font.size = Pt(14)
        p_r.font.color.rgb = C_TEXT_MUTED
        if r_idx > 0:
            p_r.space_before = Pt(5)

    # =========================================================================
    # [하단 사사 (Acknowledgment Footer)]
    # =========================================================================
    footer_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Mm(25), Mm(1140), Mm(791), Mm(22))
    footer_box.fill.solid()
    footer_box.fill.fore_color.rgb = C_WHITE
    footer_box.line.color.rgb = C_CARD_BORDER
    footer_box.line.width = Pt(1)

    tf_foot = footer_box.text_frame
    tf_foot.word_wrap = True
    tf_foot.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf_foot.margin_left = Mm(10)
    p_foot = tf_foot.paragraphs[0]
    p_foot.text = "* 본 결과물은 교육부와 경기도 재원으로 지원을 받아 수행된 경기 지역혁신중심 대학지원사업(경기RISE사업)의 연구결과 입니다. (2025-RISE-09-A21)"
    p_foot.font.name = FONT_NAME
    p_foot.font.size = Pt(15.5)
    p_foot.font.bold = True
    p_foot.font.color.rgb = C_NAVY
    p_foot.alignment = PP_ALIGN.CENTER

    output_filename = "JBER_학술포스터_템플릿_A0.pptx"
    prs.save(output_filename)
    print(f"Successfully generated logically aligned poster: {output_filename}")

if __name__ == "__main__":
    create_poster()
