#!/usr/bin/env python

"""Multiple Hypothesis Tracking module."""

# from .weighted_graph import WeightedGraph
# from .kalman_filter import KalmanFilter
from weighted_graph import WeightedGraph
from kalman_filter import KalmanFilter

from copy import deepcopy

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


__author__ = "Jon Perdomo"
__license__ = "GPL-3.0"


class MHT:
    """Main class for the MHT algorithm."""
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
        track_detections = []  # Detections for all frame tracks
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

        # Generate trees and compute the solution
        while self.__detections:
            coordinates.append({})
            detections = self.__detections.pop(0)
            logging.info("Frame {}: {} detections".format(frame_index, len(detections)))
            track_count = len(kalman_filters)
            branches_added = 0  # Total number of branches added to all the track tree at this frame
            for index, detection in enumerate(detections):
                detection_id = str(index)
                coordinates[frame_index][detection_id] = detection

                # Update existing branches
                for i in range(track_count):
                    # Copy and update the Kalman filter
                    track_tree = kalman_filters[i]
                    continued_branch = deepcopy(track_tree)
                    continued_branch.update(detection)
                    kalman_filters.append(continued_branch)
                    track_detections.append(track_detections[i] + [detection_id])
                    branches_added += 1

                # Create a new branch with the current detection:

                # Create a new Kalman filter
                kalman_filters.append(KalmanFilter(detection, v=v, dth=dth, k=k, q=q, r=r, nmiss=nmiss))

                # Create a new track detection list (list of detection IDs for each frame)
                # Each track detection list is a branch of the track tree, and is used to
                # quickly determine conflicting tracks and to query the Kalman filter list for
                # the global hypothesis.
                # First, create a list of empty strings for each frame prior to the current frame.
                # Then, append the detection ID to the current frame.
                track_detection_id = [''] * frame_index + [detection_id]
                track_detections.append(track_detection_id)
                branches_added += 1

            # Update the previous filter with a dummy detection
            prune_ids = set()
            nmiss_prune_count = 0
            for j in range(track_count):

                # Update with dummy detection coordinates
                update_success = kalman_filters[j].update(None)

                # Append a dummy detection ID to the track detection list
                track_detections[j].append('')

                # If the track was pruned, add it to the prune list
                if not update_success:
                    prune_ids.add(j)
                    nmiss_prune_count += 1
            
            # Log the N-miss pruning
            if nmiss_prune_count > 0:
                logging.info("[nmiss] Pruned %d branch(es) at frame %d", nmiss_prune_count, frame_index)

            # Prune subtrees that diverge from the solution_trees at frame k-N
            prune_index = max(0, frame_index-n_scan)
            conflicting_tracks = self.__get_conflicting_tracks(track_detections)
            solution_ids = self.__global_hypothesis(kalman_filters, conflicting_tracks)
            non_solution_ids = list(set(range(len(kalman_filters))) - set(solution_ids))
            del solution_coordinates[:]
            n_scan_prune_count = 0
            for solution_id in solution_ids:
                detections = track_detections[solution_id]  # Detection IDs for the solution track tree
                track_coordinates = []
                for i, detection in enumerate(detections):
                    if detection == '':
                        track_coordinates.append(None)
                    else:
                        track_coordinates.append(coordinates[i][detection])
                solution_coordinates.append(track_coordinates)

                # Prune branches that diverge from the solution track tree at frame k-N
                d_id = track_detections[solution_id][prune_index]
                if d_id != '':
                    for non_solution_id in non_solution_ids:
                        if d_id == track_detections[non_solution_id][prune_index]:
                            prune_ids.add(non_solution_id)
                            n_scan_prune_count += 1

            # Log the N-scan pruning
            if n_scan_prune_count > 0:
                logging.info("[nscan] Pruned %d branch(es) at frame N-%d", n_scan_prune_count, n_scan)

            # Prune branches that exceed the maximum number of branches and keep only the top b_th branches
            branch_count = branches_added - len(prune_ids)
            if branch_count > b_th:
                
                # Get the top b_th branches by score
                branch_scores = []
                for i, track_tree in enumerate(kalman_filters):
                    if i not in prune_ids:
                        branch_scores.append((i, track_tree.get_track_score()))

                # Sort by score and keep the top b_th branches
                branch_scores.sort(key=lambda x: x[1], reverse=True)
                prune_ids.update([x[0] for x in branch_scores[b_th:]])

                # Log the B-threshold pruning
                b_th_prune_count = branches_added - len(prune_ids)
                if b_th_prune_count > 0:
                    logging.info("[bth] Pruned %d branch(es) using B-threshold.", b_th_prune_count)

            # Prune tracks identified by n-scan, n-miss, and b-threshold
            for k in sorted(prune_ids, reverse=True):
                del track_detections[k]
                del kalman_filters[k]
            
            frame_index += 1

        logging.info("Generated %d track trees", len(solution_coordinates))

        return solution_coordinates

    def __get_conflicting_tracks(self, track_detections):
        # Create a conflict matrix for each frame. Each row is a pair of conflicting tracks by index.
        conflicting_tracks = []
        for detections_a in track_detections:
            for detections_b in track_detections:
                if detections_a != detections_b:
                    conflicting = False
                    for frame_index, detection in enumerate(detections_a):
                        if detection != '' and detection == detections_b[frame_index]:
                            conflicting = True
                            break

                    if conflicting:
                        conflicting_tracks.append((track_detections.index(detections_a), track_detections.index(detections_b)))

        return conflicting_tracks

    def run(self):
        """Run the MHT algorithm."""
        assert len(self.__detections) > 0, "No detections provided."
        solution_coordinates = self.__generate_track_trees()
        logging.info("MHT complete.")

        return solution_coordinates
    