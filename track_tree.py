from kalman_filter import KalmanFilter


class TrackTree:
    """
    Track tree construction and updating.
    """
    def __init__(self, frame_index):
        self.frame_index = frame_index  # The frame number / level where this track tree begins
        self.current_frame = self.frame_index
        self.kf = None  # Kalman filter for calculating the motion score
        self.motion_score = 0.  # The final motion score for the track
        self.vertex_coords = {}  # Vertex ID's (key) with their coordinate position (value)
        self.vertex_weights = {}
        self.detections = []
        self.__nodes = []

    def get_detections(self):
        return self.detections

    def get_frame_detection(self, frame_index):
        """Get the detection at the given frame."""
        try:
            detection_id = self.__nodes[frame_index]
        except IndexError:
            detection_id = None

        return detection_id

    def get_frame_number(self):
        return self.frame_index

    def get_motion_score(self):
        return self.motion_score

    def get_vertices(self):
        return self.__nodes

    def has_conflict(self, track_tree):
        """Determine whether any conflicting vertices occur between trees."""
        v1 = self.get_vertices()
        v2 = track_tree.get_vertices()
        conflict_exists = bool(set(v1) & set(v2))

        return conflict_exists

    def add_detection(self, detection_id, detection):

        # Update the tree
        self.__nodes.append(detection_id)
        if detection is None:
            self.motion_score += self.kf.update(detection)

        else:

            # Update the Kalman filter
            if self.kf:
                motion_score = self.kf.update(detection)  # Update the existing Kalman filter with the new detection
                self.motion_score += motion_score  # Update the overall motion score

            else:
                self.kf = KalmanFilter(detection)  # Initialize the Kalman filter
                self.motion_score += self.kf.get_motion_score()

        self.vertex_coords[detection_id] = detection  # Record the vertex coordinate
        self.vertex_weights[detection_id] = self.motion_score
        self.detections.append(detection)
        self.current_frame += 1

    def __str__(self):
        results = "\nTrack tree starting at frame #{}".format(self.frame_index)
        for vertex_id in self.__nodes:
            results += "\nPos: {}\nWeight:{}\n".format(self.vertex_coords[vertex_id], self.vertex_weights[vertex_id])

        return results
