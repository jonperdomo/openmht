import sys
# import kalmanfilter as kf


class OpenMHT:
    """
    Multiple hypothesis tracking.
    """
    def __init__(self, detections):
        self.detections = detections
        self.frame_count, _, self.dimensionality = self.detections.shape
        self.track_trees = []

    def global_hypothesis(self, trees):
        pass

    def run(self):
        pass