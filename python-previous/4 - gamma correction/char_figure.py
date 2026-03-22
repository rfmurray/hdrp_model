# char_figure.py  Plot achromatic and chromatic characterization data,
#                 with and without tonemapping for data correction

import numpy as np
import pandas as pd
from scipy import optimize
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
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
ax1.plot(u_data, char.lum, 'ro', markersize=10)

# 1b. achromatic characterization, with tonemapping on

# load luminance characterization measurements, made with tonemapping on
df = pd.read_csv('data/characterize/data_achromatic_T1.txt')
m_k = df['m_k'].to_numpy()
lum = df['lum'].to_numpy()
u_k = srgb(m_k)

# find the linear regression of luminance vs. u_k, constrained to pass through the origin
slope = np.linalg.lstsq(u_k.reshape(-1,1), lum.reshape(-1,1), rcond=-1)[0].item()

# plot the data and the fit
xlim = np.array([0,1])
ax1.plot(xlim, slope * xlim, 'r-')
ax1.plot(u_k, lum, 'rs', markersize=10)

# format this panel
h1 = Line2D([0], [0], marker='s', color='r', markersize=10)
h2 = Line2D([0], [0], marker='o', color='r', markersize=10)
ax1.legend(handles=[h1, h2], labels=['with tonemapping', 'without tonemapping'], frameon=False)
ax1.set_xlabel('unprocessed $u_k$', fontsize=18)
ax1.set_ylabel('luminance (cd/m$^2$)', fontsize=18)
ax1.text(0.85,15,'(a)',fontsize=24)

# 2a. chromatic characterization, with tonemapping off

# load xyz measurements
df = pd.read_csv('data/characterize/data_chromatic_T0.txt')
m = df[['m_r', 'm_g', 'm_b']].to_numpy()
xyz = df[['x', 'y', 'z']].to_numpy()
v = m

# fit a characterization model to xyz vs. v
char = CharXYZ(v=v, xyz=xyz)
char.fit()

# express the background term as a weighted sum of the primaries; solve z = w @ rgb for w
w = (char.z @ np.linalg.inv(char.rgb)).reshape((1, 3))

# plot primary coefficients vs. unprocessed values u_k
ax2 = fig.add_subplot(1,2,2)
coef = char.xyz @ np.linalg.inv(char.rgb) # find the coefficients; solve xyz = coef @ rgb for coef
u_fit = np.linspace(0, 1, 100)
v_fit = srgbinv(u_fit)
for k in range(3):
    coef_fit = char.h(v_fit, v0=char.v0[k], gamma=char.gamma[k]) + w[0,k]
    ax2.plot(u_fit, coef_fit, 'rgb'[k] + '-')
u_data = srgb(char.v)
for k in range(3):
    ax2.plot(u_data[:, k], coef[:, k], 'rgb'[k] + 'o', markersize=10)

# 2b. chromatic characterization, with tonemapping on

# load color characterization measurements, made with tonemapping on
df = pd.read_csv('data/characterize/data_chromatic_T1.txt')
m = df[['m_r', 'm_g', 'm_b']].to_numpy()
xyz = df[['x', 'y', 'z']].to_numpy()
u = srgb(m)
v = m

# fit a characterization model to xyz vs. v
char = CharXYZ(v=v, xyz=xyz)
char.fit()

# find the primary coefficients; solve xyz = coef @ rgb for coef
coef = char.xyz @ np.linalg.inv(char.rgb)

# plot the data and linear fits
u_data = srgb(char.v)
xlim = np.array([0,1])
for k in range(3):
    x = u_data[:,k].reshape((-1,1))
    y = coef[:,k].reshape((-1,1))
    slope = np.linalg.lstsq(x, y, rcond=-1)[0].item()
    ax2.plot(xlim, slope * xlim, 'rgb'[k] + '-')
for k in range(3):
    ax2.plot(u_data[:, k], coef[:, k], 'rgb'[k] + 's', markersize=10)

h1 = Line2D([0], [0], marker='s', color='b', markersize=10)
h2 = Line2D([0], [0], marker='o', color='b', markersize=10)
ax2.legend(handles=[h1, h2], labels=['with tonemapping', 'without tonemapping'], frameon=False)

ax2.set_xlabel('unprocessed $u_k$', fontsize=18)
ax2.set_ylabel('primary coefficient', fontsize=18)
ax2.text(0.85,0.06,'(b)',fontsize=24)
plt.savefig(f'figures/characterize.pdf', bbox_inches='tight')
plt.show()
