import numpy as np
from Surface import Surface
from FunnelVisualizer import FunnelVisualizer
import matplotlib.pyplot as plt

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
        cnt = 1
        fv = FunnelVisualizer(self.s)
        while cnt < len(self.similar_path):
            if cnt == 8:
                jfjf = ""
                ValueError("here")
            fv.plot_funnel(self.similar_path, self.left_boundary, self.right_boundary, self.tail, self.apex)
            edge = self.similar_path[cnt]

            pt1, pt2 = edge
            pt1 = self.vtx_map[pt1]
            pt2 = self.vtx_map[pt2]
            edge = np.array([pt1, pt2])
            if np.sum(self.left_boundary[-1]-pt1) == 0:
                print("c1")
                self.add_to_boundary(pt2, 'right', edge)
            elif np.sum(self.left_boundary[-1]-pt2) == 0:
                print("c2")
                self.add_to_boundary(pt1, 'right', edge)
            elif np.sum(self.right_boundary[-1]-pt1) == 0:
                print("c3")
                self.add_to_boundary(pt2, 'left', edge)
            elif np.sum(self.right_boundary[-1]-pt2) == 0:
                print("c4")
                self.add_to_boundary(pt1, 'left', edge)
            else:
                raise ValueError("pt1 and pt2 are in neither of the boundary arrays")
                
            cnt += 1
    
        plt.show()

    def add_to_boundary(self, pt, side, edge):
            curr_left = self.left_boundary[-2:]
            curr_right = self.right_boundary[-2:]
            curr_angle = self.signed_angle(curr_left, curr_right)

            if side == 'left':
                boundary1 = self.left_boundary
                boundary2 = self.right_boundary
                new_left = [boundary1[-2], pt]
                new_right = curr_right
            elif side == 'right':
                boundary1 = self.right_boundary
                boundary2 = self.left_boundary
                new_right = [boundary1[-2], pt]
                new_left = curr_left

            new_angle = self.signed_angle(new_left, new_right)

            if  np.abs(new_angle) < np.abs(curr_angle):
                b1, b2 = self.shrink_wedges(boundary1,boundary2, pt, side)
                if side == 'left':
                    self.left_boundary = b1
                    self.right_boundary = b2
                elif side == 'right':
                    self.right_boundary = b1
                    self.left_boundary = b2
            else: 
                boundary1.append(pt)
        
    def shrink_wedges(self, boundary1,boundary2, pt, dir):
        boundary1.append(pt)
        edge1 = list(boundary1[-3:-1])
        edge2 = list(boundary1[-2:])

        done_shrink = abs(self.signed_angle(edge1, edge2)) >= np.pi
        while not done_shrink:

            if len(boundary1)>3:
                print("here")
                boundary1.pop()
                boundary1.pop()
                boundary1.append(pt)
                edge1 = list(boundary1[-3:-1])
                edge2 = list(boundary1[-2:])
                print(edge1)
                print(edge2)
                print(dir)
                done_shrink = abs(self.signed_angle(edge1, edge2)) >= np.pi                 
            elif len(boundary1)>2:  
                print("hereer")
                boundary1.pop()
                boundary1.pop()
                boundary1.append(pt)
                edge1 = list(boundary2[0:2])                              
                edge2 = list(boundary1)
                print(edge1)
                print(edge2)
                print(dir)
                if dir == 'left':
                    done_shrink = (self.signed_angle(edge1, edge2)) <= 0
                else:
                    done_shrink = (self.signed_angle(edge1, edge2)) >= 0  
            elif len(boundary2)>2:
                print("hereree")
                boundary2.pop(0)
                self.apex = boundary2[0]
                self.tail.append(self.apex)
                boundary1 = [self.apex, pt]
                edge1 = list(boundary2[0:2])
                edge2 = list(boundary1)
                print(edge1)
                print(edge2)
                print(dir)
                if dir == 'left':
                    done_shrink = (self.signed_angle(edge1, edge2)) <= 0
                else:
                    done_shrink = (self.signed_angle(edge1, edge2)) >= 0 
            else:
                print("broken")
                break;
            print(self.signed_angle(edge1, edge2))
        return boundary1, boundary2

    def signed_angle(self, vec1, vec2):
        vec1 = np.append(vec1[0]-vec1[1], 0)
        vec2 = np.append(vec2[0]-vec2[1], 0)
        uvec1 = vec1/np.linalg.norm(vec1)
        uvec2 = vec2/np.linalg.norm(vec2)

        angle = np.arccos(np.clip(np.dot(uvec1, uvec2), -1.0, 1.0))

        if (vec1[0]*vec2[1]-vec1[1]*vec2[0]) < 0:
            return -angle
        else:
            return angle
    

if __name__ == '__main__':
    np.random.seed(0)
    surf = Surface(num_points = 30, is_terrain=False)
    num_edges = 12
    start_edge = surf.tri.simplices[0][0:2]
    last_edge = list(start_edge)
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
    start[0] = start[0]+.02
    funnel = Funnel(surf, start, path, vtx_map)
    #print(funnel.signed_angle(np.array([[0,0],[1,0]]) ,np.array([[0,0],[0,1]])))
    funnel.funnel()
            

    