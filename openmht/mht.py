#!/usr/bin/env python

from .weighted_graph import WeightedGraph
from .kalman_filter import KalmanFilter

from copy import deepcopy

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


__author__ = "Jon Perdomo"
__license__ = "GPL-3.0"
__version__ = "0.1.0"


class MHT:
    """Multiple Hypothesis Tracking."""
    def __init__(self, detections, params):
        self.__detections = list(detections)
        self.__params = params

    def __global_hypothesis(self, track_trees, conflicting_tracks):
        """
        Generate a global hypothesis by finding the maximum weighted independent
        set of a graph with tracks as vertices, and edges between conflicting tracks.
        """
        logging.info("Calculating MWIS...")
        gh_graph = WeightedGraph()
        for index, kalman_filter in enumerate(track_trees):
            gh_graph.add_weighted_vertex(str(index), kalman_filter.get_track_score())

        gh_graph.set_edges(conflicting_tracks)

        mwis_ids = gh_graph.mwis()
        logging.info("MWIS complete.")

        return mwis_ids

    def __generate_track_trees(self):
        """ Run the MHT algorithm. """

        logging.info("Generating track trees...")
        track_detections = []
        kalman_filters = []
        coordinates = []  # Coordinates for all frame detections
        frame_index = 0
        n_scan = int(self.__params.get('n'))  # Frame look-back for pruning
        b_th = self.__params.get('bth')  # Max. number of track tree branches
        nmiss = self.__params.get('nmiss')  # Max. number of false observations in tracks

        # Kalman filter parameters
        v = self.__params.get('v')
        dth = self.__params.get('dth')
        k = self.__params.get('k')
        q = self.__params.get('q')
        r = self.__params.get('r')

        # b_th = int(self.__params.pop())  # Max. number of track tree branches
        # nmiss = self.__params.nmiss  # Max. number of false observations in tracks
        solution_coordinates = []  # Coordinates for the solution track trees

        # Create a conflict matrix for each frame. Each row is a detection, each column is a track.
        conflict_matrix = []

        # Generate trees and compute the solution
        while self.__detections:
            coordinates.append({})
            detections = self.__detections.pop(0)
            logging.info("Frame {}: {} detections".format(frame_index, len(detections)))
            track_count = len(kalman_filters)
            for index, detection in enumerate(detections):
                detection_id = str(index)
                coordinates[frame_index][detection_id] = detection

                # Update existing branches
                for i in range(track_count):
                    # Copy and update the Kalman filter
                    track_tree = kalman_filters[i]
                    continued_branch = deepcopy(track_tree)
                    continued_branch._update(detection)
                    kalman_filters.append(continued_branch)
                    track_detections.append(track_detections[i] + [detection_id])

                # Create new branch from the detection
                kalman_filters.append(KalmanFilter(detection, v=v, dth=dth, k=k, q=q, r=r))
                track_detections.append([''] * frame_index + [detection_id])

            # Update the previous filter with a dummy detection
            for j in range(track_count):
                kalman_filters[j]._update(None)
                track_detections[j].append('')

            # Prune subtrees that diverge from the solution_trees at frame k-N
            prune_index = max(0, frame_index-n_scan)
            conflicting_tracks = self.__get_conflicting_tracks(track_detections)
            solution_ids = self.__global_hypothesis(kalman_filters, conflicting_tracks)
            non_solution_ids = list(set(range(len(kalman_filters))) - set(solution_ids))
            prune_ids = set()
            del solution_coordinates[:]
            for solution_id in solution_ids:
                detections = track_detections[solution_id]
                track_coordinates = []
                for i, detection in enumerate(detections):
                    if detection == '':
                        track_coordinates.append(None)
                    else:
                        track_coordinates.append(coordinates[i][detection])
                solution_coordinates.append(track_coordinates)

                d_id = track_detections[solution_id][prune_index]
                if d_id != '':
                    for non_solution_id in non_solution_ids:
                        if d_id == track_detections[non_solution_id][prune_index]:
                            prune_ids.add(non_solution_id)

            for k in sorted(prune_ids, reverse=True):
                del track_detections[k]
                del kalman_filters[k]

            logging.info("Pruned {} branch(es) at frame N-{}".format(len(prune_ids), n_scan))

            frame_index += 1

        logging.info("Generated {} track trees.".format(len(kalman_filters)))

        return solution_coordinates

    def __get_conflicting_tracks(self, track_detections):
        conflicting_tracks = []
        for i in range(len(track_detections)):
            for j in range(i + 1, len(track_detections)):
                left_ids = track_detections[i]
                right_ids = track_detections[j]
                for k in range(len(left_ids)):
                    if left_ids[k] != '' and right_ids[k] != '' and left_ids[k] == right_ids[k]:
                        conflicting_tracks.append((i, j))

        return conflicting_tracks

    def run(self):
        assert len(self.__detections)
        solution_coordinates = self.__generate_track_trees()
        logging.info("MHT complete.")

        return solution_coordinates
    