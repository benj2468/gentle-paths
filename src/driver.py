from path_mapping import path_map
from search_solution import SearchSolution
from terrain import TerrainGraph
from simplifier import surface_simplifier
from path_finder import path_finder
import matplotlib.pyplot as plt
from time import time


def quantitative_test(graph: TerrainGraph, start, end, theta_m, precision):
    s = time()
    path = path_finder(graph, start, end, theta_m, precision)

    print(
        f'theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {path.cost}; time={time() - s}'
    )


def quantitative_test_mapping(S: TerrainGraph, start, end, theta_m, precision):
    s = time()
    graph = surface_simplifier(S, len(S.nodes) / 2)
    solution = path_finder(graph, start, end, theta_m, precision)

    print(
        f'BEFORE MAPPING: theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {solution.cost}; time={time() - s}'
    )

    solution2 = path_map(S, solution, theta_m, precision)

    print(
        f'AFTER MAPPING: theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {solution2.cost}; time={time() - s}'
    )

    s = time()
    solution2 = path_finder(S, start, end, theta_m, precision)
    print(
        f'NO MAPPING: theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {solution2.cost}; time={time() - s}'
    )


def visual_mapping_test(S: TerrainGraph, start, end, theta_m, precision):

    s = time()
    graph = surface_simplifier(S, len(S.nodes) / 10)
    solution = path_finder(graph, start, end, theta_m, precision)

    print(
        f'BEFORE MAPPING: theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {solution.cost}'
    )

    plot_solution(graph, solution, theta_m, precision)

    solution2 = path_map(S, solution, theta_m, precision * 10)

    print(
        f'AFTER MAPPING: theta_m = {round(theta_m, 5)}; precision = {precision}; cost = {solution2.cost}; time={time() - s}'
    )

    plot_solution(S, solution2, theta_m, precision * 10)


def plot_solution(graph: TerrainGraph, solution: SearchSolution, theta_m,
                  precision):
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


def visual_test(graph: TerrainGraph, start, end, theta_m, precision):
    solution = path_finder(graph, start, end, theta_m, precision)

    print(f'Done: Theta = {round(theta_m, 5)}; Precision = {precision}')

    plot_solution(graph, solution, theta_m, precision)


thetas = [0.244346]
precisions = [10]

map = "RAINIER"

S = TerrainGraph.init_file(f"./maps/{map}.txt")

# start = (190000, 10000)
# end = (35000, 120000)
start = (200, 2200)
end = (3000, 3300)

S.plot()

for theta_m in thetas:
    for precision in precisions:
        quantitative_test_mapping(S, start, end, theta_m, precision)

# plt.show()
