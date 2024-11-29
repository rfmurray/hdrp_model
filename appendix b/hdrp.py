import numpy as np

Phi = 12.9232102
Gamma = 2.4
A = 0.055
X = 0.0392857
Y = 0.0030399

def srgb(x):
    y = np.empty(x.shape)
    f = x < X
    y[f] = x[f] / Phi
    y[~f] = np.power((x[~f]+A)/(1+A), Gamma)
    return y

def srgbinv(y):
    x = np.empty(y.shape)
    f = y < Y
    x[f] = y[f] * Phi
    x[~f] = np.power(y[~f], 1/Gamma)*(1+A)-A
    return x
