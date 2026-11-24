#!/usr/bin/env python3
import os
import sys
import requests
from tqdm import tqdm

url = "https://zenodo.org/api/records/14578383/files/SWEC_ETHZ_iEEG_Sez_BNEW-2025.zip/content"
out_dir = "external_datasets"
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, "SWEC_ETHZ_iEEG_Sez_BNEW-2025.zip")

print("=== Starting Direct Download: SWEC-ETHZ iEEG Dataset from Zenodo ===")
print(f"URL: {url}")
print(f"Target: {out_file}")

try:
    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024 * 1024  # 1MB chunks

    with open(out_file, 'wb') as f, tqdm(
        total=total_size, unit='iB', unit_scale=True, desc="SWEC-ETHZ Download"
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=block_size):
            if chunk:
                f.write(chunk)
                progress_bar.update(len(chunk))

    print(f"\n=== DOWNLOAD COMPLETED SUCCESSFULLY ===")
    print(f"Downloaded file: {out_file} ({os.path.getsize(out_file)} bytes)")

except Exception as err:
    print(f"\n=== DOWNLOAD ERROR: {err} ===")
    sys.exit(1)
