# knots_from_delta.py  Estimate knot points from effects of delta functions in tonemapping

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hdrp import srgb, srgbinv, TonemapCube, cubetag

df = pd.read_csv('data/data_delta.txt')
df = df[df['delta'] >= 3]
df['delta'] -= 2
df['u_k'] = 0.822 * df['i_d'] / np.pi
df['t_k'] = srgb(df['v_r'])

n = max(df['delta'])
u_knot = np.full((n,), np.nan)

plt.figure(figsize=(12,5))

for i in range(1, n+1):
    
    df2 = df[df.delta==i].reset_index()
    
    if i==1:
        j = (df2['t_k'] > 0.99).to_numpy().nonzero()[0][-1]
    elif i==n:
        j = (df2['t_k'] == 1).to_numpy().nonzero()[0][0]
    else:
        j = (df2['t_k']).to_numpy().argmax()

    u_knot[i-1] = df2.loc[j,'u_k']
    
    plt.plot(df2['u_k'], df2['t_k'], 'ro', markersize=1)
    plt.plot(2*(u_knot[i-1],), (0, 1.1), '-', color='silver')
    plt.text(0.92*u_knot[i-1], 1.05, f'{i+2}')

u_knot = np.concatenate( ( np.array((0, 1e-9)), u_knot) )
print(np.array2string(u_knot, formatter={'float' : lambda u : f'{u:.6g}'}, separator=', ', max_line_width=np.inf))

plt.xscale('log')
plt.ylim((0, 1.1))
plt.xlabel('rendered $u_k$', fontsize=18)
plt.ylabel('tonemapped $t_k$', fontsize=18)
plt.show()
