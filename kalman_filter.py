import math
import numpy as np
import matplotlib.pyplot as plt

class KalmanFilter:
    """
    Multi-dimensional Kalman filter.
    """
    def __init__(self, initial_observation):
        # For 2D X & Y pixel positions
        # print("initial observation: {}".format(initial_observation))
        # print("initial observation shape: {}".format(np.matrix(initial_observation).T.shape))
        self.z = [np.matrix(initial_observation).T]  # observations
        self.Q = np.matrix(np.eye(2)) * 1e-5

        # allocate space for arrays
        self.xhat = []  # a posteri estimate of x
        self.P = [np.matrix(np.eye(2))]  # a posteri error estimate
        self.xhatminus = []  # a priori estimate of x
        self.Pminus = []  # a priori error estimate
        self.K = []  # gain or blending factor
        self.R = 0.1 ** 2  # estimate of measurement variance, change to see effect

        # initial guesses
        self.xhat.append(self.z[-1])

    def update(self, z):
        self.z.append(z)
        # print("\nPredicted position (mu): {}".format(self.xhat[-1]))
        # print("\nActual position: {}".format(z))
        # print("\nCovariance (sigma): {}".format(self.P[-1]))

        # get the likelihood score
        L = self.calculate_likelihood(z, self.xhat[-1], self.P[-1])

        # time update
        self.xhatminus.append(self.xhat[-1])
        self.Pminus.append((self.P[-1] + self.Q))

        # measurement update
        self.K.append(self.Pminus[-1] / (self.Pminus[-1] + self.R))
        self.xhat.append(self.xhatminus[-1] + self.K[-1] * (self.z[-1] - self.xhatminus[-1]))
        self.P.append((1.0 - self.K[-1]) * self.Pminus[-1])

        return L

    def calculate_likelihood(self, x, mu, sigma):
        """
        Likelihood function for a multivariate normal distribution.
        https://en.wikipedia.org/wiki/Multivariate_normal_distribution#Likelihood_function
        """
        x = np.squeeze(x)
        mu = np.array(mu).ravel('F')
        if mu.shape != (2,):
            return 1.0

        sigma = np.matrix(sigma).reshape((2, 2))
        size = len(x)
        if size == len(mu) and (size, size) == sigma.shape:
            det = np.linalg.det(sigma)
            if det == 0:
                raise NameError("The covariance matrix can't be singular")

            norm_const = 1.0 / (math.pow((2 * math.pi), float(size) / 2) * math.pow(det, 1.0 / 2))
            x_mu = np.matrix(x - mu)
            inv = sigma.I
            result = math.pow(math.e, -0.5 * (x_mu * inv * x_mu.T))
            L = norm_const * result
            return L
        else:
            raise NameError("The dimensions of the input don't match")
