from kalmanfilter import KalmanFilter

class TrackTree:
    """
    Track tree construction and updating.
    """
    def __init__(self, frame_number):
        self.frame_number = frame_number
        self.image_area = 10.0  # Placeholder
        self.nodes = []
        self.kf = None  # Kalman filter for motion scores
        self.motion_score = 1.0

    def get_frame_number(self):
        return self.frame_number

    def add_detection(self, detection):
        if self.nodes:
            if detection is not None:  # Missing detections are ignored / not updated with the Kalman filter
                print("Detection shape: {}".format(detection.shape))
                motion_score = self.kf.update(detection)  # Update the Kalman filter with the new detection
                print("motion score: {}".format(motion_score))
                self.motion_score *= (motion_score/(1.0/self.image_area))  # Update the overall motion score
        else:
            self.kf = KalmanFilter(detection)  # Initialize the Kalman filter
        self.nodes.append(detection)

    def print_data(self):
        print("\nTrack tree starting at frame {}\n".format(self.frame_number))
        for n in self.nodes:
            print(n)

        print("\nFinal score: {}".format(round(self.motion_score, 3)))
