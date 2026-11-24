from app.graphs import adjacency, build_graph, describe, two_step

EDGES = [("a", "b", 2), ("b", "c", 1), ("a", "c", 5)]


def test_adjacency_and_describe():
    graph = build_graph(EDGES)
    assert adjacency(graph, ["a", "b", "c"]) == [[0.0, 2.0, 5.0], [2.0, 0.0, 1.0], [5.0, 1.0, 0.0]]
    assert describe(graph) == "Graph with 3 nodes and 3 edges"


def test_two_step():
    assert two_step(build_graph(EDGES), ["a", "b", "c"]) == [[29.0, 5.0, 2.0], [5.0, 5.0, 10.0], [2.0, 10.0, 26.0]]
