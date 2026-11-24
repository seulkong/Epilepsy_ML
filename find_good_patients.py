import numpy as np

data = np.load('timeseries_dataset.npz')
X_seq = data['X_seq']
y = data['y']
groups = data['groups']

for i in range(len(y)):
    seq = X_seq[i]
    valid_len = len(seq)
    for j in range(len(seq)):
        if np.all(seq[j] == 0):
            valid_len = j
            break
    if valid_len == 0: continue
    seq = seq[:valid_len]
    velocity = seq[:, 5]
    mean_vel = np.mean(velocity)
    
    if y[i] == 0 and mean_vel > 9.24:
        print(f"Good Failure Patient: {groups[i]} (idx {i}), Mean Vel: {mean_vel:.2f}")
    if y[i] == 1 and mean_vel < 4.0:
        print(f"Good Success Patient: {groups[i]} (idx {i}), Mean Vel: {mean_vel:.2f}")
        
