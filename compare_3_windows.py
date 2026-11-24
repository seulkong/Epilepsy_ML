#!/usr/bin/env python3
"""
3-Way Window Comparison Experiment
-----------------------------------
Compares prediction performance across 3 time windows:
  1. Early Seizure Window (0 - 30s)
  2. Late Seizure Window (30s - 60s)
  3. Full Seizure Window
"""

import os
import sys
import pandas as pd
import numpy as np

try:
    from Grouping_compare import evaluate_feature_subset, GROUP_A_FEATURES, FULL_FEATURES
except ImportError:
    from train_ml_experiments import evaluate_feature_subset, GROUP_A_FEATURES, FULL_FEATURES

def main():
    csv_full = 'preprocessed_features_dataset.csv'
    if not os.path.exists(csv_full):
        csv_full = 'preprocessed_features.csv'

    csv_30s = 'preprocessed_features_30s.csv'
    csv_late = 'preprocessed_features_30_to_60s.csv'

    for path, name in [(csv_full, 'Full'), (csv_30s, '0-30s'), (csv_late, '30-60s')]:
        if not os.path.exists(path):
            print(f"Error: {name} dataset ({path}) not found.")
            sys.exit(1)

    df_full = pd.read_csv(csv_full)
    df_30s = pd.read_csv(csv_30s)
    df_late = pd.read_csv(csv_late)

    print(f"=== Loading 3-Way Datasets ===")
    print(f"Full: {len(df_full)} rows, 0-30s: {len(df_30s)} rows, 30-60s: {len(df_late)} rows\n")

    res_full = evaluate_feature_subset(df_full, GROUP_A_FEATURES, n_splits=5)
    res_full['Dataset'] = "3. Full Seizure Window"

    res_30s = evaluate_feature_subset(df_30s, GROUP_A_FEATURES, n_splits=5)
    res_30s['Dataset'] = "1. Early Window (0 - 30s)"

    res_late = evaluate_feature_subset(df_late, GROUP_A_FEATURES, n_splits=5)
    res_late['Dataset'] = "2. Late Window (30s - 60s)"

    combined = pd.concat([res_30s, res_late, res_full], ignore_index=True)
    combined.sort_values(by=['Model', 'Dataset'], inplace=True)

    print("=" * 80)
    print("=== PROFESSOR EXPERIMENT: 3-WAY SEIZURE WINDOW COMPARISON (0-30s vs 30-60s vs Full) ===")
    print("=" * 80)
    print(combined.to_string(index=False))
    print("=" * 80 + "\n")

    combined.to_csv("experiment_3_way_window_comparison.csv", index=False)
    print("Saved 3-way window comparison to experiment_3_way_window_comparison.csv")

if __name__ == '__main__':
    main()
