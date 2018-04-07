import numpy as np
import matplotlib.pyplot as plt

class KalmanFilter:
    """
    Multi-dimensional Kalman filter.
    """
    def __init__(self, initial_observation):
        self.z = [initial_observation]  # observations
        self.Q = 1e-5  # process variance

        # allocate space for arrays
        self.xhat = []  # a posteri estimate of x
        self.P = []  # a posteri error estimate
        self.xhatminus = []  # a priori estimate of x
        self.Pminus = []  # a priori error estimate
        self.K = []  # gain or blending factor
        self.R = 0.1 ** 2  # estimate of measurement variance, change to see effect

        # initial guesses
        self.xhat.append(initial_observation)
        self.P.append(np.repeat(1.0, len(initial_observation)))
        self.k = 0  # iteration

    def update(self, z):
        self.z.append(z)
        print("\nPredicted position: {}".format(self.xhat[-1]))
        print("Actual position: {}\n".format(z))

        # time update
        self.xhatminus.append(self.xhat[-1])
        self.Pminus.append((self.P[-1] + self.Q))

        # measurement update
        self.K.append(self.Pminus[-1] / (self.Pminus[-1] + self.R))
        self.xhat.append(self.xhatminus[-1] + self.K[-1] * (self.z[-1] - self.xhatminus[-1]))
        self.P.append((1 - self.K[-1]) * self.Pminus[-1])
