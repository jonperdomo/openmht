""" A Python Class
A simple Python graph class, demonstrating the essential
facts and functionalities of graphs.
https://www.python-course.eu/graphs_python.php
"""
import numpy as np


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

    def find_all_paths(self, start_vertex, end_vertex, path=[]):
        """ find all paths from start_vertex to
            end_vertex in graph """
        graph = self.__graph_dict
        path = path + [start_vertex]
        if start_vertex == end_vertex:
            return [path]
        if start_vertex not in graph:
            return []
        paths = []
        for vertex in graph[start_vertex]:
            if vertex not in path:
                extended_paths = self.find_all_paths(vertex,
                                                     end_vertex,
                                                     path)
                for p in extended_paths:
                    paths.append(p)
        return paths

    def find_isolated_nodes(self):
        """ returns a list of isolated vertices. """
        graph = self.__graph_dict
        isolated = []
        for vertex in graph:
            if not graph[vertex]:
                isolated += [vertex]
        return isolated

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
        # print("Getting the complement...")
        max_value = max([int(vid) for vid in self.vertices()])+1  # Find the maximum vertex ID (+1 since 0-indexed)
        adj_mat = np.ones((max_value, max_value))  # Create the NxN matrix
        np.fill_diagonal(adj_mat, 0)  # Format as the complete matrix

        # Remove the current edges
        for edge in self.__edges:
            i, j = [int(vertex_id) for vertex_id in edge]  # Get the matrix indices
            adj_mat[i, j] = 0
            adj_mat[j, i] = 0
        # print(f"Complete.")

        return adj_mat

    def set_edges(self, edges):
        self.__edges = edges

    def vertex_degree(self, vertex):
        """ The degree of a vertex is the number of edges connecting
            it, i.e. the number of adjacent vertices. Loops are counted
            double, i.e. every occurence of vertex in the list
            of adjacent vertices
        """
        adj_vertices = self.__graph_dict[vertex]
        degree = len(adj_vertices) + adj_vertices.count(vertex)
        return degree

    def vertex_degrees(self, adj_mat):
        """ The degree of a vertex is the number of edges connecting
            it, i.e. the number of adjacent vertices. Loops are counted
            double, i.e. every occurence of vertex in the list
            of adjacent vertices
        """
        degrees = adj_mat.sum(axis=1)
        return degrees

    def vertex_support(self, vertex):
        """ The support of a vertex is defined by the
            sum of the degree of the vertices which are
            adjacent to it
        """
        adj_vertices = self.__graph_dict[vertex]
        support = sum([self.vertex_degree(vid) for vid in adj_vertices])
        return support

    def vertex_supports(self, adj_mat, degrees):
        """ The support of a vertex is defined by the
            sum of the degree of the vertices which are
            adjacent to it
        """
        supports = np.zeros(degrees.shape)
        edges = np.transpose(np.nonzero(adj_mat))
        for edge in edges:
            supports[edge[0]] += degrees[edge[1]]

        return supports

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

    def __str__(self):
        res = "vertices: "
        for k in self.__graph_dict:
            res += str(k) + " "
        res += "\nedges: "
        for edge in self.__generate_edges():
            res += str(edge) + " "
        return res


if __name__ == "__main__":
    g = {"a": ["d"],
         "b": ["c"],
         "c": ["b", "c", "d", "e"],
         "d": ["a", "c"],
         "e": ["c"],
         "f": []
         }

    graph = Graph(g)
    print(graph)
