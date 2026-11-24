#!/usr/bin/env python3
"""
Master Comparative Evaluation Pipeline:
Option 1 (External Dataset Integration) vs Option 2 (Data Augmentation & Advanced Trajectory Engineering)
---------------------------------------------------------------------------------------------------------
Evaluates 4 experimental conditions under strict Patient-Level Group Cross-Validation (GroupKFold):
  - Condition 0: Baseline (Raw ds004100, 15 features)
  - Condition 1: Option 1 Only (External SWEC-ETHZ & Kaggle SSL Features)
  - Condition 2: Option 2 Only (Data Augmentation & 3D Curvature/Torsion Math)
  - Condition 3: Option 1 + 2 Combined (Hybrid Approach)

Outputs: experiment_option1_vs_option2_results.csv
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
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

# Import custom modules
import augment_spatial_trajectory
import process_external_datasets

# Define Baseline Features
BASELINE_FEATURES = [
    'min_dist_to_resect', 'mean_dist_to_resect', 'residence_ratio',
    'velocity_mean', 'velocity_max', 'trajectory_dispersion',
    'age', 'age_onset', 'sex', 'therapy', 'implant', 'lesion_status',
    'soz_count', 'resect_count', 'initial_soz_resect_dist'
]

OPTION1_EXTRA_FEATURES = [
    'ext_psd_alpha_beta', 'ext_psd_gamma', 'ext_spectral_entropy',
    'ext_signal_power', 'ext_phase_coherence'
]

OPTION2_EXTRA_FEATURES = [
    'trajectory_curvature', 'trajectory_torsion',
    'directional_cosine_to_resect', 'velocity_dynamics_ratio'
]

def get_models():
    """Returns classification model suite."""
    return {
        'LogisticRegression': LogisticRegression(max_iter=1000, C=1.0, random_state=42),
        'MLPClassifier': MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42),
        'RandomForest': RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42),
        'ExtraTrees': ExtraTreesClassifier(n_estimators=100, max_depth=6, random_state=42),
        'GradientBoosting': GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
    }

def evaluate_condition(df, feature_cols, condition_name, n_splits=5):
    """Runs GroupKFold 5-Fold CV and Hold-out Evaluation for a given dataset and feature subset."""
    sub_df = df.dropna(subset=feature_cols + ['outcome', 'participant_id']).copy()

    X = sub_df[feature_cols].values
    y = sub_df['outcome'].values
    groups = sub_df['participant_id'].values

    # Hold-out Split (80% Train Patients / 20% Test Patients)
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_idx = next(gss.split(X, y, groups))

    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    groups_train = groups[train_idx]

    n_train_pts = len(np.unique(groups_train))
    actual_n_splits = min(n_splits, n_train_pts)
    gkf = GroupKFold(n_splits=actual_n_splits)

    models = get_models()
    results = []

    for model_name, model in models.items():
        cv_roc_scores = []
        cv_pr_scores = []

        # 5-Fold Patient-Level CV inside Train Patients
        for cv_tr, cv_val in gkf.split(X_train, y_train, groups_train):
            X_tr, X_v = X_train[cv_tr], X_train[cv_val]
            y_tr, y_v = y_train[cv_tr], y_train[cv_val]

            if model_name in ['LogisticRegression', 'MLPClassifier']:
                scaler = StandardScaler()
                X_tr = scaler.fit_transform(X_tr)
                X_v = scaler.transform(X_v)

            model.fit(X_tr, y_tr)
            probs_v = model.predict_proba(X_v)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_v)

            if len(np.unique(y_v)) > 1:
                cv_roc_scores.append(roc_auc_score(y_v, probs_v))
                cv_pr_scores.append(average_precision_score(y_v, probs_v))

        # Final Hold-out Test Evaluation
        if model_name in ['LogisticRegression', 'MLPClassifier']:
            scaler_full = StandardScaler()
            X_train_scaled = scaler_full.fit_transform(X_train)
            X_test_scaled = scaler_full.transform(X_test)
            model.fit(X_train_scaled, y_train)
            probs_test = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_test_scaled)
            preds_test = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            probs_test = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_test)
            preds_test = model.predict(X_test)

        test_roc = roc_auc_score(y_test, probs_test) if len(np.unique(y_test)) > 1 else 0.5
        test_pr = average_precision_score(y_test, probs_test) if len(np.unique(y_test)) > 1 else 0.5
        test_acc = accuracy_score(y_test, preds_test)
        test_f1 = f1_score(y_test, preds_test, zero_division=0)

        mean_cv_roc = np.mean(cv_roc_scores) if cv_roc_scores else test_roc

        results.append({
            'Condition': condition_name,
            'Model': model_name,
            'Train CV ROC-AUC': round(mean_cv_roc, 4),
            'Holdout ROC-AUC': round(test_roc, 4),
            'Holdout PR-AUC': round(test_pr, 4),
            'Holdout Accuracy': round(test_acc, 4),
            'Holdout F1-Score': round(test_f1, 4)
        })

    return pd.DataFrame(results)

def main():
    csv_raw = 'preprocessed_features.csv'
    if not os.path.exists(csv_raw):
        print(f"Error: {csv_raw} not found.")
        sys.exit(1)

    print("=== Step 1: Loading Raw Dataset ===")
    df_raw = pd.read_csv(csv_raw)

    print("=== Step 2: Preparing Option 1 Dataset (External SSL Features) ===")
    df_opt1 = process_external_datasets.create_option1_dataset(df_raw)

    print("=== Step 3: Preparing Option 2 Dataset (Augmented + Advanced Trajectory Features) ===")
    df_opt2 = augment_spatial_trajectory.augment_dataset_option2(df_raw, num_augmented_copies=2)

    print("=== Step 4: Preparing Option 1 + 2 Hybrid Dataset ===")
    df_opt12 = process_external_datasets.create_option1_dataset(df_opt2)

    # 1. Condition 0: Baseline
    print("\n[Condition 0] Evaluating Baseline...")
    res_cond0 = evaluate_condition(df_raw, BASELINE_FEATURES, 'Condition 0 (Baseline)')

    # 2. Condition 1: Option 1 Only
    print("\n[Condition 1] Evaluating Option 1 (External Datasets)...")
    res_cond1 = evaluate_condition(df_opt1, BASELINE_FEATURES + OPTION1_EXTRA_FEATURES, 'Condition 1 (Option 1: External SSL)')

    # 3. Condition 2: Option 2 Only
    print("\n[Condition 2] Evaluating Option 2 (Data Augmentation + Trajectory Math)...")
    res_cond2 = evaluate_condition(df_opt2, BASELINE_FEATURES + OPTION2_EXTRA_FEATURES, 'Condition 2 (Option 2: Augmentation & Math)')

    # 4. Condition 3: Option 1 + 2 Combined
    print("\n[Condition 3] Evaluating Option 1 + 2 Combined (Hybrid)...")
    res_cond3 = evaluate_condition(df_opt12, BASELINE_FEATURES + OPTION1_EXTRA_FEATURES + OPTION2_EXTRA_FEATURES, 'Condition 3 (Option 1+2 Hybrid)')

    # Combine all results
    combined = pd.concat([res_cond0, res_cond1, res_cond2, res_cond3], ignore_index=True)
    combined.sort_values(by=['Model', 'Holdout ROC-AUC'], ascending=[True, False], inplace=True)

    print("\n" + "=" * 90)
    print("=== EXPERIMENT RESULTS: OPTION 1 VS OPTION 2 COMPARATIVE EVALUATION (GroupKFold) ===")
    print("=" * 90)
    print(combined.to_string(index=False))
    print("=" * 90)

    out_csv = 'experiment_option1_vs_option2_results.csv'
    combined.to_csv(out_csv, index=False)
    print(f"\nSaved master comparison results to {out_csv}")

if __name__ == '__main__':
    main()
