from kalmanfilter import KalmanFilter
from graph import Graph


class TrackTree:
    """
    Track tree construction and updating.
    """
    def __init__(self, frame_number):
        self.frame_number = frame_number  # The frame number where this track begins
        self.image_area = 10.0  # TODO: Replace with actual frame dimensions
        self.kf = None  # Kalman filter for calculating the motion score
        self.motion_score = 1.0  # The final motion score for the track
        self.graph = Graph()  # Graph with detections as vertices
        self.last_vertex_id = ""  # ID of the previously added vertex
        self.vertex_coordinates = {}  # Vertex ID's (key) with their coordinate position (value)

    def get_frame_number(self):
        return self.frame_number

    def get_vertices(self):
        return self.graph.vertices()

    def has_conflict(self, track_tree):
        """Determine whether any conflicting vertices occur between trees."""
        vset1 = self.get_vertices()
        vset2 = track_tree.get_vertices()
        conflict_exists = bool(set(vset1) & set(vset2))

        return conflict_exists

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
        print("\nTrack tree starting at frame #{}".format(self.frame_number))
        print("\nFinal score: {}".format(round(self.motion_score, 3)))
        print("\nFinal graph:")
        print(self.graph)

        print("\nPositions:")
        for vertex_id in self.graph.vertices():
            print(self.vertex_coordinates[vertex_id])
