#!/usr/bin/env python3
import sys
import kagglehub

print("=== Starting Kaggle Seizure Prediction Dataset Download ===")
try:
    path = kagglehub.competition_download('seizure-prediction')
    print(f"=== DOWNLOAD COMPLETED ===")
    print(f"Dataset files saved at: {path}")
except Exception as err:
    print(f"=== DOWNLOAD ERROR ===")
    print(f"Error details: {err}")
