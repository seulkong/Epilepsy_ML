#!/usr/bin/env python3
"""
Step 3 - Extract SSL embeddings for every ds004100 seizure record and attach them
to the existing feature table by (participant_id, run_id).

For each record listed in preprocessed_features.csv:
  1. Load the cached ictal EDF and the matching channels/events TSVs (.cache_ds004100).
  2. Keep iEEG contacts (type ECOG/SEEG; EKG/ECG/EMG/reference channels dropped).
  3. Crop the ictal window [sz onset, sz offset] - the same window used for the
     trajectory features in pipeline.py.
  4. Resample to 256 Hz, band-pass 1-100 Hz, cut 4-s windows (2-s stride, <=60 per channel),
     per-window z-score, reject artefact windows (ssl_common.make_windows).
  5. Encode each window with the frozen encoder -> 128-d; average over windows to get
     one embedding per channel.
  6. Pool channels into two record-level vectors:
        ssl_soz_*  : mean over SOZ-annotated contacts (status_description contains 'soz')
        ssl_all_*  : mean over all retained contacts
Outputs (per encoder):
  ssl/features/ssl_embeddings_{tag}.csv   participant_id, run_id, n_channels, n_soz,
                                          n_windows, ssl_soz_0..127, ssl_all_0..127
Usage:
  python ssl/extract_ssl_features.py --encoder ssl/models/ssl_encoder.pt    --tag pretrained
  python ssl/extract_ssl_features.py --encoder ssl/models/random_encoder.pt --tag random
"""
import os
import re
import glob
import argparse
import numpy as np
import pandas as pd
import torch
import mne

import ssl_common as C

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, '.cache_ds004100')
OUT = os.path.join(HERE, 'features')
EXCLUDE = re.compile(r'EKG|ECG|EMG|EOG|REF|DC\d|TRIG|PHOTIC', re.IGNORECASE)
MAX_WIN_PER_CH = 60
STRIDE_SEC = 2.0


def norm(name):
    s = re.sub(r'^(EEG|iEEG)\s+', '', str(name).strip(), flags=re.IGNORECASE)
    s = re.sub(r'-Ref$', '', s, flags=re.IGNORECASE)
    return re.sub(r'\s+', '', s).upper()


def find_files(sub, run):
    hits = glob.glob(os.path.join(CACHE, f'ds004100_{sub}_*task-ictal*_{run}_ieeg.edf'))
    if len(hits) != 1:
        raise FileNotFoundError(f'{sub} {run}: {len(hits)} EDF matches')
    edf = hits[0]
    return edf, edf.replace('_ieeg.edf', '_channels.tsv'), edf.replace('_ieeg.edf', '_events.tsv')


def ictal_window(evt_path):
    """Same rule as pipeline.parse_events: first 'onset' row, first 'offset' row."""
    ev = pd.read_csv(evt_path, sep='\t')
    tt = ev['trial_type'].astype(str)
    on = ev.loc[tt.str.contains('onset', case=False), 'onset']
    off = ev.loc[tt.str.contains('offset', case=False), 'onset']
    if len(on) and len(off):
        return float(on.iloc[0]), float(off.iloc[0])
    return float(ev.iloc[0]['onset']), float(ev.iloc[1]['onset'])


@torch.no_grad()
def embed(encoder, w, dev, bs=1024):
    out = []
    for i in range(0, len(w), bs):
        out.append(encoder(torch.from_numpy(w[i:i + bs]).to(dev)).cpu().numpy())
    return np.concatenate(out) if out else np.empty((0, C.EMB_DIM), np.float32)


def process_record(encoder, dev, sub, run):
    edf, chan_tsv, evt_tsv = find_files(sub, run)
    ch = pd.read_csv(chan_tsv, sep='\t')
    ch = ch[ch['type'].astype(str).str.upper().isin(['ECOG', 'SEEG'])]
    # apply exclusion to the normalised name (raw names end in '-Ref' for some patients)
    ch = ch[~ch['name'].map(norm).str.contains(EXCLUDE)]
    is_soz = dict(zip(ch['name'].map(norm),
                      ch['status_description'].astype(str).str.contains('soz', case=False)))

    t_on, t_off = ictal_window(evt_tsv)
    raw = mne.io.read_raw_edf(edf, preload=False, verbose=False)
    keep = [c for c in raw.ch_names if norm(c) in is_soz]
    if len(keep) < 1:
        raise ValueError('no iEEG channels matched channels.tsv')
    raw.pick(keep)
    raw.crop(tmin=max(0.0, t_on), tmax=min(t_off, raw.times[-1]))
    x = raw.get_data().astype(np.float32)                       # (Ch, T)
    x = C.bandpass(C.resample_to_target(x, raw.info['sfreq']))
    w, ch_idx = C.make_windows(x, stride_sec=STRIDE_SEC, max_windows=MAX_WIN_PER_CH)
    if len(w) == 0:
        raise ValueError('ictal window shorter than 4 s or all windows rejected')

    z = embed(encoder, w, dev)                                  # (N, 128)
    chans = np.unique(ch_idx)
    ch_emb = np.stack([z[ch_idx == c].mean(0) for c in chans])  # (Ch_kept, 128)
    soz_mask = np.array([is_soz[norm(keep[c])] for c in chans])
    soz_emb = ch_emb[soz_mask].mean(0) if soz_mask.any() else np.full(C.EMB_DIM, np.nan)

    rec = dict(participant_id=sub, run_id=run, n_channels=int(len(chans)),
               n_soz=int(soz_mask.sum()), n_windows=int(len(w)),
               ictal_sec=round(t_off - t_on, 2))
    rec.update({f'ssl_soz_{i}': float(v) for i, v in enumerate(soz_emb)})
    rec.update({f'ssl_all_{i}': float(v) for i, v in enumerate(ch_emb.mean(0))})
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--encoder', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--features', default=os.path.join(ROOT, 'preprocessed_features.csv'))
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    dev = C.get_device()
    enc = C.Encoder().to(dev)
    enc.load_state_dict(torch.load(args.encoder, map_location=dev))
    enc.eval()

    base = pd.read_csv(args.features)
    recs, errs = [], []
    for i, (sub, run) in enumerate(base[['participant_id', 'run_id']].itertuples(index=False), 1):
        try:
            r = process_record(enc, dev, sub, run)
            recs.append(r)
            print(f'[{i}/{len(base)}] {sub} {run}: ch={r["n_channels"]} soz={r["n_soz"]} win={r["n_windows"]}',
                  flush=True)
        except Exception as e:
            errs.append(f'{sub}\t{run}\t{e}')
            print(f'[{i}/{len(base)}] {sub} {run}: SKIP ({e})', flush=True)

    out_csv = os.path.join(OUT, f'ssl_embeddings_{args.tag}.csv')
    pd.DataFrame(recs).to_csv(out_csv, index=False)
    with open(os.path.join(OUT, f'extract_errors_{args.tag}.log'), 'w') as f:
        f.write('\n'.join(errs) + '\n')
    print(f'saved {len(recs)} records -> {out_csv}  (skipped {len(errs)})')


if __name__ == '__main__':
    main()
