from Surface import Surface
import numpy as np
from numpy.lib.function_base import flip
from Surface import Surface
from Funnel import Funnel

# generate test
def test_funnel(seed, num_points, num_edges):
    np.random.seed(seed)
    surf = Surface(num_points = num_points, is_terrain=False)
    start_edge = surf.tri.simplices[0][0:2]
    last_edge = list(start_edge)
    path = []
    while len(path) < num_edges:
        path = []
        tri_list = [list(surf.tri.simplices[0])]
        path.append(start_edge)
        for _ in range(num_edges):
            for tri in surf.tri.simplices:
                last_edge = path[-1]
                if (last_edge[0] in tri) and (last_edge[1] in tri) and not (list(tri) in tri_list):
                    vtx1 = None
                    vtx2 = None
                    while vtx1==vtx2 or (vtx1==last_edge[0] and vtx2==last_edge[1]) \
                        or (vtx2==last_edge[0] and vtx1==last_edge[1]):
                        vtx1 = np.random.choice(tri)
                        vtx2 = np.random.choice(tri)
                    path.append([vtx1, vtx2])
                    tri_list.append(list(tri))
                    break
    path = np.array(path)
    vtx_map = surf.points
    start = (vtx_map[path[0][0]] + vtx_map[path[0][1]])/2
    start[0] = start[0]+.002
    target = (vtx_map[path[-1][0]] + vtx_map[path[-1][1]])/2
    target[0] = target[0]+.02
    funnel = Funnel(surf, start, target, path, vtx_map)
    funnel.funnel()


##########TESTS###############
# seed 1, pts 50, edges = 15
test_funnel(1, 50, 15)

# seed 0, pts 30, edges = 14
test_funnel(0, 30, 14)

# seed 1, pts 30, edges = 10
test_funnel(1, 30, 10)


