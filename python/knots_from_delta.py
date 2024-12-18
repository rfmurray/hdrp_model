# knots_from_delta.py  Estimate knot points by using delta functions for tonemapping

import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from hdrp import srgb, srgbinv, TonemapCube, cubetag

# load data from Unity project render_delta
df = pd.read_csv('data/data_delta.txt')

# calculate unprocessed color coordinates u_k and tonemapped coordinates t_k
df['u_k'] = 0.823 * df['i_d'] / np.pi   # use the Lambertian rendering model to find u_k
df['t_k'] = srgb(df['v_r'])             # use the post-processed values in the red channel to find t_k

# plot tonemapping results from one cube file (delta_16.cube)
fig = plt.figure(figsize=(14,10))
df2 = df[df['delta_m']==16].reset_index()
ax1 = fig.add_subplot(2,1,1)
ax1.plot(df2['u_k'], df2['t_k'], 'ro', markersize=3)
ax1.set_xscale('log')
ax1.set_xlim((1e-4, 100))
ax1.set_ylim((0, 1.1))
ax1.set_xlabel('unprocessed $u_k$', fontsize=18)
ax1.set_ylabel('tonemapped $t_k$', fontsize=18)
ax1.text(1.2e-4,0.1,'(a)',fontsize=24)

# plot tonemapping results from all cube files, and find knot points
ax2 = fig.add_subplot(2,1,2)
colors = list(mcolors.TABLEAU_COLORS.keys())
n = max(df['delta_m'])
u_knot = np.full((n,), np.nan)
for i in range(3, n+1):

    # find knot point
    df2 = df[df['delta_m']==i].reset_index()
    if i==3:
        j = (df2['t_k'] > 0.99).to_numpy().nonzero()[0][-1]
    elif i==n:
        j = (df2['t_k'] == 1).to_numpy().nonzero()[0][0]
    else:
        j = (df2['t_k']).to_numpy().argmax()
    u_knot[i-1] = df2.loc[j,'u_k']
    
    # plot data from this cube file
    ax2.plot(df2['u_k'], df2['t_k'], 'o', color=colors[i % 10], markersize=3)
    ax2.plot(2*(u_knot[i-1],), (0, 1.1), '-', color='silver')
    ax2.text(0.92*u_knot[i-1], 1.05, f'{i}')

# format plot
ax2.set_xscale('log')
ax2.set_xlim((1e-4, 100))
ax2.set_ylim((0, 1.1))
ax2.set_xlabel('unprocessed $u_k$', fontsize=18)
ax2.set_ylabel('tonemapped $t_k$', fontsize=18)
ax2.text(1.2e-4,0.1,'(b)',fontsize=24)
plt.savefig('figures/knots_from_delta.pdf', bbox_inches='tight')
plt.show()

# print estimates of knot points
u_knot = np.concatenate( ( np.array((0, 1e-9)), u_knot[2:]) )
print(np.array2string(u_knot, formatter={'float' : lambda u : f'{u:.4g}'}, separator=', ', max_line_width=np.inf))
