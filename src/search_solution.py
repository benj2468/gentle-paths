# Benjamin Cape - 21F - CS76
# PA2
# 10.02.10
# Slight modification to path printing since I made states objects


class SearchSolution:
    def __init__(self, problem, search_method):
        self.problem_name = str(problem)
        self.search_method = search_method
        self.path = []
        self.nodes_visited = 0
        self.cost = 0

    def __str__(self):
        string = "----\n"
        string += "{:s}\n"
        string += "attempted with search method {:s}\n"

        if len(self.path) > 0:

            string += "number of nodes visited: {:d}\n"
            string += "solution length: {:d}\n"
            string += "cost: {:f}\n"
            string += "path: {:s}\n"

            path_str = "["
            for state in self.path:
                path_str += f"{state},"
            path_str += ']'
            string = string.format(self.problem_name,
                                   self.search_method, self.nodes_visited,
                                   len(self.path), self.cost, path_str)
        else:
            string += "no solution found after visiting {:d} nodes\n"
            string = string.format(self.problem_name, self.search_method,
                                   self.nodes_visited)

        return string
