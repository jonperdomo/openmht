from kalmanfilter import KalmanFilter
from graph import Graph

class TrackTree:
    """
    Track tree construction and updating.
    """
    def __init__(self, frame_number):
        self.frame_number = frame_number
        self.image_area = 10.0  # Placeholder
        self.kf = None  # Kalman filter for motion scores
        self.motion_score = 1.0
        self.graph = Graph()
        self.last_vertex_id = ""
        self.vertex_coordinates = {}  # Vertex ID's (key) with their coordinate position (value)

    def get_frame_number(self):
        return self.frame_number

    def add_detection(self, detection, vertex_id):

        # Update the graph
        self.graph.add_vertex(vertex_id)
        if detection is None:
            self.last_vertex_id = ""  # Isolated vertex for missing detections
        else:
            if self.last_vertex_id:
                self.graph.add_edge({self.last_vertex_id, vertex_id})  # Form an edge with the previous vertex

            self.last_vertex_id = vertex_id  # Update the last vertex

            # Update the Kalman filter
            if self.kf:
                motion_score = self.kf.update(detection)  # Update the existing Kalman filter with the new detection
                self.motion_score *= (motion_score/(1.0/self.image_area))  # Update the overall motion score

            else:
                self.kf = KalmanFilter(detection)  # Initialize the Kalman filter

        self.vertex_coordinates[vertex_id] = detection  # Record the vertex coordinate

    def print_data(self):
        print("\nTrack tree starting at frame {}".format(self.frame_number))
        print("\nFinal score: {}".format(round(self.motion_score, 3)))
        print("\nFinal graph:")
        print(self.graph)

        print("\nPositions:")
        for vertex_id in self.graph.vertices():
            print(self.vertex_coordinates[vertex_id])
