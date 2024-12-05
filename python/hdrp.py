import os
import numpy as np
from scipy.interpolate import interpn
import matplotlib.pyplot as plt

Phi = 12.92
Gamma = 2.4
A = 0.055
X = 0.04045
Y = 0.0031308

def srgb(x):
    if ~isinstance(x, np.ndarray):
        x = np.array(x)
    y = np.empty(x.shape)
    f = x < X
    y[f] = x[f] / Phi
    y[~f] = np.power((x[~f]+A)/(1+A), Gamma)
    return y

def srgbinv(y):
    if ~isinstance(y, np.ndarray):
        y = np.array(y)
    x = np.empty(y.shape)
    f = y < Y
    x[f] = y[f] * Phi
    x[~f] = np.power(y[~f], 1/Gamma)*(1+A)-A
    return x

def cubetag(fname):
    if len(fname) == 0:
        return ''
    _, f = os.path.split(fname)
    return '_' + os.path.splitext(f)[0]

def gamma(x, kappa, x0, gamma_exp, delta):
    x = np.array(x)
    low = x < x0
    high = x > 1
    ok = ~(low|high)

    y = np.full(x.shape, np.nan)
    y[low] = delta
    y[high] = kappa + delta
    y[ok] = kappa * ((x[ok]-x0)/(1-x0))**gamma_exp + delta
    return y

def gammainv(y, kappa, x0, gamma_exp, delta):
    y = np.array(y)
    low = y < delta
    high = y > kappa + delta
    ok = ~(low|high)

    x = np.full(y.shape, np.nan)
    x[low] = x0
    x[high] = 1
    x[ok] = x0 + (1-x0)*((y[ok]-delta)/kappa)**(1/gamma_exp)
    return x

class TonemapCube:
    
    def __init__(self, filename=''):
        
        # knot point coordinates
        self.u_knot = np.array([0, 1e-09, 1e-08, 0.0029048, 0.00716077, 0.0127321, 0.0205241, 0.0310554, 0.045044, 0.0642878, 0.0902456, 0.125466, 0.173288, 0.237135, 0.326482, 0.441934, 0.605188, 0.82122, 1.10384, 1.49459, 2.03212, 2.75649, 3.73814, 5.08289, 6.86428, 9.34713, 12.6195, 17.1796, 23.2405, 31.4807, 42.7522, 57.6644])
        
        # 3D arrays of RGB values
        self.cubeR = self.cubeG = self.cubeB = None
        
        # interpolation method
        self.method = 'linear'
        
        # filename of .cube file
        self.filename = filename
        if self.filename:
            self.load(filename)
    
    def setchannels(self, t_knot):
        n = t_knot.size
        if n != self.u_knot.size:
            raise Exception('array size does not match number of knot points')
        self.cubeR = np.tile(t_knot.reshape((-1,1,1)),(1,n,n))
        self.cubeG = np.tile(t_knot.reshape((1,-1,1)),(n,1,n))
        self.cubeB = np.tile(t_knot.reshape((1,1,-1)),(n,n,1))

    def apply(self, u_k):
        if u_k.shape[1] != 3:
            raise Exception('u_k must be an m x 3 array')
        u_k = u_k.clip(self.u_knot[2], self.u_knot[-1])
        t_r = interpn(3*(self.u_knot,), self.cubeR, u_k, method=self.method)
        t_g = interpn(3*(self.u_knot,), self.cubeG, u_k, method=self.method)
        t_b = interpn(3*(self.u_knot,), self.cubeB, u_k, method=self.method)
        return np.column_stack((t_r, t_g, t_b))
        
    def load(self, filename=''):
        if filename:
            self.filename = filename
        
        with open(self.filename, 'r') as f:
            cubetext = f.read()
        
        mat = []
        for line in cubetext.split('\n'):
            rgb = np.fromstring(line, sep=' ')
            if rgb.size == 3:
                mat.append(rgb)
        mat = np.array(mat)
        
        n = mat.shape[0] ** (1/3)
        if abs(n-round(n)) > 1e-6:
            raise Exception('number of rows is not a perfect cube')
        n = round(n)
        if n != self.u_knot.size:
            raise Exception('cube size does not match number of knot points')
        
        self.cubeR = mat[:,0].reshape((n,n,n), order='F')
        self.cubeG = mat[:,1].reshape((n,n,n), order='F')
        self.cubeB = mat[:,2].reshape((n,n,n), order='F')
    
    def save(self, filename=''):
        if filename:
            self.filename = filename
        
        mat = np.column_stack([ self.cubeR.flatten(order='F'), self.cubeG.flatten(order='F'), self.cubeB.flatten(order='F') ])
        
        f = open(self.filename, 'w')
        f.write(f'TITLE "{self.filename}"\n')
        f.write(f'LUT_3D_SIZE {self.cubeR.shape[0]}\n')
        f.write('DOMAIN_MIN 0.0 0.0 0.0\n')
        f.write('DOMAIN_MAX 1.0 1.0 1.0\n')
        np.savetxt(f, mat, fmt='%.6f')
        f.close()
    
    def __repr__(self):
        s = 'u_knot = ' + str(self.u_knot) + '\n'
        s += 'cubeR.shape = ' + str(self.cubeR.shape) + '\n'
        s += 'cubeG.shape = ' + str(self.cubeG.shape) + '\n'
        s += 'cubeB.shape = ' + str(self.cubeB.shape) + '\n'
        s += 'filename = "' + self.filename + '"\n'
        return s
