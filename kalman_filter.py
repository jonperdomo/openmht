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

        _, evec_sigma = np.linalg.eig(np.abs(sigma))
        ln_sigma = np.linalg.inv(evec_sigma)
        np.fill_diagonal(ln_sigma, np.log(ln_sigma.diagonal()))

        op2 = (x-mu).T

        op3 = op2 * np.linalg.inv(sigma)

        op4 = (x-mu)

        op5 = op3 * op4

        op6 = 3. * np.log(np.pi)

        op7 = op5 + op6

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
            print("L: {}".format(L))
            return L
        else:
            raise NameError("The dimensions of the input don't match")

    def calculate_likelihood_DEPR(self, x, mu, sigma):
        """
        Likelihood function for a multivariate normal distribution.
        https://en.wikipedia.org/wiki/Multivariate_normal_distribution#Likelihood_function
        """
        print("Shapes: x: {}, mu: {}, sigma: {}".format(x, mu, sigma))
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
            print("L: {}".format(L))
            return L
        else:
            raise NameError("The dimensions of the input don't match")
