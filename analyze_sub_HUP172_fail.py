import numpy as np

data = np.load('timeseries_dataset.npz')
X_seq = data['X_seq']
y = data['y']
groups = data['groups']

idx = 157
seq = X_seq[idx]
valid_len = len(seq)
for i in range(len(seq)):
    if np.all(seq[i] == 0):
        valid_len = i
        break
seq = seq[:valid_len]
in_mask = seq[:, 4]
residence = np.sum(in_mask) / valid_len * 100
print(f"Patient ID: {groups[idx]}")
print(f"Outcome: {y[idx]}")
print(f"Residence Ratio: {residence:.2f} %")
