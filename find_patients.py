import numpy as np

data = np.load('timeseries_dataset.npz')
groups = data['groups']
y = data['y']

success_idx = np.where(y == 1)[0]
failure_idx = np.where(y == 0)[0]

print(f"Success Patient: {groups[success_idx[0]]} (index {success_idx[0]})")
print(f"Failure Patient: {groups[failure_idx[0]]} (index {failure_idx[0]})")
