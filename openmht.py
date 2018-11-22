#!/usr/bin/env python

import os
import sys
import getopt
import time
import csv
from copy import deepcopy

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

from weighted_graph import WeightedGraph
from kalman_filter import KalmanFilter


class OpenMHT:
    """
    Multiple hypothesis tracking.
    """
    def __init__(self, detections):
        self.detections = list(detections)

    def global_hypothesis(self, track_trees, conflicting_tracks):
        """
        Generate a global hypothesis by finding the maximum weighted independent
        set of a graph with tracks as vertices, and edges between conflicting tracks.
        """
        logging.info("Running MWIS on weighted track trees...\n")
        gh_graph = WeightedGraph()
        for tree_id, track_tree in track_trees.items():
            gh_graph.add_weighted_vertex(str(tree_id), track_tree.get_track_score())

        gh_graph.set_edges(conflicting_tracks)

        mwis_ids = gh_graph.mwis()
        logging.info("Completed MWIS.\n")

        return mwis_ids

    def generate_track_trees(self):
        logging.info("Generating track trees...\n")
        track_count = 0
        track_detections = {}
        coordinates = []  # Coordinates for all frame detections
        kalman_filters = {}
        frame_index = 0
        K = 1  # Frame look-back for track pruning
        solution_ids = []

        while self.detections:
            coordinates.append({})

            detections = self.detections.pop(0)
            # print(f"\nAdd detections: {detections}")
            new_tracks = []  # Tracks added from these detections
            for index, detection in enumerate(detections):
                detection_id = str(index)
                coordinates[-1][detection_id] = detection

                # Update existing branches
                for track_id in kalman_filters.keys():

                    # Copy and update the Kalman filter
                    track_tree = kalman_filters[track_id]
                    continued_branch = deepcopy(track_tree)
                    continued_branch.update(detection)

                    # Update track dictionaries
                    continued_track_id = str(track_count)

                    new_tracks.append((continued_track_id, continued_branch))
                    track_detections[continued_track_id] = track_detections[track_id] + [detection_id]
                    track_count += 1

                # Create new branch from the detection
                new_branch = KalmanFilter(detection)

                # Update track dictionaries
                new_track_id = str(track_count)
                new_tracks.append((new_track_id, new_branch))
                track_detections[new_track_id] = [''] * (frame_index) + [detection_id]
                track_count += 1

            # Update the previous filter with a dummy detection
            for track_id in kalman_filters.keys():
                kalman_filters[track_id].update(None)
                track_detections[track_id].append('')

            kalman_filters.update(new_tracks)

            # Prune subtrees that diverge from the solution_trees at frame k-N
            logging.info("Pruning branches...\n")
            prune_index = max(0, frame_index-K)
            conflicting_tracks = self.get_conflicting_tracks(track_detections)
            solution_ids = self.global_hypothesis(kalman_filters, conflicting_tracks)
            non_solution_ids = list(set(kalman_filters.keys()) - set(solution_ids))
            prune_ids = set()
            for solution_id in solution_ids:
                d_id = track_detections[solution_id][prune_index]
                if d_id != '':
                    for non_solution_id in non_solution_ids:
                        if d_id == track_detections[non_solution_id][prune_index]:
                            prune_ids.add(non_solution_id)

            for prune_id in prune_ids:
                track_detections.pop(prune_id)
                kalman_filters.pop(prune_id)

            logging.info(f"Pruned {len(prune_ids)} branches.\n")
            del prune_ids

            frame_index += 1

        logging.info("Track tree generation complete.\n")

        return solution_ids, track_detections, coordinates

    def get_conflicting_tracks(self, track_detections):
        conflicting_tracks = []
        track_ids = list(track_detections.keys())
        while track_ids:
            track_id = track_ids.pop()
            d_ids = track_detections[track_id]
            for test_track_id in track_ids:
                test_d_ids = track_detections[test_track_id]
                for i in range(len(d_ids)):
                    d_id = d_ids[i]
                    if d_id != '' and d_id == test_d_ids[i]:
                        conflicting_tracks.append((track_id, test_track_id))

        return conflicting_tracks

    def get_detections(self):
        return self.detections.pop()

    def run(self):
        assert len(self.detections)
        logging.info("Running MHT...\n")
        solution_ids, track_detections, coordinates = self.generate_track_trees()
        logging.info("Completed MHT.\n")

        return solution_ids, track_detections, coordinates


def read_uv_csv(file_path, frame_max=100):
    """
    Read detections from a CSV.
    Expected column headers are:
    Frame number, U, V
    """
    logging.info("Reading input CSV...\n")
    detections = []
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        current_frame = None
        detection_index = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                frame_number, u, v = int(row[0]), float(row[1]), float(row[2])
                if frame_number != current_frame:
                    detection_index = len(detections)
                    if detection_index == frame_max:
                        break

                    detections.append([])
                    current_frame = frame_number

                detections[detection_index].append([u, v])
                line_count += 1

        logging.info(f'Reading inputs complete. Processed {line_count-1} detections across {len(detections)} frames.\n')

    return detections


def write_uv_csv(file_path, track_ids, track_detections, coordinates):
    """
    Write track trees to a CSV.
    Column headers are:
    Frame number, track number, U, V
    """
    logging.info("Writing output CSV...\n")
    # Compile the results
    csv_rows = []
    for track_index in range(len(track_ids)):
        track_id = track_ids[track_index]
        detections = track_detections[track_id]
        for j in range(len(detections)):
            detection_id = detections[j]
            if detection_id:
                point = coordinates[j][detection_id]
                u, v = [str(x) for x in point]
            else:
                u = v = 'None'
            csv_rows.append([j, track_index, u, v])

    # Sort the results by frame number
    csv_rows.sort(key=lambda x: x[0])
    with open(file_path, 'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        writer.writerow(['frame', 'track', 'u', 'v'])
        writer.writerows(csv_rows)

    logging.info("CSV saved to {}\n".format(file_path))


def main(argv):
    input_file = ''
    output_file = ''

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])

    except getopt.GetoptError:
        print('openmht.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    # Parse arguments
    for opt, arg in opts:

        if opt == '-h':
            print('openmht.py -i <inputfile> -o <outputfile>')
            sys.exit()

        elif opt in ("-i", "--ifile"):
            input_file = arg

        elif opt in ("-o", "--ofile"):
            output_file = arg

    # Verify CSV file formats
    try:
        assert os.path.isfile(input_file), "Input file does not exist: {}".format(input_file)
        assert os.path.splitext(input_file)[-1].lower() == '.csv', "Input file is not CSV: {}".format(input_file)
        assert os.path.splitext(input_file)[-1].lower() == '.csv', "Output file is not CSV: {}".format(input_file)

    except AssertionError as e:
        print(e)
        sys.exit(2)

    logging.info(f"Input file is: {input_file}\n")
    logging.info(f"Output file is: {output_file}\n")

    # Read a list of detections
    detections = read_uv_csv(input_file)

    # Run MHT on detections
    start = time.time()
    mht = OpenMHT(detections)
    track_ids, track_detections, coordinates = mht.run()
    write_uv_csv(output_file, track_ids, track_detections, coordinates)
    end = time.time()
    elapsed_seconds = end - start
    logging.info("Elapsed time (seconds) {0:.3f}\n".format(elapsed_seconds))


if __name__ == "__main__":
    main(sys.argv[1:])
