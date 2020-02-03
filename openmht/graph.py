#!/usr/bin/env python
"""Graph"""

import numpy as np

__author__ = "Jon Perdomo"
__license__ = "GPL-3.0"
__version__ = "0.1.0"

class Graph(object):
    def __init__(self, graph_dict=None):
        """ initializes a graph object
            If no dictionary or None is given,
            an empty dictionary will be used
        """
        if graph_dict is None:
            graph_dict = {}

        self.__graph_dict = graph_dict
        self.__edges = []
        self.__vertices = []

    def vertices(self):
        """ returns the vertices of a graph """
        return self.__vertices

    def edges(self):
        """ returns the edges of a graph """
        return self.__generate_edges()

    def add_vertex(self, vertex):
        """ If the vertex "vertex" is not in
            self.__graph_dict, a key "vertex" with an empty
            list as a value is added to the dictionary.
            Otherwise nothing has to be done.
        """
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []
            self.__vertices.append(vertex)

    def add_edge(self, edge):
        """ assumes that edge is of type set, tuple or list;
            between two vertices can be multiple edges!
        """
        (vertex1, vertex2) = tuple(edge)
        if vertex1 in self.__graph_dict:
            self.__graph_dict[vertex1].append(vertex2)
        else:
            self.__graph_dict[vertex1] = [vertex2]

        self.__edges.append(edge)

    def adjacency_matrix(self):
        """
        Generate the adjacency matrix:
        https://en.wikipedia.org/wiki/Adjacency_matrix
        """

        max_value = max([int(vid) for vid in self.vertices()])+1  # Find the maximum vertex ID (+1 since 0-indexed)
        adj_mat = np.zeros((max_value, max_value))  # Create the NxN matrix

        # Populate the adjacency matrix from the edges
        for edge in self.edges():
            i, j = [int(vertex_id) for vertex_id in edge]  # Get the matrix indices
            adj_mat[i, j] = 1
            adj_mat[j, i] = 1

        return adj_mat

    def complement(self):
        """Generate the adjacency matrix for the complement graph."""
        max_value = max([int(vid) for vid in self.vertices()])+1  # Find the maximum vertex ID (+1 since 0-indexed)
        adj_mat = np.ones((max_value, max_value))  # Create the NxN matrix
        np.fill_diagonal(adj_mat, 0)  # Format as the complete matrix

        # Remove the current edges
        for edge in self.__edges:
            i, j = [int(vertex_id) for vertex_id in edge]  # Get the matrix indices
            adj_mat[i, j] = 0
            adj_mat[j, i] = 0

        return adj_mat

    def set_edges(self, edges):
        self.__edges = edges

    def vertex_degrees(self, adj_mat):
        """ The degree of a vertex is the number of edges connecting
            it, i.e. the number of adjacent vertices. Loops are counted
            double, i.e. every occurence of vertex in the list
            of adjacent vertices
        """
        degrees = adj_mat.sum(axis=1)
        return degrees

    def __generate_edges(self):
        """ A static method generating the edges of the
            graph "graph". Edges are represented as sets
            with one (a loop back to the vertex) or two
            vertices
        """
        edges = []
        for vertex in self.__graph_dict:
            for neighbour in self.__graph_dict[vertex]:
                if {neighbour, vertex} not in edges:
                    edges.append({vertex, neighbour})
        return edges
