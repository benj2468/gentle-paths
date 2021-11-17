import numpy as np
from numpy.lib.function_base import flip
from Surface import Surface
from FunnelVisualizer import FunnelVisualizer
import matplotlib.pyplot as plt
from copy import deepcopy

class Funnel():
    def __init__(self, surface, start, target, similar_path, vtx_map):
        self.s = surface
        self.similar_path = similar_path
        self.vtx_map = vtx_map
        self.start = start
        self.target = target

        # data structures for funnel algorithm 
        self.fan = [vtx_map[similar_path[0][0]], start, vtx_map[similar_path[0][1]]]
        self.tail = [start]
        self.apex = start

        # flag for reseeding
        self.reseed = False

        # left/right angle side
        left_edge = deepcopy(self.fan[0:2])
        left_edge.reverse()
        right_edge = deepcopy(self.fan[-2:])
        self.sign = np.sign(self.signed_angle(left_edge, right_edge))

    def funnel(self, visualize=True):
        # funnel algoirthm, no return, visualize flag determines whether we plot results
        if visualize:
            fv = FunnelVisualizer(self.s)

        for cnt in range(len(self.similar_path)-1):
            edge = self.similar_path[cnt+1]

            pt1, pt2 = (self.vtx_map[e] for e in edge) # vtx ids
            edge = np.array([pt1, pt2]) # vtx locations
            if visualize:
                fv.plot_funnel(self.similar_path, self.fan, self.tail, self.apex, edge, self.start, self.target)

            # we add pt1 or pt2 to the left or right side of the fan
            if np.sum(self.fan[0]-pt1) == 0:
                pt = pt2
                badpt = pt1
                side = 'right'
            elif np.sum(self.fan[0]-pt2) == 0:
                pt = pt1
                badpt = pt2
                side = 'right'
            elif np.sum(self.fan[-1]-pt1) == 0:
                pt = pt2
                badpt = pt1
                side = 'left'
            elif np.sum(self.fan[-1]-pt2) == 0:
                pt = pt1
                badpt = pt2
                side = 'left'
            else:
                raise ValueError("pt1 and pt2 are in neither of the boundary arrays")

            if self.reseed:
                self.reseed = False
                self.extend_funnel(side, pt)
            else:
                self.add_to_boundary(pt, badpt, side, edge)
        
        if visualize:
            fv.plot_funnel(self.similar_path, self.fan, self.tail, self.apex, edge, self.start, self.target)
        
        # update tail at end of algorithm
        target = self.target
        edge1 = [self.fan[0], target]
        self.add_to_boundary(target, self.fan[0], 'right', edge1)
        edge1 = [self.fan[-1], target]
        self.add_to_boundary(target, self.fan[-1], 'left', edge1)
        self.tail.append(target)

        if visualize:
            fv.plot_funnel(self.similar_path, self.fan, self.tail, self.apex, edge, self.start, self.target)

        plt.show()

    def add_to_boundary(self, pt, badpt, side, edge):
        # adding point to a boundary
        if side == 'left':
            ray = self.fan[0:2]
            ray_direction = self.norm(tuple(ray[0]-ray[1]))
            ray_origin = ray[1]
        elif side == 'right':
            ray = self.fan[-2:]
            ray_direction = self.norm(tuple(ray[1]-ray[0]))
            ray_origin = ray[0]
        intersect = self.line_ray_intersect(ray_origin, ray_direction, edge[0], edge[1], badpt)
        
        if intersect:
            self.extend_funnel(side, pt)
        else: 
            self.narrow_funnel(side, pt, badpt, edge)

    def extend_funnel(self, side, pt):
        # extend funnel operation
        if side == 'left':
            self.fan.insert(0, pt)
        elif side == 'right':
            self.fan.append(pt)
    
    def narrow_funnel(self, side, pt, badpt, edge):
        # narrow funnel operation
        if side == 'left':
            vtx = self.fan.pop(0)
            new_vtx = self.fan[0]
        elif side == 'right':
            vtx = self.fan.pop()
            new_vtx = self.fan[-1]
        
        # if we removed our apex, update the apex
        if np.sum(vtx-self.apex) == 0:
            self.apex = new_vtx
            self.tail.append(self.apex)
        
        # if our fan still has a ray to test, test the ray
        # otherwise, extend funnel or generate new apex
        if len(self.fan) >= 3:
            self.add_to_boundary(pt, badpt, side, edge)
        elif len(self.fan) == 2:
            if side == 'left':
                edge1 = [self.fan[0], pt]
                edge2 = deepcopy(self.fan)
            elif side == 'right':
                edge1 = deepcopy(self.fan)
                edge1.reverse()
                edge2 = [self.fan[1], pt]

            if np.sign(self.signed_angle(edge1, edge2)) == self.sign:
                self.extend_funnel(side, pt)
            else:
                self.reseed = True
                self.tail.append(badpt)
                self.apex = badpt
                if np.sum(pt-edge[0]) == 0:
                    self.fan = [edge[1]]
                else:
                    self.fan = [edge[0]]
                self.extend_funnel(side, pt)

    def signed_angle(self, vec1, vec2):
        # computes the signed angle between two vectors
        vec1 = np.append(vec1[0]-vec1[1], 0)
        vec2 = np.append(vec2[0]-vec2[1], 0)
        uvec1 = vec1/np.linalg.norm(vec1)
        uvec2 = vec2/np.linalg.norm(vec2)

        angle = np.arccos(np.clip(np.dot(uvec1, uvec2), -1.0, 1.0))

        if (vec1[0]*vec2[1]-vec1[1]*vec2[0]) < 0:
            return -angle
        else:
            return angle

    # Below code is used to fine intersection between line segment and ray
    # taken from, https://stackoverflow.com/questions/14307158/how-do-you-check-for-intersection-between-a-line-segment-and-a-line-ray-emanatin
    def magnitude(self, vector):
        return np.sqrt(np.dot(np.array(vector),np.array(vector)))

    def norm(self, vector):
        return np.array(vector)/self.magnitude(np.array(vector))

    def line_ray_intersect(self, rayOrigin, rayDirection, point1, point2, badpt):
        rayOrigin = np.array(rayOrigin, dtype=float)
        rayDirection = np.array(self.norm(rayDirection), dtype=float)
        point1 = np.array(point1, dtype=float)
        point2 = np.array(point2, dtype=float)

        v1 = rayOrigin - point1
        v2 = point2 - point1
        v3 = np.array([-rayDirection[1], rayDirection[0]])
        t1 = np.cross(v2, v1) / np.dot(v2, v3)
        t2 = np.dot(v1, v3) / np.dot(v2, v3)
        flag = False
        if t2 >= 0.0 and t2 <= 1.0:
            flag = True
            if np.sum(badpt-(rayOrigin + t1 * rayDirection)) == 0:
                flag = False
            else:
                flag = True      

        return flag        

    