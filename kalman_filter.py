import numpy as np
# from scipy.stats import multivariate_normal

class KalmanFilter:
    """
    Kalman filter for 2D & 3D vectors.
    """
    def __init__(self, initial_observation):
        self.dims = len(initial_observation)
        x = np.matrix(initial_observation).reshape((self.dims, 1))
        self.z = [x]  # observations
        self.Q = np.matrix(np.eye(self.dims)) * 1e-5

        # allocate space for arrays
        self.xhat = [x]  # a posteri estimate of x
        self.P = [np.matrix(np.eye(self.dims))]  # a posteri error estimate

        self.xhatminus = []  # a priori estimate of x
        self.Pminus = []  # a priori error estimate
        self.K = []  # gain or blending factor
        self.R = 0.1 ** 2  # estimate of measurement variance, change to see effect

        self.image_area = 1000.0  # TODO: Replace with actual frame dimensions
        self.missed_detection_score = np.log(1. - (1. / self.image_area))
        self.mot = self.missed_detection_score
        self.scores = [(None, x, self.mot)]
        self.d_th = 1000  # Gating area

    def get_motion_score(self):
        """"""
        return self.mot

    def update(self, z):
        last_detection = self.z[-1]
        if z is None:
            mot = self.missed_detection_score
            self.scores.append((last_detection, z, mot))
            self.mot = mot

        else:
            # Time update
            x = np.matrix(z).reshape((self.dims, 1))
            mu = self.xhat[-1]
            sigma = self.P[-1] + self.Q
            d_squared = self.mahalanobis_distance(x, mu, sigma)

            # Gating
            if d_squared < self.d_th:
                return 0

            else:
                mot = self.motion_score(x, mu, sigma, d_squared)
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

                self.scores.append((last_detection, z, mot))
                self.mot = mot

        return mot

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

        ln_sigma = np.log(np.linalg.det(sigma))

        op2 = (x-mu).T

        op3 = op2 * np.linalg.inv(sigma)

        op4 = (x-mu)

        op5 = op3 * op4

        op6 = float(self.dims) * np.log(2. * np.pi)

        op7 = op5 + op6

        lnL = (-0.5 * (ln_sigma + op7)).item()

        # Compare with the result from the equivalent SciPy function (below)
        # L = multivariate_normal.logpdf(np.array(x).flatten(), mean=np.array(mu).flatten(), cov=sigma)

        return lnL

    def print_scores(self):
        for previous_detection, detection, score in self.scores:
            print("\nPrevious: {}\nDetection: {}\nScore:{}".format(previous_detection, detection, score))

    def motion_score(self, x, mu, sigma, d_squared):
        mot = (np.log(self.image_area/2.*np.pi) - .5 * np.log(np.linalg.det(sigma)) - d_squared / 2.).item()

        return mot

    def mahalanobis_distance(self, x, mu, sigma):
        assert x.shape == (self.dims, 1), "X shape did not match dimensions {}".format(x.shape)
        assert mu.shape == (self.dims, 1), "Mu shape did not match dimensions {}".format(mu.shape)
        assert sigma.shape == (self.dims, self.dims), "Sigma shape did not match dimensions {}".format(sigma.shape)

        d_squared = (mu-x).T * np.linalg.inv(sigma) * (mu-x)

        return d_squared
