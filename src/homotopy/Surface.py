from scipy.spatial import Delaunay
import numpy as np


class Surface():
    def __init__(self, num_points, is_terrain):
        self.num_points = num_points
        self.is_terrain = is_terrain
        self.initialize_random_surface()

    def initialize_random_surface(self):
        self.points = np.random.rand(self.num_points, 2)
        self.tri = Delaunay(self.points)
