import numpy as np
from Surface import Surface
from FunnelVisualizer import FunnelVisualizer

class Funnel():
    def __init__(self, surface, start, similar_path, vtx_map):
        self.s = surface
        self.similar_path = similar_path
        self.vtx_map = vtx_map

        simpath1 = vtx_map[similar_path[0][0]]
        simpath2 = vtx_map[similar_path[0][1]]
        # data structures for funnel algorithm 
        ang = self.signed_angle([start, simpath1],[start, simpath2])
        if np.sign(ang) > 0:
            self.left_boundary = [start, simpath1]
            self.right_boundary = [start, simpath2]
        else:
            self.left_boundary = [start, simpath2]
            self.right_boundary = [start, simpath1]
        self.tail = []
        self.apex = start

    def funnel(self):
        cnt = 0
        while len(self.similar_path) > 0:
            edge = self.similar_path.pop(0)

            pt1, pt2 = edge
            if self.left_boundary[-1] == pt1:
                self.add_to_boundary(pt2, 'right', edge)
            elif self.left_boundary[-1] == pt2:
                self.add_to_boundary(pt1, 'right', edge)
            elif self.right_boundary[-1] == pt1:
                self.add_to_boundary(pt2, 'left', edge)
            elif self.right_boundary[-1] == pt2:
                self.add_to_boundary(pt1, 'left', edge)
            else:
                raise ValueError("pt1 and pt2 are in neither of the boundary arrays")
                
            cnt += 1

    def add_to_boundary(self, pt, side, edge):
            curr_left = self.left_boundary[-2:]
            curr_right = self.right_boundary[-2:]
            curr_angle = self.signed_angle(curr_left, curr_right)

            if side == 'left':
                boundary1 = self.left_boundary
                boundary2 = self.right_boundary
                new_left = [boundary1[-1], pt]
                new_right = curr_right
            elif side == 'right':
                boundary1 = self.right_boundary
                boundary2 = self.right_boundary
                new_right = [boundary1[-1], pt]
                new_left = curr_left

            new_angle = self.signed_angle(new_left, new_right)
            if np.sign(new_angle) == np.sign(curr_angle) and np.abs(new_angle) < np.abs(curr_angle):
                boundary1[-1] = pt
            elif np.sign(new_angle) == np.sign(curr_angle):
                boundary1.append(pt)
            else:
                for j in range(len(boundary2)):
                    self.tail.append(boundary2[j])
                self.apex = boundary2[-1]

                # clear boundary 1 and boundary 2
                b2len = len(boundary2)
                b1len = len(boundary1)
                for _ in range(b2len):
                    boundary2.pop()
                for _ in range(b1len):
                    boundary1.pop()

                # add apex and tri values to reinit b1 and 2
                boundary1.append(self.apex)
                boundary2.append(self.apex)

                edge1 = [self.apex, edge[0]]
                edge2 = [self.apex, edge[1]]
                next_angle = self.signed_angle(edge1, edge2)
                if np.sign(next_angle) == np.sign(curr_angle):
                    self.left_boundary.append(edge[0])
                    self.right_boundary.append(edge[1])
                else:
                    self.left_boundary.append(edge[1])
                    self.right_boundary.append(edge[0])

    def signed_angle(self, vec1, vec2):
        print(vec1)
        print(vec2)
        vec1 = np.append(vec1[0]-vec1[1], 0)
        vec2 = np.append(vec2[0]-vec2[1], 0)
        print(vec1)
        print(vec2)
        uvec1 = vec1/np.linalg.norm(vec1)
        uvec2 = vec2/np.linalg.norm(vec2)
        dp = np.dot(uvec1, uvec2)

        angle = np.arccos(dp)
        if (vec1[0]*vec2[1]-vec1[1]*vec2[0]) < 0:
            return -angle
        else:
            return angle
    

if __name__ == '__main__':
    surf = Surface(num_points = 10, is_terrain=False)
    print(surf.tri.simplices)
    print(surf.points)
    num_edges = 5
    start_edge = [0, 1]
    last_edge = start_edge
    path = []
    path.append(start_edge)
    for _ in range(num_edges):
        np.random.shuffle(surf.tri.simplices)
        for tri in surf.tri.simplices:
            if last_edge[0] in tri and last_edge[1] in tri:
                vtx1 = None
                vtx2 = None
                while not vtx1 or not vtx2 or vtx1==vtx2 or (vtx1==last_edge[0] and vtx2==last_edge[1]) \
                    or (vtx2==last_edge[0] and vtx1==last_edge[1]):
                    vtx1 = np.random.choice(tri)
                    vtx2 = np.random.choice(tri)
                path.append([vtx1, vtx2])

    path = np.array(path)
    vtx_map = surf.points
    start = vtx_map[path[0][0]] + vtx_map[path[0][1]]/2

    funnel = Funnel(surf, start, path, vtx_map)
    funnel.funnel()
    #FunnelVisualizer(surf)
            

    