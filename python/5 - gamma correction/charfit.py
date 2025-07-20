import numpy as np
from scipy import optimize
from scipy.stats import linregress
import matplotlib.pyplot as plt

# class for luminance characterization
class CharLum:

    def __init__(self, v=None, lum=None):

        # data from characterization measurements
        self.v = v if v is not None else None         # displayed post-processed values v_k
        self.lum = lum if lum is not None else None   # measured luminances

        # parameters of fitted model
        self.L0 = None      # minimum luminance
        self.L1 = None      # luminance range
        self.v0 = None      # v_k cutoff
        self.gamma = None   # gamma function exponent

    def fit(self):
        'fit characterization model'

        # define sum-of-squares objective function
        def errfn(param):
            return ((self.lum - self.v2lum(self.v, *param)) ** 2).sum()

        # make initial estimates of parameters
        k = self.v > 0.1
        pinit = np.array((min(self.lum), max(self.lum) - min(self.lum), 0, 3))

        # optimize fit
        # cons = optimize.LinearConstraint(A=np.array([[0, 0, 1, 0]]), lb=0)  # constrain v0 >= 0
        cons = optimize.LinearConstraint(np.array((0, 0, 1, 0)).reshape((1, 4)), np.array((0,)))  # constrain v0 >= 0
        r = optimize.minimize(errfn, pinit, constraints=cons)
        self.L0, self.L1, self.v0, self.gamma = r.x

    def plot(self):
        'plot characterization measurements and model fit'
        vv = np.linspace(0, 1, 100)
        plt.plot(vv, self.v2lum(vv), 'k-')
        plt.plot(self.v, self.lum, 'ro', markersize=10)
        plt.legend(['fit', 'measurements'], frameon=False)
        plt.xlabel('post-processed $v_k$', fontsize=18)
        plt.ylabel('luminance (cd/m$^2$)', fontsize=18)
        plt.show()

    def v2lum(self, v, L0=None, L1=None, v0=None, gamma=None):
        'convert post-processed values v_k to luminance'
        if L0 is None: L0 = self.L0
        if L1 is None: L1 = self.L1
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        return L0 + L1 * self.h(v, v0=v0, gamma=gamma)

    def lum2v(self, lum, L0=None, L1=None, v0=None, gamma=None):
        'convert luminance to post-processed values v_k'
        if L0 is None: L0 = self.L0
        if L1 is None: L1 = self.L1
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        p = (lum-L0)/L1
        return self.hinv(p, v0=v0, gamma=gamma)

    def h(self, v, v0=None, gamma=None, maxout=True):
        'activation function with parameters v0, gamma; maxout determines whether maximum value is 1.0'
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        ub = 1 if maxout else np.inf
        v = np.array(v).clip(v0, ub)
        return ((v-v0)/(1-v0)) ** gamma

    def hinv(self, p, v0=None, gamma=None, maxout=True):
        'inverse of activation function with parameters v0, gamma; maxout determines whether maximum value is 1.0'
        if v0 is None: v0 = self.v0
        if gamma is None: gamma = self.gamma
        ub = 1 if maxout else np.inf
        p = np.array(p).clip(0, ub)
        return v0 + (1-v0)*(p ** (1/gamma))

# class for color characterization
class CharXYZ:

    def __init__(self, v=None, xyz=None):

        # data from characterization measurements
        self.v = v if v is not None else None         # displayed post-processed values v_k
        self.xyz = xyz if xyz is not None else None   # measured XYZ coordinates

        # parameters of fitted model
        self.rgb = None                   # XYZ coordinates of color primaries; one in each row
        self.z = None                     # XYZ coordinates of background light
        self.v0 = [None, None, None]      # v_k cutoffs for each channel
        self.gamma = [None, None, None]   # gamma exponent for each channel

    def fit(self):
        'fit model to characterization measurements'
        self.fit1()  # first pass at model fit
        self.fit2()  # fine-tune model fit

    def fit1(self):
        'first pass at model fit'

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
        'fine-tune model fit by making a global fit'

        def param2vec(rgb, z, v0, gamma):
            'convert parameters to a single 1D vector'
            return np.hstack((rgb.flatten(), z.flatten(), np.array(v0), np.array(gamma)))

        def vec2param(v):
            'convert 1D vector back to parameters'
            return v[0:9].reshape((3,3)), v[9:12].reshape((1,3)), v[12:15].tolist(), v[15:18].tolist()

        def errfn(vec):
            'find error in fit of model to characterization measurements, for parameters in 1D vector vec'
            rgb, z, v0, gamma = vec2param(vec)
            p = (self.xyz - z) @ np.linalg.inv(rgb)  # find the activations; solve xyz = p @ rgb + z for p
            err = 0
            for k in range(3):
                phat = self.h(self.v[:,k], v0=v0[k], gamma=gamma[k])
                err += ((p[:,k]-phat)**2).sum()
            return err

        # make 1D vector with current parameter estimates
        pinit = param2vec(self.rgb, self.z, self.v0, self.gamma)
        
        # define constraints v0 >= 0
        A = np.zeros((3, pinit.size))
        A[(0,1,2),(12,13,14)] = 1
        cons = optimize.LinearConstraint(A=A, lb=0, ub=np.inf)
        
        # optimize fit
        r = optimize.minimize(errfn, pinit, constraints=cons)
        self.rgb, self.z, self.v0, self.gamma = vec2param(r.x)

    def plot(self):
        # plot photphor activations and model fit
        p = (self.xyz - self.z) @ np.linalg.inv(self.rgb) # find the activations; solve xyz = p @ rgb + z for p
        vv = np.linspace(0,1,100)
        for k in range(3):
            plt.plot(vv, self.h(vv, v0=self.v0[k], gamma=self.gamma[k]), 'rgb'[k] + '-')
        for k in range(3):
            plt.plot(self.v[:, k], p[:, k], 'rgb'[k] + 'o')
        plt.xlabel('post-processed $v_k$', fontsize=18)
        plt.ylabel('activation', fontsize=18)
        plt.legend(['red','green','blue'], frameon=False)
        plt.show()

    def v2xyz(self, v):
        'convert post-processed values v_k to XYZ coordinates'
        p = [self.h(v=v[:,k], k=k) for k in range(3)]
        p = np.column_stack(p)
        return p @ rgb + z

    def xyz2v(self, xyz):
        'convert XYZ coordinates to post-processed values v_k'
        p = (xyz-z) @ np.linalg.inv(rgb)
        v = [self.hinv(p[:,k], k=k) for k in range(3)]
        return np.column_stack(v)

    def h(self, v, v0=None, gamma=None, k=None, maxout=True):
        'activation function with parameters v0 and gamma, for channel k (R=0, G=1, B=2); maxout determines whether maximum value is 1.0'
        if v0 is None: v0 = self.v0[k]
        if gamma is None: gamma = self.gamma[k]
        ub = 1 if maxout else np.inf
        v = np.array(v).clip(v0, ub)
        return ((v-v0)/(1-v0)) ** gamma

    def hinv(self, p, v0=None, gamma=None, k=None, maxout=True):
        'inverse of activation function with parameters v0 and gamma, for channel k (R=0, G=1, B=2); maxout determines whether maximum value is 1.0'
        if v0 is None: v0 = self.v0[k]
        if gamma is None: gamma = self.gamma[k]
        ub = 1 if maxout else np.inf
        p = np.array(p).clip(0, ub)
        return v0 + (1-v0)*(p ** (1/gamma))
