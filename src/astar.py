# Benjamin Cape - 21F - CS76
# PA2
# 10.02.10
# Updated - Comp. Topology 11.20.21

from heapq import heappush, heappop
from search_solution import SearchSolution


class AstarNode:
    def __init__(self, state, heuristic, parent=None, tot_cost=0):
        self.state = state
        self.parent = parent

        self.expected_cost = tot_cost + heuristic
        self.removed = False

    def priority(self):
        return self.expected_cost

    def remove(self):
        self.removed = True

    def __str__(self) -> str:
        return str(self.state) + str(self.expected_cost)

    # comparison operator,
    # needed for heappush and heappop to work with AstarNodes:
    def __lt__(self, other):
        return self.priority() < other.priority()


class PriorityQueue:
    def __init__(self) -> None:
        self.queue = []
        self.visited = {}

    def __str__(self) -> str:

        return ','.join(list(map(str, self.queue)))

    def add_visited(self, node: AstarNode, cost: int):
        self.visited[node.state] = (cost, node)

    def get_visited(self, node: AstarNode):
        return self.visited[node.state][0]

    def try_insert(self, value, cost):
        state = value.state
        if not state in self.visited:
            self.add_visited(value, cost)
            heappush(self.queue, value)
        elif self.visited[state][0] > cost:
            self.visited[state][1].remove()
            self.add_visited(value, cost)
            heappush(self.queue, value)

    def pop(self):
        res = heappop(self.queue)
        while res.removed:
            if self.is_empty():
                return None
            res = heappop(self.queue)
        return res

    def is_empty(self):
        return len(self.queue) == 0


def backchain(node):
    result = []
    current = node
    while current:
        result.append(current.state)
        current = current.parent

    result.reverse()
    return result


def astar_search(search_problem, debug=False):
    heuristic = search_problem.heuristic
    start_node = AstarNode(search_problem.start_state,
                           heuristic(search_problem.start_state))
    frontier = PriorityQueue()

    solution = SearchSolution(search_problem,
                              "Astar with heuristic " + heuristic.__name__)

    frontier.try_insert(start_node, 0)

    while not frontier.is_empty():
        current = frontier.pop()
        if not current:
            break

        solution.nodes_visited += 1
        if search_problem.goal_test(current.state):
            solution.path = backchain(current)
            solution.cost = frontier.get_visited(current)
            return solution

        for (cost, neighbor) in search_problem.get_successors(current.state):
            tot_cost = frontier.get_visited(current)
            next = AstarNode(neighbor, heuristic(neighbor), current,
                             tot_cost + 1)
            frontier.try_insert(next, tot_cost + cost)

    solution.cost = float("inf")
    return solution
