import numpy as np

data = np.load('timeseries_dataset.npz')
X_seq = data['X_seq']
groups = data['groups']
y = data['y']

idx = 0
print(f"Patient ID: {groups[idx]}")
print(f"Outcome (1=Success, 0=Failure): {y[idx]}")

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

print(f"Duration: {valid_len * 0.5} seconds")
print(f"Initial Distance to Resection: {dist_mm[0]:.2f} mm")
print(f"Final Distance to Resection: {dist_mm[-1]:.2f} mm")
print(f"Min Distance to Resection: {np.min(dist_mm):.2f} mm")
print(f"Mean Velocity: {np.mean(velocity):.2f} mm/s")
print(f"Max Velocity: {np.max(velocity):.2f} mm/s")
residence = np.sum(in_mask) / valid_len * 100
print(f"Residence Ratio: {residence:.2f} %")
