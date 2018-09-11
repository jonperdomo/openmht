#!/usr/bin/env python

import os
import sys
import getopt
import time
import csv
from copy import deepcopy

from track_tree import TrackTree
from weighted_graph import WeightedGraph


class OpenMHT:
    """
    Multiple hypothesis tracking.
    """
    def __init__(self, detections):
        self.detections = list(detections)
        self.frame_number = 0
        self.track_trees = []  # Track hypotheses for detections in each frame
        self.detection_count = 0
        self.graph = WeightedGraph()  # Graph with tracks as vertices
        self.final_mwis = None

    def global_hypothesis(self):
        """
        Generate a global hypothesis by finding the maximum weighted independent
        set of a graph with tracks as vertices, and edges between conflicting tracks.
        """
        print(f"\t\tGenerating the track tree graph...")
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

        print(f"\t\tCalculating the MWIS...")
        mwis_ids = self.graph.mwis()
        mwis_track_trees = [self.track_trees[i] for i in mwis_ids]

        self.final_mwis = mwis_ids  # TODO: Update __str__ to not rely on this

        return mwis_track_trees

    def get_detections(self):
        return self.detections.pop()

    def run(self):
        print(f"\tGenerating all track trees...")
        while self.detections:
            detections = self.detections.pop(0)

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
            self.frame_number += 1

        print(f"\tNumber of tracks: {len(self.track_trees)}")
        print("\tGenerating the global hypothesis...")

        final_track_trees = self.global_hypothesis()

        print("\tGlobal hypothesis complete.")

        return final_track_trees

    def __str__(self):
        results = "\n\n--------\nAll trees:"
        for i in range(len(self.track_trees)):
            results += "\nID: {}".format(i+1)
            results += str(self.track_trees[i])

        results += "\n\n--------\nResults:"
        for track_tree_id in self.final_mwis:
            track_tree = self.track_trees[track_tree_id]
            results += "\nID: {}".format(track_tree_id)
            results += str(track_tree)

        results += "\nCompleted."

        return results


def read_uv_csv(file_path, frame_max=100):
    """
    Read detections from a CSV.
    Expected column headers are:
    Frame number, U, V
    """
    print(f"Reading CSV: {file_path} ...")
    detections = []
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        current_frame = None
        detection_index = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
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

        print(f'Processed {line_count-1} detections.')
        print(f'Number of frames: {len(detections)}')

    return detections


def write_uv_csv(file_path, track_trees):
    """
    Write track trees to a CSV.
    Column headers are:
    Frame number, track number, U, V
    """
    print("Writing CSV: {} ...".format(file_path))

    # Compile the results
    csv_rows = []
    for i in range(len(track_trees)):
        track_tree = track_trees[i]
        detections = track_tree.get_detections()
        initial_frame = track_tree.get_frame_number()
        for j in range(len(detections)):
            frame = str(initial_frame + j)
            if detections[j] is None:
                u = v = 'None'
            else:
                u, v = [str(x) for x in detections[j]]

            csv_rows.append([frame, i+1, u, v])

    # Sort the results by frame number
    csv_rows.sort(key=lambda x: x[0])
    with open(file_path, 'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        writer.writerow(['frame', 'track', 'u', 'v'])
        writer.writerows(csv_rows)


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

    print("Input file is: ", input_file)
    print("Output file is: ", output_file)

    # Run
    start = time.time()

    # Read input data
    detections = read_uv_csv(input_file)

    # # -- Testing section --
    #
    # import numpy as np
    # frame_count = 2
    # dimensionality = 2
    #
    # # Truth values for 3 objects
    # truth_values = [[0, 0], [10, 10], [15, 15]]
    # detections = np.zeros((frame_count, len(truth_values), dimensionality))
    # for i in range(len(truth_values)):
    #     detections[:, i] = np.random.normal(truth_values[i], 0.1, size=(frame_count, dimensionality))
    #
    # print("Detections:\n{}".format(detections))
    # # -- End testing section --

    mht = OpenMHT(detections)
    track_trees = mht.run()
    # print(mht)
    write_uv_csv(output_file, track_trees)
    end = time.time()
    elapsed_seconds = end - start
    print("Elapsed time (s) {0:.2f}".format(elapsed_seconds))

    elapsed_formatted = time.strftime('%H:%M:%S', time.gmtime(elapsed_seconds))
    print(elapsed_formatted)


if __name__ == "__main__":
    main(sys.argv[1:])
