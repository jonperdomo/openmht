from graph import Graph


class WeightedGraph(Graph):
    """
    A graph with weighted vertices.
    """
    def __init__(self, graph_dict=None):
        Graph.__init__(self, graph_dict)
        self.vertex_weights = []  # Vertex ID's with associated weights

    def mwis(self):
        '''
        Find the maximum weighted independent set.
        https://wincent.com/wiki/Computing_the_Maximum_Weighted_Independent_Set_of_a_graph_path
        '''
        for i in range(self.vertex_weights):
            vertex_id, weight = self.vertex_weights[i]

    def add_weighted_vertex(self, vertex, weight):
        """
        Add a weighted vertex to the graph.
        """
        self.add_vertex(vertex)
        self.vertex_weights.append((vertex, weight))
