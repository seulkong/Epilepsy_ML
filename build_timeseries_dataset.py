#!/usr/bin/env python3
"""
Time-Series 3D Trajectory Dataset Extraction Pipeline
------------------------------------------------------
Extracts time-series sequences of 3D spatial coordinates and kinematics (x, y, z, dist_resect, velocity, inside_mask)
for each seizure run, alongside patient-level clinical metadata.
Outputs: timeseries_dataset.npz
"""

import os
import re
import json
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

import pipeline

print("=== Starting Multi-Threaded Time-Series 3D Trajectory Dataset Extraction ===")

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

print(f"Submitting {len(tasks)} parallel tasks to extract 3D spatial time-series sequences...")

MAX_SEQ_LEN = 60  # Uniform sequence length for time-series models (30 seconds at 0.5s step)

def extract_single_timeseries(item):
    sub_id, run_id, part_row, evt_key, edf_key, chan_key, elec_key = item
    if not elec_key:
        return None, f"[SKIP] {sub_id} ({run_id}): Missing electrodes"

    try:
        meta = pipeline.parse_electrodes_and_channels(elec_key, chan_key)
        t_on, t_off = pipeline.parse_events(evt_key)
        edf_path = pipeline.fetch_file(edf_key)

        import mne
        raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)
        df_merged = meta['merged']
        c_resect = meta['c_resect']
        r_resect = meta['r_resect']

        edf_ch_map = {}
        for ch in raw.ch_names:
            norm_c = pipeline.normalize_name(ch)
            match = df_merged[df_merged['norm_name'] == norm_c]
            if not match.empty:
                row = match.iloc[0]
                edf_ch_map[ch] = np.array([row['x'], row['y'], row['z']])

        if len(edf_ch_map) < 3:
            return None, f"[SKIP] {sub_id} ({run_id}): <3 channels"

        matched_chs = list(edf_ch_map.keys())
        coords_matrix = np.array([edf_ch_map[ch] for ch in matched_chs])

        sfreq = raw.info['sfreq']
        start_sample = int(t_on * sfreq)
        stop_sample = int(min(t_off, t_on + 30.0) * sfreq)
        data, _ = raw[matched_chs, start_sample:stop_sample]

        win_samples = int(1.0 * sfreq)
        step_samples = int(0.5 * sfreq)
        n_samples = data.shape[1]

        if n_samples < win_samples:
            win_samples = n_samples
            step_samples = max(1, n_samples // 2)

        seq = []
        for s in range(0, n_samples - win_samples + 1, step_samples):
            win_data = data[:, s:s + win_samples]
            rms_power = np.sqrt(np.mean(win_data ** 2, axis=1))
            p_sum = np.sum(rms_power**2)
            if p_sum == 0:
                w = np.ones(len(matched_chs)) / len(matched_chs)
            else:
                w = (rms_power**2) / p_sum

            centroid_t = np.sum(coords_matrix * w[:, np.newaxis], axis=0)
            dist_t = np.linalg.norm(centroid_t - c_resect)
            in_mask_t = 1.0 if dist_t <= r_resect else 0.0

            seq.append([centroid_t[0], centroid_t[1], centroid_t[2], dist_t, in_mask_t])

        seq = np.array(seq, dtype=np.float32)
        if len(seq) > 1:
            vel = np.zeros((len(seq), 1), dtype=np.float32)
            vel[1:] = np.linalg.norm(np.diff(seq[:, :3], axis=0), axis=1, keepdims=True) / 0.5
        else:
            vel = np.zeros((len(seq), 1), dtype=np.float32)

        # 6-dimensional time-series vector per step: [x, y, z, dist_resect, in_mask, velocity]
        seq_full = np.hstack([seq, vel])

        # Zero-pad or truncate to MAX_SEQ_LEN
        if len(seq_full) < MAX_SEQ_LEN:
            pad_len = MAX_SEQ_LEN - len(seq_full)
            seq_full = np.pad(seq_full, ((0, pad_len), (0, 0)), mode='constant', constant_values=0.0)
        else:
            seq_full = seq_full[:MAX_SEQ_LEN]

        # Clinical metadata 9-dim vector
        clin = np.array([
            float(part_row['age']) if not pd.isna(part_row['age']) else 0.0,
            float(part_row['age_onset']) if not pd.isna(part_row['age_onset']) else 0.0,
            int(part_row['sex_encoded']),
            int(part_row['therapy_encoded']),
            int(part_row['implant_encoded']),
            int(part_row['lesion_status_encoded']),
            meta['soz_count'],
            meta['resect_count'],
            meta['initial_soz_resect_dist']
        ], dtype=np.float32)

        res = {
            'participant_id': sub_id,
            'run_id': run_id,
            'outcome': int(part_row['outcome_binary']),
            'seq': seq_full,
            'clin': clin
        }
        return res, None
    except Exception as err:
        return None, f"[SKIP] {sub_id} ({run_id}): {err}"

records = []
with ThreadPoolExecutor(max_workers=16) as executor:
    futures = [executor.submit(extract_single_timeseries, item) for item in tasks]
    for future in as_completed(futures):
        rec, err = future.result()
        if rec:
            records.append(rec)

X_seq = np.array([r['seq'] for r in records], dtype=np.float32)
X_clin = np.array([r['clin'] for r in records], dtype=np.float32)
y = np.array([r['outcome'] for r in records], dtype=np.int64)
groups = np.array([r['participant_id'] for r in records])

np.savez_compressed(
    'timeseries_dataset.npz',
    X_seq=X_seq,
    X_clin=X_clin,
    y=y,
    groups=groups
)

print("=== TIME-SERIES EXTRACTION COMPLETED SUCCESSFULLY ===")
print(f"Extracted {len(records)} 3D trajectory sequences.")
print(f"Shape of X_seq: {X_seq.shape} (Batch, Time_Steps, Features_per_step)")
print(f"Shape of X_clin: {X_clin.shape} (Batch, Clinical_Features)")
print("Saved dataset to timeseries_dataset.npz")
