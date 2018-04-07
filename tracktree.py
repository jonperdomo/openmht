from kalmanfilter import KalmanFilter

class TrackTree:
    """
    Track tree construction and updating.
    """
    def __init__(self, frame_number):
        self.frame_number = frame_number
        self.nodes = []
        self.kf = None  # Kalman filter for motion scores

    def get_frame_number(self):
        return self.frame_number

    def add_detection(self, detection):
        if self.nodes:
            if detection is not None:  # Missing detections are ignored / not updated with the Kalman filter
                self.kf.update(detection)  # Update the Kalman filter with the new detection
        else:
            self.kf = KalmanFilter(detection)  # Initialize the Kalman filter
        self.nodes.append(detection)

    def print_data(self):
        print("\nTrack tree starting at frame {}".format(self.frame_number))
        for n in self.nodes:
            print(n)
