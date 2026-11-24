#!/usr/bin/env python3
import os
import sys
import requests
from tqdm import tqdm

token = "KGAT_e96bf864460aa5de42cac31ff4b90991"
url = "https://www.kaggle.com/api/v1/competitions/data/download-all/seizure-prediction"

out_dir = "external_datasets/kaggle_seizure_prediction"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "seizure-prediction.zip")

print("=== Starting Kaggle API Direct Download via Bearer Token ===")
print(f"Target URL: {url}")
print(f"Output File: {out_file}")

headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(url, headers=headers, stream=True, timeout=60)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 * 1024  # 1MB chunks

    with open(out_file, 'wb') as f, tqdm(
        total=total_size, unit='iB', unit_scale=True, desc="Kaggle Seizure-Prediction API Download"
    ) as pbar:
        for chunk in response.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                pbar.update(len(chunk))

    print(f"\n=== KAGGLE API DOWNLOAD COMPLETED SUCCESSFULLY ===")
    print(f"Saved dataset: {out_file} ({os.path.getsize(out_file)} bytes)")

except Exception as err:
    print(f"\n=== KAGGLE API DOWNLOAD ERROR: {err} ===")
    sys.exit(1)
