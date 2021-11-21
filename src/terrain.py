from __future__ import annotations
from typing import Any, Generator, List, Tuple
import numpy as np
from numpy.random.mtrand import randint
from scipy.spatial import Delaunay, distance


class Location(object):
    def __init__(self, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        super().__init__()

    def proj(self) -> Tuple[int, int]:
        return (self.x, self.y)

    def distance(self, o: Location) -> int:
        return distance.euclidean((self.x, self.y, self.z), (o.x, o.y, o.z))

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
        return f"{self._loc}"

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

        return (np.arccos(val))

    def find(self, loc: Tuple[int, int]) -> Location:
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
        d = np.dot(p1, cp)

        z = (d - cp[0] * loc[0] - cp[1] * loc[1]) / cp[2]

        return Location(loc[0], loc[1], z)

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

    def find(self, loc: Tuple[int, int]) -> Tuple[Location, int]:
        if type(loc) == Location:
            simplex = self.tri.find_simplex([tuple(loc)[:2]])[0]
        else:
            simplex = self.tri.find_simplex([loc])[0]
        face = Face(
            list(map(lambda x: self.nodes[x], self.tri.simplices[simplex])))

        if not type(loc) == Location:
            loc = face.find(loc)
        return loc, simplex

    ## Plotting
    def plot(self, ax):
        points = np.array(list(map(lambda x: tuple(x._loc), self.nodes)))

        ax.plot_trisurf(points[:, 0],
                        points[:, 1],
                        points[:, 2],
                        cmap='viridis',
                        alpha=.7,
                        edgecolor='k',
                        linewidth=.1)

    def plot_2d(self, ax):
        points = np.array(list(map(lambda x: tuple(x._loc), self.nodes)))

        ax.triplot(
            points[:, 0],
            points[:, 1],
        )

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
