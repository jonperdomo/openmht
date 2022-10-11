from .kalman_filter import TrackFilter


class TrackNode:
    def __init__(self, frame_index, detection, conflict_id=0, filter_params=None, parent=None):
        self.frame_index = frame_index
        self.detection = detection
        self.conflict_id = conflict_id
        self.parent = parent
        self.children = None

        # If it is the root, then create a new Kalman filter
        if self.parent is None:
            self.filter = TrackFilter(frame_index, detection, filter_params)
        else:
            # Set and update the previous filter
            self.filter = parent.filter
            self.filter.add_detection(frame_index, detection)

        self.children = []

    def add_child(self, child_node):
        """
        Create a branch from a child node.
        """
        self.children.append(child_node)

    def get_filter(self):
        return self.filter

###########

    def set_root(self, key):
        self.key = key

    def inorder(self):
        if self.left is not None:
            self.left.inorder()
        print(self.key, end=' ')
        if self.right is not None:
            self.right.inorder()

    def insert_left(self, new_node):
        self.left = new_node

    def insert_right(self, new_node):
        self.right = new_node

    def search(self, key):
        if self.key == key:
            return self
        if self.left is not None:
            temp = self.left.search(key)
            if temp is not None:
                return temp
        if self.right is not None:
            temp = self.right.search(key)
            return temp
        return None

    def count_nodes(self, node):
        if node is None:
            return 0
        return 1 + self.count_nodes(node.left) + self.count_nodes(node.right)
