from __future__ import annotations
from functools import reduce
from collections import defaultdict
from typing import Any, Generator, List, Mapping, Optional, Set, Tuple
from numpy import array, linalg
import numpy
from math import acos, sqrt

from tri_collide import TriTri2D


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
    def __init__(self, label: int, location: Location):
        self._label = label
        self._loc = location
        super().__init__()

    def get_height(self) -> int:
        return self._loc.z

    def get_label(self) -> int:
        return self._label

    def __str__(self) -> str:
        return f"{self._label}"

    def __eq__(self, other: TerrainNode) -> bool:
        return self._label == other._label and self._loc == other._loc

    def __hash__(self) -> int:
        return (self._label, self._loc).__hash__()


class Dart(object):
    def __init__(self, source: TerrainNode, destination: TerrainNode) -> None:
        self.source = source
        self.destination = destination
        super().__init__()

    def __hash__(self) -> int:
        return (self.source, self.destination).__hash__()

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
        self.nodes.append(node)

    def proj(self) -> Generator[Tuple[int, int]]:
        if len(self.nodes) != 3:
            print("Can only determine projection of triangle")
            return

        return map(lambda x: x._loc.proj(), self.nodes)

    def angle(self) -> float:
        if len(self.nodes) != 3:
            print("Can only determine angle of a plane")
            return

        points = list(map(lambda x: numpy.array(tuple(x._loc)), self.nodes))
        p1 = points[0]
        p2 = points[1]
        p3 = points[2]

        v1 = p3 - p1
        v2 = p2 - p1

        # the cross product is a vector normal to the plane
        cp = numpy.cross(v1, v2)

        xy_norm = numpy.array([0, 0, 1])

        return acos(
            numpy.dot(xy_norm, cp) /
            (numpy.linalg.norm(cp) * numpy.linalg.norm(xy_norm)))

    def __str__(self) -> str:
        return ", ".join(map(str, self.nodes))


class TerrainGraph(object):
    def __init__(self) -> None:
        self.rot: Mapping[TerrainNode, List[TerrainNode]] = defaultdict(None)
        self.faces: Mapping[TerrainNode, Set[Face]] = defaultdict(None)
        self.dart_faces: Mapping[Dart, Face] = defaultdict(None)
        self.all_faces: Set[Face] = set()
        super().__init__()

    def add_node(self, node: TerrainNode):
        self.rot[node] = []
        self.faces[node] = set()

    def add_edge(self, n1: TerrainNode, n1_loc: int, n2: TerrainNode,
                 n2_loc: int):
        if not n1 in self.rot or not n2 in self.rot:
            raise ("Cannot add edge between nonexistnet nodes")

        self.rot[n1] = self.rot[n1][:n1_loc] + [n2] + self.rot[n1][n1_loc:]
        self.rot[n2] = self.rot[n2][:n2_loc] + [n1] + self.rot[n2][n2_loc:]

        ## Fix the faces

        ## Check if this edge closes a cycle
        def add_dart(a, b):
            start = Dart(a, b)
            cur = start
            path = []
            while cur:
                if cur.destination == start.source:
                    path += [cur]
                    face = Face.from_darts(path)
                    for dart in path:
                        if str(dart) in self.dart_faces and self.dart_faces[
                                str(dart)] in self.all_faces:
                            self.all_faces.remove(self.dart_faces[str(dart)])
                        self.dart_faces[str(dart)] = face
                    for v in face.nodes:
                        self.faces[v].add(face)
                    self.all_faces.add(face)
                    break
                if cur in path:
                    break
                path += [cur]
                cur = self.next(cur)

        add_dart(n1, n2)
        add_dart(n2, n1)

    def remove_node(self, node: TerrainNode):
        # TODO
        # This needs to be done that that we can perform the BFS and actually simplify the graph
        pass

    def next(self, dart: Dart) -> Optional[Dart]:
        (source, destination) = (dart.source, dart.destination)
        rotation = self.rot[destination]

        source_index = rotation.index(source)
        next_index = (source_index + 1) % len(rotation)
        if next_index == source_index:
            return None

        return Dart(destination, rotation[next_index])

    def overlapping_faces(self, face: Face) -> Generator[Face]:
        for face in self.all_faces:
            yield TriTri2D(self.proj(), face.proj())

    def triangulate(self):
        # TODO
        # This needs to get done - when we remove a vertex, we need to re-triangulate the graph
        # We might be able to do this faster
        pass

    def __str__(self) -> str:
        res = ''
        for k in self.rot:
            neighbors = ', '.join(map(str, self.rot[k]))
            res += f"{str(k)}\t: {neighbors}\n"

        return res


graph = TerrainGraph()

a = TerrainNode("A", Location(1, 0, 5))
b = TerrainNode("B", Location(1, 1, 10))
c = TerrainNode("C", Location(0, 1, 5))
d = TerrainNode("D", Location(0, 0, 0))

graph.add_node(a)
graph.add_node(b)
graph.add_node(c)
graph.add_node(d)

graph.add_edge(a, 0, b, 0)
graph.add_edge(b, 1, c, 0)
graph.add_edge(c, 1, d, 0)
graph.add_edge(d, 1, a, 1)
graph.add_edge(a, 1, c, 0)

for face in graph.all_faces:
    print(face)

    print(face.angle())
