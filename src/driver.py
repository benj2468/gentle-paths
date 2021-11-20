from math import pi
from terrain import TerrainGraph
from simplifier import surface_simplifier
from path_finder import path_finder
import matplotlib.pyplot as plt

graph = TerrainGraph.init_file("./maps_fetch/data.txt")

s = list(surface_simplifier(graph, [100]))[0]

ax1 = plt.axes(projection='3d')
s.plot(ax1)

plt.figure()

path = path_finder(s, (3534005, 640000), (3460000, 700000), pi / 15)

ax2 = plt.axes()
points = [[], []]
s.plot_2d(ax2)
for loc in path:
    loc = tuple(loc[0])[0:2]
    points[0].append(loc[0])
    points[1].append(loc[1])

ax2.scatter(points[0], points[1])
ax2.plot(points[0], points[1])

plt.show()
