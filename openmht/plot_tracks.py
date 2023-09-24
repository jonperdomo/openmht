"""Plot tracks from a file."""

import os
import matplotlib.pyplot as plt

def plot_2d_tracks(input_csv):
    """Plot tracks from a file in CSV format."""
    # Get the filename for the plot title
    filename = os.path.basename(input_csv)
    plot_title = f"Tracks from {filename}"

    # Read the CSV file
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    # Remove the header
    lines = lines[1:]

    # Sort the lines by track ID (column 2)
    lines.sort(key=lambda x: int(x.split(',')[1]))

    # Loop through the lines and parse the coordinates (columns 3 and 4) into a list of tracks
    tracks = []
    previous_track_id = None
    for line in lines:
        current_track_id = int(line.split(',')[1])
        x, y = line.split(',')[2:]
        if current_track_id != previous_track_id:
            # Store the previous track
            if previous_track_id is not None:
                tracks.append(track)

            # Create a new track
            track = []

            # Update the track ID
            previous_track_id = current_track_id
        
        # Add the coordinates to the track
        x, y = line.split(',')[2:]

        # Convert 'None' values to NaN
        if 'None' in x:
            x = 'nan'
        if 'None' in y:
            y = 'nan'

        track.append((float(x.strip()), float(y.strip())))
    # Plot the tracks
    fig = plt.figure()
    plot_axis = fig.add_subplot(111)
    for track in tracks:
        # Set a unique color for each track
        color = next(plot_axis._get_lines.prop_cycler)['color']

        # Convert the track to a list of X and Y coordinates
        x, y = zip(*track)

        # Plot the track as a line
        plot_axis.plot(x, y, color=color)

        # Plot each point in the track as a black dot
        plot_axis.scatter(x, y, color='black')

    # Set the axis labels and title
    plot_axis.set_xlabel('X')
    plot_axis.set_ylabel('Y')
    plot_axis.set_title(plot_title)
    plt.show()
