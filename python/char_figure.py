# char_figure.py  Plot achromatic and chromatic characterization data,
#                 with and without tonemapping for data correction

import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt
from hdrp import srgb, srgbinv, TonemapCube
from charfit import CharLum, CharXYZ

# 1a. achromatic characterization, with tonemapping off

# load luminance measurements
df = pd.read_csv('data/characterize/data_achromatic_T0.txt')
m_k = df['m_k'].to_numpy()
lum = df['lum'].to_numpy()
u_k = srgb(m_k)
v_k = m_k

# fit a characterization model to luminance vs. v_k
char = CharLum(v=v_k, lum=lum)
char.fit()

# plot luminance vs. unprocessed values u_k
# - the CharLum class has a method plot() that plots luminance vs.
#   post-processed values v_k, which is what is of interest for viewing
#   the fit of the characterization model; here, instead, we want to show
#   that without tonemapping for gamma correction, luminance is a nonlinear
#   function of u_k; so we'll plot that ourselves here.
u_fit = np.linspace(0, 1, 100)
v_fit = srgbinv(u_fit)
lum_fit = char.v2lum(v_fit)
fig = plt.figure(figsize=(13,5.5))
ax1 = fig.add_subplot(1,2,1)
ax1.plot(u_fit, lum_fit, 'r-')
u_data = srgb(char.v)
h1, = ax1.plot(u_data, char.lum, 'ro', markersize=10)
h1.set_label('without tonemapping')

# 1b. achromatic characterization, with tonemapping on

# load luminance characterization measurements, made with tonemapping on
df = pd.read_csv('data/characterize/data_achromatic_T1.txt')
m_k = df['m_k'].to_numpy()
lum = df['lum'].to_numpy()
u_k = srgb(m_k)

# find the linear regression of luminance vs. u_k, constrained to pass through the origin
slope = np.linalg.lstsq(u_k.reshape(-1,1), lum.reshape(-1,1))[0].item()

# plot the data and the fit
xlim = np.array([0,1])
ax1.plot(xlim, slope * xlim, 'r-')
h2, = ax1.plot(u_k, lum, 'rs', markersize=10)
h2.set_label('with tonemapping')

#plt.legend(['linear fit', 'measurements'], frameon=False)
ax1.set_xlabel('unprocessed $u_k$', fontsize=18)
ax1.set_ylabel('luminance (cd/m$^2$)', fontsize=18)
ax1.text(0.02,380,'(a)',fontsize=24)
ax1.legend(handles=[h2, h1], loc='lower right', frameon=False)

# 2a. chromatic characterization, with tonemapping off

# load xyz measurements
df = pd.read_csv('data/characterize/data_chromatic_T0.txt')
m = df[['m_r','m_g','m_b']].to_numpy()
xyz = df[['x','y','z']].to_numpy()
u = srgb(m)
v = m.copy()

# fit a characterization model to xyz vs. v_k
char = CharXYZ(v=v, xyz=xyz)
char.fit()

# plot xyz vs. unprocessed values u_k
#u_fit = np.linspace(0, 1, 100)
#v_fit = srgbinv(u_fit)
#lum_fit = char.v2lum(v_fit)
ax2 = fig.add_subplot(1,2,2)
#ax2.plot(u_fit, lum_fit, 'r-')
u = srgb(char.v)
colors = ['red', 'green', 'blue']
for i in range(3):
#    k = v[:,i] > 0 and v[:,[0,1,2]-i] == 0
    h, = ax2.plot(u[:,i], char.xyz[:,i], 'rgb'[i] + 'o', markersize=10)
    h.set_label(colors[i] + ' channel')
    

# 2b. chromatic characterization, with tonemapping on

## load luminance characterization measurements, made with tonemapping on
#df = pd.read_csv('data/characterize/data_achromatic_T1.txt')
#m_k = df['m_k'].to_numpy()
#lum = df['lum'].to_numpy()
#u_k = srgb(m_k)
#
## find the linear regression of luminance vs. u_k, constrained to pass through the origin
#slope = np.linalg.lstsq(u_k.reshape(-1,1), lum.reshape(-1,1))[0].item()
#
## plot the data and the fit
#xlim = np.array([0,1])
#ax2.plot(xlim, slope * xlim, 'g-')
#ax2.plot(u_k, lum, 'go', markersize=10)
#
##plt.legend(['linear fit', 'measurements'], frameon=False)

ax2.set_xlabel('unprocessed $u_k$', fontsize=18)
ax2.set_ylabel('primary activation', fontsize=18)
ax2.text(0.02,380,'(b)',fontsize=24)
#ax2.legend(loc='lower right', frameon=False)

plt.savefig(f'figures/characterize.pdf', bbox_inches='tight')
plt.show()
