from math import pi
from terrain import TerrainGraph
from simplifier import surface_simplifier
from path_finder import path_finder
import matplotlib.pyplot as plt

theta_m = pi / 2
precision = 10
map = "RAINIER"

graph = TerrainGraph.init_file(f"./maps/{map}.txt")

ax1 = plt.axes(projection='3d')
graph.plot(ax1)

ax1.set_title(
    f"{map}: nodes = {len(graph.nodes)} Theta = {theta_m}; Precision = {precision}"
)

# Notice different between running:
# - pi / 2 - should be straight line
# - pi / 20 - start to see curve around the mountain
# - pi / 50 - switchbacks

path = path_finder(graph, (1, 1), (20000, 20000), theta_m, precision)

points = [[], [], []]
for loc in path.path:
    loc = tuple(loc[0])
    points[0].append(loc[0])
    points[1].append(loc[1])
    points[2].append(loc[2])

ax1.scatter(points[0], points[1], points[2])
ax1.plot(points[0], points[1], points[2])

plt.show()
