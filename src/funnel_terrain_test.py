from typing import List, Tuple
from terrain import Face, TerrainGraph, Location, TerrainNode
import numpy as np
from homotopy.Surface import Surface
from homotopy.Funnel import Funnel
from homotopy.FunnelVisualizer import FunnelVisualizer
from scipy.interpolate import interp1d, interp2d
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import time


#https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
def sign(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] -
                                                                  p3[1])


def point_in_traingle(pt, tri):
    v1, v2, v3 = tri
    d1 = sign(pt, v1, v2)
    d2 = sign(pt, v2, v3)
    d3 = sign(pt, v3, v1)
    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)


#https://stackoverflow.com/questions/5507762/how-to-find-z-by-arbitrary-x-y-coordinates-within-triangle-if-you-have-triangle
def calcY(p1, p2, p3, x, z):
    det = (p2.y - p3.y) * (p1.x - p3.x) + (p3.x - p2.x) * (p1.y - p3.y)

    l1 = ((p2.y - p3.y) * (x - p3.x) + (p3.x - p2.x) * (z - p3.y)) / det
    l2 = ((p3.y - p1.y) * (x - p3.x) + (p1.x - p3.x) * (z - p3.y)) / det
    l3 = 1.0 - l1 - l2

    return l1 * p1.z + l2 * p2.z + l3 * p3.z


def construct_random_path(surf, hole_tris):
    start_edge = surf.tri.simplices[int(np.random.rand() *
                                        len(surf.tri.simplices))][0:2]
    last_edge = list(start_edge)
    path = []
    start = time.time()
    while len(path) < num_edges and (time.time() - start < 20):
        path = []
        tri_list = [list(surf.tri.simplices[0])]
        path.append(start_edge)
        for _ in range(num_edges):
            for tri in surf.tri.simplices:
                last_edge = path[-1]

                tri_test = [
                    tuple(surf.points[tri[0]]),
                    tuple(surf.points[tri[1]]),
                    tuple(surf.points[tri[2]])
                ]
                skip_tri = False

                append_tris = []
                for trih in hole_tris:
                    p0 = point_in_traingle(trih[0], tri_test)
                    p1 = point_in_traingle(trih[1], tri_test)
                    p2 = point_in_traingle(trih[2], tri_test)
                    if p0 and p1:
                        append_tris.append((0, 1))
                    if p0 and p2:
                        append_tris.append((0, 2))
                    if p1 and p2:
                        append_tris.append((1, 2))

                    if point_in_traingle(
                            trih[0], tri_test) and point_in_traingle(
                                trih[1], tri_test) and point_in_traingle(
                                    trih[2], tri_test):
                        skip_tri = True
                        break

                if not skip_tri and len(append_tris) < 2:
                    if (last_edge[0] in tri) and (
                            last_edge[1]
                            in tri) and not (list(tri) in tri_list):
                        vtx1 = None
                        vtx2 = None
                        start_new = time.time()
                        while vtx1==vtx2 or (vtx1==last_edge[0] and vtx2==last_edge[1]) \
                            or (vtx2==last_edge[0] and vtx1==last_edge[1]):
                            vtx1 = np.random.choice(tri)
                            vtx2 = np.random.choice(tri)
                            if (time.time() - start_new > .5):
                                skip_tri = True
                                break
                        if not skip_tri:
                            path.append([vtx1, vtx2])
                            tri_list.append(list(tri))
                            break
                if ((time.time() - start > 20)):
                    break
            if ((time.time() - start > 20)):
                break
    path = np.array(path)
    return path


