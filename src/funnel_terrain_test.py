from terrain import TerrainGraph, Location
import numpy as np
from homotopy.Surface import Surface
from homotopy.Funnel import Funnel
from homotopy.FunnelVisualizer import FunnelVisualizer
from scipy.interpolate import interp1d, interp2d
import matplotlib.pyplot as plt

#https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
def sign(p1, p2, p3):
    return (p1[0]-p3[0])*(p2[1]-p3[1]) - (p2[0]-p3[0])*(p1[1]-p3[1])

def point_in_traingle(pt, tri):
    v1, v2, v3 = tri
    d1 = sign(pt, v1, v2)
    d2 = sign(pt, v2, v3)
    d3 = sign(pt, v3, v1)
    has_neg = (d1 <= 0) or (d2 <= 0) or (d3 <= 0)
    has_pos = (d1 >= 0) or (d2 >= 0) or (d3 >= 0)

    return not (has_neg and has_pos)

#https://stackoverflow.com/questions/5507762/how-to-find-z-by-arbitrary-x-y-coordinates-within-triangle-if-you-have-triangle
def calcY(p1, p2, p3, x, z):
    det = (p2.y - p3.y) * (p1.x - p3.x) + (p3.x - p2.x) * (p1.y - p3.y)

    l1 = ((p2.y - p3.y) * (x - p3.x) + (p3.x - p2.x) * (z - p3.y)) / det
    l2 = ((p3.y - p1.y) * (x - p3.x) + (p1.x - p3.x) * (z - p3.y)) / det
    l3 = 1.0 - l1 - l2

    return l1 * p1.z + l2 * p2.z + l3 * p3.z

def test_funnel_terrain(seed, surf, num_edges, hole_tris, graph):     
    np.random.seed(seed)
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

                tri_test = [tuple(surf.points[tri[0]]), tuple(surf.points[tri[1]]), tuple(surf.points[tri[2]])]
                skip_tri = False
                for trih in hole_tris:
                    if point_in_traingle(trih[0],tri_test) and point_in_traingle(trih[1],tri_test)  and point_in_traingle(trih[2],tri_test):
                        skip_tri = True
                        break

                if not skip_tri:
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
    funnel = Funnel(surf, start, target, path, vtx_map, holes=hole_tris)
    path = np.array(funnel.funnel(visualize=True))
    #f = interp1d(path[:,0], path[:,1], kind='linear')
    #xmin, xmax = min(path[:,0]), max(path[:,0])
    #ymin, ymax = min(path[:,1]), max(path[:,1])
    #xs = np.linspace(xmin, xmax)
    #ys = np.linspace(ymin, ymax)
    xs = path[:,0]
    ys = path[:,1]
    pts = [(x,y) for x,y in zip(xs,ys)]
    pts_loc = [Location(x,y,0) for x,y in zip(xs,ys)]
    zs = []
    """
    for pt in pts:
        for face in graph.faces:
            tri = face.proj()
            if point_in_traingle(pt, tri):
                zs.append(calcY(face.nodes[0]._loc, face.nodes[1]._loc, face.nodes[2]._loc, pt[0], pt[1]))
                break;
    """
    idxes = []
    for idx, pt in enumerate(pts):
        for node in graph.nodes:
            if node._loc.x == pt[0] and node._loc.y == pt[1]:
                zs.append(node._loc.z);
                idxes.append(int(idx))
                break;
    print(len(zs))
    print(len(xs[(idxes)]))
    print(len(ys[(idxes)]))
    #fig = plt.figure()
    #zs = [0 for x in xs]
    #ax = plt.axes(projection='3d')
    #ax.plot(xs[(idxes)], ys[(idxes)], zs, color='k', linewidth=2)
    #graph.plot(ax=ax)
    #plt.show()

def visualize_projection_and_holes(graph, surf, tri_holes):
    fv = FunnelVisualizer(surf)    
    hole_tris = np.array(tri_holes)
    print(hole_tris.shape)
    for tri in hole_tris:
        plt.fill(tri[:, 0], tri[:, 1], 'm', alpha=.5)
    fv.plot_surface()


        

########TESTS#############
graph = TerrainGraph.init_file("./maps_fetch/data.txt")
hole_tris = []
points = set()
face_angles = []
for face in graph.faces:
    face_angles.append((np.degrees(face.angle())))
    if np.degrees(face.angle()) < 177:
        tri = []
        for node in face.nodes:
            tri.append((node._loc.x, node._loc.y))
            points.add((node._loc.x, node._loc.y))
        hole_tris.append(tri)


boundary_x = (min([x for (x,y) in graph._2d]), max([x for (x,y) in graph._2d]))
boundary_y= (min([y for (x,y) in graph._2d]), max([y for (x,y) in graph._2d]))

#points.add((boundary_x[0], boundary_y[0]))
#points.add((boundary_x[0], boundary_y[1]))
#points.add((boundary_x[1], boundary_y[0]))
#points.add((boundary_x[1], boundary_y[1]))


point_list = []
for point in points:
    point_list.append([point[0], point[1]])
points = np.array(point_list)

surf = Surface(num_points=None, is_terrain=True, init_random=False, points=points)


seed = 1
num_edges = 20

#seed = 12
#num_edges = 20

visualize_projection_and_holes(graph, surf, hole_tris)
graph.plot()
test_funnel_terrain(seed, surf, num_edges, hole_tris, graph)