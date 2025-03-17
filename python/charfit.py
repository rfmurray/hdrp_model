import numpy as np
from scipy import optimize
from scipy.stats import linregress
import matplotlib.pyplot as plt

class CharLum:

    def __init__(self, v=None, lum=None):
        # call constructor of parent?

        self.v = v if v is not None else None
        self.lum = lum if lum is not None else None

        self.L0 = None
        self.L1 = None
        self.v0 = None
        self.gamma = None

    def fit(self):
        # define sum-of-squares objective function
        def errfn(param):
            return ((self.lum - self.v2lum(self.v, *param)) ** 2).sum()

        # make initial estimates of parameters
        k = self.v > 0.1
        gamma_hat = linregress(np.log(self.v[k]), np.log(self.lum[k])).slope
        pinit = np.array((min(self.lum), max(self.lum) - min(self.lum), 0, gamma_hat))

        # optimize fit
        cons = optimize.LinearConstraint(np.array((0, 0, 1, 0)).reshape((1, 4)), np.array((0,)))  # constrain v0 >= 0
        r = optimize.minimize(errfn, pinit, constraints=cons)
        self.L0, self.L1, self.v0, self.gamma = r.x

    def plot(self):
        vv = np.linspace(0, 1, 100)
        plt.plot(vv, self.v2lum(vv), 'k-')
        plt.plot(self.v, self.lum, 'ro', markersize=10)
        plt.legend(['fit', 'measurements'], frameon=False)
        plt.xlabel('post-processed $v_k$', fontsize=18)
        plt.ylabel('luminance (cd/m$^2$)', fontsize=18)
        plt.show()

    def v2lum(self, v, L0=None, L1=None, v0=None, gamma=None):
        if L0 is None: L0 = self.L0
        if L1 is None: L1 = self.L1
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        return L0 + L1 * self.h(v, v0=v0, gamma=gamma)

    def lum2v(self, lum, L0=None, L1=None, v0=None, gamma=None):
        if L0 is None: L0 = self.L0
        if L1 is None: L1 = self.L1
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        p = (lum-L0)/L1
        return self.hinv(p, v0=v0, gamma=gamma)

    def h(self, v, v0=None, gamma=None, maxout=True):
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        ub = 1 if maxout else np.inf
        v = np.array(v).clip(v0, ub)
        return ((v-v0)/(1-v0)) ** gamma

    def hinv(self, p, v0=None, gamma=None, maxout=True):
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        ub = 1 if maxout else np.inf
        p = np.array(p).clip(0, ub)
        return v0 + (1-v0)*(p ** (1/gamma))

class CharXYZ:

    def __init__(self, v=None, xyz=None):
        # call constructor of parent?

        self.v = v if v is not None else None
        self.xyz = xyz if xyz is not None else None

        self.rgb = None
        self.z = None
        self.v0 = [None, None, None]
        self.gamma = [None, None, None]

    def fit(self):
        self.fit1()
        self.fit2()

    def fit1(self):

        # estimate the primaries and background term
        def lookup(row):
            'find the entry in self.xyz corresponding to a given row of v'
            return self.xyz[(self.v == row).all(axis=1).nonzero()[0], :].reshape((1, 3))
        self.z = lookup((0, 0, 0))
        r = lookup((1, 0, 0)) - self.z
        g = lookup((0, 1, 0)) - self.z
        b = lookup((0, 0, 1)) - self.z
        self.rgb = np.vstack((r, g, b))

        # estimate the activations; solve xyz = p @ rgb + z for p
        p = (self.xyz - self.z) @ np.linalg.inv(self.rgb)

        # for each primary, fit h() to activation vs. v
        for k in range(3):
            def errfn(param):
                return ((p[:, k] - self.h(self.v[:, k], *param)) ** 2).sum()
            # could estimate gamma from data like in achromatic version
            pinit = np.array((0, 2.2))
            cons = optimize.LinearConstraint(np.array((1, 0)), np.array((0,)))  # constrain v0 >= 0
            r = optimize.minimize(errfn, pinit, constraints=cons)
            self.v0[k], self.gamma[k] = r.x

    def fit2(self):
        def param2vec(rgb, z, v0, gamma):
            return np.hstack((rgb.flatten(), z.flatten(), np.array(v0), np.array(gamma)))
        def vec2param(v):
            return v[0:9].reshape((3,3)), v[9:12].reshape((1,3)), v[12:15].tolist(), v[15:18].tolist()
        def errfn(vec):
            rgb, z, v0, gamma = vec2param(vec)
            p = (self.xyz - z) @ np.linalg.inv(rgb)  # find the activations; solve xyz = p @ rgb + z for p
            err = 0
            for k in range(3):
                phat = self.h(self.v[:,k], v0=v0[k], gamma=gamma[k])
                err += ((p[:,k]-phat)**2).sum()
            return err
        pinit = param2vec(self.rgb, self.z, self.v0, self.gamma)
        err_pre = errfn(pinit)
        print(f'{err_pre:.3g}')
        cons = None  # define constraints v0 >= 0
        r = optimize.minimize(errfn, pinit, constraints=cons)
        err_post = errfn(r.x)
        print(f'{err_post:.3g}')
        self.rgb, self.z, self.v0, self.gamma = vec2param(r.x)

    def plot(self):
        p = (self.xyz - self.z) @ np.linalg.inv(self.rgb) # find the activations; solve xyz = p @ rgb + z for p
        vv = np.linspace(0,1,100)
        for k in range(3):
            plt.plot(vv, self.h(vv, v0=self.v0[k], gamma=self.gamma[k]), 'rgb'[k] + '-')
            plt.plot(self.v[:, k], p[:, k], 'rgb'[k] + 'o')
        plt.xlabel('post-processed $v_k$', fontsize=18)
        plt.ylabel('activation', fontsize=18)
        plt.show()

    def v2xyz(self, v, rgb=None, z=None, v0=None, gamma=None):
        if rgb is None: rgb = self.rgb
        if z is None: z = self.z
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        # return L0 + L1 * self.h(v, v0=v0, gamma=gamma)

    def xyz2v(self, lum, rgb=None, z=None, v0=None, gamma=None):
        if rgb is None: rgb = self.rgb
        if z is None: z = self.z
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        # p = (lum-L0)/L1
        # return self.hinv(p, v0=v0, gamma=gamma)

    def h(self, v, v0=None, gamma=None, k=None, maxout=True):
        if v0 is None: v0 = self.v0[k]
        if gamma is None: gamma = self.gamma[k]
        ub = 1 if maxout else np.inf
        v = np.array(v).clip(v0, ub)
        return ((v-v0)/(1-v0)) ** gamma

    def hinv(self, p, v0=None, gamma=None, k=None, maxout=True):
        if v0 is None: v0 = self.v0[k]
        if gamma is None: gamma = self.gamma[k]
        ub = 1 if maxout else np.inf
        p = np.array(p).clip(0, ub)
        return v0 + (1-v0)*(p ** (1/gamma))
