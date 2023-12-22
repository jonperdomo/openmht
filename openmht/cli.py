#!/usr/bin/env python
import sys
import argparse
import time
import csv
import logging
import pkg_resources

from pathlib import Path

from .mht import MHT

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

__author__ = "Jon Perdomo"
__license__ = "GPL-3.0"


def read_uv_csv(file_path, frame_max=100):
    """
    Read detections from a CSV.
    Expected column headers are:
    Frame number, U, V
    """
    logging.info("Reading input CSV...")
    detections = []
    with open(file_path, encoding='utf-8-sig') as csv_file:
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

        logging.info("Reading inputs complete. Processed %d lines.", line_count)

    return detections


def write_uv_csv(file_path, solution_coordinates):
    """
    Write track trees to a CSV.
    Column headers are:
    Frame number, track number, U, V
    """
    logging.info("Writing output CSV...")
    csv_rows = []
    # Flatten the track trees into a list of coordinates
    for track_index, track_coordinates in enumerate(solution_coordinates):
        for frame_index, coordinate in enumerate(track_coordinates):
            if coordinate is None:
                u = v = 'None'
            else:
                u, v = [str(x) for x in coordinate]

            csv_rows.append([frame_index, track_index, u, v])

    # Sort the results by frame number
    csv_rows.sort(key=lambda x: x[0])
    with open(file_path, 'w', encoding='utf-8-sig') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        writer.writerow(['frame', 'track', 'u', 'v'])
        writer.writerows(csv_rows)

    logging.info("CSV saved to %s", file_path)


def read_parameters(params_file_path):
    """Read in the current Kalman filter parameters."""
    param_keys = ["v", "dth", "k", "q", "r", "n", "bth", "nmiss", "pd"]
    params = {}

    # Open the parameter file and read in the parameters
    with open(params_file_path, encoding='utf-8-sig') as file:
        for line in file:
            line_data = line.split("#")[0].split('=')
            if len(line_data) == 2:
                key, val = [s.strip() for s in line_data]
                if key in param_keys:
                    try:
                        val = float(val)
                    except ValueError as exc:
                        raise AssertionError(f"Incorrect value type in params.txt: {line}") from exc

                    param_keys.remove(key)
                    params[key] = val
            else:
                raise AssertionError(f"Error in params.txt formatting: {line}")

    if param_keys:
        raise AssertionError("Parameters not found in params.txt: " + ", ".join(param_keys))

    return params


def run(cli_args=None):
    """Read in the command line parameters and run MHT."""

    # Get the version from the package if possible
    try:
        __version__ = pkg_resources.require("openmht")[0].version
        logging.info("OpenMHT version %s", __version__)
    except pkg_resources.DistributionNotFound:
        __version__ = "unknown"  # Occurs when running from source

    # MHT parameters
    parser = argparse.ArgumentParser()
    parser.add_argument('ifile', help="Input CSV file path")
    parser.add_argument('ofile', help="Output CSV file path")
    parser.add_argument('pfile', help='Path to the parameter text file')

    # Version parameter
    parser.add_argument('-V', '--version', action='version', version=f"OpenMHT version {__version__}")

    # Track visualization parameters
    parser.add_argument('-p', '--plot', action='store_true', help="Plot the tracks")

    # Parse arguments
    args = parser.parse_args(cli_args)
    input_file = args.ifile
    output_file = args.ofile
    param_file = args.pfile

    # Verify CSV file formats
    try:
        assert Path(input_file).is_file(), f"Input file does not exist: {input_file}"
        assert Path(param_file).is_file(), f"Parameter file does not exist: {param_file}"
        assert Path(input_file).suffix == '.csv', f"Input file is not CSV: {input_file}"
        assert Path(output_file).suffix == '.csv', f"Output file is not CSV: {output_file}"
        assert Path(param_file).suffix == '.txt', f"Parameter file is not TXT: {param_file}"

    except AssertionError as param_error:
        print(param_error)
        sys.exit(2)

    logging.info("Input file is: %s", input_file)
    logging.info("Output file is: %s", output_file)
    logging.info("Parameter file is: %s", param_file)

    # Read MHT parameters
    try:
        params = read_parameters(param_file)
        logging.info("MHT parameters: %s", params)

    except AssertionError as param_error:
        print(param_error)
        sys.exit(2)

    # Run MHT on detections
    detections = read_uv_csv(input_file)
    start = time.time()
    mht = MHT(detections, params)
    solution_coordinates = mht.run()
    write_uv_csv(output_file, solution_coordinates)
    end = time.time()
    elapsed_seconds = end - start
    logging.info("Elapsed time (seconds): %.3f", elapsed_seconds)

    # Plot the tracks
    if args.plot:

        # Import here to allow running without matplotlib
        from .plot_tracks import plot_2d_tracks

        logging.info("Plotting tracks...")
        plot_2d_tracks(output_file)
        logging.info("Done.")
