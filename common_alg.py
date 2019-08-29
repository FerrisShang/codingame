from queue import PriorityQueue
from random import randint
import sys
import math
import time
class C:
    UP, RIGHT, DOWN, LEFT = (0, 1, 2, 3)
class M:
    pass
class U:
    class P:
        def __init__(self, x, y):
            self.x = x
            self.y = y
        def __str__(self):
            return '({} {})'.format(self.x, self.y)
    @staticmethod
    def debug(msg):
        print('DEBUG: {}'.format(msg), file=sys.stderr)
    @staticmethod
    def graph_search_path(graph, start, end, fun_g=None, fun_h=None):
        # graph is list of list like [[1, 2], [3], [3, 1], [0]]
        frontier = PriorityQueue()
        frontier.put((0, start))
        came_from = [None for _ in range(len(graph))]
        cost_so_far = [-1 for _ in range(len(graph))]
        cost_so_far[start] = 0
        c = 0
        while not frontier.empty():
            c += 1
            _, current = frontier.get()
            if current == end: break
            for n in graph[current]:
                if fun_g is None: new_cost = cost_so_far[current] + 1
                else: new_cost = cost_so_far[current] + fun_g(current, n)
                if cost_so_far[n] < 0 or new_cost < cost_so_far[n]:
                    cost_so_far[n] = new_cost
                    if fun_h is None: priority = new_cost + (end - n)
                    else: priority = new_cost + fun_h(n, end)
                    frontier.put((priority, n))
                    came_from[n] = current
        res = [end]
        while res[0] != start:
            res.insert(0, came_from[res[0]])
        # U.debug('{} {} {}'.format(start, end, res))
        return res
    @staticmethod
    def graph_dijsktra(graph, initial):
        """
        :param graph: graph is list of list like [[1, 2], [3], [3, 1], [0]]
        :param initial: initial node
        :return: distance - list of distance to initial node
        :return: path - next node to initial node
        """
        distance = [-1 for _ in range(len(graph))]
        distance[initial] = 0
        path = [n for n in range(len(graph))]
        nodes = set([n for n in range(len(graph))])
        while nodes:
            min_node = None
            for node in nodes:
                if distance[node] >= 0:
                    if min_node is None:
                        min_node = node
                    elif distance[node] < distance[min_node]:
                        min_node = node
            if min_node is None:
                break
            nodes.remove(min_node)
            current_weight = distance[min_node]
            for edge in graph[min_node]:
                weight = current_weight + 1  # graph.distances[(min_node, edge)]
                if distance[edge] < 0 or weight < distance[edge]:
                    distance[edge] = weight
                    path[edge] = min_node
        return distance, path
    @staticmethod
    def graph_searching(graph, initial, max_length, cmp, visited_set=None):
        if visited_set is None:
            initial = [initial]
            visited_set = set()
        if max_length < 0:
            return None
        for node in initial:
            if node in visited_set: continue
            if cmp(node):
                return node
            visited_set.add(node)
            res = U.graph_searching(graph, graph[node], max_length - 1, cmp, visited_set)
            visited_set.remove(node)
            if res: return res
    @staticmethod
    def points_distance(p1, p2=(0, 0)):
        if not isinstance(p1, U.P): p1 = U.P(p1[0], p1[1])
        if not isinstance(p2, U.P): p2 = U.P(p2[0], p2[1])
        return round(math.sqrt((p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y)))
    @staticmethod
    def length_about(length, match_length, deviation=3):
        return match_length - deviation <= length < match_length + deviation
class GCOMMON:
    def __init__(self):
        self.round = 0
    def round_update(self):
        self.round += 1
    def action(self):
        pass
class G(GCOMMON):
    def __init__(self):
        GCOMMON.__init__(self)
    def process(self):
        pass
if __name__ == '__main__':
    _g = G()
    while True:
        _g.round_update()
        _g.process()
        _g.action()
