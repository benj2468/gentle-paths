from math import pi
from terrain import TerrainGraph
from simplifier import surface_simplifier
from path_finder import path_finder
import matplotlib.pyplot as plt

graph = TerrainGraph.init_file("./maps_fetch/data.txt")

# graph = list(surface_simplifier(graph, [100]))[0]

ax1 = plt.axes(projection='3d')
graph.plot(ax1)

# plt.figure()

path = path_finder(graph, (3534005, 640000), (3488000, 700000), pi / 500)

print(path.cost)

# ax2 = plt.axes()
points = [[], [], []]
# graph.plot_2d(ax2)
for loc in path.path:
    loc = tuple(loc[0])
    points[0].append(loc[0])
    points[1].append(loc[1])
    points[2].append(loc[2])

ax1.scatter(points[0], points[1], points[2])
ax1.plot(points[0], points[1], points[2])

plt.show()
