from __future__ import annotations
from functools import reduce
from collections import defaultdict
from typing import Any, Generator, List, Mapping, Optional, Set, Tuple
import numpy as np
from numpy.random.mtrand import randint
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
from math import acos, pi
from mpl_toolkits import mplot3d

from tri_collide import TriTri2D


def gather_points(p1, p2, count):
    (x, y) = p1
    (x2, y2) = p2
    dx = abs(x2 - x)
    dy = abs(y2 - y)
    for i in range(1, count + 1):
        c_x = (dx / float(i))
        c_y = (dy / dx) * c_x if dx != 0 else (dy / float(i))

        yield c_x + x, c_y + y


def split_cycle(list: List[Any], i: int,
                j: int) -> Tuple[List[Any], List[Any]]:
    l1 = []
    l2 = []
    k = i
    filling = 0
    while len(l1) + len(l2) < len(list) + 2:
        if not filling:
            l1.append(list[k])
        else:
            l2.append(list[k])
        if k == j and not filling:
            filling = not filling
        else:
            k += 1
            k %= len(list)

    return (l1, l2)


class Location(object):
    def __init__(self, x: int, y: int, z: int) -> None:
        self.x = x
        self.y = y
        self.z = z
        super().__init__()

    def proj(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def __iter__(self):
        for i in (self.x, self.y, self.z):
            yield i

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))

    def __eq__(self, other: Location) -> bool:
        return hash(self) == hash(other)

    def __str__(self) -> str:
        return f'({self.x}, {self.y}, {self.z})'


class TerrainNode(object):
    def __init__(self, label: Any, location: Location):
        self._label = label
        self._loc = location
        super().__init__()

    def get_height(self) -> int:
        return self._loc.z

    def get_label(self) -> Any:
        return self._label

    def proj(self) -> Tuple[int, int]:
        return self._loc.proj()

    def __str__(self) -> str:
        return f"{self._label}"

    def __eq__(self, other: TerrainNode) -> bool:
        return self._label == other._label and self._loc == other._loc

    def __hash__(self) -> int:
        return hash((self._label, self._loc))


class Dart():
    def __init__(self, source: TerrainNode, destination: TerrainNode) -> None:
        self.source = source
        self.destination = destination

    def __hash__(self) -> int:
        return hash((self.source, self.destination))

    def __eq__(self, o: Dart) -> bool:
        return hash(self) == hash(o)

    def __str__(self) -> str:
        return f"{self.source} -> {self.destination}"


class Face(object):
    def __init__(self, nodes: List[TerrainNode]) -> None:
        self.nodes = nodes
        super().__init__()

    def from_darts(darts: List[Dart]) -> Face:
        nodes = []
        for dart in darts:
            nodes.append(dart.destination)
        return Face(nodes)

    def add_node(self, node: TerrainNode):
        self.nodes = np.append(self.nodes, [node])

    def proj(self) -> Generator[Tuple[int, int]]:
        if len(self.nodes) != 3:
            print("Can only determine projection of triangle")
            return

        return list(map(lambda x: x._loc.proj(), self.nodes))

    def tangent_vector(self) -> np.ndarray:
        if len(self.nodes) != 3:
            print("Can only determine angle of a plane")
            return
        points = list(map(lambda x: np.array(tuple(x._loc)), self.nodes))
        p1 = points[0]
        p2 = points[1]
        p3 = points[2]

        v1 = p3 - p1
        v2 = p2 - p1

        # the cross product is a vector normal to the plane
        cp = np.cross(v1, v2)
        norm = np.linalg.norm(cp, ord=1)
        if norm == 0:
            norm = np.finfo(cp.dtype).eps
        return cp / norm

    def angle(self, otherFace: Face = None) -> float:

        cp = self.tangent_vector()

        other = np.array([0, 0, 1
                          ]) if not otherFace else otherFace.tangent_vector()

        val = (np.dot(other, cp) /
               (np.linalg.norm(cp) * np.linalg.norm(other))).round(8)

        return acos(val)

    def __hash__(self) -> str:
        if len(self.nodes) != 3:
            raise ("bad face")
        return hash((self.nodes[0], self.nodes[1], self.nodes[2]))

    def __eq__(self, o: Face) -> bool:
        return hash(self) == hash(o)

    def __str__(self) -> str:
        return ", ".join(map(str, self.nodes))


