import numpy as np
data = np.load('timeseries_dataset.npz')
print("t=1", data['X_seq'][0, 1, :])
print("t=2", data['X_seq'][0, 2, :])
