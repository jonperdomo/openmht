#!/usr/bin/env python

"""Plot MHT tracks from a file."""

import argparse

from trackvis.plot_tracks import plot_2d_tracks


def main():
    """Plot the tracks in the given file."""
    # Create the parser
    parser = argparse.ArgumentParser(description="Plot tracks from a file.")
    parser.add_argument("file", help="The file to plot.")
    parser.add_argument("-o", "--output", help="The output file name.")

    # Parse the arguments
    args = parser.parse_args()

    # Plot the tracks
    plot_2d_tracks(args.file, args.output)


if __name__ == '__main__':
    main()
