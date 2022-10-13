#!/usr/bin/env python
"""MHT"""

from .weighted_graph import WeightedGraph
# from .kalman_filter import TrackFilter
from .track_tree import TrackNode

import numpy as np
import itertools

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

    def __global_hypothesis(self, track_trees):
        """
        Generate a global hypothesis by finding the maximum weighted independent
        set of a graph with tracks as vertices, and edges between conflicting tracks.
        """
        logging.info("Calculating MWIS...")
        track_score_graph = WeightedGraph()
        conflict_dict = {}
        for index, track_tree in enumerate(track_trees):
            # Add the score to the graph
            track_score = track_tree.get_filter().get_track_score()
            track_score_graph.add_weighted_vertex(str(index), track_score)

            # Group tracks by conflict ID
            conflict_id = track_tree.get_conflict_id()
            conflict_id_key = "CID_" + str(conflict_id)
            try:
                conflict_dict[conflict_id_key].append(index)
            except KeyError:
                conflict_dict[conflict_id_key] = []
                conflict_dict[conflict_id_key].append(index)

        # An edge is created between any non-conflicting tracks. Thus, the maximum weighted clique is the
        # highest-scoring set of non-conflicting tracks.

        # Create the NxN adjacency matrix with all ones (all connected)
        vertex_count = len(track_trees)
        adjacency_mat = np.ones((vertex_count, vertex_count))
        # track_score_graph.set_adjacency_matrix(conflict_matrix)
        # track_trees.clear()
        for conflict_id in conflict_dict.keys():
            # Get all track vertices with this conflict
            conflict_vertices = conflict_dict[conflict_id]

            # Get all conflict combinations
            conflict_combos = [(a, b) for idx, a in enumerate(conflict_vertices) for b in conflict_vertices[idx + 1:]]

            # Get the reversed conflict combinations
            conflict_reversed_combos = [tuple(reversed(a)) for a in conflict_combos]

            # Get the same vertex conflicts
            edges_same_vertex = [(a, a) for a in conflict_vertices]

            # Concatenate into a single list
            all_edges = conflict_combos + conflict_reversed_combos + edges_same_vertex

            # Add 0's for all conflicting tracks
            for v1, v2 in all_edges:
                try:
                    adjacency_mat[v1, v2] = 0
                except IndexError as e:
                    print("V1=", v1)
                    print("V2=", v2)
                    b=1

        # Solve for the maximum weighted clique
        track_score_graph.set_adjacency_matrix(adjacency_mat)
        mwis_ids = track_score_graph.run()

        # Return the solution track tree nodes
        solution_trees = [track_trees[i] for i in mwis_ids]
        logging.info("MWIS complete.")

        return solution_trees

    @property
    def run(self):
        assert len(self.__detections)
        logging.info("Generating track trees...")
        track_trees = []
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
        conflict_id = 0  # Unique value for each detection conflict
        while self.__detections:
            detections = self.__detections.pop(0)
            logging.info("Frame {}: {} detections".format(frame_index, len(detections)))
            # updated_parent_nodes = []  # Contains all tree nodes created for this detection

            # Enumerate each CSV row, where 'index' is the detection ID, and 'detection' is its U,V coordinate
            detection_trees = []
            for index, detection in enumerate(detections):
                # Nodes sharing this timepoint and detection are conflicting.
                # Thus, specify a unique non-zero conflict ID that nodes generated below will share.
                conflict_id += 1

                # Add branches to all previous trees
                for track_tree in track_trees:

                    # Create a node from the detection using this parent
                    detection_branch =\
                        TrackNode(frame_index, detection, conflict_id=conflict_id, parent=track_tree)

                    # Check that the Nmiss threshold is not exceeded
                    missed_detection_count = detection_branch.get_filter().get_missed_detection_count()
                    if missed_detection_count < nmiss:

                        # Create a branch from this detection
                        # track_tree.add_child(detection_branch)
                        detection_trees.append(detection_branch)

                        # Create a dummy branch if needed
                        if detection_branch.get_filter().get_detection() is not None:
                            dummy_branch = TrackNode(frame_index, None, parent=track_tree)
                            # track_tree.add_child(dummy_branch)
                            detection_trees.append(dummy_branch)

                # Create a new track tree for this detection
                new_track_tree =\
                    TrackNode(frame_index, detection, conflict_id=conflict_id, filter_params=filter_params, parent=None)
                detection_trees.append(new_track_tree)

            # Iterate the frame
            frame_index += 1

            # TODO: Bth: Sort branches by score, keep the top bth branches
            # First, sort by root ID
            root_dict = {}
            while detection_trees:
                track_tree = detection_trees.pop()
                root_id = track_tree.get_root_id()
                try:
                    root_dict[root_id].append(track_tree)
                except KeyError:
                    root_dict[root_id] = []
                    root_dict[root_id].append(track_tree)

            # Keep only highest scoring branches for each root node
            track_trees.clear()
            for track_id in root_dict.keys():
                # Get track scores from this root
                root_tracks = root_dict[track_id]
                track_scores = [x.get_filter().get_track_score() for x in root_tracks]

                # Keep only the top scoring branches
                top_branches_idx = np.argsort(track_scores)[-b_th:]
                top_children = [root_tracks[i] for i in top_branches_idx]
                track_trees.extend(top_children)


            # Compute the solution
            solution_trees = self.__global_hypothesis(track_trees)
            # if (frame_index % n_scan) == 0:
            #     solution_ids = self.__global_hypothesis(track_filters, conflict_matrix)
            #
            #     # Remove the non-solution tracks
            #     track_filters = track_filters[solution_ids]

            # TODO: N-pruning: Get the solution node at k-N frames, remove the other children for its parent
            # TODO: Find solution. Nodes in the solution at k-N are parents. Delete ones that don't have these parents.


        # TODO: Plot results

        logging.info("Generated {} solution track trees.".format(len(solution_trees)))
        logging.info("MHT complete.")

        return solution_coordinates

    def __get_detections(self):
        return self.__detections.pop()

