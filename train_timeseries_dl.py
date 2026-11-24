#!/usr/bin/env python3
"""
Time-Series Deep Learning Model Training & Evaluation Pipeline
--------------------------------------------------------------
Implements PyTorch-based Time-Series Deep Learning Architectures:
  1. BiLSTM Classifier (Bidirectional Long Short-Term Memory)
  2. GRU Attention Classifier (Gated Recurrent Unit with Temporal Attention)
  3. Conv1D-LSTM Classifier (1D Temporal Convolution + LSTM)

Applies Patient-Level 80:20 Split (GroupShuffleSplit) & 5-Fold Group K-Fold CV.
Outputs: timeseries_dl_model_performance.csv
"""

import os
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from sklearn.model_selection import GroupShuffleSplit, GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler

# Set PyTorch Random Seed
torch.manual_seed(42)
np.random.seed(42)

# ==============================================================================
# PyTorch Time-Series Deep Learning Model Architectures
# ==============================================================================

class BiLSTMClassifier(nn.Module):
    """Bidirectional LSTM Classifier processing 3D Trajectory Time-Series + Clinical Features"""
    def __init__(self, seq_in_dim=6, clin_in_dim=9, hidden_dim=64, num_layers=2):
        super(BiLSTMClassifier, self).__init__()
        self.lstm = nn.LSTM(
            input_size=seq_in_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True
        )
        self.fc_seq = nn.Linear(hidden_dim * 2, 32)
        self.fc_clin = nn.Linear(clin_in_dim, 16)
        self.classifier = nn.Sequential(
            nn.Linear(32 + 16, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1)
        )

    def forward(self, x_seq, x_clin):
        lstm_out, (h_n, c_n) = self.lstm(x_seq)
        # Global average pooling over time dimension
        out_seq = torch.mean(lstm_out, dim=1)
        out_seq = nn.functional.relu(self.fc_seq(out_seq))
        out_clin = nn.functional.relu(self.fc_clin(x_clin))
        feat_cat = torch.cat([out_seq, out_clin], dim=1)
        logits = self.classifier(feat_cat)
        return torch.sigmoid(logits)


class GRUAttentionClassifier(nn.Module):
    """GRU Network with Temporal Attention Mechanism for 3D Trajectory Sequences"""
    def __init__(self, seq_in_dim=6, clin_in_dim=9, hidden_dim=64):
        super(GRUAttentionClassifier, self).__init__()
        self.gru = nn.GRU(
            input_size=seq_in_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )
        self.attn_w = nn.Linear(hidden_dim * 2, 1)
        self.fc_clin = nn.Linear(clin_in_dim, 16)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2 + 16, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1)
        )

    def forward(self, x_seq, x_clin):
        gru_out, _ = self.gru(x_seq)  # (Batch, Seq_Len, Hidden*2)
        attn_scores = torch.tanh(self.attn_w(gru_out))  # (Batch, Seq_Len, 1)
        attn_weights = torch.softmax(attn_scores, dim=1)
        context_vec = torch.sum(gru_out * attn_weights, dim=1)  # (Batch, Hidden*2)

        out_clin = nn.functional.relu(self.fc_clin(x_clin))
        feat_cat = torch.cat([context_vec, out_clin], dim=1)
        logits = self.classifier(feat_cat)
        return torch.sigmoid(logits)


class Conv1D_LSTMClassifier(nn.Module):
    """1D Temporal Convolution + LSTM Hybrid Architecture for 3D Trajectories"""
    def __init__(self, seq_in_dim=6, clin_in_dim=9, hidden_dim=64):
        super(Conv1D_LSTMClassifier, self).__init__()
        self.conv1d = nn.Sequential(
            nn.Conv1d(in_channels=seq_in_dim, out_channels=32, kernel_size=3, padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(kernel_size=2)
        )
        self.lstm = nn.LSTM(input_size=32, hidden_size=hidden_dim, batch_first=True, bidirectional=True)
        self.fc_clin = nn.Linear(clin_in_dim, 16)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2 + 16, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1)
        )

    def forward(self, x_seq, x_clin):
        # x_seq shape: (Batch, Seq_Len, Features) -> transpose for Conv1D: (Batch, Features, Seq_Len)
        x_conv = x_seq.transpose(1, 2)
        c_out = self.conv1d(x_conv)  # (Batch, 32, Reduced_Seq_Len)
        c_out = c_out.transpose(1, 2)  # (Batch, Reduced_Seq_Len, 32)

        l_out, _ = self.lstm(c_out)
        out_seq = torch.mean(l_out, dim=1)

        out_clin = nn.functional.relu(self.fc_clin(x_clin))
        feat_cat = torch.cat([out_seq, out_clin], dim=1)
        logits = self.classifier(feat_cat)
        return torch.sigmoid(logits)


