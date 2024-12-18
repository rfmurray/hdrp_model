# cal_achromatic_2.py

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# make an array of the post-processed values v_k displayed for the characterization measurements
v_k = np.linspace(0, 1, 11)

# make an array of the luminances recorded during the characterization measurements
# - here we'll make up some measurements; alternatively, replace 'lum' with an array of real luminance measurements
lum  = 100 * v_k + np.random.normal(scale=1, size=v_k.shape)

# find the linear regression of luminance vs. v_k
m = np.linalg.lstsq(v_k.reshape(-1,1), lum.reshape(-1,1))[0].item()

# plot the data and the fit
xlim = np.array([0,1])
plt.plot(xlim, m * xlim, 'k-')
plt.plot(v_k, lum, 'ro', markersize=10)
plt.legend(['linear fit', 'measurements'], frameon=False)
plt.xlabel('post-processed v_k', fontsize=18)
plt.ylabel('luminance (cd/m$^2$)', fontsize=18)
plt.show()
