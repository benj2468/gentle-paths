import numpy as np
from scipy.spatial import Delaunay

class Surface():
    def __init__(self, num_points, is_terrain, init_random=True, points=None):
        self.num_points = num_points
        self.is_terrain = is_terrain
        if init_random:
            self.initialize_random_surface()
        else:
            self.points = points

        self.tri = Delaunay(self.points)

    def initialize_random_surface(self):
        self.points = np.random.rand(self.num_points, 2)
