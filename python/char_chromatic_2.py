# char_chromatic_2.py  Test whether primary coefficients are proportional to u_k

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from hdrp import srgb, TonemapCube
from charfit import CharXYZ

# load color characterization measurements, made with tonemapping on
df = pd.read_csv('data/characterize/data_chromatic_T1.txt')
m = df[['m_r', 'm_g', 'm_b']].to_numpy()
xyz = df[['x', 'y', 'z']].to_numpy()
u = srgb(m)
v = m

# fit a characterization model to xyz vs. v
char = CharXYZ(v=v, xyz=xyz)
char.fit()

# express the background term as a weighted sum of the primaries; solve z = w @ rgb for w
w = (char.z @ np.linalg.inv(char.rgb)).reshape((1,3))

# estimate the primary activations; solve xyz = p @ rgb + z for p
p = (char.xyz-char.z) @ np.linalg.inv(char.rgb)

# plot the data and linear fits
xlim = np.array([0,1])
for k in range(3):
    x = u[:,k].reshape((-1,1))
    y = (p+w)[:,k].reshape((-1,1))
    slope = np.linalg.lstsq(x, y)[0].item()
    plt.plot(xlim, slope * xlim, 'rgb'[k] + '-')
    plt.plot(x, y, 'rgb'[k] + 'o', markersize=10)
plt.xlabel('unprocessed $u_k$', fontsize=18)
plt.ylabel('primary coefficients', fontsize=18)
plt.show()
