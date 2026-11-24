from app.graphs import adjacency, build_graph, describe, from_rows, two_step

PATH = [("p", "q", 1.5), ("q", "r", 2), ("r", "s", 4)]


def test_path_graph_in_another_order():
    graph = build_graph(PATH)
    nodes = ["s", "q", "p", "r"]
    assert adjacency(graph, nodes) == [[0.0, 0.0, 0.0, 4.0], [0.0, 0.0, 1.5, 2.0], [0.0, 1.5, 0.0, 0.0], [4.0, 2.0, 0.0, 0.0]]
    assert two_step(graph, nodes) == [
        [16.0, 8.0, 0.0, 0.0],
        [8.0, 6.25, 0.0, 0.0],
        [0.0, 0.0, 2.25, 3.0],
        [0.0, 0.0, 3.0, 20.0],
    ]


def test_from_rows():
    graph = from_rows([[0, 3, 0], [3, 0, 1], [0, 1, 0]])
    assert sorted(graph.nodes) == [0, 1, 2]
    assert sorted((u, v, w) for u, v, w in graph.edges(data="weight")) == [(0, 1, 3), (1, 2, 1)]
    assert describe(graph) == "Graph with 3 nodes and 2 edges"


def test_isolated_node():
    graph = build_graph([("x", "y", 1)])
    graph.add_node("z")
    assert describe(graph) == "Graph with 3 nodes and 1 edges"
    assert adjacency(graph, ["x", "y", "z"]) == [[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    assert two_step(graph, ["x", "y", "z"]) == [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 0.0]]
