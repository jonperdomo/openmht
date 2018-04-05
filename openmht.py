"""
Input arguments:
(1) File path of the input CSV with detections.
(2) Parameters for the Kalman filter.
"""

import sys
import kalmanfilter as kf


def main(argv):
    filepath = argv[0]
    print("Detections: {}".format(filepath))
    print("\nDone.")


def global_hypothesis(trees):
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
