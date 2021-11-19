from typing import List
from terrain import Location, TerrainGraph, TerrainNode
import numpy as np

from quadric_mesh_simplification.quad_mesh_simplify import simplify_mesh


def surface_simplifier(S: TerrainGraph, num_nodes: List[int]):
    '''
    Simplifies a graph and returns a series of simplified graphs, each one corresponding to the a number of nodes specified.
    '''
    points = np.array(list(map(lambda x: tuple(x._loc), S.nodes)))
    S.tri.simplices.dtype = np.uint32

    for n in num_nodes:
        points, = simplify_mesh(
            points,
            S.tri.simplices,
            num_nodes=n,
        )

        points = list(map(lambda x: TerrainNode('', Location(*x)), points))

        yield TerrainGraph(points)