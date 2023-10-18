"""Plot tracks from a file."""

import os
import matplotlib.pyplot as plt
import numpy as np

def plot_2d_tracks(input_csv, Flag_Save=False, Frames=None):
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
    track_ids = []
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
            track_ids.append(previous_track_id)
            
        
        # Add the coordinates to the track
        x, y = line.split(',')[2:]
        frame = line.split(',')[0]

        # Convert 'None' values to NaN
        if 'None' in x:
            x = 'nan'
        if 'None' in y:
            y = 'nan'

        track.append((int(frame.strip()), float(x.strip()), float(y.strip())))
    tracks.append(track)
    # Plot the tracks
    # fig = plt.figure(figsize=(10,10))
    # plot_axis = fig.add_subplot(111)
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(18,9))
    for i, track in enumerate(tracks):
        # Set a unique color for each track
        color = next(axes[0]._get_lines.prop_cycler)['color']

        # Convert the track to a list of X and Y coordinates
        frame, x, y = zip(*track)
        
        if Frames is not None:
            j = np.where(np.all([np.array(frame) >= Frames[0], 
                                 np.array(frame) <= Frames[1]], axis=0))[0]
            if np.size(j) >= 1:
                frame = np.array(frame)[j]
                x = np.array(x)[j]
                y = np.array(y)[j]

                # Plot the track as a line
                axes[0].plot(x, y, color=color, label="Track %d"%track_ids[i])
        
                # Plot each point in the track as a black dot
                axes[0].scatter(x, y, color=color)
                axes[1].plot(frame, x, '-o', color=color, label="x, Track %d"%track_ids[i])
                axes[1].plot(frame, y, '--s', color=color, label="y, Track %d"%track_ids[i])
        else:

            # Plot the track as a line
            axes[0].plot(x, y, color=color, label="Track %d"%track_ids[i])
    
            # Plot each point in the track as a black dot
            axes[0].scatter(x, y, color=color)
            axes[1].plot(frame, x, '-o', color=color, label="x, Track %d"%track_ids[i])
            axes[1].plot(frame, y, '--s', color=color, label="y, Track %d"%track_ids[i])

    # Set the axis labels and title
    axes[0].set_xlabel('X')
    axes[0].set_ylabel('Y')
    axes[0].set_title(plot_title)
    axes[0].legend()

    axes[1].set_xlabel('Frame')
    axes[1].set_ylabel('X or Y')
    axes[1].legend()
    
    plt.tight_layout()
    
    if Flag_Save:
        if Frames is not None:
            fname_out = os.path.join(os.path.dirname(input_csv), 
                                     "%s_Frames_%d_%d"%(os.path.basename(input_csv).split('.')[0], Frames[0], Frames[1]))
        else:
            fname_out = os.path.join(os.path.dirname(input_csv), os.path.basename(input_csv).split('.')[0])
        plt.savefig("%s.png"%fname_out)
    else:
        plt.show()

    plt.close()  # Close the figure so it doesn't consume memory
    