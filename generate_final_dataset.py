#!/usr/bin/env python3
import pipeline
import pandas as pd

print("Starting feature dataset generation...")
df_part = pipeline.load_participants()

with open('s3_keys.json') as f:
    keys = pipeline.json.load(f)

elec_keys = [k for k in keys if k.endswith('_electrodes.tsv')]
sub_to_elec = {pipeline.re.search(r'sub-HUP\d+', ek).group(0): ek for ek in elec_keys if pipeline.re.search(r'sub-HUP\d+', ek)}
ictal_event_keys = [k for k in keys if 'task-ictal' in k and k.endswith('_events.tsv')]
valid_sub_ids = set(df_part['participant_id'])

records = []
skipped_log = []

for evt_key in ictal_event_keys:
    fname = evt_key.split('/')[-1]
    sub_m = pipeline.re.search(r'sub-HUP\d+', fname)
    run_m = pipeline.re.search(r'run-(\d+)', fname)
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
        skipped_log.append(f"[SKIP] {sub_id} ({run_id}): Missing electrodes.tsv key")
        continue

    try:
        meta = pipeline.parse_electrodes_and_channels(elec_key, chan_key)
        t_on, t_off = pipeline.parse_events(evt_key)
        feats = pipeline.extract_trajectory_and_features(edf_key, meta, t_on, t_off)

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
            'initial_soz_resect_dist': meta['initial_soz_resect_dist'],
            'min_dist_to_resect': feats['min_dist_to_resect'],
            'mean_dist_to_resect': feats['mean_dist_to_resect'],
            'residence_ratio': feats['residence_ratio'],
            'velocity_mean': feats['velocity_mean'],
            'velocity_max': feats['velocity_max'],
            'trajectory_dispersion': feats['trajectory_dispersion']
        }
        records.append(rec)
    except Exception as err:
        skipped_log.append(f"[SKIP] {sub_id} ({run_id}): {err}")

df = pd.DataFrame(records)
df.to_csv('preprocessed_features.csv', index=False)

with open('preprocessing_error.log', 'w') as f_err:
    f_err.write('\n'.join(skipped_log) + '\n')

print(f"SUCCESSFULLY SAVED preprocessed_features.csv: {df.shape[0]} rows, {df.shape[1]} columns.")