def train_single_model(model_cls, X_seq_tr, X_clin_tr, y_tr, X_seq_te, X_clin_te, epochs=80, lr=0.001):
    """Trains a PyTorch model and evaluates probabilities on test set."""
    model = model_cls()
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.BCELoss()

    # Scaling clinical features
    scaler = StandardScaler()
    X_clin_tr_s = scaler.fit_transform(X_clin_tr)
    X_clin_te_s = scaler.transform(X_clin_te)

    # Standardize time-series 3D coordinates per feature dimension
    seq_shape = X_seq_tr.shape
    seq_reshaped = X_seq_tr.reshape(-1, seq_shape[2])
    seq_scaler = StandardScaler()
    seq_reshaped_s = seq_scaler.fit_transform(seq_reshaped)
    X_seq_tr_s = seq_reshaped_s.reshape(seq_shape)

    te_shape = X_seq_te.shape
    te_reshaped = X_seq_te.reshape(-1, te_shape[2])
    te_reshaped_s = seq_scaler.transform(te_reshaped)
    X_seq_te_s = te_reshaped_s.reshape(te_shape)

    t_seq_tr = torch.tensor(X_seq_tr_s, dtype=torch.float32)
    t_clin_tr = torch.tensor(X_clin_tr_s, dtype=torch.float32)
    t_y_tr = torch.tensor(y_tr, dtype=torch.float32).unsqueeze(1)

    t_seq_te = torch.tensor(X_seq_te_s, dtype=torch.float32)
    t_clin_te = torch.tensor(X_clin_te_s, dtype=torch.float32)

    dataset = TensorDataset(t_seq_tr, t_clin_tr, t_y_tr)
    loader = DataLoader(dataset, batch_size=16, shuffle=True)

    model.train()
    for epoch in range(epochs):
        for b_seq, b_clin, b_y in loader:
            optimizer.zero_grad()
            preds = model(b_seq, b_clin)
            loss = criterion(preds, b_y)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        test_probs = model(t_seq_te, t_clin_te).squeeze(1).numpy()

    return test_probs


def main():
    npz_path = 'timeseries_dataset.npz'
    if not os.path.exists(npz_path):
        print(f"Error: Dataset {npz_path} not found. Run build_timeseries_dataset.py first.")
        sys.exit(1)

    data = np.load(npz_path)
    X_seq = data['X_seq']
    X_clin = data['X_clin']
    y = data['y']
    groups = data['groups']

    print("=== Loading Time-Series 3D Trajectory Dataset ===")
    print(f"Total Sessions: {len(y)}, Unique Patients: {len(np.unique(groups))}")
    print(f"3D Trajectory Sequence Shape: {X_seq.shape}")

    # Patient-Level 80:20 Hold-out Split
    gss = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
    train_idx, test_holdout_idx = next(gss.split(X_seq, y, groups))

    X_seq_tr_full, X_seq_te_holdout = X_seq[train_idx], X_seq[test_holdout_idx]
    X_clin_tr_full, X_clin_te_holdout = X_clin[train_idx], X_clin[test_holdout_idx]
    y_tr_full, y_te_holdout = y[train_idx], y[test_holdout_idx]
    groups_tr_full = groups[train_idx]
    groups_te_holdout = groups[test_holdout_idx]

    n_train_pts = len(np.unique(groups_tr_full))
    n_test_pts = len(np.unique(groups_te_holdout))

    print(f"\n[Patient-Level 80:20 Split Completed]")
    print(f"  • Train Set: {len(X_seq_tr_full)} sessions ({n_train_pts} patients)")
    print(f"  • Hold-out Test Set: {len(X_seq_te_holdout)} sessions ({n_test_pts} patients)\n")

    models_to_evaluate = {
        'BiLSTM (시간 궤적 딥러닝)': BiLSTMClassifier,
        'GRU-Attention (어텐션 시계열 딥러닝)': GRUAttentionClassifier,
        'Conv1D-LSTM (1D-합성곱 시간 딥러닝)': Conv1D_LSTMClassifier
    }

    gkf = GroupKFold(n_splits=5)
    results = []

    for name, model_cls in models_to_evaluate.items():
        print(f" -> Training {name} with 5-Fold Group K-Fold CV & Hold-out Test Evaluation...")

        # 5-Fold Group CV on Train Set
        cv_aucs = []
        for cv_tr_idx, cv_val_idx in gkf.split(X_seq_tr_full, y_tr_full, groups_tr_full):
            cv_seq_tr, cv_seq_val = X_seq_tr_full[cv_tr_idx], X_seq_tr_full[cv_val_idx]
            cv_clin_tr, cv_clin_val = X_clin_tr_full[cv_tr_idx], X_clin_tr_full[cv_val_idx]
            cv_y_tr, cv_y_val = y_tr_full[cv_tr_idx], y_tr_full[cv_val_idx]

            val_probs = train_single_model(model_cls, cv_seq_tr, cv_clin_tr, cv_y_tr, cv_seq_val, cv_clin_val, epochs=50)
            cv_aucs.append(roc_auc_score(cv_y_val, val_probs))

        # Evaluate on Final Hold-out Test Set
        holdout_probs = train_single_model(model_cls, X_seq_tr_full, X_clin_tr_full, y_tr_full, X_seq_te_holdout, X_clin_te_holdout, epochs=80)
        holdout_preds = (holdout_probs >= 0.5).astype(int)

        roc_auc = roc_auc_score(y_te_holdout, holdout_probs)
        pr_auc = average_precision_score(y_te_holdout, holdout_probs)
        acc = accuracy_score(y_te_holdout, holdout_preds)
        f1 = f1_score(y_te_holdout, holdout_preds)

        results.append({
            '시계열 딥러닝 모델 (Model)': name,
            'Train CV ROC-AUC': round(np.mean(cv_aucs), 4),
            'Test Hold-out ROC-AUC': round(roc_auc, 4),
            'Test Hold-out PR-AUC': round(pr_auc, 4),
            'Test 정확도 (Accuracy)': round(acc, 4),
            'Test F1-Score': round(f1, 4)
        })

    df_res = pd.DataFrame(results).sort_values(by='Test Hold-out PR-AUC', ascending=False)
    print("\n" + "=" * 80)
    print("=== TIME-SERIES DEEP LEARNING MODEL PERFORMANCE (Hold-out Test Evaluation) ===")
    print("=" * 80)
    print(df_res.to_string(index=False))
    print("=" * 80 + "\n")

    df_res.to_csv('timeseries_dl_model_performance.csv', index=False)
    print("Saved results to timeseries_dl_model_performance.csv")

if __name__ == '__main__':
    main()
