import numpy as np
# from scipy.stats import multivariate_normal


class KalmanFilter:
    """
    Kalman filter for 2D & 3D vectors.
    """
    def __init__(self, initial_observation, image_area=307200, gating_area=1000, k=0, q=1e-5, r=0.01):
        self.dims = len(initial_observation)
        x = np.matrix(initial_observation).reshape((self.dims, 1))
        self.Q = np.matrix(np.eye(self.dims)) * q
        self.xhat = x  # a posteri estimate of x
        self.P = np.matrix(np.eye(self.dims))  # a posteri error estimate
        self.K = k  # gain or blending factor
        self.R = r  # estimate of measurement variance, change to see effect

        self.image_area = image_area
        self.missed_detection_score = np.log(1. - (1. / self.image_area))
        self.track_score = self.missed_detection_score
        self.d_th = gating_area

    def get_track_score(self):
        return self.track_score

    def update(self, z):
        if z is None:
            self.track_score += self.missed_detection_score

        else:
            # Time update
            x = np.matrix(z).reshape((self.dims, 1))
            mu = self.xhat
            sigma = self.P + self.Q
            d_squared = self.mahalanobis_distance(x, mu, sigma)

            # Gating
            if d_squared <= self.d_th:
                self.track_score += self.motion_score(sigma, d_squared)

                # Measurement update
                self.K = sigma / (sigma + self.R)
                self.xhat = mu + self.K * (x - mu)

                I = np.matrix(np.eye(self.dims))  # identity matrix
                self.P = (I - self.K) * sigma

    def motion_score(self, sigma, d_squared):
        mot = (np.log(self.image_area/2.*np.pi) - .5 * np.log(np.linalg.det(sigma)) - d_squared / 2.).item()

        return mot

    def mahalanobis_distance(self, x, mu, sigma):
        assert x.shape == (self.dims, 1), "X shape did not match dimensions {}".format(x.shape)
        assert mu.shape == (self.dims, 1), "Mu shape did not match dimensions {}".format(mu.shape)
        assert sigma.shape == (self.dims, self.dims), "Sigma shape did not match dimensions {}".format(sigma.shape)

        d_squared = (mu-x).T * np.linalg.inv(sigma) * (mu-x)

        return d_squared
