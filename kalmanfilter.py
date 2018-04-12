import math
import numpy as np
import matplotlib.pyplot as plt

class KalmanFilter:
    """
    Multi-dimensional Kalman filter.
    """
    def __init__(self, initial_observation):
        # For 2D X & Y pixel positions
        print("initial observation: {}".format(initial_observation))
        self.z = [np.matrix(initial_observation).T]  # observations
        # self.Q = 1e-5  # process variance
        self.Q = np.matrix(np.eye(2)) * 1e-5

        # allocate space for arrays
        self.xhat = []  # a posteri estimate of x
        # self.P = []  # a posteri error estimate
        # self.P = []  # a posteri error estimate
        self.P = [np.matrix(np.eye(2))]  # a posteri error estimate
        self.xhatminus = []  # a priori estimate of x
        self.Pminus = []  # a priori error estimate
        self.K = []  # gain or blending factor
        self.R = 0.1 ** 2  # estimate of measurement variance, change to see effect

        # initial guesses
        self.xhat.append(initial_observation)
        # self.P.append(np.repeat(1.0, len(initial_observation)))
        self.k = 0  # iteration

    def update(self, z):
        self.z.append(z)
        print("\nPredicted position (mu): {}".format(self.xhat[-1]))
        print("Actual position: {}".format(z))
        print("Covariance (sigma): {}".format(self.P[-1]))

        # time update
        self.xhatminus.append(self.xhat[-1])
        self.Pminus.append((self.P[-1] + self.Q))

        # measurement update
        self.K.append(self.Pminus[-1] / (self.Pminus[-1] + self.R))
        self.xhat.append(self.xhatminus[-1] + self.K[-1] * (self.z[-1] - self.xhatminus[-1]))
        self.P.append((1 - self.K[-1]) * self.Pminus[-1])

    def calculate_likelihood(self, x, mu, sigma):
        """
        Likelihood function for a multivariate normal distribution.
        https://en.wikipedia.org/wiki/Multivariate_normal_distribution#Likelihood_function
        """
        k = 2  # dimensions
        L = -0.5(np.log(np.abs(sigma))) + (x-mu).T * np.linalg.inv(sigma) * (x-mu) + k * np.log(2*math.pi)
        print("Likelihood: {}".format(L))
