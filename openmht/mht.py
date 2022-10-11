#!/usr/bin/env python
"""MHT"""

from .weighted_graph import WeightedGraph
# from .kalman_filter import TrackFilter
from .track_tree import TrackNode

from copy import deepcopy
import numpy as np

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


__author__ = "Jon Perdomo"
__license__ = "GPL-3.0"
__version__ = "0.1.0"


class MHT:
    """
    Multiple hypothesis tracking.
    """
    def __init__(self, detections, params):
        self.__detections = list(detections)
        self.__params = params

    def __global_hypothesis(self, track_trees, conflict_matrix):
        """
        Generate a global hypothesis by finding the maximum weighted independent
        set of a graph with tracks as vertices, and edges between conflicting tracks.
        """
        logging.info("Calculating MWIS...")
        gh_graph = WeightedGraph()
        for index, kalman_filter in enumerate(track_trees):
            gh_graph.add_weighted_vertex(str(index), kalman_filter.get_track_score())

        gh_graph.set_adjacency_matrix(conflict_matrix)

        mwis_ids = gh_graph.run()
        logging.info("MWIS complete.")

        return mwis_ids

    def run(self):
        assert len(self.__detections)
        logging.info("Generating track trees...")
        track_detections = []
        track_filters = []
        frame_index = 0
        n_scan = self.__params.n  # Frame look-back for track pruning
        b_th = self.__params.bth  # Max. number of track tree branches
        nmiss = self.__params.nmiss  # Max. number of false observations in tracks
        solution_coordinates = []  # List of coordinates for each track

        # Kalman filter parameters
        filter_params = {
            "v": self.__params.v,
            "dth": self.__params.dth,
            "k": self.__params.k,
            "q": self.__params.q,
            "r": self.__params.r
            }

        # Track tree with root nodes containing each filter

        # List of conflicting nodes

        # TODO: Create track tree object simply for finding the frame and detection
        #  for the bth threshold

        # Generate trees and compute the solution
        previous_track_count = 0
        updated_track_count = 0
        parent_nodes = []

        # Counter for setting unique conflict IDs at child nodes
        # Printing out unique IDs at the end enables simple conflict comparison across trees
        conflict_id = 0  # 0 for no conflict
        while self.__detections:
            frame_index += 1
            detections = self.__detections.pop(0)
            logging.info("Frame {}: {} detections".format(frame_index, len(detections)))
            # updated_parent_nodes = []  # Contains all tree nodes created for this detection

            # Add a dummy branch for missing detections at this frame
            dummy_branches = []
            for parent_node in parent_nodes:
                # Create a dummy branch
                child_node = TrackNode(frame_index, None, parent=parent_node)

                # Check that the Nmiss threshold is not exceeded
                missed_detection_count = child_node.get_filter().get_missed_detection_count()
                if missed_detection_count < nmiss:
                    dummy_branch = deepcopy(parent_node)
                    dummy_branch.add_child(child_node)
                    dummy_branches.append(dummy_branch)

            # Enumerate each CSV row, where 'index' is the detection ID, and 'detection' is its U,V coordinate
            detection_branches = []
            for index, detection in enumerate(detections):
                # Nodes sharing this timepoint and detection are conflicting.
                # Thus, specify a unique non-zero conflict ID that nodes generated below will share.
                conflict_id += 1

                # Add branches to all previous trees
                for parent_node in parent_nodes:
                    # Create a node from the detection using this parent
                    child_node = TrackNode(frame_index, detection, conflict_id=conflict_id, parent=parent_node)

                    # Check that the Nmiss threshold is not exceeded
                    missed_detection_count = child_node.get_filter().get_missed_detection_count()
                    if missed_detection_count < nmiss:

                        # Create a branch from this detection
                        detection_branch = deepcopy(parent_node)
                        detection_branch.add_child(child_node)
                        detection_branches.append(detection_branch)

                # Create a new track tree for this detection
                detection_root_node = TrackNode(frame_index, detection, conflict_id=conflict_id, filter_params=filter_params, parent=None)
                detection_branches.append(detection_root_node)

            # Concatenate all new track trees
            parent_nodes = dummy_branches + detection_branches

            # Nmiss: When adding, check if None or outside gating area.
            # Return false if Nmiss is passed. Don't add node to parent as branch.
            # TODO: Bth: Sort branches by score, keep the top bth branches

            # TODO: Plot results

            # # Compute the solution
            # if (frame_index % n_scan) == 0:
            #     solution_ids = self.__global_hypothesis(track_filters, conflict_matrix)
            #
            #     # Remove the non-solution tracks
            #     track_filters = track_filters[solution_ids]

            # TODO: N-pruning: Get the solution node at k-N frames, remove the other children for its parent

        logging.info("Generated {} track trees.".format(len(track_filters)))
        logging.info("MHT complete.")

        return solution_coordinates

    def __get_detections(self):
        return self.__detections.pop()

