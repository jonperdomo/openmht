import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal

class KalmanFilter:
    """
    Multi-dimensional Kalman filter.
    """
    def __init__(self, initial_observation):
        # For 2D X & Y pixel positions
        # print("initial observation: {}".format(initial_observation))
        # print("initial observation shape: {}".format(np.matrix(initial_observation).T.shape))
        self.dims = 2

        x = np.matrix(initial_observation).reshape((self.dims, 1))
        self.z = [x]  # observations
        self.Q = np.matrix(np.eye(self.dims)) * 1e-5

        # allocate space for arrays
        self.xhat = [x]  # a posteri estimate of x
        self.P = [np.matrix(np.eye(self.dims))]  # a posteri error estimate        # print("\nActual position: {}".format(z))
        # print("\nCovariance (sigma): {}".format(self.P[-1]))

        # get the likelihood score
        mu = self.xhat[-1]
        sigma = self.P[-1]

        L = self.calculate_likelihood(x, mu, sigma)

        self.xhatminus = []  # a priori estimate of x
        self.Pminus = []  # a priori error estimate
        self.K = []  # gain or blending factor
        self.R = 0.1 ** 2  # estimate of measurement variance, change to see effect

    def update(self, z):

        # Time update
        x = np.matrix(z).reshape((self.dims, 1))
        mu = self.xhat[-1]
        sigma = self.P[-1] + self.Q

        L = self.calculate_likelihood(x, mu, sigma)

        self.z.append(x)
        self.xhatminus.append(mu)
        self.Pminus.append(sigma)

        # Measurement update
        K = sigma / (sigma + self.R)
        self.K.append(K)

        xhat = mu + K * (x - mu)
        self.xhat.append(xhat)

        I = np.matrix(np.eye(self.dims))  # identity matrix
        P = (I - K) * sigma
        self.P.append(P)

        return L

    def calculate_likelihood(self, x, mu, sigma):
        """
        Log-likelihood function for a multivariate normal distribution.
        https://en.wikipedia.org/wiki/Multivariate_normal_distribution#Likelihood_function
        sigma: k x k covariance matrix
        x: single observation
        mu: k-dimensional mean vector
        """
        assert x.shape == (self.dims, 1), "X shape did not match dimensions {}".format(x.shape)
        assert mu.shape == (self.dims, 1), "Mu shape did not match dimensions {}".format(mu.shape)
        assert sigma.shape == (self.dims, self.dims), "Sigma shape did not match dimensions {}".format(sigma.shape)
        # print("Shapes: x: {}, mu: {}, sigma: {}".format(x, mu, sigma))

        ln_sigma = np.log(np.linalg.det(sigma))
        # print("Sigma: {}".format(sigma))
        # print("Det: {}".format(np.linalg.det(sigma)))

        op2 = (x-mu).T

        op3 = op2 * np.linalg.inv(sigma)

        op4 = (x-mu)

        op5 = op3 * op4

        op6 = float(self.dims) * np.log(2. * np.pi)

        op7 = op5 + op6

        lnL = (-0.5 * (ln_sigma + op7)).item()

        # Compare with the result from the equivalent SciPy function (below)
        # L = multivariate_normal.logpdf(np.array(x).flatten(), mean=np.array(mu).flatten(), cov=sigma)

        # print("done")

        return lnL
