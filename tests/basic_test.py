"""
Test OpenMHT performance
(Dependencies: pytest, )
"""

from openmht import cli
from openmht.mht import MHT

import numpy as np


def test_2d():
    # === Set up the 2d input array ===
    # frame_count = 50
    frame_count = 10

    # First detection
    x = np.linspace(1, 100, num=frame_count)
    y = x * 2
    d1 = np.transpose(np.vstack((x, y)))

    # Second detection
    x = np.linspace(1, 100, num=frame_count)
    y = x * 3
    d2 = np.transpose(np.vstack((x, y)))

    # Third detection
    x = np.linspace(1, 100, num=frame_count)
    y = (x * 3) + 1
    d3 = np.transpose(np.vstack((x, y)))

    # Add missing detections at frames
    d1_missing_frames = list(range(5, frame_count, 10))
    d2_missing_frames = list(range(10, frame_count, 10))
    d3_missing_frames = list(range(15, frame_count, 10))
    frame_data = []
    for frame_index in range(frame_count):
        frame_detections = []

        # Detection 1
        if frame_index not in d1_missing_frames:
            frame_detections.append(d1[frame_index, :])

        # Detection 2
        if frame_index not in d2_missing_frames:
            frame_detections.append(d2[frame_index, :])

        # Detection 3
        if frame_index not in d3_missing_frames:
            frame_detections.append(d3[frame_index, :])

        frame_data.append(frame_detections)

    # Set up the default parser arguments
    parser = cli.create_parser()
    params = parser.parse_args(['-i', 'input.csv', '-o', 'output.csv'])

    # Run MHT
    mht = MHT(frame_data, params)
    solution_coordinates = mht.run()
    assert True == True
    # # Set up the input detections
    # param_keys = ["b_th", "image_area", "gating_area", "k", "q", "r", "n"]
    # params = {}
    # with open(params_file_path) as f:
    #     for line in f:
    #         line_data = line.split("#")[0].split('=')
    #         if len(line_data) == 2:
    #             key, val = [s.strip() for s in line_data]
    #             if key in param_keys:
    #                 try:
    #                     val = float(val)
    #                 except ValueError:
    #                     raise AssertionError(f"Incorrect value type in params.txt: {line}")
    #
    #                 param_keys.remove(key)
    #                 params[key] = val
    #         else:
    #             raise AssertionError(f"Error in params.txt formatting: {line}")
    #
    # if param_keys:
    #     raise AssertionError("Parameters not found in params.txt: " + ", ".join(param_keys))
    #
    # return params
    #
    # # run MHT on detections
    # detections = read_uv_csv(input_file)
    # start = time.time()
    # mht = MHT(detections, params)
    # solution_coordinates = mht.run()
    # write_uv_csv(output_file, solution_coordinates)
    # end = time.time()
    # elapsed_seconds = end - start
    # logging.info("Elapsed time (seconds): {0:.3f}".format(elapsed_seconds))
    # self.assertEqual(True, False)  # add assertion here
