# char_chromatic_2.py  Test whether primary coefficients are proportional to u_k

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import optimize
from charfit import CharXYZ

sys.path.append('..')
from hdrp import srgb

# load color characterization measurements, made with tonemapping on
df = pd.read_csv('../data/characterize/data_chromatic_T1.txt')
m = df[['m_r', 'm_g', 'm_b']].to_numpy()
xyz = df[['x', 'y', 'z']].to_numpy()
u = srgb(m)

# fit a characterization model to xyz vs. v
char = CharXYZ(v=u, xyz=xyz)
char.fit()
# - here we fit a mapping just to get estimates of the primaries xyz and
#   mapping matrix rgb, used in the next line; with tonemapping in place,
#   the mapping from u to xyz should be linear, so we'll fit that as an easy mapping

# find the primary coefficients; solve xyz = coef @ rgb for coef
coef = char.xyz @ np.linalg.inv(char.rgb)

# plot the data and linear fits
xlim = np.array([0,1])
for k in range(3):
    x = u[:,k].reshape((-1,1))
    y = coef[:,k].reshape((-1,1))
    slope = np.linalg.lstsq(x, y)[0].item()
    plt.plot(xlim, slope * xlim, 'rgb'[k] + '-')
for k in range(3):
    plt.plot(u[:, k], coef[:, k], 'rgb'[k] + 'o')
plt.xlabel('unprocessed $u_k$', fontsize=18)
plt.ylabel('primary coefficient', fontsize=18)
plt.legend(labels=['red','green','blue'], frameon=False)
plt.savefig('../figures/char_chromatic_2.pdf');
plt.show()
