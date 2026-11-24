#!/usr/bin/env python3
"""
Prof. Feedback Experiment 2: Compare Full Seizure Trajectory vs. Initial 30s Trajectory
--------------------------------------------------------------------------------------
Evaluates and compares prediction performance (ROC-AUC, PR-AUC, Accuracy, F1)
between full-length seizure trajectory features and initial 30s trajectory features.
"""

import os
import sys
import pandas as pd
import numpy as np
try:
    from Grouping_compare import evaluate_feature_subset, FULL_FEATURES, GROUP_A_FEATURES
except ImportError:
    from train_ml_experiments import evaluate_feature_subset, FULL_FEATURES, GROUP_A_FEATURES

def main():
    csv_full = 'preprocessed_features_dataset.csv'
    if not os.path.exists(csv_full):
        csv_full = 'preprocessed_features.csv'

    csv_30s = 'preprocessed_features_30s.csv'

    if not os.path.exists(csv_full):
        print(f"Error: Full dataset {csv_full} not found.")
        sys.exit(1)

    if not os.path.exists(csv_30s):
        print(f"Error: 30s dataset {csv_30s} not found. Run fast_build_dataset_30s.py first.")
        sys.exit(1)

    print(f"=== Loading Full Dataset ({csv_full}) and 30s Dataset ({csv_30s}) ===")
    df_full = pd.read_csv(csv_full)
    df_30s = pd.read_csv(csv_30s)

    print(f"Full Dataset Rows: {len(df_full)}, 30s Dataset Rows: {len(df_30s)}")

    # 1. Evaluate Full Seizure Window (Group A Trajectory Only)
    print("\n[1] Evaluating FULL Seizure Trajectory Features (Group A)...")
    res_full_a = evaluate_feature_subset(df_full, GROUP_A_FEATURES)
    res_full_a['Dataset'] = 'Full Seizure Window'

    # 2. Evaluate Initial 30s Window (Group A Trajectory Only)
    print("\n[2] Evaluating INITIAL 30s Trajectory Features (Group A)...")
    res_30s_a = evaluate_feature_subset(df_30s, GROUP_A_FEATURES)
    res_30s_a['Dataset'] = 'Initial 30s Window'

    combined = pd.concat([res_full_a, res_30s_a], ignore_index=True)
    combined = combined[['Dataset', 'Model', 'ROC-AUC', 'PR-AUC', 'Accuracy', 'F1-Score']]
    combined.sort_values(by=['Model', 'Dataset'], inplace=True)

    print("\n" + "=" * 80)
    print("=== PROFESSOR EXPERIMENT 2 RESULTS: FULL VS. INITIAL 30s TRAJECTORY ===")
    print("=" * 80)
    print(combined.to_string(index=False))
    print("=" * 80)

    out_csv = 'experiment_2_full_vs_30s_results.csv'
    combined.to_csv(out_csv, index=False)
    print(f"\nSaved 30s vs Full comparison results to {out_csv}")

if __name__ == '__main__':
    main()
