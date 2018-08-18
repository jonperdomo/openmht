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
        pass
        # x = np.matrix(z).reshape((self.dims, 1))
        # self.z.append(x)
        # # print("\nPredicted position (mu): {}".format(self.xhat[-1]))
        #
        # # time update
        # self.xhatminus.append(mu)
        # Pminus = sigma + self.Q
        # self.Pminus.append(Pminus)
        #
        # # measurement update
        # K = sigma / (sigma + self.R)
        # self.K.append(K)
        #
        # xhat_a = mu + K
        # print("a shape: {}".format(xhat_a.shape))
        # xhat_b = x - mu
        # print("b shape: {}".format(xhat_b.shape))
        # xhat = np.matrix(xhat_a) * np.matrix(xhat_b).reshape((self.dims, 1))
        # self.xhat.append(xhat)
        #
        # P = (1.0 - K) * Pminus
        # self.P.append(P)
        #
        # # self.xhat.append(self.xhatminus[-1] + self.K[-1] * (self.z[-1] - self.xhatminus[-1]))  # Check outputs here
        # # self.P.append((1.0 - self.K[-1]) * self.Pminus[-1])
        #
        # return L

    def calculate_likelihood(self, x, mu, sigma):
        """
        Likelihood function for a multivariate normal distribution.
        https://en.wikipedia.org/wiki/Multivariate_normal_distribution#Likelihood_function
        sigma: k x k covariance matrix
        x: single observation
        mu: k-dimensional mean vector
        """
        assert x.shape == (self.dims, 1), "X shape did not match dimensions {}".format(x.shape)
        assert mu.shape == (self.dims, 1), "Mu shape did not match dimensions {}".format(mu.shape)
        assert sigma.shape == (self.dims, self.dims), "Sigma shape did not match dimensions {}".format(sigma.shape)
        print("Shapes: x: {}, mu: {}, sigma: {}".format(x, mu, sigma))

        ln_sigma = np.log(np.linalg.det(sigma))

        op2 = (x-mu).T

        op3 = op2 * np.linalg.inv(sigma)

        op4 = (x-mu)

        op5 = op3 * op4

        op6 = float(self.dims) * np.log(2. * np.pi)

        op7 = op5 + op6

        lnL = -0.5 * (ln_sigma + op7)

        # For testing my implementation above, compare with the result from the equivalent SciPy function (below)
        # X = np.array(x).flatten()
        # mean = np.array(mu).flatten()
        # L = multivariate_normal.logpdf(X, mean=mean, cov=sigma)

        print("done")

        return lnL
