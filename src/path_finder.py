from __future__ import annotations
from math import asin
from typing import List, Optional, Tuple
from search_solution import SearchSolution
from terrain import Location, TerrainGraph, TerrainNode
from astar import astar_search
import numpy as np


def segment(p: TerrainNode, r: TerrainNode, count: int) -> List[Location]:
    p_a = np.array(tuple(p._loc))
    r_a = np.array(tuple(r._loc))

    c = np.subtract(p_a, r_a)

    dist = np.linalg.norm(c)

    c_unit = c / dist

    for i in range(1, count + 1):
        cur_dist = dist * i / count
        point = np.add(r_a, (c_unit * cur_dist))
        yield Location(*tuple(point))


def incline(l1: Location, l2: Location):
    p_a = np.array(tuple(l1))
    r_a = np.array(tuple(l2))

    c = np.subtract(p_a, r_a)

    dist = np.linalg.norm(c)
    if dist == 0:
        return 0, 0

    dz = abs(l1.z - l2.z)

    return (dist, asin(dz / dist))


class PathFinderSearch():
    State = Tuple[Location, int, Optional[int]]

    def __init__(self,
                 S: TerrainGraph,
                 start: Tuple[int, int] | Location,
                 destination: Tuple[int, int] | Location,
                 theta_m: float,
                 precision: float = 10) -> None:
        self.terrain = S

        start = S.find(start)
        self.start_state = (start[0], start[1])
        self.destination = S.find(destination)
        self.theta_m = theta_m
        self.precision = precision

    def goal_test(self, state: State) -> bool:
        return self.destination[0] == state[0]

    def get_successors(self, state: State) -> Tuple[int, List[State]]:
        loc = state[0]
        for simplex in state[1:]:
            if simplex == self.destination[1]:
                dist, inc = incline(loc, self.destination[0])
                if inc <= self.theta_m:
                    yield (dist, (self.destination))
            if simplex == -1:
                continue
            face = self.terrain.tri.simplices[simplex]
            neighbors = list(self.terrain.tri.neighbors[simplex])

            p1 = self.terrain.nodes[face[0]]
            p2 = self.terrain.nodes[face[1]]
            p3 = self.terrain.nodes[face[2]]

            for i, (p, v) in enumerate([(p3, p2), (p1, p3), (p2, p1)]):
                for u in segment(p, v, self.precision):
                    dist, inc = incline(loc, u)
                    if inc <= self.theta_m:
                        yield (dist, (u, simplex, neighbors[i]))

    def heuristic(self, state: State) -> int:
        return self.destination[0].distance(state[0])


def path_finder(S: TerrainGraph,
                start: Tuple[int, int] | Location,
                destination: Tuple[int, int] | Location,
                theta_m: float,
                precision: float = None) -> SearchSolution:

    search_problem = PathFinderSearch(S, start, destination, theta_m,
                                      precision)

    res = astar_search(search_problem)

    if len(res.path):
        res.path.append(search_problem.destination)

    return res
