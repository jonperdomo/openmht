"""
Generate a random 2D test for MHT.
"""
import numpy as np
from openmht import OpenMHT


def get_test_detections():
    """
    :return: An array of randomly-generated detections (ijk) for each frame.
    """
    frame_count = 10
    detection_count = 3
    dimensionality = 2
    detections = np.zeros((frame_count, detection_count, dimensionality))

    # Truth values for 3 objects
    truth_values = [[0, 0], [10, 10], [20, 20]]
    for i in range(len(truth_values)):
        detections[:, i] = np.random.normal(truth_values[i], 0.1, size=(frame_count, dimensionality))

    # print("Detections: {}".format(detections))
    return detections

if __name__ == "__main__":
    test_points = get_test_detections()
    mht = OpenMHT(test_points)
    # mht.run()
