import numpy as np
from graph import Graph


class WeightedGraph(Graph):
    """
    A graph with weighted vertices.
    """
    def __init__(self, graph_dict=None):
        Graph.__init__(self, graph_dict)
        self.vertex_weights = {}  # Vertex ID's with associated weights

    def mwis(self):
        """
        Find the maximum weighted independent set using vertex support:
        https://waset.org/publications/12153/approximating-maximum-weighted-independent-set-using-vertex-support
        """
        adj_mat = self.get_adjacency_matrix()  # Get the graph's adjacency matrix
        n = adj_mat.shape[0]
        support_ratios = np.zeros(n)  # Record the support ratios for each vertex
        edges = self.edges()
        # while edges:
        for i in range(n):
            vertex_id = str(i)
            degree = self.vertex_degree(vertex_id)
            support = self.vertex_support(vertex_id)
            weight = self.vertex_weights[vertex_id]
            support_ratio = (support * float(degree)) / float(weight)  # Final support ratio
            support_ratios[i] = support_ratio

        print("SR's:\n{}".format(support_ratios))

    def add_weighted_vertex(self, vertex, weight):
        """
        Add a weighted vertex to the graph.
        """
        self.add_vertex(vertex)
        self.vertex_weights[vertex] = weight

    def get_adjacency_matrix(self):
        """Generate the adjacency matrix"""

        max_value = max([int(vid) for vid in self.vertices()])+1  # Find the maximum vertex ID (+1 since 0-indexed)
        adj_mat = np.zeros((max_value, max_value))  # Create the NxN matrix

        # Populate the adjacency matrix from the edges
        edges = self.edges()
        while edges:
            edge = edges.pop()
            i, j = [int(vid) for vid in edge]  # Get the matrix indices
            adj_mat[i, j] = 1

        return adj_mat
