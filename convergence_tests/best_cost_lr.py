"""
Figure 1: Convergence of cost by learning rate
"""

import os

import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt

LEARNING_RATES = (1.0, 0.5, 0.25, 0.1, 0.05, 0.02, 0.01)
BATCH_SIZES = (5, 10, 15, 25, 50)
NT = 20

for bs in BATCH_SIZES:
    if bs > NT: continue
    best_cost = []
    label = "Batch size=%i" % bs
    for lr in LEARNING_RATES:
        subdir = "nt_%i_lr_%.3f_bs_%i" % (NT, lr, bs)
        cost_history = nib.load(os.path.join(subdir, "cost_history.nii.gz")).get_data()
        best_cost.append(np.mean(cost_history, axis=(0, 1, 2))[-1])
    plt.plot(best_cost, label=label)

plt.title("Best cost by learning rate and batch size")
plt.ylabel("Best cost achieved")
plt.xlabel("Learning rate")
#plt.ylim(35, 100)
plt.xticks(range(len(LEARNING_RATES)), ["%.2f" % lr for lr in LEARNING_RATES])
plt.legend()

plt.show()