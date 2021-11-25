from typing import List, Tuple
from path_finder import incline, path_finder
from search_solution import SearchSolution
from terrain import TerrainGraph
from copy import deepcopy


def path_map(graph: TerrainGraph, solution: SearchSolution, theta_m: float,
             precision: int, ax):
    path = solution.path
    if len(path) <= 1:
        return solution

    loc_path = list(map(lambda x: x[0], path))
    res = deepcopy(solution)
    res.path = []
    res.cost = 0
    for i in range(1, len(path) - 1):
        prev = loc_path[i - 1]
        cur = loc_path[i]

        prev, p_simplex = graph.find(prev)
        cur, c_simplex = graph.find(cur)

        dist, inc = incline(prev, cur)

        if p_simplex == c_simplex and inc <= theta_m:
            print("Not Mapping")
            res.path.append((prev, ))
            res.cost += dist
        else:
            print(f"Mapping, {p_simplex}, {c_simplex} w/ angle: {inc}")
            debug = False
            sub = path_finder(graph,
                              prev,
                              cur,
                              theta_m,
                              precision,
                              debug=debug,
                              ax=ax)

            if sub.cost == float('inf'):
                print("Could not find path")
                res.cost = float('inf')
                res.path = []
                return res
            for elem in sub.path:
                res.path.append((elem[0], ))
            res.cost += sub.cost

    return res


def translate_path(S: TerrainGraph,
                   solution: SearchSolution) -> List[Tuple[int, int]]:
    path = solution.path

    simplices = [path[0][1]]
    i = 1
    while i < len(path) - 1:
        if path[i][1] != simplices[-1]:
            simplices[-1] = path[i][2]
        else:
            simplices.append(path[i][2])
        i += 1

    i = 1
    res = []
    while i < len(simplices):

        prev = S.tri.simplices[simplices[i - 1]]
        cur = S.tri.simplices[simplices[i]]
        intersection = []
        for j in prev:
            if j in cur:
                intersection.append(j)
        if len(intersection) < 2:
            print("false intersection", prev, cur)
            exit()
        res.append(tuple(intersection))
        i += 1

    return res