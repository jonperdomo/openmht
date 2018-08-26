from kalman_filter import KalmanFilter
from graph import Graph


class TrackTree:
    """
    Track tree construction and updating.
    """
    def __init__(self, frame_number):
        self.frame_number = frame_number  # The frame number where this track begins
        self.image_area = 100.0  # TODO: Replace with actual frame dimensions
        self.kf = None  # Kalman filter for calculating the motion score
        self.motion_score = 0.  # The final motion score for the track
        self.graph = Graph()  # Graph with detections as vertices
        self.last_vertex_id = ""  # ID of the previously added vertex
        self.vertex_coords = {}  # Vertex ID's (key) with their coordinate position (value)
        self.vertex_weights = {}

    def get_frame_number(self):
        return self.frame_number

    def get_motion_score(self):
        return self.motion_score

    def get_vertices(self):
        return self.graph.vertices()

    def has_conflict(self, track_tree):
        """Determine whether any conflicting vertices occur between trees."""
        v1 = self.get_vertices()
        v2 = track_tree.get_vertices()
        conflict_exists = bool(set(v1) & set(v2))

        return conflict_exists

    def add_detection(self, detection, vertex_id):

        # Update the graph
        self.graph.add_vertex(vertex_id)
        if detection is None:
            self.last_vertex_id = ""  # Isolated vertex for missing detections
            self.motion_score += self.kf.update(detection)

        else:
            if self.last_vertex_id:
                self.graph.add_edge({self.last_vertex_id, vertex_id})  # Form an edge with the previous vertex

            self.last_vertex_id = vertex_id  # Update the last vertex

            # Update the Kalman filter
            if self.kf:
                motion_score = self.kf.update(detection)  # Update the existing Kalman filter with the new detection
                self.motion_score += motion_score  # Update the overall motion score

            else:
                self.kf = KalmanFilter(detection)  # Initialize the Kalman filter
                self.motion_score += self.kf.get_motion_score()

        self.vertex_coords[vertex_id] = detection  # Record the vertex coordinate
        self.vertex_weights[vertex_id] = self.motion_score

    def __str__(self):
        results = "\nTrack tree starting at frame #{}".format(self.frame_number)
        for vertex_id in self.graph.vertices():
            results += "\nPos: {}\nWeight:{}\n".format(self.vertex_coords[vertex_id], self.vertex_weights[vertex_id])

        return results
