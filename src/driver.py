from math import pi
from terrain import Location, TerrainGraph
from simplifier import surface_simplifier
from path_finder import path_finder

graph = TerrainGraph.init_file("./maps_fetch/data.txt")

s = list(surface_simplifier(graph, [100]))[0]

path = path_finder(s, Location(3426554, 653247, -543),
                   Location(3441938, 688097, 626), pi / 2)

print(path)
