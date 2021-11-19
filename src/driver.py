from math import pi
from terrain import TerrainGraph
from simplifier import surface_simplifier
from homotopy.Funnel import Funnel

graph = TerrainGraph.init_file("./maps_fetch/data.txt")

graph.plot()

simp = surface_simplifier(graph, pi / 2.0, 0.7)

simp.plot()
