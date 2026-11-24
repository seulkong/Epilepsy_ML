#!/usr/bin/env python3
"""
OpenNeuro ds004100 iEEG Preprocessing & Spatial Feature Extraction Pipeline
-------------------------------------------------------------------------
Author: Bioinformatics & Signal Processing Data Engineer
Task: Transform raw iEEG files, electrode 3D coordinates (MNI152/fsaverage), 
      and resection/SOZ metadata into preprocessed_features.csv.
"""

import os
import re
import io
import json
import logging
import urllib.request
import numpy as np
import pandas as pd
import mne

# Setup logging
logging.basicConfig(
    filename='preprocessing_error.log',
    filemode='w',
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)

CACHE_DIR = os.path.join(os.getcwd(), '.cache_ds004100')
os.makedirs(CACHE_DIR, exist_ok=True)

S3_BASE_URL = 'https://s3.amazonaws.com/openneuro.org'

def fetch_file(relative_key):
    """Fetch file from S3 and cache locally."""
    clean_key = relative_key.lstrip('/')
    local_path = os.path.join(CACHE_DIR, clean_key.replace('/', '_'))
    
    # Check if cached file is valid (not empty or error HTML)
    if os.path.exists(local_path) and os.path.getsize(local_path) > 50:
        with open(local_path, 'rb') as f:
            header = f.read(20)
            if not header.startswith(b'<!DOCTYPE') and not header.startswith(b'<Error'):
                return local_path

    url = f"{S3_BASE_URL}/{clean_key}"
    try:
        urllib.request.urlretrieve(url, local_path)
        return local_path
    except Exception as e:
        if os.path.exists(local_path):
            os.remove(local_path)
        raise RuntimeError(f"Failed to fetch {url}: {e}")

