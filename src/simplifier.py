from math import sin, degrees
from typing import List
from matplotlib import pyplot as plt

from numpy.random import choice
from random import sample
from terrain import Face, TerrainGraph
from time import time
import numpy as np

from quadric_mesh_simplification.quad_mesh_simplify import simplify_mesh


def surface_simplifier(S: TerrainGraph, theta_m: float, eps: float):
    points = np.array(list(map(lambda x: tuple(x._loc), S.nodes)))
    S.tri.simplices.dtype = np.uint32

    points, new_faces = simplify_mesh(
        points,
        S.tri.simplices,
        num_nodes=len(points) / 5,
    )

    ax = plt.axes(projection='3d')
    ax.plot_trisurf(points[:, 0],
                    points[:, 1],
                    points[:, 2],
                    cmap='viridis',
                    edgecolor='none')
    plt.show()


# def surface_simplifier(S: TerrainGraph, theta_m: float, eps: float):
#     def delta(surface_tilde: TerrainGraph) -> float:
#         m = 0
#         for simplex in S.tri.simplices:
#             s = time()
#             tri = list(map(lambda x: S.nodes[x], simplex))
#             face = Face(tri)
#             o_faces = surface_tilde.overlapping_faces(face)
#             for o_face in o_faces:
#                 # m = max(m, lam(face, o_face))
#                 m = max(m, face.angle(o_face))
#             # print('for a simplex', time() - s)
#             # m = max(m, abs(o_face.angle() - face.angle()))
#         # for face in affected_faces:
#         #     o_faces = , affected_v)
#         #     if len(o_faces) == 0:
#         #         S.overlapping_faces(face, affected_v, True)
#         #         print('broohaha')
#         #         exit(1)
#         #     for o_face in o_faces:
#         #         # m = max(m, abs(o_face.angle() - face.angle()))
#         #         m = max(m, lam(o_face, face))

#         return m

#     def lam(face: Face, face_t: Face) -> float:
#         res = mr(face, face_t) * mr(face_t, face)
#         return res

#     def mr(face: Face, face_t: Face) -> float:
#         theta_t_max = round(min(theta_m, face_t.angle()), 3)
#         psuedo_path_slope = lambda x: x * face.angle(face_t)

#         def maximize(theta) -> float:
#             return (sin(max(psuedo_path_slope(theta), theta_m)) /
#                     sin(theta_m)) * (theta / psuedo_path_slope(theta))

#         m = float('-inf')
#         count = 10
#         for i in range(1, int(count * theta_t_max)):
#             if i == 0:
#                 continue
#             i = i / count
#             v = maximize(i)
#             m = max(v, m)

#         return m

#     # Here we will perform a simple BFS - we want to find the node that satisfies the constraints that has the fewest vertices.
#     # Keep removing vertices until we cant

#     queue = [S]

#     while len(queue):
#         surface = queue.pop(0)

#         last = len(queue) == 0
#         if len(surface.nodes) < 10:
#             return surface
#         for node in surface.nodes:
#             surface_tilde = surface.remove_node_new(node)
#             de = delta(surface_tilde)
#             print(de, len(surface.nodes))
#             # if de < .05:
#             if de < 1 + eps:
#                 queue = [surface_tilde] + queue
#         # vertices_to_remove = choice(surface.nodes, 10, replace=False)
#         # surface_tilde = surface.remove_node_new(vertices_to_remove[0])
#         # for v in vertices_to_remove[1:]:
#         #     surface_tilde = surface_tilde.remove_node_new(v)

#         # de = delta(surface_tilde)
#         # print(de, len(surface_tilde.nodes))
#         # if de < 0.0001:
#         #     queue = [surface_tilde] + queue

#         if last and len(queue) == 0:
#             return surface
