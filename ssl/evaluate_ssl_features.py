#!/usr/bin/env python3
"""
Step 4 - Does adding external-SSL iEEG embeddings improve surgical-outcome prediction?

Protocol
  * Data        : preprocessed_features.csv (ds004100; 203 seizure records, 55 patients)
                  inner-joined with ssl/features/ssl_embeddings_{pretrained,random}.csv
  * Splitting   : StratifiedGroupKFold (5 folds, groups = participant_id), repeated
                  with 10 different shuffling seeds -> no patient ever appears in both
                  train and test of the same fold.
  * Leakage ctl : StandardScaler and PCA (SSL embeddings -> k components) are fit on the
                  training fold only, then applied to the test fold.
  * Conditions  : C0 Baseline           15 trajectory + clinical features
                  C1 Baseline + SSL     + k PCA comps of pretrained SOZ embedding
                  C2 SSL only           k PCA comps of pretrained SOZ embedding
                  C3 Baseline + Random  + k PCA comps of untrained-encoder embedding (control)
  * Models      : L2 logistic regression, random forest (class-balanced)
  * Metrics     : out-of-fold predictions pooled per repeat ->
                  record-level ROC-AUC / PR-AUC / balanced accuracy, and patient-level
                  ROC-AUC (mean predicted probability per patient).
                  Reported as mean +/- SD over the 10 repeats; paired difference vs C0.
Outputs
  ssl/results/ssl_eval_per_repeat.csv, ssl/results/ssl_eval_summary.csv
"""
import os
import argparse
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, balanced_accuracy_score

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FEAT = os.path.join(HERE, 'features')
RES = os.path.join(HERE, 'results')

BASELINE = ['min_dist_to_resect', 'mean_dist_to_resect', 'residence_ratio',
            'velocity_mean', 'velocity_max', 'trajectory_dispersion',
            'age', 'age_onset', 'sex', 'therapy', 'implant', 'lesion_status',
            'soz_count', 'resect_count', 'initial_soz_resect_dist']


def models(seed):
    return {
        'LogReg': LogisticRegression(C=0.5, max_iter=5000, class_weight='balanced'),
        'RandomForest': RandomForestClassifier(n_estimators=300, max_depth=6, min_samples_leaf=3,
                                               class_weight='balanced', random_state=seed, n_jobs=-1),
    }


def fold_matrices(tr, te, base_cols, emb_cols, k):
    """Scale baseline; PCA(k) on embeddings - all fit on training rows only."""
    parts_tr, parts_te = [], []
    if base_cols:
        sc = StandardScaler().fit(tr[base_cols])
        parts_tr.append(sc.transform(tr[base_cols])); parts_te.append(sc.transform(te[base_cols]))
    if emb_cols:
        sc_e = StandardScaler().fit(tr[emb_cols])
        pca = PCA(n_components=k, random_state=0).fit(sc_e.transform(tr[emb_cols]))
        parts_tr.append(pca.transform(sc_e.transform(tr[emb_cols])))
        parts_te.append(pca.transform(sc_e.transform(te[emb_cols])))
    return np.hstack(parts_tr), np.hstack(parts_te)


def run(df, conditions, n_rep, k):
    rows = []
    y = df['outcome'].values
    g = df['participant_id'].values
    for rep in range(n_rep):
        cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=rep)
        splits = list(cv.split(df, y, g))
        for cname, (bcols, ecols) in conditions.items():
            for mname in models(rep):
                oof = np.full(len(df), np.nan)
                for tr_i, te_i in splits:
                    tr, te = df.iloc[tr_i], df.iloc[te_i]
                    Xtr, Xte = fold_matrices(tr, te, bcols, ecols, k)
                    m = models(rep)[mname].fit(Xtr, y[tr_i])
                    oof[te_i] = m.predict_proba(Xte)[:, 1]
                pt = pd.DataFrame({'g': g, 'y': y, 'p': oof}).groupby('g').agg(y=('y', 'first'), p=('p', 'mean'))
                rows.append(dict(
                    repeat=rep, condition=cname, model=mname,
                    rec_roc_auc=roc_auc_score(y, oof),
                    rec_pr_auc=average_precision_score(y, oof),
                    rec_bal_acc=balanced_accuracy_score(y, (oof >= 0.5).astype(int)),
                    pat_roc_auc=roc_auc_score(pt['y'], pt['p']),
                ))
        print(f'repeat {rep + 1}/{n_rep} done', flush=True)
    return pd.DataFrame(rows)


def summarize(per):
    metrics = ['rec_roc_auc', 'rec_pr_auc', 'rec_bal_acc', 'pat_roc_auc']
    out = []
    for (m, c), d in per.groupby(['model', 'condition'], sort=False):
        base = per[(per.model == m) & (per.condition == 'C0 Baseline')].set_index('repeat')
        row = dict(model=m, condition=c)
        for k in metrics:
            row[k] = f"{d[k].mean():.3f} ± {d[k].std(ddof=1):.3f}"
        diff = d.set_index('repeat')['pat_roc_auc'] - base['pat_roc_auc']
        row['Δpat_AUC_vs_C0'] = f"{diff.mean():+.3f} ± {diff.std(ddof=1):.3f}"
        row['repeats_better_than_C0'] = f"{int((diff > 0).sum())}/{len(diff)}"
        out.append(row)
    return pd.DataFrame(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repeats', type=int, default=10)
    ap.add_argument('--k', type=int, default=8, help='PCA components for SSL embeddings')
    ap.add_argument('--pool', default='soz', choices=['soz', 'all'])
    args = ap.parse_args()
    os.makedirs(RES, exist_ok=True)

    base = pd.read_csv(os.path.join(ROOT, 'preprocessed_features.csv'))
    pre_path = os.path.join(FEAT, 'ssl_embeddings_pretrained_shortterm.csv')
    if not os.path.exists(pre_path):
        pre_path = os.path.join(FEAT, 'ssl_embeddings_pretrained.csv')
    pre = pd.read_csv(pre_path)
    rnd = pd.read_csv(os.path.join(FEAT, 'ssl_embeddings_random.csv'))
    pcols = [c for c in pre.columns if c.startswith(f'ssl_{args.pool}_')]
    rnd = rnd.rename(columns={c: 'rnd_' + c for c in pcols})[['participant_id', 'run_id'] + ['rnd_' + c for c in pcols]]
    df = (base.merge(pre[['participant_id', 'run_id'] + pcols], on=['participant_id', 'run_id'])
              .merge(rnd, on=['participant_id', 'run_id']))
    df = df.dropna(subset=BASELINE + pcols + ['outcome']).reset_index(drop=True)
    print(f'analysis set: {len(df)} records / {df.participant_id.nunique()} patients '
          f'(S={df.groupby("participant_id").outcome.first().sum()}) | pool={args.pool} k={args.k}')

    conditions = {
        'C0 Baseline': (BASELINE, []),
        'C1 Baseline + SSL': (BASELINE, pcols),
        'C2 SSL only': ([], pcols),
        'C3 Baseline + Random-init': (BASELINE, ['rnd_' + c for c in pcols]),
    }
    per = run(df, conditions, args.repeats, args.k)
    tag = f'{args.pool}_k{args.k}'
    per.to_csv(os.path.join(RES, f'ssl_eval_per_repeat_{tag}.csv'), index=False)
    summ = summarize(per)
    summ.to_csv(os.path.join(RES, f'ssl_eval_summary_{tag}.csv'), index=False)
    pd.set_option('display.width', 200)
    print(summ.to_string(index=False))


if __name__ == '__main__':
    main()
