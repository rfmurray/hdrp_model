# char_achromatic_2.py  Test whether luminance is proportional to u_k

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hdrp import srgb

# load luminance characterization measurements, made with tonemapping on
df = pd.read_csv('data/characterize/data_achromatic_T1.txt')
m_k = df['m_k'].to_numpy()
lum = df['lum'].to_numpy()
u_k = srgb(m_k)

# find the linear regression of luminance vs. u_k, constrained to pass through the origin
slope = np.linalg.lstsq(u_k.reshape(-1,1), lum.reshape(-1,1))[0].item()

# plot the data and the fit
xlim = np.array([0,1])
plt.plot(xlim, slope * xlim, 'k-')
plt.plot(u_k, lum, 'ro', markersize=10)
plt.legend(['linear fit', 'measurements'], frameon=False)
plt.xlabel('unprocessed $u_k$', fontsize=18)
plt.ylabel('luminance (cd/m$^2$)', fontsize=18)
plt.savefig('figures/char_achromatic_2.pdf');
plt.show()
