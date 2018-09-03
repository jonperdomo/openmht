from graph import Graph


class WeightedGraph(Graph):
    """
    A graph with weighted vertices.
    """
    def __init__(self, graph_dict=None):
        Graph.__init__(self, graph_dict)
        self.vertex_weights = []

    def mwis(self):
        """Determine the maximum weighted independent set."""
        # print("\nweights: {}".format(self.vertex_weights))

        # Find all maximal independent sets
        complement = self.complement()
        # print("\n------\nComplement:\n{}".format(complement))
        R = []
        P = list(range(len(self.vertices())))
        X = []
        ind_sets = list(self.bron_kerbosch(R, P, X, complement))

        # Find the maximum weighted set
        max_weight = min(self.vertex_weights)
        mwis = []
        for ind_set in ind_sets:
            set_weight = sum([self.vertex_weights[i] for i in ind_set])
            if set_weight > max_weight:
                max_weight = set_weight
                mwis = ind_set

        # print("\nmwis: {}".format(mwis))

        return mwis

    def bron_kerbosch(self, R, P, X, g):
        if not any((P, X)):
            yield R

        for v in P[:]:
            R_v = R + [v]
            P_v = [v1 for v1 in P if v1 in self.N(v, g)]
            X_v = [v1 for v1 in X if v1 in self.N(v, g)]
            for r in self.bron_kerbosch(R_v, P_v, X_v, g):
                yield r
            P.remove(v)
            X.append(v)

    def N(self, v, g):
        return [i for i, n_v in enumerate(g[v]) if n_v]

    def add_weighted_vertex(self, vertex, weight):
        """
        Add a weighted vertex to the graph.
        """
        self.add_vertex(vertex)
        self.vertex_weights.append(weight)

    def __str__(self):
        res = super(WeightedGraph, self).__str__()
        res += "\nweights: "
        for w in self.vertex_weights:
            res += str(w) + " "

        return res
