#!/usr/bin/env python3
"""
Sequential Download & On-the-Fly Processing for SWEC-ETHZ Short-term Dataset.
Solves local disk storage constraints by processing patient ZIPs one-by-one
and deleting raw files immediately after feature extraction.

Dataset: BioCAS2018 iEEG Short-term dataset (16 patients, 100 seizures)
Sampling rate: 512 Hz
Signal variable: 'EEG' shape (T, M) -> Transposed to (M, T) for processing
"""

import os
import sys
import shutil
import zipfile
import urllib.request
import numpy as np
import scipy.io as sio
import json

import ssl_common as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, 'data')
TEMP_DIR = os.path.join(HERE, 'temp_download')
SWEC_SHORT_FS = 512.0

PATIENT_URLS = [
    ('ID1', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID1.zip'),
    ('ID2', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID2.zip'),
    ('ID3', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID3.zip'),
    ('ID4a', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID4a.zip'),
    ('ID4b', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID4b.zip'),
    ('ID5', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID5.zip'),
    ('ID6', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID6.zip'),
    ('ID7', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID7.zip'),
    ('ID8', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID8.zip'),
    ('ID9', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID9.zip'),
    ('ID10', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID10.zip'),
    ('ID11', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID11.zip'),
    ('ID12', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID12.zip'),
    ('ID13a', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID13a.zip'),
    ('ID13b', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID13b.zip'),
    ('ID14a', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID14a.zip'),
    ('ID14b', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID14b.zip'),
    ('ID15', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID15.zip'),
    ('ID16', 'https://iis-people.ee.ethz.ch/~ieeg/BioCAS2018/dataset/ID16.zip'),
]

def process_mat_file(filepath):
    """Parses a single seizure .mat file, resamples to 256Hz, and extracts 4s z-scored windows."""
    try:
        mat_data = sio.loadmat(filepath)
        if 'EEG' not in mat_data:
            return np.empty((0, C.WIN_LEN), dtype=np.float32)
        
        eeg = mat_data['EEG'].astype(np.float32)  # Shape: (T, M)
        if eeg.ndim != 2:
            return np.empty((0, C.WIN_LEN), dtype=np.float32)
        
        # Transpose to (Channels M, Time T)
        eeg = eeg.T  # (M, T)
        
        # Resample from 512 Hz to 256 Hz
        x = C.resample_to_target(eeg, SWEC_SHORT_FS)
        del eeg
        
        # Bandpass filter (1-100 Hz)
        x = C.bandpass(x)
        
        # Extract 4-second non-overlapping windows
        windows, _ = C.make_windows(x, stride_sec=C.WIN_SEC)
        return windows
    except Exception as err:
        print(f"    [Warning] Error processing {os.path.basename(filepath)}: {err}")
        return np.empty((0, C.WIN_LEN), dtype=np.float32)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    all_windows = []
    log_info = {}
    
    print("=== SWEC-ETHZ Short-Term Dataset Streaming Download & Feature Extraction ===")
    
    for pid, url in PATIENT_URLS:
        zip_name = f"{pid}.zip"
        zip_path = os.path.join(TEMP_DIR, zip_name)
        extract_folder = os.path.join(TEMP_DIR, pid)
        
        print(f"\n[Processing {pid}] Downloading from {url}...")
        try:
            # 1. Download
            urllib.request.urlretrieve(url, zip_path)
            
            # 2. Extract
            os.makedirs(extract_folder, exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extract_folder)
            
            # Remove zip immediately after extraction to save space
            if os.path.exists(zip_path):
                os.remove(zip_path)
                
            # 3. Process all .mat files in extract_folder
            mat_files = []
            for root, dirs, files in os.walk(extract_folder):
                for f in files:
                    if f.endswith('.mat'):
                        mat_files.append(os.path.join(root, f))
            
            print(f"  Found {len(mat_files)} .mat seizure files for {pid}. Extracting windows...")
            patient_windows = []
            for mf in sorted(mat_files):
                w = process_mat_file(mf)
                if len(w) > 0:
                    patient_windows.append(w.astype(np.float16))
            
            if patient_windows:
                cat_p = np.concatenate(patient_windows)
                all_windows.append(cat_p)
                log_info[pid] = {'files': len(mat_files), 'windows': len(cat_p)}
                print(f"  -> {pid} completed: {len(cat_p)} total 4-sec windows extracted.")
            else:
                log_info[pid] = {'files': len(mat_files), 'windows': 0}
                
        except Exception as err:
            print(f"  [ERROR] Failed to process {pid}: {err}")
            log_info[pid] = {'error': str(err)}
        finally:
            # 4. Clean up extracted files immediately to maintain free disk space
            if os.path.exists(extract_folder):
                shutil.rmtree(extract_folder)
            if os.path.exists(zip_path):
                os.remove(zip_path)
    
    # Consolidate and save pretraining corpus
    if all_windows:
        full_corpus = np.concatenate(all_windows)
        out_path = os.path.join(OUT_DIR, 'swec_shortterm_pretrain.npy')
        np.save(out_path, full_corpus)
        
        print("\n" + "=" * 80)
        print("=== STREAMING EXTRACTION COMPLETED SUCCESSFULLY ===")
        print(f"Total extracted pretraining corpus: {full_corpus.shape} ({full_corpus.nbytes / 1e6:.1f} MB)")
        print(f"Saved to: {out_path}")
        print("=" * 80)
        
        # Save log info
        with open(os.path.join(OUT_DIR, 'swec_shortterm_info.json'), 'w') as f:
            json.dump(log_info, f, indent=2)
    else:
        print("[ERROR] No windows were extracted.")

if __name__ == '__main__':
    main()
