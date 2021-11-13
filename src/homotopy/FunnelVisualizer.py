import matplotlib.pyplot as plt 
from Surface import Surface

class FunnelVisualizer():
    def __init__(self, surface):
        self.s = surface
        self.plot_surface()

    def plot_surface(self):
        plt.triplot(self.s.points[:,0], self.s.points[:,1], self.s.tri.simplices)
        plt.plot(self.s.points[:,0], self.s.points[:,1], 'o')
        plt.show()

if __name__ == '__main__':
    surf = Surface(num_points = 10, is_terrain=False)
    print(surf.tri.simplices)
    print(surf.points)
    FunnelVisualizer(surf)
