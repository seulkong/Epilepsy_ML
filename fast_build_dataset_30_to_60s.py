#!/usr/bin/env python3
"""
Late Seizure Window (30s-60s) Feature Extraction
-------------------------------------------------
Extracts trajectory features for the late seizure window (t_onset + 30.0s to t_onset + 60.0s).
Outputs: preprocessed_features_30_to_60s.csv
"""

import os
import re
import json
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

import pipeline

print("=== Starting Parallel Feature Extraction (Late Window 30s-60s) ===")

df_part = pipeline.load_participants()
with open('s3_keys.json') as f:
    keys = json.load(f)

elec_keys = [k for k in keys if k.endswith('_electrodes.tsv')]
sub_to_elec = {re.search(r'sub-HUP\d+', ek).group(0): ek for ek in elec_keys if re.search(r'sub-HUP\d+', ek)}
ictal_event_keys = [k for k in keys if 'task-ictal' in k and k.endswith('_events.tsv')]
valid_sub_ids = set(df_part['participant_id'])

tasks = []
for evt_key in ictal_event_keys:
    fname = evt_key.split('/')[-1]
    sub_m = re.search(r'sub-HUP\d+', fname)
    run_m = re.search(r'run-(\d+)', fname)
    if not sub_m:
        continue

    sub_id = sub_m.group(0)
    run_id = f"run-{run_m.group(1)}" if run_m else "run-01"

    if sub_id not in valid_sub_ids:
        continue

    part_row = df_part[df_part['participant_id'] == sub_id].iloc[0]
    edf_key = evt_key.replace('_events.tsv', '_ieeg.edf')
    chan_key = evt_key.replace('_events.tsv', '_channels.tsv')
    elec_key = sub_to_elec.get(sub_id)

    tasks.append((sub_id, run_id, part_row, evt_key, edf_key, chan_key, elec_key))

print(f"Submitting {len(tasks)} parallel processing tasks (Late 30s-60s window)...")

records = []
skipped_log = []

def process_single_run_30_to_60s(item):
    sub_id, run_id, part_row, evt_key, edf_key, chan_key, elec_key = item
    if not elec_key:
        return None, f"[SKIP] {sub_id} ({run_id}): Missing electrodes.tsv key"

    try:
        meta = pipeline.parse_electrodes_and_channels(elec_key, chan_key)
        t_on, t_off = pipeline.parse_events(evt_key)
        # Limit window to late 30s-60s interval
        feats = pipeline.extract_trajectory_and_features(
            edf_key, meta, t_on, t_off, max_duration_sec=30.0, offset_start_sec=30.0
        )

        rec = {
            'participant_id': sub_id,
            'run_id': run_id,
            'outcome': int(part_row['outcome_binary']),
            'age': float(part_row['age']) if not pd.isna(part_row['age']) else None,
            'age_onset': float(part_row['age_onset']) if not pd.isna(part_row['age_onset']) else None,
            'sex': int(part_row['sex_encoded']),
            'therapy': int(part_row['therapy_encoded']),
            'implant': int(part_row['implant_encoded']),
            'lesion_status': int(part_row['lesion_status_encoded']),
            'soz_count': meta['soz_count'],
            'resect_count': meta['resect_count'],
            'initial_soz_resect_dist': round(meta['initial_soz_resect_dist'], 4),
            'min_dist_to_resect': round(feats['min_dist_to_resect'], 4),
            'mean_dist_to_resect': round(feats['mean_dist_to_resect'], 4),
            'residence_ratio': round(feats['residence_ratio'], 4),
            'velocity_mean': round(feats['velocity_mean'], 4),
            'velocity_max': round(feats['velocity_max'], 4),
            'trajectory_dispersion': round(feats['trajectory_dispersion'], 4)
        }
        return rec, None
    except Exception as err:
        return None, f"[SKIP] {sub_id} ({run_id}): {err}"

with ThreadPoolExecutor(max_workers=16) as executor:
    futures = [executor.submit(process_single_run_30_to_60s, item) for item in tasks]
    for future in as_completed(futures):
        rec, err = future.result()
        if rec:
            records.append(rec)
        if err:
            skipped_log.append(err)

df_out = pd.DataFrame(records)
df_out.sort_values(by=['participant_id', 'run_id'], inplace=True)
df_out.to_csv('preprocessed_features_30_to_60s.csv', index=False)

print("=== LATE 30s-60s PARALLEL EXTRACTION COMPLETED SUCCESSFULLY ===")
print(f"Total processed feature records: {len(df_out)}")
print(f"Exported file: preprocessed_features_30_to_60s.csv ({os.path.getsize('preprocessed_features_30_to_60s.csv')} bytes)")
