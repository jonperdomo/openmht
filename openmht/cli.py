#!/usr/bin/env python
"""CLI"""

from .mht import MHT
from pathlib import Path

import sys
import argparse
import time
import csv

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

__author__ = "Jon Perdomo"
__license__ = "GPL-3.0"
__version__ = "0.1.0"


def read_uv_csv(file_path):
    """
    Read detections from a CSV.
    Expected column headers are:
    Frame number, U, V
    Where U,V is the location of a single detection at that frame.
    :return
        Nested array where the first dimension is the frame number, and the second dimension is a 2D list of each detection for that frame (U,V). Thus, detections can be accessed by frame number.

    """
    logging.info("Reading input CSV...")
    detections = []
    with open(file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        current_frame = None
        detection_index = 0

        # Loop through each row
        next(csv_reader)  # Skip the header
        for row in csv_reader:
            frame_number, u, v = int(row[0]), float(row[1]), float(row[2])
            if frame_number != current_frame:
                detection_index = len(detections)
                detections.append([])
                current_frame = frame_number

            detections[detection_index].append([u, v])
            line_count += 1

        logging.info(f'Reading inputs complete. Processed {line_count-1} detections across {len(detections)} frames.')

    return detections


def write_uv_csv(file_path, solution_coordinates):
    """
    Write track trees to a CSV.
    Column headers are:
    Frame number, track number, U, V
    """
    logging.info("Writing output CSV...")
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

    logging.info("CSV saved to {}".format(file_path))


def create_parser():
    """
    Set up the default OpenMHT parameters.
    """
    parser = argparse.ArgumentParser()

    # I/O parameters
    parser.add_argument('-i', '--input', help="Input CSV file path")
    parser.add_argument('-o', '--output', help="Output CSV file path")

    # Add OpenMHT module parameters
    # v = 307200  # Image width x height in pixels
    parser.add_argument('-v',  type=int, default=307200, help='Image width x height in pixels')

    # dth = 1000  # Gating area for new detections
    parser.add_argument('-dth', type=int, default=1000, help='Gating area for new detections')

    # k = 0  # Gain or blending factor
    parser.add_argument('-k', type=float, default=0, help='Gain or blending factor')

    # q = 0.00001  # Kalman filter process variance
    parser.add_argument('-q', type=float, default=0.00001, help='Image width x height in pixels')

    # r = 0.01  # Estimate of measurement variance
    parser.add_argument('-r', type=float, default=0.01, help='Image width x height in pixels')

    # n = 5  # N-scan pruning parameter
    parser.add_argument('-n', type=int, default=5, help='N-scan pruning parameter')

    # bth = 100  # Maximum number of track tree branches
    parser.add_argument('-bth', type=int, default=100, help='Maximum number of track tree branches')

    # nmiss = 15  # Maximum number of false observations in tracks
    parser.add_argument('-nmiss', type=int, default=15, help='Maximum number of false observations in tracks')

    return parser


def run():
    """
    Read user arguments and run OpenMHT.
    """

    # Set up the argument parser
    parser = create_parser()

    # Read user input
    params = parser.parse_args()
    input_file = params.ifile
    output_file = params.ofile

    # Verify CSV file formats
    try:
        assert Path(input_file).is_file(), f"Input file does not exist: {input_file}"
        assert Path(param_file).is_file(), f"Parameter file does not exist: {param_file}"
        assert Path(input_file).suffix == '.csv', f"Input file is not CSV: {input_file}"
        assert Path(output_file).suffix == '.csv', f"Output file is not CSV: {output_file}"
        assert Path(param_file).suffix == '.txt', f"Parameter file is not TXT: {param_file}"

    except AssertionError as e:
        print(e)
        sys.exit(2)

    logging.info(f"Input file is: {input_file}")
    logging.info(f"Output file is: {output_file}")

    # run MHT on detections
    detections = read_uv_csv(input_file)
    start = time.time()
    mht = MHT(detections, params)
    solution_coordinates = mht.run()
    write_uv_csv(output_file, solution_coordinates)
    end = time.time()
    elapsed_seconds = end - start
    logging.info(f"Elapsed time (seconds): {elapsed_seconds:.3f}")
