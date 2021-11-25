from __future__ import annotations
from math import asin
from typing import List, Optional, Tuple

from matplotlib import pyplot as plt
from search_solution import SearchSolution
from terrain import Location, TerrainGraph, TerrainNode
from astar import astar_search
import numpy as np


def coplaner(a, b, c, debug=False):
    a = np.array(tuple(a._loc))
    b = np.array(tuple(b._loc))
    c = np.array(tuple(c))

    d = np.subtract(a, c)
    if (d == [0, 0, 0]).all():
        return True
    dist = np.linalg.norm(d)

    d_unit = d / dist

    e = np.subtract(c, b)
    if (e == [0, 0, 0]).all():
        return True
    dist = np.linalg.norm(e)

    e_unit = e / dist

    if debug:
        print(e_unit, d_unit)

    return (e_unit == d_unit).all()


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
                 precision: float = 10,
                 debug=False,
                 ax=None) -> None:
        self.terrain = S

        self.start_state = S.find(start)
        self.destination = S.find(destination)
        self.theta_m = theta_m
        self.precision = precision
        self.debug = debug
        self.ax = ax

        if debug:
            print("Theta: ", theta_m)
            print("Precision: ", self.precision)

            if self.debug:
                debug_loc = tuple(self.start_state[0])
                self.ax.scatter(
                    debug_loc[0],
                    debug_loc[1],
                    debug_loc[2],
                )
                ax.text(debug_loc[0], debug_loc[1], debug_loc[2], 'Start')
                debug_loc = tuple(self.destination[0])
                self.ax.scatter(debug_loc[0], debug_loc[1], debug_loc[2])
                ax.text(debug_loc[0], debug_loc[1], debug_loc[2], 'End')

    def goal_test(self, state: State) -> bool:
        return self.destination[0] == state[0]

    def get_successors(self, state: State) -> Tuple[int, List[State]]:
        loc = state[0]
        if self.debug:
            print('Location: ', loc)
        for simplex in state[1:]:
            if self.debug:
                print('Simplex: ', simplex)
            if simplex == self.destination[1]:
                # Sometimes the destination will be on an edge - we can do a better
                # job if we check if it's coplanar and add it in the segmenting
                dist, inc = incline(loc, self.destination[0])
                yield (dist, (self.destination))
            if simplex == -1:
                continue
            face = self.terrain.tri.simplices[simplex]
            neighbors = list(self.terrain.tri.neighbors[simplex])

            p1 = self.terrain.nodes[face[0]]
            p2 = self.terrain.nodes[face[1]]
            p3 = self.terrain.nodes[face[2]]

            for i, (p, v) in enumerate([(p3, p2), (p1, p3), (p2, p1)]):
                if self.debug:
                    print('Triangle Edge: ', p, v)

                ## Check here if p, v, and loc are all co-planaer
                ## If they are, then yield loc with the opposite simplex

                if coplaner(p, v, loc, self.debug):
                    yield (0, (loc, simplex, neighbors[i]))

                for u in segment(p, v, self.precision):
                    dist, inc = incline(loc, u)
                    if self.debug:
                        debug_loc = tuple(u)
                        self.ax.scatter(debug_loc[0],
                                        debug_loc[1],
                                        debug_loc[2],
                                        color='k')
                    if self.debug:
                        print('Segment Incline: ', inc)
                    if inc <= self.theta_m:
                        if self.debug:
                            debug_loc = tuple(u)

                            self.ax.text(debug_loc[0], debug_loc[1],
                                         debug_loc[2], 'Valid')
                            print("Nighbor being added", neighbors[i])
                        yield (dist, (u, simplex, neighbors[i]))

        if self.debug:
            # plt.pause(0.5)
            # plt.gca()
            plt.show()

    def heuristic(self, state: State) -> int:
        return self.destination[0].distance(state[0])


def path_finder(S: TerrainGraph,
                start: Tuple[int, int] | Location,
                destination: Tuple[int, int] | Location,
                theta_m: float,
                precision: float = None,
                debug=False,
                ax=None) -> SearchSolution:

    search_problem = PathFinderSearch(S, start, destination, theta_m,
                                      precision, debug, ax)

    res = astar_search(search_problem, debug)

    return res
