import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib
from homotopy.Surface import Surface
import numpy as np


class FunnelVisualizer():
    def __init__(self, surface, holes=None):
        self.s = surface
        self.holes = holes

    def plot_surface(self):
        plt.triplot(self.s.points[:, 0], self.s.points[:, 1],
                    self.s.tri.simplices)
        #plt.plot(self.s.points[:, 0], self.s.points[:, 1], 'o')
        plt.show()

    def plot_funnel(self, sim_path, fan, tail, apex, edge, start, target):
        for idx,vtx in enumerate(self.s.points):
            pass
        plt.triplot(self.s.points[:, 0],
                    self.s.points[:, 1],
                    self.s.tri.simplices,
                    color='#1f77b4')
        plt.plot(start[0], start[1], 'o', color='m')
        plt.plot(target[0], target[1], 'o', color='m')
        for idx, p in enumerate(sim_path):
            arr = np.array([self.s.points[p[0]], self.s.points[p[1]]])
            norm = matplotlib.colors.Normalize(vmin=0,
                                               vmax=len(sim_path),
                                               clip=True)
            mapper = cm.ScalarMappable(norm=norm, cmap=cm.Greys_r)
            plt.plot(arr[:, 0], arr[:, 1], color=mapper.to_rgba(idx))

        if not self.holes == None:
            hole_tris = np.array(self.holes)
            for tri in hole_tris:
                plt.fill(tri[:, 0], tri[:, 1], 'k', alpha=1)

        lb = np.array(fan)
        e = np.array(edge)
        plt.plot(lb[:, 0], lb[:, 1], 'g')
        plt.plot(e[:, 0], e[:, 1], 'r')
        plt.fill(lb[:, 0], lb[:, 1], 'm', alpha=.5)
        if len(tail) > 0:
            tail = np.array(tail)
            plt.plot(tail[:, 0], tail[:, 1], 'm')
        plt.scatter(apex[0], apex[1], color='k')
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().get_yaxis().set_visible(False)
        plt.gca().axis('off')
        plt.pause(.5)
        plt.gca().clear()


if __name__ == '__main__':
    surf = Surface(num_points=10, is_terrain=False)
    print(surf.tri.simplices)
    print(surf.points)
    FunnelVisualizer(surf)
