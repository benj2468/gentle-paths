from path_finder import incline, path_finder
from search_solution import SearchSolution
from terrain import TerrainGraph
from copy import deepcopy


def path_map(graph: TerrainGraph, solution: SearchSolution, theta_m: float,
             precision: int):
    path = solution.path
    if len(path) <= 1:
        return path

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
            res.path.append((prev, ))
            res.cost += dist
        else:
            sub = path_finder(graph, prev, cur, theta_m, precision)
            for elem in sub.path:
                res.path.append((elem[0], ))
            res.cost += sub.cost

    return res