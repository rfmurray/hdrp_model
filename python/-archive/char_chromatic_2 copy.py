# char_chromatic_2.py  Test whether primary coefficients are proportional to u_k

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, h, hinv, TonemapCube

# load color characterization measurements, made with tonemapping on
df = pd.read_csv('data/characterize/data_chromatic_T1.txt')
m = df[['m_r', 'm_g', 'm_b']].to_numpy()
xyz = df[['x', 'y', 'z']].to_numpy()
u = srgb(m)

# estimate the primaries and background term
def lookup(row):
    'find the entry in xyz corresponding to a given row of u_k'
    return xyz[(u==row).all(axis=1).nonzero()[0],:].reshape((1,3))
z_hat = lookup((0,0,0))
r_hat = lookup((1,0,0)) - z_hat
g_hat = lookup((0,1,0)) - z_hat
b_hat = lookup((0,0,1)) - z_hat
rgb_hat = np.vstack((r_hat,g_hat,b_hat))

# express the background term as a weighted sum of the primaries; solve z_hat = w @ rgb_hat for w
w = (z_hat @ np.linalg.inv(rgb_hat)).reshape((1,3))

# step through the primaries
p = []
for k in range(3):

    # estimate the activation as a function of u
    # - step 1. find the rows of u where the other primaries are not activated
    # *** as in char_chromatic_1.py, maybe better not to do this
    kk = (u[:,[i for i in range(3) if i != k]] == 0).all(axis=1)
    uu = u[kk,k]
    # - step 2. estimate the activations for those rows
    xx = xyz[kk,:] - z_hat
    pp = xx.dot(rgb_hat[k,:]) / (np.linalg.norm(rgb_hat[k,:])**2)
    p.append(pp)

p = np.column_stack(p)

# # find the linear regression of luminance vs. u_k, constrained to pass through the origin
# slope = np.linalg.lstsq(u_k.reshape(-1,1), lum.reshape(-1,1))[0].item()

# plot the data and the fit
xlim = np.array([0,1])
# plt.plot(xlim, slope * xlim, 'k-')
plt.plot(u, p+w, 'ro', markersize=10)
plt.legend(['linear fit', 'measurements'], frameon=False)
plt.xlabel('unprocessed $u_k$', fontsize=18)
plt.ylabel('primary coefficients', fontsize=18)
plt.show()
