import sys
# import kalmanfilter as kf
import numpy as np
from copy import deepcopy
from tracktree import TrackTree


class OpenMHT:
    """
    Multiple hypothesis tracking.
    """
    def __init__(self, detections):
        self.detections = list(detections)
        self.frame_count, _, self.dimensionality = detections.shape
        self.frame_number = 0
        self.track_trees = []  # Track hypotheses for detections in each frame
        # self.vertex_ids = []  # Assign a vertex ID for each detection (A-Z)
        self.detection_count = 0

    def global_hypothesis(self, trees):
        pass

    def get_detections(self):
        return self.detections.pop()

    # def get_vertex_id(self):
    #     ord_index = ord('a') + len(self.vertex_ids)
    #     ord_length = ord('z') - ord('a')
    #     ord_factor = int((ord_index-ord('a')) / float(ord_length))
    #     ord_index -= (ord_length * ord_factor)
    #     vertex_id = chr(ord_index) * (ord_factor+1)
    #
    #     return vertex_id

    def run(self):
        print("Number of frames: {}".format(len(self.detections)))
        # for i in range(200):
        #     vid = self.get_vertex_id()
        #     self.vertex_ids.append(vid)
        #     print(vid)

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
        for i in range(len(self.track_trees)):
            # print("\nTrack {}".format(i))
            self.track_trees[i].print_data()
