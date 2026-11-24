#!/usr/bin/env python3
"""
Step 1 - Build the SSL pretraining corpus from the external SWEC-ETHZ long-term iEEG.

Source  : SWEC-ETHZ iEEG database (Zenodo record 14578383), long-term recordings.
          Only fully downloaded & CRC-verified hourly files are used
          (recovered by ssl/scan_truncated_zip.py):
             ID18_183h.mat, ID18_184h.mat  -> SSL training split
             ID18_186h.mat                 -> SSL validation split (held-out hour)
          Each file: 42 channels x 3,686,400 samples (1 h @ 1024 Hz).
Output  : ssl/data/swec_pretrain_{train,val}.npy  (N, 1024) float16 z-scored windows

No labels and no ds004100 data are used here (the target cohort stays untouched).
"""
import os
import glob
import json
import numpy as np
import scipy.io as sio

import ssl_common as C

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'external_datasets', 'swec_recovered', 'longterm')
OUT = os.path.join(HERE, 'data')
SWEC_FS = 1024.0
VAL_FILES = {'ID18_186h.mat'}
STRIDE_SEC = 4.0   # non-overlapping windows


def process_file(path):
    eeg = sio.loadmat(path)['EEG'].astype(np.float32)  # (42, T)
    assert abs(eeg.shape[1] / 3600.0 - SWEC_FS) < 1, f"unexpected length {eeg.shape}"
    x = C.resample_to_target(eeg, SWEC_FS)
    del eeg
    x = C.bandpass(x)
    w, _ = C.make_windows(x, stride_sec=STRIDE_SEC)
    return w


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC, '*.mat')))
    if not files:
        raise SystemExit(f"No recovered SWEC files in {SRC}. Run scan_truncated_zip.py --extract first.")

    split = {'train': [], 'val': []}
    log = {}
    for p in files:
        name = os.path.basename(p)
        w = process_file(p)
        key = 'val' if name in VAL_FILES else 'train'
        split[key].append(w.astype(np.float16))
        log[name] = {'split': key, 'windows_kept': int(len(w))}
        print(f"{name}: {len(w)} windows -> {key}")

    for k, lst in split.items():
        arr = np.concatenate(lst) if lst else np.empty((0, C.WIN_LEN), np.float16)
        np.save(os.path.join(OUT, f'swec_pretrain_{k}.npy'), arr)
        log[f'n_{k}'] = int(len(arr))
        print(f"saved {k}: {arr.shape}")

    log.update(dict(source_fs=SWEC_FS, target_fs=C.TARGET_FS, win_sec=C.WIN_SEC,
                    stride_sec=STRIDE_SEC, band=C.BAND))
    with open(os.path.join(OUT, 'pretrain_corpus_info.json'), 'w') as f:
        json.dump(log, f, indent=2)


if __name__ == '__main__':
    main()
