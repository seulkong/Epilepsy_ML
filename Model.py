#!/usr/bin/env python3
"""
================================================================================
전체 피처셋 머신러닝 & 딥러닝 모델 학습 및 임상 의사결정 임계값 도출 스크립트
================================================================================
[1번 파트] 머신러닝/딥러닝 분류 모델 학습
  - 베이스라인 모델: Random Forest, XGBoost, LightGBM
  - 딥러닝 모델: MLP (Multi-Layer Perceptron), TabNet
  - 환자 단위 교차검증: Group K-Fold (동일 환자의 발작 세션 분리로 데이터 누출 방지)

[2번 파트] 수술 여부 판단용 임계값(Cut-off Threshold) 정량 도출
  - 발작 전파 속도(velocity_mean) 및 절제 영역 체류 비율(residence_ratio) 임계값 산출
  - 임계값 기반 환자 맞춤형 치료 권고사항 (개두 절제술 vs 뇌 자극기 RNS/DBS / 레이저 수술) 자동 출력
================================================================================
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score, f1_score,
    roc_curve
)
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

# XGBoost 및 LightGBM 라이브러리 로드 시도
try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False

# TabNet 딥러닝 라이브러리 로드 시도
try:
    from pytorch_tabnet.tab_model import TabNetClassifier
    import torch
    HAS_TABNET = True
except ImportError:
    HAS_TABNET = False

# 예측에 사용할 전체 15개 피처 목록 정의
PREDICTOR_FEATURES = [
    # 공간 궤적 피처 (6개)
    'min_dist_to_resect',
    'mean_dist_to_resect',
    'residence_ratio',
    'velocity_mean',
    'velocity_max',
    'trajectory_dispersion',
    # 임상 및 해부학 피처 (9개)
    'age',
    'age_onset',
    'sex',
    'therapy',
    'implant',
    'lesion_status',
    'soz_count',
    'resect_count',
    'initial_soz_resect_dist'
]


# ==============================================================================
# [1번 파트] 머신러닝 및 딥러닝 분류 모델 생성 및 학습 함수
# ==============================================================================

def get_specified_models():
    """요청된 베이스라인 머신러닝(RF, XGB, LGB) 및 딥러닝(MLP, TabNet) 모델 객체를 반환합니다."""
    models = {}
    
    # 1. 베이스라인 머신러닝 모델
    models['RandomForest (베이스라인)'] = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    
    if HAS_XGB:
        models['XGBoost (베이스라인)'] = xgb.XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.05,
            random_state=42, eval_metric='logloss'
        )
    else:
        print("[안내] XGBoost 라이브러리가 미설치되어 있습니다. 'pip install xgboost'로 추가 가능합니다.")

    if HAS_LGB:
        models['LightGBM (베이스라인)'] = lgb.LGBMClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.05,
            random_state=42, verbose=-1
        )
    else:
        print("[안내] LightGBM 라이브러리가 미설치되어 있습니다. 'pip install lightgbm'으로 추가 가능합니다.")

    # 2. 딥러닝 모델
    models['MLP (딥러닝 - 다층 신경망)'] = MLPClassifier(
        hidden_layer_sizes=(128, 64), activation='relu',
        solver='adam', max_iter=1000, random_state=42
    )

    if HAS_TABNET:
        models['TabNet (딥러닝 - 정형 데이터 전용)'] = 'TabNetClassifier'
    else:
        print("[안내] pytorch-tabnet 라이브러리가 미설치되어 있습니다. 'pip install pytorch-tabnet torch'로 추가 가능합니다.")

    return models

def run_part1_model_training(df, n_splits=5):
    """
    [1번 파트 실행 함수]
    1. 최초 환자 단위 80:20 고정 분할 (Train: 44명 환자 / Hold-out Test: 11명 환자)
    2. Train 환자 44명을 대상으로 Group K-Fold (5 Folds) 교차 검증 수행
    3. 최종 독리 Hold-out Test 세트(11명 환자)에서 모델 평가 진행
    """
    print("\n" + "=" * 80)
    print(" [1번 파트] 전체 피처셋 기반 분류 알고리즘 및 딥러닝 모델 학습 시작")
    print("=" * 80)
    
    sub_df = df.dropna(subset=PREDICTOR_FEATURES + ['outcome', 'participant_id']).copy()
    
    X = sub_df[PREDICTOR_FEATURES].values
    y = sub_df['outcome'].values
    groups = sub_df['participant_id'].values

    # --------------------------------------------------------------------------
    # [Step 1] 환자 단위 80:20 고정 Hold-out 분할 (Train 44명 / Test 11명)
    # --------------------------------------------------------------------------
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx_holdout, test_idx_holdout = next(gss.split(X, y, groups))

    X_train_full, X_test_holdout = X[train_idx_holdout], X[test_idx_holdout]
    y_train_full, y_test_holdout = y[train_idx_holdout], y[test_idx_holdout]
    groups_train_full = groups[train_idx_holdout]
    groups_test_holdout = groups[test_idx_holdout]

    n_train_pts = len(np.unique(groups_train_full))
    n_test_pts = len(np.unique(groups_test_holdout))

    print(f" [데이터셋 80:20 고정 분할 완료]")
    print(f"  • 훈련용(Train Set): {len(X_train_full)}개 레코드 (환자 수: {n_train_pts}명)")
    print(f"  • 최종 평가용(Hold-out Test Set): {len(X_test_holdout)}개 레코드 (환자 수: {n_test_pts}명)")
    print("-" * 80)

    # --------------------------------------------------------------------------
    # [Step 2] 훈련 데이터셋 내 Group K-Fold CV 및 Hold-out Test 최종 평가
    # --------------------------------------------------------------------------
    actual_n_splits = min(n_splits, n_train_pts)
    gkf = GroupKFold(n_splits=actual_n_splits)

    models_dict = get_specified_models()
    results = []

    for model_name, model_obj in models_dict.items():
        print(f" -> {model_name} 모델 학습 (Train 44명 5-Fold CV 후 Hold-out 11명 평가) 진행 중...")
        
        # 1. Train 데이터셋 44명 내부에서 Group K-Fold 교차검증 수행
        cv_auc_scores = []
        for train_cv_idx, val_cv_idx in gkf.split(X_train_full, y_train_full, groups_train_full):
            X_tr, X_val = X_train_full[train_cv_idx], X_train_full[val_cv_idx]
            y_tr, y_val = y_train_full[train_cv_idx], y_train_full[val_cv_idx]

            scaler = StandardScaler()
            X_tr_s = scaler.fit_transform(X_tr)
            X_val_s = scaler.transform(X_val)

            if model_name == 'TabNet (딥러닝 - 정형 데이터 전용)' and HAS_TABNET:
                model = TabNetClassifier(verbose=0, seed=42)
                model.fit(X_tr_s, y_tr, eval_set=[(X_val_s, y_val)], patience=15, max_epochs=100)
                val_probs = model.predict_proba(X_val_s)[:, 1]
            elif 'MLP' in model_name:
                model_obj.fit(X_tr_s, y_tr)
                val_probs = model_obj.predict_proba(X_val_s)[:, 1]
            else:
                model_obj.fit(X_tr, y_tr)
                val_probs = model_obj.predict_proba(X_val)[:, 1]

            cv_auc_scores.append(roc_auc_score(y_val, val_probs))

        # 2. 훈련셋 전체(44명)로 재학습 후 최종 독립 Hold-out Test Set (11명)에 대해 예측 평가
        scaler_final = StandardScaler()
        X_tr_final_s = scaler_final.fit_transform(X_train_full)
        X_te_holdout_s = scaler_final.transform(X_test_holdout)

        if model_name == 'TabNet (딥러닝 - 정형 데이터 전용)' and HAS_TABNET:
            final_model = TabNetClassifier(verbose=0, seed=42)
            final_model.fit(X_tr_final_s, y_train_full, max_epochs=100)
            probs = final_model.predict_proba(X_te_holdout_s)[:, 1]
            preds = final_model.predict(X_te_holdout_s)
        elif 'MLP' in model_name:
            model_obj.fit(X_tr_final_s, y_train_full)
            probs = model_obj.predict_proba(X_te_holdout_s)[:, 1]
            preds = model_obj.predict(X_te_holdout_s)
        else:
            model_obj.fit(X_train_full, y_train_full)
            probs = model_obj.predict_proba(X_test_holdout)[:, 1]
            preds = model_obj.predict(X_test_holdout)

        # 최종 Hold-out Test Set (11명 환자) 성능 평가지표 계산
        roc_auc = roc_auc_score(y_test_holdout, probs)
        pr_auc = average_precision_score(y_test_holdout, probs)
        acc = accuracy_score(y_test_holdout, preds)
        f1 = f1_score(y_test_holdout, preds)

        results.append({
            '모델 아키텍처 (Model)': model_name,
            'Train CV ROC-AUC': round(np.mean(cv_auc_scores), 4),
            'Test Hold-out ROC-AUC': round(roc_auc, 4),
            'Test Hold-out PR-AUC': round(pr_auc, 4),
            'Test 정확도 (Accuracy)': round(acc, 4),
            'Test F1-Score': round(f1, 4)
        })

    res_df = pd.DataFrame(results).sort_values(by='Test Hold-out ROC-AUC', ascending=False)
    
    print("\n" + "-" * 80)
    print(" 전체 피처셋 모델 성능 비교표 (Group K-Fold 교차검증)")
    print("-" * 80)
    print(res_df.to_string(index=False))
    print("-" * 80)

    res_df.to_csv('part1_full_feature_model_performance.csv', index=False)
    print(" -> 1번 파트 결과가 'part1_full_feature_model_performance.csv' 파일로 저장되었습니다.\n")
    return sub_df


# ==============================================================================
# [2번 파트] 수술 여부 판단용 임계값(Cut-off Threshold) 정량 도출 함수
# ==============================================================================

def run_part2_clinical_cutoff_derivation(df):
    """
    [2번 파트 실행 함수]
    발작 전파 속도(velocity_mean) 및 절제 영역 체류 비율(residence_ratio)의
    최적 임계값을 정량 도출하고 임상 의사결정 규칙을 출력합니다.
    """
    print("=" * 80)
    print(" [2번 파트] 수술 여부 판단용 최적 임계값(Cut-off Threshold) 정량 도출")
    print("=" * 80)

    # 1. 발작 전파 속도(velocity_mean) 임계값 산출
    # 전파 속도가 빠를수록 고위험군 -> 수술 실패(outcome=0)와 연관
    s_succ = df[df['outcome'] == 1]['velocity_mean'].dropna()
    s_fail = df[df['outcome'] == 0]['velocity_mean'].dropna()

    fpr, tpr, thresholds = roc_curve(
        (df['outcome'] == 1).astype(int),
        -df['velocity_mean']  # 속도가 낮을수록 수술 성공(1)이므로 음수 처리
    )
    j_scores = tpr - fpr
    best_idx = np.argmax(j_scores)
    best_vel_cutoff = -thresholds[best_idx]

    print("\n[2-1] 발작 전파 평균 속도 (velocity_mean) 임계값 산출 결과:")
    print(f"  • 수술 성공군 (Outcome=1) 평균 전파 속도: {s_succ.mean():.4f} mm/s (중앙값: {s_succ.median():.4f} mm/s)")
    print(f"  • 수술 실패군 (Outcome=0) 평균 전파 속도: {s_fail.mean():.4f} mm/s (중앙값: {s_fail.median():.4f} mm/s)")
    print(f"  ★ 도출된 최적 수술 성공 전파 속도 임계값: <= {best_vel_cutoff:.2f} mm/s")

    # 2. 절제 영역 체류 비율(residence_ratio) 임계값 산출
    fpr_r, tpr_r, thresholds_r = roc_curve(
        (df['outcome'] == 1).astype(int),
        df['residence_ratio']
    )
    j_scores_r = tpr_r - fpr_r
    valid_mask = ~np.isinf(thresholds_r)
    if np.any(valid_mask):
        best_idx_r = np.argmax(j_scores_r[valid_mask])
        best_res_cutoff = thresholds_r[valid_mask][best_idx_r]
    else:
        best_res_cutoff = 50.0

    r_succ = df[df['outcome'] == 1]['residence_ratio'].dropna()
    r_fail = df[df['outcome'] == 0]['residence_ratio'].dropna()

    print("\n[2-2] 절제 영역 체류 비율 (residence_ratio) 임계값 산출 결과:")
    print(f"  • 수술 성공군 (Outcome=1) 평균 체류 비율: {r_succ.mean():.2f}% (중앙값: {r_succ.median():.2f}%)")
    print(f"  • 수술 실패군 (Outcome=0) 평균 체류 비율: {r_fail.mean():.2f}% (중앙값: {r_fail.median():.2f}%)")
    print(f"  ★ 도출된 최적 체류 비율 임계값: >= {best_res_cutoff:.2f}%")

    # 3. 임상 의사결정 보조 규칙 가이드라인 출력
    print("\n" + "=" * 80)
    print(" [2번 파트 최종 산출] 환자 맞춤형 치료법 결정을 위한 임상 가이드라인")
    print("=" * 80)
    print(f" 🟢 저위험 / 수술 성공 가능성 높음 (개두 절제술 RESECTION 우선 권장):")
    print(f"     - 조건: 발작 전파 속도 <= {best_vel_cutoff:.2f} mm/s")
    print(f"     - 근거: 발작이 국소 부위에서 천천히 전파되므로 뇌 조식을 잘라내는 절제 수술 완치율이 높음.\n")
    print(f" 🔴 고위험 / 개두 수술 부적합 (뇌 자극기 RNS/DBS 또는 레이저 수술 ABLATION 권장):")
    print(f"     - 조건: 발작 전파 속도 > {best_vel_cutoff:.2f} mm/s")
    print(f"     - 근거: 발작이 뇌 전체로 순식간에 퍼지는 고위험군이므로 뇌를 잘라내는 개두술을 피하고")
    print(f"            부담이 적은 뇌 자극기(RNS/DBS) 치료나 레이저 수술(Laser Ablation)을 우선 추천함.")
    print("=" * 80 + "\n")


# ==============================================================================
# 메인 실행 제어
# ==============================================================================

def main():
    # 데이터셋 파일 로드
    csv_file = 'preprocessed_features_dataset.csv'
    if not os.path.exists(csv_file):
        csv_file = 'preprocessed_features.csv'

    if not os.path.exists(csv_file):
        print(f"[오류] 데이터셋 CSV 파일({csv_file})을 찾을 수 없습니다.")
        sys.exit(1)

    print(f"=== 전처리 데이터셋 로드 완료: {csv_file} ===")
    df = pd.read_csv(csv_file)
    print(f"데이터 크기: {df.shape}, 총 환자 수: {df['participant_id'].nunique()}명")

    # 1번 파트 실행: 분류 알고리즘 및 딥러닝 모델 학습
    sub_df = run_part1_model_training(df)

    # 2번 파트 실행: 수술 여부 판단용 임계값 정량 도출 및 의사결정 규칙 산출
    run_part2_clinical_cutoff_derivation(sub_df)

if __name__ == '__main__':
    main()
