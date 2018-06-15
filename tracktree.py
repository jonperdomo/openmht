from kalmanfilter import KalmanFilter
from graph import Graph

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
        self.graph = Graph()
        self.last_vertex_id = ""

    def get_frame_number(self):
        return self.frame_number

    def add_detection(self, detection, vertex_id):
        print("VID: ", vertex_id)
        if self.nodes:
            if detection is not None:  # Missing detections are ignored / not updated with the Kalman filter
                print("Detection shape: {}".format(detection.shape))
                motion_score = self.kf.update(detection)  # Update the Kalman filter with the new detection
                print("motion score: {}".format(motion_score))
                self.motion_score *= (motion_score/(1.0/self.image_area))  # Update the overall motion score
        else:
            self.kf = KalmanFilter(detection)  # Initialize the Kalman filter
        self.nodes.append(detection)

        # Update the graph
        self.graph.add_vertex(vertex_id)
        if detection is None:
            self.last_vertex_id = ""
        else:
            if self.last_vertex_id:
                self.graph.add_edge({self.last_vertex_id, vertex_id})  # Continued vertex path

            self.last_vertex_id = vertex_id

    def print_data(self):
        print("\nTrack tree starting at frame {}\n".format(self.frame_number))
        for n in self.nodes:
            print(n)

        print("\nFinal score: {}".format(round(self.motion_score, 3)))
        print("\nFinal graph:\n")
        print(self.graph)
