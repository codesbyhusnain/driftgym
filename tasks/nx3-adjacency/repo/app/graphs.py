import networkx as nx
import numpy as np


def build_graph(edges):
    graph = nx.Graph()
    graph.add_weighted_edges_from(edges)
    return graph


def adjacency(graph, nodes):
    return nx.to_numpy_matrix(graph, nodelist=nodes).tolist()


def two_step(graph, nodes):
    matrix = nx.to_numpy_matrix(graph, nodelist=nodes)
    return (matrix * matrix).tolist()


def from_rows(rows):
    return nx.from_numpy_matrix(np.matrix(rows))


def describe(graph):
    return nx.info(graph)