class TerrainGraph(object):
    def __init__(self, nodes: List[TerrainNode]) -> None:
        self.nodes: List[TerrainNode] = np.array(nodes)
        self._2d: List[Tuple[int, int]] = list(map(lambda x: x.proj(), nodes))
        self._update_faces()
        super().__init__()

    def _update_faces(self):
        self.tri = Delaunay(self._2d) if len(self.nodes) >= 3 else None
        self.faces = list(
            map(Face,
                map(lambda x: self.nodes[x],
                    self.tri.simplices))) if len(self.nodes) >= 3 else None

    def add_node(self, node: TerrainNode):
        self.nodes = np.append(self.nodes, [node])
        self._2d.append(node.proj())
        self._update_faces()

    def remove_node(self, node: TerrainNode):
        idx = np.where(self.nodes == node)[0][0]
        self.nodes = np.delete(self.nodes, idx)
        self._2d.remove(node.proj())
        self._update_faces()

    def neighboring_faces(self, idx: int):
        neighboring_faces = []
        for s in self.tri.neighbors[idx]:
            if s == -1:
                continue
            f = Face(list(map(lambda x: self.nodes[x], self.tri.simplices[s])))
            neighboring_faces.append(f)
        return neighboring_faces

    def remove_node_new(self, node: TerrainNode):
        idx = np.where(self.nodes == node)[0][0]
        # affected_v = []
        # for s in self.tri.neighbors[idx]:
        #     for v in self.tri.simplices[s]:
        #         affected_v.append(v)
        nodes = np.delete(self.nodes, idx)
        return TerrainGraph(nodes)
        # , affected_v

    def overlapping_faces(self, face: Face) -> Set[Face]:
        res = set()
        # points = list(map(lambda x: x._loc.proj(), face.nodes))
        # t1 = points[0]
        # t2 = points[1]
        # t3 = points[2]
        # points = list(gather_points(t1, t2, 10)) + list(
        #     gather_points(t2, t3, 10)) + list(gather_points(t1, t3, 10))
        # overlapping = self.tri.find_simplex(points)
        # for o in overlapping:
        #     simplex = self.tri.simplices[o]
        #     tri = list(map(lambda x: self.nodes[x], simplex))
        #     res.add(Face(tri))

        for simplex in self.tri.simplices:
            tri = list(map(lambda x: self.nodes[x], simplex))
            f = Face(tri)
            if TriTri2D(f.proj(), face.proj()):
                res.add(f)

        return res

    def plot(self):
        points = np.array(list(map(lambda x: tuple(x._loc), self.nodes)))
        ax = plt.axes(projection='3d')
        ax.plot_trisurf(points[:, 0],
                        points[:, 1],
                        points[:, 2],
                        cmap='viridis',
                        edgecolor='none')
        plt.show()

        # plt.triplot(points[:, 0], points[:, 1], self.tri.simplices)
        # plt.plot(points[:, 0], points[:, 1], 'o')
        # plt.show()

    def triangulate(self):
        if len(self.nodes) >= 3:
            self.tri = Delaunay(self._2d)

    def __str__(self) -> str:
        if self.tri:
            return str(self.tri.simplices)
        else:
            f = ""
            for n in self.nodes:
                f += f'{n}\n'
            return f

    def init_random(i):
        points = np.random.rand(i, 4)
        nodes = []
        for p in points:
            node = TerrainNode(hex(round(p[0] * 10000)),
                               Location(p[1] * 100, p[2] * 100, p[3] * 100))
            nodes.append(node)

        return TerrainGraph(nodes)

    def init_flat(i):
        points = np.random.rand(i, 3)
        nodes = []
        for p in points:
            node = TerrainNode(hex(round(p[0] * 10000)),
                               Location(p[1] * 100, p[2] * 100, 0))
            nodes.append(node)

        return TerrainGraph(nodes)

    def init_file(file_name: str):
        with open(file_name) as f:
            nodes = []
            for l in f.readlines():
                l = l.split(' ')
                y = float(l[0])
                x = float(l[1])
                z = float(l[2])
                node = TerrainNode(hex(randint(0, 10000)), Location(x, y, z))
                nodes.append(node)

        return TerrainGraph(nodes)
