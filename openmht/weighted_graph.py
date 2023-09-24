#!/usr/bin/env python
"""Weighted Graph"""

import operator
import numpy as np

from .graph import Graph

__author__ = "Jon Perdomo"
__license__ = "GPL-3.0"


class WeightedGraph(Graph):
    """A graph with weighted vertices."""

    def __init__(self, graph_dict=None):
        Graph.__init__(self, graph_dict)
        self.__weights = {}

    def mwis(self):
        """
        Determine the maximum weighted independent set.
        Returns a list of vertex IDs.
        """

        # Find all maximal independent sets
        complement = self.complement()
        ind_sets = []
        self.____bron_kerbosch3(complement, ind_sets)

        # Find the maximum weighted set
        # NOTE: The maximum total weight of any subset of nodes in this graph
        # cannot be less than the additive inverse of the total magnitude of all
        # node weights, subtract 1. Use this value as the initial maximum
        # weight.
        max_weight = -sum(map(abs, self.__weights.values()))-1
        mwis = []
        for ind_set in ind_sets:
            set_weight = sum([self.__weights[str(i)] for i in ind_set])
            if set_weight > max_weight:
                max_weight = set_weight
                mwis = ind_set

        return mwis

    def ____bron_kerbosch3(self, g: np.ndarray, results: list):
        """With vertex ordering."""
        P = set(range(len(self.vertices())))
        R, X = set(), set()
        deg_ord = self.__degeneracy_ordering(g)

        for v in deg_ord:
            N_v = self.__n(v, g)
            self.____bron_kerbosch2(R | {v}, P & N_v, X & N_v, g, results)

            P = P - {v}
            X = X | {v}

    def ____bron_kerbosch2(self, R: set, P: set, X: set, g: np.ndarray,
                           results: list):
        """With pivoting."""
        if not any((P, X)):
            results.append(R)
            return

        # Choose pivot point u that maximizes size of N(u). This is chosen to
        # minimize the size of P - N(u), thus minimizing recursion branches.
        u_max = -1
        size_max = 0
        for u in P | X:
            size_N = len(self.__n(u, g))
            if size_N > size_max:
                u_max = u
                size_max = size_N

        for v in P - self.__n(u_max, g):
            N_v = self.__n(v, g)
            self.____bron_kerbosch2(R | {v}, P & N_v, X & N_v, g, results)

            P = P - {v}
            X = X | {v}

    def __bron_kerbosch(self, R: set, P: set, X: set, g: np.ndarray,
                        results: list):
        """Without pivoting."""
        if not any((P, X)):
            results.append(R)

        for v in set(P):
            N_v = self.__n(v, g)
            self.__bron_kerbosch(R | {v}, P & N_v, X & N_v, g, results)

            P = P - {v}
            X = X | {v}

    def __degeneracy_ordering(self, g: np.ndarray) -> list:
        """Order such that each vertex has d or fewer neighbors that come later in the ordering."""
        v_ordered = []
        degrees = list(enumerate(self.vertex_degrees(g)))
        while degrees:
            min_index, min_value = min(degrees, key=operator.itemgetter(1))
            v_ordered.append(min_index)
            degrees.remove((min_index, min_value))

        return v_ordered

    def __n(self, v: int, g: np.ndarray) -> set:
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
    