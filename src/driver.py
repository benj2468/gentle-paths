from math import pi
from terrain import *
from simplifier import surface_simplifier

graph = TerrainGraph.init_file("./maps_fetch/data.txt")
# graph = TerrainGraph.init_flat(500)

graph.plot()

simp = surface_simplifier(graph, pi / 2.0, 0.7)