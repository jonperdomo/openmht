#!/usr/bin/env python
"""Weighted Graph"""

import operator
import random

from .graph import Graph

__author__ = "Jon Perdomo"
__license__ = "GPL-3.0"
__version__ = "0.1.0"


class WeightedGraph(Graph):
    """
    A graph with weighted vertices.
    """
    def __init__(self, graph_dict=None):
        Graph.__init__(self, graph_dict)
        self.__weights = {}

    def mwis(self):
        """Determine the maximum weighted independent set."""

        # Find all maximal independent sets
        complement = self.complement()
        ind_sets = []
        self.____bron_kerbosch3(complement, ind_sets)

        # Find the maximum weighted set
        # NOTE: The maximum total weight of any subset of nodes in this graph cannot be less than the additive
        # inverse of the total magnitude of all node weights, subtract 1. Use this value as the initial maximum weight.
        max_weight = -sum(map(abs, self.__weights.values()))-1
        mwis = []
        for ind_set in ind_sets:
            set_weight = sum([self.__weights[str(i)] for i in ind_set])
            if set_weight > max_weight:
                max_weight = set_weight
                mwis = ind_set

        return mwis

    def ____bron_kerbosch3(self, g, results):
        """With vertex ordering."""
        P = set(range(len(self.vertices())))
        R, X = set(), set()
        deg_ord = self.__degeneracy_ordering(g)

        for v in deg_ord:
            N_v = self.__n(v, g)
            self.____bron_kerbosch2(R | {v}, P & N_v, X & N_v, g, results)

            P = P - {v}
            X = X | {v}

    def ____bron_kerbosch2(self, R, P, X, g, results):
        """With pivoting."""
        if not any((P, X)):
            results.append(R)
            return

        u = random.choice(tuple(P | X))
        for v in P - self.__n(u, g):
            N_v = self.__n(v, g)
            self.__bron_kerbosch(R | {v}, P & N_v, X & N_v, g, results)

            P = P - {v}
            X = X | {v}

    def __bron_kerbosch(self, R, P, X, g, results):
        """Without pivoting."""
        if not any((P, X)):
            results.append(R)

        for v in set(P):
            N_v = self.__n(v, g)
            self.__bron_kerbosch(R | {v}, P & N_v, X & N_v, g, results)

            P = P - {v}
            X = X | {v}

    def __degeneracy_ordering(self, g):
        """Order such that each vertex has d or fewer neighbors that come later in the ordering."""
        v_ordered = []
        degrees = list(enumerate(self.vertex_degrees(g)))
        while degrees:
            min_index, min_value = min(degrees, key=operator.itemgetter(1))
            v_ordered.append(min_index)
            degrees.remove((min_index, min_value))

        return v_ordered

    def __n(self, v, g):
        return set([i for i, n_v in enumerate(g[v]) if n_v])

    def add_weighted_vertex(self, vertex, weight):
        """
        Add a weighted vertex to the graph.
        """
        self.add_vertex(vertex)
        self.__weights[vertex] = weight

    def __str__(self):
        res = super(WeightedGraph, self).__str__()
        res += "\nWeights: "
        for w in self.__weights.values():
            res += str(w) + " "

        return res
