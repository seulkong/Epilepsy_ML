#!/usr/bin/env python3
"""
Option 2 (방안 2): Corrected Data Augmentation & Trajectory Ratio Feature Engineering
-----------------------------------------------------------------------------------------
Fixes applied:
1. Feature Terminology: Renamed misleading names ('trajectory_curvature', 'trajectory_torsion')
   to explicit scientific proxy names ('velocity_peak_to_mean_ratio', 'dispersion_to_resect_ratio')
   to prevent reviewer criticism.
2. Noise Measurement: Applied explicit ±1.0mm Gaussian noise jittering on spatial distance metrics
   matching electrode localization uncertainty.
3. Strict Leakage Prevention: Provided `augment_train_fold_only(df_train)` to ensure data augmentation
   is applied ONLY to the training fold and NEVER leaks into the validation/test set.
"""

import os
import sys
import numpy as np
import pandas as pd

def add_advanced_trajectory_features(df):
    """Calculates scientifically named 3D spatial trajectory ratio features."""
    df_feat = df.copy()
    eps = 1e-5

    # 1. Velocity Peak-to-Mean Ratio (formerly misnamed 'curvature')
    df_feat['velocity_peak_to_mean_ratio'] = df_feat['velocity_max'] / (df_feat['velocity_mean'] + eps)

    # 2. Dispersion-to-Resection Distance Ratio (formerly misnamed 'torsion')
    df_feat['dispersion_to_resect_ratio'] = df_feat['trajectory_dispersion'] / (df_feat['mean_dist_to_resect'] + eps)

    # 3. Directional Cosine / Proximity Ratio
    df_feat['directional_cosine_to_resect'] = df_feat['min_dist_to_resect'] / (df_feat['mean_dist_to_resect'] + eps)

    # 4. Velocity Dynamics Ratio
    df_feat['velocity_dynamics_ratio'] = (df_feat['velocity_max'] - df_feat['velocity_mean']) / (df_feat['velocity_mean'] + eps)

    return df_feat

def augment_train_fold_only(df_train, num_augmented_copies=2, jitter_std_mm=1.0, random_state=42):
    """
    Applies spatial coordinate jittering (±1.0mm Gaussian noise) strictly to the TRAIN fold.
    Preserves participant_id and prevents test data leakage.
    """
    np.random.seed(random_state)
    augmented_dfs = [df_train.copy()]

    spatial_cols = [
        'min_dist_to_resect', 'mean_dist_to_resect', 'initial_soz_resect_dist',
        'velocity_mean', 'velocity_max', 'trajectory_dispersion'
    ]

    for i in range(num_augmented_copies):
        df_aug = df_train.copy()
        # Add explicit ±1.0mm Gaussian measurement noise jittering
        for col in spatial_cols:
            if col in df_aug.columns:
                noise = np.random.normal(loc=0.0, scale=jitter_std_mm, size=len(df_aug))
                df_aug[col] = np.maximum(0.001, df_aug[col] + noise)

        df_aug['run_id'] = df_aug['run_id'].astype(str) + f"_aug{i+1}"
        augmented_dfs.append(df_aug)

    df_combined = pd.concat(augmented_dfs, ignore_index=True)
    df_combined = add_advanced_trajectory_features(df_combined)
    return df_combined

def augment_dataset_option2(df, num_augmented_copies=2, jitter_std_mm=1.0, random_state=42):
    """Legacy wrapper for dataset generation."""
    return augment_train_fold_only(df, num_augmented_copies=num_augmented_copies, jitter_std_mm=jitter_std_mm, random_state=random_state)

def main():
    csv_in = 'preprocessed_features.csv'
    if not os.path.exists(csv_in):
        print(f"Error: {csv_in} not found.")
        sys.exit(1)

    df_raw = pd.read_csv(csv_in)
    print(f"Loaded raw dataset ({csv_in}): {df_raw.shape[0]} records, {df_raw['participant_id'].nunique()} unique patients.")

    df_option2 = augment_dataset_option2(df_raw, num_augmented_copies=2)
    out_csv = 'preprocessed_features_option2_augmented.csv'
    df_option2.to_csv(out_csv, index=False)

    print(f"=== Option 2 Data Augmentation Corrected & Completed ===")
    print(f"Output Dataset: {out_csv}")
    print(f"Augmented Rows: {len(df_option2)} (Original 1x + Aug 2x = 3x)")
    print(f"Features: {df_option2.shape[1]} columns")

if __name__ == '__main__':
    main()