def normalize_name(name):
    """Normalize channel and electrode names for exact string matching."""
    if not isinstance(name, str) or pd.isna(name):
        return ''
    s = str(name).strip()
    s = re.sub(r'^EEG\s+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'^iEEG\s+', '', s, flags=re.IGNORECASE)
    s = re.sub(r'-Ref$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', '', s)
    return s.upper()

def load_participants():
    """Load participants.tsv, filter outcome (S/F), and encode clinical features."""
    p_path = fetch_file('ds004100/participants.tsv')
    df = pd.read_csv(p_path, sep='\t')

    # Filter outcome S or F
    df = df[df['outcome'].isin(['S', 'F'])].copy()

    # Label Y: S -> 1, F -> 0
    df['outcome_binary'] = df['outcome'].map({'S': 1, 'F': 0})

    # Encode categorical features
    sex_map = {'F': 0, 'M': 1}
    therapy_map = {'ABLATION': 0, 'RESECTION': 1}
    implant_map = {'ECOG': 0, 'SEEG': 1}
    lesion_map = {'NON-LESIONAL': 0, 'LESIONAL': 1}

    df['sex_encoded'] = df['sex'].map(sex_map).fillna(-1).astype(int)
    df['therapy_encoded'] = df['therapy'].map(therapy_map).fillna(-1).astype(int)
    df['implant_encoded'] = df['implant'].map(implant_map).fillna(-1).astype(int)
    df['lesion_status_encoded'] = df['lesion_status'].map(lesion_map).fillna(-1).astype(int)

    # Convert numeric fields
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    df['age_onset'] = pd.to_numeric(df['age_onset'], errors='coerce')

    return df

def parse_electrodes_and_channels(elec_key, chan_key):
    """Merge electrodes.tsv and channels.tsv to compute SOZ and Resection 3D centroids."""
    elec_path = fetch_file(elec_key)
    chan_path = fetch_file(chan_key)

    df_elec = pd.read_csv(elec_path, sep='\t')
    df_chan = pd.read_csv(chan_path, sep='\t')

    df_elec['norm_name'] = df_elec['name'].apply(normalize_name)
    df_chan['norm_name'] = df_chan['name'].apply(normalize_name)

    # Ensure numeric coordinates
    df_elec['x'] = pd.to_numeric(df_elec['x'], errors='coerce')
    df_elec['y'] = pd.to_numeric(df_elec['y'], errors='coerce')
    df_elec['z'] = pd.to_numeric(df_elec['z'], errors='coerce')

    # Drop NaNs in coordinates
    df_elec_valid = df_elec.dropna(subset=['x', 'y', 'z']).copy()

    if df_elec_valid.empty:
        raise ValueError("No valid 3D coordinates in electrodes.tsv")

    # Merge by norm_name
    merged = pd.merge(df_chan, df_elec_valid, on='norm_name', suffixes=('_chan', '_elec'))

    if merged.empty:
        raise ValueError("No matching channel names between channels.tsv and electrodes.tsv")

    if 'status_description' not in merged.columns:
        raise ValueError("status_description missing in channels.tsv")

    # Identify SOZ and Resection channels
    merged['is_soz'] = merged['status_description'].astype(str).str.contains('soz', case=False, na=False)
    merged['is_resect'] = merged['status_description'].astype(str).str.contains('resect', case=False, na=False)

    df_soz = merged[merged['is_soz']]
    df_resect = merged[merged['is_resect']]

    soz_count = len(df_soz)
    resect_count = len(df_resect)

    if soz_count == 0 or resect_count == 0:
        raise ValueError(f"Insufficient annotations: soz_count={soz_count}, resect_count={resect_count}")

    # Compute 3D centroids
    c_soz = np.array([df_soz['x'].mean(), df_soz['y'].mean(), df_soz['z'].mean()])
    c_resect = np.array([df_resect['x'].mean(), df_resect['y'].mean(), df_resect['z'].mean()])

    # Initial distance
    initial_dist = float(np.linalg.norm(c_soz - c_resect))

    # Bounding radius for resection zone
    resect_coords = df_resect[['x', 'y', 'z']].values
    resect_dists = np.linalg.norm(resect_coords - c_resect, axis=1)
    r_resect = float(np.max(resect_dists)) if len(resect_dists) > 0 else 10.0

    return {
        'merged': merged,
        'c_soz': c_soz,
        'c_resect': c_resect,
        'r_resect': r_resect,
        'soz_count': soz_count,
        'resect_count': resect_count,
        'initial_soz_resect_dist': initial_dist
    }

def parse_events(events_key):
    """Extract seizure onset and offset timestamps from events.tsv."""
    evt_path = fetch_file(events_key)
    df_evt = pd.read_csv(evt_path, sep='\t')

    onset_val = None
    offset_val = None

    for col in df_evt.columns:
        col_str = df_evt[col].astype(str)

        on_rows = df_evt[col_str.str.contains('sz onset|onset', case=False, na=False)]
        if not on_rows.empty and onset_val is None:
            onset_val = float(on_rows.iloc[0]['onset'])

        off_rows = df_evt[col_str.str.contains('sz offset|offset', case=False, na=False)]
        if not off_rows.empty and offset_val is None:
            offset_val = float(off_rows.iloc[0]['onset'])

    if onset_val is None or offset_val is None:
        if len(df_evt) >= 2 and 'onset' in df_evt.columns:
            onset_val = float(df_evt.iloc[0]['onset'])
            offset_val = float(df_evt.iloc[1]['onset'])
        else:
            raise ValueError("Missing 'sz onset' or 'sz offset' event annotations")

    if offset_val <= onset_val:
        raise ValueError(f"Invalid ictal window: onset={onset_val}, offset={offset_val}")

    return onset_val, offset_val

def extract_trajectory_and_features(edf_key, metadata, t_onset, t_offset, max_duration_sec=None, offset_start_sec=0.0):
    """Slice ictal raw iEEG signal, reconstruct 3D spatial trajectory, and compute kinematic/geometric metrics."""
    actual_start = t_onset + offset_start_sec
    if max_duration_sec is not None:
        actual_stop = min(t_offset, actual_start + max_duration_sec)
    else:
        actual_stop = t_offset

    if actual_stop <= actual_start:
        actual_stop = actual_start + 1.0

    edf_path = fetch_file(edf_key)
    raw = mne.io.read_raw_edf(edf_path, preload=True, verbose=False)

    df_merged = metadata['merged']
    c_soz = metadata['c_soz']
    c_resect = metadata['c_resect']
    r_resect = metadata['r_resect']

    # Map EDF channels to matched 3D coordinates
    edf_ch_map = {}
    for ch in raw.ch_names:
        norm_c = normalize_name(ch)
        match = df_merged[df_merged['norm_name'] == norm_c]
        if not match.empty:
            row = match.iloc[0]
            edf_ch_map[ch] = np.array([row['x'], row['y'], row['z']])

    if len(edf_ch_map) < 3:
        raise ValueError(f"Only {len(edf_ch_map)} matched electrode coordinates in EDF")

    matched_chs = list(edf_ch_map.keys())
    coords_matrix = np.array([edf_ch_map[ch] for ch in matched_chs])  # Shape: (N, 3)

    # Slice ictal signal
    sfreq = raw.info['sfreq']
    start_sample = int(actual_start * sfreq)
    stop_sample = int(actual_stop * sfreq)

    data, times = raw[matched_chs, start_sample:stop_sample]  # Shape: (N, T)

    # Sliding window parameters
    win_sec = 1.0
    step_sec = 0.5
    win_samples = int(win_sec * sfreq)
    step_samples = int(step_sec * sfreq)
    n_samples = data.shape[1]

    if n_samples < win_samples:
        win_samples = n_samples
        step_samples = max(1, n_samples // 2)

    trajectory = []

    for s in range(0, n_samples - win_samples + 1, step_samples):
        win_data = data[:, s:s + win_samples]  # Shape: (N, win_samples)
        # Compute RMS signal power per channel
        rms_power = np.sqrt(np.mean(win_data ** 2, axis=1))  # Shape: (N,)

        # Prevent divide-by-zero
        power_sum = np.sum(rms_power**2)
        if power_sum == 0:
            weights = np.ones(len(matched_chs)) / len(matched_chs)
        else:
            weights = (rms_power**2) / power_sum

        # Instantaneous 3D power-weighted centroid position
        r_t = np.sum(coords_matrix * weights[:, np.newaxis], axis=0)  # Shape: (3,)
        trajectory.append(r_t)

    trajectory = np.array(trajectory)  # Shape: (K, 3)

    if len(trajectory) == 0:
        raise ValueError("Empty trajectory reconstructed")

    # Feature Derivation
    # 1. Distances to resection center
    dists_to_resect = np.linalg.norm(trajectory - c_resect, axis=1)  # mm
    min_dist_to_resect = float(np.min(dists_to_resect))
    mean_dist_to_resect = float(np.mean(dists_to_resect))

    # 2. Residence ratio (% of frames inside resection volume boundary)
    in_mask_count = np.sum(dists_to_resect <= r_resect)
    residence_ratio = float((in_mask_count / len(trajectory)) * 100.0)

    # 3. Trajectory velocity (mm/s)
    if len(trajectory) > 1:
        frame_diffs = np.linalg.norm(np.diff(trajectory, axis=0), axis=1)  # mm between steps
        velocities = frame_diffs / step_sec  # mm/s
        velocity_mean = float(np.mean(velocities))
        velocity_max = float(np.max(velocities))
    else:
        velocity_mean = 0.0
        velocity_max = 0.0

    # 4. Trajectory dispersion (max distance from initial SOZ point)
    dispersion_dists = np.linalg.norm(trajectory - c_soz, axis=1)
    trajectory_dispersion = float(np.max(dispersion_dists))

    return {
        'min_dist_to_resect': min_dist_to_resect,
        'mean_dist_to_resect': mean_dist_to_resect,
        'residence_ratio': residence_ratio,
        'velocity_mean': velocity_mean,
        'velocity_max': velocity_max,
        'trajectory_dispersion': trajectory_dispersion
    }

def main():
    print("=== Starting ds004100 Feature Extraction Pipeline ===")
    
    # Load S3 keys list
    if not os.path.exists('s3_keys.json'):
        raise FileNotFoundError("s3_keys.json not found. Run key fetching first.")

    with open('s3_keys.json') as f:
        keys = json.load(f)

    # Map sub -> electrodes key
    elec_keys = [k for k in keys if k.endswith('_electrodes.tsv')]
    sub_to_elec = {}
    for ek in elec_keys:
        m = re.search(r'sub-HUP\d+', ek)
        if m:
            sub_to_elec[m.group(0)] = ek

    # Load participants metadata
    df_part = load_participants()
    valid_sub_ids = set(df_part['participant_id'])
    print(f"Loaded {len(df_part)} valid participants with outcome (S/F).")

    # Find all ictal events.tsv keys
    ictal_event_keys = [k for k in keys if 'task-ictal' in k and k.endswith('_events.tsv')]
    print(f"Found {len(ictal_event_keys)} candidate ictal event files.")

    processed_records = []
    skipped_count = 0

    for idx, evt_key in enumerate(ictal_event_keys, 1):
        parts = evt_key.split('/')
        fname = parts[-1]
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

        if not elec_key:
            err_msg = f"{sub_id} ({run_id}): Missing electrodes.tsv key in dataset"
            logging.info(f"[SKIP] {err_msg}")
            skipped_count += 1
            continue

        print(f"[{idx}/{len(ictal_event_keys)}] Processing {sub_id} ({run_id})...")

        try:
            # Step 2: 3D Spatial Zone Centroids
            meta_spatial = parse_electrodes_and_channels(elec_key, chan_key)

            # Step 3: Parse Events & Ictal Window
            t_onset, t_offset = parse_events(evt_key)

            # Step 3 & 4: Trajectory & Kinematic Features
            feats = extract_trajectory_and_features(edf_key, meta_spatial, t_onset, t_offset)

            # Combine all features into single row
            record = {
                'participant_id': sub_id,
                'run_id': run_id,
                'outcome': int(part_row['outcome_binary']),
                'age': float(part_row['age']) if not pd.isna(part_row['age']) else np.nan,
                'age_onset': float(part_row['age_onset']) if not pd.isna(part_row['age_onset']) else np.nan,
                'sex': int(part_row['sex_encoded']),
                'therapy': int(part_row['therapy_encoded']),
                'implant': int(part_row['implant_encoded']),
                'lesion_status': int(part_row['lesion_status_encoded']),
                'soz_count': meta_spatial['soz_count'],
                'resect_count': meta_spatial['resect_count'],
                'initial_soz_resect_dist': meta_spatial['initial_soz_resect_dist'],
                'min_dist_to_resect': feats['min_dist_to_resect'],
                'mean_dist_to_resect': feats['mean_dist_to_resect'],
                'residence_ratio': feats['residence_ratio'],
                'velocity_mean': feats['velocity_mean'],
                'velocity_max': feats['velocity_max'],
                'trajectory_dispersion': feats['trajectory_dispersion']
            }

            processed_records.append(record)
            print(f"  -> SUCCESS! Min dist: {feats['min_dist_to_resect']:.2f}mm, Residence: {feats['residence_ratio']:.1f}%")

        except Exception as err:
            err_msg = f"{sub_id} ({run_id}): {err}"
            logging.info(f"[SKIP] {err_msg}")
            print(f"  -> SKIPPED: {err}")
            skipped_count += 1

    # Consolidate and export
    df_out = pd.DataFrame(processed_records)
    out_csv = 'preprocessed_features.csv'
    df_out.to_csv(out_csv, index=False)

    print("\n==========================================")
    print(f"Pipeline Completed!")
    print(f"Successfully processed records: {len(df_out)}")
    print(f"Skipped runs logged to preprocessing_error.log: {skipped_count}")
    print(f"Saved feature dataset to: {out_csv}")
    print("==========================================")

if __name__ == '__main__':
    main()
