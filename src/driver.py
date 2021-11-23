from math import pi
from path_mapping import path_map
from search_solution import SearchSolution
from terrain import Location, TerrainGraph
from simplifier import surface_simplifier
from path_finder import path_finder
import matplotlib.pyplot as plt


def quantitative_test(graph: TerrainGraph, start, end, theta_m, precision):
    path = path_finder(graph, start, end, theta_m, precision)

    print(
        f'theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {path.cost}'
    )


def quantitative_test_mapping(S: TerrainGraph, start, end, graph: TerrainGraph,
                              theta_m, precision):
    solution = path_finder(graph, start, end, theta_m, precision)

    print(
        f'BEFORE MAPPING: theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {solution.cost}'
    )

    solution2 = path_map(S, solution, theta_m, precision)

    print(
        f'AFTER MAPPING: theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {solution2.cost}'
    )


def visual_mapping_test(S: TerrainGraph, start, end, graph: TerrainGraph,
                        theta_m, precision):
    solution = path_finder(graph, start, end, theta_m, precision)

    print(
        f'BEFORE MAPPING: theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {solution.cost}'
    )

    plot_solution(S, solution)

    solution2 = path_map(S, solution, theta_m, precision * 2)

    print(
        f'AFTER MAPPING: theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {solution2.cost}'
    )

    plot_solution(S, solution2)


def plot_solution(graph: TerrainGraph, solution: SearchSolution):
    ax = plt.axes(projection='3d')
    graph.plot(ax)

    points = [[], [], []]
    for loc in solution.path:
        loc = tuple(loc[0])
        points[0].append(loc[0])
        points[1].append(loc[1])
        points[2].append(loc[2])

    ax.scatter(points[0], points[1], points[2])
    ax.plot(points[0], points[1], points[2])

    ax.set_title(
        f"{map}: nodes = {len(graph.nodes)} Theta = {round(theta_m, 5)}; Precision = {precision} \n Distance = {solution.cost}"
    )

    plt.figure()


def visiaul_test(graph: TerrainGraph, start, end, theta_m, precision):
    solution = path_finder(graph, start, end, theta_m, precision)

    print(f'Done: Theta = {round(theta_m, 5)}; Precision = {precision}')

    plot_solution(graph, solution)


thetas = [pi / 20, pi / 30, pi / 40]
precisions = [10]

map = "FRANCONIA"

S = TerrainGraph.init_file(f"./maps/{map}.txt")

graph = surface_simplifier(S, len(S.nodes) / 2)

for theta_m in thetas:
    for precision in precisions:
        visiaul_test(S, (1, 1), (20000, 20000), theta_m, precision)

plt.show()
