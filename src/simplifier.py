from copy import deepcopy

from terrain import Location, TerrainGraph, TerrainNode
import numpy as np

from quadric_mesh_simplification.quad_mesh_simplify import simplify_mesh


def surface_simplifier(S: TerrainGraph, num_nodes: int):
    '''
    Simplifies a graph and returns a series of simplified graphs, each one corresponding to the a number of nodes specified.
    '''
    points = np.array(list(map(lambda x: tuple(x._loc), S.nodes)))

    simplices = deepcopy(S.tri.simplices)
    simplices.dtype = np.uint32

    points, _ = simplify_mesh(
        points,
        simplices,
        num_nodes,
    )

    points = list(map(lambda x: TerrainNode('', Location(*x)), points))

    return TerrainGraph(points)


def angle_simplifier(S: TerrainGraph, theta_m: float) -> TerrainGraph:
    def removable_edges(graph: TerrainGraph) -> TerrainGraph:
        for i in range(len(graph.tri.simplices)):
            if -1 in graph.tri.neighbors[i]:
                continue
            for j, neighbor in enumerate(graph.tri.neighbors[i]):
                f1 = graph.face(i)
                f2 = graph.face(neighbor)

                if f1.angle(f2) < theta_m:
                    nodes = list(graph.tri.simplices[i])
                    nodes.pop(j)
                    yield nodes

    nodes = list(S.nodes)
    new_nodes = []
    removed = list()
    for v1, v2 in removable_edges(S):
        if v1 in removed or v2 in removed:
            continue
        n1, n2 = S.nodes[v1], S.nodes[v2]
        avg = TerrainNode(
            '',
            Location((n1._loc.x + n2._loc.x) / 2, (n1._loc.y + n2._loc.y) / 2,
                     (n1._loc.z + n2._loc.z) / 2))

        nodes.remove(n1)
        nodes.remove(n2)
        removed.append(v1)
        removed.append(v2)
        new_nodes.append(avg)

    return TerrainGraph(nodes)
