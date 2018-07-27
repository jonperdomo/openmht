import numpy as np
from graph import Graph


class WeightedGraph(Graph):
    """
    A graph with weighted vertices.
    """
    def __init__(self, graph_dict=None):
        Graph.__init__(self, graph_dict)
        self.vertex_weights = []

    def mwis(self):
        """
        Find the maximum weighted independent set using vertex support:
        https://waset.org/publications/12153/approximating-maximum-weighted-independent-set-using-vertex-support
        """
        adj_mat = self.adjacency_matrix()
        n = adj_mat.shape[0]
        mwis = np.ones(n)
        weights = self.vertex_weights
        print("\nweights: {}".format(weights))

        while adj_mat.any():
            degrees = self.vertex_degrees(adj_mat)
            supports = self.vertex_supports(adj_mat, degrees)
            support_ratios = (supports * degrees) / np.array(weights)

            # Find the maximum support ratio, and add this to the vertex cover
            max_id = np.argmax(support_ratios)
            mwis[max_id] = 0

            # Remove the vertex edges from the adjacency matrix
            adj_mat[:, max_id] = 0
            adj_mat[max_id, :] = 0

        # Get the final maximum weighted independent set, S(G)=V-Vc
        mwis_vertex_ids = np.nonzero(mwis)[0]

        return mwis_vertex_ids

    def add_weighted_vertex(self, vertex, weight):
        """
        Add a weighted vertex to the graph.
        """
        self.add_vertex(vertex)
        self.vertex_weights.append(weight)
