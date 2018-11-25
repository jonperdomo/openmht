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
        for index, kalman_filter in enumerate(track_trees):
            gh_graph.add_weighted_vertex(str(index), kalman_filter.get_track_score())

        gh_graph.set_edges(conflicting_tracks)

        mwis_ids = gh_graph.mwis()
        logging.info("Completed MWIS.\n")

        return mwis_ids

    def generate_track_trees(self):
        logging.info("Generating track trees...\n")
        track_detections = []
        kalman_filters = []
        coordinates = []  # Coordinates for all frame detections
        frame_index = 0
        K = 1  # Frame look-back for track pruning
        solution_coordinates = []  # List of coordinates for each track

        while self.detections:
            coordinates.append({})
            detections = self.detections.pop(0)
            track_count = len(kalman_filters)
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

                # Create new branch from the detection
                kalman_filters.append(KalmanFilter(detection))
                track_detections.append([''] * frame_index + [detection_id])

            # Update the previous filter with a dummy detection
            for j in range(track_count):
                kalman_filters[j].update(None)
                track_detections[j].append('')

            # Prune subtrees that diverge from the solution_trees at frame k-N
            logging.info("Pruning branches...\n")
            prune_index = max(0, frame_index-K)
            conflicting_tracks = self.get_conflicting_tracks(track_detections)
            solution_ids = self.global_hypothesis(kalman_filters, conflicting_tracks)
            non_solution_ids = list(set(range(len(kalman_filters))) - set(solution_ids))
            prune_ids = set()
            del solution_coordinates[:]
            for solution_id in solution_ids:
                detections = track_detections[solution_id]
                track_coordinates = []
                for i in range(len(detections)):
                    if detections[i] == '':
                        track_coordinates.append(None)
                    else:
                        track_coordinates.append(coordinates[i][detections[i]])
                solution_coordinates.append(track_coordinates)

                d_id = track_detections[solution_id][prune_index]
                if d_id != '':
                    for non_solution_id in non_solution_ids:
                        if d_id == track_detections[non_solution_id][prune_index]:
                            prune_ids.add(non_solution_id)

            for k in sorted(prune_ids, reverse=True):
                del track_detections[k]
                del kalman_filters[k]

            frame_index += 1

        logging.info("Track tree generation complete.\n")

        return solution_coordinates

    def get_conflicting_tracks(self, track_detections):
        conflicting_tracks = []
        for i in range(len(track_detections)):
            for j in range(i + 1, len(track_detections)):
                left_ids = track_detections[i]
                right_ids = track_detections[j]
                for k in range(len(left_ids)):
                    if left_ids[k] != '' and right_ids[k] != '' and left_ids[k] == right_ids[k]:
                        conflicting_tracks.append((i, j))

        return conflicting_tracks

    def get_detections(self):
        return self.detections.pop()

    def run(self):
        assert len(self.detections)
        logging.info("Running MHT...\n")
        solution_coordinates = self.generate_track_trees()
        logging.info("Completed MHT.\n")

        return solution_coordinates


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


def write_uv_csv(file_path, solution_coordinates):
    """
    Write track trees to a CSV.
    Column headers are:
    Frame number, track number, U, V
    """
    logging.info("Writing output CSV...\n")
    csv_rows = []
    for i in range(len(solution_coordinates)):
        track_coordinates = solution_coordinates[i]
        for j in range(len(track_coordinates)):
            coordinate = track_coordinates[j]
            if coordinate is None:
                u = v = 'None'
            else:
                u, v = [str(x) for x in coordinate]

            csv_rows.append([j, i, u, v])

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
    solution_coordinates = mht.run()
    write_uv_csv(output_file, solution_coordinates)
    end = time.time()
    elapsed_seconds = end - start
    logging.info("Elapsed time (seconds) {0:.3f}\n".format(elapsed_seconds))


if __name__ == "__main__":
    main(sys.argv[1:])