def test_funnel_terrain(seed, surf, hole_tris, graph, random=True, path=None):
    np.random.seed(seed)
    if random:
        path = construct_random_path(surf, hole_tris)
    vtx_map = surf.points
    start = (vtx_map[path[0][0]] + vtx_map[path[0][1]]) / 2
    start[0] = start[0] + .002
    startz = (surf.zs[path[0][0]] + surf.zs[path[0][1]]) / 2
    target = (vtx_map[path[-1][0]] + vtx_map[path[-1][1]]) / 2
    targetz = (surf.zs[path[-1][0]] + surf.zs[path[-1][1]]) / 2
    target[0] = target[0] + .02
    funnel = Funnel(surf, start, target, path, vtx_map, holes=hole_tris)
    path = np.array(funnel.funnel(visualize=True))
    xs = path[:, 0]
    ys = path[:, 1]
    pts = [(x, y) for x, y in zip(xs, ys)]
    zs = []
    for idx, pt in enumerate(pts):
        if idx > 0 and idx != len(pts) - 1:
            for face in graph.faces:
                tri = [(face.nodes[0]._loc.x, face.nodes[0]._loc.y),
                       (face.nodes[1]._loc.x, face.nodes[1]._loc.y),
                       (face.nodes[2]._loc.x, face.nodes[2]._loc.y)]
                if point_in_traingle(pt, tri) or (pt == tri[0]) or (
                        pt == tri[1]) or (pt == tri[2]):
                    loc = Location(pt[0], pt[1], 0)
                    zs.append(face.find(pt))
                    break
    zs = [(loc.z) for loc in zs]
    plt.figure()
    zs.insert(0, startz)
    zs.append(targetz)
    ax = plt.axes(projection='3d')
    ax.plot(xs, ys, zs, color='k', linewidth=2)
    graph.plot(ax=ax)
    plt.show()

    data = []
    for node in graph.nodes:
        data.append([node._loc.x, node._loc.y, node._loc.z])
    data = np.array(data, dtype=np.int64)

    Long = data[:, 0]
    Lat = data[:, 1]
    Elev = data[:, 2]
    #Variables
    pts = 100000  #Input the desired number of points here

    [x, y] = np.meshgrid(
        np.linspace(np.min(Long), np.max(Long), num=int(np.sqrt(pts))),
        np.linspace(np.min(Lat), np.max(Lat), num=int(np.sqrt(pts))))
    z = griddata((Long, Lat), Elev, (x, y), method='linear')
    x = np.matrix.flatten(x)
    #Gridded longitude
    y = np.matrix.flatten(y)
    #Gridded latitude
    z = np.matrix.flatten(z)
    #Gridded elevation

    plt.scatter(x, y, 1, z)
    plt.colorbar(label='Elevation')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.plot(xs, ys, color='k')


def visualize_projection_and_holes(graph, surf, tri_holes):
    fv = FunnelVisualizer(surf)
    hole_tris = np.array(tri_holes)
    # print(hole_tris.shape)
    for tri in hole_tris:
        plt.fill(tri[:, 0], tri[:, 1], 'k', alpha=1)
    fv.plot_surface()


########TESTS#############

# seed = 2
# num_edges = 10
# angle = 177
# path = [(170, 65), (65, 22), (129, 22), (129, 97), (29, 97), (72, 97),
#         (66, 97), (66, 178), (178, 56), (178, 175), (175, 15), (148, 15),
#         (79, 15)]

#seed = 11
#num_edges = 8
#angle = 175
#path = [(85,5),(87,5),(60,5),(60,69),(107,69),(107,100),(100,2),(2,30),(30,93),(30,74),(30,31),(16,31),(16,71),(16,24),(16,84),(84,99)]

# graph = TerrainGraph.init_file("./data/homotopy_one.txt")


def funnel_test(graph: TerrainGraph, theta_m: float, seed: int,
                path: List[Tuple[int, int]]):
    hole_tris = []
    points = set()
    zmap = dict()
    node_idx_map = dict()

    all_nodes = []
    for (s, e) in path:
        all_nodes.extend([s, e])

    for simplex in graph.tri.simplices:
        contained = False
        nodes = list(
            map(
                lambda x:
                (x, TerrainNode('',
                                graph.find(graph.tri.points[x])[0])), simplex))

        for n in nodes:
            if n[0] in all_nodes:
                contained = True
        face = Face(
            list(
                map(
                    lambda x: TerrainNode('',
                                          graph.find(graph.tri.points[x])[0]),
                    simplex)))
        if face.angle() < theta_m or contained:
            tri = []
            for node in nodes:
                tri.append(node[1].proj())
                points.add(node[1].proj())
                node_idx_map[node[0]] = node[1].proj()
                zmap[node[1].proj()] = node[1]._loc.z
            hole_tris.append(tri)

    point_list = []
    zs = []
    for point in points:
        point_list.append(list(point))
        zs.append(zmap[point])

    fixed_path = []
    for (s, e) in path:
        s_fixed = point_list.index(list(node_idx_map[s]))
        e_fixed = point_list.index(list(node_idx_map[e]))
        fixed_path.append((s_fixed, e_fixed))

    points = np.array(point_list)

    zs = np.array(zs)

    surf = Surface(num_points=None,
                   is_terrain=True,
                   init_random=False,
                   points=points,
                   zs=zs)

    visualize_projection_and_holes(graph, surf, hole_tris)
    # #graph.plot()
    test_funnel_terrain(seed,
                        surf,
                        hole_tris,
                        graph,
                        random=False,
                        path=fixed_path)

    plt.show()
