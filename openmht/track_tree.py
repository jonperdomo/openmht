from .kalman_filter import TrackFilter

import numpy as np


def find_root(node):
    p = node
    while p.parent is not None:
        p = p.parent
    return p


class TrackNode:
    def __init__(self, frame_index, detection, conflict_id=0, filter_params=None, parent=None):
        self.frame_index = frame_index
        self.detection = detection
        self.conflict_id = conflict_id
        self.filter_params = filter_params
        self.parent = parent
        self.children = []

        # If it is the root, then create a new Kalman filter
        if self.parent is None:
            self.filter = TrackFilter(frame_index, detection, filter_params)
        else:
            # Set and update the previous filter
            self.filter = parent.filter
            self.filter.add_detection(frame_index, detection)

    def get_frame_index(self):
        return self.frame_index

    def get_detection(self):
        return self.detection

    def get_conflict_id(self):
        return self.conflict_id

    def add_child(self, child_node):
        """
        Create a branch from a child node.
        """
        self.children.append(child_node)

    def get_root_id(self):
        """
        Get the root for this track as a string ID.
        """
        if self.parent is None:
            root_id = 'root_F' + str(self.frame_index) + '_D' + str(self.detection)
        else:
            root_node = find_root(self.parent)
            root_id = 'root_F' + str(root_node.get_frame_index()) + '_D' + str(root_node.get_detection())

        return root_id

    # def add_child(self, child_node):
    #     """
    #     Create a branch from a child node.
    #     """
    #     if len(self.children) == 0:
    #         self.children.append(child_node)
    #     else:
    #         try:
    #             for parent_node in self.children:
    #                 parent_node.add_child(child_node)
    #         except RecursionError as re:
    #             print("Unable to calculate factorial. Number is too big.")

    def get_children(self):
        return self.children

    def get_nodes(self):
        child_nodes = []
        for child_node in self.children:
            if len(child_node.get_children()) == 0:
                print("HERE")
                child_nodes.append(child_node)
            else:
                child_nodes = child_node.get_nodes()

        return child_nodes

    def get_bottom_children(self):
        if len(self.children) == 0:
            yield self
        else:
            for child_node in self.children:
                child_node.get_children()

    def get_filter(self):
        return self.filter

    def prune_low_scoring_branches(self, branch_threshold):
        """
        Keep only the specified number of top scoring branches.
        """
        if len(self.children) > 1:
            child_scores = [x.get_filter().get_track_score() for x in self.children]

            if not all(x == child_scores[0] for x in child_scores):
                print("Found different scores here.")

            top_branches_idx = np.argsort(child_scores)[-branch_threshold:]
            top_children = [self.children[i] for i in top_branches_idx]
            self.children = top_children

    def __copy__(self):
        copy_instance = TrackNode(self.frame_index, self.detection, self.conflict_id, self.filter_params, self.parent)
        return copy_instance

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
