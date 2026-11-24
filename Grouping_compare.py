#!/usr/bin/env python3
"""
Prof. Feedback Experiment 1 & 3: Feature Group Ablation & Group K-Fold Cross-Validation
--------------------------------------------------------------------------------------
Feature Groups:
  - Group A (6 Spatial Trajectory Features):
      ['min_dist_to_resect', 'mean_dist_to_resect', 'residence_ratio', 'velocity_mean', 'velocity_max', 'trajectory_dispersion']
  - Group B (9 Clinical & Anatomical Features):
      ['age', 'age_onset', 'sex', 'therapy', 'implant', 'lesion_status', 'soz_count', 'resect_count', 'initial_soz_resect_dist']
  - Group A + B: All 15 predictor features combined

Group K-Fold Cross-Validation:
  - Grouped by 'participant_id' to prevent data leakage between train and test sets for the same patient.
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    ExtraTreesClassifier,
    HistGradientBoostingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier

# Optional imports for advanced boosting models
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

try:
    import catboost as cb
    HAS_CB = True
except ImportError:
    HAS_CB = False

# Define Feature Groups
GROUP_A_FEATURES = [
    'min_dist_to_resect',
    'mean_dist_to_resect',
    'residence_ratio',
    'velocity_mean',
    'velocity_max',
    'trajectory_dispersion'
]

GROUP_B_FEATURES = [
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

FULL_FEATURES = GROUP_A_FEATURES + GROUP_B_FEATURES

def get_models():
    """Returns a dictionary of ML model architectures to evaluate."""
    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'ExtraTrees': ExtraTreesClassifier(n_estimators=100, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'HistGradientBoosting': HistGradientBoostingClassifier(random_state=42),
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
        'MLPClassifier': MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
    }
    if HAS_XGB:
        models['XGBoost'] = xgb.XGBClassifier(n_estimators=100, random_state=42, eval_metric='logloss')
    if HAS_LGB:
        models['LightGBM'] = lgb.LGBMClassifier(n_estimators=100, random_state=42, verbose=-1)
    if HAS_CB:
        models['CatBoost'] = cb.CatBoostClassifier(iterations=100, random_state=42, verbose=0)
    return models

def evaluate_feature_subset(df, feature_cols, n_splits=5):
    """Evaluates models using GroupKFold cross-validation on a specified feature subset."""
    # Filter rows with NaNs in selected feature columns or target
    sub_df = df.dropna(subset=feature_cols + ['outcome', 'participant_id']).copy()
    
    X = sub_df[feature_cols].values
    y = sub_df['outcome'].values
    groups = sub_df['participant_id'].values

    # Determine unique groups for GroupKFold
    unique_groups = np.unique(groups)
    actual_n_splits = min(n_splits, len(unique_groups))
    
    gkf = GroupKFold(n_splits=actual_n_splits)
    models = get_models()
    
    results = []

    for model_name, model in models.items():
        y_true_all = []
        y_pred_prob_all = []
        y_pred_class_all = []

        for train_idx, test_idx in gkf.split(X, y, groups):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            # Scaling for models sensitive to scale
            if model_name in ['LogisticRegression', 'MLPClassifier']:
                scaler = StandardScaler()
                X_train = scaler.fit_transform(X_train)
                X_test = scaler.transform(X_test)

            model.fit(X_train, y_train)

            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X_test)[:, 1]
            elif hasattr(model, "decision_function"):
                probs = model.decision_function(X_test)
            else:
                probs = model.predict(X_test)

            preds = model.predict(X_test)

            y_true_all.extend(y_test)
            y_pred_prob_all.extend(probs)
            y_pred_class_all.extend(preds)

        y_true_all = np.array(y_true_all)
        y_pred_prob_all = np.array(y_pred_prob_all)
        y_pred_class_all = np.array(y_pred_class_all)

        # Compute metrics
        roc_auc = roc_auc_score(y_true_all, y_pred_prob_all)
        pr_auc = average_precision_score(y_true_all, y_pred_prob_all)
        acc = accuracy_score(y_true_all, y_pred_class_all)
        f1 = f1_score(y_true_all, y_pred_class_all)

        results.append({
            'Model': model_name,
            'ROC-AUC': round(roc_auc, 4),
            'PR-AUC': round(pr_auc, 4),
            'Accuracy': round(acc, 4),
            'F1-Score': round(f1, 4)
        })

    return pd.DataFrame(results)

def main():
    # Load dataset
    csv_file = 'preprocessed_features_dataset.csv'
    if not os.path.exists(csv_file):
        csv_file = 'preprocessed_features.csv'
    
    if not os.path.exists(csv_file):
        print(f"Error: Dataset CSV file not found in {os.getcwd()}")
        sys.exit(1)

    print(f"=== Loading dataset from {csv_file} ===")
    df = pd.read_csv(csv_file)
    print(f"Dataset Shape: {df.shape}")
    print(f"Total Unique Patients: {df['participant_id'].nunique()}")
    print(f"Outcome Distribution: S(1)={sum(df['outcome']==1)}, F(0)={sum(df['outcome']==0)}")
    print("=" * 60)

    # 1. Evaluate Group A + B (Full Features)
    print("\n[1] Evaluating Group A + B (Full 15 Features)...")
    res_full = evaluate_feature_subset(df, FULL_FEATURES)
    res_full['Feature_Set'] = 'Group A + B (Full)'

    # 2. Evaluate Group A Only (Spatial Trajectory Features)
    print("\n[2] Evaluating Group A Only (6 Spatial Trajectory Features)...")
    res_group_a = evaluate_feature_subset(df, GROUP_A_FEATURES)
    res_group_a['Feature_Set'] = 'Group A Only (Trajectory)'

    # 3. Evaluate Group B Only (Clinical & Anatomical Features)
    print("\n[3] Evaluating Group B Only (9 Clinical/Anatomical Features)...")
    res_group_b = evaluate_feature_subset(df, GROUP_B_FEATURES)
    res_group_b['Feature_Set'] = 'Group B Only (Clinical/Anatomical)'

    # Combine all results
    combined_res = pd.concat([res_full, res_group_a, res_group_b], ignore_index=True)
    combined_res = combined_res[['Feature_Set', 'Model', 'ROC-AUC', 'PR-AUC', 'Accuracy', 'F1-Score']]
    combined_res.sort_values(by=['Model', 'Feature_Set'], inplace=True)

    print("\n" + "=" * 80)
    print("=== PROFESSOR EXPERIMENT 1 & 3 SUMMARY RESULTS (Group K-Fold CV) ===")
    print("=" * 80)
    print(combined_res.to_string(index=False))
    print("=" * 80)

    # Save to CSV
    out_csv = 'experiment_1_feature_ablation_results.csv'
    combined_res.to_csv(out_csv, index=False)
    print(f"\nSaved ablation experiment results to {out_csv}")

if __name__ == '__main__':
    main()
