#!/usr/bin/env python
"""Kalman Filter for track motion scores"""

import numpy as np

__author__ = "Jon Perdomo"
__license__ = "GPL-3.0"
__version__ = "0.1.0"


class TrackFilter:
    """
    Track tree with Kalman filters.
    """
    def __init__(self, initial_frame, initial_observation, filter_params): #, v=307200, dth=1000, k=0, q=1e-5, r=0.01):
        # Kalman filter parameters
        self.__dims = len(initial_observation)
        x = np.matrix(initial_observation).reshape((self.__dims, 1))
        self.__Q = np.matrix(np.eye(self.__dims)) * filter_params['q']
        self.__xhat = x  # a posteri estimate of x
        self.__P = np.matrix(np.eye(self.__dims))  # a posteri error estimate
        self.__K = filter_params['k']  # gain or blending factor
        self.__R = filter_params['r']  # estimate of measurement variance, change to see effect

        self.__image_area = filter_params['v']
        self.__missed_detection_score = np.log(1. - (1. / self.__image_area))
        self.__track_score = self.__missed_detection_score
        self.__d_th = filter_params['dth']

        # List of detection frame number and coordinate data
        frame_key = self.__format_frame_key(initial_frame)
        self.__frame_detection_data = {frame_key: [initial_observation]}

    def get_track_score(self):
        return self.__track_score

    def add_detection(self, frame_index, z):
        # # Update the frame detection data for this filter
        # frame_key = self.__format_frame_key(frame_index)
        # try:
        #     self.__frame_detection_data[frame_key].append(z)
        # except KeyError:
        #     self.__frame_detection_data[frame_key] = [z]
        # TODO: Add to tree: Frame/detection ID and motion score (=single node)
        #  Only the root has the filter.

        # Update the track's motion score via the Kalman Filter
        if z is None:
            self.__track_score += self.__missed_detection_score

        else:
            # Time update
            x = np.matrix(z).reshape((self.__dims, 1))
            mu = self.__xhat
            sigma = self.__P + self.__Q
            d_squared = self.__mahalanobis_distance(x, mu, sigma)

            # Gating
            if d_squared <= self.__d_th:
                self.__track_score += self.__motion_score(sigma, d_squared)

                # Measurement update
                self.__K = sigma / (sigma + self.__R)
                self.__xhat = mu + self.__K * (x - mu)

                I = np.matrix(np.eye(self.__dims))  # identity matrix
                self.__P = (I - self.__K) * sigma

    def __format_frame_key(self, frame_number):
        frame_key = 'F' + str(frame_number)

        return frame_key

    def __motion_score(self, sigma, d_squared):
        mot = (np.log(self.__image_area/2.*np.pi) - .5 * np.log(np.linalg.det(sigma)) - d_squared / 2.).item()

        return mot

    def __mahalanobis_distance(self, x, mu, sigma):
        assert x.shape == (self.__dims, 1), "X shape did not match dimensions {}".format(x.shape)
        assert mu.shape == (self.__dims, 1), "Mu shape did not match dimensions {}".format(mu.shape)
        assert sigma.shape == (self.__dims, self.__dims), "Sigma shape did not match dimensions {}".format(sigma.shape)

        d_squared = (mu-x).T * np.linalg.inv(sigma) * (mu-x)

        return d_squared
