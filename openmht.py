import sys
# import kalmanfilter as kf
import numpy as np
from copy import deepcopy
from tracktree import TrackTree
from graph import Graph


class OpenMHT:
    """
    Multiple hypothesis tracking.
    """
    def __init__(self, detections):
        self.detections = list(detections)
        self.frame_count, _, self.dimensionality = detections.shape
        self.frame_number = 0
        self.track_trees = []  # Track hypotheses for detections in each frame
        self.detection_count = 0
        self.graph = Graph()  # Graph with tracks as vertices

    def global_hypothesis(self):
        print("# of tracks: {}".format(len(self.track_trees)))
        t1 = self.track_trees[0]
        count = 0
        for i in range(1, len(self.track_trees)):
            if t1.has_conflict(self.track_trees[i]):
                pass
            else:
                count += 1
        print("Non-conflicts: {}".format(count))

    def get_detections(self):
        return self.detections.pop()

    def run(self):
        print("Number of frames: {}".format(len(self.detections)))

        while self.detections:
            self.frame_number += 1
            detections = self.detections.pop()
            print("Number of detections: {}".format(len(detections)))

            # Update the previous track trees from the detections
            updated_track_trees = []
            for track_tree in self.track_trees:
                # Generate updated track trees from the detections
                for i in range(len(detections)):
                    detection, vertex_id = detections[i], str(self.detection_count + i)
                    track_tree_copy = deepcopy(track_tree)
                    track_tree_copy.add_detection(detection, vertex_id)
                    updated_track_trees.append(track_tree_copy)

                # Add a dummy observation to account for missing detections
                track_tree.add_detection(None, str(self.detection_count + len(detections)))
            self.track_trees.extend(updated_track_trees)

            # Generate new track trees from the detections
            for i in range(len(detections)):
                detection, vertex_id = detections[i], str(self.detection_count + i)
                track_tree = TrackTree(self.frame_number)
                track_tree.add_detection(detection, vertex_id)
                self.track_trees.append(track_tree)

            self.detection_count += len(detections) + 1  # +1 for the missing detection ID

        print("Done")
        # for i in range(len(self.track_trees)):
        #     # print("\nTrack {}".format(i))
        #     self.track_trees[i].print_data()

        gh = self.global_hypothesis()
