import numpy as np

data = np.load('timeseries_dataset.npz')
X_seq = data['X_seq']
y = data['y']
groups = data['groups']

idx = 5
seq = X_seq[idx]
valid_len = len(seq)
for i in range(len(seq)):
    if np.all(seq[i] == 0):
        valid_len = i
        break
seq = seq[:valid_len]
dist_mm = seq[:, 3]
in_mask = seq[:, 4]
velocity = seq[:, 5]

print(f"Patient ID: {groups[idx]}")
print(f"Outcome: {y[idx]}")
print(f"Mean Velocity: {np.mean(velocity):.2f} mm/s")
residence = np.sum(in_mask) / valid_len * 100
print(f"Residence Ratio: {residence:.2f} %")
