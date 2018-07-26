import sys
# import kalmanfilter as kf
import numpy as np
from copy import deepcopy
from track_tree import TrackTree
from weighted_graph import WeightedGraph


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
        self.graph = WeightedGraph()  # Graph with tracks as vertices

    def global_hypothesis(self):
        '''
        Generate a global hypothesis by finding the maximum weighted independent
        set of a graph with tracks as vertices, and edges between conflicting tracks.
        '''
        print("# of tracks: {}".format(len(self.track_trees)))
        all_trees = list(self.track_trees)
        tree_count = len(all_trees)
        vertex_ids = dict(zip(all_trees, [str(i) for i in range(tree_count)]))  # Generate the vertex ID's

        while all_trees:

            next_tree = all_trees.pop()
            vertex_id = vertex_ids[next_tree]
            motion_score = next_tree.get_motion_score()
            self.graph.add_weighted_vertex(vertex_id, motion_score)

            for i in range(len(all_trees)):
                available_tree = all_trees[i]
                if next_tree.has_conflict(available_tree):
                    edge_vertex_id = vertex_ids[available_tree]
                    self.graph.add_edge({vertex_id, edge_vertex_id})

        self.print_data()

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

        self.global_hypothesis()


    def print_data(self):
        print("\nFinal MHT graph:")
        print(self.graph)
        mwis_ids = self.graph.mwis()
        print("MWIS: {}".format(mwis_ids))
        for track_tree_id in mwis_ids:
            track_tree = self.track_trees[track_tree_id]
            track_tree.print_data()
