#!/usr/bin/env python3
import os
import shutil
import json

dl_token = os.path.expanduser('~/Downloads/kaggle.json')
target_dir = os.path.expanduser('~/.kaggle')
target_file = os.path.join(target_dir, 'kaggle.json')

if os.path.exists(dl_token):
    os.makedirs(target_dir, exist_ok=True)
    shutil.copy(dl_token, target_file)
    os.chmod(target_file, 0o600)
    print("=== Found kaggle.json in Downloads! Copied to ~/.kaggle/kaggle.json ===")
    with open(target_file) as f:
        data = json.load(f)
    print("Username:", data.get('username'))
else:
    print("=== kaggle.json not found yet in ~/Downloads ===")
