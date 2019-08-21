# https://www.codingame.com/ide/puzzle/game-of-drones

from queue import PriorityQueue
from random import randint
import sys
import math
import time
class C:
    pass
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
        # U.debug('{} {} {}'.format(match_length - deviation, length, match_length + deviation))
        return match_length - deviation <= length < match_length + deviation
class COMMON:
    def __init__(self):
        self.round = 0
        self.action_pos = []
class GCOMMON(COMMON):
    def __init__(self):
        COMMON.__init__(self)
        self.players_num, self.my_id, self.drones_num, self.zones_num = [int(i) for i in input().split()]
        self.zones = [U.P(0, 0) for _ in range(self.zones_num)]
        self.zone_owner = [-1 for _ in range(self.zones_num)]
        self.drones_pos = [[U.P(0, 0) for _ in range(self.drones_num)] for _ in range(self.players_num)]
        self.drones_prev_pos = [[U.P(0, 0) for _ in range(self.drones_num)] for _ in range(self.players_num)]
        for i in range(self.zones_num):
            self.zones[i] = U.P(*[int(p) for p in input().split()])
        self.action_pos = [U.P(0, 0) for _ in range(self.drones_num)]
        self.my_pos = self.drones_pos[self.my_id]
        U.debug('self.my_id:{}  zone_num:{}  drone_num:{}'.format(self.my_id, self.zones_num, self.drones_num))
    def round_update(self):
        for i in range(self.zones_num):
            self.zone_owner[i] = int(input())
        for i in range(self.players_num):
            for j in range(self.drones_num):
                self.drones_prev_pos[i][j] = self.drones_pos[i][j]
                self.drones_pos[i][j] = U.P(*[int(p) for p in input().split()])
    def action(self):
        for p in self.action_pos:
            print('{} {}'.format(p.x, p.y))
class G(GCOMMON):
    def __init__(self):
        GCOMMON.__init__(self)
        self.drone_target = [[0 for _ in range(self.drones_num)] for _ in range(self.players_num)]
        self.zones_wanted = [-1 for _ in range(self.zones_num)]
    def move(self, drone_id, pos):
        assert(isinstance(pos, U.P))
        self.action_pos[drone_id] = pos
    def processing(self):
        if self.round == 1:
            for i in range(self.drones_num):
                self.move(i, U.P(2000, 900))
            return
        for i in range(self.players_num):
            for j in range(self.drones_num):
                for z_idx in range(self.zones_num):
                    z_pos = self.zones[z_idx]
                    self.drone_target[i][j] = -1
                    if U.length_about(U.points_distance(z_pos, self.drones_prev_pos[i][j]) - U.points_distance(z_pos, self.drones_pos[i][j]), 100):
                        self.drone_target[i][j] = z_idx
                        break
            # U.debug('{}:{}'.format(i, self.drone_target[i]))

        self.zones_wanted = [(-1, 0, _) for _ in range(self.zones_num)]  # watched, distance, zone_idx
        for i in range(self.players_num):
            if i == self.my_id:
                continue
            for j in range(self.zones_num):
                target_num = len([self.drone_target[i][idx] for idx in range(self.drones_num) \
                                  if self.drone_target[i][idx] == j or U.points_distance(self.drones_pos[i][idx], self.zones[j]) <= 100])
                target_num, min_distance = (0, 1e5)
                for idx in range(self.drones_num):
                    drone_distance = U.points_distance(self.drones_pos[i][idx], self.zones[j])
                    if self.drone_target[i][idx] == j or drone_distance <= 100:
                        target_num += 1
                        min_distance = min(min_distance, drone_distance)
                self.zones_wanted[j] = max((target_num, min_distance, j), self.zones_wanted[j])
        self.zones_wanted.sort()
        U.debug('{}'.format(self.zones_wanted))
        drone_avalible = [True for _ in range(self.drones_num)]
        for i in range(self.zones_num):
            drone_avalible_num = len([d for d in drone_avalible if d])
            if drone_avalible_num == 0:
                break
            zone_w = self.zones_wanted[i]
            need_num = zone_w[0] + 1
            res = [
                (U.points_distance(self.zones[zone_w[2]], self.drones_pos[self.my_id][dn]), dn)
                for dn in range(self.drones_num) if drone_avalible[dn]
            ]
            res.sort()
            for j in range(min(need_num, len(res))):
                self.move(res[j][1], self.zones[zone_w[2]])
                # U.debug('{} -> {}'.format(res[j][1], zone_w[2]))
                drone_avalible[res[j][1]] = False
        for i in range(self.drones_num):
            if drone_avalible[i]:
                self.move(i, U.P(2000, 900))

if __name__ == '__main__':
    _g = G()
    while True:
        _g.round_update()
        _g.processing()
        _g.action()

